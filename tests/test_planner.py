"""Phase 8: the rule-based plan, and the three things the bounded loop is not allowed to do.

Spec 3.12. The plan is a function of `package.yaml` and nothing else, so both shipped subjects are
planned here and the difference between them is asserted rather than described: a hazard subject
with a regime column gets two checks a binary classifier does not.

The loop's refusals are the other half. An action naming an unknown tool, an action whose arguments
the tool's own `Args` model rejects -- which is where an invented `entrypoint` is caught, because
every `Args` is closed -- and an action pointing a path outside the package are refused *before*
anything runs, and each refusal is a `plan_step` event a reader can find in the trace.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from quaestor.agent import (
    MAX_FOLLOW_UP_STEPS,
    PLAN_PURPOSE,
    FollowUpAction,
    PlannedCall,
    follow_up_plan,
    guidance_queries,
    rule_based_plan,
    validate_action,
)
from quaestor.findings import DefectClass, FindingCandidate, Severity
from quaestor.llm import FakeLLM, ScriptedLLM
from quaestor.package import load_package
from quaestor.tools import default_registry
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
    """Spec 3.12: "cannot pass paths outside the package"."""
    call, reason = validate_action(
        action(tool="run_model", args={"data_dir": "/etc"}),
        default_registry(),
        load_package(CREDIT),
    )
    assert call is None
    assert "points outside the package" in reason
    inside, ok = validate_action(
        action(tool="run_model", args={"data_dir": str(tmp_path / "data")}),
        default_registry(),
        load_package(CREDIT),
        roots=[tmp_path],
    )
    assert ok == ""
    assert isinstance(inside, PlannedCall)
    assert inside.source == "loop"


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
