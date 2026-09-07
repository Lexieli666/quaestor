"""``profile_data``: schema, missingness, describe, PSI and CSI, and the ``D1`` and ``S1`` rules.

Spec section 3.7's second row. Two comparisons are computed and they are not treated alike.

**Missingness** is compared between the training split and every other declared split, because a
feature that is present in development and absent in production is a defect whatever the split was
drawn on. **PSI** is compared between train and *test* for the purpose of raising ``S1``, and
between train and every other split for the purpose of reporting: an ``out_of_time`` split is
defined as a later period and a ``vintage_holdout`` as a different origination cohort, so a
quantile-binned index between train and either of them measures the split design and not drift,
and would fire on every hazard package anybody ever writes (DECISIONS D-046). Those comparisons
are stored under ``psi.<split>.<feature>`` and are never candidates; the train-to-test comparison
keeps the bare ``psi.<feature>`` name the golden report cites.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from ..artifacts import Artifact, ArtifactKind
from ..errors import ToolError
from ..findings import DefectClass, FindingCandidate, Severity
from . import stats
from .frames import coefficients, declared_features, feature_frame, predictions, require_split
from .registry import Tool, ToolArgs, ToolContext, ToolResult

__all__ = ["ProfileDataTool"]

_DESCRIBE_COLUMNS = ("feature", "count", "mean", "std", "min", "p25", "p50", "p75", "max")
"""``profile.<split>.describe``'s columns; the percentiles are named so a citation reaches them."""

PSI_REFERENCE = "train"
"""The split every distribution is compared against: the one the champion was fitted on."""

PSI_COMPARISON = "test"
"""The one comparison ``S1`` and the package's ``psi`` threshold are read on (DECISIONS D-046)."""


class ProfileDataTool(Tool["ProfileDataTool.Args"]):
    """Profile each split and compare its distributions with the training split's."""

    name = "profile_data"
    description = (
        "Profile each declared split -- schema, missingness, descriptive statistics -- and "
        "compare every feature and the score with the training split by PSI and CSI."
    )

    class Args(ToolArgs):
        """Arguments of ``profile_data``.

        Attributes:
            splits: Which splits to profile; ``None`` means every split the package declares.
            features: Which features to compare; ``None`` means every declared feature the
                subject's own screen left in ``data_<split>.csv``.
        """

        splits: list[str] | None = None
        features: list[str] | None = None

    def run(self, args: ProfileDataTool.Args, ctx: ToolContext) -> ToolResult:
        """Profile the splits, compute PSI and CSI, and raise ``D1`` and ``S1`` where they apply.

        Args:
            args: Which splits and features to look at.
            ctx: The run's context.

        Returns:
            The profile, drift and stability artifacts, and any ``D1`` or ``S1`` candidates.

        Raises:
            ToolError: A named split or feature is not one this run has, or the training split was
                excluded, which leaves nothing to compare against.
        """
        splits = self._splits(args, ctx)
        frames = {split: feature_frame(ctx, split) for split in splits}
        features = self._features(args, ctx, frames)

        artifacts: list[Artifact] = []
        for split in splits:
            artifacts += self._profile(ctx, split, frames[split], features)

        candidates: list[FindingCandidate] = []
        missing_artifacts, missing_candidates = self._missingness(ctx, splits, frames, features)
        artifacts += missing_artifacts
        candidates += missing_candidates

        drift_artifacts, drift_candidates, worst = self._drift(ctx, splits, frames, features)
        artifacts += drift_artifacts
        candidates += drift_candidates

        return ToolResult(
            tool=self.name,
            artifacts=artifacts,
            candidates=candidates,
            summary=(
                f"profiled {len(splits)} split(s) over {len(features)} feature(s); the largest "
                f"train-to-test PSI is {worst[1]:.4f} on {worst[0]!r} against a threshold of "
                f"{ctx.thresholds['threshold.S1.psi']}"
            ),
        )

    def _splits(self, args: ProfileDataTool.Args, ctx: ToolContext) -> list[str]:
        """Resolve the requested splits, insisting the reference split is among them."""
        splits = list(args.splits) if args.splits is not None else list(ctx.splits)
        for split in splits:
            require_split(ctx, split)
        if PSI_REFERENCE not in splits:
            raise ToolError(
                f"profile_data was asked for {splits}, which does not include {PSI_REFERENCE!r}; "
                "every stability index is stated against the split the champion was fitted on"
            )
        return splits

    def _features(
        self,
        args: ProfileDataTool.Args,
        ctx: ToolContext,
        frames: dict[str, pd.DataFrame],
    ) -> list[str]:
        """Resolve the requested features to those every requested split actually carries."""
        available = declared_features(ctx, frames[PSI_REFERENCE])
        if args.features is None:
            return [
                name
                for name in available
                if all(name in frame.columns for frame in frames.values())
            ]
        unknown = [name for name in args.features if name not in available]
        if unknown:
            raise ToolError(
                f"profile_data was asked for the features {unknown}, which are not in "
                f"data_{PSI_REFERENCE}.csv; it holds {available}"
            )
        return list(args.features)

    def _profile(
        self, ctx: ToolContext, split: str, frame: pd.DataFrame, features: list[str]
    ) -> list[Artifact]:
        """Store the schema, missingness and descriptive statistics of one split."""
        store = ctx.store
        schema_rows = [
            {
                "feature": name,
                "dtype": str(frame[name].dtype),
                "n": int(len(frame)),
                "n_unique": int(frame[name].nunique(dropna=True)),
            }
            for name in features
        ]
        fractions = {name: float(frame[name].isna().mean()) for name in features}
        missing_rows: list[dict[str, Any]] = [
            {
                "feature": name,
                "n_missing": int(frame[name].isna().sum()),
                "missing_fraction": fractions[name],
            }
            for name in features
        ]
        worst_missing = max(fractions.values())
        return [
            store.put(
                f"profile.{split}.n", int(len(frame)), ArtifactKind.scalar, f"rows in {split}"
            ),
            store.put(
                f"profile.{split}.schema",
                schema_rows,
                ArtifactKind.table,
                f"the columns of data_{split}.csv the model used",
            ),
            store.put(
                f"profile.{split}.missing",
                missing_rows,
                ArtifactKind.table,
                f"missingness per feature in {split}",
            ),
            store.put(
                f"profile.{split}.missing.max",
                worst_missing,
                ArtifactKind.scalar,
                f"the largest missing fraction in {split}",
            ),
            store.put(
                f"profile.{split}.describe",
                self._describe(frame, features),
                ArtifactKind.table,
                f"descriptive statistics of {split}",
            ),
        ]

    @staticmethod
    def _describe(frame: pd.DataFrame, features: list[str]) -> list[dict[str, Any]]:
        """Return the descriptive-statistics table, one row per feature."""
        rows: list[dict[str, Any]] = []
        for name in features:
            values = pd.to_numeric(frame[name], errors="coerce").dropna().to_numpy(dtype=float)
            if values.size == 0:
                rows.append(dict.fromkeys(_DESCRIBE_COLUMNS, 0.0) | {"feature": name, "count": 0})
                continue
            quartiles = np.quantile(values, [0.25, 0.5, 0.75])
            rows.append(
                {
                    "feature": name,
                    "count": int(values.size),
                    "mean": float(values.mean()),
                    "std": float(values.std(ddof=1)) if values.size > 1 else 0.0,
                    "min": float(values.min()),
                    "p25": float(quartiles[0]),
                    "p50": float(quartiles[1]),
                    "p75": float(quartiles[2]),
                    "max": float(values.max()),
                }
            )
        return rows

    def _missingness(
        self,
        ctx: ToolContext,
        splits: list[str],
        frames: dict[str, pd.DataFrame],
        features: list[str],
    ) -> tuple[list[Artifact], list[FindingCandidate]]:
        """Compare each split's missingness with the reference split's and raise ``D1``."""
        threshold = ctx.thresholds.artifact(ctx.store, "threshold.D1.missing_gap")
        limit = ctx.thresholds["threshold.D1.missing_gap"]
        offenders: list[tuple[str, str, float]] = []
        for split in splits:
            if split == PSI_REFERENCE:
                continue
            for name in features:
                gap = abs(
                    float(frames[split][name].isna().mean())
                    - float(frames[PSI_REFERENCE][name].isna().mean())
                )
                if gap > limit:
                    offenders.append((split, name, gap))
        if not offenders:
            return [threshold], []
        evidence = [threshold.hash] + [
            ctx.store.artifact(f"profile.{split}.missing").hash
            for split in {PSI_REFERENCE, *(split for split, _, _ in offenders)}
        ]
        worst = max(offenders, key=lambda item: item[2])
        return [threshold], [
            FindingCandidate(
                defect_class=DefectClass.D1,
                evidence=sorted(set(evidence)),
                detail=(
                    f"missingness differs between {PSI_REFERENCE} and {worst[0]} by "
                    f"{worst[2]:.4f} on {worst[1]!r}, against a limit of {limit}; "
                    f"{len(offenders)} feature-split pair(s) exceed it"
                ),
                suggested_severity=Severity.medium,
                tool=self.name,
            )
        ]

    def _drift(
        self,
        ctx: ToolContext,
        splits: list[str],
        frames: dict[str, pd.DataFrame],
        features: list[str],
    ) -> tuple[list[Artifact], list[FindingCandidate], tuple[str, float]]:
        """Compute PSI and CSI against the reference split, and raise ``S1`` on train vs test."""
        store = ctx.store
        reference = frames[PSI_REFERENCE]
        coefs = self._coefficients(ctx)
        artifacts: list[Artifact] = []
        tested: dict[str, float] = {}
        worst = ("", 0.0)

        for split in splits:
            if split == PSI_REFERENCE:
                continue
            bare = split == PSI_COMPARISON
            for name in features:
                value = stats.psi(reference[name].dropna(), frames[split][name].dropna())
                logical = f"psi.{name}" if bare else f"psi.{split}.{name}"
                artifacts.append(
                    store.put(
                        logical,
                        value,
                        ArtifactKind.scalar,
                        f"PSI of {name} between {PSI_REFERENCE} and {split}",
                    )
                )
                if bare:
                    tested[name] = value
                    if value > worst[1]:
                        worst = (name, value)
            score_psi = stats.psi(
                predictions(ctx, PSI_REFERENCE)["y_score"], predictions(ctx, split)["y_score"]
            )
            artifacts.append(
                store.put(
                    "psi.y_score" if bare else f"psi.{split}.y_score",
                    score_psi,
                    ArtifactKind.scalar,
                    f"PSI of the score between {PSI_REFERENCE} and {split}",
                )
            )
            if bare:
                tested["y_score"] = score_psi
                if score_psi > worst[1]:
                    worst = ("y_score", score_psi)

        if PSI_COMPARISON in splits:
            artifacts.append(
                store.put(
                    "psi.max",
                    float(max(tested.values())),
                    ArtifactKind.scalar,
                    f"the largest {PSI_REFERENCE}-to-{PSI_COMPARISON} PSI, score included",
                )
            )
            artifacts += self._csi(ctx, reference, frames[PSI_COMPARISON], features, coefs)

        threshold = ctx.thresholds.artifact(store, "threshold.S1.psi")
        artifacts.append(threshold)
        limit = ctx.thresholds["threshold.S1.psi"]
        breaches = {name: value for name, value in tested.items() if value > limit}
        if not breaches:
            return artifacts, [], worst
        evidence = [threshold.hash] + [
            store.artifact("psi.y_score" if name == "y_score" else f"psi.{name}").hash
            for name in sorted(breaches)
        ]
        return (
            artifacts,
            [
                FindingCandidate(
                    defect_class=DefectClass.S1,
                    evidence=evidence,
                    detail=(
                        f"the population stability index between {PSI_REFERENCE} and "
                        f"{PSI_COMPARISON} is {worst[1]:.4f} on {worst[0]!r} against a threshold "
                        f"of {limit}; {len(breaches)} of {len(tested)} comparisons breach it"
                    ),
                    suggested_severity=Severity.medium,
                    tool=self.name,
                )
            ],
            worst,
        )

    @staticmethod
    def _coefficients(ctx: ToolContext) -> dict[str, float]:
        """Return the champion's coefficients, or nothing when the summary cannot be read.

        CSI weights a feature's redistribution by what it contributes to the linear predictor, so
        it needs the fitted coefficients. A subject whose ``model_summary.json`` is unreadable is
        already a contract failure the sandbox has raised; a subject whose design expands a
        feature simply has no coefficient under that feature's own name, and its CSI is reported
        as zero rather than the tool refusing to profile anything.
        """
        try:
            return coefficients(ctx)
        except ToolError:  # pragma: no cover - the sandbox rejects such a run before this
            return {}

    def _csi(
        self,
        ctx: ToolContext,
        reference: pd.DataFrame,
        actual: pd.DataFrame,
        features: list[str],
        coefs: dict[str, float],
    ) -> list[Artifact]:
        """Store each feature's characteristic stability index, and the largest of them."""
        artifacts: list[Artifact] = []
        values: dict[str, float] = {}
        for name in features:
            value = stats.csi(reference[name].dropna(), actual[name].dropna(), coefs.get(name, 0.0))
            values[name] = value
            artifacts.append(
                ctx.store.put(
                    f"csi.{name}",
                    value,
                    ArtifactKind.scalar,
                    f"CSI of {name}: its contribution to the shift in the linear predictor",
                )
            )
        artifacts.append(
            ctx.store.put(
                "csi.max",
                float(max(values.values())) if values else 0.0,
                ArtifactKind.scalar,
                "the largest characteristic stability index",
            )
        )
        return artifacts
