"""Phase 8: the drafter's prompt, its one structured answer, and the template that replaces it.

Spec 3.11 says the prompt carries five things -- the brief, the artifacts as compact JSON with
their hashes, the candidates, the guidance spans and the rules. Each of those is asserted here,
because a rule that is not in the prompt is a rule the drafter was never told, and every one of
them is enforced downstream by something that will otherwise look like a model failure.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from quaestor.artifacts import ArtifactKind, ArtifactStore
from quaestor.errors import LLMOutputError
from quaestor.findings import DefectClass, Finding, FindingCandidate, Severity
from quaestor.llm import FakeLLM
from quaestor.report.drafter import (
    DRAFT_PURPOSE,
    NO_CANDIDATES,
    DraftedSection,
    Drafter,
    GuidanceSpan,
    finding_heading,
    merge_candidates,
    spans_from_payload,
    template_section,
)
from quaestor.report.sections import artifact_briefs, brief_for
from quaestor.trace import TraceReader, TraceWriter
from quaestor.vocab import ReportSection

SPAN = GuidanceSpan(
    doc="SR26-2", section_id="V.1.b", heading="Outcomes Analysis", text="Compare outputs."
)


@pytest.fixture
def store(tmp_path: Path) -> ArtifactStore:
    """A store with the three kinds of artifact a section may be shown."""
    store = ArtifactStore(tmp_path / "artifacts")
    store.put("metrics.test.auc", 0.74801204, ArtifactKind.scalar, "auc on test")
    store.put("metrics.test.brier", 0.1489, ArtifactKind.scalar, "brier on test")
    store.put("calibration.test", [{"bin": 1, "observed": 0.05}], ArtifactKind.table, "calibration")
    return store


@pytest.fixture
def candidate(store: ArtifactStore) -> FindingCandidate:
    """One `E1` candidate over an artifact of the fixture store."""
    return FindingCandidate(
        defect_class=DefectClass.E1,
        evidence=[store.artifact("metrics.test.auc").hash],
        detail="the challenger leads the champion by more than the threshold",
        suggested_severity=Severity.low,
        tool="challenger_compare",
    )


def drafter(llm: FakeLLM, trace: TraceWriter | None = None) -> Drafter:
    """A drafter over one package, for the prompt tests."""
    return Drafter(llm, package="credit_default", version="1.0", trace=trace)


def test_the_prompt_carries_the_brief_the_artifacts_the_spans_and_the_candidates(
    store: ArtifactStore, candidate: FindingCandidate
) -> None:
    brief = brief_for(ReportSection.outcomes)
    artifacts = artifact_briefs(store, brief)
    prompt = drafter(FakeLLM()).prompt(
        brief, artifacts=artifacts, spans=[SPAN], candidates=[candidate]
    )
    assert brief.brief.splitlines()[0] in prompt
    assert brief.heading in prompt
    assert "credit_default" in prompt and "1.0" in prompt
    assert store.artifact("metrics.test.auc").hash[:8] in prompt
    assert "0.748" in prompt
    assert "[[table:calibration.test]]" in prompt
    assert SPAN.citation in prompt and SPAN.text in prompt
    assert "E1" in prompt and candidate.detail in prompt
    for rule in ("followed immediately by its [[art:", "One sentence per line", "compliant"):
        assert rule in prompt


def test_the_prompt_says_what_to_do_when_a_section_has_nothing_to_cite() -> None:
    prompt = drafter(FakeLLM()).prompt(brief_for(ReportSection.monitoring))
    assert "this section cites no artifact" in prompt
    assert "none retrieved" in prompt
    assert NO_CANDIDATES in prompt
    assert "candidates raised for this section: none -- describe nothing as a finding" in prompt


def test_the_findings_section_is_given_the_heading_to_copy(store: ArtifactStore) -> None:
    finding = Finding.from_candidates(
        [
            FindingCandidate(
                defect_class=DefectClass.E1,
                evidence=[store.artifact("metrics.test.auc").hash],
                detail="the challenger leads",
                suggested_severity=Severity.low,
                tool="challenger_compare",
            )
        ],
        store=store,
    ).numbered(1)
    prompt = drafter(FakeLLM()).prompt(brief_for(ReportSection.findings), findings=[finding])
    assert finding_heading(finding) in prompt
    assert "### F-001 · E1 effective challenge · severity **low**" == finding_heading(finding)
    assert "the challenger leads" in prompt


def test_a_section_with_no_finding_is_told_to_say_so() -> None:
    prompt = drafter(FakeLLM()).prompt(brief_for(ReportSection.findings))
    assert "No finding was raised" in prompt


def test_the_repair_round_adds_the_previous_draft_and_the_flagged_claims() -> None:
    prompt = drafter(FakeLLM()).prompt(
        brief_for(ReportSection.outcomes),
        previous="The AUC is 0.68.",
        problems=["you wrote 0.68 for metrics.test.auc; the artifact says 0.748"],
    )
    assert "Your previous draft of this section was checked" in prompt
    assert "The AUC is 0.68." in prompt
    assert "- you wrote 0.68 for metrics.test.auc" in prompt
    assert "cite the artifact" in prompt


def test_draft_returns_the_markdown_and_traces_one_llm_call(tmp_path: Path) -> None:
    llm = FakeLLM(default=json.dumps({"markdown": "  The AUC is 0.748.  "}))
    trace = TraceWriter(tmp_path / "trace.jsonl", run_id="drafter")
    markdown = drafter(llm, trace).draft(brief_for(ReportSection.outcomes))
    assert markdown == "The AUC is 0.748."
    events = TraceReader(trace.path).events("llm_call")
    assert len(events) == 1
    assert events[0].payload["purpose"] == DRAFT_PURPOSE
    assert events[0].payload["section"] == "outcomes"
    assert events[0].payload["repair"] is False


def test_a_drafter_that_answers_with_prose_twice_raises_with_the_raw_text() -> None:
    llm = FakeLLM(default="here is your section, boss")
    with pytest.raises(LLMOutputError) as caught:
        drafter(llm).draft(brief_for(ReportSection.summary))
    assert "here is your section" in (caught.value.raw or "")
    assert llm.call_count == 2


def test_an_empty_markdown_answer_is_not_a_section() -> None:
    with pytest.raises(ValueError, match="markdown"):
        DraftedSection(markdown="")


def test_spans_are_read_back_out_of_a_guidance_artifact_payload() -> None:
    payload = {
        "query": "outcomes analysis",
        "spans": [
            {"doc": "SR26-2", "section_id": "V.1.b", "heading": "Outcomes", "text": "body"},
            {"section_id": "V.1.c"},
            "not a span",
        ],
    }
    spans = spans_from_payload(payload)
    assert [span.citation for span in spans] == ["[[reg:SR26-2:V.1.b]]"]
    assert spans[0].to_payload()["heading"] == "Outcomes"
    assert spans_from_payload({"spans": 5}) == []
    assert spans_from_payload({"spans": []}) == []
    assert spans_from_payload("not a payload") == []


def test_candidates_are_grouped_by_the_section_whose_material_they_rest_on(
    candidate: FindingCandidate,
) -> None:
    grouped = merge_candidates([candidate, candidate])
    assert list(grouped) == [ReportSection.conceptual_soundness]
    assert len(grouped[ReportSection.conceptual_soundness]) == 2
    assert merge_candidates([]) == {}


# --- the template narrative of `rules_only` -------------------------------------------------


def test_the_template_writes_one_cited_sentence_per_scalar_and_declares_its_claims(
    store: ArtifactStore,
) -> None:
    brief = brief_for(ReportSection.outcomes)
    artifacts = artifact_briefs(store, brief)
    markdown, claims = template_section(brief, artifacts=artifacts, spans=[SPAN])
    assert markdown.splitlines()[0].endswith(f"{SPAN.citation}.")
    assert "The value of `metrics.test.auc` is 0.748 [[art:" in markdown
    assert "[[table:calibration.test]]" in markdown
    assert {claim.value for claim in claims} == {0.748, 0.1489}
    assert all(claim.citation for claim in claims)
    assert all(claim.section is ReportSection.outcomes for claim in claims)


def test_the_template_names_the_candidates_without_writing_a_section_number(
    store: ArtifactStore, candidate: FindingCandidate
) -> None:
    """A bare "section 6" in the prose would be a numeric token no citation follows."""
    markdown, _ = template_section(
        brief_for(ReportSection.outcomes),
        artifacts=artifact_briefs(store, brief_for(ReportSection.outcomes)),
        candidates=[candidate],
    )
    assert "Candidates raised on this section's material: E1" in markdown
    assert "(see the findings section)" in markdown
    assert "section 6" not in markdown


def test_the_template_findings_section_writes_headings_and_no_uncited_number(
    store: ArtifactStore, candidate: FindingCandidate
) -> None:
    finding = Finding.from_candidates([candidate], store=store).numbered(1)
    markdown, claims = template_section(brief_for(ReportSection.findings), findings=[finding])
    assert finding_heading(finding) in markdown
    assert "`E1` finding, raised by `challenger_compare`" in markdown
    assert claims == []
    numbers = [
        part for part in markdown.replace("`", " ").split() if part.replace(".", "").isdigit()
    ]
    assert numbers == []


def test_the_template_says_so_when_nothing_bears_on_a_section() -> None:
    markdown, claims = template_section(brief_for(ReportSection.sensitivity))
    assert markdown == "No artifact of this run bears on this section."
    assert claims == []
    empty, _ = template_section(brief_for(ReportSection.findings))
    assert "No finding was raised" in empty


def test_a_section_with_candidates_is_told_they_are_the_only_findings_it_may_describe(
    store: ArtifactStore,
) -> None:
    """D-091: the prompt states the section's candidate list, and what the list means."""
    candidate = FindingCandidate(
        defect_class=DefectClass.L2,
        evidence=[store.artifact("metrics.test.auc").hash],
        detail="1.2667% of test rows repeat a training feature vector",
        suggested_severity=Severity.medium,
        tool="check_leakage",
    )
    prompt = drafter(FakeLLM()).prompt(
        brief_for(ReportSection.data_integrity), candidates=[candidate]
    )
    assert "candidates raised for this section: 1" in prompt
    assert "L2 (contamination, suggested severity medium, from check_leakage)" in prompt
    assert "Those are the only findings this section may describe." in prompt
    assert NO_CANDIDATES not in prompt


def test_every_section_prompt_carries_the_rule_that_a_finding_is_on_the_list() -> None:
    """The rule the two contradictory sentences of the third live run broke (D-091)."""
    for section in ReportSection:
        prompt = drafter(FakeLLM()).prompt(brief_for(section))
        assert "Call something a finding only if it is in the candidate list" in prompt


def test_a_section_six_prompt_with_no_finding_still_asks_for_the_open_items(
    store: ArtifactStore,
) -> None:
    """D-096: "no findings" must not be able to mean "no questions"."""
    del store
    prompt = drafter(FakeLLM()).prompt(brief_for(ReportSection.findings))
    assert "No finding was raised." in prompt
    assert "'### Open items'" in prompt
    assert "still owes the developer the observations it made" in prompt
