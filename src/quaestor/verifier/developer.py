"""Developer claims: the numbers ``package.yaml`` declares, verified through the same grammar.

Spec section 3.2 says the ``claims:`` block is "verified like report claims", and D-016 settles
what that means under ``--synthetic``: nothing. A synthetic AUC drawn from a generating process
has no relationship to the AUC a developer declared for the real fit, so comparing the two would
manufacture either a false ``T1`` finding or a meaningless pass -- and ``T1`` detection is one of
the things the seeded-defect study measures. Under ``--synthetic`` this module returns no claims
and a sentence for Appendix D; under ``--data`` each declaration becomes an ordinary
:class:`~quaestor.verifier.claim.VerifiedClaim` with ``source: developer``.

A mismatch is the **claim channel** of a ``T1`` finding, and a finding needs evidence, so the
comparison itself is stored: ``developer_claim.<i>`` is a JSON artifact holding the declaration,
the artifact it was compared to, both values and their difference. The candidate's evidence is
that record and the artifact it cites. This is the one comparison in Quaestor that has no
threshold -- a declared number is right or it is not -- and storing it is what lets the report
cite the comparison rather than restate it (DECISIONS D-067).
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Final

from pydantic import BaseModel, ConfigDict, Field

from ..artifacts.store import ArtifactKind, ArtifactStore
from ..findings import DefectClass, FindingCandidate, Severity
from ..package import ModelPackage
from ..package.spec import DeveloperClaim
from ..vocab import ReportSection
from .claim import (
    DEFAULT_TOLERANCES,
    Claim,
    ClaimSource,
    ClaimStatus,
    SplitName,
    Tolerances,
    Unit,
    VerifiedClaim,
)
from .match import Match, match_claim

__all__ = [
    "DEVELOPER_CLAIM_PREFIX",
    "DEVELOPER_TOOL",
    "NO_CLAIMS_NOTE",
    "SYNTHETIC_NOTE",
    "DeveloperClaims",
    "logical_names_for",
    "verify_developer_claims",
]

DEVELOPER_CLAIM_PREFIX: Final = "developer_claim"
"""``developer_claim.0``: the comparison record a ``T1`` candidate points at."""

DEVELOPER_TOOL: Final = "verify_developer_claims"
"""The ``tool`` recorded on a candidate raised by this check."""

SYNTHETIC_NOTE: Final = (
    "The package declares {n} developer claim(s) about its real fit; synthetic mode does not "
    "evaluate them, because a metric computed from the generating process has no bearing on a "
    "number declared for the real sample (DECISIONS D-016)."
)
"""What Appendix D says when a run was synthetic. Formatted with the number of declarations."""

NO_CLAIMS_NOTE: Final = "`package.yaml` declares no claims:, so none were evaluated."
"""What Appendix D says when the package declares nothing to verify."""


class DeveloperClaims(BaseModel):
    """What verifying ``package.yaml`` ``claims:`` produced.

    Attributes:
        claims: One :class:`~quaestor.verifier.claim.VerifiedClaim` per declaration, with
            ``source: developer``; empty under ``--synthetic``.
        candidates: One ``T1`` candidate per mismatch.
        note: The sentence Appendix D prints when the list is empty or was not evaluated.
        messages: The matcher's sentence for each claim that did not verify, in order.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    claims: list[VerifiedClaim] = Field(default_factory=list)
    candidates: list[FindingCandidate] = Field(default_factory=list)
    note: str | None = None
    messages: list[str] = Field(default_factory=list)


def logical_names_for(metric: str, split: str | None) -> list[str]:
    """Return the logical names a developer claim could be talking about, best first.

    The declaration names a metric and a split, not an artifact, so the artifact has to be found.
    Four shapes cover every name the tools of Phase 5 write: ``metrics.<split>.<metric>`` for the
    metrics table, ``<metric>.<split>`` for the ones stored per split under their own name
    (``calibration_slope.test``), ``<metric>`` for a run-level scalar, and ``<metric>.max`` for a
    per-feature family the package declares in aggregate (``psi``).

    Args:
        metric: The metric the developer named.
        split: The split, or ``None``.

    Returns:
        Candidate logical names, in the order they are tried.
    """
    names = []
    if split:
        names.append(f"metrics.{split}.{metric}")
        names.append(f"{metric}.{split}")
    names.append(metric)
    names.append(f"{metric}.max")
    return names


def _resolve_name(store: ArtifactStore, claim: DeveloperClaim) -> str | None:
    """Return the first logical name in the store that the declaration could mean."""
    for name in logical_names_for(claim.metric or "", claim.split):
        if name in store and store.entry(name).kind is ArtifactKind.scalar:
            return name
    return None


def _unit_of(claim: DeveloperClaim) -> Unit:
    """Guess the unit of a declaration from how the developer wrote it."""
    return Unit.percent if "%" in claim.text else Unit.ratio


def _split_of(claim: DeveloperClaim) -> SplitName | None:
    """Return the declaration's split when it is one the claim grammar knows."""
    try:
        return SplitName(claim.split) if claim.split else None
    except ValueError:
        return None


def _as_claim(declaration: DeveloperClaim, citation: str | None) -> Claim:
    """Turn one ``package.yaml`` declaration into a claim of the report's own grammar."""
    return Claim(
        text=declaration.text,
        value=declaration.value,
        unit=_unit_of(declaration),
        metric=declaration.metric,
        split=_split_of(declaration),
        citation=citation,
        section=ReportSection.outcomes,
        source=ClaimSource.developer,
    )


def _comparison_record(
    index: int,
    declaration: DeveloperClaim,
    name: str,
    match: Match,
    store: ArtifactStore,
) -> str:
    """Store the threshold-free comparison as a JSON artifact and return its hash."""
    artifact = store.put(
        f"{DEVELOPER_CLAIM_PREFIX}.{index}",
        {
            "text": declaration.text,
            "metric": declaration.metric,
            "split": declaration.split,
            "declared": declaration.value,
            "artifact": name,
            "artifact_value": match.claim.artifact_value,
            "difference": (
                None
                if match.claim.artifact_value is None
                else declaration.value - match.claim.artifact_value
            ),
            "tolerance": match.claim.tolerance,
            "status": match.claim.status.value,
        },
        ArtifactKind.json,
        summary=f"developer claim {index}: {declaration.text}",
    )
    return artifact.hash


def verify_developer_claims(
    package: ModelPackage,
    store: ArtifactStore,
    *,
    data_dir: Path | None = None,
    tolerances: Tolerances = DEFAULT_TOLERANCES,
) -> DeveloperClaims:
    """Verify the ``claims:`` block of ``package.yaml`` against the run's artifacts.

    Args:
        package: The loaded package.
        store: The run's artifact store.
        data_dir: The directory the run read its data from, or ``None`` for a synthetic run, in
            which case nothing is evaluated and a note is returned for Appendix D (D-016).
        tolerances: The three defaults, overridable per run.

    Returns:
        The verified claims, the ``T1`` candidates each mismatch raised, and the Appendix D note.
    """
    declarations: Sequence[DeveloperClaim] = package.spec.claims
    if not declarations:
        return DeveloperClaims(note=NO_CLAIMS_NOTE)
    if data_dir is None:
        return DeveloperClaims(note=SYNTHETIC_NOTE.format(n=len(declarations)))

    claims: list[VerifiedClaim] = []
    candidates: list[FindingCandidate] = []
    messages: list[str] = []
    for index, declaration in enumerate(declarations):
        name = _resolve_name(store, declaration)
        citation = store.artifact(name).citation() if name else None
        match = match_claim(_as_claim(declaration, citation), store, tolerances=tolerances)
        claims.append(match.claim)
        if match.message is not None:
            messages.append(match.message)
        if match.claim.status is not ClaimStatus.mismatch or name is None:
            continue
        evidence = [
            store.artifact(name).hash,
            _comparison_record(index, declaration, name, match, store),
        ]
        candidates.append(
            FindingCandidate(
                defect_class=DefectClass.T1,
                evidence=sorted(set(evidence)),
                detail=(
                    f"the package declares {declaration.text!r}, and {name} is "
                    f"{match.claim.artifact_value:.10g}; the declaration is outside the "
                    f"{match.claim.tolerance:.10g} the claim grammar allows"
                ),
                suggested_severity=Severity.medium,
                tool=DEVELOPER_TOOL,
            )
        )
    return DeveloperClaims(claims=claims, candidates=candidates, messages=messages)
