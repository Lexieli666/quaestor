"""`trace.jsonl` is what `eval/score.py` reads instead of prose, so its shape is load-bearing.

The tests here pin three things: the envelope (`schema_version`, `ts`, `run_id`, `type`) is on
every line, the type-specific fields are at the top level of the JSON rather than nested, and a
malformed line is an error naming the file and the line number rather than a silently skipped
event. A study that silently skips events under-counts, which is the failure mode that would be
invisible in the published numbers.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from quaestor.errors import QuaestorError
from quaestor.trace import SCHEMA_VERSION, EventType, TraceEvent, TraceReader, TraceWriter

FIXED = datetime(2026, 9, 7, 12, 0, 0, tzinfo=UTC)


def writer(tmp_path: Path, run_id: str = "run-0001") -> TraceWriter:
    return TraceWriter(tmp_path / "trace.jsonl", run_id=run_id, clock=lambda: FIXED)


def test_every_event_type_of_the_spec_exists() -> None:
    assert {member.value for member in EventType} == {
        "tool_call",
        "llm_call",
        "plan_step",
        "claim_check",
        "repair",
        "finding",
    }


def test_emit_writes_one_line_per_event(tmp_path: Path) -> None:
    trace = writer(tmp_path)
    trace.emit(EventType.plan_step, step=1, tool="run_model")
    trace.emit(EventType.plan_step, step=2, tool="profile_data")
    lines = (tmp_path / "trace.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert trace.count == 2


def test_the_envelope_and_the_payload_are_both_top_level(tmp_path: Path) -> None:
    trace = writer(tmp_path)
    trace.emit(EventType.tool_call, tool="profile_data", args_hash="abcd1234", duration_s=1.5)
    record = json.loads((tmp_path / "trace.jsonl").read_text(encoding="utf-8").strip())
    assert record["schema_version"] == SCHEMA_VERSION
    assert record["run_id"] == "run-0001"
    assert record["type"] == "tool_call"
    assert record["ts"] == FIXED.isoformat()
    assert record["tool"] == "profile_data"
    assert record["duration_s"] == 1.5


def test_a_string_event_type_is_accepted(tmp_path: Path) -> None:
    event = writer(tmp_path).emit("finding", defect_class="E1")
    assert event.type is EventType.finding


def test_an_unknown_event_type_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="not a valid EventType"):
        writer(tmp_path).emit("guessing")


def test_a_field_colliding_with_the_envelope_is_rejected(tmp_path: Path) -> None:
    # Allowing it would produce a line whose `run_id` a reader cannot attribute.
    with pytest.raises(QuaestorError, match=r"collide with the envelope"):
        writer(tmp_path).emit(EventType.repair, run_id="somebody-elses-run")


def test_llm_call_records_the_fields_the_study_counts(tmp_path: Path) -> None:
    trace = writer(tmp_path)
    trace.llm_call(
        purpose="reask",
        model="claude-cli",
        tokens_in=469,
        tokens_out=14,
        cost_usd=0.00377,
        latency_ms=2211.0,
        schema="Claim",
    )
    event = TraceReader(tmp_path / "trace.jsonl").events(EventType.llm_call)[0]
    assert event.payload["purpose"] == "reask"
    assert event.payload["tokens_in"] == 469
    assert event.payload["cost_usd"] == pytest.approx(0.00377)
    assert event.payload["schema"] == "Claim"


def test_the_writer_appends_rather_than_truncating(tmp_path: Path) -> None:
    writer(tmp_path).emit(EventType.finding, defect_class="E1")
    writer(tmp_path).emit(EventType.finding, defect_class="M1")
    assert len(TraceReader(tmp_path / "trace.jsonl").events()) == 2


def test_the_writer_creates_missing_parents(tmp_path: Path) -> None:
    trace = TraceWriter(tmp_path / "a" / "b" / "trace.jsonl", run_id="r")
    trace.emit(EventType.plan_step)
    assert (tmp_path / "a" / "b" / "trace.jsonl").is_file()


def test_the_default_clock_is_utc(tmp_path: Path) -> None:
    event = TraceWriter(tmp_path / "trace.jsonl", run_id="r").emit(EventType.plan_step)
    assert event.ts.tzinfo is not None


def test_round_trip_preserves_every_field(tmp_path: Path) -> None:
    trace = writer(tmp_path)
    written = trace.emit(EventType.claim_check, claim_id="abc", status="verified", value=0.7412)
    (read_back,) = TraceReader(tmp_path / "trace.jsonl").events()
    assert read_back == written


def test_events_can_be_filtered_by_type(tmp_path: Path) -> None:
    trace = writer(tmp_path)
    trace.emit(EventType.tool_call, tool="a")
    trace.emit(EventType.finding, defect_class="E1")
    trace.emit(EventType.tool_call, tool="b")
    assert [
        e.payload["tool"] for e in TraceReader(tmp_path / "trace.jsonl").events("tool_call")
    ] == [
        "a",
        "b",
    ]


def test_blank_lines_are_skipped(tmp_path: Path) -> None:
    path = tmp_path / "trace.jsonl"
    writer(tmp_path).emit(EventType.plan_step)
    path.write_text(path.read_text(encoding="utf-8") + "\n\n", encoding="utf-8")
    assert len(TraceReader(path).events()) == 1


def test_a_missing_trace_names_the_path(tmp_path: Path) -> None:
    with pytest.raises(QuaestorError, match="there is no trace at"):
        TraceReader(tmp_path / "absent.jsonl").events()


def test_a_line_that_is_not_json_names_the_line_number(tmp_path: Path) -> None:
    path = tmp_path / "trace.jsonl"
    good = '{"schema_version":1,"ts":"2026-09-07T12:00:00+00:00","run_id":"r","type":"repair"}'
    path.write_text(good + "\nnot json\n", encoding="utf-8")
    with pytest.raises(QuaestorError, match="line 2 is not JSON"):
        TraceReader(path).events()


def test_a_line_that_is_not_an_object_names_the_line_number(tmp_path: Path) -> None:
    path = tmp_path / "trace.jsonl"
    path.write_text("[1, 2, 3]\n", encoding="utf-8")
    with pytest.raises(QuaestorError, match="line 1 is a list"):
        TraceReader(path).events()


def test_a_line_missing_an_envelope_field_names_the_line_number(tmp_path: Path) -> None:
    path = tmp_path / "trace.jsonl"
    path.write_text('{"schema_version":1,"ts":"2026-09-07T12:00:00+00:00","type":"repair"}\n')
    with pytest.raises(QuaestorError, match="line 1 is not a trace event"):
        TraceReader(path).events()


def test_a_line_with_an_unknown_type_is_an_error(tmp_path: Path) -> None:
    path = tmp_path / "trace.jsonl"
    path.write_text(
        '{"schema_version":1,"ts":"2026-09-07T12:00:00+00:00","run_id":"r","type":"nope"}\n'
    )
    with pytest.raises(QuaestorError, match="line 1 is not a trace event"):
        TraceReader(path).events()


def test_to_line_is_compact_json() -> None:
    event = TraceEvent(ts=FIXED, run_id="r", type=EventType.repair, payload={"section": "outcomes"})
    assert " " not in event.to_line()
