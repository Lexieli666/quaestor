"""`structured()` re-asks exactly once, then raises with the raw text. Both halves are the test.

Spec section 3.5's acceptance criterion. The re-ask count is a quality signal the study reports, so
"exactly once" is asserted by counting calls rather than by asserting that the result is right, and
the `reask` trace event is asserted because that is where the count comes from.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel, Field

from quaestor.errors import LLMOutputError
from quaestor.llm import Completion, FakeLLM, ScriptedLLM, strip_fence, structured
from quaestor.trace import EventType, TraceReader, TraceWriter


class Section(BaseModel):
    markdown: str
    n_citations: int = Field(ge=0)


GOOD = '{"markdown": "AUC is 0.7412 [[art:4bb1344e:metrics.test.auc]]", "n_citations": 1}'
BAD_JSON = "Sure! Here is the section you asked for."
BAD_SHAPE = '{"markdown": "no citations", "n_citations": -1}'


def writer(tmp_path: Path) -> TraceWriter:
    return TraceWriter(
        tmp_path / "trace.jsonl",
        run_id="run-0001",
        clock=lambda: datetime(2026, 9, 7, tzinfo=UTC),
    )


def test_a_valid_answer_is_returned_on_the_first_call() -> None:
    llm = FakeLLM(default=GOOD)
    section = structured(llm, "draft section 4", Section)
    assert section.n_citations == 1
    assert llm.call_count == 1


def test_the_prompt_carries_the_schema_and_the_strict_json_instruction() -> None:
    llm = FakeLLM(default=GOOD)
    structured(llm, "draft section 4", Section)
    prompt = llm.calls[0].prompt
    assert prompt.startswith("draft section 4")
    assert "one JSON object and nothing else" in prompt
    assert '"n_citations"' in prompt


def test_the_system_prompt_and_params_are_passed_through() -> None:
    llm = FakeLLM(default=GOOD)
    structured(llm, "p", Section, system="you validate models", model="claude-opus-5")
    assert llm.calls[0].system == "you validate models"
    assert llm.calls[0].params == {"model": "claude-opus-5"}


def test_one_fenced_block_is_stripped() -> None:
    llm = FakeLLM(default=f"```json\n{GOOD}\n```")
    assert structured(llm, "p", Section).n_citations == 1


def test_a_bare_fence_is_stripped() -> None:
    assert strip_fence("```\n{}\n```") == "{}"


def test_a_fence_that_does_not_wrap_the_whole_answer_is_left_alone() -> None:
    text = "here you go:\n```json\n{}\n```"
    assert strip_fence(text) == text


def test_unparsable_json_is_re_asked_exactly_once_and_then_succeeds() -> None:
    llm = ScriptedLLM([BAD_JSON, GOOD])
    assert structured(llm, "p", Section).n_citations == 1
    assert llm.call_count == 2


def test_a_valid_json_object_of_the_wrong_shape_is_re_asked() -> None:
    llm = ScriptedLLM([BAD_SHAPE, GOOD])
    assert structured(llm, "p", Section).n_citations == 1
    assert llm.call_count == 2


def test_the_re_ask_quotes_the_validation_error() -> None:
    llm = ScriptedLLM([BAD_SHAPE, GOOD])
    structured(llm, "draft section 4", Section)
    reask = llm.calls[1].prompt
    assert "Your previous answer was rejected" in reask
    assert "n_citations" in reask
    assert "greater than or equal to 0" in reask
    assert reask.startswith("draft section 4")


def test_the_re_ask_quotes_the_beginning_of_unparsable_text() -> None:
    llm = ScriptedLLM([BAD_JSON, GOOD])
    structured(llm, "p", Section)
    assert "it is not JSON" in llm.calls[1].prompt
    assert "Sure! Here is" in llm.calls[1].prompt


def test_two_failures_raise_with_the_raw_text() -> None:
    llm = ScriptedLLM([BAD_JSON])
    with pytest.raises(LLMOutputError, match="did not return a valid Section in 2 attempt") as e:
        structured(llm, "p", Section)
    assert e.value.raw == BAD_JSON
    assert llm.call_count == 2


def test_the_raw_text_of_the_last_attempt_is_the_one_carried() -> None:
    llm = ScriptedLLM([BAD_JSON, BAD_SHAPE])
    with pytest.raises(LLMOutputError) as caught:
        structured(llm, "p", Section)
    assert caught.value.raw == BAD_SHAPE


def test_max_attempts_of_one_disables_the_re_ask() -> None:
    llm = ScriptedLLM([BAD_JSON, GOOD])
    with pytest.raises(LLMOutputError, match="in 1 attempt"):
        structured(llm, "p", Section, max_attempts=1)
    assert llm.call_count == 1


def test_max_attempts_below_one_is_a_programming_error() -> None:
    with pytest.raises(ValueError, match="at least 1"):
        structured(FakeLLM(default=GOOD), "p", Section, max_attempts=0)


# --- the trace -----------------------------------------------------------------------------------


def test_the_first_call_is_traced_with_the_callers_purpose(tmp_path: Path) -> None:
    trace = writer(tmp_path)
    structured(FakeLLM(default=GOOD), "p", Section, trace=trace, purpose="draft")
    (event,) = TraceReader(tmp_path / "trace.jsonl").events(EventType.llm_call)
    assert event.payload["purpose"] == "draft"
    assert event.payload["schema"] == "Section"
    assert event.payload["attempt"] == 1
    assert event.payload["model"] == "fake-1"


def test_every_re_ask_is_an_llm_call_event_with_purpose_reask(tmp_path: Path) -> None:
    # This is how `eval/score.py` counts re-asks, so it is asserted on the file, not the return.
    trace = writer(tmp_path)
    structured(ScriptedLLM([BAD_JSON, GOOD]), "p", Section, trace=trace, purpose="extract")
    events = TraceReader(tmp_path / "trace.jsonl").events(EventType.llm_call)
    assert [e.payload["purpose"] for e in events] == ["extract", "reask"]
    assert [e.payload["attempt"] for e in events] == [1, 2]


def test_a_failed_call_is_traced_before_it_raises(tmp_path: Path) -> None:
    trace = writer(tmp_path)
    with pytest.raises(LLMOutputError):
        structured(ScriptedLLM([BAD_JSON]), "p", Section, trace=trace)
    assert len(TraceReader(tmp_path / "trace.jsonl").events(EventType.llm_call)) == 2


def test_no_trace_writer_is_fine(tmp_path: Path) -> None:
    assert structured(FakeLLM(default=GOOD), "p", Section).markdown.startswith("AUC")


def test_adapter_provenance_reaches_the_llm_call_event(tmp_path: Path) -> None:
    # A published run has to be able to say whether the Claude CLI was invoked with --bare. The
    # adapter puts it on `raw` under the `quaestor_` prefix and `structured()` copies that prefix
    # across without knowing what any of the keys mean (D-025).
    class ProvenancedLLM:
        name = "provenanced"

        def complete(self, prompt: str, *, system: str | None = None, **params: Any) -> Completion:
            return Completion(
                text=GOOD,
                model="claude-cli",
                raw={"quaestor_bare": False, "session_id": "not copied"},
            )

    trace = writer(tmp_path)
    structured(ProvenancedLLM(), "p", Section, trace=trace, purpose="draft")
    (event,) = TraceReader(tmp_path / "trace.jsonl").events(EventType.llm_call)
    assert event.payload["quaestor_bare"] is False
    assert "session_id" not in event.payload


def test_trace_fields_reach_the_event_and_not_the_provider(tmp_path: Path) -> None:
    """A drafter records which section it was drafting; a provider is never handed a `section`."""
    llm = FakeLLM(default=GOOD)
    trace = writer(tmp_path)
    structured(
        llm,
        "one section please",
        Section,
        trace=trace,
        purpose="draft",
        trace_fields={"section": "outcomes", "repair": False},
    )
    event = TraceReader(trace.path).events("llm_call")[0]
    assert event.payload["section"] == "outcomes"
    assert event.payload["repair"] is False
    assert llm.calls[0].params == {}
