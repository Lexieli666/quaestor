"""The planner: a rule-based check list, then a bounded loop the model may add four steps to.

Spec section 3.12. The plan is rules first, because what a validation must check is a property of
the package and not an opinion: every subject gets ``run_model``, ``profile_data``,
``compute_metrics``, ``check_leakage``, ``check_collinearity``, ``challenger_compare`` and one
``retrieve_guidance`` per report section; a hazard subject adds ``run_scenarios``; a package that
declares a regime column adds ``check_stability``.

Only then, and only under ``full_agent``, is the model shown the candidate findings and the tools'
own JSON schemas and asked for one action at a time: ``{"tool": ..., "args": {...}, "why": ...}``
or ``{"stop": true}``. At most four steps. Every step is a ``plan_step`` trace event, accepted or
not, which is what lets the study count what the loop did rather than what it said.

**Three actions are refused before anything runs**, and a refusal is traced with its reason rather
than raised: a tool that is not registered; arguments the tool's own ``Args`` model rejects, which
is where an invented ``entrypoint`` is caught, because every ``Args`` is closed; and any path
argument that leaves the package, its data directory or the run directory. The loop exists to ask
a second question about this model, not to reach the filesystem.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

from pydantic import BaseModel, ConfigDict, Field

from ..errors import ToolError
from ..findings import FindingCandidate
from ..llm.base import LLM
from ..llm.structured import structured
from ..package import ModelPackage
from ..package.spec import ModelType
from ..report.sections import DEFECT_CLASS_NAMES, SECTION_BRIEFS
from ..tools.registry import ToolRegistry
from ..trace import EventType, TraceWriter
from ..vocab import SECTION_ORDER

__all__ = [
    "GUIDANCE_TOOL",
    "MAX_FOLLOW_UP_STEPS",
    "PLAN_PURPOSE",
    "FollowUpAction",
    "PlanStep",
    "PlannedCall",
    "follow_up_plan",
    "guidance_queries",
    "rule_based_plan",
    "validate_action",
]

MAX_FOLLOW_UP_STEPS: Final = 4
"""Spec section 3.12: "a bounded follow-up loop (max 4 steps)"."""

PLAN_PURPOSE: Final = "plan"
"""The ``llm_call`` purpose recorded for one step of the bounded loop."""

GUIDANCE_TOOL: Final = "retrieve_guidance"
"""The one tool the rule-based plan calls once per report section."""

RUN_TOOL: Final = "run_model"
"""The one tool whose arguments can name a directory, and so the one the path rule is about."""

_PATH_HINTS: Final = ("dir", "path", "file", "root")
"""Argument names that carry a filesystem path; the loop may not point one outside the package."""


@dataclass(frozen=True)
class PlannedCall:
    """One tool call the plan will make.

    Attributes:
        tool: The tool's registered name.
        args: Its arguments, as the registry will validate them.
        why: One clause saying what this call is for; written to the ``plan_step`` event.
        source: ``rules`` for the rule-based plan, ``loop`` for the bounded follow-up loop.
    """

    tool: str
    args: Mapping[str, Any] = field(default_factory=dict)
    why: str = ""
    source: str = "rules"


class FollowUpAction(BaseModel):
    """One action of the bounded loop, exactly as spec section 3.12 writes it.

    Attributes:
        tool: The tool to call, or ``None`` when stopping.
        args: Its arguments.
        why: Why this call is worth making.
        stop: ``True`` to end the loop.
    """

    model_config = ConfigDict(extra="forbid")

    tool: str | None = None
    args: dict[str, Any] = Field(default_factory=dict)
    why: str = ""
    stop: bool = False


@dataclass(frozen=True)
class PlanStep:
    """What one step of the bounded loop asked for, and what became of it.

    Attributes:
        step: The 1-based step number.
        action: What the model asked for.
        accepted: Whether the action was executed.
        reason: Why it was refused, or why the loop stopped; empty when it was accepted.
        call: The planned call, when it was accepted.
    """

    step: int
    action: FollowUpAction
    accepted: bool
    reason: str = ""
    call: PlannedCall | None = None


def guidance_queries() -> list[tuple[str, str]]:
    """Return the guidance query each report section is anchored with.

    Returns:
        ``(section, query)`` pairs, in report order.
    """
    return [(section.value, SECTION_BRIEFS[section].guidance_query) for section in SECTION_ORDER]


def rule_based_plan(
    package: ModelPackage,
    *,
    synthetic: int | None = None,
    data_dir: Path | str | None = None,
    seed: int | None = None,
    guidance: bool = True,
) -> list[PlannedCall]:
    """Return the plan spec section 3.12 derives from ``model_type`` and ``package.yaml``.

    Args:
        package: The loaded package.
        synthetic: How many rows to generate, for an offline run.
        data_dir: Where the real data is, for a ``--data`` run.
        seed: Passed to the subject, or ``None`` for the subject's own default.
        guidance: Whether to retrieve guidance per section; ``plain_llm`` does not.

    Returns:
        The calls, in the order they run: the subject first, because everything else reads what it
        wrote, then the checks in the order the report's sections need them, then the retrievals.
    """
    spec = package.spec
    run_args: dict[str, Any] = {}
    if synthetic is not None:
        run_args["synthetic"] = int(synthetic)
    if data_dir is not None:
        run_args["data_dir"] = str(data_dir)
    if seed is not None:
        run_args["seed"] = int(seed)
    calls = [
        PlannedCall(RUN_TOOL, run_args, "run the subject and store the spec 3.3 contract"),
        PlannedCall("profile_data", {}, "profile every split and compare it with training"),
        PlannedCall("compute_metrics", {}, "recompute every metric and check declared thresholds"),
        PlannedCall("check_leakage", {}, "screen for leakage and train/test contamination"),
    ]
    if spec.regime.column:
        calls.append(
            PlannedCall(
                "check_stability",
                {},
                f"compare the champion across the regimes of {spec.regime.column!r}",
            )
        )
    calls.append(PlannedCall("check_collinearity", {}, "measure collinearity among the features"))
    calls.append(PlannedCall("challenger_compare", {}, "fit a challenger as effective challenge"))
    if spec.model_type is ModelType.discrete_time_hazard and spec.scenarios is not None:
        calls.append(PlannedCall("run_scenarios", {}, "recompute the declared rate shocks"))
    if guidance:
        calls += [
            PlannedCall(
                GUIDANCE_TOOL,
                {"query": query},
                f"anchor section {section} to the guidance",
            )
            for section, query in guidance_queries()
        ]
    return calls


def _inside(path: Path, roots: Sequence[Path]) -> bool:
    """Whether a path resolves inside one of the roots the loop is allowed to reach."""
    resolved = path.expanduser().resolve()
    for root in roots:
        try:
            resolved.relative_to(root.expanduser().resolve())
        except ValueError:
            continue
        return True
    return False


def _path_arguments(args: Mapping[str, Any]) -> list[tuple[str, str]]:
    """Return the arguments whose name says they carry a filesystem path."""
    return [
        (key, value)
        for key, value in args.items()
        if isinstance(value, str) and any(hint in key.lower() for hint in _PATH_HINTS)
    ]


def validate_action(
    action: FollowUpAction,
    registry: ToolRegistry,
    package: ModelPackage,
    *,
    roots: Sequence[Path] = (),
) -> tuple[PlannedCall | None, str]:
    """Decide whether one action of the bounded loop may run.

    Args:
        action: What the model asked for.
        registry: The tools that exist.
        package: The package being validated, which bounds where a path may point.
        roots: Extra directories the loop may name -- the run directory, and the data directory
            when the run has one.

    Returns:
        The call to make and an empty reason, or ``None`` and the reason it was refused.
    """
    if not action.tool:
        return None, "the action names no tool"
    try:
        tool = registry.get(action.tool)
    except ToolError as exc:
        return None, exc.message
    try:
        tool.parse(action.args)
    except ToolError as exc:
        return None, exc.message
    allowed = [package.root, *roots]
    for key, value in _path_arguments(action.args):
        if not _inside(Path(value), allowed):
            return None, (
                f"argument {key}={value!r} points outside the package at {package.root} and the "
                f"run's own directories; the follow-up loop may not reach the filesystem"
            )
    return PlannedCall(action.tool, dict(action.args), action.why, source="loop"), ""


_LOOP_INSTRUCTION: Final = """\
You are the planning half of a model validation. The rule-based plan has already run and produced
the candidate findings below. You may ask for at most {remaining} more tool call(s), one at a
time, and you should ask for none unless a call would tell a validator something the plan did not.

Typical follow-ups: re-profiling one feature that drifted, or recomputing metrics on a
sub-population where the model may behave differently.

Candidate findings so far:
{candidates}

Artifacts already in the store ({n_artifacts} of them), by prefix:
{prefixes}

Tools you may call, with the JSON schema of each tool's arguments:
{catalogue}

Answer with either {{"tool": "<name>", "args": {{...}}, "why": "<one clause>"}} or {{"stop": true}}.
An action naming a tool that is not listed, arguments the schema does not allow, or a path outside
the package will be refused and recorded as refused."""
"""What the loop is shown. The schemas are generated from each tool's ``Args``, never restated."""


def _prefixes(names: Sequence[str]) -> str:
    """Summarise a store by logical-name prefix, so the loop knows what exists without a dump."""
    counts: dict[str, int] = {}
    for name in names:
        head = name.split(".", 1)[0]
        counts[head] = counts.get(head, 0) + 1
    return ", ".join(f"{head} ({count})" for head, count in sorted(counts.items()))


def _candidates_block(candidates: Sequence[FindingCandidate]) -> str:
    """Render the candidates the loop is shown."""
    if not candidates:
        return "(none: every check that ran raised nothing)"
    return "\n".join(
        f"- {candidate.defect_class.value} "
        f"({DEFECT_CLASS_NAMES[candidate.defect_class]}, from {candidate.tool}): "
        f"{candidate.detail}"
        for candidate in candidates
    )


def follow_up_plan(
    llm: LLM,
    registry: ToolRegistry,
    package: ModelPackage,
    *,
    candidates: Sequence[FindingCandidate] = (),
    artifact_names: Sequence[str] = (),
    roots: Sequence[Path] = (),
    max_steps: int = MAX_FOLLOW_UP_STEPS,
    trace: TraceWriter | None = None,
    execute: Any = None,
    **params: Any,
) -> list[PlanStep]:
    """Run the bounded follow-up loop and return every step it took.

    Args:
        llm: The provider.
        registry: The tools that exist, whose schemas the model is shown.
        package: The package being validated.
        candidates: What the rule-based plan raised, which is what the loop reasons about.
        artifact_names: What is already in the store, summarised by prefix for the prompt.
        roots: Directories besides the package that a path argument may name.
        max_steps: How many steps the loop may take. Spec section 3.12 says four.
        trace: The run's trace; one ``plan_step`` event per step, accepted or refused.
        execute: Called as ``execute(call)`` for each accepted call, so that the next step sees
            what the last one produced; ``None`` plans without executing.
        **params: Passed to the provider.

    Returns:
        One :class:`PlanStep` per step, in order. The loop ends on ``{"stop": true}``, on the step
        limit, or on a refusal -- a refused action is recorded and the loop goes on to the next
        step, because a model that mistypes a tool name has not asked to stop.
    """
    steps: list[PlanStep] = []
    names = list(artifact_names)
    for number in range(1, max_steps + 1):
        prompt = _LOOP_INSTRUCTION.format(
            remaining=max_steps - number + 1,
            candidates=_candidates_block(candidates),
            n_artifacts=len(names),
            prefixes=_prefixes(names) or "(none)",
            catalogue=json.dumps(registry.catalogue(), indent=1, ensure_ascii=True),
        )
        action = structured(
            llm,
            prompt,
            FollowUpAction,
            trace=trace,
            purpose=PLAN_PURPOSE,
            trace_fields={"step": number},
            **params,
        )
        if action.stop or not action.tool:
            steps.append(PlanStep(number, action, False, "the planner stopped"))
            _trace_step(trace, steps[-1])
            break
        call, reason = validate_action(action, registry, package, roots=roots)
        step = PlanStep(number, action, call is not None, reason, call)
        steps.append(step)
        _trace_step(trace, step)
        if call is not None and execute is not None:
            result = execute(call)
            names += list(getattr(result, "artifact_names", []) or [])
    return steps


def _trace_step(trace: TraceWriter | None, step: PlanStep) -> None:
    """Write one ``plan_step`` event, whether the action ran or was refused."""
    if trace is None:
        return
    trace.emit(
        EventType.plan_step,
        step=step.step,
        source="loop",
        tool=step.action.tool,
        args=step.action.args,
        why=step.action.why,
        stop=step.action.stop,
        accepted=step.accepted,
        reason=step.reason,
    )
