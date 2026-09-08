"""The claim grammar: ``Claim``, ``VerifiedClaim`` and the tolerances they are judged under.

Spec section 3.10 and ``docs/REPORT_SCHEMA.md`` sections 6-7. A **claim** is a number in report
prose together with everything needed to check it: what it measures, on which split, in which
unit, against which artifact, and how many decimals the prose chose to write. A **verified claim**
is a claim plus the deterministic matcher's verdict -- the status, the artifact value it was
compared to, and the absolute tolerance actually applied, so a reader can see why 0.74 verified
against 0.7412 without re-deriving the rule.

The models are the schema. ``examples/golden_report/CLAIMS_SCHEMA.json`` was written in Phase 1,
before any of this code, and ``tests/test_verifier_claims.py`` parses the golden ``claims.json``
into these classes and serialises it back: if a field here drifts from the schema, that test says
so rather than a report failing to validate three phases later.

Two fields are computed rather than asked for. ``id`` is ``stable_hash([section, text, value])``,
which is how the repair loop, the ``repairs`` list and the trace all name one claim; a claim read
back from a file keeps the id the file carries, because an id is an identifier and not a checksum
(DECISIONS D-062). ``tolerance`` is filled by the matcher, never by the extractor.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Final

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ..hashing import stable_hash
from ..vocab import ReportSection

__all__ = [
    "ABS_TOL_COUNT",
    "DEFAULT_TOLERANCES",
    "GROUNDING_STATUSES",
    "Claim",
    "ClaimSource",
    "ClaimStatus",
    "Comparison",
    "SplitName",
    "Tolerances",
    "Unit",
    "VerifiedClaim",
    "claim_id",
]


class Unit(StrEnum):
    """How a number is written, which decides how it is normalised before matching.

    Attributes:
        ratio: Every dimensionless quantity not written with a ``%`` -- AUC, PSI, VIF, a
            coefficient, a lift.
        percent: Written with a ``%``; normalised against a unit-interval artifact by dividing
            by 100.
        count: A number of rows, features or events. Matched to half a unit, so integers match
            exactly.
        currency: A money amount.
        bp: Basis points, as a rate shock is written.
        months: A horizon.
    """

    ratio = "ratio"
    percent = "percent"
    # `count` shadows `str.count`, which mypy reads as a redefinition; the member name is fixed by
    # `CLAIMS_SCHEMA.json`, so the shadowing is the schema's and not a choice this module makes.
    count = "count"  # type: ignore[assignment]
    currency = "currency"
    bp = "bp"
    months = "months"


class Comparison(StrEnum):
    """What the claimed value is asserted to equal.

    ``delta`` and ``ratio`` are cited by two adjacent ``[[art:...]]`` tokens, in order (D-012).
    The enum is not nullable: ``eq`` is the explicit default, so "this number equals its artifact"
    has one spelling and not two (D-018).

    Attributes:
        eq: The value matches the cited artifact.
        delta: The value matches ``second - first``.
        ratio: The value matches ``second / first``.
    """

    eq = "eq"
    delta = "delta"
    ratio = "ratio"


class ClaimSource(StrEnum):
    """Where a claim came from.

    Attributes:
        report: Drafted prose.
        developer: A ``claims:`` entry of ``package.yaml`` (D-016).
    """

    report = "report"
    developer = "developer"


class ClaimStatus(StrEnum):
    """The matcher's verdict.

    The first five are spec section 3.10's; ``not_evaluated`` is the synthetic-mode status of a
    developer claim and may not appear on a claim whose source is ``report`` (D-016, D-018).

    Attributes:
        verified: Cited, resolved, and inside tolerance.
        mismatch: Cited and resolved, but the values differ; the artifact value is recorded.
        unsupported: The sentence carries no citation.
        dangling: The citation does not resolve.
        unattributed: Found by the regex pre-pass and not returned by the extractor.
        not_evaluated: A developer claim under ``--synthetic``.
    """

    verified = "verified"
    mismatch = "mismatch"
    unsupported = "unsupported"
    dangling = "dangling"
    unattributed = "unattributed"
    not_evaluated = "not_evaluated"


GROUNDING_STATUSES: Final = (
    ClaimStatus.verified,
    ClaimStatus.mismatch,
    ClaimStatus.unsupported,
    ClaimStatus.dangling,
    ClaimStatus.unattributed,
)
"""The five statuses grounding precision counts. ``not_evaluated`` is not one of them."""


class SplitName(StrEnum):
    """The splits a claim may be stated on, exactly as ``CLAIMS_SCHEMA.json`` enumerates them.

    Attributes:
        train: The development split.
        test: The held-out split.
        out_of_time: A later-period split; hazard subjects.
        vintage_holdout: One origination year held out; hazard subjects.
    """

    train = "train"
    test = "test"
    out_of_time = "out_of_time"
    vintage_holdout = "vintage_holdout"


class Tolerances(BaseModel):
    """The three defaults of spec section 0, echoed into ``claims.json`` so a verdict reproduces.

    Attributes:
        abs_tol_unit_interval: Absolute tolerance for a ratio or percent whose artifact value is
            in the unit interval, applied after percent-to-ratio normalisation.
        abs_tol_percent_0_100: Absolute tolerance for a percentage compared on a 0-100 scale.
        rel_tol_other: Relative tolerance for everything else.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    abs_tol_unit_interval: float = Field(default=0.005, gt=0)
    abs_tol_percent_0_100: float = Field(default=0.5, gt=0)
    rel_tol_other: float = Field(default=0.01, gt=0)


DEFAULT_TOLERANCES: Final = Tolerances()
"""Spec section 0's defaults, made precise per unit by DECISIONS D-014."""

ABS_TOL_COUNT: Final = 0.5
"""A count is either right or wrong: half a unit, which is stricter than the spec's 1% (D-014)."""


class Claim(BaseModel):
    """A numeric statement in report prose, as the extractor returns it.

    Attributes:
        text: The sentence or table row as drafted, citations included.
        value: The number as written, without thousands separators and without the ``%``.
        unit: How it is written.
        metric: What it measures, from the cited artifact's logical name; ``None`` for a bare
            count.
        split: Which split it is stated on, or ``None``.
        comparison: ``eq``, ``delta`` or ``ratio``.
        citation: The ``[[art:...]]`` the number carries -- one, or two adjacent for a
            comparison -- or ``None`` when the sentence has none.
        rounding: Decimals the prose used, when it declares them; widens the tolerance and never
            narrows it.
        section: Which of the seven sections the sentence lives in.
        id: ``stable_hash([section, text, value])``; filled in when not given.
        source: ``report`` or ``developer``.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    text: str = Field(min_length=1)
    value: float
    unit: Unit = Unit.ratio
    metric: str | None = None
    split: SplitName | None = None
    comparison: Comparison = Comparison.eq
    citation: str | None = None
    rounding: int | None = Field(default=None, ge=0)
    section: ReportSection
    id: str = ""
    source: ClaimSource = ClaimSource.report

    @model_validator(mode="after")
    def _fill_id(self) -> Claim:
        """Compute the claim id when the caller did not carry one in from a file."""
        if not self.id:
            object.__setattr__(self, "id", claim_id(self.section, self.text, self.value))
        return self

    def with_citation(self, citation: str | None) -> Claim:
        """Return a copy carrying a different citation, with the id left as it is.

        Args:
            citation: The citation text, or ``None``.

        Returns:
            The copy. The id is unchanged because the id names ``[section, text, value]`` and
            none of those moved.
        """
        return self.model_copy(update={"citation": citation})


class VerifiedClaim(Claim):
    """A :class:`Claim` plus the deterministic matcher's verdict.

    Attributes:
        status: One of :class:`ClaimStatus`.
        artifact_value: The resolved scalar, or the computed delta or ratio; ``None`` unless the
            citation resolved.
        tolerance: The absolute tolerance actually applied, in the units the comparison was made
            in.
    """

    status: ClaimStatus
    artifact_value: float | None = None
    tolerance: float = 0.0

    @model_validator(mode="after")
    def _not_evaluated_is_a_developer_status(self) -> VerifiedClaim:
        """Keep ``not_evaluated`` on the one source that has it (D-016)."""
        if self.status is ClaimStatus.not_evaluated and self.source is not ClaimSource.developer:
            raise ValueError(
                f"claim {self.id} has source {self.source} and status not_evaluated, which is "
                "the synthetic-mode status of a developer claim only"
            )
        return self

    @property
    def is_verified(self) -> bool:
        """Whether the matcher verified this claim."""
        return self.status is ClaimStatus.verified

    @property
    def counts_towards_grounding(self) -> bool:
        """Whether this claim is in grounding precision's denominator."""
        return self.status in GROUNDING_STATUSES

    def to_payload(self) -> dict[str, Any]:
        """Return the claim as the JSON object ``CLAIMS_SCHEMA.json`` validates.

        Returns:
            A plain dict, with the enums as their string values.
        """
        return self.model_dump(mode="json")


def claim_id(section: ReportSection | str, text: str, value: float) -> str:
    """Return the identity of a claim: ``stable_hash([section, text, value])``.

    Args:
        section: The section the sentence lives in.
        text: The sentence as drafted.
        value: The number as written.

    Returns:
        Sixteen hex characters.
    """
    return stable_hash([str(section), text, float(value)])
