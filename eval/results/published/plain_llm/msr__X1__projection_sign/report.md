---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: msr_prepayment
version: "1.0"
model_type: discrete_time_hazard
configuration: plain_llm
model: claude-opus-5[1m]
run_id: msr_prepayment-plain_llm-20260918T220554Z-986f3824
data_mode: synthetic
synthetic_n: 2000
grounding_precision_pre: 0.0000
grounding_precision_post: 0.0000
n_claims: 191
n_findings_by_severity: {high: 1, medium: 4, low: 2, info: 0}
generated: "2026-09-18T22:05:54Z"
illustrative: false
---

# Validation report — `msr_prepayment` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `msr_prepayment` v1.0 | `plain_llm` | claude-opus-5[1m] | synthetic, n = 2000 | 0.0000 → 0.0000 | 1 / 4 / 2 / 0 |
<!-- quaestor:renderer:end -->

This report documents an independent validation of `msr_prepayment` version 1.0, a discrete-time hazard (monthly conditional prepayment) model used to project voluntary prepayment for mortgage servicing rights valuation. The review was performed entirely against the artifacts registered for the subject run: the fitted-model summary [[art:b764932a:run.model_summary]], the feature inventory [[art:61276a96:run.features]], the split definitions [[art:dca79f2f:run.splits]], the performance metrics [[art:31ce3d08:run.metrics]], the four scored datasets [[art:0356ef50:run.data_train]], [[art:f0ac9fe8:run.data_test]], [[art:940d14da:run.data_vintage_holdout]], [[art:7ddcc721:run.data_out_of_time]], and the corresponding prediction tables [[art:f0b43d19:run.predictions_train]], [[art:d74c6620:run.predictions_test]], [[art:afa7c750:run.predictions_vintage_holdout]], [[art:f3fcb713:run.predictions_out_of_time]].

The model is a monthly discrete-time hazard with a loan-age baseline hazard represented by a natural spline with interior/boundary knots at ages ⟦unverified: 1,⟧ ⟦unverified: 10,⟧ ⟦unverified: 19,⟧ ⟦unverified: 31⟧ and ⟦unverified: 53,⟧ and twelve covariates: five origination-time characteristics (`note_rate`, `orig_ltv`, `credit_score`, `orig_upb_log`, `sato`) and seven predetermined period-start characteristics (`loan_age`, `incentive`, `burnout`, `bom_balance_log`, `rate_change_12m`, `season_sin`, `season_cos`).

Estimation and evaluation cover four samples:

| Split | Rows | Loans | Event rate | AUC | Cal. slope | CPR actual | CPR predicted |
|---|---|---|---|---|---|---|---|
| train | ⟦unverified: 36,013⟧ | ⟦unverified: 934⟧ | ⟦unverified: 0.00852⟧ | ⟦unverified: 0.7883⟧ | ⟦unverified: 0.994⟧ | ⟦unverified: 9.76%⟧ | ⟦unverified: 9.66%⟧ |
| test | ⟦unverified: 15,382⟧ | ⟦unverified: 400⟧ | ⟦unverified: 0.00806⟧ | ⟦unverified: 0.7753⟧ | ⟦unverified: 0.937⟧ | ⟦unverified: 9.26%⟧ | ⟦unverified: 9.32%⟧ |
| vintage_holdout | ⟦unverified: 32,177⟧ | ⟦unverified: 666⟧ | ⟦unverified: 0.00482⟧ | ⟦unverified: 0.7718⟧ | ⟦unverified: 0.837⟧ | ⟦unverified: 5.63%⟧ | ⟦unverified: 6.57%⟧ |
| out_of_time | ⟦unverified: 12,257⟧ | ⟦unverified: 515⟧ | ⟦unverified: 0.01795⟧ | ⟦unverified: 0.7846⟧ | ⟦unverified: 0.997⟧ | ⟦unverified: 19.53%⟧ | ⟦unverified: 20.43%⟧ |

**Overall conclusion.** Rank-ordering performance is sound and stable, and the model is internally coherent: annualized CPR figures reconcile exactly with the mean monthly predicted hazards under the standard ⟦unverified: 1⟧−(⟦unverified: 1⟧−h)^⟦unverified: 12⟧ transform on every split. However, validation identified one structural issue that must be resolved before the model can be relied upon for valuation — the declared split populations cannot be mutually loan-disjoint — together with a material calibration bias on the vintage holdout, an undocumented data/feature reconciliation gap, extrapolation of the baseline hazard well beyond the observed loan-age support, and the absence of drift, collinearity and challenger diagnostics. The model is **not approved for unrestricted production use**; it may be used on a conditional basis for indicative analysis pending the remediations in Section 6.

Scope limitations: the registered `model_summary` payload available to this review is truncated within the baseline-hazard block, so the fitted covariate coefficients, their standard errors and any regime-by-regime refits were not visible. No challenger model, no PSI/drift report, no collinearity diagnostics, no per-feature discrimination statistics, and no by-segment backtest were registered. Statements below about those topics are statements about absent evidence, not about failed tests.

## 2. Conceptual soundness

The modeling choice is appropriate to the task. A discrete-time hazard on monthly loan-period observations is the standard formulation for prepayment: it handles right-censoring naturally, permits time-varying covariates, and produces a monthly conditional hazard that aggregates to CPR without further assumptions. The covariate set covers the economically accepted drivers — refinance incentive, burnout, seasoning, seasonality, borrower credit quality, loan size, LTV and spread-at-origination — and contains no obvious omission of a first-order driver other than the absence of any geographic, occupancy, purpose, channel or servicer dimension, which limits the model's ability to explain cross-sectional dispersion within a coupon cohort.

Feature timing is declared correctly in [[art:61276a96:run.features]]: zero features are tagged `during_period` and zero are tagged `after_outcome`, and every time-varying covariate (`loan_age`, `incentive`, `burnout`, `bom_balance_log`, `rate_change_12m`, and the two seasonal harmonics) is tagged `before_period_start`. This is the correct convention for a hazard model — the covariate vector must be measured at the start of the period over which the prepayment indicator is defined — and validation found no covariate that could mechanically encode the outcome. `bom_balance_log` deserves a specific note because a balance measured at any point after the period start would be a direct leak of the termination event; as declared it is a beginning-of-month quantity and is acceptable, but the declaration is the only evidence of this and could not be independently confirmed from a data dictionary.

The baseline hazard in [[art:b764932a:run.model_summary]] has an economically sensible shape: it rises monotonically from ⟦unverified: 0.000885⟧ at age ⟦unverified: 0⟧ to a peak of ⟦unverified: 0.003295⟧ at age ⟦unverified: 43⟧ — a ⟦unverified: 3.7⟧× seasoning ramp — and then declines slowly and monotonically thereafter, consistent with a seasoning ramp followed by cohort burnout and adverse selection. There is no oscillation, no sign reversal and no discontinuity at the knots, so the spline is well behaved within the estimation range.

The weakness is at the boundary. The training data support the baseline only to loan age ⟦unverified: 59⟧ months (`loan_age` max = ⟦unverified: 59.0⟧ in the raw training profile, and the highest spline knot is ⟦unverified: 53⟧), yet the fitted baseline is tabulated continuously past age ⟦unverified: 100⟧. Beyond age ⟦unverified: 59⟧ the curve is pure linear-tail spline extrapolation carrying no information from the data, and MSR valuation is precisely the application that integrates the hazard over the full remaining term of ⟦unverified: 30⟧-year collateral. The gentle monotone decay the extrapolation produces is an assumption, not a finding, and it is not documented as such.

A second conceptual concern is that the covariate set is heavily overlapping in its rate content: `note_rate`, `sato`, `incentive` and `rate_change_12m` are all algebraic functions of the same note rate and the prevailing mortgage rate, and `burnout` is a path functional of `incentive`. This is common practice and not wrong per se, but it makes individual coefficient signs and magnitudes fragile and is the standard setting in which coefficient instability across rate regimes appears. No collinearity diagnostic was registered.

## 3. Data integrity and drift

**Completeness.** The raw training profile reports zero missing values in all thirteen profiled columns across ⟦unverified: 36,013⟧ rows. No missingness profile was registered for the test, vintage-holdout or out-of-time splits, so a like-for-like comparison of missingness across splits — the standard test for differential data quality — could not be performed. On the evidence available there is no missingness defect; there is an evidence gap.

**Feature-to-data reconciliation.** Two of the twelve declared model features, `bom_balance_log` and `rate_change_12m`, do not appear anywhere in the profiled columns of the training data [[art:0356ef50:run.data_train]]. The profile lists `loan_id`, `period`, `note_rate`, `orig_ltv`, `credit_score`, `orig_upb_log`, `sato`, `loan_age`, `incentive`, `burnout`, `season_sin`, `season_cos` and `prepaid` — ten of the twelve features plus keys and the target. Either the profile is incomplete or the two features are constructed in a downstream step that was not profiled or documented. In either case a validator cannot confirm the range, sign convention or distribution of two inputs that feed the fitted hazard, and `bom_balance_log` is the one feature whose timing directly determines whether the model leaks. This is a documentation and lineage defect that must be closed.

**Split construction.** The split manifest [[art:dca79f2f:run.splits]] reports distinct `rows_hash` values for all four samples, which establishes that no two splits contain an identical row set but establishes nothing about row- or loan-level overlap. The loan counts do not reconcile with the observed identifier space. The training profile shows `loan_id` ranging from ⟦unverified: 1⟧ to ⟦unverified: 1,334,⟧ indicating a universe of at most ⟦unverified: 1,334⟧ loans, and `train` (⟦unverified: 934⟧ loans) plus `test` (⟦unverified: 400⟧ loans) sums to exactly ⟦unverified: 1,334⟧ — consistent with a clean loan-level partition of the whole universe between those two samples. The `vintage_holdout` (⟦unverified: 666⟧ loans) and `out_of_time` (⟦unverified: 515⟧ loans) samples must therefore be drawn from loans already used in training or testing; the four declared populations total ⟦unverified: 2,515⟧ loan memberships against at most ⟦unverified: 1,334⟧ distinct loans. For the out-of-time sample this is defensible and normal — a forward time cut deliberately re-observes the same loans in later periods — but it must be disclosed, because it means the out-of-time AUC is not an out-of-sample-by-loan statistic. For the `vintage_holdout` it is a genuine defect: a vintage holdout exists to test transfer to loan cohorts the model has never seen, and a sample of ⟦unverified: 666⟧ loans that necessarily overlaps the ⟦unverified: 934⟧ training loans cannot serve that purpose. Its ⟦unverified: 0.7718⟧ AUC therefore overstates true cohort-transfer performance by an unknown amount. This is recorded as the highest-severity finding in this report.

**Drift.** No population stability index or characteristic-drift report was registered, so PSI could not be compared to any threshold. Drift is nonetheless plainly present in the metrics: the out-of-time event rate of ⟦unverified: 0.01795⟧ is ⟦unverified: 2.1⟧× the training rate of ⟦unverified: 0.00852⟧, and the corresponding actual CPR rises from ⟦unverified: 9.76%⟧ to ⟦unverified: 19.53%⟧. A doubling of the target rate across the time cut is a regime shift — its magnitude and the ⟦unverified: 2014⟧–⟦unverified: 2019⟧ training window (`period` ⟦unverified: 201402⟧ to ⟦unverified: 201912⟧) are consistent with the out-of-time sample capturing a refinance wave. The model tracks the shift well, raising mean predicted hazard from ⟦unverified: 0.00843⟧ to ⟦unverified: 0.01887⟧, which is strong evidence that the incentive and rate-change covariates are doing real work rather than the model having memorized a base rate. Drift is therefore a monitoring and documentation issue here rather than a performance failure, but it is undocumented and unquantified.

## 4. Outcomes analysis

**Discrimination.** AUC is ⟦unverified: 0.7883⟧ in-sample and ⟦unverified: 0.7753⟧ / ⟦unverified: 0.7718⟧ / ⟦unverified: 0.7846⟧ on test, vintage holdout and out-of-time respectively (Gini ⟦unverified: 0.577⟧ / ⟦unverified: 0.551⟧ / ⟦unverified: 0.544⟧ / ⟦unverified: 0.569⟧; KS ⟦unverified: 0.456⟧ / ⟦unverified: 0.416⟧ / ⟦unverified: 0.452⟧ / ⟦unverified: 0.432⟧). The largest train-to-holdout AUC gap is ⟦unverified: 0.0165⟧ (train to vintage holdout), with ⟦unverified: 0.0131⟧ to test and ⟦unverified: 0.0037⟧ to out-of-time. All are well inside any conventional degradation tolerance, and the out-of-time result is especially reassuring: discrimination is essentially preserved through a regime in which the event rate doubled. **No out-of-sample degradation defect is raised.** This conclusion must, however, be read against Section 3 — because the vintage holdout shares loans with training, its gap is a lower bound on true cohort-transfer degradation.

**Calibration.** Results are mixed and split-dependent.

- `train`: slope ⟦unverified: 0.9937⟧, mean predicted ⟦unverified: 0.008427⟧ versus observed ⟦unverified: 0.008525⟧ (−⟦unverified: 1.1%⟧); CPR ⟦unverified: 9.66%⟧ predicted versus ⟦unverified: 9.76%⟧ actual. Excellent, as expected in-sample.
- `out_of_time`: slope ⟦unverified: 0.9969⟧, mean predicted ⟦unverified: 0.018866⟧ versus observed ⟦unverified: 0.017949⟧ (+⟦unverified: 5.1%⟧); CPR ⟦unverified: 20.43%⟧ versus ⟦unverified: 19.53%⟧ actual (+⟦unverified: 4.6%⟧). Good, and notable given the regime shift.
- `test`: slope ⟦unverified: 0.9365⟧, mean predicted ⟦unverified: 0.008116⟧ versus observed ⟦unverified: 0.008061⟧ (+⟦unverified: 0.7%⟧); CPR ⟦unverified: 9.32%⟧ versus ⟦unverified: 9.26%⟧. Aggregate level is nearly exact; the slope below ⟦unverified: 0.95⟧ indicates mild over-dispersion of scores — the model spreads risk slightly too far from the mean — but it sits at the edge of, rather than outside, a conventional ⟦unverified: 0.90⟧–⟦unverified: 1.10⟧ band.
- `vintage_holdout`: slope ⟦unverified: 0.8373⟧, mean predicted ⟦unverified: 0.005647⟧ versus observed ⟦unverified: 0.004817⟧ (+⟦unverified: 17.2%⟧); CPR ⟦unverified: 6.57%⟧ predicted versus ⟦unverified: 5.63%⟧ actual (+⟦unverified: 16.7%⟧). This breaches a ⟦unverified: 0.90⟧–⟦unverified: 1.10⟧ slope band and represents a material aggregate over-prediction.

The vintage-holdout result is the economically significant one. A ⟦unverified: 16.7%⟧ relative over-statement of CPR on a low-prepayment cohort translates directly into understated MSR value and understated duration, and the direction is systematic rather than noise: the low slope means the over-prediction is concentrated in the high-score tail, i.e. the model overstates prepayment most for the loans it ranks as most likely to prepay. Brier (⟦unverified: 0.004763⟧) and log loss (⟦unverified: 0.02811⟧) are lowest on this split, but that is an artifact of the low base rate and carries no calibration information.

**Reconciliation checks.** Every split's reported CPR reconciles to its mean predicted monthly hazard under ⟦unverified: 1⟧−(⟦unverified: 1⟧−h)^⟦unverified: 12⟧ to within rounding (e.g. ⟦unverified: 1⟧−(⟦unverified: 1⟧−⟦unverified: 0.018866⟧)^⟦unverified: 12⟧ = ⟦unverified: 0.2043⟧ versus a reported ⟦unverified: 0.20432⟧; ⟦unverified: 1⟧−(⟦unverified: 1⟧−⟦unverified: 0.005647⟧)^⟦unverified: 12⟧ = ⟦unverified: 0.0657⟧ versus ⟦unverified: 0.06570⟧), and each actual CPR reconciles identically to its split event rate. The metrics file [[art:31ce3d08:run.metrics]] is internally consistent and consistent with [[art:dca79f2f:run.splits]] on row counts and event rates. No arithmetic or reporting defects were found.

**Effective challenge.** No challenger or benchmark model was registered. There is no logistic baseline, no constant-hazard or table-driven baseline, and no prior model version against which the ⟦unverified: 0.7883⟧ AUC or the hazard specification can be judged. Without a challenger, validation cannot demonstrate that the spline baseline and the twelve-covariate specification add value over a simpler alternative, and the benchmarking element of effective challenge is unmet.

## 5. Sensitivity and scenario analysis

No formal sensitivity or scenario study was registered; a projection artifact [[art:cbc0b707:run.projection]] exists but no scenario grid, rate-shock ladder or one-way sensitivity table was produced. The analysis below is therefore derived from the fitted baseline and the observed split behaviour.

**Age/seasoning profile.** The baseline hazard in [[art:b764932a:run.model_summary]] is monotone increasing from age ⟦unverified: 0⟧ through its maximum at age ⟦unverified: 43⟧ and monotone decreasing thereafter, with no local reversals. Within the support of the data (ages ⟦unverified: 0⟧–⟦unverified: 59⟧) the curve is correctly signed and correctly shaped for a prepayment ramp, and the response is smooth across all five knots. **No non-monotonicity or sign error is present inside the estimation range.**

**Extrapolation risk.** The curve is nonetheless published far outside its support: training loan ages top out at ⟦unverified: 59⟧ months and the highest spline knot is ⟦unverified: 53,⟧ yet the baseline is tabulated beyond age ⟦unverified: 100⟧. Roughly the entire second half of the tabulated curve — and, for MSR purposes, the bulk of the discounted cash-flow horizon for seasoned collateral — is determined by the spline's boundary behaviour rather than by any observation. The extrapolated tail decays gently (from ⟦unverified: 0.003295⟧ at age ⟦unverified: 43⟧ to about ⟦unverified: 0.00231⟧ at age ⟦unverified: 101,⟧ a decline of only ⟦unverified: 30%⟧ over five years), which imposes a strong and untested assumption that long-seasoned loans continue to prepay at roughly two-thirds of peak speed indefinitely. An alternative and equally defensible burnout assumption would materially change long-horizon CPR and hence MSR value. This is flagged as a scenario/extrapolation defect.

**Implicit rate-shock evidence.** The out-of-time split functions as an unplanned upward-incentive shock: actual CPR doubles from ⟦unverified: 9.76%⟧ to ⟦unverified: 19.53%⟧, and the model's predicted CPR moves from ⟦unverified: 9.66%⟧ to ⟦unverified: 20.43%⟧, an over-response of ⟦unverified: 4.6%⟧ relative with a calibration slope of ⟦unverified: 0.997⟧. The model's rate sensitivity is therefore directionally correct and close to the right magnitude at the one large shock observed. This is the single most informative piece of sensitivity evidence available, and it is favourable. It does not substitute for a symmetric shock ladder: no downward-incentive (extension) scenario was tested at all, and MSR valuation is most exposed to the extension tail.

**Untested dimensions.** No sensitivity was run on credit score, LTV, loan size or seasonality; no turnover floor or S-curve saturation behaviour was demonstrated; and no stress of the burnout path functional was performed. Because coefficient values were not available in the registered summary, validation could not verify that the incentive response saturates rather than growing without bound at extreme incentive, which is the standard failure mode of a linear-in-incentive hazard specification under a large rally.

## 6. Findings and recommendations

Findings are listed in severity order; the structured list accompanies this report.

**High — split populations cannot be mutually loan-disjoint (L2).** The four splits declare ⟦unverified: 2,515⟧ loan memberships against a `loan_id` space of at most ⟦unverified: 1,334,⟧ with `train` + `test` alone accounting for all ⟦unverified: 1,334⟧. The `vintage_holdout` and `out_of_time` samples must therefore re-use loans seen in training. *Recommendation:* publish the loan-ID intersection matrix across all four splits; rebuild the vintage holdout as a strictly loan- and vintage-disjoint sample and re-report its AUC and calibration; retain the out-of-time split as-is but relabel it explicitly as a time-forward sample on overlapping loans, and state that its AUC is not loan-out-of-sample. Until this is done, the vintage-holdout results should not be cited as independent validation.

**Medium — material over-prediction and low calibration slope on the vintage holdout (C1).** Slope ⟦unverified: 0.8373⟧ (outside a ⟦unverified: 0.90⟧–⟦unverified: 1.10⟧ band) with predicted CPR ⟦unverified: 6.57%⟧ against actual ⟦unverified: 5.63%⟧, a +⟦unverified: 16.7%⟧ relative over-statement concentrated in the high-score tail. *Recommendation:* recalibrate on a vintage-stratified basis, report calibration by score decile and by vintage cohort, and quantify the MSR value impact of the ⟦unverified: 16.7%⟧ CPR bias before any valuation use. Note that the test slope of ⟦unverified: 0.9365⟧ shows the same directional over-dispersion more mildly, so this is a specification tendency, not a one-split anomaly.

**Medium — two declared features are absent from the profiled training data (D1).** `bom_balance_log` and `rate_change_12m` appear in [[art:61276a96:run.features]] but in no profiled column of [[art:0356ef50:run.data_train]]. *Recommendation:* extend the data profile to all model inputs on all four splits, including per-split missingness, and publish a data dictionary establishing the measurement timestamp of `bom_balance_log` so its `before_period_start` designation can be independently verified.

**Medium — baseline hazard extrapolated far beyond loan-age support (X1).** The baseline is published past age ⟦unverified: 100⟧ on data supporting ages ⟦unverified: 0⟧–⟦unverified: 59,⟧ with the top knot at ⟦unverified: 53⟧; the resulting long tail is an assumption that drives long-horizon MSR cash flows. *Recommendation:* truncate the published baseline at the support boundary and replace the tail with an explicitly documented, separately justified long-age assumption; run high/low burnout-tail scenarios and report the MSR value range they imply.

**Medium — regime shift across the time cut is unquantified (S1).** The out-of-time event rate is ⟦unverified: 2.1⟧× training (CPR ⟦unverified: 19.53%⟧ versus ⟦unverified: 9.76%⟧) with no PSI or characteristic-drift report registered. Model response to the shift was good, so this is an evidence and monitoring gap rather than a performance failure. *Recommendation:* compute PSI for every covariate and for the score, train-versus-each-holdout, and record the thresholds used.

**Low — no collinearity diagnostics for a structurally overlapping covariate set (M1).** `note_rate`, `sato`, `incentive`, `rate_change_12m` and `burnout` are algebraically related; no VIF or condition-number statistic was registered. *Recommendation:* publish VIFs and the design-matrix condition number, and if they are elevated, confirm coefficient stability by bootstrap before interpreting any individual coefficient sign.

**Low — no challenger model (E1).** Nothing in the artifact store benchmarks the champion. *Recommendation:* fit at least a constant-hazard and a parsimonious logistic challenger on identical splits and report the AUC and CPR-error deltas.

**Explicitly not raised.** (i) *Out-of-sample degradation:* the maximum train-to-holdout AUC gap is ⟦unverified: 0.0165⟧, comfortably inside tolerance, and out-of-time discrimination is essentially unimpaired. (ii) *Label leakage:* no feature is declared `during_period` or `after_outcome`, and no single-feature AUC evidence of leakage exists; the ⟦unverified: 0.7883⟧ in-sample AUC is squarely in the range expected of a legitimate prepayment model, not the near-unity value a leak produces. (iii) *Run failure or runtime breach:* `run.duration_s` and `runtime.max_seconds` are both registered and nothing in `run.status` or `run.stderr` indicates a failure, though the values themselves were not inspectable in this review. (iv) *Regime coefficient instability:* the registered `model_summary` is truncated before the covariate block, so coefficient sign flips across regimes could be neither confirmed nor excluded; this is recorded as a scope limitation, not a finding, and should be closed by publishing the full coefficient table with standard errors.

### F-001 · L2 contamination · severity **high**

The split manifest declares 934 loans in train, 400 in test, 666 in vintage_holdout and 515 in out_of_time, a total of 2,515 loan memberships. The training data profile shows loan_id ranging from 1 to 1,334, bounding the universe at 1,334 distinct loans, and train (934) plus test (400) sums to exactly 1,334 — consistent with those two samples partitioning the entire loan universe. The 666 vintage_holdout loans and 515 out_of_time loans must therefore be drawn from loans already used to fit the model. Distinct rows_hash values across the four splits prove only that the row sets are not identical; they say nothing about loan-level overlap. For the out_of_time split, re-observing the same loans in later periods is normal practice but must be disclosed, since it means the 0.7846 out-of-time AUC is not out-of-sample at the loan level. For the vintage_holdout the overlap defeats the split's stated purpose — testing transfer to unseen loan cohorts — so its 0.7718 AUC and its calibration results overstate true cohort-transfer performance by an unknown margin and cannot be treated as independent validation evidence. Remediation requires publishing the loan-ID intersection matrix across all four splits and rebuilding the vintage holdout as strictly loan- and vintage-disjoint before re-reporting performance.

### F-002 · C1 calibration · severity **medium**

On the vintage_holdout split the calibration slope is 0.8373, outside a conventional 0.90-1.10 acceptance band, and mean predicted hazard is 0.005647 against an observed event rate of 0.004817, a 17.2% relative over-statement. This carries through to the annualized figure: predicted CPR 6.570% versus actual CPR 5.630%, a 16.7% relative over-prediction. The reconciliation is exact under 1-(1-h)^12, so this is a genuine level bias and not a reporting artifact. A slope materially below one means the over-prediction is concentrated in the high-score tail: the model overstates prepayment most for exactly the loans it ranks as most likely to prepay. For MSR valuation this understates model value and understates duration in a systematic direction. The same directional over-dispersion appears more mildly on the test split (slope 0.9365), indicating a specification tendency rather than a single-split anomaly; train (0.9937) and out_of_time (0.9969) slopes are sound. Recalibration on a vintage-stratified basis, calibration reporting by score decile and by cohort, and quantification of the MSR value impact of the 16.7% bias are required before valuation use.

### F-003 · D1 data integrity · severity **medium**

The feature inventory declares twelve model inputs, including bom_balance_log and rate_change_12m, both tagged before_period_start. Neither field appears in any profiled column of the training data, which contains only loan_id, period, note_rate, orig_ltv, credit_score, orig_upb_log, sato, loan_age, incentive, burnout, season_sin, season_cos and the prepaid target. Either the data profile is incomplete or these two features are constructed in an undocumented downstream step. Either way, a validator cannot confirm the range, sign convention, distribution or missingness of two inputs that feed the fitted hazard. This matters most for bom_balance_log: a balance measured at any point after the period start would directly encode the termination event, so its before_period_start designation is the single assertion standing between the model and a leak, and that assertion is currently unverifiable. Compounding the gap, missingness profiles were registered only for the training split, so the standard cross-split differential-missingness comparison could not be performed for any feature. Remediation requires profiling all twelve inputs on all four splits with per-field missingness, plus a data dictionary fixing the measurement timestamp of bom_balance_log.

### F-004 · X1 scenario analysis · severity **medium**

The fitted baseline hazard is tabulated continuously beyond loan age 101, but the training data support loan_age only to a maximum of 59 months and the highest age-spline knot is at 53. Within the supported range the curve is well behaved and economically correct: it rises monotonically from 0.000885 at age 0 to a peak of 0.003295 at age 43, a 3.7x seasoning ramp, then declines smoothly with no local reversals or sign errors, consistent with seasoning followed by burnout. Beyond age 59, however, the curve is pure boundary extrapolation of the spline and carries no information from any observation. The extrapolated tail decays only gently, from 0.003295 at the age-43 peak to roughly 0.00231 at age 101 — about 30% over five years — which silently imposes the strong assumption that long-seasoned loans keep prepaying at around two-thirds of peak speed indefinitely. MSR valuation integrates the hazard across the full remaining term of 30-year collateral, so this unsupported region drives a large share of discounted value, and an equally defensible stronger-burnout assumption would change the valuation materially. The extrapolation is nowhere documented as an assumption. The published baseline should be truncated at the support boundary and the long-age tail replaced by an explicitly justified assumption tested under high and low burnout scenarios.

### F-005 · S1 population drift · severity **medium**

The out_of_time split shows an event rate of 0.01795 against a training rate of 0.00852 — 2.1 times higher — with actual CPR rising from 9.76% to 19.53%. The training window runs from period 201402 to 201912, so the out-of-time sample sits beyond a refinance regime boundary, and a doubling of the target rate is a material population shift. No population stability index, characteristic drift report or score-distribution comparison was registered for any split, so drift could not be compared against any threshold and no thresholds were documented. The model itself responds well: mean predicted hazard rises from 0.00843 to 0.01887, calibration slope on the out-of-time split is 0.9969, predicted CPR of 20.43% overstates actual by only 4.6%, and AUC is essentially preserved at 0.7846 versus 0.7883 in training. This is strong evidence that the incentive and rate covariates are doing real economic work rather than encoding a base rate. The defect is therefore one of missing evidence and missing monitoring infrastructure rather than demonstrated performance failure: PSI must be computed for every covariate and for the score, train against each holdout, with documented amber/red thresholds, and incentive, rate_change_12m and burnout treated as priority series.

### F-006 · M1 collinearity · severity **low**

Five of the twelve covariates carry overlapping rate information: note_rate, sato (spread at origination), incentive and rate_change_12m are all algebraic functions of the same note rate and the prevailing mortgage rate, and burnout is a path functional of incentive. No variance inflation factor, condition number or correlation matrix was registered for the design matrix, so the degree of multicollinearity is unknown and could not be compared to any threshold. This specification is common practice and is not wrong in itself — predictive performance is largely insensitive to collinearity — but it is the standard setting in which individual coefficient signs and magnitudes become unstable, which matters here because MSR users interpret the incentive coefficient directly as a rate sensitivity. The registered model summary is truncated before the coefficient block, so neither the coefficients nor their standard errors were available to assess stability by inspection. Remediation is to publish VIFs and the design-matrix condition number alongside the full coefficient table, and, if they are elevated, to demonstrate coefficient stability by bootstrap before any coefficient is interpreted economically.

### F-007 · E1 effective challenge · severity **low**

The artifact store contains no challenger model, no benchmark specification and no prior model version. There is no constant-hazard baseline, no parsimonious logistic alternative and no table-driven industry prepayment benchmark against which the champion's 0.7883 training AUC, its 0.9937 calibration slope or its spline baseline specification can be judged. Without a benchmark, validation cannot demonstrate that the five-knot age spline and the twelve-covariate specification add value over a materially simpler alternative, nor can it establish whether the observed discrimination is good or merely typical for this data. No challenger was found to beat the champion because no challenger was run at all; this is recorded as an unmet element of effective challenge rather than as demonstrated champion inferiority. Remediation is to fit at least a constant-hazard baseline and a parsimonious logistic challenger on identical splits and report AUC, calibration-slope and CPR-error deltas against the champion.

Candidates raised and not promoted: none.

### Open items

No open item was recorded for this validation.

## 7. Ongoing monitoring recommendations

1. **Monthly actual-versus-predicted CPR**, reported at total-portfolio level and cut by vintage, coupon/incentive bucket, loan-age bucket and, once available, geography. Amber at a ⟦unverified: 10%⟧ relative CPR error over a rolling three months; red at ⟦unverified: 20%⟧ or at any single month above ⟦unverified: 25%⟧.
2. **Rolling calibration slope and intercept** on a twelve-month window, with the ⟦unverified: 0.90⟧–⟦unverified: 1.10⟧ band applied formally. The vintage-holdout slope of ⟦unverified: 0.8373⟧ should be the documented trigger precedent, and any production slope below ⟦unverified: 0.90⟧ for two consecutive months should force recalibration.
3. **Discrimination surveillance**: monthly AUC and KS on the most recent closed observation window, amber on a ⟦unverified: 0.05⟧ drop from the ⟦unverified: 0.7883⟧ development benchmark and red on ⟦unverified: 0.08⟧, recognizing that AUC falls mechanically when the event rate collapses and should be read alongside the base rate.
4. **PSI on every covariate and on the score**, monthly against the ⟦unverified: 2014⟧–⟦unverified: 2019⟧ training distribution, with the conventional ⟦unverified: 0.10⟧ / ⟦unverified: 0.25⟧ amber/red thresholds. Given the ⟦unverified: 2.1⟧× event-rate shift already visible in the out-of-time sample, `incentive`, `rate_change_12m` and `burnout` are the priority series.
5. **Loan-age support monitor**: track the share of the servicing book with `loan_age` above ⟦unverified: 59⟧ months — the edge of the estimation range — and report it alongside the CPR projection. When that share exceeds a documented tolerance, the extrapolated-tail assumption becomes the dominant driver of value and must be re-justified.
6. **Data-quality gate at scoring time**: per-field missingness, range and sign checks on all twelve inputs — including the two currently unprofiled features — with the job failing closed rather than imputing silently, plus a standing loan-ID disjointness assertion on any future refit's split construction.
7. **Annual full revalidation** with a rebuilt, genuinely disjoint vintage holdout, a refreshed challenger benchmark, published coefficients and VIFs, and a symmetric rate-shock ladder covering both refinance and extension scenarios. Recalibration should be triggered off-cycle by any red condition above or by a sustained regime change in the mortgage rate.

## Appendix A — Claims

Grounding precision 0.0000 before repair (0 of 191 claims verified; 179 unsupported, 7 dangling, 5 unattributed) and 0.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 0/36; conceptual_soundness 0/11; data_integrity 0/25; outcomes 0/65; sensitivity 0/18; findings 0/20; monitoring 0/16.

Developer claims: `plain_llm` runs no check over `package.yaml`'s declared claims See Appendix D.

Excluded numeric tokens (not claims): section_number (Section 6, Section 3, 1., 2.); citation_hash (b764932a, 61276a96, dca79f2f, 31ce3d08); package_version (1.0); extractor_returned_excluded_token (1.0, 6, 0.0, 3).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The model is a monthly discrete-time hazard with a loan-age… | 1 | months |  |  | eq |  | unsupported |  |
| 2 | summary | The model is a monthly discrete-time hazard with a loan-age… | 10 | months |  |  | eq |  | unsupported |  |
| 3 | summary | The model is a monthly discrete-time hazard with a loan-age… | 19 | months |  |  | eq |  | unsupported |  |
| 4 | summary | The model is a monthly discrete-time hazard with a loan-age… | 31 | months |  |  | eq |  | unsupported |  |
| 5 | summary | The model is a monthly discrete-time hazard with a loan-age… | 53 | months |  |  | eq |  | unsupported |  |
| 6 | summary | \| train \| 36,013 \| 934 \| 0.00852 \| 0.7883 \| 0.994 \| 9.76% \|… | 36013 | count | n_rows | train | eq |  | unsupported |  |
| 7 | summary | \| train \| 36,013 \| 934 \| 0.00852 \| 0.7883 \| 0.994 \| 9.76% \|… | 934 | count | n_loans | train | eq |  | unsupported |  |
| 8 | summary | \| train \| 36,013 \| 934 \| 0.00852 \| 0.7883 \| 0.994 \| 9.76% \|… | 0.00852 | ratio | event_rate | train | eq |  | unsupported |  |
| 9 | summary | \| train \| 36,013 \| 934 \| 0.00852 \| 0.7883 \| 0.994 \| 9.76% \|… | 0.7883 | ratio | auc | train | eq |  | unsupported |  |
| 10 | summary | \| train \| 36,013 \| 934 \| 0.00852 \| 0.7883 \| 0.994 \| 9.76% \|… | 0.994 | ratio | calibration_slope | train | eq |  | unsupported |  |
| 11 | summary | \| train \| 36,013 \| 934 \| 0.00852 \| 0.7883 \| 0.994 \| 9.76% \|… | 9.76 | percent | cpr_actual | train | eq |  | unsupported |  |
| 12 | summary | \| train \| 36,013 \| 934 \| 0.00852 \| 0.7883 \| 0.994 \| 9.76% \|… | 9.66 | percent | cpr_predicted | train | eq |  | unsupported |  |
| 13 | summary | \| test \| 15,382 \| 400 \| 0.00806 \| 0.7753 \| 0.937 \| 9.26% \| 9… | 15382 | count | n_rows | test | eq |  | unsupported |  |
| 14 | summary | \| test \| 15,382 \| 400 \| 0.00806 \| 0.7753 \| 0.937 \| 9.26% \| 9… | 400 | count | n_loans | test | eq |  | unsupported |  |
| 15 | summary | \| test \| 15,382 \| 400 \| 0.00806 \| 0.7753 \| 0.937 \| 9.26% \| 9… | 0.00806 | ratio | event_rate | test | eq |  | unsupported |  |
| 16 | summary | \| test \| 15,382 \| 400 \| 0.00806 \| 0.7753 \| 0.937 \| 9.26% \| 9… | 0.7753 | ratio | auc | test | eq |  | unsupported |  |
| 17 | summary | \| test \| 15,382 \| 400 \| 0.00806 \| 0.7753 \| 0.937 \| 9.26% \| 9… | 0.937 | ratio | calibration_slope | test | eq |  | unsupported |  |
| 18 | summary | \| test \| 15,382 \| 400 \| 0.00806 \| 0.7753 \| 0.937 \| 9.26% \| 9… | 9.26 | percent | cpr_actual | test | eq |  | unsupported |  |
| 19 | summary | \| test \| 15,382 \| 400 \| 0.00806 \| 0.7753 \| 0.937 \| 9.26% \| 9… | 9.32 | percent | cpr_predicted | test | eq |  | unsupported |  |
| 20 | summary | \| vintage_holdout \| 32,177 \| 666 \| 0.00482 \| 0.7718 \| 0.837… | 32177 | count | n_rows | vintage_holdout | eq |  | unsupported |  |
| 21 | summary | \| vintage_holdout \| 32,177 \| 666 \| 0.00482 \| 0.7718 \| 0.837… | 666 | count | n_loans | vintage_holdout | eq |  | unsupported |  |
| 22 | summary | \| vintage_holdout \| 32,177 \| 666 \| 0.00482 \| 0.7718 \| 0.837… | 0.00482 | ratio | event_rate | vintage_holdout | eq |  | unsupported |  |
| 23 | summary | \| vintage_holdout \| 32,177 \| 666 \| 0.00482 \| 0.7718 \| 0.837… | 0.7718 | ratio | auc | vintage_holdout | eq |  | unsupported |  |
| 24 | summary | \| vintage_holdout \| 32,177 \| 666 \| 0.00482 \| 0.7718 \| 0.837… | 0.837 | ratio | calibration_slope | vintage_holdout | eq |  | unsupported |  |
| 25 | summary | \| vintage_holdout \| 32,177 \| 666 \| 0.00482 \| 0.7718 \| 0.837… | 5.63 | percent | cpr_actual | vintage_holdout | eq |  | unsupported |  |
| 26 | summary | \| vintage_holdout \| 32,177 \| 666 \| 0.00482 \| 0.7718 \| 0.837… | 6.57 | percent | cpr_predicted | vintage_holdout | eq |  | unsupported |  |
| 27 | summary | \| out_of_time \| 12,257 \| 515 \| 0.01795 \| 0.7846 \| 0.997 \| 19… | 12257 | count | n_rows | out_of_time | eq |  | unsupported |  |
| 28 | summary | \| out_of_time \| 12,257 \| 515 \| 0.01795 \| 0.7846 \| 0.997 \| 19… | 515 | count | n_loans | out_of_time | eq |  | unsupported |  |
| 29 | summary | \| out_of_time \| 12,257 \| 515 \| 0.01795 \| 0.7846 \| 0.997 \| 19… | 0.01795 | ratio | event_rate | out_of_time | eq |  | unsupported |  |
| 30 | summary | \| out_of_time \| 12,257 \| 515 \| 0.01795 \| 0.7846 \| 0.997 \| 19… | 0.7846 | ratio | auc | out_of_time | eq |  | unsupported |  |
| 31 | summary | \| out_of_time \| 12,257 \| 515 \| 0.01795 \| 0.7846 \| 0.997 \| 19… | 0.997 | ratio | calibration_slope | out_of_time | eq |  | unsupported |  |
| 32 | summary | \| out_of_time \| 12,257 \| 515 \| 0.01795 \| 0.7846 \| 0.997 \| 19… | 19.53 | percent | cpr_actual | out_of_time | eq |  | unsupported |  |
| 33 | summary | \| out_of_time \| 12,257 \| 515 \| 0.01795 \| 0.7846 \| 0.997 \| 19… | 20.43 | percent | cpr_predicted | out_of_time | eq |  | unsupported |  |
| 34 | summary | **Overall conclusion.** Rank-ordering performance is sound a… | 1 | ratio |  |  | eq |  | unsupported |  |
| 35 | summary | **Overall conclusion.** Rank-ordering performance is sound a… | 1 | ratio |  |  | eq |  | unsupported |  |
| 36 | summary | **Overall conclusion.** Rank-ordering performance is sound a… | 12 | months |  |  | eq |  | unsupported |  |
| 37 | conceptual_soundness | The baseline hazard in has an economically sensible shape: i… | 0.000885 | ratio | baseline_hazard |  | eq | `[[art:b764932a:run.model_summary]]` | dangling |  |
| 38 | conceptual_soundness | The baseline hazard in has an economically sensible shape: i… | 0 | months | loan_age |  | eq | `[[art:b764932a:run.model_summary]]` | dangling |  |
| 39 | conceptual_soundness | The baseline hazard in has an economically sensible shape: i… | 0.003295 | ratio | baseline_hazard |  | eq | `[[art:b764932a:run.model_summary]]` | dangling |  |
| 40 | conceptual_soundness | The baseline hazard in has an economically sensible shape: i… | 43 | months | loan_age |  | eq | `[[art:b764932a:run.model_summary]]` | dangling |  |
| 41 | conceptual_soundness | The baseline hazard in has an economically sensible shape: i… | 3.7 | ratio | baseline_hazard |  | eq | `[[art:b764932a:run.model_summary]]` | dangling |  |
| 42 | conceptual_soundness | The weakness is at the boundary. The training data support t… | 59 | months | loan_age | train | eq |  | unsupported |  |
| 43 | conceptual_soundness | The weakness is at the boundary. The training data support t… | 59 | months | loan_age | train | eq |  | unsupported |  |
| 44 | conceptual_soundness | The weakness is at the boundary. The training data support t… | 53 | months | loan_age |  | eq |  | unsupported |  |
| 45 | conceptual_soundness | The weakness is at the boundary. The training data support t… | 100 | months | loan_age |  | eq |  | unsupported |  |
| 46 | conceptual_soundness | The weakness is at the boundary. The training data support t… | 59 | months | loan_age |  | eq |  | unsupported |  |
| 47 | conceptual_soundness | The weakness is at the boundary. The training data support t… | 30 | months |  |  | eq |  | unsupported |  |
| 48 | data_integrity | **Completeness.** The raw training profile reports zero miss… | 36013 | count | row_count | train | eq |  | unsupported |  |
| 49 | data_integrity | **Split construction.** The split manifest reports distinct… | 1 | count | loan_id | train | eq |  | unsupported |  |
| 50 | data_integrity | **Split construction.** The split manifest reports distinct… | 1334 | count | loan_count |  | eq |  | unattributed |  |
| 51 | data_integrity | **Split construction.** The split manifest reports distinct… | 1334 | count | loan_count |  | eq |  | unattributed |  |
| 52 | data_integrity | **Split construction.** The split manifest reports distinct… | 934 | count | loan_count | train | eq |  | unsupported |  |
| 53 | data_integrity | **Split construction.** The split manifest reports distinct… | 400 | count | loan_count | test | eq |  | unsupported |  |
| 54 | data_integrity | **Split construction.** The split manifest reports distinct… | 1334 | count | loan_count |  | eq |  | unattributed |  |
| 55 | data_integrity | **Split construction.** The split manifest reports distinct… | 666 | count | loan_count | vintage_holdout | eq |  | unsupported |  |
| 56 | data_integrity | **Split construction.** The split manifest reports distinct… | 515 | count | loan_count | out_of_time | eq |  | unsupported |  |
| 57 | data_integrity | **Split construction.** The split manifest reports distinct… | 2515 | count | loan_count |  | eq |  | unsupported |  |
| 58 | data_integrity | **Split construction.** The split manifest reports distinct… | 1334 | count |  |  | eq |  | unattributed |  |
| 59 | data_integrity | **Split construction.** The split manifest reports distinct… | 666 | count | loan_count | vintage_holdout | eq |  | unsupported |  |
| 60 | data_integrity | **Split construction.** The split manifest reports distinct… | 934 | count | loan_count | train | eq |  | unsupported |  |
| 61 | data_integrity | **Split construction.** The split manifest reports distinct… | 0.7718 | ratio | auc | vintage_holdout | eq |  | unsupported |  |
| 62 | data_integrity | **Drift.** No population stability index or characteristic-d… | 0.01795 | ratio | event_rate | out_of_time | eq |  | unsupported |  |
| 63 | data_integrity | **Drift.** No population stability index or characteristic-d… | 2.1 | ratio | event_rate |  | ratio |  | unsupported |  |
| 64 | data_integrity | **Drift.** No population stability index or characteristic-d… | 0.00852 | ratio | event_rate | train | eq |  | unsupported |  |
| 65 | data_integrity | **Drift.** No population stability index or characteristic-d… | 9.76 | percent | actual_cpr | train | eq |  | unsupported |  |
| 66 | data_integrity | **Drift.** No population stability index or characteristic-d… | 19.53 | percent | actual_cpr | out_of_time | eq |  | unsupported |  |
| 67 | data_integrity | **Drift.** No population stability index or characteristic-d… | 2014 | ratio |  | train | eq |  | unsupported |  |
| 68 | data_integrity | **Drift.** No population stability index or characteristic-d… | 2019 | ratio |  | train | eq |  | unsupported |  |
| 69 | data_integrity | **Drift.** No population stability index or characteristic-d… | 201402 | ratio |  | train | eq |  | unsupported |  |
| 70 | data_integrity | **Drift.** No population stability index or characteristic-d… | 201912 | ratio |  | train | eq |  | unsupported |  |
| 71 | data_integrity | **Drift.** No population stability index or characteristic-d… | 0.00843 | ratio | mean_predicted_hazard | train | eq |  | unsupported |  |
| 72 | data_integrity | **Drift.** No population stability index or characteristic-d… | 0.01887 | ratio | mean_predicted_hazard | out_of_time | eq |  | unsupported |  |
| 73 | outcomes | **Discrimination.** AUC is 0.7883 in-sample and 0.7753 / 0.7… | 0.7883 | ratio | auc | train | eq |  | unsupported |  |
| 74 | outcomes | **Discrimination.** AUC is 0.7883 in-sample and 0.7753 / 0.7… | 0.7753 | ratio | auc | test | eq |  | unsupported |  |
| 75 | outcomes | **Discrimination.** AUC is 0.7883 in-sample and 0.7753 / 0.7… | 0.7718 | ratio | auc | vintage_holdout | eq |  | unsupported |  |
| 76 | outcomes | **Discrimination.** AUC is 0.7883 in-sample and 0.7753 / 0.7… | 0.7846 | ratio | auc | out_of_time | eq |  | unsupported |  |
| 77 | outcomes | **Discrimination.** AUC is 0.7883 in-sample and 0.7753 / 0.7… | 0.577 | ratio | gini | train | eq |  | unsupported |  |
| 78 | outcomes | **Discrimination.** AUC is 0.7883 in-sample and 0.7753 / 0.7… | 0.551 | ratio | gini | test | eq |  | unsupported |  |
| 79 | outcomes | **Discrimination.** AUC is 0.7883 in-sample and 0.7753 / 0.7… | 0.544 | ratio | gini | vintage_holdout | eq |  | unsupported |  |
| 80 | outcomes | **Discrimination.** AUC is 0.7883 in-sample and 0.7753 / 0.7… | 0.569 | ratio | gini | out_of_time | eq |  | unsupported |  |
| 81 | outcomes | **Discrimination.** AUC is 0.7883 in-sample and 0.7753 / 0.7… | 0.456 | ratio | ks | train | eq |  | unsupported |  |
| 82 | outcomes | **Discrimination.** AUC is 0.7883 in-sample and 0.7753 / 0.7… | 0.416 | ratio | ks | test | eq |  | unsupported |  |
| 83 | outcomes | **Discrimination.** AUC is 0.7883 in-sample and 0.7753 / 0.7… | 0.452 | ratio | ks | vintage_holdout | eq |  | unsupported |  |
| 84 | outcomes | **Discrimination.** AUC is 0.7883 in-sample and 0.7753 / 0.7… | 0.432 | ratio | ks | out_of_time | eq |  | unsupported |  |
| 85 | outcomes | **Discrimination.** AUC is 0.7883 in-sample and 0.7753 / 0.7… | 0.0165 | ratio | delta_auc | vintage_holdout | delta |  | unsupported |  |
| 86 | outcomes | **Discrimination.** AUC is 0.7883 in-sample and 0.7753 / 0.7… | 0.0131 | ratio | delta_auc | test | delta |  | unsupported |  |
| 87 | outcomes | **Discrimination.** AUC is 0.7883 in-sample and 0.7753 / 0.7… | 0.0037 | ratio | delta_auc | out_of_time | delta |  | unsupported |  |
| 88 | outcomes | - `train`: slope 0.9937, mean predicted 0.008427 versus obse… | 0.9937 | ratio | calibration_slope | train | eq |  | unsupported |  |
| 89 | outcomes | - `train`: slope 0.9937, mean predicted 0.008427 versus obse… | 0.008427 | ratio | mean_predicted | train | eq |  | unsupported |  |
| 90 | outcomes | - `train`: slope 0.9937, mean predicted 0.008427 versus obse… | 0.008525 | ratio | event_rate | train | eq |  | unsupported |  |
| 91 | outcomes | - `train`: slope 0.9937, mean predicted 0.008427 versus obse… | 1.1 | percent |  |  | eq |  | unattributed |  |
| 92 | outcomes | - `train`: slope 0.9937, mean predicted 0.008427 versus obse… | 9.66 | percent | cpr_predicted | train | eq |  | unsupported |  |
| 93 | outcomes | - `train`: slope 0.9937, mean predicted 0.008427 versus obse… | 9.76 | percent | cpr_actual | train | eq |  | unsupported |  |
| 94 | outcomes | - `out_of_time`: slope 0.9969, mean predicted 0.018866 versu… | 0.9969 | ratio | calibration_slope | out_of_time | eq |  | unsupported |  |
| 95 | outcomes | - `out_of_time`: slope 0.9969, mean predicted 0.018866 versu… | 0.018866 | ratio | mean_predicted | out_of_time | eq |  | unsupported |  |
| 96 | outcomes | - `out_of_time`: slope 0.9969, mean predicted 0.018866 versu… | 0.017949 | ratio | event_rate | out_of_time | eq |  | unsupported |  |
| 97 | outcomes | - `out_of_time`: slope 0.9969, mean predicted 0.018866 versu… | 5.1 | percent | calibration_error | out_of_time | eq |  | unsupported |  |
| 98 | outcomes | - `out_of_time`: slope 0.9969, mean predicted 0.018866 versu… | 20.43 | percent | cpr_predicted | out_of_time | eq |  | unsupported |  |
| 99 | outcomes | - `out_of_time`: slope 0.9969, mean predicted 0.018866 versu… | 19.53 | percent | cpr_actual | out_of_time | eq |  | unsupported |  |
| 100 | outcomes | - `out_of_time`: slope 0.9969, mean predicted 0.018866 versu… | 4.6 | percent | cpr_error | out_of_time | eq |  | unsupported |  |
| 101 | outcomes | - `test`: slope 0.9365, mean predicted 0.008116 versus obser… | 0.9365 | ratio | calibration_slope | test | eq |  | unsupported |  |
| 102 | outcomes | - `test`: slope 0.9365, mean predicted 0.008116 versus obser… | 0.008116 | ratio | mean_predicted | test | eq |  | unsupported |  |
| 103 | outcomes | - `test`: slope 0.9365, mean predicted 0.008116 versus obser… | 0.008061 | ratio | event_rate | test | eq |  | unsupported |  |
| 104 | outcomes | - `test`: slope 0.9365, mean predicted 0.008116 versus obser… | 0.7 | percent | calibration_error | test | eq |  | unsupported |  |
| 105 | outcomes | - `test`: slope 0.9365, mean predicted 0.008116 versus obser… | 9.32 | percent | cpr_predicted | test | eq |  | unsupported |  |
| 106 | outcomes | - `test`: slope 0.9365, mean predicted 0.008116 versus obser… | 9.26 | percent | cpr_actual | test | eq |  | unsupported |  |
| 107 | outcomes | - `test`: slope 0.9365, mean predicted 0.008116 versus obser… | 0.95 | ratio | calibration_slope | test | eq |  | unsupported |  |
| 108 | outcomes | - `test`: slope 0.9365, mean predicted 0.008116 versus obser… | 0.9 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 109 | outcomes | - `test`: slope 0.9365, mean predicted 0.008116 versus obser… | 1.1 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 110 | outcomes | - `vintage_holdout`: slope 0.8373, mean predicted 0.005647 v… | 0.8373 | ratio | calibration_slope | vintage_holdout | eq |  | unsupported |  |
| 111 | outcomes | - `vintage_holdout`: slope 0.8373, mean predicted 0.005647 v… | 0.005647 | ratio | mean_predicted | vintage_holdout | eq |  | unsupported |  |
| 112 | outcomes | - `vintage_holdout`: slope 0.8373, mean predicted 0.005647 v… | 0.004817 | ratio | event_rate | vintage_holdout | eq |  | unsupported |  |
| 113 | outcomes | - `vintage_holdout`: slope 0.8373, mean predicted 0.005647 v… | 17.2 | percent | calibration_error | vintage_holdout | eq |  | unsupported |  |
| 114 | outcomes | - `vintage_holdout`: slope 0.8373, mean predicted 0.005647 v… | 6.57 | percent | cpr_predicted | vintage_holdout | eq |  | unsupported |  |
| 115 | outcomes | - `vintage_holdout`: slope 0.8373, mean predicted 0.005647 v… | 5.63 | percent | cpr_actual | vintage_holdout | eq |  | unsupported |  |
| 116 | outcomes | - `vintage_holdout`: slope 0.8373, mean predicted 0.005647 v… | 16.7 | percent | cpr_error | vintage_holdout | eq |  | unsupported |  |
| 117 | outcomes | - `vintage_holdout`: slope 0.8373, mean predicted 0.005647 v… | 0.9 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 118 | outcomes | - `vintage_holdout`: slope 0.8373, mean predicted 0.005647 v… | 1.1 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 119 | outcomes | The vintage-holdout result is the economically significant o… | 16.7 | percent | cpr_error | vintage_holdout | eq |  | unsupported |  |
| 120 | outcomes | The vintage-holdout result is the economically significant o… | 0.004763 | ratio | brier | vintage_holdout | eq |  | unsupported |  |
| 121 | outcomes | The vintage-holdout result is the economically significant o… | 0.02811 | ratio | log_loss | vintage_holdout | eq |  | unsupported |  |
| 122 | outcomes | **Reconciliation checks.** Every split's reported CPR reconc… | 1 | ratio |  |  | eq |  | unsupported |  |
| 123 | outcomes | **Reconciliation checks.** Every split's reported CPR reconc… | 1 | ratio |  |  | eq |  | unsupported |  |
| 124 | outcomes | **Reconciliation checks.** Every split's reported CPR reconc… | 12 | months |  |  | eq |  | unsupported |  |
| 125 | outcomes | **Reconciliation checks.** Every split's reported CPR reconc… | 1 | ratio |  |  | eq |  | unsupported |  |
| 126 | outcomes | **Reconciliation checks.** Every split's reported CPR reconc… | 1 | ratio |  |  | eq |  | unsupported |  |
| 127 | outcomes | **Reconciliation checks.** Every split's reported CPR reconc… | 0.018866 | ratio | mean_predicted | out_of_time | eq |  | unsupported |  |
| 128 | outcomes | **Reconciliation checks.** Every split's reported CPR reconc… | 12 | months |  |  | eq |  | unsupported |  |
| 129 | outcomes | **Reconciliation checks.** Every split's reported CPR reconc… | 0.2043 | ratio | cpr_predicted | out_of_time | eq |  | unsupported |  |
| 130 | outcomes | **Reconciliation checks.** Every split's reported CPR reconc… | 0.20432 | ratio | cpr_predicted | out_of_time | eq |  | unsupported |  |
| 131 | outcomes | **Reconciliation checks.** Every split's reported CPR reconc… | 1 | ratio |  |  | eq |  | unsupported |  |
| 132 | outcomes | **Reconciliation checks.** Every split's reported CPR reconc… | 1 | ratio |  |  | eq |  | unsupported |  |
| 133 | outcomes | **Reconciliation checks.** Every split's reported CPR reconc… | 0.005647 | ratio | mean_predicted | vintage_holdout | eq |  | unsupported |  |
| 134 | outcomes | **Reconciliation checks.** Every split's reported CPR reconc… | 12 | months |  |  | eq |  | unsupported |  |
| 135 | outcomes | **Reconciliation checks.** Every split's reported CPR reconc… | 0.0657 | ratio | cpr_predicted | vintage_holdout | eq |  | unsupported |  |
| 136 | outcomes | **Reconciliation checks.** Every split's reported CPR reconc… | 0.0657 | ratio | cpr_predicted | vintage_holdout | eq |  | unsupported |  |
| 137 | outcomes | **Effective challenge.** No challenger or benchmark model wa… | 0.7883 | ratio | auc | train | eq |  | unsupported |  |
| 138 | sensitivity | **Age/seasoning profile.** The baseline hazard in is monoton… | 0 | months |  |  | eq | `[[art:b764932a:run.model_summary]]` | dangling |  |
| 139 | sensitivity | **Age/seasoning profile.** The baseline hazard in is monoton… | 43 | months |  |  | eq | `[[art:b764932a:run.model_summary]]` | dangling |  |
| 140 | sensitivity | **Age/seasoning profile.** The baseline hazard in is monoton… | 0 | months |  |  | eq |  | unsupported |  |
| 141 | sensitivity | **Age/seasoning profile.** The baseline hazard in is monoton… | 59 | months |  |  | eq |  | unsupported |  |
| 142 | sensitivity | **Extrapolation risk.** The curve is nonetheless published f… | 59 | months |  | train | eq |  | unsupported |  |
| 143 | sensitivity | **Extrapolation risk.** The curve is nonetheless published f… | 53 | months |  |  | eq |  | unsupported |  |
| 144 | sensitivity | **Extrapolation risk.** The curve is nonetheless published f… | 100 | months |  |  | eq |  | unsupported |  |
| 145 | sensitivity | **Extrapolation risk.** The curve is nonetheless published f… | 0.003295 | ratio | baseline_hazard |  | eq |  | unsupported |  |
| 146 | sensitivity | **Extrapolation risk.** The curve is nonetheless published f… | 43 | months |  |  | eq |  | unsupported |  |
| 147 | sensitivity | **Extrapolation risk.** The curve is nonetheless published f… | 0.00231 | ratio | baseline_hazard |  | eq |  | unsupported |  |
| 148 | sensitivity | **Extrapolation risk.** The curve is nonetheless published f… | 101 | months |  |  | eq |  | unsupported |  |
| 149 | sensitivity | **Extrapolation risk.** The curve is nonetheless published f… | 30 | percent | baseline_hazard |  | eq |  | unsupported |  |
| 150 | sensitivity | **Implicit rate-shock evidence.** The out-of-time split func… | 9.76 | percent | cpr |  | eq |  | unsupported |  |
| 151 | sensitivity | **Implicit rate-shock evidence.** The out-of-time split func… | 19.53 | percent | cpr | out_of_time | eq |  | unsupported |  |
| 152 | sensitivity | **Implicit rate-shock evidence.** The out-of-time split func… | 9.66 | percent | predicted_cpr |  | eq |  | unsupported |  |
| 153 | sensitivity | **Implicit rate-shock evidence.** The out-of-time split func… | 20.43 | percent | predicted_cpr | out_of_time | eq |  | unsupported |  |
| 154 | sensitivity | **Implicit rate-shock evidence.** The out-of-time split func… | 4.6 | percent |  | out_of_time | eq |  | unsupported |  |
| 155 | sensitivity | **Implicit rate-shock evidence.** The out-of-time split func… | 0.997 | ratio | calibration_slope | out_of_time | eq |  | unsupported |  |
| 156 | findings | **High — split populations cannot be mutually loan-disjoint… | 2515 | count |  |  | eq |  | unsupported |  |
| 157 | findings | **High — split populations cannot be mutually loan-disjoint… | 1334 | count |  |  | eq |  | unsupported |  |
| 158 | findings | **High — split populations cannot be mutually loan-disjoint… | 1334 | count |  |  | eq |  | unsupported |  |
| 159 | findings | **Medium — material over-prediction and low calibration slop… | 0.8373 | ratio | calibration_slope | vintage_holdout | eq |  | unsupported |  |
| 160 | findings | **Medium — material over-prediction and low calibration slop… | 0.9 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 161 | findings | **Medium — material over-prediction and low calibration slop… | 1.1 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 162 | findings | **Medium — material over-prediction and low calibration slop… | 6.57 | percent | predicted_cpr | vintage_holdout | eq |  | unsupported |  |
| 163 | findings | **Medium — material over-prediction and low calibration slop… | 5.63 | percent | actual_cpr | vintage_holdout | eq |  | unsupported |  |
| 164 | findings | **Medium — material over-prediction and low calibration slop… | 16.7 | percent | cpr_bias | vintage_holdout | eq |  | unsupported |  |
| 165 | findings | **Medium — material over-prediction and low calibration slop… | 16.7 | percent | cpr_bias | vintage_holdout | eq |  | unsupported |  |
| 166 | findings | **Medium — material over-prediction and low calibration slop… | 0.9365 | ratio | calibration_slope | test | eq |  | unsupported |  |
| 167 | findings | **Medium — baseline hazard extrapolated far beyond loan-age… | 100 | months |  |  | eq |  | unsupported |  |
| 168 | findings | **Medium — baseline hazard extrapolated far beyond loan-age… | 0 | months |  |  | eq |  | unsupported |  |
| 169 | findings | **Medium — baseline hazard extrapolated far beyond loan-age… | 59 | months |  |  | eq |  | unsupported |  |
| 170 | findings | **Medium — baseline hazard extrapolated far beyond loan-age… | 53 | months |  |  | eq |  | unsupported |  |
| 171 | findings | **Medium — regime shift across the time cut is unquantified… | 2.1 | ratio | event_rate | out_of_time | eq |  | unsupported |  |
| 172 | findings | **Medium — regime shift across the time cut is unquantified… | 19.53 | percent | event_rate | out_of_time | eq |  | unsupported |  |
| 173 | findings | **Medium — regime shift across the time cut is unquantified… | 9.76 | percent | event_rate | train | eq |  | unsupported |  |
| 174 | findings | **Explicitly not raised.** (i) *Out-of-sample degradation:*… | 0.0165 | ratio | delta_auc |  | eq |  | unsupported |  |
| 175 | findings | **Explicitly not raised.** (i) *Out-of-sample degradation:*… | 0.7883 | ratio | auc | train | eq |  | unsupported |  |
| 176 | monitoring | 1. **Monthly actual-versus-predicted CPR**, reported at tota… | 10 | percent | cpr |  | eq |  | unsupported |  |
| 177 | monitoring | 1. **Monthly actual-versus-predicted CPR**, reported at tota… | 20 | percent | cpr |  | eq |  | unsupported |  |
| 178 | monitoring | 1. **Monthly actual-versus-predicted CPR**, reported at tota… | 25 | percent | cpr |  | eq |  | unsupported |  |
| 179 | monitoring | 2. **Rolling calibration slope and intercept** on a twelve-m… | 0.9 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 180 | monitoring | 2. **Rolling calibration slope and intercept** on a twelve-m… | 1.1 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 181 | monitoring | 2. **Rolling calibration slope and intercept** on a twelve-m… | 0.8373 | ratio | calibration_slope | vintage_holdout | eq |  | unsupported |  |
| 182 | monitoring | 2. **Rolling calibration slope and intercept** on a twelve-m… | 0.9 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 183 | monitoring | 3. **Discrimination surveillance**: monthly AUC and KS on th… | 0.05 | ratio | auc |  | eq |  | unsupported |  |
| 184 | monitoring | 3. **Discrimination surveillance**: monthly AUC and KS on th… | 0.7883 | ratio | auc | train | eq |  | unsupported |  |
| 185 | monitoring | 3. **Discrimination surveillance**: monthly AUC and KS on th… | 0.08 | ratio | auc |  | eq |  | unsupported |  |
| 186 | monitoring | 4. **PSI on every covariate and on the score**, monthly agai… | 2014 | ratio |  | train | eq |  | unsupported |  |
| 187 | monitoring | 4. **PSI on every covariate and on the score**, monthly agai… | 2019 | ratio |  | train | eq |  | unsupported |  |
| 188 | monitoring | 4. **PSI on every covariate and on the score**, monthly agai… | 0.1 | ratio | psi |  | eq |  | unsupported |  |
| 189 | monitoring | 4. **PSI on every covariate and on the score**, monthly agai… | 0.25 | ratio | psi |  | eq |  | unsupported |  |
| 190 | monitoring | 4. **PSI on every covariate and on the score**, monthly agai… | 2.1 | ratio | event_rate | out_of_time | ratio |  | unsupported |  |
| 191 | monitoring | 5. **Loan-age support monitor**: track the share of the serv… | 59 | months | loan_age |  | eq |  | unsupported |  |

## Appendix B — Artifact index

The store holds 19 artifacts; the 13 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `run.data_out_of_time` | `7ddcc721` | table | table, 12257 rows | the subject's data_out_of_time.csv |
| `run.data_test` | `f0ac9fe8` | table | table, 15382 rows | the subject's data_test.csv |
| `run.data_train` | `0356ef50` | table | table, 36013 rows | the subject's data_train.csv |
| `run.data_vintage_holdout` | `940d14da` | table | table, 32177 rows | the subject's data_vintage_holdout.csv |
| `run.features` | `61276a96` | json | json | the subject's features.json |
| `run.metrics` | `31ce3d08` | json | json | the subject's metrics.json |
| `run.model_summary` | `b764932a` | json | json | the subject's model_summary.json |
| `run.predictions_out_of_time` | `f3fcb713` | table | table, 12257 rows | the subject's predictions_out_of_time.csv |
| `run.predictions_test` | `d74c6620` | table | table, 15382 rows | the subject's predictions_test.csv |
| `run.predictions_train` | `f0b43d19` | table | table, 36013 rows | the subject's predictions_train.csv |
| `run.predictions_vintage_holdout` | `afa7c750` | table | table, 32177 rows | the subject's predictions_vintage_holdout.csv |
| `run.projection` | `cbc0b707` | json | json | the subject's projection.json |
| `run.splits` | `dca79f2f` | json | json | the subject's splits.json |

## Appendix C — Run trace summary

| quantity | value |
|---|---|
| tool calls | 1 (run_model 1) |
| plan steps (bounded loop) | 0 |
| LLM calls | 8 (plain_llm 1, extract 7) |
| re-asks | 0 |
| repair rounds | 0 |
| tokens in / out | 65,378 / 42,344 |
| notional cost (USD) | 1.7016 |
| wall-clock (s) | 494.32 |
| subject run (s) | 2.58 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | msr_prepayment-plain_llm-20260918T220554Z-986f3824 |

## Appendix D — Not checked

| item | reason |
|---|---|
| `check_stability` (R1) | this configuration runs no checks |
| `run_scenarios` (X1) | this configuration runs no checks |
| developer claims (T1, claim channel) | `plain_llm` runs no check over `package.yaml`'s declared claims |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
| every check of spec 3.7 but `run_model` | `plain_llm` runs the subject and one model call, by design |
