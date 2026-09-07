"""The rate-shock projection: surviving balance, servicing value and the convexity it implies.

Spec section 4.2 asks the subject itself to write `projection.json`, so that `run_scenarios` has
a developer-computed projection to reproduce and an `X1` has something to disagree with. This
module is that projection and nothing more: it takes the fitted champion as a callable, the book
of loans still alive at a valuation month, and the declarations of `package.yaml`'s `scenarios`
block, and rolls the hazard forward.

The shock is a **parallel** shift of the whole rate path the projection uses, history included,
so it moves `incentive` -- where a rate shock acts on a servicing right -- and leaves
`rate_change_12m` alone. The rejected alternative, shocking only the months after the valuation
date, turns a level shock into a level shock plus a one-off twelve-month slope shock, and the
convexity table would then be reporting two shocks at once (DECISIONS D-042).

Nothing here imports `quaestor`.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from .features import (
    BURNOUT_MONTHS,
    FEATURE_NAMES,
    RATE_CHANGE_LAG,
    TERM_MONTHS,
    add_months,
    calendar_month,
    month_index,
    month_period,
    rate_lookup,
    scheduled_balances,
)

MONTHS_PER_YEAR = 12
BASIS_POINTS_PER_PERCENT = 100.0
"""A shock is declared in basis points; `incentive` and the rate path are in percent."""

BASIS_POINTS_PER_UNIT = 10_000.0
"""A servicing fee is declared in basis points of the surviving balance, annualised."""

HazardFunction = Callable[[pd.DataFrame], np.ndarray]
"""What the champion looks like from here: the twelve features in, a monthly hazard out."""


@dataclass(frozen=True)
class Book:
    """The loans still being serviced at the valuation month, in the state they are in.

    Attributes:
        loan_id: The identifiers, for the record.
        as_of: The valuation month, `YYYYMM`; every loan is alive at its close.
        balance: The balance at the close of `as_of`, which is the balance the first projected
            month's fee accrues on.
        loan_age: Months since origination at the close of `as_of`.
        note_rate: The annual note rate in percent.
        burnout: The burnout each loan carries into the first projected month.
        statics: The `at_origination` features, one column each, in declaration order.
    """

    loan_id: np.ndarray
    as_of: int
    balance: np.ndarray
    loan_age: np.ndarray
    note_rate: np.ndarray
    burnout: np.ndarray
    statics: pd.DataFrame

    @property
    def n_loans(self) -> int:
        """How many loans are being valued."""
        return int(self.balance.size)

    @property
    def beginning_balance(self) -> float:
        """The book's balance at the valuation month, which every value is a fraction of."""
        return float(self.balance.sum())


def forward_rates(rates: pd.DataFrame, as_of: int, horizon_months: int) -> np.ndarray:
    """Return the month-start rate for each projected month, and for twelve months before it.

    Args:
        rates: The month-close rate calendar.
        as_of: The valuation month.
        horizon_months: How many months are projected.

    Returns:
        An array of length `horizon_months + RATE_CHANGE_LAG`, whose element
        `RATE_CHANGE_LAG + j - 1` is the rate at the start of the `j`-th projected month. The
        leading elements are the twelve months of history `rate_change_12m` needs.

    Raises:
        ValueError: The calendar does not reach far enough forward. The subject's own rate path
            is generated long enough on purpose; a real calendar is extended by the caller.
    """
    values, base = rate_lookup(rates)
    first = int(month_index(as_of)) - RATE_CHANGE_LAG
    offsets = np.arange(first, first + horizon_months + RATE_CHANGE_LAG) - base
    if offsets.min() < 0 or offsets.max() >= values.size:
        raise ValueError(
            f"the rate calendar runs {int(month_period(base))} to "
            f"{int(month_period(base + values.size - 1))}, which does not cover the "
            f"{horizon_months} months projected from {as_of} plus the {RATE_CHANGE_LAG} months of "
            "history the twelve-month rate change needs"
        )
    return values[offsets]


def _feature_frame(
    book: Book, path: np.ndarray, shock_bp: int, horizon_months: int
) -> tuple[pd.DataFrame, np.ndarray]:
    """Build the twelve features for every loan in every projected month, in one frame.

    Returns the frame and the scheduled balance path it was built from, whose column `k` is the
    balance after `k` further payments, so column 0 is the balance at the valuation month.

    The frame is `n_loans * horizon_months` rows in loan-major order, so a hazard read back out
    of it reshapes to `(n_loans, horizon_months)`. Every column is a projection of the same
    beginning-of-month rule the panel was built with: month `j` uses the balance and age at the
    close of month `j - 1` and the rate at the start of month `j`.
    """
    n, horizon = book.n_loans, horizon_months
    shock = shock_bp / BASIS_POINTS_PER_PERCENT
    start_rate = path[RATE_CHANGE_LAG : RATE_CHANGE_LAG + horizon] + shock
    lagged_rate = path[:horizon] + shock

    balances = np.column_stack(
        [
            book.balance,
            scheduled_balances(
                book.balance,
                book.note_rate,
                np.maximum(TERM_MONTHS - book.loan_age, 1.0),
                horizon,
            ),
        ]
    )
    incentive = book.note_rate[:, None] - start_rate[None, :]
    positive = np.maximum(incentive, 0.0)
    burnout = book.burnout[:, None] + (np.cumsum(positive, axis=1) - positive) / BURNOUT_MONTHS
    ages = book.loan_age[:, None] + np.arange(horizon, dtype=float)[None, :]
    periods = np.array(
        [add_months(int(book.as_of), step) for step in range(1, horizon + 1)], dtype=np.int64
    )
    month_of_year = calendar_month(periods).astype(float)

    frame = pd.DataFrame(
        {
            "loan_age": ages.reshape(-1),
            "incentive": incentive.reshape(-1),
            "burnout": burnout.reshape(-1),
            "bom_balance_log": np.log(np.maximum(balances[:, :horizon], 1.0)).reshape(-1),
            "rate_change_12m": np.tile(start_rate - lagged_rate, (n, 1)).reshape(-1),
            "season_sin": np.tile(
                np.sin(2.0 * np.pi * month_of_year / MONTHS_PER_YEAR), (n, 1)
            ).reshape(-1),
            "season_cos": np.tile(
                np.cos(2.0 * np.pi * month_of_year / MONTHS_PER_YEAR), (n, 1)
            ).reshape(-1),
        }
    )
    for name in book.statics.columns:
        frame[name] = np.repeat(book.statics[name].to_numpy(dtype=float), horizon)
    return frame[FEATURE_NAMES], balances


def _one_shock(
    hazard_of: HazardFunction,
    book: Book,
    path: np.ndarray,
    shock_bp: int,
    *,
    horizon_months: int,
    servicing_fee_bp: float,
    discount_rate_annual: float,
) -> tuple[float, np.ndarray, float]:
    """Value the book under one parallel shock.

    Returns the present value of the servicing fee over the horizon, the book's closing surviving
    balance in each projected month, and the first year's CPR. Every figure is in the currency of
    the balances, summed over the book.
    """
    frame, balances = _feature_frame(book, path, shock_bp, horizon_months)
    hazards = np.asarray(hazard_of(frame), dtype=float).reshape(book.n_loans, horizon_months)
    survival = np.cumprod(1.0 - hazards, axis=1)
    # The fee accrues on the balance the month opens with, so on the prior month's survival.
    opening_survival = np.column_stack([np.ones(book.n_loans), survival[:, :-1]])

    opening_balance = (balances[:, :horizon_months] * opening_survival).sum(axis=0)
    closing_balance = (balances[:, 1 : horizon_months + 1] * survival).sum(axis=0)
    monthly_fee = servicing_fee_bp / BASIS_POINTS_PER_UNIT / MONTHS_PER_YEAR
    months = np.arange(1, horizon_months + 1, dtype=float)
    discount = (1.0 + discount_rate_annual / MONTHS_PER_YEAR) ** -months
    value = float((monthly_fee * opening_balance * discount).sum())

    first_year = min(MONTHS_PER_YEAR, horizon_months)
    smm = float(hazards[:, :first_year].mean())
    cpr = 1.0 - (1.0 - smm) ** MONTHS_PER_YEAR
    return value, closing_balance, cpr


def project(
    hazard_of: HazardFunction,
    book: Book,
    rates: pd.DataFrame,
    *,
    rate_shocks_bp: list[int],
    horizon_months: int,
    servicing_fee_bp: float,
    discount_rate_annual: float,
    convexity_expectation: str,
) -> dict[str, Any]:
    """Roll the champion's hazard forward under every declared shock and value the servicing.

    Args:
        hazard_of: The fitted champion, as a function of the twelve features.
        book: The loans alive at the valuation month.
        rates: The month-close rate calendar, long enough to cover the horizon.
        rate_shocks_bp: The declared parallel shocks, which must include the base case.
        horizon_months: How far to project.
        servicing_fee_bp: The declared annual servicing fee, in basis points.
        discount_rate_annual: The declared discount rate.
        convexity_expectation: What `package.yaml` says the value curve should do, carried into
            the file so that `run_scenarios` can compare its own verdict with the declaration.

    Returns:
        The payload of `projection.json`: `value_by_shock` and `value_change` keyed by the shock
        in basis points, `balance_by_month` (the book's closing surviving balance in each
        projected month, per shock), the first-year `cpr_by_shock`, and the realised `convexity`
        -- the sum of the value changes at the extreme down and up shocks, which is negative when
        the fall under the down shock outweighs the rise under the up shock.

    Raises:
        ValueError: The shocks do not include the base case, or the book is empty.
    """
    if 0 not in rate_shocks_bp:
        raise ValueError(f"rate_shocks_bp {rate_shocks_bp} does not include the base case 0")
    if book.n_loans == 0:
        raise ValueError(
            f"no loan in the panel is still alive at {book.as_of}, so there is no servicing book "
            "to value; check that the valuation month is the panel's last period"
        )
    path = forward_rates(rates, book.as_of, horizon_months)

    values: dict[str, float] = {}
    balances: dict[str, list[float]] = {}
    cprs: dict[str, float] = {}
    for shock in sorted(rate_shocks_bp):
        value, balance, cpr = _one_shock(
            hazard_of,
            book,
            path,
            shock,
            horizon_months=horizon_months,
            servicing_fee_bp=servicing_fee_bp,
            discount_rate_annual=discount_rate_annual,
        )
        values[str(shock)] = value
        balances[str(shock)] = [float(item) for item in balance]
        cprs[str(shock)] = float(cpr)

    base = values["0"]
    changes = {shock: value - base for shock, value in values.items()}
    extremes = changes[str(min(rate_shocks_bp))] + changes[str(max(rate_shocks_bp))]
    return {
        "as_of_period": int(book.as_of),
        "horizon_months": int(horizon_months),
        "n_loans": book.n_loans,
        "beginning_balance": book.beginning_balance,
        "servicing_fee_bp": float(servicing_fee_bp),
        "discount_rate_annual": float(discount_rate_annual),
        "convexity_expectation": convexity_expectation,
        "rate_path_assumption": (
            "the month-close rate calendar, held flat beyond its last observed month, shifted in "
            "parallel by the shock over the whole path so that only incentive moves"
        ),
        "value_by_shock": values,
        "value_change": changes,
        "balance_by_month": balances,
        "cpr_by_shock": cprs,
        "convexity": extremes,
        "convexity_realised": (
            "negative" if extremes < 0.0 else "positive" if extremes > 0.0 else "flat"
        ),
    }
