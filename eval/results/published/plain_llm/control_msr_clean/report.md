---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: msr_prepayment
version: "1.0"
model_type: discrete_time_hazard
configuration: plain_llm
model: claude-opus-5[1m]
run_id: msr_prepayment-plain_llm-20260918T074209Z-986f3824
data_mode: synthetic
synthetic_n: 2000
grounding_precision_pre: 0.0000
grounding_precision_post: 0.0000
n_claims: 140
n_findings_by_severity: {high: 1, medium: 5, low: 1, info: 3}
generated: "2026-09-18T07:42:09Z"
illustrative: false
---

# Validation report — `msr_prepayment` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `msr_prepayment` v1.0 | `plain_llm` | claude-opus-5[1m] | synthetic, n = 2000 | 0.0000 → 0.0000 | 1 / 5 / 1 / 3 |
<!-- quaestor:renderer:end -->

The subject is a discrete-time hazard model of voluntary prepayment estimated at the loan-month level, with a spline in loan age (knots at ⟦unverified: 1,⟧ ⟦unverified: 10,⟧ ⟦unverified: 19,⟧ ⟦unverified: 31⟧ and ⟦unverified: 53⟧ months, [[art:b764932a:run.model_summary#age_spline_knots]]) and twelve covariates ([[art:61276a96:run.features]]). It is evaluated on four splits — `train`, `test`, `out_of_time` and `vintage_holdout` ([[art:dca79f2f:run.splits]], [[art:31ce3d08:run.metrics]]).

Scope of this review: conceptual soundness of the specification, internal consistency and integrity of the reported artifacts, out-of-sample and out-of-time outcomes, calibration, and the usability of the hazard curve for valuation projection. Not in scope, because the artifacts do not support it: re-derivation of parameter estimates, loan-level re-scoring, and any independent benchmark.

Headline conclusion: **discrimination is stable and the reported metric set is internally consistent, but the model is materially biased upward on the vintage holdout and its hazard curve is published well beyond the age range it was estimated on.** The first issue is a valuation-relevant calibration defect; the second is a projection defect. Neither is fatal to the modelling approach, but both must be remediated before the model is used to mark MSR.

What I could verify held up. Every `event_rate` in [[art:31ce3d08:run.metrics]] matches the corresponding entry in [[art:dca79f2f:run.splits]], every row count matches, `gini` equals `2·AUC − 1` on all four splits, and each `cpr_*` figure is the correct twelve-month annualisation of the matching monthly rate (e.g. test: `1 − (1 − 0.008061)^12 = 0.09256`, which is `cpr_actual` to six places). The training `event_rate` also equals the mean of `prepaid` in the raw profile ([[art:010d5167:plain_llm.profile]]). There is no arithmetic defect in the reported metric set.

## 2. Conceptual soundness

**Specification.** A discrete-time hazard on loan-months is the appropriate frame for prepayment: it handles right-censoring naturally, it lets the age ramp be estimated non-parametrically, and it produces the monthly SMM that an MSR cash-flow engine consumes. The covariate set is the conventional one — note rate, original LTV, credit score, log original UPB and SATO at origination; loan age, refinance incentive, burnout, log beginning-of-month balance, twelve-month rate change and a sine/cosine seasonality pair as time-varying ([[art:61276a96:run.features]]). Nothing in that list is unusual or unjustified for an agency prepayment model.

**Leakage by construction.** The timing declarations are clean: five features `at_origination`, seven `before_period_start`, zero `during_period`, zero `after_outcome` ([[art:61276a96:run.features]]). Every time-varying covariate — including `bom_balance_log`, the one most at risk of being computed end-of-period — is declared as known before the period opens. I found no L1 defect. I note the limit of this check: it rests on the developer's own timing labels, and no univariate AUCs were reported, so the "single feature above ⟦unverified: 0.90⟧" arm of the leakage test could not be executed.

**Baseline hazard shape.** The tabulated baseline ([[art:b764932a:run.model_summary#baseline_hazard]]) rises monotonically from ⟦unverified: 0.000885⟧ at age ⟦unverified: 0⟧ to a peak of ⟦unverified: 0.003295⟧ at age ⟦unverified: 43,⟧ then declines slowly and monotonically thereafter. Annualised, that is a ramp from roughly ⟦unverified: 1.1%⟧ CPR to ⟦unverified: 3.9%⟧ CPR at the seasoning peak. The shape is economically right — a seasoning ramp, a turnover plateau, then gradual decay — and the peak sits in a defensible window.

**Coefficients are not disclosed.** The model summary supplied contains the spline knots and the baseline hazard table but no covariate coefficient vector. I therefore could not perform the most basic economic check on a prepayment model: that the `incentive` coefficient is positive, that `burnout` is negative, that `credit_score` enters positively and that `orig_ltv` enters negatively. This is a documentation gap, not an identified error, and it is recorded as such.

**Correlated regressors.** Four of the twelve covariates are algebraically entangled. `sato` is a rate spread at origination, `incentive` is a rate spread at the observation date, `rate_change_12m` is the change in the rate that drives `incentive`, and `note_rate` is a common term in the first two. Separately, `orig_upb_log` and `bom_balance_log` are the same quantity at two points in the loan's life and will be correlated near ⟦unverified: 0.9⟧ in a book this lightly seasoned. No VIF or condition number was reported. Point estimates on individual rate terms should be treated as unstable until that diagnostic exists.

**Estimation density.** The training split carries ⟦unverified: 36,013⟧ loan-months but only about ⟦unverified: 307⟧ prepayment events (⟦unverified: 0.008525⟧ × ⟦unverified: 36,013⟧). Against twelve covariates plus roughly four to six spline degrees of freedom, that is on the order of ⟦unverified: 18⟧ events per parameter — above the conventional floor of ten, but not comfortably so. Relatedly, the ⟦unverified: 36,013⟧ rows come from only ⟦unverified: 934⟧ loans ([[art:dca79f2f:run.splits]]), so the observations are repeated measures and are not independent. Metrics computed row-wise, as these appear to be, will understate sampling error; the effective sample for inference is closer to the loan count than the row count. Confidence intervals quoted anywhere off these artifacts should be widened accordingly.

**Rate-cycle coverage.** The training periods run ⟦unverified: 201402⟧ to ⟦unverified: 201912⟧ ([[art:010d5167:plain_llm.profile]]), a stretch in which mortgage rates trended down with no sustained reversal. Training `incentive` spans −⟦unverified: 3.12⟧ to +⟦unverified: 3.17⟧ with mean +⟦unverified: 0.55⟧, so the in-the-money side of the S-curve is populated, but the model has never seen a sustained rising-rate lock-in regime. Extrapolation into one is unsupported by the estimation sample.

## 3. Data integrity and drift

**Missingness.** The training profile reports zero missing values on every column present ([[art:010d5167:plain_llm.profile]]). That is clean on its face.

**Two declared features are absent from the profiled data.** The feature manifest declares `bom_balance_log` and `rate_change_12m` ([[art:61276a96:run.features]]), but neither column appears in the training raw-data profile, which instead lists `loan_id`, `period`, `note_rate`, `orig_ltv`, `credit_score`, `orig_upb_log`, `sato`, `loan_age`, `incentive`, `burnout`, `season_sin`, `season_cos` and `prepaid` ([[art:010d5167:plain_llm.profile]]). Either the two features were derived downstream of the profiling step, or they were declared but not built. I cannot tell which from the artifacts, and the distinction matters: in the second case the model has ten effective covariates, not twelve, and the documentation overstates it. This is recorded as D1.

**Missingness cannot be compared across splits.** Profiles exist only for `train`. The `test`, `out_of_time` and `vintage_holdout` tables ([[art:f0ac9fe8:run.data_test]], [[art:7ddcc721:run.data_out_of_time]], [[art:940d14da:run.data_vintage_holdout]]) were not profiled, so the cross-split missingness test that D1 exists to catch could not be run in either direction.

**Split disjointness is asserted, not demonstrated.** The loan counts are train ⟦unverified: 934,⟧ test ⟦unverified: 400,⟧ `out_of_time` ⟦unverified: 515,⟧ `vintage_holdout` ⟦unverified: 666⟧ ([[art:dca79f2f:run.splits]]). Note that train and test loans sum to exactly ⟦unverified: 1,334,⟧ which is precisely the maximum `loan_id` in the training data ([[art:010d5167:plain_llm.profile]]) — consistent with a clean loan-level partition of a ⟦unverified: 1,334⟧-loan universe. But the vintage holdout then contributes a further ⟦unverified: 666⟧ loans, which cannot fit inside that same universe without overlap. Either the loan universe is larger than ⟦unverified: 1,334⟧ (entirely possible, since a vintage-based holdout would draw higher IDs that never appear in train), or the vintage holdout shares loans with the training split. The `rows_hash` values differ across all four splits, which establishes that the row sets differ but says nothing about loan-level overlap. I am not asserting contamination; I am recording that the evidence needed to rule it out was not produced. Given that `vintage_holdout` is the split on which the model performs worst, its independence is exactly the thing most worth proving.

**Drift.** No PSI was computed for any feature or for the score, on any split. The one drift signal available is in the outcome itself: the `out_of_time` event rate of ⟦unverified: 0.017949⟧ is ⟦unverified: 2.11⟧× the training rate of ⟦unverified: 0.008525⟧ ([[art:dca79f2f:run.splits]]), an annualised CPR of ⟦unverified: 19.5%⟧ against ⟦unverified: 9.8%⟧. Given that training ends in December ⟦unverified: 2019,⟧ this is consistent with the model being pushed into a refinance wave. A regime shift of that magnitude in the target ordinarily comes with substantial shift in `incentive` and `rate_change_12m`, and none of it has been measured. Recorded as S1.

## 4. Outcomes analysis

| Split | n | loans | events (approx.) | AUC | KS | slope | CPR act. | CPR pred. | error |
|---|---|---|---|---|---|---|---|---|---|
| train | ⟦unverified: 36,013⟧ | ⟦unverified: 934⟧ | ⟦unverified: 307⟧ | ⟦unverified: 0.7883⟧ | ⟦unverified: 0.456⟧ | ⟦unverified: 0.994⟧ | ⟦unverified: 9.76%⟧ | ⟦unverified: 9.66%⟧ | −⟦unverified: 1.1%⟧ |
| test | ⟦unverified: 15,382⟧ | ⟦unverified: 400⟧ | ⟦unverified: 124⟧ | ⟦unverified: 0.7753⟧ | ⟦unverified: 0.416⟧ | ⟦unverified: 0.937⟧ | ⟦unverified: 9.26%⟧ | ⟦unverified: 9.32%⟧ | +⟦unverified: 0.6%⟧ |
| out_of_time | ⟦unverified: 12,257⟧ | ⟦unverified: 515⟧ | ⟦unverified: 220⟧ | ⟦unverified: 0.7846⟧ | ⟦unverified: 0.432⟧ | ⟦unverified: 0.997⟧ | ⟦unverified: 19.53%⟧ | ⟦unverified: 20.43%⟧ | +⟦unverified: 4.6%⟧ |
| vintage_holdout | ⟦unverified: 32,177⟧ | ⟦unverified: 666⟧ | ⟦unverified: 155⟧ | ⟦unverified: 0.7718⟧ | ⟦unverified: 0.452⟧ | ⟦unverified: 0.837⟧ | ⟦unverified: 5.63%⟧ | ⟦unverified: 6.57%⟧ | **+⟦unverified: 16.7%⟧** |

**Discrimination is stable and there is no out-of-sample degradation.** The train-to-test AUC gap is ⟦unverified: 0.013⟧, train-to-vintage ⟦unverified: 0.017⟧, and train-to-out-of-time only ⟦unverified: 0.003⟧. With roughly ⟦unverified: 124⟧ events in the test split, the standard error on its AUC is on the order of ⟦unverified: 0.03⟧, so none of these gaps is distinguishable from sampling noise. KS tracks AUC consistently across all four splits. I record no O1 defect. That the model holds ⟦unverified: 0.785⟧ AUC through a regime in which the event rate doubled is a genuine strength and should be stated as such: the rate-response covariates are doing real work, not merely fitting the training period's level.

**Calibration in the training period and out of time is good.** Slopes of ⟦unverified: 0.994⟧ and ⟦unverified: 0.997⟧, with mean predicted within ⟦unverified: 1%⟧ and ⟦unverified: 5%⟧ of observed respectively. The out-of-time result is the more impressive of the two — the model absorbed a doubling of the prepayment rate and still landed within ⟦unverified: 90⟧ basis points of CPR (⟦unverified: 20.4%⟧ predicted against ⟦unverified: 19.5%⟧ actual), with the modest error in the conservative direction for an MSR holder only in the sense of being pessimistic on value.

**Calibration on the vintage holdout fails.** The slope is ⟦unverified: 0.837⟧, outside any conventional [⟦unverified: 0.90⟧, ⟦unverified: 1.10⟧] acceptance band and the worst of the four splits by a wide margin. More consequentially, the level is biased: mean predicted ⟦unverified: 0.005647⟧ against an observed event rate of ⟦unverified: 0.004817⟧, a ⟦unverified: 17.2%⟧ relative over-prediction of the monthly hazard, which annualises to ⟦unverified: 6.57%⟧ predicted CPR against ⟦unverified: 5.63%⟧ actual. For a prepayment model whose output feeds MSR valuation, a systematic ⟦unverified: 17%⟧ overstatement of CPR on a whole vintage cohort translates more or less directly into a systematic understatement of asset value on that cohort. This is the report's principal finding.

The pattern across splits is informative about cause. Error is small where the observed prepayment rate is near the training level (test, +⟦unverified: 0.6%⟧), moderate where it is far above (out-of-time, +⟦unverified: 4.6%⟧), and large where it is far below (vintage holdout, +⟦unverified: 16.7%⟧). The vintage holdout is also the most seasoned population — ⟦unverified: 32,177⟧ rows over ⟦unverified: 666⟧ loans, ⟦unverified: 48⟧ months per loan, against ⟦unverified: 39⟧ for train — and these are loans that persisted without prepaying. The model's baseline hazard peaks at age ⟦unverified: 43⟧ and decays only gently thereafter ([[art:b764932a:run.model_summary#baseline_hazard]]). A slow-burning, seasoned, low-propensity cohort is precisely where too shallow a post-peak decay, or too weak a burnout effect, would show up as over-prediction. The slope below 1.0 says the same thing from the other side: the model's high scores are too high. I regard under-modelled burnout and an over-flat post-peak hazard as the leading hypothesis, and it is directly testable once the coefficient vector is disclosed.

The test slope of ⟦unverified: 0.937⟧ is within band but sits toward its lower edge and points the same way. I treat it as corroborating rather than as a separate defect.

**No challenger.** The artifact store contains exactly one model. There is no benchmark — not a logistic regression on the same design matrix, not a gradient-boosted alternative, not an industry S-curve — against which the ⟦unverified: 0.775⟧ test AUC can be judged. An AUC of ⟦unverified: 0.775⟧ on monthly prepayment is a plausible-looking number, and that is the problem: without a challenger there is no way to know whether the spline-plus-covariate structure is earning its complexity or whether a simpler specification would match it. Effective challenge is unmet.

## 5. Sensitivity and scenario analysis

This section is where the artifact set is thinnest. A `run.projection` artifact exists ([[art:c07c9271:run.projection]]) but no rate-shock grid, incentive ladder or scenario CPR table was made available, so the two tests that matter most for an MSR model could not be run: whether predicted CPR is monotone increasing in refinance incentive across the S-curve, and whether the ±⟦unverified: 25⟧/⟦unverified: 50⟧/⟦unverified: 100⟧bp rate shocks produce sensible and correctly-signed CPR responses. I cannot report an X1 finding on the S-curve in either direction, and no one should read the absence of such a finding as a pass.

What can be assessed is the hazard curve itself, and it has a defect. The training data contain loan ages from ⟦unverified: 0⟧ to ⟦unverified: 59⟧ months ([[art:010d5167:plain_llm.profile]]), and the final age spline knot sits at ⟦unverified: 53⟧ ([[art:b764932a:run.model_summary#age_spline_knots]]). The published baseline hazard table nonetheless runs past age ⟦unverified: 101⟧ and, on the evidence of the truncation, further still ([[art:b764932a:run.model_summary#baseline_hazard]]). Everything beyond age ⟦unverified: 59⟧ is extrapolation, and everything beyond the last knot at ⟦unverified: 53⟧ is linear extrapolation of the log-hazard into a region with no data at all. The extrapolated segment is not innocuous: between ages ⟦unverified: 43⟧ and ⟦unverified: 101⟧ the tabulated hazard falls about ⟦unverified: 30%⟧, from ⟦unverified: 0.003295⟧ to ⟦unverified: 0.002311⟧, and that decline is a pure artifact of the spline's terminal slope rather than an estimated behaviour.

This matters because MSR valuation requires hazards out to ⟦unverified: 360⟧ months. More than ⟦unverified: 80%⟧ of the horizon over which this model will be used to discount cash flows lies outside the range on which it was fit, and the extrapolation runs in the direction of ever-lower prepayment — which raises projected MSR value the further out you go. The model must not be used for full-term projection until the tail is either estimated on seasoned data or replaced with an explicitly documented, conservatively-chosen terminal assumption. Recorded as X1.

I also note the absence of any sensitivity analysis around the collinear rate block described in section 2. Where `note_rate`, `sato`, `incentive` and `rate_change_12m` coexist, the standard demonstration is to re-fit with each in turn dropped and show that fitted CPR is stable even if individual coefficients move. That was not done.

## 6. Findings and recommendations

In priority order:

1. **Vintage holdout calibration (C1, high).** Remediate before valuation use. Diagnose by recalibrating on the seasoned cohort and testing the burnout and post-peak age terms specifically; re-run the slope and CPR-error tests on a refreshed vintage holdout. Do not paper over it with a flat scaling factor — the slope of ⟦unverified: 0.837⟧ says the error is score-dependent, so a level adjustment would fix the mean and leave the ranking miscalibrated.
2. **Hazard extrapolated beyond data support (X1, medium).** Either extend the estimation sample to cover seasoned ages, or truncate the published hazard at age ⟦unverified: 59⟧ and document an explicit terminal assumption for ages beyond it. State the valuation impact of the choice.
3. **No challenger model (E1, medium).** Build at least one, on the same splits, and report the same metric set. This is required for effective challenge and is inexpensive here.
4. **Undocumented drift (S1, medium).** Compute feature-level and score-level PSI for `test`, `out_of_time` and `vintage_holdout` against `train`. The ⟦unverified: 2.1⟧× outcome-rate shift into the out-of-time window makes this non-optional.
5. **Two declared features missing from the profiled data (D1, medium).** Confirm whether `bom_balance_log` and `rate_change_12m` were actually constructed and entered the fit. Reconcile the feature manifest with the data profile either way, and profile all four splits.
6. **No collinearity diagnostics (M1, medium).** Report VIF and the design-matrix condition number for the rate block and the balance pair, with a drop-one-out stability analysis.
7. **Split disjointness not demonstrated (L2, low).** Publish loan-ID intersection counts between all split pairs, particularly train against `vintage_holdout`.
8. **Coefficients not disclosed (R1, info).** Publish the covariate coefficient vector with standard errors so that sign and economic-reasonableness checks can be performed. Discrimination is stable across regimes (AUC ⟦unverified: 0.772⟧–⟦unverified: 0.788⟧), so no regime defect is asserted — but it is untested, not cleared.
9. **No declared acceptance thresholds (T1, info).** No developer-stated performance thresholds, calibration bands or runtime claims accompany the run, so no declared threshold could be tested for breach.

Overall assessment: **approved for use only after the calibration and extrapolation findings are remediated.** The core specification is sound and the discrimination evidence is credible and regime-robust; the defects are in level accuracy on a seasoned cohort, in the unsupported tail, and in the diagnostic record rather than in the modelling approach itself.

### F-001 · C1 calibration · severity **high**

On the vintage_holdout split the calibration slope is 0.8373, outside any conventional [0.90, 1.10] acceptance band and by far the worst of the four splits (train 0.9937, test 0.9365, out_of_time 0.9969). The level is biased in the same direction: mean predicted hazard 0.005647 against an observed event rate 0.004817, a 17.2% relative over-prediction, which annualises to 6.57% predicted CPR against 5.63% actual. For a model feeding MSR valuation, a systematic 17% overstatement of CPR on a whole vintage cohort maps close to directly onto a systematic understatement of asset value on that cohort. The error pattern across splits points to a cause: the bias is near zero where the observed rate is near the training level (test, +0.6%), moderate where it is well above (out_of_time, +4.6%), and large where it is well below (vintage_holdout, +16.7%). The vintage holdout is also the most seasoned population, at 48 loan-months per loan against 39 for train, and consists of loans that persisted without prepaying. Since the baseline hazard peaks at age 43 and decays only gently after, a post-peak ramp that is too flat, or a burnout effect that is too weak, would produce exactly this signature; the sub-1.0 slope says the same thing from the other side, that the model's high scores are too high. A flat scaling correction is not an adequate remedy because the slope shows the error is score-dependent, not merely a level offset.

### F-002 · X1 scenario analysis · severity **medium**

Training loan_age spans 0 to 59 months and the final age spline knot sits at 53, but the tabulated baseline hazard runs past age 101 and, judging by the truncation of the summary, further still. Everything beyond age 59 is extrapolation and everything beyond the last knot at 53 is linear extrapolation of the log-hazard into a region containing no data. The extrapolated segment is not neutral: the tabulated hazard falls roughly 30% between ages 43 and 101, from 0.003295 to 0.002311, and that decline is an artifact of the spline's terminal slope rather than an estimated behaviour. This matters because MSR valuation requires hazards out to 360 months, so more than 80% of the horizon over which the curve will be used lies outside its support, and the extrapolation runs toward ever-lower prepayment, which inflates projected MSR value the further out it is taken. Separately, no rate-shock grid or incentive ladder was supplied with the projection artifact, so the monotonicity and sign of the S-curve response to refinance incentive could not be tested at all; the absence of an S-curve finding here should not be read as a pass.

### F-003 · E1 effective challenge · severity **medium**

The artifact store contains a single model. No benchmark of any kind accompanies it: not a plain logistic regression on the same design matrix, not a gradient-boosted alternative, not an industry S-curve. The reported test AUC of 0.7753 is plausible for a monthly prepayment hazard, and that is precisely the difficulty: with nothing to compare against, there is no basis for judging whether the age spline plus twelve covariates is earning its complexity, or whether a materially simpler specification would reach the same discrimination and perhaps better calibration on the seasoned cohort. Effective challenge requires at least one competing model run on the identical splits and reported on the identical metric set. This is inexpensive to remedy here, since the splits and the feature pipeline already exist.

### F-004 · S1 population drift · severity **medium**

No population stability index was reported for any feature or for the model score, on any split, against the training distribution. The one drift signal that can be read from the artifacts is in the outcome itself: the out_of_time event rate of 0.017949 is 2.11 times the training rate of 0.008525, equivalent to 19.5% annualised CPR against 9.8%. Given that the training periods end at 201912, this is consistent with the model being pushed into a refinance wave. A shift of that size in the target is normally accompanied by substantial movement in the refinance incentive and twelve-month rate-change distributions, and none of it has been measured. To the model's credit, discrimination and calibration held through the shift (AUC 0.7846, slope 0.9969), which suggests the rate-response covariates are absorbing the regime rather than the model merely fitting a level; but that is an inference from the outcome metrics, not a substitute for the feature-level drift measurement, which is what would give early warning before performance degrades.

### F-005 · D1 data integrity · severity **medium**

The feature manifest declares twelve features including bom_balance_log and rate_change_12m, both timed before_period_start. Neither column appears in the raw data profile of the training split, which lists loan_id, period, note_rate, orig_ltv, credit_score, orig_upb_log, sato, loan_age, incentive, burnout, season_sin, season_cos and prepaid. Either the two features were derived downstream of the profiling step, or they were declared but never constructed. The artifacts do not distinguish these, and the distinction is material: under the second reading the fitted model has ten effective covariates rather than twelve and the documentation overstates its content. Compounding this, profiles exist only for the training split, so the cross-split missingness comparison that this defect class exists to detect could not be performed in either direction for test, out_of_time or vintage_holdout. Within the columns that were profiled, missingness is zero throughout, which is clean as far as it goes.

### F-006 · M1 collinearity · severity **medium**

No VIF, condition number or drop-one-out stability analysis was reported. Four of the twelve covariates are related by construction: sato is a rate spread measured at origination, incentive is a rate spread measured at the observation date, rate_change_12m is the change in the market rate that drives incentive, and note_rate is a common term inside the first two. Separately, orig_upb_log and bom_balance_log are the same quantity measured at two points in the loan's life and will be strongly correlated in a book this lightly seasoned, where mean loan age is 22 months. With roughly 307 training events supporting twelve covariates plus four to six spline degrees of freedom, near-collinearity in this block will make individual rate coefficients unstable in sign and magnitude even where fitted CPR is well behaved. Until the diagnostic exists, no economic interpretation should be placed on any single rate coefficient, and the standard drop-one-out demonstration that fitted CPR is stable has not been provided.

### F-007 · L2 contamination · severity **low**

The splits report 934, 400, 515 and 666 loans for train, test, out_of_time and vintage_holdout. Train and test loan counts sum to exactly 1,334, which is precisely the maximum loan_id observed in the training data, a pattern consistent with a clean loan-level partition of a 1,334-loan universe. The vintage holdout then contributes a further 666 loans, which cannot fit within that same universe without overlap. The benign explanation is that the loan universe exceeds 1,334 because a vintage-based holdout draws later-originated, higher-numbered loans that never appear in train, and the training loan_id mean of 560.6 against a uniform-draw expectation of 667.5 is consistent with the training loans sitting at the lower end of a larger ID range. The rows_hash values differ across all four splits, which establishes that the row sets differ but is silent on loan-level overlap. I am not asserting contamination; I am recording that the evidence needed to exclude it was not produced, and noting that vintage_holdout is both the split whose independence is least demonstrated and the split on which the model performs worst, which is the combination most worth resolving. Publishing pairwise loan-ID intersection counts would close this immediately.

### F-008 · R1 regime stability · severity **info**

Discrimination is stable across all four splits, with AUC ranging only from 0.7718 to 0.7883 and KS from 0.416 to 0.456; the widest AUC gap, 0.0166 between train and vintage_holdout, is well inside sampling error given roughly 124 to 307 events per split. On that evidence no regime defect is asserted. However, the model summary supplied contains only the age spline knots and the baseline hazard table, with no covariate coefficient vector and no standard errors. The most elementary economic checks on a prepayment model therefore could not be performed at all, in any regime: that incentive enters positively, that burnout enters negatively, that credit_score enters positively and orig_ltv negatively, and that none of these flips sign between the training and out-of-time regimes. This is recorded as untested rather than cleared, and it also blocks the diagnostic work needed to explain the vintage holdout calibration failure.

### F-009 · O1 out-of-sample degradation · severity **info**

Out-of-sample discrimination holds up. The train-to-test AUC gap is 0.0131 (0.7883 to 0.7753), train-to-vintage_holdout 0.0166, and train-to-out_of_time only 0.0032. KS moves consistently with AUC and never falls below 0.416. No O1 defect is recorded. Two caveats belong on the record rather than against the model. First, the test split carries roughly 124 events (0.008061 x 15,382), so the standard error on its AUC is of order 0.03 and none of the observed gaps is statistically distinguishable from noise in either direction; the analysis has limited power to detect a genuine gap below about 0.05. Second, the 36,013 training rows come from only 934 loans, so observations are repeated measures on the same borrowers and row-wise metrics will understate sampling error, with the effective sample for inference closer to the loan count than the row count. Any confidence interval derived from these artifacts should be widened accordingly.

### F-010 · T1 declared threshold · severity **info**

The artifact set contains no model documentation stating acceptance criteria: no minimum AUC, no calibration slope band, no maximum tolerated CPR error, and no stated performance claim of any kind. No declared threshold could therefore be tested for breach, and the bands applied in this report are the reviewer's conventional ones rather than the developer's. Runtime artifacts exist for both the observed duration and the cap, but their values are not exposed in what was provided, so the runtime cap likewise could not be checked; the run status artifact is present and nothing in the metric set indicates a failed or truncated run. Before the next validation cycle the developer should publish explicit acceptance criteria so that subsequent reviews test the model against its own stated standard.

Candidates raised and not promoted: none.

### Open items

No open item was recorded for this validation.

## 7. Ongoing monitoring recommendations

- **Monthly actual-versus-predicted CPR**, reported in aggregate and cut by vintage, age bucket and incentive bucket. Amber at ⟦unverified: 10%⟧ relative error on any material bucket, red at ⟦unverified: 20%⟧. The vintage holdout defect would have tripped the red threshold, so this cut is the one that earns its keep.
- **Quarterly calibration slope** on a rolling twelve-month window, with an action trigger outside [⟦unverified: 0.90⟧, ⟦unverified: 1.10⟧]. Track it by age bucket, not only in aggregate, since the aggregate slope on this model is fine on three splits out of four.
- **Quarterly discrimination**: AUC and KS on the rolling window, with a trigger at a ⟦unverified: 0.05⟧ absolute drop from the ⟦unverified: 0.775⟧ test benchmark. Given roughly ⟦unverified: 120⟧–⟦unverified: 300⟧ events per window, do not act on smaller moves; they are noise.
- **Monthly PSI** on `incentive`, `rate_change_12m`, `loan_age`, `credit_score` and the model score, with the usual ⟦unverified: 0.10⟧ watch / ⟦unverified: 0.25⟧ action thresholds. This model has only ever seen a falling-rate regime, so the `incentive` and `rate_change_12m` distributions are the early-warning instruments.
- **Age-support monitor.** Report the share of the scored book with loan age above ⟦unverified: 59⟧ months, the boundary of the estimation sample. Escalate for re-estimation when that share exceeds a documented tolerance; it will rise mechanically as the book seasons.
- **Feature-availability check** each scoring cycle, asserting that all declared features are present and non-null in the scoring frame. The `bom_balance_log` / `rate_change_12m` discrepancy is exactly the kind of drift between manifest and pipeline that this catches.
- **Annual challenger re-run and full revalidation**, with earlier revalidation triggered by any sustained rate-regime reversal, since the training window contains no such episode.

## Appendix A — Claims

Grounding precision 0.0000 before repair (0 of 140 claims verified; 109 unsupported, 29 dangling, 2 unattributed) and 0.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 0/5; conceptual_soundness 0/20; data_integrity 0/14; outcomes 0/69; sensitivity 0/16; findings 0/5; monitoring 0/11.

Developer claims: `plain_llm` runs no check over `package.yaml`'s declared claims See Appendix D.

Excluded numeric tokens (not claims): section_number (section 2, 1., 2., 3.); inline_code (`2·AUC − 1`, `1 − (1 − 0.008061)^12 = 0.09256`); citation_hash (b764932a, 61276a96, dca79f2f, 31ce3d08); package_version (1.0); extractor_returned_excluded_token (2, 1, 0.008061, 12).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The subject is a discrete-time hazard model of voluntary pre… | 1 | months | age_spline_knots |  | eq | `[[art:b764932a:run.model_summary#age_spline_knots]]` | dangling |  |
| 2 | summary | The subject is a discrete-time hazard model of voluntary pre… | 10 | months | age_spline_knots |  | eq | `[[art:b764932a:run.model_summary#age_spline_knots]]` | dangling |  |
| 3 | summary | The subject is a discrete-time hazard model of voluntary pre… | 19 | months | age_spline_knots |  | eq | `[[art:b764932a:run.model_summary#age_spline_knots]]` | dangling |  |
| 4 | summary | The subject is a discrete-time hazard model of voluntary pre… | 31 | months | age_spline_knots |  | eq | `[[art:b764932a:run.model_summary#age_spline_knots]]` | dangling |  |
| 5 | summary | The subject is a discrete-time hazard model of voluntary pre… | 53 | months | age_spline_knots |  | eq | `[[art:b764932a:run.model_summary#age_spline_knots]]` | dangling |  |
| 6 | conceptual_soundness | **Leakage by construction.** The timing declarations are cle… | 0.9 | ratio | auc |  | eq |  | unsupported |  |
| 7 | conceptual_soundness | **Baseline hazard shape.** The tabulated baseline () rises m… | 0.000885 | ratio | baseline_hazard |  | eq | `[[art:b764932a:run.model_summary#baseline_hazard]]` | dangling |  |
| 8 | conceptual_soundness | **Baseline hazard shape.** The tabulated baseline () rises m… | 0 | months |  |  | eq | `[[art:b764932a:run.model_summary#baseline_hazard]]` | dangling |  |
| 9 | conceptual_soundness | **Baseline hazard shape.** The tabulated baseline () rises m… | 0.003295 | ratio | baseline_hazard |  | eq | `[[art:b764932a:run.model_summary#baseline_hazard]]` | dangling |  |
| 10 | conceptual_soundness | **Baseline hazard shape.** The tabulated baseline () rises m… | 43 | months |  |  | eq | `[[art:b764932a:run.model_summary#baseline_hazard]]` | dangling |  |
| 11 | conceptual_soundness | **Baseline hazard shape.** The tabulated baseline () rises m… | 1.1 | percent | cpr |  | eq |  | unsupported |  |
| 12 | conceptual_soundness | **Baseline hazard shape.** The tabulated baseline () rises m… | 3.9 | percent | cpr |  | eq |  | unsupported |  |
| 13 | conceptual_soundness | **Correlated regressors.** Four of the twelve covariates are… | 0.9 | ratio | correlation |  | eq |  | unsupported |  |
| 14 | conceptual_soundness | **Estimation density.** The training split carries 36,013 lo… | 36013 | count | n_rows | train | eq |  | unsupported |  |
| 15 | conceptual_soundness | **Estimation density.** The training split carries 36,013 lo… | 307 | count |  | train | eq |  | unsupported |  |
| 16 | conceptual_soundness | **Estimation density.** The training split carries 36,013 lo… | 0.008525 | ratio | event_rate | train | eq |  | unsupported |  |
| 17 | conceptual_soundness | **Estimation density.** The training split carries 36,013 lo… | 36013 | count | n_rows | train | eq |  | unsupported |  |
| 18 | conceptual_soundness | **Estimation density.** The training split carries 36,013 lo… | 18 | ratio |  |  | eq |  | unsupported |  |
| 19 | conceptual_soundness | **Estimation density.** The training split carries 36,013 lo… | 36013 | count | n_rows | train | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 20 | conceptual_soundness | **Estimation density.** The training split carries 36,013 lo… | 934 | count | n_loans | train | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 21 | conceptual_soundness | **Rate-cycle coverage.** The training periods run 201402 to… | 201402 | ratio |  | train | eq | `[[art:010d5167:plain_llm.profile]]` | dangling |  |
| 22 | conceptual_soundness | **Rate-cycle coverage.** The training periods run 201402 to… | 201912 | ratio |  | train | eq | `[[art:010d5167:plain_llm.profile]]` | dangling |  |
| 23 | conceptual_soundness | **Rate-cycle coverage.** The training periods run 201402 to… | 3.12 | ratio |  |  | eq |  | unattributed |  |
| 24 | conceptual_soundness | **Rate-cycle coverage.** The training periods run 201402 to… | 3.17 | ratio | incentive | train | eq |  | unsupported |  |
| 25 | conceptual_soundness | **Rate-cycle coverage.** The training periods run 201402 to… | 0.55 | ratio | incentive | train | eq |  | unsupported |  |
| 26 | data_integrity | **Split disjointness is asserted, not demonstrated.** The lo… | 934 | count | n_loans | train | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 27 | data_integrity | **Split disjointness is asserted, not demonstrated.** The lo… | 400 | count | n_loans | test | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 28 | data_integrity | **Split disjointness is asserted, not demonstrated.** The lo… | 515 | count | n_loans | out_of_time | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 29 | data_integrity | **Split disjointness is asserted, not demonstrated.** The lo… | 666 | count | n_loans | vintage_holdout | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 30 | data_integrity | **Split disjointness is asserted, not demonstrated.** The lo… | 1334 | count | loan_id_max | train | eq | `[[art:010d5167:plain_llm.profile]]` | dangling |  |
| 31 | data_integrity | **Split disjointness is asserted, not demonstrated.** The lo… | 1334 | count |  |  | eq | `[[art:010d5167:plain_llm.profile]]` | dangling |  |
| 32 | data_integrity | **Split disjointness is asserted, not demonstrated.** The lo… | 666 | count | n_loans | vintage_holdout | eq |  | unsupported |  |
| 33 | data_integrity | **Split disjointness is asserted, not demonstrated.** The lo… | 1334 | count |  |  | eq |  | unsupported |  |
| 34 | data_integrity | **Drift.** No PSI was computed for any feature or for the sc… | 0.017949 | ratio | event_rate | out_of_time | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 35 | data_integrity | **Drift.** No PSI was computed for any feature or for the sc… | 2.11 | ratio | event_rate |  | ratio | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 36 | data_integrity | **Drift.** No PSI was computed for any feature or for the sc… | 0.008525 | ratio | event_rate | train | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 37 | data_integrity | **Drift.** No PSI was computed for any feature or for the sc… | 19.5 | percent | cpr | out_of_time | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 38 | data_integrity | **Drift.** No PSI was computed for any feature or for the sc… | 9.8 | percent | cpr | train | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 39 | data_integrity | **Drift.** No PSI was computed for any feature or for the sc… | 2019 | ratio |  | train | eq |  | unsupported |  |
| 40 | outcomes | \| train \| 36,013 \| 934 \| 307 \| 0.7883 \| 0.456 \| 0.994 \| 9.76… | 36013 | count | n_rows | train | eq |  | unsupported |  |
| 41 | outcomes | \| train \| 36,013 \| 934 \| 307 \| 0.7883 \| 0.456 \| 0.994 \| 9.76… | 934 | count | n_loans | train | eq |  | unsupported |  |
| 42 | outcomes | \| train \| 36,013 \| 934 \| 307 \| 0.7883 \| 0.456 \| 0.994 \| 9.76… | 307 | count | n_events | train | eq |  | unsupported |  |
| 43 | outcomes | \| train \| 36,013 \| 934 \| 307 \| 0.7883 \| 0.456 \| 0.994 \| 9.76… | 0.7883 | ratio | auc | train | eq |  | unsupported |  |
| 44 | outcomes | \| train \| 36,013 \| 934 \| 307 \| 0.7883 \| 0.456 \| 0.994 \| 9.76… | 0.456 | ratio | ks | train | eq |  | unsupported |  |
| 45 | outcomes | \| train \| 36,013 \| 934 \| 307 \| 0.7883 \| 0.456 \| 0.994 \| 9.76… | 0.994 | ratio | calibration_slope | train | eq |  | unsupported |  |
| 46 | outcomes | \| train \| 36,013 \| 934 \| 307 \| 0.7883 \| 0.456 \| 0.994 \| 9.76… | 9.76 | percent | cpr_actual | train | eq |  | unsupported |  |
| 47 | outcomes | \| train \| 36,013 \| 934 \| 307 \| 0.7883 \| 0.456 \| 0.994 \| 9.76… | 9.66 | percent | cpr_predicted | train | eq |  | unsupported |  |
| 48 | outcomes | \| train \| 36,013 \| 934 \| 307 \| 0.7883 \| 0.456 \| 0.994 \| 9.76… | 1.1 | percent |  |  | eq |  | unattributed |  |
| 49 | outcomes | \| test \| 15,382 \| 400 \| 124 \| 0.7753 \| 0.416 \| 0.937 \| 9.26%… | 15382 | count | n_rows | test | eq |  | unsupported |  |
| 50 | outcomes | \| test \| 15,382 \| 400 \| 124 \| 0.7753 \| 0.416 \| 0.937 \| 9.26%… | 400 | count | n_loans | test | eq |  | unsupported |  |
| 51 | outcomes | \| test \| 15,382 \| 400 \| 124 \| 0.7753 \| 0.416 \| 0.937 \| 9.26%… | 124 | count | n_events | test | eq |  | unsupported |  |
| 52 | outcomes | \| test \| 15,382 \| 400 \| 124 \| 0.7753 \| 0.416 \| 0.937 \| 9.26%… | 0.7753 | ratio | auc | test | eq |  | unsupported |  |
| 53 | outcomes | \| test \| 15,382 \| 400 \| 124 \| 0.7753 \| 0.416 \| 0.937 \| 9.26%… | 0.416 | ratio | ks | test | eq |  | unsupported |  |
| 54 | outcomes | \| test \| 15,382 \| 400 \| 124 \| 0.7753 \| 0.416 \| 0.937 \| 9.26%… | 0.937 | ratio | calibration_slope | test | eq |  | unsupported |  |
| 55 | outcomes | \| test \| 15,382 \| 400 \| 124 \| 0.7753 \| 0.416 \| 0.937 \| 9.26%… | 9.26 | percent | cpr_actual | test | eq |  | unsupported |  |
| 56 | outcomes | \| test \| 15,382 \| 400 \| 124 \| 0.7753 \| 0.416 \| 0.937 \| 9.26%… | 9.32 | percent | cpr_predicted | test | eq |  | unsupported |  |
| 57 | outcomes | \| test \| 15,382 \| 400 \| 124 \| 0.7753 \| 0.416 \| 0.937 \| 9.26%… | 0.6 | percent | cpr_error | test | eq |  | unsupported |  |
| 58 | outcomes | \| out_of_time \| 12,257 \| 515 \| 220 \| 0.7846 \| 0.432 \| 0.997… | 12257 | count | n_rows | out_of_time | eq |  | unsupported |  |
| 59 | outcomes | \| out_of_time \| 12,257 \| 515 \| 220 \| 0.7846 \| 0.432 \| 0.997… | 515 | count | n_loans | out_of_time | eq |  | unsupported |  |
| 60 | outcomes | \| out_of_time \| 12,257 \| 515 \| 220 \| 0.7846 \| 0.432 \| 0.997… | 220 | count | n_events | out_of_time | eq |  | unsupported |  |
| 61 | outcomes | \| out_of_time \| 12,257 \| 515 \| 220 \| 0.7846 \| 0.432 \| 0.997… | 0.7846 | ratio | auc | out_of_time | eq |  | unsupported |  |
| 62 | outcomes | \| out_of_time \| 12,257 \| 515 \| 220 \| 0.7846 \| 0.432 \| 0.997… | 0.432 | ratio | ks | out_of_time | eq |  | unsupported |  |
| 63 | outcomes | \| out_of_time \| 12,257 \| 515 \| 220 \| 0.7846 \| 0.432 \| 0.997… | 0.997 | ratio | calibration_slope | out_of_time | eq |  | unsupported |  |
| 64 | outcomes | \| out_of_time \| 12,257 \| 515 \| 220 \| 0.7846 \| 0.432 \| 0.997… | 19.53 | percent | cpr_actual | out_of_time | eq |  | unsupported |  |
| 65 | outcomes | \| out_of_time \| 12,257 \| 515 \| 220 \| 0.7846 \| 0.432 \| 0.997… | 20.43 | percent | cpr_predicted | out_of_time | eq |  | unsupported |  |
| 66 | outcomes | \| out_of_time \| 12,257 \| 515 \| 220 \| 0.7846 \| 0.432 \| 0.997… | 4.6 | percent | cpr_error | out_of_time | eq |  | unsupported |  |
| 67 | outcomes | \| vintage_holdout \| 32,177 \| 666 \| 155 \| 0.7718 \| 0.452 \| 0.… | 32177 | count | n_rows | vintage_holdout | eq |  | unsupported |  |
| 68 | outcomes | \| vintage_holdout \| 32,177 \| 666 \| 155 \| 0.7718 \| 0.452 \| 0.… | 666 | count | n_loans | vintage_holdout | eq |  | unsupported |  |
| 69 | outcomes | \| vintage_holdout \| 32,177 \| 666 \| 155 \| 0.7718 \| 0.452 \| 0.… | 155 | count | n_events | vintage_holdout | eq |  | unsupported |  |
| 70 | outcomes | \| vintage_holdout \| 32,177 \| 666 \| 155 \| 0.7718 \| 0.452 \| 0.… | 0.7718 | ratio | auc | vintage_holdout | eq |  | unsupported |  |
| 71 | outcomes | \| vintage_holdout \| 32,177 \| 666 \| 155 \| 0.7718 \| 0.452 \| 0.… | 0.452 | ratio | ks | vintage_holdout | eq |  | unsupported |  |
| 72 | outcomes | \| vintage_holdout \| 32,177 \| 666 \| 155 \| 0.7718 \| 0.452 \| 0.… | 0.837 | ratio | calibration_slope | vintage_holdout | eq |  | unsupported |  |
| 73 | outcomes | \| vintage_holdout \| 32,177 \| 666 \| 155 \| 0.7718 \| 0.452 \| 0.… | 5.63 | percent | cpr_actual | vintage_holdout | eq |  | unsupported |  |
| 74 | outcomes | \| vintage_holdout \| 32,177 \| 666 \| 155 \| 0.7718 \| 0.452 \| 0.… | 6.57 | percent | cpr_predicted | vintage_holdout | eq |  | unsupported |  |
| 75 | outcomes | \| vintage_holdout \| 32,177 \| 666 \| 155 \| 0.7718 \| 0.452 \| 0.… | 16.7 | percent | cpr_error | vintage_holdout | eq |  | unsupported |  |
| 76 | outcomes | **Discrimination is stable and there is no out-of-sample deg… | 0.013 | ratio | delta_auc | test | delta |  | unsupported |  |
| 77 | outcomes | **Discrimination is stable and there is no out-of-sample deg… | 0.017 | ratio | delta_auc | vintage_holdout | delta |  | unsupported |  |
| 78 | outcomes | **Discrimination is stable and there is no out-of-sample deg… | 0.003 | ratio | delta_auc | out_of_time | delta |  | unsupported |  |
| 79 | outcomes | **Discrimination is stable and there is no out-of-sample deg… | 124 | count | n_events | test | eq |  | unsupported |  |
| 80 | outcomes | **Discrimination is stable and there is no out-of-sample deg… | 0.03 | ratio | auc | test | eq |  | unsupported |  |
| 81 | outcomes | **Discrimination is stable and there is no out-of-sample deg… | 0.785 | ratio | auc | out_of_time | eq |  | unsupported |  |
| 82 | outcomes | **Calibration in the training period and out of time is good… | 0.994 | ratio | calibration_slope | train | eq |  | unsupported |  |
| 83 | outcomes | **Calibration in the training period and out of time is good… | 0.997 | ratio | calibration_slope | out_of_time | eq |  | unsupported |  |
| 84 | outcomes | **Calibration in the training period and out of time is good… | 1 | percent | cpr_error | train | eq |  | unsupported |  |
| 85 | outcomes | **Calibration in the training period and out of time is good… | 5 | percent | cpr_error | out_of_time | eq |  | unsupported |  |
| 86 | outcomes | **Calibration in the training period and out of time is good… | 90 | bp | cpr_error | out_of_time | eq |  | unsupported |  |
| 87 | outcomes | **Calibration in the training period and out of time is good… | 20.4 | percent | cpr_predicted | out_of_time | eq |  | unsupported |  |
| 88 | outcomes | **Calibration in the training period and out of time is good… | 19.5 | percent | cpr_actual | out_of_time | eq |  | unsupported |  |
| 89 | outcomes | **Calibration on the vintage holdout fails.** The slope is 0… | 0.837 | ratio | calibration_slope | vintage_holdout | eq |  | unsupported |  |
| 90 | outcomes | **Calibration on the vintage holdout fails.** The slope is 0… | 0.9 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 91 | outcomes | **Calibration on the vintage holdout fails.** The slope is 0… | 1.1 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 92 | outcomes | **Calibration on the vintage holdout fails.** The slope is 0… | 0.005647 | ratio | mean_predicted | vintage_holdout | eq |  | unsupported |  |
| 93 | outcomes | **Calibration on the vintage holdout fails.** The slope is 0… | 0.004817 | ratio | event_rate | vintage_holdout | eq |  | unsupported |  |
| 94 | outcomes | **Calibration on the vintage holdout fails.** The slope is 0… | 17.2 | percent | relative_error | vintage_holdout | eq |  | unsupported |  |
| 95 | outcomes | **Calibration on the vintage holdout fails.** The slope is 0… | 6.57 | percent | cpr_predicted | vintage_holdout | eq |  | unsupported |  |
| 96 | outcomes | **Calibration on the vintage holdout fails.** The slope is 0… | 5.63 | percent | cpr_actual | vintage_holdout | eq |  | unsupported |  |
| 97 | outcomes | **Calibration on the vintage holdout fails.** The slope is 0… | 17 | percent | relative_error | vintage_holdout | eq |  | unsupported |  |
| 98 | outcomes | The pattern across splits is informative about cause. Error… | 0.6 | percent | cpr_error | test | eq |  | unsupported |  |
| 99 | outcomes | The pattern across splits is informative about cause. Error… | 4.6 | percent | cpr_error | out_of_time | eq |  | unsupported |  |
| 100 | outcomes | The pattern across splits is informative about cause. Error… | 16.7 | percent | cpr_error | vintage_holdout | eq |  | unsupported |  |
| 101 | outcomes | The pattern across splits is informative about cause. Error… | 32177 | count | n_rows | vintage_holdout | eq |  | unsupported |  |
| 102 | outcomes | The pattern across splits is informative about cause. Error… | 666 | count | n_loans | vintage_holdout | eq |  | unsupported |  |
| 103 | outcomes | The pattern across splits is informative about cause. Error… | 48 | months | months_per_loan | vintage_holdout | eq |  | unsupported |  |
| 104 | outcomes | The pattern across splits is informative about cause. Error… | 39 | months | months_per_loan | train | eq |  | unsupported |  |
| 105 | outcomes | The pattern across splits is informative about cause. Error… | 43 | months | baseline_hazard |  | eq | `[[art:b764932a:run.model_summary#baseline_hazard]]` | dangling |  |
| 106 | outcomes | The test slope of 0.937 is within band but sits toward its l… | 0.937 | ratio | calibration_slope | test | eq |  | unsupported |  |
| 107 | outcomes | **No challenger.** The artifact store contains exactly one m… | 0.775 | ratio | auc | test | eq |  | unsupported |  |
| 108 | outcomes | **No challenger.** The artifact store contains exactly one m… | 0.775 | ratio | auc | test | eq |  | unsupported |  |
| 109 | sensitivity | This section is where the artifact set is thinnest. A `run.p… | 25 | bp |  |  | eq |  | unsupported |  |
| 110 | sensitivity | This section is where the artifact set is thinnest. A `run.p… | 50 | bp |  |  | eq |  | unsupported |  |
| 111 | sensitivity | This section is where the artifact set is thinnest. A `run.p… | 100 | bp |  |  | eq |  | unsupported |  |
| 112 | sensitivity | What can be assessed is the hazard curve itself, and it has… | 0 | months | profile | train | eq | `[[art:010d5167:plain_llm.profile]]` | dangling |  |
| 113 | sensitivity | What can be assessed is the hazard curve itself, and it has… | 59 | months | profile | train | eq | `[[art:010d5167:plain_llm.profile]]` | dangling |  |
| 114 | sensitivity | What can be assessed is the hazard curve itself, and it has… | 53 | months | age_spline_knots |  | eq | `[[art:b764932a:run.model_summary#age_spline_knots]]` | dangling |  |
| 115 | sensitivity | What can be assessed is the hazard curve itself, and it has… | 101 | months | baseline_hazard |  | eq | `[[art:b764932a:run.model_summary#baseline_hazard]]` | dangling |  |
| 116 | sensitivity | What can be assessed is the hazard curve itself, and it has… | 59 | months |  |  | eq |  | unsupported |  |
| 117 | sensitivity | What can be assessed is the hazard curve itself, and it has… | 53 | months |  |  | eq |  | unsupported |  |
| 118 | sensitivity | What can be assessed is the hazard curve itself, and it has… | 43 | months |  |  | eq |  | unsupported |  |
| 119 | sensitivity | What can be assessed is the hazard curve itself, and it has… | 101 | months |  |  | eq |  | unsupported |  |
| 120 | sensitivity | What can be assessed is the hazard curve itself, and it has… | 30 | percent |  |  | eq |  | unsupported |  |
| 121 | sensitivity | What can be assessed is the hazard curve itself, and it has… | 0.003295 | ratio |  |  | eq |  | unsupported |  |
| 122 | sensitivity | What can be assessed is the hazard curve itself, and it has… | 0.002311 | ratio |  |  | eq |  | unsupported |  |
| 123 | sensitivity | This matters because MSR valuation requires hazards out to 3… | 360 | months |  |  | eq |  | unsupported |  |
| 124 | sensitivity | This matters because MSR valuation requires hazards out to 3… | 80 | percent |  |  | eq |  | unsupported |  |
| 125 | findings | 1. **Vintage holdout calibration (C1, high).** Remediate bef… | 0.837 | ratio | calibration_slope | vintage_holdout | eq |  | unsupported |  |
| 126 | findings | 2. **Hazard extrapolated beyond data support (X1, medium).**… | 59 | months |  |  | eq |  | unsupported |  |
| 127 | findings | 4. **Undocumented drift (S1, medium).** Compute feature-leve… | 2.1 | ratio | event_rate | out_of_time | eq |  | unsupported |  |
| 128 | findings | 8. **Coefficients not disclosed (R1, info).** Publish the co… | 0.772 | ratio | auc |  | eq |  | unsupported |  |
| 129 | findings | 8. **Coefficients not disclosed (R1, info).** Publish the co… | 0.788 | ratio | auc |  | eq |  | unsupported |  |
| 130 | monitoring | - **Monthly actual-versus-predicted CPR**, reported in aggre… | 10 | percent | cpr |  | eq |  | unsupported |  |
| 131 | monitoring | - **Monthly actual-versus-predicted CPR**, reported in aggre… | 20 | percent | cpr |  | eq |  | unsupported |  |
| 132 | monitoring | - **Quarterly calibration slope** on a rolling twelve-month… | 0.9 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 133 | monitoring | - **Quarterly calibration slope** on a rolling twelve-month… | 1.1 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 134 | monitoring | - **Quarterly discrimination**: AUC and KS on the rolling wi… | 0.05 | ratio | delta_auc |  | eq |  | unsupported |  |
| 135 | monitoring | - **Quarterly discrimination**: AUC and KS on the rolling wi… | 0.775 | ratio | auc | test | eq |  | unsupported |  |
| 136 | monitoring | - **Quarterly discrimination**: AUC and KS on the rolling wi… | 120 | count | events |  | eq |  | unsupported |  |
| 137 | monitoring | - **Quarterly discrimination**: AUC and KS on the rolling wi… | 300 | count | events |  | eq |  | unsupported |  |
| 138 | monitoring | - **Monthly PSI** on `incentive`, `rate_change_12m`, `loan_a… | 0.1 | ratio | psi |  | eq |  | unsupported |  |
| 139 | monitoring | - **Monthly PSI** on `incentive`, `rate_change_12m`, `loan_a… | 0.25 | ratio | psi |  | eq |  | unsupported |  |
| 140 | monitoring | - **Age-support monitor.** Report the share of the scored bo… | 59 | months | loan_age |  | eq |  | unsupported |  |

## Appendix B — Artifact index

The store holds 19 artifacts; the 14 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `plain_llm.profile` | `010d5167` | json | json | raw profile of data_train.csv |
| `run.data_out_of_time` | `7ddcc721` | table | table, 12257 rows | the subject's data_out_of_time.csv |
| `run.data_test` | `f0ac9fe8` | table | table, 15382 rows | the subject's data_test.csv |
| `run.data_train` | `0356ef50` | table | table, 36013 rows | the subject's data_train.csv |
| `run.data_vintage_holdout` | `940d14da` | table | table, 32177 rows | the subject's data_vintage_holdout.csv |
| `run.duration_s` | `db33e92f` | scalar | 2.476382208 | subject wall-clock seconds |
| `run.features` | `61276a96` | json | json | the subject's features.json |
| `run.metrics` | `31ce3d08` | json | json | the subject's metrics.json |
| `run.model_summary` | `b764932a` | json | json | the subject's model_summary.json |
| `run.predictions_vintage_holdout` | `afa7c750` | table | table, 32177 rows | the subject's predictions_vintage_holdout.csv |
| `run.projection` | `c07c9271` | json | json | the subject's projection.json |
| `run.splits` | `dca79f2f` | json | json | the subject's splits.json |
| `run.status` | `5c222bcc` | json | json | how the subject's subprocess ended |
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |

## Appendix C — Run trace summary

| quantity | value |
|---|---|
| tool calls | 1 (run_model 1) |
| plan steps (bounded loop) | 0 |
| LLM calls | 8 (plain_llm 1, extract 7) |
| re-asks | 0 |
| repair rounds | 0 |
| tokens in / out | 64,096 / 46,187 |
| notional cost (USD) | 1.7841 |
| wall-clock (s) | 551.59 |
| subject run (s) | 2.48 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | msr_prepayment-plain_llm-20260918T074209Z-986f3824 |

## Appendix D — Not checked

| item | reason |
|---|---|
| `check_stability` (R1) | this configuration runs no checks |
| `run_scenarios` (X1) | this configuration runs no checks |
| developer claims (T1, claim channel) | `plain_llm` runs no check over `package.yaml`'s declared claims |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
| every check of spec 3.7 but `run_model` | `plain_llm` runs the subject and one model call, by design |
