"""The regulatory corpus: two guidance documents, a hand-written BM25, and what ``[[reg:]]`` means.

Filled in Phase 6 from spec section 3.8. The corpus holds **SR 11-7** (April 4, 2011, superseded)
and **SR 26-2** (April 17, 2026, current; the same text as OCC Bulletin 2026-13), and it holds
them because a validation report that anchors a section to the guidance has to anchor it to text a
reader can find. OCC Bulletin 2011-12 is deliberately not ingested (DECISIONS D-055).

Three files next to this one are the corpus: ``sr11-7.jsonl``, ``sr26-2.jsonl`` and
``SOURCES.json``. :mod:`quaestor.corpus.ingest` writes them once, by hand, from PDFs that are
never committed; :mod:`quaestor.corpus.documents` reads them; :mod:`quaestor.corpus.bm25` ranks
them. Nothing at runtime opens a PDF, and ``pypdf`` is a development dependency imported inside
one function of the ingest script.
"""

from __future__ import annotations

from .bm25 import K1, B, BM25Index, ScoredSpan, retrieve, scored_payload, tokenize
from .documents import (
    CORPUS_FILES,
    SOURCES_FILE,
    RegulatoryCorpus,
    Source,
    Span,
    corpus_root,
    load_corpus,
)

__all__ = [
    "B",
    "BM25Index",
    "CORPUS_FILES",
    "K1",
    "RegulatoryCorpus",
    "SOURCES_FILE",
    "ScoredSpan",
    "Source",
    "Span",
    "corpus_root",
    "load_corpus",
    "retrieve",
    "scored_payload",
    "tokenize",
]
