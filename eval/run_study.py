"""The study harness: one `quaestor validate` per (variant, configuration), in resumable chunks.

`04-SEEDED-DEFECT-STUDY.md` section 3 and `docs/STUDY.md` sections 4 and 5. The study is 62 paid
runs over eighteen variants and three configurations, measured at about **10.85 hours of model
time in nineteen sittings** (D-180), and no sitting runs it to the end. So the unit this module
works in is not the study, it is the **chunk**: one invocation of `quaestor study run`, ended by a
cost ceiling or by the operator, whose completed cells are written down as they finish and skipped
by the next invocation.

**What a cell is.** One `(variant, configuration)` pair, run by `quaestor.pipeline.validate` in
this process and written to `<out>/<configuration>/<variant>/`. Cells are ordered configuration by
configuration and, inside a configuration, by variant id, so a chunk that stops half way leaves a
prefix rather than a scatter.

**A cell owns its directory.** Whatever an earlier attempt left in `<out>/<configuration>/
<variant>/` -- and in that cell's cassette store -- is removed before the cell is attempted again.
Without that a retry is impossible rather than untidy: the artifact store refuses to rebind a
logical name to a new hash, so the subject's second run collides on `run.duration_s` before
anything else happens. A killed chunk is the normal case (D-174), so a retry has to work from
whatever the kill left.

**A rejection is terminal; a failure is not.** A cell whose report the renderer refused is
recorded `rejected` and is not attempted again, because the calls were made and paid for and
another draw from the model is not what would change the answer -- `plain_llm` has no repair round
(D-072) and `full_agent`'s runs before the renderer is reached, so neither arm can talk itself out
of a refusal. `retry_rejected` re-attempts them, once, after the thing that caused the refusal has
been changed (D-187).

**Resumability is a ledger, not a scan.** `<out>/ledger.json` is rewritten after every cell and
records, per cell: the status, the attempt count, the cost, the wall clock, both grounding
figures, the finding classes, **and the checks that did not run**. A cell whose latest attempt is
`done` is skipped; anything else is attempted again, because a study with a missing cell is not
the study that was budgeted, and the operator who wants a cell left alone can see it in the ledger
and stop. The ledger is the file a driver reads -- `remaining` is in it -- and the exit code is
deliberately not enough to tell a finished study from a capped chunk, for the same reason D-177
gives about a run: two different outcomes are now the same code. the field is called
`remaining_in_last_plan` because it counts the cells of the *invocation's own plan*, so the rule
for a driver is to rerun the same command line until it reads zero -- a different command line
writes a different plan's number over it.

**`--max-cost` is two ceilings, and both are needed.** Before a cell starts, its estimated cost is
compared with what is left, and a cell that does not fit does not start: that is what makes a
chunk end cleanly on a cell boundary instead of stranding a half-paid run. Before every model
call, the ceiling is checked against what has actually been spent: that is the circuit breaker
D-179 asks for, because a ceiling that can only be read between runs cannot see the one run that
doubles its own drafting bill through a pair of re-asks. The estimate comes from the ledger's own
completed cells of the same configuration and subject when there are any, and from D-179's three
measured runs when there are not.

**An unpriced call under a ceiling is an error.** `Completion.cost_usd` is `None` when nobody
priced the call, and `quaestor.llm.base` says in as many words why it is not `0.0`: a zero that
means "unknown" turns a cost ceiling into a check that always passes. So a provider that does not
price its calls is refused a ceiling rather than silently given an infinite one.

Nothing in this module is imported by `src/quaestor`; it lives in `eval/` beside `seed.py` and is
loaded from there by `quaestor study run`, for the reason D-127 gives. Unlike `seed.py` it has no
`main` of its own: a second entry point would have to build a provider from a `--llm` name, and
that is the one thing `quaestor validate` already does, in one place, with one set of rules about
which flags may be combined. `quaestor study run` is the front door, and D-174's rule is about
which *shell* a sitting is typed into, not which entry point it calls.
"""

from __future__ import annotations

import fcntl
import json
import os
import shutil
import time
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

import yaml

from quaestor.configs import synthetic_default_n
from quaestor.errors import QuaestorError, ReportSchemaError
from quaestor.llm.base import LLM, Completion
from quaestor.llm.recording import RecordingLLM
from quaestor.package import load_package
from quaestor.pipeline import ValidationRun, validate
from quaestor.vocab import Configuration

__all__ = [
    "ESTIMATED_COST_USD",
    "LEDGER_FILE",
    "SEED_FILE",
    "BudgetedLLM",
    "Cell",
    "CellRecord",
    "ChunkSummary",
    "Ledger",
    "StudyLockedError",
    "REJECTED",
    "StudyBudgetError",
    "plan_cells",
    "run_chunk",
    "study_lock",
    "subject_of_variant",
]

LEDGER_FILE: Final = "ledger.json"
"""What a chunk writes after every cell and the next chunk reads before its first."""

LEDGER_SCHEMA_VERSION: Final = 2
"""Bumped when `remaining` became `remaining_in_last_plan`, which is what it always counted.

Reading an older ledger is unaffected -- only `cells` is read back -- so a study part-way through
picks up the new spelling on its next flush. The bump is for the driver, not for this module: a
script written against version 1 should fail to find its field rather than read a zero that means
something else.
"""

SEED_FILE: Final = "SEED.yaml"
"""The variant's answer key. This module reads one field of it -- the subject -- to price a cell."""

DONE: Final = "done"
FAILED: Final = "failed"
REJECTED: Final = "rejected"
"""What a cell can end as.

`done` produced a report. `failed` did not and is **retried** by the next chunk, because the
likeliest reason a cell is not done is that the chunk was killed (D-174) and a retry is the fix.
`rejected` also produced no report -- the renderer refused what the model wrote -- and is
**terminal**, because the calls were made and paid for and a retry is a fresh sample rather than a
repair: `plain_llm` has no repair round at all (D-072), and `full_agent`'s runs before the renderer
is called, so neither arm can correct a refusal by trying again (D-187).
"""

TERMINAL: Final = frozenset({DONE, REJECTED})
"""The statuses a later chunk does not attempt again."""

ESTIMATED_COST_USD: Final[Mapping[str, Mapping[str, float]]] = {
    Configuration.rules_only.value: {"credit_default": 0.0, "msr_prepayment": 0.0},
    Configuration.plain_llm.value: {"credit_default": 1.5622, "msr_prepayment": 1.6335},
    Configuration.full_agent.value: {"credit_default": 5.2635, "msr_prepayment": 5.5033},
}
"""What a cell is expected to cost before one has been run, in US dollars (D-179, D-180).

Four of the six are measured directly -- `rules_only` makes no model call at all, and the three
pricing runs of 2026-09-17 measured `plain_llm` on credit at $1.5622 and `full_agent` at $5.2635
on credit and $5.5033 on MSR. The fifth, `plain_llm` on MSR, is the one arm the pre-flight did not
price, and is D-180's stated scaling of the credit figure by the measured MSR/credit `full_agent`
ratio of 1.0456. It is a table of *estimates* and it is used for one purpose only: deciding
whether a cell fits in what is left of a chunk's ceiling. What a cell actually cost is read back
from its own run and written to the ledger, and a later cell of the same configuration and subject
is priced from that instead.
"""

_DEFAULT_SUBJECT: Final = "credit_default"
"""What a variant whose `SEED.yaml` names no subject is priced as: the cheaper of the two."""


class StudyBudgetError(Exception):
    """The chunk's `--max-cost` ceiling was reached, or a call came back unpriced beneath one.

    Deliberately *not* a `QuaestorError`: the pipeline catches those in several places, and a
    circuit breaker that a `except ToolError` swallows is not a circuit breaker. Nothing in
    `src/quaestor` catches a bare `Exception`, so this reaches `run_chunk` from wherever inside a
    run it was raised.
    """


@dataclass
class BudgetedLLM:
    """A provider that refuses to make the call that would take the chunk past its ceiling.

    Attributes:
        inner: The provider doing the work.
        max_cost_usd: The chunk's ceiling, or `None` for no ceiling at all.
        spent_usd: What the calls made through this wrapper have cost so far.
        calls: How many of them there have been.
    """

    inner: LLM
    max_cost_usd: float | None = None
    spent_usd: float = 0.0
    calls: int = 0

    @property
    def name(self) -> str:
        """The wrapped provider's own name, so a trace says what actually answered."""
        return str(self.inner.name)

    @property
    def remaining_usd(self) -> float:
        """What is left of the ceiling, or infinity when there is none."""
        if self.max_cost_usd is None:
            return float("inf")
        return self.max_cost_usd - self.spent_usd

    def complete(self, prompt: str, *, system: str | None = None, **params: Any) -> Completion:
        """Complete one prompt, unless the ceiling has already been reached.

        Args:
            prompt: The user-turn text.
            system: The system prompt, when there is one.
            **params: Provider parameters, passed through untouched.

        Returns:
            The completion.

        Raises:
            StudyBudgetError: The ceiling is reached, or the completion came back with no price
                under a ceiling -- which would otherwise make every later check pass.
        """
        if self.max_cost_usd is not None and self.spent_usd >= self.max_cost_usd:
            raise StudyBudgetError(
                f"the chunk's --max-cost ceiling of ${self.max_cost_usd:.4f} is reached "
                f"(${self.spent_usd:.4f} over {self.calls} call(s)); the run in flight is "
                "abandoned and the ledger keeps every cell that finished"
            )
        completion = self.inner.complete(prompt, system=system, **params)
        self.calls += 1
        if completion.cost_usd is None:
            if self.max_cost_usd is not None:
                raise StudyBudgetError(
                    f"the provider {self.name!r} priced no call, so --max-cost "
                    f"${self.max_cost_usd:.4f} has nothing to count against; run the chunk "
                    "without --max-cost, or with a provider that reports a cost"
                )
            return completion
        self.spent_usd += completion.cost_usd
        return completion


@dataclass(frozen=True, order=True)
class Cell:
    """One unit of the study: a variant run under one configuration."""

    configuration: str
    variant: str

    @property
    def key(self) -> str:
        """How the ledger names this cell."""
        return f"{self.configuration}/{self.variant}"


@dataclass
class CellRecord:
    """What the ledger keeps about one cell, whether it finished or not.

    Attributes:
        cell: Which cell.
        status: `done` or `failed`.
        attempts: How many chunks have tried it, this one included.
        cost_usd: What the run's model calls cost through the budgeted provider.
        calls: How many model calls it made.
        seconds: Wall clock of the run itself.
        out_dir: Where its report was written.
        precision_pre: Grounding precision before repair.
        precision_post: Grounding precision after the last repair round.
        n_claims: How many claims the verifier extracted.
        findings: The classes it raised, with their severities.
        checks_failed: The rule-based checks that did not run, with their own messages (D-177).
            This is the field a caller judges the run by; the exit code cannot tell a partial
            checklist from a clean one.
        error: The exception that ended the cell, on a `failed` one.
        budget_stopped: Whether it was the chunk's ceiling that ended it, rather than the subject
            or the package. Recorded as its own field rather than read back out of the message,
            so that the decision to stop the chunk is a flag and not a substring search.
    """

    cell: Cell
    status: str
    attempts: int = 1
    cost_usd: float = 0.0
    calls: int = 0
    seconds: float = 0.0
    out_dir: str | None = None
    precision_pre: float | None = None
    precision_post: float | None = None
    n_claims: int | None = None
    findings: list[dict[str, str]] = field(default_factory=list)
    checks_failed: list[dict[str, str]] = field(default_factory=list)
    error: str | None = None
    budget_stopped: bool = False

    def to_payload(self) -> dict[str, Any]:
        """The ledger's own JSON for this cell."""
        return {
            "configuration": self.cell.configuration,
            "variant": self.cell.variant,
            "status": self.status,
            "attempts": self.attempts,
            "cost_usd": round(self.cost_usd, 6),
            "calls": self.calls,
            "seconds": round(self.seconds, 3),
            "out_dir": self.out_dir,
            "precision_pre": self.precision_pre,
            "precision_post": self.precision_post,
            "n_claims": self.n_claims,
            "findings": list(self.findings),
            "checks_failed": list(self.checks_failed),
            "error": self.error,
            "budget_stopped": self.budget_stopped,
        }

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> CellRecord:
        """Read one cell back out of a ledger written by an earlier chunk."""
        return cls(
            cell=Cell(str(payload["configuration"]), str(payload["variant"])),
            status=str(payload["status"]),
            attempts=int(payload.get("attempts", 1)),
            cost_usd=float(payload.get("cost_usd", 0.0)),
            calls=int(payload.get("calls", 0)),
            seconds=float(payload.get("seconds", 0.0)),
            out_dir=payload.get("out_dir"),
            precision_pre=payload.get("precision_pre"),
            precision_post=payload.get("precision_post"),
            n_claims=payload.get("n_claims"),
            findings=list(payload.get("findings") or []),
            checks_failed=list(payload.get("checks_failed") or []),
            error=payload.get("error"),
            budget_stopped=bool(payload.get("budget_stopped", False)),
        )


class Ledger:
    """`<out>/ledger.json`: what has been run, what it cost, and what is left.

    It is rewritten in full after every cell rather than appended to, because a chunk that is
    killed -- which is how D-174's seventh sitting ended -- must leave a file that parses. The
    write is to a temporary name in the same directory and then a rename, so a kill between the
    two leaves the previous ledger rather than half of the next one.
    """

    def __init__(self, path: Path | str) -> None:
        """Open, or start, the ledger at a path.

        Args:
            path: Where `ledger.json` is.
        """
        self.path = Path(path)
        self.records: dict[str, CellRecord] = {}
        if self.path.is_file():
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            for row in payload.get("cells", []):
                record = CellRecord.from_payload(row)
                self.records[record.cell.key] = record

    def is_settled(self, cell: Cell) -> bool:
        """Whether an earlier chunk reached a terminal answer for this cell.

        `done` and `rejected` are both terminal; only `failed` is attempted again. A `rejected`
        cell is re-attempted only when the operator asks for it by name, because the thing that
        would change its answer is a change to this codebase and not another draw from the model.
        """
        record = self.records.get(cell.key)
        return record is not None and record.status in TERMINAL

    def was_rejected(self, cell: Cell) -> bool:
        """Whether this cell's terminal answer was the renderer refusing what the model wrote."""
        record = self.records.get(cell.key)
        return record is not None and record.status == REJECTED

    def attempts(self, cell: Cell) -> int:
        """How many chunks have already tried this cell."""
        record = self.records.get(cell.key)
        return record.attempts if record else 0

    def observed(self, configuration: str, subject_of: Mapping[str, str]) -> dict[str, list[float]]:
        """Costs of the finished cells of one configuration, grouped by the variant's subject."""
        seen: dict[str, list[float]] = {}
        for record in self.records.values():
            if record.status != DONE or record.cell.configuration != configuration:
                continue
            subject = subject_of.get(record.cell.variant, _DEFAULT_SUBJECT)
            seen.setdefault(subject, []).append(record.cost_usd)
        return seen

    def record(self, record: CellRecord, *, remaining: int) -> None:
        """Write one cell into the ledger and flush the whole file.

        Args:
            record: The cell's record. Its `attempts` is set from what the ledger already holds.
            remaining: How many cells of this invocation's plan are still not `done`, this one
                counted. It reaches the file as `remaining_in_last_plan`, because a chunk may be
                restricted by `only` or to one configuration and the number is then true of the
                plan and false of the study; a driver that reruns the *same command line* until
                that field is zero is right either way.
        """
        record.attempts = self.attempts(record.cell) + 1
        self.records[record.cell.key] = record
        self.flush(remaining=remaining)

    def flush(self, *, remaining: int) -> None:
        """Write `ledger.json`, atomically.

        Args:
            remaining: How many cells of *this invocation's plan* are not `done`. It is written as
                `remaining_in_last_plan` and not as `remaining`, because a chunk restricted by
                `--config` or `--only` leaves a number that is true of its own plan and false of
                the study: a `rules_only` chunk resumed after the arm finished writes zero while
                seventeen `plain_llm` cells are still outstanding. A driver reruns one command
                line until the field reads zero *for that command line* (D-181, amended).
        """
        payload = {
            "schema_version": LEDGER_SCHEMA_VERSION,
            "remaining_in_last_plan": remaining,
            "done": sum(1 for item in self.records.values() if item.status == DONE),
            "rejected": sum(1 for item in self.records.values() if item.status == REJECTED),
            "failed": sum(1 for item in self.records.values() if item.status == FAILED),
            "cost_usd": round(sum(item.cost_usd for item in self.records.values()), 6),
            "cells": [
                self.records[key].to_payload() for key in sorted(self.records, key=str.casefold)
            ],
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        temporary.replace(self.path)


LOCK_FILE: Final = "study.lock"
"""Held for the whole of a chunk, so two chunks cannot write one `ledger.json` between them."""


class StudyLockedError(QuaestorError):
    """Another `quaestor study run` holds this `--out` directory."""


@contextmanager
def study_lock(root: Path) -> Iterator[None]:
    """Hold an exclusive lock on a study directory for the length of a chunk.

    **Why this exists, measured.** `Ledger` reads its snapshot when it is constructed and writes
    the whole file on every flush, so two chunks against one `--out` are last-writer-wins over a
    stale snapshot: the second process's flush erases every cell the first recorded after the
    second started. On 2026-09-18 that came within seconds of erasing
    `plain_llm/control_msr_clean` -- **a finished cell, 8 calls, $1.784082** -- from the ledger of
    a live study, while a diagnostic chunk was run against the same tree. The cell's *output* would
    have survived on disk and its ledger row would not, so the next chunk would have seen it as
    un-run, cleared its directory and paid for it again. **That is the failure mode this study
    cannot tolerate**: it is silent, it is unattributable afterwards -- the bill simply comes in
    higher -- and nothing in the result tree records that it happened.

    D-174's rule that a sitting is run by one operator at one keyboard is the convention that
    prevented it until now. This is that convention enforced, which is what a 19-chunk study over
    62 paid cells needs: a rule that holds only while everyone remembers it is not a rule.

    The lock is `flock(2)` on `<out>/study.lock` rather than a PID file, because **a killed chunk
    must stay resumable**. A kill is how a sitting normally ends (D-174), and the kernel drops a
    `flock` when the process dies however it dies, so the next chunk acquires it without anyone
    clearing anything by hand. A PID file would have to be reaped, and the reaping is another thing
    to get wrong at the worst moment. The file itself is left in place on release: deleting it is a
    race of its own, and it costs nothing to leave.

    Args:
        root: The study directory, which must already exist.

    Yields:
        Nothing; the lock is held for the body.

    Raises:
        StudyLockedError: Another process holds it. The message names the process, so the operator
            can tell a live sitting from something they have forgotten about.
    """
    path = root / LOCK_FILE
    handle = path.open("a+", encoding="utf-8")
    try:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            handle.seek(0)
            holder = handle.read().strip() or "an unknown process"
            raise StudyLockedError(
                f"{root} is locked by another `quaestor study run` ({holder}); two chunks writing "
                f"one {LEDGER_FILE} lose whichever cells the loser recorded last, and a lost cell "
                "of a finished run is paid for twice",
                fix="wait for it to finish, or stop it; then rerun this command",
            ) from exc
        handle.seek(0)
        handle.truncate()
        handle.write(f"pid {os.getpid()} since {datetime.now(UTC).isoformat(timespec='seconds')}\n")
        handle.flush()
        yield
    finally:
        handle.close()


@dataclass
class ChunkSummary:
    """What one invocation did, and whether the study has more to do.

    Attributes:
        ran: The cells this chunk finished.
        failed: The cells this chunk tried and could not finish, which the next chunk retries.
        rejected: The cells whose report the renderer refused, which the next chunk does not.
        skipped: The cells an earlier chunk had already finished.
        remaining: How many cells of this invocation's plan are still not `done` -- the plan's,
            not the study's, because a chunk may be restricted by `only` or to one configuration.
        spent_usd: What this chunk's model calls cost.
        stopped_for_budget: Whether the chunk ended on its ceiling rather than on its last cell.
            A chunk can stop before a cell it cannot afford or inside one it could not finish, and
            both set this.
    """

    ran: list[CellRecord] = field(default_factory=list)
    failed: list[CellRecord] = field(default_factory=list)
    rejected: list[CellRecord] = field(default_factory=list)
    skipped: list[Cell] = field(default_factory=list)
    remaining: int = 0
    spent_usd: float = 0.0
    stopped_for_budget: bool = False

    @property
    def checks_failed(self) -> list[CellRecord]:
        """The cells that produced a report with a check missing from it (D-177)."""
        return [record for record in self.ran if record.checks_failed]


def subject_of_variant(variant_dir: Path) -> str:
    """Read the subject a variant was seeded from, for pricing it.

    `SEED.yaml` is the answer key and no code path in `quaestor` opens it; this is the study
    harness, not the pipeline, and the one field it reads decides which column of
    `ESTIMATED_COST_USD` a cell is priced from -- nothing that reaches a report.

    Args:
        variant_dir: The variant package's directory.

    Returns:
        The subject name, or `credit_default` when the variant carries no answer key.
    """
    path = variant_dir / SEED_FILE
    if not path.is_file():
        return _DEFAULT_SUBJECT
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return str(payload.get("subject") or _DEFAULT_SUBJECT)


def plan_cells(
    variants_dir: Path | str,
    configurations: Sequence[str],
    *,
    only: Sequence[str] | None = None,
) -> list[Cell]:
    """List every cell of the study, in the order a chunk runs them.

    Args:
        variants_dir: Where `quaestor study build` wrote the variant packages.
        configurations: Which configurations to run, in the order they are to be run in.
        only: Variant ids to restrict to, or `None` for all of them.

    Returns:
        The cells: configuration by configuration, and inside each, by variant id.

    Raises:
        QuaestorError: There is no such directory, it holds no variant, or `only` names a variant
            that is not in it.
    """
    root = Path(variants_dir)
    if not root.is_dir():
        raise QuaestorError(
            f"there is no variants directory at {root}",
            fix="quaestor study build --taxonomy eval/taxonomy.yaml --out eval/variants",
        )
    found = sorted(
        item.name for item in root.iterdir() if item.is_dir() and (item / "package.yaml").is_file()
    )
    if not found:
        raise QuaestorError(
            f"{root} holds no model package, so there is no study to run",
            fix="quaestor study build --taxonomy eval/taxonomy.yaml --out eval/variants",
        )
    wanted = list(found)
    if only is not None:
        missing = sorted(set(only) - set(found))
        if missing:
            raise QuaestorError(
                f"{root} has no variant named {', '.join(missing)}",
                fix=f"ls {root}",
            )
        wanted = [name for name in found if name in set(only)]
    return [Cell(configuration, name) for configuration in configurations for name in wanted]


def _estimate(cell: Cell, subject: str, ledger: Ledger, subject_of: Mapping[str, str]) -> float:
    """What this cell is expected to cost: the ledger's own runs first, D-179's table second."""
    observed = ledger.observed(cell.configuration, subject_of).get(subject)
    if observed:
        return sum(observed) / len(observed)
    table = ESTIMATED_COST_USD.get(cell.configuration, {})
    return float(table.get(subject, max(table.values(), default=0.0)))


def run_chunk(  # noqa: PLR0913 - a chunk is defined by every one of these
    variants_dir: Path | str,
    out_dir: Path | str,
    *,
    provider: LLM,
    configurations: Sequence[str],
    synthetic: int | None = None,
    data_dir: Path | str | None = None,
    max_cost_usd: float | None = None,
    only: Sequence[str] | None = None,
    cassettes_dir: Path | str | None = None,
    retry_rejected: bool = False,
    log: Any = print,
    **params: Any,
) -> ChunkSummary:
    """Run as many cells as the ceiling allows, writing each one down as it finishes.

    Args:
        variants_dir: Where the variant packages are.
        out_dir: The study directory: `ledger.json` and one directory per cell.
        provider: The provider every cell's model calls go through. It is wrapped in a
            `BudgetedLLM` here, so the ceiling counts every call of every cell of this chunk.
        configurations: Which configurations to run, in order.
        synthetic: The panel size to generate; `None` with no `data_dir` means each subject's
            own documented default, which is what a bare `--synthetic` asks for and what the two
            subjects disagree about (5,000 rows and 2,000).
        data_dir: Where the subjects' real data is, or `None` under `--synthetic`.
        max_cost_usd: The chunk's ceiling, or `None` for no ceiling.
        only: Variant ids to restrict to.
        cassettes_dir: Where to record every model call, or `None` not to. Each cell gets its own
            store under `<cassettes_dir>/<configuration>/<variant>/`, never a pooled one: a
            cassette is keyed on a hash of the request, so two runs that send the same prompt are
            ambiguous in one directory (`docs/STUDY.md` section 4).
        retry_rejected: Attempt the cells an earlier chunk recorded `rejected` as well. Off by
            default: a rejection is terminal because another draw from the model is not what would
            change it. It is turned on deliberately, once, after the thing that caused the
            refusal has been changed (D-187).
        log: Where the per-cell lines go; `print` by default.
        **params: Passed to the provider on every call of every cell, such as `model`. D-151 is
            the reason a study run names its model: a run priced against an unnamed model is not
            comparable to the tape layer or to the committed live runs.

    Returns:
        What the chunk did.

    Raises:
        QuaestorError: The variants directory is not usable, or a cell's package will not load.
    """
    cells = plan_cells(variants_dir, configurations, only=only)
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    with study_lock(root):
        return _run_cells(
            cells,
            root,
            Path(variants_dir),
            provider=provider,
            synthetic=synthetic,
            data_dir=data_dir,
            max_cost_usd=max_cost_usd,
            cassettes_dir=cassettes_dir,
            retry_rejected=retry_rejected,
            log=log,
            params=params,
        )


def _run_cells(  # noqa: PLR0913 - the chunk's parameters, minus the ones the lock consumed
    cells: Sequence[Cell],
    root: Path,
    variants_dir: Path,
    *,
    provider: LLM,
    synthetic: int | None,
    data_dir: Path | str | None,
    max_cost_usd: float | None,
    cassettes_dir: Path | str | None,
    retry_rejected: bool,
    log: Any,
    params: Mapping[str, Any],
) -> ChunkSummary:
    """Run the planned cells. Called only with the study lock held.

    The ledger is both *read* and *written* in here, which is the whole point of the lock being
    outside it: a snapshot taken before another chunk's flush and written after it erases that
    chunk's cells.
    """
    ledger = Ledger(root / LEDGER_FILE)
    subject_of = {cell.variant: subject_of_variant(variants_dir / cell.variant) for cell in cells}
    budgeted = BudgetedLLM(provider, max_cost_usd=max_cost_usd)
    summary = ChunkSummary()

    def outstanding() -> int:
        return sum(1 for item in cells if not ledger.is_settled(item))

    for cell in cells:
        if ledger.is_settled(cell) and not (retry_rejected and ledger.was_rejected(cell)):
            summary.skipped.append(cell)
            continue
        subject = subject_of[cell.variant]
        estimate = _estimate(cell, subject, ledger, subject_of)
        if estimate > budgeted.remaining_usd:
            log(
                f"{cell.key}: not started; the estimate of ${estimate:.4f} does not fit in the "
                f"${budgeted.remaining_usd:.4f} left of --max-cost"
            )
            summary.stopped_for_budget = True
            break
        cell_out = root / cell.configuration / cell.variant
        cell_tapes = (
            Path(cassettes_dir) / cell.configuration / cell.variant
            if cassettes_dir is not None
            else None
        )
        for path in _clear_previous_attempt(cell_out, cell_tapes):
            log(f"{cell.key}: discarded an unfinished earlier attempt at {path}")
        if cell_tapes is not None:
            budgeted.inner = RecordingLLM(provider, cell_tapes)
        record = _run_cell(
            cell,
            variants_dir / cell.variant,
            cell_out,
            budgeted=budgeted,
            synthetic=synthetic,
            data_dir=data_dir,
            log=log,
            params=params,
        )
        if record.status == DONE:
            summary.ran.append(record)
        elif record.status == REJECTED:
            summary.rejected.append(record)
        else:
            summary.failed.append(record)
        ledger.record(record, remaining=outstanding())
        if record.budget_stopped:
            summary.stopped_for_budget = True
            break

    summary.spent_usd = budgeted.spent_usd
    summary.remaining = outstanding()
    ledger.flush(remaining=summary.remaining)
    return summary


def _run_cell(  # noqa: PLR0913 - a cell needs each of these and none of them has a default
    cell: Cell,
    package_dir: Path,
    cell_out: Path,
    *,
    budgeted: BudgetedLLM,
    synthetic: int | None,
    data_dir: Path | str | None,
    log: Any,
    params: Mapping[str, Any],
) -> CellRecord:
    """Run one cell and turn whatever happened into a ledger record.

    Only the two failures a study expects are caught -- the chunk running out of money, and a
    `QuaestorError`, which is every way this codebase says "that did not work", the renderer's
    refusal and a subject that will not run included. Anything else is a defect in the harness or
    in the pipeline, and it ends the chunk rather than being written down as a miss: the ledger is
    already flushed, so the cells that finished are safe, and spending the rest of a sitting
    against a broken harness buys nothing.
    """
    started = time.monotonic()
    spent_before, calls_before = budgeted.spent_usd, budgeted.calls
    try:
        package = load_package(package_dir, data_dir=data_dir)
        rows = _rows_for(package.name, synthetic, data_dir)
        run = validate(
            package,
            llm=budgeted,
            config=cell.configuration,
            data_dir=data_dir,
            synthetic=rows,
            out=cell_out,
            **params,
        )
    except StudyBudgetError as exc:
        return _ended(
            cell, FAILED, str(exc), budgeted, spent_before, calls_before, started, log, True
        )
    except ReportSchemaError as exc:
        return _ended(
            cell, REJECTED, str(exc.message), budgeted, spent_before, calls_before, started, log
        )
    except QuaestorError as exc:
        return _ended(
            cell, FAILED, str(exc.message), budgeted, spent_before, calls_before, started, log
        )
    record = _record_of(cell, run, cell_out, budgeted, spent_before, calls_before, started)
    log(
        f"{cell.key}: {len(record.findings)} finding(s), grounding "
        f"{run.precision_pre:.4f}/{run.precision_post:.4f} over {run.claims.n_claims} claims, "
        f"${record.cost_usd:.4f} in {record.calls} call(s), {record.seconds:.1f}s"
    )
    for failure in record.checks_failed:
        log(f"{cell.key}: check did not run — {failure['tool']}: {failure['message']}")
    return record


def _clear_previous_attempt(cell_out: Path, cell_tapes: Path | None) -> list[str]:
    """Remove what an earlier attempt at this cell left behind, and say what was removed.

    **A cell owns its directory, and an attempt starts from nothing.** The artifact store is
    content-addressed with a logical-name index, so it refuses to rebind a name to a new hash --
    correctly, because every citation written against the old hash would stop resolving. That makes
    a *retry* into a directory a previous attempt half-filled impossible rather than merely untidy:
    the subject runs again, takes a different number of seconds, and `run.duration_s` collides on
    the first thing it stores. A chunk that is killed is the normal case, not the exceptional one
    (D-174), so retrying has to work from whatever the kill left.

    The cassette store goes with it, for the reason `docs/STUDY.md` section 4 gives about pooling:
    a cassette is keyed on a hash of the request, so an abandoned attempt's tapes sitting beside a
    retry's are two runs in one directory, which is exactly the ambiguity per-cell stores exist to
    prevent.

    This is `seed()`'s rule applied to a run rather than to a package -- a variant directory is
    removed before it is rebuilt "so that seeding twice writes the same bytes rather than layering
    one recipe on another" -- and it belongs here rather than in `validate`, which does not own its
    `--out` directory. Its caller does, and for a cell the caller is this module.

    Args:
        cell_out: The cell's run directory.
        cell_tapes: The cell's cassette store, or `None` when nothing is being recorded.

    Returns:
        The paths removed, in the order they were removed; empty when there was nothing there.
    """
    removed: list[str] = []
    for path in (cell_out, cell_tapes):
        if path is not None and path.exists():
            shutil.rmtree(path)
            removed.append(str(path))
    return removed


def _rows_for(package_name: str, synthetic: int | None, data_dir: Path | str | None) -> int | None:
    """Resolve what `--synthetic` means for one subject, or `None` for a `--data` cell.

    Args:
        package_name: The variant's package name, which is the subject's name.
        synthetic: The row count the chunk was given, or `None`.
        data_dir: The real data directory, or `None`.

    Returns:
        The row count to generate, or `None` under `--data`.

    Raises:
        QuaestorError: There is no documented size for this subject and none was named, in which
            case the human names a number rather than the harness inventing one.
    """
    if data_dir is not None:
        return None
    if synthetic is not None:
        return synthetic
    default = synthetic_default_n(package_name)
    if default is None:
        raise QuaestorError(
            f"no documented synthetic size for the package {package_name!r}, so a bare "
            "--synthetic has no number to use for it",
            fix="quaestor study run --synthetic 2000 ...",
        )
    return default


def _ended(  # noqa: PLR0913 - the record is a function of the meters around the ending
    cell: Cell,
    status: str,
    message: str,
    budgeted: BudgetedLLM,
    spent_before: float,
    calls_before: int,
    started: float,
    log: Any,
    budget_stopped: bool = False,
) -> CellRecord:
    """Build the ledger record of a cell that produced no report, and say so on the log."""
    record = CellRecord(
        cell=cell,
        status=status,
        cost_usd=budgeted.spent_usd - spent_before,
        calls=budgeted.calls - calls_before,
        seconds=time.monotonic() - started,
        error=message,
        budget_stopped=budget_stopped,
    )
    log(f"{cell.key}: {status.upper()} after {record.seconds:.1f}s -- {message}")
    return record


def _record_of(  # noqa: PLR0913 - the record is a function of the run and of the meters around it
    cell: Cell,
    run: ValidationRun,
    cell_out: Path,
    budgeted: BudgetedLLM,
    spent_before: float,
    calls_before: int,
    started: float,
) -> CellRecord:
    """Build the ledger record of a cell that produced a report."""
    return CellRecord(
        cell=cell,
        status=DONE,
        cost_usd=budgeted.spent_usd - spent_before,
        calls=budgeted.calls - calls_before,
        seconds=time.monotonic() - started,
        out_dir=str(cell_out),
        precision_pre=run.precision_pre,
        precision_post=run.precision_post,
        n_claims=run.claims.n_claims,
        findings=[
            {"class": finding.defect_class.value, "severity": finding.severity.value}
            for finding in run.findings.findings
        ],
        checks_failed=[
            {"tool": failure.tool, "message": failure.message} for failure in run.checks_failed
        ],
    )
