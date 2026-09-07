"""The statistics of spec 3.7, each against a longhand example.

Every expected value in this module was computed by hand or is exact by construction, which is the
point of writing the statistics out rather than importing them: a number in a validation report has
to be defensible one line at a time. Where a value is arithmetic, the arithmetic is in the test's
comment.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from quaestor.errors import ToolError
from quaestor.tools import stats

# --- PSI, on a hand-computed two-bin example ----------------------------------------------------


def test_psi_on_the_hand_computed_two_bin_example() -> None:
    # Expected = [0, 0, 1, 1]: the single interior edge is the median, 0.5, so the two bins hold
    # half the sample each. Actual = [0, 0, 0, 1]: three quarters below, one quarter above.
    #   PSI = (0.75 - 0.5) * ln(0.75 / 0.5) + (0.25 - 0.5) * ln(0.25 / 0.5)
    #       = 0.25 * ln(1.5) - 0.25 * ln(0.5)
    #       = 0.25 * 0.4054651081 + 0.25 * 0.6931471806
    #       = 0.2746530722
    value = stats.psi([0.0, 0.0, 1.0, 1.0], [0.0, 0.0, 0.0, 1.0], bins=2)
    expected = 0.25 * math.log(1.5) - 0.25 * math.log(0.5)
    assert value == pytest.approx(expected, abs=1e-12)
    assert value == pytest.approx(0.2746530722, abs=1e-9)


def test_psi_is_zero_when_the_two_samples_fill_the_bins_alike() -> None:
    sample = np.linspace(0.0, 1.0, 500)
    assert stats.psi(sample, sample) == pytest.approx(0.0, abs=1e-12)


def test_psi_floors_an_empty_bin_instead_of_returning_an_infinity() -> None:
    # Every actual value falls in the top bin, so nine of the ten bins are empty; the 0.5% floor
    # is what keeps the logarithm finite.
    value = stats.psi(np.linspace(0.0, 1.0, 1000), np.full(1000, 0.99))
    assert math.isfinite(value)
    assert value > 4.0


def test_psi_collapses_duplicate_quantile_edges_on_a_discrete_feature() -> None:
    # A feature that is 0 in 95% of rows has every one of the nine interior quantiles at 0, so the
    # ten requested bins collapse to the two the sample can support.
    sample = [0.0] * 95 + [1.0] * 5
    edges = stats.psi_bin_edges(sample, bins=10)
    assert edges.tolist() == [0.0]
    assert stats.psi(sample, sample) == pytest.approx(0.0)
    assert stats.psi(sample, [0.0] * 50 + [1.0] * 50) > 0.5


def test_a_statistic_on_an_empty_sample_says_so() -> None:
    with pytest.raises(ToolError, match="empty sample"):
        stats.psi([], [1.0])


# --- CSI ----------------------------------------------------------------------------------------


def test_csi_is_zero_when_the_coefficient_is_zero() -> None:
    reference = np.linspace(0.0, 1.0, 200)
    actual = np.linspace(0.5, 1.5, 200)
    assert stats.csi(reference, actual, 0.0) == pytest.approx(0.0)


def test_csi_grows_with_the_coefficient_and_with_the_shift() -> None:
    reference = np.linspace(0.0, 1.0, 400)
    small = np.linspace(0.1, 1.1, 400)
    large = np.linspace(0.6, 1.6, 400)
    assert stats.csi(reference, large, 1.0) > stats.csi(reference, small, 1.0) > 0.0
    assert stats.csi(reference, large, 2.0) == pytest.approx(2.0 * stats.csi(reference, large, 1.0))


def test_csi_of_a_constant_feature_is_zero_rather_than_a_division_by_zero() -> None:
    assert stats.csi(np.full(50, 3.0), np.full(50, 4.0), 1.5) == 0.0


# --- KS and Brier, on five-row examples ---------------------------------------------------------


def test_ks_on_a_five_row_example() -> None:
    # Scores 0.1 0.2 0.3 0.4 0.5 with outcomes 0 0 1 0 1. Two events, three non-events.
    #   after 0.1: F+ = 0/2 = 0.00, F- = 1/3 = 0.3333, |d| = 0.3333
    #   after 0.2: F+ = 0.00,       F- = 2/3 = 0.6667, |d| = 0.6667  <- the maximum
    #   after 0.3: F+ = 1/2 = 0.50, F- = 0.6667,       |d| = 0.1667
    #   after 0.4: F+ = 0.50,       F- = 3/3 = 1.0000, |d| = 0.5000
    #   after 0.5: F+ = 1.00,       F- = 1.0000,       |d| = 0.0000
    value = stats.ks([0, 0, 1, 0, 1], [0.1, 0.2, 0.3, 0.4, 0.5])
    assert value == pytest.approx(2.0 / 3.0, abs=1e-12)


def test_ks_is_one_when_the_score_separates_the_classes_completely() -> None:
    assert stats.ks([0, 0, 0, 1, 1], [0.1, 0.2, 0.3, 0.8, 0.9]) == pytest.approx(1.0)


def test_ks_needs_both_classes() -> None:
    with pytest.raises(ToolError, match="one class"):
        stats.ks([0, 0, 0], [0.1, 0.2, 0.3])


def test_brier_on_a_five_row_example() -> None:
    # (0.1-0)^2 + (0.2-0)^2 + (0.3-1)^2 + (0.4-0)^2 + (0.5-1)^2
    #   = 0.01 + 0.04 + 0.49 + 0.16 + 0.25 = 0.95, over five rows = 0.19
    value = stats.brier([0, 0, 1, 0, 1], [0.1, 0.2, 0.3, 0.4, 0.5])
    assert value == pytest.approx(0.19, abs=1e-12)


def test_brier_is_zero_on_a_perfect_forecast() -> None:
    assert stats.brier([0, 1, 0, 1, 1], [0.0, 1.0, 0.0, 1.0, 1.0]) == pytest.approx(0.0)


def test_a_score_outside_zero_and_one_is_refused() -> None:
    with pytest.raises(ToolError, match="not a probability"):
        stats.brier([0, 1], [0.5, 1.4])


def test_a_score_that_is_not_finite_is_refused_by_both_the_auc_and_the_brier() -> None:
    with pytest.raises(ToolError, match="not a finite number"):
        stats.auc([0, 1, 0, 1], [0.1, 0.2, float("inf"), 0.4])
    with pytest.raises(ToolError, match="not a finite number"):
        stats.brier([0, 1], [0.5, float("nan")])


def test_an_outcome_that_is_not_zero_or_one_is_refused() -> None:
    with pytest.raises(ToolError, match="not 0 and 1"):
        stats.brier([0, 2], [0.5, 0.5])


def test_logloss_on_a_two_row_example() -> None:
    # -(ln 0.8 + ln 0.6) / 2 = -(-0.2231435513 - 0.5108256238) / 2 = 0.3669845875
    value = stats.logloss([1, 0], [0.8, 0.4])
    assert value == pytest.approx(-(math.log(0.8) + math.log(0.6)) / 2.0, abs=1e-12)
    assert value == pytest.approx(0.3669845875, abs=1e-9)


# --- Gini and AUC -------------------------------------------------------------------------------


def test_gini_is_twice_the_auc_minus_one() -> None:
    assert stats.gini(0.75) == pytest.approx(0.5)
    assert stats.gini(0.5) == pytest.approx(0.0)


def test_auc_on_a_perfectly_ordered_example() -> None:
    assert stats.auc([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9]) == pytest.approx(1.0)
    assert stats.auc([1, 1, 0, 0], [0.1, 0.2, 0.8, 0.9]) == pytest.approx(0.0)


def test_auc_on_a_sample_with_one_class_says_which_outcome_it_held() -> None:
    with pytest.raises(ToolError, match="no AUC"):
        stats.auc([0, 0, 0], [0.1, 0.2, 0.3])


# --- Calibration slope and intercept ------------------------------------------------------------
#
# Both cases are exact. Twelve rows in three groups of four, with predicted probabilities 0.25, 0.5
# and 0.75 and observed event counts 1, 2 and 3, so the observed rate in each group *is* the
# predicted probability. The score equations of a logistic regression of y on logit(p) are
# sum(y - mu) = 0 and sum(logit(p) * (y - mu)) = 0, and both hold exactly at slope 1, intercept 0.


_EXACT_P = [0.25] * 4 + [0.5] * 4 + [0.75] * 4
_EXACT_Y = [1, 0, 0, 0] + [1, 1, 0, 0] + [1, 1, 1, 0]


def test_the_calibration_slope_of_an_exactly_calibrated_sample_is_one() -> None:
    slope, intercept = stats.calibration_slope_intercept(_EXACT_Y, _EXACT_P)
    assert slope == pytest.approx(1.0, abs=1e-9)
    assert intercept == pytest.approx(0.0, abs=1e-9)


def test_the_calibration_slope_of_an_over_confident_sample_is_a_half() -> None:
    # The same three groups, with the same observed rates 0.25, 0.5, 0.75, but predictions whose
    # log odds are doubled: 0.1, 0.5, 0.9. At slope 0.5 and intercept 0 the fitted probabilities
    # are sigmoid(0.5 * logit(0.1)) = 0.25, 0.5 and 0.75 -- the observed rates exactly -- so every
    # residual is zero and both score equations hold. The model is over-confident and the slope
    # says so.
    over_confident = [0.1] * 4 + [0.5] * 4 + [0.9] * 4
    slope, intercept = stats.calibration_slope_intercept(_EXACT_Y, over_confident)
    assert slope == pytest.approx(0.5, abs=1e-9)
    assert intercept == pytest.approx(0.0, abs=1e-9)


def test_the_calibration_slope_of_an_under_confident_sample_is_above_one() -> None:
    under_confident = [0.4] * 4 + [0.5] * 4 + [0.6] * 4
    slope, _ = stats.calibration_slope_intercept(_EXACT_Y, under_confident)
    assert slope > 1.0


def test_a_calibration_slope_needs_variation_in_the_prediction() -> None:
    with pytest.raises(ToolError, match="no calibration slope"):
        stats.calibration_slope_intercept([0, 1, 0, 1], [0.5, 0.5, 0.5, 0.5])


def test_a_calibration_slope_needs_both_outcomes() -> None:
    with pytest.raises(ToolError, match="both an event and a non-event"):
        stats.calibration_slope_intercept([1, 1, 1], [0.2, 0.5, 0.8])


def test_a_separable_sample_does_not_converge_and_says_why() -> None:
    with pytest.raises(ToolError, match="did not converge"):
        stats.calibration_slope_intercept(
            [0, 0, 1, 1], [0.01, 0.02, 0.98, 0.99], max_iterations=3, tolerance=1e-14
        )


# --- VIF, on a three-column example with a known linear dependency -------------------------------


def test_vif_on_three_columns_with_a_known_linear_dependency() -> None:
    # x3 = x1 + x2 exactly, so each column's R-squared on the other two is 1 and every VIF is
    # infinite; the cap is what an artifact can hold.
    rng = np.random.default_rng(20260901)
    x1 = rng.normal(size=200)
    x2 = rng.normal(size=200)
    frame = pd.DataFrame({"x1": x1, "x2": x2, "x3": x1 + x2})
    factors = stats.variance_inflation_factors(frame)
    assert set(factors) == {"x1", "x2", "x3"}
    assert min(factors.values()) == pytest.approx(stats.VIF_CAP)


def test_vif_on_three_columns_with_a_known_correlation() -> None:
    # x2 = x1 + noise with a correlation of exactly 0.8 by construction: R-squared of x2 on x1 is
    # 0.64, so its VIF is 1 / (1 - 0.64) = 2.7778, and x3 is independent of both.
    rng = np.random.default_rng(7)
    base = rng.normal(size=200_000)
    noise = rng.normal(size=200_000)
    x1 = (base - base.mean()) / base.std()
    residual = noise - np.dot(noise, x1) / np.dot(x1, x1) * x1
    residual = (residual - residual.mean()) / residual.std()
    x2 = 0.8 * x1 + math.sqrt(1.0 - 0.64) * residual
    frame = pd.DataFrame({"x1": x1, "x2": x2, "x3": rng.normal(size=200_000)})
    factors = stats.variance_inflation_factors(frame)
    assert factors["x1"] == pytest.approx(1.0 / (1.0 - 0.64), abs=0.02)
    assert factors["x2"] == pytest.approx(1.0 / (1.0 - 0.64), abs=0.02)
    assert factors["x3"] == pytest.approx(1.0, abs=0.02)


def test_a_constant_column_gets_the_cap_rather_than_a_singular_matrix() -> None:
    frame = pd.DataFrame({"a": [1.0, 2.0, 3.0, 4.0], "b": [5.0, 5.0, 5.0, 5.0]})
    assert stats.variance_inflation_factors(frame)["b"] == pytest.approx(stats.VIF_CAP)


def test_a_single_column_has_a_vif_of_one() -> None:
    assert stats.variance_inflation_factors(pd.DataFrame({"a": [1.0, 2.0, 3.0]})) == {"a": 1.0}


def test_vif_needs_a_column_and_a_row() -> None:
    with pytest.raises(ToolError, match="at least one column"):
        stats.variance_inflation_factors(pd.DataFrame())
    with pytest.raises(ToolError, match="at least one row"):
        stats.variance_inflation_factors(pd.DataFrame({"a": []}))


# --- Belsley's condition number ------------------------------------------------------------------


def test_belsleys_kappa_of_an_orthogonal_design_is_one() -> None:
    # Two orthogonal standardised columns have equal singular values.
    frame = pd.DataFrame({"a": [1.0, -1.0, 1.0, -1.0], "b": [1.0, 1.0, -1.0, -1.0]})
    assert stats.belsley_condition_number(frame) == pytest.approx(1.0, abs=1e-9)


def test_belsleys_kappa_is_the_square_root_of_the_eigenvalue_ratio() -> None:
    # For two standardised columns with correlation r the correlation matrix's eigenvalues are
    # 1 + r and 1 - r, so kappa is sqrt((1 + r) / (1 - r)). With r = 0.6 that is sqrt(4) = 2.
    rng = np.random.default_rng(11)
    base = rng.normal(size=100_000)
    noise = rng.normal(size=100_000)
    a = (base - base.mean()) / base.std()
    residual = noise - np.dot(noise, a) / np.dot(a, a) * a
    residual = (residual - residual.mean()) / residual.std()
    b = 0.6 * a + math.sqrt(1.0 - 0.36) * residual
    kappa = stats.belsley_condition_number(pd.DataFrame({"a": a, "b": b}))
    assert kappa == pytest.approx(math.sqrt(1.6 / 0.4), abs=0.01)


def test_belsleys_kappa_of_a_constant_column_is_the_cap() -> None:
    frame = pd.DataFrame({"a": [1.0, 2.0, 3.0], "b": [1.0, 1.0, 1.0]})
    assert stats.belsley_condition_number(frame) == pytest.approx(stats.VIF_CAP)


def test_belsleys_kappa_of_a_rank_deficient_design_is_the_cap() -> None:
    rng = np.random.default_rng(3)
    a = rng.normal(size=100)
    frame = pd.DataFrame({"a": a, "b": rng.normal(size=100), "c": a * 2.0})
    assert stats.belsley_condition_number(frame) == pytest.approx(stats.VIF_CAP)


def test_belsleys_kappa_needs_a_column_and_a_row() -> None:
    with pytest.raises(ToolError, match="at least one column"):
        stats.belsley_condition_number(pd.DataFrame())
    with pytest.raises(ToolError, match="at least one row"):
        stats.belsley_condition_number(pd.DataFrame({"a": []}))


# --- CPR ------------------------------------------------------------------------------------------


def test_cpr_annualises_a_monthly_hazard() -> None:
    # 1 - (1 - 0.01) ** 12 = 1 - 0.99 ** 12 = 1 - 0.8863848717 = 0.1136151283
    assert stats.cpr_from_smm(0.01) == pytest.approx(0.1136151283, abs=1e-9)
    assert stats.cpr_from_smm(0.0) == pytest.approx(0.0)
    assert stats.cpr_from_smm(1.0) == pytest.approx(1.0)


def test_a_monthly_rate_outside_zero_and_one_is_refused() -> None:
    with pytest.raises(ToolError, match="not a monthly rate"):
        stats.cpr_from_smm(1.4)


# --- Calibration and decile tables ----------------------------------------------------------------


def test_the_calibration_table_has_ten_ascending_equal_count_bins() -> None:
    rng = np.random.default_rng(5)
    scores = rng.uniform(size=1500)
    truth = (rng.uniform(size=1500) < scores).astype(int)
    rows = stats.calibration_table(truth, scores)
    assert [row["bin"] for row in rows] == list(range(1, 11))
    assert {row["count"] for row in rows} == {150}
    predicted = [row["mean_predicted"] for row in rows]
    assert predicted == sorted(predicted)
    assert sum(row["count"] for row in rows) == 1500


def test_the_decile_table_puts_the_highest_probabilities_first() -> None:
    truth = [1, 1, 1, 0, 0, 0, 1, 0, 0, 0]
    scores = [0.9, 0.85, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
    rows = stats.deciles_table(truth, scores)
    assert [row["decile"] for row in rows] == list(range(1, 11))
    assert [row["count"] for row in rows] == [1] * 10
    assert rows[0]["event_rate"] == pytest.approx(1.0)
    # Base rate 0.4, so a decile that is all events has a lift of 1 / 0.4 = 2.5.
    assert rows[0]["lift"] == pytest.approx(2.5)
    assert rows[-1]["event_rate"] == pytest.approx(0.0)


def test_top_two_capture_is_the_share_of_events_in_the_first_two_deciles() -> None:
    truth = [1, 1, 1, 0, 0, 0, 1, 0, 0, 0]
    scores = [0.9, 0.85, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
    rows = stats.deciles_table(truth, scores)
    # Four events in all, two of them in the top two deciles.
    assert stats.top_capture(rows) == pytest.approx(0.5)


def test_top_capture_of_a_table_with_no_event_is_zero() -> None:
    rows = stats.deciles_table([0, 0, 0, 0], [0.1, 0.2, 0.3, 0.4])
    assert stats.top_capture(rows) == 0.0
    assert all(row["lift"] == 0.0 for row in rows)


def test_the_tables_degrade_gracefully_on_a_sample_smaller_than_ten() -> None:
    rows = stats.calibration_table([0, 1, 0], [0.1, 0.9, 0.2])
    assert len(rows) == 3
    assert [row["count"] for row in rows] == [1, 1, 1]
