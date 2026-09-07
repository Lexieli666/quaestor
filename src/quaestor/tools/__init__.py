"""The tool registry and one module per tool.

Filled in Phase 5 from spec section 3.7. Each tool declares a pydantic ``Args`` model from which
the JSON schema is generated once and consumed by three callers -- the planner, the MCP server and
the CLI -- and returns artifacts plus finding candidates drawn from the fixed class list
``L1 L2 R1 C1 S1 M1 D1 T1 O1 E1 X1 R0``.

Eight of spec section 3.7's nine tools are registered by :func:`default_registry`. The ninth,
``retrieve_guidance``, needs the regulatory corpus and its BM25 index, which arrive in Phase 6;
nothing is registered for it here, so a planner that asks for it is refused by name and the
refusal is traced, rather than getting a stub that returns no guidance and looks as though it
worked.
"""

from __future__ import annotations

from typing import Any

from .challenger import ChallengerCompareTool
from .collinearity import CheckCollinearityTool
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
    "package_threshold_names",
]


def default_registry() -> ToolRegistry:
    """Return a registry holding every tool this phase ships, in the order a plan runs them.

    Returns:
        The registry. ``run_model`` first, because everything else reads what it wrote; then the
        checks, in the order the report's sections need them.
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
    ]
    return ToolRegistry(tools)
