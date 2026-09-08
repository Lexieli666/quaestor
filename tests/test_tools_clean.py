"""Every tool over both clean synthetic subjects, end to end, with the candidate set asserted.

This is the Phase 5 half of the two expectations the earlier phases fixed at data level:

* `credit_default` at seed 20260901 and `--synthetic 5000` raises exactly `{E1}`, at severity
  `low`, because its generating process carries an interaction the additive champion cannot
  represent (DECISIONS D-017, D-036);
* `msr_prepayment` at seed 20260901 and `--synthetic 2000` raises exactly `{}` -- nothing at all --
  because the champion is the right functional form for its process (DECISIONS D-047).

Both are asserted here over the *tools*, which is as far as Phase 5 reaches; the pipeline-level
assertion, over findings and a rendered report, is Phase 8's. Every number quoted in the comments
below was measured by this test on this machine and is recorded in DECISIONS D-053.

The second thing this module checks is the golden report's Appendix B: every logical name
`examples/golden_report/report.md` cites, and that this phase is responsible for, resolves in a
real run's store. The golden report is the executable specification, so a citation it writes that
no tool produces would mean one of the two is wrong.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from quaestor import ArtifactStore, TraceReader, TraceWriter, load_package
from quaestor.tools import ToolContext, ToolResult, default_registry

CREDIT = Path(__file__).resolve().parent.parent / "subjects" / "credit_default"
MSR = Path(__file__).resolve().parent.parent / "subjects" / "msr_prepayment"

CREDIT_PLAN: list[tuple[str, dict[str, object]]] = [
    ("run_model", {"synthetic": 5000}),
    ("profile_data", {}),
    ("compute_metrics", {}),
    ("check_leakage", {}),
    ("check_collinearity", {}),
    ("challenger_compare", {}),
    # The bounded follow-up loop's question, which the golden report's section 4 asks: does the
    # model discriminate as well among low-limit clients?
    (
        "compute_metrics",
        {"splits": ["test"], "subpopulation": {"column": "limit_bal", "rule": "below_median"}},
    ),
    (
        "compute_metrics",
        {"splits": ["test"], "subpopulation": {"column": "limit_bal", "rule": "above_median"}},
    ),
]
"""The rule-based plan of spec 3.12 for a binary classifier, plus one follow-up."""

MSR_PLAN: list[tuple[str, dict[str, object]]] = [
    ("run_model", {"synthetic": 2000}),
    ("profile_data", {}),
    ("compute_metrics", {}),
    ("check_leakage", {}),
    ("check_stability", {}),
    ("check_collinearity", {}),
    ("challenger_compare", {}),
    ("run_scenarios", {}),
]
"""The same plan for a hazard subject: a regime column adds stability, scenarios add the shocks."""

GOLDEN_APPENDIX_B = [
    "calibration.mean_rel_gap.test",
    "calibration.test",
    "calibration_intercept.test",
    "calibration_slope.test",
    "challenger.auc",
    "challenger.brier",
    "challenger.delta_auc",
    "condition_number",
    "csi.max",
    "deciles.test",
    "deciles.test.top2_capture",
    "leakage.name_screen.n_matched",
    "leakage.overlap",
    "leakage.target_corr.max_single_feature_auc",
    "leakage.timing.n_flagged",
    "metrics.test.auc",
    "metrics.test.brier",
    "metrics.test.event_rate",
    "metrics.test.gini",
    "metrics.test.ks",
    "metrics.test.logloss",
    "metrics.test.mean_predicted",
    "metrics.test.n",
    "metrics.test.sub.limit_bal_high.auc",
    "metrics.test.sub.limit_bal_low.auc",
    "metrics.test.sub.limit_bal_low.n",
    "metrics.train.auc",
    "metrics.train.brier",
    "metrics.train.event_rate",
    "metrics.train.gini",
    "metrics.train.ks",
    "metrics.train.logloss",
    "metrics.train.n",
    "profile.test.missing.max",
    "profile.test.n",
    "profile.train.missing.max",
    "profile.train.n",
    "psi.max",
    "psi.utilisation",
    "psi.y_score",
    "rule.calibration_first_event_rate",
    "run.duration_s",
    "run.features",
    "run.metrics",
    "run.model_summary",
    "run.splits",
    "threshold.C1.mean_ratio_rel",
    "threshold.D1.missing_gap",
    "threshold.E1.delta_auc",
    "threshold.L1.single_feature_auc",
    "threshold.L2.overlap",
    "threshold.M1.condition_number",
    "threshold.M1.vif",
    "threshold.O1.auc_gap",
    "threshold.package.auc.test.min",
    "threshold.package.brier.test.max",
    "threshold.package.calibration_slope.test.max",
    "threshold.package.calibration_slope.test.min",
    "threshold.package.psi.max",
    "vif.max",
    "vif.utilisation",
]
"""Appendix B of `examples/golden_report/report.md`, less `guidance.*`, which is Phase 6's."""


def _run_plan(
    tmp_path: Path, package_dir: Path, plan: list[tuple[str, dict[str, object]]]
) -> tuple[ToolContext, list[ToolResult]]:
    """Run a whole plan over one clean subject, `run_model` included, and return every result."""
    ctx = ToolContext(
        package=load_package(package_dir),
        store=ArtifactStore(tmp_path / "artifacts"),
        out_dir=tmp_path / "run",
        trace=TraceWriter(tmp_path / "trace.jsonl", run_id=f"clean-{package_dir.name}"),
    )
    registry = default_registry()
    return ctx, [registry.call(tool, args, ctx) for tool, args in plan]


@pytest.fixture(scope="module")
def credit(tmp_path_factory: pytest.TempPathFactory) -> tuple[ToolContext, list[ToolResult]]:
    """Every tool over the clean synthetic `credit_default` subject, from the run onwards."""
    return _run_plan(tmp_path_factory.mktemp("clean_credit"), CREDIT, CREDIT_PLAN)


@pytest.fixture(scope="module")
def msr(tmp_path_factory: pytest.TempPathFactory) -> tuple[ToolContext, list[ToolResult]]:
    """Every tool over the clean synthetic `msr_prepayment` subject, from the run onwards."""
    return _run_plan(tmp_path_factory.mktemp("clean_msr"), MSR, MSR_PLAN)


def raised(results: list[ToolResult]) -> list[str]:
    """Every defect class the plan raised, sorted and deduplicated."""
    return sorted(
        {candidate.defect_class.value for result in results for candidate in result.candidates}
    )


# --- credit_default: exactly {E1}, as DECISIONS D-017 fixes ---------------------------------------


def test_the_clean_credit_subject_raises_exactly_e1(
    credit: tuple[ToolContext, list[ToolResult]],
) -> None:
    ctx, results = credit
    assert raised(results) == ["E1"]
    candidates = [candidate for result in results for candidate in result.candidates]
    assert len(candidates) == 1
    assert candidates[0].suggested_severity.value == "low"
    assert candidates[0].tool == "challenger_compare"
    # Every hash the candidate names is in the store, which is what a Finding requires in Phase 7.
    assert all(ctx.store.get(digest).hash == digest for digest in candidates[0].evidence)


def test_the_numbers_behind_the_credit_subjects_clean_run(
    credit: tuple[ToolContext, list[ToolResult]],
) -> None:
    ctx, _ = credit
    store = ctx.store
    # Discrimination and calibration: no O1, no C1.
    assert store.value("metrics.train.auc") == pytest.approx(0.7584, abs=0.001)
    assert store.value("metrics.test.auc") == pytest.approx(0.7480, abs=0.001)
    assert store.value("metrics.train.auc") - store.value("metrics.test.auc") < 0.08
    assert store.value("calibration_slope.test") == pytest.approx(1.0027, abs=0.01)
    assert store.value("calibration.mean_rel_gap.test") == pytest.approx(0.0159, abs=0.005)
    # Drift and integrity: no S1, no D1.
    assert store.value("psi.max") == pytest.approx(0.0102, abs=0.002)
    assert store.value("psi.y_score") == pytest.approx(0.0070, abs=0.002)
    assert store.value("profile.train.missing.max") == 0.0
    assert store.value("profile.test.missing.max") == 0.0
    # Leakage and contamination: no L1, no L2.
    assert store.value("leakage.timing.n_flagged") == 0
    assert store.value("leakage.target_corr.max_single_feature_auc") == pytest.approx(
        0.6831, abs=0.002
    )
    assert store.value("leakage.overlap.ids") == 0.0
    assert store.value("leakage.overlap.features") == 0.0
    assert store.value("leakage.duplicates.train") == 0.0
    assert store.value("leakage.overlap") == 0.0
    assert store.value("leakage.name_screen.n_matched") == 0
    # Collinearity: no M1, the screen having removed the pair (D-035, D-036).
    assert store.value("vif.max") == pytest.approx(7.295, abs=0.01)
    assert store.value("condition_number") == pytest.approx(5.547, abs=0.01)
    # Effective challenge: the one candidate.
    assert store.value("challenger.auc") == pytest.approx(0.8240, abs=0.001)
    assert store.value("challenger.delta_auc") == pytest.approx(0.0760, abs=0.001)


def test_every_golden_appendix_b_name_resolves_in_a_real_credit_run(
    credit: tuple[ToolContext, list[ToolResult]],
) -> None:
    ctx, _ = credit
    missing = [name for name in GOLDEN_APPENDIX_B if name not in ctx.store]
    assert missing == []


def test_the_credit_plan_writes_one_trace_event_per_tool_call(
    credit: tuple[ToolContext, list[ToolResult]],
) -> None:
    ctx, results = credit
    assert ctx.trace is not None
    events = TraceReader(ctx.trace.path).events("tool_call")
    assert len(events) == len(CREDIT_PLAN)
    assert [event.payload["tool"] for event in events] == [tool for tool, _ in CREDIT_PLAN]
    assert all(event.payload["ok"] for event in events)
    assert sum(len(event.payload["artifacts"]) for event in events) == sum(
        len(result.artifacts) for result in results
    )


# --- msr_prepayment: exactly {}, as DECISIONS D-047 fixes ----------------------------------------


def test_the_clean_hazard_subject_raises_nothing(msr: tuple[ToolContext, list[ToolResult]]) -> None:
    _, results = msr
    assert raised(results) == []


def test_the_numbers_behind_the_hazard_subjects_clean_run(
    msr: tuple[ToolContext, list[ToolResult]],
) -> None:
    ctx, _ = msr
    store = ctx.store
    # O1, both rules: the train-to-test gap is 0.0130, the out-of-time AUC is above test and the
    # vintage holdout is 0.0035 below it, against thresholds of 0.08 and 0.05 (D-053).
    assert store.value("metrics.train.auc") == pytest.approx(0.7883, abs=0.001)
    assert store.value("metrics.test.auc") == pytest.approx(0.7753, abs=0.001)
    assert store.value("metrics.out_of_time.auc") == pytest.approx(0.7846, abs=0.001)
    assert store.value("metrics.vintage_holdout.auc") == pytest.approx(0.7718, abs=0.001)
    # C1 on every split: every slope is inside [0.80, 1.20] and every mean-to-observed gap is
    # inside 25%, the widest being the vintage holdout's 0.8373 and 17.2%.
    for split in ("train", "test", "out_of_time", "vintage_holdout"):
        assert 0.80 <= store.value(f"calibration_slope.{split}") <= 1.20
        assert store.value(f"calibration.mean_rel_gap.{split}") <= 0.25
    assert store.value("calibration_slope.vintage_holdout") == pytest.approx(0.8373, abs=0.01)
    assert store.value("calibration.mean_rel_gap.vintage_holdout") == pytest.approx(0.172, abs=0.01)
    # S1 on train against test only (D-046): 0.065, where the out-of-time comparison is 3.09.
    assert store.value("psi.max") == pytest.approx(0.065, abs=0.005)
    assert store.value("psi.out_of_time.burnout") == pytest.approx(2.945, abs=0.05)
    # L1, L2, M1, E1.
    assert store.value("leakage.target_corr.max_single_feature_auc") == pytest.approx(
        0.7239, abs=0.002
    )
    assert store.value("leakage.overlap.ids") == 0.0
    assert store.value("leakage.overlap.features") == 0.0
    assert store.value("leakage.duplicates.train") == 0.0
    assert store.value("leakage.overlap") == 0.0
    assert store.value("vif.max") == pytest.approx(4.976, abs=0.01)
    assert store.value("condition_number") == pytest.approx(4.943, abs=0.01)
    assert store.value("challenger.delta_auc") == pytest.approx(-0.0415, abs=0.001)
    # R1: the regime AUCs differ by 0.0011 and no retained coefficient flips sign.
    regimes = {row["regime"]: float(row["auc"]) for row in store.load("stability.auc_by_regime")}
    assert regimes["falling"] == pytest.approx(0.7227, abs=0.002)
    assert regimes["rising"] == pytest.approx(0.7238, abs=0.002)
    assert abs(regimes["falling"] - regimes["rising"]) < 0.10
    # X1: monotone, and negatively convex as package.yaml declares.
    assert store.value("scenario.value_change.-300") == pytest.approx(-1_297_986, rel=0.01)
    assert store.value("scenario.value_change.300") == pytest.approx(168_055, rel=0.01)
    assert store.value("scenario.convexity") == pytest.approx(-1_129_932, rel=0.01)


def test_the_hazard_subject_gets_the_cpr_table_a_prepayment_reader_wants(
    msr: tuple[ToolContext, list[ToolResult]],
) -> None:
    ctx, _ = msr
    rows = ctx.store.load("cpr.test")
    assert list(rows[0]) == ["period", "n", "actual_cpr", "predicted_cpr"]
    assert len(rows) > 12
    assert ctx.store.value("cpr.test.mae") == pytest.approx(0.0426, abs=0.005)
    assert ctx.store.value("cpr.train.mae") == pytest.approx(0.0266, abs=0.005)


def test_the_classification_subject_gets_no_cpr_table(
    credit: tuple[ToolContext, list[ToolResult]],
) -> None:
    ctx, _ = credit
    assert not [name for name in ctx.store.names() if name.startswith("cpr.")]


def test_every_stored_scalar_is_citable_and_every_table_is_rectangular(
    msr: tuple[ToolContext, list[ToolResult]],
) -> None:
    ctx, _ = msr
    for name in ctx.store.names():
        entry = ctx.store.entry(name)
        if entry.kind.value == "scalar":
            assert isinstance(ctx.store.value(name), float)
        elif entry.kind.value == "table":
            rows = ctx.store.load(name)
            assert rows and all(list(row) == list(rows[0]) for row in rows)
        assert entry.summary, f"{name} has no caption for Appendix B"
