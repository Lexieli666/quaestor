"""Phase 8: the rule-based plan, and the three things the bounded loop is not allowed to do.

Spec 3.12. The plan is a function of `package.yaml` and nothing else, so both shipped subjects are
planned here and the difference between them is asserted rather than described: a hazard subject
with a regime column gets two checks a binary classifier does not.

The loop's refusals are the other half. An action naming an unknown tool, an action whose arguments
the tool's own `Args` model rejects -- which is where an invented `entrypoint` is caught, because
every `Args` is closed -- an action pointing a path outside the package, and an action naming a
tool that exists but does not apply to this package are refused *before* anything runs, and each
refusal is a `plan_step` event a reader can find in the trace.

The Phase 9 follow-up adds the fourth refusal (D-089), the menu it is the second line of defence
for, a tool that raises rather than refuses (D-088), and the two blocks the prompt now carries
(D-090).
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pytest

from quaestor.agent import (
    MAX_FOLLOW_UP_STEPS,
    PLAN_PURPOSE,
    CompletedCall,
    FollowUpAction,
    PlannedCall,
    PlanStep,
    applicable_tools,
    completed_calls,
    follow_up_plan,
    guidance_queries,
    inapplicable_reason,
    loop_prompt,
    rule_based_plan,
    validate_action,
)
from quaestor.errors import ArtifactError, ToolError
from quaestor.findings import DefectClass, FindingCandidate, Severity
from quaestor.llm import FakeLLM, ScriptedLLM
from quaestor.package import load_package
from quaestor.tools import ToolResult, default_registry
from quaestor.trace import TraceReader, TraceWriter
from quaestor.vocab import SECTION_ORDER

REPO_ROOT = Path(__file__).resolve().parents[1]
CREDIT = REPO_ROOT / "subjects" / "credit_default"
MSR = REPO_ROOT / "subjects" / "msr_prepayment"


def action(**fields: object) -> FollowUpAction:
    """Build one loop action."""
    return FollowUpAction.model_validate(fields)


def scripted(*actions: dict[str, object]) -> ScriptedLLM:
    """A provider that answers the loop with these actions, in order."""
    return ScriptedLLM([json.dumps(item) for item in actions])


# --- the rule-based plan --------------------------------------------------------------------


def test_a_binary_classifier_gets_the_six_checks_and_one_retrieval_per_section() -> None:
    plan = rule_based_plan(load_package(CREDIT), synthetic=5000)
    tools = [call.tool for call in plan]
    assert tools[:6] == [
        "run_model",
        "profile_data",
        "compute_metrics",
        "check_leakage",
        "check_collinearity",
        "challenger_compare",
    ]
    assert tools[6:] == ["retrieve_guidance"] * len(SECTION_ORDER)
    assert "check_stability" not in tools
    assert "run_scenarios" not in tools
    assert plan[0].args == {"synthetic": 5000}
    assert all(call.why for call in plan)
    assert all(call.source == "rules" for call in plan)


def test_a_hazard_subject_with_a_regime_column_adds_stability_and_scenarios() -> None:
    plan = rule_based_plan(load_package(MSR), synthetic=2000)
    tools = [call.tool for call in plan]
    assert "check_stability" in tools
    assert "run_scenarios" in tools
    assert tools.index("check_stability") < tools.index("challenger_compare")
    assert tools.index("run_scenarios") > tools.index("challenger_compare")


def test_the_run_arguments_follow_the_data_mode_and_the_seed() -> None:
    data = rule_based_plan(load_package(CREDIT), data_dir="/data/credit", seed=20260901)
    assert data[0].args == {"data_dir": "/data/credit", "seed": 20260901}
    bare = rule_based_plan(load_package(CREDIT))
    assert bare[0].args == {}


def test_the_baseline_asks_for_no_guidance() -> None:
    plan = rule_based_plan(load_package(CREDIT), synthetic=5000, guidance=False)
    assert "retrieve_guidance" not in [call.tool for call in plan]


def test_every_section_has_a_guidance_query_and_they_are_all_different() -> None:
    queries = guidance_queries()
    assert [section for section, _ in queries] == [section.value for section in SECTION_ORDER]
    assert len({query for _, query in queries}) == len(queries)


# --- what the loop may not do ----------------------------------------------------------------


def test_an_unknown_tool_is_refused_with_the_list_of_the_ones_that_exist() -> None:
    call, reason = validate_action(
        action(tool="check_everything", args={}), default_registry(), load_package(CREDIT)
    )
    assert call is None
    assert "there is no tool named 'check_everything'" in reason
    assert "profile_data" in reason


def test_an_action_that_names_no_tool_is_refused() -> None:
    call, reason = validate_action(
        action(why="i am thinking"), default_registry(), load_package(CREDIT)
    )
    assert call is None
    assert "names no tool" in reason


def test_a_run_model_with_a_different_entrypoint_is_refused_by_the_closed_args_model() -> None:
    """Spec 3.12: "cannot call `run_model` with a different entrypoint"."""
    call, reason = validate_action(
        action(tool="run_model", args={"entrypoint": "python -m evil"}),
        default_registry(),
        load_package(CREDIT),
    )
    assert call is None
    assert "entrypoint" in reason


def test_a_path_outside_the_package_is_refused(tmp_path: Path) -> None:
    """Spec 3.12: "cannot pass paths outside the package".

    The second half is the ordering of D-089: a path *inside* the package passes the path rule and
    is then refused by the applicability rule, because `run_model` is never an offer the loop may
    make. Both refusals are reachable, and each names its own problem.
    """
    call, reason = validate_action(
        action(tool="run_model", args={"data_dir": "/etc"}),
        default_registry(),
        load_package(CREDIT),
    )
    assert call is None
    assert "points outside the package" in reason
    inside, why = validate_action(
        action(tool="run_model", args={"data_dir": str(tmp_path / "data")}),
        default_registry(),
        load_package(CREDIT),
        roots=[tmp_path],
    )
    assert inside is None
    assert "points outside the package" not in why
    assert why.startswith("not applicable to this package:")
    assert "may not run the subject" in why


def test_an_argument_of_the_wrong_shape_is_refused_by_the_tool_itself() -> None:
    call, reason = validate_action(
        action(tool="compute_metrics", args={"splits": "test"}),
        default_registry(),
        load_package(CREDIT),
    )
    assert call is None
    assert "compute_metrics" in reason


# --- the loop -------------------------------------------------------------------------------


def test_a_planner_that_stops_at_once_takes_one_step_and_asks_for_nothing(
    tmp_path: Path,
) -> None:
    trace = TraceWriter(tmp_path / "trace.jsonl", run_id="stop")
    steps = follow_up_plan(
        scripted({"stop": True}), default_registry(), load_package(CREDIT), trace=trace
    )
    assert len(steps) == 1
    assert steps[0].accepted is False
    assert steps[0].reason == "the planner stopped"
    events = TraceReader(trace.path).events("plan_step")
    assert len(events) == 1
    assert events[0].payload["stop"] is True


def test_one_follow_up_then_stop_executes_exactly_one_call(tmp_path: Path) -> None:
    executed: list[PlannedCall] = []
    steps = follow_up_plan(
        scripted(
            {"tool": "profile_data", "args": {"splits": ["test"]}, "why": "look again"},
            {"stop": True},
        ),
        default_registry(),
        load_package(CREDIT),
        execute=executed.append,
    )
    assert [step.accepted for step in steps] == [True, False]
    assert [call.tool for call in executed] == ["profile_data"]
    assert executed[0].why == "look again"


def test_a_refused_action_does_not_stop_the_loop_and_is_never_executed(tmp_path: Path) -> None:
    executed: list[PlannedCall] = []
    trace = TraceWriter(tmp_path / "trace.jsonl", run_id="refused")
    steps = follow_up_plan(
        scripted({"tool": "nope", "args": {}, "why": "x"}, {"stop": True}),
        default_registry(),
        load_package(CREDIT),
        trace=trace,
        execute=executed.append,
    )
    assert [step.accepted for step in steps] == [False, False]
    assert executed == []
    events = TraceReader(trace.path).events("plan_step")
    assert events[0].payload["accepted"] is False
    assert "no tool named" in events[0].payload["reason"]


def test_the_loop_is_bounded_at_four_steps(tmp_path: Path) -> None:
    llm = FakeLLM(default=json.dumps({"tool": "profile_data", "args": {}, "why": "again"}))
    steps = follow_up_plan(llm, default_registry(), load_package(CREDIT), execute=lambda call: None)
    assert len(steps) == MAX_FOLLOW_UP_STEPS
    assert all(step.accepted for step in steps)


def test_the_loop_is_shown_the_candidates_the_schemas_and_what_is_in_the_store() -> None:
    llm = ScriptedLLM([json.dumps({"stop": True})])
    candidate = FindingCandidate(
        defect_class=DefectClass.E1,
        evidence=["4bb1344e"],
        detail="the challenger leads the champion",
        suggested_severity=Severity.low,
        tool="challenger_compare",
    )
    follow_up_plan(
        llm,
        default_registry(),
        load_package(CREDIT),
        candidates=[candidate],
        artifact_names=["metrics.test.auc", "metrics.train.auc", "psi.max"],
    )
    prompt = llm.calls[0].prompt
    assert "E1 (effective challenge, from challenger_compare)" in prompt
    assert candidate.detail in prompt
    assert "metrics (2), psi (1)" in prompt
    assert '"tool": "compute_metrics"' in prompt
    assert "subpopulation" in prompt
    assert "at most 4 more tool call(s)" in prompt


def test_the_loop_records_one_llm_call_per_step(tmp_path: Path) -> None:
    trace = TraceWriter(tmp_path / "trace.jsonl", run_id="calls")
    follow_up_plan(
        scripted({"tool": "profile_data", "args": {}, "why": "again"}, {"stop": True}),
        default_registry(),
        load_package(CREDIT),
        trace=trace,
        execute=lambda call: None,
    )
    events = TraceReader(trace.path).events("llm_call")
    assert [event.payload["purpose"] for event in events] == [PLAN_PURPOSE, PLAN_PURPOSE]
    assert [event.payload["step"] for event in events] == [1, 2]


def test_the_loop_shows_the_next_step_what_the_last_one_produced() -> None:
    """The point of executing inside the loop: step two knows what step one stored."""

    class Result:
        artifact_names = ["metrics.test.sub.limit_bal_low.auc"]

    llm = ScriptedLLM(
        [
            json.dumps({"tool": "profile_data", "args": {}, "why": "one"}),
            json.dumps({"stop": True}),
        ]
    )
    follow_up_plan(
        llm,
        default_registry(),
        load_package(CREDIT),
        artifact_names=["psi.max"],
        execute=lambda call: Result(),
    )
    assert "psi (1)" in llm.calls[0].prompt
    assert "metrics (1)" in llm.calls[1].prompt


@pytest.mark.parametrize("bad", ["stop", 3, None])
def test_an_action_that_is_not_the_schema_is_re_asked_and_then_raises(bad: object) -> None:
    from quaestor.errors import LLMOutputError

    llm = FakeLLM(default=json.dumps(bad))
    with pytest.raises(LLMOutputError):
        follow_up_plan(llm, default_registry(), load_package(CREDIT))


# --- the applicability filter (D-089) ---------------------------------------------------------


def test_the_menu_offers_only_the_tools_the_package_supports() -> None:
    """`run_model` never, `check_stability` and `run_scenarios` only where they can answer."""
    registry = default_registry()
    credit = applicable_tools(registry, load_package(CREDIT))
    msr = applicable_tools(registry, load_package(MSR))

    assert "run_model" not in credit
    assert "run_model" not in msr
    assert "check_stability" not in credit
    assert "run_scenarios" not in credit
    assert "check_stability" in msr
    assert "run_scenarios" in msr
    assert set(msr) - set(credit) == {"check_stability", "run_scenarios"}
    assert set(credit) < set(registry.names())


def test_the_prompt_lists_the_applicable_schemas_and_no_others() -> None:
    registry = default_registry()
    credit = loop_prompt(registry, load_package(CREDIT), remaining=4)
    msr = loop_prompt(registry, load_package(MSR), remaining=4)

    assert '"tool": "run_model"' not in credit
    assert '"tool": "run_model"' not in msr
    assert '"tool": "check_stability"' not in credit
    assert '"tool": "run_scenarios"' not in credit
    assert '"tool": "check_stability"' in msr
    assert '"tool": "run_scenarios"' in msr
    assert "Only the tools that apply to" in credit


def test_a_tool_that_exists_but_does_not_apply_is_refused_before_it_runs() -> None:
    """The second live attempt's action, decided by the rule that would have refused it."""
    registry = default_registry()
    call, reason = validate_action(
        action(tool="check_stability", args={"split": "test"}, why="regimes out of sample"),
        registry,
        load_package(CREDIT),
    )
    assert call is None
    assert reason.startswith("not applicable to this package:")
    assert "declares no `regime.column`" in reason

    scenarios, why = validate_action(
        action(tool="run_scenarios", args={}), registry, load_package(CREDIT)
    )
    assert scenarios is None
    assert why.startswith("not applicable to this package:")
    assert "no projection to shock" in why

    allowed, ok = validate_action(
        action(tool="check_stability", args={"split": "test"}), registry, load_package(MSR)
    )
    assert ok == ""
    assert isinstance(allowed, PlannedCall)


def test_an_applicable_tool_has_no_reason_and_an_unknown_name_is_not_this_rule_s_business() -> None:
    package = load_package(CREDIT)
    assert inapplicable_reason("profile_data", package) == ""
    assert inapplicable_reason("check_everything", package) == ""


def test_the_inapplicable_refusal_is_traced_and_fed_back_to_the_next_step(tmp_path: Path) -> None:
    """D-089 plus D-090: refused, recorded, and quoted in the prompt of the step after it."""
    executed: list[PlannedCall] = []
    trace = TraceWriter(tmp_path / "trace.jsonl", run_id="inapplicable")
    llm = scripted(
        {"tool": "check_stability", "args": {"split": "test"}, "why": "regimes"},
        {"stop": True},
    )
    steps = follow_up_plan(
        llm,
        default_registry(),
        load_package(CREDIT),
        trace=trace,
        execute=executed.append,
    )
    assert [step.accepted for step in steps] == [False, False]
    assert [step.executed for step in steps] == [False, False]
    assert executed == []
    assert steps[0].reason.startswith("not applicable to this package:")

    events = TraceReader(trace.path).events("plan_step")
    assert events[0].payload["accepted"] is False
    assert events[0].payload["executed"] is False
    assert "not applicable to this package:" in events[0].payload["reason"]
    assert events[0].payload["error"] == ""

    second = llm.calls[1].prompt
    assert "What earlier steps of this loop did:" in second
    assert 'step 1: check_stability({"split": "test"}) was refused: not applicable' in second


# --- a tool that raises (D-088) ---------------------------------------------------------------


def test_an_accepted_call_whose_tool_raises_is_recorded_and_does_not_end_the_run(
    tmp_path: Path,
) -> None:
    """The defect of the second live attempt: the loop asked, the tool raised, the run died."""
    asked: list[str] = []
    trace = TraceWriter(tmp_path / "trace.jsonl", run_id="raised")

    def explode(call: PlannedCall) -> ToolResult:
        asked.append(call.tool)
        raise ToolError("the regime column 'month' is not in data_test.csv")

    llm = scripted(
        {"tool": "profile_data", "args": {"splits": ["test"]}, "why": "look again"},
        {"stop": True},
    )
    steps = follow_up_plan(
        llm, default_registry(), load_package(CREDIT), trace=trace, execute=explode
    )

    assert asked == ["profile_data"]
    assert steps[0].accepted is True
    assert steps[0].executed is False
    assert steps[0].error == "the regime column 'month' is not in data_test.csv"
    assert steps[0].reason == ""
    assert steps[0].call is not None
    assert [step.accepted for step in steps] == [True, False]

    events = TraceReader(trace.path).events("plan_step")
    assert events[0].payload["accepted"] is True
    assert events[0].payload["executed"] is False
    assert events[0].payload["error"] == "the regime column 'month' is not in data_test.csv"

    second = llm.calls[1].prompt
    assert "was accepted and the tool failed: the regime column" in second


def test_a_call_that_raises_still_counts_against_the_bound() -> None:
    """Four failures are four steps: a tool that raises does not buy the loop another turn."""

    def explode(call: PlannedCall) -> ToolResult:
        raise ToolError("nothing to profile")

    llm = FakeLLM(default=json.dumps({"tool": "profile_data", "args": {}, "why": "again"}))
    steps = follow_up_plan(llm, default_registry(), load_package(CREDIT), execute=explode)
    assert len(steps) == MAX_FOLLOW_UP_STEPS
    assert all(step.accepted and not step.executed and step.error for step in steps)


def test_a_step_the_loop_only_planned_is_accepted_and_not_executed() -> None:
    """With no executor nothing runs, so `executed` is false and no error is invented."""
    steps = follow_up_plan(
        scripted({"tool": "profile_data", "args": {}, "why": "one"}, {"stop": True}),
        default_registry(),
        load_package(CREDIT),
    )
    assert steps[0].accepted is True
    assert steps[0].executed is False
    assert steps[0].error == ""


# --- what the plan already did (D-090) --------------------------------------------------------


def test_the_prompt_lists_the_rule_based_plan_s_calls_and_what_they_raised() -> None:
    prompt = loop_prompt(
        default_registry(),
        load_package(CREDIT),
        remaining=4,
        completed=[
            CompletedCall("run_model", {"synthetic": 600}, ()),
            CompletedCall("check_leakage", {}, ["L2"]),
        ],
    )
    assert "Calls the rule-based plan has already made" in prompt
    assert '- run_model({"synthetic": 600}) -> no candidate' in prompt
    assert "- check_leakage({}) -> L2" in prompt
    assert "not for repeating the plan" in prompt


def test_a_configuration_that_ran_no_check_says_so_rather_than_showing_an_empty_list() -> None:
    prompt = loop_prompt(default_registry(), load_package(CREDIT), remaining=1)
    assert "(none: this configuration ran no rule-based check)" in prompt


def test_completed_calls_pairs_the_plan_with_its_results() -> None:
    plan = rule_based_plan(load_package(CREDIT), synthetic=600)[:2]
    results = [ToolResult(tool="run_model"), ToolResult(tool="profile_data")]
    paired = completed_calls(plan, results)
    assert [call.tool for call in paired] == ["run_model", "profile_data"]
    assert paired[0].args == {"synthetic": 600}
    assert paired[0].classes == []
    short = completed_calls(plan, results[:1])
    assert short == [CompletedCall("run_model", {"synthetic": 600}, [])]


def test_the_loop_is_sent_exactly_what_loop_prompt_builds() -> None:
    """The prompt is one function, so a test can reproduce a recorded call's bytes."""
    llm = ScriptedLLM([json.dumps({"stop": True})])
    package = load_package(CREDIT)
    completed = [CompletedCall("run_model", {"synthetic": 600}, ())]
    follow_up_plan(
        llm,
        default_registry(),
        package,
        completed=completed,
        artifact_names=["psi.max"],
    )
    assert llm.calls[0].prompt.startswith(
        loop_prompt(
            default_registry(),
            package,
            remaining=MAX_FOLLOW_UP_STEPS,
            completed=completed,
            artifact_names=["psi.max"],
        )
    )


def test_a_step_that_named_no_tool_contributes_no_history_line() -> None:
    """The stop step ends the loop, so it is never fed back as something that was asked for."""
    stopped = PlanStep(1, action(stop=True), False, "the planner stopped")
    prompt = loop_prompt(default_registry(), load_package(CREDIT), remaining=4, history=[stopped])
    assert "What earlier steps of this loop did:" not in prompt
    assert "step 1" not in prompt


# --- the loop is shown the data's own column names (DECISIONS D-107) ----------------------------


def test_the_prompt_lists_the_columns_a_sub_population_can_be_selected_on() -> None:
    """The fourth live run spent a step and a tool call on a column name that does not exist."""
    prompt = loop_prompt(
        default_registry(),
        load_package(CREDIT),
        remaining=4,
        data_columns=["client_id", "limit_bal", "delinq_count_6m", "default_next_month"],
    )
    assert "`limit_bal`" in prompt
    assert "`delinq_count_6m`" in prompt
    assert "does not exist" in prompt


def test_a_configuration_with_no_data_says_so_rather_than_showing_an_empty_list() -> None:
    prompt = loop_prompt(default_registry(), load_package(CREDIT), remaining=4)
    assert "(none: this configuration ran no subject" in prompt


# --- a loop step refused for a name collision costs the step, not the run (D-190) --------------


COLLISION = (
    "the logical name 'stability.auc_by_regime' already holds artifact 960f708fa38d007d and "
    "cannot be replaced by f8a99daaffa18678"
)
"""The message that ended a paid `full_agent` cell twenty-nine seconds in."""


def _raising(error: Exception) -> Callable[[PlannedCall], None]:
    """An `execute` that refuses every call the loop makes."""

    def execute(_call: PlannedCall) -> None:
        raise error

    return execute


def test_an_artifact_collision_in_a_loop_step_costs_the_step_and_not_the_run(
    tmp_path: Path,
) -> None:
    """D-088's stated intent, with the exception type it did not cover.

    A `full_agent` cell was lost to this. The loop asked `check_stability` for `split: test` after
    the checklist had run it on the fitting split -- a correct and useful request, an out-of-sample
    regime check the in-sample run could hide -- and the tool's artifact names carry no split, so
    the second call tried to rebind `stability.auc_by_regime`. `ArtifactError` is not a `ToolError`,
    so it went straight past the loop's guard and ended a run that had already been paid for.
    """
    trace = TraceWriter(tmp_path / "trace.jsonl", run_id="collision")
    steps = follow_up_plan(
        scripted(
            {"tool": "check_stability", "args": {"split": "test"}, "why": "out-of-sample regime"},
            {"stop": True},
        ),
        default_registry(),
        load_package(MSR),
        trace=trace,
        execute=_raising(ArtifactError(COLLISION)),
    )
    assert [step.accepted for step in steps] == [True, False]
    assert steps[0].executed is False
    assert "stability.auc_by_regime" in steps[0].error
    event = TraceReader(trace.path).events("plan_step")[0]
    assert event.payload["executed"] is False
    assert "stability.auc_by_regime" in event.payload["error"]


def test_a_tool_error_in_a_loop_step_is_what_it_always_was() -> None:
    """The guard D-088 wrote still does exactly what it did; D-190 only widens the type."""
    steps = follow_up_plan(
        scripted(
            {"tool": "check_stability", "args": {"split": "test"}, "why": "x"},
            {"stop": True},
        ),
        default_registry(),
        load_package(MSR),
        execute=_raising(ToolError("the split has one row")),
    )
    assert steps[0].accepted and steps[0].executed is False
    assert steps[0].error == "the split has one row"


def test_the_loop_goes_on_to_its_next_step_after_a_collision() -> None:
    """The point of the whole change: the run keeps what it has already paid for."""
    steps = follow_up_plan(
        scripted(
            {"tool": "check_stability", "args": {"split": "test"}, "why": "collides"},
            {"tool": "profile_data", "args": {"splits": ["test"]}, "why": "still useful"},
            {"stop": True},
        ),
        default_registry(),
        load_package(MSR),
        max_steps=3,
        execute=_raising(ArtifactError(COLLISION)),
    )
    assert [step.accepted for step in steps] == [True, True, False]
    assert [step.action.tool for step in steps[:2]] == ["check_stability", "profile_data"]
    assert steps[0].executed is False and "stability.auc_by_regime" in steps[0].error
