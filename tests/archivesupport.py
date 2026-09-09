"""Reading the archived live runs of `eval/results/first-live/` as offline fixtures.

Every defect class this project has found in a live run was found by a human reading a rendered
report at roughly $6 and twenty-two minutes a run. The runs themselves are committed -- report,
`claims.json`, trace, cassettes and artifact index -- so the reading a person did once can be done
by `pytest` every time, on the same bytes, at no cost. This module is the reader; the checks are in
`tests/test_archive_fixtures.py`.

**The drafters' own completions are the text under check, not only `report.md`.** A repair round
removes the numbers it could not verify, so a token that provoked a round is precisely the token
the shipped report no longer holds: the third live run's section 4 drafted "under rule O1 (D-050)
is 0.08", the `50` was counted as a claim of fifty, and the round deleted the reference before the
renderer ever saw it. A tokenizer check over `report.md` alone therefore cannot see the class of
defect it exists to find. Each archived run's draft calls are recovered from its cassettes, and a
repair round's *previous* draft is recovered from the repair prompt itself, which quotes it
verbatim under `Previous draft:` (DECISIONS D-118).

Nothing here calls a model, downloads anything or reads a row of real data: the cassettes are read
as JSON and the reports as text.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any, Final

from claimsupport import ClaimKey
from quaestor import TraceReader
from quaestor.report.renderer import drafted_and_rendered_body
from quaestor.report.sections import section_heading
from quaestor.trace import EventType, TraceEvent
from quaestor.verifier.claim import VerifiedClaim
from quaestor.verifier.match import Match
from quaestor.verifier.tokens import EligibleNumbers, eligible_numbers
from quaestor.vocab import SECTION_ORDER, ReportSection

__all__ = [
    "ARCHIVE",
    "CREDIT_VERSION",
    "RENDERED_RUNS",
    "ArchivedRun",
    "DraftCall",
    "RepairRound",
    "rendered_runs",
    "section_of_heading",
]

ARCHIVE: Final = Path(__file__).resolve().parents[1] / "eval" / "results" / "first-live"
"""Where the operator's live runs are committed (D-087)."""

RENDERED_RUNS: Final = ("credit-attempt3", "credit-attempt4", "credit-attempt5")
"""The archived runs that rendered a report and wrote a `claims.json`.

Attempts 1 and 2 produced neither -- the first was refused by the renderer over an uncovered number
that was never a claim (D-084) and the second exited 1 when a tool the loop asked for raised
(D-088) -- so neither can answer "is every token covered by a post-repair claim". Attempt 1's own
draft calls are still readable and one check below uses them, against the verified `claim_check`
events of its trace rather than against a claims document it does not have.
"""

CREDIT_VERSION: Final = "1.0"
"""`subjects/credit_default/package.yaml`'s version, which the pre-pass excludes (D-084).

Passed to the tokenizer here for the same reason the pipeline passes it: the drafter mentions the
package by name and version, and a caller that omits it counts the `1.0` as a claim of one.
"""

_PREVIOUS_MARKER: Final = "Previous draft:\n"
"""Where the repair prompt starts quoting the draft it is asking about."""

_PROBLEMS_MARKER: Final = "Problems, one per line, in the form the verifier reported them:"
"""Where the repair prompt stops quoting the draft and starts listing what is wrong with it.

Both markers are `REPAIR_INSTRUCTION`'s own text (`report/drafter.py`). They are matched as
literals rather than imported because the archived prompts were written by the builds of the day:
the sentences D-109 added are not in any of them, and a fixture keyed on today's constant would
stop reading yesterday's run the next time that instruction is edited.
"""

_DRAFT_PROMPT_OPENING: Final = "You are drafting one section"
"""How every drafting prompt opens, first draft and re-draft alike."""

_SECTION_MARKER: Final = "Section: "
"""The prompt line that names which of the seven sections is being drafted."""


@cache
def section_of_heading() -> dict[str, ReportSection]:
    """Map each level-2 heading to its section, from the shipped briefs rather than a table.

    Returns:
        ``{"## 4. Outcomes analysis": ReportSection.outcomes, ...}``.
    """
    return {section_heading(section): section for section in SECTION_ORDER}


def _problems_of(tail: str) -> list[str]:
    """The verifier's sentences a repair prompt listed, taken as the run's own bullet list.

    Args:
        tail: The prompt from the problems marker onwards.

    Returns:
        One sentence per bullet, in prompt order. The list ends at the first line that is not a
        bullet, which is `REPAIR_INSTRUCTION`'s "Re-draft the whole section" paragraph.
    """
    problems: list[str] = []
    for line in tail.split("\n"):
        if line.startswith("- "):
            problems.append(line[2:])
        elif problems:
            break
    return problems


@dataclass(frozen=True)
class DraftCall:
    """One drafting call of an archived run, recovered from its cassette.

    Attributes:
        cassette: The tape's file name, so a failure names the bytes it came from.
        section: Which of the seven sections was being drafted.
        markdown: What the drafter returned, as `DraftedSection.markdown`.
        previous: The draft this call was asked to repair, quoted in its own prompt, or ``None``
            for a first draft.
        problems: The verifier's sentences the prompt listed, empty for a first draft.
    """

    cassette: str
    section: ReportSection
    markdown: str
    previous: str | None = None
    problems: tuple[str, ...] = ()

    @property
    def is_repair(self) -> bool:
        """Whether this call is a repair round's re-draft."""
        return self.previous is not None

    def eligible(self) -> EligibleNumbers:
        """The eligible numbers of what the drafter returned, by the pipeline's own definition."""
        return eligible_numbers(self.markdown, package_version=CREDIT_VERSION)


@dataclass(frozen=True)
class RepairRound:
    """One repair round of an archived run, with everything a replay of it needs.

    Attributes:
        run: The run this round belongs to.
        event: The round's own `repair` trace event.
        call: The re-draft call, whose prompt carries the previous draft.
        failures: The flagged claims, as `claims.json` recorded them before the round.
    """

    run: ArchivedRun
    event: TraceEvent
    call: DraftCall
    failures: tuple[Match, ...]

    @property
    def section(self) -> ReportSection:
        """Which section the round re-drafted."""
        return self.call.section

    @property
    def previous(self) -> str:
        """The draft as it stood before the round, from the prompt that quoted it."""
        assert self.call.previous is not None, self.call.cassette
        return self.call.previous

    @property
    def redraft(self) -> str:
        """What the drafter returned for the round."""
        return self.call.markdown

    def flagged_lines(self) -> tuple[str, ...]:
        """The lines of the previous draft that carried a flagged claim, whitespace collapsed."""
        return tuple(" ".join(match.claim.text.split()) for match in self.failures)

    def unflagged_lines(self) -> tuple[str, ...]:
        """Every written line of the previous draft that carried no flagged claim, as written."""
        flagged = set(self.flagged_lines())
        return tuple(
            line
            for line in self.previous.split("\n")
            if line.strip() and " ".join(line.split()) not in flagged
        )


@dataclass(frozen=True)
class ArchivedRun:
    """One committed live run, read from disk.

    Attributes:
        name: The directory name under `eval/results/first-live/`.
    """

    name: str

    @property
    def path(self) -> Path:
        """The run's directory."""
        return ARCHIVE / self.name

    def report(self) -> str:
        """The run's rendered report."""
        return (self.path / "report.md").read_text(encoding="utf-8")

    def body(self) -> str:
        """Sections 1 to 7 of the report: what the drafter wrote and the renderer placed."""
        return drafted_and_rendered_body(self.report())

    def claims(self) -> dict[str, Any]:
        """The run's `claims.json`."""
        return dict(json.loads((self.path / "claims.json").read_text(encoding="utf-8")))

    def claim_keys(self, stage: str = "post_repair") -> list[ClaimKey]:
        """The run's claims at one stage, as coverage keys.

        Args:
            stage: ``"pre_repair"`` or ``"post_repair"``.

        Returns:
            One key per claim, in file order.
        """
        return [
            ClaimKey(claim["value"], claim["unit"] == "percent") for claim in self.claims()[stage]
        ]

    def events(self, kind: EventType | None = None) -> list[TraceEvent]:
        """The run's trace events, all of them or of one type, in file order."""
        events = list(TraceReader(self.path / "trace.jsonl"))
        return events if kind is None else [event for event in events if event.type is kind]

    def cassettes(self) -> Iterator[tuple[str, dict[str, Any]]]:
        """Every tape of the run, in file-name order, as ``(file name, payload)``."""
        for path in sorted((self.path / "cassettes").glob("*.json")):
            yield path.name, dict(json.loads(path.read_text(encoding="utf-8")))

    def draft_calls(self) -> list[DraftCall]:
        """Every drafting call of the run, first drafts and re-drafts, in cassette order.

        A tape is a drafting call when its prompt opens the way `DRAFT_PROMPT` opens, and a repair
        round when that prompt also quotes a previous draft. The section comes from the prompt's
        own `Section:` line, resolved against the shipped briefs.
        """
        calls: list[DraftCall] = []
        for name, tape in self.cassettes():
            prompt = str(tape["request"]["prompt"])
            if not prompt.startswith(_DRAFT_PROMPT_OPENING):
                continue
            heading = prompt.split(_SECTION_MARKER, 1)[1].split("\n", 1)[0].strip()
            markdown = str(json.loads(tape["completion"]["text"])["markdown"])
            previous: str | None = None
            problems: tuple[str, ...] = ()
            if _PROBLEMS_MARKER in prompt:
                head, tail = prompt.split(_PROBLEMS_MARKER, 1)
                previous = head.split(_PREVIOUS_MARKER, 1)[1].rstrip("\n")
                problems = tuple(_problems_of(tail))
            calls.append(
                DraftCall(
                    cassette=name,
                    section=section_of_heading()[heading],
                    markdown=markdown,
                    previous=previous,
                    problems=problems,
                )
            )
        return calls

    def first_drafts(self) -> list[DraftCall]:
        """The run's first draft of each section, in cassette order."""
        return [call for call in self.draft_calls() if not call.is_repair]

    def repair_rounds(self) -> list[RepairRound]:
        """Every repair round of the run, in trace order, each with its re-draft and its failures.

        The round's flagged claims are the pre-repair claims whose ids the `repair` event lists,
        which is the run's own record of what provoked it rather than a recomputation of it.
        """
        by_id = {claim["id"]: claim for claim in self.claims()["pre_repair"]}
        redrafts = {call.section: call for call in self.draft_calls() if call.is_repair}
        rounds: list[RepairRound] = []
        for event in self.events(EventType.repair):
            section = ReportSection(event.payload["section"])
            rounds.append(
                RepairRound(
                    run=self,
                    event=event,
                    call=redrafts[section],
                    failures=tuple(
                        Match(claim=VerifiedClaim(**by_id[claim_id]))
                        for claim_id in event.payload["flagged"]
                    ),
                )
            )
        return rounds


def rendered_runs() -> list[ArchivedRun]:
    """The archived runs that rendered a report, in attempt order."""
    return [ArchivedRun(name) for name in RENDERED_RUNS]
