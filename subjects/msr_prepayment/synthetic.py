"""The synthetic panel, for a human: `python synthetic.py --n 2000 --out DIR`.

The generating process itself is `code/synthetic.py`, because `quaestor.sandbox.run_model` copies
only `code/` into the subprocess's working tree and the subject has to be able to draw its own
panel in there (DECISIONS D-029). This file is the entry point named in the repository layout: it
re-exports :class:`SyntheticProcess`, :func:`generate` and :func:`rate_path` under the subject's
root so that a reader who wants to look at the data can write the panel and the rate calendar
without knowing about the sandbox, and it carries the loader the test suite uses to import out of
`code/` without the standard library's `code` module being shadowed for the whole process.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

SUBJECT_DIR = Path(__file__).resolve().parent
CODE_DIR = SUBJECT_DIR / "code"
PACKAGE_ALIAS = "msr_prepayment_code"
"""The name `code/` is imported under here. Inside the sandbox it is imported as `code` instead."""


def load_code_module(name: str) -> ModuleType:
    """Import one module out of `code/` under an alias, so `import code` still means the stdlib.

    The sandbox runs the subject as `python -m code.run`, where the package really is called
    `code` and shadowing the standard library module for one subprocess is harmless. Outside the
    sandbox -- here, in `sample_freddie.py`, in the test suite -- that shadowing would last for
    the whole process, so the package is loaded from its path under an alias instead, with its
    search path set so that the relative imports inside it keep working. The alias differs from
    the sibling subject's, so both subjects can be loaded into one test session.
    """
    if PACKAGE_ALIAS not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            PACKAGE_ALIAS,
            CODE_DIR / "__init__.py",
            submodule_search_locations=[str(CODE_DIR)],
        )
        if spec is None or spec.loader is None:  # pragma: no cover - a missing code/ is a defect
            raise SystemExit(f"{CODE_DIR} is not importable; the subject is incomplete")
        package = importlib.util.module_from_spec(spec)
        sys.modules[PACKAGE_ALIAS] = package
        spec.loader.exec_module(package)
    return importlib.import_module(f"{PACKAGE_ALIAS}.{name}")


_synthetic = load_code_module("synthetic")
_features = load_code_module("features")

SyntheticProcess = _synthetic.SyntheticProcess
generate = _synthetic.generate
engineered = _synthetic.engineered
rate_path = _synthetic.rate_path
DEFAULT_SEED = _synthetic.DEFAULT_SEED
build_panel = _features.build_panel

__all__ = [
    "DEFAULT_SEED",
    "SyntheticProcess",
    "build_panel",
    "engineered",
    "generate",
    "load_code_module",
    "main",
    "rate_path",
]


def main(argv: list[str] | None = None) -> int:
    """Write one synthetic panel and its rate calendar to a directory. Returns an exit code."""
    parser = argparse.ArgumentParser(
        prog="python synthetic.py",
        description="Draw a synthetic msr_prepayment panel from the known hazard.",
    )
    parser.add_argument("--n", type=int, default=2000, help="how many loans (default 2000)")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="the process seed")
    parser.add_argument("--out", required=True, help="a directory to write the two CSVs into")
    parser.add_argument(
        "--raw",
        action="store_true",
        help="write the raw loan-month schema instead of the twelve engineered features",
    )
    args = parser.parse_args(argv)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    process = SyntheticProcess(n_loans=args.n, seed=args.seed)
    raw, rates = generate(process)
    panel = raw if args.raw else build_panel(raw, rates)
    for name, frame in (("panel.csv", panel), ("rates.csv", rates)):
        frame.to_csv(out_dir / name, index=False, float_format="%.10g", lineterminator="\n")
        print(f"wrote {len(frame)} rows and {len(frame.columns)} columns to {out_dir / name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
