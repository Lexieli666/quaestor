"""The synthetic generating process: N clients from a logistic model with known coefficients.

This is the panel every test, the demo and CI run on, so it is the clean control of the seeded
defect study (DECISIONS D-017). It carries exactly two deliberate structures and no defect:

* a **near-collinear pair**: the six statement balances of a client differ only by a small
  multiplicative shock, so `bill_last` is `bill_mean_6m` plus noise and the subject's own VIF
  screen removes one of the pair before fitting (as it does for `utilisation` and
  `utilisation_mean_6m`, which are those two balances divided by the same credit limit);
* an **interaction**, `utilisation x delinq_last`, which the additive logistic champion cannot
  represent, so a boosted challenger beats it by more than the 0.03 effective-challenge threshold.
  That is a true statement about the champion's functional form rather than a defect, which is
  exactly the shape of an `E1` finding.

Every parameter of the process is a field of :class:`SyntheticProcess`, so a Phase 10 defect
recipe perturbs one number in one dataclass rather than patching arithmetic. The intercept is not
one of them: it is solved for each parameter set so that the mean default probability is
`target_event_rate`, which is what keeps a recipe that changes a coefficient from also moving the
base rate and confounding the study.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .features import ID_COLUMN, N_STATEMENTS, RAW_COLUMNS, TARGET_COLUMN

DEFAULT_SEED = 20260901
"""The seed `package.yaml` declares. Every number below is reproducible from it."""


@dataclass(frozen=True)
class SyntheticProcess:
    """Every parameter of the generating process, in one place.

    The defaults are the clean control. A seeded-defect recipe copies this dataclass with one
    field changed; nothing else in the subject needs to know.
    """

    n_clients: int = 5000
    seed: int = DEFAULT_SEED
    target_event_rate: float = 0.22

    # --- credit limit and age (the two `at_origination` features) --------------------------------
    limit_log_mean: float = 11.4  # exp(11.4) is about 89,000 currency units
    limit_log_sd: float = 0.62
    limit_min: float = 10_000.0
    limit_max: float = 800_000.0
    age_mean: float = 35.0
    age_sd: float = 9.0
    age_min: int = 21
    age_max: int = 79

    # --- utilisation: the level of the statement balance against the limit ----------------------
    utilisation_alpha: float = 1.7
    utilisation_beta: float = 2.3
    utilisation_scale: float = 1.05
    utilisation_reference: float = 0.42

    # --- the statement path: persistent, which is what makes the collinear pair -----------------
    bill_noise_last_sd: float = 0.06
    bill_noise_history_sd: float = 0.09
    bill_trend_sd: float = 0.04

    # --- payments ------------------------------------------------------------------------------
    pay_ratio_alpha: float = 1.9
    pay_ratio_beta: float = 1.5
    pay_ratio_scale: float = 1.4
    pay_ratio_reference: float = 0.65
    pay_noise_sd: float = 0.18

    # --- delinquency: a client-level propensity, then a code per statement ----------------------
    delinq_propensity_alpha: float = 0.75
    delinq_propensity_beta: float = 2.6
    delinq_severity_p: float = 0.55
    delinq_code_max: int = 8

    # --- the logistic process, on the drivers rather than on their noisy observations -----------
    beta_utilisation: float = 4.6
    beta_delinq_last: float = 0.9
    beta_delinq_count: float = 0.1
    beta_pay_ratio: float = -0.95
    beta_limit: float = -0.34
    beta_age: float = -0.09
    beta_interaction: float = -5.4
    intercept_bounds: tuple[float, float] = field(default=(-12.0, 12.0))

    def replace(self, **changes: object) -> SyntheticProcess:
        """Return a copy with some fields changed, for a defect recipe or a sensitivity run."""
        from dataclasses import replace as _replace

        return _replace(self, **changes)  # type: ignore[arg-type]


def generate(process: SyntheticProcess | None = None) -> pd.DataFrame:
    """Draw one synthetic panel: the canonical raw statement schema plus the target.

    The frame has `process.n_clients` rows and the columns of
    :data:`code.features.RAW_COLUMNS` plus `default_next_month`. Given the same
    :class:`SyntheticProcess` it is byte-identical, on any platform numpy supports.
    """
    process = process or SyntheticProcess()
    if process.n_clients < 2:
        raise ValueError(f"n_clients must be at least 2, not {process.n_clients}")
    rng = np.random.default_rng(process.seed)
    n = process.n_clients

    limit = np.clip(
        np.round(np.exp(rng.normal(process.limit_log_mean, process.limit_log_sd, n)), -3),
        process.limit_min,
        process.limit_max,
    )
    age = np.clip(
        np.round(rng.normal(process.age_mean, process.age_sd, n)),
        process.age_min,
        process.age_max,
    )
    utilisation = process.utilisation_scale * rng.beta(
        process.utilisation_alpha, process.utilisation_beta, n
    )
    pay_ratio = process.pay_ratio_scale * rng.beta(
        process.pay_ratio_alpha, process.pay_ratio_beta, n
    )

    propensity = rng.beta(process.delinq_propensity_alpha, process.delinq_propensity_beta, n)
    past_due = rng.random((n, N_STATEMENTS)) < propensity[:, None]
    severity = 1 + rng.geometric(process.delinq_severity_p, (n, N_STATEMENTS))
    delinq = np.where(past_due, np.minimum(severity, process.delinq_code_max), 0).astype(float)

    bills = _statement_path(rng, process, utilisation * limit)
    pays = _payments(rng, process, bills, pay_ratio)

    drivers = _drivers(
        process, utilisation, delinq[:, 0], (delinq > 0).sum(axis=1), pay_ratio, limit, age
    )
    intercept = _solve_intercept(drivers, process)
    probability = _sigmoid(intercept + drivers)
    target = (rng.random(n) < probability).astype(int)

    frame = pd.DataFrame({ID_COLUMN: np.arange(1, n + 1, dtype=np.int64)})
    frame["limit_bal"] = limit
    frame["age"] = age.astype(np.int64)
    for index in range(N_STATEMENTS):
        frame[f"bill_amt_{index + 1}"] = bills[:, index]
    for index in range(N_STATEMENTS):
        frame[f"pay_amt_{index + 1}"] = pays[:, index]
    for index in range(N_STATEMENTS):
        frame[f"delinq_{index + 1}"] = delinq[:, index].astype(np.int64)
    frame[TARGET_COLUMN] = target
    return frame[[*RAW_COLUMNS, TARGET_COLUMN]]


def _statement_path(
    rng: np.random.Generator, process: SyntheticProcess, base: np.ndarray
) -> np.ndarray:
    """Render six statement balances around a client's own level, most recent first.

    The level is persistent and the month-to-month shock is small, which is the whole of the
    deliberate near-collinearity: `bill_amt_1` is the six-month mean plus a few per cent.
    """
    n = base.size
    growth = rng.normal(0.0, process.bill_trend_sd, n)
    months = np.arange(N_STATEMENTS, dtype=float)  # 0 is the most recent statement
    shock = np.empty((n, N_STATEMENTS))
    shock[:, 0] = rng.normal(0.0, process.bill_noise_last_sd, n)
    shock[:, 1:] = rng.normal(0.0, process.bill_noise_history_sd, (n, N_STATEMENTS - 1))
    path = base[:, None] * (1.0 + growth[:, None]) ** (-months[None, :]) * (1.0 + shock)
    return np.round(np.maximum(path, 0.0), 2)


def _payments(
    rng: np.random.Generator,
    process: SyntheticProcess,
    bills: np.ndarray,
    pay_ratio: np.ndarray,
) -> np.ndarray:
    """Render six payments: each settles a fraction of the statement that closed before it."""
    settled = np.concatenate([bills[:, 1:], bills[:, -1:]], axis=1)
    noise = 1.0 + rng.normal(0.0, process.pay_noise_sd, bills.shape)
    return np.round(np.maximum(settled * pay_ratio[:, None] * noise, 0.0), 2)


def _drivers(
    process: SyntheticProcess,
    utilisation: np.ndarray,
    delinq_last: np.ndarray,
    delinq_count: np.ndarray,
    pay_ratio: np.ndarray,
    limit: np.ndarray,
    age: np.ndarray,
) -> np.ndarray:
    """Return the linear predictor without its intercept.

    The drivers are the latent quantities, not their noisy observations, so the champion's ceiling
    is set by the statement shock as well as by its functional form.
    """
    centred_utilisation = utilisation - process.utilisation_reference
    return (
        process.beta_utilisation * centred_utilisation
        + process.beta_delinq_last * delinq_last
        + process.beta_delinq_count * delinq_count
        + process.beta_pay_ratio * (pay_ratio - process.pay_ratio_reference)
        + process.beta_limit * (np.log(limit) - process.limit_log_mean)
        + process.beta_age * (age - process.age_mean) / 10.0
        + process.beta_interaction * centred_utilisation * delinq_last
    )


def _sigmoid(values: np.ndarray) -> np.ndarray:
    """The logistic function, written so that a large negative value does not overflow."""
    return np.where(
        values >= 0.0,
        1.0 / (1.0 + np.exp(-np.clip(values, 0.0, None))),
        np.exp(np.clip(values, None, 0.0)) / (1.0 + np.exp(np.clip(values, None, 0.0))),
    )


def _solve_intercept(drivers: np.ndarray, process: SyntheticProcess) -> float:
    """Solve for the intercept that puts the mean default probability at the target rate.

    Bisection on a monotone function, to a tolerance far below the sampling noise of any panel
    this subject generates, so the base rate is a parameter of the process rather than an
    accident of the coefficients.
    """
    low, high = process.intercept_bounds
    for _ in range(200):
        middle = 0.5 * (low + high)
        if float(_sigmoid(middle + drivers).mean()) < process.target_event_rate:
            low = middle
        else:
            high = middle
    return 0.5 * (low + high)
