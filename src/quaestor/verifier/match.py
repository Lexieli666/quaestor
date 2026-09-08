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
"""

from __future__ import annotations

from collections.abc import Container, Iterable, Sequence
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

__all__ = [
    "Match",
    "match_claim",
    "match_claims",
    "normalise",
    "tolerance_for",
]

PERCENT_PER_UNIT: Final = 100.0
"""``22.0%`` is ``0.22`` when the artifact it is compared to lives in the unit interval."""

BP_PER_UNIT: Final = 10_000.0
"""``25 bp`` is ``0.0025`` when the artifact it is compared to is a rate rather than a shock."""


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


def tolerance_for(
    unit: Unit,
    artifact_value: float,
    rounding: int | None = None,
    tolerances: Tolerances = DEFAULT_TOLERANCES,
) -> float:
    """Return the absolute tolerance that applies, in the units the comparison is made in.

    D-014, which makes spec section 0's three defaults precise per unit: a count matches to half
    a unit; a ratio or a percent whose artifact lies in the unit interval matches to 0.005 after
    normalisation; a percent compared on a 0-100 scale matches to 0.5; everything else matches to
    1% of the artifact value. A declared ``rounding`` widens the result and never narrows it.

    Args:
        unit: The claim's unit.
        artifact_value: The artifact value, already normalised to the comparison's units.
        rounding: The decimals the prose declared, or ``None``.
        tolerances: The three defaults, overridable per run.

    Returns:
        The absolute tolerance.
    """
    if unit is Unit.count:
        base = ABS_TOL_COUNT
    elif unit in (Unit.ratio, Unit.percent, Unit.bp) and abs(artifact_value) <= 1.0:
        base = tolerances.abs_tol_unit_interval
    elif unit is Unit.percent:
        base = tolerances.abs_tol_percent_0_100
    else:
        base = tolerances.rel_tol_other * abs(artifact_value)
    if rounding is not None:
        base = max(base, 0.5 * 10.0**-rounding)
    return base


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
            "a number is cited as [[art:<hash8>:<logical_name>]]"
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
    if unattributed:
        return _verdict(
            claim,
            ClaimStatus.unattributed,
            tolerance=tolerance_for(claim.unit, claim.value, claim.rounding, tolerances),
            message=(
                f"the number {claim.value:g} appears in the prose but the extractor did not "
                "return it; it is counted against the report"
            ),
        )
    if not claim.citation:
        return _verdict(
            claim,
            ClaimStatus.unsupported,
            tolerance=tolerance_for(claim.unit, claim.value, claim.rounding, tolerances),
            message=(
                f"you wrote {claim.value:g} with no citation; cite the artifact it comes from as "
                "[[art:<hash8>:<logical_name>]] or remove the number"
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
    tolerance = tolerance_for(claim.unit, artifact_value, claim.rounding, tolerances)
    written = normalise(claim.unit, claim.value, artifact_value)
    if abs(written - artifact_value) <= tolerance:
        return _verdict(
            claim, ClaimStatus.verified, artifact_value=artifact_value, tolerance=tolerance
        )
    cited = " and ".join(str(citation.name) for citation in citations)
    return _verdict(
        claim,
        ClaimStatus.mismatch,
        artifact_value=artifact_value,
        tolerance=tolerance,
        message=(
            f"you wrote {claim.value:g} for {cited}; the artifact says {artifact_value:.10g} "
            f"(tolerance {tolerance:.10g}); cite the right artifact, correct the number, or "
            "remove it"
        ),
    )


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
