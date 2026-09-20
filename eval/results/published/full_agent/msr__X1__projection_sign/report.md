---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: msr_prepayment
version: "1.0"
model_type: discrete_time_hazard
configuration: full_agent
model: claude-opus-5[1m]
run_id: msr_prepayment-full_agent-20260920T202713Z-e61d346a
data_mode: synthetic
synthetic_n: 2000
grounding_precision_pre: 0.9849
grounding_precision_post: 1.0000
n_claims: 326
n_findings_by_severity: {high: 1, medium: 0, low: 0, info: 0}
generated: "2026-09-20T20:27:13Z"
illustrative: false
---

# Validation report — `msr_prepayment` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `msr_prepayment` v1.0 | `full_agent` | claude-opus-5[1m] | synthetic, n = 2000 | 0.9849 → 1.0000 | 1 / 0 / 0 / 0 |
<!-- quaestor:renderer:end -->

The subject of this report is the model package msr_prepayment version 1.0, a probability model that predicts whether a loan prepays over the modelled horizon, and the report follows the structure of the Federal Reserve's model risk management guidance on model validation and monitoring [[reg:SR26-2:V]].

The subject was re-run from its package definition and every metric quoted below was recomputed by the validator from the model's scored output, under the wall-clock cap of 300 [[art:2ad8d1a5:runtime.max_seconds]] seconds the package declares.
The development split holds 36013 [[art:6fdfeabb:metrics.train.n]] rows and the test split holds 15382 [[art:e55953e1:metrics.test.n]] rows.
The out-of-time split holds 12257 [[art:7898809e:metrics.out_of_time.n]] rows and the vintage holdout holds 32177 [[art:37a92951:metrics.vintage_holdout.n]] rows.

Discrimination on test, at 0.7753 [[art:57066271:metrics.test.auc]], sits above the developer-declared floor of 0.65 [[art:fececac1:threshold.package.auc.test.min]].
The calibration slope on test, at 0.9365 [[art:3e42ee62:calibration_slope.test]], lies inside the declared band running from 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] to 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The largest train-to-test population stability index, at 0.06189 [[art:c2e8c8fd:psi.max]], is below the declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
On each declared threshold recomputed here, the subject passes.

Discrimination is of a similar order on the later splits, at 0.7846 [[art:6f2a2d99:metrics.out_of_time.auc]] out of time and 0.7718 [[art:ac6794c5:metrics.vintage_holdout.auc]] on the vintage holdout.
The recomputed calibration slopes are 0.9937 [[art:534cb102:calibration_slope.train]] on train, 0.9365 [[art:3e42ee62:calibration_slope.test]] on test, 0.9969 [[art:a49b2789:calibration_slope.out_of_time]] out of time and 0.8373 [[art:08d6b321:calibration_slope.vintage_holdout]] on the vintage holdout, the last being the lowest among them and the furthest below the declared floor's side of the band.

This validation published F-001, a X1 scenario analysis finding at high severity, raised out of the scenario run.
Section 6 sets that finding out in full, with its evidence and its recommended disposition.

## 2. Conceptual soundness

This section assesses the design and construction of the champion, the developmental evidence behind its variable selection, and the benchmarking that constitutes effective challenge [[reg:SR26-2:V.1.a]].

### Design and inputs

The champion is a parametric regression scoring a binary prepayment outcome, with an intercept of -5.502 [[art:b764932a:run.model_summary#intercept]] and a coefficient on each retained term, fitted on 36013 [[art:b764932a:run.model_summary#n_train]] loan-months drawn from 934 [[art:b764932a:run.model_summary#n_train_loans]] loans.
Loan age enters through a spline basis rather than a linear term, which is the conventional way to let the seasoning ramp bend.
The feature inventory holds 12 [[art:61276a96:run.features#n]] features.
Of these, 5 [[art:61276a96:run.features#at_origination]] are fixed at origination and 7 [[art:61276a96:run.features#before_period_start]] are known before the performance period opens.
No feature is observed during the period, at 0 [[art:61276a96:run.features#during_period]], and none is observed only after the outcome is known, at 0 [[art:61276a96:run.features#after_outcome]].
On timing alone, then, every input is available at the point the score would have to be produced, which is the property a prepayment model used for servicing-asset valuation needs.

The developer's own screen removed terms on collinearity grounds against a variance inflation cutoff of 10 [[art:b764932a:run.model_summary#vif_threshold]].
The twelve-month rate change was dropped at a variance inflation of 12.38 [[art:b764932a:run.model_summary#removed.rate_change_12m.vif]], modestly above that cutoff and plainly overlapping the refinance incentive and the spread-at-origination term, which both carry rate movement.
The log beginning-of-month balance was dropped at 40090 [[art:b764932a:run.model_summary#removed.bom_balance_log.vif]], far above the cutoff and consistent with near-exact redundancy against the log origination balance together with the loan age terms, since amortisation makes current balance a deterministic function of the two.
Removing that term is the right call on construction grounds, and it also removes a quantity that moves with the outcome being modelled.

### Coefficients and expected signs

The largest coefficient in the fitted model is on the refinance incentive at 1.253 [[art:b764932a:run.model_summary#coefficients.incentive.value]], positive, which is what prepayment behaviour requires: borrowers further in the money refinance more.
The loan age spline terms take values 0.6491 [[art:b764932a:run.model_summary#coefficients.loan_age_spline_1.value]], 0.04548 [[art:b764932a:run.model_summary#coefficients.loan_age_spline_2.value]], -0.09539 [[art:b764932a:run.model_summary#coefficients.loan_age_spline_3.value]] and -0.2386 [[art:b764932a:run.model_summary#coefficients.loan_age_spline_4.value]] in basis order, a profile that rises early and turns down later, which is the seasoning shape the subject matter expects.
Credit score enters positive at 0.4074 [[art:b764932a:run.model_summary#coefficients.credit_score.value]], consistent with stronger borrowers being better able to qualify for a refinance.
The log origination balance enters positive at 0.3036 [[art:b764932a:run.model_summary#coefficients.orig_upb_log.value]], consistent with larger balances making the fixed cost of refinancing worth paying.
Original loan-to-value enters negative at -0.243 [[art:b764932a:run.model_summary#coefficients.orig_ltv.value]], consistent with thinner equity constraining refinance eligibility.
The spread at origination enters positive at 0.01282 [[art:b764932a:run.model_summary#coefficients.sato.value]], small relative to the other terms.
The seasonality terms take 0.0702 [[art:b764932a:run.model_summary#coefficients.season_sin.value]] and -0.1239 [[art:b764932a:run.model_summary#coefficients.season_cos.value]], a mild annual cycle.
Burnout enters positive at 0.07952 [[art:b764932a:run.model_summary#coefficients.burnout.value]], which runs against the usual expectation that a pool already exposed to refinance opportunity prepays less, though its own univariate direction points the same way as the fit, at 1 [[art:bfc96bb2:sign_check.burnout.univariate_direction]] against a fitted sign of 1 [[art:a3063608:sign_check.burnout.coef_sign]], so the tension is with prior expectation rather than with the data as this model measures it.
The note rate enters negative at -0.4457 [[art:b764932a:run.model_summary#coefficients.note_rate.value]], where a higher note rate is the rate the borrower stands to refinance away from and would ordinarily be expected to raise prepayment.

Across the retained features checked, the fitted sign contradicts the feature's own univariate direction in 1 [[art:f96ece96:sign_check.n_disagreements]] case, and that case is the note rate.
Its fitted coefficient carries sign -1 [[art:aecf7ccb:sign_check.note_rate.coef_sign]] while its single-feature relationship with the outcome on train carries sign 1 [[art:61f6e1ac:sign_check.note_rate.univariate_direction]], and the agreement indicator stands at 0 [[art:a453463d:sign_check.note_rate.agrees]].
Refitting the champion's form without the note rate changes test AUC by -0.002585 [[art:14558b82:ablation.note_rate.delta_auc]], so the term is carrying a little discrimination but the model is not leaning on it; the disagreement is a small one in effect, and it is readable as a partial effect, since the incentive and spread-at-origination terms already carry the rate signal the note rate would otherwise supply on its own.
Every other checked feature agrees: the refinance incentive at 1 [[art:f7b2338e:sign_check.incentive.agrees]], credit score at 1 [[art:915bf8eb:sign_check.credit_score.agrees]], the log origination balance at 1 [[art:07a9d3e6:sign_check.orig_upb_log.agrees]], original loan-to-value at 1 [[art:7021aeb0:sign_check.orig_ltv.agrees]], the spread at origination at 1 [[art:2401eba2:sign_check.sato.agrees]], burnout at 1 [[art:2eec20ab:sign_check.burnout.agrees]], and the two seasonality terms at 1 [[art:e110f357:sign_check.season_sin.agrees]] and 1 [[art:7f18ddf7:sign_check.season_cos.agrees]].
The fitted and univariate signs match on the incentive at 1 [[art:684cf11a:sign_check.incentive.coef_sign]] and 1 [[art:8098d951:sign_check.incentive.univariate_direction]], on credit score at 1 [[art:1ec1078b:sign_check.credit_score.coef_sign]] and 1 [[art:42303896:sign_check.credit_score.univariate_direction]], on the log origination balance at 1 [[art:5aa309fc:sign_check.orig_upb_log.coef_sign]] and 1 [[art:b9743ecb:sign_check.orig_upb_log.univariate_direction]], on original loan-to-value at -1 [[art:7eec65ec:sign_check.orig_ltv.coef_sign]] and -1 [[art:76dbc708:sign_check.orig_ltv.univariate_direction]], on the spread at origination at 1 [[art:c031d0d5:sign_check.sato.coef_sign]] and 1 [[art:c08233a6:sign_check.sato.univariate_direction]], and on the seasonality terms at 1 [[art:761188ce:sign_check.season_sin.coef_sign]] against 1 [[art:cae6b096:sign_check.season_sin.univariate_direction]] and -1 [[art:7dbb1ffc:sign_check.season_cos.coef_sign]] against -1 [[art:03e931f0:sign_check.season_cos.univariate_direction]].

### What the model is actually using

Ablation refits the champion's form on the retained set and drops one feature at a time, measuring from a refit level of 0.7673 [[art:54367df6:ablation.baseline_auc]], which sits below the champion's recomputed test AUC, so the deltas should be read against that level rather than against the champion's own headline discrimination.
The refinance incentive carries the most discrimination, at -0.04117 [[art:78108590:ablation.incentive.delta_auc]], further from zero than any other term's delta and consistent with its being the largest coefficient and the economically central driver.
The log origination balance follows at -0.01927 [[art:0ddb11a9:ablation.orig_upb_log.delta_auc]] and credit score at -0.01474 [[art:9bdeb0df:ablation.credit_score.delta_auc]].
Below those sit original loan-to-value at -0.002294 [[art:57ea66c5:ablation.orig_ltv.delta_auc]] and the note rate at -0.002585 [[art:14558b82:ablation.note_rate.delta_auc]], the seasonality terms at -0.0004826 [[art:a288439d:ablation.season_cos.delta_auc]] and -0.0003885 [[art:e54c8581:ablation.season_sin.delta_auc]], and burnout at -0.0001876 [[art:3cba039b:ablation.burnout.delta_auc]], all close enough to zero that the model would discriminate on test much as it does without them.
Test AUC rises when loan age is dropped, at 0.0008166 [[art:be669163:ablation.loan_age.delta_auc]], and when the spread at origination is dropped, at 0.0005201 [[art:57703504:ablation.sato.delta_auc]], so neither term is buying test discrimination on this split despite the seasoning spline being theoretically central to prepayment.
That is a design observation worth carrying forward: the spline's shape is what theory expects, but its contribution to ranking on the test split is not positive, and a reviewer should not treat the presence of a theoretically motivated term as evidence that it is doing work.

### Effective challenge

Benchmarking against an alternative specification is the practical form of effective challenge for a model of this kind [[reg:SR26-2:IV.1]].
The challenger reaches an AUC on test of 0.7337 [[art:705b66f0:challenger.auc]] against the champion's recomputed test AUC of 0.7753 [[art:57066271:metrics.test.auc]].
The challenger's margin over the champion is -0.04155 [[art:4d28c096:challenger.delta_auc]], that is, the challenger trails on discrimination.
The declared threshold for the difference to matter is a challenger lead of 0.03 [[art:e042774c:threshold.E1.delta_auc]], and the observed margin is negative and therefore on the opposite side of that threshold, so the challenger does not displace the champion.
The same ordering holds on calibration, where the champion's Brier score on test is 0.007894 [[art:7d3583cd:metrics.test.brier]] and the challenger's is 0.00863 [[art:85a89ef9:challenger.brier]], the larger of the two and so the worse.
The challenge is therefore real but not decisive against the champion: the alternative is worse on both the ranking and the probability metric, which supports retaining the champion's form while leaving the question of whether a stronger challenger exists open.

### Assessment

On design, the champion's inputs are all known before the outcome window, the collinearity screen removed the terms that most plainly duplicated retained information, and the coefficients on the incentive, credit score, balance, loan-to-value and seasoning terms point the way prepayment behaviour expects.
The one sign disagreement sits on a term the ablation evidence shows the model barely relies on, and the terms the model does rely on all carry expected signs.
The weaker points of the developmental evidence are the seasoning spline and the spread-at-origination term, whose removal does not cost test discrimination, and the burnout coefficient, whose sign runs against conventional expectation even though the data as fitted agree with it.

## 3. Data integrity and drift

Sound development practice includes a critical assessment of data quality, relevance, and inputs, and this section reviews the data behind msr_prepayment 1.0 against the thresholds the package declares [[reg:SR26-2:IV.1]].

### Split sizes and missingness

The evaluation splits hold 36013 [[art:c5ebd9c9:profile.train.n]] rows for training, 15382 [[art:e3abc1b8:profile.test.n]] rows for test, 32177 [[art:426e712a:profile.vintage_holdout.n]] rows for the vintage holdout and 12257 [[art:fa39c5cf:profile.out_of_time.n]] rows for the out-of-time window.
The largest missing fraction of any column is 0 [[art:050a3099:profile.train.missing.max]] in train, 0 [[art:f813848d:profile.test.missing.max]] in test, 0 [[art:329bb430:profile.vintage_holdout.missing.max]] in the vintage holdout and 0 [[art:4dafce11:profile.out_of_time.missing.max]] in the out-of-time window.
Every one of those four values lies below the declared allowance for the missingness gap between splits, 0.1 [[art:9cce25ea:threshold.D1.missing_gap]], and the four are equal to one another, so the splits do not separate from each other on missingness at all.
Complete columns in every split mean that no imputation convention stands between the training population and the held-out ones, which removes one common source of split-to-split incomparability.

### Population stability, train against the other splits

The declared bound on the population stability index is 0.25 [[art:278b9016:threshold.S1.psi]], which is the same bound the package manifest declares, 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
Between train and test the largest population shift over the features and the model score is 0.06189 [[art:c2e8c8fd:psi.max]], attributable to credit_score at 0.06189 [[art:7e87527c:psi.credit_score]], and it sits below the declared bound of 0.25 [[art:278b9016:threshold.S1.psi]].
The remaining train-to-test shifts are smaller: orig_upb_log at 0.04817 [[art:55030a3b:psi.orig_upb_log]], orig_ltv at 0.03617 [[art:cd1ff136:psi.orig_ltv]], sato at 0.02773 [[art:584da64f:psi.sato]], note_rate at 0.01371 [[art:ecc6adf3:psi.note_rate]], burnout at 0.004614 [[art:9dc7ecc2:psi.burnout]], incentive at 0.0009923 [[art:2da5570f:psi.incentive]], loan_age at 0.0001994 [[art:2202b157:psi.loan_age]], season_cos at 1.79e-05 [[art:addec503:psi.season_cos]] and season_sin at 2.939e-06 [[art:4d2ed98d:psi.season_sin]].
The model score itself shifts by 0.001953 [[art:3b9dee2d:psi.y_score]] between train and test, below the declared bound of 0.25 [[art:278b9016:threshold.S1.psi]], so the test split is drawn from substantially the same population the model was fitted on.

The two time-displaced splits behave differently, and several of their shifts stand above the declared bound of 0.25 [[art:278b9016:threshold.S1.psi]].
In the out-of-time window, burnout shifts by 2.945 [[art:7b0bbebb:psi.out_of_time.burnout]], loan_age by 2.484 [[art:d6eaaaf5:psi.out_of_time.loan_age]], note_rate by 0.6977 [[art:cabd371d:psi.out_of_time.note_rate]] and incentive by 0.4958 [[art:42076ed1:psi.out_of_time.incentive]], each above that bound.
The model score shifts by 0.7056 [[art:2dc61374:psi.out_of_time.y_score]] over the same window, also above the declared bound of 0.25 [[art:278b9016:threshold.S1.psi]], so the drift in the inputs carries through to the output distribution rather than cancelling within it.
The other out-of-time shifts remain below that bound: orig_upb_log at 0.07136 [[art:ac349b67:psi.out_of_time.orig_upb_log]], credit_score at 0.05988 [[art:d7249e47:psi.out_of_time.credit_score]], orig_ltv at 0.04301 [[art:3eee5db4:psi.out_of_time.orig_ltv]], season_sin at 0.02789 [[art:144e1bd9:psi.out_of_time.season_sin]], sato at 0.01299 [[art:c2233ce6:psi.out_of_time.sato]] and season_cos at 0.007524 [[art:25cf6b85:psi.out_of_time.season_cos]].
In the vintage holdout, note_rate shifts by 0.6088 [[art:f281f8a7:psi.vintage_holdout.note_rate]] and incentive by 0.4475 [[art:5e61b6f9:psi.vintage_holdout.incentive]], both above the declared bound of 0.25 [[art:278b9016:threshold.S1.psi]], while loan_age at 0.07112 [[art:6d92c48b:psi.vintage_holdout.loan_age]], burnout at 0.04749 [[art:e29067e6:psi.vintage_holdout.burnout]], orig_upb_log at 0.0404 [[art:77ec758a:psi.vintage_holdout.orig_upb_log]], credit_score at 0.03996 [[art:3498d307:psi.vintage_holdout.credit_score]], sato at 0.02989 [[art:eea64c25:psi.vintage_holdout.sato]], orig_ltv at 0.02942 [[art:d07cfb7d:psi.vintage_holdout.orig_ltv]], season_cos at 0.001288 [[art:9fe842a8:psi.vintage_holdout.season_cos]] and season_sin at 0.0007309 [[art:b0dc9745:psi.vintage_holdout.season_sin]] all lie below it.
The score shift in the vintage holdout is 0.1421 [[art:3713457e:psi.vintage_holdout.y_score]], below the declared bound of 0.25 [[art:278b9016:threshold.S1.psi]], unlike the score shift in the out-of-time window.
Comparing the two displaced populations feature by feature at the level of the reported indices, and not as a difference or a ratio between them, the burnout shift is larger in the out-of-time window at 2.945 [[art:7b0bbebb:psi.out_of_time.burnout]] than in the vintage holdout at 0.04749 [[art:e29067e6:psi.vintage_holdout.burnout]], the loan_age shift is likewise larger out of time at 2.484 [[art:d6eaaaf5:psi.out_of_time.loan_age]] than in the vintage holdout at 0.07112 [[art:6d92c48b:psi.vintage_holdout.loan_age]], and the note_rate and incentive shifts stand above the declared bound in both.
The declared bound is stated for train against test, so its application to the two time-displaced splits is read here as a diagnostic reference rather than as the bound those splits were set against.

### Characteristic stability

At the characteristic level, the largest single contribution to the shift in the linear predictor is 0.03438 [[art:54bd75b0:csi.max]], carried by orig_ltv at 0.03438 [[art:97d51193:csi.orig_ltv]], which lies below the declared stability bound of 0.25 [[art:278b9016:threshold.S1.psi]].
The remaining contributions are note_rate at 0.01822 [[art:92901ac4:csi.note_rate]], credit_score at 0.007909 [[art:c40b4ede:csi.credit_score]], incentive at 0.005804 [[art:874ef644:csi.incentive]], orig_upb_log at 0.002969 [[art:bb919ade:csi.orig_upb_log]], sato at 0.001487 [[art:6a5f7a41:csi.sato]], burnout at 0.0009851 [[art:b2729e08:csi.burnout]], season_cos at 0.0004785 [[art:75b544aa:csi.season_cos]], season_sin at 7.624e-05 [[art:d55271d6:csi.season_sin]] and loan_age at 0 [[art:df52c920:csi.loan_age]].
The ordering of these contributions does not follow the ordering of the population shifts above, which indicates that the features moving most between the splits are not uniformly the ones carrying the most weight in the predictor.

### Leakage screens

No feature is declared as observed during the performance period or after the outcome, with 0 [[art:742bcd24:leakage.timing.n_flagged]] features so declared, so the declared timing of the inputs raises nothing on its face.
The strongest single feature reaches an AUC of 0.7239 [[art:1fe630dd:leakage.target_corr.max_single_feature_auc]], below the declared allowance of 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]], which is the level at which one input would be doing the work of the target itself.
The share of test rows whose feature values also appear in train is 0 [[art:4c9fcd09:leakage.overlap]].

The contamination screen has two arms and each is read against its own bound.
The share of test rows whose loan and period identifiers also identify a row of train is 0 [[art:63d37fc5:leakage.overlap.ids]], below the declared allowance of 0.005 [[art:9f336eaf:threshold.L2.overlap]].
The share of test rows whose feature vectors also appear in train is 0 [[art:0fec8048:leakage.overlap.features]], read against the bound the feature-overlap rule actually applied, 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].
That applied bound is the larger of the declared overlap allowance and a multiple of the share of train rows whose feature values are not unique within train, the latter being 0 [[art:4474c227:leakage.duplicates.train]]; the widening term therefore contributed nothing here, and the applied bound of 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]] coincides with the declared allowance of 0.005 [[art:9f336eaf:threshold.L2.overlap]].
The rationale for the wider bound on the feature arm is that two distinct subjects may write the same discrete row by coincidence, which is not contamination; with no repeated feature vectors inside train, that allowance is not being relied on.
The name screen matches 0 [[art:407e62be:leakage.name_screen.n_matched]] feature names against the target-adjacent lexicon, so no input is flagged as a renamed restatement of the outcome.

### Assessment

On missingness, train-to-test population stability, characteristic stability and every leakage and contamination screen, the reported values sit on the permissive side of the bound each was read against.
The material qualification is temporal: on the out-of-time window several input shifts and the score shift stand above the stability bound declared for train against test, and on the vintage holdout the note_rate and incentive shifts do so while the score shift does not.
This bears on how far performance measured on the test split can be read as indicative of behaviour on periods displaced from the training window, and it is the basis on which the ongoing-monitoring discussion elsewhere in this report should be read.

## 4. Outcomes analysis

Outcomes analysis here compares the model's recomputed outputs with the realised outcomes on each split, in the sense of the guidance that outcomes analysis assesses model performance relative to model objectives and business use [[reg:SR26-2:V.1.b]].

This section reports calibration before discrimination.
The reason is the declared use: package.yaml states that this model's output is consumed as a probability and not only as a ranking, so whether the predicted probabilities mean what they say is the leading question, whatever the level of the event rate turns out to be.
Rank-ordering evidence follows, and is read as secondary to the level of the probabilities.

### Calibration

The calibration slope, from the logistic regression of the outcome on the logit of the predicted probability, is 0.9937 [[art:534cb102:calibration_slope.train]] on train, 0.9365 [[art:3e42ee62:calibration_slope.test]] on test, 0.9969 [[art:a49b2789:calibration_slope.out_of_time]] on the out-of-time split and 0.8373 [[art:08d6b321:calibration_slope.vintage_holdout]] on the vintage holdout.
All four sit inside the declared band, whose floor is 0.8 [[art:749634ae:threshold.C1.calibration_slope.min]] and whose ceiling is 1.2 [[art:b6672579:threshold.C1.calibration_slope.max]], with the vintage holdout the nearest of the four to the floor.
The intercept of the same regression is -0.01454 [[art:11d7a3ca:calibration_intercept.train]] on train, -0.277 [[art:e87b5c13:calibration_intercept.test]] on test, -0.06272 [[art:fc7ece3a:calibration_intercept.out_of_time]] on the out-of-time split and -0.9028 [[art:44715143:calibration_intercept.vintage_holdout]] on the vintage holdout.
The intercepts are negative on every split, and the vintage holdout carries the one furthest from zero.

Mean predicted probability against the observed event rate reads 0.008427 [[art:a63f6555:metrics.train.mean_predicted]] against 0.008525 [[art:b9ef3327:metrics.train.event_rate]] on train, 0.008116 [[art:3bc93911:metrics.test.mean_predicted]] against 0.008061 [[art:570cc08a:metrics.test.event_rate]] on test, 0.01887 [[art:3833e0c5:metrics.out_of_time.mean_predicted]] against 0.01795 [[art:83ccf5c0:metrics.out_of_time.event_rate]] on the out-of-time split, and 0.005647 [[art:5ae28866:metrics.vintage_holdout.mean_predicted]] against 0.004817 [[art:e3590a16:metrics.vintage_holdout.event_rate]] on the vintage holdout.
Expressed as a relative gap, that comparison is 0.01152 [[art:e28c45a9:calibration.mean_rel_gap.train]] on train, 0.006755 [[art:59b8a1f5:calibration.mean_rel_gap.test]] on test, 0.05109 [[art:c599bd89:calibration.mean_rel_gap.out_of_time]] on the out-of-time split and 0.1722 [[art:55a672c2:calibration.mean_rel_gap.vintage_holdout]] on the vintage holdout.
Each of the four is below the declared tolerance on that relative gap, which is 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]], and the vintage holdout is the largest of the four while test is the smallest.
On the vintage holdout the model predicts above the realised rate, which is the direction a shallow slope and a negative intercept together would suggest.

The decile view of calibration on test is reproduced below.

<!-- quaestor:renderer:begin table calibration.test -->
Calibration by decile of predicted probability on test [[art:dcbc44e6:calibration.test]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.0004313 | 0.0006498 | 1539 |
| 2 | 0.0008926 | 0.0013 | 1539 |
| 3 | 0.001466 | 0.003251 | 1538 |
| 4 | 0.002302 | 0.002601 | 1538 |
| 5 | 0.003457 | 0.003251 | 1538 |
| 6 | 0.00511 | 0.005202 | 1538 |
| 7 | 0.007546 | 0.009103 | 1538 |
| 8 | 0.01122 | 0.008453 | 1538 |
| 9 | 0.01694 | 0.01235 | 1538 |
| 10 | 0.0318 | 0.03446 | 1538 |
<!-- quaestor:renderer:end -->

Back-testing of the aggregate prepayment speed gives a mean absolute difference between actual and predicted CPR of 0.02658 [[art:f2c3683c:cpr.train.mae]] on train, 0.04264 [[art:ff266c97:cpr.test.mae]] on test, 0.05857 [[art:a7ecd72b:cpr.out_of_time.mae]] on the out-of-time split and 0.0289 [[art:172ebed4:cpr.vintage_holdout.mae]] on the vintage holdout.
The out-of-time split carries the largest of those four and train the smallest.

<!-- quaestor:renderer:begin table cpr.test -->
Actual against predicted CPR by period on test [[art:ecbd1494:cpr.test]]:

| period | n | actual_cpr | predicted_cpr |
|---|---|---|---|
| 201402 | 15 | 0 | 0.03798 |
| 201403 | 28 | 0 | 0.03254 |
| 201404 | 56 | 0 | 0.02309 |
| 201405 | 68 | 0 | 0.02233 |
| 201406 | 80 | 0 | 0.02166 |
| 201407 | 97 | 0.1169 | 0.01797 |
| 201408 | 111 | 0 | 0.01554 |
| 201409 | 133 | 0.08659 | 0.01216 |
| 201410 | 145 | 0 | 0.01021 |
| 201411 | 161 | 0 | 0.008095 |
| 201412 | 175 | 0 | 0.007842 |
| 201501 | 198 | 0 | 0.007428 |
| 201502 | 198 | 0 | 0.007044 |
| 201503 | 198 | 0.05895 | 0.008695 |
| 201504 | 197 | 0 | 0.009549 |
| 201505 | 197 | 0 | 0.01325 |
| 201506 | 197 | 0 | 0.01494 |
| 201507 | 197 | 0 | 0.01945 |
| 201508 | 197 | 0 | 0.02688 |
| 201509 | 197 | 0.05924 | 0.02957 |
| 201510 | 196 | 0.05954 | 0.03698 |
| 201511 | 195 | 0 | 0.04786 |
| 201512 | 195 | 0 | 0.04992 |
| 201601 | 195 | 0.1698 | 0.07173 |
| 201602 | 192 | 0.06074 | 0.1054 |
| 201603 | 191 | 0.1187 | 0.1396 |
| 201604 | 189 | 0.1198 | 0.1539 |
| 201605 | 187 | 0.3673 | 0.2084 |
| 201606 | 180 | 0.1255 | 0.2036 |
| 201607 | 178 | 0.1268 | 0.2127 |
| 201608 | 176 | 0.06609 | 0.1941 |
| 201609 | 175 | 0.1288 | 0.1538 |
| 201610 | 173 | 0.1893 | 0.1126 |
| 201611 | 170 | 0.06835 | 0.09407 |
| 201612 | 169 | 0.06874 | 0.06776 |
| 201701 | 168 | 0.1339 | 0.0556 |
| 201702 | 176 | 0.2924 | 0.04679 |
| 201703 | 191 | 0.06105 | 0.04026 |
| 201704 | 199 | 0 | 0.03496 |
| 201705 | 218 | 0.05368 | 0.03454 |
| 201706 | 238 | 0.04927 | 0.03104 |
| 201707 | 248 | 0 | 0.02665 |
| 201708 | 274 | 0 | 0.02081 |
| 201709 | 284 | 0.08131 | 0.02157 |
| 201710 | 300 | 0 | 0.01654 |
| 201711 | 323 | 0.03653 | 0.01645 |
| 201712 | 334 | 0.03534 | 0.0209 |
| 201801 | 354 | 0.03338 | 0.02414 |
| 201802 | 353 | 0.06591 | 0.03339 |
| 201803 | 351 | 0.03366 | 0.05241 |
| 201804 | 350 | 0.06646 | 0.0823 |
| 201805 | 348 | 0.1594 | 0.1256 |
| 201806 | 343 | 0.1616 | 0.1493 |
| 201807 | 338 | 0.1638 | 0.161 |
| 201808 | 333 | 0.06974 | 0.1733 |
| 201809 | 331 | 0.2544 | 0.1831 |
| 201810 | 323 | 0.1707 | 0.177 |
| 201811 | 318 | 0.07292 | 0.1609 |
| 201812 | 316 | 0.1742 | 0.1816 |
| 201901 | 311 | 0.1098 | 0.1932 |
| 201902 | 300 | 0.1488 | 0.2297 |
| 201903 | 285 | 0.2253 | 0.2456 |
| 201904 | 258 | 0.246 | 0.2356 |
| 201905 | 243 | 0.1385 | 0.2078 |
| 201906 | 233 | 0.2688 | 0.169 |
| 201907 | 219 | 0.1984 | 0.1198 |
| 201908 | 206 | 0 | 0.08499 |
| 201909 | 191 | 0.06105 | 0.05731 |
| 201910 | 182 | 0.06398 | 0.04077 |
| 201911 | 171 | 0.06796 | 0.03594 |
| 201912 | 166 | 0 | 0.03505 |
<!-- quaestor:renderer:end -->

### Discrimination

| Metric | train | test | out_of_time | vintage_holdout |
| --- | --- | --- | --- | --- |
| AUC | 0.7883 [[art:fa609ae1:metrics.train.auc]] | 0.7753 [[art:57066271:metrics.test.auc]] | 0.7846 [[art:6f2a2d99:metrics.out_of_time.auc]] | 0.7718 [[art:ac6794c5:metrics.vintage_holdout.auc]] |
| Gini | 0.5767 [[art:0b6b2058:metrics.train.gini]] | 0.5505 [[art:fe7f75d7:metrics.test.gini]] | 0.5691 [[art:890252d7:metrics.out_of_time.gini]] | 0.5436 [[art:a4a532f0:metrics.vintage_holdout.gini]] |
| KS | 0.4562 [[art:c355478b:metrics.train.ks]] | 0.4162 [[art:c569c301:metrics.test.ks]] | 0.4321 [[art:16d3e4fe:metrics.out_of_time.ks]] | 0.4516 [[art:b5b9e888:metrics.vintage_holdout.ks]] |
| Brier | 0.008317 [[art:83666c70:metrics.train.brier]] | 0.007894 [[art:7d3583cd:metrics.test.brier]] | 0.01713 [[art:40d244d4:metrics.out_of_time.brier]] | 0.004763 [[art:f3c6bdcc:metrics.vintage_holdout.brier]] |
| Log loss | 0.04408 [[art:199c7db5:metrics.train.logloss]] | 0.04263 [[art:320e4c6b:metrics.test.logloss]] | 0.07975 [[art:2b7c9b2d:metrics.out_of_time.logloss]] | 0.02811 [[art:c32e3713:metrics.vintage_holdout.logloss]] |
| Share of events in the top two deciles | 0.5961 [[art:e8dd0c53:deciles.train.top2_capture]] | 0.5806 [[art:43c4adc5:deciles.test.top2_capture]] | 0.5773 [[art:df63152b:deciles.out_of_time.top2_capture]] | 0.5871 [[art:8b59f312:deciles.vintage_holdout.top2_capture]] |
| Rows | 36013 [[art:6fdfeabb:metrics.train.n]] | 15382 [[art:e55953e1:metrics.test.n]] | 12257 [[art:7898809e:metrics.out_of_time.n]] | 32177 [[art:37a92951:metrics.vintage_holdout.n]] |

AUC on train, at 0.7883 [[art:fa609ae1:metrics.train.auc]], stands above AUC on test, at 0.7753 [[art:57066271:metrics.test.auc]], and the two differ by less than the declared bound on the train-to-test AUC gap, which is 0.08 [[art:630f28f4:threshold.O1.auc_gap]].
The ordering evidence is therefore stable between the estimation sample and the held-out sample at the split level, and the weaker readings are the calibration ones on the vintage holdout described above.

<!-- quaestor:renderer:begin table deciles.test -->
Decile separation on test; decile 1 holds the highest probabilities [[art:309fa6f3:deciles.test]]:

| decile | count | events | event_rate | lift |
|---|---|---|---|---|
| 1 | 1539 | 53 | 0.03444 | 4.272 |
| 2 | 1539 | 19 | 0.01235 | 1.531 |
| 3 | 1538 | 13 | 0.008453 | 1.049 |
| 4 | 1538 | 14 | 0.009103 | 1.129 |
| 5 | 1538 | 8 | 0.005202 | 0.6452 |
| 6 | 1538 | 5 | 0.003251 | 0.4033 |
| 7 | 1538 | 4 | 0.002601 | 0.3226 |
| 8 | 1538 | 5 | 0.003251 | 0.4033 |
| 9 | 1538 | 2 | 0.0013 | 0.1613 |
| 10 | 1538 | 1 | 0.0006502 | 0.08066 |
<!-- quaestor:renderer:end -->

### Declared thresholds

<!-- quaestor:renderer:begin table thresholds.evaluation -->
Every threshold package.yaml declares, with its bound, the recomputed value and the outcome [[art:f71ddec9:thresholds.evaluation]]:

| metric | split | bound | value | result |
|---|---|---|---|---|
| auc | test | minimum 0.65 | 0.7753 | pass |
| calibration_slope | test | minimum 0.8 | 0.9365 | pass |
| calibration_slope | test | maximum 1.2 | 0.9365 | pass |
| psi |  | maximum 0.25 | 0.06189 | pass |
<!-- quaestor:renderer:end -->

The table above is the tool's own evaluation of each bound package.yaml declares, pairing the metric and split with the recomputed value and the resulting outcome, so it states the threshold position of this run rather than restating it in prose.
It covers the declared bounds on AUC, on the calibration slope and on the population stability index.

### Follow-up analyses

The planning loop ran two further metric computations, each on one half of the incentive distribution, and both are reported here.

The first recomputed every metric on the slice `incentive > median(incentive)` of each split.
It was asked because a non-monotone shock curve would be expected to originate in the in-the-money half, where a rate shift moves refinance incentive most, so fit and CPR calibration there test whether the shock behaviour reflects a hazard mis-fit rather than a projection artefact.

<!-- quaestor:renderer:begin table metrics.train.sub.incentive_high -->
Every metric on the incentive above_median slice of train [[art:58071691:metrics.train.sub.incentive_high]]:

| metric | value |
|---|---|
| n | 18006 |
| event_rate | 0.01433 |
| auc | 0.7182 |
| gini | 0.4364 |
| ks | 0.3337 |
| brier | 0.01393 |
| logloss | 0.07032 |
| mean_predicted | 0.01412 |
| mean_rel_gap | 0.01445 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.incentive_high -->
Every metric on the incentive above_median slice of test [[art:142c806c:metrics.test.sub.incentive_high]]:

| metric | value |
|---|---|
| n | 7691 |
| event_rate | 0.01313 |
| auc | 0.7269 |
| gini | 0.4537 |
| ks | 0.37 |
| brier | 0.01281 |
| logloss | 0.06538 |
| mean_predicted | 0.01359 |
| mean_rel_gap | 0.03492 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.out_of_time.sub.incentive_high -->
Every metric on the incentive above_median slice of out_of_time [[art:6c7182e4:metrics.out_of_time.sub.incentive_high]]:

| metric | value |
|---|---|
| n | 6127 |
| event_rate | 0.02824 |
| auc | 0.7472 |
| gini | 0.4944 |
| ks | 0.3876 |
| brier | 0.0267 |
| logloss | 0.1176 |
| mean_predicted | 0.03172 |
| mean_rel_gap | 0.1235 |
| share | 0.4999 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.vintage_holdout.sub.incentive_high -->
Every metric on the incentive above_median slice of vintage_holdout [[art:672368b3:metrics.vintage_holdout.sub.incentive_high]]:

| metric | value |
|---|---|
| n | 16088 |
| event_rate | 0.007397 |
| auc | 0.753 |
| gini | 0.5061 |
| ks | 0.3841 |
| brier | 0.007298 |
| logloss | 0.04077 |
| mean_predicted | 0.009598 |
| mean_rel_gap | 0.2976 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

On train this slice's AUC falls 0.07016 [[art:8d8827f2:metrics.train.sub.incentive_high.auc_gap]] below the split's own, within the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] at which a sub-population would become an open item.
On test the shortfall is 0.0484 [[art:5a0ba9c4:metrics.test.sub.incentive_high.auc_gap]], on the out-of-time split 0.03734 [[art:1c0207f9:metrics.out_of_time.sub.incentive_high.auc_gap]] and on the vintage holdout 0.01875 [[art:2ebd6757:metrics.vintage_holdout.sub.incentive_high.auc_gap]], each of them within that same bound.
The slice holds 0.5 [[art:277218fb:metrics.train.sub.incentive_high.share]] of train, 0.5 [[art:549aa934:metrics.test.sub.incentive_high.share]] of test, 0.4999 [[art:431d1ff2:metrics.out_of_time.sub.incentive_high.share]] of the out-of-time split and 0.5 [[art:cb627056:metrics.vintage_holdout.sub.incentive_high.share]] of the vintage holdout, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] a sub-population must clear and below the ceiling of 0.95 [[art:a928a05c:threshold.O1.slice_max_share]] at which it would be refused as the whole split.
Mean predicted against observed on the slice, relative, is 0.01445 [[art:7d3d3639:metrics.train.sub.incentive_high.mean_rel_gap]] on train, 0.03492 [[art:f90b2790:metrics.test.sub.incentive_high.mean_rel_gap]] on test and 0.1235 [[art:f0899b32:metrics.out_of_time.sub.incentive_high.mean_rel_gap]] on the out-of-time split, all below the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
On the vintage holdout the same quantity is 0.2976 [[art:d14397a7:metrics.vintage_holdout.sub.incentive_high.mean_rel_gap]], above that tolerance, with mean predicted at 0.009598 [[art:192eb7d4:metrics.vintage_holdout.sub.incentive_high.mean_predicted]] against an observed rate of 0.007397 [[art:947de0ec:metrics.vintage_holdout.sub.incentive_high.event_rate]].
Since the ordering shortfall on that split stays within its bound while the relative mean gap exceeds its tolerance, the weakness in the in-the-money half of the vintage holdout is in the level of the probabilities rather than in their ordering.

The second recomputed every metric on the complementary slice `incentive <= median(incentive)`, to see whether the non-monotone shock curve coincides with degraded fit and CPR in the low-incentive rows that the down-shocks move.

<!-- quaestor:renderer:begin table metrics.train.sub.incentive_low -->
Every metric on the incentive below_median slice of train [[art:9c590135:metrics.train.sub.incentive_low]]:

| metric | value |
|---|---|
| n | 18007 |
| event_rate | 0.002721 |
| auc | 0.7213 |
| gini | 0.4426 |
| ks | 0.3665 |
| brier | 0.002705 |
| logloss | 0.01785 |
| mean_predicted | 0.002732 |
| mean_rel_gap | 0.003953 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.incentive_low -->
Every metric on the incentive below_median slice of test [[art:53406e16:metrics.test.sub.incentive_low]]:

| metric | value |
|---|---|
| n | 7691 |
| event_rate | 0.002991 |
| auc | 0.6824 |
| gini | 0.3649 |
| ks | 0.3145 |
| brier | 0.00298 |
| logloss | 0.01989 |
| mean_predicted | 0.002641 |
| mean_rel_gap | 0.1169 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.out_of_time.sub.incentive_low -->
Every metric on the incentive below_median slice of out_of_time [[art:1ebd5e5e:metrics.out_of_time.sub.incentive_low]]:

| metric | value |
|---|---|
| n | 6130 |
| event_rate | 0.007667 |
| auc | 0.7683 |
| gini | 0.5365 |
| ks | 0.4679 |
| brier | 0.007557 |
| logloss | 0.04189 |
| mean_predicted | 0.006015 |
| mean_rel_gap | 0.2155 |
| share | 0.5001 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.vintage_holdout.sub.incentive_low -->
Every metric on the incentive below_median slice of vintage_holdout [[art:10caac80:metrics.vintage_holdout.sub.incentive_low]]:

| metric | value |
|---|---|
| n | 16089 |
| event_rate | 0.002238 |
| auc | 0.6724 |
| gini | 0.3447 |
| ks | 0.3456 |
| brier | 0.002229 |
| logloss | 0.01545 |
| mean_predicted | 0.001696 |
| mean_rel_gap | 0.2422 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

On train this slice's AUC falls 0.06703 [[art:134d7c07:metrics.train.sub.incentive_low.auc_gap]] below the split's own and on the out-of-time split 0.0163 [[art:faa1a185:metrics.out_of_time.sub.incentive_low.auc_gap]], both within the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].
On test the shortfall is 0.09283 [[art:a0523ad8:metrics.test.sub.incentive_low.auc_gap]] and on the vintage holdout 0.09945 [[art:9de83338:metrics.vintage_holdout.sub.incentive_low.auc_gap]], both above that bound, and each is carried to the open items as a question for the model developer as well as being reported here.
The slice holds 0.5 [[art:d7af12f0:metrics.train.sub.incentive_low.share]] of train, 0.5 [[art:1d5dd4c2:metrics.test.sub.incentive_low.share]] of test, 0.5001 [[art:c7aaafd2:metrics.out_of_time.sub.incentive_low.share]] of the out-of-time split and 0.5 [[art:d94e6531:metrics.vintage_holdout.sub.incentive_low.share]] of the vintage holdout, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] and below the ceiling of 0.95 [[art:a928a05c:threshold.O1.slice_max_share]].
Mean predicted against observed on the slice, relative, is 0.003953 [[art:05adce6c:metrics.train.sub.incentive_low.mean_rel_gap]] on train, 0.1169 [[art:aede705c:metrics.test.sub.incentive_low.mean_rel_gap]] on test, 0.2155 [[art:81d9f6b7:metrics.out_of_time.sub.incentive_low.mean_rel_gap]] on the out-of-time split and 0.2422 [[art:20691619:metrics.vintage_holdout.sub.incentive_low.mean_rel_gap]] on the vintage holdout, each below the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
On test and on the vintage holdout, therefore, the level of the probabilities in the out-of-the-money half stays inside tolerance while the ordering shortfall is the quantity that breaches its bound, so the weakness there is in the ordering rather than in the level.
Comparing the two halves of the incentive distribution by which relative mean gap is the larger, and not by the difference or the ratio between them, the above-median half carries the larger relative gap on the vintage holdout while the below-median half carries the larger relative gap on test and on the out-of-time split.
Comparing the same two halves by which AUC shortfall is the larger, again by direction only, the below-median half carries the larger shortfall on test and on the vintage holdout while the above-median half carries the larger shortfall on train and on the out-of-time split.

## 5. Sensitivity and scenario analysis

Sensitivity analysis and stress testing across a wide range of inputs, including extreme values, are how a validation establishes the boundaries of a model's performance and identifies the conditions under which it becomes unstable or inaccurate [[reg:SR11-7:V.1.a]].

The subject is a hazard model estimated with a declared rate-regime column, so the multicollinearity diagnostics, the regime-stability checks and the rate-shock scenarios all apply to it; each is reported below rather than deferred to Appendix D as inapplicable to this model type.

### Multicollinearity among the retained features

The largest variance inflation factor among the retained features is 4.976 [[art:f9e0db60:vif.max]], below the declared bound of 10 [[art:aeb4f33c:threshold.M1.vif]].

That largest value is carried by the note rate at 4.976 [[art:37532fa8:vif.note_rate]], with burnout next at 3.439 [[art:88879cb2:vif.burnout]] and loan age at 2.929 [[art:5573d536:vif.loan_age]].

The remaining retained features sit further from the bound: the refinancing incentive at 2.226 [[art:2da1b19c:vif.incentive]], the spread at origination at 1.713 [[art:a6c55fce:vif.sato]], the seasonal cosine at 1.018 [[art:a9cfa7eb:vif.season_cos]], the credit score at 1.008 [[art:f05d536a:vif.credit_score]], the log original balance at 1.006 [[art:24f8e4d1:vif.orig_upb_log]], the original loan-to-value at 1.005 [[art:65b35f3b:vif.orig_ltv]] and the seasonal sine at 1.004 [[art:669c5fcb:vif.season_sin]].

Belsley's condition number of the column-standardised design is 4.943 [[art:4f06a3c5:condition_number]], below the declared bound of 30 [[art:7e52fd7a:threshold.M1.condition_number]].

Neither the feature-level reading nor the design-level reading crosses the bound it was read against, so the retained design gives no indication that coefficient estimates are being destabilised by collinearity.

### Stability across the declared regimes

<!-- quaestor:renderer:begin table stability.auc_by_regime -->
The champion's AUC within each rate_regime on train [[art:960f708f:stability.auc_by_regime]]:

| regime | n | event_rate | auc |
|---|---|---|---|
| falling | 17873 | 0.01438 | 0.7227 |
| rising | 18140 | 0.002756 | 0.7238 |
<!-- quaestor:renderer:end -->

The within-regime discrimination shown above is read against a declared bound of 0.1 [[art:b64213d7:threshold.R1.auc_gap]] on the AUC difference across regimes.

A coefficient sign flip is counted only where an influential feature changes sign across regimes with a coefficient magnitude above 0.05 [[art:aca84377:threshold.R1.sign_flip_coef]] and an absolute z of at least 2 [[art:2e4428c7:threshold.R1.sign_flip_z]] in each regime.

On that joint criterion the flip indicator reads 0 for the refinancing incentive [[art:0cc7a37d:stability.incentive.sign_flip]], 0 for the note rate [[art:e7ce4912:stability.note_rate.sign_flip]], 0 for the spread at origination [[art:1f302ccd:stability.sato.sign_flip]], 0 for loan age [[art:b7191217:stability.loan_age.sign_flip]], 0 for burnout [[art:6bc05e82:stability.burnout.sign_flip]], 0 for the credit score [[art:d956c276:stability.credit_score.sign_flip]], 0 for the original loan-to-value [[art:054d5fab:stability.orig_ltv.sign_flip]], 0 for the log original balance [[art:fb1ae6c8:stability.orig_upb_log.sign_flip]], 0 for the seasonal cosine [[art:1850e2de:stability.season_cos.sign_flip]] and 0 for the seasonal sine [[art:6ba36a3b:stability.season_sin.sign_flip]].

No retained feature reverses the direction of its effect across the declared regimes under that criterion.

### Rate-shock scenarios

<!-- quaestor:renderer:begin table scenario.value_by_shock -->
Servicing value, its change from the base case and first-year CPR, by shock [[art:89c9bef7:scenario.value_by_shock]]:

| shock_bp | value | value_change | cpr |
|---|---|---|---|
| -300 | 1.765e+06 | 168100 | 0.0005476 |
| -200 | 742500 | -854300 | 0.2519 |
| -100 | 1.274e+06 | -322600 | 0.07951 |
| 0 | 1.597e+06 | 0 | 0.02322 |
| 100 | 1.716e+06 | 119600 | 0.006683 |
| 200 | 1.754e+06 | 157000 | 0.001915 |
| 300 | 1.765e+06 | 168100 | 0.0005476 |
<!-- quaestor:renderer:end -->

At the downward extreme the change in servicing value is 168100 [[art:e1211d5d:scenario.value_change.-300]], and at the upward extreme it is 168100 [[art:38e75872:scenario.value_change.300]], the same value at both ends of the shock grid.

Between those ends the profile reverses direction on the downward side: the change is -854300 [[art:03816874:scenario.value_change.-200]] at the deeper of the two intermediate downward shocks and -322600 [[art:d33e8e3c:scenario.value_change.-100]] at the shallower one, both below the base case of 0 [[art:1e1b0b88:scenario.value_change.0]] and both below the change recorded at the downward extreme.

On the upward side the changes rise steadily, from 119600 [[art:d0970bd9:scenario.value_change.100]] at the shallowest upward shock to 157000 [[art:d69c2be1:scenario.value_change.200]] at the intermediate one and to 168100 [[art:38e75872:scenario.value_change.300]] at the upward extreme.

The projected value is therefore not monotone in the rate shock, a shape that a parallel shift of a single rate path cannot produce, and this is raised as finding X1 at suggested high severity.

The realised convexity is 336100 [[art:6d2d7838:scenario.convexity]], which is positive, whereas the package declares the direction to be negative; that sign disagreement is the second limb of the same finding.

Because the non-monotonicity and the sign disagreement both bear on the shock grid rather than on the fitted design, they do not disturb the collinearity and regime-stability evidence above, but they do argue for limited reliance on shock-based valuation outputs until the scenario engine is investigated.

## 6. Findings and recommendations

Findings are ordered by severity, highest first, and each carries the recomputed values and scenario artifacts it rests on, in keeping with validation that identifies model limitations and errors and clarifies whether corrective actions may be warranted [[reg:SR26-2:V]].

### F-001 · X1 scenario analysis · severity **high**

**The projected servicing value is not monotone in the parallel rate shock, and the realised convexity comes out positive where the package declares it negative.**

At the largest down-shock the projected value is 1765000 [[art:cbc0b707:run.projection#value_by_shock.-300]], above the 742500 [[art:cbc0b707:run.projection#value_by_shock.-200]] reached at the next down-shock and above the base-case 1597000 [[art:cbc0b707:run.projection#value_by_shock.0]], so the value curve turns back on itself inside the down-shocks.

<!-- quaestor:renderer:begin table scenario.value_by_shock -->
Servicing value, its change from the base case and first-year CPR, by shock [[art:89c9bef7:scenario.value_by_shock]]:

| shock_bp | value | value_change | cpr |
|---|---|---|---|
| -300 | 1.765e+06 | 168100 | 0.0005476 |
| -200 | 742500 | -854300 | 0.2519 |
| -100 | 1.274e+06 | -322600 | 0.07951 |
| 0 | 1.597e+06 | 0 | 0.02322 |
| 100 | 1.716e+06 | 119600 | 0.006683 |
| 200 | 1.754e+06 | 157000 | 0.001915 |
| 300 | 1.765e+06 | 168100 | 0.0005476 |
<!-- quaestor:renderer:end -->

The change from the base case at the largest down-shock is 168100 [[art:e1211d5d:scenario.value_change.-300]] and the change at the largest up-shock is 168100 [[art:38e75872:scenario.value_change.300]], identical in both sign and magnitude where a fall and a rise in rates should move servicing value in opposite directions.

First-year CPR at the largest down-shock is 0.0005476 [[art:cbc0b707:run.projection#cpr_by_shock.-300]] and first-year CPR at the largest up-shock is 0.0005476 [[art:cbc0b707:run.projection#cpr_by_shock.300]], the same prepayment response at opposite ends of the grid, while at the next down-shock CPR is 0.2519 [[art:cbc0b707:run.projection#cpr_by_shock.-200]].

The realised convexity, the change at the largest down-shock taken together with the change at the largest up-shock, is 336100 [[art:6d2d7838:scenario.convexity]] and is positive, the opposite of the negative convexity the package declares.

The validator concludes that the extreme down-shock grid point does not carry a distinct rate path through the projection but reproduces the extreme up-shock result, so the down-shock leg of the scenario grid does not represent the behaviour a parallel shift of a single rate path would produce and the declared convexity sign is contradicted by the run's own output.

The developer should trace how the shock grid is applied to the rate path in the projection code, repair the extreme down-shock path so that prepayment speeds and value respond to it as they do at the intermediate down-shocks, re-run the scenario set, and either restate the declared convexity sign in package.yaml or explain the economics that would justify the declared sign against the repaired output.

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1, S1), `compute_metrics` (T1, C1, O1), `check_leakage` (L1, L2), `check_stability` (R1), `check_collinearity` (M1), `challenger_compare` (E1).

### Open items

On the test split, AUC inside the segment `incentive <= median(incentive)` is 0.6824 [[art:0f9a3d96:metrics.test.sub.incentive_low.auc]] against 0.7753 [[art:57066271:metrics.test.auc]] over the whole split, a shortfall of 0.09283 [[art:a0523ad8:metrics.test.sub.incentive_low.auc_gap]] measured as a difference and read against the 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] gap bound on 0.5 [[art:1d5dd4c2:metrics.test.sub.incentive_low.share]] of the split, at or above the 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] share bound — selecting on the incentive variable also holds nearly constant everything correlated with it, so can the model developer show what the model still discriminates on inside that segment and which features carry the ranking there?

On the vintage_holdout split, AUC inside the segment `incentive <= median(incentive)` is 0.6724 [[art:0510c841:metrics.vintage_holdout.sub.incentive_low.auc]] against 0.7718 [[art:ac6794c5:metrics.vintage_holdout.auc]] over the whole split, a shortfall of 0.09945 [[art:9de83338:metrics.vintage_holdout.sub.incentive_low.auc_gap]] measured as a difference and read against the 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] gap bound on 0.5 [[art:d94e6531:metrics.vintage_holdout.sub.incentive_low.share]] of the split, at or above the 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] share bound — can the model developer say what ranking signal the model relies on in that segment out of sample, and whether it is the signal intended for borrowers with little incentive to refinance?

The fitted coefficient on `note_rate` carries sign -1 [[art:aecf7ccb:sign_check.note_rate.coef_sign]] where that feature's own univariate direction, the bound the sign was read against, is 1 [[art:61f6e1ac:sign_check.note_rate.univariate_direction]], with the agreement indicator at 0 [[art:a453463d:sign_check.note_rate.agrees]] — since conditioning on the other features also conditions on whatever they share with the note rate, can the model developer identify the correlated covariates that turn the fitted direction around and document why the conditional direction is the economically intended one?

## 7. Ongoing monitoring recommendations

Ongoing monitoring should evaluate the extent to which this model continues to perform as expected given changes in products, exposures, activities, clients, data relevance, or market conditions, with a frequency and scope set by the nature of the model and its materiality [[reg:SR26-2:V.2]].

### Ordering of the monitoring report

The monitoring report should present calibration evidence before discrimination evidence, which is the order this report used in its performance section, because package.yaml declares that this model's output is used as a probability and not only as a ranking.

A score that is consumed as a level, not as a rank, can hold its ordering while its level drifts, so a report that leads with rank-ordering can leave that drift unreported for a full cycle.

### Quantities, frequency, and bound

The bounds below are the ones package.yaml already declares and this validation checked against; monitoring should hold to those artifacts rather than restate them as new limits.

- Recompute the largest population stability index across the scored inputs and the score itself for each production vintage against the development distribution, at the monthly production cycle, holding to the declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]]; at validation the largest train-to-test shift was 0.06189 [[art:c2e8c8fd:psi.max]], well below that ceiling, so the useful monitoring signal is the trend of this quantity toward the ceiling rather than the breach alone.
- Refit the logistic regression of the realized prepayment outcome on the logit of the predicted probability for each completed performance window and report the slope against the declared band of 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] to 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]], quarterly, once outcomes for the window have been observed; the validation value of 0.9365 [[art:3e42ee62:calibration_slope.test]] sits inside that band and closer to its lower edge than to its upper, so a monitoring series that drifts downward approaches the breach first.
- Recompute discrimination on the same realized outcomes quarterly against the declared floor of 0.65 [[art:fececac1:threshold.package.auc.test.min]]; the validation value was 0.7753 [[art:57066271:metrics.test.auc]], above that floor, and monitoring should report the level and the direction of movement in the same table each cycle so that deterioration is visible before the floor is reached.
- Report the input-shift quantity and both outcome quantities against the same two sub-populations the model is used on, giving for each cycle both the absolute gap between the sub-populations and the ratio of their values, and naming which comparison a conclusion of "alike" rests on, since two sub-populations whose absolute gaps match can differ materially in ratio.

Where any of these series falls persistently outside the declared bounds, the response is the one the guidance contemplates for outcomes that deviate from established thresholds: an overlay, an adjustment, a recalibration, or redevelopment, decided under the organization's model risk policy rather than by the monitoring report itself [[reg:SR26-2:V.1.b]].

### Benchmarking that monitoring adds

The champion was compared with a challenger in this validation, and that comparison is reported in the model-comparison section of this report, on the development sample.

What monitoring adds is the comparison that the development data cannot give: the challenger refitted on production vintages, so that the benchmark is estimated on the same loans, rate environment, and servicing behavior the champion is being scored against, rather than on the vintages that produced the champion.

A refitted challenger that pulls away from the champion on the production vintages should trigger investigation into the source and degree of the difference before it is read as evidence against the champion, since the benchmark is itself an alternative prediction and may differ because of its data or method [[reg:SR11-7:V.1.b]].

### What this validation could not cover

This validation observed the model on samples fixed at development time, so monitoring carries the burden of back-testing the model against outcomes realized after those samples, at an observation frequency matched to the prepayment performance window.

Monitoring, not this validation, is the place where production implementation is confirmed: that the input feeds remain accurate, complete, and consistent with the model's purpose, and that the deployed code matches the reviewed code under change control [[reg:SR11-7:V.1.b]].

Override behavior is outside what this validation could observe, and monitoring should record the rate of overrides, the reasons given, and whether overridden cases outperform the model, because a consistently improving override process indicates the model needs revision.

The model's behavior when inputs move outside the ranges represented in the development data, particularly rate environments not spanned by those vintages, is a limitation this validation could not resolve, and monitoring should flag the cycles in which those ranges are approached or exceeded.

The development-stage limitations recorded elsewhere in this report should be reassessed on the same cycle as the quantitative series above, so that they are revisited as conditions change rather than only at the next scheduled validation [[reg:SR26-2:V.2]].

## Appendix A — Claims

Grounding precision 0.9849 before repair (326 of 331 claims verified; 5 mismatch) and 1.0000 after 0 claim(s) rewritten and 5 number(s) removed from the prose. Per section (post-repair): summary 18/18; conceptual_soundness 70/70; data_integrity 79/79; outcomes 92/92; sensitivity 36/36; findings 24/24; monitoring 7/7.

Developer claims: The package declares 3 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). See Appendix D.

Excluded numeric tokens (not claims): section_number (Section 6); citation_hash (2ad8d1a5, 6fdfeabb, e55953e1, 7898809e); regulatory_section_id (SR26-2:V, SR26-2:V.1.a, SR26-2:IV.1, SR26-2:V.1.b); finding_id (F-001); package_version (1.0); extractor_returned_excluded_token (1.0, 001,, 6, 12.0).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The subject was re-run from its package definition and every… | 300 | ratio | runtime |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 2 | summary | The development split holds 36013 rows and the test split ho… | 36013 | count | n | train | eq | `[[art:6fdfeabb:metrics.train.n]]` | verified | 36013 |
| 3 | summary | The development split holds 36013 rows and the test split ho… | 15382 | count | n | test | eq | `[[art:e55953e1:metrics.test.n]]` | verified | 15382 |
| 4 | summary | The out-of-time split holds 12257 rows and the vintage holdo… | 12257 | count | n | out_of_time | eq | `[[art:7898809e:metrics.out_of_time.n]]` | verified | 12257 |
| 5 | summary | The out-of-time split holds 12257 rows and the vintage holdo… | 32177 | count | n | vintage_holdout | eq | `[[art:37a92951:metrics.vintage_holdout.n]]` | verified | 32177 |
| 6 | summary | Discrimination on test, at 0.7753 , sits above the developer… | 0.7753 | ratio | auc | test | eq | `[[art:57066271:metrics.test.auc]]` | verified | 0.7752553922 |
| 7 | summary | Discrimination on test, at 0.7753 , sits above the developer… | 0.65 | ratio | auc | test | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 8 | summary | The calibration slope on test, at 0.9365 , lies inside the d… | 0.9365 | ratio | calibration_slope | test | eq | `[[art:3e42ee62:calibration_slope.test]]` | verified | 0.9365180494 |
| 9 | summary | The calibration slope on test, at 0.9365 , lies inside the d… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 10 | summary | The calibration slope on test, at 0.9365 , lies inside the d… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 11 | summary | The largest train-to-test population stability index, at 0.0… | 0.06189 | ratio | psi |  | eq | `[[art:c2e8c8fd:psi.max]]` | verified | 0.06188985797 |
| 12 | summary | The largest train-to-test population stability index, at 0.0… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 13 | summary | Discrimination is of a similar order on the later splits, at… | 0.7846 | ratio | auc | out_of_time | eq | `[[art:6f2a2d99:metrics.out_of_time.auc]]` | verified | 0.7845616168 |
| 14 | summary | Discrimination is of a similar order on the later splits, at… | 0.7718 | ratio | auc | vintage_holdout | eq | `[[art:ac6794c5:metrics.vintage_holdout.auc]]` | verified | 0.7717974135 |
| 15 | summary | The recomputed calibration slopes are 0.9937 on train, 0.936… | 0.9937 | ratio | calibration_slope | train | eq | `[[art:534cb102:calibration_slope.train]]` | verified | 0.9936945557 |
| 16 | summary | The recomputed calibration slopes are 0.9937 on train, 0.936… | 0.9365 | ratio | calibration_slope | test | eq | `[[art:3e42ee62:calibration_slope.test]]` | verified | 0.9365180494 |
| 17 | summary | The recomputed calibration slopes are 0.9937 on train, 0.936… | 0.9969 | ratio | calibration_slope | out_of_time | eq | `[[art:a49b2789:calibration_slope.out_of_time]]` | verified | 0.9969389246 |
| 18 | summary | The recomputed calibration slopes are 0.9937 on train, 0.936… | 0.8373 | ratio | calibration_slope | vintage_holdout | eq | `[[art:08d6b321:calibration_slope.vintage_holdout]]` | verified | 0.837279841 |
| 19 | conceptual_soundness | The champion is a parametric regression scoring a binary pre… | -5.502 | ratio | intercept |  | eq | `[[art:b764932a:run.model_summary#intercept]]` | verified | -5.502203635 |
| 20 | conceptual_soundness | The champion is a parametric regression scoring a binary pre… | 36013 | count | n_train | train | eq | `[[art:b764932a:run.model_summary#n_train]]` | verified | 36013 |
| 21 | conceptual_soundness | The champion is a parametric regression scoring a binary pre… | 934 | count | n_train_loans | train | eq | `[[art:b764932a:run.model_summary#n_train_loans]]` | verified | 934 |
| 22 | conceptual_soundness | The feature inventory holds 12 features. | 12 | count | n |  | eq | `[[art:61276a96:run.features#n]]` | verified | 12 |
| 23 | conceptual_soundness | Of these, 5 are fixed at origination and 7 are known before… | 5 | count | at_origination |  | eq | `[[art:61276a96:run.features#at_origination]]` | verified | 5 |
| 24 | conceptual_soundness | Of these, 5 are fixed at origination and 7 are known before… | 7 | count | before_period_start |  | eq | `[[art:61276a96:run.features#before_period_start]]` | verified | 7 |
| 25 | conceptual_soundness | No feature is observed during the period, at 0 , and none is… | 0 | count | during_period |  | eq | `[[art:61276a96:run.features#during_period]]` | verified | 0 |
| 26 | conceptual_soundness | No feature is observed during the period, at 0 , and none is… | 0 | count | after_outcome |  | eq | `[[art:61276a96:run.features#after_outcome]]` | verified | 0 |
| 27 | conceptual_soundness | The developer's own screen removed terms on collinearity gro… | 10 | ratio | vif_threshold |  | eq | `[[art:b764932a:run.model_summary#vif_threshold]]` | verified | 10 |
| 28 | conceptual_soundness | The twelve-month rate change was dropped at a variance infla… | 12.38 | ratio | vif |  | eq | `[[art:b764932a:run.model_summary#removed.rate_change_12m.vif]]` | verified | 12.377209 |
| 29 | conceptual_soundness | The log beginning-of-month balance was dropped at 40090 , fa… | 40090 | ratio | vif |  | eq | `[[art:b764932a:run.model_summary#removed.bom_balance_log.vif]]` | verified | 40090.39108 |
| 30 | conceptual_soundness | The largest coefficient in the fitted model is on the refina… | 1.253 | ratio | coefficient |  | eq | `[[art:b764932a:run.model_summary#coefficients.incentive.value]]` | verified | 1.253400948 |
| 31 | conceptual_soundness | The loan age spline terms take values 0.6491 , 0.04548 , -0.… | 0.6491 | ratio | coefficient |  | eq | `[[art:b764932a:run.model_summary#coefficients.loan_age_spline_1.value]]` | verified | 0.6491385114 |
| 32 | conceptual_soundness | The loan age spline terms take values 0.6491 , 0.04548 , -0.… | 0.04548 | ratio | coefficient |  | eq | `[[art:b764932a:run.model_summary#coefficients.loan_age_spline_2.value]]` | verified | 0.04547611044 |
| 33 | conceptual_soundness | The loan age spline terms take values 0.6491 , 0.04548 , -0.… | -0.09539 | ratio | coefficient |  | eq | `[[art:b764932a:run.model_summary#coefficients.loan_age_spline_3.value]]` | verified | -0.09538696407 |
| 34 | conceptual_soundness | The loan age spline terms take values 0.6491 , 0.04548 , -0.… | -0.2386 | ratio | coefficient |  | eq | `[[art:b764932a:run.model_summary#coefficients.loan_age_spline_4.value]]` | verified | -0.2385660288 |
| 35 | conceptual_soundness | Credit score enters positive at 0.4074 , consistent with str… | 0.4074 | ratio | coefficient |  | eq | `[[art:b764932a:run.model_summary#coefficients.credit_score.value]]` | verified | 0.4073637042 |
| 36 | conceptual_soundness | The log origination balance enters positive at 0.3036 , cons… | 0.3036 | ratio | coefficient |  | eq | `[[art:b764932a:run.model_summary#coefficients.orig_upb_log.value]]` | verified | 0.3036365647 |
| 37 | conceptual_soundness | Original loan-to-value enters negative at -0.243 , consisten… | -0.243 | ratio | coefficient |  | eq | `[[art:b764932a:run.model_summary#coefficients.orig_ltv.value]]` | verified | -0.2430424725 |
| 38 | conceptual_soundness | The spread at origination enters positive at 0.01282 , small… | 0.01282 | ratio | coefficient |  | eq | `[[art:b764932a:run.model_summary#coefficients.sato.value]]` | verified | 0.01281978784 |
| 39 | conceptual_soundness | The seasonality terms take 0.0702 and -0.1239 , a mild annua… | 0.0702 | ratio | coefficient |  | eq | `[[art:b764932a:run.model_summary#coefficients.season_sin.value]]` | verified | 0.07019923172 |
| 40 | conceptual_soundness | The seasonality terms take 0.0702 and -0.1239 , a mild annua… | -0.1239 | ratio | coefficient |  | eq | `[[art:b764932a:run.model_summary#coefficients.season_cos.value]]` | verified | -0.1238708376 |
| 41 | conceptual_soundness | Burnout enters positive at 0.07952 , which runs against the… | 0.07952 | ratio | coefficient |  | eq | `[[art:b764932a:run.model_summary#coefficients.burnout.value]]` | verified | 0.07951968723 |
| 42 | conceptual_soundness | Burnout enters positive at 0.07952 , which runs against the… | 1 | ratio | univariate_direction |  | eq | `[[art:bfc96bb2:sign_check.burnout.univariate_direction]]` | verified | 1 |
| 43 | conceptual_soundness | Burnout enters positive at 0.07952 , which runs against the… | 1 | ratio | coef_sign |  | eq | `[[art:a3063608:sign_check.burnout.coef_sign]]` | verified | 1 |
| 44 | conceptual_soundness | The note rate enters negative at -0.4457 , where a higher no… | -0.4457 | ratio | coefficient |  | eq | `[[art:b764932a:run.model_summary#coefficients.note_rate.value]]` | verified | -0.4457241706 |
| 45 | conceptual_soundness | Across the retained features checked, the fitted sign contra… | 1 | count | n_disagreements |  | eq | `[[art:f96ece96:sign_check.n_disagreements]]` | verified | 1 |
| 46 | conceptual_soundness | Its fitted coefficient carries sign -1 while its single-feat… | -1 | ratio | coef_sign |  | eq | `[[art:aecf7ccb:sign_check.note_rate.coef_sign]]` | verified | -1 |
| 47 | conceptual_soundness | Its fitted coefficient carries sign -1 while its single-feat… | 1 | ratio | univariate_direction | train | eq | `[[art:61f6e1ac:sign_check.note_rate.univariate_direction]]` | verified | 1 |
| 48 | conceptual_soundness | Its fitted coefficient carries sign -1 while its single-feat… | 0 | ratio | agrees |  | eq | `[[art:a453463d:sign_check.note_rate.agrees]]` | verified | 0 |
| 49 | conceptual_soundness | Refitting the champion's form without the note rate changes… | -0.002585 | ratio | delta_auc | test | eq | `[[art:14558b82:ablation.note_rate.delta_auc]]` | verified | -0.002585106068 |
| 50 | conceptual_soundness | Every other checked feature agrees: the refinance incentive… | 1 | ratio | agrees |  | eq | `[[art:f7b2338e:sign_check.incentive.agrees]]` | verified | 1 |
| 51 | conceptual_soundness | Every other checked feature agrees: the refinance incentive… | 1 | ratio | agrees |  | eq | `[[art:915bf8eb:sign_check.credit_score.agrees]]` | verified | 1 |
| 52 | conceptual_soundness | Every other checked feature agrees: the refinance incentive… | 1 | ratio | agrees |  | eq | `[[art:07a9d3e6:sign_check.orig_upb_log.agrees]]` | verified | 1 |
| 53 | conceptual_soundness | Every other checked feature agrees: the refinance incentive… | 1 | ratio | agrees |  | eq | `[[art:7021aeb0:sign_check.orig_ltv.agrees]]` | verified | 1 |
| 54 | conceptual_soundness | Every other checked feature agrees: the refinance incentive… | 1 | ratio | agrees |  | eq | `[[art:2401eba2:sign_check.sato.agrees]]` | verified | 1 |
| 55 | conceptual_soundness | Every other checked feature agrees: the refinance incentive… | 1 | ratio | agrees |  | eq | `[[art:2eec20ab:sign_check.burnout.agrees]]` | verified | 1 |
| 56 | conceptual_soundness | Every other checked feature agrees: the refinance incentive… | 1 | ratio | agrees |  | eq | `[[art:e110f357:sign_check.season_sin.agrees]]` | verified | 1 |
| 57 | conceptual_soundness | Every other checked feature agrees: the refinance incentive… | 1 | ratio | agrees |  | eq | `[[art:7f18ddf7:sign_check.season_cos.agrees]]` | verified | 1 |
| 58 | conceptual_soundness | The fitted and univariate signs match on the incentive at 1… | 1 | ratio | coef_sign |  | eq | `[[art:684cf11a:sign_check.incentive.coef_sign]]` | verified | 1 |
| 59 | conceptual_soundness | The fitted and univariate signs match on the incentive at 1… | 1 | ratio | univariate_direction |  | eq | `[[art:8098d951:sign_check.incentive.univariate_direction]]` | verified | 1 |
| 60 | conceptual_soundness | The fitted and univariate signs match on the incentive at 1… | 1 | ratio | coef_sign |  | eq | `[[art:1ec1078b:sign_check.credit_score.coef_sign]]` | verified | 1 |
| 61 | conceptual_soundness | The fitted and univariate signs match on the incentive at 1… | 1 | ratio | univariate_direction |  | eq | `[[art:42303896:sign_check.credit_score.univariate_direction]]` | verified | 1 |
| 62 | conceptual_soundness | The fitted and univariate signs match on the incentive at 1… | 1 | ratio | coef_sign |  | eq | `[[art:5aa309fc:sign_check.orig_upb_log.coef_sign]]` | verified | 1 |
| 63 | conceptual_soundness | The fitted and univariate signs match on the incentive at 1… | 1 | ratio | univariate_direction |  | eq | `[[art:b9743ecb:sign_check.orig_upb_log.univariate_direction]]` | verified | 1 |
| 64 | conceptual_soundness | The fitted and univariate signs match on the incentive at 1… | -1 | ratio | coef_sign |  | eq | `[[art:7eec65ec:sign_check.orig_ltv.coef_sign]]` | verified | -1 |
| 65 | conceptual_soundness | The fitted and univariate signs match on the incentive at 1… | -1 | ratio | univariate_direction |  | eq | `[[art:76dbc708:sign_check.orig_ltv.univariate_direction]]` | verified | -1 |
| 66 | conceptual_soundness | The fitted and univariate signs match on the incentive at 1… | 1 | ratio | coef_sign |  | eq | `[[art:c031d0d5:sign_check.sato.coef_sign]]` | verified | 1 |
| 67 | conceptual_soundness | The fitted and univariate signs match on the incentive at 1… | 1 | ratio | univariate_direction |  | eq | `[[art:c08233a6:sign_check.sato.univariate_direction]]` | verified | 1 |
| 68 | conceptual_soundness | The fitted and univariate signs match on the incentive at 1… | 1 | ratio | coef_sign |  | eq | `[[art:761188ce:sign_check.season_sin.coef_sign]]` | verified | 1 |
| 69 | conceptual_soundness | The fitted and univariate signs match on the incentive at 1… | 1 | ratio | univariate_direction |  | eq | `[[art:cae6b096:sign_check.season_sin.univariate_direction]]` | verified | 1 |
| 70 | conceptual_soundness | The fitted and univariate signs match on the incentive at 1… | -1 | ratio | coef_sign |  | eq | `[[art:7dbb1ffc:sign_check.season_cos.coef_sign]]` | verified | -1 |
| 71 | conceptual_soundness | The fitted and univariate signs match on the incentive at 1… | -1 | ratio | univariate_direction |  | eq | `[[art:03e931f0:sign_check.season_cos.univariate_direction]]` | verified | -1 |
| 72 | conceptual_soundness | Ablation refits the champion's form on the retained set and… | 0.7673 | ratio | baseline_auc | test | eq | `[[art:54367df6:ablation.baseline_auc]]` | verified | 0.7672992275 |
| 73 | conceptual_soundness | The refinance incentive carries the most discrimination, at… | -0.04117 | ratio | delta_auc | test | eq | `[[art:78108590:ablation.incentive.delta_auc]]` | verified | -0.0411745927 |
| 74 | conceptual_soundness | The log origination balance follows at -0.01927 and credit s… | -0.01927 | ratio | delta_auc | test | eq | `[[art:0ddb11a9:ablation.orig_upb_log.delta_auc]]` | verified | -0.01926646624 |
| 75 | conceptual_soundness | The log origination balance follows at -0.01927 and credit s… | -0.01474 | ratio | delta_auc | test | eq | `[[art:9bdeb0df:ablation.credit_score.delta_auc]]` | verified | -0.0147431913 |
| 76 | conceptual_soundness | Below those sit original loan-to-value at -0.002294 and the… | -0.002294 | ratio | delta_auc | test | eq | `[[art:57ea66c5:ablation.orig_ltv.delta_auc]]` | verified | -0.002294407165 |
| 77 | conceptual_soundness | Below those sit original loan-to-value at -0.002294 and the… | -0.002585 | ratio | delta_auc | test | eq | `[[art:14558b82:ablation.note_rate.delta_auc]]` | verified | -0.002585106068 |
| 78 | conceptual_soundness | Below those sit original loan-to-value at -0.002294 and the… | -0.0004826 | ratio | delta_auc | test | eq | `[[art:a288439d:ablation.season_cos.delta_auc]]` | verified | -0.00048256018 |
| 79 | conceptual_soundness | Below those sit original loan-to-value at -0.002294 and the… | -0.0003885 | ratio | delta_auc | test | eq | `[[art:e54c8581:ablation.season_sin.delta_auc]]` | verified | -0.0003884794439 |
| 80 | conceptual_soundness | Below those sit original loan-to-value at -0.002294 and the… | -0.0001876 | ratio | delta_auc | test | eq | `[[art:3cba039b:ablation.burnout.delta_auc]]` | verified | -0.0001876329287 |
| 81 | conceptual_soundness | Test AUC rises when loan age is dropped, at 0.0008166 , and… | 0.0008166 | ratio | delta_auc | test | eq | `[[art:be669163:ablation.loan_age.delta_auc]]` | verified | 0.0008165996474 |
| 82 | conceptual_soundness | Test AUC rises when loan age is dropped, at 0.0008166 , and… | 0.0005201 | ratio | delta_auc | test | eq | `[[art:57703504:ablation.sato.delta_auc]]` | verified | 0.0005200867657 |
| 83 | conceptual_soundness | The challenger reaches an AUC on test of 0.7337 against the… | 0.7337 | ratio | auc | test | eq | `[[art:705b66f0:challenger.auc]]` | verified | 0.7337079121 |
| 84 | conceptual_soundness | The challenger reaches an AUC on test of 0.7337 against the… | 0.7753 | ratio | auc | test | eq | `[[art:57066271:metrics.test.auc]]` | verified | 0.7752553922 |
| 85 | conceptual_soundness | The challenger's margin over the champion is -0.04155 , that… | -0.04155 | ratio | delta_auc | test | eq | `[[art:4d28c096:challenger.delta_auc]]` | verified | -0.04154748012 |
| 86 | conceptual_soundness | The declared threshold for the difference to matter is a cha… | 0.03 | ratio | delta_auc |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 87 | conceptual_soundness | The same ordering holds on calibration, where the champion's… | 0.007894 | ratio | brier | test | eq | `[[art:7d3583cd:metrics.test.brier]]` | verified | 0.00789356705 |
| 88 | conceptual_soundness | The same ordering holds on calibration, where the champion's… | 0.00863 | ratio | brier | test | eq | `[[art:85a89ef9:challenger.brier]]` | verified | 0.008629514666 |
| 89 | data_integrity | The evaluation splits hold 36013 rows for training, 15382 ro… | 36013 | count | profile.n | train | eq | `[[art:c5ebd9c9:profile.train.n]]` | verified | 36013 |
| 90 | data_integrity | The evaluation splits hold 36013 rows for training, 15382 ro… | 15382 | count | profile.n | test | eq | `[[art:e3abc1b8:profile.test.n]]` | verified | 15382 |
| 91 | data_integrity | The evaluation splits hold 36013 rows for training, 15382 ro… | 32177 | count | profile.n | vintage_holdout | eq | `[[art:426e712a:profile.vintage_holdout.n]]` | verified | 32177 |
| 92 | data_integrity | The evaluation splits hold 36013 rows for training, 15382 ro… | 12257 | count | profile.n | out_of_time | eq | `[[art:fa39c5cf:profile.out_of_time.n]]` | verified | 12257 |
| 93 | data_integrity | The largest missing fraction of any column is 0 in train, 0… | 0 | ratio | profile.missing.max | train | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 94 | data_integrity | The largest missing fraction of any column is 0 in train, 0… | 0 | ratio | profile.missing.max | test | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 95 | data_integrity | The largest missing fraction of any column is 0 in train, 0… | 0 | ratio | profile.missing.max | vintage_holdout | eq | `[[art:329bb430:profile.vintage_holdout.missing.max]]` | verified | 0 |
| 96 | data_integrity | The largest missing fraction of any column is 0 in train, 0… | 0 | ratio | profile.missing.max | out_of_time | eq | `[[art:4dafce11:profile.out_of_time.missing.max]]` | verified | 0 |
| 97 | data_integrity | Every one of those four values lies below the declared allow… | 0.1 | ratio | threshold.D1.missing_gap |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 98 | data_integrity | The declared bound on the population stability index is 0.25… | 0.25 | ratio | threshold.S1.psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 99 | data_integrity | The declared bound on the population stability index is 0.25… | 0.25 | ratio | threshold.package.psi.max |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 100 | data_integrity | Between train and test the largest population shift over the… | 0.06189 | ratio | psi.max |  | eq | `[[art:c2e8c8fd:psi.max]]` | verified | 0.06188985797 |
| 101 | data_integrity | Between train and test the largest population shift over the… | 0.06189 | ratio | psi.credit_score |  | eq | `[[art:7e87527c:psi.credit_score]]` | verified | 0.06188985797 |
| 102 | data_integrity | Between train and test the largest population shift over the… | 0.25 | ratio | threshold.S1.psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 103 | data_integrity | The remaining train-to-test shifts are smaller: orig_upb_log… | 0.04817 | ratio | psi.orig_upb_log |  | eq | `[[art:55030a3b:psi.orig_upb_log]]` | verified | 0.04817081196 |
| 104 | data_integrity | The remaining train-to-test shifts are smaller: orig_upb_log… | 0.03617 | ratio | psi.orig_ltv |  | eq | `[[art:cd1ff136:psi.orig_ltv]]` | verified | 0.03617297258 |
| 105 | data_integrity | The remaining train-to-test shifts are smaller: orig_upb_log… | 0.02773 | ratio | psi.sato |  | eq | `[[art:584da64f:psi.sato]]` | verified | 0.02772829856 |
| 106 | data_integrity | The remaining train-to-test shifts are smaller: orig_upb_log… | 0.01371 | ratio | psi.note_rate |  | eq | `[[art:ecc6adf3:psi.note_rate]]` | verified | 0.01370911382 |
| 107 | data_integrity | The remaining train-to-test shifts are smaller: orig_upb_log… | 0.004614 | ratio | psi.burnout |  | eq | `[[art:9dc7ecc2:psi.burnout]]` | verified | 0.004614338236 |
| 108 | data_integrity | The remaining train-to-test shifts are smaller: orig_upb_log… | 0.0009923 | ratio | psi.incentive |  | eq | `[[art:2da5570f:psi.incentive]]` | verified | 0.0009922551416 |
| 109 | data_integrity | The remaining train-to-test shifts are smaller: orig_upb_log… | 0.0001994 | ratio | psi.loan_age |  | eq | `[[art:2202b157:psi.loan_age]]` | verified | 0.0001993816816 |
| 110 | data_integrity | The remaining train-to-test shifts are smaller: orig_upb_log… | 1.79e-05 | ratio | psi.season_cos |  | eq | `[[art:addec503:psi.season_cos]]` | verified | 1.790085913e-05 |
| 111 | data_integrity | The remaining train-to-test shifts are smaller: orig_upb_log… | 2.939e-06 | ratio | psi.season_sin |  | eq | `[[art:4d2ed98d:psi.season_sin]]` | verified | 2.939045338e-06 |
| 112 | data_integrity | The model score itself shifts by 0.001953 between train and… | 0.001953 | ratio | psi.y_score |  | eq | `[[art:3b9dee2d:psi.y_score]]` | verified | 0.001952903716 |
| 113 | data_integrity | The model score itself shifts by 0.001953 between train and… | 0.25 | ratio | threshold.S1.psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 114 | data_integrity | The two time-displaced splits behave differently, and severa… | 0.25 | ratio | threshold.S1.psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 115 | data_integrity | In the out-of-time window, burnout shifts by 2.945 , loan_ag… | 2.945 | ratio | psi.burnout | out_of_time | eq | `[[art:7b0bbebb:psi.out_of_time.burnout]]` | verified | 2.944521522 |
| 116 | data_integrity | In the out-of-time window, burnout shifts by 2.945 , loan_ag… | 2.484 | ratio | psi.loan_age | out_of_time | eq | `[[art:d6eaaaf5:psi.out_of_time.loan_age]]` | verified | 2.483993033 |
| 117 | data_integrity | In the out-of-time window, burnout shifts by 2.945 , loan_ag… | 0.6977 | ratio | psi.note_rate | out_of_time | eq | `[[art:cabd371d:psi.out_of_time.note_rate]]` | verified | 0.6976589281 |
| 118 | data_integrity | In the out-of-time window, burnout shifts by 2.945 , loan_ag… | 0.4958 | ratio | psi.incentive | out_of_time | eq | `[[art:42076ed1:psi.out_of_time.incentive]]` | verified | 0.4958065489 |
| 119 | data_integrity | The model score shifts by 0.7056 over the same window, also… | 0.7056 | ratio | psi.y_score | out_of_time | eq | `[[art:2dc61374:psi.out_of_time.y_score]]` | verified | 0.7055906656 |
| 120 | data_integrity | The model score shifts by 0.7056 over the same window, also… | 0.25 | ratio | threshold.S1.psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 121 | data_integrity | The other out-of-time shifts remain below that bound: orig_u… | 0.07136 | ratio | psi.orig_upb_log | out_of_time | eq | `[[art:ac349b67:psi.out_of_time.orig_upb_log]]` | verified | 0.07136421414 |
| 122 | data_integrity | The other out-of-time shifts remain below that bound: orig_u… | 0.05988 | ratio | psi.credit_score | out_of_time | eq | `[[art:d7249e47:psi.out_of_time.credit_score]]` | verified | 0.05987964443 |
| 123 | data_integrity | The other out-of-time shifts remain below that bound: orig_u… | 0.04301 | ratio | psi.orig_ltv | out_of_time | eq | `[[art:3eee5db4:psi.out_of_time.orig_ltv]]` | verified | 0.04300793312 |
| 124 | data_integrity | The other out-of-time shifts remain below that bound: orig_u… | 0.02789 | ratio | psi.season_sin | out_of_time | eq | `[[art:144e1bd9:psi.out_of_time.season_sin]]` | verified | 0.02788988464 |
| 125 | data_integrity | The other out-of-time shifts remain below that bound: orig_u… | 0.01299 | ratio | psi.sato | out_of_time | eq | `[[art:c2233ce6:psi.out_of_time.sato]]` | verified | 0.01298850667 |
| 126 | data_integrity | The other out-of-time shifts remain below that bound: orig_u… | 0.007524 | ratio | psi.season_cos | out_of_time | eq | `[[art:25cf6b85:psi.out_of_time.season_cos]]` | verified | 0.00752368457 |
| 127 | data_integrity | In the vintage holdout, note_rate shifts by 0.6088 and incen… | 0.6088 | ratio | psi.note_rate | vintage_holdout | eq | `[[art:f281f8a7:psi.vintage_holdout.note_rate]]` | verified | 0.608822927 |
| 128 | data_integrity | In the vintage holdout, note_rate shifts by 0.6088 and incen… | 0.4475 | ratio | psi.incentive | vintage_holdout | eq | `[[art:5e61b6f9:psi.vintage_holdout.incentive]]` | verified | 0.4475226601 |
| 129 | data_integrity | In the vintage holdout, note_rate shifts by 0.6088 and incen… | 0.25 | ratio | threshold.S1.psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 130 | data_integrity | In the vintage holdout, note_rate shifts by 0.6088 and incen… | 0.07112 | ratio | psi.loan_age | vintage_holdout | eq | `[[art:6d92c48b:psi.vintage_holdout.loan_age]]` | verified | 0.07111526296 |
| 131 | data_integrity | In the vintage holdout, note_rate shifts by 0.6088 and incen… | 0.04749 | ratio | psi.burnout | vintage_holdout | eq | `[[art:e29067e6:psi.vintage_holdout.burnout]]` | verified | 0.04749372789 |
| 132 | data_integrity | In the vintage holdout, note_rate shifts by 0.6088 and incen… | 0.0404 | ratio | psi.orig_upb_log | vintage_holdout | eq | `[[art:77ec758a:psi.vintage_holdout.orig_upb_log]]` | verified | 0.04039645306 |
| 133 | data_integrity | In the vintage holdout, note_rate shifts by 0.6088 and incen… | 0.03996 | ratio | psi.credit_score | vintage_holdout | eq | `[[art:3498d307:psi.vintage_holdout.credit_score]]` | verified | 0.03995819732 |
| 134 | data_integrity | In the vintage holdout, note_rate shifts by 0.6088 and incen… | 0.02989 | ratio | psi.sato | vintage_holdout | eq | `[[art:eea64c25:psi.vintage_holdout.sato]]` | verified | 0.02989256711 |
| 135 | data_integrity | In the vintage holdout, note_rate shifts by 0.6088 and incen… | 0.02942 | ratio | psi.orig_ltv | vintage_holdout | eq | `[[art:d07cfb7d:psi.vintage_holdout.orig_ltv]]` | verified | 0.0294150369 |
| 136 | data_integrity | In the vintage holdout, note_rate shifts by 0.6088 and incen… | 0.001288 | ratio | psi.season_cos | vintage_holdout | eq | `[[art:9fe842a8:psi.vintage_holdout.season_cos]]` | verified | 0.0012879007 |
| 137 | data_integrity | In the vintage holdout, note_rate shifts by 0.6088 and incen… | 0.0007309 | ratio | psi.season_sin | vintage_holdout | eq | `[[art:b0dc9745:psi.vintage_holdout.season_sin]]` | verified | 0.0007309374015 |
| 138 | data_integrity | The score shift in the vintage holdout is 0.1421 , below the… | 0.1421 | ratio | psi.y_score | vintage_holdout | eq | `[[art:3713457e:psi.vintage_holdout.y_score]]` | verified | 0.142110315 |
| 139 | data_integrity | The score shift in the vintage holdout is 0.1421 , below the… | 0.25 | ratio | threshold.S1.psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 140 | data_integrity | Comparing the two displaced populations feature by feature a… | 2.945 | ratio | psi.burnout | out_of_time | eq | `[[art:7b0bbebb:psi.out_of_time.burnout]]` | verified | 2.944521522 |
| 141 | data_integrity | Comparing the two displaced populations feature by feature a… | 0.04749 | ratio | psi.burnout | vintage_holdout | eq | `[[art:e29067e6:psi.vintage_holdout.burnout]]` | verified | 0.04749372789 |
| 142 | data_integrity | Comparing the two displaced populations feature by feature a… | 2.484 | ratio | psi.loan_age | out_of_time | eq | `[[art:d6eaaaf5:psi.out_of_time.loan_age]]` | verified | 2.483993033 |
| 143 | data_integrity | Comparing the two displaced populations feature by feature a… | 0.07112 | ratio | psi.loan_age | vintage_holdout | eq | `[[art:6d92c48b:psi.vintage_holdout.loan_age]]` | verified | 0.07111526296 |
| 144 | data_integrity | At the characteristic level, the largest single contribution… | 0.03438 | ratio | csi.max |  | eq | `[[art:54bd75b0:csi.max]]` | verified | 0.03438094941 |
| 145 | data_integrity | At the characteristic level, the largest single contribution… | 0.03438 | ratio | csi.orig_ltv |  | eq | `[[art:97d51193:csi.orig_ltv]]` | verified | 0.03438094941 |
| 146 | data_integrity | At the characteristic level, the largest single contribution… | 0.25 | ratio | threshold.S1.psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 147 | data_integrity | The remaining contributions are note_rate at 0.01822 , credi… | 0.01822 | ratio | csi.note_rate |  | eq | `[[art:92901ac4:csi.note_rate]]` | verified | 0.01822065751 |
| 148 | data_integrity | The remaining contributions are note_rate at 0.01822 , credi… | 0.007909 | ratio | csi.credit_score |  | eq | `[[art:c40b4ede:csi.credit_score]]` | verified | 0.007908848663 |
| 149 | data_integrity | The remaining contributions are note_rate at 0.01822 , credi… | 0.005804 | ratio | csi.incentive |  | eq | `[[art:874ef644:csi.incentive]]` | verified | 0.005803522882 |
| 150 | data_integrity | The remaining contributions are note_rate at 0.01822 , credi… | 0.002969 | ratio | csi.orig_upb_log |  | eq | `[[art:bb919ade:csi.orig_upb_log]]` | verified | 0.00296903904 |
| 151 | data_integrity | The remaining contributions are note_rate at 0.01822 , credi… | 0.001487 | ratio | csi.sato |  | eq | `[[art:6a5f7a41:csi.sato]]` | verified | 0.001487358985 |
| 152 | data_integrity | The remaining contributions are note_rate at 0.01822 , credi… | 0.0009851 | ratio | csi.burnout |  | eq | `[[art:b2729e08:csi.burnout]]` | verified | 0.0009851123767 |
| 153 | data_integrity | The remaining contributions are note_rate at 0.01822 , credi… | 0.0004785 | ratio | csi.season_cos |  | eq | `[[art:75b544aa:csi.season_cos]]` | verified | 0.0004785421555 |
| 154 | data_integrity | The remaining contributions are note_rate at 0.01822 , credi… | 7.624e-05 | ratio | csi.season_sin |  | eq | `[[art:d55271d6:csi.season_sin]]` | verified | 7.624273793e-05 |
| 155 | data_integrity | The remaining contributions are note_rate at 0.01822 , credi… | 0 | ratio | csi.loan_age |  | eq | `[[art:df52c920:csi.loan_age]]` | verified | 0 |
| 156 | data_integrity | No feature is declared as observed during the performance pe… | 0 | count | leakage.timing.n_flagged |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 157 | data_integrity | The strongest single feature reaches an AUC of 0.7239 , belo… | 0.7239 | ratio | leakage.target_corr.max_single_feature_auc |  | eq | `[[art:1fe630dd:leakage.target_corr.max_single_feature_auc]]` | verified | 0.7238936567 |
| 158 | data_integrity | The strongest single feature reaches an AUC of 0.7239 , belo… | 0.9 | ratio | threshold.L1.single_feature_auc |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 159 | data_integrity | The share of test rows whose feature values also appear in t… | 0 | ratio | leakage.overlap |  | eq | `[[art:4c9fcd09:leakage.overlap]]` | verified | 0 |
| 160 | data_integrity | The share of test rows whose loan and period identifiers als… | 0 | ratio | leakage.overlap.ids |  | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 161 | data_integrity | The share of test rows whose loan and period identifiers als… | 0.005 | ratio | threshold.L2.overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 162 | data_integrity | The share of test rows whose feature vectors also appear in… | 0 | ratio | leakage.overlap.features |  | eq | `[[art:0fec8048:leakage.overlap.features]]` | verified | 0 |
| 163 | data_integrity | The share of test rows whose feature vectors also appear in… | 0.005 | ratio | threshold.L2.overlap.features_effective |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 164 | data_integrity | That applied bound is the larger of the declared overlap all… | 0 | ratio | leakage.duplicates | train | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 165 | data_integrity | That applied bound is the larger of the declared overlap all… | 0.005 | ratio | threshold.L2.overlap.features_effective |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 166 | data_integrity | That applied bound is the larger of the declared overlap all… | 0.005 | ratio | threshold.L2.overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 167 | data_integrity | The name screen matches 0 feature names against the target-a… | 0 | count | leakage.name_screen.n_matched |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 168 | outcomes | The calibration slope, from the logistic regression of the o… | 0.9937 | ratio | calibration_slope | train | eq | `[[art:534cb102:calibration_slope.train]]` | verified | 0.9936945557 |
| 169 | outcomes | The calibration slope, from the logistic regression of the o… | 0.9365 | ratio | calibration_slope | test | eq | `[[art:3e42ee62:calibration_slope.test]]` | verified | 0.9365180494 |
| 170 | outcomes | The calibration slope, from the logistic regression of the o… | 0.9969 | ratio | calibration_slope | out_of_time | eq | `[[art:a49b2789:calibration_slope.out_of_time]]` | verified | 0.9969389246 |
| 171 | outcomes | The calibration slope, from the logistic regression of the o… | 0.8373 | ratio | calibration_slope | vintage_holdout | eq | `[[art:08d6b321:calibration_slope.vintage_holdout]]` | verified | 0.837279841 |
| 172 | outcomes | All four sit inside the declared band, whose floor is 0.8 an… | 0.8 | ratio | calibration_slope |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 173 | outcomes | All four sit inside the declared band, whose floor is 0.8 an… | 1.2 | ratio | calibration_slope |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 174 | outcomes | The intercept of the same regression is -0.01454 on train, -… | -0.01454 | ratio | calibration_intercept | train | eq | `[[art:11d7a3ca:calibration_intercept.train]]` | verified | -0.01453793696 |
| 175 | outcomes | The intercept of the same regression is -0.01454 on train, -… | -0.277 | ratio | calibration_intercept | test | eq | `[[art:e87b5c13:calibration_intercept.test]]` | verified | -0.2769708146 |
| 176 | outcomes | The intercept of the same regression is -0.01454 on train, -… | -0.06272 | ratio | calibration_intercept | out_of_time | eq | `[[art:fc7ece3a:calibration_intercept.out_of_time]]` | verified | -0.06272473851 |
| 177 | outcomes | The intercept of the same regression is -0.01454 on train, -… | -0.9028 | ratio | calibration_intercept | vintage_holdout | eq | `[[art:44715143:calibration_intercept.vintage_holdout]]` | verified | -0.9028328443 |
| 178 | outcomes | Mean predicted probability against the observed event rate r… | 0.008427 | ratio | mean_predicted | train | eq | `[[art:a63f6555:metrics.train.mean_predicted]]` | verified | 0.008426526894 |
| 179 | outcomes | Mean predicted probability against the observed event rate r… | 0.008525 | ratio | event_rate | train | eq | `[[art:b9ef3327:metrics.train.event_rate]]` | verified | 0.008524699414 |
| 180 | outcomes | Mean predicted probability against the observed event rate r… | 0.008116 | ratio | mean_predicted | test | eq | `[[art:3bc93911:metrics.test.mean_predicted]]` | verified | 0.008115821785 |
| 181 | outcomes | Mean predicted probability against the observed event rate r… | 0.008061 | ratio | event_rate | test | eq | `[[art:570cc08a:metrics.test.event_rate]]` | verified | 0.008061370433 |
| 182 | outcomes | Mean predicted probability against the observed event rate r… | 0.01887 | ratio | mean_predicted | out_of_time | eq | `[[art:3833e0c5:metrics.out_of_time.mean_predicted]]` | verified | 0.01886588953 |
| 183 | outcomes | Mean predicted probability against the observed event rate r… | 0.01795 | ratio | event_rate | out_of_time | eq | `[[art:83ccf5c0:metrics.out_of_time.event_rate]]` | verified | 0.01794892714 |
| 184 | outcomes | Mean predicted probability against the observed event rate r… | 0.005647 | ratio | mean_predicted | vintage_holdout | eq | `[[art:5ae28866:metrics.vintage_holdout.mean_predicted]]` | verified | 0.005646788012 |
| 185 | outcomes | Mean predicted probability against the observed event rate r… | 0.004817 | ratio | event_rate | vintage_holdout | eq | `[[art:e3590a16:metrics.vintage_holdout.event_rate]]` | verified | 0.004817105386 |
| 186 | outcomes | Expressed as a relative gap, that comparison is 0.01152 on t… | 0.01152 | ratio | mean_rel_gap | train | eq | `[[art:e28c45a9:calibration.mean_rel_gap.train]]` | verified | 0.01151624417 |
| 187 | outcomes | Expressed as a relative gap, that comparison is 0.01152 on t… | 0.006755 | ratio | mean_rel_gap | test | eq | `[[art:59b8a1f5:calibration.mean_rel_gap.test]]` | verified | 0.006754602372 |
| 188 | outcomes | Expressed as a relative gap, that comparison is 0.01152 on t… | 0.05109 | ratio | mean_rel_gap | out_of_time | eq | `[[art:c599bd89:calibration.mean_rel_gap.out_of_time]]` | verified | 0.05108730888 |
| 189 | outcomes | Expressed as a relative gap, that comparison is 0.01152 on t… | 0.1722 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:55a672c2:calibration.mean_rel_gap.vintage_holdout]]` | verified | 0.1722367603 |
| 190 | outcomes | Each of the four is below the declared tolerance on that rel… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 191 | outcomes | Back-testing of the aggregate prepayment speed gives a mean… | 0.02658 | ratio | cpr_mae | train | eq | `[[art:f2c3683c:cpr.train.mae]]` | verified | 0.02657629251 |
| 192 | outcomes | Back-testing of the aggregate prepayment speed gives a mean… | 0.04264 | ratio | cpr_mae | test | eq | `[[art:ff266c97:cpr.test.mae]]` | verified | 0.042636033 |
| 193 | outcomes | Back-testing of the aggregate prepayment speed gives a mean… | 0.05857 | ratio | cpr_mae | out_of_time | eq | `[[art:a7ecd72b:cpr.out_of_time.mae]]` | verified | 0.05856944955 |
| 194 | outcomes | Back-testing of the aggregate prepayment speed gives a mean… | 0.0289 | ratio | cpr_mae | vintage_holdout | eq | `[[art:172ebed4:cpr.vintage_holdout.mae]]` | verified | 0.0289048118 |
| 195 | outcomes | \| AUC \| 0.7883 \| 0.7753 \| 0.7846 \| 0.7718 \| | 0.7883 | ratio | auc | train | eq | `[[art:fa609ae1:metrics.train.auc]]` | verified | 0.7883327303 |
| 196 | outcomes | \| AUC \| 0.7883 \| 0.7753 \| 0.7846 \| 0.7718 \| | 0.7753 | ratio | auc | test | eq | `[[art:57066271:metrics.test.auc]]` | verified | 0.7752553922 |
| 197 | outcomes | \| AUC \| 0.7883 \| 0.7753 \| 0.7846 \| 0.7718 \| | 0.7846 | ratio | auc | out_of_time | eq | `[[art:6f2a2d99:metrics.out_of_time.auc]]` | verified | 0.7845616168 |
| 198 | outcomes | \| AUC \| 0.7883 \| 0.7753 \| 0.7846 \| 0.7718 \| | 0.7718 | ratio | auc | vintage_holdout | eq | `[[art:ac6794c5:metrics.vintage_holdout.auc]]` | verified | 0.7717974135 |
| 199 | outcomes | \| Gini \| 0.5767 \| 0.5505 \| 0.5691 \| 0.5436 \| | 0.5767 | ratio | gini | train | eq | `[[art:0b6b2058:metrics.train.gini]]` | verified | 0.5766654607 |
| 200 | outcomes | \| Gini \| 0.5767 \| 0.5505 \| 0.5691 \| 0.5436 \| | 0.5505 | ratio | gini | test | eq | `[[art:fe7f75d7:metrics.test.gini]]` | verified | 0.5505107844 |
| 201 | outcomes | \| Gini \| 0.5767 \| 0.5505 \| 0.5691 \| 0.5436 \| | 0.5691 | ratio | gini | out_of_time | eq | `[[art:890252d7:metrics.out_of_time.gini]]` | verified | 0.5691232337 |
| 202 | outcomes | \| Gini \| 0.5767 \| 0.5505 \| 0.5691 \| 0.5436 \| | 0.5436 | ratio | gini | vintage_holdout | eq | `[[art:a4a532f0:metrics.vintage_holdout.gini]]` | verified | 0.5435948269 |
| 203 | outcomes | \| KS \| 0.4562 \| 0.4162 \| 0.4321 \| 0.4516 \| | 0.4562 | ratio | ks | train | eq | `[[art:c355478b:metrics.train.ks]]` | verified | 0.4562056834 |
| 204 | outcomes | \| KS \| 0.4562 \| 0.4162 \| 0.4321 \| 0.4516 \| | 0.4162 | ratio | ks | test | eq | `[[art:c569c301:metrics.test.ks]]` | verified | 0.4161772354 |
| 205 | outcomes | \| KS \| 0.4562 \| 0.4162 \| 0.4321 \| 0.4516 \| | 0.4321 | ratio | ks | out_of_time | eq | `[[art:16d3e4fe:metrics.out_of_time.ks]]` | verified | 0.4321115953 |
| 206 | outcomes | \| KS \| 0.4562 \| 0.4162 \| 0.4321 \| 0.4516 \| | 0.4516 | ratio | ks | vintage_holdout | eq | `[[art:b5b9e888:metrics.vintage_holdout.ks]]` | verified | 0.4515647508 |
| 207 | outcomes | \| Brier \| 0.008317 \| 0.007894 \| 0.01713 \| 0.004763 \| | 0.008317 | ratio | brier | train | eq | `[[art:83666c70:metrics.train.brier]]` | verified | 0.008317491392 |
| 208 | outcomes | \| Brier \| 0.008317 \| 0.007894 \| 0.01713 \| 0.004763 \| | 0.007894 | ratio | brier | test | eq | `[[art:7d3583cd:metrics.test.brier]]` | verified | 0.00789356705 |
| 209 | outcomes | \| Brier \| 0.008317 \| 0.007894 \| 0.01713 \| 0.004763 \| | 0.01713 | ratio | brier | out_of_time | eq | `[[art:40d244d4:metrics.out_of_time.brier]]` | verified | 0.0171279495 |
| 210 | outcomes | \| Brier \| 0.008317 \| 0.007894 \| 0.01713 \| 0.004763 \| | 0.004763 | ratio | brier | vintage_holdout | eq | `[[art:f3c6bdcc:metrics.vintage_holdout.brier]]` | verified | 0.004763025704 |
| 211 | outcomes | \| Log loss \| 0.04408 \| 0.04263 \| 0.07975 \| 0.02811 \| | 0.04408 | ratio | logloss | train | eq | `[[art:199c7db5:metrics.train.logloss]]` | verified | 0.04408402922 |
| 212 | outcomes | \| Log loss \| 0.04408 \| 0.04263 \| 0.07975 \| 0.02811 \| | 0.04263 | ratio | logloss | test | eq | `[[art:320e4c6b:metrics.test.logloss]]` | verified | 0.04263297829 |
| 213 | outcomes | \| Log loss \| 0.04408 \| 0.04263 \| 0.07975 \| 0.02811 \| | 0.07975 | ratio | logloss | out_of_time | eq | `[[art:2b7c9b2d:metrics.out_of_time.logloss]]` | verified | 0.07975283787 |
| 214 | outcomes | \| Log loss \| 0.04408 \| 0.04263 \| 0.07975 \| 0.02811 \| | 0.02811 | ratio | logloss | vintage_holdout | eq | `[[art:c32e3713:metrics.vintage_holdout.logloss]]` | verified | 0.02810570342 |
| 215 | outcomes | \| Share of events in the top two deciles \| 0.5961 \| 0.5806 \|… | 0.5961 | ratio | top2_capture | train | eq | `[[art:e8dd0c53:deciles.train.top2_capture]]` | verified | 0.5960912052 |
| 216 | outcomes | \| Share of events in the top two deciles \| 0.5961 \| 0.5806 \|… | 0.5806 | ratio | top2_capture | test | eq | `[[art:43c4adc5:deciles.test.top2_capture]]` | verified | 0.5806451613 |
| 217 | outcomes | \| Share of events in the top two deciles \| 0.5961 \| 0.5806 \|… | 0.5773 | ratio | top2_capture | out_of_time | eq | `[[art:df63152b:deciles.out_of_time.top2_capture]]` | verified | 0.5772727273 |
| 218 | outcomes | \| Share of events in the top two deciles \| 0.5961 \| 0.5806 \|… | 0.5871 | ratio | top2_capture | vintage_holdout | eq | `[[art:8b59f312:deciles.vintage_holdout.top2_capture]]` | verified | 0.5870967742 |
| 219 | outcomes | \| Rows \| 36013 \| 15382 \| 12257 \| 32177 \| | 36013 | count | n | train | eq | `[[art:6fdfeabb:metrics.train.n]]` | verified | 36013 |
| 220 | outcomes | \| Rows \| 36013 \| 15382 \| 12257 \| 32177 \| | 15382 | count | n | test | eq | `[[art:e55953e1:metrics.test.n]]` | verified | 15382 |
| 221 | outcomes | \| Rows \| 36013 \| 15382 \| 12257 \| 32177 \| | 12257 | count | n | out_of_time | eq | `[[art:7898809e:metrics.out_of_time.n]]` | verified | 12257 |
| 222 | outcomes | \| Rows \| 36013 \| 15382 \| 12257 \| 32177 \| | 32177 | count | n | vintage_holdout | eq | `[[art:37a92951:metrics.vintage_holdout.n]]` | verified | 32177 |
| 223 | outcomes | AUC on train, at 0.7883 , stands above AUC on test, at 0.775… | 0.7883 | ratio | auc | train | eq | `[[art:fa609ae1:metrics.train.auc]]` | verified | 0.7883327303 |
| 224 | outcomes | AUC on train, at 0.7883 , stands above AUC on test, at 0.775… | 0.7753 | ratio | auc | test | eq | `[[art:57066271:metrics.test.auc]]` | verified | 0.7752553922 |
| 225 | outcomes | AUC on train, at 0.7883 , stands above AUC on test, at 0.775… | 0.08 | ratio | auc_gap |  | eq | `[[art:630f28f4:threshold.O1.auc_gap]]` | verified | 0.08 |
| 226 | outcomes | On train this slice's AUC falls 0.07016 below the split's ow… | 0.07016 | ratio | auc_gap | train | eq | `[[art:8d8827f2:metrics.train.sub.incentive_high.auc_gap]]` | verified | 0.07015660217 |
| 227 | outcomes | On train this slice's AUC falls 0.07016 below the split's ow… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 228 | outcomes | On test the shortfall is 0.0484 , on the out-of-time split 0… | 0.0484 | ratio | auc_gap | test | eq | `[[art:5a0ba9c4:metrics.test.sub.incentive_high.auc_gap]]` | verified | 0.04840270693 |
| 229 | outcomes | On test the shortfall is 0.0484 , on the out-of-time split 0… | 0.03734 | ratio | auc_gap | out_of_time | eq | `[[art:1c0207f9:metrics.out_of_time.sub.incentive_high.auc_gap]]` | verified | 0.0373425714 |
| 230 | outcomes | On test the shortfall is 0.0484 , on the out-of-time split 0… | 0.01875 | ratio | auc_gap | vintage_holdout | eq | `[[art:2ebd6757:metrics.vintage_holdout.sub.incentive_high.auc_gap]]` | verified | 0.01874804418 |
| 231 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.4999 of the out… | 0.5 | ratio | share | train | eq | `[[art:277218fb:metrics.train.sub.incentive_high.share]]` | verified | 0.4999861161 |
| 232 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.4999 of the out… | 0.5 | ratio | share | test | eq | `[[art:549aa934:metrics.test.sub.incentive_high.share]]` | verified | 0.5 |
| 233 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.4999 of the out… | 0.4999 | ratio | share | out_of_time | eq | `[[art:431d1ff2:metrics.out_of_time.sub.incentive_high.share]]` | verified | 0.499877621 |
| 234 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.4999 of the out… | 0.5 | ratio | share | vintage_holdout | eq | `[[art:cb627056:metrics.vintage_holdout.sub.incentive_high.share]]` | verified | 0.499984461 |
| 235 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.4999 of the out… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 236 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.4999 of the out… | 0.95 | ratio | slice_max_share |  | eq | `[[art:a928a05c:threshold.O1.slice_max_share]]` | verified | 0.95 |
| 237 | outcomes | Mean predicted against observed on the slice, relative, is 0… | 0.01445 | ratio | mean_rel_gap | train | eq | `[[art:7d3d3639:metrics.train.sub.incentive_high.mean_rel_gap]]` | verified | 0.01445428336 |
| 238 | outcomes | Mean predicted against observed on the slice, relative, is 0… | 0.03492 | ratio | mean_rel_gap | test | eq | `[[art:f90b2790:metrics.test.sub.incentive_high.mean_rel_gap]]` | verified | 0.03491504769 |
| 239 | outcomes | Mean predicted against observed on the slice, relative, is 0… | 0.1235 | ratio | mean_rel_gap | out_of_time | eq | `[[art:f0899b32:metrics.out_of_time.sub.incentive_high.mean_rel_gap]]` | verified | 0.123516925 |
| 240 | outcomes | Mean predicted against observed on the slice, relative, is 0… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 241 | outcomes | On the vintage holdout the same quantity is 0.2976 , above t… | 0.2976 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:d14397a7:metrics.vintage_holdout.sub.incentive_high.mean_rel_gap]]` | verified | 0.2975984466 |
| 242 | outcomes | On the vintage holdout the same quantity is 0.2976 , above t… | 0.009598 | ratio | mean_predicted | vintage_holdout | eq | `[[art:192eb7d4:metrics.vintage_holdout.sub.incentive_high.mean_predicted]]` | verified | 0.009598098902 |
| 243 | outcomes | On the vintage holdout the same quantity is 0.2976 , above t… | 0.007397 | ratio | event_rate | vintage_holdout | eq | `[[art:947de0ec:metrics.vintage_holdout.sub.incentive_high.event_rate]]` | verified | 0.007396817504 |
| 244 | outcomes | On train this slice's AUC falls 0.06703 below the split's ow… | 0.06703 | ratio | auc_gap | train | eq | `[[art:134d7c07:metrics.train.sub.incentive_low.auc_gap]]` | verified | 0.06702950807 |
| 245 | outcomes | On train this slice's AUC falls 0.06703 below the split's ow… | 0.0163 | ratio | auc_gap | out_of_time | eq | `[[art:faa1a185:metrics.out_of_time.sub.incentive_low.auc_gap]]` | verified | 0.01629917634 |
| 246 | outcomes | On train this slice's AUC falls 0.06703 below the split's ow… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 247 | outcomes | On test the shortfall is 0.09283 and on the vintage holdout… | 0.09283 | ratio | auc_gap | test | eq | `[[art:a0523ad8:metrics.test.sub.incentive_low.auc_gap]]` | verified | 0.09282587144 |
| 248 | outcomes | On test the shortfall is 0.09283 and on the vintage holdout… | 0.09945 | ratio | auc_gap | vintage_holdout | eq | `[[art:9de83338:metrics.vintage_holdout.sub.incentive_low.auc_gap]]` | verified | 0.09944645103 |
| 249 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.5001 of the out… | 0.5 | ratio | share | train | eq | `[[art:d7af12f0:metrics.train.sub.incentive_low.share]]` | verified | 0.5000138839 |
| 250 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.5001 of the out… | 0.5 | ratio | share | test | eq | `[[art:1d5dd4c2:metrics.test.sub.incentive_low.share]]` | verified | 0.5 |
| 251 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.5001 of the out… | 0.5001 | ratio | share | out_of_time | eq | `[[art:c7aaafd2:metrics.out_of_time.sub.incentive_low.share]]` | verified | 0.500122379 |
| 252 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.5001 of the out… | 0.5 | ratio | share | vintage_holdout | eq | `[[art:d94e6531:metrics.vintage_holdout.sub.incentive_low.share]]` | verified | 0.500015539 |
| 253 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.5001 of the out… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 254 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.5001 of the out… | 0.95 | ratio | slice_max_share |  | eq | `[[art:a928a05c:threshold.O1.slice_max_share]]` | verified | 0.95 |
| 255 | outcomes | Mean predicted against observed on the slice, relative, is 0… | 0.003953 | ratio | mean_rel_gap | train | eq | `[[art:05adce6c:metrics.train.sub.incentive_low.mean_rel_gap]]` | verified | 0.003953431529 |
| 256 | outcomes | Mean predicted against observed on the slice, relative, is 0… | 0.1169 | ratio | mean_rel_gap | test | eq | `[[art:aede705c:metrics.test.sub.incentive_low.mean_rel_gap]]` | verified | 0.1169064836 |
| 257 | outcomes | Mean predicted against observed on the slice, relative, is 0… | 0.2155 | ratio | mean_rel_gap | out_of_time | eq | `[[art:81d9f6b7:metrics.out_of_time.sub.incentive_low.mean_rel_gap]]` | verified | 0.2155153206 |
| 258 | outcomes | Mean predicted against observed on the slice, relative, is 0… | 0.2422 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:20691619:metrics.vintage_holdout.sub.incentive_low.mean_rel_gap]]` | verified | 0.2421532582 |
| 259 | outcomes | Mean predicted against observed on the slice, relative, is 0… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 260 | sensitivity | The largest variance inflation factor among the retained fea… | 4.976 | ratio | vif |  | eq | `[[art:f9e0db60:vif.max]]` | verified | 4.975500767 |
| 261 | sensitivity | The largest variance inflation factor among the retained fea… | 10 | ratio | vif |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 262 | sensitivity | That largest value is carried by the note rate at 4.976 , wi… | 4.976 | ratio | vif |  | eq | `[[art:37532fa8:vif.note_rate]]` | verified | 4.975500767 |
| 263 | sensitivity | That largest value is carried by the note rate at 4.976 , wi… | 3.439 | ratio | vif |  | eq | `[[art:88879cb2:vif.burnout]]` | verified | 3.439328594 |
| 264 | sensitivity | That largest value is carried by the note rate at 4.976 , wi… | 2.929 | ratio | vif |  | eq | `[[art:5573d536:vif.loan_age]]` | verified | 2.928871763 |
| 265 | sensitivity | The remaining retained features sit further from the bound:… | 2.226 | ratio | vif |  | eq | `[[art:2da1b19c:vif.incentive]]` | verified | 2.22632259 |
| 266 | sensitivity | The remaining retained features sit further from the bound:… | 1.713 | ratio | vif |  | eq | `[[art:a6c55fce:vif.sato]]` | verified | 1.71256814 |
| 267 | sensitivity | The remaining retained features sit further from the bound:… | 1.018 | ratio | vif |  | eq | `[[art:a9cfa7eb:vif.season_cos]]` | verified | 1.017653349 |
| 268 | sensitivity | The remaining retained features sit further from the bound:… | 1.008 | ratio | vif |  | eq | `[[art:f05d536a:vif.credit_score]]` | verified | 1.007978309 |
| 269 | sensitivity | The remaining retained features sit further from the bound:… | 1.006 | ratio | vif |  | eq | `[[art:24f8e4d1:vif.orig_upb_log]]` | verified | 1.005846447 |
| 270 | sensitivity | The remaining retained features sit further from the bound:… | 1.005 | ratio | vif |  | eq | `[[art:65b35f3b:vif.orig_ltv]]` | verified | 1.004506143 |
| 271 | sensitivity | The remaining retained features sit further from the bound:… | 1.004 | ratio | vif |  | eq | `[[art:669c5fcb:vif.season_sin]]` | verified | 1.004128844 |
| 272 | sensitivity | Belsley's condition number of the column-standardised design… | 4.943 | ratio | condition_number |  | eq | `[[art:4f06a3c5:condition_number]]` | verified | 4.942565522 |
| 273 | sensitivity | Belsley's condition number of the column-standardised design… | 30 | ratio | condition_number |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 274 | sensitivity | The within-regime discrimination shown above is read against… | 0.1 | ratio | auc_gap |  | eq | `[[art:b64213d7:threshold.R1.auc_gap]]` | verified | 0.1 |
| 275 | sensitivity | A coefficient sign flip is counted only where an influential… | 0.05 | ratio | sign_flip_coef |  | eq | `[[art:aca84377:threshold.R1.sign_flip_coef]]` | verified | 0.05 |
| 276 | sensitivity | A coefficient sign flip is counted only where an influential… | 2 | ratio | sign_flip_z |  | eq | `[[art:2e4428c7:threshold.R1.sign_flip_z]]` | verified | 2 |
| 277 | sensitivity | On that joint criterion the flip indicator reads 0 for the r… | 0 | ratio | sign_flip |  | eq | `[[art:0cc7a37d:stability.incentive.sign_flip]]` | verified | 0 |
| 278 | sensitivity | On that joint criterion the flip indicator reads 0 for the r… | 0 | ratio | sign_flip |  | eq | `[[art:e7ce4912:stability.note_rate.sign_flip]]` | verified | 0 |
| 279 | sensitivity | On that joint criterion the flip indicator reads 0 for the r… | 0 | ratio | sign_flip |  | eq | `[[art:1f302ccd:stability.sato.sign_flip]]` | verified | 0 |
| 280 | sensitivity | On that joint criterion the flip indicator reads 0 for the r… | 0 | ratio | sign_flip |  | eq | `[[art:b7191217:stability.loan_age.sign_flip]]` | verified | 0 |
| 281 | sensitivity | On that joint criterion the flip indicator reads 0 for the r… | 0 | ratio | sign_flip |  | eq | `[[art:6bc05e82:stability.burnout.sign_flip]]` | verified | 0 |
| 282 | sensitivity | On that joint criterion the flip indicator reads 0 for the r… | 0 | ratio | sign_flip |  | eq | `[[art:d956c276:stability.credit_score.sign_flip]]` | verified | 0 |
| 283 | sensitivity | On that joint criterion the flip indicator reads 0 for the r… | 0 | ratio | sign_flip |  | eq | `[[art:054d5fab:stability.orig_ltv.sign_flip]]` | verified | 0 |
| 284 | sensitivity | On that joint criterion the flip indicator reads 0 for the r… | 0 | ratio | sign_flip |  | eq | `[[art:fb1ae6c8:stability.orig_upb_log.sign_flip]]` | verified | 0 |
| 285 | sensitivity | On that joint criterion the flip indicator reads 0 for the r… | 0 | ratio | sign_flip |  | eq | `[[art:1850e2de:stability.season_cos.sign_flip]]` | verified | 0 |
| 286 | sensitivity | On that joint criterion the flip indicator reads 0 for the r… | 0 | ratio | sign_flip |  | eq | `[[art:6ba36a3b:stability.season_sin.sign_flip]]` | verified | 0 |
| 287 | sensitivity | At the downward extreme the change in servicing value is 168… | 168100 | currency | value_change |  | eq | `[[art:e1211d5d:scenario.value_change.-300]]` | verified | 168054.7452 |
| 288 | sensitivity | At the downward extreme the change in servicing value is 168… | 168100 | currency | value_change |  | eq | `[[art:38e75872:scenario.value_change.300]]` | verified | 168054.7452 |
| 289 | sensitivity | Between those ends the profile reverses direction on the dow… | -854300 | currency | value_change |  | eq | `[[art:03816874:scenario.value_change.-200]]` | verified | -854265.8614 |
| 290 | sensitivity | Between those ends the profile reverses direction on the dow… | -322600 | currency | value_change |  | eq | `[[art:d33e8e3c:scenario.value_change.-100]]` | verified | -322648.7678 |
| 291 | sensitivity | Between those ends the profile reverses direction on the dow… | 0 | currency | value_change |  | eq | `[[art:1e1b0b88:scenario.value_change.0]]` | verified | 0 |
| 292 | sensitivity | On the upward side the changes rise steadily, from 119600 at… | 119600 | currency | value_change |  | eq | `[[art:d0970bd9:scenario.value_change.100]]` | verified | 119555.7352 |
| 293 | sensitivity | On the upward side the changes rise steadily, from 119600 at… | 157000 | currency | value_change |  | eq | `[[art:d69c2be1:scenario.value_change.200]]` | verified | 156987.0553 |
| 294 | sensitivity | On the upward side the changes rise steadily, from 119600 at… | 168100 | currency | value_change |  | eq | `[[art:38e75872:scenario.value_change.300]]` | verified | 168054.7452 |
| 295 | sensitivity | The realised convexity is 336100 , which is positive, wherea… | 336100 | currency | convexity |  | eq | `[[art:6d2d7838:scenario.convexity]]` | verified | 336109.4903 |
| 296 | findings | At the largest down-shock the projected value is 1765000 , a… | 1765000 | currency | value_by_shock |  | eq | `[[art:cbc0b707:run.projection#value_by_shock.-300]]` | verified | 1764869.753 |
| 297 | findings | At the largest down-shock the projected value is 1765000 , a… | 742500 | currency | value_by_shock |  | eq | `[[art:cbc0b707:run.projection#value_by_shock.-200]]` | verified | 742549.1466 |
| 298 | findings | At the largest down-shock the projected value is 1765000 , a… | 1597000 | currency | value_by_shock |  | eq | `[[art:cbc0b707:run.projection#value_by_shock.0]]` | verified | 1596815.008 |
| 299 | findings | The change from the base case at the largest down-shock is 1… | 168100 | currency | value_change |  | eq | `[[art:e1211d5d:scenario.value_change.-300]]` | verified | 168054.7452 |
| 300 | findings | The change from the base case at the largest down-shock is 1… | 168100 | currency | value_change |  | eq | `[[art:38e75872:scenario.value_change.300]]` | verified | 168054.7452 |
| 301 | findings | First-year CPR at the largest down-shock is 0.0005476 and fi… | 0.0005476 | ratio | cpr_by_shock |  | eq | `[[art:cbc0b707:run.projection#cpr_by_shock.-300]]` | verified | 0.0005476230611 |
| 302 | findings | First-year CPR at the largest down-shock is 0.0005476 and fi… | 0.0005476 | ratio | cpr_by_shock |  | eq | `[[art:cbc0b707:run.projection#cpr_by_shock.300]]` | verified | 0.0005476230611 |
| 303 | findings | First-year CPR at the largest down-shock is 0.0005476 and fi… | 0.2519 | ratio | cpr_by_shock |  | eq | `[[art:cbc0b707:run.projection#cpr_by_shock.-200]]` | verified | 0.2518840464 |
| 304 | findings | The realised convexity, the change at the largest down-shock… | 336100 | currency | convexity |  | eq | `[[art:6d2d7838:scenario.convexity]]` | verified | 336109.4903 |
| 305 | findings | On the test split, AUC inside the segment `incentive <= medi… | 0.6824 | ratio | auc | test | eq | `[[art:0f9a3d96:metrics.test.sub.incentive_low.auc]]` | verified | 0.6824295208 |
| 306 | findings | On the test split, AUC inside the segment `incentive <= medi… | 0.7753 | ratio | auc | test | eq | `[[art:57066271:metrics.test.auc]]` | verified | 0.7752553922 |
| 307 | findings | On the test split, AUC inside the segment `incentive <= medi… | 0.09283 | ratio | auc_gap | test | eq | `[[art:a0523ad8:metrics.test.sub.incentive_low.auc_gap]]` | verified | 0.09282587144 |
| 308 | findings | On the test split, AUC inside the segment `incentive <= medi… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 309 | findings | On the test split, AUC inside the segment `incentive <= medi… | 0.5 | ratio | share | test | eq | `[[art:1d5dd4c2:metrics.test.sub.incentive_low.share]]` | verified | 0.5 |
| 310 | findings | On the test split, AUC inside the segment `incentive <= medi… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 311 | findings | On the vintage_holdout split, AUC inside the segment `incent… | 0.6724 | ratio | auc | vintage_holdout | eq | `[[art:0510c841:metrics.vintage_holdout.sub.incentive_low.auc]]` | verified | 0.6723509624 |
| 312 | findings | On the vintage_holdout split, AUC inside the segment `incent… | 0.7718 | ratio | auc | vintage_holdout | eq | `[[art:ac6794c5:metrics.vintage_holdout.auc]]` | verified | 0.7717974135 |
| 313 | findings | On the vintage_holdout split, AUC inside the segment `incent… | 0.09945 | ratio | auc_gap | vintage_holdout | eq | `[[art:9de83338:metrics.vintage_holdout.sub.incentive_low.auc_gap]]` | verified | 0.09944645103 |
| 314 | findings | On the vintage_holdout split, AUC inside the segment `incent… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 315 | findings | On the vintage_holdout split, AUC inside the segment `incent… | 0.5 | ratio | share | vintage_holdout | eq | `[[art:d94e6531:metrics.vintage_holdout.sub.incentive_low.share]]` | verified | 0.500015539 |
| 316 | findings | On the vintage_holdout split, AUC inside the segment `incent… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 317 | findings | The fitted coefficient on `note_rate` carries sign -1 where… | -1 | ratio | coef_sign |  | eq | `[[art:aecf7ccb:sign_check.note_rate.coef_sign]]` | verified | -1 |
| 318 | findings | The fitted coefficient on `note_rate` carries sign -1 where… | 1 | ratio | univariate_direction |  | eq | `[[art:61f6e1ac:sign_check.note_rate.univariate_direction]]` | verified | 1 |
| 319 | findings | The fitted coefficient on `note_rate` carries sign -1 where… | 0 | ratio | agrees |  | eq | `[[art:a453463d:sign_check.note_rate.agrees]]` | verified | 0 |
| 320 | monitoring | - Recompute the largest population stability index across th… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 321 | monitoring | - Recompute the largest population stability index across th… | 0.06189 | ratio | psi |  | eq | `[[art:c2e8c8fd:psi.max]]` | verified | 0.06188985797 |
| 322 | monitoring | - Refit the logistic regression of the realized prepayment o… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 323 | monitoring | - Refit the logistic regression of the realized prepayment o… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 324 | monitoring | - Refit the logistic regression of the realized prepayment o… | 0.9365 | ratio | calibration_slope | test | eq | `[[art:3e42ee62:calibration_slope.test]]` | verified | 0.9365180494 |
| 325 | monitoring | - Recompute discrimination on the same realized outcomes qua… | 0.65 | ratio | auc | test | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 326 | monitoring | - Recompute discrimination on the same realized outcomes qua… | 0.7753 | ratio | auc | test | eq | `[[art:57066271:metrics.test.auc]]` | verified | 0.7752553922 |

## Appendix B — Artifact index

The store holds 371 artifacts; the 252 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `ablation.baseline_auc` | `54367df6` | scalar | 0.7672992275 | AUC on test of a refit of the champion's functional form on every retained feature, the level each ablation delta is measured from |
| `ablation.burnout.delta_auc` | `3cba039b` | scalar | -0.0001876329287 | change in test AUC when the champion's form is refitted without burnout |
| `ablation.credit_score.delta_auc` | `9bdeb0df` | scalar | -0.0147431913 | change in test AUC when the champion's form is refitted without credit_score |
| `ablation.incentive.delta_auc` | `78108590` | scalar | -0.0411745927 | change in test AUC when the champion's form is refitted without incentive |
| `ablation.loan_age.delta_auc` | `be669163` | scalar | 0.0008165996474 | change in test AUC when the champion's form is refitted without loan_age |
| `ablation.note_rate.delta_auc` | `14558b82` | scalar | -0.002585106068 | change in test AUC when the champion's form is refitted without note_rate |
| `ablation.orig_ltv.delta_auc` | `57ea66c5` | scalar | -0.002294407165 | change in test AUC when the champion's form is refitted without orig_ltv |
| `ablation.orig_upb_log.delta_auc` | `0ddb11a9` | scalar | -0.01926646624 | change in test AUC when the champion's form is refitted without orig_upb_log |
| `ablation.sato.delta_auc` | `57703504` | scalar | 0.0005200867657 | change in test AUC when the champion's form is refitted without sato |
| `ablation.season_cos.delta_auc` | `a288439d` | scalar | -0.00048256018 | change in test AUC when the champion's form is refitted without season_cos |
| `ablation.season_sin.delta_auc` | `e54c8581` | scalar | -0.0003884794439 | change in test AUC when the champion's form is refitted without season_sin |
| `calibration.mean_rel_gap.out_of_time` | `c599bd89` | scalar | 0.05108730888 | mean predicted against observed on out_of_time, relative |
| `calibration.mean_rel_gap.test` | `59b8a1f5` | scalar | 0.006754602372 | mean predicted against observed on test, relative |
| `calibration.mean_rel_gap.train` | `e28c45a9` | scalar | 0.01151624417 | mean predicted against observed on train, relative |
| `calibration.mean_rel_gap.vintage_holdout` | `55a672c2` | scalar | 0.1722367603 | mean predicted against observed on vintage_holdout, relative |
| `calibration.test` | `dcbc44e6` | table | table, 10 rows | calibration by decile of predicted probability on test |
| `calibration_intercept.out_of_time` | `fc7ece3a` | scalar | -0.06272473851 | logistic regression of the outcome on logit(p) on out_of_time: the intercept |
| `calibration_intercept.test` | `e87b5c13` | scalar | -0.2769708146 | logistic regression of the outcome on logit(p) on test: the intercept |
| `calibration_intercept.train` | `11d7a3ca` | scalar | -0.01453793696 | logistic regression of the outcome on logit(p) on train: the intercept |
| `calibration_intercept.vintage_holdout` | `44715143` | scalar | -0.9028328443 | logistic regression of the outcome on logit(p) on vintage_holdout: the intercept |
| `calibration_slope.out_of_time` | `a49b2789` | scalar | 0.9969389246 | logistic regression of the outcome on logit(p) on out_of_time: the slope |
| `calibration_slope.test` | `3e42ee62` | scalar | 0.9365180494 | logistic regression of the outcome on logit(p) on test: the slope |
| `calibration_slope.train` | `534cb102` | scalar | 0.9936945557 | logistic regression of the outcome on logit(p) on train: the slope |
| `calibration_slope.vintage_holdout` | `08d6b321` | scalar | 0.837279841 | logistic regression of the outcome on logit(p) on vintage_holdout: the slope |
| `challenger.auc` | `705b66f0` | scalar | 0.7337079121 | the challenger's AUC on test |
| `challenger.brier` | `85a89ef9` | scalar | 0.008629514666 | the challenger's Brier score on test |
| `challenger.delta_auc` | `4d28c096` | scalar | -0.04154748012 | the challenger's AUC on test minus the champion's |
| `condition_number` | `4f06a3c5` | scalar | 4.942565522 | Belsley's condition number of the column-standardised design |
| `cpr.out_of_time.mae` | `a7ecd72b` | scalar | 0.05856944955 | mean absolute difference between actual and predicted CPR on out_of_time |
| `cpr.test` | `ecbd1494` | table | table, 71 rows | actual against predicted CPR by period on test |
| `cpr.test.mae` | `ff266c97` | scalar | 0.042636033 | mean absolute difference between actual and predicted CPR on test |
| `cpr.train.mae` | `f2c3683c` | scalar | 0.02657629251 | mean absolute difference between actual and predicted CPR on train |
| `cpr.vintage_holdout.mae` | `172ebed4` | scalar | 0.0289048118 | mean absolute difference between actual and predicted CPR on vintage_holdout |
| `csi.burnout` | `b2729e08` | scalar | 0.0009851123767 | CSI of burnout: its contribution to the shift in the linear predictor |
| `csi.credit_score` | `c40b4ede` | scalar | 0.007908848663 | CSI of credit_score: its contribution to the shift in the linear predictor |
| `csi.incentive` | `874ef644` | scalar | 0.005803522882 | CSI of incentive: its contribution to the shift in the linear predictor |
| `csi.loan_age` | `df52c920` | scalar | 0 | CSI of loan_age: its contribution to the shift in the linear predictor |
| `csi.max` | `54bd75b0` | scalar | 0.03438094941 | the largest characteristic stability index |
| `csi.note_rate` | `92901ac4` | scalar | 0.01822065751 | CSI of note_rate: its contribution to the shift in the linear predictor |
| `csi.orig_ltv` | `97d51193` | scalar | 0.03438094941 | CSI of orig_ltv: its contribution to the shift in the linear predictor |
| `csi.orig_upb_log` | `bb919ade` | scalar | 0.00296903904 | CSI of orig_upb_log: its contribution to the shift in the linear predictor |
| `csi.sato` | `6a5f7a41` | scalar | 0.001487358985 | CSI of sato: its contribution to the shift in the linear predictor |
| `csi.season_cos` | `75b544aa` | scalar | 0.0004785421555 | CSI of season_cos: its contribution to the shift in the linear predictor |
| `csi.season_sin` | `d55271d6` | scalar | 7.624273793e-05 | CSI of season_sin: its contribution to the shift in the linear predictor |
| `deciles.out_of_time.top2_capture` | `df63152b` | scalar | 0.5772727273 | share of out_of_time events in the top two deciles |
| `deciles.test` | `309fa6f3` | table | table, 10 rows | decile separation on test; decile 1 holds the highest probabilities |
| `deciles.test.top2_capture` | `43c4adc5` | scalar | 0.5806451613 | share of test events in the top two deciles |
| `deciles.train.top2_capture` | `e8dd0c53` | scalar | 0.5960912052 | share of train events in the top two deciles |
| `deciles.vintage_holdout.top2_capture` | `8b59f312` | scalar | 0.5870967742 | share of vintage_holdout events in the top two deciles |
| `leakage.duplicates.train` | `4474c227` | scalar | 0 | share of train rows whose feature values are not unique within train |
| `leakage.name_screen.n_matched` | `407e62be` | scalar | 0 | feature names matching the target-adjacent lexicon |
| `leakage.overlap` | `4c9fcd09` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.features` | `0fec8048` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.ids` | `63d37fc5` | scalar | 0 | share of test rows whose ['loan_id', 'period'] also identify a row of train |
| `leakage.target_corr.max_single_feature_auc` | `1fe630dd` | scalar | 0.7238936567 | the AUC of the strongest single feature |
| `leakage.timing.n_flagged` | `742bcd24` | scalar | 0 | features declared during_period or after_outcome |
| `metrics.out_of_time.auc` | `6f2a2d99` | scalar | 0.7845616168 | auc on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.brier` | `40d244d4` | scalar | 0.0171279495 | brier on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.event_rate` | `83ccf5c0` | scalar | 0.01794892714 | event_rate on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.gini` | `890252d7` | scalar | 0.5691232337 | gini on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.ks` | `16d3e4fe` | scalar | 0.4321115953 | ks on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.logloss` | `2b7c9b2d` | scalar | 0.07975283787 | logloss on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.mean_predicted` | `3833e0c5` | scalar | 0.01886588953 | mean_predicted on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.n` | `7898809e` | scalar | 12257 | n on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.sub.incentive_high` | `6c7182e4` | table | table, 10 rows | every metric on the incentive above_median slice of out_of_time |
| `metrics.out_of_time.sub.incentive_high.auc_gap` | `1c0207f9` | scalar | 0.0373425714 | how far AUC on the incentive above_median slice of out_of_time falls below AUC on all of out_of_time |
| `metrics.out_of_time.sub.incentive_high.mean_rel_gap` | `f0899b32` | scalar | 0.123516925 | mean predicted against observed on the incentive above_median slice of out_of_time, relative |
| `metrics.out_of_time.sub.incentive_high.share` | `431d1ff2` | scalar | 0.499877621 | the share of out_of_time the incentive above_median slice holds |
| `metrics.out_of_time.sub.incentive_low` | `1ebd5e5e` | table | table, 10 rows | every metric on the incentive below_median slice of out_of_time |
| `metrics.out_of_time.sub.incentive_low.auc_gap` | `faa1a185` | scalar | 0.01629917634 | how far AUC on the incentive below_median slice of out_of_time falls below AUC on all of out_of_time |
| `metrics.out_of_time.sub.incentive_low.mean_rel_gap` | `81d9f6b7` | scalar | 0.2155153206 | mean predicted against observed on the incentive below_median slice of out_of_time, relative |
| `metrics.out_of_time.sub.incentive_low.share` | `c7aaafd2` | scalar | 0.500122379 | the share of out_of_time the incentive below_median slice holds |
| `metrics.test.auc` | `57066271` | scalar | 0.7752553922 | auc on test, recomputed by quaestor |
| `metrics.test.brier` | `7d3583cd` | scalar | 0.00789356705 | brier on test, recomputed by quaestor |
| `metrics.test.event_rate` | `570cc08a` | scalar | 0.008061370433 | event_rate on test, recomputed by quaestor |
| `metrics.test.gini` | `fe7f75d7` | scalar | 0.5505107844 | gini on test, recomputed by quaestor |
| `metrics.test.ks` | `c569c301` | scalar | 0.4161772354 | ks on test, recomputed by quaestor |
| `metrics.test.logloss` | `320e4c6b` | scalar | 0.04263297829 | logloss on test, recomputed by quaestor |
| `metrics.test.mean_predicted` | `3bc93911` | scalar | 0.008115821785 | mean_predicted on test, recomputed by quaestor |
| `metrics.test.n` | `e55953e1` | scalar | 15382 | n on test, recomputed by quaestor |
| `metrics.test.sub.incentive_high` | `142c806c` | table | table, 10 rows | every metric on the incentive above_median slice of test |
| `metrics.test.sub.incentive_high.auc_gap` | `5a0ba9c4` | scalar | 0.04840270693 | how far AUC on the incentive above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.incentive_high.mean_rel_gap` | `f90b2790` | scalar | 0.03491504769 | mean predicted against observed on the incentive above_median slice of test, relative |
| `metrics.test.sub.incentive_high.share` | `549aa934` | scalar | 0.5 | the share of test the incentive above_median slice holds |
| `metrics.test.sub.incentive_low` | `53406e16` | table | table, 10 rows | every metric on the incentive below_median slice of test |
| `metrics.test.sub.incentive_low.auc` | `0f9a3d96` | scalar | 0.6824295208 | auc on the incentive below_median slice of test |
| `metrics.test.sub.incentive_low.auc_gap` | `a0523ad8` | scalar | 0.09282587144 | how far AUC on the incentive below_median slice of test falls below AUC on all of test |
| `metrics.test.sub.incentive_low.mean_rel_gap` | `aede705c` | scalar | 0.1169064836 | mean predicted against observed on the incentive below_median slice of test, relative |
| `metrics.test.sub.incentive_low.share` | `1d5dd4c2` | scalar | 0.5 | the share of test the incentive below_median slice holds |
| `metrics.train.auc` | `fa609ae1` | scalar | 0.7883327303 | auc on train, recomputed by quaestor |
| `metrics.train.brier` | `83666c70` | scalar | 0.008317491392 | brier on train, recomputed by quaestor |
| `metrics.train.event_rate` | `b9ef3327` | scalar | 0.008524699414 | event_rate on train, recomputed by quaestor |
| `metrics.train.gini` | `0b6b2058` | scalar | 0.5766654607 | gini on train, recomputed by quaestor |
| `metrics.train.ks` | `c355478b` | scalar | 0.4562056834 | ks on train, recomputed by quaestor |
| `metrics.train.logloss` | `199c7db5` | scalar | 0.04408402922 | logloss on train, recomputed by quaestor |
| `metrics.train.mean_predicted` | `a63f6555` | scalar | 0.008426526894 | mean_predicted on train, recomputed by quaestor |
| `metrics.train.n` | `6fdfeabb` | scalar | 36013 | n on train, recomputed by quaestor |
| `metrics.train.sub.incentive_high` | `58071691` | table | table, 10 rows | every metric on the incentive above_median slice of train |
| `metrics.train.sub.incentive_high.auc_gap` | `8d8827f2` | scalar | 0.07015660217 | how far AUC on the incentive above_median slice of train falls below AUC on all of train |
| `metrics.train.sub.incentive_high.mean_rel_gap` | `7d3d3639` | scalar | 0.01445428336 | mean predicted against observed on the incentive above_median slice of train, relative |
| `metrics.train.sub.incentive_high.share` | `277218fb` | scalar | 0.4999861161 | the share of train the incentive above_median slice holds |
| `metrics.train.sub.incentive_low` | `9c590135` | table | table, 10 rows | every metric on the incentive below_median slice of train |
| `metrics.train.sub.incentive_low.auc_gap` | `134d7c07` | scalar | 0.06702950807 | how far AUC on the incentive below_median slice of train falls below AUC on all of train |
| `metrics.train.sub.incentive_low.mean_rel_gap` | `05adce6c` | scalar | 0.003953431529 | mean predicted against observed on the incentive below_median slice of train, relative |
| `metrics.train.sub.incentive_low.share` | `d7af12f0` | scalar | 0.5000138839 | the share of train the incentive below_median slice holds |
| `metrics.vintage_holdout.auc` | `ac6794c5` | scalar | 0.7717974135 | auc on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.brier` | `f3c6bdcc` | scalar | 0.004763025704 | brier on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.event_rate` | `e3590a16` | scalar | 0.004817105386 | event_rate on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.gini` | `a4a532f0` | scalar | 0.5435948269 | gini on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.ks` | `b5b9e888` | scalar | 0.4515647508 | ks on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.logloss` | `c32e3713` | scalar | 0.02810570342 | logloss on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.mean_predicted` | `5ae28866` | scalar | 0.005646788012 | mean_predicted on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.n` | `37a92951` | scalar | 32177 | n on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.sub.incentive_high` | `672368b3` | table | table, 10 rows | every metric on the incentive above_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.incentive_high.auc_gap` | `2ebd6757` | scalar | 0.01874804418 | how far AUC on the incentive above_median slice of vintage_holdout falls below AUC on all of vintage_holdout |
| `metrics.vintage_holdout.sub.incentive_high.event_rate` | `947de0ec` | scalar | 0.007396817504 | event_rate on the incentive above_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.incentive_high.mean_predicted` | `192eb7d4` | scalar | 0.009598098902 | mean_predicted on the incentive above_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.incentive_high.mean_rel_gap` | `d14397a7` | scalar | 0.2975984466 | mean predicted against observed on the incentive above_median slice of vintage_holdout, relative |
| `metrics.vintage_holdout.sub.incentive_high.share` | `cb627056` | scalar | 0.499984461 | the share of vintage_holdout the incentive above_median slice holds |
| `metrics.vintage_holdout.sub.incentive_low` | `10caac80` | table | table, 10 rows | every metric on the incentive below_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.incentive_low.auc` | `0510c841` | scalar | 0.6723509624 | auc on the incentive below_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.incentive_low.auc_gap` | `9de83338` | scalar | 0.09944645103 | how far AUC on the incentive below_median slice of vintage_holdout falls below AUC on all of vintage_holdout |
| `metrics.vintage_holdout.sub.incentive_low.mean_rel_gap` | `20691619` | scalar | 0.2421532582 | mean predicted against observed on the incentive below_median slice of vintage_holdout, relative |
| `metrics.vintage_holdout.sub.incentive_low.share` | `d94e6531` | scalar | 0.500015539 | the share of vintage_holdout the incentive below_median slice holds |
| `profile.out_of_time.missing.max` | `4dafce11` | scalar | 0 | the largest missing fraction in out_of_time |
| `profile.out_of_time.n` | `fa39c5cf` | scalar | 12257 | rows in out_of_time |
| `profile.test.missing.max` | `f813848d` | scalar | 0 | the largest missing fraction in test |
| `profile.test.n` | `e3abc1b8` | scalar | 15382 | rows in test |
| `profile.train.missing.max` | `050a3099` | scalar | 0 | the largest missing fraction in train |
| `profile.train.n` | `c5ebd9c9` | scalar | 36013 | rows in train |
| `profile.vintage_holdout.missing.max` | `329bb430` | scalar | 0 | the largest missing fraction in vintage_holdout |
| `profile.vintage_holdout.n` | `426e712a` | scalar | 32177 | rows in vintage_holdout |
| `psi.burnout` | `9dc7ecc2` | scalar | 0.004614338236 | PSI of burnout between train and test |
| `psi.credit_score` | `7e87527c` | scalar | 0.06188985797 | PSI of credit_score between train and test |
| `psi.incentive` | `2da5570f` | scalar | 0.0009922551416 | PSI of incentive between train and test |
| `psi.loan_age` | `2202b157` | scalar | 0.0001993816816 | PSI of loan_age between train and test |
| `psi.max` | `c2e8c8fd` | scalar | 0.06188985797 | the largest train-to-test PSI, score included |
| `psi.note_rate` | `ecc6adf3` | scalar | 0.01370911382 | PSI of note_rate between train and test |
| `psi.orig_ltv` | `cd1ff136` | scalar | 0.03617297258 | PSI of orig_ltv between train and test |
| `psi.orig_upb_log` | `55030a3b` | scalar | 0.04817081196 | PSI of orig_upb_log between train and test |
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
| `psi.out_of_time.y_score` | `2dc61374` | scalar | 0.7055906656 | PSI of the score between train and out_of_time |
| `psi.sato` | `584da64f` | scalar | 0.02772829856 | PSI of sato between train and test |
| `psi.season_cos` | `addec503` | scalar | 1.790085913e-05 | PSI of season_cos between train and test |
| `psi.season_sin` | `4d2ed98d` | scalar | 2.939045338e-06 | PSI of season_sin between train and test |
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
| `psi.vintage_holdout.y_score` | `3713457e` | scalar | 0.142110315 | PSI of the score between train and vintage_holdout |
| `psi.y_score` | `3b9dee2d` | scalar | 0.001952903716 | PSI of the score between train and test |
| `run.features` | `61276a96` | json | json | the subject's features.json |
| `run.model_summary` | `b764932a` | json | json | the subject's model_summary.json |
| `run.projection` | `cbc0b707` | json | json | the subject's projection.json |
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |
| `scenario.convexity` | `6d2d7838` | scalar | 336109.4903 | the value change at -300 bp plus the change at 300 bp; negative when the fall outweighs the rise |
| `scenario.value_by_shock` | `89c9bef7` | table | table, 7 rows | servicing value, its change from the base case and first-year CPR, by shock |
| `scenario.value_change.-100` | `d33e8e3c` | scalar | -322648.7678 | change in servicing value at -100 bp |
| `scenario.value_change.-200` | `03816874` | scalar | -854265.8614 | change in servicing value at -200 bp |
| `scenario.value_change.-300` | `e1211d5d` | scalar | 168054.7452 | change in servicing value at -300 bp |
| `scenario.value_change.0` | `1e1b0b88` | scalar | 0 | change in servicing value at 0 bp |
| `scenario.value_change.100` | `d0970bd9` | scalar | 119555.7352 | change in servicing value at 100 bp |
| `scenario.value_change.200` | `d69c2be1` | scalar | 156987.0553 | change in servicing value at 200 bp |
| `scenario.value_change.300` | `38e75872` | scalar | 168054.7452 | change in servicing value at 300 bp |
| `sign_check.burnout.agrees` | `2eec20ab` | scalar | 1 | 1 when the fitted sign on burnout agrees with its univariate direction, 0 when it does not |
| `sign_check.burnout.coef_sign` | `a3063608` | scalar | 1 | the sign of the fitted coefficient on burnout |
| `sign_check.burnout.univariate_direction` | `bfc96bb2` | scalar | 1 | the sign of burnout's own single-feature AUC on train minus 0.5 |
| `sign_check.credit_score.agrees` | `915bf8eb` | scalar | 1 | 1 when the fitted sign on credit_score agrees with its univariate direction, 0 when it does not |
| `sign_check.credit_score.coef_sign` | `1ec1078b` | scalar | 1 | the sign of the fitted coefficient on credit_score |
| `sign_check.credit_score.univariate_direction` | `42303896` | scalar | 1 | the sign of credit_score's own single-feature AUC on train minus 0.5 |
| `sign_check.incentive.agrees` | `f7b2338e` | scalar | 1 | 1 when the fitted sign on incentive agrees with its univariate direction, 0 when it does not |
| `sign_check.incentive.coef_sign` | `684cf11a` | scalar | 1 | the sign of the fitted coefficient on incentive |
| `sign_check.incentive.univariate_direction` | `8098d951` | scalar | 1 | the sign of incentive's own single-feature AUC on train minus 0.5 |
| `sign_check.n_disagreements` | `f96ece96` | scalar | 1 | retained features whose fitted sign contradicts their univariate direction, of 9 checked |
| `sign_check.note_rate.agrees` | `a453463d` | scalar | 0 | 1 when the fitted sign on note_rate agrees with its univariate direction, 0 when it does not |
| `sign_check.note_rate.coef_sign` | `aecf7ccb` | scalar | -1 | the sign of the fitted coefficient on note_rate |
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
| `sign_check.season_sin.agrees` | `e110f357` | scalar | 1 | 1 when the fitted sign on season_sin agrees with its univariate direction, 0 when it does not |
| `sign_check.season_sin.coef_sign` | `761188ce` | scalar | 1 | the sign of the fitted coefficient on season_sin |
| `sign_check.season_sin.univariate_direction` | `cae6b096` | scalar | 1 | the sign of season_sin's own single-feature AUC on train minus 0.5 |
| `stability.auc_by_regime` | `960f708f` | table | table, 2 rows | the champion's AUC within each rate_regime on train |
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
| `threshold.O1.slice_auc_gap` | `0a827b87` | scalar | 0.08 | how far a sub-population's AUC may fall below the split's before the result is an open item; it raises no candidate |
| `threshold.O1.slice_max_share` | `a928a05c` | scalar | 0.95 | the share of a split at which a sub-population is the whole split and is refused |
| `threshold.O1.slice_min_share` | `9a6f1a87` | scalar | 0.1 | the share of a split a sub-population must hold before it can raise an open item |
| `threshold.R1.auc_gap` | `b64213d7` | scalar | 0.1 | R1: the AUC difference across regimes |
| `threshold.R1.sign_flip_coef` | `aca84377` | scalar | 0.05 | R1: the coefficient a sign flip must exceed in both regimes |
| `threshold.R1.sign_flip_z` | `2e4428c7` | scalar | 2 | R1: the \|z\| a sign flip's coefficient must reach in both regimes |
| `threshold.S1.psi` | `278b9016` | scalar | 0.25 | S1: the population stability index, train against test |
| `threshold.package.auc.test.min` | `fececac1` | scalar | 0.65 | package.yaml declares auc min 0.65 |
| `threshold.package.calibration_slope.test.max` | `0adb7a89` | scalar | 1.2 | package.yaml declares calibration_slope max 1.2 |
| `threshold.package.calibration_slope.test.min` | `95fdb848` | scalar | 0.8 | package.yaml declares calibration_slope min 0.8 |
| `threshold.package.psi.max` | `fbb5a9d1` | scalar | 0.25 | package.yaml declares psi max 0.25 |
| `thresholds.evaluation` | `f71ddec9` | table | table, 4 rows | every threshold package.yaml declares, with its bound, the recomputed value and the outcome |
| `vif.burnout` | `88879cb2` | scalar | 3.439328594 | variance inflation factor of burnout on train |
| `vif.credit_score` | `f05d536a` | scalar | 1.007978309 | variance inflation factor of credit_score on train |
| `vif.incentive` | `2da1b19c` | scalar | 2.22632259 | variance inflation factor of incentive on train |
| `vif.loan_age` | `5573d536` | scalar | 2.928871763 | variance inflation factor of loan_age on train |
| `vif.max` | `f9e0db60` | scalar | 4.975500767 | the largest variance inflation factor |
| `vif.note_rate` | `37532fa8` | scalar | 4.975500767 | variance inflation factor of note_rate on train |
| `vif.orig_ltv` | `65b35f3b` | scalar | 1.004506143 | variance inflation factor of orig_ltv on train |
| `vif.orig_upb_log` | `24f8e4d1` | scalar | 1.005846447 | variance inflation factor of orig_upb_log on train |
| `vif.sato` | `a6c55fce` | scalar | 1.71256814 | variance inflation factor of sato on train |
| `vif.season_cos` | `a9cfa7eb` | scalar | 1.017653349 | variance inflation factor of season_cos on train |
| `vif.season_sin` | `669c5fcb` | scalar | 1.004128844 | variance inflation factor of season_sin on train |

## Appendix C — Run trace summary

| quantity | value |
|---|---|
| tool calls | 18 (run_model 1, profile_data 1, compute_metrics 3, check_leakage 1, check_stability 1, check_collinearity 1, challenger_compare 1, run_scenarios 2, retrieve_guidance 7) |
| plan steps (bounded loop) | 4 |
| LLM calls | 20 (plan 4, draft 8, extract 8) |
| re-asks | 0 |
| repair rounds | 1 |
| tokens in / out | 266,985 / 116,862 |
| notional cost (USD) | 5.6529 |
| wall-clock (s) | 1236.31 |
| subject run (s) | 2.94 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | msr_prepayment-full_agent-20260920T202713Z-e61d346a |

## Appendix D — Not checked

| item | reason |
|---|---|
| developer claims (T1, claim channel) | The package declares 3 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
