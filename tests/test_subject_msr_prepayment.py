"""The `msr_prepayment` subject, in synthetic mode: the spec 4.2 acceptance list, at data level.

Every assertion here is about the panel, the fit and the projection, not about the pipeline. The
pipeline-level statement of DECISIONS D-047 -- that the clean synthetic hazard subject yields no
finding at all, the counterpart of D-017 for the classification subject -- cannot be made until
the tools, the findings and the report exist in Phases 5 to 8. What can be made now is the
data-level version of it:

* the champion passes every threshold `package.yaml` declares, so no `T1` competes;
* the boosted challenger does *not* beat it by the 0.03 effective-challenge margin, so unlike the
  credit subject this one is expected to yield no `E1` either;
* the projection's value curve is monotone and bends the way `package.yaml` declares, so no `X1`;
* both rate regimes appear in every split, so `check_stability` has something to compare;
* beginning-of-month lagging holds: a month's raw closing values reach the next month's features
  and never its own.

The subject runs once per session through `run_model`, because that is how the pipeline runs it
and a contract file that only passes when written by a test helper is not a contract.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from types import ModuleType
from typing import Any

import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

from quaestor import ArtifactStore, load_package, run_model
from quaestor.package import ConvexityExpectation
from quaestor.sandbox import RunResult, read_contract
from quaestor.tools.stats import calibration_slope_intercept

MSR_PREPAYMENT = Path(__file__).resolve().parent.parent / "subjects" / "msr_prepayment"

SYNTHETIC_N = 2000
"""What spec 4.2 declares the synthetic mode is, and what CI runs."""

CHALLENGER_THRESHOLD = 0.03
"""Spec 3.7's `E1` rule: a challenger that beats the champion by more than this is a finding."""

VIF_THRESHOLD = 10.0
"""Spec 3.7's `M1` rule, and the subject's own screen threshold."""

SPLITS = ("train", "test", "out_of_time", "vintage_holdout")


@pytest.fixture(scope="session")
def msr_result(tmp_path_factory: pytest.TempPathFactory) -> RunResult:
    """Run the synthetic subject once through the sandbox and share the result."""
    package = load_package(MSR_PREPAYMENT)
    out_dir = tmp_path_factory.mktemp("msr_synthetic") / "run"
    return run_model(package, None, out_dir, synthetic=SYNTHETIC_N)


@pytest.fixture(scope="session")
def msr_files(msr_result: RunResult) -> dict[str, Path]:
    """The paths of the spec 3.3 files the run wrote."""
    return {name: msr_result.out_dir / name for name in msr_result.files}


@pytest.fixture(scope="session")
def msr_panel(msr_synthetic: ModuleType, msr_features: ModuleType) -> pd.DataFrame:
    """The modelling panel of the default synthetic process, for the data-level assertions."""
    raw, rates = msr_synthetic.generate(msr_synthetic.SyntheticProcess(n_loans=SYNTHETIC_N))
    return msr_features.build_panel(raw, rates)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def retained_features(msr_files: dict[str, Path], msr_features: ModuleType) -> list[str]:
    """The declared features the screen kept, read off the model summary's coefficients."""
    summary = read_json(msr_files["model_summary.json"])
    named = [entry["feature"] for entry in summary["coefficients"]]
    return [name for name in msr_features.FEATURE_NAMES if name in named] + [
        name for name in msr_features.FEATURE_NAMES if f"{name}_spline_1" in named
    ]


# --- the contract (spec 3.3) ---------------------------------------------------------------------


def test_the_run_writes_every_spec_33_file(msr_result: RunResult) -> None:
    assert sorted(msr_result.files) == sorted(
        [
            "features.json",
            "metrics.json",
            "model_summary.json",
            "projection.json",
            "splits.json",
            *(f"predictions_{split}.csv" for split in SPLITS),
            *(f"data_{split}.csv" for split in SPLITS),
        ]
    )
    for name, logical in msr_result.files.items():
        assert (msr_result.out_dir / name).is_file()
        assert logical == f"run.{Path(name).stem}"


def test_every_contract_file_is_schema_valid(msr_result: RunResult) -> None:
    package = load_package(MSR_PREPAYMENT)
    contract = read_contract(package.spec, msr_result.out_dir)
    assert [item.name for item in contract][:5] == [
        "splits.json",
        "features.json",
        "metrics.json",
        "model_summary.json",
        "predictions_train.csv",
    ]
    assert "projection.json" in {item.name for item in contract}


def test_the_run_writes_nothing_unexpected(msr_result: RunResult) -> None:
    assert msr_result.unexpected_output == []


def test_features_json_declares_the_twelve_features_with_their_package_timings(
    msr_files: dict[str, Path],
) -> None:
    package = load_package(MSR_PREPAYMENT)
    written = read_json(msr_files["features.json"])
    assert [entry["name"] for entry in written] == package.spec.feature_names
    declared = {feature.name: feature.timing.value for feature in package.spec.features}
    assert {entry["name"]: entry["timing"] for entry in written} == declared


def test_the_features_artifact_counts_the_declared_timings(msr_result: RunResult) -> None:
    store = ArtifactStore(msr_result.store_root)
    payload = store.load("run.features")
    assert payload["n"] == 12
    assert payload["at_origination"] == 5
    assert payload["before_period_start"] == 7
    assert payload["during_period"] == 0
    assert payload["after_outcome"] == 0


def test_predictions_carry_one_row_per_loan_month(
    msr_files: dict[str, Path], msr_features: ModuleType
) -> None:
    for split in SPLITS:
        predictions = pd.read_csv(msr_files[f"predictions_{split}.csv"])
        assert list(predictions.columns) == [
            msr_features.ID_COLUMN,
            msr_features.TIME_COLUMN,
            "y_true",
            "y_score",
        ]
        assert not predictions.duplicated([msr_features.ID_COLUMN, msr_features.TIME_COLUMN]).any()
        assert predictions["y_score"].between(0.0, 1.0).all()
        assert set(predictions["y_true"].unique()) <= {0, 1}


def test_the_data_files_carry_the_regime_column_beside_the_identifier_and_the_target(
    msr_files: dict[str, Path], msr_features: ModuleType
) -> None:
    for split in SPLITS:
        frame = pd.read_csv(msr_files[f"data_{split}.csv"])
        assert frame.columns[0] == msr_features.ID_COLUMN
        assert frame.columns[1] == msr_features.TIME_COLUMN
        assert frame.columns[-2] == msr_features.REGIME_COLUMN
        assert frame.columns[-1] == msr_features.TARGET_COLUMN
        assert msr_features.REGIME_COLUMN not in msr_features.FEATURE_NAMES


def test_the_model_summary_carries_the_baseline_hazard_by_loan_age(
    msr_files: dict[str, Path],
) -> None:
    summary = read_json(msr_files["model_summary.json"])
    baseline = summary["baseline_hazard"]
    assert [entry["loan_age"] for entry in baseline] == [float(age) for age in range(0, 121)]
    hazards = [entry["hazard"] for entry in baseline]
    assert all(0.0 < value < 1.0 for value in hazards)
    # The seasoning hump: the fitted hazard rises off the origination month and then declines.
    peak = int(np.argmax(hazards[:61]))
    assert 6 <= peak <= 60, peak
    assert hazards[peak] > hazards[0]
    assert summary["model"] == "logistic_hazard_age_spline"
    assert len(summary["age_spline_knots"]) >= 3


def test_the_splits_summary_counts_loan_months_and_hashes_the_pairs(
    msr_files: dict[str, Path], msr_features: ModuleType
) -> None:
    splits = read_json(msr_files["splits.json"])
    assert sorted(splits) == sorted(SPLITS)
    for split in SPLITS:
        frame = pd.read_csv(msr_files[f"data_{split}.csv"])
        assert splits[split]["n"] == len(frame)
        assert splits[split]["n_loans"] == frame[msr_features.ID_COLUMN].nunique()
        assert splits[split]["rows_hash"] == msr_features.rows_hash(
            frame[msr_features.ID_COLUMN].to_numpy(),
            frame[msr_features.TIME_COLUMN].to_numpy(),
        )
    # train and out_of_time hold the same loans over disjoint periods, so a hash over loans alone
    # would make them the same split.
    assert splits["train"]["rows_hash"] != splits["out_of_time"]["rows_hash"]


def test_the_developers_metrics_cover_every_split(msr_files: dict[str, Path]) -> None:
    metrics = read_json(msr_files["metrics.json"])
    assert sorted(metrics) == sorted(SPLITS)
    for split in SPLITS:
        assert sorted(metrics[split]) == [
            "auc",
            "brier",
            "calibration_slope",
            "cpr_actual",
            "cpr_predicted",
            "event_rate",
            "gini",
            "ks",
            "logloss",
            "mean_predicted",
            "n",
        ]


# --- the splits ----------------------------------------------------------------------------------


def test_the_splits_are_the_rules_package_yaml_declares(
    msr_files: dict[str, Path], msr_features: ModuleType
) -> None:
    frames = {split: pd.read_csv(msr_files[f"data_{split}.csv"]) for split in SPLITS}
    time = msr_features.TIME_COLUMN
    loans = {split: set(frames[split][msr_features.ID_COLUMN]) for split in SPLITS}

    assert frames["train"][time].max() <= msr_features.PERIOD_CUT
    assert frames["test"][time].max() <= msr_features.PERIOD_CUT
    assert frames["out_of_time"][time].min() > msr_features.PERIOD_CUT
    # train and test partition the training vintages' loans; out_of_time holds all of them.
    assert loans["train"].isdisjoint(loans["test"])
    assert loans["out_of_time"] <= loans["train"] | loans["test"]
    assert loans["vintage_holdout"].isdisjoint(loans["train"] | loans["test"])
    held = round(len(loans["test"]) / (len(loans["train"]) + len(loans["test"])), 2)
    assert held == pytest.approx(msr_features.TEST_FRACTION, abs=0.01)


def test_the_vintage_holdout_is_exactly_the_declared_origination_year(
    msr_panel: pd.DataFrame, msr_features: ModuleType
) -> None:
    masks = msr_features.split_panel(msr_panel)
    years = msr_features.origination_year(msr_panel["orig_period"].to_numpy())
    assert set(years[masks["vintage_holdout"]]) == {msr_features.HOLDOUT_VINTAGE}
    for split in ("train", "test", "out_of_time"):
        assert set(years[masks[split]]) <= set(msr_features.TRAIN_VINTAGES)


def test_both_rate_regimes_are_present_in_every_split(
    msr_files: dict[str, Path], msr_features: ModuleType
) -> None:
    for split in SPLITS:
        frame = pd.read_csv(msr_files[f"data_{split}.csv"])
        present = set(frame[msr_features.REGIME_COLUMN].unique())
        assert present == set(msr_features.REGIME_VALUES), (split, present)
        share = frame[msr_features.REGIME_COLUMN].value_counts(normalize=True).min()
        assert share > 0.1, (split, share)


def test_the_split_draw_ignores_row_order(
    msr_panel: pd.DataFrame, msr_features: ModuleType
) -> None:
    order = np.random.default_rng(5).permutation(len(msr_panel))
    shuffled = msr_panel.iloc[order].reset_index(drop=True)
    first = msr_features.split_panel(msr_panel)
    again = msr_features.split_panel(shuffled)
    for split in SPLITS:
        assert set(msr_panel.loc[first[split], msr_features.ID_COLUMN]) == set(
            shuffled.loc[again[split], msr_features.ID_COLUMN]
        )


# --- beginning-of-month lagging (the leakage screen the subject has to survive) -------------------


def perturbed_panels(
    msr_synthetic: ModuleType, msr_features: ModuleType, column: str, month_offset: int = 12
) -> tuple[pd.DataFrame, pd.DataFrame, int]:
    """Build the panel twice, the second time with one raw month-t value moved, and name t.

    The loan chosen is one that survives well past the perturbed month, so that both month t and
    month t + 1 exist in both panels and can be compared row for row.
    """
    process = msr_synthetic.SyntheticProcess(n_loans=60)
    raw, rates = msr_synthetic.generate(process)
    counts = raw.groupby(msr_features.ID_COLUMN).size()
    loan = int(counts.idxmax())
    rows = raw[raw[msr_features.ID_COLUMN] == loan].sort_values(msr_features.TIME_COLUMN)
    period = int(rows[msr_features.TIME_COLUMN].iloc[month_offset])

    perturbed_raw, perturbed_rates = raw.copy(), rates.copy()
    if column == msr_features.RATE_COLUMN:
        mask = perturbed_rates[msr_features.TIME_COLUMN] == period
        perturbed_rates.loc[mask, column] += 1.75
    elif column == "prepaid":
        mask = (perturbed_raw[msr_features.ID_COLUMN] == loan) & (
            perturbed_raw[msr_features.TIME_COLUMN] == period
        )
        perturbed_raw.loc[mask, column] = 1
    else:
        mask = (perturbed_raw[msr_features.ID_COLUMN] == loan) & (
            perturbed_raw[msr_features.TIME_COLUMN] == period
        )
        perturbed_raw.loc[mask, column] *= 0.5
    return (
        msr_features.build_panel(raw, rates),
        msr_features.build_panel(perturbed_raw, perturbed_rates),
        period,
    )


def features_at(panel: pd.DataFrame, msr_features: ModuleType, period: int) -> pd.DataFrame:
    """The feature rows of one period, indexed by loan, for a row-for-row comparison."""
    rows = panel[panel[msr_features.TIME_COLUMN] == period]
    return rows.set_index(msr_features.ID_COLUMN)[msr_features.FEATURE_NAMES].sort_index()


@pytest.mark.parametrize("column", ["eom_balance", "market_rate_close"])
def test_a_month_t_raw_value_reaches_month_t_plus_one_and_never_month_t(
    msr_synthetic: ModuleType, msr_features: ModuleType, column: str
) -> None:
    clean, dirty, period = perturbed_panels(msr_synthetic, msr_features, column)
    later = msr_features.add_months(period, 1)

    before = features_at(clean, msr_features, period)
    after = features_at(dirty, msr_features, period)
    pd.testing.assert_frame_equal(before, after)

    changed = features_at(clean, msr_features, later).compare(
        features_at(dirty, msr_features, later)
    )
    assert not changed.empty, f"perturbing {column} in {period} left {later} untouched"


def test_the_payoff_of_month_t_enters_no_feature_in_any_month(
    msr_synthetic: ModuleType, msr_features: ModuleType
) -> None:
    clean, dirty, period = perturbed_panels(msr_synthetic, msr_features, "prepaid")
    # The panel is shorter, because a loan that pays off is not observed after it; every feature
    # row the two panels share is identical, and the target of month t is what moved.
    shared = clean.merge(
        dirty,
        on=[msr_features.ID_COLUMN, msr_features.TIME_COLUMN],
        suffixes=("_clean", "_dirty"),
    )
    for name in msr_features.FEATURE_NAMES:
        assert np.allclose(shared[f"{name}_clean"], shared[f"{name}_dirty"]), name
    moved = shared[shared[msr_features.TIME_COLUMN] == period]
    assert (moved[f"{msr_features.TARGET_COLUMN}_clean"] == 0).all()
    assert (moved[f"{msr_features.TARGET_COLUMN}_dirty"] == 1).any()


def test_the_lagged_features_are_the_previous_months_closing_values(
    msr_synthetic: ModuleType, msr_features: ModuleType
) -> None:
    process = msr_synthetic.SyntheticProcess(n_loans=40)
    raw, rates = msr_synthetic.generate(process)
    panel = msr_features.build_panel(raw, rates)
    closes = raw.set_index([msr_features.ID_COLUMN, msr_features.TIME_COLUMN])
    rate_by_period = dict(
        zip(
            rates[msr_features.TIME_COLUMN].to_numpy(dtype=int),
            rates[msr_features.RATE_COLUMN].to_numpy(dtype=float),
            strict=True,
        )
    )
    for row in panel.head(200).itertuples():
        previous = msr_features.add_months(int(row.period), -1)
        close = closes.loc[(row.loan_id, previous)]
        assert row.loan_age == pytest.approx(close["eom_age"])
        assert row.bom_balance_log == pytest.approx(np.log(close["eom_balance"]))
        assert row.incentive == pytest.approx(row.note_rate - rate_by_period[previous])
        assert row.rate_change_12m == pytest.approx(
            rate_by_period[previous] - rate_by_period[msr_features.add_months(previous, -12)]
        )


def test_burnout_accumulates_only_over_strictly_earlier_months(
    msr_synthetic: ModuleType, msr_features: ModuleType
) -> None:
    raw, rates = msr_synthetic.generate(msr_synthetic.SyntheticProcess(n_loans=20))
    panel = msr_features.build_panel(raw, rates).sort_values(
        [msr_features.ID_COLUMN, msr_features.TIME_COLUMN]
    )
    for _, loan in panel.groupby(msr_features.ID_COLUMN):
        incentive = loan["incentive"].to_numpy()
        burnout = loan["burnout"].to_numpy()
        assert burnout[0] == 0.0
        expected = np.cumsum(np.maximum(incentive, 0.0)) - np.maximum(incentive, 0.0)
        assert np.allclose(burnout, expected / msr_features.BURNOUT_MONTHS)


def test_a_gap_in_a_loans_months_breaks_the_lag_rather_than_lagging_across_it(
    msr_synthetic: ModuleType, msr_features: ModuleType
) -> None:
    raw, rates = msr_synthetic.generate(msr_synthetic.SyntheticProcess(n_loans=20))
    loan = int(raw[msr_features.ID_COLUMN].iloc[0])
    rows = raw[raw[msr_features.ID_COLUMN] == loan].sort_values(msr_features.TIME_COLUMN)
    dropped = int(rows[msr_features.TIME_COLUMN].iloc[5])
    holed = raw.drop(
        raw[
            (raw[msr_features.ID_COLUMN] == loan) & (raw[msr_features.TIME_COLUMN] == dropped)
        ].index
    )
    panel = msr_features.build_panel(holed, rates)
    periods = set(panel.loc[panel[msr_features.ID_COLUMN] == loan, msr_features.TIME_COLUMN])
    assert dropped not in periods
    assert msr_features.add_months(dropped, 1) not in periods
    assert msr_features.add_months(dropped, 2) in periods


def test_no_feature_is_declared_after_outcome(msr_features: ModuleType) -> None:
    package = load_package(MSR_PREPAYMENT)
    assert package.pre_run_candidates() == []
    assert set(msr_features.FEATURE_TIMING.values()) == {
        "at_origination",
        "before_period_start",
    }


# --- the screen and the spline -------------------------------------------------------------------


def test_the_screen_removes_the_current_balance_and_leaves_nothing_collinear(
    msr_files: dict[str, Path], msr_panel: pd.DataFrame, msr_features: ModuleType
) -> None:
    summary = read_json(msr_files["model_summary.json"])
    removed = {entry["feature"]: entry["vif"] for entry in summary["removed"]}
    # `bom_balance_log` is `orig_upb_log` plus a small amortisation term, so one of the pair has
    # to go; the screen's last-declared rule takes the later-declared one (D-045).
    assert "bom_balance_log" in removed
    assert removed["bom_balance_log"] > VIF_THRESHOLD
    assert "orig_upb_log" not in removed

    masks = msr_features.split_panel(msr_panel)
    retained = retained_features(msr_files, msr_features)
    after = msr_features.variance_inflation_factors(msr_panel.loc[masks["train"], retained])
    assert max(after.values()) <= VIF_THRESHOLD, after
    assert set(removed) | set(retained) == set(msr_features.FEATURE_NAMES)


def test_the_condition_number_of_the_retained_design_stays_under_the_m1_rule(
    msr_files: dict[str, Path], msr_panel: pd.DataFrame, msr_features: ModuleType
) -> None:
    # Belsley's kappa on the column-standardised matrix, as DECISIONS D-035 fixes it.
    masks = msr_features.split_panel(msr_panel)
    matrix = msr_panel.loc[masks["train"], retained_features(msr_files, msr_features)].to_numpy(
        dtype=float
    )
    standardised = (matrix - matrix.mean(axis=0)) / matrix.std(axis=0)
    singular = np.linalg.svd(standardised, compute_uv=False)
    assert singular.max() / singular.min() < 30.0


def test_the_natural_spline_basis_is_linear_beyond_its_boundary_knots(
    msr_features: ModuleType,
) -> None:
    knots = np.array([0.0, 10.0, 20.0, 30.0, 40.0])
    basis = msr_features.natural_spline_basis(np.linspace(-20.0, 80.0, 201), knots)
    assert basis.shape == (201, knots.size - 1)
    # Beyond the boundary knots a natural cubic spline is linear, so its second difference is 0.
    outside = msr_features.natural_spline_basis(np.array([45.0, 50.0, 55.0, 60.0]), knots)
    second = np.diff(outside, n=2, axis=0)
    assert np.allclose(second, 0.0, atol=1e-8)
    below = msr_features.natural_spline_basis(np.array([-20.0, -15.0, -10.0, -5.0]), knots)
    assert np.allclose(np.diff(below, n=2, axis=0), 0.0, atol=1e-8)


def test_the_spline_basis_rejects_knots_it_cannot_use(msr_features: ModuleType) -> None:
    with pytest.raises(ValueError, match="at least three knots"):
        msr_features.natural_spline_basis(np.zeros(3), np.array([1.0, 2.0]))
    with pytest.raises(ValueError, match="not strictly ascending"):
        msr_features.natural_spline_basis(np.zeros(3), np.array([1.0, 2.0, 2.0]))


def test_the_design_matrix_replaces_loan_age_with_its_basis(
    msr_panel: pd.DataFrame, msr_features: ModuleType
) -> None:
    knots = msr_features.age_spline_knots(msr_panel["loan_age"].to_numpy())
    retained = ["note_rate", "loan_age", "incentive"]
    matrix, names = msr_features.design_matrix(msr_panel.head(50), retained, knots)
    assert names == [
        "note_rate",
        *msr_features.spline_column_names("loan_age", knots),
        "incentive",
    ]
    assert matrix.shape == (50, len(names))
    # With loan_age screened out there is no basis at all.
    _, plain = msr_features.design_matrix(msr_panel.head(50), ["note_rate", "incentive"], knots)
    assert plain == ["note_rate", "incentive"]


def test_a_constant_column_gets_the_documented_vif_cap(msr_features: ModuleType) -> None:
    frame = pd.DataFrame({"a": np.arange(10.0), "b": np.ones(10)})
    factors = msr_features.variance_inflation_factors(frame)
    assert factors["b"] == msr_features.VIF_CAP
    assert msr_features.variance_inflation_factors(frame[["a"]]) == {"a": 1.0}


def test_the_screen_keeps_the_earlier_declared_member_of_a_pair(
    msr_features: ModuleType,
) -> None:
    rng = np.random.default_rng(3)
    first = rng.normal(size=400)
    frame = pd.DataFrame(
        {
            "keep_me": first,
            "duplicate": first + rng.normal(scale=0.01, size=400),
            "independent": rng.normal(size=400),
        }
    )
    retained, removed = msr_features.vif_screen(frame)
    assert retained == ["keep_me", "independent"]
    assert [entry["feature"] for entry in removed] == ["duplicate"]


# --- the champion, the challenger and the declared thresholds -------------------------------------


def test_the_champion_passes_every_threshold_package_yaml_declares(
    msr_files: dict[str, Path], msr_features: ModuleType
) -> None:
    package = load_package(MSR_PREPAYMENT)
    predictions = pd.read_csv(msr_files["predictions_test.csv"])
    truth = predictions["y_true"].to_numpy()
    scores = predictions["y_score"].to_numpy()
    measured = {
        "auc": float(roc_auc_score(truth, scores)),
        "calibration_slope": calibration_slope(truth, scores),
        "psi": worst_psi(msr_files, retained_features(msr_files, msr_features)),
    }
    assert sorted(threshold.metric for threshold in package.spec.thresholds) == sorted(measured)
    for threshold in package.spec.thresholds:
        value = measured[threshold.metric]
        if threshold.min is not None:
            assert value >= threshold.min, f"{threshold.metric} {value} < {threshold.min}"
        if threshold.max is not None:
            assert value <= threshold.max, f"{threshold.metric} {value} > {threshold.max}"


def calibration_slope(truth: np.ndarray, scores: np.ndarray) -> float:
    """Spec 3.7's definition: a logistic regression of the outcome on the predicted log odds.

    Unpenalised and converged, exactly as the subject's own `_calibration_slope` fits it: the
    default `C = 1.0` is a prior where spec 3.7 means the maximum likelihood estimate, and lbfgs's
    default `tol = 1e-4` stops short of the optimum by 0.05 wherever the slope is near 1. A
    reference estimator that did either would test the declared threshold against a different
    quantity from the one the subject reports (D-160).
    """
    clipped = np.clip(scores, 1e-9, 1.0 - 1e-9)
    logit = np.log(clipped / (1.0 - clipped)).reshape(-1, 1)
    fitted = LogisticRegression(C=np.inf, max_iter=1000, tol=1e-10).fit(logit, truth)
    return float(fitted.coef_[0][0])


def test_the_subjects_slope_is_the_same_estimator_quaestor_recomputes(
    msr_files: dict[str, Path],
) -> None:
    """The subject's `calibration_slope` agrees with `calibration_slope_intercept` on every split.

    Both are the unpenalised maximum likelihood slope of `logit(P(y = 1)) = a + b logit(p)`,
    reached by two different routes: the subject runs scikit-learn's lbfgs at `C = np.inf` and
    `tol = 1e-10`, `quaestor.tools.stats` runs its own Newton iteration to a 1e-10 step. They
    agree to about 1e-9 relative, so the 1e-6 asserted here leaves three orders of headroom for
    platform arithmetic while still failing on either way the two had already drifted apart: a
    penalty, or lbfgs's default tolerance, which between them left the subject reporting 0.9660 on
    the real test split where the Newton iteration read 1.0168. This test is what stops that
    happening again (DECISIONS D-160).
    """
    metrics = read_json(msr_files["metrics.json"])
    for split in SPLITS:
        predictions = pd.read_csv(msr_files[f"predictions_{split}.csv"])
        expected, _ = calibration_slope_intercept(
            predictions["y_true"].to_numpy(), predictions["y_score"].to_numpy()
        )
        reported = metrics[split]["calibration_slope"]
        assert reported == pytest.approx(expected, rel=1e-6), (
            f"{split}: the subject reports {reported!r} and quaestor recomputes {expected!r}; "
            "the two estimators have drifted apart again"
        )


def worst_psi(msr_files: dict[str, Path], features: list[str]) -> float:
    """PSI by hand, train against test: ten quantile bins from train, a 0.5% floor per share.

    Train against *test* only, which is the comparison the `psi` threshold means: the two are
    the same population sampled twice. Train against `out_of_time` or `vintage_holdout` measures
    the split design -- a later rate environment, a different origination year -- and is reported
    rather than tested (DECISIONS D-046).
    """
    train = pd.read_csv(msr_files["data_train.csv"])
    test = pd.read_csv(msr_files["data_test.csv"])
    worst = 0.0
    for feature in features:
        edges = np.quantile(train[feature], np.linspace(0.0, 1.0, 11))
        edges[0], edges[-1] = -np.inf, np.inf
        expected = np.maximum(np.histogram(train[feature], bins=edges)[0] / len(train), 0.005)
        actual = np.maximum(np.histogram(test[feature], bins=edges)[0] / len(test), 0.005)
        worst = max(worst, float(((actual - expected) * np.log(actual / expected)).sum()))
    return worst


def test_the_challenger_does_not_beat_the_champion_by_the_e1_margin(
    msr_files: dict[str, Path], msr_features: ModuleType
) -> None:
    retained = retained_features(msr_files, msr_features)
    train = pd.read_csv(msr_files["data_train.csv"])
    test = pd.read_csv(msr_files["data_test.csv"])
    champion = pd.read_csv(msr_files["predictions_test.csv"])

    champion_auc = roc_auc_score(champion["y_true"], champion["y_score"])
    challenger = HistGradientBoostingClassifier(random_state=20260901).fit(
        train[retained], train[msr_features.TARGET_COLUMN]
    )
    challenger_auc = roc_auc_score(
        test[msr_features.TARGET_COLUMN], challenger.predict_proba(test[retained])[:, 1]
    )
    assert challenger_auc - champion_auc <= CHALLENGER_THRESHOLD, (
        f"champion {champion_auc:.4f}, challenger {challenger_auc:.4f}: the spline hazard no "
        "longer captures the generating process, so the clean control would carry an E1"
    )


def test_no_single_feature_predicts_the_outcome_the_way_a_leak_would(
    msr_panel: pd.DataFrame, msr_features: ModuleType
) -> None:
    masks = msr_features.split_panel(msr_panel)
    train = msr_panel[masks["train"]]
    truth = train[msr_features.TARGET_COLUMN].to_numpy()
    for feature in msr_features.FEATURE_NAMES:
        auc = float(roc_auc_score(truth, train[feature].to_numpy()))
        assert max(auc, 1.0 - auc) < 0.90, feature


def test_the_out_of_sample_splits_do_not_fall_away_from_test(
    msr_files: dict[str, Path],
) -> None:
    # Spec 3.7's `O1`: a test-minus-train AUC gap above 0.08, or an out-of-time or vintage AUC
    # more than 0.05 below test.
    metrics = read_json(msr_files["metrics.json"])
    assert metrics["train"]["auc"] - metrics["test"]["auc"] < 0.08
    for split in ("out_of_time", "vintage_holdout"):
        assert metrics[split]["auc"] > metrics["test"]["auc"] - 0.05, split


# --- the projection ------------------------------------------------------------------------------


def test_the_projection_covers_every_declared_shock(msr_files: dict[str, Path]) -> None:
    package = load_package(MSR_PREPAYMENT)
    projection = read_json(msr_files["projection.json"])
    assert package.spec.scenarios is not None
    shocks = [str(shock) for shock in package.spec.scenarios.rate_shocks_bp]
    assert sorted(projection["value_by_shock"]) == sorted(shocks)
    assert sorted(projection["value_change"]) == sorted(shocks)
    assert sorted(projection["balance_by_month"]) == sorted(shocks)
    assert projection["horizon_months"] == package.spec.scenarios.horizon_months
    assert projection["servicing_fee_bp"] == package.spec.scenarios.servicing_fee_bp
    assert projection["discount_rate_annual"] == package.spec.scenarios.discount_rate_annual
    assert projection["convexity_expectation"] == package.spec.scenarios.convexity_expectation.value
    for shock in shocks:
        balances = projection["balance_by_month"][shock]
        assert len(balances) == package.spec.scenarios.horizon_months
        assert all(later <= earlier for earlier, later in zip(balances, balances[1:], strict=False))
        assert balances[0] <= projection["beginning_balance"]
    assert projection["value_change"]["0"] == 0.0


def test_the_projection_has_the_negative_convexity_sign_pattern(
    msr_files: dict[str, Path],
) -> None:
    # Signs, not magnitudes: what is asserted is that the servicing value falls when rates fall,
    # rises when they rise, and falls further than it rises -- which is what a mortgage-servicing
    # right does and what `package.yaml` declares.
    projection = read_json(msr_files["projection.json"])
    change = projection["value_change"]
    assert change["-300"] < 0.0
    assert change["300"] > 0.0
    assert abs(change["-300"]) > abs(change["300"])
    assert projection["convexity"] < 0.0
    assert projection["convexity_realised"] == ConvexityExpectation.negative.value
    assert projection["convexity_realised"] == projection["convexity_expectation"]


def test_the_projected_value_curve_is_monotone_in_the_shock(
    msr_files: dict[str, Path],
) -> None:
    # Spec 3.7's `X1` fires on a non-monotone curve as well as on the wrong sign pattern.
    projection = read_json(msr_files["projection.json"])
    shocks = sorted(int(key) for key in projection["value_by_shock"])
    values = [projection["value_by_shock"][str(shock)] for shock in shocks]
    assert values == sorted(values), dict(zip(shocks, values, strict=True))
    speeds = [projection["cpr_by_shock"][str(shock)] for shock in shocks]
    assert speeds == sorted(speeds, reverse=True), dict(zip(shocks, speeds, strict=True))


def test_the_projection_values_the_loans_alive_at_the_panels_last_month(
    msr_files: dict[str, Path],
    msr_panel: pd.DataFrame,
    msr_run: ModuleType,
    msr_features: ModuleType,
) -> None:
    projection = read_json(msr_files["projection.json"])
    assert projection["as_of_period"] == int(msr_panel[msr_features.TIME_COLUMN].max())
    book = msr_run.servicing_book(msr_panel)
    assert book.n_loans == projection["n_loans"] > 0
    assert book.beginning_balance == pytest.approx(projection["beginning_balance"])
    last = msr_panel[msr_panel[msr_features.TIME_COLUMN] == projection["as_of_period"]]
    assert book.n_loans == int((last[msr_features.TARGET_COLUMN] == 0).sum())


def test_a_projection_without_a_base_case_is_refused(
    msr_run: ModuleType,
    msr_projection: ModuleType,
    msr_panel: pd.DataFrame,
    msr_synthetic: ModuleType,
) -> None:
    book = msr_run.servicing_book(msr_panel)
    rates = msr_synthetic.rate_path(msr_synthetic.SyntheticProcess())
    with pytest.raises(ValueError, match="does not include the base case"):
        msr_projection.project(
            lambda frame: np.full(len(frame), 0.01),
            book,
            rates,
            rate_shocks_bp=[-100, 100],
            horizon_months=12,
            servicing_fee_bp=25.0,
            discount_rate_annual=0.08,
            convexity_expectation="negative",
        )


def test_a_rate_calendar_too_short_for_the_horizon_says_so(
    msr_run: ModuleType,
    msr_projection: ModuleType,
    msr_panel: pd.DataFrame,
    msr_synthetic: ModuleType,
) -> None:
    book = msr_run.servicing_book(msr_panel)
    rates = msr_synthetic.rate_path(msr_synthetic.SyntheticProcess().replace(rate_end_month=202412))
    with pytest.raises(ValueError, match="does not cover the 180 months projected"):
        msr_projection.forward_rates(rates, book.as_of, 180)


def test_a_flat_hazard_makes_the_shock_irrelevant(
    msr_run: ModuleType,
    msr_projection: ModuleType,
    msr_panel: pd.DataFrame,
    msr_synthetic: ModuleType,
) -> None:
    # A model that ignores its inputs has no convexity at all, which is the negative control for
    # the sign-pattern test above.
    book = msr_run.servicing_book(msr_panel)
    rates = msr_synthetic.rate_path(msr_synthetic.SyntheticProcess())
    projection = msr_projection.project(
        lambda frame: np.full(len(frame), 0.01),
        book,
        rates,
        rate_shocks_bp=[-300, 0, 300],
        horizon_months=24,
        servicing_fee_bp=25.0,
        discount_rate_annual=0.08,
        convexity_expectation="negative",
    )
    assert projection["value_change"] == {"-300": 0.0, "0": 0.0, "300": 0.0}
    assert projection["convexity_realised"] == "flat"


def test_the_subjects_scenario_declarations_match_package_yaml(msr_run: ModuleType) -> None:
    # The subject cannot read `package.yaml` (spec 3.2 hands it no path to it), so the block is
    # restated in `code/run.py`; this is the one place the duplication is resolved (D-043).
    scenarios = load_package(MSR_PREPAYMENT).spec.scenarios
    assert scenarios is not None
    assert msr_run.RATE_SHOCKS_BP == scenarios.rate_shocks_bp
    assert msr_run.HORIZON_MONTHS == scenarios.horizon_months
    assert msr_run.SERVICING_FEE_BP == scenarios.servicing_fee_bp
    assert msr_run.DISCOUNT_RATE_ANNUAL == scenarios.discount_rate_annual
    assert msr_run.CONVEXITY_EXPECTATION == scenarios.convexity_expectation.value


def test_the_subjects_split_declarations_match_package_yaml(msr_features: ModuleType) -> None:
    splits = load_package(MSR_PREPAYMENT).spec.splits
    assert msr_features.SPLIT_NAMES == tuple(splits.names())
    for vintage in msr_features.TRAIN_VINTAGES:
        assert str(vintage) in splits.train.rule
    assert str(msr_features.HOLDOUT_VINTAGE) in splits.vintage_holdout.rule
    assert str(msr_features.DECLARED_SEED) in splits.train.rule
    assert "2019-12" in splits.train.rule and str(msr_features.PERIOD_CUT) == "201912"
    assert "2020-01" in splits.out_of_time.rule


# --- determinism and the budget -------------------------------------------------------------------


def test_two_runs_of_one_seed_are_byte_identical(msr_result: RunResult, tmp_path: Path) -> None:
    package = load_package(MSR_PREPAYMENT)
    second = run_model(package, None, tmp_path / "again", synthetic=SYNTHETIC_N)
    for name in ("predictions_train.csv", "splits.json", "projection.json"):
        assert (msr_result.out_dir / name).read_bytes() == (second.out_dir / name).read_bytes()


def test_a_different_seed_draws_a_different_panel(msr_synthetic: ModuleType) -> None:
    process = msr_synthetic.SyntheticProcess(n_loans=60)
    first, rates = msr_synthetic.generate(process)
    same, same_rates = msr_synthetic.generate(process)
    other, other_rates = msr_synthetic.generate(process.replace(seed=11))
    assert first.equals(same)
    assert rates.equals(same_rates)
    assert not first.equals(other)
    assert not rates.equals(other_rates)


def test_the_run_is_well_under_the_sixty_second_budget(msr_result: RunResult) -> None:
    assert msr_result.duration_s < 60.0


# --- the generating process -----------------------------------------------------------------------


def test_the_process_hits_its_declared_monthly_payoff_rate(
    msr_panel: pd.DataFrame,
    msr_synthetic: ModuleType,
    msr_process: ModuleType,
    msr_features: ModuleType,
) -> None:
    # The intercept is solved so that the mean hazard over the *uncensored* schedule panel is
    # `target_smm`; the observed panel's event rate is lower, because a loan that pays off early
    # takes its remaining high-hazard months out of the sample with it.
    process = msr_synthetic.SyntheticProcess(n_loans=SYNTHETIC_N)
    rates = msr_process.rate_path(process)
    schedule = msr_features.build_panel(
        msr_process.schedule_panel(process, msr_process.loan_book(process, rates)), rates
    )
    predictor = msr_process.linear_predictor(process, schedule)
    intercept = msr_process.solve_intercept(process, predictor)
    mean_hazard = float(msr_process.hazard(process, intercept, predictor).mean())
    assert mean_hazard == pytest.approx(process.target_smm, abs=1e-5)

    observed = float(msr_panel["prepaid"].mean())
    assert 0.5 * process.target_smm < observed < process.target_smm


def test_every_parameter_of_the_process_is_a_field_of_one_dataclass(
    msr_synthetic: ModuleType,
) -> None:
    fields = {field.name for field in dataclasses.fields(msr_synthetic.SyntheticProcess)}
    assert {
        "n_loans",
        "seed",
        "months_observed",
        "target_smm",
        "cohort_years",
        "turnover_floor",
        "beta_incentive",
        "beta_age_years",
        "beta_age_years_squared",
        "beta_burnout",
        "beta_season_sin",
        "rate_cycle_amplitude",
        "rate_ramp_pp_per_year",
        "sato_sd",
    } <= fields
    process = msr_synthetic.SyntheticProcess()
    assert process.replace(beta_incentive=0.0).beta_incentive == 0.0
    # The intercept is solved rather than declared, so a recipe that moves a coefficient does not
    # also move the base rate.
    assert not any(
        field.startswith("intercept") and field != "intercept_bounds" for field in fields
    )


def test_the_process_rejects_a_book_too_small_to_split(msr_synthetic: ModuleType) -> None:
    with pytest.raises(ValueError, match="n_loans must be at least 6"):
        msr_synthetic.generate(msr_synthetic.SyntheticProcess(n_loans=4))


def test_the_process_rejects_a_target_speed_below_its_own_floor(
    msr_synthetic: ModuleType,
) -> None:
    with pytest.raises(ValueError, match="not above turnover_floor"):
        msr_synthetic.generate(msr_synthetic.SyntheticProcess(n_loans=20, target_smm=0.0001))


def test_the_rate_path_has_a_falling_and_a_rising_twelve_month_stretch(
    msr_synthetic: ModuleType, msr_features: ModuleType
) -> None:
    rates = msr_synthetic.rate_path(msr_synthetic.SyntheticProcess())
    values = rates[msr_features.RATE_COLUMN].to_numpy()
    change = values[12:] - values[:-12]
    assert (change < 0).any() and (change > 0).any()
    assert (change < 0).mean() > 0.2
    assert (change > 0).mean() > 0.2
    # No gap and no repeat: `rate_lookup` insists on it, and the projection depends on it.
    assert msr_features.rate_lookup(rates)[0].size == len(rates)


def test_the_rate_path_is_flat_where_the_projection_starts_shocking_it(
    msr_synthetic: ModuleType, msr_features: ModuleType
) -> None:
    process = msr_synthetic.SyntheticProcess()
    assert process.rate_flat_from_month == msr_features.add_months(process.observation_end_month, 1)
    rates = msr_synthetic.rate_path(process)
    tail = rates[rates[msr_features.TIME_COLUMN] >= process.rate_flat_from_month]
    assert tail[msr_features.RATE_COLUMN].nunique() == 1


def test_the_rate_path_rejects_a_backwards_span(msr_synthetic: ModuleType) -> None:
    with pytest.raises(ValueError, match="not a forward span"):
        msr_synthetic.rate_path(
            msr_synthetic.SyntheticProcess(rate_start_month=202001, rate_end_month=201901)
        )


def test_three_cohorts_originate_across_their_years(
    msr_panel: pd.DataFrame, msr_synthetic: ModuleType, msr_features: ModuleType
) -> None:
    process = msr_synthetic.SyntheticProcess()
    years = msr_features.origination_year(msr_panel["orig_period"].to_numpy())
    assert set(years) == set(process.cohort_years)
    months = set(msr_panel["orig_period"].to_numpy() % 100)
    assert len(months) > 1, "a cohort that originates in one month confounds age with calendar"


def test_the_observation_window_ends_on_one_month_for_every_loan(
    msr_synthetic: ModuleType, msr_features: ModuleType
) -> None:
    process = msr_synthetic.SyntheticProcess(n_loans=60)
    raw, _ = msr_synthetic.generate(process)
    assert int(raw[msr_features.TIME_COLUMN].max()) <= process.observation_end_month
    ages = raw.groupby(msr_features.ID_COLUMN)["eom_age"].max()
    assert ages.max() == process.months_observed


def test_a_paid_off_loan_is_not_observed_after_its_payoff(
    msr_synthetic: ModuleType, msr_features: ModuleType
) -> None:
    raw, _ = msr_synthetic.generate(msr_synthetic.SyntheticProcess(n_loans=200))
    for _, loan in raw.groupby(msr_features.ID_COLUMN):
        rows = loan.sort_values(msr_features.TIME_COLUMN)
        payoffs = rows[msr_features.TARGET_COLUMN].to_numpy()
        assert payoffs.sum() <= 1
        if payoffs.sum() == 1:
            assert payoffs[-1] == 1
            assert rows["eom_balance"].to_numpy()[-1] == 0.0
    assert 0.2 < float(raw.groupby(msr_features.ID_COLUMN)[msr_features.TARGET_COLUMN].max().mean())


def test_the_hazard_is_convex_in_incentive_over_the_whole_operating_range(
    msr_synthetic: ModuleType, msr_process: ModuleType
) -> None:
    # The base case sits near a one per cent monthly payoff rate, a logit near -4.6, and the
    # logistic is convex everywhere below zero; the negative-convexity sign pattern the
    # projection reports is therefore a property of the process (DECISIONS D-040).
    process = msr_synthetic.SyntheticProcess()
    logits = np.linspace(-9.0, -1.0, 200)
    values = msr_process.hazard(process, 0.0, logits)
    assert np.all(np.diff(values, n=2) > 0.0)
    assert values.min() > process.turnover_floor
    assert msr_process.hazard(process, -50.0, np.array([0.0]))[0] == pytest.approx(
        process.turnover_floor, abs=1e-9
    )


def test_the_note_rate_is_drawn_around_the_rate_at_origination(
    msr_synthetic: ModuleType, msr_process: ModuleType, msr_features: ModuleType
) -> None:
    process = msr_synthetic.SyntheticProcess(n_loans=900)
    rates = msr_process.rate_path(process)
    book = msr_process.loan_book(process, rates)
    lookup = dict(
        zip(
            rates[msr_features.TIME_COLUMN].to_numpy(dtype=int),
            rates[msr_features.RATE_COLUMN].to_numpy(dtype=float),
            strict=True,
        )
    )
    at_origination = np.array(
        [
            lookup[msr_features.add_months(int(period), -1)]
            for period in book["orig_period"].to_numpy()
        ]
    )
    spread = book["note_rate"].to_numpy() - at_origination
    assert np.allclose(spread, book["sato"].to_numpy(), atol=0.001)
    assert abs(float(spread.mean()) - process.sato_mean) < 0.05


def test_the_panel_carries_no_missing_value(msr_panel: pd.DataFrame) -> None:
    assert not msr_panel.isna().to_numpy().any()


def test_the_amortisation_schedule_matches_a_hand_computed_loan(
    msr_features: ModuleType,
) -> None:
    # 100,000 over 360 months at 6% nominal: r = 0.005, and the balance after one payment is
    # 100,000 x ((1.005^360 - 1.005) / (1.005^360 - 1)).
    balances = msr_features.scheduled_balances(
        np.array([100_000.0]), np.array([6.0]), np.array([360.0]), 3
    )
    growth = 1.005**360
    assert balances[0, 0] == pytest.approx(100_000.0 * (growth - 1.005) / (growth - 1.0))
    assert balances[0, 1] < balances[0, 0]
    # Past the term there is nothing left, and a zero-rate loan amortises linearly.
    assert msr_features.scheduled_balances(
        np.array([1200.0]), np.array([0.0]), np.array([12.0]), 13
    )[0].tolist() == pytest.approx(
        [1100.0, 1000.0, 900.0, 800.0, 700.0, 600.0, 500.0, 400.0, 300.0, 200.0, 100.0, 0.0, 0.0]
    )


# --- the panel builder's own error messages -------------------------------------------------------


def test_a_raw_panel_missing_a_column_names_it(
    msr_synthetic: ModuleType, msr_features: ModuleType
) -> None:
    raw, rates = msr_synthetic.generate(msr_synthetic.SyntheticProcess(n_loans=20))
    with pytest.raises(ValueError, match="eom_age"):
        msr_features.build_panel(raw.drop(columns=["eom_age"]), rates)


def test_a_rate_calendar_with_a_gap_says_where(
    msr_synthetic: ModuleType, msr_features: ModuleType
) -> None:
    rates = msr_synthetic.rate_path(msr_synthetic.SyntheticProcess())
    holed = rates.drop(rates.index[40])
    with pytest.raises(ValueError, match="gap or a repeated month"):
        msr_features.rate_lookup(holed)
    with pytest.raises(ValueError, match="is empty"):
        msr_features.rate_lookup(rates.head(0))
    with pytest.raises(ValueError, match=r"missing \['market_rate_close'\]"):
        msr_features.rate_lookup(rates.drop(columns=[msr_features.RATE_COLUMN]))


def test_a_rate_calendar_that_starts_too_late_names_the_month_it_cannot_reach(
    msr_synthetic: ModuleType, msr_features: ModuleType
) -> None:
    raw, rates = msr_synthetic.generate(msr_synthetic.SyntheticProcess(n_loans=20))
    with pytest.raises(ValueError, match="does not cover"):
        msr_features.build_panel(raw, rates[rates[msr_features.TIME_COLUMN] >= 201401])


def test_a_raw_panel_with_no_predecessor_month_is_refused(
    msr_synthetic: ModuleType, msr_features: ModuleType
) -> None:
    raw, rates = msr_synthetic.generate(msr_synthetic.SyntheticProcess(n_loans=20))
    firsts = raw.groupby(msr_features.ID_COLUMN, as_index=False).first()
    with pytest.raises(ValueError, match="no loan-month .* has a predecessor"):
        msr_features.build_panel(firsts[msr_features.RAW_PANEL_COLUMNS], rates)


def test_month_arithmetic_crosses_a_year_boundary(msr_features: ModuleType) -> None:
    assert msr_features.add_months(201912, 1) == 202001
    assert msr_features.add_months(202001, -1) == 201912
    assert msr_features.add_months(201401, -13) == 201212
    assert int(msr_features.calendar_month(201907)) == 7
    assert int(msr_features.month_period(msr_features.month_index(202312))) == 202312
