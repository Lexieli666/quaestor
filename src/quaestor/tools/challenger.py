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

The **ablation** is the same idea turned inwards and raises nothing. One refit of the champion's
own functional form -- linear in the log-odds, which is what both shipped subjects are -- per
retained feature, each without that feature, each scored on the same held-out split:
``ablation.<feature>.delta_auc`` is how much test AUC the model loses by dropping it. That is the
materiality measure section 2 needs when ``check_collinearity`` reports a coefficient whose sign
contradicts its univariate direction, because a sign flip on a column the model barely uses is not
the same statement as one on a column it depends on (DECISIONS D-095).
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from ..artifacts import Artifact, ArtifactKind
from ..errors import ToolError
from ..findings import DefectClass, FindingCandidate, Severity
from . import stats
from .frames import declared_features, feature_frame, predictions, require_split, scored_frame
from .registry import Tool, ToolArgs, ToolContext, ToolResult

__all__ = [
    "CHALLENGER_NAME",
    "MAX_ABLATION_FEATURES",
    "ChallengerCompareTool",
]

MAX_ABLATION_FEATURES: Final = 25
"""How many features the ablation will refit for; above it the whole ablation is skipped.

The cost is one refit per feature plus one baseline, and a refit of a logistic scorecard on a
twenty-thousand-row panel is a few tens of milliseconds -- ten refits on ``credit_default``, eleven
on ``msr_prepayment``. The cap exists so that a package with two hundred features cannot silently
turn one tool call into two hundred fits inside the subject's wall-clock budget. When it bites,
``ablation.skipped`` records that it did and why, because a measurement that was not made must not
look like a measurement that came back empty (D-095).
"""

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

        missing = {
            train: float(design.isna().any(axis=1).mean()),
            test: float(held_out.isna().any(axis=1).mean()),
        }
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

        if any(share > 0.0 for share in missing.values()):
            artifacts.append(
                ctx.store.put(
                    "challenger.missing_values",
                    {
                        "rows_with_a_missing_feature": missing,
                        "handling": (
                            "the boosted challenger takes missing values natively; how the "
                            "champion treated them is the subject's own choice and is not "
                            "recoverable from the contract files"
                        ),
                    },
                    ArtifactKind.json,
                    "the share of rows carrying a missing feature value in each split, and how "
                    "the challenger read them",
                )
            )

        artifacts += self._ablation(
            ctx, design, held_out, truth, test_truth, features, test, missing=missing
        )

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

    def _ablation(  # noqa: PLR0913 - the two matrices, the two outcome vectors and the names
        self,
        ctx: ToolContext,
        design: pd.DataFrame,
        held_out: pd.DataFrame,
        truth: np.typing.NDArray[Any],
        test_truth: np.typing.NDArray[Any],
        features: list[str],
        test: str,
        *,
        missing: Mapping[str, float],
    ) -> list[Artifact]:
        """Refit the champion's functional form without each feature and store the AUC it costs.

        The refit is a standardised logistic regression, which is the champion's own form on both
        shipped subjects. It is **not** the champion's own fit: the subject's coefficients were
        produced by the subject's code, which this validator never imports (spec section 3.6). So
        ``ablation.baseline_auc`` is stored beside the deltas and is the number each delta is
        measured from -- it is close to ``metrics.<test>.auc`` and is not the same number, and
        subtracting the deltas from the champion's own AUC would mix two fits.

        Args:
            ctx: The run's context.
            design: The fitting split's numeric feature matrix.
            held_out: The held-out split's numeric feature matrix.
            truth: The fitting split's outcomes.
            test_truth: The held-out split's outcomes.
            features: The feature names, in matrix order.
            test: The held-out split's name, for the captions.
            missing: The share of rows carrying a missing feature value, per split.

        Returns:
            The baseline AUC, one delta per feature, or the single ``ablation.skipped`` note.
        """
        if any(share > 0.0 for share in missing.values()):
            return [
                ctx.store.put(
                    "ablation.skipped",
                    {
                        "reason": (
                            "a feature matrix with missing values, which the standardised "
                            "logistic refit this ablation uses cannot take"
                        ),
                        "rows_with_a_missing_feature": dict(missing),
                    },
                    ArtifactKind.json,
                    "the per-feature ablation was not run: the feature matrix holds missing values",
                )
            ]
        if len(features) > MAX_ABLATION_FEATURES:
            return [
                ctx.store.put(
                    "ablation.skipped",
                    {
                        "reason": "more features than the ablation refits for",
                        "n_features": len(features),
                        "max_features": MAX_ABLATION_FEATURES,
                    },
                    ArtifactKind.json,
                    f"the per-feature ablation was not run: {len(features)} features against a "
                    f"cap of {MAX_ABLATION_FEATURES}",
                )
            ]
        baseline = self._refit_auc(design, held_out, truth, test_truth, features)
        artifacts = [
            ctx.store.put(
                "ablation.baseline_auc",
                baseline,
                ArtifactKind.scalar,
                f"AUC on {test} of a refit of the champion's functional form on every retained "
                "feature, the level each ablation delta is measured from",
            )
        ]
        for name in features:
            kept = [other for other in features if other != name]
            without = self._refit_auc(design, held_out, truth, test_truth, kept)
            artifacts.append(
                ctx.store.put(
                    f"ablation.{name}.delta_auc",
                    without - baseline,
                    ArtifactKind.scalar,
                    f"change in {test} AUC when the champion's form is refitted without {name}",
                )
            )
        return artifacts

    @staticmethod
    def _refit_auc(
        design: pd.DataFrame,
        held_out: pd.DataFrame,
        truth: np.typing.NDArray[Any],
        test_truth: np.typing.NDArray[Any],
        features: list[str],
    ) -> float:
        """Fit a standardised logistic regression on the columns and score the held-out split."""
        model = Pipeline(
            [("scale", StandardScaler()), ("fit", LogisticRegression(max_iter=1000))]
        ).fit(design[features], truth)
        return stats.auc(test_truth, model.predict_proba(held_out[features])[:, 1])

    @staticmethod
    def _numeric(frame: pd.DataFrame, features: list[str], split: str) -> pd.DataFrame:
        """Return the feature matrix as numbers, keeping a genuinely missing cell missing.

        A column that does not parse as a number and a column with a hole in it are two different
        facts, and coercion turns both into ``NaN``. They are told apart by comparing the mask
        before and after: a cell that was a value and is now ``NaN`` was not a number, which no
        model here can take; a cell that was already empty is missing data, which is exactly what
        the ``D1`` screen exists to report and which the boosted challenger reads natively
        (DECISIONS D-125).
        """
        raw = frame[features]
        matrix: pd.DataFrame = raw.apply(pd.to_numeric, errors="coerce")
        unparsed = matrix.isna() & ~raw.isna()
        if bool(unparsed.any().any()):
            columns = sorted(matrix.columns[unparsed.any()].tolist())
            raise ToolError(
                f"data_{split}.csv holds a non-numeric value in {columns}, so the challenger "
                "cannot be fitted on the champion's own matrix"
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
