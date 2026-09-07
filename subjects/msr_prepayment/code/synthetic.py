"""The synthetic generating process: N loans x 60 months from a known discrete-time hazard.

This is the panel every test, the demo and CI run on, so it is the clean control of the seeded
defect study -- the hazard subject's counterpart of the credit subject's DECISIONS D-017. It
carries no defect. What it does carry, deliberately, is the structure spec section 4.2 needs the
projection to be able to find:

* a **rate path with both regimes**: a thirty-month cycle around a mildly falling trend, so that
  the twelve-month change in the mortgage rate is negative for stretches and positive for others
  and every split holds loan-months of both (`falling` and `rising`);
* **three origination cohorts**, each of which meets the cycle at a different phase, so the same
  note rate means a different refinance incentive in each;
* a **hazard that is convex in incentive over the whole operating range**. The base case sits at
  a monthly payoff rate near one per cent, which is a logit near -4.6, and the logistic function
  is convex everywhere below zero. The negative-convexity sign pattern the projection reports is
  therefore a property of the process rather than a tuned number: a parallel fall in rates raises
  the hazard by more than the same parallel rise lowers it, and the `turnover_floor` below which
  no borrower's payoff probability can go bounds the upside further (DECISIONS D-040).

Every parameter of the process is a field of :class:`SyntheticProcess`, so a Phase 10 defect
recipe perturbs one number in one dataclass rather than patching arithmetic. The intercept is not
one of them: it is solved for each parameter set so that the mean monthly payoff rate is
`target_smm`, which is what keeps a recipe that changes a coefficient from also moving the base
rate and confounding the study.

The process reads its own inputs through `code/features.py`: the schedule panel is built and
passed through :func:`~code.features.build_panel`, and the hazard is a function of the resulting
feature columns. So the generating process and the champion see one definition of `incentive`,
`burnout` and `loan_age`, and a lagging bug could not hide in the difference between them.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .features import (
    FEATURE_NAMES,
    ID_COLUMN,
    RATE_COLUMN,
    RAW_PANEL_COLUMNS,
    TARGET_COLUMN,
    TERM_MONTHS,
    TIME_COLUMN,
    add_months,
    build_panel,
    month_index,
    month_period,
    scheduled_balances,
)

DEFAULT_SEED = 20260901
"""The seed `package.yaml` declares. Every number below is reproducible from it."""

RATE_SEED_OFFSET = 7717
"""The rate path is drawn from its own stream, so changing `n_loans` does not move the market."""


@dataclass(frozen=True)
class SyntheticProcess:
    """Every parameter of the generating process, in one place.

    The defaults are the clean control. A seeded-defect recipe copies this dataclass with one
    field changed; nothing else in the subject needs to know.
    """

    n_loans: int = 2000
    seed: int = DEFAULT_SEED
    months_observed: int = 60
    target_smm: float = 0.0105
    """The mean monthly payoff rate the intercept is solved for; 0.0105 is a 12% CPR."""

    # --- the calendar: three cohorts, and a rate path long enough to lag and to project ---------
    cohort_years: tuple[int, ...] = field(default=(2014, 2017, 2019))
    origination_months: int = 12
    """Originations are spread over the first N months of each cohort year, as the real files are.

    A cohort that all originated in one month would make loan age a near-deterministic function
    of the calendar, and therefore of `incentive` and `rate_change_12m`, which is a collinearity
    of the sampling design rather than of the model (DECISIONS D-041).
    """
    rate_start_month: int = 201201
    rate_end_month: int = 204012

    # --- the mortgage rate path, in percent ------------------------------------------------------
    rate_base: float = 4.40
    rate_anchor_month: int = 201401
    rate_trend_per_year: float = -0.06
    rate_cycle_months: float = 30.0
    rate_cycle_amplitude: float = 0.95
    rate_cycle_phase_months: float = 5.0
    rate_wiggle_months: float = 11.0
    rate_wiggle_amplitude: float = 0.14
    rate_ramp_start_month: int = 202201
    rate_ramp_pp_per_year: float = 1.05
    rate_ramp_years: float = 2.0
    """A late level rise, so the book being valued is out of the money at the valuation month.

    Without it every loan still alive at the end of the panel carries a large positive incentive,
    the base-case prepayment speed is already fast, and the projection has more room to gain
    under an up shock than to lose under a down one -- which is *positive* convexity, and the
    wrong answer for a servicing right. A servicing book is negatively convex when it is at or
    out of the money, which is the state the ramp puts it in (DECISIONS D-040).
    """
    rate_noise_sd: float = 0.045
    rate_min: float = 2.40
    rate_max: float = 7.50
    rate_flat_from_month: int = 202402
    """Beyond the last observed month the path is held flat, which is what the projection shocks."""

    # --- the loans -------------------------------------------------------------------------------
    sato_mean: float = 0.30
    sato_sd: float = 0.38
    orig_ltv_mean: float = 74.0
    orig_ltv_sd: float = 13.0
    orig_ltv_min: float = 30.0
    orig_ltv_max: float = 97.0
    credit_score_mean: float = 742.0
    credit_score_sd: float = 46.0
    credit_score_min: float = 620.0
    credit_score_max: float = 820.0
    orig_upb_log_mean: float = 12.16
    orig_upb_log_sd: float = 0.44
    orig_upb_min: float = 40_000.0
    orig_upb_max: float = 760_000.0

    # --- the hazard, on the same feature columns the champion is fitted to -----------------------
    turnover_floor: float = 0.0008
    """The floor on the monthly payoff probability: the borrowers who move whatever rates do."""
    beta_incentive: float = 1.15
    beta_age_years: float = 1.80
    beta_age_years_squared: float = -0.24
    """The two age terms make the seasoning hump, which peaks at 1.80 / (2 x 0.24) = 3.75 years."""
    beta_burnout: float = -0.18
    beta_season_sin: float = 0.12
    beta_season_cos: float = -0.25
    """Together a summer peak: `season_cos` is -1 in June, so a negative coefficient lifts it."""
    beta_orig_ltv: float = -0.022
    beta_credit_score: float = 0.009
    beta_orig_upb_log: float = 0.80
    beta_sato: float = -0.15
    beta_note_rate: float = 0.0
    beta_bom_balance_log: float = 0.0
    """The loan-size effect is declared once, on `orig_upb_log`; the current balance is that plus
    an amortisation term, and giving it a coefficient of its own would put the same effect in the
    process twice and make the screen's removal of it look like a loss of signal."""
    beta_rate_change_12m: float = -0.10
    intercept_bounds: tuple[float, float] = field(default=(-18.0, 8.0))

    def replace(self, **changes: object) -> SyntheticProcess:
        """Return a copy with some fields changed, for a defect recipe or a sensitivity run."""
        from dataclasses import replace as _replace

        return _replace(self, **changes)  # type: ignore[arg-type]

    @property
    def observation_end_month(self) -> int:
        """The common data cut-off: the month the youngest cohort's first loan completes in.

        A real performance file ends on one calendar month for every loan, not `months_observed`
        after each loan's own origination, and the projection needs a valuation month that a
        whole vintage is still alive in rather than only the loans originated in one month. So a
        loan is observed to the earlier of its `months_observed`-th month and this one, which
        truncates the youngest cohort's later originations and nothing else (DECISIONS D-044).
        """
        return add_months(max(self.cohort_years) * 100 + 1, self.months_observed)

    def months_of(self, orig_period: np.ndarray) -> np.ndarray:
        """How many performance months each loan is observed for, given the common cut-off."""
        available = month_index(self.observation_end_month) - month_index(orig_period)
        return np.minimum(np.maximum(available, 0), self.months_observed)


def rate_path(process: SyntheticProcess | None = None) -> pd.DataFrame:
    """Draw the market-rate calendar: the 30-year rate at the close of each month, in percent.

    Args:
        process: The parameters; the default is the clean control.

    Returns:
        A frame with `period` and `market_rate_close`, one row per month from
        `rate_start_month` to `rate_end_month` with no gaps. Beyond `rate_flat_from_month` the
        rate is held at its value in that month, which is the flat-forward assumption the
        projection shocks in parallel.
    """
    process = process or SyntheticProcess()
    rng = np.random.default_rng(process.seed + RATE_SEED_OFFSET)
    first = int(month_index(process.rate_start_month))
    last = int(month_index(process.rate_end_month))
    if last <= first:
        raise ValueError(
            f"the rate calendar runs {process.rate_start_month} to {process.rate_end_month}, "
            "which is not a forward span"
        )
    months = np.arange(first, last + 1, dtype=float)
    elapsed = months - float(month_index(process.rate_anchor_month))
    level = process.rate_base + process.rate_trend_per_year * elapsed / 12.0
    cycle = process.rate_cycle_amplitude * np.sin(
        2.0 * np.pi * (elapsed - process.rate_cycle_phase_months) / process.rate_cycle_months
    )
    wiggle = process.rate_wiggle_amplitude * np.sin(
        2.0 * np.pi * elapsed / process.rate_wiggle_months
    )
    since_ramp = months - float(month_index(process.rate_ramp_start_month))
    ramp = process.rate_ramp_pp_per_year * np.clip(since_ramp / 12.0, 0.0, process.rate_ramp_years)
    noise = rng.normal(0.0, process.rate_noise_sd, months.size)
    rate = np.clip(level + cycle + wiggle + ramp + noise, process.rate_min, process.rate_max)

    flat_from = int(month_index(process.rate_flat_from_month)) - first
    if 0 <= flat_from < rate.size:
        rate[flat_from:] = rate[flat_from]
    return pd.DataFrame({TIME_COLUMN: month_period(months.astype(np.int64)), RATE_COLUMN: rate})


def _sigmoid(values: np.ndarray) -> np.ndarray:
    """The logistic function, written so that a large negative value does not overflow."""
    clipped_up = np.clip(values, 0.0, None)
    clipped_down = np.clip(values, None, 0.0)
    return np.where(
        values >= 0.0,
        1.0 / (1.0 + np.exp(-clipped_up)),
        np.exp(clipped_down) / (1.0 + np.exp(clipped_down)),
    )


def linear_predictor(process: SyntheticProcess, panel: pd.DataFrame) -> np.ndarray:
    """Return the hazard's linear predictor without its intercept, from the feature columns.

    The features are read out of the panel :func:`~code.features.build_panel` produced, so the
    process cannot disagree with the champion about what `incentive` or `burnout` means. Loan age
    enters as a hump in years -- a ramp that peaks and then declines, which is what a seasoning
    curve looks like -- rather than as a spline, so that the champion's spline has a smooth truth
    to recover rather than a copy of its own basis.
    """
    age_years = panel["loan_age"].to_numpy(dtype=float) / 12.0
    return (
        process.beta_incentive * panel["incentive"].to_numpy(dtype=float)
        + process.beta_age_years * age_years
        + process.beta_age_years_squared * age_years**2
        + process.beta_burnout * panel["burnout"].to_numpy(dtype=float)
        + process.beta_season_sin * panel["season_sin"].to_numpy(dtype=float)
        + process.beta_season_cos * panel["season_cos"].to_numpy(dtype=float)
        + process.beta_orig_ltv * (panel["orig_ltv"].to_numpy(dtype=float) - process.orig_ltv_mean)
        + process.beta_credit_score
        * (panel["credit_score"].to_numpy(dtype=float) - process.credit_score_mean)
        + process.beta_orig_upb_log
        * (panel["orig_upb_log"].to_numpy(dtype=float) - process.orig_upb_log_mean)
        + process.beta_sato * (panel["sato"].to_numpy(dtype=float) - process.sato_mean)
        + process.beta_note_rate * panel["note_rate"].to_numpy(dtype=float)
        + process.beta_bom_balance_log * panel["bom_balance_log"].to_numpy(dtype=float)
        + process.beta_rate_change_12m * panel["rate_change_12m"].to_numpy(dtype=float)
    )


def hazard(process: SyntheticProcess, intercept: float, predictor: np.ndarray) -> np.ndarray:
    """Return the monthly payoff probability: a turnover floor plus a logistic response.

    `turnover_floor` is the share of borrowers who move, divorce or die in a month whatever rates
    do, so no loan's payoff probability can fall below it. It is the reason the projection's
    upside is bounded while its downside is not, which is half of negative convexity; the other
    half is the convexity of the logistic itself below zero (DECISIONS D-040).
    """
    return process.turnover_floor + (1.0 - process.turnover_floor) * _sigmoid(intercept + predictor)


def solve_intercept(process: SyntheticProcess, predictor: np.ndarray) -> float:
    """Solve for the intercept that puts the mean monthly payoff rate at `target_smm`.

    Bisection on a monotone function, to a tolerance far below the sampling noise of any panel
    this subject generates, so the base rate is a parameter of the process rather than an accident
    of the coefficients.

    Raises:
        ValueError: `target_smm` is at or below the turnover floor, which no intercept can reach.
    """
    if process.target_smm <= process.turnover_floor:
        raise ValueError(
            f"target_smm {process.target_smm} is not above turnover_floor "
            f"{process.turnover_floor}; no intercept can bring the mean hazard below the floor"
        )
    low, high = process.intercept_bounds
    for _ in range(200):
        middle = 0.5 * (low + high)
        if float(hazard(process, middle, predictor).mean()) < process.target_smm:
            low = middle
        else:
            high = middle
    return 0.5 * (low + high)


def loan_book(process: SyntheticProcess, rates: pd.DataFrame) -> pd.DataFrame:
    """Draw the loans: three origination cohorts, note rates around the rate at origination.

    Returns one row per loan with `loan_id` and the static columns of the raw schema. Originations
    are spread over the first `origination_months` months of each cohort year; identifiers are
    assigned in cohort blocks and ascending, so the split's draw over sorted identifiers is
    stratified on origination year by construction.
    """
    if process.n_loans < len(process.cohort_years) * 2:
        raise ValueError(
            f"n_loans must be at least {len(process.cohort_years) * 2} so that every one of the "
            f"{len(process.cohort_years)} cohorts can be split, not {process.n_loans}"
        )
    rng = np.random.default_rng(process.seed)
    rate_by_period = dict(
        zip(
            rates[TIME_COLUMN].to_numpy(dtype=np.int64),
            rates[RATE_COLUMN].to_numpy(dtype=float),
            strict=True,
        )
    )
    cohorts = process.cohort_years
    shares = np.full(len(cohorts), process.n_loans // len(cohorts), dtype=int)
    shares[: process.n_loans % len(cohorts)] += 1

    rows = []
    next_id = 1
    for year, count in zip(cohorts, shares, strict=True):
        offsets = rng.integers(0, process.origination_months, count)
        orig_period = np.array(
            [add_months(int(year) * 100 + 1, int(offset)) for offset in offsets], dtype=np.int64
        )
        # The rate at the start of the origination month is the close of the month before it.
        market = np.array(
            [rate_by_period[add_months(int(period), -1)] for period in orig_period], dtype=float
        )
        sato = rng.normal(process.sato_mean, process.sato_sd, count)
        upb = np.clip(
            np.round(
                np.exp(rng.normal(process.orig_upb_log_mean, process.orig_upb_log_sd, count)), -3
            ),
            process.orig_upb_min,
            process.orig_upb_max,
        )
        rows.append(
            pd.DataFrame(
                {
                    ID_COLUMN: np.arange(next_id, next_id + count, dtype=np.int64),
                    "orig_period": orig_period,
                    "note_rate": np.round(market + sato, 3),
                    "sato": np.round(sato, 3),
                    "orig_ltv": np.clip(
                        np.round(rng.normal(process.orig_ltv_mean, process.orig_ltv_sd, count)),
                        process.orig_ltv_min,
                        process.orig_ltv_max,
                    ),
                    "credit_score": np.clip(
                        np.round(
                            rng.normal(process.credit_score_mean, process.credit_score_sd, count)
                        ),
                        process.credit_score_min,
                        process.credit_score_max,
                    ),
                    "orig_upb": upb,
                }
            )
        )
        next_id += count
    return pd.concat(rows, ignore_index=True)


def schedule_panel(process: SyntheticProcess, book: pd.DataFrame) -> pd.DataFrame:
    """Return the raw panel a book with no payoffs would produce: every loan alive to the horizon.

    One row per loan-month from the origination month, whose closing balance is the original
    balance and whose closing age is zero, through `months_observed` further months of level-
    payment amortisation. This is the frame the hazard is evaluated on, before any loan is
    censored, which is why it exists: the hazard at month t depends only on values known at the
    start of month t, so the whole path is determined before a single payoff is drawn.
    """
    n = len(book)
    counts = process.months_of(book["orig_period"].to_numpy()) + 1
    balances = np.column_stack(
        [
            book["orig_upb"].to_numpy(dtype=float),
            scheduled_balances(
                book["orig_upb"].to_numpy(dtype=float),
                book["note_rate"].to_numpy(dtype=float),
                np.full(n, TERM_MONTHS, dtype=float),
                process.months_observed,
            ),
        ]
    )
    offsets = np.concatenate([np.arange(count, dtype=np.int64) for count in counts])
    position = np.repeat(np.arange(n, dtype=np.int64), counts)
    panel = pd.DataFrame(
        {
            ID_COLUMN: book[ID_COLUMN].to_numpy()[position],
            TIME_COLUMN: month_period(
                month_index(book["orig_period"].to_numpy())[position] + offsets
            ),
            "eom_balance": balances[position, offsets],
            "eom_age": offsets.astype(float),
            TARGET_COLUMN: np.zeros(offsets.size, dtype=int),
        }
    )
    return panel.merge(book, on=ID_COLUMN, how="left")[RAW_PANEL_COLUMNS]


def generate(
    process: SyntheticProcess | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Draw one synthetic book and return its raw loan-month panel and its rate calendar.

    Returns:
        The censored raw panel -- :data:`~code.features.RAW_PANEL_COLUMNS`, one row per observed
        loan-month, ending at the month the loan paid off with a zero closing balance and a
        `prepaid` of 1 -- and the market-rate calendar the panel was drawn against.

    Given the same :class:`SyntheticProcess` both frames are byte-identical, on any platform
    numpy supports.
    """
    process = process or SyntheticProcess()
    rates = rate_path(process)
    book = loan_book(process, rates)
    schedule = schedule_panel(process, book)
    panel = build_panel(schedule, rates)

    n = len(book)
    counts = process.months_of(book["orig_period"].to_numpy())
    if len(panel) != int(counts.sum()):
        raise ValueError(
            f"the schedule panel yielded {len(panel)} feature rows where {int(counts.sum())} were "
            "expected; the rate calendar is too short to lag every month"
        )
    predictor = linear_predictor(process, panel)
    intercept = solve_intercept(process, predictor)
    hazards = hazard(process, intercept, predictor)

    rng = np.random.default_rng(process.seed + 1)
    paid = rng.random(hazards.size) < hazards
    # The first payoff month inside each loan's own block of the ragged schedule panel.
    blocks = np.concatenate([[0], np.cumsum(counts)])
    survives = np.ones(n, dtype=bool)
    payoff_offset = counts.copy()
    for position in range(n):
        block = paid[blocks[position] : blocks[position + 1]]
        if block.any():
            survives[position] = False
            payoff_offset[position] = int(block.argmax()) + 1

    rows_per_loan = payoff_offset + 1
    offsets = np.concatenate([np.arange(count, dtype=np.int64) for count in rows_per_loan])
    loan_position = np.repeat(np.arange(n, dtype=np.int64), rows_per_loan)
    is_payoff = (offsets == payoff_offset[loan_position]) & ~survives[loan_position]

    schedule_key = pd.MultiIndex.from_arrays(
        [schedule[ID_COLUMN].to_numpy(), schedule[TIME_COLUMN].to_numpy()]
    )
    wanted = pd.MultiIndex.from_arrays(
        [
            book[ID_COLUMN].to_numpy()[loan_position],
            month_period(month_index(book["orig_period"].to_numpy())[loan_position] + offsets),
        ]
    )
    censored = schedule.set_index(schedule_key).loc[wanted].reset_index(drop=True)
    censored[TARGET_COLUMN] = is_payoff.astype(int)
    censored.loc[is_payoff, "eom_balance"] = 0.0
    return censored[RAW_PANEL_COLUMNS], rates


def engineered(process: SyntheticProcess | None = None) -> pd.DataFrame:
    """Draw one synthetic book and return its modelling panel, for a human looking at the data."""
    raw, rates = generate(process)
    panel = build_panel(raw, rates)
    return panel[
        [ID_COLUMN, TIME_COLUMN, "orig_period", *FEATURE_NAMES, "rate_regime", TARGET_COLUMN]
    ]
