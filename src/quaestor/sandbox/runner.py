"""``run_model``: run a subject in a subprocess with caps, then check what it wrote.

Spec section 3.6. The subject is somebody else's code, and a validation run is not the place to
find out what it does to the process it is imported into, so it is never imported: it runs as a
subprocess whose working directory is a temporary copy of the package's ``code/``, whose
environment is scrubbed to four variables, whose wall clock is capped from ``runtime.max_seconds``
and whose address space is capped from ``runtime.max_memory_mb`` on the platforms that honour the
limit. Standard output and standard error are captured and stored, so a failed run is diagnosable
from the artifact store rather than from a terminal that has scrolled away.

Two things are deliberately not enforced here. The first is networking: an operating-system
sandbox is out of scope for v0.1, so the environment carries ``QUAESTOR_NO_NETWORK=1`` as a
declaration to a cooperating subject and the ``Dockerfile`` beside this module documents the
containerised path where the guarantee is real. The second is the memory cap on macOS, where
``RLIMIT_AS`` is not reliably enforced; there the run records ``memory_cap: unenforced`` and is
never failed for it (DECISIONS D-028).
"""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable
from enum import StrEnum
from pathlib import Path
from typing import Any, Final

from pydantic import BaseModel, ConfigDict

from ..artifacts import Artifact, ArtifactKind, ArtifactStore
from ..errors import SandboxError
from ..hashing import sha256_file, stable_hash
from ..package import ModelPackage
from ..trace import EventType, TraceWriter
from .contract import ContractFile, read_contract, required_files

__all__ = [
    "ARTIFACTS_DIRNAME",
    "MAX_CAPTURE_BYTES",
    "MemoryCap",
    "RunResult",
    "memory_cap_policy",
    "run_model",
]

ARTIFACTS_DIRNAME: Final = "artifacts"
"""Where ``run_model`` puts its store when the caller does not pass one (spec section 8)."""

MAX_CAPTURE_BYTES: Final = 64 * 1024
"""How much of each captured stream is kept. A subject that prints a megabyte gets truncated."""

TRUNCATION_MARKER: Final = "\n... [truncated by quaestor.sandbox at {kept} bytes of {total}]\n"
"""Appended to a truncated stream, so nobody reads a cut-off log as a complete one."""

_ENV_PASSTHROUGH: Final = ("PATH", "PYTHONPATH")
"""The only two variables inherited from the caller: enough to find an interpreter and its path."""

_PYTHON_TOKENS: Final = frozenset({"python", "python3", "py"})
"""Entrypoint words replaced by :data:`sys.executable`, so the subject runs in this virtualenv."""


class MemoryCap(StrEnum):
    """Whether the address-space cap was applied to the subprocess.

    Attributes:
        enforced: ``RLIMIT_AS`` was set to ``runtime.max_memory_mb`` in the child.
        unenforced: The platform does not honour the limit, so it was not set. Recorded on the
            result and in the trace, and printed in the report's Appendix C, because a cap that
            was never applied must not be quoted as if it had been.
    """

    enforced = "enforced"
    unenforced = "unenforced"


class RunResult(BaseModel):
    """What one subject run did, and what of it is now in the artifact store.

    Attributes:
        package: The package name, as declared.
        argv: The command that was run, after the entrypoint's ``python`` was resolved.
        out_dir: Where the subject wrote its contract files.
        data_mode: ``"synthetic"`` or ``"data"``.
        synthetic: How many rows were asked for, in synthetic mode.
        seed: The seed passed to the subject, or ``None`` when the subject's default was used.
        duration_s: Wall-clock seconds the subprocess took.
        returncode: Its exit status.
        stdout: Its captured standard output, truncated at :data:`MAX_CAPTURE_BYTES`.
        stderr: Its captured standard error, truncated the same way.
        memory_cap: Whether the address-space cap was applied.
        memory_cap_mb: The cap that was asked for, applied or not.
        max_seconds: The wall-clock cap that was applied.
        files: Contract file name to the artifact name it was stored under.
        artifacts: Every artifact this run put in the store, contract files included.
        unexpected_output: Files the subject wrote into ``out_dir`` that the contract does not
            name, relative to ``out_dir`` and sorted. Each is described by an artifact and is a
            flag rather than a failure: a subject that writes a figure has not broken anything.
        store_root: The store the artifacts went into.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    package: str
    argv: list[str]
    out_dir: Path
    data_mode: str
    synthetic: int | None
    seed: int | None
    duration_s: float
    returncode: int
    stdout: str
    stderr: str
    memory_cap: MemoryCap
    memory_cap_mb: int
    max_seconds: int
    files: dict[str, str]
    artifacts: list[Artifact]
    unexpected_output: list[str]
    store_root: Path

    @property
    def timed_out(self) -> bool:
        """Whether the run was killed for outrunning its wall-clock cap.

        Always ``False`` on a returned result: a killed run raises instead. The property exists so
        that the trace and a caller reading the exception's store can ask the same question.
        """
        return self.returncode == _TIMEOUT_RETURNCODE


_TIMEOUT_RETURNCODE: Final = -9
"""What a ``SIGKILL``ed process group reports; recorded on ``run.status`` for a killed run."""


def memory_cap_policy(platform: str | None = None) -> MemoryCap:
    """Return whether this platform's ``RLIMIT_AS`` is worth setting.

    Args:
        platform: A :data:`sys.platform` string; defaults to the running platform.

    Returns:
        :attr:`MemoryCap.enforced` on a platform where the limit both exists and is honoured, and
        :attr:`MemoryCap.unenforced` everywhere else.

    On macOS the limit exists and is not reliably enforced: the kernel does not fail an
    ``mmap`` of address space the process never touches, and numpy's BLAS reserves far more
    address space than it commits, so a cap that *were* honoured would kill a healthy 5,000-row
    fit while the cap as actually implemented stops nothing. Rather than set a limit whose effect
    depends on the machine, the policy is explicit and is recorded on every run (DECISIONS D-028).
    """
    name = platform if platform is not None else sys.platform
    if not name.startswith("linux"):
        return MemoryCap.unenforced
    try:
        import resource
    except ImportError:  # pragma: no cover - POSIX only, and linux always has it
        return MemoryCap.unenforced
    return MemoryCap.enforced if hasattr(resource, "RLIMIT_AS") else MemoryCap.unenforced


def _limiter(memory_cap_mb: int) -> Callable[[], None]:
    """Build the ``preexec_fn`` that caps the child's address space.

    Runs in the forked child between ``fork`` and ``exec``, which is the only place a limit can be
    applied to the child alone. A failure to set it is swallowed: the cap is a guard against a
    runaway subject, not a correctness requirement, and no run is ever failed because a platform
    would not take the limit.
    """

    def apply() -> None:  # pragma: no cover - runs in the forked child, not in this process
        import resource

        limit = memory_cap_mb * 1024 * 1024
        try:
            resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
        except (ValueError, OSError):
            pass

    return apply


def build_argv(
    entrypoint: str,
    out_dir: Path,
    *,
    data_dir: Path | None,
    synthetic: int | None,
    seed: int | None,
) -> list[str]:
    """Turn ``package.yaml``'s entrypoint into an argument vector.

    Args:
        entrypoint: The declared command, ``python -m code.run`` by convention.
        out_dir: Passed as ``--out``; absolute, because the subprocess runs elsewhere.
        data_dir: Passed as ``--data`` when given.
        synthetic: Passed as ``--synthetic`` when given.
        seed: Passed as ``--seed`` when given, so that a subject's own declared default is used
            when the caller does not care.

    Returns:
        The argument vector, with a leading ``python`` replaced by this interpreter so that the
        subject runs against the same installed scikit-learn the validator was tested with.

    Raises:
        SandboxError: The entrypoint is empty.
    """
    words = shlex.split(entrypoint)
    if not words:
        raise SandboxError(
            "the package declares an empty entrypoint; spec 3.2 expects something like "
            "'python -m code.run'"
        )
    if words[0] in _PYTHON_TOKENS:
        words[0] = sys.executable
    argv = [*words, "--out", str(out_dir.resolve())]
    if synthetic is not None:
        argv += ["--synthetic", str(synthetic)]
    if data_dir is not None:
        argv += ["--data", str(Path(data_dir).resolve())]
    if seed is not None:
        argv += ["--seed", str(seed)]
    return argv


def _truncate(stream: str) -> str:
    """Keep the head of a captured stream, marking it when there was more."""
    encoded = stream.encode("utf-8", errors="replace")
    if len(encoded) <= MAX_CAPTURE_BYTES:
        return stream
    kept = encoded[:MAX_CAPTURE_BYTES].decode("utf-8", errors="ignore")
    return kept + TRUNCATION_MARKER.format(kept=MAX_CAPTURE_BYTES, total=len(encoded))


def _extras(out_dir: Path, expected: list[str], store_root: Path) -> list[str]:
    """Return everything in ``out_dir`` the contract does not name, relative and sorted.

    The store is excluded whether or not it lives inside ``out_dir``: it is Quaestor's own, and a
    previous run's index turning up as this run's unexpected output would be an accusation
    against the wrong process.
    """
    known = set(expected)
    found = []
    for path in sorted(out_dir.rglob("*")):
        if not path.is_file():
            continue
        if store_root == path.parent or store_root in path.parents:
            continue
        relative = path.relative_to(out_dir).as_posix()
        if relative not in known:
            found.append(relative)
    return found


def _unexpected_name(relative: str) -> str:
    """Return the artifact name an unexpected file is described under.

    ``figures/roc.png`` becomes ``run.unexpected.figures.roc.png``: both the directory separator
    and the extension's dot are already the store's segment separator, and every other character
    a logical name does not admit becomes an underscore, so a file called ``odd name!.txt`` still
    gets a citable artifact.
    """
    segments = [
        "".join(
            character if character.isalnum() or character in "_+-" else "_" for character in part
        )
        for part in relative.replace(".", "/").split("/")
        if part
    ]
    return ".".join(["run", "unexpected", *segments])


def _describe_unexpected(path: Path, relative: str) -> dict[str, Any]:
    """Describe an unexpected file: what it is called, how big it is, and its text if it has any.

    The bytes themselves are not copied into the store. The store's kinds are a scalar, a table, a
    JSON object and a figure, and an arbitrary file a subject chose to write is none of those; the
    file is still where the subject wrote it, and what a finding needs to cite is that it exists,
    how large it is and what it says.
    """
    blob = path.read_bytes()
    description: dict[str, Any] = {
        "file": relative,
        "bytes": len(blob),
        "sha256": sha256_file(path),
    }
    if len(blob) <= MAX_CAPTURE_BYTES:
        try:
            description["text"] = blob.decode("utf-8")
        except UnicodeDecodeError:
            description["text"] = None
    return description


def run_model(
    package: ModelPackage,
    data_dir: Path | str | None = None,
    out_dir: Path | str | None = None,
    *,
    synthetic: int | None = None,
    seed: int | None = None,
    store: ArtifactStore | None = None,
    trace: TraceWriter | None = None,
) -> RunResult:
    """Run a package's subject in a capped subprocess and store what it wrote.

    Args:
        package: The loaded package. Its ``code/`` is copied, its ``entrypoint`` is run and its
            ``runtime`` block supplies both caps.
        data_dir: Where the subject's real data is, for a ``--data`` run.
        out_dir: Where the subject writes the contract files of spec 3.3. Created if absent.
        synthetic: How many rows to generate, for a ``--synthetic`` run. Exactly one of
            ``data_dir`` and ``synthetic`` must be given.
        seed: Passed to the subject as ``--seed``; ``None`` leaves the subject's declared default.
        store: Where the run's artifacts go. Defaults to a store at ``<out_dir>/artifacts``.
        trace: When given, one ``tool_call`` event is emitted for the run, successful or not.

    Returns:
        The run's result, with the stored artifacts.

    Raises:
        SandboxError: Neither or both of ``data_dir`` and ``synthetic`` were given; the package
            has no ``code/``; the subject exited non-zero; it outran its wall-clock cap; or it did
            not write the contract of spec 3.3. In every case ``run.stdout``, ``run.stderr``,
            ``run.duration_s`` and ``run.status`` are in the store before the error is raised, so
            that the caller can raise an evidenced ``R0`` finding candidate.
    """
    if (data_dir is None) == (synthetic is None):
        raise SandboxError(
            f"run_model on package {package.name!r} needs exactly one of a data directory and a "
            f"synthetic row count, not {'both' if synthetic is not None else 'neither'}",
            fix="quaestor validate <package> --synthetic 5000 --out <dir>",
        )
    if out_dir is None:
        raise SandboxError(f"run_model on package {package.name!r} needs an output directory")
    if not package.code_dir.is_dir():
        raise SandboxError(
            f"package {package.name!r} has no code/ directory at {package.code_dir}, so there is "
            f"nothing for {package.spec.entrypoint!r} to run"
        )

    resolved_out = Path(out_dir)
    resolved_out.mkdir(parents=True, exist_ok=True)
    store_root = store.root if store is not None else resolved_out / ARTIFACTS_DIRNAME
    argv = build_argv(
        package.spec.entrypoint,
        resolved_out,
        data_dir=Path(data_dir) if data_dir is not None else None,
        synthetic=synthetic,
        seed=seed,
    )
    runtime = package.spec.runtime
    cap = memory_cap_policy()

    work = Path(tempfile.mkdtemp(prefix=f"quaestor-{package.name}-"))
    try:
        shutil.copytree(package.code_dir, work / package.code_dir.name)
        home = work / "home"
        home.mkdir()
        stdout, stderr, returncode, duration = _execute(
            argv,
            work=work,
            home=home,
            runtime_seconds=runtime.max_seconds,
            cap=cap,
            memory_cap_mb=runtime.max_memory_mb,
        )
    finally:
        shutil.rmtree(work, ignore_errors=True)

    resolved_store = store if store is not None else ArtifactStore(store_root)
    artifacts = [
        resolved_store.put("run.stdout", stdout, ArtifactKind.json, "the subject's stdout"),
        resolved_store.put("run.stderr", stderr, ArtifactKind.json, "the subject's stderr"),
        resolved_store.put(
            "run.duration_s", duration, ArtifactKind.scalar, "subject wall-clock seconds"
        ),
        resolved_store.put(
            "run.status",
            {
                "returncode": returncode,
                "timed_out": returncode == _TIMEOUT_RETURNCODE,
                "memory_cap": cap.value,
                "memory_cap_mb": runtime.max_memory_mb,
                "max_seconds": runtime.max_seconds,
                "data_mode": "synthetic" if synthetic is not None else "data",
                "synthetic": synthetic,
                "seed": seed,
            },
            ArtifactKind.json,
            "how the subject's subprocess ended",
        ),
    ]

    def emit(**fields: Any) -> None:
        if trace is not None:
            trace.emit(
                EventType.tool_call,
                tool="run_model",
                args_hash=stable_hash(
                    {
                        "package": package.name,
                        "entrypoint": package.spec.entrypoint,
                        "synthetic": synthetic,
                        "seed": seed,
                        "data_dir": str(data_dir) if data_dir is not None else None,
                    }
                ),
                duration_s=duration,
                memory_cap=cap.value,
                **fields,
            )

    if returncode == _TIMEOUT_RETURNCODE:
        emit(artifacts=[artifact.hash for artifact in artifacts], ok=False, timed_out=True)
        raise SandboxError(
            f"the subject of package {package.name!r} outran its wall-clock cap of "
            f"{runtime.max_seconds} s and was killed after {duration:.1f} s; its output so far is "
            f"in the artifact store as run.stdout and run.stderr",
            fix="raise runtime.max_seconds in package.yaml, or make the subject faster",
        )
    if returncode != 0:
        emit(artifacts=[artifact.hash for artifact in artifacts], ok=False, timed_out=False)
        raise SandboxError(
            f"the subject of package {package.name!r} exited {returncode}; the command was "
            f"{shlex.join(argv)} and its standard error ends: {_tail(stderr)}",
            fix="run that command by hand in the package's code/ directory",
        )

    expected = required_files(package.spec)
    unexpected = _extras(resolved_out, expected, store_root)
    contract = read_contract(package.spec, resolved_out)
    artifacts += _store_contract(resolved_store, contract)
    for relative in unexpected:
        artifacts.append(
            resolved_store.put(
                _unexpected_name(relative),
                _describe_unexpected(resolved_out / relative, relative),
                ArtifactKind.json,
                f"unexpected output: {relative}",
            )
        )

    emit(
        artifacts=[artifact.hash for artifact in artifacts],
        ok=True,
        timed_out=False,
        unexpected_output=unexpected,
    )
    return RunResult(
        package=package.name,
        argv=argv,
        out_dir=resolved_out,
        data_mode="synthetic" if synthetic is not None else "data",
        synthetic=synthetic,
        seed=seed,
        duration_s=duration,
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
        memory_cap=cap,
        memory_cap_mb=runtime.max_memory_mb,
        max_seconds=runtime.max_seconds,
        files={item.name: item.logical_name for item in contract},
        artifacts=artifacts,
        unexpected_output=unexpected,
        store_root=resolved_store.root,
    )


def _store_contract(store: ArtifactStore, contract: list[ContractFile]) -> list[Artifact]:
    """Put every contract file in the store under ``run.<stem>``."""
    return [
        store.put(item.logical_name, item.payload, item.kind, f"the subject's {item.name}")
        for item in contract
    ]


def _execute(
    argv: list[str],
    *,
    work: Path,
    home: Path,
    runtime_seconds: int,
    cap: MemoryCap,
    memory_cap_mb: int,
) -> tuple[str, str, int, float]:
    """Run the argument vector under both caps and return its output, status and duration."""
    env = {name: os.environ[name] for name in _ENV_PASSTHROUGH if name in os.environ}
    env["HOME"] = str(home)
    env["QUAESTOR_NO_NETWORK"] = "1"
    started = time.monotonic()
    # The argument vector comes from the package's own declared entrypoint, never from a model.
    process = subprocess.Popen(
        argv,
        cwd=work,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        start_new_session=True,
        preexec_fn=_limiter(memory_cap_mb) if cap is MemoryCap.enforced else None,
    )
    try:
        stdout, stderr = process.communicate(timeout=runtime_seconds)
        returncode = process.returncode
    except subprocess.TimeoutExpired:
        _kill_group(process)
        stdout, stderr = process.communicate()
        returncode = _TIMEOUT_RETURNCODE
    duration = time.monotonic() - started
    return _truncate(stdout or ""), _truncate(stderr or ""), returncode, duration


def _kill_group(process: subprocess.Popen[str]) -> None:
    """Kill the subject's whole process group, so a subject that forked leaves nothing behind."""
    try:
        os.killpg(os.getpgid(process.pid), 9)
    except (ProcessLookupError, PermissionError):  # pragma: no cover - the child already exited
        process.kill()


def _tail(stream: str, lines: int = 3) -> str:
    """Return the last few non-empty lines of a stream, for an error message."""
    kept = [line for line in stream.strip().splitlines() if line.strip()][-lines:]
    return " / ".join(kept) if kept else "(nothing)"
