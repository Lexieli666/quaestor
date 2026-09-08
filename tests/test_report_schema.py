"""Phase 8: the packaged report schema, and the refusals it defines.

`examples/golden_report/REPORT_SCHEMA.json` is the Phase 1 specification of a report; the renderer
needs it at runtime and `examples/` is not in the wheel, so the file is copied into the package as
`src/quaestor/report/report_schema.json`. The first test here is the pin that keeps the two
copies from drifting: it compares them byte for byte, so a sanctioned edit to the golden schema
under D-011 that forgot the copy fails the suite rather than leaving the renderer enforcing last
month's rules (D-074).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from quaestor.errors import ReportSchemaError
from quaestor.report.schema import (
    APPENDIX_A_HEADING,
    OPEN_ITEMS_HEADING,
    REPORT_SCHEMA,
    REQUIRED_HEADINGS,
    SCHEMA_FILE,
    check_front_matter,
    check_structure,
    front_matter_of,
    required_renderer_blocks,
)
from quaestor.vocab import Configuration

GOLDEN = Path(__file__).resolve().parents[1] / "examples" / "golden_report" / "REPORT_SCHEMA.json"

GOOD_FRONT = {
    "schema_version": 1,
    "quaestor_version": "0.1.0.dev0",
    "package": "credit_default",
    "version": "1.0",
    "model_type": "binary_classification",
    "configuration": "full_agent",
    "model": "fake",
    "run_id": "credit_default-full_agent-0000",
    "data_mode": "synthetic",
    "synthetic_n": 5000,
    "grounding_precision_pre": 0.98,
    "grounding_precision_post": 1.0,
    "n_claims": 49,
    "n_findings_by_severity": {"high": 0, "medium": 0, "low": 1, "info": 0},
    "generated": "2026-09-08T00:00:00Z",
    "illustrative": False,
}


def _headings_with_open_items() -> list[str]:
    """The eleven level-2 headings, with section 6's required `### Open items` under its own."""
    lines: list[str] = []
    for heading in REQUIRED_HEADINGS:
        lines.append(heading)
        if heading == "## 6. Findings and recommendations":
            lines.append(OPEN_ITEMS_HEADING)
    return lines


MINIMAL_REPORT = "\n".join(
    [
        "---",
        "schema_version: 1",
        "---",
        "",
        "# Validation report",
        "",
        *_headings_with_open_items(),
    ]
)


def test_the_packaged_schema_is_the_golden_schema_byte_for_byte() -> None:
    assert SCHEMA_FILE.read_bytes() == GOLDEN.read_bytes()


def test_the_schema_exposes_the_eleven_headings_and_the_scope_block() -> None:
    assert len(REQUIRED_HEADINGS) == 11
    assert REQUIRED_HEADINGS[0] == "## 1. Summary and scope"
    assert REQUIRED_HEADINGS[-1] == "## Appendix D — Not checked"
    assert APPENDIX_A_HEADING in REQUIRED_HEADINGS
    blocks = required_renderer_blocks()
    assert [block["name"] for block in blocks] == ["scope"]


def test_good_front_matter_has_no_problems() -> None:
    assert check_front_matter(GOOD_FRONT) == []


@pytest.mark.parametrize(
    ("key", "value", "needle"),
    [
        ("configuration", "vibes", "configuration"),
        ("grounding_precision_post", 1.5, "grounding_precision_post"),
        ("package", "Credit Default", "package"),
        ("quaestor_version", "", "quaestor_version"),
        ("illustrative", "yes", "illustrative"),
    ],
)
def test_front_matter_that_breaks_the_schema_is_named_field_by_field(
    key: str, value: object, needle: str
) -> None:
    problems = check_front_matter({**GOOD_FRONT, key: value})
    assert problems
    assert any(needle in problem for problem in problems)


def test_a_missing_grounding_figure_is_its_own_refusal() -> None:
    """Spec 3.11: "refuses to write a report ... without both precision figures"."""
    front = dict(GOOD_FRONT)
    front["grounding_precision_pre"] = None
    problems = check_front_matter(front)
    assert any("carries no grounding_precision_pre" in problem for problem in problems)


def test_synthetic_mode_must_state_how_many_rows_it_generated() -> None:
    front = {key: value for key, value in GOOD_FRONT.items() if key != "synthetic_n"}
    assert check_front_matter(front)


def test_a_well_formed_report_skeleton_passes_the_structural_checks() -> None:
    report = MINIMAL_REPORT + "\n" + required_renderer_blocks()[0]["begin"] + "\n"
    assert check_structure(report, configuration=Configuration.rules_only) == []


def test_a_section_six_without_open_items_is_refused() -> None:
    """D-096: a report whose section 6 has no open-items subsection is not written."""
    report = MINIMAL_REPORT.replace(OPEN_ITEMS_HEADING + "\n", "")
    problems = check_structure(report, configuration=Configuration.rules_only)
    assert any(OPEN_ITEMS_HEADING in problem for problem in problems)


def test_a_report_with_no_section_six_at_all_is_reported_once_for_the_heading() -> None:
    """With section 6 gone the level-2 rule has already named the real problem (D-096)."""
    report = MINIMAL_REPORT.replace("## 6. Findings and recommendations\n", "")
    problems = check_structure(report, configuration=Configuration.rules_only)
    assert any("level-2 headings" in problem for problem in problems)
    assert any(OPEN_ITEMS_HEADING in problem for problem in problems)


def test_headings_out_of_order_are_reported_with_what_was_found() -> None:
    report = MINIMAL_REPORT.replace("## 2. Conceptual soundness\n", "")
    problems = check_structure(report, configuration=Configuration.rules_only)
    assert any("level-2 headings" in problem for problem in problems)


def test_a_report_without_appendix_a_is_refused() -> None:
    report = MINIMAL_REPORT.replace(APPENDIX_A_HEADING, "## Appendix A — Something else")
    problems = check_structure(report, configuration=Configuration.rules_only)
    assert any("claims appendix" in problem for problem in problems)


def test_a_malformed_double_bracket_token_is_refused() -> None:
    report = MINIMAL_REPORT + "\nThe AUC is 0.74 [[art:ZZZZ:metrics.test.auc]].\n"
    problems = check_structure(report, configuration=Configuration.rules_only)
    assert any("not well-formed citations" in problem for problem in problems)


def test_a_table_directive_the_renderer_did_not_expand_is_refused() -> None:
    report = MINIMAL_REPORT + "\n[[table:calibration.test]]\n"
    problems = check_structure(report, configuration=Configuration.rules_only)
    assert any("[[table:calibration.test]]" in problem for problem in problems)


def test_the_word_compliant_is_refused_anywhere_in_the_report() -> None:
    report = MINIMAL_REPORT + "\nThis model is compliant with the guidance.\n"
    problems = check_structure(report, configuration=Configuration.rules_only)
    assert any("whole report" in problem for problem in problems)


def test_a_citation_that_leaked_into_appendix_c_is_refused() -> None:
    report = MINIMAL_REPORT + "\n\n## Appendix C — Run trace summary\n[[art:4bb1344e:metrics.a]]\n"
    problems = check_structure(report, configuration=Configuration.rules_only)
    assert any("Appendix C and Appendix D only" in problem for problem in problems)


def test_an_uncovered_number_binds_full_agent_and_not_the_other_two() -> None:
    """The third refusal rule names `full_agent`, because it is the arm that drafts with rules."""
    report = MINIMAL_REPORT + "\n" + required_renderer_blocks()[0]["begin"] + "\n"
    uncovered = ["0.68"]
    assert (
        check_structure(report, configuration=Configuration.rules_only, uncovered=uncovered) == []
    )
    problems = check_structure(report, configuration=Configuration.full_agent, uncovered=uncovered)
    assert any("0.68" in problem for problem in problems)


def test_front_matter_of_reads_the_block_and_refuses_a_report_without_one() -> None:
    assert front_matter_of(MINIMAL_REPORT) == {"schema_version": 1}
    with pytest.raises(ReportSchemaError, match="delimited by ---"):
        front_matter_of("# no front matter here")
    with pytest.raises(ReportSchemaError, match="not a mapping"):
        front_matter_of("---\n- a\n- list\n---\n")


def test_the_schema_declares_the_three_refusal_rules_the_renderer_implements() -> None:
    rules = REPORT_SCHEMA["x-quaestor-refusal-rules"]
    assert len(rules) == 3
    assert any("front matter" in rule for rule in rules)
    assert any("Appendix A" in rule for rule in rules)
    assert any("⟦unverified" in rule for rule in rules)
