"""The report's machine-readable structure, and the checks the renderer refuses to write past.

``examples/golden_report/REPORT_SCHEMA.json`` is the Phase 1 specification of a report: a JSON
Schema over the front matter, plus the ``x-quaestor-*`` structural rules that JSON Schema cannot
express over markdown -- the eleven level-2 headings in order, the required ``scope`` renderer
block, the citation forms, and the patterns a report may not contain. The renderer needs all of it
at runtime and ``examples/`` is not shipped inside the wheel, so the file is **copied into the
package** as ``report_schema.json`` and read from there, exactly as the regulatory corpus is; the
two copies are pinned byte-for-byte by ``tests/test_report_schema.py``, so a sanctioned edit to
the golden schema under D-011 that forgot the copy is a failing test rather than a renderer that
enforces last month's rules (DECISIONS D-074).

:func:`check_front_matter` and :func:`check_structure` are the refusals of spec section 3.11 and
of the schema's own ``x-quaestor-refusal-rules``: schema-invalid front matter, a missing Appendix
A, a missing grounding figure, and -- under ``full_agent`` -- a number in the prose that no
verified claim covers and that nothing wrapped.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Final

import jsonschema
import yaml

from ..errors import ReportSchemaError
from ..vocab import Configuration

__all__ = [
    "APPENDIX_A_HEADING",
    "SCHEMA_FILE",
    "REPORT_SCHEMA",
    "REQUIRED_HEADINGS",
    "check_front_matter",
    "check_structure",
    "front_matter_of",
    "required_renderer_blocks",
]

SCHEMA_FILE: Final = Path(__file__).with_name("report_schema.json")
"""The packaged copy of ``examples/golden_report/REPORT_SCHEMA.json``, read once at import."""

REPORT_SCHEMA: Final[dict[str, Any]] = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
"""``examples/golden_report/REPORT_SCHEMA.json``, shipped so that the renderer carries its rules."""


REQUIRED_HEADINGS: Final[tuple[str, ...]] = tuple(REPORT_SCHEMA["x-quaestor-required-headings"])
"""The eleven level-2 headings, in order; the report may hold no other."""

APPENDIX_A_HEADING: Final = "## Appendix A — Claims"
"""The appendix the renderer refuses to write a report without."""

RENDERER_BLOCK_RE: Final = re.compile(REPORT_SCHEMA["x-quaestor-renderer-block-pattern"])
"""A renderer block: the scope block, or one expanded table."""

ARTIFACT_CITATION_RE: Final = re.compile(REPORT_SCHEMA["x-quaestor-citation-patterns"]["artifact"])
"""A well-formed ``[[art:...]]`` citation."""

REGULATORY_CITATION_RE: Final = re.compile(
    REPORT_SCHEMA["x-quaestor-citation-patterns"]["regulatory"]
)
"""A well-formed ``[[reg:...]]`` citation."""

ANY_TOKEN_RE: Final = re.compile(r"\[\[[^\]]+\]\]")
"""Anything written in double brackets, well-formed or not."""


def required_renderer_blocks() -> list[Mapping[str, Any]]:
    """Return the renderer blocks every report must carry.

    Returns:
        One mapping per required block, each naming where it goes and how it opens and closes.
    """
    return list(REPORT_SCHEMA["x-quaestor-required-renderer-blocks"])


def front_matter_of(report: str) -> dict[str, Any]:
    """Parse a report's YAML front matter.

    Args:
        report: The whole of ``report.md``.

    Returns:
        The front matter as a plain dict.

    Raises:
        ReportSchemaError: The report does not begin with a YAML front-matter block.
    """
    parts = report.split("---\n")
    if len(parts) < 3 or parts[0].strip():
        raise ReportSchemaError(
            "a report begins with a YAML front-matter block delimited by ---; this one does not"
        )
    loaded = yaml.safe_load(parts[1])
    if not isinstance(loaded, dict):
        raise ReportSchemaError("the report's front matter is not a mapping of keys to values")
    return loaded


def check_front_matter(front: Mapping[str, Any]) -> list[str]:
    """Validate the front matter against the schema and against the two refusal rules.

    Args:
        front: The parsed front matter.

    Returns:
        One message per problem, empty when there is none.
    """
    problems: list[str] = []
    validator = jsonschema.Draft202012Validator(REPORT_SCHEMA)
    for error in sorted(validator.iter_errors(dict(front)), key=str):
        where = ".".join(str(part) for part in error.absolute_path) or "<front matter>"
        problems.append(f"front matter {where}: {error.message}")
    for key in ("grounding_precision_pre", "grounding_precision_post"):
        if front.get(key) is None:
            problems.append(
                f"the front matter carries no {key}; a report prints both grounding precision "
                "figures or it is not written"
            )
    return problems


def check_structure(
    report: str,
    *,
    configuration: Configuration,
    uncovered: Sequence[str] = (),
) -> list[str]:
    """Check a rendered report's headings, citations, appendices and forbidden patterns.

    Args:
        report: The whole of ``report.md``.
        configuration: Which configuration wrote it; the wrapper rule binds ``full_agent``.
        uncovered: Numeric tokens of the prose that no verified claim covers and that nothing
            wrapped, as the renderer computed them.

    Returns:
        One message per problem, empty when there is none.
    """
    problems: list[str] = []
    headings = [line for line in report.splitlines() if line.startswith("## ")]
    if headings != list(REQUIRED_HEADINGS):
        problems.append(
            f"the report's level-2 headings are {headings}, not the eleven "
            f"docs/REPORT_SCHEMA.md fixes, in order"
        )
    if APPENDIX_A_HEADING not in report:
        problems.append(
            f"the report has no {APPENDIX_A_HEADING!r}; a report without its claims appendix is "
            "a report whose numbers cannot be audited"
        )
    for block in required_renderer_blocks():
        if str(block["begin"]) not in report:
            problems.append(f"the report has no {block['name']} renderer block")
    bad = [
        token
        for token in ANY_TOKEN_RE.findall(report)
        if not (ARTIFACT_CITATION_RE.fullmatch(token) or REGULATORY_CITATION_RE.fullmatch(token))
    ]
    if bad:
        problems.append(f"these double-bracket tokens are not well-formed citations: {bad}")
    problems.extend(_forbidden(report))
    if configuration is Configuration.full_agent and uncovered:
        problems.append(
            f"these numbers in the prose are covered by no verified claim and are not wrapped "
            f"{'⟦unverified: …⟧'}: {list(uncovered)}"
        )
    return problems


def _forbidden(report: str) -> list[str]:
    """Apply the schema's forbidden patterns, each inside the scope it declares."""
    problems: list[str] = []
    for rule in REPORT_SCHEMA["x-quaestor-forbidden-patterns"]:
        scope = str(rule["scope"])
        text = report if scope == "whole report" else _appendices_c_and_d(report)
        found = re.findall(str(rule["pattern"]), text, flags=re.I)
        if found:
            problems.append(f"{sorted(set(found))} in {scope}: {rule['why']}")
    return problems


def _appendices_c_and_d(report: str) -> str:
    """Return Appendix C and Appendix D, the scope of the citation-leak rule."""
    marker = "## Appendix C"
    return report.split(marker, 1)[1] if marker in report else ""
