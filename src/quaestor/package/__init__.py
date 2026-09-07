"""The model package: ``PackageSpec``, the ``package.yaml`` schema, the loader and its validation.

Filled in Phase 2 from spec section 3.2. A package is the directory that
describes a subject: ``package.yaml``, the subject code under ``code/`` and optional developer
``docs/``. The loader names the offending field on every validation error, and a feature declared
``timing: after_outcome`` is an ``L1`` finding candidate before anything runs.
"""

from __future__ import annotations

from .loader import MANIFEST_FIX, PACKAGE_FILE, ModelPackage, load_package
from .spec import (
    ConvexityExpectation,
    DataSpec,
    DeveloperClaim,
    Feature,
    FeatureTiming,
    ModelType,
    PackageSpec,
    RegimeSpec,
    RuntimeSpec,
    ScenariosSpec,
    SplitRule,
    SplitsSpec,
    ThresholdSpec,
)

__all__ = [
    "MANIFEST_FIX",
    "PACKAGE_FILE",
    "ConvexityExpectation",
    "DataSpec",
    "DeveloperClaim",
    "Feature",
    "FeatureTiming",
    "ModelPackage",
    "ModelType",
    "PackageSpec",
    "RegimeSpec",
    "RuntimeSpec",
    "ScenariosSpec",
    "SplitRule",
    "SplitsSpec",
    "ThresholdSpec",
    "load_package",
]
