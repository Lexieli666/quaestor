"""The claim grammar, the extractor, the deterministic matcher and grounding precision.

Spec section 3.10. Extraction is an LLM call; nothing else here is. A deterministic regex pre-pass
finds every numeric token in a section, so the extractor cannot lower the denominator of grounding
precision by omitting a number, and the matcher resolves every citation against the artifact store
itself rather than believing what the extractor said about it.

The pipeline of Phase 8 uses the four steps in this order: :func:`extract` per section,
:func:`match_claims` over the claims it returned, :func:`grounding` over the verdicts, and
:class:`ClaimsDocument` to persist all of it as ``claims.json``.
"""

from __future__ import annotations

from .claim import (
    ABS_TOL_COUNT,
    DEFAULT_TOLERANCES,
    GROUNDING_STATUSES,
    Claim,
    ClaimSource,
    ClaimStatus,
    Comparison,
    SplitName,
    Tolerances,
    Unit,
    VerifiedClaim,
    claim_id,
)
from .claims_doc import ClaimsDocument, Repair, RepairSide
from .developer import DeveloperClaims, verify_developer_claims
from .extract import (
    EXTRACTION_INSTRUCTION,
    ExcludedToken,
    Exclusion,
    ExtractedClaim,
    ExtractedClaims,
    Extraction,
    drafted_prose,
    extract,
    merge_exclusions,
    numeric_tokens,
    token_value,
)
from .grounding import GroundingFigure, SectionGrounding, grounding, precision_of
from .match import Match, match_claim, match_claims, normalise, tolerance_for

__all__ = [
    "ABS_TOL_COUNT",
    "DEFAULT_TOLERANCES",
    "EXTRACTION_INSTRUCTION",
    "GROUNDING_STATUSES",
    "Claim",
    "ClaimSource",
    "ClaimStatus",
    "ClaimsDocument",
    "Comparison",
    "DeveloperClaims",
    "ExcludedToken",
    "Exclusion",
    "ExtractedClaim",
    "ExtractedClaims",
    "Extraction",
    "GroundingFigure",
    "Match",
    "Repair",
    "RepairSide",
    "SectionGrounding",
    "SplitName",
    "Tolerances",
    "Unit",
    "VerifiedClaim",
    "claim_id",
    "drafted_prose",
    "extract",
    "grounding",
    "match_claim",
    "match_claims",
    "merge_exclusions",
    "normalise",
    "numeric_tokens",
    "precision_of",
    "token_value",
    "tolerance_for",
    "verify_developer_claims",
]
