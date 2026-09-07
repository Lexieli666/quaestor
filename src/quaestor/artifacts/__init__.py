"""The content-addressed artifact store, its index and the citation syntax.

Empty in Phase 0; filled in Phase 2 from spec section 3.4. Payload bytes are canonical so that
identical results hash identically across runs and processes, which is what makes a citation
``[[art:<hash8>:<logical_name>]]`` checkable rather than decorative.
"""
