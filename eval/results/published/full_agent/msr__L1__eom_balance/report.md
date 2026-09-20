---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: msr_prepayment
version: "1.0"
model_type: discrete_time_hazard
configuration: full_agent
model: claude-opus-5[1m]
run_id: msr_prepayment-full_agent-20260920T181437Z-e61d346a
data_mode: synthetic
synthetic_n: 2000
grounding_precision_pre: 0.9879
grounding_precision_post: 1.0000
n_claims: 326
n_findings_by_severity: {high: 2, medium: 0, low: 0, info: 0}
generated: "2026-09-20T18:14:37Z"
illustrative: false
---

# Validation report — `msr_prepayment` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `msr_prepayment` v1.0 | `full_agent` | claude-opus-5[1m] | synthetic, n = 2000 | 0.9879 → 1.0000 | 2 / 0 / 0 / 0 |
<!-- quaestor:renderer:end -->

The subject of this validation is the msr_prepayment model package, a loan-level model that predicts the probability of mortgage prepayment, and this report follows the structure of the Federal Reserve's model risk management guidance on model validation and monitoring [[reg:SR26-2:V]].
Quaestor re-executed the packaged subject end to end under the wall-clock cap of 300 [[art:2ad8d1a5:runtime.max_seconds]] seconds the package declares, and every performance figure below was recomputed from the subject's own scored output rather than copied from the development record.
The training split holds 36013 [[art:c5ebd9c9:profile.train.n]] rows and the test split holds 15382 [[art:e3abc1b8:profile.test.n]] rows.
Scoring also covers an out-of-time split of 12257 [[art:7898809e:metrics.out_of_time.n]] rows and a vintage holdout of 32177 [[art:37a92951:metrics.vintage_holdout.n]] rows.
Against the developer-declared minimum test discrimination of 0.65 [[art:fececac1:threshold.package.auc.test.min]], the recomputed test AUC of 1 [[art:4619bd69:metrics.test.auc]] lies above that bound, so the subject passes the declared discrimination threshold.
Against the developer-declared population stability ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]], the largest train-to-test stability index of 0.06189 [[art:c2e8c8fd:psi.max]] lies below that bound, so the subject passes the declared stability threshold.
Discrimination is at the same level of 1 [[art:bcb747a3:metrics.out_of_time.auc]] on the out-of-time split and 1 [[art:00749c11:metrics.vintage_holdout.auc]] on the vintage holdout, so the declared bounds are cleared on the held-out populations as well as on test.
This validation raised F-001, a L1 leakage finding at high severity, and F-002, a X1 scenario analysis finding at high severity.
Each is set out in full in the findings section, which heads them '### F-001 · L1 leakage · severity **high**' and '### F-002 · X1 scenario analysis · severity **high**', and the scope table above this prose carries their tally by severity.
Because the guidance treats validation as an assessment of reliability and limitations rather than a pass-fail exercise [[reg:SR26-2:V]], the threshold results above should be read together with those findings and not in place of them.

## 2. Conceptual soundness

Model design is assessed here against the expectation that validation covers model design, key modeling choices, assumptions, construction, and the quality and extent of developmental evidence [[reg:SR26-2:V.1.a]].

### Champion and its inputs

The champion is a logistic model of monthly prepayment with an intercept of -9.211 [[art:f6c2df89:run.model_summary#intercept]], fitted on 36013 [[art:f6c2df89:run.model_summary#n_train]] loan-months drawn from 934 [[art:f6c2df89:run.model_summary#n_train_loans]] loans, with loan age entered through spline terms rather than a single linear effect.
That functional form is a conventional choice for this outcome: a monotone link on a binary monthly event, with the seasoning profile left free enough to bend.

The feature set carries 12 [[art:61276a96:run.features#n]] features in total.
Of these, 5 [[art:61276a96:run.features#at_origination]] are fixed at origination and 7 [[art:61276a96:run.features#before_period_start]] are known before the start of the period being predicted.
The count of features first observable during the predicted period is 0 [[art:61276a96:run.features#during_period]], and the count observable only after the outcome is realised is 0 [[art:61276a96:run.features#after_outcome]].
On timing alone, then, there is no input dated after the event it helps predict, which is the first thing a design review of a monthly hazard model should want to establish.

The developer's own collinearity screen removed `rate_change_12m` at a variance inflation factor of 11.28 [[art:f6c2df89:run.model_summary#removed.rate_change_12m.vif]], against a screen cut of 10 [[art:f6c2df89:run.model_summary#vif_threshold]].
That removal is defensible on its face, since a rolling rate-change term is close to a linear combination of the refinance-incentive and spread-at-origination terms the model retains, and dropping it leaves the retained rate terms individually interpretable.
The screen is a threshold on collinearity and not on economic redundancy, so it does not by itself settle whether the retained set still contains overlapping constructs.

### Coefficients and expected signs

The largest coefficient in magnitude by a wide margin is the one on current balance, at -1.672 [[art:f6c2df89:run.model_summary#coefficients.bom_balance_log.value]], followed by the one on original balance, at 0.4741 [[art:f6c2df89:run.model_summary#coefficients.orig_upb_log.value]].
The remaining terms sit well below those two in magnitude: the refinance incentive at 0.02004 [[art:f6c2df89:run.model_summary#coefficients.incentive.value]], credit score at 0.01149 [[art:f6c2df89:run.model_summary#coefficients.credit_score.value]], note rate at 0.009311 [[art:f6c2df89:run.model_summary#coefficients.note_rate.value]], burnout at -0.008197 [[art:f6c2df89:run.model_summary#coefficients.burnout.value]], original LTV at -0.00636 [[art:f6c2df89:run.model_summary#coefficients.orig_ltv.value]], the spread at origination at 0.00387 [[art:f6c2df89:run.model_summary#coefficients.sato.value]], and the two seasonality terms at -0.005008 [[art:f6c2df89:run.model_summary#coefficients.season_cos.value]] and -0.001276 [[art:f6c2df89:run.model_summary#coefficients.season_sin.value]].
The loan-age spline terms run 0.01175 [[art:f6c2df89:run.model_summary#coefficients.loan_age_spline_1.value]], -0.02828 [[art:f6c2df89:run.model_summary#coefficients.loan_age_spline_2.value]], -0.03906 [[art:f6c2df89:run.model_summary#coefficients.loan_age_spline_3.value]] and -0.05271 [[art:f6c2df89:run.model_summary#coefficients.loan_age_spline_4.value]], a rising-then-falling profile that matches the seasoning ramp and subsequent decline a prepayment model is expected to reproduce.

The signs on the rate and credit terms are those the subject matter expects.
A higher note rate and a larger refinance incentive both raise the modelled prepayment rate, as a borrower paying above the prevailing rate has more to gain from refinancing.
A higher spread at origination moves in the same direction, for the same reason.
A higher credit score raises the modelled rate, consistent with better-qualified borrowers finding it easier to requalify.
A higher original LTV lowers it, consistent with thinner equity obstructing a refinance.
Burnout enters negatively, which is also what the subject matter expects of a pool that has already exercised its refinance option.

The pairing of the balance terms deserves the design record's attention.
The current-balance term enters negatively and the original-balance term positively, and the two are mechanically related through amortisation, so the fitted pair is more naturally read as encoding paydown and seasoning jointly than as two independent statements about loan size.
Each term taken alone carries a sign the subject matter can rationalise, but their joint interpretation depends on a correlation the collinearity screen did not act on, and the magnitude of the current-balance coefficient relative to every other term in the model means the reading of that pair drives most of the score's variation.

### Fitted signs against univariate directions

The count of retained features whose fitted sign contradicts the direction of their own single-feature relationship with the outcome on train is 2 [[art:66ce738a:sign_check.n_disagreements]].

The first is burnout, whose fitted coefficient carries sign -1 [[art:dcfb2de4:sign_check.burnout.coef_sign]] while its univariate direction on train is 1 [[art:bfc96bb2:sign_check.burnout.univariate_direction]], recorded as a disagreement at 0 [[art:56826e40:sign_check.burnout.agrees]].
Refitting the champion's form without burnout changes test AUC by 0 [[art:d50de877:ablation.burnout.delta_auc]], so the disagreement sits on a term the fitted model is not relying on for discrimination.
It is worth stating plainly that the fitted negative sign here is the one prepayment practice expects; the contradiction is with the feature's raw train-level direction, which a conditional fit can legitimately reverse when the rate terms absorb the incentive that drives the raw association.

The second is the sine seasonality term, whose fitted coefficient carries sign -1 [[art:92ed5b5f:sign_check.season_sin.coef_sign]] while its univariate direction on train is 1 [[art:cae6b096:sign_check.season_sin.univariate_direction]], recorded as a disagreement at 0 [[art:74f2d0e0:sign_check.season_sin.agrees]].
Refitting without it changes test AUC by 0 [[art:a4f7b0c1:ablation.season_sin.delta_auc]], so this disagreement likewise falls on a term the model barely uses, and a seasonality phase term has no sign the subject matter pins down in advance.

The remaining checked features agree with their univariate directions: current balance at 1 [[art:26b1789b:sign_check.bom_balance_log.agrees]] with fitted sign -1 [[art:d2e88db3:sign_check.bom_balance_log.coef_sign]] and univariate direction -1 [[art:8ee4f8fe:sign_check.bom_balance_log.univariate_direction]]; credit score at 1 [[art:915bf8eb:sign_check.credit_score.agrees]] with fitted sign 1 [[art:1ec1078b:sign_check.credit_score.coef_sign]] and univariate direction 1 [[art:42303896:sign_check.credit_score.univariate_direction]]; the refinance incentive at 1 [[art:f7b2338e:sign_check.incentive.agrees]] with fitted sign 1 [[art:684cf11a:sign_check.incentive.coef_sign]] and univariate direction 1 [[art:8098d951:sign_check.incentive.univariate_direction]]; note rate at 1 [[art:ca18290e:sign_check.note_rate.agrees]] with fitted sign 1 [[art:0e3296a5:sign_check.note_rate.coef_sign]] and univariate direction 1 [[art:61f6e1ac:sign_check.note_rate.univariate_direction]]; original LTV at 1 [[art:7021aeb0:sign_check.orig_ltv.agrees]] with fitted sign -1 [[art:7eec65ec:sign_check.orig_ltv.coef_sign]] and univariate direction -1 [[art:76dbc708:sign_check.orig_ltv.univariate_direction]]; original balance at 1 [[art:07a9d3e6:sign_check.orig_upb_log.agrees]] with fitted sign 1 [[art:5aa309fc:sign_check.orig_upb_log.coef_sign]] and univariate direction 1 [[art:b9743ecb:sign_check.orig_upb_log.univariate_direction]]; the spread at origination at 1 [[art:2401eba2:sign_check.sato.agrees]] with fitted sign 1 [[art:c031d0d5:sign_check.sato.coef_sign]] and univariate direction 1 [[art:c08233a6:sign_check.sato.univariate_direction]]; and the cosine seasonality term at 1 [[art:7f18ddf7:sign_check.season_cos.agrees]] with fitted sign -1 [[art:7dbb1ffc:sign_check.season_cos.coef_sign]] and univariate direction -1 [[art:03e931f0:sign_check.season_cos.univariate_direction]].

### Contribution of each variable

Assessing the choice of variables through their impact on model output is part of the developmental evidence a validation is expected to weigh [[reg:SR11-7:V.1.a]].
The ablations are measured from a refit of the champion's form on every retained feature, which scores 1 [[art:7610ff35:ablation.baseline_auc]] on test.
Dropping current balance changes test AUC by -0.2327 [[art:c226f60f:ablation.bom_balance_log.delta_auc]], the one term whose removal costs the refit any discrimination.
Dropping burnout changes it by 0 [[art:d50de877:ablation.burnout.delta_auc]], credit score by 0 [[art:d1dff006:ablation.credit_score.delta_auc]], the refinance incentive by 0 [[art:33a25e3c:ablation.incentive.delta_auc]], loan age by 0 [[art:1a789b08:ablation.loan_age.delta_auc]], note rate by 0 [[art:65b3f07a:ablation.note_rate.delta_auc]], original LTV by 0 [[art:370eaea8:ablation.orig_ltv.delta_auc]], original balance by 0 [[art:e245ef14:ablation.orig_upb_log.delta_auc]], the spread at origination by 0 [[art:2bbb0015:ablation.sato.delta_auc]], the cosine seasonality term by 0 [[art:9453331c:ablation.season_cos.delta_auc]] and the sine seasonality term by 0 [[art:a4f7b0c1:ablation.season_sin.delta_auc]].
Read together, the coefficient magnitudes and the ablation deltas tell the same story: the score's ordering of loans rests on current balance, and the economically motivated rate, credit and seasoning terms that justify the model's design are not what the fit is using to separate prepayments from non-prepayments on test.
That is a conceptual-soundness concern in its own right, because a model whose stated rationale rests on refinance economics but whose discrimination rests on a balance variable is not doing on test what its design document says it does.
The reader should also note that a baseline at the top of the AUC scale compresses this evidence, since a refit can only lose discrimination from such a level and never gain it, which limits how much the equal deltas can be asked to carry.

### Effective challenge

The challenger scores 1 [[art:5aeaf534:challenger.auc]] on test against the champion's recomputed 1 [[art:4619bd69:metrics.test.auc]], a difference of 0 [[art:d8eca8f5:challenger.delta_auc]].
The threshold at which a challenger's lead over the champion would be treated as material is 0.03 [[art:e042774c:threshold.E1.delta_auc]].
The observed lead is below that threshold, so the benchmark gives no ground on discrimination for preferring the challenger to the champion.

On calibration the two are not identical: the champion's Brier score on test is 1.011e-08 [[art:67fd4fea:metrics.test.brier]] and the challenger's is 3.226e-13 [[art:0b5236ca:challenger.brier]], the lower of the two being the challenger's.
The comparison drawn here is one of ordering between the two levels only, not of the difference or the ratio between them.

The effective challenge should be read with its limits in view.
When champion and challenger both sit at the ceiling of the discrimination scale, an AUC comparison cannot separate them whatever their internal differences, and a threshold expressed as an AUD lead has nothing to bite on.
The Brier levels, both extremely close to zero, point the same way: on this test sample the two models are agreeing with the outcome almost exactly, which makes the benchmarking exercise weak evidence for the champion's design rather than strong evidence for it.
A challenge capable of exercising the design would need to be run on data where the champion does not already separate the outcome completely.

## 3. Data integrity and drift

Supervisory guidance places a critical assessment of data quality, relevance, and inputs among the core activities of model testing, and this section reads the package's data screens on that basis [[reg:SR26-2:IV.1]].

### Missingness

The training split holds 36013 [[art:c5ebd9c9:profile.train.n]] rows, the test split 15382 [[art:e3abc1b8:profile.test.n]], the vintage holdout 32177 [[art:426e712a:profile.vintage_holdout.n]] and the out-of-time split 12257 [[art:fa39c5cf:profile.out_of_time.n]].
The largest missing fraction is 0 [[art:050a3099:profile.train.missing.max]] in train, 0 [[art:f813848d:profile.test.missing.max]] in test, 0 [[art:329bb430:profile.vintage_holdout.missing.max]] in the vintage holdout and 0 [[art:4dafce11:profile.out_of_time.missing.max]] out of time.
No split's largest missing fraction stands apart from another's, so the between-split missingness gap cannot reach the declared bound of 0.1 [[art:9cce25ea:threshold.D1.missing_gap]].
Missingness is therefore not a source of differential treatment across the evaluation populations.

### Population and characteristic stability

The largest train-to-test population stability index, the score included, is 0.06189 [[art:c2e8c8fd:psi.max]], below the declared stability bound of 0.25 [[art:278b9016:threshold.S1.psi]], which the package also carries at 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
That maximum is credit_score at 0.06189 [[art:7e87527c:psi.credit_score]], followed by orig_upb_log at 0.04817 [[art:55030a3b:psi.orig_upb_log]], orig_ltv at 0.03617 [[art:cd1ff136:psi.orig_ltv]], bom_balance_log at 0.03018 [[art:ce3c425c:psi.bom_balance_log]] and sato at 0.02773 [[art:584da64f:psi.sato]].
The remaining train-to-test indices sit lower still: note_rate at 0.01371 [[art:ecc6adf3:psi.note_rate]], burnout at 0.004614 [[art:9dc7ecc2:psi.burnout]], incentive at 0.0009923 [[art:2da5570f:psi.incentive]], loan_age at 0.0001994 [[art:2202b157:psi.loan_age]], season_cos at 1.79e-05 [[art:addec503:psi.season_cos]] and season_sin at 2.939e-06 [[art:4d2ed98d:psi.season_sin]], with the score itself at 0.01874 [[art:2ad82680:psi.y_score]].
The train-to-test comparison is accordingly quiet across every input and across the score.

Read against the same declared bound of 0.25 [[art:278b9016:threshold.S1.psi]], the train-to-out-of-time comparison is not quiet.
Burnout stands at 2.945 [[art:7b0bbebb:psi.out_of_time.burnout]], loan_age at 2.484 [[art:d6eaaaf5:psi.out_of_time.loan_age]], note_rate at 0.6977 [[art:cabd371d:psi.out_of_time.note_rate]] and incentive at 0.4958 [[art:42076ed1:psi.out_of_time.incentive]], each above that bound.
The other out-of-time indices remain under it: bom_balance_log at 0.08708 [[art:9fa682d1:psi.out_of_time.bom_balance_log]], orig_upb_log at 0.07136 [[art:ac349b67:psi.out_of_time.orig_upb_log]], credit_score at 0.05988 [[art:d7249e47:psi.out_of_time.credit_score]], orig_ltv at 0.04301 [[art:3eee5db4:psi.out_of_time.orig_ltv]], season_sin at 0.02789 [[art:144e1bd9:psi.out_of_time.season_sin]], sato at 0.01299 [[art:c2233ce6:psi.out_of_time.sato]] and season_cos at 0.007524 [[art:25cf6b85:psi.out_of_time.season_cos]].
The score shifts less than the worst of its inputs, at 0.1451 [[art:12620838:psi.out_of_time.y_score]], which is below the declared bound of 0.25 [[art:278b9016:threshold.S1.psi]].

The vintage holdout sits between the two: read against the declared bound of 0.25 [[art:278b9016:threshold.S1.psi]], note_rate at 0.6088 [[art:f281f8a7:psi.vintage_holdout.note_rate]] and incentive at 0.4475 [[art:5e61b6f9:psi.vintage_holdout.incentive]] are above it.
Every other input is below that bound: loan_age at 0.07112 [[art:6d92c48b:psi.vintage_holdout.loan_age]], burnout at 0.04749 [[art:e29067e6:psi.vintage_holdout.burnout]], orig_upb_log at 0.0404 [[art:77ec758a:psi.vintage_holdout.orig_upb_log]], credit_score at 0.03996 [[art:3498d307:psi.vintage_holdout.credit_score]], bom_balance_log at 0.03707 [[art:b3073b46:psi.vintage_holdout.bom_balance_log]], sato at 0.02989 [[art:eea64c25:psi.vintage_holdout.sato]], orig_ltv at 0.02942 [[art:d07cfb7d:psi.vintage_holdout.orig_ltv]], season_cos at 0.001288 [[art:9fe842a8:psi.vintage_holdout.season_cos]] and season_sin at 0.0007309 [[art:b0dc9745:psi.vintage_holdout.season_sin]], with the score at 0.05813 [[art:33ffbed6:psi.vintage_holdout.y_score]].
Comparing the two out-of-sample populations feature by feature on the level of the index rather than on any derived difference or ratio, note_rate and incentive are the pair above the bound in both, while burnout and loan_age are far above it out of time and below it in the vintage holdout.
The direction of travel is consistent with holdouts drawn from later vintages and later periods, where seasoning and rate-path variables move away from the training distribution, and none of these exceedances is among the candidate findings for this section; they are reported here against the bound named above and left to the findings section's open items.

Characteristic stability, which attributes the shift in the linear predictor to individual inputs, is dominated by bom_balance_log at 0.03215 [[art:60a10892:csi.bom_balance_log]], which is also the largest such contribution at 0.03215 [[art:b2440ca1:csi.max]].
The rest contribute far less: orig_upb_log at 0.004636 [[art:5d1c16f2:csi.orig_upb_log]], orig_ltv at 0.0008996 [[art:7ea837e1:csi.orig_ltv]], sato at 0.000449 [[art:fb71eb9e:csi.sato]], note_rate at 0.0003806 [[art:587b33e9:csi.note_rate]], credit_score at 0.000223 [[art:d87a2d40:csi.credit_score]], burnout at 0.0001016 [[art:a5da1daa:csi.burnout]], incentive at 9.278e-05 [[art:41325258:csi.incentive]], season_cos at 1.935e-05 [[art:de66f2c6:csi.season_cos]], season_sin at 1.386e-06 [[art:4c3f0dd9:csi.season_sin]] and loan_age at 0 [[art:df52c920:csi.loan_age]].
No characteristic contribution approaches the declared stability bound of 0.25 [[art:278b9016:threshold.S1.psi]] against which the population indices above were read.

### Leakage and contamination screens

The timing screen flags 0 [[art:742bcd24:leakage.timing.n_flagged]] features declared as observed during the period or after the outcome, so no input is declared to be knowable only after the event it predicts.
The target-adjacent name screen matches 0 [[art:407e62be:leakage.name_screen.n_matched]] feature names, so no input is implicated by naming alone.
The single-feature discrimination screen is the exception: the strongest single feature reaches an AUC of 1 [[art:7f74c0d5:leakage.target_corr.max_single_feature_auc]] against the declared bound of 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]], and the check attributes that to bom_balance_log.
This is a leakage finding at high suggested severity, and it is material: a single input that separates the outcome perfectly leaves the rest of the specification unexercised, and every downstream performance number should be read as conditional on its resolution.
That the same input also carries the largest characteristic contribution at 0.03215 [[art:60a10892:csi.bom_balance_log]] means the shift in the linear predictor is driven mostly by the feature under suspicion, which weakens the stability evidence above rather than reinforcing it.

The contamination screen has both arms below their respective bounds.
The share of test rows whose identifying keys also identify a row of train is 0 [[art:63d37fc5:leakage.overlap.ids]], against the declared bound of 0.005 [[art:9f336eaf:threshold.L2.overlap]].
The share of test rows whose feature values also appear in train is 0 [[art:0fec8048:leakage.overlap.features]], read against the bound the feature-overlap rule actually applied, 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]], which is the larger of the declared bound and twice the within-train duplicate share, the latter standing at 0 [[art:4474c227:leakage.duplicates.train]].
The row-overlap screen reported alongside them is likewise 0 [[art:4c9fcd09:leakage.overlap]].
Distinguishing the two arms matters because coincident feature vectors from different subjects are not contamination, whereas a repeated key is; here neither arm shows anything, so the split boundary itself is sound and the leakage concern rests entirely on the single-feature discrimination screen.

## 4. Outcomes analysis

Outcomes analysis compares this model's outputs against the corresponding real-world outcomes, and the guidance frames that comparison against the model's objectives and its business use [[reg:SR26-2:V.1.b]].

This section reports calibration before discrimination.

The reason is the declared use: package.yaml declares that this model's output is consumed as a probability and not only as a ranking, so whether the predicted probabilities mean what they say is the leading question here, whatever rate the event occurs at.

### Calibration

The subject reports a calibration slope of 2.867 [[art:e8f6c83d:run.metrics#train.calibration_slope]] on train, 2.833 [[art:e8f6c83d:run.metrics#test.calibration_slope]] on test, 2.924 [[art:e8f6c83d:run.metrics#out_of_time.calibration_slope]] out of time and 2.797 [[art:e8f6c83d:run.metrics#vintage_holdout.calibration_slope]] on the vintage holdout.

The declared band for that slope runs from 0.8 [[art:749634ae:threshold.C1.calibration_slope.min]] to 1.2 [[art:b6672579:threshold.C1.calibration_slope.max]], and all four reported slopes sit above the top of that band.

The indicator that the predictions separate the outcome stands at 1 [[art:d7ee2241:calibration.separable.train]] on train, 1 [[art:81c3fa7a:calibration.separable.test]] on test, 1 [[art:258b7972:calibration.separable.out_of_time]] out of time and 1 [[art:137e2c39:calibration.separable.vintage_holdout]] on the vintage holdout, and where the predictions separate the outcome a slope of this kind has no finite maximum likelihood estimate, which is the caveat the figures above carry.

Mean predicted probability on train is 0.008607 [[art:6f9330ed:metrics.train.mean_predicted]] against an observed rate of 0.008525 [[art:b9ef3327:metrics.train.event_rate]], a relative gap of 0.009654 [[art:db1bca38:calibration.mean_rel_gap.train]].

On test the mean predicted probability is 0.008144 [[art:83863be2:metrics.test.mean_predicted]] against an observed rate of 0.008061 [[art:570cc08a:metrics.test.event_rate]], a relative gap of 0.01026 [[art:4e1854b1:calibration.mean_rel_gap.test]].

Out of time the mean predicted probability is 0.01802 [[art:276f106a:metrics.out_of_time.mean_predicted]] against an observed rate of 0.01795 [[art:83ccf5c0:metrics.out_of_time.event_rate]], a relative gap of 0.003913 [[art:68619260:calibration.mean_rel_gap.out_of_time]].

On the vintage holdout the mean predicted probability is 0.004899 [[art:af925790:metrics.vintage_holdout.mean_predicted]] against an observed rate of 0.004817 [[art:e3590a16:metrics.vintage_holdout.event_rate]], a relative gap of 0.01696 [[art:1438e44d:calibration.mean_rel_gap.vintage_holdout]].

The tolerance on that relative gap is 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]], and each of the four relative gaps sits below it.

Comparing those gaps against one another as differences in the gaps themselves, and not as ratios between them, the vintage holdout's 0.01696 [[art:1438e44d:calibration.mean_rel_gap.vintage_holdout]] is the largest and the out-of-time 0.003913 [[art:68619260:calibration.mean_rel_gap.out_of_time]] the smallest, with test at 0.01026 [[art:4e1854b1:calibration.mean_rel_gap.test]] and train at 0.009654 [[art:db1bca38:calibration.mean_rel_gap.train]] between them; the ratios between these gaps are a separate comparison and are not stated here.

In portfolio terms, the mean absolute difference between actual and predicted CPR is 0.000928 [[art:99b2b87f:cpr.train.mae]] on train, 0.0009292 [[art:be219b85:cpr.test.mae]] on test, 0.0007118 [[art:bdc9d54f:cpr.out_of_time.mae]] out of time and 0.0009299 [[art:d1a19e91:cpr.vintage_holdout.mae]] on the vintage holdout.

On test the actual CPR is 0.09256 [[art:e8f6c83d:run.metrics#test.cpr_actual]] against a predicted 0.09347 [[art:e8f6c83d:run.metrics#test.cpr_predicted]], and out of time the actual CPR is 0.1953 [[art:e8f6c83d:run.metrics#out_of_time.cpr_actual]] against a predicted 0.196 [[art:e8f6c83d:run.metrics#out_of_time.cpr_predicted]].

Calibration by decile of predicted probability on test is set out below.

<!-- quaestor:renderer:begin table calibration.test -->
Calibration by decile of predicted probability on test [[art:a3f4f35f:calibration.test]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 6.427e-05 | 0 | 1539 |
| 2 | 7.269e-05 | 0 | 1539 |
| 3 | 7.745e-05 | 0 | 1538 |
| 4 | 8.161e-05 | 0 | 1538 |
| 5 | 8.541e-05 | 0 | 1538 |
| 6 | 8.919e-05 | 0 | 1538 |
| 7 | 9.302e-05 | 0 | 1538 |
| 8 | 9.697e-05 | 0 | 1538 |
| 9 | 0.0001019 | 0 | 1538 |
| 10 | 0.08069 | 0.08062 | 1538 |
<!-- quaestor:renderer:end -->

Actual against predicted CPR by period on test is set out below.

<!-- quaestor:renderer:begin table cpr.test -->
Actual against predicted CPR by period on test [[art:0aa376c9:cpr.test]]:

| period | n | actual_cpr | predicted_cpr |
|---|---|---|---|
| 201402 | 15 | 0 | 0.001003 |
| 201403 | 28 | 0 | 0.001005 |
| 201404 | 56 | 0 | 0.001001 |
| 201405 | 68 | 0 | 0.001008 |
| 201406 | 80 | 0 | 0.001017 |
| 201407 | 97 | 0.1169 | 0.1178 |
| 201408 | 111 | 0 | 0.001024 |
| 201409 | 133 | 0.08659 | 0.08747 |
| 201410 | 145 | 0 | 0.001017 |
| 201411 | 161 | 0 | 0.00102 |
| 201412 | 175 | 0 | 0.001019 |
| 201501 | 198 | 0 | 0.001022 |
| 201502 | 198 | 0 | 0.001023 |
| 201503 | 198 | 0.05895 | 0.05989 |
| 201504 | 197 | 0 | 0.001036 |
| 201505 | 197 | 0 | 0.001046 |
| 201506 | 197 | 0 | 0.001053 |
| 201507 | 197 | 0 | 0.00106 |
| 201508 | 197 | 0 | 0.001067 |
| 201509 | 197 | 0.05924 | 0.06022 |
| 201510 | 196 | 0.05954 | 0.06053 |
| 201511 | 195 | 0 | 0.001074 |
| 201512 | 195 | 0 | 0.001073 |
| 201601 | 195 | 0.1698 | 0.1706 |
| 201602 | 192 | 0.06074 | 0.06175 |
| 201603 | 191 | 0.1187 | 0.1196 |
| 201604 | 189 | 0.1198 | 0.1208 |
| 201605 | 187 | 0.3673 | 0.3679 |
| 201606 | 180 | 0.1255 | 0.1264 |
| 201607 | 178 | 0.1268 | 0.1277 |
| 201608 | 176 | 0.06609 | 0.06712 |
| 201609 | 175 | 0.1288 | 0.1298 |
| 201610 | 173 | 0.1893 | 0.1902 |
| 201611 | 170 | 0.06835 | 0.06932 |
| 201612 | 169 | 0.06874 | 0.0697 |
| 201701 | 168 | 0.1339 | 0.1347 |
| 201702 | 176 | 0.2924 | 0.293 |
| 201703 | 191 | 0.06105 | 0.062 |
| 201704 | 199 | 0 | 0.001051 |
| 201705 | 218 | 0.05368 | 0.05465 |
| 201706 | 238 | 0.04927 | 0.05024 |
| 201707 | 248 | 0 | 0.001041 |
| 201708 | 274 | 0 | 0.001035 |
| 201709 | 284 | 0.08131 | 0.08222 |
| 201710 | 300 | 0 | 0.001024 |
| 201711 | 323 | 0.03653 | 0.03749 |
| 201712 | 334 | 0.03534 | 0.03629 |
| 201801 | 354 | 0.03338 | 0.03435 |
| 201802 | 353 | 0.06591 | 0.06684 |
| 201803 | 351 | 0.03366 | 0.03464 |
| 201804 | 350 | 0.06646 | 0.06741 |
| 201805 | 348 | 0.1594 | 0.1602 |
| 201806 | 343 | 0.1616 | 0.1624 |
| 201807 | 338 | 0.1638 | 0.1646 |
| 201808 | 333 | 0.06974 | 0.07068 |
| 201809 | 331 | 0.2544 | 0.2551 |
| 201810 | 323 | 0.1707 | 0.1715 |
| 201811 | 318 | 0.07292 | 0.07384 |
| 201812 | 316 | 0.1742 | 0.1749 |
| 201901 | 311 | 0.1098 | 0.1106 |
| 201902 | 300 | 0.1488 | 0.1496 |
| 201903 | 285 | 0.2253 | 0.2261 |
| 201904 | 258 | 0.246 | 0.2467 |
| 201905 | 243 | 0.1385 | 0.1393 |
| 201906 | 233 | 0.2688 | 0.2694 |
| 201907 | 219 | 0.1984 | 0.1992 |
| 201908 | 206 | 0 | 0.001056 |
| 201909 | 191 | 0.06105 | 0.06202 |
| 201910 | 182 | 0.06398 | 0.06495 |
| 201911 | 171 | 0.06796 | 0.06895 |
| 201912 | 166 | 0 | 0.001076 |
<!-- quaestor:renderer:end -->

### Discrimination

The recomputed discrimination metrics by split are set out in the table below, one row per metric.

| Metric | train | test | out_of_time | vintage_holdout |
| --- | --- | --- | --- | --- |
| AUC | 1 [[art:6269694d:metrics.train.auc]] | 1 [[art:4619bd69:metrics.test.auc]] | 1 [[art:bcb747a3:metrics.out_of_time.auc]] | 1 [[art:00749c11:metrics.vintage_holdout.auc]] |
| Gini | 1 [[art:e2084e07:metrics.train.gini]] | 1 [[art:35acd744:metrics.test.gini]] | 1 [[art:6d939d01:metrics.out_of_time.gini]] | 1 [[art:f4aa377a:metrics.vintage_holdout.gini]] |
| KS | 1 [[art:24c2277d:metrics.train.ks]] | 1 [[art:a13846c8:metrics.test.ks]] | 1 [[art:e3aa3687:metrics.out_of_time.ks]] | 1 [[art:cb4509f6:metrics.vintage_holdout.ks]] |
| Brier | 1.096e-08 [[art:0c2c4489:metrics.train.brier]] | 1.011e-08 [[art:67fd4fea:metrics.test.brier]] | 1.376e-08 [[art:44f11124:metrics.out_of_time.brier]] | 8.646e-09 [[art:c58e369c:metrics.vintage_holdout.brier]] |
| Log loss | 9.128e-05 [[art:1761d10c:metrics.train.logloss]] | 9.043e-05 [[art:db4e6b76:metrics.test.logloss]] | 9.057e-05 [[art:4ff30655:metrics.out_of_time.logloss]] | 8.629e-05 [[art:85bdc089:metrics.vintage_holdout.logloss]] |
| Rows scored | 36013 [[art:6fdfeabb:metrics.train.n]] | 15382 [[art:e55953e1:metrics.test.n]] | 12257 [[art:7898809e:metrics.out_of_time.n]] | 32177 [[art:37a92951:metrics.vintage_holdout.n]] |

The share of events falling in the top two deciles of predicted probability is 1 [[art:194d1fbd:deciles.train.top2_capture]] on train, 1 [[art:466bfdc8:deciles.test.top2_capture]] on test, 1 [[art:d3114d7a:deciles.out_of_time.top2_capture]] out of time and 1 [[art:db275674:deciles.vintage_holdout.top2_capture]] on the vintage holdout.

AUC on train is 1 [[art:6269694d:metrics.train.auc]] and AUC on test is 1 [[art:4619bd69:metrics.test.auc]], neither above the other, so the train-to-test gap stays below the bound of 0.08 [[art:630f28f4:threshold.O1.auc_gap]].

AUC out of time is 1 [[art:bcb747a3:metrics.out_of_time.auc]] and on the vintage holdout 1 [[art:00749c11:metrics.vintage_holdout.auc]], neither below the test figure, against the allowance of 0.05 [[art:90f8b6d9:threshold.O1.holdout_gap]] for how far a period split may fall below test.

Decile separation on test, with the highest probabilities in the first decile, is set out below.

<!-- quaestor:renderer:begin table deciles.test -->
Decile separation on test; decile 1 holds the highest probabilities [[art:a859c712:deciles.test]]:

| decile | count | events | event_rate | lift |
|---|---|---|---|---|
| 1 | 1539 | 124 | 0.08057 | 9.995 |
| 2 | 1539 | 0 | 0 | 0 |
| 3 | 1538 | 0 | 0 | 0 |
| 4 | 1538 | 0 | 0 | 0 |
| 5 | 1538 | 0 | 0 | 0 |
| 6 | 1538 | 0 | 0 | 0 |
| 7 | 1538 | 0 | 0 | 0 |
| 8 | 1538 | 0 | 0 | 0 |
| 9 | 1538 | 0 | 0 | 0 |
| 10 | 1538 | 0 | 0 | 0 |
<!-- quaestor:renderer:end -->

This degree of separation on every split is what the calibration evidence above has to be read against: an ordering this clean leaves the level of the probabilities as the question that matters for a probability-valued output.

### Declared thresholds

The thresholds package.yaml declares, with the bound, the recomputed value and the outcome for each, are set out below as the tool computed them.

<!-- quaestor:renderer:begin table thresholds.evaluation -->
Every threshold package.yaml declares, with its bound, the recomputed value and the outcome [[art:25af6e79:thresholds.evaluation]]:

| metric | split | bound | value | result |
|---|---|---|---|---|
| auc | test | minimum 0.65 | 1 | pass |
| calibration_slope | test | minimum 0.8 | not evaluated: calibration_slope.test is not in the store | not evaluated |
| calibration_slope | test | maximum 1.2 | not evaluated: calibration_slope.test is not in the store | not evaluated |
| psi |  | maximum 0.25 | 0.06189 | pass |
<!-- quaestor:renderer:end -->

The table pairs each declared bound with the value recomputed on its split, among them the AUC floor of 0.65 [[art:fececac1:threshold.package.auc.test.min]] and the population stability ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]], against which the largest train-to-test stability index is 0.06189 [[art:c2e8c8fd:psi.max]].

Its outcome column is the computed record for those bounds and governs wherever this section's prose could be read another way.

### Follow-up analyses

The planning loop ran one further step: every metric recomputed on the slice `bom_balance_log <= median(bom_balance_log)` of each split.

It was asked because the prepayment events on each split fall entirely within that slice, so scoring it shows whether the champion retains discrimination once the separating split on that feature is conditioned out, which is what makes the single-feature concern material rather than cosmetic.

<!-- quaestor:renderer:begin table metrics.train.sub.bom_balance_log_low -->
Every metric on the bom_balance_log below_median slice of train [[art:179b230e:metrics.train.sub.bom_balance_log_low]]:

| metric | value |
|---|---|
| n | 18007 |
| event_rate | 0.01705 |
| auc | 1 |
| gini | 1 |
| ks | 1 |
| brier | 1.567e-08 |
| logloss | 0.000104 |
| mean_predicted | 0.01713 |
| mean_rel_gap | 0.005047 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.bom_balance_log_low -->
Every metric on the bom_balance_log below_median slice of test [[art:3333d0d1:metrics.test.sub.bom_balance_log_low]]:

| metric | value |
|---|---|
| n | 7691 |
| event_rate | 0.01612 |
| auc | 1 |
| gini | 1 |
| ks | 1 |
| brier | 1.403e-08 |
| logloss | 0.0001027 |
| mean_predicted | 0.01621 |
| mean_rel_gap | 0.005415 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.out_of_time.sub.bom_balance_log_low -->
Every metric on the bom_balance_log below_median slice of out_of_time [[art:8342d448:metrics.out_of_time.sub.bom_balance_log_low]]:

| metric | value |
|---|---|
| n | 6129 |
| event_rate | 0.03589 |
| auc | 1 |
| gini | 1 |
| ks | 1 |
| brier | 2.189e-08 |
| logloss | 0.0001067 |
| mean_predicted | 0.03596 |
| mean_rel_gap | 0.001841 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.vintage_holdout.sub.bom_balance_log_low -->
Every metric on the bom_balance_log below_median slice of vintage_holdout [[art:547f8789:metrics.vintage_holdout.sub.bom_balance_log_low]]:

| metric | value |
|---|---|
| n | 16089 |
| event_rate | 0.009634 |
| auc | 1 |
| gini | 1 |
| ks | 1 |
| brier | 1.144e-08 |
| logloss | 9.662e-05 |
| mean_predicted | 0.009721 |
| mean_rel_gap | 0.009076 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

On train the slice holds 0.5 [[art:cf8da663:metrics.train.sub.bom_balance_log_low.share]] of the split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] a sub-population must hold and below the ceiling of 0.95 [[art:a928a05c:threshold.O1.slice_max_share]] at which it would be the whole split, and its AUC falls 0 [[art:d6a2abd9:metrics.train.sub.bom_balance_log_low.auc_gap]] below the split's own against the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].

Mean predicted on that slice is 0.01713 [[art:a2ea08bd:metrics.train.sub.bom_balance_log_low.mean_predicted]] against an observed rate of 0.01705 [[art:ad34a08d:metrics.train.sub.bom_balance_log_low.event_rate]], a relative gap of 0.005047 [[art:b68c896e:metrics.train.sub.bom_balance_log_low.mean_rel_gap]], so what movement there is sits in the level of the probabilities and not in their ordering.

On test the slice holds 0.5 [[art:92640866:metrics.test.sub.bom_balance_log_low.share]] of the split, above that same floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] and below the ceiling of 0.95 [[art:a928a05c:threshold.O1.slice_max_share]], and its AUC falls 0 [[art:15d6b42a:metrics.test.sub.bom_balance_log_low.auc_gap]] below the split's own against the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].

Mean predicted on that slice is 0.01621 [[art:ea1d611d:metrics.test.sub.bom_balance_log_low.mean_predicted]] against an observed rate of 0.01612 [[art:857f20f7:metrics.test.sub.bom_balance_log_low.event_rate]], a relative gap of 0.005415 [[art:51020e4b:metrics.test.sub.bom_balance_log_low.mean_rel_gap]], again a matter of level rather than of ordering.

Out of time the slice holds 0.5 [[art:3b641caa:metrics.out_of_time.sub.bom_balance_log_low.share]] of the split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] and below the ceiling of 0.95 [[art:a928a05c:threshold.O1.slice_max_share]], and its AUC falls 0 [[art:63da67de:metrics.out_of_time.sub.bom_balance_log_low.auc_gap]] below the split's own against the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].

Mean predicted on that slice is 0.03596 [[art:762160e6:metrics.out_of_time.sub.bom_balance_log_low.mean_predicted]] against an observed rate of 0.03589 [[art:da848331:metrics.out_of_time.sub.bom_balance_log_low.event_rate]], a relative gap of 0.001841 [[art:249e8321:metrics.out_of_time.sub.bom_balance_log_low.mean_rel_gap]], so the level again carries what little divergence there is.

On the vintage holdout the slice holds 0.5 [[art:80d79940:metrics.vintage_holdout.sub.bom_balance_log_low.share]] of the split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] and below the ceiling of 0.95 [[art:a928a05c:threshold.O1.slice_max_share]], and its AUC falls 0 [[art:6b406bf5:metrics.vintage_holdout.sub.bom_balance_log_low.auc_gap]] below the split's own against the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].

Mean predicted on that slice is 0.009721 [[art:aa56f401:metrics.vintage_holdout.sub.bom_balance_log_low.mean_predicted]] against an observed rate of 0.009634 [[art:81942b57:metrics.vintage_holdout.sub.bom_balance_log_low.event_rate]], a relative gap of 0.009076 [[art:c6339ca6:metrics.vintage_holdout.sub.bom_balance_log_low.mean_rel_gap]], once more a level difference rather than a ranking one.

Comparing those four slice gaps against one another as differences between the relative gaps themselves, and not as ratios between them, the vintage holdout's 0.009076 [[art:c6339ca6:metrics.vintage_holdout.sub.bom_balance_log_low.mean_rel_gap]] is the largest and the out-of-time 0.001841 [[art:249e8321:metrics.out_of_time.sub.bom_balance_log_low.mean_rel_gap]] the smallest, and the ratios between them are a different comparison that is not made here.

Conditioning on the slice therefore leaves discrimination where it stood on the full splits, and the divergence it does surface is in the level of the probabilities, which is the quantity this section leads with.

## 5. Sensitivity and scenario analysis

Sensitivity analysis and checks for robustness and stability are validation activities in their own right, and their purpose is to establish the range of conditions over which a model behaves as expected and the conditions under which it may become unstable [[reg:SR11-7:V.1.a]].
All of the analyses called for at this stage apply to the subject: the design admits a multicollinearity reading, the data carry a declared regime column, and the subject is a hazard model, so the rate-shock scenarios were run rather than set aside as inapplicable to this model type.

### 5.1 Multicollinearity among the retained features

The largest variance inflation factor among the retained features, carried by the note rate term, is 4.978 [[art:b1d416c0:vif.max]], which sits below the declared bound of 10 [[art:aeb4f33c:threshold.M1.vif]] for any retained feature.
The next largest values are on burnout at 3.44 [[art:91e7ce55:vif.burnout]] and loan age at 2.93 [[art:43980218:vif.loan_age]], both further from that bound than the note rate term.
The incentive term stands at 2.234 [[art:d924a341:vif.incentive]] and the spread-at-origination term at 1.713 [[art:08e0ca20:vif.sato]].
The remaining features sit close to unity: the logged beginning-of-month balance at 1.143 [[art:0b30efbf:vif.bom_balance_log]], the logged original balance at 1.134 [[art:347761f6:vif.orig_upb_log]], the seasonal cosine at 1.018 [[art:a2dc57c7:vif.season_cos]], credit score at 1.009 [[art:b8652149:vif.credit_score]], original LTV at 1.005 [[art:10f2f018:vif.orig_ltv]] and the seasonal sine at 1.004 [[art:5069e43c:vif.season_sin]].
Belsley's condition number of the column-standardised design is 4.954 [[art:d0edbe6f:condition_number]], below the declared bound of 30 [[art:7e52fd7a:threshold.M1.condition_number]].
On both readings the design shows no near-dependency strong enough, under the declared criteria, to render the coefficient estimates unstable.

### 5.2 Stability across the declared regimes

The champion's discrimination within each declared rate regime on train is set out below.

<!-- quaestor:renderer:begin table stability.auc_by_regime -->
The champion's AUC within each rate_regime on train [[art:9edbf2d0:stability.auc_by_regime]]:

| regime | n | event_rate | auc |
|---|---|---|---|
| falling | 17873 | 0.01438 | 1 |
| rising | 18140 | 0.002756 | 1 |
<!-- quaestor:renderer:end -->

The bound these per-regime values are read against is an across-regime AUC difference of 0.1 [[art:b64213d7:threshold.R1.auc_gap]].
A coefficient sign flip is counted only where the coefficient exceeds 0.05 [[art:aca84377:threshold.R1.sign_flip_coef]] in both regimes and reaches a |z| of at least 2 [[art:2e4428c7:threshold.R1.sign_flip_z]] in each.
On that joint test the flip indicator is 0 for the note rate [[art:e7ce4912:stability.note_rate.sign_flip]], 0 for incentive [[art:0cc7a37d:stability.incentive.sign_flip]], 0 for burnout [[art:6bc05e82:stability.burnout.sign_flip]], 0 for loan age [[art:b7191217:stability.loan_age.sign_flip]] and 0 for the spread-at-origination term [[art:1f302ccd:stability.sato.sign_flip]].
It is likewise 0 for credit score [[art:d956c276:stability.credit_score.sign_flip]], 0 for original LTV [[art:054d5fab:stability.orig_ltv.sign_flip]], 0 for the logged original balance [[art:fb1ae6c8:stability.orig_upb_log.sign_flip]], 0 for the logged beginning-of-month balance [[art:a9b4364d:stability.bom_balance_log.sign_flip]], 0 for the seasonal sine [[art:6ba36a3b:stability.season_sin.sign_flip]] and 0 for the seasonal cosine [[art:1850e2de:stability.season_cos.sign_flip]].
No retained feature therefore reverses the direction of its effect across the declared regimes at a magnitude and significance the criteria treat as material.

### 5.3 Rate-shock scenarios

Servicing value, its change from the base case and first-year prepayment speed are reported by shock below.

<!-- quaestor:renderer:begin table scenario.value_by_shock -->
Servicing value, its change from the base case and first-year CPR, by shock [[art:c4d5cb25:scenario.value_by_shock]]:

| shock_bp | value | value_change | cpr |
|---|---|---|---|
| -300 | 1.762e+06 | -92.11 | 0.0007734 |
| -200 | 1.762e+06 | -83.78 | 0.0007603 |
| -100 | 1.762e+06 | -57.15 | 0.0007469 |
| 0 | 1.762e+06 | 0 | 0.0007328 |
| 100 | 1.762e+06 | 77.18 | 0.0007184 |
| 200 | 1.762e+06 | 155.8 | 0.0007041 |
| 300 | 1.762e+06 | 232.8 | 0.0006902 |
<!-- quaestor:renderer:end -->

Going from the deepest downward shock to the largest upward shock, the change in servicing value is -92.11 [[art:0f83fead:scenario.value_change.-300]], then -83.78 [[art:75d82514:scenario.value_change.-200]], then -57.15 [[art:0445ffec:scenario.value_change.-100]], then 0 [[art:1e1b0b88:scenario.value_change.0]] at the base case, then 77.18 [[art:d16cc2a1:scenario.value_change.100]], then 155.8 [[art:4871ddee:scenario.value_change.200]] and then 232.8 [[art:a0678af4:scenario.value_change.300]].
The value change therefore increases at every step of the shock grid, so the curve is monotone in the rate shock, with the sign of the response in the direction expected of a servicing asset: value falls as rates rally and prepayments accelerate, and rises as rates sell off.
On the downward side the successive value changes crowd together as the shock deepens, so the response flattens into the rally rather than steepening.
The realised convexity, defined as the change at the deepest downward shock added to the change at the largest upward shock, is 140.7 [[art:4451c907:scenario.convexity]], and its positive sign means the gain in the sell-off outweighs the loss in the rally.
The package declares this quantity to be negative, and the realised value contradicts that declaration; this is finding X1, raised at high severity from the scenario run.
Because the declared direction is the assumption under which downside valuation and hedging behaviour would be reasoned about, the gap between the declared sign and the realised one is a limitation on the use of the scenario output until the declaration or the model's rate response is reconciled.
No other quantity reported in this section breaches the bound it was read against.

## 6. Findings and recommendations

Findings below are ordered by severity, highest first, and each carries the recomputed artifacts on which it rests, so that the source and extent of the model risk is characterised by evidence rather than by assertion [[reg:SR26-2:V]].

### F-001 · L1 leakage · severity **high**

**A single input separates the outcome perfectly on its own, so the model's discrimination is carried by a quantity that cannot be a genuine predictor of the event it precedes.**

The strongest single feature, `bom_balance_log`, reaches an AUC of 1 [[art:7f74c0d5:leakage.target_corr.max_single_feature_auc]] on train, above the declared ceiling of 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]] for what one feature may reach alone.

The number of features whose declared timing places them during or after the outcome is 0 [[art:742bcd24:leakage.timing.n_flagged]], so the declared timing table does not by itself account for the separation and the defect lies in how the feature is constructed rather than in how it is labelled.

<!-- quaestor:renderer:begin table leakage.target_corr -->
Each feature against the outcome on train, on its own [[art:ce82a409:leakage.target_corr]]:

| feature | abs_corr | single_feature_auc | numeric |
|---|---|---|---|
| note_rate | 0.0272 | 0.5826 | true |
| orig_ltv | 0.01822 | 0.5572 | true |
| credit_score | 0.03009 | 0.5959 | true |
| orig_upb_log | 0.02222 | 0.5675 | true |
| sato | 0.01787 | 0.5525 | true |
| loan_age | 0.04014 | 0.6284 | true |
| incentive | 0.07061 | 0.7239 | true |
| burnout | 0.05248 | 0.6732 | true |
| bom_balance_log | 0.9317 | 1 | true |
| season_sin | 0.005124 | 0.5149 | true |
| season_cos | 0.01658 | 0.553 | true |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table leakage.timing -->
Each feature's declared timing; flagged means during or after the outcome [[art:8cdad1c5:leakage.timing]]:

| feature | timing | flagged |
|---|---|---|
| note_rate | at_origination | false |
| orig_ltv | at_origination | false |
| credit_score | at_origination | false |
| orig_upb_log | at_origination | false |
| sato | at_origination | false |
| loan_age | before_period_start | false |
| incentive | before_period_start | false |
| burnout | before_period_start | false |
| bom_balance_log | before_period_start | false |
| rate_change_12m | before_period_start | false |
| season_sin | before_period_start | false |
| season_cos | before_period_start | false |
<!-- quaestor:renderer:end -->

The validator concludes that a feature at the maximum attainable single-feature AUC is contemporaneous with or derived from the outcome, and that every downstream performance statistic for this package is therefore uninterpretable as evidence of predictive skill.

The developer should trace `bom_balance_log` to its source field, establish the period in which its value becomes fixed relative to the prepayment outcome, and either rebuild it from information available at the as-of period or drop it and refit, then resubmit the package with the single-feature screen re-run.

### F-002 · X1 scenario analysis · severity **high**

**The servicing value profile across the rate shock grid curves in the opposite direction to the one the package declares, so the model misstates the sign of the asset's second-order rate sensitivity.**

The change in servicing value at the deepest downward rate shock on the grid is -92.11 [[art:0f83fead:scenario.value_change.-300]] and the change at the largest upward rate shock on the grid is 232.8 [[art:a0678af4:scenario.value_change.300]], the rise in the up-shock being the larger of the two in magnitude.

The realised convexity taken from those two changes is 140.7 [[art:4451c907:scenario.convexity]], a positive quantity, where `package.yaml` declares the convexity of this asset to be negative.

The subject's own projection record carries the same positive figure at 140.7 [[art:7d3ba32d:run.projection#convexity]], so the discrepancy is between the package's declared behaviour and its implemented behaviour rather than between two recomputations.

First-year CPR does move in the expected direction across the grid, at 0.0007734 [[art:7d3ba32d:run.projection#cpr_by_shock.-300]] under the deepest downward rate shock and 0.0006902 [[art:7d3ba32d:run.projection#cpr_by_shock.300]] under the largest upward rate shock, which places the defect in the transmission from prepayment speed to value rather than in the prepayment response itself.

<!-- quaestor:renderer:begin table scenario.value_by_shock -->
Servicing value, its change from the base case and first-year CPR, by shock [[art:c4d5cb25:scenario.value_by_shock]]:

| shock_bp | value | value_change | cpr |
|---|---|---|---|
| -300 | 1.762e+06 | -92.11 | 0.0007734 |
| -200 | 1.762e+06 | -83.78 | 0.0007603 |
| -100 | 1.762e+06 | -57.15 | 0.0007469 |
| 0 | 1.762e+06 | 0 | 0.0007328 |
| 100 | 1.762e+06 | 77.18 | 0.0007184 |
| 200 | 1.762e+06 | 155.8 | 0.0007041 |
| 300 | 1.762e+06 | 232.8 | 0.0006902 |
<!-- quaestor:renderer:end -->

The validator concludes that the shock grid reports rate sensitivity with the wrong curvature, so hedging, limit-setting or valuation decisions taken from this grid would be directed against the exposure they are meant to offset.

The developer should reconcile the cashflow and discounting path that maps prepayment speed to servicing value against the declared negative convexity, determine whether the declaration or the implementation is in error, correct the one that is wrong and re-run the shock grid before the package is used.

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1, S1), `compute_metrics` (T1, C1, O1), `check_leakage` (L2), `check_stability` (R1), `check_collinearity` (M1), `challenger_compare` (E1).

### Open items

Model developer — what does the model discriminate on, with the remaining features held fixed, such that the fitted coefficient on `burnout` carries sign -1 [[art:dcfb2de4:sign_check.burnout.coef_sign]] while that feature's own univariate direction on train is 1 [[art:bfc96bb2:sign_check.burnout.univariate_direction]], the agreement indicator read against that univariate direction standing at 0 [[art:56826e40:sign_check.burnout.agrees]]?

Model developer — what does the model discriminate on, with the remaining features held fixed, such that the fitted coefficient on `season_sin` carries sign -1 [[art:92ed5b5f:sign_check.season_sin.coef_sign]] while that feature's own univariate direction on train is 1 [[art:cae6b096:sign_check.season_sin.univariate_direction]], the agreement indicator read against that univariate direction standing at 0 [[art:74f2d0e0:sign_check.season_sin.agrees]]?

## 7. Ongoing monitoring recommendations

Ongoing monitoring evaluates the extent to which this model continues to perform as expected given potential changes in products, exposures, activities, clients, data relevance, or market conditions, and the plan below is scoped to the model's use and materiality rather than to a fixed template. [[reg:SR26-2:V.2]]

### Quantities to track and the bounds to track them against

Discrimination on realized prepayment outcomes should be recomputed on each production vintage as its performance window closes and compared against the floor of 0.65 [[art:fececac1:threshold.package.auc.test.min]] that package.yaml declares, which is the same bound this validation checked against and not a new one set by monitoring.
On the held-out test sample this validation recomputed discrimination of 1 [[art:4619bd69:metrics.test.auc]], above that declared floor.
A held-out value at the very top of the range this statistic can take is an expectation for monitoring to confirm against production outcomes, not a level to be assumed, because such a value can reflect the composition and separability of the development sample rather than the population the model will score in use.
Monitoring should therefore report the production value beside 1 [[art:4619bd69:metrics.test.auc]] and treat any sustained distance below it as a trigger for investigation well before the declared floor of 0.65 [[art:fececac1:threshold.package.auc.test.min]] is approached.

Input and score stability should be recomputed at each production reporting cycle, per feature and on the model score itself, holding the development sample as the fixed reference distribution so that successive cycles remain comparable to one another.
The largest train-to-test population shift observed in this validation, score included, was 0.06189 [[art:c2e8c8fd:psi.max]], which is below the ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]] declared in package.yaml and leaves headroom before that ceiling is reached.
The production series should be compared against that same ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]] and, separately, against the observed development level of 0.06189 [[art:c2e8c8fd:psi.max]], since drift that stays under the ceiling but climbs steadily away from the development level is informative earlier than a single breach is.
When a shift is reported for more than one sub-population, the monitoring report should state whether it is comparing the absolute gaps between them or the ratio of one to the other, and should report the comparison it did not lead with as well, because sub-populations whose absolute gaps are alike can differ materially on the ratio.

### How the monitoring report should order its evidence

The monitoring report should present calibration evidence before discrimination evidence, as section 4 of this report did, because package.yaml declares that this model's output is used as a probability and not only as a ranking.
Ordering the evidence that way keeps the quantity the business consumes, the level of the predicted probability, ahead of the quantity that only orders borrowers relative to one another.
Outcomes analysis on production vintages should compare predicted prepayment probabilities with realized prepayment, and persistent deviation outside the declared thresholds should be escalated for consideration of overlay, adjustment, recalibration, or redevelopment. [[reg:SR26-2:V.1.b]]

### The benchmark monitoring adds

Section 2 of this report compared a challenger model with the champion, so benchmarking against an alternative model is already part of this validation and monitoring is not being asked to supply it for the first time.
What monitoring adds is the comparison the development data cannot give: the challenger refitted on production vintages, rather than an external or vendor reference.
Refitting the challenger on production vintages separates divergence that comes from the population having moved from divergence that comes from the champion's specification, which a challenger frozen at development vintages cannot distinguish.
Discrepancies between champion and refitted challenger should prompt investigation into the source and degree of the difference rather than an automatic conclusion that the champion is in error, since the challenger is itself an alternative prediction. [[reg:SR11-7:V.1.b]]

### What this validation could not cover and monitoring should watch instead

This validation observed the model on development and held-out data, so the behaviour of the model under interest-rate and refinancing conditions outside the range spanned by that sample is something only production experience can show, and monitoring should record the prevailing rate environment alongside each performance cycle so that deterioration can be attributed or ruled out.
Process verification belongs to monitoring rather than to this validation: that servicing and loan-level data feeds remain accurate, complete, and consistent with the model's purpose, and that the implementing code is under change control with changes logged and auditable. [[reg:SR11-7:V.1.b]]
Overrides, where model output is ignored, altered, or reversed by users, should be logged with their reasons and their realized performance tracked, because a high override rate or overrides that consistently improve on the model is a signal about the model rather than about the users. [[reg:SR11-7:V.1.b]]
Prepayment is a long-horizon outcome, so back-testing on closed performance windows should be supplemented by early-warning metrics reported from shortly after implementation and by trend analysis of those metrics over time, with the early-warning metrics treated as a complement to back-testing and not a replacement for it. [[reg:SR11-7:V.1.c]]
The sensitivity and stability checks performed at development should be repeated on the same cadence as the stability reporting, and any input range or market condition in which the model was shown to be reliable should be monitored for the point at which it is approached or exceeded. [[reg:SR11-7:V.1.b]]
Material model risk can remain even after sound development and rigorous validation, so users of this model's output should be told its limitations and should supplement it with complementary analysis rather than rely on the monitoring thresholds alone as evidence of continued fitness. [[reg:SR26-2:V]]

## Appendix A — Claims

Grounding precision 0.9879 before repair (326 of 330 claims verified; 4 unsupported) and 1.0000 after 0 claim(s) rewritten and 4 number(s) removed from the prose. Per section (post-repair): summary 11/11; conceptual_soundness 75/75; data_integrity 75/75; outcomes 106/106; sensitivity 36/36; findings 15/15; monitoring 8/8.

Developer claims: The package declares 3 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). See Appendix D.

Excluded numeric tokens (not claims): section_number (5.1, 5.2, 5.3, section 4); citation_hash (2ad8d1a5, c5ebd9c9, e3abc1b8, 7898809e); regulatory_section_id (SR26-2:V, SR26-2:V.1.a, SR11-7:V.1.a, SR26-2:IV.1); finding_id (F-001, F-002); extractor_returned_excluded_token (12.0, 1.0, 2.0, 3.0).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | Quaestor re-executed the packaged subject end to end under t… | 300 | ratio | runtime.max_seconds |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 2 | summary | The training split holds 36013 rows and the test split holds… | 36013 | count | n | train | eq | `[[art:c5ebd9c9:profile.train.n]]` | verified | 36013 |
| 3 | summary | The training split holds 36013 rows and the test split holds… | 15382 | count | n | test | eq | `[[art:e3abc1b8:profile.test.n]]` | verified | 15382 |
| 4 | summary | Scoring also covers an out-of-time split of 12257 rows and a… | 12257 | count | n | out_of_time | eq | `[[art:7898809e:metrics.out_of_time.n]]` | verified | 12257 |
| 5 | summary | Scoring also covers an out-of-time split of 12257 rows and a… | 32177 | count | n | vintage_holdout | eq | `[[art:37a92951:metrics.vintage_holdout.n]]` | verified | 32177 |
| 6 | summary | Against the developer-declared minimum test discrimination o… | 0.65 | ratio | auc | test | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 7 | summary | Against the developer-declared minimum test discrimination o… | 1 | ratio | auc | test | eq | `[[art:4619bd69:metrics.test.auc]]` | verified | 1 |
| 8 | summary | Against the developer-declared population stability ceiling… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 9 | summary | Against the developer-declared population stability ceiling… | 0.06189 | ratio | psi |  | eq | `[[art:c2e8c8fd:psi.max]]` | verified | 0.06188985797 |
| 10 | summary | Discrimination is at the same level of 1 on the out-of-time… | 1 | ratio | auc | out_of_time | eq | `[[art:bcb747a3:metrics.out_of_time.auc]]` | verified | 1 |
| 11 | summary | Discrimination is at the same level of 1 on the out-of-time… | 1 | ratio | auc | vintage_holdout | eq | `[[art:00749c11:metrics.vintage_holdout.auc]]` | verified | 1 |
| 12 | conceptual_soundness | The champion is a logistic model of monthly prepayment with… | -9.211 | ratio | intercept |  | eq | `[[art:f6c2df89:run.model_summary#intercept]]` | verified | -9.21098863 |
| 13 | conceptual_soundness | The champion is a logistic model of monthly prepayment with… | 36013 | count | n_train | train | eq | `[[art:f6c2df89:run.model_summary#n_train]]` | verified | 36013 |
| 14 | conceptual_soundness | The champion is a logistic model of monthly prepayment with… | 934 | count | n_train_loans | train | eq | `[[art:f6c2df89:run.model_summary#n_train_loans]]` | verified | 934 |
| 15 | conceptual_soundness | The feature set carries 12 features in total. | 12 | count | n |  | eq | `[[art:61276a96:run.features#n]]` | verified | 12 |
| 16 | conceptual_soundness | Of these, 5 are fixed at origination and 7 are known before… | 5 | count | at_origination |  | eq | `[[art:61276a96:run.features#at_origination]]` | verified | 5 |
| 17 | conceptual_soundness | Of these, 5 are fixed at origination and 7 are known before… | 7 | count | before_period_start |  | eq | `[[art:61276a96:run.features#before_period_start]]` | verified | 7 |
| 18 | conceptual_soundness | The count of features first observable during the predicted… | 0 | count | during_period |  | eq | `[[art:61276a96:run.features#during_period]]` | verified | 0 |
| 19 | conceptual_soundness | The count of features first observable during the predicted… | 0 | count | after_outcome |  | eq | `[[art:61276a96:run.features#after_outcome]]` | verified | 0 |
| 20 | conceptual_soundness | The developer's own collinearity screen removed `rate_change… | 11.28 | ratio | vif |  | eq | `[[art:f6c2df89:run.model_summary#removed.rate_change_12m.vif]]` | verified | 11.281482 |
| 21 | conceptual_soundness | The developer's own collinearity screen removed `rate_change… | 10 | ratio | vif_threshold |  | eq | `[[art:f6c2df89:run.model_summary#vif_threshold]]` | verified | 10 |
| 22 | conceptual_soundness | The largest coefficient in magnitude by a wide margin is the… | -1.672 | ratio | coefficient |  | eq | `[[art:f6c2df89:run.model_summary#coefficients.bom_balance_log.value]]` | verified | -1.672066702 |
| 23 | conceptual_soundness | The largest coefficient in magnitude by a wide margin is the… | 0.4741 | ratio | coefficient |  | eq | `[[art:f6c2df89:run.model_summary#coefficients.orig_upb_log.value]]` | verified | 0.4740843675 |
| 24 | conceptual_soundness | The remaining terms sit well below those two in magnitude: t… | 0.02004 | ratio | coefficient |  | eq | `[[art:f6c2df89:run.model_summary#coefficients.incentive.value]]` | verified | 0.02003899053 |
| 25 | conceptual_soundness | The remaining terms sit well below those two in magnitude: t… | 0.01149 | ratio | coefficient |  | eq | `[[art:f6c2df89:run.model_summary#coefficients.credit_score.value]]` | verified | 0.01148861819 |
| 26 | conceptual_soundness | The remaining terms sit well below those two in magnitude: t… | 0.009311 | ratio | coefficient |  | eq | `[[art:f6c2df89:run.model_summary#coefficients.note_rate.value]]` | verified | 0.00931139845 |
| 27 | conceptual_soundness | The remaining terms sit well below those two in magnitude: t… | -0.008197 | ratio | coefficient |  | eq | `[[art:f6c2df89:run.model_summary#coefficients.burnout.value]]` | verified | -0.008197497662 |
| 28 | conceptual_soundness | The remaining terms sit well below those two in magnitude: t… | -0.00636 | ratio | coefficient |  | eq | `[[art:f6c2df89:run.model_summary#coefficients.orig_ltv.value]]` | verified | -0.006359519739 |
| 29 | conceptual_soundness | The remaining terms sit well below those two in magnitude: t… | 0.00387 | ratio | coefficient |  | eq | `[[art:f6c2df89:run.model_summary#coefficients.sato.value]]` | verified | 0.003870180498 |
| 30 | conceptual_soundness | The remaining terms sit well below those two in magnitude: t… | -0.005008 | ratio | coefficient |  | eq | `[[art:f6c2df89:run.model_summary#coefficients.season_cos.value]]` | verified | -0.005007633237 |
| 31 | conceptual_soundness | The remaining terms sit well below those two in magnitude: t… | -0.001276 | ratio | coefficient |  | eq | `[[art:f6c2df89:run.model_summary#coefficients.season_sin.value]]` | verified | -0.001276332193 |
| 32 | conceptual_soundness | The loan-age spline terms run 0.01175 , -0.02828 , -0.03906… | 0.01175 | ratio | coefficient |  | eq | `[[art:f6c2df89:run.model_summary#coefficients.loan_age_spline_1.value]]` | verified | 0.01174940768 |
| 33 | conceptual_soundness | The loan-age spline terms run 0.01175 , -0.02828 , -0.03906… | -0.02828 | ratio | coefficient |  | eq | `[[art:f6c2df89:run.model_summary#coefficients.loan_age_spline_2.value]]` | verified | -0.02828082109 |
| 34 | conceptual_soundness | The loan-age spline terms run 0.01175 , -0.02828 , -0.03906… | -0.03906 | ratio | coefficient |  | eq | `[[art:f6c2df89:run.model_summary#coefficients.loan_age_spline_3.value]]` | verified | -0.03905673436 |
| 35 | conceptual_soundness | The loan-age spline terms run 0.01175 , -0.02828 , -0.03906… | -0.05271 | ratio | coefficient |  | eq | `[[art:f6c2df89:run.model_summary#coefficients.loan_age_spline_4.value]]` | verified | -0.05271305715 |
| 36 | conceptual_soundness | The count of retained features whose fitted sign contradicts… | 2 | count | n_disagreements | train | eq | `[[art:66ce738a:sign_check.n_disagreements]]` | verified | 2 |
| 37 | conceptual_soundness | The first is burnout, whose fitted coefficient carries sign… | -1 | ratio | coef_sign |  | eq | `[[art:dcfb2de4:sign_check.burnout.coef_sign]]` | verified | -1 |
| 38 | conceptual_soundness | The first is burnout, whose fitted coefficient carries sign… | 1 | ratio | univariate_direction | train | eq | `[[art:bfc96bb2:sign_check.burnout.univariate_direction]]` | verified | 1 |
| 39 | conceptual_soundness | The first is burnout, whose fitted coefficient carries sign… | 0 | ratio | agrees |  | eq | `[[art:56826e40:sign_check.burnout.agrees]]` | verified | 0 |
| 40 | conceptual_soundness | Refitting the champion's form without burnout changes test A… | 0 | ratio | delta_auc | test | eq | `[[art:d50de877:ablation.burnout.delta_auc]]` | verified | 0 |
| 41 | conceptual_soundness | The second is the sine seasonality term, whose fitted coeffi… | -1 | ratio | coef_sign |  | eq | `[[art:92ed5b5f:sign_check.season_sin.coef_sign]]` | verified | -1 |
| 42 | conceptual_soundness | The second is the sine seasonality term, whose fitted coeffi… | 1 | ratio | univariate_direction | train | eq | `[[art:cae6b096:sign_check.season_sin.univariate_direction]]` | verified | 1 |
| 43 | conceptual_soundness | The second is the sine seasonality term, whose fitted coeffi… | 0 | ratio | agrees |  | eq | `[[art:74f2d0e0:sign_check.season_sin.agrees]]` | verified | 0 |
| 44 | conceptual_soundness | Refitting without it changes test AUC by 0 , so this disagre… | 0 | ratio | delta_auc | test | eq | `[[art:a4f7b0c1:ablation.season_sin.delta_auc]]` | verified | 0 |
| 45 | conceptual_soundness | The remaining checked features agree with their univariate d… | 1 | ratio | agrees |  | eq | `[[art:26b1789b:sign_check.bom_balance_log.agrees]]` | verified | 1 |
| 46 | conceptual_soundness | The remaining checked features agree with their univariate d… | -1 | ratio | coef_sign |  | eq | `[[art:d2e88db3:sign_check.bom_balance_log.coef_sign]]` | verified | -1 |
| 47 | conceptual_soundness | The remaining checked features agree with their univariate d… | -1 | ratio | univariate_direction | train | eq | `[[art:8ee4f8fe:sign_check.bom_balance_log.univariate_direction]]` | verified | -1 |
| 48 | conceptual_soundness | The remaining checked features agree with their univariate d… | 1 | ratio | agrees |  | eq | `[[art:915bf8eb:sign_check.credit_score.agrees]]` | verified | 1 |
| 49 | conceptual_soundness | The remaining checked features agree with their univariate d… | 1 | ratio | coef_sign |  | eq | `[[art:1ec1078b:sign_check.credit_score.coef_sign]]` | verified | 1 |
| 50 | conceptual_soundness | The remaining checked features agree with their univariate d… | 1 | ratio | univariate_direction | train | eq | `[[art:42303896:sign_check.credit_score.univariate_direction]]` | verified | 1 |
| 51 | conceptual_soundness | The remaining checked features agree with their univariate d… | 1 | ratio | agrees |  | eq | `[[art:f7b2338e:sign_check.incentive.agrees]]` | verified | 1 |
| 52 | conceptual_soundness | The remaining checked features agree with their univariate d… | 1 | ratio | coef_sign |  | eq | `[[art:684cf11a:sign_check.incentive.coef_sign]]` | verified | 1 |
| 53 | conceptual_soundness | The remaining checked features agree with their univariate d… | 1 | ratio | univariate_direction | train | eq | `[[art:8098d951:sign_check.incentive.univariate_direction]]` | verified | 1 |
| 54 | conceptual_soundness | The remaining checked features agree with their univariate d… | 1 | ratio | agrees |  | eq | `[[art:ca18290e:sign_check.note_rate.agrees]]` | verified | 1 |
| 55 | conceptual_soundness | The remaining checked features agree with their univariate d… | 1 | ratio | coef_sign |  | eq | `[[art:0e3296a5:sign_check.note_rate.coef_sign]]` | verified | 1 |
| 56 | conceptual_soundness | The remaining checked features agree with their univariate d… | 1 | ratio | univariate_direction | train | eq | `[[art:61f6e1ac:sign_check.note_rate.univariate_direction]]` | verified | 1 |
| 57 | conceptual_soundness | The remaining checked features agree with their univariate d… | 1 | ratio | agrees |  | eq | `[[art:7021aeb0:sign_check.orig_ltv.agrees]]` | verified | 1 |
| 58 | conceptual_soundness | The remaining checked features agree with their univariate d… | -1 | ratio | coef_sign |  | eq | `[[art:7eec65ec:sign_check.orig_ltv.coef_sign]]` | verified | -1 |
| 59 | conceptual_soundness | The remaining checked features agree with their univariate d… | -1 | ratio | univariate_direction | train | eq | `[[art:76dbc708:sign_check.orig_ltv.univariate_direction]]` | verified | -1 |
| 60 | conceptual_soundness | The remaining checked features agree with their univariate d… | 1 | ratio | agrees |  | eq | `[[art:07a9d3e6:sign_check.orig_upb_log.agrees]]` | verified | 1 |
| 61 | conceptual_soundness | The remaining checked features agree with their univariate d… | 1 | ratio | coef_sign |  | eq | `[[art:5aa309fc:sign_check.orig_upb_log.coef_sign]]` | verified | 1 |
| 62 | conceptual_soundness | The remaining checked features agree with their univariate d… | 1 | ratio | univariate_direction | train | eq | `[[art:b9743ecb:sign_check.orig_upb_log.univariate_direction]]` | verified | 1 |
| 63 | conceptual_soundness | The remaining checked features agree with their univariate d… | 1 | ratio | agrees |  | eq | `[[art:2401eba2:sign_check.sato.agrees]]` | verified | 1 |
| 64 | conceptual_soundness | The remaining checked features agree with their univariate d… | 1 | ratio | coef_sign |  | eq | `[[art:c031d0d5:sign_check.sato.coef_sign]]` | verified | 1 |
| 65 | conceptual_soundness | The remaining checked features agree with their univariate d… | 1 | ratio | univariate_direction | train | eq | `[[art:c08233a6:sign_check.sato.univariate_direction]]` | verified | 1 |
| 66 | conceptual_soundness | The remaining checked features agree with their univariate d… | 1 | ratio | agrees |  | eq | `[[art:7f18ddf7:sign_check.season_cos.agrees]]` | verified | 1 |
| 67 | conceptual_soundness | The remaining checked features agree with their univariate d… | -1 | ratio | coef_sign |  | eq | `[[art:7dbb1ffc:sign_check.season_cos.coef_sign]]` | verified | -1 |
| 68 | conceptual_soundness | The remaining checked features agree with their univariate d… | -1 | ratio | univariate_direction | train | eq | `[[art:03e931f0:sign_check.season_cos.univariate_direction]]` | verified | -1 |
| 69 | conceptual_soundness | The ablations are measured from a refit of the champion's fo… | 1 | ratio | baseline_auc | test | eq | `[[art:7610ff35:ablation.baseline_auc]]` | verified | 1 |
| 70 | conceptual_soundness | Dropping current balance changes test AUC by -0.2327 , the o… | -0.2327 | ratio | delta_auc | test | eq | `[[art:c226f60f:ablation.bom_balance_log.delta_auc]]` | verified | -0.2327007725 |
| 71 | conceptual_soundness | Dropping burnout changes it by 0 , credit score by 0 , the r… | 0 | ratio | delta_auc | test | eq | `[[art:d50de877:ablation.burnout.delta_auc]]` | verified | 0 |
| 72 | conceptual_soundness | Dropping burnout changes it by 0 , credit score by 0 , the r… | 0 | ratio | delta_auc | test | eq | `[[art:d1dff006:ablation.credit_score.delta_auc]]` | verified | 0 |
| 73 | conceptual_soundness | Dropping burnout changes it by 0 , credit score by 0 , the r… | 0 | ratio | delta_auc | test | eq | `[[art:33a25e3c:ablation.incentive.delta_auc]]` | verified | 0 |
| 74 | conceptual_soundness | Dropping burnout changes it by 0 , credit score by 0 , the r… | 0 | ratio | delta_auc | test | eq | `[[art:1a789b08:ablation.loan_age.delta_auc]]` | verified | 0 |
| 75 | conceptual_soundness | Dropping burnout changes it by 0 , credit score by 0 , the r… | 0 | ratio | delta_auc | test | eq | `[[art:65b3f07a:ablation.note_rate.delta_auc]]` | verified | 0 |
| 76 | conceptual_soundness | Dropping burnout changes it by 0 , credit score by 0 , the r… | 0 | ratio | delta_auc | test | eq | `[[art:370eaea8:ablation.orig_ltv.delta_auc]]` | verified | 0 |
| 77 | conceptual_soundness | Dropping burnout changes it by 0 , credit score by 0 , the r… | 0 | ratio | delta_auc | test | eq | `[[art:e245ef14:ablation.orig_upb_log.delta_auc]]` | verified | 0 |
| 78 | conceptual_soundness | Dropping burnout changes it by 0 , credit score by 0 , the r… | 0 | ratio | delta_auc | test | eq | `[[art:2bbb0015:ablation.sato.delta_auc]]` | verified | 0 |
| 79 | conceptual_soundness | Dropping burnout changes it by 0 , credit score by 0 , the r… | 0 | ratio | delta_auc | test | eq | `[[art:9453331c:ablation.season_cos.delta_auc]]` | verified | 0 |
| 80 | conceptual_soundness | Dropping burnout changes it by 0 , credit score by 0 , the r… | 0 | ratio | delta_auc | test | eq | `[[art:a4f7b0c1:ablation.season_sin.delta_auc]]` | verified | 0 |
| 81 | conceptual_soundness | The challenger scores 1 on test against the champion's recom… | 1 | ratio | auc | test | eq | `[[art:5aeaf534:challenger.auc]]` | verified | 1 |
| 82 | conceptual_soundness | The challenger scores 1 on test against the champion's recom… | 1 | ratio | auc | test | eq | `[[art:4619bd69:metrics.test.auc]]` | verified | 1 |
| 83 | conceptual_soundness | The challenger scores 1 on test against the champion's recom… | 0 | ratio | delta_auc | test | eq | `[[art:d8eca8f5:challenger.delta_auc]]` | verified | 0 |
| 84 | conceptual_soundness | The threshold at which a challenger's lead over the champion… | 0.03 | ratio | delta_auc |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 85 | conceptual_soundness | On calibration the two are not identical: the champion's Bri… | 1.011e-08 | ratio | brier | test | eq | `[[art:67fd4fea:metrics.test.brier]]` | verified | 1.01061577e-08 |
| 86 | conceptual_soundness | On calibration the two are not identical: the champion's Bri… | 3.226e-13 | ratio | brier | test | eq | `[[art:0b5236ca:challenger.brier]]` | verified | 3.226460021e-13 |
| 87 | data_integrity | The training split holds 36013 rows, the test split 15382 ,… | 36013 | count | n | train | eq | `[[art:c5ebd9c9:profile.train.n]]` | verified | 36013 |
| 88 | data_integrity | The training split holds 36013 rows, the test split 15382 ,… | 15382 | count | n | test | eq | `[[art:e3abc1b8:profile.test.n]]` | verified | 15382 |
| 89 | data_integrity | The training split holds 36013 rows, the test split 15382 ,… | 32177 | count | n | vintage_holdout | eq | `[[art:426e712a:profile.vintage_holdout.n]]` | verified | 32177 |
| 90 | data_integrity | The training split holds 36013 rows, the test split 15382 ,… | 12257 | count | n | out_of_time | eq | `[[art:fa39c5cf:profile.out_of_time.n]]` | verified | 12257 |
| 91 | data_integrity | The largest missing fraction is 0 in train, 0 in test, 0 in… | 0 | ratio | missing | train | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 92 | data_integrity | The largest missing fraction is 0 in train, 0 in test, 0 in… | 0 | ratio | missing | test | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 93 | data_integrity | The largest missing fraction is 0 in train, 0 in test, 0 in… | 0 | ratio | missing | vintage_holdout | eq | `[[art:329bb430:profile.vintage_holdout.missing.max]]` | verified | 0 |
| 94 | data_integrity | The largest missing fraction is 0 in train, 0 in test, 0 in… | 0 | ratio | missing | out_of_time | eq | `[[art:4dafce11:profile.out_of_time.missing.max]]` | verified | 0 |
| 95 | data_integrity | No split's largest missing fraction stands apart from anothe… | 0.1 | ratio | missing_gap |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 96 | data_integrity | The largest train-to-test population stability index, the sc… | 0.06189 | ratio | psi |  | eq | `[[art:c2e8c8fd:psi.max]]` | verified | 0.06188985797 |
| 97 | data_integrity | The largest train-to-test population stability index, the sc… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 98 | data_integrity | The largest train-to-test population stability index, the sc… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 99 | data_integrity | That maximum is credit_score at 0.06189 , followed by orig_u… | 0.06189 | ratio | psi |  | eq | `[[art:7e87527c:psi.credit_score]]` | verified | 0.06188985797 |
| 100 | data_integrity | That maximum is credit_score at 0.06189 , followed by orig_u… | 0.04817 | ratio | psi |  | eq | `[[art:55030a3b:psi.orig_upb_log]]` | verified | 0.04817081196 |
| 101 | data_integrity | That maximum is credit_score at 0.06189 , followed by orig_u… | 0.03617 | ratio | psi |  | eq | `[[art:cd1ff136:psi.orig_ltv]]` | verified | 0.03617297258 |
| 102 | data_integrity | That maximum is credit_score at 0.06189 , followed by orig_u… | 0.03018 | ratio | psi |  | eq | `[[art:ce3c425c:psi.bom_balance_log]]` | verified | 0.03017956995 |
| 103 | data_integrity | That maximum is credit_score at 0.06189 , followed by orig_u… | 0.02773 | ratio | psi |  | eq | `[[art:584da64f:psi.sato]]` | verified | 0.02772829856 |
| 104 | data_integrity | The remaining train-to-test indices sit lower still: note_ra… | 0.01371 | ratio | psi |  | eq | `[[art:ecc6adf3:psi.note_rate]]` | verified | 0.01370911382 |
| 105 | data_integrity | The remaining train-to-test indices sit lower still: note_ra… | 0.004614 | ratio | psi |  | eq | `[[art:9dc7ecc2:psi.burnout]]` | verified | 0.004614338236 |
| 106 | data_integrity | The remaining train-to-test indices sit lower still: note_ra… | 0.0009923 | ratio | psi |  | eq | `[[art:2da5570f:psi.incentive]]` | verified | 0.0009922551416 |
| 107 | data_integrity | The remaining train-to-test indices sit lower still: note_ra… | 0.0001994 | ratio | psi |  | eq | `[[art:2202b157:psi.loan_age]]` | verified | 0.0001993816816 |
| 108 | data_integrity | The remaining train-to-test indices sit lower still: note_ra… | 1.79e-05 | ratio | psi |  | eq | `[[art:addec503:psi.season_cos]]` | verified | 1.790085913e-05 |
| 109 | data_integrity | The remaining train-to-test indices sit lower still: note_ra… | 2.939e-06 | ratio | psi |  | eq | `[[art:4d2ed98d:psi.season_sin]]` | verified | 2.939045338e-06 |
| 110 | data_integrity | The remaining train-to-test indices sit lower still: note_ra… | 0.01874 | ratio | psi |  | eq | `[[art:2ad82680:psi.y_score]]` | verified | 0.01873789359 |
| 111 | data_integrity | Read against the same declared bound of 0.25 , the train-to-… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 112 | data_integrity | Burnout stands at 2.945 , loan_age at 2.484 , note_rate at 0… | 2.945 | ratio | psi | out_of_time | eq | `[[art:7b0bbebb:psi.out_of_time.burnout]]` | verified | 2.944521522 |
| 113 | data_integrity | Burnout stands at 2.945 , loan_age at 2.484 , note_rate at 0… | 2.484 | ratio | psi | out_of_time | eq | `[[art:d6eaaaf5:psi.out_of_time.loan_age]]` | verified | 2.483993033 |
| 114 | data_integrity | Burnout stands at 2.945 , loan_age at 2.484 , note_rate at 0… | 0.6977 | ratio | psi | out_of_time | eq | `[[art:cabd371d:psi.out_of_time.note_rate]]` | verified | 0.6976589281 |
| 115 | data_integrity | Burnout stands at 2.945 , loan_age at 2.484 , note_rate at 0… | 0.4958 | ratio | psi | out_of_time | eq | `[[art:42076ed1:psi.out_of_time.incentive]]` | verified | 0.4958065489 |
| 116 | data_integrity | The other out-of-time indices remain under it: bom_balance_l… | 0.08708 | ratio | psi | out_of_time | eq | `[[art:9fa682d1:psi.out_of_time.bom_balance_log]]` | verified | 0.08707630682 |
| 117 | data_integrity | The other out-of-time indices remain under it: bom_balance_l… | 0.07136 | ratio | psi | out_of_time | eq | `[[art:ac349b67:psi.out_of_time.orig_upb_log]]` | verified | 0.07136421414 |
| 118 | data_integrity | The other out-of-time indices remain under it: bom_balance_l… | 0.05988 | ratio | psi | out_of_time | eq | `[[art:d7249e47:psi.out_of_time.credit_score]]` | verified | 0.05987964443 |
| 119 | data_integrity | The other out-of-time indices remain under it: bom_balance_l… | 0.04301 | ratio | psi | out_of_time | eq | `[[art:3eee5db4:psi.out_of_time.orig_ltv]]` | verified | 0.04300793312 |
| 120 | data_integrity | The other out-of-time indices remain under it: bom_balance_l… | 0.02789 | ratio | psi | out_of_time | eq | `[[art:144e1bd9:psi.out_of_time.season_sin]]` | verified | 0.02788988464 |
| 121 | data_integrity | The other out-of-time indices remain under it: bom_balance_l… | 0.01299 | ratio | psi | out_of_time | eq | `[[art:c2233ce6:psi.out_of_time.sato]]` | verified | 0.01298850667 |
| 122 | data_integrity | The other out-of-time indices remain under it: bom_balance_l… | 0.007524 | ratio | psi | out_of_time | eq | `[[art:25cf6b85:psi.out_of_time.season_cos]]` | verified | 0.00752368457 |
| 123 | data_integrity | The score shifts less than the worst of its inputs, at 0.145… | 0.1451 | ratio | psi | out_of_time | eq | `[[art:12620838:psi.out_of_time.y_score]]` | verified | 0.1450932669 |
| 124 | data_integrity | The score shifts less than the worst of its inputs, at 0.145… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 125 | data_integrity | The vintage holdout sits between the two: read against the d… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 126 | data_integrity | The vintage holdout sits between the two: read against the d… | 0.6088 | ratio | psi | vintage_holdout | eq | `[[art:f281f8a7:psi.vintage_holdout.note_rate]]` | verified | 0.608822927 |
| 127 | data_integrity | The vintage holdout sits between the two: read against the d… | 0.4475 | ratio | psi | vintage_holdout | eq | `[[art:5e61b6f9:psi.vintage_holdout.incentive]]` | verified | 0.4475226601 |
| 128 | data_integrity | Every other input is below that bound: loan_age at 0.07112 ,… | 0.07112 | ratio | psi | vintage_holdout | eq | `[[art:6d92c48b:psi.vintage_holdout.loan_age]]` | verified | 0.07111526296 |
| 129 | data_integrity | Every other input is below that bound: loan_age at 0.07112 ,… | 0.04749 | ratio | psi | vintage_holdout | eq | `[[art:e29067e6:psi.vintage_holdout.burnout]]` | verified | 0.04749372789 |
| 130 | data_integrity | Every other input is below that bound: loan_age at 0.07112 ,… | 0.0404 | ratio | psi | vintage_holdout | eq | `[[art:77ec758a:psi.vintage_holdout.orig_upb_log]]` | verified | 0.04039645306 |
| 131 | data_integrity | Every other input is below that bound: loan_age at 0.07112 ,… | 0.03996 | ratio | psi | vintage_holdout | eq | `[[art:3498d307:psi.vintage_holdout.credit_score]]` | verified | 0.03995819732 |
| 132 | data_integrity | Every other input is below that bound: loan_age at 0.07112 ,… | 0.03707 | ratio | psi | vintage_holdout | eq | `[[art:b3073b46:psi.vintage_holdout.bom_balance_log]]` | verified | 0.03706738664 |
| 133 | data_integrity | Every other input is below that bound: loan_age at 0.07112 ,… | 0.02989 | ratio | psi | vintage_holdout | eq | `[[art:eea64c25:psi.vintage_holdout.sato]]` | verified | 0.02989256711 |
| 134 | data_integrity | Every other input is below that bound: loan_age at 0.07112 ,… | 0.02942 | ratio | psi | vintage_holdout | eq | `[[art:d07cfb7d:psi.vintage_holdout.orig_ltv]]` | verified | 0.0294150369 |
| 135 | data_integrity | Every other input is below that bound: loan_age at 0.07112 ,… | 0.001288 | ratio | psi | vintage_holdout | eq | `[[art:9fe842a8:psi.vintage_holdout.season_cos]]` | verified | 0.0012879007 |
| 136 | data_integrity | Every other input is below that bound: loan_age at 0.07112 ,… | 0.0007309 | ratio | psi | vintage_holdout | eq | `[[art:b0dc9745:psi.vintage_holdout.season_sin]]` | verified | 0.0007309374015 |
| 137 | data_integrity | Every other input is below that bound: loan_age at 0.07112 ,… | 0.05813 | ratio | psi | vintage_holdout | eq | `[[art:33ffbed6:psi.vintage_holdout.y_score]]` | verified | 0.05813498782 |
| 138 | data_integrity | Characteristic stability, which attributes the shift in the… | 0.03215 | ratio | csi |  | eq | `[[art:60a10892:csi.bom_balance_log]]` | verified | 0.03214820108 |
| 139 | data_integrity | Characteristic stability, which attributes the shift in the… | 0.03215 | ratio | csi |  | eq | `[[art:b2440ca1:csi.max]]` | verified | 0.03214820108 |
| 140 | data_integrity | The rest contribute far less: orig_upb_log at 0.004636 , ori… | 0.004636 | ratio | csi |  | eq | `[[art:5d1c16f2:csi.orig_upb_log]]` | verified | 0.004635722963 |
| 141 | data_integrity | The rest contribute far less: orig_upb_log at 0.004636 , ori… | 0.0008996 | ratio | csi |  | eq | `[[art:7ea837e1:csi.orig_ltv]]` | verified | 0.0008996218814 |
| 142 | data_integrity | The rest contribute far less: orig_upb_log at 0.004636 , ori… | 0.000449 | ratio | csi |  | eq | `[[art:fb71eb9e:csi.sato]]` | verified | 0.0004490205147 |
| 143 | data_integrity | The rest contribute far less: orig_upb_log at 0.004636 , ori… | 0.0003806 | ratio | csi |  | eq | `[[art:587b33e9:csi.note_rate]]` | verified | 0.0003806385501 |
| 144 | data_integrity | The rest contribute far less: orig_upb_log at 0.004636 , ori… | 0.000223 | ratio | csi |  | eq | `[[art:d87a2d40:csi.credit_score]]` | verified | 0.000223048204 |
| 145 | data_integrity | The rest contribute far less: orig_upb_log at 0.004636 , ori… | 0.0001016 | ratio | csi |  | eq | `[[art:a5da1daa:csi.burnout]]` | verified | 0.0001015529196 |
| 146 | data_integrity | The rest contribute far less: orig_upb_log at 0.004636 , ori… | 9.278e-05 | ratio | csi |  | eq | `[[art:41325258:csi.incentive]]` | verified | 9.278494663e-05 |
| 147 | data_integrity | The rest contribute far less: orig_upb_log at 0.004636 , ori… | 1.935e-05 | ratio | csi |  | eq | `[[art:de66f2c6:csi.season_cos]]` | verified | 1.934566399e-05 |
| 148 | data_integrity | The rest contribute far less: orig_upb_log at 0.004636 , ori… | 1.386e-06 | ratio | csi |  | eq | `[[art:4c3f0dd9:csi.season_sin]]` | verified | 1.386212619e-06 |
| 149 | data_integrity | The rest contribute far less: orig_upb_log at 0.004636 , ori… | 0 | ratio | csi |  | eq | `[[art:df52c920:csi.loan_age]]` | verified | 0 |
| 150 | data_integrity | No characteristic contribution approaches the declared stabi… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 151 | data_integrity | The timing screen flags 0 features declared as observed duri… | 0 | count | n_flagged |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 152 | data_integrity | The target-adjacent name screen matches 0 feature names, so… | 0 | count | n_matched |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 153 | data_integrity | The single-feature discrimination screen is the exception: t… | 1 | ratio | single_feature_auc |  | eq | `[[art:7f74c0d5:leakage.target_corr.max_single_feature_auc]]` | verified | 1 |
| 154 | data_integrity | The single-feature discrimination screen is the exception: t… | 0.9 | ratio | single_feature_auc |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 155 | data_integrity | That the same input also carries the largest characteristic… | 0.03215 | ratio | csi |  | eq | `[[art:60a10892:csi.bom_balance_log]]` | verified | 0.03214820108 |
| 156 | data_integrity | The share of test rows whose identifying keys also identify… | 0 | ratio | overlap_ids |  | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 157 | data_integrity | The share of test rows whose identifying keys also identify… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 158 | data_integrity | The share of test rows whose feature values also appear in t… | 0 | ratio | overlap_features |  | eq | `[[art:0fec8048:leakage.overlap.features]]` | verified | 0 |
| 159 | data_integrity | The share of test rows whose feature values also appear in t… | 0.005 | ratio | overlap |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 160 | data_integrity | The share of test rows whose feature values also appear in t… | 0 | ratio | duplicates | train | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 161 | data_integrity | The row-overlap screen reported alongside them is likewise 0… | 0 | ratio | overlap |  | eq | `[[art:4c9fcd09:leakage.overlap]]` | verified | 0 |
| 162 | outcomes | The subject reports a calibration slope of 2.867 on train, 2… | 2.867 | ratio | calibration_slope | train | eq | `[[art:e8f6c83d:run.metrics#train.calibration_slope]]` | verified | 2.866529812 |
| 163 | outcomes | The subject reports a calibration slope of 2.867 on train, 2… | 2.833 | ratio | calibration_slope | test | eq | `[[art:e8f6c83d:run.metrics#test.calibration_slope]]` | verified | 2.833229739 |
| 164 | outcomes | The subject reports a calibration slope of 2.867 on train, 2… | 2.924 | ratio | calibration_slope | out_of_time | eq | `[[art:e8f6c83d:run.metrics#out_of_time.calibration_slope]]` | verified | 2.924389935 |
| 165 | outcomes | The subject reports a calibration slope of 2.867 on train, 2… | 2.797 | ratio | calibration_slope | vintage_holdout | eq | `[[art:e8f6c83d:run.metrics#vintage_holdout.calibration_slope]]` | verified | 2.797139199 |
| 166 | outcomes | The declared band for that slope runs from 0.8 to 1.2 , and… | 0.8 | ratio | calibration_slope |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 167 | outcomes | The declared band for that slope runs from 0.8 to 1.2 , and… | 1.2 | ratio | calibration_slope |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 168 | outcomes | The indicator that the predictions separate the outcome stan… | 1 | ratio | separable | train | eq | `[[art:d7ee2241:calibration.separable.train]]` | verified | 1 |
| 169 | outcomes | The indicator that the predictions separate the outcome stan… | 1 | ratio | separable | test | eq | `[[art:81c3fa7a:calibration.separable.test]]` | verified | 1 |
| 170 | outcomes | The indicator that the predictions separate the outcome stan… | 1 | ratio | separable | out_of_time | eq | `[[art:258b7972:calibration.separable.out_of_time]]` | verified | 1 |
| 171 | outcomes | The indicator that the predictions separate the outcome stan… | 1 | ratio | separable | vintage_holdout | eq | `[[art:137e2c39:calibration.separable.vintage_holdout]]` | verified | 1 |
| 172 | outcomes | Mean predicted probability on train is 0.008607 against an o… | 0.008607 | ratio | mean_predicted | train | eq | `[[art:6f9330ed:metrics.train.mean_predicted]]` | verified | 0.008606994732 |
| 173 | outcomes | Mean predicted probability on train is 0.008607 against an o… | 0.008525 | ratio | event_rate | train | eq | `[[art:b9ef3327:metrics.train.event_rate]]` | verified | 0.008524699414 |
| 174 | outcomes | Mean predicted probability on train is 0.008607 against an o… | 0.009654 | ratio | mean_rel_gap | train | eq | `[[art:db1bca38:calibration.mean_rel_gap.train]]` | verified | 0.009653750145 |
| 175 | outcomes | On test the mean predicted probability is 0.008144 against a… | 0.008144 | ratio | mean_predicted | test | eq | `[[art:83863be2:metrics.test.mean_predicted]]` | verified | 0.008144072878 |
| 176 | outcomes | On test the mean predicted probability is 0.008144 against a… | 0.008061 | ratio | event_rate | test | eq | `[[art:570cc08a:metrics.test.event_rate]]` | verified | 0.008061370433 |
| 177 | outcomes | On test the mean predicted probability is 0.008144 against a… | 0.01026 | ratio | mean_rel_gap | test | eq | `[[art:4e1854b1:calibration.mean_rel_gap.test]]` | verified | 0.01025910486 |
| 178 | outcomes | Out of time the mean predicted probability is 0.01802 agains… | 0.01802 | ratio | mean_predicted | out_of_time | eq | `[[art:276f106a:metrics.out_of_time.mean_predicted]]` | verified | 0.01801915996 |
| 179 | outcomes | Out of time the mean predicted probability is 0.01802 agains… | 0.01795 | ratio | event_rate | out_of_time | eq | `[[art:83ccf5c0:metrics.out_of_time.event_rate]]` | verified | 0.01794892714 |
| 180 | outcomes | Out of time the mean predicted probability is 0.01802 agains… | 0.003913 | ratio | mean_rel_gap | out_of_time | eq | `[[art:68619260:calibration.mean_rel_gap.out_of_time]]` | verified | 0.003912925468 |
| 181 | outcomes | On the vintage holdout the mean predicted probability is 0.0… | 0.004899 | ratio | mean_predicted | vintage_holdout | eq | `[[art:af925790:metrics.vintage_holdout.mean_predicted]]` | verified | 0.004898804843 |
| 182 | outcomes | On the vintage holdout the mean predicted probability is 0.0… | 0.004817 | ratio | event_rate | vintage_holdout | eq | `[[art:e3590a16:metrics.vintage_holdout.event_rate]]` | verified | 0.004817105386 |
| 183 | outcomes | On the vintage holdout the mean predicted probability is 0.0… | 0.01696 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:1438e44d:calibration.mean_rel_gap.vintage_holdout]]` | verified | 0.01696028022 |
| 184 | outcomes | The tolerance on that relative gap is 0.25 , and each of the… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 185 | outcomes | Comparing those gaps against one another as differences in t… | 0.01696 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:1438e44d:calibration.mean_rel_gap.vintage_holdout]]` | verified | 0.01696028022 |
| 186 | outcomes | Comparing those gaps against one another as differences in t… | 0.003913 | ratio | mean_rel_gap | out_of_time | eq | `[[art:68619260:calibration.mean_rel_gap.out_of_time]]` | verified | 0.003912925468 |
| 187 | outcomes | Comparing those gaps against one another as differences in t… | 0.01026 | ratio | mean_rel_gap | test | eq | `[[art:4e1854b1:calibration.mean_rel_gap.test]]` | verified | 0.01025910486 |
| 188 | outcomes | Comparing those gaps against one another as differences in t… | 0.009654 | ratio | mean_rel_gap | train | eq | `[[art:db1bca38:calibration.mean_rel_gap.train]]` | verified | 0.009653750145 |
| 189 | outcomes | In portfolio terms, the mean absolute difference between act… | 0.000928 | ratio | mae | train | eq | `[[art:99b2b87f:cpr.train.mae]]` | verified | 0.0009279500644 |
| 190 | outcomes | In portfolio terms, the mean absolute difference between act… | 0.0009292 | ratio | mae | test | eq | `[[art:be219b85:cpr.test.mae]]` | verified | 0.0009292114418 |
| 191 | outcomes | In portfolio terms, the mean absolute difference between act… | 0.0007118 | ratio | mae | out_of_time | eq | `[[art:bdc9d54f:cpr.out_of_time.mae]]` | verified | 0.0007117577187 |
| 192 | outcomes | In portfolio terms, the mean absolute difference between act… | 0.0009299 | ratio | mae | vintage_holdout | eq | `[[art:d1a19e91:cpr.vintage_holdout.mae]]` | verified | 0.0009298655279 |
| 193 | outcomes | On test the actual CPR is 0.09256 against a predicted 0.0934… | 0.09256 | ratio | cpr_actual | test | eq | `[[art:e8f6c83d:run.metrics#test.cpr_actual]]` | verified | 0.09256057792 |
| 194 | outcomes | On test the actual CPR is 0.09256 against a predicted 0.0934… | 0.09347 | ratio | cpr_predicted | test | eq | `[[art:e8f6c83d:run.metrics#test.cpr_predicted]]` | verified | 0.09346805004 |
| 195 | outcomes | On test the actual CPR is 0.09256 against a predicted 0.0934… | 0.1953 | ratio | cpr_actual | out_of_time | eq | `[[art:e8f6c83d:run.metrics#out_of_time.cpr_actual]]` | verified | 0.1953465213 |
| 196 | outcomes | On test the actual CPR is 0.09256 against a predicted 0.0934… | 0.196 | ratio | cpr_predicted | out_of_time | eq | `[[art:e8f6c83d:run.metrics#out_of_time.cpr_predicted]]` | verified | 0.1960368014 |
| 197 | outcomes | \| AUC \| 1 \| 1 \| 1 \| 1 \| | 1 | ratio | auc | train | eq | `[[art:6269694d:metrics.train.auc]]` | verified | 1 |
| 198 | outcomes | \| AUC \| 1 \| 1 \| 1 \| 1 \| | 1 | ratio | auc | test | eq | `[[art:4619bd69:metrics.test.auc]]` | verified | 1 |
| 199 | outcomes | \| AUC \| 1 \| 1 \| 1 \| 1 \| | 1 | ratio | auc | out_of_time | eq | `[[art:bcb747a3:metrics.out_of_time.auc]]` | verified | 1 |
| 200 | outcomes | \| AUC \| 1 \| 1 \| 1 \| 1 \| | 1 | ratio | auc | vintage_holdout | eq | `[[art:00749c11:metrics.vintage_holdout.auc]]` | verified | 1 |
| 201 | outcomes | \| Gini \| 1 \| 1 \| 1 \| 1 \| | 1 | ratio | gini | train | eq | `[[art:e2084e07:metrics.train.gini]]` | verified | 1 |
| 202 | outcomes | \| Gini \| 1 \| 1 \| 1 \| 1 \| | 1 | ratio | gini | test | eq | `[[art:35acd744:metrics.test.gini]]` | verified | 1 |
| 203 | outcomes | \| Gini \| 1 \| 1 \| 1 \| 1 \| | 1 | ratio | gini | out_of_time | eq | `[[art:6d939d01:metrics.out_of_time.gini]]` | verified | 1 |
| 204 | outcomes | \| Gini \| 1 \| 1 \| 1 \| 1 \| | 1 | ratio | gini | vintage_holdout | eq | `[[art:f4aa377a:metrics.vintage_holdout.gini]]` | verified | 1 |
| 205 | outcomes | \| KS \| 1 \| 1 \| 1 \| 1 \| | 1 | ratio | ks | train | eq | `[[art:24c2277d:metrics.train.ks]]` | verified | 1 |
| 206 | outcomes | \| KS \| 1 \| 1 \| 1 \| 1 \| | 1 | ratio | ks | test | eq | `[[art:a13846c8:metrics.test.ks]]` | verified | 1 |
| 207 | outcomes | \| KS \| 1 \| 1 \| 1 \| 1 \| | 1 | ratio | ks | out_of_time | eq | `[[art:e3aa3687:metrics.out_of_time.ks]]` | verified | 1 |
| 208 | outcomes | \| KS \| 1 \| 1 \| 1 \| 1 \| | 1 | ratio | ks | vintage_holdout | eq | `[[art:cb4509f6:metrics.vintage_holdout.ks]]` | verified | 1 |
| 209 | outcomes | \| Brier \| 1.096e-08 \| 1.011e-08 \| 1.376e-08 \| 8.646e-09 \| | 1.096e-08 | ratio | brier | train | eq | `[[art:0c2c4489:metrics.train.brier]]` | verified | 1.095784085e-08 |
| 210 | outcomes | \| Brier \| 1.096e-08 \| 1.011e-08 \| 1.376e-08 \| 8.646e-09 \| | 1.011e-08 | ratio | brier | test | eq | `[[art:67fd4fea:metrics.test.brier]]` | verified | 1.01061577e-08 |
| 211 | outcomes | \| Brier \| 1.096e-08 \| 1.011e-08 \| 1.376e-08 \| 8.646e-09 \| | 1.376e-08 | ratio | brier | out_of_time | eq | `[[art:44f11124:metrics.out_of_time.brier]]` | verified | 1.375799568e-08 |
| 212 | outcomes | \| Brier \| 1.096e-08 \| 1.011e-08 \| 1.376e-08 \| 8.646e-09 \| | 8.646e-09 | ratio | brier | vintage_holdout | eq | `[[art:c58e369c:metrics.vintage_holdout.brier]]` | verified | 8.645548253e-09 |
| 213 | outcomes | \| Log loss \| 9.128e-05 \| 9.043e-05 \| 9.057e-05 \| 8.629e-05 \| | 9.128e-05 | ratio | logloss | train | eq | `[[art:1761d10c:metrics.train.logloss]]` | verified | 9.128014231e-05 |
| 214 | outcomes | \| Log loss \| 9.128e-05 \| 9.043e-05 \| 9.057e-05 \| 8.629e-05 \| | 9.043e-05 | ratio | logloss | test | eq | `[[art:db4e6b76:metrics.test.logloss]]` | verified | 9.04295748e-05 |
| 215 | outcomes | \| Log loss \| 9.128e-05 \| 9.043e-05 \| 9.057e-05 \| 8.629e-05 \| | 9.057e-05 | ratio | logloss | out_of_time | eq | `[[art:4ff30655:metrics.out_of_time.logloss]]` | verified | 9.056637435e-05 |
| 216 | outcomes | \| Log loss \| 9.128e-05 \| 9.043e-05 \| 9.057e-05 \| 8.629e-05 \| | 8.629e-05 | ratio | logloss | vintage_holdout | eq | `[[art:85bdc089:metrics.vintage_holdout.logloss]]` | verified | 8.629383814e-05 |
| 217 | outcomes | \| Rows scored \| 36013 \| 15382 \| 12257 \| 32177 \| | 36013 | count | n | train | eq | `[[art:6fdfeabb:metrics.train.n]]` | verified | 36013 |
| 218 | outcomes | \| Rows scored \| 36013 \| 15382 \| 12257 \| 32177 \| | 15382 | count | n | test | eq | `[[art:e55953e1:metrics.test.n]]` | verified | 15382 |
| 219 | outcomes | \| Rows scored \| 36013 \| 15382 \| 12257 \| 32177 \| | 12257 | count | n | out_of_time | eq | `[[art:7898809e:metrics.out_of_time.n]]` | verified | 12257 |
| 220 | outcomes | \| Rows scored \| 36013 \| 15382 \| 12257 \| 32177 \| | 32177 | count | n | vintage_holdout | eq | `[[art:37a92951:metrics.vintage_holdout.n]]` | verified | 32177 |
| 221 | outcomes | The share of events falling in the top two deciles of predic… | 1 | ratio | top2_capture | train | eq | `[[art:194d1fbd:deciles.train.top2_capture]]` | verified | 1 |
| 222 | outcomes | The share of events falling in the top two deciles of predic… | 1 | ratio | top2_capture | test | eq | `[[art:466bfdc8:deciles.test.top2_capture]]` | verified | 1 |
| 223 | outcomes | The share of events falling in the top two deciles of predic… | 1 | ratio | top2_capture | out_of_time | eq | `[[art:d3114d7a:deciles.out_of_time.top2_capture]]` | verified | 1 |
| 224 | outcomes | The share of events falling in the top two deciles of predic… | 1 | ratio | top2_capture | vintage_holdout | eq | `[[art:db275674:deciles.vintage_holdout.top2_capture]]` | verified | 1 |
| 225 | outcomes | AUC on train is 1 and AUC on test is 1 , neither above the o… | 1 | ratio | auc | train | eq | `[[art:6269694d:metrics.train.auc]]` | verified | 1 |
| 226 | outcomes | AUC on train is 1 and AUC on test is 1 , neither above the o… | 1 | ratio | auc | test | eq | `[[art:4619bd69:metrics.test.auc]]` | verified | 1 |
| 227 | outcomes | AUC on train is 1 and AUC on test is 1 , neither above the o… | 0.08 | ratio | auc_gap |  | eq | `[[art:630f28f4:threshold.O1.auc_gap]]` | verified | 0.08 |
| 228 | outcomes | AUC out of time is 1 and on the vintage holdout 1 , neither… | 1 | ratio | auc | out_of_time | eq | `[[art:bcb747a3:metrics.out_of_time.auc]]` | verified | 1 |
| 229 | outcomes | AUC out of time is 1 and on the vintage holdout 1 , neither… | 1 | ratio | auc | vintage_holdout | eq | `[[art:00749c11:metrics.vintage_holdout.auc]]` | verified | 1 |
| 230 | outcomes | AUC out of time is 1 and on the vintage holdout 1 , neither… | 0.05 | ratio | holdout_gap |  | eq | `[[art:90f8b6d9:threshold.O1.holdout_gap]]` | verified | 0.05 |
| 231 | outcomes | The table pairs each declared bound with the value recompute… | 0.65 | ratio | auc | test | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 232 | outcomes | The table pairs each declared bound with the value recompute… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 233 | outcomes | The table pairs each declared bound with the value recompute… | 0.06189 | ratio | psi |  | eq | `[[art:c2e8c8fd:psi.max]]` | verified | 0.06188985797 |
| 234 | outcomes | On train the slice holds 0.5 of the split, above the floor o… | 0.5 | ratio | share | train | eq | `[[art:cf8da663:metrics.train.sub.bom_balance_log_low.share]]` | verified | 0.5000138839 |
| 235 | outcomes | On train the slice holds 0.5 of the split, above the floor o… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 236 | outcomes | On train the slice holds 0.5 of the split, above the floor o… | 0.95 | ratio | slice_max_share |  | eq | `[[art:a928a05c:threshold.O1.slice_max_share]]` | verified | 0.95 |
| 237 | outcomes | On train the slice holds 0.5 of the split, above the floor o… | 0 | ratio | auc_gap | train | eq | `[[art:d6a2abd9:metrics.train.sub.bom_balance_log_low.auc_gap]]` | verified | 0 |
| 238 | outcomes | On train the slice holds 0.5 of the split, above the floor o… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 239 | outcomes | Mean predicted on that slice is 0.01713 against an observed… | 0.01713 | ratio | mean_predicted | train | eq | `[[art:a2ea08bd:metrics.train.sub.bom_balance_log_low.mean_predicted]]` | verified | 0.01713496515 |
| 240 | outcomes | Mean predicted on that slice is 0.01713 against an observed… | 0.01705 | ratio | event_rate | train | eq | `[[art:ad34a08d:metrics.train.sub.bom_balance_log_low.event_rate]]` | verified | 0.01704892542 |
| 241 | outcomes | Mean predicted on that slice is 0.01713 against an observed… | 0.005047 | ratio | mean_rel_gap | train | eq | `[[art:b68c896e:metrics.train.sub.bom_balance_log_low.mean_rel_gap]]` | verified | 0.005046636528 |
| 242 | outcomes | On test the slice holds 0.5 of the split, above that same fl… | 0.5 | ratio | share | test | eq | `[[art:92640866:metrics.test.sub.bom_balance_log_low.share]]` | verified | 0.5 |
| 243 | outcomes | On test the slice holds 0.5 of the split, above that same fl… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 244 | outcomes | On test the slice holds 0.5 of the split, above that same fl… | 0.95 | ratio | slice_max_share |  | eq | `[[art:a928a05c:threshold.O1.slice_max_share]]` | verified | 0.95 |
| 245 | outcomes | On test the slice holds 0.5 of the split, above that same fl… | 0 | ratio | auc_gap | test | eq | `[[art:15d6b42a:metrics.test.sub.bom_balance_log_low.auc_gap]]` | verified | 0 |
| 246 | outcomes | On test the slice holds 0.5 of the split, above that same fl… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 247 | outcomes | Mean predicted on that slice is 0.01621 against an observed… | 0.01621 | ratio | mean_predicted | test | eq | `[[art:ea1d611d:metrics.test.sub.bom_balance_log_low.mean_predicted]]` | verified | 0.01621003759 |
| 248 | outcomes | Mean predicted on that slice is 0.01621 against an observed… | 0.01612 | ratio | event_rate | test | eq | `[[art:857f20f7:metrics.test.sub.bom_balance_log_low.event_rate]]` | verified | 0.01612274087 |
| 249 | outcomes | Mean predicted on that slice is 0.01621 against an observed… | 0.005415 | ratio | mean_rel_gap | test | eq | `[[art:51020e4b:metrics.test.sub.bom_balance_log_low.mean_rel_gap]]` | verified | 0.005414509197 |
| 250 | outcomes | Out of time the slice holds 0.5 of the split, above the floo… | 0.5 | ratio | share | out_of_time | eq | `[[art:3b641caa:metrics.out_of_time.sub.bom_balance_log_low.share]]` | verified | 0.500040793 |
| 251 | outcomes | Out of time the slice holds 0.5 of the split, above the floo… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 252 | outcomes | Out of time the slice holds 0.5 of the split, above the floo… | 0.95 | ratio | slice_max_share |  | eq | `[[art:a928a05c:threshold.O1.slice_max_share]]` | verified | 0.95 |
| 253 | outcomes | Out of time the slice holds 0.5 of the split, above the floo… | 0 | ratio | auc_gap | out_of_time | eq | `[[art:63da67de:metrics.out_of_time.sub.bom_balance_log_low.auc_gap]]` | verified | 0 |
| 254 | outcomes | Out of time the slice holds 0.5 of the split, above the floo… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 255 | outcomes | Mean predicted on that slice is 0.03596 against an observed… | 0.03596 | ratio | mean_predicted | out_of_time | eq | `[[art:762160e6:metrics.out_of_time.sub.bom_balance_log_low.mean_predicted]]` | verified | 0.03596101298 |
| 256 | outcomes | Mean predicted on that slice is 0.03596 against an observed… | 0.03589 | ratio | event_rate | out_of_time | eq | `[[art:da848331:metrics.out_of_time.sub.bom_balance_log_low.event_rate]]` | verified | 0.03589492576 |
| 257 | outcomes | Mean predicted on that slice is 0.03596 against an observed… | 0.001841 | ratio | mean_rel_gap | out_of_time | eq | `[[art:249e8321:metrics.out_of_time.sub.bom_balance_log_low.mean_rel_gap]]` | verified | 0.001841129916 |
| 258 | outcomes | On the vintage holdout the slice holds 0.5 of the split, abo… | 0.5 | ratio | share | vintage_holdout | eq | `[[art:80d79940:metrics.vintage_holdout.sub.bom_balance_log_low.share]]` | verified | 0.500015539 |
| 259 | outcomes | On the vintage holdout the slice holds 0.5 of the split, abo… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 260 | outcomes | On the vintage holdout the slice holds 0.5 of the split, abo… | 0.95 | ratio | slice_max_share |  | eq | `[[art:a928a05c:threshold.O1.slice_max_share]]` | verified | 0.95 |
| 261 | outcomes | On the vintage holdout the slice holds 0.5 of the split, abo… | 0 | ratio | auc_gap | vintage_holdout | eq | `[[art:6b406bf5:metrics.vintage_holdout.sub.bom_balance_log_low.auc_gap]]` | verified | 0 |
| 262 | outcomes | On the vintage holdout the slice holds 0.5 of the split, abo… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 263 | outcomes | Mean predicted on that slice is 0.009721 against an observed… | 0.009721 | ratio | mean_predicted | vintage_holdout | eq | `[[art:aa56f401:metrics.vintage_holdout.sub.bom_balance_log_low.mean_predicted]]` | verified | 0.009721345496 |
| 264 | outcomes | Mean predicted on that slice is 0.009721 against an observed… | 0.009634 | ratio | event_rate | vintage_holdout | eq | `[[art:81942b57:metrics.vintage_holdout.sub.bom_balance_log_low.event_rate]]` | verified | 0.009633911368 |
| 265 | outcomes | Mean predicted on that slice is 0.009721 against an observed… | 0.009076 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:c6339ca6:metrics.vintage_holdout.sub.bom_balance_log_low.mean_rel_gap]]` | verified | 0.00907566245 |
| 266 | outcomes | Comparing those four slice gaps against one another as diffe… | 0.009076 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:c6339ca6:metrics.vintage_holdout.sub.bom_balance_log_low.mean_rel_gap]]` | verified | 0.00907566245 |
| 267 | outcomes | Comparing those four slice gaps against one another as diffe… | 0.001841 | ratio | mean_rel_gap | out_of_time | eq | `[[art:249e8321:metrics.out_of_time.sub.bom_balance_log_low.mean_rel_gap]]` | verified | 0.001841129916 |
| 268 | sensitivity | The largest variance inflation factor among the retained fea… | 4.978 | ratio | vif |  | eq | `[[art:b1d416c0:vif.max]]` | verified | 4.977599595 |
| 269 | sensitivity | The largest variance inflation factor among the retained fea… | 10 | ratio | vif |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 270 | sensitivity | The next largest values are on burnout at 3.44 and loan age… | 3.44 | ratio | vif |  | eq | `[[art:91e7ce55:vif.burnout]]` | verified | 3.439982425 |
| 271 | sensitivity | The next largest values are on burnout at 3.44 and loan age… | 2.93 | ratio | vif |  | eq | `[[art:43980218:vif.loan_age]]` | verified | 2.930049511 |
| 272 | sensitivity | The incentive term stands at 2.234 and the spread-at-origina… | 2.234 | ratio | vif |  | eq | `[[art:d924a341:vif.incentive]]` | verified | 2.234058893 |
| 273 | sensitivity | The incentive term stands at 2.234 and the spread-at-origina… | 1.713 | ratio | vif |  | eq | `[[art:08e0ca20:vif.sato]]` | verified | 1.712581428 |
| 274 | sensitivity | The remaining features sit close to unity: the logged beginn… | 1.143 | ratio | vif |  | eq | `[[art:0b30efbf:vif.bom_balance_log]]` | verified | 1.142939813 |
| 275 | sensitivity | The remaining features sit close to unity: the logged beginn… | 1.134 | ratio | vif |  | eq | `[[art:347761f6:vif.orig_upb_log]]` | verified | 1.134478986 |
| 276 | sensitivity | The remaining features sit close to unity: the logged beginn… | 1.018 | ratio | vif |  | eq | `[[art:a2dc57c7:vif.season_cos]]` | verified | 1.01775523 |
| 277 | sensitivity | The remaining features sit close to unity: the logged beginn… | 1.009 | ratio | vif |  | eq | `[[art:b8652149:vif.credit_score]]` | verified | 1.009199828 |
| 278 | sensitivity | The remaining features sit close to unity: the logged beginn… | 1.005 | ratio | vif |  | eq | `[[art:10f2f018:vif.orig_ltv]]` | verified | 1.004907818 |
| 279 | sensitivity | The remaining features sit close to unity: the logged beginn… | 1.004 | ratio | vif |  | eq | `[[art:5069e43c:vif.season_sin]]` | verified | 1.004179036 |
| 280 | sensitivity | Belsley's condition number of the column-standardised design… | 4.954 | ratio | condition_number |  | eq | `[[art:d0edbe6f:condition_number]]` | verified | 4.953837779 |
| 281 | sensitivity | Belsley's condition number of the column-standardised design… | 30 | ratio | condition_number |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 282 | sensitivity | The bound these per-regime values are read against is an acr… | 0.1 | ratio | auc_gap |  | eq | `[[art:b64213d7:threshold.R1.auc_gap]]` | verified | 0.1 |
| 283 | sensitivity | A coefficient sign flip is counted only where the coefficien… | 0.05 | ratio | sign_flip_coef |  | eq | `[[art:aca84377:threshold.R1.sign_flip_coef]]` | verified | 0.05 |
| 284 | sensitivity | A coefficient sign flip is counted only where the coefficien… | 2 | ratio | sign_flip_z |  | eq | `[[art:2e4428c7:threshold.R1.sign_flip_z]]` | verified | 2 |
| 285 | sensitivity | On that joint test the flip indicator is 0 for the note rate… | 0 | ratio | sign_flip |  | eq | `[[art:e7ce4912:stability.note_rate.sign_flip]]` | verified | 0 |
| 286 | sensitivity | On that joint test the flip indicator is 0 for the note rate… | 0 | ratio | sign_flip |  | eq | `[[art:0cc7a37d:stability.incentive.sign_flip]]` | verified | 0 |
| 287 | sensitivity | On that joint test the flip indicator is 0 for the note rate… | 0 | ratio | sign_flip |  | eq | `[[art:6bc05e82:stability.burnout.sign_flip]]` | verified | 0 |
| 288 | sensitivity | On that joint test the flip indicator is 0 for the note rate… | 0 | ratio | sign_flip |  | eq | `[[art:b7191217:stability.loan_age.sign_flip]]` | verified | 0 |
| 289 | sensitivity | On that joint test the flip indicator is 0 for the note rate… | 0 | ratio | sign_flip |  | eq | `[[art:1f302ccd:stability.sato.sign_flip]]` | verified | 0 |
| 290 | sensitivity | It is likewise 0 for credit score , 0 for original LTV , 0 f… | 0 | ratio | sign_flip |  | eq | `[[art:d956c276:stability.credit_score.sign_flip]]` | verified | 0 |
| 291 | sensitivity | It is likewise 0 for credit score , 0 for original LTV , 0 f… | 0 | ratio | sign_flip |  | eq | `[[art:054d5fab:stability.orig_ltv.sign_flip]]` | verified | 0 |
| 292 | sensitivity | It is likewise 0 for credit score , 0 for original LTV , 0 f… | 0 | ratio | sign_flip |  | eq | `[[art:fb1ae6c8:stability.orig_upb_log.sign_flip]]` | verified | 0 |
| 293 | sensitivity | It is likewise 0 for credit score , 0 for original LTV , 0 f… | 0 | ratio | sign_flip |  | eq | `[[art:a9b4364d:stability.bom_balance_log.sign_flip]]` | verified | 0 |
| 294 | sensitivity | It is likewise 0 for credit score , 0 for original LTV , 0 f… | 0 | ratio | sign_flip |  | eq | `[[art:6ba36a3b:stability.season_sin.sign_flip]]` | verified | 0 |
| 295 | sensitivity | It is likewise 0 for credit score , 0 for original LTV , 0 f… | 0 | ratio | sign_flip |  | eq | `[[art:1850e2de:stability.season_cos.sign_flip]]` | verified | 0 |
| 296 | sensitivity | Going from the deepest downward shock to the largest upward… | -92.11 | currency | value_change |  | eq | `[[art:0f83fead:scenario.value_change.-300]]` | verified | -92.10987115 |
| 297 | sensitivity | Going from the deepest downward shock to the largest upward… | -83.78 | currency | value_change |  | eq | `[[art:75d82514:scenario.value_change.-200]]` | verified | -83.77616324 |
| 298 | sensitivity | Going from the deepest downward shock to the largest upward… | -57.15 | currency | value_change |  | eq | `[[art:0445ffec:scenario.value_change.-100]]` | verified | -57.14884469 |
| 299 | sensitivity | Going from the deepest downward shock to the largest upward… | 0 | currency | value_change |  | eq | `[[art:1e1b0b88:scenario.value_change.0]]` | verified | 0 |
| 300 | sensitivity | Going from the deepest downward shock to the largest upward… | 77.18 | currency | value_change |  | eq | `[[art:d16cc2a1:scenario.value_change.100]]` | verified | 77.1836951 |
| 301 | sensitivity | Going from the deepest downward shock to the largest upward… | 155.8 | currency | value_change |  | eq | `[[art:4871ddee:scenario.value_change.200]]` | verified | 155.7824864 |
| 302 | sensitivity | Going from the deepest downward shock to the largest upward… | 232.8 | currency | value_change |  | eq | `[[art:a0678af4:scenario.value_change.300]]` | verified | 232.8287879 |
| 303 | sensitivity | The realised convexity, defined as the change at the deepest… | 140.7 | currency | convexity |  | eq | `[[art:4451c907:scenario.convexity]]` | verified | 140.7189167 |
| 304 | findings | The strongest single feature, `bom_balance_log`, reaches an… | 1 | ratio | auc | train | eq | `[[art:7f74c0d5:leakage.target_corr.max_single_feature_auc]]` | verified | 1 |
| 305 | findings | The strongest single feature, `bom_balance_log`, reaches an… | 0.9 | ratio | auc |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 306 | findings | The number of features whose declared timing places them dur… | 0 | count | n_flagged |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 307 | findings | The change in servicing value at the deepest downward rate s… | -92.11 | ratio | value_change |  | eq | `[[art:0f83fead:scenario.value_change.-300]]` | verified | -92.10987115 |
| 308 | findings | The change in servicing value at the deepest downward rate s… | 232.8 | ratio | value_change |  | eq | `[[art:a0678af4:scenario.value_change.300]]` | verified | 232.8287879 |
| 309 | findings | The realised convexity taken from those two changes is 140.7… | 140.7 | ratio | convexity |  | eq | `[[art:4451c907:scenario.convexity]]` | verified | 140.7189167 |
| 310 | findings | The subject's own projection record carries the same positiv… | 140.7 | ratio | convexity |  | eq | `[[art:7d3ba32d:run.projection#convexity]]` | verified | 140.7189167 |
| 311 | findings | First-year CPR does move in the expected direction across th… | 0.0007734 | ratio | cpr_by_shock |  | eq | `[[art:7d3ba32d:run.projection#cpr_by_shock.-300]]` | verified | 0.0007733749519 |
| 312 | findings | First-year CPR does move in the expected direction across th… | 0.0006902 | ratio | cpr_by_shock |  | eq | `[[art:7d3ba32d:run.projection#cpr_by_shock.300]]` | verified | 0.0006901743211 |
| 313 | findings | Model developer — what does the model discriminate on, with… | -1 | ratio | coef_sign |  | eq | `[[art:dcfb2de4:sign_check.burnout.coef_sign]]` | verified | -1 |
| 314 | findings | Model developer — what does the model discriminate on, with… | 1 | ratio | univariate_direction | train | eq | `[[art:bfc96bb2:sign_check.burnout.univariate_direction]]` | verified | 1 |
| 315 | findings | Model developer — what does the model discriminate on, with… | 0 | ratio | agrees |  | eq | `[[art:56826e40:sign_check.burnout.agrees]]` | verified | 0 |
| 316 | findings | Model developer — what does the model discriminate on, with… | -1 | ratio | coef_sign |  | eq | `[[art:92ed5b5f:sign_check.season_sin.coef_sign]]` | verified | -1 |
| 317 | findings | Model developer — what does the model discriminate on, with… | 1 | ratio | univariate_direction | train | eq | `[[art:cae6b096:sign_check.season_sin.univariate_direction]]` | verified | 1 |
| 318 | findings | Model developer — what does the model discriminate on, with… | 0 | ratio | agrees |  | eq | `[[art:74f2d0e0:sign_check.season_sin.agrees]]` | verified | 0 |
| 319 | monitoring | Discrimination on realized prepayment outcomes should be rec… | 0.65 | ratio | auc | test | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 320 | monitoring | On the held-out test sample this validation recomputed discr… | 1 | ratio | auc | test | eq | `[[art:4619bd69:metrics.test.auc]]` | verified | 1 |
| 321 | monitoring | Monitoring should therefore report the production value besi… | 1 | ratio | auc | test | eq | `[[art:4619bd69:metrics.test.auc]]` | verified | 1 |
| 322 | monitoring | Monitoring should therefore report the production value besi… | 0.65 | ratio | auc | test | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 323 | monitoring | The largest train-to-test population shift observed in this… | 0.06189 | ratio | psi |  | eq | `[[art:c2e8c8fd:psi.max]]` | verified | 0.06188985797 |
| 324 | monitoring | The largest train-to-test population shift observed in this… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 325 | monitoring | The production series should be compared against that same c… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 326 | monitoring | The production series should be compared against that same c… | 0.06189 | ratio | psi |  | eq | `[[art:c2e8c8fd:psi.max]]` | verified | 0.06188985797 |

## Appendix B — Artifact index

The store holds 328 artifacts; the 247 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `ablation.baseline_auc` | `7610ff35` | scalar | 1 | AUC on test of a refit of the champion's functional form on every retained feature, the level each ablation delta is measured from |
| `ablation.bom_balance_log.delta_auc` | `c226f60f` | scalar | -0.2327007725 | change in test AUC when the champion's form is refitted without bom_balance_log |
| `ablation.burnout.delta_auc` | `d50de877` | scalar | 0 | change in test AUC when the champion's form is refitted without burnout |
| `ablation.credit_score.delta_auc` | `d1dff006` | scalar | 0 | change in test AUC when the champion's form is refitted without credit_score |
| `ablation.incentive.delta_auc` | `33a25e3c` | scalar | 0 | change in test AUC when the champion's form is refitted without incentive |
| `ablation.loan_age.delta_auc` | `1a789b08` | scalar | 0 | change in test AUC when the champion's form is refitted without loan_age |
| `ablation.note_rate.delta_auc` | `65b3f07a` | scalar | 0 | change in test AUC when the champion's form is refitted without note_rate |
| `ablation.orig_ltv.delta_auc` | `370eaea8` | scalar | 0 | change in test AUC when the champion's form is refitted without orig_ltv |
| `ablation.orig_upb_log.delta_auc` | `e245ef14` | scalar | 0 | change in test AUC when the champion's form is refitted without orig_upb_log |
| `ablation.sato.delta_auc` | `2bbb0015` | scalar | 0 | change in test AUC when the champion's form is refitted without sato |
| `ablation.season_cos.delta_auc` | `9453331c` | scalar | 0 | change in test AUC when the champion's form is refitted without season_cos |
| `ablation.season_sin.delta_auc` | `a4f7b0c1` | scalar | 0 | change in test AUC when the champion's form is refitted without season_sin |
| `calibration.mean_rel_gap.out_of_time` | `68619260` | scalar | 0.003912925468 | mean predicted against observed on out_of_time, relative |
| `calibration.mean_rel_gap.test` | `4e1854b1` | scalar | 0.01025910486 | mean predicted against observed on test, relative |
| `calibration.mean_rel_gap.train` | `db1bca38` | scalar | 0.009653750145 | mean predicted against observed on train, relative |
| `calibration.mean_rel_gap.vintage_holdout` | `1438e44d` | scalar | 0.01696028022 | mean predicted against observed on vintage_holdout, relative |
| `calibration.separable.out_of_time` | `258b7972` | scalar | 1 | the predictions on out_of_time separate the outcome, so the calibration slope has no finite maximum likelihood estimate and was not computed |
| `calibration.separable.test` | `81c3fa7a` | scalar | 1 | the predictions on test separate the outcome, so the calibration slope has no finite maximum likelihood estimate and was not computed |
| `calibration.separable.train` | `d7ee2241` | scalar | 1 | the predictions on train separate the outcome, so the calibration slope has no finite maximum likelihood estimate and was not computed |
| `calibration.separable.vintage_holdout` | `137e2c39` | scalar | 1 | the predictions on vintage_holdout separate the outcome, so the calibration slope has no finite maximum likelihood estimate and was not computed |
| `calibration.test` | `a3f4f35f` | table | table, 10 rows | calibration by decile of predicted probability on test |
| `challenger.auc` | `5aeaf534` | scalar | 1 | the challenger's AUC on test |
| `challenger.brier` | `0b5236ca` | scalar | 3.226460021e-13 | the challenger's Brier score on test |
| `challenger.delta_auc` | `d8eca8f5` | scalar | 0 | the challenger's AUC on test minus the champion's |
| `condition_number` | `d0edbe6f` | scalar | 4.953837779 | Belsley's condition number of the column-standardised design |
| `cpr.out_of_time.mae` | `bdc9d54f` | scalar | 0.0007117577187 | mean absolute difference between actual and predicted CPR on out_of_time |
| `cpr.test` | `0aa376c9` | table | table, 71 rows | actual against predicted CPR by period on test |
| `cpr.test.mae` | `be219b85` | scalar | 0.0009292114418 | mean absolute difference between actual and predicted CPR on test |
| `cpr.train.mae` | `99b2b87f` | scalar | 0.0009279500644 | mean absolute difference between actual and predicted CPR on train |
| `cpr.vintage_holdout.mae` | `d1a19e91` | scalar | 0.0009298655279 | mean absolute difference between actual and predicted CPR on vintage_holdout |
| `csi.bom_balance_log` | `60a10892` | scalar | 0.03214820108 | CSI of bom_balance_log: its contribution to the shift in the linear predictor |
| `csi.burnout` | `a5da1daa` | scalar | 0.0001015529196 | CSI of burnout: its contribution to the shift in the linear predictor |
| `csi.credit_score` | `d87a2d40` | scalar | 0.000223048204 | CSI of credit_score: its contribution to the shift in the linear predictor |
| `csi.incentive` | `41325258` | scalar | 9.278494663e-05 | CSI of incentive: its contribution to the shift in the linear predictor |
| `csi.loan_age` | `df52c920` | scalar | 0 | CSI of loan_age: its contribution to the shift in the linear predictor |
| `csi.max` | `b2440ca1` | scalar | 0.03214820108 | the largest characteristic stability index |
| `csi.note_rate` | `587b33e9` | scalar | 0.0003806385501 | CSI of note_rate: its contribution to the shift in the linear predictor |
| `csi.orig_ltv` | `7ea837e1` | scalar | 0.0008996218814 | CSI of orig_ltv: its contribution to the shift in the linear predictor |
| `csi.orig_upb_log` | `5d1c16f2` | scalar | 0.004635722963 | CSI of orig_upb_log: its contribution to the shift in the linear predictor |
| `csi.sato` | `fb71eb9e` | scalar | 0.0004490205147 | CSI of sato: its contribution to the shift in the linear predictor |
| `csi.season_cos` | `de66f2c6` | scalar | 1.934566399e-05 | CSI of season_cos: its contribution to the shift in the linear predictor |
| `csi.season_sin` | `4c3f0dd9` | scalar | 1.386212619e-06 | CSI of season_sin: its contribution to the shift in the linear predictor |
| `deciles.out_of_time.top2_capture` | `d3114d7a` | scalar | 1 | share of out_of_time events in the top two deciles |
| `deciles.test` | `a859c712` | table | table, 10 rows | decile separation on test; decile 1 holds the highest probabilities |
| `deciles.test.top2_capture` | `466bfdc8` | scalar | 1 | share of test events in the top two deciles |
| `deciles.train.top2_capture` | `194d1fbd` | scalar | 1 | share of train events in the top two deciles |
| `deciles.vintage_holdout.top2_capture` | `db275674` | scalar | 1 | share of vintage_holdout events in the top two deciles |
| `leakage.duplicates.train` | `4474c227` | scalar | 0 | share of train rows whose feature values are not unique within train |
| `leakage.name_screen.n_matched` | `407e62be` | scalar | 0 | feature names matching the target-adjacent lexicon |
| `leakage.overlap` | `4c9fcd09` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.features` | `0fec8048` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.ids` | `63d37fc5` | scalar | 0 | share of test rows whose ['loan_id', 'period'] also identify a row of train |
| `leakage.target_corr` | `ce82a409` | table | table, 11 rows | each feature against the outcome on train, on its own |
| `leakage.target_corr.max_single_feature_auc` | `7f74c0d5` | scalar | 1 | the AUC of the strongest single feature |
| `leakage.timing` | `8cdad1c5` | table | table, 12 rows | each feature's declared timing; flagged means during or after the outcome |
| `leakage.timing.n_flagged` | `742bcd24` | scalar | 0 | features declared during_period or after_outcome |
| `metrics.out_of_time.auc` | `bcb747a3` | scalar | 1 | auc on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.brier` | `44f11124` | scalar | 1.375799568e-08 | brier on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.event_rate` | `83ccf5c0` | scalar | 0.01794892714 | event_rate on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.gini` | `6d939d01` | scalar | 1 | gini on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.ks` | `e3aa3687` | scalar | 1 | ks on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.logloss` | `4ff30655` | scalar | 9.056637435e-05 | logloss on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.mean_predicted` | `276f106a` | scalar | 0.01801915996 | mean_predicted on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.n` | `7898809e` | scalar | 12257 | n on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.sub.bom_balance_log_low` | `8342d448` | table | table, 10 rows | every metric on the bom_balance_log below_median slice of out_of_time |
| `metrics.out_of_time.sub.bom_balance_log_low.auc_gap` | `63da67de` | scalar | 0 | how far AUC on the bom_balance_log below_median slice of out_of_time falls below AUC on all of out_of_time |
| `metrics.out_of_time.sub.bom_balance_log_low.event_rate` | `da848331` | scalar | 0.03589492576 | event_rate on the bom_balance_log below_median slice of out_of_time |
| `metrics.out_of_time.sub.bom_balance_log_low.mean_predicted` | `762160e6` | scalar | 0.03596101298 | mean_predicted on the bom_balance_log below_median slice of out_of_time |
| `metrics.out_of_time.sub.bom_balance_log_low.mean_rel_gap` | `249e8321` | scalar | 0.001841129916 | mean predicted against observed on the bom_balance_log below_median slice of out_of_time, relative |
| `metrics.out_of_time.sub.bom_balance_log_low.share` | `3b641caa` | scalar | 0.500040793 | the share of out_of_time the bom_balance_log below_median slice holds |
| `metrics.test.auc` | `4619bd69` | scalar | 1 | auc on test, recomputed by quaestor |
| `metrics.test.brier` | `67fd4fea` | scalar | 1.01061577e-08 | brier on test, recomputed by quaestor |
| `metrics.test.event_rate` | `570cc08a` | scalar | 0.008061370433 | event_rate on test, recomputed by quaestor |
| `metrics.test.gini` | `35acd744` | scalar | 1 | gini on test, recomputed by quaestor |
| `metrics.test.ks` | `a13846c8` | scalar | 1 | ks on test, recomputed by quaestor |
| `metrics.test.logloss` | `db4e6b76` | scalar | 9.04295748e-05 | logloss on test, recomputed by quaestor |
| `metrics.test.mean_predicted` | `83863be2` | scalar | 0.008144072878 | mean_predicted on test, recomputed by quaestor |
| `metrics.test.n` | `e55953e1` | scalar | 15382 | n on test, recomputed by quaestor |
| `metrics.test.sub.bom_balance_log_low` | `3333d0d1` | table | table, 10 rows | every metric on the bom_balance_log below_median slice of test |
| `metrics.test.sub.bom_balance_log_low.auc_gap` | `15d6b42a` | scalar | 0 | how far AUC on the bom_balance_log below_median slice of test falls below AUC on all of test |
| `metrics.test.sub.bom_balance_log_low.event_rate` | `857f20f7` | scalar | 0.01612274087 | event_rate on the bom_balance_log below_median slice of test |
| `metrics.test.sub.bom_balance_log_low.mean_predicted` | `ea1d611d` | scalar | 0.01621003759 | mean_predicted on the bom_balance_log below_median slice of test |
| `metrics.test.sub.bom_balance_log_low.mean_rel_gap` | `51020e4b` | scalar | 0.005414509197 | mean predicted against observed on the bom_balance_log below_median slice of test, relative |
| `metrics.test.sub.bom_balance_log_low.share` | `92640866` | scalar | 0.5 | the share of test the bom_balance_log below_median slice holds |
| `metrics.train.auc` | `6269694d` | scalar | 1 | auc on train, recomputed by quaestor |
| `metrics.train.brier` | `0c2c4489` | scalar | 1.095784085e-08 | brier on train, recomputed by quaestor |
| `metrics.train.event_rate` | `b9ef3327` | scalar | 0.008524699414 | event_rate on train, recomputed by quaestor |
| `metrics.train.gini` | `e2084e07` | scalar | 1 | gini on train, recomputed by quaestor |
| `metrics.train.ks` | `24c2277d` | scalar | 1 | ks on train, recomputed by quaestor |
| `metrics.train.logloss` | `1761d10c` | scalar | 9.128014231e-05 | logloss on train, recomputed by quaestor |
| `metrics.train.mean_predicted` | `6f9330ed` | scalar | 0.008606994732 | mean_predicted on train, recomputed by quaestor |
| `metrics.train.n` | `6fdfeabb` | scalar | 36013 | n on train, recomputed by quaestor |
| `metrics.train.sub.bom_balance_log_low` | `179b230e` | table | table, 10 rows | every metric on the bom_balance_log below_median slice of train |
| `metrics.train.sub.bom_balance_log_low.auc_gap` | `d6a2abd9` | scalar | 0 | how far AUC on the bom_balance_log below_median slice of train falls below AUC on all of train |
| `metrics.train.sub.bom_balance_log_low.event_rate` | `ad34a08d` | scalar | 0.01704892542 | event_rate on the bom_balance_log below_median slice of train |
| `metrics.train.sub.bom_balance_log_low.mean_predicted` | `a2ea08bd` | scalar | 0.01713496515 | mean_predicted on the bom_balance_log below_median slice of train |
| `metrics.train.sub.bom_balance_log_low.mean_rel_gap` | `b68c896e` | scalar | 0.005046636528 | mean predicted against observed on the bom_balance_log below_median slice of train, relative |
| `metrics.train.sub.bom_balance_log_low.share` | `cf8da663` | scalar | 0.5000138839 | the share of train the bom_balance_log below_median slice holds |
| `metrics.vintage_holdout.auc` | `00749c11` | scalar | 1 | auc on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.brier` | `c58e369c` | scalar | 8.645548253e-09 | brier on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.event_rate` | `e3590a16` | scalar | 0.004817105386 | event_rate on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.gini` | `f4aa377a` | scalar | 1 | gini on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.ks` | `cb4509f6` | scalar | 1 | ks on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.logloss` | `85bdc089` | scalar | 8.629383814e-05 | logloss on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.mean_predicted` | `af925790` | scalar | 0.004898804843 | mean_predicted on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.n` | `37a92951` | scalar | 32177 | n on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.sub.bom_balance_log_low` | `547f8789` | table | table, 10 rows | every metric on the bom_balance_log below_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.bom_balance_log_low.auc_gap` | `6b406bf5` | scalar | 0 | how far AUC on the bom_balance_log below_median slice of vintage_holdout falls below AUC on all of vintage_holdout |
| `metrics.vintage_holdout.sub.bom_balance_log_low.event_rate` | `81942b57` | scalar | 0.009633911368 | event_rate on the bom_balance_log below_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.bom_balance_log_low.mean_predicted` | `aa56f401` | scalar | 0.009721345496 | mean_predicted on the bom_balance_log below_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.bom_balance_log_low.mean_rel_gap` | `c6339ca6` | scalar | 0.00907566245 | mean predicted against observed on the bom_balance_log below_median slice of vintage_holdout, relative |
| `metrics.vintage_holdout.sub.bom_balance_log_low.share` | `80d79940` | scalar | 0.500015539 | the share of vintage_holdout the bom_balance_log below_median slice holds |
| `profile.out_of_time.missing.max` | `4dafce11` | scalar | 0 | the largest missing fraction in out_of_time |
| `profile.out_of_time.n` | `fa39c5cf` | scalar | 12257 | rows in out_of_time |
| `profile.test.missing.max` | `f813848d` | scalar | 0 | the largest missing fraction in test |
| `profile.test.n` | `e3abc1b8` | scalar | 15382 | rows in test |
| `profile.train.missing.max` | `050a3099` | scalar | 0 | the largest missing fraction in train |
| `profile.train.n` | `c5ebd9c9` | scalar | 36013 | rows in train |
| `profile.vintage_holdout.missing.max` | `329bb430` | scalar | 0 | the largest missing fraction in vintage_holdout |
| `profile.vintage_holdout.n` | `426e712a` | scalar | 32177 | rows in vintage_holdout |
| `psi.bom_balance_log` | `ce3c425c` | scalar | 0.03017956995 | PSI of bom_balance_log between train and test |
| `psi.burnout` | `9dc7ecc2` | scalar | 0.004614338236 | PSI of burnout between train and test |
| `psi.credit_score` | `7e87527c` | scalar | 0.06188985797 | PSI of credit_score between train and test |
| `psi.incentive` | `2da5570f` | scalar | 0.0009922551416 | PSI of incentive between train and test |
| `psi.loan_age` | `2202b157` | scalar | 0.0001993816816 | PSI of loan_age between train and test |
| `psi.max` | `c2e8c8fd` | scalar | 0.06188985797 | the largest train-to-test PSI, score included |
| `psi.note_rate` | `ecc6adf3` | scalar | 0.01370911382 | PSI of note_rate between train and test |
| `psi.orig_ltv` | `cd1ff136` | scalar | 0.03617297258 | PSI of orig_ltv between train and test |
| `psi.orig_upb_log` | `55030a3b` | scalar | 0.04817081196 | PSI of orig_upb_log between train and test |
| `psi.out_of_time.bom_balance_log` | `9fa682d1` | scalar | 0.08707630682 | PSI of bom_balance_log between train and out_of_time |
| `psi.out_of_time.burnout` | `7b0bbebb` | scalar | 2.944521522 | PSI of burnout between train and out_of_time |
| `psi.out_of_time.credit_score` | `d7249e47` | scalar | 0.05987964443 | PSI of credit_score between train and out_of_time |
| `psi.out_of_time.incentive` | `42076ed1` | scalar | 0.4958065489 | PSI of incentive between train and out_of_time |
| `psi.out_of_time.loan_age` | `d6eaaaf5` | scalar | 2.483993033 | PSI of loan_age between train and out_of_time |
| `psi.out_of_time.note_rate` | `cabd371d` | scalar | 0.6976589281 | PSI of note_rate between train and out_of_time |
| `psi.out_of_time.orig_ltv` | `3eee5db4` | scalar | 0.04300793312 | PSI of orig_ltv between train and out_of_time |
| `psi.out_of_time.orig_upb_log` | `ac349b67` | scalar | 0.07136421414 | PSI of orig_upb_log between train and out_of_time |
| `psi.out_of_time.sato` | `c2233ce6` | scalar | 0.01298850667 | PSI of sato between train and out_of_time |
| `psi.out_of_time.season_cos` | `25cf6b85` | scalar | 0.00752368457 | PSI of season_cos between train and out_of_time |
| `psi.out_of_time.season_sin` | `144e1bd9` | scalar | 0.02788988464 | PSI of season_sin between train and out_of_time |
| `psi.out_of_time.y_score` | `12620838` | scalar | 0.1450932669 | PSI of the score between train and out_of_time |
| `psi.sato` | `584da64f` | scalar | 0.02772829856 | PSI of sato between train and test |
| `psi.season_cos` | `addec503` | scalar | 1.790085913e-05 | PSI of season_cos between train and test |
| `psi.season_sin` | `4d2ed98d` | scalar | 2.939045338e-06 | PSI of season_sin between train and test |
| `psi.vintage_holdout.bom_balance_log` | `b3073b46` | scalar | 0.03706738664 | PSI of bom_balance_log between train and vintage_holdout |
| `psi.vintage_holdout.burnout` | `e29067e6` | scalar | 0.04749372789 | PSI of burnout between train and vintage_holdout |
| `psi.vintage_holdout.credit_score` | `3498d307` | scalar | 0.03995819732 | PSI of credit_score between train and vintage_holdout |
| `psi.vintage_holdout.incentive` | `5e61b6f9` | scalar | 0.4475226601 | PSI of incentive between train and vintage_holdout |
| `psi.vintage_holdout.loan_age` | `6d92c48b` | scalar | 0.07111526296 | PSI of loan_age between train and vintage_holdout |
| `psi.vintage_holdout.note_rate` | `f281f8a7` | scalar | 0.608822927 | PSI of note_rate between train and vintage_holdout |
| `psi.vintage_holdout.orig_ltv` | `d07cfb7d` | scalar | 0.0294150369 | PSI of orig_ltv between train and vintage_holdout |
| `psi.vintage_holdout.orig_upb_log` | `77ec758a` | scalar | 0.04039645306 | PSI of orig_upb_log between train and vintage_holdout |
| `psi.vintage_holdout.sato` | `eea64c25` | scalar | 0.02989256711 | PSI of sato between train and vintage_holdout |
| `psi.vintage_holdout.season_cos` | `9fe842a8` | scalar | 0.0012879007 | PSI of season_cos between train and vintage_holdout |
| `psi.vintage_holdout.season_sin` | `b0dc9745` | scalar | 0.0007309374015 | PSI of season_sin between train and vintage_holdout |
| `psi.vintage_holdout.y_score` | `33ffbed6` | scalar | 0.05813498782 | PSI of the score between train and vintage_holdout |
| `psi.y_score` | `2ad82680` | scalar | 0.01873789359 | PSI of the score between train and test |
| `run.features` | `61276a96` | json | json | the subject's features.json |
| `run.metrics` | `e8f6c83d` | json | json | the subject's metrics.json |
| `run.model_summary` | `f6c2df89` | json | json | the subject's model_summary.json |
| `run.projection` | `7d3ba32d` | json | json | the subject's projection.json |
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |
| `scenario.convexity` | `4451c907` | scalar | 140.7189167 | the value change at -300 bp plus the change at 300 bp; negative when the fall outweighs the rise |
| `scenario.value_by_shock` | `c4d5cb25` | table | table, 7 rows | servicing value, its change from the base case and first-year CPR, by shock |
| `scenario.value_change.-100` | `0445ffec` | scalar | -57.14884469 | change in servicing value at -100 bp |
| `scenario.value_change.-200` | `75d82514` | scalar | -83.77616324 | change in servicing value at -200 bp |
| `scenario.value_change.-300` | `0f83fead` | scalar | -92.10987115 | change in servicing value at -300 bp |
| `scenario.value_change.0` | `1e1b0b88` | scalar | 0 | change in servicing value at 0 bp |
| `scenario.value_change.100` | `d16cc2a1` | scalar | 77.1836951 | change in servicing value at 100 bp |
| `scenario.value_change.200` | `4871ddee` | scalar | 155.7824864 | change in servicing value at 200 bp |
| `scenario.value_change.300` | `a0678af4` | scalar | 232.8287879 | change in servicing value at 300 bp |
| `sign_check.bom_balance_log.agrees` | `26b1789b` | scalar | 1 | 1 when the fitted sign on bom_balance_log agrees with its univariate direction, 0 when it does not |
| `sign_check.bom_balance_log.coef_sign` | `d2e88db3` | scalar | -1 | the sign of the fitted coefficient on bom_balance_log |
| `sign_check.bom_balance_log.univariate_direction` | `8ee4f8fe` | scalar | -1 | the sign of bom_balance_log's own single-feature AUC on train minus 0.5 |
| `sign_check.burnout.agrees` | `56826e40` | scalar | 0 | 1 when the fitted sign on burnout agrees with its univariate direction, 0 when it does not |
| `sign_check.burnout.coef_sign` | `dcfb2de4` | scalar | -1 | the sign of the fitted coefficient on burnout |
| `sign_check.burnout.univariate_direction` | `bfc96bb2` | scalar | 1 | the sign of burnout's own single-feature AUC on train minus 0.5 |
| `sign_check.credit_score.agrees` | `915bf8eb` | scalar | 1 | 1 when the fitted sign on credit_score agrees with its univariate direction, 0 when it does not |
| `sign_check.credit_score.coef_sign` | `1ec1078b` | scalar | 1 | the sign of the fitted coefficient on credit_score |
| `sign_check.credit_score.univariate_direction` | `42303896` | scalar | 1 | the sign of credit_score's own single-feature AUC on train minus 0.5 |
| `sign_check.incentive.agrees` | `f7b2338e` | scalar | 1 | 1 when the fitted sign on incentive agrees with its univariate direction, 0 when it does not |
| `sign_check.incentive.coef_sign` | `684cf11a` | scalar | 1 | the sign of the fitted coefficient on incentive |
| `sign_check.incentive.univariate_direction` | `8098d951` | scalar | 1 | the sign of incentive's own single-feature AUC on train minus 0.5 |
| `sign_check.n_disagreements` | `66ce738a` | scalar | 2 | retained features whose fitted sign contradicts their univariate direction, of 10 checked |
| `sign_check.note_rate.agrees` | `ca18290e` | scalar | 1 | 1 when the fitted sign on note_rate agrees with its univariate direction, 0 when it does not |
| `sign_check.note_rate.coef_sign` | `0e3296a5` | scalar | 1 | the sign of the fitted coefficient on note_rate |
| `sign_check.note_rate.univariate_direction` | `61f6e1ac` | scalar | 1 | the sign of note_rate's own single-feature AUC on train minus 0.5 |
| `sign_check.orig_ltv.agrees` | `7021aeb0` | scalar | 1 | 1 when the fitted sign on orig_ltv agrees with its univariate direction, 0 when it does not |
| `sign_check.orig_ltv.coef_sign` | `7eec65ec` | scalar | -1 | the sign of the fitted coefficient on orig_ltv |
| `sign_check.orig_ltv.univariate_direction` | `76dbc708` | scalar | -1 | the sign of orig_ltv's own single-feature AUC on train minus 0.5 |
| `sign_check.orig_upb_log.agrees` | `07a9d3e6` | scalar | 1 | 1 when the fitted sign on orig_upb_log agrees with its univariate direction, 0 when it does not |
| `sign_check.orig_upb_log.coef_sign` | `5aa309fc` | scalar | 1 | the sign of the fitted coefficient on orig_upb_log |
| `sign_check.orig_upb_log.univariate_direction` | `b9743ecb` | scalar | 1 | the sign of orig_upb_log's own single-feature AUC on train minus 0.5 |
| `sign_check.sato.agrees` | `2401eba2` | scalar | 1 | 1 when the fitted sign on sato agrees with its univariate direction, 0 when it does not |
| `sign_check.sato.coef_sign` | `c031d0d5` | scalar | 1 | the sign of the fitted coefficient on sato |
| `sign_check.sato.univariate_direction` | `c08233a6` | scalar | 1 | the sign of sato's own single-feature AUC on train minus 0.5 |
| `sign_check.season_cos.agrees` | `7f18ddf7` | scalar | 1 | 1 when the fitted sign on season_cos agrees with its univariate direction, 0 when it does not |
| `sign_check.season_cos.coef_sign` | `7dbb1ffc` | scalar | -1 | the sign of the fitted coefficient on season_cos |
| `sign_check.season_cos.univariate_direction` | `03e931f0` | scalar | -1 | the sign of season_cos's own single-feature AUC on train minus 0.5 |
| `sign_check.season_sin.agrees` | `74f2d0e0` | scalar | 0 | 1 when the fitted sign on season_sin agrees with its univariate direction, 0 when it does not |
| `sign_check.season_sin.coef_sign` | `92ed5b5f` | scalar | -1 | the sign of the fitted coefficient on season_sin |
| `sign_check.season_sin.univariate_direction` | `cae6b096` | scalar | 1 | the sign of season_sin's own single-feature AUC on train minus 0.5 |
| `stability.auc_by_regime` | `9edbf2d0` | table | table, 2 rows | the champion's AUC within each rate_regime on train |
| `stability.bom_balance_log.sign_flip` | `a9b4364d` | scalar | 0 | 1 when bom_balance_log is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.burnout.sign_flip` | `6bc05e82` | scalar | 0 | 1 when burnout is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.credit_score.sign_flip` | `d956c276` | scalar | 0 | 1 when credit_score is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.incentive.sign_flip` | `0cc7a37d` | scalar | 0 | 1 when incentive is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.loan_age.sign_flip` | `b7191217` | scalar | 0 | 1 when loan_age is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.note_rate.sign_flip` | `e7ce4912` | scalar | 0 | 1 when note_rate is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.orig_ltv.sign_flip` | `054d5fab` | scalar | 0 | 1 when orig_ltv is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.orig_upb_log.sign_flip` | `fb1ae6c8` | scalar | 0 | 1 when orig_upb_log is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.sato.sign_flip` | `1f302ccd` | scalar | 0 | 1 when sato is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.season_cos.sign_flip` | `1850e2de` | scalar | 0 | 1 when season_cos is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.season_sin.sign_flip` | `6ba36a3b` | scalar | 0 | 1 when season_sin is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `threshold.C1.calibration_slope.max` | `b6672579` | scalar | 1.2 | C1: the top of the calibration slope band |
| `threshold.C1.calibration_slope.min` | `749634ae` | scalar | 0.8 | C1: the bottom of the calibration slope band |
| `threshold.C1.mean_ratio_rel` | `20e93a8c` | scalar | 0.25 | C1: mean predicted against observed, relative |
| `threshold.D1.missing_gap` | `9cce25ea` | scalar | 0.1 | D1: the missingness gap between splits, as a fraction |
| `threshold.E1.delta_auc` | `e042774c` | scalar | 0.03 | E1: the challenger's AUC lead over the champion |
| `threshold.L1.single_feature_auc` | `c29e7a34` | scalar | 0.9 | L1: the AUC one feature may reach on its own |
| `threshold.L2.overlap` | `9f336eaf` | scalar | 0.005 | L2: the fraction of test rows that may also be in train |
| `threshold.L2.overlap.features_effective` | `1ee888c5` | scalar | 0.005 | L2: the bound the feature-overlap rule applied, the larger of threshold.L2.overlap and 2 x leakage.duplicates.train |
| `threshold.M1.condition_number` | `7e52fd7a` | scalar | 30 | M1: Belsley's condition number of the design |
| `threshold.M1.vif` | `aeb4f33c` | scalar | 10 | M1: the variance inflation factor of any retained feature |
| `threshold.O1.auc_gap` | `630f28f4` | scalar | 0.08 | O1: the train-to-test AUC gap |
| `threshold.O1.holdout_gap` | `90f8b6d9` | scalar | 0.05 | O1: how far a period split's AUC may fall below test |
| `threshold.O1.slice_auc_gap` | `0a827b87` | scalar | 0.08 | how far a sub-population's AUC may fall below the split's before the result is an open item; it raises no candidate |
| `threshold.O1.slice_max_share` | `a928a05c` | scalar | 0.95 | the share of a split at which a sub-population is the whole split and is refused |
| `threshold.O1.slice_min_share` | `9a6f1a87` | scalar | 0.1 | the share of a split a sub-population must hold before it can raise an open item |
| `threshold.R1.auc_gap` | `b64213d7` | scalar | 0.1 | R1: the AUC difference across regimes |
| `threshold.R1.sign_flip_coef` | `aca84377` | scalar | 0.05 | R1: the coefficient a sign flip must exceed in both regimes |
| `threshold.R1.sign_flip_z` | `2e4428c7` | scalar | 2 | R1: the \|z\| a sign flip's coefficient must reach in both regimes |
| `threshold.S1.psi` | `278b9016` | scalar | 0.25 | S1: the population stability index, train against test |
| `threshold.package.auc.test.min` | `fececac1` | scalar | 0.65 | package.yaml declares auc min 0.65 |
| `threshold.package.psi.max` | `fbb5a9d1` | scalar | 0.25 | package.yaml declares psi max 0.25 |
| `thresholds.evaluation` | `25af6e79` | table | table, 4 rows | every threshold package.yaml declares, with its bound, the recomputed value and the outcome |
| `vif.bom_balance_log` | `0b30efbf` | scalar | 1.142939813 | variance inflation factor of bom_balance_log on train |
| `vif.burnout` | `91e7ce55` | scalar | 3.439982425 | variance inflation factor of burnout on train |
| `vif.credit_score` | `b8652149` | scalar | 1.009199828 | variance inflation factor of credit_score on train |
| `vif.incentive` | `d924a341` | scalar | 2.234058893 | variance inflation factor of incentive on train |
| `vif.loan_age` | `43980218` | scalar | 2.930049511 | variance inflation factor of loan_age on train |
| `vif.max` | `b1d416c0` | scalar | 4.977599595 | the largest variance inflation factor |
| `vif.orig_ltv` | `10f2f018` | scalar | 1.004907818 | variance inflation factor of orig_ltv on train |
| `vif.orig_upb_log` | `347761f6` | scalar | 1.134478986 | variance inflation factor of orig_upb_log on train |
| `vif.sato` | `08e0ca20` | scalar | 1.712581428 | variance inflation factor of sato on train |
| `vif.season_cos` | `a2dc57c7` | scalar | 1.01775523 | variance inflation factor of season_cos on train |
| `vif.season_sin` | `5069e43c` | scalar | 1.004179036 | variance inflation factor of season_sin on train |

## Appendix C — Run trace summary

| quantity | value |
|---|---|
| tool calls | 18 (run_model 1, profile_data 1, compute_metrics 3, check_leakage 2, check_stability 1, check_collinearity 1, challenger_compare 1, run_scenarios 1, retrieve_guidance 7) |
| plan steps (bounded loop) | 4 |
| LLM calls | 20 (plan 4, draft 8, extract 8) |
| re-asks | 0 |
| repair rounds | 1 |
| tokens in / out | 250,734 / 116,498 |
| notional cost (USD) | 5.4684 |
| wall-clock (s) | 1275.79 |
| subject run (s) | 2.47 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | msr_prepayment-full_agent-20260920T181437Z-e61d346a |

## Appendix D — Not checked

| item | reason |
|---|---|
| developer claims (T1, claim channel) | The package declares 3 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
