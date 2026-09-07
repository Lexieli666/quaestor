"""``challenger_compare``: effective challenge, and the ``E1`` rule.

Spec section 3.7's seventh row. A gradient-boosted tree is fitted on exactly the columns the
champion was fitted on -- ``data_train.csv`` as the subject wrote it -- and scored on
``data_test.csv``. If it beats the champion by more than the effective-challenge threshold, that
is an ``E1``: not a defect, but a statement about the champion's functional form that SR 11-7's
effective-challenge expectation asks a validator to make, which is why its suggested severity is
``low``.

The challenger is deliberately the crudest possible one: a ``HistGradientBoostingClassifier`` at
its defaults with a fixed seed. A tuned challenger would make the comparison a statement about how
hard the validator tried, and the study's numbers would then depend on tuning effort rather than
on the champion.
"""

from __future__ import annotations

from typing import Final

import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier

from ..artifacts import Artifact, ArtifactKind
from ..errors import ToolError
from ..findings import DefectClass, FindingCandidate, Severity
from . import stats
from .frames import declared_features, feature_frame, predictions, require_split, scored_frame
from .registry import Tool, ToolArgs, ToolContext, ToolResult

__all__ = ["CHALLENGER_NAME", "ChallengerCompareTool"]

CHALLENGER_NAME: Final = "hist_gradient_boosting"
"""What the challenger is, recorded as an artifact so the report never has to name it in prose."""

DEFAULT_SEED: Final = 20260901
"""The seed both subjects declare, so a challenger comparison is reproducible from the package."""


class ChallengerCompareTool(Tool["ChallengerCompareTool.Args"]):
    """Fit a boosted-tree challenger on the champion's own features and compare."""

    name = "challenger_compare"
    description = (
        "Fit a histogram gradient-boosting challenger on the same feature matrix the champion "
        "used and compare its test AUC and Brier score with the champion's."
    )

    class Args(ToolArgs):
        """Arguments of ``challenger_compare``.

        Attributes:
            train_split: Which split to fit the challenger on.
            test_split: Which split to compare on.
            seed: The challenger's random state.
        """

        train_split: str = "train"
        test_split: str = "test"
        seed: int = DEFAULT_SEED

    def run(self, args: ChallengerCompareTool.Args, ctx: ToolContext) -> ToolResult:
        """Fit the challenger, compare it with the champion and raise ``E1`` on a material lead.

        Args:
            args: Which splits to use and with which seed.
            ctx: The run's context.

        Returns:
            The challenger's name, AUC, Brier score and AUC lead, and any ``E1`` candidate.

        Raises:
            ToolError: A named split is not declared, the feature matrix is not numeric, or a
                split holds one outcome only.
        """
        train = require_split(ctx, args.train_split)
        test = require_split(ctx, args.test_split)
        train_frame = scored_frame(ctx, train)
        test_frame = scored_frame(ctx, test)
        features = [
            name
            for name in declared_features(ctx, train_frame)
            if name in feature_frame(ctx, test).columns
        ]
        design = self._numeric(train_frame, features, train)
        held_out = self._numeric(test_frame, features, test)
        truth = train_frame["y_true"].to_numpy(dtype=int)
        if truth.min() == truth.max():
            raise ToolError(
                f"split {train!r} holds one outcome only, so no challenger can be fitted on it"
            )

        challenger = HistGradientBoostingClassifier(random_state=args.seed).fit(design, truth)
        scores = challenger.predict_proba(held_out)[:, 1]
        test_truth = test_frame["y_true"].to_numpy(dtype=int)
        challenger_auc = stats.auc(test_truth, scores)
        challenger_brier = stats.brier(test_truth, scores)
        champion_auc = self._champion_auc(ctx, test)
        delta = challenger_auc - champion_auc

        artifacts: list[Artifact] = [
            ctx.store.put(
                "challenger.name",
                CHALLENGER_NAME,
                ArtifactKind.json,
                "the challenger model, at its library defaults",
            ),
            ctx.store.put(
                "challenger.auc",
                challenger_auc,
                ArtifactKind.scalar,
                f"the challenger's AUC on {test}",
            ),
            ctx.store.put(
                "challenger.brier",
                challenger_brier,
                ArtifactKind.scalar,
                f"the challenger's Brier score on {test}",
            ),
            ctx.store.put(
                "challenger.delta_auc",
                delta,
                ArtifactKind.scalar,
                f"the challenger's AUC on {test} minus the champion's",
            ),
        ]

        threshold = ctx.thresholds.artifact(ctx.store, "threshold.E1.delta_auc")
        artifacts.append(threshold)
        limit = ctx.thresholds["threshold.E1.delta_auc"]
        candidates: list[FindingCandidate] = []
        if delta > limit:
            evidence = [
                ctx.store.artifact("challenger.delta_auc").hash,
                ctx.store.artifact("challenger.auc").hash,
                threshold.hash,
            ]
            if f"metrics.{test}.auc" in ctx.store:
                evidence.append(ctx.store.artifact(f"metrics.{test}.auc").hash)
            candidates.append(
                FindingCandidate(
                    defect_class=DefectClass.E1,
                    evidence=sorted(set(evidence)),
                    detail=(
                        f"a {CHALLENGER_NAME} challenger reaches an AUC of {challenger_auc:.4f} "
                        f"on {test} against the champion's {champion_auc:.4f}, a lead of "
                        f"{delta:.4f} against an effective-challenge threshold of {limit}"
                    ),
                    suggested_severity=Severity.low,
                    tool=self.name,
                )
            )

        return ToolResult(
            tool=self.name,
            artifacts=artifacts,
            candidates=candidates,
            summary=(
                f"challenger AUC {challenger_auc:.4f} against the champion's "
                f"{champion_auc:.4f} on {test}, a lead of {delta:+.4f} against {limit}"
            ),
        )

    @staticmethod
    def _numeric(frame: pd.DataFrame, features: list[str], split: str) -> pd.DataFrame:
        """Return the feature matrix as numbers, naming the offending column if it is not."""
        matrix: pd.DataFrame = frame[features].apply(pd.to_numeric, errors="coerce")
        if matrix.isna().any().any():
            columns = sorted(matrix.columns[matrix.isna().any()].tolist())
            raise ToolError(
                f"data_{split}.csv holds a non-numeric or missing value in {columns}, so the "
                "challenger cannot be fitted on the champion's own matrix"
            )
        return matrix

    @staticmethod
    def _champion_auc(ctx: ToolContext, split: str) -> float:
        """Return the champion's AUC on a split, from the store when ``compute_metrics`` has run.

        Reading the stored value rather than recomputing keeps one number in one place: the report
        cites ``metrics.<split>.auc`` beside ``challenger.delta_auc``, and two independent
        computations of "the champion's AUC" that agreed to fifteen digits would still be two.
        """
        logical = f"metrics.{split}.auc"
        if logical in ctx.store:
            return ctx.store.value(logical)
        frame = predictions(ctx, split)
        return stats.auc(frame["y_true"], frame["y_score"])
