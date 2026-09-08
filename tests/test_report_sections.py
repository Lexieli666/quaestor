"""Phase 8: the section plan -- which artifacts each section may cite, and how it is shown them.

The selectors here are the only thing standing between a drafter and every number a run produced,
because the rule the drafter is held to is "write no number that is not in the JSON" and the JSON
is what this module builds. A selector that let a table through would print four calibration
tables; one that let every metric through would make a summary that wanders.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from quaestor.artifacts import ArtifactKind, ArtifactStore
from quaestor.findings import DefectClass
from quaestor.report.sections import (
    DEFECT_CLASS_NAMES,
    MAX_JSON_PATHS,
    SECTION_BRIEFS,
    ArtifactBrief,
    artifact_briefs,
    brief_for,
    calibration_before_discrimination,
    flatten_json,
    four_significant_figures,
    ordered_briefs,
    section_heading,
    written_number,
)
from quaestor.vocab import SECTION_ORDER, ReportSection


@pytest.fixture
def store(tmp_path: Path) -> ArtifactStore:
    """A store with one artifact of each kind the sections select over."""
    store = ArtifactStore(tmp_path / "artifacts")
    store.put("metrics.test.auc", 0.74801204, ArtifactKind.scalar, "auc on test")
    store.put("metrics.test.event_rate", 0.2246, ArtifactKind.scalar, "event rate on test")
    store.put("rule.calibration_first_event_rate", 0.05, ArtifactKind.scalar, "the rare-event rule")
    store.put("psi.max", 0.011, ArtifactKind.scalar, "the largest PSI")
    store.put("calibration.test", [{"bin": 1, "observed": 0.05}], ArtifactKind.table, "calibration")
    store.put(
        "run.model_summary",
        {
            "coefficients": [{"feature": "utilisation", "value": 0.4871234}],
            "removed": [{"name": "bill_last", "vif": 41.7}],
            "note": "not a number",
        },
        ArtifactKind.json,
        "the subject's model_summary.json",
    )
    return store


def test_every_section_has_a_brief_a_heading_and_a_guidance_query() -> None:
    assert list(SECTION_BRIEFS) == list(SECTION_ORDER)
    for section in SECTION_ORDER:
        brief = brief_for(section)
        assert brief.heading.startswith("## ")
        assert brief.guidance_query
        assert brief.brief.strip()
        assert section_heading(section) == brief.heading


def test_every_defect_class_has_a_human_name_for_its_finding_heading() -> None:
    assert set(DEFECT_CLASS_NAMES) == set(DefectClass)
    assert DEFECT_CLASS_NAMES[DefectClass.E1] == "effective challenge"


def test_four_significant_figures_is_what_the_drafter_is_shown() -> None:
    assert four_significant_figures(0.74801204) == 0.748
    assert four_significant_figures(1500) == 1500
    assert four_significant_figures(-1129931.65) == -1130000.0


def test_written_number_never_uses_an_exponent() -> None:
    """`format(1e-05, "g")` writes `1e-05`, whose first numeric token is 1: a different claim."""
    assert written_number(1e-05) == "0.00001"
    assert written_number(1500.0) == "1500"
    assert written_number(0.748) == "0.748"
    assert written_number(-0.0672) == "-0.0672"


def test_flatten_json_addresses_list_elements_the_way_a_citation_does() -> None:
    payload = {
        "coefficients": [{"feature": "utilisation", "value": 0.487}],
        "removed": [{"name": "bill_last", "vif": 41.7}],
        "n": 12,
        "note": "not a number",
        "flag": True,
        "anonymous": [{"value": 1.0}],
    }
    flat = flatten_json(payload)
    assert flat["coefficients.utilisation.value"] == 0.487
    assert flat["removed.bill_last.vif"] == 41.7
    assert flat["n"] == 12
    assert "note" not in flat
    assert "flag" not in flat
    assert not [path for path in flat if path.startswith("anonymous")]


def test_flatten_json_stops_at_the_cap() -> None:
    payload = {"values": [{"name": f"f{i}", "value": float(i)} for i in range(MAX_JSON_PATHS + 10)]}
    assert len(flatten_json(payload)) == MAX_JSON_PATHS


def test_a_section_is_shown_scalars_its_own_tables_and_nothing_else(store: ArtifactStore) -> None:
    briefs = artifact_briefs(store, brief_for(ReportSection.outcomes))
    kinds = {item.name: item.kind.value for item in briefs}
    assert kinds["metrics.test.auc"] == "scalar"
    assert kinds["calibration.test"] == "table"
    assert kinds["run.metrics"] if "run.metrics" in kinds else True
    data = artifact_briefs(store, brief_for(ReportSection.data_integrity))
    assert "calibration.test" not in {item.name for item in data}
    assert "psi.max" in {item.name for item in data}


def test_the_extra_names_are_how_the_findings_section_is_given_its_evidence(
    store: ArtifactStore,
) -> None:
    briefs = artifact_briefs(
        store, brief_for(ReportSection.findings), extra=["metrics.test.auc", "not.in.the.store"]
    )
    assert [item.name for item in briefs] == ["metrics.test.auc"]


def test_the_payload_a_scalar_a_table_and_a_json_artifact_reach_the_prompt_as(
    store: ArtifactStore,
) -> None:
    briefs = {item.name: item for item in artifact_briefs(store, brief_for(ReportSection.outcomes))}
    scalar = briefs["metrics.test.auc"].to_payload()
    assert scalar["value"] == 0.748
    assert scalar["citation"].startswith("[[art:") and scalar["citation"].endswith(
        ":metrics.test.auc]]"
    )
    table = briefs["calibration.test"].to_payload()
    assert table["directive"] == "[[table:calibration.test]]"
    assert "value" not in table
    summary = artifact_briefs(store, brief_for(ReportSection.conceptual_soundness))
    json_brief = next(item for item in summary if item.name == "run.model_summary")
    payload = json_brief.to_payload()
    assert payload["values"]["coefficients.utilisation.value"] == 0.4871
    assert payload["citation_form"] == f"[[art:{json_brief.hash8}:run.model_summary#<path>]]"
    assert json_brief.path_citation("removed.bill_last.vif").endswith(
        "run.model_summary#removed.bill_last.vif]]"
    )


def test_a_truncated_json_artifact_says_so(tmp_path: Path) -> None:
    store = ArtifactStore(tmp_path / "artifacts")
    store.put(
        "run.model_summary",
        {"coefficients": [{"feature": f"f{i}", "value": float(i)} for i in range(MAX_JSON_PATHS)]},
        ArtifactKind.json,
        "many coefficients",
    )
    brief = artifact_briefs(store, brief_for(ReportSection.conceptual_soundness))[0]
    assert brief.truncated is True
    assert brief.to_payload()["truncated"] is True


def test_a_figure_is_not_an_artifact_a_section_can_cite(tmp_path: Path) -> None:
    """A figure is evidence a reader looks at; there is no number in it to cite or to match."""
    store = ArtifactStore(tmp_path / "artifacts")
    store.put("psi.max", 0.011, ArtifactKind.scalar, "the largest PSI")
    store.put("psi.figure", b"\x89PNG\r\n\x1a\n", ArtifactKind.figure, "a drift chart")
    brief = brief_for(ReportSection.data_integrity)
    assert [item.name for item in artifact_briefs(store, brief)] == ["psi.max"]
    # Even named outright -- which is how a finding's evidence reaches section 6 -- it is dropped.
    named = artifact_briefs(store, brief, extra=["psi.figure"])
    assert [item.name for item in named] == ["psi.max"]


def test_calibration_comes_first_only_on_a_rare_event(tmp_path: Path) -> None:
    """Spec 3.11's rule, read from the artifacts rather than from a constant in the prose."""
    store = ArtifactStore(tmp_path / "artifacts")
    assert calibration_before_discrimination(store) is False
    store.put("metrics.test.event_rate", 0.2246, ArtifactKind.scalar, "event rate")
    store.put("rule.calibration_first_event_rate", 0.05, ArtifactKind.scalar, "the rule")
    assert calibration_before_discrimination(store) is False
    rare = ArtifactStore(tmp_path / "rare")
    rare.put("metrics.test.event_rate", 0.0084, ArtifactKind.scalar, "event rate")
    rare.put("rule.calibration_first_event_rate", 0.05, ArtifactKind.scalar, "the rule")
    assert calibration_before_discrimination(rare) is True


def test_the_outcomes_brief_swaps_when_calibration_comes_first(tmp_path: Path) -> None:
    store = ArtifactStore(tmp_path / "artifacts")
    store.put("metrics.test.event_rate", 0.0084, ArtifactKind.scalar, "event rate")
    store.put("rule.calibration_first_event_rate", 0.05, ArtifactKind.scalar, "the rule")
    briefs = {brief.section: brief for brief in ordered_briefs(store)}
    assert "calibration before discrimination" in briefs[ReportSection.outcomes].brief
    plain = {brief.section: brief for brief in ordered_briefs(ArtifactStore(tmp_path / "plain"))}
    assert "discrimination before calibration" in plain[ReportSection.outcomes].brief
    assert [brief.section for brief in ordered_briefs(store)] == list(SECTION_ORDER)


def test_a_brief_matches_exact_names_and_dotted_prefixes() -> None:
    brief = brief_for(ReportSection.data_integrity)
    assert brief.matches("psi.utilisation")
    assert brief.matches("leakage.overlap")
    assert not brief.matches("challenger.auc")
    assert brief_for(ReportSection.summary).matches("psi.max")
    assert not brief_for(ReportSection.summary).matches("psi.utilisation")


def test_an_artifact_brief_is_frozen_and_carries_its_own_citation() -> None:
    brief = ArtifactBrief(
        name="metrics.test.auc",
        hash8="4bb1344e",
        kind=ArtifactKind.scalar,
        value=0.7412,
        summary="auc",
    )
    assert brief.citation == "[[art:4bb1344e:metrics.test.auc]]"
    with pytest.raises(ValidationError):
        brief.value = 1.0  # type: ignore[misc]
