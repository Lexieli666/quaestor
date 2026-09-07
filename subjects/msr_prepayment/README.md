# `msr_prepayment` — a discrete-time hazard subject

A mortgage prepayment model with a servicing-value projection, rebuilt from scratch as a
**validation subject**: something for Quaestor to validate, not a model anyone should use. It is
the second clean control of the seeded defect study (`DECISIONS.md` D-047), and the one that is
expected to yield **no finding at all** — its champion is the correct functional form for its
generating process, where the credit subject's is deliberately misspecified and must yield an
`E1`. Which is why what it does and does not contain is written down here rather than left in the
code.

Two data modes, one pipeline. `--synthetic N` draws N loans over 60 months from a known hazard and
is what every test, CI and the demo use. `--data DIR` fits the panel that `sample_freddie.py`
built once from the Freddie Mac and FRED files; no real data is committed here, and no test reads
any.

## Data source and licence

| | |
|---|---|
| loan data | Freddie Mac **Single-Family Loan-Level Dataset**, the *sample* files for origination years **2014, 2017 and 2019** |
| rate series | FRED **`MORTGAGE30US`** (Freddie Mac Primary Mortgage Market Survey, 30-year fixed, weekly) |
| terms | Freddie Mac's terms of use permit analysis of the loan-level records but **not their redistribution**. FRED's series is public |
| what is committed | **nothing from the loan-level files: not a row, not a per-loan digest, not a loan sequence number.** `package.yaml`'s `data.manifest` records the SHA-256 of the five files `sample_freddie.py` writes, and `artifacts/real/` will hold the aggregates of the real run — coefficients, metrics, split sizes and split digests — and nothing else |

That is the whole of the difference from the sibling subject: UCI's CC BY 4.0 lets
`credit_default` commit a derived sample's digests and aggregates, and Freddie Mac's terms let
this subject commit aggregates only (spec §4). The `rows_hash` in `splits.json` is a digest of the
**set** of `loan_id:period` pairs, where `loan_id` is a dense integer assigned by
`sample_freddie.py` and not a Freddie Mac loan sequence number, so it identifies a split without
identifying a loan.

## The sample rule

`package.yaml` declares it: **20,000 loans in total, seed 20260901, stratified by origination
year** — so about 6,667 from each of 2014, 2017 and 2019, drawn over each vintage's sorted loan
sequence numbers so that the draw does not depend on the order the files happen to be in.

`sample_freddie.py` expects the sample files unzipped in place under `--raw`, with the names the
distribution gives them:

```
sample_orig_2014.txt   sample_svcg_2014.txt      (from sample_2014.zip)
sample_orig_2017.txt   sample_svcg_2017.txt      (from sample_2017.zip)
sample_orig_2019.txt   sample_svcg_2019.txt      (from sample_2019.zip)
```

Both are pipe-delimited with no header row, so the field order is positional and is written out in
`ORIGINATION_LAYOUT` and `PERFORMANCE_LAYOUT` (32 fields each, the order the 2024 user guide
documents). The reader compares the file's field count with the layout's and says so if Freddie Mac
has revised it, rather than mapping `ocltv` where `oltv` should be (`DECISIONS.md` D-048).

**The event is a voluntary payoff: zero-balance code `01`.** Every other zero-balance code — a
third-party sale (`02`), a short sale (`03`), a repurchase (`06`), an REO disposition (`09`), a
note sale (`15`), a non-credit removal (`96`–`98`) — censors the loan at that month, as do six
months past due and legal maturity. The month a loan exits for one of those reasons is dropped
rather than counted as a month it survived, because what happened in it was a competing exit.

**The rate series.** `MORTGAGE30US` is weekly, so the **first observation of each month** is that
month's month-start rate — and it is stored as the close of the month *before* it, because every
raw value this subject reads is a closing value of the month it is labelled with. See the next
section.

## Beginning-of-month lagging, which is the one rule here

Every raw value is a **closing** value of its own month: the loan's balance and age at the close
of month *t*, whether it paid off during month *t*, and the market rate at the close of month *t*.
Every feature at month *t* is then a function of month *t − 1*'s closes and of month *t*'s
position in the calendar, and of nothing else — `incentive` included, because the rate at the
close of month *t − 1* **is** the rate at the start of month *t*: no time passes between them
(`DECISIONS.md` D-038).

That is one rule with no exceptions, which is what makes it testable. `tests/
test_subject_msr_prepayment.py` perturbs each of the three raw month-*t* quantities in turn and
asserts that month *t*'s feature row does not move while month *t + 1*'s does; the payoff, being
the outcome, enters no feature in any month.

The cost is one line of documentation: a reader who looks up `2020-01` in `rates.csv` is looking
at the survey print published in the first week of February 2020.

## The twelve features

`package.yaml` declares them with their timings and their notes; `code/features.py` is the single
definition of what they *are*, over the raw loan-month schema (`loan_id`, `period`, `eom_balance`,
`eom_age`, `prepaid`, plus the origination statics) and the rate calendar (`period`,
`market_rate_close`). Both modes go through the same `build_panel`: `code/synthetic.py` renders
that schema from the generating process and `sample_freddie.py` renames the Freddie Mac and FRED
columns into it. A feature cannot mean one thing on the real panel and another on the synthetic
one.

Five are `at_origination` — `note_rate`, `orig_ltv`, `credit_score`, `orig_upb_log`, `sato` — and
seven are `before_period_start`: `loan_age`, `incentive`, `burnout`, `bom_balance_log`,
`rate_change_12m`, `season_sin`, `season_cos`. None is `during_period` or `after_outcome`.

`rate_regime` — `falling` when `rate_change_12m` is negative and `rising` otherwise — is written
into `data_<split>.csv` beside the identifier, the period and the target. It is **not** a model
feature; it is what `check_stability` splits on.

Two structures are deliberate and are not defects:

* **the near-collinear pair.** `bom_balance_log` is `orig_upb_log` plus the log of the scheduled
  amortisation factor, whose spread over 60 months of a 360-month loan is about 0.03 against 0.44
  for the loan size — so its VIF before the screen is about 40,000. The subject's own VIF screen
  resolves it before fitting. A package that declares both the original and the current balance is
  an ordinary package, not a defective one (`DECISIONS.md` D-045).
* **no interaction.** Unlike the credit subject, the generating process here is additive in the
  declared features apart from the age hump, which the champion's spline can represent. So a
  boosted challenger does **not** beat the champion, and the clean control is expected to carry no
  `E1`. That is the point of having two controls that behave differently.

## The champion

VIF screen at 10 over the twelve declared features, one feature removed per round — the
last declared of those above the threshold (`DECISIONS.md` D-031, as for the sibling subject) →
natural cubic spline basis on `loan_age`, five knots at the fitting split's 5th, 27.5th, 50th,
72.5th and 95th percentiles, rounded to whole months and written out in numpy so the fit is linear
beyond its boundary knots and the 180-month projection cannot extrapolate a cubic ramp
(`DECISIONS.md` D-039) → `StandardScaler` → `LogisticRegression`, `class_weight=None`, `lbfgs`,
`max_iter=1000`, one row per loan-month. Coefficients are reported on the standardised scale.
`model_summary.json` also carries `baseline_hazard`: the fitted monthly hazard by loan age from 0
to 120 months at zero incentive and zero burnout, every other feature at its mean over the fitting
split, which is the seasoning curve the champion learned and cannot be read off a spline's
coefficients.

## The projection

`code/projection.py` values the servicing book as of the panel's last month — every loan whose
last observed month is that month and which did not pay off in it — by rolling the champion's own
hazard forward `horizon_months` under each declared shock. The shock is a **parallel** shift of
the whole rate path, history included, so it acts through `incentive` and leaves `rate_change_12m`
alone (`DECISIONS.md` D-042); beyond the last observed month the path is held flat. The servicing
fee accrues monthly on the beginning-of-month surviving balance at `servicing_fee_bp / 12` and is
discounted at `discount_rate_annual / 12`. `projection.json` carries `value_by_shock`,
`value_change` relative to the base case, the closing surviving balance by month per shock,
`cpr_by_shock`, and the realised `convexity` — the sum of the value changes at the extreme down
and up shocks, negative when the fall outweighs the rise.

The negative convexity is a property of the process rather than a tuned number
(`DECISIONS.md` D-040): the base-case monthly payoff rate is around one per cent, a logit near
−4.6, and the logistic is convex everywhere below zero, so a parallel fall in rates raises the
hazard by more than the same rise lowers it; the `turnover_floor` bounds the upside further; and
the rate path's late level rise leaves the surviving book about two points **out of the money** at
the valuation month, which is the state in which a servicing right is negatively convex at all.

`package.yaml`'s `scenarios` block is restated as five module constants in `code/run.py`, because
spec §3.2 hands a subject a data directory and an output directory and no path to the package it
is being validated against; a test reconciles the two copies, and that test is the only place the
duplication is allowed to be resolved (`DECISIONS.md` D-043).

## How to run it

```bash
# synthetic, offline, deterministic: what CI and the demo run
python -m code.run --out /tmp/run --synthetic 2000            # from this directory
python synthetic.py --n 2000 --out /tmp/panel                 # just look at the data

# through Quaestor's sandbox, with the caps and the spec 3.3 contract check
quaestor validate subjects/msr_prepayment --synthetic 2000 --llm fake --out /tmp/r   # Phase 9

# the real panel: unzip sample_2014.zip, sample_2017.zip and sample_2019.zip into one
# directory and export FRED MORTGAGE30US to CSV first, then
python sample_freddie.py --raw ~/code/data-raw/freddie \
    --fred ~/code/data-raw/fred/MORTGAGE30US.csv --out ~/code/data-raw/msr
#   -> writes train.csv, test.csv, out_of_time.csv, vintage_holdout.csv and rates.csv,
#      and prints the manifest block to paste into package.yaml
python -m code.run --out /tmp/run_real --data ~/code/data-raw/msr
```

## What the run writes

`code/run.py --out DIR` writes the standard artifact contract of spec §3.3, and nothing else:
`splits.json` (loan-months, loans, event rate and the `rows_hash` of the sorted `loan_id:period`
pairs — a hash over loans alone would make `train` and `out_of_time` the same split, since they
hold the same loans over disjoint periods), `features.json`, `metrics.json`,
`model_summary.json` (standardised coefficients, `removed: [{feature, vif}]`, the spline knots and
`baseline_hazard`), `predictions_<split>.csv` (one row per loan-month: `loan_id`, `period`,
`y_true`, `y_score`), `data_<split>.csv` (the post-screen feature matrix actually used, with the
identifier, the period, `rate_regime` and the target beside it) and `projection.json`.

## Measured on the synthetic panel

Seed 20260901, `--synthetic 2000`, this machine (Python 3.12.14, scikit-learn 1.9.0), through
`run_model`:

| | |
|---|---|
| loan-months, loans | 95,829 over 2,000 loans in three cohorts (2014, 2017, 2019) |
| monthly payoff rate | 0.0084 observed; the intercept is solved so the uncensored schedule averages 0.0105 |
| loans paying off inside the window | 40.3% |
| train / test / out-of-time / vintage | 36,013 (934 loans) / 15,382 (400) / 12,257 (515) / 32,177 (666) |
| event rate by split | 0.00852 / 0.00806 / 0.01795 / 0.00482 |
| features retained | 10 of 12 (`rate_change_12m` at VIF 12.4 and then `bom_balance_log` at 40,090 removed) |
| worst retained VIF, Belsley condition number | 4.98, 4.94 |
| age spline knots | 1, 10, 19, 31, 53 months |
| champion AUC — test / train / out-of-time / vintage | **0.7753** / 0.7883 / 0.7846 / 0.7718 |
| champion test Brier, calibration slope | 0.007894, 0.959 |
| largest single-feature AUC | 0.724 (`incentive`) |
| worst PSI, train vs test | 0.065 (`credit_score`) |
| AUC by regime (falling / rising) | 0.7227 / 0.7238, no coefficient sign flip |
| challenger (`HistGradientBoostingClassifier`, defaults, seed 20260901) test AUC | 0.7337 |
| challenger − champion AUC | **−0.0415** (the `E1` threshold is +0.03, so no finding) |
| baseline hazard | 0.00088 at age 0, peaking at 0.00329 at age 43, 0.00301 at age 60 |
| projection book | 511 loans, 96.6 million of balance, as of 2024-01 |
| value change at −300bp / +300bp | **−1,297,986** / **+168,055**; monotone across all seven shocks; convexity −1,129,932 |
| wall-clock, through `run_model` | about 3.1 s (subprocess 2.4 s) |

Two things in that table are worth a sentence rather than a silent pass. **PSI against the
out-of-time and vintage splits is large** — `burnout` 3.09 and `loan_age` 2.41 against
out-of-time, `note_rate` 0.62 against the vintage holdout — and that is the split design rather
than drift: an out-of-time split is *defined* as older loans in a later rate environment and a
vintage holdout as a different origination cohort. The `psi` threshold and `S1` are therefore read
as train-against-test, and the other comparisons are reported and not tested
(`DECISIONS.md` D-046). And **the fitted `burnout` coefficient is +0.079 where the process's is
−0.18**: burnout is a near-monotone function of loan age, whose effect the spline absorbs, so its
own coefficient is weakly identified. A validator should say so; it is not a defect.

## Measured on the real sample

*Filled after the first real run.* Nothing in this section is quoted anywhere until a committed
run has produced it: `package.yaml`'s `data.manifest` is `null`, its `claims` list is empty, and
`artifacts/real/` does not exist yet.

## Files

```
package.yaml       the declaration Quaestor validates against (spec 3.2)
README.md          this file
synthetic.py       the human-facing panel writer; re-exports the process out of code/
sample_freddie.py  builds the four split panels and rates.csv; never run by a test
code/              the only directory the sandbox copies into the subprocess
  run.py           the entrypoint: python -m code.run --out DIR [--data DIR | --synthetic N]
  features.py      the raw schema, the twelve features, the four splits, the spline, the screen
  synthetic.py     the generating process; every parameter is a field of SyntheticProcess
  projection.py    the rate-shock roll-forward and the servicing valuation
```

Nothing in `code/` imports `quaestor`: the subject does not know it is being validated.
