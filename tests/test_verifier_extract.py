"""Phase 7: extraction, and the regex pre-pass that keeps the denominator honest.

The load-bearing test is the second one: a `FakeLLM` that returns two of a section's four numbers
must still produce four claims, the two it omitted marked `unattributed`. If that ever passes with
two claims, grounding precision becomes a number an extractor can improve by working less.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from quaestor.artifacts import ArtifactKind, ArtifactStore
from quaestor.errors import LLMOutputError
from quaestor.llm import FakeLLM
from quaestor.trace import EventType, TraceReader, TraceWriter
from quaestor.verifier import (
    ClaimStatus,
    Unit,
    drafted_prose,
    extract,
    match_claims,
    merge_exclusions,
)
from quaestor.verifier.extract import (
    EXTRACTION_INSTRUCTION,
    ExtractedClaims,
    numbered_lines,
    numbered_prose,
    numeric_tokens,
    token_value,
)
from quaestor.verifier.extract import (
    EXTRACTOR_RETURNED_EXCLUDED as RETURNED_EXCLUDED,
)
from quaestor.vocab import ReportSection
from verifiersupport import golden_report

SECTION = ReportSection.outcomes


@pytest.fixture
def store(tmp_path: Path) -> ArtifactStore:
    """A store holding the four artifacts the fixture section cites."""
    store = ArtifactStore(tmp_path / "artifacts")
    store.put("metrics.test.auc", 0.7412, ArtifactKind.scalar)
    store.put("threshold.package.auc.test.min", 0.7, ArtifactKind.scalar)
    store.put("profile.train.n", 3500, ArtifactKind.scalar)
    store.put("profile.test.n", 1500, ArtifactKind.scalar)
    return store


def section(store: ArtifactStore) -> str:
    """Two lines of drafted prose carrying four numbers, three of them cited."""
    auc = store.artifact("metrics.test.auc").citation()
    floor = store.artifact("threshold.package.auc.test.min").citation()
    train = store.artifact("profile.train.n").citation()
    return (
        f"The test AUC is 0.7412 {auc} against a floor of 0.70 {floor}.\n"
        f"The training split holds 3,500 {train} clients and 1,500 rows were held out.\n"
    )


def llm_returning(*claims: dict[str, Any]) -> FakeLLM:
    """A fake extractor that answers with exactly these claims, whatever it is asked."""
    return FakeLLM(default=json.dumps({"claims": list(claims)}))


def test_the_extractor_returns_the_claims_the_model_gave(store: ArtifactStore) -> None:
    """The happy path: four numbers, four claims, none added by the pre-pass."""
    markdown = section(store)
    llm = llm_returning(
        {"line": 1, "value": 0.7412, "unit": "ratio", "metric": "auc", "split": "test"},
        {"line": 1, "value": 0.7, "unit": "ratio", "metric": "auc"},
        {"line": 2, "value": 3500, "unit": "count"},
        {"line": 2, "value": 1500, "unit": "count"},
    )
    extraction = extract(SECTION, markdown, llm)
    assert [claim.value for claim in extraction.claims] == [0.7412, 0.7, 3500, 1500]
    assert extraction.unattributed == []
    assert extraction.n_from_model == 4


def test_a_fake_extractor_that_omits_two_numbers_shows_both_as_unattributed(
    store: ArtifactStore,
) -> None:
    """The pre-pass is the denominator: the extractor cannot lower it by omission."""
    markdown = section(store)
    llm = llm_returning(
        {
            "line": 1,
            "value": 0.7412,
            "unit": "ratio",
            "citation": store.artifact("metrics.test.auc").citation(),
        },
        {
            "line": 2,
            "value": 3500,
            "unit": "count",
            "citation": store.artifact("profile.train.n").citation(),
        },
    )
    extraction = extract(SECTION, markdown, llm)
    assert [claim.value for claim in extraction.claims] == [0.7412, 0.7, 3500, 1500]
    assert len(extraction.unattributed) == 2
    matches = match_claims(extraction.claims, store, unattributed=extraction.unattributed_ids)
    assert [match.status for match in matches] == [
        ClaimStatus.verified,
        ClaimStatus.unattributed,
        ClaimStatus.verified,
        ClaimStatus.unattributed,
    ]


def test_tokens_are_matched_to_claims_by_value_and_order_within_the_line(
    store: ArtifactStore,
) -> None:
    """The citation that ends up on a claim is the one the drafter wrote beside that number."""
    markdown = section(store)
    llm = llm_returning(
        {
            "line": 1,
            "value": 0.7,
            "unit": "ratio",
            "citation": store.artifact("threshold.package.auc.test.min").citation(),
        },
        {
            "line": 1,
            "value": 0.7412,
            "unit": "ratio",
            "citation": store.artifact("metrics.test.auc").citation(),
        },
    )
    extraction = extract(SECTION, markdown, llm)
    first, second = extraction.claims[0], extraction.claims[1]
    assert (first.value, second.value) == (0.7412, 0.7)
    assert first.citation is not None and "metrics.test.auc" in first.citation


def test_a_number_the_model_invents_is_dropped_and_recorded(store: ArtifactStore) -> None:
    """The pre-pass owns the eligible set: a number that is not in the prose is not a claim.

    The mirror of the omission test above. The extractor cannot lower the denominator by leaving
    a number out, and it cannot raise it by returning one the prose does not carry either -- which
    is what would happen if a model answered with the digits of a citation hash and the pre-pass
    took its word for it (D-077).
    """
    markdown = section(store)
    llm = llm_returning(
        {"line": 1, "value": 0.99, "unit": "ratio"},
    )
    extraction = extract(SECTION, markdown, llm)
    assert [claim.value for claim in extraction.claims] == [0.7412, 0.7, 3500, 1500]
    assert extraction.n_from_model == 1
    dropped = [item for item in extraction.exclusions if item.pattern == RETURNED_EXCLUDED]
    assert [item.examples for item in dropped] == [["0.99"]]


@pytest.mark.parametrize(
    ("prose", "value", "written"),
    [
        ("The `bill_mean_6m` feature is retained.", 6, "6.0"),
        ("## 4. Outcomes analysis", 4, "4"),
        (
            "<!-- quaestor:renderer:begin table deciles.test -->\n"
            "| 1 | 2.2409 |\n"
            "<!-- quaestor:renderer:end -->",
            2.2409,
            "2.2409",
        ),
    ],
    ids=["inline_code", "heading", "renderer_block"],
)
def test_a_claim_for_an_excluded_token_is_dropped_whatever_excluded_it(
    prose: str, value: float, written: str
) -> None:
    """Each of D-015's exclusion classes survives an extractor that claims what is inside it."""
    llm = llm_returning({"line": 1, "value": value, "unit": "ratio"})
    extraction = extract(SECTION, prose, llm)
    assert extraction.claims == []
    dropped = [item for item in extraction.exclusions if item.pattern == RETURNED_EXCLUDED]
    assert [item.examples for item in dropped] == [[written]]


def test_a_claim_for_a_number_inside_a_citation_is_dropped(store: ArtifactStore) -> None:
    """The commonest way an extractor would inflate the numerator: claiming a citation's digits.

    A logical name carries numbers of its own -- ``scenario.value_change.-300`` names a shock, it
    does not claim minus three hundred -- and so does the eight-character hash beside it. Both are
    excluded by construction (D-015), so a claim for either is dropped.
    """
    store.put("scenario.value_change.-300", -1297986.0, ArtifactKind.scalar)
    citation = store.artifact("scenario.value_change.-300").citation()
    line = f"Servicing value falls by 1,297,986 {citation} at the largest downward shock."
    llm = llm_returning(
        {"line": 1, "value": 1297986, "unit": "currency", "citation": citation},
        {"line": 1, "value": -300, "unit": "bp", "citation": citation},
    )
    extraction = extract(SECTION, line, llm)
    assert [claim.value for claim in extraction.claims] == [1297986]
    dropped = [item for item in extraction.exclusions if item.pattern == RETURNED_EXCLUDED]
    assert [item.examples for item in dropped] == [["-300.0"]]


def test_a_claim_that_names_the_wrong_line_keeps_its_citation(store: ArtifactStore) -> None:
    """An extractor that names the wrong line does not get its claim thrown away.

    The second pass offers a claim no token of its own line accounted for to any unfilled token of
    the section, by value, so a misattributed line costs the report nothing. Only a number that is
    nowhere in the prose is dropped -- including one whose line number is not in the prose at all,
    which is the shape a hallucinated line takes once the model returns an index (D-085).
    """
    markdown = section(store)
    llm = llm_returning(
        {
            "line": 2,
            "value": 0.7412,
            "citation": store.artifact("metrics.test.auc").citation(),
        },
        {"line": 99, "value": 0.5},
    )
    extraction = extract(SECTION, markdown, llm)
    assert [claim.value for claim in extraction.claims] == [0.7412, 0.7, 3500, 1500]
    first = extraction.claims[0]
    assert first.citation is not None and "metrics.test.auc" in first.citation
    assert first.id not in extraction.unattributed_ids
    assert extraction.n_from_model == 2
    dropped = [item for item in extraction.exclusions if item.pattern == RETURNED_EXCLUDED]
    assert [item.examples for item in dropped] == [["0.5"]]


def test_renderer_blocks_are_excluded_from_the_prompt_and_from_the_denominator() -> None:
    """No model wrote a renderer block, so there is nothing in it to verify (D-013)."""
    markdown = (
        "The top decile lifts by 2.24.\n\n"
        "<!-- quaestor:renderer:begin table deciles.test -->\n"
        "| decile | lift |\n|---|---|\n| 1 | 2.2409 |\n"
        "<!-- quaestor:renderer:end -->\n"
    )
    assert "2.2409" not in drafted_prose(markdown)
    extraction = extract(SECTION, markdown, llm_returning())
    assert [claim.value for claim in extraction.claims] == [2.24]
    assert [exclusion.pattern for exclusion in extraction.exclusions] == ["renderer_block"]
    assert extraction.n_excluded_tokens == 2


def test_the_exclusion_list_records_every_class_with_its_own_tokens(
    store: ArtifactStore,
) -> None:
    """D-015's list, each class recorded with what it actually swallowed."""
    markdown = (
        "## 4. Outcomes analysis\n"
        "The model validates `credit_default` version 1.0 against the guidance "
        "[[reg:SR26-2:V.1.c]] (see also SR 11-7 V.1.c), see F-001 and §6; the feature "
        "`psi 0.25` is retained and the AUC is 0.7412 "
        f"{store.artifact('metrics.test.auc').citation()}.\n"
    )
    extraction = extract(SECTION, markdown, llm_returning(), package_version="1.0")
    patterns = {exclusion.pattern: exclusion.examples for exclusion in extraction.exclusions}
    assert set(patterns) == {
        "section_number",
        "inline_code",
        "citation_hash",
        "regulatory_section_id",
        "finding_id",
        "package_version",
    }
    assert patterns["finding_id"] == ["F-001"]
    assert patterns["package_version"] == ["1.0"]
    assert patterns["inline_code"] == ["`psi 0.25`"]
    assert "SR26-2:V.1.c" in patterns["regulatory_section_id"]
    assert [claim.value for claim in extraction.claims] == [0.7412]


def test_a_number_that_ends_a_sentence_is_not_mistaken_for_a_list_marker() -> None:
    """`\\d+\\.` is section numbering only at the start of a line, never mid-sentence."""
    markdown = "The number of flagged features is 0.\nThe overlap is 0.\n"
    extraction = extract(SECTION, markdown, llm_returning())
    assert [claim.value for claim in extraction.claims] == [0.0, 0.0]


def test_a_list_marker_at_the_start_of_a_line_is_excluded() -> None:
    """`1.` opening a line is numbering; the number beside it is still a claim."""
    markdown = "1. The AUC is 0.7412 with no citation.\n"
    extraction = extract(SECTION, markdown, llm_returning())
    assert [claim.value for claim in extraction.claims] == [0.7412]


def test_the_pre_pass_infers_a_unit_for_the_claims_it_adds() -> None:
    """The guess only sets the tolerance recorded beside a claim nothing is compared to."""
    markdown = "The rate is 22.0% and the count is 1500 and the ratio is 0.5.\n"
    extraction = extract(SECTION, markdown, llm_returning())
    assert [claim.unit for claim in extraction.claims] == [Unit.percent, Unit.count, Unit.ratio]


def test_extraction_writes_an_llm_call_event_with_purpose_extract(
    store: ArtifactStore, tmp_path: Path
) -> None:
    """The study counts extractions and re-asks; both are `llm_call` events."""
    trace = TraceWriter(tmp_path / "trace.jsonl", run_id="r1")
    extract(SECTION, section(store), llm_returning(), trace=trace)
    events = TraceReader(tmp_path / "trace.jsonl").events(EventType.llm_call)
    assert [event.payload["purpose"] for event in events] == ["extract"]


def test_an_extractor_that_never_returns_json_raises_with_the_raw_text(
    store: ArtifactStore,
) -> None:
    """`structured` re-asks once and then fails loudly; extraction does not swallow it."""
    with pytest.raises(LLMOutputError):
        extract(SECTION, section(store), FakeLLM(default="not json at all"))


def test_the_instruction_names_the_section_and_carries_the_prose(store: ArtifactStore) -> None:
    """The prompt is the spec 3.10 instruction, not a paraphrase of it per call site."""
    llm = FakeLLM(default='{"claims": []}')
    extract(SECTION, section(store), llm)
    prompt = llm.calls[0].prompt
    assert EXTRACTION_INSTRUCTION.split("\n", 1)[0] in prompt
    assert "outcomes" in prompt
    assert "0.7412" in prompt


def test_the_prompt_numbers_the_prose_and_asks_for_the_number_not_the_text(
    store: ArtifactStore,
) -> None:
    """The extractor names a line rather than quoting it, which is what D-085 bought."""
    llm = FakeLLM(default='{"claims": []}')
    markdown = section(store)
    extract(SECTION, markdown, llm)
    prompt = llm.calls[0].prompt
    for number, line in enumerate(markdown.splitlines(), 1):
        assert f"{number}| {line}" in prompt
    assert '"line" is the number printed to the left' in prompt
    # The field is gone from the schema, so a model that answers with the old shape is rejected
    # rather than quietly half-understood.
    assert "text" not in ExtractedClaims.model_json_schema()["$defs"]["ExtractedClaim"]["required"]
    with pytest.raises(LLMOutputError):
        extract(SECTION, markdown, llm_returning({"text": "a line", "value": 0.7412}))


def test_numbering_the_prose_and_reading_it_back_is_a_round_trip() -> None:
    """`numbered_lines` is the inverse of `numbered_prose`, table rows and blank lines included."""
    prose = "The AUC is 0.7412.\n\n| decile | lift |\n| 1 | 2.2409 |"
    lines = prose.split("\n")
    assert numbered_lines(numbered_prose(prose)) == dict(enumerate(lines, 1))
    assert numbered_prose(prose).splitlines()[3] == "4| | 1 | 2.2409 |"


def test_the_package_version_is_excluded_at_the_end_of_a_sentence_too() -> None:
    """A version at the end of a sentence is still the version; the full stop is punctuation."""
    markdown = "The champion in credit_default 1.0 scores 0.7412 on test.\nIt is version 1.0.\n"
    extraction = extract(SECTION, markdown, llm_returning(), package_version="1.0")
    assert [claim.value for claim in extraction.claims] == [0.7412]
    patterns = {exclusion.pattern: exclusion.examples for exclusion in extraction.exclusions}
    assert patterns["package_version"] == ["1.0"]
    assert extraction.n_excluded_tokens == 2


def test_merge_exclusions_deduplicates_across_sections(store: ArtifactStore) -> None:
    """`claims.json` publishes one exclusion list for the whole report."""
    markdown = "F-001 is the only finding; the AUC is 0.7412 with no citation.\n"
    first = extract(ReportSection.summary, markdown, llm_returning())
    second = extract(ReportSection.findings, markdown, llm_returning())
    merged = merge_exclusions([first, second])
    assert [exclusion.examples for exclusion in merged] == [["F-001"]]


def test_the_pre_pass_reproduces_the_golden_report_s_claim_set_section_by_section() -> None:
    """The Phase 1 specification's 92 claims are exactly what the Phase 7 pre-pass finds.

    The golden's numbers are illustrative and its hashes resolve to nothing, so this asserts the
    *tokenisation*: with a fake extractor that returns nothing, every claim in the golden's
    `claims.json` is found by the pre-pass, in the section it belongs to, and nothing else is.
    """
    report = golden_report()
    body = report.split("\n---\n", 1)[1]
    heads = [
        "## 1. Summary",
        "## 2. Conceptual",
        "## 3. Data integrity",
        "## 4. Outcomes",
        "## 5. Sensitivity",
        "## 6. Findings",
        "## 7. Ongoing",
        "## Appendix A",
    ]
    golden_claims = json.loads(
        (Path(__file__).resolve().parents[1] / "examples/golden_report/claims.json").read_text(
            encoding="utf-8"
        )
    )["post_repair"]
    total = 0
    for index, name in enumerate(ReportSection):
        markdown = body.split(heads[index])[1].split(heads[index + 1])[0]
        found = extract(name, markdown, llm_returning(), package_version="1.0")
        want = sorted(claim["value"] for claim in golden_claims if claim["section"] == name.value)
        assert sorted(claim.value for claim in found.claims) == want, name
        assert len(found.unattributed) == len(found.claims)
        total += len(found.claims)
    assert total == 92


def test_numeric_tokens_reads_separators_and_per_cent_signs() -> None:
    """The tokenizer and the value parser are one pair, used by the eval harness too."""
    assert [token for _, token in numeric_tokens("3,500 rows at 22.0% and -0.021")] == [
        "3,500",
        "22.0%",
        "-0.021",
    ]
    assert token_value("3,500") == 3500.0
    assert token_value("22.0%") == 22.0


# --- exponent notation, one token (DECISIONS D-099) ---------------------------------------------


@pytest.mark.parametrize("literal", ["1.92e-05", "-5.589e-05", "9.982e-06"])
def test_an_exponent_literal_is_one_token_with_its_own_value(literal: str) -> None:
    """The three literals of the fourth live run, each of which tokenised as two numbers."""
    tokens = numeric_tokens(f"the delta is {literal} on the test split")
    assert [token for _, token in tokens] == [literal]
    assert token_value(literal) == float(literal)


def test_the_pre_pass_counts_an_exponent_literal_once(store: ArtifactStore) -> None:
    """Six of the fourth live run's claims were the two halves of three exponent literals."""
    store.put("ablation.utilisation.delta_auc", 1.9204697640939905e-05, ArtifactKind.scalar)
    citation = store.artifact("ablation.utilisation.delta_auc").citation()
    prose = f"Refitting without utilisation changes test AUC by 1.92e-05 {citation}.\n"
    found = extract(
        SECTION,
        prose,
        llm_returning({"line": 1, "value": 1.92e-05, "citation": citation}),
    )
    assert [claim.value for claim in found.claims] == [1.92e-05]
    assert found.unattributed == []
    matches = match_claims(found.claims, store, unattributed=found.unattributed_ids)
    assert [match.status for match in matches] == [ClaimStatus.verified]


def test_the_line_index_path_still_resolves_a_line_that_holds_an_exponent(
    store: ArtifactStore,
) -> None:
    """D-085's index, over prose whose line is now one token shorter than it used to be."""
    store.put("csi.bill_mean_6m", 9.982086887188549e-06, ArtifactKind.scalar)
    citation = store.artifact("csi.bill_mean_6m").citation()
    prose = f"The largest characteristic shift is small.\n- bill_mean_6m, 9.982e-06 {citation}\n"
    found = extract(
        SECTION,
        prose,
        llm_returning({"line": 2, "value": 9.982e-06, "citation": citation}),
    )
    assert [claim.value for claim in found.claims] == [9.982e-06]
    assert found.claims[0].text.startswith("- bill_mean_6m,")
    assert found.unattributed == []


# --- Phase 9 follow-up 5: a section reference is not a claim (D-112) ---------------------------


def test_a_reference_to_a_section_of_this_report_is_not_a_claim(store: ArtifactStore) -> None:
    """The fifth live report's section 7 opened "Section 4 of this report reported …"."""
    markdown = (
        "Section 4 of this report reported discrimination before calibration, because the rate "
        f"is at or above 0.05 {store.artifact('metrics.test.auc').citation()}.\n"
    )
    extraction = extract(SECTION, markdown, llm_returning())
    assert [claim.value for claim in extraction.claims] == [0.05]
    patterns = {exclusion.pattern: exclusion.examples for exclusion in extraction.exclusions}
    assert "Section 4" in patterns["section_number"]


def test_a_number_after_the_word_section_in_another_sense_is_still_a_claim() -> None:
    """The pattern needs the digits to follow the word, so a sentence about a slice is untouched."""
    markdown = "The cross-section holds 4 rows and the mean is 0.5.\n"
    extraction = extract(SECTION, markdown, llm_returning())
    assert [claim.value for claim in extraction.claims] == [4.0, 0.5]
