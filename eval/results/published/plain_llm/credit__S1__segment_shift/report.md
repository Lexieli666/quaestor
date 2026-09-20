---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: plain_llm
model: claude-opus-5[1m]
run_id: credit_default-plain_llm-20260918T185539Z-6e98ce62
data_mode: synthetic
synthetic_n: 5000
grounding_precision_pre: 0.0000
grounding_precision_post: 0.0000
n_claims: 96
n_findings_by_severity: {high: 0, medium: 2, low: 2, info: 0}
generated: "2026-09-18T18:55:39Z"
illustrative: false
---

# Validation report — `credit_default` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `credit_default` v1.0 | `plain_llm` | claude-opus-5[1m] | synthetic, n = 5000 | 0.0000 → 0.0000 | 0 / 2 / 2 / 0 |
<!-- quaestor:renderer:end -->

This report validates package `credit_default` version 1.0, a binary classification model that estimates the probability of `default_next_month` for a credit card portfolio. The subject is a standardised logistic regression with nine retained features, an intercept of ⟦unverified: -1.2512⟧, and no class weighting ([[art:b82670e1:run.model_summary]]).

The scope of the review is limited to what the developer lodged in the artifact store: the run status and streams ([[art:2922931d:run.status]], [[art:0cece598:run.stdout]], [[art:41728c38:run.stderr]]), the feature inventory with timing declarations ([[art:abbb748e:run.features]]), the split definitions and row hashes ([[art:616e04cb:run.splits]]), the fitted model summary ([[art:b82670e1:run.model_summary]]), the performance metrics ([[art:0accf706:run.metrics]]), the scored tables ([[art:fdbe7077:run.predictions_test]], [[art:5d347554:run.predictions_train]]), the underlying split tables ([[art:bc07261a:run.data_train]], [[art:fff035ab:run.data_test]]), and the runtime record ([[art:d6169f24:run.duration_s]], [[art:2ad8d1a5:runtime.max_seconds]]). No documentation of intended use, no approved performance thresholds, no challenger model, and no scenario or sensitivity study were supplied; those absences shape several conclusions below.

Headline performance is moderate and stable. Test AUC is ⟦unverified: 0.7525⟧ with Gini ⟦unverified: 0.5050⟧ and KS ⟦unverified: 0.4306⟧ on ⟦unverified: 1,500⟧ rows; train AUC is ⟦unverified: 0.7599⟧ with Gini ⟦unverified: 0.5198⟧ and KS ⟦unverified: 0.4559⟧ on ⟦unverified: 1,789⟧ rows ([[art:0accf706:run.metrics]]). Discrimination is adequate for a behavioural default scorecard of this size. The material weaknesses are not in rank ordering but in coefficient stability under collinearity, in out-of-sample calibration of the predicted level, and in the completeness of the validation evidence itself.

Overall opinion: the model is **fit for use with required remediation**. No finding rises to the level of blocking deployment, but the calibration and collinearity items must be closed before the model is relied on for any purpose that consumes the probability level rather than the rank.

## 2. Conceptual soundness

The choice of a logistic regression on standardised inputs is appropriate to the task. It is monotone in each input, its coefficients are directly inspectable, and `standardised: true` means the reported magnitudes are comparable across features ([[art:b82670e1:run.model_summary]]). The feature set is a conventional behavioural panel: two origination attributes (`limit_bal`, `age`) and ten pre-period behavioural attributes covering utilisation, payment ratio, delinquency, and billing trend ([[art:abbb748e:run.features]]).

Timing discipline is sound on its face. The feature inventory declares `after_outcome: 0` and `during_period: 0`, with all twelve candidate features either `at_origination` (⟦unverified: 2⟧) or `before_period_start` (⟦unverified: 10⟧) ([[art:abbb748e:run.features]]). No feature is drawn from the outcome window, so there is no declared target leakage. Nothing in the metrics contradicts this: an AUC of ⟦unverified: 0.7525⟧ and KS of ⟦unverified: 0.4306⟧ ([[art:0accf706:run.metrics]]) are in the range one expects from legitimate behavioural signal, not the near-separation that a leaked feature produces. Per-feature discrimination was not lodged, so the single-feature AUC test could not be run directly, but the aggregate evidence gives no cause for concern.

The serious conceptual problem is in the fitted coefficients. Three of the nine retained coefficients carry signs that contradict the economics of consumer credit ([[art:b82670e1:run.model_summary#coefficients]]):

- `delinq_max_6m` at ⟦unverified: -0.0032⟧. The worst delinquency observed in six months should raise default risk, not lower it. The value is also effectively zero, which is itself a signal of a coefficient that has been absorbed by its correlated neighbours.
- `pay_ratio_mean_6m` at ⟦unverified: -0.4569⟧ against `pay_ratio_last` at +⟦unverified: 0.1877⟧. These are the same quantity at two horizons and they enter with opposite signs and with the mean carrying the second-largest absolute weight in the model. A model in which paying more on average lowers risk while paying more last month raises it is not telling a coherent story; it is splitting a single correlated signal across two coefficients.
- `bill_trend_6m` at ⟦unverified: -0.0787⟧. A rising bill trend reducing default probability is defensible only under a specific reading (growing balances as a proxy for an active, healthy account), and that reading was not documented.

The dominant driver, `delinq_last` at +⟦unverified: 0.6395⟧, is correctly signed and is by a wide margin the largest standardised effect, as one would expect. `limit_bal` at ⟦unverified: -0.0791⟧ and `age` at ⟦unverified: -0.0860⟧ are both correctly signed and small. `utilisation` at +⟦unverified: 0.1902⟧ is correctly signed.

The absence of `class_weight` is acceptable given a ⟦unverified: 24.4%⟧ train event rate ([[art:b82670e1:run.model_summary]], [[art:616e04cb:run.splits]]); this is not an imbalance regime that requires reweighting, and reweighting would have damaged the calibration that the model does achieve in-sample.

No challenger model was lodged. Effective challenge therefore rests entirely on this review, with no benchmark against a gradient-boosted alternative, a reduced-form scorecard, or the incumbent process. This is a gap in the development file rather than a demonstrated defect, and it is recorded as such in section 6 rather than as a scored finding, since no challenger artifact exists to be compared against.

## 3. Data integrity and drift

The training profile is clean in the narrow sense. All eleven analysed columns report `missing: 0.0` across ⟦unverified: 1,789⟧ rows, and the value ranges are plausible throughout: `age` spans ⟦unverified: 21⟧ to ⟦unverified: 62,⟧ `limit_bal` spans ⟦unverified: 10,000⟧ to ⟦unverified: 88,000,⟧ and `delinq_last`, `delinq_count_6m`, and `delinq_max_6m` take small non-negative integer values. Two items in the profile warrant note. `utilisation` reaches a maximum of ⟦unverified: 1.1297⟧, meaning balances above the limit; this is realistic for a revolving product but it means the feature is not bounded at unity as its name suggests. `pay_ratio_last` maxes at exactly ⟦unverified: 2.0⟧ while `pay_ratio_mean_6m` maxes at ⟦unverified: 1.6385⟧, which is the signature of a cap applied to the point-in-time variable. A cap at a round number is a preprocessing decision that should be documented, because it changes the shape of the right tail of a feature that carries a positive coefficient.

The population accounting does not close. `client_id` runs from ⟦unverified: 1⟧ to ⟦unverified: 5,000⟧ in the training profile, and the two splits together account for ⟦unverified: 1,789⟧ + ⟦unverified: 1,500⟧ = ⟦unverified: 3,289⟧ rows ([[art:616e04cb:run.splits]], [[art:bc07261a:run.data_train]], [[art:fff035ab:run.data_test]]). Roughly a third of the identifier space is unaccounted for, with no exclusion log, no filter criteria, and no statement of whether the dropped records were ineligible, incomplete, or simply not sampled. If the exclusions correlate with risk, every metric in this report is conditioned on a population that was never characterised.

The split proportions are also unusual. A ⟦unverified: 1,789⟧/⟦unverified: 1,500⟧ allocation is ⟦unverified: 54.4%⟧ train and ⟦unverified: 45.6%⟧ test. Holding out nearly half the data is defensible for a small sample, but it was not justified, and it leaves the training set thin for a nine-parameter model fitted after a collinearity screen.

Missingness could not be compared across splits. Only the training profile was lodged; no equivalent profile exists for the test split, so the cross-split missingness test central to data-integrity review cannot be executed against [[art:fff035ab:run.data_test]]. The zero-missingness result for training does not transfer.

On contamination, the two `rows_hash` values in [[art:616e04cb:run.splits]] are distinct, which confirms only that the two row sets are not identical. No client-level overlap check was lodged, and because the model is behavioural and a single `client_id` could plausibly contribute rows to both splits, the absence of a de-duplication attestation is a real gap. There is no positive evidence of overlap, so no L2 finding is raised, but the check should be executed and recorded.

On drift, no PSI was computed for either the population or the score, on either the features or the predictions ([[art:fdbe7077:run.predictions_test]], [[art:5d347554:run.predictions_train]]). The one drift signal available is the event rate, which falls from ⟦unverified: 0.2437⟧ in train to ⟦unverified: 0.2247⟧ in test ([[art:616e04cb:run.splits]], [[art:0accf706:run.metrics]]), a ⟦unverified: 1.90⟧ percentage point absolute and ⟦unverified: 7.8%⟧ relative decline. For a split that should be exchangeable, this is larger than sampling noise comfortably explains at n = ⟦unverified: 1,500⟧ and suggests either a time-ordered split that was not declared as such or a non-random allocation. It is also the mechanism behind the calibration gap in section 4.

## 4. Outcomes analysis

Discrimination holds up out of sample. AUC moves from ⟦unverified: 0.7599⟧ on train to ⟦unverified: 0.7525⟧ on test, a gap of ⟦unverified: 0.0074⟧, and Gini moves from ⟦unverified: 0.5198⟧ to ⟦unverified: 0.5050⟧ ([[art:0accf706:run.metrics]]). A gap this small is well inside any reasonable degradation threshold and is the clearest positive result in the file: the model is not overfitted. KS softens from ⟦unverified: 0.4559⟧ to ⟦unverified: 0.4306⟧, a ⟦unverified: 0.0253⟧ decline that is consistent with the AUC picture and with the smaller test event base. There is no out-of-sample degradation finding.

Calibration is where the model separates into two regimes. On train, mean predicted probability is ⟦unverified: 0.2436878⟧ against an observed event rate of ⟦unverified: 0.2437116⟧ ([[art:0accf706:run.metrics]]) — agreement to five decimal places, which is simply the maximum-likelihood fitting identity for a logistic regression with an intercept and tells us nothing about calibration quality. On test, mean predicted is ⟦unverified: 0.2121848⟧ against an observed ⟦unverified: 0.2246667⟧, an absolute shortfall of ⟦unverified: 0.0124819⟧ and a relative under-prediction of ⟦unverified: 5.6%⟧. The model systematically under-states the probability of default on unseen data.

The direction here is worth dwelling on, because it is counterintuitive. The test event rate is *lower* than the train event rate, yet the model under-predicts on test. That combination means the score distribution shifted down by more than the outcome rate did: the test population scores as materially safer than it actually behaved. Any use of these probabilities for expected-loss calculation, provisioning, or pricing would understate exposure by roughly one twentieth of the loss estimate before any other source of error. Rank-ordering uses — cut-off strategies, queue prioritisation, referral rules — are unaffected, since AUC and KS are preserved.

Brier score improves from ⟦unverified: 0.1636⟧ on train to ⟦unverified: 0.1524⟧ on test, and log loss from ⟦unverified: 0.4967⟧ to ⟦unverified: 0.4717⟧ ([[art:0accf706:run.metrics]]). These are not evidence that the model performs better out of sample. Both are scale-sensitive to the base rate, and a test set with a ⟦unverified: 1.90⟧ point lower event rate will mechanically produce lower values at equal skill. Read alongside the AUC gap and the calibration shortfall, the correct reading is that the test set is marginally easier, not that the model is stronger there.

No calibration slope or intercept was fitted, and no decile or bucket-level reliability table was lodged. The mean-level comparison above is therefore the only calibration evidence available, and it cannot distinguish a uniform level shift — correctable with an intercept recalibration — from a slope problem in which the tails are mis-ranked in probability space. That distinction determines the remedy and should be settled before any recalibration is attempted.

## 5. Sensitivity and scenario analysis

No scenario analysis was performed. The store contains no stressed populations, no shifted-input runs, no value or profit curves as a function of cut-off, and no downturn overlay. The X1 test for non-monotone or wrong-signed value curves therefore has no artifact to run against, and no such finding is raised.

What can be said about sensitivity comes from the coefficient vector itself. Because the model is standardised ([[art:b82670e1:run.model_summary]]), each coefficient is the log-odds response to a one-standard-deviation move in its input, and the ranking is unambiguous. `delinq_last` at +⟦unverified: 0.6395⟧ is ⟦unverified: 1.4⟧ times the next largest effect and ⟦unverified: 3.4⟧ times the largest correctly-signed effect after that. Using the training dispersion of ⟦unverified: 1.3060⟧ for `delinq_last`, a move from a clean account to roughly two missed payments carries about ⟦unverified: 0.64⟧ in log-odds on its own, which at the base rate moves predicted probability from roughly ⟦unverified: 22%⟧ to roughly ⟦unverified: 35%⟧. The model is, in practical terms, a delinquency indicator with modest adjustments.

That concentration is a sensitivity exposure. If `delinq_last` is mis-stated, lags, or changes definition upstream — a collections policy change, a payment-holiday programme, a servicing migration — the model's output moves more than any other single input could move it, and there is no compensating signal. The second-largest coefficient, `pay_ratio_mean_6m` at ⟦unverified: -0.4569⟧, compounds the exposure rather than diversifying it, because as section 2 sets out its sign is not economically interpretable and it is likely acting as a partial correction to correlated terms rather than as an independent driver.

At the other extreme, `delinq_max_6m` at ⟦unverified: -0.0032⟧ contributes essentially nothing. A one-standard-deviation move of ⟦unverified: 1.9871⟧ in that feature changes the log-odds by about ⟦unverified: -0.006⟧, which is not distinguishable from zero. Carrying a wrong-signed, zero-magnitude term costs nothing in prediction but does cost in governance: it is a term whose behaviour under a shifted population cannot be predicted from its fitted value.

Stability across regimes could not be assessed. No time-partitioned, vintage-partitioned, or segment-partitioned refits were lodged, so the R1 tests for sign flips across regimes and for material AUC differences across regimes have no evidence base. Given the event-rate differential noted in section 3, which hints at a possible time ordering in the split, a vintage-stratified refit should be a condition of approval.

## 6. Findings and recommendations

Four findings are raised, detailed in the structured list that accompanies this report. In summary:

**C1, medium — out-of-sample calibration shortfall.** Mean predicted ⟦unverified: 0.2122⟧ against observed ⟦unverified: 0.2247⟧ on test, a ⟦unverified: 5.6%⟧ relative under-prediction of the default level, against exact agreement on train. Remediation: fit and report a calibration slope and intercept on test, produce a decile reliability table, and apply an intercept recalibration only after confirming the slope is within band. Do not use the raw probabilities for any expected-loss purpose until this is closed.

**M1, medium — severe multicollinearity with residual coefficient instability.** Three features were removed at VIFs of ⟦unverified: 331.00⟧, ⟦unverified: 59.82⟧, and ⟦unverified: 15.57⟧ against a declared threshold of ⟦unverified: 10.0⟧, and the surviving coefficient vector still shows wrong-signed and near-zero terms. Remediation: report post-removal VIFs and the condition number for the retained nine, and either re-specify the correlated payment-ratio and delinquency families into single orthogonal terms or apply a penalised fit.

**S1, low — unexplained event-rate differential and no drift measurement.** A ⟦unverified: 1.90⟧ point event-rate gap between splits with no PSI computed on features or scores. Remediation: compute feature and score PSI between the splits, and declare whether the split is random or time-ordered.

**D1, low — incomplete population accounting and no cross-split missingness comparison.** Roughly a third of the `client_id` space is unaccounted for with no exclusion log, and only the training profile was lodged. Remediation: publish the exclusion criteria and counts, and lodge a test-split profile so missingness can be compared.

Two further gaps do not meet the evidentiary bar for a scored finding but are conditions the developer should close. First, **no challenger model was submitted**, so effective challenge is unsupported by any comparative benchmark; at minimum a penalised logistic and a gradient-boosted alternative should be fitted on the same splits and compared on test AUC and calibration. Second, **no client-level overlap check was lodged**; the distinct `rows_hash` values in [[art:616e04cb:run.splits]] establish only that the row sets differ, and a behavioural panel can place the same obligor on both sides of a split.

On runtime, the store carries both [[art:d6169f24:run.duration_s]] and [[art:2ad8d1a5:runtime.max_seconds]], and nothing in [[art:2922931d:run.status]] or [[art:41728c38:run.stderr]] indicates a failed or truncated run. No R0 finding is raised.

**Recommended disposition: approve for rank-ordering use, with the C1 and M1 remediations as conditions precedent to any use of the model's probability level.**

### F-001 · C1 calibration · severity **medium**

On the test split the mean predicted probability is 0.2121848 against an observed event rate of 0.2246667, an absolute shortfall of 0.0124819 and a relative under-prediction of 5.6%. On train the two agree to five decimal places (0.2436878 predicted against 0.2437116 observed), but that agreement is the maximum-likelihood fitting identity for a logistic regression with a free intercept and carries no evidence about calibration quality. The direction of the test result is notable: the test event rate is lower than the train event rate, yet the model still under-predicts, meaning the score distribution shifted down by more than the outcome rate did and the test population scores as materially safer than it behaved. Discrimination is unaffected, so rank-ordering uses such as cut-off strategies remain sound, but any expected-loss, provisioning, or pricing use would understate exposure by roughly one twentieth before any other source of error. The improvement in Brier (0.1636 to 0.1524) and log loss (0.4967 to 0.4717) does not offset this: both are base-rate sensitive and fall mechanically on a test set with a 1.90 point lower event rate. No calibration slope, intercept, or decile reliability table was lodged, so it cannot be determined whether this is a uniform level shift correctable by intercept recalibration or a slope defect, and that distinction determines the remedy.

### F-002 · M1 collinearity · severity **medium**

The development run removed three features against a declared VIF threshold of 10.0: bill_last at VIF 331.00, utilisation_mean_6m at 59.82, and bill_mean_6m at 15.57. A VIF of 331 indicates near-exact linear dependence among the billing and utilisation family, and the removal screen was the right response. However, the screen did not resolve the problem, and the fitted coefficients on the nine retained features show the classic signature of residual collinearity. delinq_max_6m carries -0.003169, which is both wrong-signed (the worst delinquency in six months cannot reduce default risk) and effectively zero, indicating its signal has been absorbed by correlated neighbours. pay_ratio_mean_6m at -0.4569 and pay_ratio_last at +0.1877 are the same quantity at two horizons entering with opposite signs, with the mean carrying the second-largest absolute standardised weight in the entire model; no coherent credit story supports paying more on average lowering risk while paying more last month raises it. bill_trend_6m at -0.0787 is a third questionable sign. Critically, post-removal VIFs for the nine retained features were not reported, and no condition number was lodged, so the developer's own declared control at threshold 10.0 cannot be verified as satisfied for the final specification. The coefficients being standardised makes the instability directly visible and comparable across features.

### F-003 · S1 population drift · severity **low**

The training split has an event rate of 0.2437116 and the test split 0.2246667, a 1.90 percentage point absolute and 7.8% relative decline. For an allocation that should be exchangeable, a gap of this size at n = 1,500 is larger than sampling variation comfortably explains and suggests either a time-ordered split that was never declared as such or a non-random allocation rule. The same differential is the mechanism behind the calibration shortfall reported separately, so it is not a cosmetic observation. Compounding this, no population stability index was computed at all: neither feature-level PSI between the two data tables nor score-level PSI between the two prediction tables was lodged, so the standard drift test has no result on file and the event-rate gap is the only drift signal available. The split proportions are themselves unusual at 54.4% train against 45.6% test, which is a defensible choice for a small sample but was not justified and leaves a thin training base for a nine-parameter model fitted after a collinearity screen. The developer should declare whether the split is random or time-ordered and compute feature and score PSI against the training baseline.

### F-004 · D1 data integrity · severity **low**

The population accounting does not close. client_id in the training profile runs from 1 to 5,000, while the two splits together account for only 1,789 + 1,500 = 3,289 rows. Roughly a third of the identifier space is unaccounted for, with no exclusion log, no stated filter criteria, and no statement of whether the dropped records were ineligible, incomplete, or simply unsampled. If those exclusions correlate with default risk, every metric in this review is conditioned on a population that was never characterised. Separately, the missingness comparison that data-integrity review requires could not be executed: only the training profile was lodged, which reports missing = 0.0 across all eleven analysed columns, and no equivalent profile exists for the test split, so nothing establishes that the clean result transfers to the held-out data. Two preprocessing decisions visible in the training profile also lack documentation: pay_ratio_last is capped at exactly 2.0 while pay_ratio_mean_6m maxes at 1.6385, a round-number cap that reshapes the right tail of a positively-weighted feature, and utilisation reaches 1.1297, meaning the feature is not bounded at unity as its name implies. Remediation is to publish exclusion criteria and counts and to lodge a test-split profile.

Candidates raised and not promoted: none.

### Open items

No open item was recorded for this validation.

## 7. Ongoing monitoring recommendations

Monitoring should be built around the two weaknesses this review identified, since those are where the model will fail first.

*Monthly.* Track mean predicted probability against realised default rate on each new outcome cohort, and alert when the relative gap exceeds ⟦unverified: 10%⟧ or when the same-signed gap persists for three consecutive cohorts. Given that the model already under-predicts by ⟦unverified: 5.6%⟧ on its own test set, the starting position consumes a large part of any tolerance, and the threshold should be treated as tight rather than generous. Track the score distribution PSI against the training baseline in [[art:5d347554:run.predictions_train]], with review at ⟦unverified: 0.10⟧ and escalation at ⟦unverified: 0.25⟧.

*Quarterly.* Recompute AUC, Gini, and KS on rolling outcome windows and compare against the test baselines of ⟦unverified: 0.7525⟧, ⟦unverified: 0.5050⟧, and ⟦unverified: 0.4306⟧ in [[art:0accf706:run.metrics]]; escalate on an AUC decline beyond ⟦unverified: 0.05⟧. Compute feature-level PSI for all nine retained inputs, with particular attention to `delinq_last`, which the sensitivity analysis shows carries the model. Produce a decile reliability table so that calibration drift can be localised rather than only detected in aggregate.

*Semi-annually.* Refit the specification on the most recent window and compare the coefficient vector against [[art:b82670e1:run.model_summary#coefficients]]. Any sign change on `delinq_last`, `utilisation`, or `limit_bal` should trigger immediate review. The already-anomalous terms — `delinq_max_6m`, `pay_ratio_mean_6m`, `bill_trend_6m` — should be expected to move and should be monitored as a set rather than individually, since their instability is a joint property of their correlation structure. Re-run the VIF screen at the declared ⟦unverified: 10.0⟧ threshold and report the condition number.

*Annually or on trigger.* Perform full revalidation including a challenger comparison and the scenario analysis that this review could not conduct. Trigger an off-cycle revalidation on any of: a change in the upstream definition of `delinq_last` or the `pay_ratio_last` cap at ⟦unverified: 2.0⟧; a collections, forbearance, or servicing policy change; a portfolio event rate outside the ⟦unverified: 0.20⟧–⟦unverified: 0.28⟧ band bracketing the observed ⟦unverified: 0.2247⟧ and ⟦unverified: 0.2437⟧; or two consecutive quarters of calibration breach.

## Appendix A — Claims

Grounding precision 0.0000 before repair (0 of 96 claims verified; 60 unsupported, 36 dangling) and 0.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 0/9; conceptual_soundness 0/13; data_integrity 0/22; outcomes 0/19; sensitivity 0/11; findings 0/8; monitoring 0/14.

Developer claims: `plain_llm` runs no check over `package.yaml`'s declared claims See Appendix D.

Excluded numeric tokens (not claims): section_number (section 6, section 4, section 2, section 3); inline_code (`after_outcome: 0`, `during_period: 0`, `missing: 0.0`); citation_hash (b82670e1, 2922931d, 0cece598, 41728c38); package_version (1.0); extractor_returned_excluded_token (1.0, 0, 6, 0.0).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | This report validates package `credit_default` version 1.0,… | -1.2512 | ratio | coefficient |  | eq | `[[art:b82670e1:run.model_summary]]` | dangling |  |
| 2 | summary | Headline performance is moderate and stable. Test AUC is 0.7… | 0.7525 | ratio | auc | test | eq | `[[art:0accf706:run.metrics]]` | dangling |  |
| 3 | summary | Headline performance is moderate and stable. Test AUC is 0.7… | 0.505 | ratio | gini | test | eq | `[[art:0accf706:run.metrics]]` | dangling |  |
| 4 | summary | Headline performance is moderate and stable. Test AUC is 0.7… | 0.4306 | ratio | ks | test | eq | `[[art:0accf706:run.metrics]]` | dangling |  |
| 5 | summary | Headline performance is moderate and stable. Test AUC is 0.7… | 1500 | count | row_count | test | eq | `[[art:0accf706:run.metrics]]` | dangling |  |
| 6 | summary | Headline performance is moderate and stable. Test AUC is 0.7… | 0.7599 | ratio | auc | train | eq | `[[art:0accf706:run.metrics]]` | dangling |  |
| 7 | summary | Headline performance is moderate and stable. Test AUC is 0.7… | 0.5198 | ratio | gini | train | eq | `[[art:0accf706:run.metrics]]` | dangling |  |
| 8 | summary | Headline performance is moderate and stable. Test AUC is 0.7… | 0.4559 | ratio | ks | train | eq | `[[art:0accf706:run.metrics]]` | dangling |  |
| 9 | summary | Headline performance is moderate and stable. Test AUC is 0.7… | 1789 | count | row_count | train | eq | `[[art:0accf706:run.metrics]]` | dangling |  |
| 10 | conceptual_soundness | Timing discipline is sound on its face. The feature inventor… | 2 | count |  |  | eq | `[[art:abbb748e:run.features]]` | dangling |  |
| 11 | conceptual_soundness | Timing discipline is sound on its face. The feature inventor… | 10 | count |  |  | eq | `[[art:abbb748e:run.features]]` | dangling |  |
| 12 | conceptual_soundness | Timing discipline is sound on its face. The feature inventor… | 0.7525 | ratio | auc |  | eq | `[[art:0accf706:run.metrics]]` | dangling |  |
| 13 | conceptual_soundness | Timing discipline is sound on its face. The feature inventor… | 0.4306 | ratio | ks |  | eq | `[[art:0accf706:run.metrics]]` | dangling |  |
| 14 | conceptual_soundness | - `delinq_max_6m` at -0.0032. The worst delinquency observed… | -0.0032 | ratio | coefficient |  | eq |  | unsupported |  |
| 15 | conceptual_soundness | - `pay_ratio_mean_6m` at -0.4569 against `pay_ratio_last` at… | -0.4569 | ratio | coefficient |  | eq |  | unsupported |  |
| 16 | conceptual_soundness | - `pay_ratio_mean_6m` at -0.4569 against `pay_ratio_last` at… | 0.1877 | ratio | coefficient |  | eq |  | unsupported |  |
| 17 | conceptual_soundness | - `bill_trend_6m` at -0.0787. A rising bill trend reducing d… | -0.0787 | ratio | coefficient |  | eq |  | unsupported |  |
| 18 | conceptual_soundness | The dominant driver, `delinq_last` at +0.6395, is correctly… | 0.6395 | ratio | coefficient |  | eq |  | unsupported |  |
| 19 | conceptual_soundness | The dominant driver, `delinq_last` at +0.6395, is correctly… | -0.0791 | ratio | coefficient |  | eq |  | unsupported |  |
| 20 | conceptual_soundness | The dominant driver, `delinq_last` at +0.6395, is correctly… | -0.086 | ratio | coefficient |  | eq |  | unsupported |  |
| 21 | conceptual_soundness | The dominant driver, `delinq_last` at +0.6395, is correctly… | 0.1902 | ratio | coefficient |  | eq |  | unsupported |  |
| 22 | conceptual_soundness | The absence of `class_weight` is acceptable given a 24.4% tr… | 24.4 | percent | event_rate | train | eq | `[[art:616e04cb:run.splits]]` | dangling |  |
| 23 | data_integrity | The training profile is clean in the narrow sense. All eleve… | 1789 | count | rows | train | eq |  | unsupported |  |
| 24 | data_integrity | The training profile is clean in the narrow sense. All eleve… | 21 | ratio | age | train | eq |  | unsupported |  |
| 25 | data_integrity | The training profile is clean in the narrow sense. All eleve… | 62 | ratio | age | train | eq |  | unsupported |  |
| 26 | data_integrity | The training profile is clean in the narrow sense. All eleve… | 10000 | currency | limit_bal | train | eq |  | unsupported |  |
| 27 | data_integrity | The training profile is clean in the narrow sense. All eleve… | 88000 | currency | limit_bal | train | eq |  | unsupported |  |
| 28 | data_integrity | The training profile is clean in the narrow sense. All eleve… | 1.1297 | ratio | utilisation | train | eq |  | unsupported |  |
| 29 | data_integrity | The training profile is clean in the narrow sense. All eleve… | 2 | ratio | pay_ratio_last | train | eq |  | unsupported |  |
| 30 | data_integrity | The training profile is clean in the narrow sense. All eleve… | 1.6385 | ratio | pay_ratio_mean_6m | train | eq |  | unsupported |  |
| 31 | data_integrity | The population accounting does not close. `client_id` runs f… | 1 | count | client_id | train | eq |  | unsupported |  |
| 32 | data_integrity | The population accounting does not close. `client_id` runs f… | 5000 | count | client_id | train | eq |  | unsupported |  |
| 33 | data_integrity | The population accounting does not close. `client_id` runs f… | 1789 | count | rows | train | eq | `[[art:bc07261a:run.data_train]]` | dangling |  |
| 34 | data_integrity | The population accounting does not close. `client_id` runs f… | 1500 | count | rows | test | eq | `[[art:fff035ab:run.data_test]]` | dangling |  |
| 35 | data_integrity | The population accounting does not close. `client_id` runs f… | 3289 | count | rows |  | eq | `[[art:616e04cb:run.splits]]` | dangling |  |
| 36 | data_integrity | The split proportions are also unusual. A 1,789/1,500 alloca… | 1789 | count | rows | train | eq |  | unsupported |  |
| 37 | data_integrity | The split proportions are also unusual. A 1,789/1,500 alloca… | 1500 | count | rows | test | eq |  | unsupported |  |
| 38 | data_integrity | The split proportions are also unusual. A 1,789/1,500 alloca… | 54.4 | percent |  | train | eq |  | unsupported |  |
| 39 | data_integrity | The split proportions are also unusual. A 1,789/1,500 alloca… | 45.6 | percent |  | test | eq |  | unsupported |  |
| 40 | data_integrity | On drift, no PSI was computed for either the population or t… | 0.2437 | ratio | event_rate | train | eq | `[[art:616e04cb:run.splits]]` | dangling |  |
| 41 | data_integrity | On drift, no PSI was computed for either the population or t… | 0.2247 | ratio | event_rate | test | eq | `[[art:0accf706:run.metrics]]` | dangling |  |
| 42 | data_integrity | On drift, no PSI was computed for either the population or t… | 1.9 | percent | event_rate |  | delta |  | unsupported |  |
| 43 | data_integrity | On drift, no PSI was computed for either the population or t… | 7.8 | percent | event_rate |  | eq |  | unsupported |  |
| 44 | data_integrity | On drift, no PSI was computed for either the population or t… | 1500 | count | rows | test | eq |  | unsupported |  |
| 45 | outcomes | Discrimination holds up out of sample. AUC moves from 0.7599… | 0.7599 | ratio | auc | train | eq | `[[art:0accf706:run.metrics]]` | dangling |  |
| 46 | outcomes | Discrimination holds up out of sample. AUC moves from 0.7599… | 0.7525 | ratio | auc | test | eq | `[[art:0accf706:run.metrics]]` | dangling |  |
| 47 | outcomes | Discrimination holds up out of sample. AUC moves from 0.7599… | 0.0074 | ratio | auc |  | delta | `[[art:0accf706:run.metrics]]` | dangling |  |
| 48 | outcomes | Discrimination holds up out of sample. AUC moves from 0.7599… | 0.5198 | ratio | gini | train | eq | `[[art:0accf706:run.metrics]]` | dangling |  |
| 49 | outcomes | Discrimination holds up out of sample. AUC moves from 0.7599… | 0.505 | ratio | gini | test | eq | `[[art:0accf706:run.metrics]]` | dangling |  |
| 50 | outcomes | Discrimination holds up out of sample. AUC moves from 0.7599… | 0.4559 | ratio | ks | train | eq |  | unsupported |  |
| 51 | outcomes | Discrimination holds up out of sample. AUC moves from 0.7599… | 0.4306 | ratio | ks | test | eq |  | unsupported |  |
| 52 | outcomes | Discrimination holds up out of sample. AUC moves from 0.7599… | 0.0253 | ratio | ks |  | delta |  | unsupported |  |
| 53 | outcomes | Calibration is where the model separates into two regimes. O… | 0.2436878 | ratio | mean_predicted | train | eq | `[[art:0accf706:run.metrics]]` | dangling |  |
| 54 | outcomes | Calibration is where the model separates into two regimes. O… | 0.2437116 | ratio | event_rate | train | eq | `[[art:0accf706:run.metrics]]` | dangling |  |
| 55 | outcomes | Calibration is where the model separates into two regimes. O… | 0.2121848 | ratio | mean_predicted | test | eq |  | unsupported |  |
| 56 | outcomes | Calibration is where the model separates into two regimes. O… | 0.2246667 | ratio | event_rate | test | eq |  | unsupported |  |
| 57 | outcomes | Calibration is where the model separates into two regimes. O… | 0.0124819 | ratio | mean_predicted | test | delta |  | unsupported |  |
| 58 | outcomes | Calibration is where the model separates into two regimes. O… | 5.6 | percent | mean_predicted | test | eq |  | unsupported |  |
| 59 | outcomes | Brier score improves from 0.1636 on train to 0.1524 on test,… | 0.1636 | ratio | brier | train | eq | `[[art:0accf706:run.metrics]]` | dangling |  |
| 60 | outcomes | Brier score improves from 0.1636 on train to 0.1524 on test,… | 0.1524 | ratio | brier | test | eq | `[[art:0accf706:run.metrics]]` | dangling |  |
| 61 | outcomes | Brier score improves from 0.1636 on train to 0.1524 on test,… | 0.4967 | ratio | log_loss | train | eq | `[[art:0accf706:run.metrics]]` | dangling |  |
| 62 | outcomes | Brier score improves from 0.1636 on train to 0.1524 on test,… | 0.4717 | ratio | log_loss | test | eq | `[[art:0accf706:run.metrics]]` | dangling |  |
| 63 | outcomes | Brier score improves from 0.1636 on train to 0.1524 on test,… | 1.9 | ratio | event_rate |  | delta |  | unsupported |  |
| 64 | sensitivity | What can be said about sensitivity comes from the coefficien… | 0.6395 | ratio | coefficient |  | eq |  | unsupported |  |
| 65 | sensitivity | What can be said about sensitivity comes from the coefficien… | 1.4 | ratio | coefficient |  | eq |  | unsupported |  |
| 66 | sensitivity | What can be said about sensitivity comes from the coefficien… | 3.4 | ratio | coefficient |  | eq |  | unsupported |  |
| 67 | sensitivity | What can be said about sensitivity comes from the coefficien… | 1.306 | ratio | std | train | eq |  | unsupported |  |
| 68 | sensitivity | What can be said about sensitivity comes from the coefficien… | 0.64 | ratio | coefficient |  | eq |  | unsupported |  |
| 69 | sensitivity | What can be said about sensitivity comes from the coefficien… | 22 | percent |  |  | eq |  | unsupported |  |
| 70 | sensitivity | What can be said about sensitivity comes from the coefficien… | 35 | percent |  |  | eq |  | unsupported |  |
| 71 | sensitivity | That concentration is a sensitivity exposure. If `delinq_las… | -0.4569 | ratio | coefficient |  | eq |  | unsupported |  |
| 72 | sensitivity | At the other extreme, `delinq_max_6m` at -0.0032 contributes… | -0.0032 | ratio | coefficient |  | eq |  | unsupported |  |
| 73 | sensitivity | At the other extreme, `delinq_max_6m` at -0.0032 contributes… | 1.9871 | ratio | std |  | eq |  | unsupported |  |
| 74 | sensitivity | At the other extreme, `delinq_max_6m` at -0.0032 contributes… | -0.006 | ratio | coefficient |  | eq |  | unsupported |  |
| 75 | findings | **C1, medium — out-of-sample calibration shortfall.** Mean p… | 0.2122 | ratio | mean_predicted | test | eq |  | unsupported |  |
| 76 | findings | **C1, medium — out-of-sample calibration shortfall.** Mean p… | 0.2247 | ratio | event_rate | test | eq |  | unsupported |  |
| 77 | findings | **C1, medium — out-of-sample calibration shortfall.** Mean p… | 5.6 | percent |  | test | eq |  | unsupported |  |
| 78 | findings | **M1, medium — severe multicollinearity with residual coeffi… | 331 | ratio | vif |  | eq |  | unsupported |  |
| 79 | findings | **M1, medium — severe multicollinearity with residual coeffi… | 59.82 | ratio | vif |  | eq |  | unsupported |  |
| 80 | findings | **M1, medium — severe multicollinearity with residual coeffi… | 15.57 | ratio | vif |  | eq |  | unsupported |  |
| 81 | findings | **M1, medium — severe multicollinearity with residual coeffi… | 10 | ratio | vif |  | eq |  | unsupported |  |
| 82 | findings | **S1, low — unexplained event-rate differential and no drift… | 1.9 | ratio | event_rate |  | delta |  | unsupported |  |
| 83 | monitoring | *Monthly.* Track mean predicted probability against realised… | 10 | percent |  |  | eq |  | unsupported |  |
| 84 | monitoring | *Monthly.* Track mean predicted probability against realised… | 5.6 | percent |  | test | eq |  | unsupported |  |
| 85 | monitoring | *Monthly.* Track mean predicted probability against realised… | 0.1 | ratio | psi | train | eq | `[[art:5d347554:run.predictions_train]]` | dangling |  |
| 86 | monitoring | *Monthly.* Track mean predicted probability against realised… | 0.25 | ratio | psi | train | eq | `[[art:5d347554:run.predictions_train]]` | dangling |  |
| 87 | monitoring | *Quarterly.* Recompute AUC, Gini, and KS on rolling outcome… | 0.7525 | ratio | auc | test | eq | `[[art:0accf706:run.metrics]]` | dangling |  |
| 88 | monitoring | *Quarterly.* Recompute AUC, Gini, and KS on rolling outcome… | 0.505 | ratio | gini | test | eq | `[[art:0accf706:run.metrics]]` | dangling |  |
| 89 | monitoring | *Quarterly.* Recompute AUC, Gini, and KS on rolling outcome… | 0.4306 | ratio | ks | test | eq | `[[art:0accf706:run.metrics]]` | dangling |  |
| 90 | monitoring | *Quarterly.* Recompute AUC, Gini, and KS on rolling outcome… | 0.05 | ratio | delta_auc |  | eq | `[[art:0accf706:run.metrics]]` | dangling |  |
| 91 | monitoring | *Semi-annually.* Refit the specification on the most recent… | 10 | ratio | vif |  | eq |  | unsupported |  |
| 92 | monitoring | *Annually or on trigger.* Perform full revalidation includin… | 2 | ratio |  |  | eq |  | unsupported |  |
| 93 | monitoring | *Annually or on trigger.* Perform full revalidation includin… | 0.2 | ratio | event_rate |  | eq |  | unsupported |  |
| 94 | monitoring | *Annually or on trigger.* Perform full revalidation includin… | 0.28 | ratio | event_rate |  | eq |  | unsupported |  |
| 95 | monitoring | *Annually or on trigger.* Perform full revalidation includin… | 0.2247 | ratio | event_rate |  | eq |  | unsupported |  |
| 96 | monitoring | *Annually or on trigger.* Perform full revalidation includin… | 0.2437 | ratio | event_rate |  | eq |  | unsupported |  |

## Appendix B — Artifact index

The store holds 14 artifacts; the 13 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `run.data_test` | `fff035ab` | table | table, 1500 rows | the subject's data_test.csv |
| `run.data_train` | `bc07261a` | table | table, 1789 rows | the subject's data_train.csv |
| `run.duration_s` | `d6169f24` | scalar | 1.214335125 | subject wall-clock seconds |
| `run.features` | `abbb748e` | json | json | the subject's features.json |
| `run.metrics` | `0accf706` | json | json | the subject's metrics.json |
| `run.model_summary` | `b82670e1` | json | json | the subject's model_summary.json |
| `run.predictions_test` | `fdbe7077` | table | table, 1500 rows | the subject's predictions_test.csv |
| `run.predictions_train` | `5d347554` | table | table, 1789 rows | the subject's predictions_train.csv |
| `run.splits` | `616e04cb` | json | json | the subject's splits.json |
| `run.status` | `2922931d` | json | json | how the subject's subprocess ended |
| `run.stderr` | `41728c38` | json | json | the subject's stderr |
| `run.stdout` | `0cece598` | json | json | the subject's stdout |
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |

## Appendix C — Run trace summary

| quantity | value |
|---|---|
| tool calls | 1 (run_model 1) |
| plan steps (bounded loop) | 0 |
| LLM calls | 8 (plain_llm 1, extract 7) |
| re-asks | 0 |
| repair rounds | 0 |
| tokens in / out | 59,723 / 34,954 |
| notional cost (USD) | 1.4554 |
| wall-clock (s) | 430.75 |
| subject run (s) | 1.21 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | credit_default-plain_llm-20260918T185539Z-6e98ce62 |

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
