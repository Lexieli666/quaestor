"""Phase 7: every one of the golden report's 92 post-repair claims, re-matched for real.

`examples/golden_report/` fixes the shape of a report and says so: its numbers are illustrative and
its hashes are `sha256(logical_name)[:8]`, which resolve to nothing. This module rebuilds an
artifact store from Appendix B under the golden's own logical names and runs the Phase 7 matcher
over all 92 claims of `claims.json`.

**The hashes cannot agree and this test does not pretend they do.** A content address of an
illustrative value is not the address of the same value stored today, so each citation's `hash8`
is rewritten to the rebuilt store's before matching, and the citation is asserted on its logical
name and its path. Every other citation check in the repository -- `tests/test_citations.py`,
`tests/test_verifier_match.py`, and the pipeline itself from Phase 8 -- asserts the hash, which is
the half that stops a number being cited to another run's artifact. See `tests/verifiersupport.py`
for how the store is built and which of its values come from the report's prose rather than from
Appendix B.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import pytest

from quaestor.artifacts import ArtifactStore
from quaestor.verifier import Claim, ClaimStatus, VerifiedClaim, grounding, match_claims
from verifiersupport import golden_store, rehash_citation

GOLDEN = Path(__file__).resolve().parents[1] / "examples" / "golden_report"
CLAIMS: dict[str, Any] = json.loads((GOLDEN / "claims.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def store(tmp_path_factory: pytest.TempPathFactory) -> ArtifactStore:
    """A real store holding every artifact Appendix B names, under its own logical names."""
    return golden_store(tmp_path_factory.mktemp("golden") / "artifacts")


def rebound(raw: dict[str, Any], store: ArtifactStore) -> Claim:
    """The golden claim with its citation pointed at the rebuilt store."""
    fields = {key: value for key, value in raw.items() if key in Claim.model_fields}
    fields["citation"] = rehash_citation(raw["citation"], store)
    return Claim.model_validate(fields)


def test_every_post_repair_claim_of_the_golden_report_verifies(store: ArtifactStore) -> None:
    """All 92, through the real matcher, against a store built from Appendix B."""
    claims = [rebound(raw, store) for raw in CLAIMS["post_repair"]]
    matches = match_claims(claims, store)
    failed = [
        (match.claim.value, match.claim.citation, match.status.value, match.message)
        for match in matches
        if match.status is not ClaimStatus.verified
    ]
    assert failed == []
    assert len(matches) == 92
    assert grounding([match.claim for match in matches]).precision == 1.0


def test_the_rebuilt_artifact_values_agree_with_the_golden_s_own(store: ArtifactStore) -> None:
    """A claim's `artifact_value` is what the golden recorded, not merely something in range."""
    for raw in CLAIMS["post_repair"]:
        match = match_claims([rebound(raw, store)], store)[0]
        assert match.claim.artifact_value == pytest.approx(raw["artifact_value"]), raw["text"]


def test_every_tolerance_narrows_or_stands_under_the_rounding_amendment(
    store: ArtifactStore,
) -> None:
    """D-069 can only tighten what D-014 allowed, and it tightens 60 of the golden's 92 claims.

    The golden `claims.json` was written in Phase 1 under D-014, whose tolerance is the flat
    default for the claim's unit; D-069 holds a number to the precision its own sentence wrote and
    keeps that default as a ceiling, so the applied tolerance can only fall. It falls for 60 of
    the 92 -- every four-decimal metric from 0.005 to 0.00005, `22.0%` from 0.005 to 0.0005, and
    each of the six claims that declared a `rounding`, which under D-014 *widened* the default and
    now narrows it -- and every one of the 92 still verifies, which is the assertion above.
    """
    narrowed = 0
    for raw in CLAIMS["post_repair"]:
        applied = match_claims([rebound(raw, store)], store)[0].claim.tolerance
        assert applied <= raw["tolerance"] + 1e-12, raw["text"]
        narrowed += applied < raw["tolerance"] - 1e-12
    assert narrowed == 60


def test_the_pre_repair_figures_reproduce_from_the_golden_s_own_claim_list() -> None:
    """`grounding` over `pre_repair` gives the two numbers the front matter prints."""
    figure = grounding([VerifiedClaim.model_validate(raw) for raw in CLAIMS["pre_repair"]])
    assert figure.model_dump(mode="json") == CLAIMS["grounding"]["pre_repair"]
    after = grounding([VerifiedClaim.model_validate(raw) for raw in CLAIMS["post_repair"]])
    assert after.model_dump(mode="json") == CLAIMS["grounding"]["post_repair"]


def test_the_store_holds_every_logical_name_the_golden_cites(store: ArtifactStore) -> None:
    """Appendix B is the artifact index, so nothing the prose cites may be missing from it."""
    cited = Counter(
        raw["citation"].split(":")[2].split("]]")[0].split("#")[0]
        for raw in CLAIMS["post_repair"]
        if raw["citation"]
    )
    assert set(cited) <= set(store.names())
    assert len(store) == 62
