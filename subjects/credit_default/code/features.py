"""The twelve engineered features, the stratified split and the VIF screen.

This module is the single definition of what the `credit_default` features *are*. Both data modes
go through it: `code/synthetic.py` renders the canonical raw statement schema below and
`code/run.py` engineers from it, while `sample.py` renames the UCI columns into the same raw
schema and calls the same `engineer`. A feature therefore cannot mean one thing on the real sample
and another on the synthetic panel.

Nothing here imports `quaestor`, and nothing here reads a file: the subject is an ordinary
scikit-learn pipeline that a model developer could have written, which is the point -- Quaestor
validates it from the outside, through the artifact contract of spec section 3.3.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

ID_COLUMN = "client_id"
TARGET_COLUMN = "default_next_month"

N_STATEMENTS = 6
"""How many statements of history the raw schema carries; index 1 is the most recent."""

RAW_COLUMNS: list[str] = (
    [ID_COLUMN, "limit_bal", "age"]
    + [f"bill_amt_{i}" for i in range(1, N_STATEMENTS + 1)]
    + [f"pay_amt_{i}" for i in range(1, N_STATEMENTS + 1)]
    + [f"delinq_{i}" for i in range(1, N_STATEMENTS + 1)]
)
"""The canonical raw schema: one row per client, six statements of history, oldest last."""

FEATURE_NAMES: list[str] = [
    "limit_bal",
    "age",
    "utilisation",
    "utilisation_mean_6m",
    "pay_ratio_last",
    "pay_ratio_mean_6m",
    "delinq_last",
    "delinq_count_6m",
    "delinq_max_6m",
    "bill_mean_6m",
    "bill_last",
    "bill_trend_6m",
]
"""The twelve features, in the declaration order of `package.yaml`, which the screen respects."""

FEATURE_TIMING: dict[str, str] = {
    "limit_bal": "at_origination",
    "age": "at_origination",
    "utilisation": "before_period_start",
    "utilisation_mean_6m": "before_period_start",
    "pay_ratio_last": "before_period_start",
    "pay_ratio_mean_6m": "before_period_start",
    "delinq_last": "before_period_start",
    "delinq_count_6m": "before_period_start",
    "delinq_max_6m": "before_period_start",
    "bill_mean_6m": "before_period_start",
    "bill_last": "before_period_start",
    "bill_trend_6m": "before_period_start",
}
"""The timing each feature is declared with in `package.yaml`; `features.json` repeats it."""

PAY_RATIO_CAP = 2.0
"""`pay_ratio_last` is capped at 2, as `package.yaml` says: a full repayment plus a credit."""

BALANCE_FLOOR = 1.0
"""The smallest denominator a payment ratio divides by, so a zero statement is not a division."""

VIF_THRESHOLD = 10.0
"""The screen's rule. `check_collinearity` raises `M1` at the same value (spec section 3.7)."""

VIF_CAP = 1.0e6
"""What a perfectly collinear feature's VIF is reported as, so the file holds a real number."""

DECLARED_SEED = 20260901
"""The seed `package.yaml` declares in its split rule; `--seed` overrides it."""

TEST_FRACTION = 0.3
"""`package.yaml`: a random 70% of clients for training, stratified on the target."""


@dataclass(frozen=True)
class Split:
    """One split of client identifiers, and the summary `splits.json` records for it."""

    name: str
    ids: np.ndarray

    @property
    def n(self) -> int:
        return int(self.ids.size)


def engineer(raw: pd.DataFrame) -> pd.DataFrame:
    """Turn the canonical raw statement schema into the twelve declared features.

    The frame comes back with `client_id`, the twelve features in declaration order and, when the
    raw frame carries it, the target. Every column is float except the identifier and the target.
    """
    missing = [column for column in RAW_COLUMNS if column not in raw.columns]
    if missing:
        raise ValueError(f"the raw frame is missing {missing}; the schema is {RAW_COLUMNS}")

    bills = raw[[f"bill_amt_{i}" for i in range(1, N_STATEMENTS + 1)]].to_numpy(dtype=float)
    pays = raw[[f"pay_amt_{i}" for i in range(1, N_STATEMENTS + 1)]].to_numpy(dtype=float)
    delinq = raw[[f"delinq_{i}" for i in range(1, N_STATEMENTS + 1)]].to_numpy(dtype=float)
    limit = raw["limit_bal"].to_numpy(dtype=float)

    bill_mean = bills.mean(axis=1)
    # Payment i settles the statement that closed one month earlier, which is statement i + 1.
    denominators = np.maximum(bills[:, 1:], BALANCE_FLOOR)
    ratios = np.clip(pays[:, :-1] / denominators, 0.0, PAY_RATIO_CAP)

    engineered = pd.DataFrame(
        {
            ID_COLUMN: raw[ID_COLUMN].to_numpy(),
            "limit_bal": limit,
            "age": raw["age"].to_numpy(dtype=float),
            "utilisation": bills[:, 0] / limit,
            "utilisation_mean_6m": bill_mean / limit,
            "pay_ratio_last": ratios[:, 0],
            "pay_ratio_mean_6m": ratios.mean(axis=1),
            "delinq_last": delinq[:, 0],
            "delinq_count_6m": (delinq > 0).sum(axis=1).astype(float),
            "delinq_max_6m": delinq.max(axis=1),
            "bill_mean_6m": bill_mean,
            "bill_last": bills[:, 0],
            "bill_trend_6m": _trend(bills),
        }
    )
    if TARGET_COLUMN in raw.columns:
        engineered[TARGET_COLUMN] = raw[TARGET_COLUMN].to_numpy(dtype=int)
    return engineered


def _trend(bills: np.ndarray) -> np.ndarray:
    """Return the ordinary-least-squares slope of the statement balance, oldest month first.

    A positive slope is a balance that has been growing. The design matrix is the same for every
    client, so the slope is a fixed linear combination of the six balances and needs no fitting.
    """
    months = np.arange(N_STATEMENTS, dtype=float)  # 0 is the oldest statement
    centred = months - months.mean()
    oldest_first = bills[:, ::-1]
    return (oldest_first * centred).sum(axis=1) / float((centred**2).sum())


def stratified_split(
    ids: np.ndarray,
    y: np.ndarray,
    *,
    seed: int,
    test_fraction: float = TEST_FRACTION,
) -> tuple[Split, Split]:
    """Split client identifiers into train and test, stratified on the target.

    The split is drawn over the sorted unique identifiers of each outcome class, so it depends on
    the client identifiers and the seed and not on the row order of the frame: a variant that
    shuffles the rows (spec section 5's harmless control) gets the same split.
    """
    rng = np.random.default_rng(seed)
    train_parts: list[np.ndarray] = []
    test_parts: list[np.ndarray] = []
    for outcome in (0, 1):
        stratum = np.sort(np.unique(ids[y == outcome]))
        shuffled = stratum[rng.permutation(stratum.size)]
        n_test = int(round(test_fraction * stratum.size))
        test_parts.append(shuffled[:n_test])
        train_parts.append(shuffled[n_test:])
    train = np.sort(np.concatenate(train_parts))
    test = np.sort(np.concatenate(test_parts))
    return Split("train", train), Split("test", test)


def rows_hash(ids: np.ndarray) -> str:
    """Return the `splits.json` row hash: SHA-256 of the sorted identifiers, one per line.

    Sorted, so the hash is the identity of a *set* of clients and not of a row order; rendered as
    decimal integers joined by newlines with no trailing newline, so that two implementations of
    this contract agree.
    """
    text = "\n".join(str(int(value)) for value in np.sort(ids))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def variance_inflation_factors(frame: pd.DataFrame) -> dict[str, float]:
    """Return the VIF of every column: `1 / (1 - R^2)` of that column on all the others.

    Computed with `LinearRegression` rather than by inverting the correlation matrix, so that a
    column with no variance -- which a seeded defect can produce -- gives a finite answer instead
    of a singular matrix. A single column has nothing to be inflated by and gets 1.0.
    """
    columns = list(frame.columns)
    if len(columns) < 2:
        return {column: 1.0 for column in columns}
    values = frame.to_numpy(dtype=float)
    factors: dict[str, float] = {}
    for position, column in enumerate(columns):
        target = values[:, position]
        others = np.delete(values, position, axis=1)
        spread = float(target.var())
        if spread == 0.0:
            factors[column] = VIF_CAP
            continue
        residual = target - LinearRegression().fit(others, target).predict(others)
        r_squared = 1.0 - float(residual.var()) / spread
        factors[column] = min(1.0 / max(1.0 - r_squared, 1.0 / VIF_CAP), VIF_CAP)
    return factors


def vif_screen(
    frame: pd.DataFrame,
    *,
    threshold: float = VIF_THRESHOLD,
) -> tuple[list[str], list[dict[str, float | str]]]:
    """Drop features until every retained one has a VIF at or below the threshold.

    One feature leaves per round: the **last declared** of those whose VIF exceeds the threshold,
    not the worst offender. Near-duplicate features come in pairs whose two VIFs are nearly equal,
    so choosing by magnitude would decide which of `utilisation` and `utilisation_mean_6m`
    survives by a coin-flip in the fourth decimal; choosing by declaration order keeps the feature
    the developer wrote first and makes the outcome reproducible across seeds (DECISIONS D-031).

    Returns the retained feature names in declaration order and the removals in the order they
    happened, each with the VIF it had when it was removed.
    """
    retained = list(frame.columns)
    removed: list[dict[str, float | str]] = []
    while len(retained) > 1:
        factors = variance_inflation_factors(frame[retained])
        offenders = [name for name in retained if factors[name] > threshold]
        if not offenders:
            break
        victim = offenders[-1]
        removed.append({"feature": victim, "vif": round(factors[victim], 6)})
        retained.remove(victim)
    return retained, removed
