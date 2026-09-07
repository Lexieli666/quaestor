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
MSR_PREPAYMENT = SUBJECTS / "msr_prepayment"


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


@pytest.fixture(scope="session")
def msr_synthetic() -> ModuleType:
    """`subjects/msr_prepayment/synthetic.py`, which re-exports the generating process."""
    return load_module("msr_prepayment_subject_synthetic", MSR_PREPAYMENT / "synthetic.py")


@pytest.fixture(scope="session")
def msr_features(msr_synthetic: ModuleType) -> ModuleType:
    """`subjects/msr_prepayment/code/features.py`: the panel, the splits, the spline, the screen."""
    module = msr_synthetic.load_code_module("features")
    assert isinstance(module, ModuleType)
    return module


@pytest.fixture(scope="session")
def msr_process(msr_synthetic: ModuleType) -> ModuleType:
    """`subjects/msr_prepayment/code/synthetic.py`: the generating process, in full."""
    module = msr_synthetic.load_code_module("synthetic")
    assert isinstance(module, ModuleType)
    return module


@pytest.fixture(scope="session")
def msr_projection(msr_synthetic: ModuleType) -> ModuleType:
    """`subjects/msr_prepayment/code/projection.py`: the rate-shock roll-forward."""
    module = msr_synthetic.load_code_module("projection")
    assert isinstance(module, ModuleType)
    return module


@pytest.fixture(scope="session")
def msr_run() -> ModuleType:
    """`subjects/msr_prepayment/code/run.py`: the entrypoint, for its declarations and helpers."""
    synthetic = load_module("msr_prepayment_subject_synthetic", MSR_PREPAYMENT / "synthetic.py")
    module = synthetic.load_code_module("run")
    assert isinstance(module, ModuleType)
    return module


@pytest.fixture(scope="session")
def msr_sample() -> ModuleType:
    """`subjects/msr_prepayment/sample_freddie.py`, covered for arguments and the column map."""
    return load_module("msr_prepayment_subject_sample", MSR_PREPAYMENT / "sample_freddie.py")


# --- Phase 5: one clean run of each subject, and the variants the tool tests perturb -------------
#
# A tool reads the spec 3.3 contract and nothing else, so a rule can be tested by running the real
# subject once and then perturbing the files it wrote -- an `after_outcome` timing, a duplicated
# row, a shifted split, a reintroduced collinear column, a false declared threshold, a sign-flipped
# projection. That is a truer test than a hand-written frame: the negative case is the subject as
# it actually is, and the positive case differs from it by one edit a reader can name.


@pytest.fixture(scope="session")
def credit_run_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Run the synthetic `credit_default` subject once and return the directory it wrote."""
    from quaestor import load_package, run_model

    out_dir = tmp_path_factory.mktemp("tools_credit") / "run"
    run_model(load_package(CREDIT_DEFAULT), None, out_dir, synthetic=5000)
    return out_dir


@pytest.fixture(scope="session")
def msr_run_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Run the synthetic `msr_prepayment` subject once and return the directory it wrote."""
    from quaestor import load_package, run_model

    out_dir = tmp_path_factory.mktemp("tools_msr") / "run"
    run_model(load_package(MSR_PREPAYMENT), None, out_dir, synthetic=2000)
    return out_dir
