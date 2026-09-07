"""The tool registry and one module per tool.

Filled in Phase 5 from spec section 3.7. Each tool declares a pydantic ``Args`` model from which
the JSON schema is generated once and consumed by three callers -- the planner, the MCP server and
the CLI -- and returns artifacts plus finding candidates drawn from the fixed class list
``L1 L2 R1 C1 S1 M1 D1 T1 O1 E1 X1 R0``.

All nine of spec section 3.7's tools are registered by :func:`default_registry` from Phase 6 on.
``retrieve_guidance`` was deliberately absent in Phase 5, because it needs the regulatory corpus
and its BM25 index and a stub that returned no spans would have looked to a planner like guidance
that had been retrieved; the corpus arrived with Phase 6 and the tool with it.
"""

from __future__ import annotations

from typing import Any

from .challenger import ChallengerCompareTool
from .collinearity import CheckCollinearityTool
from .guidance import RetrieveGuidanceTool, guidance_name
from .leakage import CheckLeakageTool
from .metrics import ComputeMetricsTool, Subpopulation
from .profiler import ProfileDataTool
from .registry import Tool, ToolArgs, ToolContext, ToolRegistry, ToolResult
from .run import RunModelTool
from .scenarios import RunScenariosTool
from .stability import CheckStabilityTool
from .thresholds import DEFAULT_THRESHOLDS, Thresholds, package_threshold_names

__all__ = [
    "DEFAULT_THRESHOLDS",
    "ChallengerCompareTool",
    "CheckCollinearityTool",
    "CheckLeakageTool",
    "CheckStabilityTool",
    "ComputeMetricsTool",
    "ProfileDataTool",
    "RetrieveGuidanceTool",
    "RunModelTool",
    "RunScenariosTool",
    "Subpopulation",
    "Thresholds",
    "Tool",
    "ToolArgs",
    "ToolContext",
    "ToolRegistry",
    "ToolResult",
    "default_registry",
    "guidance_name",
    "package_threshold_names",
]


def default_registry() -> ToolRegistry:
    """Return a registry holding every tool this phase ships, in the order a plan runs them.

    Returns:
        The registry. ``run_model`` first, because everything else reads what it wrote; then the
        checks, in the order the report's sections need them; ``retrieve_guidance`` last, because
        it reads nothing a run produced and every section calls it.
    """
    tools: list[Tool[Any]] = [
        RunModelTool(),
        ProfileDataTool(),
        ComputeMetricsTool(),
        CheckLeakageTool(),
        CheckStabilityTool(),
        CheckCollinearityTool(),
        ChallengerCompareTool(),
        RunScenariosTool(),
        RetrieveGuidanceTool(),
    ]
    return ToolRegistry(tools)
