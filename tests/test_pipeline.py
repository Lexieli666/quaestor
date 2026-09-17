"""Phase 8, end to end: `validate()` over both synthetic subjects, offline, with a `FakeLLM`.

This is where the two expectations the earlier phases fixed finally hold at pipeline level:

* clean synthetic `credit_default` yields exactly one finding, `E1` at severity `low` (D-017),
* clean synthetic `msr_prepayment` yields none at all (D-047),

and it is where the substance of `CLAUDE.md`'s gate condition 5b runs. The `quaestor validate`
*command line* arrives in Phase 9; what that command will do is `validate()`, and both subjects go
through it here, producing a report that validates against `docs/REPORT_SCHEMA.md` by the same
checks `tests/test_golden_spec.py` applies to the Phase 1 golden.

Nothing here calls a live model, downloads anything or trains on real data: `SectionFake`
(`tests/reportsupport.py`) answers the drafter, the extractor, the planner and the baseline, and
both subjects run in `--synthetic` mode.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import jsonschema
import pytest

from quaestor import Configuration, TraceReader, validate
from quaestor.artifacts import ArtifactKind
from quaestor.errors import ToolError
from quaestor.findings import DefectClass, Severity, open_items
from quaestor.pipeline import UNEVIDENCED_PREFIX, ValidationRun
from quaestor.report import UNVERIFIED_OPEN, check_report
from quaestor.report.schema import FOLLOW_UPS_HEADING, OPEN_ITEMS_HEADING
from quaestor.tools.collinearity import CheckCollinearityTool
from quaestor.tools.metrics import SCALAR_METRICS
from quaestor.tools.run import RunModelTool
from quaestor.tools.thresholds import (
    SLICE_GAP_BOUND,
    SLICE_SHARE_CEILING,
    SLICE_SHARE_FLOOR,
    Thresholds,
)
from reportsupport import SectionFake

REPO_ROOT = Path(__file__).resolve().parents[1]
GOLDEN = REPO_ROOT / "examples" / "golden_report"
CREDIT = REPO_ROOT / "subjects" / "credit_default"
MSR = REPO_ROOT / "subjects" / "msr_prepayment"
SMALL = 1200
"""How many rows the variant runs generate: enough for every tool, small enough to run six times.

A panel this small is not the clean panel D-017 is about: at 1,200 rows the credit subject raises
`T1` at high and `C1` at medium beside the `E1` D-017 names, so a test that runs at `SMALL` cannot
assert the finding set and the two Phase 9 follow-up cases asserted `"E1" in` it instead. Those two
now run at the default 5,000 and assert the set, because the difference is 0.24 s a run (D-119);
every other use of this constant is a case whose subject is a planner action or a configuration
and not the finding set.
"""


def run_validate(
    package: Path,
    out: Path,
    *,
    llm: SectionFake | None = None,
    config: Configuration = Configuration.full_agent,
    synthetic: int = 5000,
    thresholds: Thresholds | None = None,
) -> ValidationRun:
    """Run the pipeline once, offline, with the shared fake."""
    return validate(
        package,
        llm=llm or SectionFake(),
        config=config,
        synthetic=synthetic,
        out=out,
        thresholds=thresholds,
        quaestor_version="0.1.0.dev0",
    )


@pytest.fixture(scope="module")
def credit(tmp_path_factory: pytest.TempPathFactory) -> ValidationRun:
    """One `full_agent` run of the clean synthetic `credit_default` subject."""
    return run_validate(CREDIT, tmp_path_factory.mktemp("credit") / "out")


@pytest.fixture(scope="module")
def hazard(tmp_path_factory: pytest.TempPathFactory) -> ValidationRun:
    """One `full_agent` run of the clean synthetic `msr_prepayment` subject."""
    return run_validate(MSR, tmp_path_factory.mktemp("msr") / "out", synthetic=2000)


# --- the two documents, and the four files spec section 8 says a run writes ----------------------


def test_no_artifact_a_run_stores_names_an_entry_of_the_decision_log(
    credit: ValidationRun, hazard: ValidationRun
) -> None:
    """D-116: a caption is shown to the drafter and printed in Appendix B, so it stays readable.

    The third live run copied `(D-050)` out of `threshold.O1.auc_gap`'s caption into its prose,
    where the `50` was counted as a claim of fifty. The tokenizer now excludes the reference
    wherever a model writes it; this is the other half, and it is asserted over every artifact two
    whole runs store rather than over the one table that had them, because any tool can write a
    caption.
    """
    for run in (credit, hazard):
        named = {
            name: run.store.entry(name).summary
            for name in run.store.names()
            if re.search(r"\bD-\d{3}\b", run.store.entry(name).summary)
        }
        assert named == {}, run.package.spec.name


def test_validate_writes_the_four_files_and_the_store(credit: ValidationRun) -> None:
    for name in ("report.md", "claims.json", "findings.json", "trace.jsonl"):
        assert (credit.out_dir / name).is_file(), name
    assert (credit.out_dir / "artifacts" / "index.json").is_file()
    assert credit.report_path == credit.out_dir / "report.md"


def test_the_credit_report_is_schema_valid_with_both_grounding_figures(
    credit: ValidationRun,
) -> None:
    """Spec 3.11's acceptance: the synthetic credit subject under `FakeLLM` validates."""
    front = json.loads(json.dumps(_front(credit.report)))
    schema = json.loads((GOLDEN / "REPORT_SCHEMA.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(front)
    assert front["grounding_precision_pre"] == pytest.approx(credit.precision_pre)
    assert front["grounding_precision_post"] == pytest.approx(credit.precision_post)
    assert front["n_claims"] == credit.claims.n_claims > 0
    assert front["illustrative"] is False
    assert "## Appendix A — Claims" in credit.report


def test_the_credit_report_passes_the_checks_the_golden_spec_applies(
    credit: ValidationRun,
) -> None:
    assert check_report(credit.report, credit.configuration, credit.claims.post_repair) == []


def test_the_clean_credit_subject_yields_exactly_one_e1_finding_at_low(
    credit: ValidationRun,
) -> None:
    """D-017, at pipeline level at last: one finding, `E1`, severity `low`."""
    findings = credit.findings.findings
    assert len(findings) == 1
    assert findings[0].id == "F-001"
    assert findings[0].defect_class.value == "E1"
    assert findings[0].severity.value == "low"
    assert findings[0].suggested_severity == findings[0].severity
    assert findings[0].evidence
    assert credit.findings.counts_by_severity() == {"high": 0, "medium": 0, "low": 1, "info": 0}
    assert credit.findings.candidates_not_promoted == []


def test_the_clean_hazard_subject_yields_no_finding_at_all(hazard: ValidationRun) -> None:
    """D-047, at pipeline level: the counterpart of D-017 is an empty findings list."""
    assert hazard.findings.findings == []
    assert hazard.findings.candidates_not_promoted == []
    assert hazard.findings.counts_by_severity() == {"high": 0, "medium": 0, "low": 0, "info": 0}
    assert check_report(hazard.report, hazard.configuration, hazard.claims.post_repair) == []


def test_the_hazard_report_carries_a_scenario_table_and_a_cpr_table(
    hazard: ValidationRun,
) -> None:
    """Both are renderer blocks: the drafter wrote a directive and never a cell."""
    for name in ("scenario.value_by_shock", "cpr.test"):
        begin = f"<!-- quaestor:renderer:begin table {name} -->"
        assert begin in hazard.report, name
        block = hazard.report.split(begin, 1)[1].split("<!-- quaestor:renderer:end -->", 1)[0]
        assert block.count("|") > 10, name
        assert "[[art:" in block and name in block
    assert "[[table:" not in hazard.report


def test_the_two_documents_validate_against_the_phase_1_schemas(credit: ValidationRun) -> None:
    pairs = (("CLAIMS_SCHEMA.json", "claims.json"), ("FINDINGS_SCHEMA.json", "findings.json"))
    for schema_name, document_name in pairs:
        schema = json.loads((GOLDEN / schema_name).read_text(encoding="utf-8"))
        document = json.loads((credit.out_dir / document_name).read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(document)


def test_every_artifact_citation_in_the_report_resolves_in_this_run_s_store(
    credit: ValidationRun,
) -> None:
    """The half `tests/test_verifier_golden.py` cannot check: the hash, against a real store."""
    import re

    cited = re.findall(r"\[\[art:([0-9a-f]{8}):([A-Za-z0-9_.+-]+?)(?:#|\]\])", credit.report)
    assert cited
    for hash8, name in cited:
        assert credit.store.entry(name).hash.startswith(hash8), (hash8, name)


def test_the_trace_holds_every_event_type_the_run_produced(credit: ValidationRun) -> None:
    events = list(TraceReader(credit.out_dir / "trace.jsonl"))
    kinds = {event.type.value for event in events}
    assert {"tool_call", "llm_call", "plan_step", "claim_check", "finding"} <= kinds
    assert all(event.run_id == credit.run_id for event in events)


# --- the repair loop ----------------------------------------------------------------------------


def test_one_repair_round_when_the_second_draft_cites_the_number(tmp_path: Path) -> None:
    """Spec 3.11's acceptance: an uncited number the re-draft fixes costs exactly one round."""
    llm = SectionFake(drop_citation_for=["challenger.brier"])
    run = run_validate(CREDIT, tmp_path / "out", llm=llm, synthetic=SMALL)
    rounds = TraceReader(run.out_dir / "trace.jsonl").events("repair")
    assert len(rounds) == 1
    assert rounds[0].payload["section"] == "conceptual_soundness"
    assert rounds[0].payload["round"] == 1
    assert run.precision_pre < 1.0
    assert run.precision_post == 1.0
    assert len(run.claims.repairs) == 1
    repair = run.claims.repairs[0]
    assert repair.before.status.value == "unsupported"
    assert repair.after.status.value == "verified"
    assert "no citation" in repair.instruction
    assert UNVERIFIED_OPEN not in run.report


def test_two_failed_rounds_leave_the_number_wrapped_and_the_post_figure_lower(
    tmp_path: Path,
) -> None:
    """The wrapper of spec 3.11, and the refusal that makes it compulsory."""
    llm = SectionFake(wrong_value_for={"challenger.brier": 0.9})
    run = run_validate(CREDIT, tmp_path / "out", llm=llm, synthetic=SMALL)
    rounds = TraceReader(run.out_dir / "trace.jsonl").events("repair")
    assert len(rounds) == 2
    assert [event.payload["round"] for event in rounds] == [1, 2]
    assert f"{UNVERIFIED_OPEN}0.9⟧" in run.report
    assert run.precision_post < 1.0
    assert _front(run.report)["grounding_precision_post"] == pytest.approx(run.precision_post)
    failed = [c for c in run.claims.post_repair if c.status.value != "verified"]
    assert [claim.value for claim in failed] == [0.9]
    assert check_report(run.report, run.configuration, run.claims.post_repair) == []


def test_a_number_that_is_not_in_the_drafter_s_json_is_wrapped_and_not_dropped(
    tmp_path: Path,
) -> None:
    """A pipeline that could drop an unverifiable number would flatter its own headline."""
    llm = SectionFake(wrong_value_for={"metrics.test.brier": 0.4242})
    run = run_validate(CREDIT, tmp_path / "out", llm=llm, synthetic=SMALL)
    assert "0.4242" in run.report
    assert f"{UNVERIFIED_OPEN}0.4242⟧" in run.report
    assert any(claim.value == 0.4242 for claim in run.claims.post_repair)


# --- the three configurations ---------------------------------------------------------------


def test_rules_only_emits_no_llm_call_event_at_all(tmp_path: Path) -> None:
    """The $0 arm of the study: spec 3.13's "template text (no LLM)", asserted on the trace."""
    llm = SectionFake()
    run = run_validate(
        CREDIT, tmp_path / "out", llm=llm, config=Configuration.rules_only, synthetic=SMALL
    )
    assert TraceReader(run.out_dir / "trace.jsonl").events("llm_call") == []
    assert llm.call_count == 0
    assert run.precision_post == 1.0
    assert run.claims.n_claims > 0
    assert check_report(run.report, run.configuration, run.claims.post_repair) == []


def test_plain_llm_records_an_unevidenced_finding_and_scores_it_as_one(tmp_path: Path) -> None:
    """Spec 3.13: a baseline finding naming no existing artifact is recorded, not believed."""
    llm = SectionFake(
        plain_findings=[
            {
                "defect_class": "C1",
                "severity": "high",
                "title": "the model is miscalibrated",
                "narrative": "the probabilities do not mean what they say",
                "evidence": ["no_such_artifact"],
            }
        ]
    )
    run = run_validate(
        CREDIT, tmp_path / "out", llm=llm, config=Configuration.plain_llm, synthetic=SMALL
    )
    assert run.findings.findings == []
    declined = run.findings.candidates_not_promoted
    assert len(declined) == 1
    assert declined[0].defect_class.value == "C1"
    assert declined[0].tool == "plain_llm"
    assert declined[0].reason.startswith(UNEVIDENCED_PREFIX)
    assert "unevidenced_record.0" in run.store
    written = json.loads((run.out_dir / "findings.json").read_text(encoding="utf-8"))
    assert written["candidates_not_promoted"][0]["reason"].startswith(UNEVIDENCED_PREFIX)
    assert [call.tool for call in run.plan] == ["run_model"]


def test_plain_llm_promotes_a_finding_whose_evidence_does_resolve(tmp_path: Path) -> None:
    """The other half of the same rule: named evidence that exists makes an ordinary finding."""
    llm = SectionFake(
        plain_findings=[
            {
                "defect_class": "D1",
                "severity": "low",
                "title": "the training profile is worth a look",
                "narrative": "the raw profile carries the columns the model used",
                "evidence": ["plain_llm.profile"],
            }
        ]
    )
    run = run_validate(
        CREDIT, tmp_path / "out", llm=llm, config=Configuration.plain_llm, synthetic=SMALL
    )
    assert [finding.defect_class.value for finding in run.findings.findings] == ["D1"]
    assert run.findings.findings[0].tool == "plain_llm"
    assert run.findings.candidates_not_promoted == []


# --- the bounded follow-up loop ------------------------------------------------------------


def test_the_loop_runs_exactly_one_follow_up_then_stops(tmp_path: Path) -> None:
    """Spec 3.12's acceptance: a fake scripted to ask once then stop yields one extra tool call."""
    llm = SectionFake(
        plan_actions=[
            {
                "tool": "compute_metrics",
                "args": {
                    "splits": ["test"],
                    "subpopulation": {"column": "limit_bal", "rule": "below_median"},
                },
                "why": "does the model discriminate as well among low-limit clients?",
            },
            {"stop": True},
        ]
    )
    run = run_validate(CREDIT, tmp_path / "out", llm=llm, synthetic=SMALL)
    assert [step.accepted for step in run.steps] == [True, False]
    assert run.steps[0].call is not None
    assert run.steps[0].call.tool == "compute_metrics"
    assert "metrics.test.sub.limit_bal_low.auc" in run.store
    calls = TraceReader(run.out_dir / "trace.jsonl").events("tool_call")
    assert [event.payload["tool"] for event in calls].count("compute_metrics") == 2


def test_an_unknown_tool_is_refused_and_traced_and_never_executed(tmp_path: Path) -> None:
    """Spec 3.12's second acceptance, with the refusal readable from the trace alone."""
    llm = SectionFake(
        plan_actions=[
            {"tool": "check_everything", "args": {}, "why": "a tool that does not exist"},
            {"stop": True},
        ]
    )
    run = run_validate(CREDIT, tmp_path / "out", llm=llm, synthetic=SMALL)
    assert [step.accepted for step in run.steps] == [False, False]
    assert "there is no tool named" in run.steps[0].reason
    steps = TraceReader(run.out_dir / "trace.jsonl").events("plan_step")
    assert steps[0].payload["accepted"] is False
    assert steps[0].payload["tool"] == "check_everything"
    calls = TraceReader(run.out_dir / "trace.jsonl").events("tool_call")
    assert all(event.payload["tool"] != "check_everything" for event in calls)


def _front(report: str) -> dict[str, object]:
    """Parse a report's YAML front matter."""
    import yaml

    loaded = yaml.safe_load(report.split("---\n")[1])
    assert isinstance(loaded, dict)
    return loaded


def _finding_set(run: ValidationRun) -> set[tuple[str, str]]:
    """The run's findings as `(defect class, severity)` pairs, so a test can assert the set.

    D-017 is a statement about the whole set and not about one member of it: the clean synthetic
    `credit_default` panel yields exactly `{E1 low}`. A case that asserts `"E1" in` the list would
    pass on a panel that also raised `T1` and `C1`, which is what 1,200 rows does (D-119).
    """
    return {(f.defect_class.value, f.severity.value) for f in run.findings.findings}


# --- the Phase 9 follow-up: an inapplicable request, and a tool that raises ----------------------


def test_an_inapplicable_tool_is_refused_and_the_run_still_drafts(tmp_path: Path) -> None:
    """The second live attempt's action on the subject it was made against (D-089).

    `credit_default` declares no `regime.column`, so `check_stability` is not on the menu and a
    request for it is refused before anything runs. The run then does what the attempt did not: it
    drafts, verifies, repairs and renders.
    """
    llm = SectionFake(
        plan_actions=[
            {
                "tool": "check_stability",
                "args": {"split": "test"},
                "why": "regime-dependent degradation out of sample is still untested",
            },
            {"stop": True},
        ]
    )
    run = run_validate(CREDIT, tmp_path / "out", llm=llm)

    assert [step.accepted for step in run.steps] == [False, False]
    assert [step.executed for step in run.steps] == [False, False]
    assert run.steps[0].reason.startswith("not applicable to this package:")
    assert "declares no `regime.column`" in run.steps[0].reason

    steps = TraceReader(run.out_dir / "trace.jsonl").events("plan_step")
    assert steps[0].payload["tool"] == "check_stability"
    assert steps[0].payload["accepted"] is False
    assert steps[0].payload["executed"] is False
    calls = TraceReader(run.out_dir / "trace.jsonl").events("tool_call")
    assert all(event.payload["tool"] != "check_stability" for event in calls)

    assert (
        check_report(
            run.report,
            run.configuration,
            run.claims.post_repair,
            package_version=run.package.spec.version,
        )
        == []
    )
    assert run.precision_post == 1.0
    assert _finding_set(run) == {("E1", "low")}, "D-017 still holds when a step is refused"
    assert "`check_stability` (R1)" in run.report


def test_a_follow_up_that_raises_inside_the_tool_still_produces_a_report(tmp_path: Path) -> None:
    """D-088: accepted, executed false, the message on the step -- and a finished report.

    `check_collinearity` applies to this package and its `Args` take any split name, so a split
    the package does not declare is refused by the tool and not by the planner. That is the shape
    the second live attempt died in, and this asserts that it no longer ends the run.
    """
    llm = SectionFake(
        plan_actions=[
            {
                "tool": "check_collinearity",
                "args": {"split": "out_of_time"},
                "why": "collinearity may differ out of time",
            },
            {"stop": True},
        ]
    )
    run = run_validate(CREDIT, tmp_path / "out", llm=llm)

    assert [step.accepted for step in run.steps] == [True, False]
    assert run.steps[0].executed is False
    assert "does not declare a split named 'out_of_time'" in run.steps[0].error
    assert run.steps[0].reason == ""
    assert run.steps[0].call is not None

    events = TraceReader(run.out_dir / "trace.jsonl")
    steps = events.events("plan_step")
    assert steps[0].payload["accepted"] is True
    assert steps[0].payload["executed"] is False
    assert "out_of_time" in steps[0].payload["error"]
    collinearity = [
        event
        for event in events.events("tool_call")
        if event.payload["tool"] == "check_collinearity"
    ]
    assert [event.payload["ok"] for event in collinearity] == [True, False]

    assert run.report_path.is_file()
    assert (
        check_report(
            run.report,
            run.configuration,
            run.claims.post_repair,
            package_version=run.package.spec.version,
        )
        == []
    )
    assert run.precision_post == 1.0
    assert _finding_set(run) == {("E1", "low")}, "D-017 still holds when a step's tool raises"


# --- the Phase 9 follow-up 4: an executed step reaches the prose (D-101, D-102) -----------------

SLICE_ACTIONS = [
    {
        "tool": "compute_metrics",
        "args": {
            "splits": ["test"],
            "subpopulation": {"column": "limit_bal", "rule": "below_median"},
        },
        "why": "does discrimination hold on the low-limit half, or only in aggregate?",
    },
    {"stop": True},
]
"""One sub-population step, the shape three of the fourth live run's four steps took."""


def _section(report: str, heading: str) -> str:
    """Return one level-2 section of a rendered report."""
    from quaestor.report.schema import REQUIRED_HEADINGS

    headings = list(REQUIRED_HEADINGS)
    after = report.split(heading, 1)[1]
    later = [item for item in headings[headings.index(heading) + 1 :] if item in after]
    return after.split(later[0], 1)[0] if later else after


def test_a_material_follow_up_is_reported_and_raised_as_an_open_item(tmp_path: Path) -> None:
    """The gap bound is lowered so that this slice qualifies; nothing else about the run changes."""
    run = run_validate(
        CREDIT,
        tmp_path / "out",
        llm=SectionFake(plan_actions=list(SLICE_ACTIONS)),
        synthetic=SMALL,
        thresholds=Thresholds({SLICE_GAP_BOUND: 0.01}),
    )
    slice_auc = "metrics.test.sub.limit_bal_low.auc"
    assert run.store.value("metrics.test.sub.limit_bal_low.auc_gap") > 0.01
    outcomes = _section(run.report, "## 4. Outcomes analysis")
    findings = _section(run.report, "## 6. Findings and recommendations")
    assert FOLLOW_UPS_HEADING in outcomes
    assert slice_auc in outcomes.split(FOLLOW_UPS_HEADING, 1)[1]
    assert slice_auc in findings.split(OPEN_ITEMS_HEADING, 1)[1]
    assert "finding" not in findings.split(OPEN_ITEMS_HEADING, 1)[1].lower()


# --- D-177: a check of the checklist that raises costs its own row, not the run ----------------


def _raising(message: str) -> Any:
    """A `Tool.run` that raises `ToolError` the way a check that cannot answer does."""

    def run(self: Any, args: Any, ctx: Any) -> Any:
        raise ToolError(message, fix="quaestor tool check_collinearity --help")

    return run


def test_a_checklist_check_that_raises_leaves_a_report_and_an_appendix_d_row(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """D-088 said a `ToolError` from the rule-based plan is the run's failure; D-177 reverses it.

    Eleven checks' worth of artifacts and, under `full_agent`, a paid model call were being thrown
    away over one check that could not answer. The report is written without it and says so.
    """
    monkeypatch.setattr(
        CheckCollinearityTool, "run", _raising("the design matrix is singular on this split")
    )
    run = run_validate(CREDIT, tmp_path / "out", synthetic=SMALL)
    assert [(item.tool, item.message) for item in run.checks_failed] == [
        ("check_collinearity", "the design matrix is singular on this split")
    ]
    appendix = run.report.split("## Appendix D — Not checked", 1)[1]
    assert "`check_collinearity` (M1)" in appendix
    assert "did not run: the design matrix is singular on this split" in appendix


def test_a_check_that_raised_screened_for_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`checks_without_candidates` is a claim that a check looked and found nothing (D-088)."""
    monkeypatch.setattr(CheckCollinearityTool, "run", _raising("singular"))
    run = run_validate(CREDIT, tmp_path / "out", synthetic=SMALL)
    assert "check_collinearity" not in run.findings.checks_without_candidates
    assert "compute_metrics" in run.findings.checks_without_candidates


def test_the_trace_says_which_check_died_and_what_it_said(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`ok: false` could not say why, and once the run survives the trace is the only record."""
    monkeypatch.setattr(CheckCollinearityTool, "run", _raising("the design matrix is singular"))
    run = run_validate(CREDIT, tmp_path / "out", synthetic=SMALL)
    events = [
        event
        for event in TraceReader(run.out_dir / "trace.jsonl").events()
        if event.type.value == "tool_call" and event.payload.get("tool") == "check_collinearity"
    ]
    assert len(events) == 1
    assert events[0].payload["ok"] is False
    assert events[0].payload["error"] == "the design matrix is singular"


def test_a_clean_run_has_no_failed_check_and_no_such_appendix_row(credit: ValidationRun) -> None:
    """The row exists only when it is true; every run this repository commits has none."""
    assert credit.checks_failed == []
    assert "did not run:" not in credit.report


def test_the_subject_run_failing_is_still_the_runs_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`run_model` is the one call D-177 leaves fatal: everything after it reads what it wrote."""
    monkeypatch.setattr(RunModelTool, "run", _raising("the package has no `code/` directory"))
    with pytest.raises(ToolError, match="no `code/` directory"):
        run_validate(CREDIT, tmp_path / "out", synthetic=SMALL)


def test_a_sign_disagreement_reaches_section_six_without_any_loop_step(tmp_path: Path) -> None:
    """The observation D-096 named as an example and no report had ever written (D-173).

    `sign_check.*` belongs to section 2's selector and to no step of the bounded loop, so before
    the minting rule there was no path by which section 6 could learn of it: its brief named the
    kind of thing and its artifact list carried none of them. Here the loop runs nothing at all
    and the disagreement is still an open item, cited, on a run whose finding set is unchanged.
    """
    run = run_validate(CREDIT, tmp_path / "out")
    disagreeing = [
        name
        for name in run.store.names()
        if name.startswith("sign_check.")
        and name.endswith(".agrees")
        and run.store.value(name) == 0.0
    ]
    assert disagreeing, "the synthetic credit champion fits at least one contradicting sign"
    items = open_items(run.store, Thresholds().values)
    assert [item.subject for item in items] == [
        name[len("sign_check.") : -len(".agrees")] for name in disagreeing
    ]
    written = _section(run.report, "## 6. Findings and recommendations")
    written = written.split(OPEN_ITEMS_HEADING, 1)[1]
    for name in disagreeing:
        assert f":{name}]]" in written
    assert "finding" not in written.lower()
    assert [(f.defect_class, f.severity) for f in run.findings.findings] == [
        (DefectClass.E1, Severity.low)
    ], "D-017's finding set is what a prompt-text change may not move"


def test_a_follow_up_inside_the_bound_stays_in_the_section_that_computed_it(
    tmp_path: Path,
) -> None:
    """The same step at the shipped bound: reported, and no open item (D-102)."""
    run = run_validate(
        CREDIT,
        tmp_path / "out",
        llm=SectionFake(plan_actions=list(SLICE_ACTIONS)),
        synthetic=SMALL,
    )
    slice_auc = "metrics.test.sub.limit_bal_low.auc"
    assert run.store.value("metrics.test.sub.limit_bal_low.auc_gap") < run.store.value(
        SLICE_GAP_BOUND
    )
    outcomes = _section(run.report, "## 4. Outcomes analysis")
    findings = _section(run.report, "## 6. Findings and recommendations")
    assert slice_auc in outcomes.split(FOLLOW_UPS_HEADING, 1)[1]
    assert slice_auc not in findings


def test_a_slice_below_the_size_floor_never_reaches_the_open_items(tmp_path: Path) -> None:
    """The floor overrides the gap: a small slice's gap is sampling noise, not a question."""
    run = run_validate(
        CREDIT,
        tmp_path / "out",
        llm=SectionFake(plan_actions=list(SLICE_ACTIONS)),
        synthetic=SMALL,
        thresholds=Thresholds({SLICE_GAP_BOUND: 0.01, SLICE_SHARE_FLOOR: 0.9}),
    )
    slice_auc = "metrics.test.sub.limit_bal_low.auc"
    assert run.store.value("metrics.test.sub.limit_bal_low.share") < 0.9
    outcomes = _section(run.report, "## 4. Outcomes analysis")
    findings = _section(run.report, "## 6. Findings and recommendations")
    assert slice_auc in outcomes.split(FOLLOW_UPS_HEADING, 1)[1]
    assert slice_auc not in findings


def test_a_slice_that_is_the_whole_split_is_refused_and_the_report_still_renders(
    tmp_path: Path,
) -> None:
    """D-121 end to end: the shape the sixth live run's third step took, and what it costs now.

    That step asked for `delinq_count_6m above_median` on a column whose median is 0, and the tool
    answered -- share 1 on both splits, an AUC gap of 0, and a paragraph of section 4 reporting the
    split to itself. The ceiling is lowered here so the same refusal fires on a slice the synthetic
    panel does have, because what is under test is the path and not the number: the step is
    recorded accepted and not executed, its message reaches the trace and the next step's prompt
    (D-088), nothing of the slice is in the store, `### Follow-up analyses` is absent because no
    step executed, and the report renders and validates.
    """
    llm = SectionFake(plan_actions=list(SLICE_ACTIONS))
    run = run_validate(
        CREDIT,
        tmp_path / "out",
        llm=llm,
        thresholds=Thresholds({SLICE_SHARE_CEILING: 0.4}),
    )

    assert [step.accepted for step in run.steps] == [True, False]
    assert run.steps[0].executed is False
    assert run.steps[0].reason == ""
    assert "limit_bal <= median(limit_bal)" in run.steps[0].error
    assert SLICE_SHARE_CEILING in run.steps[0].error

    step = TraceReader(run.out_dir / "trace.jsonl").events("plan_step")[0]
    assert step.payload["accepted"] is True
    assert step.payload["executed"] is False
    assert "median(limit_bal)" in step.payload["error"]
    assert not [name for name in run.store.names() if ".sub.limit_bal_low" in name]
    assert FOLLOW_UPS_HEADING not in run.report

    assert run.report_path.is_file()
    assert (
        check_report(
            run.report,
            run.configuration,
            run.claims.post_repair,
            package_version=run.package.spec.version,
        )
        == []
    )
    assert run.precision_post == 1.0
    assert _finding_set(run) == {("E1", "low")}, "D-017 still holds when a slice is refused"


def test_the_loop_is_told_that_a_slice_which_is_the_whole_split_is_refused(
    tmp_path: Path,
) -> None:
    """D-122: the planner is told the rule before it spends a step finding it out.

    The example the rule carries is pinned as well, because D-146 found it falsified by D-122
    itself: under `above_median` = `> median`, a column whose median is its minimum selects at
    most half the split, so the sentence's own first clause made its own example impossible. The
    degenerate median rule is `below_median` on a column whose median is its *maximum*.
    """
    llm = SectionFake(plan_actions=[{"stop": True}])
    run_validate(CREDIT, tmp_path / "out", llm=llm, synthetic=SMALL)
    prompt = next(call.prompt for call in llm.calls if "You are the planning half" in call.prompt)
    assert "A sub-population must be a proper part of the split." in prompt
    assert "a rule that resolves to the whole of it" in prompt
    assert "`below_median` on a column whose median is also its\nmaximum" in prompt
    assert "`above_median` on a column whose median is also its" not in prompt
    assert "`above_median` the rows strictly above it" in prompt
    assert "is refused with the share it selected" in prompt


def test_a_run_whose_loop_stopped_carries_no_follow_up_subsection(credit: ValidationRun) -> None:
    """The heading is required of the sections the loop ran a step for, and of no others."""
    assert FOLLOW_UPS_HEADING not in credit.report


def test_the_loop_is_shown_the_columns_it_can_slice_on(tmp_path: Path) -> None:
    """D-107: the step that asked for `credit_limit` on a subject whose column is `limit_bal`."""
    llm = SectionFake(plan_actions=[{"stop": True}])
    run_validate(CREDIT, tmp_path / "out", llm=llm, synthetic=SMALL)
    plan_prompts = [call.prompt for call in llm.calls if "You are the planning half" in call.prompt]
    assert len(plan_prompts) == 1
    assert "`limit_bal`" in plan_prompts[0]
    assert "`credit_limit`" not in plan_prompts[0]
    assert "`default_next_month`" in plan_prompts[0]


def test_a_follow_up_reports_its_metrics_as_a_table_and_interprets_them_in_prose(
    tmp_path: Path,
) -> None:
    """D-115: the ten metrics are a rendered table, and the gap and the share stay cited prose."""
    run = run_validate(
        CREDIT,
        tmp_path / "out",
        llm=SectionFake(plan_actions=list(SLICE_ACTIONS)),
        synthetic=SMALL,
    )
    table = "metrics.test.sub.limit_bal_low"
    assert run.store.entry(table).kind is ArtifactKind.table
    rows = run.store.load(table)
    assert [str(row["metric"]) for row in rows] == [*SCALAR_METRICS, "mean_rel_gap", "share"]
    outcomes = _section(run.report, "## 4. Outcomes analysis")
    assert f"<!-- quaestor:renderer:begin table {table} -->" in outcomes
    assert f"[[table:{table}]]" not in outcomes, "the directive is expanded, not left standing"
    follow_ups = outcomes.split(FOLLOW_UPS_HEADING, 1)[1]
    assert f"{table}.auc_gap" in follow_ups
    assert f"{table}.share" in follow_ups
    claims = {claim.citation for claim in run.claims.post_repair if claim.citation}
    assert any(f"{table}.auc_gap" in citation for citation in claims)
    assert any(f"{table}.share" in citation for citation in claims)
