"""Phase 7: `package.yaml` `claims:`, the claim channel of a T1 finding, and synthetic mode."""

from __future__ import annotations

from pathlib import Path

import pytest

from quaestor import ArtifactStore, DefectClass, Finding, load_package
from quaestor.artifacts import ArtifactKind
from quaestor.package import ModelPackage
from quaestor.verifier import ClaimSource, ClaimStatus, verify_developer_claims
from quaestor.verifier.developer import DEVELOPER_CLAIM_PREFIX, logical_names_for

SUBJECT = Path(__file__).resolve().parents[1] / "subjects" / "credit_default"


@pytest.fixture
def package() -> ModelPackage:
    """The shipped credit subject, which declares two developer claims about its real fit."""
    return load_package(SUBJECT)


@pytest.fixture
def store(tmp_path: Path) -> ArtifactStore:
    """A store whose test AUC agrees with the declaration and whose Brier does not."""
    store = ArtifactStore(tmp_path / "artifacts")
    store.put("metrics.test.auc", 0.7553, ArtifactKind.scalar)
    store.put("metrics.test.brier", 0.1602, ArtifactKind.scalar)
    return store


def test_the_package_declares_the_claims_this_module_verifies(package: ModelPackage) -> None:
    """The fixture is the shipped subject, so the test moves when the package does."""
    assert [claim.metric for claim in package.spec.claims] == ["auc", "brier"]


def test_synthetic_mode_evaluates_nothing_and_returns_a_note(
    package: ModelPackage, store: ArtifactStore
) -> None:
    """D-016: a synthetic AUC cannot verify a number declared for the real sample."""
    result = verify_developer_claims(package, store)
    assert result.claims == []
    assert result.candidates == []
    assert result.note is not None and "synthetic" in result.note
    assert "2" in result.note


def test_under_data_each_declaration_becomes_a_verified_claim(
    package: ModelPackage, store: ArtifactStore, tmp_path: Path
) -> None:
    """The declared AUC of 0.755 matches 0.7553; the declared Brier of 0.139 does not."""
    result = verify_developer_claims(package, store, data_dir=tmp_path)
    assert [claim.source for claim in result.claims] == [ClaimSource.developer] * 2
    assert [claim.status for claim in result.claims] == [
        ClaimStatus.verified,
        ClaimStatus.mismatch,
    ]
    assert result.claims[0].citation is not None
    assert "metrics.test.auc" in result.claims[0].citation


def test_a_mismatched_declaration_raises_a_t1_candidate_with_stored_evidence(
    package: ModelPackage, store: ArtifactStore, tmp_path: Path
) -> None:
    """The comparison itself is an artifact, so the finding it feeds has evidence to cite."""
    result = verify_developer_claims(package, store, data_dir=tmp_path)
    assert [candidate.defect_class for candidate in result.candidates] == [DefectClass.T1]
    candidate = result.candidates[0]
    record = store.load(f"{DEVELOPER_CLAIM_PREFIX}.1")
    assert record["declared"] == 0.139
    assert record["artifact"] == "metrics.test.brier"
    assert record["artifact_value"] == 0.1602
    assert store.artifact(f"{DEVELOPER_CLAIM_PREFIX}.1").hash in candidate.evidence
    finding = Finding.from_candidates([candidate], store=store)
    assert finding.defect_class is DefectClass.T1
    assert len(finding.evidence) == 2


def test_a_declaration_with_no_artifact_is_unsupported(
    package: ModelPackage, tmp_path: Path
) -> None:
    """Nothing to compare to is not a mismatch: no citation could be formed at all."""
    empty = ArtifactStore(tmp_path / "empty")
    result = verify_developer_claims(package, empty, data_dir=tmp_path)
    assert {claim.status for claim in result.claims} == {ClaimStatus.unsupported}
    assert result.candidates == []


def test_a_package_with_no_claims_returns_the_other_note(
    package: ModelPackage, store: ArtifactStore, tmp_path: Path
) -> None:
    """Appendix D distinguishes "declares none" from "declared but not evaluated"."""
    bare = package.model_copy(update={"spec": package.spec.model_copy(update={"claims": []})})
    result = verify_developer_claims(bare, store, data_dir=tmp_path)
    assert result.note is not None and "no claims" in result.note


def test_the_logical_names_a_declaration_could_mean_are_tried_in_order() -> None:
    """A declaration names a metric and a split; the artifact has to be found from those."""
    assert logical_names_for("auc", "test") == [
        "metrics.test.auc",
        "auc.test",
        "auc",
        "auc.max",
    ]
    assert logical_names_for("psi", None) == ["psi", "psi.max"]


def test_a_split_the_claim_grammar_does_not_know_becomes_null(
    package: ModelPackage, store: ArtifactStore, tmp_path: Path
) -> None:
    """`package.yaml` may name a split the grammar's four-value enum does not carry."""
    declaration = package.spec.claims[0].model_copy(update={"split": "holdout_2019"})
    spec = package.spec.model_copy(update={"claims": [declaration]})
    result = verify_developer_claims(
        package.model_copy(update={"spec": spec}), store, data_dir=tmp_path
    )
    assert result.claims[0].split is None
