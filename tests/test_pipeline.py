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
from pathlib import Path

import jsonschema
import pytest

from quaestor import Configuration, TraceReader, validate
from quaestor.pipeline import UNEVIDENCED_PREFIX, ValidationRun
from quaestor.report import UNVERIFIED_OPEN, check_report
from reportsupport import SectionFake

REPO_ROOT = Path(__file__).resolve().parents[1]
GOLDEN = REPO_ROOT / "examples" / "golden_report"
CREDIT = REPO_ROOT / "subjects" / "credit_default"
MSR = REPO_ROOT / "subjects" / "msr_prepayment"
SMALL = 1200
"""How many rows the variant runs generate: enough for every tool, small enough to run six times."""


def run_validate(
    package: Path,
    out: Path,
    *,
    llm: SectionFake | None = None,
    config: Configuration = Configuration.full_agent,
    synthetic: int = 5000,
) -> ValidationRun:
    """Run the pipeline once, offline, with the shared fake."""
    return validate(
        package,
        llm=llm or SectionFake(),
        config=config,
        synthetic=synthetic,
        out=out,
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
    run = run_validate(CREDIT, tmp_path / "out", llm=llm, synthetic=SMALL)

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
    assert "E1" in [finding.defect_class.value for finding in run.findings.findings]
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
    run = run_validate(CREDIT, tmp_path / "out", llm=llm, synthetic=SMALL)

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
    assert "E1" in [finding.defect_class.value for finding in run.findings.findings]
