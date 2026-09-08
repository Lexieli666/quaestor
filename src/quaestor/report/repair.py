"""The repair loop: at most two re-drafts of a section, then the number is wrapped, never dropped.

Spec section 3.11. A section with any claim that did not verify is re-drafted, with the flagged
claims listed in the form the verifier reported them -- "you wrote 0.68 for metrics.oot.auc; the
artifact says 0.6812; cite or remove" -- and the new draft is extracted and matched again. Two
rounds at most. Whatever still does not verify stays in the prose, wrapped ``⟦unverified: 0.68⟧``,
so a reader sees the number *and* sees that nobody could check it.

The wrapper is the part that matters. A pipeline that quietly deleted a number it could not verify
would report a better grounding precision the worse its drafter was, because the denominator would
shrink with the numerator; the whole apparatus of the pre-pass exists to stop exactly that, and
the wrapper is the same argument at the other end of the loop. ``REPORT_SCHEMA.json``'s third
refusal rule enforces it: under ``full_agent`` an uncovered number that is not wrapped is a report
the renderer will not write.

Each round is one ``repair`` trace event and one or more ``repairs`` entries in ``claims.json``.
Pairing a claim before a round with the claim that replaced it after it is done by id first -- an
uncited number that gains its citation keeps its id, because the id is a hash of section, text and
value and only the citation moved -- then by nearest unpaired verified value, and a number the
drafter removed instead of citing leaves no ``after`` side and is recorded on the trace event
alone (DECISIONS D-073).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Final

from ..findings import Finding, FindingCandidate
from ..trace import EventType, TraceWriter
from ..verifier.claim import ClaimStatus, VerifiedClaim
from ..verifier.claims_doc import Repair, RepairSide
from ..verifier.extract import Extraction, masked_prose, numeric_tokens, token_value
from ..verifier.match import Match
from ..vocab import ReportSection
from .drafter import Drafter, GuidanceSpan
from .sections import ArtifactBrief, SectionBrief

__all__ = [
    "MAX_REPAIR_ROUNDS",
    "UNVERIFIED_CLOSE",
    "UNVERIFIED_OPEN",
    "DraftInputs",
    "RepairOutcome",
    "SectionDraft",
    "Verify",
    "is_wrapped",
    "repair_sections",
    "wrap_unverified",
    "wrapped_values",
]

MAX_REPAIR_ROUNDS: Final = 2
"""Spec section 3.11: "at most two rounds". A third would be a loop that hides a bad prompt."""

UNVERIFIED_OPEN: Final = "⟦unverified: "
"""The opening of the wrapper, as ``REPORT_SCHEMA.json`` writes it."""

UNVERIFIED_CLOSE: Final = "⟧"
"""The closing bracket of the wrapper."""

RELATIVE_PAIRING_WINDOW: Final = 0.1
"""How far a corrected number may move and still be recognised as the same claim repaired.

A repair corrects a number the drafter got slightly wrong -- 0.0136 for 0.0126 -- or attaches a
citation to one it wrote correctly. A number that moved by more than a tenth of itself is a
different statement, and pairing it would put a false row in the repairs table.
"""

Verify = Callable[[ReportSection, str], "tuple[Extraction, list[Match]]"]
"""Extract and match one section's markdown. Injected, because each configuration extracts its own
way: ``full_agent`` and ``plain_llm`` ask a model, ``rules_only`` declares its claims as it writes
them."""


@dataclass
class DraftInputs:
    """Everything a section needs to be drafted again, unchanged between rounds.

    Attributes:
        artifacts: What the section may cite.
        spans: The guidance retrieved for it.
        candidates: The candidates raised on its material.
        findings: The findings section 6 must write about.
    """

    artifacts: Sequence[ArtifactBrief] = ()
    spans: Sequence[GuidanceSpan] = ()
    candidates: Sequence[FindingCandidate] = ()
    findings: Sequence[Finding] = ()


@dataclass
class SectionDraft:
    """One section as it stands: its prose, its claims and their verdicts.

    Attributes:
        brief: The section's brief.
        markdown: The prose as drafted, before the wrapper is applied.
        extraction: What the extractor and the pre-pass produced over it.
        matches: One verdict per claim, in prose order.
        rounds: How many repair rounds this section went through.
    """

    brief: SectionBrief
    markdown: str
    extraction: Extraction
    matches: list[Match] = field(default_factory=list)
    rounds: int = 0

    @property
    def section(self) -> ReportSection:
        """Which of the seven sections this is."""
        return self.brief.section

    @property
    def claims(self) -> list[VerifiedClaim]:
        """The verified claims, in prose order."""
        return [match.claim for match in self.matches]

    @property
    def failures(self) -> list[Match]:
        """The claims that did not verify, in prose order."""
        return [match for match in self.matches if match.claim.status is not ClaimStatus.verified]

    @property
    def problems(self) -> list[str]:
        """The verifier's sentences for the claims that did not verify, for the repair prompt."""
        return [match.message for match in self.failures if match.message]


@dataclass
class RepairOutcome:
    """What the repair loop did.

    Attributes:
        drafts: The sections as they stand after the loop, in report order.
        repairs: One entry per claim a round changed, for ``claims.json``.
        rounds: How many rounds ran in total, over all sections.
    """

    drafts: list[SectionDraft]
    repairs: list[Repair] = field(default_factory=list)
    rounds: int = 0


def _pair(before: Match, after: Sequence[Match], taken: set[int]) -> int | None:
    """Return the index in ``after`` of the claim that replaced ``before``, or ``None``.

    By id first: a number that gained a citation keeps its id, because the id hashes the section,
    the text and the value and only the citation moved. Then by nearest verified value inside
    :data:`RELATIVE_PAIRING_WINDOW`, which is the drafter correcting a number it got wrong.
    """
    for index, match in enumerate(after):
        if index not in taken and match.claim.id == before.claim.id:
            return index
    best: tuple[float, int] | None = None
    scale = max(abs(before.claim.value), 1e-9)
    for index, match in enumerate(after):
        if index in taken or match.claim.status is not ClaimStatus.verified:
            continue
        distance = abs(match.claim.value - before.claim.value) / scale
        if distance <= RELATIVE_PAIRING_WINDOW and (best is None or distance < best[0]):
            best = (distance, index)
    return None if best is None else best[1]


def _round_records(
    section: ReportSection,
    before: Sequence[Match],
    after: Sequence[Match],
) -> tuple[list[Repair], list[float]]:
    """Pair one round's failed claims with what replaced them; return the rows and what went."""
    rows: list[Repair] = []
    removed: list[float] = []
    taken: set[int] = set()
    for match in before:
        index = _pair(match, after, taken)
        if index is None:
            removed.append(match.claim.value)
            continue
        taken.add(index)
        replacement = after[index].claim
        rows.append(
            Repair(
                section=section,
                claim_id=match.claim.id,
                before=RepairSide(value=match.claim.value, status=match.claim.status),
                after=RepairSide(value=replacement.value, status=replacement.status),
                instruction=match.message or "the claim did not verify",
            )
        )
    return rows, removed


def repair_sections(
    drafts: Sequence[SectionDraft],
    *,
    drafter: Drafter,
    verify: Verify,
    inputs: Mapping[ReportSection, DraftInputs],
    trace: TraceWriter | None = None,
    max_rounds: int = MAX_REPAIR_ROUNDS,
) -> RepairOutcome:
    """Re-draft every section that holds an unverified claim, at most twice each.

    Args:
        drafts: The sections as first drafted, extracted and matched.
        drafter: The drafter, which is asked for a new draft with the problems listed.
        verify: Extract and match one section's markdown.
        inputs: Per section, what it needs to be drafted again.
        trace: The run's trace; one ``repair`` event per round.
        max_rounds: How many rounds one section may have. Spec section 3.11 says two.

    Returns:
        The sections after the loop, the repair records, and how many rounds ran.
    """
    outcome = RepairOutcome(drafts=list(drafts))
    for position, draft in enumerate(outcome.drafts):
        for _ in range(max_rounds):
            failures = draft.failures
            if not failures:
                break
            problems = draft.problems
            given = inputs.get(draft.section, DraftInputs())
            markdown = drafter.draft(
                draft.brief,
                artifacts=given.artifacts,
                spans=given.spans,
                candidates=given.candidates,
                findings=given.findings,
                previous=draft.markdown,
                problems=problems,
            )
            extraction, matches = verify(draft.section, markdown)
            rows, removed = _round_records(draft.section, failures, matches)
            draft = SectionDraft(
                brief=draft.brief,
                markdown=markdown,
                extraction=extraction,
                matches=matches,
                rounds=draft.rounds + 1,
            )
            outcome.drafts[position] = draft
            outcome.repairs.extend(rows)
            outcome.rounds += 1
            if trace is not None:
                trace.emit(
                    EventType.repair,
                    section=draft.section.value,
                    round=draft.rounds,
                    flagged=[match.claim.id for match in failures],
                    instructions=problems,
                    repaired=[row.claim_id for row in rows if row.after.status == "verified"],
                    removed=removed,
                    still_failing=[
                        match.claim.id
                        for match in matches
                        if match.claim.status is not ClaimStatus.verified
                    ],
                )
    return outcome


def is_wrapped(markdown: str, start: int) -> bool:
    """Whether the token at this offset already sits inside an ``⟦unverified: …⟧`` wrapper.

    Args:
        markdown: The section's prose.
        start: The offset of the token's first character.

    Returns:
        ``True`` when the nearest wrapper marker before the token is an opening one.
    """
    opened = markdown.rfind(UNVERIFIED_OPEN, 0, start)
    if opened < 0:
        return False
    closed = markdown.rfind(UNVERIFIED_CLOSE, 0, start)
    return closed < opened


def wrap_unverified(markdown: str, claims: Sequence[VerifiedClaim]) -> str:
    """Wrap every number of a section that did not verify, in place, and leave the rest alone.

    Args:
        markdown: The section's prose, as drafted.
        claims: The section's claims, verified and not.

    Returns:
        The prose with each unverified number wrapped ``⟦unverified: <number>⟧``. The token is
        wrapped as the drafter wrote it, thousands separators and per cent sign included, so the
        report still reads as a sentence.

    Only tokens the pre-pass would have counted are candidates. A claim whose value happens to
    match digits inside a citation's hash must not turn ``[[art:6bff3109:...]]`` into
    ``[[art:⟦unverified: 6⟧bff3109:...]]``, which is not a citation at all.
    """
    failed = [claim for claim in claims if claim.status is not ClaimStatus.verified]
    if not failed:
        return markdown
    spans = numeric_tokens(masked_prose(markdown))
    used: set[int] = set()
    chosen: list[tuple[int, str]] = []
    for claim in failed:
        for start, token in spans:
            if start in used or token_value(token) != claim.value:
                continue
            if is_wrapped(markdown, start):
                continue
            used.add(start)
            chosen.append((start, token))
            break
    result = markdown
    for start, token in sorted(chosen, reverse=True):
        result = (
            result[:start]
            + UNVERIFIED_OPEN
            + token
            + UNVERIFIED_CLOSE
            + result[start + len(token) :]
        )
    return result


def wrapped_values(text: str) -> list[float]:
    """Return the numbers a piece of prose wraps as unverified.

    Args:
        text: Any part of a report.

    Returns:
        One value per wrapper, in order, so the renderer can check that every unverified claim has
        one and that no wrapper stands for a claim that verified.
    """
    values: list[float] = []
    position = text.find(UNVERIFIED_OPEN)
    while position >= 0:
        start = position + len(UNVERIFIED_OPEN)
        end = text.find(UNVERIFIED_CLOSE, start)
        if end < 0:
            break
        body = text[start:end].strip()
        tokens = numeric_tokens(body)
        if tokens:
            values.append(token_value(tokens[0][1]))
        position = text.find(UNVERIFIED_OPEN, end)
    return values
