"""The vocabulary the three persisted documents share: section identifiers and configurations.

``report.md``'s front matter, ``claims.json`` and ``findings.json`` all name the same seven
sections and the same three configurations, and the two JSON Schemas of
``examples/golden_report/`` spell both enums out. One spelling of each therefore has to exist
somewhere every writer of those files can import.

That somewhere is not ``report/`` and not ``configs.py``. Phase 8 fills both of those with code
that imports :mod:`quaestor.findings`, :mod:`quaestor.verifier` and :mod:`quaestor.tools`, and
those modules need the two enums now, so putting the vocabulary in either would make the import
graph a cycle. A module with no imports of its own cannot (DECISIONS D-060).
"""

from __future__ import annotations

from enum import StrEnum
from typing import Final

__all__ = ["SECTION_ORDER", "Configuration", "ReportSection"]


class ReportSection(StrEnum):
    """The seven drafted sections, by the identifier ``claims.json`` and ``findings.json`` use.

    ``docs/REPORT_SCHEMA.md`` section 3 fixes the identifiers; the four appendices are rendered
    rather than drafted and so are not sections a claim or a finding can belong to.

    Attributes:
        summary: Summary and scope.
        conceptual_soundness: Design, features and their timing, effective challenge.
        data_integrity: Profiles, missingness, drift.
        outcomes: Metrics by split, calibration, the threshold table.
        sensitivity: Stability by regime, collinearity, scenarios.
        findings: The findings themselves, severity-ordered.
        monitoring: Ongoing monitoring recommendations.
    """

    summary = "summary"
    conceptual_soundness = "conceptual_soundness"
    data_integrity = "data_integrity"
    outcomes = "outcomes"
    sensitivity = "sensitivity"
    findings = "findings"
    monitoring = "monitoring"


SECTION_ORDER: Final = tuple(ReportSection)
"""The sections in report order, which is the order Appendix A and the per-section table use."""


class Configuration(StrEnum):
    """The three configurations spec section 3.13 compares in the study.

    Attributes:
        full_agent: The product: rule-based plan plus a bounded follow-up loop, an LLM per
            section with citations, the verifier on with repair.
        rules_only: The deterministic checks alone, template narrative, no model call.
        plain_llm: One model call over the raw artifacts, no tools and no repair.
    """

    full_agent = "full_agent"
    rules_only = "rules_only"
    plain_llm = "plain_llm"
