"""Build the real sample from the UCI file: `python sample.py --raw DIR --out DIR`.

Never run by a test and never run in CI: `CLAUDE.md` forbids downloading data and forbids training
on real data inside `pytest`, so the suite covers this file for argument handling only. A human
downloads the UCI *Default of Credit Card Clients* dataset once, runs this script, pastes the
printed manifest into `package.yaml`, and from then on `quaestor validate subjects/credit_default
--data <dir>` verifies those digests before anything runs.

Two input forms are accepted, because the UCI distribution is a legacy `.xls` that pandas can only
read through `xlrd`, which is not a dependency of this project (DECISIONS D-027):

* `default of credit card clients.xls` -- read directly when `xlrd` happens to be importable;
* `default_of_credit_card_clients.csv` -- what the operator exports once from a spreadsheet
  otherwise. The failure message says exactly that.

The twelve features are engineered by `code/features.py`, the same function the synthetic mode
uses, and the split is the same `stratified_split` at the same declared seed. That is deliberate:
a feature must not be able to mean one thing on the real sample and another on the synthetic one.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pandas as pd


def _load_features() -> ModuleType:
    """Import `code/features.py` from its path, under a name that is not `code`.

    The sandbox runs the subject as `python -m code.run`, where the package really is called
    `code`; outside the sandbox that name would shadow the standard library module for the whole
    of this process. `code/features.py` imports nothing of its own, so it loads standalone --
    this script deliberately does not go through the subject-root `synthetic.py`, whose loader
    registers a package alias that a second subject's loader would collide with.
    """
    alias = "credit_default_features"
    if alias in sys.modules:
        return sys.modules[alias]
    path = Path(__file__).resolve().parent / "code" / "features.py"
    spec = importlib.util.spec_from_file_location(alias, path)
    if spec is None or spec.loader is None:  # pragma: no cover - a missing code/ is a defect
        raise SystemExit(f"{path} is not importable; the subject is incomplete")
    module = importlib.util.module_from_spec(spec)
    # Registered before it is executed, because a dataclass defined under
    # `from __future__ import annotations` resolves its own module out of `sys.modules`.
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


_features = _load_features()

XLS_NAME = "default of credit card clients.xls"
CSV_NAME = "default_of_credit_card_clients.csv"
DATASET_ID = 350
"""The UCI dataset id, quoted in `package.yaml` and in `README.md`."""

TARGET_SOURCE_COLUMNS = ("default payment next month", "default.payment.next.month", "Y")
"""The three spellings the target carries across the `.xls`, the CSV export and the raw header."""

EXPORT_ADVICE = (
    f"pandas cannot read {XLS_NAME!r} without `xlrd`, which is not a dependency of this "
    f"project. Open the file once in a spreadsheet and export it as {CSV_NAME!r} into the same "
    "directory, then run this script again."
)


def main(argv: list[str] | None = None) -> int:
    """Build `train.csv` and `test.csv` from the UCI file and print the manifest. Exit code."""
    args = parse_args(argv)
    raw_dir, out_dir = Path(args.raw), Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    source = resolve_source(raw_dir)
    raw = read_raw(source)
    canonical = to_canonical(raw)
    if args.max_clients is not None:
        canonical = canonical.head(args.max_clients)
    frame = _features.engineer(canonical)

    train, test = _features.stratified_split(
        frame[_features.ID_COLUMN].to_numpy(),
        frame[_features.TARGET_COLUMN].to_numpy(),
        seed=args.seed,
    )
    manifest = {}
    for split in (train, test):
        part = frame[frame[_features.ID_COLUMN].isin(split.ids)]
        path = out_dir / f"{split.name}.csv"
        part.to_csv(path, index=False, float_format="%.10g", lineterminator="\n")
        manifest[path.name] = sha256_file(path)
        print(
            f"wrote {path} ({split.n} clients, event rate "
            f"{part[_features.TARGET_COLUMN].mean():.4f})"
        )

    print("\npaste into package.yaml under data:\n")
    print("  manifest:")
    for name, digest in manifest.items():
        print(f'    {name}: "{digest}"')
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse the arguments. `--raw` and `--out` are both required; nothing is downloaded."""
    parser = argparse.ArgumentParser(
        prog="python sample.py",
        description=(
            f"Build the credit_default sample from the UCI dataset {DATASET_ID}. "
            "Downloads nothing: point --raw at the directory you downloaded into."
        ),
    )
    parser.add_argument(
        "--raw", required=True, help=f"a directory holding {XLS_NAME} or {CSV_NAME}"
    )
    parser.add_argument("--out", required=True, help="where to write train.csv and test.csv")
    parser.add_argument(
        "--seed",
        type=int,
        default=_features.DECLARED_SEED,
        help=f"the split seed (default {_features.DECLARED_SEED}, as package.yaml declares)",
    )
    parser.add_argument(
        "--max-clients",
        type=int,
        default=None,
        help="keep only the first N clients by identifier; the default keeps all 30,000",
    )
    return parser.parse_args(argv)


def xlrd_available() -> bool:
    """Whether `xlrd` can be imported, which decides whether the `.xls` can be read at all."""
    return importlib.util.find_spec("xlrd") is not None


def resolve_source(raw_dir: Path) -> Path:
    """Return the input file to read, preferring the CSV export over the legacy `.xls`.

    Raises `SystemExit` when neither form is present, or when only the `.xls` is present and
    `xlrd` is not importable, in which case the message is the one-off export instruction.
    """
    if not raw_dir.is_dir():
        raise SystemExit(f"{raw_dir} is not a directory; pass --raw <the download directory>")
    csv_path, xls_path = raw_dir / CSV_NAME, raw_dir / XLS_NAME
    if csv_path.is_file():
        return csv_path
    if xls_path.is_file():
        if not xlrd_available():
            raise SystemExit(EXPORT_ADVICE)
        return xls_path
    raise SystemExit(
        f"{raw_dir} holds neither {CSV_NAME!r} nor {XLS_NAME!r}; download UCI dataset "
        f"{DATASET_ID} (Default of Credit Card Clients, CC BY 4.0) into it first"
    )


def read_raw(source: Path) -> pd.DataFrame:
    """Read the UCI file with its real header row, whichever of the two forms it is."""
    if source.suffix == ".csv":
        frame = pd.read_csv(source)
        if "X1" in frame.columns or "Unnamed: 1" in frame.columns:
            frame = pd.read_csv(source, header=1)
        return frame
    return pd.read_excel(source, header=1)


def to_canonical(raw: pd.DataFrame) -> pd.DataFrame:
    """Rename the UCI columns into the canonical raw statement schema. No arithmetic but the codes.

    The UCI repayment-status columns are `PAY_0` for the most recent month and `PAY_2` to `PAY_6`
    for the five before it, coded -2 for no consumption, -1 for paid in full and 0 for revolving
    credit; only a positive value is a month past due, so the codes are floored at zero and
    nothing else about them is interpreted.
    """
    columns = {str(name).strip(): name for name in raw.columns}
    target = next((columns[name] for name in TARGET_SOURCE_COLUMNS if name in columns), None)
    if target is None:
        raise SystemExit(
            f"the file has no target column; expected one of {list(TARGET_SOURCE_COLUMNS)}, "
            f"found {sorted(columns)[:12]}..."
        )
    required = ["ID", "LIMIT_BAL", "AGE", "PAY_0", *(f"PAY_{i}" for i in range(2, 7))]
    required += [f"BILL_AMT{i}" for i in range(1, 7)] + [f"PAY_AMT{i}" for i in range(1, 7)]
    missing = [name for name in required if name not in columns]
    if missing:
        raise SystemExit(f"the file is missing the UCI columns {missing}")

    canonical = pd.DataFrame(
        {
            _features.ID_COLUMN: raw[columns["ID"]].astype("int64"),
            "limit_bal": raw[columns["LIMIT_BAL"]].astype(float),
            "age": raw[columns["AGE"]].astype("int64"),
        }
    )
    for index in range(1, 7):
        canonical[f"bill_amt_{index}"] = raw[columns[f"BILL_AMT{index}"]].astype(float)
        canonical[f"pay_amt_{index}"] = raw[columns[f"PAY_AMT{index}"]].astype(float)
    pay_status = ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]
    for index, name in enumerate(pay_status, start=1):
        canonical[f"delinq_{index}"] = raw[columns[name]].clip(lower=0).astype("int64")
    canonical[_features.TARGET_COLUMN] = raw[target].astype("int64")
    return canonical[[*_features.RAW_COLUMNS, _features.TARGET_COLUMN]]


def sha256_file(path: Path, chunk_bytes: int = 1 << 20) -> str:
    """Return a file's SHA-256 hex digest, the form `package.yaml`'s manifest records."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while chunk := handle.read(chunk_bytes):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    sys.exit(main())
