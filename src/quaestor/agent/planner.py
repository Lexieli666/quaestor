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

**Four actions are refused before anything runs**, and a refusal is traced with its reason rather
than raised: a tool that is not registered; arguments the tool's own ``Args`` model rejects, which
is where an invented ``entrypoint`` is caught, because every ``Args`` is closed; any path argument
that leaves the package, its data directory or the run directory; and a tool that is registered
but does not apply to this package -- ``check_stability`` without a ``regime.column``,
``run_scenarios`` on anything but a hazard subject, and ``run_model``, which the loop may never
call (D-089). An inapplicable tool is also kept off the menu the loop is shown, so the refusal is
the second line of defence and not the first.

**A tool that raises is not the run's failure.** A ``ToolError`` from a loop-requested call is
caught: the step is traced with ``accepted: true``, ``executed: false`` and the tool's message,
the next step's prompt carries that message, and the pipeline goes on to draft with what it has
(D-088). A failing *rule-based* call is still the run's failure, as it was.

The prompt itself is :func:`loop_prompt`, which lists what the rule-based plan called and raised
and what earlier steps of the loop did, so that the model reasons from the run rather than from
the candidate list alone (D-090).
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
from ..tools.registry import ToolRegistry, ToolResult
from ..trace import EventType, TraceWriter
from ..vocab import SECTION_ORDER

__all__ = [
    "GUIDANCE_TOOL",
    "MAX_FOLLOW_UP_STEPS",
    "PLAN_PURPOSE",
    "SCENARIOS_TOOL",
    "STABILITY_TOOL",
    "CompletedCall",
    "FollowUpAction",
    "PlanStep",
    "PlannedCall",
    "applicable_tools",
    "completed_calls",
    "follow_up_plan",
    "guidance_queries",
    "inapplicable_reason",
    "loop_prompt",
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

STABILITY_TOOL: Final = "check_stability"
"""Applicable only to a package that declares a ``regime.column``."""

SCENARIOS_TOOL: Final = "run_scenarios"
"""Applicable only to a hazard package that declares a ``scenarios`` block."""

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

    ``accepted`` and ``executed`` are two questions, and the second is the one D-088 adds: an
    action may pass every rule the loop applies and then fail inside the tool, which is neither a
    refusal nor a success and is the shape the second live attempt died in.

    Attributes:
        step: The 1-based step number.
        action: What the model asked for.
        accepted: Whether the action passed every rule and was handed to the executor.
        executed: Whether the executor ran it and returned. ``False`` when the action was
            refused, when the loop stopped, when the tool raised, and when the loop was asked to
            plan without an executor.
        reason: Why it was refused, or why the loop stopped; empty when it was accepted.
        error: The ``ToolError`` message, when an accepted call raised; empty otherwise.
        call: The planned call, when it was accepted.
    """

    step: int
    action: FollowUpAction
    accepted: bool
    reason: str = ""
    call: PlannedCall | None = None
    executed: bool = False
    error: str = ""


@dataclass(frozen=True)
class CompletedCall:
    """One call that has already been made, as the bounded loop is shown it.

    Attributes:
        tool: The tool that ran.
        args: The arguments it ran with.
        classes: The defect classes it raised, sorted; empty when it raised none.
    """

    tool: str
    args: Mapping[str, Any] = field(default_factory=dict)
    classes: Sequence[str] = ()


def completed_calls(
    calls: Sequence[PlannedCall], results: Sequence[ToolResult]
) -> list[CompletedCall]:
    """Pair a plan with its results, for the block the loop is shown.

    Args:
        calls: The calls the plan made, in order.
        results: What each returned, in the same order. A shorter sequence than ``calls`` -- a
            plan cut short -- pairs only as far as it goes.

    Returns:
        One :class:`CompletedCall` per pair, in plan order.
    """
    return [
        CompletedCall(call.tool, dict(call.args), result.classes)
        for call, result in zip(calls, results, strict=False)
    ]


def inapplicable_reason(tool: str, package: ModelPackage) -> str:
    """Return why a tool does not apply to this package, or ``""`` when it does.

    Three tools of the registry are not offers the bounded loop may make (D-089).
    ``run_model`` is never one: spec section 3.12 gives the loop a second question about a run
    that has happened, not the power to make it happen differently. ``check_stability`` needs a
    ``regime.column`` and ``run_scenarios`` needs a hazard subject with a ``scenarios`` block, and
    without them each tool raises the moment it is called -- which is what the second live attempt
    spent a plan call discovering.

    Args:
        tool: The tool's registered name.
        package: The package being validated.

    Returns:
        A clause naming what the package lacks, or the empty string when the tool applies.
    """
    spec = package.spec
    if tool == RUN_TOOL:
        return (
            "the follow-up loop may not run the subject; the rule-based plan runs it exactly "
            "once and every artifact the loop can read comes from that one run"
        )
    if tool == STABILITY_TOOL and not spec.regime.column:
        return (
            f"package {package.name!r} declares no `regime.column`, so there are no regimes to "
            "compare and Appendix D lists `check_stability` as not checked"
        )
    if tool == SCENARIOS_TOOL and (
        spec.model_type is not ModelType.discrete_time_hazard or spec.scenarios is None
    ):
        return (
            f"package {package.name!r} is a {spec.model_type.value} package with "
            f"{'no' if spec.scenarios is None else 'no applicable'} `scenarios` block, so there "
            "is no projection to shock"
        )
    return ""


def applicable_tools(registry: ToolRegistry, package: ModelPackage) -> list[str]:
    """Return the registered tools the bounded loop may offer for this package.

    Args:
        registry: The tools that exist.
        package: The package being validated.

    Returns:
        Their names, in registration order.
    """
    return [name for name in registry.names() if not inapplicable_reason(name, package)]


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
                STABILITY_TOOL,
                {},
                f"compare the champion across the regimes of {spec.regime.column!r}",
            )
        )
    calls.append(PlannedCall("check_collinearity", {}, "measure collinearity among the features"))
    calls.append(PlannedCall("challenger_compare", {}, "fit a challenger as effective challenge"))
    if spec.model_type is ModelType.discrete_time_hazard and spec.scenarios is not None:
        calls.append(PlannedCall(SCENARIOS_TOOL, {}, "recompute the declared rate shocks"))
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

    The four rules are applied in this order: the tool exists, its own ``Args`` model takes the
    arguments, no path argument leaves the package, and the tool applies to this package. The
    applicability rule is last on purpose (D-089), so that the three refusals spec section 3.12
    names keep their own messages: an action that asks ``run_model`` for a different
    ``entrypoint`` is still refused by the closed ``Args`` that names the field, and one that
    points a path at ``/etc`` is still refused by the rule that says so.
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
    why_not = inapplicable_reason(action.tool, package)
    if why_not:
        return None, f"not applicable to this package: {why_not}"
    return PlannedCall(action.tool, dict(action.args), action.why, source="loop"), ""


_LOOP_INSTRUCTION: Final = """\
You are the planning half of a model validation. The rule-based plan has already run; the calls
it made and the candidate findings they raised are below.

You may ask for at most {remaining} more tool call(s), one at a time, and you should ask for none
unless a call would tell a validator something the plan did not. The loop is for a follow-up
question about what the candidates show, not for repeating the plan.

Typical follow-ups: re-profiling one feature that drifted, or recomputing metrics on a
sub-population where the model may behave differently.

Calls the rule-based plan has already made, with the defect classes each raised:
{completed}

Candidate findings so far:
{candidates}

Artifacts already in the store ({n_artifacts} of them), by prefix:
{prefixes}
{history}
Tools you may call, with the JSON schema of each tool's arguments. Only the tools that apply to
this package are listed; a tool the registry has and this package does not support is not on the
list and asking for it will be refused:
{catalogue}

Answer with either {{"tool": "<name>", "args": {{...}}, "why": "<one clause>"}} or {{"stop": true}}.
An action naming a tool that is not listed, arguments the schema does not allow, or a path outside
the package will be refused and recorded as refused."""
"""What the loop is shown. The schemas are generated from each tool's ``Args``, never restated."""


def _completed_block(completed: Sequence[CompletedCall]) -> str:
    """Render what has already run, so the loop reasons from the run and not from the list."""
    if not completed:
        return "(none: this configuration ran no rule-based check)"
    return "\n".join(
        f"- {call.tool}({json.dumps(dict(call.args), sort_keys=True)}) -> "
        + (", ".join(call.classes) if call.classes else "no candidate")
        for call in completed
    )


def _history_block(steps: Sequence[PlanStep]) -> str:
    """Render what earlier steps of this loop asked for and what became of each.

    The refusal reason and the ``ToolError`` message both come back here, which is the half of
    D-088 and D-089 the model sees: a step that was refused as inapplicable, or that was accepted
    and then failed inside the tool, is not worth spending the next step on again.
    """
    lines: list[str] = []
    for step in steps:
        if not step.action.tool:
            continue
        asked = f"- step {step.step}: {step.action.tool}"
        asked += f"({json.dumps(step.action.args, sort_keys=True)})"
        if not step.accepted:
            lines.append(f"{asked} was refused: {step.reason}")
        elif step.error:
            lines.append(f"{asked} was accepted and the tool failed: {step.error}")
        else:
            lines.append(f"{asked} ran")
    if not lines:
        return ""
    return "\nWhat earlier steps of this loop did:\n" + "\n".join(lines) + "\n"


def loop_prompt(
    registry: ToolRegistry,
    package: ModelPackage,
    *,
    remaining: int,
    candidates: Sequence[FindingCandidate] = (),
    completed: Sequence[CompletedCall] = (),
    artifact_names: Sequence[str] = (),
    history: Sequence[PlanStep] = (),
) -> str:
    """Build the prompt one step of the bounded loop is sent.

    Args:
        registry: The tools that exist; only the applicable ones are offered (D-089).
        package: The package being validated, which decides what applies.
        remaining: How many calls the model may still ask for, this one included.
        candidates: What has been raised so far.
        completed: What the rule-based plan called, and what each call raised (D-090).
        artifact_names: What is in the store, summarised by prefix rather than dumped.
        history: The steps this loop has already taken, so a refusal or a tool failure is fed
            back rather than repeated (D-088).

    Returns:
        The prompt. It is a function rather than a template substitution at the call site so that
        a test can send the loop exactly what a recorded run was sent.
    """
    catalogue = [
        entry
        for entry in registry.catalogue()
        if not inapplicable_reason(str(entry["tool"]), package)
    ]
    return _LOOP_INSTRUCTION.format(
        remaining=remaining,
        completed=_completed_block(completed),
        candidates=_candidates_block(candidates),
        n_artifacts=len(artifact_names),
        prefixes=_prefixes(artifact_names) or "(none)",
        history=_history_block(history),
        catalogue=json.dumps(catalogue, indent=1, ensure_ascii=True),
    )


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
    completed: Sequence[CompletedCall] = (),
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
        registry: The tools that exist, whose applicable schemas the model is shown.
        package: The package being validated.
        candidates: What the rule-based plan raised, which is what the loop reasons about.
        completed: What the rule-based plan called and what each call raised (D-090).
        artifact_names: What is already in the store, summarised by prefix for the prompt.
        roots: Directories besides the package that a path argument may name.
        max_steps: How many steps the loop may take. Spec section 3.12 says four.
        trace: The run's trace; one ``plan_step`` event per step, accepted or refused.
        execute: Called as ``execute(call)`` for each accepted call, so that the next step sees
            what the last one produced; ``None`` plans without executing.
        **params: Passed to the provider.

    Returns:
        One :class:`PlanStep` per step, in order. The loop ends on ``{"stop": true}`` or on the
        step limit. Neither a refusal nor a tool that raised ends it -- both are recorded, both
        count against the limit, and both are fed back into the next step's prompt, because a
        model that asked for the wrong thing has not asked to stop (D-088).
    """
    steps: list[PlanStep] = []
    names = list(artifact_names)
    for number in range(1, max_steps + 1):
        prompt = loop_prompt(
            registry,
            package,
            remaining=max_steps - number + 1,
            candidates=candidates,
            completed=completed,
            artifact_names=names,
            history=steps,
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
        if call is None:
            steps.append(PlanStep(number, action, False, reason))
            _trace_step(trace, steps[-1])
            continue
        executed, error = False, ""
        if execute is not None:
            try:
                result = execute(call)
            except ToolError as exc:
                error = exc.message
            else:
                executed = True
                names += list(getattr(result, "artifact_names", []) or [])
        step = PlanStep(number, action, True, "", call, executed=executed, error=error)
        steps.append(step)
        _trace_step(trace, step)
    return steps


def _trace_step(trace: TraceWriter | None, step: PlanStep) -> None:
    """Write one ``plan_step`` event: what was asked for, whether it was accepted, whether it ran.

    ``executed`` and ``error`` are what ``eval/score.py`` and a reader of the trace need in order
    to tell a step the loop refused from a step the loop accepted and the tool could not answer
    (D-088). The registry has already written that failure's own ``tool_call`` event with
    ``ok: false``; this is the planner's side of the same fact.
    """
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
        executed=step.executed,
        reason=step.reason,
        error=step.error,
    )
