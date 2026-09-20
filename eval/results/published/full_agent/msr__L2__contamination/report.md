---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: msr_prepayment
version: "1.0"
model_type: discrete_time_hazard
configuration: full_agent
model: claude-opus-5[1m]
run_id: msr_prepayment-full_agent-20260920T183556Z-e61d346a
data_mode: synthetic
synthetic_n: 2000
grounding_precision_pre: 0.9968
grounding_precision_post: 1.0000
n_claims: 311
n_findings_by_severity: {high: 0, medium: 1, low: 0, info: 0}
generated: "2026-09-20T18:35:56Z"
illustrative: false
---

# Validation report — `msr_prepayment` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `msr_prepayment` v1.0 | `full_agent` | claude-opus-5[1m] | synthetic, n = 2000 | 0.9968 → 1.0000 | 0 / 1 / 0 / 0 |
<!-- quaestor:renderer:end -->

The subject of this report is the model package msr_prepayment version 1.0, a loan-level model that predicts the probability of mortgage prepayment, and this report follows the structure of the Federal Reserve's model risk management guidance on model validation and monitoring [[reg:SR26-2:V]].
The subject was executed by quaestor under the wall-clock cap of 300 seconds [[art:2ad8d1a5:runtime.max_seconds]] that the package manifest declares, and every performance figure below was recomputed from the subject's own scored outputs.
The training split holds 36474 rows [[art:7e94d818:profile.train.n]], the test split holds 15382 rows [[art:e3abc1b8:profile.test.n]], the out-of-time split holds 12257 rows [[art:7898809e:metrics.out_of_time.n]], and the vintage holdout split holds 32177 rows [[art:37a92951:metrics.vintage_holdout.n]].
Recomputed outputs were compared against realised outcomes on each split in the manner outcomes analysis contemplates [[reg:SR26-2:V.1.b]].

The subject passes each of the developer-declared thresholds evaluated in this section.
Discrimination on test, at 0.7759 [[art:225b99b5:metrics.test.auc]], is above the declared floor of 0.65 [[art:fececac1:threshold.package.auc.test.min]].
The calibration slope on test, at 0.939 [[art:80d029cc:calibration_slope.test]], lies inside the declared band running from a floor of 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] to a ceiling of 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The largest train-to-test population stability index, at 0.06021 [[art:e09026cf:psi.max]], is below the declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].

Discrimination holds up away from the test split, with AUC of 0.7888 [[art:88da2e97:metrics.train.auc]] on train, 0.7871 [[art:2e910103:metrics.out_of_time.auc]] out of time and 0.7722 [[art:ff084e89:metrics.vintage_holdout.auc]] on the vintage holdout.
The calibration slope is 0.9958 [[art:a10d9430:calibration_slope.train]] on train and 1.008 [[art:860e5dd2:calibration_slope.out_of_time]] out of time, while the vintage holdout slope of 0.8363 [[art:20da9c88:calibration_slope.vintage_holdout]] is the lowest of the recomputed slopes and the closest to the declared floor.
On the above-median period slice of test, which holds a share of 0.4863 [[art:a6e7ff2a:metrics.test.sub.period_high.share]] of that split, AUC of 0.746 [[art:a6fb0274:metrics.test.sub.period_high.auc]] falls below AUC on all of test, and that shortfall expressed as a difference is 0.02993 [[art:95a3f44c:metrics.test.sub.period_high.auc_gap]].
The design is well conditioned, with a largest variance inflation factor of 4.973 [[art:d9b015aa:vif.max]] and a condition number of 4.941 [[art:cf4a0dab:condition_number]].

This validation raised F-001, a L2 contamination finding at medium severity, arising from the leakage check.
That finding is written out in full in section 6, and nothing else recorded in this section is a finding of this validation.

## 2. Conceptual soundness

Validating conceptual soundness means assessing the model's design, construction, and developmental evidence, including key modeling choices and the benchmarking of alternatives [[reg:SR26-2:V.1.a]].

### Design and feature timing

The champion is a logistic hazard model for monthly prepayment, fitted on 36474 [[art:8e6d6768:run.model_summary#n_train]] loan-months drawn from 1395 [[art:8e6d6768:run.model_summary#n_train_loans]] loans, with an intercept of -5.475 [[art:8e6d6768:run.model_summary#intercept]] and a four-term spline in loan age as its only departure from linearity in the log-odds.
It retains 12 [[art:61276a96:run.features#n]] features.
Of these, 5 [[art:61276a96:run.features#at_origination]] are known at origination and 7 [[art:61276a96:run.features#before_period_start]] are known before the start of the performance period.
No feature is measured during the period, at 0 [[art:61276a96:run.features#during_period]], and none is measured after the outcome, at 0 [[art:61276a96:run.features#after_outcome]].
That timing profile is what the intended use requires: every input is observable at the point the prediction would be made, so the design carries no look-ahead by construction.

### Features removed by the developer's own screen

The developer screened retained features on variance inflation against a declared cut of 10 [[art:8e6d6768:run.model_summary#vif_threshold]].
Two features were dropped on that basis.
The twelve-month rate change was removed at a variance inflation of 12.38 [[art:8e6d6768:run.model_summary#removed.rate_change_12m.vif]], marginally above the cut.
The log beginning-of-month balance was removed at 40180 [[art:8e6d6768:run.model_summary#removed.bom_balance_log.vif]], far above it, which is the signature of a near-exact linear dependence rather than ordinary correlation — the log balance at the start of the month is close to a deterministic function of the log original balance and loan age, both of which are retained.
Both removals are consistent with the stated screen and with the subject matter: the information each dropped feature carried is substantially reproduced by features the model keeps.

### Coefficient magnitudes and expected signs

The largest coefficient in the model is on the refinance incentive, at 1.245 [[art:8e6d6768:run.model_summary#coefficients.incentive.value]], which is what a prepayment model should show — borrowers whose note rate stands above available market rates have the most to gain from refinancing.
The first loan-age spline term is next in magnitude at 0.6986 [[art:8e6d6768:run.model_summary#coefficients.loan_age_spline_1.value]], with the later terms at 0.04151 [[art:8e6d6768:run.model_summary#coefficients.loan_age_spline_2.value]], -0.1133 [[art:8e6d6768:run.model_summary#coefficients.loan_age_spline_3.value]] and -0.2691 [[art:8e6d6768:run.model_summary#coefficients.loan_age_spline_4.value]]; the rising-then-falling shape across those terms is the seasoning ramp the subject matter expects, with prepayment speeds climbing over the first years of a loan's life and flattening thereafter.
Credit score enters at 0.4041 [[art:8e6d6768:run.model_summary#coefficients.credit_score.value]] and log original balance at 0.3134 [[art:8e6d6768:run.model_summary#coefficients.orig_upb_log.value]], both positive, matching the expectation that stronger borrowers and larger balances refinance more readily because they qualify more easily and recover closing costs faster.
Original loan-to-value enters at -0.2583 [[art:8e6d6768:run.model_summary#coefficients.orig_ltv.value]], negative as expected, since higher leverage impedes refinancing.
The seasonal pair enters at 0.04934 [[art:8e6d6768:run.model_summary#coefficients.season_sin.value]] and -0.1466 [[art:8e6d6768:run.model_summary#coefficients.season_cos.value]], and the spread at origination over the then-prevailing market rate at 0.004651 [[art:8e6d6768:run.model_summary#coefficients.sato.value]], both small relative to the incentive term.
Burnout enters at 0.08795 [[art:8e6d6768:run.model_summary#coefficients.burnout.value]]; the conventional expectation is that burnout dampens the response to incentive, so a positive sign here runs against the usual reading, though the magnitude is small beside the leading terms.
The note rate coefficient is -0.4545 [[art:8e6d6768:run.model_summary#coefficients.note_rate.value]] and is discussed below.

### Fitted signs against univariate directions

The fitted sign contradicts the feature's own univariate direction on train for 1 [[art:f96ece96:sign_check.n_disagreements]] of the features checked.
That feature is the note rate: its fitted coefficient carries sign -1 [[art:aecf7ccb:sign_check.note_rate.coef_sign]] while its own single-feature relationship with prepayment on train carries sign 1 [[art:61f6e1ac:sign_check.note_rate.univariate_direction]], and the agreement flag is accordingly 0 [[art:a453463d:sign_check.note_rate.agrees]].
Taken alone, a higher note rate predicts faster prepayment, which is the economically intuitive direction; conditional on the refinance incentive already in the model, the note rate's remaining contribution turns negative, which is the behaviour to expect when the incentive term absorbs the rate-gap information and the residual note-rate variation proxies for borrower quality and origination vintage.
The measure of how much this disagreement matters is the discrimination the feature carries: refitting the champion's form without the note rate changes test AUC by -0.002577 [[art:730edeaf:ablation.note_rate.delta_auc]], a small loss beside the -0.04119 [[art:7213d612:ablation.incentive.delta_auc]] attached to the refinance incentive and the -0.01961 [[art:5bc33417:ablation.orig_upb_log.delta_auc]] and -0.01477 [[art:479f419e:ablation.credit_score.delta_auc]] attached to log original balance and credit score.
So the flipped sign sits on a feature the model leans on only lightly, which is a materially different statement from a flip on one of the terms carrying the bulk of the discrimination.
Every other feature checked agrees: the refinance incentive at 1 [[art:f7b2338e:sign_check.incentive.agrees]], credit score at 1 [[art:915bf8eb:sign_check.credit_score.agrees]], log original balance at 1 [[art:07a9d3e6:sign_check.orig_upb_log.agrees]], original loan-to-value at 1 [[art:7021aeb0:sign_check.orig_ltv.agrees]], the origination spread at 1 [[art:2401eba2:sign_check.sato.agrees]], burnout at 1 [[art:2eec20ab:sign_check.burnout.agrees]], and the two seasonal terms at 1 [[art:e110f357:sign_check.season_sin.agrees]] and 1 [[art:7f18ddf7:sign_check.season_cos.agrees]].
In each of those cases the fitted sign and the univariate direction point the same way — positive for the incentive at 1 [[art:684cf11a:sign_check.incentive.coef_sign]] and 1 [[art:8098d951:sign_check.incentive.univariate_direction]], for credit score at 1 [[art:1ec1078b:sign_check.credit_score.coef_sign]] and 1 [[art:42303896:sign_check.credit_score.univariate_direction]], for log original balance at 1 [[art:5aa309fc:sign_check.orig_upb_log.coef_sign]] and 1 [[art:b9743ecb:sign_check.orig_upb_log.univariate_direction]], for the origination spread at 1 [[art:c031d0d5:sign_check.sato.coef_sign]] and 1 [[art:c08233a6:sign_check.sato.univariate_direction]], for burnout at 1 [[art:a3063608:sign_check.burnout.coef_sign]] and 1 [[art:bfc96bb2:sign_check.burnout.univariate_direction]], and for the sine seasonal term at 1 [[art:761188ce:sign_check.season_sin.coef_sign]] and 1 [[art:cae6b096:sign_check.season_sin.univariate_direction]]; negative for original loan-to-value at -1 [[art:7eec65ec:sign_check.orig_ltv.coef_sign]] and -1 [[art:76dbc708:sign_check.orig_ltv.univariate_direction]] and for the cosine seasonal term at -1 [[art:7dbb1ffc:sign_check.season_cos.coef_sign]] and -1 [[art:03e931f0:sign_check.season_cos.univariate_direction]].
These sign comparisons and the ablation deltas are read here as developmental evidence bearing on the design, and no rule of this validation fires on either of them.

### What each feature carries

Ablation deltas are measured from a refit of the champion's form on every retained feature, which scores 0.7674 [[art:fdbd1084:ablation.baseline_auc]] on test, below the recomputed test discrimination of the delivered champion at 0.7759 [[art:225b99b5:metrics.test.auc]].
The refinance incentive dominates, at -0.04119 [[art:7213d612:ablation.incentive.delta_auc]], followed by log original balance at -0.01961 [[art:5bc33417:ablation.orig_upb_log.delta_auc]] and credit score at -0.01477 [[art:479f419e:ablation.credit_score.delta_auc]].
The remaining terms contribute far less: original loan-to-value at -0.002215 [[art:6b1c5d74:ablation.orig_ltv.delta_auc]], the cosine seasonal term at -0.000481 [[art:655cfcbe:ablation.season_cos.delta_auc]], the sine seasonal term at -0.0003927 [[art:0b5a4b1b:ablation.season_sin.delta_auc]] and burnout at -0.0003018 [[art:177952dc:ablation.burnout.delta_auc]].
Two features leave test discrimination no worse when dropped: loan age at 0.000814 [[art:863965a3:ablation.loan_age.delta_auc]] and the origination spread at 0.0005941 [[art:c477ddcb:ablation.sato.delta_auc]], both positive, meaning the refit without them scored above the baseline on test.
A positive ablation delta on loan age does not argue for removing the seasoning ramp, which the subject matter requires and which the spline is there to represent, but it does say that on this test period the ramp is not buying discrimination on top of the other terms.

### Effective challenge

The challenger scores 0.7366 [[art:abe111e2:challenger.auc]] on test against the champion's 0.7759 [[art:225b99b5:metrics.test.auc]], and the challenger's discrimination minus the champion's is -0.03936 [[art:46dde851:challenger.delta_auc]].
The declared threshold that decides whether the comparison matters is stated as a challenger lead in test discrimination of 0.03 [[art:e042774c:threshold.E1.delta_auc]].
Because the reported difference is negative, the challenger trails rather than leads, so the threshold that would mark a materially better alternative is not reached.
On calibration the same ordering holds: the champion's test Brier score is 0.007893 [[art:66eaf26f:metrics.test.brier]] and the challenger's is 0.009228 [[art:acd8735a:challenger.brier]], and since a lower Brier score is better, the champion is the better calibrated of the two.
The benchmarking exercise therefore supports the champion's functional form as the retained specification rather than the alternative [[reg:SR26-2:V.1.a]].

### Assessment

The design is aligned with the stated purpose, its inputs are all observable before the predicted outcome, its multicollinearity screen is documented and applied against a declared cut, and its leading coefficients carry the signs and relative magnitudes the prepayment literature would expect.
The one conditional sign reversal, on the note rate, is explicable through the incentive term and sits on a feature carrying little of the model's discrimination.
The developmental evidence reviewed in this section is sufficient in quality and extent to support the champion's conceptual design for its intended use [[reg:SR26-2:V.1.a]]; nothing in this section is raised as a finding.

## 3. Data integrity and drift

Model testing includes a critical assessment of data quality, relevance, and inputs, and this section reviews the package's input data on those terms [[reg:SR26-2:IV.1]].

### Missingness

The splits carry 36474 [[art:7e94d818:profile.train.n]] rows in train, 15382 [[art:e3abc1b8:profile.test.n]] in test, 32177 [[art:426e712a:profile.vintage_holdout.n]] in the vintage holdout and 12257 [[art:fa39c5cf:profile.out_of_time.n]] out of time.
The largest missing fraction is 0 [[art:050a3099:profile.train.missing.max]] in train, 0 [[art:f813848d:profile.test.missing.max]] in test, 0 [[art:329bb430:profile.vintage_holdout.missing.max]] in the vintage holdout and 0 [[art:4dafce11:profile.out_of_time.missing.max]] out of time.
Every split therefore reports the same largest missing fraction, so no split stands apart from another on missingness and the between-split gap is not above the declared allowance of 0.1 [[art:9cce25ea:threshold.D1.missing_gap]].

### Population stability

Between train and test the inputs move little: burnout 0.004931 [[art:33f5ebc2:psi.burnout]], credit_score 0.06021 [[art:d18c84c9:psi.credit_score]], incentive 0.0008807 [[art:68e58ed4:psi.incentive]], loan_age 0.0001936 [[art:0de705ab:psi.loan_age]], note_rate 0.009204 [[art:c7f1a67b:psi.note_rate]], orig_ltv 0.03525 [[art:5a52f767:psi.orig_ltv]], orig_upb_log 0.04276 [[art:a8060a5e:psi.orig_upb_log]], sato 0.02937 [[art:d035c9fe:psi.sato]], season_cos 2.852e-05 [[art:4c164ad6:psi.season_cos]] and season_sin 3.361e-06 [[art:34445e67:psi.season_sin]].
The score itself shifts by 0.001802 [[art:b90e64c8:psi.y_score]] over the same pair of splits.
The largest train-to-test shift, the score included, is 0.06021 [[art:e09026cf:psi.max]], which sits below the declared population stability bound of 0.25 [[art:278b9016:threshold.S1.psi]] and below the package-declared maximum of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].

The holdouts drawn on other vintages and other periods behave differently, and I read them against the package-declared maximum of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]] rather than against the train-against-test bound.
Between train and the vintage holdout, burnout moves 0.04787 [[art:d7eb40ee:psi.vintage_holdout.burnout]], credit_score 0.03957 [[art:eb8b579f:psi.vintage_holdout.credit_score]], incentive 0.4468 [[art:a5809fbc:psi.vintage_holdout.incentive]], loan_age 0.07104 [[art:880920e4:psi.vintage_holdout.loan_age]], note_rate 0.6036 [[art:8903dffa:psi.vintage_holdout.note_rate]], orig_ltv 0.02878 [[art:e538a378:psi.vintage_holdout.orig_ltv]], orig_upb_log 0.03584 [[art:983493d4:psi.vintage_holdout.orig_upb_log]], sato 0.03244 [[art:9cde942f:psi.vintage_holdout.sato]], season_cos 0.001415 [[art:0b2e1ed1:psi.vintage_holdout.season_cos]] and season_sin 0.0007471 [[art:accfeb86:psi.vintage_holdout.season_sin]], with the score at 0.1381 [[art:b7edb3fa:psi.vintage_holdout.y_score]].
Of those, incentive at 0.4468 [[art:a5809fbc:psi.vintage_holdout.incentive]] and note_rate at 0.6036 [[art:8903dffa:psi.vintage_holdout.note_rate]] stand above that declared maximum of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
Between train and the out-of-time split, burnout moves 2.941 [[art:2f1775e6:psi.out_of_time.burnout]], credit_score 0.05907 [[art:736d4786:psi.out_of_time.credit_score]], incentive 0.496 [[art:8f1aad44:psi.out_of_time.incentive]], loan_age 2.483 [[art:a53fe5b7:psi.out_of_time.loan_age]], note_rate 0.698 [[art:41ec908a:psi.out_of_time.note_rate]], orig_ltv 0.04224 [[art:3e1cfd51:psi.out_of_time.orig_ltv]], orig_upb_log 0.06798 [[art:bd610e8f:psi.out_of_time.orig_upb_log]], sato 0.01229 [[art:8c2d71b1:psi.out_of_time.sato]], season_cos 0.01068 [[art:9bb91b1d:psi.out_of_time.season_cos]] and season_sin 0.02791 [[art:1c848842:psi.out_of_time.season_sin]], with the score at 0.7067 [[art:926393e5:psi.out_of_time.y_score]].
Of those, burnout, loan_age, note_rate, incentive and the score stand above the same declared maximum of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
Comparing the holdouts level for level, and not by any difference or ratio between them, the out-of-time split shows the more extreme shifts: burnout at 2.941 [[art:2f1775e6:psi.out_of_time.burnout]] and loan_age at 2.483 [[art:a53fe5b7:psi.out_of_time.loan_age]] are further above the bound than any input is between train and the vintage holdout, where the largest reported shift is note_rate at 0.6036 [[art:8903dffa:psi.vintage_holdout.note_rate]].
The score, likewise, moves further out of time at 0.7067 [[art:926393e5:psi.out_of_time.y_score]] than it does against the vintage holdout at 0.1381 [[art:b7edb3fa:psi.vintage_holdout.y_score]], and further in both than the 0.001802 [[art:b90e64c8:psi.y_score]] it moves between train and test.
These exceedances are reported here against the bound named above and are not raised as findings in this section; they are left to the findings section's open items.

### Characteristic stability

The per-input contributions to the shift in the linear predictor are: burnout 0.001163 [[art:2af1e79a:csi.burnout]], credit_score 0.008069 [[art:17137aa1:csi.credit_score]], incentive 0.005099 [[art:4fb0f08d:csi.incentive]], loan_age 0 [[art:df52c920:csi.loan_age]], note_rate 0.01445 [[art:d8ee67a8:csi.note_rate]], orig_ltv 0.03602 [[art:5ce12077:csi.orig_ltv]], orig_upb_log 0.003374 [[art:d6de1f4a:csi.orig_upb_log]], sato 0.0005107 [[art:5d9bf44b:csi.sato]], season_cos 0.0006697 [[art:f8939193:csi.season_cos]] and season_sin 5.589e-05 [[art:eef3a546:csi.season_sin]].
The largest of them is 0.03602 [[art:cf5a5274:csi.max]], carried by orig_ltv, and it sits below the declared stability bound of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]], which the package declares for population stability rather than for this decomposition.
No single input dominates the shift in the linear predictor on this evidence.

### Leakage screens

Features declared as observed during the performance period or after the outcome number 0 [[art:742bcd24:leakage.timing.n_flagged]], so the declared timings raise nothing.
The target-adjacent name lexicon matches 0 [[art:407e62be:leakage.name_screen.n_matched]] feature names.
The strongest single feature reaches an AUC of 0.7245 [[art:6db1c162:leakage.target_corr.max_single_feature_auc]], below the 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]] that one feature may reach on its own, so no input is standing in for the target.
The share of test rows whose feature values also appear in train is 0.02997 [[art:4fb7c6b6:leakage.overlap]].

The contamination screen has an identifier arm and a feature arm, and each is read against its own bound.
On the identifier arm, the share of out-of-time rows whose loan and period keys also identify a train row is 0 [[art:63d37fc5:leakage.overlap.ids]], below the declared contamination bound of 0.005 [[art:9f336eaf:threshold.L2.overlap]].
On the feature arm, the share of test rows repeating a train feature vector is 0.02997 [[art:bcbccff8:leakage.overlap.features]], read against the bound that rule actually applied, 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]], and it stands above that bound.
That applied bound is the larger of the declared contamination bound of 0.005 [[art:9f336eaf:threshold.L2.overlap]] and a scaled version of the share of train rows whose feature values are not unique within train, which is 0 [[art:4474c227:leakage.duplicates.train]]; with no repetition inside train, the applied bound rests at the declared level.
The screen raises a contamination finding of medium severity: rows of test repeat a feature vector of train while carrying identifiers of their own, at 0.02997 [[art:bcbccff8:leakage.overlap.features]] against the applied bound of 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]], and the copy may have been re-keyed.
Because the within-train duplicate share is 0 [[art:4474c227:leakage.duplicates.train]], the repetition cannot be explained as two subjects coincidentally writing the same discrete row, which strengthens the contamination reading rather than the coincidence one.
Test results drawn from the test split should therefore be read with that overlap in mind, since the discriminatory evidence it supports is to that extent not out of sample [[reg:SR26-2:V.1.b]].

## 4. Outcomes analysis

Outcomes analysis compares the model's outputs with the realized outcomes on each split, which is the comparison [[reg:SR26-2:V.1.b]] describes as the assessment of model performance relative to model objectives and business use.

This section reports calibration before discrimination.
The reason is the declared use: package.yaml states that this model's output is consumed as a probability and not only as a ranking, so whether the predicted probabilities mean what they say is the leading question whatever the event rate happens to be.

### Calibration

On test, the logistic regression of the outcome on the logit of the predicted probability gives a slope of 0.939 [[art:80d029cc:calibration_slope.test]] and an intercept of -0.2952 [[art:f2adc1ec:calibration_intercept.test]].
On train the same regression gives a slope of 0.9958 [[art:a10d9430:calibration_slope.train]] and an intercept of -0.02732 [[art:f381282b:calibration_intercept.train]].
On out-of-time it gives a slope of 1.008 [[art:860e5dd2:calibration_slope.out_of_time]] and an intercept of -0.05834 [[art:e50f09e0:calibration_intercept.out_of_time]].
On vintage holdout it gives a slope of 0.8363 [[art:20da9c88:calibration_slope.vintage_holdout]] and an intercept of -0.9462 [[art:1256d464:calibration_intercept.vintage_holdout]].
The declared band for the slope runs from 0.8 [[art:749634ae:threshold.C1.calibration_slope.min]] to 1.2 [[art:b6672579:threshold.C1.calibration_slope.max]]; the out-of-time slope sits nearest the centre of that band and the vintage-holdout slope nearest its lower edge, and the vintage-holdout intercept is the one furthest from zero.

Mean predicted on test is 0.008364 [[art:542ddc6b:metrics.test.mean_predicted]] against an observed rate of 0.008061 [[art:570cc08a:metrics.test.event_rate]], a relative gap of 0.03754 [[art:40409705:calibration.mean_rel_gap.test]] against a tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
Mean predicted on train is 0.008694 [[art:3eee0092:metrics.train.mean_predicted]] against an observed rate of 0.008609 [[art:73327d6c:metrics.train.event_rate]], a relative gap of 0.009844 [[art:0b47f454:calibration.mean_rel_gap.train]] against the same tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
Mean predicted on out-of-time is 0.01945 [[art:3cc343ae:metrics.out_of_time.mean_predicted]] against an observed rate of 0.01795 [[art:83ccf5c0:metrics.out_of_time.event_rate]], a relative gap of 0.08366 [[art:4084ccd4:calibration.mean_rel_gap.out_of_time]] against the same tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
Mean predicted on vintage holdout is 0.005914 [[art:08dbc56d:metrics.vintage_holdout.mean_predicted]] against an observed rate of 0.004817 [[art:e3590a16:metrics.vintage_holdout.event_rate]], a relative gap of 0.2277 [[art:4b6b5371:calibration.mean_rel_gap.vintage_holdout]] against the same tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
Comparing these gaps in their ratio form, the predicted level runs above the observed rate on every split reported here, the relative gap is smallest on train and largest on vintage holdout, and the vintage-holdout gap is the one closest to the tolerance.

The decile view of predicted against observed probability on test is reproduced below.

<!-- quaestor:renderer:begin table calibration.test -->
Calibration by decile of predicted probability on test [[art:9633f335:calibration.test]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.000432 | 0.0006498 | 1539 |
| 2 | 0.0009024 | 0.001949 | 1539 |
| 3 | 0.001508 | 0.002601 | 1538 |
| 4 | 0.00238 | 0.002601 | 1538 |
| 5 | 0.003578 | 0.003251 | 1538 |
| 6 | 0.005278 | 0.005202 | 1538 |
| 7 | 0.007781 | 0.009103 | 1538 |
| 8 | 0.01156 | 0.008453 | 1538 |
| 9 | 0.01744 | 0.01235 | 1538 |
| 10 | 0.03278 | 0.03446 | 1538 |
<!-- quaestor:renderer:end -->

Back-testing of the aggregate prepayment speed gives a mean absolute difference between actual and predicted CPR of 0.02615 [[art:1baf9f3a:cpr.train.mae]] on train, 0.04285 [[art:13564933:cpr.test.mae]] on test, 0.05671 [[art:6699b093:cpr.out_of_time.mae]] on out-of-time and 0.03048 [[art:34f4c62c:cpr.vintage_holdout.mae]] on vintage holdout.
The period-by-period comparison of actual against predicted CPR on test is reproduced below.

<!-- quaestor:renderer:begin table cpr.test -->
Actual against predicted CPR by period on test [[art:28397851:cpr.test]]:

| period | n | actual_cpr | predicted_cpr |
|---|---|---|---|
| 201402 | 15 | 0 | 0.03606 |
| 201403 | 28 | 0 | 0.03138 |
| 201404 | 56 | 0 | 0.02273 |
| 201405 | 68 | 0 | 0.0225 |
| 201406 | 80 | 0 | 0.02227 |
| 201407 | 97 | 0.1169 | 0.01873 |
| 201408 | 111 | 0 | 0.0162 |
| 201409 | 133 | 0.08659 | 0.01253 |
| 201410 | 145 | 0 | 0.01034 |
| 201411 | 161 | 0 | 0.00803 |
| 201412 | 175 | 0 | 0.007633 |
| 201501 | 198 | 0 | 0.007151 |
| 201502 | 198 | 0 | 0.006816 |
| 201503 | 198 | 0.05895 | 0.008539 |
| 201504 | 197 | 0 | 0.009596 |
| 201505 | 197 | 0 | 0.01364 |
| 201506 | 197 | 0 | 0.0157 |
| 201507 | 197 | 0 | 0.02068 |
| 201508 | 197 | 0 | 0.02857 |
| 201509 | 197 | 0.05924 | 0.03113 |
| 201510 | 196 | 0.05954 | 0.03822 |
| 201511 | 195 | 0 | 0.04848 |
| 201512 | 195 | 0 | 0.04981 |
| 201601 | 195 | 0.1698 | 0.07096 |
| 201602 | 192 | 0.06074 | 0.1045 |
| 201603 | 191 | 0.1187 | 0.1404 |
| 201604 | 189 | 0.1198 | 0.1581 |
| 201605 | 187 | 0.3673 | 0.2184 |
| 201606 | 180 | 0.1255 | 0.2176 |
| 201607 | 178 | 0.1268 | 0.2298 |
| 201608 | 176 | 0.06609 | 0.2104 |
| 201609 | 175 | 0.1288 | 0.1657 |
| 201610 | 173 | 0.1893 | 0.1199 |
| 201611 | 170 | 0.06835 | 0.09839 |
| 201612 | 169 | 0.06874 | 0.06992 |
| 201701 | 168 | 0.1339 | 0.05696 |
| 201702 | 176 | 0.2924 | 0.04801 |
| 201703 | 191 | 0.06105 | 0.04173 |
| 201704 | 199 | 0 | 0.03695 |
| 201705 | 218 | 0.05368 | 0.03717 |
| 201706 | 238 | 0.04927 | 0.03395 |
| 201707 | 248 | 0 | 0.02939 |
| 201708 | 274 | 0 | 0.02284 |
| 201709 | 284 | 0.08131 | 0.0233 |
| 201710 | 300 | 0 | 0.01748 |
| 201711 | 323 | 0.03653 | 0.01692 |
| 201712 | 334 | 0.03534 | 0.02102 |
| 201801 | 354 | 0.03338 | 0.02394 |
| 201802 | 353 | 0.06591 | 0.03304 |
| 201803 | 351 | 0.03366 | 0.05231 |
| 201804 | 350 | 0.06646 | 0.08342 |
| 201805 | 348 | 0.1594 | 0.1294 |
| 201806 | 343 | 0.1616 | 0.1561 |
| 201807 | 338 | 0.1638 | 0.1696 |
| 201808 | 333 | 0.06974 | 0.182 |
| 201809 | 331 | 0.2544 | 0.19 |
| 201810 | 323 | 0.1707 | 0.1805 |
| 201811 | 318 | 0.07292 | 0.1608 |
| 201812 | 316 | 0.1742 | 0.1784 |
| 201901 | 311 | 0.1098 | 0.1883 |
| 201902 | 300 | 0.1488 | 0.2245 |
| 201903 | 285 | 0.2253 | 0.2431 |
| 201904 | 258 | 0.246 | 0.2381 |
| 201905 | 243 | 0.1385 | 0.215 |
| 201906 | 233 | 0.2688 | 0.1787 |
| 201907 | 219 | 0.1984 | 0.1289 |
| 201908 | 206 | 0 | 0.09191 |
| 201909 | 191 | 0.06105 | 0.06184 |
| 201910 | 182 | 0.06398 | 0.04343 |
| 201911 | 171 | 0.06796 | 0.0377 |
| 201912 | 166 | 0 | 0.0362 |
<!-- quaestor:renderer:end -->

### Discrimination

Discrimination is reported second, one row per recomputed metric across the four splits.

| Metric | train | test | out_of_time | vintage_holdout |
| --- | --- | --- | --- | --- |
| AUC | 0.7888 [[art:88da2e97:metrics.train.auc]] | 0.7759 [[art:225b99b5:metrics.test.auc]] | 0.7871 [[art:2e910103:metrics.out_of_time.auc]] | 0.7722 [[art:ff084e89:metrics.vintage_holdout.auc]] |
| Gini | 0.5775 [[art:a786960b:metrics.train.gini]] | 0.5519 [[art:0aebb8a9:metrics.test.gini]] | 0.5742 [[art:442c1e75:metrics.out_of_time.gini]] | 0.5443 [[art:14144a5d:metrics.vintage_holdout.gini]] |
| KS | 0.4561 [[art:12bd02b0:metrics.train.ks]] | 0.4195 [[art:3abd1f94:metrics.test.ks]] | 0.4422 [[art:c8dd3c8a:metrics.out_of_time.ks]] | 0.4492 [[art:178bbe36:metrics.vintage_holdout.ks]] |
| Brier | 0.008396 [[art:a3ddd3d7:metrics.train.brier]] | 0.007893 [[art:66eaf26f:metrics.test.brier]] | 0.01712 [[art:9dbe134b:metrics.out_of_time.brier]] | 0.004765 [[art:31ac126b:metrics.vintage_holdout.brier]] |
| Log loss | 0.04442 [[art:fce5969c:metrics.train.logloss]] | 0.04261 [[art:a801271e:metrics.test.logloss]] | 0.0796 [[art:793f94ec:metrics.out_of_time.logloss]] | 0.02814 [[art:e1b4f0f1:metrics.vintage_holdout.logloss]] |
| Mean predicted | 0.008694 [[art:3eee0092:metrics.train.mean_predicted]] | 0.008364 [[art:542ddc6b:metrics.test.mean_predicted]] | 0.01945 [[art:3cc343ae:metrics.out_of_time.mean_predicted]] | 0.005914 [[art:08dbc56d:metrics.vintage_holdout.mean_predicted]] |
| Event rate | 0.008609 [[art:73327d6c:metrics.train.event_rate]] | 0.008061 [[art:570cc08a:metrics.test.event_rate]] | 0.01795 [[art:83ccf5c0:metrics.out_of_time.event_rate]] | 0.004817 [[art:e3590a16:metrics.vintage_holdout.event_rate]] |
| Rows | 36474 [[art:82d2c58e:metrics.train.n]] | 15382 [[art:e55953e1:metrics.test.n]] | 12257 [[art:7898809e:metrics.out_of_time.n]] | 32177 [[art:37a92951:metrics.vintage_holdout.n]] |

AUC on train at 0.7888 [[art:88da2e97:metrics.train.auc]] stands above AUC on test at 0.7759 [[art:225b99b5:metrics.test.auc]], and the developer bound on that train-to-test difference is 0.08 [[art:630f28f4:threshold.O1.auc_gap]], which the separation between those two recomputed values stays well inside.
Rank ordering remains close across splits: the out-of-time AUC sits above the test AUC and the vintage-holdout AUC just below it, so the ordering ability does not deteriorate on the later data in the way the probability level does.
The share of events falling in the highest-probability deciles is 0.5955 [[art:adaecbab:deciles.train.top2_capture]] on train, 0.5806 [[art:43c4adc5:deciles.test.top2_capture]] on test, 0.5864 [[art:e28ccabb:deciles.out_of_time.top2_capture]] on out-of-time and 0.5806 [[art:0d0c0310:deciles.vintage_holdout.top2_capture]] on vintage holdout.
The decile separation on test, with the highest probabilities in the leading decile, is reproduced below.

<!-- quaestor:renderer:begin table deciles.test -->
Decile separation on test; decile 1 holds the highest probabilities [[art:8e91a22f:deciles.test]]:

| decile | count | events | event_rate | lift |
|---|---|---|---|---|
| 1 | 1539 | 53 | 0.03444 | 4.272 |
| 2 | 1539 | 19 | 0.01235 | 1.531 |
| 3 | 1538 | 13 | 0.008453 | 1.049 |
| 4 | 1538 | 14 | 0.009103 | 1.129 |
| 5 | 1538 | 8 | 0.005202 | 0.6452 |
| 6 | 1538 | 5 | 0.003251 | 0.4033 |
| 7 | 1538 | 4 | 0.002601 | 0.3226 |
| 8 | 1538 | 4 | 0.002601 | 0.3226 |
| 9 | 1538 | 3 | 0.001951 | 0.242 |
| 10 | 1538 | 1 | 0.0006502 | 0.08066 |
<!-- quaestor:renderer:end -->

### Declared thresholds

The bounds package.yaml declares are set out below against the values recomputed in this run, each with its outcome.

<!-- quaestor:renderer:begin table thresholds.evaluation -->
Every threshold package.yaml declares, with its bound, the recomputed value and the outcome [[art:6eb162e0:thresholds.evaluation]]:

| metric | split | bound | value | result |
|---|---|---|---|---|
| auc | test | minimum 0.65 | 0.7759 | pass |
| calibration_slope | test | minimum 0.8 | 0.939 | pass |
| calibration_slope | test | maximum 1.2 | 0.939 | pass |
| psi |  | maximum 0.25 | 0.06021 | pass |
<!-- quaestor:renderer:end -->

The table was assembled by the tool from the same recomputed quantities reported above, so its outcome column rests on the numbers already cited in this section.
The bounds bearing most directly on outcomes analysis are the calibration slope band from 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] to 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]] and the AUC floor of 0.65 [[art:fececac1:threshold.package.auc.test.min]].

### Follow-up analyses

The planning loop asked for the full metric set to be recomputed on the slice `period > median(period)` of test.
It was asked because re-keyed copies of train rows are expected to concentrate in the earlier periods, so the later half of test is where the headline discrimination and calibration can be read with that contamination largely excluded.

<!-- quaestor:renderer:begin table metrics.test.sub.period_high -->
Every metric on the period above_median slice of test [[art:d28f323d:metrics.test.sub.period_high]]:

| metric | value |
|---|---|
| n | 7480 |
| event_rate | 0.0107 |
| auc | 0.746 |
| gini | 0.492 |
| ks | 0.3882 |
| brier | 0.01045 |
| logloss | 0.05495 |
| mean_predicted | 0.01159 |
| mean_rel_gap | 0.08392 |
| share | 0.4863 |
<!-- quaestor:renderer:end -->

AUC on the slice is 0.746 [[art:a6fb0274:metrics.test.sub.period_high.auc]], which falls 0.02993 [[art:95a3f44c:metrics.test.sub.period_high.auc_gap]] below the AUC on all of test, against a bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] on how far a sub-population's AUC may fall below its split's, so the slice does not rise to an open item on that comparison.
The slice holds 0.4863 [[art:a6e7ff2a:metrics.test.sub.period_high.share]] of test, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] a sub-population must hold before it can raise an open item and below the share of 0.95 [[art:a928a05c:threshold.O1.slice_max_share]] at which it would be refused as the whole split.
Mean predicted on the slice is 0.01159 [[art:cf372d1a:metrics.test.sub.period_high.mean_predicted]] against an observed rate of 0.0107 [[art:f82a90d7:metrics.test.sub.period_high.event_rate]], a relative gap of 0.08392 [[art:794ad5e8:metrics.test.sub.period_high.mean_rel_gap]] against the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
Comparing the two relative gaps as ratios rather than as absolute differences, the slice gap of 0.08392 [[art:794ad5e8:metrics.test.sub.period_high.mean_rel_gap]] is wider than the gap of 0.03754 [[art:40409705:calibration.mean_rel_gap.test]] on all of test, while the slice AUC stays close to the split's own, so what the later half of test registers is a shift in the level of the probabilities rather than a loss of ordering.

## 5. Sensitivity and scenario analysis

Sound practice employs sensitivity analysis and stress testing over a wide range of inputs, including extreme values, to establish the boundaries of model performance and to identify conditions under which a model may become unstable [[reg:SR11-7:V.1.a]].

The subject is a hazard model estimated with a declared regime column, so the multicollinearity diagnostics, the regime-stability checks and the rate-shock scenarios named for this section all apply to it, and each was run as reported below.
Nothing in this section is set aside in Appendix D as inapplicable to a model of this form, and no result here is reported from an analysis that does not apply.

### Multicollinearity among the retained features

The largest variance inflation factor across the retained features is 4.973 [[art:d9b015aa:vif.max]], below the declared tolerance of 10 [[art:aeb4f33c:threshold.M1.vif]].
That maximum is carried by the note rate, whose variance inflation factor is 4.973 [[art:dfd3d0c7:vif.note_rate]], with burnout next at 3.442 [[art:15d2d2b7:vif.burnout]], loan age at 2.929 [[art:da5f6107:vif.loan_age]], the refinance incentive at 2.226 [[art:13d92899:vif.incentive]] and the spread at origination at 1.708 [[art:4802c713:vif.sato]].
The remaining retained features sit closer to the no-collinearity floor: the cosine seasonal term at 1.018 [[art:0046feb1:vif.season_cos]], the credit score at 1.008 [[art:8908e744:vif.credit_score]], the log original balance at 1.006 [[art:127ff775:vif.orig_upb_log]], the original loan-to-value at 1.004 [[art:ca78c9fc:vif.orig_ltv]] and the sine seasonal term at 1.004 [[art:c19a5e9a:vif.season_sin]].
Belsley's condition number of the column-standardised design is 4.941 [[art:cf4a0dab:condition_number]], below the declared tolerance of 30 [[art:7e52fd7a:threshold.M1.condition_number]].
On the two diagnostics taken together, the retained design shows no near-dependence that approaches either declared limit.

### Stability across the declared regimes

Discrimination was measured within each declared rate regime on train, and the by-regime values are reproduced below.

<!-- quaestor:renderer:begin table stability.auc_by_regime -->
The champion's AUC within each rate_regime on train [[art:411b1cfe:stability.auc_by_regime]]:

| regime | n | event_rate | auc |
|---|---|---|---|
| falling | 18092 | 0.01443 | 0.7249 |
| rising | 18382 | 0.002883 | 0.7323 |
<!-- quaestor:renderer:end -->

The declared tolerance for the discrimination difference across regimes is 0.1 [[art:b64213d7:threshold.R1.auc_gap]], and the regime values in the table above are what that tolerance is read against.
A sign flip is declared to count only where a feature is among the leading features and its coefficient exceeds 0.05 [[art:aca84377:threshold.R1.sign_flip_coef]] in magnitude with an absolute z-statistic reaching 2 [[art:2e4428c7:threshold.R1.sign_flip_z]] in each regime.
Under that definition the indicator stands at 0 for the note rate [[art:e7ce4912:stability.note_rate.sign_flip]], at 0 for the refinance incentive [[art:0cc7a37d:stability.incentive.sign_flip]], at 0 for burnout [[art:6bc05e82:stability.burnout.sign_flip]] and at 0 for loan age [[art:b7191217:stability.loan_age.sign_flip]].
It likewise stands at 0 for the spread at origination [[art:1f302ccd:stability.sato.sign_flip]], at 0 for the credit score [[art:d956c276:stability.credit_score.sign_flip]], at 0 for the original loan-to-value [[art:054d5fab:stability.orig_ltv.sign_flip]], at 0 for the log original balance [[art:fb1ae6c8:stability.orig_upb_log.sign_flip]], at 0 for the sine seasonal term [[art:6ba36a3b:stability.season_sin.sign_flip]] and at 0 for the cosine seasonal term [[art:1850e2de:stability.season_cos.sign_flip]].
No retained feature therefore reverses the direction of its effect across the declared regimes at a strength and significance that meet the declared test in each of them.

### Rate-shock scenarios

Servicing value, its change from the base case and first-year prepayment speed were computed at each declared shock, and the grid is reproduced below.

<!-- quaestor:renderer:begin table scenario.value_by_shock -->
Servicing value, its change from the base case and first-year CPR, by shock [[art:51e09003:scenario.value_by_shock]]:

| shock_bp | value | value_change | cpr |
|---|---|---|---|
| -300 | 320300 | -1.3e+06 | 0.6116 |
| -200 | 798200 | -821800 | 0.2468 |
| -100 | 1.325e+06 | -295200 | 0.07814 |
| 0 | 1.62e+06 | 0 | 0.02294 |
| 100 | 1.724e+06 | 103800 | 0.006652 |
| 200 | 1.756e+06 | 135900 | 0.001921 |
| 300 | 1.765e+06 | 145400 | 0.0005536 |
<!-- quaestor:renderer:end -->

At the extreme downward shock the change in servicing value is -1300000 [[art:1bb5faa9:scenario.value_change.-300]], the largest displacement from the base case in either direction.
At the intermediate downward shock the change is -821800 [[art:fc515a18:scenario.value_change.-200]] and at the mildest downward shock it is -295200 [[art:8d716ed3:scenario.value_change.-100]], each closer to the base case than the shock beyond it.
The base case change is 0 [[art:1e1b0b88:scenario.value_change.0]] by construction.
On the upward side the change is 103800 [[art:32d76ec2:scenario.value_change.100]] at the mildest shock, 135900 [[art:9ff1104d:scenario.value_change.200]] at the intermediate shock and 145400 [[art:a5bb5830:scenario.value_change.300]] at the extreme shock.
The value change rises without reversal as the shock moves from the extreme downward end to the extreme upward end, so the response curve is monotone in the shock over the declared grid.
The gains on the upward side also grow by less at each successive step than the losses on the downward side, so the curve is not merely monotone but flattens as rates rise and steepens as they fall.
The convexity measure, formed as the change at the extreme downward shock plus the change at the extreme upward shock, is -1154000 [[art:e6e5c89b:scenario.convexity]].
Its negative sign means the fall at the extreme downward shock outweighs the rise at the extreme upward shock, which is the direction the package declares for a servicing asset whose prepayment option works against the holder as rates decline.
The scenario response is therefore in the declared direction as well as monotone, and the asymmetry between the downward and upward extremes is the dominant feature of the profile.

Nothing in this section is raised as a finding.

## 6. Findings and recommendations

Findings are ordered by severity and each carries the recomputed quantities and the bound the comparison was made against, in keeping with validation that identifies model limitations and errors and clarifies whether corrective actions may be warranted [[reg:SR26-2:V]].

### F-001 · L2 contamination · severity **medium**

**Rows of the test split repeat feature vectors of the training split while carrying identifiers of their own, so the held-out evaluation is not independent of the data the model was fitted on.**

The share of test rows whose feature values also appear in train is 0.02997 [[art:bcbccff8:leakage.overlap.features]].

That share was read against a bound of 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]], which the rule took as the larger of the declared contamination bound of 0.005 [[art:9f336eaf:threshold.L2.overlap]] and a term scaled from the within-train duplicate share.

The observed share lies above that bound, and the comparison reported here is the difference between the two rather than their ratio.

The share of train rows whose feature values are not unique within train is 0 [[art:4474c227:leakage.duplicates.train]], so the repetition arises across the split boundary rather than from duplication inside train, and the repeated rows may be a re-keyed copy.

The validator concludes that test-set performance for this package is measured in part on rows the model has already seen, so any accuracy, discrimination or calibration statistic computed on that split overstates out-of-sample behaviour by an amount this section does not attempt to quantify.

The model developer should trace the provenance of the repeated rows, establish whether the identifiers were reassigned during extraction, rebuild the train and test split so that no feature vector crosses it, and rerun the performance evidence on the rebuilt split before the package is relied on.

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1, S1), `compute_metrics` (T1, C1, O1), `check_leakage` (L1), `check_stability` (R1), `check_collinearity` (M1), `challenger_compare` (E1), `run_scenarios` (X1).

### Open items

What does the model discriminate on inside the segment where the fitted coefficient sign on note_rate is -1 [[art:aecf7ccb:sign_check.note_rate.coef_sign]] while the direction that feature shows on its own, the quantity the agreement was read against, is 1 [[art:61f6e1ac:sign_check.note_rate.univariate_direction]] and the agreement indicator stands at 0 [[art:a453463d:sign_check.note_rate.agrees]], and which correlated drivers is the fitted sign absorbing — model developer?

## 7. Ongoing monitoring recommendations

Ongoing monitoring should evaluate the extent to which this package continues to perform as expected given changes in products, exposures, borrower behavior, data relevance, or market conditions, with the scope and frequency of reports set by the model's nature and materiality [[reg:SR26-2:V.2]].

### Quantities to track and the bounds to track them against

The monitoring plan should re-measure the same quantities this validation checked, against the same declared thresholds, so that a production reading is directly comparable to the validation reading.

Calibration should be tracked as the logistic slope of the outcome on the logit of the score, against the declared lower bound of 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] and the declared upper bound of 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The validation reading of 0.939 [[art:80d029cc:calibration_slope.test]] sits inside that declared interval and below 1.0, nearer the lower bound than the upper one, so monitoring should treat further movement downward as the direction that reaches a declared bound first.

Discrimination should be tracked as the area under the ROC curve on realized outcomes, against the declared floor of 0.65 [[art:fececac1:threshold.package.auc.test.min]].
The validation reading of 0.7759 [[art:225b99b5:metrics.test.auc]] stands above that floor and gives the reference level against which production vintages should be read.

Input and score stability should be tracked as the population stability index across scored features and the score itself, against the declared maximum of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
The largest train-to-test value observed in this validation was 0.06021 [[art:e09026cf:psi.max]], well below that declared maximum, and production drift should be reported as the largest value across the monitored set rather than an average over it.

### Frequency

Stability of the scored population and of the score distribution should be reported at every scoring cycle, since drift can be measured without waiting for outcomes.
Calibration and discrimination should be reported as each vintage's prepayment performance window closes and outcomes become observable, and re-reported cumulatively so that a slow drift is visible against the trend and not only against a single period's noise.
A fuller review that revisits the declared thresholds themselves, the model's assumptions, and its documented limitations belongs on the periodic revalidation cycle rather than the routine reporting cycle [[reg:SR26-2:V]].
When readings fall persistently outside the declared bounds, the plan should route to investigation and then to adjustment, recalibration, or redevelopment rather than to a repeated exception [[reg:SR26-2:V.1.b]].

### How the monitoring report should order its evidence

The monitoring report should present calibration before discrimination, as section 4 of this report did, because the package declares that the output is used as a probability and not only as a ranking.
A score that still rank-orders acceptably while drifting in level is a failure of the declared use, and an ordering that leads with discrimination would show the acceptable half of that picture first.

### What monitoring adds beyond this validation

Section 2 compared a challenger against the champion, so benchmarking against an alternative model was part of this validation; what monitoring adds is the comparison the development data cannot supply, namely a benchmark against the challenger refitted on production vintages, so that the comparison reflects the population being scored now rather than the population the champion was fit on [[reg:SR11-7:V.1.b]].
Discrepancies between the champion and that refitted benchmark should trigger investigation into their sources and degree rather than an automatic conclusion that either one is in error [[reg:SR11-7:V.1.b]].

### Limitations this validation could not cover

This validation observed the model on a fixed development and test split, so it could not speak to behavior under interest-rate and refinancing regimes outside the window those data span, and monitoring should watch for such regime shifts explicitly given how strongly prepayment responds to them.
It likewise could not observe the production implementation, so monitoring should carry process verification of the scoring pipeline, the input feeds, and the change control around the deployed code [[reg:SR11-7:V.1.b]].
Overrides of model output by users are visible only in production, and monitoring should record their rate, their reasons, and whether overridden cases outperform the model, since a persistent pattern there points at the model rather than at the users [[reg:SR11-7:V.1.b]].
Thin segments and servicer or geography strata that were sparsely represented in the test data should be tracked separately as volume accumulates, because aggregate calibration and discrimination can stay inside their declared bounds while a segment deteriorates underneath them.
Where segment-level performance is compared across two sub-populations, the report should state whether it is comparing the absolute gap or the ratio and report the chosen comparison consistently, since sub-populations with matching absolute gaps can differ substantially in ratio.
Finally, back-testing against realized prepayment over the full performance window is what confirms the model still meets its design objectives, and early-warning readings on shorter horizons complement that rather than replace it [[reg:SR26-2:V.1.b]].

## Appendix A — Claims

Grounding precision 0.9968 before repair (310 of 311 claims verified; 1 dangling) and 1.0000 after 1 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 23/23; conceptual_soundness 73/73; data_integrity 82/82; outcomes 84/84; sensitivity 35/35; findings 7/7; monitoring 7/7.

Repairs:

| section | before | after | instruction to the drafter |
|---|---|---|---|
| data_integrity | 0.005099 (dangling) | 0.005099 (dangling) | ⟪art:4fb08d:csi.incentive⟫ quotes '4fb08d', which is shorter than the 8 characters a citation carries; 'csi.incentive' is 4fb0f08d -- the token is quoted as ⟪…⟫ and not in its double brackets because this is a diagnostic about a citation and not a citation: a report that printed it as it was written would be refused for carrying a token that is not a well-formed citation |
| data_integrity | 0.005099 (dangling) | 0.005099 (verified) | [[art:4fb08d0d:csi.incentive]] quotes 4fb08d0d, which is not a prefix of 4fb0f08d09c63d24 -- the hash 'csi.incentive' actually has. The number cited belongs to another artifact or another run |

Developer claims: The package declares 3 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). See Appendix D.

Excluded numeric tokens (not claims): section_number (section 6, section 4, Section 2); citation_hash (2ad8d1a5, 7e94d818, e3abc1b8, 7898809e); regulatory_section_id (SR26-2:V, SR26-2:V.1.b, SR26-2:V.1.a, SR26-2:IV.1); finding_id (F-001); package_version (1.0); extractor_returned_excluded_token (1.0, 001,, 2.0, 6,).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The subject was executed by quaestor under the wall-clock ca… | 300 | ratio | runtime.max_seconds |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 2 | summary | The training split holds 36474 rows , the test split holds 1… | 36474 | count | n | train | eq | `[[art:7e94d818:profile.train.n]]` | verified | 36474 |
| 3 | summary | The training split holds 36474 rows , the test split holds 1… | 15382 | count | n | test | eq | `[[art:e3abc1b8:profile.test.n]]` | verified | 15382 |
| 4 | summary | The training split holds 36474 rows , the test split holds 1… | 12257 | count | n | out_of_time | eq | `[[art:7898809e:metrics.out_of_time.n]]` | verified | 12257 |
| 5 | summary | The training split holds 36474 rows , the test split holds 1… | 32177 | count | n | vintage_holdout | eq | `[[art:37a92951:metrics.vintage_holdout.n]]` | verified | 32177 |
| 6 | summary | Discrimination on test, at 0.7759 , is above the declared fl… | 0.7759 | ratio | auc | test | eq | `[[art:225b99b5:metrics.test.auc]]` | verified | 0.7759451414 |
| 7 | summary | Discrimination on test, at 0.7759 , is above the declared fl… | 0.65 | ratio | auc | test | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 8 | summary | The calibration slope on test, at 0.939 , lies inside the de… | 0.939 | ratio | calibration_slope | test | eq | `[[art:80d029cc:calibration_slope.test]]` | verified | 0.9389856921 |
| 9 | summary | The calibration slope on test, at 0.939 , lies inside the de… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 10 | summary | The calibration slope on test, at 0.939 , lies inside the de… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 11 | summary | The largest train-to-test population stability index, at 0.0… | 0.06021 | ratio | psi |  | eq | `[[art:e09026cf:psi.max]]` | verified | 0.06021122495 |
| 12 | summary | The largest train-to-test population stability index, at 0.0… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 13 | summary | Discrimination holds up away from the test split, with AUC o… | 0.7888 | ratio | auc | train | eq | `[[art:88da2e97:metrics.train.auc]]` | verified | 0.7887583845 |
| 14 | summary | Discrimination holds up away from the test split, with AUC o… | 0.7871 | ratio | auc | out_of_time | eq | `[[art:2e910103:metrics.out_of_time.auc]]` | verified | 0.7871132191 |
| 15 | summary | Discrimination holds up away from the test split, with AUC o… | 0.7722 | ratio | auc | vintage_holdout | eq | `[[art:ff084e89:metrics.vintage_holdout.auc]]` | verified | 0.7721582541 |
| 16 | summary | The calibration slope is 0.9958 on train and 1.008 out of ti… | 0.9958 | ratio | calibration_slope | train | eq | `[[art:a10d9430:calibration_slope.train]]` | verified | 0.9958299755 |
| 17 | summary | The calibration slope is 0.9958 on train and 1.008 out of ti… | 1.008 | ratio | calibration_slope | out_of_time | eq | `[[art:860e5dd2:calibration_slope.out_of_time]]` | verified | 1.007762878 |
| 18 | summary | The calibration slope is 0.9958 on train and 1.008 out of ti… | 0.8363 | ratio | calibration_slope | vintage_holdout | eq | `[[art:20da9c88:calibration_slope.vintage_holdout]]` | verified | 0.8363376022 |
| 19 | summary | On the above-median period slice of test, which holds a shar… | 0.4863 | ratio | share | test | eq | `[[art:a6e7ff2a:metrics.test.sub.period_high.share]]` | verified | 0.4862826681 |
| 20 | summary | On the above-median period slice of test, which holds a shar… | 0.746 | ratio | auc | test | eq | `[[art:a6fb0274:metrics.test.sub.period_high.auc]]` | verified | 0.7460118243 |
| 21 | summary | On the above-median period slice of test, which holds a shar… | 0.02993 | ratio | auc_gap | test | eq | `[[art:95a3f44c:metrics.test.sub.period_high.auc_gap]]` | verified | 0.02993331709 |
| 22 | summary | The design is well conditioned, with a largest variance infl… | 4.973 | ratio | vif |  | eq | `[[art:d9b015aa:vif.max]]` | verified | 4.973309839 |
| 23 | summary | The design is well conditioned, with a largest variance infl… | 4.941 | ratio | condition_number |  | eq | `[[art:cf4a0dab:condition_number]]` | verified | 4.941319585 |
| 24 | conceptual_soundness | The champion is a logistic hazard model for monthly prepayme… | 36474 | count | n_train | train | eq | `[[art:8e6d6768:run.model_summary#n_train]]` | verified | 36474 |
| 25 | conceptual_soundness | The champion is a logistic hazard model for monthly prepayme… | 1395 | count | n_train_loans | train | eq | `[[art:8e6d6768:run.model_summary#n_train_loans]]` | verified | 1395 |
| 26 | conceptual_soundness | The champion is a logistic hazard model for monthly prepayme… | -5.475 | ratio | intercept |  | eq | `[[art:8e6d6768:run.model_summary#intercept]]` | verified | -5.474795404 |
| 27 | conceptual_soundness | It retains 12 features. | 12 | count | n |  | eq | `[[art:61276a96:run.features#n]]` | verified | 12 |
| 28 | conceptual_soundness | Of these, 5 are known at origination and 7 are known before… | 5 | count | at_origination |  | eq | `[[art:61276a96:run.features#at_origination]]` | verified | 5 |
| 29 | conceptual_soundness | Of these, 5 are known at origination and 7 are known before… | 7 | count | before_period_start |  | eq | `[[art:61276a96:run.features#before_period_start]]` | verified | 7 |
| 30 | conceptual_soundness | No feature is measured during the period, at 0 , and none is… | 0 | count | during_period |  | eq | `[[art:61276a96:run.features#during_period]]` | verified | 0 |
| 31 | conceptual_soundness | No feature is measured during the period, at 0 , and none is… | 0 | count | after_outcome |  | eq | `[[art:61276a96:run.features#after_outcome]]` | verified | 0 |
| 32 | conceptual_soundness | The developer screened retained features on variance inflati… | 10 | ratio | vif_threshold |  | eq | `[[art:8e6d6768:run.model_summary#vif_threshold]]` | verified | 10 |
| 33 | conceptual_soundness | The twelve-month rate change was removed at a variance infla… | 12.38 | ratio | vif |  | eq | `[[art:8e6d6768:run.model_summary#removed.rate_change_12m.vif]]` | verified | 12.380905 |
| 34 | conceptual_soundness | The log beginning-of-month balance was removed at 40180 , fa… | 40180 | ratio | vif |  | eq | `[[art:8e6d6768:run.model_summary#removed.bom_balance_log.vif]]` | verified | 40183.41422 |
| 35 | conceptual_soundness | The largest coefficient in the model is on the refinance inc… | 1.245 | ratio | coefficient |  | eq | `[[art:8e6d6768:run.model_summary#coefficients.incentive.value]]` | verified | 1.245444301 |
| 36 | conceptual_soundness | The first loan-age spline term is next in magnitude at 0.698… | 0.6986 | ratio | coefficient |  | eq | `[[art:8e6d6768:run.model_summary#coefficients.loan_age_spline_1.value]]` | verified | 0.6985602665 |
| 37 | conceptual_soundness | The first loan-age spline term is next in magnitude at 0.698… | 0.04151 | ratio | coefficient |  | eq | `[[art:8e6d6768:run.model_summary#coefficients.loan_age_spline_2.value]]` | verified | 0.0415134052 |
| 38 | conceptual_soundness | The first loan-age spline term is next in magnitude at 0.698… | -0.1133 | ratio | coefficient |  | eq | `[[art:8e6d6768:run.model_summary#coefficients.loan_age_spline_3.value]]` | verified | -0.1132984086 |
| 39 | conceptual_soundness | The first loan-age spline term is next in magnitude at 0.698… | -0.2691 | ratio | coefficient |  | eq | `[[art:8e6d6768:run.model_summary#coefficients.loan_age_spline_4.value]]` | verified | -0.2691463257 |
| 40 | conceptual_soundness | Credit score enters at 0.4041 and log original balance at 0.… | 0.4041 | ratio | coefficient |  | eq | `[[art:8e6d6768:run.model_summary#coefficients.credit_score.value]]` | verified | 0.4040561215 |
| 41 | conceptual_soundness | Credit score enters at 0.4041 and log original balance at 0.… | 0.3134 | ratio | coefficient |  | eq | `[[art:8e6d6768:run.model_summary#coefficients.orig_upb_log.value]]` | verified | 0.3133635312 |
| 42 | conceptual_soundness | Original loan-to-value enters at -0.2583 , negative as expec… | -0.2583 | ratio | coefficient |  | eq | `[[art:8e6d6768:run.model_summary#coefficients.orig_ltv.value]]` | verified | -0.25829772 |
| 43 | conceptual_soundness | The seasonal pair enters at 0.04934 and -0.1466 , and the sp… | 0.04934 | ratio | coefficient |  | eq | `[[art:8e6d6768:run.model_summary#coefficients.season_sin.value]]` | verified | 0.04933732714 |
| 44 | conceptual_soundness | The seasonal pair enters at 0.04934 and -0.1466 , and the sp… | -0.1466 | ratio | coefficient |  | eq | `[[art:8e6d6768:run.model_summary#coefficients.season_cos.value]]` | verified | -0.1466175825 |
| 45 | conceptual_soundness | The seasonal pair enters at 0.04934 and -0.1466 , and the sp… | 0.004651 | ratio | coefficient |  | eq | `[[art:8e6d6768:run.model_summary#coefficients.sato.value]]` | verified | 0.004651250403 |
| 46 | conceptual_soundness | Burnout enters at 0.08795 ; the conventional expectation is… | 0.08795 | ratio | coefficient |  | eq | `[[art:8e6d6768:run.model_summary#coefficients.burnout.value]]` | verified | 0.08795149525 |
| 47 | conceptual_soundness | The note rate coefficient is -0.4545 and is discussed below. | -0.4545 | ratio | coefficient |  | eq | `[[art:8e6d6768:run.model_summary#coefficients.note_rate.value]]` | verified | -0.4544698026 |
| 48 | conceptual_soundness | The fitted sign contradicts the feature's own univariate dir… | 1 | count | n_disagreements | train | eq | `[[art:f96ece96:sign_check.n_disagreements]]` | verified | 1 |
| 49 | conceptual_soundness | That feature is the note rate: its fitted coefficient carrie… | -1 | ratio | coef_sign |  | eq | `[[art:aecf7ccb:sign_check.note_rate.coef_sign]]` | verified | -1 |
| 50 | conceptual_soundness | That feature is the note rate: its fitted coefficient carrie… | 1 | ratio | univariate_direction | train | eq | `[[art:61f6e1ac:sign_check.note_rate.univariate_direction]]` | verified | 1 |
| 51 | conceptual_soundness | That feature is the note rate: its fitted coefficient carrie… | 0 | ratio | agrees |  | eq | `[[art:a453463d:sign_check.note_rate.agrees]]` | verified | 0 |
| 52 | conceptual_soundness | The measure of how much this disagreement matters is the dis… | -0.002577 | ratio | delta_auc | test | eq | `[[art:730edeaf:ablation.note_rate.delta_auc]]` | verified | -0.002577177916 |
| 53 | conceptual_soundness | The measure of how much this disagreement matters is the dis… | -0.04119 | ratio | delta_auc | test | eq | `[[art:7213d612:ablation.incentive.delta_auc]]` | verified | -0.04118780629 |
| 54 | conceptual_soundness | The measure of how much this disagreement matters is the dis… | -0.01961 | ratio | delta_auc | test | eq | `[[art:5bc33417:ablation.orig_upb_log.delta_auc]]` | verified | -0.01960949095 |
| 55 | conceptual_soundness | The measure of how much this disagreement matters is the dis… | -0.01477 | ratio | delta_auc | test | eq | `[[art:479f419e:ablation.credit_score.delta_auc]]` | verified | -0.01477490391 |
| 56 | conceptual_soundness | Every other feature checked agrees: the refinance incentive… | 1 | ratio | agrees |  | eq | `[[art:f7b2338e:sign_check.incentive.agrees]]` | verified | 1 |
| 57 | conceptual_soundness | Every other feature checked agrees: the refinance incentive… | 1 | ratio | agrees |  | eq | `[[art:915bf8eb:sign_check.credit_score.agrees]]` | verified | 1 |
| 58 | conceptual_soundness | Every other feature checked agrees: the refinance incentive… | 1 | ratio | agrees |  | eq | `[[art:07a9d3e6:sign_check.orig_upb_log.agrees]]` | verified | 1 |
| 59 | conceptual_soundness | Every other feature checked agrees: the refinance incentive… | 1 | ratio | agrees |  | eq | `[[art:7021aeb0:sign_check.orig_ltv.agrees]]` | verified | 1 |
| 60 | conceptual_soundness | Every other feature checked agrees: the refinance incentive… | 1 | ratio | agrees |  | eq | `[[art:2401eba2:sign_check.sato.agrees]]` | verified | 1 |
| 61 | conceptual_soundness | Every other feature checked agrees: the refinance incentive… | 1 | ratio | agrees |  | eq | `[[art:2eec20ab:sign_check.burnout.agrees]]` | verified | 1 |
| 62 | conceptual_soundness | Every other feature checked agrees: the refinance incentive… | 1 | ratio | agrees |  | eq | `[[art:e110f357:sign_check.season_sin.agrees]]` | verified | 1 |
| 63 | conceptual_soundness | Every other feature checked agrees: the refinance incentive… | 1 | ratio | agrees |  | eq | `[[art:7f18ddf7:sign_check.season_cos.agrees]]` | verified | 1 |
| 64 | conceptual_soundness | In each of those cases the fitted sign and the univariate di… | 1 | ratio | coef_sign |  | eq | `[[art:684cf11a:sign_check.incentive.coef_sign]]` | verified | 1 |
| 65 | conceptual_soundness | In each of those cases the fitted sign and the univariate di… | 1 | ratio | univariate_direction |  | eq | `[[art:8098d951:sign_check.incentive.univariate_direction]]` | verified | 1 |
| 66 | conceptual_soundness | In each of those cases the fitted sign and the univariate di… | 1 | ratio | coef_sign |  | eq | `[[art:1ec1078b:sign_check.credit_score.coef_sign]]` | verified | 1 |
| 67 | conceptual_soundness | In each of those cases the fitted sign and the univariate di… | 1 | ratio | univariate_direction |  | eq | `[[art:42303896:sign_check.credit_score.univariate_direction]]` | verified | 1 |
| 68 | conceptual_soundness | In each of those cases the fitted sign and the univariate di… | 1 | ratio | coef_sign |  | eq | `[[art:5aa309fc:sign_check.orig_upb_log.coef_sign]]` | verified | 1 |
| 69 | conceptual_soundness | In each of those cases the fitted sign and the univariate di… | 1 | ratio | univariate_direction |  | eq | `[[art:b9743ecb:sign_check.orig_upb_log.univariate_direction]]` | verified | 1 |
| 70 | conceptual_soundness | In each of those cases the fitted sign and the univariate di… | 1 | ratio | coef_sign |  | eq | `[[art:c031d0d5:sign_check.sato.coef_sign]]` | verified | 1 |
| 71 | conceptual_soundness | In each of those cases the fitted sign and the univariate di… | 1 | ratio | univariate_direction |  | eq | `[[art:c08233a6:sign_check.sato.univariate_direction]]` | verified | 1 |
| 72 | conceptual_soundness | In each of those cases the fitted sign and the univariate di… | 1 | ratio | coef_sign |  | eq | `[[art:a3063608:sign_check.burnout.coef_sign]]` | verified | 1 |
| 73 | conceptual_soundness | In each of those cases the fitted sign and the univariate di… | 1 | ratio | univariate_direction |  | eq | `[[art:bfc96bb2:sign_check.burnout.univariate_direction]]` | verified | 1 |
| 74 | conceptual_soundness | In each of those cases the fitted sign and the univariate di… | 1 | ratio | coef_sign |  | eq | `[[art:761188ce:sign_check.season_sin.coef_sign]]` | verified | 1 |
| 75 | conceptual_soundness | In each of those cases the fitted sign and the univariate di… | 1 | ratio | univariate_direction |  | eq | `[[art:cae6b096:sign_check.season_sin.univariate_direction]]` | verified | 1 |
| 76 | conceptual_soundness | In each of those cases the fitted sign and the univariate di… | -1 | ratio | coef_sign |  | eq | `[[art:7eec65ec:sign_check.orig_ltv.coef_sign]]` | verified | -1 |
| 77 | conceptual_soundness | In each of those cases the fitted sign and the univariate di… | -1 | ratio | univariate_direction |  | eq | `[[art:76dbc708:sign_check.orig_ltv.univariate_direction]]` | verified | -1 |
| 78 | conceptual_soundness | In each of those cases the fitted sign and the univariate di… | -1 | ratio | coef_sign |  | eq | `[[art:7dbb1ffc:sign_check.season_cos.coef_sign]]` | verified | -1 |
| 79 | conceptual_soundness | In each of those cases the fitted sign and the univariate di… | -1 | ratio | univariate_direction |  | eq | `[[art:03e931f0:sign_check.season_cos.univariate_direction]]` | verified | -1 |
| 80 | conceptual_soundness | Ablation deltas are measured from a refit of the champion's… | 0.7674 | ratio | auc | test | eq | `[[art:fdbd1084:ablation.baseline_auc]]` | verified | 0.7674403486 |
| 81 | conceptual_soundness | Ablation deltas are measured from a refit of the champion's… | 0.7759 | ratio | auc | test | eq | `[[art:225b99b5:metrics.test.auc]]` | verified | 0.7759451414 |
| 82 | conceptual_soundness | The refinance incentive dominates, at -0.04119 , followed by… | -0.04119 | ratio | delta_auc | test | eq | `[[art:7213d612:ablation.incentive.delta_auc]]` | verified | -0.04118780629 |
| 83 | conceptual_soundness | The refinance incentive dominates, at -0.04119 , followed by… | -0.01961 | ratio | delta_auc | test | eq | `[[art:5bc33417:ablation.orig_upb_log.delta_auc]]` | verified | -0.01960949095 |
| 84 | conceptual_soundness | The refinance incentive dominates, at -0.04119 , followed by… | -0.01477 | ratio | delta_auc | test | eq | `[[art:479f419e:ablation.credit_score.delta_auc]]` | verified | -0.01477490391 |
| 85 | conceptual_soundness | The remaining terms contribute far less: original loan-to-va… | -0.002215 | ratio | delta_auc | test | eq | `[[art:6b1c5d74:ablation.orig_ltv.delta_auc]]` | verified | -0.002214597102 |
| 86 | conceptual_soundness | The remaining terms contribute far less: original loan-to-va… | -0.000481 | ratio | delta_auc | test | eq | `[[art:655cfcbe:ablation.season_cos.delta_auc]]` | verified | -0.0004809745496 |
| 87 | conceptual_soundness | The remaining terms contribute far less: original loan-to-va… | -0.0003927 | ratio | delta_auc | test | eq | `[[art:0b5a4b1b:ablation.season_sin.delta_auc]]` | verified | -0.0003927077916 |
| 88 | conceptual_soundness | The remaining terms contribute far less: original loan-to-va… | -0.0003018 | ratio | delta_auc | test | eq | `[[art:177952dc:ablation.burnout.delta_auc]]` | verified | -0.0003017983163 |
| 89 | conceptual_soundness | Two features leave test discrimination no worse when dropped… | 0.000814 | ratio | delta_auc | test | eq | `[[art:863965a3:ablation.loan_age.delta_auc]]` | verified | 0.0008139569301 |
| 90 | conceptual_soundness | Two features leave test discrimination no worse when dropped… | 0.0005941 | ratio | delta_auc | test | eq | `[[art:c477ddcb:ablation.sato.delta_auc]]` | verified | 0.0005940828502 |
| 91 | conceptual_soundness | The challenger scores 0.7366 on test against the champion's… | 0.7366 | ratio | auc | test | eq | `[[art:abe111e2:challenger.auc]]` | verified | 0.7365834528 |
| 92 | conceptual_soundness | The challenger scores 0.7366 on test against the champion's… | 0.7759 | ratio | auc | test | eq | `[[art:225b99b5:metrics.test.auc]]` | verified | 0.7759451414 |
| 93 | conceptual_soundness | The challenger scores 0.7366 on test against the champion's… | -0.03936 | ratio | delta_auc | test | eq | `[[art:46dde851:challenger.delta_auc]]` | verified | -0.03936168863 |
| 94 | conceptual_soundness | The declared threshold that decides whether the comparison m… | 0.03 | ratio | delta_auc | test | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 95 | conceptual_soundness | On calibration the same ordering holds: the champion's test… | 0.007893 | ratio | brier | test | eq | `[[art:66eaf26f:metrics.test.brier]]` | verified | 0.007892754939 |
| 96 | conceptual_soundness | On calibration the same ordering holds: the champion's test… | 0.009228 | ratio | brier | test | eq | `[[art:acd8735a:challenger.brier]]` | verified | 0.009228035552 |
| 97 | data_integrity | The splits carry 36474 rows in train, 15382 in test, 32177 i… | 36474 | count | n | train | eq | `[[art:7e94d818:profile.train.n]]` | verified | 36474 |
| 98 | data_integrity | The splits carry 36474 rows in train, 15382 in test, 32177 i… | 15382 | count | n | test | eq | `[[art:e3abc1b8:profile.test.n]]` | verified | 15382 |
| 99 | data_integrity | The splits carry 36474 rows in train, 15382 in test, 32177 i… | 32177 | count | n | vintage_holdout | eq | `[[art:426e712a:profile.vintage_holdout.n]]` | verified | 32177 |
| 100 | data_integrity | The splits carry 36474 rows in train, 15382 in test, 32177 i… | 12257 | count | n | out_of_time | eq | `[[art:fa39c5cf:profile.out_of_time.n]]` | verified | 12257 |
| 101 | data_integrity | The largest missing fraction is 0 in train, 0 in test, 0 in… | 0 | ratio | missing | train | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 102 | data_integrity | The largest missing fraction is 0 in train, 0 in test, 0 in… | 0 | ratio | missing | test | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 103 | data_integrity | The largest missing fraction is 0 in train, 0 in test, 0 in… | 0 | ratio | missing | vintage_holdout | eq | `[[art:329bb430:profile.vintage_holdout.missing.max]]` | verified | 0 |
| 104 | data_integrity | The largest missing fraction is 0 in train, 0 in test, 0 in… | 0 | ratio | missing | out_of_time | eq | `[[art:4dafce11:profile.out_of_time.missing.max]]` | verified | 0 |
| 105 | data_integrity | Every split therefore reports the same largest missing fract… | 0.1 | ratio | missing_gap |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 106 | data_integrity | Between train and test the inputs move little: burnout 0.004… | 0.004931 | ratio | psi |  | eq | `[[art:33f5ebc2:psi.burnout]]` | verified | 0.004931216889 |
| 107 | data_integrity | Between train and test the inputs move little: burnout 0.004… | 0.06021 | ratio | psi |  | eq | `[[art:d18c84c9:psi.credit_score]]` | verified | 0.06021122495 |
| 108 | data_integrity | Between train and test the inputs move little: burnout 0.004… | 0.0008807 | ratio | psi |  | eq | `[[art:68e58ed4:psi.incentive]]` | verified | 0.0008807210511 |
| 109 | data_integrity | Between train and test the inputs move little: burnout 0.004… | 0.0001936 | ratio | psi |  | eq | `[[art:0de705ab:psi.loan_age]]` | verified | 0.0001935522768 |
| 110 | data_integrity | Between train and test the inputs move little: burnout 0.004… | 0.009204 | ratio | psi |  | eq | `[[art:c7f1a67b:psi.note_rate]]` | verified | 0.009203799735 |
| 111 | data_integrity | Between train and test the inputs move little: burnout 0.004… | 0.03525 | ratio | psi |  | eq | `[[art:5a52f767:psi.orig_ltv]]` | verified | 0.03524928958 |
| 112 | data_integrity | Between train and test the inputs move little: burnout 0.004… | 0.04276 | ratio | psi |  | eq | `[[art:a8060a5e:psi.orig_upb_log]]` | verified | 0.04275593453 |
| 113 | data_integrity | Between train and test the inputs move little: burnout 0.004… | 0.02937 | ratio | psi |  | eq | `[[art:d035c9fe:psi.sato]]` | verified | 0.02937047655 |
| 114 | data_integrity | Between train and test the inputs move little: burnout 0.004… | 2.852e-05 | ratio | psi |  | eq | `[[art:4c164ad6:psi.season_cos]]` | verified | 2.852014247e-05 |
| 115 | data_integrity | Between train and test the inputs move little: burnout 0.004… | 3.361e-06 | ratio | psi |  | eq | `[[art:34445e67:psi.season_sin]]` | verified | 3.360751567e-06 |
| 116 | data_integrity | The score itself shifts by 0.001802 over the same pair of sp… | 0.001802 | ratio | psi |  | eq | `[[art:b90e64c8:psi.y_score]]` | verified | 0.001802030258 |
| 117 | data_integrity | The largest train-to-test shift, the score included, is 0.06… | 0.06021 | ratio | psi |  | eq | `[[art:e09026cf:psi.max]]` | verified | 0.06021122495 |
| 118 | data_integrity | The largest train-to-test shift, the score included, is 0.06… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 119 | data_integrity | The largest train-to-test shift, the score included, is 0.06… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 120 | data_integrity | The holdouts drawn on other vintages and other periods behav… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 121 | data_integrity | Between train and the vintage holdout, burnout moves 0.04787… | 0.04787 | ratio | psi | vintage_holdout | eq | `[[art:d7eb40ee:psi.vintage_holdout.burnout]]` | verified | 0.04787342519 |
| 122 | data_integrity | Between train and the vintage holdout, burnout moves 0.04787… | 0.03957 | ratio | psi | vintage_holdout | eq | `[[art:eb8b579f:psi.vintage_holdout.credit_score]]` | verified | 0.03956501951 |
| 123 | data_integrity | Between train and the vintage holdout, burnout moves 0.04787… | 0.4468 | ratio | psi | vintage_holdout | eq | `[[art:a5809fbc:psi.vintage_holdout.incentive]]` | verified | 0.4467844664 |
| 124 | data_integrity | Between train and the vintage holdout, burnout moves 0.04787… | 0.07104 | ratio | psi | vintage_holdout | eq | `[[art:880920e4:psi.vintage_holdout.loan_age]]` | verified | 0.07103580061 |
| 125 | data_integrity | Between train and the vintage holdout, burnout moves 0.04787… | 0.6036 | ratio | psi | vintage_holdout | eq | `[[art:8903dffa:psi.vintage_holdout.note_rate]]` | verified | 0.6035871138 |
| 126 | data_integrity | Between train and the vintage holdout, burnout moves 0.04787… | 0.02878 | ratio | psi | vintage_holdout | eq | `[[art:e538a378:psi.vintage_holdout.orig_ltv]]` | verified | 0.0287751179 |
| 127 | data_integrity | Between train and the vintage holdout, burnout moves 0.04787… | 0.03584 | ratio | psi | vintage_holdout | eq | `[[art:983493d4:psi.vintage_holdout.orig_upb_log]]` | verified | 0.03584175044 |
| 128 | data_integrity | Between train and the vintage holdout, burnout moves 0.04787… | 0.03244 | ratio | psi | vintage_holdout | eq | `[[art:9cde942f:psi.vintage_holdout.sato]]` | verified | 0.03244197722 |
| 129 | data_integrity | Between train and the vintage holdout, burnout moves 0.04787… | 0.001415 | ratio | psi | vintage_holdout | eq | `[[art:0b2e1ed1:psi.vintage_holdout.season_cos]]` | verified | 0.001415335964 |
| 130 | data_integrity | Between train and the vintage holdout, burnout moves 0.04787… | 0.0007471 | ratio | psi | vintage_holdout | eq | `[[art:accfeb86:psi.vintage_holdout.season_sin]]` | verified | 0.0007471395641 |
| 131 | data_integrity | Between train and the vintage holdout, burnout moves 0.04787… | 0.1381 | ratio | psi | vintage_holdout | eq | `[[art:b7edb3fa:psi.vintage_holdout.y_score]]` | verified | 0.1381257303 |
| 132 | data_integrity | Of those, incentive at 0.4468 and note_rate at 0.6036 stand… | 0.4468 | ratio | psi | vintage_holdout | eq | `[[art:a5809fbc:psi.vintage_holdout.incentive]]` | verified | 0.4467844664 |
| 133 | data_integrity | Of those, incentive at 0.4468 and note_rate at 0.6036 stand… | 0.6036 | ratio | psi | vintage_holdout | eq | `[[art:8903dffa:psi.vintage_holdout.note_rate]]` | verified | 0.6035871138 |
| 134 | data_integrity | Of those, incentive at 0.4468 and note_rate at 0.6036 stand… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 135 | data_integrity | Between train and the out-of-time split, burnout moves 2.941… | 2.941 | ratio | psi | out_of_time | eq | `[[art:2f1775e6:psi.out_of_time.burnout]]` | verified | 2.940517648 |
| 136 | data_integrity | Between train and the out-of-time split, burnout moves 2.941… | 0.05907 | ratio | psi | out_of_time | eq | `[[art:736d4786:psi.out_of_time.credit_score]]` | verified | 0.05906553221 |
| 137 | data_integrity | Between train and the out-of-time split, burnout moves 2.941… | 0.496 | ratio | psi | out_of_time | eq | `[[art:8f1aad44:psi.out_of_time.incentive]]` | verified | 0.4959842347 |
| 138 | data_integrity | Between train and the out-of-time split, burnout moves 2.941… | 2.483 | ratio | psi | out_of_time | eq | `[[art:a53fe5b7:psi.out_of_time.loan_age]]` | verified | 2.482521703 |
| 139 | data_integrity | Between train and the out-of-time split, burnout moves 2.941… | 0.698 | ratio | psi | out_of_time | eq | `[[art:41ec908a:psi.out_of_time.note_rate]]` | verified | 0.6979848935 |
| 140 | data_integrity | Between train and the out-of-time split, burnout moves 2.941… | 0.04224 | ratio | psi | out_of_time | eq | `[[art:3e1cfd51:psi.out_of_time.orig_ltv]]` | verified | 0.04223900725 |
| 141 | data_integrity | Between train and the out-of-time split, burnout moves 2.941… | 0.06798 | ratio | psi | out_of_time | eq | `[[art:bd610e8f:psi.out_of_time.orig_upb_log]]` | verified | 0.0679791761 |
| 142 | data_integrity | Between train and the out-of-time split, burnout moves 2.941… | 0.01229 | ratio | psi | out_of_time | eq | `[[art:8c2d71b1:psi.out_of_time.sato]]` | verified | 0.01229057251 |
| 143 | data_integrity | Between train and the out-of-time split, burnout moves 2.941… | 0.01068 | ratio | psi | out_of_time | eq | `[[art:9bb91b1d:psi.out_of_time.season_cos]]` | verified | 0.01068186712 |
| 144 | data_integrity | Between train and the out-of-time split, burnout moves 2.941… | 0.02791 | ratio | psi | out_of_time | eq | `[[art:1c848842:psi.out_of_time.season_sin]]` | verified | 0.02790812853 |
| 145 | data_integrity | Between train and the out-of-time split, burnout moves 2.941… | 0.7067 | ratio | psi | out_of_time | eq | `[[art:926393e5:psi.out_of_time.y_score]]` | verified | 0.706727876 |
| 146 | data_integrity | Of those, burnout, loan_age, note_rate, incentive and the sc… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 147 | data_integrity | Comparing the holdouts level for level, and not by any diffe… | 2.941 | ratio | psi | out_of_time | eq | `[[art:2f1775e6:psi.out_of_time.burnout]]` | verified | 2.940517648 |
| 148 | data_integrity | Comparing the holdouts level for level, and not by any diffe… | 2.483 | ratio | psi | out_of_time | eq | `[[art:a53fe5b7:psi.out_of_time.loan_age]]` | verified | 2.482521703 |
| 149 | data_integrity | Comparing the holdouts level for level, and not by any diffe… | 0.6036 | ratio | psi | vintage_holdout | eq | `[[art:8903dffa:psi.vintage_holdout.note_rate]]` | verified | 0.6035871138 |
| 150 | data_integrity | The score, likewise, moves further out of time at 0.7067 tha… | 0.7067 | ratio | psi | out_of_time | eq | `[[art:926393e5:psi.out_of_time.y_score]]` | verified | 0.706727876 |
| 151 | data_integrity | The score, likewise, moves further out of time at 0.7067 tha… | 0.1381 | ratio | psi | vintage_holdout | eq | `[[art:b7edb3fa:psi.vintage_holdout.y_score]]` | verified | 0.1381257303 |
| 152 | data_integrity | The score, likewise, moves further out of time at 0.7067 tha… | 0.001802 | ratio | psi |  | eq | `[[art:b90e64c8:psi.y_score]]` | verified | 0.001802030258 |
| 153 | data_integrity | The per-input contributions to the shift in the linear predi… | 0.001163 | ratio | csi |  | eq | `[[art:2af1e79a:csi.burnout]]` | verified | 0.001162803488 |
| 154 | data_integrity | The per-input contributions to the shift in the linear predi… | 0.008069 | ratio | csi |  | eq | `[[art:17137aa1:csi.credit_score]]` | verified | 0.008068926476 |
| 155 | data_integrity | The per-input contributions to the shift in the linear predi… | 0.005099 | ratio | csi |  | eq | `[[art:4fb0f08d:csi.incentive]]` | verified | 0.005098722582 |
| 156 | data_integrity | The per-input contributions to the shift in the linear predi… | 0 | ratio | csi |  | eq | `[[art:df52c920:csi.loan_age]]` | verified | 0 |
| 157 | data_integrity | The per-input contributions to the shift in the linear predi… | 0.01445 | ratio | csi |  | eq | `[[art:d8ee67a8:csi.note_rate]]` | verified | 0.01444840152 |
| 158 | data_integrity | The per-input contributions to the shift in the linear predi… | 0.03602 | ratio | csi |  | eq | `[[art:5ce12077:csi.orig_ltv]]` | verified | 0.0360163058 |
| 159 | data_integrity | The per-input contributions to the shift in the linear predi… | 0.003374 | ratio | csi |  | eq | `[[art:d6de1f4a:csi.orig_upb_log]]` | verified | 0.003374084917 |
| 160 | data_integrity | The per-input contributions to the shift in the linear predi… | 0.0005107 | ratio | csi |  | eq | `[[art:5d9bf44b:csi.sato]]` | verified | 0.0005107233981 |
| 161 | data_integrity | The per-input contributions to the shift in the linear predi… | 0.0006697 | ratio | csi |  | eq | `[[art:f8939193:csi.season_cos]]` | verified | 0.0006696922627 |
| 162 | data_integrity | The per-input contributions to the shift in the linear predi… | 5.589e-05 | ratio | csi |  | eq | `[[art:eef3a546:csi.season_sin]]` | verified | 5.589052952e-05 |
| 163 | data_integrity | The largest of them is 0.03602 , carried by orig_ltv, and it… | 0.03602 | ratio | csi |  | eq | `[[art:cf5a5274:csi.max]]` | verified | 0.0360163058 |
| 164 | data_integrity | The largest of them is 0.03602 , carried by orig_ltv, and it… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 165 | data_integrity | Features declared as observed during the performance period… | 0 | count | n_flagged |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 166 | data_integrity | The target-adjacent name lexicon matches 0 feature names. | 0 | count | n_matched |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 167 | data_integrity | The strongest single feature reaches an AUC of 0.7245 , belo… | 0.7245 | ratio | single_feature_auc |  | eq | `[[art:6db1c162:leakage.target_corr.max_single_feature_auc]]` | verified | 0.7244788731 |
| 168 | data_integrity | The strongest single feature reaches an AUC of 0.7245 , belo… | 0.9 | ratio | single_feature_auc |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 169 | data_integrity | The share of test rows whose feature values also appear in t… | 0.02997 | ratio | overlap |  | eq | `[[art:4fb7c6b6:leakage.overlap]]` | verified | 0.02997009492 |
| 170 | data_integrity | On the identifier arm, the share of out-of-time rows whose l… | 0 | ratio | overlap_ids |  | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 171 | data_integrity | On the identifier arm, the share of out-of-time rows whose l… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 172 | data_integrity | On the feature arm, the share of test rows repeating a train… | 0.02997 | ratio | overlap_features |  | eq | `[[art:bcbccff8:leakage.overlap.features]]` | verified | 0.02997009492 |
| 173 | data_integrity | On the feature arm, the share of test rows repeating a train… | 0.005 | ratio | overlap_features |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 174 | data_integrity | That applied bound is the larger of the declared contaminati… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 175 | data_integrity | That applied bound is the larger of the declared contaminati… | 0 | ratio | duplicates | train | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 176 | data_integrity | The screen raises a contamination finding of medium severity… | 0.02997 | ratio | overlap_features |  | eq | `[[art:bcbccff8:leakage.overlap.features]]` | verified | 0.02997009492 |
| 177 | data_integrity | The screen raises a contamination finding of medium severity… | 0.005 | ratio | overlap_features |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 178 | data_integrity | Because the within-train duplicate share is 0 , the repetiti… | 0 | ratio | duplicates | train | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 179 | outcomes | On test, the logistic regression of the outcome on the logit… | 0.939 | ratio | calibration_slope | test | eq | `[[art:80d029cc:calibration_slope.test]]` | verified | 0.9389856921 |
| 180 | outcomes | On test, the logistic regression of the outcome on the logit… | -0.2952 | ratio | calibration_intercept | test | eq | `[[art:f2adc1ec:calibration_intercept.test]]` | verified | -0.2952175968 |
| 181 | outcomes | On train the same regression gives a slope of 0.9958 and an… | 0.9958 | ratio | calibration_slope | train | eq | `[[art:a10d9430:calibration_slope.train]]` | verified | 0.9958299755 |
| 182 | outcomes | On train the same regression gives a slope of 0.9958 and an… | -0.02732 | ratio | calibration_intercept | train | eq | `[[art:f381282b:calibration_intercept.train]]` | verified | -0.02732327203 |
| 183 | outcomes | On out-of-time it gives a slope of 1.008 and an intercept of… | 1.008 | ratio | calibration_slope | out_of_time | eq | `[[art:860e5dd2:calibration_slope.out_of_time]]` | verified | 1.007762878 |
| 184 | outcomes | On out-of-time it gives a slope of 1.008 and an intercept of… | -0.05834 | ratio | calibration_intercept | out_of_time | eq | `[[art:e50f09e0:calibration_intercept.out_of_time]]` | verified | -0.0583358688 |
| 185 | outcomes | On vintage holdout it gives a slope of 0.8363 and an interce… | 0.8363 | ratio | calibration_slope | vintage_holdout | eq | `[[art:20da9c88:calibration_slope.vintage_holdout]]` | verified | 0.8363376022 |
| 186 | outcomes | On vintage holdout it gives a slope of 0.8363 and an interce… | -0.9462 | ratio | calibration_intercept | vintage_holdout | eq | `[[art:1256d464:calibration_intercept.vintage_holdout]]` | verified | -0.9462036021 |
| 187 | outcomes | The declared band for the slope runs from 0.8 to 1.2 ; the o… | 0.8 | ratio | calibration_slope |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 188 | outcomes | The declared band for the slope runs from 0.8 to 1.2 ; the o… | 1.2 | ratio | calibration_slope |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 189 | outcomes | Mean predicted on test is 0.008364 against an observed rate… | 0.008364 | ratio | mean_predicted | test | eq | `[[art:542ddc6b:metrics.test.mean_predicted]]` | verified | 0.008363991555 |
| 190 | outcomes | Mean predicted on test is 0.008364 against an observed rate… | 0.008061 | ratio | event_rate | test | eq | `[[art:570cc08a:metrics.test.event_rate]]` | verified | 0.008061370433 |
| 191 | outcomes | Mean predicted on test is 0.008364 against an observed rate… | 0.03754 | ratio | mean_rel_gap | test | eq | `[[art:40409705:calibration.mean_rel_gap.test]]` | verified | 0.03753966213 |
| 192 | outcomes | Mean predicted on test is 0.008364 against an observed rate… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 193 | outcomes | Mean predicted on train is 0.008694 against an observed rate… | 0.008694 | ratio | mean_predicted | train | eq | `[[art:3eee0092:metrics.train.mean_predicted]]` | verified | 0.008693620795 |
| 194 | outcomes | Mean predicted on train is 0.008694 against an observed rate… | 0.008609 | ratio | event_rate | train | eq | `[[art:73327d6c:metrics.train.event_rate]]` | verified | 0.008608872073 |
| 195 | outcomes | Mean predicted on train is 0.008694 against an observed rate… | 0.009844 | ratio | mean_rel_gap | train | eq | `[[art:0b47f454:calibration.mean_rel_gap.train]]` | verified | 0.009844346741 |
| 196 | outcomes | Mean predicted on train is 0.008694 against an observed rate… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 197 | outcomes | Mean predicted on out-of-time is 0.01945 against an observed… | 0.01945 | ratio | mean_predicted | out_of_time | eq | `[[art:3cc343ae:metrics.out_of_time.mean_predicted]]` | verified | 0.01945061747 |
| 198 | outcomes | Mean predicted on out-of-time is 0.01945 against an observed… | 0.01795 | ratio | event_rate | out_of_time | eq | `[[art:83ccf5c0:metrics.out_of_time.event_rate]]` | verified | 0.01794892714 |
| 199 | outcomes | Mean predicted on out-of-time is 0.01945 against an observed… | 0.08366 | ratio | mean_rel_gap | out_of_time | eq | `[[art:4084ccd4:calibration.mean_rel_gap.out_of_time]]` | verified | 0.08366462899 |
| 200 | outcomes | Mean predicted on out-of-time is 0.01945 against an observed… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 201 | outcomes | Mean predicted on vintage holdout is 0.005914 against an obs… | 0.005914 | ratio | mean_predicted | vintage_holdout | eq | `[[art:08dbc56d:metrics.vintage_holdout.mean_predicted]]` | verified | 0.005913917042 |
| 202 | outcomes | Mean predicted on vintage holdout is 0.005914 against an obs… | 0.004817 | ratio | event_rate | vintage_holdout | eq | `[[art:e3590a16:metrics.vintage_holdout.event_rate]]` | verified | 0.004817105386 |
| 203 | outcomes | Mean predicted on vintage holdout is 0.005914 against an obs… | 0.2277 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:4b6b5371:calibration.mean_rel_gap.vintage_holdout]]` | verified | 0.2276910236 |
| 204 | outcomes | Mean predicted on vintage holdout is 0.005914 against an obs… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 205 | outcomes | Back-testing of the aggregate prepayment speed gives a mean… | 0.02615 | ratio | cpr_mae | train | eq | `[[art:1baf9f3a:cpr.train.mae]]` | verified | 0.02615146691 |
| 206 | outcomes | Back-testing of the aggregate prepayment speed gives a mean… | 0.04285 | ratio | cpr_mae | test | eq | `[[art:13564933:cpr.test.mae]]` | verified | 0.04285359689 |
| 207 | outcomes | Back-testing of the aggregate prepayment speed gives a mean… | 0.05671 | ratio | cpr_mae | out_of_time | eq | `[[art:6699b093:cpr.out_of_time.mae]]` | verified | 0.05670843092 |
| 208 | outcomes | Back-testing of the aggregate prepayment speed gives a mean… | 0.03048 | ratio | cpr_mae | vintage_holdout | eq | `[[art:34f4c62c:cpr.vintage_holdout.mae]]` | verified | 0.03048231099 |
| 209 | outcomes | \| AUC \| 0.7888 \| 0.7759 \| 0.7871 \| 0.7722 \| | 0.7888 | ratio | auc | train | eq | `[[art:88da2e97:metrics.train.auc]]` | verified | 0.7887583845 |
| 210 | outcomes | \| AUC \| 0.7888 \| 0.7759 \| 0.7871 \| 0.7722 \| | 0.7759 | ratio | auc | test | eq | `[[art:225b99b5:metrics.test.auc]]` | verified | 0.7759451414 |
| 211 | outcomes | \| AUC \| 0.7888 \| 0.7759 \| 0.7871 \| 0.7722 \| | 0.7871 | ratio | auc | out_of_time | eq | `[[art:2e910103:metrics.out_of_time.auc]]` | verified | 0.7871132191 |
| 212 | outcomes | \| AUC \| 0.7888 \| 0.7759 \| 0.7871 \| 0.7722 \| | 0.7722 | ratio | auc | vintage_holdout | eq | `[[art:ff084e89:metrics.vintage_holdout.auc]]` | verified | 0.7721582541 |
| 213 | outcomes | \| Gini \| 0.5775 \| 0.5519 \| 0.5742 \| 0.5443 \| | 0.5775 | ratio | gini | train | eq | `[[art:a786960b:metrics.train.gini]]` | verified | 0.5775167691 |
| 214 | outcomes | \| Gini \| 0.5775 \| 0.5519 \| 0.5742 \| 0.5443 \| | 0.5519 | ratio | gini | test | eq | `[[art:0aebb8a9:metrics.test.gini]]` | verified | 0.5518902828 |
| 215 | outcomes | \| Gini \| 0.5775 \| 0.5519 \| 0.5742 \| 0.5443 \| | 0.5742 | ratio | gini | out_of_time | eq | `[[art:442c1e75:metrics.out_of_time.gini]]` | verified | 0.5742264382 |
| 216 | outcomes | \| Gini \| 0.5775 \| 0.5519 \| 0.5742 \| 0.5443 \| | 0.5443 | ratio | gini | vintage_holdout | eq | `[[art:14144a5d:metrics.vintage_holdout.gini]]` | verified | 0.5443165082 |
| 217 | outcomes | \| KS \| 0.4561 \| 0.4195 \| 0.4422 \| 0.4492 \| | 0.4561 | ratio | ks | train | eq | `[[art:12bd02b0:metrics.train.ks]]` | verified | 0.4560599388 |
| 218 | outcomes | \| KS \| 0.4561 \| 0.4195 \| 0.4422 \| 0.4492 \| | 0.4195 | ratio | ks | test | eq | `[[art:3abd1f94:metrics.test.ks]]` | verified | 0.4194605474 |
| 219 | outcomes | \| KS \| 0.4561 \| 0.4195 \| 0.4422 \| 0.4492 \| | 0.4422 | ratio | ks | out_of_time | eq | `[[art:c8dd3c8a:metrics.out_of_time.ks]]` | verified | 0.4421873466 |
| 220 | outcomes | \| KS \| 0.4561 \| 0.4195 \| 0.4422 \| 0.4492 \| | 0.4492 | ratio | ks | vintage_holdout | eq | `[[art:178bbe36:metrics.vintage_holdout.ks]]` | verified | 0.4492226111 |
| 221 | outcomes | \| Brier \| 0.008396 \| 0.007893 \| 0.01712 \| 0.004765 \| | 0.008396 | ratio | brier | train | eq | `[[art:a3ddd3d7:metrics.train.brier]]` | verified | 0.008396301302 |
| 222 | outcomes | \| Brier \| 0.008396 \| 0.007893 \| 0.01712 \| 0.004765 \| | 0.007893 | ratio | brier | test | eq | `[[art:66eaf26f:metrics.test.brier]]` | verified | 0.007892754939 |
| 223 | outcomes | \| Brier \| 0.008396 \| 0.007893 \| 0.01712 \| 0.004765 \| | 0.01712 | ratio | brier | out_of_time | eq | `[[art:9dbe134b:metrics.out_of_time.brier]]` | verified | 0.01712189167 |
| 224 | outcomes | \| Brier \| 0.008396 \| 0.007893 \| 0.01712 \| 0.004765 \| | 0.004765 | ratio | brier | vintage_holdout | eq | `[[art:31ac126b:metrics.vintage_holdout.brier]]` | verified | 0.00476513883 |
| 225 | outcomes | \| Log loss \| 0.04442 \| 0.04261 \| 0.0796 \| 0.02814 \| | 0.04442 | ratio | logloss | train | eq | `[[art:fce5969c:metrics.train.logloss]]` | verified | 0.04441572278 |
| 226 | outcomes | \| Log loss \| 0.04442 \| 0.04261 \| 0.0796 \| 0.02814 \| | 0.04261 | ratio | logloss | test | eq | `[[art:a801271e:metrics.test.logloss]]` | verified | 0.04261094263 |
| 227 | outcomes | \| Log loss \| 0.04442 \| 0.04261 \| 0.0796 \| 0.02814 \| | 0.0796 | ratio | logloss | out_of_time | eq | `[[art:793f94ec:metrics.out_of_time.logloss]]` | verified | 0.07960455821 |
| 228 | outcomes | \| Log loss \| 0.04442 \| 0.04261 \| 0.0796 \| 0.02814 \| | 0.02814 | ratio | logloss | vintage_holdout | eq | `[[art:e1b4f0f1:metrics.vintage_holdout.logloss]]` | verified | 0.02814470369 |
| 229 | outcomes | \| Mean predicted \| 0.008694 \| 0.008364 \| 0.01945 \| 0.005914… | 0.008694 | ratio | mean_predicted | train | eq | `[[art:3eee0092:metrics.train.mean_predicted]]` | verified | 0.008693620795 |
| 230 | outcomes | \| Mean predicted \| 0.008694 \| 0.008364 \| 0.01945 \| 0.005914… | 0.008364 | ratio | mean_predicted | test | eq | `[[art:542ddc6b:metrics.test.mean_predicted]]` | verified | 0.008363991555 |
| 231 | outcomes | \| Mean predicted \| 0.008694 \| 0.008364 \| 0.01945 \| 0.005914… | 0.01945 | ratio | mean_predicted | out_of_time | eq | `[[art:3cc343ae:metrics.out_of_time.mean_predicted]]` | verified | 0.01945061747 |
| 232 | outcomes | \| Mean predicted \| 0.008694 \| 0.008364 \| 0.01945 \| 0.005914… | 0.005914 | ratio | mean_predicted | vintage_holdout | eq | `[[art:08dbc56d:metrics.vintage_holdout.mean_predicted]]` | verified | 0.005913917042 |
| 233 | outcomes | \| Event rate \| 0.008609 \| 0.008061 \| 0.01795 \| 0.004817 \| | 0.008609 | ratio | event_rate | train | eq | `[[art:73327d6c:metrics.train.event_rate]]` | verified | 0.008608872073 |
| 234 | outcomes | \| Event rate \| 0.008609 \| 0.008061 \| 0.01795 \| 0.004817 \| | 0.008061 | ratio | event_rate | test | eq | `[[art:570cc08a:metrics.test.event_rate]]` | verified | 0.008061370433 |
| 235 | outcomes | \| Event rate \| 0.008609 \| 0.008061 \| 0.01795 \| 0.004817 \| | 0.01795 | ratio | event_rate | out_of_time | eq | `[[art:83ccf5c0:metrics.out_of_time.event_rate]]` | verified | 0.01794892714 |
| 236 | outcomes | \| Event rate \| 0.008609 \| 0.008061 \| 0.01795 \| 0.004817 \| | 0.004817 | ratio | event_rate | vintage_holdout | eq | `[[art:e3590a16:metrics.vintage_holdout.event_rate]]` | verified | 0.004817105386 |
| 237 | outcomes | \| Rows \| 36474 \| 15382 \| 12257 \| 32177 \| | 36474 | count | n | train | eq | `[[art:82d2c58e:metrics.train.n]]` | verified | 36474 |
| 238 | outcomes | \| Rows \| 36474 \| 15382 \| 12257 \| 32177 \| | 15382 | count | n | test | eq | `[[art:e55953e1:metrics.test.n]]` | verified | 15382 |
| 239 | outcomes | \| Rows \| 36474 \| 15382 \| 12257 \| 32177 \| | 12257 | count | n | out_of_time | eq | `[[art:7898809e:metrics.out_of_time.n]]` | verified | 12257 |
| 240 | outcomes | \| Rows \| 36474 \| 15382 \| 12257 \| 32177 \| | 32177 | count | n | vintage_holdout | eq | `[[art:37a92951:metrics.vintage_holdout.n]]` | verified | 32177 |
| 241 | outcomes | AUC on train at 0.7888 stands above AUC on test at 0.7759 ,… | 0.7888 | ratio | auc | train | eq | `[[art:88da2e97:metrics.train.auc]]` | verified | 0.7887583845 |
| 242 | outcomes | AUC on train at 0.7888 stands above AUC on test at 0.7759 ,… | 0.7759 | ratio | auc | test | eq | `[[art:225b99b5:metrics.test.auc]]` | verified | 0.7759451414 |
| 243 | outcomes | AUC on train at 0.7888 stands above AUC on test at 0.7759 ,… | 0.08 | ratio | auc_gap |  | eq | `[[art:630f28f4:threshold.O1.auc_gap]]` | verified | 0.08 |
| 244 | outcomes | The share of events falling in the highest-probability decil… | 0.5955 | ratio | top2_capture | train | eq | `[[art:adaecbab:deciles.train.top2_capture]]` | verified | 0.5955414013 |
| 245 | outcomes | The share of events falling in the highest-probability decil… | 0.5806 | ratio | top2_capture | test | eq | `[[art:43c4adc5:deciles.test.top2_capture]]` | verified | 0.5806451613 |
| 246 | outcomes | The share of events falling in the highest-probability decil… | 0.5864 | ratio | top2_capture | out_of_time | eq | `[[art:e28ccabb:deciles.out_of_time.top2_capture]]` | verified | 0.5863636364 |
| 247 | outcomes | The share of events falling in the highest-probability decil… | 0.5806 | ratio | top2_capture | vintage_holdout | eq | `[[art:0d0c0310:deciles.vintage_holdout.top2_capture]]` | verified | 0.5806451613 |
| 248 | outcomes | The bounds bearing most directly on outcomes analysis are th… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 249 | outcomes | The bounds bearing most directly on outcomes analysis are th… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 250 | outcomes | The bounds bearing most directly on outcomes analysis are th… | 0.65 | ratio | auc | test | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 251 | outcomes | AUC on the slice is 0.746 , which falls 0.02993 below the AU… | 0.746 | ratio | auc | test | eq | `[[art:a6fb0274:metrics.test.sub.period_high.auc]]` | verified | 0.7460118243 |
| 252 | outcomes | AUC on the slice is 0.746 , which falls 0.02993 below the AU… | 0.02993 | ratio | auc_gap | test | eq | `[[art:95a3f44c:metrics.test.sub.period_high.auc_gap]]` | verified | 0.02993331709 |
| 253 | outcomes | AUC on the slice is 0.746 , which falls 0.02993 below the AU… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 254 | outcomes | The slice holds 0.4863 of test, above the floor of 0.1 a sub… | 0.4863 | ratio | share | test | eq | `[[art:a6e7ff2a:metrics.test.sub.period_high.share]]` | verified | 0.4862826681 |
| 255 | outcomes | The slice holds 0.4863 of test, above the floor of 0.1 a sub… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 256 | outcomes | The slice holds 0.4863 of test, above the floor of 0.1 a sub… | 0.95 | ratio | slice_max_share |  | eq | `[[art:a928a05c:threshold.O1.slice_max_share]]` | verified | 0.95 |
| 257 | outcomes | Mean predicted on the slice is 0.01159 against an observed r… | 0.01159 | ratio | mean_predicted | test | eq | `[[art:cf372d1a:metrics.test.sub.period_high.mean_predicted]]` | verified | 0.01159277483 |
| 258 | outcomes | Mean predicted on the slice is 0.01159 against an observed r… | 0.0107 | ratio | event_rate | test | eq | `[[art:f82a90d7:metrics.test.sub.period_high.event_rate]]` | verified | 0.01069518717 |
| 259 | outcomes | Mean predicted on the slice is 0.01159 against an observed r… | 0.08392 | ratio | mean_rel_gap | test | eq | `[[art:794ad5e8:metrics.test.sub.period_high.mean_rel_gap]]` | verified | 0.08392444656 |
| 260 | outcomes | Mean predicted on the slice is 0.01159 against an observed r… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 261 | outcomes | Comparing the two relative gaps as ratios rather than as abs… | 0.08392 | ratio | mean_rel_gap | test | eq | `[[art:794ad5e8:metrics.test.sub.period_high.mean_rel_gap]]` | verified | 0.08392444656 |
| 262 | outcomes | Comparing the two relative gaps as ratios rather than as abs… | 0.03754 | ratio | mean_rel_gap | test | eq | `[[art:40409705:calibration.mean_rel_gap.test]]` | verified | 0.03753966213 |
| 263 | sensitivity | The largest variance inflation factor across the retained fe… | 4.973 | ratio | vif |  | eq | `[[art:d9b015aa:vif.max]]` | verified | 4.973309839 |
| 264 | sensitivity | The largest variance inflation factor across the retained fe… | 10 | ratio | vif |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 265 | sensitivity | That maximum is carried by the note rate, whose variance inf… | 4.973 | ratio | vif |  | eq | `[[art:dfd3d0c7:vif.note_rate]]` | verified | 4.973309839 |
| 266 | sensitivity | That maximum is carried by the note rate, whose variance inf… | 3.442 | ratio | vif |  | eq | `[[art:15d2d2b7:vif.burnout]]` | verified | 3.441796277 |
| 267 | sensitivity | That maximum is carried by the note rate, whose variance inf… | 2.929 | ratio | vif |  | eq | `[[art:da5f6107:vif.loan_age]]` | verified | 2.928894489 |
| 268 | sensitivity | That maximum is carried by the note rate, whose variance inf… | 2.226 | ratio | vif |  | eq | `[[art:13d92899:vif.incentive]]` | verified | 2.225948498 |
| 269 | sensitivity | That maximum is carried by the note rate, whose variance inf… | 1.708 | ratio | vif |  | eq | `[[art:4802c713:vif.sato]]` | verified | 1.70802752 |
| 270 | sensitivity | The remaining retained features sit closer to the no-colline… | 1.018 | ratio | vif |  | eq | `[[art:0046feb1:vif.season_cos]]` | verified | 1.017677402 |
| 271 | sensitivity | The remaining retained features sit closer to the no-colline… | 1.008 | ratio | vif |  | eq | `[[art:8908e744:vif.credit_score]]` | verified | 1.007807025 |
| 272 | sensitivity | The remaining retained features sit closer to the no-colline… | 1.006 | ratio | vif |  | eq | `[[art:127ff775:vif.orig_upb_log]]` | verified | 1.005824647 |
| 273 | sensitivity | The remaining retained features sit closer to the no-colline… | 1.004 | ratio | vif |  | eq | `[[art:ca78c9fc:vif.orig_ltv]]` | verified | 1.004492604 |
| 274 | sensitivity | The remaining retained features sit closer to the no-colline… | 1.004 | ratio | vif |  | eq | `[[art:c19a5e9a:vif.season_sin]]` | verified | 1.004122258 |
| 275 | sensitivity | Belsley's condition number of the column-standardised design… | 4.941 | ratio | condition_number |  | eq | `[[art:cf4a0dab:condition_number]]` | verified | 4.941319585 |
| 276 | sensitivity | Belsley's condition number of the column-standardised design… | 30 | ratio | condition_number |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 277 | sensitivity | The declared tolerance for the discrimination difference acr… | 0.1 | ratio | auc_gap |  | eq | `[[art:b64213d7:threshold.R1.auc_gap]]` | verified | 0.1 |
| 278 | sensitivity | A sign flip is declared to count only where a feature is amo… | 0.05 | ratio | sign_flip_coef |  | eq | `[[art:aca84377:threshold.R1.sign_flip_coef]]` | verified | 0.05 |
| 279 | sensitivity | A sign flip is declared to count only where a feature is amo… | 2 | ratio | sign_flip_z |  | eq | `[[art:2e4428c7:threshold.R1.sign_flip_z]]` | verified | 2 |
| 280 | sensitivity | Under that definition the indicator stands at 0 for the note… | 0 | count | sign_flip |  | eq | `[[art:e7ce4912:stability.note_rate.sign_flip]]` | verified | 0 |
| 281 | sensitivity | Under that definition the indicator stands at 0 for the note… | 0 | count | sign_flip |  | eq | `[[art:0cc7a37d:stability.incentive.sign_flip]]` | verified | 0 |
| 282 | sensitivity | Under that definition the indicator stands at 0 for the note… | 0 | count | sign_flip |  | eq | `[[art:6bc05e82:stability.burnout.sign_flip]]` | verified | 0 |
| 283 | sensitivity | Under that definition the indicator stands at 0 for the note… | 0 | count | sign_flip |  | eq | `[[art:b7191217:stability.loan_age.sign_flip]]` | verified | 0 |
| 284 | sensitivity | It likewise stands at 0 for the spread at origination , at 0… | 0 | count | sign_flip |  | eq | `[[art:1f302ccd:stability.sato.sign_flip]]` | verified | 0 |
| 285 | sensitivity | It likewise stands at 0 for the spread at origination , at 0… | 0 | count | sign_flip |  | eq | `[[art:d956c276:stability.credit_score.sign_flip]]` | verified | 0 |
| 286 | sensitivity | It likewise stands at 0 for the spread at origination , at 0… | 0 | count | sign_flip |  | eq | `[[art:054d5fab:stability.orig_ltv.sign_flip]]` | verified | 0 |
| 287 | sensitivity | It likewise stands at 0 for the spread at origination , at 0… | 0 | count | sign_flip |  | eq | `[[art:fb1ae6c8:stability.orig_upb_log.sign_flip]]` | verified | 0 |
| 288 | sensitivity | It likewise stands at 0 for the spread at origination , at 0… | 0 | count | sign_flip |  | eq | `[[art:6ba36a3b:stability.season_sin.sign_flip]]` | verified | 0 |
| 289 | sensitivity | It likewise stands at 0 for the spread at origination , at 0… | 0 | count | sign_flip |  | eq | `[[art:1850e2de:stability.season_cos.sign_flip]]` | verified | 0 |
| 290 | sensitivity | At the extreme downward shock the change in servicing value… | -1300000 | currency | value_change |  | eq | `[[art:1bb5faa9:scenario.value_change.-300]]` | verified | -1299764.383 |
| 291 | sensitivity | At the intermediate downward shock the change is -821800 and… | -821800 | currency | value_change |  | eq | `[[art:fc515a18:scenario.value_change.-200]]` | verified | -821809.3771 |
| 292 | sensitivity | At the intermediate downward shock the change is -821800 and… | -295200 | currency | value_change |  | eq | `[[art:8d716ed3:scenario.value_change.-100]]` | verified | -295185.0824 |
| 293 | sensitivity | The base case change is 0 by construction. | 0 | currency | value_change |  | eq | `[[art:1e1b0b88:scenario.value_change.0]]` | verified | 0 |
| 294 | sensitivity | On the upward side the change is 103800 at the mildest shock… | 103800 | currency | value_change |  | eq | `[[art:32d76ec2:scenario.value_change.100]]` | verified | 103821.8979 |
| 295 | sensitivity | On the upward side the change is 103800 at the mildest shock… | 135900 | currency | value_change |  | eq | `[[art:9ff1104d:scenario.value_change.200]]` | verified | 135913.6115 |
| 296 | sensitivity | On the upward side the change is 103800 at the mildest shock… | 145400 | currency | value_change |  | eq | `[[art:a5bb5830:scenario.value_change.300]]` | verified | 145416.3854 |
| 297 | sensitivity | The convexity measure, formed as the change at the extreme d… | -1154000 | currency | convexity |  | eq | `[[art:e6e5c89b:scenario.convexity]]` | verified | -1154347.998 |
| 298 | findings | The share of test rows whose feature values also appear in t… | 0.02997 | ratio | leakage.overlap.features | test | eq | `[[art:bcbccff8:leakage.overlap.features]]` | verified | 0.02997009492 |
| 299 | findings | That share was read against a bound of 0.005 , which the rul… | 0.005 | ratio | threshold.L2.overlap.features_effective |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 300 | findings | That share was read against a bound of 0.005 , which the rul… | 0.005 | ratio | threshold.L2.overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 301 | findings | The share of train rows whose feature values are not unique… | 0 | ratio | leakage.duplicates.train | train | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 302 | findings | What does the model discriminate on inside the segment where… | -1 | ratio | sign_check.note_rate.coef_sign |  | eq | `[[art:aecf7ccb:sign_check.note_rate.coef_sign]]` | verified | -1 |
| 303 | findings | What does the model discriminate on inside the segment where… | 1 | ratio | sign_check.note_rate.univariate_direction |  | eq | `[[art:61f6e1ac:sign_check.note_rate.univariate_direction]]` | verified | 1 |
| 304 | findings | What does the model discriminate on inside the segment where… | 0 | ratio | sign_check.note_rate.agrees |  | eq | `[[art:a453463d:sign_check.note_rate.agrees]]` | verified | 0 |
| 305 | monitoring | Calibration should be tracked as the logistic slope of the o… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 306 | monitoring | Calibration should be tracked as the logistic slope of the o… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 307 | monitoring | The validation reading of 0.939 sits inside that declared in… | 0.939 | ratio | calibration_slope | test | eq | `[[art:80d029cc:calibration_slope.test]]` | verified | 0.9389856921 |
| 308 | monitoring | Discrimination should be tracked as the area under the ROC c… | 0.65 | ratio | auc | test | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 309 | monitoring | The validation reading of 0.7759 stands above that floor and… | 0.7759 | ratio | auc | test | eq | `[[art:225b99b5:metrics.test.auc]]` | verified | 0.7759451414 |
| 310 | monitoring | Input and score stability should be tracked as the populatio… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 311 | monitoring | The largest train-to-test value observed in this validation… | 0.06021 | ratio | psi |  | eq | `[[art:e09026cf:psi.max]]` | verified | 0.06021122495 |

## Appendix B — Artifact index

The store holds 287 artifacts; the 222 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `ablation.baseline_auc` | `fdbd1084` | scalar | 0.7674403486 | AUC on test of a refit of the champion's functional form on every retained feature, the level each ablation delta is measured from |
| `ablation.burnout.delta_auc` | `177952dc` | scalar | -0.0003017983163 | change in test AUC when the champion's form is refitted without burnout |
| `ablation.credit_score.delta_auc` | `479f419e` | scalar | -0.01477490391 | change in test AUC when the champion's form is refitted without credit_score |
| `ablation.incentive.delta_auc` | `7213d612` | scalar | -0.04118780629 | change in test AUC when the champion's form is refitted without incentive |
| `ablation.loan_age.delta_auc` | `863965a3` | scalar | 0.0008139569301 | change in test AUC when the champion's form is refitted without loan_age |
| `ablation.note_rate.delta_auc` | `730edeaf` | scalar | -0.002577177916 | change in test AUC when the champion's form is refitted without note_rate |
| `ablation.orig_ltv.delta_auc` | `6b1c5d74` | scalar | -0.002214597102 | change in test AUC when the champion's form is refitted without orig_ltv |
| `ablation.orig_upb_log.delta_auc` | `5bc33417` | scalar | -0.01960949095 | change in test AUC when the champion's form is refitted without orig_upb_log |
| `ablation.sato.delta_auc` | `c477ddcb` | scalar | 0.0005940828502 | change in test AUC when the champion's form is refitted without sato |
| `ablation.season_cos.delta_auc` | `655cfcbe` | scalar | -0.0004809745496 | change in test AUC when the champion's form is refitted without season_cos |
| `ablation.season_sin.delta_auc` | `0b5a4b1b` | scalar | -0.0003927077916 | change in test AUC when the champion's form is refitted without season_sin |
| `calibration.mean_rel_gap.out_of_time` | `4084ccd4` | scalar | 0.08366462899 | mean predicted against observed on out_of_time, relative |
| `calibration.mean_rel_gap.test` | `40409705` | scalar | 0.03753966213 | mean predicted against observed on test, relative |
| `calibration.mean_rel_gap.train` | `0b47f454` | scalar | 0.009844346741 | mean predicted against observed on train, relative |
| `calibration.mean_rel_gap.vintage_holdout` | `4b6b5371` | scalar | 0.2276910236 | mean predicted against observed on vintage_holdout, relative |
| `calibration.test` | `9633f335` | table | table, 10 rows | calibration by decile of predicted probability on test |
| `calibration_intercept.out_of_time` | `e50f09e0` | scalar | -0.0583358688 | logistic regression of the outcome on logit(p) on out_of_time: the intercept |
| `calibration_intercept.test` | `f2adc1ec` | scalar | -0.2952175968 | logistic regression of the outcome on logit(p) on test: the intercept |
| `calibration_intercept.train` | `f381282b` | scalar | -0.02732327203 | logistic regression of the outcome on logit(p) on train: the intercept |
| `calibration_intercept.vintage_holdout` | `1256d464` | scalar | -0.9462036021 | logistic regression of the outcome on logit(p) on vintage_holdout: the intercept |
| `calibration_slope.out_of_time` | `860e5dd2` | scalar | 1.007762878 | logistic regression of the outcome on logit(p) on out_of_time: the slope |
| `calibration_slope.test` | `80d029cc` | scalar | 0.9389856921 | logistic regression of the outcome on logit(p) on test: the slope |
| `calibration_slope.train` | `a10d9430` | scalar | 0.9958299755 | logistic regression of the outcome on logit(p) on train: the slope |
| `calibration_slope.vintage_holdout` | `20da9c88` | scalar | 0.8363376022 | logistic regression of the outcome on logit(p) on vintage_holdout: the slope |
| `challenger.auc` | `abe111e2` | scalar | 0.7365834528 | the challenger's AUC on test |
| `challenger.brier` | `acd8735a` | scalar | 0.009228035552 | the challenger's Brier score on test |
| `challenger.delta_auc` | `46dde851` | scalar | -0.03936168863 | the challenger's AUC on test minus the champion's |
| `condition_number` | `cf4a0dab` | scalar | 4.941319585 | Belsley's condition number of the column-standardised design |
| `cpr.out_of_time.mae` | `6699b093` | scalar | 0.05670843092 | mean absolute difference between actual and predicted CPR on out_of_time |
| `cpr.test` | `28397851` | table | table, 71 rows | actual against predicted CPR by period on test |
| `cpr.test.mae` | `13564933` | scalar | 0.04285359689 | mean absolute difference between actual and predicted CPR on test |
| `cpr.train.mae` | `1baf9f3a` | scalar | 0.02615146691 | mean absolute difference between actual and predicted CPR on train |
| `cpr.vintage_holdout.mae` | `34f4c62c` | scalar | 0.03048231099 | mean absolute difference between actual and predicted CPR on vintage_holdout |
| `csi.burnout` | `2af1e79a` | scalar | 0.001162803488 | CSI of burnout: its contribution to the shift in the linear predictor |
| `csi.credit_score` | `17137aa1` | scalar | 0.008068926476 | CSI of credit_score: its contribution to the shift in the linear predictor |
| `csi.incentive` | `4fb0f08d` | scalar | 0.005098722582 | CSI of incentive: its contribution to the shift in the linear predictor |
| `csi.loan_age` | `df52c920` | scalar | 0 | CSI of loan_age: its contribution to the shift in the linear predictor |
| `csi.max` | `cf5a5274` | scalar | 0.0360163058 | the largest characteristic stability index |
| `csi.note_rate` | `d8ee67a8` | scalar | 0.01444840152 | CSI of note_rate: its contribution to the shift in the linear predictor |
| `csi.orig_ltv` | `5ce12077` | scalar | 0.0360163058 | CSI of orig_ltv: its contribution to the shift in the linear predictor |
| `csi.orig_upb_log` | `d6de1f4a` | scalar | 0.003374084917 | CSI of orig_upb_log: its contribution to the shift in the linear predictor |
| `csi.sato` | `5d9bf44b` | scalar | 0.0005107233981 | CSI of sato: its contribution to the shift in the linear predictor |
| `csi.season_cos` | `f8939193` | scalar | 0.0006696922627 | CSI of season_cos: its contribution to the shift in the linear predictor |
| `csi.season_sin` | `eef3a546` | scalar | 5.589052952e-05 | CSI of season_sin: its contribution to the shift in the linear predictor |
| `deciles.out_of_time.top2_capture` | `e28ccabb` | scalar | 0.5863636364 | share of out_of_time events in the top two deciles |
| `deciles.test` | `8e91a22f` | table | table, 10 rows | decile separation on test; decile 1 holds the highest probabilities |
| `deciles.test.top2_capture` | `43c4adc5` | scalar | 0.5806451613 | share of test events in the top two deciles |
| `deciles.train.top2_capture` | `adaecbab` | scalar | 0.5955414013 | share of train events in the top two deciles |
| `deciles.vintage_holdout.top2_capture` | `0d0c0310` | scalar | 0.5806451613 | share of vintage_holdout events in the top two deciles |
| `leakage.duplicates.train` | `4474c227` | scalar | 0 | share of train rows whose feature values are not unique within train |
| `leakage.name_screen.n_matched` | `407e62be` | scalar | 0 | feature names matching the target-adjacent lexicon |
| `leakage.overlap` | `4fb7c6b6` | scalar | 0.02997009492 | share of test rows whose feature values also appear in train |
| `leakage.overlap.features` | `bcbccff8` | scalar | 0.02997009492 | share of test rows whose feature values also appear in train |
| `leakage.overlap.ids` | `63d37fc5` | scalar | 0 | share of out_of_time rows whose ['loan_id', 'period'] also identify a row of train |
| `leakage.target_corr.max_single_feature_auc` | `6db1c162` | scalar | 0.7244788731 | the AUC of the strongest single feature |
| `leakage.timing.n_flagged` | `742bcd24` | scalar | 0 | features declared during_period or after_outcome |
| `metrics.out_of_time.auc` | `2e910103` | scalar | 0.7871132191 | auc on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.brier` | `9dbe134b` | scalar | 0.01712189167 | brier on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.event_rate` | `83ccf5c0` | scalar | 0.01794892714 | event_rate on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.gini` | `442c1e75` | scalar | 0.5742264382 | gini on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.ks` | `c8dd3c8a` | scalar | 0.4421873466 | ks on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.logloss` | `793f94ec` | scalar | 0.07960455821 | logloss on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.mean_predicted` | `3cc343ae` | scalar | 0.01945061747 | mean_predicted on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.n` | `7898809e` | scalar | 12257 | n on out_of_time, recomputed by quaestor |
| `metrics.test.auc` | `225b99b5` | scalar | 0.7759451414 | auc on test, recomputed by quaestor |
| `metrics.test.brier` | `66eaf26f` | scalar | 0.007892754939 | brier on test, recomputed by quaestor |
| `metrics.test.event_rate` | `570cc08a` | scalar | 0.008061370433 | event_rate on test, recomputed by quaestor |
| `metrics.test.gini` | `0aebb8a9` | scalar | 0.5518902828 | gini on test, recomputed by quaestor |
| `metrics.test.ks` | `3abd1f94` | scalar | 0.4194605474 | ks on test, recomputed by quaestor |
| `metrics.test.logloss` | `a801271e` | scalar | 0.04261094263 | logloss on test, recomputed by quaestor |
| `metrics.test.mean_predicted` | `542ddc6b` | scalar | 0.008363991555 | mean_predicted on test, recomputed by quaestor |
| `metrics.test.n` | `e55953e1` | scalar | 15382 | n on test, recomputed by quaestor |
| `metrics.test.sub.period_high` | `d28f323d` | table | table, 10 rows | every metric on the period above_median slice of test |
| `metrics.test.sub.period_high.auc` | `a6fb0274` | scalar | 0.7460118243 | auc on the period above_median slice of test |
| `metrics.test.sub.period_high.auc_gap` | `95a3f44c` | scalar | 0.02993331709 | how far AUC on the period above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.period_high.event_rate` | `f82a90d7` | scalar | 0.01069518717 | event_rate on the period above_median slice of test |
| `metrics.test.sub.period_high.mean_predicted` | `cf372d1a` | scalar | 0.01159277483 | mean_predicted on the period above_median slice of test |
| `metrics.test.sub.period_high.mean_rel_gap` | `794ad5e8` | scalar | 0.08392444656 | mean predicted against observed on the period above_median slice of test, relative |
| `metrics.test.sub.period_high.share` | `a6e7ff2a` | scalar | 0.4862826681 | the share of test the period above_median slice holds |
| `metrics.train.auc` | `88da2e97` | scalar | 0.7887583845 | auc on train, recomputed by quaestor |
| `metrics.train.brier` | `a3ddd3d7` | scalar | 0.008396301302 | brier on train, recomputed by quaestor |
| `metrics.train.event_rate` | `73327d6c` | scalar | 0.008608872073 | event_rate on train, recomputed by quaestor |
| `metrics.train.gini` | `a786960b` | scalar | 0.5775167691 | gini on train, recomputed by quaestor |
| `metrics.train.ks` | `12bd02b0` | scalar | 0.4560599388 | ks on train, recomputed by quaestor |
| `metrics.train.logloss` | `fce5969c` | scalar | 0.04441572278 | logloss on train, recomputed by quaestor |
| `metrics.train.mean_predicted` | `3eee0092` | scalar | 0.008693620795 | mean_predicted on train, recomputed by quaestor |
| `metrics.train.n` | `82d2c58e` | scalar | 36474 | n on train, recomputed by quaestor |
| `metrics.vintage_holdout.auc` | `ff084e89` | scalar | 0.7721582541 | auc on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.brier` | `31ac126b` | scalar | 0.00476513883 | brier on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.event_rate` | `e3590a16` | scalar | 0.004817105386 | event_rate on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.gini` | `14144a5d` | scalar | 0.5443165082 | gini on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.ks` | `178bbe36` | scalar | 0.4492226111 | ks on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.logloss` | `e1b4f0f1` | scalar | 0.02814470369 | logloss on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.mean_predicted` | `08dbc56d` | scalar | 0.005913917042 | mean_predicted on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.n` | `37a92951` | scalar | 32177 | n on vintage_holdout, recomputed by quaestor |
| `profile.out_of_time.missing.max` | `4dafce11` | scalar | 0 | the largest missing fraction in out_of_time |
| `profile.out_of_time.n` | `fa39c5cf` | scalar | 12257 | rows in out_of_time |
| `profile.test.missing.max` | `f813848d` | scalar | 0 | the largest missing fraction in test |
| `profile.test.n` | `e3abc1b8` | scalar | 15382 | rows in test |
| `profile.train.missing.max` | `050a3099` | scalar | 0 | the largest missing fraction in train |
| `profile.train.n` | `7e94d818` | scalar | 36474 | rows in train |
| `profile.vintage_holdout.missing.max` | `329bb430` | scalar | 0 | the largest missing fraction in vintage_holdout |
| `profile.vintage_holdout.n` | `426e712a` | scalar | 32177 | rows in vintage_holdout |
| `psi.burnout` | `33f5ebc2` | scalar | 0.004931216889 | PSI of burnout between train and test |
| `psi.credit_score` | `d18c84c9` | scalar | 0.06021122495 | PSI of credit_score between train and test |
| `psi.incentive` | `68e58ed4` | scalar | 0.0008807210511 | PSI of incentive between train and test |
| `psi.loan_age` | `0de705ab` | scalar | 0.0001935522768 | PSI of loan_age between train and test |
| `psi.max` | `e09026cf` | scalar | 0.06021122495 | the largest train-to-test PSI, score included |
| `psi.note_rate` | `c7f1a67b` | scalar | 0.009203799735 | PSI of note_rate between train and test |
| `psi.orig_ltv` | `5a52f767` | scalar | 0.03524928958 | PSI of orig_ltv between train and test |
| `psi.orig_upb_log` | `a8060a5e` | scalar | 0.04275593453 | PSI of orig_upb_log between train and test |
| `psi.out_of_time.burnout` | `2f1775e6` | scalar | 2.940517648 | PSI of burnout between train and out_of_time |
| `psi.out_of_time.credit_score` | `736d4786` | scalar | 0.05906553221 | PSI of credit_score between train and out_of_time |
| `psi.out_of_time.incentive` | `8f1aad44` | scalar | 0.4959842347 | PSI of incentive between train and out_of_time |
| `psi.out_of_time.loan_age` | `a53fe5b7` | scalar | 2.482521703 | PSI of loan_age between train and out_of_time |
| `psi.out_of_time.note_rate` | `41ec908a` | scalar | 0.6979848935 | PSI of note_rate between train and out_of_time |
| `psi.out_of_time.orig_ltv` | `3e1cfd51` | scalar | 0.04223900725 | PSI of orig_ltv between train and out_of_time |
| `psi.out_of_time.orig_upb_log` | `bd610e8f` | scalar | 0.0679791761 | PSI of orig_upb_log between train and out_of_time |
| `psi.out_of_time.sato` | `8c2d71b1` | scalar | 0.01229057251 | PSI of sato between train and out_of_time |
| `psi.out_of_time.season_cos` | `9bb91b1d` | scalar | 0.01068186712 | PSI of season_cos between train and out_of_time |
| `psi.out_of_time.season_sin` | `1c848842` | scalar | 0.02790812853 | PSI of season_sin between train and out_of_time |
| `psi.out_of_time.y_score` | `926393e5` | scalar | 0.706727876 | PSI of the score between train and out_of_time |
| `psi.sato` | `d035c9fe` | scalar | 0.02937047655 | PSI of sato between train and test |
| `psi.season_cos` | `4c164ad6` | scalar | 2.852014247e-05 | PSI of season_cos between train and test |
| `psi.season_sin` | `34445e67` | scalar | 3.360751567e-06 | PSI of season_sin between train and test |
| `psi.vintage_holdout.burnout` | `d7eb40ee` | scalar | 0.04787342519 | PSI of burnout between train and vintage_holdout |
| `psi.vintage_holdout.credit_score` | `eb8b579f` | scalar | 0.03956501951 | PSI of credit_score between train and vintage_holdout |
| `psi.vintage_holdout.incentive` | `a5809fbc` | scalar | 0.4467844664 | PSI of incentive between train and vintage_holdout |
| `psi.vintage_holdout.loan_age` | `880920e4` | scalar | 0.07103580061 | PSI of loan_age between train and vintage_holdout |
| `psi.vintage_holdout.note_rate` | `8903dffa` | scalar | 0.6035871138 | PSI of note_rate between train and vintage_holdout |
| `psi.vintage_holdout.orig_ltv` | `e538a378` | scalar | 0.0287751179 | PSI of orig_ltv between train and vintage_holdout |
| `psi.vintage_holdout.orig_upb_log` | `983493d4` | scalar | 0.03584175044 | PSI of orig_upb_log between train and vintage_holdout |
| `psi.vintage_holdout.sato` | `9cde942f` | scalar | 0.03244197722 | PSI of sato between train and vintage_holdout |
| `psi.vintage_holdout.season_cos` | `0b2e1ed1` | scalar | 0.001415335964 | PSI of season_cos between train and vintage_holdout |
| `psi.vintage_holdout.season_sin` | `accfeb86` | scalar | 0.0007471395641 | PSI of season_sin between train and vintage_holdout |
| `psi.vintage_holdout.y_score` | `b7edb3fa` | scalar | 0.1381257303 | PSI of the score between train and vintage_holdout |
| `psi.y_score` | `b90e64c8` | scalar | 0.001802030258 | PSI of the score between train and test |
| `run.features` | `61276a96` | json | json | the subject's features.json |
| `run.model_summary` | `8e6d6768` | json | json | the subject's model_summary.json |
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |
| `scenario.convexity` | `e6e5c89b` | scalar | -1154347.998 | the value change at -300 bp plus the change at 300 bp; negative when the fall outweighs the rise |
| `scenario.value_by_shock` | `51e09003` | table | table, 7 rows | servicing value, its change from the base case and first-year CPR, by shock |
| `scenario.value_change.-100` | `8d716ed3` | scalar | -295185.0824 | change in servicing value at -100 bp |
| `scenario.value_change.-200` | `fc515a18` | scalar | -821809.3771 | change in servicing value at -200 bp |
| `scenario.value_change.-300` | `1bb5faa9` | scalar | -1299764.383 | change in servicing value at -300 bp |
| `scenario.value_change.0` | `1e1b0b88` | scalar | 0 | change in servicing value at 0 bp |
| `scenario.value_change.100` | `32d76ec2` | scalar | 103821.8979 | change in servicing value at 100 bp |
| `scenario.value_change.200` | `9ff1104d` | scalar | 135913.6115 | change in servicing value at 200 bp |
| `scenario.value_change.300` | `a5bb5830` | scalar | 145416.3854 | change in servicing value at 300 bp |
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
| `stability.auc_by_regime` | `411b1cfe` | table | table, 2 rows | the champion's AUC within each rate_regime on train |
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
| `thresholds.evaluation` | `6eb162e0` | table | table, 4 rows | every threshold package.yaml declares, with its bound, the recomputed value and the outcome |
| `vif.burnout` | `15d2d2b7` | scalar | 3.441796277 | variance inflation factor of burnout on train |
| `vif.credit_score` | `8908e744` | scalar | 1.007807025 | variance inflation factor of credit_score on train |
| `vif.incentive` | `13d92899` | scalar | 2.225948498 | variance inflation factor of incentive on train |
| `vif.loan_age` | `da5f6107` | scalar | 2.928894489 | variance inflation factor of loan_age on train |
| `vif.max` | `d9b015aa` | scalar | 4.973309839 | the largest variance inflation factor |
| `vif.note_rate` | `dfd3d0c7` | scalar | 4.973309839 | variance inflation factor of note_rate on train |
| `vif.orig_ltv` | `ca78c9fc` | scalar | 1.004492604 | variance inflation factor of orig_ltv on train |
| `vif.orig_upb_log` | `127ff775` | scalar | 1.005824647 | variance inflation factor of orig_upb_log on train |
| `vif.sato` | `4802c713` | scalar | 1.70802752 | variance inflation factor of sato on train |
| `vif.season_cos` | `0046feb1` | scalar | 1.017677402 | variance inflation factor of season_cos on train |
| `vif.season_sin` | `c19a5e9a` | scalar | 1.004122258 | variance inflation factor of season_sin on train |

## Appendix C — Run trace summary

| quantity | value |
|---|---|
| tool calls | 18 (run_model 1, profile_data 1, compute_metrics 2, check_leakage 3, check_stability 1, check_collinearity 1, challenger_compare 1, run_scenarios 1, retrieve_guidance 7) |
| plan steps (bounded loop) | 4 |
| LLM calls | 22 (plan 4, draft 9, extract 9) |
| re-asks | 0 |
| repair rounds | 2 |
| tokens in / out | 279,202 / 124,435 |
| notional cost (USD) | 5.9585 |
| wall-clock (s) | 1297.09 |
| subject run (s) | 2.78 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | msr_prepayment-full_agent-20260920T183556Z-e61d346a |

## Appendix D — Not checked

| item | reason |
|---|---|
| developer claims (T1, claim channel) | The package declares 3 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
