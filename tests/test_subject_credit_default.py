"""The `credit_default` subject, in synthetic mode: the spec 4.1 acceptance list, at data level.

Every assertion here is about the panel and the fit, not about the pipeline. The pipeline-level
statement of DECISIONS D-017 -- that the clean synthetic subject yields exactly one finding, `E1`
at severity `low` -- cannot be made until the tools, the findings and the report exist in Phases
5 to 8. What can be made now is the data-level version of it, and it is the harder half:

* the challenger really does beat the champion by more than the 0.03 effective-challenge
  threshold, so the `E1` of D-017 will have something true to report;
* the champion passes every threshold `package.yaml` declares, so no `T1` competes with it;
* `bill_last` really is collinear before the screen and nothing retained is collinear after it,
  so the screen resolves the pair rather than leaving an `M1`;
* the split is stratified and the run is reproducible from its seed.

The subject runs once per session through `run_model`, because that is how the pipeline runs it and
a contract file that only passes when written by a test helper is not a contract.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import ModuleType

import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

from quaestor import ArtifactStore, load_package, run_model
from quaestor.sandbox import RunResult, read_contract

CREDIT_DEFAULT = Path(__file__).resolve().parent.parent / "subjects" / "credit_default"

SYNTHETIC_N = 5000
"""What the D-017 expectation is stated at, and what CI runs."""

CHALLENGER_THRESHOLD = 0.03
"""Spec 3.7's `E1` rule: a challenger that beats the champion by more than this is a finding."""

VIF_THRESHOLD = 10.0
"""Spec 3.7's `M1` rule, and the subject's own screen threshold."""


@pytest.fixture(scope="session")
def credit_run(tmp_path_factory: pytest.TempPathFactory) -> RunResult:
    """Run the synthetic subject once through the sandbox and share the result."""
    package = load_package(CREDIT_DEFAULT)
    out_dir = tmp_path_factory.mktemp("credit_synthetic") / "run"
    return run_model(package, None, out_dir, synthetic=SYNTHETIC_N)


@pytest.fixture(scope="session")
def credit_files(credit_run: RunResult) -> dict[str, Path]:
    """The paths of the spec 3.3 files the run wrote."""
    return {name: credit_run.out_dir / name for name in credit_run.files}


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def matrix_of(path: Path, features: list[str]) -> pd.DataFrame:
    return pd.read_csv(path)[features]


def retained_features(credit_files: dict[str, Path]) -> list[str]:
    summary = read_json(credit_files["model_summary.json"])
    assert isinstance(summary, dict)
    return [entry["feature"] for entry in summary["coefficients"]]


# --- the contract (spec 3.3) --------------------------------------------------------------------


def test_the_run_writes_every_spec_33_file(credit_run: RunResult) -> None:
    assert sorted(credit_run.files) == [
        "data_test.csv",
        "data_train.csv",
        "features.json",
        "metrics.json",
        "model_summary.json",
        "predictions_test.csv",
        "predictions_train.csv",
        "splits.json",
    ]
    for name, logical in credit_run.files.items():
        assert (credit_run.out_dir / name).is_file()
        assert logical == f"run.{Path(name).stem}"


def test_every_contract_file_is_schema_valid(credit_run: RunResult) -> None:
    package = load_package(CREDIT_DEFAULT)
    contract = read_contract(package.spec, credit_run.out_dir)
    assert [item.name for item in contract] == [
        "splits.json",
        "features.json",
        "metrics.json",
        "model_summary.json",
        "predictions_train.csv",
        "data_train.csv",
        "predictions_test.csv",
        "data_test.csv",
    ]


def test_the_run_writes_nothing_unexpected(credit_run: RunResult) -> None:
    assert credit_run.unexpected_output == []


def test_features_json_declares_the_twelve_features_with_their_package_timings(
    credit_files: dict[str, Path],
) -> None:
    package = load_package(CREDIT_DEFAULT)
    written = read_json(credit_files["features.json"])
    assert isinstance(written, list)
    assert [entry["name"] for entry in written] == package.spec.feature_names
    declared = {feature.name: feature.timing.value for feature in package.spec.features}
    assert {entry["name"]: entry["timing"] for entry in written} == declared


def test_the_features_artifact_resolves_the_goldens_run_features_citations(
    credit_run: RunResult,
) -> None:
    store = ArtifactStore(credit_run.store_root)
    payload = store.load("run.features")
    assert payload["n"] == 12
    assert payload["at_origination"] == 2
    assert payload["before_period_start"] == 10
    assert payload["during_period"] == 0
    assert payload["after_outcome"] == 0
    assert [item["name"] for item in payload["items"]][:2] == ["limit_bal", "age"]


def test_the_developers_metrics_cover_both_splits(credit_files: dict[str, Path]) -> None:
    metrics = read_json(credit_files["metrics.json"])
    assert isinstance(metrics, dict)
    assert sorted(metrics) == ["test", "train"]
    for split in ("train", "test"):
        assert sorted(metrics[split]) == [
            "auc",
            "brier",
            "event_rate",
            "gini",
            "ks",
            "logloss",
            "mean_predicted",
            "n",
        ]


# --- the split ----------------------------------------------------------------------------------


def test_the_split_is_seventy_thirty_stratified_and_disjoint(
    credit_files: dict[str, Path], credit_features: ModuleType
) -> None:
    splits = read_json(credit_files["splits.json"])
    assert isinstance(splits, dict)
    assert splits["train"]["n"] == 3500
    assert splits["test"]["n"] == 1500
    assert abs(splits["train"]["event_rate"] - splits["test"]["event_rate"]) < 0.005

    train_ids = pd.read_csv(credit_files["data_train.csv"])["client_id"].to_numpy()
    test_ids = pd.read_csv(credit_files["data_test.csv"])["client_id"].to_numpy()
    assert np.intersect1d(train_ids, test_ids).size == 0
    assert sorted(np.concatenate([train_ids, test_ids])) == list(range(1, SYNTHETIC_N + 1))


def test_the_rows_hash_is_the_sha256_of_the_sorted_identifiers(
    credit_files: dict[str, Path], credit_features: ModuleType
) -> None:
    splits = read_json(credit_files["splits.json"])
    assert isinstance(splits, dict)
    for split in ("train", "test"):
        ids = pd.read_csv(credit_files[f"data_{split}.csv"])["client_id"].to_numpy()
        assert splits[split]["rows_hash"] == credit_features.rows_hash(ids)


def test_a_stratified_split_keeps_the_event_rate_in_both_halves(
    credit_features: ModuleType,
) -> None:
    ids = np.arange(1, 1001)
    y = np.zeros(1000, dtype=int)
    y[::5] = 1  # a 20% event rate
    train, test = credit_features.stratified_split(ids, y, seed=20260901)
    assert train.n == 700
    assert test.n == 300
    rate = {
        name: float(y[np.isin(ids, split.ids)].mean())
        for name, split in (("train", train), ("test", test))
    }
    assert rate == {"train": 0.2, "test": 0.2}


def test_the_split_ignores_row_order(credit_features: ModuleType) -> None:
    ids = np.arange(1, 201)
    y = (ids % 4 == 0).astype(int)
    order = np.random.default_rng(11).permutation(ids.size)
    first, _ = credit_features.stratified_split(ids, y, seed=7)
    shuffled, _ = credit_features.stratified_split(ids[order], y[order], seed=7)
    assert list(first.ids) == list(shuffled.ids)


# --- the VIF screen -----------------------------------------------------------------------------


def test_bill_last_is_collinear_before_the_screen_and_nothing_retained_is_after_it(
    credit_files: dict[str, Path],
    credit_features: ModuleType,
    credit_synthetic: ModuleType,
) -> None:
    package = load_package(CREDIT_DEFAULT)
    raw = pd.read_csv(credit_files["data_train.csv"])
    retained = retained_features(credit_files)

    # The screen ran on the full twelve, which `data_train.csv` no longer holds, so the pre-screen
    # matrix is rebuilt from the same process at the same seed.
    generated = credit_features.engineer(
        credit_synthetic.generate(credit_synthetic.SyntheticProcess(n_clients=SYNTHETIC_N))
    )
    train_ids = raw["client_id"].to_numpy()
    full = generated[generated[credit_features.ID_COLUMN].isin(train_ids)][
        package.spec.feature_names
    ]
    before = credit_features.variance_inflation_factors(full)
    assert before["bill_last"] > VIF_THRESHOLD
    assert before["bill_mean_6m"] > VIF_THRESHOLD

    after = credit_features.variance_inflation_factors(raw[retained])
    assert max(after.values()) <= VIF_THRESHOLD, after


def test_the_screen_removed_bill_last_and_listed_its_vif(credit_files: dict[str, Path]) -> None:
    summary = read_json(credit_files["model_summary.json"])
    assert isinstance(summary, dict)
    removed = {entry["feature"]: entry["vif"] for entry in summary["removed"]}
    assert "bill_last" in removed
    assert removed["bill_last"] > VIF_THRESHOLD
    assert "bill_mean_6m" not in removed  # exactly one of the pair leaves (D-017)
    assert set(removed) | set(retained_features(credit_files)) == set(
        load_package(CREDIT_DEFAULT).spec.feature_names
    )


def test_the_screen_keeps_the_earlier_declared_member_of_a_pair(
    credit_features: ModuleType,
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
    retained, removed = credit_features.vif_screen(frame)
    assert retained == ["keep_me", "independent"]
    assert [entry["feature"] for entry in removed] == ["duplicate"]
    assert removed[0]["vif"] > VIF_THRESHOLD


def test_a_constant_column_gets_the_documented_vif_cap(credit_features: ModuleType) -> None:
    frame = pd.DataFrame({"a": np.arange(10.0), "b": np.ones(10)})
    factors = credit_features.variance_inflation_factors(frame)
    assert factors["b"] == credit_features.VIF_CAP
    assert credit_features.variance_inflation_factors(frame[["a"]]) == {"a": 1.0}


# --- the champion, the challenger and the declared thresholds ------------------------------------


def test_the_challenger_beats_the_champion_by_more_than_the_e1_threshold(
    credit_files: dict[str, Path],
) -> None:
    retained = retained_features(credit_files)
    train = pd.read_csv(credit_files["data_train.csv"])
    test = pd.read_csv(credit_files["data_test.csv"])
    champion = pd.read_csv(credit_files["predictions_test.csv"])

    champion_auc = roc_auc_score(champion["y_true"], champion["y_score"])
    challenger = HistGradientBoostingClassifier(random_state=20260901).fit(
        train[retained], train["default_next_month"]
    )
    challenger_auc = roc_auc_score(
        test["default_next_month"], challenger.predict_proba(test[retained])[:, 1]
    )
    assert challenger_auc - champion_auc > CHALLENGER_THRESHOLD, (
        f"champion {champion_auc:.4f}, challenger {challenger_auc:.4f}: the interaction of D-017 "
        "is no longer worth an E1"
    )


def test_the_champion_passes_every_threshold_package_yaml_declares(
    credit_files: dict[str, Path],
) -> None:
    package = load_package(CREDIT_DEFAULT)
    predictions = pd.read_csv(credit_files["predictions_test.csv"])
    truth = predictions["y_true"].to_numpy()
    scores = predictions["y_score"].to_numpy()
    measured = {
        "auc": float(roc_auc_score(truth, scores)),
        "brier": float(np.mean((scores - truth) ** 2)),
        "calibration_slope": calibration_slope(truth, scores),
        "psi": worst_psi(credit_files, retained_features(credit_files)),
    }
    for threshold in package.spec.thresholds:
        value = measured[threshold.metric]
        if threshold.min is not None:
            assert value >= threshold.min, f"{threshold.metric} {value} < {threshold.min}"
        if threshold.max is not None:
            assert value <= threshold.max, f"{threshold.metric} {value} > {threshold.max}"


def calibration_slope(truth: np.ndarray, scores: np.ndarray) -> float:
    """Spec 3.7's definition: a logistic regression of the outcome on the predicted log odds."""
    logit = np.log(scores / (1.0 - scores)).reshape(-1, 1)
    return float(LogisticRegression(max_iter=1000).fit(logit, truth).coef_[0][0])


def worst_psi(credit_files: dict[str, Path], features: list[str]) -> float:
    """PSI by hand: ten quantile bins taken from train, a 0.5% floor on every share."""
    train = pd.read_csv(credit_files["data_train.csv"])
    test = pd.read_csv(credit_files["data_test.csv"])
    worst = 0.0
    for feature in features:
        edges = np.quantile(train[feature], np.linspace(0.0, 1.0, 11))
        edges[0], edges[-1] = -np.inf, np.inf
        expected = np.maximum(np.histogram(train[feature], bins=edges)[0] / len(train), 0.005)
        actual = np.maximum(np.histogram(test[feature], bins=edges)[0] / len(test), 0.005)
        worst = max(worst, float(((actual - expected) * np.log(actual / expected)).sum()))
    return worst


def test_the_champion_is_a_logistic_regression_with_default_class_weights(
    credit_files: dict[str, Path],
) -> None:
    summary = read_json(credit_files["model_summary.json"])
    assert isinstance(summary, dict)
    assert summary["model"] == "logistic_regression"
    assert summary["class_weight"] is None
    assert summary["standardised"] is True
    assert summary["n_train"] == 3500


# --- determinism --------------------------------------------------------------------------------


def test_two_runs_of_one_seed_are_byte_identical(credit_run: RunResult, tmp_path: Path) -> None:
    package = load_package(CREDIT_DEFAULT)
    second = run_model(package, None, tmp_path / "again", synthetic=SYNTHETIC_N)
    for name in ("predictions_train.csv", "predictions_test.csv", "splits.json"):
        assert (credit_run.out_dir / name).read_bytes() == (second.out_dir / name).read_bytes()


def test_a_different_seed_draws_a_different_panel(credit_synthetic: ModuleType) -> None:
    process = credit_synthetic.SyntheticProcess(n_clients=400)
    first = credit_synthetic.generate(process)
    same = credit_synthetic.generate(process)
    other = credit_synthetic.generate(process.replace(seed=11))
    assert first.equals(same)
    assert not first.equals(other)


def test_the_run_is_well_under_the_sixty_second_budget(credit_run: RunResult) -> None:
    assert credit_run.duration_s < 60.0


# --- the generating process ----------------------------------------------------------------------


def test_the_process_hits_its_declared_base_event_rate(credit_synthetic: ModuleType) -> None:
    frame = credit_synthetic.generate(credit_synthetic.SyntheticProcess(n_clients=SYNTHETIC_N))
    assert abs(float(frame["default_next_month"].mean()) - 0.22) < 0.02


def test_every_parameter_of_the_process_is_a_field_of_one_dataclass(
    credit_synthetic: ModuleType,
) -> None:
    import dataclasses

    fields = {field.name for field in dataclasses.fields(credit_synthetic.SyntheticProcess)}
    assert {
        "n_clients",
        "seed",
        "target_event_rate",
        "beta_utilisation",
        "beta_interaction",
        "bill_noise_last_sd",
        "delinq_propensity_alpha",
    } <= fields
    assert credit_synthetic.SyntheticProcess().replace(beta_interaction=0.0).beta_interaction == 0.0


def test_the_process_rejects_a_panel_too_small_to_split(credit_synthetic: ModuleType) -> None:
    with pytest.raises(ValueError, match="n_clients must be at least 2"):
        credit_synthetic.generate(credit_synthetic.SyntheticProcess(n_clients=1))


def test_the_raw_panel_has_the_canonical_schema(
    credit_synthetic: ModuleType, credit_features: ModuleType
) -> None:
    frame = credit_synthetic.generate(credit_synthetic.SyntheticProcess(n_clients=50))
    assert list(frame.columns) == [
        *credit_features.RAW_COLUMNS,
        credit_features.TARGET_COLUMN,
    ]
    assert (frame["limit_bal"] > 0).all()
    assert (frame[[f"bill_amt_{i}" for i in range(1, 7)]] >= 0).all().all()
    assert frame[[f"delinq_{i}" for i in range(1, 7)]].to_numpy().max() <= 8


def test_the_near_collinear_pair_is_near_collinear_by_construction(
    credit_synthetic: ModuleType, credit_features: ModuleType
) -> None:
    frame = credit_features.engineer(
        credit_synthetic.generate(credit_synthetic.SyntheticProcess(n_clients=2000))
    )
    correlation = float(frame["bill_last"].corr(frame["bill_mean_6m"]))
    assert correlation > 0.98


# --- the engineering, on a hand-computed example -------------------------------------------------


def hand_made_client(credit_features: ModuleType) -> pd.DataFrame:
    """One client whose twelve features can be worked out on paper."""
    row: dict[str, object] = {
        credit_features.ID_COLUMN: 1,
        "limit_bal": 1000.0,
        "age": 40,
    }
    for index, bill in enumerate([600.0, 500.0, 400.0, 300.0, 200.0, 100.0], start=1):
        row[f"bill_amt_{index}"] = bill
    for index, payment in enumerate([250.0, 100.0, 50.0, 60.0, 40.0, 20.0], start=1):
        row[f"pay_amt_{index}"] = payment
    for index, code in enumerate([2, 0, 1, 0, 0, 3], start=1):
        row[f"delinq_{index}"] = code
    return pd.DataFrame([row])


def test_the_engineering_matches_a_hand_computed_client(credit_features: ModuleType) -> None:
    engineered = credit_features.engineer(hand_made_client(credit_features)).iloc[0]
    assert engineered["utilisation"] == pytest.approx(0.6)
    assert engineered["utilisation_mean_6m"] == pytest.approx(350.0 / 1000.0)
    assert engineered["bill_mean_6m"] == pytest.approx(350.0)
    assert engineered["bill_last"] == pytest.approx(600.0)
    # 250 / 500, 100 / 400, 50 / 300, 60 / 200, 40 / 100
    assert engineered["pay_ratio_last"] == pytest.approx(0.5)
    assert engineered["pay_ratio_mean_6m"] == pytest.approx(
        np.mean([0.5, 0.25, 1.0 / 6.0, 0.3, 0.4])
    )
    assert engineered["delinq_last"] == 2
    assert engineered["delinq_count_6m"] == 3
    assert engineered["delinq_max_6m"] == 3
    # Balances rise by 100 a month from the oldest statement to the most recent.
    assert engineered["bill_trend_6m"] == pytest.approx(100.0)


def test_the_payment_ratio_is_capped_where_package_yaml_says(credit_features: ModuleType) -> None:
    frame = hand_made_client(credit_features)
    frame.loc[0, "pay_amt_1"] = 5000.0
    engineered = credit_features.engineer(frame).iloc[0]
    assert engineered["pay_ratio_last"] == credit_features.PAY_RATIO_CAP


def test_a_zero_statement_balance_does_not_divide_by_zero(credit_features: ModuleType) -> None:
    frame = hand_made_client(credit_features)
    for index in range(1, 7):
        frame.loc[0, f"bill_amt_{index}"] = 0.0
    engineered = credit_features.engineer(frame).iloc[0]
    assert engineered["utilisation"] == 0.0
    assert engineered["pay_ratio_last"] == credit_features.PAY_RATIO_CAP


def test_engineering_names_the_columns_a_raw_frame_is_missing(
    credit_features: ModuleType,
) -> None:
    frame = hand_made_client(credit_features).drop(columns=["bill_amt_3"])
    with pytest.raises(ValueError, match="bill_amt_3"):
        credit_features.engineer(frame)


def test_the_engineered_frame_carries_the_target_only_when_the_raw_one_does(
    credit_features: ModuleType,
) -> None:
    frame = hand_made_client(credit_features)
    assert credit_features.TARGET_COLUMN not in credit_features.engineer(frame).columns
    frame[credit_features.TARGET_COLUMN] = 1
    assert credit_features.TARGET_COLUMN in credit_features.engineer(frame).columns
