"""``trace.jsonl``: the machine-readable record of what a run did.

Spec section 3.1 fixes the shape: one JSON object per line, ``schema_version: 1``, the fields
``ts``, ``run_id`` and ``type``, and then whatever that event type carries. The six types are
``tool_call``, ``llm_call``, ``plan_step``, ``claim_check``, ``repair`` and ``finding``.

The trace exists so that ``eval/score.py`` can score a run without reading a word of its prose.
That is the constraint that shapes this module: everything the study counts -- tool calls, re-asks,
tokens, notional cost, repair rounds, promoted findings -- has to be an event field, never a
sentence. Appendix C of the report is rendered from the same file, so a number in that appendix is
a number somebody can recompute from the trace.

On disk the type-specific fields are top level, as the spec writes them. In memory they live in
:attr:`TraceEvent.payload`, which is what keeps this module ``mypy --strict``-clean without a
model per event type: ``extra="allow"`` would put them on the model, where every read is an
attribute the type checker has never heard of (DECISIONS D-020).
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterator, Mapping
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, Final

from pydantic import BaseModel, ConfigDict, Field

from .errors import QuaestorError

__all__ = [
    "SCHEMA_VERSION",
    "EventType",
    "TraceEvent",
    "TraceReader",
    "TraceWriter",
]

SCHEMA_VERSION: Final = 1
"""The version stamped on every line. Every file Quaestor persists carries one."""

_RESERVED: Final = frozenset({"schema_version", "ts", "run_id", "type"})
"""Top-level keys the envelope owns; an event's own fields may not use them."""


class EventType(StrEnum):
    """The event types of spec section 3.1.

    Attributes:
        tool_call: A tool ran. Fields: ``tool``, ``args_hash``, ``duration_s``, ``artifacts``.
        llm_call: A model was called. Fields: ``purpose``, ``model``, ``tokens_in``,
            ``tokens_out``, ``cost_usd``, ``latency_ms``. ``purpose`` is ``"reask"`` on every
            retry, which is how the study counts them.
        plan_step: One step of the planner, rule-based or from the bounded follow-up loop.
        claim_check: One claim matched against the artifact store.
        repair: One repair round over one section.
        finding: A candidate was promoted to a finding, or its severity was changed.
    """

    tool_call = "tool_call"
    llm_call = "llm_call"
    plan_step = "plan_step"
    claim_check = "claim_check"
    repair = "repair"
    finding = "finding"


class TraceEvent(BaseModel):
    """One line of ``trace.jsonl``.

    Attributes:
        schema_version: Always :data:`SCHEMA_VERSION`.
        ts: When the event was emitted, timezone-aware.
        run_id: The run this event belongs to; joins the trace to the report's front matter.
        type: Which of the six event types this is.
        payload: The type-specific fields, written at the top level of the JSON line.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: int = SCHEMA_VERSION
    ts: datetime
    run_id: str
    type: EventType
    payload: dict[str, Any] = Field(default_factory=dict)

    def to_line(self) -> str:
        """Serialise the event to one JSONL line, with the payload fields at the top level.

        Returns:
            Compact JSON with no trailing newline.
        """
        record: dict[str, Any] = {
            "schema_version": self.schema_version,
            "ts": self.ts.isoformat(),
            "run_id": self.run_id,
            "type": self.type.value,
        }
        record.update(self.payload)
        return json.dumps(record, ensure_ascii=True, separators=(",", ":"), sort_keys=False)

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> TraceEvent:
        """Rebuild an event from a parsed JSONL record, folding unknown keys into the payload.

        Args:
            record: One decoded line of a trace file.

        Returns:
            The event.

        Raises:
            KeyError: The record is missing one of the envelope fields.
        """
        payload = {key: value for key, value in record.items() if key not in _RESERVED}
        return cls(
            schema_version=int(record["schema_version"]),
            ts=datetime.fromisoformat(str(record["ts"])),
            run_id=str(record["run_id"]),
            type=EventType(record["type"]),
            payload=payload,
        )


def _utc_now() -> datetime:
    """Return the current time in UTC. Injectable so that a test's trace is byte-stable."""
    return datetime.now(UTC)


class TraceWriter:
    """Appends events to ``trace.jsonl``, one line per event.

    The file is opened, written and closed per event rather than held open, so that a run killed
    mid-way -- a sandbox timeout, a cost ceiling, an interrupt -- leaves a trace of everything that
    happened up to the kill. A validation run emits a few hundred events, so the cost of doing so
    is not measurable next to a subprocess model fit.

    Attributes:
        path: The file being appended to.
        run_id: Stamped on every event.
        count: How many events have been written.
    """

    def __init__(
        self,
        path: Path | str,
        *,
        run_id: str,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        """Open (or create) a trace file for appending.

        Args:
            path: Where to write. Parent directories are created.
            run_id: The run identifier stamped on every event and on the report's front matter.
            clock: Returns the timestamp for each event; defaults to the current UTC time. Tests
                pass a fixed clock so that a trace file is byte-comparable.
        """
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.run_id = run_id
        self._clock = clock or _utc_now
        self.count = 0

    def emit(self, event_type: EventType | str, **fields: Any) -> TraceEvent:
        """Write one event.

        Args:
            event_type: One of :class:`EventType`, or its string value.
            **fields: The type-specific fields, written at the top level of the line.

        Returns:
            The event as written, so a caller can assert on it without re-reading the file.

        Raises:
            QuaestorError: A field name collides with one of the envelope keys
                (``schema_version``, ``ts``, ``run_id``, ``type``), which would make the line
                ambiguous to read back.
        """
        clashes = sorted(_RESERVED & set(fields))
        if clashes:
            raise QuaestorError(
                f"trace event fields {clashes} collide with the envelope fields of "
                f"{self.path}; rename them, as a reader cannot tell the two apart"
            )
        event = TraceEvent(
            ts=self._clock(),
            run_id=self.run_id,
            type=EventType(event_type),
            payload=dict(fields),
        )
        with open(self.path, "a", encoding="utf-8") as handle:
            handle.write(event.to_line() + "\n")
        self.count += 1
        return event

    def llm_call(
        self,
        *,
        purpose: str,
        model: str,
        tokens_in: int | None = None,
        tokens_out: int | None = None,
        cost_usd: float | None = None,
        latency_ms: float | None = None,
        **fields: Any,
    ) -> TraceEvent:
        """Write one ``llm_call`` event with the fields spec section 3.1 names.

        This one convenience method exists because the field names of an ``llm_call`` are counted
        by the study (re-asks, tokens, notional cost) and so must not acquire a second spelling.

        Args:
            purpose: Why the call was made -- ``"draft"``, ``"extract"``, ``"reask"``, ``"plan"``.
            model: The model that answered, as the adapter reports it.
            tokens_in: Prompt tokens, or ``None`` when the provider does not report them.
            tokens_out: Completion tokens, or ``None`` when the provider does not report them.
            cost_usd: Notional cost, or ``None`` when the call was not priced.
            latency_ms: Wall-clock duration of the call.
            **fields: Anything else worth recording, such as the schema that was asked for.

        Returns:
            The event as written.
        """
        return self.emit(
            EventType.llm_call,
            purpose=purpose,
            model=model,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            **fields,
        )


class TraceReader:
    """Reads ``trace.jsonl`` back into :class:`TraceEvent` objects.

    This is the half of the module ``eval/`` uses: the study scores a run from its trace and its
    artifacts and never from its prose, so this reader is on the scoring path and a malformed line
    is an error rather than something to skip quietly.

    Attributes:
        path: The file being read.
    """

    def __init__(self, path: Path | str) -> None:
        """Point the reader at a trace file.

        Args:
            path: The file to read. It is not opened until the reader is iterated.
        """
        self.path = Path(path)

    def __iter__(self) -> Iterator[TraceEvent]:
        """Yield every event in file order.

        Yields:
            One :class:`TraceEvent` per non-empty line.

        Raises:
            QuaestorError: The file does not exist, a line is not JSON, or a line is missing an
                envelope field. The message names the file and the line number.
        """
        if not self.path.is_file():
            raise QuaestorError(
                f"there is no trace at {self.path}",
                fix="quaestor validate <package> --out <dir>",
            )
        with open(self.path, encoding="utf-8") as handle:
            for number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                yield self._parse(number, line)

    def _parse(self, number: int, line: str) -> TraceEvent:
        """Parse one line, naming the file and the line number on failure."""
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise QuaestorError(f"{self.path} line {number} is not JSON: {exc}") from exc
        if not isinstance(record, dict):
            raise QuaestorError(
                f"{self.path} line {number} is a {type(record).__name__}, not a JSON object"
            )
        try:
            return TraceEvent.from_record(record)
        except (KeyError, ValueError) as exc:
            raise QuaestorError(f"{self.path} line {number} is not a trace event: {exc}") from exc

    def events(self, event_type: EventType | str | None = None) -> list[TraceEvent]:
        """Read every event, optionally of one type only.

        Args:
            event_type: Keep only events of this type, or ``None`` to keep all of them.

        Returns:
            The events, in file order.
        """
        wanted = EventType(event_type) if event_type is not None else None
        return [event for event in self if wanted is None or event.type is wanted]
