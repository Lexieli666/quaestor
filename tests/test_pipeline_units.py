"""Phase 8: the pipeline's own small decisions, tested where a whole run cannot reach them.

Promotion, the baseline's raw profile, the split of a one-call report into sections and the
reading of a drafted finding's title are each a paragraph of `validate()` that a green end-to-end
run never exercises: a clean subject has no evidence-less candidate, a subject that ran always
wrote `data_train.csv`, and a competent fake always writes every heading. Each of those is where a
real run will differ from the tests, so each is asserted on its own.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from quaestor.artifacts import ArtifactKind, ArtifactStore
from quaestor.configs import config_for
from quaestor.findings import PRE_RUN_TOOL, DefectClass, FindingCandidate, Severity
from quaestor.package import load_package
from quaestor.pipeline import (
    PLAIN_PROFILE,
    PlainFinding,
    PlainReport,
    _checks_without_candidates,
    _model_id,
    _not_checked,
    _plain_findings,
    _profile_for_baseline,
    _promote,
    _quaestor_version,
    _run_id,
    _split_sections,
    _title_and_narrative,
)
from quaestor.report.sections import ordered_briefs
from quaestor.trace import TraceReader, TraceWriter
from quaestor.vocab import Configuration, ReportSection

REPO_ROOT = Path(__file__).resolve().parents[1]
CREDIT = REPO_ROOT / "subjects" / "credit_default"
MSR = REPO_ROOT / "subjects" / "msr_prepayment"


@pytest.fixture
def store(tmp_path: Path) -> ArtifactStore:
    """A store with one scalar, which is all a candidate needs to point at."""
    store = ArtifactStore(tmp_path / "artifacts")
    store.put("metrics.test.auc", 0.7412, ArtifactKind.scalar, "auc on test")
    return store


def test_the_version_on_the_front_matter_is_the_installed_one() -> None:
    import quaestor

    assert _quaestor_version() == quaestor.__version__


def test_candidates_of_one_class_are_merged_into_one_finding(store: ArtifactStore) -> None:
    digest = store.artifact("metrics.test.auc").hash
    candidates = [
        FindingCandidate(
            defect_class=DefectClass.S1,
            evidence=[digest],
            detail=f"{feature} drifted",
            suggested_severity=Severity.medium,
            tool="profile_data",
        )
        for feature in ("limit_bal", "utilisation")
    ]
    findings, declined = _promote(candidates, store, None)
    assert len(findings) == 1
    assert findings[0].candidates_merged == 2
    assert declined == []


def test_a_candidate_no_tool_has_evidenced_yet_cannot_become_a_finding(
    store: ArtifactStore,
) -> None:
    """The evidence rule is the constraint the project is built around; it is not waived here."""
    pre_run = FindingCandidate(
        defect_class=DefectClass.L1,
        evidence=[],
        detail="a feature is declared after_outcome",
        suggested_severity=Severity.high,
        tool=PRE_RUN_TOOL,
    )
    findings, declined = _promote([pre_run], store, None)
    assert findings == []
    assert len(declined) == 1
    assert declined[0].defect_class is DefectClass.L1
    assert "no artifact names it" in declined[0].reason


def test_a_pre_run_candidate_joins_the_check_that_evidenced_its_class(
    store: ArtifactStore,
) -> None:
    digest = store.artifact("metrics.test.auc").hash
    pre_run = FindingCandidate(
        defect_class=DefectClass.L1,
        evidence=[],
        detail="a feature is declared after_outcome",
        suggested_severity=Severity.high,
        tool=PRE_RUN_TOOL,
    )
    evidenced = FindingCandidate(
        defect_class=DefectClass.L1,
        evidence=[digest],
        detail="the timing screen flagged one feature",
        suggested_severity=Severity.high,
        tool="check_leakage",
    )
    findings, declined = _promote([pre_run, evidenced], store, None)
    assert declined == []
    assert len(findings) == 1
    assert findings[0].candidates_merged == 2
    assert "after_outcome" in findings[0].narrative


def test_a_check_that_raised_one_of_its_classes_still_reports_the_others() -> None:
    clear = _checks_without_candidates(
        ["run_model", "profile_data", "compute_metrics"], [DefectClass.D1]
    )
    assert clear == {
        "profile_data": [DefectClass.S1],
        "compute_metrics": [DefectClass.T1, DefectClass.C1, DefectClass.O1],
    }
    assert "run_model" not in clear


def test_the_baseline_profile_is_empty_when_the_subject_wrote_no_matrix(
    store: ArtifactStore, tmp_path: Path
) -> None:
    assert _profile_for_baseline(tmp_path / "nothing", store) == {}
    assert PLAIN_PROFILE not in store


def test_the_baseline_profile_describes_the_columns_and_is_stored(
    store: ArtifactStore, tmp_path: Path
) -> None:
    out = tmp_path / "run"
    out.mkdir()
    (out / "data_train.csv").write_text("id,x,y\n1,0.5,1\n2,1.5,0\n", encoding="utf-8")
    profile = _profile_for_baseline(out, store)
    assert profile["n_rows"] == 2
    assert profile["columns"]["x"]["mean"] == pytest.approx(1.0)
    assert profile["columns"]["x"]["missing"] == 0.0
    assert PLAIN_PROFILE in store


def test_a_one_call_report_is_split_on_the_headings_it_wrote(tmp_path: Path) -> None:
    briefs = ordered_briefs(ArtifactStore(tmp_path / "artifacts"))
    markdown = (
        "## 1. Summary and scope\nThe summary.\n"
        "## 4. Outcomes analysis\nThe outcomes.\n"
        "## 7. Ongoing monitoring recommendations\nThe monitoring.\n"
    )
    sections = _split_sections(markdown, briefs)
    assert sections[ReportSection.summary] == "The summary."
    assert sections[ReportSection.outcomes] == "The outcomes."
    assert sections[ReportSection.monitoring] == "The monitoring."
    assert ReportSection.sensitivity not in sections


def test_a_drafted_finding_gives_up_its_bold_title(store: ArtifactStore) -> None:
    title, narrative = _title_and_narrative("**A challenger wins.**\nAnd here is why.")
    assert title == "A challenger wins."
    assert narrative == "And here is why."
    assert _title_and_narrative("No bold anywhere.") == ("", "No bold anywhere.")
    assert _title_and_narrative("**Only a title.**") == ("Only a title.", "Only a title.")


def test_a_baseline_finding_whose_evidence_is_a_logical_name_resolves(
    store: ArtifactStore,
) -> None:
    answer = PlainReport(
        markdown="",
        findings=[
            PlainFinding(
                defect_class=DefectClass.C1,
                severity=Severity.medium,
                title="miscalibrated",
                narrative="the probabilities drift",
                evidence=["metrics.test.auc", "no.such.name"],
            )
        ],
    )
    findings, declined = _plain_findings(answer, store, None)
    assert declined == []
    assert findings[0].evidence == [store.artifact("metrics.test.auc").hash[:8]]
    assert findings[0].tool == "plain_llm"


def test_a_baseline_finding_with_no_prose_at_all_still_gets_a_title(
    store: ArtifactStore,
) -> None:
    answer = PlainReport(
        markdown="",
        findings=[PlainFinding(defect_class=DefectClass.M1, evidence=["metrics.test.auc"])],
    )
    findings, _ = _plain_findings(answer, store, None)
    assert findings[0].title == "M1"
    assert findings[0].narrative == "M1"


def test_appendix_d_says_why_each_check_did_not_run() -> None:
    package = load_package(CREDIT)
    rows = _not_checked(package, config_for(Configuration.full_agent), ["run_model"], "a note")
    items = {row.item: row.reason for row in rows}
    assert "package declares no `regime.column`" in items["`check_stability` (R1)"]
    assert "not applicable to `binary_classification`" in items["`run_scenarios` (X1)"]
    assert items["developer claims (T1, claim channel)"] == "a note"
    assert "no `docs/` directory" in items["developer documentation"]
    assert "the run read no data directory" in items["data manifest"]


def test_appendix_d_says_which_configuration_left_a_check_out() -> None:
    """On a hazard subject the two checks exist, so the reason is the arm and not the model type."""
    package = load_package(MSR)
    rows = _not_checked(package, config_for(Configuration.plain_llm), ["run_model"], None)
    reasons = " ".join(row.reason for row in rows)
    assert "this configuration runs no checks" in reasons
    assert "runs the subject and one model call, by design" in reasons
    template = _not_checked(
        load_package(CREDIT), config_for(Configuration.rules_only), ["run_model"], None
    )
    assert any("calls no model" in row.reason for row in template)


# --- what a run is called, and what wrote it (D-093) --------------------------------------------


def _args() -> tuple[Any, ...]:
    """The five inputs a run id hashes, for the credit package under `full_agent`."""
    return (load_package(CREDIT), config_for(Configuration.full_agent), "real", None, None)


def test_two_runs_of_one_set_of_inputs_no_longer_share_an_identifier() -> None:
    """Attempts 1 and 3 both carried `credit_default-full_agent-d03b07c6` (D-093)."""
    early = _run_id(*_args(), datetime(2026, 9, 8, 3, 40, 14, tzinfo=UTC))
    late = _run_id(*_args(), datetime(2026, 9, 8, 6, 39, 34, tzinfo=UTC))
    assert early != late
    assert early.split("-")[-1] == late.split("-")[-1], "the input hash still says they agree"
    assert late.split("-")[-2] == "20260908T063934Z"


def test_the_stamp_is_utc_whatever_the_caller_s_timezone_is() -> None:
    """A run id is a joining key and must not depend on where the operator sat."""
    moment = datetime(2026, 9, 8, 6, 39, 34, tzinfo=UTC)
    shifted = moment.astimezone(timezone(timedelta(hours=-7)))
    assert _run_id(*_args(), moment) == _run_id(*_args(), shifted)


def test_the_input_hash_still_separates_two_different_runs() -> None:
    """Different inputs, same second: the hash is what it always was."""
    moment = datetime(2026, 9, 8, 6, 39, 34, tzinfo=UTC)
    package, config, mode, _, seed = _args()
    real = _run_id(package, config, mode, None, seed, moment)
    synthetic = _run_id(package, config, "synthetic", 5000, seed, moment)
    assert real.split("-")[-1] != synthetic.split("-")[-1]
    assert real.split("-")[-2] == synthetic.split("-")[-2]


def test_the_model_id_is_read_off_the_run_s_own_completions(tmp_path: Path) -> None:
    """The adapter is what you re-run; the id is what a published study compares (D-093)."""
    trace = TraceWriter(tmp_path / "trace.jsonl", run_id="r1")
    trace.llm_call(purpose="plan", model="claude-opus-5[1m]", tokens_in=2, tokens_out=525)
    trace.llm_call(purpose="draft", model="claude-opus-5[1m]", tokens_in=2, tokens_out=4989)
    assert _model_id(list(TraceReader(trace.path))) == "claude-opus-5[1m]"


def test_a_run_that_met_two_models_names_both(tmp_path: Path) -> None:
    trace = TraceWriter(tmp_path / "trace.jsonl", run_id="r1")
    trace.llm_call(purpose="plan", model="claude-opus-5[1m]")
    trace.llm_call(purpose="draft", model="claude-haiku-4-5-20251001")
    assert _model_id(list(TraceReader(trace.path))) == (
        "claude-opus-5[1m], claude-haiku-4-5-20251001"
    )


def test_a_run_no_model_answered_names_none(tmp_path: Path) -> None:
    """`rules_only` calls nothing, which is a different fact from "the adapter was called fake"."""
    trace = TraceWriter(tmp_path / "trace.jsonl", run_id="r1")
    trace.emit("tool_call", tool="run_model", args_hash="a", duration_s=1.0, artifacts=[], ok=True)
    assert _model_id(list(TraceReader(trace.path))) == ""
