"""The standard artifact contract of spec section 3.3: what a subject run must have written.

Everything downstream of the sandbox consumes these files and nothing else, which is what makes
one set of tools generic across a binary classifier, a discrete-time hazard model and every
seeded variant. So the contract is checked immediately after the subprocess exits, before any
tool runs: a missing or malformed file is a :class:`~quaestor.errors.SandboxError` that names the
file, the field and, where one exists, the flag to re-run with.

The check is deliberately shallow. It asks whether a file is present, parses, and carries the keys
and column names the contract fixes; it does not ask whether the numbers in it are right. The
developer's own ``metrics.json`` is never trusted -- Quaestor recomputes every metric from
``predictions_<split>.csv`` in Phase 5 -- so validating its values here would be checking the
wrong thing in the wrong place.

One transformation happens on the way into the artifact store. ``features.json`` is a list on
disk, as the spec fixes it, and a list has no addressable count: ``[[art:...:run.features#n]]``,
which the golden report writes, cannot resolve against it. So the artifact built from that file is
an object carrying ``n``, one count per feature timing, and the list itself under ``items``
(DECISIONS D-026).
"""

from __future__ import annotations

import csv
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Final

from pydantic import BaseModel, ConfigDict

from ..artifacts import ArtifactKind
from ..errors import SandboxError
from ..package import FeatureTiming, ModelType, PackageSpec

__all__ = [
    "CONTRACT_JSON_FILES",
    "ContractFile",
    "features_artifact",
    "read_contract",
    "required_files",
]

CONTRACT_JSON_FILES: Final = ("splits.json", "features.json", "metrics.json", "model_summary.json")
"""The four JSON files every subject writes, whatever its model type."""

_ROWS_HASH_LENGTH: Final = 64
"""``splits.json`` carries a full SHA-256 of the sorted identifiers, not a ``stable_hash``."""

_PREDICTION_COLUMNS: Final = ("y_true", "y_score")
"""The two columns every ``predictions_<split>.csv`` carries beside the identifier."""

_FIX = "quaestor validate <package> --synthetic 5000 --out <dir>, then inspect <dir>"
"""What to do about a contract violation: re-run and look at what the subject actually wrote."""


class ContractFile(BaseModel):
    """One file of the contract, parsed and ready for the artifact store.

    Attributes:
        name: The file name inside the run's output directory.
        logical_name: The artifact name it is stored under, always ``run.<stem>``.
        kind: ``json`` for the four JSON files, ``table`` for the CSVs.
        payload: The parsed payload, as :meth:`ArtifactStore.put` wants it -- the decoded object
            for a JSON file, a list of row mappings for a CSV.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    logical_name: str
    kind: ArtifactKind
    payload: Any


def required_files(spec: PackageSpec) -> list[str]:
    """Return the file names this package's subject must write, in report order.

    Args:
        spec: The parsed ``package.yaml``. Its declared splits decide how many prediction and
            data files there are, and its model type decides whether ``projection.json`` is
            required.

    Returns:
        The required file names.
    """
    names = list(CONTRACT_JSON_FILES)
    for split in spec.splits.names():
        names.append(f"predictions_{split}.csv")
        names.append(f"data_{split}.csv")
    if spec.model_type is ModelType.discrete_time_hazard:
        names.append("projection.json")
    return names


def read_contract(spec: PackageSpec, out_dir: Path) -> list[ContractFile]:
    """Check every required file and return them parsed, in the order of :func:`required_files`.

    Args:
        spec: The parsed ``package.yaml``.
        out_dir: Where the subject wrote.

    Returns:
        One :class:`ContractFile` per required file.

    Raises:
        SandboxError: A required file is missing, does not parse, or does not carry what the
            contract fixes. The message names the file.
    """
    files: list[ContractFile] = []
    for name in required_files(spec):
        path = out_dir / name
        if not path.is_file():
            raise SandboxError(
                f"the subject of package {spec.name!r} did not write {name} to {out_dir}; spec "
                f"3.3 requires {required_files(spec)}",
                fix=_FIX,
            )
        files.append(_read_one(spec, path))
    return files


def _read_one(spec: PackageSpec, path: Path) -> ContractFile:
    """Parse and validate one contract file, dispatching on its name."""
    name = path.name
    if name.endswith(".csv"):
        rows = _read_csv(path)
        if name.startswith("predictions_"):
            _check_predictions(spec, path, rows)
        else:
            _check_data(spec, path, rows)
        return ContractFile(
            name=name, logical_name=_logical(name), kind=ArtifactKind.table, payload=rows
        )
    payload = _read_json(path)
    checkers = {
        "splits.json": _check_splits,
        "features.json": _check_features,
        "metrics.json": _check_metrics,
        "model_summary.json": _check_model_summary,
        "projection.json": _check_projection,
    }
    checkers[name](spec, path, payload)
    stored = features_artifact(payload) if name == "features.json" else payload
    return ContractFile(
        name=name, logical_name=_logical(name), kind=ArtifactKind.json, payload=stored
    )


def _logical(name: str) -> str:
    """Return the artifact name a contract file is stored under: ``run.<stem>``."""
    return f"run.{Path(name).stem}"


def features_artifact(payload: Any) -> dict[str, Any]:
    """Turn the ``features.json`` list into the object the store holds under ``run.features``.

    Args:
        payload: The decoded ``features.json``, a list of ``{name, dtype, timing}`` objects.

    Returns:
        ``{"n": <count>, <timing>: <count>, ..., "items": [...]}``, with a key for every one of
        the four timings including the ones no feature declares, so that a report can cite the
        zero as evidence that nothing is declared ``after_outcome`` (DECISIONS D-026).
    """
    items = list(payload)
    counts = {timing.value: 0 for timing in FeatureTiming}
    for item in items:
        timing = str(item.get("timing", ""))
        if timing in counts:
            counts[timing] += 1
    return {"n": len(items), **counts, "items": items}


def _malformed(path: Path, detail: str) -> SandboxError:
    """Build the one error shape this module raises, naming the file and what is wrong with it."""
    return SandboxError(f"{path} does not satisfy the spec 3.3 contract: {detail}", fix=_FIX)


def _read_json(path: Path) -> Any:
    """Read one JSON contract file, attributing a parse error to the file."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise _malformed(path, f"it is not JSON ({exc})") from exc
    except UnicodeDecodeError as exc:
        raise _malformed(path, "it is not UTF-8 text") from exc


def _read_csv(path: Path) -> list[dict[str, str]]:
    """Read one CSV contract file into row mappings, insisting it has a header and a row."""
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise _malformed(path, "it is not UTF-8 text") from exc
    reader = csv.DictReader(text.splitlines())
    if not reader.fieldnames:
        raise _malformed(path, "it has no header row")
    rows = [dict(row) for row in reader]
    if not rows:
        raise _malformed(path, "it has a header but no rows")
    for number, row in enumerate(rows, start=2):
        if None in row or any(value is None for value in row.values()):
            raise _malformed(path, f"line {number} has fewer fields than the header")
    return rows


def _mapping(path: Path, payload: Any, what: str) -> Mapping[str, Any]:
    """Insist that a payload is a JSON object."""
    if not isinstance(payload, Mapping):
        raise _malformed(path, f"{what} is a {type(payload).__name__}, not an object")
    return payload


def _number(path: Path, value: Any, what: str) -> float:
    """Insist that a value is a real number, which every metric and coefficient is."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise _malformed(path, f"{what} is {value!r}, not a number")
    return float(value)


def _check_splits(spec: PackageSpec, path: Path, payload: Any) -> None:
    """``{split: {"n", "event_rate", "rows_hash"}}`` for every declared split."""
    splits = _mapping(path, payload, "the file")
    for split in spec.splits.names():
        if split not in splits:
            raise _malformed(
                path, f"it has no entry for the declared split {split!r}; it has {sorted(splits)}"
            )
        entry = _mapping(path, splits[split], f"{split!r}")
        for key in ("n", "event_rate", "rows_hash"):
            if key not in entry:
                raise _malformed(path, f"{split!r} has no {key!r}")
        if not isinstance(entry["n"], int) or isinstance(entry["n"], bool) or entry["n"] < 0:
            raise _malformed(path, f"{split}.n is {entry['n']!r}, not a row count")
        rate = _number(path, entry["event_rate"], f"{split}.event_rate")
        if not 0.0 <= rate <= 1.0:
            raise _malformed(path, f"{split}.event_rate is {rate}, which is not a rate in [0, 1]")
        digest = entry["rows_hash"]
        if not isinstance(digest, str) or len(digest) != _ROWS_HASH_LENGTH:
            raise _malformed(
                path,
                f"{split}.rows_hash is {digest!r}, not the {_ROWS_HASH_LENGTH}-character SHA-256 "
                "of the split's sorted identifiers",
            )


def _check_features(spec: PackageSpec, path: Path, payload: Any) -> None:
    """``[{"name", "dtype", "timing"}]``, covering the features ``package.yaml`` declares."""
    if not isinstance(payload, Sequence) or isinstance(payload, (str, bytes)):
        raise _malformed(path, f"the file is a {type(payload).__name__}, not a list of features")
    if not payload:
        raise _malformed(path, "it declares no features")
    timings = {timing.value for timing in FeatureTiming}
    written = []
    for position, item in enumerate(payload):
        entry = _mapping(path, item, f"element {position}")
        for key in ("name", "dtype", "timing"):
            if key not in entry:
                raise _malformed(path, f"element {position} has no {key!r}")
        if entry["timing"] not in timings:
            raise _malformed(
                path,
                f"element {position} declares timing {entry['timing']!r}, which is not one of "
                f"{sorted(timings)}",
            )
        written.append(str(entry["name"]))
    undeclared = sorted(set(written) - set(spec.feature_names))
    if undeclared:
        raise _malformed(
            path,
            f"it names the features {undeclared}, which package.yaml does not declare; a check "
            "cannot read a timing for a feature that has none",
        )


def _check_metrics(spec: PackageSpec, path: Path, payload: Any) -> None:
    """``{split: {metric: number}}``: the developer's own metrics, recomputed later, never used."""
    metrics = _mapping(path, payload, "the file")
    for split in spec.splits.names():
        if split not in metrics:
            raise _malformed(
                path,
                f"it has no metrics for the declared split {split!r}; it has {sorted(metrics)}",
            )
        entry = _mapping(path, metrics[split], f"{split!r}")
        if not entry:
            raise _malformed(path, f"{split!r} carries no metrics")
        for key, value in entry.items():
            _number(path, value, f"{split}.{key}")


def _check_model_summary(spec: PackageSpec, path: Path, payload: Any) -> None:
    """``{"coefficients": [{"feature", "value"}], "removed": [{"feature", "vif"}]}``."""
    summary = _mapping(path, payload, "the file")
    if "coefficients" not in summary:
        raise _malformed(path, "it has no 'coefficients'; spec 3.3 requires the fitted values")
    _check_named_numbers(path, summary["coefficients"], "coefficients", "value")
    if summary.get("removed") is not None:
        _check_named_numbers(path, summary["removed"], "removed", "vif")
    if spec.model_type is ModelType.discrete_time_hazard and "baseline_hazard" not in summary:
        raise _malformed(
            path, "a discrete_time_hazard subject must also write 'baseline_hazard' (spec 3.3)"
        )


def _check_named_numbers(path: Path, payload: Any, what: str, value_key: str) -> None:
    """Check a ``[{"feature": name, "<value_key>": number}]`` list, as spec 3.3 shapes both."""
    if not isinstance(payload, Sequence) or isinstance(payload, (str, bytes)):
        raise _malformed(path, f"{what!r} is a {type(payload).__name__}, not a list")
    for position, item in enumerate(payload):
        entry = _mapping(path, item, f"{what}[{position}]")
        if "feature" not in entry:
            raise _malformed(path, f"{what}[{position}] has no 'feature'")
        if value_key not in entry:
            raise _malformed(path, f"{what}[{position}] has no {value_key!r}")
        _number(path, entry[value_key], f"{what}[{position}].{value_key}")


def _check_projection(spec: PackageSpec, path: Path, payload: Any) -> None:
    """Hazard only: surviving balance by month under each declared shock, plus its valuation."""
    projection = _mapping(path, payload, "the file")
    for key in ("value_by_shock", "balance_by_month"):
        if key not in projection:
            raise _malformed(path, f"it has no {key!r}; spec 4.2 requires both")
    shocks = _mapping(path, projection["value_by_shock"], "'value_by_shock'")
    declared = spec.scenarios.rate_shocks_bp if spec.scenarios else []
    missing = [shock for shock in declared if str(shock) not in shocks]
    if missing:
        raise _malformed(path, f"'value_by_shock' has no entry for the declared shocks {missing}")


def _id_columns(spec: PackageSpec) -> tuple[str, ...]:
    """Return the two spellings of the identifier column a contract CSV may use.

    Spec 3.3 writes the column as ``id``; a subject that writes the identifier its own
    ``package.yaml`` declares -- ``client_id``, ``loan_id`` -- is saying the same thing more
    usefully, and both are accepted (DECISIONS D-032).
    """
    return ("id", spec.data.id_column)


def _check_predictions(spec: PackageSpec, path: Path, rows: list[dict[str, str]]) -> None:
    """``id, [time], y_true, y_score``, with a probability and an outcome on every row."""
    columns = list(rows[0])
    if not any(name in columns for name in _id_columns(spec)):
        raise _malformed(
            path, f"it has no identifier column; expected one of {list(_id_columns(spec))}"
        )
    for name in _PREDICTION_COLUMNS:
        if name not in columns:
            raise _malformed(path, f"it has no {name!r} column; it has {columns}")
    if spec.data.time_column is not None and spec.data.time_column not in columns:
        raise _malformed(
            path,
            f"the package declares data.time_column {spec.data.time_column!r}, which a hazard "
            f"subject writes one row per; the file has {columns}",
        )
    for number, row in enumerate(rows, start=2):
        score = _csv_float(path, row["y_score"], number, "y_score")
        if not 0.0 <= score <= 1.0:
            raise _malformed(path, f"line {number} has y_score {score}, which is not a probability")
        truth = _csv_float(path, row["y_true"], number, "y_true")
        if truth not in (0.0, 1.0):
            raise _malformed(path, f"line {number} has y_true {row['y_true']!r}, not 0 or 1")


def _check_data(spec: PackageSpec, path: Path, rows: list[dict[str, str]]) -> None:
    """Check the post-screen matrix: the identifier and at least one declared feature."""
    columns = list(rows[0])
    if not any(name in columns for name in _id_columns(spec)):
        raise _malformed(
            path, f"it has no identifier column; expected one of {list(_id_columns(spec))}"
        )
    present = [name for name in spec.feature_names if name in columns]
    if not present:
        raise _malformed(
            path,
            f"it holds none of the declared features {spec.feature_names}, so no drift, "
            f"collinearity or leakage screen can read it; it has {columns}",
        )


def _csv_float(path: Path, raw: str, line: int, column: str) -> float:
    """Parse one numeric CSV cell, naming the line and the column when it is not a number."""
    try:
        return float(raw)
    except ValueError as exc:
        raise _malformed(path, f"line {line} has {column} {raw!r}, which is not a number") from exc
