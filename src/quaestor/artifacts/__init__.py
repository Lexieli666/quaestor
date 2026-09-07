"""The content-addressed artifact store, its index and the citation syntax.

Filled in Phase 2 from spec section 3.4. Payload bytes are canonical so that
identical results hash identically across runs and processes, which is what makes a citation
``[[art:<hash8>:<logical_name>]]`` checkable rather than decorative.
"""

from __future__ import annotations

from .citations import (
    CITATION_RE,
    Citation,
    CitationKind,
    CitationStatus,
    ResolvedCitation,
    adjacent_pairs,
    parse_citations,
    resolve,
)
from .store import (
    FLOAT_FORMAT,
    HASH_LENGTH,
    INDEX_FILE,
    SHORT_HASH_LENGTH,
    Artifact,
    ArtifactKind,
    ArtifactStore,
    IndexEntry,
    canonical_bytes,
)

__all__ = [
    "CITATION_RE",
    "FLOAT_FORMAT",
    "HASH_LENGTH",
    "INDEX_FILE",
    "SHORT_HASH_LENGTH",
    "Artifact",
    "ArtifactKind",
    "ArtifactStore",
    "Citation",
    "CitationKind",
    "CitationStatus",
    "IndexEntry",
    "ResolvedCitation",
    "adjacent_pairs",
    "canonical_bytes",
    "parse_citations",
    "resolve",
]
