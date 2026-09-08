"""Phase 7: the claim grammar and the `claims.json` envelope, against the Phase 1 schema.

`examples/golden_report/CLAIMS_SCHEMA.json` was written before this code and is pinned by
`MANIFEST.json`, so parsing the golden `claims.json` into the models and serialising it back is
the check that the models *are* the schema rather than something close to it.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema
import pytest
from pydantic import ValidationError

from quaestor.verifier import (
    DEFAULT_TOLERANCES,
    Claim,
    ClaimsDocument,
    ClaimSource,
    ClaimStatus,
    Comparison,
    Exclusion,
    Repair,
    RepairSide,
    SplitName,
    Unit,
    VerifiedClaim,
    claim_id,
)
from quaestor.vocab import Configuration, ReportSection

GOLDEN = Path(__file__).resolve().parents[1] / "examples" / "golden_report"
CLAIMS_SCHEMA: dict[str, Any] = json.loads(
    (GOLDEN / "CLAIMS_SCHEMA.json").read_text(encoding="utf-8")
)
GOLDEN_CLAIMS: dict[str, Any] = json.loads((GOLDEN / "claims.json").read_text(encoding="utf-8"))


def test_the_golden_claims_json_parses_into_the_models_and_re_serialises_unchanged() -> None:
    """Key order aside, the models round-trip the Phase 1 specification exactly."""
    document = ClaimsDocument.model_validate(GOLDEN_CLAIMS)
    assert document.to_payload() == GOLDEN_CLAIMS
    jsonschema.validate(document.to_payload(), CLAIMS_SCHEMA)


def test_every_golden_claim_parses_into_verified_claim_field_for_field() -> None:
    """All 92 pre-repair and 92 post-repair claims are the grammar, not a superset of it."""
    for key in ("pre_repair", "post_repair"):
        for raw in GOLDEN_CLAIMS[key]:
            claim = VerifiedClaim.model_validate(raw)
            assert claim.to_payload() == raw


def test_a_claim_computes_its_own_id_and_keeps_one_it_is_given() -> None:
    """The id is `stable_hash([section, text, value])`, and a file's own id survives a read."""
    claim = Claim(text="AUC is 0.74", value=0.74, section=ReportSection.outcomes)
    assert claim.id == claim_id(ReportSection.outcomes, "AUC is 0.74", 0.74)
    assert (
        GOLDEN_CLAIMS["pre_repair"][0]["id"]
        == VerifiedClaim.model_validate(GOLDEN_CLAIMS["pre_repair"][0]).id
    )


def test_a_report_claim_may_not_be_not_evaluated() -> None:
    """`not_evaluated` is the synthetic-mode status of a developer claim and nothing else."""
    with pytest.raises(ValidationError, match="developer claim"):
        VerifiedClaim(
            text="AUC is 0.74",
            value=0.74,
            section=ReportSection.outcomes,
            source=ClaimSource.report,
            status=ClaimStatus.not_evaluated,
        )


def test_the_grammar_holds_the_enums_the_schema_holds() -> None:
    """Each enum is exhaustive against `CLAIMS_SCHEMA.json`, which is what closes the file."""
    defs = CLAIMS_SCHEMA["$defs"]
    properties = defs["claim_core"]["properties"]
    assert [unit.value for unit in Unit] == properties["unit"]["enum"]
    assert [c.value for c in Comparison] == properties["comparison"]["enum"]
    assert [s.value for s in ClaimSource] == properties["source"]["enum"]
    assert [s.value for s in SplitName] + [None] == properties["split"]["enum"]
    assert [s.value for s in ClaimStatus if s is not ClaimStatus.not_evaluated] == defs["status"][
        "enum"
    ]
    assert [s.value for s in ReportSection] == defs["section"]["enum"]


def test_a_built_document_computes_both_grounding_figures(tmp_path: Path) -> None:
    """`build` derives the figures from the claim lists rather than being told them."""
    claims = [
        VerifiedClaim(
            text=f"metric {i} is 0.7",
            value=0.7,
            section=ReportSection.outcomes,
            status=ClaimStatus.verified if i else ClaimStatus.unsupported,
        )
        for i in range(4)
    ]
    document = ClaimsDocument.build(
        package="credit_default",
        version="1.0",
        configuration=Configuration.full_agent,
        run_id="r1",
        pre_repair=claims,
        exclusions=[Exclusion(pattern="package_version", examples=["1.0"])],
        developer_claims_note="synthetic mode does not evaluate developer claims.",
    )
    assert document.precision_pre == 0.75
    assert document.precision_post == 0.75
    assert document.n_claims == 4
    assert document.tolerances == DEFAULT_TOLERANCES
    path = document.write(tmp_path / "claims.json")
    jsonschema.validate(json.loads(path.read_text(encoding="utf-8")), CLAIMS_SCHEMA)
    assert ClaimsDocument.read(path).to_payload() == document.to_payload()


def test_a_document_with_no_note_omits_the_key_rather_than_writing_null(tmp_path: Path) -> None:
    """`developer_claims_note` is optional in the schema; a null would be a third spelling."""
    document = ClaimsDocument.build(
        package="credit_default",
        version="1.0",
        configuration=Configuration.rules_only,
        run_id="r1",
        pre_repair=[],
    )
    assert "developer_claims_note" not in document.to_payload()
    jsonschema.validate(document.to_payload(), CLAIMS_SCHEMA)


def test_a_repair_record_is_the_shape_appendix_a_prints() -> None:
    """Phase 8 fills `repairs`; Phase 7 fixes what one looks like."""
    repair = Repair(
        section=ReportSection.summary,
        claim_id="ea3c9ebe0e303e95",
        before=RepairSide(value=3500, status=ClaimStatus.unsupported),
        after=RepairSide(value=3500, status=ClaimStatus.verified),
        instruction="you wrote 3,500 with no citation; the artifact profile.train.n has 3500",
    )
    document = ClaimsDocument.build(
        package="credit_default",
        version="1.0",
        configuration=Configuration.full_agent,
        run_id="r1",
        pre_repair=[],
        repairs=[repair],
    )
    jsonschema.validate(document.to_payload(), CLAIMS_SCHEMA)
