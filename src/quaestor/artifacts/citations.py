"""Citations: the five forms of ``[[...]]`` a report may carry, and what they resolve to.

``docs/REPORT_SCHEMA.md`` section 5 fixes the syntax and Phase 1 fixed it before any of this code
existed, which is the point of a golden report. Five forms:

* ``[[art:<hash8>:<logical_name>]]`` -- a scalar artifact.
* ``[[art:<hash8>:<logical_name>#<path>]]`` -- one cell of a table, addressed by the value in its
  first column and then the column name, or one path into a JSON artifact, dotted, with list
  elements addressed by their ``feature`` value, or by their ``name`` when they carry no
  ``feature`` (DECISIONS D-026).
* two adjacent ``[[art:...]]`` tokens -- the two operands of a ``delta`` or ``ratio`` claim, in
  order.
* ``[[reg:<doc>:<section_id>]]`` -- a span of the committed regulatory corpus, ``SR11-7`` or
  ``SR26-2`` (DECISIONS D-055). Resolved against the JSONL that :mod:`quaestor.corpus` ships, so a
  citation to a document that was never ingested or to a section the guidance does not have is
  ``dangling`` and the message names the citation.
* ``[[table:<logical_name>]]`` -- a drafter directive the renderer expands (D-013).

Resolution is deterministic and has no model in it. A citation that names a hash the store does not
hold, a hash8 that is not a prefix of the artifact the name points at, or a logical name the index
has never heard of, is ``dangling``, and the message quotes the citation as it was written -- the
repair loop hands that message straight back to the drafter.

Path resolution is structural only: a path walks keys and list elements and never computes. A
report that wants to cite "the number of features" cites an artifact that holds that count, which
is why ``run.features`` is stored as an object with its counts rather than as a bare list
(DECISIONS D-026).
"""

from __future__ import annotations

import re
from enum import StrEnum
from typing import Any, Final

from pydantic import BaseModel, ConfigDict

from ..corpus import RegulatoryCorpus, load_corpus
from ..errors import ArtifactError
from .store import SHORT_HASH_LENGTH, ArtifactKind, ArtifactStore

__all__ = [
    "CITATION_RE",
    "Citation",
    "CitationKind",
    "CitationStatus",
    "ResolvedCitation",
    "adjacent_pairs",
    "parse_citations",
    "resolve",
]

CITATION_RE: Final = re.compile(
    r"\[\[(?P<scheme>art|reg|table):(?P<body>[^\[\]]+)\]\]",
)
"""Every ``[[scheme:body]]`` token. A malformed body is reported, not skipped silently."""

_LIST_KEYS: Final = ("feature", "name")
"""The fields a list element is addressed by inside a JSON path, tried in this order.

``docs/REPORT_SCHEMA.md`` section 5 names ``feature``, which is what spec 3.3 calls the label in
``model_summary.json``'s ``coefficients`` and ``removed`` lists. The same section's other list is
``features.json``, whose elements label themselves ``name``, so a citation into
``run.features#items.<feature>.timing`` would have nothing to walk by. Accepting the second
spelling costs one fallback and is what lets both of the contract's own lists be cited
(DECISIONS D-026).
"""


class CitationKind(StrEnum):
    """Which of the three schemes a citation uses.

    Attributes:
        art: An artifact in this run's store.
        reg: A section of the regulatory corpus.
        table: A drafter directive asking the renderer to expand a table artifact.
    """

    art = "art"
    reg = "reg"
    table = "table"


class CitationStatus(StrEnum):
    """What happened when a citation was resolved.

    Attributes:
        resolved: The citation points at something that exists.
        dangling: It does not, and the message says why.
    """

    resolved = "resolved"
    dangling = "dangling"


class Citation(BaseModel):
    """One parsed citation and where in the text it was found.

    Attributes:
        raw: The citation exactly as written, brackets included.
        kind: Which scheme it uses.
        hash8: The quoted hash prefix, for an ``art`` citation.
        name: The logical artifact name, for ``art`` and ``table``.
        path: The ``#`` suffix of an ``art`` citation, or ``None``.
        doc: The corpus document, for a ``reg`` citation.
        section_id: The corpus section, for a ``reg`` citation.
        start: Offset of the first ``[`` in the text it was parsed from.
        end: Offset just past the last ``]``.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    raw: str
    kind: CitationKind
    hash8: str | None = None
    name: str | None = None
    path: str | None = None
    doc: str | None = None
    section_id: str | None = None
    start: int = 0
    end: int = 0


def parse_citations(text: str) -> list[Citation]:
    """Find every citation in a piece of prose, in the order it appears.

    Args:
        text: The prose to scan. A drafted section, a finding narrative, one table row.

    Returns:
        The citations, with their offsets, so that adjacency can be tested afterwards.

    Raises:
        ArtifactError: A token uses a known scheme with a body that does not parse -- an ``art``
            citation with no logical name, a ``reg`` citation with no section. Naming it here is
            better than letting it resolve as ``dangling``, which would read as the drafter citing
            something that does not exist rather than writing a malformed citation.
    """
    citations: list[Citation] = []
    for match in CITATION_RE.finditer(text):
        scheme = CitationKind(match.group("scheme"))
        body = match.group("body")
        raw, start, end = match.group(0), match.start(), match.end()
        if scheme is CitationKind.table:
            citations.append(Citation(raw=raw, kind=scheme, name=body, start=start, end=end))
            continue
        head, _, tail = body.partition(":")
        if not head or not tail:
            shape = (
                "[[art:<hash8>:<logical_name>]]"
                if scheme is CitationKind.art
                else "[[reg:<doc>:<section_id>]]"
            )
            raise ArtifactError(
                f"{raw} is not a citation: {scheme.value} takes two colon-separated parts, {shape}"
            )
        if scheme is CitationKind.reg:
            citations.append(
                Citation(raw=raw, kind=scheme, doc=head, section_id=tail, start=start, end=end)
            )
            continue
        name, _, path = tail.partition("#")
        citations.append(
            Citation(
                raw=raw,
                kind=scheme,
                hash8=head,
                name=name,
                path=path or None,
                start=start,
                end=end,
            )
        )
    return citations


def adjacent_pairs(citations: list[Citation]) -> list[tuple[Citation, Citation]]:
    """Return the pairs of ``art`` citations written with nothing between them.

    Two adjacent citations are how a ``delta`` or ``ratio`` claim cites both of its operands, in
    order: the claimed value is ``second - first`` for a delta and ``second / first`` for a ratio
    (D-012).

    Args:
        citations: The output of :func:`parse_citations`, in text order.

    Returns:
        Each adjacent pair, in text order. A run of three touching citations yields two
        overlapping pairs, and the matcher rejects that when it sees it.
    """
    pairs = []
    for first, second in zip(citations, citations[1:], strict=False):
        if (
            first.kind is CitationKind.art
            and second.kind is CitationKind.art
            and first.end == second.start
        ):
            pairs.append((first, second))
    return pairs


class ResolvedCitation(BaseModel):
    """What a citation turned out to point at.

    Attributes:
        citation: The citation as parsed.
        status: Whether it resolved.
        value: The number it resolves to, when it names a scalar or a numeric cell or path.
        message: Why it did not resolve; ``None`` when it resolved.
        kind: The kind of artifact it resolved to, when it resolved to one.
        heading: The guidance heading a ``reg`` citation resolved to, so that a renderer can name
            the section a report anchors itself to without re-reading the corpus.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    citation: Citation
    status: CitationStatus
    value: float | None = None
    message: str | None = None
    kind: ArtifactKind | None = None
    heading: str | None = None

    @property
    def is_resolved(self) -> bool:
        """Whether the citation points at something that exists."""
        return self.status is CitationStatus.resolved


def resolve(
    citation: Citation,
    store: ArtifactStore,
    *,
    corpus: RegulatoryCorpus | None = None,
) -> ResolvedCitation:
    """Resolve one citation against an artifact store and the regulatory corpus.

    Args:
        citation: A parsed citation.
        store: The run's artifact store.
        corpus: The corpus a ``reg`` citation resolves against; defaults to the committed one.

    Returns:
        The resolution. Every failure is :attr:`CitationStatus.dangling` with a message that
        quotes the citation, which is what the repair loop hands back to the drafter.
    """
    if citation.kind is CitationKind.reg:
        return _resolve_guidance(citation, corpus or load_corpus())
    if citation.kind is CitationKind.table:
        return _resolve_table_directive(citation, store)
    return _resolve_artifact(citation, store)


def _resolve_guidance(citation: Citation, corpus: RegulatoryCorpus) -> ResolvedCitation:
    """Resolve ``[[reg:<doc>:<section_id>]]`` against the committed corpus."""
    doc, section_id = citation.doc or "", citation.section_id or ""
    if doc not in corpus.documents():
        return _dangling(
            citation,
            f"{citation.raw} names document {doc!r}, which is not in the regulatory corpus; it "
            f"holds {corpus.documents()}. OCC Bulletin 2011-12 is deliberately not ingested "
            "(DECISIONS D-055)",
        )
    span = corpus.get(doc, section_id)
    if span is None:
        return _dangling(
            citation,
            f"{citation.raw} names section {section_id!r}, which {doc} does not have; its "
            f"sections are {corpus.section_ids(doc)}",
        )
    return ResolvedCitation(citation=citation, status=CitationStatus.resolved, heading=span.heading)


def _dangling(citation: Citation, message: str) -> ResolvedCitation:
    """Build a dangling resolution whose message quotes the citation as it was written."""
    return ResolvedCitation(citation=citation, status=CitationStatus.dangling, message=message)


def _resolve_table_directive(citation: Citation, store: ArtifactStore) -> ResolvedCitation:
    """Resolve ``[[table:<name>]]``: it must name a table artifact the renderer can expand."""
    name = citation.name or ""
    if name not in store:
        return _dangling(
            citation, f"{citation.raw} names {name!r}, which is not in the artifact index"
        )
    entry = store.entry(name)
    if entry.kind is not ArtifactKind.table:
        return _dangling(
            citation,
            f"{citation.raw} names a {entry.kind} artifact; only a table can be expanded into a "
            "renderer block",
        )
    return ResolvedCitation(
        citation=citation, status=CitationStatus.resolved, kind=ArtifactKind.table
    )


def _resolve_artifact(citation: Citation, store: ArtifactStore) -> ResolvedCitation:
    """Resolve ``[[art:<hash8>:<name>[#path]]]`` against the index and the payload."""
    name = citation.name or ""
    hash8 = citation.hash8 or ""
    if name not in store:
        return _dangling(
            citation, f"{citation.raw} names {name!r}, which is not in the artifact index"
        )
    entry = store.entry(name)
    if len(hash8) < SHORT_HASH_LENGTH:
        return _dangling(
            citation,
            f"{citation.raw} quotes {hash8!r}, which is shorter than the {SHORT_HASH_LENGTH} "
            f"characters a citation carries; {name!r} is {entry.hash[:SHORT_HASH_LENGTH]}",
        )
    if not entry.hash.startswith(hash8):
        return _dangling(
            citation,
            f"{citation.raw} quotes {hash8}, which is not a prefix of {entry.hash} -- the hash "
            f"{name!r} actually has. The number cited belongs to another artifact or another run",
        )
    if not (store.root / entry.file).is_file():
        return _dangling(
            citation, f"{citation.raw} resolves to {entry.file}, which is not in {store.root}"
        )
    if citation.path is None:
        return _resolve_whole(citation, store, name)
    return _resolve_path(citation, store, name)


def _resolve_whole(citation: Citation, store: ArtifactStore, name: str) -> ResolvedCitation:
    """Resolve a citation with no ``#`` suffix, which must name a scalar."""
    entry = store.entry(name)
    if entry.kind is not ArtifactKind.scalar:
        return _dangling(
            citation,
            f"{citation.raw} cites a {entry.kind} artifact as if it were a number; add a "
            f"#<path> suffix naming the cell or path to cite",
        )
    return ResolvedCitation(
        citation=citation,
        status=CitationStatus.resolved,
        value=store.value(name),
        kind=ArtifactKind.scalar,
    )


def _resolve_path(citation: Citation, store: ArtifactStore, name: str) -> ResolvedCitation:
    """Resolve a ``#`` suffix into a table cell or a JSON path."""
    entry = store.entry(name)
    path = citation.path or ""
    try:
        if entry.kind is ArtifactKind.table:
            found = _table_cell(store, name, path)
        elif entry.kind is ArtifactKind.json:
            found = _json_path(store.load(name), path)
        else:
            return _dangling(
                citation,
                f"{citation.raw} carries a #{path} suffix, but {name!r} is a {entry.kind} "
                "artifact, which has no addressable parts",
            )
    except ArtifactError as exc:
        return _dangling(citation, f"{citation.raw} does not resolve: {exc.message}")
    number = _as_float(found)
    if number is None:
        return _dangling(
            citation,
            f"{citation.raw} resolves to {found!r}, which is not a number, so no claim can be "
            "matched against it",
        )
    return ResolvedCitation(
        citation=citation, status=CitationStatus.resolved, value=number, kind=entry.kind
    )


def _table_cell(store: ArtifactStore, name: str, path: str) -> Any:
    """Return one cell of a table, addressed as ``<row_key>.<column>``."""
    row_key, _, column = path.partition(".")
    if not column:
        raise ArtifactError(
            f"a table cell is cited as #<row>.<column>, not #{path}; the row key is the value in "
            f"the table's first column"
        )
    rows = store.load(name)
    columns = list(rows[0].keys()) if rows else []
    if column not in columns:
        raise ArtifactError(f"{name!r} has columns {columns}, not {column!r}")
    key_column = columns[0]
    for row in rows:
        if str(row[key_column]) == row_key:
            return row[column]
    keys = [str(row[key_column]) for row in rows]
    raise ArtifactError(f"no row of {name!r} has {key_column} == {row_key!r}; rows are {keys}")


def _json_path(payload: Any, path: str) -> Any:
    """Walk a dotted path into a JSON artifact, addressing list elements by their ``feature``."""
    current = payload
    walked: list[str] = []
    for segment in path.split("."):
        walked.append(segment)
        here = ".".join(walked)
        if isinstance(current, dict):
            if segment not in current:
                raise ArtifactError(f"#{here} is not in the artifact; it has {sorted(current)}")
            current = current[segment]
        elif isinstance(current, list):
            current = _list_element(current, segment, here)
        else:
            raise ArtifactError(
                f"#{here} walks into a {type(current).__name__}, which has no addressable parts"
            )
    return current


def _list_element(items: list[Any], segment: str, here: str) -> Any:
    """Return the element of a list labelled ``segment``, by its ``feature`` or by its ``name``."""
    labels: list[str] = []
    for key in _LIST_KEYS:
        for item in items:
            if isinstance(item, dict) and key in item:
                if str(item[key]) == segment:
                    return item
                labels.append(str(item[key]))
        if labels:
            break
    keys = " or ".join(_LIST_KEYS)
    raise ArtifactError(
        f"no element at #{here} has {keys} == {segment!r}"
        + (f"; the list holds {labels}" if labels else f"; its elements have no {keys} field")
    )


def _as_float(value: Any) -> float | None:
    """Coerce a resolved cell or path to a number, or return ``None`` when it is not one."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None
