"""Phase 7: `Finding`, its evidence rule, and the `findings.json` envelope.

The evidence rule is the one `CLAUDE.md` states as a hard constraint -- a `Finding` cannot be
constructed without at least one artifact hash that exists in the store -- so it is tested from
both sides: a hash the store does not hold is refused by name, and a promotion with no evidence at
all is refused whatever the candidate says. The severity rule is tested the same way: a change
without a reason and a reason without a change are both refused.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema
import pytest
from pydantic import ValidationError

from quaestor import ArtifactStore, DefectClass, Finding, FindingCandidate, Severity
from quaestor.artifacts import ArtifactKind
from quaestor.findings import (
    PRE_RUN_TOOL,
    STORE_CONTEXT_KEY,
    CandidateNotPromoted,
    FindingsDocument,
    severity_rank,
)
from quaestor.trace import EventType, TraceReader, TraceWriter
from quaestor.vocab import Configuration, ReportSection

GOLDEN = Path(__file__).resolve().parents[1] / "examples" / "golden_report"
FINDINGS_SCHEMA: dict[str, Any] = json.loads(
    (GOLDEN / "FINDINGS_SCHEMA.json").read_text(encoding="utf-8")
)


@pytest.fixture
def store(tmp_path: Path) -> ArtifactStore:
    """A store holding the three artifacts these tests cite."""
    store = ArtifactStore(tmp_path / "artifacts")
    store.put("challenger.delta_auc", 0.0323, ArtifactKind.scalar)
    store.put("challenger.auc", 0.7735, ArtifactKind.scalar)
    store.put("threshold.E1.delta_auc", 0.03, ArtifactKind.scalar)
    return store


def candidate(
    store: ArtifactStore, *names: str, severity: Severity = Severity.low
) -> FindingCandidate:
    """One E1 candidate naming the given artifacts."""
    return FindingCandidate(
        defect_class=DefectClass.E1,
        evidence=[store.artifact(name).hash for name in names],
        detail="a challenger leads the champion by 0.0323 against a threshold of 0.03",
        suggested_severity=severity,
        tool="challenger_compare",
    )


def test_the_golden_findings_json_parses_and_re_serialises_unchanged() -> None:
    """The golden document round-trips through the models, key order aside."""
    payload = json.loads((GOLDEN / "findings.json").read_text(encoding="utf-8"))
    document = FindingsDocument.model_validate(payload, context={STORE_CONTEXT_KEY: None})
    assert document.to_payload() == payload
    jsonschema.validate(document.to_payload(), FINDINGS_SCHEMA)


def test_a_document_read_back_without_a_store_keeps_the_evidence_rule_s_shape() -> None:
    """Reading without a store waives the lookup, never the non-empty list."""
    payload = json.loads((GOLDEN / "findings.json").read_text(encoding="utf-8"))
    payload["findings"][0]["evidence"] = []
    with pytest.raises(ValidationError, match="at least 1 item"):
        FindingsDocument.model_validate(payload, context={STORE_CONTEXT_KEY: None})


def test_a_finding_with_no_store_in_the_context_is_refused(store: ArtifactStore) -> None:
    """The rule may be waived deliberately, never by forgetting to pass a store."""
    with pytest.raises(ValidationError, match="validated against an artifact store"):
        Finding(
            defect_class=DefectClass.E1,
            severity=Severity.low,
            suggested_severity=Severity.low,
            tool="challenger_compare",
            title="t",
            narrative="n",
            evidence=[store.artifact("challenger.auc").short_hash],
            section=ReportSection.conceptual_soundness,
        )


def test_a_finding_whose_evidence_is_not_in_the_store_is_refused_by_name(
    store: ArtifactStore,
) -> None:
    """The message names the hash, because that is what a reader has to go and look for."""
    with pytest.raises(ValidationError, match="deadbeef"):
        Finding.model_validate(
            {
                "defect_class": "E1",
                "severity": "low",
                "suggested_severity": "low",
                "tool": "challenger_compare",
                "title": "t",
                "narrative": "n",
                "evidence": ["deadbeef"],
                "section": "conceptual_soundness",
            },
            context={STORE_CONTEXT_KEY: store},
        )


def test_a_severity_change_without_a_reason_is_refused(store: ArtifactStore) -> None:
    """Spec 3.9 lets the agent re-severitise with a one-sentence reason, not without one."""
    with pytest.raises(ValidationError, match="one-sentence reason"):
        Finding.from_candidates(
            [candidate(store, "challenger.auc")], store=store, severity=Severity.high
        )


def test_a_reason_without_a_change_is_refused(store: ArtifactStore) -> None:
    """A reason beside an unchanged severity reads as a change that did not happen."""
    with pytest.raises(ValidationError, match="did not change"):
        Finding.from_candidates(
            [candidate(store, "challenger.auc")],
            store=store,
            severity=Severity.low,
            severity_reason="kept as suggested",
        )


def test_a_severity_change_with_a_reason_is_recorded_on_the_finding(store: ArtifactStore) -> None:
    """Both severities and the reason survive onto the object the report prints."""
    finding = Finding.from_candidates(
        [candidate(store, "challenger.auc")],
        store=store,
        severity=Severity.medium,
        severity_reason="the champion is used for pricing, so a 0.03 gap is material.",
    )
    assert (finding.severity, finding.suggested_severity) == (Severity.medium, Severity.low)
    assert finding.severity_reason is not None


def test_promotion_unions_the_evidence_and_counts_what_it_merged(store: ArtifactStore) -> None:
    """Merging candidates of one class is a union of evidence and a count, nothing else."""
    finding = Finding.from_candidates(
        [
            candidate(store, "challenger.auc", "challenger.delta_auc"),
            candidate(store, "challenger.delta_auc", "threshold.E1.delta_auc"),
        ],
        store=store,
    )
    assert finding.candidates_merged == 2
    assert len(finding.evidence) == 3
    assert finding.evidence == sorted(finding.evidence)
    assert finding.section is ReportSection.conceptual_soundness


def test_promotion_takes_the_highest_suggested_severity(store: ArtifactStore) -> None:
    """Merging a low and a high candidate suggests high, and needs no reason to publish it."""
    finding = Finding.from_candidates(
        [
            candidate(store, "challenger.auc", severity=Severity.low),
            candidate(store, "challenger.delta_auc", severity=Severity.high),
        ],
        store=store,
    )
    assert finding.suggested_severity is Severity.high
    assert finding.severity_reason is None


def test_candidates_of_two_classes_cannot_be_merged(store: ArtifactStore) -> None:
    """Spec 3.9 permits merging candidates *of the same class*."""
    other = candidate(store, "challenger.auc").model_copy(update={"defect_class": DefectClass.M1})
    with pytest.raises(ValueError, match="cannot be merged"):
        Finding.from_candidates([candidate(store, "challenger.auc"), other], store=store)


def test_no_candidate_means_no_finding(store: ArtifactStore) -> None:
    """The LLM writes narrative; it does not mint findings."""
    with pytest.raises(ValueError, match="at least one FindingCandidate"):
        Finding.from_candidates([], store=store)


def test_a_pre_run_candidate_must_have_its_evidence_attached_first(store: ArtifactStore) -> None:
    """The loader's L1 candidate carries no artifact; promoting it as it stands is refused."""
    pre_run = FindingCandidate(
        defect_class=DefectClass.L1,
        evidence=[],
        detail="feature 'recovery_amount' is declared timing: after_outcome",
        suggested_severity=Severity.high,
        tool=PRE_RUN_TOOL,
    )
    with pytest.raises(ValueError, match="no artifact between them"):
        Finding.from_candidates([pre_run], store=store)


def test_promotion_writes_one_finding_trace_event(store: ArtifactStore, tmp_path: Path) -> None:
    """The study counts promotions and severity changes from the trace, never from prose."""
    trace = TraceWriter(tmp_path / "trace.jsonl", run_id="r1")
    Finding.from_candidates(
        [candidate(store, "challenger.auc")],
        store=store,
        severity=Severity.medium,
        severity_reason="the champion is used for pricing.",
        trace=trace,
    )
    events = TraceReader(tmp_path / "trace.jsonl").events(EventType.finding)
    assert len(events) == 1
    assert events[0].payload["severity_changed"] is True
    assert events[0].payload["defect_class"] == "E1"


def test_the_document_orders_by_severity_and_numbers_in_that_order(store: ArtifactStore) -> None:
    """`F-001` is the most serious finding, whatever order the tools produced them in."""
    low = Finding.from_candidates([candidate(store, "challenger.auc")], store=store)
    high = Finding.from_candidates(
        [candidate(store, "challenger.delta_auc", severity=Severity.high)], store=store
    )
    document = FindingsDocument.build(
        package="credit_default",
        version="1.0",
        configuration=Configuration.full_agent,
        run_id="r1",
        findings=[low, high],
        checks_without_candidates={"check_leakage": [DefectClass.L1, DefectClass.L2]},
    )
    assert [finding.id for finding in document.findings] == ["F-001", "F-002"]
    assert document.findings[0].severity is Severity.high
    assert document.counts_by_severity() == {"high": 1, "medium": 0, "low": 1, "info": 0}
    jsonschema.validate(document.to_payload(), FINDINGS_SCHEMA)


def test_a_written_document_reads_back_and_validates(store: ArtifactStore, tmp_path: Path) -> None:
    """`findings.json` on disk is the envelope the schema describes."""
    finding = Finding.from_candidates([candidate(store, "challenger.auc")], store=store)
    document = FindingsDocument.build(
        package="credit_default",
        version="1.0",
        configuration=Configuration.rules_only,
        run_id="r1",
        findings=[finding],
        candidates_not_promoted=[
            CandidateNotPromoted.of(
                candidate(store, "threshold.E1.delta_auc"), "the gap is inside the threshold"
            )
        ],
    )
    path = document.write(tmp_path / "out" / "findings.json")
    jsonschema.validate(json.loads(path.read_text(encoding="utf-8")), FINDINGS_SCHEMA)
    reread = FindingsDocument.read(path)
    assert reread.to_payload() == document.to_payload()
    assert reread.by_severity(Severity.low)[0].id == "F-001"


def test_evidence_must_be_written_as_the_eight_characters_a_citation_quotes(
    store: ArtifactStore,
) -> None:
    """`FINDINGS_SCHEMA.json` fixes the width; a full hash in the list would not validate."""
    with pytest.raises(ValidationError, match="hex characters"):
        Finding.model_validate(
            {
                "defect_class": "E1",
                "severity": "low",
                "suggested_severity": "low",
                "tool": "challenger_compare",
                "title": "t",
                "narrative": "n",
                "evidence": [store.artifact("challenger.auc").hash],
                "section": "conceptual_soundness",
            },
            context={STORE_CONTEXT_KEY: store},
        )


def test_severity_rank_is_the_report_order() -> None:
    """The enum's order is asserted rather than assumed."""
    order = (Severity.high, Severity.medium, Severity.low, Severity.info)
    assert [severity_rank(severity) for severity in order] == [0, 1, 2, 3]


def test_a_context_that_is_not_a_store_is_refused(store: ArtifactStore) -> None:
    """The waiver is `None`; anything else in the slot is a mistake, not a policy."""
    with pytest.raises(ValidationError, match="not an ArtifactStore"):
        Finding.model_validate(
            {
                "defect_class": "E1",
                "severity": "low",
                "suggested_severity": "low",
                "tool": "challenger_compare",
                "title": "t",
                "narrative": "n",
                "evidence": [store.artifact("challenger.auc").short_hash],
                "section": "conceptual_soundness",
            },
            context={STORE_CONTEXT_KEY: "an artifact store, honestly"},
        )
