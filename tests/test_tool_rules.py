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
from quaestor.tools.collinearity import sign_of
from quaestor.tools.leakage import DUPLICATE_MULTIPLE, FEATURE_OVERLAP_BOUND, duplicate_share
from quaestor.tools.metrics import THRESHOLD_TABLE, subpopulation_expression
from quaestor.tools.run import MAX_SECONDS_NAME
from quaestor.tools.thresholds import EFFECTIVE_SUFFIX, effective_name
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
#
# The seeded `L2` shape of `04-SEEDED-DEFECT-STUDY.md` section 2 is "copy 3% of the test rows into
# train", and it has two variants: the copy keeps the identifiers it came with, or it is re-keyed.
# Both are contamination and both must fire; they fire at different severities and on different
# evidence, because a shared identifier is contamination on its face while a shared feature vector
# is only contamination once it is more than coincidence in this dataset (D-086).


def contaminate(ctx: ToolContext, fraction: float = 0.03, *, rekey: bool) -> int:
    """Copy the head of the test split into train, with or without new identifiers.

    Args:
        ctx: The context whose run directory is perturbed.
        fraction: What share of the test split to copy.
        rekey: Whether the copies are given identifiers of their own, which is what a
            contamination that went through a de-duplication step looks like.

    Returns:
        How many rows were copied.
    """
    train = pd.read_csv(ctx.out_dir / "data_train.csv")
    test = pd.read_csv(ctx.out_dir / "data_test.csv")
    id_column = ctx.package.spec.data.id_column
    copied = test.head(int(fraction * len(test))).copy()
    train_predictions = pd.read_csv(ctx.out_dir / "predictions_train.csv")
    test_predictions = pd.read_csv(ctx.out_dir / "predictions_test.csv")
    copied_predictions = test_predictions.head(len(copied)).copy()
    if rekey:
        fresh = range(
            int(train[id_column].max()) + 1, int(train[id_column].max()) + 1 + len(copied)
        )
        copied[id_column] = list(fresh)
        copied_predictions[id_column] = list(fresh)
    write_csv(ctx.out_dir / "data_train.csv", pd.concat([train, copied], ignore_index=True))
    # A subject that trained on the contaminated split would have scored those rows too.
    write_csv(
        ctx.out_dir / "predictions_train.csv",
        pd.concat([train_predictions, copied_predictions], ignore_index=True),
    )
    return len(copied)


def test_l2_fires_high_when_the_copied_test_rows_keep_their_identifiers(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    contaminate(ctx, rekey=False)
    result = run("check_leakage", ctx)
    assert classes(result) == ["L2"]
    assert result.candidates[0].suggested_severity is Severity.high
    assert ctx.store.value("leakage.overlap.ids") == pytest.approx(0.03, abs=0.005)
    assert ctx.store.value("leakage.overlap.features") == pytest.approx(0.03, abs=0.005)
    assert "identifier" in result.candidates[0].detail
    # The identifier artifact is the evidence the high severity rests on.
    assert ctx.store.artifact("leakage.overlap.ids").hash in result.candidates[0].evidence


def test_l2_fires_medium_when_the_copied_test_rows_are_re_keyed(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    contaminate(ctx, rekey=True)
    result = run("check_leakage", ctx)
    assert classes(result) == ["L2"]
    assert result.candidates[0].suggested_severity is Severity.medium
    # No identifier is shared, so the high rule is silent and the feature-vector rule carries it.
    assert ctx.store.value("leakage.overlap.ids") == 0.0
    assert ctx.store.value("leakage.overlap.features") == pytest.approx(0.03, abs=0.005)
    assert "re-keyed" in result.candidates[0].detail
    assert ctx.store.artifact("leakage.duplicates.train").hash in result.candidates[0].evidence


def test_l2_does_not_fire_on_a_clean_split(tmp_path: Path, credit_run_dir: Path) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    result = run("check_leakage", ctx)
    assert classes(result) == []
    assert ctx.store.value("leakage.overlap.ids") == 0.0
    assert ctx.store.value("leakage.overlap.features") == 0.0
    assert ctx.store.value("leakage.duplicates.train") == 0.0
    # The Phase 1 golden report cites `leakage.overlap`; it stays, as an alias of the feature
    # overlap, so that a committed citation keeps resolving (D-086).
    assert ctx.store.value("leakage.overlap") == ctx.store.value("leakage.overlap.features")


def test_the_within_train_duplicate_share_of_an_empty_split_is_zero() -> None:
    """The baseline of a split with no rows is zero, not a division by zero."""
    assert duplicate_share([]) == 0.0
    assert duplicate_share(["a", "b", "c"]) == 0.0
    assert duplicate_share(["a", "a", "b", "c"]) == 0.5


def test_l2_refuses_two_splits_with_no_identifier_column_in_common(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    """Without a shared identifier no row of one split can be recognised in the other.

    The screen says so rather than hashing an empty key, which would make every row of the test
    split look like every row of the training split and report 100% contamination.
    """
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    id_column = ctx.package.spec.data.id_column
    frame = pd.read_csv(ctx.out_dir / "data_test.csv")
    write_csv(ctx.out_dir / "data_test.csv", frame.rename(columns={id_column: "id"}))
    with pytest.raises(ToolError, match="share no identifier column"):
        run("check_leakage", ctx)


def discretise(ctx: ToolContext, share: float = 0.013, *, modes: int = 3) -> None:
    """Give a share of both splits one of a few identical feature vectors, keeping every id.

    This is the shape of the first live credit run, in which 1.2556% of the test rows repeated a
    feature vector of train and 1.1619% of the train rows repeated one of each other: a panel of
    coarse integer features has coincidental collisions, and they are as common inside one split
    as across two. Every identifier stays distinct, so nothing here is contamination.

    Args:
        ctx: The context whose run directory is perturbed.
        share: What share of each split's rows to place on a modal vector.
        modes: How many distinct modal vectors to spread them over.
    """
    declared = [feature.name for feature in ctx.package.spec.features]
    train = pd.read_csv(ctx.out_dir / "data_train.csv")
    columns = [name for name in declared if name in train.columns]
    # The modal vectors are the same in both splits, which is what makes the collisions
    # coincidental rather than a copy across the boundary: a modal row is as likely to be matched
    # inside its own split as in the other one.
    modal = [list(train.loc[index, columns]) for index in range(modes)]
    for split in ("train", "test"):
        frame = train if split == "train" else pd.read_csv(ctx.out_dir / "data_test.csv")
        marked = int(share * len(frame))
        for position in range(marked):
            frame.loc[frame.index[position], columns] = modal[position % modes]
        write_csv(ctx.out_dir / f"data_{split}.csv", frame)


def test_l2_does_not_fire_on_coincidental_duplicates_in_a_discrete_panel(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    """The first live run's false alarm, as a test: the same rate inside train and across splits.

    Under the Phase 5 rule -- any feature-vector overlap above 0.5% -- this panel raises `L2` at
    severity high and the run reports contamination that is not there. Under D-086's rule the
    cross-split share has to beat twice the within-train share, and here the two are the same
    number, so nothing fires and all three quantities are reported.
    """
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    discretise(ctx)
    result = run("check_leakage", ctx)
    features = ctx.store.value("leakage.overlap.features")
    duplicates = ctx.store.value("leakage.duplicates.train")
    overlap_threshold = ctx.thresholds["threshold.L2.overlap"]

    assert features > overlap_threshold, "the panel must break the Phase 5 rule to be the case"
    assert features == pytest.approx(0.013, abs=0.004)
    assert duplicates == pytest.approx(features, rel=0.10)
    assert ctx.store.value("leakage.overlap.ids") == 0.0
    assert classes(result) == []


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


def test_a_separable_split_is_reported_rather_than_ending_the_run(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    """D-126: a leak that separates the outcome must not stop the report being written."""
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    frame = pd.read_csv(ctx.out_dir / "predictions_test.csv")
    # The predictions now say exactly what happened, which is what a leaked feature produces.
    frame["y_score"] = np.where(frame["y_true"] == 1, 1.0 - 1e-9, 1e-9)
    write_csv(ctx.out_dir / "predictions_test.csv", frame)
    result = run("compute_metrics", ctx, {"splits": ["test"]})
    assert ctx.store.value("calibration.separable.test") == 1
    assert "calibration_slope.test" not in ctx.store
    assert "calibration_intercept.test" not in ctx.store
    assert ctx.store.value("metrics.test.auc") == 1.0
    assert "C1" not in classes(result)
    rows = {row["metric"]: row for row in ctx.store.load(THRESHOLD_TABLE)}
    assert rows["calibration_slope"]["result"] == "not evaluated"
    assert "calibration_slope on test" in result.summary


def test_the_clean_subject_is_not_separable(tmp_path: Path, credit_run_dir: Path) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    run("compute_metrics", ctx, {"splits": ["test"]})
    assert "calibration.separable.test" not in ctx.store
    assert "calibration_slope.test" in ctx.store


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
    assert ctx.store.artifact(MAX_SECONDS_NAME).hash in candidate.evidence
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
    # The two halves partition the split; ties at the median fall in the lower half (D-121).
    high = ctx.store.value("metrics.test.sub.limit_bal_high.n")
    assert low + high == ctx.store.value("metrics.test.n") == 1500
    assert low == pytest.approx(750, abs=25)


def test_a_discrete_column_whose_median_is_its_minimum_partitions_and_does_not_degenerate(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    """D-121, on the shape of column the sixth live run's third step asked about.

    `delinq_count_6m` on the real credit sample has a median of 0, so `>= median` selected every
    row of both splits: share 1, an AUC gap of 0, and a slice identical to its parent. The column
    is rebuilt here as a count whose median is its minimum -- two thirds zeros -- and the two rules
    are asserted to do what D-121 says: the upper half is the rows that are strictly above 0, the
    lower half is the zeros, and together they are the split.
    """
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    for split in ("train", "test"):
        frame = pd.read_csv(ctx.out_dir / f"data_{split}.csv")
        counts = np.zeros(len(frame), dtype=int)
        counts[: len(frame) // 3] = np.arange(1, len(frame) // 3 + 1) % 3 + 1
        frame["delinq_count_6m"] = counts
        write_csv(ctx.out_dir / f"data_{split}.csv", frame)
    run("compute_metrics", ctx, {"splits": ["test"]})
    total = ctx.store.value("metrics.test.n")
    slice_ = {"column": "delinq_count_6m", "rule": "below_median"}
    run("compute_metrics", ctx, {"splits": ["test"], "subpopulation": slice_})
    low = ctx.store.value("metrics.test.sub.delinq_count_6m_low.n")
    run(
        "compute_metrics",
        ctx,
        {"splits": ["test"], "subpopulation": {**slice_, "rule": "above_median"}},
    )
    high = ctx.store.value("metrics.test.sub.delinq_count_6m_high.n")
    assert low + high == total
    assert low == pytest.approx(total * 2 / 3, abs=2)
    assert ctx.store.value("metrics.test.sub.delinq_count_6m_high.share") < 0.95
    assert ctx.store.value("metrics.test.sub.delinq_count_6m_low.share") < 0.95


def test_a_rule_that_selects_the_whole_split_is_refused_with_the_share_it_selected(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    """D-121's refusal, on a constant column, which no median rule can make a proper part of.

    Both a median rule and an equality resolve to the whole split here, and the same check catches
    both because it reads the share the rule selected and not the rule. The message names the
    resolved expression, the share and the bound, which is what `follow_up_plan` quotes back to the
    loop (D-088).
    """
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    for split in ("train", "test"):
        frame = pd.read_csv(ctx.out_dir / f"data_{split}.csv")
        frame["delinq_count_6m"] = 0
        write_csv(ctx.out_dir / f"data_{split}.csv", frame)
    run("compute_metrics", ctx, {"splits": ["test"]})
    before = set(ctx.store.names())
    with pytest.raises(ToolError, match="holds 1 of 'test'") as raised:
        run(
            "compute_metrics",
            ctx,
            {
                "splits": ["test"],
                "subpopulation": {"column": "delinq_count_6m", "rule": "below_median"},
            },
        )
    assert "delinq_count_6m <= median(delinq_count_6m)" in raised.value.message
    assert "threshold.O1.slice_max_share" in raised.value.message
    with pytest.raises(ToolError, match="holds 1 of 'test'"):
        run(
            "compute_metrics",
            ctx,
            {
                "splits": ["test"],
                "subpopulation": {"column": "delinq_count_6m", "rule": "equals:0"},
            },
        )
    assert set(ctx.store.names()) == before, "the pre-pass raises before anything is stored"


def test_the_whole_split_check_is_a_pre_pass_over_every_split_asked_for(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    """A slice degenerate on the second split stores nothing of the first (D-121, D-088).

    `train` slices cleanly and `test` does not, so the call must leave the store as it found it:
    a run whose loop step raised goes on to draft, and half a slice in the store is half a slice
    the drafter can cite.
    """
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    frame = pd.read_csv(ctx.out_dir / "data_test.csv")
    frame["delinq_count_6m"] = 0
    write_csv(ctx.out_dir / "data_test.csv", frame)
    run("compute_metrics", ctx, {"splits": ["train", "test"]})
    before = set(ctx.store.names())
    with pytest.raises(ToolError, match="holds 1 of 'test'"):
        run(
            "compute_metrics",
            ctx,
            {
                "splits": ["train", "test"],
                "subpopulation": {"column": "delinq_count_6m", "rule": "equals:0"},
            },
        )
    assert set(ctx.store.names()) == before
    assert not [name for name in ctx.store.names() if ".sub.delinq_count_6m_eq_0" in name]


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


# --- D-091: the bound the feature-overlap rule applied is an artifact ---------------------------


def test_the_feature_overlap_rule_stores_the_bound_it_applied(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    """A rule that derives its bound from the data stores it, or no report can cite it."""
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    run("check_leakage", ctx)
    declared = ctx.store.value("threshold.L2.overlap")
    duplicates = ctx.store.value("leakage.duplicates.train")
    assert ctx.store.value(FEATURE_OVERLAP_BOUND) == pytest.approx(
        max(declared, DUPLICATE_MULTIPLE * duplicates)
    )
    assert "the larger of" in ctx.store.entry(FEATURE_OVERLAP_BOUND).summary


def test_a_discrete_panel_stores_a_bound_above_the_declared_one(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    """The attempt's own shape: the applied bound is the number the report has to compare with."""
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    _coarsen(ctx)
    run("check_leakage", ctx)
    assert ctx.store.value("leakage.duplicates.train") > 0.0
    assert ctx.store.value(FEATURE_OVERLAP_BOUND) > ctx.store.value("threshold.L2.overlap")


def _coarsen(ctx: ToolContext) -> None:
    """Split every feature at its own median, so distinct clients collide as the real sample's do.

    The synthetic generator draws continuous features, whose vectors are unique by construction --
    which is exactly why the clean control could not have caught D-086's false alarm. Twelve
    binary columns give 4,096 cells for 3,500 training rows, which is what a panel of delinquency
    counts and rounded bills looks like.
    """
    for split in ("train", "test"):
        frame = pd.read_csv(ctx.out_dir / f"data_{split}.csv")
        for column in frame.columns:
            if column in ("client_id", "default_next_month"):
                continue
            values = pd.to_numeric(frame[column], errors="coerce")
            frame[column] = (values >= values.median()).astype(int)
        write_csv(ctx.out_dir / f"data_{split}.csv", frame)


def test_the_medium_candidate_cites_the_bound_it_was_read_against(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    """D-091: the number in the detail sentence is a number the reader can resolve."""
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    contaminate(ctx, rekey=True)
    result = run("check_leakage", ctx)
    assert classes(result) == ["L2"]
    assert ctx.store.artifact(FEATURE_OVERLAP_BOUND).hash in result.candidates[0].evidence


def test_the_high_candidate_cites_the_bound_when_the_feature_arm_fires_too(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    contaminate(ctx, rekey=False)
    result = run("check_leakage", ctx)
    assert result.candidates[0].suggested_severity is Severity.high
    assert ctx.store.artifact(FEATURE_OVERLAP_BOUND).hash in result.candidates[0].evidence


def test_effective_name_is_the_one_spelling_of_a_derived_bound() -> None:
    assert effective_name("threshold.L2.overlap", "features") == FEATURE_OVERLAP_BOUND
    assert FEATURE_OVERLAP_BOUND.endswith(EFFECTIVE_SUFFIX)


# --- D-092: the developer-threshold table the tool computes --------------------------------------


def test_compute_metrics_writes_one_row_per_declared_bound(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    """The table section 4 points at, so the table and the `T1` rule cannot disagree."""
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    run("profile_data", ctx)
    result = run("compute_metrics", ctx)
    assert classes(result) == []
    rows = ctx.store.load(THRESHOLD_TABLE)
    assert [(row["metric"], row["split"], row["result"]) for row in rows] == [
        ("auc", "test", "pass"),
        ("brier", "test", "pass"),
        ("calibration_slope", "test", "pass"),
        ("calibration_slope", "test", "pass"),
        ("psi", "", "pass"),
    ]
    assert rows[0]["bound"] == "minimum 0.7"
    assert rows[1]["bound"] == "maximum 0.2"
    assert float(rows[4]["value"]) == pytest.approx(ctx.store.value("psi.max"))


def test_the_psi_row_says_pass_only_because_profile_data_ran(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    """Without `psi.max` the row is `not evaluated` and says why -- never a silent pass (D-092)."""
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    run("compute_metrics", ctx)
    rows = ctx.store.load(THRESHOLD_TABLE)
    psi = [row for row in rows if row["metric"] == "psi"]
    assert [row["result"] for row in psi] == ["not evaluated"]
    assert "psi.max is not in the store" in psi[0]["value"]
    assert psi[0]["bound"] == "maximum 0.25"


def test_a_declared_metric_this_pipeline_computes_nothing_for_says_so(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    """A rule no artifact answers is `not evaluated` with the metric named, not omitted."""

    def add_rule(spec: dict[str, object]) -> None:
        rules = spec["thresholds"]
        assert isinstance(rules, list)
        rules.append({"metric": "lift_at_10", "split": "test", "min": 2.0})

    package = variant_package(tmp_path, CREDIT, add_rule)
    ctx = context(tmp_path, package, credit_run_dir)
    result = run("compute_metrics", ctx)
    assert "not evaluated" in result.summary
    rows = ctx.store.load(THRESHOLD_TABLE)
    odd = [row for row in rows if row["metric"] == "lift_at_10"]
    assert [row["result"] for row in odd] == ["not evaluated"]
    assert "no artifact of this run answers 'lift_at_10'" in odd[0]["value"]


def test_the_runtime_cap_is_stored_outside_the_threshold_family(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    """D-092: a wall-clock cap is not a performance threshold and must not be listed as one."""
    ctx = bare_context(tmp_path, CREDIT)
    run("run_model", ctx, {"synthetic": 600})
    assert MAX_SECONDS_NAME == "runtime.max_seconds"
    assert MAX_SECONDS_NAME in ctx.store
    assert "threshold.package.max_seconds" not in ctx.store
    assert ctx.store.value(MAX_SECONDS_NAME) == 300.0


# --- D-095: the sign check and the ablation, neither of which raises anything --------------------


def test_the_sign_check_compares_each_coefficient_with_its_univariate_direction(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    """Three artifacts per retained feature plus the count, and no candidate from any of them."""
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    result = run("check_collinearity", ctx)
    assert classes(result) == []
    features = [
        name.split(".")[1]
        for name in ctx.store.names()
        if name.startswith("sign_check.") and name.endswith(".agrees")
    ]
    assert features, "no feature was sign-checked"
    for name in features:
        assert ctx.store.value(f"sign_check.{name}.coef_sign") in (-1.0, 0.0, 1.0)
        assert ctx.store.value(f"sign_check.{name}.univariate_direction") in (-1.0, 0.0, 1.0)
        agrees = ctx.store.value(f"sign_check.{name}.agrees")
        assert agrees in (0.0, 1.0)
        assert (agrees == 1.0) == (
            ctx.store.value(f"sign_check.{name}.coef_sign")
            == ctx.store.value(f"sign_check.{name}.univariate_direction")
        )
    disagreements = sum(
        1 for name in features if ctx.store.value(f"sign_check.{name}.agrees") == 0.0
    )
    assert ctx.store.value("sign_check.n_disagreements") == disagreements
    assert "disagree with the univariate direction" in result.summary


def test_a_feature_the_model_summary_has_no_coefficient_for_is_not_sign_checked(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    """An expanded spline column or a screened-out term has no fitted sign to compare."""
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    summary = read_json(ctx.out_dir / "model_summary.json")
    dropped = str(summary["coefficients"].pop(0)["feature"])
    write_json(ctx.out_dir / "model_summary.json", summary)
    run("check_collinearity", ctx)
    assert f"vif.{dropped}" in ctx.store
    assert f"sign_check.{dropped}.agrees" not in ctx.store


def test_sign_of_reports_zero_as_zero() -> None:
    """A coefficient of zero has no direction, and calling it positive would invent one."""
    assert (sign_of(0.3), sign_of(-0.3), sign_of(0.0)) == (1, -1, 0)


def test_the_ablation_refits_the_champion_s_form_without_each_feature(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    """One delta per retained feature, measured from the refit on all of them (D-095)."""
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    result = run("challenger_compare", ctx)
    assert classes(result) == ["E1"]
    deltas = [name for name in ctx.store.names() if name.startswith("ablation.")]
    assert "ablation.baseline_auc" in deltas
    assert len(deltas) == 11, deltas
    baseline = ctx.store.value("ablation.baseline_auc")
    assert 0.5 < baseline < 1.0
    # Dropping the strongest driver costs discrimination; the sign says which way (D-095).
    assert ctx.store.value("ablation.delinq_last.delta_auc") < -0.01
    assert "ablation.skipped" not in ctx.store


def test_the_ablation_is_skipped_and_says_so_above_the_feature_cap(
    tmp_path: Path, credit_run_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A measurement not made must not look like one that came back empty (D-095)."""
    monkeypatch.setattr("quaestor.tools.challenger.MAX_ABLATION_FEATURES", 3)
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    run("challenger_compare", ctx)
    assert "ablation.baseline_auc" not in ctx.store
    note = ctx.store.load("ablation.skipped")
    assert note["max_features"] == 3
    assert note["n_features"] > 3
    assert "not run" in ctx.store.entry("ablation.skipped").summary


def test_a_split_whose_outcome_is_constant_is_sign_checked_against_nothing(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    """No direction exists to compare a coefficient with, so nothing is claimed about one."""
    ctx = context(tmp_path, CREDIT, credit_run_dir)
    frame = pd.read_csv(ctx.out_dir / "predictions_train.csv")
    frame["y_true"] = 1
    write_csv(ctx.out_dir / "predictions_train.csv", frame)
    result = run("check_collinearity", ctx)
    assert classes(result) == []
    assert ctx.store.value("sign_check.n_disagreements") == 0
    assert not [name for name in ctx.store.names() if name.endswith(".agrees")]
    assert "vif.max" in ctx.store, "the collinearity statistics are unaffected"


def test_a_slice_rule_reads_as_an_expression_over_its_column() -> None:
    """D-112: the prose writes the rule in code, so its parameter is not read as a claim.

    The boundary is D-121's: the median's own rows are in the lower half, so the two rules
    partition the split and neither of them is the split.
    """
    assert subpopulation_expression("delinq_last", "equals:0") == "delinq_last == 0"
    assert subpopulation_expression("limit_bal", "below_median") == "limit_bal <= median(limit_bal)"
    assert subpopulation_expression("utilisation", "above_median") == (
        "utilisation > median(utilisation)"
    )
