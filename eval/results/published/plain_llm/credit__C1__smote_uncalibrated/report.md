---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: plain_llm
model: claude-opus-5[1m]
run_id: credit_default-plain_llm-20260918T081650Z-6e98ce62
data_mode: synthetic
synthetic_n: 5000
grounding_precision_pre: 0.0068
grounding_precision_post: 0.0068
n_claims: 146
n_findings_by_severity: {high: 1, medium: 4, low: 4, info: 0}
generated: "2026-09-18T08:16:50Z"
illustrative: false
---

# Validation report — `credit_default` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `credit_default` v1.0 | `plain_llm` | claude-opus-5[1m] | synthetic, n = 5000 | 0.0068 → 0.0068 | 1 / 4 / 4 / 0 |
<!-- quaestor:renderer:end -->

This report documents an independent validation of package `credit_default`, version 1.0, a binary classification model that predicts the target `default_next_month` for a credit card portfolio. The subject is a standardised logistic regression estimated on ⟦unverified: 3,500⟧ training rows with a ⟦unverified: 1,500⟧-row test split ([[art:3986de2e:run.model_summary]], [[art:3b6b0a38:run.splits]]).

The material reviewed consists solely of the subject's own declarations and outputs: the metric block [[art:d89e6798:run.metrics]], the model summary [[art:3986de2e:run.model_summary]], the feature inventory [[art:abbb748e:run.features]], the split manifest [[art:3b6b0a38:run.splits]], the scored tables [[art:ef97fb76:run.predictions_test]] and [[art:c259f6c7:run.predictions_train]], the source tables [[art:6a89f2be:run.data_train]] and [[art:26fbbf1d:run.data_test]], and the run telemetry [[art:2922931d:run.status]], [[art:ad0e4ee8:run.stdout]], [[art:41728c38:run.stderr]], [[art:e273f4fd:run.duration_s]] and [[art:2ad8d1a5:runtime.max_seconds]]. No independent re-estimation, no challenger model, no regime segmentation, and no scenario grid were available to the validator; conclusions that depend on those exercises are recorded as limitations rather than as clean passes.

**Overall opinion.** The model discriminates acceptably but does not produce usable probabilities. Test AUC is ⟦unverified: 0.7764⟧ with KS ⟦unverified: 0.4656⟧, and out-of-sample degradation is effectively nil. However, mean predicted probability on test is ⟦unverified: 0.4379⟧ against an observed event rate of ⟦unverified: 0.2247⟧ — an over-prediction of roughly ⟦unverified: 1.95⟧x — and the resulting Brier score (⟦unverified: 0.1929⟧) and log loss (⟦unverified: 0.5935⟧) are both *worse* than those of a constant predictor set at the base rate (⟦unverified: 0.1742⟧ and ⟦unverified: 0.5328⟧ respectively). A model whose probabilistic accuracy is beaten by the portfolio average cannot be used for expected-loss, provisioning, or pricing purposes as it stands. Use should be restricted to rank-ordering applications until the score is recalibrated.

## 2. Conceptual soundness

The model form — standardised logistic regression with an explicit VIF screen — is appropriate and transparent for a retail default application, and is defensible against the regulatory expectation that credit decisioning be explainable.

**Feature timing.** The inventory in [[art:abbb748e:run.features]] declares ⟦unverified: 12⟧ candidate features, of which ⟦unverified: 2⟧ are `at_origination` and ⟦unverified: 10⟧ are `before_period_start`; the counts for `during_period` and `after_outcome` are both zero ([[art:abbb748e:run.features#during_period]], [[art:abbb748e:run.features#after_outcome]]). Taken at face value, every predictor is observable before the performance window opens, and no target leakage is declared. The validator notes that no single-feature discrimination diagnostic was produced, so the leakage screen rests entirely on the developer's timing labels rather than on an empirical check; no individual coefficient magnitude in [[art:3986de2e:run.model_summary#coefficients]] is large enough to suggest a near-deterministic predictor.

**Variable selection.** Two features were dropped for multicollinearity against a declared threshold of ⟦unverified: 10.0⟧: `bill_last` at VIF ⟦unverified: 160.9⟧ and `utilisation_mean_6m` at VIF ⟦unverified: 36.4⟧ ([[art:3986de2e:run.model_summary#removed]]). The stated threshold was therefore honoured, and the screen itself is sound practice. What the screen does not resolve is that the surviving specification still contains three overlapping billing/utilisation constructs (`utilisation`, `bill_mean_6m`, `bill_trend_6m`) and three overlapping delinquency constructs (`delinq_last`, `delinq_count_6m`, `delinq_max_6m`). No post-removal VIF values or condition number were reported, so the validator cannot confirm that the retained design matrix is well conditioned.

**Coefficient signs.** With standardised inputs, the fitted coefficients ([[art:3986de2e:run.model_summary#coefficients]]) are economically plausible for the risk drivers — `delinq_last` +⟦unverified: 1.0228⟧, `delinq_count_6m` +⟦unverified: 0.1404⟧, `delinq_max_6m` +⟦unverified: 0.0135⟧, `utilisation` +⟦unverified: 0.4769⟧, `age` ⟦unverified: -0.0763⟧, `pay_ratio_last` ⟦unverified: -0.0918⟧, `pay_ratio_mean_6m` ⟦unverified: -0.1725⟧. Three signs are counterintuitive and warrant challenge:

| Feature | Coefficient | Expected sign | Comment |
|---|---|---|---|
| `bill_mean_6m` | ⟦unverified: -0.2763⟧ | positive | Larger average balances associated with *lower* default odds |
| `bill_trend_6m` | ⟦unverified: -0.2180⟧ | positive | Rising balances associated with *lower* default odds |
| `limit_bal` | +⟦unverified: 0.0163⟧ | negative | Higher granted limit (a proxy for underwritten quality) associated with *higher* default odds |

The most likely explanation is residual correlation between `utilisation` and the two billing terms: `utilisation` absorbs the risk signal and the billing terms take offsetting negative loadings. This is a stability concern rather than a fit concern, but it means the individual coefficients cannot be interpreted or used for reason-code generation without further work.

**Intercept.** The fitted intercept is +0.0674 ([[art:3986de2e:run.model_summary#intercept]]). Because the features are standardised, the linear predictor has mean equal to the intercept, implying a central predicted probability near ⟦unverified: 0.517⟧ on a population whose prevalence is ⟦unverified: 0.2246⟧. This is the signature of an estimation sample balanced to roughly ⟦unverified: 50⟧/⟦unverified: 50,⟧ yet the summary declares `class_weight: null` ([[art:3986de2e:run.model_summary#class_weight]]). The declaration and the fitted object are not reconcilable, and this is the root cause of the calibration defect in section 4.

## 3. Data integrity and drift

The training profile of [[art:6a89f2be:run.data_train]] reports ⟦unverified: 3,500⟧ rows with zero missing values in every one of the thirteen columns, including the target. Complete data across ⟦unverified: 45,500⟧ cells is unusual for retail credit and suggests either a pre-cleaned extract or an imputation step applied upstream of profiling; neither is documented.

Several distributional features deserve comment. `pay_ratio_last` has a maximum of exactly ⟦unverified: 2.0000⟧ against a minimum of ⟦unverified: 0.00077⟧, which is the fingerprint of an undocumented cap rather than a naturally occurring bound; `pay_ratio_mean_6m` reaches only ⟦unverified: 1.6385⟧, consistent with the cap binding on the single-month series alone. `utilisation` ranges to ⟦unverified: 1.1297⟧, i.e. over-limit accounts are retained rather than truncated, which is defensible but should be stated. `bill_trend_6m` is heavily left-skewed (mean ⟦unverified: -237.6⟧, min ⟦unverified: -67,201,⟧ max +⟦unverified: 27,398⟧) and `bill_mean_6m` spans two orders of magnitude (⟦unverified: 429⟧ to ⟦unverified: 506,281⟧) with no winsorisation; standardisation rescales but does not tame the influence of these tails on a logistic fit. Finally, `client_id` is carried in the profiled frame with a range of ⟦unverified: 1⟧ to ⟦unverified: 5,000⟧ across a ⟦unverified: 5,000⟧-row universe; it is not in the feature inventory and is correctly excluded from the model, but its presence in the modelling frame is an avoidable identifier-leakage hazard.

**Split integrity.** [[art:3b6b0a38:run.splits]] records distinct row hashes for the two partitions (train `e028347d…`, test `3e28943d…`), and the split sizes reconcile with `n_train` in [[art:3986de2e:run.model_summary#n_train]]. The hashes establish that the two row sets are not identical; they do not establish that no individual client appears in both. Given that ⟦unverified: 3,500⟧ + ⟦unverified: 1,500⟧ exactly exhausts the ⟦unverified: 1⟧–⟦unverified: 5,000⟧ identifier range, a disjoint split is plausible, but no overlap statistic was computed and the validator cannot close this point from [[art:6a89f2be:run.data_train]] and [[art:26fbbf1d:run.data_test]] alone.

**Missingness comparison.** A profile was supplied for the training split only. Without the corresponding profile of [[art:26fbbf1d:run.data_test]], the split-to-split missingness comparison required by the data integrity standard could not be performed.

**Drift.** No population stability index, score PSI, or characteristic-level drift measure appears anywhere in the artifact store. The only comparison available is the event rate, which is ⟦unverified: 0.2246⟧ in train and ⟦unverified: 0.2247⟧ in test ([[art:3b6b0a38:run.splits]]) — reassuring as to target prevalence, but silent as to covariate or score drift. Since the split appears to be random rather than out-of-time, no meaningful drift conclusion is available in any case: the model has never been tested on a forward period.

## 4. Outcomes analysis

All figures below are from [[art:d89e6798:run.metrics]].

| Metric | Train (n=⟦unverified: 3,500⟧) | Test (n=⟦unverified: 1,500⟧) | Gap |
|---|---|---|---|
| AUC | ⟦unverified: 0.7765⟧ | ⟦unverified: 0.7764⟧ | ⟦unverified: -0.0001⟧ |
| Gini | ⟦unverified: 0.5530⟧ | ⟦unverified: 0.5527⟧ | ⟦unverified: -0.0003⟧ |
| KS | ⟦unverified: 0.4801⟧ | ⟦unverified: 0.4656⟧ | ⟦unverified: -0.0145⟧ |
| Brier | ⟦unverified: 0.1969⟧ | ⟦unverified: 0.1929⟧ | ⟦unverified: -0.0040⟧ |
| Log loss | ⟦unverified: 0.6031⟧ | ⟦unverified: 0.5935⟧ | ⟦unverified: -0.0096⟧ |
| Event rate | ⟦unverified: 0.2246⟧ | ⟦unverified: 0.2247⟧ | +⟦unverified: 0.0001⟧ |
| Mean predicted | ⟦unverified: 0.4427⟧ | ⟦unverified: 0.4379⟧ | ⟦unverified: -0.0048⟧ |

**Discrimination.** Test AUC of ⟦unverified: 0.7764⟧ (Gini ⟦unverified: 0.5527⟧, KS ⟦unverified: 0.4656⟧) is within the range normally regarded as acceptable for a retail default scorecard. Gini reconciles exactly with ⟦unverified: 2⟧·AUC−⟦unverified: 1,⟧ and the metric block is internally consistent.

**Out-of-sample stability.** The train-to-test AUC gap is ⟦unverified: 0.0001⟧ — for practical purposes, zero. A ten-parameter logistic model on ⟦unverified: 3,500⟧ rows is heavily over-determined and should not overfit materially, so a small gap is expected; a gap this close to zero, with test Brier and log loss actually *better* than train, is at the outer edge of what a random split ordinarily produces and is one of the reasons the validator flags the absence of an overlap check in section 3. There is no evidence of out-of-sample degradation, and no O1 finding is raised.

**Calibration.** This is where the model fails. Mean predicted probability on test is ⟦unverified: 0.4379⟧ against an observed rate of ⟦unverified: 0.2247⟧, a ratio of ⟦unverified: 1.95⟧:⟦unverified: 1⟧; the same pattern holds in train (⟦unverified: 0.4427⟧ vs ⟦unverified: 0.2246⟧). In log-odds terms the score sits about ⟦unverified: 0.99⟧ too high: logit(⟦unverified: 0.2247⟧) = −⟦unverified: 1.2385⟧ while logit(⟦unverified: 0.4379⟧) = −⟦unverified: 0.2497⟧. Expressed on a ⟦unverified: 1,500⟧-account test book, the model expects roughly ⟦unverified: 657⟧ defaults where ⟦unverified: 337⟧ occurred.

The consequences are quantitative, not cosmetic. A constant predictor that simply assigns every account the base rate of ⟦unverified: 0.2247⟧ achieves a Brier score of p(⟦unverified: 1⟧−p) = ⟦unverified: 0.1742⟧ and a log loss of ⟦unverified: 0.5328⟧. The subject model scores ⟦unverified: 0.1929⟧ and ⟦unverified: 0.5935⟧ — ⟦unverified: 10.7%⟧ and ⟦unverified: 11.4%⟧ worse respectively. Despite genuine rank-ordering power, the level error is severe enough to destroy all of it and more on any probability-weighted metric. Any downstream use that multiplies the score by an exposure — expected loss, IFRS ⟦unverified: 9⟧ / CECL provisioning, risk-based pricing, limit assignment — would roughly double the loss estimate.

As set out in section 2, the arithmetic points to a specific cause rather than to generic miscalibration: a near-zero intercept on standardised features centres the score near ⟦unverified: 0.5⟧, which is what an estimation sample balanced to ⟦unverified: 50⟧/⟦unverified: 50⟧ produces. The declared `class_weight: null` is inconsistent with that. The remedy is correspondingly cheap: refit on the unweighted population, or apply a prior-correction offset of approximately −⟦unverified: 0.99⟧ to the linear predictor, then re-verify the slope on a held-out decile plot.

## 5. Sensitivity and scenario analysis

No scenario artifact, stress grid, partial-dependence output, or value/profitability curve exists in the store, so the X1 scenario test could not be executed as specified. What follows is what can be inferred from the fitted coefficients in [[art:3986de2e:run.model_summary#coefficients]] and the input distributions in [[art:6a89f2be:run.data_train]].

**Univariate sensitivity.** Because the inputs are standardised, coefficient magnitude is directly comparable. A one-standard-deviation deterioration in `delinq_last` (+⟦unverified: 1.32⟧ missed payments) moves the log-odds by +⟦unverified: 1.0228⟧, i.e. an odds multiplier of ⟦unverified: 2.78⟧; this single variable dominates the model, contributing more than twice the effect of the next largest term. `utilisation` follows at +⟦unverified: 0.4769⟧ per ⟦unverified: 0.234⟧ of utilisation (odds ×⟦unverified: 1.61⟧). Everything else is second-order: the two billing terms at −⟦unverified: 0.2763⟧ and −⟦unverified: 0.2180⟧, `pay_ratio_mean_6m` at −⟦unverified: 0.1725⟧, `delinq_count_6m` at +⟦unverified: 0.1404⟧, and a tail of near-null effects (`pay_ratio_last` −⟦unverified: 0.0918⟧, `age` −⟦unverified: 0.0763⟧, `limit_bal` +⟦unverified: 0.0163⟧, `delinq_max_6m` +⟦unverified: 0.0135⟧). The concentration of explanatory weight in one recent-delinquency flag is a concentration risk in its own right: the score will be unstable if the upstream delinquency feed changes definition, lags, or cure treatment.

**Scenario implications of the wrong-signed terms.** Because `bill_mean_6m` and `bill_trend_6m` carry negative loadings totalling −⟦unverified: 0.4943⟧, a stress scenario in which balances rise across the book — the ordinary form of a consumer-credit downturn — would *reduce* predicted default probability through those two channels, partially offsetting the increase coming through `utilisation`. Net directionality under a balance-growth stress depends on the correlation structure between the three terms and is not determinable from the artifacts. The model's response to the most obvious adverse scenario is therefore ambiguous at best and perverse at worst. This is recorded as a finding.

**Regime and segment stability.** No by-regime, by-vintage, or by-segment metrics were produced. With a random rather than out-of-time split, no statement about temporal stability of either the coefficients or the AUC is supportable, and the R1 test could not be run.

**Effective challenge.** No challenger model was submitted. The validator nevertheless observes that the simplest possible benchmark — the base-rate constant predictor — outperforms the champion on both Brier and log loss, as shown in section 4. That is a failure of effective challenge on the evidence already in the store, and is recorded as such.

**Execution.** [[art:2922931d:run.status]], [[art:41728c38:run.stderr]] and [[art:ad0e4ee8:run.stdout]] disclose no failure, and [[art:e273f4fd:run.duration_s]] discloses no breach of [[art:2ad8d1a5:runtime.max_seconds]]. No R0 finding is raised.

## 6. Findings and recommendations

| # | Class | Severity | Title |
|---|---|---|---|
| ⟦unverified: 1⟧ | C1 | High | Systematic over-prediction: mean predicted ⟦unverified: 0.438⟧ vs observed ⟦unverified: 0.225⟧ |
| ⟦unverified: 2⟧ | E1 | Medium | Base-rate constant predictor beats the champion on Brier and log loss |
| ⟦unverified: 3⟧ | T1 | Medium | Declared `class_weight: null` inconsistent with the fitted intercept |
| ⟦unverified: 4⟧ | M1 | Medium | Residual collinearity: three counterintuitive coefficient signs after VIF screening |
| ⟦unverified: 5⟧ | X1 | Medium | Negative billing coefficients invert the response to a balance-growth stress |
| ⟦unverified: 6⟧ | S1 | Low | No PSI or drift measurement of any kind; split is not out-of-time |
| ⟦unverified: 7⟧ | R1 | Low | No regime, vintage, or segment stability analysis |
| ⟦unverified: 8⟧ | D1 | Low | No test-split profile; undocumented cap on `pay_ratio_last` |
| ⟦unverified: 9⟧ | L2 | Low | Split disjointness asserted by row hash only; no overlap statistic |

**Required before production use.**

1. Recalibrate. Refit on the unweighted population or apply a prior-correction offset of about −⟦unverified: 0.99⟧ to the linear predictor, then evidence the result with a decile-level observed-vs-expected table, a calibration slope and intercept with confidence bounds, and a Brier score that beats ⟦unverified: 0.1742⟧ on the test split.
2. Reconcile the training configuration with the declaration in [[art:3986de2e:run.model_summary]]. If resampling or weighting was applied, document it; if it was not, explain the intercept.
3. Resolve the sign anomalies on `bill_mean_6m`, `bill_trend_6m` and `limit_bal` — report post-removal VIFs and the design matrix condition number, and either drop the redundant billing terms or replace the three overlapping constructs with a single orthogonalised balance factor. Confirm that discrimination is not materially harmed.
4. Produce at least one genuine challenger (a penalised logistic fit and a gradient-boosted benchmark are the conventional pair) and report AUC, Brier and log loss for all three against the base-rate floor.
5. Publish the train/test overlap count on `client_id` and the test-split data profile, so that the L2 and D1 tests can be closed on evidence rather than inference.
6. Re-split out-of-time and re-report. Until a forward-period test exists, the model has no demonstrated temporal validity.

**Documentation gaps to close.** The cap on `pay_ratio_last` at ⟦unverified: 2.0⟧; the treatment producing zero missingness; the retention of over-limit `utilisation` values above 1.0; the exclusion path for `client_id`; and the absence of any outlier treatment on `bill_mean_6m` and `bill_trend_6m`.

### F-001 · C1 calibration · severity **high**

Mean predicted probability on the test split is 0.43790 against an observed event rate of 0.22467, a ratio of 1.95:1; the same bias is present in train (0.44275 vs 0.22457). In log-odds terms the score sits approximately 0.99 too high (logit 0.2247 = -1.2385; logit 0.4379 = -0.2497). On the 1,500-row test book the model expects roughly 657 defaults where 337 occurred. The error is severe enough to dominate the model's genuine discrimination: the test Brier score of 0.19288 and log loss of 0.59350 are both worse than those of a constant predictor set at the base rate (0.17420 and 0.53281), by 10.7% and 11.4% respectively. Any downstream use that multiplies the score by an exposure -- expected loss, provisioning, risk-based pricing, limit assignment -- would roughly double the loss estimate. The root cause is visible in the model summary: with standardised features the linear predictor has mean equal to the intercept, and the fitted intercept of +0.06740 implies a central predicted probability near 0.517 on a population with prevalence 0.2246, which is the signature of an estimation sample balanced to 50/50. Remediation is inexpensive -- refit on the unweighted population or apply a prior-correction offset of about -0.99 -- but until it is done and evidenced with a decile-level observed-versus-expected table and a calibration slope, the model must not be used for any probability-based decision.

### F-002 · E1 effective challenge · severity **medium**

No challenger model was submitted for this validation, which is itself a gap in effective challenge. More seriously, the evidence already in the store shows the champion losing to the most trivial benchmark available. A constant predictor assigning every account the test-split base rate of 0.22467 achieves a Brier score of p(1-p) = 0.17420 and a log loss of 0.53281. The subject model records 0.19288 and 0.59350 -- worse on both. The model's AUC of 0.7764 confirms it carries real rank-ordering information, so this is not a discrimination failure but the arithmetic consequence of the calibration defect; nonetheless, a champion that cannot beat the portfolio average on probabilistic accuracy has not passed effective challenge. The developer should produce at least a penalised logistic fit and a gradient-boosted benchmark, and report AUC, Brier and log loss for all candidates against the base-rate floor, after the recalibration in finding 1 is complete.

### F-003 · T1 declared threshold · severity **medium**

The model summary declares class_weight: null and standardised: true. Those two declarations together are testable: when every feature is centred at zero, the mean of the linear predictor equals the intercept, so an unweighted fit on a population with a 22.46% event rate should produce an intercept near logit(0.2246) = -1.239. The reported intercept is +0.06740, corresponding to a central probability near 0.517 -- almost exactly what a sample balanced to 50/50 would yield, and consistent with the observed mean predicted probabilities of 0.4428 (train) and 0.4379 (test). Either class balancing, resampling, or weighting was applied and not declared, or the intercept was not fitted against the population prevalence. This is a breach of a developer declaration in its own right, and it is the mechanism behind the calibration finding. The developer must reconcile the training configuration with the summary artifact: if resampling or weighting was applied it must be documented along with the base-rate correction applied at scoring time; if it was not, the intercept requires explanation.

### F-004 · M1 collinearity · severity **medium**

The VIF screen was run against a declared threshold of 10.0 and removed bill_last (VIF 160.89) and utilisation_mean_6m (VIF 36.36), so the declared threshold was honoured. The presence of a VIF of 161 in the candidate set nonetheless establishes that the billing and utilisation block was severely collinear, and the retained specification still contains three overlapping balance constructs (utilisation, bill_mean_6m, bill_trend_6m) and three overlapping delinquency constructs (delinq_last, delinq_count_6m, delinq_max_6m). No post-removal VIF values and no design-matrix condition number were reported, so the validator cannot confirm the retained model is well conditioned. The empirical symptom is visible in the coefficients: bill_mean_6m at -0.27627 and bill_trend_6m at -0.21804 both imply that larger and rising balances reduce default odds, and limit_bal at +0.01627 implies that a higher underwritten limit raises them. All three contradict credit intuition and are consistent with utilisation absorbing the risk signal while the correlated billing terms take offsetting negative loadings. The coefficients therefore cannot be used for reason-code generation or adverse-action explanation, and their stability across refits is doubtful. The developer should publish post-removal VIFs and the condition number, and either drop the redundant billing terms or replace the three balance constructs with a single orthogonalised factor, confirming that discrimination is not materially harmed.

### F-005 · X1 scenario analysis · severity **medium**

No scenario grid, stress result, partial-dependence output, or value curve exists in the artifact store, so the scenario test could not be executed as specified and this finding is derived from the fitted coefficients. Because bill_mean_6m carries -0.27627 and bill_trend_6m carries -0.21804, totalling -0.49430 on standardised inputs, a scenario in which balances rise across the book -- the ordinary form of a consumer credit downturn -- pushes predicted default probability down through those two channels, partially or wholly offsetting the increase arriving through utilisation at +0.47685. The response curve to the single most obvious adverse scenario is therefore of indeterminate and possibly wrong sign, and the net effect cannot be resolved from the artifacts because the correlation structure between the three terms is not reported. A closely related concentration issue compounds this: delinq_last at +1.02284 carries more than twice the weight of any other term, so the model's stress behaviour is effectively a single-variable response with a perverse balance offset. The developer should produce an explicit scenario grid over utilisation and balance growth, demonstrate monotonicity of predicted risk in each stress direction, and re-specify the balance block if monotonicity cannot be achieved.

### F-006 · S1 population drift · severity **low**

The artifact store contains no population stability index, no score PSI, and no characteristic-level drift measure. The only cross-split comparison available is target prevalence, which is 0.22457 in train against 0.22467 in test -- stable, but silent as to covariate or score distribution. The split also appears to be random rather than temporal: the two partitions of 3,500 and 1,500 rows exactly exhaust the 1-5,000 client identifier range, the event rates are near-identical to four decimal places, and no vintage or period field appears in the feature inventory. Consequently the stability test could not be performed, and even if it had been, a random split cannot evidence temporal stability. The model has never been tested on a forward period. The developer should construct an out-of-time holdout, report score and characteristic PSI against the development distribution, and re-report discrimination and calibration on that window before production use.

### F-007 · R1 regime stability · severity **low**

The validation standard requires evidence that top-feature signs and discrimination hold across regimes. No by-regime, by-vintage, or by-segment metrics exist in the store: the metric block reports only pooled train and test figures, and no time or segment identifier appears in the feature inventory. The stability of the dominant coefficient -- delinq_last at +1.02284, which carries the majority of the model's signal -- is therefore entirely untested, as is the stability of the three counterintuitive signs identified separately. This is recorded as a coverage gap rather than a demonstrated instability; the validator makes no claim that a flip or an AUC divergence exists, only that neither has been ruled out. The developer should segment at minimum by vintage and by limit band, and report per-segment AUC together with refitted coefficient signs for the top five features.

### F-008 · D1 data integrity · severity **low**

A data profile was supplied for the training split only. It reports 3,500 rows with zero missing values across all thirteen columns -- 45,500 cells with no gaps, which is unusual for retail credit data and suggests either a pre-cleaned extract or an undocumented imputation step upstream of profiling. Because no corresponding profile of the test table was provided, the required split-to-split missingness comparison could not be performed and the data integrity test is open rather than passed. Three further integrity items in the training profile are undocumented: pay_ratio_last has a maximum of exactly 2.0000 against a minimum of 0.00077, the fingerprint of a cap rather than a natural bound (pay_ratio_mean_6m reaches only 1.6385, consistent with the cap binding on the single-month series); utilisation extends to 1.1297, so over-limit accounts are retained, which is defensible but unstated; and bill_mean_6m (429 to 506,281) and bill_trend_6m (-67,201 to +27,398) receive no winsorisation despite extreme tails that standardisation rescales but does not tame. The developer should publish the test-split profile, document the cap and the missingness treatment, and state the outlier policy for the balance fields.

### F-009 · L2 contamination · severity **low**

The split manifest records distinct row hashes for the two partitions (train e028347d..., test 3e28943d...) and the sizes reconcile with n_train in the model summary. Distinct hashes establish only that the two row sets are not identical; they do not establish that no individual client appears in both, and no overlap count on client_id was computed. Two observations keep this open rather than closed. First, client_id spans 1 to 5,000 across a universe of 5,000 rows and the splits sum to exactly 5,000, which is consistent with a disjoint partition but also with any other allocation. Second, the train-to-test AUC gap is -0.0001 and both Brier and log loss are better on test than on train -- a degree of agreement at the outer edge of what a random split ordinarily produces, though not in itself abnormal for a ten-parameter logistic model on 3,500 rows. The validator raises no claim of contamination; the defect is that the check was never run. The developer should publish the count of client_id values common to both partitions.

Candidates raised and not promoted: none.

### Open items

No open item was recorded for this validation.

## 7. Ongoing monitoring recommendations

Once the calibration defect is remediated, the following monitoring plan should be instituted and owned by the model owner, with results reported to the model risk committee.

**Monthly.** Score PSI against the development distribution, with a ⟦unverified: 0.10⟧ investigate / ⟦unverified: 0.25⟧ escalate convention. Characteristic-level PSI for the ten retained features, with particular attention to `delinq_last` given that it carries the majority of the model's signal. Population volumes, override rates, and the distribution of scores across the decision bands.

**Quarterly.** Observed-versus-expected default rates overall and by score decile, with a binomial test at each decile; calibration slope and intercept, with an action trigger if the slope falls outside [⟦unverified: 0.8⟧, ⟦unverified: 1.2⟧] or the intercept drifts by more than ⟦unverified: 0.25⟧ in log-odds. Discrimination on the newest complete performance window — AUC, Gini, KS — with escalation if AUC falls more than ⟦unverified: 0.05⟧ below the validated ⟦unverified: 0.7764⟧. Brier score benchmarked against the contemporaneous base-rate floor, since that comparison is precisely what the current version fails.

**Annually.** Full coefficient refresh and sign review, including re-run of the VIF screen and condition number. Re-execution of the challenger suite; escalate to redevelopment if a challenger exceeds the champion AUC by more than ⟦unverified: 0.02⟧. Review of feature timing declarations in [[art:abbb748e:run.features]] against the current source systems, to confirm that no field has silently moved into the performance window. Confirmation that the upstream definition of delinquency, cure, and the `pay_ratio` cap remain unchanged.

**Event-driven.** Any change to the delinquency data feed, any change to limit-setting policy (which would shift `limit_bal` and `utilisation` jointly), and any macroeconomic deterioration that materially moves the balance distribution should trigger an off-cycle calibration review, given the model's ambiguous response to balance growth documented in section 5.

## Appendix A — Claims

Grounding precision 0.0068 before repair (1 of 146 claims verified; 109 unsupported, 18 dangling, 18 unattributed) and 0.0068 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 0/11; conceptual_soundness 1/21; data_integrity 0/20; outcomes 0/57; sensitivity 0/15; findings 0/14; monitoring 0/8.

Developer claims: `plain_llm` runs no check over `package.yaml`'s declared claims See Appendix D.

Excluded numeric tokens (not claims): section_number (section 4, section 3, section 2, 1.); inline_code (`3e28943d…`); citation_hash (3986de2e, 3b6b0a38, d89e6798, abbb748e); package_version (1.0); extractor_returned_excluded_token (1.0, 4, 3, -1.2385).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | This report documents an independent validation of package `… | 3500 | count | n_train | train | eq | `[[art:3986de2e:run.model_summary]]` | dangling |  |
| 2 | summary | This report documents an independent validation of package `… | 1500 | count | n_test | test | eq | `[[art:3b6b0a38:run.splits]]` | dangling |  |
| 3 | summary | **Overall opinion.** The model discriminates acceptably but… | 0.7764 | ratio | auc | test | eq |  | unsupported |  |
| 4 | summary | **Overall opinion.** The model discriminates acceptably but… | 0.4656 | ratio | ks | test | eq |  | unsupported |  |
| 5 | summary | **Overall opinion.** The model discriminates acceptably but… | 0.4379 | ratio | mean_predicted_probability | test | eq |  | unsupported |  |
| 6 | summary | **Overall opinion.** The model discriminates acceptably but… | 0.2247 | ratio | event_rate | test | eq |  | unsupported |  |
| 7 | summary | **Overall opinion.** The model discriminates acceptably but… | 1.95 | ratio |  | test | ratio |  | unsupported |  |
| 8 | summary | **Overall opinion.** The model discriminates acceptably but… | 0.1929 | ratio | brier | test | eq |  | unsupported |  |
| 9 | summary | **Overall opinion.** The model discriminates acceptably but… | 0.5935 | ratio | log_loss | test | eq |  | unsupported |  |
| 10 | summary | **Overall opinion.** The model discriminates acceptably but… | 0.1742 | ratio | brier | test | eq |  | unsupported |  |
| 11 | summary | **Overall opinion.** The model discriminates acceptably but… | 0.5328 | ratio | log_loss | test | eq |  | unsupported |  |
| 12 | conceptual_soundness | **Feature timing.** The inventory in declares 12 candidate f… | 12 | count | features |  | eq | `[[art:abbb748e:run.features]]` | dangling |  |
| 13 | conceptual_soundness | **Feature timing.** The inventory in declares 12 candidate f… | 2 | count |  |  | eq |  | unsupported |  |
| 14 | conceptual_soundness | **Feature timing.** The inventory in declares 12 candidate f… | 10 | count |  |  | eq |  | unsupported |  |
| 15 | conceptual_soundness | **Variable selection.** Two features were dropped for multic… | 10 | ratio | vif |  | eq | `[[art:3986de2e:run.model_summary#removed]]` | dangling |  |
| 16 | conceptual_soundness | **Variable selection.** Two features were dropped for multic… | 160.9 | ratio | vif |  | eq | `[[art:3986de2e:run.model_summary#removed]]` | dangling |  |
| 17 | conceptual_soundness | **Variable selection.** Two features were dropped for multic… | 36.4 | ratio | vif |  | eq | `[[art:3986de2e:run.model_summary#removed]]` | dangling |  |
| 18 | conceptual_soundness | **Coefficient signs.** With standardised inputs, the fitted… | 1.0228 | ratio | coefficient |  | eq | `[[art:3986de2e:run.model_summary#coefficients]]` | dangling |  |
| 19 | conceptual_soundness | **Coefficient signs.** With standardised inputs, the fitted… | 0.1404 | ratio | coefficient |  | eq | `[[art:3986de2e:run.model_summary#coefficients]]` | dangling |  |
| 20 | conceptual_soundness | **Coefficient signs.** With standardised inputs, the fitted… | 0.0135 | ratio | coefficient |  | eq | `[[art:3986de2e:run.model_summary#coefficients]]` | dangling |  |
| 21 | conceptual_soundness | **Coefficient signs.** With standardised inputs, the fitted… | 0.4769 | ratio | coefficient |  | eq | `[[art:3986de2e:run.model_summary#coefficients]]` | dangling |  |
| 22 | conceptual_soundness | **Coefficient signs.** With standardised inputs, the fitted… | -0.0763 | ratio | coefficient |  | eq | `[[art:3986de2e:run.model_summary#coefficients]]` | dangling |  |
| 23 | conceptual_soundness | **Coefficient signs.** With standardised inputs, the fitted… | -0.0918 | ratio | coefficient |  | eq | `[[art:3986de2e:run.model_summary#coefficients]]` | dangling |  |
| 24 | conceptual_soundness | **Coefficient signs.** With standardised inputs, the fitted… | -0.1725 | ratio | coefficient |  | eq | `[[art:3986de2e:run.model_summary#coefficients]]` | dangling |  |
| 25 | conceptual_soundness | \| `bill_mean_6m` \| -0.2763 \| positive \| Larger average balan… | -0.2763 | ratio | coefficient |  | eq |  | unsupported |  |
| 26 | conceptual_soundness | \| `bill_trend_6m` \| -0.2180 \| positive \| Rising balances ass… | -0.218 | ratio | coefficient |  | eq |  | unsupported |  |
| 27 | conceptual_soundness | \| `limit_bal` \| +0.0163 \| negative \| Higher granted limit (a… | 0.0163 | ratio | coefficient |  | eq |  | unsupported |  |
| 28 | conceptual_soundness | **Intercept.** The fitted intercept is +0.0674 (). Because t… | 0.0674 | ratio | intercept |  | eq | `[[art:3986de2e:run.model_summary#intercept]]` | verified | 0.06740330428 |
| 29 | conceptual_soundness | **Intercept.** The fitted intercept is +0.0674 (). Because t… | 0.517 | ratio |  |  | eq |  | unsupported |  |
| 30 | conceptual_soundness | **Intercept.** The fitted intercept is +0.0674 (). Because t… | 0.2246 | ratio | event_rate |  | eq |  | unsupported |  |
| 31 | conceptual_soundness | **Intercept.** The fitted intercept is +0.0674 (). Because t… | 50 | ratio |  |  | eq |  | unsupported |  |
| 32 | conceptual_soundness | **Intercept.** The fitted intercept is +0.0674 (). Because t… | 50 | ratio |  |  | eq |  | unsupported |  |
| 33 | data_integrity | The training profile of reports 3,500 rows with zero missing… | 3500 | count |  | train | eq | `[[art:6a89f2be:run.data_train]]` | dangling |  |
| 34 | data_integrity | The training profile of reports 3,500 rows with zero missing… | 45500 | count |  | train | eq |  | unsupported |  |
| 35 | data_integrity | Several distributional features deserve comment. `pay_ratio_… | 2 | ratio |  | train | eq |  | unsupported |  |
| 36 | data_integrity | Several distributional features deserve comment. `pay_ratio_… | 0.00077 | ratio |  | train | eq |  | unsupported |  |
| 37 | data_integrity | Several distributional features deserve comment. `pay_ratio_… | 1.6385 | ratio |  | train | eq |  | unsupported |  |
| 38 | data_integrity | Several distributional features deserve comment. `pay_ratio_… | 1.1297 | ratio |  | train | eq |  | unsupported |  |
| 39 | data_integrity | Several distributional features deserve comment. `pay_ratio_… | -237.6 | currency |  | train | eq |  | unsupported |  |
| 40 | data_integrity | Several distributional features deserve comment. `pay_ratio_… | -67201 | currency |  | train | eq |  | unsupported |  |
| 41 | data_integrity | Several distributional features deserve comment. `pay_ratio_… | 27398 | currency |  | train | eq |  | unsupported |  |
| 42 | data_integrity | Several distributional features deserve comment. `pay_ratio_… | 429 | currency |  | train | eq |  | unsupported |  |
| 43 | data_integrity | Several distributional features deserve comment. `pay_ratio_… | 506281 | currency |  | train | eq |  | unsupported |  |
| 44 | data_integrity | Several distributional features deserve comment. `pay_ratio_… | 1 | count |  |  | eq |  | unsupported |  |
| 45 | data_integrity | Several distributional features deserve comment. `pay_ratio_… | 5000 | count |  |  | eq |  | unsupported |  |
| 46 | data_integrity | Several distributional features deserve comment. `pay_ratio_… | 5000 | count |  |  | eq |  | unsupported |  |
| 47 | data_integrity | **Split integrity.** records distinct row hashes for the two… | 3500 | count |  | train | eq | `[[art:6a89f2be:run.data_train]]` | dangling |  |
| 48 | data_integrity | **Split integrity.** records distinct row hashes for the two… | 1500 | count |  | test | eq | `[[art:26fbbf1d:run.data_test]]` | dangling |  |
| 49 | data_integrity | **Split integrity.** records distinct row hashes for the two… | 1 | count |  |  | eq |  | unsupported |  |
| 50 | data_integrity | **Split integrity.** records distinct row hashes for the two… | 5000 | count |  |  | eq |  | unsupported |  |
| 51 | data_integrity | **Drift.** No population stability index, score PSI, or char… | 0.2246 | ratio | event_rate | train | eq | `[[art:3b6b0a38:run.splits]]` | dangling |  |
| 52 | data_integrity | **Drift.** No population stability index, score PSI, or char… | 0.2247 | ratio | event_rate | test | eq | `[[art:3b6b0a38:run.splits]]` | dangling |  |
| 53 | outcomes | \| Metric \| Train (n=3,500) \| Test (n=1,500) \| Gap \| | 3500 | count |  | train | eq |  | unsupported |  |
| 54 | outcomes | \| Metric \| Train (n=3,500) \| Test (n=1,500) \| Gap \| | 1500 | count |  | test | eq |  | unsupported |  |
| 55 | outcomes | \| AUC \| 0.7765 \| 0.7764 \| -0.0001 \| | 0.7765 | ratio | auc | train | eq |  | unsupported |  |
| 56 | outcomes | \| AUC \| 0.7765 \| 0.7764 \| -0.0001 \| | 0.7764 | ratio | auc | test | eq |  | unsupported |  |
| 57 | outcomes | \| AUC \| 0.7765 \| 0.7764 \| -0.0001 \| | -0.0001 | ratio | delta_auc |  | delta |  | unsupported |  |
| 58 | outcomes | \| Gini \| 0.5530 \| 0.5527 \| -0.0003 \| | 0.553 | ratio | gini | train | eq |  | unsupported |  |
| 59 | outcomes | \| Gini \| 0.5530 \| 0.5527 \| -0.0003 \| | 0.5527 | ratio | gini | test | eq |  | unsupported |  |
| 60 | outcomes | \| Gini \| 0.5530 \| 0.5527 \| -0.0003 \| | -0.0003 | ratio | gini |  | delta |  | unsupported |  |
| 61 | outcomes | \| KS \| 0.4801 \| 0.4656 \| -0.0145 \| | 0.4801 | ratio | ks | train | eq |  | unsupported |  |
| 62 | outcomes | \| KS \| 0.4801 \| 0.4656 \| -0.0145 \| | 0.4656 | ratio | ks | test | eq |  | unsupported |  |
| 63 | outcomes | \| KS \| 0.4801 \| 0.4656 \| -0.0145 \| | -0.0145 | ratio | ks |  | delta |  | unsupported |  |
| 64 | outcomes | \| Brier \| 0.1969 \| 0.1929 \| -0.0040 \| | 0.1969 | ratio | brier | train | eq |  | unsupported |  |
| 65 | outcomes | \| Brier \| 0.1969 \| 0.1929 \| -0.0040 \| | 0.1929 | ratio | brier | test | eq |  | unsupported |  |
| 66 | outcomes | \| Brier \| 0.1969 \| 0.1929 \| -0.0040 \| | -0.004 | ratio | brier |  | delta |  | unsupported |  |
| 67 | outcomes | \| Log loss \| 0.6031 \| 0.5935 \| -0.0096 \| | 0.6031 | ratio | log_loss | train | eq |  | unsupported |  |
| 68 | outcomes | \| Log loss \| 0.6031 \| 0.5935 \| -0.0096 \| | 0.5935 | ratio | log_loss | test | eq |  | unsupported |  |
| 69 | outcomes | \| Log loss \| 0.6031 \| 0.5935 \| -0.0096 \| | -0.0096 | ratio | log_loss |  | delta |  | unsupported |  |
| 70 | outcomes | \| Event rate \| 0.2246 \| 0.2247 \| +0.0001 \| | 0.2246 | ratio | event_rate | train | eq |  | unsupported |  |
| 71 | outcomes | \| Event rate \| 0.2246 \| 0.2247 \| +0.0001 \| | 0.2247 | ratio | event_rate | test | eq |  | unsupported |  |
| 72 | outcomes | \| Event rate \| 0.2246 \| 0.2247 \| +0.0001 \| | 0.0001 | ratio | event_rate |  | delta |  | unsupported |  |
| 73 | outcomes | \| Mean predicted \| 0.4427 \| 0.4379 \| -0.0048 \| | 0.4427 | ratio | mean_predicted | train | eq |  | unsupported |  |
| 74 | outcomes | \| Mean predicted \| 0.4427 \| 0.4379 \| -0.0048 \| | 0.4379 | ratio | mean_predicted | test | eq |  | unsupported |  |
| 75 | outcomes | \| Mean predicted \| 0.4427 \| 0.4379 \| -0.0048 \| | -0.0048 | ratio | mean_predicted |  | delta |  | unsupported |  |
| 76 | outcomes | **Discrimination.** Test AUC of 0.7764 (Gini 0.5527, KS 0.46… | 0.7764 | ratio | auc | test | eq |  | unsupported |  |
| 77 | outcomes | **Discrimination.** Test AUC of 0.7764 (Gini 0.5527, KS 0.46… | 0.5527 | ratio | gini | test | eq |  | unsupported |  |
| 78 | outcomes | **Discrimination.** Test AUC of 0.7764 (Gini 0.5527, KS 0.46… | 0.4656 | ratio | ks | test | eq |  | unsupported |  |
| 79 | outcomes | **Discrimination.** Test AUC of 0.7764 (Gini 0.5527, KS 0.46… | 2 | ratio |  |  | eq |  | unsupported |  |
| 80 | outcomes | **Discrimination.** Test AUC of 0.7764 (Gini 0.5527, KS 0.46… | 1 | ratio |  |  | eq |  | unsupported |  |
| 81 | outcomes | **Out-of-sample stability.** The train-to-test AUC gap is 0.… | 0.0001 | ratio | delta_auc |  | delta |  | unsupported |  |
| 82 | outcomes | **Out-of-sample stability.** The train-to-test AUC gap is 0.… | 3500 | count |  | train | eq |  | unsupported |  |
| 83 | outcomes | **Calibration.** This is where the model fails. Mean predict… | 0.4379 | ratio | mean_predicted | test | eq |  | unsupported |  |
| 84 | outcomes | **Calibration.** This is where the model fails. Mean predict… | 0.2247 | ratio | event_rate | test | eq |  | unsupported |  |
| 85 | outcomes | **Calibration.** This is where the model fails. Mean predict… | 1.95 | ratio |  | test | ratio |  | unsupported |  |
| 86 | outcomes | **Calibration.** This is where the model fails. Mean predict… | 1 | ratio |  |  | eq |  | unsupported |  |
| 87 | outcomes | **Calibration.** This is where the model fails. Mean predict… | 0.4427 | ratio | mean_predicted | train | eq |  | unsupported |  |
| 88 | outcomes | **Calibration.** This is where the model fails. Mean predict… | 0.2246 | ratio | event_rate | train | eq |  | unsupported |  |
| 89 | outcomes | **Calibration.** This is where the model fails. Mean predict… | 0.99 | ratio |  |  | eq |  | unsupported |  |
| 90 | outcomes | **Calibration.** This is where the model fails. Mean predict… | 0.2247 | ratio | event_rate | test | eq |  | unsupported |  |
| 91 | outcomes | **Calibration.** This is where the model fails. Mean predict… | 1.2385 | ratio |  |  | eq |  | unattributed |  |
| 92 | outcomes | **Calibration.** This is where the model fails. Mean predict… | 0.4379 | ratio | mean_predicted | test | eq |  | unsupported |  |
| 93 | outcomes | **Calibration.** This is where the model fails. Mean predict… | 0.2497 | ratio |  |  | eq |  | unattributed |  |
| 94 | outcomes | **Calibration.** This is where the model fails. Mean predict… | 1500 | count |  | test | eq |  | unsupported |  |
| 95 | outcomes | **Calibration.** This is where the model fails. Mean predict… | 657 | count |  | test | eq |  | unsupported |  |
| 96 | outcomes | **Calibration.** This is where the model fails. Mean predict… | 337 | count |  | test | eq |  | unsupported |  |
| 97 | outcomes | The consequences are quantitative, not cosmetic. A constant… | 0.2247 | ratio | event_rate | test | eq |  | unsupported |  |
| 98 | outcomes | The consequences are quantitative, not cosmetic. A constant… | 1 | ratio |  |  | eq |  | unsupported |  |
| 99 | outcomes | The consequences are quantitative, not cosmetic. A constant… | 0.1742 | ratio | brier | test | eq |  | unsupported |  |
| 100 | outcomes | The consequences are quantitative, not cosmetic. A constant… | 0.5328 | ratio | log_loss | test | eq |  | unsupported |  |
| 101 | outcomes | The consequences are quantitative, not cosmetic. A constant… | 0.1929 | ratio | brier | test | eq |  | unsupported |  |
| 102 | outcomes | The consequences are quantitative, not cosmetic. A constant… | 0.5935 | ratio | log_loss | test | eq |  | unsupported |  |
| 103 | outcomes | The consequences are quantitative, not cosmetic. A constant… | 10.7 | percent | brier | test | eq |  | unsupported |  |
| 104 | outcomes | The consequences are quantitative, not cosmetic. A constant… | 11.4 | percent | log_loss | test | eq |  | unsupported |  |
| 105 | outcomes | The consequences are quantitative, not cosmetic. A constant… | 9 | ratio |  |  | eq |  | unsupported |  |
| 106 | outcomes | As set out in section 2, the arithmetic points to a specific… | 0.5 | ratio |  |  | eq |  | unsupported |  |
| 107 | outcomes | As set out in section 2, the arithmetic points to a specific… | 50 | ratio |  |  | eq |  | unsupported |  |
| 108 | outcomes | As set out in section 2, the arithmetic points to a specific… | 50 | ratio |  |  | eq |  | unsupported |  |
| 109 | outcomes | As set out in section 2, the arithmetic points to a specific… | 0.99 | ratio |  |  | eq |  | unattributed |  |
| 110 | sensitivity | **Univariate sensitivity.** Because the inputs are standardi… | 1.32 | count |  |  | eq |  | unsupported |  |
| 111 | sensitivity | **Univariate sensitivity.** Because the inputs are standardi… | 1.0228 | ratio | coefficient |  | eq |  | unsupported |  |
| 112 | sensitivity | **Univariate sensitivity.** Because the inputs are standardi… | 2.78 | ratio |  |  | eq |  | unsupported |  |
| 113 | sensitivity | **Univariate sensitivity.** Because the inputs are standardi… | 0.4769 | ratio | coefficient |  | eq |  | unsupported |  |
| 114 | sensitivity | **Univariate sensitivity.** Because the inputs are standardi… | 0.234 | ratio |  |  | eq |  | unsupported |  |
| 115 | sensitivity | **Univariate sensitivity.** Because the inputs are standardi… | 1.61 | ratio |  |  | eq |  | unsupported |  |
| 116 | sensitivity | **Univariate sensitivity.** Because the inputs are standardi… | 0.2763 | ratio |  |  | eq |  | unattributed |  |
| 117 | sensitivity | **Univariate sensitivity.** Because the inputs are standardi… | 0.218 | ratio |  |  | eq |  | unattributed |  |
| 118 | sensitivity | **Univariate sensitivity.** Because the inputs are standardi… | 0.1725 | ratio |  |  | eq |  | unattributed |  |
| 119 | sensitivity | **Univariate sensitivity.** Because the inputs are standardi… | 0.1404 | ratio | coefficient |  | eq |  | unsupported |  |
| 120 | sensitivity | **Univariate sensitivity.** Because the inputs are standardi… | 0.0918 | ratio |  |  | eq |  | unattributed |  |
| 121 | sensitivity | **Univariate sensitivity.** Because the inputs are standardi… | 0.0763 | ratio |  |  | eq |  | unattributed |  |
| 122 | sensitivity | **Univariate sensitivity.** Because the inputs are standardi… | 0.0163 | ratio | coefficient |  | eq |  | unsupported |  |
| 123 | sensitivity | **Univariate sensitivity.** Because the inputs are standardi… | 0.0135 | ratio | coefficient |  | eq |  | unsupported |  |
| 124 | sensitivity | **Scenario implications of the wrong-signed terms.** Because… | 0.4943 | ratio |  |  | eq |  | unattributed |  |
| 125 | findings | **Documentation gaps to close.** The cap on `pay_ratio_last`… | 1 | ratio |  |  | eq |  | unsupported |  |
| 126 | findings | \| 1 \| C1 \| High \| Systematic over-prediction: mean predicted… | 0.438 | ratio | mean_predicted |  | eq |  | unsupported |  |
| 127 | findings | \| 1 \| C1 \| High \| Systematic over-prediction: mean predicted… | 0.225 | ratio | event_rate |  | eq |  | unsupported |  |
| 128 | findings | \| 2 \| E1 \| Medium \| Base-rate constant predictor beats the c… | 2 | count |  |  | eq |  | unattributed |  |
| 129 | findings | \| 3 \| T1 \| Medium \| Declared `class_weight: null` inconsiste… | 3 | count |  |  | eq |  | unattributed |  |
| 130 | findings | \| 4 \| M1 \| Medium \| Residual collinearity: three counterintu… | 4 | count |  |  | eq |  | unattributed |  |
| 131 | findings | \| 5 \| X1 \| Medium \| Negative billing coefficients invert the… | 5 | count |  |  | eq |  | unattributed |  |
| 132 | findings | \| 6 \| S1 \| Low \| No PSI or drift measurement of any kind; sp… | 6 | count |  |  | eq |  | unattributed |  |
| 133 | findings | \| 7 \| R1 \| Low \| No regime, vintage, or segment stability an… | 7 | count |  |  | eq |  | unattributed |  |
| 134 | findings | \| 8 \| D1 \| Low \| No test-split profile; undocumented cap on… | 8 | count |  |  | eq |  | unattributed |  |
| 135 | findings | \| 9 \| L2 \| Low \| Split disjointness asserted by row hash onl… | 9 | count |  |  | eq |  | unattributed |  |
| 136 | findings | 1. Recalibrate. Refit on the unweighted population or apply… | 0.99 | ratio |  |  | eq |  | unattributed |  |
| 137 | findings | 1. Recalibrate. Refit on the unweighted population or apply… | 0.1742 | ratio | brier | test | eq |  | unsupported |  |
| 138 | findings | **Documentation gaps to close.** The cap on `pay_ratio_last`… | 2 | ratio |  |  | eq |  | unsupported |  |
| 139 | monitoring | **Monthly.** Score PSI against the development distribution,… | 0.1 | ratio | psi |  | eq |  | unsupported |  |
| 140 | monitoring | **Monthly.** Score PSI against the development distribution,… | 0.25 | ratio | psi |  | eq |  | unsupported |  |
| 141 | monitoring | **Quarterly.** Observed-versus-expected default rates overal… | 0.8 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 142 | monitoring | **Quarterly.** Observed-versus-expected default rates overal… | 1.2 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 143 | monitoring | **Quarterly.** Observed-versus-expected default rates overal… | 0.25 | ratio | calibration_intercept |  | eq |  | unsupported |  |
| 144 | monitoring | **Quarterly.** Observed-versus-expected default rates overal… | 0.05 | ratio | delta_auc |  | eq |  | unsupported |  |
| 145 | monitoring | **Quarterly.** Observed-versus-expected default rates overal… | 0.7764 | ratio | auc |  | eq |  | unsupported |  |
| 146 | monitoring | **Annually.** Full coefficient refresh and sign review, incl… | 0.02 | ratio | delta_auc |  | eq |  | unsupported |  |

## Appendix B — Artifact index

The store holds 14 artifacts; the 13 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `run.data_test` | `26fbbf1d` | table | table, 1500 rows | the subject's data_test.csv |
| `run.data_train` | `6a89f2be` | table | table, 3500 rows | the subject's data_train.csv |
| `run.duration_s` | `e273f4fd` | scalar | 1.665950583 | subject wall-clock seconds |
| `run.features` | `abbb748e` | json | json | the subject's features.json |
| `run.metrics` | `d89e6798` | json | json | the subject's metrics.json |
| `run.model_summary` | `3986de2e` | json | json | the subject's model_summary.json |
| `run.predictions_test` | `ef97fb76` | table | table, 1500 rows | the subject's predictions_test.csv |
| `run.predictions_train` | `c259f6c7` | table | table, 3500 rows | the subject's predictions_train.csv |
| `run.splits` | `3b6b0a38` | json | json | the subject's splits.json |
| `run.status` | `2922931d` | json | json | how the subject's subprocess ended |
| `run.stderr` | `41728c38` | json | json | the subject's stderr |
| `run.stdout` | `ad0e4ee8` | json | json | the subject's stdout |
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |

## Appendix C — Run trace summary

| quantity | value |
|---|---|
| tool calls | 1 (run_model 1) |
| plan steps (bounded loop) | 0 |
| LLM calls | 8 (plain_llm 1, extract 7) |
| re-asks | 0 |
| repair rounds | 0 |
| tokens in / out | 60,100 / 36,736 |
| notional cost (USD) | 1.5041 |
| wall-clock (s) | 437.72 |
| subject run (s) | 1.67 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | credit_default-plain_llm-20260918T081650Z-6e98ce62 |

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
