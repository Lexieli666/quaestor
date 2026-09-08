"""Structural checks over examples/golden_report/, the Phase 1 executable specification.

Checks 1-9 are the nine checks of the Cowork draft's `check_golden.py` (kept in the package folder,
not here); checks 10-13 add the manifest pin, the `DECISIONS.md` D-011 pin, the two JSON Schemas
over `claims.json` and `findings.json`, and the regulatory section ids. From Phase 8 the same
functions are pointed at a real pipeline run, which is what makes the golden a specification rather
than a description.

Offline by construction: PyYAML, jsonschema and the standard library only, no git, no network, no
skips and no xfails.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "examples" / "golden_report"
DECISIONS = ROOT / "DECISIONS.md"
OUTLINE = ROOT / "data" / "regulatory" / "sr11-7-outline.yaml"

MANIFEST_FILES = (
    "CLAIMS_SCHEMA.json",
    "FINDINGS_SCHEMA.json",
    "REPORT_SCHEMA.json",
    "claims.json",
    "findings.json",
    "report.md",
)

REPORT = (GOLDEN / "report.md").read_text(encoding="utf-8")
SCHEMA: dict[str, Any] = json.loads((GOLDEN / "REPORT_SCHEMA.json").read_text(encoding="utf-8"))
CLAIMS: dict[str, Any] = json.loads((GOLDEN / "claims.json").read_text(encoding="utf-8"))
FINDINGS: dict[str, Any] = json.loads((GOLDEN / "findings.json").read_text(encoding="utf-8"))
FRONT: dict[str, Any] = yaml.safe_load(REPORT.split("---\n")[1])


def sha256_of(path: Path) -> str:
    """Hex digest of a file's bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def appendix_b_index() -> dict[str, str]:
    """Logical name to hash8, read from the Appendix B table of `report.md`."""
    rows = re.findall(r"^\| `([^`]+)` \| `([0-9a-f]{8})` \|", REPORT, flags=re.M)
    return dict(rows)


def drafted_prose() -> str:
    """Sections 1-7 with every excluded token removed (the regex pre-pass of spec 3.10)."""
    body = REPORT.split("\n---\n", 1)[1].split("## Appendix A")[0]
    body = re.sub(SCHEMA["x-quaestor-renderer-block-pattern"], " ", body)
    body = re.sub(r"\[\[art:[0-9a-f]{8}:[^\]]+\]\]|\[\[reg:[^\]]+\]\]", " ", body)
    body = re.sub(r"`[^`]*`", " ", body)
    body = re.sub(r"^#+ .*$", " ", body, flags=re.M)
    return re.sub(r"§\d+|F-\d{3}|version " + re.escape(FRONT["version"]), " ", body)


# 1
def test_front_matter_validates_against_report_schema() -> None:
    jsonschema.Draft202012Validator.check_schema(SCHEMA)
    jsonschema.Draft202012Validator(SCHEMA).validate(FRONT)


# 2
def test_level_2_headings_are_exactly_the_required_headings_in_order() -> None:
    h2 = [line for line in REPORT.splitlines() if line.startswith("## ")]
    assert h2 == SCHEMA["x-quaestor-required-headings"]


# 3
def test_scope_renderer_block_is_the_first_thing_under_section_1() -> None:
    section_1 = REPORT.split("## 1. Summary and scope\n", 1)[1]
    begin = SCHEMA["x-quaestor-required-renderer-blocks"][0]["begin"]
    assert section_1.lstrip().startswith(begin)


# 4
def test_every_double_bracket_token_is_a_well_formed_citation() -> None:
    artifact = re.compile(SCHEMA["x-quaestor-citation-patterns"]["artifact"])
    regulatory = re.compile(SCHEMA["x-quaestor-citation-patterns"]["regulatory"])
    tokens = re.findall(r"\[\[[^\]]+\]\]", REPORT)
    assert tokens, "the golden report carries no citations at all"
    bad = [t for t in tokens if not (artifact.fullmatch(t) or regulatory.fullmatch(t))]
    assert not bad, bad


# 5
def test_front_matter_agrees_with_claims_json_and_findings_json() -> None:
    grounding = CLAIMS["grounding"]
    assert grounding["pre_repair"]["precision"] == FRONT["grounding_precision_pre"]
    assert grounding["post_repair"]["precision"] == FRONT["grounding_precision_post"]
    assert grounding["post_repair"]["n_claims"] == FRONT["n_claims"] == len(CLAIMS["post_repair"])
    severities = Counter(f["severity"] for f in FINDINGS["findings"])
    by_severity = {k: severities.get(k, 0) for k in ("high", "medium", "low", "info")}
    assert by_severity == FRONT["n_findings_by_severity"]


# 6
def test_artifact_citations_and_finding_evidence_resolve_against_appendix_b() -> None:
    index = appendix_b_index()
    cited = list(re.finditer(r"\[\[art:([0-9a-f]{8}):([A-Za-z0-9_.-]+?)(?:#|\]\])", REPORT))
    assert cited, "the golden report cites no artifact"
    for match in cited:
        assert index.get(match.group(2)) == match.group(1), match.groups()
    for finding in FINDINGS["findings"]:
        assert finding["evidence"], finding["id"]
        assert all(h in index.values() for h in finding["evidence"]), finding["id"]


# 7
def test_every_numeric_token_in_the_prose_is_covered_by_a_post_repair_claim() -> None:
    numeric = re.findall(r"(?<![\w.])-?\d[\d,]*(?:\.\d+)?(?:[eE][+-]?\d+)?%?", drafted_prose())
    unclaimed = Counter(
        (claim["value"], claim["unit"] == "percent") for claim in CLAIMS["post_repair"]
    )
    uncovered = []
    for token in numeric:
        key = (float(token.replace(",", "").rstrip("%")), token.endswith("%"))
        if unclaimed[key] > 0:
            unclaimed[key] -= 1
        else:
            uncovered.append(token)
    assert not uncovered, f"numbers in the prose with no claim: {uncovered}"
    assert not [k for k, v in unclaimed.items() if v > 0], "claims with no token in the prose"


# 8
def test_the_report_uses_no_forbidden_compliance_language() -> None:
    whole_report = [
        fp for fp in SCHEMA["x-quaestor-forbidden-patterns"] if fp["scope"] == "whole report"
    ]
    assert whole_report, "REPORT_SCHEMA.json declares no whole-report forbidden pattern"
    for forbidden in whole_report:
        assert not re.search(forbidden["pattern"], REPORT, flags=re.I), forbidden


# 9
def test_every_claim_is_verified_post_repair_or_wrapped_in_the_prose() -> None:
    for claim in CLAIMS["post_repair"]:
        if claim["status"] != "verified":
            assert f"⟦unverified: {claim['value']}" in REPORT, claim["id"]


# 10
def test_every_golden_file_hash_matches_manifest_json() -> None:
    manifest = json.loads((GOLDEN / "MANIFEST.json").read_text(encoding="utf-8"))
    assert set(manifest["files"]) == set(MANIFEST_FILES)
    for name, expected in manifest["files"].items():
        assert sha256_of(GOLDEN / name) == expected, name


# 11
def test_manifest_json_hash_matches_the_pin_in_decisions_d_011() -> None:
    decisions = DECISIONS.read_text(encoding="utf-8")
    entry = re.search(r"^## D-011\..*?(?=^## D-|\Z)", decisions, flags=re.M | re.S)
    assert entry, "DECISIONS.md has no D-011 entry pinning examples/golden_report/MANIFEST.json"
    pin = re.search(
        r"Pinned hash[^`]*`MANIFEST\.json`[^`]*`([0-9a-f]{64})`", entry.group(0), flags=re.S
    )
    assert pin, "D-011 states no pinned MANIFEST.json sha256"
    assert sha256_of(GOLDEN / "MANIFEST.json") == pin.group(1)


# 12
def test_claims_json_and_findings_json_validate_against_their_schemas() -> None:
    pairs = (("CLAIMS_SCHEMA.json", CLAIMS), ("FINDINGS_SCHEMA.json", FINDINGS))
    for schema_name, document in pairs:
        schema = json.loads((GOLDEN / schema_name).read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(document)


# 13
def test_every_regulatory_citation_names_a_section_of_the_sr11_7_outline() -> None:
    outline = yaml.safe_load(OUTLINE.read_text(encoding="utf-8"))
    section_ids = {str(section["section_id"]) for section in outline["sections"]}
    cited = re.findall(r"\[\[reg:(SR11-7|OCC2011-12):([^\]]+)\]\]", REPORT)
    assert cited, "the golden report cites no guidance section"
    for document, section_id in cited:
        assert document in {"SR11-7", "OCC2011-12"}, document
        assert section_id in section_ids, f"{document}:{section_id}"
