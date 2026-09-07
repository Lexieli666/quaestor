"""Reading the spec 3.3 contract: the one place a tool turns a subject's files into frames.

Every tool consumes the standard artifact contract and nothing else -- that is what makes one set
of checks generic across a binary classifier, a discrete-time hazard model and every seeded
variant -- so the reading happens once, here, and each function raises a
:class:`~quaestor.errors.ToolError` that names the file and the tool's way out of it. The sandbox
has already checked these files for presence and schema (:mod:`quaestor.sandbox.contract`); what
this module adds is the numeric typing and the joins the checks need.

The identifier column has two admissible spellings, ``id`` and whatever ``package.yaml`` declares
(DECISIONS D-032), so nothing here hard-codes either.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from ..errors import ToolError
from ..package import ModelPackage
from .registry import ToolContext

__all__ = [
    "coefficients",
    "declared_features",
    "feature_frame",
    "id_columns",
    "key_columns",
    "model_summary",
    "predictions",
    "projection",
    "require_split",
    "scored_frame",
]

_FIX = "quaestor validate <package> --synthetic 5000 --out <dir>, then inspect <dir>"
"""What to do about a missing or unreadable contract file: re-run the subject and look."""


def require_split(ctx: ToolContext, split: str) -> str:
    """Check that a split name is one the package declares.

    Args:
        ctx: The run's context.
        split: The split name to check.

    Returns:
        The split name.

    Raises:
        ToolError: The package does not declare it; the message lists the ones it does.
    """
    if split not in ctx.splits:
        raise ToolError(
            f"package {ctx.package.name!r} does not declare a split named {split!r}; it declares "
            f"{ctx.splits}"
        )
    return split


def _read_csv(path: Path) -> pd.DataFrame:
    """Read one contract CSV, attributing a missing file or a parse failure to the file."""
    if not path.is_file():
        raise ToolError(
            f"{path} is missing, so no check can read it; the subject writes it as part of the "
            "spec 3.3 contract",
            fix=_FIX,
        )
    try:
        frame = pd.read_csv(path)
    except (ValueError, UnicodeDecodeError) as exc:
        raise ToolError(f"{path} is not readable as CSV: {exc}", fix=_FIX) from exc
    if frame.empty:
        raise ToolError(f"{path} has a header but no rows", fix=_FIX)
    return frame


def _read_json(path: Path) -> Any:
    """Read one contract JSON file, attributing a missing file or a parse failure to the file."""
    if not path.is_file():
        raise ToolError(
            f"{path} is missing, so no check can read it; the subject writes it as part of the "
            "spec 3.3 contract",
            fix=_FIX,
        )
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ToolError(f"{path} is not readable as JSON: {exc}", fix=_FIX) from exc


def id_columns(package: ModelPackage) -> tuple[str, str]:
    """Return the two admissible spellings of the identifier column.

    Args:
        package: The loaded package.

    Returns:
        ``("id", <the declared id column>)``.
    """
    return ("id", package.spec.data.id_column)


def key_columns(ctx: ToolContext, frame: pd.DataFrame) -> list[str]:
    """Return the columns that identify a row: the identifier, and the period for a hazard panel.

    Args:
        ctx: The run's context.
        frame: The frame to look in.

    Returns:
        The key columns present in the frame.

    Raises:
        ToolError: The frame carries neither spelling of the identifier column.
    """
    present = [name for name in id_columns(ctx.package) if name in frame.columns]
    if not present:
        raise ToolError(
            f"a contract file of package {ctx.package.name!r} has no identifier column; expected "
            f"one of {list(id_columns(ctx.package))}, found {list(frame.columns)}",
            fix=_FIX,
        )
    keys = present[:1]
    time_column = ctx.package.spec.data.time_column
    if time_column is not None and time_column in frame.columns:
        keys.append(time_column)
    return keys


def predictions(ctx: ToolContext, split: str) -> pd.DataFrame:
    """Return ``predictions_<split>.csv`` with ``y_true`` and ``y_score`` as numbers.

    Args:
        ctx: The run's context.
        split: The split to read.

    Returns:
        The frame, with ``y_true`` as ``int`` and ``y_score`` as ``float``.

    Raises:
        ToolError: The split is not declared, the file is missing, or a column is not numeric.
    """
    require_split(ctx, split)
    frame = _read_csv(ctx.out_dir / f"predictions_{split}.csv")
    for column in ("y_true", "y_score"):
        if column not in frame.columns:
            raise ToolError(
                f"predictions_{split}.csv of package {ctx.package.name!r} has no {column!r} "
                f"column; it has {list(frame.columns)}",
                fix=_FIX,
            )
    try:
        frame["y_true"] = frame["y_true"].astype(int)
        frame["y_score"] = frame["y_score"].astype(float)
    except (TypeError, ValueError) as exc:
        raise ToolError(
            f"predictions_{split}.csv of package {ctx.package.name!r} holds a non-numeric "
            f"y_true or y_score: {exc}",
            fix=_FIX,
        ) from exc
    return frame


def feature_frame(ctx: ToolContext, split: str) -> pd.DataFrame:
    """Return ``data_<split>.csv``: the feature matrix the subject actually used.

    Args:
        ctx: The run's context.
        split: The split to read.

    Returns:
        The frame as written, columns unchanged.

    Raises:
        ToolError: The split is not declared or the file is missing.
    """
    require_split(ctx, split)
    return _read_csv(ctx.out_dir / f"data_{split}.csv")


def declared_features(ctx: ToolContext, frame: pd.DataFrame) -> list[str]:
    """Return the declared features present in a frame, in ``package.yaml``'s declaration order.

    A subject's own screen removes features before fitting, so ``data_<split>.csv`` holds a subset
    of what ``package.yaml`` declares; the checks run on what the model actually used.

    Args:
        ctx: The run's context.
        frame: The frame to look in.

    Returns:
        The feature names present.

    Raises:
        ToolError: The frame holds none of the declared features, so no check can read it.
    """
    present = [name for name in ctx.package.spec.feature_names if name in frame.columns]
    if not present:
        raise ToolError(
            f"none of the features package {ctx.package.name!r} declares is in this contract "
            f"file, which has {list(frame.columns)}; no drift, collinearity or leakage screen can "
            "read it",
            fix=_FIX,
        )
    return present


def scored_frame(ctx: ToolContext, split: str) -> pd.DataFrame:
    """Return ``data_<split>.csv`` joined to its predictions on the identifier (and the period).

    Args:
        ctx: The run's context.
        split: The split to read.

    Returns:
        The joined frame, carrying the features, the target, ``y_true`` and ``y_score``.

    Raises:
        ToolError: Either file is missing, or the join leaves a row without a prediction, which
            means the two files disagree about what the split holds.
    """
    features = feature_frame(ctx, split)
    scores = predictions(ctx, split)
    keys = key_columns(ctx, features)
    missing = [key for key in keys if key not in scores.columns]
    if missing:
        raise ToolError(
            f"predictions_{split}.csv of package {ctx.package.name!r} has no {missing} column, so "
            f"it cannot be joined to data_{split}.csv on {keys}",
            fix=_FIX,
        )
    joined = features.merge(scores[[*keys, "y_true", "y_score"]], on=keys, how="left")
    if len(joined) != len(features) or joined["y_score"].isna().any():
        raise ToolError(
            f"data_{split}.csv and predictions_{split}.csv of package {ctx.package.name!r} do not "
            f"describe the same rows: joining on {keys} left "
            f"{int(joined['y_score'].isna().sum())} of {len(features)} rows unscored",
            fix=_FIX,
        )
    return joined


def model_summary(ctx: ToolContext) -> dict[str, Any]:
    """Return ``model_summary.json``.

    Args:
        ctx: The run's context.

    Returns:
        The decoded object.

    Raises:
        ToolError: The file is missing, unreadable, or not an object.
    """
    payload = _read_json(ctx.out_dir / "model_summary.json")
    if not isinstance(payload, dict):
        raise ToolError(
            f"model_summary.json of package {ctx.package.name!r} is a "
            f"{type(payload).__name__}, not an object",
            fix=_FIX,
        )
    return payload


def coefficients(ctx: ToolContext) -> dict[str, float]:
    """Return the champion's fitted coefficients or importances, keyed by feature.

    Args:
        ctx: The run's context.

    Returns:
        Feature name to value, in the order ``model_summary.json`` lists them. For a subject whose
        design expands a feature -- the hazard champion's spline on ``loan_age`` -- the expanded
        column names are what the file carries, and they are returned as they are.

    Raises:
        ToolError: The file has no ``coefficients`` list, or an entry is malformed.
    """
    summary = model_summary(ctx)
    raw = summary.get("coefficients")
    if not isinstance(raw, list):
        raise ToolError(
            f"model_summary.json of package {ctx.package.name!r} has no 'coefficients' list",
            fix=_FIX,
        )
    values: dict[str, float] = {}
    for position, entry in enumerate(raw):
        if not isinstance(entry, dict) or "feature" not in entry or "value" not in entry:
            raise ToolError(
                f"coefficients[{position}] of model_summary.json is {entry!r}, not "
                "{'feature': ..., 'value': ...}",
                fix=_FIX,
            )
        values[str(entry["feature"])] = float(entry["value"])
    return values


def projection(ctx: ToolContext) -> dict[str, Any]:
    """Return ``projection.json``, which only a hazard subject writes.

    Args:
        ctx: The run's context.

    Returns:
        The decoded object.

    Raises:
        ToolError: The file is missing or is not an object.
    """
    payload = _read_json(ctx.out_dir / "projection.json")
    if not isinstance(payload, dict):
        raise ToolError(
            f"projection.json of package {ctx.package.name!r} is a {type(payload).__name__}, not "
            "an object",
            fix=_FIX,
        )
    return payload
