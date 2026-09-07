"""The model package: ``PackageSpec``, the ``package.yaml`` schema, the loader and its validation.

Empty in Phase 0; filled in Phase 2 from spec section 3.2. A package is the directory that
describes a subject: ``package.yaml``, the subject code under ``code/`` and optional developer
``docs/``. The loader names the offending field on every validation error, and a feature declared
``timing: after_outcome`` is an ``L1`` finding candidate before anything runs.
"""
