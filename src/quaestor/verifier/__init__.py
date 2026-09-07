"""The claim grammar, the extractor, the deterministic matcher and grounding precision.

Empty in Phase 0; filled in Phase 7 from spec section 3.10. Extraction is an LLM call; matching is
not. A deterministic regex pre-pass finds every numeric token in a section, so the extractor cannot
lower the denominator of grounding precision by omitting a number.
"""
