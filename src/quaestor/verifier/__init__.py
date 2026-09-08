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
    ExtractedClaim,
    ExtractedClaims,
    Extraction,
    extract,
    extraction_from,
    merge_exclusions,
    numbered_lines,
    numbered_prose,
)
from .grounding import GroundingFigure, SectionGrounding, grounding, precision_of
from .match import (
    Match,
    default_tolerance,
    match_claim,
    match_claims,
    normalisation_scale,
    normalise,
    tolerance_for,
    written_decimals,
)
from .tokens import (
    EXTRACTOR_RETURNED_EXCLUDED,
    NUMERIC_TOKEN_RE,
    EligibleNumbers,
    EligibleToken,
    ExcludedToken,
    Exclusion,
    drafted_prose,
    eligible_numbers,
    exclusions_of,
    line_spans,
    numeric_tokens,
    token_value,
)

__all__ = [
    "ABS_TOL_COUNT",
    "DEFAULT_TOLERANCES",
    "EXTRACTION_INSTRUCTION",
    "EXTRACTOR_RETURNED_EXCLUDED",
    "GROUNDING_STATUSES",
    "NUMERIC_TOKEN_RE",
    "Claim",
    "ClaimSource",
    "ClaimStatus",
    "ClaimsDocument",
    "Comparison",
    "DeveloperClaims",
    "EligibleNumbers",
    "EligibleToken",
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
    "default_tolerance",
    "drafted_prose",
    "eligible_numbers",
    "exclusions_of",
    "extract",
    "extraction_from",
    "grounding",
    "line_spans",
    "match_claim",
    "match_claims",
    "merge_exclusions",
    "normalisation_scale",
    "normalise",
    "numbered_lines",
    "numbered_prose",
    "numeric_tokens",
    "precision_of",
    "token_value",
    "tolerance_for",
    "verify_developer_claims",
    "written_decimals",
]
