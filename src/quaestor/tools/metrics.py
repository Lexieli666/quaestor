"""``compute_metrics``: Quaestor's own metrics, calibration, deciles, CPR, and ``T1``/``C1``/``O1``.

Spec section 3.7's third row. The developer's ``metrics.json`` is stored by the sandbox and never
used here: every number in this module is recomputed from ``predictions_<split>.csv``, which is
the point of the exercise -- a validation that quoted the developer's own metrics back at them
would have checked the arithmetic of the report and nothing else.

Three rules live here.

``T1`` reads every threshold ``package.yaml`` declares, resolves it to the artifact that answers it
and compares. A rule this tool cannot resolve -- a metric no artifact holds -- is reported in the
summary as not evaluated rather than passed, because a declaration nobody checked must not read as
a declaration that held.

``C1`` is the calibration rule, and it is applied to **every** split computed, not to ``test``
alone. The scoping argument that keeps ``S1`` on train-against-test (DECISIONS D-046) does not
transfer: a population's composition in a later period differs by construction, but whether the
model's probabilities still mean what they say in that period is exactly the question an
outcomes analysis asks.

``O1`` keeps both of the rules spec section 3.7 states: a train-to-test AUC gap, and a period split
whose AUC falls below the test split's. The first is read as train minus test, a generalisation
gap, which is the reading the golden report's prose and the threshold's own name carry
(DECISIONS D-050).
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any, Final

import numpy as np
import pandas as pd
from pydantic import field_validator

from ..artifacts import Artifact, ArtifactKind
from ..errors import ToolError
from ..findings import DefectClass, FindingCandidate, Severity
from ..package import ThresholdSpec
from . import stats
from .frames import feature_frame, predictions, require_split, scored_frame
from .registry import Tool, ToolArgs, ToolContext, ToolResult
from .thresholds import SLICE_GAP_BOUND, SLICE_SHARE_FLOOR, package_threshold_names

__all__ = [
    "THRESHOLD_TABLE",
    "ComputeMetricsTool",
    "Subpopulation",
    "metric_artifact_name",
    "sub_metrics_table_name",
    "subpopulation_expression",
]

THRESHOLD_TABLE: Final = "thresholds.evaluation"
"""The table artifact that answers "did the model clear what the developer declared?" in one place.

One row per bound ``package.yaml`` states, with the metric, the split it is stated on, the bound,
the recomputed value and ``pass`` / ``fail`` / ``not evaluated``. It exists because on the third
live run section 4 was asked to *assemble* that table from the loose ``threshold.package.*``
scalars it had been shown, and assembled it wrongly: it wrote that PSI was "not recomputed in the
artifacts available to this section" while sections 1 and 3 both cited ``psi.max``, and it printed
the subject's wall-clock cap as a performance threshold. A table the tool computes and the drafter
only points at cannot disagree with the rest of the report, which is D-013's argument applied to
the one table a validation report is most often read for (DECISIONS D-092).
"""


def sub_metrics_table_name(split: str, slug: str) -> str:
    """Return the name of the table holding one sub-population's metrics on one split.

    Args:
        split: The split the slice was taken of.
        slug: The slice's own name segment, from :attr:`Subpopulation.slug`.

    Returns:
        ``metrics.<split>.sub.<slug>``, the stem the slice's scalars already share.
    """
    return f"metrics.{split}.sub.{slug}"


SCALAR_METRICS: Final = (
    "n",
    "event_rate",
    "auc",
    "gini",
    "ks",
    "brier",
    "logloss",
    "mean_predicted",
)
"""The scalar metrics stored under ``metrics.<split>.<metric>`` for every split."""

_SPLIT_METRIC_NAMES: Final = {
    "auc": "metrics.{split}.auc",
    "gini": "metrics.{split}.gini",
    "ks": "metrics.{split}.ks",
    "brier": "metrics.{split}.brier",
    "logloss": "metrics.{split}.logloss",
    "event_rate": "metrics.{split}.event_rate",
    "mean_predicted": "metrics.{split}.mean_predicted",
    "n": "metrics.{split}.n",
    "calibration_slope": "calibration_slope.{split}",
    "calibration_intercept": "calibration_intercept.{split}",
    "cpr_mae": "cpr.{split}.mae",
}
"""Which artifact answers a developer threshold stated on a split."""

_GLOBAL_METRIC_NAMES: Final = {
    "psi": "psi.max",
    "csi": "csi.max",
    "vif": "vif.max",
    "condition_number": "condition_number",
}
"""Which artifact answers a developer threshold stated over every feature."""

_RULE_RE: Final = re.compile(r"^(below_median|above_median|equals:.+)$")
"""The sub-population rules the planner may ask for."""

_SLUG_RE: Final = re.compile(r"[^A-Za-z0-9_+-]+")
"""Everything a logical-name segment cannot hold, replaced by an underscore in a slug."""


def metric_artifact_name(metric: str, split: str | None) -> str | None:
    """Return the logical name that answers a declared threshold, or ``None`` if none does.

    Args:
        metric: The metric named in ``package.yaml``.
        split: The split it is stated on, or ``None`` for a rule over every feature.

    Returns:
        The artifact's logical name, or ``None`` when no artifact this pipeline computes answers
        the rule.
    """
    if metric in _GLOBAL_METRIC_NAMES:
        return _GLOBAL_METRIC_NAMES[metric]
    template = _SPLIT_METRIC_NAMES.get(metric)
    if template is None or split is None:
        return None
    return template.format(split=split)


def subpopulation_expression(column: str, rule: str) -> str:
    """Return the slice rule as an expression over the column, for prose to quote in code.

    Args:
        column: The column sliced on.
        rule: ``below_median``, ``above_median`` or ``equals:<value>``.

    Returns:
        ``delinq_last == 0``, ``limit_bal < median(limit_bal)``, ``utilisation >=
        median(utilisation)``.

    The drafter is asked to write this inside backticks, which the tokenizer masks as inline code.
    On the fifth live run two follow-up paragraphs opened "**delinq_last equals 0.**" and
    "**delinq_last equals 1.**", and the 0 and the 1 -- the parameters of a slice rule, not
    quantities anything computed -- were counted as claims, flagged as unsupported and removed in
    a repair round (DECISIONS D-112).
    """
    if rule == "below_median":
        return f"{column} < median({column})"
    if rule == "above_median":
        return f"{column} >= median({column})"
    return f"{column} == {rule.split(':', 1)[1]}"


class Subpopulation(ToolArgs):
    """A slice of one split, for the follow-up metrics the bounded loop asks for.

    Attributes:
        column: The column to slice on. It must be in ``data_<split>.csv``, which holds the
            features the model actually used plus the identifier and the target.
        rule: ``below_median``, ``above_median`` or ``equals:<value>``.
    """

    column: str
    rule: str

    @field_validator("rule")
    @classmethod
    def _known_rule(cls, value: str) -> str:
        """Reject a rule that is not one of the three the tool implements."""
        if not _RULE_RE.match(value):
            raise ValueError(
                f"{value!r} is not a sub-population rule; use below_median, above_median or "
                "equals:<value>"
            )
        return value

    @property
    def slug(self) -> str:
        """The name segment this slice's artifacts are stored under.

        ``below_median`` on ``limit_bal`` is ``limit_bal_low`` and ``above_median`` is
        ``limit_bal_high``, which is what the golden report cites; an equality is
        ``<column>_eq_<value>`` with everything a logical name cannot hold replaced.
        """
        if self.rule == "below_median":
            return f"{self.column}_low"
        if self.rule == "above_median":
            return f"{self.column}_high"
        value = _SLUG_RE.sub("_", self.rule.split(":", 1)[1]).strip("_")
        return f"{self.column}_eq_{value}"


class ComputeMetricsTool(Tool["ComputeMetricsTool.Args"]):
    """Recompute discrimination, calibration and separation, and check the declared thresholds."""

    name = "compute_metrics"
    description = (
        "Recompute AUC, Gini, KS, Brier, log loss, calibration and decile separation from the "
        "subject's predictions for each split -- and, for a hazard subject, monthly CPR -- then "
        "check every threshold package.yaml declares."
    )

    class Args(ToolArgs):
        """Arguments of ``compute_metrics``.

        Attributes:
            splits: Which splits to compute; ``None`` means every split the package declares.
            subpopulation: A slice of each split to compute the scalar metrics on as well, for
                the bounded follow-up loop's "how does it do on the low-limit half" question.
        """

        splits: list[str] | None = None
        subpopulation: Subpopulation | None = None

    def run(self, args: ComputeMetricsTool.Args, ctx: ToolContext) -> ToolResult:
        """Recompute every metric and raise ``T1``, ``C1`` and ``O1`` where they apply.

        Args:
            args: Which splits, and which sub-population if any.
            ctx: The run's context.

        Returns:
            The metric, calibration, decile and CPR artifacts, and any candidates.

        Raises:
            ToolError: A named split is not declared, or a split holds one class only, so no
                discrimination or calibration statistic exists for it.
        """
        splits = [require_split(ctx, split) for split in (args.splits or ctx.splits)]
        artifacts: list[Artifact] = [
            ctx.thresholds.artifact(ctx.store, "rule.calibration_first_event_rate")
        ]
        computed: dict[str, dict[str, float]] = {}
        for split in splits:
            values, split_artifacts = self._one_split(ctx, split)
            computed[split] = values
            artifacts += split_artifacts
        if args.subpopulation is not None:
            artifacts += self._subpopulation(ctx, splits, args.subpopulation)

        candidates: list[FindingCandidate] = []
        threshold_artifacts, threshold_candidates, unevaluated = self._thresholds(ctx)
        artifacts += threshold_artifacts
        candidates += threshold_candidates

        calibration_artifacts, calibration_candidates = self._calibration_rule(ctx, computed)
        artifacts += calibration_artifacts
        candidates += calibration_candidates

        degradation_artifacts, degradation_candidates = self._degradation(ctx, computed)
        artifacts += degradation_artifacts
        candidates += degradation_candidates

        pending = f"; not evaluated: {unevaluated}" if unevaluated else ""
        headline = ", ".join(
            f"{split} AUC {computed[split]['auc']:.4f}"
            for split in splits
            if "auc" in computed[split]
        )
        return ToolResult(
            tool=self.name,
            artifacts=artifacts,
            candidates=candidates,
            summary=f"{headline}{pending}",
        )

    def _one_split(self, ctx: ToolContext, split: str) -> tuple[dict[str, float], list[Artifact]]:
        """Compute and store every metric of one split."""
        frame = predictions(ctx, split)
        truth = frame["y_true"].to_numpy(dtype=int)
        scores = frame["y_score"].to_numpy(dtype=float)
        if truth.min() == truth.max():
            raise ToolError(
                f"split {split!r} of package {ctx.package.name!r} holds only outcome "
                f"{int(truth[0])} over {truth.size} rows, so it has no AUC, KS or calibration "
                "slope; the split rule is not selecting what package.yaml says it does"
            )
        area = stats.auc(truth, scores)
        values: dict[str, float] = {
            "n": float(truth.size),
            "event_rate": float(truth.mean()),
            "auc": area,
            "gini": stats.gini(area),
            "ks": stats.ks(truth, scores),
            "brier": stats.brier(truth, scores),
            "logloss": stats.logloss(truth, scores),
            "mean_predicted": float(scores.mean()),
        }
        artifacts = [
            ctx.store.put(
                f"metrics.{split}.{metric}",
                int(values[metric]) if metric == "n" else values[metric],
                ArtifactKind.scalar,
                f"{metric} on {split}, recomputed by quaestor",
            )
            for metric in SCALAR_METRICS
        ]

        slope, intercept = stats.calibration_slope_intercept(truth, scores)
        values["calibration_slope"] = slope
        values["calibration_intercept"] = intercept
        rate = values["event_rate"]
        relative_gap = abs(values["mean_predicted"] - rate) / rate if rate > 0.0 else 0.0
        values["mean_rel_gap"] = relative_gap
        artifacts += [
            ctx.store.put(
                f"calibration.{split}",
                stats.calibration_table(truth, scores),
                ArtifactKind.table,
                f"calibration by decile of predicted probability on {split}",
            ),
            ctx.store.put(
                f"calibration_slope.{split}",
                slope,
                ArtifactKind.scalar,
                f"logistic regression of the outcome on logit(p) on {split}: the slope",
            ),
            ctx.store.put(
                f"calibration_intercept.{split}",
                intercept,
                ArtifactKind.scalar,
                f"logistic regression of the outcome on logit(p) on {split}: the intercept",
            ),
            ctx.store.put(
                f"calibration.mean_rel_gap.{split}",
                relative_gap,
                ArtifactKind.scalar,
                f"mean predicted against observed on {split}, relative",
            ),
        ]

        rows = stats.deciles_table(truth, scores)
        artifacts += [
            ctx.store.put(
                f"deciles.{split}",
                rows,
                ArtifactKind.table,
                f"decile separation on {split}; decile 1 holds the highest probabilities",
            ),
            ctx.store.put(
                f"deciles.{split}.top2_capture",
                stats.top_capture(rows),
                ArtifactKind.scalar,
                f"share of {split} events in the top two deciles",
            ),
        ]
        artifacts += self._cpr(ctx, split, frame)
        return values, artifacts

    def _cpr(self, ctx: ToolContext, split: str, frame: pd.DataFrame) -> list[Artifact]:
        """Store the monthly actual-against-predicted CPR table for a hazard subject.

        A discrete-time hazard is fitted on loan-months and read in annual terms, so the table a
        prepayment reader wants is the monthly single-month mortality of each period, annualised
        both for the outcome and for the prediction. ``cpr.<split>.mae`` is the mean absolute
        difference between the two curves; no threshold governs it today, and a package that
        declares a ``cpr_mae`` rule gets it checked by ``T1`` without any further change here.
        """
        time_column = ctx.package.spec.data.time_column
        if time_column is None or time_column not in frame.columns:
            return []
        grouped = frame.groupby(time_column, sort=True)
        rows: list[dict[str, Any]] = []
        for period, part in grouped:
            actual = stats.cpr_from_smm(float(part["y_true"].mean()))
            predicted = stats.cpr_from_smm(float(part["y_score"].mean()))
            rows.append(
                {
                    str(time_column): int(period)
                    if isinstance(period, (int, np.integer))
                    else period,
                    "n": int(len(part)),
                    "actual_cpr": actual,
                    "predicted_cpr": predicted,
                }
            )
        error = float(np.mean([abs(row["actual_cpr"] - row["predicted_cpr"]) for row in rows]))
        return [
            ctx.store.put(
                f"cpr.{split}",
                rows,
                ArtifactKind.table,
                f"actual against predicted CPR by {time_column} on {split}",
            ),
            ctx.store.put(
                f"cpr.{split}.mae",
                error,
                ArtifactKind.scalar,
                f"mean absolute difference between actual and predicted CPR on {split}",
            ),
        ]

    def _subpopulation(
        self, ctx: ToolContext, splits: list[str], slice_: Subpopulation
    ) -> list[Artifact]:
        """Compute the scalar metrics on one slice of each split, and how it reads.

        Besides the eight scalars, each slice stores two numbers and the two bounds they are read
        against: ``metrics.<split>.sub.<slug>.auc_gap``, the split's own AUC minus the slice's, and
        ``metrics.<split>.sub.<slug>.share``, the slice's share of the split. They decide **where**
        the result is reported -- a slice materially worse than the headline and large enough to
        matter is a question for the model developer in section 6's open items, and any other slice
        is supporting evidence in the section that computed it -- and they raise **no candidate**:
        a model that discriminates less well on a segment selected by one of its own features is
        usually a model conditioning correctly, and a rule that fired on it would be the false
        alarm D-086 exists to refuse. Storing the two bounds is D-091: the sentence that says a
        slice is materially worse cites the number that decided it (DECISIONS D-102).
        """
        artifacts: list[Artifact] = [
            ctx.thresholds.artifact(ctx.store, SLICE_GAP_BOUND),
            ctx.thresholds.artifact(ctx.store, SLICE_SHARE_FLOOR),
        ]
        for split in splits:
            frame = scored_frame(ctx, split)
            if slice_.column not in frame.columns:
                raise ToolError(
                    f"data_{split}.csv of package {ctx.package.name!r} has no column "
                    f"{slice_.column!r}, so the sub-population cannot be selected; it has "
                    f"{list(feature_frame(ctx, split).columns)}"
                )
            part = frame[self._mask(frame, slice_)]
            if part.empty:
                raise ToolError(
                    f"the sub-population {slice_.column}:{slice_.rule} selects no row of {split!r}"
                )
            truth = part["y_true"].to_numpy(dtype=int)
            scores = part["y_score"].to_numpy(dtype=float)
            area = stats.auc(truth, scores)
            values: dict[str, float] = {
                "n": float(truth.size),
                "event_rate": float(truth.mean()),
                "auc": area,
                "gini": stats.gini(area),
                "ks": stats.ks(truth, scores),
                "brier": stats.brier(truth, scores),
                "logloss": stats.logloss(truth, scores),
                "mean_predicted": float(scores.mean()),
            }
            artifacts += [
                ctx.store.put(
                    f"metrics.{split}.sub.{slice_.slug}.{metric}",
                    int(values[metric]) if metric == "n" else values[metric],
                    ArtifactKind.scalar,
                    f"{metric} on the {slice_.column} {slice_.rule} slice of {split}",
                )
                for metric in SCALAR_METRICS
            ]
            artifacts += self._slice_reading(ctx, split, slice_, frame, values)
        return artifacts

    @staticmethod
    def _slice_reading(
        ctx: ToolContext,
        split: str,
        slice_: Subpopulation,
        frame: pd.DataFrame,
        values: Mapping[str, float],
    ) -> list[Artifact]:
        """Store how one slice reads against its split, and the slice's metrics as a table.

        The eight scalars and the share are also stored as ``metrics.<split>.sub.<slug>``, one row
        per metric, so that the section reporting the slice can point at a table instead of
        enumerating nine cited numbers per split. That is D-092's argument about the threshold
        table, applied to the family the bounded loop generates: on the fifth live run four slices
        wrote 72 of the report's 285 claims and most of its 417 claim checks, all of them
        transcription of numbers a table renders from the store, and a table's cells are excluded
        from extraction because the renderer and not a model wrote them (D-013, DECISIONS D-115).
        The AUC gap and the share stay scalars as well: they are what the interpreting sentences
        cite, and a number in prose needs an artifact behind it.
        """
        stem = sub_metrics_table_name(split, slice_.slug)
        headline = f"metrics.{split}.auc"
        share = float(values["n"]) / float(len(frame))
        stored: list[Artifact] = [
            ctx.store.put(
                f"{stem}.share",
                share,
                ArtifactKind.scalar,
                f"the share of {split} the {slice_.column} {slice_.rule} slice holds",
            )
        ]
        if headline in ctx.store:
            stored.append(
                ctx.store.put(
                    f"{stem}.auc_gap",
                    ctx.store.value(headline) - values["auc"],
                    ArtifactKind.scalar,
                    f"how far AUC on the {slice_.column} {slice_.rule} slice of {split} falls "
                    f"below AUC on all of {split}",
                )
            )
        rows = [{"metric": metric, "value": values[metric]} for metric in SCALAR_METRICS]
        rows.append({"metric": "share", "value": share})
        stored.append(
            ctx.store.put(
                stem,
                rows,
                ArtifactKind.table,
                f"every metric on the {slice_.column} {slice_.rule} slice of {split}",
            )
        )
        return stored

    @staticmethod
    def _mask(frame: pd.DataFrame, slice_: Subpopulation) -> pd.Series[bool]:
        """Return the boolean mask one sub-population rule selects."""
        column = frame[slice_.column]
        if slice_.rule in ("below_median", "above_median"):
            numeric = pd.to_numeric(column, errors="coerce")
            if numeric.isna().all():
                raise ToolError(
                    f"column {slice_.column!r} is not numeric, so it has no median to slice at"
                )
            median = float(numeric.median())
            return numeric < median if slice_.rule == "below_median" else numeric >= median
        wanted = slice_.rule.split(":", 1)[1]
        return column.astype(str) == wanted

    def _thresholds(
        self, ctx: ToolContext
    ) -> tuple[list[Artifact], list[FindingCandidate], list[str]]:
        """Check every developer-declared threshold against the store, and raise ``T1``."""
        artifacts: list[Artifact] = []
        candidates: list[FindingCandidate] = []
        unevaluated: list[str] = []
        rows: list[dict[str, Any]] = []
        for rule in ctx.package.spec.thresholds:
            name = metric_artifact_name(rule.metric, rule.split)
            if name is None or name not in ctx.store:
                unevaluated.append(f"{rule.metric}{f' on {rule.split}' if rule.split else ''}")
                rows += _unevaluated_rows(rule, name)
                continue
            value = ctx.store.value(name)
            bounds = package_threshold_names(rule)
            stored = {
                logical: ctx.store.put(
                    logical,
                    bound,
                    ArtifactKind.scalar,
                    f"package.yaml declares {rule.metric} {logical.rsplit('.', 1)[1]} {bound}",
                )
                for logical, bound in bounds.items()
            }
            artifacts += list(stored.values())
            for logical, bound in bounds.items():
                breached = value < bound if logical.endswith(".min") else value > bound
                rows.append(
                    {
                        "metric": rule.metric,
                        "split": rule.split or "",
                        "bound": _bound_text(logical, bound),
                        "value": value,
                        "result": "fail" if breached else "pass",
                    }
                )
                if not breached:
                    continue
                candidates.append(
                    FindingCandidate(
                        defect_class=DefectClass.T1,
                        evidence=[ctx.store.artifact(name).hash, stored[logical].hash],
                        detail=self._breach_detail(rule, logical, bound, name, value),
                        suggested_severity=Severity.high,
                        tool=self.name,
                    )
                )
        artifacts.append(
            ctx.store.put(
                THRESHOLD_TABLE,
                rows,
                ArtifactKind.table,
                "every threshold package.yaml declares, with its bound, the recomputed value and "
                "the outcome",
            )
        )
        return artifacts, candidates, unevaluated

    @staticmethod
    def _breach_detail(
        rule: ThresholdSpec, logical: str, bound: float, name: str, value: float
    ) -> str:
        """One sentence naming the declared rule, the artifact and the number that broke it."""
        direction = "below the minimum" if logical.endswith(".min") else "above the maximum"
        where = f" on {rule.split}" if rule.split else ""
        return (
            f"package.yaml declares {rule.metric}{where} {logical.rsplit('.', 1)[1]} {bound}; "
            f"quaestor computed {value:.6g} ({name}), which is {direction}"
        )

    def _calibration_rule(
        self, ctx: ToolContext, computed: dict[str, dict[str, float]]
    ) -> tuple[list[Artifact], list[FindingCandidate]]:
        """Raise ``C1`` where a slope leaves its band or mean predicted leaves the event rate."""
        low = ctx.thresholds["threshold.C1.calibration_slope.min"]
        high = ctx.thresholds["threshold.C1.calibration_slope.max"]
        relative = ctx.thresholds["threshold.C1.mean_ratio_rel"]
        # Stored whether or not anything breaches them: a report that says "the slope is inside
        # [0.80, 1.20]" is citing two numbers, and a number in prose needs an artifact behind it.
        bounds = {
            key: ctx.thresholds.artifact(ctx.store, key)
            for key in (
                "threshold.C1.calibration_slope.min",
                "threshold.C1.calibration_slope.max",
                "threshold.C1.mean_ratio_rel",
            )
        }
        artifacts: list[Artifact] = list(bounds.values())
        candidates: list[FindingCandidate] = []
        for split, values in computed.items():
            slope = values["calibration_slope"]
            gap = values["mean_rel_gap"]
            outside = slope < low or slope > high
            adrift = gap > relative
            if not (outside or adrift):
                continue
            evidence: list[str] = []
            detail: list[str] = []
            if outside:
                bound = (
                    "threshold.C1.calibration_slope.min"
                    if slope < low
                    else "threshold.C1.calibration_slope.max"
                )
                evidence += [
                    ctx.store.artifact(f"calibration_slope.{split}").hash,
                    bounds[bound].hash,
                ]
                detail.append(
                    f"the calibration slope on {split} is {slope:.4f}, outside [{low}, {high}]"
                )
            if adrift:
                artifact = bounds["threshold.C1.mean_ratio_rel"]
                evidence += [
                    ctx.store.artifact(f"calibration.mean_rel_gap.{split}").hash,
                    ctx.store.artifact(f"metrics.{split}.mean_predicted").hash,
                    ctx.store.artifact(f"metrics.{split}.event_rate").hash,
                    artifact.hash,
                ]
                detail.append(
                    f"the mean predicted probability on {split} ({values['mean_predicted']:.6g}) "
                    f"differs from the observed rate ({values['event_rate']:.6g}) by {gap:.2%} "
                    f"relative, against a tolerance of {relative:.0%}"
                )
            candidates.append(
                FindingCandidate(
                    defect_class=DefectClass.C1,
                    evidence=sorted(set(evidence)),
                    detail="; ".join(detail),
                    suggested_severity=Severity.medium,
                    tool=self.name,
                )
            )
        return artifacts, candidates

    def _degradation(
        self, ctx: ToolContext, computed: dict[str, dict[str, float]]
    ) -> tuple[list[Artifact], list[FindingCandidate]]:
        """Raise ``O1`` on a train-to-test gap, or on a period split below test."""
        artifacts: list[Artifact] = []
        candidates: list[FindingCandidate] = []
        if "train" in computed and "test" in computed:
            gap = computed["train"]["auc"] - computed["test"]["auc"]
            limit = ctx.thresholds["threshold.O1.auc_gap"]
            artifact = ctx.thresholds.artifact(ctx.store, "threshold.O1.auc_gap")
            artifacts.append(artifact)
            if gap > limit:
                candidates.append(
                    FindingCandidate(
                        defect_class=DefectClass.O1,
                        evidence=[
                            ctx.store.artifact("metrics.train.auc").hash,
                            ctx.store.artifact("metrics.test.auc").hash,
                            artifact.hash,
                        ],
                        detail=(
                            f"the training AUC of {computed['train']['auc']:.4f} exceeds the test "
                            f"AUC of {computed['test']['auc']:.4f} by {gap:.4f}, against a "
                            f"generalisation-gap threshold of {limit}"
                        ),
                        suggested_severity=Severity.medium,
                        tool=self.name,
                    )
                )
        if "test" not in computed:
            return artifacts, candidates
        holdout_limit = ctx.thresholds["threshold.O1.holdout_gap"]
        period_splits = [split for split in ("out_of_time", "vintage_holdout") if split in computed]
        if not period_splits:
            return artifacts, candidates
        holdout_threshold = ctx.thresholds.artifact(ctx.store, "threshold.O1.holdout_gap")
        artifacts.append(holdout_threshold)
        for split in period_splits:
            shortfall = computed["test"]["auc"] - computed[split]["auc"]
            if shortfall <= holdout_limit:
                continue
            candidates.append(
                FindingCandidate(
                    defect_class=DefectClass.O1,
                    evidence=[
                        ctx.store.artifact(f"metrics.{split}.auc").hash,
                        ctx.store.artifact("metrics.test.auc").hash,
                        holdout_threshold.hash,
                    ],
                    detail=(
                        f"the AUC on {split} is {computed[split]['auc']:.4f}, below the test AUC "
                        f"of {computed['test']['auc']:.4f} by {shortfall:.4f}, against a "
                        f"threshold of {holdout_limit}"
                    ),
                    suggested_severity=Severity.medium,
                    tool=self.name,
                )
            )
        return artifacts, candidates


def _bound_text(logical: str, bound: float) -> str:
    """Render one bound as ``minimum 0.7`` or ``maximum 0.2``, from the name it is stored under."""
    direction = "minimum" if logical.endswith(".min") else "maximum"
    return f"{direction} {bound:.6g}"


def _unevaluated_rows(rule: ThresholdSpec, name: str | None) -> list[dict[str, Any]]:
    """Render the rows of a declared rule this pipeline computed no artifact for.

    A declaration nobody checked must not read as a declaration that held (spec section 3.7), so
    the row is written with the bound the developer stated and ``not evaluated`` in place of a
    value, and the reason is the metric's own name.

    Args:
        rule: The declared rule.
        name: The logical name that would have answered it, or ``None`` when none exists.

    Returns:
        One row per bound the rule states.
    """
    why = (
        f"no artifact of this run answers {rule.metric!r}"
        if name is None
        else f"{name} is not in the store"
    )
    return [
        {
            "metric": rule.metric,
            "split": rule.split or "",
            "bound": _bound_text(logical, bound),
            "value": f"not evaluated: {why}",
            "result": "not evaluated",
        }
        for logical, bound in package_threshold_names(rule).items()
    ]
