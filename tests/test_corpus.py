"""The regulatory corpus: the committed documents, and the ingest that produced them.

Two halves. The first pins the committed JSONL against the outline files in `data/regulatory/`,
so that a corpus edited by hand, or an outline changed without a re-ingest, is a failure here. The
second exercises `quaestor.corpus.ingest` end to end on a synthetic two-page PDF this module
writes with pypdf's own writer: no test reads `sr1107a1.pdf` or `sr2602a1.pdf`, which are not in
this repository and never will be.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from datetime import date
from pathlib import Path

import pytest
import yaml
from pypdf import PdfWriter
from pypdf.generic import ContentStream, DictionaryObject, NameObject

from quaestor.corpus import CORPUS_FILES, SOURCES_FILE, RegulatoryCorpus, Span, load_corpus
from quaestor.corpus.documents import corpus_root
from quaestor.corpus.ingest import (
    OUTLINE_FILES,
    Outline,
    extract_pages,
    ingest,
    ingest_document,
    load_outline,
    main,
    outline_dir,
    split_sections,
)
from quaestor.errors import CorpusError

REPO_ROOT = Path(__file__).resolve().parents[1]
REGULATORY = REPO_ROOT / "data" / "regulatory"


# --- the committed corpus -------------------------------------------------------------------------


def test_both_documents_are_committed_and_no_others() -> None:
    corpus = load_corpus()
    assert corpus.documents() == ["SR11-7", "SR26-2"]
    # OCC Bulletin 2011-12 carried the same text as SR 11-7 and was rescinded (DECISIONS D-055).
    assert corpus.get("OCC2011-12", "V") is None


def test_the_committed_sections_are_the_outline_s_sections_in_order() -> None:
    corpus = load_corpus()
    for document, file_name in OUTLINE_FILES.items():
        outline = load_outline(REGULATORY / file_name, document)
        assert corpus.section_ids(document) == [s.section_id for s in outline.sections]
        for span in corpus.sections(document):
            expected = next(s for s in outline.sections if s.section_id == span.section_id)
            assert span.heading == expected.heading


def test_the_two_documents_have_the_section_counts_the_run_log_records() -> None:
    corpus = load_corpus()
    assert len(corpus.sections("SR11-7")) == 21
    assert len(corpus.sections("SR26-2")) == 16
    assert len(corpus) == 37


def test_every_section_that_has_prose_in_the_document_has_text() -> None:
    # SR 26-2's IV and V.1 are pure container headings: the next heading follows immediately, so
    # they are ingested with an empty body rather than with the text of the section beneath them.
    empty = {(span.doc, span.section_id) for span in load_corpus() if not span.text}
    assert empty == {("SR26-2", "IV"), ("SR26-2", "V.1")}


def test_the_outcomes_analysis_sections_read_like_outcomes_analysis() -> None:
    corpus = load_corpus()
    superseded = corpus.get("SR11-7", "V.1.c")
    current = corpus.get("SR26-2", "V.1.b")
    assert superseded is not None and current is not None
    assert superseded.heading == current.heading == "Outcomes Analysis"
    assert "backtesting" in superseded.text.lower() or "back-testing" in superseded.text.lower()
    assert "outcomes analysis" in current.text.lower()


def test_the_corpus_carries_no_page_markers() -> None:
    for span in load_corpus():
        for line in span.text.splitlines():
            assert not line.strip().isdigit(), (span.doc, span.section_id, line)
            assert not line.strip().startswith("Page "), (span.doc, span.section_id, line)


def test_sources_records_the_provenance_of_both_documents() -> None:
    corpus = load_corpus()
    superseded = corpus.sources["SR11-7"]
    current = corpus.sources["SR26-2"]
    assert superseded.status == "superseded by SR26-2 on 2026-04-17"
    assert current.status == "current"
    assert superseded.issued == "2011-04-04"
    assert current.issued == "2026-04-17"
    assert (superseded.pages, superseded.sections) == (21, 21)
    assert (current.pages, current.sections) == (12, 16)
    for source in (superseded, current):
        assert len(source.pdf_sha256) == 64
        assert source.source_url.startswith("https://www.federalreserve.gov/")


def test_sources_pins_the_outline_files_that_were_split_by() -> None:
    import hashlib

    for document, source in load_corpus().sources.items():
        digest = hashlib.sha256((REGULATORY / OUTLINE_FILES[document]).read_bytes()).hexdigest()
        assert source.outline_sha256 == digest, f"{document}: re-run the ingest"


def test_the_corpus_files_are_where_the_package_ships_them() -> None:
    for file_name in CORPUS_FILES.values():
        assert (corpus_root() / file_name).is_file()
    assert (corpus_root() / SOURCES_FILE).is_file()


def test_loading_is_cached_per_root() -> None:
    assert load_corpus() is load_corpus()


# --- the corpus object ----------------------------------------------------------------------------


def span(doc: str, section_id: str, heading: str = "H", text: str = "t") -> Span:
    return Span(doc=doc, section_id=section_id, heading=heading, text=text)


def test_a_corpus_addresses_a_span_by_document_and_section() -> None:
    corpus = RegulatoryCorpus([span("A", "I"), span("B", "I")])
    found = corpus.get("B", "I")
    assert found is not None and found.doc == "B"
    assert corpus.get("A", "II") is None
    assert len(corpus) == 2
    assert [s.doc for s in corpus] == ["A", "B"]


def test_two_spans_with_one_address_are_refused() -> None:
    with pytest.raises(CorpusError, match=r"\[\[reg:A:I\]\]"):
        RegulatoryCorpus([span("A", "I"), span("A", "I", heading="other")])


def test_a_subset_keeps_only_the_named_documents() -> None:
    corpus = RegulatoryCorpus([span("A", "I"), span("B", "I")])
    assert corpus.subset(["A"]).documents() == ["A"]
    assert corpus.subset(None) is corpus


def test_a_subset_of_a_document_that_is_not_there_names_the_ones_that_are() -> None:
    corpus = RegulatoryCorpus([span("A", "I")])
    with pytest.raises(CorpusError, match=r"holds \['A'\]"):
        corpus.subset(["C"])


def test_a_span_renders_its_own_citation() -> None:
    assert span("SR26-2", "V.1.b").citation == "[[reg:SR26-2:V.1.b]]"


def test_a_missing_document_names_the_ingest_command(tmp_path: Path) -> None:
    with pytest.raises(CorpusError, match="was never ingested") as caught:
        load_corpus(tmp_path)
    assert "quaestor.corpus.ingest" in (caught.value.fix or "")


def test_a_malformed_line_names_the_line(tmp_path: Path) -> None:
    for file_name in CORPUS_FILES.values():
        (tmp_path / file_name).write_text('{"doc": "X"}\n', encoding="utf-8")
    with pytest.raises(CorpusError, match="line 1 is not a corpus span"):
        load_corpus(tmp_path)


def test_blank_lines_in_a_jsonl_are_skipped(tmp_path: Path) -> None:
    for doc, file_name in CORPUS_FILES.items():
        payload = json.dumps({"doc": doc, "section_id": "I", "heading": "H", "text": "t"})
        (tmp_path / file_name).write_text(f"\n{payload}\n\n", encoding="utf-8")
    assert len(load_corpus(tmp_path)) == 2


# --- the ingest -----------------------------------------------------------------------------------


def write_pdf(path: Path, pages: Sequence[Sequence[str]]) -> None:
    """Write a PDF whose pages hold these lines of text, using pypdf's own writer."""
    writer = PdfWriter()
    for lines in pages:
        page = writer.add_blank_page(width=612, height=792)
        drawn = ["BT", "/F1 12 Tf", "14 TL", "72 720 Td"]
        for line in lines:
            escaped = line.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")
            drawn += [f"({escaped}) Tj", "T*"]
        drawn.append("ET")
        stream = ContentStream(None, writer)
        stream.set_data("\n".join(drawn).encode("ascii"))
        page.replace_contents(stream)
        font = DictionaryObject(
            {
                NameObject("/Type"): NameObject("/Font"),
                NameObject("/Subtype"): NameObject("/Type1"),
                NameObject("/BaseFont"): NameObject("/Helvetica"),
            }
        )
        page[NameObject("/Resources")] = DictionaryObject(
            {NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})}
        )
    with path.open("wb") as handle:
        writer.write(handle)


TOY_PAGES = {
    "SR11-7": [
        ["I. Introduction, page 1", "II. Second Part, page 2", "I. INTRODUCTION", "alpha beta"],
        ["1", "gamma delta", "II. SECOND PART", "epsilon"],
    ],
    "SR26-2": [
        ["I. INTRODUCTION", "one two", "Page 1"],
        ["II. SECOND PART", "three four"],
    ],
}

TOY_OUTLINE = {
    "SR11-7": {
        "document": "SR11-7",
        "title": "Toy superseded guidance",
        "issued": date(2011, 4, 4),
        "source_url": "https://example.invalid/sr1107a1.pdf",
        "superseded_by": "SR26-2",
        "superseded_on": date(2026, 4, 17),
        "sections": [
            {"section_id": "I", "heading": "Introduction"},
            {"section_id": "II", "heading": "Second Part"},
        ],
    },
    "SR26-2": {
        "document": "SR26-2",
        "title": "Toy current guidance",
        "issued": date(2026, 4, 17),
        "source_url": "https://example.invalid/sr2602a1.pdf",
        "supersedes": ["SR11-7"],
        "sections": [
            {"section_id": "I", "heading": "Introduction"},
            {"section_id": "II", "heading": "Second Part"},
        ],
    },
}


@pytest.fixture
def toy_ingest(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    """A synthetic two-page PDF per document, a matching outline directory, and an out directory."""
    outlines = tmp_path / "outlines"
    outlines.mkdir()
    for document, payload in TOY_OUTLINE.items():
        (outlines / OUTLINE_FILES[document]).write_text(
            yaml.safe_dump(payload, sort_keys=False), encoding="utf-8"
        )
    pdfs = tmp_path / "pdfs"
    pdfs.mkdir()
    for document, pages in TOY_PAGES.items():
        write_pdf(pdfs / f"{document}.pdf", pages)
    return pdfs / "SR11-7.pdf", pdfs / "SR26-2.pdf", outlines, tmp_path / "out"


def test_the_ingest_writes_both_documents_and_their_sources(
    toy_ingest: tuple[Path, Path, Path, Path],
) -> None:
    sr117, sr262, outlines, out = toy_ingest
    sources = ingest(sr117, sr262, out, outlines=outlines, ingested=date(2026, 9, 7))

    assert [source.document for source in sources] == ["SR11-7", "SR26-2"]
    assert [source.pages for source in sources] == [2, 2]
    assert [source.sections for source in sources] == [2, 2]
    assert sources[0].status == "superseded by SR26-2 on 2026-04-17"
    assert sources[1].status == "current"
    assert all(source.ingested == "2026-09-07" for source in sources)

    corpus = load_corpus(out)
    assert corpus.documents() == ["SR11-7", "SR26-2"]
    first = corpus.get("SR11-7", "I")
    assert first is not None
    assert first.heading == "Introduction"
    assert first.text == "alpha beta\ngamma delta"
    second = corpus.get("SR26-2", "II")
    assert second is not None and second.text == "three four"


def test_the_table_of_contents_is_not_mistaken_for_the_body(
    toy_ingest: tuple[Path, Path, Path, Path],
) -> None:
    sr117, sr262, outlines, out = toy_ingest
    ingest(sr117, sr262, out, outlines=outlines, ingested=date(2026, 9, 7))
    introduction = load_corpus(out).get("SR11-7", "I")
    assert introduction is not None
    # "I. Introduction, page 1" is a contents entry, not the heading; the section starts below it.
    assert "page 1" not in introduction.text
    assert "II. Second Part, page 2" not in introduction.text


def test_the_ingest_drops_page_markers(toy_ingest: tuple[Path, Path, Path, Path]) -> None:
    sr117, sr262, outlines, out = toy_ingest
    ingest(sr117, sr262, out, outlines=outlines, ingested=date(2026, 9, 7))
    for span_ in load_corpus(out):
        assert "Page 1" not in span_.text
        assert "\n1\n" not in f"\n{span_.text}\n"


def test_the_ingest_is_idempotent(toy_ingest: tuple[Path, Path, Path, Path]) -> None:
    sr117, sr262, outlines, out = toy_ingest
    ingest(sr117, sr262, out, outlines=outlines, ingested=date(2026, 9, 7))
    before = {path.name: path.read_bytes() for path in sorted(out.iterdir())}
    ingest(sr117, sr262, out, outlines=outlines, ingested=date(2026, 9, 7))
    after = {path.name: path.read_bytes() for path in sorted(out.iterdir())}
    assert before == after
    assert set(before) == {*CORPUS_FILES.values(), SOURCES_FILE}


def test_the_command_line_runs_the_ingest(
    toy_ingest: tuple[Path, Path, Path, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    sr117, sr262, outlines, out = toy_ingest
    code = main(
        [
            "--sr117",
            str(sr117),
            "--sr262",
            str(sr262),
            "--out",
            str(out),
            "--outlines",
            str(outlines),
        ]
    )
    assert code == 0
    printed = capsys.readouterr().out
    assert "SR11-7: 2 sections from 2 pages (superseded by SR26-2 on 2026-04-17)" in printed
    assert "SR26-2: 2 sections from 2 pages (current)" in printed


def test_the_command_line_reports_a_failure_without_a_traceback(
    toy_ingest: tuple[Path, Path, Path, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    _, sr262, outlines, out = toy_ingest
    code = main(
        [
            "--sr117",
            str(out / "absent.pdf"),
            "--sr262",
            str(sr262),
            "--out",
            str(out),
            "--outlines",
            str(outlines),
        ]
    )
    assert code == 1
    assert "corpus ingest failed" in capsys.readouterr().err


def test_a_heading_the_document_lacks_names_the_heading(
    toy_ingest: tuple[Path, Path, Path, Path],
) -> None:
    sr117, _, outlines, out = toy_ingest
    payload = dict(TOY_OUTLINE["SR11-7"])
    payload["sections"] = [
        {"section_id": "I", "heading": "Introduction"},
        {"section_id": "III", "heading": "Outcomes Analysis"},
    ]
    (outlines / OUTLINE_FILES["SR11-7"]).write_text(
        yaml.safe_dump(payload, sort_keys=False), encoding="utf-8"
    )
    with pytest.raises(CorpusError, match="'Outcomes Analysis'") as caught:
        ingest_document("SR11-7", sr117, out, outlines=outlines, ingested=date(2026, 9, 7))
    assert "SR11-7 section III" in caught.value.message
    assert "never force the text to the outline" in (caught.value.fix or "")


def test_a_heading_out_of_the_document_s_order_is_not_found(
    toy_ingest: tuple[Path, Path, Path, Path],
) -> None:
    sr117, _, outlines, out = toy_ingest
    payload = dict(TOY_OUTLINE["SR11-7"])
    payload["sections"] = [
        {"section_id": "I", "heading": "Second Part"},
        {"section_id": "II", "heading": "Introduction"},
    ]
    (outlines / OUTLINE_FILES["SR11-7"]).write_text(
        yaml.safe_dump(payload, sort_keys=False), encoding="utf-8"
    )
    with pytest.raises(CorpusError, match="'Introduction'"):
        ingest_document("SR11-7", sr117, out, outlines=outlines, ingested=date(2026, 9, 7))


def test_a_document_the_corpus_does_not_hold_is_refused(
    toy_ingest: tuple[Path, Path, Path, Path],
) -> None:
    sr117, _, outlines, out = toy_ingest
    with pytest.raises(CorpusError, match="OCC2011-12"):
        ingest_document("OCC2011-12", sr117, out, outlines=outlines)


def test_a_pdf_that_is_not_there_is_named(tmp_path: Path) -> None:
    with pytest.raises(CorpusError, match="there is no PDF at"):
        extract_pages(tmp_path / "absent.pdf")


def test_an_outline_that_is_not_there_is_named(tmp_path: Path) -> None:
    with pytest.raises(CorpusError, match="there is no section outline at"):
        load_outline(tmp_path / "absent.yaml")


def test_an_outline_with_an_unknown_field_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "outline.yaml"
    payload = dict(TOY_OUTLINE["SR26-2"])
    payload["chapters"] = []
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    with pytest.raises(CorpusError, match="is not a section outline"):
        load_outline(path)


def test_an_outline_for_another_document_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "sr26-2-outline.yaml"
    path.write_text(yaml.safe_dump(TOY_OUTLINE["SR26-2"], sort_keys=False), encoding="utf-8")
    with pytest.raises(CorpusError, match="declares document 'SR26-2'"):
        load_outline(path, "SR11-7")


def test_the_real_outlines_load_and_are_where_the_ingest_looks() -> None:
    assert outline_dir() == REGULATORY
    superseded = load_outline(REGULATORY / OUTLINE_FILES["SR11-7"], "SR11-7")
    current = load_outline(REGULATORY / OUTLINE_FILES["SR26-2"], "SR26-2")
    assert superseded.status == "superseded by SR26-2 on 2026-04-17"
    assert current.status == "current"
    assert current.supersedes == ["SR11-7", "SR21-8"]
    assert current.same_text_as is not None and "2026-13" in current.same_text_as


def test_splitting_ignores_the_text_before_the_first_heading() -> None:
    outline = Outline.model_validate(
        {
            **TOY_OUTLINE["SR26-2"],
            "sections": [{"section_id": "I", "heading": "Introduction"}],
        }
    )
    spans = split_sections("a cover page\nI. INTRODUCTION\nthe body", outline)
    assert spans == [Span(doc="SR26-2", section_id="I", heading="Introduction", text="the body")]


def test_a_heading_may_carry_a_letter_or_a_number_label() -> None:
    outline = Outline.model_validate(
        {
            **TOY_OUTLINE["SR26-2"],
            "sections": [
                {"section_id": "V.1.a", "heading": "Conceptual Soundness"},
                {"section_id": "V.1.b", "heading": "Outcomes Analysis"},
            ],
        }
    )
    text = "a. Conceptual Soundness\ndesign\n3) Outcomes Analysis\nbacktests"
    spans = split_sections(text, outline)
    assert [s.text for s in spans] == ["design", "backtests"]
