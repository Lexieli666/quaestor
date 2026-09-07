"""Every candidate rule of spec 3.7, positive and negative, on the synthetic subjects' own output.

The negative case of each rule is the clean subject: the same run the session fixtures produce,
which raises nothing but the `E1` DECISIONS D-017 fixes. The positive case is that run with one
named edit -- the edits `04-SEEDED-DEFECT-STUDY.md` section 2 describes -- applied to the spec 3.3
contract files, which is all a tool reads. So each pair differs by exactly one thing, and the thing
is legible in the test's own name.

The clean subjects run once per session (`credit_run_dir`, `msr_run_dir` in `conftest.py`); each
test copies that output and perturbs its copy.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from quaestor import ArtifactStore, load_package
from quaestor.errors import ToolError
from quaestor.findings import DefectClass, Severity
from quaestor.tools import Thresholds, ToolContext, ToolResult, default_registry
from toolsupport import context, read_json, variant_package, write_csv, write_json

CREDIT = Path(__file__).resolve().parent.parent / "subjects" / "credit_default"
MSR = Path(__file__).resolve().parent.parent / "subjects" / "msr_prepayment"


def classes(result: ToolResult) -> list[str]:
    """The defect classes one tool call raised."""
    return result.classes


def run(tool_name: str, ctx: ToolContext, args: dict[str, object] | None = None) -> ToolResult:
    """Call one registered tool through the registry, so every call is validated and traced."""
    return default_registry().call(tool_name, args or {}, ctx)


def bare_context(tmp_path: Path, package_dir: Path) -> ToolContext:
    """A context with no run copied into it, for the tool that produces the run itself."""
    return ToolContext(
        package=load_package(package_dir),
        store=ArtifactStore(tmp_path / "artifacts"),
        out_dir=tmp_path / "run",
    )


# --- L1: a feature declared after_outcome -------------------------------------------------------


def test_l1_fires_on_a_feature_declared_after_outcome(tmp_path: Path, credit_run_dir: Path) -> None:
    def mistime(spec: dict[str, object]) -> None:
        features = spec["features"]
        assert isinstance(features, list)
        features[6]["timing"] = "after_outcome"  # delinq_last

    package = variant_package(tmp_path, CREDIT, mistime)
    ctx = context(tmp_path, package, credit_run_dir)
    result = run("check_leakage", ctx)
    assert classes(result) == ["L1"]
    candidate = result.candidates[0]
    assert candidate.suggested_severity is Severity.high
    assert "delinq_last" in candidate.detail
    assert ctx.store.value("leakage.timing.n_flagged") == 1
    # The candidate's evidence is in the store, which is what a Finding will be built from.
    assert all(ctx.store.get(digest) for digest in candidate.evidence)
    # The package's own pre-run screen sees the same thing before any tool runs.
    assert [c.defect_class for c in ctx.package.pre_run_candidates()] == [DefectClass.L1]


def test_l1_does_not_fire_on_the_clean_credit_subject(tmp_path: Path, credit_run_dir: Path) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    result = run("check_leakage", ctx)
    assert classes(result) == []
    assert ctx.store.value("leakage.timing.n_flagged") == 0
    assert ctx.store.value("leakage.name_screen.n_matched") == 0


# --- L1: a single feature that predicts the outcome on its own ------------------------------------


def test_l1_fires_when_one_feature_scores_above_the_single_feature_auc_threshold(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    frame = pd.read_csv(ctx.out_dir / "data_train.csv")
    # The leak: one declared feature is overwritten with the outcome itself, jittered so it is not
    # literally a copy of the target column.
    rng = np.random.default_rng(20260901)
    frame["utilisation"] = frame["default_next_month"] + rng.normal(0.0, 0.05, len(frame))
    write_csv(ctx.out_dir / "data_train.csv", frame)
    result = run("check_leakage", ctx)
    assert classes(result) == ["L1"]
    assert ctx.store.value("leakage.target_corr.max_single_feature_auc") > 0.9
    assert "utilisation" in result.candidates[0].detail


def test_the_single_feature_screen_orients_a_negatively_related_feature(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    frame = pd.read_csv(ctx.out_dir / "data_train.csv")
    rng = np.random.default_rng(7)
    # The same leak with the sign reversed: a feature that predicts "not default" is as leaky.
    frame["utilisation"] = -frame["default_next_month"] + rng.normal(0.0, 0.05, len(frame))
    write_csv(ctx.out_dir / "data_train.csv", frame)
    assert classes(run("check_leakage", ctx)) == ["L1"]


# --- L2: duplicated rows across the split boundary ------------------------------------------------


def test_l2_fires_when_test_rows_are_duplicated_into_train(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    train = pd.read_csv(ctx.out_dir / "data_train.csv")
    test = pd.read_csv(ctx.out_dir / "data_test.csv")
    duplicated = int(0.03 * len(test))
    write_csv(
        ctx.out_dir / "data_train.csv",
        pd.concat([train, test.head(duplicated)], ignore_index=True),
    )
    # A subject that trained on the contaminated split would have scored those rows too.
    train_predictions = pd.read_csv(ctx.out_dir / "predictions_train.csv")
    test_predictions = pd.read_csv(ctx.out_dir / "predictions_test.csv")
    write_csv(
        ctx.out_dir / "predictions_train.csv",
        pd.concat([train_predictions, test_predictions.head(duplicated)], ignore_index=True),
    )
    result = run("check_leakage", ctx)
    assert classes(result) == ["L2"]
    assert ctx.store.value("leakage.overlap") == pytest.approx(0.03, abs=0.005)
    assert result.candidates[0].suggested_severity is Severity.high


def test_l2_does_not_fire_on_a_clean_split(tmp_path: Path, credit_run_dir: Path) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    run("check_leakage", ctx)
    assert ctx.store.value("leakage.overlap") == 0.0


# --- S1: a shifted test split ---------------------------------------------------------------------


def test_s1_fires_when_the_test_split_is_shifted(tmp_path: Path, credit_run_dir: Path) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    frame = pd.read_csv(ctx.out_dir / "data_test.csv")
    # The population shift: the test split is drawn from the low-limit half of the book.
    frame = frame[frame["limit_bal"] < frame["limit_bal"].median()]
    write_csv(ctx.out_dir / "data_test.csv", frame)
    result = run("profile_data", ctx)
    assert classes(result) == ["S1"]
    assert ctx.store.value("psi.limit_bal") > 0.25
    assert ctx.store.value("psi.max") == ctx.store.value("psi.limit_bal")


def test_s1_does_not_fire_on_the_clean_credit_subject(tmp_path: Path, credit_run_dir: Path) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    result = run("profile_data", ctx)
    assert classes(result) == []
    assert ctx.store.value("psi.max") < 0.25


def test_s1_reads_train_against_test_only_and_reports_the_period_splits(
    tmp_path: Path, msr_run_dir: Path
) -> None:
    # DECISIONS D-046: the out-of-time comparison is far above the threshold by construction and
    # is stored under its own name, where no rule reads it.
    ctx = context(tmp_path, MSR, msr_run_dir)
    result = run("profile_data", ctx)
    assert classes(result) == []
    assert ctx.store.value("psi.max") < 0.25
    assert ctx.store.value("psi.out_of_time.burnout") > 1.0
    assert ctx.store.value("psi.vintage_holdout.note_rate") > 0.25
    assert "psi.out_of_time.max" not in ctx.store


# --- D1: a feature missing in one split only -----------------------------------------------------


def test_d1_fires_when_a_feature_is_missing_in_test_only(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    frame = pd.read_csv(ctx.out_dir / "data_test.csv")
    blanked = frame.index[: int(0.3 * len(frame))]
    frame.loc[blanked, "age"] = np.nan
    write_csv(ctx.out_dir / "data_test.csv", frame)
    result = run("profile_data", ctx)
    assert classes(result) == ["D1"]
    assert "age" in result.candidates[0].detail
    assert ctx.store.value("profile.test.missing.max") == pytest.approx(0.3, abs=0.01)
    assert ctx.store.value("profile.train.missing.max") == 0.0


def test_d1_does_not_fire_on_a_gap_under_ten_points(tmp_path: Path, credit_run_dir: Path) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    frame = pd.read_csv(ctx.out_dir / "data_test.csv")
    frame.loc[frame.index[: int(0.05 * len(frame))], "age"] = np.nan
    write_csv(ctx.out_dir / "data_test.csv", frame)
    result = run("profile_data", ctx)
    assert classes(result) == []
    assert ctx.store.value("profile.test.missing.max") == pytest.approx(0.05, abs=0.01)


# --- M1: a reintroduced collinear column ---------------------------------------------------------


def test_m1_fires_when_the_screened_out_collinear_feature_is_reintroduced(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    frame = pd.read_csv(ctx.out_dir / "data_train.csv")
    # `bill_last` is what the subject's own VIF screen removed for near-duplicating
    # `bill_mean_6m`; putting it back is the M1 recipe.
    rng = np.random.default_rng(20260901)
    noise = float(frame["bill_mean_6m"].std()) * 0.05
    frame["bill_last"] = frame["bill_mean_6m"] * 1.01 + rng.normal(0.0, noise, len(frame))
    write_csv(ctx.out_dir / "data_train.csv", frame)
    result = run("check_collinearity", ctx)
    assert classes(result) == ["M1"]
    assert ctx.store.value("vif.bill_last") > 10.0
    assert ctx.store.value("vif.bill_mean_6m") > 10.0
    assert ctx.store.value("vif.max") == max(
        ctx.store.value("vif.bill_last"), ctx.store.value("vif.bill_mean_6m")
    )
    assert "2 feature(s) exceed a VIF of 10.0" in result.candidates[0].detail


def test_m1_does_not_fire_on_the_screened_matrix(tmp_path: Path, credit_run_dir: Path) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    result = run("check_collinearity", ctx)
    assert classes(result) == []
    assert ctx.store.value("vif.max") < 10.0
    # DECISIONS D-035: Belsley's kappa, not the eigenvalue ratio, which would be its square.
    assert ctx.store.value("condition_number") == pytest.approx(5.55, abs=0.02)


def test_m1_fires_on_a_condition_number_alone(tmp_path: Path, credit_run_dir: Path) -> None:
    # A threshold override is the cheapest way to exercise the kappa half of the rule on its own.
    ctx = context(
        tmp_path,
        CREDIT,
        credit_run_dir,
        thresholds=Thresholds({"threshold.M1.condition_number": 3.0}),
    )
    result = run("check_collinearity", ctx)
    assert classes(result) == ["M1"]
    assert "condition number" in result.candidates[0].detail


# --- T1: a false developer threshold -------------------------------------------------------------


def test_t1_fires_when_a_declared_threshold_is_breached(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    def raise_the_floor(spec: dict[str, object]) -> None:
        thresholds = spec["thresholds"]
        assert isinstance(thresholds, list)
        thresholds[0]["min"] = 0.99  # auc on test, which the champion cannot reach

    package = variant_package(tmp_path, CREDIT, raise_the_floor)
    ctx = context(tmp_path, package, credit_run_dir)
    result = run("compute_metrics", ctx)
    assert classes(result) == ["T1"]
    candidate = result.candidates[0]
    assert candidate.suggested_severity is Severity.high
    assert "0.99" in candidate.detail
    assert ctx.store.value("threshold.package.auc.test.min") == 0.99
    assert ctx.store.artifact("metrics.test.auc").hash in candidate.evidence


def test_t1_does_not_fire_on_the_thresholds_the_subject_declares(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    result = run("compute_metrics", ctx)
    assert classes(result) == []
    assert ctx.store.value("threshold.package.auc.test.min") == 0.70
    assert ctx.store.value("threshold.package.brier.test.max") == 0.20


def test_a_declared_threshold_no_artifact_answers_is_reported_as_not_evaluated(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    def add_an_unknown_metric(spec: dict[str, object]) -> None:
        thresholds = spec["thresholds"]
        assert isinstance(thresholds, list)
        thresholds.append({"metric": "sharpe_ratio", "split": "test", "min": 1.0})

    package = variant_package(tmp_path, CREDIT, add_an_unknown_metric)
    ctx = context(tmp_path, package, credit_run_dir)
    result = run("compute_metrics", ctx)
    assert classes(result) == []
    # `psi` is unevaluated too, because profile_data has not run in this test.
    assert "not evaluated: ['psi', 'sharpe_ratio on test']" in result.summary


def test_the_psi_threshold_is_checked_when_profile_data_has_run(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    def tighten_psi(spec: dict[str, object]) -> None:
        thresholds = spec["thresholds"]
        assert isinstance(thresholds, list)
        thresholds[3]["max"] = 0.001

    package = variant_package(tmp_path, CREDIT, tighten_psi)
    ctx = context(tmp_path, package, credit_run_dir)
    run("profile_data", ctx)
    result = run("compute_metrics", ctx)
    assert classes(result) == ["T1"]
    assert "psi" in result.candidates[0].detail
    assert ctx.store.artifact("psi.max").hash in result.candidates[0].evidence


# --- C1: an over-confident score ------------------------------------------------------------------


def test_c1_fires_on_an_over_confident_prediction(tmp_path: Path, credit_run_dir: Path) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    frame = pd.read_csv(ctx.out_dir / "predictions_test.csv")
    # Doubling the log odds is the miscalibration recipe: the ordering, and so the AUC, is
    # unchanged, and the calibration slope halves.
    odds = np.log(frame["y_score"] / (1.0 - frame["y_score"]))
    frame["y_score"] = 1.0 / (1.0 + np.exp(-2.5 * odds))
    write_csv(ctx.out_dir / "predictions_test.csv", frame)
    result = run("compute_metrics", ctx, {"splits": ["test"]})
    assert "C1" in classes(result)
    assert ctx.store.value("calibration_slope.test") < 0.8
    assert ctx.store.value("metrics.test.auc") == pytest.approx(0.7480, abs=0.001)


def test_c1_fires_when_the_mean_prediction_leaves_the_observed_rate(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    frame = pd.read_csv(ctx.out_dir / "predictions_test.csv")
    frame["y_score"] = np.clip(frame["y_score"] * 1.5, 0.0, 1.0)
    write_csv(ctx.out_dir / "predictions_test.csv", frame)
    result = run("compute_metrics", ctx, {"splits": ["test"]})
    assert "C1" in classes(result)
    assert ctx.store.value("calibration.mean_rel_gap.test") > 0.25


def test_c1_does_not_fire_on_the_clean_subjects(tmp_path: Path, credit_run_dir: Path) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    result = run("compute_metrics", ctx)
    assert classes(result) == []
    assert 0.8 < ctx.store.value("calibration_slope.test") < 1.2
    assert ctx.store.value("calibration.mean_rel_gap.test") < 0.25


# --- O1: out-of-sample degradation ---------------------------------------------------------------


def test_o1_fires_on_a_train_to_test_auc_gap(tmp_path: Path, credit_run_dir: Path) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    frame = pd.read_csv(ctx.out_dir / "predictions_test.csv")
    # The score is shuffled on the test split only: the model has learned the training sample.
    frame["y_score"] = frame["y_score"].sample(frac=1.0, random_state=20260901).to_numpy()
    write_csv(ctx.out_dir / "predictions_test.csv", frame)
    result = run("compute_metrics", ctx)
    assert "O1" in classes(result)
    candidate = next(c for c in result.candidates if c.defect_class is DefectClass.O1)
    assert "generalisation-gap threshold of 0.08" in candidate.detail
    assert ctx.store.artifact("threshold.O1.auc_gap").hash in candidate.evidence


def test_o1_fires_when_a_period_split_falls_below_test(tmp_path: Path, msr_run_dir: Path) -> None:
    ctx = context(tmp_path, MSR, msr_run_dir)
    frame = pd.read_csv(ctx.out_dir / "predictions_out_of_time.csv")
    frame["y_score"] = frame["y_score"].sample(frac=1.0, random_state=20260901).to_numpy()
    write_csv(ctx.out_dir / "predictions_out_of_time.csv", frame)
    result = run("compute_metrics", ctx)
    assert "O1" in classes(result)
    candidate = next(c for c in result.candidates if c.defect_class is DefectClass.O1)
    assert "out_of_time" in candidate.detail
    assert ctx.store.artifact("threshold.O1.holdout_gap").hash in candidate.evidence


def test_o1_does_not_fire_on_the_clean_hazard_subject(tmp_path: Path, msr_run_dir: Path) -> None:
    # Spec 3.7's second O1 rule, measured on the clean synthetic control as the Phase 5 prompt
    # requires: out-of-time AUC is *above* test and the vintage holdout is 0.0035 below it, so
    # neither comparison approaches the 0.05 threshold (DECISIONS D-053).
    ctx = context(tmp_path, MSR, msr_run_dir)
    result = run("compute_metrics", ctx)
    assert classes(result) == []
    test_auc = ctx.store.value("metrics.test.auc")
    assert ctx.store.value("metrics.out_of_time.auc") > test_auc
    assert test_auc - ctx.store.value("metrics.vintage_holdout.auc") == pytest.approx(
        0.0035, abs=0.001
    )


# --- E1: effective challenge ---------------------------------------------------------------------


def test_e1_fires_on_the_clean_credit_subject_as_d_017_says_it_must(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    result = run("challenger_compare", ctx)
    assert classes(result) == ["E1"]
    assert result.candidates[0].suggested_severity is Severity.low
    assert ctx.store.value("challenger.delta_auc") == pytest.approx(0.0760, abs=0.001)
    assert json.loads((ctx.store.artifact("challenger.name").path).read_text()) == (
        "hist_gradient_boosting"
    )


def test_e1_does_not_fire_on_the_clean_hazard_subject(tmp_path: Path, msr_run_dir: Path) -> None:
    ctx = context(tmp_path, MSR, msr_run_dir)
    result = run("challenger_compare", ctx)
    assert classes(result) == []
    assert ctx.store.value("challenger.delta_auc") == pytest.approx(-0.0415, abs=0.001)


def test_the_challenger_cites_the_champion_auc_the_store_already_holds(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    run("compute_metrics", ctx, {"splits": ["test"]})
    result = run("challenger_compare", ctx)
    assert ctx.store.artifact("metrics.test.auc").hash in result.candidates[0].evidence


# --- R1: a regime-dependent feature --------------------------------------------------------------


def test_r1_fires_when_a_feature_changes_sign_across_regimes(
    tmp_path: Path, msr_run_dir: Path
) -> None:
    ctx = context(tmp_path, MSR, msr_run_dir)
    frame = pd.read_csv(ctx.out_dir / "data_train.csv")
    # The recipe of `04` section 2: the incentive coefficient flips between the falling and rising
    # regimes. Reversing the feature's sign within one regime is the same defect seen from the
    # data side, and leaves the champion's own scores untouched.
    rising = frame["rate_regime"] == "rising"
    frame.loc[rising, "incentive"] = -frame.loc[rising, "incentive"]
    write_csv(ctx.out_dir / "data_train.csv", frame)
    result = run("check_stability", ctx)
    assert classes(result) == ["R1"]
    assert "incentive" in result.candidates[0].detail
    assert ctx.store.value("stability.incentive.sign_flip") == 1


def test_r1_fires_when_discrimination_differs_across_regimes(
    tmp_path: Path, msr_run_dir: Path
) -> None:
    ctx = context(tmp_path, MSR, msr_run_dir)
    frame = pd.read_csv(ctx.out_dir / "predictions_train.csv")
    data = pd.read_csv(ctx.out_dir / "data_train.csv")
    merged = frame.merge(data[["loan_id", "period", "rate_regime"]], on=["loan_id", "period"])
    rising = merged["rate_regime"] == "rising"
    frame.loc[rising.to_numpy(), "y_score"] = (
        frame.loc[rising.to_numpy(), "y_score"].sample(frac=1.0, random_state=11).to_numpy()
    )
    write_csv(ctx.out_dir / "predictions_train.csv", frame)
    result = run("check_stability", ctx)
    assert classes(result) == ["R1"]
    assert "AUC differs" in result.candidates[0].detail


def test_r1_does_not_fire_on_the_clean_hazard_subject(tmp_path: Path, msr_run_dir: Path) -> None:
    ctx = context(tmp_path, MSR, msr_run_dir)
    result = run("check_stability", ctx)
    assert classes(result) == []
    rows = ctx.store.load("stability.auc_by_regime")
    assert [row["regime"] for row in rows] == ["falling", "rising"]
    assert all(
        ctx.store.value(f"stability.{name}.sign_flip") == 0 for name in ["incentive", "sato"]
    )
    # psi_over_time is reported and never a candidate.
    assert len(ctx.store.load("stability.psi_over_time")) > 1


def test_check_stability_refuses_a_package_with_no_regime_column(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    with pytest.raises(ToolError, match="declares no regime.column"):
        run("check_stability", ctx)


# --- X1: a sign-flipped projection ---------------------------------------------------------------


def test_x1_fires_on_a_projection_whose_value_rises_at_the_down_shock(
    tmp_path: Path, msr_run_dir: Path
) -> None:
    ctx = context(tmp_path, MSR, msr_run_dir)
    payload = read_json(ctx.out_dir / "projection.json")
    # The recipe of `04` section 2: a sign error in the projection makes value rise at -300bp.
    base = payload["value_by_shock"]["0"]
    for shock in ("-300", "-200", "-100"):
        payload["value_by_shock"][shock] = base + (base - payload["value_by_shock"][shock])
    write_json(ctx.out_dir / "projection.json", payload)
    result = run("run_scenarios", ctx)
    assert classes(result) == ["X1"]
    detail = result.candidates[0].detail
    assert "not monotone" in detail or "convexity" in detail
    assert ctx.store.value("scenario.convexity") > 0.0


def test_x1_fires_when_the_convexity_contradicts_the_declaration(
    tmp_path: Path, msr_run_dir: Path
) -> None:
    def declare_positive(spec: dict[str, object]) -> None:
        scenarios = spec["scenarios"]
        assert isinstance(scenarios, dict)
        scenarios["convexity_expectation"] = "positive"

    package = variant_package(tmp_path, MSR, declare_positive)
    ctx = context(tmp_path, package, msr_run_dir)
    result = run("run_scenarios", ctx)
    assert classes(result) == ["X1"]
    assert "declares positive" in result.candidates[0].detail


def test_x1_does_not_fire_on_the_clean_projection(tmp_path: Path, msr_run_dir: Path) -> None:
    ctx = context(tmp_path, MSR, msr_run_dir)
    result = run("run_scenarios", ctx)
    assert classes(result) == []
    assert ctx.store.value("scenario.convexity") < 0.0
    assert ctx.store.value("scenario.value_change.-300") < 0.0
    assert ctx.store.value("scenario.value_change.300") > 0.0
    assert "monotone in the shock" in result.summary


def test_run_scenarios_reports_a_projection_that_disagrees_with_itself(
    tmp_path: Path, msr_run_dir: Path
) -> None:
    ctx = context(tmp_path, MSR, msr_run_dir)
    payload = read_json(ctx.out_dir / "projection.json")
    payload["value_change"]["-300"] = 1.0
    payload["convexity"] = 1.0
    write_json(ctx.out_dir / "projection.json", payload)
    result = run("run_scenarios", ctx)
    assert classes(result) == []
    assert "disagrees with the recomputation at -300 bp" in result.summary
    assert "convexity" in result.summary
    # The recomputation, not the developer's number, is what was stored.
    assert ctx.store.value("scenario.value_change.-300") < 0.0


def test_run_scenarios_refuses_a_classification_package(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    with pytest.raises(ToolError, match="no scenarios block"):
        run("run_scenarios", ctx)


# --- R0: the subject does not run ----------------------------------------------------------------


def _broken_package(tmp_path: Path, body: str) -> Path:
    """Write a package whose subject does what `body` says, and nothing else."""
    root = tmp_path / "broken"
    (root / "code").mkdir(parents=True)
    (root / "code" / "__init__.py").write_text("", encoding="utf-8")
    (root / "code" / "run.py").write_text(body, encoding="utf-8")
    (root / "package.yaml").write_text(
        "\n".join(
            [
                "name: broken",
                'version: "1.0"',
                "model_type: binary_classification",
                'entrypoint: "python -m code.run"',
                "data:",
                "  source: a subject that fails, for the R0 rule",
                "  target: y",
                '  event_definition: "1 if the event happened"',
                "  id_column: id",
                "splits:",
                '  train: {rule: "all of it"}',
                '  test:  {rule: "all of it"}',
                "features:",
                "  - {name: x, timing: at_origination}",
                "runtime:",
                "  max_seconds: 60",
                "  max_memory_mb: 512",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return root


def test_r0_fires_when_the_subject_exits_non_zero(tmp_path: Path) -> None:
    package = _broken_package(
        tmp_path,
        'import sys\nprint("about to fail")\nsys.exit("the fit did not converge")\n',
    )
    # The run directory is written by the tool itself, so no clean run is copied here.
    ctx = bare_context(tmp_path, package)
    result = run("run_model", ctx, {"synthetic": 10})
    assert classes(result) == ["R0"]
    candidate = result.candidates[0]
    assert candidate.suggested_severity is Severity.high
    assert "did not complete a run" in candidate.detail
    assert ctx.store.artifact("run.stdout").hash in candidate.evidence
    assert ctx.store.artifact("threshold.package.max_seconds").hash in candidate.evidence
    assert "about to fail" in ctx.store.load("run.stdout")


def test_r0_fires_when_the_subject_outruns_its_wall_clock_cap(tmp_path: Path) -> None:
    package = _broken_package(tmp_path, "import time\ntime.sleep(30)\n")
    yaml_path = package / "package.yaml"
    yaml_path.write_text(
        yaml_path.read_text(encoding="utf-8").replace("max_seconds: 60", "max_seconds: 1"),
        encoding="utf-8",
    )
    ctx = bare_context(tmp_path, package)
    result = run("run_model", ctx, {"synthetic": 10})
    assert classes(result) == ["R0"]
    assert "wall-clock cap" in result.candidates[0].detail
    assert ctx.store.load("run.status")["timed_out"] is True


def test_r0_does_not_fire_on_a_subject_that_runs(tmp_path: Path) -> None:
    ctx = bare_context(tmp_path, CREDIT)
    result = run("run_model", ctx, {"synthetic": 500})
    assert classes(result) == []
    assert "run.metrics" in ctx.store
    assert ctx.store.value("run.duration_s") < 60.0


def test_a_request_run_model_cannot_honour_is_an_error_not_a_finding(tmp_path: Path) -> None:
    ctx = bare_context(tmp_path, CREDIT)
    with pytest.raises(ToolError, match="exactly one of --synthetic and --data"):
        run("run_model", ctx, {})
    with pytest.raises(ToolError, match="exactly one of --synthetic and --data"):
        run("run_model", ctx, {"synthetic": 10, "data_dir": str(tmp_path)})


def test_a_package_with_no_subject_is_an_error_not_a_finding(tmp_path: Path) -> None:
    package = _broken_package(tmp_path, "print('unused')\n")
    loaded = load_package(package)
    (package / "code" / "run.py").unlink()
    (package / "code" / "__init__.py").unlink()
    (package / "code").rmdir()
    ctx = ToolContext(
        package=loaded, store=ArtifactStore(tmp_path / "artifacts"), out_dir=tmp_path / "run"
    )
    with pytest.raises(ToolError, match="could not start the subject"):
        run("run_model", ctx, {"synthetic": 10})


# --- the tools' own argument errors --------------------------------------------------------------


def test_a_tool_asked_for_an_undeclared_split_says_which_splits_exist(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    with pytest.raises(ToolError, match=r"does not declare a split named 'out_of_time'"):
        run("compute_metrics", ctx, {"splits": ["out_of_time"]})


def test_profile_data_needs_the_reference_split(tmp_path: Path, credit_run_dir: Path) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    with pytest.raises(ToolError, match="does not include 'train'"):
        run("profile_data", ctx, {"splits": ["test"]})


def test_a_tool_asked_for_a_feature_the_matrix_does_not_hold_says_what_it_holds(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    with pytest.raises(ToolError, match="bill_last"):
        run("profile_data", ctx, {"features": ["bill_last"]})
    with pytest.raises(ToolError, match="bill_last"):
        run("check_collinearity", ctx, {"features": ["bill_last"]})


def test_a_missing_contract_file_names_the_file_and_the_command(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    (ctx.out_dir / "data_test.csv").unlink()
    with pytest.raises(ToolError, match="data_test.csv is missing"):
        run("profile_data", ctx)


def test_predictions_that_do_not_describe_the_same_rows_are_refused(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    frame = pd.read_csv(ctx.out_dir / "predictions_train.csv")
    write_csv(ctx.out_dir / "predictions_train.csv", frame.head(100))
    with pytest.raises(ToolError, match="do not describe the same rows"):
        run("check_leakage", ctx)


def test_a_split_with_one_outcome_is_refused_by_name(tmp_path: Path, credit_run_dir: Path) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    frame = pd.read_csv(ctx.out_dir / "predictions_test.csv")
    frame["y_true"] = 0
    write_csv(ctx.out_dir / "predictions_test.csv", frame)
    with pytest.raises(ToolError, match="holds only outcome 0"):
        run("compute_metrics", ctx, {"splits": ["test"]})


# --- sub-population metrics ----------------------------------------------------------------------


def test_a_sub_population_is_computed_under_the_name_the_golden_report_cites(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    run(
        "compute_metrics",
        ctx,
        {"splits": ["test"], "subpopulation": {"column": "limit_bal", "rule": "below_median"}},
    )
    low = ctx.store.value("metrics.test.sub.limit_bal_low.n")
    assert 0.5 < ctx.store.value("metrics.test.sub.limit_bal_low.auc") < 1.0
    run(
        "compute_metrics",
        ctx,
        {"splits": ["test"], "subpopulation": {"column": "limit_bal", "rule": "above_median"}},
    )
    # The two halves partition the split; ties at the median fall in the upper half.
    high = ctx.store.value("metrics.test.sub.limit_bal_high.n")
    assert low + high == ctx.store.value("metrics.test.n") == 1500
    assert low == pytest.approx(750, abs=25)


def test_a_sub_population_may_be_selected_by_equality(tmp_path: Path, msr_run_dir: Path) -> None:
    ctx = context(tmp_path, MSR, msr_run_dir)
    run(
        "compute_metrics",
        ctx,
        {"splits": ["test"], "subpopulation": {"column": "rate_regime", "rule": "equals:falling"}},
    )
    assert ctx.store.value("metrics.test.sub.rate_regime_eq_falling.n") > 0


def test_a_sub_population_that_selects_nothing_or_no_column_says_so(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    with pytest.raises(ToolError, match="has no column 'nope'"):
        run(
            "compute_metrics",
            ctx,
            {"splits": ["test"], "subpopulation": {"column": "nope", "rule": "below_median"}},
        )
    with pytest.raises(ToolError, match="selects no row"):
        run(
            "compute_metrics",
            ctx,
            {
                "splits": ["test"],
                "subpopulation": {"column": "limit_bal", "rule": "equals:not-a-limit"},
            },
        )
