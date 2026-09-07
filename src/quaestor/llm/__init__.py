"""The ``LLM`` protocol, ``Completion``, the offline fakes and the two live adapters.

Empty in Phase 0; filled in Phase 2 from spec section 3.5. The protocol is structurally identical
to Probatio's ``Provider`` on purpose: Probatio's ``provider`` fixture is then a valid ``LLM``,
which is how the test layer records cassettes of Quaestor's own calls. Anthropic is the only live
provider shipped: ``AnthropicLLM`` over the SDK and ``ClaudeCLILLM`` over the Claude Code CLI.
"""
