"""Phase 0's only tests: the package imports, the version is what pyproject reads, the CLI runs.

These are deliberately about wiring, not behaviour. There is no behaviour yet. What they protect is
the three things a broken scaffold breaks silently: an import name that does not match the
distribution name, a version that drifts between `__init__.py` and the built metadata, and a
console-script entry point that points at a function that does not exist.
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


def test_no_implementation_code_beyond_the_phase_0_stubs() -> None:
    # Phase 0 is scaffolding. If a later phase's module lands here without its tests, this fails
    # and the run log's claim that Phase 0 shipped no implementation stops being true.
    modules = sorted(
        p.relative_to(REPO_ROOT / "src" / "quaestor").as_posix()
        for p in (REPO_ROOT / "src" / "quaestor").rglob("*.py")
    )
    assert modules == [
        "__init__.py",
        "agent/__init__.py",
        "artifacts/__init__.py",
        "cli.py",
        "corpus/__init__.py",
        "llm/__init__.py",
        "package/__init__.py",
        "report/__init__.py",
        "sandbox/__init__.py",
        "tools/__init__.py",
        "verifier/__init__.py",
    ]
