"""Extraction: one model call per section, then a regex pre-pass that owns the denominator.

Spec section 3.10. The extractor is the one place in the verifier where a model is asked for
anything, and it is asked for a list, not a judgement: every number in the section's prose, with
the unit it is written in, the metric and split it is about, the citation it carries, and the
comparison it makes. Nothing it returns is trusted -- :mod:`quaestor.verifier.match` resolves
every citation itself -- but an extractor that simply *omitted* a number would shrink the
denominator of grounding precision, and a headline that improves when the extractor gets lazier is
worthless.

So the model does not own the denominator. A deterministic pre-pass tokenises the same prose,
after masking the six classes of excluded token D-015 fixed, and every numeric token the model did
not return becomes a claim with status ``unattributed``. The pre-pass can only ever *add* claims;
it is the floor under the denominator, and the exclusion list -- with the tokens it actually
excluded -- is written into ``claims.json`` so that a reader can audit what was left out.

The unit the pre-pass works in is a **line**: the report format writes one sentence, or one table
row, per line, so a line is the sentence a claim quotes. Within a line, tokens are matched to the
model's claims by value and in order, which is what lets a sentence that says "0.7412 against
0.7538" attach the right citation to the right number without any model involvement. The rejected
alternative was matching by string offset inside the sentence, which fails the moment the drafter
writes ``3,500`` and the extractor returns ``3500``; see ``docs/DESIGN.md``, Phase 7.
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

__all__ = [
    "EXTRACTION_INSTRUCTION",
    "EXTRACT_PURPOSE",
    "NUMERIC_TOKEN_RE",
    "ExcludedToken",
    "Exclusion",
    "ExtractedClaim",
    "ExtractedClaims",
    "Extraction",
    "drafted_prose",
    "extract",
    "merge_exclusions",
    "numeric_tokens",
    "token_value",
]

EXTRACT_PURPOSE: Final = "extract"
"""The ``llm_call`` purpose recorded for an extraction, so the study can count them."""

EXTRACTION_INSTRUCTION: Final = """\
You are extracting the numeric claims of one section of a model-validation report, so that each
can be checked against the artifact it cites. Section: {section}.

List EVERY number that appears in the prose below, in the order it appears, including numbers that
appear inside a citation's logical name and numbers written with a thousands separator or a per
cent sign. For each one:

- "text" is the whole line the number appears on, copied exactly, citations included.
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

NUMERIC_TOKEN_RE: Final = re.compile(r"(?<![\w.])-?\d[\d,]*(?:\.\d+)?%?")
"""Every numeric token in prose. The same expression ``tests/test_golden_spec.py`` check 7 uses."""

_RENDERER_BLOCK_RE: Final = re.compile(
    r"<!--\s*quaestor:renderer:begin.*?-->.*?<!--\s*quaestor:renderer:end\s*-->", re.DOTALL
)
"""A renderer block, begin marker to end marker. Nothing inside it was written by a model."""

_TABLE_DIRECTIVE_RE: Final = re.compile(r"\[\[table:[^\]]*\]\]")
"""A drafter's ``[[table:...]]`` directive, which the renderer replaces with a renderer block."""

_HEADING_RE: Final = re.compile(r"^[ \t]*#{1,6}[ \t].*$", re.MULTILINE)
"""A markdown heading. ``## 4. Outcomes analysis`` numbers the section, it does not claim a 4."""

_INLINE_CODE_RE: Final = re.compile(r"`[^`\n]*`")
"""Inline code: ``bill_mean_6m`` is a feature name, not a claim of six (D-015)."""

_ART_CITATION_RE: Final = re.compile(r"\[\[art:(?P<hash8>[0-9a-fA-F]+):[^\]]*\]\]")
"""An artifact citation. Its hash and its logical name both carry digits that are not claims."""

_REG_CITATION_RE: Final = re.compile(r"\[\[reg:(?P<body>[^\]]*)\]\]")
"""A regulatory citation: ``[[reg:SR26-2:V.1.b]]`` is a section id, not three numbers."""

_FINDING_ID_RE: Final = re.compile(r"\bF-\d{3}\b")
"""``F-001``: finding numbering."""

_SECTION_NUMBER_RE: Final = re.compile(r"§\s?\d+(?:\.\d+)*|^[ \t]*\d+\.(?=\s)", re.MULTILINE)
r"""Section and list numbering: ``§6``, and a ``1.`` that opens a line.

Anchored to the start of the line on purpose. An unanchored ``\d+\.`` followed by a space also
matches the ``0.`` of "no feature is flagged 0." and would silently delete a claim, which is the
failure mode an exclusion list is most dangerous for: it lowers the denominator invisibly."""

_REG_SECTION_ID_RE: Final = re.compile(
    r"\bSR\s?\d{2}-\d+\b|\bOCC\s?\d{4}-\d+\b|\b[IVX]+(?:\.\d+)+(?:\.[a-z])?\b"
)
"""A section id written in prose rather than inside a citation: ``V.1.c``, ``SR 11-7``."""


class ExcludedToken(BaseModel):
    """One numeric token the pre-pass deliberately ignored, and the class it fell into.

    Attributes:
        pattern: The exclusion class, as ``claims.json`` names it.
        text: The token as written.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    pattern: str
    text: str


class Exclusion(BaseModel):
    """A class of numeric token the regex pre-pass deliberately ignored, with examples.

    Attributes:
        pattern: The class name, as ``CLAIMS_SCHEMA.json`` and Appendix A print it.
        examples: The tokens actually excluded, deduplicated, in first-seen order.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    pattern: str
    examples: list[str] = Field(min_length=1)


class ExtractedClaim(BaseModel):
    """One claim as the model returns it: the grammar minus the fields the caller already knows.

    ``section``, ``id`` and ``source`` are not asked for. The caller knows which section it passed
    in, the id is a hash of the other three fields, and the source of an extraction is always
    ``report``; asking a model for a value the caller can compute is a way of being told a
    different one (DECISIONS D-063).

    Attributes:
        text: The line the number appears on.
        value: The number as written, separators and per cent sign removed.
        unit: How it is written.
        metric: What it measures, or ``None``.
        split: Which split it is about, or ``None``.
        comparison: ``eq``, ``delta`` or ``ratio``.
        citation: The citation the number carries, or ``None``.
        rounding: Decimals the prose used, or ``None``.
    """

    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)
    value: float
    unit: Unit = Unit.ratio
    metric: str | None = None
    split: SplitName | None = None
    comparison: Comparison = Comparison.eq
    citation: str | None = None
    rounding: int | None = Field(default=None, ge=0)

    def to_claim(self, section: ReportSection) -> Claim:
        """Return the full :class:`Claim` for one section.

        Args:
            section: The section the extraction was run over.

        Returns:
            The claim, with its id computed and its source set to ``report``.
        """
        return Claim(
            text=self.text,
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
            prints so that the size of the exclusion is visible next to the precision.
        n_from_model: How many claims the model returned, so extraction recall is measurable.
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


def drafted_prose(markdown: str) -> str:
    """Return the section's prose with every renderer block removed.

    Everything inside a renderer block was written by the renderer from an artifact, so no model
    produced it and there is nothing to verify (D-013). Removing it before the model sees it also
    keeps a ten-row table out of the extraction prompt.

    Args:
        markdown: The section as drafted and rendered.

    Returns:
        The prose, with renderer blocks replaced by a blank line.
    """
    return _RENDERER_BLOCK_RE.sub("\n", markdown)


def numeric_tokens(text: str) -> list[tuple[int, str]]:
    """Return every numeric token of a piece of text with its offset.

    Args:
        text: The text to scan.

    Returns:
        ``(offset, token)`` pairs, in order.
    """
    return [(match.start(), match.group(0)) for match in NUMERIC_TOKEN_RE.finditer(text)]


def token_value(token: str) -> float:
    """Return the number a token writes, without its separators or per cent sign.

    Args:
        token: A numeric token such as ``3,500`` or ``22.0%``.

    Returns:
        The number as written: ``3500.0``, ``22.0``.
    """
    return float(token.replace(",", "").rstrip("%"))


def _mask(
    text: str,
    pattern: re.Pattern[str],
    name: str,
    found: list[ExcludedToken],
    *,
    example: str = "match",
) -> str:
    """Blank out every match of one pattern, recording the numeric tokens it swallowed.

    Args:
        text: The text to mask, in place of which spaces are written so that every offset
            downstream still points where it did.
        pattern: What to mask.
        name: The exclusion class to record under.
        found: The running list of excluded tokens.
        example: What to record as the example -- ``"match"`` for a pattern that *is* the token
            (``§6``, ``F-001``, an inline code span), ``"token"`` for a region that merely
            contains tokens (a heading, a renderer block), or the name of a group, which is how a
            citation records the eight hex characters inside it. The first two record nothing
            when the region held no numeric token, because an exclusion list is a list of tokens
            that were excluded; a citation records unconditionally, because its hash and its
            logical name are excluded by construction whether or not this tokenizer would have
            picked a number out of them.

    Returns:
        The masked text, the same length as the input.
    """
    result = list(text)
    for match in pattern.finditer(text):
        tokens = [token for _, token in numeric_tokens(match.group(0))]
        grouped = example not in ("match", "token")
        if tokens or grouped:
            if example == "match":
                found.append(ExcludedToken(pattern=name, text=match.group(0)))
            elif example == "token":
                found.extend(ExcludedToken(pattern=name, text=token) for token in tokens)
            else:
                found.append(ExcludedToken(pattern=name, text=match.group(example)))
        for index in range(match.start(), match.end()):
            if result[index] != "\n":
                result[index] = " "
    return "".join(result)


def _mask_version(text: str, version: str | None, found: list[ExcludedToken]) -> str:
    """Blank out the package version string, which the front matter already states."""
    if not version or not NUMERIC_TOKEN_RE.fullmatch(version):
        return text
    pattern = re.compile(rf"(?<![\w.]){re.escape(version)}(?![\w.])")
    return _mask(text, pattern, "package_version", found)


def _masked(markdown: str, package_version: str | None) -> tuple[str, list[ExcludedToken]]:
    """Mask every excluded region of a section, in the order D-015 lists them."""
    found: list[ExcludedToken] = []
    text = _mask(markdown, _RENDERER_BLOCK_RE, "renderer_block", found, example="token")
    text = _mask(text, _TABLE_DIRECTIVE_RE, "renderer_block", found, example="token")
    text = _mask(text, _ART_CITATION_RE, "citation_hash", found, example="hash8")
    text = _mask(text, _REG_CITATION_RE, "regulatory_section_id", found, example="body")
    text = _mask(text, _INLINE_CODE_RE, "inline_code", found)
    text = _mask(text, _FINDING_ID_RE, "finding_id", found)
    text = _mask(text, _HEADING_RE, "section_number", found, example="token")
    text = _mask(text, _SECTION_NUMBER_RE, "section_number", found)
    text = _mask(text, _REG_SECTION_ID_RE, "regulatory_section_id", found)
    text = _mask_version(text, package_version, found)
    return text, found


_PATTERN_ORDER: Final = (
    "renderer_block",
    "section_number",
    "inline_code",
    "citation_hash",
    "regulatory_section_id",
    "finding_id",
    "package_version",
)
"""The order the exclusion list is written in, so two runs of one report produce one file."""


def _exclusions(found: Sequence[ExcludedToken]) -> list[Exclusion]:
    """Group the excluded tokens by class, deduplicating examples and keeping first-seen order."""
    grouped: dict[str, list[str]] = {}
    for item in found:
        examples = grouped.setdefault(item.pattern, [])
        if item.text not in examples:
            examples.append(item.text)
    return [
        Exclusion(pattern=name, examples=grouped[name])
        for name in _PATTERN_ORDER
        if name in grouped
    ]


def _line_spans(text: str) -> list[tuple[int, int]]:
    """Return the ``(start, end)`` offsets of every line that holds a non-space character."""
    spans: list[tuple[int, int]] = []
    offset = 0
    for line in text.split("\n"):
        if line.strip():
            spans.append((offset, offset + len(line)))
        offset += len(line) + 1
    return spans


def _normalise(text: str) -> str:
    """Collapse whitespace, so a claim's text can be compared with the line it came from."""
    return " ".join(text.split())


def _assign_to_lines(
    claims: Sequence[Claim], lines: Sequence[str]
) -> tuple[dict[int, list[Claim]], list[Claim]]:
    """Group the model's claims by the line each one quotes, keeping the model's own order."""
    normalised = [_normalise(line) for line in lines]
    assigned: dict[int, list[Claim]] = {}
    stray: list[Claim] = []
    for claim in claims:
        quoted = _normalise(claim.text)
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


def _prepass(
    section: ReportSection,
    markdown: str,
    model_claims: Sequence[Claim],
    package_version: str | None,
) -> tuple[list[Claim], list[str], list[Exclusion], int]:
    """Tokenise the prose and add a claim for every number the model did not return."""
    masked, excluded = _masked(markdown, package_version)
    spans = _line_spans(masked)
    lines = [markdown[start:end].strip() for start, end in spans]
    assigned, stray = _assign_to_lines(model_claims, lines)

    ordered: list[Claim] = []
    unattributed: list[str] = []
    for index, (start, end) in enumerate(spans):
        pool = list(assigned.get(index, []))
        for _, token in numeric_tokens(masked[start:end]):
            value = token_value(token)
            match = next((claim for claim in pool if claim.value == value), None)
            if match is not None:
                pool.remove(match)
                ordered.append(match)
                continue
            added = Claim(
                text=lines[index],
                value=value,
                unit=_infer_unit(token),
                section=section,
                source=ClaimSource.report,
            )
            ordered.append(added)
            unattributed.append(added.id)
        ordered.extend(pool)
    ordered.extend(stray)
    return ordered, unattributed, _exclusions(excluded), len(excluded)


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

    One :func:`~quaestor.llm.structured.structured` call asks the model for the claims; the
    deterministic pre-pass then adds every numeric token the model did not return, as an
    ``unattributed`` claim. The pre-pass is the denominator of grounding precision, which is why
    it runs whatever the model answered and can only add.

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
    answer = structured(
        llm,
        EXTRACTION_INSTRUCTION.format(section=section.value, prose=prose),
        ExtractedClaims,
        trace=trace,
        purpose=EXTRACT_PURPOSE,
        **params,
    )
    model_claims = [item.to_claim(section) for item in answer.claims]
    claims, unattributed, exclusions, n_excluded = _prepass(
        section, markdown, model_claims, package_version
    )
    return Extraction(
        section=section,
        claims=claims,
        unattributed=unattributed,
        exclusions=exclusions,
        n_excluded_tokens=n_excluded,
        n_from_model=len(model_claims),
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
    return _exclusions(found)
