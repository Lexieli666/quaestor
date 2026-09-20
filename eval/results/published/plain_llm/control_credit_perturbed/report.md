---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: plain_llm
model: claude-opus-5[1m]
run_id: credit_default-plain_llm-20260918T073410Z-6e98ce62
data_mode: synthetic
synthetic_n: 5000
grounding_precision_pre: 0.0000
grounding_precision_post: 0.0000
n_claims: 122
n_findings_by_severity: {high: 0, medium: 4, low: 3, info: 3}
generated: "2026-09-18T07:34:10Z"
illustrative: false
---

# Validation report — `credit_default` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `credit_default` v1.0 | `plain_llm` | claude-opus-5[1m] | synthetic, n = 5000 | 0.0000 → 0.0000 | 0 / 4 / 3 / 3 |
<!-- quaestor:renderer:end -->

This report documents an independent validation of package `credit_default` version 1.0, a binary classification model estimated to predict `default_next_month`. The subject is a standardised logistic regression with ten retained predictors, an intercept of ⟦unverified: -1.3958⟧, fitted on ⟦unverified: 3,500⟧ training rows and evaluated on ⟦unverified: 1,500⟧ held-out rows ([[art:f181acb8:run.model_summary]], [[art:aebcad6a:run.metrics]], [[art:3b6b0a38:run.splits]]).

The validation was conducted entirely against the artifacts the development run itself emitted: the metrics file, the model summary, the feature inventory with timing declarations, the split manifest, the raw training-split profile, and the run's status and output streams ([[art:2f9cb453:run.features]], [[art:05bbd6f4:plain_llm.profile]], [[art:2922931d:run.status]], [[art:5d8f71ad:run.stdout]], [[art:41728c38:run.stderr]]). Prediction tables for both splits exist in the store ([[art:dea9574d:run.predictions_test]], [[art:c734ca2d:run.predictions_train]]) but no derived calibration, segmentation, drift, scenario or benchmarking artifacts were produced by the developer, which bounds what can be concluded here.

Headline discriminatory performance is moderate and stable: test AUC ⟦unverified: 0.7480⟧ (Gini ⟦unverified: 0.4960⟧, KS ⟦unverified: 0.4183⟧) against train AUC ⟦unverified: 0.7584⟧ (Gini ⟦unverified: 0.5169⟧, KS ⟦unverified: 0.4451⟧). Aggregate calibration is close, with mean predicted probability ⟦unverified: 0.2211⟧ on test against an observed event rate of ⟦unverified: 0.2247⟧. The test Brier score of ⟦unverified: 0.1489⟧ compares to a no-skill reference of p(⟦unverified: 1⟧-p) = ⟦unverified: 0.1742⟧, a Brier skill of roughly ⟦unverified: 0.15⟧.

On that evidence the model's rank-ordering is fit for a low-stakes, monitored use. However, the validation file is incomplete in ways that matter for a credit-decisioning model: there is no out-of-time sample, no challenger, no calibration slope, no segment-level testing, and no scenario analysis. Several retained coefficients carry economically wrong signs, which is the single most substantive conceptual concern. Overall assessment: **usable with required remediation**, not approvable for unrestricted use as documented.

## 2. Conceptual soundness

The choice of a standardised logistic regression for a binary default outcome is appropriate and defensible. It is monotone in each predictor by construction, its coefficients are directly interpretable, and it produces probabilities rather than scores alone, which the near-equality of mean predicted and observed rates confirms was achieved ([[art:aebcad6a:run.metrics]]). `class_weight` is null, which is correct for a model whose output is intended to be a probability: at a ⟦unverified: 22.5%⟧ event rate there is no need to reweight, and reweighting would have destroyed the aggregate calibration that the metrics show.

The feature set is coherent for the problem. Two predictors are declared `at_origination` (`f_limit_bal`, `f_age`) and ten are declared `before_period_start`; none is declared `during_period` or `after_outcome` ([[art:2f9cb453:run.features]]). Taken at face value, the timing declarations are consistent with a model that forecasts next-month default from information available at the start of the period, and the absence of any post-outcome feature is a genuine strength of the specification.

The coefficient vector, however, is not economically coherent, and this is the report's principal conceptual finding ([[art:f181acb8:run.model_summary]]). Four signs contradict established credit behaviour:

- `f_pay_ratio_last` enters at **+⟦unverified: 0.1026⟧** while `f_pay_ratio_mean_6m` enters at **⟦unverified: -0.3554⟧**. Paying down more of the last bill cannot raise default odds while paying down more on average lowers them. One of the two is absorbing the other's variance.
- `f_delinq_max_6m` enters at **⟦unverified: -0.0322⟧** while `f_delinq_last` enters at **+⟦unverified: 0.7334⟧** and `f_delinq_count_6m` at **+⟦unverified: 0.1226⟧**. A higher worst-case delinquency in the window reducing risk is not interpretable.
- `f_bill_trend_6m` enters at **⟦unverified: -0.2225⟧**, making rising balances protective.
- `f_limit_bal` enters at **+⟦unverified: 0.0727⟧**. Credit limits are underwriter-assigned and normally inversely related to risk; a positive sign implies the lender's own underwriting is adversely selecting.

`f_delinq_last` (+⟦unverified: 0.7334⟧) is by a wide margin the dominant predictor, and its sign and magnitude are correct and intuitive. `f_utilisation` (+⟦unverified: 0.2662⟧) and `f_age` (⟦unverified: -0.0673⟧) are likewise correctly signed. The problem is confined to the collinear families, which points to the diagnosis in section 6: the wrong signs are a symptom of residual multicollinearity rather than of a broken outcome definition.

No single-feature AUC screen is present in the store, so the specification cannot be cleared of the possibility that one predictor trivially reproduces the outcome. Given that the full ten-feature model reaches only ⟦unverified: 0.7480⟧ on test, no single feature can plausibly exceed ⟦unverified: 0.90⟧, and this residual risk is recorded as informational rather than as a defect.

## 3. Data integrity and drift

The training-split profile is clean on its face ([[art:05bbd6f4:plain_llm.profile]]). All thirteen columns report `missing: 0.0` across ⟦unverified: 3,500⟧ rows. Ranges are broadly plausible: `f_age` spans ⟦unverified: 21⟧-⟦unverified: 63,⟧ `f_limit_bal` spans ⟦unverified: 10,000⟧-⟦unverified: 800,000,⟧ `f_delinq_last` spans ⟦unverified: 0⟧-⟦unverified: 8,⟧ and the target mean of ⟦unverified: 0.22457⟧ reconciles exactly with the declared training event rate of ⟦unverified: 0.2245714⟧ in the split manifest ([[art:3b6b0a38:run.splits]]).

Three integrity observations qualify that clean bill of health.

First, `f_pay_ratio_last` has a maximum of exactly **⟦unverified: 2.0⟧** while its six-month counterpart `f_pay_ratio_mean_6m` tops out at ⟦unverified: 1.6385⟧. A maximum sitting on a round number to full precision is the signature of a winsorisation or cap, and no capping rule is documented anywhere in the emitted artifacts. If the cap exists it must be declared, because it changes the meaning of the coefficient; if it does not, the coincidence needs explanation.

Second, `f_utilisation` reaches **⟦unverified: 1.1298⟧**, i.e. balances exceeding the assigned limit. This is genuinely possible through over-limit fees and interest accrual, so it is not an error, but combined with the positive sign on `f_limit_bal` it warrants confirmation that the ratio's denominator is the contemporaneous limit.

Third, universal zero missingness across every raw column, including six-month aggregates that require a full payment history, is unusual for retail credit data. Either the population was filtered to complete histories — which would be a material scope restriction on where the model may be applied and is not documented — or imputation occurred silently upstream of the profile.

On drift, the store contains no basis for an assessment. There is no out-of-time or out-of-universe sample, no PSI computation for either the population or the score distribution, and no date field appears in the profile. The two splits ([[art:7c66774a:run.data_train]], [[art:10c3b98e:run.data_test]]) carry distinct row hashes and near-identical event rates (⟦unverified: 0.2245714⟧ against ⟦unverified: 0.2246667⟧), a ⟦unverified: 0.01⟧ percentage point difference that is the signature of a stratified random split rather than a temporal one. A random split cannot detect drift by construction: it guarantees that train and test are drawn from the same period and therefore the same regime. No drift finding can be raised on evidence, and no drift assurance can be given either. This absence is reported as the defect, since a credit model validated only in-sample-period has no demonstrated stability.

A cross-split missingness comparison, which is the standard integrity test, could not be performed because only the training-split profile was emitted. No profile of the test split exists in the store.

## 4. Outcomes analysis

Discrimination on the held-out split is moderate and, importantly, stable ([[art:aebcad6a:run.metrics]]):

| Metric | Train (n=⟦unverified: 3,500⟧) | Test (n=⟦unverified: 1,500⟧) | Gap |
|---|---|---|---|
| AUC | ⟦unverified: 0.75844⟧ | ⟦unverified: 0.74799⟧ | ⟦unverified: 0.01045⟧ |
| Gini | ⟦unverified: 0.51687⟧ | ⟦unverified: 0.49598⟧ | ⟦unverified: 0.02089⟧ |
| KS | ⟦unverified: 0.44514⟧ | ⟦unverified: 0.41827⟧ | ⟦unverified: 0.02687⟧ |
| Log loss | ⟦unverified: 0.46500⟧ | ⟦unverified: 0.46729⟧ | +⟦unverified: 0.00229⟧ |
| Brier | ⟦unverified: 0.14891⟧ | ⟦unverified: 0.14885⟧ | ⟦unverified: -0.00007⟧ |
| Mean predicted | ⟦unverified: 0.22462⟧ | ⟦unverified: 0.22110⟧ | — |
| Event rate | ⟦unverified: 0.22457⟧ | ⟦unverified: 0.22467⟧ | — |

The train-to-test AUC gap of **⟦unverified: 0.0104⟧** is small in absolute terms and well inside any conventional degradation threshold. Ten standardised coefficients fitted on ⟦unverified: 3,500⟧ observations with ⟦unverified: 786⟧ events gives roughly ⟦unverified: 79⟧ events per parameter, so the near-absence of a generalisation gap is exactly what the specification predicts. Gini and Brier are internally consistent throughout: ⟦unverified: 2⟧(⟦unverified: 0.74799⟧) - ⟦unverified: 1⟧ = ⟦unverified: 0.49598⟧ and ⟦unverified: 2⟧(⟦unverified: 0.75844⟧) - ⟦unverified: 1⟧ = ⟦unverified: 0.51687⟧ both reconcile to the reported values, which is a useful check that the metrics file is self-consistent rather than assembled from separate runs. The Brier score is in fact marginally *better* on test than on train, which is noise at this sample size but confirms there is no overfitting to diagnose.

Aggregate calibration is good. Mean predicted probability on test is ⟦unverified: 0.22110⟧ against an observed ⟦unverified: 0.22467⟧, an under-prediction of ⟦unverified: 0.36⟧ percentage points, or a predicted-to-observed ratio of ⟦unverified: 0.984⟧. On train the two agree to ⟦unverified: 0.00005⟧, as maximum-likelihood fitting of an intercept guarantees. The test Brier of ⟦unverified: 0.14885⟧ against the no-skill reference of ⟦unverified: 0.22467⟧ x ⟦unverified: 0.77533⟧ = ⟦unverified: 0.17420⟧ implies a Brier skill score of ⟦unverified: 0.146⟧.

What cannot be concluded is that the model is calibrated *across* the score range. Agreement of the means is a necessary but not sufficient condition, and it is entirely compatible with a calibration slope well away from 1.0 — a model that is systematically over-confident at the top of the distribution and under-confident at the bottom will still reproduce the mean. No calibration slope, intercept, decile table or reliability curve was emitted, though the per-row prediction tables needed to compute them are in the store ([[art:dea9574d:run.predictions_test]], [[art:c734ca2d:run.predictions_train]]). This is a remediable gap rather than an observed failure, and it is graded accordingly.

No threshold, cut-off or approval rate is declared anywhere in the artifacts, so no confusion-matrix analysis at a decision point was possible, and no developer-declared performance claim exists that could be tested for breach. The one numeric threshold the developer did declare, `vif_threshold: 10.0`, is addressed in section 5.

## 5. Sensitivity and scenario analysis

No scenario or sensitivity artifacts were produced. There is no value curve, no partial-dependence output, no univariate shock analysis and no stress scenario in the store. The assessment below is therefore derived analytically from the coefficient vector, which for a standardised logistic regression fully determines the shape of every univariate risk curve.

Because the link is logistic and each feature enters linearly, each implied value curve is monotone in that feature, with direction given by the sign of its coefficient. Reading the curves off [[art:f181acb8:run.model_summary]], four of the ten slope in the wrong direction, as set out in section 2: increasing `f_pay_ratio_last`, decreasing `f_delinq_max_6m`, decreasing `f_bill_trend_6m` and increasing `f_limit_bal` are all modelled as risk-increasing or risk-reducing against economic expectation. Considered as a family rather than one at a time, the surfaces are worse than wrong-signed, they are non-monotone: along the delinquency dimension, risk rises steeply in `f_delinq_last` (+⟦unverified: 0.7334⟧) and in `f_delinq_count_6m` (+⟦unverified: 0.1226⟧) but falls in `f_delinq_max_6m` (⟦unverified: -0.0322⟧), so a borrower whose delinquency deepens across all three measures simultaneously does not move monotonically in predicted risk. The same holds for the payment-ratio pair, where the last-period and six-month-mean terms oppose each other at +⟦unverified: 0.1026⟧ and ⟦unverified: -0.3554⟧.

The practical consequence is that the model cannot be used for any purpose that relies on the behaviour of an individual coefficient: reason codes, adverse-action explanations, affordability what-ifs, or pricing sensitivities would all be misleading, even though the aggregate ranking is sound. Rank-ordering survives because the offsetting terms net out across the correlated block; explanation does not.

On sensitivity to specification, the developer did run one diagnostic and acted on it. Two features were dropped against a declared VIF threshold of ⟦unverified: 10.0⟧: `f_bill_last` at VIF **⟦unverified: 160.89⟧** and `f_utilisation_mean_6m` at VIF **⟦unverified: 36.36⟧** ([[art:f181acb8:run.model_summary]]). That removal was correct and is credited. But no post-removal VIFs or condition number were reported, so there is no evidence that the retained ten satisfy the developer's own declared threshold. The surviving set still contains three delinquency measures over the same six-month window, two payment ratios, a level-and-trend pair on billing, and `f_utilisation` whose six-month sibling was removed for collinearity. The wrong signs documented above are the expected fingerprint of exactly that residual dependence, since collinearity inflates coefficient variance and readily flips the sign of the weaker member of a correlated pair without materially harming joint fit — which is precisely the pattern observed, a ⟦unverified: 0.0104⟧ AUC gap alongside an uninterpretable coefficient vector.

No challenger model of any kind was fitted. With no benchmark — not a penalised logistic regression, not a gradient-boosted tree, not even a single-feature `f_delinq_last` scorecard — there is no way to judge whether ⟦unverified: 0.7480⟧ represents the information available in these twelve features or leaves material signal unused. Effective challenge is a requirement, not an enhancement, and it is absent.

On execution, the run recorded a status and a duration against a declared runtime cap ([[art:2922931d:run.status]], [[art:6ca13444:run.duration_s]], [[art:2ad8d1a5:runtime.max_seconds]]), and the streams ([[art:5d8f71ad:run.stdout]], [[art:41728c38:run.stderr]]) are present. Nothing in the metrics or summary suggests a truncated or failed fit — all declared counts reconcile, `n_train: 3500` matches the split manifest — so no execution defect is raised.

## 6. Findings and recommendations

The validation raises eight defects: four medium, three low and one informational, alongside two informational observations recorded for completeness. None is high: the model's rank-ordering is demonstrated on held-out data, aggregate calibration holds, and no leakage or contamination was observed, so there is no basis for withholding the model outright.

**Medium — required before unrestricted use.**

1. *Residual multicollinearity (M1).* Re-report VIFs and the design-matrix condition number for the retained ten features. Where families remain dependent, consolidate rather than dropping arbitrarily: retain one payment-ratio measure, replace the three delinquency counts with a single ordered severity measure, and either drop `f_bill_trend_6m` or orthogonalise it against `f_bill_mean_6m`. Re-fitting with a penalty (ridge or elastic net) is an acceptable alternative and would also serve as the challenger required by finding ⟦unverified: 3⟧.

2. *Wrong-signed and non-monotone risk surfaces (X1).* Every retained coefficient must carry an economically defensible sign before the model is used for anything beyond ranking. Until it does, explicitly prohibit reason-code and adverse-action use. Produce univariate value curves over the observed range of each feature as part of the re-fit package.

3. *No effective challenge (E1).* Fit at least one challenger on the same split and report its test AUC alongside the champion's ⟦unverified: 0.7480⟧. A penalised logistic regression and a gradient-boosted tree are the natural pair; if a challenger beats the champion by a material margin, the champion's ten-feature specification needs revisiting.

4. *No out-of-time validation and no drift measurement (S1).* The random, event-rate-stratified split cannot evidence stability over time. Construct a genuine out-of-time sample, report AUC and calibration on it, and compute PSI for both the feature distributions and the score distribution against the development population.

**Low — document and remediate at next revision.**

5. *Calibration slope not estimated (C1).* Mean predicted matches observed to ⟦unverified: 0.36⟧ percentage points, but the slope is untested. Compute the calibration slope and intercept and a ten-bin reliability table from [[art:dea9574d:run.predictions_test]]; confirm the slope falls inside its band.

6. *Undocumented capping and completeness (D1).* Document the origin of the exact ⟦unverified: 2.0⟧ maximum on `f_pay_ratio_last`, confirm the denominator convention permitting `f_utilisation` above 1.0, and state whether universal zero missingness reflects a completeness filter on the population. Emit a test-split profile so cross-split missingness can be compared.

7. *No segment or regime testing (R1).* Report AUC and the sign of `f_delinq_last` — the dominant term at +⟦unverified: 0.7334⟧ — separately across meaningful segments such as age bands, limit bands and utilisation bands, to confirm the specification is not driven by one sub-population.

**Informational.**

8. *Split overlap not independently verifiable (L2).* The manifest carries one aggregate row hash per split and no identifier-level intersection test. `client_id` ranges from ⟦unverified: 1⟧ to ⟦unverified: 5,000⟧ in a ⟦unverified: 3,500⟧-row training profile against ⟦unverified: 3,500⟧ + ⟦unverified: 1,500⟧ = ⟦unverified: 5,000⟧ total rows, which is consistent with a clean partition of ⟦unverified: 5,000⟧ distinct clients, and the distinct row hashes are consistent with disjoint sets. Contamination is therefore unlikely but not demonstrated; emit an explicit identifier-intersection count. Note also that if any client contributes multiple rows, row-level disjointness would not imply client-level disjointness.

The out-of-sample gap (O1) and the leakage screen (L1) are recorded below as informational observations with no remediation attached: the ⟦unverified: 0.0104⟧ AUC gap is comfortably within tolerance, and the timing declarations show zero `after_outcome` and zero `during_period` features.

### F-001 · M1 collinearity · severity **medium**

The developer declared a VIF threshold of 10.0 and removed two features that breached it: f_bill_last at VIF 160.89 and f_utilisation_mean_6m at VIF 36.36. That action was correct, but no post-removal VIFs and no design-matrix condition number were reported, so there is no evidence that the ten retained features satisfy the developer's own declared threshold. The retained set still contains three delinquency measures over the same six-month window (f_delinq_last, f_delinq_count_6m, f_delinq_max_6m), two payment ratios (f_pay_ratio_last, f_pay_ratio_mean_6m), a level-and-trend pair on billing (f_bill_mean_6m, f_bill_trend_6m), and f_utilisation whose six-month sibling was removed precisely for collinearity. The coefficient vector bears the classic fingerprint of residual dependence: within each correlated family the weaker member's sign has flipped (f_pay_ratio_last +0.1026 against f_pay_ratio_mean_6m -0.3554; f_delinq_max_6m -0.0322 against f_delinq_last +0.7334) while joint fit is unharmed, as shown by the small 0.0104 train-to-test AUC gap. Collinearity inflates coefficient variance and readily reverses the sign of a correlated term without degrading discrimination, which is exactly the pattern observed. Remediation: re-report VIFs and the condition number for the retained ten, consolidate the dependent families into single measures, or re-fit under a ridge or elastic-net penalty.

### F-002 · X1 scenario analysis · severity **medium**

No scenario or sensitivity artifacts were emitted, so the implied value curves were derived analytically from the coefficient vector; for a logistic model with linear terms, each univariate curve's direction is fully determined by the sign of its coefficient. Four of the ten slope against economic expectation. f_pay_ratio_last enters at +0.1026, making a larger paydown of the most recent bill risk-increasing, while f_pay_ratio_mean_6m enters at -0.3554 and makes the same behaviour risk-reducing on average. f_delinq_max_6m enters at -0.0322, so a worse peak delinquency in the window reduces predicted risk, directly contradicting f_delinq_last at +0.7334 and f_delinq_count_6m at +0.1226. f_bill_trend_6m enters at -0.2225, making rising balances protective. f_limit_bal enters at +0.0727, implying that the lender's own underwriter-assigned limits are positively associated with default. Read as families rather than individually, the surfaces are not merely wrong-signed but non-monotone: a borrower whose delinquency deepens on all three measures simultaneously does not move monotonically in predicted risk, and the same holds along the payment-ratio dimension. Aggregate rank-ordering survives because the offsetting terms net out within the correlated block, but the model cannot support reason codes, adverse-action explanations, affordability what-ifs or pricing sensitivities. Remediation: every retained coefficient must carry a defensible sign before any coefficient-level use; produce univariate value curves over each feature's observed range; prohibit explanation-based use in the interim.

### F-003 · E1 effective challenge · severity **medium**

The store contains exactly one fitted model, the ten-feature standardised logistic regression described in the model summary, and one set of metrics. No challenger of any kind was estimated: not a penalised logistic regression, not a tree ensemble, not even a trivial single-feature scorecard on f_delinq_last, which at +0.7334 is the dominant term and would establish how much of the 0.7480 test AUC the remaining nine features actually contribute. Without a benchmark there is no way to judge whether 0.7480 extracts the information available in these twelve candidate features or leaves material signal unused, and no way to test whether a specification free of the sign anomalies would perform as well. Effective challenge is a requirement rather than an enhancement, and its absence cannot be cured by the champion's own in-sample-period stability. Remediation: fit at least one challenger on the identical split, report its test AUC beside the champion's, and revisit the champion specification if the margin is material. A penalised re-fit would satisfy this finding and the multicollinearity finding together.

### F-004 · S1 population drift · severity **medium**

The split manifest reports train n=3,500 with event rate 0.2245714 and test n=1,500 with event rate 0.2246667, a difference of 0.01 percentage point. Agreement that tight is the signature of an event-rate-stratified random split, not a temporal one, and no date or vintage field appears anywhere in the training profile's thirteen columns. A random split cannot detect drift by construction, because it guarantees both partitions are drawn from the same period and therefore the same regime. Consistent with this, the store contains no PSI computation for either the feature distributions or the score distribution, and no out-of-time or out-of-universe holdout. The defect reported is therefore the absence of the test rather than an observed drift breach: no drift finding can be raised on this evidence, but no stability assurance can be given either, and a credit model validated only within its development period has no demonstrated durability. Remediation: construct a genuine out-of-time sample, report AUC and calibration on it against the in-period baselines of 0.7480 and 0.2211 mean predicted, and compute feature-level and score-level PSI against the development population.

### F-005 · C1 calibration · severity **low**

Aggregate calibration is good as far as it is measured. On test, mean predicted probability is 0.221105 against an observed event rate of 0.224667, an under-prediction of 0.36 percentage points and a predicted-to-observed ratio of 0.984; on train the two agree to 0.00005, as maximum-likelihood estimation of an intercept guarantees. The test Brier of 0.148851 against the no-skill reference p(1-p) = 0.224667 x 0.775333 = 0.174204 implies a Brier skill score of 0.146. However, agreement of the means is a necessary but not sufficient condition for calibration: a model that is over-confident at the top of the score distribution and under-confident at the bottom reproduces the mean exactly while carrying a calibration slope well away from 1.0. No calibration slope, calibration intercept, decile table or reliability curve was emitted, so nothing can be concluded about calibration across the score range, which is what matters for any probability-based decision or pricing use. The per-row prediction tables required to compute all of these are already in the store, so this is a cheap documentation gap rather than an observed failure, and it is graded low accordingly. Remediation: compute the calibration slope and intercept and a ten-bin reliability table from the test predictions and confirm the slope falls inside its band.

### F-006 · D1 data integrity · severity **low**

The training profile is clean on its face, with missing 0.0 on all thirteen columns over 3,500 rows and a target mean of 0.22457 that reconciles exactly with the declared training event rate. Three qualifications apply. First, f_pay_ratio_last has a maximum of exactly 2.0 to full reported precision, while its six-month counterpart f_pay_ratio_mean_6m tops out at 1.6385; a maximum resting on a round number is the signature of a winsorisation or cap, and no capping rule is documented in any emitted artifact, which matters because a cap changes the interpretation of the +0.1026 coefficient on that feature. Second, f_utilisation reaches 1.1297, i.e. balances exceeding the assigned limit; this is genuinely possible through over-limit fees and interest accrual and is not treated as an error, but taken together with the counterintuitive positive sign on f_limit_bal it warrants confirmation that the ratio uses the contemporaneous limit as its denominator. Third, universal zero missingness across every raw column, including six-month aggregates that require a complete payment history, is unusual for retail credit data and implies either an undocumented completeness filter on the population, which would materially restrict where the model may be applied, or silent upstream imputation. Separately, the standard cross-split missingness comparison could not be performed at all, because only the training-split profile was emitted and no profile of the test split exists in the store. Remediation: document the capping rule and the utilisation denominator, state whether a completeness filter was applied, and emit a test-split profile.

### F-007 · R1 regime stability · severity **low**

Performance and coefficients are reported only for the pooled population. No segment-level or regime-level breakdown exists in the store: there is no AUC by age band, limit band, utilisation band or delinquency status, and no re-estimation of the coefficient vector within sub-populations. Because the split is random and within a single period, the two partitions do not constitute distinct regimes and cannot substitute for this analysis. The exposure is concentrated in one term: f_delinq_last dominates the model at +0.7334, roughly twice the magnitude of the next largest coefficient, so if its sign or strength is driven by one sub-population the pooled 0.7480 test AUC would overstate performance elsewhere. The four wrong-signed coefficients identified elsewhere in this report raise the same question from the other direction, since sign flips confined to a segment are a common consequence of heterogeneous populations pooled into one linear specification. Remediation: report AUC, KS and calibration separately across age, limit and utilisation bands, together with the sign and magnitude of f_delinq_last within each, and confirm the specification is not driven by a single sub-population.

### F-008 · L2 contamination · severity **info**

No contamination was observed and none is alleged. The split manifest carries distinct row hashes for the two partitions, 3e28943d for test and e028347d for train, which is consistent with disjoint row sets. The counts reconcile with a clean partition of a single population: 3,500 train plus 1,500 test equals 5,000, and client_id in the training profile ranges from 1 to 5,000 with a mean of 2,513.91 against the 2,500.5 expected under uniform sampling from 5,000 distinct clients. Overlap is therefore unlikely. What is missing is the direct test: the manifest provides one aggregate hash per split and no identifier-level intersection count, so disjointness is inferred rather than demonstrated. Two residual risks remain unaddressed by the hashes alone. Identical hashes would prove overlap, but distinct hashes only prove the row multisets differ, not that they share no rows. And if any client contributes more than one row to the modelling table, row-level disjointness would not imply client-level disjointness, which is the form of contamination that actually inflates held-out performance. Recorded as informational with no remediation beyond emitting an explicit client_id intersection count between the two splits.

### F-009 · O1 out-of-sample degradation · severity **info**

Recorded as an observation with no remediation attached, since the tested condition passes. Discrimination degrades only marginally out of sample: AUC falls from 0.758436 on train to 0.747989 on test, a gap of 0.010447; Gini from 0.516871 to 0.495978; KS from 0.445140 to 0.418268. Log loss rises by only 0.00229, from 0.465001 to 0.467291, and the Brier score is in fact fractionally better on test (0.148851) than on train (0.148915), which is noise at this sample size but confirms there is no overfitting to remediate. The result is what the specification predicts: ten standardised coefficients fitted on 3,500 rows with roughly 786 events gives about 79 events per estimated parameter, ample for a stable linear fit. The metrics file is also internally self-consistent on this point, since 2(0.747989) - 1 = 0.495978 and 2(0.758436) - 1 = 0.516871 both reconcile exactly to the reported Gini values, indicating the train and test figures come from a single coherent run rather than being assembled from separate fits. No out-of-sample degradation defect is raised. Note that this conclusion is confined to the development period; it says nothing about stability over time, which is covered separately.

### F-010 · L1 leakage · severity **info**

Recorded as an observation with no remediation attached, since the tested conditions pass. The feature inventory declares 12 candidate features with after_outcome = 0 and during_period = 0; two are declared at_origination (f_limit_bal, f_age) and ten are declared before_period_start. Taken at face value, the declarations are consistent with a model that forecasts next-month default using only information available at the start of the period, and the complete absence of post-outcome or contemporaneous features is a genuine strength of the specification rather than merely the absence of a problem. On the second limb of the leakage test, no single-feature AUC screen was emitted, so no predictor has been individually cleared against the 0.90 bar. That residual risk is judged immaterial by arithmetic: the full ten-feature model reaches only 0.747989 on test, and since adding features cannot reduce in-sample discrimination, no individual feature can plausibly approach 0.90. The largest standardised coefficient, f_delinq_last at +0.7334, is a behavioural delinquency measure whose predictive strength is expected and legitimate rather than suspicious. The one caveat is that the timing declarations are the developer's own assertions and no artifact in the store independently verifies the observation windows against the outcome definition.

Candidates raised and not promoted: none.

### Open items

No open item was recorded for this validation.

## 7. Ongoing monitoring recommendations

The development evidence supports monitored use only, and the monitoring plan must compensate for what validation could not establish.

**Monthly.** Track the realised default rate against the mean predicted probability, with the development test values of ⟦unverified: 0.2247⟧ observed and ⟦unverified: 0.2211⟧ predicted as the reference pair; escalate on a sustained divergence beyond a pre-agreed tolerance over three consecutive cycles. Track score-distribution PSI against the development population and escalate above the institution's standard threshold. Track feature-level missingness against the profiled baseline of exactly zero on all thirteen columns ([[art:05bbd6f4:plain_llm.profile]]) — because the baseline is zero, *any* emerging missingness is a signal and should alert rather than merely be logged. Track the share of `f_pay_ratio_last` observations landing exactly on ⟦unverified: 2.0⟧ and of `f_utilisation` observations above 1.0, both of which bear on finding ⟦unverified: 6⟧.

**Quarterly.** Recompute AUC, KS and Brier on accumulated production outcomes against the test baselines of ⟦unverified: 0.7480⟧, ⟦unverified: 0.4183⟧ and ⟦unverified: 0.1489⟧. Recompute the calibration slope and intercept and a decile reliability table. Re-estimate the coefficient vector on recent data and compare signs and magnitudes against [[art:f181acb8:run.model_summary]], with specific attention to whether `f_delinq_last` remains the dominant positive term and whether the four wrong-signed coefficients identified in section 2 stabilise, flip or persist. Persistence of those signs across refits would confirm the multicollinearity diagnosis and should force the re-specification in finding ⟦unverified: 1⟧.

**Annually.** Re-run the full validation, including the out-of-time test, the challenger comparison and the segment-level analysis that findings ⟦unverified: 3,⟧ ⟦unverified: 4⟧ and ⟦unverified: 7⟧ require. Re-verify split hygiene on any new development sample.

**Standing conditions.** Pending remediation of finding ⟦unverified: 2,⟧ the model is approved for rank-ordering only; individual coefficients must not be used to generate customer-facing explanations or adverse-action reasons. Because no decision threshold was declared or tested, any cut-off adopted in production must be validated separately before use. Because completeness of the development population is undocumented, application of the model to segments with incomplete six-month histories is outside the validated scope until finding ⟦unverified: 6⟧ is closed.

## Appendix A — Claims

Grounding precision 0.0000 before repair (0 of 122 claims verified; 112 unsupported, 10 dangling) and 0.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 0/15; conceptual_soundness 0/13; data_integrity 0/15; outcomes 0/43; sensitivity 0/10; findings 0/13; monitoring 0/13.

Developer claims: `plain_llm` runs no check over `package.yaml`'s declared claims See Appendix D.

Excluded numeric tokens (not claims): section_number (section 6, section 5, section 2, 1.); inline_code (`missing: 0.0`, `vif_threshold: 10.0`, `n_train: 3500`); citation_hash (f181acb8, aebcad6a, 3b6b0a38, 2f9cb453); package_version (1.0); extractor_returned_excluded_token (1.0, 10.0, 2, 4.0).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | This report documents an independent validation of package `… | -1.3958 | ratio | coefficient |  | eq | `[[art:f181acb8:run.model_summary]]` | dangling |  |
| 2 | summary | This report documents an independent validation of package `… | 3500 | count | n_rows | train | eq | `[[art:3b6b0a38:run.splits]]` | dangling |  |
| 3 | summary | This report documents an independent validation of package `… | 1500 | count | n_rows | test | eq | `[[art:3b6b0a38:run.splits]]` | dangling |  |
| 4 | summary | Headline discriminatory performance is moderate and stable:… | 0.748 | ratio | auc | test | eq |  | unsupported |  |
| 5 | summary | Headline discriminatory performance is moderate and stable:… | 0.496 | ratio | gini | test | eq |  | unsupported |  |
| 6 | summary | Headline discriminatory performance is moderate and stable:… | 0.4183 | ratio | ks | test | eq |  | unsupported |  |
| 7 | summary | Headline discriminatory performance is moderate and stable:… | 0.7584 | ratio | auc | train | eq |  | unsupported |  |
| 8 | summary | Headline discriminatory performance is moderate and stable:… | 0.5169 | ratio | gini | train | eq |  | unsupported |  |
| 9 | summary | Headline discriminatory performance is moderate and stable:… | 0.4451 | ratio | ks | train | eq |  | unsupported |  |
| 10 | summary | Headline discriminatory performance is moderate and stable:… | 0.2211 | ratio | mean_predicted_probability | test | eq |  | unsupported |  |
| 11 | summary | Headline discriminatory performance is moderate and stable:… | 0.2247 | ratio | event_rate | test | eq |  | unsupported |  |
| 12 | summary | Headline discriminatory performance is moderate and stable:… | 0.1489 | ratio | brier | test | eq |  | unsupported |  |
| 13 | summary | Headline discriminatory performance is moderate and stable:… | 1 | ratio |  |  | eq |  | unsupported |  |
| 14 | summary | Headline discriminatory performance is moderate and stable:… | 0.1742 | ratio | brier_reference | test | eq |  | unsupported |  |
| 15 | summary | Headline discriminatory performance is moderate and stable:… | 0.15 | ratio | brier_skill | test | eq |  | unsupported |  |
| 16 | conceptual_soundness | The choice of a standardised logistic regression for a binar… | 22.5 | percent | event_rate |  | eq |  | unsupported |  |
| 17 | conceptual_soundness | - `f_pay_ratio_last` enters at **+0.1026** while `f_pay_rati… | 0.1026 | ratio | coefficient |  | eq |  | unsupported |  |
| 18 | conceptual_soundness | - `f_pay_ratio_last` enters at **+0.1026** while `f_pay_rati… | -0.3554 | ratio | coefficient |  | eq |  | unsupported |  |
| 19 | conceptual_soundness | - `f_delinq_max_6m` enters at **-0.0322** while `f_delinq_la… | -0.0322 | ratio | coefficient |  | eq |  | unsupported |  |
| 20 | conceptual_soundness | - `f_delinq_max_6m` enters at **-0.0322** while `f_delinq_la… | 0.7334 | ratio | coefficient |  | eq |  | unsupported |  |
| 21 | conceptual_soundness | - `f_delinq_max_6m` enters at **-0.0322** while `f_delinq_la… | 0.1226 | ratio | coefficient |  | eq |  | unsupported |  |
| 22 | conceptual_soundness | - `f_bill_trend_6m` enters at **-0.2225**, making rising bal… | -0.2225 | ratio | coefficient |  | eq |  | unsupported |  |
| 23 | conceptual_soundness | - `f_limit_bal` enters at **+0.0727**. Credit limits are und… | 0.0727 | ratio | coefficient |  | eq |  | unsupported |  |
| 24 | conceptual_soundness | `f_delinq_last` (+0.7334) is by a wide margin the dominant p… | 0.7334 | ratio | coefficient |  | eq |  | unsupported |  |
| 25 | conceptual_soundness | `f_delinq_last` (+0.7334) is by a wide margin the dominant p… | 0.2662 | ratio | coefficient |  | eq |  | unsupported |  |
| 26 | conceptual_soundness | `f_delinq_last` (+0.7334) is by a wide margin the dominant p… | -0.0673 | ratio | coefficient |  | eq |  | unsupported |  |
| 27 | conceptual_soundness | No single-feature AUC screen is present in the store, so the… | 0.748 | ratio | auc | test | eq |  | unsupported |  |
| 28 | conceptual_soundness | No single-feature AUC screen is present in the store, so the… | 0.9 | ratio | auc |  | eq |  | unsupported |  |
| 29 | data_integrity | The training-split profile is clean on its face (). All thir… | 3500 | count |  | train | eq |  | unsupported |  |
| 30 | data_integrity | The training-split profile is clean on its face (). All thir… | 21 | ratio |  | train | eq |  | unsupported |  |
| 31 | data_integrity | The training-split profile is clean on its face (). All thir… | 63 | ratio |  | train | eq |  | unsupported |  |
| 32 | data_integrity | The training-split profile is clean on its face (). All thir… | 10000 | currency |  | train | eq |  | unsupported |  |
| 33 | data_integrity | The training-split profile is clean on its face (). All thir… | 800000 | currency |  | train | eq |  | unsupported |  |
| 34 | data_integrity | The training-split profile is clean on its face (). All thir… | 0 | ratio |  | train | eq |  | unsupported |  |
| 35 | data_integrity | The training-split profile is clean on its face (). All thir… | 8 | count |  | train | eq |  | unsupported |  |
| 36 | data_integrity | The training-split profile is clean on its face (). All thir… | 0.22457 | ratio | event_rate | train | eq |  | unsupported |  |
| 37 | data_integrity | The training-split profile is clean on its face (). All thir… | 0.2245714 | ratio | event_rate | train | eq | `[[art:3b6b0a38:run.splits]]` | dangling |  |
| 38 | data_integrity | First, `f_pay_ratio_last` has a maximum of exactly **2.0** w… | 2 | ratio |  | train | eq |  | unsupported |  |
| 39 | data_integrity | First, `f_pay_ratio_last` has a maximum of exactly **2.0** w… | 1.6385 | ratio |  | train | eq |  | unsupported |  |
| 40 | data_integrity | Second, `f_utilisation` reaches **1.1298**, i.e. balances ex… | 1.1298 | ratio |  | train | eq |  | unsupported |  |
| 41 | data_integrity | On drift, the store contains no basis for an assessment. The… | 0.2245714 | ratio | event_rate | train | eq | `[[art:7c66774a:run.data_train]]` | dangling |  |
| 42 | data_integrity | On drift, the store contains no basis for an assessment. The… | 0.2246667 | ratio | event_rate | test | eq | `[[art:10c3b98e:run.data_test]]` | dangling |  |
| 43 | data_integrity | On drift, the store contains no basis for an assessment. The… | 0.01 | percent | event_rate |  | delta | `[[art:7c66774a:run.data_train]] [[art:10c3b98e:run.data_test]]` | dangling |  |
| 44 | outcomes | \| Metric \| Train (n=3,500) \| Test (n=1,500) \| Gap \| | 3500 | count | n_rows | train | eq |  | unsupported |  |
| 45 | outcomes | \| Metric \| Train (n=3,500) \| Test (n=1,500) \| Gap \| | 1500 | count | n_rows | test | eq |  | unsupported |  |
| 46 | outcomes | \| AUC \| 0.75844 \| 0.74799 \| 0.01045 \| | 0.75844 | ratio | auc | train | eq |  | unsupported |  |
| 47 | outcomes | \| AUC \| 0.75844 \| 0.74799 \| 0.01045 \| | 0.74799 | ratio | auc | test | eq |  | unsupported |  |
| 48 | outcomes | \| AUC \| 0.75844 \| 0.74799 \| 0.01045 \| | 0.01045 | ratio | delta_auc |  | delta |  | unsupported |  |
| 49 | outcomes | \| Gini \| 0.51687 \| 0.49598 \| 0.02089 \| | 0.51687 | ratio | gini | train | eq |  | unsupported |  |
| 50 | outcomes | \| Gini \| 0.51687 \| 0.49598 \| 0.02089 \| | 0.49598 | ratio | gini | test | eq |  | unsupported |  |
| 51 | outcomes | \| Gini \| 0.51687 \| 0.49598 \| 0.02089 \| | 0.02089 | ratio | delta_gini |  | delta |  | unsupported |  |
| 52 | outcomes | \| KS \| 0.44514 \| 0.41827 \| 0.02687 \| | 0.44514 | ratio | ks | train | eq |  | unsupported |  |
| 53 | outcomes | \| KS \| 0.44514 \| 0.41827 \| 0.02687 \| | 0.41827 | ratio | ks | test | eq |  | unsupported |  |
| 54 | outcomes | \| KS \| 0.44514 \| 0.41827 \| 0.02687 \| | 0.02687 | ratio | delta_ks |  | delta |  | unsupported |  |
| 55 | outcomes | \| Log loss \| 0.46500 \| 0.46729 \| +0.00229 \| | 0.465 | ratio | log_loss | train | eq |  | unsupported |  |
| 56 | outcomes | \| Log loss \| 0.46500 \| 0.46729 \| +0.00229 \| | 0.46729 | ratio | log_loss | test | eq |  | unsupported |  |
| 57 | outcomes | \| Log loss \| 0.46500 \| 0.46729 \| +0.00229 \| | 0.00229 | ratio | delta_log_loss |  | delta |  | unsupported |  |
| 58 | outcomes | \| Brier \| 0.14891 \| 0.14885 \| -0.00007 \| | 0.14891 | ratio | brier | train | eq |  | unsupported |  |
| 59 | outcomes | \| Brier \| 0.14891 \| 0.14885 \| -0.00007 \| | 0.14885 | ratio | brier | test | eq |  | unsupported |  |
| 60 | outcomes | \| Brier \| 0.14891 \| 0.14885 \| -0.00007 \| | -7e-05 | ratio | delta_brier |  | delta |  | unsupported |  |
| 61 | outcomes | \| Mean predicted \| 0.22462 \| 0.22110 \| — \| | 0.22462 | ratio | mean_predicted | train | eq |  | unsupported |  |
| 62 | outcomes | \| Mean predicted \| 0.22462 \| 0.22110 \| — \| | 0.2211 | ratio | mean_predicted | test | eq |  | unsupported |  |
| 63 | outcomes | \| Event rate \| 0.22457 \| 0.22467 \| — \| | 0.22457 | ratio | event_rate | train | eq |  | unsupported |  |
| 64 | outcomes | \| Event rate \| 0.22457 \| 0.22467 \| — \| | 0.22467 | ratio | event_rate | test | eq |  | unsupported |  |
| 65 | outcomes | The train-to-test AUC gap of **0.0104** is small in absolute… | 0.0104 | ratio | delta_auc |  | delta |  | unsupported |  |
| 66 | outcomes | The train-to-test AUC gap of **0.0104** is small in absolute… | 3500 | count | n_rows | train | eq |  | unsupported |  |
| 67 | outcomes | The train-to-test AUC gap of **0.0104** is small in absolute… | 786 | count | n_events | train | eq |  | unsupported |  |
| 68 | outcomes | The train-to-test AUC gap of **0.0104** is small in absolute… | 79 | ratio | events_per_parameter | train | eq |  | unsupported |  |
| 69 | outcomes | The train-to-test AUC gap of **0.0104** is small in absolute… | 2 | ratio |  |  | eq |  | unsupported |  |
| 70 | outcomes | The train-to-test AUC gap of **0.0104** is small in absolute… | 0.74799 | ratio | auc | test | eq |  | unsupported |  |
| 71 | outcomes | The train-to-test AUC gap of **0.0104** is small in absolute… | 1 | ratio |  |  | eq |  | unsupported |  |
| 72 | outcomes | The train-to-test AUC gap of **0.0104** is small in absolute… | 0.49598 | ratio | gini | test | eq |  | unsupported |  |
| 73 | outcomes | The train-to-test AUC gap of **0.0104** is small in absolute… | 2 | ratio |  |  | eq |  | unsupported |  |
| 74 | outcomes | The train-to-test AUC gap of **0.0104** is small in absolute… | 0.75844 | ratio | auc | train | eq |  | unsupported |  |
| 75 | outcomes | The train-to-test AUC gap of **0.0104** is small in absolute… | 1 | ratio |  |  | eq |  | unsupported |  |
| 76 | outcomes | The train-to-test AUC gap of **0.0104** is small in absolute… | 0.51687 | ratio | gini | train | eq |  | unsupported |  |
| 77 | outcomes | Aggregate calibration is good. Mean predicted probability on… | 0.2211 | ratio | mean_predicted | test | eq |  | unsupported |  |
| 78 | outcomes | Aggregate calibration is good. Mean predicted probability on… | 0.22467 | ratio | event_rate | test | eq |  | unsupported |  |
| 79 | outcomes | Aggregate calibration is good. Mean predicted probability on… | 0.36 | percent | calibration_gap | test | delta |  | unsupported |  |
| 80 | outcomes | Aggregate calibration is good. Mean predicted probability on… | 0.984 | ratio | predicted_to_observed | test | ratio |  | unsupported |  |
| 81 | outcomes | Aggregate calibration is good. Mean predicted probability on… | 5e-05 | ratio | calibration_gap | train | delta |  | unsupported |  |
| 82 | outcomes | Aggregate calibration is good. Mean predicted probability on… | 0.14885 | ratio | brier | test | eq |  | unsupported |  |
| 83 | outcomes | Aggregate calibration is good. Mean predicted probability on… | 0.22467 | ratio | event_rate | test | eq |  | unsupported |  |
| 84 | outcomes | Aggregate calibration is good. Mean predicted probability on… | 0.77533 | ratio | event_rate | test | eq |  | unsupported |  |
| 85 | outcomes | Aggregate calibration is good. Mean predicted probability on… | 0.1742 | ratio | brier_no_skill | test | eq |  | unsupported |  |
| 86 | outcomes | Aggregate calibration is good. Mean predicted probability on… | 0.146 | ratio | brier_skill_score | test | eq |  | unsupported |  |
| 87 | sensitivity | Because the link is logistic and each feature enters linearl… | 0.7334 | ratio | coefficient |  | eq |  | unsupported |  |
| 88 | sensitivity | Because the link is logistic and each feature enters linearl… | 0.1226 | ratio | coefficient |  | eq |  | unsupported |  |
| 89 | sensitivity | Because the link is logistic and each feature enters linearl… | -0.0322 | ratio | coefficient |  | eq |  | unsupported |  |
| 90 | sensitivity | Because the link is logistic and each feature enters linearl… | 0.1026 | ratio | coefficient |  | eq |  | unsupported |  |
| 91 | sensitivity | Because the link is logistic and each feature enters linearl… | -0.3554 | ratio | coefficient |  | eq |  | unsupported |  |
| 92 | sensitivity | On sensitivity to specification, the developer did run one d… | 10 | ratio | vif |  | eq | `[[art:f181acb8:run.model_summary]]` | dangling |  |
| 93 | sensitivity | On sensitivity to specification, the developer did run one d… | 160.89 | ratio | vif |  | eq | `[[art:f181acb8:run.model_summary]]` | dangling |  |
| 94 | sensitivity | On sensitivity to specification, the developer did run one d… | 36.36 | ratio | vif |  | eq | `[[art:f181acb8:run.model_summary]]` | dangling |  |
| 95 | sensitivity | On sensitivity to specification, the developer did run one d… | 0.0104 | ratio | delta_auc |  | delta |  | unsupported |  |
| 96 | sensitivity | No challenger model of any kind was fitted. With no benchmar… | 0.748 | ratio | auc |  | eq |  | unsupported |  |
| 97 | findings | 1. *Residual multicollinearity (M1).* Re-report VIFs and the… | 3 | count |  |  | eq |  | unsupported |  |
| 98 | findings | 3. *No effective challenge (E1).* Fit at least one challenge… | 0.748 | ratio | auc | test | eq |  | unsupported |  |
| 99 | findings | 5. *Calibration slope not estimated (C1).* Mean predicted ma… | 0.36 | percent |  |  | eq |  | unsupported |  |
| 100 | findings | 6. *Undocumented capping and completeness (D1).* Document th… | 2 | ratio |  |  | eq |  | unsupported |  |
| 101 | findings | 7. *No segment or regime testing (R1).* Report AUC and the s… | 0.7334 | ratio | coefficient |  | eq |  | unsupported |  |
| 102 | findings | 8. *Split overlap not independently verifiable (L2).* The ma… | 1 | count |  |  | eq |  | unsupported |  |
| 103 | findings | 8. *Split overlap not independently verifiable (L2).* The ma… | 5000 | count |  |  | eq |  | unsupported |  |
| 104 | findings | 8. *Split overlap not independently verifiable (L2).* The ma… | 3500 | count |  | train | eq |  | unsupported |  |
| 105 | findings | 8. *Split overlap not independently verifiable (L2).* The ma… | 3500 | count |  | train | eq |  | unsupported |  |
| 106 | findings | 8. *Split overlap not independently verifiable (L2).* The ma… | 1500 | count |  | test | eq |  | unsupported |  |
| 107 | findings | 8. *Split overlap not independently verifiable (L2).* The ma… | 5000 | count |  |  | eq |  | unsupported |  |
| 108 | findings | 8. *Split overlap not independently verifiable (L2).* The ma… | 5000 | count |  |  | eq |  | unsupported |  |
| 109 | findings | The out-of-sample gap (O1) and the leakage screen (L1) are r… | 0.0104 | ratio | delta_auc |  | eq |  | unsupported |  |
| 110 | monitoring | **Monthly.** Track the realised default rate against the mea… | 0.2247 | ratio | event_rate | test | eq |  | unsupported |  |
| 111 | monitoring | **Monthly.** Track the realised default rate against the mea… | 0.2211 | ratio | mean_predicted_probability | test | eq |  | unsupported |  |
| 112 | monitoring | **Monthly.** Track the realised default rate against the mea… | 2 | ratio |  |  | eq |  | unsupported |  |
| 113 | monitoring | **Monthly.** Track the realised default rate against the mea… | 6 | ratio |  |  | eq |  | unsupported |  |
| 114 | monitoring | **Quarterly.** Recompute AUC, KS and Brier on accumulated pr… | 0.748 | ratio | auc | test | eq |  | unsupported |  |
| 115 | monitoring | **Quarterly.** Recompute AUC, KS and Brier on accumulated pr… | 0.4183 | ratio | ks | test | eq |  | unsupported |  |
| 116 | monitoring | **Quarterly.** Recompute AUC, KS and Brier on accumulated pr… | 0.1489 | ratio | brier | test | eq |  | unsupported |  |
| 117 | monitoring | **Quarterly.** Recompute AUC, KS and Brier on accumulated pr… | 1 | ratio |  |  | eq |  | unsupported |  |
| 118 | monitoring | **Annually.** Re-run the full validation, including the out-… | 3 | ratio |  |  | eq |  | unsupported |  |
| 119 | monitoring | **Annually.** Re-run the full validation, including the out-… | 4 | ratio |  |  | eq |  | unsupported |  |
| 120 | monitoring | **Annually.** Re-run the full validation, including the out-… | 7 | ratio |  |  | eq |  | unsupported |  |
| 121 | monitoring | **Standing conditions.** Pending remediation of finding 2, t… | 2 | ratio |  |  | eq |  | unsupported |  |
| 122 | monitoring | **Standing conditions.** Pending remediation of finding 2, t… | 6 | months |  |  | eq |  | unsupported |  |

## Appendix B — Artifact index

The store holds 14 artifacts; the 14 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `plain_llm.profile` | `05bbd6f4` | json | json | raw profile of data_train.csv |
| `run.data_test` | `10c3b98e` | table | table, 1500 rows | the subject's data_test.csv |
| `run.data_train` | `7c66774a` | table | table, 3500 rows | the subject's data_train.csv |
| `run.duration_s` | `6ca13444` | scalar | 1.149517167 | subject wall-clock seconds |
| `run.features` | `2f9cb453` | json | json | the subject's features.json |
| `run.metrics` | `aebcad6a` | json | json | the subject's metrics.json |
| `run.model_summary` | `f181acb8` | json | json | the subject's model_summary.json |
| `run.predictions_test` | `dea9574d` | table | table, 1500 rows | the subject's predictions_test.csv |
| `run.predictions_train` | `c734ca2d` | table | table, 3500 rows | the subject's predictions_train.csv |
| `run.splits` | `3b6b0a38` | json | json | the subject's splits.json |
| `run.status` | `2922931d` | json | json | how the subject's subprocess ended |
| `run.stderr` | `41728c38` | json | json | the subject's stderr |
| `run.stdout` | `5d8f71ad` | json | json | the subject's stdout |
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |

## Appendix C — Run trace summary

| quantity | value |
|---|---|
| tool calls | 1 (run_model 1) |
| plan steps (bounded loop) | 0 |
| LLM calls | 8 (plain_llm 1, extract 7) |
| re-asks | 0 |
| repair rounds | 0 |
| tokens in / out | 60,475 / 40,681 |
| notional cost (USD) | 1.6067 |
| wall-clock (s) | 477.43 |
| subject run (s) | 1.15 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | credit_default-plain_llm-20260918T073410Z-6e98ce62 |

## Appendix D — Not checked

| item | reason |
|---|---|
| `check_stability` (R1) | package declares no `regime.column` |
| `run_scenarios` (X1) | not applicable to `binary_classification` |
| out-of-time and vintage-holdout metrics (O1, second rule) | package declares neither split |
| developer claims (T1, claim channel) | `plain_llm` runs no check over `package.yaml`'s declared claims |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
| every check of spec 3.7 but `run_model` | `plain_llm` runs the subject and one model call, by design |
