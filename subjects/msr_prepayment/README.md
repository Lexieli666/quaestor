# `msr_prepayment` — a discrete-time hazard subject

A mortgage prepayment model with a servicing-value projection, rebuilt from scratch as a
**validation subject**: something for Quaestor to validate, not a model anyone should use. It is
the second clean control of the seeded defect study (`DECISIONS.md` D-047), and the one that is
expected to yield **no finding at all on the synthetic panel** — its champion is the correct
functional form for that generating process, where the credit subject's is deliberately
misspecified and must yield an `E1`. Which is why what it does and does not contain is written
down here rather than left in the code.

**On the real panel it yields one finding**, and that is not a defect in the rule: `C1` at
severity medium, on the two period splits, from a calibration slope of 0.432 out-of-time against
the declared [0.80, 1.20] band and mean predicted-to-observed gaps of 0.4618 out-of-time and
0.4932 on the vintage holdout against a 0.25 threshold. A hazard fitted through 2019
under-predicts the 2020–21 refinancing wave by about half — out-of-time CPR **0.203** observed
against **0.114** predicted, vintage holdout **0.210** against **0.112** — and `C1` is scoped to
every split by `metrics.py`'s own docstring, for the reason D-046's train-against-test scoping of
`psi` does not transfer to calibration. The real control is therefore not clean, the number is a
fact about the model rather than about the check, and `DECISIONS.md` **D-161** records what the
study does about it: each control carries a measured baseline finding set per data mode, and a
baseline finding on a control is not a false alarm.

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
| what is committed | **nothing from the loan-level files: not a row, not a per-loan digest, not a loan sequence number.** `package.yaml`'s `data.manifest` records the SHA-256 of the five files `sample_freddie.py` writes, and `artifacts/real/` holds the aggregates of the real run — coefficients, metrics, split sizes and split digests, the fitted seasoning curve and the rate-shock projection — and nothing else |

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

`sample_freddie.py` expects the sample files unzipped in place under `--raw`, **with the names the
distribution gives them** — it never renames a downloaded file. The performance member has been
distributed under two names, and either is accepted, per vintage:

| from | origination file | performance file, either name |
|---|---|---|
| `sample_2014.zip` | `sample_orig_2014.txt` | `sample_svcg_2014.txt`, `sample_perf_2014.txt` |
| `sample_2017.zip` | `sample_orig_2017.txt` | `sample_svcg_2017.txt`, `sample_perf_2017.txt` |
| `sample_2019.zip` | `sample_orig_2019.txt` | `sample_svcg_2019.txt`, `sample_perf_2019.txt` |

`sample_svcg_YYYY.txt` is looked for first, because that is what the archived distributions of
these three vintages carry; `sample_perf_YYYY.txt` is what the July 2026 distribution writes
(`DECISIONS.md` D-159).

**Two layouts, chosen by field count.** The files are pipe-delimited with no header row, so the
field order is positional and two publications of each are written out:

| | origination | performance | written out as |
|---|---:|---:|---|
| the 2024 user guide | 32 fields | 32 fields | `ORIGINATION_LAYOUT_2024`, `PERFORMANCE_LAYOUT_2024` |
| Release 47, July 2026 | 31 fields | 35 fields | `ORIGINATION_LAYOUT_2026`, `PERFORMANCE_LAYOUT_2026` |

Release 47 moves `Servicer Name` and `Mortgage Insurance Cancellation Indicator` out of the
origination file and into the performance file, adds `VantageScore 4.0` to the first and
`Bankruptcy Cramdown Costs` to the second, and renames a number of fields — nine of the
performance file's thirty-two among them — without changing what they hold. The reader counts the fields, picks the layout, **prints which release it read the file as**,
and refuses any other count rather than mapping `ocltv` where `oltv` should be — which is D-048's
rule unchanged, now with a second layout to choose between.

Nothing this subject reads moved: **every column the sampler uses downstream sits at the same
position in both layouts** — `credit_score`, `first_payment_date`, `orig_upb`, `oltv`,
`orig_interest_rate`, `loan_sequence_number` and `orig_loan_term` in the origination file (all
within positions 1–24, which the two publications share exactly), and `loan_sequence_number`,
`monthly_reporting_period`, `current_actual_upb`, `current_loan_delinquency_status`, `loan_age`,
`remaining_months_to_legal_maturity`, `zero_balance_code`, `zero_balance_effective_date` and
`current_interest_rate` in the performance file (all within 1–32, where Release 47 changes names
and not order). `tests/test_msr_sample_freddie.py` asserts the positions, and asserts separately
that the same three loans map to the same panel through either layout.

**The event is a voluntary payoff: zero-balance code `01`.** Every other zero-balance code — a
third-party sale (`02`), a short sale (`03`), a repurchase (`06`), an REO disposition (`09`), a
note sale (`15`), a reperforming-loan sale (`16`), a non-credit removal (`96`–`98`) — censors the
loan at that month, as do six months past due and legal maturity. The month a loan exits for one of
those reasons is dropped rather than counted as a month it survived, because what happened in it
was a competing exit. Read against the July 2026 guide's own enumeration — `01`, `02`, `03`, `09`,
`15`, `16`, `96` — that list is a superset by three: `16` is **added**, because a reperforming-loan
sale is a disposition and not a payoff, and `06`, `97` and `98` are **kept** although the current
guide no longer lists them, because the archived distributions of these three vintages may carry
them and an unlisted code would be read as a month the loan survived. Measured on the Release 47
`sample_perf_2014.txt` of the 2026-09-16 run, they do not: the codes that appear are `01` (40,813),
`16` (141), `96` (95), `09` (82), `02` (61), `15` (41) and `03` (28), and a retired code that never
appears costs nothing while an unlisted one that does appear is silent.

Delinquency status is two characters wide in Release 47 — `00` for current, `01` for one month past
due, with `RA` for a payment plan and `XX` for unknown. The count is taken numerically, so the
padded and unpadded forms agree and a non-numeric status is treated as not past due: censoring a
loan on a status the servicer could not report would silently drop the months in question.

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
The `calibration_slope` in `metrics.json` is the **unpenalised and converged** maximum likelihood
slope of the outcome on the predicted log odds, fitted at `C = np.inf` and `tol = 1e-10`. Neither
argument is decoration. `C = 1.0` is a prior where spec 3.7 means the MLE, though on a panel this
size it is worth only about 4e-5; lbfgs's default `tol = 1e-4` is worth **0.05**, because it stops
on the gradient well short of the optimum wherever the slope is near 1 — at the defaults this
subject reported 0.966 on the real test split where the maximum likelihood estimate is 1.017. That
is the estimator and not the model, and this is the one quantity the subject reports that a
validator recomputes by a different route, so the two are made the same estimator deliberately
(`DECISIONS.md` D-160).
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
the rate path's late level rise **moves** the surviving book about two points — mean
first-projected-month incentive +1.288 without the ramp and −0.717 with it, a move of 2.005 points
— which leaves it **out of the money** at the valuation month, the state in which a servicing right
is negatively convex at all. Two points is the move and not the level (`DECISIONS.md` D-170).

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
| champion test Brier, calibration slope | 0.007894, 0.937 |
| largest single-feature AUC | 0.724 (`incentive`) |
| worst PSI, train vs test | 0.065 (`credit_score`) |
| AUC by regime (falling / rising) | 0.7227 / 0.7238, no coefficient sign flip |
| challenger (`HistGradientBoostingClassifier`, defaults, seed 20260901) test AUC | 0.7337 |
| challenger − champion AUC | **−0.0415** (the `E1` threshold is +0.03, so no finding) |
| baseline hazard | 0.00088 at age 0, peaking at 0.00329 at age 43, 0.00301 at age 60 |
| projection book | 511 loans, 96.6 million of balance, as of 2024-01 |
| base servicing value | 1,596,815 |
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

**The −81.29% this book loses at −300bp is not comparable with the −11.35% the real sample's book
loses at the same shock**, and the difference is the book rather than the machinery: the synthetic
book sits much closer to the money at its valuation month than the real one does, so the same
parallel fall moves it much further in. `DECISIONS.md` **D-170** measures that gap, decomposes it
and records why the generating process is **not** recalibrated to the real fit.

## Measured on the real sample

Run of **2026-09-16** on this machine (Python 3.12.14, scikit-learn 1.9.0, numpy 2.5.3, pandas
3.0.5): `sample_freddie.py` over the Release 47 sample files for 2014, 2017 and 2019 at the
declared 20,000 loans and seed 20260901, then `python -m code.run --data`. Every number below is
copied from `artifacts/real/metrics.json`, `splits.json`, `model_summary.json` and
`projection.json`, which are the committed record of that run; `package.yaml`'s three developer
`claims` are the same file rounded to three significant figures, except the calibration slope,
which is written to four so that the verifier's half-a-last-decimal tolerance admits it. The two
wall-clocks are the operator's `time` of that afternoon and are the only rows here no committed
artifact holds. The four `calibration_slope` values were re-measured on 2026-09-16 after the
estimator fix of `DECISIONS.md` D-160; every other number in this table is from the original run
and is byte-identical on the re-run.

| | |
|---|---|
| `train.csv` SHA-256 | `1f220f505e5b5d6478ae4e88bd732bccff793c114172680d8b99e930679ca196` |
| `test.csv` SHA-256 | `c92f126e77f406fff90bf7792c646fe2fea3973754104759090f93a2431cd0e0` |
| `out_of_time.csv` SHA-256 | `176dfd7382fdb40c1aeab5a57c9450975780e0d092cc34dbeeed6082465c7c23` |
| `vintage_holdout.csv` SHA-256 | `597f3e894c8cce066624ae325799a60a5a0f82ac9b096586b9633976489364b4` |
| `rates.csv` SHA-256 | `45bef524be2dcef44deebbef04c5abc8af42823c2ef740cb9f0cb130e8562c7b` |
| loan-months / loans / event rate — train | 313,538 / 8,596 / 0.00948 |
| — test | 135,060 / 3,685 / 0.00917 |
| — out-of-time | 283,343 / 7,954 / 0.01868 |
| — vintage holdout | 221,779 / 6,123 / 0.01948 |
| features retained | 10 of 12 (`bom_balance_log` at VIF 16.50 and then `note_rate` at 18.07 removed) |
| champion test AUC / Brier / calibration slope | **0.6549** / 0.00906 / 1.017 |
| champion test CPR, actual vs predicted | 0.1047 vs 0.1094 |
| champion train AUC / calibration slope | 0.6504 / 0.997 |
| out-of-time AUC / slope / CPR actual vs predicted | 0.690 / **0.432** / 0.203 vs 0.114 |
| vintage-holdout AUC / slope / CPR actual vs predicted | 0.739 / 0.850 / 0.210 vs 0.112 |
| projection book | 3,946 loans, $560.9M of beginning balance, as of 202603 |
| base servicing value | $9,498,507 |
| value change at −300bp / +300bp | **−$1,077,724** (−11.35%) / **+$167,117** (+1.76%); convexity −910,607, realised negative as declared |
| wall-clock, `sample_freddie.py` | 26.97 s (`time`, total) |
| wall-clock, `python -m code.run --data` | 10.16 s (`time`, total) |

**Test AUC clears the declared floor by 0.005.** `package.yaml` declares `auc test min 0.65` and
the fit returns 0.6549; the floor was set before the run and is not moved now that the margin is
known, because a floor moved after seeing the number is the `T1` defect this tool exists to catch
(`DECISIONS.md` D-160).

**CPR level is reported and not tested.** No `cpr_mae` threshold is declared and no developer
claim is made about CPR: `verifier/developer.py` resolves a claim to `metrics.<split>.<metric>`,
`<metric>.<split>`, `<metric>` or `<metric>.max`, and no artifact holds an annualised CPR *level*
— `cpr.<split>` is a by-period table and `cpr.<split>.mae` an error — so a CPR claim would be a
declaration nothing could check (D-160). Nor is there an out-of-time or vintage claim: the
developer does not get to claim drift.

The panel and the run both live outside the repository, and `--data` re-verifies the five digests
above before fitting. The finding the fake-LLM validate raises on this panel — one `C1` at medium
— is the opening section of this file and `DECISIONS.md` D-161.

## Files

```
package.yaml       the declaration Quaestor validates against (spec 3.2)
README.md          this file
synthetic.py       the human-facing panel writer; re-exports the process out of code/
sample_freddie.py  builds the four split panels and rates.csv; never run by a test
artifacts/real/    aggregates of the committed real-sample run: metrics, coefficients, split digests, features, projection
code/              the only directory the sandbox copies into the subprocess
  run.py           the entrypoint: python -m code.run --out DIR [--data DIR | --synthetic N]
  features.py      the raw schema, the twelve features, the four splits, the spline, the screen
  synthetic.py     the generating process; every parameter is a field of SyntheticProcess
  projection.py    the rate-shock roll-forward and the servicing valuation
```

Nothing in `code/` imports `quaestor`: the subject does not know it is being validated.
