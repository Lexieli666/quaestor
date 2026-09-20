---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: plain_llm
model: claude-opus-5[1m]
run_id: credit_default-plain_llm-20260918T181914Z-6e98ce62
data_mode: synthetic
synthetic_n: 5000
grounding_precision_pre: 0.0000
grounding_precision_post: 0.0000
n_claims: 92
n_findings_by_severity: {high: 0, medium: 4, low: 3, info: 2}
generated: "2026-09-18T18:19:14Z"
illustrative: false
---

# Validation report — `credit_default` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `credit_default` v1.0 | `plain_llm` | claude-opus-5[1m] | synthetic, n = 5000 | 0.0000 → 0.0000 | 0 / 4 / 3 / 2 |
<!-- quaestor:renderer:end -->

This report documents an independent validation of package `credit_default` version 1.0, a binary classification model that predicts `default_next_month` for revolving credit clients. The subject is a standardised logistic regression with ten retained predictors and an intercept of ⟦unverified: -1.3968⟧ [[art:259cdde6:run.model_summary]]. Development used ⟦unverified: 3,545⟧ rows and evaluation used a ⟦unverified: 1,500⟧-row held-out split [[art:c005db79:run.splits]].

The validation was performed entirely against the artifacts the developer deposited in the store: the metrics block [[art:4cb18aab:run.metrics]], the model summary [[art:259cdde6:run.model_summary]], the feature inventory and timing declarations [[art:abbb748e:run.features]], the split manifest [[art:c005db79:run.splits]], the scored tables [[art:b0650ce2:run.predictions_test]] and [[art:9df50bd0:run.predictions_train]], the underlying split tables [[art:1b015759:run.data_train]] and [[art:26fbbf1d:run.data_test]], and the raw training profile [[art:3e5e172d:plain_llm.profile]]. Run control artifacts [[art:2922931d:run.status]], [[art:719a149c:run.duration_s]] and [[art:2ad8d1a5:runtime.max_seconds]] were reviewed for evidence of execution failure or cap breach; none was found, and no R0 condition is raised.

Headline discrimination is AUC ⟦unverified: 0.7480⟧ on test and ⟦unverified: 0.7589⟧ on train, equivalent to Gini ⟦unverified: 0.4961⟧ and ⟦unverified: 0.5177⟧ and KS ⟦unverified: 0.4190⟧ and ⟦unverified: 0.4447⟧ [[art:4cb18aab:run.metrics]]. The reported Gini values reconcile exactly with ⟦unverified: 2⟧·AUC−⟦unverified: 1⟧ on both splits, and the train event rate in the metrics block, the split manifest and the raw profile all agree at ⟦unverified: 0.22454⟧ [[art:4cb18aab:run.metrics]] [[art:c005db79:run.splits]] [[art:3e5e172d:plain_llm.profile]]. The internal arithmetic of the submission is therefore consistent.

The model's discriminatory power is modest but defensible for a ten-variable behavioural scorecard, and its aggregate calibration is tight. The material weaknesses are not in the headline numbers: they are in the coefficient structure, which carries several economically wrong signs that survive the developer's own collinearity pruning, and in the substantial body of validation evidence that was never produced at all — no out-of-time sample, no drift measurement, no challenger, no calibration slope, and no scenario analysis. The model is usable subject to remediation of the sign-instability issue and the addition of the missing evidence; it should not be promoted to unsupervised production use until an out-of-time result and a challenger comparison exist.

## 2. Conceptual soundness

The choice of a standardised logistic regression for a binary default outcome is appropriate and conventional. Standardisation is declared (`standardised: true`), which makes the coefficient magnitudes directly comparable as effect sizes [[art:259cdde6:run.model_summary]]. `class_weight` is null, which is acceptable at a ⟦unverified: 22.5%⟧ event rate — the class imbalance is mild enough that unweighted fitting will not materially distort the likelihood, and the observed calibration confirms this.

The feature inventory is the strongest part of the submission. Twelve candidate features are declared, of which two are `at_origination` and ten are `before_period_start`; zero are `during_period` and zero are `after_outcome` [[art:abbb748e:run.features]]. The counts reconcile with the twelve listed items. On the developer's own declarations there is no target leakage by construction: every predictor is observable strictly before the performance window opens. This is corroborated by the modest headline AUC of ⟦unverified: 0.7480⟧ [[art:4cb18aab:run.metrics]] — a leaked feature of the kind that triggers an L1 condition would drive discrimination far above the observed level, and no single-feature AUC anywhere near ⟦unverified: 0.90⟧ is compatible with a full-model AUC of ⟦unverified: 0.748⟧. No L1 defect is raised. It should be noted, however, that the timing labels are developer assertions; validation could not independently re-derive the observation dates, because no date or vintage column appears anywhere in the profile [[art:3e5e172d:plain_llm.profile]].

The fitted coefficient structure is where conceptual soundness weakens. Reading [[art:259cdde6:run.model_summary]], the dominant driver is `delinq_last` at +⟦unverified: 0.7279⟧, roughly ⟦unverified: 2.7⟧ times the next largest term and entirely plausible: the most recent delinquency bucket should be the single best behavioural predictor. `utilisation` at +⟦unverified: 0.2700⟧ is correctly signed. But three signs are hard to defend:

- `delinq_max_6m` carries **⟦unverified: -0.0305⟧**, implying that a worse maximum delinquency over six months *reduces* default risk, holding the last and the count constant. This is economically wrong.
- `pay_ratio_mean_6m` carries **⟦unverified: -0.3768⟧** while `pay_ratio_last` carries **+⟦unverified: 0.1180⟧**. The two measure the same behaviour over different windows and flip sign against each other; on any credit-risk reading, a higher payment ratio should reduce risk, so the larger, better-determined six-month term has the defensible sign and the recent term does not.
- `limit_bal` carries **+⟦unverified: 0.0742⟧**, implying that a larger granted credit line increases default probability. Underwriting assigns larger limits to better-assessed clients, so the expected sign is negative. The magnitude is small, but the sign is counterintuitive and is not explained.
- `bill_mean_6m` at ⟦unverified: -0.3703⟧ and `bill_trend_6m` at ⟦unverified: -0.2243⟧ are both large and negative, meaning higher and rising balances reduce risk. These are defensible only under a specific "active, transacting account" story, which the developer has not documented.

The developer did address collinearity: `bill_last` (VIF ⟦unverified: 161.13⟧) and `utilisation_mean_6m` (VIF ⟦unverified: 36.45⟧) were removed against a declared threshold of ⟦unverified: 10.0⟧ [[art:259cdde6:run.model_summary]]. That was the right action. The problem is that the pruning stopped there and no post-removal VIF table or condition number was deposited, so there is no evidence that the surviving ten features clear the declared threshold. The sign pattern above — same-family features with opposing signs, and a near-zero wrong-signed term inside a three-variable delinquency block — is the classic fingerprint of residual multicollinearity, and it is what drives findings M1 and T1 below. `age` at ⟦unverified: -0.0693⟧ (younger clients riskier) and `delinq_count_6m` at +⟦unverified: 0.1244⟧ are both correctly signed and unremarkable.

## 3. Data integrity and drift

The raw training profile shows ⟦unverified: 3,545⟧ rows with **zero missing values in every one of the thirteen columns**, including the behavioural aggregates [[art:3e5e172d:plain_llm.profile]]. Complete data across a six-month behavioural panel is not what a real servicing extract looks like; it points to upstream imputation, dropping of incomplete accounts, or a filtered population. None of these is documented. If incomplete accounts were dropped, the development sample is not representative of the scoring population and the model will be applied to a population it never saw.

Two distributional artefacts warrant attention. First, `pay_ratio_last` has a maximum of **exactly ⟦unverified: 2.0⟧** while its sibling `pay_ratio_mean_6m` reaches only ⟦unverified: 1.6385⟧ [[art:3e5e172d:plain_llm.profile]]. An exact round maximum on one variable and not the other is the signature of an undocumented cap or winsorisation applied to a single feature. This matters directly: the capped feature is one half of the sign-flipped payment-ratio pair discussed in section 2, and a truncated right tail is a sufficient mechanism to destabilise its coefficient. Second, `utilisation` reaches ⟦unverified: 1.1298⟧, i.e. over-limit accounts are present and uncapped. That is economically real and not a defect, but it is inconsistent treatment relative to the capped payment ratio. `bill_trend_6m` is heavily left-skewed (mean ⟦unverified: -234.9⟧, min ⟦unverified: -67,201,⟧ max +⟦unverified: 27,398,⟧ sd ⟦unverified: 3,119⟧), which is plausible for a balance-trend variable but means the term is dominated by a small number of large paydowns.

On split integrity: train n=⟦unverified: 3,545⟧ and test n=⟦unverified: 1,500⟧ sum to ⟦unverified: 5,045,⟧ which is exactly the maximum observed `client_id` against a minimum of ⟦unverified: 1⟧ [[art:3e5e172d:plain_llm.profile]] [[art:c005db79:run.splits]]. The row hashes differ (`26a3b938…` for train, `3e28943d…` for test). The row counts are therefore consistent with a clean disjoint partition of ⟦unverified: 5,045⟧ distinct clients, and no evidence of contamination was found. This is recorded as an informational L2 observation rather than a defect, because differing row hashes demonstrate that the two sets are not identical but do not by themselves prove disjointness at client level; a client-level intersection count was not deposited.

No profile of the **test** split was deposited. Missingness, distributions and caps could therefore be compared across splits only in one direction, and the D1 test proper — whether missingness differs materially between splits — could not be executed. This is the basis of the D1 finding below.

On drift: **no drift evidence exists in the store**. There is no PSI calculation for either the population or the score, no out-of-time sample, and no date column from which one could be constructed [[art:3e5e172d:plain_llm.profile]]. The split is evidently random rather than temporal: train and test event rates are ⟦unverified: 0.224542⟧ and ⟦unverified: 0.224667⟧ [[art:c005db79:run.splits]], a difference of ⟦unverified: 0.0001⟧ that no genuine out-of-time sample of a credit portfolio would produce. A random split measures variance, not stability. The entire question of whether this model survives a change in economic regime, a change in underwriting policy, or a change in portfolio mix is unaddressed. This is finding S1.

## 4. Outcomes analysis

Discrimination is stable between development and holdout. Test AUC is ⟦unverified: 0.7480⟧ against train AUC ⟦unverified: 0.7589⟧, a gap of **⟦unverified: 0.0109⟧** [[art:4cb18aab:run.metrics]]. For a ten-parameter linear model fitted on ⟦unverified: 3,545⟧ rows this is well within sampling noise and indicates no meaningful overfitting; the model has not memorised its development sample. KS moves from ⟦unverified: 0.4447⟧ to ⟦unverified: 0.4190⟧ and Gini from ⟦unverified: 0.5177⟧ to ⟦unverified: 0.4961⟧, both consistent with the AUC gap. No O1 defect is raised; the result is recorded as an informational finding because the absence of degradation is itself a validation conclusion worth stating.

Log loss is ⟦unverified: 0.4650⟧ on train and ⟦unverified: 0.4674⟧ on test, and the Brier score is ⟦unverified: 0.14904⟧ on train against ⟦unverified: 0.14895⟧ on test — marginally *better* out of sample, which again is consistent with noise rather than any structural difference [[art:4cb18aab:run.metrics]].

Aggregate calibration is good. On test, mean predicted probability is ⟦unverified: 0.22130⟧ against an observed event rate of ⟦unverified: 0.22467⟧ — an absolute gap of ⟦unverified: 0.0034⟧, or about ⟦unverified: 1.5%⟧ in relative terms, i.e. a very slight under-prediction of risk. On train the correspondence is near-exact (⟦unverified: 0.224615⟧ predicted against ⟦unverified: 0.224542⟧ observed), as expected from a logistic fit with an intercept [[art:4cb18aab:run.metrics]]. No C1 breach on the mean-prediction test.

The limitation is that mean-level agreement is a weak calibration test. A model can match the portfolio average exactly while being badly miscalibrated in the tails — over-predicting in the top decile and under-predicting in the bottom, which is precisely where a credit decision gets made. **No calibration slope, no calibration intercept, and no decile or bucket calibration table were deposited**, although the scored tables [[art:b0650ce2:run.predictions_test]] and [[art:9df50bd0:run.predictions_train]] contain everything needed to produce them. The C1 condition — slope outside its band — could therefore not be evaluated. This is recorded as a low-severity C1 finding on evidential grounds, not because a miscalibration was demonstrated.

No challenger model of any kind appears in the store. There is one model summary [[art:259cdde6:run.model_summary]] and one metrics block [[art:4cb18aab:run.metrics]]. Effective challenge requires that the champion's performance be shown to be non-trivially better than a credible alternative — at minimum a penalised regression retaining the two VIF-dropped features, a gradient-boosted benchmark, and a single-variable `delinq_last` baseline. The last of these matters here: `delinq_last` carries a coefficient roughly ⟦unverified: 2.7⟧ times the next largest, so a substantial share of the AUC ⟦unverified: 0.748⟧ may be attributable to one variable, and without that benchmark the incremental value of the other nine features is unquantified. This is finding E1.

## 5. Sensitivity and scenario analysis

**No scenario, stress or sensitivity artifact was deposited.** There are no partial dependence curves, no value curves, no univariate response profiles, and no stressed-population reruns anywhere in the store. Sensitivity therefore had to be assessed analytically from the fitted coefficients [[art:259cdde6:run.model_summary]], which for a linear-in-logit model fully determine the response shape.

That analysis produces a genuine X1 condition. The three delinquency features jointly describe severity, and as fitted the model's response across them is **non-monotone**:

- `delinq_last` +⟦unverified: 0.7279⟧ (risk rises with recent delinquency — correct)
- `delinq_count_6m` +⟦unverified: 0.1244⟧ (risk rises with frequency — correct)
- `delinq_max_6m` **⟦unverified: -0.0305⟧** (risk *falls* as the worst delinquency in the window deepens — wrong-signed)

Because `delinq_max_6m` ranges ⟦unverified: 0⟧ to ⟦unverified: 8⟧ with a mean of ⟦unverified: 2.09⟧ [[art:3e5e172d:plain_llm.profile]], the wrong-signed term is applied across a wide range and partially offsets the correctly signed frequency term. A client whose delinquency deepens over the window is credited with a risk reduction along that axis. The effect is small in magnitude, but the shape is indefensible: no scenario in which a portfolio's delinquency severity worsens should show a risk decrease from that channel, and any stress scenario built on this model will understate the deterioration.

The same problem appears in the payment-ratio pair, where `pay_ratio_mean_6m` (⟦unverified: -0.3768⟧) and `pay_ratio_last` (+⟦unverified: 0.1180⟧) respond in opposite directions to the same underlying behaviour, and in `limit_bal` (+⟦unverified: 0.0742⟧), where the scenario "grant a larger line" increases modelled default probability. Under a limit-increase strategy scenario — an obvious use of this model — that sign would generate the wrong recommendation.

Because the standardised coefficients determine the response directly, these are not hypotheses about what a scenario analysis might show; they are what the scenario analysis will show when it is run. The remediation is to constrain or re-specify the affected terms, not to document the curves.

## 6. Findings and recommendations

Nine findings are recorded: four of medium severity, three of low severity, and two informational. None is assessed as high, because discrimination is stable, aggregate calibration is tight, and no leakage or contamination was found.

**Medium.** M1 (residual multicollinearity evidenced by wrong and opposed coefficient signs surviving the VIF pruning), X1 (non-monotone delinquency response and wrong-signed limit response), S1 (no drift measurement and no out-of-time sample; the split is random), and E1 (no challenger, hence no effective challenge, with the `delinq_last` dominance making a single-variable baseline especially necessary).

**Low.** C1 (calibration evidenced only at the portfolio mean; no slope and no bucket table), D1 (no test-split profile, so the cross-split missingness comparison could not be run; universal zero missingness and an exact ⟦unverified: 2.0⟧ cap on `pay_ratio_last` are undocumented), and T1 (the declared VIF threshold of ⟦unverified: 10.0⟧ cannot be shown to hold for the retained ten features, because no post-removal VIF table was deposited).

**Informational.** O1 (train-to-test AUC gap of ⟦unverified: 0.0109⟧ — no degradation, recorded as a passed test) and L2 (row counts consistent with a disjoint partition of ⟦unverified: 5,045⟧ clients; no contamination found, though a client-level intersection was not deposited).

Recommended remediation, in priority order:

1. **Re-specify the collinear blocks.** Recompute VIFs and the condition number on the retained ten features and deposit the table. Collapse the delinquency block (`delinq_last`, `delinq_count_6m`, `delinq_max_6m`) and the payment-ratio pair into non-redundant constructions, or fit with sign constraints, until every retained coefficient carries an economically defensible sign. Re-examine `limit_bal` specifically.
2. **Build an out-of-time sample.** Restore a date or vintage field, hold out the most recent period, and report AUC, KS and calibration on it alongside PSI for both the population and the score distribution. The current random split cannot support a stability claim.
3. **Run effective challenge.** At minimum: a single-variable `delinq_last` baseline, a penalised regression retaining the VIF-dropped features, and a gradient-boosted benchmark. Report the AUC deltas.
4. **Deposit full calibration evidence.** Calibration slope and intercept with confidence intervals, plus a decile table of predicted against observed, on the test split.
5. **Document the data preparation.** Explain the zero missingness, the exact ⟦unverified: 2.0⟧ cap on `pay_ratio_last`, and the inconsistent treatment of over-limit `utilisation`. Deposit a test-split profile so cross-split integrity can be checked.
6. **Produce the sensitivity curves** once the signs are fixed, and confirm monotonicity across each risk-ordered feature family.

Until items ⟦unverified: 1⟧ through ⟦unverified: 3⟧ are complete, the model should be restricted to monitored use with human review of decisions near the cut-off, and should not be used to support limit-increase strategies given the `limit_bal` sign.

### F-001 · M1 collinearity · severity **medium**

The developer removed two features on VIF grounds — bill_last at VIF 161.13 and utilisation_mean_6m at VIF 36.45, against a declared threshold of 10.0 — but the retained ten-feature specification still carries the signature of collinearity. Within the three-variable delinquency block, delinq_last is +0.7279 and delinq_count_6m is +0.1244, both correct, while delinq_max_6m is -0.0305, implying that a deeper worst-case delinquency reduces default risk. In the payment-ratio pair, pay_ratio_mean_6m is -0.3768 while pay_ratio_last is +0.1180: two measures of the same behaviour over different windows entering with opposite signs. limit_bal is +0.0742, implying a larger granted credit line raises default probability, against the underwriting logic that better-assessed clients receive larger lines. Near-zero wrong-signed terms inside a correlated family, and same-family features flipping against each other, are the classic fingerprint of variance inflation that the pruning did not fully clear. No post-removal VIF table and no condition number were deposited, so the residual inflation could not be quantified directly; it is inferred from the sign structure. The consequence is that individual coefficients are not interpretable, the model cannot be defended to a credit committee on economic grounds, and the affected terms will be unstable under refit.

### F-002 · X1 scenario analysis · severity **medium**

No scenario, stress or sensitivity artifact exists in the store, so the response surface was derived analytically from the fitted coefficients, which for a linear-in-logit model fully determine it. The derived delinquency value curve is non-monotone: risk rises with delinq_last (+0.7279) and with delinq_count_6m (+0.1244) but falls with delinq_max_6m (-0.0305). Since delinq_max_6m ranges from 0 to 8 with a mean of 2.09, this wrong-signed term operates across a wide range and partially offsets the correctly signed frequency term, so a client whose delinquency deepens is credited with a risk reduction along that axis. Any stress scenario in which portfolio delinquency severity worsens will therefore understate the deterioration. The same defect appears in limit_bal (+0.0742): under a limit-increase scenario, which is an obvious intended use of a model of this type, the model recommends the wrong direction. The payment-ratio pair compounds the problem by responding in opposite directions to the same underlying behaviour. These are not hypotheses about what a scenario analysis might reveal; they are what it will reveal when run, and the remediation is re-specification with sign constraints rather than documentation of the curves.

### F-003 · S1 population drift · severity **medium**

No PSI calculation exists for either the population or the score distribution, and no out-of-time validation sample was deposited. The split appears to be random rather than temporal: train and test event rates are 0.224542 and 0.224667 respectively, a difference of roughly one part in ten thousand that no genuine out-of-time sample of a revolving credit portfolio would produce. A random split measures sampling variance, not stability, and provides no evidence that the model holds under a change of economic regime, underwriting policy or portfolio mix. The underlying obstacle is structural: no date or vintage column appears anywhere in the training profile, so an out-of-time split could not be constructed from the deposited data even retrospectively, and regime-segmented stability testing is equally foreclosed. For a behavioural credit-default model, whose predictors are six-month aggregates that are themselves sensitive to macroeconomic conditions, this is the single largest gap in the evidence base. Remediation requires restoring a date field, holding out the most recent period, and reporting discrimination, calibration and PSI on it.

### F-004 · E1 effective challenge · severity **medium**

The store contains exactly one model summary and one metrics block. No challenger of any kind was fitted, so there is no evidence that the champion's AUC of 0.7480 is non-trivially better than a credible alternative, and no basis for concluding that the chosen specification is the right one. This matters more than usual here because delinq_last carries a standardised coefficient of +0.7279, roughly 2.7 times the next largest term, which raises the concrete possibility that a substantial share of the model's discrimination comes from a single variable. Without a univariate delinq_last baseline, the incremental value of the other nine features — including the four with problematic signs — is entirely unquantified, and the case for a ten-variable specification over a much simpler one has not been made. The minimum remediation is a three-way comparison against a single-variable delinq_last baseline, a penalised regression that retains the two VIF-dropped features rather than discarding their information, and a gradient-boosted benchmark to bound the loss from the linear functional form, with AUC deltas reported on the same holdout.

### F-005 · C1 calibration · severity **low**

Aggregate calibration passes: test mean predicted probability is 0.22130 against an observed event rate of 0.22467, an absolute gap of 0.0034 or about 1.5% relative, a slight under-prediction of risk, and the train figures agree almost exactly at 0.224615 against 0.224542 as expected from a fitted intercept. Brier scores of 0.14895 on test and 0.14904 on train corroborate reasonable probabilistic accuracy. However, mean-level agreement is a weak test: a model can match the portfolio average exactly while over-predicting in the top decile and under-predicting in the bottom, which is precisely where a credit cut-off operates. No calibration slope, no calibration intercept and no decile or bucket calibration table were deposited, so the C1 condition proper — slope outside its band — could not be evaluated. This is recorded on evidential grounds rather than because miscalibration was demonstrated. The scored prediction tables for both splits are present and contain everything required, so the remediation is inexpensive: report slope and intercept with confidence intervals and a ten-bucket predicted-versus-observed table on the test split.

### F-006 · D1 data integrity · severity **low**

The D1 test proper — whether missingness differs materially between splits — could not be executed, because a profile was deposited for the training split only. What the training profile does show raises two concerns. First, all thirteen columns report exactly zero missing values across 3,545 rows, including the six-month behavioural aggregates. Complete data across a behavioural panel is not what a real servicing extract yields; it indicates undocumented upstream imputation, dropping of incomplete accounts, or a filtered population, any of which would make the development sample unrepresentative of the population the model is scored on. Second, pay_ratio_last has a maximum of exactly 2.0 while its sibling pay_ratio_mean_6m reaches only 1.6385, an exact round bound on one variable and not the other that is the signature of an undocumented cap or winsorisation. This is not cosmetic: the capped feature is one half of the sign-flipped payment-ratio pair, and a truncated right tail is a sufficient mechanism to destabilise its coefficient. By contrast utilisation is left uncapped at 1.1298, so over-limit accounts pass through unmodified — economically real, but inconsistent treatment relative to the payment ratio. Remediation is to deposit a test-split profile and document the missingness handling and the cap.

### F-007 · T1 declared threshold · severity **low**

The model summary declares a vif_threshold of 10.0 and documents two removals against it: bill_last at VIF 161.13 and utilisation_mean_6m at VIF 36.45. The removals were the correct action and the two reported figures are unambiguous breaches. What is missing is any evidence that the threshold is satisfied after the removals. No post-removal VIF table and no condition number were deposited for the ten retained features, so the developer's implicit claim that the final specification complies with its own declared threshold is unverifiable from the store. The claim is also affirmatively doubtful: the opposed signs within the delinquency block and the payment-ratio pair are consistent with at least one retained feature still exceeding a VIF of 10. Remediation is to recompute and deposit VIFs for all ten retained features together with the design-matrix condition number, and to continue pruning or re-specifying until the declared threshold actually holds.

### F-008 · O1 out-of-sample degradation · severity **info**

Recorded as a passed test rather than a defect. Test AUC is 0.7480 against train AUC 0.7589, a gap of 0.0109. Supporting metrics move consistently and by similarly small amounts: KS from 0.4447 to 0.4190, Gini from 0.5177 to 0.4961, log loss from 0.4650 to 0.4674, and the Brier score is marginally better out of sample at 0.14895 against 0.14904. For a ten-parameter linear model fitted on 3,545 rows, a gap of this size is well within sampling noise and indicates that the model has not memorised its development sample. The reported Gini values reconcile exactly with 2*AUC-1 on both splits, and the train event rate agrees across the metrics block, the split manifest and the raw profile at 0.22454, so the submission is internally consistent. No remediation is attached. The one qualification is that this result is a within-sample-period statement only: because the split is random rather than temporal, it bounds variance but says nothing about stability over time, which is addressed separately under S1.

### F-009 · L2 contamination · severity **info**

Recorded as a passed check. Train n=3,545 and test n=1,500 sum to exactly 5,045, which matches the maximum observed client_id against a minimum of 1 in the training profile, and the two split row hashes differ (26a3b938... for train, 3e28943d... for test). The counts are therefore consistent with a clean disjoint partition of 5,045 distinct clients with no duplication, and no evidence of contamination above any threshold was found. The modest AUC of 0.7480 and the small train-to-test gap independently corroborate this: material row overlap would inflate holdout performance toward the training figure, which is not observed. The check is recorded as informational rather than clean because differing row hashes establish only that the two sets are not identical, not that they are disjoint at client level; an explicit client-level intersection count was not deposited. Depositing one would close the point at negligible cost.

Candidates raised and not promoted: none.

### Open items

No open item was recorded for this validation.

## 7. Ongoing monitoring recommendations

Monitoring should be calibrated to the specific weaknesses identified above rather than to a generic template.

*Monthly.* Score distribution PSI against the development baseline, with an amber threshold of ⟦unverified: 0.10⟧ and a red threshold of ⟦unverified: 0.25⟧. Feature-level PSI on the ten retained predictors, with particular attention to `delinq_last`, whose coefficient of +⟦unverified: 0.7279⟧ makes the model's output disproportionately sensitive to any shift or definitional change in that field [[art:259cdde6:run.model_summary]]. Mean predicted probability against the development benchmark of ⟦unverified: 0.2213⟧ on test, alerting on a sustained deviation beyond ±⟦unverified: 10%⟧ relative [[art:4cb18aab:run.metrics]]. Volume of scored records hitting the `pay_ratio_last` cap of ⟦unverified: 2.0⟧ and the share of `utilisation` values above 1.0, since both are undocumented boundary behaviours [[art:3e5e172d:plain_llm.profile]]. Missingness rates by feature, which must remain at the zero observed in development or else the production population differs from the development population [[art:3e5e172d:plain_llm.profile]].

*Quarterly, once outcomes mature.* Realised AUC, KS and Gini on the newest complete performance window, with an amber trigger at AUC below ⟦unverified: 0.70⟧ and a red trigger below ⟦unverified: 0.65⟧ against the ⟦unverified: 0.7480⟧ test baseline. Calibration slope and intercept plus a decile table of predicted against observed — this is the control that substitutes for the calibration evidence missing from the current submission. Observed default rate against the ⟦unverified: 0.2247⟧ development rate.

*Annually, or on trigger.* Full refit with recomputed VIFs and condition number, verifying that every coefficient retains a defensible sign — the delinquency and payment-ratio blocks are the specific terms to watch, since instability there has already been demonstrated. Re-run of the challenger suite. Review of the observation-window and cap definitions.

*Triggers for out-of-cycle revalidation.* Any red PSI breach; two consecutive amber breaches; any change to underwriting or limit-assignment policy, which bears directly on the anomalous `limit_bal` sign; any change to the delinquency bucketing definitions; and any material shift in portfolio mix or macroeconomic regime, which the current evidence base — having no out-of-time sample at all — gives no basis for assessing.

## Appendix A — Claims

Grounding precision 0.0000 before repair (0 of 92 claims verified; 47 unsupported, 45 dangling) and 0.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 0/12; conceptual_soundness 0/18; data_integrity 0/16; outcomes 0/20; sensitivity 0/9; findings 0/7; monitoring 0/10.

Developer claims: `plain_llm` runs no check over `package.yaml`'s declared claims See Appendix D.

Excluded numeric tokens (not claims): section_number (section 2, 1., 2., 3.); inline_code (`26a3b938…`, `3e28943d…`); citation_hash (259cdde6, c005db79, 4cb18aab, abbb748e); package_version (1.0); extractor_returned_excluded_token (1.0, 0.0, 13.0, 6.0).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | This report documents an independent validation of package `… | -1.3968 | ratio | coefficient |  | eq | `[[art:259cdde6:run.model_summary]]` | dangling |  |
| 2 | summary | This report documents an independent validation of package `… | 3545 | count | n_rows | train | eq | `[[art:c005db79:run.splits]]` | dangling |  |
| 3 | summary | This report documents an independent validation of package `… | 1500 | count | n_rows | test | eq | `[[art:c005db79:run.splits]]` | dangling |  |
| 4 | summary | Headline discrimination is AUC 0.7480 on test and 0.7589 on… | 0.748 | ratio | auc | test | eq | `[[art:4cb18aab:run.metrics]]` | dangling |  |
| 5 | summary | Headline discrimination is AUC 0.7480 on test and 0.7589 on… | 0.7589 | ratio | auc | train | eq | `[[art:4cb18aab:run.metrics]]` | dangling |  |
| 6 | summary | Headline discrimination is AUC 0.7480 on test and 0.7589 on… | 0.4961 | ratio | gini | test | eq | `[[art:4cb18aab:run.metrics]]` | dangling |  |
| 7 | summary | Headline discrimination is AUC 0.7480 on test and 0.7589 on… | 0.5177 | ratio | gini | train | eq | `[[art:4cb18aab:run.metrics]]` | dangling |  |
| 8 | summary | Headline discrimination is AUC 0.7480 on test and 0.7589 on… | 0.419 | ratio | ks | test | eq | `[[art:4cb18aab:run.metrics]]` | dangling |  |
| 9 | summary | Headline discrimination is AUC 0.7480 on test and 0.7589 on… | 0.4447 | ratio | ks | train | eq | `[[art:4cb18aab:run.metrics]]` | dangling |  |
| 10 | summary | Headline discrimination is AUC 0.7480 on test and 0.7589 on… | 2 | ratio |  |  | eq |  | unsupported |  |
| 11 | summary | Headline discrimination is AUC 0.7480 on test and 0.7589 on… | 1 | ratio |  |  | eq |  | unsupported |  |
| 12 | summary | Headline discrimination is AUC 0.7480 on test and 0.7589 on… | 0.22454 | ratio | event_rate | train | eq | `[[art:4cb18aab:run.metrics]]` | dangling |  |
| 13 | conceptual_soundness | The choice of a standardised logistic regression for a binar… | 22.5 | percent | event_rate |  | eq |  | unsupported |  |
| 14 | conceptual_soundness | The feature inventory is the strongest part of the submissio… | 0.748 | ratio | auc |  | eq | `[[art:4cb18aab:run.metrics]]` | dangling |  |
| 15 | conceptual_soundness | The feature inventory is the strongest part of the submissio… | 0.9 | ratio | auc |  | eq |  | unsupported |  |
| 16 | conceptual_soundness | The feature inventory is the strongest part of the submissio… | 0.748 | ratio | auc |  | eq |  | unsupported |  |
| 17 | conceptual_soundness | The fitted coefficient structure is where conceptual soundne… | 0.7279 | ratio | coefficient |  | eq | `[[art:259cdde6:run.model_summary]]` | dangling |  |
| 18 | conceptual_soundness | The fitted coefficient structure is where conceptual soundne… | 2.7 | ratio | coefficient |  | ratio |  | unsupported |  |
| 19 | conceptual_soundness | The fitted coefficient structure is where conceptual soundne… | 0.27 | ratio | coefficient |  | eq |  | unsupported |  |
| 20 | conceptual_soundness | - `delinq_max_6m` carries **-0.0305**, implying that a worse… | -0.0305 | ratio | coefficient |  | eq |  | unsupported |  |
| 21 | conceptual_soundness | - `pay_ratio_mean_6m` carries **-0.3768** while `pay_ratio_l… | -0.3768 | ratio | coefficient |  | eq |  | unsupported |  |
| 22 | conceptual_soundness | - `pay_ratio_mean_6m` carries **-0.3768** while `pay_ratio_l… | 0.118 | ratio | coefficient |  | eq |  | unsupported |  |
| 23 | conceptual_soundness | - `limit_bal` carries **+0.0742**, implying that a larger gr… | 0.0742 | ratio | coefficient |  | eq |  | unsupported |  |
| 24 | conceptual_soundness | - `bill_mean_6m` at -0.3703 and `bill_trend_6m` at -0.2243 a… | -0.3703 | ratio | coefficient |  | eq |  | unsupported |  |
| 25 | conceptual_soundness | - `bill_mean_6m` at -0.3703 and `bill_trend_6m` at -0.2243 a… | -0.2243 | ratio | coefficient |  | eq |  | unsupported |  |
| 26 | conceptual_soundness | The developer did address collinearity: `bill_last` (VIF 161… | 161.13 | ratio | vif |  | eq | `[[art:259cdde6:run.model_summary]]` | dangling |  |
| 27 | conceptual_soundness | The developer did address collinearity: `bill_last` (VIF 161… | 36.45 | ratio | vif |  | eq | `[[art:259cdde6:run.model_summary]]` | dangling |  |
| 28 | conceptual_soundness | The developer did address collinearity: `bill_last` (VIF 161… | 10 | ratio | vif |  | eq | `[[art:259cdde6:run.model_summary]]` | dangling |  |
| 29 | conceptual_soundness | The developer did address collinearity: `bill_last` (VIF 161… | -0.0693 | ratio | coefficient |  | eq |  | unsupported |  |
| 30 | conceptual_soundness | The developer did address collinearity: `bill_last` (VIF 161… | 0.1244 | ratio | coefficient |  | eq |  | unsupported |  |
| 31 | data_integrity | The raw training profile shows 3,545 rows with **zero missin… | 3545 | count | row_count | train | eq | `[[art:3e5e172d:plain_llm.profile]]` | dangling |  |
| 32 | data_integrity | Two distributional artefacts warrant attention. First, `pay_… | 2 | ratio | max | train | eq | `[[art:3e5e172d:plain_llm.profile]]` | dangling |  |
| 33 | data_integrity | Two distributional artefacts warrant attention. First, `pay_… | 1.6385 | ratio | max | train | eq | `[[art:3e5e172d:plain_llm.profile]]` | dangling |  |
| 34 | data_integrity | Two distributional artefacts warrant attention. First, `pay_… | 1.1298 | ratio | max | train | eq |  | unsupported |  |
| 35 | data_integrity | Two distributional artefacts warrant attention. First, `pay_… | -234.9 | currency | mean | train | eq |  | unsupported |  |
| 36 | data_integrity | Two distributional artefacts warrant attention. First, `pay_… | -67201 | currency | min | train | eq |  | unsupported |  |
| 37 | data_integrity | Two distributional artefacts warrant attention. First, `pay_… | 27398 | currency | max | train | eq |  | unsupported |  |
| 38 | data_integrity | Two distributional artefacts warrant attention. First, `pay_… | 3119 | currency | sd | train | eq |  | unsupported |  |
| 39 | data_integrity | On split integrity: train n=3,545 and test n=1,500 sum to 5,… | 3545 | count | row_count | train | eq | `[[art:c005db79:run.splits]]` | dangling |  |
| 40 | data_integrity | On split integrity: train n=3,545 and test n=1,500 sum to 5,… | 1500 | count | row_count | test | eq | `[[art:c005db79:run.splits]]` | dangling |  |
| 41 | data_integrity | On split integrity: train n=3,545 and test n=1,500 sum to 5,… | 5045 | count | row_count |  | eq | `[[art:3e5e172d:plain_llm.profile]]` | dangling |  |
| 42 | data_integrity | On split integrity: train n=3,545 and test n=1,500 sum to 5,… | 1 | count | min |  | eq | `[[art:3e5e172d:plain_llm.profile]]` | dangling |  |
| 43 | data_integrity | On split integrity: train n=3,545 and test n=1,500 sum to 5,… | 5045 | count | client_count |  | eq |  | unsupported |  |
| 44 | data_integrity | On drift: **no drift evidence exists in the store**. There i… | 0.224542 | ratio | event_rate | train | eq | `[[art:c005db79:run.splits]]` | dangling |  |
| 45 | data_integrity | On drift: **no drift evidence exists in the store**. There i… | 0.224667 | ratio | event_rate | test | eq | `[[art:c005db79:run.splits]]` | dangling |  |
| 46 | data_integrity | On drift: **no drift evidence exists in the store**. There i… | 0.0001 | ratio | event_rate |  | delta | `[[art:c005db79:run.splits]]` | dangling |  |
| 47 | outcomes | Discrimination is stable between development and holdout. Te… | 0.748 | ratio | auc | test | eq | `[[art:4cb18aab:run.metrics]]` | dangling |  |
| 48 | outcomes | Discrimination is stable between development and holdout. Te… | 0.7589 | ratio | auc | train | eq | `[[art:4cb18aab:run.metrics]]` | dangling |  |
| 49 | outcomes | Discrimination is stable between development and holdout. Te… | 0.0109 | ratio | delta_auc |  | delta | `[[art:4cb18aab:run.metrics]]` | dangling |  |
| 50 | outcomes | Discrimination is stable between development and holdout. Te… | 3545 | count |  | train | eq |  | unsupported |  |
| 51 | outcomes | Discrimination is stable between development and holdout. Te… | 0.4447 | ratio | ks | train | eq |  | unsupported |  |
| 52 | outcomes | Discrimination is stable between development and holdout. Te… | 0.419 | ratio | ks | test | eq |  | unsupported |  |
| 53 | outcomes | Discrimination is stable between development and holdout. Te… | 0.5177 | ratio | gini | train | eq |  | unsupported |  |
| 54 | outcomes | Discrimination is stable between development and holdout. Te… | 0.4961 | ratio | gini | test | eq |  | unsupported |  |
| 55 | outcomes | Log loss is 0.4650 on train and 0.4674 on test, and the Brie… | 0.465 | ratio | log_loss | train | eq | `[[art:4cb18aab:run.metrics]]` | dangling |  |
| 56 | outcomes | Log loss is 0.4650 on train and 0.4674 on test, and the Brie… | 0.4674 | ratio | log_loss | test | eq | `[[art:4cb18aab:run.metrics]]` | dangling |  |
| 57 | outcomes | Log loss is 0.4650 on train and 0.4674 on test, and the Brie… | 0.14904 | ratio | brier | train | eq | `[[art:4cb18aab:run.metrics]]` | dangling |  |
| 58 | outcomes | Log loss is 0.4650 on train and 0.4674 on test, and the Brie… | 0.14895 | ratio | brier | test | eq | `[[art:4cb18aab:run.metrics]]` | dangling |  |
| 59 | outcomes | Aggregate calibration is good. On test, mean predicted proba… | 0.2213 | ratio | mean_prediction | test | eq | `[[art:4cb18aab:run.metrics]]` | dangling |  |
| 60 | outcomes | Aggregate calibration is good. On test, mean predicted proba… | 0.22467 | ratio | event_rate | test | eq | `[[art:4cb18aab:run.metrics]]` | dangling |  |
| 61 | outcomes | Aggregate calibration is good. On test, mean predicted proba… | 0.0034 | ratio | event_rate | test | delta | `[[art:4cb18aab:run.metrics]]` | dangling |  |
| 62 | outcomes | Aggregate calibration is good. On test, mean predicted proba… | 1.5 | percent |  | test | eq | `[[art:4cb18aab:run.metrics]]` | dangling |  |
| 63 | outcomes | Aggregate calibration is good. On test, mean predicted proba… | 0.224615 | ratio | mean_prediction | train | eq | `[[art:4cb18aab:run.metrics]]` | dangling |  |
| 64 | outcomes | Aggregate calibration is good. On test, mean predicted proba… | 0.224542 | ratio | event_rate | train | eq | `[[art:4cb18aab:run.metrics]]` | dangling |  |
| 65 | outcomes | No challenger model of any kind appears in the store. There… | 2.7 | ratio | coefficient |  | ratio |  | unsupported |  |
| 66 | outcomes | No challenger model of any kind appears in the store. There… | 0.748 | ratio | auc | test | eq |  | unsupported |  |
| 67 | sensitivity | - `delinq_last` +0.7279 (risk rises with recent delinquency… | 0.7279 | ratio | coefficient |  | eq |  | unsupported |  |
| 68 | sensitivity | - `delinq_count_6m` +0.1244 (risk rises with frequency — cor… | 0.1244 | ratio | coefficient |  | eq |  | unsupported |  |
| 69 | sensitivity | - `delinq_max_6m` **-0.0305** (risk *falls* as the worst del… | -0.0305 | ratio | coefficient |  | eq |  | unsupported |  |
| 70 | sensitivity | Because `delinq_max_6m` ranges 0 to 8 with a mean of 2.09 ,… | 0 | ratio | min |  | eq | `[[art:3e5e172d:plain_llm.profile]]` | dangling |  |
| 71 | sensitivity | Because `delinq_max_6m` ranges 0 to 8 with a mean of 2.09 ,… | 8 | ratio | max |  | eq | `[[art:3e5e172d:plain_llm.profile]]` | dangling |  |
| 72 | sensitivity | Because `delinq_max_6m` ranges 0 to 8 with a mean of 2.09 ,… | 2.09 | ratio | mean |  | eq | `[[art:3e5e172d:plain_llm.profile]]` | dangling |  |
| 73 | sensitivity | The same problem appears in the payment-ratio pair, where `p… | -0.3768 | ratio | coefficient |  | eq |  | unsupported |  |
| 74 | sensitivity | The same problem appears in the payment-ratio pair, where `p… | 0.118 | ratio | coefficient |  | eq |  | unsupported |  |
| 75 | sensitivity | The same problem appears in the payment-ratio pair, where `p… | 0.0742 | ratio | coefficient |  | eq |  | unsupported |  |
| 76 | findings | **Low.** C1 (calibration evidenced only at the portfolio mea… | 2 | ratio |  |  | eq |  | unsupported |  |
| 77 | findings | **Low.** C1 (calibration evidenced only at the portfolio mea… | 10 | ratio | vif |  | eq |  | unsupported |  |
| 78 | findings | **Informational.** O1 (train-to-test AUC gap of 0.0109 — no… | 0.0109 | ratio | delta_auc |  | delta |  | unsupported |  |
| 79 | findings | **Informational.** O1 (train-to-test AUC gap of 0.0109 — no… | 5045 | count |  |  | eq |  | unsupported |  |
| 80 | findings | 5. **Document the data preparation.** Explain the zero missi… | 2 | ratio |  |  | eq |  | unsupported |  |
| 81 | findings | Until items 1 through 3 are complete, the model should be re… | 1 | count |  |  | eq |  | unsupported |  |
| 82 | findings | Until items 1 through 3 are complete, the model should be re… | 3 | count |  |  | eq |  | unsupported |  |
| 83 | monitoring | *Monthly.* Score distribution PSI against the development ba… | 0.1 | ratio | psi |  | eq |  | unsupported |  |
| 84 | monitoring | *Monthly.* Score distribution PSI against the development ba… | 0.25 | ratio | psi |  | eq |  | unsupported |  |
| 85 | monitoring | *Monthly.* Score distribution PSI against the development ba… | 0.7279 | ratio | coefficient |  | eq | `[[art:259cdde6:run.model_summary]]` | dangling |  |
| 86 | monitoring | *Monthly.* Score distribution PSI against the development ba… | 0.2213 | ratio | mean_predicted_probability | test | eq | `[[art:4cb18aab:run.metrics]]` | dangling |  |
| 87 | monitoring | *Monthly.* Score distribution PSI against the development ba… | 10 | count | n_features |  | eq | `[[art:259cdde6:run.model_summary]]` | dangling |  |
| 88 | monitoring | *Monthly.* Score distribution PSI against the development ba… | 2 | ratio | max |  | eq | `[[art:3e5e172d:plain_llm.profile]]` | dangling |  |
| 89 | monitoring | *Quarterly, once outcomes mature.* Realised AUC, KS and Gini… | 0.7 | ratio | auc |  | eq |  | unsupported |  |
| 90 | monitoring | *Quarterly, once outcomes mature.* Realised AUC, KS and Gini… | 0.65 | ratio | auc |  | eq |  | unsupported |  |
| 91 | monitoring | *Quarterly, once outcomes mature.* Realised AUC, KS and Gini… | 0.748 | ratio | auc | test | eq |  | unsupported |  |
| 92 | monitoring | *Quarterly, once outcomes mature.* Realised AUC, KS and Gini… | 0.2247 | ratio | event_rate | train | eq |  | unsupported |  |

## Appendix B — Artifact index

The store holds 14 artifacts; the 12 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `plain_llm.profile` | `3e5e172d` | json | json | raw profile of data_train.csv |
| `run.data_test` | `26fbbf1d` | table | table, 1500 rows | the subject's data_test.csv |
| `run.data_train` | `1b015759` | table | table, 3545 rows | the subject's data_train.csv |
| `run.duration_s` | `719a149c` | scalar | 1.543819291 | subject wall-clock seconds |
| `run.features` | `abbb748e` | json | json | the subject's features.json |
| `run.metrics` | `4cb18aab` | json | json | the subject's metrics.json |
| `run.model_summary` | `259cdde6` | json | json | the subject's model_summary.json |
| `run.predictions_test` | `b0650ce2` | table | table, 1500 rows | the subject's predictions_test.csv |
| `run.predictions_train` | `9df50bd0` | table | table, 3545 rows | the subject's predictions_train.csv |
| `run.splits` | `c005db79` | json | json | the subject's splits.json |
| `run.status` | `2922931d` | json | json | how the subject's subprocess ended |
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |

## Appendix C — Run trace summary

| quantity | value |
|---|---|
| tool calls | 1 (run_model 1) |
| plan steps (bounded loop) | 0 |
| LLM calls | 8 (plain_llm 1, extract 7) |
| re-asks | 0 |
| repair rounds | 0 |
| tokens in / out | 60,163 / 34,601 |
| notional cost (USD) | 1.4513 |
| wall-clock (s) | 423.99 |
| subject run (s) | 1.54 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | credit_default-plain_llm-20260918T181914Z-6e98ce62 |

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
