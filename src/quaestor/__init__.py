"""Quaestor: an agentic model-validation copilot.

Quaestor takes a model package -- code, a data reference, fitted artifacts and the developer's own
claims -- runs a fixed set of deterministic checks over it, and drafts an SR 11-7-shaped validation
report in which every quantitative claim carries a machine-checked citation to a computed artifact.
Findings are structured objects that cannot exist without evidence; the report prints its grounding
precision before and after repair. Quaestor is not a compliance product and makes no claim of
compliance or certification.

What this module exports grows with the phases that implement it. Phase 0 is scaffolding only, so
``__version__`` is the sole public name; spec section 9 fixes the eventual public surface
(``ModelPackage``, ``load_package``, ``ArtifactStore``, ``LLM``, ``Completion``, ``FakeLLM``,
``Finding``, ``DefectClass``, ``validate`` and the error hierarchy).

``__version__`` is the single source of truth for the distribution version, which
``pyproject.toml`` reads through hatchling. The distribution is named ``quaestor-mrm`` because the
PyPI name ``quaestor`` belongs to an unrelated project; the import name is ``quaestor``
(DECISIONS D-002).
"""

from __future__ import annotations

__version__ = "0.1.0.dev0"

__all__ = ["__version__"]
