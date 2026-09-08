"""The section plan, the drafter, the repair loop and the renderer.

Empty in Phase 0; filled in Phase 8 from spec section 3.11. The renderer refuses to write a report
that lacks its claims appendix or either grounding-precision figure, and a claim that survives two
repair rounds unverified stays in the prose wrapped so a reader sees it.
"""

from __future__ import annotations

from .drafter import (
    DRAFT_INSTRUCTION,
    DRAFT_PURPOSE,
    REPAIR_INSTRUCTION,
    DraftedSection,
    Drafter,
    GuidanceSpan,
    finding_heading,
    merge_candidates,
    spans_from_payload,
    template_section,
)
from .renderer import (
    APPENDICES,
    NotChecked,
    ReportInputs,
    check_report,
    drafted_body,
    front_matter,
    render_report,
    scope_block,
    uncovered_numbers,
    write_report,
)
from .repair import (
    MAX_REPAIR_ROUNDS,
    UNVERIFIED_CLOSE,
    UNVERIFIED_OPEN,
    DraftInputs,
    RepairOutcome,
    SectionDraft,
    repair_sections,
    wrap_unverified,
    wrapped_values,
)
from .schema import (
    APPENDIX_A_HEADING,
    REPORT_SCHEMA,
    REQUIRED_HEADINGS,
    check_front_matter,
    check_structure,
    front_matter_of,
)
from .sections import (
    DEFECT_CLASS_NAMES,
    SECTION_BRIEFS,
    ArtifactBrief,
    SectionBrief,
    artifact_briefs,
    brief_for,
    calibration_before_discrimination,
    ordered_briefs,
    section_heading,
    written_number,
)

__all__ = [
    "APPENDICES",
    "APPENDIX_A_HEADING",
    "DEFECT_CLASS_NAMES",
    "DRAFT_INSTRUCTION",
    "DRAFT_PURPOSE",
    "MAX_REPAIR_ROUNDS",
    "REPAIR_INSTRUCTION",
    "REPORT_SCHEMA",
    "REQUIRED_HEADINGS",
    "SECTION_BRIEFS",
    "UNVERIFIED_CLOSE",
    "UNVERIFIED_OPEN",
    "ArtifactBrief",
    "DraftInputs",
    "DraftedSection",
    "Drafter",
    "GuidanceSpan",
    "NotChecked",
    "RepairOutcome",
    "ReportInputs",
    "SectionBrief",
    "SectionDraft",
    "artifact_briefs",
    "brief_for",
    "calibration_before_discrimination",
    "check_front_matter",
    "check_report",
    "check_structure",
    "drafted_body",
    "finding_heading",
    "front_matter",
    "front_matter_of",
    "merge_candidates",
    "ordered_briefs",
    "render_report",
    "repair_sections",
    "scope_block",
    "section_heading",
    "spans_from_payload",
    "template_section",
    "uncovered_numbers",
    "wrap_unverified",
    "wrapped_values",
    "write_report",
    "written_number",
]
