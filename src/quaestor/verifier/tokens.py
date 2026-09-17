"""The eligible-number tokenizer: one definition of "a number in the prose", for every caller.

Spec section 3.10 and DECISIONS D-015. Three parts of the pipeline have to agree about which
numeric tokens of a drafted section are *claims*: the extraction pre-pass, which builds the
denominator of grounding precision; the repair loop, which wraps a number it could not verify; and
the renderer, which refuses under ``full_agent`` to write a report whose prose carries a number no
verified claim accounts for. Three callers reading the same rule out of three code paths is three
chances to disagree, and the first live validation lost a whole run to exactly that: the pre-pass
excluded the ``1.0`` of "credit_default 1.0" as the package version, the renderer -- which called
the masking helper without knowing the version -- did not, and a report in which every one of 140
claims verified was refused for an uncovered number that was never a claim (DECISIONS D-084).

So the rule lives here, once, as :func:`eligible_numbers`, and every caller reads it from here.
The function returns the masked text, the section's lines, the eligible tokens with their offsets,
and the tokens it excluded with the class each fell into -- everything any of the three callers
needs, so that none of them has a reason to re-derive a part of it.

The exclusion classes are D-015's six, in D-015's order: a renderer block or a ``[[table:...]]``
directive (nothing inside was written by a model), the hex characters and the logical name inside
an artifact citation, a regulatory section id, inline code, a finding id, section and list
numbering -- including a cross-reference to a section of this report written in words, "Section 4"
(D-112) -- and the package version string, plus three added since: a reference to an entry of
this project's own decision log, ``D-050`` (D-116), an integer that labels a bin rather than
measuring one, ``decile 1`` (D-166), and the digits of an algorithm or standard name, ``SHA-256``
(D-169). Masking writes spaces over each region rather
than deleting it, so every offset a caller computes still points where it did in the original text.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Final, NamedTuple

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "EXTRACTOR_RETURNED_EXCLUDED",
    "NUMERIC_TOKEN_RE",
    "EligibleNumbers",
    "EligibleToken",
    "ExcludedToken",
    "Exclusion",
    "drafted_prose",
    "eligible_numbers",
    "exclusions_of",
    "line_spans",
    "numeric_tokens",
    "token_value",
]

EXTRACTOR_RETURNED_EXCLUDED: Final = "extractor_returned_excluded_token"
"""The exclusion class for a claim the model returned that the pre-pass had already excluded.

The pre-pass defines which numbers are eligible; the model only classifies them. A claim it
returns for a token inside inline code, a citation's hash, a heading or a renderer block is
therefore dropped rather than counted, and the number it wrote is published here so that the
dropping is auditable rather than silent (DECISIONS D-077)."""

NUMERIC_TOKEN_RE: Final = re.compile(r"(?<![\w.])-?\d[\d,]*(?:\.\d+)?(?:[eE][+-]?\d+)?%?")
"""Every numeric token in prose. The same expression ``tests/test_golden_spec.py`` check 7 uses.

The exponent group is one token with the mantissa, not two numbers beside it. Without it
``1.92e-05`` tokenised as ``1.92`` and ``05``: the mantissa's own claim could never verify -- the
artifact holds 0.0000192 -- and the exponent's digits became a second, invented claim of five. All
six pre-repair failures of the fourth live ``credit_default`` run were that one defect, over the
three literals ``1.92e-05``, ``-5.589e-05`` and ``9.982e-06`` (DECISIONS D-099). The drafter writes
exponent notation because that is how ``json.dumps`` prints a value of 1.9e-05 at four significant
figures, so the tokenizer has to read what the prompt taught it to write.
"""

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

_DECISIONS_REFERENCE_RE: Final = re.compile(r"\bD-\d{3}\b")
"""``D-050``: a reference to an entry of this project's own decision log.

Section 4 of the third live ``credit_default`` run drafted "The declared bound on the train-to-test
AUC gap under rule O1 (D-050) is 0.08 [[art:630f28f4:threshold.O1.auc_gap]]", and the ``50`` was
counted in the denominator, flagged as unattributed and removed by a repair round that also lost the
sentence's second, verified ``0.08``. The drafter did not invent the reference: the artifact summary
it was shown reads "O1: the train-to-test AUC gap (D-050)". So the number leaves the denominator
here, and the summary stops carrying the reference (DECISIONS D-116).

It is a class of its own rather than a widening of :data:`_FINDING_ID_RE` because it is a different
document: ``F-001`` numbers a finding of *this report*, which Appendix A resolves, and ``D-050``
numbers an entry of ``DECISIONS.md``, which a reader of the report cannot look up at all.
"""

_SECTION_NUMBER_RE: Final = re.compile(r"§\s?\d+(?:\.\d+)*|^[ \t]*\d+\.(?=\s)", re.MULTILINE)
r"""Section and list numbering: ``§6``, and a ``1.`` that opens a line.

Anchored to the start of the line on purpose. An unanchored ``\d+\.`` followed by a space also
matches the ``0.`` of "no feature is flagged 0." and would silently delete a claim, which is the
failure mode an exclusion list is most dangerous for: it lowers the denominator invisibly."""

_SECTION_REFERENCE_RE: Final = re.compile(r"(?<![\w-])[Ss]ection[ \t]+\d+(?:\.\d+)*")
"""A cross-reference to a section of this report: ``Section 4 of this report``, ``section 5.2``.

The fifth live run's section 7 opened a paragraph "Section 4 of this report reported discrimination
before calibration", and the 4 was counted as a claim, flagged as unsupported and removed in a
repair round -- the sentence that survives says "the performance section of this report". A
section number is the report's own numbering, which :data:`_SECTION_NUMBER_RE` already excludes
where the section writes it as ``§4`` or as a heading, and a reference in words is the same number
(DECISIONS D-112).

The lookbehind refuses ``sub-section 4`` only to the extent of not matching the hyphen form as a
whole word; what it exists for is to keep the pattern from firing inside a longer word.
"""

_LABEL_NUMBER_RE: Final = re.compile(
    r"\b(?:decile|bin|quantile|quintile|step|round|regime)[ \t]+\d{1,3}\b", re.IGNORECASE
)
"""An integer that **labels** a bin rather than measuring one: ``decile 1``, ``step 2``.

Section 4 of the first live ``msr_prepayment`` run wrote "The decile separation on test, with
decile 1 holding the highest probabilities, is shown below", and the ``1`` was tokenised as a claim
of value 1.0, flagged unsupported -- it has no artifact, because it is a name -- and removed by a
repair round whose replacement, "the first decile", is a word-number our own repair instruction
asked for. The number names which bucket is meant; nothing in the store holds it, and nothing could
(DECISIONS D-166).

The credit runs never met it because the only ``decile 1`` they wrote is the renderer's own caption
"decile separation on test; decile 1 holds the highest probabilities", which is inside a renderer
block and already excluded. A drafter that writes the same phrase in its own prose is writing the
same non-claim, and this is the class that says so.

It is a class of its own rather than a widening of :data:`_SECTION_NUMBER_RE` for the reason
:data:`_DECISIONS_REFERENCE_RE` is: a bin label numbers a partition the report computed, which
Appendix A's table resolves, where a section number numbers the report itself.

Bounded on both sides so that it cannot eat a measurement. The integer is one to three digits and a
whole word, so ``decile 1000`` does not match; the label word is immediately before it, so "top 2
deciles capture 0.38" keeps its 2 and its 0.38, and "decile event rate 0.021" keeps its 0.021."""

_REG_SECTION_ID_RE: Final = re.compile(
    r"\bSR\s?\d{2}-\d+\b|\bOCC\s?\d{4}-\d+\b|\b[IVX]+(?:\.\d+)+(?:\.[a-z])?\b"
)
"""A section id written in prose rather than inside a citation: ``V.1.c``, ``SR 11-7``."""

_ALGORITHM_NAME_RE: Final = re.compile(r"\b(?!SR-|OCC-)[A-Z]{2,}-\d{1,4}\b")
"""The digits of an **algorithm or standard name**: ``SHA-256``, ``MD-5``, ``ISO-8601``.

Section 3 of the second live ``msr_prepayment`` run wrote "verified each one against its recorded
SHA-256 digest before any split was read", and the ``256`` was tokenised as a claim of value 256.0,
flagged unsupported -- no artifact holds it, because it names a hash function -- and removed by a
repair round whose replacement, "its recorded cryptographic digest", is honest and slightly worse
prose. It was the run's only pre-repair failure and it cost a report that was otherwise 298 of 298
(DECISIONS D-169).

The renderer's own caption two lines below writes ``SHA-256`` as well and was never a claim,
because it is inside a renderer block: the same near-miss that hid :data:`_LABEL_NUMBER_RE`'s
``decile 1`` until a drafter wrote the phrase in its own prose. This is the fourth class of this
shape after D-112's section reference, D-116's ``D-050`` and D-166's bin label, and what the four
have in common is an identifier whose digits a reader does not read as a measurement.

The lookahead keeps a **regulator code** out of this class, so ``SR-11-7`` and ``OCC-2011-12`` are
left for :data:`_REG_SECTION_ID_RE` -- which is also why the mask runs after it, so ``SR 11-7`` is
already blanked as a ``regulatory_section_id`` before this pattern sees the line. Neither hyphenated
spelling is one the corpus or the drafter produces; whether the reg pattern should learn them is its
own question and not this one.

Bounded so that it cannot eat a measurement. The letters are two or more, upper case and a whole
word, so a shock label keeps its number: "a shock of -300 bp" and "scenario -300" are untouched,
and so is the lower-case ``bp-300``. The integer is one to four digits and a whole word, so
``SHA-25612`` does not match. An upper-case ``BP-300`` **would** be masked, which is the one place
the shape rule over-reaches; nothing in this pipeline writes it, and the alternative is a whitelist
of algorithm names that a drafter would fall off the first time it reached for a fifth one."""

_PATTERN_ORDER: Final = (
    "renderer_block",
    "section_number",
    "label_number",
    "inline_code",
    "citation_hash",
    "regulatory_section_id",
    "algorithm_name",
    "finding_id",
    "decisions_reference",
    "package_version",
    EXTRACTOR_RETURNED_EXCLUDED,
)
"""The order the exclusion list is written in, so two runs of one report produce one file."""


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


class EligibleToken(NamedTuple):
    """One numeric token of the prose that is a claim, and where it is.

    Attributes:
        offset: Its offset in the section as written, which the masking preserves.
        text: The token as the drafter wrote it, separators and per cent sign included.
        line: Its index in :attr:`EligibleNumbers.lines`.
    """

    offset: int
    text: str
    line: int

    @property
    def value(self) -> float:
        """The number the token writes, without its separators or per cent sign."""
        return token_value(self.text)


@dataclass(frozen=True)
class EligibleNumbers:
    """The eligible numbers of one section, with everything a caller needs to place them.

    Attributes:
        masked: The section with every excluded region blanked out, offsets preserved.
        lines: The section's non-blank lines, stripped, in order; a claim quotes one of these.
        tokens: The eligible tokens, in prose order.
        excluded: The numeric tokens that were excluded, with the class each fell into.
    """

    masked: str
    lines: list[str] = field(default_factory=list)
    tokens: list[EligibleToken] = field(default_factory=list)
    excluded: list[ExcludedToken] = field(default_factory=list)


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
        token: A numeric token such as ``3,500``, ``22.0%`` or ``1.92e-05``.

    Returns:
        The number as written: ``3500.0``, ``22.0``, ``1.92e-05``. ``float`` reads the exponent
        form itself, so the mantissa and the exponent are one value here exactly as they are one
        token in :data:`NUMERIC_TOKEN_RE`.
    """
    return float(token.replace(",", "").rstrip("%"))


def line_spans(text: str) -> list[tuple[int, int]]:
    """Return the ``(start, end)`` offsets of every line that holds a non-space character.

    Args:
        text: The text to scan, usually the masked prose.

    Returns:
        One ``(start, end)`` pair per non-blank line, in order.
    """
    spans: list[tuple[int, int]] = []
    offset = 0
    for line in text.split("\n"):
        if line.strip():
            spans.append((offset, offset + len(line)))
        offset += len(line) + 1
    return spans


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


def eligible_numbers(markdown: str, *, package_version: str | None = None) -> EligibleNumbers:
    """Return the numbers of one section that are claims, and the ones that are not.

    **This is the one definition of an eligible number.** The extraction pre-pass, the repair
    loop's wrapper and the renderer's uncovered-number check all read it from here, so that a
    number is a claim in all three places or in none (DECISIONS D-084).

    Args:
        markdown: The section as written, renderer blocks included.
        package_version: The package's version string, so that the ``1.0`` of
            "credit_default 1.0" is excluded rather than counted. A caller that omits it is
            asserting that the prose cannot mention the version, which is what the first live
            validation disproved: pass it whenever the package is in reach.

    Returns:
        The masked text, the lines, the eligible tokens in prose order, and the excluded tokens.
    """
    masked, excluded = _masked(markdown, package_version)
    spans = line_spans(masked)
    lines = [markdown[start:end].strip() for start, end in spans]
    tokens = [
        EligibleToken(offset=start + offset, text=token, line=index)
        for index, (start, end) in enumerate(spans)
        for offset, token in numeric_tokens(masked[start:end])
    ]
    return EligibleNumbers(masked=masked, lines=lines, tokens=tokens, excluded=excluded)


def exclusions_of(found: Sequence[ExcludedToken]) -> list[Exclusion]:
    """Group excluded tokens by class, deduplicating examples and keeping first-seen order.

    Args:
        found: The excluded tokens, in the order they were found.

    Returns:
        One :class:`Exclusion` per class present, in :data:`_PATTERN_ORDER`.
    """
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
    r"""Blank out the package version string, which the front matter already states.

    The trailing guard is ``(?!\w|\.\d)`` and not ``(?![\w.])``: version ``1.0`` at the end of a
    sentence is written ``1.0.``, and a guard that refused a following full stop left exactly the
    token this exclusion exists for eligible, which the renderer would then refuse the report over
    (D-084). ``1.0.3`` and ``1.0x`` are still not the version ``1.0``.
    """
    if not version or not NUMERIC_TOKEN_RE.fullmatch(version):
        return text
    pattern = re.compile(rf"(?<![\w.]){re.escape(version)}(?!\w|\.\d)")
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
    text = _mask(text, _DECISIONS_REFERENCE_RE, "decisions_reference", found)
    text = _mask(text, _HEADING_RE, "section_number", found, example="token")
    text = _mask(text, _SECTION_NUMBER_RE, "section_number", found)
    text = _mask(text, _SECTION_REFERENCE_RE, "section_number", found)
    text = _mask(text, _LABEL_NUMBER_RE, "label_number", found)
    text = _mask(text, _REG_SECTION_ID_RE, "regulatory_section_id", found)
    text = _mask(text, _ALGORITHM_NAME_RE, "algorithm_name", found)
    text = _mask_version(text, package_version, found)
    return text, found
