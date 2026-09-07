# Quaestor

SR 11-7-shaped, not a compliance product, no bank data.

Quaestor is an agentic model-validation copilot: it takes a model package — the subject's code, a
reference to its data, its fitted artifacts and the developer's own claims — runs a fixed set of
deterministic checks over it in a capped subprocess, and drafts a validation report shaped after
the sections of SR 11-7, in which every quantitative claim carries a machine-checked citation to a
computed artifact, every finding is a structured object that cannot be constructed without evidence
artifacts, and the report prints its own grounding precision before and after repair. What makes it
worth reading rather than another wrapper is the open evaluation: defects are seeded into the
author's own rebuilt models, and detection precision and recall, the false-alarm rate and
per-report grounding precision are published, misses included.

Scaffolding only at this commit; nothing runs yet. `PROGRESS.md` is the build order.
