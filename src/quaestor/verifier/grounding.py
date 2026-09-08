"""Grounding precision: the one number this project is asking to be judged on.

Spec section 3.10 defines it as ``verified / (verified + mismatch + unsupported + dangling +
unattributed)``, per section and per report, computed before and after repair, and both figures
are printed on the report's first page. The definition has no free parameters and this module has
no options: it counts statuses.

Two properties are load-bearing and are asserted in ``tests/test_verifier_grounding.py``. The
denominator is every claim the pre-pass found, not every claim the extractor returned, so an
extractor that omits a number cannot raise the score. And a report with no claims at all scores
**0.0**, not 1.0: a vacuous 1.0000 on the front page of an empty report is the one number in this
repository that could flatter by construction, and the printed ``n_claims`` beside it is what
makes 0.0 readable (DECISIONS D-066).
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Final

from pydantic import BaseModel, ConfigDict, Field

from ..vocab import SECTION_ORDER, ReportSection
from .claim import GROUNDING_STATUSES, ClaimStatus, VerifiedClaim

__all__ = [
    "PRECISION_DECIMALS",
    "GroundingFigure",
    "SectionGrounding",
    "grounding",
    "precision_of",
]

PRECISION_DECIMALS: Final = 4
"""Precision is rounded to four decimals, the width the golden report's front matter prints."""


class SectionGrounding(BaseModel):
    """One section's row of the grounding table.

    Attributes:
        verified: How many claims verified.
        n_claims: How many claims the section has, in the five counted statuses.
        precision: ``verified / n_claims``, rounded to four decimals; ``0.0`` when there are no
            claims.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    verified: int = Field(ge=0)
    n_claims: int = Field(ge=0)
    precision: float = Field(ge=0.0, le=1.0)


class GroundingFigure(BaseModel):
    """Grounding precision for a whole report, at one point in the repair loop.

    Attributes:
        precision: ``verified / n_claims``, rounded to four decimals.
        n_claims: The denominator, printed beside the precision so it is interpretable.
        status_counts: How many claims each of the five statuses holds.
        per_section: One row per section that has at least one claim, in report order.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    precision: float = Field(ge=0.0, le=1.0)
    n_claims: int = Field(ge=0)
    status_counts: dict[str, int]
    per_section: dict[str, SectionGrounding] = Field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        """Return the figure as the JSON object ``CLAIMS_SCHEMA.json`` validates.

        Returns:
            A plain dict.
        """
        return self.model_dump(mode="json")


def precision_of(verified: int, n_claims: int) -> float:
    """Return ``verified / n_claims`` rounded to four decimals, or ``0.0`` when there are none.

    Args:
        verified: How many claims verified.
        n_claims: How many claims were counted.

    Returns:
        The precision.
    """
    if n_claims <= 0:
        return 0.0
    return round(verified / n_claims, PRECISION_DECIMALS)


def grounding(claims: Iterable[VerifiedClaim]) -> GroundingFigure:
    """Compute grounding precision over a list of verified claims.

    Claims whose status is ``not_evaluated`` -- developer claims under ``--synthetic`` (D-016) --
    are not counted at all: they were never compared to anything, so counting them either way
    would be an opinion rather than a measurement.

    Args:
        claims: The verified claims of one report, at one point in the repair loop.

    Returns:
        The figure, with its per-section rows in report order.
    """
    counted = [claim for claim in claims if claim.counts_towards_grounding]
    status_counts = {status.value: 0 for status in GROUNDING_STATUSES}
    per_section_verified: dict[ReportSection, int] = {}
    per_section_total: dict[ReportSection, int] = {}
    for claim in counted:
        status_counts[claim.status.value] += 1
        per_section_total[claim.section] = per_section_total.get(claim.section, 0) + 1
        if claim.status is ClaimStatus.verified:
            per_section_verified[claim.section] = per_section_verified.get(claim.section, 0) + 1
    verified = status_counts[ClaimStatus.verified.value]
    return GroundingFigure(
        precision=precision_of(verified, len(counted)),
        n_claims=len(counted),
        status_counts=status_counts,
        per_section={
            section.value: SectionGrounding(
                verified=per_section_verified.get(section, 0),
                n_claims=per_section_total[section],
                precision=precision_of(
                    per_section_verified.get(section, 0), per_section_total[section]
                ),
            )
            for section in SECTION_ORDER
            if section in per_section_total
        },
    )
