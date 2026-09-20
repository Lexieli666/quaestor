---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: msr_prepayment
version: "1.0"
model_type: discrete_time_hazard
configuration: plain_llm
model: claude-opus-5[1m]
run_id: msr_prepayment-plain_llm-20260918T215755Z-986f3824
data_mode: synthetic
synthetic_n: 2000
grounding_precision_pre: 0.0000
grounding_precision_post: 0.0000
n_claims: 144
n_findings_by_severity: {high: 3, medium: 4, low: 2, info: 1}
generated: "2026-09-18T21:57:55Z"
illustrative: false
---

# Validation report — `msr_prepayment` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `msr_prepayment` v1.0 | `plain_llm` | claude-opus-5[1m] | synthetic, n = 2000 | 0.0000 → 0.0000 | 3 / 4 / 2 / 1 |
<!-- quaestor:renderer:end -->

This report covers validation of `msr_prepayment` v1.0, a discrete-time hazard model of voluntary prepayment used to project cash flows for mortgage servicing rights. The review is based exclusively on the artifacts registered by the subject run: the metrics file [[art:0ed16a42:run.metrics]], the model summary [[art:cf58dded:run.model_summary]], the feature manifest [[art:61276a96:run.features]], the split manifest [[art:53221637:run.splits]], the raw training profile [[art:f3a0b7f4:plain_llm.profile]], the four scored prediction tables ([[art:dcc88ba4:run.predictions_train]], [[art:90b547ad:run.predictions_test]], [[art:a7e53ac8:run.predictions_out_of_time]], [[art:a7e53ac8:run.predictions_vintage_holdout]] as registered), and the projection output [[art:9fcedb3d:run.projection]].

The model is a monthly hazard specification with twelve covariates and a spline in loan age (knots at ⟦unverified: 2,⟧ ⟦unverified: 13,⟧ ⟦unverified: 26,⟧ ⟦unverified: 39⟧ and ⟦unverified: 55⟧ months). Discrimination is reasonable and stable — AUC ⟦unverified: 0.800⟧ in train, ⟦unverified: 0.785⟧ in test, ⟦unverified: 0.772⟧ in the vintage holdout — and the reported CPR figures reconcile exactly to the reported monthly SMM means under the standard annualisation, so the metric plumbing is internally consistent.

The conclusions are nonetheless adverse. Three issues are material enough to block use as-is. First, the split registered as `out_of_time` is a byte-identical copy of `test` (identical `rows_hash`, identical row count, identical metrics to ten decimal places), so the model has never been evaluated on a genuine out-of-time sample despite the report structure claiming one. Second, the model over-predicts prepayment by roughly ⟦unverified: 24⟧–⟦unverified: 28%⟧ on every split it did not fit, in the same direction on both, which is a level error that flows directly into MSR value. Third, the baseline hazard is tabulated out to loan age ⟦unverified: 101⟧+ months from training data whose maximum observed loan age is ⟦unverified: 59⟧ months, and the extrapolated tail decays toward zero — the region of the curve that the valuation depends on most is the region with no data behind it.

Scope limits worth stating plainly: the model summary available to this review is truncated inside the `baseline_hazard` array, so the fitted coefficient vector was not inspectable and no regime-by-regime sign stability test could be run. No challenger model, no PSI computation, no VIF or condition-number diagnostic, and no developer-declared performance thresholds appear anywhere in the artifact store. Those absences are themselves findings, but they also mean several standard tests could not be executed rather than executed and passed.

## 2. Conceptual soundness

The specification is recognisable as a conventional prepayment hazard model and the broad shape is defensible. The covariate set in [[art:61276a96:run.features]] contains the expected drivers: refinance incentive, burnout, spread at origination (SATO), note rate, original LTV, credit score, loan size, current balance, a twelve-month rate change, loan age, and a sine/cosine seasonality pair. The feature timing declarations are clean: five features are `at_origination`, seven are `before_period_start`, and zero are declared `after_outcome` or `during_period`. On the declared timing alone there is no forward-looking covariate, and the counts reconcile (⟦unverified: 5⟧ + ⟦unverified: 7⟧ = ⟦unverified: 12⟧ = `n`). Because per-feature univariate discrimination was not published, the complementary leakage test — a single covariate achieving implausibly high standalone AUC — could not be run, so leakage is unrefuted rather than affirmatively cleared.

The age spline is the weak point. Knots sit at ⟦unverified: 2,⟧ ⟦unverified: 13,⟧ ⟦unverified: 26,⟧ ⟦unverified: 39⟧ and ⟦unverified: 55⟧ months, and the training data in [[art:f3a0b7f4:plain_llm.profile]] has `loan_age` ranging ⟦unverified: 0⟧ to ⟦unverified: 59⟧ with a mean of ⟦unverified: 26.9⟧. Only about four months of observed data sit beyond the final knot, which means the terminal basis function is estimated from a sliver of the sample and then relied upon for every projection month thereafter. The tabulated baseline in [[art:cf58dded:run.model_summary#baseline_hazard]] rises from ⟦unverified: 0.00109⟧ at age ⟦unverified: 0⟧ to a peak of ⟦unverified: 0.00410⟧ at age ⟦unverified: 39,⟧ then declines monotonically to ⟦unverified: 0.000349⟧ by age ⟦unverified: 101⟧ — roughly ⟦unverified: 8.5%⟧ of peak. A seasoning ramp followed by a plateau is the standard empirical pattern; a ramp followed by sustained decay toward zero is not, and it implies that a well-seasoned, deeply in-the-money loan is nearly incapable of prepaying. This is discussed further in section 5.

A second conceptual concern is redundancy in the rate block. `note_rate`, `sato`, `incentive`, and `rate_change_12m` are not independent constructs: SATO is the note rate net of the prevailing rate at origination, incentive is the note rate net of the current prevailing rate, and the twelve-month rate change is very nearly the difference between those two over a one-year window. Fitting all four alongside one another is close to fitting a linear dependency, which does not necessarily harm aggregate prediction but does make individual coefficients unstable and their signs uninterpretable — a problem for a model whose scenario behaviour is supposed to be explainable to a valuation committee. No VIF or condition number was published to bound this.

Finally, the relationship between the published baseline hazard and the observed event rates is not documented. Peak baseline hazard is ⟦unverified: 0.0041⟧ per month, while the observed train-period mean SMM is ⟦unverified: 0.0083⟧ and the test-period mean is ⟦unverified: 0.0179⟧ — implying that the covariate multipliers routinely carry a factor of two to four. That is arithmetically possible if the baseline is evaluated at covariate zeros rather than at sample means, but the artifact does not say which convention applies, and a reader could easily misread the tabulated curve as a standalone prepayment vector.

## 3. Data integrity and drift

The raw training profile reports zero missing values in every column, and the ranges are plausible throughout: note rate ⟦unverified: 2.285⟧–⟦unverified: 6.384⟧, original LTV ⟦unverified: 43⟧–⟦unverified: 97,⟧ credit score ⟦unverified: 620⟧–⟦unverified: 820,⟧ log original UPB ⟦unverified: 10.65⟧–⟦unverified: 13.36⟧, incentive −⟦unverified: 3.12⟧ to +⟦unverified: 3.17⟧, burnout ⟦unverified: 0⟧ to ⟦unverified: 9.32⟧. The seasonality pair has means near zero and standard deviations near ⟦unverified: 0.707⟧, exactly as a sine/cosine encoding of month should. The observation window runs from ⟦unverified: 201402⟧ to ⟦unverified: 201912⟧. Nothing in the univariate profile suggests corrupted or imputed data.

Two integrity problems sit above that clean surface.

The first is the duplicate split. [[art:53221637:run.splits]] gives `test` and `out_of_time` the same `rows_hash` of `c64c3f16…`, the same ⟦unverified: 12,257⟧ rows, the same ⟦unverified: 515⟧ loans, and the same event rate of ⟦unverified: 0.017949⟧; [[art:0ed16a42:run.metrics]] then reports identical AUC, Brier, calibration slope, KS, logloss, and both CPR figures for the two. These are not two similar samples, they are one sample recorded twice. Any statement in model documentation that the model was validated out-of-time is, on this evidence, unsupported.

The second is a reconciliation break between the feature manifest and the data. [[art:61276a96:run.features]] declares `bom_balance_log` and `rate_change_12m` as model inputs, but neither column appears in the training profile [[art:f3a0b7f4:plain_llm.profile]], which otherwise lists every one of the remaining ten features plus `loan_id`, `period`, and the `prepaid` target. Either the profile is materially incomplete, or the model was scored using columns that are not in the registered training data. Both readings require resolution before the model can be certified, and the second would be disqualifying.

On drift: the splits are not exchangeable. Event rates are ⟦unverified: 0.00832⟧ in train, ⟦unverified: 0.01795⟧ in test/out-of-time, and ⟦unverified: 0.00482⟧ in the vintage holdout — a ⟦unverified: 2.2⟧x increase from train to test and a ⟦unverified: 3.7⟧x spread across the three. Mean predicted hazard tracks the same pattern (⟦unverified: 0.00833⟧, ⟦unverified: 0.02283⟧, ⟦unverified: 0.00616⟧), so the score distribution itself has shifted by a factor of nearly three between the fitting sample and the evaluation sample. A training window ending in December ⟦unverified: 2019⟧ and a test window with a ⟦unverified: 19.5%⟧ actual CPR is the signature of a model fit before a refinance wave and evaluated inside one. No PSI was computed on either the covariates or the scores, so the drift is visible in the aggregates but unquantified at the distributional level where it matters.

Sample size deserves a note even though it is not a defect class. The three splits cover roughly ⟦unverified: 1,848⟧ loan-records in total (⟦unverified: 667⟧ train, ⟦unverified: 666⟧ vintage holdout, ⟦unverified: 515⟧ test), and the event counts are approximately ⟦unverified: 279,⟧ ⟦unverified: 155,⟧ and ⟦unverified: 220⟧ respectively. Metrics computed on ⟦unverified: 33,522⟧ and ⟦unverified: 12,257⟧ loan-months look precise, but loan-months from one loan are strongly correlated; the effective sample is closer to the loan count than the row count, and every confidence interval implied by these metrics is narrower than it should be.

## 4. Outcomes analysis

Discrimination holds up. AUC is ⟦unverified: 0.8003⟧ in train, ⟦unverified: 0.7846⟧ in test, and ⟦unverified: 0.7716⟧ in the vintage holdout (Gini ⟦unverified: 0.601⟧, ⟦unverified: 0.569⟧, ⟦unverified: 0.543⟧; KS ⟦unverified: 0.474⟧, ⟦unverified: 0.437⟧, ⟦unverified: 0.462⟧). The train-to-test gap of ⟦unverified: 0.016⟧ and the train-to-holdout gap of ⟦unverified: 0.029⟧ are small for a model of this type and do not indicate overfitting of the rank ordering. Brier and logloss differ substantially across splits (⟦unverified: 0.0081⟧/⟦unverified: 0.0428⟧ in train versus ⟦unverified: 0.0173⟧/⟦unverified: 0.0805⟧ in test), but that is almost entirely the base-rate difference rather than a quality difference, and should not be read as degradation.

Calibration is where the model fails. On test, predicted CPR is ⟦unverified: 0.2420⟧ against actual ⟦unverified: 0.1953⟧ — over-prediction of ⟦unverified: 23.9%⟧. In monthly terms, mean predicted hazard is ⟦unverified: 0.022827⟧ against an observed event rate of ⟦unverified: 0.017949⟧, over-prediction of ⟦unverified: 27.2%⟧. The vintage holdout shows the same error in the same direction and of nearly the same magnitude: predicted CPR ⟦unverified: 0.0714⟧ against actual ⟦unverified: 0.0563⟧ (+⟦unverified: 26.9%⟧), mean predicted ⟦unverified: 0.006157⟧ against an event rate of ⟦unverified: 0.004817⟧ (+⟦unverified: 27.8%⟧). Train calibration is essentially perfect (slope ⟦unverified: 1.015⟧, mean predicted ⟦unverified: 0.008333⟧ against an event rate ⟦unverified: 0.008323⟧), which confirms the fit converged and localises the problem to generalisation rather than estimation.

The calibration slopes add a second layer. Test slope is ⟦unverified: 0.9369⟧, marginally inside a conventional ⟦unverified: 0.9⟧–⟦unverified: 1.1⟧ acceptance band; vintage holdout slope is ⟦unverified: 0.8554⟧, outside it. A slope below one alongside a mean prediction well above the observed rate indicates both an intercept error and compression — the model is too aggressive overall, and disproportionately so in the high-score tail where the most prepayment-prone loans sit. For MSR valuation this is the adverse direction on both counts: it understates servicing asset value and understates the duration of the servicing cash flows.

Because `out_of_time` duplicates `test`, the vintage holdout is the only evaluation sample that is genuinely distinct from the test sample, and it is the one on which calibration is worst. There is no third, independent read to arbitrate.

Effective challenge was not performed. The artifact store contains no challenger metrics, no benchmark model, and no comparison of any kind against a simpler alternative — not even an S-curve or a static PSA-style vector, either of which would be a fair baseline for a twelve-covariate hazard model. Absent that, the ⟦unverified: 0.78⟧ AUC has no reference point: it is not known whether the covariate machinery earns its complexity over a much simpler specification.

## 5. Sensitivity and scenario analysis

No formal scenario grid — parallel rate shocks, incentive sweeps, or a value-versus-rate curve — appears in the artifact store, so sensitivity behaviour must be inferred from the fitted baseline and the feature set. That inference raises one substantive concern.

The baseline hazard in [[art:cf58dded:run.model_summary#baseline_hazard]] is non-monotone by construction: it ramps from ⟦unverified: 0.00109⟧ at age ⟦unverified: 0⟧ to a maximum of ⟦unverified: 0.00410⟧ at age ⟦unverified: 39,⟧ and then declines continuously for every month thereafter — ⟦unverified: 0.00260⟧ at age ⟦unverified: 55,⟧ ⟦unverified: 0.00161⟧ at age ⟦unverified: 66,⟧ ⟦unverified: 0.00109⟧ at age ⟦unverified: 75⟧ (back to the age-zero level), ⟦unverified: 0.000495⟧ at age ⟦unverified: 93,⟧ and ⟦unverified: 0.000349⟧ at age ⟦unverified: 101,⟧ with the tabulation continuing beyond. The ramp is correct and expected. The decay is not supported by data: training `loan_age` maxes out at ⟦unverified: 59⟧ months, so every value from month ⟦unverified: 60⟧ onward is spline extrapolation, and the last knot at ⟦unverified: 55⟧ means the extrapolation is governed by a basis function fitted on the thinnest part of the sample.

The consequence for MSR is direct and one-directional. A servicing asset's value is dominated by how long the loan survives, and a hazard that decays toward zero in the seasoned years produces long survival, long cash-flow tails, and inflated value — while simultaneously making the asset look insensitive to rate rallies at exactly the ages where the book will spend most of its life. The projection in [[art:9fcedb3d:run.projection]] inherits this shape wholesale. In combination with the calibration error from section 4, which pushes value the other way in the early months, the net bias on any given cohort is not predictable from the artifacts and could be large in either direction.

Sign and stability testing across rate regimes could not be performed. The coefficient vector is not visible in the available portion of the model summary, so it was not possible to check whether `incentive`, `sato`, or `burnout` retain their expected signs when the model is refit within the pre-⟦unverified: 2020⟧ and post-⟦unverified: 2020⟧ windows separately. Given that the test sample sits in a materially different rate regime from the training sample, this test is exactly the one most worth running, and it remains open. Discrimination at least does not collapse across regimes — AUC moves only from ⟦unverified: 0.800⟧ to ⟦unverified: 0.785⟧ — which is mild evidence against gross instability in the rank ordering, but says nothing about coefficient-level stability or about level accuracy, which has already failed.

## 6. Findings and recommendations

Ten findings are recorded below in the structured list, three at high severity.

The duplicate `out_of_time` split should be rebuilt first, because it conditions everything else: until a genuinely disjoint out-of-time sample exists, there is no evidence on which the model's forward performance can be assessed, and the current documentation overstates the validation that was done. The rebuilt split should be disjoint in both time and loan identity from train.

The calibration error should be remediated rather than merely disclosed. A recalibration of the hazard intercept on a recent window is the minimum; given the holdout slope of ⟦unverified: 0.855⟧, a slope correction or a refit with regime-aware terms is likely also needed. Recalibration should be validated on a sample not used to fit the correction.

The age-spline tail should be constrained. Extending knots to the limit of observed age (⟦unverified: 59⟧ months) and imposing a flat or gently declining plateau beyond it — rather than allowing free spline extrapolation to month ⟦unverified: 101⟧ and beyond — would remove the unsupported decay. If the servicing book contains loans materially older than ⟦unverified: 59⟧ months, the training window should be extended to cover them rather than relying on extrapolation.

The feature-manifest reconciliation break should be resolved by confirming, against the source data, whether `bom_balance_log` and `rate_change_12m` were actually available at scoring time. Alongside that, VIF or condition-number diagnostics should be published for the correlated rate block, and a challenger model should be fit and compared so that the champion's complexity is justified against an explicit alternative.

Recommended disposition: the model should not be approved for production MSR valuation in its current form. The combination of an absent out-of-time test, a ~⟦unverified: 27%⟧ level bias, and an unsupported hazard tail in the region that drives valuation is sufficient to withhold approval pending remediation of the three high-severity findings and re-validation.

### F-001 · D1 data integrity · severity **high**

run.splits registers `test` and `out_of_time` with the same rows_hash (c64c3f16...), the same 12,257 rows, the same 515 loans, and the same event rate of 0.017949. run.metrics then reports identical values for both splits on every single measure to ten decimal places: AUC 0.7846182604, Brier 0.01725186302, calibration slope 0.9368866216, KS 0.4373216673, logloss 0.08050056271, cpr_actual 0.1953465213, cpr_predicted 0.2420168196, mean_predicted 0.02282661269. These are not two samples that happen to agree; they are one sample registered under two names. The practical consequence is that the model has never been evaluated on a genuine out-of-time hold-back, and the only evaluation sample truly distinct from `test` is `vintage_holdout`, which is also the sample on which calibration is worst. Any documentation asserting that out-of-time performance was tested is unsupported by the artifacts. A disjoint out-of-time split, separated from train in both time and loan identity, must be constructed and the evaluation rerun before any performance conclusion can stand.

### F-002 · C1 calibration · severity **high**

Calibration fails in the same direction and at nearly the same magnitude on every sample the model did not fit. On test, predicted CPR is 0.2420168 against an actual of 0.1953465, an over-prediction of 23.9%; in monthly terms mean predicted hazard is 0.02282661 against an observed event rate of 0.01794893, an over-prediction of 27.2%. On the vintage holdout, predicted CPR is 0.0714378 against actual 0.0562981 (+26.9%) and mean predicted 0.00615746 against an event rate of 0.00481711 (+27.8%). Train calibration is by contrast essentially exact (slope 1.0151657, mean predicted 0.00833286 against event rate 0.00832289), which confirms the fit converged and localises the failure to generalisation. The calibration slopes compound the problem: 0.9369 on test is marginally inside a conventional 0.90-1.10 band, but 0.8554 on the vintage holdout is outside it. A sub-unit slope combined with a mean prediction well above the observed rate implies both an intercept error and compression, with the largest absolute errors falling in the high-score tail where the most prepayment-prone loans sit. For an MSR application this biases the servicing asset downward and understates cash-flow duration. Recalibration of the intercept on a recent window is the minimum remedy; the holdout slope indicates a slope correction or a regime-aware refit is likely also required, validated on a sample not used to fit the correction.

### F-003 · X1 scenario analysis · severity **high**

The tabulated baseline in run.model_summary ramps from 0.001085 at loan age 0 to a peak of 0.004096 at age 39, then declines monotonically for every subsequent month: 0.002600 at age 55, 0.001609 at age 66, 0.001086 at age 75 (back to its age-zero level), 0.000495 at age 93, and 0.000349 at age 101, continuing beyond. The training data in the raw profile has loan_age ranging only 0 to 59 with a mean of 26.9, and the final spline knot sits at 55. Every hazard value from month 60 onward is therefore pure extrapolation, governed by a basis function estimated on roughly four months of thin data. The resulting shape is not merely uncertain, it is the wrong shape: the standard empirical pattern for voluntary prepayment is a seasoning ramp followed by a plateau, not a ramp followed by decay toward zero. As specified, a well-seasoned and deeply in-the-money loan is treated as nearly incapable of prepaying. Because MSR value is dominated by how long the loan survives, this inflates projected cash-flow tails and makes the asset look insensitive to rate rallies precisely at the ages where the book spends most of its life; the projection artifact inherits the shape wholesale. The remedy is to extend knots to the limit of observed age and impose a flat or gently declining plateau beyond the data, or to extend the training window to cover the seasoned ages the servicing book actually contains rather than extrapolating into them.

### F-004 · D1 data integrity · severity **medium**

run.features declares twelve model inputs, among them `bom_balance_log` and `rate_change_12m`, both typed float64 and both timed `before_period_start`. Neither column appears anywhere in the raw training profile, which does list all ten of the other declared features (note_rate, orig_ltv, credit_score, orig_upb_log, sato, loan_age, incentive, burnout, season_sin, season_cos) plus loan_id, period, and the prepaid target, each with zero missingness. The omission of exactly two of twelve, with everything else reconciling cleanly, is a genuine break rather than a formatting artifact. Only two readings are available: either the profile is materially incomplete and does not describe the data actually used, or the model was scored on columns absent from the registered training data. The first undermines the reliability of the data documentation this validation rests on; the second would be disqualifying, since a sixth of the covariate set would then have unknown provenance and unknown timing relative to the outcome. This must be reconciled against the source data before certification, and the timing of both features re-confirmed, since a balance or rate-change field constructed carelessly is a common leakage vector.

### F-005 · L2 contamination · severity **medium**

run.splits reports 667 loans in train and 666 in vintage_holdout, against 515 in test. The raw training profile shows loan_id spanning 1 to 667 with a mean of 331.7, consistent with a contiguous identifier range covering essentially the entire loan population. A holdout containing 666 of 667 loans is not plausibly a disjoint set of borrowers; the far more likely construction is a time-based partition in which the same loans contribute loan-months to both train and holdout. The rows_hash values differ (546177c8 for train, 34ba776e for vintage_holdout) so the rows themselves are distinct, which is why this is recorded as a loan-level rather than row-level overlap. The consequence is still material: loan-months from a single loan share the same origination characteristics, the same borrower, and strongly correlated covariate paths, so a holdout drawn from the same loans measures within-loan temporal generalisation only and systematically overstates performance on genuinely unseen borrowers. This also compounds the effective-sample-size problem, since the roughly 155 holdout events are drawn from loans the model has already seen. Split assignment should be made disjoint at the loan_id level, and the reported metrics recomputed on that basis.

### F-006 · S1 population drift · severity **medium**

The three splits are not exchangeable. Event rates are 0.0083229 in train, 0.0179489 in test/out_of_time, and 0.0048171 in the vintage holdout: a 2.2x increase from train to test and a 3.7x spread across the three. The score distribution shifts in step, with mean predicted hazard moving from 0.0083329 in train to 0.0228266 in test and 0.0061575 in the holdout, a factor of nearly three between the fitting sample and the test sample. The training window closes at period 201912 and the test sample exhibits a 19.5% actual CPR, the signature of a model estimated before a refinance wave and evaluated inside one. This is precisely the condition under which a prepayment model's level accuracy degrades, and it is consistent with the calibration failure recorded separately. No population stability index was computed on either the covariates or the predicted scores, so the drift is visible only in the split-level aggregates and remains unquantified at the distributional level where a threshold could be applied. PSI should be computed for every covariate and for the score against the training reference, with conventional 0.10 amber and 0.25 red thresholds, both retrospectively across these splits and on an ongoing quarterly basis.

### F-007 · M1 collinearity · severity **medium**

The feature manifest includes note_rate, sato, incentive, and rate_change_12m as four separate inputs, but these are near-deterministic functions of one another. SATO is the note rate net of the prevailing market rate at origination, incentive is the note rate net of the current prevailing rate, and the twelve-month rate change is approximately the difference between those two quantities over a one-year window. Fitting all four simultaneously approaches fitting a linear dependency. The training profile is consistent with this: note_rate has mean 4.564 and standard deviation 0.655, sato mean 0.284 and standard deviation 0.378, and incentive mean 0.296 and standard deviation 0.973, with the sato and incentive means nearly identical as would be expected if they differ mainly by a common rate-level term. No variance inflation factor, condition number, or correlation matrix was published anywhere in the artifact store, so the severity of the dependency is unbounded. Aggregate predictive accuracy may be unaffected, but individual coefficients become unstable and their signs uninterpretable, which directly undermines the scenario explanations a valuation committee needs and makes the model fragile to refitting on a new rate regime. VIF and condition number should be computed and published, and the rate block reduced or orthogonalised if they breach the usual thresholds.

### F-008 · O1 out-of-sample degradation · severity **low**

AUC falls from 0.8002919 in train to 0.7846183 in test, a gap of 0.0157, and to 0.7716058 in the vintage holdout, a gap of 0.0287. Gini follows the same ordering (0.6005838, 0.5692365, 0.5432116). Both gaps are well within a conventional 0.05 tolerance and do not indicate overfitting of the rank ordering, which is the reason this is recorded at low severity rather than higher. It is recorded at all because the decay is monotone in the direction of increasing distance from the fitting sample and because the holdout, being the only sample genuinely distinct from test, is the one that degrades most. The larger differences in Brier (0.0081114 train versus 0.0172519 test) and logloss (0.0427936 versus 0.0805006) should not be read as additional degradation: they are driven almost entirely by the difference in base rate between the splits, since the test event rate is 2.2x the train rate. Discrimination is the one dimension on which this model performs acceptably, and the finding should not be allowed to obscure that the failure is in calibration rather than ranking.

### F-009 · T1 declared threshold · severity **low**

Nothing in the registered artifacts states what performance the developer claimed or what thresholds the model was expected to meet. run.model_summary contains the fitted structure only, and run.status, run.stdout, and run.stderr carry no acceptance criteria for discrimination, calibration, CPR tracking error, or stability. In consequence no threshold-breach test could be executed: the calibration errors of 23.9% and 26.9% on predicted versus actual CPR, and the vintage holdout calibration slope of 0.8554, are judged in this report against conventional industry bands rather than against anything the developer committed to. This is a documentation gap rather than a modelling error, but it is a governance-relevant one, because it means there is no pre-declared standard against which a future monitoring breach could be adjudicated, and it leaves the validator setting the bar after the results are known. Explicit thresholds should be documented for CPR tracking error, calibration slope, AUC floor, and covariate and score PSI before the model is resubmitted, and those thresholds should be the ones the ongoing monitoring program in section 7 enforces.

### F-010 · E1 effective challenge · severity **info**

The artifact store contains no challenger metrics, no benchmark specification, and no comparison of the champion against any alternative. run.metrics reports a single model across four splits and nothing else, and run.model_summary describes only the champion hazard specification. For a twelve-covariate discrete-time hazard model with a five-knot age spline, the natural comparators are cheap and standard: a simple S-curve in refinance incentive, a static PSA-style vector, or a logistic model on a reduced covariate set. Without at least one such comparison, the reported AUC of 0.785 has no reference point, and it cannot be established that the covariate machinery and the spline earn their complexity over a materially simpler and more stable alternative. This is recorded as informational rather than as a breach because no challenger was beaten; the point is that none was attempted. A challenger should be fit and compared before approval, and refit annually thereafter as part of the monitoring cycle.

Candidates raised and not promoted: none.

### Open items

No open item was recorded for this validation.

## 7. Ongoing monitoring recommendations

Once the high-severity items are remediated, the following monitoring program is recommended, and should be documented with explicit thresholds — none currently exist, which is itself a finding.

Monthly, compare actual to predicted CPR at the total-portfolio level and within cohort buckets defined by incentive and by loan age. An amber trigger at ±⟦unverified: 10%⟧ relative error and a red trigger at ±⟦unverified: 20%⟧ would have caught the current ⟦unverified: 24⟧–⟦unverified: 28%⟧ bias immediately. Report the monthly SMM mean alongside the annualised CPR so that the two remain reconcilable.

Quarterly, recompute the calibration slope and intercept on a rolling twelve-month window, with an amber band of ⟦unverified: 0.90⟧–⟦unverified: 1.10⟧ on the slope and escalation outside ⟦unverified: 0.85⟧–⟦unverified: 1.15⟧. Recompute AUC, Gini, and KS on the same window and trigger review on a drop of more than ⟦unverified: 0.05⟧ from the validation-period AUC of ⟦unverified: 0.785⟧.

Quarterly, compute PSI on every model covariate and on the predicted score distribution against the training reference, with the conventional ⟦unverified: 0.10⟧ amber and ⟦unverified: 0.25⟧ red thresholds. The ⟦unverified: 2.7⟧x shift in mean predicted score already observed between train and test would have breached any such threshold, and score PSI is the single most informative early warning for this model given its rate-regime sensitivity.

Annually, or on any red trigger, refit and compare against a challenger to confirm the champion still earns its complexity, and re-examine coefficient signs on `incentive`, `sato`, and `burnout` within the most recent regime. Also annually, reconcile the realised prepayment experience of seasoned cohorts against the extrapolated portion of the age curve, since that is the part of the model with no data behind it and it will only be testable as the book ages.

Operationally, add a pre-run assertion that split `rows_hash` values are pairwise distinct and that loan identifiers do not intersect across train and holdout, so that the duplicate-split defect cannot recur silently. Record and monitor run duration against [[art:2ad8d1a5:runtime.max_seconds]]; the registered duration [[art:04b9b5f2:run.duration_s]] and the run status [[art:5c222bcc:run.status]] were not inspectable in this review, so no conclusion is drawn about runtime compliance in either direction.

## Appendix A — Claims

Grounding precision 0.0000 before repair (0 of 144 claims verified; 116 unsupported, 27 dangling, 1 unattributed) and 0.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 0/12; conceptual_soundness 0/21; data_integrity 0/37; outcomes 0/35; sensitivity 0/21; findings 0/5; monitoring 0/13.

Developer claims: `plain_llm` runs no check over `package.yaml`'s declared claims See Appendix D.

Excluded numeric tokens (not claims): section_number (section 5, section 4); citation_hash (0ed16a42, cf58dded, 61276a96, 53221637); extractor_returned_excluded_token (1.0, 5, 12.0, -3.12).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The model is a monthly hazard specification with twelve cova… | 2 | months |  |  | eq |  | unsupported |  |
| 2 | summary | The model is a monthly hazard specification with twelve cova… | 13 | months |  |  | eq |  | unsupported |  |
| 3 | summary | The model is a monthly hazard specification with twelve cova… | 26 | months |  |  | eq |  | unsupported |  |
| 4 | summary | The model is a monthly hazard specification with twelve cova… | 39 | months |  |  | eq |  | unsupported |  |
| 5 | summary | The model is a monthly hazard specification with twelve cova… | 55 | months |  |  | eq |  | unsupported |  |
| 6 | summary | The model is a monthly hazard specification with twelve cova… | 0.8 | ratio | auc | train | eq |  | unsupported |  |
| 7 | summary | The model is a monthly hazard specification with twelve cova… | 0.785 | ratio | auc | test | eq |  | unsupported |  |
| 8 | summary | The model is a monthly hazard specification with twelve cova… | 0.772 | ratio | auc | vintage_holdout | eq |  | unsupported |  |
| 9 | summary | The conclusions are nonetheless adverse. Three issues are ma… | 24 | percent |  |  | eq |  | unsupported |  |
| 10 | summary | The conclusions are nonetheless adverse. Three issues are ma… | 28 | percent |  |  | eq |  | unsupported |  |
| 11 | summary | The conclusions are nonetheless adverse. Three issues are ma… | 101 | months |  |  | eq |  | unsupported |  |
| 12 | summary | The conclusions are nonetheless adverse. Three issues are ma… | 59 | months |  | train | eq |  | unsupported |  |
| 13 | conceptual_soundness | The specification is recognisable as a conventional prepayme… | 5 | count |  |  | eq |  | unsupported |  |
| 14 | conceptual_soundness | The specification is recognisable as a conventional prepayme… | 7 | count |  |  | eq |  | unsupported |  |
| 15 | conceptual_soundness | The specification is recognisable as a conventional prepayme… | 12 | count |  |  | eq |  | unsupported |  |
| 16 | conceptual_soundness | The age spline is the weak point. Knots sit at 2, 13, 26, 39… | 2 | months |  |  | eq |  | unsupported |  |
| 17 | conceptual_soundness | The age spline is the weak point. Knots sit at 2, 13, 26, 39… | 13 | months |  |  | eq |  | unsupported |  |
| 18 | conceptual_soundness | The age spline is the weak point. Knots sit at 2, 13, 26, 39… | 26 | months |  |  | eq |  | unsupported |  |
| 19 | conceptual_soundness | The age spline is the weak point. Knots sit at 2, 13, 26, 39… | 39 | months |  |  | eq |  | unsupported |  |
| 20 | conceptual_soundness | The age spline is the weak point. Knots sit at 2, 13, 26, 39… | 55 | months |  |  | eq |  | unsupported |  |
| 21 | conceptual_soundness | The age spline is the weak point. Knots sit at 2, 13, 26, 39… | 0 | months |  | train | eq | `[[art:f3a0b7f4:plain_llm.profile]]` | dangling |  |
| 22 | conceptual_soundness | The age spline is the weak point. Knots sit at 2, 13, 26, 39… | 59 | months |  | train | eq | `[[art:f3a0b7f4:plain_llm.profile]]` | dangling |  |
| 23 | conceptual_soundness | The age spline is the weak point. Knots sit at 2, 13, 26, 39… | 26.9 | months |  | train | eq | `[[art:f3a0b7f4:plain_llm.profile]]` | dangling |  |
| 24 | conceptual_soundness | The age spline is the weak point. Knots sit at 2, 13, 26, 39… | 0.00109 | ratio | baseline_hazard |  | eq | `[[art:cf58dded:run.model_summary#baseline_hazard]]` | dangling |  |
| 25 | conceptual_soundness | The age spline is the weak point. Knots sit at 2, 13, 26, 39… | 0 | months | baseline_hazard |  | eq | `[[art:cf58dded:run.model_summary#baseline_hazard]]` | dangling |  |
| 26 | conceptual_soundness | The age spline is the weak point. Knots sit at 2, 13, 26, 39… | 0.0041 | ratio | baseline_hazard |  | eq | `[[art:cf58dded:run.model_summary#baseline_hazard]]` | dangling |  |
| 27 | conceptual_soundness | The age spline is the weak point. Knots sit at 2, 13, 26, 39… | 39 | months | baseline_hazard |  | eq | `[[art:cf58dded:run.model_summary#baseline_hazard]]` | dangling |  |
| 28 | conceptual_soundness | The age spline is the weak point. Knots sit at 2, 13, 26, 39… | 0.000349 | ratio | baseline_hazard |  | eq | `[[art:cf58dded:run.model_summary#baseline_hazard]]` | dangling |  |
| 29 | conceptual_soundness | The age spline is the weak point. Knots sit at 2, 13, 26, 39… | 101 | months | baseline_hazard |  | eq | `[[art:cf58dded:run.model_summary#baseline_hazard]]` | dangling |  |
| 30 | conceptual_soundness | The age spline is the weak point. Knots sit at 2, 13, 26, 39… | 8.5 | percent | baseline_hazard |  | eq | `[[art:cf58dded:run.model_summary#baseline_hazard]]` | dangling |  |
| 31 | conceptual_soundness | Finally, the relationship between the published baseline haz… | 0.0041 | ratio | baseline_hazard |  | eq |  | unsupported |  |
| 32 | conceptual_soundness | Finally, the relationship between the published baseline haz… | 0.0083 | ratio | event_rate | train | eq |  | unsupported |  |
| 33 | conceptual_soundness | Finally, the relationship between the published baseline haz… | 0.0179 | ratio | event_rate | test | eq |  | unsupported |  |
| 34 | data_integrity | The raw training profile reports zero missing values in ever… | 2.285 | ratio | note_rate | train | eq |  | unsupported |  |
| 35 | data_integrity | The raw training profile reports zero missing values in ever… | 6.384 | ratio | note_rate | train | eq |  | unsupported |  |
| 36 | data_integrity | The raw training profile reports zero missing values in ever… | 43 | ratio | ltv | train | eq |  | unsupported |  |
| 37 | data_integrity | The raw training profile reports zero missing values in ever… | 97 | ratio | ltv | train | eq |  | unsupported |  |
| 38 | data_integrity | The raw training profile reports zero missing values in ever… | 620 | ratio | credit_score | train | eq |  | unsupported |  |
| 39 | data_integrity | The raw training profile reports zero missing values in ever… | 820 | ratio | credit_score | train | eq |  | unsupported |  |
| 40 | data_integrity | The raw training profile reports zero missing values in ever… | 10.65 | ratio | log_upb | train | eq |  | unsupported |  |
| 41 | data_integrity | The raw training profile reports zero missing values in ever… | 13.36 | ratio | log_upb | train | eq |  | unsupported |  |
| 42 | data_integrity | The raw training profile reports zero missing values in ever… | 3.12 | ratio |  |  | eq |  | unattributed |  |
| 43 | data_integrity | The raw training profile reports zero missing values in ever… | 3.17 | ratio | incentive | train | eq |  | unsupported |  |
| 44 | data_integrity | The raw training profile reports zero missing values in ever… | 0 | ratio | burnout | train | eq |  | unsupported |  |
| 45 | data_integrity | The raw training profile reports zero missing values in ever… | 9.32 | ratio | burnout | train | eq |  | unsupported |  |
| 46 | data_integrity | The raw training profile reports zero missing values in ever… | 0.707 | ratio | std | train | eq |  | unsupported |  |
| 47 | data_integrity | The raw training profile reports zero missing values in ever… | 201402 | ratio | period | train | eq |  | unsupported |  |
| 48 | data_integrity | The raw training profile reports zero missing values in ever… | 201912 | ratio | period | train | eq |  | unsupported |  |
| 49 | data_integrity | The first is the duplicate split. gives `test` and `out_of_t… | 12257 | count | rows | test | eq | `[[art:53221637:run.splits]]` | dangling |  |
| 50 | data_integrity | The first is the duplicate split. gives `test` and `out_of_t… | 515 | count | loans | test | eq | `[[art:53221637:run.splits]]` | dangling |  |
| 51 | data_integrity | The first is the duplicate split. gives `test` and `out_of_t… | 0.017949 | ratio | event_rate | test | eq | `[[art:53221637:run.splits]]` | dangling |  |
| 52 | data_integrity | On drift: the splits are not exchangeable. Event rates are 0… | 0.00832 | ratio | event_rate | train | eq |  | unsupported |  |
| 53 | data_integrity | On drift: the splits are not exchangeable. Event rates are 0… | 0.01795 | ratio | event_rate | test | eq |  | unsupported |  |
| 54 | data_integrity | On drift: the splits are not exchangeable. Event rates are 0… | 0.00482 | ratio | event_rate | vintage_holdout | eq |  | unsupported |  |
| 55 | data_integrity | On drift: the splits are not exchangeable. Event rates are 0… | 2.2 | ratio | event_rate |  | ratio |  | unsupported |  |
| 56 | data_integrity | On drift: the splits are not exchangeable. Event rates are 0… | 3.7 | ratio | event_rate |  | ratio |  | unsupported |  |
| 57 | data_integrity | On drift: the splits are not exchangeable. Event rates are 0… | 0.00833 | ratio | mean_predicted_hazard | train | eq |  | unsupported |  |
| 58 | data_integrity | On drift: the splits are not exchangeable. Event rates are 0… | 0.02283 | ratio | mean_predicted_hazard | test | eq |  | unsupported |  |
| 59 | data_integrity | On drift: the splits are not exchangeable. Event rates are 0… | 0.00616 | ratio | mean_predicted_hazard | vintage_holdout | eq |  | unsupported |  |
| 60 | data_integrity | On drift: the splits are not exchangeable. Event rates are 0… | 2019 | ratio |  | train | eq |  | unsupported |  |
| 61 | data_integrity | On drift: the splits are not exchangeable. Event rates are 0… | 19.5 | percent | cpr | test | eq |  | unsupported |  |
| 62 | data_integrity | Sample size deserves a note even though it is not a defect c… | 1848 | count | loans |  | eq |  | unsupported |  |
| 63 | data_integrity | Sample size deserves a note even though it is not a defect c… | 667 | count | loans | train | eq |  | unsupported |  |
| 64 | data_integrity | Sample size deserves a note even though it is not a defect c… | 666 | count | loans | vintage_holdout | eq |  | unsupported |  |
| 65 | data_integrity | Sample size deserves a note even though it is not a defect c… | 515 | count | loans | test | eq |  | unsupported |  |
| 66 | data_integrity | Sample size deserves a note even though it is not a defect c… | 279 | count | event_count | train | eq |  | unsupported |  |
| 67 | data_integrity | Sample size deserves a note even though it is not a defect c… | 155 | count | event_count | vintage_holdout | eq |  | unsupported |  |
| 68 | data_integrity | Sample size deserves a note even though it is not a defect c… | 220 | count | event_count | test | eq |  | unsupported |  |
| 69 | data_integrity | Sample size deserves a note even though it is not a defect c… | 33522 | count | rows | train | eq |  | unsupported |  |
| 70 | data_integrity | Sample size deserves a note even though it is not a defect c… | 12257 | count | rows | test | eq |  | unsupported |  |
| 71 | outcomes | Discrimination holds up. AUC is 0.8003 in train, 0.7846 in t… | 0.8003 | ratio | auc | train | eq |  | unsupported |  |
| 72 | outcomes | Discrimination holds up. AUC is 0.8003 in train, 0.7846 in t… | 0.7846 | ratio | auc | test | eq |  | unsupported |  |
| 73 | outcomes | Discrimination holds up. AUC is 0.8003 in train, 0.7846 in t… | 0.7716 | ratio | auc | vintage_holdout | eq |  | unsupported |  |
| 74 | outcomes | Discrimination holds up. AUC is 0.8003 in train, 0.7846 in t… | 0.601 | ratio | gini | train | eq |  | unsupported |  |
| 75 | outcomes | Discrimination holds up. AUC is 0.8003 in train, 0.7846 in t… | 0.569 | ratio | gini | test | eq |  | unsupported |  |
| 76 | outcomes | Discrimination holds up. AUC is 0.8003 in train, 0.7846 in t… | 0.543 | ratio | gini | vintage_holdout | eq |  | unsupported |  |
| 77 | outcomes | Discrimination holds up. AUC is 0.8003 in train, 0.7846 in t… | 0.474 | ratio | ks | train | eq |  | unsupported |  |
| 78 | outcomes | Discrimination holds up. AUC is 0.8003 in train, 0.7846 in t… | 0.437 | ratio | ks | test | eq |  | unsupported |  |
| 79 | outcomes | Discrimination holds up. AUC is 0.8003 in train, 0.7846 in t… | 0.462 | ratio | ks | vintage_holdout | eq |  | unsupported |  |
| 80 | outcomes | Discrimination holds up. AUC is 0.8003 in train, 0.7846 in t… | 0.016 | ratio | delta_auc | test | delta |  | unsupported |  |
| 81 | outcomes | Discrimination holds up. AUC is 0.8003 in train, 0.7846 in t… | 0.029 | ratio | delta_auc | vintage_holdout | delta |  | unsupported |  |
| 82 | outcomes | Discrimination holds up. AUC is 0.8003 in train, 0.7846 in t… | 0.0081 | ratio | brier | train | eq |  | unsupported |  |
| 83 | outcomes | Discrimination holds up. AUC is 0.8003 in train, 0.7846 in t… | 0.0428 | ratio | logloss | train | eq |  | unsupported |  |
| 84 | outcomes | Discrimination holds up. AUC is 0.8003 in train, 0.7846 in t… | 0.0173 | ratio | brier | test | eq |  | unsupported |  |
| 85 | outcomes | Discrimination holds up. AUC is 0.8003 in train, 0.7846 in t… | 0.0805 | ratio | logloss | test | eq |  | unsupported |  |
| 86 | outcomes | Calibration is where the model fails. On test, predicted CPR… | 0.242 | ratio | predicted_cpr | test | eq |  | unsupported |  |
| 87 | outcomes | Calibration is where the model fails. On test, predicted CPR… | 0.1953 | ratio | actual_cpr | test | eq |  | unsupported |  |
| 88 | outcomes | Calibration is where the model fails. On test, predicted CPR… | 23.9 | percent | cpr_over_prediction | test | eq |  | unsupported |  |
| 89 | outcomes | Calibration is where the model fails. On test, predicted CPR… | 0.022827 | ratio | mean_predicted | test | eq |  | unsupported |  |
| 90 | outcomes | Calibration is where the model fails. On test, predicted CPR… | 0.017949 | ratio | event_rate | test | eq |  | unsupported |  |
| 91 | outcomes | Calibration is where the model fails. On test, predicted CPR… | 27.2 | percent | hazard_over_prediction | test | eq |  | unsupported |  |
| 92 | outcomes | Calibration is where the model fails. On test, predicted CPR… | 0.0714 | ratio | predicted_cpr | vintage_holdout | eq |  | unsupported |  |
| 93 | outcomes | Calibration is where the model fails. On test, predicted CPR… | 0.0563 | ratio | actual_cpr | vintage_holdout | eq |  | unsupported |  |
| 94 | outcomes | Calibration is where the model fails. On test, predicted CPR… | 26.9 | percent | cpr_over_prediction | vintage_holdout | eq |  | unsupported |  |
| 95 | outcomes | Calibration is where the model fails. On test, predicted CPR… | 0.006157 | ratio | mean_predicted | vintage_holdout | eq |  | unsupported |  |
| 96 | outcomes | Calibration is where the model fails. On test, predicted CPR… | 0.004817 | ratio | event_rate | vintage_holdout | eq |  | unsupported |  |
| 97 | outcomes | Calibration is where the model fails. On test, predicted CPR… | 27.8 | percent | hazard_over_prediction | vintage_holdout | eq |  | unsupported |  |
| 98 | outcomes | Calibration is where the model fails. On test, predicted CPR… | 1.015 | ratio | calibration_slope | train | eq |  | unsupported |  |
| 99 | outcomes | Calibration is where the model fails. On test, predicted CPR… | 0.008333 | ratio | mean_predicted | train | eq |  | unsupported |  |
| 100 | outcomes | Calibration is where the model fails. On test, predicted CPR… | 0.008323 | ratio | event_rate | train | eq |  | unsupported |  |
| 101 | outcomes | The calibration slopes add a second layer. Test slope is 0.9… | 0.9369 | ratio | calibration_slope | test | eq |  | unsupported |  |
| 102 | outcomes | The calibration slopes add a second layer. Test slope is 0.9… | 0.9 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 103 | outcomes | The calibration slopes add a second layer. Test slope is 0.9… | 1.1 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 104 | outcomes | The calibration slopes add a second layer. Test slope is 0.9… | 0.8554 | ratio | calibration_slope | vintage_holdout | eq |  | unsupported |  |
| 105 | outcomes | Effective challenge was not performed. The artifact store co… | 0.78 | ratio | auc | test | eq |  | unsupported |  |
| 106 | sensitivity | The baseline hazard in is non-monotone by construction: it r… | 0.00109 | ratio | baseline_hazard |  | eq | `[[art:cf58dded:run.model_summary#baseline_hazard]]` | dangling |  |
| 107 | sensitivity | The baseline hazard in is non-monotone by construction: it r… | 0 | months | loan_age |  | eq | `[[art:cf58dded:run.model_summary#baseline_hazard]]` | dangling |  |
| 108 | sensitivity | The baseline hazard in is non-monotone by construction: it r… | 0.0041 | ratio | baseline_hazard |  | eq | `[[art:cf58dded:run.model_summary#baseline_hazard]]` | dangling |  |
| 109 | sensitivity | The baseline hazard in is non-monotone by construction: it r… | 39 | months | loan_age |  | eq | `[[art:cf58dded:run.model_summary#baseline_hazard]]` | dangling |  |
| 110 | sensitivity | The baseline hazard in is non-monotone by construction: it r… | 0.0026 | ratio | baseline_hazard |  | eq | `[[art:cf58dded:run.model_summary#baseline_hazard]]` | dangling |  |
| 111 | sensitivity | The baseline hazard in is non-monotone by construction: it r… | 55 | months | loan_age |  | eq | `[[art:cf58dded:run.model_summary#baseline_hazard]]` | dangling |  |
| 112 | sensitivity | The baseline hazard in is non-monotone by construction: it r… | 0.00161 | ratio | baseline_hazard |  | eq | `[[art:cf58dded:run.model_summary#baseline_hazard]]` | dangling |  |
| 113 | sensitivity | The baseline hazard in is non-monotone by construction: it r… | 66 | months | loan_age |  | eq | `[[art:cf58dded:run.model_summary#baseline_hazard]]` | dangling |  |
| 114 | sensitivity | The baseline hazard in is non-monotone by construction: it r… | 0.00109 | ratio | baseline_hazard |  | eq | `[[art:cf58dded:run.model_summary#baseline_hazard]]` | dangling |  |
| 115 | sensitivity | The baseline hazard in is non-monotone by construction: it r… | 75 | months | loan_age |  | eq | `[[art:cf58dded:run.model_summary#baseline_hazard]]` | dangling |  |
| 116 | sensitivity | The baseline hazard in is non-monotone by construction: it r… | 0.000495 | ratio | baseline_hazard |  | eq | `[[art:cf58dded:run.model_summary#baseline_hazard]]` | dangling |  |
| 117 | sensitivity | The baseline hazard in is non-monotone by construction: it r… | 93 | months | loan_age |  | eq | `[[art:cf58dded:run.model_summary#baseline_hazard]]` | dangling |  |
| 118 | sensitivity | The baseline hazard in is non-monotone by construction: it r… | 0.000349 | ratio | baseline_hazard |  | eq | `[[art:cf58dded:run.model_summary#baseline_hazard]]` | dangling |  |
| 119 | sensitivity | The baseline hazard in is non-monotone by construction: it r… | 101 | months | loan_age |  | eq | `[[art:cf58dded:run.model_summary#baseline_hazard]]` | dangling |  |
| 120 | sensitivity | The baseline hazard in is non-monotone by construction: it r… | 59 | months | loan_age | train | eq |  | unsupported |  |
| 121 | sensitivity | The baseline hazard in is non-monotone by construction: it r… | 60 | months | loan_age |  | eq |  | unsupported |  |
| 122 | sensitivity | The baseline hazard in is non-monotone by construction: it r… | 55 | months | loan_age |  | eq |  | unsupported |  |
| 123 | sensitivity | Sign and stability testing across rate regimes could not be… | 2020 | ratio |  |  | eq |  | unsupported |  |
| 124 | sensitivity | Sign and stability testing across rate regimes could not be… | 2020 | ratio |  |  | eq |  | unsupported |  |
| 125 | sensitivity | Sign and stability testing across rate regimes could not be… | 0.8 | ratio | auc | train | eq |  | unsupported |  |
| 126 | sensitivity | Sign and stability testing across rate regimes could not be… | 0.785 | ratio | auc | test | eq |  | unsupported |  |
| 127 | findings | The calibration error should be remediated rather than merel… | 0.855 | ratio | calibration_slope | vintage_holdout | eq |  | unsupported |  |
| 128 | findings | The age-spline tail should be constrained. Extending knots t… | 59 | months |  |  | eq |  | unsupported |  |
| 129 | findings | The age-spline tail should be constrained. Extending knots t… | 101 | months |  |  | eq |  | unsupported |  |
| 130 | findings | The age-spline tail should be constrained. Extending knots t… | 59 | months |  |  | eq |  | unsupported |  |
| 131 | findings | Recommended disposition: the model should not be approved fo… | 27 | percent |  |  | eq |  | unsupported |  |
| 132 | monitoring | Monthly, compare actual to predicted CPR at the total-portfo… | 10 | percent |  |  | eq |  | unsupported |  |
| 133 | monitoring | Monthly, compare actual to predicted CPR at the total-portfo… | 20 | percent |  |  | eq |  | unsupported |  |
| 134 | monitoring | Monthly, compare actual to predicted CPR at the total-portfo… | 24 | percent |  |  | eq |  | unsupported |  |
| 135 | monitoring | Monthly, compare actual to predicted CPR at the total-portfo… | 28 | percent |  |  | eq |  | unsupported |  |
| 136 | monitoring | Quarterly, recompute the calibration slope and intercept on… | 0.9 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 137 | monitoring | Quarterly, recompute the calibration slope and intercept on… | 1.1 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 138 | monitoring | Quarterly, recompute the calibration slope and intercept on… | 0.85 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 139 | monitoring | Quarterly, recompute the calibration slope and intercept on… | 1.15 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 140 | monitoring | Quarterly, recompute the calibration slope and intercept on… | 0.05 | ratio | delta_auc |  | eq |  | unsupported |  |
| 141 | monitoring | Quarterly, recompute the calibration slope and intercept on… | 0.785 | ratio | auc |  | eq |  | unsupported |  |
| 142 | monitoring | Quarterly, compute PSI on every model covariate and on the p… | 0.1 | ratio | psi |  | eq |  | unsupported |  |
| 143 | monitoring | Quarterly, compute PSI on every model covariate and on the p… | 0.25 | ratio | psi |  | eq |  | unsupported |  |
| 144 | monitoring | Quarterly, compute PSI on every model covariate and on the p… | 2.7 | ratio |  |  | eq |  | unsupported |  |

## Appendix B — Artifact index

The store holds 19 artifacts; the 19 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `plain_llm.profile` | `f3a0b7f4` | json | json | raw profile of data_train.csv |
| `run.data_out_of_time` | `7ddcc721` | table | table, 12257 rows | the subject's data_out_of_time.csv |
| `run.data_test` | `37197b92` | table | table, 12257 rows | the subject's data_test.csv |
| `run.data_train` | `ca4a8c57` | table | table, 33522 rows | the subject's data_train.csv |
| `run.data_vintage_holdout` | `940d14da` | table | table, 32177 rows | the subject's data_vintage_holdout.csv |
| `run.duration_s` | `04b9b5f2` | scalar | 2.333572458 | subject wall-clock seconds |
| `run.features` | `61276a96` | json | json | the subject's features.json |
| `run.metrics` | `0ed16a42` | json | json | the subject's metrics.json |
| `run.model_summary` | `cf58dded` | json | json | the subject's model_summary.json |
| `run.predictions_out_of_time` | `1fbaf335` | table | table, 12257 rows | the subject's predictions_out_of_time.csv |
| `run.predictions_test` | `90b547ad` | table | table, 12257 rows | the subject's predictions_test.csv |
| `run.predictions_train` | `dcc88ba4` | table | table, 33522 rows | the subject's predictions_train.csv |
| `run.predictions_vintage_holdout` | `a7e53ac8` | table | table, 32177 rows | the subject's predictions_vintage_holdout.csv |
| `run.projection` | `9fcedb3d` | json | json | the subject's projection.json |
| `run.splits` | `53221637` | json | json | the subject's splits.json |
| `run.status` | `5c222bcc` | json | json | how the subject's subprocess ended |
| `run.stderr` | `41728c38` | json | json | the subject's stderr |
| `run.stdout` | `521fb527` | json | json | the subject's stdout |
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |

## Appendix C — Run trace summary

| quantity | value |
|---|---|
| tool calls | 1 (run_model 1) |
| plan steps (bounded loop) | 0 |
| LLM calls | 8 (plain_llm 1, extract 7) |
| re-asks | 0 |
| repair rounds | 0 |
| tokens in / out | 63,183 / 38,467 |
| notional cost (USD) | 1.5812 |
| wall-clock (s) | 475.24 |
| subject run (s) | 2.33 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | msr_prepayment-plain_llm-20260918T215755Z-986f3824 |

## Appendix D — Not checked

| item | reason |
|---|---|
| `check_stability` (R1) | this configuration runs no checks |
| `run_scenarios` (X1) | this configuration runs no checks |
| developer claims (T1, claim channel) | `plain_llm` runs no check over `package.yaml`'s declared claims |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
| every check of spec 3.7 but `run_model` | `plain_llm` runs the subject and one model call, by design |
