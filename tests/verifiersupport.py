"""Building an artifact store the golden report's own claims can be re-matched against.

`examples/golden_report/` is a specification, not a run: every number in it is illustrative and
every hash is `sha256(logical_name)[:8]`, which resolves to nothing. To point the Phase 7 matcher
at all 92 of its post-repair claims, this module rebuilds a store from Appendix B — the logical
name, the kind and the value of every artifact the report cites — and rewrites each citation's
hash to the one the rebuilt store actually produced.

**Matching on the logical name is a licence this one test takes and nothing else does.** In a real
run the hash is the point: it is what stops a number being cited to an artifact of another run.
Here the hashes cannot agree, because a content address of an illustrative value is not the
address of the same value stored today, so the test asserts the half of the citation that can be
asserted and says so out loud.

Three shapes of artifact are needed and Appendix B only carries one of them. Scalars come straight
from the appendix. The two table artifacts are read back out of the report's own renderer blocks,
with their printed headers turned back into the column names the citations use (`event rate` is
printed, `event_rate` is cited). The five JSON artifacts have no values in the appendix at all, so
they are written out here from the report's prose, which is the same numbers by a different route
and is stated as a limitation in `PROGRESS.md`.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Final

from quaestor.artifacts import ArtifactKind, ArtifactStore

ROOT: Final = Path(__file__).resolve().parents[1]
GOLDEN: Final = ROOT / "examples" / "golden_report"

_APPENDIX_B_RE: Final = re.compile(
    r"^\| `(?P<name>[^`]+)` \| `(?P<hash>[0-9a-f]{8})` \| (?P<kind>\w+) \| (?P<value>[^|]*)\|$",
    re.MULTILINE,
)
"""One row of Appendix B: logical name, illustrative hash, kind, and the scalar value or a note."""

_TABLE_BLOCK_RE: Final = re.compile(
    r"<!--\s*quaestor:renderer:begin table (?P<name>\S+) -->(?P<body>.*?)<!--\s*"
    r"quaestor:renderer:end\s*-->",
    re.DOTALL,
)
"""A renderer block holding one expanded table artifact."""

_CITATION_HASH_RE: Final = re.compile(
    r"\[\[art:[0-9a-f]{8}:(?P<name>[^\]#]+)(?P<path>#[^\]]*)?\]\]"
)
"""An artifact citation, so its illustrative hash can be swapped for the rebuilt store's."""

GOLDEN_JSON_ARTIFACTS: Final[dict[str, Any]] = {
    "run.features": {
        "n": 12,
        "at_origination": 2,
        "before_period_start": 10,
        "during_period": 0,
        "after_outcome": 0,
    },
    "run.metrics": {
        "train": {"auc": 0.7538, "brier": 0.1401},
        "test": {"auc": 0.7412, "brier": 0.1428},
    },
    "run.model_summary": {
        "coefficients": [
            {"feature": "delinq_last", "value": 0.612},
            {"feature": "utilisation", "value": 0.487},
            {"feature": "delinq_count_6m", "value": 0.298},
            {"feature": "pay_ratio_mean_6m", "value": -0.244},
            {"feature": "limit_bal", "value": -0.171},
        ],
        "removed": [{"feature": "bill_last", "vif": 41.7}],
    },
    "run.splits": {
        "train": {"n": 3500, "event_rate": 0.22},
        "test": {"n": 1500, "event_rate": 0.22},
    },
    "guidance.outcomes_analysis": [
        {"doc": "SR11-7", "section_id": "V.1.c", "text": "Outcomes analysis."}
    ],
}
"""The JSON artifacts the golden's claims address by path, written from the report's own prose.

Appendix B lists these five by name and kind and prints no value for them, so unlike the scalars
they cannot be read out of the appendix. Every number below appears in the report's prose beside
the citation that addresses it: `run.features#n` is the "12 engineered features" of section 2,
`run.model_summary#removed.bill_last.vif` is its 41.7, and so on.
"""


def golden_report() -> str:
    """Return the golden report's markdown.

    Returns:
        The whole file, front matter included.
    """
    return (GOLDEN / "report.md").read_text(encoding="utf-8")


def appendix_b_scalars(report: str) -> dict[str, float]:
    """Return every scalar artifact of Appendix B, by logical name.

    Args:
        report: The golden report's markdown.

    Returns:
        Logical name to value, for the rows whose kind is ``scalar``.
    """
    scalars: dict[str, float] = {}
    for match in _APPENDIX_B_RE.finditer(report):
        if match.group("kind") != "scalar":
            continue
        scalars[match.group("name")] = float(match.group("value").strip())
    return scalars


def renderer_tables(report: str) -> dict[str, list[dict[str, str]]]:
    """Return the table artifacts the report's renderer blocks expanded.

    The printed headers are turned back into the column names the citations use: a header of
    ``event rate`` is the artifact's ``event_rate`` column, which is how
    ``[[art:...:deciles.test#1.event_rate]]`` addresses it.

    Args:
        report: The golden report's markdown.

    Returns:
        Logical name to rows, each row a mapping of column name to cell text.
    """
    tables: dict[str, list[dict[str, str]]] = {}
    for match in _TABLE_BLOCK_RE.finditer(report):
        rows = [
            line.strip()
            for line in match.group("body").splitlines()
            if line.strip().startswith("|")
        ]
        cells = [[cell.strip() for cell in row.strip("|").split("|")] for row in rows]
        header = [name.replace(" ", "_") for name in cells[0]]
        body = [row for row in cells[1:] if not set("".join(row)) <= set("-: ")]
        tables[match.group("name")] = [dict(zip(header, row, strict=True)) for row in body]
    return tables


def golden_store(root: Path) -> ArtifactStore:
    """Build a store holding every artifact the golden report cites, under its own logical names.

    Args:
        root: Where to put the store.

    Returns:
        The store: Appendix B's scalars, the two expanded tables, and the five JSON artifacts of
        :data:`GOLDEN_JSON_ARTIFACTS`.
    """
    report = golden_report()
    store = ArtifactStore(root)
    for name, value in appendix_b_scalars(report).items():
        store.put(name, value, ArtifactKind.scalar, summary=f"golden {name}")
    for name, rows in renderer_tables(report).items():
        store.put(name, rows, ArtifactKind.table, summary=f"golden {name}")
    for name, payload in GOLDEN_JSON_ARTIFACTS.items():
        store.put(name, payload, ArtifactKind.json, summary=f"golden {name}")
    return store


def rehash_citation(citation: str | None, store: ArtifactStore) -> str | None:
    """Rewrite a golden citation's illustrative hash to the one the rebuilt store produced.

    Args:
        citation: The citation text, or ``None``.
        store: The rebuilt store.

    Returns:
        The citation with each ``hash8`` replaced by the store's, or ``None``.
    """
    if citation is None:
        return None

    def swap(match: re.Match[str]) -> str:
        name = match.group("name")
        path = match.group("path") or ""
        return f"[[art:{store.artifact(name).short_hash}:{name}{path}]]"

    return _CITATION_HASH_RE.sub(swap, citation)
