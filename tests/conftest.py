"""Shared test support: loading a subject's own modules without shadowing `code`.

A subject's entrypoint is `python -m code.run`, so its implementation lives in a package literally
named `code`, which shadows the standard library module of that name. Inside the sandbox's
subprocess that is harmless and is what spec section 3.2 asks for. Inside the test process it
would last for the whole session, so nothing here ever puts a subject directory on `sys.path`:
each module is loaded from its path under a name of its own, which also keeps the second subject's
`synthetic.py` (Phase 4) from colliding with the first one's.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SUBJECTS = REPO_ROOT / "subjects"
CREDIT_DEFAULT = SUBJECTS / "credit_default"


def load_module(alias: str, path: Path) -> ModuleType:
    """Load one standalone module from its path, under an alias, and cache it in `sys.modules`."""
    if alias in sys.modules:
        return sys.modules[alias]
    spec = importlib.util.spec_from_file_location(alias, path)
    assert spec is not None and spec.loader is not None, f"{path} is not importable"
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def credit_synthetic() -> ModuleType:
    """`subjects/credit_default/synthetic.py`, which re-exports the generating process."""
    return load_module("credit_default_subject_synthetic", CREDIT_DEFAULT / "synthetic.py")


@pytest.fixture(scope="session")
def credit_features(credit_synthetic: ModuleType) -> ModuleType:
    """`subjects/credit_default/code/features.py`: the twelve features, the split, the screen."""
    module = credit_synthetic.load_code_module("features")
    assert isinstance(module, ModuleType)
    return module


@pytest.fixture(scope="session")
def credit_sample() -> ModuleType:
    """`subjects/credit_default/sample.py`, covered for argument handling only."""
    return load_module("credit_default_subject_sample", CREDIT_DEFAULT / "sample.py")
