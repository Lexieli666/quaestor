"""Stable content hashing: the identity of every artifact, claim and cassette key.

Every persisted identity in Quaestor is a :func:`stable_hash` -- canonical JSON, SHA-256, a prefix
of the hex digest -- exactly as in Probatio, so that a cassette key recorded on a laptop means the
same thing on a CI runner and an artifact computed twice in two processes is one artifact. Python's
built-in :func:`hash` cannot be used for this: it is salted per process for strings.

Canonical means mapping keys sorted and coerced to strings, no insignificant whitespace, ASCII
escapes for every non-ASCII character, sets ordered by their own canonical form, pydantic models
reduced with ``model_dump(mode="json")``, and ``NaN`` or an infinity rejected rather than emitted
as the non-standard tokens :mod:`json` would otherwise write.

Floats are serialised by :func:`repr`, which since Python 3.1 is the shortest string that round
trips to the same double and is therefore both fixed and lossless. That is deliberately *not* the
``%.10g`` formatting that :mod:`quaestor.artifacts` applies to artifact payloads: an artifact is
rounded once, on the way in, so that two runs agree; a hash must never conflate two values that
differ, so it hashes what it was given (DECISIONS D-019).
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence, Set
from pathlib import PurePath
from typing import Any, Final

from pydantic import BaseModel

__all__ = ["MAX_LENGTH", "canonical_json", "sha256_file", "stable_hash"]

MAX_LENGTH: Final = 64
"""The number of hex characters in a full SHA-256 digest, and so the longest hash."""

_SCALARS: Final = (bool, int, float, str)


def _canonicalise(obj: object) -> Any:
    """Reduce an object to JSON-serialisable primitives with every ordering pinned down."""
    if obj is None or isinstance(obj, _SCALARS):
        return obj
    if isinstance(obj, BaseModel):
        return _canonicalise(obj.model_dump(mode="json"))
    if isinstance(obj, PurePath):
        return obj.as_posix()
    if isinstance(obj, Mapping):
        return {str(key): _canonicalise(value) for key, value in obj.items()}
    if isinstance(obj, Set):
        members = [_canonicalise(member) for member in obj]
        return sorted(members, key=lambda member: json.dumps(member, sort_keys=True))
    if isinstance(obj, (bytes, bytearray)):
        return obj.decode("utf-8", errors="strict")
    if isinstance(obj, Sequence):
        return [_canonicalise(item) for item in obj]
    raise TypeError(
        f"stable_hash cannot canonicalise {type(obj).__name__}; pass a pydantic model or plain "
        "JSON-compatible data, so that the hash means the same thing in the next process"
    )


def canonical_json(obj: object) -> str:
    """Serialise an object to the one JSON string Quaestor hashes.

    Args:
        obj: Any pydantic model, mapping, sequence, set, path, or JSON scalar.

    Returns:
        Compact JSON with sorted keys and ASCII escapes.

    Raises:
        TypeError: The object holds a type that has no canonical JSON form.
        ValueError: The object holds ``NaN`` or an infinity, which JSON cannot represent.
    """
    return json.dumps(
        _canonicalise(obj),
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def stable_hash(obj: object, *, length: int = 16) -> str:
    """Hash an object's content reproducibly across processes, platforms and interpreters.

    Args:
        obj: The object to hash; see :func:`canonical_json` for what is accepted.
        length: How many hex characters to return, from 1 to :data:`MAX_LENGTH`. The default of
            16 is the length of every identity Quaestor persists; artifact citations quote the
            first 8 of those.

    Returns:
        The first ``length`` hex characters of the SHA-256 digest of the canonical JSON.

    Raises:
        ValueError: ``length`` is outside ``1..MAX_LENGTH``.
    """
    if not 1 <= length <= MAX_LENGTH:
        raise ValueError(f"length must be between 1 and {MAX_LENGTH}, not {length}")
    digest = hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()
    return digest[:length]


def sha256_file(path: PurePath | str, *, chunk_bytes: int = 1 << 20) -> str:
    """Return the full SHA-256 hex digest of a file's bytes.

    Used to verify a package's declared data manifest (spec section 3.2). It is a plain file
    digest, not a :func:`stable_hash`, because the value it is compared against was produced by
    ``sha256sum`` on somebody else's machine.

    Args:
        path: The file to read.
        chunk_bytes: How much to read at a time, so that a large CSV is not held in memory.

    Returns:
        The 64-character hex digest.
    """
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while chunk := handle.read(chunk_bytes):
            digest.update(chunk)
    return digest.hexdigest()
