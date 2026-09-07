"""``check_collinearity``: variance inflation factors and Belsley's condition number.

Spec section 3.7's sixth row. Both statistics are computed on the feature matrix the subject
actually fitted on -- ``data_train.csv``, which is post-screen for both shipped subjects -- because
the question ``M1`` asks is whether the *fitted* model's coefficients are identified, not whether
the developer's first draft of the feature list was.

``condition_number`` is Belsley's kappa: the ratio of the largest to the smallest singular value
of the column-standardised design. The ratio of the correlation matrix's extreme eigenvalues is
its square, and pairing that quantity with the rule of thumb of 30 stated for this one is how a
healthy model acquires a collinearity finding (DECISIONS D-035).
"""

from __future__ import annotations

import pandas as pd

from ..artifacts import Artifact, ArtifactKind
from ..errors import ToolError
from ..findings import DefectClass, FindingCandidate, Severity
from . import stats
from .frames import declared_features, feature_frame, require_split
from .registry import Tool, ToolArgs, ToolContext, ToolResult

__all__ = ["CheckCollinearityTool"]


class CheckCollinearityTool(Tool["CheckCollinearityTool.Args"]):
    """Measure multicollinearity among the features the champion was fitted on."""

    name = "check_collinearity"
    description = (
        "Compute each retained feature's variance inflation factor and Belsley's condition "
        "number of the column-standardised design matrix."
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
        """Compute the VIFs and the condition number, and raise ``M1`` where either breaches.

        Args:
            args: Which split and features to measure.
            ctx: The run's context.

        Returns:
            One artifact per feature's VIF, the largest of them, the condition number, and any
            ``M1`` candidate.

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
                f"{kappa:.4g} against {kappa_limit}"
            ),
        )
