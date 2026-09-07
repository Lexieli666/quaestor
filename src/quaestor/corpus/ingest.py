"""``python -m quaestor.corpus.ingest``: turn two guidance PDFs into the committed corpus.

Spec section 3.8. This module is a **dev-time script**, run by a human once per document revision:

.. code-block:: console

    $ python -m quaestor.corpus.ingest --sr117 ~/sr1107a1.pdf --sr262 ~/sr2602a1.pdf

It reads the PDFs the human downloaded (``data/README.md`` says from where), extracts their text
with ``pypdf``, splits each document by the section outline in ``data/regulatory/``, and writes
``sr11-7.jsonl``, ``sr26-2.jsonl`` and ``SOURCES.json`` next to :mod:`quaestor.corpus.documents`.
The JSONL files are committed -- both documents are public U.S. government works -- and the PDFs
never are.

``pypdf`` is imported **inside** :func:`extract_pages` and nowhere else, so it is a development
dependency that no runtime code path and no test import reaches. Everything downstream of the
ingest reads the committed JSONL, which is why a validation run has no PDF parser in it at all.

Splitting is deliberately literal. A heading matches a line of the extracted text when the line,
with its whitespace collapsed and an optional ``I.``/``1.``/``a.`` label removed, equals the
outline's heading case-insensitively; the search for each heading starts after the previous one,
so the outline's order is the document's order and the table of contents (whose entries carry a
``, page 9`` suffix) cannot be mistaken for the body. A heading the outline names and the text
does not have is a :class:`~quaestor.errors.CorpusError` naming it: the outline is a claim about
the document, and a claim about a regulatory document that the document does not support is the
one thing this project cannot ship (DECISIONS D-056).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Sequence
from datetime import date
from pathlib import Path
from typing import Any, Final

import yaml
from pydantic import BaseModel, ConfigDict

from ..errors import CorpusError
from ..hashing import sha256_file
from .documents import CORPUS_FILES, SOURCES_FILE, Source, Span, corpus_root

__all__ = [
    "OUTLINE_FILES",
    "Outline",
    "OutlineSection",
    "extract_pages",
    "ingest",
    "ingest_document",
    "load_outline",
    "main",
    "outline_dir",
    "split_sections",
]

OUTLINE_FILES: Final = {"SR11-7": "sr11-7-outline.yaml", "SR26-2": "sr26-2-outline.yaml"}
"""Document id to the outline file its sections are named in."""

_LABEL: Final = re.compile(r"^(?:[IVXLCDM]+|[0-9]+|[a-z])[.)]\s+")
"""A leading section label on a heading line: ``V.``, ``1.``, ``a.``. Removed before comparing."""

_PAGE_MARKER: Final = re.compile(r"^(?:Page\s+)?[0-9]+$")
"""A line that is only a page number. Both documents put one on every page."""


class OutlineSection(BaseModel):
    """One entry of a section outline.

    Attributes:
        section_id: Quaestor's identifier for the section, as a ``[[reg:...]]`` citation names it.
        heading: The heading as the document writes it; the ingest matches on this.
        parent: The enclosing section's id, or ``None`` for a top-level section. Recorded for a
            reader of the outline; the ingest does not use it, because the document's own order
            already says what encloses what.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    section_id: str
    heading: str
    parent: str | None = None


class Outline(BaseModel):
    """A section outline: what the ingest expects to find in a document, and in what order.

    Attributes:
        document: The document id, which must match the one being ingested.
        title: The document's own title.
        issued: The date it was issued.
        source_url: The public URL its PDF is downloaded from.
        sections: Its sections, in document order.
        supersedes: The documents it replaced, if any.
        superseded_by: The document that replaced it, if any.
        superseded_on: The date it was superseded, if it was.
        same_text_as: A note naming another issuance carrying the same text, if one does.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    document: str
    title: str
    issued: date
    source_url: str
    sections: list[OutlineSection]
    supersedes: list[str] = []
    superseded_by: str | None = None
    superseded_on: date | None = None
    same_text_as: str | None = None

    @property
    def status(self) -> str:
        """``current``, or ``superseded by <doc> on <date>``, as ``SOURCES.json`` records it."""
        if self.superseded_by is None or self.superseded_on is None:
            return "current"
        return f"superseded by {self.superseded_by} on {self.superseded_on.isoformat()}"


def outline_dir() -> Path:
    """Return the repository's ``data/regulatory/`` directory, where the outlines live.

    Returns:
        The directory. This works from a source checkout, which is the only place the ingest is
        ever run: an installed wheel ships no ``data/`` and needs none, because it ships the
        already-ingested JSONL.
    """
    return Path(__file__).resolve().parents[3] / "data" / "regulatory"


def load_outline(path: Path, expected_document: str | None = None) -> Outline:
    """Read one outline file.

    Args:
        path: The YAML file.
        expected_document: The document id it must declare, or ``None`` to accept whatever it
            declares.

    Returns:
        The parsed outline.

    Raises:
        CorpusError: The file is missing, is not valid YAML, declares a field the model does not
            know, or names a different document than expected.
    """
    if not path.is_file():
        raise CorpusError(f"there is no section outline at {path}")
    try:
        payload: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
        outline = Outline.model_validate(payload)
    except Exception as exc:  # noqa: BLE001 - the message must name the file
        raise CorpusError(f"{path.name} is not a section outline: {exc}") from exc
    if expected_document is not None and outline.document != expected_document:
        raise CorpusError(
            f"{path.name} declares document {outline.document!r}, but it is being used to ingest "
            f"{expected_document!r}"
        )
    return outline


def extract_pages(pdf: Path) -> list[str]:
    """Extract the text of every page of a PDF.

    This is the only function in Quaestor that imports ``pypdf``, and it is never called from a
    test or from a validation run.

    Args:
        pdf: The PDF to read.

    Returns:
        One string per page, in page order.

    Raises:
        CorpusError: The file is missing, or ``pypdf`` is not installed.
    """
    if not pdf.is_file():
        raise CorpusError(f"there is no PDF at {pdf}")
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - pypdf is a declared dev dependency
        raise CorpusError(
            "the corpus ingest needs pypdf, which is a development dependency and is not "
            "imported anywhere else",
            fix="pip install -e '.[dev]'",
        ) from exc
    reader = PdfReader(str(pdf))
    return [page.extract_text() or "" for page in reader.pages]


def _normalise(line: str) -> str:
    """Collapse a line's whitespace, so that a heading is compared on its words alone."""
    return " ".join(line.split())


def _matches(line: str, heading: str) -> bool:
    """Whether a line of extracted text is this heading.

    The line must *be* the heading, not contain it: a table-of-contents entry reads
    ``V. Model Validation, page 9`` and a body heading reads ``V. MODEL VALIDATION``, and only the
    second one is where the section starts.
    """
    return _LABEL.sub("", _normalise(line)).casefold() == _normalise(heading).casefold()


def split_sections(text: str, outline: Outline) -> list[Span]:
    """Split a document's extracted text into one span per outline section.

    Args:
        text: The whole document's text, pages joined by newlines.
        outline: The sections to find, in document order.

    Returns:
        One span per outline section, in outline order. Everything before the first heading -- the
        cover page and the table of contents -- is discarded, and so is every page-number line.

    Raises:
        CorpusError: A heading the outline names is not in the text at or after the previous
            heading. The message names the heading, the section id and the document.
    """
    lines = text.splitlines()
    starts: list[int] = []
    cursor = 0
    for section in outline.sections:
        found = next(
            (i for i in range(cursor, len(lines)) if _matches(lines[i], section.heading)),
            None,
        )
        if found is None:
            raise CorpusError(
                f"{outline.document} section {section.section_id} is headed "
                f"{section.heading!r} in the outline, and no line of the extracted text after "
                f"line {cursor} is that heading",
                fix=(
                    f"correct the heading in {OUTLINE_FILES.get(outline.document, 'the outline')} "
                    "to the document's own wording; never force the text to the outline"
                ),
            )
        starts.append(found)
        cursor = found + 1

    spans: list[Span] = []
    for position, section in enumerate(outline.sections):
        first = starts[position] + 1
        last = starts[position + 1] if position + 1 < len(starts) else len(lines)
        body = [
            _normalise(line)
            for line in lines[first:last]
            if _normalise(line) and not _PAGE_MARKER.match(_normalise(line))
        ]
        spans.append(
            Span(
                doc=outline.document,
                section_id=section.section_id,
                heading=section.heading,
                text="\n".join(body),
            )
        )
    return spans


def _write_jsonl(path: Path, spans: Sequence[Span]) -> None:
    """Write one span per line, keys sorted, so that two ingests of one PDF are byte-identical."""
    lines = [
        json.dumps(span.model_dump(mode="json"), sort_keys=True, ensure_ascii=False)
        for span in spans
    ]
    path.write_text("".join(f"{line}\n" for line in lines), encoding="utf-8")


def ingest_document(
    document: str,
    pdf: Path,
    out: Path,
    *,
    outlines: Path | None = None,
    ingested: date | None = None,
) -> Source:
    """Ingest one document: extract, split, write its JSONL, and return its provenance.

    Args:
        document: The document id, one of the keys of
            :data:`~quaestor.corpus.documents.CORPUS_FILES`.
        pdf: The downloaded PDF.
        out: The directory to write the JSONL into.
        outlines: Where the outline files are; defaults to the repository's ``data/regulatory``.
        ingested: The date to record; defaults to today.

    Returns:
        The document's :class:`~quaestor.corpus.documents.Source` record.

    Raises:
        CorpusError: The document id is unknown, the PDF or the outline is missing, or a heading
            the outline names is not in the document.
    """
    if document not in CORPUS_FILES:
        raise CorpusError(
            f"{document!r} is not a corpus document; the corpus holds {sorted(CORPUS_FILES)} "
            "(DECISIONS D-055)"
        )
    directory = outlines or outline_dir()
    outline = load_outline(directory / OUTLINE_FILES[document], document)
    pages = extract_pages(pdf)
    spans = split_sections("\n".join(pages), outline)
    out.mkdir(parents=True, exist_ok=True)
    _write_jsonl(out / CORPUS_FILES[document], spans)
    return Source(
        document=document,
        title=outline.title,
        issued=outline.issued.isoformat(),
        status=outline.status,
        source_url=outline.source_url,
        pdf_sha256=sha256_file(pdf),
        pages=len(pages),
        sections=len(spans),
        outline_sha256=sha256_file(directory / OUTLINE_FILES[document]),
        ingested=(ingested or date.today()).isoformat(),
    )


def ingest(
    sr117: Path,
    sr262: Path,
    out: Path | None = None,
    *,
    outlines: Path | None = None,
    ingested: date | None = None,
) -> list[Source]:
    """Ingest both documents and write ``SOURCES.json``.

    Args:
        sr117: The SR 11-7 attachment PDF.
        sr262: The SR 26-2 attachment PDF.
        out: Where to write; defaults to the corpus package directory, which is what a real
            ingest wants, because that is what gets committed.
        outlines: Where the outline files are; defaults to the repository's ``data/regulatory``.
        ingested: The date to record; defaults to today. Passing it is what makes the ingest
            byte-idempotent across days in a test.

    Returns:
        One provenance record per document, in corpus order.

    Raises:
        CorpusError: Either document fails to ingest.
    """
    destination = out or corpus_root()
    sources = [
        ingest_document("SR11-7", sr117, destination, outlines=outlines, ingested=ingested),
        ingest_document("SR26-2", sr262, destination, outlines=outlines, ingested=ingested),
    ]
    payload = {
        "schema_version": 1,
        "documents": [source.model_dump(mode="json") for source in sources],
    }
    (destination / SOURCES_FILE).write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return sources


def main(argv: Sequence[str] | None = None) -> int:
    """Run the ingest from the command line.

    Args:
        argv: The arguments, or ``None`` to read ``sys.argv``.

    Returns:
        ``0`` on success, ``1`` when the ingest failed; the message goes to standard error.
    """
    parser = argparse.ArgumentParser(
        prog="python -m quaestor.corpus.ingest",
        description=(
            "Split the two model-risk guidance PDFs into the committed regulatory corpus. A "
            "dev-time script: no test and no validation run calls it."
        ),
    )
    parser.add_argument("--sr117", type=Path, required=True, help="the SR 11-7 attachment PDF")
    parser.add_argument("--sr262", type=Path, required=True, help="the SR 26-2 attachment PDF")
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="where to write the JSONL and SOURCES.json (default: the corpus package directory)",
    )
    parser.add_argument(
        "--outlines",
        type=Path,
        default=None,
        help="where the section outlines are (default: data/regulatory of this checkout)",
    )
    args = parser.parse_args(argv)
    try:
        sources = ingest(args.sr117, args.sr262, args.out, outlines=args.outlines)
    except CorpusError as exc:
        print(f"corpus ingest failed: {exc}", file=sys.stderr)
        return 1
    for source in sources:
        print(
            f"{source.document}: {source.sections} sections from {source.pages} pages "
            f"({source.status}), pdf sha256 {source.pdf_sha256[:16]}…"
        )
    return 0


if __name__ == "__main__":  # pragma: no cover - the module's command-line entry point
    raise SystemExit(main())
