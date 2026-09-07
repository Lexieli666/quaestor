"""``run_scenarios``: the rate-shock table, its convexity, and the ``X1`` rule.

Spec section 3.7's eighth row, for hazard subjects only. The subject writes ``projection.json``
itself (spec section 4.2), because rolling the fitted hazard forward needs the fitted hazard, and
the validator never imports the subject. What this tool does with that file is recompute
everything derived from it: the value change at each shock is taken as the shock's value minus the
base case's, and the convexity as the sum of the changes at the extreme down and up shocks. The
developer's own ``value_change`` and ``convexity`` fields are read only to be compared with those
recomputations, and a disagreement is reported in the summary rather than silently adopted -- the
same rule that keeps ``metrics.json`` out of the outcomes analysis.

``X1`` fires on either of two things: a value curve that is not monotone in the shock, which no
parallel shift of a rate path should produce; or a convexity whose sign contradicts what
``package.yaml``'s ``scenarios.convexity_expectation`` declares.
"""

from __future__ import annotations

from typing import Any, Final

from ..artifacts import Artifact, ArtifactKind
from ..errors import ToolError
from ..findings import DefectClass, FindingCandidate, Severity
from ..package import ModelType
from .frames import projection
from .registry import Tool, ToolArgs, ToolContext, ToolResult

__all__ = ["RunScenariosTool"]

_TOLERANCE: Final = 1e-6
"""Relative tolerance when comparing the developer's stated changes with the recomputed ones."""


class RunScenariosTool(Tool["RunScenariosTool.Args"]):
    """Read the subject's projection, recompute its value changes and check its convexity."""

    name = "run_scenarios"
    description = (
        "Read the hazard subject's projection, recompute the servicing value change at each "
        "declared rate shock and the convexity of the curve, and check both against the "
        "convexity the package declares."
    )

    class Args(ToolArgs):
        """Arguments of ``run_scenarios``.

        Attributes:
            expectation: Which way the value curve is expected to bend, overriding
                ``scenarios.convexity_expectation``; ``None`` uses the package's own declaration,
                which is the only thing a validation should normally test against.
        """

        expectation: str | None = None

    def run(self, args: RunScenariosTool.Args, ctx: ToolContext) -> ToolResult:
        """Store the shock table and raise ``X1`` on a non-monotone or wrong-signed curve.

        Args:
            args: An optional override of the declared convexity expectation.
            ctx: The run's context.

        Returns:
            The shock table, one value-change artifact per shock, the convexity, and any ``X1``.

        Raises:
            ToolError: The package is not a hazard package, declares no scenarios, or its
                ``projection.json`` does not carry a value for every declared shock.
        """
        spec = ctx.package.spec
        if spec.model_type is not ModelType.discrete_time_hazard or spec.scenarios is None:
            raise ToolError(
                f"package {ctx.package.name!r} is a {spec.model_type} package with "
                f"{'no' if spec.scenarios is None else 'no applicable'} scenarios block, so there "
                "is no projection to shock; the report lists this in Appendix D as not checked"
            )
        payload = projection(ctx)
        shocks = sorted(spec.scenarios.rate_shocks_bp)
        values = self._values(ctx, payload, shocks)
        base = values[0]
        changes = {shock: values[shock] - base for shock in shocks}

        rows: list[dict[str, Any]] = [
            {
                "shock_bp": shock,
                "value": values[shock],
                "value_change": changes[shock],
                "cpr": float(payload.get("cpr_by_shock", {}).get(str(shock), 0.0)),
            }
            for shock in shocks
        ]
        convexity = changes[shocks[0]] + changes[shocks[-1]]
        artifacts: list[Artifact] = [
            ctx.store.put(
                "scenario.value_by_shock",
                rows,
                ArtifactKind.table,
                "servicing value, its change from the base case and first-year CPR, by shock",
            ),
            *(
                ctx.store.put(
                    f"scenario.value_change.{shock}",
                    changes[shock],
                    ArtifactKind.scalar,
                    f"change in servicing value at {shock} bp",
                )
                for shock in shocks
            ),
            ctx.store.put(
                "scenario.convexity",
                convexity,
                ArtifactKind.scalar,
                (
                    f"the value change at {shocks[0]} bp plus the change at {shocks[-1]} bp; "
                    "negative when the fall outweighs the rise"
                ),
            ),
        ]

        expectation = args.expectation or spec.scenarios.convexity_expectation.value
        monotone = self._monotone(values, shocks)
        realised = "negative" if convexity < 0.0 else "positive" if convexity > 0.0 else "flat"
        candidates: list[FindingCandidate] = []
        if not monotone or realised != expectation:
            evidence = [
                ctx.store.artifact("scenario.value_by_shock").hash,
                ctx.store.artifact("scenario.convexity").hash,
                ctx.store.artifact(f"scenario.value_change.{shocks[0]}").hash,
                ctx.store.artifact(f"scenario.value_change.{shocks[-1]}").hash,
            ]
            if "run.projection" in ctx.store:
                evidence.append(ctx.store.artifact("run.projection").hash)
            detail = []
            if not monotone:
                detail.append(
                    "the projected value is not monotone in the rate shock, which a parallel "
                    f"shift of one rate path cannot produce: {[values[s] for s in shocks]}"
                )
            if realised != expectation:
                detail.append(
                    f"the realised convexity is {convexity:.6g} ({realised}) where package.yaml "
                    f"declares {expectation}"
                )
            candidates.append(
                FindingCandidate(
                    defect_class=DefectClass.X1,
                    evidence=sorted(set(evidence)),
                    detail="; ".join(detail),
                    suggested_severity=Severity.high,
                    tool=self.name,
                )
            )

        return ToolResult(
            tool=self.name,
            artifacts=artifacts,
            candidates=candidates,
            summary=(
                f"value change {changes[shocks[0]]:+.6g} at {shocks[0]} bp and "
                f"{changes[shocks[-1]]:+.6g} at {shocks[-1]} bp; convexity {convexity:+.6g} "
                f"({realised}, declared {expectation}); the curve is "
                f"{'monotone' if monotone else 'not monotone'} in the shock"
                f"{self._developer_disagreement(payload, changes, convexity)}"
            ),
        )

    @staticmethod
    def _values(ctx: ToolContext, payload: dict[str, Any], shocks: list[int]) -> dict[int, float]:
        """Read the value under each declared shock, naming any the projection does not carry."""
        raw = payload.get("value_by_shock")
        if not isinstance(raw, dict):
            raise ToolError(
                f"projection.json of package {ctx.package.name!r} has no 'value_by_shock' object; "
                "spec 4.2 requires the subject to write one"
            )
        missing = [shock for shock in shocks if str(shock) not in raw]
        if missing:
            raise ToolError(
                f"projection.json of package {ctx.package.name!r} has no value for the declared "
                f"shocks {missing}; it has {sorted(raw)}"
            )
        try:
            return {shock: float(raw[str(shock)]) for shock in shocks}
        except (TypeError, ValueError) as exc:
            raise ToolError(
                f"projection.json of package {ctx.package.name!r} holds a non-numeric value in "
                f"'value_by_shock': {exc}"
            ) from exc

    @staticmethod
    def _monotone(values: dict[int, float], shocks: list[int]) -> bool:
        """Whether the value curve moves one way across the shocks, ties allowed."""
        ordered = [values[shock] for shock in shocks]
        differences = [
            second - first for first, second in zip(ordered[:-1], ordered[1:], strict=True)
        ]
        return all(step >= 0.0 for step in differences) or all(step <= 0.0 for step in differences)

    @staticmethod
    def _developer_disagreement(
        payload: dict[str, Any], changes: dict[int, float], convexity: float
    ) -> str:
        """Report where the subject's own derived numbers differ from the recomputed ones."""
        stated = payload.get("value_change")
        problems: list[str] = []
        if isinstance(stated, dict):
            for shock, change in changes.items():
                if str(shock) not in stated:
                    continue
                declared = float(stated[str(shock)])
                if abs(declared - change) > _TOLERANCE * max(abs(change), 1.0):
                    problems.append(f"{shock} bp ({declared:.6g} against {change:.6g})")
        declared_convexity = payload.get("convexity")
        if isinstance(declared_convexity, (int, float)) and abs(
            float(declared_convexity) - convexity
        ) > _TOLERANCE * max(abs(convexity), 1.0):
            problems.append(f"convexity ({float(declared_convexity):.6g} against {convexity:.6g})")
        if not problems:
            return ""
        return (
            "; the subject's own projection.json disagrees with the recomputation at "
            + ", ".join(problems)
        )
