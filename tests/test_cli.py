"""Phase 9: the command line, run the way a user runs it — as a subprocess, from a shell.

The load-bearing test is the first one. `CLAUDE.md`'s command list ends with

    quaestor validate subjects/credit_default --synthetic --llm fake --out /tmp/r

and until this phase that line could not be run at all: gate condition 5b has been recorded as
"not applicable" in every run-log line since Phase 1. Here it runs, on both subjects, through the
installed console script, and the report it writes is checked by the same rules the renderer
refuses on.

Everything is offline. `--llm fake` is `quaestor.llm.OfflineLLM`, which ships inside the package
precisely so that this line needs no network, no key and no subscription (D-080), and every run
here is `--synthetic`.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

import pytest

from quaestor import Configuration, cli, load_package
from quaestor.cli import (
    EXIT_FAILED_RUN,
    EXIT_OK,
    EXIT_USAGE,
    _capped,
    _live_provider,
    _synthetic_n,
    build_parser,
    main,
)
from quaestor.configs import synthetic_default_n
from quaestor.corpus.documents import Source
from quaestor.errors import CorpusError
from quaestor.report import check_report
from quaestor.verifier import ClaimsDocument

REPO_ROOT = Path(__file__).resolve().parents[1]
CREDIT = REPO_ROOT / "subjects" / "credit_default"
MSR = REPO_ROOT / "subjects" / "msr_prepayment"
SMALL = 600
"""Rows for the runs whose subject is beside the point; the two gate runs use the real defaults."""


def quaestor(*argv: str, timeout: int = 600) -> subprocess.CompletedProcess[str]:
    """Run the installed console script as a user would, and return the completed process."""
    executable = shutil.which("quaestor")
    assert executable is not None, "the `quaestor` console script is not on PATH; pip install -e ."
    return subprocess.run(
        [executable, *argv], capture_output=True, text=True, timeout=timeout, check=False
    )


def run(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, str, str]:
    """Call `main` in this process and return its exit code, stdout and stderr.

    The same entry point the console script calls, reached without paying for an interpreter
    start-up per case -- and, unlike a subprocess, measured by `coverage`. Argparse exits rather
    than returning for a usage error, so `SystemExit` is caught and its code returned.
    """
    try:
        code = main(list(argv))
    except SystemExit as raised:
        code = int(raised.code or 0)
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def report_of(out: Path) -> str:
    """Read the report a run wrote, failing with its own error output if it wrote none."""
    path = out / "report.md"
    assert path.is_file(), f"no report at {path}"
    return path.read_text(encoding="utf-8")


def claims_of(out: Path) -> ClaimsDocument:
    """Read the claims document a run wrote."""
    return ClaimsDocument.read(out / "claims.json")


def check_the_report(out: Path) -> None:
    """Apply the renderer's own rules to what a command-line run produced."""
    claims = claims_of(out)
    problems = check_report(report_of(out), Configuration.full_agent, claims.post_repair)
    assert problems == [], problems
    assert "## Appendix A" in report_of(out)
    assert claims.precision_pre == 1.0 and claims.precision_post == 1.0


# --- the line in CLAUDE.md's command list ----------------------------------------------------


@pytest.mark.parametrize(
    ("package", "expected_n"),
    [(CREDIT, 5000), (MSR, 2000)],
    ids=["credit_default", "msr_prepayment"],
)
def test_the_command_list_line_runs_end_to_end_on_both_subjects(
    package: Path, expected_n: int, tmp_path: Path
) -> None:
    """`quaestor validate <pkg> --synthetic --llm fake --out DIR`: gate condition 5b itself.

    Bare `--synthetic` takes the subject's documented size -- 5,000 rows for the credit subject,
    2,000 loans for the hazard subject (D-081) -- which is what every figure in `PROGRESS.md` was
    measured at, and the front matter records the number that was used.
    """
    out = tmp_path / "r"
    completed = quaestor(
        "validate", str(package), "--synthetic", "--llm", "fake", "--out", str(out)
    )
    assert completed.returncode == EXIT_OK, completed.stderr
    assert f"report: {out / 'report.md'}" in completed.stdout
    assert "grounding precision:" in completed.stdout
    report = report_of(out)
    assert f"synthetic_n: {expected_n}" in report
    assert "grounding_precision_pre:" in report and "grounding_precision_post:" in report
    check_the_report(out)
    for name in ("claims.json", "findings.json", "trace.jsonl"):
        assert (out / name).is_file()
    assert (out / "artifacts" / "index.json").is_file()


def test_the_documented_default_is_the_one_the_subjects_declare() -> None:
    assert synthetic_default_n("credit_default") == 5000
    assert synthetic_default_n("msr_prepayment") == 2000
    assert synthetic_default_n("a_package_this_version_has_never_seen") is None


def test_a_package_with_no_documented_size_refuses_a_bare_synthetic(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # Inventing a row count would decide every figure computed from the panel, so the program
    # asks for one instead (D-081).
    package = tmp_path / "unknown_subject"
    shutil.copytree(CREDIT, package)
    text = (package / "package.yaml").read_text(encoding="utf-8")
    (package / "package.yaml").write_text(
        text.replace("name: credit_default", "name: unknown_subject", 1), encoding="utf-8"
    )
    code, _, err = run(
        capsys,
        "validate",
        str(package),
        "--synthetic",
        "--llm",
        "fake",
        "--out",
        str(tmp_path / "r"),
    )
    assert code == EXIT_USAGE
    assert "no documented synthetic size" in err
    assert "--synthetic 2000" in err


# --- usage errors ----------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("argv", "needle"),
    [
        ([], "the following arguments are required: COMMAND"),
        (["validate"], "the following arguments are required"),
        (["validate", "PKG", "--llm", "fake", "--out", "/tmp/x"], "one of the arguments"),
        (["validate", "PKG", "--synthetic", "--llm", "wrong", "--out", "/tmp/x"], "invalid choice"),
        (["tool"], "the following arguments are required"),
        (["tool", "no_such_tool", "--pkg", "P", "--run-dir", "D"], "invalid choice"),
        (["corpus"], "the following arguments are required: ACTION"),
        (["study", "score"], "the following arguments are required"),
        (["verifier-eval"], "invalid choice"),
        (["mcp"], "invalid choice"),
    ],
    ids=[
        "no-command",
        "validate-without-anything",
        "validate-without-a-data-source",
        "validate-with-an-unknown-provider",
        "tool-without-anything",
        "tool-with-an-unknown-tool",
        "corpus-without-an-action",
        "study-score-without-the-two-directories-it-reads",
        "verifier-eval-is-phase-13",
        "mcp-is-phase-15",
    ],
)
def test_a_usage_error_exits_two_and_names_the_command_that_fixes_it(
    argv: Sequence[str], needle: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """Including the two commands of spec 3.14 that this version deliberately does not have.

    `verifier-eval` and `mcp` are rejected as unknown commands rather than accepted and apologised
    for, which is the same argument the Phase 0 design paragraph makes about half-built flag
    surfaces (D-082). `study score` is no longer one of them: Phase 12 is the phase that scores,
    so it has a parser, and what it refuses here is a request that names neither of the two
    directories it reads.
    """
    code, _, err = run(capsys, *argv)
    assert code == EXIT_USAGE
    assert needle in err
    assert "  fix: quaestor" in err and "--help" in err


@pytest.mark.parametrize(
    ("argv", "needle", "fix"),
    [
        (["--synthetic", "0"], "is not a number of rows", "--synthetic 2000"),
        (["--synthetic", "-3"], "is not a number of rows", "--synthetic 2000"),
        (["--synthetic", "--llm", "replay"], "needs --cassettes", "--cassettes DIR"),
    ],
    ids=["zero-rows", "negative-rows", "replay-without-cassettes"],
)
def test_a_request_the_parser_accepts_and_the_program_refuses_exits_two(
    argv: Sequence[str], needle: str, fix: str, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code, _, err = run(
        capsys,
        "validate",
        str(CREDIT),
        *argv,
        *(["--llm", "fake"] if "--llm" not in argv else []),
        "--out",
        str(tmp_path / "r"),
    )
    assert code == EXIT_USAGE
    assert needle in err
    assert fix in err


def test_cassettes_without_replay_is_refused_rather_than_ignored(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # A flag that is silently not read is a flag a user believes was honoured.
    code, _, err = run(
        capsys,
        "validate",
        str(CREDIT),
        "--synthetic",
        str(SMALL),
        "--llm",
        "fake",
        "--cassettes",
        str(tmp_path / "tapes"),
        "--out",
        str(tmp_path / "r"),
    )
    assert code == EXIT_USAGE
    assert "read only by --llm replay" in err


def test_a_package_that_does_not_load_exits_two_and_names_the_package(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code, _, err = run(
        capsys,
        "validate",
        str(tmp_path / "nothing"),
        "--synthetic",
        "--llm",
        "fake",
        "--out",
        str(tmp_path / "r"),
    )
    assert code == EXIT_USAGE
    assert "no model package" in err
    assert "  fix: " in err


def test_the_console_script_writes_a_usage_error_to_stderr_and_exits_two() -> None:
    # The in-process cases above go through `main`; this one proves the installed script does the
    # same thing, including which stream the message goes to.
    completed = quaestor("validate", "--synthetic")
    assert completed.returncode == EXIT_USAGE
    assert completed.stdout == ""
    assert "quaestor: error:" in completed.stderr
    assert "  fix: quaestor validate --help" in completed.stderr


def test_the_version_is_printed_by_a_flag_rather_than_by_a_bare_invocation() -> None:
    from quaestor import __version__

    completed = quaestor("--version")
    assert completed.returncode == EXIT_OK
    assert completed.stdout.strip() == f"quaestor {__version__}"


# --- quaestor tool ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def run_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """One small credit run, so that `quaestor tool` has a run directory to read."""
    out = tmp_path_factory.mktemp("toolrun") / "r"
    assert (
        main(
            ["validate", str(CREDIT), "--synthetic", str(SMALL), "--llm", "fake", "--out", str(out)]
        )
        == EXIT_OK
    )
    return out


def test_quaestor_tool_prints_the_summary_and_every_artifact_name(
    run_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code, out, err = run(
        capsys,
        "tool",
        "compute_metrics",
        "--pkg",
        str(CREDIT),
        "--run-dir",
        str(run_dir),
        "--args-json",
        json.dumps({"splits": ["test"]}),
    )
    assert code == EXIT_OK, err
    assert out.startswith("compute_metrics: ")
    assert "artifact metrics.test.auc" in out
    assert "artifact calibration.test" in out
    assert "artifacts stored under" in out


def test_quaestor_tool_defaults_to_no_arguments_at_all(
    run_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code, out, err = run(
        capsys, "tool", "check_collinearity", "--pkg", str(CREDIT), "--run-dir", str(run_dir)
    )
    assert code == EXIT_OK, err
    assert "artifact condition_number" in out


def test_quaestor_tool_reports_the_candidates_a_check_raised(
    run_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # The credit subject's one expected finding, E1, comes from this check (D-017).
    code, out, err = run(
        capsys, "tool", "challenger_compare", "--pkg", str(CREDIT), "--run-dir", str(run_dir)
    )
    assert code == EXIT_OK, err
    assert "candidate E1 (low)" in out


@pytest.mark.parametrize(
    ("args_json", "needle"),
    [("not json at all", "is not JSON"), ('["a list"]', "must be a JSON object")],
    ids=["unparsable", "not-an-object"],
)
def test_quaestor_tool_refuses_args_json_that_is_not_an_object(
    args_json: str, needle: str, run_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code, _, err = run(
        capsys,
        "tool",
        "compute_metrics",
        "--pkg",
        str(CREDIT),
        "--run-dir",
        str(run_dir),
        "--args-json",
        args_json,
    )
    assert code == EXIT_USAGE
    assert needle in err
    assert "  fix: quaestor tool" in err


def test_a_tool_that_cannot_read_its_inputs_exits_one_and_names_the_missing_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # Exit 1 rather than 2: the request was well formed and the check ran into a run that is not
    # there, which is the same class of failure as a report the renderer refuses.
    code, _, err = run(
        capsys,
        "tool",
        "compute_metrics",
        "--pkg",
        str(CREDIT),
        "--run-dir",
        str(tmp_path / "empty"),
    )
    assert code == EXIT_FAILED_RUN
    assert "predictions_train.csv" in err
    assert "  fix: " in err


# --- corpus ingest ---------------------------------------------------------------------------


def test_corpus_ingest_names_a_pdf_that_is_not_there(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # The only offline assertion available: no test may read a PDF, and none is committed.
    code, _, err = run(
        capsys,
        "corpus",
        "ingest",
        "--sr117",
        str(tmp_path / "a.pdf"),
        "--sr262",
        str(tmp_path / "b.pdf"),
    )
    assert code == EXIT_USAGE
    assert "a.pdf" in err
    assert "  fix: " in err


def test_a_tool_run_against_a_package_that_does_not_load_exits_two(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code, _, err = run(
        capsys,
        "tool",
        "compute_metrics",
        "--pkg",
        str(tmp_path / "nothing"),
        "--run-dir",
        str(tmp_path / "r"),
    )
    assert code == EXIT_USAGE
    assert "no model package" in err


def _source(document: str) -> Source:
    """One provenance record, as the ingest returns; no PDF is read to build it."""
    return Source(
        document=document,
        title=f"{document} title",
        issued="2026-04-17",
        status="current",
        source_url=f"https://example.invalid/{document}.pdf",
        pdf_sha256="0" * 64,
        pages=12,
        sections=16,
        outline_sha256="1" * 64,
        ingested="2026-09-07",
    )


def test_corpus_ingest_prints_what_each_document_produced(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # The ingest itself is `tests/test_corpus.py`'s; what is under test here is the wiring, and no
    # test in this repository may read a PDF, so the two PDFs are empty files and never opened.
    for name in ("a.pdf", "b.pdf"):
        (tmp_path / name).write_bytes(b"")
    monkeypatch.setattr(cli, "ingest", lambda *a, **k: [_source("SR11-7"), _source("SR26-2")])
    code, out, _ = run(
        capsys,
        "corpus",
        "ingest",
        "--sr117",
        str(tmp_path / "a.pdf"),
        "--sr262",
        str(tmp_path / "b.pdf"),
    )
    assert code == EXIT_OK
    assert "SR11-7: 16 sections from 12 pages (current)" in out
    assert "SR26-2: 16 sections from 12 pages (current)" in out


def test_an_ingest_that_fails_on_its_own_document_exits_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # Exit 1, not 2: the request was well formed and the work failed. A heading the outline names
    # and the document does not have is the case this stands for (D-056).
    for name in ("a.pdf", "b.pdf"):
        (tmp_path / name).write_bytes(b"")

    def explode(*args: object, **kwargs: object) -> list[Source]:
        raise CorpusError("the heading 'V.1.c' is not in SR11-7 after 'V.1.b'")

    monkeypatch.setattr(cli, "ingest", explode)
    code, _, err = run(
        capsys,
        "corpus",
        "ingest",
        "--sr117",
        str(tmp_path / "a.pdf"),
        "--sr262",
        str(tmp_path / "b.pdf"),
    )
    assert code == EXIT_FAILED_RUN
    assert "is not in SR11-7" in err
    assert "  fix: quaestor corpus ingest" in err


def test_corpus_ingest_is_wired_to_the_dev_time_script() -> None:
    help_text = _help_of(["corpus", "ingest", "--help"])
    assert "--sr117" in help_text and "--sr262" in help_text and "--outlines" in help_text


# --- the pieces, on their own ----------------------------------------------------------------


def _help_of(argv: Sequence[str]) -> str:
    """Render one parser's help without running the program."""
    completed = subprocess.run(
        [sys.executable, "-m", "quaestor.cli", *argv],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    return completed.stdout


def test_the_top_level_help_lists_the_four_commands_that_exist() -> None:
    text = _help_of(["--help"])
    assert "validate" in text and "tool" in text and "corpus" in text and "study" in text
    assert "verifier-eval" not in text and " mcp" not in text


def test_study_offers_build_run_and_score() -> None:
    """D-082 applied the way it asks to be: each action appears in the phase that makes it work."""
    lines = _help_of(["study", "--help"]).splitlines()
    actions = [line.split()[0] for line in lines if line.startswith("    ") and line.split()]
    assert "build" in actions and "run" in actions and "score" in actions


def test_a_data_run_asks_the_subject_for_no_generated_rows() -> None:
    # The `--data` half of the mutually exclusive pair, which no offline test can run end to end:
    # `CLAUDE.md` forbids a test that reads real data at all.
    assert _synthetic_n(load_package(CREDIT), None) is None
    assert _synthetic_n(load_package(CREDIT), 1200) == 1200


def test_timeout_overrides_the_subjects_wall_clock_cap() -> None:
    package = load_package(CREDIT)
    assert package.spec.runtime.max_seconds != 7
    assert _capped(package, 7).spec.runtime.max_seconds == 7
    assert _capped(package, None) is package


def test_the_provider_flag_builds_the_adapter_it_names() -> None:
    # No call is made: constructing `ClaudeCLILLM` runs no subprocess, and the fake runs nothing.
    assert _live_provider("fake", None).name == "fake"
    claude = _live_provider("claude-cli", "claude-opus-5")
    assert claude.name == "claude-cli"
    assert getattr(claude, "model", None) == "claude-opus-5"


def test_the_anthropic_extra_is_not_installed_and_the_error_says_how_to_install_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # `CLAUDE.md` keeps `anthropic` out of the dev environment; the CLI must fail on the request
    # rather than half-way through a run.
    code, _, err = run(
        capsys,
        "validate",
        str(CREDIT),
        "--synthetic",
        str(SMALL),
        "--llm",
        "anthropic",
        "--out",
        str(tmp_path / "r"),
    )
    assert code == EXIT_USAGE
    assert "pip install" in err


def test_main_returns_the_exit_code_rather_than_raising(tmp_path: Path) -> None:
    # The console-script wrapper passes what `main` returns to `sys.exit`, so it has to return.
    assert main(["tool", "compute_metrics", "--pkg", str(CREDIT), "--run-dir", str(tmp_path)]) == (
        EXIT_FAILED_RUN
    )


def test_the_parser_is_buildable_without_running_anything() -> None:
    parser = build_parser()
    args = parser.parse_args(["validate", "P", "--synthetic", "--llm", "fake", "--out", "O"])
    assert args.command == "validate"
    assert args.config == Configuration.full_agent.value
    assert re.fullmatch(r"-?\d+", str(args.synthetic))


def test_a_validate_whose_checklist_partly_failed_still_exits_zero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """D-177's consequence for the scripted interface, which is what D-082's codes are about.

    Exit 1 means "ran and did not produce what it was asked for". A run that wrote a report naming
    the check it is missing produced what it was asked for, minus one row, and says so in the
    report rather than in the exit code. The run that genuinely produces nothing -- the subject
    itself failing to run -- still exits 1, which the case below pins.
    """
    from quaestor.errors import ToolError
    from quaestor.tools.collinearity import CheckCollinearityTool

    def raising(self: object, args: object, ctx: object) -> object:
        raise ToolError("the design matrix is singular on this split")

    monkeypatch.setattr(CheckCollinearityTool, "run", raising)
    out = tmp_path / "r"
    code, printed, err = run(
        capsys,
        "validate",
        str(CREDIT),
        "--synthetic",
        str(SMALL),
        "--llm",
        "fake",
        "--out",
        str(out),
    )
    assert code == EXIT_OK, err
    assert printed.startswith("report: ")
    assert "did not run: the design matrix is singular on this split" in (
        (out / "report.md").read_text(encoding="utf-8")
    )


def test_a_validate_whose_subject_would_not_run_still_exits_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """The other side of D-177: `run_model` is the one call whose failure is still the run's."""
    from quaestor.errors import ToolError
    from quaestor.tools.run import RunModelTool

    def raising(self: object, args: object, ctx: object) -> object:
        raise ToolError("the package has no `code/` directory")

    monkeypatch.setattr(RunModelTool, "run", raising)
    code, printed, err = run(
        capsys,
        "validate",
        str(CREDIT),
        "--synthetic",
        str(SMALL),
        "--llm",
        "fake",
        "--out",
        str(tmp_path / "r"),
    )
    assert code == EXIT_FAILED_RUN
    assert printed == ""
    assert "no `code/` directory" in err
