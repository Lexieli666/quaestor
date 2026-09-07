"""Wiring, not behaviour: the package imports, the version is what pyproject reads, the CLI runs.

What these protect is the handful of things a scaffold breaks silently: an import name that does
not match the distribution name, a version that drifts between `__init__.py` and the built
metadata, and a console-script entry point that points at a function that does not exist.

Two lists here are pinned rather than derived, and each is updated by the phase that changes it, in
that phase's own commit: every module under `src/quaestor/`, so that a module landing without its
tests is a failure rather than a discovery; and `quaestor.__all__`, which spec section 9 fixes and
which grows one phase at a time.
"""

from __future__ import annotations

import importlib
import shutil
import subprocess
import sys
from importlib import metadata
from pathlib import Path

import pytest

import quaestor
from quaestor.cli import main

EXPECTED_VERSION = "0.1.0.dev0"
DISTRIBUTION = "quaestor-mrm"

# Every directory of the CLAUDE.md `src/quaestor/` layout, as an importable module name. Each is a
# real package with a docstring naming the phase that fills it; importing them here is what keeps
# an accidentally-deleted `__init__.py` from passing the gate.
SUBPACKAGES = [
    "quaestor.agent",
    "quaestor.artifacts",
    "quaestor.corpus",
    "quaestor.llm",
    "quaestor.package",
    "quaestor.report",
    "quaestor.sandbox",
    "quaestor.tools",
    "quaestor.verifier",
]

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_import_and_version() -> None:
    assert quaestor.__version__ == EXPECTED_VERSION
    assert quaestor.__doc__ is not None


def test_installed_metadata_version_matches_source() -> None:
    # hatchling reads the version out of `src/quaestor/__init__.py`; if that wiring breaks, the
    # built distribution and the source disagree and nothing else notices.
    assert metadata.version(DISTRIBUTION) == EXPECTED_VERSION


def test_console_script_entry_point_is_declared() -> None:
    scripts = metadata.entry_points(group="console_scripts")
    quaestor_scripts = [ep for ep in scripts if ep.name == "quaestor"]
    assert len(quaestor_scripts) == 1
    assert quaestor_scripts[0].value == "quaestor.cli:main"


@pytest.mark.parametrize("module_name", SUBPACKAGES)
def test_subpackage_imports_and_is_documented(module_name: str) -> None:
    module = importlib.import_module(module_name)
    assert module.__doc__ is not None, f"{module_name} has no docstring"


def test_py_typed_marker_is_shipped() -> None:
    assert (Path(quaestor.__file__).parent / "py.typed").is_file()


def test_main_prints_the_version(capsys: pytest.CaptureFixture[str]) -> None:
    assert main() == 0
    assert capsys.readouterr().out.strip() == f"quaestor {EXPECTED_VERSION}"


def test_main_ignores_arguments(capsys: pytest.CaptureFixture[str]) -> None:
    # The stub accepts an explicit argv so that Phase 9 can add a parser without changing callers.
    assert main(["--not-a-flag-yet"]) == 0
    assert capsys.readouterr().out.strip() == f"quaestor {EXPECTED_VERSION}"


def test_cli_stub_runs_as_a_subprocess() -> None:
    executable = shutil.which("quaestor")
    assert executable is not None, "the `quaestor` console script is not on PATH; pip install -e ."
    completed = subprocess.run(
        [executable],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == f"quaestor {EXPECTED_VERSION}"


def test_module_invocation_exits_zero() -> None:
    # The same code path reached the way a developer reaches it before the script is installed.
    completed = subprocess.run(
        [sys.executable, "-c", "import sys; from quaestor.cli import main; sys.exit(main())"],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == f"quaestor {EXPECTED_VERSION}"


def test_the_module_list_is_the_one_the_run_log_claims() -> None:
    # Pinned so that a module landing without its tests, or a module quietly disappearing, is a
    # failure rather than a discovery. Updated by the phase that adds a module, in that phase's
    # own commit: Phase 2 added errors, hashing, trace, findings, package/, artifacts/ and llm/;
    # Phase 3 added sandbox/contract.py and sandbox/runner.py.
    modules = sorted(
        p.relative_to(REPO_ROOT / "src" / "quaestor").as_posix()
        for p in (REPO_ROOT / "src" / "quaestor").rglob("*.py")
    )
    assert modules == [
        "__init__.py",
        "agent/__init__.py",
        "artifacts/__init__.py",
        "artifacts/citations.py",
        "artifacts/store.py",
        "cli.py",
        "corpus/__init__.py",
        "errors.py",
        "findings.py",
        "hashing.py",
        "llm/__init__.py",
        "llm/anthropic.py",
        "llm/base.py",
        "llm/claude_cli.py",
        "llm/fake.py",
        "llm/structured.py",
        "package/__init__.py",
        "package/loader.py",
        "package/spec.py",
        "report/__init__.py",
        "sandbox/__init__.py",
        "sandbox/contract.py",
        "sandbox/runner.py",
        "tools/__init__.py",
        "trace.py",
        "verifier/__init__.py",
    ]


# The public surface of spec section 9, as far as Phase 3 implements it. `Finding` arrives in
# Phase 7 and `validate` in Phase 8; both are asserted absent so that a half-built one cannot be
# mistaken for the real thing. `run_model` is on the list from Phase 3 because `CLAUDE.md` makes
# subprocess execution of a subject a hard constraint, so it is part of the surface a reader of
# the package has to be able to find.
PUBLIC_API = [
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
    "MemoryCap",
    "ModelPackage",
    "PackageError",
    "QuaestorError",
    "ReportSchemaError",
    "RunResult",
    "SandboxError",
    "Severity",
    "ToolError",
    "TraceEvent",
    "TraceReader",
    "TraceWriter",
    "VerificationError",
    "__version__",
    "load_package",
    "run_model",
    "stable_hash",
]


def test_the_public_api_is_exactly_what_phase_3_ships() -> None:
    assert quaestor.__all__ == PUBLIC_API


@pytest.mark.parametrize("symbol", PUBLIC_API)
def test_every_public_symbol_is_importable_and_documented(symbol: str) -> None:
    value = getattr(quaestor, symbol)
    if symbol != "__version__":
        assert value.__doc__, f"quaestor.{symbol} has no docstring"


@pytest.mark.parametrize("symbol", ["Finding", "validate"])
def test_the_symbols_of_a_later_phase_are_not_exported_yet(symbol: str) -> None:
    assert not hasattr(quaestor, symbol)
