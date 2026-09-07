"""The committed regulatory corpus: the spans a ``[[reg:...]]`` citation resolves against.

Spec section 3.8. Two documents are ingested, and the choice of which two is DECISIONS D-055:
``SR11-7`` (April 4, 2011, superseded on April 17, 2026) is kept so that a historical citation
still resolves, and ``SR26-2`` (the interagency revision, the same text as OCC Bulletin 2026-13)
is the current guidance the drafter cites by default from Phase 8. OCC Bulletin 2011-12 is not
ingested: it carried the same text as SR 11-7 and was rescinded by OCC 2026-13, so a second copy
of a superseded document would only give the retriever two ways to say the same thing.

The corpus is data, not code: :mod:`quaestor.corpus.ingest` writes ``sr11-7.jsonl``,
``sr26-2.jsonl`` and ``SOURCES.json`` next to this module once, by hand, from PDFs that are never
committed, and everything at runtime reads only those three files. Loading is cached because the
whole corpus is 37 sections of public text and every retrieval, citation resolution and report
section would otherwise re-read it.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator
from functools import cache
from pathlib import Path
from typing import Any, Final

from pydantic import BaseModel, ConfigDict

from ..errors import CorpusError

__all__ = [
    "CORPUS_FILES",
    "RegulatoryCorpus",
    "SOURCES_FILE",
    "Source",
    "Span",
    "corpus_root",
    "load_corpus",
]

SOURCES_FILE: Final = "SOURCES.json"
"""Where the provenance of each ingested document lives, next to the JSONL files."""

CORPUS_FILES: Final = {"SR11-7": "sr11-7.jsonl", "SR26-2": "sr26-2.jsonl"}
"""Document id to the file its sections are committed in, in citation order."""


class Span(BaseModel):
    """One section of one guidance document, as ingested.

    Attributes:
        doc: The document id a citation names, ``SR11-7`` or ``SR26-2``.
        section_id: The section id a citation names, such as ``V.1.c``. Quaestor's own
            identifiers, taken from the outline file, not from the document's own numbering.
        heading: The heading exactly as the document writes it.
        text: The section's body, page markers removed, one paragraph per line.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    doc: str
    section_id: str
    heading: str
    text: str

    @property
    def citation(self) -> str:
        """The ``[[reg:...]]`` citation that resolves to this span."""
        return f"[[reg:{self.doc}:{self.section_id}]]"


class Source(BaseModel):
    """Where one ingested document came from and what state it is in.

    Attributes:
        document: The document id, matching :attr:`Span.doc`.
        title: The document's own title.
        issued: The date the document was issued, ``YYYY-MM-DD``.
        status: ``current``, or ``superseded by <doc> on <date>``.
        source_url: The public URL the PDF was downloaded from.
        pdf_sha256: The ``sha256`` of the PDF that was ingested, which is not committed.
        pages: How many pages that PDF had.
        sections: How many sections were written to the JSONL.
        outline_sha256: The ``sha256`` of the outline file the text was split by.
        ingested: The date the ingest was run, ``YYYY-MM-DD``.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    document: str
    title: str
    issued: str
    status: str
    source_url: str
    pdf_sha256: str
    pages: int
    sections: int
    outline_sha256: str
    ingested: str


class RegulatoryCorpus:
    """Every ingested span, addressable by document and section id.

    Attributes:
        spans: The spans, in document order and then in outline order.
        sources: The provenance of each document, keyed by document id.
    """

    def __init__(self, spans: Iterable[Span], sources: Iterable[Source] = ()) -> None:
        """Build a corpus over some spans.

        Args:
            spans: The spans, in the order they should be listed.
            sources: The provenance records, one per document.

        Raises:
            CorpusError: Two spans share a document and a section id, which would make a citation
                ambiguous.
        """
        self.spans: list[Span] = list(spans)
        self.sources: dict[str, Source] = {source.document: source for source in sources}
        self._by_id: dict[tuple[str, str], Span] = {}
        for span in self.spans:
            key = (span.doc, span.section_id)
            if key in self._by_id:
                raise CorpusError(
                    f"the corpus holds two sections {span.section_id!r} of {span.doc}; a "
                    f"[[reg:{span.doc}:{span.section_id}]] citation would be ambiguous"
                )
            self._by_id[key] = span

    def __len__(self) -> int:
        """How many spans the corpus holds."""
        return len(self.spans)

    def __iter__(self) -> Iterator[Span]:
        """Yield every span, in corpus order."""
        return iter(self.spans)

    def documents(self) -> list[str]:
        """Return the document ids present, in corpus order."""
        seen: list[str] = []
        for span in self.spans:
            if span.doc not in seen:
                seen.append(span.doc)
        return seen

    def sections(self, doc: str) -> list[Span]:
        """Return one document's spans, in outline order.

        Args:
            doc: The document id.

        Returns:
            Its spans, or an empty list when the document is not in the corpus.
        """
        return [span for span in self.spans if span.doc == doc]

    def get(self, doc: str, section_id: str) -> Span | None:
        """Return one span, or ``None`` when nothing of that name is in the corpus.

        Args:
            doc: The document id.
            section_id: The section id.

        Returns:
            The span, or ``None``.
        """
        return self._by_id.get((doc, section_id))

    def section_ids(self, doc: str) -> list[str]:
        """Return one document's section ids, in outline order.

        Args:
            doc: The document id.

        Returns:
            Its section ids.
        """
        return [span.section_id for span in self.sections(doc)]

    def subset(self, docs: Iterable[str] | None) -> RegulatoryCorpus:
        """Return the corpus restricted to some documents.

        Args:
            docs: The document ids to keep, or ``None`` for all of them.

        Returns:
            A corpus over the kept spans. The sources travel with them.

        Raises:
            CorpusError: A named document is not in the corpus; the message lists the ones that
                are, because a retrieval restricted to a document that was never ingested would
                otherwise return nothing and look like a document with nothing to say.
        """
        if docs is None:
            return self
        wanted = list(docs)
        unknown = [doc for doc in wanted if doc not in self.documents()]
        if unknown:
            raise CorpusError(
                f"the corpus holds no document {unknown}; it holds {self.documents()}"
            )
        kept = [span for span in self.spans if span.doc in wanted]
        return RegulatoryCorpus(kept, [self.sources[doc] for doc in wanted if doc in self.sources])


def corpus_root() -> Path:
    """Return the directory the committed JSONL files live in."""
    return Path(__file__).resolve().parent


def _read_jsonl(path: Path, doc: str) -> list[Span]:
    """Read one document's JSONL into spans, naming the line that fails."""
    spans: list[Span] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload: Any = json.loads(line)
            spans.append(Span.model_validate(payload))
        except Exception as exc:  # noqa: BLE001 - the message must name the line
            raise CorpusError(
                f"{path.name} line {number} is not a corpus span: {exc}",
                fix=f"python -m quaestor.corpus.ingest --sr117 PDF --sr262 PDF to rebuild {doc}",
            ) from exc
    return spans


def _load(root: Path) -> RegulatoryCorpus:
    """Read every committed document under ``root``."""
    spans: list[Span] = []
    for doc, file_name in CORPUS_FILES.items():
        path = root / file_name
        if not path.is_file():
            raise CorpusError(
                f"the regulatory corpus is missing {path}; {doc} was never ingested",
                fix="python -m quaestor.corpus.ingest --sr117 PDF --sr262 PDF",
            )
        spans += _read_jsonl(path, doc)
    sources_path = root / SOURCES_FILE
    sources: list[Source] = []
    if sources_path.is_file():
        raw: Any = json.loads(sources_path.read_text(encoding="utf-8"))
        sources = [Source.model_validate(entry) for entry in raw["documents"]]
    return RegulatoryCorpus(spans, sources)


@cache
def _load_cached(root: str) -> RegulatoryCorpus:
    """Cache one root's corpus; the key is a string so that it hashes."""
    return _load(Path(root))


def load_corpus(root: Path | str | None = None) -> RegulatoryCorpus:
    """Load the committed corpus.

    Args:
        root: The directory holding the JSONL files. Defaults to the package's own, which is what
            every caller other than a test uses.

    Returns:
        The corpus. The result is cached per root: the files are committed and do not change
        under a running process.

    Raises:
        CorpusError: A document's JSONL is missing or malformed.
    """
    return _load_cached(str(corpus_root() if root is None else Path(root)))
