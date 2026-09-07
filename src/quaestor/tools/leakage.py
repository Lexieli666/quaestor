"""``check_leakage``: timing, single-feature power, split contamination and a name screen.

Spec section 3.7's fourth row. Four screens, of which only the first reads a declaration and the
other three read the data:

* **timing** counts the features ``package.yaml`` declares ``during_period`` or ``after_outcome``.
  Both are reported; only ``after_outcome`` raises ``L1``, since a value observed inside the
  outcome window may still be legitimate and a value observed after it cannot be.
* **target correlation** scores each feature on its own. The statistic is the AUC of the single
  feature against the outcome, oriented so that a feature which predicts the outcome *downwards*
  scores as high as one that predicts it upwards -- a leak does not become less of a leak for
  carrying a minus sign.
* **overlap** hashes each row's feature values and asks what share of the test split's hashes are
  also in the training split's. Hashing the values rather than the identifier is deliberate: the
  contamination recipe of the study duplicates rows, and a duplicate arrives with an identifier of
  its own.
* **name screen** matches each feature name against a small lexicon of target-adjacent words and
  against the package's own declared target column, which is the one word that is certainly wrong
  to have inside a feature name.
"""

from __future__ import annotations

import hashlib
from typing import Any, Final

import numpy as np
import pandas as pd

from ..artifacts import Artifact, ArtifactKind
from ..errors import ToolError
from ..findings import DefectClass, FindingCandidate, Severity
from ..package import FeatureTiming
from . import stats
from .frames import declared_features, feature_frame, require_split, scored_frame
from .registry import Tool, ToolArgs, ToolContext, ToolResult

__all__ = ["NAME_LEXICON", "CheckLeakageTool", "row_hashes"]

NAME_LEXICON: Final = (
    "target",
    "label",
    "outcome",
    "response",
    "y_true",
    "actual",
    "realised",
    "realized",
    "observed",
    "future",
    "next_",
    "subsequent",
    "post_",
    "after",
    "chargeoff",
    "charge_off",
    "writeoff",
    "write_off",
    "payoff",
    "paid_off",
    "prepaid",
    "prepay",
    "resolution",
    "ever_",
)
"""Words a feature name should not contain, because each names the thing being predicted.

Deliberately short and deliberately specific. A lexicon that matched ``pay``, ``bill`` or
``delinq`` would flag half of a perfectly ordinary credit-card feature set, and a screen whose
false-alarm rate is that high is one a validator learns to ignore. The package's own declared
target column is added to this list at run time, which is the match that matters most.
"""

_FLAGGED_TIMINGS: Final = (FeatureTiming.during_period, FeatureTiming.after_outcome)
"""What the timing screen reports; ``L1`` fires on the second of them only."""


def row_hashes(frame: pd.DataFrame, columns: list[str]) -> list[str]:
    """Return one hash per row of the named columns, rendered canonically.

    Args:
        frame: The rows to hash.
        columns: Which columns make up a row's identity; sorted before rendering so that two
            frames whose columns are in different orders still agree.

    Returns:
        One hex digest per row, in the frame's row order.
    """
    ordered = sorted(columns)
    values = frame[ordered].to_numpy(dtype=object)
    return [
        hashlib.sha256("|".join(str(cell) for cell in row).encode("utf-8")).hexdigest()
        for row in values
    ]


class CheckLeakageTool(Tool["CheckLeakageTool.Args"]):
    """Screen the features and the splits for leakage and contamination."""

    name = "check_leakage"
    description = (
        "Screen for leakage: declared feature timings, each feature's own AUC against the "
        "outcome, the share of test rows that also appear in train, and target-adjacent feature "
        "names."
    )

    class Args(ToolArgs):
        """Arguments of ``check_leakage``.

        Attributes:
            train_split: The split the single-feature screen is run on and overlap is measured
                against.
            test_split: The split whose rows are looked for in the training split.
        """

        train_split: str = "train"
        test_split: str = "test"

    def run(self, args: CheckLeakageTool.Args, ctx: ToolContext) -> ToolResult:
        """Run the four screens and raise ``L1`` and ``L2`` where they apply.

        Args:
            args: Which splits to compare.
            ctx: The run's context.

        Returns:
            The four screens' artifacts and any candidates.

        Raises:
            ToolError: A named split is not declared, or the training split holds one outcome only.
        """
        train = require_split(ctx, args.train_split)
        test = require_split(ctx, args.test_split)
        artifacts: list[Artifact] = []
        candidates: list[FindingCandidate] = []

        timing_artifacts, offenders = self._timing(ctx)
        artifacts += timing_artifacts

        strongest, target_artifacts = self._target_power(ctx, train)
        artifacts += target_artifacts

        overlap, overlap_artifact = self._overlap(ctx, train, test)
        artifacts.append(overlap_artifact)

        matched, name_artifacts = self._name_screen(ctx)
        artifacts += name_artifacts

        # Both thresholds are stored whether or not they are breached: the report says what the
        # screen would have fired on, and a number in prose has to have an artifact behind it.
        single_feature = ctx.thresholds.artifact(ctx.store, "threshold.L1.single_feature_auc")
        overlap_threshold = ctx.thresholds.artifact(ctx.store, "threshold.L2.overlap")
        artifacts += [single_feature, overlap_threshold]

        limit = ctx.thresholds["threshold.L1.single_feature_auc"]
        if offenders or strongest[1] > limit:
            evidence = [
                ctx.store.artifact("leakage.timing").hash,
                ctx.store.artifact("leakage.timing.n_flagged").hash,
            ]
            detail = []
            if offenders:
                detail.append(
                    f"package.yaml declares {offenders} with timing after_outcome, so their "
                    "values are not known when the model scores"
                )
            if strongest[1] > limit:
                evidence += [
                    ctx.store.artifact("leakage.target_corr.max_single_feature_auc").hash,
                    ctx.store.artifact("leakage.target_corr").hash,
                    single_feature.hash,
                ]
                detail.append(
                    f"{strongest[0]!r} scores an AUC of {strongest[1]:.4f} on its own against a "
                    f"leakage threshold of {limit}"
                )
            candidates.append(
                FindingCandidate(
                    defect_class=DefectClass.L1,
                    evidence=sorted(set(evidence)),
                    detail="; ".join(detail),
                    suggested_severity=Severity.high,
                    tool=self.name,
                )
            )

        overlap_limit = ctx.thresholds["threshold.L2.overlap"]
        if overlap > overlap_limit:
            candidates.append(
                FindingCandidate(
                    defect_class=DefectClass.L2,
                    evidence=[overlap_artifact.hash, overlap_threshold.hash],
                    detail=(
                        f"{overlap:.4%} of the rows of {test!r} also appear in {train!r}, against "
                        f"a contamination threshold of {overlap_limit:.2%}; the held-out split is "
                        "not held out"
                    ),
                    suggested_severity=Severity.high,
                    tool=self.name,
                )
            )

        return ToolResult(
            tool=self.name,
            artifacts=artifacts,
            candidates=candidates,
            summary=(
                f"{len(offenders)} feature(s) declared after_outcome; strongest single feature "
                f"{strongest[0]!r} at AUC {strongest[1]:.4f}; overlap {overlap:.4%}; "
                f"{len(matched)} name(s) matched the lexicon"
            ),
        )

    def _timing(self, ctx: ToolContext) -> tuple[list[Artifact], list[str]]:
        """Store the declared timings and return the ``after_outcome`` offenders."""
        rows: list[dict[str, Any]] = [
            {
                "feature": feature.name,
                "timing": feature.timing.value,
                "flagged": feature.timing in _FLAGGED_TIMINGS,
            }
            for feature in ctx.package.spec.features
        ]
        flagged = [row for row in rows if row["flagged"]]
        artifacts = [
            ctx.store.put(
                "leakage.timing",
                rows,
                ArtifactKind.table,
                "each feature's declared timing; flagged means during or after the outcome",
            ),
            ctx.store.put(
                "leakage.timing.n_flagged",
                len(flagged),
                ArtifactKind.scalar,
                "features declared during_period or after_outcome",
            ),
        ]
        offenders = [
            feature.name
            for feature in ctx.package.spec.features_with_timing(FeatureTiming.after_outcome)
        ]
        return artifacts, offenders

    def _target_power(
        self, ctx: ToolContext, split: str
    ) -> tuple[tuple[str, float], list[Artifact]]:
        """Score every feature on its own against the outcome and store the table."""
        frame = scored_frame(ctx, split)
        features = declared_features(ctx, frame)
        truth = frame["y_true"].to_numpy(dtype=int)
        if truth.min() == truth.max():
            raise ToolError(
                f"split {split!r} of package {ctx.package.name!r} holds one outcome only, so no "
                "feature can be scored against it"
            )
        rows: list[dict[str, Any]] = []
        for name in features:
            values = pd.to_numeric(frame[name], errors="coerce")
            if values.isna().all():
                rows.append(
                    {"feature": name, "abs_corr": 0.0, "single_feature_auc": 0.5, "numeric": False}
                )
                continue
            filled = values.fillna(values.median()).to_numpy(dtype=float)
            if float(np.std(filled)) == 0.0:
                rows.append(
                    {"feature": name, "abs_corr": 0.0, "single_feature_auc": 0.5, "numeric": True}
                )
                continue
            area = stats.auc(truth, filled)
            rows.append(
                {
                    "feature": name,
                    "abs_corr": float(abs(np.corrcoef(filled, truth)[0, 1])),
                    "single_feature_auc": float(max(area, 1.0 - area)),
                    "numeric": True,
                }
            )
        strongest = max(rows, key=lambda row: float(row["single_feature_auc"]))
        artifacts = [
            ctx.store.put(
                "leakage.target_corr",
                rows,
                ArtifactKind.table,
                f"each feature against the outcome on {split}, on its own",
            ),
            ctx.store.put(
                "leakage.target_corr.max_single_feature_auc",
                float(strongest["single_feature_auc"]),
                ArtifactKind.scalar,
                "the AUC of the strongest single feature",
            ),
        ]
        return (str(strongest["feature"]), float(strongest["single_feature_auc"])), artifacts

    def _overlap(self, ctx: ToolContext, train: str, test: str) -> tuple[float, Artifact]:
        """Store the share of test rows whose feature values also appear in train."""
        train_frame = feature_frame(ctx, train)
        test_frame = feature_frame(ctx, test)
        columns = [
            name for name in declared_features(ctx, test_frame) if name in train_frame.columns
        ]
        seen = set(row_hashes(train_frame, columns))
        digests = row_hashes(test_frame, columns)
        share = float(sum(digest in seen for digest in digests) / len(digests))
        return share, ctx.store.put(
            "leakage.overlap",
            share,
            ArtifactKind.scalar,
            f"share of {test} rows whose feature values also appear in {train}",
        )

    def _name_screen(self, ctx: ToolContext) -> tuple[list[str], list[Artifact]]:
        """Store which feature names match the target-adjacent lexicon."""
        target = ctx.package.spec.data.target.lower()
        terms = (*NAME_LEXICON, target)
        rows: list[dict[str, Any]] = []
        matched: list[str] = []
        for feature in ctx.package.spec.features:
            hits = sorted({term for term in terms if term in feature.name.lower()})
            rows.append(
                {"feature": feature.name, "matched": ";".join(hits), "n_matched": len(hits)}
            )
            if hits:
                matched.append(feature.name)
        return matched, [
            ctx.store.put(
                "leakage.name_screen",
                rows,
                ArtifactKind.table,
                "feature names against the target-adjacent lexicon and the declared target",
            ),
            ctx.store.put(
                "leakage.name_screen.n_matched",
                len(matched),
                ArtifactKind.scalar,
                "feature names matching the target-adjacent lexicon",
            ),
        ]
