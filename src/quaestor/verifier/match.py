"""Matching: deterministic, no model, and the one place a claim becomes a verdict.

Spec section 3.10. The extractor may be wrong about anything; the matcher is not allowed to be
wrong about anything. It resolves the citation itself against the artifact store, normalises the
units, applies the tolerance D-014 fixes for the claim's unit, and records the artifact value and
the tolerance it used, so a reader of Appendix A can see why 0.74 verified against 0.7412 and why
0.23 did not verify against 0.2213.

Five statuses, and each is a different failure of grounding, not a different degree of one:
``verified`` (cited, resolved, inside tolerance), ``mismatch`` (cited and resolved, values
differ), ``unsupported`` (no citation), ``dangling`` (a citation that resolves to nothing) and
``unattributed`` (a number the extractor never returned, found by the pre-pass). Every one of them
carries a message written for the drafter rather than for a log: the repair loop of Phase 8 hands
it back verbatim, which is why the message names the logical name, the value written and the value
the artifact holds.

The message is not a field of :class:`~quaestor.verifier.claim.VerifiedClaim`. ``claims.json`` is
the study's scoring input and its schema is closed; a per-claim sentence belongs to the repair
loop and to ``trace.jsonl``, so :class:`Match` carries the claim and the message together and only
the claim is persisted (DECISIONS D-065).

**The tolerance is the precision the prose chose.** A claim verifies when the artifact value
rounds to the number as written, at the number of decimals the prose actually wrote: 0.74 verifies
against 0.7412, 0.021 does not verify against 0.0175, and 22.0% does not verify against 0.2212.
Spec section 0's three defaults are the *ceiling* that tolerance never exceeds, not the tolerance
itself, and ``rounding`` remains an explicit override that can only narrow further (DECISIONS
D-069, amending D-014). Counts stay exact.
"""

from __future__ import annotations

import re
from collections.abc import Container, Iterable, Mapping, Sequence
from decimal import Decimal, InvalidOperation
from typing import Final

from pydantic import BaseModel, ConfigDict

from ..artifacts.citations import Citation, CitationKind, parse_citations, resolve
from ..artifacts.store import ArtifactStore
from ..errors import ArtifactError
from ..trace import EventType, TraceWriter
from .claim import (
    ABS_TOL_COUNT,
    DEFAULT_TOLERANCES,
    Claim,
    ClaimStatus,
    Comparison,
    Tolerances,
    Unit,
    VerifiedClaim,
)
from .extract import numeric_tokens, token_value
from .tokens import NUMERIC_TOKEN_RE

__all__ = [
    "DIRECTION_VERBS",
    "Match",
    "default_tolerance",
    "direction_of",
    "match_claim",
    "match_claims",
    "normalise",
    "normalisation_scale",
    "tolerance_for",
    "written_decimals",
]

PERCENT_PER_UNIT: Final = 100.0
"""``22.0%`` is ``0.22`` when the artifact it is compared to lives in the unit interval."""

BP_PER_UNIT: Final = 10_000.0
"""``25 bp`` is ``0.0025`` when the artifact it is compared to is a rate rather than a shock."""

DIRECTION_VERBS: Final[Mapping[str, int]] = {
    "falls": -1,
    "drops": -1,
    "declines": -1,
    "decreases": -1,
    "shrinks": -1,
    "loses": -1,
    "rises": +1,
    "gains": +1,
    "increases": +1,
    "grows": +1,
}
"""Verbs that put the sign of a change in the prose instead of in the number (DECISIONS D-167).

Section 5 of the first live ``msr_prepayment`` run wrote "At the downward extreme the servicing
value **falls by** 1078000" against ``scenario.value_change.-300 = -1077724.40``. The magnitude was
well inside tolerance -- 275.6 against 500 -- and the claim was recorded a ``mismatch``, because the
matcher compared a written ``+1078000`` with a stored ``-1077724.40``. The repair round rewrote the
sentence to "changes by -1078000", which verifies and reads like a machine.

The verb is not decoration: "falls by" and "rises by" are two different assertions about the same
magnitude, and a report that may not say which way a servicing value moved is worse grounded, not
better. So a claim whose sentence carries one of these verbs governing ``by`` is matched on
**magnitude**, and the verb's direction must agree with the artifact's sign -- a "falls by" against
a positive artifact is still a mismatch, and the sign is checked rather than dropped.

The credit subject could not have found this: a classifier's artifacts are probabilities, rates and
counts, and none of them is signed. The rule needs a scenario table to bite on.
"""

_DIRECTION_RE: Final = re.compile(
    rf"\b(?P<verb>{'|'.join(DIRECTION_VERBS)})\s+by\s+(?:[a-z]+\s+){{0,2}}"
    rf"(?P<number>{NUMERIC_TOKEN_RE.pattern})",
    re.IGNORECASE,
)
"""``falls by 1078000``, ``rises by only 167100``: the verb, ``by``, and the number it governs.

Up to two intervening lowercase words, because the very sentence this rule was written for carries
one -- "while at the upward extreme it rises by **only** 167100". The bound is two rather than
unlimited so that the pattern cannot reach across a clause and attach a verb to a number in the
next one; ``by`` is required, so "falls to 0.43" is not a change claim and keeps today's
comparison."""


class Match(BaseModel):
    """One claim's verdict, and the sentence the repair loop hands back to the drafter.

    Attributes:
        claim: The verified claim, exactly as ``claims.json`` persists it.
        message: Why the claim is not verified, naming the logical name, the value written and
            the value the artifact holds; ``None`` when it verified.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    claim: VerifiedClaim
    message: str | None = None

    @property
    def status(self) -> ClaimStatus:
        """The verdict."""
        return self.claim.status


def _decimals_of_token(token: str) -> int:
    """Return the place value of a numeric token's last significant digit, as a decimal count.

    Positive for a token with a fractional part -- ``22.0`` writes one decimal and claims tenths.
    **Negative** for an integer written with trailing zeros: ``-1130000`` claims nothing below ten
    thousand, so its precision is ``10^4`` and its decimal count is ``-4``. That is the same
    sentence read in the other direction, and it is what lets a currency amount written to four
    significant figures verify against the figure it was rounded from. It cannot make a tolerance
    loose on its own: spec section 0's default for the unit is still the ceiling, so ``10`` cited
    to a threshold of 10 is held to 1% of 10 and not to five.

    **The exponent shifts the place value and the mantissa keeps the precision.** ``1.920e-05``
    writes three decimals of a mantissa scaled by ``10^-5``, so its last significant digit stands
    for ``10^-8`` and its decimal count is ``8``; the tolerance that follows is half of that, which
    is the precision the prose chose and not the precision of the mantissa read on its own. Holding
    the mantissa's three decimals against an unscaled tolerance of ``0.0005`` would let any value
    of the same order verify, which is the opposite of D-069 (DECISIONS D-099).
    """
    body = token.rstrip("%").lstrip("-").replace(",", "")
    mantissa, marker, exponent = body.partition("e") if "e" in body else body.partition("E")
    shift = int(exponent) if marker else 0
    whole, dot, fraction = mantissa.partition(".")
    if dot:
        return len(fraction) - shift
    stripped = whole.rstrip("0")
    return -(len(whole) - len(stripped)) - shift


def _decimals_of_number(value: float) -> int:
    """Return how many decimals a number's shortest decimal form carries.

    The fallback for a claim whose ``text`` does not contain the token -- a developer claim
    reconstructed from ``package.yaml``, a claim built by a test. It cannot see a trailing zero,
    which is exactly why the token in the prose is preferred: ``22.0`` and ``22`` are the same
    float and are not the same statement about precision. The sign convention is the token's:
    ``1500.0`` normalises to ``15E+2`` and so claims nothing below a hundred, giving ``-2``.
    """
    try:
        exponent = Decimal(repr(float(value))).normalize().as_tuple().exponent
    except (InvalidOperation, ValueError, OverflowError):  # pragma: no cover - non-finite value
        return 0
    return -int(exponent) if isinstance(exponent, int) else 0


def written_decimals(value: float, text: str | None = None) -> int:
    """Return the number of decimals the prose used when it wrote this number.

    The claim's own sentence is the authority: the first numeric token in it whose value is the
    claimed value is the token the drafter wrote, so ``22.0%`` declares one decimal and ``22%``
    declares none, though both parse to the same float. Only when the sentence holds no such
    token -- which happens for a developer claim rebuilt from ``package.yaml`` -- is the float's
    own shortest form used.

    Args:
        value: The claimed value, as parsed.
        text: The sentence the number was written in, or ``None``.

    Returns:
        The decimal count, in the units the number was written in.
    """
    if text:
        for _, token in numeric_tokens(text):
            if token_value(token) == value:
                return _decimals_of_token(token)
    return _decimals_of_number(value)


def normalisation_scale(unit: Unit, artifact_value: float) -> float:
    """Return the factor :func:`normalise` divides a written value by, as a multiplier.

    A tolerance stated in the units the prose wrote has to be carried into the units the artifact
    is held in, exactly as the value is: half a tenth of a per cent is ``0.0005`` against a rate.

    Args:
        unit: The claim's unit.
        artifact_value: What the claim is compared to.

    Returns:
        ``0.01`` for a per cent against a unit-interval artifact, ``0.0001`` for basis points
        against a rate, ``1.0`` otherwise.
    """
    if unit is Unit.percent and abs(artifact_value) <= 1.0:
        return 1.0 / PERCENT_PER_UNIT
    if unit is Unit.bp and abs(artifact_value) <= 1.0:
        return 1.0 / BP_PER_UNIT
    return 1.0


def default_tolerance(
    unit: Unit,
    artifact_value: float,
    tolerances: Tolerances = DEFAULT_TOLERANCES,
) -> float:
    """Return spec section 0's default for one unit, which is the ceiling tolerance never exceeds.

    D-014's mapping, unchanged: a count matches to half a unit; a ratio or a per cent whose
    artifact lies in the unit interval matches to 0.005 after normalisation; a per cent compared
    on a 0-100 scale matches to 0.5; everything else matches to 1% of the artifact value.

    Args:
        unit: The claim's unit.
        artifact_value: The artifact value, in the units the comparison is made in.
        tolerances: The three defaults, overridable per run.

    Returns:
        The ceiling.
    """
    if unit is Unit.count:
        return ABS_TOL_COUNT
    if unit in (Unit.ratio, Unit.percent, Unit.bp) and abs(artifact_value) <= 1.0:
        return tolerances.abs_tol_unit_interval
    if unit is Unit.percent:
        return tolerances.abs_tol_percent_0_100
    return tolerances.rel_tol_other * abs(artifact_value)


def tolerance_for(
    unit: Unit,
    artifact_value: float,
    rounding: int | None = None,
    tolerances: Tolerances = DEFAULT_TOLERANCES,
    *,
    decimals: int | None = None,
) -> float:
    """Return the absolute tolerance that applies, in the units the comparison is made in.

    D-069, amending D-014: a claim verifies when the artifact rounds to the number as written, at
    the precision the prose used, so the tolerance is half a unit in the last decimal the prose
    wrote -- carried into the artifact's units by :func:`normalisation_scale` -- and spec section
    0's default for the unit is the ceiling it never exceeds. A count is exact whatever it was
    written to. A declared ``rounding`` narrows further and can never widen.

    Args:
        unit: The claim's unit.
        artifact_value: The artifact value, already normalised to the comparison's units.
        rounding: The decimals the prose declared, or ``None``.
        tolerances: The three defaults, overridable per run.
        decimals: The decimals the prose actually wrote, from :func:`written_decimals`, or
            ``None`` when the caller has no sentence to read them from.

    Returns:
        The absolute tolerance.
    """
    applied = default_tolerance(unit, artifact_value, tolerances)
    if unit is Unit.count:
        return applied
    scale = normalisation_scale(unit, artifact_value)
    for declared in (decimals, rounding):
        if declared is not None:
            applied = min(applied, 0.5 * 10.0**-declared * scale)
    return applied


def direction_of(text: str, value: float) -> int | None:
    """Return the sign a direction verb put on one number of a sentence, or ``None``.

    The direction is **derived from the claim's own sentence** every time it is wanted rather than
    stored on the claim. ``claims.json``'s schema is closed -- ``CLAIMS_SCHEMA.json`` was written
    in Phase 1 and closes both ``claim_core`` and ``verified_claim`` with
    ``unevaluatedProperties: false`` -- so a ``direction`` field would be a report-schema change
    after Phase 1, which ``CLAUDE.md`` makes a stop-and-ask, and Appendix A would gain a column,
    which moves the golden report. Neither is worth buying: ``text`` already carries the verb, this
    function is the one reading of it, and the matcher and Appendix A both call it (DECISIONS
    D-167).

    Args:
        text: The sentence the number was written in.
        value: The claimed value, as parsed. A signed number states its own direction, so only a
            positive value -- a magnitude the verb is carrying the sign of -- can have one.

    Returns:
        ``-1`` for a verb of decrease, ``+1`` for a verb of increase, ``None`` when the sentence
        has no such verb governing this number.
    """
    if value <= 0:
        return None
    for match in _DIRECTION_RE.finditer(text):
        if token_value(match.group("number")) == value:
            return DIRECTION_VERBS[match.group("verb").lower()]
    return None


def normalise(unit: Unit, value: float, artifact_value: float) -> float:
    """Return the claimed value in the units the artifact is held in.

    A percent normalises to a ratio when the artifact lives in the unit interval, which is what
    lets ``22.0%`` verify against ``0.22`` without a second tolerance regime (D-014); basis points
    normalise the same way against a rate. A percent held on a 0-100 scale, and a rate shock held
    in basis points, are compared as written.

    Args:
        unit: The claim's unit.
        value: The number as written.
        artifact_value: What it is compared to.

    Returns:
        The claimed value, in the artifact's units.
    """
    if unit is Unit.percent and abs(artifact_value) <= 1.0:
        return value / PERCENT_PER_UNIT
    if unit is Unit.bp and abs(artifact_value) <= 1.0:
        return value / BP_PER_UNIT
    return value


def _verdict(
    claim: Claim,
    status: ClaimStatus,
    *,
    artifact_value: float | None = None,
    tolerance: float = 0.0,
    message: str | None = None,
) -> Match:
    """Build a match from a claim and a verdict."""
    verified = VerifiedClaim(
        **claim.model_dump(include=set(Claim.model_fields)),
        status=status,
        artifact_value=artifact_value,
        tolerance=tolerance,
    )
    return Match(claim=verified, message=message)


def _art_citations(claim: Claim) -> tuple[list[Citation], str | None]:
    """Parse a claim's citation into artifact citations, or say what is wrong with it."""
    text = claim.citation or ""
    try:
        citations = parse_citations(text)
    except ArtifactError as exc:
        return [], f"the citation on {claim.value:g} does not parse: {exc.message}"
    art = [citation for citation in citations if citation.kind is CitationKind.art]
    if not art:
        return [], (
            f"you wrote {claim.value:g} with the citation {text!r}, which names no artifact; "
            "a number is cited by an artifact citation carrying the hash and the logical name"
        )
    wanted = 2 if claim.comparison is not Comparison.eq else 1
    if len(art) != wanted:
        return [], (
            f"you wrote {claim.value:g} as a {claim.comparison.value} of two artifacts but cited "
            f"{len(art)}; a {claim.comparison.value} carries two adjacent [[art:...]] citations, "
            "the first operand then the second"
            if wanted == 2
            else (
                f"you wrote {claim.value:g} with {len(art)} citations; an eq claim carries one, "
                "and two adjacent citations mean a delta or a ratio"
            )
        )
    return art, None


def match_claim(
    claim: Claim,
    store: ArtifactStore,
    *,
    unattributed: bool = False,
    tolerances: Tolerances = DEFAULT_TOLERANCES,
    trace: TraceWriter | None = None,
) -> Match:
    """Match one claim against the artifact store and return its verdict.

    Args:
        claim: The claim, as the extractor or the pre-pass produced it.
        store: The run's artifact store.
        unattributed: Whether the pre-pass added this claim, in which case the status is
            ``unattributed`` whatever the citation says -- the extractor did not return it, and
            that is the fact being recorded.
        tolerances: The three defaults, overridable per run.
        trace: The run's trace; one ``claim_check`` event is written per claim.

    Returns:
        The match: the verified claim and, when it did not verify, the sentence the repair loop
        hands back to the drafter.
    """
    match = _match(claim, store, unattributed=unattributed, tolerances=tolerances)
    if trace is not None:
        trace.emit(
            EventType.claim_check,
            claim_id=match.claim.id,
            section=match.claim.section.value,
            value=match.claim.value,
            unit=match.claim.unit.value,
            comparison=match.claim.comparison.value,
            citation=match.claim.citation,
            status=match.claim.status.value,
            artifact_value=match.claim.artifact_value,
            tolerance=match.claim.tolerance,
            message=match.message,
        )
    return match


def _match(
    claim: Claim,
    store: ArtifactStore,
    *,
    unattributed: bool,
    tolerances: Tolerances,
) -> Match:
    """Decide one claim's status, without touching the trace."""
    decimals = written_decimals(claim.value, claim.text)
    if unattributed:
        return _verdict(
            claim,
            ClaimStatus.unattributed,
            tolerance=tolerance_for(
                claim.unit, claim.value, claim.rounding, tolerances, decimals=decimals
            ),
            message=(
                f"the number {claim.value:g} appears in the prose but the extractor did not "
                "return it; it is counted against the report"
            ),
        )
    if not claim.citation:
        return _verdict(
            claim,
            ClaimStatus.unsupported,
            tolerance=tolerance_for(
                claim.unit, claim.value, claim.rounding, tolerances, decimals=decimals
            ),
            message=(
                f"you wrote {claim.value:g} with no citation; cite the artifact it comes from, "
                "with its hash and its logical name, or remove the number"
            ),
        )
    citations, problem = _art_citations(claim)
    if problem is not None:
        return _verdict(claim, ClaimStatus.dangling, message=problem)
    resolved = [resolve(citation, store) for citation in citations]
    unresolved = [item for item in resolved if not item.is_resolved]
    if unresolved:
        return _verdict(
            claim,
            ClaimStatus.dangling,
            message="; ".join(item.message or "" for item in unresolved),
        )
    values = [item.value for item in resolved]
    if any(value is None for value in values):  # pragma: no cover - defensive; see below
        # A resolved *artifact* citation always carries a number today: a scalar resolves to its
        # value and a path that resolves to anything else is already dangling. The guard is here
        # so that a sixth citation form cannot reach `float(None)` by being added quietly.
        names = [citation.name for citation in citations]
        return _verdict(
            claim,
            ClaimStatus.dangling,
            message=(
                f"you wrote {claim.value:g} citing {names}, which resolves to something that is "
                "not a number, so nothing can be compared"
            ),
        )
    numbers = [float(value) for value in values if value is not None]
    artifact_value, problem = _combine(claim, citations, numbers)
    if artifact_value is None:
        return _verdict(claim, ClaimStatus.dangling, message=problem)
    tolerance = tolerance_for(
        claim.unit, artifact_value, claim.rounding, tolerances, decimals=decimals
    )
    written = normalise(claim.unit, claim.value, artifact_value)
    direction = direction_of(claim.text, claim.value)
    cited = " and ".join(str(citation.name) for citation in citations)
    if direction is None:
        if abs(written - artifact_value) <= tolerance:
            return _verdict(
                claim, ClaimStatus.verified, artifact_value=artifact_value, tolerance=tolerance
            )
        message = (
            f"you wrote {claim.value:g} for {cited}; the artifact says {artifact_value:.10g} "
            f"(tolerance {tolerance:.10g}); cite the right artifact, correct the number, or "
            "remove it"
        )
    elif abs(abs(written) - abs(artifact_value)) > tolerance:
        message = (
            f"you wrote {claim.value:g} for {cited}; the artifact's magnitude is "
            f"{abs(artifact_value):.10g} (tolerance {tolerance:.10g}); cite the right artifact, "
            "correct the number, or remove it"
        )
    elif _sign(artifact_value) == direction:
        return _verdict(
            claim, ClaimStatus.verified, artifact_value=artifact_value, tolerance=tolerance
        )
    else:
        moved = "up" if direction > 0 else "down"
        actual = "up" if artifact_value > 0 else "down" if artifact_value < 0 else "not at all"
        message = (
            f"your sentence says {cited} moves {moved} by {claim.value:g}, and the artifact says "
            f"{artifact_value:.10g}, which moves {actual}; the magnitude agrees and the direction "
            "does not, so change the verb or cite the other end of the scenario"
        )
    return _verdict(
        claim,
        ClaimStatus.mismatch,
        artifact_value=artifact_value,
        tolerance=tolerance,
        message=message,
    )


def _sign(value: float) -> int:
    """Return ``-1``, ``0`` or ``+1``; a zero artifact moves in no direction and matches no verb."""
    return (value > 0) - (value < 0)


def _combine(
    claim: Claim, citations: Sequence[Citation], values: Sequence[float]
) -> tuple[float | None, str | None]:
    """Reduce one or two resolved values to the number the claim asserts."""
    if claim.comparison is Comparison.eq:
        return values[0], None
    first, second = values[0], values[1]
    if claim.comparison is Comparison.delta:
        return second - first, None
    if first == 0.0:
        return None, (
            f"you wrote {claim.value:g} as the ratio of {citations[1].name} to "
            f"{citations[0].name}, and {citations[0].name} is zero"
        )
    return second / first, None


def match_claims(
    claims: Iterable[Claim],
    store: ArtifactStore,
    *,
    unattributed: Container[str] = frozenset(),
    tolerances: Tolerances = DEFAULT_TOLERANCES,
    trace: TraceWriter | None = None,
) -> list[Match]:
    """Match every claim of a section or a report, in order.

    Args:
        claims: The claims.
        store: The run's artifact store.
        unattributed: The ids the pre-pass added, from
            :attr:`~quaestor.verifier.extract.Extraction.unattributed_ids`.
        tolerances: The three defaults, overridable per run.
        trace: The run's trace; one ``claim_check`` event per claim.

    Returns:
        One match per claim, in the order given.
    """
    return [
        match_claim(
            claim,
            store,
            unattributed=claim.id in unattributed,
            tolerances=tolerances,
            trace=trace,
        )
        for claim in claims
    ]
