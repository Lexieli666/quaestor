"""``check_collinearity``: variance inflation factors, Belsley's condition number and the signs.

Spec section 3.7's sixth row. Both statistics are computed on the feature matrix the subject
actually fitted on -- ``data_train.csv``, which is post-screen for both shipped subjects -- because
the question ``M1`` asks is whether the *fitted* model's coefficients are identified, not whether
the developer's first draft of the feature list was.

``condition_number`` is Belsley's kappa: the ratio of the largest to the smallest singular value
of the column-standardised design. The ratio of the correlation matrix's extreme eigenvalues is
its square, and pairing that quantity with the rule of thumb of 30 stated for this one is how a
healthy model acquires a collinearity finding (DECISIONS D-035).

The **sign check** is the second half of the same question and raises nothing. A near-dependency
among the columns is what makes a fitted coefficient take a sign its own marginal relationship
with the outcome contradicts, so this tool is where the comparison belongs: for each retained
feature it stores the sign of the coefficient, the sign of that feature's own relationship with
the outcome on the fitting split -- the sign of its single-feature AUC minus a half -- and whether
the two agree. No rule fires on a disagreement, because a sign flip may be the model correctly
conditioning on the other columns; it is evidence section 2 writes about, and
``challenger_compare``'s ablation deltas are what say how much it matters (DECISIONS D-095).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..artifacts import Artifact, ArtifactKind
from ..errors import ToolError
from ..findings import DefectClass, FindingCandidate, Severity
from . import stats
from .frames import coefficients, declared_features, feature_frame, require_split, scored_frame
from .registry import Tool, ToolArgs, ToolContext, ToolResult

__all__ = ["CheckCollinearityTool", "sign_of"]


def sign_of(value: float) -> int:
    """Return ``+1``, ``-1`` or ``0``, so that a sign is an artifact a citation can address.

    Args:
        value: The quantity whose direction is wanted.

    Returns:
        The sign. Exactly zero is zero: a coefficient of zero has no direction to agree with, and
        reporting it as positive would invent one.
    """
    if value > 0.0:
        return 1
    if value < 0.0:
        return -1
    return 0


class CheckCollinearityTool(Tool["CheckCollinearityTool.Args"]):
    """Measure multicollinearity among the features the champion was fitted on."""

    name = "check_collinearity"
    description = (
        "Compute each retained feature's variance inflation factor, Belsley's condition number "
        "of the column-standardised design matrix, and whether each fitted coefficient's sign "
        "agrees with that feature's own univariate direction."
    )

    class Args(ToolArgs):
        """Arguments of ``check_collinearity``.

        Attributes:
            split: Which split's feature matrix to measure; the fitting split by default.
            features: Which features to include; ``None`` means every declared feature the
                subject's own screen left in the matrix.
        """

        split: str = "train"
        features: list[str] | None = None

    def run(self, args: CheckCollinearityTool.Args, ctx: ToolContext) -> ToolResult:
        """Compute the VIFs, the condition number and the sign check, and raise ``M1``.

        Args:
            args: Which split and features to measure.
            ctx: The run's context.

        Returns:
            One artifact per feature's VIF, the largest of them, the condition number, the sign
            check's three artifacts per feature and its disagreement count, and any ``M1``
            candidate.

        Raises:
            ToolError: The split is not declared, a named feature is not in the matrix, or the
                matrix is not numeric.
        """
        split = require_split(ctx, args.split)
        frame = feature_frame(ctx, split)
        available = declared_features(ctx, frame)
        names = list(args.features) if args.features is not None else available
        unknown = [name for name in names if name not in available]
        if unknown:
            raise ToolError(
                f"check_collinearity was asked for {unknown}, which data_{split}.csv does not "
                f"hold; it holds {available}"
            )
        matrix = frame[names].apply(pd.to_numeric, errors="coerce")
        if matrix.isna().any().any():
            columns = sorted(matrix.columns[matrix.isna().any()].tolist())
            raise ToolError(
                f"data_{split}.csv holds a non-numeric or missing value in {columns}, so no "
                "variance inflation factor can be computed; impute or drop it in the subject"
            )

        factors = stats.variance_inflation_factors(matrix)
        artifacts: list[Artifact] = [
            ctx.store.put(
                f"vif.{name}",
                value,
                ArtifactKind.scalar,
                f"variance inflation factor of {name} on {split}",
            )
            for name, value in factors.items()
        ]
        worst_name = max(factors, key=lambda name: factors[name])
        worst = factors[worst_name]
        artifacts.append(
            ctx.store.put(
                "vif.max", worst, ArtifactKind.scalar, "the largest variance inflation factor"
            )
        )
        kappa = stats.belsley_condition_number(matrix)
        artifacts.append(
            ctx.store.put(
                "condition_number",
                kappa,
                ArtifactKind.scalar,
                "Belsley's condition number of the column-standardised design (D-035)",
            )
        )

        sign_artifacts, disagreements = self._sign_check(ctx, split, names)
        artifacts += sign_artifacts

        vif_threshold = ctx.thresholds.artifact(ctx.store, "threshold.M1.vif")
        kappa_threshold = ctx.thresholds.artifact(ctx.store, "threshold.M1.condition_number")
        artifacts += [vif_threshold, kappa_threshold]
        vif_limit = ctx.thresholds["threshold.M1.vif"]
        kappa_limit = ctx.thresholds["threshold.M1.condition_number"]
        candidates: list[FindingCandidate] = []
        if worst > vif_limit or kappa > kappa_limit:
            evidence: list[str] = []
            detail: list[str] = []
            if worst > vif_limit:
                offenders = sorted(name for name, value in factors.items() if value > vif_limit)
                evidence += [
                    ctx.store.artifact("vif.max").hash,
                    *(ctx.store.artifact(f"vif.{name}").hash for name in offenders),
                    vif_threshold.hash,
                ]
                detail.append(
                    f"{len(offenders)} feature(s) exceed a VIF of {vif_limit}, the worst being "
                    f"{worst_name!r} at {worst:.4g}"
                )
            if kappa > kappa_limit:
                evidence += [ctx.store.artifact("condition_number").hash, kappa_threshold.hash]
                detail.append(
                    f"the condition number of the standardised design is {kappa:.4g}, above the "
                    f"threshold of {kappa_limit}"
                )
            candidates.append(
                FindingCandidate(
                    defect_class=DefectClass.M1,
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
                f"largest VIF {worst:.4g} on {worst_name!r} against {vif_limit}; condition number "
                f"{kappa:.4g} against {kappa_limit}; {len(disagreements)} coefficient sign(s) "
                f"disagree with the univariate direction"
                + (f": {disagreements}" if disagreements else "")
            ),
        )

    def _sign_check(
        self, ctx: ToolContext, split: str, names: list[str]
    ) -> tuple[list[Artifact], list[str]]:
        """Store, per retained feature, the coefficient's sign against its univariate direction.

        The univariate direction is the sign of the feature's own AUC against the outcome minus a
        half, computed on the same split the coefficients were fitted on. It is not the sign of a
        correlation: an AUC is what the leakage screen already uses for "does this column, on its
        own, say anything about the outcome", and the two screens disagreeing about the direction
        of the same column would be a defect of this codebase rather than of a model.

        A feature the champion's own summary carries no coefficient for -- an expanded spline
        column, a term the developer's screen removed -- is skipped: there is no fitted sign to
        compare. So is a feature whose column is constant, which has no direction at all.

        Args:
            ctx: The run's context.
            split: The fitting split.
            names: The retained features, as measured for their VIFs.

        Returns:
            The artifacts, and the names whose signs disagree, in ``names`` order.
        """
        fitted = coefficients(ctx)
        frame = scored_frame(ctx, split)
        truth = frame["y_true"].to_numpy(dtype=int)
        artifacts: list[Artifact] = []
        disagreements: list[str] = []
        checked = 0
        for name in names:
            if name not in fitted or name not in frame.columns:
                continue
            values = pd.to_numeric(frame[name], errors="coerce")
            column = values.fillna(values.median()).to_numpy(dtype=float)
            if truth.min() == truth.max() or float(np.std(column)) == 0.0:
                continue
            coef_sign = sign_of(fitted[name])
            univariate = sign_of(stats.auc(truth, column) - 0.5)
            agrees = int(coef_sign == univariate and coef_sign != 0)
            checked += 1
            if not agrees:
                disagreements.append(name)
            artifacts += [
                ctx.store.put(
                    f"sign_check.{name}.coef_sign",
                    coef_sign,
                    ArtifactKind.scalar,
                    f"the sign of the fitted coefficient on {name}",
                ),
                ctx.store.put(
                    f"sign_check.{name}.univariate_direction",
                    univariate,
                    ArtifactKind.scalar,
                    f"the sign of {name}'s own single-feature AUC on {split} minus 0.5",
                ),
                ctx.store.put(
                    f"sign_check.{name}.agrees",
                    agrees,
                    ArtifactKind.scalar,
                    f"1 when the fitted sign on {name} agrees with its univariate direction, "
                    "0 when it does not",
                ),
            ]
        artifacts.append(
            ctx.store.put(
                "sign_check.n_disagreements",
                len(disagreements),
                ArtifactKind.scalar,
                f"retained features whose fitted sign contradicts their univariate direction, "
                f"of {checked} checked",
            )
        )
        return artifacts, disagreements
