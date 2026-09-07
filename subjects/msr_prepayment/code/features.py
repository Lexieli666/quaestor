"""The loan-month panel, the four splits, the age spline basis and the VIF screen.

This module is the single definition of what the `msr_prepayment` features *are*. Both data modes
go through it: `code/synthetic.py` renders the raw loan-month schema below from a known hazard and
`sample_freddie.py` renames the Freddie Mac and FRED columns into the same schema, and both then
call the same `build_panel`. A feature therefore cannot mean one thing on the real panel and
another on the synthetic one.

**Beginning-of-month lagging is the one rule here, and it has no exceptions.** Every raw value the
subject reads is a *closing* value of the month it is labelled with -- the loan's balance and age
at the close of month t, whether it paid off during month t, and the market rate at the close of
month t. Every feature at month t is then a function of month t-1's closes and of month t's
position in the calendar, and of nothing else. In particular `incentive` uses the market rate at
the close of month t-1, which is the rate at the start of month t: no time passes between them
(DECISIONS D-038). The outcome is the payoff observed during month t, which enters no feature at
any month.

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

ID_COLUMN = "loan_id"
TIME_COLUMN = "period"
TARGET_COLUMN = "prepaid"
REGIME_COLUMN = "rate_regime"
"""The four column names `package.yaml` declares in `data`, `regime` and the target."""

REGIME_VALUES = ("falling", "rising")
"""`package.yaml`: "falling" when `rate_change_12m` is negative, "rising" otherwise."""

STATIC_COLUMNS = [
    "orig_period",
    "note_rate",
    "sato",
    "orig_ltv",
    "credit_score",
    "orig_upb",
]
"""What a loan carries once, from its origination record."""

MONTHLY_COLUMNS = ["eom_balance", "eom_age", TARGET_COLUMN]
"""What a loan carries per month, all of it observed at or by the close of that month."""

RAW_PANEL_COLUMNS = [ID_COLUMN, TIME_COLUMN, *MONTHLY_COLUMNS, *STATIC_COLUMNS]
"""The raw loan-month schema: one row per loan-month, the closing record of that month."""

RATE_COLUMN = "market_rate_close"
RATE_COLUMNS = [TIME_COLUMN, RATE_COLUMN]
"""The market-rate calendar: the 30-year rate at the close of each month, in percent."""

FEATURE_NAMES: list[str] = [
    "note_rate",
    "orig_ltv",
    "credit_score",
    "orig_upb_log",
    "sato",
    "loan_age",
    "incentive",
    "burnout",
    "bom_balance_log",
    "rate_change_12m",
    "season_sin",
    "season_cos",
]
"""The twelve features, in the declaration order of `package.yaml`, which the screen respects."""

FEATURE_TIMING: dict[str, str] = {
    "note_rate": "at_origination",
    "orig_ltv": "at_origination",
    "credit_score": "at_origination",
    "orig_upb_log": "at_origination",
    "sato": "at_origination",
    "loan_age": "before_period_start",
    "incentive": "before_period_start",
    "burnout": "before_period_start",
    "bom_balance_log": "before_period_start",
    "rate_change_12m": "before_period_start",
    "season_sin": "before_period_start",
    "season_cos": "before_period_start",
}
"""The timing each feature is declared with in `package.yaml`; `features.json` repeats it."""

RATE_CHANGE_LAG = 12
"""`rate_change_12m` is the twelve-month change in the month-start rate."""

BURNOUT_MONTHS = 12.0
"""Burnout is cumulative positive incentive in percentage-point *years*, so it stays O(1)."""

BALANCE_FLOOR = 1.0
"""The smallest balance the log is taken of, so a rounded-down balance is not a domain error."""

VIF_THRESHOLD = 10.0
"""The screen's rule. `check_collinearity` raises `M1` at the same value (spec section 3.7)."""

VIF_CAP = 1.0e6
"""What a perfectly collinear feature's VIF is reported as, so the file holds a real number."""

DECLARED_SEED = 20260901
"""The seed `package.yaml` declares in its split rules; `--seed` overrides it."""

TRAIN_VINTAGES = (2014, 2017)
"""`package.yaml`: the two origination years train and test are drawn from."""

HOLDOUT_VINTAGE = 2019
"""`package.yaml`: the origination year held out whole."""

PERIOD_CUT = 201912
"""`package.yaml`: train and test stop here; `out_of_time` is everything after it."""

TEST_FRACTION = 0.3
"""`package.yaml`: a random 70% of the training vintages' loans, stratified on vintage."""

SPLIT_NAMES = ("train", "test", "out_of_time", "vintage_holdout")
"""The four splits `package.yaml` declares, in the loader's report order."""

AGE_SPLINE_KNOT_QUANTILES = (0.05, 0.275, 0.5, 0.725, 0.95)
"""Five knots at these quantiles of the training `loan_age`, the usual natural-spline placing."""


@dataclass(frozen=True)
class Split:
    """One split of loan-months, and the summary `splits.json` records for it."""

    name: str
    ids: np.ndarray
    periods: np.ndarray

    @property
    def n(self) -> int:
        """How many loan-months the split holds."""
        return int(self.ids.size)

    @property
    def n_loans(self) -> int:
        """How many distinct loans the split holds."""
        return int(np.unique(self.ids).size)


def month_index(period: int | np.ndarray) -> np.ndarray:
    """Turn a `YYYYMM` period into a count of months since year 0, so arithmetic is ordinary."""
    values = np.asarray(period, dtype=np.int64)
    return values // 100 * 12 + values % 100 - 1


def month_period(index: int | np.ndarray) -> np.ndarray:
    """Turn a month count back into a `YYYYMM` period."""
    values = np.asarray(index, dtype=np.int64)
    return values // 12 * 100 + values % 12 + 1


def add_months(period: int, months: int) -> int:
    """Return the `YYYYMM` period `months` after `period`, which may be negative."""
    return int(month_period(int(month_index(period)) + months))


def calendar_month(period: int | np.ndarray) -> np.ndarray:
    """Return the month of the year, 1 to 12, of a `YYYYMM` period."""
    return np.asarray(period, dtype=np.int64) % 100


def rate_lookup(rates: pd.DataFrame) -> tuple[np.ndarray, int]:
    """Return the month-close rate as a dense array plus the month index of its first element.

    Args:
        rates: A frame with :data:`RATE_COLUMNS`, one row per calendar month, no gaps.

    Returns:
        The rates in month order and the :func:`month_index` of the first month.

    Raises:
        ValueError: A column is missing, the calendar has a gap, or a month repeats.
    """
    missing = [column for column in RATE_COLUMNS if column not in rates.columns]
    if missing:
        raise ValueError(f"the rate calendar is missing {missing}; the schema is {RATE_COLUMNS}")
    ordered = rates.sort_values(TIME_COLUMN)
    index = month_index(ordered[TIME_COLUMN].to_numpy())
    if index.size == 0:
        raise ValueError("the rate calendar is empty")
    expected = np.arange(int(index[0]), int(index[0]) + index.size)
    if not np.array_equal(index, expected):
        raise ValueError(
            "the rate calendar has a gap or a repeated month between "
            f"{int(ordered[TIME_COLUMN].iloc[0])} and {int(ordered[TIME_COLUMN].iloc[-1])}; "
            "every month between the two must appear exactly once"
        )
    return ordered[RATE_COLUMN].to_numpy(dtype=float), int(index[0])


def build_panel(raw: pd.DataFrame, rates: pd.DataFrame) -> pd.DataFrame:
    """Turn the raw loan-month schema and the rate calendar into the twelve declared features.

    Args:
        raw: One row per loan-month with :data:`RAW_PANEL_COLUMNS`. Every value in the row for
            month t is a closing value of month t.
        rates: The month-close market rate, :data:`RATE_COLUMNS`.

    Returns:
        The modelling panel: `loan_id`, `period`, `orig_period`, the twelve features in
        declaration order, `rate_regime` and the target, ordered by loan then period. A loan's
        first raw month has no predecessor to lag, so it carries no feature row; nor does a month
        whose predecessor is absent, or whose predecessor closed at a zero balance.

    Raises:
        ValueError: A raw column is missing, or the rate calendar does not reach far enough back
            to give a month its own month-start rate and the one twelve months earlier.
    """
    missing = [column for column in RAW_PANEL_COLUMNS if column not in raw.columns]
    if missing:
        raise ValueError(f"the raw panel is missing {missing}; the schema is {RAW_PANEL_COLUMNS}")
    rate_values, rate_base = rate_lookup(rates)

    frame = raw.sort_values([ID_COLUMN, TIME_COLUMN], kind="stable").reset_index(drop=True)
    by_loan = frame.groupby(ID_COLUMN, sort=False)
    index = month_index(frame[TIME_COLUMN].to_numpy())
    previous_index = by_loan[TIME_COLUMN].shift(1)
    previous_balance = by_loan["eom_balance"].shift(1)
    previous_age = by_loan["eom_age"].shift(1)

    consecutive = (index - month_index(previous_index.fillna(0).to_numpy())) == 1
    keep = previous_index.notna().to_numpy() & consecutive & (previous_balance.fillna(0.0) > 0.0)
    if not keep.any():
        raise ValueError(
            "no loan-month in the raw panel has a predecessor month to lag, so the panel is "
            "empty; a loan needs its origination month plus at least one performance month"
        )

    kept = frame[keep].reset_index(drop=True)
    kept_index = index[keep]
    start_rate = _rate_at(rate_values, rate_base, kept_index - 1, "the month-start rate")
    lagged_rate = _rate_at(
        rate_values,
        rate_base,
        kept_index - 1 - RATE_CHANGE_LAG,
        f"the rate {RATE_CHANGE_LAG} months before the month start",
    )
    incentive = kept["note_rate"].to_numpy(dtype=float) - start_rate
    month_of_year = calendar_month(kept[TIME_COLUMN].to_numpy()).astype(float)

    panel = pd.DataFrame(
        {
            ID_COLUMN: kept[ID_COLUMN].to_numpy(),
            TIME_COLUMN: kept[TIME_COLUMN].to_numpy(),
            "orig_period": kept["orig_period"].to_numpy(),
            "note_rate": kept["note_rate"].to_numpy(dtype=float),
            "orig_ltv": kept["orig_ltv"].to_numpy(dtype=float),
            "credit_score": kept["credit_score"].to_numpy(dtype=float),
            "orig_upb_log": np.log(
                np.maximum(kept["orig_upb"].to_numpy(dtype=float), BALANCE_FLOOR)
            ),
            "sato": kept["sato"].to_numpy(dtype=float),
            "loan_age": previous_age[keep].to_numpy(dtype=float),
            "incentive": incentive,
            "burnout": _burnout(kept[ID_COLUMN].to_numpy(), incentive),
            "bom_balance_log": np.log(
                np.maximum(previous_balance[keep].to_numpy(dtype=float), BALANCE_FLOOR)
            ),
            "rate_change_12m": start_rate - lagged_rate,
            "season_sin": np.sin(2.0 * np.pi * month_of_year / 12.0),
            "season_cos": np.cos(2.0 * np.pi * month_of_year / 12.0),
        }
    )
    panel[REGIME_COLUMN] = np.where(
        panel["rate_change_12m"].to_numpy() < 0.0, REGIME_VALUES[0], REGIME_VALUES[1]
    )
    panel[TARGET_COLUMN] = kept[TARGET_COLUMN].to_numpy(dtype=int)
    return panel[
        [ID_COLUMN, TIME_COLUMN, "orig_period", *FEATURE_NAMES, REGIME_COLUMN, TARGET_COLUMN]
    ]


def _rate_at(values: np.ndarray, base: int, wanted: np.ndarray, what: str) -> np.ndarray:
    """Read the rate calendar at absolute month indices, naming the month that is not in it."""
    offsets = wanted - base
    if offsets.min() < 0 or offsets.max() >= values.size:
        short = wanted[(offsets < 0) | (offsets >= values.size)]
        raise ValueError(
            f"the rate calendar does not cover {int(month_period(short.min()))}, which is {what} "
            f"of a loan-month in the panel; it runs {int(month_period(base))} to "
            f"{int(month_period(base + values.size - 1))}"
        )
    return values[offsets]


def _burnout(loan_ids: np.ndarray, incentive: np.ndarray) -> np.ndarray:
    """Cumulative positive incentive over the months strictly before this one, in point-years.

    A loan's own first panel month has no prior month and therefore no burnout, which is why the
    running total has its own row subtracted rather than being shifted: a shift would have to
    invent a value for the first row of every loan.
    """
    positive = np.maximum(incentive, 0.0)
    running = pd.Series(positive).groupby(pd.Series(loan_ids), sort=False).cumsum().to_numpy()
    return (running - positive) / BURNOUT_MONTHS


def origination_year(orig_period: np.ndarray) -> np.ndarray:
    """Return the origination year of a `YYYYMM` origination period."""
    return np.asarray(orig_period, dtype=np.int64) // 100


def split_panel(
    panel: pd.DataFrame,
    *,
    seed: int = DECLARED_SEED,
    test_fraction: float = TEST_FRACTION,
) -> dict[str, np.ndarray]:
    """Return one boolean mask per declared split, exactly as `package.yaml` words the rules.

    Args:
        panel: The modelling panel from :func:`build_panel`.
        seed: The seed for the 70/30 draw over loans.
        test_fraction: The share of the training vintages' loans held out as `test`.

    Returns:
        A mask per name in :data:`SPLIT_NAMES`, over the panel's rows.

    The draw is over the sorted unique loan identifiers of each training vintage, so it depends on
    the identifiers and the seed and not on the row order of the panel: a variant that shuffles
    the rows (spec section 5's harmless control) gets the same split.
    """
    years = origination_year(panel["orig_period"].to_numpy())
    periods = panel[TIME_COLUMN].to_numpy(dtype=np.int64)
    loans = panel[ID_COLUMN].to_numpy()
    in_training_vintages = np.isin(years, TRAIN_VINTAGES)

    rng = np.random.default_rng(seed)
    train_loans: list[np.ndarray] = []
    test_loans: list[np.ndarray] = []
    for vintage in TRAIN_VINTAGES:
        stratum = np.sort(np.unique(loans[years == vintage]))
        shuffled = stratum[rng.permutation(stratum.size)]
        n_test = int(round(test_fraction * stratum.size))
        test_loans.append(shuffled[:n_test])
        train_loans.append(shuffled[n_test:])
    fitted = np.concatenate(train_loans) if train_loans else np.array([])
    held = np.concatenate(test_loans) if test_loans else np.array([])

    early = periods <= PERIOD_CUT
    return {
        "train": in_training_vintages & early & np.isin(loans, fitted),
        "test": in_training_vintages & early & np.isin(loans, held),
        "out_of_time": in_training_vintages & ~early,
        "vintage_holdout": years == HOLDOUT_VINTAGE,
    }


def rows_hash(loan_ids: np.ndarray, periods: np.ndarray) -> str:
    """Return the `splits.json` row hash: SHA-256 of the sorted `loan_id:period` pairs.

    A hazard split is a set of loan-*months*, not of loans -- `train` and `out_of_time` hold the
    same loans over disjoint periods -- so the identity hashed is the pair. Sorted, so the hash is
    the identity of a set and not of a row order; one pair per line with no trailing newline, so
    that two implementations of this contract agree.
    """
    pairs = sorted(
        f"{int(loan):d}:{int(period):d}" for loan, period in zip(loan_ids, periods, strict=True)
    )
    return hashlib.sha256("\n".join(pairs).encode("utf-8")).hexdigest()


def natural_spline_basis(values: np.ndarray, knots: np.ndarray) -> np.ndarray:
    """Return the natural cubic spline basis of `values`, without its constant column.

    Args:
        values: Where to evaluate the basis.
        knots: At least three knots, ascending; the first and last are the boundary knots beyond
            which the fit is constrained to be linear.

    Returns:
        An array with one row per value and `len(knots) - 1` columns: the identity column and one
        truncated-cubic difference per interior knot.

    Raises:
        ValueError: Fewer than three knots, or knots that are not strictly ascending.

    This is the basis of Hastie, Tibshirani and Friedman section 5.2.1: `N_1 = x` and
    `N_{k+1} = d_k - d_{K-1}` with `d_k(x) = ((x - xi_k)_+^3 - (x - xi_K)_+^3) / (xi_K - xi_k)`.
    Written out in numpy because the alternative -- scikit-learn's `SplineTransformer` -- gives a
    B-spline basis with no natural boundary constraint, and a prepayment ramp extrapolated as a
    cubic beyond the oldest loan age in the sample is exactly the shape a projection must not
    invent (DECISIONS D-039).
    """
    nodes = np.asarray(knots, dtype=float)
    if nodes.size < 3:
        raise ValueError(f"a natural cubic spline needs at least three knots, not {nodes.size}")
    if np.any(np.diff(nodes) <= 0.0):
        raise ValueError(f"the spline knots {nodes.tolist()} are not strictly ascending")
    x = np.asarray(values, dtype=float)
    last, penultimate = nodes[-1], nodes[-2]

    def truncated(knot: float) -> np.ndarray:
        return np.maximum(x - knot, 0.0) ** 3

    tail = truncated(last)
    reference = (truncated(penultimate) - tail) / (last - penultimate)
    columns = [x]
    for knot in nodes[:-2]:
        columns.append((truncated(knot) - tail) / (last - knot) - reference)
    return np.column_stack(columns)


def spline_column_names(prefix: str, knots: np.ndarray) -> list[str]:
    """Return the design-matrix column names :func:`natural_spline_basis` produces."""
    return [f"{prefix}_spline_{position}" for position in range(1, len(knots))]


def age_spline_knots(loan_age: np.ndarray) -> np.ndarray:
    """Return the five `loan_age` knots, taken from the fitting split's own quantiles.

    Rounded to whole months, because a knot at 11.7 months is a false precision on a variable
    that only takes integers, and de-duplicated so that a split with a narrow age range still
    yields a usable basis.
    """
    quantiles = np.quantile(np.asarray(loan_age, dtype=float), AGE_SPLINE_KNOT_QUANTILES)
    return np.unique(np.round(quantiles))


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
    not the worst offender, for the reason the sibling subject gives (DECISIONS D-031) -- a
    near-duplicate pair has two nearly equal VIFs, so choosing by magnitude decides which member
    survives in the fourth decimal, while choosing by declaration order keeps the feature the
    developer wrote first and is reproducible across seeds.

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


def design_matrix(
    frame: pd.DataFrame, retained: list[str], knots: np.ndarray
) -> tuple[np.ndarray, list[str]]:
    """Return the champion's design matrix and its column names.

    `loan_age` is replaced by its natural cubic spline basis; every other retained feature enters
    linearly. When the screen removed `loan_age` the basis is not built, so the design is exactly
    what was retained.
    """
    columns: list[np.ndarray] = []
    names: list[str] = []
    for name in retained:
        if name == "loan_age":
            basis = natural_spline_basis(frame[name].to_numpy(dtype=float), knots)
            columns.append(basis)
            names.extend(spline_column_names(name, knots))
        else:
            columns.append(frame[name].to_numpy(dtype=float).reshape(-1, 1))
            names.append(name)
    return np.column_stack(columns), names


TERM_MONTHS = 360
"""The declared amortisation term of every loan in the synthetic book, in months."""


def scheduled_balances(
    balance: np.ndarray,
    note_rate: np.ndarray,
    remaining_term: np.ndarray,
    months: int,
) -> np.ndarray:
    """Return the level-payment amortisation path, one row per loan and one column per month.

    Args:
        balance: The balance each loan starts from.
        note_rate: The annual note rate in percent.
        remaining_term: How many scheduled payments each loan has left.
        months: How many months to project, so column `j` is the balance after `j + 1` payments.

    Returns:
        The scheduled balances, floored at zero and zero from the month the term runs out.

    Shared by the generating process and the projection because the same schedule underlies
    `bom_balance_log` in both: a loan that has not paid off amortises, and nothing else moves its
    balance.
    """
    principal = np.asarray(balance, dtype=float).reshape(-1, 1)
    rate = np.asarray(note_rate, dtype=float).reshape(-1, 1) / 1200.0
    term = np.asarray(remaining_term, dtype=float).reshape(-1, 1)
    elapsed = np.arange(1, months + 1, dtype=float).reshape(1, -1)
    growth = np.where(rate > 0.0, (1.0 + rate) ** term, 1.0)
    interest_free = principal * np.maximum(1.0 - elapsed / np.maximum(term, 1.0), 0.0)
    amortising = principal * (growth - (1.0 + rate) ** elapsed) / np.maximum(growth - 1.0, 1e-12)
    path = np.where(rate > 0.0, amortising, interest_free)
    return np.where(elapsed > term, 0.0, np.maximum(path, 0.0))
