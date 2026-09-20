---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: plain_llm
model: claude-opus-5[1m]
run_id: credit_default-plain_llm-20260918T082409Z-6e98ce62
data_mode: synthetic
synthetic_n: 5000
grounding_precision_pre: 0.0000
grounding_precision_post: 0.0000
n_claims: 103
n_findings_by_severity: {high: 0, medium: 3, low: 6, info: 2}
generated: "2026-09-18T08:24:09Z"
illustrative: false
---

# Validation report — `credit_default` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `credit_default` v1.0 | `plain_llm` | claude-opus-5[1m] | synthetic, n = 5000 | 0.0000 → 0.0000 | 0 / 3 / 6 / 2 |
<!-- quaestor:renderer:end -->

This report documents an independent validation review of package `credit_default`, version 1.0, a `binary_classification` model that predicts `default_next_month` for credit-card clients. The subject is a standardised logistic regression over ten retained features, fitted on ⟦unverified: 3,500⟧ training rows and evaluated on ⟦unverified: 1,500⟧ held-out rows ([[art:74c10f15:run.model_summary]], [[art:3b6b0a38:run.splits]]).

The scope of the review is limited to the artifacts the developer produced. Those are: a metrics file, a model summary, a feature inventory with timing declarations, a split manifest with row hashes, raw-data profiles, prediction tables for both splits, and run telemetry ([[art:c2f664c6:run.metrics]], [[art:74c10f15:run.model_summary]], [[art:abbb748e:run.features]], [[art:3b6b0a38:run.splits]], [[art:6a89f2be:run.data_train]], [[art:3b63748c:run.data_test]], [[art:6fd8f98a:run.predictions_train]], [[art:d612396b:run.predictions_test]], [[art:2922931d:run.status]], [[art:1742051a:run.duration_s]], [[art:2ad8d1a5:runtime.max_seconds]]).

Headline performance: test AUC ⟦unverified: 0.7446⟧, Gini ⟦unverified: 0.4893⟧, KS ⟦unverified: 0.4100⟧, Brier ⟦unverified: 0.1494⟧, log-loss ⟦unverified: 0.4684⟧ on n = ⟦unverified: 1,500⟧ with an observed event rate of ⟦unverified: 22.47%⟧ ([[art:c2f664c6:run.metrics#test]]). Discrimination is adequate for a behavioural default scorecard and the internal consistency of the metric set checks out (Gini = ⟦unverified: 2⟧·AUC − ⟦unverified: 1⟧ to ten decimal places on both splits).

The binding limitation of this review is coverage rather than performance. The developer supplied a single champion model, a single random train/test partition, and no out-of-time sample, no challenger, no population-stability computation, no calibration curve, and no sensitivity or scenario grids. Several standard validation tests therefore could not be executed at all, and the corresponding findings below record untested control areas rather than measured failures. Sections ⟦unverified: 3⟧ through ⟦unverified: 5⟧ state explicitly, in each case, whether a conclusion is measured or unassessable.

## 2. Conceptual soundness

The choice of a standardised logistic regression for a regulated credit-default application is appropriate and defensible: the functional form is monotone in each feature, the coefficients are directly interpretable as log-odds per standard deviation, and the model is straightforward to monitor and to challenge. Standardisation is declared (`standardised: true`) and `class_weight` is `null`, which is the correct choice here — the ⟦unverified: 22.5%⟧ event rate is not so imbalanced as to require reweighting, and leaving weights off preserves the natural calibration of the fitted probabilities.

The feature inventory is well constructed from a timing standpoint. Of twelve candidate features, two are `at_origination` and ten are `before_period_start`; `during_period` and `after_outcome` are both zero ([[art:abbb748e:run.features]]). No feature is declared as observable at or after the outcome, so there is no declared target leakage. The dominant coefficient, `delinq_last` at +⟦unverified: 0.7334⟧, is an economically sensible driver of next-month default, and the overall discrimination (test AUC ⟦unverified: 0.7446⟧) is in the range one expects from behavioural repayment history — not the implausibly high range that would signal a leaked outcome proxy.

The soundness concern is coefficient signs. Three of the ten retained coefficients point the wrong way relative to credit-risk theory or contradict a sibling feature ([[art:74c10f15:run.model_summary#coefficients]]):

- `limit_bal` = **+⟦unverified: 0.0727⟧** (odds ratio ⟦unverified: 1.075⟧ per SD). A higher approved credit limit implies a *higher* modelled default probability. The granted limit is itself the lender's prior creditworthiness assessment, so the expected sign is negative.
- `delinq_max_6m` = **−⟦unverified: 0.0322⟧** (OR ⟦unverified: 0.968⟧ per SD). The worst delinquency observed in the last six months *reduces* modelled risk, while `delinq_last` (+⟦unverified: 0.7334⟧) and `delinq_count_6m` (+⟦unverified: 0.1226⟧) increase it. The three cannot all be right.
- `pay_ratio_last` = **+⟦unverified: 0.1026⟧** against `pay_ratio_mean_6m` = **−⟦unverified: 0.3554⟧**. Paying a larger share of the most recent bill raises risk while paying a larger average share lowers it. One of these is a suppressor artefact rather than an economic relationship.

`bill_mean_6m` = −⟦unverified: 0.3726⟧ is also questionable in combination with `utilisation` = +⟦unverified: 0.2662⟧, since the two are positively related in the raw data and would be expected to carry the same sign. The most probable explanation for all of these is residual collinearity within the delinquency, payment-ratio and billing feature families (see section 3 and finding M1), not a coding error: the magnitudes of the wrong-signed terms are small, which is the signature of variance inflation splitting a shared signal rather than of a mislabelled column.

The practical consequence is that this model is usable for ranking but must not be used for reason-code generation, adverse-action explanation, or any pricing logic that reads individual coefficients as marginal effects, until the signs are repaired.

## 3. Data integrity and drift

**Integrity — measured.** The training profile reports zero missing values in all thirteen columns across ⟦unverified: 3,500⟧ rows ([[art:6a89f2be:run.data_train]]). Ranges are broadly plausible: `age` ⟦unverified: 21⟧–⟦unverified: 63,⟧ `limit_bal` ⟦unverified: 10,000⟧–⟦unverified: 800,000,⟧ `utilisation` ⟦unverified: 0.0045⟧–⟦unverified: 1.1297⟧. Utilisation above 1.0 is legitimate (over-limit balances) and needs no correction, only documentation.

Two integrity observations do warrant recording. First, `pay_ratio_last` has a maximum of exactly **⟦unverified: 2.0⟧** while `pay_ratio_mean_6m` maxes at ⟦unverified: 1.6385⟧; an exact round bound on one variable and not the other is the signature of an undocumented cap, and capping is an undeclared transformation that must be reproduced identically in production scoring. Second, `bill_trend_6m` has mean −⟦unverified: 237.6⟧ with standard deviation ⟦unverified: 3,118.5⟧ and a minimum of −⟦unverified: 67,201.4⟧, i.e. a tail more than twenty standard deviations from the mean, with no winsorisation or trimming documented anywhere in the artifact set. In a standardised linear model, a single such observation exerts material leverage.

**Cross-split integrity — unassessable.** A raw-data profile was supplied for the training split only. No equivalent profile exists for the test split, so the standard comparison of missingness and marginal distributions between splits could not be performed ([[art:6a89f2be:run.data_train]], [[art:3b63748c:run.data_test]]). Zero missingness in train does not establish zero missingness in test.

**Split disjointness — partially assessable.** `splits.json` records distinct `rows_hash` values for train (`e028347d…`) and test (`3e28943d…`) ([[art:3b6b0a38:run.splits]]). Distinct manifest hashes establish only that the two row sets are not identical; they are not an overlap test. The indirect evidence is reassuring but not conclusive: `client_id` in train ranges ⟦unverified: 1⟧–⟦unverified: 5,000⟧ with mean ⟦unverified: 2,513.91⟧ over ⟦unverified: 3,500⟧ rows, and ⟦unverified: 3,500⟧ + ⟦unverified: 1,500⟧ = ⟦unverified: 5,000,⟧ which is exactly what a disjoint random partition of ⟦unverified: 5,000⟧ distinct clients would produce (expected mean ⟦unverified: 2,500.5⟧ against observed ⟦unverified: 2,513.91⟧). No explicit key-intersection or duplicate-client count was computed, so contamination remains formally untested.

**Drift — unassessable.** No population stability index was computed for any feature, and no score-distribution PSI was computed between train and test or against any later period. There is no out-of-time sample: the test set is a random partition of the same population and the same period as the training set, which by construction cannot detect drift. The only cross-split comparison available is the target prevalence, ⟦unverified: 22.4571%⟧ in train against ⟦unverified: 22.4667%⟧ in test, a difference of ⟦unverified: 0.0095⟧ percentage points, confirming the split was stratified but saying nothing about feature or score drift over time ([[art:c2f664c6:run.metrics]], [[art:3b6b0a38:run.splits]]).

**Multicollinearity — measured, and incompletely controlled.** The developer declared a VIF threshold of ⟦unverified: 10.0⟧ and removed two features on that basis: `bill_last` (VIF ⟦unverified: 160.89⟧) and `utilisation_mean_6m` (VIF ⟦unverified: 36.36⟧) ([[art:74c10f15:run.model_summary#removed]]). The screen was clearly run and the two worst offenders were correctly dropped. What is missing is the evidence that the control succeeded: no post-pruning VIF values are reported for the ten retained features, and no condition number is reported for the retained design matrix. Since `bill_last` was removed but `bill_mean_6m` and `bill_trend_6m` were kept, and `utilisation_mean_6m` was removed but `utilisation` was kept, the retained set still contains three delinquency variables, two payment-ratio variables and two billing variables drawn from overlapping windows. The wrong-signed coefficients documented in section 2 are the expected symptom of exactly that residual dependence, and they are the strongest available evidence that a VIF cut-off of ⟦unverified: 10.0⟧ was not stringent enough for this feature set.

## 4. Outcomes analysis

**Discrimination.** Test AUC is ⟦unverified: 0.7446⟧ against train AUC ⟦unverified: 0.7584⟧, a gap of **⟦unverified: 0.0138⟧** ([[art:c2f664c6:run.metrics]]). KS degrades from ⟦unverified: 0.4451⟧ to ⟦unverified: 0.4100⟧ (gap ⟦unverified: 0.0351⟧) and Gini from ⟦unverified: 0.5169⟧ to ⟦unverified: 0.4893⟧ (gap ⟦unverified: 0.0276⟧). Log-loss rises only from ⟦unverified: 0.4650⟧ to ⟦unverified: 0.4684⟧ and Brier from ⟦unverified: 0.1489⟧ to ⟦unverified: 0.1494⟧. A ⟦unverified: 1.4⟧-point AUC gap on a ⟦unverified: 3,500⟧-row training sample with ten parameters is well within sampling noise and comfortably inside any conventional out-of-sample degradation tolerance; this model is not materially over-fitted. The absence of overfitting is the clearest positive result in the artifact set and is recorded as informational only.

**Calibration.** On train, mean predicted probability is ⟦unverified: 0.224623⟧ against an observed event rate of ⟦unverified: 0.224571⟧ — agreement to four decimal places, which is the expected fixed-point property of unpenalised logistic maximum likelihood and confirms the fit converged. On test, mean predicted is **⟦unverified: 0.212653⟧** against an observed **⟦unverified: 0.224667⟧**. The model under-predicts the test event rate by **⟦unverified: 1.20⟧ percentage points**, a predicted-to-observed ratio of **⟦unverified: 0.9465⟧**, i.e. ⟦unverified: 5.35%⟧ relative under-prediction of aggregate expected defaults. For a portfolio-level expected-loss input this is a real, directional bias and would understate provisions by roughly ⟦unverified: 5%⟧ if applied unadjusted.

The magnitude is modest and may be partly a ⟦unverified: 1,500⟧-row sampling effect, but it cannot be decomposed, because no calibration curve, decile table or fitted calibration slope and intercept were produced. Calibration was assessed here only in aggregate, from the two mean-predicted figures in the metrics file. Per-decile calibration, which is what actually matters for a scorecard used with cut-offs, is untested despite the prediction tables being available to test it ([[art:d612396b:run.predictions_test]], [[art:6fd8f98a:run.predictions_train]]).

**Effective challenge.** No challenger model of any kind was submitted — no regularised variant, no gradient-boosted benchmark, no single-feature or `delinq_last`-only baseline. `model_summary.json` documents one specification and `metrics.json` reports one model's results. Without at least one benchmark there is no evidence that the ten-feature logistic form captures the available signal, and in particular no evidence on whether the three wrong-signed features contribute anything at all. This is the most significant procedural gap in the submission.

## 5. Sensitivity and scenario analysis

No sensitivity or scenario analysis was performed by the developer. The artifact set contains no partial-dependence output, no univariate response curves, no stressed-input scoring, no macroeconomic overlay, and no perturbation or stability testing of the coefficient vector. Nothing in the store reports what happens to predicted default rates under a downturn in utilisation, a deterioration in payment ratios, or a shift in the delinquency distribution.

What can be inferred analytically is that the coefficient vector implies three economically wrong-signed response curves ([[art:74c10f15:run.model_summary#coefficients]]). Because the model is a monotone logistic function of a linear index, the sign of each coefficient fully determines the shape of that feature's value curve:

- Stressing `delinq_max_6m` upward — a worsening worst-delinquency scenario — *lowers* the predicted default probability (coefficient −⟦unverified: 0.0322⟧). This is the wrong direction for a stress test and would produce a downturn scenario that looks better than the base case on that axis.
- Stressing `limit_bal` upward *raises* predicted default (+⟦unverified: 0.0727⟧), so a limit-increase scenario is scored as risk-increasing on the feature itself rather than through utilisation.
- `pay_ratio_last` (+⟦unverified: 0.1026⟧) and `pay_ratio_mean_6m` (−⟦unverified: 0.3554⟧) respond in opposite directions to the same repayment shock, so any scenario that moves repayment behaviour coherently across both windows produces a partially self-cancelling and unpredictable net effect.

Any scenario suite built on this coefficient vector would therefore report directionally wrong sensitivities for at least part of the input space. The repair is the collinearity remediation in section 6, not a change to the scenario methodology. Until both the remediation and an actual scenario suite exist, the model has no validated behaviour outside the range of the development sample, and its use should be restricted to populations resembling the training profile ([[art:6a89f2be:run.data_train]]).

## 6. Findings and recommendations

Eleven findings are recorded below and enumerated in the structured list that accompanies this report. Two are measured defects in the model as built (M1, C1); one is a procedural omission of a mandatory control (E1); one is an undocumented and therefore unverifiable developer control (T1); six record validation areas that could not be tested with the artifacts supplied (X1, S1, L2, D1, R1, plus the informational L1 coverage note); and one records a favourable measured result (O1).

Required remediations, in priority order:

1. **Resolve the sign anomalies before any interpretive use (M1).** Re-run the collinearity screen at a stricter threshold — VIF ⟦unverified: 5⟧ is the conventional choice for a scorecard — report post-pruning VIFs and the design-matrix condition number for the retained set, and collapse each overlapping family to one representative: one delinquency severity measure, one delinquency frequency measure, one payment-ratio window, one billing-level measure. Every retained coefficient must carry the economically expected sign, or the exception must be argued and documented.
2. **Submit at least one challenger and a trivial baseline (E1).** A penalised logistic model and a `delinq_last`-only scorecard are the minimum. Report the AUC and Brier differences on the same test split so effective challenge can be evidenced.
3. **Produce a calibration assessment and correct the test-set bias (C1).** Fit and report the calibration slope and intercept, publish a ten-bin predicted-versus-observed table from the existing prediction tables, and either re-calibrate the intercept or document why the ⟦unverified: 5.35%⟧ relative under-prediction is acceptable for the intended use.
4. **Evidence the split hygiene (L2).** Report the client-key intersection count between train and test and the duplicate-key count within each. The indirect arithmetic is reassuring but an explicit zero-overlap statement is required.
5. **Profile the test split and document the transformations (D1).** Publish the test-split profile so cross-split missingness and distributions can be compared, declare the apparent ⟦unverified: 2.0⟧ cap on `pay_ratio_last`, and state the treatment of the extreme `bill_trend_6m` tail.
6. **Build the out-of-time and stability evidence (S1, R1).** Score a later time period, compute feature-level and score-level PSI against the development sample, and re-fit or at minimum re-score across segments and time regimes to test coefficient-sign and AUC stability.
7. **Add a scenario suite (X1).** Univariate response curves for all retained features plus a downturn scenario, produced after the sign remediation so the curves are directionally meaningful.

On current evidence the model's discrimination is sound and stable out of sample, and the leakage-timing discipline is good. The model should be approved only for rank-ordering use, with conditions: no coefficient-level interpretation or reason-code use, and no unadjusted use of the predicted probabilities as expected-loss inputs, until items ⟦unverified: 1⟧ through ⟦unverified: 3⟧ are closed.

### F-001 · M1 collinearity · severity **medium**

The developer ran a VIF screen at a declared threshold of 10.0 and removed the two worst offenders, bill_last (VIF 160.89) and utilisation_mean_6m (VIF 36.36). The screen was not stringent enough. The retained ten-feature set still contains three delinquency variables (delinq_last, delinq_count_6m, delinq_max_6m), two payment-ratio windows (pay_ratio_last, pay_ratio_mean_6m) and two billing variables (bill_mean_6m, bill_trend_6m) drawn from overlapping observation windows, and the fitted coefficients show the classic signature of variance inflation splitting a shared signal. Specifically: delinq_max_6m is -0.0322 (a worse six-month peak delinquency lowers modelled risk) while delinq_last is +0.7334 and delinq_count_6m is +0.1226; pay_ratio_last is +0.1026 against pay_ratio_mean_6m at -0.3554, so the same repayment behaviour is scored in opposite directions depending on window; and limit_bal is +0.0727, making a larger approved limit risk-increasing when the granted limit is itself the lender's creditworthiness assessment. bill_mean_6m at -0.3726 is likewise opposed to utilisation at +0.2662 despite the two being positively related in the raw data. No post-pruning VIF values and no design-matrix condition number were reported for the retained set, so the developer produced no evidence that the declared control actually succeeded; the wrong-signed coefficients are the evidence that it did not. Discrimination is unaffected, but the coefficients cannot be read as marginal effects, which rules out reason-code and adverse-action use. Remediation: re-screen at VIF 5, collapse each overlapping family to a single representative, and report post-pruning VIFs plus the condition number.

### F-002 · E1 effective challenge · severity **medium**

The artifact store contains exactly one model specification and one set of performance metrics. There is no regularised variant, no gradient-boosted or tree-based challenger, and not even a trivial single-feature baseline such as a delinq_last-only scorecard, despite delinq_last carrying by far the largest coefficient at +0.7334 and being an obvious candidate to reproduce most of the test AUC of 0.7446 on its own. Effective challenge is a mandatory validation control and it could not be performed at all. The absence has a concrete analytical cost here: without a benchmark there is no evidence that the ten-feature specification adds anything over a parsimonious alternative, and in particular no evidence on whether the three wrong-signed features flagged under M1 contribute any predictive value or are pure noise absorbed by collinearity. Remediation: submit a penalised logistic challenger and a single-feature baseline scored on the identical test split, and report the AUC and Brier deltas.

### F-003 · T1 declared threshold · severity **medium**

model_summary.json declares vif_threshold = 10.0 as an explicit developer control and evidences its application only by listing the two features removed and their pre-removal VIFs (bill_last 160.89, utilisation_mean_6m 36.36). No VIF is reported for any of the ten retained features after pruning, and no condition number is reported for the retained design matrix. The declared claim that the fitted model satisfies VIF < 10.0 on all inputs is therefore unsupported by any artifact, and cannot be independently confirmed or refuted from the store. The indirect evidence points against the claim: three retained coefficients carry economically inverted signs, which is difficult to reconcile with a genuinely well-conditioned design matrix. Two further developer choices are declared but unevidenced in the same way: standardised = true is stated with no scaler means or standard deviations recorded, which is a production-reproducibility gap since identical scaling must be applied at scoring time; and the raw profile shows pay_ratio_last capped at exactly 2.0 while its sibling pay_ratio_mean_6m maxes at 1.6385, implying an undeclared transformation. Remediation: publish the full post-pruning VIF vector, the condition number, and the fitted scaler parameters, and declare all input caps.

### F-004 · C1 calibration · severity **low**

On the test split, mean predicted probability is 0.212653 against an observed event rate of 0.224667. The model under-predicts aggregate default by 1.20 percentage points, a predicted-to-observed ratio of 0.9465, or 5.35% relative under-statement of expected defaults. Used unadjusted as an expected-loss input this would understate portfolio provisions by roughly 5%. On the training split the same comparison is 0.224623 against 0.224571, agreeing to four decimals, which is the expected fixed-point property of unpenalised logistic maximum likelihood and confirms the fit converged correctly; the bias is therefore specific to out-of-sample behaviour rather than a fitting failure. The magnitude is modest for n = 1500 and may be partly a sampling effect, but it cannot be decomposed because the developer produced no calibration curve, no decile predicted-versus-observed table, and no fitted calibration slope or intercept. Aggregate means are the only calibration evidence available, so per-decile calibration -- the property that actually governs behaviour at a scorecard cut-off -- is entirely untested even though the prediction tables needed to test it are present in the store. Remediation: fit and report the calibration slope and intercept, publish a ten-bin calibration table from run.predictions_test, and either re-calibrate the intercept or justify the residual bias for the intended use.

### F-005 · X1 scenario analysis · severity **low**

The artifact set contains no sensitivity or scenario output of any kind: no partial-dependence plots, no univariate response curves, no stressed-input scoring, no macroeconomic overlay, and no coefficient perturbation or stability testing. The model's behaviour outside the range of the development sample is therefore undocumented. Because the subject is a monotone logistic function of a linear index, the sign of each coefficient fully determines the shape of that feature's value curve, and the fitted vector implies three response curves that run the wrong way. Stressing delinq_max_6m upward, as a downturn scenario would, lowers the predicted default probability (coefficient -0.0322), so a stress test on worst-delinquency would report the stressed portfolio as safer than the base case. Stressing limit_bal upward raises predicted default (+0.0727), inverting the expected relationship. And pay_ratio_last (+0.1026) against pay_ratio_mean_6m (-0.3554) means any coherent repayment shock moves the two terms in opposing directions, producing a partially self-cancelling and unpredictable net sensitivity. Any scenario suite built on this coefficient vector would report directionally wrong sensitivities over part of the input space. Remediation: close the M1 collinearity finding first, then build univariate response curves for all retained features plus a downturn scenario, since curves produced before the sign repair would not be meaningful.

### F-006 · S1 population drift · severity **low**

No population stability index was computed for any feature, and no score-distribution PSI was computed between the splits or against any later period. More fundamentally, there is no out-of-time validation sample: the test set is a random partition of the same population over the same period as the training set, so it cannot detect temporal drift regardless of how it is analysed. The only cross-split distributional comparison available in the store is target prevalence, 22.4571% in train against 22.4667% in test, a difference of 0.0095 percentage points. That confirms the partition was stratified on the outcome but is silent on feature and score drift. Stability of this model in production is consequently unevidenced, and the monthly and quarterly PSI monitoring recommended in section 7 would be starting from no baseline measurement at all. Remediation: score a later closed outcome window and report feature-level and score-level PSI against the frozen development sample, with triggers at 0.10 amber and 0.25 red.

### F-007 · L2 contamination · severity **low**

splits.json records distinct row hashes for the two splits (train e028347d..., test 3e28943d...). Distinct manifest hashes establish only that the two row sets are not identical; they are not a test of row or key overlap, and no key-intersection count or within-split duplicate count was computed anywhere in the artifact set. Train/test contamination is therefore formally untested. The indirect arithmetic is reassuring and I found no positive sign of leakage: client_id in the training split ranges from 1 to 5,000 with a mean of 2,513.91 over 3,500 rows, and 3,500 + 1,500 = 5,000, which is precisely the pattern a disjoint random partition of 5,000 distinct clients would produce, the expected mean under that hypothesis being 2,500.5. The modest 1.4-point train-to-test AUC gap is also inconsistent with heavy contamination, since overlap would tend to compress that gap toward zero. This is recorded as an unclosed control rather than a detected defect. Remediation: report the client-key intersection count between splits and the duplicate-key count within each, and state zero overlap explicitly.

### F-008 · D1 data integrity · severity **low**

A raw-data profile was supplied for the training split only. It is clean -- zero missing values across all thirteen columns in 3,500 rows, with plausible ranges for age (21-63), limit_bal (10,000-800,000) and utilisation (0.0045-1.1297, where values above 1.0 are legitimate over-limit balances). But no equivalent profile exists for the test split, so the standard validation test of whether missingness or marginal distributions differ materially between splits could not be run at all. Zero missingness in train establishes nothing about test. Two integrity issues are visible within the training profile itself and should be documented regardless. First, pay_ratio_last has a maximum of exactly 2.0 while its sibling pay_ratio_mean_6m maxes at 1.6385; an exact round bound on one variable and not the other indicates an undeclared cap, and any such transformation must be reproduced identically in production scoring. Second, bill_trend_6m has mean -237.6 and standard deviation 3,118.5 but a minimum of -67,201.4, a tail beyond twenty standard deviations, with no winsorisation or trimming documented; in a standardised linear model a single such observation carries material leverage on the fitted coefficient. Remediation: publish the test-split profile, declare the pay_ratio_last cap, and state the treatment of the bill_trend_6m tail.

### F-009 · R1 regime stability · severity **low**

No regime, vintage, or segment analysis was performed. The developer supplied a single random train/test partition covering one population and one period, so there is no basis on which to test either of the two regime properties this validation is required to assess: whether a top feature flips sign across regimes, and whether AUC differs materially across them. Coefficient-sign stability is of particular concern for this model, because the collinearity documented under M1 makes the coefficient vector inherently unstable -- when a shared signal is split across correlated features, small changes in sample composition can move the individual loadings substantially, including across zero. The three already-inverted signs (delinq_max_6m, pay_ratio_last, limit_bal) are small in magnitude and thus the most likely to flip on re-fit. Recorded as low severity because it is an untested area rather than a measured failure, but the annual re-fit sign comparison recommended in section 7 is the control that would catch this. Remediation: re-fit and re-score across time vintages and material portfolio segments, reporting AUC and the full coefficient vector for each so sign and discrimination stability can be evidenced.

### F-010 · O1 out-of-sample degradation · severity **info**

Recorded as a favourable measured result rather than a defect. Train AUC is 0.7584 against test AUC 0.7446, a gap of 0.0138, well inside any conventional out-of-sample degradation tolerance. The supporting metrics agree: Gini falls from 0.5169 to 0.4893 (gap 0.0276), KS from 0.4451 to 0.4100 (gap 0.0351), log-loss rises only from 0.4650 to 0.4684, and Brier from 0.1489 to 0.1494. For a ten-parameter logistic model fitted on 3,500 rows these differences are consistent with sampling noise, and the model shows no sign of over-fitting. The metric set is also internally consistent, with Gini equal to 2*AUC - 1 to ten decimal places on both splits, which gives confidence that the reported figures were computed correctly rather than transcribed. No remediation is attached. The one caveat is that this gap is measured on a random in-time partition, so it evidences absence of over-fitting but not stability over time; see the S1 finding on the missing out-of-time sample. The baselines of 0.7446 AUC, 0.4893 Gini and 0.4100 KS should be frozen as the monitoring reference points.

### F-011 · L1 leakage · severity **info**

Recorded as informational, documenting a control that passes on the evidence available and a screen that was not run. The feature inventory is clean on timing: of twelve candidates, two are at_origination and ten are before_period_start, with during_period = 0 and after_outcome = 0. No feature is declared as observable at or after the outcome, so there is no declared leakage against the default_next_month target, and the timing discipline in the feature construction is good. The observed performance is also consistent with legitimate behavioural prediction rather than a leaked outcome proxy: test AUC of 0.7446 sits squarely in the expected range for a repayment-history scorecard, whereas a leaked outcome would typically drive discrimination far higher. What is missing is the confirmatory screen. No per-feature univariate AUC was computed, so the specific test of whether any single feature exceeds AUC 0.90 could not be executed directly; it was assessed only by inference from the model-level AUC and from the fact that no single coefficient dominates to the degree that would be required (delinq_last leads at +0.7334, but the full ten-feature model reaches only 0.7446). Remediation: report univariate AUC for each of the twelve candidate features to close the screen formally.

Candidates raised and not promoted: none.

### Open items

No open item was recorded for this validation.

## 7. Ongoing monitoring recommendations

Once the remediations above are closed, monitoring should be established on the following schedule.

**Monthly.** Score-distribution PSI against the frozen development sample ([[art:6a89f2be:run.data_train]]), with an amber trigger at ⟦unverified: 0.10⟧ and a red trigger at ⟦unverified: 0.25⟧. Mean predicted probability against realised default rate for the scored cohort, tracked as a predicted-to-observed ratio with an amber band outside ⟦unverified: 0.90⟧–⟦unverified: 1.10⟧ — note that the current test-set ratio of ⟦unverified: 0.9465⟧ already sits inside that band but off-centre, so the metric should be monitored from a known starting bias. Prediction-volume and score-percentile reconciliation, and a null-rate check on all ten scoring inputs, since production missingness is entirely untested at present.

**Quarterly.** Feature-level PSI for each of the ten retained features, at the same triggers. Discrimination on the newest closed outcome window — AUC, Gini and KS — against the test baselines of ⟦unverified: 0.7446⟧, ⟦unverified: 0.4893⟧ and ⟦unverified: 0.4100⟧; escalate on an AUC decline exceeding ⟦unverified: 0.05⟧ from baseline. A ten-bin calibration table with the fitted slope, escalating on a slope outside ⟦unverified: 0.80⟧–⟦unverified: 1.20⟧. Continued monitoring of the `bill_trend_6m` tail and of the `pay_ratio_last` cap rate, both of which are undocumented transformations today.

**Annually, or on trigger.** Full re-validation including a re-fit on the most recent data, with an explicit coefficient-sign comparison against the approved specification — this is the control that catches the collinearity problem recurring. Re-run of effective challenge against a live challenger. Segment-level and time-regime-level AUC and sign stability testing. Refresh of the scenario suite.

**Immediate triggers for off-cycle review.** Any coefficient sign flip on re-fit, any score PSI above ⟦unverified: 0.25⟧, a predicted-to-observed ratio outside ⟦unverified: 0.85⟧–⟦unverified: 1.15⟧ for two consecutive months, a shift in portfolio default prevalence of more than five percentage points from the ⟦unverified: 22.5%⟧ development base rate, or any change to the upstream construction of the delinquency, payment-ratio or billing feature families. Run telemetry should also be captured on every scheduled re-fit, with duration checked against the configured cap ([[art:1742051a:run.duration_s]], [[art:2ad8d1a5:runtime.max_seconds]], [[art:2922931d:run.status]]).

## Appendix A — Claims

Grounding precision 0.0000 before repair (0 of 103 claims verified; 77 unsupported, 19 dangling, 7 unattributed) and 0.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 0/13; conceptual_soundness 0/13; data_integrity 0/29; outcomes 0/24; sensitivity 0/4; findings 0/5; monitoring 0/15.

Developer claims: `plain_llm` runs no check over `package.yaml`'s declared claims See Appendix D.

Excluded numeric tokens (not claims): section_number (section 3, section 2, section 6, 1.); inline_code (`3e28943d…`); citation_hash (74c10f15, 3b6b0a38, c2f664c6, abbb748e); package_version (1.0); extractor_returned_excluded_token (1.0, -0.0322, -0.3554, -0.3726).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | This report documents an independent validation review of pa… | 3500 | count | splits | train | eq | `[[art:3b6b0a38:run.splits]]` | dangling |  |
| 2 | summary | This report documents an independent validation review of pa… | 1500 | count | splits | test | eq | `[[art:3b6b0a38:run.splits]]` | dangling |  |
| 3 | summary | Headline performance: test AUC 0.7446, Gini 0.4893, KS 0.410… | 0.7446 | ratio | auc | test | eq | `[[art:c2f664c6:run.metrics#test]]` | dangling |  |
| 4 | summary | Headline performance: test AUC 0.7446, Gini 0.4893, KS 0.410… | 0.4893 | ratio | gini | test | eq | `[[art:c2f664c6:run.metrics#test]]` | dangling |  |
| 5 | summary | Headline performance: test AUC 0.7446, Gini 0.4893, KS 0.410… | 0.41 | ratio | ks | test | eq | `[[art:c2f664c6:run.metrics#test]]` | dangling |  |
| 6 | summary | Headline performance: test AUC 0.7446, Gini 0.4893, KS 0.410… | 0.1494 | ratio | brier | test | eq | `[[art:c2f664c6:run.metrics#test]]` | dangling |  |
| 7 | summary | Headline performance: test AUC 0.7446, Gini 0.4893, KS 0.410… | 0.4684 | ratio | log_loss | test | eq | `[[art:c2f664c6:run.metrics#test]]` | dangling |  |
| 8 | summary | Headline performance: test AUC 0.7446, Gini 0.4893, KS 0.410… | 1500 | count | n | test | eq | `[[art:c2f664c6:run.metrics#test]]` | dangling |  |
| 9 | summary | Headline performance: test AUC 0.7446, Gini 0.4893, KS 0.410… | 22.47 | percent | event_rate | test | eq | `[[art:c2f664c6:run.metrics#test]]` | dangling |  |
| 10 | summary | Headline performance: test AUC 0.7446, Gini 0.4893, KS 0.410… | 2 | ratio |  |  | eq |  | unsupported |  |
| 11 | summary | Headline performance: test AUC 0.7446, Gini 0.4893, KS 0.410… | 1 | ratio |  |  | eq |  | unsupported |  |
| 12 | summary | The binding limitation of this review is coverage rather tha… | 3 | ratio |  |  | eq |  | unsupported |  |
| 13 | summary | The binding limitation of this review is coverage rather tha… | 5 | ratio |  |  | eq |  | unsupported |  |
| 14 | conceptual_soundness | The choice of a standardised logistic regression for a regul… | 22.5 | percent | event_rate |  | eq |  | unsupported |  |
| 15 | conceptual_soundness | The feature inventory is well constructed from a timing stan… | 0.7334 | ratio | coefficient |  | eq |  | unsupported |  |
| 16 | conceptual_soundness | The feature inventory is well constructed from a timing stan… | 0.7446 | ratio | auc | test | eq |  | unsupported |  |
| 17 | conceptual_soundness | - `limit_bal` = **+0.0727** (odds ratio 1.075 per SD). A hig… | 0.0727 | ratio | coefficient |  | eq |  | unsupported |  |
| 18 | conceptual_soundness | - `limit_bal` = **+0.0727** (odds ratio 1.075 per SD). A hig… | 1.075 | ratio | odds_ratio |  | eq |  | unsupported |  |
| 19 | conceptual_soundness | - `delinq_max_6m` = **−0.0322** (OR 0.968 per SD). The worst… | 0.0322 | ratio |  |  | eq |  | unattributed |  |
| 20 | conceptual_soundness | - `delinq_max_6m` = **−0.0322** (OR 0.968 per SD). The worst… | 0.968 | ratio | odds_ratio |  | eq |  | unsupported |  |
| 21 | conceptual_soundness | - `delinq_max_6m` = **−0.0322** (OR 0.968 per SD). The worst… | 0.7334 | ratio | coefficient |  | eq |  | unsupported |  |
| 22 | conceptual_soundness | - `delinq_max_6m` = **−0.0322** (OR 0.968 per SD). The worst… | 0.1226 | ratio | coefficient |  | eq |  | unsupported |  |
| 23 | conceptual_soundness | - `pay_ratio_last` = **+0.1026** against `pay_ratio_mean_6m`… | 0.1026 | ratio | coefficient |  | eq |  | unsupported |  |
| 24 | conceptual_soundness | - `pay_ratio_last` = **+0.1026** against `pay_ratio_mean_6m`… | 0.3554 | ratio |  |  | eq |  | unattributed |  |
| 25 | conceptual_soundness | `bill_mean_6m` = −0.3726 is also questionable in combination… | 0.3726 | ratio |  |  | eq |  | unattributed |  |
| 26 | conceptual_soundness | `bill_mean_6m` = −0.3726 is also questionable in combination… | 0.2662 | ratio | coefficient |  | eq |  | unsupported |  |
| 27 | data_integrity | **Integrity — measured.** The training profile reports zero… | 3500 | count |  | train | eq | `[[art:6a89f2be:run.data_train]]` | dangling |  |
| 28 | data_integrity | **Integrity — measured.** The training profile reports zero… | 21 | ratio |  | train | eq |  | unsupported |  |
| 29 | data_integrity | **Integrity — measured.** The training profile reports zero… | 63 | ratio |  | train | eq |  | unsupported |  |
| 30 | data_integrity | **Integrity — measured.** The training profile reports zero… | 10000 | currency |  | train | eq |  | unsupported |  |
| 31 | data_integrity | **Integrity — measured.** The training profile reports zero… | 800000 | currency |  | train | eq |  | unsupported |  |
| 32 | data_integrity | **Integrity — measured.** The training profile reports zero… | 0.0045 | ratio |  | train | eq |  | unsupported |  |
| 33 | data_integrity | **Integrity — measured.** The training profile reports zero… | 1.1297 | ratio |  | train | eq |  | unsupported |  |
| 34 | data_integrity | Two integrity observations do warrant recording. First, `pay… | 2 | ratio |  | train | eq |  | unsupported |  |
| 35 | data_integrity | Two integrity observations do warrant recording. First, `pay… | 1.6385 | ratio |  | train | eq |  | unsupported |  |
| 36 | data_integrity | Two integrity observations do warrant recording. First, `pay… | 237.6 | ratio |  |  | eq |  | unattributed |  |
| 37 | data_integrity | Two integrity observations do warrant recording. First, `pay… | 3118.5 | currency |  | train | eq |  | unsupported |  |
| 38 | data_integrity | Two integrity observations do warrant recording. First, `pay… | 67201.4 | ratio |  |  | eq |  | unattributed |  |
| 39 | data_integrity | **Split disjointness — partially assessable.** `splits.json`… | 1 | count |  | train | eq |  | unsupported |  |
| 40 | data_integrity | **Split disjointness — partially assessable.** `splits.json`… | 5000 | count |  | train | eq |  | unsupported |  |
| 41 | data_integrity | **Split disjointness — partially assessable.** `splits.json`… | 2513.91 | ratio |  | train | eq |  | unsupported |  |
| 42 | data_integrity | **Split disjointness — partially assessable.** `splits.json`… | 3500 | count |  | train | eq |  | unsupported |  |
| 43 | data_integrity | **Split disjointness — partially assessable.** `splits.json`… | 3500 | count |  | train | eq |  | unsupported |  |
| 44 | data_integrity | **Split disjointness — partially assessable.** `splits.json`… | 1500 | count |  | test | eq |  | unsupported |  |
| 45 | data_integrity | **Split disjointness — partially assessable.** `splits.json`… | 5000 | count |  |  | eq |  | unsupported |  |
| 46 | data_integrity | **Split disjointness — partially assessable.** `splits.json`… | 5000 | count |  |  | eq |  | unsupported |  |
| 47 | data_integrity | **Split disjointness — partially assessable.** `splits.json`… | 2500.5 | ratio |  |  | eq |  | unsupported |  |
| 48 | data_integrity | **Split disjointness — partially assessable.** `splits.json`… | 2513.91 | ratio |  | train | eq |  | unsupported |  |
| 49 | data_integrity | **Drift — unassessable.** No population stability index was… | 22.4571 | percent | event_rate | train | eq | `[[art:c2f664c6:run.metrics]]` | dangling |  |
| 50 | data_integrity | **Drift — unassessable.** No population stability index was… | 22.4667 | percent | event_rate | test | eq | `[[art:3b6b0a38:run.splits]]` | dangling |  |
| 51 | data_integrity | **Drift — unassessable.** No population stability index was… | 0.0095 | percent | event_rate |  | delta | `[[art:c2f664c6:run.metrics]]` | dangling |  |
| 52 | data_integrity | **Multicollinearity — measured, and incompletely controlled.… | 10 | ratio | vif | train | eq | `[[art:74c10f15:run.model_summary#removed]]` | dangling |  |
| 53 | data_integrity | **Multicollinearity — measured, and incompletely controlled.… | 160.89 | ratio | vif | train | eq | `[[art:74c10f15:run.model_summary#removed]]` | dangling |  |
| 54 | data_integrity | **Multicollinearity — measured, and incompletely controlled.… | 36.36 | ratio | vif | train | eq | `[[art:74c10f15:run.model_summary#removed]]` | dangling |  |
| 55 | data_integrity | **Multicollinearity — measured, and incompletely controlled.… | 10 | ratio | vif |  | eq |  | unsupported |  |
| 56 | outcomes | **Discrimination.** Test AUC is 0.7446 against train AUC 0.7… | 0.7446 | ratio | auc | test | eq | `[[art:c2f664c6:run.metrics]]` | dangling |  |
| 57 | outcomes | **Discrimination.** Test AUC is 0.7446 against train AUC 0.7… | 0.7584 | ratio | auc | train | eq | `[[art:c2f664c6:run.metrics]]` | dangling |  |
| 58 | outcomes | **Discrimination.** Test AUC is 0.7446 against train AUC 0.7… | 0.0138 | ratio | delta_auc |  | delta | `[[art:c2f664c6:run.metrics]]` | dangling |  |
| 59 | outcomes | **Discrimination.** Test AUC is 0.7446 against train AUC 0.7… | 0.4451 | ratio | ks | train | eq |  | unsupported |  |
| 60 | outcomes | **Discrimination.** Test AUC is 0.7446 against train AUC 0.7… | 0.41 | ratio | ks | test | eq |  | unsupported |  |
| 61 | outcomes | **Discrimination.** Test AUC is 0.7446 against train AUC 0.7… | 0.0351 | ratio | delta_ks |  | delta |  | unsupported |  |
| 62 | outcomes | **Discrimination.** Test AUC is 0.7446 against train AUC 0.7… | 0.5169 | ratio | gini | train | eq |  | unsupported |  |
| 63 | outcomes | **Discrimination.** Test AUC is 0.7446 against train AUC 0.7… | 0.4893 | ratio | gini | test | eq |  | unsupported |  |
| 64 | outcomes | **Discrimination.** Test AUC is 0.7446 against train AUC 0.7… | 0.0276 | ratio | delta_gini |  | delta |  | unsupported |  |
| 65 | outcomes | **Discrimination.** Test AUC is 0.7446 against train AUC 0.7… | 0.465 | ratio | log_loss | train | eq |  | unsupported |  |
| 66 | outcomes | **Discrimination.** Test AUC is 0.7446 against train AUC 0.7… | 0.4684 | ratio | log_loss | test | eq |  | unsupported |  |
| 67 | outcomes | **Discrimination.** Test AUC is 0.7446 against train AUC 0.7… | 0.1489 | ratio | brier | train | eq |  | unsupported |  |
| 68 | outcomes | **Discrimination.** Test AUC is 0.7446 against train AUC 0.7… | 0.1494 | ratio | brier | test | eq |  | unsupported |  |
| 69 | outcomes | **Discrimination.** Test AUC is 0.7446 against train AUC 0.7… | 1.4 | ratio | delta_auc |  | delta |  | unsupported |  |
| 70 | outcomes | **Discrimination.** Test AUC is 0.7446 against train AUC 0.7… | 3500 | count | n_rows | train | eq |  | unsupported |  |
| 71 | outcomes | **Calibration.** On train, mean predicted probability is 0.2… | 0.224623 | ratio | mean_predicted | train | eq |  | unsupported |  |
| 72 | outcomes | **Calibration.** On train, mean predicted probability is 0.2… | 0.224571 | ratio | event_rate | train | eq |  | unsupported |  |
| 73 | outcomes | **Calibration.** On train, mean predicted probability is 0.2… | 0.212653 | ratio | mean_predicted | test | eq |  | unsupported |  |
| 74 | outcomes | **Calibration.** On train, mean predicted probability is 0.2… | 0.224667 | ratio | event_rate | test | eq |  | unsupported |  |
| 75 | outcomes | **Calibration.** On train, mean predicted probability is 0.2… | 1.2 | ratio | calibration_gap | test | delta |  | unsupported |  |
| 76 | outcomes | **Calibration.** On train, mean predicted probability is 0.2… | 0.9465 | ratio | calibration_ratio | test | ratio |  | unsupported |  |
| 77 | outcomes | **Calibration.** On train, mean predicted probability is 0.2… | 5.35 | percent | calibration_ratio | test | eq |  | unsupported |  |
| 78 | outcomes | **Calibration.** On train, mean predicted probability is 0.2… | 5 | percent | calibration_ratio | test | eq |  | unsupported |  |
| 79 | outcomes | The magnitude is modest and may be partly a 1,500-row sampli… | 1500 | count | n_rows | test | eq |  | unsupported |  |
| 80 | sensitivity | - Stressing `delinq_max_6m` upward — a worsening worst-delin… | 0.0322 | ratio |  |  | eq |  | unattributed |  |
| 81 | sensitivity | - Stressing `limit_bal` upward *raises* predicted default (+… | 0.0727 | ratio | coefficient |  | eq |  | unsupported |  |
| 82 | sensitivity | - `pay_ratio_last` (+0.1026) and `pay_ratio_mean_6m` (−0.355… | 0.1026 | ratio | coefficient |  | eq |  | unsupported |  |
| 83 | sensitivity | - `pay_ratio_last` (+0.1026) and `pay_ratio_mean_6m` (−0.355… | 0.3554 | ratio |  |  | eq |  | unattributed |  |
| 84 | findings | 1. **Resolve the sign anomalies before any interpretive use… | 5 | ratio | vif |  | eq |  | unsupported |  |
| 85 | findings | 3. **Produce a calibration assessment and correct the test-s… | 5.35 | percent |  | test | eq |  | unsupported |  |
| 86 | findings | 5. **Profile the test split and document the transformations… | 2 | ratio |  | test | eq |  | unsupported |  |
| 87 | findings | On current evidence the model's discrimination is sound and… | 1 | ratio |  |  | eq |  | unsupported |  |
| 88 | findings | On current evidence the model's discrimination is sound and… | 3 | ratio |  |  | eq |  | unsupported |  |
| 89 | monitoring | **Monthly.** Score-distribution PSI against the frozen devel… | 0.1 | ratio | psi |  | eq |  | unsupported |  |
| 90 | monitoring | **Monthly.** Score-distribution PSI against the frozen devel… | 0.25 | ratio | psi |  | eq |  | unsupported |  |
| 91 | monitoring | **Monthly.** Score-distribution PSI against the frozen devel… | 0.9 | ratio | predicted_to_observed |  | eq |  | unsupported |  |
| 92 | monitoring | **Monthly.** Score-distribution PSI against the frozen devel… | 1.1 | ratio | predicted_to_observed |  | eq |  | unsupported |  |
| 93 | monitoring | **Monthly.** Score-distribution PSI against the frozen devel… | 0.9465 | ratio | predicted_to_observed | test | eq |  | unsupported |  |
| 94 | monitoring | **Quarterly.** Feature-level PSI for each of the ten retaine… | 0.7446 | ratio | auc | test | eq |  | unsupported |  |
| 95 | monitoring | **Quarterly.** Feature-level PSI for each of the ten retaine… | 0.4893 | ratio | gini | test | eq |  | unsupported |  |
| 96 | monitoring | **Quarterly.** Feature-level PSI for each of the ten retaine… | 0.41 | ratio | ks | test | eq |  | unsupported |  |
| 97 | monitoring | **Quarterly.** Feature-level PSI for each of the ten retaine… | 0.05 | ratio | delta_auc |  | eq |  | unsupported |  |
| 98 | monitoring | **Quarterly.** Feature-level PSI for each of the ten retaine… | 0.8 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 99 | monitoring | **Quarterly.** Feature-level PSI for each of the ten retaine… | 1.2 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 100 | monitoring | **Immediate triggers for off-cycle review.** Any coefficient… | 0.25 | ratio | psi |  | eq |  | unsupported |  |
| 101 | monitoring | **Immediate triggers for off-cycle review.** Any coefficient… | 0.85 | ratio | predicted_to_observed |  | eq |  | unsupported |  |
| 102 | monitoring | **Immediate triggers for off-cycle review.** Any coefficient… | 1.15 | ratio | predicted_to_observed |  | eq |  | unsupported |  |
| 103 | monitoring | **Immediate triggers for off-cycle review.** Any coefficient… | 22.5 | percent | event_rate | train | eq |  | unsupported |  |

## Appendix B — Artifact index

The store holds 14 artifacts; the 11 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `run.data_test` | `3b63748c` | table | table, 1500 rows | the subject's data_test.csv |
| `run.data_train` | `6a89f2be` | table | table, 3500 rows | the subject's data_train.csv |
| `run.duration_s` | `1742051a` | scalar | 1.389325834 | subject wall-clock seconds |
| `run.features` | `abbb748e` | json | json | the subject's features.json |
| `run.metrics` | `c2f664c6` | json | json | the subject's metrics.json |
| `run.model_summary` | `74c10f15` | json | json | the subject's model_summary.json |
| `run.predictions_test` | `d612396b` | table | table, 1500 rows | the subject's predictions_test.csv |
| `run.predictions_train` | `6fd8f98a` | table | table, 3500 rows | the subject's predictions_train.csv |
| `run.splits` | `3b6b0a38` | json | json | the subject's splits.json |
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
| tokens in / out | 59,720 / 35,500 |
| notional cost (USD) | 1.4690 |
| wall-clock (s) | 433.05 |
| subject run (s) | 1.39 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | credit_default-plain_llm-20260918T082409Z-6e98ce62 |

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
