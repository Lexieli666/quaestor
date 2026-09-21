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

EXPECTED_VERSION = "0.1.0"  # Phase 16: the release; `tests/test_docs_provenance.py` pins it
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
    # Phase 9 turned the version stub into a parser, so the version is a flag rather than the
    # program's whole behaviour; `--version` is argparse's action, which exits rather than returns.
    with pytest.raises(SystemExit) as raised:
        main(["--version"])
    assert raised.value.code == 0
    assert capsys.readouterr().out.strip() == f"quaestor {EXPECTED_VERSION}"


def test_main_with_no_command_is_a_usage_error(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as raised:
        main([])
    assert raised.value.code == 2
    assert "fix: quaestor --help" in capsys.readouterr().err


def test_the_console_script_runs_as_a_subprocess() -> None:
    executable = shutil.which("quaestor")
    assert executable is not None, "the `quaestor` console script is not on PATH; pip install -e ."
    completed = subprocess.run(
        [executable, "--version"],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == f"quaestor {EXPECTED_VERSION}"


def test_module_invocation_reaches_the_same_parser() -> None:
    # The same code path reached the way a developer reaches it before the script is installed.
    completed = subprocess.run(
        [sys.executable, "-m", "quaestor.cli", "--version"],
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
    # Phase 3 added sandbox/contract.py and sandbox/runner.py; Phase 5 added the eight tool
    # modules of tools/ plus its registry, thresholds, frames and hand-written statistics; Phase 6
    # added corpus/bm25.py, corpus/documents.py, corpus/ingest.py and tools/guidance.py; Phase 7
    # added vocab.py and the six modules of verifier/; Phase 8 added agent/planner.py, configs.py,
    # pipeline.py and the five modules of report/; Phase 9 added llm/offline.py (the provider
    # behind `--llm fake`) and llm/recording.py, and turned cli.py from a stub into a parser.
    modules = sorted(
        p.relative_to(REPO_ROOT / "src" / "quaestor").as_posix()
        for p in (REPO_ROOT / "src" / "quaestor").rglob("*.py")
    )
    assert modules == [
        "__init__.py",
        "agent/__init__.py",
        "agent/planner.py",
        "artifacts/__init__.py",
        "artifacts/citations.py",
        "artifacts/store.py",
        "cli.py",
        "configs.py",
        "corpus/__init__.py",
        "corpus/bm25.py",
        "corpus/documents.py",
        "corpus/ingest.py",
        "errors.py",
        "findings.py",
        "hashing.py",
        "llm/__init__.py",
        "llm/anthropic.py",
        "llm/base.py",
        "llm/claude_cli.py",
        "llm/fake.py",
        "llm/offline.py",
        "llm/recording.py",
        "llm/structured.py",
        "package/__init__.py",
        "package/loader.py",
        "package/spec.py",
        "pipeline.py",
        "report/__init__.py",
        "report/drafter.py",
        "report/renderer.py",
        "report/repair.py",
        "report/schema.py",
        "report/sections.py",
        "sandbox/__init__.py",
        "sandbox/contract.py",
        "sandbox/runner.py",
        "tools/__init__.py",
        "tools/challenger.py",
        "tools/collinearity.py",
        "tools/frames.py",
        "tools/guidance.py",
        "tools/leakage.py",
        "tools/metrics.py",
        "tools/profiler.py",
        "tools/registry.py",
        "tools/run.py",
        "tools/scenarios.py",
        "tools/stability.py",
        "tools/stats.py",
        "tools/thresholds.py",
        "trace.py",
        "verifier/__init__.py",
        "verifier/claim.py",
        "verifier/claims_doc.py",
        "verifier/developer.py",
        "verifier/extract.py",
        "verifier/grounding.py",
        "verifier/match.py",
        "verifier/tokens.py",
        "vocab.py",
    ]


# The public surface of spec section 9, complete as of Phase 8, which adds `validate` -- the
# pipeline entry section 9 names -- with `ValidationRun`, `ConfigSpec` and `CONFIGURATIONS` beside
# it, because a caller that cannot name a configuration cannot ask for one.
# `run_model` is on the list from Phase 3 because `CLAUDE.md` makes subprocess execution of a
# subject a hard constraint, so it is part of the surface a reader of the package has to be able
# to find; `Finding`, the claim grammar and the two persisted documents joined it in Phase 7,
# because a caller that cannot name a finding or a claim cannot check either one.
PUBLIC_API = [
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


def test_the_public_api_is_exactly_what_phase_8_ships() -> None:
    assert quaestor.__all__ == PUBLIC_API


@pytest.mark.parametrize("symbol", PUBLIC_API)
def test_every_public_symbol_is_importable_and_documented(symbol: str) -> None:
    value = getattr(quaestor, symbol)
    if symbol != "__version__":
        assert value.__doc__, f"quaestor.{symbol} has no docstring"


def test_the_pipeline_entry_of_spec_section_9_is_now_exported() -> None:
    # Phases 2 to 7 asserted `validate` absent, so that a half-built one could not be mistaken for
    # the real thing. Phase 8 builds it; the assertion turns over rather than being deleted.
    assert callable(quaestor.validate)
    assert quaestor.validate.__doc__
