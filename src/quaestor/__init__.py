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
:func:`~quaestor.hashing.stable_hash`; Phase 3 adds :func:`~quaestor.sandbox.run_model`.
Phase 7 adds ``Finding`` and the claim verifier; Phase 8 adds :func:`~quaestor.pipeline.validate`,
the pipeline entry of spec section 9, and the three configurations it runs under.

``__version__`` is the single source of truth for the distribution version, which
``pyproject.toml`` reads through hatchling. The distribution is named ``quaestor-mrm`` because the
PyPI name ``quaestor`` belongs to an unrelated project; the import name is ``quaestor``
(DECISIONS D-002).
"""

from __future__ import annotations

from .artifacts import Artifact, ArtifactStore
from .configs import CONFIGURATIONS, ConfigSpec
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
from .findings import DefectClass, Finding, FindingCandidate, FindingsDocument, Severity
from .hashing import stable_hash
from .llm import LLM, Completion, FakeLLM
from .package import ModelPackage, load_package
from .pipeline import ValidationRun, validate
from .sandbox import MemoryCap, RunResult, run_model
from .trace import EventType, TraceEvent, TraceReader, TraceWriter
from .verifier import Claim, ClaimsDocument, ClaimStatus, VerifiedClaim
from .vocab import Configuration, ReportSection

__version__ = "0.1.0"

__all__ = [
    "LLM",
    "Artifact",
    "ArtifactError",
    "ArtifactStore",
    "Claim",
    "ClaimStatus",
    "ClaimsDocument",
    "CONFIGURATIONS",
    "Completion",
    "ConfigSpec",
    "Configuration",
    "DefectClass",
    "EventType",
    "FakeLLM",
    "Finding",
    "FindingCandidate",
    "FindingsDocument",
    "LLMOutputError",
    "LLMProviderError",
    "MemoryCap",
    "ModelPackage",
    "PackageError",
    "QuaestorError",
    "ReportSchemaError",
    "ReportSection",
    "RunResult",
    "SandboxError",
    "Severity",
    "ToolError",
    "TraceEvent",
    "TraceReader",
    "TraceWriter",
    "ValidationRun",
    "VerificationError",
    "VerifiedClaim",
    "__version__",
    "load_package",
    "run_model",
    "stable_hash",
    "validate",
]
