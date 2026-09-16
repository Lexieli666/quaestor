"""``check_stability``: how the model behaves across regimes and over time, and the ``R1`` rule.

Spec section 3.7's fifth row. Two questions, one of which needs a fit of its own.

*Does the champion discriminate equally well in each regime?* is answered from the champion's own
scores: the rows of the analysed split are grouped by the regime column and the AUC of the stored
predictions is computed within each group. Nothing is refitted, so this is a statement about the
model that was shipped.

*Does a feature mean the same thing in each regime?* cannot be answered from the champion at all,
because the champion is one fit and has one coefficient per feature. So a plain unpenalised
logistic regression is fitted **within each regime** on the standardised retained features -- at
``C = np.inf`` and a stopping tolerance of 1e-10, because a diagnostic that compares coefficients
across regimes must not be reading a penalty or an unfinished descent (DECISIONS D-163) -- and it
is those coefficients that are compared. The feature ranking is taken from the same fits -- the
ten largest mean absolute coefficients across the regimes -- rather than from the champion's, whose
design may expand a feature into a spline basis under names no regime fit shares (DECISIONS
D-053).

A sign flip is read through **two** gates, because a coefficient that disagrees with itself across
regimes has to be both large enough to matter and precise enough to be a coefficient at all:
``threshold.R1.sign_flip_coef`` is the materiality gate on ``|coef|`` and
``threshold.R1.sign_flip_z`` is the precision gate on ``|coef / s.e.|``, and both must hold in
every regime. The standard errors come from each regime fit's own observed information
(:func:`~quaestor.tools.stats.logistic_standard_errors`) and are stored beside the coefficients,
so a reader can see how far from zero a flipping coefficient actually was (DECISIONS D-164). A
feature that is constant inside a regime -- the case of a package whose regime column is one of
its own features -- is not estimated there at all, so its standard error and its ``z`` are empty
cells and it cannot clear the precision gate.

``stability.psi_over_time`` is reported and never a candidate: the score distribution of a later
period differs from the fitting window's by the same construction that keeps ``S1`` on
train-against-test (DECISIONS D-046).
"""

from __future__ import annotations

from typing import Any, Final, NamedTuple

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from ..artifacts import Artifact, ArtifactKind
from ..errors import ToolError
from ..findings import DefectClass, FindingCandidate, Severity
from . import stats
from .frames import declared_features, require_split, scored_frame
from .registry import Tool, ToolArgs, ToolContext, ToolResult

__all__ = ["CheckStabilityTool", "RegimeFit"]

TOP_FEATURES: Final = 10
"""How many features the sign-flip rule looks at, as spec section 3.7 states it."""


class RegimeFit(NamedTuple):
    """One feature's coefficient in one regime, with the precision of that estimate.

    A feature that does not vary inside a regime -- which is what every feature that is *also* the
    regime column is -- has no coefficient there to estimate and no standard error either, so both
    it and :attr:`z` are ``None`` and the table's cells are empty. The alternative was a large
    finite stand-in on the pattern of :data:`~quaestor.tools.stats.VIF_CAP`, which would print a
    precision for a parameter the regime's data never identified (DECISIONS D-164).

    Attributes:
        coefficient: The standardised coefficient of the regime's own unpenalised fit.
        standard_error: Its standard error, from that fit's observed information matrix, or
            ``None`` when the feature is constant within the regime.
    """

    coefficient: float
    standard_error: float | None

    @property
    def z(self) -> float | None:
        """The coefficient in units of its own standard error, which is ``R1``'s precision gate."""
        if self.standard_error is None:
            return None
        return self.coefficient / self.standard_error


_MAX_ITERATIONS: Final = 1000
"""Iterations for the per-regime fits; the same cap both shipped subjects use for the champion."""

_TOLERANCE: Final = 1e-10
"""Where the per-regime fits stop, which is where ``stats.calibration_slope_intercept`` stops."""


class CheckStabilityTool(Tool["CheckStabilityTool.Args"]):
    """Compare discrimination and feature behaviour across the declared regimes."""

    name = "check_stability"
    description = (
        "Split the fitting data by the package's regime column and compare the champion's AUC "
        "and each feature's coefficient across regimes; report the score's PSI over time."
    )

    class Args(ToolArgs):
        """Arguments of ``check_stability``.

        Attributes:
            regime_column: Which column defines the regimes; ``None`` takes ``regime.column`` from
                ``package.yaml``.
            split: Which split to compare within; the fitting split by default, because that is
                where a coefficient's meaning is decided.
        """

        regime_column: str | None = None
        split: str = "train"

    def run(self, args: CheckStabilityTool.Args, ctx: ToolContext) -> ToolResult:
        """Compare the regimes and raise ``R1`` on a sign flip or an AUC gap.

        Args:
            args: Which regime column and split to use.
            ctx: The run's context.

        Returns:
            The per-regime coefficient tables, the AUC table, the score's PSI over time and any
            ``R1`` candidate.

        Raises:
            ToolError: The package declares no regime column and none was given, the column is not
                in the data, or it takes fewer than two values in the analysed split.
        """
        column = args.regime_column or ctx.package.spec.regime.column
        if column is None:
            raise ToolError(
                f"package {ctx.package.name!r} declares no regime.column and check_stability was "
                "given none, so there is nothing to compare across; the report lists this in "
                "Appendix D as not checked"
            )
        split = require_split(ctx, args.split)
        frame = scored_frame(ctx, split)
        if column not in frame.columns:
            raise ToolError(
                f"the regime column {column!r} is not in data_{split}.csv, which holds "
                f"{list(frame.columns)}; the subject must write it beside the features"
            )
        regimes = [str(value) for value in sorted(frame[column].astype(str).unique())]
        if len(regimes) < 2:
            raise ToolError(
                f"the regime column {column!r} takes only the value {regimes} in {split!r}, so "
                "there are no two regimes to compare"
            )
        features = declared_features(ctx, frame)

        artifacts: list[Artifact] = []
        auc_rows, auc_by_regime = self._auc_by_regime(frame, column, regimes)
        artifacts.append(
            ctx.store.put(
                "stability.auc_by_regime",
                auc_rows,
                ArtifactKind.table,
                f"the champion's AUC within each {column} on {split}",
            )
        )
        coefficients = self._regime_coefficients(ctx, frame, column, regimes, features)
        flips, coefficient_artifacts = self._store_coefficients(
            ctx, regimes, features, coefficients
        )
        artifacts += coefficient_artifacts
        artifacts += self._psi_over_time(ctx, split)

        # All three thresholds are stored whether or not the rule fires, so that a report saying
        # the coefficients held their signs can cite what "held" meant -- both halves of it.
        coefficient_threshold = ctx.thresholds.artifact(ctx.store, "threshold.R1.sign_flip_coef")
        z_threshold = ctx.thresholds.artifact(ctx.store, "threshold.R1.sign_flip_z")
        auc_threshold = ctx.thresholds.artifact(ctx.store, "threshold.R1.auc_gap")
        artifacts += [coefficient_threshold, z_threshold, auc_threshold]

        candidates: list[FindingCandidate] = []
        spread = max(auc_by_regime.values()) - min(auc_by_regime.values())
        auc_limit = ctx.thresholds["threshold.R1.auc_gap"]
        coefficient_limit = ctx.thresholds["threshold.R1.sign_flip_coef"]
        z_limit = ctx.thresholds["threshold.R1.sign_flip_z"]
        if flips or spread > auc_limit:
            evidence: list[str] = []
            detail: list[str] = []
            if flips:
                evidence += (
                    [coefficient_threshold.hash, z_threshold.hash]
                    + [ctx.store.artifact(f"stability.{name}.sign_flip").hash for name in flips]
                    + [
                        ctx.store.artifact(f"stability.{name}.coef_or_importance_by_regime").hash
                        for name in flips
                    ]
                )
                detail.append(
                    f"{sorted(flips)} change sign across {column} with a coefficient above "
                    f"{coefficient_limit} and a |z| of at least {z_limit} in every regime"
                )
            if spread > auc_limit:
                evidence += [
                    ctx.store.artifact("stability.auc_by_regime").hash,
                    auc_threshold.hash,
                ]
                detail.append(
                    f"the champion's AUC differs by {spread:.4f} across {column} (from "
                    f"{min(auc_by_regime.values()):.4f} to {max(auc_by_regime.values()):.4f}), "
                    f"against a threshold of {auc_limit}"
                )
            candidates.append(
                FindingCandidate(
                    defect_class=DefectClass.R1,
                    evidence=sorted(set(evidence)),
                    detail="; ".join(detail),
                    suggested_severity=Severity.medium,
                    tool=self.name,
                )
            )

        return ToolResult(
            tool=self.name,
            artifacts=artifacts,
            candidates=candidates,
            summary=(
                f"{len(regimes)} regimes of {column} on {split}: AUC "
                + ", ".join(f"{name} {auc_by_regime[name]:.4f}" for name in regimes)
                + f"; {len(flips)} sign flip(s) among the top {TOP_FEATURES} features"
            ),
        )

    @staticmethod
    def _auc_by_regime(
        frame: pd.DataFrame, column: str, regimes: list[str]
    ) -> tuple[list[dict[str, Any]], dict[str, float]]:
        """Return the AUC of the champion's own scores within each regime."""
        rows: list[dict[str, Any]] = []
        values: dict[str, float] = {}
        for regime in regimes:
            part = frame[frame[column].astype(str) == regime]
            truth = part["y_true"].to_numpy(dtype=int)
            if truth.min() == truth.max():
                raise ToolError(
                    f"regime {regime!r} holds one outcome only over {truth.size} rows, so the "
                    "champion's discrimination in it cannot be measured"
                )
            area = stats.auc(truth, part["y_score"].to_numpy(dtype=float))
            values[regime] = area
            rows.append(
                {
                    "regime": regime,
                    "n": int(len(part)),
                    "event_rate": float(truth.mean()),
                    "auc": area,
                }
            )
        return rows, values

    @staticmethod
    def _regime_coefficients(
        ctx: ToolContext,
        frame: pd.DataFrame,
        column: str,
        regimes: list[str],
        features: list[str],
    ) -> dict[str, dict[str, RegimeFit]]:
        """Fit one unpenalised logistic regression per regime and return coefficients and errors.

        The fit is ``C = np.inf`` at ``tol = 1e-10`` so that it is the maximum likelihood estimate
        this docstring has always claimed and is converged to the same place as
        :func:`~quaestor.tools.stats.calibration_slope_intercept`'s own Newton iteration, whose
        tolerance that is; scikit-learn's defaults are a penalty and a stopping rule that leaves
        the optimum by more than the quantity compared here (DECISIONS D-163).

        Each coefficient comes back with the standard error of that same converged fit, taken from
        its observed information ``(X'WX)^-1`` on the standardised design with the intercept column
        the fit used. ``R1``'s precision gate reads them, and a regime whose information matrix is
        singular is refused here rather than given a standard error of convenience (D-164).

        Raises:
            ToolError: A regime holds a non-numeric or missing feature value, or its fit's
                information matrix is singular.
        """
        coefficients: dict[str, dict[str, RegimeFit]] = {}
        for regime in regimes:
            part = frame[frame[column].astype(str) == regime]
            matrix = part[features].apply(pd.to_numeric, errors="coerce")
            if matrix.isna().any().any():
                raise ToolError(
                    f"data of regime {regime!r} holds a non-numeric or missing feature value, so "
                    "no per-regime coefficient can be fitted"
                )
            values = matrix.to_numpy(dtype=float)
            spread = values.std(axis=0)
            standardised = (values - values.mean(axis=0)) / np.where(spread == 0.0, 1.0, spread)
            fitted = LogisticRegression(C=np.inf, max_iter=_MAX_ITERATIONS, tol=_TOLERANCE).fit(
                standardised, part["y_true"].to_numpy(dtype=int)
            )
            identified = [position for position, width in enumerate(spread) if width != 0.0]
            design = np.column_stack([np.ones(len(standardised)), standardised[:, identified]])
            try:
                errors = stats.logistic_standard_errors(
                    design, fitted.predict_proba(standardised)[:, 1]
                )
            except ToolError as exc:
                raise ToolError(
                    f"the per-regime fit of regime {regime!r} has a singular information matrix "
                    f"over {len(part)} rows of features that do vary, so its coefficients have no "
                    f"standard error and R1's precision gate cannot be applied to them: "
                    f"{exc.message}"
                ) from exc
            by_position = dict(zip(identified, errors[1:], strict=True))
            coefficients[regime] = {
                name: RegimeFit(
                    float(value),
                    None if position not in by_position else float(by_position[position]),
                )
                for position, (name, value) in enumerate(
                    zip(features, fitted.coef_[0], strict=True)
                )
            }
        return coefficients

    def _store_coefficients(
        self,
        ctx: ToolContext,
        regimes: list[str],
        features: list[str],
        coefficients: dict[str, dict[str, RegimeFit]],
    ) -> tuple[list[str], list[Artifact]]:
        """Store each feature's coefficients by regime and its sign flip, and return the flips.

        A feature flips when it is among the top :data:`TOP_FEATURES` by mean absolute
        coefficient, its coefficients have opposite signs across the regimes, and in **every**
        regime the coefficient clears both gates: ``|coef|`` above
        ``threshold.R1.sign_flip_coef``, which asks whether the disagreement is large enough to
        matter, and ``|coef / s.e.|`` at least ``threshold.R1.sign_flip_z``, which asks whether
        either coefficient can be told from zero at all. They are different questions and both are
        kept: a precisely estimated 0.001 is not a regime effect, and neither is a 0.09 with a
        standard error of 0.29 (DECISIONS D-164).
        """
        limit = ctx.thresholds["threshold.R1.sign_flip_coef"]
        z_limit = ctx.thresholds["threshold.R1.sign_flip_z"]
        magnitude = {
            name: float(
                np.mean([abs(coefficients[regime][name].coefficient) for regime in regimes])
            )
            for name in features
        }
        top = sorted(features, key=lambda name: -magnitude[name])[:TOP_FEATURES]
        artifacts: list[Artifact] = []
        flips: list[str] = []
        for name in features:
            fits = [coefficients[regime][name] for regime in regimes]
            values = [fit.coefficient for fit in fits]
            flipped = (
                name in top
                and min(values) < 0.0 < max(values)
                and all(abs(fit.coefficient) > limit for fit in fits)
                and all(fit.z is not None and abs(fit.z) >= z_limit for fit in fits)
            )
            if flipped:
                flips.append(name)
            artifacts += [
                ctx.store.put(
                    f"stability.{name}.coef_or_importance_by_regime",
                    [
                        {
                            "regime": regime,
                            "coefficient": coefficients[regime][name].coefficient,
                            "se": coefficients[regime][name].standard_error,
                            "z": coefficients[regime][name].z,
                        }
                        for regime in regimes
                    ],
                    ArtifactKind.table,
                    (
                        f"{name}'s coefficient in a per-regime refit, standardised, with the "
                        "standard error and z of each"
                    ),
                ),
                ctx.store.put(
                    f"stability.{name}.sign_flip",
                    int(flipped),
                    ArtifactKind.scalar,
                    (
                        f"1 when {name} is among the top {TOP_FEATURES} features and changes sign "
                        f"across regimes with a coefficient above {limit} and a |z| of at least "
                        f"{z_limit} in each"
                    ),
                ),
            ]
        return flips, artifacts

    def _psi_over_time(self, ctx: ToolContext, split: str) -> list[Artifact]:
        """Store the score's PSI in each calendar bucket against the analysed split's own scores.

        Every declared split is pooled, so the table shows what a monitoring pack would show: how
        far the score distribution of each period has moved from the window the model was fitted
        in. A hazard subject's period column supplies the buckets; a subject with no time column
        has no such table, and the summary says so rather than an empty artifact implying a check
        that ran.
        """
        time_column = ctx.package.spec.data.time_column
        if time_column is None:
            return []
        reference = scored_frame(ctx, split)
        if time_column not in reference.columns:  # pragma: no cover - the contract check rejects
            return []  # a hazard panel with no period column before any tool sees it
        pooled = pd.concat(
            [scored_frame(ctx, name) for name in ctx.splits], ignore_index=True, sort=False
        )
        periods = pd.to_numeric(pooled[time_column], errors="coerce")
        if periods.isna().any():
            return []
        buckets = (periods // 100).astype(int)
        rows: list[dict[str, Any]] = []
        for bucket in sorted(buckets.unique()):
            part = pooled[buckets == bucket]
            rows.append(
                {
                    "bucket": int(bucket),
                    "n": int(len(part)),
                    "psi": stats.psi(reference["y_score"], part["y_score"]),
                }
            )
        return [
            ctx.store.put(
                "stability.psi_over_time",
                rows,
                ArtifactKind.table,
                f"PSI of the score in each calendar year against {split}; reported, not tested",
            )
        ]
