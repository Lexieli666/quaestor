"""The subject: `python -m code.run --out DIR [--data DIR | --synthetic N] [--seed S]`.

What a model developer hands over. It builds the loan-month panel of `package.yaml` with
beginning-of-month lagging, screens the twelve declared features for multicollinearity, fits a
discrete-time logistic hazard with a natural cubic spline on loan age, projects the servicing book
under every declared rate shock, and writes the standard artifact contract of spec section 3.3
into `--out`. Quaestor reads only those files, which is what lets the same checks run against this
subject, against the classification subject and against every seeded variant.

Two data modes, one pipeline:

* `--synthetic N` draws N loans over 60 months from `code/synthetic.py`'s known hazard and builds
  the panel here, so the whole pipeline -- panel, screen, splits, fit, projection -- is exercised
  offline and deterministically.
* `--data DIR` reads the four split panels `sample_freddie.py` built from the Freddie Mac
  performance files and the FRED rate series, with the same `build_panel` and the same split
  rules. The splits are not re-drawn in this mode: the sample *is* the split, and the digests
  `package.yaml` pins are what make the real fit reproducible (DECISIONS D-030, as for the
  sibling subject).

Nothing here imports `quaestor`, and nothing here reaches the network.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .features import (
    BURNOUT_MONTHS,
    DECLARED_SEED,
    FEATURE_NAMES,
    FEATURE_TIMING,
    ID_COLUMN,
    REGIME_COLUMN,
    SPLIT_NAMES,
    TARGET_COLUMN,
    TERM_MONTHS,
    TIME_COLUMN,
    VIF_THRESHOLD,
    Split,
    age_spline_knots,
    build_panel,
    design_matrix,
    rows_hash,
    scheduled_balances,
    split_panel,
    vif_screen,
)
from .projection import Book, HazardFunction, project
from .synthetic import SyntheticProcess, generate

MODEL_NAME = "logistic_hazard_age_spline"
FLOAT_FORMAT = "%.10g"
"""The same ten significant digits the artifact store rounds to, so a CSV round-trips exactly."""

BASELINE_HAZARD_MAX_AGE = 120
"""How far the reported baseline hazard by loan age runs: ten years, whatever the panel holds."""

CALIBRATION_FIT_TOL = 1e-10
"""The lbfgs tolerance of the calibration-slope fit; the default 1e-4 stops 0.05 short."""

RATE_SHOCKS_BP = [-300, -200, -100, 0, 100, 200, 300]
HORIZON_MONTHS = 180
SERVICING_FEE_BP = 25.0
DISCOUNT_RATE_ANNUAL = 0.08
CONVEXITY_EXPECTATION = "negative"
"""The `scenarios` block of `package.yaml`, restated here because the subject does not read it.

A subject is somebody else's code: spec section 3.2 hands it a data directory and an output
directory, not the package Quaestor is validating, and gives it no way to read `package.yaml`. So
the five declarations are duplicated here, and a test asserts the two copies agree -- which is
the only place the duplication is allowed to be resolved (DECISIONS D-043).
"""


def main(argv: list[str] | None = None) -> int:
    """Run the subject end to end and write the spec section 3.3 files. Returns an exit code."""
    args = parse_args(argv)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.synthetic is not None:
        process = SyntheticProcess(n_loans=args.synthetic, seed=args.seed)
        raw, rates = generate(process)
        panel = build_panel(raw, rates)
        masks = split_panel(panel, seed=args.seed)
        mode = f"synthetic n={args.synthetic}"
    else:
        panel, masks = _read_sample(Path(args.data))
        rates = _read_rates(Path(args.data))
        mode = f"data {args.data}"

    splits = {
        name: Split(
            name,
            panel.loc[mask, ID_COLUMN].to_numpy(),
            panel.loc[mask, TIME_COLUMN].to_numpy(),
        )
        for name, mask in masks.items()
    }
    train_mask = masks["train"]
    # The screen runs on the twelve declared features, before `loan_age` becomes a spline basis:
    # `bom_balance_log` is `orig_upb_log` plus a small amortisation term, so one of the pair has
    # to leave or every coefficient in the fit is a difference of two collinear columns (D-045).
    retained, removed = vif_screen(panel.loc[train_mask, FEATURE_NAMES], threshold=VIF_THRESHOLD)
    knots = age_spline_knots(panel.loc[train_mask, "loan_age"].to_numpy())
    design, design_names = design_matrix(panel[FEATURE_NAMES], retained, knots)

    champion = Pipeline(
        [("scale", StandardScaler()), ("logit", LogisticRegression(max_iter=1000))]
    ).fit(design[train_mask], panel.loc[train_mask, TARGET_COLUMN])

    def hazard_of(frame: pd.DataFrame) -> np.ndarray:
        """The fitted champion as a function of the twelve features, for the projection."""
        matrix, _ = design_matrix(frame, retained, knots)
        return np.asarray(champion.predict_proba(matrix)[:, 1], dtype=float)

    hazard: HazardFunction = hazard_of

    scores = np.asarray(champion.predict_proba(design)[:, 1], dtype=float)
    metrics: dict[str, dict[str, float]] = {}
    for name, mask in masks.items():
        part = panel[mask]
        truth = part[TARGET_COLUMN].to_numpy(dtype=int)
        split_scores = scores[mask]
        _write_csv(
            out_dir / f"predictions_{name}.csv",
            pd.DataFrame(
                {
                    ID_COLUMN: part[ID_COLUMN].to_numpy(),
                    TIME_COLUMN: part[TIME_COLUMN].to_numpy(),
                    "y_true": truth,
                    "y_score": split_scores,
                }
            ),
        )
        _write_csv(
            out_dir / f"data_{name}.csv",
            part[[ID_COLUMN, TIME_COLUMN, *retained, REGIME_COLUMN, TARGET_COLUMN]],
        )
        metrics[name] = _metrics(truth, split_scores)

    _write_json(
        out_dir / "splits.json",
        {
            name: {
                "n": split.n,
                "n_loans": split.n_loans,
                "event_rate": float(panel.loc[masks[name], TARGET_COLUMN].mean()),
                "rows_hash": rows_hash(split.ids, split.periods),
            }
            for name, split in splits.items()
        },
    )
    _write_json(
        out_dir / "features.json",
        [
            {"name": name, "dtype": str(panel[name].dtype), "timing": FEATURE_TIMING[name]}
            for name in FEATURE_NAMES
        ],
    )
    _write_json(out_dir / "metrics.json", metrics)
    _write_json(
        out_dir / "model_summary.json",
        {
            "model": MODEL_NAME,
            "standardised": True,
            "class_weight": None,
            "n_train": int(train_mask.sum()),
            "n_train_loans": splits["train"].n_loans,
            "vif_threshold": VIF_THRESHOLD,
            "age_spline_knots": [float(knot) for knot in knots],
            "intercept": float(champion.named_steps["logit"].intercept_[0]),
            "coefficients": [
                {"feature": name, "value": float(value)}
                for name, value in zip(
                    design_names, champion.named_steps["logit"].coef_[0], strict=True
                )
            ],
            "removed": removed,
            "baseline_hazard": _baseline_hazard(hazard, panel[train_mask]),
        },
    )

    book = servicing_book(panel)
    projection = project(
        hazard,
        book,
        rates,
        rate_shocks_bp=RATE_SHOCKS_BP,
        horizon_months=HORIZON_MONTHS,
        servicing_fee_bp=SERVICING_FEE_BP,
        discount_rate_annual=DISCOUNT_RATE_ANNUAL,
        convexity_expectation=CONVEXITY_EXPECTATION,
    )
    _write_json(out_dir / "projection.json", projection)

    print(
        f"msr_prepayment: {mode}, seed {args.seed}; "
        f"{len(retained)} of {len(FEATURE_NAMES)} features retained, "
        f"removed {[entry['feature'] for entry in removed]}; "
        + ", ".join(f"{name} n={split.n}" for name, split in splits.items())
        + f"; test auc={metrics['test']['auc']:.4f} brier={metrics['test']['brier']:.6f}; "
        f"projection as of {book.as_of} on {book.n_loans} loans, "
        f"value change -300bp {projection['value_change']['-300']:.2f}, "
        f"+300bp {projection['value_change']['300']:.2f}"
    )
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse the entrypoint's arguments. Exactly one of `--data` and `--synthetic` is required."""
    parser = argparse.ArgumentParser(
        prog="python -m code.run", description="Fit the msr_prepayment champion."
    )
    parser.add_argument("--out", required=True, help="where to write the spec 3.3 files")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--data", help="a directory holding the four split panels and rates.csv")
    source.add_argument(
        "--synthetic", type=int, metavar="N", help="draw N loans from the known hazard"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DECLARED_SEED,
        help=f"the seed for the draw and the split (default {DECLARED_SEED}, as package.yaml says)",
    )
    return parser.parse_args(argv)


def _read_sample(data_dir: Path) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    """Read the four split panels `sample_freddie.py` wrote, already built and already split."""
    parts = []
    sizes = {}
    for name in SPLIT_NAMES:
        path = data_dir / f"{name}.csv"
        if not path.is_file():
            raise SystemExit(
                f"{path} is missing; build the panel with `python sample_freddie.py --raw D "
                "--fred F --out DIR`"
            )
        part = pd.read_csv(path)
        expected = [
            ID_COLUMN,
            TIME_COLUMN,
            "orig_period",
            *FEATURE_NAMES,
            REGIME_COLUMN,
            TARGET_COLUMN,
        ]
        missing = [column for column in expected if column not in part.columns]
        if missing:
            raise SystemExit(f"{path} is missing the columns {missing}")
        parts.append(part[expected])
        sizes[name] = len(part)
    panel = pd.concat(parts, ignore_index=True)
    masks: dict[str, np.ndarray] = {}
    start = 0
    for name in SPLIT_NAMES:
        mask = np.zeros(len(panel), dtype=bool)
        mask[start : start + sizes[name]] = True
        masks[name] = mask
        start += sizes[name]
    return panel, masks


def _read_rates(data_dir: Path) -> pd.DataFrame:
    """Read the month-close rate calendar the real sample was built against."""
    path = data_dir / "rates.csv"
    if not path.is_file():
        raise SystemExit(
            f"{path} is missing; `sample_freddie.py` writes it beside the four split panels, and "
            "the projection cannot roll a hazard forward without a rate path"
        )
    return pd.read_csv(path)


def servicing_book(panel: pd.DataFrame) -> Book:
    """Assemble the loans still being serviced at the panel's last month, in the state they are in.

    The valuation month is the panel's own last period, and the book is every loan whose last
    observed month is that month and which did not pay off in it -- which is what a servicer
    actually holds. Each loan's closing balance, closing age and burnout are rolled one month
    forward from its last panel row, because a feature row for month t carries the state at the
    *start* of t and the projection starts from the state at its *close*.
    """
    as_of = int(panel[TIME_COLUMN].max())
    last = (
        panel.sort_values([ID_COLUMN, TIME_COLUMN], kind="stable")
        .groupby(ID_COLUMN, sort=True, as_index=False)
        .last()
    )
    alive = last[(last[TIME_COLUMN] == as_of) & (last[TARGET_COLUMN] == 0)].reset_index(drop=True)

    note_rate = alive["note_rate"].to_numpy(dtype=float)
    loan_age = alive["loan_age"].to_numpy(dtype=float)
    bom_balance = np.exp(alive["bom_balance_log"].to_numpy(dtype=float))
    incentive = alive["incentive"].to_numpy(dtype=float)
    closing = scheduled_balances(
        bom_balance, note_rate, np.maximum(TERM_MONTHS - loan_age, 1.0), 1
    )[:, 0]
    return Book(
        loan_id=alive[ID_COLUMN].to_numpy(),
        as_of=as_of,
        balance=closing,
        loan_age=loan_age + 1.0,
        note_rate=note_rate,
        burnout=alive["burnout"].to_numpy(dtype=float)
        + np.maximum(incentive, 0.0) / BURNOUT_MONTHS,
        statics=alive[["note_rate", "orig_ltv", "credit_score", "orig_upb_log", "sato"]],
    )


def _baseline_hazard(
    hazard_of: Callable[[pd.DataFrame], np.ndarray], train: pd.DataFrame
) -> list[dict[str, float]]:
    """The fitted hazard by loan age at zero incentive, spec section 3.3's hazard-only field.

    Every other feature is held at its mean over the fitting split, `incentive` and `burnout` at
    zero: a borrower with no refinance incentive and none accumulated. What is left is the
    seasoning curve the champion learned, which is the thing a reader wants to see beside the
    coefficients and cannot read off them once loan age enters as a spline.
    """
    ages = np.arange(0, BASELINE_HAZARD_MAX_AGE + 1, dtype=float)
    frame = pd.DataFrame(
        {name: np.full(ages.size, float(train[name].mean())) for name in FEATURE_NAMES}
    )
    frame["loan_age"] = ages
    frame["incentive"] = 0.0
    frame["burnout"] = 0.0
    hazards = np.asarray(hazard_of(frame), dtype=float)
    return [
        {"loan_age": float(age), "hazard": float(value)}
        for age, value in zip(ages, hazards, strict=True)
    ]


def _metrics(truth: np.ndarray, scores: np.ndarray) -> dict[str, float]:
    """The developer's own metrics. Quaestor recomputes every one of them and trusts none."""
    order = np.argsort(scores)
    sorted_truth = truth[order]
    positives = max(int(truth.sum()), 1)
    negatives = max(int(truth.size - truth.sum()), 1)
    cumulative_positive = np.cumsum(sorted_truth) / positives
    cumulative_negative = np.cumsum(1 - sorted_truth) / negatives
    auc = float(roc_auc_score(truth, scores))
    smm = float(truth.mean())
    predicted_smm = float(scores.mean())
    return {
        "n": int(truth.size),
        "event_rate": smm,
        "auc": auc,
        "gini": 2.0 * auc - 1.0,
        "ks": float(np.max(np.abs(cumulative_positive - cumulative_negative))),
        "brier": float(np.mean((scores - truth) ** 2)),
        "logloss": float(log_loss(truth, scores, labels=[0, 1])),
        "mean_predicted": predicted_smm,
        "calibration_slope": _calibration_slope(truth, scores),
        "cpr_actual": 1.0 - (1.0 - smm) ** 12,
        "cpr_predicted": 1.0 - (1.0 - predicted_smm) ** 12,
    }


def _calibration_slope(truth: np.ndarray, scores: np.ndarray) -> float:
    """Spec section 3.7: a logistic regression of the outcome on the predicted log odds.

    Both non-default arguments matter, and the second one matters more (DECISIONS D-160).
    `C = np.inf` -- scikit-learn 1.9's spelling of no penalty -- because spec section 3.7 means the
    maximum likelihood estimate and the default `C = 1.0` is a prior; on a panel this size that is
    worth about 4e-5, so it is a correctness point rather than a numerical one. `tol = 1e-10`
    because lbfgs's default 1e-4 stops on the gradient well short of the optimum wherever the slope
    is near 1: on the real test split it reads 0.9660 against the converged 1.0168. Together they
    make this the same estimator a validator recomputing the slope by Newton iteration arrives at,
    which is the point -- a diagnostic two honest routines disagree about by 0.05 is not a
    diagnostic.
    """
    clipped = np.clip(scores, 1e-9, 1.0 - 1e-9)
    logit = np.log(clipped / (1.0 - clipped)).reshape(-1, 1)
    fitted = LogisticRegression(C=np.inf, max_iter=1000, tol=CALIBRATION_FIT_TOL).fit(logit, truth)
    return float(fitted.coef_[0][0])


def _write_csv(path: Path, frame: pd.DataFrame) -> None:
    """Write a CSV with the fixed float format, so two runs of one seed are byte-identical."""
    frame.to_csv(path, index=False, float_format=FLOAT_FORMAT, lineterminator="\n")


def _write_json(path: Path, payload: object) -> None:
    """Write JSON with sorted keys and a trailing newline."""
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
