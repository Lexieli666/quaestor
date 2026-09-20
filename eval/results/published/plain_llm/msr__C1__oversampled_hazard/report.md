---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: msr_prepayment
version: "1.0"
model_type: discrete_time_hazard
configuration: plain_llm
model: claude-opus-5[1m]
run_id: msr_prepayment-plain_llm-20260918T212241Z-986f3824
data_mode: synthetic
synthetic_n: 2000
grounding_precision_pre: 0.0000
grounding_precision_post: 0.0000
n_claims: 168
n_findings_by_severity: {high: 2, medium: 5, low: 1, info: 2}
generated: "2026-09-18T21:22:41Z"
illustrative: false
---

# Validation report — `msr_prepayment` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `msr_prepayment` v1.0 | `plain_llm` | claude-opus-5[1m] | synthetic, n = 2000 | 0.0000 → 0.0000 | 2 / 5 / 1 / 2 |
<!-- quaestor:renderer:end -->

This report documents an independent validation of `msr_prepayment` version 1.0, a discrete-time hazard model of voluntary prepayment used to project cash flows for mortgage servicing right (MSR) valuation. The review covers the artifacts registered by the development run: the feature manifest [[art:61276a96:run.features]], the fitted model summary [[art:a65c5723:run.model_summary]], the split definitions [[art:dca79f2f:run.splits]], the performance metrics [[art:03ed7db3:run.metrics]], the four modelling tables [[art:0356ef50:run.data_train]], [[art:f0ac9fe8:run.data_test]], [[art:940d14da:run.data_vintage_holdout]], [[art:7ddcc721:run.data_out_of_time]], the corresponding prediction tables, and the run status and log artifacts [[art:5c222bcc:run.status]], [[art:fb0d94c5:run.stdout]], [[art:41728c38:run.stderr]].

Scope note and limitation: the validation was performed against the submitted artifact store only. No re-estimation, no independent replication of the fit, and no challenger model were available. The `run.model_summary` artifact as presented contains the age-spline knots and the tabulated baseline hazard but no covariate coefficient table, standard errors, or fit diagnostics; several conclusions below are therefore inferential and are marked as such.

**Overall assessment: not approved for production use in its current form.** Discrimination is acceptable and stable, but the model's absolute level is wrong by a factor of roughly four to five on every split including the training split, and the split design shows evidence of loan-level reuse across partitions. For an MSR model the absolute level *is* the deliverable: a model that predicts a ⟦unverified: 38%⟧ annual CPR where ⟦unverified: 10%⟧ was observed will systematically and materially understate the value of the servicing asset. Two high-severity findings must be cleared before the model is used for valuation, and four medium-severity findings require remediation on a defined timetable.

## 2. Conceptual soundness

The modelling approach — a discrete-time hazard on loan-month observations with a flexible baseline in loan age and a multiplicative covariate term — is a standard and defensible choice for prepayment. The covariate set in [[art:61276a96:run.features]] is conventional and economically sensible for the purpose: note rate, original LTV, credit score, log original UPB and SATO at origination; loan age, refinance incentive, burnout, log beginning-of-month balance, trailing ⟦unverified: 12⟧-month rate change and a sine/cosine seasonality pair measured before the period start. The declared timing is disciplined — ⟦unverified: 5⟧ features at origination, ⟦unverified: 7⟧ measured before the period start, ⟦unverified: 0⟧ measured during the period and ⟦unverified: 0⟧ after the outcome — so there is no *declared* look-ahead into the performance month. That is a genuine strength and reflects the correct construction for a hazard panel.

The baseline hazard in [[art:a65c5723:run.model_summary#baseline_hazard]] has the expected shape for a seasoning ramp: it rises from ⟦unverified: 0.00404⟧ at loan age ⟦unverified: 0⟧ to a peak of ⟦unverified: 0.02098⟧ around loan age ⟦unverified: 42⟧–⟦unverified: 43,⟧ then declines. A hump-shaped ramp is conceptually correct. Two concerns qualify this.

First, the age spline uses knots at ⟦unverified: 1,⟧ ⟦unverified: 10,⟧ ⟦unverified: 19,⟧ ⟦unverified: 31⟧ and ⟦unverified: 53⟧ months, and the tabulated hazard is carried out past loan age ⟦unverified: 102,⟧ but the training data supports loan ages only to ⟦unverified: 59⟧ months ([[art:0356ef50:run.data_train]], `loan_age` max = ⟦unverified: 59⟧). Everything beyond month ⟦unverified: 59⟧ is extrapolation beyond the last knot, where a spline of this form is linear in the log-hazard and therefore decays monotonically without limit. MSR valuation requires projecting the full remaining term — for ⟦unverified: 30⟧-year collateral, up to ⟦unverified: 360⟧ months. The great majority of the projection horizon is thus governed by an unsupported functional-form assumption rather than by data. This is developed further in section 5.

Second, several covariates are structurally collinear by construction. SATO is the note rate less the market rate prevailing at origination; refinance incentive is the note rate less the current market rate; `rate_change_12m` is a trailing difference of the same market rate series; and burnout is a cumulative function of past incentive. Including all five alongside the raw note rate is defensible only with explicit collinearity diagnostics, and none appear anywhere in the package. Without coefficient estimates in the model summary, the validator cannot check whether the incentive coefficient carries the expected positive sign, whether burnout carries the expected negative sign, or whether any of these have been destabilised by collinearity. This is a material documentation gap for a model of this use.

The training window (`period` from ⟦unverified: 201402⟧ to ⟦unverified: 201912⟧ in [[art:0356ef50:run.data_train]]) contains no observation of the ⟦unverified: 2020⟧–⟦unverified: 2021⟧ refinance wave. Any structural break associated with that episode is outside the estimation sample.

## 3. Data integrity and drift

**Feature manifest does not reconcile to the training table.** The manifest [[art:61276a96:run.features]] declares ⟦unverified: 12⟧ features. The raw profile of the training split [[art:0356ef50:run.data_train]] contains `note_rate`, `orig_ltv`, `credit_score`, `orig_upb_log`, `sato`, `loan_age`, `incentive`, `burnout`, `season_sin` and `season_cos` — ten of the twelve. Two declared features, `bom_balance_log` and `rate_change_12m`, are absent from the training data profile entirely. Either the model was scored on inputs that do not exist in the training table, or the profile and the manifest describe different datasets, or the two features were engineered downstream by a step that is not represented in the artifact store. All three explanations are defects. Under any of them the validator cannot confirm what the model was actually fit on, and the two missing features cannot be profiled for range, missingness, or drift.

**Missingness.** Every profiled column in the training table reports zero missing values. That is clean, but profiles for the test, vintage-holdout and out-of-time tables were not supplied, so missingness *differences* across splits cannot be tested. This is an untested control rather than a passed one.

**Split construction and possible loan reuse.** [[art:dca79f2f:run.splits]] reports distinct loan counts of ⟦unverified: 934⟧ (train), ⟦unverified: 400⟧ (test), ⟦unverified: 666⟧ (vintage holdout) and ⟦unverified: 515⟧ (out-of-time), summing to ⟦unverified: 2,515⟧ loan-split assignments. The training table alone contains `loan_id` values ranging from ⟦unverified: 1⟧ to ⟦unverified: 1,334,⟧ which bounds a contiguously numbered universe at ⟦unverified: 1,334⟧ loans. Train and vintage holdout together already claim ⟦unverified: 1,600⟧ loans. Unless the splits draw on disjoint identifier spaces — which the shared numbering convention and the presence of ⟦unverified: 934⟧ of the ⟦unverified: 1,334⟧ identifiers in train alone make unlikely — the same loans appear in more than one partition. For a loan-month panel this is the classic contamination failure mode: the same borrower's months land on both sides of the split, and the out-of-sample metrics are then not out-of-sample. This is recorded as a high-severity finding; it should be resolved definitively by intersecting the `loan_id` sets behind the `rows_hash` values in [[art:dca79f2f:run.splits]] and the four prediction tables.

**Population and outcome drift.** Observed monthly event rates differ sharply across partitions: ⟦unverified: 0.00852⟧ (train), ⟦unverified: 0.00806⟧ (test), ⟦unverified: 0.00482⟧ (vintage holdout) and ⟦unverified: 0.01795⟧ (out-of-time). The out-of-time rate is ⟦unverified: 2.1⟧x the training rate and ⟦unverified: 3.7⟧x the vintage-holdout rate. This is a large shift in the prepayment environment, consistent with a refinance wave falling in the out-of-time window. No PSI, KS-on-features, or any other drift statistic was produced for either the input distributions or the score distribution. Drift of this magnitude in the target, combined with the absence of any drift diagnostic, is recorded as a finding.

## 4. Outcomes analysis

**Discrimination is acceptable and, unusually, stable.** From [[art:03ed7db3:run.metrics]]: AUC is ⟦unverified: 0.7892⟧ (train), ⟦unverified: 0.7758⟧ (test), ⟦unverified: 0.7743⟧ (vintage holdout) and ⟦unverified: 0.7898⟧ (out-of-time), with Gini of ⟦unverified: 0.578⟧, ⟦unverified: 0.552⟧, ⟦unverified: 0.549⟧ and ⟦unverified: 0.580⟧ and KS of ⟦unverified: 0.454⟧, ⟦unverified: 0.428⟧, ⟦unverified: 0.453⟧ and ⟦unverified: 0.437⟧. The largest train-to-holdout AUC gap is ⟦unverified: 0.0149⟧, well inside any conventional degradation threshold; the out-of-time AUC is marginally *above* train. There is no evidence of overfitting in the rank-ordering sense. Interpreted cautiously, however, this stability is also consistent with the split-contamination concern in section 3: if loans are shared across partitions, out-of-sample discrimination will look artificially like in-sample discrimination. The clean result should not be relied upon until the split integrity question is closed.

**Calibration fails, severely, on every split including train.** Mean predicted monthly hazard against observed event rate:

| Split | n | mean predicted | observed event rate | ratio | CPR predicted | CPR actual |
|---|---|---|---|---|---|---|
| train | ⟦unverified: 36,013⟧ | ⟦unverified: 0.03925⟧ | ⟦unverified: 0.00852⟧ | ⟦unverified: 4.61⟧x | ⟦unverified: 0.3815⟧ | ⟦unverified: 0.0976⟧ |
| test | ⟦unverified: 15,382⟧ | ⟦unverified: 0.03802⟧ | ⟦unverified: 0.00806⟧ | ⟦unverified: 4.72⟧x | ⟦unverified: 0.3720⟧ | ⟦unverified: 0.0926⟧ |
| vintage_holdout | ⟦unverified: 32,177⟧ | ⟦unverified: 0.02582⟧ | ⟦unverified: 0.00482⟧ | ⟦unverified: 5.36⟧x | ⟦unverified: 0.2694⟧ | ⟦unverified: 0.0563⟧ |
| out_of_time | ⟦unverified: 12,257⟧ | ⟦unverified: 0.07793⟧ | ⟦unverified: 0.01795⟧ | ⟦unverified: 4.34⟧x | ⟦unverified: 0.6223⟧ | ⟦unverified: 0.1953⟧ |

The reported CPR figures are exactly the annualisation of the mean hazards (for train, ⟦unverified: 1⟧ − (⟦unverified: 1⟧ − ⟦unverified: 0.03925⟧)^⟦unverified: 12⟧ = ⟦unverified: 0.3815⟧; for the actuals, ⟦unverified: 1⟧ − (⟦unverified: 1⟧ − ⟦unverified: 0.00852⟧)^⟦unverified: 12⟧ = ⟦unverified: 0.0976⟧), so the CPR gap is not an independent error — it is the same level bias expressed on the scale that matters for valuation. The model predicts a ⟦unverified: 38%⟧ annual CPR on its own training data where ⟦unverified: 9.8%⟧ was realised, and a ⟦unverified: 62%⟧ CPR out-of-time against ⟦unverified: 19.5%⟧ realised. A CPR error of this size is disqualifying for MSR valuation: prepayment speed drives the runoff of the servicing fee strip almost one-for-one, and a model running four times fast will undervalue the asset dramatically and will misdirect any hedging built on its durations.

That the bias is present *in the training sample* rules out the usual explanations — regime shift, population change, or holdout mis-specification — and points instead to a defect in the fitting or scoring path. A correctly fit hazard model with an intercept reproduces the sample base rate almost exactly. Candidate causes worth investigating: predictions emitted on a different scale or from a different link than the one used in fitting; an offset, exposure, or annualisation applied to the scored output but not to the fitted target; case-control or event-weighted sampling in training that was never corrected back to the population prior; or a mismatch between the loan-month base of `n` and the base over which predictions were averaged.

**The reported calibration slopes are internally inconsistent with this bias and should not be relied on.** [[art:03ed7db3:run.metrics]] reports slopes of ⟦unverified: 1.015⟧ (train), ⟦unverified: 0.954⟧ (test), ⟦unverified: 0.856⟧ (vintage holdout) and ⟦unverified: 1.066⟧ (out-of-time). A model over-predicting the mean by a factor of ⟦unverified: 4.6⟧ cannot simultaneously have a calibration slope of ⟦unverified: 1.015⟧ unless the slope is being computed in a way that absorbs the level error — for instance as a logistic recalibration slope with a freely refitted intercept, which measures only the shape of the relationship and is blind to level bias by construction. The slope statistic as reported therefore conceals the principal defect, and the vintage-holdout value of ⟦unverified: 0.856⟧ additionally falls outside a conventional [⟦unverified: 0.9⟧, ⟦unverified: 1.1⟧] acceptance band, indicating shape error on that partition as well.

Brier scores (⟦unverified: 0.0104⟧ train, ⟦unverified: 0.0099⟧ test, ⟦unverified: 0.0061⟧ vintage holdout, ⟦unverified: 0.0240⟧ out-of-time) and log-loss (⟦unverified: 0.0630⟧, ⟦unverified: 0.0612⟧, ⟦unverified: 0.0416⟧, ⟦unverified: 0.1174⟧) are inflated relative to what the event rates would support and are consistent with the level bias rather than reassuring against it.

**Effective challenge.** No challenger model, benchmark, or naive baseline appears in the artifact store. There is consequently no evidence that the fitted hazard specification outperforms a simple seasoning-ramp-plus-incentive baseline, and no basis on which to assess whether the observed AUC of ~⟦unverified: 0.78⟧ is good, adequate, or poor for this collateral.

## 5. Sensitivity and scenario analysis

No scenario grid, no rate-shock ladder, and no partial-dependence or value-curve output were supplied. The `run.projection` artifact [[art:f7fe5a1a:run.projection]] is registered but its contents were not made available for review, so no projected CPR vector or MSR value curve could be inspected. The validator cannot confirm that predicted speeds respond monotonically and with the correct sign to a parallel shift in mortgage rates, which for a prepayment model is the single most important sensitivity test and an explicit expectation for models used in valuation.

What can be assessed is the age dimension, from the tabulated baseline in [[art:a65c5723:run.model_summary#baseline_hazard]]. The curve rises monotonically from ⟦unverified: 0.00404⟧ at age ⟦unverified: 0⟧ to ⟦unverified: 0.02098⟧ at age ⟦unverified: 42⟧–⟦unverified: 43⟧ and then declines monotonically thereafter, reaching ⟦unverified: 0.01246⟧ by age ⟦unverified: 102⟧ and continuing downward. Up to age ⟦unverified: 59⟧ this is supported by data. Beyond age ⟦unverified: 59⟧ it is not: the training table contains no loan older than ⟦unverified: 59⟧ months, the final spline knot sits at ⟦unverified: 53⟧ months, and the curve past that point is a pure linear-in-log extrapolation. An MSR projection runs to ⟦unverified: 360⟧ months. On the submitted specification, roughly ⟦unverified: 84%⟧ of the projection horizon is governed by an extrapolated tail that falls steadily toward zero, implying that seasoned loans essentially stop prepaying — an assumption that is neither economically motivated nor empirically tested here, and one that pushes projected lifetime speeds in the opposite direction from the four-fold level bias identified in section 4. The net effect on MSR value is indeterminate without rerunning the projection, which is itself a reason not to rely on the current output.

The out-of-time split provides the only quasi-scenario evidence available. It captures a materially faster prepayment environment (event rate ⟦unverified: 0.01795⟧ against ⟦unverified: 0.00852⟧ in train). The model's rank-ordering held up there, which is genuinely encouraging, but its level error persisted and widened in absolute terms — a ⟦unverified: 62%⟧ predicted CPR against ⟦unverified: 20%⟧ realised. The model does not respond correctly in magnitude to the one regime change it has been exposed to.

## 6. Findings and recommendations

**High severity — must be resolved before any production use**

1. *Calibration level failure (C1).* Predicted prepayment is ⟦unverified: 4.3⟧x–⟦unverified: 5.4⟧x observed on all four splits, including train. Required remediation: trace and repair the fitting/scoring path, then demonstrate that mean predicted hazard reproduces the observed event rate on the training sample to within a stated tolerance before any holdout evidence is presented.
2. *Probable loan reuse across splits (L2).* Split loan counts sum to ⟦unverified: 2,515⟧ against a loan universe bounded at ⟦unverified: 1,334⟧. Required remediation: publish the loan-level intersection of the four partitions; if non-empty, rebuild the splits with loan-level (not row-level) assignment and re-report all metrics.

**Medium severity — remediation required on a defined timetable**

3. *Feature manifest does not reconcile to the data (D1).* `bom_balance_log` and `rate_change_12m` are declared but absent from the training profile. Reconcile the manifest, the training table and the scoring inputs, and re-profile all four splits.
4. *Calibration slope statistic is misleading (C1).* Report the slope with the intercept held fixed, or report intercept and slope jointly, so that level bias cannot be absorbed. The vintage-holdout slope of ⟦unverified: 0.856⟧ is outside band on its own terms.
5. *Unsupported extrapolation of the age ramp (X1).* The baseline hazard is projected past ⟦unverified: 102⟧ months on data that stops at ⟦unverified: 59⟧. Either cap the ramp at the last supported age with a documented flat tail, extend the estimation sample to cover seasoned collateral, or overlay an externally justified long-age assumption and disclose it.
6. *Drift undocumented and outcome drift large (S1).* Event rates vary ⟦unverified: 3.7⟧x across partitions with no PSI or score-drift diagnostic produced. Compute feature-level and score-level PSI for each split against train and report against a stated threshold.
7. *Collinearity diagnostics absent (M1).* Note rate, SATO, incentive, `rate_change_12m` and burnout are structurally related. Report VIFs and the design-matrix condition number, and show coefficient signs and stability.

**Low severity and observations**

8. *No declared thresholds or coefficient disclosure (T1).* The package states no acceptance thresholds, no use limitations, and no coefficient table, so developer claims cannot be tested and the model summary cannot support independent review.
9. *No effective challenge (E1).* No challenger or benchmark exists in the store.
10. *Discrimination is stable out-of-sample (O1, informational).* The maximum train-to-holdout AUC gap is ⟦unverified: 0.0149⟧, below any conventional threshold — a positive result, subject to confirmation once finding ⟦unverified: 2⟧ is closed.

### F-001 · C1 calibration · severity **high**

Mean predicted monthly hazard is 0.03925 against an observed event rate of 0.00852 on train (4.61x), 0.03802 vs 0.00806 on test (4.72x), 0.02582 vs 0.00482 on the vintage holdout (5.36x), and 0.07793 vs 0.01795 out-of-time (4.34x). The reported CPR figures are the exact 12-month annualisation of these means (1 - (1 - 0.03925)^12 = 0.3815 predicted against 0.0976 actual on train; 0.6223 against 0.1953 out-of-time), so the CPR gap is the same defect expressed on the valuation scale rather than an independent error. Because the bias is present in the training sample itself, it cannot be explained by regime shift or holdout mis-specification: a correctly fit hazard model with an intercept reproduces its own sample base rate. This points to a defect in the fitting or scoring path -- predictions emitted on a different scale or link than the fitted target, an offset or annualisation applied to scores but not to the target, event-weighted or case-control sampling never corrected back to the population prior, or a mismatch between the loan-month base of n and the base over which predictions were averaged. For an MSR model this is disqualifying: prepayment speed drives runoff of the servicing fee strip nearly one-for-one, so a model running four times fast will materially undervalue the asset and misdirect any hedge built on its durations. Remediation must demonstrate that mean predicted hazard reproduces the training event rate within a stated tolerance before any holdout evidence is presented.

### F-002 · L2 contamination · severity **high**

run.splits reports distinct loan counts of 934 (train), 400 (test), 666 (vintage holdout) and 515 (out-of-time), summing to 2,515 loan-split assignments. The training table's loan_id field ranges from 1 to 1,334, which bounds a contiguously numbered loan universe at 1,334 distinct loans; train and the vintage holdout together already claim 1,600. Unless the partitions draw on disjoint identifier spaces -- made unlikely by the shared numbering convention and by train alone holding 934 of the 1,334 identifiers -- the same loans appear in more than one split. In a loan-month panel this is the classic contamination failure mode: the same borrower's months land on both sides of the boundary, and the reported out-of-sample metrics are then not out-of-sample. This would also supply an alternative explanation for the unusually flat AUC profile across partitions (0.7892 train, 0.7758 test, 0.7743 vintage, 0.7898 out-of-time), in which the out-of-time AUC actually exceeds train. The inference is drawn from counts rather than from a direct set intersection and should be closed definitively by intersecting the loan_id sets behind the rows_hash values in run.splits and the four prediction tables; if non-empty, the splits must be rebuilt with loan-level rather than row-level assignment and all metrics re-reported.

### F-003 · D1 data integrity · severity **medium**

The feature manifest declares 12 features, of which 7 are timed before_period_start. The raw profile of the training split contains note_rate, orig_ltv, credit_score, orig_upb_log, sato, loan_age, incentive, burnout, season_sin and season_cos -- ten of the twelve -- plus loan_id, period and the prepaid target. bom_balance_log and rate_change_12m do not appear at all. Either the model was scored on inputs absent from the training table, or the manifest and the profile describe different datasets, or the two features were engineered by a downstream step not represented in the artifact store. Each explanation is a defect, and under all three the validator cannot confirm what the model was actually fit on. The two features are also unprofiled, so their ranges, missingness and cross-split drift cannot be assessed -- a material gap given that rate_change_12m carries the rate regime that drives prepayment. Separately, missingness is reported as zero for every profiled training column, but no profiles were supplied for the test, vintage-holdout or out-of-time tables, so cross-split missingness differences remain an untested control rather than a passed one.

### F-004 · C1 calibration · severity **medium**

Reported calibration slopes are 1.0147 (train), 0.9537 (test), 0.8562 (vintage holdout) and 1.0664 (out-of-time). A model over-predicting the mean hazard by a factor of 4.6 on its own training data cannot simultaneously exhibit a training calibration slope of 1.015 unless the statistic is computed in a way that absorbs level error -- most plausibly as a logistic recalibration slope with a freely refitted intercept, which by construction measures only the shape of the predicted-to-observed relationship and is blind to the level. As reported, the slope therefore masks the principal defect in the model and would allow a reviewer relying on it alone to conclude that calibration is acceptable. The vintage-holdout value of 0.856 additionally falls outside a conventional [0.9, 1.1] acceptance band on its own terms, indicating shape error on that partition in addition to the level error. Remediation: report the slope with the intercept held fixed, or report calibration intercept and slope jointly, so that level bias is visible in the statistic.

### F-005 · X1 scenario analysis · severity **medium**

The tabulated baseline hazard rises monotonically from 0.004044 at loan age 0 to a peak of 0.020978 at ages 42-43, then declines monotonically, reaching 0.012458 by age 102 and continuing downward. The hump shape is conceptually correct for a seasoning ramp, but the training table contains no loan older than 59 months and the final age-spline knot sits at 53 months, so everything past month 59 is a linear-in-log extrapolation beyond the last knot rather than an estimated quantity. MSR valuation projects the full remaining term -- up to 360 months for 30-year collateral -- so roughly 84% of the projection horizon is governed by an unsupported functional-form assumption whose tail decays steadily toward zero, implying that seasoned loans effectively stop prepaying. That assumption pushes projected lifetime speeds in the opposite direction from the four-fold level bias, leaving the net effect on MSR value indeterminate without rerunning the projection. No scenario grid, rate-shock ladder or value curve was supplied, and the contents of run.projection were not available for review, so the more important sensitivity -- monotone, correctly signed CPR and MSR response to a parallel rate shift -- could not be tested at all. Remediation: cap the ramp at the last supported age with a documented flat tail, extend the estimation sample to seasoned collateral, or overlay and disclose an externally justified long-age assumption; and publish a rate-shock ladder.

### F-006 · S1 population drift · severity **medium**

Monthly event rates are 0.00852 (train), 0.00806 (test), 0.00482 (vintage holdout) and 0.01795 (out-of-time). The out-of-time rate is 2.1x the training rate and 3.7x the vintage-holdout rate, indicating a materially different prepayment environment across partitions -- consistent with a refinance wave falling in the out-of-time window, and with a training period (201402 to 201912) that contains no observation of the 2020-2021 refinance episode. No PSI, feature-level drift statistic, or score-distribution drift statistic was computed for any split, so it cannot be determined whether the shift is driven by the rate-sensitive covariates (incentive, sato, rate_change_12m, burnout), by population composition, or by a structural break in behaviour. The model's over-prediction ratio also varies with the regime, from 4.34x out-of-time to 5.36x on the vintage holdout, which is itself a sign of regime sensitivity in the level. Remediation: compute feature-level and score-level PSI against the estimation sample for each split and report against a stated threshold (0.10 investigate, 0.25 escalate).

### F-007 · M1 collinearity · severity **medium**

The feature set includes note_rate, sato, incentive, rate_change_12m and burnout together. These are related by construction: SATO is the note rate less the market rate at origination, incentive is the note rate less the current market rate, rate_change_12m is a trailing difference of the same market rate series, and burnout is a cumulative function of past incentive. Near-collinearity among them is close to certain, yet no variance inflation factors, condition number, or coefficient stability evidence appears anywhere in the package. The model summary as presented contains the age-spline knots and the tabulated baseline hazard but no covariate coefficient table or standard errors, so the validator cannot check whether the incentive coefficient carries the expected positive sign, whether burnout carries the expected negative sign, or whether collinearity has inflated standard errors or destabilised the estimates. This matters beyond inference: collinearity-driven coefficient instability is one of the mechanisms that can produce a badly miscalibrated level, and it cannot be ruled out as a contributor to the primary finding. Remediation: report VIFs and the design-matrix condition number, disclose the coefficient table with signs and standard errors, and justify retaining all five rate-related covariates.

### F-008 · T1 declared threshold · severity **low**

The submitted package states no performance acceptance thresholds, no calibration tolerance, no use limitations, and no documented model assumptions against which the observed metrics could be tested. The model summary discloses the age-spline knots and the tabulated baseline hazard but omits the covariate coefficient table, standard errors and fit diagnostics. Consequently no developer claim can be independently verified, and the summary as it stands cannot support independent review or the reproduction of a single prediction. For a model feeding MSR valuation, documented thresholds -- in particular an actual-to-predicted CPR tolerance -- are a prerequisite for both approval and ongoing monitoring.

### F-009 · E1 effective challenge · severity **info**

The artifact store contains a single champion run with no challenger, benchmark, or naive baseline. There is therefore no evidence that the fitted discrete-time hazard specification outperforms a simple alternative such as a seasoning-ramp-plus-incentive model or an industry-standard prepayment curve, and no basis on which to judge whether the observed AUC of roughly 0.78 is strong, adequate, or weak for this collateral and horizon. No challenger was found to beat the champion because none was run; this finding records the absence of the control rather than a failed comparison. Remediation: submit a documented challenger comparison on identical splits as part of the resubmission.

### F-010 · O1 out-of-sample degradation · severity **info**

AUC is 0.7892 on train, 0.7758 on test, 0.7743 on the vintage holdout and 0.7898 out-of-time; Gini is 0.578, 0.552, 0.549 and 0.580, and KS is 0.454, 0.428, 0.453 and 0.437. The largest train-to-holdout AUC gap is 0.0149, comfortably inside any conventional degradation threshold, and the out-of-time AUC marginally exceeds train. On its face there is no evidence of overfitting in the rank-ordering sense, which is a genuine positive for the specification. The result is recorded as informational rather than clean because the same flatness is also what loan reuse across splits would produce; it should be re-confirmed once the split-integrity finding is closed, and it carries no weight against the separate and severe calibration failure, since discrimination and level are independent properties and only the latter drives MSR value.

Candidates raised and not promoted: none.

### Open items

No open item was recorded for this validation.

## 7. Ongoing monitoring recommendations

Once the high-severity findings are remediated and the model is re-submitted, the following monitoring programme is recommended.

**Monthly.** Report actual versus predicted CPR at the total-portfolio level and the ratio of mean predicted hazard to realised event rate, with an amber trigger at a ratio outside [⟦unverified: 0.85⟧, ⟦unverified: 1.15⟧] and a red trigger outside [⟦unverified: 0.75⟧, ⟦unverified: 1.25⟧] for two consecutive months. Given that the present defect is a level error, the actual-to-predicted CPR ratio should be the headline monitoring metric, reported before and above any discrimination statistic.

**Monthly.** Track score-distribution PSI and feature-level PSI against the estimation sample, with a ⟦unverified: 0.10⟧ investigate threshold and a ⟦unverified: 0.25⟧ escalate threshold. Include `incentive`, `sato`, `rate_change_12m` and `burnout` explicitly, since these carry the rate regime.

**Quarterly.** Report AUC, KS and the fixed-intercept calibration slope on a rolling ⟦unverified: 12⟧-month observation window, with an alert if AUC falls more than ⟦unverified: 0.05⟧ below the validated benchmark of ⟦unverified: 0.78⟧ or if the slope leaves [⟦unverified: 0.9⟧, ⟦unverified: 1.1⟧].

**Quarterly.** Report actual versus predicted CPR disaggregated by loan-age bucket (⟦unverified: 0⟧–⟦unverified: 12,⟧ ⟦unverified: 13⟧–⟦unverified: 24,⟧ ⟦unverified: 25⟧–⟦unverified: 36,⟧ ⟦unverified: 37⟧–⟦unverified: 59,⟧ ⟦unverified: 60⟧+) and by incentive bucket. The ⟦unverified: 60⟧+ age bucket should be reported separately and prominently for as long as the age ramp relies on extrapolation, since that region is unsupported by the estimation data.

**Semi-annual.** Refresh the seasoning ramp against accumulated seasoned experience and re-test the extrapolated tail. Re-run a rate-shock ladder (−⟦unverified: 100,⟧ −⟦unverified: 50,⟧ ⟦unverified: 0,⟧ +⟦unverified: 50,⟧ +⟦unverified: 100,⟧ +⟦unverified: 200⟧ bp) and confirm monotone, correctly signed CPR and MSR value response; a non-monotone or wrong-signed curve is an immediate escalation.

**Annual.** Full revalidation including re-estimation on refreshed data, a documented challenger comparison, and re-testing of split integrity by loan identifier. Any structural change in the rate environment comparable to the out-of-time period should trigger an off-cycle revalidation rather than waiting for the annual date.

## Appendix A — Claims

Grounding precision 0.0000 before repair (0 of 168 claims verified; 132 unsupported, 32 dangling, 4 unattributed) and 0.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 0/2; conceptual_soundness 0/25; data_integrity 0/18; outcomes 0/69; sensitivity 0/17; findings 0/10; monitoring 0/27.

Developer claims: `plain_llm` runs no check over `package.yaml`'s declared claims See Appendix D.

Excluded numeric tokens (not claims): section_number (section 5, section 3, section 4, 1.); citation_hash (61276a96, a65c5723, dca79f2f, 03ed7db3); package_version (1.0); extractor_returned_excluded_token (1.0, 4.0, 5.0, 2.0).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | **Overall assessment: not approved for production use in its… | 38 | percent |  |  | eq |  | unsupported |  |
| 2 | summary | **Overall assessment: not approved for production use in its… | 10 | percent |  |  | eq |  | unsupported |  |
| 3 | conceptual_soundness | The modelling approach — a discrete-time hazard on loan-mont… | 12 | months |  |  | eq | `[[art:61276a96:run.features]]` | dangling |  |
| 4 | conceptual_soundness | The modelling approach — a discrete-time hazard on loan-mont… | 5 | count |  |  | eq |  | unsupported |  |
| 5 | conceptual_soundness | The modelling approach — a discrete-time hazard on loan-mont… | 7 | count |  |  | eq |  | unsupported |  |
| 6 | conceptual_soundness | The modelling approach — a discrete-time hazard on loan-mont… | 0 | count |  |  | eq |  | unsupported |  |
| 7 | conceptual_soundness | The modelling approach — a discrete-time hazard on loan-mont… | 0 | count |  |  | eq |  | unsupported |  |
| 8 | conceptual_soundness | The baseline hazard in has the expected shape for a seasonin… | 0.00404 | ratio | baseline_hazard |  | eq | `[[art:a65c5723:run.model_summary#baseline_hazard]]` | dangling |  |
| 9 | conceptual_soundness | The baseline hazard in has the expected shape for a seasonin… | 0 | months | loan_age |  | eq | `[[art:a65c5723:run.model_summary#baseline_hazard]]` | dangling |  |
| 10 | conceptual_soundness | The baseline hazard in has the expected shape for a seasonin… | 0.02098 | ratio | baseline_hazard |  | eq | `[[art:a65c5723:run.model_summary#baseline_hazard]]` | dangling |  |
| 11 | conceptual_soundness | The baseline hazard in has the expected shape for a seasonin… | 42 | months | loan_age |  | eq | `[[art:a65c5723:run.model_summary#baseline_hazard]]` | dangling |  |
| 12 | conceptual_soundness | The baseline hazard in has the expected shape for a seasonin… | 43 | months | loan_age |  | eq | `[[art:a65c5723:run.model_summary#baseline_hazard]]` | dangling |  |
| 13 | conceptual_soundness | First, the age spline uses knots at 1, 10, 19, 31 and 53 mon… | 1 | months |  |  | eq |  | unsupported |  |
| 14 | conceptual_soundness | First, the age spline uses knots at 1, 10, 19, 31 and 53 mon… | 10 | months |  |  | eq |  | unsupported |  |
| 15 | conceptual_soundness | First, the age spline uses knots at 1, 10, 19, 31 and 53 mon… | 19 | months |  |  | eq |  | unsupported |  |
| 16 | conceptual_soundness | First, the age spline uses knots at 1, 10, 19, 31 and 53 mon… | 31 | months |  |  | eq |  | unsupported |  |
| 17 | conceptual_soundness | First, the age spline uses knots at 1, 10, 19, 31 and 53 mon… | 53 | months |  |  | eq |  | unsupported |  |
| 18 | conceptual_soundness | First, the age spline uses knots at 1, 10, 19, 31 and 53 mon… | 102 | months | loan_age |  | eq |  | unsupported |  |
| 19 | conceptual_soundness | First, the age spline uses knots at 1, 10, 19, 31 and 53 mon… | 59 | months | loan_age | train | eq | `[[art:0356ef50:run.data_train]]` | dangling |  |
| 20 | conceptual_soundness | First, the age spline uses knots at 1, 10, 19, 31 and 53 mon… | 59 | months | loan_age | train | eq | `[[art:0356ef50:run.data_train]]` | dangling |  |
| 21 | conceptual_soundness | First, the age spline uses knots at 1, 10, 19, 31 and 53 mon… | 59 | months | loan_age | train | eq |  | unsupported |  |
| 22 | conceptual_soundness | First, the age spline uses knots at 1, 10, 19, 31 and 53 mon… | 30 | ratio |  |  | eq |  | unsupported |  |
| 23 | conceptual_soundness | First, the age spline uses knots at 1, 10, 19, 31 and 53 mon… | 360 | months |  |  | eq |  | unsupported |  |
| 24 | conceptual_soundness | The training window (`period` from 201402 to 201912 in ) con… | 201402 | ratio | period | train | eq | `[[art:0356ef50:run.data_train]]` | dangling |  |
| 25 | conceptual_soundness | The training window (`period` from 201402 to 201912 in ) con… | 201912 | ratio | period | train | eq | `[[art:0356ef50:run.data_train]]` | dangling |  |
| 26 | conceptual_soundness | The training window (`period` from 201402 to 201912 in ) con… | 2020 | ratio |  |  | eq |  | unsupported |  |
| 27 | conceptual_soundness | The training window (`period` from 201402 to 201912 in ) con… | 2021 | ratio |  |  | eq |  | unsupported |  |
| 28 | data_integrity | **Feature manifest does not reconcile to the training table.… | 12 | count | features |  | eq | `[[art:61276a96:run.features]]` | dangling |  |
| 29 | data_integrity | **Split construction and possible loan reuse.** reports dist… | 934 | count | splits | train | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 30 | data_integrity | **Split construction and possible loan reuse.** reports dist… | 400 | count | splits | test | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 31 | data_integrity | **Split construction and possible loan reuse.** reports dist… | 666 | count | splits | vintage_holdout | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 32 | data_integrity | **Split construction and possible loan reuse.** reports dist… | 515 | count | splits | out_of_time | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 33 | data_integrity | **Split construction and possible loan reuse.** reports dist… | 2515 | count | splits |  | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 34 | data_integrity | **Split construction and possible loan reuse.** reports dist… | 1 | count |  | train | eq |  | unsupported |  |
| 35 | data_integrity | **Split construction and possible loan reuse.** reports dist… | 1334 | count |  | train | eq |  | unsupported |  |
| 36 | data_integrity | **Split construction and possible loan reuse.** reports dist… | 1334 | count |  |  | eq |  | unsupported |  |
| 37 | data_integrity | **Split construction and possible loan reuse.** reports dist… | 1600 | count |  |  | eq |  | unsupported |  |
| 38 | data_integrity | **Split construction and possible loan reuse.** reports dist… | 934 | count |  | train | eq |  | unsupported |  |
| 39 | data_integrity | **Split construction and possible loan reuse.** reports dist… | 1334 | count |  |  | eq |  | unsupported |  |
| 40 | data_integrity | **Population and outcome drift.** Observed monthly event rat… | 0.00852 | ratio | event_rate | train | eq |  | unsupported |  |
| 41 | data_integrity | **Population and outcome drift.** Observed monthly event rat… | 0.00806 | ratio | event_rate | test | eq |  | unsupported |  |
| 42 | data_integrity | **Population and outcome drift.** Observed monthly event rat… | 0.00482 | ratio | event_rate | vintage_holdout | eq |  | unsupported |  |
| 43 | data_integrity | **Population and outcome drift.** Observed monthly event rat… | 0.01795 | ratio | event_rate | out_of_time | eq |  | unsupported |  |
| 44 | data_integrity | **Population and outcome drift.** Observed monthly event rat… | 2.1 | ratio | event_rate | out_of_time | ratio |  | unsupported |  |
| 45 | data_integrity | **Population and outcome drift.** Observed monthly event rat… | 3.7 | ratio | event_rate | out_of_time | ratio |  | unsupported |  |
| 46 | outcomes | **Discrimination is acceptable and, unusually, stable.** Fro… | 0.7892 | ratio | auc | train | eq | `[[art:03ed7db3:run.metrics]]` | dangling |  |
| 47 | outcomes | **Discrimination is acceptable and, unusually, stable.** Fro… | 0.7758 | ratio | auc | test | eq | `[[art:03ed7db3:run.metrics]]` | dangling |  |
| 48 | outcomes | **Discrimination is acceptable and, unusually, stable.** Fro… | 0.7743 | ratio | auc | vintage_holdout | eq | `[[art:03ed7db3:run.metrics]]` | dangling |  |
| 49 | outcomes | **Discrimination is acceptable and, unusually, stable.** Fro… | 0.7898 | ratio | auc | out_of_time | eq | `[[art:03ed7db3:run.metrics]]` | dangling |  |
| 50 | outcomes | **Discrimination is acceptable and, unusually, stable.** Fro… | 0.578 | ratio | gini | train | eq | `[[art:03ed7db3:run.metrics]]` | dangling |  |
| 51 | outcomes | **Discrimination is acceptable and, unusually, stable.** Fro… | 0.552 | ratio | gini | test | eq | `[[art:03ed7db3:run.metrics]]` | dangling |  |
| 52 | outcomes | **Discrimination is acceptable and, unusually, stable.** Fro… | 0.549 | ratio | gini | vintage_holdout | eq | `[[art:03ed7db3:run.metrics]]` | dangling |  |
| 53 | outcomes | **Discrimination is acceptable and, unusually, stable.** Fro… | 0.58 | ratio | gini | out_of_time | eq | `[[art:03ed7db3:run.metrics]]` | dangling |  |
| 54 | outcomes | **Discrimination is acceptable and, unusually, stable.** Fro… | 0.454 | ratio | ks | train | eq | `[[art:03ed7db3:run.metrics]]` | dangling |  |
| 55 | outcomes | **Discrimination is acceptable and, unusually, stable.** Fro… | 0.428 | ratio | ks | test | eq | `[[art:03ed7db3:run.metrics]]` | dangling |  |
| 56 | outcomes | **Discrimination is acceptable and, unusually, stable.** Fro… | 0.453 | ratio | ks | vintage_holdout | eq | `[[art:03ed7db3:run.metrics]]` | dangling |  |
| 57 | outcomes | **Discrimination is acceptable and, unusually, stable.** Fro… | 0.437 | ratio | ks | out_of_time | eq | `[[art:03ed7db3:run.metrics]]` | dangling |  |
| 58 | outcomes | **Discrimination is acceptable and, unusually, stable.** Fro… | 0.0149 | ratio | delta_auc | vintage_holdout | delta |  | unsupported |  |
| 59 | outcomes | \| train \| 36,013 \| 0.03925 \| 0.00852 \| 4.61x \| 0.3815 \| 0.09… | 36013 | count | n | train | eq |  | unsupported |  |
| 60 | outcomes | \| train \| 36,013 \| 0.03925 \| 0.00852 \| 4.61x \| 0.3815 \| 0.09… | 0.03925 | ratio | mean_predicted | train | eq |  | unsupported |  |
| 61 | outcomes | \| train \| 36,013 \| 0.03925 \| 0.00852 \| 4.61x \| 0.3815 \| 0.09… | 0.00852 | ratio | event_rate | train | eq |  | unsupported |  |
| 62 | outcomes | \| train \| 36,013 \| 0.03925 \| 0.00852 \| 4.61x \| 0.3815 \| 0.09… | 4.61 | ratio | ratio | train | ratio |  | unsupported |  |
| 63 | outcomes | \| train \| 36,013 \| 0.03925 \| 0.00852 \| 4.61x \| 0.3815 \| 0.09… | 0.3815 | ratio | cpr_predicted | train | eq |  | unsupported |  |
| 64 | outcomes | \| train \| 36,013 \| 0.03925 \| 0.00852 \| 4.61x \| 0.3815 \| 0.09… | 0.0976 | ratio | cpr_actual | train | eq |  | unsupported |  |
| 65 | outcomes | \| test \| 15,382 \| 0.03802 \| 0.00806 \| 4.72x \| 0.3720 \| 0.092… | 15382 | count | n | test | eq |  | unsupported |  |
| 66 | outcomes | \| test \| 15,382 \| 0.03802 \| 0.00806 \| 4.72x \| 0.3720 \| 0.092… | 0.03802 | ratio | mean_predicted | test | eq |  | unsupported |  |
| 67 | outcomes | \| test \| 15,382 \| 0.03802 \| 0.00806 \| 4.72x \| 0.3720 \| 0.092… | 0.00806 | ratio | event_rate | test | eq |  | unsupported |  |
| 68 | outcomes | \| test \| 15,382 \| 0.03802 \| 0.00806 \| 4.72x \| 0.3720 \| 0.092… | 4.72 | ratio | ratio | test | ratio |  | unsupported |  |
| 69 | outcomes | \| test \| 15,382 \| 0.03802 \| 0.00806 \| 4.72x \| 0.3720 \| 0.092… | 0.372 | ratio | cpr_predicted | test | eq |  | unsupported |  |
| 70 | outcomes | \| test \| 15,382 \| 0.03802 \| 0.00806 \| 4.72x \| 0.3720 \| 0.092… | 0.0926 | ratio | cpr_actual | test | eq |  | unsupported |  |
| 71 | outcomes | \| vintage_holdout \| 32,177 \| 0.02582 \| 0.00482 \| 5.36x \| 0.2… | 32177 | count | n | vintage_holdout | eq |  | unsupported |  |
| 72 | outcomes | \| vintage_holdout \| 32,177 \| 0.02582 \| 0.00482 \| 5.36x \| 0.2… | 0.02582 | ratio | mean_predicted | vintage_holdout | eq |  | unsupported |  |
| 73 | outcomes | \| vintage_holdout \| 32,177 \| 0.02582 \| 0.00482 \| 5.36x \| 0.2… | 0.00482 | ratio | event_rate | vintage_holdout | eq |  | unsupported |  |
| 74 | outcomes | \| vintage_holdout \| 32,177 \| 0.02582 \| 0.00482 \| 5.36x \| 0.2… | 5.36 | ratio | ratio | vintage_holdout | ratio |  | unsupported |  |
| 75 | outcomes | \| vintage_holdout \| 32,177 \| 0.02582 \| 0.00482 \| 5.36x \| 0.2… | 0.2694 | ratio | cpr_predicted | vintage_holdout | eq |  | unsupported |  |
| 76 | outcomes | \| vintage_holdout \| 32,177 \| 0.02582 \| 0.00482 \| 5.36x \| 0.2… | 0.0563 | ratio | cpr_actual | vintage_holdout | eq |  | unsupported |  |
| 77 | outcomes | \| out_of_time \| 12,257 \| 0.07793 \| 0.01795 \| 4.34x \| 0.6223… | 12257 | count | n | out_of_time | eq |  | unsupported |  |
| 78 | outcomes | \| out_of_time \| 12,257 \| 0.07793 \| 0.01795 \| 4.34x \| 0.6223… | 0.07793 | ratio | mean_predicted | out_of_time | eq |  | unsupported |  |
| 79 | outcomes | \| out_of_time \| 12,257 \| 0.07793 \| 0.01795 \| 4.34x \| 0.6223… | 0.01795 | ratio | event_rate | out_of_time | eq |  | unsupported |  |
| 80 | outcomes | \| out_of_time \| 12,257 \| 0.07793 \| 0.01795 \| 4.34x \| 0.6223… | 4.34 | ratio | ratio | out_of_time | ratio |  | unsupported |  |
| 81 | outcomes | \| out_of_time \| 12,257 \| 0.07793 \| 0.01795 \| 4.34x \| 0.6223… | 0.6223 | ratio | cpr_predicted | out_of_time | eq |  | unsupported |  |
| 82 | outcomes | \| out_of_time \| 12,257 \| 0.07793 \| 0.01795 \| 4.34x \| 0.6223… | 0.1953 | ratio | cpr_actual | out_of_time | eq |  | unsupported |  |
| 83 | outcomes | The reported CPR figures are exactly the annualisation of th… | 1 | ratio |  |  | eq |  | unsupported |  |
| 84 | outcomes | The reported CPR figures are exactly the annualisation of th… | 1 | ratio |  |  | eq |  | unsupported |  |
| 85 | outcomes | The reported CPR figures are exactly the annualisation of th… | 0.03925 | ratio | mean_predicted | train | eq |  | unsupported |  |
| 86 | outcomes | The reported CPR figures are exactly the annualisation of th… | 12 | months |  |  | eq |  | unsupported |  |
| 87 | outcomes | The reported CPR figures are exactly the annualisation of th… | 0.3815 | ratio | cpr_predicted | train | eq |  | unsupported |  |
| 88 | outcomes | The reported CPR figures are exactly the annualisation of th… | 1 | ratio |  |  | eq |  | unsupported |  |
| 89 | outcomes | The reported CPR figures are exactly the annualisation of th… | 1 | ratio |  |  | eq |  | unsupported |  |
| 90 | outcomes | The reported CPR figures are exactly the annualisation of th… | 0.00852 | ratio | event_rate | train | eq |  | unsupported |  |
| 91 | outcomes | The reported CPR figures are exactly the annualisation of th… | 12 | months |  |  | eq |  | unsupported |  |
| 92 | outcomes | The reported CPR figures are exactly the annualisation of th… | 0.0976 | ratio | cpr_actual | train | eq |  | unsupported |  |
| 93 | outcomes | The reported CPR figures are exactly the annualisation of th… | 38 | percent | cpr_predicted | train | eq |  | unsupported |  |
| 94 | outcomes | The reported CPR figures are exactly the annualisation of th… | 9.8 | percent | cpr_actual | train | eq |  | unsupported |  |
| 95 | outcomes | The reported CPR figures are exactly the annualisation of th… | 62 | percent | cpr_predicted | out_of_time | eq |  | unsupported |  |
| 96 | outcomes | The reported CPR figures are exactly the annualisation of th… | 19.5 | percent | cpr_actual | out_of_time | eq |  | unsupported |  |
| 97 | outcomes | **The reported calibration slopes are internally inconsisten… | 1.015 | ratio | calibration_slope | train | eq | `[[art:03ed7db3:run.metrics]]` | dangling |  |
| 98 | outcomes | **The reported calibration slopes are internally inconsisten… | 0.954 | ratio | calibration_slope | test | eq | `[[art:03ed7db3:run.metrics]]` | dangling |  |
| 99 | outcomes | **The reported calibration slopes are internally inconsisten… | 0.856 | ratio | calibration_slope | vintage_holdout | eq | `[[art:03ed7db3:run.metrics]]` | dangling |  |
| 100 | outcomes | **The reported calibration slopes are internally inconsisten… | 1.066 | ratio | calibration_slope | out_of_time | eq | `[[art:03ed7db3:run.metrics]]` | dangling |  |
| 101 | outcomes | **The reported calibration slopes are internally inconsisten… | 4.6 | ratio | ratio | train | ratio |  | unsupported |  |
| 102 | outcomes | **The reported calibration slopes are internally inconsisten… | 1.015 | ratio | calibration_slope | train | eq |  | unsupported |  |
| 103 | outcomes | **The reported calibration slopes are internally inconsisten… | 0.856 | ratio | calibration_slope | vintage_holdout | eq |  | unsupported |  |
| 104 | outcomes | **The reported calibration slopes are internally inconsisten… | 0.9 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 105 | outcomes | **The reported calibration slopes are internally inconsisten… | 1.1 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 106 | outcomes | Brier scores (0.0104 train, 0.0099 test, 0.0061 vintage hold… | 0.0104 | ratio | brier | train | eq |  | unsupported |  |
| 107 | outcomes | Brier scores (0.0104 train, 0.0099 test, 0.0061 vintage hold… | 0.0099 | ratio | brier | test | eq |  | unsupported |  |
| 108 | outcomes | Brier scores (0.0104 train, 0.0099 test, 0.0061 vintage hold… | 0.0061 | ratio | brier | vintage_holdout | eq |  | unsupported |  |
| 109 | outcomes | Brier scores (0.0104 train, 0.0099 test, 0.0061 vintage hold… | 0.024 | ratio | brier | out_of_time | eq |  | unsupported |  |
| 110 | outcomes | Brier scores (0.0104 train, 0.0099 test, 0.0061 vintage hold… | 0.063 | ratio | log_loss | train | eq |  | unsupported |  |
| 111 | outcomes | Brier scores (0.0104 train, 0.0099 test, 0.0061 vintage hold… | 0.0612 | ratio | log_loss | test | eq |  | unsupported |  |
| 112 | outcomes | Brier scores (0.0104 train, 0.0099 test, 0.0061 vintage hold… | 0.0416 | ratio | log_loss | vintage_holdout | eq |  | unsupported |  |
| 113 | outcomes | Brier scores (0.0104 train, 0.0099 test, 0.0061 vintage hold… | 0.1174 | ratio | log_loss | out_of_time | eq |  | unsupported |  |
| 114 | outcomes | **Effective challenge.** No challenger model, benchmark, or… | 0.78 | ratio | auc |  | eq |  | unsupported |  |
| 115 | sensitivity | What can be assessed is the age dimension, from the tabulate… | 0.00404 | ratio | baseline_hazard |  | eq |  | unsupported |  |
| 116 | sensitivity | What can be assessed is the age dimension, from the tabulate… | 0 | months |  |  | eq |  | unsupported |  |
| 117 | sensitivity | What can be assessed is the age dimension, from the tabulate… | 0.02098 | ratio | baseline_hazard |  | eq |  | unsupported |  |
| 118 | sensitivity | What can be assessed is the age dimension, from the tabulate… | 42 | months |  |  | eq |  | unsupported |  |
| 119 | sensitivity | What can be assessed is the age dimension, from the tabulate… | 43 | months |  |  | eq |  | unsupported |  |
| 120 | sensitivity | What can be assessed is the age dimension, from the tabulate… | 0.01246 | ratio | baseline_hazard |  | eq |  | unsupported |  |
| 121 | sensitivity | What can be assessed is the age dimension, from the tabulate… | 102 | months |  |  | eq |  | unsupported |  |
| 122 | sensitivity | What can be assessed is the age dimension, from the tabulate… | 59 | months |  |  | eq |  | unsupported |  |
| 123 | sensitivity | What can be assessed is the age dimension, from the tabulate… | 59 | months |  |  | eq |  | unsupported |  |
| 124 | sensitivity | What can be assessed is the age dimension, from the tabulate… | 59 | months |  | train | eq |  | unsupported |  |
| 125 | sensitivity | What can be assessed is the age dimension, from the tabulate… | 53 | months |  |  | eq |  | unsupported |  |
| 126 | sensitivity | What can be assessed is the age dimension, from the tabulate… | 360 | months |  |  | eq |  | unsupported |  |
| 127 | sensitivity | What can be assessed is the age dimension, from the tabulate… | 84 | percent |  |  | eq |  | unsupported |  |
| 128 | sensitivity | The out-of-time split provides the only quasi-scenario evide… | 0.01795 | ratio | event_rate | out_of_time | eq |  | unsupported |  |
| 129 | sensitivity | The out-of-time split provides the only quasi-scenario evide… | 0.00852 | ratio | event_rate | train | eq |  | unsupported |  |
| 130 | sensitivity | The out-of-time split provides the only quasi-scenario evide… | 62 | percent | cpr | out_of_time | eq |  | unsupported |  |
| 131 | sensitivity | The out-of-time split provides the only quasi-scenario evide… | 20 | percent | cpr | out_of_time | eq |  | unsupported |  |
| 132 | findings | 1. *Calibration level failure (C1).* Predicted prepayment is… | 4.3 | ratio |  |  | eq |  | unsupported |  |
| 133 | findings | 1. *Calibration level failure (C1).* Predicted prepayment is… | 5.4 | ratio |  |  | eq |  | unsupported |  |
| 134 | findings | 2. *Probable loan reuse across splits (L2).* Split loan coun… | 2515 | count |  |  | eq |  | unsupported |  |
| 135 | findings | 2. *Probable loan reuse across splits (L2).* Split loan coun… | 1334 | count |  |  | eq |  | unsupported |  |
| 136 | findings | 4. *Calibration slope statistic is misleading (C1).* Report… | 0.856 | ratio | calibration_slope | vintage_holdout | eq |  | unsupported |  |
| 137 | findings | 5. *Unsupported extrapolation of the age ramp (X1).* The bas… | 102 | months |  |  | eq |  | unsupported |  |
| 138 | findings | 5. *Unsupported extrapolation of the age ramp (X1).* The bas… | 59 | months |  |  | eq |  | unsupported |  |
| 139 | findings | 6. *Drift undocumented and outcome drift large (S1).* Event… | 3.7 | ratio | event_rate |  | eq |  | unsupported |  |
| 140 | findings | 10. *Discrimination is stable out-of-sample (O1, information… | 0.0149 | ratio | delta_auc |  | eq |  | unsupported |  |
| 141 | findings | 10. *Discrimination is stable out-of-sample (O1, information… | 2 | count |  |  | eq |  | unsupported |  |
| 142 | monitoring | **Monthly.** Report actual versus predicted CPR at the total… | 0.85 | ratio |  |  | eq |  | unsupported |  |
| 143 | monitoring | **Monthly.** Report actual versus predicted CPR at the total… | 1.15 | ratio |  |  | eq |  | unsupported |  |
| 144 | monitoring | **Monthly.** Report actual versus predicted CPR at the total… | 0.75 | ratio |  |  | eq |  | unsupported |  |
| 145 | monitoring | **Monthly.** Report actual versus predicted CPR at the total… | 1.25 | ratio |  |  | eq |  | unsupported |  |
| 146 | monitoring | **Monthly.** Track score-distribution PSI and feature-level… | 0.1 | ratio | psi |  | eq |  | unsupported |  |
| 147 | monitoring | **Monthly.** Track score-distribution PSI and feature-level… | 0.25 | ratio | psi |  | eq |  | unsupported |  |
| 148 | monitoring | **Quarterly.** Report AUC, KS and the fixed-intercept calibr… | 12 | months |  |  | eq |  | unsupported |  |
| 149 | monitoring | **Quarterly.** Report AUC, KS and the fixed-intercept calibr… | 0.05 | ratio | auc |  | eq |  | unsupported |  |
| 150 | monitoring | **Quarterly.** Report AUC, KS and the fixed-intercept calibr… | 0.78 | ratio | auc |  | eq |  | unsupported |  |
| 151 | monitoring | **Quarterly.** Report AUC, KS and the fixed-intercept calibr… | 0.9 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 152 | monitoring | **Quarterly.** Report AUC, KS and the fixed-intercept calibr… | 1.1 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 153 | monitoring | **Quarterly.** Report actual versus predicted CPR disaggrega… | 0 | months |  |  | eq |  | unsupported |  |
| 154 | monitoring | **Quarterly.** Report actual versus predicted CPR disaggrega… | 12 | months |  |  | eq |  | unsupported |  |
| 155 | monitoring | **Quarterly.** Report actual versus predicted CPR disaggrega… | 13 | months |  |  | eq |  | unsupported |  |
| 156 | monitoring | **Quarterly.** Report actual versus predicted CPR disaggrega… | 24 | months |  |  | eq |  | unsupported |  |
| 157 | monitoring | **Quarterly.** Report actual versus predicted CPR disaggrega… | 25 | months |  |  | eq |  | unsupported |  |
| 158 | monitoring | **Quarterly.** Report actual versus predicted CPR disaggrega… | 36 | months |  |  | eq |  | unsupported |  |
| 159 | monitoring | **Quarterly.** Report actual versus predicted CPR disaggrega… | 37 | months |  |  | eq |  | unsupported |  |
| 160 | monitoring | **Quarterly.** Report actual versus predicted CPR disaggrega… | 59 | months |  |  | eq |  | unsupported |  |
| 161 | monitoring | **Quarterly.** Report actual versus predicted CPR disaggrega… | 60 | months |  |  | eq |  | unsupported |  |
| 162 | monitoring | **Quarterly.** Report actual versus predicted CPR disaggrega… | 60 | months |  |  | eq |  | unsupported |  |
| 163 | monitoring | **Semi-annual.** Refresh the seasoning ramp against accumula… | 100 | bp |  |  | eq |  | unattributed |  |
| 164 | monitoring | **Semi-annual.** Refresh the seasoning ramp against accumula… | 50 | bp |  |  | eq |  | unattributed |  |
| 165 | monitoring | **Semi-annual.** Refresh the seasoning ramp against accumula… | 0 | bp |  |  | eq |  | unsupported |  |
| 166 | monitoring | **Semi-annual.** Refresh the seasoning ramp against accumula… | 50 | count |  |  | eq |  | unattributed |  |
| 167 | monitoring | **Semi-annual.** Refresh the seasoning ramp against accumula… | 100 | count |  |  | eq |  | unattributed |  |
| 168 | monitoring | **Semi-annual.** Refresh the seasoning ramp against accumula… | 200 | bp |  |  | eq |  | unsupported |  |

## Appendix B — Artifact index

The store holds 19 artifacts; the 16 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `run.data_out_of_time` | `7ddcc721` | table | table, 12257 rows | the subject's data_out_of_time.csv |
| `run.data_test` | `f0ac9fe8` | table | table, 15382 rows | the subject's data_test.csv |
| `run.data_train` | `0356ef50` | table | table, 36013 rows | the subject's data_train.csv |
| `run.data_vintage_holdout` | `940d14da` | table | table, 32177 rows | the subject's data_vintage_holdout.csv |
| `run.features` | `61276a96` | json | json | the subject's features.json |
| `run.metrics` | `03ed7db3` | json | json | the subject's metrics.json |
| `run.model_summary` | `a65c5723` | json | json | the subject's model_summary.json |
| `run.predictions_out_of_time` | `848a1341` | table | table, 12257 rows | the subject's predictions_out_of_time.csv |
| `run.predictions_test` | `48b8c85f` | table | table, 15382 rows | the subject's predictions_test.csv |
| `run.predictions_train` | `e0c35654` | table | table, 36013 rows | the subject's predictions_train.csv |
| `run.predictions_vintage_holdout` | `40b64ebe` | table | table, 32177 rows | the subject's predictions_vintage_holdout.csv |
| `run.projection` | `f7fe5a1a` | json | json | the subject's projection.json |
| `run.splits` | `dca79f2f` | json | json | the subject's splits.json |
| `run.status` | `5c222bcc` | json | json | how the subject's subprocess ended |
| `run.stderr` | `41728c38` | json | json | the subject's stderr |
| `run.stdout` | `fb0d94c5` | json | json | the subject's stdout |

## Appendix C — Run trace summary

| quantity | value |
|---|---|
| tool calls | 1 (run_model 1) |
| plan steps (bounded loop) | 0 |
| LLM calls | 8 (plain_llm 1, extract 7) |
| re-asks | 0 |
| repair rounds | 0 |
| tokens in / out | 63,791 / 40,601 |
| notional cost (USD) | 1.6467 |
| wall-clock (s) | 472.50 |
| subject run (s) | 2.39 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | msr_prepayment-plain_llm-20260918T212241Z-986f3824 |

## Appendix D — Not checked

| item | reason |
|---|---|
| `check_stability` (R1) | this configuration runs no checks |
| `run_scenarios` (X1) | this configuration runs no checks |
| developer claims (T1, claim channel) | `plain_llm` runs no check over `package.yaml`'s declared claims |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
| every check of spec 3.7 but `run_model` | `plain_llm` runs the subject and one model call, by design |
