# `credit_default` — a binary-classification subject

A credit-card default scoring model, rebuilt from scratch as a **validation subject**: something
for Quaestor to validate, not a model anyone should use. It is the clean control of the seeded
defect study (`DECISIONS.md` D-017), which is why what it does and does not contain is written
down here rather than left in the code.

Two data modes, one pipeline. `--synthetic N` draws N clients from a generating process with known
coefficients and is what every test, CI and the demo use. `--data DIR` fits the sample that
`sample.py` built once from the UCI file; no real data is committed here, and no test reads any.

## Data source and licence

| | |
|---|---|
| dataset | *Default of Credit Card Clients*, UCI Machine Learning Repository, id **350** |
| citation | Yeh, I. (2009). doi [10.24432/C55S3H](https://doi.org/10.24432/C55S3H) |
| licence | CC BY 4.0 — redistribution of a derived sample is permitted with attribution |
| rows | 30,000 clients, one row each, six months of statement history |
| what is committed | nothing from the file itself: not a row, not a digest of a row. `package.yaml`'s `data.manifest` records the SHA-256 of the two CSVs `sample.py` writes, and `artifacts/real/` holds the aggregates of the real run (`metrics.json`, `model_summary.json`, `splits.json`, `features.json`), which CC BY 4.0 permits as derived statistics (spec §4) |

The licence is the reason this dataset is the shipped default rather than the loan dataset of the
original project, whose terms do not permit redistributing a sample (spec §4.1).

## The sample rule

Every one of the 30,000 clients is kept; `--max-clients N` keeps the first N by identifier for a
quick check. The split is a **stratified 70/30 by client identifier, seed 20260901**, exactly as
`package.yaml` declares it, and `sample.py` draws it once: `train.csv` and `test.csv` *are* the
split, and their two digests in `data.manifest` are what makes the real fit reproducible. Under
`--data`, `code/run.py` therefore reads the split rather than re-drawing it; under `--synthetic` it
draws the same rule at the same seed (`DECISIONS.md` D-030).

## How to run it

```bash
# synthetic, offline, deterministic: what CI and the demo run
python -m code.run --out /tmp/run --synthetic 5000            # from this directory
python synthetic.py --n 5000 --out /tmp/panel.csv --engineered  # just look at the data

# through Quaestor's sandbox, with the caps and the spec 3.3 contract check
quaestor validate subjects/credit_default --synthetic 5000 --llm fake --out /tmp/r   # Phase 9

# the real sample: download UCI 350 into ~/Downloads/uci350 first, then
python sample.py --raw ~/Downloads/uci350 --out ~/data/credit_default
#   -> writes train.csv and test.csv and prints the manifest block to paste into package.yaml
python -m code.run --out /tmp/run_real --data ~/data/credit_default
```

`sample.py` accepts either `default of credit card clients.xls` (read only if `xlrd` happens to be
importable — it is not a dependency of this project) or `default_of_credit_card_clients.csv`, which
is what the operator exports once from a spreadsheet. It says so if neither is there
(`DECISIONS.md` D-027).

## The twelve features

`package.yaml` declares them, with their timings and their notes; `code/features.py` is the single
definition of what they *are*, over a canonical raw statement schema (`limit_bal`, `age`,
`bill_amt_1..6` most recent first, `pay_amt_1..6`, `delinq_1..6`). Both modes go through it:
`code/synthetic.py` renders that schema from the process, and `sample.py` renames the UCI columns
into it. A feature cannot mean one thing on the real sample and another on the synthetic panel.

The UCI repayment-status columns (`PAY_0`, `PAY_2`…`PAY_6`) code −2 as no consumption, −1 as paid
in full and 0 as revolving credit; only a positive value is a month past due, so they are floored
at zero and nothing else about them is interpreted.

Two structures are deliberate and are not defects:

* **the near-collinear pair.** A client's six statement balances differ by a few per cent, so
  `bill_last` is `bill_mean_6m` plus noise — and, divided by the same credit limit, so are
  `utilisation` and `utilisation_mean_6m`. The subject's own VIF screen resolves both pairs before
  fitting: on the default synthetic panel it removes `bill_last` (VIF ≈ 161) and then
  `utilisation_mean_6m` (VIF ≈ 36), leaving ten features whose worst VIF is about 7.3.
* **the interaction `utilisation × delinq_last`.** For a client who is current, a high balance
  predicts default; for one already past due, a high balance predicts it less, because the
  past-due client with almost no balance is the one who has stopped using the card. An additive
  logistic regression cannot represent that, so a boosted challenger legitimately beats it — the
  shape of an `E1` effective-challenge finding rather than of a defect (`DECISIONS.md` D-017).

## The champion

Feature engineering → VIF screen at 10, one feature removed per round (the last declared of those
above the threshold, `DECISIONS.md` D-031) → `StandardScaler` → `LogisticRegression`,
`class_weight=None`, `lbfgs`, `max_iter=1000`. Coefficients are reported on the standardised
scale, so they are comparable across features of wildly different units. The developer's own
metrics go into `metrics.json` and Quaestor recomputes every one of them.

## What the run writes

`code/run.py --out DIR` writes the standard artifact contract of spec §3.3, and nothing else:
`splits.json` (with `rows_hash`, the SHA-256 of the split's sorted client identifiers, one per
line, no trailing newline), `features.json`, `metrics.json`, `model_summary.json` (standardised
coefficients plus `removed: [{feature, vif}]`), `predictions_<split>.csv` and `data_<split>.csv`
(the post-screen feature matrix actually used, with the identifier and the target beside it, since
that is what the drift, collinearity and leakage screens read).

## Measured on the synthetic panel

Seed 20260901, `--synthetic 5000`, this machine (Python 3.12.14, scikit-learn 1.9.0):

| | |
|---|---|
| event rate | 0.2246 |
| train / test | 3,500 / 1,500 clients, event rate 0.2246 / 0.2247 |
| features retained | 10 of 12 (`bill_last`, `utilisation_mean_6m` removed) |
| champion test AUC | 0.7480 |
| champion test Brier | 0.1489 |
| challenger (`HistGradientBoostingClassifier`, defaults, seed 20260901) test AUC | 0.8240 |
| challenger − champion AUC | **+0.0760** (the `E1` threshold is 0.03) |
| worst PSI, train vs test | 0.0102 |
| wall-clock, through `run_model` | about 1.6 s |

## Measured on the real sample

Run of 2026-09-07 on this machine (Python 3.12.14, scikit-learn 1.9.0), `sample.py` over all
30,000 UCI clients, then `python -m code.run --data`. The numbers below are copied from
`artifacts/real/metrics.json` and `artifacts/real/splits.json`, which are the committed record of
that run; `package.yaml`'s two developer `claims` are rounded from the same file.

| | |
|---|---|
| `train.csv` SHA-256 | `77fdcbcd5529320782b87e96b0d833e7fcd16a2406806015e9beb8b2ee49e203` |
| `test.csv` SHA-256 | `04ee1f59e84debfcf56efc3096153e01df7e69ae4e017ef9e22ec56fa3bcf857` |
| clients, event rate | train 21,000 (0.2212), test 9,000 (0.2212) |
| features retained | 10 of 12 (`bill_last`, `utilisation_mean_6m` removed) |
| champion test AUC / Brier | 0.7550 / 0.1385 |
| champion train AUC / Brier | 0.7546 / 0.1384 |
| wall-clock, `python -m code.run --data` | 1.33 s (`time`, total) |

The sample itself lives outside the repository (`~/code/data-raw/credit/`); `--data` re-verifies
the two digests before fitting.

## Files

```
package.yaml     the declaration Quaestor validates against (spec 3.2)
README.md        this file
synthetic.py     the human-facing panel writer; re-exports the process out of code/
sample.py        builds train.csv and test.csv from the UCI file; never run by a test
artifacts/real/  aggregates of the committed real-sample run: metrics, coefficients, split digests, features
code/            the only directory the sandbox copies into the subprocess
  run.py         the entrypoint: python -m code.run --out DIR [--data DIR | --synthetic N]
  features.py    the twelve features, the stratified split, the VIF screen
  synthetic.py   the generating process; every parameter is a field of SyntheticProcess
```

Nothing in `code/` imports `quaestor`: the subject does not know it is being validated.
