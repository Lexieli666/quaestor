"""Quaestor: an agentic model-validation copilot.

Quaestor takes a model package -- code, a data reference, fitted artifacts and the developer's own
claims -- runs a fixed set of deterministic checks over it, and drafts an SR 11-7-shaped validation
report in which every quantitative claim carries a machine-checked citation to a computed artifact.
Findings are structured objects that cannot exist without evidence; the report prints its grounding
precision before and after repair. Quaestor is not a compliance product and makes no claim of
compliance or certification.

What this module exports grows with the phases that implement it. Spec section 9 fixes the
eventual public surface; Phase 2 ships everything on that list that now exists -- the package
loader, the artifact store, the LLM layer, the defect vocabulary, the errors and
:func:`~quaestor.hashing.stable_hash`. ``Finding`` arrives in Phase 7 and ``validate`` in Phase 8.

``__version__`` is the single source of truth for the distribution version, which
``pyproject.toml`` reads through hatchling. The distribution is named ``quaestor-mrm`` because the
PyPI name ``quaestor`` belongs to an unrelated project; the import name is ``quaestor``
(DECISIONS D-002).
"""

from __future__ import annotations

from .artifacts import Artifact, ArtifactStore
from .errors import (
    ArtifactError,
    LLMOutputError,
    LLMProviderError,
    PackageError,
    QuaestorError,
    ReportSchemaError,
    SandboxError,
    ToolError,
    VerificationError,
)
from .findings import DefectClass, FindingCandidate, Severity
from .hashing import stable_hash
from .llm import LLM, Completion, FakeLLM
from .package import ModelPackage, load_package
from .trace import EventType, TraceEvent, TraceReader, TraceWriter

__version__ = "0.1.0.dev0"

__all__ = [
    "LLM",
    "Artifact",
    "ArtifactError",
    "ArtifactStore",
    "Completion",
    "DefectClass",
    "EventType",
    "FakeLLM",
    "FindingCandidate",
    "LLMOutputError",
    "LLMProviderError",
    "ModelPackage",
    "PackageError",
    "QuaestorError",
    "ReportSchemaError",
    "SandboxError",
    "Severity",
    "ToolError",
    "TraceEvent",
    "TraceReader",
    "TraceWriter",
    "VerificationError",
    "__version__",
    "load_package",
    "stable_hash",
]
