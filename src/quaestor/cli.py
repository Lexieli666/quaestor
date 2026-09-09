"""The ``quaestor`` console script: ``validate``, ``tool``, ``corpus ingest`` and ``study build``.

Spec section 3.14 lists eight commands. Four of them exist today, and only those four have a
parser: ``study run`` and ``study score`` arrive with the study in Phase 12, ``verifier-eval``
with Phase 13, and ``mcp`` with Phase 15. A flag that parses and then says "not implemented" is
worse than no flag, because a reader of ``--help`` cannot tell the difference between what this
program does and what it is going to do; the Phase 0 design paragraph on half-built flag surfaces
is the whole argument, and it applies here (D-082). ``study`` therefore takes exactly one action
today, and ``quaestor study run`` is an argparse "invalid choice" like any misspelling.

``study build`` is the one command whose implementation is not in this package. The seeded-defect
generator lives in ``eval/seed.py``, outside ``src/``, because the pipeline being measured must
not be able to import the thing that plants the defects; so the command loads it from beside the
taxonomy it was given, and says so when it is not there (DECISIONS D-127).

**Exit codes**, which are the interface a script sees:

* ``0`` -- the command did what it was asked.
* ``1`` -- the command ran and did not produce what it was asked for: a validation the renderer
  refused, a tool whose inputs are not there, an ingest whose outline does not match its document.
  The run directory holds the trace of how far it got.
* ``2`` -- the request itself was wrong: a flag, a missing package, a package that does not load,
  a PDF that is not where the command says it is. Nothing was run.

Every message written to standard error names the command that fixes it, which is spec section
3.1's rule about error messages applied to the program's own front door.
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
    "SEED_MODULE",
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

_SEED_ALIAS: Final = "quaestor_eval_seed"
"""What ``eval/seed.py`` is imported as, so it does not collide with anything on the path."""

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
    """Add ``quaestor study build``: the seeded-defect variants of `04` section 2.

    ``build`` is the only action, so ``quaestor study run`` and ``quaestor study score`` are
    argparse "invalid choice" errors until Phase 12 writes them, which is what D-082 asks of every
    command that does not exist yet.
    """
    study_parser = commands.add_parser(
        "study",
        help="build the seeded-defect variants the evaluation runs on",
        description=(
            "The seeded-defect study of 04-SEEDED-DEFECT-STUDY.md. Only `build` exists today: it "
            "writes one variant package per row of the taxonomy, each with a SEED.yaml recording "
            "what was done to it that no validation run ever reads. `run` and `score` are Phase "
            "12."
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
    build_parser.set_defaults(run=_run_study_build)


def _load_seed_module(directory: Path) -> ModuleType:
    """Import ``eval/seed.py`` from a directory, under an alias of its own.

    Args:
        directory: Where the taxonomy is, which is where the generator is looked for.

    Returns:
        The loaded module.

    Raises:
        PackageError: There is no ``seed.py`` there, or it does not import.
    """
    path = directory / SEED_MODULE
    if not path.is_file():
        raise PackageError(
            f"there is no {SEED_MODULE} beside {directory}, so there is no seeded-defect "
            "generator to run; `quaestor study build` works inside a checkout of this "
            "repository, where eval/seed.py sits next to eval/taxonomy.yaml",
            fix="quaestor study build --taxonomy eval/taxonomy.yaml --out eval/variants",
        )
    spec = importlib.util.spec_from_file_location(_SEED_ALIAS, path)
    if spec is None or spec.loader is None:  # pragma: no cover - a file that is not importable
        raise PackageError(f"{path} is not importable as a module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[_SEED_ALIAS] = module
    spec.loader.exec_module(module)
    return module


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
    try:
        taxonomy = seed_module.load_taxonomy(taxonomy_path)
        results: list[Any] = seed_module.build_all(
            taxonomy,
            args.out,
            subjects_dir=subjects,
            synthetic_n=seed_module.synthetic_sizes(taxonomy, args.synthetic),
        )
    except (ValueError, KeyError, OSError) as exc:
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
            print(f"{result.spec.id}: dropped ({result.spec.dropped_reason})")
    print(f"{built} variant(s) under {args.out}; {len(results) - built} dropped")
    return EXIT_OK


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
