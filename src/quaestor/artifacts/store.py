"""``ArtifactStore``: every computed number, table and figure, addressed by its content.

Spec section 3.4. A validation report is only as good as the ability to point at what produced
each of its numbers, so nothing a tool computes reaches the drafter except through this store:
``put`` returns an :class:`Artifact` whose hash is the number's identity, and the prose cites that
hash. Payload bytes are canonical -- sorted keys, floats formatted ``%.10g`` -- so the same
computation run twice, in two processes, produces one hash and not two.

The address covers the logical name as well as the payload. Pure value addressing would give
``metrics.train.event_rate`` and ``metrics.test.event_rate`` one hash whenever the two splits
happen to have the same event rate, and a finding's evidence list could then no longer say which
split it rested on (DECISIONS D-023).
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
from collections.abc import Mapping, Sequence
from enum import StrEnum
from pathlib import Path
from typing import Any, Final

from pydantic import BaseModel, ConfigDict, Field

from ..errors import ArtifactError
from ..hashing import stable_hash

__all__ = [
    "FLOAT_FORMAT",
    "HASH_LENGTH",
    "INDEX_FILE",
    "SHORT_HASH_LENGTH",
    "Artifact",
    "ArtifactKind",
    "ArtifactStore",
    "IndexEntry",
    "TableRows",
    "canonical_bytes",
]

INDEX_FILE: Final = "index.json"
"""The name of the index inside the store root."""

HASH_LENGTH: Final = 16
"""How many hex characters an artifact hash has. Citations quote the first eight."""

SHORT_HASH_LENGTH: Final = 8
"""How many hex characters a citation quotes: enough to be unambiguous, short enough to read."""

FLOAT_FORMAT: Final = ".10g"
"""Ten significant digits: past any metric's meaningful precision, short of a double's noise."""

SCHEMA_VERSION: Final = 1
"""Stamped on ``index.json``, as on every file Quaestor persists."""

_NAME_RE: Final = re.compile(r"^[a-z][A-Za-z0-9_]*(\.[A-Za-z0-9_+-]+)*$")
"""Logical names: lowercase-initial dotted segments; class codes keep their case (D-012, D-013)."""

TableRows = Sequence[Mapping[str, Any]]
"""A table payload: rows as mappings, every row carrying the same keys in the same order."""


class ArtifactKind(StrEnum):
    """What an artifact holds, which decides how it is serialised and how it may be cited.

    Attributes:
        scalar: One number. Cited bare; its value is copied into the index.
        table: Rows, written as canonical CSV. Cited with a ``#<row_key>.<column>`` suffix, where
            the row key is the value in the table's first column.
        json: A nested object. Cited with a dotted ``#path``.
        figure: PNG bytes. Never cited for a value; it is evidence a reader looks at.
    """

    scalar = "scalar"
    table = "table"
    json = "json"
    figure = "figure"


_SUFFIX: Final = {
    ArtifactKind.scalar: ".json",
    ArtifactKind.table: ".csv",
    ArtifactKind.json: ".json",
    ArtifactKind.figure: ".png",
}


class Artifact(BaseModel):
    """One stored artifact.

    Attributes:
        hash: The 16-character content address. A citation quotes its first eight characters.
        name: The logical name, such as ``metrics.test.auc``.
        kind: What it holds.
        path: Where the payload bytes are, inside the store root.
        summary: A caption for a human, rendered in Appendix B and above an expanded table.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    hash: str
    name: str
    kind: ArtifactKind
    path: Path
    summary: str = ""

    @property
    def short_hash(self) -> str:
        """The first eight characters of the hash, as a citation quotes it."""
        return self.hash[:SHORT_HASH_LENGTH]

    def citation(self, path: str | None = None) -> str:
        """Render the citation that resolves to this artifact.

        Args:
            path: The ``#row.column`` or ``#dotted.path`` suffix, for a table or JSON artifact.

        Returns:
            The citation text, ready to paste into prose.
        """
        suffix = f"#{path}" if path else ""
        return f"[[art:{self.short_hash}:{self.name}{suffix}]]"


class IndexEntry(BaseModel):
    """One row of ``index.json``: what a logical name resolves to.

    Attributes:
        hash: The artifact's content address.
        kind: What the artifact holds.
        value: The scalar value, or ``None`` for a table, JSON or figure artifact. Keeping it
            here is what lets the verifier match a cited scalar without opening the payload.
        summary: The caption.
        file: The payload file name, relative to the store root.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    hash: str
    kind: ArtifactKind
    value: float | None = None
    summary: str = ""
    file: str


class _Index(BaseModel):
    """The whole of ``index.json``."""

    model_config = ConfigDict(extra="forbid")

    schema_version: int = SCHEMA_VERSION
    artifacts: dict[str, IndexEntry] = Field(default_factory=dict)


def _format_number(value: float | int) -> str:
    """Format a number canonically: integers exactly, floats to ten significant digits.

    Booleans never reach here: every caller rejects or renders them first, because ``True`` is an
    ``int`` in Python and a scalar artifact of ``1`` that came from a flag is not a measurement.
    """
    if isinstance(value, int):
        return str(value)
    if not math.isfinite(value):
        raise ArtifactError(f"{value!r} has no canonical form; an artifact must be a real number")
    return format(value, FLOAT_FORMAT)


def _round_floats(obj: Any) -> Any:
    """Round every float in a JSON payload to the canonical ten significant digits."""
    if isinstance(obj, bool) or obj is None or isinstance(obj, (int, str)):
        return obj
    if isinstance(obj, float):
        return float(_format_number(obj))
    if isinstance(obj, Mapping):
        return {str(key): _round_floats(value) for key, value in obj.items()}
    if isinstance(obj, Sequence):
        return [_round_floats(item) for item in obj]
    raise ArtifactError(
        f"a json artifact cannot hold {type(obj).__name__}; pass plain JSON-compatible data"
    )


def _cell(value: Any) -> str:
    """Render one table cell canonically."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return _format_number(value)
    return str(value)


def _table_bytes(rows: TableRows) -> bytes:
    """Render rows as canonical CSV, insisting that every row has the same columns."""
    if not rows:
        raise ArtifactError("a table artifact needs at least one row; there is nothing to cite")
    columns = list(rows[0].keys())
    if not columns:
        raise ArtifactError("a table artifact needs at least one column")
    for number, row in enumerate(rows, start=1):
        if list(row.keys()) != columns:
            raise ArtifactError(
                f"row {number} of the table has columns {list(row.keys())}, not {columns}; a "
                "table artifact is rectangular so that a #row.column citation is unambiguous"
            )
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(columns)
    for row in rows:
        writer.writerow([_cell(row[column]) for column in columns])
    return buffer.getvalue().encode("utf-8")


def canonical_bytes(kind: ArtifactKind, payload: Any) -> bytes:
    """Render a payload to the bytes that are hashed and written.

    Args:
        kind: What the payload is.
        payload: The value, rows, object or PNG bytes.

    Returns:
        The canonical bytes: a JSON number for a scalar, canonical CSV for a table, sorted-key
        JSON with ``%.10g`` floats for a JSON artifact, and the bytes themselves for a figure.

    Raises:
        ArtifactError: The payload does not match the kind, or holds a value with no canonical
            form (``NaN``, an infinity, a type JSON cannot express).
    """
    if kind is ArtifactKind.scalar:
        if not isinstance(payload, (int, float)) or isinstance(payload, bool):
            raise ArtifactError(f"a scalar artifact holds a number, not {type(payload).__name__}")
        return (_format_number(payload) + "\n").encode("utf-8")
    if kind is ArtifactKind.table:
        if isinstance(payload, Mapping) or not isinstance(payload, Sequence):
            raise ArtifactError(
                f"a table artifact holds a sequence of row mappings, not "
                f"{type(payload).__name__}; a DataFrame is passed as df.to_dict('records')"
            )
        return _table_bytes(payload)
    if kind is ArtifactKind.json:
        rounded = _round_floats(payload)
        text = json.dumps(rounded, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
        return (text + "\n").encode("utf-8")
    if not isinstance(payload, (bytes, bytearray)):
        raise ArtifactError(f"a figure artifact holds PNG bytes, not {type(payload).__name__}")
    return bytes(payload)


class ArtifactStore:
    """A directory of content-addressed artifacts and the index that names them.

    Attributes:
        root: The store directory. ``index.json`` and the payload files live directly inside it.
    """

    def __init__(self, root: Path | str) -> None:
        """Open a store, reading an existing ``index.json`` if there is one.

        Args:
            root: The store directory. It is created if it does not exist.

        Raises:
            ArtifactError: ``index.json`` exists but is not a readable index.
        """
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._index = self._read_index()

    @property
    def index_path(self) -> Path:
        """Where the index is written."""
        return self.root / INDEX_FILE

    def _read_index(self) -> _Index:
        """Load ``index.json``, or start an empty index."""
        if not self.index_path.is_file():
            return _Index()
        try:
            raw = json.loads(self.index_path.read_text(encoding="utf-8"))
            return _Index.model_validate(raw)
        except (json.JSONDecodeError, ValueError) as exc:
            raise ArtifactError(
                f"{self.index_path} is not a readable artifact index: {exc}"
            ) from exc

    def _write_index(self) -> None:
        """Write ``index.json`` with its names in sorted order, so a diff is readable."""
        payload = {
            "schema_version": self._index.schema_version,
            "artifacts": {
                name: self._index.artifacts[name].model_dump(mode="json")
                for name in sorted(self._index.artifacts)
            },
        }
        self.index_path.write_text(
            json.dumps(payload, indent=2, sort_keys=False, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )

    def put(
        self,
        logical_name: str,
        payload: Any,
        kind: ArtifactKind | str,
        summary: str = "",
    ) -> Artifact:
        """Store one artifact and return it.

        Storing the same payload under the same name twice is idempotent: the hash is the same,
        the file is already there, and the same :class:`Artifact` comes back. Storing a *different*
        payload under a name that is already taken is an error, because a citation already written
        against the old hash would quietly stop resolving.

        Args:
            logical_name: The dotted name the prose cites, such as ``metrics.test.auc``.
            payload: A number, rows, a JSON-compatible object, or PNG bytes.
            kind: Which of those it is.
            summary: A caption for Appendix B and for an expanded table.

        Returns:
            The stored artifact.

        Raises:
            ArtifactError: The name is malformed, the payload does not match the kind, or the name
                is already taken by a different payload.
        """
        kind = ArtifactKind(kind)
        if not _NAME_RE.match(logical_name):
            raise ArtifactError(
                f"{logical_name!r} is not a logical artifact name; names are lowercase-initial "
                "dotted segments, with class codes keeping their case (threshold.E1.delta_auc)"
            )
        blob = canonical_bytes(kind, payload)
        digest = hashlib.sha256(blob).hexdigest()
        artifact_hash = stable_hash(
            {"kind": kind.value, "name": logical_name, "payload_sha256": digest},
            length=HASH_LENGTH,
        )
        existing = self._index.artifacts.get(logical_name)
        if existing is not None and existing.hash != artifact_hash:
            raise ArtifactError(
                f"the logical name {logical_name!r} already holds artifact {existing.hash} and "
                f"cannot be replaced by {artifact_hash}; every citation written against the old "
                "hash would stop resolving. Store the new value under a distinct name",
            )
        file_name = f"{artifact_hash}{_SUFFIX[kind]}"
        path = self.root / file_name
        if not path.exists():
            path.write_bytes(blob)
        value = float(payload) if kind is ArtifactKind.scalar else None
        self._index.artifacts[logical_name] = IndexEntry(
            hash=artifact_hash, kind=kind, value=value, summary=summary, file=file_name
        )
        self._write_index()
        return Artifact(
            hash=artifact_hash, name=logical_name, kind=kind, path=path, summary=summary
        )

    def names(self) -> list[str]:
        """Return every logical name in the store, sorted."""
        return sorted(self._index.artifacts)

    def __contains__(self, logical_name: object) -> bool:
        """Whether a logical name is in the index."""
        return logical_name in self._index.artifacts

    def __len__(self) -> int:
        """How many logical names the store holds."""
        return len(self._index.artifacts)

    def entry(self, logical_name: str) -> IndexEntry:
        """Return the index entry for a logical name.

        Args:
            logical_name: The name to look up.

        Returns:
            Its index entry.

        Raises:
            ArtifactError: The name is not in the index; the message lists nearby names.
        """
        entry = self._index.artifacts.get(logical_name)
        if entry is None:
            raise ArtifactError(
                f"{logical_name!r} is not in the artifact index at {self.index_path}"
                f"{self._nearby(logical_name)}"
            )
        return entry

    def _nearby(self, logical_name: str) -> str:
        """Suggest names sharing a prefix, so a typo is visible in the error itself."""
        prefix = logical_name.rsplit(".", 1)[0]
        near = [name for name in self.names() if name.startswith(prefix)][:5]
        return f"; names beginning {prefix!r}: {near}" if near else ""

    def artifact(self, logical_name: str) -> Artifact:
        """Return the artifact a logical name points at.

        Args:
            logical_name: The name to look up.

        Returns:
            The artifact.

        Raises:
            ArtifactError: The name is not in the index.
        """
        entry = self.entry(logical_name)
        return Artifact(
            hash=entry.hash,
            name=logical_name,
            kind=entry.kind,
            path=self.root / entry.file,
            summary=entry.summary,
        )

    def get(self, artifact_hash: str) -> Artifact:
        """Return the artifact with this hash, or with this hash as a prefix.

        Args:
            artifact_hash: A full 16-character hash, or a prefix of at least eight characters as
                a citation quotes it.

        Returns:
            The artifact.

        Raises:
            ArtifactError: The prefix is too short, matches nothing, or matches more than one
                artifact.
        """
        if len(artifact_hash) < SHORT_HASH_LENGTH:
            raise ArtifactError(
                f"{artifact_hash!r} is shorter than the {SHORT_HASH_LENGTH} characters a citation "
                "quotes, so it cannot identify an artifact"
            )
        matches = [
            name
            for name, entry in self._index.artifacts.items()
            if entry.hash.startswith(artifact_hash)
        ]
        if not matches:
            raise ArtifactError(f"no artifact in {self.root} has a hash beginning {artifact_hash}")
        if len(matches) > 1:
            raise ArtifactError(
                f"the hash prefix {artifact_hash} matches {sorted(matches)}; quote more of it"
            )
        return self.artifact(matches[0])

    def value(self, logical_name: str) -> float:
        """Return the scalar value of a logical name.

        Args:
            logical_name: The name to look up.

        Returns:
            The number.

        Raises:
            ArtifactError: The name is not in the index, or the artifact is not a scalar. A table
                names its columns in the message, because the caller wanted one cell of it.
        """
        entry = self.entry(logical_name)
        short = entry.hash[:SHORT_HASH_LENGTH]
        if entry.kind is ArtifactKind.table:
            columns = self.columns(logical_name)
            raise ArtifactError(
                f"{logical_name!r} is a table with columns {columns}, not a scalar; cite one cell "
                f"as [[art:{short}:{logical_name}#<row>.<column>]]"
            )
        if entry.kind is ArtifactKind.json:
            raise ArtifactError(
                f"{logical_name!r} is a json artifact, not a scalar; cite one path as "
                f"[[art:{short}:{logical_name}#<dotted.path>]]"
            )
        if entry.kind is ArtifactKind.figure:
            raise ArtifactError(f"{logical_name!r} is a figure and has no value to cite")
        if entry.value is None:
            raise ArtifactError(
                f"the index entry for the scalar {logical_name!r} at {self.index_path} carries no "
                "value; the index has been edited by hand"
            )
        return entry.value

    def load(self, logical_name: str) -> Any:
        """Return an artifact's payload, parsed back from its canonical bytes.

        Args:
            logical_name: The name to look up.

        Returns:
            A ``float`` for a scalar, a list of row dicts for a table, the decoded object for a
            JSON artifact, and ``bytes`` for a figure. Table cells come back as strings, which is
            what CSV holds; the citation resolver converts one cell at a time.

        Raises:
            ArtifactError: The name is not in the index, or its payload file is missing.
        """
        entry = self.entry(logical_name)
        path = self.root / entry.file
        if not path.is_file():
            raise ArtifactError(
                f"the payload of {logical_name!r} is missing from {path}; the store at "
                f"{self.root} and its index disagree"
            )
        if entry.kind is ArtifactKind.figure:
            return path.read_bytes()
        text = path.read_text(encoding="utf-8")
        if entry.kind is ArtifactKind.table:
            return list(csv.DictReader(io.StringIO(text)))
        return json.loads(text)

    def columns(self, logical_name: str) -> list[str]:
        """Return a table artifact's column names, the first of which is its row key.

        Args:
            logical_name: The name of a table artifact.

        Returns:
            The columns, in file order.

        Raises:
            ArtifactError: The name is not in the index, or is not a table.
        """
        entry = self.entry(logical_name)
        if entry.kind is not ArtifactKind.table:
            raise ArtifactError(f"{logical_name!r} is a {entry.kind}, not a table")
        rows = self.load(logical_name)
        return list(rows[0].keys()) if rows else []
