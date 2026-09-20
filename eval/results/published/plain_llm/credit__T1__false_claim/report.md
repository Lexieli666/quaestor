---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: plain_llm
model: claude-opus-5[1m]
run_id: credit_default-plain_llm-20260918T190251Z-6e98ce62
data_mode: synthetic
synthetic_n: 5000
grounding_precision_pre: 0.0000
grounding_precision_post: 0.0000
n_claims: 124
n_findings_by_severity: {high: 0, medium: 2, low: 4, info: 2}
generated: "2026-09-18T19:02:51Z"
illustrative: false
---

# Validation report — `credit_default` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `credit_default` v1.0 | `plain_llm` | claude-opus-5[1m] | synthetic, n = 5000 | 0.0000 → 0.0000 | 0 / 2 / 4 / 2 |
<!-- quaestor:renderer:end -->

This report documents the independent validation of package `credit_default` version 1.0, a binary classification model that estimates the probability of `default_next_month` for revolving credit clients. The subject is a standardised logistic regression with ten retained predictors and an intercept of ⟦unverified: -1.395828⟧ ([[art:74c10f15:run.model_summary]]), fitted on ⟦unverified: 3,500⟧ training rows and evaluated on ⟦unverified: 1,500⟧ test rows ([[art:3b6b0a38:run.splits]]).

The validation was performed against the developer-supplied artifact store only. The evidence available comprises the fitted model summary ([[art:74c10f15:run.model_summary]]), the performance metrics ([[art:aebcad6a:run.metrics]]), the feature inventory and timing declarations ([[art:abbb748e:run.features]]), the split manifest ([[art:3b6b0a38:run.splits]]), the training and test design matrices ([[art:6a89f2be:run.data_train]], [[art:26fbbf1d:run.data_test]]), the scored prediction tables ([[art:6fd8f98a:run.predictions_train]], [[art:66bafeec:run.predictions_test]]), and the run telemetry ([[art:2922931d:run.status]], [[art:5d8f71ad:run.stdout]], [[art:41728c38:run.stderr]], [[art:2c131563:run.duration_s]], [[art:2ad8d1a5:runtime.max_seconds]]).

Headline discrimination is acceptable for a retail behavioural scorecard: test AUC ⟦unverified: 0.747989⟧, Gini ⟦unverified: 0.495978⟧, KS ⟦unverified: 0.418268⟧ ([[art:aebcad6a:run.metrics#test]]). Aggregate calibration on test is close, with mean predicted ⟦unverified: 0.221105⟧ against an observed event rate of ⟦unverified: 0.224667⟧ ([[art:aebcad6a:run.metrics#test]]).

The material weaknesses are not in headline performance. They are (a) a block of economically implausible coefficient signs that is the residue of the multicollinearity the developer partially treated, and (b) an evidence gap: the store contains no calibration curve, no population-stability computation, no challenger model, and no sensitivity or scenario output. Sections ⟦unverified: 5⟧ and ⟦unverified: 7⟧ below are therefore written in large part as statements of what could not be tested rather than what was tested, and the reader should treat them that way.

**Scope limitation.** No out-of-time sample, no segment-level performance, no score-cut or confusion analysis, and no profile of the test split were supplied. Several standard validation tests are consequently unexecutable on this evidence base, and the conclusions of this report are conditional on that.

## 2. Conceptual soundness

**Model form.** Logistic regression on ten standardised predictors ([[art:74c10f15:run.model_summary]]) is a defensible and conventional choice for this use case. It is transparent, monotone in each predictor by construction, and its coefficients are directly reviewable — which is what makes the sign problems below visible and therefore reviewable at all. `class_weight` is null; with an event rate of ⟦unverified: 0.2246⟧ ([[art:3b6b0a38:run.splits]]) the class imbalance is mild and no reweighting is required. Because the features are standardised, coefficient magnitudes are directly comparable as per-standard-deviation effects.

**Feature timing.** The inventory declares twelve features, of which two are `at_origination` and ten are `before_period_start`; zero are declared `during_period` and zero `after_outcome` ([[art:abbb748e:run.features]]). The counts reconcile to the twelve listed items. On the developer's own declarations there is no target leakage by construction, and no single feature exhibits the discrimination that would signal an undeclared leak — the full ten-feature model reaches only ⟦unverified: 0.747989⟧ AUC ([[art:aebcad6a:run.metrics#test]]), so no individual predictor can be carrying a leaked outcome. We accept the timing declarations as plausible but note they are declarations: no independent verification of the observation windows was possible from the store.

**Signs and economic plausibility.** This is where the model fails to satisfy conceptual review. Of the ten retained coefficients ([[art:74c10f15:run.model_summary#coefficients]]), four carry signs that contradict credit intuition or contradict a sibling feature measuring the same construct:

| Feature | Coefficient | Expected sign | Assessment |
|---|---|---|---|
| `delinq_last` | +⟦unverified: 0.733422⟧ | + | Correct, and correctly dominant (OR ⟦unverified: 2.08⟧ per SD) |
| `utilisation` | +⟦unverified: 0.266208⟧ | + | Correct |
| `delinq_count_6m` | +⟦unverified: 0.122580⟧ | + | Correct |
| `age` | ⟦unverified: -0.067258⟧ | - | Correct |
| `pay_ratio_mean_6m` | ⟦unverified: -0.355372⟧ | - | Correct |
| `delinq_max_6m` | **⟦unverified: -0.032214⟧** | + | **Wrong sign** — worst delinquency in six months reduces predicted risk |
| `pay_ratio_last` | **+⟦unverified: 0.102591⟧** | - | **Wrong sign**, and opposite its own six-month mean |
| `limit_bal` | **+⟦unverified: 0.072656⟧** | - | **Counterintuitive** — a larger granted limit raises predicted risk |
| `bill_mean_6m` | **⟦unverified: -0.372628⟧** | ambiguous/+ | Large negative, second-largest effect in the model |
| `bill_trend_6m` | ⟦unverified: -0.222475⟧ | ambiguous | Rising balances reduce risk; weakly defensible at best |

The pattern is diagnostic rather than random. `pay_ratio_last` and `pay_ratio_mean_6m` measure the same construct at two horizons and carry opposite signs; `delinq_last`, `delinq_count_6m` and `delinq_max_6m` form a three-member block of which the maximum-severity member alone goes negative. These are the classic signatures of a partially-treated collinear block, in which surviving variables absorb compensating signs from the variables that remain correlated with them. See section 6, finding M1.

The intercept of ⟦unverified: -1.395828⟧ implies a probability of ⟦unverified: 0.1985⟧ at the mean of every standardised feature, against a sample mean prediction of ⟦unverified: 0.224623⟧. The gap is the expected consequence of the convexity of the logistic link and is not a defect.

## 3. Data integrity and drift

**Completeness.** The training profile reports ⟦unverified: 0.0⟧ missingness on all thirteen columns including the target ([[art:6a89f2be:run.data_train]]). Completeness on the training split is therefore not a concern. No equivalent profile was supplied for the test split ([[art:26fbbf1d:run.data_test]]), so the standard cross-split missingness comparison could not be performed and no conclusion on differential missingness can be drawn in either direction.

**Split integrity.** The two splits carry distinct row hashes — train `e028347d…`, test `3e28943d…` ([[art:3b6b0a38:run.splits]]) — and the split sizes sum to exactly ⟦unverified: 5,000,⟧ which is the maximum observed `client_id` in the training profile ([[art:6a89f2be:run.data_train]]). A ⟦unverified: 3,500⟧/⟦unverified: 1,500⟧ disjoint partition of a ⟦unverified: 5,000⟧-client population is fully consistent with this arithmetic, and the near-identical event rates (⟦unverified: 0.224571⟧ train, ⟦unverified: 0.224667⟧ test) are consistent with a stratified or a large random split. We found no indication of train/test contamination. We record, however, that no row-level identifier intersection was computed, so the conclusion rests on arithmetic consistency rather than on a direct overlap test. `client_id` is present in the raw data but is correctly absent from the twelve declared features ([[art:abbb748e:run.features]]), so the identifier is not acting as a predictor.

**Distributional observations.** Three items in the training profile warrant documentation ([[art:6a89f2be:run.data_train]]):

- `pay_ratio_last` has a maximum of exactly ⟦unverified: 2.0⟧, against a maximum of ⟦unverified: 1.638541⟧ for its six-month mean. A round-number ceiling of this kind is a capping or winsorisation rule, and no such transformation is documented in the model summary or the feature inventory. Undocumented censoring of a predictor that also carries a wrong sign is worth resolving jointly with section 2.
- `utilisation` reaches ⟦unverified: 1.129703⟧, i.e. over-limit accounts are present in the sample. This is realistic for revolving credit but should be stated explicitly, since it affects how the feature is interpreted at the top of its range.
- `bill_trend_6m` has a standard deviation of ⟦unverified: 3,118.55⟧ against a range of ⟦unverified: -67,201.41⟧ to ⟦unverified: 27,397.95⟧ — roughly twenty-two standard deviations at the lower tail. The feature is severely heavy-tailed and asymmetric. Standardisation rescales but does not tame this; a small number of clients exert leverage on the ⟦unverified: -0.222475⟧ coefficient out of proportion to their number. `bill_mean_6m` is similarly skewed (mean ⟦unverified: 47,885.13⟧, standard deviation ⟦unverified: 44,974.79⟧, maximum ⟦unverified: 506,280.67⟧).

**Drift.** No population stability index, characteristic analysis, or score-distribution comparison exists anywhere in the store. The only drift-adjacent evidence available is that the two splits have near-identical event rates and that mean predicted score moves only from ⟦unverified: 0.224623⟧ to ⟦unverified: 0.221105⟧ between them ([[art:aebcad6a:run.metrics]]) — which tells us the random partition is stable and tells us nothing about stability over time, since both splits are drawn from the same period. Drift is therefore unassessed, not assessed-and-clean. See finding S1.

## 4. Outcomes analysis

**Discrimination.** Performance is consistent across the two splits ([[art:aebcad6a:run.metrics]]):

| Metric | Train (n=⟦unverified: 3,500⟧) | Test (n=⟦unverified: 1,500⟧) | Gap |
|---|---|---|---|
| AUC | ⟦unverified: 0.758436⟧ | ⟦unverified: 0.747989⟧ | ⟦unverified: 0.010447⟧ |
| Gini | ⟦unverified: 0.516871⟧ | ⟦unverified: 0.495978⟧ | ⟦unverified: 0.020893⟧ |
| KS | ⟦unverified: 0.445140⟧ | ⟦unverified: 0.418268⟧ | ⟦unverified: 0.026872⟧ |
| Log loss | ⟦unverified: 0.465001⟧ | ⟦unverified: 0.467291⟧ | ⟦unverified: 0.002290⟧ |
| Brier | ⟦unverified: 0.148915⟧ | ⟦unverified: 0.148851⟧ | ⟦unverified: -0.000064⟧ |
| Mean predicted | ⟦unverified: 0.224623⟧ | ⟦unverified: 0.221105⟧ | ⟦unverified: 0.003518⟧ |
| Observed rate | ⟦unverified: 0.224571⟧ | ⟦unverified: 0.224667⟧ | — |

The train-to-test AUC gap is ⟦unverified: 0.010447⟧, about ⟦unverified: 1.4%⟧ in relative terms. For a ten-parameter linear model on ⟦unverified: 3,500⟧ observations — roughly ⟦unverified: 79⟧ events per parameter — this is well inside what sampling variation alone explains, and it is materially below any conventional degradation threshold. There is no evidence of overfitting. Indeed the test Brier score is fractionally *better* than the train Brier score, which is unremarkable at these sample sizes but confirms the absence of memorisation. Discrimination of KS ⟦unverified: 0.418⟧ / Gini ⟦unverified: 0.496⟧ is respectable for a behavioural default scorecard.

**Calibration.** In aggregate, the model is well calibrated. On train the mean prediction of ⟦unverified: 0.224623⟧ sits essentially on the observed ⟦unverified: 0.224571⟧, as maximum-likelihood logistic regression with an intercept guarantees. On test the mean prediction of ⟦unverified: 0.221105⟧ sits ⟦unverified: 0.003562⟧ below the observed ⟦unverified: 0.224667⟧, a relative shortfall of ⟦unverified: 1.59%⟧ — a mild under-prediction of aggregate risk, but far inside any reasonable tolerance band and consistent with ordinary sampling noise on ⟦unverified: 1,500⟧ rows and ⟦unverified: 337⟧ events.

Aggregate calibration is, however, the *only* calibration evidence available. No calibration slope or intercept was fitted, no decile or bucketed observed-versus-expected table was produced, and no reliability curve exists in the store. A model can match on the mean while being badly miscalibrated in the tails, and for credit decisioning the tails are where the model is used. The prediction tables ([[art:66bafeec:run.predictions_test]], [[art:6fd8f98a:run.predictions_train]]) contain the raw material for this test; it simply was not run. See finding C1.

**Regime and segment stability.** No segmentation of outcomes was performed — not by vintage, not by limit band, not by utilisation band, not by delinquency status. The train/test split appears to be a random partition of a single population rather than an out-of-time division ([[art:3b6b0a38:run.splits]]), so even the two splits available cannot stand in for a regime comparison. Whether the dominant `delinq_last` effect or any other coefficient is stable across economic regimes or across the book is untested. See finding R1.

**Effective challenge.** No challenger, benchmark, or baseline model appears in the store. The only fitted object is the champion ([[art:74c10f15:run.model_summary]]) and the only metrics are its own ([[art:aebcad6a:run.metrics]]). We cannot therefore assert that a simpler model (for example, `delinq_last` and `utilisation` alone) fails to match ⟦unverified: 0.747989⟧ AUC — a relevant question given that `delinq_last` carries an odds ratio of ⟦unverified: 2.08⟧ per standard deviation and four of the remaining nine coefficients are wrong-signed. See finding E1.

## 5. Sensitivity and scenario analysis

**No sensitivity or scenario artifacts were produced.** The store contains no perturbation analysis, no univariate value curves, no stress scenarios, no reject-inference or downturn overlay, and no assessment of the score's response to shifts in any input distribution. This section therefore reports what can be inferred analytically from the fitted coefficients, and nothing more.

Because the model is a standardised logistic regression, each feature's implied response curve is fully determined by its coefficient: the log-odds move by the coefficient for every one-standard-deviation move in the feature, monotonically and without interaction. Sensitivity ranking per standard deviation is therefore read directly from [[art:74c10f15:run.model_summary#coefficients]]:

1. `delinq_last` +⟦unverified: 0.733422⟧ (odds ratio ⟦unverified: 2.082⟧ per SD) — dominant
2. `bill_mean_6m` ⟦unverified: -0.372628⟧
3. `pay_ratio_mean_6m` ⟦unverified: -0.355372⟧
4. `utilisation` +⟦unverified: 0.266208⟧
5. `bill_trend_6m` ⟦unverified: -0.222475⟧

The remaining five features each move the log-odds by less than ⟦unverified: 0.13⟧ per standard deviation and contribute marginally.

The analytic scenario review is what surfaces the substantive problem. Four of the ten implied value curves run in the wrong direction (section 2): increasing the worst delinquency observed in six months *lowers* predicted default probability; increasing the most recent payment ratio *raises* it, while increasing the six-month mean of the same ratio lowers it; and granting a larger credit limit *raises* predicted risk. Each of these, presented as a scenario to a credit officer, would be rejected as economically wrong. Because the features are standardised, the magnitudes are directly comparable and the wrong-signed effects are not negligible: `bill_mean_6m` at ⟦unverified: -0.372628⟧ is the second-strongest driver in the entire model.

The practical consequence is that the score is not safe to use for any counterfactual or what-if purpose — limit-setting, affordability simulation, or customer-level explanation — even though it discriminates acceptably in rank-ordering terms. A model whose partial effects point the wrong way can rank correctly in aggregate while giving indefensible answers to individual questions. See finding X1.

Stress on the heavy tail of `bill_trend_6m` and `bill_mean_6m` (section 3) is likewise untested; given the leverage those distributions imply, the stability of their two large negative coefficients under resampling is an open question that a bootstrap would settle cheaply.

## 6. Findings and recommendations

Findings are listed in severity order. Two are medium and require remediation before the model is fit for the counterfactual uses described in section 5; four are low and are documentation or evidence gaps; two are informational.

**M1 (medium) — Residual multicollinearity after incomplete treatment.** The developer removed `bill_last` (VIF ⟦unverified: 160.888514⟧) and `utilisation_mean_6m` (VIF ⟦unverified: 36.356335⟧) against a declared threshold of ⟦unverified: 10.0⟧ ([[art:74c10f15:run.model_summary#removed]]). A VIF of ⟦unverified: 161⟧ indicates an extremely tight collinear block, and removing its two most extreme members does not dissolve it. No post-removal VIF recomputation and no design-matrix condition number appear anywhere in the store, so compliance with the developer's own ⟦unverified: 10.0⟧ threshold after the drops is asserted rather than demonstrated. The sign pathology documented in section 2 — `delinq_max_6m` negative inside an otherwise positive delinquency block, `pay_ratio_last` and `pay_ratio_mean_6m` in opposition, `bill_mean_6m` and `bill_trend_6m` both strongly negative after their collinear partner `bill_last` was dropped — is the expected behavioural fingerprint of exactly this residual condition. *Recommendation:* recompute VIFs and the condition number on the final ten-feature design; if any exceed the declared threshold, consolidate the delinquency, payment-ratio and billing blocks into one representative or one composite each, or fit with a ridge penalty, and re-verify the signs.

**X1 (medium) — Wrong-signed implied value curves.** Four of ten partial-effect curves run against credit logic: `delinq_max_6m` ⟦unverified: -0.032214⟧, `pay_ratio_last` +⟦unverified: 0.102591⟧, `limit_bal` +⟦unverified: 0.072656⟧, and `bill_mean_6m` ⟦unverified: -0.372628⟧ ([[art:74c10f15:run.model_summary#coefficients]]). Under standardisation these are directly comparable effects and one of them is the second-largest in the model. The model must not be used for counterfactual, limit-setting, or customer-explanation purposes until the signs are defensible. *Recommendation:* impose sign constraints or reduce the feature set per M1, and require every retained coefficient to carry a documented economic rationale before approval.

**C1 (low) — Calibration evidenced only at the mean.** Aggregate calibration is good (test mean predicted ⟦unverified: 0.221105⟧ versus observed ⟦unverified: 0.224667⟧, a ⟦unverified: 1.59%⟧ relative under-prediction; train essentially exact) ([[art:aebcad6a:run.metrics]]). But no calibration slope, no decile observed-versus-expected table, and no reliability curve were produced, so tail calibration — the region that drives credit decisions — is untested. *Recommendation:* fit a calibration slope and intercept on the test predictions and publish a decile observed-versus-expected table from [[art:66bafeec:run.predictions_test]].

**S1 (low) — Drift unassessed.** No PSI or characteristic-stability computation exists, and both splits are drawn from the same period, so no time-dimension stability evidence is available at all ([[art:3b6b0a38:run.splits]], [[art:aebcad6a:run.metrics]]). *Recommendation:* construct an out-of-time holdout and compute feature-level and score-level PSI against the development sample before deployment.

**D1 (low) — Test-split profile absent; undocumented capping in the training data.** No data profile was supplied for the test split ([[art:26fbbf1d:run.data_test]]), so the cross-split missingness and distribution comparison could not be performed; the training split is fully complete ([[art:6a89f2be:run.data_train]]). Separately, `pay_ratio_last` has a maximum of exactly ⟦unverified: 2.0⟧ against ⟦unverified: 1.638541⟧ for its own six-month mean, indicating an undocumented cap, and `bill_trend_6m` is extremely heavy-tailed. *Recommendation:* publish the test-split profile, document the capping rule and its rationale, and assess the leverage of the billing-feature tails.

**E1 (low) — No effective challenge.** The store contains a single fitted model and no benchmark ([[art:74c10f15:run.model_summary]], [[art:aebcad6a:run.metrics]]). Given that `delinq_last` alone carries an odds ratio of ⟦unverified: 2.08⟧ per standard deviation while four other coefficients are wrong-signed, a two- or three-feature challenger may well match ⟦unverified: 0.747989⟧ test AUC with none of the sign problems. *Recommendation:* fit and document at least one parsimonious challenger and one non-linear benchmark.

**R1 (info) — Regime stability untested.** No segment or regime breakdown of performance or coefficients was produced, and the random train/test partition cannot substitute for one ([[art:3b6b0a38:run.splits]], [[art:abbb748e:run.features]]). No instability is alleged; none could be detected either. Recorded so that the gap is not mistaken for a clean result.

**O1 (info) — Out-of-sample degradation within tolerance.** The train-to-test AUC gap is ⟦unverified: 0.010447⟧ (⟦unverified: 0.758436⟧ to ⟦unverified: 0.747989⟧), with Gini and KS gaps of ⟦unverified: 0.020893⟧ and ⟦unverified: 0.026872⟧ and a test Brier fractionally better than train ([[art:aebcad6a:run.metrics]]). At roughly ⟦unverified: 79⟧ events per parameter this is consistent with sampling variation. No overfitting finding is raised; the observation is recorded as a positive control on the fitting process.

### F-001 · M1 collinearity · severity **medium**

The developer removed bill_last (VIF 160.888514) and utilisation_mean_6m (VIF 36.356335) against a declared vif_threshold of 10.0. A VIF of 161 indicates an extremely tight collinear block, and dropping its two most extreme members does not necessarily dissolve it. No post-removal VIF recomputation and no design-matrix condition number appear anywhere in the artifact store, so compliance with the developer's own 10.0 threshold on the final ten-feature design is asserted rather than demonstrated. The surviving coefficients show the classic behavioural fingerprint of residual collinearity: delinq_max_6m is negative (-0.032214) inside an otherwise positive delinquency block (delinq_last +0.733422, delinq_count_6m +0.122580); pay_ratio_last (+0.102591) and pay_ratio_mean_6m (-0.355372) measure the same construct at two horizons with opposite signs; and bill_mean_6m (-0.372628) and bill_trend_6m (-0.222475) are both strongly negative after their collinear partner bill_last was dropped. Because the features are standardised, these magnitudes are directly comparable and the affected effects are not negligible. Recommendation: recompute VIFs and the condition number on the final design; consolidate the delinquency, payment-ratio and billing blocks or apply a ridge penalty, and re-verify signs.

### F-002 · X1 scenario analysis · severity **medium**

No sensitivity or scenario artifacts were produced at all, so the implied value curves were reconstructed analytically from the standardised coefficients, which fully determine each feature's monotone response. Four of the ten run against credit logic: delinq_max_6m at -0.032214 means the worst delinquency observed in six months lowers predicted default probability; pay_ratio_last at +0.102591 means a higher recent payment ratio raises it, in direct opposition to its own six-month mean; limit_bal at +0.072656 means a larger granted limit raises predicted risk; and bill_mean_6m at -0.372628 is a large negative effect that is in fact the second-strongest driver in the whole model. Presented as scenarios to a credit officer, each of these would be rejected as economically wrong. The practical consequence is that the score may rank-order acceptably in aggregate (test AUC 0.747989) while giving indefensible answers to individual counterfactual questions, so it is not safe for limit-setting, affordability simulation, or customer-level reason codes as it stands. Recommendation: impose sign constraints or reduce the feature set per the multicollinearity finding, and require a documented economic rationale for every retained coefficient before approval.

### F-003 · C1 calibration · severity **low**

Aggregate calibration is good and raises no defect in itself: on test, mean predicted 0.221105 against an observed event rate of 0.224667, a 1.59% relative under-prediction well inside any reasonable tolerance on 1,500 rows and 337 events; on train, mean predicted 0.224623 against observed 0.224571, essentially exact as maximum-likelihood logistic regression with an intercept guarantees. However, the mean is the only calibration evidence in the store. No calibration slope or intercept was fitted, no bucketed observed-versus-expected table was produced, and no reliability curve exists. A model can match on the mean while being materially miscalibrated in the tails, and for credit decisioning the tails are where the model is actually used. The raw material is present in the scored prediction tables and the test simply was not run. Recommendation: fit a calibration slope and intercept on the test predictions and publish a decile observed-versus-expected table.

### F-004 · S1 population drift · severity **low**

No population stability index, characteristic analysis, or score-distribution comparison exists anywhere in the artifact store. The only drift-adjacent evidence available is that the two splits have near-identical event rates (0.224571 train, 0.224667 test) and that mean predicted score moves only from 0.224623 to 0.221105 between them. That demonstrates the random partition is internally stable and says nothing whatever about stability over time, because both splits are drawn from the same period and the split manifest shows no out-of-time division. Drift is therefore unassessed rather than assessed-and-clean, and this report should not be read as evidence of stability. Recommendation: construct an out-of-time holdout and compute feature-level and score-level PSI against the development sample before deployment, with conventional 0.10 amber and 0.25 red triggers thereafter.

### F-005 · D1 data integrity · severity **low**

The training split profile reports 0.0 missingness across all thirteen columns including the target, so completeness on the training data is not a concern. No equivalent profile was supplied for the test split, so the standard cross-split missingness and distribution comparison could not be performed, and no conclusion on differential missingness can be drawn in either direction. Separately, the training profile shows pay_ratio_last with a maximum of exactly 2.0 against a maximum of 1.638541 for its own six-month mean; a round-number ceiling of this kind is a capping or winsorisation rule, and no such transformation is documented in the model summary or the feature inventory. This matters more than it otherwise would because the same feature also carries a wrong sign. Finally, bill_trend_6m has a standard deviation of 3,118.55 against a range of -67,201.41 to 27,397.95 — roughly twenty-two standard deviations at the lower tail — and bill_mean_6m is similarly skewed (mean 47,885.13, maximum 506,280.67), so a small number of clients exert leverage on those two large negative coefficients out of proportion to their number. Recommendation: publish the test-split profile, document the capping rule, and bootstrap the billing coefficients to assess tail leverage.

### F-006 · E1 effective challenge · severity **low**

The artifact store contains a single fitted object — the champion logistic regression — and a single set of metrics, its own. No challenger, benchmark, or parsimonious baseline was fitted, so the claim that the ten-feature specification earns its complexity is untested. This is materially relevant here rather than a procedural box-tick: delinq_last alone carries a coefficient of 0.733422 on the standardised scale, an odds ratio of 2.08 per standard deviation and roughly double the next-largest effect, while four of the remaining nine coefficients are wrong-signed. A two- or three-feature challenger built on delinq_last and utilisation may well match the 0.747989 test AUC with none of the sign pathology, in which case the champion should be retired in its favour. No breach of an effective-challenge threshold is asserted, because no comparison was run. Recommendation: fit and document at least one parsimonious challenger and one non-linear benchmark, and record the comparison.

### F-007 · R1 regime stability · severity **info**

No segmentation of outcomes or coefficients was performed — not by vintage, limit band, utilisation band, or delinquency status — and no out-of-time sample exists. The train/test split appears from the manifest and the near-identical event rates to be a random partition of a single 5,000-client population rather than a time-based division, so even the two splits available cannot stand in for a regime comparison. Whether the dominant delinq_last effect or any other coefficient is stable across economic regimes or across the book is therefore unknown. No instability is alleged and none was detected, because the test was not executable on this evidence base. This is recorded at informational severity so that the absence of evidence is not later mistaken for evidence of stability; the remediation is folded into the out-of-time revalidation recommended under the drift finding.

### F-008 · O1 out-of-sample degradation · severity **info**

The train-to-test AUC gap is 0.010447 (0.758436 falling to 0.747989), about 1.4% in relative terms, with Gini falling 0.020893 (0.516871 to 0.495978) and KS falling 0.026872 (0.445140 to 0.418268). Log loss rises only 0.002290, and the test Brier score of 0.148851 is in fact fractionally better than the train Brier of 0.148915. For a ten-parameter linear model fitted on 3,500 observations — roughly 79 events per parameter at an event rate of 0.2246 — a gap of this size is comfortably explained by sampling variation alone and sits well below any conventional degradation threshold. No overfitting finding is raised and no remediation is attached. The observation is recorded as a positive control confirming that the fitting process did not memorise the training sample, which is relevant context for the medium findings above: the model's problems lie in its coefficient structure and its missing evidence, not in its generalisation.

Candidates raised and not promoted: none.

### Open items

No open item was recorded for this validation.

## 7. Ongoing monitoring recommendations

The monitoring plan below assumes the medium findings are remediated first; a model with wrong-signed partial effects should not enter production monitoring, it should re-enter development.

**Monthly.**
- Score-distribution PSI against the development sample ([[art:6a89f2be:run.data_train]]), with an amber trigger at ⟦unverified: 0.10⟧ and a red trigger at ⟦unverified: 0.25⟧, escalating to model review on a red.
- Mean predicted versus realised default rate on the scored population, benchmarked against the development relationship (test: ⟦unverified: 0.221105⟧ predicted, ⟦unverified: 0.224667⟧ observed) with a ⟦unverified: 10%⟧ relative tolerance band before investigation.
- Volume, override rate, and rejected/missing-input counts. Given the reported ⟦unverified: 0.0⟧ missingness at development ([[art:6a89f2be:run.data_train]]), any material production missingness is by itself an escalation.

**Quarterly.**
- Feature-level PSI on all ten retained predictors, with particular attention to `delinq_last` — a single feature carrying an odds ratio of ⟦unverified: 2.08⟧ per standard deviation makes the score fragile to any change in delinquency-flag definition, collections policy, or payment-holiday treatment upstream. A definitional change in that one field would invalidate the score outright.
- Discrimination on the accumulated outcome window: AUC, Gini and KS against the development baselines of ⟦unverified: 0.747989⟧ / ⟦unverified: 0.495978⟧ / ⟦unverified: 0.418268⟧ ([[art:aebcad6a:run.metrics#test]]). Trigger review on a sustained AUC drop below ⟦unverified: 0.70⟧.
- Decile observed-versus-expected calibration table, which closes finding C1 in production as well as in development.
- Tail monitoring on `bill_trend_6m` and `bill_mean_6m`, whose development distributions are severely skewed and whose coefficients are correspondingly leverage-sensitive.

**Annually, or on trigger.**
- Full refit with recomputed VIFs and condition number, with an explicit sign review of every coefficient against its documented economic rationale — the standing control for findings M1 and X1.
- Refresh of the challenger suite required by finding E1, with the champion retired if a challenger beats it materially.
- Out-of-time revalidation on the most recent complete window, which is the control that closes finding S1 and provides the first genuine regime comparison (finding R1).

**Standing conditions of use.** Until M1 and X1 are remediated, the score should be approved for rank-ordering and cut-off decisioning only, and explicitly not for limit-setting, affordability simulation, customer-level reason codes, or any what-if analysis, since four of its ten partial effects point the wrong way. Any upstream change to the delinquency, payment-ratio, or billing feature definitions should trigger immediate revalidation rather than waiting for the scheduled cycle.

## Appendix A — Claims

Grounding precision 0.0000 before repair (0 of 124 claims verified; 61 unsupported, 63 dangling) and 0.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 0/10; conceptual_soundness 0/16; data_integrity 0/19; outcomes 0/38; sensitivity 0/8; findings 0/22; monitoring 0/11.

Developer claims: `plain_llm` runs no check over `package.yaml`'s declared claims See Appendix D.

Excluded numeric tokens (not claims): section_number (section 6, section 2, 1., 2.); inline_code (`3e28943d…`); citation_hash (74c10f15, 3b6b0a38, aebcad6a, abbb748e); package_version (1.0); extractor_returned_excluded_token (1.0, 10.0, 12.0, 2.0).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | This report documents the independent validation of package… | -1.395828 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary]]` | dangling |  |
| 2 | summary | This report documents the independent validation of package… | 3500 | count | n_rows | train | eq | `[[art:3b6b0a38:run.splits]]` | dangling |  |
| 3 | summary | This report documents the independent validation of package… | 1500 | count | n_rows | test | eq | `[[art:3b6b0a38:run.splits]]` | dangling |  |
| 4 | summary | Headline discrimination is acceptable for a retail behaviour… | 0.747989 | ratio | auc | test | eq | `[[art:aebcad6a:run.metrics#test]]` | dangling |  |
| 5 | summary | Headline discrimination is acceptable for a retail behaviour… | 0.495978 | ratio | gini | test | eq | `[[art:aebcad6a:run.metrics#test]]` | dangling |  |
| 6 | summary | Headline discrimination is acceptable for a retail behaviour… | 0.418268 | ratio | ks | test | eq | `[[art:aebcad6a:run.metrics#test]]` | dangling |  |
| 7 | summary | Headline discrimination is acceptable for a retail behaviour… | 0.221105 | ratio | mean_predicted | test | eq | `[[art:aebcad6a:run.metrics#test]]` | dangling |  |
| 8 | summary | Headline discrimination is acceptable for a retail behaviour… | 0.224667 | ratio | event_rate | test | eq | `[[art:aebcad6a:run.metrics#test]]` | dangling |  |
| 9 | summary | The material weaknesses are not in headline performance. The… | 5 | ratio |  |  | eq |  | unsupported |  |
| 10 | summary | The material weaknesses are not in headline performance. The… | 7 | ratio |  |  | eq |  | unsupported |  |
| 11 | conceptual_soundness | **Model form.** Logistic regression on ten standardised pred… | 0.2246 | ratio | event_rate |  | eq | `[[art:3b6b0a38:run.splits]]` | dangling |  |
| 12 | conceptual_soundness | **Feature timing.** The inventory declares twelve features,… | 0.747989 | ratio | auc | test | eq | `[[art:aebcad6a:run.metrics#test]]` | dangling |  |
| 13 | conceptual_soundness | \| `delinq_last` \| +0.733422 \| + \| Correct, and correctly dom… | 0.733422 | ratio | coefficient |  | eq |  | unsupported |  |
| 14 | conceptual_soundness | \| `delinq_last` \| +0.733422 \| + \| Correct, and correctly dom… | 2.08 | ratio | odds_ratio |  | eq |  | unsupported |  |
| 15 | conceptual_soundness | \| `utilisation` \| +0.266208 \| + \| Correct \| | 0.266208 | ratio | coefficient |  | eq |  | unsupported |  |
| 16 | conceptual_soundness | \| `delinq_count_6m` \| +0.122580 \| + \| Correct \| | 0.12258 | ratio | coefficient |  | eq |  | unsupported |  |
| 17 | conceptual_soundness | \| `age` \| -0.067258 \| - \| Correct \| | -0.067258 | ratio | coefficient |  | eq |  | unsupported |  |
| 18 | conceptual_soundness | \| `pay_ratio_mean_6m` \| -0.355372 \| - \| Correct \| | -0.355372 | ratio | coefficient |  | eq |  | unsupported |  |
| 19 | conceptual_soundness | \| `delinq_max_6m` \| **-0.032214** \| + \| **Wrong sign** — wor… | -0.032214 | ratio | coefficient |  | eq |  | unsupported |  |
| 20 | conceptual_soundness | \| `pay_ratio_last` \| **+0.102591** \| - \| **Wrong sign**, and… | 0.102591 | ratio | coefficient |  | eq |  | unsupported |  |
| 21 | conceptual_soundness | \| `limit_bal` \| **+0.072656** \| - \| **Counterintuitive** — a… | 0.072656 | ratio | coefficient |  | eq |  | unsupported |  |
| 22 | conceptual_soundness | \| `bill_mean_6m` \| **-0.372628** \| ambiguous/+ \| Large negat… | -0.372628 | ratio | coefficient |  | eq |  | unsupported |  |
| 23 | conceptual_soundness | \| `bill_trend_6m` \| -0.222475 \| ambiguous \| Rising balances… | -0.222475 | ratio | coefficient |  | eq |  | unsupported |  |
| 24 | conceptual_soundness | The intercept of -1.395828 implies a probability of 0.1985 a… | -1.395828 | ratio | intercept |  | eq |  | unsupported |  |
| 25 | conceptual_soundness | The intercept of -1.395828 implies a probability of 0.1985 a… | 0.1985 | ratio | probability |  | eq |  | unsupported |  |
| 26 | conceptual_soundness | The intercept of -1.395828 implies a probability of 0.1985 a… | 0.224623 | ratio | mean_prediction |  | eq |  | unsupported |  |
| 27 | data_integrity | **Completeness.** The training profile reports 0.0 missingne… | 0 | ratio | missingness | train | eq | `[[art:6a89f2be:run.data_train]]` | dangling |  |
| 28 | data_integrity | **Split integrity.** The two splits carry distinct row hashe… | 5000 | count | client_id_max | train | eq | `[[art:6a89f2be:run.data_train]]` | dangling |  |
| 29 | data_integrity | **Split integrity.** The two splits carry distinct row hashe… | 3500 | count | n_rows | train | eq |  | unsupported |  |
| 30 | data_integrity | **Split integrity.** The two splits carry distinct row hashe… | 1500 | count | n_rows | test | eq |  | unsupported |  |
| 31 | data_integrity | **Split integrity.** The two splits carry distinct row hashe… | 5000 | count | n_rows |  | eq |  | unsupported |  |
| 32 | data_integrity | **Split integrity.** The two splits carry distinct row hashe… | 0.224571 | ratio | event_rate | train | eq |  | unsupported |  |
| 33 | data_integrity | **Split integrity.** The two splits carry distinct row hashe… | 0.224667 | ratio | event_rate | test | eq |  | unsupported |  |
| 34 | data_integrity | - `pay_ratio_last` has a maximum of exactly 2.0, against a m… | 2 | ratio | pay_ratio_last_max | train | eq |  | unsupported |  |
| 35 | data_integrity | - `pay_ratio_last` has a maximum of exactly 2.0, against a m… | 1.638541 | ratio | pay_ratio_mean_6m_max | train | eq |  | unsupported |  |
| 36 | data_integrity | - `utilisation` reaches 1.129703, i.e. over-limit accounts a… | 1.129703 | ratio | utilisation_max | train | eq |  | unsupported |  |
| 37 | data_integrity | - `bill_trend_6m` has a standard deviation of 3,118.55 again… | 3118.55 | currency | bill_trend_6m_std | train | eq |  | unsupported |  |
| 38 | data_integrity | - `bill_trend_6m` has a standard deviation of 3,118.55 again… | -67201.41 | currency | bill_trend_6m_min | train | eq |  | unsupported |  |
| 39 | data_integrity | - `bill_trend_6m` has a standard deviation of 3,118.55 again… | 27397.95 | currency | bill_trend_6m_max | train | eq |  | unsupported |  |
| 40 | data_integrity | - `bill_trend_6m` has a standard deviation of 3,118.55 again… | -0.222475 | ratio | coefficient |  | eq |  | unsupported |  |
| 41 | data_integrity | - `bill_trend_6m` has a standard deviation of 3,118.55 again… | 47885.13 | currency | bill_mean_6m_mean | train | eq |  | unsupported |  |
| 42 | data_integrity | - `bill_trend_6m` has a standard deviation of 3,118.55 again… | 44974.79 | currency | bill_mean_6m_std | train | eq |  | unsupported |  |
| 43 | data_integrity | - `bill_trend_6m` has a standard deviation of 3,118.55 again… | 506280.67 | currency | bill_mean_6m_max | train | eq |  | unsupported |  |
| 44 | data_integrity | **Drift.** No population stability index, characteristic ana… | 0.224623 | ratio | mean_predicted_score | train | eq | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 45 | data_integrity | **Drift.** No population stability index, characteristic ana… | 0.221105 | ratio | mean_predicted_score | test | eq | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 46 | outcomes | \| Metric \| Train (n=3,500) \| Test (n=1,500) \| Gap \| | 3500 | count |  | train | eq | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 47 | outcomes | \| Metric \| Train (n=3,500) \| Test (n=1,500) \| Gap \| | 1500 | count |  | test | eq | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 48 | outcomes | \| AUC \| 0.758436 \| 0.747989 \| 0.010447 \| | 0.758436 | ratio | auc | train | eq | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 49 | outcomes | \| AUC \| 0.758436 \| 0.747989 \| 0.010447 \| | 0.747989 | ratio | auc | test | eq | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 50 | outcomes | \| AUC \| 0.758436 \| 0.747989 \| 0.010447 \| | 0.010447 | ratio | delta_auc |  | eq | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 51 | outcomes | \| Gini \| 0.516871 \| 0.495978 \| 0.020893 \| | 0.516871 | ratio | gini | train | eq | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 52 | outcomes | \| Gini \| 0.516871 \| 0.495978 \| 0.020893 \| | 0.495978 | ratio | gini | test | eq | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 53 | outcomes | \| Gini \| 0.516871 \| 0.495978 \| 0.020893 \| | 0.020893 | ratio | delta_gini |  | eq | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 54 | outcomes | \| KS \| 0.445140 \| 0.418268 \| 0.026872 \| | 0.44514 | ratio | ks | train | eq | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 55 | outcomes | \| KS \| 0.445140 \| 0.418268 \| 0.026872 \| | 0.418268 | ratio | ks | test | eq | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 56 | outcomes | \| KS \| 0.445140 \| 0.418268 \| 0.026872 \| | 0.026872 | ratio | delta_ks |  | eq | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 57 | outcomes | \| Log loss \| 0.465001 \| 0.467291 \| 0.002290 \| | 0.465001 | ratio | log_loss | train | eq | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 58 | outcomes | \| Log loss \| 0.465001 \| 0.467291 \| 0.002290 \| | 0.467291 | ratio | log_loss | test | eq | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 59 | outcomes | \| Log loss \| 0.465001 \| 0.467291 \| 0.002290 \| | 0.00229 | ratio | delta_log_loss |  | eq | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 60 | outcomes | \| Brier \| 0.148915 \| 0.148851 \| -0.000064 \| | 0.148915 | ratio | brier | train | eq | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 61 | outcomes | \| Brier \| 0.148915 \| 0.148851 \| -0.000064 \| | 0.148851 | ratio | brier | test | eq | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 62 | outcomes | \| Brier \| 0.148915 \| 0.148851 \| -0.000064 \| | -6.4e-05 | ratio | delta_brier |  | eq | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 63 | outcomes | \| Mean predicted \| 0.224623 \| 0.221105 \| 0.003518 \| | 0.224623 | ratio | mean_predicted | train | eq | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 64 | outcomes | \| Mean predicted \| 0.224623 \| 0.221105 \| 0.003518 \| | 0.221105 | ratio | mean_predicted | test | eq | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 65 | outcomes | \| Mean predicted \| 0.224623 \| 0.221105 \| 0.003518 \| | 0.003518 | ratio | delta_mean_predicted |  | eq | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 66 | outcomes | \| Observed rate \| 0.224571 \| 0.224667 \| — \| | 0.224571 | ratio | event_rate | train | eq | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 67 | outcomes | \| Observed rate \| 0.224571 \| 0.224667 \| — \| | 0.224667 | ratio | event_rate | test | eq | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 68 | outcomes | The train-to-test AUC gap is 0.010447, about 1.4% in relativ… | 0.010447 | ratio | delta_auc |  | delta |  | unsupported |  |
| 69 | outcomes | The train-to-test AUC gap is 0.010447, about 1.4% in relativ… | 1.4 | percent | delta_auc |  | eq |  | unsupported |  |
| 70 | outcomes | The train-to-test AUC gap is 0.010447, about 1.4% in relativ… | 3500 | count |  | train | eq |  | unsupported |  |
| 71 | outcomes | The train-to-test AUC gap is 0.010447, about 1.4% in relativ… | 79 | ratio |  |  | eq |  | unsupported |  |
| 72 | outcomes | The train-to-test AUC gap is 0.010447, about 1.4% in relativ… | 0.418 | ratio | ks | test | eq |  | unsupported |  |
| 73 | outcomes | The train-to-test AUC gap is 0.010447, about 1.4% in relativ… | 0.496 | ratio | gini | test | eq |  | unsupported |  |
| 74 | outcomes | **Calibration.** In aggregate, the model is well calibrated.… | 0.224623 | ratio | mean_predicted | train | eq |  | unsupported |  |
| 75 | outcomes | **Calibration.** In aggregate, the model is well calibrated.… | 0.224571 | ratio | event_rate | train | eq |  | unsupported |  |
| 76 | outcomes | **Calibration.** In aggregate, the model is well calibrated.… | 0.221105 | ratio | mean_predicted | test | eq |  | unsupported |  |
| 77 | outcomes | **Calibration.** In aggregate, the model is well calibrated.… | 0.003562 | ratio | delta_mean_predicted | test | eq |  | unsupported |  |
| 78 | outcomes | **Calibration.** In aggregate, the model is well calibrated.… | 0.224667 | ratio | event_rate | test | eq |  | unsupported |  |
| 79 | outcomes | **Calibration.** In aggregate, the model is well calibrated.… | 1.59 | percent | delta_mean_predicted | test | eq |  | unsupported |  |
| 80 | outcomes | **Calibration.** In aggregate, the model is well calibrated.… | 1500 | count |  | test | eq |  | unsupported |  |
| 81 | outcomes | **Calibration.** In aggregate, the model is well calibrated.… | 337 | count | event_count | test | eq |  | unsupported |  |
| 82 | outcomes | **Effective challenge.** No challenger, benchmark, or baseli… | 0.747989 | ratio | auc | test | eq |  | unsupported |  |
| 83 | outcomes | **Effective challenge.** No challenger, benchmark, or baseli… | 2.08 | ratio | coefficient |  | eq |  | unsupported |  |
| 84 | sensitivity | 1. `delinq_last` +0.733422 (odds ratio 2.082 per SD) — domin… | 0.733422 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients]]` | dangling |  |
| 85 | sensitivity | 1. `delinq_last` +0.733422 (odds ratio 2.082 per SD) — domin… | 2.082 | ratio | odds_ratio |  | eq | `[[art:74c10f15:run.model_summary#coefficients]]` | dangling |  |
| 86 | sensitivity | 2. `bill_mean_6m` -0.372628 | -0.372628 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients]]` | dangling |  |
| 87 | sensitivity | 3. `pay_ratio_mean_6m` -0.355372 | -0.355372 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients]]` | dangling |  |
| 88 | sensitivity | 4. `utilisation` +0.266208 | 0.266208 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients]]` | dangling |  |
| 89 | sensitivity | 5. `bill_trend_6m` -0.222475 | -0.222475 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients]]` | dangling |  |
| 90 | sensitivity | The remaining five features each move the log-odds by less t… | 0.13 | ratio | coefficient |  | eq |  | unsupported |  |
| 91 | sensitivity | The analytic scenario review is what surfaces the substantiv… | -0.372628 | ratio | coefficient |  | eq |  | unsupported |  |
| 92 | findings | **M1 (medium) — Residual multicollinearity after incomplete… | 160.888514 | ratio | vif |  | eq | `[[art:74c10f15:run.model_summary#removed]]` | dangling |  |
| 93 | findings | **M1 (medium) — Residual multicollinearity after incomplete… | 36.356335 | ratio | vif |  | eq | `[[art:74c10f15:run.model_summary#removed]]` | dangling |  |
| 94 | findings | **M1 (medium) — Residual multicollinearity after incomplete… | 10 | ratio | vif |  | eq | `[[art:74c10f15:run.model_summary#removed]]` | dangling |  |
| 95 | findings | **M1 (medium) — Residual multicollinearity after incomplete… | 161 | ratio | vif |  | eq |  | unsupported |  |
| 96 | findings | **M1 (medium) — Residual multicollinearity after incomplete… | 10 | ratio | vif |  | eq |  | unsupported |  |
| 97 | findings | **X1 (medium) — Wrong-signed implied value curves.** Four of… | -0.032214 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients]]` | dangling |  |
| 98 | findings | **X1 (medium) — Wrong-signed implied value curves.** Four of… | 0.102591 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients]]` | dangling |  |
| 99 | findings | **X1 (medium) — Wrong-signed implied value curves.** Four of… | 0.072656 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients]]` | dangling |  |
| 100 | findings | **X1 (medium) — Wrong-signed implied value curves.** Four of… | -0.372628 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients]]` | dangling |  |
| 101 | findings | **C1 (low) — Calibration evidenced only at the mean.** Aggre… | 0.221105 | ratio | mean_predicted | test | eq | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 102 | findings | **C1 (low) — Calibration evidenced only at the mean.** Aggre… | 0.224667 | ratio | event_rate | test | eq | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 103 | findings | **C1 (low) — Calibration evidenced only at the mean.** Aggre… | 1.59 | percent | calibration | test | eq | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 104 | findings | **D1 (low) — Test-split profile absent; undocumented capping… | 2 | ratio | max | train | eq |  | unsupported |  |
| 105 | findings | **D1 (low) — Test-split profile absent; undocumented capping… | 1.638541 | ratio | mean | train | eq |  | unsupported |  |
| 106 | findings | **E1 (low) — No effective challenge.** The store contains a… | 2.08 | ratio | odds_ratio |  | eq |  | unsupported |  |
| 107 | findings | **E1 (low) — No effective challenge.** The store contains a… | 0.747989 | ratio | auc | test | eq |  | unsupported |  |
| 108 | findings | **O1 (info) — Out-of-sample degradation within tolerance.**… | 0.010447 | ratio | delta_auc |  | eq | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 109 | findings | **O1 (info) — Out-of-sample degradation within tolerance.**… | 0.758436 | ratio | auc | train | eq | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 110 | findings | **O1 (info) — Out-of-sample degradation within tolerance.**… | 0.747989 | ratio | auc | test | eq | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 111 | findings | **O1 (info) — Out-of-sample degradation within tolerance.**… | 0.020893 | ratio | delta_gini |  | eq | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 112 | findings | **O1 (info) — Out-of-sample degradation within tolerance.**… | 0.026872 | ratio | delta_ks |  | eq | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 113 | findings | **O1 (info) — Out-of-sample degradation within tolerance.**… | 79 | count | events_per_parameter |  | eq |  | unsupported |  |
| 114 | monitoring | - Score-distribution PSI against the development sample (),… | 0.1 | ratio | psi | train | eq | `[[art:6a89f2be:run.data_train]]` | dangling |  |
| 115 | monitoring | - Score-distribution PSI against the development sample (),… | 0.25 | ratio | psi | train | eq | `[[art:6a89f2be:run.data_train]]` | dangling |  |
| 116 | monitoring | - Mean predicted versus realised default rate on the scored… | 0.221105 | ratio | mean_predicted | test | eq |  | unsupported |  |
| 117 | monitoring | - Mean predicted versus realised default rate on the scored… | 0.224667 | ratio | event_rate | test | eq |  | unsupported |  |
| 118 | monitoring | - Mean predicted versus realised default rate on the scored… | 10 | percent |  |  | eq |  | unsupported |  |
| 119 | monitoring | - Volume, override rate, and rejected/missing-input counts.… | 0 | ratio | missingness | train | eq | `[[art:6a89f2be:run.data_train]]` | dangling |  |
| 120 | monitoring | - Feature-level PSI on all ten retained predictors, with par… | 2.08 | ratio | odds_ratio |  | eq |  | unsupported |  |
| 121 | monitoring | - Discrimination on the accumulated outcome window: AUC, Gin… | 0.747989 | ratio | auc | test | eq | `[[art:aebcad6a:run.metrics#test]]` | dangling |  |
| 122 | monitoring | - Discrimination on the accumulated outcome window: AUC, Gin… | 0.495978 | ratio | gini | test | eq | `[[art:aebcad6a:run.metrics#test]]` | dangling |  |
| 123 | monitoring | - Discrimination on the accumulated outcome window: AUC, Gin… | 0.418268 | ratio | ks | test | eq | `[[art:aebcad6a:run.metrics#test]]` | dangling |  |
| 124 | monitoring | - Discrimination on the accumulated outcome window: AUC, Gin… | 0.7 | ratio | auc |  | eq |  | unsupported |  |

## Appendix B — Artifact index

The store holds 14 artifacts; the 13 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `run.data_test` | `26fbbf1d` | table | table, 1500 rows | the subject's data_test.csv |
| `run.data_train` | `6a89f2be` | table | table, 3500 rows | the subject's data_train.csv |
| `run.duration_s` | `2c131563` | scalar | 1.372255167 | subject wall-clock seconds |
| `run.features` | `abbb748e` | json | json | the subject's features.json |
| `run.metrics` | `aebcad6a` | json | json | the subject's metrics.json |
| `run.model_summary` | `74c10f15` | json | json | the subject's model_summary.json |
| `run.predictions_test` | `66bafeec` | table | table, 1500 rows | the subject's predictions_test.csv |
| `run.predictions_train` | `6fd8f98a` | table | table, 3500 rows | the subject's predictions_train.csv |
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
| tokens in / out | 61,415 / 43,561 |
| notional cost (USD) | 1.6888 |
| wall-clock (s) | 515.16 |
| subject run (s) | 1.37 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | credit_default-plain_llm-20260918T190251Z-6e98ce62 |

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
