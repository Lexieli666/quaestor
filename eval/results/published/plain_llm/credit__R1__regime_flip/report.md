---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: plain_llm
model: claude-opus-5[1m]
run_id: credit_default-plain_llm-20260918T183409Z-6e98ce62
data_mode: synthetic
synthetic_n: 5000
grounding_precision_pre: 0.0000
grounding_precision_post: 0.0000
n_claims: 130
n_findings_by_severity: {high: 0, medium: 3, low: 6, info: 1}
generated: "2026-09-18T18:34:09Z"
illustrative: false
---

# Validation report — `credit_default` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `credit_default` v1.0 | `plain_llm` | claude-opus-5[1m] | synthetic, n = 5000 | 0.0000 → 0.0000 | 0 / 3 / 6 / 1 |
<!-- quaestor:renderer:end -->

This report documents an independent validation of package `credit_default`, version 1.0, a binary classification model that estimates the probability of `default_next_month` for revolving credit clients. The subject is a standardised logistic regression with ten retained predictors and an intercept of ⟦unverified: -1.3967⟧ [[art:15071cdb:run.model_summary]]. Development used ⟦unverified: 3,500⟧ rows and testing ⟦unverified: 1,500⟧ rows, drawn from a population of ⟦unverified: 5,000⟧ clients spanning application cohorts ⟦unverified: 2013⟧ through ⟦unverified: 2016⟧ [[art:1013df27:run.splits]].

The scope of this review is confined to the artifacts the developer produced and registered: the metrics file [[art:6ce7b4d6:run.metrics]], the model summary [[art:15071cdb:run.model_summary]], the feature inventory [[art:abbb748e:run.features]], the split manifest [[art:1013df27:run.splits]], the scored tables [[art:9936180e:run.predictions_test]] and [[art:fc881548:run.predictions_train]], the split tables [[art:929365b0:run.data_train]] and [[art:7ea4b8e1:run.data_test]], and the run telemetry [[art:2922931d:run.status]], [[art:63f5ebcf:run.duration_s]], [[art:2ad8d1a5:runtime.max_seconds]], [[art:07e84a56:run.stdout]] and [[art:41728c38:run.stderr]]. No independent re-estimation, no challenger build, and no re-scoring of the holdout were performed as part of this exercise; conclusions are therefore drawn from the developer's own evidence and from what that evidence does not contain.

Headline discriminatory performance is AUC ⟦unverified: 0.7690⟧ in-sample and ⟦unverified: 0.7337⟧ out-of-sample, with Gini of ⟦unverified: 0.5381⟧ and ⟦unverified: 0.4673⟧ and KS of ⟦unverified: 0.4426⟧ and ⟦unverified: 0.4096⟧ respectively [[art:6ce7b4d6:run.metrics]]. Aggregate calibration is close: mean predicted probability on test is ⟦unverified: 0.2292⟧ against an observed event rate of ⟦unverified: 0.2240⟧, and on train ⟦unverified: 0.2243⟧ against ⟦unverified: 0.2243⟧. On a Brier basis the model improves on the no-skill base-rate forecast (⟦unverified: 0.1738⟧) by roughly ⟦unverified: 14%⟧ in-sample and ⟦unverified: 12%⟧ out-of-sample. The model is, on its face, a competent and conventionally specified scorecard. The material concerns raised below are not about its headline numbers but about the validation evidence that has not been produced: there is no challenger, no scenario or sensitivity work, no drift measurement, no segment or regime cut, and no post-selection collinearity diagnostic.

Overall assessment: the model is **usable subject to remediation**. No finding rises to a level that would require withdrawal of the model, but the absence of effective challenge, scenario analysis, and drift monitoring evidence means the validation package as it stands is incomplete against normal model-risk expectations.

## 2. Conceptual soundness

The choice of a logistic regression for a binary default outcome is appropriate, transparent, and standard for this use. Inputs are standardised [[art:15071cdb:run.model_summary#standardised]], which makes the reported coefficients comparable in magnitude and supports the sign review below. The feature inventory declares twelve candidate features, of which two are `at_origination` and ten are `before_period_start`; none are declared `during_period` or `after_outcome` [[art:abbb748e:run.features]]. On the face of the declared timing there is no forward-looking information in the design, and the dominant coefficient — `delinq_last` at ⟦unverified: 0.7518⟧ — is economically the right variable to dominate a next-month default model.

The sign pattern is, however, only partly coherent. Four of the ten retained coefficients behave as credit intuition would predict: `utilisation` positive (⟦unverified: 0.2801⟧), `delinq_last` positive (⟦unverified: 0.7518⟧), `delinq_count_6m` positive (⟦unverified: 0.0638⟧), `delinq_max_6m` positive (⟦unverified: 0.0313⟧), with `age` mildly negative (⟦unverified: -0.0088⟧) and `pay_ratio_mean_6m` negative (⟦unverified: -0.2204⟧). Three do not. `limit_bal` carries a **positive** coefficient of ⟦unverified: 0.0794⟧, implying that a larger granted credit limit raises default odds once other factors are held constant; limits are normally granted as a function of assessed quality, and the univariate relationship in this population is almost certainly the other way. `bill_mean_6m` carries a **negative** coefficient of ⟦unverified: -0.2543⟧, implying that a larger average outstanding balance reduces default odds, which is the opposite of the exposure-risk relationship one expects and sits awkwardly beside the positive sign on `utilisation` — the two are numerator-related. `bill_trend_6m` is likewise negative at ⟦unverified: -0.2207⟧, i.e. a rising balance trajectory is scored as protective.

The most likely explanation is not that these relationships are real but that they are artefacts of residual correlation among the balance and payment blocks, which is discussed in section 6 under the multicollinearity finding. Sign instability of this kind is exactly the symptom that survives a VIF screen when the screen is applied once and not re-applied after removal. The developer has not provided any univariate or bivariate diagnostic, marginal-effect plot, or partial-dependence output that would let a reviewer distinguish a genuine conditional reversal from a collinearity artefact, and no such artifact exists in the store.

A second conceptual gap is the absence of any benchmark. There is no challenger model, no simple scorecard baseline, and not even a single-feature reference such as `delinq_last` alone, against which the ten-feature specification could be shown to earn its complexity. Effective challenge is a required element of model validation and its complete absence is recorded as a finding.

## 3. Data integrity and drift

The training profile reports ⟦unverified: 3,500⟧ rows with **zero missingness in every column**, including all twelve candidate features, the `client_id` key, the `application_cohort` vintage, and the `default_next_month` target. Uniformly zero missingness across thirteen fields in a retail credit dataset is unusual in production data and is more typical of a curated or synthetic extract; it is not in itself a defect, but it means the model carries no evidence at all about how it behaves when an input is absent, and no imputation or missing-indicator policy is documented.

A comparable profile for the test split has not been produced. The store contains the test table [[art:7ea4b8e1:run.data_test]] but no profile artifact for it, so the standard integrity check — that missingness rates do not differ materially between development and holdout — cannot be executed. This is recorded as a finding at low severity because the training side shows no missingness at all and the observed event rates are near-identical across splits (⟦unverified: 0.2243⟧ train versus ⟦unverified: 0.2240⟧ test, [[art:1013df27:run.splits]]), which is weak evidence that the two extracts were drawn the same way.

Distributional integrity of the inputs is mostly unremarkable: `limit_bal` ranges ⟦unverified: 10,000⟧ to ⟦unverified: 800,000⟧ with mean ⟦unverified: 106,204⟧; `age` ranges ⟦unverified: 21⟧ to ⟦unverified: 63⟧; `utilisation` ranges ⟦unverified: 0.0045⟧ to ⟦unverified: 1.1297⟧, where values above 1.0 are legitimate over-limit positions. Two fields deserve comment. `bill_trend_6m` has mean ⟦unverified: -246.3⟧ and standard deviation ⟦unverified: 3,095.6⟧ but a minimum of ⟦unverified: -67,201.4⟧ and a maximum of ⟦unverified: 27,398.0⟧ — roughly ⟦unverified: -21.7⟧ and +⟦unverified: 8.9⟧ standard deviations respectively. In a standardised logistic regression a handful of observations at twenty-odd sigma will dominate the standardisation constants and can materially move the fitted coefficient for that feature; no winsorisation, clipping, or transformation is documented. `bill_mean_6m` is similarly right-skewed, with a maximum of ⟦unverified: 443,112⟧ against a mean of ⟦unverified: 47,238⟧. Given that both of these features carry counterintuitive negative signs, the interaction between untreated outliers and coefficient estimation is a plausible contributing cause and should be tested.

On drift, the store contains **no population stability index, no score distribution comparison, and no cohort-by-cohort breakdown of any kind**. The data carry an `application_cohort` field spanning ⟦unverified: 2013⟧ to ⟦unverified: 2016⟧ with mean ⟦unverified: 2014.51⟧, so the vintage information required to measure drift is present in the source and simply was not used. Nothing in [[art:1013df27:run.splits]] indicates that the holdout was constructed out-of-time; the train split's `client_id` values span the full ⟦unverified: 1⟧ to ⟦unverified: 5,000⟧ range with a mean of ⟦unverified: 2,511⟧ against a ⟦unverified: 2,500.5⟧ expectation for a uniform random draw, which is the signature of a random row-level split across the pooled cohorts rather than a temporal one. A random split across vintages cannot detect drift by construction, because both sides of the comparison are mixtures of the same four years in the same proportions. The model's stability over time is therefore entirely unevidenced, and this is reported as a drift finding notwithstanding that no threshold breach can be demonstrated — the point is that no measurement exists.

On contamination, the split manifest records distinct `rows_hash` digests for the two splits (`16cd92c5…` for train, `0ab5339f…` for test). These are whole-split digests: they confirm the two splits are not the same set of rows, but they carry no information about row-level or client-level overlap between them. With ⟦unverified: 3,500⟧ plus ⟦unverified: 1,500⟧ rows summing exactly to the ⟦unverified: 5,000⟧ distinct `client_id` values implied by the training profile's range, a clean disjoint partition is the most probable reading. That reading has not been demonstrated, and no per-row or per-client overlap count artifact exists, so the contamination check is recorded as unexecuted rather than as passed.

## 4. Outcomes analysis

Discrimination is moderate and typical for a credit default scorecard of this construction. On the holdout the model achieves AUC ⟦unverified: 0.7337⟧, Gini ⟦unverified: 0.4673⟧, and KS ⟦unverified: 0.4096⟧ against ⟦unverified: 1,500⟧ observations and ⟦unverified: 336⟧ events at a ⟦unverified: 0.224⟧ event rate [[art:6ce7b4d6:run.metrics]]. In-sample figures are AUC ⟦unverified: 0.7690⟧, Gini ⟦unverified: 0.5381⟧, KS ⟦unverified: 0.4426⟧ on ⟦unverified: 3,500⟧ observations.

The train-to-test AUC gap is ⟦unverified: 0.0354⟧. In relative terms the Gini falls from ⟦unverified: 0.5381⟧ to ⟦unverified: 0.4673⟧, a ⟦unverified: 13.2%⟧ relative loss of ranking power, and KS falls by ⟦unverified: 0.0330⟧. A gap of this size is below the ⟦unverified: 0.05⟧ AUC threshold customarily applied for a material out-of-sample degradation finding, and for a ten-parameter model fitted on ⟦unverified: 3,500⟧ rows with ⟦unverified: 785⟧ events — roughly ⟦unverified: 79⟧ events per parameter — some optimism in the development figures is expected and benign. It is nonetheless recorded as a low-severity finding because the relative Gini loss is not trivial and because, with no cross-validation folds, no bootstrap confidence interval, and no repeated-split evidence in the store, the reviewer cannot distinguish ordinary in-sample optimism from a genuine overfit. A single train/test partition gives a point estimate with no dispersion around it.

Probability accuracy is good in aggregate. The Brier score is ⟦unverified: 0.1536⟧ on test against a base-rate reference of ⟦unverified: 0.2240⟧ × ⟦unverified: 0.7760⟧ = ⟦unverified: 0.1738⟧, a Brier skill score of ⟦unverified: 11.7%⟧; in-sample the corresponding figures are ⟦unverified: 0.1489⟧ and ⟦unverified: 14.4%⟧. Log loss is ⟦unverified: 0.4788⟧ on test and ⟦unverified: 0.4632⟧ on train. The direction and size of each train-to-test movement is consistent — the model loses a modest, uniform amount of both ranking and sharpness out of sample, with no sign of a discontinuity.

Aggregate calibration is close to unbiased. Mean predicted probability on test is ⟦unverified: 0.2292⟧ against an observed ⟦unverified: 0.2240⟧, an absolute over-prediction of ⟦unverified: 0.0052⟧ and a relative over-prediction of ⟦unverified: 2.3%⟧. In-sample the mean prediction equals the observed rate to four decimal places, which is the arithmetic consequence of fitting an intercept by maximum likelihood rather than independent evidence of calibration quality. The ⟦unverified: 2.3%⟧ out-of-sample over-prediction is conservative in direction and well inside any reasonable tolerance band.

What the outcomes evidence does **not** contain is any calibration diagnostic below the level of the grand mean. There is no calibration slope or intercept from a regression of outcome on log-odds, no decile or bucketed observed-versus-expected table, no Hosmer–Lemeshow or equivalent statistic, and no reliability curve. A model can match the population mean exactly while being badly miscalibrated within the tail that actually drives credit decisioning — over-predicting in the top decile and under-predicting in the bottom, with the two errors cancelling in the average. The scored tables [[art:9936180e:run.predictions_test]] and [[art:fc881548:run.predictions_train]] are present and contain everything needed to build these diagnostics; they were simply not built. A calibration finding is raised at low severity, reflecting that the aggregate evidence available is reassuring while the granular evidence is absent.

No segmentation of outcomes has been performed. Performance has not been reported by application cohort, by limit band, by age band, by utilisation band, or by delinquency status, so there is no evidence on whether the ⟦unverified: 0.7337⟧ holdout AUC is uniform across the book or is an average over segments that behave very differently. Given that `application_cohort` is carried in the data and spans four vintages, a by-vintage AUC table was directly available and is the single most useful missing exhibit in this package.

## 5. Sensitivity and scenario analysis

No sensitivity analysis and no scenario analysis have been performed. The artifact store contains no stress specification, no shocked input set, no re-scored output under any alternative assumption, and no value or response curve for any feature. This section therefore records an absence rather than a result.

The work that would normally appear here, and that the available data would support, includes at minimum: a univariate response curve for each retained feature, showing predicted probability as the feature is swept across its observed range with the remainder held at their means, checked for monotonicity and for sign agreement with credit intuition; a coefficient-stability exercise, refitting on bootstrap resamples or leave-one-cohort-out folds to establish whether the counterintuitive signs on `limit_bal`, `bill_mean_6m`, and `bill_trend_6m` are stable or are flipping across resamples; a shock test moving `utilisation` and the delinquency block adversely to represent a downturn, with the resulting shift in mean predicted probability and in the approval-rate-versus-default-rate trade-off reported; and an outlier-sensitivity test refitting with `bill_trend_6m` winsorised, given the ⟦unverified: -21.7⟧ sigma minimum noted in section 3.

The monotonicity check matters directly here and is not a formality. Because the specification is linear in the standardised features with no splines, interactions, or binning, each feature's response curve is monotone in the log-odds **by construction** — the shape cannot reveal a non-monotonicity even if one exists in the data. What the curve would reveal is direction, and on the evidence of the fitted coefficients three of the ten curves would slope the wrong way: the predicted default probability would **fall** as average billed balance rises and as the balance trajectory steepens, and would **rise** as the granted credit limit rises. Under a scenario in which a client's balances grow while the limit is held fixed, this model would report the client as becoming safer. That is a wrong-signed value curve, it is visible directly in [[art:15071cdb:run.model_summary#coefficients]], and it is recorded as a scenario finding on that basis even though no scenario artifact was produced. The linear form also means the model cannot represent the threshold behaviour that delinquency counts usually exhibit — the step from zero to one missed payment is not the same as the step from five to six — and no evidence has been offered that the linear approximation is adequate.

## 6. Findings and recommendations

Ten findings are recorded. None is rated high. Three are rated medium and carry required remediation before the next validation cycle; the remainder are documentation and evidence gaps.

**Medium.** *Residual multicollinearity and unverified sign stability.* The developer applied a VIF screen at a threshold of ⟦unverified: 10.0⟧ and removed `bill_last` (VIF ⟦unverified: 164.11⟧) and `utilisation_mean_6m` (VIF ⟦unverified: 38.98⟧) [[art:15071cdb:run.model_summary#removed]]. No post-removal VIF values, condition number, or correlation matrix has been reported for the ten retained features, so the claim implicit in the screen — that the final specification is free of harmful collinearity — is undemonstrated. The retained set still contains three obviously co-moving blocks: `pay_ratio_last` with `pay_ratio_mean_6m`, `delinq_last` with `delinq_count_6m` and `delinq_max_6m`, and `bill_mean_6m` with `bill_trend_6m` and with `utilisation`. Removing the two worst offenders from a correlated block typically leaves the survivors carrying unstable coefficients rather than curing the condition, and the three counterintuitive signs documented in section 2 are the expected symptom. *Recommendation:* recompute VIF and the design-matrix condition number on the final ten-feature matrix, publish the values, and if any exceed the declared threshold of ⟦unverified: 10.0⟧, either prune further, combine the correlated block into a single index, or move to a penalised fit. Report coefficient signs and magnitudes from bootstrap resamples alongside the point estimates.

**Medium.** *No effective challenge.* No challenger model of any kind exists in the store. The ten-feature specification has not been compared against a single-feature `delinq_last` baseline, a parsimonious three-to-four feature scorecard, or a non-linear alternative such as gradient boosting. Without a benchmark, neither the adequacy of AUC ⟦unverified: 0.7337⟧ nor the incremental value of the seven weakest features can be assessed, and the three counterintuitive coefficients cannot be shown to be earning their place. *Recommendation:* build and register at least two challengers — one deliberately simpler, one more flexible — and report holdout AUC, Gini, and Brier for each against the champion.

**Medium.** *No drift measurement and a non-temporal holdout.* No PSI, score-distribution comparison, or cohort breakdown exists, and the holdout appears to be a random partition across pooled ⟦unverified: 2013⟧–⟦unverified: 2016⟧ vintages rather than an out-of-time sample. Stability over time is unevidenced and, under the current split design, unmeasurable. *Recommendation:* recut the holdout out-of-time — fit on ⟦unverified: 2013⟧–⟦unverified: 2015,⟧ test on ⟦unverified: 2016⟧ — and publish feature-level and score-level PSI between the fitting window and each subsequent vintage against a stated threshold, conventionally ⟦unverified: 0.10⟧ for investigation and ⟦unverified: 0.25⟧ for action.

**Low.** *Wrong-signed response curves.* `limit_bal` (+⟦unverified: 0.0794⟧), `bill_mean_6m` (⟦unverified: -0.2543⟧), and `bill_trend_6m` (⟦unverified: -0.2207⟧) imply response curves that run counter to credit intuition, as set out in section 5. *Recommendation:* produce the ten response curves, investigate each reversal, and consider sign constraints on the affected coefficients.

**Low.** *Out-of-sample degradation on a single unreplicated split.* A ⟦unverified: 0.0354⟧ AUC gap and a ⟦unverified: 13.2%⟧ relative Gini loss, below the customary ⟦unverified: 0.05⟧ materiality threshold but unaccompanied by any cross-validation or interval estimate. *Recommendation:* report k-fold cross-validated AUC with dispersion.

**Low.** *Calibration evidenced only at the grand mean.* Aggregate bias is +⟦unverified: 0.0052⟧ on test, which is acceptable; no slope, decile table, or reliability curve has been produced. *Recommendation:* publish a ten-bucket observed-versus-expected table and a calibration slope from the existing scored tables.

**Low.** *Split integrity not demonstrated.* Whole-split row hashes distinguish the two splits but do not evidence row-level or client-level disjointness. *Recommendation:* publish the intersection count of `client_id` between [[art:929365b0:run.data_train]] and [[art:7ea4b8e1:run.data_test]].

**Low.** *Data integrity comparison incomplete; untreated extreme outliers.* No test-split profile exists, so the cross-split missingness comparison cannot be run; `bill_trend_6m` carries a ⟦unverified: -21.7⟧ sigma minimum with no documented treatment. *Recommendation:* profile the test split and refit with the two balance features winsorised at the ⟦unverified: 1⟧st and ⟦unverified: 99⟧th percentiles as a sensitivity check.

**Low.** *Declared VIF threshold not demonstrably satisfied.* The developer declares `vif_threshold: 10.0` but publishes VIF values only for the two removed features. *Recommendation:* publish final-specification VIFs against the declared threshold.

**Info.** *Leakage screened only by declaration.* Feature timing is declared as two `at_origination` and ten `before_period_start`, with zero `during_period` and zero `after_outcome` [[art:abbb748e:run.features]], and no single-feature AUC approaches a leakage-suggestive level implicitly — the strongest coefficient, `delinq_last`, sits inside a model whose total AUC is ⟦unverified: 0.7337⟧. The declaration has not been independently verified against extraction timestamps, and no per-feature AUC table was produced. No leakage is indicated; the check rests on the developer's own labelling.

**Info.** *Run telemetry.* The run status, duration, and runtime cap artifacts are present [[art:2922931d:run.status]], [[art:63f5ebcf:run.duration_s]], [[art:2ad8d1a5:runtime.max_seconds]] and nothing in the package indicates the run failed or breached its cap. The specific values were not restated in the developer's written summary; no defect is raised.

### F-001 · M1 collinearity · severity **medium**

The developer screened candidate features at a declared VIF threshold of 10.0 and removed bill_last (VIF 164.11) and utilisation_mean_6m (VIF 38.98). No VIF values, condition number, or correlation matrix has been published for the ten features that were retained, so the final specification has not been shown to satisfy the developer's own threshold. The retained set still contains three co-moving blocks: pay_ratio_last with pay_ratio_mean_6m; delinq_last with delinq_count_6m and delinq_max_6m; and bill_mean_6m with bill_trend_6m and with utilisation. Removing the two worst members of a correlated block typically leaves the survivors carrying unstable coefficients rather than curing the condition, and the expected symptom is visible: limit_bal takes a positive coefficient (+0.0794), implying a larger granted limit raises default odds; bill_mean_6m takes a negative coefficient (-0.2543), implying a larger average outstanding balance lowers them; and bill_trend_6m takes a negative coefficient (-0.2207), implying a rising balance trajectory is protective. Since inputs are standardised these magnitudes are directly comparable, and bill_mean_6m is the second-largest absolute coefficient in the model, so the anomaly is not confined to a negligible term. Recommend recomputing VIF and the design-matrix condition number on the final ten-feature matrix, publishing the values against the declared threshold, and reporting bootstrap coefficient distributions to establish whether the three signs are stable.

### F-002 · E1 effective challenge · severity **medium**

The artifact store contains no challenger model, no benchmark, and no baseline. The ten-feature logistic regression has not been compared against a single-feature delinq_last scorecard, against a parsimonious three-to-four feature specification, or against a more flexible alternative such as gradient boosting. Without any benchmark, the adequacy of the 0.7337 holdout AUC cannot be judged, the incremental contribution of the seven weakest features cannot be established, and the three counterintuitive coefficients cannot be shown to be earning their place in the specification. Effective challenge is a required element of model validation and its complete absence leaves the champion's selection unevidenced. Note that this finding asserts an absence of evidence rather than a demonstrated threshold breach: no challenger has been shown to beat the champion, because no challenger exists. Recommend building and registering at least two challengers, one deliberately simpler and one more flexible, and reporting holdout AUC, Gini, and Brier for each alongside the champion's 0.7337, 0.4673, and 0.1536.

### F-003 · S1 population drift · severity **medium**

No population stability index, score distribution comparison, or cohort-level breakdown exists anywhere in the artifact store, for either the features or the model output. The underlying data carry an application_cohort field spanning 2013 to 2016 with mean 2014.51, so the vintage information required to measure drift was present in the source and simply was not used. Compounding this, the holdout does not appear to be out-of-time: the split manifest records no temporal basis, and the training split's client_id values span the full 1 to 5,000 range with a mean of 2,511 against a 2,500.5 expectation for a uniform random draw, which is the signature of a random row-level partition across pooled vintages. A random split across four cohorts cannot detect drift by construction, since both sides of the comparison are mixtures of the same years in the same proportions. The model's stability over time is therefore entirely unevidenced and, under the current design, unmeasurable. No PSI threshold breach is asserted, because no PSI was computed. Recommend recutting the holdout out-of-time, fitting on 2013 to 2015 and testing on 2016, and publishing feature-level and score-level PSI between the fitting window and each subsequent vintage against a stated threshold of 0.10 for investigation and 0.25 for action.

### F-004 · X1 scenario analysis · severity **low**

No sensitivity analysis, stress specification, shocked input set, or response curve exists in the artifact store. Because the specification is linear in the standardised features with no splines, interactions, or binning, each feature's response curve is monotone in the log-odds by construction, so a monotonicity check cannot fail. What the curves would reveal is direction, and on the fitted coefficients three of the ten slope the wrong way: predicted default probability falls as average billed balance rises (bill_mean_6m, -0.2543) and as the balance trajectory steepens (bill_trend_6m, -0.2207), and rises as the granted credit limit rises (limit_bal, +0.0794). Under a scenario in which a client's balances grow while the limit is held fixed, this model reports the client as becoming safer. The wrong-signed curves are visible directly in the coefficient vector, which is why this is raised despite no scenario artifact having been produced. The linear form also cannot represent the threshold behaviour that delinquency counts usually exhibit, and no evidence has been offered that the linear approximation is adequate. Recommend producing univariate response curves for all ten features, a coefficient-stability exercise over bootstrap or leave-one-cohort-out resamples, and an adverse shock test on utilisation and the delinquency block reporting the shift in mean predicted probability.

### F-005 · O1 out-of-sample degradation · severity **low**

AUC falls from 0.7690 in-sample to 0.7337 out-of-sample, a gap of 0.0354. Gini falls from 0.5381 to 0.4673, a 13.2 percent relative loss of ranking power, and KS falls from 0.4426 to 0.4096. The AUC gap sits below the 0.05 threshold customarily applied for a material degradation finding, and for a ten-parameter model fitted on 3,500 rows with roughly 785 events (about 79 events per parameter) some in-sample optimism is expected and benign. It is recorded at low severity for two reasons: the relative Gini loss is not trivial, and the package contains no cross-validation folds, no bootstrap confidence interval, and no repeated-split evidence, so a reviewer cannot distinguish ordinary optimism from a genuine overfit. A single train/test partition yields a point estimate with no dispersion around it. Recommend reporting k-fold cross-validated AUC with its standard deviation so that the observed gap can be judged against sampling variability.

### F-006 · C1 calibration · severity **low**

Aggregate calibration is good: mean predicted probability on the holdout is 0.2292 against an observed event rate of 0.2240, an absolute over-prediction of 0.0052 and a relative over-prediction of 2.3 percent, conservative in direction and inside any reasonable tolerance band. The in-sample agreement of 0.2243 against 0.2243 is the arithmetic consequence of fitting an intercept by maximum likelihood and is not independent evidence. No calibration diagnostic below the grand mean has been produced: there is no calibration slope from a regression of outcome on log-odds, no decile or bucketed observed-versus-expected table, no Hosmer-Lemeshow statistic, and no reliability curve. A model can match the population mean exactly while being badly miscalibrated in the upper deciles that actually drive credit decisions, with over- and under-prediction cancelling in the average. The scored tables contain everything needed to build these diagnostics and they were simply not built. Severity is low because the aggregate evidence available is reassuring and no band breach can be demonstrated. Recommend publishing a ten-bucket observed-versus-expected table and a calibration slope from the existing prediction tables.

### F-007 · L2 contamination · severity **low**

The split manifest records distinct whole-split digests, 16cd92c5 for the 3,500-row training split and 0ab5339f for the 1,500-row test split. These confirm that the two splits are not the same set of rows, but they carry no information about row-level or client-level overlap between them. The training profile shows client_id ranging from 1 to 5,000, and 3,500 plus 1,500 sums exactly to 5,000, so a clean disjoint partition of distinct clients is the most probable reading of the design. That reading has not been demonstrated: no per-row or per-client intersection count exists in the store, and no contamination check appears to have been run. This finding records the check as unexecuted rather than as failed; no overlap above any threshold is asserted. Recommend publishing the intersection count of client_id between the train and test tables, and confirming that the partition is by client rather than by row so that no client contributes observations to both sides.

### F-008 · D1 data integrity · severity **low**

The required integrity check, that missingness rates do not differ materially between the development and holdout extracts, cannot be executed because no profile artifact exists for the test split. The training profile reports zero missingness in every one of thirteen columns, which is unusual for retail credit data and means the model carries no evidence about its behaviour when an input is absent; no imputation or missing-indicator policy is documented. Weak indirect evidence that both extracts were drawn the same way comes from the near-identical event rates, 0.2243 on train against 0.2240 on test. Separately, bill_trend_6m has mean -246.3 and standard deviation 3,095.6 but a minimum of -67,201.4 and a maximum of 27,398.0, roughly -21.7 and +8.9 standard deviations; bill_mean_6m is similarly skewed with a maximum of 443,112 against a mean of 47,238. In a standardised logistic regression, observations at twenty-odd sigma dominate the standardisation constants and can materially move the fitted coefficient, and no winsorisation, clipping, or transformation is documented for either field. Both features carry counterintuitive negative signs, so the interaction between untreated outliers and coefficient estimation is a plausible contributing cause. Recommend profiling the test split and refitting with both balance features winsorised at the 1st and 99th percentiles as a sensitivity check.

### F-009 · T1 declared threshold · severity **low**

The model summary declares vif_threshold: 10.0 and standardised: true, and reports VIF values only for the two features that were removed, bill_last at 164.11 and utilisation_mean_6m at 38.98. No VIF is reported for any of the ten features that were retained. The implicit claim carried by a declared threshold is that the delivered specification meets it, and that claim is undemonstrated on the published evidence. Given the correlated blocks that remain in the retained set, it is not safe to assume that removing the two worst offenders brought all survivors below 10.0; iterative VIF elimination routinely requires several passes, and only one pass is documented. This is recorded separately from the multicollinearity finding because the issue here is the unsubstantiated threshold claim rather than the statistical condition itself. Recommend publishing final-specification VIF values for all ten retained features against the declared threshold, and documenting whether the screen was applied iteratively or in a single pass.

### F-010 · L1 leakage · severity **info**

The feature inventory declares twelve candidates with timing labels: two at_origination, ten before_period_start, zero during_period, and zero after_outcome. On the declared timing there is no forward-looking information in the design, and the dominant coefficient, delinq_last at 0.7518, is economically the correct variable to dominate a next-month default model. No single feature can plausibly be carrying leakage-level signal given that the full ten-feature model reaches only 0.7690 in-sample and 0.7337 out-of-sample AUC, which bounds any individual contribution well below a leakage-suggestive level. However, the timing declarations have not been independently verified against extraction timestamps or source-system cut dates, and no per-feature univariate AUC table was produced, so the screen rests entirely on the developer's own labelling. No leakage is indicated and no remediation is attached; this is recorded as an observation so that the basis of the clean leakage assessment is transparent. Recommend publishing per-feature univariate AUCs and confirming the timing labels against extraction metadata at the next review.

Candidates raised and not promoted: none.

### Open items

No open item was recorded for this validation.

## 7. Ongoing monitoring recommendations

Monitoring should be structured around the three things this validation could not establish: stability over time, calibration in the tail, and the stability of the counterintuitive coefficients.

*Monthly.* Track the realised default rate against the mean predicted probability for the scored population, with an alert if the absolute gap exceeds ⟦unverified: 0.020⟧ or the relative gap exceeds ⟦unverified: 10%⟧ for two consecutive months; the current out-of-sample gap of ⟦unverified: 0.0052⟧ is a reasonable baseline. Track mean and standard deviation of the score distribution and compute score PSI against the development sample, investigating at ⟦unverified: 0.10⟧ and escalating at ⟦unverified: 0.25⟧.

*Quarterly.* Recompute AUC, Gini, KS, and Brier on the accumulated out-of-time window and compare against the holdout baselines of ⟦unverified: 0.7337⟧, ⟦unverified: 0.4673⟧, ⟦unverified: 0.4096⟧, and ⟦unverified: 0.1536⟧. Escalate on an AUC fall below ⟦unverified: 0.68⟧ or a Brier rise above ⟦unverified: 0.165⟧, which would put the model within sight of the ⟦unverified: 0.1738⟧ no-skill reference. Publish a ten-bucket observed-versus-expected calibration table and a calibration slope each quarter; a slope drifting materially below 1.0 indicates the score has become over-dispersed and requires recalibration of the intercept and slope before any refit is considered. Compute feature-level PSI for all ten retained inputs, with particular attention to `utilisation`, `delinq_last`, and `bill_mean_6m`, which carry the three largest absolute coefficients.

*Annually, or on breach.* Refit the specification on the most recent window and compare the full coefficient vector against the incumbent, with explicit attention to whether `limit_bal`, `bill_mean_6m`, and `bill_trend_6m` retain their current signs; a sign flip in any of the three across refits confirms the collinearity diagnosis in section 6 and should trigger respecification rather than recalibration. Re-run the challenger comparison against the same benchmarks each year so that the champion's continued selection is an evidenced decision. Re-profile both splits for missingness and outlier incidence, since the current zero-missingness position is unlikely to persist in live data and the model has no documented missing-value policy.

*Triggers for out-of-cycle review.* Any of the following should force a review ahead of schedule: score PSI above ⟦unverified: 0.25⟧; two consecutive quarters of AUC below ⟦unverified: 0.68⟧; an absolute calibration gap above ⟦unverified: 0.030⟧ in any month; a change in the upstream definition of the delinquency or billing fields; or a shift in the underwriting policy that governs `limit_bal`, given that this feature currently carries a positive and unexplained coefficient and the model's behaviour under a changed limit-setting regime is not understood.

## Appendix A — Claims

Grounding precision 0.0000 before repair (0 of 130 claims verified; 103 unsupported, 27 dangling) and 0.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 0/19; conceptual_soundness 0/10; data_integrity 0/28; outcomes 0/34; sensitivity 0/1; findings 0/23; monitoring 0/15.

Developer claims: `plain_llm` runs no check over `package.yaml`'s declared claims See Appendix D.

Excluded numeric tokens (not claims): section_number (section 6, section 3, section 2, section 5); inline_code (`16cd92c5…`, `0ab5339f…`, `vif_threshold: 10.0`); citation_hash (15071cdb, 1013df27, 6ce7b4d6, abbb748e); package_version (1.0); extractor_returned_excluded_token (1.0, 12.0, 2.0, 10.0).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | This report documents an independent validation of package `… | -1.3967 | ratio | coefficient |  | eq | `[[art:15071cdb:run.model_summary]]` | dangling |  |
| 2 | summary | This report documents an independent validation of package `… | 3500 | count | n_rows | train | eq | `[[art:1013df27:run.splits]]` | dangling |  |
| 3 | summary | This report documents an independent validation of package `… | 1500 | count | n_rows | test | eq | `[[art:1013df27:run.splits]]` | dangling |  |
| 4 | summary | This report documents an independent validation of package `… | 5000 | count | n_rows |  | eq | `[[art:1013df27:run.splits]]` | dangling |  |
| 5 | summary | This report documents an independent validation of package `… | 2013 | ratio |  |  | eq | `[[art:1013df27:run.splits]]` | dangling |  |
| 6 | summary | This report documents an independent validation of package `… | 2016 | ratio |  |  | eq | `[[art:1013df27:run.splits]]` | dangling |  |
| 7 | summary | Headline discriminatory performance is AUC 0.7690 in-sample… | 0.769 | ratio | auc | train | eq | `[[art:6ce7b4d6:run.metrics]]` | dangling |  |
| 8 | summary | Headline discriminatory performance is AUC 0.7690 in-sample… | 0.7337 | ratio | auc | test | eq | `[[art:6ce7b4d6:run.metrics]]` | dangling |  |
| 9 | summary | Headline discriminatory performance is AUC 0.7690 in-sample… | 0.5381 | ratio | gini | train | eq | `[[art:6ce7b4d6:run.metrics]]` | dangling |  |
| 10 | summary | Headline discriminatory performance is AUC 0.7690 in-sample… | 0.4673 | ratio | gini | test | eq | `[[art:6ce7b4d6:run.metrics]]` | dangling |  |
| 11 | summary | Headline discriminatory performance is AUC 0.7690 in-sample… | 0.4426 | ratio | ks | train | eq | `[[art:6ce7b4d6:run.metrics]]` | dangling |  |
| 12 | summary | Headline discriminatory performance is AUC 0.7690 in-sample… | 0.4096 | ratio | ks | test | eq | `[[art:6ce7b4d6:run.metrics]]` | dangling |  |
| 13 | summary | Headline discriminatory performance is AUC 0.7690 in-sample… | 0.2292 | ratio | mean_predicted | test | eq |  | unsupported |  |
| 14 | summary | Headline discriminatory performance is AUC 0.7690 in-sample… | 0.224 | ratio | event_rate | test | eq |  | unsupported |  |
| 15 | summary | Headline discriminatory performance is AUC 0.7690 in-sample… | 0.2243 | ratio | mean_predicted | train | eq |  | unsupported |  |
| 16 | summary | Headline discriminatory performance is AUC 0.7690 in-sample… | 0.2243 | ratio | event_rate | train | eq |  | unsupported |  |
| 17 | summary | Headline discriminatory performance is AUC 0.7690 in-sample… | 0.1738 | ratio | brier |  | eq |  | unsupported |  |
| 18 | summary | Headline discriminatory performance is AUC 0.7690 in-sample… | 14 | percent | brier | train | eq |  | unsupported |  |
| 19 | summary | Headline discriminatory performance is AUC 0.7690 in-sample… | 12 | percent | brier | test | eq |  | unsupported |  |
| 20 | conceptual_soundness | The choice of a logistic regression for a binary default out… | 0.7518 | ratio | coefficient |  | eq |  | unsupported |  |
| 21 | conceptual_soundness | The sign pattern is, however, only partly coherent. Four of… | 0.2801 | ratio | coefficient |  | eq |  | unsupported |  |
| 22 | conceptual_soundness | The sign pattern is, however, only partly coherent. Four of… | 0.7518 | ratio | coefficient |  | eq |  | unsupported |  |
| 23 | conceptual_soundness | The sign pattern is, however, only partly coherent. Four of… | 0.0638 | ratio | coefficient |  | eq |  | unsupported |  |
| 24 | conceptual_soundness | The sign pattern is, however, only partly coherent. Four of… | 0.0313 | ratio | coefficient |  | eq |  | unsupported |  |
| 25 | conceptual_soundness | The sign pattern is, however, only partly coherent. Four of… | -0.0088 | ratio | coefficient |  | eq |  | unsupported |  |
| 26 | conceptual_soundness | The sign pattern is, however, only partly coherent. Four of… | -0.2204 | ratio | coefficient |  | eq |  | unsupported |  |
| 27 | conceptual_soundness | The sign pattern is, however, only partly coherent. Four of… | 0.0794 | ratio | coefficient |  | eq |  | unsupported |  |
| 28 | conceptual_soundness | The sign pattern is, however, only partly coherent. Four of… | -0.2543 | ratio | coefficient |  | eq |  | unsupported |  |
| 29 | conceptual_soundness | The sign pattern is, however, only partly coherent. Four of… | -0.2207 | ratio | coefficient |  | eq |  | unsupported |  |
| 30 | data_integrity | The training profile reports 3,500 rows with **zero missingn… | 3500 | count |  | train | eq |  | unsupported |  |
| 31 | data_integrity | A comparable profile for the test split has not been produce… | 0.2243 | ratio | event_rate | train | eq | `[[art:1013df27:run.splits]]` | dangling |  |
| 32 | data_integrity | A comparable profile for the test split has not been produce… | 0.224 | ratio | event_rate | test | eq | `[[art:1013df27:run.splits]]` | dangling |  |
| 33 | data_integrity | Distributional integrity of the inputs is mostly unremarkabl… | 10000 | currency |  | train | eq |  | unsupported |  |
| 34 | data_integrity | Distributional integrity of the inputs is mostly unremarkabl… | 800000 | currency |  | train | eq |  | unsupported |  |
| 35 | data_integrity | Distributional integrity of the inputs is mostly unremarkabl… | 106204 | currency |  | train | eq |  | unsupported |  |
| 36 | data_integrity | Distributional integrity of the inputs is mostly unremarkabl… | 21 | ratio |  | train | eq |  | unsupported |  |
| 37 | data_integrity | Distributional integrity of the inputs is mostly unremarkabl… | 63 | ratio |  | train | eq |  | unsupported |  |
| 38 | data_integrity | Distributional integrity of the inputs is mostly unremarkabl… | 0.0045 | ratio |  | train | eq |  | unsupported |  |
| 39 | data_integrity | Distributional integrity of the inputs is mostly unremarkabl… | 1.1297 | ratio |  | train | eq |  | unsupported |  |
| 40 | data_integrity | Distributional integrity of the inputs is mostly unremarkabl… | -246.3 | currency |  | train | eq |  | unsupported |  |
| 41 | data_integrity | Distributional integrity of the inputs is mostly unremarkabl… | 3095.6 | currency |  | train | eq |  | unsupported |  |
| 42 | data_integrity | Distributional integrity of the inputs is mostly unremarkabl… | -67201.4 | currency |  | train | eq |  | unsupported |  |
| 43 | data_integrity | Distributional integrity of the inputs is mostly unremarkabl… | 27398 | currency |  | train | eq |  | unsupported |  |
| 44 | data_integrity | Distributional integrity of the inputs is mostly unremarkabl… | -21.7 | ratio |  | train | eq |  | unsupported |  |
| 45 | data_integrity | Distributional integrity of the inputs is mostly unremarkabl… | 8.9 | ratio |  | train | eq |  | unsupported |  |
| 46 | data_integrity | Distributional integrity of the inputs is mostly unremarkabl… | 443112 | currency |  | train | eq |  | unsupported |  |
| 47 | data_integrity | Distributional integrity of the inputs is mostly unremarkabl… | 47238 | currency |  | train | eq |  | unsupported |  |
| 48 | data_integrity | On drift, the store contains **no population stability index… | 2013 | ratio |  |  | eq |  | unsupported |  |
| 49 | data_integrity | On drift, the store contains **no population stability index… | 2016 | ratio |  |  | eq |  | unsupported |  |
| 50 | data_integrity | On drift, the store contains **no population stability index… | 2014.51 | ratio |  |  | eq |  | unsupported |  |
| 51 | data_integrity | On drift, the store contains **no population stability index… | 1 | count |  | train | eq | `[[art:1013df27:run.splits]]` | dangling |  |
| 52 | data_integrity | On drift, the store contains **no population stability index… | 5000 | count |  | train | eq | `[[art:1013df27:run.splits]]` | dangling |  |
| 53 | data_integrity | On drift, the store contains **no population stability index… | 2511 | ratio |  | train | eq | `[[art:1013df27:run.splits]]` | dangling |  |
| 54 | data_integrity | On drift, the store contains **no population stability index… | 2500.5 | ratio |  | train | eq | `[[art:1013df27:run.splits]]` | dangling |  |
| 55 | data_integrity | On contamination, the split manifest records distinct `rows_… | 3500 | count |  | train | eq |  | unsupported |  |
| 56 | data_integrity | On contamination, the split manifest records distinct `rows_… | 1500 | count |  | test | eq |  | unsupported |  |
| 57 | data_integrity | On contamination, the split manifest records distinct `rows_… | 5000 | count |  |  | eq |  | unsupported |  |
| 58 | outcomes | Discrimination is moderate and typical for a credit default… | 0.7337 | ratio | auc | test | eq | `[[art:6ce7b4d6:run.metrics]]` | dangling |  |
| 59 | outcomes | Discrimination is moderate and typical for a credit default… | 0.4673 | ratio | gini | test | eq | `[[art:6ce7b4d6:run.metrics]]` | dangling |  |
| 60 | outcomes | Discrimination is moderate and typical for a credit default… | 0.4096 | ratio | ks | test | eq | `[[art:6ce7b4d6:run.metrics]]` | dangling |  |
| 61 | outcomes | Discrimination is moderate and typical for a credit default… | 1500 | count | n_obs | test | eq | `[[art:6ce7b4d6:run.metrics]]` | dangling |  |
| 62 | outcomes | Discrimination is moderate and typical for a credit default… | 336 | count | n_events | test | eq | `[[art:6ce7b4d6:run.metrics]]` | dangling |  |
| 63 | outcomes | Discrimination is moderate and typical for a credit default… | 0.224 | ratio | event_rate | test | eq | `[[art:6ce7b4d6:run.metrics]]` | dangling |  |
| 64 | outcomes | Discrimination is moderate and typical for a credit default… | 0.769 | ratio | auc | train | eq |  | unsupported |  |
| 65 | outcomes | Discrimination is moderate and typical for a credit default… | 0.5381 | ratio | gini | train | eq |  | unsupported |  |
| 66 | outcomes | Discrimination is moderate and typical for a credit default… | 0.4426 | ratio | ks | train | eq |  | unsupported |  |
| 67 | outcomes | Discrimination is moderate and typical for a credit default… | 3500 | count | n_obs | train | eq |  | unsupported |  |
| 68 | outcomes | The train-to-test AUC gap is 0.0354. In relative terms the G… | 0.0354 | ratio | delta_auc |  | delta |  | unsupported |  |
| 69 | outcomes | The train-to-test AUC gap is 0.0354. In relative terms the G… | 0.5381 | ratio | gini | train | eq |  | unsupported |  |
| 70 | outcomes | The train-to-test AUC gap is 0.0354. In relative terms the G… | 0.4673 | ratio | gini | test | eq |  | unsupported |  |
| 71 | outcomes | The train-to-test AUC gap is 0.0354. In relative terms the G… | 13.2 | percent | gini |  | eq |  | unsupported |  |
| 72 | outcomes | The train-to-test AUC gap is 0.0354. In relative terms the G… | 0.033 | ratio | delta_ks |  | delta (down) |  | unsupported |  |
| 73 | outcomes | The train-to-test AUC gap is 0.0354. In relative terms the G… | 0.05 | ratio | delta_auc |  | eq |  | unsupported |  |
| 74 | outcomes | The train-to-test AUC gap is 0.0354. In relative terms the G… | 3500 | count | n_obs | train | eq |  | unsupported |  |
| 75 | outcomes | The train-to-test AUC gap is 0.0354. In relative terms the G… | 785 | count | n_events | train | eq |  | unsupported |  |
| 76 | outcomes | The train-to-test AUC gap is 0.0354. In relative terms the G… | 79 | ratio | events_per_parameter | train | eq |  | unsupported |  |
| 77 | outcomes | Probability accuracy is good in aggregate. The Brier score i… | 0.1536 | ratio | brier | test | eq |  | unsupported |  |
| 78 | outcomes | Probability accuracy is good in aggregate. The Brier score i… | 0.224 | ratio | event_rate | test | eq |  | unsupported |  |
| 79 | outcomes | Probability accuracy is good in aggregate. The Brier score i… | 0.776 | ratio | event_rate | test | eq |  | unsupported |  |
| 80 | outcomes | Probability accuracy is good in aggregate. The Brier score i… | 0.1738 | ratio | brier | test | eq |  | unsupported |  |
| 81 | outcomes | Probability accuracy is good in aggregate. The Brier score i… | 11.7 | percent | brier_skill_score | test | eq |  | unsupported |  |
| 82 | outcomes | Probability accuracy is good in aggregate. The Brier score i… | 0.1489 | ratio | brier | train | eq |  | unsupported |  |
| 83 | outcomes | Probability accuracy is good in aggregate. The Brier score i… | 14.4 | percent | brier_skill_score | train | eq |  | unsupported |  |
| 84 | outcomes | Probability accuracy is good in aggregate. The Brier score i… | 0.4788 | ratio | log_loss | test | eq |  | unsupported |  |
| 85 | outcomes | Probability accuracy is good in aggregate. The Brier score i… | 0.4632 | ratio | log_loss | train | eq |  | unsupported |  |
| 86 | outcomes | Aggregate calibration is close to unbiased. Mean predicted p… | 0.2292 | ratio | mean_predicted | test | eq |  | unsupported |  |
| 87 | outcomes | Aggregate calibration is close to unbiased. Mean predicted p… | 0.224 | ratio | event_rate | test | eq |  | unsupported |  |
| 88 | outcomes | Aggregate calibration is close to unbiased. Mean predicted p… | 0.0052 | ratio | calibration_gap | test | delta |  | unsupported |  |
| 89 | outcomes | Aggregate calibration is close to unbiased. Mean predicted p… | 2.3 | percent | calibration_gap | test | eq |  | unsupported |  |
| 90 | outcomes | Aggregate calibration is close to unbiased. Mean predicted p… | 2.3 | percent | calibration_gap | test | eq |  | unsupported |  |
| 91 | outcomes | No segmentation of outcomes has been performed. Performance… | 0.7337 | ratio | auc | test | eq |  | unsupported |  |
| 92 | sensitivity | The work that would normally appear here, and that the avail… | -21.7 | ratio |  |  | eq |  | unsupported |  |
| 93 | findings | **Medium.** *Residual multicollinearity and unverified sign… | 10 | ratio | vif_threshold |  | eq | `[[art:15071cdb:run.model_summary#removed]]` | dangling |  |
| 94 | findings | **Medium.** *Residual multicollinearity and unverified sign… | 164.11 | ratio | vif |  | eq | `[[art:15071cdb:run.model_summary#removed]]` | dangling |  |
| 95 | findings | **Medium.** *Residual multicollinearity and unverified sign… | 38.98 | ratio | vif |  | eq | `[[art:15071cdb:run.model_summary#removed]]` | dangling |  |
| 96 | findings | **Medium.** *Residual multicollinearity and unverified sign… | 10 | ratio | vif_threshold |  | eq |  | unsupported |  |
| 97 | findings | **Medium.** *No effective challenge.* No challenger model of… | 0.7337 | ratio | auc |  | eq |  | unsupported |  |
| 98 | findings | **Medium.** *No drift measurement and a non-temporal holdout… | 2013 | ratio |  |  | eq |  | unsupported |  |
| 99 | findings | **Medium.** *No drift measurement and a non-temporal holdout… | 2016 | ratio |  |  | eq |  | unsupported |  |
| 100 | findings | **Medium.** *No drift measurement and a non-temporal holdout… | 2013 | ratio |  |  | eq |  | unsupported |  |
| 101 | findings | **Medium.** *No drift measurement and a non-temporal holdout… | 2015 | ratio |  |  | eq |  | unsupported |  |
| 102 | findings | **Medium.** *No drift measurement and a non-temporal holdout… | 2016 | ratio |  |  | eq |  | unsupported |  |
| 103 | findings | **Medium.** *No drift measurement and a non-temporal holdout… | 0.1 | ratio | psi |  | eq |  | unsupported |  |
| 104 | findings | **Medium.** *No drift measurement and a non-temporal holdout… | 0.25 | ratio | psi |  | eq |  | unsupported |  |
| 105 | findings | **Low.** *Wrong-signed response curves.* `limit_bal` (+0.079… | 0.0794 | ratio | coefficient |  | eq |  | unsupported |  |
| 106 | findings | **Low.** *Wrong-signed response curves.* `limit_bal` (+0.079… | -0.2543 | ratio | coefficient |  | eq |  | unsupported |  |
| 107 | findings | **Low.** *Wrong-signed response curves.* `limit_bal` (+0.079… | -0.2207 | ratio | coefficient |  | eq |  | unsupported |  |
| 108 | findings | **Low.** *Out-of-sample degradation on a single unreplicated… | 0.0354 | ratio | delta_auc |  | delta |  | unsupported |  |
| 109 | findings | **Low.** *Out-of-sample degradation on a single unreplicated… | 13.2 | percent | gini |  | eq |  | unsupported |  |
| 110 | findings | **Low.** *Out-of-sample degradation on a single unreplicated… | 0.05 | ratio | delta_auc |  | eq |  | unsupported |  |
| 111 | findings | **Low.** *Calibration evidenced only at the grand mean.* Agg… | 0.0052 | ratio | calibration_bias | test | eq |  | unsupported |  |
| 112 | findings | **Low.** *Data integrity comparison incomplete; untreated ex… | -21.7 | ratio | min_sigma |  | eq |  | unsupported |  |
| 113 | findings | **Low.** *Data integrity comparison incomplete; untreated ex… | 1 | ratio |  |  | eq |  | unsupported |  |
| 114 | findings | **Low.** *Data integrity comparison incomplete; untreated ex… | 99 | ratio |  |  | eq |  | unsupported |  |
| 115 | findings | **Info.** *Leakage screened only by declaration.* Feature ti… | 0.7337 | ratio | auc |  | eq |  | unsupported |  |
| 116 | monitoring | *Monthly.* Track the realised default rate against the mean… | 0.02 | ratio | calibration_gap |  | eq |  | unsupported |  |
| 117 | monitoring | *Monthly.* Track the realised default rate against the mean… | 10 | percent | calibration_gap |  | eq |  | unsupported |  |
| 118 | monitoring | *Monthly.* Track the realised default rate against the mean… | 0.0052 | ratio | calibration_gap | test | eq |  | unsupported |  |
| 119 | monitoring | *Monthly.* Track the realised default rate against the mean… | 0.1 | ratio | psi |  | eq |  | unsupported |  |
| 120 | monitoring | *Monthly.* Track the realised default rate against the mean… | 0.25 | ratio | psi |  | eq |  | unsupported |  |
| 121 | monitoring | *Quarterly.* Recompute AUC, Gini, KS, and Brier on the accum… | 0.7337 | ratio | auc | test | eq |  | unsupported |  |
| 122 | monitoring | *Quarterly.* Recompute AUC, Gini, KS, and Brier on the accum… | 0.4673 | ratio | gini | test | eq |  | unsupported |  |
| 123 | monitoring | *Quarterly.* Recompute AUC, Gini, KS, and Brier on the accum… | 0.4096 | ratio | ks | test | eq |  | unsupported |  |
| 124 | monitoring | *Quarterly.* Recompute AUC, Gini, KS, and Brier on the accum… | 0.1536 | ratio | brier | test | eq |  | unsupported |  |
| 125 | monitoring | *Quarterly.* Recompute AUC, Gini, KS, and Brier on the accum… | 0.68 | ratio | auc | out_of_time | eq |  | unsupported |  |
| 126 | monitoring | *Quarterly.* Recompute AUC, Gini, KS, and Brier on the accum… | 0.165 | ratio | brier | out_of_time | eq |  | unsupported |  |
| 127 | monitoring | *Quarterly.* Recompute AUC, Gini, KS, and Brier on the accum… | 0.1738 | ratio | brier |  | eq |  | unsupported |  |
| 128 | monitoring | *Triggers for out-of-cycle review.* Any of the following sho… | 0.25 | ratio | psi |  | eq |  | unsupported |  |
| 129 | monitoring | *Triggers for out-of-cycle review.* Any of the following sho… | 0.68 | ratio | auc |  | eq |  | unsupported |  |
| 130 | monitoring | *Triggers for out-of-cycle review.* Any of the following sho… | 0.03 | ratio | calibration_gap |  | eq |  | unsupported |  |

## Appendix B — Artifact index

The store holds 14 artifacts; the 13 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `run.data_test` | `7ea4b8e1` | table | table, 1500 rows | the subject's data_test.csv |
| `run.data_train` | `929365b0` | table | table, 3500 rows | the subject's data_train.csv |
| `run.duration_s` | `63f5ebcf` | scalar | 1.3932415 | subject wall-clock seconds |
| `run.features` | `abbb748e` | json | json | the subject's features.json |
| `run.metrics` | `6ce7b4d6` | json | json | the subject's metrics.json |
| `run.model_summary` | `15071cdb` | json | json | the subject's model_summary.json |
| `run.predictions_test` | `9936180e` | table | table, 1500 rows | the subject's predictions_test.csv |
| `run.predictions_train` | `fc881548` | table | table, 3500 rows | the subject's predictions_train.csv |
| `run.splits` | `1013df27` | json | json | the subject's splits.json |
| `run.status` | `2922931d` | json | json | how the subject's subprocess ended |
| `run.stderr` | `41728c38` | json | json | the subject's stderr |
| `run.stdout` | `07e84a56` | json | json | the subject's stdout |
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |

## Appendix C — Run trace summary

| quantity | value |
|---|---|
| tool calls | 1 (run_model 1) |
| plan steps (bounded loop) | 0 |
| LLM calls | 8 (plain_llm 1, extract 7) |
| re-asks | 0 |
| repair rounds | 0 |
| tokens in / out | 61,455 / 38,979 |
| notional cost (USD) | 1.5746 |
| wall-clock (s) | 465.45 |
| subject run (s) | 1.39 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | credit_default-plain_llm-20260918T183409Z-6e98ce62 |

## Appendix D — Not checked

| item | reason |
|---|---|
| `check_stability` (R1) | this configuration runs no checks |
| `run_scenarios` (X1) | not applicable to `binary_classification` |
| out-of-time and vintage-holdout metrics (O1, second rule) | package declares neither split |
| developer claims (T1, claim channel) | `plain_llm` runs no check over `package.yaml`'s declared claims |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
| every check of spec 3.7 but `run_model` | `plain_llm` runs the subject and one model call, by design |
