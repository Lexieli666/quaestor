"""The second live validation: one plan call, one inapplicable request, and an abort.

`eval/results/first-live/credit-attempt2/` is the record of the run of 2026-09-08 that never
reached the drafter. The rule-based plan ran clean -- 13 calls, no candidate, the `L2` false alarm
of D-086 gone -- and then the bounded loop asked for `check_stability` on a package that declares
no `regime.column`. The tool raised, and the exception left `validate()` as exit 1: 14 tool calls,
one model call, no report. `docs/EVALUATION.md` section 1 writes the run up; this module is the
half of the write-up a machine checks.

Nothing here calls a model. The first test reads the trace. The second replays the run's one
cassette through `ReplayLLM` and puts the live model's own answer back into the loop, where it is
now refused as inapplicable (D-089) and the pipeline goes on to render (D-088).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Final

import pytest

from quaestor import Configuration, TraceReader, validate
from quaestor.llm import Completion, ReplayLLM
from quaestor.llm.offline import prompt_kind
from quaestor.pipeline import ValidationRun
from quaestor.report import check_report
from reportsupport import SectionFake

REPO_ROOT: Final = Path(__file__).resolve().parents[1]
CREDIT: Final = REPO_ROOT / "subjects" / "credit_default"
ATTEMPT: Final = REPO_ROOT / "eval" / "results" / "first-live" / "credit-attempt2"
"""The committed record of the run this module is about."""

CASSETTE: Final = ATTEMPT / "cassettes" / "d477a0f0034266b8.json"
"""Its one tape: the single plan call, whose answer is the whole of the attempt's agency."""

ROW_LEVEL: Final = (
    "run.data_train",
    "run.data_test",
    "run.predictions_train",
    "run.predictions_test",
)
"""The four artifacts whose payload the repository deliberately does not hold (D-087)."""

SMALL: Final = 1200
"""Rows for the replay run: enough for every tool, small enough to run once in a test."""


def _events() -> list[Any]:
    """Every event of the attempt's trace, in file order."""
    return list(TraceReader(ATTEMPT / "trace.jsonl"))


class TapedPlan:
    """The offline fake, with the bounded loop's first answer taken off attempt 2's own tape.

    The tape is served by :class:`~quaestor.llm.ReplayLLM` under the key it was recorded with --
    the recorded prompt, read back out of the cassette -- and not under the key of the prompt the
    loop sends today, because a cassette's key is a hash of the request and D-089 and D-090
    changed that request on purpose. What is replayed is the live model's answer, byte for byte;
    what is not replayed is the question, which this build no longer asks the same way.

    Attributes:
        name: What the report records as the model: a replay of the recorded provider, over a
            fake for every call the attempt never made.
        replay: The provider reading `credit-attempt2/cassettes/`.
        recorded: The prompt the attempt's plan call was sent, which is that tape's key.
        plan_calls: How many plan calls have been made.
    """

    def __init__(self) -> None:
        """Open the attempt's cassette directory and read the recorded request back."""
        self.replay = ReplayLLM(ATTEMPT / "cassettes")
        self.recorded = str(json.loads(CASSETTE.read_text(encoding="utf-8"))["request"]["prompt"])
        self.fake = SectionFake()
        self.plan_calls = 0
        self.name = f"replay({self.replay.name})+fake"

    def complete(self, prompt: str, *, system: str | None = None, **params: Any) -> Completion:
        """Answer the first plan call from the tape and every other call from the offline fake.

        Args:
            prompt: The user-turn text.
            system: The system prompt, when the caller has one.
            **params: Passed to the fake; the tape is served with the parameters it was recorded
                with, which is what its key is over.

        Returns:
            The recorded completion for the first plan call, the fake's answer otherwise.
        """
        if prompt_kind(prompt) == "plan":
            self.plan_calls += 1
            if self.plan_calls == 1:
                return self.replay.complete(self.recorded)
        return self.fake.complete(prompt, system=system, **params)


@pytest.fixture(scope="module")
def replayed(tmp_path_factory: pytest.TempPathFactory) -> tuple[TapedPlan, ValidationRun]:
    """One `full_agent` run whose plan step is the attempt's recorded answer."""
    llm = TapedPlan()
    run = validate(
        CREDIT,
        llm=llm,
        config=Configuration.full_agent,
        synthetic=SMALL,
        out=tmp_path_factory.mktemp("attempt2") / "out",
        quaestor_version="0.1.0.dev0",
    )
    return llm, run


def test_the_attempt_s_record_is_the_run_the_write_up_describes() -> None:
    """Every number `docs/EVALUATION.md` quotes for this attempt comes from this trace.

    `CLAUDE.md`: no number in the documentation that a committed run did not produce.
    """
    events = _events()
    tools = [event for event in events if event.type == "tool_call"]
    calls = [event for event in events if event.type == "llm_call"]
    steps = [event for event in events if event.type == "plan_step"]

    assert len(events) == 16
    assert len(tools) == 14
    assert len(calls) == 1
    assert len(steps) == 1

    # The plan: 13 calls, every one clean, and no `L2` -- the run was made after D-086.
    assert [event.payload["ok"] for event in tools] == [True] * 13 + [False]
    assert all(event.payload["candidates"] == [] for event in tools)
    assert [event for event in events if event.type == "finding"] == []
    assert round(sum(float(event.payload["duration_s"]) for event in tools), 2) == 2.69
    assert sum(len(event.payload["artifacts"]) for event in tools) == 124

    # The one model call.
    assert calls[0].payload["purpose"] == "plan"
    assert calls[0].payload["schema"] == "FollowUpAction"
    assert calls[0].payload["model"] == "claude-opus-5[1m]"
    assert int(calls[0].payload["tokens_out"]) == 693
    assert float(calls[0].payload["cost_usd"]) == 0.10093
    assert round(float(calls[0].payload["latency_ms"]) / 1000, 1) == 13.0
    assert round((events[-1].ts - events[0].ts).total_seconds(), 2) == 15.09

    # The step that killed the run: accepted, then the tool raised.
    assert steps[0].payload["tool"] == "check_stability"
    assert steps[0].payload["args"] == {"split": "test"}
    assert steps[0].payload["accepted"] is True
    assert steps[0].payload["reason"] == ""
    assert tools[-1].payload["tool"] == "check_stability"
    assert tools[-1].payload["artifacts"] == []
    assert not list((ATTEMPT).glob("report.md"))

    # The trace of a build that had not yet been fixed records no `executed` field at all.
    assert "executed" not in steps[0].payload


def test_the_committed_record_holds_no_row_of_the_real_sample() -> None:
    """D-087's rule, applied to the second attempt: a complete index, four absent payloads."""
    index = json.loads((ATTEMPT / "artifacts" / "index.json").read_text(encoding="utf-8"))
    entries = index["artifacts"]
    assert len(entries) == 124
    for name in ROW_LEVEL:
        assert name in entries
        assert not (ATTEMPT / "artifacts" / entries[name]["file"]).exists()
    absent = {
        name
        for name, entry in entries.items()
        if not (ATTEMPT / "artifacts" / entry["file"]).exists()
    }
    assert absent == set(ROW_LEVEL)
    assert not list((ATTEMPT / "run").glob("*.csv"))
    assert {path.name for path in (ATTEMPT / "run").iterdir()} == {
        "splits.json",
        "features.json",
        "metrics.json",
        "model_summary.json",
    }


def test_the_recorded_answer_is_the_action_the_attempt_died_on() -> None:
    """The tape says what the model asked for; the trace says what happened to it."""
    cassette = json.loads(CASSETTE.read_text(encoding="utf-8"))
    assert cassette["provider"] == "claude-cli"
    assert cassette["calls"] == 1
    answer = json.loads(str(cassette["completion"]["text"]))
    assert answer["tool"] == "check_stability"
    assert answer["args"] == {"split": "test"}
    assert answer["why"]
    assert int(cassette["completion"]["tokens_out"]) == 693
    assert int(cassette["completion"]["tokens_in"]) == 2
    usage = cassette["completion"]["raw"]["usage"]
    assert int(usage["output_tokens_details"]["thinking_tokens"]) == 628


def test_the_attempt_s_answer_replayed_no_longer_aborts(
    replayed: tuple[TapedPlan, ValidationRun],
) -> None:
    """The whole point: the same answer, this build, a rendered report.

    `check_stability` is not on the menu this package is offered, so the request is refused before
    anything runs, with the reason the model is told on the next step (D-089); the pipeline goes on
    to draft, verify, repair and render (D-088). The attempt's exit 1 becomes a report.
    """
    llm, run = replayed

    assert llm.replay.served == ["d477a0f0034266b8"]
    assert llm.plan_calls == 2

    assert run.steps[0].action.tool == "check_stability"
    assert run.steps[0].action.args == {"split": "test"}
    assert run.steps[0].accepted is False
    assert run.steps[0].executed is False
    assert run.steps[0].reason.startswith("not applicable to this package:")
    assert "declares no `regime.column`" in run.steps[0].reason
    assert run.steps[1].reason == "the planner stopped"

    calls = TraceReader(run.out_dir / "trace.jsonl").events("tool_call")
    assert all(event.payload["tool"] != "check_stability" for event in calls)

    assert run.report_path.is_file()
    assert (
        check_report(
            run.report,
            run.configuration,
            run.claims.post_repair,
            package_version=run.package.spec.version,
        )
        == []
    )
    assert run.precision_post == 1.0
    assert "`check_stability` (R1)" in run.report
