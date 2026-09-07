"""The planner: a rule-based check list plus a bounded JSON-action loop.

Empty in Phase 0; filled in Phase 8 from spec section 3.12. The rule-based plan is derived from
``model_type`` and ``package.yaml``; under ``full_agent`` a follow-up loop of at most four steps may
request further tool calls, and it can neither name an unknown tool nor reach a path outside the
package.
"""
