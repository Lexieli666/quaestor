"""Extraction: one model call per section, then a regex pre-pass that owns the denominator.

Spec section 3.10. The extractor is the one place in the verifier where a model is asked for
anything, and it is asked for a list, not a judgement: every number in the section's prose, with
the unit it is written in, the metric and split it is about, the citation it carries, and the
comparison it makes. Nothing it returns is trusted -- :mod:`quaestor.verifier.match` resolves
every citation itself -- but an extractor that simply *omitted* a number would shrink the
denominator of grounding precision, and a headline that improves when the extractor gets lazier is
worthless.

So the model does not own the denominator. A deterministic pre-pass tokenises the same prose,
after masking the six classes of excluded token D-015 fixed, and **that pre-pass defines the set of
eligible numbers**; the model only classifies them. The tokeniser and the exclusion rules live in
:mod:`quaestor.verifier.tokens`, which is also what the repair loop and the renderer read, so that
a number is a claim in all three places or in none (D-084). A numeric token the model did not
return becomes a claim with status ``unattributed``, so the denominator cannot be lowered by
omission; a claim the model returned for a token the pre-pass excluded is dropped and recorded
under ``extractor_returned_excluded_token``, so the denominator cannot be *raised* by an extractor
that claims the digits of a hash either (D-077). The exclusion list -- with the tokens actually
excluded -- is written into ``claims.json`` so that a reader can audit what was left out.

The unit the pre-pass works in is a **line**: the report format writes one sentence, or one table
row, per line, so a line is the sentence a claim quotes. The model is shown the prose with every
line numbered and returns that number rather than the line's text (D-085): the first live run spent
63,865 of its 92,196 output tokens re-typing prose the caller already had. Within a line, tokens
are matched to the model's claims by value and in order, which is what lets a sentence that says
"0.7412 against 0.7538" attach the right citation to the right number without any model
involvement. The rejected alternative was matching by string offset inside the sentence, which
fails the moment the drafter writes ``3,500`` and the extractor returns ``3500``; see
``docs/DESIGN.md``, Phase 7.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from typing import Any, Final

from pydantic import BaseModel, ConfigDict, Field

from ..llm.base import LLM
from ..llm.structured import structured
from ..trace import TraceWriter
from ..vocab import ReportSection
from .claim import Claim, ClaimSource, Comparison, SplitName, Unit
from .tokens import (
    EXTRACTOR_RETURNED_EXCLUDED,
    NUMERIC_TOKEN_RE,
    EligibleNumbers,
    ExcludedToken,
    Exclusion,
    drafted_prose,
    eligible_numbers,
    exclusions_of,
    numeric_tokens,
    token_value,
)

__all__ = [
    "EXTRACTION_INSTRUCTION",
    "EXTRACTOR_RETURNED_EXCLUDED",
    "EXTRACT_PURPOSE",
    "NUMBERED_LINE_RE",
    "NUMERIC_TOKEN_RE",
    "ExcludedToken",
    "Exclusion",
    "ExtractedClaim",
    "ExtractedClaims",
    "Extraction",
    "drafted_prose",
    "eligible_numbers",
    "extract",
    "extraction_from",
    "merge_exclusions",
    "numbered_lines",
    "numbered_prose",
    "numeric_tokens",
    "token_value",
]

EXTRACT_PURPOSE: Final = "extract"
"""The ``llm_call`` purpose recorded for an extraction, so the study can count them."""

NUMBERED_LINE_RE: Final = re.compile(r"^[ \t]*(?P<number>\d+)\|[ ]?(?P<line>.*)$")
"""One line of the numbered prose the extraction prompt shows: ``  12| The test AUC is …``."""

EXTRACTION_INSTRUCTION: Final = """\
You are extracting the numeric claims of one section of a model-validation report, so that each
can be checked against the artifact it cites. Section: {section}.

The prose is printed below one line per line, each prefixed with its own number and a vertical
bar. List EVERY number that appears in the prose, in the order it appears, including numbers that
appear inside a citation's logical name and numbers written with a thousands separator or a per
cent sign. For each one:

- "line" is the number printed to the left of the line the number appears on. Give the number
  only; do not copy the line's text back, and do not count the prefix itself as a number.
- "value" is the number as written, with thousands separators and the per cent sign removed:
  "3,500" is 3500, "22.0%" is 22.0.
- "unit" is "percent" when the number is written with a per cent sign, "count" for a number of
  rows, features or events, "currency", "bp" for basis points, "months" for a horizon, and
  "ratio" for every other dimensionless quantity (AUC, PSI, VIF, a coefficient, a lift).
- "metric" is what the number measures, taken from the logical name of the artifact it cites
  (auc, brier, psi, vif, calibration_slope, delta_auc, coefficient, event_rate, ...), or null.
- "split" is train, test, out_of_time or vintage_holdout, or null.
- "comparison" is "eq" for a number that equals its artifact; "delta" for a difference written
  "from a to b" or "a gap of x", whose value is the second cited artifact minus the first; and
  "ratio" for a number written as one artifact divided by another. A delta or ratio carries TWO
  adjacent citations, in that order.
- "citation" is the [[art:...]] token the number carries, copied exactly, or null when the
  sentence carries none. Do not invent a citation and do not move one from another number.
- "rounding" is the number of decimals the prose wrote when it wrote fewer than the artifact has
  (2 for a lift written 2.24), or null.

Return every number even when it has no citation: a number you leave out is still counted, and
counted against the report.

Prose:
{prose}
"""
"""The instruction of spec section 3.10, made explicit enough to be answered the same way twice."""


class ExtractedClaim(BaseModel):
    """One claim as the model returns it: the grammar minus the fields the caller already knows.

    ``text``, ``section``, ``id`` and ``source`` are not asked for. The caller knows which section
    it passed in, the id is a hash of the other three fields, the source of an extraction is
    always ``report``, and the text is the line the model named -- which the caller has in front
    of it, so asking for it back costs output tokens and adds a way for the answer to disagree
    with the prose (D-063, D-085).

    Attributes:
        line: The 1-based number of the line the number appears on, as the prompt printed it.
        value: The number as written, separators and per cent sign removed.
        unit: How it is written.
        metric: What it measures, or ``None``.
        split: Which split it is about, or ``None``.
        comparison: ``eq``, ``delta`` or ``ratio``.
        citation: The citation the number carries, or ``None``.
        rounding: Decimals the prose used, or ``None``.
    """

    model_config = ConfigDict(extra="forbid")

    line: int = Field(ge=1)
    value: float
    unit: Unit = Unit.ratio
    metric: str | None = None
    split: SplitName | None = None
    comparison: Comparison = Comparison.eq
    citation: str | None = None
    rounding: int | None = Field(default=None, ge=0)

    def to_claim(self, section: ReportSection, text: str) -> Claim:
        """Return the full :class:`Claim` for one section.

        Args:
            section: The section the extraction was run over.
            text: The line :attr:`line` names, which the caller resolved from the prose it sent.

        Returns:
            The claim, with its id computed and its source set to ``report``.
        """
        return Claim(
            text=text,
            value=self.value,
            unit=self.unit,
            metric=self.metric,
            split=self.split,
            comparison=self.comparison,
            citation=self.citation,
            rounding=self.rounding,
            section=section,
            source=ClaimSource.report,
        )


class ExtractedClaims(BaseModel):
    """The JSON object the extractor is asked for: a list of claims under one key.

    A bare JSON array is a shape more models get wrong than a single-key object, and
    :func:`~quaestor.llm.structured.structured` validates a ``BaseModel``, not a list.

    Attributes:
        claims: The claims, in the order the numbers appear.
    """

    model_config = ConfigDict(extra="forbid")

    claims: list[ExtractedClaim] = Field(default_factory=list)


class Extraction(BaseModel):
    """What one section's extraction produced: the claims, the pre-pass's additions, the audit.

    Spec section 3.10 writes the extractor's signature as ``-> list[Claim]``. That list is
    :attr:`claims`; the record carries two more things the spec's own text requires and a bare
    list cannot hold -- which of the claims the pre-pass added (they are ``unattributed``, not
    ``unsupported``, and the matcher has to be able to tell) and the exclusion list that
    ``claims.json`` must publish (DECISIONS D-064).

    Attributes:
        section: The section extracted.
        claims: Every claim, the model's and the pre-pass's, in prose order.
        unattributed: The ids of the claims the pre-pass added.
        exclusions: The classes of numeric token that were excluded, with examples.
        n_excluded_tokens: How many numeric tokens were excluded in total, which Appendix A
            prints so that the size of the exclusion is visible next to the precision. Every
            claim the pre-pass dropped as ineligible is counted here too, for the same reason.
        n_from_model: How many claims the model returned, including any that were dropped, so
            extraction recall is measurable against what the model actually said.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    section: ReportSection
    claims: list[Claim] = Field(default_factory=list)
    unattributed: list[str] = Field(default_factory=list)
    exclusions: list[Exclusion] = Field(default_factory=list)
    n_excluded_tokens: int = 0
    n_from_model: int = 0

    @property
    def unattributed_ids(self) -> frozenset[str]:
        """The ids the matcher must mark ``unattributed`` rather than ``unsupported``."""
        return frozenset(self.unattributed)


def numbered_prose(prose: str) -> str:
    """Return the prose with every line prefixed by its own 1-based number and a vertical bar.

    This is the form the extraction prompt shows and the form :attr:`ExtractedClaim.line` refers
    to: line 1 is the first line of the prose, blank lines included, so that the numbering is a
    plain count and neither side has to agree about which lines were worth numbering.

    Args:
        prose: The section's prose, renderer blocks already removed.

    Returns:
        The numbered text, one line per input line.
    """
    lines = prose.split("\n")
    width = len(str(len(lines)))
    return "\n".join(f"{number:>{width}}| {line}" for number, line in enumerate(lines, 1))


def numbered_lines(numbered: str) -> dict[int, str]:
    """Return the lines of a numbered prose block, keyed by the number printed beside each.

    The inverse of :func:`numbered_prose`, for a caller that has the prompt and not the prose:
    the offline fake reads its own answer's line numbers back out of what it was sent, and a test
    reconstructs a live run's section from a recorded cassette.

    Args:
        numbered: The numbered block, as :func:`numbered_prose` writes it.

    Returns:
        Line number to line text, for every row that carries a number.
    """
    found: dict[int, str] = {}
    for row in numbered.split("\n"):
        match = NUMBERED_LINE_RE.match(row)
        if match is not None:
            found[int(match.group("number"))] = match.group("line")
    return found


def _assign_to_lines(
    claims: Sequence[Claim], lines: Sequence[str]
) -> tuple[dict[int, list[Claim]], list[Claim]]:
    """Group the model's claims by the line each one quotes, keeping the model's own order."""
    normalised = [" ".join(line.split()) for line in lines]
    assigned: dict[int, list[Claim]] = {}
    stray: list[Claim] = []
    for claim in claims:
        quoted = " ".join(claim.text.split())
        index = next((i for i, line in enumerate(normalised) if line == quoted), None)
        if index is None:
            index = next(
                (i for i, line in enumerate(normalised) if quoted and quoted in line), None
            )
        if index is None:
            stray.append(claim)
            continue
        assigned.setdefault(index, []).append(claim)
    return assigned, stray


def _infer_unit(token: str) -> Unit:
    """Guess the unit of a token the model never described.

    A per cent sign is decisive; an integer written with no decimal point is a count; anything
    else is a ratio. The guess only decides the tolerance recorded beside an ``unattributed``
    claim, which is never compared to anything, so a wrong guess cannot change a verdict.
    """
    if token.endswith("%"):
        return Unit.percent
    return Unit.count if "." not in token else Unit.ratio


def _as_written(claim: Claim) -> str:
    """Return the number of a dropped claim as its own sentence wrote it.

    Args:
        claim: The claim the pre-pass is dropping.

    Returns:
        The first numeric token of the claim's text whose value is the claim's value, so that the
        exclusion list quotes the report rather than a re-formatted float; ``repr`` of the value
        when the model quoted a sentence the number is not in.
    """
    for _, token in numeric_tokens(claim.text):
        if token_value(token) == claim.value:
            return token
    return repr(claim.value)


def _prepass(
    section: ReportSection,
    markdown: str,
    model_claims: Sequence[Claim],
    package_version: str | None,
    unplaceable: Sequence[float] = (),
) -> tuple[list[Claim], list[str], list[Exclusion], int]:
    """Tokenise the prose, add what the model missed and drop what it should not have returned.

    The pre-pass defines the set of eligible numbers -- :func:`~quaestor.verifier.tokens.
    eligible_numbers` is that definition -- and the model only classifies them. So the two
    directions are not symmetric. A numeric token of the masked prose that no returned claim
    accounts for becomes an ``unattributed`` claim -- the denominator cannot be lowered by
    omission. A claim the model returned that no eligible token accounts for is **dropped**, and
    recorded under :data:`~quaestor.verifier.tokens.EXTRACTOR_RETURNED_EXCLUDED`: it is a number
    from inside inline code, a citation's hash, a heading or a renderer block, all of which D-015
    excluded, or a number that is not in the section at all (DECISIONS D-077).

    A claim is matched to a token in two passes, both by value. The first is within the line the
    claim quotes, which is what attaches the right citation to the right number in a sentence that
    writes two. The second offers what is left over to any unfilled token anywhere in the section,
    so that an extractor that named the wrong line still has its citation used rather than thrown
    away.

    Args:
        section: The section being extracted.
        markdown: The section as written.
        model_claims: The claims the model returned, already resolved to their lines.
        package_version: The package's version string, so that "version 1.0" is excluded.
        unplaceable: Values the model returned whose line number was not in the prose at all;
            they are dropped exactly as an ineligible token's claim is.

    Returns:
        The claims in prose order, the ids the pre-pass added, the exclusion list, and how many
        tokens were excluded in total.
    """
    eligible: EligibleNumbers = eligible_numbers(markdown, package_version=package_version)
    lines = eligible.lines
    assigned, stray = _assign_to_lines(model_claims, lines)

    pools = {index: list(claims) for index, claims in assigned.items()}
    filled: dict[int, Claim] = {}
    for position, token in enumerate(eligible.tokens):
        pool = pools.get(token.line, [])
        match = next((claim for claim in pool if claim.value == token.value), None)
        if match is not None:
            pool.remove(match)
            filled[position] = match
    leftover = [claim for _, pool in sorted(pools.items()) for claim in pool] + list(stray)
    for position, token in enumerate(eligible.tokens):
        if position in filled:
            continue
        match = next((claim for claim in leftover if claim.value == token.value), None)
        if match is not None:
            leftover.remove(match)
            filled[position] = match

    ordered: list[Claim] = []
    unattributed: list[str] = []
    for position, token in enumerate(eligible.tokens):
        claim = filled.get(position)
        if claim is None:
            claim = Claim(
                text=lines[token.line],
                value=token.value,
                unit=_infer_unit(token.text),
                section=section,
                source=ClaimSource.report,
            )
            unattributed.append(claim.id)
        ordered.append(claim)
    excluded = (
        list(eligible.excluded)
        + [
            ExcludedToken(pattern=EXTRACTOR_RETURNED_EXCLUDED, text=_as_written(claim))
            for claim in leftover
        ]
        + [
            ExcludedToken(pattern=EXTRACTOR_RETURNED_EXCLUDED, text=repr(float(value)))
            for value in unplaceable
        ]
    )
    return ordered, unattributed, exclusions_of(excluded), len(excluded)


def extraction_from(
    section: ReportSection | str,
    markdown: str,
    claims: Sequence[Claim],
    *,
    package_version: str | None = None,
) -> Extraction:
    """Run the pre-pass over a section whose claims are already known, with no model call.

    This is the half of :func:`extract` that follows the model call, exposed on its own for the
    ``rules_only`` configuration of spec section 3.13, whose template writes its own claims as it
    writes its prose and so has nothing to ask a model for. The pre-pass still runs, and still
    owns the denominator: a number the template wrote and did not declare becomes an
    ``unattributed`` claim exactly as a drafter's would.

    Args:
        section: Which of the seven sections this is.
        markdown: The section as written.
        claims: The claims whose author already knows what they are.
        package_version: The package's version string, so that "version 1.0" is excluded.

    Returns:
        The extraction, with ``n_from_model`` counting the claims that were handed in.
    """
    section = ReportSection(section)
    given = list(claims)
    ordered, unattributed, exclusions, n_excluded = _prepass(
        section, markdown, given, package_version
    )
    return Extraction(
        section=section,
        claims=ordered,
        unattributed=unattributed,
        exclusions=exclusions,
        n_excluded_tokens=n_excluded,
        n_from_model=len(given),
    )


def extract(
    section: ReportSection | str,
    markdown: str,
    llm: LLM,
    *,
    package_version: str | None = None,
    trace: TraceWriter | None = None,
    **params: Any,
) -> Extraction:
    """Extract every numeric claim of one drafted section.

    One :func:`~quaestor.llm.structured.structured` call asks the model for the claims, each named
    by the number of the line it is on; this function resolves those line numbers against the
    prose it sent, and the deterministic pre-pass then adds every numeric token the model did not
    return, as an ``unattributed`` claim, and drops every claim the model returned that no
    eligible token accounts for. The pre-pass owns the denominator of grounding precision, which
    is why it runs whatever the model answered and why the model's list is a classification of its
    tokens rather than a proposal of its own.

    Args:
        section: Which of the seven sections this is.
        markdown: The section as drafted, renderer blocks included; they are removed before the
            model sees them and are excluded from the pre-pass.
        llm: The provider. Tests pass a ``FakeLLM``; nothing here calls a live model.
        package_version: The package's version string, so that the ``1.0`` of "version 1.0" is
            excluded rather than counted as a claim (D-015).
        trace: The run's trace; the extraction is one ``llm_call`` event with purpose
            ``extract``, and a re-ask is one more with purpose ``reask``.
        **params: Passed to the provider, such as ``model``.

    Returns:
        The extraction: the claims in prose order, the ids the pre-pass added, and the exclusion
        list.

    Raises:
        LLMOutputError: The model did not return a valid list of claims in two attempts.
    """
    section = ReportSection(section)
    prose = drafted_prose(markdown)
    lines = prose.split("\n")
    answer = structured(
        llm,
        EXTRACTION_INSTRUCTION.format(section=section.value, prose=numbered_prose(prose)),
        ExtractedClaims,
        trace=trace,
        purpose=EXTRACT_PURPOSE,
        **params,
    )
    model_claims: list[Claim] = []
    unplaceable: list[float] = []
    for item in answer.claims:
        text = lines[item.line - 1].strip() if item.line <= len(lines) else ""
        if text:
            model_claims.append(item.to_claim(section, text))
        else:
            unplaceable.append(item.value)
    claims, unattributed, exclusions, n_excluded = _prepass(
        section, markdown, model_claims, package_version, unplaceable
    )
    return Extraction(
        section=section,
        claims=claims,
        unattributed=unattributed,
        exclusions=exclusions,
        n_excluded_tokens=n_excluded,
        n_from_model=len(answer.claims),
    )


def merge_exclusions(extractions: Iterable[Extraction]) -> list[Exclusion]:
    """Merge the exclusion lists of every section into the one ``claims.json`` publishes.

    Args:
        extractions: The per-section extractions of one report.

    Returns:
        One :class:`Exclusion` per class, examples deduplicated and in first-seen order.
    """
    found = [
        ExcludedToken(pattern=exclusion.pattern, text=example)
        for extraction in extractions
        for exclusion in extraction.exclusions
        for example in exclusion.examples
    ]
    return exclusions_of(found)
