"""The tool registry and one module per tool.

Empty in Phase 0; filled in Phase 5 from spec section 3.7. Each tool declares a pydantic ``Args``
model from which the JSON schema is generated once and consumed by three callers -- the planner,
the MCP server and the CLI -- and returns artifacts plus finding candidates drawn from the fixed
class list ``L1 L2 R1 C1 S1 M1 D1 T1 O1 E1 X1 R0``.
"""
