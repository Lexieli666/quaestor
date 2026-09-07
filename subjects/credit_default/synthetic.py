"""The synthetic panel, for a human and for `sample.py`: `python synthetic.py --n 5000 --out F`.

The generating process itself is `code/synthetic.py`, because `quaestor.sandbox.run_model` copies
only `code/` into the subprocess's working tree and the subject has to be able to draw its own
panel in there (DECISIONS D-029). This file is the entry point named in the repository layout: it
re-exports :class:`SyntheticProcess` and :func:`generate` under the subject's root so that a
reader who wants to look at the data can write one CSV without knowing about the sandbox, and it
carries the loader both it and `sample.py` use to import out of `code/` without the standard
library's `code` module being shadowed for the whole process.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

SUBJECT_DIR = Path(__file__).resolve().parent
CODE_DIR = SUBJECT_DIR / "code"
PACKAGE_ALIAS = "credit_default_code"
"""The name `code/` is imported under here. Inside the sandbox it is imported as `code` instead."""


def load_code_module(name: str) -> ModuleType:
    """Import one module out of `code/` under an alias, so `import code` still means the stdlib.

    The sandbox runs the subject as `python -m code.run`, where the package really is called
    `code` and shadowing the standard library module for one subprocess is harmless. Outside the
    sandbox -- here, in `sample.py`, in the test suite -- that shadowing would last for the whole
    process, so the package is loaded from its path under an alias instead, with its search path
    set so that the relative imports inside it keep working.
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
DEFAULT_SEED = _synthetic.DEFAULT_SEED
engineer = _features.engineer

__all__ = [
    "DEFAULT_SEED",
    "SyntheticProcess",
    "engineer",
    "generate",
    "load_code_module",
    "main",
]


def main(argv: list[str] | None = None) -> int:
    """Write one synthetic panel to a CSV, raw or engineered. Returns an exit code."""
    parser = argparse.ArgumentParser(
        prog="python synthetic.py",
        description="Draw a synthetic credit_default panel from the known process.",
    )
    parser.add_argument("--n", type=int, default=5000, help="how many clients (default 5000)")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="the process seed")
    parser.add_argument("--out", required=True, help="where to write the CSV")
    parser.add_argument(
        "--engineered",
        action="store_true",
        help="write the twelve engineered features instead of the raw statement schema",
    )
    args = parser.parse_args(argv)
    frame = generate(SyntheticProcess(n_clients=args.n, seed=args.seed))
    if args.engineered:
        frame = engineer(frame)
    frame.to_csv(args.out, index=False, float_format="%.10g", lineterminator="\n")
    print(f"wrote {len(frame)} rows and {len(frame.columns)} columns to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
