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

The re-draft is asked for in whole and taken in part: only the lines that carried a flagged claim
are taken from it, and every other line of the section is kept byte-identical (D-109). A model
correcting one sentence rewrites its neighbours too, and a rewritten neighbour whose citations all
resolve is a sentence no part of this pipeline can see is wrong.

Each round is one ``repair`` trace event and one or more ``repairs`` entries in ``claims.json``.
Pairing a claim before a round with the claim that replaced it after it is done by id first -- an
uncited number that gains its citation keeps its id, because the id is a hash of section, text and
value and only the citation moved -- then by nearest unpaired verified value **among the claims
that are the same statement**, which is the same line or the same cited logical name (D-105), and a
number the drafter removed instead of citing leaves no ``after`` side and is recorded on the trace
event alone (DECISIONS D-073).
"""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Final

from ..findings import Finding, FindingCandidate
from ..trace import EventType, TraceWriter
from ..verifier.claim import ClaimStatus, VerifiedClaim
from ..verifier.claims_doc import Repair, RepairSide
from ..verifier.extract import Extraction
from ..verifier.match import Match
from ..verifier.tokens import NUMERIC_TOKEN_RE, eligible_numbers, numeric_tokens, token_value
from ..vocab import ReportSection
from .drafter import Drafter, GuidanceSpan
from .sections import ArtifactBrief, FollowUp, SectionBrief

__all__ = [
    "MAX_REPAIR_ROUNDS",
    "REDRAFT_SIMILARITY",
    "UNVERIFIED_CLOSE",
    "UNVERIFIED_OPEN",
    "DraftInputs",
    "RepairOutcome",
    "SectionDraft",
    "Verify",
    "is_wrapped",
    "repair_sections",
    "scope_to_flagged_lines",
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

Nearness is necessary and not sufficient: :func:`_same_statement` decides which claims the window
is even applied to (D-105).
"""

REDRAFT_SIMILARITY: Final = 0.5
"""How much of a line a re-draft must keep for the new line to be read as that line rewritten.

A repair round re-drafts the whole section and only the flagged lines are taken from it (D-109),
so each line the drafter returns has to be attributed to the line of the previous draft it is a
rewrite of. The attribution itself is the argument of the whole line against every line of the
previous draft: a new line belongs to the old line it most resembles, which is what keeps the
re-drafted sibling of a flagged paragraph attached to its own original instead of being spliced
over the flagged one. This is only the floor beneath that -- a new line that resembles even its
best old line this little is a sentence the drafter wrote fresh, and it is not taken.

On the fifth live run the five flagged lines resemble their own replacements at 0.839, 0.941,
0.942, 0.974 and 0.981, so the floor has a wide margin under every rewrite that run made. It is
generous on purpose: with the argmax doing the discriminating, being wrong towards the floor
costs a line the drafter meant to keep, and a repair round that silently shortens a section is a
worse outcome than one that keeps a sentence it could have dropped.
"""

_CITED_NAME_RE: Final = re.compile(r"\[\[art:[0-9a-fA-F]+:(?P<name>[^\]#]+)")
"""The logical name inside an artifact citation, which is what says two claims are about one thing.

The ``#`` path is deliberately not part of the name: ``run.model_summary#coefficients.age.value``
and ``run.model_summary#coefficients.age.se`` are two numbers of one artifact, and a re-draft that
corrects one of them is still a repair of the sentence that cited it.
"""

_CITATION_TOKEN_RE: Final = re.compile(r"\[\[[^\]]*\]\]")
"""Any citation, removed before two lines are compared: gaining one is what a repair often is."""

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
        follow_ups: The bounded loop's executed steps this section is asked to report (D-101).
    """

    artifacts: Sequence[ArtifactBrief] = ()
    spans: Sequence[GuidanceSpan] = ()
    candidates: Sequence[FindingCandidate] = ()
    findings: Sequence[Finding] = ()
    follow_ups: Sequence[FollowUp] = ()


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


def _logical_names(claim: VerifiedClaim) -> frozenset[str]:
    """Return the logical names a claim's citation resolves to, or nothing when it has none."""
    return frozenset(match.group("name") for match in _CITED_NAME_RE.finditer(claim.citation or ""))


def _uncited(text: str) -> str:
    """Return a line with its citations removed and its whitespace collapsed."""
    return " ".join(_CITATION_TOKEN_RE.sub(" ", text).split())


def _skeleton(text: str) -> str:
    """Return a claim's line with its citations and its numbers removed, whitespace collapsed.

    What is left is the sentence the drafter wrote around the number, which is what survives the
    two things a repair does to a line: it corrects the number, or it attaches the citation the
    number was missing. Both change ``Claim.text`` -- the text is the whole line, citations
    included (D-085) -- and so both change the claim id, which is why the id-first pass cannot
    recognise them and something weaker than equality is needed.
    """
    return " ".join(NUMERIC_TOKEN_RE.sub(" ", _uncited(text)).split())


def _same_statement(before: Match, after: Match) -> bool:
    """Whether two claims are close enough to be the same statement, corrected.

    The two grounds of D-105 are not alternatives, they are ordered by what the flagged claim
    carries. **A flagged claim that cites a logical name is about that quantity**, so its
    replacement has to cite it too, wherever in the section the re-draft moved the sentence to.
    **Only a flagged claim with no citation falls back on the line**: the sentence with its numbers
    and its citations taken out, which is what a re-draft keeps while it attaches the citation the
    number was missing, and which is the one case where there is no name to compare.

    Reading the two as alternatives is what the fifth live run paid for. The four sub-population
    paragraphs of its section 4 are written to one sentence skeleton, so the flagged
    ``metrics.train.sub.limit_bal_low.n`` of 10160 and the untouched, verified
    ``metrics.train.sub.utilisation_high.n`` of 10500 had the same line with their numbers and
    citations removed, and 10500 is inside the window of 10160 (DECISIONS D-111).
    """
    names = _logical_names(before.claim)
    if names:
        return bool(names & _logical_names(after.claim))
    return _skeleton(before.claim.text) == _skeleton(after.claim.text)


def _collapsed(text: str) -> str:
    """Return a line with its whitespace collapsed, which is how two lines are compared here."""
    return " ".join(text.split())


def _flagged_line_numbers(lines: Sequence[str], failures: Sequence[Match]) -> set[int]:
    """Return the indices of the previous draft's lines that carry a flagged claim.

    ``Claim.text`` *is* the line the number sits on -- the extractor returns the line's number and
    the caller resolves it against the prose it sent (D-085), and the pre-pass builds an
    unattributed claim from the same line -- so the flagged lines are found by matching that text
    back against the draft, with whitespace collapsed on both sides because the pre-pass strips it.
    """
    wanted = {_collapsed(match.claim.text) for match in failures}
    return {index for index, line in enumerate(lines) if _collapsed(line) in wanted}


def _closest(lines: Sequence[str], candidate: str) -> int | None:
    """Return the index of the line of the previous draft this new line is a rewrite of.

    The line of the previous draft the candidate most resembles, ties going to the earlier one,
    and ``None`` when even that one shares too little with it: below
    :data:`REDRAFT_SIMILARITY` and not the same sentence with its numbers and citations taken out.

    The argmax is the part that matters. A section whose paragraphs are written to one skeleton --
    the fifth live run's four sub-population paragraphs -- offers several old lines that read alike,
    and the re-drafted sibling of a flagged line resembles *its own* original more than it
    resembles the flagged one, because its numbers are its own. Attributing every new line before
    deciding what to keep is therefore what stops the sibling being spliced over the flagged line.

    Citations are removed before the comparison, for the reason :func:`_skeleton` removes them:
    attaching one is a thing a repair *does*, and a citation is thirty-odd characters of hash and
    logical name that two lines of a section often share exactly. Left in, they made a line whose
    citation was being added resemble any other line carrying that citation more than its own
    former self.
    """
    wanted = _uncited(candidate)
    best: tuple[float, int] | None = None
    for index, line in enumerate(lines):
        if not line.strip():
            continue
        ratio = SequenceMatcher(None, _uncited(line), wanted).ratio()
        if best is None or ratio > best[0]:
            best = (ratio, index)
    if best is None or best[0] < REDRAFT_SIMILARITY:
        return None
    return best[1]


def scope_to_flagged_lines(
    previous: str, redraft: str, failures: Sequence[Match]
) -> tuple[str, int]:
    """Take from a re-draft only the lines that carried a flagged claim (DECISIONS D-109).

    A repair round asks for the whole section because a sentence cannot be corrected out of its
    context, and the model returns the whole section -- including lines nothing was wrong with. On
    the fifth live run the round on section 4 flagged four numbers and the re-draft also rewrote an
    unflagged line of the same paragraph into "the slice AUC falls below its split's by 0.007286 on
    test and by -0.02732 [[art:41fca294:metrics.train.sub.utilisation_high.auc_gap]] is not the
    figure for this slice; on train the gap is -0.001109", a sentence about another slice spliced
    into this one. Every citation in it resolved, so grounding precision was 1.0000 and nothing
    downstream could see it: the verifier checks that a number matches its artifact, not that a
    sentence is about the thing the paragraph is about.

    So the re-draft is scoped. Every line of the previous draft that carried no flagged claim is
    kept byte-identical; a flagged line is replaced by the line of the re-draft that replaced it,
    or dropped where the re-draft dropped it; and a line the re-draft added elsewhere is not taken.

    Args:
        previous: The section as it stood before this round.
        redraft: What the drafter returned.
        failures: The claims that did not verify, whose ``text`` is the line each sits on.

    Returns:
        The section with the flagged lines re-drafted and nothing else changed, and how many of
        those lines the re-draft actually changed.
    """
    lines = previous.split("\n")
    flagged = _flagged_line_numbers(lines, failures)
    if not flagged:
        # Nothing in the previous draft carries a flagged claim -- the section was drafted from a
        # prose the failures did not come from -- so there is no line to scope the re-draft to.
        return redraft, len(redraft.split("\n"))
    taken: dict[int, list[str]] = {}
    for candidate in redraft.split("\n"):
        if not candidate.strip():
            continue
        index = _closest(lines, candidate)
        if index is not None and index in flagged:
            taken.setdefault(index, []).append(candidate)
    result: list[str] = []
    changed = 0
    for index, line in enumerate(lines):
        if index not in flagged:
            result.append(line)
            continue
        rewritten = taken.get(index, [])
        if rewritten != [line]:
            changed += 1
        result.extend(rewritten)
    return "\n".join(result), changed


def _pair(before: Match, after: Sequence[Match], taken: set[int]) -> int | None:
    """Return the index in ``after`` of the claim that replaced ``before``, or ``None``.

    By id first: a number that gained a citation keeps its id, because the id hashes the section,
    the text and the value and only the citation moved. Then by nearest verified value inside
    :data:`RELATIVE_PAIRING_WINDOW`, which is the drafter correcting a number it got wrong -- but
    only among the claims :func:`_same_statement` admits, because a value on its own is not an
    identity. On the fourth live run the flagged ``1.92`` of "refitting without utilisation
    changes test AUC by 1.92e-05" was paired with the surviving, unrelated ``2`` of "2 are known
    at origination", which sits inside the window of anything near two: Appendix A then reported
    one claim rewritten and five numbers removed of a round that rewrote none and removed six,
    and the repairs table carried a row joining two sentences with nothing to do with each other
    (DECISIONS D-105).
    """
    for index, match in enumerate(after):
        if index not in taken and match.claim.id == before.claim.id:
            return index
    best: tuple[float, int] | None = None
    scale = max(abs(before.claim.value), 1e-9)
    for index, match in enumerate(after):
        if index in taken or match.claim.status is not ClaimStatus.verified:
            continue
        if not _same_statement(before, match):
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
            returned = drafter.draft(
                draft.brief,
                artifacts=given.artifacts,
                spans=given.spans,
                candidates=given.candidates,
                findings=given.findings,
                follow_ups=given.follow_ups,
                previous=draft.markdown,
                problems=problems,
            )
            markdown, redrafted = scope_to_flagged_lines(draft.markdown, returned, failures)
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
                    lines_redrafted=redrafted,
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


def wrap_unverified(
    markdown: str,
    claims: Sequence[VerifiedClaim],
    *,
    package_version: str | None = None,
) -> str:
    """Wrap every number of a section that did not verify, in place, and leave the rest alone.

    Args:
        markdown: The section's prose, as drafted.
        claims: The section's claims, verified and not.
        package_version: The package's version string, so that the wrapper and the pre-pass agree
            about which tokens exist (D-084).

    Returns:
        The prose with each unverified number wrapped ``⟦unverified: <number>⟧``. The token is
        wrapped as the drafter wrote it, thousands separators and per cent sign included, so the
        report still reads as a sentence.

    Only tokens the pre-pass would have counted are candidates -- the candidates are literally
    :func:`~quaestor.verifier.tokens.eligible_numbers`' own. A claim whose value happens to match
    digits inside a citation's hash must not turn ``[[art:6bff3109:...]]`` into
    ``[[art:⟦unverified: 6⟧bff3109:...]]``, which is not a citation at all.
    """
    failed = [claim for claim in claims if claim.status is not ClaimStatus.verified]
    if not failed:
        return markdown
    eligible = eligible_numbers(markdown, package_version=package_version)
    spans = [(token.offset, token.text) for token in eligible.tokens]
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
