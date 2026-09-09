"""Reading the spec 3.3 contract: what each tool does when a file is not what it should be.

The happy paths of `quaestor.tools.frames` are covered wherever a tool runs. This module covers
the other half, which is the half a validator actually meets: a truncated CSV, a prediction column
that is not numeric, a data file whose columns are somebody else's. Every message has to name the
file, because the reader of that message is looking at a directory of nine files and needs to know
which one to open.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from quaestor.errors import ToolError
from quaestor.tools import ToolContext, default_registry
from quaestor.tools.frames import (
    coefficients,
    declared_features,
    key_columns,
    model_summary,
    predictions,
    projection,
    scored_frame,
)
from toolsupport import context, read_json, write_csv, write_json

CREDIT = Path(__file__).resolve().parent.parent / "subjects" / "credit_default"
MSR = Path(__file__).resolve().parent.parent / "subjects" / "msr_prepayment"


@pytest.fixture
def credit_ctx(tmp_path: Path, credit_run_dir: Path) -> ToolContext:
    """A private copy of the clean `credit_default` run, safe to break."""
    return context(tmp_path, CREDIT, credit_run_dir)


@pytest.fixture
def msr_ctx(tmp_path: Path, msr_run_dir: Path) -> ToolContext:
    """A private copy of the clean `msr_prepayment` run, safe to break."""
    return context(tmp_path, MSR, msr_run_dir)


# --- CSV and JSON reading ------------------------------------------------------------------------


def test_a_csv_with_a_header_and_no_rows_says_so(credit_ctx: ToolContext) -> None:
    (credit_ctx.out_dir / "data_test.csv").write_text("client_id,limit_bal\n", encoding="utf-8")
    with pytest.raises(ToolError, match="has a header but no rows"):
        declared_features(credit_ctx, pd.read_csv(credit_ctx.out_dir / "data_test.csv"))
        default_registry().call("profile_data", {}, credit_ctx)


def test_an_unreadable_csv_names_the_file(credit_ctx: ToolContext) -> None:
    (credit_ctx.out_dir / "predictions_test.csv").write_bytes(b"\xff\xfe not utf-8 at all")
    with pytest.raises(ToolError, match="predictions_test.csv"):
        predictions(credit_ctx, "test")


def test_a_prediction_column_that_is_not_numeric_names_the_file(credit_ctx: ToolContext) -> None:
    frame = pd.read_csv(credit_ctx.out_dir / "predictions_test.csv")
    frame["y_score"] = "not a number"
    write_csv(credit_ctx.out_dir / "predictions_test.csv", frame)
    with pytest.raises(ToolError, match="non-numeric y_true or y_score"):
        predictions(credit_ctx, "test")


def test_a_predictions_file_missing_a_column_names_the_column(credit_ctx: ToolContext) -> None:
    frame = pd.read_csv(credit_ctx.out_dir / "predictions_test.csv")
    write_csv(credit_ctx.out_dir / "predictions_test.csv", frame.drop(columns=["y_score"]))
    with pytest.raises(ToolError, match="has no 'y_score' column"):
        predictions(credit_ctx, "test")


def test_a_missing_json_file_names_the_file(msr_ctx: ToolContext) -> None:
    (msr_ctx.out_dir / "projection.json").unlink()
    with pytest.raises(ToolError, match="projection.json is missing"):
        projection(msr_ctx)


def test_an_unparsable_json_file_names_the_file(credit_ctx: ToolContext) -> None:
    (credit_ctx.out_dir / "model_summary.json").write_text("{not json", encoding="utf-8")
    with pytest.raises(ToolError, match="model_summary.json is not readable as JSON"):
        model_summary(credit_ctx)


def test_a_json_file_that_is_not_an_object_says_what_it_is(credit_ctx: ToolContext) -> None:
    write_json(credit_ctx.out_dir / "model_summary.json", [1, 2, 3])
    with pytest.raises(ToolError, match="is a list, not an object"):
        model_summary(credit_ctx)
    write_json(credit_ctx.out_dir / "model_summary.json", {"coefficients": "not a list"})
    with pytest.raises(ToolError, match="no 'coefficients' list"):
        coefficients(credit_ctx)
    write_json(credit_ctx.out_dir / "model_summary.json", {"coefficients": [{"feature": "a"}]})
    with pytest.raises(ToolError, match=r"coefficients\[0\]"):
        coefficients(credit_ctx)


def test_a_projection_that_is_not_an_object_says_what_it_is(msr_ctx: ToolContext) -> None:
    write_json(msr_ctx.out_dir / "projection.json", [1, 2, 3])
    with pytest.raises(ToolError, match="is a list, not an object"):
        projection(msr_ctx)


# --- identifiers and joins -----------------------------------------------------------------------


def test_a_contract_file_with_no_identifier_column_lists_the_two_spellings(
    credit_ctx: ToolContext,
) -> None:
    frame = pd.read_csv(credit_ctx.out_dir / "data_test.csv").drop(columns=["client_id"])
    with pytest.raises(ToolError, match=r"expected one of \['id', 'client_id'\]"):
        key_columns(credit_ctx, frame)


def test_a_hazard_panel_is_keyed_by_the_identifier_and_the_period(msr_ctx: ToolContext) -> None:
    frame = pd.read_csv(msr_ctx.out_dir / "data_test.csv")
    assert key_columns(msr_ctx, frame) == ["loan_id", "period"]


def test_predictions_without_the_period_cannot_be_joined(msr_ctx: ToolContext) -> None:
    frame = pd.read_csv(msr_ctx.out_dir / "predictions_test.csv")
    write_csv(msr_ctx.out_dir / "predictions_test.csv", frame.drop(columns=["period"]))
    with pytest.raises(ToolError, match=r"has no \['period'\] column"):
        scored_frame(msr_ctx, "test")


def test_a_data_file_holding_none_of_the_declared_features_says_what_it_holds(
    credit_ctx: ToolContext,
) -> None:
    frame = pd.DataFrame({"client_id": [1, 2], "something_else": [3.0, 4.0]})
    with pytest.raises(ToolError, match="none of the features package"):
        declared_features(credit_ctx, frame)


# --- the tools' remaining branches ---------------------------------------------------------------


def test_a_non_numeric_feature_matrix_is_refused_by_both_tools_that_fit_on_it(
    credit_ctx: ToolContext,
) -> None:
    frame = pd.read_csv(credit_ctx.out_dir / "data_train.csv")
    frame["age"] = "not a number"
    write_csv(credit_ctx.out_dir / "data_train.csv", frame)
    with pytest.raises(ToolError, match=r"non-numeric or missing value in \['age'\]"):
        default_registry().call("check_collinearity", {}, credit_ctx)
    with pytest.raises(ToolError, match=r"non-numeric value in \['age'\]"):
        default_registry().call("challenger_compare", {}, credit_ctx)


def test_a_missing_feature_value_is_not_a_non_numeric_one(credit_ctx: ToolContext) -> None:
    """D-125: the challenger reads a hole natively and says so; the VIF has no answer for one."""
    frame = pd.read_csv(credit_ctx.out_dir / "data_test.csv")
    frame.loc[frame.index[:300], "age"] = np.nan
    write_csv(credit_ctx.out_dir / "data_test.csv", frame)
    result = default_registry().call("challenger_compare", {}, credit_ctx)
    record = credit_ctx.store.load("challenger.missing_values")
    assert record["rows_with_a_missing_feature"]["train"] == 0.0
    assert record["rows_with_a_missing_feature"]["test"] > 0.0
    assert "ablation.baseline_auc" not in credit_ctx.store
    skipped = credit_ctx.store.load("ablation.skipped")
    assert "missing values" in skipped["reason"]
    assert "challenger.auc" in {artifact.name for artifact in result.artifacts}

    train = pd.read_csv(credit_ctx.out_dir / "data_train.csv")
    train.loc[train.index[:300], "age"] = np.nan
    write_csv(credit_ctx.out_dir / "data_train.csv", train)
    with pytest.raises(ToolError, match=r"non-numeric or missing value in \['age'\]"):
        default_registry().call("check_collinearity", {}, credit_ctx)


def test_a_feature_the_screen_cannot_score_is_reported_at_a_neutral_auc(
    credit_ctx: ToolContext,
) -> None:
    frame = pd.read_csv(credit_ctx.out_dir / "data_train.csv")
    frame["age"] = 40.0  # a constant column: no variation, so nothing to discriminate with
    frame["bill_trend_6m"] = np.nan  # and a column with no value at all
    write_csv(credit_ctx.out_dir / "data_train.csv", frame)
    result = default_registry().call("check_leakage", {}, credit_ctx)
    rows = {row["feature"]: row for row in credit_ctx.store.load("leakage.target_corr")}
    assert float(rows["age"]["single_feature_auc"]) == 0.5
    assert rows["age"]["numeric"] == "true"
    assert float(rows["bill_trend_6m"]["single_feature_auc"]) == 0.5
    assert rows["bill_trend_6m"]["numeric"] == "false"
    assert result.classes == []


def test_the_name_screen_matches_a_feature_named_after_the_target(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    from toolsupport import variant_package

    def rename(spec: dict[str, object]) -> None:
        features = spec["features"]
        assert isinstance(features, list)
        features[1]["name"] = "age_at_outcome"

    package = variant_package(tmp_path, CREDIT, rename)
    ctx = context(tmp_path, package, credit_run_dir)
    frame = pd.read_csv(ctx.out_dir / "data_train.csv").rename(columns={"age": "age_at_outcome"})
    write_csv(ctx.out_dir / "data_train.csv", frame)
    test_frame = pd.read_csv(ctx.out_dir / "data_test.csv").rename(
        columns={"age": "age_at_outcome"}
    )
    write_csv(ctx.out_dir / "data_test.csv", test_frame)
    result = default_registry().call("check_leakage", {}, ctx)
    assert ctx.store.value("leakage.name_screen.n_matched") == 1
    rows = {row["feature"]: row["matched"] for row in ctx.store.load("leakage.name_screen")}
    assert rows["age_at_outcome"] == "outcome"
    # The name screen reports and never raises: spec 3.7 gives it no candidate class.
    assert result.classes == []


def test_a_feature_with_no_value_at_all_still_gets_a_describe_row(
    credit_ctx: ToolContext,
) -> None:
    frame = pd.read_csv(credit_ctx.out_dir / "data_train.csv")
    frame["age"] = np.nan
    write_csv(credit_ctx.out_dir / "data_train.csv", frame)
    default_registry().call("profile_data", {"splits": ["train"], "features": ["age"]}, credit_ctx)
    rows = {row["feature"]: row for row in credit_ctx.store.load("profile.train.describe")}
    assert int(rows["age"]["count"]) == 0
    assert credit_ctx.store.value("profile.train.missing.max") == 1.0


def test_the_worst_train_to_test_comparison_may_be_the_score_itself(
    credit_ctx: ToolContext,
) -> None:
    frame = pd.read_csv(credit_ctx.out_dir / "predictions_test.csv")
    # A test split scored by a different model: the features have not moved, the score has.
    frame["y_score"] = np.clip(frame["y_score"] * 0.2, 1e-6, 1.0)
    write_csv(credit_ctx.out_dir / "predictions_test.csv", frame)
    result = default_registry().call("profile_data", {}, credit_ctx)
    assert credit_ctx.store.value("psi.y_score") == credit_ctx.store.value("psi.max")
    assert "'y_score'" in result.summary


def test_a_projection_missing_a_declared_shock_names_the_shock(msr_ctx: ToolContext) -> None:
    payload = read_json(msr_ctx.out_dir / "projection.json")
    del payload["value_by_shock"]["-300"]
    write_json(msr_ctx.out_dir / "projection.json", payload)
    with pytest.raises(ToolError, match=r"no value for the declared shocks \[-300\]"):
        default_registry().call("run_scenarios", {}, msr_ctx)


def test_a_projection_with_no_value_by_shock_says_so(msr_ctx: ToolContext) -> None:
    payload = read_json(msr_ctx.out_dir / "projection.json")
    payload["value_by_shock"] = "not an object"
    write_json(msr_ctx.out_dir / "projection.json", payload)
    with pytest.raises(ToolError, match="no 'value_by_shock' object"):
        default_registry().call("run_scenarios", {}, msr_ctx)


def test_a_projection_with_a_non_numeric_value_says_so(msr_ctx: ToolContext) -> None:
    payload = read_json(msr_ctx.out_dir / "projection.json")
    payload["value_by_shock"]["0"] = "free"
    write_json(msr_ctx.out_dir / "projection.json", payload)
    with pytest.raises(ToolError, match="non-numeric value in 'value_by_shock'"):
        default_registry().call("run_scenarios", {}, msr_ctx)


def test_run_scenarios_cites_the_subjects_own_projection_when_it_is_in_the_store(
    msr_ctx: ToolContext,
) -> None:
    payload = read_json(msr_ctx.out_dir / "projection.json")
    msr_ctx.store.put("run.projection", payload, "json", "the subject's projection.json")
    payload["value_by_shock"]["-300"] = payload["value_by_shock"]["300"] * 2.0
    write_json(msr_ctx.out_dir / "projection.json", payload)
    result = default_registry().call("run_scenarios", {}, msr_ctx)
    assert result.classes == ["X1"]
    assert msr_ctx.store.artifact("run.projection").hash in result.candidates[0].evidence


def test_run_scenarios_may_be_asked_to_test_a_different_expectation(msr_ctx: ToolContext) -> None:
    result = default_registry().call("run_scenarios", {"expectation": "negative"}, msr_ctx)
    assert result.classes == []
    assert "declared negative" in result.summary


def test_check_stability_needs_the_regime_column_in_the_data(msr_ctx: ToolContext) -> None:
    frame = pd.read_csv(msr_ctx.out_dir / "data_train.csv").drop(columns=["rate_regime"])
    write_csv(msr_ctx.out_dir / "data_train.csv", frame)
    with pytest.raises(ToolError, match="is not in data_train.csv"):
        default_registry().call("check_stability", {}, msr_ctx)


def test_check_stability_needs_two_regimes(msr_ctx: ToolContext) -> None:
    frame = pd.read_csv(msr_ctx.out_dir / "data_train.csv")
    frame["rate_regime"] = "falling"
    write_csv(msr_ctx.out_dir / "data_train.csv", frame)
    with pytest.raises(ToolError, match="only the value \\['falling'\\]"):
        default_registry().call("check_stability", {}, msr_ctx)


def test_check_stability_needs_both_outcomes_inside_each_regime(msr_ctx: ToolContext) -> None:
    data = pd.read_csv(msr_ctx.out_dir / "data_train.csv")
    predictions_frame = pd.read_csv(msr_ctx.out_dir / "predictions_train.csv")
    rising = (data["rate_regime"] == "rising").to_numpy()
    predictions_frame.loc[rising, "y_true"] = 0
    data.loc[rising, "prepaid"] = 0
    write_csv(msr_ctx.out_dir / "data_train.csv", data)
    write_csv(msr_ctx.out_dir / "predictions_train.csv", predictions_frame)
    with pytest.raises(ToolError, match="holds one outcome only"):
        default_registry().call("check_stability", {}, msr_ctx)


def test_check_stability_refuses_a_regime_whose_features_are_not_numeric(
    msr_ctx: ToolContext,
) -> None:
    frame = pd.read_csv(msr_ctx.out_dir / "data_train.csv")
    frame["incentive"] = "not a number"
    write_csv(msr_ctx.out_dir / "data_train.csv", frame)
    with pytest.raises(ToolError, match="no per-regime coefficient can be fitted"):
        default_registry().call("check_stability", {}, msr_ctx)


def test_stability_over_time_is_omitted_when_the_period_is_not_a_number(
    msr_ctx: ToolContext,
) -> None:
    for split in ("train", "test", "out_of_time", "vintage_holdout"):
        frame = pd.read_csv(msr_ctx.out_dir / f"data_{split}.csv")
        frame["period"] = frame["period"].astype(str) + "-M"
        write_csv(msr_ctx.out_dir / f"data_{split}.csv", frame)
        scores = pd.read_csv(msr_ctx.out_dir / f"predictions_{split}.csv")
        scores["period"] = scores["period"].astype(str) + "-M"
        write_csv(msr_ctx.out_dir / f"predictions_{split}.csv", scores)
    result = default_registry().call("check_stability", {}, msr_ctx)
    assert "stability.psi_over_time" not in msr_ctx.store
    assert result.classes == []


def test_a_classification_subject_has_no_psi_over_time_table(
    tmp_path: Path, credit_run_dir: Path
) -> None:
    from toolsupport import variant_package

    def add_a_regime(spec: dict[str, object]) -> None:
        spec["regime"] = {"column": "delinq_max_6m"}

    package = variant_package(tmp_path, CREDIT, add_a_regime)
    ctx = context(tmp_path, package, credit_run_dir)
    result = default_registry().call("check_stability", {}, ctx)
    # A classifier declares no time column, so there is no calendar to bucket by.
    assert "stability.psi_over_time" not in ctx.store
    assert "stability.auc_by_regime" in ctx.store
    assert isinstance(result.summary, str)


def test_a_challenger_cannot_be_fitted_on_a_split_with_one_outcome(
    credit_ctx: ToolContext,
) -> None:
    frame = pd.read_csv(credit_ctx.out_dir / "predictions_train.csv")
    frame["y_true"] = 0
    write_csv(credit_ctx.out_dir / "predictions_train.csv", frame)
    with pytest.raises(ToolError, match="one outcome only"):
        default_registry().call("challenger_compare", {}, credit_ctx)


def test_a_score_that_is_not_a_finite_number_is_refused(credit_ctx: ToolContext) -> None:
    frame = pd.read_csv(credit_ctx.out_dir / "predictions_test.csv")
    frame.loc[frame.index[0], "y_score"] = np.inf
    write_csv(credit_ctx.out_dir / "predictions_test.csv", frame)
    with pytest.raises(ToolError, match="not a finite number"):
        default_registry().call("compute_metrics", {"splits": ["test"]}, credit_ctx)


def test_a_sub_population_on_a_column_with_no_median_is_refused(msr_ctx: ToolContext) -> None:
    with pytest.raises(ToolError, match="no median to slice at"):
        default_registry().call(
            "compute_metrics",
            {
                "splits": ["test"],
                "subpopulation": {"column": "rate_regime", "rule": "below_median"},
            },
            msr_ctx,
        )


def test_the_single_feature_screen_needs_both_outcomes(credit_ctx: ToolContext) -> None:
    frame = pd.read_csv(credit_ctx.out_dir / "predictions_train.csv")
    frame["y_true"] = 0
    write_csv(credit_ctx.out_dir / "predictions_train.csv", frame)
    with pytest.raises(ToolError, match="holds one outcome only"):
        default_registry().call("check_leakage", {}, credit_ctx)


def test_the_degradation_rules_need_the_test_split_to_have_been_computed(
    credit_ctx: ToolContext,
) -> None:
    result = default_registry().call("compute_metrics", {"splits": ["train"]}, credit_ctx)
    assert result.classes == []
    assert "threshold.O1.auc_gap" not in credit_ctx.store
    assert "metrics.train.auc" in credit_ctx.store


def test_a_projection_that_states_no_change_for_a_shock_is_not_reported_as_disagreeing(
    msr_ctx: ToolContext,
) -> None:
    payload = read_json(msr_ctx.out_dir / "projection.json")
    del payload["value_change"]["-300"]
    write_json(msr_ctx.out_dir / "projection.json", payload)
    result = default_registry().call("run_scenarios", {}, msr_ctx)
    assert result.classes == []
    assert "disagrees" not in result.summary


def test_r0_fires_when_a_completed_run_reports_a_duration_past_the_cap(
    tmp_path: Path, credit_run_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A run the sandbox returned rather than killed, whose wall clock is nonetheless past the cap:
    # the kill and the clock can disagree at the boundary, and the tool trusts the clock.
    from quaestor.sandbox import RunResult
    from quaestor.tools import run as run_module

    ctx = context(tmp_path, CREDIT, credit_run_dir)
    real = run_module.sandbox_run_model

    def slow(*args: object, **kwargs: object) -> RunResult:
        result = real(*args, **kwargs)  # type: ignore[arg-type]
        return result.model_copy(update={"duration_s": result.max_seconds + 1.0})

    monkeypatch.setattr(run_module, "sandbox_run_model", slow)
    result = default_registry().call("run_model", {"synthetic": 500}, ctx)
    assert result.classes == ["R0"]
    assert "against the 300 s cap" in result.candidates[0].detail
    assert result.candidates[0].suggested_severity.value == "medium"
