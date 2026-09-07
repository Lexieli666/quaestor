"""BM25 by hand: the tokenizer, the arithmetic, and retrieval over the committed corpus.

The ranking of the three-document toy corpus is computed longhand in the test itself, digit by
digit, so that a change to `k1`, to `b`, to the idf smoothing or to the length normalisation
fails here with the number it produced rather than somewhere downstream with a different report.
"""

from __future__ import annotations

import math

import pytest

from quaestor.corpus import K1, B, BM25Index, load_corpus, retrieve, scored_payload, tokenize
from quaestor.errors import CorpusError

# --- the toy corpus, and its ranking computed by hand ---------------------------------------------

TOY = [
    "the model risk",
    "model model validation",
    "outcomes analysis of the model",
]

# tokens:      D1 [the, model, risk]                       len 3
#              D2 [model, model, validation]               len 3
#              D3 [outcomes, analysis, of, the, model]     len 5
# N = 3, avgdl = (3 + 3 + 5) / 3 = 11/3 = 3.666667
#
# idf(t) = ln((N - df + 0.5) / (df + 0.5) + 1)
#   model:      df 3 -> ln(0.5 / 3.5 + 1) = ln(1.14285714) = 0.13353139
#   validation: df 1 -> ln(2.5 / 1.5 + 1) = ln(2.66666667) = 0.98082925
#
# norm(d) = k1 * (1 - b + b * len(d) / avgdl), with k1 = 1.5 and b = 0.75
#   D1, D2: 1.5 * (0.25 + 0.75 * 3 / 3.666667) = 1.5 * 0.86363636 = 1.29545455
#   D3:     1.5 * (0.25 + 0.75 * 5 / 3.666667) = 1.5 * 1.27272727 = 1.90909091
#
# score(q, d) = sum over t of idf(t) * f(t,d) * (k1 + 1) / (f(t,d) + norm(d))
# for the query "model validation":
#   D1: 0.13353139 * 1 * 2.5 / (1 + 1.29545455) = 0.33382848 / 2.29545455 = 0.14543023
#   D2: 0.13353139 * 2 * 2.5 / (2 + 1.29545455) = 0.66765696 / 3.29545455 = 0.20259935
#     + 0.98082925 * 1 * 2.5 / (1 + 1.29545455) = 2.45207313 / 2.29545455 = 1.06822988
#     = 1.27082923
#   D3: 0.13353139 * 1 * 2.5 / (1 + 1.90909091) = 0.33382848 / 2.90909091 = 0.11475354
#
# so the ranking is D2, D1, D3.
HAND_COMPUTED = [0.14543023, 1.27082923, 0.11475354]


@pytest.fixture
def toy() -> BM25Index:
    """The three-document toy corpus, tokenized."""
    return BM25Index(tokenize(text) for text in TOY)


def test_the_parameters_are_the_ones_the_spec_fixes() -> None:
    assert (K1, B) == (1.5, 0.75)


def test_the_tokenizer_lowercases_and_splits_on_non_alphanumerics() -> None:
    assert tokenize("Outcomes Analysis, §V.1.c -- 'back-testing' (2011)") == [
        "outcomes",
        "analysis",
        "v",
        "1",
        "c",
        "back",
        "testing",
        "2011",
    ]
    assert tokenize("   ") == []


def test_the_tokenizer_does_not_stem_and_keeps_every_word() -> None:
    # No stemming: "models" and "model" are different terms. No stop-words: "the" is a term.
    assert tokenize("The models model") == ["the", "models", "model"]


def test_the_index_counts_lengths_and_document_frequencies(toy: BM25Index) -> None:
    assert len(toy) == 3
    assert toy.average_length == pytest.approx(11 / 3)
    assert toy.document_frequency("model") == 3
    assert toy.document_frequency("validation") == 1
    assert toy.document_frequency("absent") == 0


def test_the_idf_of_a_term_in_every_document_is_small_but_positive(toy: BM25Index) -> None:
    assert toy.idf("model") == pytest.approx(math.log(1 + 0.5 / 3.5), abs=1e-9)
    assert toy.idf("model") > 0
    assert toy.idf("validation") == pytest.approx(math.log(1 + 2.5 / 1.5), abs=1e-9)


def test_the_scores_are_the_hand_computed_ones(toy: BM25Index) -> None:
    assert toy.scores("model validation") == pytest.approx(HAND_COMPUTED, abs=5e-8)


def test_the_ranking_is_the_hand_computed_one(toy: BM25Index) -> None:
    ranked = toy.rank("model validation")
    assert [index for index, _ in ranked] == [1, 0, 2]
    assert ranked[0][1] == pytest.approx(1.27082923, abs=5e-8)


def test_k_truncates_the_ranking(toy: BM25Index) -> None:
    assert [index for index, _ in toy.rank("model validation", 2)] == [1, 0]


def test_a_document_sharing_no_term_with_the_query_is_not_returned(toy: BM25Index) -> None:
    ranked = toy.rank("validation")
    assert [index for index, _ in ranked] == [1]


def test_a_query_with_no_term_in_the_corpus_returns_nothing(toy: BM25Index) -> None:
    assert toy.rank("prepayment convexity") == []


def test_a_repeated_query_term_counts_twice(toy: BM25Index) -> None:
    once = toy.score("model", 0)
    assert toy.score("model model", 0) == pytest.approx(2 * once)


def test_an_empty_index_has_no_average_length() -> None:
    empty = BM25Index([])
    assert len(empty) == 0
    assert empty.average_length == 0.0
    assert empty.rank("anything") == []


def test_tokens_may_be_passed_instead_of_text(toy: BM25Index) -> None:
    assert toy.scores(["model", "validation"]) == pytest.approx(toy.scores("model validation"))


# --- retrieval over the committed corpus ----------------------------------------------------------


def test_the_acceptance_query_returns_both_outcomes_analysis_sections() -> None:
    # Spec 3.7's acceptance criterion, with D-054's correction: SR 11-7 numbers outcomes analysis
    # V.1.c, not the V.3 the spec's sentence names, and SR 26-2 renumbers it V.1.b.
    spans = retrieve("outcomes analysis")
    assert len(spans) == 3
    found = {(span.doc, span.section_id) for span in spans}
    assert ("SR11-7", "V.1.c") in found
    assert ("SR26-2", "V.1.b") in found


def test_retrieval_is_ordered_by_descending_score() -> None:
    scores = [span.score for span in retrieve("outcomes analysis")]
    assert scores == sorted(scores, reverse=True)
    assert all(score > 0 for score in scores)


def test_a_span_carries_its_heading_its_text_and_its_citation() -> None:
    best = retrieve("outcomes analysis")[0]
    assert best.heading == "Outcomes Analysis"
    assert best.text
    assert best.citation == f"[[reg:{best.doc}:{best.section_id}]]"


def test_the_search_can_be_restricted_to_the_current_guidance() -> None:
    spans = retrieve("outcomes analysis", 3, ["SR26-2"])
    assert {span.doc for span in spans} == {"SR26-2"}
    assert spans[0].section_id == "V.1.b"


def test_the_search_can_be_restricted_to_the_superseded_guidance() -> None:
    spans = retrieve("outcomes analysis", 1, ["SR11-7"])
    assert [(span.doc, span.section_id) for span in spans] == [("SR11-7", "V.1.c")]


def test_k_limits_how_many_spans_come_back() -> None:
    assert len(retrieve("model validation", 1)) == 1
    assert len(retrieve("model validation", 7)) == 7


def test_restricting_to_a_document_that_was_never_ingested_is_an_error() -> None:
    with pytest.raises(CorpusError, match="OCC2011-12"):
        retrieve("outcomes analysis", 3, ["OCC2011-12"])


def test_a_query_the_guidance_never_discusses_retrieves_nothing() -> None:
    assert retrieve("prepayment burnout convexity") == []


def test_the_heading_is_scored_with_the_body() -> None:
    # "Internal Audit" is a heading whose section does not repeat the phrase often; a retriever
    # that scored the body alone would not put it first.
    assert retrieve("internal audit", 1, ["SR11-7"])[0].section_id == "VI.4"


def test_a_retrieval_can_be_run_against_a_corpus_passed_in() -> None:
    corpus = load_corpus().subset(["SR26-2"])
    spans = retrieve("documentation", 2, corpus=corpus)
    assert {span.doc for span in spans} == {"SR26-2"}


def test_the_stored_payload_rounds_the_score_so_two_runs_hash_alike() -> None:
    payload = scored_payload(retrieve("outcomes analysis", 2))
    assert [set(row) for row in payload] == [{"doc", "section_id", "heading", "text", "score"}] * 2
    for row in payload:
        assert isinstance(row["score"], float)
        assert row["score"] == round(float(row["score"]), 6)
