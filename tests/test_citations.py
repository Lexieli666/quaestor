"""Citation syntax exactly as `docs/REPORT_SCHEMA.md` section 5 fixed it in Phase 1.

Phase 1 wrote the golden report before any of this code existed, so these tests quote its real
citations: a scalar, a table cell, a JSON path, a coefficient addressed by its `feature` value, an
adjacent pair on a delta claim, a `[[reg:...]]` anchor and a `[[table:...]]` directive. If the
parser and the golden ever disagree, the golden is right.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from quaestor.artifacts import (
    ArtifactKind,
    ArtifactStore,
    Citation,
    CitationKind,
    CitationStatus,
    adjacent_pairs,
    parse_citations,
    resolve,
)
from quaestor.errors import ArtifactError
from quaestor.report.schema import is_report_citation, malformed_citations

DECILES = [
    {"decile": 1, "count": 150, "events": 74, "event_rate": 0.493, "lift": 2.24},
    {"decile": 2, "count": 150, "events": 52, "event_rate": 0.347, "lift": 1.58},
]
MODEL_SUMMARY = {
    "coefficients": [
        {"feature": "delinq_last", "value": 0.612},
        {"feature": "utilisation", "value": 0.487},
    ],
    "removed": [{"feature": "bill_last", "vif": 41.7}],
    "note": "eleven features retained",
}
FEATURES = {"n": 12, "at_origination": 2, "before_period_start": 10}


@pytest.fixture()
def store(tmp_path: Path) -> ArtifactStore:
    target = ArtifactStore(tmp_path / "artifacts")
    target.put("metrics.test.auc", 0.7412, "scalar", "test AUC")
    target.put("metrics.train.auc", 0.7538, "scalar", "train AUC")
    target.put("deciles.test", DECILES, "table", "decile separation, test split")
    target.put("run.model_summary", MODEL_SUMMARY, "json", "the subject's model summary")
    target.put("run.features", FEATURES, "json", "feature counts by timing")
    target.put("figure.calibration", b"\x89PNG", "figure", "calibration plot")
    return target


def one(text: str) -> Citation:
    (citation,) = parse_citations(text)
    return citation


# --- parsing ------------------------------------------------------------------------------------


def test_a_scalar_citation_parses() -> None:
    citation = one("test AUC 0.7412 [[art:4bb1344e:metrics.test.auc]].")
    assert citation.kind is CitationKind.art
    assert citation.hash8 == "4bb1344e"
    assert citation.name == "metrics.test.auc"
    assert citation.path is None
    assert citation.raw == "[[art:4bb1344e:metrics.test.auc]]"


def test_a_table_cell_citation_parses() -> None:
    citation = one("a lift of 2.24 [[art:20368492:deciles.test#1.lift]]")
    assert citation.name == "deciles.test"
    assert citation.path == "1.lift"


def test_a_json_path_citation_parses() -> None:
    citation = one("[[art:843f4548:run.model_summary#coefficients.utilisation.value]]")
    assert citation.path == "coefficients.utilisation.value"


def test_a_regulatory_citation_parses() -> None:
    citation = one("outcomes analysis [[reg:SR11-7:V.1.c]]")
    assert citation.kind is CitationKind.reg
    assert citation.doc == "SR11-7"
    assert citation.section_id == "V.1.c"


def test_a_table_directive_parses() -> None:
    citation = one("[[table:calibration.test]]")
    assert citation.kind is CitationKind.table
    assert citation.name == "calibration.test"


def test_citations_come_back_in_text_order() -> None:
    text = "0.7538 [[art:dd1bb63e:metrics.train.auc]] and 0.7412 [[art:4bb1344e:metrics.test.auc]]"
    assert [c.name for c in parse_citations(text)] == ["metrics.train.auc", "metrics.test.auc"]


def test_prose_without_citations_yields_none() -> None:
    assert parse_citations("Regime stability was not assessed.") == []


def test_an_unknown_scheme_is_not_a_citation() -> None:
    assert parse_citations("[[doi:10.24432/C55S3H]]") == []


def test_a_malformed_art_citation_is_an_error() -> None:
    with pytest.raises(ArtifactError, match=r"\[\[art:<hash8>:<logical_name>\]\]"):
        parse_citations("0.74 [[art:metrics.test.auc]]")


def test_a_malformed_reg_citation_is_an_error() -> None:
    with pytest.raises(ArtifactError, match=r"\[\[reg:<doc>:<section_id>\]\]"):
        parse_citations("guidance [[reg:SR11-7]]")


# --- adjacency ------------------------------------------------------------------------------------


def test_two_adjacent_citations_are_a_pair() -> None:
    text = "The gap is 0.0126 [[art:4bb1344e:metrics.test.auc]][[art:dd1bb63e:metrics.train.auc]]."
    (pair,) = adjacent_pairs(parse_citations(text))
    assert (pair[0].name, pair[1].name) == ("metrics.test.auc", "metrics.train.auc")


def test_citations_separated_by_a_space_are_not_a_pair() -> None:
    text = "0.7412 [[art:4bb1344e:metrics.test.auc]] and [[art:dd1bb63e:metrics.train.auc]]"
    assert adjacent_pairs(parse_citations(text)) == []


def test_a_reg_citation_never_pairs() -> None:
    text = "[[reg:SR11-7:V.1]][[art:4bb1344e:metrics.test.auc]]"
    assert adjacent_pairs(parse_citations(text)) == []


# --- resolution -----------------------------------------------------------------------------------


def test_a_scalar_citation_resolves_to_its_value(store: ArtifactStore) -> None:
    artifact = store.artifact("metrics.test.auc")
    resolved = resolve(one(artifact.citation()), store)
    assert resolved.is_resolved
    assert resolved.value == pytest.approx(0.7412)
    assert resolved.kind is ArtifactKind.scalar
    assert resolved.message is None


def test_a_table_cell_citation_resolves(store: ArtifactStore) -> None:
    artifact = store.artifact("deciles.test")
    resolved = resolve(one(artifact.citation("1.lift")), store)
    assert resolved.value == pytest.approx(2.24)
    assert resolved.kind is ArtifactKind.table


def test_a_json_path_citation_resolves(store: ArtifactStore) -> None:
    artifact = store.artifact("run.features")
    assert resolve(one(artifact.citation("n")), store).value == pytest.approx(12)


def test_a_list_element_is_addressed_by_its_feature_value(store: ArtifactStore) -> None:
    artifact = store.artifact("run.model_summary")
    resolved = resolve(one(artifact.citation("coefficients.utilisation.value")), store)
    assert resolved.value == pytest.approx(0.487)


def test_a_second_list_field_is_addressed_the_same_way(store: ArtifactStore) -> None:
    artifact = store.artifact("run.model_summary")
    resolved = resolve(one(artifact.citation("removed.bill_last.vif")), store)
    assert resolved.value == pytest.approx(41.7)


def test_a_table_directive_resolves_to_its_table(store: ArtifactStore) -> None:
    resolved = resolve(one("[[table:deciles.test]]"), store)
    assert resolved.is_resolved
    assert resolved.kind is ArtifactKind.table


def test_a_regulatory_citation_resolves_against_the_committed_corpus(store: ArtifactStore) -> None:
    resolved = resolve(one("[[reg:SR11-7:V.1.c]]"), store)
    assert resolved.is_resolved
    assert resolved.heading == "Outcomes Analysis"
    assert resolved.value is None


def test_the_current_guidance_resolves_too(store: ArtifactStore) -> None:
    resolved = resolve(one("[[reg:SR26-2:V.1.b]]"), store)
    assert resolved.is_resolved
    assert resolved.heading == "Outcomes Analysis"


# --- what dangles ---------------------------------------------------------------------------------


def dangling_message(text: str, store: ArtifactStore) -> str:
    """Resolve a citation that must dangle, and hold every dangling message to its contract.

    Two contracts, one per kind of token, applied here rather than in one test so that every
    dangling site in `citations.py` is covered by the site that exercises it (DECISIONS D-192).

    A token a rendered report may carry is named verbatim: the drafter has to recognise the form
    it is being asked to rewrite. A token no report may carry -- a hash too short, a stray brace, a
    `[[table:...]]` directive -- is named without its brackets, because the message is printed in
    Appendix A's repairs table and `check_structure` reads the whole report.
    """
    resolved = resolve(one(text), store)
    assert resolved.status is CitationStatus.dangling
    assert resolved.value is None
    message = resolved.message or ""
    if is_report_citation(text):
        assert text in message, "a dangling message must quote the citation as it was written"
    else:
        assert text not in message, "a diagnostic must not print a token no report may carry"
        assert text.strip("[]") in message, "it must still name the token that failed"
        assert "diagnostic" in message, "and say plainly that it is quoting one"
    assert malformed_citations(message) == [], "no message may be refused by the renderer"
    return message


def test_a_guidance_section_the_document_does_not_have_dangles(store: ArtifactStore) -> None:
    # Spec 3.7 asks for SR 11-7 "V.3"; the document has no such section (DECISIONS D-054).
    message = dangling_message("[[reg:SR11-7:V.3]]", store)
    assert "[[reg:SR11-7:V.3]]" in message
    assert "V.1.c" in message


def test_a_guidance_document_that_was_never_ingested_dangles(store: ArtifactStore) -> None:
    # `OCC2011-12` is not one of the two documents the citation grammar admits, so the token is
    # malformed as well as unresolvable and the message names it without its brackets (D-192).
    message = dangling_message("[[reg:OCC2011-12:V]]", store)
    assert "⟪reg:OCC2011-12:V⟫" in message
    assert "SR11-7" in message and "SR26-2" in message


def test_a_logical_name_not_in_the_index_dangles(store: ArtifactStore) -> None:
    message = dangling_message("[[art:4bb1344e:metrics.oot.auc]]", store)
    assert "not in the artifact index" in message


def test_a_hash8_that_is_not_a_prefix_of_the_named_artifact_dangles(store: ArtifactStore) -> None:
    message = dangling_message("[[art:deadbeef:metrics.test.auc]]", store)
    assert "is not a prefix of" in message
    assert store.entry("metrics.test.auc").hash in message


def test_a_hash8_that_is_too_short_dangles(store: ArtifactStore) -> None:
    assert "shorter than the 8" in dangling_message("[[art:4bb1:metrics.test.auc]]", store)


def test_a_malformed_token_is_quoted_so_that_the_diagnostic_can_be_printed(
    store: ArtifactStore,
) -> None:
    """DECISIONS D-192: the message is printed in Appendix A, so it may not carry the bad token.

    The three things the quoting has to do at once: keep the report renderable, still name the
    token that failed so a reader and the drafter can both find it, and say what it is doing.
    """
    message = dangling_message("[[art:4bb1:metrics.test.auc]]", store)
    assert "⟪art:4bb1:metrics.test.auc⟫" in message
    assert "[[" not in message and "]]" not in message
    assert "diagnostic about a citation and not a citation" in message
    # And the hash it should have carried, which is what the drafter is being asked to write.
    assert store.entry("metrics.test.auc").hash[:8] in message
    # A report carrying the message verbatim is renderable; one carrying the raw token is not.
    assert check_structure_would_refuse("[[art:4bb1:metrics.test.auc]]")
    assert not check_structure_would_refuse(message)


def check_structure_would_refuse(text: str) -> bool:
    """Whether the renderer's structural check would refuse a report carrying this text."""
    return bool(malformed_citations(text))


def test_a_missing_payload_file_dangles(store: ArtifactStore) -> None:
    artifact = store.artifact("metrics.test.auc")
    artifact.path.unlink()
    assert "which is not in" in dangling_message(artifact.citation(), store)


def test_a_table_cited_as_a_scalar_dangles(store: ArtifactStore) -> None:
    artifact = store.artifact("deciles.test")
    assert "add a #<path> suffix" in dangling_message(artifact.citation(), store)


def test_a_missing_row_dangles_and_lists_the_rows(store: ArtifactStore) -> None:
    artifact = store.artifact("deciles.test")
    message = dangling_message(artifact.citation("7.lift"), store)
    assert "no row of" in message
    assert "['1', '2']" in message


def test_a_missing_column_dangles_and_lists_the_columns(store: ArtifactStore) -> None:
    artifact = store.artifact("deciles.test")
    assert "has columns" in dangling_message(artifact.citation("1.slope"), store)


def test_a_cell_path_without_a_column_dangles(store: ArtifactStore) -> None:
    artifact = store.artifact("deciles.test")
    assert "#<row>.<column>" in dangling_message(artifact.citation("1"), store)


def test_a_missing_json_key_dangles_and_lists_the_keys(store: ArtifactStore) -> None:
    artifact = store.artifact("run.features")
    message = dangling_message(artifact.citation("during_period"), store)
    assert "at_origination" in message


def test_a_missing_list_element_dangles_and_lists_the_features(store: ArtifactStore) -> None:
    artifact = store.artifact("run.model_summary")
    message = dangling_message(artifact.citation("coefficients.limit_bal.value"), store)
    assert "delinq_last" in message


def test_a_list_without_a_label_field_says_so(store: ArtifactStore) -> None:
    store.put("run.plain_list", {"items": [1, 2, 3]}, "json")
    artifact = store.artifact("run.plain_list")
    message = dangling_message(artifact.citation("items.first"), store)
    assert "no feature or name field" in message


# --- the second list key, DECISIONS D-026 --------------------------------------------------------


def test_a_list_element_is_addressed_by_its_name_when_it_has_no_feature(
    store: ArtifactStore,
) -> None:
    store.put(
        "vif.by_feature",
        {"items": [{"name": "utilisation", "vif": 4.31}, {"name": "limit_bal", "vif": 2.02}]},
        "json",
        "variance inflation by feature",
    )
    artifact = store.artifact("vif.by_feature")
    assert resolve(one(artifact.citation("items.utilisation.vif")), store).value == pytest.approx(
        4.31
    )


def test_feature_is_tried_before_name(store: ArtifactStore) -> None:
    store.put(
        "run.both_labels",
        {"items": [{"feature": "a", "name": "b", "value": 1.0}]},
        "json",
    )
    artifact = store.artifact("run.both_labels")
    assert resolve(one(artifact.citation("items.a.value")), store).value == pytest.approx(1.0)
    message = dangling_message(artifact.citation("items.b.value"), store)
    assert "feature or name == 'b'" in message


def test_a_path_walking_into_a_scalar_dangles(store: ArtifactStore) -> None:
    artifact = store.artifact("run.features")
    assert "no addressable parts" in dangling_message(artifact.citation("n.deeper"), store)


def test_a_path_on_a_figure_dangles(store: ArtifactStore) -> None:
    artifact = store.artifact("figure.calibration")
    message = dangling_message(artifact.citation("1.lift"), store)
    assert "which has no addressable parts" in message


def test_a_non_numeric_path_dangles(store: ArtifactStore) -> None:
    artifact = store.artifact("run.model_summary")
    message = dangling_message(artifact.citation("note"), store)
    assert "is not a number" in message


def test_a_table_directive_naming_a_scalar_dangles(store: ArtifactStore) -> None:
    message = dangling_message("[[table:metrics.test.auc]]", store)
    assert "only a table can be expanded" in message


def test_a_table_directive_naming_nothing_dangles(store: ArtifactStore) -> None:
    assert "not in the artifact index" in dangling_message("[[table:calibration.test]]", store)


def test_a_boolean_path_is_not_a_number(store: ArtifactStore) -> None:
    store.put("run.flags", {"clean": True}, "json")
    assert "is not a number" in dangling_message(
        store.artifact("run.flags").citation("clean"), store
    )


def test_a_null_path_is_not_a_number(store: ArtifactStore) -> None:
    store.put("run.optional", {"baseline_hazard": None}, "json")
    artifact = store.artifact("run.optional")
    assert "is not a number" in dangling_message(artifact.citation("baseline_hazard"), store)
