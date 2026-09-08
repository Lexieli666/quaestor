"""The planner: a rule-based check list plus a bounded JSON-action loop.

Filled in Phase 8 from spec section 3.12. The rule-based plan is derived from ``model_type`` and
``package.yaml``; under ``full_agent`` a follow-up loop of at most four steps may request further
tool calls, and it can neither name an unknown tool nor reach a path outside the package.
"""

from __future__ import annotations

from .planner import (
    GUIDANCE_TOOL,
    MAX_FOLLOW_UP_STEPS,
    PLAN_PURPOSE,
    FollowUpAction,
    PlannedCall,
    PlanStep,
    follow_up_plan,
    guidance_queries,
    rule_based_plan,
    validate_action,
)

__all__ = [
    "GUIDANCE_TOOL",
    "MAX_FOLLOW_UP_STEPS",
    "PLAN_PURPOSE",
    "FollowUpAction",
    "PlanStep",
    "PlannedCall",
    "follow_up_plan",
    "guidance_queries",
    "rule_based_plan",
    "validate_action",
]
