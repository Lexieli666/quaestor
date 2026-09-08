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
* **overlap** is two quantities and a baseline, because on discrete data the feature-vector
  screen alone is a false-alarm generator. ``leakage.overlap.ids`` is the share of test rows whose
  *identifier* -- the declared id column, and the period as well for a hazard panel -- also
  appears in train: two splits that share a row identity is contamination on its face.
  ``leakage.overlap.features`` is the share of test rows whose *feature vector* appears in train,
  which catches the study's contamination recipe when it re-keys what it copies but which also
  fires on any panel whose features have small discrete support. So it is read against
  ``leakage.duplicates.train``, the share of train rows whose feature vector is not unique inside
  train: that is what coincidence looks like in this dataset, measured on the split that cannot be
  contaminated by itself (DECISIONS D-086).
* **name screen** matches each feature name against a small lexicon of target-adjacent words and
  against the package's own declared target column, which is the one word that is certainly wrong
  to have inside a feature name.
"""

from __future__ import annotations

import hashlib
from collections import Counter
from collections.abc import Sequence
from typing import Any, Final, NamedTuple

import numpy as np
import pandas as pd

from ..artifacts import Artifact, ArtifactKind
from ..errors import ToolError
from ..findings import DefectClass, FindingCandidate, Severity
from ..package import FeatureTiming
from . import stats
from .frames import (
    declared_features,
    feature_frame,
    key_columns,
    require_split,
    scored_frame,
)
from .registry import Tool, ToolArgs, ToolContext, ToolResult
from .thresholds import effective_name

__all__ = [
    "DUPLICATE_MULTIPLE",
    "FEATURE_OVERLAP_BOUND",
    "NAME_LEXICON",
    "OVERLAP_THRESHOLD",
    "CheckLeakageTool",
    "Overlaps",
    "duplicate_share",
    "row_hashes",
]

OVERLAP_THRESHOLD: Final = "threshold.L2.overlap"
"""The declared contamination bound, which both arms of ``L2`` are read against."""

FEATURE_OVERLAP_BOUND: Final = effective_name(OVERLAP_THRESHOLD, "features")
"""``threshold.L2.overlap.features_effective``: the bound the feature-vector arm actually applied.

D-086 derives it -- ``max(threshold.L2.overlap, 2 x leakage.duplicates.train)`` -- so on any real
panel it is a different number from the declared 0.5%, and on the third live run the drafter,
having only the declared one, compared 1.256% with 0.5%, called the result an exceedance and said
it was "recorded as a finding" while section 6 correctly said no finding was raised. The bound the
rule applied is now an artifact like any other, so the sentence a reader is owed can be written
with a citation behind it (DECISIONS D-091).
"""

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

_OVERLAP_FIX: Final = (
    "check that both splits write the package's declared id_column, which spec 3.3 requires of "
    "every data_<split>.csv"
)
"""What to do about two splits with no identifier column in common."""

DUPLICATE_MULTIPLE: Final = 2.0
"""How far above the within-train duplicate share the test-in-train share must sit to be a defect.

The feature-vector overlap of two splits drawn from one discrete population is not zero and is not
a defect: it is the chance that two different clients wrote the same row. The rate at which that
happens in *this* dataset is measured on the training split alone, where a repeat cannot be
contamination, and the screen fires when the cross-split rate is more than twice it. The factor is
a factor and not a test: it is deliberately blunt, because the quantity it guards is a false-alarm
rate rather than a p-value, and a doubling is far outside what re-drawing the split moves. On the
first live credit run the cross-split share was 1.2556% (``leakage.overlap``, committed under
``eval/results/first-live/credit-attempt1/artifacts/``) against a within-train share of 1.1619%
recomputed from that run's own ``data_train.csv``, which is not committed (D-087) -- a ratio of
1.08 where this constant asks for more than 2, and the false alarm it exists to refuse (D-086).
"""


class Overlaps(NamedTuple):
    """What the contamination screen measured, and the artifacts it stored for each part.

    Attributes:
        ids: The share of test rows whose identifier also appears in train.
        features: The share of test rows whose feature vector also appears in train.
        duplicates: The share of train rows whose feature vector is not unique within train.
        artifacts: The five artifacts -- the alias, the two overlaps, the duplicate share and
            the derived bound the feature arm applied.
    """

    ids: float
    features: float
    duplicates: float
    artifacts: list[Artifact]


def duplicate_share(digests: Sequence[str]) -> float:
    """Return the share of rows whose hash occurs more than once in the same split.

    This is the leave-one-out chance that a row of this split is matched by another row of it,
    which is the baseline the cross-split share is read against: a row's own presence is excluded
    by asking whether the hash occurs *more than once*, so a split of entirely unique rows scores
    zero rather than one.

    Args:
        digests: One hash per row.

    Returns:
        The share, in ``[0, 1]``; zero for an empty split.
    """
    if not digests:
        return 0.0
    counts = Counter(digests)
    return float(sum(count for count in counts.values() if count > 1) / len(digests))


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
        "outcome, the share of test rows that also appear in train by identifier and by feature "
        "vector, the within-train duplicate share those are read against, and target-adjacent "
        "feature names."
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

        overlaps = self._overlap(ctx, train, test)
        artifacts += overlaps.artifacts

        matched, name_artifacts = self._name_screen(ctx)
        artifacts += name_artifacts

        # Both thresholds are stored whether or not they are breached: the report says what the
        # screen would have fired on, and a number in prose has to have an artifact behind it.
        single_feature = ctx.thresholds.artifact(ctx.store, "threshold.L1.single_feature_auc")
        overlap_threshold = ctx.thresholds.artifact(ctx.store, OVERLAP_THRESHOLD)
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

        candidate = self._contamination(ctx, overlaps, train, test, overlap_threshold)
        if candidate is not None:
            candidates.append(candidate)

        return ToolResult(
            tool=self.name,
            artifacts=artifacts,
            candidates=candidates,
            summary=(
                f"{len(offenders)} feature(s) declared after_outcome; strongest single feature "
                f"{strongest[0]!r} at AUC {strongest[1]:.4f}; identifier overlap "
                f"{overlaps.ids:.4%}; feature overlap {overlaps.features:.4%} against a "
                f"within-train duplicate share of {overlaps.duplicates:.4%}; {len(matched)} "
                "name(s) matched the lexicon"
            ),
        )

    def _contamination(
        self,
        ctx: ToolContext,
        overlaps: Overlaps,
        train: str,
        test: str,
        threshold: Artifact,
    ) -> FindingCandidate | None:
        """Return the ``L2`` candidate the two overlaps justify, or ``None``.

        Two rules, in severity order (DECISIONS D-086):

        * a shared **identifier** is contamination on its face -- the same row is in both splits
          under the same name -- so an identifier overlap above ``threshold.L2.overlap`` is a
          candidate at severity **high**;
        * a shared **feature vector** with distinct identifiers may be contamination whose keys
          were rewritten, or it may be two different subjects with the same values, so it is a
          candidate at severity **medium** and only when the cross-split share exceeds both
          ``threshold.L2.overlap`` and :data:`DUPLICATE_MULTIPLE` times the share of train rows
          that repeat a feature vector inside train. That derived number is stored as
          :data:`FEATURE_OVERLAP_BOUND` and read back from the store here, so the bound the rule
          applied and the bound a report may cite are one artifact (D-091).

        Neither rule firing is not silence: all three quantities are stored and the report writes
        them, which is what "the values are reported" means.

        Args:
            ctx: The run's context, for the artifacts the evidence names.
            overlaps: What the screen measured.
            train: The training split's name.
            test: The held-out split's name.
            threshold: The stored ``threshold.L2.overlap`` artifact.

        Returns:
            The candidate, or ``None`` when neither rule fires.
        """
        limit = ctx.thresholds[OVERLAP_THRESHOLD]
        bound = ctx.store.artifact(FEATURE_OVERLAP_BOUND)
        baseline = ctx.store.value(FEATURE_OVERLAP_BOUND)
        ids_artifact = ctx.store.artifact("leakage.overlap.ids")
        features_artifact = ctx.store.artifact("leakage.overlap.features")
        duplicates_artifact = ctx.store.artifact("leakage.duplicates.train")
        if overlaps.ids > limit:
            evidence = [ids_artifact.hash, threshold.hash]
            detail = (
                f"{overlaps.ids:.4%} of the rows of {test!r} carry an identifier that also "
                f"identifies a row of {train!r}, against a contamination threshold of "
                f"{limit:.2%}; the held-out split is not held out"
            )
            if overlaps.features > baseline:
                evidence += [features_artifact.hash, duplicates_artifact.hash, bound.hash]
                detail += (
                    f", and {overlaps.features:.4%} of them repeat a feature vector of {train!r} "
                    f"against a within-train duplicate share of {overlaps.duplicates:.4%}"
                )
            return FindingCandidate(
                defect_class=DefectClass.L2,
                evidence=sorted(set(evidence)),
                detail=detail,
                suggested_severity=Severity.high,
                tool=self.name,
            )
        if overlaps.features > baseline:
            return FindingCandidate(
                defect_class=DefectClass.L2,
                evidence=sorted(
                    {
                        features_artifact.hash,
                        duplicates_artifact.hash,
                        threshold.hash,
                        bound.hash,
                    }
                ),
                detail=(
                    f"{overlaps.features:.4%} of the rows of {test!r} repeat a feature vector of "
                    f"{train!r} while carrying identifiers of their own, against "
                    f"{baseline:.4%} -- the larger of the {limit:.2%} contamination threshold "
                    f"and twice the {overlaps.duplicates:.4%} of {train!r} rows that repeat a "
                    f"feature vector inside {train!r}; the copy may have been re-keyed"
                ),
                suggested_severity=Severity.medium,
                tool=self.name,
            )
        return None

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

    def _overlap(self, ctx: ToolContext, train: str, test: str) -> Overlaps:
        """Store both contamination overlaps and the within-train duplicate share.

        Args:
            ctx: The run's context.
            train: The split the test rows are looked for in.
            test: The split whose rows are looked up.

        Returns:
            The three shares and the five artifacts they are stored as. ``leakage.overlap`` is
            kept as an alias of ``leakage.overlap.features``, because it is the name the Phase 1
            golden report cites and a logical name that stops resolving is a citation that
            dangles (D-086).
        """
        train_frame = feature_frame(ctx, train)
        test_frame = feature_frame(ctx, test)
        columns = [
            name for name in declared_features(ctx, test_frame) if name in train_frame.columns
        ]
        train_digests = row_hashes(train_frame, columns)
        test_digests = row_hashes(test_frame, columns)
        seen = set(train_digests)
        features = float(sum(digest in seen for digest in test_digests) / len(test_digests))
        duplicates = duplicate_share(train_digests)

        keys = [
            name for name in key_columns(ctx, test_frame) if name in key_columns(ctx, train_frame)
        ]
        if not keys:
            raise ToolError(
                f"data_{train}.csv and data_{test}.csv of package {ctx.package.name!r} share no "
                "identifier column, so no row of one can be recognised in the other",
                fix=_OVERLAP_FIX,
            )
        train_keys = set(row_hashes(train_frame, keys))
        test_keys = row_hashes(test_frame, keys)
        ids = float(sum(digest in train_keys for digest in test_keys) / len(test_keys))

        artifacts = [
            ctx.store.put(
                "leakage.overlap.ids",
                ids,
                ArtifactKind.scalar,
                f"share of {test} rows whose {keys} also identify a row of {train}",
            ),
            ctx.store.put(
                "leakage.overlap.features",
                features,
                ArtifactKind.scalar,
                f"share of {test} rows whose feature values also appear in {train}",
            ),
            ctx.store.put(
                "leakage.overlap",
                features,
                ArtifactKind.scalar,
                f"share of {test} rows whose feature values also appear in {train}",
            ),
            ctx.store.put(
                "leakage.duplicates.train",
                duplicates,
                ArtifactKind.scalar,
                f"share of {train} rows whose feature values are not unique within {train}",
            ),
            ctx.store.put(
                FEATURE_OVERLAP_BOUND,
                max(ctx.thresholds[OVERLAP_THRESHOLD], DUPLICATE_MULTIPLE * duplicates),
                ArtifactKind.scalar,
                (
                    f"L2: the bound the feature-overlap rule applied, the larger of "
                    f"{OVERLAP_THRESHOLD} and {DUPLICATE_MULTIPLE:g} x leakage.duplicates.train"
                ),
            ),
        ]
        return Overlaps(ids=ids, features=features, duplicates=duplicates, artifacts=artifacts)

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
