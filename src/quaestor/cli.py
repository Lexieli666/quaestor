"""The ``quaestor`` console script: ``validate``, ``tool``, ``corpus ingest`` and ``study build``.

Spec section 3.14 lists eight commands. Five of them exist today, and only those five have a
parser: ``verifier-eval`` arrives with Phase 13 and ``mcp`` with Phase 15, and ``study score`` is
``python eval/score.py``, which reads run directories and never runs anything. A flag that parses
and then says "not implemented" is worse than no flag, because a reader of ``--help`` cannot tell
the difference between what this program does and what it is going to do; the Phase 0 design
paragraph on half-built flag surfaces is the whole argument, and it applies here (D-082).

``study build`` and ``study run`` are the two commands whose implementation is not in this
package. The seeded-defect generator lives in ``eval/seed.py`` and the study harness in
``eval/run_study.py``, outside ``src/``, because the pipeline being measured must not be able to
import the thing that plants the defects and because a study harness is a development tool that
only makes sense inside a checkout; so each command loads its module from beside the taxonomy it
was given, and says so when it is not there (DECISIONS D-127).

**Exit codes**, which are the interface a script sees:

* ``0`` -- the command did what it was asked.
* ``1`` -- the command ran and did not produce what it was asked for: a validation the renderer
  refused, a tool whose inputs are not there, an ingest whose outline does not match its document,
  a study chunk one of whose cells produced no report. The run directory holds the trace of how
  far it got.
* ``2`` -- the request itself was wrong: a flag, a missing package, a package that does not load,
  a PDF that is not where the command says it is. Nothing was run.

Every message written to standard error names the command that fixes it, which is spec section
3.1's rule about error messages applied to the program's own front door.

**The exit code is not the whole answer, and two commands say so.** A ``validate`` whose checklist
partly failed exits ``0`` and names the missing check in Appendix D, so a caller judging a run
reads ``checks_failed`` and not the code (D-177). A ``study run`` that stopped on its cost ceiling
exits ``0`` exactly as one that finished the study does, so a caller reruns the same command line
until ``remaining`` in ``ledger.json`` reads zero.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from types import ModuleType
from typing import Any, Final, NoReturn

from . import __version__
from .artifacts.store import ArtifactStore
from .configs import CONFIGURATIONS, synthetic_default_n
from .corpus.ingest import ingest
from .errors import CorpusError, PackageError, QuaestorError
from .hashing import stable_hash
from .llm.base import LLM
from .llm.offline import OfflineLLM
from .llm.recording import RecordingLLM, ReplayLLM
from .package import ModelPackage, load_package
from .pipeline import validate
from .tools import default_registry
from .tools.registry import ToolContext
from .trace import TraceWriter
from .vocab import Configuration

__all__ = [
    "EXIT_FAILED_RUN",
    "EXIT_OK",
    "EXIT_USAGE",
    "PROVIDERS",
    "RUN_STUDY_MODULE",
    "SEED_MODULE",
    "STUDY_ORDER",
    "build_parser",
    "main",
]

EXIT_OK: Final = 0
"""The command did what it was asked."""

EXIT_FAILED_RUN: Final = 1
"""A validation ran and produced no report."""

EXIT_USAGE: Final = 2
"""The request was wrong; nothing ran. Also argparse's own exit code for a bad flag."""

PROVIDERS: Final = ("fake", "anthropic", "claude-cli", "replay")
"""The four values of ``--llm``. Anthropic is the only live vendor, by ``CLAUDE.md``'s rule."""

SYNTHETIC_FROM_SUBJECT: Final = -1
"""What ``--synthetic`` with no number parses to, before the subject's documented size is read."""

_TRACE_FILE: Final = "trace.jsonl"
"""A ``quaestor tool`` call appends to the same trace a validation of that run directory wrote."""

SEED_MODULE: Final = "seed.py"
"""The seeded-defect generator, looked for beside ``--taxonomy`` and loaded under an alias."""

RUN_STUDY_MODULE: Final = "run_study.py"
"""The study harness, looked for in the same place and loaded the same way."""

_SEED_ALIAS: Final = "quaestor_eval_seed"
"""What ``eval/seed.py`` is imported as, so it does not collide with anything on the path."""

_RUN_STUDY_ALIAS: Final = "quaestor_eval_run_study"
"""What ``eval/run_study.py`` is imported as, for the same reason."""

STUDY_ORDER: Final = (
    Configuration.rules_only.value,
    Configuration.plain_llm.value,
    Configuration.full_agent.value,
)
"""The order ``study run`` runs the configurations in when ``--config`` is not given.

Cheapest first, which is ``docs/STUDY.md`` section 4's order and not :data:`CONFIGURATIONS`'s:
``rules_only`` makes no model call, so eighteen of them are a free rehearsal of the harness, and
``plain_llm`` costs about a third of ``full_agent`` a run (D-179). A defect in the study harness
should be found by the arm that costs nothing to re-run.
"""

_DEFAULT_TAXONOMY: Final = Path("eval") / "taxonomy.yaml"
_SUBJECTS_DIRNAME: Final = "subjects"
"""Where the clean subjects are, relative to the checkout the taxonomy was found in."""


class _Parser(argparse.ArgumentParser):
    """An ``ArgumentParser`` whose usage errors name the help that fixes them."""

    def error(self, message: str) -> NoReturn:
        """Print the usage error, name the fixing command, and exit ``2``.

        Args:
            message: What argparse found wrong.

        Raises:
            SystemExit: Always, with :data:`EXIT_USAGE`.
        """
        self.print_usage(sys.stderr)
        print(f"quaestor: error: {message}", file=sys.stderr)
        print(f"  fix: {self.prog} --help", file=sys.stderr)
        raise SystemExit(EXIT_USAGE)


def build_parser() -> argparse.ArgumentParser:
    """Build the parser for every command this version supports.

    Returns:
        The parser. Exposed so that ``--help`` can be rendered in a document and asserted on in a
        test without running the program.
    """
    parser = _Parser(
        prog="quaestor",
        description=(
            "An agentic model-validation copilot: run the checks over a model package and draft "
            "an SR 11-7-shaped report in which every number carries a citation to a computed "
            "artifact. Not a compliance product and not a claim of compliance."
        ),
    )
    parser.add_argument(
        "--version", action="version", version=f"quaestor {__version__}", help="print the version"
    )
    commands = parser.add_subparsers(dest="command", metavar="COMMAND", required=True)
    _add_validate(commands)
    _add_tool(commands)
    _add_corpus(commands)
    _add_study(commands)
    return parser


def _add_validate(commands: Any) -> None:
    """Add ``quaestor validate``, the command spec section 1 states the goal in terms of."""
    validate_parser = commands.add_parser(
        "validate",
        help="validate one model package and write report.md, claims.json, findings.json",
        description=(
            "Run a model package through the planner, the checks, the drafter and the verifier, "
            "and write report.md, claims.json, findings.json, trace.jsonl and the artifact store "
            "under --out. Exactly one of --data and --synthetic says where the data comes from."
        ),
    )
    validate_parser.add_argument("package", metavar="PKG", type=Path, help="the package directory")
    source = validate_parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--data",
        metavar="DIR",
        type=Path,
        default=None,
        help="the directory holding the subject's real data; its manifest is verified if declared",
    )
    source.add_argument(
        "--synthetic",
        metavar="N",
        nargs="?",
        type=int,
        const=SYNTHETIC_FROM_SUBJECT,
        default=None,
        help=(
            "generate N rows from the subject's known process instead of reading data; with no "
            "number, the subject's documented default (credit_default 5000, msr_prepayment 2000)"
        ),
    )
    validate_parser.add_argument(
        "--llm",
        choices=PROVIDERS,
        required=True,
        help=(
            "fake: the offline provider, no network; anthropic: the SDK; claude-cli: the Claude "
            "Code CLI on your own login; replay: answers from --cassettes and nothing else"
        ),
    )
    validate_parser.add_argument(
        "--model",
        metavar="M",
        default=None,
        help="the model to ask; applies to --llm anthropic and --llm claude-cli",
    )
    validate_parser.add_argument(
        "--config",
        metavar="C",
        choices=[name.value for name in CONFIGURATIONS],
        default=Configuration.full_agent.value,
        help="which configuration to run (default: full_agent)",
    )
    validate_parser.add_argument(
        "--out", metavar="DIR", type=Path, required=True, help="where to write the run"
    )
    validate_parser.add_argument(
        "--timeout",
        metavar="S",
        type=int,
        default=None,
        help="override the package's runtime.max_seconds wall-clock cap on the subject",
    )
    validate_parser.add_argument(
        "--record-cassettes",
        metavar="DIR",
        type=Path,
        default=None,
        help="write one JSON file per model call, so a live run can be replayed and audited",
    )
    validate_parser.add_argument(
        "--cassettes",
        metavar="DIR",
        type=Path,
        default=None,
        help="where --llm replay reads its recorded calls from",
    )
    validate_parser.set_defaults(run=_run_validate)


def _add_tool(commands: Any) -> None:
    """Add ``quaestor tool``: one registered check, over a run directory that already exists."""
    registry = default_registry()
    tool_parser = commands.add_parser(
        "tool",
        help="run one registered tool and print its summary and the artifacts it stored",
        description=(
            "Run one check on its own, against a run directory a validation already wrote (or an "
            "empty one, for run_model). Prints the tool's summary, the finding candidates it "
            "raised and the logical name of every artifact it stored."
        ),
    )
    tool_parser.add_argument(
        "name", metavar="NAME", choices=registry.names(), help="the tool to run"
    )
    tool_parser.add_argument(
        "--pkg", metavar="PKG", type=Path, required=True, help="the package directory"
    )
    tool_parser.add_argument(
        "--run-dir",
        metavar="DIR",
        type=Path,
        required=True,
        help="a validation's --out directory: its artifacts/ store and its run/ contract files",
    )
    tool_parser.add_argument(
        "--args-json",
        metavar="JSON",
        default="{}",
        help="the tool's arguments as one JSON object (default: {})",
    )
    tool_parser.set_defaults(run=_run_tool)


def _add_corpus(commands: Any) -> None:
    """Add ``quaestor corpus ingest``: the dev-time script of spec section 3.8."""
    corpus_parser = commands.add_parser(
        "corpus",
        help="build the committed regulatory corpus from the two guidance PDFs",
        description="The dev-time ingest of spec section 3.8. No validation run reads a PDF.",
    )
    actions = corpus_parser.add_subparsers(dest="action", metavar="ACTION", required=True)
    ingest_parser = actions.add_parser(
        "ingest",
        help="split the two guidance PDFs into corpus/*.jsonl and SOURCES.json",
        description=(
            "Extract the text of the two PDFs, split each by its committed section outline, and "
            "write the JSONL the retriever reads. Run once per document revision; the JSONL is "
            "committed and the PDFs never are."
        ),
    )
    ingest_parser.add_argument(
        "--sr117", type=Path, required=True, help="the SR 11-7 attachment PDF"
    )
    ingest_parser.add_argument(
        "--sr262", type=Path, required=True, help="the SR 26-2 attachment PDF"
    )
    ingest_parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="where to write (default: the installed corpus package directory)",
    )
    ingest_parser.add_argument(
        "--outlines",
        type=Path,
        default=None,
        help="where the section outlines are (default: data/regulatory of this checkout)",
    )
    ingest_parser.set_defaults(run=_run_corpus)


def _add_study(commands: Any) -> None:
    """Add ``quaestor study build`` and ``quaestor study run``.

    ``score`` is deliberately not an action: it reads finished run directories and runs nothing,
    so it is ``python eval/score.py`` and not a verb of this program. ``quaestor study score``
    stays an argparse "invalid choice", which is what D-082 asks of every command that does not
    exist here.
    """
    study_parser = commands.add_parser(
        "study",
        help="build the seeded-defect variants the evaluation runs on, and run the study",
        description=(
            "The seeded-defect study of 04-SEEDED-DEFECT-STUDY.md. `build` writes one variant "
            "package per row of the taxonomy, each with a SEED.yaml recording what was done to it "
            "that no validation run ever reads; `run` validates those variants under one or more "
            "configurations, in resumable chunks. Scoring is `python eval/score.py`."
        ),
    )
    actions = study_parser.add_subparsers(dest="action", metavar="ACTION", required=True)
    build_parser = actions.add_parser(
        "build",
        help="write one variant package per row of eval/taxonomy.yaml",
        description=(
            "Copy each subject, apply one recipe to the copy and write SEED.yaml beside it. The "
            "variants are generated artefacts and are never committed; --out should be a "
            "gitignored directory. Real-data variants are built at study time from a --data path "
            "and are not written here."
        ),
    )
    build_parser.add_argument(
        "--taxonomy",
        metavar="FILE",
        type=Path,
        default=_DEFAULT_TAXONOMY,
        help=f"the taxonomy to build (default: {_DEFAULT_TAXONOMY}); {SEED_MODULE} is loaded "
        "from the same directory",
    )
    build_parser.add_argument(
        "--out", metavar="DIR", type=Path, required=True, help="where the variant packages go"
    )
    build_parser.add_argument(
        "--subjects",
        metavar="DIR",
        type=Path,
        default=None,
        help="where the clean subjects are (default: subjects/ beside the taxonomy's directory)",
    )
    build_parser.add_argument(
        "--synthetic",
        metavar="N",
        nargs="?",
        type=int,
        const=SYNTHETIC_FROM_SUBJECT,
        default=None,
        help=(
            "the panel size each variant is meant to be validated at, recorded in its SEED.yaml; "
            "with no number, each subject's documented default"
        ),
    )
    build_parser.add_argument(
        "--data",
        metavar="DIR",
        type=Path,
        default=None,
        help=(
            "build the variants for a --data validation against this directory, verifying each "
            "one's manifest against it; the four recipes that need a column the real sample does "
            "not carry are skipped by name (D-137)"
        ),
    )
    build_parser.set_defaults(run=_run_study_build)
    _add_study_run(actions)


def _add_study_run(actions: Any) -> None:
    """Add ``quaestor study run``: one chunk of the study, resumable and capped.

    The flag surface is ``validate``'s, because a cell *is* a validation and a second spelling of
    ``--llm`` or ``--synthetic`` would be a second set of rules about which of them combine. What
    is new is the two flags a study needs and a single run does not: ``--config``, which may be
    repeated, and ``--max-cost``, the chunk's ceiling.
    """
    run_parser = actions.add_parser(
        "run",
        help="run one chunk of the study: every (variant, configuration) cell not yet finished",
        description=(
            "Validate each variant under each configuration and write the result under --out, "
            "with a ledger.json that records what finished, what it cost and which checks did "
            "not run. Re-running the same command resumes: a cell whose latest attempt finished "
            "is skipped. --max-cost is the ceiling for this invocation alone -- one sitting -- "
            "and is checked both before a cell starts and before every model call."
        ),
    )
    run_parser.add_argument(
        "--variants",
        metavar="DIR",
        type=Path,
        required=True,
        help="where `quaestor study build` wrote the variant packages",
    )
    run_parser.add_argument(
        "--out", metavar="DIR", type=Path, required=True, help="the study directory"
    )
    run_parser.add_argument(
        "--config",
        metavar="C",
        action="append",
        choices=[name.value for name in CONFIGURATIONS],
        default=None,
        help=(
            "which configuration to run; repeat it to run several, in the order given "
            f"(default: {', '.join(STUDY_ORDER)}, which is cheapest first)"
        ),
    )
    source = run_parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--data",
        metavar="DIR",
        type=Path,
        default=None,
        help="the directory holding the subjects' real data",
    )
    source.add_argument(
        "--synthetic",
        metavar="N",
        nargs="?",
        type=int,
        const=SYNTHETIC_FROM_SUBJECT,
        default=None,
        help="generate N rows per variant; with no number, each subject's documented default",
    )
    run_parser.add_argument(
        "--llm", choices=PROVIDERS, required=True, help="the provider every cell's calls go to"
    )
    run_parser.add_argument(
        "--model",
        metavar="M",
        default=None,
        help="the model to ask; name it, or the study is not comparable to the runs it quotes",
    )
    run_parser.add_argument(
        "--max-cost",
        metavar="USD",
        type=float,
        default=None,
        help=(
            "stop this chunk once its model calls have cost this much; a cell whose estimate "
            "does not fit is not started, and a call that would cross the line is not made"
        ),
    )
    run_parser.add_argument(
        "--only",
        metavar="VARIANT",
        action="append",
        default=None,
        help="restrict the chunk to these variants; repeat it for several",
    )
    run_parser.add_argument(
        "--taxonomy",
        metavar="FILE",
        type=Path,
        default=_DEFAULT_TAXONOMY,
        help=f"where {RUN_STUDY_MODULE} is looked for (default: beside {_DEFAULT_TAXONOMY})",
    )
    run_parser.add_argument(
        "--record-cassettes",
        metavar="DIR",
        type=Path,
        default=None,
        help="record every model call, one store per cell, so the study can be replayed",
    )
    run_parser.add_argument(
        "--cassettes",
        metavar="DIR",
        type=Path,
        default=None,
        help="where --llm replay reads its recorded calls from",
    )
    run_parser.set_defaults(run=_run_study_run)


def _load_eval_module(directory: Path, filename: str, alias: str, fix: str) -> ModuleType:
    """Import one module of ``eval/`` from a directory, under an alias of its own.

    Both of the ``study`` actions are implemented outside this package and found the same way:
    beside the taxonomy the command was given, which is the one path a caller always names.

    Args:
        directory: Where the taxonomy is, which is where the module is looked for.
        filename: The module's file name, :data:`SEED_MODULE` or :data:`RUN_STUDY_MODULE`.
        alias: What to import it as, so it collides with nothing on the path.
        fix: The command to suggest when it is not there.

    Returns:
        The loaded module.

    Raises:
        PackageError: There is no such file there, or it does not import.
    """
    path = directory / filename
    if not path.is_file():
        raise PackageError(
            f"there is no {filename} beside {directory}; `quaestor study` works inside a checkout "
            f"of this repository, where eval/{filename} sits next to eval/taxonomy.yaml",
            fix=fix,
        )
    spec = importlib.util.spec_from_file_location(alias, path)
    if spec is None or spec.loader is None:  # pragma: no cover - a file that is not importable
        raise PackageError(f"{path} is not importable as a module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


def _load_seed_module(directory: Path) -> ModuleType:
    """Import ``eval/seed.py``, the seeded-defect generator."""
    return _load_eval_module(
        directory,
        SEED_MODULE,
        _SEED_ALIAS,
        "quaestor study build --taxonomy eval/taxonomy.yaml --out eval/variants",
    )


def _load_run_study_module(directory: Path) -> ModuleType:
    """Import ``eval/run_study.py``, the study harness."""
    return _load_eval_module(
        directory,
        RUN_STUDY_MODULE,
        _RUN_STUDY_ALIAS,
        "quaestor study run --variants eval/variants --out eval/results/run --llm fake "
        "--synthetic --config rules_only",
    )


def _run_study_build(args: argparse.Namespace) -> int:
    """Run ``quaestor study build`` and print where each variant went."""
    taxonomy_path = Path(args.taxonomy)
    if not taxonomy_path.is_file():
        return _fail(
            f"there is no taxonomy at {taxonomy_path}",
            "quaestor study build --taxonomy eval/taxonomy.yaml --out eval/variants",
        )
    try:
        seed_module = _load_seed_module(taxonomy_path.parent)
    except PackageError as exc:
        return _fail(str(exc.message), exc.fix or "quaestor study build --help")
    subjects = (
        Path(args.subjects)
        if args.subjects is not None
        else taxonomy_path.parent.parent / _SUBJECTS_DIRNAME
    )
    if not subjects.is_dir():
        return _fail(
            f"there is no subjects directory at {subjects}",
            "quaestor study build --taxonomy eval/taxonomy.yaml --subjects subjects "
            "--out eval/variants",
        )
    if args.data is not None and not Path(args.data).is_dir():
        return _fail(
            f"there is no data directory at {args.data}",
            "see data/README.md for where each subject's sample comes from",
        )
    try:
        taxonomy = seed_module.load_taxonomy(taxonomy_path)
        results: list[Any] = seed_module.build_all(
            taxonomy,
            args.out,
            subjects_dir=subjects,
            synthetic_n=seed_module.synthetic_sizes(taxonomy, args.synthetic),
            data_dir=args.data,
        )
    except (ValueError, KeyError, OSError, QuaestorError) as exc:
        return _fail(
            f"{taxonomy_path} could not be built: {exc}",
            f"cat {taxonomy_path}",
            code=EXIT_FAILED_RUN,
        )
    built = 0
    for result in results:
        if result.built:
            built += 1
            print(f"{result.spec.id}: {result.spec.recipe} -> {result.root}")
        else:
            print(f"{result.spec.id}: not built ({result.reason})")
    print(f"{built} variant(s) under {args.out}; {len(results) - built} not built")
    return EXIT_OK


def _run_study_run(args: argparse.Namespace) -> int:
    """Run ``quaestor study run``: one chunk, then a summary of what is left.

    The return value is :data:`EXIT_OK` for a chunk that ended cleanly, whether it ended because
    the study is finished or because the ceiling was reached, and :data:`EXIT_FAILED_RUN` when a
    cell produced no report. Which of the two clean endings happened is in ``ledger.json``, and
    the ``checks_failed`` a finished cell carries is printed here and written there: D-177's rule
    is that a caller judging a run reads those and not this number.
    """
    taxonomy_path = Path(args.taxonomy)
    try:
        harness = _load_run_study_module(taxonomy_path.parent)
        provider = _provider(argparse.Namespace(**{**vars(args), "record_cassettes": None}))
    except QuaestorError as exc:
        return _fail(str(exc.message), exc.fix or "quaestor study run --help")
    configurations = args.config or list(STUDY_ORDER)
    model: dict[str, Any] = {"model": args.model} if args.model else {}
    try:
        summary = harness.run_chunk(
            args.variants,
            args.out,
            provider=provider,
            configurations=configurations,
            synthetic=None if args.synthetic == SYNTHETIC_FROM_SUBJECT else args.synthetic,
            data_dir=args.data,
            max_cost_usd=args.max_cost,
            only=args.only,
            cassettes_dir=args.record_cassettes,
            **model,
        )
    except QuaestorError as exc:
        return _fail(str(exc.message), exc.fix or "quaestor study run --help")
    ledger = Path(args.out) / harness.LEDGER_FILE
    print(
        f"{len(summary.ran)} cell(s) run, {len(summary.failed)} failed, "
        f"{len(summary.skipped)} already done; ${summary.spent_usd:.4f} spent"
    )
    if summary.stopped_for_budget:
        print(f"stopped on --max-cost ${args.max_cost:.4f}; rerun the same command to continue")
    for record in summary.checks_failed:
        tools = ", ".join(failure["tool"] for failure in record.checks_failed)
        print(f"{record.cell.key}: reported without {tools}")
    print(f"{summary.remaining} cell(s) of this plan remaining; ledger: {ledger}")
    return EXIT_FAILED_RUN if summary.failed else EXIT_OK


def _fail(message: str, fix: str, code: int = EXIT_USAGE) -> int:
    """Write one error to standard error, with the command that fixes it, and return its code."""
    print(f"quaestor: error: {message}", file=sys.stderr)
    print(f"  fix: {fix}", file=sys.stderr)
    return code


def _provider(args: argparse.Namespace) -> LLM:
    """Build the provider ``--llm`` names, wrapped in a recorder when one was asked for.

    Args:
        args: The parsed ``validate`` arguments.

    Returns:
        The provider.

    Raises:
        LLMProviderError: The provider cannot be built -- the ``anthropic`` extra is not
            installed, or ``--llm replay`` was given a directory that does not exist.
        PackageError: ``--cassettes`` was given without ``--llm replay``, or the other way round.
    """
    if args.llm == "replay":
        if args.cassettes is None:
            raise PackageError(
                "--llm replay needs --cassettes DIR, the directory a recorded run wrote",
                fix="quaestor validate PKG ... --llm replay --cassettes DIR",
            )
        inner: LLM = ReplayLLM(args.cassettes)
    else:
        if args.cassettes is not None:
            raise PackageError(
                "--cassettes is read only by --llm replay; nothing would consult it here",
                fix=f"quaestor validate ... --llm replay --cassettes {args.cassettes}",
            )
        inner = _live_provider(args.llm, args.model)
    if args.record_cassettes is not None:
        return RecordingLLM(inner, args.record_cassettes)
    return inner


def _live_provider(name: str, model: str | None) -> LLM:
    """Build one of the three providers that are not a replay."""
    if name == "fake":
        return OfflineLLM()
    if name == "anthropic":
        from .llm.anthropic import AnthropicLLM

        return AnthropicLLM(model=model) if model else AnthropicLLM()
    from .llm.claude_cli import ClaudeCLILLM

    return ClaudeCLILLM(model=model)


def _capped(package: ModelPackage, timeout: int | None) -> ModelPackage:
    """Return the package with ``--timeout`` applied to the subject's wall-clock cap."""
    if timeout is None:
        return package
    runtime = package.spec.runtime.model_copy(update={"max_seconds": timeout})
    return package.model_copy(update={"spec": package.spec.model_copy(update={"runtime": runtime})})


def _synthetic_n(package: ModelPackage, requested: int | None) -> int | None:
    """Resolve ``--synthetic`` to a row count, reading the subject's default when given none.

    Args:
        package: The loaded package.
        requested: What the flag parsed to: ``None`` for a ``--data`` run, a positive number, or
            :data:`SYNTHETIC_FROM_SUBJECT` for a bare ``--synthetic``.

    Returns:
        The row count, or ``None`` for a ``--data`` run.

    Raises:
        PackageError: The number is not positive, or the package is not one whose documented size
            this version knows -- in which case the human names a number rather than the program
            inventing one.
    """
    if requested is None:
        return None
    if requested == SYNTHETIC_FROM_SUBJECT:
        default = synthetic_default_n(package.name)
        if default is None:
            raise PackageError(
                f"no documented synthetic size for the package {package.name!r}, so bare "
                f"--synthetic has no number to use",
                fix=f"quaestor validate {package.root} --synthetic 2000 --llm fake --out DIR",
            )
        return default
    if requested <= 0:
        raise PackageError(
            f"--synthetic {requested} is not a number of rows to generate",
            fix=f"quaestor validate {package.root} --synthetic 2000 --llm fake --out DIR",
        )
    return requested


def _run_validate(args: argparse.Namespace) -> int:
    """Run ``quaestor validate`` and print where the report went."""
    try:
        package = load_package(args.package, data_dir=args.data)
        package = _capped(package, args.timeout)
        synthetic = _synthetic_n(package, args.synthetic)
        llm = _provider(args)
    except QuaestorError as exc:
        return _fail(str(exc.message), exc.fix or "quaestor validate --help")
    try:
        run = validate(
            package,
            llm=llm,
            config=args.config,
            data_dir=args.data,
            synthetic=synthetic,
            out=args.out,
        )
    except QuaestorError as exc:
        return _fail(
            str(exc.message),
            exc.fix or f"cat {Path(args.out) / _TRACE_FILE}",
            code=EXIT_FAILED_RUN,
        )
    print(f"report: {run.report_path}")
    print(
        f"grounding precision: {run.precision_pre:.4f} pre-repair, "
        f"{run.precision_post:.4f} post-repair over {run.claims.n_claims} claims"
    )
    print(f"findings: {len(run.findings.findings)}; artifacts: {len(run.store)}")
    return EXIT_OK


def _run_tool(args: argparse.Namespace) -> int:
    """Run ``quaestor tool`` and print the summary, the candidates and the artifact names."""
    try:
        arguments = json.loads(args.args_json)
    except json.JSONDecodeError as exc:
        return _fail(
            f"--args-json is not JSON: {exc}",
            "quaestor tool NAME --pkg PKG --run-dir DIR --args-json '{}'",
        )
    if not isinstance(arguments, dict):
        return _fail(
            f"--args-json must be a JSON object, not a {type(arguments).__name__}",
            'quaestor tool NAME --pkg PKG --run-dir DIR --args-json \'{"split": "test"}\'',
        )
    try:
        package = load_package(args.pkg)
    except PackageError as exc:
        return _fail(str(exc.message), exc.fix or "quaestor tool --help")
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    ctx = ToolContext(
        package=package,
        store=ArtifactStore(run_dir / "artifacts"),
        out_dir=run_dir / "run",
        trace=TraceWriter(
            run_dir / _TRACE_FILE,
            run_id=stable_hash({"tool": args.name, "args": arguments, "pkg": package.name}),
        ),
    )
    try:
        result = default_registry().call(args.name, arguments, ctx)
    except QuaestorError as exc:
        return _fail(
            str(exc.message),
            exc.fix or f"quaestor tool run_model --pkg {args.pkg} --run-dir {run_dir}",
            code=EXIT_FAILED_RUN,
        )
    print(f"{result.tool}: {result.summary}")
    for candidate in result.candidates:
        print(f"candidate {candidate.defect_class.value} ({candidate.suggested_severity.value})")
    for artifact in result.artifacts:
        print(f"artifact {artifact.name}")
    print(f"{len(result.artifacts)} artifacts stored under {run_dir / 'artifacts'}")
    return EXIT_OK


def _run_corpus(args: argparse.Namespace) -> int:
    """Run ``quaestor corpus ingest`` and print what each document produced."""
    for pdf in (args.sr117, args.sr262):
        if not Path(pdf).is_file():
            return _fail(
                f"there is no PDF at {pdf}",
                "see data/README.md for where each guidance document is downloaded from",
            )
    try:
        sources = ingest(args.sr117, args.sr262, args.out, outlines=args.outlines)
    except CorpusError as exc:
        return _fail(
            str(exc.message),
            exc.fix or "quaestor corpus ingest --sr117 PDF --sr262 PDF",
            code=EXIT_FAILED_RUN,
        )
    for source in sources:
        print(
            f"{source.document}: {source.sections} sections from {source.pages} pages "
            f"({source.status}), pdf sha256 {source.pdf_sha256[:16]}…"
        )
    return EXIT_OK


def main(argv: Sequence[str] | None = None) -> int:
    """Parse the command line and run one command.

    Args:
        argv: The arguments, excluding the program name, or ``None`` to read ``sys.argv``.

    Returns:
        :data:`EXIT_OK`, :data:`EXIT_FAILED_RUN` or :data:`EXIT_USAGE`. The console-script wrapper
        generated from ``[project.scripts]`` passes this value to :func:`sys.exit`.
    """
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    run: Any = args.run
    result: int = run(args)
    return result


if __name__ == "__main__":  # pragma: no cover - the module's command-line entry point
    raise SystemExit(main())
