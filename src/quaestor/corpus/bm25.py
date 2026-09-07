"""BM25 over the regulatory corpus, written by hand.

Spec section 3.8 fixes the parameters: ``k1 = 1.5``, ``b = 0.75``, a tokenizer that lowercases and
splits on runs of non-alphanumeric characters, no stemming and no stop-word list. The scoring
function is the Robertson/Sparck Jones form with the ``+0.5`` smoothing, which is what "BM25"
without qualification means:

.. code-block:: text

    idf(t)      = ln( (N - df(t) + 0.5) / (df(t) + 0.5) + 1 )
    score(q, d) = sum over t in q of  idf(t) * f(t, d) * (k1 + 1)
                                      / ( f(t, d) + k1 * (1 - b + b * |d| / avgdl) )

The ``+ 1`` inside the logarithm is what keeps the idf of a term that appears in every document at
a small positive number rather than at zero or below; without it a single-term query over a corpus
where every section mentions "model" would score every section identically at zero and the ranking
would be the corpus order. That choice is the one place this implementation has to take a side,
and it is recorded in DECISIONS D-057.

There is no index on disk and no inverted index in memory: the corpus is 37 sections of a few
thousand words each, so a linear pass over term frequencies costs less than a millisecond and
saves a persistence format nobody would read. A hand-written scorer is also the only kind whose
arithmetic a test can check longhand, which ``tests/test_bm25.py`` does on a three-document toy
corpus.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from typing import Final

from pydantic import BaseModel, ConfigDict

from .documents import RegulatoryCorpus, Span, load_corpus

__all__ = [
    "B",
    "BM25Index",
    "K1",
    "ScoredSpan",
    "retrieve",
    "scored_payload",
    "tokenize",
]

K1: Final = 1.5
"""Term-frequency saturation. Spec section 3.8."""

B: Final = 0.75
"""Length normalisation. Spec section 3.8."""

_TOKEN_SPLIT: Final = re.compile(r"[^0-9a-z]+")
"""Runs of non-alphanumeric characters, applied after lowercasing."""


def tokenize(text: str) -> list[str]:
    """Split text into BM25 terms: lowercase, split on non-alphanumerics, keep everything else.

    Args:
        text: Any string -- a query, a heading, a section body.

    Returns:
        The tokens, in order, with empty strings dropped. No stemming and no stop-word removal:
        both would have to be tuned against a corpus of two documents, and "model" carrying almost
        no information is something the idf already says.
    """
    return [token for token in _TOKEN_SPLIT.split(text.lower()) if token]


class BM25Index:
    """A BM25 scorer over a fixed list of documents.

    Attributes:
        documents: The tokenized documents, in the order they were given.
        average_length: The mean document length in tokens; ``0.0`` for an empty index.
    """

    def __init__(self, documents: Iterable[Sequence[str]], *, k1: float = K1, b: float = B) -> None:
        """Build the index by counting term frequencies once.

        Args:
            documents: One token sequence per document.
            k1: Term-frequency saturation.
            b: Length normalisation.
        """
        self.documents: list[list[str]] = [list(tokens) for tokens in documents]
        self.k1 = k1
        self.b = b
        self._frequencies: list[Counter[str]] = [Counter(tokens) for tokens in self.documents]
        self._lengths: list[int] = [len(tokens) for tokens in self.documents]
        total = sum(self._lengths)
        self.average_length: float = total / len(self.documents) if self.documents else 0.0
        self._document_frequency: Counter[str] = Counter()
        for frequencies in self._frequencies:
            self._document_frequency.update(frequencies.keys())

    def __len__(self) -> int:
        """How many documents the index holds."""
        return len(self.documents)

    def document_frequency(self, term: str) -> int:
        """How many documents contain a term.

        Args:
            term: A token, already lowercased.

        Returns:
            The document frequency.
        """
        return self._document_frequency[term]

    def idf(self, term: str) -> float:
        """Return a term's inverse document frequency.

        Args:
            term: A token, already lowercased.

        Returns:
            ``ln((N - df + 0.5) / (df + 0.5) + 1)``, which is positive for every term including
            one that appears in every document.
        """
        n = len(self.documents)
        df = self._document_frequency[term]
        return math.log((n - df + 0.5) / (df + 0.5) + 1.0)

    def score(self, query: str | Sequence[str], index: int) -> float:
        """Score one document against a query.

        Args:
            query: The query, as text or as tokens.
            index: Which document to score.

        Returns:
            The BM25 score. Repeated query terms count once each time they are repeated, which is
            what the sum over query terms means.
        """
        terms = tokenize(query) if isinstance(query, str) else list(query)
        frequencies = self._frequencies[index]
        length = self._lengths[index]
        norm = self.k1 * (1.0 - self.b + self.b * (length / self.average_length))
        total = 0.0
        for term in terms:
            frequency = frequencies[term]
            if frequency == 0:
                continue
            total += self.idf(term) * frequency * (self.k1 + 1.0) / (frequency + norm)
        return total

    def scores(self, query: str | Sequence[str]) -> list[float]:
        """Score every document against a query, in index order.

        Args:
            query: The query, as text or as tokens.

        Returns:
            One score per document.
        """
        terms = tokenize(query) if isinstance(query, str) else list(query)
        return [self.score(terms, index) for index in range(len(self.documents))]

    def rank(self, query: str | Sequence[str], k: int | None = None) -> list[tuple[int, float]]:
        """Rank the documents by score, best first.

        Args:
            query: The query, as text or as tokens.
            k: How many to return; ``None`` for all of them.

        Returns:
            ``(index, score)`` pairs, sorted by descending score and then by ascending index, so
            that a tie is broken by corpus order rather than by whatever ``sort`` happened to do.
            Documents scoring zero are dropped: a section that shares no term with the query is
            not a retrieval result, it is the absence of one.
        """
        ranked = [(index, score) for index, score in enumerate(self.scores(query)) if score > 0.0]
        ranked.sort(key=lambda pair: (-pair[1], pair[0]))
        return ranked if k is None else ranked[:k]


class ScoredSpan(BaseModel):
    """One retrieved span and what it scored.

    Attributes:
        doc: The document id.
        section_id: The section id, as a ``[[reg:...]]`` citation names it.
        heading: The heading as the document writes it.
        text: The section body.
        score: Its BM25 score against the query.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    doc: str
    section_id: str
    heading: str
    text: str
    score: float

    @property
    def citation(self) -> str:
        """The ``[[reg:...]]`` citation that resolves to this span."""
        return f"[[reg:{self.doc}:{self.section_id}]]"


def _span_tokens(span: Span) -> list[str]:
    """Tokenize one span: its heading and then its body.

    The heading is part of the scored text on purpose. "Outcomes Analysis" is a heading and not a
    phrase the section's prose repeats, so a retriever that scored the body alone would rank the
    section that discusses outcomes analysis in passing above the one named after it.
    """
    return tokenize(f"{span.heading}\n{span.text}")


def retrieve(
    query: str,
    k: int = 3,
    docs: Sequence[str] | None = None,
    *,
    corpus: RegulatoryCorpus | None = None,
) -> list[ScoredSpan]:
    """Retrieve the sections of the regulatory corpus that best match a query.

    Args:
        query: What to look for, in plain words.
        k: How many spans to return, at most.
        docs: Restrict the search to these document ids; ``None`` searches both.
        corpus: The corpus to search. Defaults to the committed one.

    Returns:
        The best-scoring spans, best first, at most ``k`` of them, each carrying its score. A span
        that shares no term with the query is never returned, so a query about something the
        guidance does not discuss returns fewer than ``k`` results, or none.

    Raises:
        CorpusError: ``docs`` names a document that was never ingested, or the committed corpus is
            missing or malformed.
    """
    searched = (corpus or load_corpus()).subset(docs)
    spans = list(searched)
    index = BM25Index(_span_tokens(span) for span in spans)
    return [
        ScoredSpan(
            doc=spans[position].doc,
            section_id=spans[position].section_id,
            heading=spans[position].heading,
            text=spans[position].text,
            score=score,
        )
        for position, score in index.rank(query, k)
    ]


def scored_payload(spans: Iterable[ScoredSpan]) -> list[Mapping[str, object]]:
    """Render retrieved spans as the JSON payload an artifact stores.

    Args:
        spans: The retrieved spans.

    Returns:
        One mapping per span, with the score rounded to six decimals so that two runs of the same
        query hash identically whatever the last bit of the arithmetic did.
    """
    return [
        {
            "doc": span.doc,
            "section_id": span.section_id,
            "heading": span.heading,
            "text": span.text,
            "score": round(span.score, 6),
        }
        for span in spans
    ]
