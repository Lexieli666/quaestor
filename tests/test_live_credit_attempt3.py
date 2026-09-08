"""The third live validation: the first one that rendered, and the two sentences it got wrong.

`eval/results/first-live/credit-attempt3/` is the record of the run of 2026-09-08 that reached a
report: 19 model calls, 13 tool calls, 159 post-repair claims, grounding precision 0.9816 before
repair and 1.0000 after, no finding, exit 0. Two of its sentences are false, and both are the
tool's fault rather than the model's -- section 3 called an overlap "recorded as a finding" while
section 6 said none was raised, and section 4.4 said PSI had not been recomputed while sections 1
and 3 both cited `psi.max`. `docs/EVALUATION.md` section 1 writes the run up; this module is the
half of the write-up a machine checks.

Every figure asserted here is re-derived from `trace.jsonl`, `claims.json`, `findings.json`, the
19 cassettes and the artifact index of that directory, so a number that drifts from the run fails
the suite. Nothing here calls a model: the cassettes are read as JSON, and the one provider
touched is `ClaudeCLILLM`'s payload mapping, driven over the attempt's own recorded `usage`
objects.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

import pytest

from quaestor import TraceReader
from quaestor.artifacts.store import ArtifactStore
from quaestor.configs import config_for
from quaestor.package import load_package
from quaestor.pipeline import _run_id
from quaestor.report.renderer import _numbers_removed, _table_cell
from quaestor.report.sections import artifact_briefs, brief_for
from quaestor.tools import ToolContext, default_registry
from quaestor.tools.leakage import DUPLICATE_MULTIPLE, FEATURE_OVERLAP_BOUND
from quaestor.tools.metrics import THRESHOLD_TABLE
from quaestor.tools.run import MAX_SECONDS_NAME
from quaestor.trace import EventType, TraceEvent, TraceWriter
from quaestor.vocab import Configuration, ReportSection

REPO_ROOT: Final = Path(__file__).resolve().parents[1]
CREDIT: Final = REPO_ROOT / "subjects" / "credit_default"
ATTEMPT: Final = REPO_ROOT / "eval" / "results" / "first-live" / "credit-attempt3"
"""The committed record of the run this module is about."""

ATTEMPT_1: Final = REPO_ROOT / "eval" / "results" / "first-live" / "credit-attempt1"
"""The first attempt, whose run id this one shares -- which is the defect D-093 closes."""

ROW_LEVEL: Final = (
    "run.data_train",
    "run.data_test",
    "run.predictions_train",
    "run.predictions_test",
)
"""The four artifacts whose payload the repository deliberately does not hold (D-087)."""

SHARED_RUN_ID: Final = "credit_default-full_agent-d03b07c6"
"""The identifier attempts 1 and 3 both carry: one string, two runs, one build apart."""


def _events() -> list[TraceEvent]:
    """Every event of the attempt's trace, in file order."""
    return list(TraceReader(ATTEMPT / "trace.jsonl"))


def _of(kind: EventType) -> list[TraceEvent]:
    """The attempt's events of one type."""
    return [event for event in _events() if event.type is kind]


def _report() -> str:
    """The attempt's rendered report, as committed."""
    return (ATTEMPT / "report.md").read_text(encoding="utf-8")


def _index() -> dict[str, Any]:
    """The attempt's artifact index: every logical name the run stored."""
    payload = json.loads((ATTEMPT / "artifacts" / "index.json").read_text(encoding="utf-8"))
    return dict(payload["artifacts"])


TODAY_PLAN: Final = (
    ("run_model", {"synthetic": 5000}),
    ("profile_data", {}),
    ("compute_metrics", {}),
    ("check_leakage", {}),
    ("check_collinearity", {}),
    ("challenger_compare", {}),
)
"""The attempt's own rule-based plan, less the seven guidance calls, which store no scalar.

5,000 rows because that is the clean synthetic control D-017 fixes; a smaller panel moves the
calibration slope enough to fail a declared threshold, which would make this fixture a test of the
sample size rather than of the table.
"""


@pytest.fixture(scope="module")
def today(tmp_path_factory: pytest.TempPathFactory) -> ArtifactStore:
    """The store the same plan fills on this build, for the "and now" half of each defect."""
    out = tmp_path_factory.mktemp("attempt3_today")
    ctx = ToolContext(
        package=load_package(CREDIT),
        store=ArtifactStore(out / "artifacts"),
        out_dir=out / "run",
        trace=TraceWriter(out / "trace.jsonl", run_id="attempt3-today"),
    )
    registry = default_registry()
    for tool, args in TODAY_PLAN:
        registry.call(tool, dict(args), ctx)
    return ctx.store


def _cassettes() -> list[dict[str, Any]]:
    """The attempt's 19 tapes, in file-name order."""
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((ATTEMPT / "cassettes").glob("*.json"))
    ]


# --- what the run did -------------------------------------------------------------------------


def test_the_trace_is_the_run_the_evaluation_describes() -> None:
    """The shape of the record: 282 events, 19 model calls, 13 tool calls, 2 repair rounds."""
    counts = Counter(event.type for event in _events())
    assert sum(counts.values()) == 282
    assert counts[EventType.llm_call] == 19
    assert counts[EventType.tool_call] == 13
    assert counts[EventType.plan_step] == 1
    assert counts[EventType.repair] == 2
    assert counts[EventType.claim_check] == 247


def test_nineteen_model_calls_are_one_plan_nine_drafts_and_nine_extractions() -> None:
    """Seven sections drafted and extracted, plus two repair re-drafts and their re-extractions."""
    calls = _of(EventType.llm_call)
    assert Counter(str(event.payload["purpose"]) for event in calls) == {
        "draft": 9,
        "extract": 9,
        "plan": 1,
    }
    repairs = [event for event in calls if event.payload.get("repair")]
    assert [str(event.payload["section"]) for event in repairs] == ["data_integrity", "outcomes"]


def test_the_plan_ran_clean_and_the_loop_stopped_at_once() -> None:
    """Thirteen rule-based calls, no candidate from any of them, and no follow-up asked for."""
    tools = _of(EventType.tool_call)
    assert Counter(str(event.payload["tool"]) for event in tools) == {
        "retrieve_guidance": 7,
        "run_model": 1,
        "profile_data": 1,
        "compute_metrics": 1,
        "check_leakage": 1,
        "check_collinearity": 1,
        "challenger_compare": 1,
    }
    assert all(event.payload["ok"] for event in tools)
    assert [event.payload["candidates"] for event in tools if event.payload["candidates"]] == []
    assert sum(float(event.payload["duration_s"]) for event in tools) == pytest.approx(
        2.888, abs=1e-3
    )
    step = _of(EventType.plan_step)[0]
    assert step.payload["stop"] is True
    assert step.payload["reason"] == "the planner stopped"


def test_the_claims_are_the_figures_the_front_matter_prints() -> None:
    """159 post-repair claims, 0.9816 -> 1.0000, and no finding at any severity."""
    claims = json.loads((ATTEMPT / "claims.json").read_text(encoding="utf-8"))
    assert claims["grounding"]["pre_repair"]["precision"] == 0.9816
    assert claims["grounding"]["post_repair"]["precision"] == 1.0
    assert claims["grounding"]["post_repair"]["n_claims"] == 159
    assert json.loads((ATTEMPT / "findings.json").read_text(encoding="utf-8"))["findings"] == []
    statuses = Counter(str(event.payload["status"]) for event in _of(EventType.claim_check))
    assert statuses == {"verified": 244, "unattributed": 2, "unsupported": 1}


def test_the_bill_is_what_the_evaluation_quotes() -> None:
    """104,675 output tokens, $4.3822, 1,217.79 s from the first traced event to the last."""
    calls = _of(EventType.llm_call)
    assert sum(int(event.payload["tokens_out"]) for event in calls) == 104_675
    assert sum(float(event.payload["cost_usd"]) for event in calls) == pytest.approx(
        4.3822, abs=5e-5
    )
    extraction = [event for event in calls if event.payload["purpose"] == "extract"]
    assert sum(int(event.payload["tokens_out"]) for event in extraction) == 70_147
    events = _events()
    span = (events[-1].ts - events[0].ts).total_seconds()
    assert span == pytest.approx(1217.79, abs=0.01)


# --- the first false sentence: a bound that was not an artifact (D-091) -------------------------


def test_section_three_called_it_a_finding_and_section_six_said_none_was_raised() -> None:
    """The contradiction, quoted from the committed report so the record is the record."""
    report = _report()
    assert "this is recorded as a finding rather than as an observation" in report
    assert "No finding was raised for the credit_default version 1.0 model package" in report
    assert json.loads((ATTEMPT / "findings.json").read_text(encoding="utf-8"))["findings"] == []


def test_the_bound_the_l2_rule_applied_was_not_in_that_run_s_store() -> None:
    """The cause: the drafter compared 0.01256 with 0.005 because 0.02324 did not exist (D-091)."""
    index = _index()
    assert "threshold.L2.overlap" in index
    assert "leakage.overlap.features" in index
    assert "leakage.duplicates.train" in index
    assert FEATURE_OVERLAP_BOUND not in index, (
        "the attempt stored the effective bound after all; the premise of D-091 is wrong"
    )
    store = ArtifactStore(ATTEMPT / "artifacts")
    declared = store.value("threshold.L2.overlap")
    overlap = store.value("leakage.overlap.features")
    duplicates = store.value("leakage.duplicates.train")
    applied = max(declared, DUPLICATE_MULTIPLE * duplicates)
    assert overlap > declared, "the comparison the drafter made was arithmetically right"
    assert overlap < applied, "the comparison the rule made raised nothing"
    assert applied == pytest.approx(0.023238, abs=1e-6)


def test_a_run_on_this_build_stores_the_bound_the_rule_applied(today: ArtifactStore) -> None:
    """And a report drafted today is shown it, because section 3's selector takes threshold.L2."""
    assert FEATURE_OVERLAP_BOUND in today
    briefs = artifact_briefs(today, brief_for(ReportSection.data_integrity))
    assert FEATURE_OVERLAP_BOUND in {item.name for item in briefs}
    assert today.value(FEATURE_OVERLAP_BOUND) == pytest.approx(
        max(
            today.value("threshold.L2.overlap"),
            DUPLICATE_MULTIPLE * today.value("leakage.duplicates.train"),
        )
    )


# --- the second false sentence: a table the drafter assembled (D-092) ---------------------------


def test_section_four_said_psi_was_not_recomputed_while_two_sections_cited_it() -> None:
    """The contradiction, and the runtime cap printed as a performance threshold."""
    report = _report()
    assert "| PSI, maximum | 0.25" in report
    assert "Not recomputed in the artifacts available to this section" in report
    assert "psi.max" in report, "sections 1 and 3 did cite it"
    assert "psi.max" in _index()
    assert "| Wall-clock seconds, maximum |" in report


def test_the_run_had_the_cap_inside_the_threshold_family_and_no_threshold_table() -> None:
    """Both halves of the cause, read off the attempt's own index (D-092)."""
    index = _index()
    assert "threshold.package.max_seconds" in index
    assert MAX_SECONDS_NAME == "runtime.max_seconds"
    assert MAX_SECONDS_NAME not in index
    assert THRESHOLD_TABLE not in index


def test_a_run_on_this_build_writes_the_threshold_table_and_keeps_the_cap_out_of_it(
    today: ArtifactStore,
) -> None:
    """One row per declared bound, computed by the tool; the cap is a runtime artifact."""
    assert MAX_SECONDS_NAME in today
    assert "threshold.package.max_seconds" not in today
    rows = today.load(THRESHOLD_TABLE)
    assert [row["metric"] for row in rows] == [
        "auc",
        "brier",
        "calibration_slope",
        "calibration_slope",
        "psi",
    ]
    assert {row["result"] for row in rows} == {"pass"}


# --- what the record could not say about itself (D-093, D-097) ---------------------------------


def test_the_front_matter_recorded_the_adapter_and_the_trace_the_model() -> None:
    """`model: claude-cli` is the subprocess; every one of the 19 calls names the model (D-093)."""
    assert "model: claude-cli" in _report()
    models = {str(event.payload["model"]) for event in _of(EventType.llm_call)}
    assert models == {"claude-opus-5[1m]"}


def test_the_cli_now_counts_the_cached_input_tokens_the_attempt_paid_for() -> None:
    """38 tokens in for 19 calls, against 176,851 across the three usage fields (D-093)."""
    recorded = sum(int(event.payload["tokens_in"]) for event in _of(EventType.llm_call))
    assert recorded == 38
    tapes = _cassettes()
    assert len(tapes) == 19
    counted = sum(_input_tokens_of(dict(tape["completion"]["raw"]["usage"])) for tape in tapes)
    assert counted == 176_851
    assert counted > recorded * 1000


def _input_tokens_of(usage: dict[str, Any]) -> int:
    """What `ClaudeCLILLM` now reports for one recorded `usage` object."""
    from quaestor.llm.claude_cli import _input_tokens

    counted = _input_tokens(usage)
    assert counted is not None
    return counted


def test_attempts_one_and_three_share_a_run_id_and_two_runs_today_do_not() -> None:
    """A joining key that joins each report to two traces, closed by a stamp (D-093)."""
    assert SHARED_RUN_ID in _report()
    first = (ATTEMPT_1 / "trace.jsonl").read_text(encoding="utf-8")
    assert SHARED_RUN_ID in first
    package = load_package(CREDIT)
    config = config_for(Configuration.full_agent)
    args = (package, config, "real", None, None)
    early = _run_id(*args, datetime(2026, 9, 8, 3, 40, 14, tzinfo=UTC))
    late = _run_id(*args, datetime(2026, 9, 8, 6, 39, 34, tzinfo=UTC))
    assert early != late
    assert early.endswith(late.rsplit("-", 1)[1]), "same inputs still hash the same"
    assert late == "credit_default-full_agent-20260908T063934Z-" + late.rsplit("-", 1)[1]


def test_the_appendix_said_zero_repairs_of_a_run_that_removed_three_numbers() -> None:
    """Only rewrites become `repairs` rows; the removals are on the trace (D-097)."""
    assert "after 0 repaired claim(s)" in _report()
    assert json.loads((ATTEMPT / "claims.json").read_text(encoding="utf-8"))["repairs"] == []
    rounds = _of(EventType.repair)
    assert [list(event.payload["removed"]) for event in rounds] == [[9.982, 6.0], [50.0]]
    assert all(event.payload["repaired"] == [] for event in rounds)
    assert _numbers_removed(_events()) == 3


def test_the_expanded_tables_printed_ten_digits_beside_four_figure_prose() -> None:
    """The decile table's own cells, quoted; `_table_cell` now prints them at four (D-094)."""
    report = _report()
    assert "| 1 | 900 | 617 | 0.6855555556 | 3.098945254 |" in report
    assert "0.4952 " in report, "the prose beside it wrote four significant figures"
    assert _table_cell("0.6855555556") == "0.6856"
    assert _table_cell("3.098945254") == "3.099"
    assert _table_cell("900") == "900"


# --- what D-085 actually saved, measured across the two runs -----------------------------------


def _extraction_split(attempt: Path) -> tuple[int, int, int]:
    """One attempt's extraction calls, total output tokens and thinking tokens, from its tapes."""
    calls = output = thinking = 0
    for path in sorted((attempt / "cassettes").glob("*.json")):
        tape = json.loads(path.read_text(encoding="utf-8"))
        if "You are extracting the numeric claims" not in tape["request"]["prompt"]:
            continue
        usage = tape["completion"]["raw"]["usage"]
        calls += 1
        output += int(usage["output_tokens"])
        thinking += int(usage["output_tokens_details"]["thinking_tokens"])
    return calls, output, thinking


def _claim_checks(attempt: Path) -> int:
    """How many claims one attempt's extractor produced verdicts for, over every pass."""
    return sum(
        1 for event in TraceReader(attempt / "trace.jsonl") if event.type is EventType.claim_check
    )


def test_the_extractor_s_answer_more_than_halved_per_claim_and_the_bill_did_not_fall() -> None:
    """D-085 promised the saving would be measured on the next live run, not estimated."""
    first_calls, first_out, first_think = _extraction_split(ATTEMPT_1)
    third_calls, third_out, third_think = _extraction_split(ATTEMPT)
    assert (first_calls, first_out, first_think) == (8, 63_865, 33_833)
    assert (third_calls, third_out, third_think) == (9, 70_147, 47_550)
    assert third_out > first_out, "the bill went up"

    first_answer = (first_out - first_think) / _claim_checks(ATTEMPT_1)
    third_answer = (third_out - third_think) / _claim_checks(ATTEMPT)
    assert round(first_answer) == 168
    assert round(third_answer) == 91
    assert first_think / first_out == pytest.approx(0.53, abs=0.005)
    assert third_think / third_out == pytest.approx(0.68, abs=0.005)


# --- what is committed, and what is not (D-087) ------------------------------------------------


def test_the_row_level_artifacts_are_listed_and_their_payloads_are_not_here() -> None:
    """The index is the run's inventory; the four largest payloads are deliberately absent."""
    index = _index()
    assert len(index) == 124
    for name in ROW_LEVEL:
        assert name in index, name
        assert not (ATTEMPT / "artifacts" / f"{index[name]['hash']}.csv").exists()


def test_no_committed_file_of_the_attempt_is_row_sized() -> None:
    """`find eval/results/first-live/credit-attempt3 -size +20k` over the CSVs, as D-087 asks."""
    big = [path for path in ATTEMPT.rglob("*.csv") if path.stat().st_size > 20 * 1024]
    assert big == [], f"row-level files are committed: {big}"
