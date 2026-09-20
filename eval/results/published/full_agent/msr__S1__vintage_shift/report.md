---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: msr_prepayment
version: "1.0"
model_type: discrete_time_hazard
configuration: full_agent
model: claude-opus-5[1m]
run_id: msr_prepayment-full_agent-20260920T200607Z-e61d346a
data_mode: synthetic
synthetic_n: 2000
grounding_precision_pre: 0.9940
grounding_precision_post: 1.0000
n_claims: 334
n_findings_by_severity: {high: 1, medium: 2, low: 0, info: 0}
generated: "2026-09-20T20:06:07Z"
illustrative: false
---

# Validation report — `msr_prepayment` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `msr_prepayment` v1.0 | `full_agent` | claude-opus-5[1m] | synthetic, n = 2000 | 0.9940 → 1.0000 | 1 / 2 / 0 / 0 |
<!-- quaestor:renderer:end -->

This report records the independent validation of the model package msr_prepayment version 1.0, a loan-level model whose output is the probability of prepayment, and it follows the validation framework set out in supervisory guidance [[reg:SR26-2:V]].
The subject was re-executed end to end from the developer's package under the wall-clock cap it declares, 300 seconds [[art:2ad8d1a5:runtime.max_seconds]], and the performance figures cited here were recomputed by this validation from the subject's own predictions rather than carried over from the developer's report.
Outcomes analysis was performed on each split the package defines, comparing recomputed model output to realised outcomes in the manner the guidance describes [[reg:SR26-2:V.1.b]].
The training split holds 33522 rows [[art:60d3a086:profile.train.n]] and the test split holds 12257 rows [[art:3b91ffcc:profile.test.n]].
The out-of-time split holds 12257 rows [[art:7898809e:metrics.out_of_time.n]] and the vintage holdout holds 32177 rows [[art:37a92951:metrics.vintage_holdout.n]].
On the headline result, discrimination on the test split at 0.7846 [[art:d57b2552:metrics.test.auc]] sits above the developer-declared floor of 0.65 [[art:fececac1:threshold.package.auc.test.min]], so that declared bound is met.
The calibration slope on the test split at 0.9369 [[art:290cccd9:calibration_slope.test]] sits inside the developer-declared band running from a lower bound of 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] to an upper bound of 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]], so that declared bound is met on both sides.
The remaining declared bounds, and the behaviour that drew the findings named below, are set out with their evidence in the sections that follow.
This validation raised F-001, a T1 declared threshold finding at high severity.
It raised F-002, a S1 population drift finding at medium severity.
It raised F-003, a C1 calibration finding at medium severity.
Each of those is written out in full, with the evidence behind it and the action it calls for, in section 6.

## 2. Conceptual soundness

Assessing conceptual soundness means assessing and documenting the model's design, its construction and its developmental testing, and subjecting the modeling choices to critical analysis by weighing the quality and extent of the developmental evidence [[reg:SR26-2:V.1.a]].

### Design and inputs

The champion is a prepayment model estimated on loan-month observations and linear in the log-odds, with an intercept of -5.517 [[art:cf58dded:run.model_summary#intercept]], a spline basis in loan age, and the remaining covariates entering linearly.
It was fitted on 33522 [[art:cf58dded:run.model_summary#n_train]] loan-month rows drawn from 667 [[art:cf58dded:run.model_summary#n_train_loans]] distinct loans, so the effective cross-sectional width of the training sample is much narrower than the row count suggests.
The specification retains 12 [[art:61276a96:run.features#n]] features.
By timing, 5 [[art:61276a96:run.features#at_origination]] are known at origination and 7 [[art:61276a96:run.features#before_period_start]] are known before the start of the period being predicted.
Features observed during the prediction period number 0 [[art:61276a96:run.features#during_period]], and features observed after the outcome number 0 [[art:61276a96:run.features#after_outcome]].
On the timing evidence as presented, every input is available at or before the moment the model is asked to predict, which is what a forward-looking prepayment model requires and which removes the most common route to lookahead.

### The developer's own screen

The developer applied a collinearity screen with a cutoff of 10 [[art:cf58dded:run.model_summary#vif_threshold]] on the variance inflation factor and dropped two inputs on it.
A trailing rate-change feature was removed at a variance inflation of 11.98 [[art:cf58dded:run.model_summary#removed.rate_change_12m.vif]], which sits just above that cutoff.
A log beginning-of-month balance feature was removed at 39120 [[art:cf58dded:run.model_summary#removed.bom_balance_log.vif]], by a wide margin the larger of the two and a level that indicates near-exact linear dependence on other retained inputs.
Both removals are defensible on their face: a trailing rate change overlaps heavily with the retained refinance-incentive term, and a log beginning-of-month balance overlaps with the retained log original balance and the loan-age basis.
The screen is a coefficient-stability device rather than a predictive one, so its use here is consistent with an interpretable specification whose coefficient signs are meant to be read.

### Coefficients and expected signs

The refinance incentive carries the largest coefficient in magnitude at 1.18 [[art:cf58dded:run.model_summary#coefficients.incentive.value]], positive, which is what prepayment subject matter expects: the deeper a borrower is in the money, the more likely they refinance.
The leading loan-age spline term is 0.6271 [[art:cf58dded:run.model_summary#coefficients.loan_age_spline_1.value]] and the trailing one is -0.4007 [[art:cf58dded:run.model_summary#coefficients.loan_age_spline_4.value]], with intermediate terms of 0.1035 [[art:cf58dded:run.model_summary#coefficients.loan_age_spline_2.value]] and -0.08673 [[art:cf58dded:run.model_summary#coefficients.loan_age_spline_3.value]], a rise-then-decline shape in age that matches the usual seasoning ramp followed by decay.
Credit score enters at 0.4228 [[art:cf58dded:run.model_summary#coefficients.credit_score.value]], positive, consistent with stronger borrowers being better able to qualify for a refinance.
Original loan-to-value enters at -0.2265 [[art:cf58dded:run.model_summary#coefficients.orig_ltv.value]], negative, consistent with thinner equity impeding a refinance.
Log original balance enters at 0.3277 [[art:cf58dded:run.model_summary#coefficients.orig_upb_log.value]], positive, consistent with larger balances making the fixed cost of refinancing worth paying.
The note rate enters at -0.522 [[art:cf58dded:run.model_summary#coefficients.note_rate.value]], negative, which is not the direction subject matter would expect from a rate variable in isolation, and is discussed below.
Burnout enters at 0.1918 [[art:cf58dded:run.model_summary#coefficients.burnout.value]], positive, whereas the conventional prior is that accumulated exposure to refinance opportunity dampens rather than raises the remaining pool's propensity to prepay; the sign is worth the developer's explanation even though it matches this feature's own univariate direction.
The seasonal pair enters at 0.1129 [[art:cf58dded:run.model_summary#coefficients.season_sin.value]] and -0.1391 [[art:cf58dded:run.model_summary#coefficients.season_cos.value]], and the spread at origination at 0.01832 [[art:cf58dded:run.model_summary#coefficients.sato.value]], the smallest in magnitude of the fitted coefficients.

### Sign agreement and what each feature carries

The count of retained features whose fitted sign contradicts their own univariate direction is 1 [[art:f96ece96:sign_check.n_disagreements]], and that feature is the note rate.
Its fitted coefficient sign is -1 [[art:aecf7ccb:sign_check.note_rate.coef_sign]] while its univariate direction on train is 1 [[art:61f6e1ac:sign_check.note_rate.univariate_direction]], so agreement is recorded as 0 [[art:a453463d:sign_check.note_rate.agrees]].
The natural reading is conditioning: with the refinance incentive already in the specification, the note rate is left to carry a residual effect whose direction need not follow its raw relationship with prepayment.
The weight to put on the disagreement is set by what the model draws from the feature, and refitting the champion's form without the note rate changes test AUC by 0.005792 [[art:338b461a:ablation.note_rate.delta_auc]], a positive change, meaning discrimination did not fall when it was dropped.
A sign flip on a term the fitted model is not using for discrimination is a weaker concern than the same flip on a load-bearing term, and this is the former.

Every other checked feature agrees with its univariate direction: the refinance incentive at 1 [[art:f7b2338e:sign_check.incentive.agrees]], credit score at 1 [[art:915bf8eb:sign_check.credit_score.agrees]], original loan-to-value at 1 [[art:7021aeb0:sign_check.orig_ltv.agrees]], log original balance at 1 [[art:07a9d3e6:sign_check.orig_upb_log.agrees]], burnout at 1 [[art:2eec20ab:sign_check.burnout.agrees]], the spread at origination at 1 [[art:2401eba2:sign_check.sato.agrees]], and the two seasonal terms at 1 [[art:e110f357:sign_check.season_sin.agrees]] and 1 [[art:7f18ddf7:sign_check.season_cos.agrees]].
The fitted and univariate signs behind those agreements run positive for the incentive at 1 [[art:684cf11a:sign_check.incentive.coef_sign]] and 1 [[art:8098d951:sign_check.incentive.univariate_direction]], positive for credit score at 1 [[art:1ec1078b:sign_check.credit_score.coef_sign]] and 1 [[art:42303896:sign_check.credit_score.univariate_direction]], negative for original loan-to-value at -1 [[art:7eec65ec:sign_check.orig_ltv.coef_sign]] and -1 [[art:76dbc708:sign_check.orig_ltv.univariate_direction]], positive for log original balance at 1 [[art:5aa309fc:sign_check.orig_upb_log.coef_sign]] and 1 [[art:b9743ecb:sign_check.orig_upb_log.univariate_direction]], positive for burnout at 1 [[art:a3063608:sign_check.burnout.coef_sign]] and 1 [[art:bfc96bb2:sign_check.burnout.univariate_direction]], positive for the spread at origination at 1 [[art:c031d0d5:sign_check.sato.coef_sign]] and 1 [[art:c08233a6:sign_check.sato.univariate_direction]], and for the seasonal pair 1 [[art:761188ce:sign_check.season_sin.coef_sign]] with 1 [[art:cae6b096:sign_check.season_sin.univariate_direction]] and -1 [[art:7dbb1ffc:sign_check.season_cos.coef_sign]] with -1 [[art:03e931f0:sign_check.season_cos.univariate_direction]].

The leave-one-out refits are measured from a refit of the champion's form on every retained feature, which scores 0.7802 [[art:93dda83a:ablation.baseline_auc]] on test, a level slightly below the champion's own recomputed test discrimination of 0.7846 [[art:d57b2552:metrics.test.auc]].
Dropping the refinance incentive changes test AUC by -0.07943 [[art:46802ce1:ablation.incentive.delta_auc]], the largest loss of any single feature and the one the specification most depends on.
Dropping credit score changes it by -0.0298 [[art:a2d10cd7:ablation.credit_score.delta_auc]], log original balance by -0.01681 [[art:6158bf75:ablation.orig_upb_log.delta_auc]], original loan-to-value by -0.01199 [[art:84275e57:ablation.orig_ltv.delta_auc]], loan age by -0.009946 [[art:ca8fa8e9:ablation.loan_age.delta_auc]], the cosine seasonal term by -0.005672 [[art:bdbbba37:ablation.season_cos.delta_auc]] and the spread at origination by -0.004237 [[art:c9eb03ef:ablation.sato.delta_auc]], all negative and so all carrying some discrimination.
Dropping burnout changes it by 0.004292 [[art:8aa8bccf:ablation.burnout.delta_auc]] and dropping the sine seasonal term by 0.00054 [[art:95e1e0c6:ablation.season_sin.delta_auc]], both positive, so neither was contributing discrimination on test in the presence of the rest.
Taken together the design concentrates its discriminatory content in the refinance incentive with credit score second, which is where a prepayment model's economics say it should sit, and the terms whose direction is open to question are the ones the fitted model leans on least.

### Effective challenge

The challenger scores 0.7211 [[art:489cd7a6:challenger.auc]] on test against the champion's recomputed 0.7846 [[art:d57b2552:metrics.test.auc]], and the challenger's discrimination minus the champion's is -0.06356 [[art:7e119a34:challenger.delta_auc]].
The declared decision rule turns on the challenger's lead over the champion, set at 0.03 [[art:e042774c:threshold.E1.delta_auc]], so a lead of that size or more would be the signal that the alternative approach beats the incumbent by an amount worth acting on.
The reported difference is negative, meaning the challenger trails rather than leads, and so the difference between the two does not meet the condition under which it would matter for the champion's standing.
Calibration points the same way: the champion's test Brier score of 0.01725 [[art:68e8b1cf:metrics.test.brier]] is below the challenger's 0.02173 [[art:36aa75c4:challenger.brier]], meaning the champion's probabilities are the more accurate of the two on that measure.
The benchmark therefore supports the champion's specification rather than displacing it, which is the kind of benchmarking-to-other-models evidence that conceptual soundness review is meant to weigh [[reg:SR26-2:V.1.a]].

### Assessment

The design is coherent with the economics of prepayment: the inputs are all available before the predicted period, the collinearity screen removed terms that duplicated retained ones, the dominant coefficient and the largest ablation loss are both on the refinance incentive, and the loan-age basis traces the expected seasoning shape.
The two points a reader should hold open are the single fitted sign that contradicts its univariate direction, on a feature whose removal did not cost discrimination, and the positive burnout coefficient, which agrees with its own univariate direction but runs against the conventional prior and would benefit from the developer's written rationale.
Neither point is raised as a finding in this report, and no finding is raised against the champion's functional form here.

## 3. Data integrity and drift

Model testing includes a critical assessment of data quality, relevance, and inputs, and this section reviews the package's missingness, stability, and leakage evidence on those terms. [[reg:SR26-2:IV.1]]

### Missingness across the splits

The training split holds 33522 [[art:60d3a086:profile.train.n]] rows, the test split 12257 [[art:3b91ffcc:profile.test.n]], the out-of-time split 12257 [[art:fa39c5cf:profile.out_of_time.n]], and the vintage holdout 32177 [[art:426e712a:profile.vintage_holdout.n]].
The largest missing fraction on any column of the training split is 0 [[art:050a3099:profile.train.missing.max]].
The largest missing fraction in the test split is 0 [[art:f813848d:profile.test.missing.max]], in the out-of-time split 0 [[art:4dafce11:profile.out_of_time.missing.max]], and in the vintage holdout 0 [[art:329bb430:profile.vintage_holdout.missing.max]].
Comparing the splits by the difference between these largest missing fractions rather than by their ratio, every split stands at the same value, so the separation between any pair of splits stays below the declared missingness-gap bound of 0.1 [[art:9cce25ea:threshold.D1.missing_gap]].
On this screen the data pass, and the ratio comparison is degenerate here because the splits do not differ on the quantity being compared.

### Population stability, train against the other splits

The declared stability bound is 0.25 [[art:278b9016:threshold.S1.psi]], and the package declaration carries the same bound at 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
The largest train-to-test population stability index, the score included, is 3.016 [[art:4fae32c6:psi.max]], well above that bound.
It falls on burnout, whose train-to-test index is 3.016 [[art:1d35a583:psi.burnout]].
Loan age follows at 1.68 [[art:987aabe4:psi.loan_age]], note rate at 1.342 [[art:2f1cb70b:psi.note_rate]], and incentive at 0.8734 [[art:0f61188c:psi.incentive]], each above the declared bound of 0.25 [[art:278b9016:threshold.S1.psi]].
The score itself shifts by 0.8372 [[art:92ac1652:psi.y_score]] between train and test, also above that bound.
The remaining train-to-test indices sit below it: orig UPB log at 0.08171 [[art:f075546d:psi.orig_upb_log]], credit score at 0.07088 [[art:91c4ab83:psi.credit_score]], orig LTV at 0.04332 [[art:85842fd0:psi.orig_ltv]], SATO at 0.02284 [[art:4809116c:psi.sato]], seasonal sine at 0.01631 [[art:46fec014:psi.season_sin]], and seasonal cosine at 0.004988 [[art:62ae6c81:psi.season_cos]].
The out-of-time split reproduces this pattern feature by feature: burnout at 3.016 [[art:8cedaf79:psi.out_of_time.burnout]], loan age at 1.68 [[art:ab2af3f2:psi.out_of_time.loan_age]], note rate at 1.342 [[art:fc610fd1:psi.out_of_time.note_rate]], incentive at 0.8734 [[art:ec6da34d:psi.out_of_time.incentive]], and the score at 0.8372 [[art:d39a4ced:psi.out_of_time.y_score]], all above the declared bound of 0.25 [[art:278b9016:threshold.S1.psi]].
The quieter out-of-time features stay below that bound: orig UPB log at 0.08171 [[art:9ca9c306:psi.out_of_time.orig_upb_log]], credit score at 0.07088 [[art:a7ef717f:psi.out_of_time.credit_score]], orig LTV at 0.04332 [[art:7eedf98f:psi.out_of_time.orig_ltv]], SATO at 0.02284 [[art:79f6f94a:psi.out_of_time.sato]], seasonal sine at 0.01631 [[art:fe2b0197:psi.out_of_time.season_sin]], and seasonal cosine at 0.004988 [[art:ef947d09:psi.out_of_time.season_cos]].
These out-of-time breaches are read against the same declared bound of 0.25 [[art:278b9016:threshold.S1.psi]] and are carried forward as open items rather than reported here as findings.
The vintage holdout behaves differently, with every comparison below the declared bound: note rate at 0.2743 [[art:d4e6aa9a:psi.vintage_holdout.note_rate]] is the largest feature shift, followed by incentive at 0.2101 [[art:1d339225:psi.vintage_holdout.incentive]], the score at 0.08202 [[art:5d010092:psi.vintage_holdout.y_score]], orig LTV at 0.03575 [[art:1f0e3df0:psi.vintage_holdout.orig_ltv]], loan age at 0.03489 [[art:e579422e:psi.vintage_holdout.loan_age]], burnout at 0.03122 [[art:b2dacb71:psi.vintage_holdout.burnout]], orig UPB log at 0.03038 [[art:10fd298a:psi.vintage_holdout.orig_upb_log]], SATO at 0.02841 [[art:6c4e561c:psi.vintage_holdout.sato]], credit score at 0.01929 [[art:16906529:psi.vintage_holdout.credit_score]], seasonal cosine at 0.00164 [[art:4482dc21:psi.vintage_holdout.season_cos]], and seasonal sine at 0.001971 [[art:836b68bf:psi.vintage_holdout.season_sin]].
Note rate at 0.2743 [[art:d4e6aa9a:psi.vintage_holdout.note_rate]] sits above the declared bound of 0.25 [[art:278b9016:threshold.S1.psi]] and is the one vintage-holdout comparison that does so.
The contrast is directional and material: the same features that shift hardest between train and test also shift hardest between train and out-of-time, while the vintage holdout resembles the training population far more closely on burnout and loan age in particular.

### Characteristic stability

Incentive contributes the largest characteristic shift in the linear predictor at 0.9221 [[art:f430cc2d:csi.incentive]], which is also the largest characteristic stability index overall at 0.9221 [[art:d4b08859:csi.max]].
Note rate contributes 0.4832 [[art:a2be3f30:csi.note_rate]] and burnout 0.3489 [[art:e0f86ff2:csi.burnout]], both above the declared stability bound of 0.25 [[art:278b9016:threshold.S1.psi]].
The remaining contributions are smaller: credit score at 0.09087 [[art:4fbc434e:csi.credit_score]], orig UPB log at 0.06562 [[art:ba82e949:csi.orig_upb_log]], orig LTV at 0.02303 [[art:af80429c:csi.orig_ltv]], seasonal sine at 0.01316 [[art:ff10caf4:csi.season_sin]], seasonal cosine at 0.003265 [[art:49e6d56e:csi.season_cos]], SATO at 0.0001468 [[art:7d563a3f:csi.sato]], and loan age at 0 [[art:df52c920:csi.loan_age]].
Loan age is instructive: its population shift between train and test is large at 1.68 [[art:987aabe4:psi.loan_age]] while its contribution to the shift in the linear predictor is 0 [[art:df52c920:csi.loan_age]], so the distributional movement there does not translate into movement of the score.
Incentive runs the other way, with a population shift of 0.8734 [[art:0f61188c:psi.incentive]] and the largest characteristic contribution at 0.9221 [[art:f430cc2d:csi.incentive]].

### Leakage and contamination screens

The count of features declared as observed during the performance period or after the outcome is 0 [[art:742bcd24:leakage.timing.n_flagged]], so no declared timing violates the intended information set.
The strongest single feature reaches an AUC of 0.7422 [[art:b6b29a14:leakage.target_corr.max_single_feature_auc]], below the bound of 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]] that any one feature may reach on its own.
The share of test rows whose feature values also appear in train is 0 [[art:4c9fcd09:leakage.overlap]].
The identifier arm of the contamination screen, the share of test rows whose loan and period keys also identify a training row, is 0 [[art:63d37fc5:leakage.overlap.ids]], below the declared overlap bound of 0.005 [[art:9f336eaf:threshold.L2.overlap]].
The feature-vector arm is read against its own bound rather than the declared one, because two distinct subjects writing the same discrete row is coincidence rather than contamination.
The share of training rows whose feature values are not unique within train is 0 [[art:4474c227:leakage.duplicates.train]], so the bound the feature-overlap rule applied is the declared one, at 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].
The feature-vector overlap is 0 [[art:0fec8048:leakage.overlap.features]], below that applied bound of 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].
The number of feature names matching the target-adjacent lexicon is 0 [[art:407e62be:leakage.name_screen.n_matched]], so the name screen raises nothing.
Taken together, the leakage screens are clean on every arm evaluated here.

### Assessment

One finding is raised in this section, S1, population drift at medium severity: the train-to-test population stability index on burnout is 3.016 [[art:1d35a583:psi.burnout]] against a declared bound of 0.25 [[art:278b9016:threshold.S1.psi]], and it is not the only comparison to breach that bound.
Missingness and the full set of leakage screens sit within their declared bounds, so the data-integrity risk in this package concentrates in population and characteristic drift rather than in contamination or data completeness.
The vintage holdout is the split closest to the training population, and the drift evidence should condition how much weight the test and out-of-time results in later sections are allowed to carry.

## 4. Outcomes analysis

Outcomes analysis compares model outputs to the corresponding real-world outcomes, and where results fall persistently outside established performance thresholds, adjustment, recalibration, or redevelopment may be warranted [[reg:SR26-2:V.1.b]].
This section reports calibration before discrimination.
The reason is the declared use: package.yaml declares that this model's output is consumed as a probability and not only as a ranking, so the leading question is whether the probabilities mean what they say, and that question leads whatever the event rate turns out to be.

### Calibration

The calibration slope, from the logistic regression of the outcome on the logit of the predicted probability, is 1.015 [[art:6ee05ed8:calibration_slope.train]] on train, 0.9369 [[art:290cccd9:calibration_slope.test]] on test, 0.9369 [[art:994798d5:calibration_slope.out_of_time]] out of time and 0.8554 [[art:6b42345a:calibration_slope.vintage_holdout]] on the vintage holdout.
Each of those slopes sits inside the declared band running from 0.8 [[art:749634ae:threshold.C1.calibration_slope.min]] to 1.2 [[art:b6672579:threshold.C1.calibration_slope.max]], with the vintage holdout the closest of the four to the lower edge.
The intercept of the same regression is 0.06177 [[art:7184b1c0:calibration_intercept.train]] on train, -0.4556 [[art:256e21c4:calibration_intercept.test]] on test, -0.4556 [[art:8dc58882:calibration_intercept.out_of_time]] out of time and -0.8976 [[art:21c5b98a:calibration_intercept.vintage_holdout]] on the vintage holdout, so the level shift on the held-out splits runs in the direction of over-prediction while the slope stays near unity.
Mean predicted probability against the observed rate is 0.008333 [[art:4ea7b930:metrics.train.mean_predicted]] against 0.008323 [[art:b0cf2348:metrics.train.event_rate]] on train.
On test it is 0.02283 [[art:1c1a1d8d:metrics.test.mean_predicted]] against 0.01795 [[art:d222aedf:metrics.test.event_rate]].
Out of time it is 0.02283 [[art:4d7aa98b:metrics.out_of_time.mean_predicted]] against 0.01795 [[art:83ccf5c0:metrics.out_of_time.event_rate]].
On the vintage holdout it is 0.006157 [[art:914aeeba:metrics.vintage_holdout.mean_predicted]] against 0.004817 [[art:e3590a16:metrics.vintage_holdout.event_rate]].
Expressed relative to the observed rate, that gap is 0.001197 [[art:7d19dc79:calibration.mean_rel_gap.train]] on train, which is below the declared tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
On test the relative gap is 0.2718 [[art:04dcea16:calibration.mean_rel_gap.test]], above that tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]], and this exceedance is a finding of the validation.
Out of time the relative gap is 0.2718 [[art:c5239af4:calibration.mean_rel_gap.out_of_time]], likewise above the tolerance, and it too is a finding.
On the vintage holdout the relative gap is 0.2782 [[art:2eba48c2:calibration.mean_rel_gap.vintage_holdout]], the largest of the four and also above the tolerance, and it is a finding as well.
The decile view of predicted probability against realized outcome on test is reproduced below.

<!-- quaestor:renderer:begin table calibration.test -->
Calibration by decile of predicted probability on test [[art:07848a4c:calibration.test]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.001873 | 0 | 1226 |
| 2 | 0.003677 | 0.002447 | 1226 |
| 3 | 0.005318 | 0.002447 | 1226 |
| 4 | 0.007303 | 0.0106 | 1226 |
| 5 | 0.009752 | 0.009788 | 1226 |
| 6 | 0.01306 | 0.01223 | 1226 |
| 7 | 0.01816 | 0.01142 | 1226 |
| 8 | 0.02727 | 0.02694 | 1225 |
| 9 | 0.04395 | 0.02857 | 1225 |
| 10 | 0.09799 | 0.0751 | 1225 |
<!-- quaestor:renderer:end -->

Against realized prepayment speeds, the mean absolute difference between actual and predicted CPR is 0.03373 [[art:609b1f19:cpr.train.mae]] on train, 0.06724 [[art:fe0e020a:cpr.test.mae]] on test, 0.06724 [[art:ed058023:cpr.out_of_time.mae]] out of time and 0.03062 [[art:10b5118d:cpr.vintage_holdout.mae]] on the vintage holdout.

<!-- quaestor:renderer:begin table cpr.test -->
Actual against predicted CPR by period on test [[art:81cf8976:cpr.test]]:

| period | n | actual_cpr | predicted_cpr |
|---|---|---|---|
| 202001 | 515 | 0 | 0.04662 |
| 202002 | 515 | 0.04562 | 0.05737 |
| 202003 | 513 | 0 | 0.06594 |
| 202004 | 513 | 0.08966 | 0.09018 |
| 202005 | 509 | 0.06848 | 0.09956 |
| 202006 | 506 | 0.1539 | 0.1084 |
| 202007 | 499 | 0.1962 | 0.09795 |
| 202008 | 490 | 0.1158 | 0.09853 |
| 202009 | 485 | 0.04838 | 0.1064 |
| 202010 | 483 | 0.222 | 0.1265 |
| 202011 | 473 | 0.246 | 0.1732 |
| 202012 | 462 | 0.1674 | 0.2402 |
| 202101 | 455 | 0.2938 | 0.3149 |
| 202102 | 442 | 0.3204 | 0.4631 |
| 202103 | 428 | 0.3669 | 0.5622 |
| 202104 | 412 | 0.5703 | 0.6164 |
| 202105 | 384 | 0.539 | 0.6034 |
| 202106 | 360 | 0.5308 | 0.5455 |
| 202107 | 338 | 0.4412 | 0.466 |
| 202108 | 322 | 0.1712 | 0.3364 |
| 202109 | 317 | 0.1737 | 0.2921 |
| 202110 | 312 | 0.03779 | 0.2473 |
| 202111 | 311 | 0.0745 | 0.2087 |
| 202112 | 309 | 0.1105 | 0.2077 |
| 202201 | 306 | 0.1115 | 0.1809 |
| 202202 | 272 | 0.08475 | 0.1934 |
| 202203 | 244 | 0.04809 | 0.1364 |
| 202204 | 221 | 0.1513 | 0.113 |
| 202205 | 194 | 0 | 0.08172 |
| 202206 | 167 | 0.06954 | 0.05779 |
| 202207 | 145 | 0.07969 | 0.03948 |
| 202208 | 119 | 0 | 0.03001 |
| 202209 | 98 | 0 | 0.02484 |
| 202210 | 68 | 0 | 0.02792 |
| 202211 | 45 | 0 | 0.02572 |
| 202212 | 25 | 0 | 0.02416 |
<!-- quaestor:renderer:end -->

### Discrimination

The recomputed metrics by split are set out one row per metric below, each cell carrying its own citation.

| Metric | Train | Test | Out-of-time | Vintage holdout |
| --- | --- | --- | --- | --- |
| AUC | 0.8003 [[art:41d3c4e6:metrics.train.auc]] | 0.7846 [[art:d57b2552:metrics.test.auc]] | 0.7846 [[art:ee898745:metrics.out_of_time.auc]] | 0.7716 [[art:610c13fd:metrics.vintage_holdout.auc]] |
| Gini | 0.6006 [[art:66b6cc81:metrics.train.gini]] | 0.5692 [[art:1291e305:metrics.test.gini]] | 0.5692 [[art:46899ec9:metrics.out_of_time.gini]] | 0.5432 [[art:4b1525bb:metrics.vintage_holdout.gini]] |
| KS | 0.474 [[art:3e0b8829:metrics.train.ks]] | 0.4373 [[art:857a0cf9:metrics.test.ks]] | 0.4373 [[art:6360ccf9:metrics.out_of_time.ks]] | 0.4618 [[art:c3ac5a54:metrics.vintage_holdout.ks]] |
| Brier | 0.008111 [[art:e9077291:metrics.train.brier]] | 0.01725 [[art:68e8b1cf:metrics.test.brier]] | 0.01725 [[art:f0fd020a:metrics.out_of_time.brier]] | 0.004767 [[art:115af096:metrics.vintage_holdout.brier]] |
| Log loss | 0.04279 [[art:e62507ab:metrics.train.logloss]] | 0.0805 [[art:c576b630:metrics.test.logloss]] | 0.0805 [[art:205ce509:metrics.out_of_time.logloss]] | 0.02818 [[art:96a19aae:metrics.vintage_holdout.logloss]] |
| Observations | 33522 [[art:dd20fa4c:metrics.train.n]] | 12257 [[art:90b46eb1:metrics.test.n]] | 12257 [[art:7898809e:metrics.out_of_time.n]] | 32177 [[art:37a92951:metrics.vintage_holdout.n]] |

Train AUC of 0.8003 [[art:41d3c4e6:metrics.train.auc]] stands above test AUC of 0.7846 [[art:d57b2552:metrics.test.auc]], and the train-to-test gap between the two was read against a bound of 0.08 [[art:630f28f4:threshold.O1.auc_gap]].
The out-of-time AUC of 0.7846 [[art:ee898745:metrics.out_of_time.auc]] and the vintage holdout AUC of 0.7716 [[art:610c13fd:metrics.vintage_holdout.auc]] were each read against the bound of 0.05 [[art:90f8b6d9:threshold.O1.holdout_gap]] on how far a period split's AUC may fall below test, with the vintage holdout the further of the two below test.
The separation of the test split by decile of predicted probability is reproduced below.

<!-- quaestor:renderer:begin table deciles.test -->
Decile separation on test; decile 1 holds the highest probabilities [[art:26b0ba93:deciles.test]]:

| decile | count | events | event_rate | lift |
|---|---|---|---|---|
| 1 | 1226 | 92 | 0.07504 | 4.181 |
| 2 | 1226 | 35 | 0.02855 | 1.591 |
| 3 | 1226 | 33 | 0.02692 | 1.5 |
| 4 | 1226 | 14 | 0.01142 | 0.6362 |
| 5 | 1226 | 15 | 0.01223 | 0.6817 |
| 6 | 1226 | 12 | 0.009788 | 0.5453 |
| 7 | 1226 | 13 | 0.0106 | 0.5908 |
| 8 | 1225 | 3 | 0.002449 | 0.1364 |
| 9 | 1225 | 3 | 0.002449 | 0.1364 |
| 10 | 1225 | 0 | 0 | 0 |
<!-- quaestor:renderer:end -->

### Developer-declared thresholds

<!-- quaestor:renderer:begin table thresholds.evaluation -->
Every threshold package.yaml declares, with its bound, the recomputed value and the outcome [[art:9aea64d5:thresholds.evaluation]]:

| metric | split | bound | value | result |
|---|---|---|---|---|
| auc | test | minimum 0.65 | 0.7846 | pass |
| calibration_slope | test | minimum 0.8 | 0.9369 | pass |
| calibration_slope | test | maximum 1.2 | 0.9369 | pass |
| psi |  | maximum 0.25 | 3.016 | fail |
<!-- quaestor:renderer:end -->

The table shows the recomputed test AUC of 0.7846 [[art:d57b2552:metrics.test.auc]] above the declared minimum of 0.65 [[art:fececac1:threshold.package.auc.test.min]], and the recomputed test calibration slope of 0.9369 [[art:290cccd9:calibration_slope.test]] inside the declared band from 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] to 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The declared stability bound of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]] is the one the recomputed largest train-to-test population stability index of 3.016 [[art:4fae32c6:psi.max]] stands above, and that breach is a finding of this validation.

### Follow-up analyses

The bounded planning loop asked for every metric recomputed on the slice `burnout > median(burnout)`, because the question was whether the relative over-prediction on the held-out splits concentrates in the high-burnout half, the feature whose train-to-test drift drove the stability finding.

<!-- quaestor:renderer:begin table metrics.train.sub.burnout_high -->
Every metric on the burnout above_median slice of train [[art:fb49a094:metrics.train.sub.burnout_high]]:

| metric | value |
|---|---|
| n | 16761 |
| event_rate | 0.01289 |
| auc | 0.7679 |
| gini | 0.5357 |
| ks | 0.4121 |
| brier | 0.01251 |
| logloss | 0.06262 |
| mean_predicted | 0.01301 |
| mean_rel_gap | 0.009235 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.burnout_high -->
Every metric on the burnout above_median slice of test [[art:af562636:metrics.test.sub.burnout_high]]:

| metric | value |
|---|---|
| n | 6128 |
| event_rate | 0.01942 |
| auc | 0.7764 |
| gini | 0.5528 |
| ks | 0.4315 |
| brier | 0.01887 |
| logloss | 0.08837 |
| mean_predicted | 0.03187 |
| mean_rel_gap | 0.641 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.out_of_time.sub.burnout_high -->
Every metric on the burnout above_median slice of out_of_time [[art:014114c3:metrics.out_of_time.sub.burnout_high]]:

| metric | value |
|---|---|
| n | 6128 |
| event_rate | 0.01942 |
| auc | 0.7764 |
| gini | 0.5528 |
| ks | 0.4315 |
| brier | 0.01887 |
| logloss | 0.08837 |
| mean_predicted | 0.03187 |
| mean_rel_gap | 0.641 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.vintage_holdout.sub.burnout_high -->
Every metric on the burnout above_median slice of vintage_holdout [[art:fa1d60e6:metrics.vintage_holdout.sub.burnout_high]]:

| metric | value |
|---|---|
| n | 16088 |
| event_rate | 0.007583 |
| auc | 0.7317 |
| gini | 0.4633 |
| ks | 0.3682 |
| brier | 0.007477 |
| logloss | 0.04207 |
| mean_predicted | 0.008596 |
| mean_rel_gap | 0.1335 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

On this slice the AUC falls below the split's own by 0.03243 [[art:a18d63eb:metrics.train.sub.burnout_high.auc_gap]] on train, by 0.008195 [[art:ad1d8f68:metrics.test.sub.burnout_high.auc_gap]] on test, by 0.008195 [[art:c93b5fc8:metrics.out_of_time.sub.burnout_high.auc_gap]] out of time and by 0.03995 [[art:f49dd552:metrics.vintage_holdout.sub.burnout_high.auc_gap]] on the vintage holdout, each within the slice bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]], so none of them is an open item.
The slice holds 0.5 [[art:e7e14804:metrics.train.sub.burnout_high.share]] of train, 0.5 [[art:efeac6e1:metrics.test.sub.burnout_high.share]] of test, 0.5 [[art:b5c30bbc:metrics.out_of_time.sub.burnout_high.share]] of out of time and 0.5 [[art:379549be:metrics.vintage_holdout.sub.burnout_high.share]] of the vintage holdout, all above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] at which a sub-population is large enough to be read.
Mean predicted against the observed rate on the slice gives a relative gap of 0.009235 [[art:d3a62f43:metrics.train.sub.burnout_high.mean_rel_gap]] on train, 0.641 [[art:668dd56c:metrics.test.sub.burnout_high.mean_rel_gap]] on test, 0.641 [[art:e79c0bd2:metrics.out_of_time.sub.burnout_high.mean_rel_gap]] out of time and 0.1335 [[art:4ef00612:metrics.vintage_holdout.sub.burnout_high.mean_rel_gap]] on the vintage holdout.
Because the AUC shortfalls stay within the slice bound while the relative level gaps on test and out of time rise well above the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]], the weakness on this half reads as one of the level of the probabilities rather than of their ordering.

The loop then asked for every metric on the complement slice `burnout <= median(burnout)`, because the complement is what tells whether the level error is concentrated in the high-burnout rows already measured or is spread across the split.

<!-- quaestor:renderer:begin table metrics.train.sub.burnout_low -->
Every metric on the burnout below_median slice of train [[art:1fbd40fa:metrics.train.sub.burnout_low]]:

| metric | value |
|---|---|
| n | 16761 |
| event_rate | 0.003759 |
| auc | 0.7493 |
| gini | 0.4986 |
| ks | 0.4053 |
| brier | 0.003716 |
| logloss | 0.02297 |
| mean_predicted | 0.00366 |
| mean_rel_gap | 0.02636 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.burnout_low -->
Every metric on the burnout below_median slice of test [[art:0ca2deda:metrics.test.sub.burnout_low]]:

| metric | value |
|---|---|
| n | 6129 |
| event_rate | 0.01648 |
| auc | 0.8119 |
| gini | 0.6239 |
| ks | 0.496 |
| brier | 0.01564 |
| logloss | 0.07263 |
| mean_predicted | 0.01379 |
| mean_rel_gap | 0.1633 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.out_of_time.sub.burnout_low -->
Every metric on the burnout below_median slice of out_of_time [[art:3acfe0f8:metrics.out_of_time.sub.burnout_low]]:

| metric | value |
|---|---|
| n | 6129 |
| event_rate | 0.01648 |
| auc | 0.8119 |
| gini | 0.6239 |
| ks | 0.496 |
| brier | 0.01564 |
| logloss | 0.07263 |
| mean_predicted | 0.01379 |
| mean_rel_gap | 0.1633 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.vintage_holdout.sub.burnout_low -->
Every metric on the burnout below_median slice of vintage_holdout [[art:a4cc6bb8:metrics.vintage_holdout.sub.burnout_low]]:

| metric | value |
|---|---|
| n | 16089 |
| event_rate | 0.002051 |
| auc | 0.7485 |
| gini | 0.497 |
| ks | 0.4714 |
| brier | 0.002057 |
| logloss | 0.01429 |
| mean_predicted | 0.003719 |
| mean_rel_gap | 0.8134 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

Here the AUC falls below the split's own by 0.05101 [[art:d6960b9c:metrics.train.sub.burnout_low.auc_gap]] on train and by 0.0231 [[art:d85223fe:metrics.vintage_holdout.sub.burnout_low.auc_gap]] on the vintage holdout, while on test and out of time the gap is -0.02731 [[art:c6967420:metrics.test.sub.burnout_low.auc_gap]] and -0.02731 [[art:414188ff:metrics.out_of_time.sub.burnout_low.auc_gap]], the negative sign meaning the slice ranks better than the split it sits in; all four are within the slice bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]], so none is an open item.
The slice holds 0.5 [[art:a4cc9400:metrics.train.sub.burnout_low.share]] of train, 0.5 [[art:4307ceba:metrics.test.sub.burnout_low.share]] of test, 0.5 [[art:d6102b4a:metrics.out_of_time.sub.burnout_low.share]] of out of time and 0.5 [[art:b327a747:metrics.vintage_holdout.sub.burnout_low.share]] of the vintage holdout, each above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].
Mean predicted against the observed rate gives a relative gap of 0.02636 [[art:e08aba69:metrics.train.sub.burnout_low.mean_rel_gap]] on train, 0.1633 [[art:64191da8:metrics.test.sub.burnout_low.mean_rel_gap]] on test, 0.1633 [[art:6355b95b:metrics.out_of_time.sub.burnout_low.mean_rel_gap]] out of time and 0.8134 [[art:b9abef02:metrics.vintage_holdout.sub.burnout_low.mean_rel_gap]] on the vintage holdout.
Comparing the two burnout halves on the relative mean gap, taken as levels of that already-relative quantity, the above-median half is the larger on test at 0.641 [[art:668dd56c:metrics.test.sub.burnout_high.mean_rel_gap]] against 0.1633 [[art:64191da8:metrics.test.sub.burnout_low.mean_rel_gap]], while on the vintage holdout the direction reverses and the below-median half is the larger at 0.8134 [[art:b9abef02:metrics.vintage_holdout.sub.burnout_low.mean_rel_gap]] against 0.1335 [[art:4ef00612:metrics.vintage_holdout.sub.burnout_high.mean_rel_gap]].
So the level error is not confined to one side of the burnout median, and on both halves it is the level of the probabilities, not their ordering, that carries the weakness.

The loop finally asked for every metric on the slice `incentive > median(incentive)`, because concentration of the over-prediction in the in-the-money half would point to the refinance response rather than to a flat shift in the intercept.

<!-- quaestor:renderer:begin table metrics.train.sub.incentive_high -->
Every metric on the incentive above_median slice of train [[art:ab3dc71d:metrics.train.sub.incentive_high]]:

| metric | value |
|---|---|
| n | 16761 |
| event_rate | 0.0139 |
| auc | 0.7496 |
| gini | 0.4993 |
| ks | 0.3783 |
| brier | 0.01349 |
| logloss | 0.06741 |
| mean_predicted | 0.01395 |
| mean_rel_gap | 0.003817 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.incentive_high -->
Every metric on the incentive above_median slice of test [[art:358f21f3:metrics.test.sub.incentive_high]]:

| metric | value |
|---|---|
| n | 6127 |
| event_rate | 0.02824 |
| auc | 0.7444 |
| gini | 0.4887 |
| ks | 0.3711 |
| brier | 0.02696 |
| logloss | 0.1194 |
| mean_predicted | 0.03865 |
| mean_rel_gap | 0.369 |
| share | 0.4999 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.out_of_time.sub.incentive_high -->
Every metric on the incentive above_median slice of out_of_time [[art:44dd161f:metrics.out_of_time.sub.incentive_high]]:

| metric | value |
|---|---|
| n | 6127 |
| event_rate | 0.02824 |
| auc | 0.7444 |
| gini | 0.4887 |
| ks | 0.3711 |
| brier | 0.02696 |
| logloss | 0.1194 |
| mean_predicted | 0.03865 |
| mean_rel_gap | 0.369 |
| share | 0.4999 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.vintage_holdout.sub.incentive_high -->
Every metric on the incentive above_median slice of vintage_holdout [[art:94f6c834:metrics.vintage_holdout.sub.incentive_high]]:

| metric | value |
|---|---|
| n | 16088 |
| event_rate | 0.007397 |
| auc | 0.7555 |
| gini | 0.5109 |
| ks | 0.3926 |
| brier | 0.007305 |
| logloss | 0.0409 |
| mean_predicted | 0.01029 |
| mean_rel_gap | 0.3916 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

The slice's AUC falls below the split's own by 0.05065 [[art:1eb21997:metrics.train.sub.incentive_high.auc_gap]] on train, by 0.04024 [[art:fa601af0:metrics.test.sub.incentive_high.auc_gap]] on test, by 0.04024 [[art:81bf8d6d:metrics.out_of_time.sub.incentive_high.auc_gap]] out of time and by 0.01615 [[art:2853b3a5:metrics.vintage_holdout.sub.incentive_high.auc_gap]] on the vintage holdout, each within the slice bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] and therefore supporting evidence rather than an open item.
The slice holds 0.5 [[art:64a6d28c:metrics.train.sub.incentive_high.share]] of train, 0.4999 [[art:a2b45314:metrics.test.sub.incentive_high.share]] of test, 0.4999 [[art:431d1ff2:metrics.out_of_time.sub.incentive_high.share]] of out of time and 0.5 [[art:cb627056:metrics.vintage_holdout.sub.incentive_high.share]] of the vintage holdout, all above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].
Mean predicted against the observed rate gives a relative gap of 0.003817 [[art:957b62eb:metrics.train.sub.incentive_high.mean_rel_gap]] on train, 0.369 [[art:2d6199b1:metrics.test.sub.incentive_high.mean_rel_gap]] on test, 0.369 [[art:7c011df6:metrics.out_of_time.sub.incentive_high.mean_rel_gap]] out of time and 0.3916 [[art:bb893376:metrics.vintage_holdout.sub.incentive_high.mean_rel_gap]] on the vintage holdout, each of the held-out three above the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
On this slice too the ordering holds within its bound while the level of the probabilities runs high on every held-out split, so the in-the-money half shares the miss rather than explaining it on its own.

## 5. Sensitivity and scenario analysis

This section reports sensitivity and scenario analysis as part of the critical analysis of model design, key assumptions, and developmental evidence expected of a validation [[reg:SR26-2:V.1.a]].
The accompanying expectation that sensitivity work be paired with stress testing over a wide range of inputs, including extreme values, to establish where a model becomes unstable is taken from the superseded guidance, which states it where the retrieved spans of the revision do not [[reg:SR11-7:V.1.a]].
Each of the procedures covered here — multicollinearity among the retained features, stability across the declared rate regimes, and the rate-shock scenarios — applies to a hazard model of this form estimated on a design that carries a regime column, and none of them is carried in Appendix D as inapplicable to this model type.

### Multicollinearity among the retained features

The largest variance inflation factor across the retained features is 4.288 [[art:fecfb289:vif.max]], which sits below the declared ceiling of 10 [[art:aeb4f33c:threshold.M1.vif]].
That maximum is attained by the note rate at 4.288 [[art:1113d019:vif.note_rate]], the feature most nearly explained by the rest of the design.
The remaining factors are 3.601 for burnout [[art:127bbabe:vif.burnout]], 2.593 for loan age [[art:b30f78aa:vif.loan_age]], 2.195 for the refinancing incentive [[art:60c8eef8:vif.incentive]], 1.627 for the spread at origination [[art:4b2ebef2:vif.sato]], 1.014 for the original loan-to-value ratio [[art:d9449fe2:vif.orig_ltv]], 1.012 for the log original balance [[art:59e2ab98:vif.orig_upb_log]], 1.011 for the credit score [[art:1f19769b:vif.credit_score]], 1.011 for the seasonal sine term [[art:3b05b05a:vif.season_sin]] and 1.007 for the seasonal cosine term [[art:f741ba51:vif.season_cos]].
Belsley's condition number of the column-standardised design is 4.778 [[art:5e2416a9:condition_number]], well below the declared ceiling of 30 [[art:7e52fd7a:threshold.M1.condition_number]].
The two diagnostics agree in direction: neither the per-feature measure nor the whole-design measure approaches its threshold, and the coefficient estimates are not reported here as resting on a near-singular design.

### Stability across the declared regimes

The champion's discrimination within each declared rate regime on the training data is set out below, and the declared tolerance on the difference in that measure across regimes is 0.1 [[art:b64213d7:threshold.R1.auc_gap]].

<!-- quaestor:renderer:begin table stability.auc_by_regime -->
The champion's AUC within each rate_regime on train [[art:3b0ee961:stability.auc_by_regime]]:

| regime | n | event_rate | auc |
|---|---|---|---|
| falling | 16370 | 0.01411 | 0.7415 |
| rising | 17152 | 0.002799 | 0.7306 |
<!-- quaestor:renderer:end -->

Coefficient stability is assessed by a sign-flip test that counts a flip only where the coefficient exceeds 0.05 [[art:aca84377:threshold.R1.sign_flip_coef]] in magnitude and its absolute z-statistic reaches 2 [[art:2e4428c7:threshold.R1.sign_flip_z]] in both regimes.
On that test the indicator is 0 for the note rate [[art:e7ce4912:stability.note_rate.sign_flip]], 0 for the refinancing incentive [[art:0cc7a37d:stability.incentive.sign_flip]], 0 for burnout [[art:6bc05e82:stability.burnout.sign_flip]], 0 for loan age [[art:b7191217:stability.loan_age.sign_flip]], 0 for the spread at origination [[art:1f302ccd:stability.sato.sign_flip]], 0 for the credit score [[art:d956c276:stability.credit_score.sign_flip]], 0 for the original loan-to-value ratio [[art:054d5fab:stability.orig_ltv.sign_flip]], 0 for the log original balance [[art:fb1ae6c8:stability.orig_upb_log.sign_flip]], 0 for the seasonal sine term [[art:6ba36a3b:stability.season_sin.sign_flip]] and 0 for the seasonal cosine term [[art:1850e2de:stability.season_cos.sign_flip]].
No retained feature therefore reverses the direction of its effect between regimes at a magnitude and significance the test would register, so the estimated prepayment response keeps a consistent sign structure across the declared rate environments.

### Rate-shock scenarios

Servicing value, its change from the base case and first-year prepayment speed are reported across the shock grid below.

<!-- quaestor:renderer:begin table scenario.value_by_shock -->
Servicing value, its change from the base case and first-year CPR, by shock [[art:7ca37cab:scenario.value_by_shock]]:

| shock_bp | value | value_change | cpr |
|---|---|---|---|
| -300 | 529900 | -1.166e+06 | 0.5407 |
| -200 | 1.108e+06 | -587900 | 0.2095 |
| -100 | 1.525e+06 | -171500 | 0.06584 |
| 0 | 1.696e+06 | 0 | 0.01955 |
| 100 | 1.747e+06 | 51210 | 0.005826 |
| 200 | 1.763e+06 | 66660 | 0.001738 |
| 300 | 1.767e+06 | 71320 | 0.0005173 |
<!-- quaestor:renderer:end -->

At the extreme downward shock the change in servicing value is -1166000 [[art:dfaf9b49:scenario.value_change.-300]], and at the extreme upward shock it is 71320 [[art:1bebd745:scenario.value_change.300]].
The base case is anchored at 0 [[art:1e1b0b88:scenario.value_change.0]] by construction, and the value change rises monotonically with the shock across the grid, from the loss at the extreme downward shock to the gain at the extreme upward shock, with no reversal at any intermediate node.
The downside is much the larger of the two extremes in magnitude, and the loss at the extreme downward shock is far further from the base case than the gain at the extreme upward shock is.
The convexity measure, formed as the change at the extreme downward shock added to the change at the extreme upward shock, is -1095000 [[art:70b14b4a:scenario.convexity]].
Its negative sign means the fall under falling rates outweighs the rise under rising rates, which is the direction of curvature the package declares for this asset, so the measured convexity agrees in direction with the declaration.
This asymmetry is the behaviour a servicing position is expected to show as the prepayment option moves into the money, and it is the region in which the model's outputs carry the most value at risk and warrant the closest attention in use.

## 6. Findings and recommendations

Findings below are ordered by severity, highest first, and each carries the recomputed values and the declared bound it was read against, so that the reliability and the limits of this model package can be judged from the evidence rather than from the conclusion [[reg:SR26-2:V]].

### F-001 · T1 declared threshold · severity **high**

**The largest train-to-test population stability index recomputed in this run sits far above the maximum the package itself declares for that quantity.**

The package declares a maximum of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]] for the population stability index, and the largest value recomputed between train and test, the score included, is 3.016 [[art:4fae32c6:psi.max]], which is above that maximum.

The validator concludes that the package breaches a limit its own configuration sets, so the recomputed behaviour of the model is outside the range the developer declared as acceptable, and this is a defect in the package as submitted and not a difference of methodology between developer and validator.

The developer should either re-establish the model on data whose train-to-test movement falls within the declared maximum of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]], or restate the limit with an argued basis and resubmit, and in the interim state the breach to model users as a limitation on use.

### F-002 · S1 population drift · severity **medium**

**The train and test populations differ enough on the model's own inputs, and on the score it produces, that fitted relationships learned on train are not being evaluated on a comparable population.**

Against a threshold of 0.25 [[art:278b9016:threshold.S1.psi]], the population stability index between train and test is 3.016 [[art:1d35a583:psi.burnout]] on `burnout`, the largest of the comparisons reported here.

The same index is 1.68 [[art:987aabe4:psi.loan_age]] on `loan_age`, 1.342 [[art:2f1cb70b:psi.note_rate]] on `note_rate`, and 0.8734 [[art:0f61188c:psi.incentive]] on `incentive`, each above that threshold.

The score's own distribution moves as well, at 0.8372 [[art:92ac1652:psi.y_score]], above the same threshold of 0.25 [[art:278b9016:threshold.S1.psi]], so the drift is not confined to the inputs but reaches the model output.

The validator concludes that drift of this extent limits what the test results establish about performance on the training population, and that it is a plausible contributor to the calibration defect recorded below rather than an independent observation.

The developer should document what changed between the two samples, say whether the split is chronological or otherwise structured, and show either that the split is the intended one for the model's use or that a comparable split leaves the fitted relationships intact.

### F-003 · C1 calibration · severity **medium**

**The mean predicted probability stands above the observed event rate on every split reported here, by a relative margin beyond the declared tolerance in each case.**

Against a relative tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]], the mean predicted probability on test is 0.02283 [[art:1c1a1d8d:metrics.test.mean_predicted]] where the observed rate is 0.01795 [[art:d222aedf:metrics.test.event_rate]], a relative gap of 0.2718 [[art:04dcea16:calibration.mean_rel_gap.test]].

On out_of_time the mean predicted probability is 0.02283 [[art:4d7aa98b:metrics.out_of_time.mean_predicted]] against an observed rate of 0.01795 [[art:83ccf5c0:metrics.out_of_time.event_rate]], a relative gap of 0.2718 [[art:c5239af4:calibration.mean_rel_gap.out_of_time]], again above that tolerance.

On vintage_holdout the mean predicted probability is 0.006157 [[art:914aeeba:metrics.vintage_holdout.mean_predicted]] against an observed rate of 0.004817 [[art:e3590a16:metrics.vintage_holdout.event_rate]], a relative gap of 0.2782 [[art:2eba48c2:calibration.mean_rel_gap.vintage_holdout]].

The comparison drawn across these splits is the relative gap and not the absolute difference: the predicted and observed levels on vintage_holdout are both well below those on test, while the relative gap on vintage_holdout is the larger of the two, so a reader should not treat the splits as alike on the absolute scale on the strength of their similar relative gaps.

The decile tables below show where in the predicted range the over-prediction sits on each split.

<!-- quaestor:renderer:begin table calibration.test -->
Calibration by decile of predicted probability on test [[art:07848a4c:calibration.test]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.001873 | 0 | 1226 |
| 2 | 0.003677 | 0.002447 | 1226 |
| 3 | 0.005318 | 0.002447 | 1226 |
| 4 | 0.007303 | 0.0106 | 1226 |
| 5 | 0.009752 | 0.009788 | 1226 |
| 6 | 0.01306 | 0.01223 | 1226 |
| 7 | 0.01816 | 0.01142 | 1226 |
| 8 | 0.02727 | 0.02694 | 1225 |
| 9 | 0.04395 | 0.02857 | 1225 |
| 10 | 0.09799 | 0.0751 | 1225 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table calibration.out_of_time -->
Calibration by decile of predicted probability on out_of_time [[art:a16e1248:calibration.out_of_time]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.001873 | 0 | 1226 |
| 2 | 0.003677 | 0.002447 | 1226 |
| 3 | 0.005318 | 0.002447 | 1226 |
| 4 | 0.007303 | 0.0106 | 1226 |
| 5 | 0.009752 | 0.009788 | 1226 |
| 6 | 0.01306 | 0.01223 | 1226 |
| 7 | 0.01816 | 0.01142 | 1226 |
| 8 | 0.02727 | 0.02694 | 1225 |
| 9 | 0.04395 | 0.02857 | 1225 |
| 10 | 0.09799 | 0.0751 | 1225 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table calibration.vintage_holdout -->
Calibration by decile of predicted probability on vintage_holdout [[art:a402f077:calibration.vintage_holdout]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.0004637 | 0.001243 | 3218 |
| 2 | 0.0008609 | 0.001554 | 3218 |
| 3 | 0.001234 | 0.0003108 | 3218 |
| 4 | 0.001671 | 0.001554 | 3218 |
| 5 | 0.002261 | 0.001865 | 3218 |
| 6 | 0.003137 | 0.002797 | 3218 |
| 7 | 0.004596 | 0.002486 | 3218 |
| 8 | 0.007083 | 0.008393 | 3217 |
| 9 | 0.01187 | 0.008082 | 3217 |
| 10 | 0.02841 | 0.01989 | 3217 |
<!-- quaestor:renderer:end -->

The validator concludes that the level of the model's output is biased upward on every split reported here, that the bias persists on the vintage holdout as well as on the in-period splits, and that any use of the predictions as probabilities rather than as a ranking is affected by it.

The developer should recalibrate the output level against observed experience, report the recomputed relative gaps against the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]] on each split, and confirm that the test and out_of_time splits are drawn from distinct populations given that their recomputed predicted and observed values coincide.

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1), `compute_metrics` (O1), `check_leakage` (L1, L2), `check_stability` (R1), `check_collinearity` (M1), `challenger_compare` (E1), `run_scenarios` (X1).

### Open items

Given that the fitted coefficient on `note_rate` carries sign -1 [[art:aecf7ccb:sign_check.note_rate.coef_sign]] while that feature's own univariate direction, the bound the fitted sign was read against, is 1 [[art:61f6e1ac:sign_check.note_rate.univariate_direction]] and the agreement indicator between the two therefore stands at 0 [[art:a453463d:sign_check.note_rate.agrees]], can the model developer explain what the fitted term is discriminating on once the variables correlated with `note_rate` are held alongside it, and whether the conditional direction it carries in the fitted model is the one the developer intends?

## 7. Ongoing monitoring recommendations

Ongoing monitoring of this package should be designed around the expectation that monitoring evaluates the extent to which a model performs as expected given potential changes in products, exposures, activities, clients, data relevance, or market conditions, and that the frequency and scope of monitoring reports follow the nature and materiality of the model [[reg:SR26-2:V.2]].

### 7.1 Quantities to track and the bounds to track them against

Monitoring should reuse the bounds this validation checked against rather than setting fresh ones, so that a production breach and a validation breach mean the same thing.

Calibration on each production vintage should be tracked as the slope of the outcome on the logit of the score, against the declared lower bound of 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] and the declared upper bound of 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The value observed in this validation, 0.9369 [[art:290cccd9:calibration_slope.test]], sits inside that band and below the midpoint of it, so monitoring should treat downward movement toward the lower bound as the nearer of the two approaches.

Discrimination should be tracked as AUC on each vintage against the declared floor of 0.65 [[art:fececac1:threshold.package.auc.test.min]], with the validation value of 0.7846 [[art:d57b2552:metrics.test.auc]] as the reference level above that floor.
A decline toward the floor is more informative than the level itself, so the monitoring report should carry the trajectory across vintages alongside each point value.

Population and score stability should be tracked as PSI against the declared bound of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]], reported per input and for the score itself rather than as a single summary.
The largest train-to-test value seen in this validation, 3.016 [[art:4fae32c6:psi.max]], is well above that declared bound, which means the stability series starts from a level already outside the bound and monitoring cannot treat a breach in production as the first signal of drift.
Because of that starting position, the stability panel should show which input carries the largest value in each vintage and whether the identity of that input changes, since a stable magnitude arising from a shifting set of inputs is a different condition from a persistent shift in one input.

### 7.2 Frequency

Stability of the inputs and of the score distribution can be computed without waiting for outcomes and should be reported at every scoring cycle, monthly at minimum.
Calibration and discrimination require realized prepayment outcomes and should be reported quarterly on vintages whose performance window has closed, with the window stated explicitly in each report so that partially seasoned vintages are not read as matured ones.
The benchmarking comparison described below should be reported at least annually, and sooner if the stability series or the calibration series moves materially.

### 7.3 Ordering of evidence in the monitoring report

Section 4 of this report presented calibration before discrimination because the package declares that this model's output is consumed as a probability and not only as a ranking.
Monitoring reports should preserve that order for the same reason: when the output is used as a probability, a well-ranked but mis-levelled score is a defect that a discrimination-first presentation buries.
Where a vintage shows movement in both, the report should say which of the two moved further from its declared bound rather than describing the pair as jointly degraded.

### 7.4 Benchmarking that monitoring adds

Section 2 of this report compares the champion against a challenger, so benchmarking against an alternative model is part of this validation and monitoring does not introduce it.
What monitoring adds is the comparison the development data cannot supply: the challenger refitted on production vintages, so that the champion is measured against an alternative estimated on the population actually being scored rather than against one estimated on the development sample.
Discrepancies between the champion and that refitted challenger should trigger investigation into the source and degree of the difference rather than automatic replacement, since the challenger is itself an alternative prediction and differences may reflect the different estimation sample [[reg:SR11-7:V.1.b]].
If a refit on production vintages is not feasible in a given period, an external or vendor prepayment reference may stand in, but the report should say which of the two comparisons it is presenting, because they answer different questions.

### 7.5 What this validation could not cover

This validation observed the model on development and test data, so it says nothing about behaviour on vintages originated after that data was assembled; monitoring carries that burden through the vintage-by-vintage series above.
Process verification in the production environment — that inputs arrive accurate, complete, and consistent with the model's purpose, and that the deployed code matches the reviewed code under change control — is an operational check that monitoring must perform on the live system [[reg:SR11-7:V.1.b]].
Overrides of model output by users, and whether the override process consistently improves on the model, can only be observed in production and should be logged, rated for outcome, and reviewed in each monitoring cycle [[reg:SR11-7:V.1.b]].
Back-testing over the full prepayment performance window accumulates slowly, so monitoring should pair it with early-warning metrics computed shortly after each vintage is scored rather than deferring all outcome evidence to the matured window [[reg:SR26-2:V.1.b]].
Sensitivity of the model to the rate environment and to other macroeconomic conditions outside the range spanned by the development data is a limitation to be reassessed over time rather than settled here, and monitoring should flag when scoring populations approach or exceed the input ranges the model was estimated on [[reg:SR26-2:V.2]].

### 7.6 Escalation

A quantity that moves outside its declared bound, or that trends toward it across consecutive vintages, should route to the model owner with a written assessment of whether overlay, recalibration, or redevelopment is the appropriate response [[reg:SR26-2:V.2]].
Persistent deviation outside the declared bounds, as opposed to a single vintage, is the condition under which adjustment, recalibration, or redevelopment is normally considered [[reg:SR26-2:V.1.b]].

## Appendix A — Claims

Grounding precision 0.9940 before repair (334 of 336 claims verified; 2 unsupported) and 1.0000 after 0 claim(s) rewritten and 2 number(s) removed from the prose. Per section (post-repair): summary 10/10; conceptual_soundness 70/70; data_integrity 79/79; outcomes 113/113; sensitivity 31/31; findings 24/24; monitoring 7/7.

Developer claims: The package declares 3 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). See Appendix D.

Excluded numeric tokens (not claims): section_number (section 6, 7.1, 7.2, 7.3); citation_hash (2ad8d1a5, 60d3a086, 3b91ffcc, 7898809e); regulatory_section_id (SR26-2:V, SR26-2:V.1.b, SR26-2:V.1.a, SR26-2:IV.1); finding_id (F-001, F-002, F-003); package_version (1.0); extractor_returned_excluded_token (1.0, 6, 12.0, 4.0).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The subject was re-executed end to end from the developer's… | 300 | ratio | runtime.max_seconds |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 2 | summary | The training split holds 33522 rows and the test split holds… | 33522 | count | n | train | eq | `[[art:60d3a086:profile.train.n]]` | verified | 33522 |
| 3 | summary | The training split holds 33522 rows and the test split holds… | 12257 | count | n | test | eq | `[[art:3b91ffcc:profile.test.n]]` | verified | 12257 |
| 4 | summary | The out-of-time split holds 12257 rows and the vintage holdo… | 12257 | count | n | out_of_time | eq | `[[art:7898809e:metrics.out_of_time.n]]` | verified | 12257 |
| 5 | summary | The out-of-time split holds 12257 rows and the vintage holdo… | 32177 | count | n | vintage_holdout | eq | `[[art:37a92951:metrics.vintage_holdout.n]]` | verified | 32177 |
| 6 | summary | On the headline result, discrimination on the test split at… | 0.7846 | ratio | auc | test | eq | `[[art:d57b2552:metrics.test.auc]]` | verified | 0.7846182604 |
| 7 | summary | On the headline result, discrimination on the test split at… | 0.65 | ratio | auc | test | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 8 | summary | The calibration slope on the test split at 0.9369 sits insid… | 0.9369 | ratio | calibration_slope | test | eq | `[[art:290cccd9:calibration_slope.test]]` | verified | 0.9368866293 |
| 9 | summary | The calibration slope on the test split at 0.9369 sits insid… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 10 | summary | The calibration slope on the test split at 0.9369 sits insid… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 11 | conceptual_soundness | The champion is a prepayment model estimated on loan-month o… | -5.517 | ratio | intercept |  | eq | `[[art:cf58dded:run.model_summary#intercept]]` | verified | -5.517061245 |
| 12 | conceptual_soundness | It was fitted on 33522 loan-month rows drawn from 667 distin… | 33522 | count | n_train | train | eq | `[[art:cf58dded:run.model_summary#n_train]]` | verified | 33522 |
| 13 | conceptual_soundness | It was fitted on 33522 loan-month rows drawn from 667 distin… | 667 | count | n_train_loans | train | eq | `[[art:cf58dded:run.model_summary#n_train_loans]]` | verified | 667 |
| 14 | conceptual_soundness | The specification retains 12 features. | 12 | count | n |  | eq | `[[art:61276a96:run.features#n]]` | verified | 12 |
| 15 | conceptual_soundness | By timing, 5 are known at origination and 7 are known before… | 5 | count | at_origination |  | eq | `[[art:61276a96:run.features#at_origination]]` | verified | 5 |
| 16 | conceptual_soundness | By timing, 5 are known at origination and 7 are known before… | 7 | count | before_period_start |  | eq | `[[art:61276a96:run.features#before_period_start]]` | verified | 7 |
| 17 | conceptual_soundness | Features observed during the prediction period number 0 , an… | 0 | count | during_period |  | eq | `[[art:61276a96:run.features#during_period]]` | verified | 0 |
| 18 | conceptual_soundness | Features observed during the prediction period number 0 , an… | 0 | count | after_outcome |  | eq | `[[art:61276a96:run.features#after_outcome]]` | verified | 0 |
| 19 | conceptual_soundness | The developer applied a collinearity screen with a cutoff of… | 10 | ratio | vif_threshold |  | eq | `[[art:cf58dded:run.model_summary#vif_threshold]]` | verified | 10 |
| 20 | conceptual_soundness | A trailing rate-change feature was removed at a variance inf… | 11.98 | ratio | vif |  | eq | `[[art:cf58dded:run.model_summary#removed.rate_change_12m.vif]]` | verified | 11.980734 |
| 21 | conceptual_soundness | A log beginning-of-month balance feature was removed at 3912… | 39120 | ratio | vif |  | eq | `[[art:cf58dded:run.model_summary#removed.bom_balance_log.vif]]` | verified | 39124.25486 |
| 22 | conceptual_soundness | The refinance incentive carries the largest coefficient in m… | 1.18 | ratio | coefficient |  | eq | `[[art:cf58dded:run.model_summary#coefficients.incentive.value]]` | verified | 1.180215141 |
| 23 | conceptual_soundness | The leading loan-age spline term is 0.6271 and the trailing… | 0.6271 | ratio | coefficient |  | eq | `[[art:cf58dded:run.model_summary#coefficients.loan_age_spline_1.value]]` | verified | 0.6271134021 |
| 24 | conceptual_soundness | The leading loan-age spline term is 0.6271 and the trailing… | -0.4007 | ratio | coefficient |  | eq | `[[art:cf58dded:run.model_summary#coefficients.loan_age_spline_4.value]]` | verified | -0.4006818139 |
| 25 | conceptual_soundness | The leading loan-age spline term is 0.6271 and the trailing… | 0.1035 | ratio | coefficient |  | eq | `[[art:cf58dded:run.model_summary#coefficients.loan_age_spline_2.value]]` | verified | 0.1034661786 |
| 26 | conceptual_soundness | The leading loan-age spline term is 0.6271 and the trailing… | -0.08673 | ratio | coefficient |  | eq | `[[art:cf58dded:run.model_summary#coefficients.loan_age_spline_3.value]]` | verified | -0.08672634265 |
| 27 | conceptual_soundness | Credit score enters at 0.4228 , positive, consistent with st… | 0.4228 | ratio | coefficient |  | eq | `[[art:cf58dded:run.model_summary#coefficients.credit_score.value]]` | verified | 0.4228037046 |
| 28 | conceptual_soundness | Original loan-to-value enters at -0.2265 , negative, consist… | -0.2265 | ratio | coefficient |  | eq | `[[art:cf58dded:run.model_summary#coefficients.orig_ltv.value]]` | verified | -0.2265163201 |
| 29 | conceptual_soundness | Log original balance enters at 0.3277 , positive, consistent… | 0.3277 | ratio | coefficient |  | eq | `[[art:cf58dded:run.model_summary#coefficients.orig_upb_log.value]]` | verified | 0.3277471666 |
| 30 | conceptual_soundness | The note rate enters at -0.522 , negative, which is not the… | -0.522 | ratio | coefficient |  | eq | `[[art:cf58dded:run.model_summary#coefficients.note_rate.value]]` | verified | -0.5220226084 |
| 31 | conceptual_soundness | Burnout enters at 0.1918 , positive, whereas the conventiona… | 0.1918 | ratio | coefficient |  | eq | `[[art:cf58dded:run.model_summary#coefficients.burnout.value]]` | verified | 0.1917654912 |
| 32 | conceptual_soundness | The seasonal pair enters at 0.1129 and -0.1391 , and the spr… | 0.1129 | ratio | coefficient |  | eq | `[[art:cf58dded:run.model_summary#coefficients.season_sin.value]]` | verified | 0.1129264019 |
| 33 | conceptual_soundness | The seasonal pair enters at 0.1129 and -0.1391 , and the spr… | -0.1391 | ratio | coefficient |  | eq | `[[art:cf58dded:run.model_summary#coefficients.season_cos.value]]` | verified | -0.139058519 |
| 34 | conceptual_soundness | The seasonal pair enters at 0.1129 and -0.1391 , and the spr… | 0.01832 | ratio | coefficient |  | eq | `[[art:cf58dded:run.model_summary#coefficients.sato.value]]` | verified | 0.01832046228 |
| 35 | conceptual_soundness | The count of retained features whose fitted sign contradicts… | 1 | count | n_disagreements |  | eq | `[[art:f96ece96:sign_check.n_disagreements]]` | verified | 1 |
| 36 | conceptual_soundness | Its fitted coefficient sign is -1 while its univariate direc… | -1 | ratio | coef_sign |  | eq | `[[art:aecf7ccb:sign_check.note_rate.coef_sign]]` | verified | -1 |
| 37 | conceptual_soundness | Its fitted coefficient sign is -1 while its univariate direc… | 1 | ratio | univariate_direction | train | eq | `[[art:61f6e1ac:sign_check.note_rate.univariate_direction]]` | verified | 1 |
| 38 | conceptual_soundness | Its fitted coefficient sign is -1 while its univariate direc… | 0 | ratio | agrees |  | eq | `[[art:a453463d:sign_check.note_rate.agrees]]` | verified | 0 |
| 39 | conceptual_soundness | The weight to put on the disagreement is set by what the mod… | 0.005792 | ratio | delta_auc | test | eq | `[[art:338b461a:ablation.note_rate.delta_auc]]` | verified | 0.005792367473 |
| 40 | conceptual_soundness | Every other checked feature agrees with its univariate direc… | 1 | ratio | agrees |  | eq | `[[art:f7b2338e:sign_check.incentive.agrees]]` | verified | 1 |
| 41 | conceptual_soundness | Every other checked feature agrees with its univariate direc… | 1 | ratio | agrees |  | eq | `[[art:915bf8eb:sign_check.credit_score.agrees]]` | verified | 1 |
| 42 | conceptual_soundness | Every other checked feature agrees with its univariate direc… | 1 | ratio | agrees |  | eq | `[[art:7021aeb0:sign_check.orig_ltv.agrees]]` | verified | 1 |
| 43 | conceptual_soundness | Every other checked feature agrees with its univariate direc… | 1 | ratio | agrees |  | eq | `[[art:07a9d3e6:sign_check.orig_upb_log.agrees]]` | verified | 1 |
| 44 | conceptual_soundness | Every other checked feature agrees with its univariate direc… | 1 | ratio | agrees |  | eq | `[[art:2eec20ab:sign_check.burnout.agrees]]` | verified | 1 |
| 45 | conceptual_soundness | Every other checked feature agrees with its univariate direc… | 1 | ratio | agrees |  | eq | `[[art:2401eba2:sign_check.sato.agrees]]` | verified | 1 |
| 46 | conceptual_soundness | Every other checked feature agrees with its univariate direc… | 1 | ratio | agrees |  | eq | `[[art:e110f357:sign_check.season_sin.agrees]]` | verified | 1 |
| 47 | conceptual_soundness | Every other checked feature agrees with its univariate direc… | 1 | ratio | agrees |  | eq | `[[art:7f18ddf7:sign_check.season_cos.agrees]]` | verified | 1 |
| 48 | conceptual_soundness | The fitted and univariate signs behind those agreements run… | 1 | ratio | coef_sign |  | eq | `[[art:684cf11a:sign_check.incentive.coef_sign]]` | verified | 1 |
| 49 | conceptual_soundness | The fitted and univariate signs behind those agreements run… | 1 | ratio | univariate_direction |  | eq | `[[art:8098d951:sign_check.incentive.univariate_direction]]` | verified | 1 |
| 50 | conceptual_soundness | The fitted and univariate signs behind those agreements run… | 1 | ratio | coef_sign |  | eq | `[[art:1ec1078b:sign_check.credit_score.coef_sign]]` | verified | 1 |
| 51 | conceptual_soundness | The fitted and univariate signs behind those agreements run… | 1 | ratio | univariate_direction |  | eq | `[[art:42303896:sign_check.credit_score.univariate_direction]]` | verified | 1 |
| 52 | conceptual_soundness | The fitted and univariate signs behind those agreements run… | -1 | ratio | coef_sign |  | eq | `[[art:7eec65ec:sign_check.orig_ltv.coef_sign]]` | verified | -1 |
| 53 | conceptual_soundness | The fitted and univariate signs behind those agreements run… | -1 | ratio | univariate_direction |  | eq | `[[art:76dbc708:sign_check.orig_ltv.univariate_direction]]` | verified | -1 |
| 54 | conceptual_soundness | The fitted and univariate signs behind those agreements run… | 1 | ratio | coef_sign |  | eq | `[[art:5aa309fc:sign_check.orig_upb_log.coef_sign]]` | verified | 1 |
| 55 | conceptual_soundness | The fitted and univariate signs behind those agreements run… | 1 | ratio | univariate_direction |  | eq | `[[art:b9743ecb:sign_check.orig_upb_log.univariate_direction]]` | verified | 1 |
| 56 | conceptual_soundness | The fitted and univariate signs behind those agreements run… | 1 | ratio | coef_sign |  | eq | `[[art:a3063608:sign_check.burnout.coef_sign]]` | verified | 1 |
| 57 | conceptual_soundness | The fitted and univariate signs behind those agreements run… | 1 | ratio | univariate_direction |  | eq | `[[art:bfc96bb2:sign_check.burnout.univariate_direction]]` | verified | 1 |
| 58 | conceptual_soundness | The fitted and univariate signs behind those agreements run… | 1 | ratio | coef_sign |  | eq | `[[art:c031d0d5:sign_check.sato.coef_sign]]` | verified | 1 |
| 59 | conceptual_soundness | The fitted and univariate signs behind those agreements run… | 1 | ratio | univariate_direction |  | eq | `[[art:c08233a6:sign_check.sato.univariate_direction]]` | verified | 1 |
| 60 | conceptual_soundness | The fitted and univariate signs behind those agreements run… | 1 | ratio | coef_sign |  | eq | `[[art:761188ce:sign_check.season_sin.coef_sign]]` | verified | 1 |
| 61 | conceptual_soundness | The fitted and univariate signs behind those agreements run… | 1 | ratio | univariate_direction |  | eq | `[[art:cae6b096:sign_check.season_sin.univariate_direction]]` | verified | 1 |
| 62 | conceptual_soundness | The fitted and univariate signs behind those agreements run… | -1 | ratio | coef_sign |  | eq | `[[art:7dbb1ffc:sign_check.season_cos.coef_sign]]` | verified | -1 |
| 63 | conceptual_soundness | The fitted and univariate signs behind those agreements run… | -1 | ratio | univariate_direction |  | eq | `[[art:03e931f0:sign_check.season_cos.univariate_direction]]` | verified | -1 |
| 64 | conceptual_soundness | The leave-one-out refits are measured from a refit of the ch… | 0.7802 | ratio | baseline_auc | test | eq | `[[art:93dda83a:ablation.baseline_auc]]` | verified | 0.7802163028 |
| 65 | conceptual_soundness | The leave-one-out refits are measured from a refit of the ch… | 0.7846 | ratio | auc | test | eq | `[[art:d57b2552:metrics.test.auc]]` | verified | 0.7846182604 |
| 66 | conceptual_soundness | Dropping the refinance incentive changes test AUC by -0.0794… | -0.07943 | ratio | delta_auc | test | eq | `[[art:46802ce1:ablation.incentive.delta_auc]]` | verified | -0.07943499966 |
| 67 | conceptual_soundness | Dropping credit score changes it by -0.0298 , log original b… | -0.0298 | ratio | delta_auc | test | eq | `[[art:a2d10cd7:ablation.credit_score.delta_auc]]` | verified | -0.02980393786 |
| 68 | conceptual_soundness | Dropping credit score changes it by -0.0298 , log original b… | -0.01681 | ratio | delta_auc | test | eq | `[[art:6158bf75:ablation.orig_upb_log.delta_auc]]` | verified | -0.01681104473 |
| 69 | conceptual_soundness | Dropping credit score changes it by -0.0298 , log original b… | -0.01199 | ratio | delta_auc | test | eq | `[[art:84275e57:ablation.orig_ltv.delta_auc]]` | verified | -0.01199332362 |
| 70 | conceptual_soundness | Dropping credit score changes it by -0.0298 , log original b… | -0.009946 | ratio | delta_auc | test | eq | `[[art:ca8fa8e9:ablation.loan_age.delta_auc]]` | verified | -0.009945848784 |
| 71 | conceptual_soundness | Dropping credit score changes it by -0.0298 , log original b… | -0.005672 | ratio | delta_auc | test | eq | `[[art:bdbbba37:ablation.season_cos.delta_auc]]` | verified | -0.005672283187 |
| 72 | conceptual_soundness | Dropping credit score changes it by -0.0298 , log original b… | -0.004237 | ratio | delta_auc | test | eq | `[[art:c9eb03ef:ablation.sato.delta_auc]]` | verified | -0.004237313737 |
| 73 | conceptual_soundness | Dropping burnout changes it by 0.004292 and dropping the sin… | 0.004292 | ratio | delta_auc | test | eq | `[[art:8aa8bccf:ablation.burnout.delta_auc]]` | verified | 0.00429206915 |
| 74 | conceptual_soundness | Dropping burnout changes it by 0.004292 and dropping the sin… | 0.00054 | ratio | delta_auc | test | eq | `[[art:95e1e0c6:ablation.season_sin.delta_auc]]` | verified | 0.0005400016615 |
| 75 | conceptual_soundness | The challenger scores 0.7211 on test against the champion's… | 0.7211 | ratio | auc | test | eq | `[[art:489cd7a6:challenger.auc]]` | verified | 0.7210566662 |
| 76 | conceptual_soundness | The challenger scores 0.7211 on test against the champion's… | 0.7846 | ratio | auc | test | eq | `[[art:d57b2552:metrics.test.auc]]` | verified | 0.7846182604 |
| 77 | conceptual_soundness | The challenger scores 0.7211 on test against the champion's… | -0.06356 | ratio | delta_auc | test | eq | `[[art:7e119a34:challenger.delta_auc]]` | verified | -0.06356159418 |
| 78 | conceptual_soundness | The declared decision rule turns on the challenger's lead ov… | 0.03 | ratio | delta_auc |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 79 | conceptual_soundness | Calibration points the same way: the champion's test Brier s… | 0.01725 | ratio | brier | test | eq | `[[art:68e8b1cf:metrics.test.brier]]` | verified | 0.01725186302 |
| 80 | conceptual_soundness | Calibration points the same way: the champion's test Brier s… | 0.02173 | ratio | brier | test | eq | `[[art:36aa75c4:challenger.brier]]` | verified | 0.02173012265 |
| 81 | data_integrity | The training split holds 33522 rows, the test split 12257 ,… | 33522 | count | n | train | eq | `[[art:60d3a086:profile.train.n]]` | verified | 33522 |
| 82 | data_integrity | The training split holds 33522 rows, the test split 12257 ,… | 12257 | count | n | test | eq | `[[art:3b91ffcc:profile.test.n]]` | verified | 12257 |
| 83 | data_integrity | The training split holds 33522 rows, the test split 12257 ,… | 12257 | count | n | out_of_time | eq | `[[art:fa39c5cf:profile.out_of_time.n]]` | verified | 12257 |
| 84 | data_integrity | The training split holds 33522 rows, the test split 12257 ,… | 32177 | count | n | vintage_holdout | eq | `[[art:426e712a:profile.vintage_holdout.n]]` | verified | 32177 |
| 85 | data_integrity | The largest missing fraction on any column of the training s… | 0 | ratio | missing_max | train | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 86 | data_integrity | The largest missing fraction in the test split is 0 , in the… | 0 | ratio | missing_max | test | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 87 | data_integrity | The largest missing fraction in the test split is 0 , in the… | 0 | ratio | missing_max | out_of_time | eq | `[[art:4dafce11:profile.out_of_time.missing.max]]` | verified | 0 |
| 88 | data_integrity | The largest missing fraction in the test split is 0 , in the… | 0 | ratio | missing_max | vintage_holdout | eq | `[[art:329bb430:profile.vintage_holdout.missing.max]]` | verified | 0 |
| 89 | data_integrity | Comparing the splits by the difference between these largest… | 0.1 | ratio | missing_gap |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 90 | data_integrity | The declared stability bound is 0.25 , and the package decla… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 91 | data_integrity | The declared stability bound is 0.25 , and the package decla… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 92 | data_integrity | The largest train-to-test population stability index, the sc… | 3.016 | ratio | psi | test | eq | `[[art:4fae32c6:psi.max]]` | verified | 3.016020048 |
| 93 | data_integrity | It falls on burnout, whose train-to-test index is 3.016 . | 3.016 | ratio | psi | test | eq | `[[art:1d35a583:psi.burnout]]` | verified | 3.016020048 |
| 94 | data_integrity | Loan age follows at 1.68 , note rate at 1.342 , and incentiv… | 1.68 | ratio | psi | test | eq | `[[art:987aabe4:psi.loan_age]]` | verified | 1.679868562 |
| 95 | data_integrity | Loan age follows at 1.68 , note rate at 1.342 , and incentiv… | 1.342 | ratio | psi | test | eq | `[[art:2f1cb70b:psi.note_rate]]` | verified | 1.341893523 |
| 96 | data_integrity | Loan age follows at 1.68 , note rate at 1.342 , and incentiv… | 0.8734 | ratio | psi | test | eq | `[[art:0f61188c:psi.incentive]]` | verified | 0.8734495361 |
| 97 | data_integrity | Loan age follows at 1.68 , note rate at 1.342 , and incentiv… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 98 | data_integrity | The score itself shifts by 0.8372 between train and test, al… | 0.8372 | ratio | psi | test | eq | `[[art:92ac1652:psi.y_score]]` | verified | 0.8371883582 |
| 99 | data_integrity | The remaining train-to-test indices sit below it: orig UPB l… | 0.08171 | ratio | psi | test | eq | `[[art:f075546d:psi.orig_upb_log]]` | verified | 0.08171063787 |
| 100 | data_integrity | The remaining train-to-test indices sit below it: orig UPB l… | 0.07088 | ratio | psi | test | eq | `[[art:91c4ab83:psi.credit_score]]` | verified | 0.07088355626 |
| 101 | data_integrity | The remaining train-to-test indices sit below it: orig UPB l… | 0.04332 | ratio | psi | test | eq | `[[art:85842fd0:psi.orig_ltv]]` | verified | 0.04331914243 |
| 102 | data_integrity | The remaining train-to-test indices sit below it: orig UPB l… | 0.02284 | ratio | psi | test | eq | `[[art:4809116c:psi.sato]]` | verified | 0.02284102604 |
| 103 | data_integrity | The remaining train-to-test indices sit below it: orig UPB l… | 0.01631 | ratio | psi | test | eq | `[[art:46fec014:psi.season_sin]]` | verified | 0.01631255179 |
| 104 | data_integrity | The remaining train-to-test indices sit below it: orig UPB l… | 0.004988 | ratio | psi | test | eq | `[[art:62ae6c81:psi.season_cos]]` | verified | 0.004987781308 |
| 105 | data_integrity | The out-of-time split reproduces this pattern feature by fea… | 3.016 | ratio | psi | out_of_time | eq | `[[art:8cedaf79:psi.out_of_time.burnout]]` | verified | 3.016020048 |
| 106 | data_integrity | The out-of-time split reproduces this pattern feature by fea… | 1.68 | ratio | psi | out_of_time | eq | `[[art:ab2af3f2:psi.out_of_time.loan_age]]` | verified | 1.679868562 |
| 107 | data_integrity | The out-of-time split reproduces this pattern feature by fea… | 1.342 | ratio | psi | out_of_time | eq | `[[art:fc610fd1:psi.out_of_time.note_rate]]` | verified | 1.341893523 |
| 108 | data_integrity | The out-of-time split reproduces this pattern feature by fea… | 0.8734 | ratio | psi | out_of_time | eq | `[[art:ec6da34d:psi.out_of_time.incentive]]` | verified | 0.8734495361 |
| 109 | data_integrity | The out-of-time split reproduces this pattern feature by fea… | 0.8372 | ratio | psi | out_of_time | eq | `[[art:d39a4ced:psi.out_of_time.y_score]]` | verified | 0.8371883582 |
| 110 | data_integrity | The out-of-time split reproduces this pattern feature by fea… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 111 | data_integrity | The quieter out-of-time features stay below that bound: orig… | 0.08171 | ratio | psi | out_of_time | eq | `[[art:9ca9c306:psi.out_of_time.orig_upb_log]]` | verified | 0.08171063787 |
| 112 | data_integrity | The quieter out-of-time features stay below that bound: orig… | 0.07088 | ratio | psi | out_of_time | eq | `[[art:a7ef717f:psi.out_of_time.credit_score]]` | verified | 0.07088355626 |
| 113 | data_integrity | The quieter out-of-time features stay below that bound: orig… | 0.04332 | ratio | psi | out_of_time | eq | `[[art:7eedf98f:psi.out_of_time.orig_ltv]]` | verified | 0.04331914243 |
| 114 | data_integrity | The quieter out-of-time features stay below that bound: orig… | 0.02284 | ratio | psi | out_of_time | eq | `[[art:79f6f94a:psi.out_of_time.sato]]` | verified | 0.02284102604 |
| 115 | data_integrity | The quieter out-of-time features stay below that bound: orig… | 0.01631 | ratio | psi | out_of_time | eq | `[[art:fe2b0197:psi.out_of_time.season_sin]]` | verified | 0.01631255179 |
| 116 | data_integrity | The quieter out-of-time features stay below that bound: orig… | 0.004988 | ratio | psi | out_of_time | eq | `[[art:ef947d09:psi.out_of_time.season_cos]]` | verified | 0.004987781308 |
| 117 | data_integrity | These out-of-time breaches are read against the same declare… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 118 | data_integrity | The vintage holdout behaves differently, with every comparis… | 0.2743 | ratio | psi | vintage_holdout | eq | `[[art:d4e6aa9a:psi.vintage_holdout.note_rate]]` | verified | 0.2742521405 |
| 119 | data_integrity | The vintage holdout behaves differently, with every comparis… | 0.2101 | ratio | psi | vintage_holdout | eq | `[[art:1d339225:psi.vintage_holdout.incentive]]` | verified | 0.2100590512 |
| 120 | data_integrity | The vintage holdout behaves differently, with every comparis… | 0.08202 | ratio | psi | vintage_holdout | eq | `[[art:5d010092:psi.vintage_holdout.y_score]]` | verified | 0.0820229283 |
| 121 | data_integrity | The vintage holdout behaves differently, with every comparis… | 0.03575 | ratio | psi | vintage_holdout | eq | `[[art:1f0e3df0:psi.vintage_holdout.orig_ltv]]` | verified | 0.03575446718 |
| 122 | data_integrity | The vintage holdout behaves differently, with every comparis… | 0.03489 | ratio | psi | vintage_holdout | eq | `[[art:e579422e:psi.vintage_holdout.loan_age]]` | verified | 0.03488721615 |
| 123 | data_integrity | The vintage holdout behaves differently, with every comparis… | 0.03122 | ratio | psi | vintage_holdout | eq | `[[art:b2dacb71:psi.vintage_holdout.burnout]]` | verified | 0.03122017454 |
| 124 | data_integrity | The vintage holdout behaves differently, with every comparis… | 0.03038 | ratio | psi | vintage_holdout | eq | `[[art:10fd298a:psi.vintage_holdout.orig_upb_log]]` | verified | 0.03037586387 |
| 125 | data_integrity | The vintage holdout behaves differently, with every comparis… | 0.02841 | ratio | psi | vintage_holdout | eq | `[[art:6c4e561c:psi.vintage_holdout.sato]]` | verified | 0.02840898929 |
| 126 | data_integrity | The vintage holdout behaves differently, with every comparis… | 0.01929 | ratio | psi | vintage_holdout | eq | `[[art:16906529:psi.vintage_holdout.credit_score]]` | verified | 0.01928865688 |
| 127 | data_integrity | The vintage holdout behaves differently, with every comparis… | 0.00164 | ratio | psi | vintage_holdout | eq | `[[art:4482dc21:psi.vintage_holdout.season_cos]]` | verified | 0.001640289708 |
| 128 | data_integrity | The vintage holdout behaves differently, with every comparis… | 0.001971 | ratio | psi | vintage_holdout | eq | `[[art:836b68bf:psi.vintage_holdout.season_sin]]` | verified | 0.001971264046 |
| 129 | data_integrity | Note rate at 0.2743 sits above the declared bound of 0.25 an… | 0.2743 | ratio | psi | vintage_holdout | eq | `[[art:d4e6aa9a:psi.vintage_holdout.note_rate]]` | verified | 0.2742521405 |
| 130 | data_integrity | Note rate at 0.2743 sits above the declared bound of 0.25 an… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 131 | data_integrity | Incentive contributes the largest characteristic shift in th… | 0.9221 | ratio | csi |  | eq | `[[art:f430cc2d:csi.incentive]]` | verified | 0.9220903461 |
| 132 | data_integrity | Incentive contributes the largest characteristic shift in th… | 0.9221 | ratio | csi |  | eq | `[[art:d4b08859:csi.max]]` | verified | 0.9220903461 |
| 133 | data_integrity | Note rate contributes 0.4832 and burnout 0.3489 , both above… | 0.4832 | ratio | csi |  | eq | `[[art:a2be3f30:csi.note_rate]]` | verified | 0.4831662682 |
| 134 | data_integrity | Note rate contributes 0.4832 and burnout 0.3489 , both above… | 0.3489 | ratio | csi |  | eq | `[[art:e0f86ff2:csi.burnout]]` | verified | 0.3488802555 |
| 135 | data_integrity | Note rate contributes 0.4832 and burnout 0.3489 , both above… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 136 | data_integrity | The remaining contributions are smaller: credit score at 0.0… | 0.09087 | ratio | csi |  | eq | `[[art:4fbc434e:csi.credit_score]]` | verified | 0.09086513179 |
| 137 | data_integrity | The remaining contributions are smaller: credit score at 0.0… | 0.06562 | ratio | csi |  | eq | `[[art:ba82e949:csi.orig_upb_log]]` | verified | 0.06561601038 |
| 138 | data_integrity | The remaining contributions are smaller: credit score at 0.0… | 0.02303 | ratio | csi |  | eq | `[[art:af80429c:csi.orig_ltv]]` | verified | 0.02302783458 |
| 139 | data_integrity | The remaining contributions are smaller: credit score at 0.0… | 0.01316 | ratio | csi |  | eq | `[[art:ff10caf4:csi.season_sin]]` | verified | 0.01315757493 |
| 140 | data_integrity | The remaining contributions are smaller: credit score at 0.0… | 0.003265 | ratio | csi |  | eq | `[[art:49e6d56e:csi.season_cos]]` | verified | 0.003265173321 |
| 141 | data_integrity | The remaining contributions are smaller: credit score at 0.0… | 0.0001468 | ratio | csi |  | eq | `[[art:7d563a3f:csi.sato]]` | verified | 0.0001467991037 |
| 142 | data_integrity | The remaining contributions are smaller: credit score at 0.0… | 0 | ratio | csi |  | eq | `[[art:df52c920:csi.loan_age]]` | verified | 0 |
| 143 | data_integrity | Loan age is instructive: its population shift between train… | 1.68 | ratio | psi | test | eq | `[[art:987aabe4:psi.loan_age]]` | verified | 1.679868562 |
| 144 | data_integrity | Loan age is instructive: its population shift between train… | 0 | ratio | csi |  | eq | `[[art:df52c920:csi.loan_age]]` | verified | 0 |
| 145 | data_integrity | Incentive runs the other way, with a population shift of 0.8… | 0.8734 | ratio | psi | test | eq | `[[art:0f61188c:psi.incentive]]` | verified | 0.8734495361 |
| 146 | data_integrity | Incentive runs the other way, with a population shift of 0.8… | 0.9221 | ratio | csi |  | eq | `[[art:f430cc2d:csi.incentive]]` | verified | 0.9220903461 |
| 147 | data_integrity | The count of features declared as observed during the perfor… | 0 | count | n_flagged |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 148 | data_integrity | The strongest single feature reaches an AUC of 0.7422 , belo… | 0.7422 | ratio | single_feature_auc |  | eq | `[[art:b6b29a14:leakage.target_corr.max_single_feature_auc]]` | verified | 0.7422083739 |
| 149 | data_integrity | The strongest single feature reaches an AUC of 0.7422 , belo… | 0.9 | ratio | single_feature_auc |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 150 | data_integrity | The share of test rows whose feature values also appear in t… | 0 | ratio | overlap | test | eq | `[[art:4c9fcd09:leakage.overlap]]` | verified | 0 |
| 151 | data_integrity | The identifier arm of the contamination screen, the share of… | 0 | ratio | overlap_ids | test | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 152 | data_integrity | The identifier arm of the contamination screen, the share of… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 153 | data_integrity | The share of training rows whose feature values are not uniq… | 0 | ratio | duplicates | train | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 154 | data_integrity | The share of training rows whose feature values are not uniq… | 0.005 | ratio | overlap |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 155 | data_integrity | The feature-vector overlap is 0 , below that applied bound o… | 0 | ratio | overlap_features | test | eq | `[[art:0fec8048:leakage.overlap.features]]` | verified | 0 |
| 156 | data_integrity | The feature-vector overlap is 0 , below that applied bound o… | 0.005 | ratio | overlap |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 157 | data_integrity | The number of feature names matching the target-adjacent lex… | 0 | count | n_matched |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 158 | data_integrity | One finding is raised in this section, S1, population drift… | 3.016 | ratio | psi | test | eq | `[[art:1d35a583:psi.burnout]]` | verified | 3.016020048 |
| 159 | data_integrity | One finding is raised in this section, S1, population drift… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 160 | outcomes | The calibration slope, from the logistic regression of the o… | 1.015 | ratio | calibration_slope | train | eq | `[[art:6ee05ed8:calibration_slope.train]]` | verified | 1.015165743 |
| 161 | outcomes | The calibration slope, from the logistic regression of the o… | 0.9369 | ratio | calibration_slope | test | eq | `[[art:290cccd9:calibration_slope.test]]` | verified | 0.9368866293 |
| 162 | outcomes | The calibration slope, from the logistic regression of the o… | 0.9369 | ratio | calibration_slope | out_of_time | eq | `[[art:994798d5:calibration_slope.out_of_time]]` | verified | 0.9368866293 |
| 163 | outcomes | The calibration slope, from the logistic regression of the o… | 0.8554 | ratio | calibration_slope | vintage_holdout | eq | `[[art:6b42345a:calibration_slope.vintage_holdout]]` | verified | 0.8553956316 |
| 164 | outcomes | Each of those slopes sits inside the declared band running f… | 0.8 | ratio | calibration_slope |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 165 | outcomes | Each of those slopes sits inside the declared band running f… | 1.2 | ratio | calibration_slope |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 166 | outcomes | The intercept of the same regression is 0.06177 on train, -0… | 0.06177 | ratio | calibration_intercept | train | eq | `[[art:7184b1c0:calibration_intercept.train]]` | verified | 0.06176828223 |
| 167 | outcomes | The intercept of the same regression is 0.06177 on train, -0… | -0.4556 | ratio | calibration_intercept | test | eq | `[[art:256e21c4:calibration_intercept.test]]` | verified | -0.4555664421 |
| 168 | outcomes | The intercept of the same regression is 0.06177 on train, -0… | -0.4556 | ratio | calibration_intercept | out_of_time | eq | `[[art:8dc58882:calibration_intercept.out_of_time]]` | verified | -0.4555664421 |
| 169 | outcomes | The intercept of the same regression is 0.06177 on train, -0… | -0.8976 | ratio | calibration_intercept | vintage_holdout | eq | `[[art:21c5b98a:calibration_intercept.vintage_holdout]]` | verified | -0.8976276791 |
| 170 | outcomes | Mean predicted probability against the observed rate is 0.00… | 0.008333 | ratio | mean_predicted | train | eq | `[[art:4ea7b930:metrics.train.mean_predicted]]` | verified | 0.008332856538 |
| 171 | outcomes | Mean predicted probability against the observed rate is 0.00… | 0.008323 | ratio | event_rate | train | eq | `[[art:b0cf2348:metrics.train.event_rate]]` | verified | 0.008322892429 |
| 172 | outcomes | On test it is 0.02283 against 0.01795 . | 0.02283 | ratio | mean_predicted | test | eq | `[[art:1c1a1d8d:metrics.test.mean_predicted]]` | verified | 0.02282661269 |
| 173 | outcomes | On test it is 0.02283 against 0.01795 . | 0.01795 | ratio | event_rate | test | eq | `[[art:d222aedf:metrics.test.event_rate]]` | verified | 0.01794892714 |
| 174 | outcomes | Out of time it is 0.02283 against 0.01795 . | 0.02283 | ratio | mean_predicted | out_of_time | eq | `[[art:4d7aa98b:metrics.out_of_time.mean_predicted]]` | verified | 0.02282661269 |
| 175 | outcomes | Out of time it is 0.02283 against 0.01795 . | 0.01795 | ratio | event_rate | out_of_time | eq | `[[art:83ccf5c0:metrics.out_of_time.event_rate]]` | verified | 0.01794892714 |
| 176 | outcomes | On the vintage holdout it is 0.006157 against 0.004817 . | 0.006157 | ratio | mean_predicted | vintage_holdout | eq | `[[art:914aeeba:metrics.vintage_holdout.mean_predicted]]` | verified | 0.006157456637 |
| 177 | outcomes | On the vintage holdout it is 0.006157 against 0.004817 . | 0.004817 | ratio | event_rate | vintage_holdout | eq | `[[art:e3590a16:metrics.vintage_holdout.event_rate]]` | verified | 0.004817105386 |
| 178 | outcomes | Expressed relative to the observed rate, that gap is 0.00119… | 0.001197 | ratio | mean_rel_gap | train | eq | `[[art:7d19dc79:calibration.mean_rel_gap.train]]` | verified | 0.001197193051 |
| 179 | outcomes | Expressed relative to the observed rate, that gap is 0.00119… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 180 | outcomes | On test the relative gap is 0.2718 , above that tolerance of… | 0.2718 | ratio | mean_rel_gap | test | eq | `[[art:04dcea16:calibration.mean_rel_gap.test]]` | verified | 0.2717535987 |
| 181 | outcomes | On test the relative gap is 0.2718 , above that tolerance of… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 182 | outcomes | Out of time the relative gap is 0.2718 , likewise above the… | 0.2718 | ratio | mean_rel_gap | out_of_time | eq | `[[art:c5239af4:calibration.mean_rel_gap.out_of_time]]` | verified | 0.2717535987 |
| 183 | outcomes | On the vintage holdout the relative gap is 0.2782 , the larg… | 0.2782 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:2eba48c2:calibration.mean_rel_gap.vintage_holdout]]` | verified | 0.2782482723 |
| 184 | outcomes | Against realized prepayment speeds, the mean absolute differ… | 0.03373 | ratio | cpr_mae | train | eq | `[[art:609b1f19:cpr.train.mae]]` | verified | 0.03373481364 |
| 185 | outcomes | Against realized prepayment speeds, the mean absolute differ… | 0.06724 | ratio | cpr_mae | test | eq | `[[art:fe0e020a:cpr.test.mae]]` | verified | 0.06723889098 |
| 186 | outcomes | Against realized prepayment speeds, the mean absolute differ… | 0.06724 | ratio | cpr_mae | out_of_time | eq | `[[art:ed058023:cpr.out_of_time.mae]]` | verified | 0.06723889098 |
| 187 | outcomes | Against realized prepayment speeds, the mean absolute differ… | 0.03062 | ratio | cpr_mae | vintage_holdout | eq | `[[art:10b5118d:cpr.vintage_holdout.mae]]` | verified | 0.03061840342 |
| 188 | outcomes | \| AUC \| 0.8003 \| 0.7846 \| 0.7846 \| 0.7716 \| | 0.8003 | ratio | auc | train | eq | `[[art:41d3c4e6:metrics.train.auc]]` | verified | 0.8002919094 |
| 189 | outcomes | \| AUC \| 0.8003 \| 0.7846 \| 0.7846 \| 0.7716 \| | 0.7846 | ratio | auc | test | eq | `[[art:d57b2552:metrics.test.auc]]` | verified | 0.7846182604 |
| 190 | outcomes | \| AUC \| 0.8003 \| 0.7846 \| 0.7846 \| 0.7716 \| | 0.7846 | ratio | auc | out_of_time | eq | `[[art:ee898745:metrics.out_of_time.auc]]` | verified | 0.7846182604 |
| 191 | outcomes | \| AUC \| 0.8003 \| 0.7846 \| 0.7846 \| 0.7716 \| | 0.7716 | ratio | auc | vintage_holdout | eq | `[[art:610c13fd:metrics.vintage_holdout.auc]]` | verified | 0.7716058113 |
| 192 | outcomes | \| Gini \| 0.6006 \| 0.5692 \| 0.5692 \| 0.5432 \| | 0.6006 | ratio | gini | train | eq | `[[art:66b6cc81:metrics.train.gini]]` | verified | 0.6005838187 |
| 193 | outcomes | \| Gini \| 0.6006 \| 0.5692 \| 0.5692 \| 0.5432 \| | 0.5692 | ratio | gini | test | eq | `[[art:1291e305:metrics.test.gini]]` | verified | 0.5692365207 |
| 194 | outcomes | \| Gini \| 0.6006 \| 0.5692 \| 0.5692 \| 0.5432 \| | 0.5692 | ratio | gini | out_of_time | eq | `[[art:46899ec9:metrics.out_of_time.gini]]` | verified | 0.5692365207 |
| 195 | outcomes | \| Gini \| 0.6006 \| 0.5692 \| 0.5692 \| 0.5432 \| | 0.5432 | ratio | gini | vintage_holdout | eq | `[[art:4b1525bb:metrics.vintage_holdout.gini]]` | verified | 0.5432116227 |
| 196 | outcomes | \| KS \| 0.474 \| 0.4373 \| 0.4373 \| 0.4618 \| | 0.474 | ratio | ks | train | eq | `[[art:3e0b8829:metrics.train.ks]]` | verified | 0.4740174906 |
| 197 | outcomes | \| KS \| 0.474 \| 0.4373 \| 0.4373 \| 0.4618 \| | 0.4373 | ratio | ks | test | eq | `[[art:857a0cf9:metrics.test.ks]]` | verified | 0.4373216673 |
| 198 | outcomes | \| KS \| 0.474 \| 0.4373 \| 0.4373 \| 0.4618 \| | 0.4373 | ratio | ks | out_of_time | eq | `[[art:6360ccf9:metrics.out_of_time.ks]]` | verified | 0.4373216673 |
| 199 | outcomes | \| KS \| 0.474 \| 0.4373 \| 0.4373 \| 0.4618 \| | 0.4618 | ratio | ks | vintage_holdout | eq | `[[art:c3ac5a54:metrics.vintage_holdout.ks]]` | verified | 0.4617647948 |
| 200 | outcomes | \| Brier \| 0.008111 \| 0.01725 \| 0.01725 \| 0.004767 \| | 0.008111 | ratio | brier | train | eq | `[[art:e9077291:metrics.train.brier]]` | verified | 0.008111422906 |
| 201 | outcomes | \| Brier \| 0.008111 \| 0.01725 \| 0.01725 \| 0.004767 \| | 0.01725 | ratio | brier | test | eq | `[[art:68e8b1cf:metrics.test.brier]]` | verified | 0.01725186302 |
| 202 | outcomes | \| Brier \| 0.008111 \| 0.01725 \| 0.01725 \| 0.004767 \| | 0.01725 | ratio | brier | out_of_time | eq | `[[art:f0fd020a:metrics.out_of_time.brier]]` | verified | 0.01725186302 |
| 203 | outcomes | \| Brier \| 0.008111 \| 0.01725 \| 0.01725 \| 0.004767 \| | 0.004767 | ratio | brier | vintage_holdout | eq | `[[art:115af096:metrics.vintage_holdout.brier]]` | verified | 0.004766820283 |
| 204 | outcomes | \| Log loss \| 0.04279 \| 0.0805 \| 0.0805 \| 0.02818 \| | 0.04279 | ratio | logloss | train | eq | `[[art:e62507ab:metrics.train.logloss]]` | verified | 0.04279363896 |
| 205 | outcomes | \| Log loss \| 0.04279 \| 0.0805 \| 0.0805 \| 0.02818 \| | 0.0805 | ratio | logloss | test | eq | `[[art:c576b630:metrics.test.logloss]]` | verified | 0.08050056271 |
| 206 | outcomes | \| Log loss \| 0.04279 \| 0.0805 \| 0.0805 \| 0.02818 \| | 0.0805 | ratio | logloss | out_of_time | eq | `[[art:205ce509:metrics.out_of_time.logloss]]` | verified | 0.08050056271 |
| 207 | outcomes | \| Log loss \| 0.04279 \| 0.0805 \| 0.0805 \| 0.02818 \| | 0.02818 | ratio | logloss | vintage_holdout | eq | `[[art:96a19aae:metrics.vintage_holdout.logloss]]` | verified | 0.02818314174 |
| 208 | outcomes | \| Observations \| 33522 \| 12257 \| 12257 \| 32177 \| | 33522 | count | n | train | eq | `[[art:dd20fa4c:metrics.train.n]]` | verified | 33522 |
| 209 | outcomes | \| Observations \| 33522 \| 12257 \| 12257 \| 32177 \| | 12257 | count | n | test | eq | `[[art:90b46eb1:metrics.test.n]]` | verified | 12257 |
| 210 | outcomes | \| Observations \| 33522 \| 12257 \| 12257 \| 32177 \| | 12257 | count | n | out_of_time | eq | `[[art:7898809e:metrics.out_of_time.n]]` | verified | 12257 |
| 211 | outcomes | \| Observations \| 33522 \| 12257 \| 12257 \| 32177 \| | 32177 | count | n | vintage_holdout | eq | `[[art:37a92951:metrics.vintage_holdout.n]]` | verified | 32177 |
| 212 | outcomes | Train AUC of 0.8003 stands above test AUC of 0.7846 , and th… | 0.8003 | ratio | auc | train | eq | `[[art:41d3c4e6:metrics.train.auc]]` | verified | 0.8002919094 |
| 213 | outcomes | Train AUC of 0.8003 stands above test AUC of 0.7846 , and th… | 0.7846 | ratio | auc | test | eq | `[[art:d57b2552:metrics.test.auc]]` | verified | 0.7846182604 |
| 214 | outcomes | Train AUC of 0.8003 stands above test AUC of 0.7846 , and th… | 0.08 | ratio | auc_gap |  | eq | `[[art:630f28f4:threshold.O1.auc_gap]]` | verified | 0.08 |
| 215 | outcomes | The out-of-time AUC of 0.7846 and the vintage holdout AUC of… | 0.7846 | ratio | auc | out_of_time | eq | `[[art:ee898745:metrics.out_of_time.auc]]` | verified | 0.7846182604 |
| 216 | outcomes | The out-of-time AUC of 0.7846 and the vintage holdout AUC of… | 0.7716 | ratio | auc | vintage_holdout | eq | `[[art:610c13fd:metrics.vintage_holdout.auc]]` | verified | 0.7716058113 |
| 217 | outcomes | The out-of-time AUC of 0.7846 and the vintage holdout AUC of… | 0.05 | ratio | holdout_gap |  | eq | `[[art:90f8b6d9:threshold.O1.holdout_gap]]` | verified | 0.05 |
| 218 | outcomes | The table shows the recomputed test AUC of 0.7846 above the… | 0.7846 | ratio | auc | test | eq | `[[art:d57b2552:metrics.test.auc]]` | verified | 0.7846182604 |
| 219 | outcomes | The table shows the recomputed test AUC of 0.7846 above the… | 0.65 | ratio | auc | test | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 220 | outcomes | The table shows the recomputed test AUC of 0.7846 above the… | 0.9369 | ratio | calibration_slope | test | eq | `[[art:290cccd9:calibration_slope.test]]` | verified | 0.9368866293 |
| 221 | outcomes | The table shows the recomputed test AUC of 0.7846 above the… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 222 | outcomes | The table shows the recomputed test AUC of 0.7846 above the… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 223 | outcomes | The declared stability bound of 0.25 is the one the recomput… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 224 | outcomes | The declared stability bound of 0.25 is the one the recomput… | 3.016 | ratio | psi |  | eq | `[[art:4fae32c6:psi.max]]` | verified | 3.016020048 |
| 225 | outcomes | On this slice the AUC falls below the split's own by 0.03243… | 0.03243 | ratio | auc_gap | train | eq | `[[art:a18d63eb:metrics.train.sub.burnout_high.auc_gap]]` | verified | 0.03243264786 |
| 226 | outcomes | On this slice the AUC falls below the split's own by 0.03243… | 0.008195 | ratio | auc_gap | test | eq | `[[art:ad1d8f68:metrics.test.sub.burnout_high.auc_gap]]` | verified | 0.00819466047 |
| 227 | outcomes | On this slice the AUC falls below the split's own by 0.03243… | 0.008195 | ratio | auc_gap | out_of_time | eq | `[[art:c93b5fc8:metrics.out_of_time.sub.burnout_high.auc_gap]]` | verified | 0.00819466047 |
| 228 | outcomes | On this slice the AUC falls below the split's own by 0.03243… | 0.03995 | ratio | auc_gap | vintage_holdout | eq | `[[art:f49dd552:metrics.vintage_holdout.sub.burnout_high.auc_gap]]` | verified | 0.03995268778 |
| 229 | outcomes | On this slice the AUC falls below the split's own by 0.03243… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 230 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.5 of out of tim… | 0.5 | ratio | share | train | eq | `[[art:e7e14804:metrics.train.sub.burnout_high.share]]` | verified | 0.5 |
| 231 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.5 of out of tim… | 0.5 | ratio | share | test | eq | `[[art:efeac6e1:metrics.test.sub.burnout_high.share]]` | verified | 0.499959207 |
| 232 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.5 of out of tim… | 0.5 | ratio | share | out_of_time | eq | `[[art:b5c30bbc:metrics.out_of_time.sub.burnout_high.share]]` | verified | 0.499959207 |
| 233 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.5 of out of tim… | 0.5 | ratio | share | vintage_holdout | eq | `[[art:379549be:metrics.vintage_holdout.sub.burnout_high.share]]` | verified | 0.499984461 |
| 234 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.5 of out of tim… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 235 | outcomes | Mean predicted against the observed rate on the slice gives… | 0.009235 | ratio | mean_rel_gap | train | eq | `[[art:d3a62f43:metrics.train.sub.burnout_high.mean_rel_gap]]` | verified | 0.009235116294 |
| 236 | outcomes | Mean predicted against the observed rate on the slice gives… | 0.641 | ratio | mean_rel_gap | test | eq | `[[art:668dd56c:metrics.test.sub.burnout_high.mean_rel_gap]]` | verified | 0.6410194511 |
| 237 | outcomes | Mean predicted against the observed rate on the slice gives… | 0.641 | ratio | mean_rel_gap | out_of_time | eq | `[[art:e79c0bd2:metrics.out_of_time.sub.burnout_high.mean_rel_gap]]` | verified | 0.6410194511 |
| 238 | outcomes | Mean predicted against the observed rate on the slice gives… | 0.1335 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:4ef00612:metrics.vintage_holdout.sub.burnout_high.mean_rel_gap]]` | verified | 0.1334945197 |
| 239 | outcomes | Because the AUC shortfalls stay within the slice bound while… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 240 | outcomes | Here the AUC falls below the split's own by 0.05101 on train… | 0.05101 | ratio | auc_gap | train | eq | `[[art:d6960b9c:metrics.train.sub.burnout_low.auc_gap]]` | verified | 0.05100723122 |
| 241 | outcomes | Here the AUC falls below the split's own by 0.05101 on train… | 0.0231 | ratio | auc_gap | vintage_holdout | eq | `[[art:d85223fe:metrics.vintage_holdout.sub.burnout_low.auc_gap]]` | verified | 0.02310435431 |
| 242 | outcomes | Here the AUC falls below the split's own by 0.05101 on train… | -0.02731 | ratio | auc_gap | test | eq | `[[art:c6967420:metrics.test.sub.burnout_low.auc_gap]]` | verified | -0.02731220276 |
| 243 | outcomes | Here the AUC falls below the split's own by 0.05101 on train… | -0.02731 | ratio | auc_gap | out_of_time | eq | `[[art:414188ff:metrics.out_of_time.sub.burnout_low.auc_gap]]` | verified | -0.02731220276 |
| 244 | outcomes | Here the AUC falls below the split's own by 0.05101 on train… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 245 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.5 of out of tim… | 0.5 | ratio | share | train | eq | `[[art:a4cc9400:metrics.train.sub.burnout_low.share]]` | verified | 0.5 |
| 246 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.5 of out of tim… | 0.5 | ratio | share | test | eq | `[[art:4307ceba:metrics.test.sub.burnout_low.share]]` | verified | 0.500040793 |
| 247 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.5 of out of tim… | 0.5 | ratio | share | out_of_time | eq | `[[art:d6102b4a:metrics.out_of_time.sub.burnout_low.share]]` | verified | 0.500040793 |
| 248 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.5 of out of tim… | 0.5 | ratio | share | vintage_holdout | eq | `[[art:b327a747:metrics.vintage_holdout.sub.burnout_low.share]]` | verified | 0.500015539 |
| 249 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.5 of out of tim… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 250 | outcomes | Mean predicted against the observed rate gives a relative ga… | 0.02636 | ratio | mean_rel_gap | train | eq | `[[art:e08aba69:metrics.train.sub.burnout_low.mean_rel_gap]]` | verified | 0.02636140092 |
| 251 | outcomes | Mean predicted against the observed rate gives a relative ga… | 0.1633 | ratio | mean_rel_gap | test | eq | `[[art:64191da8:metrics.test.sub.burnout_low.mean_rel_gap]]` | verified | 0.1633220095 |
| 252 | outcomes | Mean predicted against the observed rate gives a relative ga… | 0.1633 | ratio | mean_rel_gap | out_of_time | eq | `[[art:6355b95b:metrics.out_of_time.sub.burnout_low.mean_rel_gap]]` | verified | 0.1633220095 |
| 253 | outcomes | Mean predicted against the observed rate gives a relative ga… | 0.8134 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:b9abef02:metrics.vintage_holdout.sub.burnout_low.mean_rel_gap]]` | verified | 0.8133985092 |
| 254 | outcomes | Comparing the two burnout halves on the relative mean gap, t… | 0.641 | ratio | mean_rel_gap | test | eq | `[[art:668dd56c:metrics.test.sub.burnout_high.mean_rel_gap]]` | verified | 0.6410194511 |
| 255 | outcomes | Comparing the two burnout halves on the relative mean gap, t… | 0.1633 | ratio | mean_rel_gap | test | eq | `[[art:64191da8:metrics.test.sub.burnout_low.mean_rel_gap]]` | verified | 0.1633220095 |
| 256 | outcomes | Comparing the two burnout halves on the relative mean gap, t… | 0.8134 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:b9abef02:metrics.vintage_holdout.sub.burnout_low.mean_rel_gap]]` | verified | 0.8133985092 |
| 257 | outcomes | Comparing the two burnout halves on the relative mean gap, t… | 0.1335 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:4ef00612:metrics.vintage_holdout.sub.burnout_high.mean_rel_gap]]` | verified | 0.1334945197 |
| 258 | outcomes | The slice's AUC falls below the split's own by 0.05065 on tr… | 0.05065 | ratio | auc_gap | train | eq | `[[art:1eb21997:metrics.train.sub.incentive_high.auc_gap]]` | verified | 0.05064713955 |
| 259 | outcomes | The slice's AUC falls below the split's own by 0.05065 on tr… | 0.04024 | ratio | auc_gap | test | eq | `[[art:fa601af0:metrics.test.sub.incentive_high.auc_gap]]` | verified | 0.04024472996 |
| 260 | outcomes | The slice's AUC falls below the split's own by 0.05065 on tr… | 0.04024 | ratio | auc_gap | out_of_time | eq | `[[art:81bf8d6d:metrics.out_of_time.sub.incentive_high.auc_gap]]` | verified | 0.04024472996 |
| 261 | outcomes | The slice's AUC falls below the split's own by 0.05065 on tr… | 0.01615 | ratio | auc_gap | vintage_holdout | eq | `[[art:2853b3a5:metrics.vintage_holdout.sub.incentive_high.auc_gap]]` | verified | 0.01615104629 |
| 262 | outcomes | The slice's AUC falls below the split's own by 0.05065 on tr… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 263 | outcomes | The slice holds 0.5 of train, 0.4999 of test, 0.4999 of out… | 0.5 | ratio | share | train | eq | `[[art:64a6d28c:metrics.train.sub.incentive_high.share]]` | verified | 0.5 |
| 264 | outcomes | The slice holds 0.5 of train, 0.4999 of test, 0.4999 of out… | 0.4999 | ratio | share | test | eq | `[[art:a2b45314:metrics.test.sub.incentive_high.share]]` | verified | 0.499877621 |
| 265 | outcomes | The slice holds 0.5 of train, 0.4999 of test, 0.4999 of out… | 0.4999 | ratio | share | out_of_time | eq | `[[art:431d1ff2:metrics.out_of_time.sub.incentive_high.share]]` | verified | 0.499877621 |
| 266 | outcomes | The slice holds 0.5 of train, 0.4999 of test, 0.4999 of out… | 0.5 | ratio | share | vintage_holdout | eq | `[[art:cb627056:metrics.vintage_holdout.sub.incentive_high.share]]` | verified | 0.499984461 |
| 267 | outcomes | The slice holds 0.5 of train, 0.4999 of test, 0.4999 of out… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 268 | outcomes | Mean predicted against the observed rate gives a relative ga… | 0.003817 | ratio | mean_rel_gap | train | eq | `[[art:957b62eb:metrics.train.sub.incentive_high.mean_rel_gap]]` | verified | 0.003817038981 |
| 269 | outcomes | Mean predicted against the observed rate gives a relative ga… | 0.369 | ratio | mean_rel_gap | test | eq | `[[art:2d6199b1:metrics.test.sub.incentive_high.mean_rel_gap]]` | verified | 0.3689915805 |
| 270 | outcomes | Mean predicted against the observed rate gives a relative ga… | 0.369 | ratio | mean_rel_gap | out_of_time | eq | `[[art:7c011df6:metrics.out_of_time.sub.incentive_high.mean_rel_gap]]` | verified | 0.3689915805 |
| 271 | outcomes | Mean predicted against the observed rate gives a relative ga… | 0.3916 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:bb893376:metrics.vintage_holdout.sub.incentive_high.mean_rel_gap]]` | verified | 0.3916330365 |
| 272 | outcomes | Mean predicted against the observed rate gives a relative ga… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 273 | sensitivity | The largest variance inflation factor across the retained fe… | 4.288 | ratio | vif |  | eq | `[[art:fecfb289:vif.max]]` | verified | 4.288168629 |
| 274 | sensitivity | The largest variance inflation factor across the retained fe… | 10 | ratio | vif |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 275 | sensitivity | That maximum is attained by the note rate at 4.288 , the fea… | 4.288 | ratio | vif |  | eq | `[[art:1113d019:vif.note_rate]]` | verified | 4.288168629 |
| 276 | sensitivity | The remaining factors are 3.601 for burnout , 2.593 for loan… | 3.601 | ratio | vif |  | eq | `[[art:127bbabe:vif.burnout]]` | verified | 3.601072256 |
| 277 | sensitivity | The remaining factors are 3.601 for burnout , 2.593 for loan… | 2.593 | ratio | vif |  | eq | `[[art:b30f78aa:vif.loan_age]]` | verified | 2.593200289 |
| 278 | sensitivity | The remaining factors are 3.601 for burnout , 2.593 for loan… | 2.195 | ratio | vif |  | eq | `[[art:60c8eef8:vif.incentive]]` | verified | 2.195314756 |
| 279 | sensitivity | The remaining factors are 3.601 for burnout , 2.593 for loan… | 1.627 | ratio | vif |  | eq | `[[art:4b2ebef2:vif.sato]]` | verified | 1.627027838 |
| 280 | sensitivity | The remaining factors are 3.601 for burnout , 2.593 for loan… | 1.014 | ratio | vif |  | eq | `[[art:d9449fe2:vif.orig_ltv]]` | verified | 1.013521613 |
| 281 | sensitivity | The remaining factors are 3.601 for burnout , 2.593 for loan… | 1.012 | ratio | vif |  | eq | `[[art:59e2ab98:vif.orig_upb_log]]` | verified | 1.012256745 |
| 282 | sensitivity | The remaining factors are 3.601 for burnout , 2.593 for loan… | 1.011 | ratio | vif |  | eq | `[[art:1f19769b:vif.credit_score]]` | verified | 1.011319432 |
| 283 | sensitivity | The remaining factors are 3.601 for burnout , 2.593 for loan… | 1.011 | ratio | vif |  | eq | `[[art:3b05b05a:vif.season_sin]]` | verified | 1.010543525 |
| 284 | sensitivity | The remaining factors are 3.601 for burnout , 2.593 for loan… | 1.007 | ratio | vif |  | eq | `[[art:f741ba51:vif.season_cos]]` | verified | 1.007021417 |
| 285 | sensitivity | Belsley's condition number of the column-standardised design… | 4.778 | ratio | condition_number |  | eq | `[[art:5e2416a9:condition_number]]` | verified | 4.777601017 |
| 286 | sensitivity | Belsley's condition number of the column-standardised design… | 30 | ratio | condition_number |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 287 | sensitivity | The champion's discrimination within each declared rate regi… | 0.1 | ratio | auc_gap |  | eq | `[[art:b64213d7:threshold.R1.auc_gap]]` | verified | 0.1 |
| 288 | sensitivity | Coefficient stability is assessed by a sign-flip test that c… | 0.05 | ratio | sign_flip_coef |  | eq | `[[art:aca84377:threshold.R1.sign_flip_coef]]` | verified | 0.05 |
| 289 | sensitivity | Coefficient stability is assessed by a sign-flip test that c… | 2 | ratio | sign_flip_z |  | eq | `[[art:2e4428c7:threshold.R1.sign_flip_z]]` | verified | 2 |
| 290 | sensitivity | On that test the indicator is 0 for the note rate , 0 for th… | 0 | ratio | sign_flip |  | eq | `[[art:e7ce4912:stability.note_rate.sign_flip]]` | verified | 0 |
| 291 | sensitivity | On that test the indicator is 0 for the note rate , 0 for th… | 0 | ratio | sign_flip |  | eq | `[[art:0cc7a37d:stability.incentive.sign_flip]]` | verified | 0 |
| 292 | sensitivity | On that test the indicator is 0 for the note rate , 0 for th… | 0 | ratio | sign_flip |  | eq | `[[art:6bc05e82:stability.burnout.sign_flip]]` | verified | 0 |
| 293 | sensitivity | On that test the indicator is 0 for the note rate , 0 for th… | 0 | ratio | sign_flip |  | eq | `[[art:b7191217:stability.loan_age.sign_flip]]` | verified | 0 |
| 294 | sensitivity | On that test the indicator is 0 for the note rate , 0 for th… | 0 | ratio | sign_flip |  | eq | `[[art:1f302ccd:stability.sato.sign_flip]]` | verified | 0 |
| 295 | sensitivity | On that test the indicator is 0 for the note rate , 0 for th… | 0 | ratio | sign_flip |  | eq | `[[art:d956c276:stability.credit_score.sign_flip]]` | verified | 0 |
| 296 | sensitivity | On that test the indicator is 0 for the note rate , 0 for th… | 0 | ratio | sign_flip |  | eq | `[[art:054d5fab:stability.orig_ltv.sign_flip]]` | verified | 0 |
| 297 | sensitivity | On that test the indicator is 0 for the note rate , 0 for th… | 0 | ratio | sign_flip |  | eq | `[[art:fb1ae6c8:stability.orig_upb_log.sign_flip]]` | verified | 0 |
| 298 | sensitivity | On that test the indicator is 0 for the note rate , 0 for th… | 0 | ratio | sign_flip |  | eq | `[[art:6ba36a3b:stability.season_sin.sign_flip]]` | verified | 0 |
| 299 | sensitivity | On that test the indicator is 0 for the note rate , 0 for th… | 0 | ratio | sign_flip |  | eq | `[[art:1850e2de:stability.season_cos.sign_flip]]` | verified | 0 |
| 300 | sensitivity | At the extreme downward shock the change in servicing value… | -1166000 | currency | value_change |  | eq | `[[art:dfaf9b49:scenario.value_change.-300]]` | verified | -1166173.182 |
| 301 | sensitivity | At the extreme downward shock the change in servicing value… | 71320 | currency | value_change |  | eq | `[[art:1bebd745:scenario.value_change.300]]` | verified | 71316.75564 |
| 302 | sensitivity | The base case is anchored at 0 by construction, and the valu… | 0 | currency | value_change |  | eq | `[[art:1e1b0b88:scenario.value_change.0]]` | verified | 0 |
| 303 | sensitivity | The convexity measure, formed as the change at the extreme d… | -1095000 | currency | convexity |  | eq | `[[art:70b14b4a:scenario.convexity]]` | verified | -1094856.426 |
| 304 | findings | The package declares a maximum of 0.25 for the population st… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 305 | findings | The package declares a maximum of 0.25 for the population st… | 3.016 | ratio | psi |  | eq | `[[art:4fae32c6:psi.max]]` | verified | 3.016020048 |
| 306 | findings | The developer should either re-establish the model on data w… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 307 | findings | Against a threshold of 0.25 , the population stability index… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 308 | findings | Against a threshold of 0.25 , the population stability index… | 3.016 | ratio | psi |  | eq | `[[art:1d35a583:psi.burnout]]` | verified | 3.016020048 |
| 309 | findings | The same index is 1.68 on `loan_age`, 1.342 on `note_rate`,… | 1.68 | ratio | psi |  | eq | `[[art:987aabe4:psi.loan_age]]` | verified | 1.679868562 |
| 310 | findings | The same index is 1.68 on `loan_age`, 1.342 on `note_rate`,… | 1.342 | ratio | psi |  | eq | `[[art:2f1cb70b:psi.note_rate]]` | verified | 1.341893523 |
| 311 | findings | The same index is 1.68 on `loan_age`, 1.342 on `note_rate`,… | 0.8734 | ratio | psi |  | eq | `[[art:0f61188c:psi.incentive]]` | verified | 0.8734495361 |
| 312 | findings | The score's own distribution moves as well, at 0.8372 , abov… | 0.8372 | ratio | psi |  | eq | `[[art:92ac1652:psi.y_score]]` | verified | 0.8371883582 |
| 313 | findings | The score's own distribution moves as well, at 0.8372 , abov… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 314 | findings | Against a relative tolerance of 0.25 , the mean predicted pr… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 315 | findings | Against a relative tolerance of 0.25 , the mean predicted pr… | 0.02283 | ratio | mean_predicted | test | eq | `[[art:1c1a1d8d:metrics.test.mean_predicted]]` | verified | 0.02282661269 |
| 316 | findings | Against a relative tolerance of 0.25 , the mean predicted pr… | 0.01795 | ratio | event_rate | test | eq | `[[art:d222aedf:metrics.test.event_rate]]` | verified | 0.01794892714 |
| 317 | findings | Against a relative tolerance of 0.25 , the mean predicted pr… | 0.2718 | ratio | mean_rel_gap | test | eq | `[[art:04dcea16:calibration.mean_rel_gap.test]]` | verified | 0.2717535987 |
| 318 | findings | On out_of_time the mean predicted probability is 0.02283 aga… | 0.02283 | ratio | mean_predicted | out_of_time | eq | `[[art:4d7aa98b:metrics.out_of_time.mean_predicted]]` | verified | 0.02282661269 |
| 319 | findings | On out_of_time the mean predicted probability is 0.02283 aga… | 0.01795 | ratio | event_rate | out_of_time | eq | `[[art:83ccf5c0:metrics.out_of_time.event_rate]]` | verified | 0.01794892714 |
| 320 | findings | On out_of_time the mean predicted probability is 0.02283 aga… | 0.2718 | ratio | mean_rel_gap | out_of_time | eq | `[[art:c5239af4:calibration.mean_rel_gap.out_of_time]]` | verified | 0.2717535987 |
| 321 | findings | On vintage_holdout the mean predicted probability is 0.00615… | 0.006157 | ratio | mean_predicted | vintage_holdout | eq | `[[art:914aeeba:metrics.vintage_holdout.mean_predicted]]` | verified | 0.006157456637 |
| 322 | findings | On vintage_holdout the mean predicted probability is 0.00615… | 0.004817 | ratio | event_rate | vintage_holdout | eq | `[[art:e3590a16:metrics.vintage_holdout.event_rate]]` | verified | 0.004817105386 |
| 323 | findings | On vintage_holdout the mean predicted probability is 0.00615… | 0.2782 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:2eba48c2:calibration.mean_rel_gap.vintage_holdout]]` | verified | 0.2782482723 |
| 324 | findings | The developer should recalibrate the output level against ob… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 325 | findings | Given that the fitted coefficient on `note_rate` carries sig… | -1 | ratio | coef_sign |  | eq | `[[art:aecf7ccb:sign_check.note_rate.coef_sign]]` | verified | -1 |
| 326 | findings | Given that the fitted coefficient on `note_rate` carries sig… | 1 | ratio | univariate_direction |  | eq | `[[art:61f6e1ac:sign_check.note_rate.univariate_direction]]` | verified | 1 |
| 327 | findings | Given that the fitted coefficient on `note_rate` carries sig… | 0 | ratio | agrees |  | eq | `[[art:a453463d:sign_check.note_rate.agrees]]` | verified | 0 |
| 328 | monitoring | Calibration on each production vintage should be tracked as… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 329 | monitoring | Calibration on each production vintage should be tracked as… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 330 | monitoring | The value observed in this validation, 0.9369 , sits inside… | 0.9369 | ratio | calibration_slope | test | eq | `[[art:290cccd9:calibration_slope.test]]` | verified | 0.9368866293 |
| 331 | monitoring | Discrimination should be tracked as AUC on each vintage agai… | 0.65 | ratio | auc | test | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 332 | monitoring | Discrimination should be tracked as AUC on each vintage agai… | 0.7846 | ratio | auc | test | eq | `[[art:d57b2552:metrics.test.auc]]` | verified | 0.7846182604 |
| 333 | monitoring | Population and score stability should be tracked as PSI agai… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 334 | monitoring | The largest train-to-test value seen in this validation, 3.0… | 3.016 | ratio | psi |  | eq | `[[art:4fae32c6:psi.max]]` | verified | 3.016020048 |

## Appendix B — Artifact index

The store holds 419 artifacts; the 257 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `ablation.baseline_auc` | `93dda83a` | scalar | 0.7802163028 | AUC on test of a refit of the champion's functional form on every retained feature, the level each ablation delta is measured from |
| `ablation.burnout.delta_auc` | `8aa8bccf` | scalar | 0.00429206915 | change in test AUC when the champion's form is refitted without burnout |
| `ablation.credit_score.delta_auc` | `a2d10cd7` | scalar | -0.02980393786 | change in test AUC when the champion's form is refitted without credit_score |
| `ablation.incentive.delta_auc` | `46802ce1` | scalar | -0.07943499966 | change in test AUC when the champion's form is refitted without incentive |
| `ablation.loan_age.delta_auc` | `ca8fa8e9` | scalar | -0.009945848784 | change in test AUC when the champion's form is refitted without loan_age |
| `ablation.note_rate.delta_auc` | `338b461a` | scalar | 0.005792367473 | change in test AUC when the champion's form is refitted without note_rate |
| `ablation.orig_ltv.delta_auc` | `84275e57` | scalar | -0.01199332362 | change in test AUC when the champion's form is refitted without orig_ltv |
| `ablation.orig_upb_log.delta_auc` | `6158bf75` | scalar | -0.01681104473 | change in test AUC when the champion's form is refitted without orig_upb_log |
| `ablation.sato.delta_auc` | `c9eb03ef` | scalar | -0.004237313737 | change in test AUC when the champion's form is refitted without sato |
| `ablation.season_cos.delta_auc` | `bdbbba37` | scalar | -0.005672283187 | change in test AUC when the champion's form is refitted without season_cos |
| `ablation.season_sin.delta_auc` | `95e1e0c6` | scalar | 0.0005400016615 | change in test AUC when the champion's form is refitted without season_sin |
| `calibration.mean_rel_gap.out_of_time` | `c5239af4` | scalar | 0.2717535987 | mean predicted against observed on out_of_time, relative |
| `calibration.mean_rel_gap.test` | `04dcea16` | scalar | 0.2717535987 | mean predicted against observed on test, relative |
| `calibration.mean_rel_gap.train` | `7d19dc79` | scalar | 0.001197193051 | mean predicted against observed on train, relative |
| `calibration.mean_rel_gap.vintage_holdout` | `2eba48c2` | scalar | 0.2782482723 | mean predicted against observed on vintage_holdout, relative |
| `calibration.out_of_time` | `a16e1248` | table | table, 10 rows | calibration by decile of predicted probability on out_of_time |
| `calibration.test` | `07848a4c` | table | table, 10 rows | calibration by decile of predicted probability on test |
| `calibration.vintage_holdout` | `a402f077` | table | table, 10 rows | calibration by decile of predicted probability on vintage_holdout |
| `calibration_intercept.out_of_time` | `8dc58882` | scalar | -0.4555664421 | logistic regression of the outcome on logit(p) on out_of_time: the intercept |
| `calibration_intercept.test` | `256e21c4` | scalar | -0.4555664421 | logistic regression of the outcome on logit(p) on test: the intercept |
| `calibration_intercept.train` | `7184b1c0` | scalar | 0.06176828223 | logistic regression of the outcome on logit(p) on train: the intercept |
| `calibration_intercept.vintage_holdout` | `21c5b98a` | scalar | -0.8976276791 | logistic regression of the outcome on logit(p) on vintage_holdout: the intercept |
| `calibration_slope.out_of_time` | `994798d5` | scalar | 0.9368866293 | logistic regression of the outcome on logit(p) on out_of_time: the slope |
| `calibration_slope.test` | `290cccd9` | scalar | 0.9368866293 | logistic regression of the outcome on logit(p) on test: the slope |
| `calibration_slope.train` | `6ee05ed8` | scalar | 1.015165743 | logistic regression of the outcome on logit(p) on train: the slope |
| `calibration_slope.vintage_holdout` | `6b42345a` | scalar | 0.8553956316 | logistic regression of the outcome on logit(p) on vintage_holdout: the slope |
| `challenger.auc` | `489cd7a6` | scalar | 0.7210566662 | the challenger's AUC on test |
| `challenger.brier` | `36aa75c4` | scalar | 0.02173012265 | the challenger's Brier score on test |
| `challenger.delta_auc` | `7e119a34` | scalar | -0.06356159418 | the challenger's AUC on test minus the champion's |
| `condition_number` | `5e2416a9` | scalar | 4.777601017 | Belsley's condition number of the column-standardised design |
| `cpr.out_of_time.mae` | `ed058023` | scalar | 0.06723889098 | mean absolute difference between actual and predicted CPR on out_of_time |
| `cpr.test` | `81cf8976` | table | table, 36 rows | actual against predicted CPR by period on test |
| `cpr.test.mae` | `fe0e020a` | scalar | 0.06723889098 | mean absolute difference between actual and predicted CPR on test |
| `cpr.train.mae` | `609b1f19` | scalar | 0.03373481364 | mean absolute difference between actual and predicted CPR on train |
| `cpr.vintage_holdout.mae` | `10b5118d` | scalar | 0.03061840342 | mean absolute difference between actual and predicted CPR on vintage_holdout |
| `csi.burnout` | `e0f86ff2` | scalar | 0.3488802555 | CSI of burnout: its contribution to the shift in the linear predictor |
| `csi.credit_score` | `4fbc434e` | scalar | 0.09086513179 | CSI of credit_score: its contribution to the shift in the linear predictor |
| `csi.incentive` | `f430cc2d` | scalar | 0.9220903461 | CSI of incentive: its contribution to the shift in the linear predictor |
| `csi.loan_age` | `df52c920` | scalar | 0 | CSI of loan_age: its contribution to the shift in the linear predictor |
| `csi.max` | `d4b08859` | scalar | 0.9220903461 | the largest characteristic stability index |
| `csi.note_rate` | `a2be3f30` | scalar | 0.4831662682 | CSI of note_rate: its contribution to the shift in the linear predictor |
| `csi.orig_ltv` | `af80429c` | scalar | 0.02302783458 | CSI of orig_ltv: its contribution to the shift in the linear predictor |
| `csi.orig_upb_log` | `ba82e949` | scalar | 0.06561601038 | CSI of orig_upb_log: its contribution to the shift in the linear predictor |
| `csi.sato` | `7d563a3f` | scalar | 0.0001467991037 | CSI of sato: its contribution to the shift in the linear predictor |
| `csi.season_cos` | `49e6d56e` | scalar | 0.003265173321 | CSI of season_cos: its contribution to the shift in the linear predictor |
| `csi.season_sin` | `ff10caf4` | scalar | 0.01315757493 | CSI of season_sin: its contribution to the shift in the linear predictor |
| `deciles.test` | `26b0ba93` | table | table, 10 rows | decile separation on test; decile 1 holds the highest probabilities |
| `leakage.duplicates.train` | `4474c227` | scalar | 0 | share of train rows whose feature values are not unique within train |
| `leakage.name_screen.n_matched` | `407e62be` | scalar | 0 | feature names matching the target-adjacent lexicon |
| `leakage.overlap` | `4c9fcd09` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.features` | `0fec8048` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.ids` | `63d37fc5` | scalar | 0 | share of test rows whose ['loan_id', 'period'] also identify a row of train |
| `leakage.target_corr.max_single_feature_auc` | `b6b29a14` | scalar | 0.7422083739 | the AUC of the strongest single feature |
| `leakage.timing.n_flagged` | `742bcd24` | scalar | 0 | features declared during_period or after_outcome |
| `metrics.out_of_time.auc` | `ee898745` | scalar | 0.7846182604 | auc on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.brier` | `f0fd020a` | scalar | 0.01725186302 | brier on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.event_rate` | `83ccf5c0` | scalar | 0.01794892714 | event_rate on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.gini` | `46899ec9` | scalar | 0.5692365207 | gini on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.ks` | `6360ccf9` | scalar | 0.4373216673 | ks on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.logloss` | `205ce509` | scalar | 0.08050056271 | logloss on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.mean_predicted` | `4d7aa98b` | scalar | 0.02282661269 | mean_predicted on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.n` | `7898809e` | scalar | 12257 | n on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.sub.burnout_high` | `014114c3` | table | table, 10 rows | every metric on the burnout above_median slice of out_of_time |
| `metrics.out_of_time.sub.burnout_high.auc_gap` | `c93b5fc8` | scalar | 0.00819466047 | how far AUC on the burnout above_median slice of out_of_time falls below AUC on all of out_of_time |
| `metrics.out_of_time.sub.burnout_high.mean_rel_gap` | `e79c0bd2` | scalar | 0.6410194511 | mean predicted against observed on the burnout above_median slice of out_of_time, relative |
| `metrics.out_of_time.sub.burnout_high.share` | `b5c30bbc` | scalar | 0.499959207 | the share of out_of_time the burnout above_median slice holds |
| `metrics.out_of_time.sub.burnout_low` | `3acfe0f8` | table | table, 10 rows | every metric on the burnout below_median slice of out_of_time |
| `metrics.out_of_time.sub.burnout_low.auc_gap` | `414188ff` | scalar | -0.02731220276 | how far AUC on the burnout below_median slice of out_of_time falls below AUC on all of out_of_time |
| `metrics.out_of_time.sub.burnout_low.mean_rel_gap` | `6355b95b` | scalar | 0.1633220095 | mean predicted against observed on the burnout below_median slice of out_of_time, relative |
| `metrics.out_of_time.sub.burnout_low.share` | `d6102b4a` | scalar | 0.500040793 | the share of out_of_time the burnout below_median slice holds |
| `metrics.out_of_time.sub.incentive_high` | `44dd161f` | table | table, 10 rows | every metric on the incentive above_median slice of out_of_time |
| `metrics.out_of_time.sub.incentive_high.auc_gap` | `81bf8d6d` | scalar | 0.04024472996 | how far AUC on the incentive above_median slice of out_of_time falls below AUC on all of out_of_time |
| `metrics.out_of_time.sub.incentive_high.mean_rel_gap` | `7c011df6` | scalar | 0.3689915805 | mean predicted against observed on the incentive above_median slice of out_of_time, relative |
| `metrics.out_of_time.sub.incentive_high.share` | `431d1ff2` | scalar | 0.499877621 | the share of out_of_time the incentive above_median slice holds |
| `metrics.test.auc` | `d57b2552` | scalar | 0.7846182604 | auc on test, recomputed by quaestor |
| `metrics.test.brier` | `68e8b1cf` | scalar | 0.01725186302 | brier on test, recomputed by quaestor |
| `metrics.test.event_rate` | `d222aedf` | scalar | 0.01794892714 | event_rate on test, recomputed by quaestor |
| `metrics.test.gini` | `1291e305` | scalar | 0.5692365207 | gini on test, recomputed by quaestor |
| `metrics.test.ks` | `857a0cf9` | scalar | 0.4373216673 | ks on test, recomputed by quaestor |
| `metrics.test.logloss` | `c576b630` | scalar | 0.08050056271 | logloss on test, recomputed by quaestor |
| `metrics.test.mean_predicted` | `1c1a1d8d` | scalar | 0.02282661269 | mean_predicted on test, recomputed by quaestor |
| `metrics.test.n` | `90b46eb1` | scalar | 12257 | n on test, recomputed by quaestor |
| `metrics.test.sub.burnout_high` | `af562636` | table | table, 10 rows | every metric on the burnout above_median slice of test |
| `metrics.test.sub.burnout_high.auc_gap` | `ad1d8f68` | scalar | 0.00819466047 | how far AUC on the burnout above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.burnout_high.mean_rel_gap` | `668dd56c` | scalar | 0.6410194511 | mean predicted against observed on the burnout above_median slice of test, relative |
| `metrics.test.sub.burnout_high.share` | `efeac6e1` | scalar | 0.499959207 | the share of test the burnout above_median slice holds |
| `metrics.test.sub.burnout_low` | `0ca2deda` | table | table, 10 rows | every metric on the burnout below_median slice of test |
| `metrics.test.sub.burnout_low.auc_gap` | `c6967420` | scalar | -0.02731220276 | how far AUC on the burnout below_median slice of test falls below AUC on all of test |
| `metrics.test.sub.burnout_low.mean_rel_gap` | `64191da8` | scalar | 0.1633220095 | mean predicted against observed on the burnout below_median slice of test, relative |
| `metrics.test.sub.burnout_low.share` | `4307ceba` | scalar | 0.500040793 | the share of test the burnout below_median slice holds |
| `metrics.test.sub.incentive_high` | `358f21f3` | table | table, 10 rows | every metric on the incentive above_median slice of test |
| `metrics.test.sub.incentive_high.auc_gap` | `fa601af0` | scalar | 0.04024472996 | how far AUC on the incentive above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.incentive_high.mean_rel_gap` | `2d6199b1` | scalar | 0.3689915805 | mean predicted against observed on the incentive above_median slice of test, relative |
| `metrics.test.sub.incentive_high.share` | `a2b45314` | scalar | 0.499877621 | the share of test the incentive above_median slice holds |
| `metrics.train.auc` | `41d3c4e6` | scalar | 0.8002919094 | auc on train, recomputed by quaestor |
| `metrics.train.brier` | `e9077291` | scalar | 0.008111422906 | brier on train, recomputed by quaestor |
| `metrics.train.event_rate` | `b0cf2348` | scalar | 0.008322892429 | event_rate on train, recomputed by quaestor |
| `metrics.train.gini` | `66b6cc81` | scalar | 0.6005838187 | gini on train, recomputed by quaestor |
| `metrics.train.ks` | `3e0b8829` | scalar | 0.4740174906 | ks on train, recomputed by quaestor |
| `metrics.train.logloss` | `e62507ab` | scalar | 0.04279363896 | logloss on train, recomputed by quaestor |
| `metrics.train.mean_predicted` | `4ea7b930` | scalar | 0.008332856538 | mean_predicted on train, recomputed by quaestor |
| `metrics.train.n` | `dd20fa4c` | scalar | 33522 | n on train, recomputed by quaestor |
| `metrics.train.sub.burnout_high` | `fb49a094` | table | table, 10 rows | every metric on the burnout above_median slice of train |
| `metrics.train.sub.burnout_high.auc_gap` | `a18d63eb` | scalar | 0.03243264786 | how far AUC on the burnout above_median slice of train falls below AUC on all of train |
| `metrics.train.sub.burnout_high.mean_rel_gap` | `d3a62f43` | scalar | 0.009235116294 | mean predicted against observed on the burnout above_median slice of train, relative |
| `metrics.train.sub.burnout_high.share` | `e7e14804` | scalar | 0.5 | the share of train the burnout above_median slice holds |
| `metrics.train.sub.burnout_low` | `1fbd40fa` | table | table, 10 rows | every metric on the burnout below_median slice of train |
| `metrics.train.sub.burnout_low.auc_gap` | `d6960b9c` | scalar | 0.05100723122 | how far AUC on the burnout below_median slice of train falls below AUC on all of train |
| `metrics.train.sub.burnout_low.mean_rel_gap` | `e08aba69` | scalar | 0.02636140092 | mean predicted against observed on the burnout below_median slice of train, relative |
| `metrics.train.sub.burnout_low.share` | `a4cc9400` | scalar | 0.5 | the share of train the burnout below_median slice holds |
| `metrics.train.sub.incentive_high` | `ab3dc71d` | table | table, 10 rows | every metric on the incentive above_median slice of train |
| `metrics.train.sub.incentive_high.auc_gap` | `1eb21997` | scalar | 0.05064713955 | how far AUC on the incentive above_median slice of train falls below AUC on all of train |
| `metrics.train.sub.incentive_high.mean_rel_gap` | `957b62eb` | scalar | 0.003817038981 | mean predicted against observed on the incentive above_median slice of train, relative |
| `metrics.train.sub.incentive_high.share` | `64a6d28c` | scalar | 0.5 | the share of train the incentive above_median slice holds |
| `metrics.vintage_holdout.auc` | `610c13fd` | scalar | 0.7716058113 | auc on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.brier` | `115af096` | scalar | 0.004766820283 | brier on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.event_rate` | `e3590a16` | scalar | 0.004817105386 | event_rate on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.gini` | `4b1525bb` | scalar | 0.5432116227 | gini on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.ks` | `c3ac5a54` | scalar | 0.4617647948 | ks on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.logloss` | `96a19aae` | scalar | 0.02818314174 | logloss on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.mean_predicted` | `914aeeba` | scalar | 0.006157456637 | mean_predicted on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.n` | `37a92951` | scalar | 32177 | n on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.sub.burnout_high` | `fa1d60e6` | table | table, 10 rows | every metric on the burnout above_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.burnout_high.auc_gap` | `f49dd552` | scalar | 0.03995268778 | how far AUC on the burnout above_median slice of vintage_holdout falls below AUC on all of vintage_holdout |
| `metrics.vintage_holdout.sub.burnout_high.mean_rel_gap` | `4ef00612` | scalar | 0.1334945197 | mean predicted against observed on the burnout above_median slice of vintage_holdout, relative |
| `metrics.vintage_holdout.sub.burnout_high.share` | `379549be` | scalar | 0.499984461 | the share of vintage_holdout the burnout above_median slice holds |
| `metrics.vintage_holdout.sub.burnout_low` | `a4cc6bb8` | table | table, 10 rows | every metric on the burnout below_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.burnout_low.auc_gap` | `d85223fe` | scalar | 0.02310435431 | how far AUC on the burnout below_median slice of vintage_holdout falls below AUC on all of vintage_holdout |
| `metrics.vintage_holdout.sub.burnout_low.mean_rel_gap` | `b9abef02` | scalar | 0.8133985092 | mean predicted against observed on the burnout below_median slice of vintage_holdout, relative |
| `metrics.vintage_holdout.sub.burnout_low.share` | `b327a747` | scalar | 0.500015539 | the share of vintage_holdout the burnout below_median slice holds |
| `metrics.vintage_holdout.sub.incentive_high` | `94f6c834` | table | table, 10 rows | every metric on the incentive above_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.incentive_high.auc_gap` | `2853b3a5` | scalar | 0.01615104629 | how far AUC on the incentive above_median slice of vintage_holdout falls below AUC on all of vintage_holdout |
| `metrics.vintage_holdout.sub.incentive_high.mean_rel_gap` | `bb893376` | scalar | 0.3916330365 | mean predicted against observed on the incentive above_median slice of vintage_holdout, relative |
| `metrics.vintage_holdout.sub.incentive_high.share` | `cb627056` | scalar | 0.499984461 | the share of vintage_holdout the incentive above_median slice holds |
| `profile.out_of_time.missing.max` | `4dafce11` | scalar | 0 | the largest missing fraction in out_of_time |
| `profile.out_of_time.n` | `fa39c5cf` | scalar | 12257 | rows in out_of_time |
| `profile.test.missing.max` | `f813848d` | scalar | 0 | the largest missing fraction in test |
| `profile.test.n` | `3b91ffcc` | scalar | 12257 | rows in test |
| `profile.train.missing.max` | `050a3099` | scalar | 0 | the largest missing fraction in train |
| `profile.train.n` | `60d3a086` | scalar | 33522 | rows in train |
| `profile.vintage_holdout.missing.max` | `329bb430` | scalar | 0 | the largest missing fraction in vintage_holdout |
| `profile.vintage_holdout.n` | `426e712a` | scalar | 32177 | rows in vintage_holdout |
| `psi.burnout` | `1d35a583` | scalar | 3.016020048 | PSI of burnout between train and test |
| `psi.credit_score` | `91c4ab83` | scalar | 0.07088355626 | PSI of credit_score between train and test |
| `psi.incentive` | `0f61188c` | scalar | 0.8734495361 | PSI of incentive between train and test |
| `psi.loan_age` | `987aabe4` | scalar | 1.679868562 | PSI of loan_age between train and test |
| `psi.max` | `4fae32c6` | scalar | 3.016020048 | the largest train-to-test PSI, score included |
| `psi.note_rate` | `2f1cb70b` | scalar | 1.341893523 | PSI of note_rate between train and test |
| `psi.orig_ltv` | `85842fd0` | scalar | 0.04331914243 | PSI of orig_ltv between train and test |
| `psi.orig_upb_log` | `f075546d` | scalar | 0.08171063787 | PSI of orig_upb_log between train and test |
| `psi.out_of_time.burnout` | `8cedaf79` | scalar | 3.016020048 | PSI of burnout between train and out_of_time |
| `psi.out_of_time.credit_score` | `a7ef717f` | scalar | 0.07088355626 | PSI of credit_score between train and out_of_time |
| `psi.out_of_time.incentive` | `ec6da34d` | scalar | 0.8734495361 | PSI of incentive between train and out_of_time |
| `psi.out_of_time.loan_age` | `ab2af3f2` | scalar | 1.679868562 | PSI of loan_age between train and out_of_time |
| `psi.out_of_time.note_rate` | `fc610fd1` | scalar | 1.341893523 | PSI of note_rate between train and out_of_time |
| `psi.out_of_time.orig_ltv` | `7eedf98f` | scalar | 0.04331914243 | PSI of orig_ltv between train and out_of_time |
| `psi.out_of_time.orig_upb_log` | `9ca9c306` | scalar | 0.08171063787 | PSI of orig_upb_log between train and out_of_time |
| `psi.out_of_time.sato` | `79f6f94a` | scalar | 0.02284102604 | PSI of sato between train and out_of_time |
| `psi.out_of_time.season_cos` | `ef947d09` | scalar | 0.004987781308 | PSI of season_cos between train and out_of_time |
| `psi.out_of_time.season_sin` | `fe2b0197` | scalar | 0.01631255179 | PSI of season_sin between train and out_of_time |
| `psi.out_of_time.y_score` | `d39a4ced` | scalar | 0.8371883582 | PSI of the score between train and out_of_time |
| `psi.sato` | `4809116c` | scalar | 0.02284102604 | PSI of sato between train and test |
| `psi.season_cos` | `62ae6c81` | scalar | 0.004987781308 | PSI of season_cos between train and test |
| `psi.season_sin` | `46fec014` | scalar | 0.01631255179 | PSI of season_sin between train and test |
| `psi.vintage_holdout.burnout` | `b2dacb71` | scalar | 0.03122017454 | PSI of burnout between train and vintage_holdout |
| `psi.vintage_holdout.credit_score` | `16906529` | scalar | 0.01928865688 | PSI of credit_score between train and vintage_holdout |
| `psi.vintage_holdout.incentive` | `1d339225` | scalar | 0.2100590512 | PSI of incentive between train and vintage_holdout |
| `psi.vintage_holdout.loan_age` | `e579422e` | scalar | 0.03488721615 | PSI of loan_age between train and vintage_holdout |
| `psi.vintage_holdout.note_rate` | `d4e6aa9a` | scalar | 0.2742521405 | PSI of note_rate between train and vintage_holdout |
| `psi.vintage_holdout.orig_ltv` | `1f0e3df0` | scalar | 0.03575446718 | PSI of orig_ltv between train and vintage_holdout |
| `psi.vintage_holdout.orig_upb_log` | `10fd298a` | scalar | 0.03037586387 | PSI of orig_upb_log between train and vintage_holdout |
| `psi.vintage_holdout.sato` | `6c4e561c` | scalar | 0.02840898929 | PSI of sato between train and vintage_holdout |
| `psi.vintage_holdout.season_cos` | `4482dc21` | scalar | 0.001640289708 | PSI of season_cos between train and vintage_holdout |
| `psi.vintage_holdout.season_sin` | `836b68bf` | scalar | 0.001971264046 | PSI of season_sin between train and vintage_holdout |
| `psi.vintage_holdout.y_score` | `5d010092` | scalar | 0.0820229283 | PSI of the score between train and vintage_holdout |
| `psi.y_score` | `92ac1652` | scalar | 0.8371883582 | PSI of the score between train and test |
| `run.features` | `61276a96` | json | json | the subject's features.json |
| `run.model_summary` | `cf58dded` | json | json | the subject's model_summary.json |
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |
| `scenario.convexity` | `70b14b4a` | scalar | -1094856.426 | the value change at -300 bp plus the change at 300 bp; negative when the fall outweighs the rise |
| `scenario.value_by_shock` | `7ca37cab` | table | table, 7 rows | servicing value, its change from the base case and first-year CPR, by shock |
| `scenario.value_change.-300` | `dfaf9b49` | scalar | -1166173.182 | change in servicing value at -300 bp |
| `scenario.value_change.0` | `1e1b0b88` | scalar | 0 | change in servicing value at 0 bp |
| `scenario.value_change.300` | `1bebd745` | scalar | 71316.75564 | change in servicing value at 300 bp |
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
| `stability.auc_by_regime` | `3b0ee961` | table | table, 2 rows | the champion's AUC within each rate_regime on train |
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
| `threshold.O1.slice_min_share` | `9a6f1a87` | scalar | 0.1 | the share of a split a sub-population must hold before it can raise an open item |
| `threshold.R1.auc_gap` | `b64213d7` | scalar | 0.1 | R1: the AUC difference across regimes |
| `threshold.R1.sign_flip_coef` | `aca84377` | scalar | 0.05 | R1: the coefficient a sign flip must exceed in both regimes |
| `threshold.R1.sign_flip_z` | `2e4428c7` | scalar | 2 | R1: the \|z\| a sign flip's coefficient must reach in both regimes |
| `threshold.S1.psi` | `278b9016` | scalar | 0.25 | S1: the population stability index, train against test |
| `threshold.package.auc.test.min` | `fececac1` | scalar | 0.65 | package.yaml declares auc min 0.65 |
| `threshold.package.calibration_slope.test.max` | `0adb7a89` | scalar | 1.2 | package.yaml declares calibration_slope max 1.2 |
| `threshold.package.calibration_slope.test.min` | `95fdb848` | scalar | 0.8 | package.yaml declares calibration_slope min 0.8 |
| `threshold.package.psi.max` | `fbb5a9d1` | scalar | 0.25 | package.yaml declares psi max 0.25 |
| `thresholds.evaluation` | `9aea64d5` | table | table, 4 rows | every threshold package.yaml declares, with its bound, the recomputed value and the outcome |
| `vif.burnout` | `127bbabe` | scalar | 3.601072256 | variance inflation factor of burnout on train |
| `vif.credit_score` | `1f19769b` | scalar | 1.011319432 | variance inflation factor of credit_score on train |
| `vif.incentive` | `60c8eef8` | scalar | 2.195314756 | variance inflation factor of incentive on train |
| `vif.loan_age` | `b30f78aa` | scalar | 2.593200289 | variance inflation factor of loan_age on train |
| `vif.max` | `fecfb289` | scalar | 4.288168629 | the largest variance inflation factor |
| `vif.note_rate` | `1113d019` | scalar | 4.288168629 | variance inflation factor of note_rate on train |
| `vif.orig_ltv` | `d9449fe2` | scalar | 1.013521613 | variance inflation factor of orig_ltv on train |
| `vif.orig_upb_log` | `59e2ab98` | scalar | 1.012256745 | variance inflation factor of orig_upb_log on train |
| `vif.sato` | `4b2ebef2` | scalar | 1.627027838 | variance inflation factor of sato on train |
| `vif.season_cos` | `f741ba51` | scalar | 1.007021417 | variance inflation factor of season_cos on train |
| `vif.season_sin` | `3b05b05a` | scalar | 1.010543525 | variance inflation factor of season_sin on train |

## Appendix C — Run trace summary

| quantity | value |
|---|---|
| tool calls | 19 (run_model 1, profile_data 2, compute_metrics 4, check_leakage 1, check_stability 1, check_collinearity 1, challenger_compare 1, run_scenarios 1, retrieve_guidance 7) |
| plan steps (bounded loop) | 4 |
| LLM calls | 20 (plan 4, draft 8, extract 8) |
| re-asks | 0 |
| repair rounds | 1 |
| tokens in / out | 290,438 / 120,345 |
| notional cost (USD) | 5.9989 |
| wall-clock (s) | 1263.01 |
| subject run (s) | 2.32 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | msr_prepayment-full_agent-20260920T200607Z-e61d346a |

## Appendix D — Not checked

| item | reason |
|---|---|
| developer claims (T1, claim channel) | The package declares 3 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
