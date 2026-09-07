"""Building the variants the Phase 5 tool tests run against: a copied run, one edit, one context.

Every candidate rule of spec 3.7 is tested against the real subject twice: once as it is, which is
the negative case, and once with a single named edit to what it wrote, which is the positive one.
The edits are the ones `04-SEEDED-DEFECT-STUDY.md` section 2 describes -- an `after_outcome`
timing, a duplicated row, a shifted split, a reintroduced collinear column, a false declared
threshold, a sign-flipped projection -- applied here to the contract files rather than to the
subject's source, because the contract is all a tool ever reads.

Nothing here writes into a subject's own directory: a variant is a copy of the run directory and,
where a rule needs one, a copy of `package.yaml` beside an empty `code/`.
"""

from __future__ import annotations

import json
import shutil
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from quaestor import ArtifactStore, TraceWriter, load_package
from quaestor.tools import Thresholds, ToolContext

__all__ = [
    "context",
    "read_json",
    "variant_package",
    "write_csv",
    "write_json",
]

FLOAT_FORMAT = "%.10g"
"""The format both subjects write their CSVs with, so a perturbed file reads back the same way."""


def context(
    tmp_path: Path,
    package_dir: Path,
    run_dir: Path,
    *,
    thresholds: Thresholds | None = None,
    trace: bool = True,
) -> ToolContext:
    """Copy a run and return a tool context over the copy, with a store of its own.

    Args:
        tmp_path: The test's temporary directory.
        package_dir: The package to load; either a subject or a variant built by
            :func:`variant_package`.
        run_dir: The run directory to copy, usually one of the session fixtures.
        thresholds: Effective thresholds, defaulting to the spec 3.7 values.
        trace: Whether to give the context a trace writer.

    Returns:
        A context whose ``out_dir`` is a private copy of the run, safe to perturb.
    """
    out_dir = tmp_path / "run"
    if not out_dir.exists():
        shutil.copytree(run_dir, out_dir)
    store = ArtifactStore(tmp_path / "artifacts")
    writer = TraceWriter(tmp_path / "trace.jsonl", run_id="test-run") if trace else None
    return ToolContext(
        package=load_package(package_dir),
        store=store,
        out_dir=out_dir,
        trace=writer,
        thresholds=thresholds or Thresholds(),
    )


def variant_package(
    tmp_path: Path,
    package_dir: Path,
    mutate: Callable[[dict[str, Any]], None],
    *,
    name: str = "variant",
) -> Path:
    """Write a copy of a `package.yaml` with one edit applied, beside an empty `code/`.

    Args:
        tmp_path: The test's temporary directory.
        package_dir: The package to copy.
        mutate: Applied to the parsed `package.yaml` in place.
        name: The directory name to write under, so one test can build two variants.

    Returns:
        The variant package's directory.
    """
    root = tmp_path / name
    (root / "code").mkdir(parents=True, exist_ok=True)
    (root / "code" / "run.py").write_text(
        '"""Not a subject: a variant package.yaml for a tool test, never run."""\n',
        encoding="utf-8",
    )
    spec = yaml.safe_load((package_dir / "package.yaml").read_text(encoding="utf-8"))
    mutate(spec)
    (root / "package.yaml").write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")
    return root


def read_json(path: Path) -> Any:
    """Read one JSON file from a run directory."""
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Mapping[str, Any] | list[Any]) -> None:
    """Write one JSON file back into a run directory, as the subjects write theirs."""
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, frame: pd.DataFrame) -> None:
    """Write one CSV back into a run directory, with the subjects' own float format."""
    frame.to_csv(path, index=False, float_format=FLOAT_FORMAT, lineterminator="\n")
