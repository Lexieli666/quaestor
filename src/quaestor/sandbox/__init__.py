"""``run_model``: executing a subject in a capped subprocess.

Empty in Phase 0; filled in Phase 3 from spec section 3.6. A subject is never imported into the
validator's process: it runs in a subprocess with a scrubbed environment, a wall-clock cap, a
memory cap and networking disabled, and every file of the standard artifact contract is checked
for presence and schema afterwards.
"""
