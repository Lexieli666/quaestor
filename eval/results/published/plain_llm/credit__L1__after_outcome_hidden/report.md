---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: plain_llm
model: claude-opus-5[1m]
run_id: credit_default-plain_llm-20260918T181308Z-6e98ce62
data_mode: synthetic
synthetic_n: 5000
grounding_precision_pre: 0.0000
grounding_precision_post: 0.0000
n_claims: 82
n_findings_by_severity: {high: 1, medium: 4, low: 3, info: 2}
generated: "2026-09-18T18:13:08Z"
illustrative: false
---

# Validation report — `credit_default` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `credit_default` v1.0 | `plain_llm` | claude-opus-5[1m] | synthetic, n = 5000 | 0.0000 → 0.0000 | 1 / 4 / 3 / 2 |
<!-- quaestor:renderer:end -->

This report documents an independent validation of package `credit_default` version 1.0, a binary classification model estimating the probability of a client defaulting in the following month (`default_next_month`). The subject is a standardised logistic regression with eleven retained predictors, an intercept of ⟦unverified: -6.1028⟧, fitted on ⟦unverified: 3,500⟧ training rows and evaluated on ⟦unverified: 1,500⟧ test rows [[art:e4b3fd0e:run.model_summary]], [[art:3b6b0a38:run.splits]].

The scope of the review covers conceptual soundness of the specification, the integrity and timing of the input data, the reported discrimination and calibration outcomes, and the completeness of the sensitivity, scenario and challenger work. The evidence base is limited to the artifacts the developer deposited: metrics [[art:65d0d3f7:run.metrics]], model summary [[art:e4b3fd0e:run.model_summary]], the feature inventory [[art:b85c116d:run.features]], the split manifest [[art:3b6b0a38:run.splits]], the training and test tables [[art:43dc824d:run.data_train]], [[art:7db99b1c:run.data_test]], the scored outputs [[art:ebd7a887:run.predictions_train]], [[art:1eb04cca:run.predictions_test]], and the run logs [[art:2922931d:run.status]], [[art:94cf46a2:run.stdout]], [[art:41728c38:run.stderr]].

The headline conclusion is that the model **should not be used as it stands**. Its reported performance — test AUC ⟦unverified: 0.9755⟧, KS ⟦unverified: 0.8784⟧, Brier ⟦unverified: 0.0425⟧ against a ⟦unverified: 22.5%⟧ event rate — is not attainable on a genuine forward-looking consumer default problem and is, in our assessment, the signature of target leakage through the predictor `pay_amt_next`. Every downstream outcome in this report is contaminated by that defect, so the discrimination, calibration and stability results below should be read as descriptions of a leaking model, not as evidence of predictive skill.

## 2. Conceptual soundness

The choice of a logistic regression on standardised inputs is appropriate for a regulated credit-risk application: it is transparent, its coefficients are directly interpretable as standardised log-odds effects, and it supports the sign and magnitude review that follows. The developer applied a variance-inflation screen at a declared threshold of ⟦unverified: 10.0⟧ and removed `bill_last` (VIF ⟦unverified: 162.93⟧) and `utilisation_mean_6m` (VIF ⟦unverified: 36.78⟧) [[art:e4b3fd0e:run.model_summary#removed]]. That is sound practice and is documented.

The specification nevertheless fails on three conceptual grounds.

**The predictor `pay_amt_next` is not knowable at scoring time.** Its name denotes the payment amount in the next period, which is the very period over which the outcome `default_next_month` is measured. The feature inventory declares it `before_period_start` and reports `after_outcome: 0` and `during_period: 0` [[art:b85c116d:run.features]], but that declaration is contradicted by the variable's own semantics and by its behaviour in the fitted model. Its standardised coefficient is **⟦unverified: -12.3667⟧**, while the largest of the other ten coefficients is ⟦unverified: 1.6512⟧ (`bill_mean_6m`) [[art:e4b3fd0e:run.model_summary#coefficients]]. A one-standard-deviation increase in this single variable moves the log-odds by more than twelve units — an odds ratio of roughly ⟦unverified: 4e-6⟧. No legitimate behavioural covariate carries that weight; a coefficient of this size is the arithmetic of a variable that mechanically encodes the label.

**The fitted intercept is inconsistent with the average prediction.** On standardised inputs every predictor has mean zero, so a linear predictor evaluated at the feature means equals the intercept, ⟦unverified: -6.1028⟧, implying a probability near ⟦unverified: 0.002⟧. Yet the reported mean predicted probability is ⟦unverified: 0.2246⟧ on train and ⟦unverified: 0.2330⟧ on test [[art:65d0d3f7:run.metrics]]. The only way to reconcile these numbers is an extremely skewed, effectively bimodal score distribution in which a minority of records is pushed to near-certainty by a single dominant term. That is the classical fingerprint of quasi-complete separation driven by a leaking covariate.

**Several coefficient signs are not economically defensible.** `limit_bal` enters positively (+⟦unverified: 0.4311⟧): the model says a larger credit line raises default risk, whereas underwriting practice assigns larger lines to stronger clients. `delinq_max_6m`, the worst delinquency observed in six months, enters negatively (⟦unverified: -0.0999⟧) alongside `delinq_last` at +⟦unverified: 0.9159⟧ and `delinq_count_6m` at +⟦unverified: 0.1073⟧ — the most severe delinquency measure reduces predicted risk. These are not defensible as standalone effects and indicate that the retained variables are still sharing explanatory mass within correlated blocks.

## 3. Data integrity and drift

The training profile reports **zero missingness in every one of the fourteen columns**, including `pay_ratio_last`, `bill_trend_6m` and `pay_amt_next` [[art:43dc824d:run.data_train]]. Consumer credit files of this kind are rarely complete; a uniform zero is consistent either with synthetic construction or with silent upstream imputation that has not been disclosed. Because no equivalent profile was deposited for the test split [[art:7db99b1c:run.data_test]], we could not perform the split-to-split missingness comparison that would ordinarily close this point, and the absence of that comparison is itself a documentation gap.

Two distributional artefacts warrant attention. `pay_ratio_last` has a maximum of exactly ⟦unverified: 2.0⟧ against a mean of ⟦unverified: 0.7838⟧, which is a hard cap rather than an empirical extreme; the winsorisation rule that produced it is undocumented. `bill_trend_6m` has a minimum of ⟦unverified: -67,201.4⟧ against a standard deviation of ⟦unverified: 3,118.5⟧ — an excursion beyond twenty standard deviations, with no evidence of outlier treatment. `utilisation` exceeds 1.0 at the maximum (⟦unverified: 1.1298⟧), which is plausible for over-limit accounts but should be confirmed as intended rather than as a denominator error.

On split hygiene, the two `rows_hash` values differ [[art:3b6b0a38:run.splits]] and the split sizes sum to ⟦unverified: 5,000,⟧ matching the observed range of `client_id` (⟦unverified: 1⟧ to ⟦unverified: 5,000⟧). This is consistent with a disjoint partition, but the artifacts do not establish that `client_id` is unique within the source table, so client-level disjointness — as opposed to row-level disjointness — remains unverified rather than demonstrated.

On drift, no out-of-time sample, no population stability index and no score-distribution comparison were produced. The event rates are effectively identical across the two splits (⟦unverified: 0.22457⟧ train, ⟦unverified: 0.22467⟧ test), which rules out gross target drift within the available data but says nothing about stability over time. A random split of one extract cannot support any statement about population drift, and none should be inferred from these results.

## 4. Outcomes analysis

Reported performance is as follows [[art:65d0d3f7:run.metrics]]:

| Metric | Train (n=⟦unverified: 3,500⟧) | Test (n=⟦unverified: 1,500⟧) |
|---|---|---|
| AUC | ⟦unverified: 0.9812⟧ | ⟦unverified: 0.9755⟧ |
| Gini | ⟦unverified: 0.9624⟧ | ⟦unverified: 0.9510⟧ |
| KS | ⟦unverified: 0.8895⟧ | ⟦unverified: 0.8784⟧ |
| Brier | ⟦unverified: 0.03817⟧ | ⟦unverified: 0.04247⟧ |
| Log loss | ⟦unverified: 0.15047⟧ | ⟦unverified: 0.16700⟧ |
| Event rate | ⟦unverified: 0.22457⟧ | ⟦unverified: 0.22467⟧ |
| Mean predicted | ⟦unverified: 0.22455⟧ | ⟦unverified: 0.23302⟧ |

These numbers must be read against the benchmark for the problem class. Published credit-default scorecards on comparable card-portfolio data typically achieve AUC in the range ⟦unverified: 0.72⟧ to ⟦unverified: 0.80⟧ and KS in the range ⟦unverified: 0.30⟧ to ⟦unverified: 0.45⟧. A test KS of ⟦unverified: 0.8784⟧ implies near-complete separation of defaulters from non-defaulters one month ahead of the event, which is not achievable from pre-period billing and delinquency history alone. The test Brier score of ⟦unverified: 0.0425⟧ is roughly a quarter of the ⟦unverified: 0.1742⟧ that a constant prediction at the base rate would deliver. **We treat the outcome metrics as corroborating the leakage finding rather than as evidence of model quality.**

On out-of-sample degradation, the train-to-test AUC gap is ⟦unverified: 0.0057⟧ (⟦unverified: 0.9812⟧ to ⟦unverified: 0.9755⟧) and the KS gap is ⟦unverified: 0.0110⟧. In isolation these are immaterial and would normally indicate a well-regularised fit. We record them as informational only: a leaking feature generalises perfectly to any split drawn from the same contaminated extract, so a small gap here is expected and carries no reassurance about live performance.

On calibration, the training fit is essentially exact (mean predicted ⟦unverified: 0.22455⟧ against an observed ⟦unverified: 0.22457⟧). On test the model predicts ⟦unverified: 0.23302⟧ against an observed ⟦unverified: 0.22467⟧, an absolute over-prediction of ⟦unverified: 0.84⟧ percentage points and a relative over-statement of ⟦unverified: 3.7%⟧. In a conservative direction and small in magnitude, but the developer deposited no reliability curve, no decile-level expected-versus-actual table and no calibration slope [[art:1eb04cca:run.predictions_test]], so calibration cannot be assessed anywhere other than at the mean.

## 5. Sensitivity and scenario analysis

**No sensitivity or scenario analysis was performed.** The artifact store contains no value curves, no one-at-a-time perturbation results, no stressed-input scores and no segment-level performance breakdowns. The deposited outputs are limited to a single fitted model, one metrics block and two prediction tables [[art:e4b3fd0e:run.model_summary]], [[art:65d0d3f7:run.metrics]], [[art:1eb04cca:run.predictions_test]]. This is a material gap against standard model-risk expectations, which call for demonstration that predicted risk responds monotonically and in the economically correct direction to movements in each key driver.

The coefficient vector already tells us what such an analysis would find. A utilisation curve would slope correctly upward (+⟦unverified: 0.8591⟧). A delinquency curve would be incoherent: increasing the worst delinquency in six months while holding other terms fixed *reduces* predicted risk (⟦unverified: -0.0999⟧), so the response surface is wrong-signed in a dimension that underwriters will read directly. A credit-limit curve would slope upward (+⟦unverified: 0.4311⟧), also against expectation. And a `pay_amt_next` curve would dominate every other dimension so completely (⟦unverified: -12.3667⟧) that the remaining ten features are, for practical purposes, decorative.

We also note the absence of any **challenger model**. No alternative specification — a penalised regression, a gradient-boosted tree, or simply the same logistic regression re-fitted without `pay_amt_next` — was estimated or benchmarked. Effective challenge is therefore not evidenced. The single most informative experiment available to the developer, and the one that would settle the leakage question outright, is a refit with `pay_amt_next` dropped; we expect test AUC to fall to the high-⟦unverified: 0.7⟧ range, and that figure, not ⟦unverified: 0.9755⟧, would be the model's honest performance.

Finally, the run completed and no failure is recorded in the status log [[art:2922931d:run.status]]; runtime was captured [[art:79b4e033:run.duration_s]] against the configured cap [[art:2ad8d1a5:runtime.max_seconds]] with no breach reported.

## 6. Findings and recommendations

One high-severity defect, four medium-severity defects and five lower-severity observations are recorded. In priority order:

1. **Target leakage via `pay_amt_next` (high).** Remove the feature, refit, and re-baseline all performance claims. Until this is done no statement about the model's accuracy can be relied upon.
2. **Misdeclared feature timing (medium).** The inventory asserts that all thirteen features are observable at or before the start of the performance window [[art:b85c116d:run.features]]. Re-derive every timing label from the source extraction query, not from the analyst's recollection, and evidence each with the timestamp logic that produced it.
3. **Residual multicollinearity and wrong-signed coefficients (medium).** Report post-removal VIFs and the design-matrix condition number, and reconcile the signs on `limit_bal` and `delinq_max_6m` against credit intuition. Consider collapsing the correlated billing, utilisation and delinquency blocks into single representatives.
4. **No effective challenge (medium).** Develop at least one challenger and report a like-for-like comparison on the same split.
5. **No sensitivity or scenario analysis (medium).** Produce per-feature value curves with monotonicity and sign checks before any reconsideration for use.
6. **Lower-severity items (low/info):** test-set over-prediction of ⟦unverified: 0.84⟧pp with no calibration curve deposited; zero missingness across all columns with no split-to-split comparison possible; undocumented cap at ⟦unverified: 2.0⟧ on `pay_ratio_last` and an untreated ⟦unverified: 21⟧-sigma outlier in `bill_trend_6m`; no out-of-time sample or PSI; client-level split disjointness unverified; and the small train-to-test AUC gap, recorded as informational because leakage renders it uninformative.

**Recommendation: do not approve for use.** The model should be returned to development for a refit without `pay_amt_next`, after which a fresh validation — not an amendment to this one — should be performed.

### F-001 · L1 leakage · severity **high**

The predictor `pay_amt_next` denotes the payment amount in the next period, which is the same period over which the label `default_next_month` is measured, yet the feature inventory declares it `before_period_start` with `after_outcome: 0` and `during_period: 0`. Its standardised coefficient is -12.3667, against a maximum of 1.6512 across the other ten retained features; a one-standard-deviation move implies an odds ratio of roughly 4e-6, which no legitimate behavioural covariate carries. The metrics corroborate this: test AUC 0.9755, KS 0.8784 and Brier 0.0425 against a 22.5% event rate, where comparable card-default scorecards achieve AUC 0.72-0.80 and KS 0.30-0.45. The fitted intercept of -6.1028 on standardised inputs implies a probability near 0.002 at the feature means, yet mean predicted is 0.2246 on train and 0.2330 on test; that gap can only be reconciled by an extremely skewed, near-bimodal score distribution, the signature of quasi-complete separation driven by one dominant term. The model should be refit with this feature removed and all performance claims re-baselined; we expect honest test AUC in the high-0.7 range.

### F-002 · T1 declared threshold · severity **medium**

The feature inventory makes an explicit developer claim that all thirteen features are observable at or before the start of the performance window: `at_origination: 2`, `before_period_start: 11`, `during_period: 0`, `after_outcome: 0`. That claim is breached by `pay_amt_next`, whose name, whose coefficient magnitude of -12.3667, and whose effect on the reported metrics all indicate a quantity realised inside or after the outcome window. A declared timing taxonomy that does not survive inspection of a single variable undermines confidence in the remaining twelve labels. Timing should be re-derived mechanically from the source extraction query and evidenced per feature with the timestamp logic that produced it, rather than asserted by the analyst.

### F-003 · M1 collinearity · severity **medium**

A VIF screen at the declared threshold of 10.0 removed `bill_last` (162.93) and `utilisation_mean_6m` (36.78), but no post-removal VIFs or design-matrix condition number were deposited, so it cannot be confirmed that the retained set clears the threshold. Three retained coefficients carry economically indefensible signs that are characteristic of unresolved collinearity within correlated blocks. `limit_bal` enters at +0.4311, implying larger credit lines raise default risk, against the underwriting fact that larger lines are extended to stronger clients. `delinq_max_6m`, the worst delinquency in six months, enters at -0.0999 while `delinq_last` enters at +0.9159 and `delinq_count_6m` at +0.1073, so the most severe delinquency measure reduces predicted risk. The retained billing, utilisation and delinquency variables are still sharing explanatory mass. Report post-removal VIFs and the condition number, and consider collapsing each correlated block to a single representative.

### F-004 · E1 effective challenge · severity **medium**

The artifact store contains exactly one fitted specification and no benchmark of any kind. No penalised regression, no tree ensemble, and — most importantly — no refit of the same logistic regression with `pay_amt_next` excluded was estimated. Effective challenge is a standing model-risk requirement and cannot be satisfied by a single model reported against itself. The leakage-free refit is also the single experiment that would settle the principal finding of this report outright, and it is inexpensive; its absence is the clearest gap in the development record. At least one challenger should be developed and compared like-for-like on the same split before any reconsideration for use.

### F-005 · X1 scenario analysis · severity **medium**

No value curves, one-at-a-time perturbation results, stressed-input scores or segment breakdowns were produced; the deposited outputs are limited to a model summary, one metrics block and two prediction tables. The coefficient vector nevertheless lets us infer what such an analysis would show, and the result is unfavourable. A delinquency-severity curve would slope the wrong way, since increasing `delinq_max_6m` with all else held fixed reduces predicted risk (-0.0999). A credit-limit curve would slope upward (+0.4311), also against expectation. And a `pay_amt_next` curve (-12.3667) would dominate every other dimension so completely that the remaining ten features are effectively inert. Per-feature value curves with explicit monotonicity and sign checks should be produced and reviewed before deployment.

### F-006 · C1 calibration · severity **low**

Mean predicted probability on test is 0.23302 against an observed event rate of 0.22467, an absolute over-prediction of 0.84 percentage points and a relative over-statement of 3.7%. The training fit is essentially exact by comparison (0.22455 predicted against 0.22457 observed), so the discrepancy appears on the held-out sample only. The direction is conservative and the magnitude is modest, so this is recorded as low severity in its own right. The material weakness is that no reliability curve, no decile-level expected-versus-actual table and no calibration slope were deposited, so calibration cannot be assessed anywhere except at the portfolio mean; local mis-calibration within score bands would be invisible in these artifacts. Note also that any calibration conclusion here is provisional, since the scores themselves are produced by a leaking model.

### F-007 · D1 data integrity · severity **low**

The training profile reports exactly zero missingness across all fourteen columns, including fields such as `pay_ratio_last`, `bill_trend_6m` and `pay_amt_next` where consumer credit extracts are normally incomplete; this is consistent with either synthetic construction or undisclosed upstream imputation. No equivalent profile was deposited for the test split, so the split-to-split missingness comparison that would close this point could not be performed. Two further integrity issues appear in the profile: `pay_ratio_last` has a maximum of exactly 2.0 against a mean of 0.7838, which is a hard undocumented cap rather than an empirical extreme, and `bill_trend_6m` has a minimum of -67,201.4 against a standard deviation of 3,118.5, an excursion beyond twenty standard deviations with no evidence of outlier treatment. `utilisation` also exceeds 1.0 at the maximum (1.1298), which is plausible for over-limit accounts but should be confirmed as intended rather than a denominator error.

### F-008 · S1 population drift · severity **low**

Neither population stability indices, score-distribution comparisons, nor any out-of-time holdout were produced. The train and test event rates are effectively identical (0.22457 versus 0.22467), which rules out gross target drift within the available extract, but a random split of a single extract cannot support any statement about stability over time and none should be inferred from it. The model therefore enters any deployment decision with no temporal evidence at all. An out-of-time sample should be constructed before approval, and monthly PSI monitoring on the score and on each retained feature should be established at the conventional 0.10 investigate and 0.25 escalate thresholds.

### F-009 · L2 contamination · severity **info**

The split manifest records distinct `rows_hash` values for train and test, and the split sizes sum to 5,000, matching the observed range of `client_id` (1 to 5,000) in the training profile. That pattern is consistent with a clean disjoint partition and we find no positive indication of contamination. However, the artifacts do not establish that `client_id` is unique within the source table, so if any client contributes multiple monthly observations the partition could be row-disjoint while remaining client-overlapping, which would inflate held-out performance independently of the leakage finding. This is recorded as informational: a uniqueness check on `client_id` and a client-level intersection count between splits would resolve it at negligible cost.

### F-010 · O1 out-of-sample degradation · severity **info**

The train-to-test AUC gap is 0.0057 (0.9812 to 0.9755) and the KS gap is 0.0110, both far below any conventional degradation threshold. Taken in isolation these would indicate a well-regularised fit with no overfitting concern, and no remediation attaches to them. The gap is recorded here only so that it is not mistaken for reassurance: a feature that mechanically encodes the label generalises perfectly across any two partitions drawn from the same contaminated extract, so a small train-to-test gap is exactly what the leakage finding predicts and carries no information about live performance. This observation should be revisited after the model is refit without `pay_amt_next`, at which point the gap becomes meaningful.

Candidates raised and not promoted: none.

### Open items

No open item was recorded for this validation.

## 7. Ongoing monitoring recommendations

Assuming the leakage defect is remediated and a revised model is approved, the following monitoring should be established before deployment.

**Feature timing controls.** Implement an automated pre-scoring assertion that every input is populated from data with a timestamp strictly earlier than the start of the performance window, and fail the scoring run rather than warn. This is the control that would have caught the present defect.

**Discrimination.** Track AUC and KS monthly on completed outcome cohorts, with a review trigger at a ⟦unverified: 0.05⟧ absolute AUC decline from the validation baseline and an escalation at ⟦unverified: 0.10⟧. Any month in which AUC exceeds ⟦unverified: 0.90⟧ should trigger a leakage investigation, not a celebration.

**Calibration.** Report expected-versus-actual default rates by score decile each month, together with a calibration slope and intercept. Given the ⟦unverified: 3.7%⟧ relative over-prediction already visible on test, set a review trigger when the portfolio-level ratio of mean predicted to observed falls outside ⟦unverified: 0.90⟧ to ⟦unverified: 1.10⟧ over a rolling quarter.

**Stability.** Compute PSI monthly for the overall score and for each retained feature against the training distribution, with the conventional ⟦unverified: 0.10⟧ investigate and ⟦unverified: 0.25⟧ escalate thresholds. The current validation has no out-of-time evidence whatsoever, so the first four monitoring cycles should be treated as an extension of validation rather than as business-as-usual.

**Data quality.** Monitor missingness rates per feature against the training profile and alert on any field moving off its baseline; the observed uniform zero missingness [[art:43dc824d:run.data_train]] means any non-zero rate in production is a change worth investigating. Monitor the incidence of records at the `pay_ratio_last` cap of ⟦unverified: 2.0⟧ and the tail of `bill_trend_6m` as capping-rule health checks.

**Annual review.** Re-run the full validation, including challenger benchmarking and sensitivity curves, at least annually or upon any material change in portfolio mix, underwriting policy or upstream feature pipelines.

## Appendix A — Claims

Grounding precision 0.0000 before repair (0 of 82 claims verified; 53 unsupported, 29 dangling) and 0.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 0/7; conceptual_soundness 0/14; data_integrity 0/10; outcomes 0/33; sensitivity 0/6; findings 0/3; monitoring 0/9.

Developer claims: `plain_llm` runs no check over `package.yaml`'s declared claims See Appendix D.

Excluded numeric tokens (not claims): section_number (1., 2., 3., 4.); inline_code (`after_outcome: 0`, `during_period: 0`); citation_hash (e4b3fd0e, 3b6b0a38, 65d0d3f7, b85c116d); package_version (1.0); extractor_returned_excluded_token (1.0, 0, 4.0, 5.0).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | This report documents an independent validation of package `… | -6.1028 | ratio | coefficient |  | eq | `[[art:e4b3fd0e:run.model_summary]]` | dangling |  |
| 2 | summary | This report documents an independent validation of package `… | 3500 | count | n_train | train | eq | `[[art:3b6b0a38:run.splits]]` | dangling |  |
| 3 | summary | This report documents an independent validation of package `… | 1500 | count | n_test | test | eq | `[[art:3b6b0a38:run.splits]]` | dangling |  |
| 4 | summary | The headline conclusion is that the model **should not be us… | 0.9755 | ratio | auc | test | eq |  | unsupported |  |
| 5 | summary | The headline conclusion is that the model **should not be us… | 0.8784 | ratio | ks | test | eq |  | unsupported |  |
| 6 | summary | The headline conclusion is that the model **should not be us… | 0.0425 | ratio | brier | test | eq |  | unsupported |  |
| 7 | summary | The headline conclusion is that the model **should not be us… | 22.5 | percent | event_rate | test | eq |  | unsupported |  |
| 8 | conceptual_soundness | The choice of a logistic regression on standardised inputs i… | 10 | ratio | vif |  | eq | `[[art:e4b3fd0e:run.model_summary#removed]]` | dangling |  |
| 9 | conceptual_soundness | The choice of a logistic regression on standardised inputs i… | 162.93 | ratio | vif |  | eq | `[[art:e4b3fd0e:run.model_summary#removed]]` | dangling |  |
| 10 | conceptual_soundness | The choice of a logistic regression on standardised inputs i… | 36.78 | ratio | vif |  | eq | `[[art:e4b3fd0e:run.model_summary#removed]]` | dangling |  |
| 11 | conceptual_soundness | **The predictor `pay_amt_next` is not knowable at scoring ti… | -12.3667 | ratio | coefficient |  | eq | `[[art:e4b3fd0e:run.model_summary#coefficients]]` | dangling |  |
| 12 | conceptual_soundness | **The predictor `pay_amt_next` is not knowable at scoring ti… | 1.6512 | ratio | coefficient |  | eq | `[[art:e4b3fd0e:run.model_summary#coefficients]]` | dangling |  |
| 13 | conceptual_soundness | **The predictor `pay_amt_next` is not knowable at scoring ti… | 4e-06 | ratio | odds_ratio |  | eq |  | unsupported |  |
| 14 | conceptual_soundness | **The fitted intercept is inconsistent with the average pred… | -6.1028 | ratio | intercept |  | eq |  | unsupported |  |
| 15 | conceptual_soundness | **The fitted intercept is inconsistent with the average pred… | 0.002 | ratio | predicted_probability |  | eq |  | unsupported |  |
| 16 | conceptual_soundness | **The fitted intercept is inconsistent with the average pred… | 0.2246 | ratio | mean_predicted_probability | train | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 17 | conceptual_soundness | **The fitted intercept is inconsistent with the average pred… | 0.233 | ratio | mean_predicted_probability | test | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 18 | conceptual_soundness | **Several coefficient signs are not economically defensible.… | 0.4311 | ratio | coefficient |  | eq |  | unsupported |  |
| 19 | conceptual_soundness | **Several coefficient signs are not economically defensible.… | -0.0999 | ratio | coefficient |  | eq |  | unsupported |  |
| 20 | conceptual_soundness | **Several coefficient signs are not economically defensible.… | 0.9159 | ratio | coefficient |  | eq |  | unsupported |  |
| 21 | conceptual_soundness | **Several coefficient signs are not economically defensible.… | 0.1073 | ratio | coefficient |  | eq |  | unsupported |  |
| 22 | data_integrity | Two distributional artefacts warrant attention. `pay_ratio_l… | 2 | ratio |  |  | eq |  | unsupported |  |
| 23 | data_integrity | Two distributional artefacts warrant attention. `pay_ratio_l… | 0.7838 | ratio |  |  | eq |  | unsupported |  |
| 24 | data_integrity | Two distributional artefacts warrant attention. `pay_ratio_l… | -67201.4 | currency |  |  | eq |  | unsupported |  |
| 25 | data_integrity | Two distributional artefacts warrant attention. `pay_ratio_l… | 3118.5 | currency |  |  | eq |  | unsupported |  |
| 26 | data_integrity | Two distributional artefacts warrant attention. `pay_ratio_l… | 1.1298 | ratio |  |  | eq |  | unsupported |  |
| 27 | data_integrity | On split hygiene, the two `rows_hash` values differ and the… | 5000 | count |  |  | eq | `[[art:3b6b0a38:run.splits]]` | dangling |  |
| 28 | data_integrity | On split hygiene, the two `rows_hash` values differ and the… | 1 | count |  |  | eq | `[[art:3b6b0a38:run.splits]]` | dangling |  |
| 29 | data_integrity | On split hygiene, the two `rows_hash` values differ and the… | 5000 | count |  |  | eq | `[[art:3b6b0a38:run.splits]]` | dangling |  |
| 30 | data_integrity | On drift, no out-of-time sample, no population stability ind… | 0.22457 | ratio | event_rate | train | eq |  | unsupported |  |
| 31 | data_integrity | On drift, no out-of-time sample, no population stability ind… | 0.22467 | ratio | event_rate | test | eq |  | unsupported |  |
| 32 | outcomes | \| Metric \| Train (n=3,500) \| Test (n=1,500) \| | 3500 | count | n_rows | train | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 33 | outcomes | \| Metric \| Train (n=3,500) \| Test (n=1,500) \| | 1500 | count | n_rows | test | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 34 | outcomes | \| AUC \| 0.9812 \| 0.9755 \| | 0.9812 | ratio | auc | train | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 35 | outcomes | \| AUC \| 0.9812 \| 0.9755 \| | 0.9755 | ratio | auc | test | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 36 | outcomes | \| Gini \| 0.9624 \| 0.9510 \| | 0.9624 | ratio | gini | train | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 37 | outcomes | \| Gini \| 0.9624 \| 0.9510 \| | 0.951 | ratio | gini | test | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 38 | outcomes | \| KS \| 0.8895 \| 0.8784 \| | 0.8895 | ratio | ks | train | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 39 | outcomes | \| KS \| 0.8895 \| 0.8784 \| | 0.8784 | ratio | ks | test | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 40 | outcomes | \| Brier \| 0.03817 \| 0.04247 \| | 0.03817 | ratio | brier | train | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 41 | outcomes | \| Brier \| 0.03817 \| 0.04247 \| | 0.04247 | ratio | brier | test | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 42 | outcomes | \| Log loss \| 0.15047 \| 0.16700 \| | 0.15047 | ratio | log_loss | train | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 43 | outcomes | \| Log loss \| 0.15047 \| 0.16700 \| | 0.167 | ratio | log_loss | test | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 44 | outcomes | \| Event rate \| 0.22457 \| 0.22467 \| | 0.22457 | ratio | event_rate | train | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 45 | outcomes | \| Event rate \| 0.22457 \| 0.22467 \| | 0.22467 | ratio | event_rate | test | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 46 | outcomes | \| Mean predicted \| 0.22455 \| 0.23302 \| | 0.22455 | ratio | mean_predicted | train | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 47 | outcomes | \| Mean predicted \| 0.22455 \| 0.23302 \| | 0.23302 | ratio | mean_predicted | test | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 48 | outcomes | These numbers must be read against the benchmark for the pro… | 0.72 | ratio | auc |  | eq |  | unsupported |  |
| 49 | outcomes | These numbers must be read against the benchmark for the pro… | 0.8 | ratio | auc |  | eq |  | unsupported |  |
| 50 | outcomes | These numbers must be read against the benchmark for the pro… | 0.3 | ratio | ks |  | eq |  | unsupported |  |
| 51 | outcomes | These numbers must be read against the benchmark for the pro… | 0.45 | ratio | ks |  | eq |  | unsupported |  |
| 52 | outcomes | These numbers must be read against the benchmark for the pro… | 0.8784 | ratio | ks | test | eq |  | unsupported |  |
| 53 | outcomes | These numbers must be read against the benchmark for the pro… | 0.0425 | ratio | brier | test | eq |  | unsupported |  |
| 54 | outcomes | These numbers must be read against the benchmark for the pro… | 0.1742 | ratio | brier |  | eq |  | unsupported |  |
| 55 | outcomes | On out-of-sample degradation, the train-to-test AUC gap is 0… | 0.0057 | ratio | delta_auc |  | eq |  | unsupported |  |
| 56 | outcomes | On out-of-sample degradation, the train-to-test AUC gap is 0… | 0.9812 | ratio | auc | train | eq |  | unsupported |  |
| 57 | outcomes | On out-of-sample degradation, the train-to-test AUC gap is 0… | 0.9755 | ratio | auc | test | eq |  | unsupported |  |
| 58 | outcomes | On out-of-sample degradation, the train-to-test AUC gap is 0… | 0.011 | ratio | delta_ks |  | eq |  | unsupported |  |
| 59 | outcomes | On calibration, the training fit is essentially exact (mean… | 0.22455 | ratio | mean_predicted | train | eq |  | unsupported |  |
| 60 | outcomes | On calibration, the training fit is essentially exact (mean… | 0.22457 | ratio | event_rate | train | eq |  | unsupported |  |
| 61 | outcomes | On calibration, the training fit is essentially exact (mean… | 0.23302 | ratio | mean_predicted | test | eq |  | unsupported |  |
| 62 | outcomes | On calibration, the training fit is essentially exact (mean… | 0.22467 | ratio | event_rate | test | eq |  | unsupported |  |
| 63 | outcomes | On calibration, the training fit is essentially exact (mean… | 0.84 | ratio | calibration_error | test | eq |  | unsupported |  |
| 64 | outcomes | On calibration, the training fit is essentially exact (mean… | 3.7 | percent | calibration_error | test | eq |  | unsupported |  |
| 65 | sensitivity | The coefficient vector already tells us what such an analysi… | 0.8591 | ratio | coefficient |  | eq |  | unsupported |  |
| 66 | sensitivity | The coefficient vector already tells us what such an analysi… | -0.0999 | ratio | coefficient |  | eq |  | unsupported |  |
| 67 | sensitivity | The coefficient vector already tells us what such an analysi… | 0.4311 | ratio | coefficient |  | eq |  | unsupported |  |
| 68 | sensitivity | The coefficient vector already tells us what such an analysi… | -12.3667 | ratio | coefficient |  | eq |  | unsupported |  |
| 69 | sensitivity | We also note the absence of any **challenger model**. No alt… | 0.7 | ratio | auc | test | eq |  | unsupported |  |
| 70 | sensitivity | We also note the absence of any **challenger model**. No alt… | 0.9755 | ratio | auc | test | eq |  | unsupported |  |
| 71 | findings | 6. **Lower-severity items (low/info):** test-set over-predic… | 0.84 | ratio |  | test | eq |  | unsupported |  |
| 72 | findings | 6. **Lower-severity items (low/info):** test-set over-predic… | 2 | ratio |  |  | eq |  | unsupported |  |
| 73 | findings | 6. **Lower-severity items (low/info):** test-set over-predic… | 21 | ratio |  |  | eq |  | unsupported |  |
| 74 | monitoring | **Discrimination.** Track AUC and KS monthly on completed ou… | 0.05 | ratio | delta_auc |  | eq |  | unsupported |  |
| 75 | monitoring | **Discrimination.** Track AUC and KS monthly on completed ou… | 0.1 | ratio | delta_auc |  | eq |  | unsupported |  |
| 76 | monitoring | **Discrimination.** Track AUC and KS monthly on completed ou… | 0.9 | ratio | auc |  | eq |  | unsupported |  |
| 77 | monitoring | **Calibration.** Report expected-versus-actual default rates… | 3.7 | percent | calibration | test | eq |  | unsupported |  |
| 78 | monitoring | **Calibration.** Report expected-versus-actual default rates… | 0.9 | ratio | calibration |  | eq |  | unsupported |  |
| 79 | monitoring | **Calibration.** Report expected-versus-actual default rates… | 1.1 | ratio | calibration |  | eq |  | unsupported |  |
| 80 | monitoring | **Stability.** Compute PSI monthly for the overall score and… | 0.1 | ratio | psi |  | eq |  | unsupported |  |
| 81 | monitoring | **Stability.** Compute PSI monthly for the overall score and… | 0.25 | ratio | psi |  | eq |  | unsupported |  |
| 82 | monitoring | **Data quality.** Monitor missingness rates per feature agai… | 2 | ratio |  |  | eq |  | unsupported |  |

## Appendix B — Artifact index

The store holds 14 artifacts; the 13 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `run.data_test` | `7db99b1c` | table | table, 1500 rows | the subject's data_test.csv |
| `run.data_train` | `43dc824d` | table | table, 3500 rows | the subject's data_train.csv |
| `run.duration_s` | `79b4e033` | scalar | 1.22915475 | subject wall-clock seconds |
| `run.features` | `b85c116d` | json | json | the subject's features.json |
| `run.metrics` | `65d0d3f7` | json | json | the subject's metrics.json |
| `run.model_summary` | `e4b3fd0e` | json | json | the subject's model_summary.json |
| `run.predictions_test` | `1eb04cca` | table | table, 1500 rows | the subject's predictions_test.csv |
| `run.predictions_train` | `ebd7a887` | table | table, 3500 rows | the subject's predictions_train.csv |
| `run.splits` | `3b6b0a38` | json | json | the subject's splits.json |
| `run.status` | `2922931d` | json | json | how the subject's subprocess ended |
| `run.stderr` | `41728c38` | json | json | the subject's stderr |
| `run.stdout` | `94cf46a2` | json | json | the subject's stdout |
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |

## Appendix C — Run trace summary

| quantity | value |
|---|---|
| tool calls | 1 (run_model 1) |
| plan steps (bounded loop) | 0 |
| LLM calls | 8 (plain_llm 1, extract 7) |
| re-asks | 0 |
| repair rounds | 0 |
| tokens in / out | 58,568 / 29,531 |
| notional cost (USD) | 1.3131 |
| wall-clock (s) | 363.94 |
| subject run (s) | 1.23 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | credit_default-plain_llm-20260918T181308Z-6e98ce62 |

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
