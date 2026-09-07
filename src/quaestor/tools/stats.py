"""The statistics, by hand: PSI, CSI, KS, Gini, Brier, calibration, VIF, Belsley's kappa, CPR.

Spec section 3.7 asks for these to be implemented here and tested against longhand examples, with
AUC alone taken from scikit-learn. The reason is not distrust of a library: it is that a
validation report's numbers have to be defensible one line at a time, and a validator who is asked
"what did you bin PSI on?" must be able to point at the ten lines that did it rather than at a
package version. So each function is small, each states its convention in its docstring, and each
has a test whose expected value was computed by hand.

The conventions, once, because they are the part that varies between shops:

* **PSI** bins the *expected* sample -- the training split -- into ten quantile bins, applies the
  same edges to the actual sample, floors both proportions at 0.5% so an empty bin cannot make the
  index infinite, and sums ``(actual - expected) * ln(actual / expected)``. Duplicate quantile
  edges collapse, so a feature with twelve distinct values gets the bins it can support rather
  than an error.
* **CSI** is *not* a second name for a feature's PSI, which would make ``csi.<feature>`` a copy of
  ``psi.<feature>``. It is the shift in the linear predictor attributable to one feature: the
  redistribution of that feature's mass across the same bins, weighted by what the champion's
  coefficient contributes in each bin (DECISIONS D-052).
* **KS** is the largest vertical distance between the empirical distribution of the score among
  events and among non-events.
* The **calibration slope and intercept** come from a logistic regression of the outcome on
  ``logit(p)``, fitted by the Newton iterations in :func:`calibration_slope_intercept` rather than
  by scikit-learn, whose ``LogisticRegression`` is penalised by default and would return a slope
  shrunk by a regularisation constant nobody declared.
* **VIF** is ``1 / (1 - R^2)`` of each column on the others, from an unpenalised least squares
  fit, capped at :data:`VIF_CAP` so that an exactly dependent column gives a large finite number
  instead of an infinity the artifact store cannot hold.
* **Belsley's kappa** is the ratio of the largest to the smallest singular value of the
  column-standardised design matrix, which is the quantity the threshold of 30 is stated for
  (DECISIONS D-035).
* **CPR** annualises a monthly single-month mortality: ``1 - (1 - SMM) ** 12``.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Final

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from sklearn.linear_model import LinearRegression
from sklearn.metrics import roc_auc_score

from ..errors import ToolError

__all__ = [
    "MONTHS_PER_YEAR",
    "PSI_BINS",
    "PSI_FLOOR",
    "VIF_CAP",
    "auc",
    "belsley_condition_number",
    "brier",
    "calibration_slope_intercept",
    "calibration_table",
    "cpr_from_smm",
    "csi",
    "deciles_table",
    "gini",
    "ks",
    "logloss",
    "psi",
    "psi_bin_edges",
    "top_capture",
    "variance_inflation_factors",
]

PSI_BINS: Final = 10
"""How many quantile bins PSI and CSI use, from the expected sample."""

PSI_FLOOR: Final = 0.005
"""The 0.5% floor on a bin's proportion, so an empty bin cannot make the index infinite."""

VIF_CAP: Final = 1.0e6
"""What an exactly dependent column's VIF is reported as; an infinity has no canonical form."""

MONTHS_PER_YEAR: Final = 12
"""The exponent that turns a monthly hazard into an annual CPR."""

_EPS: Final = 1e-12
"""Clip for a probability before a logit or a logarithm."""


Vector = NDArray[np.float64]


def _as_vector(values: Sequence[float] | NDArray[Any] | pd.Series) -> Vector:
    """Return a one-dimensional float array, whatever array-like was passed."""
    array = np.asarray(values, dtype=float).reshape(-1)
    if array.size == 0:
        raise ToolError("a statistic cannot be computed on an empty sample")
    return array


def _check_probabilities(scores: Vector) -> Vector:
    """Insist that scores are probabilities, naming the offending value if they are not."""
    if not np.all(np.isfinite(scores)):
        raise ToolError("a predicted score is not a finite number")
    if scores.min() < 0.0 or scores.max() > 1.0:
        raise ToolError(
            f"predicted scores run from {scores.min():.6g} to {scores.max():.6g}, which is not a "
            "probability; every metric here reads y_score as one"
        )
    return scores


def _check_binary(truth: Vector) -> Vector:
    """Insist that outcomes are 0 or 1."""
    unique = np.unique(truth)
    if not np.all(np.isin(unique, (0.0, 1.0))):
        raise ToolError(f"y_true holds {unique.tolist()}, not 0 and 1")
    return truth


def auc(y_true: Sequence[float] | NDArray[Any] | pd.Series, y_score: Any) -> float:
    """Return the area under the ROC curve, from scikit-learn.

    The one statistic spec section 3.7 does not ask for by hand: the trapezoidal rule over a sorted
    score is not the part of a validation anyone doubts, and scikit-learn's tie handling is the
    convention every reader will assume.

    Args:
        y_true: The outcomes, 0 or 1.
        y_score: The predicted probabilities.

    Returns:
        The AUC.

    Raises:
        ToolError: A score is not a finite number, or the sample holds only one class so no AUC
            exists. The message says which, because a sub-population request usually gets the
            second one wrong.
    """
    truth = _check_binary(_as_vector(y_true))
    scores = _as_vector(y_score)
    if not np.all(np.isfinite(scores)):
        raise ToolError(
            "a score passed to the AUC is not a finite number; an AUC ranks its inputs and a "
            "missing or infinite rank has no place in the ordering"
        )
    if truth.min() == truth.max():
        raise ToolError(
            f"every one of the {truth.size} rows has y_true = {truth[0]:.0f}, so there is no AUC "
            "to compute; a sub-population with no event cannot be scored for discrimination"
        )
    return float(roc_auc_score(truth, scores))


def gini(area_under_curve: float) -> float:
    """Return ``2 * AUC - 1``.

    Args:
        area_under_curve: The AUC.

    Returns:
        The Gini coefficient.
    """
    return 2.0 * float(area_under_curve) - 1.0


def ks(y_true: Any, y_score: Any) -> float:
    """Return the Kolmogorov-Smirnov separation between events and non-events.

    The two empirical distribution functions are stepped through the score in ascending order and
    the largest absolute difference between them is returned.

    Args:
        y_true: The outcomes, 0 or 1.
        y_score: The predicted probabilities.

    Returns:
        The KS statistic, in [0, 1].

    Raises:
        ToolError: The sample holds only one class.
    """
    truth = _check_binary(_as_vector(y_true))
    scores = _as_vector(y_score)
    positives = float(truth.sum())
    negatives = float(truth.size - truth.sum())
    if positives == 0.0 or negatives == 0.0:
        raise ToolError("KS needs both an event and a non-event; this sample has one class")
    order = np.argsort(scores, kind="stable")
    sorted_truth = truth[order]
    cumulative_positive = np.cumsum(sorted_truth) / positives
    cumulative_negative = np.cumsum(1.0 - sorted_truth) / negatives
    return float(np.max(np.abs(cumulative_positive - cumulative_negative)))


def brier(y_true: Any, y_score: Any) -> float:
    """Return the Brier score: the mean squared difference between probability and outcome.

    Args:
        y_true: The outcomes, 0 or 1.
        y_score: The predicted probabilities.

    Returns:
        The Brier score.
    """
    truth = _check_binary(_as_vector(y_true))
    scores = _check_probabilities(_as_vector(y_score))
    return float(np.mean((scores - truth) ** 2))


def logloss(y_true: Any, y_score: Any) -> float:
    """Return the mean negative log likelihood, with probabilities clipped away from 0 and 1.

    Args:
        y_true: The outcomes, 0 or 1.
        y_score: The predicted probabilities.

    Returns:
        The log loss.
    """
    truth = _check_binary(_as_vector(y_true))
    scores = np.clip(_check_probabilities(_as_vector(y_score)), _EPS, 1.0 - _EPS)
    return float(-np.mean(truth * np.log(scores) + (1.0 - truth) * np.log(1.0 - scores)))


def logit(probabilities: Vector) -> Vector:
    """Return ``log(p / (1 - p))`` with the probabilities clipped away from 0 and 1.

    Args:
        probabilities: Probabilities.

    Returns:
        Their log odds.
    """
    clipped = np.clip(probabilities, _EPS, 1.0 - _EPS)
    return np.asarray(np.log(clipped / (1.0 - clipped)), dtype=float)


def calibration_slope_intercept(
    y_true: Any, y_score: Any, *, max_iterations: int = 100, tolerance: float = 1e-10
) -> tuple[float, float]:
    """Fit ``logit(P(y = 1)) = intercept + slope * logit(p)`` by Newton's method and return both.

    The fit is the unpenalised maximum likelihood estimate, obtained by iteratively reweighted
    least squares written out here: at each step the score vector is ``X'(y - mu)`` and the
    Hessian is ``-X'WX`` with ``W = mu(1 - mu)``, and the step is their solution. Perfect
    calibration is exactly ``(1.0, 0.0)``, which is what the test asserts on a sample constructed
    to make it so.

    scikit-learn's ``LogisticRegression`` is not used, and not only because spec section 3.7 says
    to write it: its default ``C = 1.0`` penalises the coefficient, so a perfectly calibrated
    sample would come back with a slope short of 1 by an amount that depends on the sample size.

    Args:
        y_true: The outcomes, 0 or 1.
        y_score: The predicted probabilities.
        max_iterations: How many Newton steps to take before giving up.
        tolerance: The largest coefficient change that counts as converged.

    Returns:
        ``(slope, intercept)``.

    Raises:
        ToolError: The sample has one class, the design is singular -- which happens when every
            prediction is the same number, so there is no slope to fit -- or the iteration did not
            converge.
    """
    truth = _check_binary(_as_vector(y_true))
    scores = _check_probabilities(_as_vector(y_score))
    if truth.min() == truth.max():
        raise ToolError("a calibration slope needs both an event and a non-event in the sample")
    predictor = logit(scores)
    if float(predictor.std()) == 0.0:
        raise ToolError(
            "every prediction in this sample is the same number, so the logit of the prediction "
            "has no variation and no calibration slope exists"
        )
    design = np.column_stack([np.ones_like(predictor), predictor])
    beta = np.zeros(2, dtype=float)
    for _ in range(max_iterations):
        eta = design @ beta
        mu = 1.0 / (1.0 + np.exp(-eta))
        weights = np.clip(mu * (1.0 - mu), _EPS, None)
        gradient = design.T @ (truth - mu)
        hessian = design.T @ (design * weights[:, None])
        try:
            step = np.linalg.solve(hessian, gradient)
        except np.linalg.LinAlgError as exc:  # pragma: no cover - guarded by the std check above
            raise ToolError(f"the calibration fit's design is singular: {exc}") from exc
        beta = beta + step
        if float(np.max(np.abs(step))) < tolerance:
            return float(beta[1]), float(beta[0])
    raise ToolError(
        f"the calibration slope did not converge in {max_iterations} Newton steps; the sample is "
        "probably separable, which means no finite maximum likelihood estimate exists"
    )


def psi_bin_edges(expected: Any, *, bins: int = PSI_BINS) -> Vector:
    """Return the interior bin edges: the quantiles of the expected sample.

    Duplicate edges are collapsed, so a feature with fewer distinct values than bins is binned as
    finely as it can be rather than raising.

    Args:
        expected: The reference sample, which is the training split.
        bins: How many bins to aim for.

    Returns:
        The interior edges, ascending; the outer edges are minus and plus infinity.
    """
    values = _as_vector(expected)
    quantiles = np.linspace(0.0, 1.0, bins + 1)[1:-1]
    return np.asarray(np.unique(np.quantile(values, quantiles)), dtype=float)


def _bin_index(values: Vector, edges: Vector) -> NDArray[np.intp]:
    """Return each value's bin, the bins being ``(-inf, e1], (e1, e2], ..., (ek, inf)``.

    The upper edge belongs to its bin, which is what makes the binning usable on a feature with a
    mass point: a column that is zero in most rows has its zeros in the first bin rather than
    spread by whichever side of a half-open interval a floating-point comparison lands on.
    """
    return np.asarray(np.digitize(values, edges, right=True), dtype=np.intp)


def _proportions(values: Vector, edges: Vector) -> Vector:
    """Return the share of a sample falling in each bin, floored at :data:`PSI_FLOOR`."""
    counts = np.bincount(_bin_index(values, edges), minlength=edges.size + 1)
    return np.maximum(counts / float(values.size), PSI_FLOOR)


def psi(expected: Any, actual: Any, *, bins: int = PSI_BINS) -> float:
    """Return the population stability index of an actual sample against an expected one.

    Args:
        expected: The reference sample; the training split, by convention.
        actual: The sample being compared with it.
        bins: How many quantile bins to cut the expected sample into.

    Returns:
        The index. Zero when the two samples fall in the bins in the same proportions.
    """
    reference = _as_vector(expected)
    observed = _as_vector(actual)
    edges = psi_bin_edges(reference, bins=bins)
    expected_share = _proportions(reference, edges)
    actual_share = _proportions(observed, edges)
    return float(np.sum((actual_share - expected_share) * np.log(actual_share / expected_share)))


def csi(expected: Any, actual: Any, coefficient: float, *, bins: int = PSI_BINS) -> float:
    """Return the characteristic stability index: one feature's contribution to the score shift.

    The same bins as :func:`psi`, but the redistribution of mass is weighted by what the feature
    contributes to the linear predictor in each bin -- the coefficient times the bin's mean
    standardised value -- and the result is the absolute shift in the linear predictor
    attributable to this feature alone. Reading CSI as a synonym for the feature's own PSI would
    make ``csi.<feature>`` a copy of ``psi.<feature>`` and tell a reader nothing new
    (DECISIONS D-052).

    Args:
        expected: The feature's values in the reference sample.
        actual: The feature's values in the sample being compared.
        coefficient: The champion's coefficient on this feature, as fitted on standardised inputs.
        bins: How many quantile bins to cut the expected sample into.

    Returns:
        The absolute shift in the linear predictor, in log-odds.
    """
    reference = _as_vector(expected)
    observed = _as_vector(actual)
    spread = float(reference.std())
    if spread == 0.0:
        return 0.0
    edges = psi_bin_edges(reference, bins=bins)
    expected_share = _proportions(reference, edges)
    actual_share = _proportions(observed, edges)
    assignment = _bin_index(reference, edges)
    standardised = (reference - float(reference.mean())) / spread
    points = np.array(
        [
            float(coefficient) * float(standardised[assignment == index].mean())
            if np.any(assignment == index)
            else 0.0
            for index in range(expected_share.size)
        ],
        dtype=float,
    )
    return float(abs(np.sum((actual_share - expected_share) * points)))


def variance_inflation_factors(frame: pd.DataFrame) -> dict[str, float]:
    """Return each column's VIF: ``1 / (1 - R^2)`` of that column on all the others.

    Computed from an unpenalised least squares fit rather than by inverting the correlation
    matrix, so a column with no variance -- which a seeded defect can produce -- gives a finite
    answer rather than a singular matrix. A single column has nothing to be inflated by and gets
    1.0. The result is capped at :data:`VIF_CAP`, because an exactly dependent column's VIF is an
    infinity and an artifact must be a real number.

    Args:
        frame: The design, one column per feature.

    Returns:
        Feature name to VIF, in the frame's column order.

    Raises:
        ToolError: The frame has no columns or no rows.
    """
    columns = list(frame.columns)
    if not columns:
        raise ToolError("a VIF needs at least one column")
    if len(frame.index) == 0:
        raise ToolError("a VIF needs at least one row")
    if len(columns) < 2:
        return {str(column): 1.0 for column in columns}
    values = frame.to_numpy(dtype=float)
    factors: dict[str, float] = {}
    for position, column in enumerate(columns):
        target = values[:, position]
        others = np.delete(values, position, axis=1)
        spread = float(target.var())
        if spread == 0.0:
            factors[str(column)] = VIF_CAP
            continue
        fitted = LinearRegression().fit(others, target)
        residual = target - fitted.predict(others)
        r_squared = 1.0 - float(residual.var()) / spread
        factors[str(column)] = float(min(1.0 / max(1.0 - r_squared, 1.0 / VIF_CAP), VIF_CAP))
    return factors


def belsley_condition_number(frame: pd.DataFrame) -> float:
    """Return Belsley's kappa: the singular-value ratio of the column-standardised design.

    Each column is centred and divided by its standard deviation, the singular values of the
    result are taken, and the largest is divided by the smallest. This is the quantity the rule of
    thumb of 30 is stated for; the ratio of the correlation matrix's extreme *eigenvalues* is its
    square, and pairing that with the same threshold is how a healthy model acquires a
    collinearity finding (DECISIONS D-035).

    Args:
        frame: The design, one column per feature.

    Returns:
        The condition number, capped at :data:`VIF_CAP` when a column is constant or the design is
        exactly rank deficient.

    Raises:
        ToolError: The frame has no columns or no rows.
    """
    columns = list(frame.columns)
    if not columns:
        raise ToolError("a condition number needs at least one column")
    if len(frame.index) == 0:
        raise ToolError("a condition number needs at least one row")
    matrix = frame.to_numpy(dtype=float)
    spread = matrix.std(axis=0)
    if float(np.min(spread)) == 0.0:
        return VIF_CAP
    standardised = (matrix - matrix.mean(axis=0)) / spread
    singular = np.linalg.svd(standardised, compute_uv=False)
    smallest = float(singular.min())
    if smallest <= 0.0:  # pragma: no cover - an exactly zero singular value; floating point
        return VIF_CAP  # gives a tiny positive one even for an exactly dependent column
    return float(min(float(singular.max()) / smallest, VIF_CAP))


def cpr_from_smm(smm: float) -> float:
    """Annualise a monthly prepayment rate: ``1 - (1 - SMM) ** 12``.

    Args:
        smm: The single-month mortality, a monthly hazard in [0, 1].

    Returns:
        The conditional prepayment rate.

    Raises:
        ToolError: The monthly rate is not in [0, 1].
    """
    if not 0.0 <= smm <= 1.0:
        raise ToolError(f"a single-month mortality of {smm} is not a monthly rate in [0, 1]")
    return float(1.0 - (1.0 - smm) ** MONTHS_PER_YEAR)


def _equal_groups(size: int, groups: int) -> list[NDArray[np.intp]]:
    """Split ``0..size-1`` into as many nearly equal contiguous blocks as the sample supports."""
    return [block for block in np.array_split(np.arange(size), min(groups, size)) if block.size]


def calibration_table(y_true: Any, y_score: Any, *, bins: int = PSI_BINS) -> list[dict[str, Any]]:
    """Return the calibration table: equal-count bins of the score, ascending.

    Args:
        y_true: The outcomes, 0 or 1.
        y_score: The predicted probabilities.
        bins: How many bins; ten by convention, and the golden report's shape.

    Returns:
        One row per bin with ``bin`` (1 is the lowest predicted probability), ``mean_predicted``,
        ``observed`` and ``count``.
    """
    truth = _check_binary(_as_vector(y_true))
    scores = _check_probabilities(_as_vector(y_score))
    order = np.argsort(scores, kind="stable")
    rows = []
    for number, block in enumerate(_equal_groups(scores.size, bins), start=1):
        index = order[block]
        rows.append(
            {
                "bin": number,
                "mean_predicted": float(scores[index].mean()),
                "observed": float(truth[index].mean()),
                "count": int(index.size),
            }
        )
    return rows


def deciles_table(y_true: Any, y_score: Any, *, groups: int = PSI_BINS) -> list[dict[str, Any]]:
    """Return the decile table, the first decile holding the highest predicted probabilities.

    Args:
        y_true: The outcomes, 0 or 1.
        y_score: The predicted probabilities.
        groups: How many groups; ten by convention.

    Returns:
        One row per decile with ``decile``, ``count``, ``events``, ``event_rate`` and ``lift``,
        the lift being the decile's event rate over the whole sample's.
    """
    truth = _check_binary(_as_vector(y_true))
    scores = _check_probabilities(_as_vector(y_score))
    base = float(truth.mean())
    order = np.argsort(-scores, kind="stable")
    rows = []
    for number, block in enumerate(_equal_groups(scores.size, groups), start=1):
        index = order[block]
        rate = float(truth[index].mean())
        rows.append(
            {
                "decile": number,
                "count": int(index.size),
                "events": int(truth[index].sum()),
                "event_rate": rate,
                "lift": float(rate / base) if base > 0.0 else 0.0,
            }
        )
    return rows


def top_capture(rows: Sequence[Mapping[str, Any]], *, deciles: int = 2) -> float:
    """Return the share of all events that fall in the top deciles of the decile table.

    Args:
        rows: The rows :func:`deciles_table` returned.
        deciles: How many of the top deciles to add up.

    Returns:
        The captured share of events, in [0, 1].
    """
    total = sum(int(row["events"]) for row in rows)
    if total == 0:
        return 0.0
    captured = sum(int(row["events"]) for row in rows[:deciles])
    return float(captured / total)
