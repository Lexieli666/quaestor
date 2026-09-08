"""The first live validation's three defects, each pinned against that run's own trace.

`eval/results/first-live/credit-attempt1/` is the record of the run of 2026-09-08 that refused to
render: 17 model calls, 179 claim checks of which 176 verified, one repair round -- and then a
`ReportSchemaError`, because the renderer found an uncovered number in section 2 that the
extraction pre-pass had never counted as a claim. `docs/EVALUATION.md` writes that run up; this
module is the half of the write-up that a machine checks.

Nothing here calls a model. The section drafts are reconstructed from the recorded extraction
prompts -- each one carries the prose it was asked about -- and the claims from the `claim_check`
events, so both tests read the attempt rather than a re-enactment of it.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Final

import pytest

from quaestor.report.renderer import uncovered_numbers
from quaestor.trace import EventType, TraceEvent, TraceReader
from quaestor.verifier import (
    ClaimSource,
    ClaimStatus,
    Unit,
    VerifiedClaim,
    eligible_numbers,
    extraction_from,
    token_value,
)
from quaestor.vocab import ReportSection

ATTEMPT: Final = (
    Path(__file__).resolve().parent.parent / "eval" / "results" / "first-live" / "credit-attempt1"
)
"""The committed record of the run this module is about."""

PACKAGE_VERSION: Final = "1.0"
"""`subjects/credit_default/package.yaml`'s version, which is what the attempt validated."""

VERSION_SENTENCE: Final = "The champion in credit_default 1.0 is a linear-in-log-odds scorecard"
"""The sentence that cost the attempt its report: the `1.0` is the package version (D-084)."""

# The extraction prompt of Phase 9 opened the prose with this marker and `structured` appended the
# JSON instruction after it. Both are pinned here rather than rebuilt from today's
# `EXTRACTION_INSTRUCTION`, which no longer asks for the same fields (D-085): a recorded prompt is
# a historical document, and a test that reconstructs it from the current template would silently
# stop reading the attempt the next time the template changes.
PROSE_MARKER: Final = "\nProse:\n"
JSON_MARKER: Final = "\n\nAnswer with one JSON object"
SECTION_RE: Final = re.compile(r"Section: (?P<section>[a-z_]+)\.")


def _events() -> list[TraceEvent]:
    """Every event of the attempt's trace, in file order."""
    return list(TraceReader(ATTEMPT / "trace.jsonl"))


def _extraction_prose() -> dict[float, tuple[ReportSection, str]]:
    """The prose of every recorded extraction call, keyed by the call's latency.

    The latency is the join key because it is what the cassette and the `llm_call` event both
    record and no two of the attempt's calls share; the trace supplies the order.
    """
    found: dict[float, tuple[ReportSection, str]] = {}
    for path in sorted((ATTEMPT / "cassettes").glob("*.json")):
        cassette = json.loads(path.read_text(encoding="utf-8"))
        prompt = str(cassette["request"]["prompt"])
        match = SECTION_RE.search(prompt)
        if not prompt.startswith("You are extracting") or match is None:
            continue
        prose = prompt.split(PROSE_MARKER, 1)[1].split(JSON_MARKER, 1)[0]
        found[float(cassette["completion"]["latency_ms"])] = (
            ReportSection(match.group("section")),
            prose,
        )
    return found


def _drafts() -> dict[ReportSection, str]:
    """Each section as the attempt last drafted it, in the order the trace ran the extractions.

    A section the repair loop re-drafted was extracted twice; the draft the renderer was asked to
    write is the last one, so the last extraction of each section wins.
    """
    prose = _extraction_prose()
    drafts: dict[ReportSection, str] = {}
    for event in _events():
        if event.type is EventType.llm_call and event.payload.get("purpose") == "extract":
            section, text = prose[float(event.payload["latency_ms"])]
            drafts[section] = text
    return drafts


def _claim_runs() -> Iterator[tuple[ReportSection, list[VerifiedClaim]]]:
    """Yield each consecutive run of `claim_check` events as one section's claims."""
    section: ReportSection | None = None
    claims: list[VerifiedClaim] = []
    for event in _events():
        if event.type is not EventType.claim_check:
            continue
        here = ReportSection(event.payload["section"])
        if here is not section and section is not None:
            yield section, claims
            claims = []
        section = here
        claims.append(
            VerifiedClaim(
                # The trace records a claim's verdict and not its sentence, and nothing here
                # reads the sentence: the checks are on the value and the status.
                text=str(event.payload["claim_id"]),
                value=float(event.payload["value"]),
                unit=Unit(event.payload["unit"]),
                section=here,
                source=ClaimSource.report,
                status=ClaimStatus(event.payload["status"]),
            )
        )
    if section is not None:
        yield section, claims


def _post_repair_claims() -> dict[ReportSection, list[VerifiedClaim]]:
    """The claims of each section as they stood after the repair loop.

    A section that was re-drafted has two runs of `claim_check` events; the post-repair verdicts
    are the later run, so the last run of each section wins, exactly as `_drafts` takes the last
    draft.
    """
    return dict(_claim_runs())


@pytest.fixture(scope="module")
def drafts() -> dict[ReportSection, str]:
    """The attempt's seven final section drafts, reconstructed from its cassettes."""
    return _drafts()


@pytest.fixture(scope="module")
def claims() -> dict[ReportSection, list[VerifiedClaim]]:
    """The attempt's post-repair claims, section by section, from its trace."""
    return _post_repair_claims()


def test_the_attempt_s_record_is_the_run_the_write_up_describes(
    drafts: dict[ReportSection, str],
    claims: dict[ReportSection, list[VerifiedClaim]],
) -> None:
    """Every number `docs/EVALUATION.md` quotes for this attempt comes from this trace.

    `CLAUDE.md`: no number in the documentation that a committed run did not produce. This is that
    rule applied to the one run whose numbers the documentation quotes.
    """
    events = _events()
    calls = [event for event in events if event.type is EventType.llm_call]
    checks = [event for event in events if event.type is EventType.claim_check]
    extractions = [event for event in calls if event.payload["purpose"] == "extract"]
    statuses = [str(event.payload["status"]) for event in checks]

    assert len(events) == 212
    assert len(calls) == 17
    assert [event.payload["purpose"] for event in calls].count("draft") == 8
    assert [event.payload["purpose"] for event in calls].count("plan") == 1
    assert "reask" not in [event.payload["purpose"] for event in calls]
    assert len(checks) == 179
    assert statuses.count("verified") == 176
    assert statuses.count("unattributed") == 2
    assert statuses.count("unsupported") == 1
    repairs = [event for event in events if event.type is EventType.repair]
    findings = [event for event in events if event.type is EventType.finding]
    assert len(repairs) == 1
    assert repairs[0].payload["section"] == ReportSection.data_integrity.value
    assert repairs[0].payload["round"] == 1
    assert sorted(repairs[0].payload["removed"]) == [3.3, 6.0, 9.982]
    assert repairs[0].payload["still_failing"] == []
    assert len(findings) == 1
    assert findings[0].payload["defect_class"] == "L2"
    assert findings[0].payload["severity"] == "high"
    index = json.loads((ATTEMPT / "artifacts" / "index.json").read_text(encoding="utf-8"))
    names = {entry["hash"][:8]: name for name, entry in index["artifacts"].items()}
    assert len(index["artifacts"]) == 121
    assert sorted(names[hash8] for hash8 in findings[0].payload["evidence"]) == [
        "leakage.overlap",
        "threshold.L2.overlap",
    ]

    tools = [event for event in events if event.type is EventType.tool_call]
    assert len(tools) == 13
    assert round(sum(float(event.payload["duration_s"]) for event in tools), 2) == 2.66

    assert len(extractions) == 8
    assert sum(int(event.payload["tokens_out"]) for event in calls) == 92196
    assert sum(int(event.payload["tokens_out"]) for event in extractions) == 63865
    longest = max(extractions, key=lambda event: int(event.payload["tokens_out"]))
    assert int(longest.payload["tokens_out"]) == 20257
    assert round(float(longest.payload["latency_ms"]) / 1000) == 197
    assert round(sum(float(event.payload["cost_usd"]) for event in calls), 2) == 3.82
    assert round((events[-1].ts - events[0].ts).total_seconds()) == 1019

    # The reconstruction covers the whole report, so neither test below is reading a fragment.
    assert set(drafts) == set(claims) == set(ReportSection)
    assert sum(len(section) for section in claims.values()) == 140


def test_the_pre_pass_and_the_renderer_tokenise_the_attempt_s_sections_alike(
    drafts: dict[ReportSection, str],
) -> None:
    """One tokenizer: sections 2 and 3 of the attempt, seen by both callers that disagreed.

    The pre-pass with no claims handed in turns every eligible token into an `unattributed` claim;
    the renderer with no verified claims reports every eligible token as uncovered. Both lists are
    therefore the eligible set itself, and they are equal because there is now one function that
    computes it (D-084).
    """
    for section in (ReportSection.conceptual_soundness, ReportSection.data_integrity):
        markdown = drafts[section]
        tokens = [
            token.text
            for token in eligible_numbers(markdown, package_version=PACKAGE_VERSION).tokens
        ]
        prepass = extraction_from(section, markdown, [], package_version=PACKAGE_VERSION)
        renderer = uncovered_numbers(markdown, [], package_version=PACKAGE_VERSION)

        assert tokens, f"section {section.value} of the attempt carries no eligible number"
        values = [token_value(token) for token in tokens]
        assert renderer == tokens
        assert [claim.value for claim in prepass.claims] == values
        assert prepass.unattributed == [claim.id for claim in prepass.claims]
        assert "1.0" not in tokens


def test_the_attempt_s_refusal_cannot_recur(
    drafts: dict[ReportSection, str],
    claims: dict[ReportSection, list[VerifiedClaim]],
) -> None:
    """The run whose 140 claims all verified is a run the renderer writes.

    Two assertions, and the second is the one that matters. Every section of the attempt, checked
    against its own post-repair verdicts, now has nothing uncovered -- so the refusal does not
    happen. And section 2 without the package version still reports `1.0`, which is the defect
    itself: what fixed the run is that the version reaches the check, not that the sentence
    changed or that the rule was relaxed.
    """
    assert VERSION_SENTENCE in drafts[ReportSection.conceptual_soundness]
    for section, markdown in drafts.items():
        verdicts = claims[section]
        assert [claim.status for claim in verdicts] == [ClaimStatus.verified] * len(verdicts)
        assert uncovered_numbers(markdown, verdicts, package_version=PACKAGE_VERSION) == []

    assert uncovered_numbers(
        drafts[ReportSection.conceptual_soundness],
        claims[ReportSection.conceptual_soundness],
    ) == ["1.0"]
