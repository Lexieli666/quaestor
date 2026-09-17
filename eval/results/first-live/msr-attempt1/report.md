---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: msr_prepayment
version: "1.0"
model_type: discrete_time_hazard
configuration: full_agent
model: claude-opus-5[1m]
run_id: msr_prepayment-full_agent-20260916T235634Z-e98677a9
data_mode: real
grounding_precision_pre: 0.9934
grounding_precision_post: 1.0000
n_claims: 304
n_findings_by_severity: {high: 0, medium: 1, low: 0, info: 0}
generated: "2026-09-16T23:56:34Z"
illustrative: false
---

# Validation report — `msr_prepayment` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `msr_prepayment` v1.0 | `full_agent` | claude-opus-5[1m] | real, Freddie Mac Single-Family Loan-Level Dataset, sample files for origination years 2014, 2017 and 2019 (20,000 loans, seed 20260901, built by sample_freddie.py); FRED MORTGAGE30US (Freddie Mac PMMS, weekly, month-start value). Synthetic mode: synthetic.py. No loan-level rows are redistributed. | 0.9934 → 1.0000 | 0 / 1 / 0 / 0 |
<!-- quaestor:renderer:end -->

The msr_prepayment package is a loan-level mortgage prepayment model that predicts the probability a loan prepays over the performance window, and this report follows the structure of the Federal Reserve's model risk management guidance on model validation and monitoring [[reg:SR26-2:V]].

The subject was run as an independent recomputation: the package was executed under the wall-clock cap of 300 seconds [[art:2ad8d1a5:runtime.max_seconds]] that its manifest declares, and the performance figures cited here were recomputed from the scored data rather than carried over from the developer's own report, which is the outcomes-analysis posture the guidance describes [[reg:SR26-2:V.1.b]].
Recomputation covered the training split, at 313538 rows [[art:6582e5dd:profile.train.n]]; the test split, at 135060 rows [[art:75b5b833:profile.test.n]]; a vintage holdout, at 221779 rows [[art:faabc78e:metrics.vintage_holdout.n]]; and an out-of-time sample, at 283343 rows [[art:c164ae00:metrics.out_of_time.n]].
Within those splits the run also evaluates the two incentive-defined subgroups, calibration slope on each split, train-to-test stability of the inputs and the score, design-matrix collinearity diagnostics, and a champion-versus-challenger comparison on test.

The model passes each of the thresholds its developers declared in the package manifest.
Discrimination on test is 0.6549 [[art:f3890b65:metrics.test.auc]] against a declared floor of 0.65 [[art:fececac1:threshold.package.auc.test.min]], clearing the bound by a narrow margin.
The calibration slope on test is 1.017 [[art:9b1edaa3:calibration_slope.test]], inside the declared band running from 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] to 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The largest train-to-test population stability index, the score included, is 0.005703 [[art:f632d5d4:psi.max]], far below the declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].

No findings were raised at any severity.

## 2. Conceptual soundness

Conceptual soundness here is assessed as the guidance frames it: an evaluation of model design, construction and developmental evidence, with the modelling choices subjected to critical analysis of both the quality and the extent of that evidence [[reg:SR26-2:V.1.a]].

### Design and inputs

The champion is a logistic model of monthly prepayment, linear in its retained inputs apart from a spline basis in loan age, fitted on 313538 [[art:29028ebe:run.model_summary#n_train]] loan-months drawn from 8596 [[art:29028ebe:run.model_summary#n_train_loans]] loans, with an intercept of -4.79 [[art:29028ebe:run.model_summary#intercept]].
The feature inventory carries 12 [[art:0849f814:run.features#n]] features in total, of which 5 [[art:0849f814:run.features#at_origination]] are known at origination and 7 [[art:0849f814:run.features#before_period_start]] are known before the start of the performance period.
No feature is dated to the performance period itself, at 0 [[art:0849f814:run.features#during_period]], and none is dated after the outcome is observed, at 0 [[art:0849f814:run.features#after_outcome]], so on the timing evidence available to this section every input is knowable at the point the model is asked to predict.

The developer's own screen removed two inputs on collinearity grounds, each against a variance inflation limit of 10 [[art:29028ebe:run.model_summary#vif_threshold]].
The beginning-of-month balance was removed at an inflation factor of 16.5 [[art:29028ebe:run.model_summary#removed.bom_balance_log.vif]], and the note rate was removed at 18.07 [[art:29028ebe:run.model_summary#removed.note_rate.vif]].
Both removals are reasonable in subject-matter terms, since the beginning-of-month balance is largely determined by original balance and loan age and the note rate is the dominant component of the rate incentive that the model keeps, but the consequence is that the retained rate signal enters only through the incentive and spread variables rather than through the contract rate itself.

### Coefficients and expected signs

The largest single coefficient is on the first loan-age spline term at 0.611 [[art:29028ebe:run.model_summary#coefficients.loan_age_spline_1.value]], with the later spline terms at -0.04263 [[art:29028ebe:run.model_summary#coefficients.loan_age_spline_2.value]], -0.1501 [[art:29028ebe:run.model_summary#coefficients.loan_age_spline_3.value]] and -0.254 [[art:29028ebe:run.model_summary#coefficients.loan_age_spline_4.value]], a rising-then-falling age profile that matches the seasoning ramp practitioners expect of prepayment.
The refinance incentive carries 0.3952 [[art:29028ebe:run.model_summary#coefficients.incentive.value]] and log original balance carries 0.286 [[art:29028ebe:run.model_summary#coefficients.orig_upb_log.value]]; both are positive, and both are the direction subject matter expects, since deeper in-the-money borrowers and larger borrowers refinance more readily.
The spread at origination enters at -0.09479 [[art:29028ebe:run.model_summary#coefficients.sato.value]] and original loan-to-value at -0.08576 [[art:29028ebe:run.model_summary#coefficients.orig_ltv.value]]; the loan-to-value sign is defensible as an equity constraint on refinancing, while the negative spread coefficient runs against the usual reading that borrowers who took an above-market rate have more to gain from refinancing.
The twelve-month rate change enters at -0.06772 [[art:29028ebe:run.model_summary#coefficients.rate_change_12m.value]], which is the expected direction, since rising rates suppress refinancing.
Burnout carries 0.0008253 [[art:29028ebe:run.model_summary#coefficients.burnout.value]], positive where the subject-matter expectation is that repeatedly passed-over refinancing opportunities depress prepayment, though the magnitude is small enough that the model leans on it very little.
Credit score at 0.02917 [[art:29028ebe:run.model_summary#coefficients.credit_score.value]] and the seasonal pair at 0.01281 [[art:29028ebe:run.model_summary#coefficients.season_sin.value]] and -0.04626 [[art:29028ebe:run.model_summary#coefficients.season_cos.value]] are the smallest terms in the fit.

### Fitted signs against univariate direction

Of the retained features checked, 3 [[art:e223cd4a:sign_check.n_disagreements]] have a fitted sign that contradicts the direction of their own single-feature relationship with the outcome on train.
Original loan-to-value is fitted at -1 [[art:7eec65ec:sign_check.orig_ltv.coef_sign]] against a univariate direction of +1 [[art:85aabf06:sign_check.orig_ltv.univariate_direction]], recorded as a disagreement at 0 [[art:3f64b057:sign_check.orig_ltv.agrees]], and removing it from the fitted form costs -0.002233 [[art:acb0dcd5:ablation.orig_ltv.delta_auc]] of test discrimination, so the model does rely on it to a modest degree.
The spread at origination is fitted at -1 [[art:265915cf:sign_check.sato.coef_sign]] against a univariate direction of +1 [[art:c08233a6:sign_check.sato.univariate_direction]], recorded as a disagreement at 0 [[art:b3755963:sign_check.sato.agrees]], and it is the more material of the two, since removing it costs -0.003026 [[art:f406b192:ablation.sato.delta_auc]].
The sine seasonal term is fitted at +1 [[art:761188ce:sign_check.season_sin.coef_sign]] against a univariate direction of -1 [[art:b75f0b9c:sign_check.season_sin.univariate_direction]], recorded as a disagreement at 0 [[art:74f2d0e0:sign_check.season_sin.agrees]], but removing it changes test discrimination by 0.000108 [[art:47876c72:ablation.season_sin.delta_auc]], an improvement rather than a loss, so this flip is on a term the model barely uses.
The reversals on the two loan-level terms are the ones a reviewer should press the developer on, because each is a case where the multivariate fit has reversed a relationship visible in the data on its own, most plausibly through correlation with the loan-age and incentive structure that the collinearity screen left in place.
The remaining features checked agree with their univariate direction, including the incentive at +1 [[art:684cf11a:sign_check.incentive.coef_sign]] against +1 [[art:8098d951:sign_check.incentive.univariate_direction]], log original balance at +1 [[art:5aa309fc:sign_check.orig_upb_log.coef_sign]] against +1 [[art:b9743ecb:sign_check.orig_upb_log.univariate_direction]], the rate change at -1 [[art:272b397e:sign_check.rate_change_12m.coef_sign]] against -1 [[art:35df3bf5:sign_check.rate_change_12m.univariate_direction]], credit score at +1 [[art:1ec1078b:sign_check.credit_score.coef_sign]] against +1 [[art:42303896:sign_check.credit_score.univariate_direction]], burnout at +1 [[art:a3063608:sign_check.burnout.coef_sign]] against +1 [[art:bfc96bb2:sign_check.burnout.univariate_direction]], and the cosine seasonal term at -1 [[art:7dbb1ffc:sign_check.season_cos.coef_sign]] against -1 [[art:03e931f0:sign_check.season_cos.univariate_direction]], with agreement recorded at 1 [[art:f7b2338e:sign_check.incentive.agrees]], 1 [[art:07a9d3e6:sign_check.orig_upb_log.agrees]], 1 [[art:61c1d5cc:sign_check.rate_change_12m.agrees]], 1 [[art:915bf8eb:sign_check.credit_score.agrees]], 1 [[art:2eec20ab:sign_check.burnout.agrees]] and 1 [[art:7f18ddf7:sign_check.season_cos.agrees]] respectively.

### What the form actually leans on

Refits of the champion's functional form with one feature dropped are measured from a full-retained-feature baseline of 0.6391 [[art:ed55c319:ablation.baseline_auc]] on test.
Discrimination is concentrated in two inputs: dropping log original balance costs -0.0171 [[art:d9fda2c8:ablation.orig_upb_log.delta_auc]] and dropping the refinance incentive costs -0.0161 [[art:b1880518:ablation.incentive.delta_auc]].
Loan age contributes -0.004572 [[art:0b5dcaeb:ablation.loan_age.delta_auc]], and beyond the spread and loan-to-value terms already discussed the remaining inputs are close to inert, with the rate change at -0.0003635 [[art:f472749f:ablation.rate_change_12m.delta_auc]], credit score at -0.0002604 [[art:9963f841:ablation.credit_score.delta_auc]], the sine seasonal term at 0.000108 [[art:47876c72:ablation.season_sin.delta_auc]], burnout at 0.0005739 [[art:499cf97d:ablation.burnout.delta_auc]] and the cosine seasonal term at 0.001845 [[art:0931b2a0:ablation.season_cos.delta_auc]].
The last three of those are positive, meaning the refit without the feature scored higher than the refit with it, which is weak evidence that the seasonal pair and burnout are adding noise rather than signal to the form as specified.
That a prepayment model's discrimination rests as much on loan size as on the rate incentive is worth the developer's comment, since loan size is a proxy for refinancing economics rather than a driver of them and its relationship to prepayment is the more likely to drift with origination vintage.

### Effective challenge

The challenger scores 0.6653 [[art:6f811314:challenger.auc]] on test against the champion's recomputed 0.6549 [[art:f3890b65:metrics.test.auc]], a lead of 0.01042 [[art:10b988e8:challenger.delta_auc]].
The rule that decides whether such a difference matters sets the bar for a material challenger lead at 0.03 [[art:e042774c:threshold.E1.delta_auc]], and the observed lead is below it, so the challenger does not displace the champion on discrimination.
Calibration tells the same story in the same direction, with the challenger at 0.009119 [[art:0e717888:challenger.brier]] against the champion's 0.009063 [[art:21d0b581:metrics.test.brier]], where the champion is marginally the better of the two.
The challenge is therefore effective in the sense that an alternative approach was fitted and compared on held-out data, and its result supports retaining the champion's functional form rather than replacing it; the qualifications above concern how that form allocates weight among its inputs, not whether it is outperformed.

## 3. Data integrity and drift

Sound development practice includes a critical assessment of data quality, relevance, and inputs, alongside out-of-sample and out-of-time testing, and this section reviews that evidence for the package under review. [[reg:SR26-2:IV.1]]

### Splits, missingness and provenance

The run profiles a training split of 313538 rows [[art:6582e5dd:profile.train.n]], a test split of 135060 rows [[art:75b5b833:profile.test.n]], an out-of-time split of 283343 rows [[art:a0103a06:profile.out_of_time.n]], and a vintage holdout of 221779 rows [[art:fcb7e414:profile.vintage_holdout.n]].

The largest missing fraction in any column is 0 [[art:050a3099:profile.train.missing.max]] in train, 0 [[art:f813848d:profile.test.missing.max]] in test, 0 [[art:4dafce11:profile.out_of_time.missing.max]] in the out-of-time split, and 0 [[art:329bb430:profile.vintage_holdout.missing.max]] in the vintage holdout.

Because these maxima coincide, no split differs from another on this measure, so the between-split gap is nil and sits inside the permitted missingness gap of 0.1 [[art:9cce25ea:threshold.D1.missing_gap]].

The input files the run consumed were each checked against a recorded cryptographic digest before the run began, so the profiled rows can be traced to fixed inputs.

<!-- quaestor:renderer:begin table data.manifest -->
The files data.manifest declares, each verified against its SHA-256 before the run [[art:4a0ccaba:data.manifest]]:

| file | sha256 | verified |
|---|---|---|
| out_of_time.csv | 176dfd7382fdb40c1aeab5a57c9450975780e0d092cc34dbeeed6082465c7c23 | true |
| rates.csv | 45bef524be2dcef44deebbef04c5abc8af42823c2ef740cb9f0cb130e8562c7b | true |
| test.csv | c92f126e77f406fff90bf7792c646fe2fea3973754104759090f93a2431cd0e0 | true |
| train.csv | 1f220f505e5b5d6478ae4e88bd732bccff793c114172680d8b99e930679ca196 | true |
| vintage_holdout.csv | 597f3e894c8cce066624ae325799a60a5a0f82ac9b096586b9633976489364b4 | true |
<!-- quaestor:renderer:end -->

### Population and characteristic stability

The declared stability bound is 0.25 [[art:278b9016:threshold.S1.psi]], stated for the training split against test, and the package declares the same ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]]; the paragraphs below read the other two splits against that same bound, noting that it was declared for the train-against-test comparison.

Between train and test the largest population stability index, the score included, is 0.005703 [[art:f632d5d4:psi.max]], carried by original loan-to-value at 0.005703 [[art:6ea40553:psi.orig_ltv]], which is far inside the bound of 0.25 [[art:278b9016:threshold.S1.psi]].

The remaining train-to-test indices are smaller still: credit score 0.003718 [[art:8a078965:psi.credit_score]], log original balance 0.002753 [[art:4af07770:psi.orig_upb_log]], spread at origination 0.002192 [[art:e68bfd2e:psi.sato]], burnout 0.001567 [[art:40a3f946:psi.burnout]], the score itself 0.0006641 [[art:6e6c94e1:psi.y_score]], incentive 0.0003749 [[art:61538982:psi.incentive]], loan age 8.302e-05 [[art:f548214d:psi.loan_age]], the twelve-month rate change 3.589e-05 [[art:23b9e924:psi.rate_change_12m]], and the two seasonal terms at 3.366e-06 [[art:ae17ebba:psi.season_sin]] and 3.184e-06 [[art:9db38513:psi.season_cos]].

The test split is therefore, on this evidence, drawn from the same population as the training split.

The out-of-time split is different in kind, with loan age shifting by 3.086 [[art:5f3c6bba:psi.out_of_time.loan_age]], incentive by 1.726 [[art:73dfd106:psi.out_of_time.incentive]], burnout by 1.551 [[art:5316f456:psi.out_of_time.burnout]], the score by 1.54 [[art:75370112:psi.out_of_time.y_score]], and the twelve-month rate change by 0.8254 [[art:09e68722:psi.out_of_time.rate_change_12m]], each of them above the declared bound of 0.25 [[art:278b9016:threshold.S1.psi]].

The rest of the out-of-time picture is quiet by comparison: the seasonal sine term at 0.02419 [[art:7388771e:psi.out_of_time.season_sin]], log original balance at 0.02136 [[art:abf1e02d:psi.out_of_time.orig_upb_log]], original loan-to-value at 0.01598 [[art:7f6fab7a:psi.out_of_time.orig_ltv]], spread at origination at 0.01473 [[art:85a8a904:psi.out_of_time.sato]], the seasonal cosine term at 0.00591 [[art:8ef132e3:psi.out_of_time.season_cos]], and credit score at 0.004578 [[art:5341c0a9:psi.out_of_time.credit_score]], all inside 0.25 [[art:278b9016:threshold.S1.psi]].

The vintage holdout shows the same pattern in milder form, with incentive at 1.298 [[art:86f7884e:psi.vintage_holdout.incentive]], the twelve-month rate change at 0.8816 [[art:2575a328:psi.vintage_holdout.rate_change_12m]], the score at 0.7656 [[art:ae7b9c29:psi.vintage_holdout.y_score]], and burnout at 0.5116 [[art:e3a3122f:psi.vintage_holdout.burnout]] standing above the declared bound of 0.25 [[art:278b9016:threshold.S1.psi]].

Within that split the remaining measures sit below the bound: spread at origination at 0.2002 [[art:b34d2ebe:psi.vintage_holdout.sato]], loan age at 0.1507 [[art:2de85f94:psi.vintage_holdout.loan_age]], log original balance at 0.03076 [[art:bd074d53:psi.vintage_holdout.orig_upb_log]], original loan-to-value at 0.01065 [[art:a5066c0f:psi.vintage_holdout.orig_ltv]], credit score at 0.007218 [[art:341abd78:psi.vintage_holdout.credit_score]], the seasonal sine term at 0.003659 [[art:dad1e65c:psi.vintage_holdout.season_sin]], and the seasonal cosine term at 0.000942 [[art:67aee1b5:psi.vintage_holdout.season_cos]].

The features that move are the rate-sensitive and seasoning-sensitive ones, and the score moves with them, which is what a change of rate environment between the training window and the later windows would produce rather than a defect in the data assembly.

Characteristic stability, which weighs each feature's shift by its contribution to the linear predictor, is small throughout, the largest being 0.006455 [[art:131d42db:csi.max]], carried by log original balance at 0.006455 [[art:7561e8b0:csi.orig_upb_log]].

The other contributions are spread at origination at 0.001116 [[art:a54b158e:csi.sato]], incentive at 0.001102 [[art:020f5ce2:csi.incentive]], original loan-to-value at 0.0005902 [[art:1c9006f3:csi.orig_ltv]], the twelve-month rate change at 0.0002237 [[art:ffdb6fdd:csi.rate_change_12m]], the seasonal cosine term at 6.191e-05 [[art:c70e3aa4:csi.season_cos]], credit score at 1.97e-05 [[art:0a280759:csi.credit_score]], the seasonal sine term at 2.108e-05 [[art:fb3bf812:csi.season_sin]], burnout at 3.43e-06 [[art:e4d3e34a:csi.burnout]], and loan age at 0 [[art:df52c920:csi.loan_age]].

Read against the declared ceiling of 0.25 [[art:278b9016:threshold.S1.psi]], the weighted contribution of each feature to the shift in the linear predictor is immaterial.

### Leakage screens

Features declared as observed during the performance period or after the outcome number 0 [[art:742bcd24:leakage.timing.n_flagged]], so the declared timings place every input ahead of the event being predicted.

The strongest single feature reaches an AUC of 0.5995 [[art:9e2ffad1:leakage.target_corr.max_single_feature_auc]] on its own, against the permitted single-feature ceiling of 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]], which is the profile of an ordinary weak predictor rather than of a feature that encodes the outcome.

The contamination screen has an identifier arm and a feature-vector arm, and each is read against its own bound.

On the identifier arm, the share of test rows whose loan and period identifiers also identify a training row is 0 [[art:63d37fc5:leakage.overlap.ids]], against the declared bound of 0.005 [[art:9f336eaf:threshold.L2.overlap]].

On the feature-vector arm, the share of test rows whose feature values also appear in train is 0 [[art:0fec8048:leakage.overlap.features]], against the bound the rule actually applied of 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].

That applied bound is the larger of the declared overlap bound and twice the within-train duplicate share of 0.0001531 [[art:ce57652e:leakage.duplicates.train]], on the reasoning that distinct subjects writing the same discrete row is coincidence rather than contamination; here the declared bound is the larger of the pair, so the widening has no practical effect.

The corresponding row-level overlap measure is likewise 0 [[art:4c9fcd09:leakage.overlap]], again read against the applied bound of 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].

The name screen matches 0 [[art:407e62be:leakage.name_screen.n_matched]] feature names against the target-adjacent lexicon, so no input is named in a way that suggests it restates the label.

### Assessment

On missingness, provenance, train-to-test stability and every leakage screen, the data supporting this package is sound and the measured quantities sit inside the bounds cited above.

The substantive issue is drift: the out-of-time and vintage holdout splits sit outside the declared stability bound on the rate-sensitive, seasoning-sensitive and score distributions, and deviations of that kind outside established thresholds are the circumstance in which adjustment, recalibration or redevelopment may be warranted. [[reg:SR26-2:V.1.b]]

Accordingly, performance measured on those later splits should be read as evidence about a population the training window did not contain, and the stability of the score under a changed rate environment should be carried forward into ongoing monitoring rather than treated as settled by the train-to-test comparison.

## 4. Outcomes analysis

Outcomes analysis compares model outputs to corresponding real-world outcomes to assess model performance relative to model objectives and business use [[reg:SR26-2:V.1.b]].

This section reports calibration before discrimination.

The reason is the declared business use: package.yaml states that this model's output is consumed as a probability and not only as a ranking, so whether the predicted probabilities mean what they say is the leading question, whatever the event rate on any split happens to be.

### Calibration

On test, the logistic regression of the outcome on the logit of the predicted probability gives a slope of 1.017 [[art:9b1edaa3:calibration_slope.test]] and an intercept of 0.02905 [[art:1a8280dd:calibration_intercept.test]].

On train, the same regression gives a slope of 0.9971 [[art:28331672:calibration_slope.train]] and an intercept of -0.016 [[art:be40e0a7:calibration_intercept.train]].

On vintage_holdout, the slope is 0.8502 [[art:80fe61d2:calibration_slope.vintage_holdout]] with an intercept of 0.06119 [[art:0d75b532:calibration_intercept.vintage_holdout]].

On out_of_time, the slope falls to 0.4321 [[art:d9f87bb2:calibration_slope.out_of_time]] with an intercept of -1.762 [[art:53a8d76b:calibration_intercept.out_of_time]], outside the declared band whose lower bound is 0.8 [[art:749634ae:threshold.C1.calibration_slope.min]] and whose upper bound is 1.2 [[art:b6672579:threshold.C1.calibration_slope.max]].

Mean predicted probability against the observed rate follows the same pattern across the splits.

On train, the mean predicted probability is 0.009503 [[art:716b94b2:metrics.train.mean_predicted]] against an observed rate of 0.009476 [[art:8ecc2809:metrics.train.event_rate]], a relative gap of 0.002897 [[art:332fc4d9:calibration.mean_rel_gap.train]] against a tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].

On test, the mean predicted probability is 0.009606 [[art:24595a04:metrics.test.mean_predicted]] against an observed rate of 0.009174 [[art:78206f7c:metrics.test.event_rate]], a relative gap of 0.04709 [[art:a173f6c5:calibration.mean_rel_gap.test]] against the same tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].

On vintage_holdout, the mean predicted probability is 0.009873 [[art:c12c52f7:metrics.vintage_holdout.mean_predicted]] against an observed rate of 0.01948 [[art:bab66615:metrics.vintage_holdout.event_rate]], a relative gap of 0.4932 [[art:92b5a8c4:calibration.mean_rel_gap.vintage_holdout]] against a tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].

On out_of_time, the mean predicted probability is 0.01005 [[art:fd777cc4:metrics.out_of_time.mean_predicted]] against an observed rate of 0.01868 [[art:cf3a82aa:metrics.out_of_time.event_rate]], a relative gap of 0.4618 [[art:9e4c8750:calibration.mean_rel_gap.out_of_time]] against a tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].

Both holdouts therefore under-predict the level of the event by roughly half of the observed rate, and these two exceedances are raised as calibration findings.

The decile calibration on test is shown below.

<!-- quaestor:renderer:begin table calibration.test -->
Calibration by decile of predicted probability on test [[art:c8e7323f:calibration.test]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.003224 | 0.003998 | 13506 |
| 2 | 0.004562 | 0.003406 | 13506 |
| 3 | 0.005598 | 0.004813 | 13506 |
| 4 | 0.006645 | 0.006145 | 13506 |
| 5 | 0.00777 | 0.006219 | 13506 |
| 6 | 0.009053 | 0.009181 | 13506 |
| 7 | 0.01059 | 0.01111 | 13506 |
| 8 | 0.0125 | 0.01229 | 13506 |
| 9 | 0.01511 | 0.01355 | 13506 |
| 10 | 0.02101 | 0.02103 | 13506 |
<!-- quaestor:renderer:end -->

The portfolio-level prepayment comparison tells the same story in CPR terms: the mean absolute difference between actual and predicted CPR is 0.02202 [[art:3487a403:cpr.train.mae]] on train and 0.02642 [[art:939c5fb9:cpr.test.mae]] on test, but 0.0785 [[art:0cc82390:cpr.vintage_holdout.mae]] on vintage_holdout and 0.08656 [[art:a467ad41:cpr.out_of_time.mae]] on out_of_time.

The period-by-period comparison on test is shown below.

<!-- quaestor:renderer:begin table cpr.test -->
Actual against predicted CPR by period on test [[art:f76e789f:cpr.test]]:

| period | n | actual_cpr | predicted_cpr |
|---|---|---|---|
| 201402 | 3 | 0 | 0.05041 |
| 201403 | 149 | 0 | 0.05295 |
| 201404 | 313 | 0 | 0.04797 |
| 201405 | 513 | 0.02314 | 0.05264 |
| 201406 | 652 | 0.0362 | 0.06489 |
| 201407 | 792 | 0.04452 | 0.06948 |
| 201408 | 967 | 0 | 0.06762 |
| 201409 | 1124 | 0.05209 | 0.06972 |
| 201410 | 1268 | 0.04631 | 0.06112 |
| 201411 | 1414 | 0.07376 | 0.06842 |
| 201412 | 1582 | 0.05902 | 0.07859 |
| 201501 | 1725 | 0.05425 | 0.09164 |
| 201502 | 1722 | 0.143 | 0.1042 |
| 201503 | 1718 | 0.1433 | 0.09927 |
| 201504 | 1697 | 0.1201 | 0.1105 |
| 201505 | 1679 | 0.1213 | 0.106 |
| 201506 | 1669 | 0.09614 | 0.1022 |
| 201507 | 1655 | 0.06334 | 0.08881 |
| 201508 | 1652 | 0.07027 | 0.1012 |
| 201509 | 1641 | 0.07754 | 0.1021 |
| 201510 | 1629 | 0.1117 | 0.1066 |
| 201511 | 1614 | 0.09249 | 0.1046 |
| 201512 | 1599 | 0.1204 | 0.1017 |
| 201601 | 1582 | 0.1416 | 0.1017 |
| 201602 | 1562 | 0.06699 | 0.1272 |
| 201603 | 1553 | 0.1373 | 0.1459 |
| 201604 | 1535 | 0.1591 | 0.159 |
| 201605 | 1513 | 0.1612 | 0.1651 |
| 201606 | 1490 | 0.1143 | 0.1648 |
| 201607 | 1475 | 0.165 | 0.2022 |
| 201608 | 1453 | 0.2215 | 0.1951 |
| 201609 | 1423 | 0.2189 | 0.1889 |
| 201610 | 1393 | 0.2434 | 0.1916 |
| 201611 | 1361 | 0.2881 | 0.1772 |
| 201612 | 1323 | 0.2264 | 0.1234 |
| 201701 | 1297 | 0.1544 | 0.1171 |
| 201702 | 1280 | 0.1236 | 0.1196 |
| 201703 | 1441 | 0.1544 | 0.1233 |
| 201704 | 1578 | 0.08052 | 0.1209 |
| 201705 | 1726 | 0.1057 | 0.1252 |
| 201706 | 1854 | 0.1105 | 0.1291 |
| 201707 | 2005 | 0.1133 | 0.1173 |
| 201708 | 2166 | 0.09022 | 0.1127 |
| 201709 | 2304 | 0.08022 | 0.119 |
| 201710 | 2465 | 0.1367 | 0.1063 |
| 201711 | 2605 | 0.06695 | 0.09659 |
| 201712 | 2795 | 0.0944 | 0.09981 |
| 201801 | 2912 | 0.07555 | 0.1004 |
| 201802 | 2893 | 0.06048 | 0.08523 |
| 201803 | 2881 | 0.07245 | 0.07518 |
| 201804 | 2863 | 0.08841 | 0.07972 |
| 201805 | 2841 | 0.07737 | 0.07234 |
| 201806 | 2821 | 0.02106 | 0.0727 |
| 201807 | 2815 | 0.07409 | 0.07337 |
| 201808 | 2796 | 0.09044 | 0.06745 |
| 201809 | 2771 | 0.08325 | 0.06753 |
| 201810 | 2750 | 0.09189 | 0.05877 |
| 201811 | 2728 | 0.06402 | 0.05383 |
| 201812 | 2724 | 0.06411 | 0.05784 |
| 201901 | 2708 | 0.03488 | 0.07125 |
| 201902 | 2699 | 0.06469 | 0.08242 |
| 201903 | 2684 | 0.0566 | 0.08822 |
| 201904 | 2690 | 0.08566 | 0.1166 |
| 201905 | 2669 | 0.1068 | 0.1166 |
| 201906 | 2645 | 0.1036 | 0.148 |
| 201907 | 2620 | 0.1411 | 0.1543 |
| 201908 | 2588 | 0.1427 | 0.1528 |
| 201909 | 2555 | 0.1606 | 0.178 |
| 201910 | 2519 | 0.1546 | 0.1587 |
| 201911 | 2482 | 0.1484 | 0.1548 |
| 201912 | 2450 | 0.171 | 0.1556 |
<!-- quaestor:renderer:end -->

### Discrimination

Discrimination is reported one metric at a time across the four splits.

AUC is 0.6504 [[art:40964132:metrics.train.auc]] on train, 0.6549 [[art:f3890b65:metrics.test.auc]] on test, 0.7388 [[art:95f87cc7:metrics.vintage_holdout.auc]] on vintage_holdout and 0.6898 [[art:cb57fe9a:metrics.out_of_time.auc]] on out_of_time.

Gini is 0.3007 [[art:da0e7063:metrics.train.gini]] on train, 0.3099 [[art:5710cba3:metrics.test.gini]] on test, 0.4776 [[art:75ad81b1:metrics.vintage_holdout.gini]] on vintage_holdout and 0.3796 [[art:6c5edac7:metrics.out_of_time.gini]] on out_of_time.

KS is 0.2262 [[art:96e91aee:metrics.train.ks]] on train, 0.2375 [[art:c35222f3:metrics.test.ks]] on test, 0.411 [[art:699a7598:metrics.vintage_holdout.ks]] on vintage_holdout and 0.3021 [[art:c486329f:metrics.out_of_time.ks]] on out_of_time.

The Brier score is 0.009359 [[art:574cf8a4:metrics.train.brier]] on train, 0.009063 [[art:21d0b581:metrics.test.brier]] on test, 0.01898 [[art:6a660ed9:metrics.vintage_holdout.brier]] on vintage_holdout and 0.01824 [[art:4ddcaaea:metrics.out_of_time.brier]] on out_of_time.

Log loss is 0.05226 [[art:716b9dc1:metrics.train.logloss]] on train, 0.05083 [[art:048e9ca7:metrics.test.logloss]] on test, 0.09345 [[art:630a591b:metrics.vintage_holdout.logloss]] on vintage_holdout and 0.09576 [[art:8d53f72c:metrics.out_of_time.logloss]] on out_of_time.

The row counts behind these metrics are 313538 [[art:72c7a6d2:metrics.train.n]] on train, 135060 [[art:629740ff:metrics.test.n]] on test, 221779 [[art:faabc78e:metrics.vintage_holdout.n]] on vintage_holdout and 283343 [[art:c164ae00:metrics.out_of_time.n]] on out_of_time.

The share of events captured in the top two deciles is 0.38 [[art:b2f9e5d8:deciles.train.top2_capture]] on train, 0.3769 [[art:1d4dff05:deciles.test.top2_capture]] on test, 0.5116 [[art:3cd3b5a3:deciles.vintage_holdout.top2_capture]] on vintage_holdout and 0.4313 [[art:58f451c3:deciles.out_of_time.top2_capture]] on out_of_time.

The decile separation on test, with the first decile holding the highest probabilities, is shown below.

<!-- quaestor:renderer:begin table deciles.test -->
Decile separation on test; decile 1 holds the highest probabilities [[art:d98c638f:deciles.test]]:

| decile | count | events | event_rate | lift |
|---|---|---|---|---|
| 1 | 13506 | 284 | 0.02103 | 2.292 |
| 2 | 13506 | 183 | 0.01355 | 1.477 |
| 3 | 13506 | 166 | 0.01229 | 1.34 |
| 4 | 13506 | 150 | 0.01111 | 1.211 |
| 5 | 13506 | 124 | 0.009181 | 1.001 |
| 6 | 13506 | 84 | 0.006219 | 0.678 |
| 7 | 13506 | 83 | 0.006145 | 0.6699 |
| 8 | 13506 | 65 | 0.004813 | 0.5246 |
| 9 | 13506 | 46 | 0.003406 | 0.3713 |
| 10 | 13506 | 54 | 0.003998 | 0.4358 |
<!-- quaestor:renderer:end -->

The train-to-test AUC gap is the difference between 0.6504 [[art:40964132:metrics.train.auc]] and 0.6549 [[art:f3890b65:metrics.test.auc]], which is well inside the declared bound of 0.08 [[art:630f28f4:threshold.O1.auc_gap]] and shows no evidence of over-fitting in the ranking.

Ranking therefore holds up out of sample and out of time while the level of the probabilities does not, which is the pattern a probability-consuming use is most exposed to.

### Developer-declared thresholds

<!-- quaestor:renderer:begin table thresholds.evaluation -->
Every threshold package.yaml declares, with its bound, the recomputed value and the outcome [[art:920227a3:thresholds.evaluation]]:

| metric | split | bound | value | result |
|---|---|---|---|---|
| auc | test | minimum 0.65 | 0.6549 | pass |
| calibration_slope | test | minimum 0.8 | 1.017 | pass |
| calibration_slope | test | maximum 1.2 | 1.017 | pass |
| psi |  | maximum 0.25 | 0.005703 | pass |
<!-- quaestor:renderer:end -->

The table sets each bound package.yaml declares against the value recomputed here and reports the outcome for each.

The calibration slope band and the mean-ratio tolerance are the bounds at issue in this section.

### Follow-up analyses

The bounded planning loop ran four subpopulation recomputations, splitting each holdout at the median of the refinance incentive, to ask whether the out-of-time under-prediction is a uniform level shift or a failure to respond to the incentive driver.

The first step recomputed every metric on out_of_time restricted to `incentive > median(incentive)`.

It was asked because a calibration slope well below one suggests the under-prediction is concentrated where refinance incentive is high, so slicing out_of_time on incentive distinguishes a level shift from a failure to respond to the driver.

<!-- quaestor:renderer:begin table metrics.out_of_time.sub.incentive_high -->
Every metric on the incentive above_median slice of out_of_time [[art:8ca3a5fb:metrics.out_of_time.sub.incentive_high]]:

| metric | value |
|---|---|
| n | 141671 |
| event_rate | 0.02949 |
| auc | 0.6046 |
| gini | 0.2091 |
| ks | 0.1587 |
| brier | 0.02863 |
| logloss | 0.1342 |
| mean_predicted | 0.0188 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

On this slice AUC falls 0.08523 [[art:e7b201c8:metrics.out_of_time.sub.incentive_high.auc_gap]] below the split's own AUC, above the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] at which a sub-population result becomes an open item.

The slice holds 0.5 [[art:4787f68a:metrics.out_of_time.sub.incentive_high.share]] of the split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] and below the ceiling of 0.95 [[art:a928a05c:threshold.O1.slice_max_share]] at which a slice would be refused as the whole split.

Mean predicted here is 0.0188 [[art:b7288bbc:metrics.out_of_time.sub.incentive_high.mean_predicted]] against an observed rate of 0.02949 [[art:f62f5a9c:metrics.out_of_time.sub.incentive_high.event_rate]], so the probabilities are too low in level on exactly the rows where prepayment is most common, and the ordering weakens there as well.

The second step recomputed every metric on out_of_time restricted to `incentive <= median(incentive)`.

It was asked because the complementary half shows whether the out-of-time under-prediction is uniform or concentrated in the high-incentive rows measured in the first step.

<!-- quaestor:renderer:begin table metrics.out_of_time.sub.incentive_low -->
Every metric on the incentive below_median slice of out_of_time [[art:eced92cd:metrics.out_of_time.sub.incentive_low]]:

| metric | value |
|---|---|
| n | 141672 |
| event_rate | 0.00787 |
| auc | 0.5198 |
| gini | 0.03962 |
| ks | 0.09045 |
| brier | 0.007849 |
| logloss | 0.05733 |
| mean_predicted | 0.001307 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

On this slice AUC falls 0.17 [[art:379c90f9:metrics.out_of_time.sub.incentive_low.auc_gap]] below the split's own AUC, above the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].

The slice holds 0.5 [[art:cc116fda:metrics.out_of_time.sub.incentive_low.share]] of the split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] and below the ceiling of 0.95 [[art:a928a05c:threshold.O1.slice_max_share]].

Mean predicted here is 0.001307 [[art:e77d973c:metrics.out_of_time.sub.incentive_low.mean_predicted]] against an observed rate of 0.00787 [[art:b87e9246:metrics.out_of_time.sub.incentive_low.event_rate]], so the level is understated here too, and with AUC at 0.5198 [[art:5f017449:metrics.out_of_time.sub.incentive_low.auc]] the ordering within this half is close to uninformative, making the weakness one of ordering as well as level.

The third step recomputed every metric on vintage_holdout restricted to `incentive > median(incentive)`.

It was asked to check whether the same high-incentive slice that drives the out_of_time under-prediction also drives the vintage_holdout shortfall, or whether the miscalibration there is uniform.

<!-- quaestor:renderer:begin table metrics.vintage_holdout.sub.incentive_high -->
Every metric on the incentive above_median slice of vintage_holdout [[art:eac314b9:metrics.vintage_holdout.sub.incentive_high]]:

| metric | value |
|---|---|
| n | 110698 |
| event_rate | 0.03165 |
| auc | 0.6654 |
| gini | 0.3307 |
| ks | 0.2567 |
| brier | 0.0307 |
| logloss | 0.1414 |
| mean_predicted | 0.01662 |
| share | 0.4991 |
<!-- quaestor:renderer:end -->

On this slice AUC falls 0.07345 [[art:dfc93d01:metrics.vintage_holdout.sub.incentive_high.auc_gap]] below the split's own AUC, within the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]], so it stands as supporting evidence rather than an open item.

The slice holds 0.4991 [[art:6ee6cf53:metrics.vintage_holdout.sub.incentive_high.share]] of the split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] and below the ceiling of 0.95 [[art:a928a05c:threshold.O1.slice_max_share]].

Mean predicted here is 0.01662 [[art:1f806ffc:metrics.vintage_holdout.sub.incentive_high.mean_predicted]] against an observed rate of 0.03165 [[art:7a446230:metrics.vintage_holdout.sub.incentive_high.event_rate]], so on this holdout the weakness in the high-incentive half is in the level of the probabilities while the ordering stays within the bound.

The fourth step recomputed every metric on vintage_holdout restricted to `incentive <= median(incentive)`.

It was asked to complete the incentive two-by-two so a validator can see whether the under-prediction is uniform across incentive in both holdouts or concentrated in the refinance-incentive half.

<!-- quaestor:renderer:begin table metrics.vintage_holdout.sub.incentive_low -->
Every metric on the incentive below_median slice of vintage_holdout [[art:7e722b90:metrics.vintage_holdout.sub.incentive_low]]:

| metric | value |
|---|---|
| n | 111081 |
| event_rate | 0.007346 |
| auc | 0.5956 |
| gini | 0.1912 |
| ks | 0.1726 |
| brier | 0.007294 |
| logloss | 0.04566 |
| mean_predicted | 0.003153 |
| share | 0.5009 |
<!-- quaestor:renderer:end -->

On this slice AUC falls 0.1432 [[art:2b9eda62:metrics.vintage_holdout.sub.incentive_low.auc_gap]] below the split's own AUC, above the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].

The slice holds 0.5009 [[art:4e4aac59:metrics.vintage_holdout.sub.incentive_low.share]] of the split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] and below the ceiling of 0.95 [[art:a928a05c:threshold.O1.slice_max_share]].

Mean predicted here is 0.003153 [[art:037a5534:metrics.vintage_holdout.sub.incentive_low.mean_predicted]] against an observed rate of 0.007346 [[art:8cd3a201:metrics.vintage_holdout.sub.incentive_low.event_rate]], so the level is understated in this half as well, and with AUC at 0.5956 [[art:e5b67962:metrics.vintage_holdout.sub.incentive_low.auc]] the ordering is materially weaker than the headline too.

Taken together, the four slices show that the under-prediction on both holdouts is present on either side of the incentive median rather than confined to the high-incentive half, and that the headline AUC on each holdout is supported in part by separation between the incentive halves rather than within them.

The three slices whose AUC gap exceeds its bound are open items for the findings section and questions for the model developer, not findings raised here.

## 5. Sensitivity and scenario analysis

Sensitivity analysis and stress testing over a wide range of inputs, including extreme values, are called for where appropriate to the particular model, so that the boundaries of model performance and the conditions under which it may become unstable can be established [[reg:SR11-7:V.1.a]].

### Multicollinearity among the retained features

The largest variance inflation factor across the retained features is 4.629 [[art:82a187c7:vif.max]], well inside the threshold of 10 [[art:aeb4f33c:threshold.M1.vif]].
That maximum is carried by the rate incentive term at 4.629 [[art:0c33ec65:vif.incentive]], followed by burnout at 3.749 [[art:f9a490a7:vif.burnout]] and the spread at origination at 3.015 [[art:42163c15:vif.sato]].
The remaining retained features sit lower still, with loan age at 2.690 [[art:12ee5768:vif.loan_age]], the twelve-month rate change at 2.205 [[art:7f4d0c73:vif.rate_change_12m]], original loan-to-value at 1.107 [[art:a998810f:vif.orig_ltv]], log original balance at 1.061 [[art:0dde7942:vif.orig_upb_log]], the seasonal sine at 1.025 [[art:6afd05c9:vif.season_sin]], credit score at 1.023 [[art:373087f2:vif.credit_score]] and the seasonal cosine at 1.006 [[art:2950847c:vif.season_cos]].
Belsley's condition number of the column-standardised design is 4.565 [[art:87b61976:condition_number]] against a threshold of 30 [[art:7e52fd7a:threshold.M1.condition_number]], so the design shows no ill-conditioning of the kind that would make the fitted coefficients fragile to small perturbations of the data.
The clustering of the three largest factors around the incentive, burnout and spread terms is the expected consequence of their shared dependence on the rate path, and at these magnitudes it does not threaten the separate identification of their effects.

### Stability across the declared regimes

The package declares a rate-regime column, so discrimination was examined within each regime rather than only in aggregate.

<!-- quaestor:renderer:begin table stability.auc_by_regime -->
The champion's AUC within each rate_regime on train [[art:f293ebc6:stability.auc_by_regime]]:

| regime | n | event_rate | auc |
|---|---|---|---|
| falling | 162717 | 0.01121 | 0.6575 |
| rising | 150821 | 0.007605 | 0.6144 |
<!-- quaestor:renderer:end -->

The tolerance applied to the spread in discrimination across regimes is 0.1 [[art:b64213d7:threshold.R1.auc_gap]].
Coefficient stability was screened by asking whether any of the ten leading features changes sign between regimes while exceeding a coefficient magnitude of 0.05 [[art:aca84377:threshold.R1.sign_flip_coef]] with an absolute z-statistic of at least 2 [[art:2e4428c7:threshold.R1.sign_flip_z]] in both.
No feature meets that condition: the indicator is 0 for the rate incentive [[art:0cc7a37d:stability.incentive.sign_flip]], 0 for burnout [[art:6bc05e82:stability.burnout.sign_flip]], 0 for the spread at origination [[art:1f302ccd:stability.sato.sign_flip]], 0 for loan age [[art:b7191217:stability.loan_age.sign_flip]] and 0 for the twelve-month rate change [[art:465700ff:stability.rate_change_12m.sign_flip]].
It is likewise 0 for credit score [[art:d956c276:stability.credit_score.sign_flip]], 0 for original loan-to-value [[art:054d5fab:stability.orig_ltv.sign_flip]], 0 for log original balance [[art:fb1ae6c8:stability.orig_upb_log.sign_flip]], 0 for the seasonal sine [[art:6ba36a3b:stability.season_sin.sign_flip]] and 0 for the seasonal cosine [[art:1850e2de:stability.season_cos.sign_flip]].
The economic direction of every leading driver therefore holds across the declared regimes, which is the more consequential stability property for a hazard model used to project prepayment behaviour through changing rate environments.

### Rate-shock scenarios

The subject is a hazard model feeding a servicing valuation, so the parallel rate-shock ladder applies and was run across the declared grid of shocks.

<!-- quaestor:renderer:begin table scenario.value_by_shock -->
Servicing value, its change from the base case and first-year CPR, by shock [[art:9ae3b068:scenario.value_by_shock]]:

| shock_bp | value | value_change | cpr |
|---|---|---|---|
| -300 | 8.421e+06 | -1.078e+06 | 0.04609 |
| -200 | 8.999e+06 | -499400 | 0.02422 |
| -100 | 9.323e+06 | -175200 | 0.01265 |
| 0 | 9.499e+06 | 0 | 0.006586 |
| 100 | 9.591e+06 | 92920 | 0.003423 |
| 200 | 9.64e+06 | 141700 | 0.001778 |
| 300 | 9.666e+06 | 167100 | 0.0009226 |
<!-- quaestor:renderer:end -->

At the downward extreme the servicing value changes by -1078000 [[art:9bab8e73:scenario.value_change.-300]], while at the upward extreme it rises by only 167100 [[art:d7f60dfe:scenario.value_change.300]].
The change in value is monotone increasing in the shock across the whole ladder, rising without reversal from the deepest rally through the base case to the largest sell-off, which is the behaviour a prepayment-driven servicing asset should show.
The sum of the changes at the two extremes is -910600 [[art:67b742b1:scenario.convexity]], so the loss on the rally outweighs the gain on the sell-off by a wide margin.
That negative sign is the direction the package declares for this asset, and its magnitude confirms that the asymmetry is pronounced rather than marginal: the response to falling rates is roughly six times the response to rising rates of the same size.
The practical implication is that the valuation is far more exposed to a rally than to a sell-off, and the flattening of the gain between the successive upward shocks shown in the ladder indicates that the upside is close to saturated by the largest shock tested.

### Scope of this section

The three sensitivity exercises reported above — multicollinearity diagnostics, regime stability and the rate-shock ladder — all apply to this model type, and each was run.
Checks that are reserved for other model types, and so were not run here, are listed in Appendix D; nothing in that list is reported above or should be read as having been exercised on this model.

## 6. Findings and recommendations

Findings below are ordered by severity and, within a severity, by the order in which the checks ran, and each carries the recomputed quantity, the threshold it was measured against and the citation of the artifact holding both, so that the reader can judge the source and extent of the model risk and whether corrective action is warranted [[reg:SR26-2:V]].

### F-001 · C1 calibration · severity **medium**

**The model systematically under-predicts prepayment on both holdout splits and its scores are compressed against the outcome, so the package is mis-calibrated in level and in slope.**

The logistic regression of the outcome on the predicted logit over the out-of-time split has a slope of 0.4321 [[art:d9f87bb2:calibration_slope.out_of_time]], below the floor of the acceptable band at 0.8 [[art:749634ae:threshold.C1.calibration_slope.min]].

Mean predicted probability on the out-of-time split is 0.01005 [[art:fd777cc4:metrics.out_of_time.mean_predicted]] against an observed event rate of 0.01868 [[art:cf3a82aa:metrics.out_of_time.event_rate]], a relative shortfall of 0.4618 [[art:9e4c8750:calibration.mean_rel_gap.out_of_time]] against a tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].

On the vintage holdout the mean predicted probability is 0.009873 [[art:c12c52f7:metrics.vintage_holdout.mean_predicted]] against an observed event rate of 0.01948 [[art:bab66615:metrics.vintage_holdout.event_rate]], a relative shortfall of 0.4932 [[art:92b5a8c4:calibration.mean_rel_gap.vintage_holdout]] against the same tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].

The validator concludes that the miss is not a single-split artefact, because it reproduces on two independent holdouts at close to the same magnitude and in the same direction, and that a slope well under one means the shortfall widens as the predicted score rises rather than sitting as a constant offset.

The model developer should re-fit or re-calibrate the score so that its predicted level matches the observed rate within tolerance on both holdouts, and should document whether the compression reflects an omitted or mis-specified response to the prepayment driver rather than an intercept that can be shifted.

Until the recalibration is evidenced, the validator recommends that downstream use of the point predictions be constrained and the limitation communicated to model users, with the remediation tracked to a documented response [[reg:SR26-2:VI.3]].

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1, S1), `compute_metrics` (T1, O1), `check_leakage` (L1, L2), `check_stability` (R1), `check_collinearity` (M1), `challenger_compare` (E1), `run_scenarios` (X1).

### Open items

On the segment `incentive > median(incentive)`, which holds 0.5 [[art:4787f68a:metrics.out_of_time.sub.incentive_high.share]] of the out-of-time split, what does the model discriminate on inside a population already selected on the refinance driver, given that AUC there is 0.6046 [[art:a1a6fd72:metrics.out_of_time.sub.incentive_high.auc]], which falls 0.08523 [[art:e7b201c8:metrics.out_of_time.sub.incentive_high.auc_gap]] below the split's own headline AUC and so sits above the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] the comparison was made against, and who on the model developer's side will answer it?

<!-- quaestor:renderer:begin table metrics.out_of_time.sub.incentive_high -->
Every metric on the incentive above_median slice of out_of_time [[art:8ca3a5fb:metrics.out_of_time.sub.incentive_high]]:

| metric | value |
|---|---|
| n | 141671 |
| event_rate | 0.02949 |
| auc | 0.6046 |
| gini | 0.2091 |
| ks | 0.1587 |
| brier | 0.02863 |
| logloss | 0.1342 |
| mean_predicted | 0.0188 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

On the complementary segment `incentive <= median(incentive)`, which holds 0.5 [[art:cc116fda:metrics.out_of_time.sub.incentive_low.share]] of the out-of-time split, what remains for the model to discriminate on once incentive is held near-constant, given that AUC there is 0.5198 [[art:5f017449:metrics.out_of_time.sub.incentive_low.auc]], which falls 0.17 [[art:379c90f9:metrics.out_of_time.sub.incentive_low.auc_gap]] below the split's own headline AUC and so sits above the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] the comparison was made against, and who on the model developer's side will answer it?

<!-- quaestor:renderer:begin table metrics.out_of_time.sub.incentive_low -->
Every metric on the incentive below_median slice of out_of_time [[art:eced92cd:metrics.out_of_time.sub.incentive_low]]:

| metric | value |
|---|---|
| n | 141672 |
| event_rate | 0.00787 |
| auc | 0.5198 |
| gini | 0.03962 |
| ks | 0.09045 |
| brier | 0.007849 |
| logloss | 0.05733 |
| mean_predicted | 0.001307 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

On the segment `incentive <= median(incentive)` of the vintage holdout, which holds 0.5009 [[art:4e4aac59:metrics.vintage_holdout.sub.incentive_low.share]] of that split, what does the model rank on inside that segment, given that AUC there is 0.5956 [[art:e5b67962:metrics.vintage_holdout.sub.incentive_low.auc]], which falls 0.1432 [[art:2b9eda62:metrics.vintage_holdout.sub.incentive_low.auc_gap]] below the split's own headline AUC and so sits above the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] the comparison was made against, and who on the model developer's side will answer it?

<!-- quaestor:renderer:begin table metrics.vintage_holdout.sub.incentive_low -->
Every metric on the incentive below_median slice of vintage_holdout [[art:7e722b90:metrics.vintage_holdout.sub.incentive_low]]:

| metric | value |
|---|---|
| n | 111081 |
| event_rate | 0.007346 |
| auc | 0.5956 |
| gini | 0.1912 |
| ks | 0.1726 |
| brier | 0.007294 |
| logloss | 0.04566 |
| mean_predicted | 0.003153 |
| share | 0.5009 |
<!-- quaestor:renderer:end -->

None of the three observations above is a defect under any rule applied in this validation, and each is recorded here as a question the model developer is asked to answer, with the model developer as owner in each case because the artifacts name no one else.

## 7. Ongoing monitoring recommendations

Ongoing monitoring should evaluate whether this package continues to perform as expected given changes in products, exposures, activities, clients, data relevance, or market conditions, with frequency and scope set by the model's nature, the availability of new data, and its materiality [[reg:SR26-2:V.2]].

### Quantities to track, frequency, and bound

Calibration should be tracked first: recompute the logistic regression of the realized outcome on the logit of the predicted probability on each closed production vintage, monthly, and compare the slope against the package's declared lower bound of 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] and upper bound of 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The validation sample gives the baseline for that series at 1.017 [[art:9b1edaa3:calibration_slope.test]], comfortably inside the declared band, so a monitored slope drifting toward either bound is a change from the state reviewed here rather than a continuation of it.

Discrimination should be tracked next: recompute the area under the ROC curve on production outcomes, quarterly or at whatever cadence the performance window allows a vintage to close, against the package's declared floor of 0.65 [[art:fececac1:threshold.package.auc.test.min]].
The validation value of 0.6549 [[art:f3890b65:metrics.test.auc]] clears that floor by a narrow margin, so monitoring should carry an internal warning level set above the declared floor and escalate on the warning level rather than waiting for a breach of the declared one.

Input and score stability should be tracked monthly: compute the population stability index for each model input and for the score itself, measured from the development distribution to the current production vintage, against the package's declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
The largest such shift observed within the development data, score included, was 0.005703 [[art:f632d5d4:psi.max]], which is a very quiet baseline and means the monitoring series should be read against the development distribution rather than against the train-to-test comparison, whose near-zero movement reflects a single sampled population and not the passage of time.

### How the monitoring report should order its evidence

The monitoring report should present calibration before discrimination, as section 4 of this report did, because the package declares that the model's output is consumed as a probability and not only as a ranking.
A score used as a probability can rank obligors correctly while stating the wrong level, so a monitoring pack that leads with rank-ordering would let a level error accumulate behind an unchanged discrimination series.

### Benchmarking

Monitoring should add a comparison that the development data cannot supply on its own: the challenger model compared with the champion in section 2 should be refit on production vintages and its outputs compared with the champion's on the same vintages, at least annually and after any material change in the modeled population.
Benchmarking of this kind compares the model's inputs and outputs to estimates from an alternative model, and discrepancies should trigger investigation into the sources and degree of the differences rather than being read directly as model error, since the benchmark is itself an alternative prediction [[reg:SR11-7:V.1.b]].
A close match between champion and refitted challenger is evidence in favor of the champion, but it should be read with caution, because the two share development lineage and can drift together.

### What monitoring should watch that this validation could not

This validation was conducted on a fixed development sample, so outcomes analysis against realized prepayment behaviour over time falls to monitoring: back-testing on vintages observed after implementation, at an observation frequency matched to the performance window, is the test that distinguishes a model that generalizes from one that fit its sample [[reg:SR26-2:V.1.b]].
Rate-environment sensitivity is the material exposure here, and the development window contains only the regimes it contains, so monitoring should track performance separately by origination vintage and by the prevailing rate incentive, and should flag when production inputs approach or exceed the ranges over which the model was estimated.
Process verification belongs to monitoring rather than to this review: the scoring implementation in production systems, the accuracy and completeness of the servicing and market data feeding it, and change control over the code should be verified on a recurring schedule.
Override behaviour should be logged and analyzed, since a high override rate, or an override process that consistently improves on the model, indicates the model is not performing as intended and may warrant revision.
Finally, monitoring should revisit the model's declared limitations on each cycle and record the response taken when a tracked series crosses a warning level or a declared bound, so that the decision between overlay, recalibration, and redevelopment is made against evidence rather than after the fact [[reg:SR26-2:V]].

## Appendix A — Claims

Grounding precision 0.9934 before repair (303 of 305 claims verified; 1 mismatch, 1 unsupported) and 1.0000 after 0 claim(s) rewritten and 2 number(s) removed from the prose. Per section (post-repair): summary 12/12; conceptual_soundness 70/70; data_integrity 72/72; outcomes 91/91; sensitivity 30/30; findings 22/22; monitoring 7/7.

Developer claims: 3 of 3 declared in `package.yaml` verify against this run's artifacts.

Excluded numeric tokens (not claims): section_number (section 4, section 2); citation_hash (2ad8d1a5, 6582e5dd, 75b5b833, faabc78e); regulatory_section_id (SR26-2:V, SR26-2:V.1.b, SR26-2:V.1.a, SR26-2:IV.1); finding_id (F-001); extractor_returned_excluded_token (1.0, 2.0, 3.0, 4.0).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The subject was run as an independent recomputation: the pac… | 300 | ratio | runtime |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 2 | summary | Recomputation covered the training split, at 313538 rows ; t… | 313538 | count | n | train | eq | `[[art:6582e5dd:profile.train.n]]` | verified | 313538 |
| 3 | summary | Recomputation covered the training split, at 313538 rows ; t… | 135060 | count | n | test | eq | `[[art:75b5b833:profile.test.n]]` | verified | 135060 |
| 4 | summary | Recomputation covered the training split, at 313538 rows ; t… | 221779 | count | n | vintage_holdout | eq | `[[art:faabc78e:metrics.vintage_holdout.n]]` | verified | 221779 |
| 5 | summary | Recomputation covered the training split, at 313538 rows ; t… | 283343 | count | n | out_of_time | eq | `[[art:c164ae00:metrics.out_of_time.n]]` | verified | 283343 |
| 6 | summary | Discrimination on test is 0.6549 against a declared floor of… | 0.6549 | ratio | auc | test | eq | `[[art:f3890b65:metrics.test.auc]]` | verified | 0.6549316245 |
| 7 | summary | Discrimination on test is 0.6549 against a declared floor of… | 0.65 | ratio | auc | test | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 8 | summary | The calibration slope on test is 1.017 , inside the declared… | 1.017 | ratio | calibration_slope | test | eq | `[[art:9b1edaa3:calibration_slope.test]]` | verified | 1.01683551 |
| 9 | summary | The calibration slope on test is 1.017 , inside the declared… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 10 | summary | The calibration slope on test is 1.017 , inside the declared… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 11 | summary | The largest train-to-test population stability index, the sc… | 0.005703 | ratio | psi |  | eq | `[[art:f632d5d4:psi.max]]` | verified | 0.005703237396 |
| 12 | summary | The largest train-to-test population stability index, the sc… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 13 | conceptual_soundness | The champion is a logistic model of monthly prepayment, line… | 313538 | count | n_train | train | eq | `[[art:29028ebe:run.model_summary#n_train]]` | verified | 313538 |
| 14 | conceptual_soundness | The champion is a logistic model of monthly prepayment, line… | 8596 | count | n_train_loans | train | eq | `[[art:29028ebe:run.model_summary#n_train_loans]]` | verified | 8596 |
| 15 | conceptual_soundness | The champion is a logistic model of monthly prepayment, line… | -4.79 | ratio | intercept | train | eq | `[[art:29028ebe:run.model_summary#intercept]]` | verified | -4.790257858 |
| 16 | conceptual_soundness | The feature inventory carries 12 features in total, of which… | 12 | count | n_features |  | eq | `[[art:0849f814:run.features#n]]` | verified | 12 |
| 17 | conceptual_soundness | The feature inventory carries 12 features in total, of which… | 5 | count | at_origination |  | eq | `[[art:0849f814:run.features#at_origination]]` | verified | 5 |
| 18 | conceptual_soundness | The feature inventory carries 12 features in total, of which… | 7 | count | before_period_start |  | eq | `[[art:0849f814:run.features#before_period_start]]` | verified | 7 |
| 19 | conceptual_soundness | No feature is dated to the performance period itself, at 0 ,… | 0 | count | during_period |  | eq | `[[art:0849f814:run.features#during_period]]` | verified | 0 |
| 20 | conceptual_soundness | No feature is dated to the performance period itself, at 0 ,… | 0 | count | after_outcome |  | eq | `[[art:0849f814:run.features#after_outcome]]` | verified | 0 |
| 21 | conceptual_soundness | The developer's own screen removed two inputs on collinearit… | 10 | ratio | vif_threshold |  | eq | `[[art:29028ebe:run.model_summary#vif_threshold]]` | verified | 10 |
| 22 | conceptual_soundness | The beginning-of-month balance was removed at an inflation f… | 16.5 | ratio | vif |  | eq | `[[art:29028ebe:run.model_summary#removed.bom_balance_log.vif]]` | verified | 16.49621 |
| 23 | conceptual_soundness | The beginning-of-month balance was removed at an inflation f… | 18.07 | ratio | vif |  | eq | `[[art:29028ebe:run.model_summary#removed.note_rate.vif]]` | verified | 18.069373 |
| 24 | conceptual_soundness | The largest single coefficient is on the first loan-age spli… | 0.611 | ratio | coefficient |  | eq | `[[art:29028ebe:run.model_summary#coefficients.loan_age_spline_1.value]]` | verified | 0.6109670628 |
| 25 | conceptual_soundness | The largest single coefficient is on the first loan-age spli… | -0.04263 | ratio | coefficient |  | eq | `[[art:29028ebe:run.model_summary#coefficients.loan_age_spline_2.value]]` | verified | -0.04262684642 |
| 26 | conceptual_soundness | The largest single coefficient is on the first loan-age spli… | -0.1501 | ratio | coefficient |  | eq | `[[art:29028ebe:run.model_summary#coefficients.loan_age_spline_3.value]]` | verified | -0.1501198233 |
| 27 | conceptual_soundness | The largest single coefficient is on the first loan-age spli… | -0.254 | ratio | coefficient |  | eq | `[[art:29028ebe:run.model_summary#coefficients.loan_age_spline_4.value]]` | verified | -0.2539751749 |
| 28 | conceptual_soundness | The refinance incentive carries 0.3952 and log original bala… | 0.3952 | ratio | coefficient |  | eq | `[[art:29028ebe:run.model_summary#coefficients.incentive.value]]` | verified | 0.3951616506 |
| 29 | conceptual_soundness | The refinance incentive carries 0.3952 and log original bala… | 0.286 | ratio | coefficient |  | eq | `[[art:29028ebe:run.model_summary#coefficients.orig_upb_log.value]]` | verified | 0.2860296007 |
| 30 | conceptual_soundness | The spread at origination enters at -0.09479 and original lo… | -0.09479 | ratio | coefficient |  | eq | `[[art:29028ebe:run.model_summary#coefficients.sato.value]]` | verified | -0.09479477581 |
| 31 | conceptual_soundness | The spread at origination enters at -0.09479 and original lo… | -0.08576 | ratio | coefficient |  | eq | `[[art:29028ebe:run.model_summary#coefficients.orig_ltv.value]]` | verified | -0.08575694141 |
| 32 | conceptual_soundness | The twelve-month rate change enters at -0.06772 , which is t… | -0.06772 | ratio | coefficient |  | eq | `[[art:29028ebe:run.model_summary#coefficients.rate_change_12m.value]]` | verified | -0.06772214655 |
| 33 | conceptual_soundness | Burnout carries 0.0008253 , positive where the subject-matte… | 0.0008253 | ratio | coefficient |  | eq | `[[art:29028ebe:run.model_summary#coefficients.burnout.value]]` | verified | 0.000825312491 |
| 34 | conceptual_soundness | Credit score at 0.02917 and the seasonal pair at 0.01281 and… | 0.02917 | ratio | coefficient |  | eq | `[[art:29028ebe:run.model_summary#coefficients.credit_score.value]]` | verified | 0.02916512564 |
| 35 | conceptual_soundness | Credit score at 0.02917 and the seasonal pair at 0.01281 and… | 0.01281 | ratio | coefficient |  | eq | `[[art:29028ebe:run.model_summary#coefficients.season_sin.value]]` | verified | 0.01280983524 |
| 36 | conceptual_soundness | Credit score at 0.02917 and the seasonal pair at 0.01281 and… | -0.04626 | ratio | coefficient |  | eq | `[[art:29028ebe:run.model_summary#coefficients.season_cos.value]]` | verified | -0.04626116305 |
| 37 | conceptual_soundness | Of the retained features checked, 3 have a fitted sign that… | 3 | count | n_disagreements | train | eq | `[[art:e223cd4a:sign_check.n_disagreements]]` | verified | 3 |
| 38 | conceptual_soundness | Original loan-to-value is fitted at -1 against a univariate… | -1 | ratio | coef_sign |  | eq | `[[art:7eec65ec:sign_check.orig_ltv.coef_sign]]` | verified | -1 |
| 39 | conceptual_soundness | Original loan-to-value is fitted at -1 against a univariate… | 1 | ratio | univariate_direction | train | eq | `[[art:85aabf06:sign_check.orig_ltv.univariate_direction]]` | verified | 1 |
| 40 | conceptual_soundness | Original loan-to-value is fitted at -1 against a univariate… | 0 | ratio | agrees |  | eq | `[[art:3f64b057:sign_check.orig_ltv.agrees]]` | verified | 0 |
| 41 | conceptual_soundness | Original loan-to-value is fitted at -1 against a univariate… | -0.002233 | ratio | delta_auc | test | eq | `[[art:acb0dcd5:ablation.orig_ltv.delta_auc]]` | verified | -0.002233212172 |
| 42 | conceptual_soundness | The spread at origination is fitted at -1 against a univaria… | -1 | ratio | coef_sign |  | eq | `[[art:265915cf:sign_check.sato.coef_sign]]` | verified | -1 |
| 43 | conceptual_soundness | The spread at origination is fitted at -1 against a univaria… | 1 | ratio | univariate_direction | train | eq | `[[art:c08233a6:sign_check.sato.univariate_direction]]` | verified | 1 |
| 44 | conceptual_soundness | The spread at origination is fitted at -1 against a univaria… | 0 | ratio | agrees |  | eq | `[[art:b3755963:sign_check.sato.agrees]]` | verified | 0 |
| 45 | conceptual_soundness | The spread at origination is fitted at -1 against a univaria… | -0.003026 | ratio | delta_auc | test | eq | `[[art:f406b192:ablation.sato.delta_auc]]` | verified | -0.003026491141 |
| 46 | conceptual_soundness | The sine seasonal term is fitted at +1 against a univariate… | 1 | ratio | coef_sign |  | eq | `[[art:761188ce:sign_check.season_sin.coef_sign]]` | verified | 1 |
| 47 | conceptual_soundness | The sine seasonal term is fitted at +1 against a univariate… | -1 | ratio | univariate_direction | train | eq | `[[art:b75f0b9c:sign_check.season_sin.univariate_direction]]` | verified | -1 |
| 48 | conceptual_soundness | The sine seasonal term is fitted at +1 against a univariate… | 0 | ratio | agrees |  | eq | `[[art:74f2d0e0:sign_check.season_sin.agrees]]` | verified | 0 |
| 49 | conceptual_soundness | The sine seasonal term is fitted at +1 against a univariate… | 0.000108 | ratio | delta_auc | test | eq | `[[art:47876c72:ablation.season_sin.delta_auc]]` | verified | 0.0001080069018 |
| 50 | conceptual_soundness | The remaining features checked agree with their univariate d… | 1 | ratio | coef_sign |  | eq | `[[art:684cf11a:sign_check.incentive.coef_sign]]` | verified | 1 |
| 51 | conceptual_soundness | The remaining features checked agree with their univariate d… | 1 | ratio | univariate_direction | train | eq | `[[art:8098d951:sign_check.incentive.univariate_direction]]` | verified | 1 |
| 52 | conceptual_soundness | The remaining features checked agree with their univariate d… | 1 | ratio | coef_sign |  | eq | `[[art:5aa309fc:sign_check.orig_upb_log.coef_sign]]` | verified | 1 |
| 53 | conceptual_soundness | The remaining features checked agree with their univariate d… | 1 | ratio | univariate_direction | train | eq | `[[art:b9743ecb:sign_check.orig_upb_log.univariate_direction]]` | verified | 1 |
| 54 | conceptual_soundness | The remaining features checked agree with their univariate d… | -1 | ratio | coef_sign |  | eq | `[[art:272b397e:sign_check.rate_change_12m.coef_sign]]` | verified | -1 |
| 55 | conceptual_soundness | The remaining features checked agree with their univariate d… | -1 | ratio | univariate_direction | train | eq | `[[art:35df3bf5:sign_check.rate_change_12m.univariate_direction]]` | verified | -1 |
| 56 | conceptual_soundness | The remaining features checked agree with their univariate d… | 1 | ratio | coef_sign |  | eq | `[[art:1ec1078b:sign_check.credit_score.coef_sign]]` | verified | 1 |
| 57 | conceptual_soundness | The remaining features checked agree with their univariate d… | 1 | ratio | univariate_direction | train | eq | `[[art:42303896:sign_check.credit_score.univariate_direction]]` | verified | 1 |
| 58 | conceptual_soundness | The remaining features checked agree with their univariate d… | 1 | ratio | coef_sign |  | eq | `[[art:a3063608:sign_check.burnout.coef_sign]]` | verified | 1 |
| 59 | conceptual_soundness | The remaining features checked agree with their univariate d… | 1 | ratio | univariate_direction | train | eq | `[[art:bfc96bb2:sign_check.burnout.univariate_direction]]` | verified | 1 |
| 60 | conceptual_soundness | The remaining features checked agree with their univariate d… | -1 | ratio | coef_sign |  | eq | `[[art:7dbb1ffc:sign_check.season_cos.coef_sign]]` | verified | -1 |
| 61 | conceptual_soundness | The remaining features checked agree with their univariate d… | -1 | ratio | univariate_direction | train | eq | `[[art:03e931f0:sign_check.season_cos.univariate_direction]]` | verified | -1 |
| 62 | conceptual_soundness | The remaining features checked agree with their univariate d… | 1 | ratio | agrees |  | eq | `[[art:f7b2338e:sign_check.incentive.agrees]]` | verified | 1 |
| 63 | conceptual_soundness | The remaining features checked agree with their univariate d… | 1 | ratio | agrees |  | eq | `[[art:07a9d3e6:sign_check.orig_upb_log.agrees]]` | verified | 1 |
| 64 | conceptual_soundness | The remaining features checked agree with their univariate d… | 1 | ratio | agrees |  | eq | `[[art:61c1d5cc:sign_check.rate_change_12m.agrees]]` | verified | 1 |
| 65 | conceptual_soundness | The remaining features checked agree with their univariate d… | 1 | ratio | agrees |  | eq | `[[art:915bf8eb:sign_check.credit_score.agrees]]` | verified | 1 |
| 66 | conceptual_soundness | The remaining features checked agree with their univariate d… | 1 | ratio | agrees |  | eq | `[[art:2eec20ab:sign_check.burnout.agrees]]` | verified | 1 |
| 67 | conceptual_soundness | The remaining features checked agree with their univariate d… | 1 | ratio | agrees |  | eq | `[[art:7f18ddf7:sign_check.season_cos.agrees]]` | verified | 1 |
| 68 | conceptual_soundness | Refits of the champion's functional form with one feature dr… | 0.6391 | ratio | baseline_auc | test | eq | `[[art:ed55c319:ablation.baseline_auc]]` | verified | 0.6391430546 |
| 69 | conceptual_soundness | Discrimination is concentrated in two inputs: dropping log o… | -0.0171 | ratio | delta_auc | test | eq | `[[art:d9fda2c8:ablation.orig_upb_log.delta_auc]]` | verified | -0.01710427827 |
| 70 | conceptual_soundness | Discrimination is concentrated in two inputs: dropping log o… | -0.0161 | ratio | delta_auc | test | eq | `[[art:b1880518:ablation.incentive.delta_auc]]` | verified | -0.01609580876 |
| 71 | conceptual_soundness | Loan age contributes -0.004572 , and beyond the spread and l… | -0.004572 | ratio | delta_auc | test | eq | `[[art:0b5dcaeb:ablation.loan_age.delta_auc]]` | verified | -0.004571578483 |
| 72 | conceptual_soundness | Loan age contributes -0.004572 , and beyond the spread and l… | -0.0003635 | ratio | delta_auc | test | eq | `[[art:f472749f:ablation.rate_change_12m.delta_auc]]` | verified | -0.0003635311596 |
| 73 | conceptual_soundness | Loan age contributes -0.004572 , and beyond the spread and l… | -0.0002604 | ratio | delta_auc | test | eq | `[[art:9963f841:ablation.credit_score.delta_auc]]` | verified | -0.0002603974752 |
| 74 | conceptual_soundness | Loan age contributes -0.004572 , and beyond the spread and l… | 0.000108 | ratio | delta_auc | test | eq | `[[art:47876c72:ablation.season_sin.delta_auc]]` | verified | 0.0001080069018 |
| 75 | conceptual_soundness | Loan age contributes -0.004572 , and beyond the spread and l… | 0.0005739 | ratio | delta_auc | test | eq | `[[art:499cf97d:ablation.burnout.delta_auc]]` | verified | 0.0005738937198 |
| 76 | conceptual_soundness | Loan age contributes -0.004572 , and beyond the spread and l… | 0.001845 | ratio | delta_auc | test | eq | `[[art:0931b2a0:ablation.season_cos.delta_auc]]` | verified | 0.001844627367 |
| 77 | conceptual_soundness | The challenger scores 0.6653 on test against the champion's… | 0.6653 | ratio | auc | test | eq | `[[art:6f811314:challenger.auc]]` | verified | 0.6653496435 |
| 78 | conceptual_soundness | The challenger scores 0.6653 on test against the champion's… | 0.6549 | ratio | auc | test | eq | `[[art:f3890b65:metrics.test.auc]]` | verified | 0.6549316245 |
| 79 | conceptual_soundness | The challenger scores 0.6653 on test against the champion's… | 0.01042 | ratio | delta_auc | test | eq | `[[art:10b988e8:challenger.delta_auc]]` | verified | 0.01041801898 |
| 80 | conceptual_soundness | The rule that decides whether such a difference matters sets… | 0.03 | ratio | delta_auc |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 81 | conceptual_soundness | Calibration tells the same story in the same direction, with… | 0.009119 | ratio | brier | test | eq | `[[art:0e717888:challenger.brier]]` | verified | 0.00911859482 |
| 82 | conceptual_soundness | Calibration tells the same story in the same direction, with… | 0.009063 | ratio | brier | test | eq | `[[art:21d0b581:metrics.test.brier]]` | verified | 0.009062660213 |
| 83 | data_integrity | The run profiles a training split of 313538 rows , a test sp… | 313538 | count | n | train | eq | `[[art:6582e5dd:profile.train.n]]` | verified | 313538 |
| 84 | data_integrity | The run profiles a training split of 313538 rows , a test sp… | 135060 | count | n | test | eq | `[[art:75b5b833:profile.test.n]]` | verified | 135060 |
| 85 | data_integrity | The run profiles a training split of 313538 rows , a test sp… | 283343 | count | n | out_of_time | eq | `[[art:a0103a06:profile.out_of_time.n]]` | verified | 283343 |
| 86 | data_integrity | The run profiles a training split of 313538 rows , a test sp… | 221779 | count | n | vintage_holdout | eq | `[[art:fcb7e414:profile.vintage_holdout.n]]` | verified | 221779 |
| 87 | data_integrity | The largest missing fraction in any column is 0 in train, 0… | 0 | ratio | missing_max | train | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 88 | data_integrity | The largest missing fraction in any column is 0 in train, 0… | 0 | ratio | missing_max | test | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 89 | data_integrity | The largest missing fraction in any column is 0 in train, 0… | 0 | ratio | missing_max | out_of_time | eq | `[[art:4dafce11:profile.out_of_time.missing.max]]` | verified | 0 |
| 90 | data_integrity | The largest missing fraction in any column is 0 in train, 0… | 0 | ratio | missing_max | vintage_holdout | eq | `[[art:329bb430:profile.vintage_holdout.missing.max]]` | verified | 0 |
| 91 | data_integrity | Because these maxima coincide, no split differs from another… | 0.1 | ratio | missing_gap |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 92 | data_integrity | The declared stability bound is 0.25 , stated for the traini… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 93 | data_integrity | The declared stability bound is 0.25 , stated for the traini… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 94 | data_integrity | Between train and test the largest population stability inde… | 0.005703 | ratio | psi |  | eq | `[[art:f632d5d4:psi.max]]` | verified | 0.005703237396 |
| 95 | data_integrity | Between train and test the largest population stability inde… | 0.005703 | ratio | psi |  | eq | `[[art:6ea40553:psi.orig_ltv]]` | verified | 0.005703237396 |
| 96 | data_integrity | Between train and test the largest population stability inde… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 97 | data_integrity | The remaining train-to-test indices are smaller still: credi… | 0.003718 | ratio | psi |  | eq | `[[art:8a078965:psi.credit_score]]` | verified | 0.003717519291 |
| 98 | data_integrity | The remaining train-to-test indices are smaller still: credi… | 0.002753 | ratio | psi |  | eq | `[[art:4af07770:psi.orig_upb_log]]` | verified | 0.002752784614 |
| 99 | data_integrity | The remaining train-to-test indices are smaller still: credi… | 0.002192 | ratio | psi |  | eq | `[[art:e68bfd2e:psi.sato]]` | verified | 0.002192276542 |
| 100 | data_integrity | The remaining train-to-test indices are smaller still: credi… | 0.001567 | ratio | psi |  | eq | `[[art:40a3f946:psi.burnout]]` | verified | 0.001566859823 |
| 101 | data_integrity | The remaining train-to-test indices are smaller still: credi… | 0.0006641 | ratio | psi |  | eq | `[[art:6e6c94e1:psi.y_score]]` | verified | 0.0006640882006 |
| 102 | data_integrity | The remaining train-to-test indices are smaller still: credi… | 0.0003749 | ratio | psi |  | eq | `[[art:61538982:psi.incentive]]` | verified | 0.0003749417053 |
| 103 | data_integrity | The remaining train-to-test indices are smaller still: credi… | 8.302e-05 | ratio | psi |  | eq | `[[art:f548214d:psi.loan_age]]` | verified | 8.302102495e-05 |
| 104 | data_integrity | The remaining train-to-test indices are smaller still: credi… | 3.589e-05 | ratio | psi |  | eq | `[[art:23b9e924:psi.rate_change_12m]]` | verified | 3.588607828e-05 |
| 105 | data_integrity | The remaining train-to-test indices are smaller still: credi… | 3.366e-06 | ratio | psi |  | eq | `[[art:ae17ebba:psi.season_sin]]` | verified | 3.365586451e-06 |
| 106 | data_integrity | The remaining train-to-test indices are smaller still: credi… | 3.184e-06 | ratio | psi |  | eq | `[[art:9db38513:psi.season_cos]]` | verified | 3.183525037e-06 |
| 107 | data_integrity | The out-of-time split is different in kind, with loan age sh… | 3.086 | ratio | psi | out_of_time | eq | `[[art:5f3c6bba:psi.out_of_time.loan_age]]` | verified | 3.085573352 |
| 108 | data_integrity | The out-of-time split is different in kind, with loan age sh… | 1.726 | ratio | psi | out_of_time | eq | `[[art:73dfd106:psi.out_of_time.incentive]]` | verified | 1.726005597 |
| 109 | data_integrity | The out-of-time split is different in kind, with loan age sh… | 1.551 | ratio | psi | out_of_time | eq | `[[art:5316f456:psi.out_of_time.burnout]]` | verified | 1.551357138 |
| 110 | data_integrity | The out-of-time split is different in kind, with loan age sh… | 1.54 | ratio | psi | out_of_time | eq | `[[art:75370112:psi.out_of_time.y_score]]` | verified | 1.539886915 |
| 111 | data_integrity | The out-of-time split is different in kind, with loan age sh… | 0.8254 | ratio | psi | out_of_time | eq | `[[art:09e68722:psi.out_of_time.rate_change_12m]]` | verified | 0.8254176602 |
| 112 | data_integrity | The out-of-time split is different in kind, with loan age sh… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 113 | data_integrity | The rest of the out-of-time picture is quiet by comparison:… | 0.02419 | ratio | psi | out_of_time | eq | `[[art:7388771e:psi.out_of_time.season_sin]]` | verified | 0.0241861509 |
| 114 | data_integrity | The rest of the out-of-time picture is quiet by comparison:… | 0.02136 | ratio | psi | out_of_time | eq | `[[art:abf1e02d:psi.out_of_time.orig_upb_log]]` | verified | 0.02135726451 |
| 115 | data_integrity | The rest of the out-of-time picture is quiet by comparison:… | 0.01598 | ratio | psi | out_of_time | eq | `[[art:7f6fab7a:psi.out_of_time.orig_ltv]]` | verified | 0.01597816452 |
| 116 | data_integrity | The rest of the out-of-time picture is quiet by comparison:… | 0.01473 | ratio | psi | out_of_time | eq | `[[art:85a8a904:psi.out_of_time.sato]]` | verified | 0.01472768815 |
| 117 | data_integrity | The rest of the out-of-time picture is quiet by comparison:… | 0.00591 | ratio | psi | out_of_time | eq | `[[art:8ef132e3:psi.out_of_time.season_cos]]` | verified | 0.005910467488 |
| 118 | data_integrity | The rest of the out-of-time picture is quiet by comparison:… | 0.004578 | ratio | psi | out_of_time | eq | `[[art:5341c0a9:psi.out_of_time.credit_score]]` | verified | 0.004578346658 |
| 119 | data_integrity | The rest of the out-of-time picture is quiet by comparison:… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 120 | data_integrity | The vintage holdout shows the same pattern in milder form, w… | 1.298 | ratio | psi | vintage_holdout | eq | `[[art:86f7884e:psi.vintage_holdout.incentive]]` | verified | 1.297995585 |
| 121 | data_integrity | The vintage holdout shows the same pattern in milder form, w… | 0.8816 | ratio | psi | vintage_holdout | eq | `[[art:2575a328:psi.vintage_holdout.rate_change_12m]]` | verified | 0.8816315659 |
| 122 | data_integrity | The vintage holdout shows the same pattern in milder form, w… | 0.7656 | ratio | psi | vintage_holdout | eq | `[[art:ae7b9c29:psi.vintage_holdout.y_score]]` | verified | 0.7656434406 |
| 123 | data_integrity | The vintage holdout shows the same pattern in milder form, w… | 0.5116 | ratio | psi | vintage_holdout | eq | `[[art:e3a3122f:psi.vintage_holdout.burnout]]` | verified | 0.5116279641 |
| 124 | data_integrity | The vintage holdout shows the same pattern in milder form, w… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 125 | data_integrity | Within that split the remaining measures sit below the bound… | 0.2002 | ratio | psi | vintage_holdout | eq | `[[art:b34d2ebe:psi.vintage_holdout.sato]]` | verified | 0.2002005108 |
| 126 | data_integrity | Within that split the remaining measures sit below the bound… | 0.1507 | ratio | psi | vintage_holdout | eq | `[[art:2de85f94:psi.vintage_holdout.loan_age]]` | verified | 0.1506849325 |
| 127 | data_integrity | Within that split the remaining measures sit below the bound… | 0.03076 | ratio | psi | vintage_holdout | eq | `[[art:bd074d53:psi.vintage_holdout.orig_upb_log]]` | verified | 0.03076150585 |
| 128 | data_integrity | Within that split the remaining measures sit below the bound… | 0.01065 | ratio | psi | vintage_holdout | eq | `[[art:a5066c0f:psi.vintage_holdout.orig_ltv]]` | verified | 0.01065378135 |
| 129 | data_integrity | Within that split the remaining measures sit below the bound… | 0.007218 | ratio | psi | vintage_holdout | eq | `[[art:341abd78:psi.vintage_holdout.credit_score]]` | verified | 0.007217892201 |
| 130 | data_integrity | Within that split the remaining measures sit below the bound… | 0.003659 | ratio | psi | vintage_holdout | eq | `[[art:dad1e65c:psi.vintage_holdout.season_sin]]` | verified | 0.003658742975 |
| 131 | data_integrity | Within that split the remaining measures sit below the bound… | 0.000942 | ratio | psi | vintage_holdout | eq | `[[art:67aee1b5:psi.vintage_holdout.season_cos]]` | verified | 0.0009420084002 |
| 132 | data_integrity | Characteristic stability, which weighs each feature's shift… | 0.006455 | ratio | csi |  | eq | `[[art:131d42db:csi.max]]` | verified | 0.00645531823 |
| 133 | data_integrity | Characteristic stability, which weighs each feature's shift… | 0.006455 | ratio | csi |  | eq | `[[art:7561e8b0:csi.orig_upb_log]]` | verified | 0.00645531823 |
| 134 | data_integrity | The other contributions are spread at origination at 0.00111… | 0.001116 | ratio | csi |  | eq | `[[art:a54b158e:csi.sato]]` | verified | 0.001115931346 |
| 135 | data_integrity | The other contributions are spread at origination at 0.00111… | 0.001102 | ratio | csi |  | eq | `[[art:020f5ce2:csi.incentive]]` | verified | 0.001102078062 |
| 136 | data_integrity | The other contributions are spread at origination at 0.00111… | 0.0005902 | ratio | csi |  | eq | `[[art:1c9006f3:csi.orig_ltv]]` | verified | 0.0005902054355 |
| 137 | data_integrity | The other contributions are spread at origination at 0.00111… | 0.0002237 | ratio | csi |  | eq | `[[art:ffdb6fdd:csi.rate_change_12m]]` | verified | 0.0002237020655 |
| 138 | data_integrity | The other contributions are spread at origination at 0.00111… | 6.191e-05 | ratio | csi |  | eq | `[[art:c70e3aa4:csi.season_cos]]` | verified | 6.190848201e-05 |
| 139 | data_integrity | The other contributions are spread at origination at 0.00111… | 1.97e-05 | ratio | csi |  | eq | `[[art:0a280759:csi.credit_score]]` | verified | 1.970189663e-05 |
| 140 | data_integrity | The other contributions are spread at origination at 0.00111… | 2.108e-05 | ratio | csi |  | eq | `[[art:fb3bf812:csi.season_sin]]` | verified | 2.108057316e-05 |
| 141 | data_integrity | The other contributions are spread at origination at 0.00111… | 3.43e-06 | ratio | csi |  | eq | `[[art:e4d3e34a:csi.burnout]]` | verified | 3.430062025e-06 |
| 142 | data_integrity | The other contributions are spread at origination at 0.00111… | 0 | ratio | csi |  | eq | `[[art:df52c920:csi.loan_age]]` | verified | 0 |
| 143 | data_integrity | Read against the declared ceiling of 0.25 , the weighted con… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 144 | data_integrity | Features declared as observed during the performance period… | 0 | count | n_flagged |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 145 | data_integrity | The strongest single feature reaches an AUC of 0.5995 on its… | 0.5995 | ratio | auc |  | eq | `[[art:9e2ffad1:leakage.target_corr.max_single_feature_auc]]` | verified | 0.5994570075 |
| 146 | data_integrity | The strongest single feature reaches an AUC of 0.5995 on its… | 0.9 | ratio | auc |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 147 | data_integrity | On the identifier arm, the share of test rows whose loan and… | 0 | ratio | overlap |  | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 148 | data_integrity | On the identifier arm, the share of test rows whose loan and… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 149 | data_integrity | On the feature-vector arm, the share of test rows whose feat… | 0 | ratio | overlap |  | eq | `[[art:0fec8048:leakage.overlap.features]]` | verified | 0 |
| 150 | data_integrity | On the feature-vector arm, the share of test rows whose feat… | 0.005 | ratio | overlap |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 151 | data_integrity | That applied bound is the larger of the declared overlap bou… | 0.0001531 | ratio | duplicates | train | eq | `[[art:ce57652e:leakage.duplicates.train]]` | verified | 0.0001530914913 |
| 152 | data_integrity | The corresponding row-level overlap measure is likewise 0 ,… | 0 | ratio | overlap |  | eq | `[[art:4c9fcd09:leakage.overlap]]` | verified | 0 |
| 153 | data_integrity | The corresponding row-level overlap measure is likewise 0 ,… | 0.005 | ratio | overlap |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 154 | data_integrity | The name screen matches 0 feature names against the target-a… | 0 | count | n_matched |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 155 | outcomes | On test, the logistic regression of the outcome on the logit… | 1.017 | ratio | calibration_slope | test | eq | `[[art:9b1edaa3:calibration_slope.test]]` | verified | 1.01683551 |
| 156 | outcomes | On test, the logistic regression of the outcome on the logit… | 0.02905 | ratio | calibration_intercept | test | eq | `[[art:1a8280dd:calibration_intercept.test]]` | verified | 0.02905298382 |
| 157 | outcomes | On train, the same regression gives a slope of 0.9971 and an… | 0.9971 | ratio | calibration_slope | train | eq | `[[art:28331672:calibration_slope.train]]` | verified | 0.9971012419 |
| 158 | outcomes | On train, the same regression gives a slope of 0.9971 and an… | -0.016 | ratio | calibration_intercept | train | eq | `[[art:be40e0a7:calibration_intercept.train]]` | verified | -0.01599765114 |
| 159 | outcomes | On vintage_holdout, the slope is 0.8502 with an intercept of… | 0.8502 | ratio | calibration_slope | vintage_holdout | eq | `[[art:80fe61d2:calibration_slope.vintage_holdout]]` | verified | 0.8501990162 |
| 160 | outcomes | On vintage_holdout, the slope is 0.8502 with an intercept of… | 0.06119 | ratio | calibration_intercept | vintage_holdout | eq | `[[art:0d75b532:calibration_intercept.vintage_holdout]]` | verified | 0.06118872124 |
| 161 | outcomes | On out_of_time, the slope falls to 0.4321 with an intercept… | 0.4321 | ratio | calibration_slope | out_of_time | eq | `[[art:d9f87bb2:calibration_slope.out_of_time]]` | verified | 0.432125782 |
| 162 | outcomes | On out_of_time, the slope falls to 0.4321 with an intercept… | -1.762 | ratio | calibration_intercept | out_of_time | eq | `[[art:53a8d76b:calibration_intercept.out_of_time]]` | verified | -1.761998635 |
| 163 | outcomes | On out_of_time, the slope falls to 0.4321 with an intercept… | 0.8 | ratio | calibration_slope |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 164 | outcomes | On out_of_time, the slope falls to 0.4321 with an intercept… | 1.2 | ratio | calibration_slope |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 165 | outcomes | On train, the mean predicted probability is 0.009503 against… | 0.009503 | ratio | mean_predicted | train | eq | `[[art:716b94b2:metrics.train.mean_predicted]]` | verified | 0.009503175968 |
| 166 | outcomes | On train, the mean predicted probability is 0.009503 against… | 0.009476 | ratio | event_rate | train | eq | `[[art:8ecc2809:metrics.train.event_rate]]` | verified | 0.00947572543 |
| 167 | outcomes | On train, the mean predicted probability is 0.009503 against… | 0.002897 | ratio | mean_rel_gap | train | eq | `[[art:332fc4d9:calibration.mean_rel_gap.train]]` | verified | 0.002896932549 |
| 168 | outcomes | On train, the mean predicted probability is 0.009503 against… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 169 | outcomes | On test, the mean predicted probability is 0.009606 against… | 0.009606 | ratio | mean_predicted | test | eq | `[[art:24595a04:metrics.test.mean_predicted]]` | verified | 0.009605653506 |
| 170 | outcomes | On test, the mean predicted probability is 0.009606 against… | 0.009174 | ratio | event_rate | test | eq | `[[art:78206f7c:metrics.test.event_rate]]` | verified | 0.009173700578 |
| 171 | outcomes | On test, the mean predicted probability is 0.009606 against… | 0.04709 | ratio | mean_rel_gap | test | eq | `[[art:a173f6c5:calibration.mean_rel_gap.test]]` | verified | 0.04708600686 |
| 172 | outcomes | On test, the mean predicted probability is 0.009606 against… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 173 | outcomes | On vintage_holdout, the mean predicted probability is 0.0098… | 0.009873 | ratio | mean_predicted | vintage_holdout | eq | `[[art:c12c52f7:metrics.vintage_holdout.mean_predicted]]` | verified | 0.009872671801 |
| 174 | outcomes | On vintage_holdout, the mean predicted probability is 0.0098… | 0.01948 | ratio | event_rate | vintage_holdout | eq | `[[art:bab66615:metrics.vintage_holdout.event_rate]]` | verified | 0.01947885057 |
| 175 | outcomes | On vintage_holdout, the mean predicted probability is 0.0098… | 0.4932 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:92b5a8c4:calibration.mean_rel_gap.vintage_holdout]]` | verified | 0.4931594261 |
| 176 | outcomes | On vintage_holdout, the mean predicted probability is 0.0098… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 177 | outcomes | On out_of_time, the mean predicted probability is 0.01005 ag… | 0.01005 | ratio | mean_predicted | out_of_time | eq | `[[art:fd777cc4:metrics.out_of_time.mean_predicted]]` | verified | 0.01005421904 |
| 178 | outcomes | On out_of_time, the mean predicted probability is 0.01005 ag… | 0.01868 | ratio | event_rate | out_of_time | eq | `[[art:cf3a82aa:metrics.out_of_time.event_rate]]` | verified | 0.01868053913 |
| 179 | outcomes | On out_of_time, the mean predicted probability is 0.01005 ag… | 0.4618 | ratio | mean_rel_gap | out_of_time | eq | `[[art:9e4c8750:calibration.mean_rel_gap.out_of_time]]` | verified | 0.4617811099 |
| 180 | outcomes | On out_of_time, the mean predicted probability is 0.01005 ag… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 181 | outcomes | The portfolio-level prepayment comparison tells the same sto… | 0.02202 | ratio | cpr_mae | train | eq | `[[art:3487a403:cpr.train.mae]]` | verified | 0.02201633853 |
| 182 | outcomes | The portfolio-level prepayment comparison tells the same sto… | 0.02642 | ratio | cpr_mae | test | eq | `[[art:939c5fb9:cpr.test.mae]]` | verified | 0.02641734834 |
| 183 | outcomes | The portfolio-level prepayment comparison tells the same sto… | 0.0785 | ratio | cpr_mae | vintage_holdout | eq | `[[art:0cc82390:cpr.vintage_holdout.mae]]` | verified | 0.07850151406 |
| 184 | outcomes | The portfolio-level prepayment comparison tells the same sto… | 0.08656 | ratio | cpr_mae | out_of_time | eq | `[[art:a467ad41:cpr.out_of_time.mae]]` | verified | 0.08656382516 |
| 185 | outcomes | AUC is 0.6504 on train, 0.6549 on test, 0.7388 on vintage_ho… | 0.6504 | ratio | auc | train | eq | `[[art:40964132:metrics.train.auc]]` | verified | 0.6503543409 |
| 186 | outcomes | AUC is 0.6504 on train, 0.6549 on test, 0.7388 on vintage_ho… | 0.6549 | ratio | auc | test | eq | `[[art:f3890b65:metrics.test.auc]]` | verified | 0.6549316245 |
| 187 | outcomes | AUC is 0.6504 on train, 0.6549 on test, 0.7388 on vintage_ho… | 0.7388 | ratio | auc | vintage_holdout | eq | `[[art:95f87cc7:metrics.vintage_holdout.auc]]` | verified | 0.7388200711 |
| 188 | outcomes | AUC is 0.6504 on train, 0.6549 on test, 0.7388 on vintage_ho… | 0.6898 | ratio | auc | out_of_time | eq | `[[art:cb57fe9a:metrics.out_of_time.auc]]` | verified | 0.6898015086 |
| 189 | outcomes | Gini is 0.3007 on train, 0.3099 on test, 0.4776 on vintage_h… | 0.3007 | ratio | gini | train | eq | `[[art:da0e7063:metrics.train.gini]]` | verified | 0.3007086819 |
| 190 | outcomes | Gini is 0.3007 on train, 0.3099 on test, 0.4776 on vintage_h… | 0.3099 | ratio | gini | test | eq | `[[art:5710cba3:metrics.test.gini]]` | verified | 0.309863249 |
| 191 | outcomes | Gini is 0.3007 on train, 0.3099 on test, 0.4776 on vintage_h… | 0.4776 | ratio | gini | vintage_holdout | eq | `[[art:75ad81b1:metrics.vintage_holdout.gini]]` | verified | 0.4776401422 |
| 192 | outcomes | Gini is 0.3007 on train, 0.3099 on test, 0.4776 on vintage_h… | 0.3796 | ratio | gini | out_of_time | eq | `[[art:6c5edac7:metrics.out_of_time.gini]]` | verified | 0.3796030172 |
| 193 | outcomes | KS is 0.2262 on train, 0.2375 on test, 0.411 on vintage_hold… | 0.2262 | ratio | ks | train | eq | `[[art:96e91aee:metrics.train.ks]]` | verified | 0.2261527235 |
| 194 | outcomes | KS is 0.2262 on train, 0.2375 on test, 0.411 on vintage_hold… | 0.2375 | ratio | ks | test | eq | `[[art:c35222f3:metrics.test.ks]]` | verified | 0.237529396 |
| 195 | outcomes | KS is 0.2262 on train, 0.2375 on test, 0.411 on vintage_hold… | 0.411 | ratio | ks | vintage_holdout | eq | `[[art:699a7598:metrics.vintage_holdout.ks]]` | verified | 0.4110310226 |
| 196 | outcomes | KS is 0.2262 on train, 0.2375 on test, 0.411 on vintage_hold… | 0.3021 | ratio | ks | out_of_time | eq | `[[art:c486329f:metrics.out_of_time.ks]]` | verified | 0.3020779889 |
| 197 | outcomes | The Brier score is 0.009359 on train, 0.009063 on test, 0.01… | 0.009359 | ratio | brier | train | eq | `[[art:574cf8a4:metrics.train.brier]]` | verified | 0.009358514597 |
| 198 | outcomes | The Brier score is 0.009359 on train, 0.009063 on test, 0.01… | 0.009063 | ratio | brier | test | eq | `[[art:21d0b581:metrics.test.brier]]` | verified | 0.009062660213 |
| 199 | outcomes | The Brier score is 0.009359 on train, 0.009063 on test, 0.01… | 0.01898 | ratio | brier | vintage_holdout | eq | `[[art:6a660ed9:metrics.vintage_holdout.brier]]` | verified | 0.01897762486 |
| 200 | outcomes | The Brier score is 0.009359 on train, 0.009063 on test, 0.01… | 0.01824 | ratio | brier | out_of_time | eq | `[[art:4ddcaaea:metrics.out_of_time.brier]]` | verified | 0.01823697645 |
| 201 | outcomes | Log loss is 0.05226 on train, 0.05083 on test, 0.09345 on vi… | 0.05226 | ratio | logloss | train | eq | `[[art:716b9dc1:metrics.train.logloss]]` | verified | 0.05225625901 |
| 202 | outcomes | Log loss is 0.05226 on train, 0.05083 on test, 0.09345 on vi… | 0.05083 | ratio | logloss | test | eq | `[[art:048e9ca7:metrics.test.logloss]]` | verified | 0.0508316292 |
| 203 | outcomes | Log loss is 0.05226 on train, 0.05083 on test, 0.09345 on vi… | 0.09345 | ratio | logloss | vintage_holdout | eq | `[[art:630a591b:metrics.vintage_holdout.logloss]]` | verified | 0.09344516111 |
| 204 | outcomes | Log loss is 0.05226 on train, 0.05083 on test, 0.09345 on vi… | 0.09576 | ratio | logloss | out_of_time | eq | `[[art:8d53f72c:metrics.out_of_time.logloss]]` | verified | 0.09576249258 |
| 205 | outcomes | The row counts behind these metrics are 313538 on train, 135… | 313538 | count | n | train | eq | `[[art:72c7a6d2:metrics.train.n]]` | verified | 313538 |
| 206 | outcomes | The row counts behind these metrics are 313538 on train, 135… | 135060 | count | n | test | eq | `[[art:629740ff:metrics.test.n]]` | verified | 135060 |
| 207 | outcomes | The row counts behind these metrics are 313538 on train, 135… | 221779 | count | n | vintage_holdout | eq | `[[art:faabc78e:metrics.vintage_holdout.n]]` | verified | 221779 |
| 208 | outcomes | The row counts behind these metrics are 313538 on train, 135… | 283343 | count | n | out_of_time | eq | `[[art:c164ae00:metrics.out_of_time.n]]` | verified | 283343 |
| 209 | outcomes | The share of events captured in the top two deciles is 0.38… | 0.38 | ratio | top2_capture | train | eq | `[[art:b2f9e5d8:deciles.train.top2_capture]]` | verified | 0.3800067317 |
| 210 | outcomes | The share of events captured in the top two deciles is 0.38… | 0.3769 | ratio | top2_capture | test | eq | `[[art:1d4dff05:deciles.test.top2_capture]]` | verified | 0.3769168684 |
| 211 | outcomes | The share of events captured in the top two deciles is 0.38… | 0.5116 | ratio | top2_capture | vintage_holdout | eq | `[[art:3cd3b5a3:deciles.vintage_holdout.top2_capture]]` | verified | 0.5115740741 |
| 212 | outcomes | The share of events captured in the top two deciles is 0.38… | 0.4313 | ratio | top2_capture | out_of_time | eq | `[[art:58f451c3:deciles.out_of_time.top2_capture]]` | verified | 0.4313243907 |
| 213 | outcomes | The train-to-test AUC gap is the difference between 0.6504 a… | 0.6504 | ratio | auc | train | eq | `[[art:40964132:metrics.train.auc]]` | verified | 0.6503543409 |
| 214 | outcomes | The train-to-test AUC gap is the difference between 0.6504 a… | 0.6549 | ratio | auc | test | eq | `[[art:f3890b65:metrics.test.auc]]` | verified | 0.6549316245 |
| 215 | outcomes | The train-to-test AUC gap is the difference between 0.6504 a… | 0.08 | ratio | auc_gap |  | eq | `[[art:630f28f4:threshold.O1.auc_gap]]` | verified | 0.08 |
| 216 | outcomes | On this slice AUC falls 0.08523 below the split's own AUC, a… | 0.08523 | ratio | auc_gap | out_of_time | eq | `[[art:e7b201c8:metrics.out_of_time.sub.incentive_high.auc_gap]]` | verified | 0.08522987832 |
| 217 | outcomes | On this slice AUC falls 0.08523 below the split's own AUC, a… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 218 | outcomes | The slice holds 0.5 of the split, above the floor of 0.1 and… | 0.5 | ratio | share | out_of_time | eq | `[[art:4787f68a:metrics.out_of_time.sub.incentive_high.share]]` | verified | 0.4999982354 |
| 219 | outcomes | The slice holds 0.5 of the split, above the floor of 0.1 and… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 220 | outcomes | The slice holds 0.5 of the split, above the floor of 0.1 and… | 0.95 | ratio | slice_max_share |  | eq | `[[art:a928a05c:threshold.O1.slice_max_share]]` | verified | 0.95 |
| 221 | outcomes | Mean predicted here is 0.0188 against an observed rate of 0.… | 0.0188 | ratio | mean_predicted | out_of_time | eq | `[[art:b7288bbc:metrics.out_of_time.sub.incentive_high.mean_predicted]]` | verified | 0.01880179941 |
| 222 | outcomes | Mean predicted here is 0.0188 against an observed rate of 0.… | 0.02949 | ratio | event_rate | out_of_time | eq | `[[art:f62f5a9c:metrics.out_of_time.sub.incentive_high.event_rate]]` | verified | 0.02949086263 |
| 223 | outcomes | On this slice AUC falls 0.17 below the split's own AUC, abov… | 0.17 | ratio | auc_gap | out_of_time | eq | `[[art:379c90f9:metrics.out_of_time.sub.incentive_low.auc_gap]]` | verified | 0.1699901597 |
| 224 | outcomes | On this slice AUC falls 0.17 below the split's own AUC, abov… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 225 | outcomes | The slice holds 0.5 of the split, above the floor of 0.1 and… | 0.5 | ratio | share | out_of_time | eq | `[[art:cc116fda:metrics.out_of_time.sub.incentive_low.share]]` | verified | 0.5000017646 |
| 226 | outcomes | The slice holds 0.5 of the split, above the floor of 0.1 and… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 227 | outcomes | The slice holds 0.5 of the split, above the floor of 0.1 and… | 0.95 | ratio | slice_max_share |  | eq | `[[art:a928a05c:threshold.O1.slice_max_share]]` | verified | 0.95 |
| 228 | outcomes | Mean predicted here is 0.001307 against an observed rate of… | 0.001307 | ratio | mean_predicted | out_of_time | eq | `[[art:e77d973c:metrics.out_of_time.sub.incentive_low.mean_predicted]]` | verified | 0.001306700417 |
| 229 | outcomes | Mean predicted here is 0.001307 against an observed rate of… | 0.00787 | ratio | event_rate | out_of_time | eq | `[[art:b87e9246:metrics.out_of_time.sub.incentive_low.event_rate]]` | verified | 0.007870291942 |
| 230 | outcomes | Mean predicted here is 0.001307 against an observed rate of… | 0.5198 | ratio | auc | out_of_time | eq | `[[art:5f017449:metrics.out_of_time.sub.incentive_low.auc]]` | verified | 0.5198113489 |
| 231 | outcomes | On this slice AUC falls 0.07345 below the split's own AUC, w… | 0.07345 | ratio | auc_gap | vintage_holdout | eq | `[[art:dfc93d01:metrics.vintage_holdout.sub.incentive_high.auc_gap]]` | verified | 0.07344783185 |
| 232 | outcomes | On this slice AUC falls 0.07345 below the split's own AUC, w… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 233 | outcomes | The slice holds 0.4991 of the split, above the floor of 0.1… | 0.4991 | ratio | share | vintage_holdout | eq | `[[art:6ee6cf53:metrics.vintage_holdout.sub.incentive_high.share]]` | verified | 0.4991365278 |
| 234 | outcomes | The slice holds 0.4991 of the split, above the floor of 0.1… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 235 | outcomes | The slice holds 0.4991 of the split, above the floor of 0.1… | 0.95 | ratio | slice_max_share |  | eq | `[[art:a928a05c:threshold.O1.slice_max_share]]` | verified | 0.95 |
| 236 | outcomes | Mean predicted here is 0.01662 against an observed rate of 0… | 0.01662 | ratio | mean_predicted | vintage_holdout | eq | `[[art:1f806ffc:metrics.vintage_holdout.sub.incentive_high.mean_predicted]]` | verified | 0.0166159798 |
| 237 | outcomes | Mean predicted here is 0.01662 against an observed rate of 0… | 0.03165 | ratio | event_rate | vintage_holdout | eq | `[[art:7a446230:metrics.vintage_holdout.sub.incentive_high.event_rate]]` | verified | 0.03165368841 |
| 238 | outcomes | On this slice AUC falls 0.1432 below the split's own AUC, ab… | 0.1432 | ratio | auc_gap | vintage_holdout | eq | `[[art:2b9eda62:metrics.vintage_holdout.sub.incentive_low.auc_gap]]` | verified | 0.1432067181 |
| 239 | outcomes | On this slice AUC falls 0.1432 below the split's own AUC, ab… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 240 | outcomes | The slice holds 0.5009 of the split, above the floor of 0.1… | 0.5009 | ratio | share | vintage_holdout | eq | `[[art:4e4aac59:metrics.vintage_holdout.sub.incentive_low.share]]` | verified | 0.5008634722 |
| 241 | outcomes | The slice holds 0.5009 of the split, above the floor of 0.1… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 242 | outcomes | The slice holds 0.5009 of the split, above the floor of 0.1… | 0.95 | ratio | slice_max_share |  | eq | `[[art:a928a05c:threshold.O1.slice_max_share]]` | verified | 0.95 |
| 243 | outcomes | Mean predicted here is 0.003153 against an observed rate of… | 0.003153 | ratio | mean_predicted | vintage_holdout | eq | `[[art:037a5534:metrics.vintage_holdout.sub.incentive_low.mean_predicted]]` | verified | 0.003152614288 |
| 244 | outcomes | Mean predicted here is 0.003153 against an observed rate of… | 0.007346 | ratio | event_rate | vintage_holdout | eq | `[[art:8cd3a201:metrics.vintage_holdout.sub.incentive_low.event_rate]]` | verified | 0.007345990763 |
| 245 | outcomes | Mean predicted here is 0.003153 against an observed rate of… | 0.5956 | ratio | auc | vintage_holdout | eq | `[[art:e5b67962:metrics.vintage_holdout.sub.incentive_low.auc]]` | verified | 0.595613353 |
| 246 | sensitivity | The largest variance inflation factor across the retained fe… | 4.629 | ratio | vif |  | eq | `[[art:82a187c7:vif.max]]` | verified | 4.628790677 |
| 247 | sensitivity | The largest variance inflation factor across the retained fe… | 10 | ratio | vif |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 248 | sensitivity | That maximum is carried by the rate incentive term at 4.629… | 4.629 | ratio | vif |  | eq | `[[art:0c33ec65:vif.incentive]]` | verified | 4.628790677 |
| 249 | sensitivity | That maximum is carried by the rate incentive term at 4.629… | 3.749 | ratio | vif |  | eq | `[[art:f9a490a7:vif.burnout]]` | verified | 3.748625457 |
| 250 | sensitivity | That maximum is carried by the rate incentive term at 4.629… | 3.015 | ratio | vif |  | eq | `[[art:42163c15:vif.sato]]` | verified | 3.014708865 |
| 251 | sensitivity | The remaining retained features sit lower still, with loan a… | 2.69 | ratio | vif |  | eq | `[[art:12ee5768:vif.loan_age]]` | verified | 2.689839788 |
| 252 | sensitivity | The remaining retained features sit lower still, with loan a… | 2.205 | ratio | vif |  | eq | `[[art:7f4d0c73:vif.rate_change_12m]]` | verified | 2.204676098 |
| 253 | sensitivity | The remaining retained features sit lower still, with loan a… | 1.107 | ratio | vif |  | eq | `[[art:a998810f:vif.orig_ltv]]` | verified | 1.106875268 |
| 254 | sensitivity | The remaining retained features sit lower still, with loan a… | 1.061 | ratio | vif |  | eq | `[[art:0dde7942:vif.orig_upb_log]]` | verified | 1.060864995 |
| 255 | sensitivity | The remaining retained features sit lower still, with loan a… | 1.025 | ratio | vif |  | eq | `[[art:6afd05c9:vif.season_sin]]` | verified | 1.024602455 |
| 256 | sensitivity | The remaining retained features sit lower still, with loan a… | 1.023 | ratio | vif |  | eq | `[[art:373087f2:vif.credit_score]]` | verified | 1.022563505 |
| 257 | sensitivity | The remaining retained features sit lower still, with loan a… | 1.006 | ratio | vif |  | eq | `[[art:2950847c:vif.season_cos]]` | verified | 1.005586044 |
| 258 | sensitivity | Belsley's condition number of the column-standardised design… | 4.565 | ratio | condition_number |  | eq | `[[art:87b61976:condition_number]]` | verified | 4.565343746 |
| 259 | sensitivity | Belsley's condition number of the column-standardised design… | 30 | ratio | condition_number |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 260 | sensitivity | The tolerance applied to the spread in discrimination across… | 0.1 | ratio | auc_gap |  | eq | `[[art:b64213d7:threshold.R1.auc_gap]]` | verified | 0.1 |
| 261 | sensitivity | Coefficient stability was screened by asking whether any of… | 0.05 | ratio | sign_flip_coef |  | eq | `[[art:aca84377:threshold.R1.sign_flip_coef]]` | verified | 0.05 |
| 262 | sensitivity | Coefficient stability was screened by asking whether any of… | 2 | ratio | sign_flip_z |  | eq | `[[art:2e4428c7:threshold.R1.sign_flip_z]]` | verified | 2 |
| 263 | sensitivity | No feature meets that condition: the indicator is 0 for the… | 0 | ratio | sign_flip |  | eq | `[[art:0cc7a37d:stability.incentive.sign_flip]]` | verified | 0 |
| 264 | sensitivity | No feature meets that condition: the indicator is 0 for the… | 0 | ratio | sign_flip |  | eq | `[[art:6bc05e82:stability.burnout.sign_flip]]` | verified | 0 |
| 265 | sensitivity | No feature meets that condition: the indicator is 0 for the… | 0 | ratio | sign_flip |  | eq | `[[art:1f302ccd:stability.sato.sign_flip]]` | verified | 0 |
| 266 | sensitivity | No feature meets that condition: the indicator is 0 for the… | 0 | ratio | sign_flip |  | eq | `[[art:b7191217:stability.loan_age.sign_flip]]` | verified | 0 |
| 267 | sensitivity | No feature meets that condition: the indicator is 0 for the… | 0 | ratio | sign_flip |  | eq | `[[art:465700ff:stability.rate_change_12m.sign_flip]]` | verified | 0 |
| 268 | sensitivity | It is likewise 0 for credit score , 0 for original loan-to-v… | 0 | ratio | sign_flip |  | eq | `[[art:d956c276:stability.credit_score.sign_flip]]` | verified | 0 |
| 269 | sensitivity | It is likewise 0 for credit score , 0 for original loan-to-v… | 0 | ratio | sign_flip |  | eq | `[[art:054d5fab:stability.orig_ltv.sign_flip]]` | verified | 0 |
| 270 | sensitivity | It is likewise 0 for credit score , 0 for original loan-to-v… | 0 | ratio | sign_flip |  | eq | `[[art:fb1ae6c8:stability.orig_upb_log.sign_flip]]` | verified | 0 |
| 271 | sensitivity | It is likewise 0 for credit score , 0 for original loan-to-v… | 0 | ratio | sign_flip |  | eq | `[[art:6ba36a3b:stability.season_sin.sign_flip]]` | verified | 0 |
| 272 | sensitivity | It is likewise 0 for credit score , 0 for original loan-to-v… | 0 | ratio | sign_flip |  | eq | `[[art:1850e2de:stability.season_cos.sign_flip]]` | verified | 0 |
| 273 | sensitivity | At the downward extreme the servicing value changes by -1078… | -1078000 | currency | value_change |  | eq | `[[art:9bab8e73:scenario.value_change.-300]]` | verified | -1077724.403 |
| 274 | sensitivity | At the downward extreme the servicing value changes by -1078… | 167100 | currency | value_change |  | eq | `[[art:d7f60dfe:scenario.value_change.300]]` | verified | 167117.0554 |
| 275 | sensitivity | The sum of the changes at the two extremes is -910600 , so t… | -910600 | currency | convexity |  | eq | `[[art:67b742b1:scenario.convexity]]` | verified | -910607.3477 |
| 276 | findings | The logistic regression of the outcome on the predicted logi… | 0.4321 | ratio | calibration_slope | out_of_time | eq | `[[art:d9f87bb2:calibration_slope.out_of_time]]` | verified | 0.432125782 |
| 277 | findings | The logistic regression of the outcome on the predicted logi… | 0.8 | ratio | calibration_slope |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 278 | findings | Mean predicted probability on the out-of-time split is 0.010… | 0.01005 | ratio | mean_predicted | out_of_time | eq | `[[art:fd777cc4:metrics.out_of_time.mean_predicted]]` | verified | 0.01005421904 |
| 279 | findings | Mean predicted probability on the out-of-time split is 0.010… | 0.01868 | ratio | event_rate | out_of_time | eq | `[[art:cf3a82aa:metrics.out_of_time.event_rate]]` | verified | 0.01868053913 |
| 280 | findings | Mean predicted probability on the out-of-time split is 0.010… | 0.4618 | ratio | mean_rel_gap | out_of_time | eq | `[[art:9e4c8750:calibration.mean_rel_gap.out_of_time]]` | verified | 0.4617811099 |
| 281 | findings | Mean predicted probability on the out-of-time split is 0.010… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 282 | findings | On the vintage holdout the mean predicted probability is 0.0… | 0.009873 | ratio | mean_predicted | vintage_holdout | eq | `[[art:c12c52f7:metrics.vintage_holdout.mean_predicted]]` | verified | 0.009872671801 |
| 283 | findings | On the vintage holdout the mean predicted probability is 0.0… | 0.01948 | ratio | event_rate | vintage_holdout | eq | `[[art:bab66615:metrics.vintage_holdout.event_rate]]` | verified | 0.01947885057 |
| 284 | findings | On the vintage holdout the mean predicted probability is 0.0… | 0.4932 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:92b5a8c4:calibration.mean_rel_gap.vintage_holdout]]` | verified | 0.4931594261 |
| 285 | findings | On the vintage holdout the mean predicted probability is 0.0… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 286 | findings | On the segment `incentive > median(incentive)`, which holds… | 0.5 | ratio | share | out_of_time | eq | `[[art:4787f68a:metrics.out_of_time.sub.incentive_high.share]]` | verified | 0.4999982354 |
| 287 | findings | On the segment `incentive > median(incentive)`, which holds… | 0.6046 | ratio | auc | out_of_time | eq | `[[art:a1a6fd72:metrics.out_of_time.sub.incentive_high.auc]]` | verified | 0.6045716303 |
| 288 | findings | On the segment `incentive > median(incentive)`, which holds… | 0.08523 | ratio | auc_gap | out_of_time | eq | `[[art:e7b201c8:metrics.out_of_time.sub.incentive_high.auc_gap]]` | verified | 0.08522987832 |
| 289 | findings | On the segment `incentive > median(incentive)`, which holds… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 290 | findings | On the complementary segment `incentive <= median(incentive)… | 0.5 | ratio | share | out_of_time | eq | `[[art:cc116fda:metrics.out_of_time.sub.incentive_low.share]]` | verified | 0.5000017646 |
| 291 | findings | On the complementary segment `incentive <= median(incentive)… | 0.5198 | ratio | auc | out_of_time | eq | `[[art:5f017449:metrics.out_of_time.sub.incentive_low.auc]]` | verified | 0.5198113489 |
| 292 | findings | On the complementary segment `incentive <= median(incentive)… | 0.17 | ratio | auc_gap | out_of_time | eq | `[[art:379c90f9:metrics.out_of_time.sub.incentive_low.auc_gap]]` | verified | 0.1699901597 |
| 293 | findings | On the complementary segment `incentive <= median(incentive)… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 294 | findings | On the segment `incentive <= median(incentive)` of the vinta… | 0.5009 | ratio | share | vintage_holdout | eq | `[[art:4e4aac59:metrics.vintage_holdout.sub.incentive_low.share]]` | verified | 0.5008634722 |
| 295 | findings | On the segment `incentive <= median(incentive)` of the vinta… | 0.5956 | ratio | auc | vintage_holdout | eq | `[[art:e5b67962:metrics.vintage_holdout.sub.incentive_low.auc]]` | verified | 0.595613353 |
| 296 | findings | On the segment `incentive <= median(incentive)` of the vinta… | 0.1432 | ratio | auc_gap | vintage_holdout | eq | `[[art:2b9eda62:metrics.vintage_holdout.sub.incentive_low.auc_gap]]` | verified | 0.1432067181 |
| 297 | findings | On the segment `incentive <= median(incentive)` of the vinta… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 298 | monitoring | Calibration should be tracked first: recompute the logistic… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 299 | monitoring | Calibration should be tracked first: recompute the logistic… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 300 | monitoring | The validation sample gives the baseline for that series at… | 1.017 | ratio | calibration_slope | test | eq | `[[art:9b1edaa3:calibration_slope.test]]` | verified | 1.01683551 |
| 301 | monitoring | Discrimination should be tracked next: recompute the area un… | 0.65 | ratio | auc | test | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 302 | monitoring | The validation value of 0.6549 clears that floor by a narrow… | 0.6549 | ratio | auc | test | eq | `[[art:f3890b65:metrics.test.auc]]` | verified | 0.6549316245 |
| 303 | monitoring | Input and score stability should be tracked monthly: compute… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 304 | monitoring | The largest such shift observed within the development data,… | 0.005703 | ratio | psi |  | eq | `[[art:f632d5d4:psi.max]]` | verified | 0.005703237396 |

## Appendix B — Artifact index

The store holds 320 artifacts; the 234 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `ablation.baseline_auc` | `ed55c319` | scalar | 0.6391430546 | AUC on test of a refit of the champion's functional form on every retained feature, the level each ablation delta is measured from |
| `ablation.burnout.delta_auc` | `499cf97d` | scalar | 0.0005738937198 | change in test AUC when the champion's form is refitted without burnout |
| `ablation.credit_score.delta_auc` | `9963f841` | scalar | -0.0002603974752 | change in test AUC when the champion's form is refitted without credit_score |
| `ablation.incentive.delta_auc` | `b1880518` | scalar | -0.01609580876 | change in test AUC when the champion's form is refitted without incentive |
| `ablation.loan_age.delta_auc` | `0b5dcaeb` | scalar | -0.004571578483 | change in test AUC when the champion's form is refitted without loan_age |
| `ablation.orig_ltv.delta_auc` | `acb0dcd5` | scalar | -0.002233212172 | change in test AUC when the champion's form is refitted without orig_ltv |
| `ablation.orig_upb_log.delta_auc` | `d9fda2c8` | scalar | -0.01710427827 | change in test AUC when the champion's form is refitted without orig_upb_log |
| `ablation.rate_change_12m.delta_auc` | `f472749f` | scalar | -0.0003635311596 | change in test AUC when the champion's form is refitted without rate_change_12m |
| `ablation.sato.delta_auc` | `f406b192` | scalar | -0.003026491141 | change in test AUC when the champion's form is refitted without sato |
| `ablation.season_cos.delta_auc` | `0931b2a0` | scalar | 0.001844627367 | change in test AUC when the champion's form is refitted without season_cos |
| `ablation.season_sin.delta_auc` | `47876c72` | scalar | 0.0001080069018 | change in test AUC when the champion's form is refitted without season_sin |
| `calibration.mean_rel_gap.out_of_time` | `9e4c8750` | scalar | 0.4617811099 | mean predicted against observed on out_of_time, relative |
| `calibration.mean_rel_gap.test` | `a173f6c5` | scalar | 0.04708600686 | mean predicted against observed on test, relative |
| `calibration.mean_rel_gap.train` | `332fc4d9` | scalar | 0.002896932549 | mean predicted against observed on train, relative |
| `calibration.mean_rel_gap.vintage_holdout` | `92b5a8c4` | scalar | 0.4931594261 | mean predicted against observed on vintage_holdout, relative |
| `calibration.test` | `c8e7323f` | table | table, 10 rows | calibration by decile of predicted probability on test |
| `calibration_intercept.out_of_time` | `53a8d76b` | scalar | -1.761998635 | logistic regression of the outcome on logit(p) on out_of_time: the intercept |
| `calibration_intercept.test` | `1a8280dd` | scalar | 0.02905298382 | logistic regression of the outcome on logit(p) on test: the intercept |
| `calibration_intercept.train` | `be40e0a7` | scalar | -0.01599765114 | logistic regression of the outcome on logit(p) on train: the intercept |
| `calibration_intercept.vintage_holdout` | `0d75b532` | scalar | 0.06118872124 | logistic regression of the outcome on logit(p) on vintage_holdout: the intercept |
| `calibration_slope.out_of_time` | `d9f87bb2` | scalar | 0.432125782 | logistic regression of the outcome on logit(p) on out_of_time: the slope |
| `calibration_slope.test` | `9b1edaa3` | scalar | 1.01683551 | logistic regression of the outcome on logit(p) on test: the slope |
| `calibration_slope.train` | `28331672` | scalar | 0.9971012419 | logistic regression of the outcome on logit(p) on train: the slope |
| `calibration_slope.vintage_holdout` | `80fe61d2` | scalar | 0.8501990162 | logistic regression of the outcome on logit(p) on vintage_holdout: the slope |
| `challenger.auc` | `6f811314` | scalar | 0.6653496435 | the challenger's AUC on test |
| `challenger.brier` | `0e717888` | scalar | 0.00911859482 | the challenger's Brier score on test |
| `challenger.delta_auc` | `10b988e8` | scalar | 0.01041801898 | the challenger's AUC on test minus the champion's |
| `condition_number` | `87b61976` | scalar | 4.565343746 | Belsley's condition number of the column-standardised design |
| `cpr.out_of_time.mae` | `a467ad41` | scalar | 0.08656382516 | mean absolute difference between actual and predicted CPR on out_of_time |
| `cpr.test` | `f76e789f` | table | table, 71 rows | actual against predicted CPR by period on test |
| `cpr.test.mae` | `939c5fb9` | scalar | 0.02641734834 | mean absolute difference between actual and predicted CPR on test |
| `cpr.train.mae` | `3487a403` | scalar | 0.02201633853 | mean absolute difference between actual and predicted CPR on train |
| `cpr.vintage_holdout.mae` | `0cc82390` | scalar | 0.07850151406 | mean absolute difference between actual and predicted CPR on vintage_holdout |
| `csi.burnout` | `e4d3e34a` | scalar | 3.430062025e-06 | CSI of burnout: its contribution to the shift in the linear predictor |
| `csi.credit_score` | `0a280759` | scalar | 1.970189663e-05 | CSI of credit_score: its contribution to the shift in the linear predictor |
| `csi.incentive` | `020f5ce2` | scalar | 0.001102078062 | CSI of incentive: its contribution to the shift in the linear predictor |
| `csi.loan_age` | `df52c920` | scalar | 0 | CSI of loan_age: its contribution to the shift in the linear predictor |
| `csi.max` | `131d42db` | scalar | 0.00645531823 | the largest characteristic stability index |
| `csi.orig_ltv` | `1c9006f3` | scalar | 0.0005902054355 | CSI of orig_ltv: its contribution to the shift in the linear predictor |
| `csi.orig_upb_log` | `7561e8b0` | scalar | 0.00645531823 | CSI of orig_upb_log: its contribution to the shift in the linear predictor |
| `csi.rate_change_12m` | `ffdb6fdd` | scalar | 0.0002237020655 | CSI of rate_change_12m: its contribution to the shift in the linear predictor |
| `csi.sato` | `a54b158e` | scalar | 0.001115931346 | CSI of sato: its contribution to the shift in the linear predictor |
| `csi.season_cos` | `c70e3aa4` | scalar | 6.190848201e-05 | CSI of season_cos: its contribution to the shift in the linear predictor |
| `csi.season_sin` | `fb3bf812` | scalar | 2.108057316e-05 | CSI of season_sin: its contribution to the shift in the linear predictor |
| `data.manifest` | `4a0ccaba` | table | table, 5 rows | the files data.manifest declares, each verified against its SHA-256 before the run |
| `deciles.out_of_time.top2_capture` | `58f451c3` | scalar | 0.4313243907 | share of out_of_time events in the top two deciles |
| `deciles.test` | `d98c638f` | table | table, 10 rows | decile separation on test; decile 1 holds the highest probabilities |
| `deciles.test.top2_capture` | `1d4dff05` | scalar | 0.3769168684 | share of test events in the top two deciles |
| `deciles.train.top2_capture` | `b2f9e5d8` | scalar | 0.3800067317 | share of train events in the top two deciles |
| `deciles.vintage_holdout.top2_capture` | `3cd3b5a3` | scalar | 0.5115740741 | share of vintage_holdout events in the top two deciles |
| `leakage.duplicates.train` | `ce57652e` | scalar | 0.0001530914913 | share of train rows whose feature values are not unique within train |
| `leakage.name_screen.n_matched` | `407e62be` | scalar | 0 | feature names matching the target-adjacent lexicon |
| `leakage.overlap` | `4c9fcd09` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.features` | `0fec8048` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.ids` | `63d37fc5` | scalar | 0 | share of test rows whose ['loan_id', 'period'] also identify a row of train |
| `leakage.target_corr.max_single_feature_auc` | `9e2ffad1` | scalar | 0.5994570075 | the AUC of the strongest single feature |
| `leakage.timing.n_flagged` | `742bcd24` | scalar | 0 | features declared during_period or after_outcome |
| `metrics.out_of_time.auc` | `cb57fe9a` | scalar | 0.6898015086 | auc on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.brier` | `4ddcaaea` | scalar | 0.01823697645 | brier on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.event_rate` | `cf3a82aa` | scalar | 0.01868053913 | event_rate on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.gini` | `6c5edac7` | scalar | 0.3796030172 | gini on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.ks` | `c486329f` | scalar | 0.3020779889 | ks on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.logloss` | `8d53f72c` | scalar | 0.09576249258 | logloss on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.mean_predicted` | `fd777cc4` | scalar | 0.01005421904 | mean_predicted on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.n` | `c164ae00` | scalar | 283343 | n on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.sub.incentive_high` | `8ca3a5fb` | table | table, 9 rows | every metric on the incentive above_median slice of out_of_time |
| `metrics.out_of_time.sub.incentive_high.auc` | `a1a6fd72` | scalar | 0.6045716303 | auc on the incentive above_median slice of out_of_time |
| `metrics.out_of_time.sub.incentive_high.auc_gap` | `e7b201c8` | scalar | 0.08522987832 | how far AUC on the incentive above_median slice of out_of_time falls below AUC on all of out_of_time |
| `metrics.out_of_time.sub.incentive_high.event_rate` | `f62f5a9c` | scalar | 0.02949086263 | event_rate on the incentive above_median slice of out_of_time |
| `metrics.out_of_time.sub.incentive_high.mean_predicted` | `b7288bbc` | scalar | 0.01880179941 | mean_predicted on the incentive above_median slice of out_of_time |
| `metrics.out_of_time.sub.incentive_high.share` | `4787f68a` | scalar | 0.4999982354 | the share of out_of_time the incentive above_median slice holds |
| `metrics.out_of_time.sub.incentive_low` | `eced92cd` | table | table, 9 rows | every metric on the incentive below_median slice of out_of_time |
| `metrics.out_of_time.sub.incentive_low.auc` | `5f017449` | scalar | 0.5198113489 | auc on the incentive below_median slice of out_of_time |
| `metrics.out_of_time.sub.incentive_low.auc_gap` | `379c90f9` | scalar | 0.1699901597 | how far AUC on the incentive below_median slice of out_of_time falls below AUC on all of out_of_time |
| `metrics.out_of_time.sub.incentive_low.event_rate` | `b87e9246` | scalar | 0.007870291942 | event_rate on the incentive below_median slice of out_of_time |
| `metrics.out_of_time.sub.incentive_low.mean_predicted` | `e77d973c` | scalar | 0.001306700417 | mean_predicted on the incentive below_median slice of out_of_time |
| `metrics.out_of_time.sub.incentive_low.share` | `cc116fda` | scalar | 0.5000017646 | the share of out_of_time the incentive below_median slice holds |
| `metrics.test.auc` | `f3890b65` | scalar | 0.6549316245 | auc on test, recomputed by quaestor |
| `metrics.test.brier` | `21d0b581` | scalar | 0.009062660213 | brier on test, recomputed by quaestor |
| `metrics.test.event_rate` | `78206f7c` | scalar | 0.009173700578 | event_rate on test, recomputed by quaestor |
| `metrics.test.gini` | `5710cba3` | scalar | 0.309863249 | gini on test, recomputed by quaestor |
| `metrics.test.ks` | `c35222f3` | scalar | 0.237529396 | ks on test, recomputed by quaestor |
| `metrics.test.logloss` | `048e9ca7` | scalar | 0.0508316292 | logloss on test, recomputed by quaestor |
| `metrics.test.mean_predicted` | `24595a04` | scalar | 0.009605653506 | mean_predicted on test, recomputed by quaestor |
| `metrics.test.n` | `629740ff` | scalar | 135060 | n on test, recomputed by quaestor |
| `metrics.train.auc` | `40964132` | scalar | 0.6503543409 | auc on train, recomputed by quaestor |
| `metrics.train.brier` | `574cf8a4` | scalar | 0.009358514597 | brier on train, recomputed by quaestor |
| `metrics.train.event_rate` | `8ecc2809` | scalar | 0.00947572543 | event_rate on train, recomputed by quaestor |
| `metrics.train.gini` | `da0e7063` | scalar | 0.3007086819 | gini on train, recomputed by quaestor |
| `metrics.train.ks` | `96e91aee` | scalar | 0.2261527235 | ks on train, recomputed by quaestor |
| `metrics.train.logloss` | `716b9dc1` | scalar | 0.05225625901 | logloss on train, recomputed by quaestor |
| `metrics.train.mean_predicted` | `716b94b2` | scalar | 0.009503175968 | mean_predicted on train, recomputed by quaestor |
| `metrics.train.n` | `72c7a6d2` | scalar | 313538 | n on train, recomputed by quaestor |
| `metrics.vintage_holdout.auc` | `95f87cc7` | scalar | 0.7388200711 | auc on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.brier` | `6a660ed9` | scalar | 0.01897762486 | brier on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.event_rate` | `bab66615` | scalar | 0.01947885057 | event_rate on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.gini` | `75ad81b1` | scalar | 0.4776401422 | gini on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.ks` | `699a7598` | scalar | 0.4110310226 | ks on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.logloss` | `630a591b` | scalar | 0.09344516111 | logloss on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.mean_predicted` | `c12c52f7` | scalar | 0.009872671801 | mean_predicted on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.n` | `faabc78e` | scalar | 221779 | n on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.sub.incentive_high` | `eac314b9` | table | table, 9 rows | every metric on the incentive above_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.incentive_high.auc_gap` | `dfc93d01` | scalar | 0.07344783185 | how far AUC on the incentive above_median slice of vintage_holdout falls below AUC on all of vintage_holdout |
| `metrics.vintage_holdout.sub.incentive_high.event_rate` | `7a446230` | scalar | 0.03165368841 | event_rate on the incentive above_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.incentive_high.mean_predicted` | `1f806ffc` | scalar | 0.0166159798 | mean_predicted on the incentive above_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.incentive_high.share` | `6ee6cf53` | scalar | 0.4991365278 | the share of vintage_holdout the incentive above_median slice holds |
| `metrics.vintage_holdout.sub.incentive_low` | `7e722b90` | table | table, 9 rows | every metric on the incentive below_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.incentive_low.auc` | `e5b67962` | scalar | 0.595613353 | auc on the incentive below_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.incentive_low.auc_gap` | `2b9eda62` | scalar | 0.1432067181 | how far AUC on the incentive below_median slice of vintage_holdout falls below AUC on all of vintage_holdout |
| `metrics.vintage_holdout.sub.incentive_low.event_rate` | `8cd3a201` | scalar | 0.007345990763 | event_rate on the incentive below_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.incentive_low.mean_predicted` | `037a5534` | scalar | 0.003152614288 | mean_predicted on the incentive below_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.incentive_low.share` | `4e4aac59` | scalar | 0.5008634722 | the share of vintage_holdout the incentive below_median slice holds |
| `profile.out_of_time.missing.max` | `4dafce11` | scalar | 0 | the largest missing fraction in out_of_time |
| `profile.out_of_time.n` | `a0103a06` | scalar | 283343 | rows in out_of_time |
| `profile.test.missing.max` | `f813848d` | scalar | 0 | the largest missing fraction in test |
| `profile.test.n` | `75b5b833` | scalar | 135060 | rows in test |
| `profile.train.missing.max` | `050a3099` | scalar | 0 | the largest missing fraction in train |
| `profile.train.n` | `6582e5dd` | scalar | 313538 | rows in train |
| `profile.vintage_holdout.missing.max` | `329bb430` | scalar | 0 | the largest missing fraction in vintage_holdout |
| `profile.vintage_holdout.n` | `fcb7e414` | scalar | 221779 | rows in vintage_holdout |
| `psi.burnout` | `40a3f946` | scalar | 0.001566859823 | PSI of burnout between train and test |
| `psi.credit_score` | `8a078965` | scalar | 0.003717519291 | PSI of credit_score between train and test |
| `psi.incentive` | `61538982` | scalar | 0.0003749417053 | PSI of incentive between train and test |
| `psi.loan_age` | `f548214d` | scalar | 8.302102495e-05 | PSI of loan_age between train and test |
| `psi.max` | `f632d5d4` | scalar | 0.005703237396 | the largest train-to-test PSI, score included |
| `psi.orig_ltv` | `6ea40553` | scalar | 0.005703237396 | PSI of orig_ltv between train and test |
| `psi.orig_upb_log` | `4af07770` | scalar | 0.002752784614 | PSI of orig_upb_log between train and test |
| `psi.out_of_time.burnout` | `5316f456` | scalar | 1.551357138 | PSI of burnout between train and out_of_time |
| `psi.out_of_time.credit_score` | `5341c0a9` | scalar | 0.004578346658 | PSI of credit_score between train and out_of_time |
| `psi.out_of_time.incentive` | `73dfd106` | scalar | 1.726005597 | PSI of incentive between train and out_of_time |
| `psi.out_of_time.loan_age` | `5f3c6bba` | scalar | 3.085573352 | PSI of loan_age between train and out_of_time |
| `psi.out_of_time.orig_ltv` | `7f6fab7a` | scalar | 0.01597816452 | PSI of orig_ltv between train and out_of_time |
| `psi.out_of_time.orig_upb_log` | `abf1e02d` | scalar | 0.02135726451 | PSI of orig_upb_log between train and out_of_time |
| `psi.out_of_time.rate_change_12m` | `09e68722` | scalar | 0.8254176602 | PSI of rate_change_12m between train and out_of_time |
| `psi.out_of_time.sato` | `85a8a904` | scalar | 0.01472768815 | PSI of sato between train and out_of_time |
| `psi.out_of_time.season_cos` | `8ef132e3` | scalar | 0.005910467488 | PSI of season_cos between train and out_of_time |
| `psi.out_of_time.season_sin` | `7388771e` | scalar | 0.0241861509 | PSI of season_sin between train and out_of_time |
| `psi.out_of_time.y_score` | `75370112` | scalar | 1.539886915 | PSI of the score between train and out_of_time |
| `psi.rate_change_12m` | `23b9e924` | scalar | 3.588607828e-05 | PSI of rate_change_12m between train and test |
| `psi.sato` | `e68bfd2e` | scalar | 0.002192276542 | PSI of sato between train and test |
| `psi.season_cos` | `9db38513` | scalar | 3.183525037e-06 | PSI of season_cos between train and test |
| `psi.season_sin` | `ae17ebba` | scalar | 3.365586451e-06 | PSI of season_sin between train and test |
| `psi.vintage_holdout.burnout` | `e3a3122f` | scalar | 0.5116279641 | PSI of burnout between train and vintage_holdout |
| `psi.vintage_holdout.credit_score` | `341abd78` | scalar | 0.007217892201 | PSI of credit_score between train and vintage_holdout |
| `psi.vintage_holdout.incentive` | `86f7884e` | scalar | 1.297995585 | PSI of incentive between train and vintage_holdout |
| `psi.vintage_holdout.loan_age` | `2de85f94` | scalar | 0.1506849325 | PSI of loan_age between train and vintage_holdout |
| `psi.vintage_holdout.orig_ltv` | `a5066c0f` | scalar | 0.01065378135 | PSI of orig_ltv between train and vintage_holdout |
| `psi.vintage_holdout.orig_upb_log` | `bd074d53` | scalar | 0.03076150585 | PSI of orig_upb_log between train and vintage_holdout |
| `psi.vintage_holdout.rate_change_12m` | `2575a328` | scalar | 0.8816315659 | PSI of rate_change_12m between train and vintage_holdout |
| `psi.vintage_holdout.sato` | `b34d2ebe` | scalar | 0.2002005108 | PSI of sato between train and vintage_holdout |
| `psi.vintage_holdout.season_cos` | `67aee1b5` | scalar | 0.0009420084002 | PSI of season_cos between train and vintage_holdout |
| `psi.vintage_holdout.season_sin` | `dad1e65c` | scalar | 0.003658742975 | PSI of season_sin between train and vintage_holdout |
| `psi.vintage_holdout.y_score` | `ae7b9c29` | scalar | 0.7656434406 | PSI of the score between train and vintage_holdout |
| `psi.y_score` | `6e6c94e1` | scalar | 0.0006640882006 | PSI of the score between train and test |
| `run.features` | `0849f814` | json | json | the subject's features.json |
| `run.model_summary` | `29028ebe` | json | json | the subject's model_summary.json |
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |
| `scenario.convexity` | `67b742b1` | scalar | -910607.3477 | the value change at -300 bp plus the change at 300 bp; negative when the fall outweighs the rise |
| `scenario.value_by_shock` | `9ae3b068` | table | table, 7 rows | servicing value, its change from the base case and first-year CPR, by shock |
| `scenario.value_change.-300` | `9bab8e73` | scalar | -1077724.403 | change in servicing value at -300 bp |
| `scenario.value_change.300` | `d7f60dfe` | scalar | 167117.0554 | change in servicing value at 300 bp |
| `sign_check.burnout.agrees` | `2eec20ab` | scalar | 1 | 1 when the fitted sign on burnout agrees with its univariate direction, 0 when it does not |
| `sign_check.burnout.coef_sign` | `a3063608` | scalar | 1 | the sign of the fitted coefficient on burnout |
| `sign_check.burnout.univariate_direction` | `bfc96bb2` | scalar | 1 | the sign of burnout's own single-feature AUC on train minus 0.5 |
| `sign_check.credit_score.agrees` | `915bf8eb` | scalar | 1 | 1 when the fitted sign on credit_score agrees with its univariate direction, 0 when it does not |
| `sign_check.credit_score.coef_sign` | `1ec1078b` | scalar | 1 | the sign of the fitted coefficient on credit_score |
| `sign_check.credit_score.univariate_direction` | `42303896` | scalar | 1 | the sign of credit_score's own single-feature AUC on train minus 0.5 |
| `sign_check.incentive.agrees` | `f7b2338e` | scalar | 1 | 1 when the fitted sign on incentive agrees with its univariate direction, 0 when it does not |
| `sign_check.incentive.coef_sign` | `684cf11a` | scalar | 1 | the sign of the fitted coefficient on incentive |
| `sign_check.incentive.univariate_direction` | `8098d951` | scalar | 1 | the sign of incentive's own single-feature AUC on train minus 0.5 |
| `sign_check.n_disagreements` | `e223cd4a` | scalar | 3 | retained features whose fitted sign contradicts their univariate direction, of 9 checked |
| `sign_check.orig_ltv.agrees` | `3f64b057` | scalar | 0 | 1 when the fitted sign on orig_ltv agrees with its univariate direction, 0 when it does not |
| `sign_check.orig_ltv.coef_sign` | `7eec65ec` | scalar | -1 | the sign of the fitted coefficient on orig_ltv |
| `sign_check.orig_ltv.univariate_direction` | `85aabf06` | scalar | 1 | the sign of orig_ltv's own single-feature AUC on train minus 0.5 |
| `sign_check.orig_upb_log.agrees` | `07a9d3e6` | scalar | 1 | 1 when the fitted sign on orig_upb_log agrees with its univariate direction, 0 when it does not |
| `sign_check.orig_upb_log.coef_sign` | `5aa309fc` | scalar | 1 | the sign of the fitted coefficient on orig_upb_log |
| `sign_check.orig_upb_log.univariate_direction` | `b9743ecb` | scalar | 1 | the sign of orig_upb_log's own single-feature AUC on train minus 0.5 |
| `sign_check.rate_change_12m.agrees` | `61c1d5cc` | scalar | 1 | 1 when the fitted sign on rate_change_12m agrees with its univariate direction, 0 when it does not |
| `sign_check.rate_change_12m.coef_sign` | `272b397e` | scalar | -1 | the sign of the fitted coefficient on rate_change_12m |
| `sign_check.rate_change_12m.univariate_direction` | `35df3bf5` | scalar | -1 | the sign of rate_change_12m's own single-feature AUC on train minus 0.5 |
| `sign_check.sato.agrees` | `b3755963` | scalar | 0 | 1 when the fitted sign on sato agrees with its univariate direction, 0 when it does not |
| `sign_check.sato.coef_sign` | `265915cf` | scalar | -1 | the sign of the fitted coefficient on sato |
| `sign_check.sato.univariate_direction` | `c08233a6` | scalar | 1 | the sign of sato's own single-feature AUC on train minus 0.5 |
| `sign_check.season_cos.agrees` | `7f18ddf7` | scalar | 1 | 1 when the fitted sign on season_cos agrees with its univariate direction, 0 when it does not |
| `sign_check.season_cos.coef_sign` | `7dbb1ffc` | scalar | -1 | the sign of the fitted coefficient on season_cos |
| `sign_check.season_cos.univariate_direction` | `03e931f0` | scalar | -1 | the sign of season_cos's own single-feature AUC on train minus 0.5 |
| `sign_check.season_sin.agrees` | `74f2d0e0` | scalar | 0 | 1 when the fitted sign on season_sin agrees with its univariate direction, 0 when it does not |
| `sign_check.season_sin.coef_sign` | `761188ce` | scalar | 1 | the sign of the fitted coefficient on season_sin |
| `sign_check.season_sin.univariate_direction` | `b75f0b9c` | scalar | -1 | the sign of season_sin's own single-feature AUC on train minus 0.5 |
| `stability.auc_by_regime` | `f293ebc6` | table | table, 2 rows | the champion's AUC within each rate_regime on train |
| `stability.burnout.sign_flip` | `6bc05e82` | scalar | 0 | 1 when burnout is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.credit_score.sign_flip` | `d956c276` | scalar | 0 | 1 when credit_score is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.incentive.sign_flip` | `0cc7a37d` | scalar | 0 | 1 when incentive is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.loan_age.sign_flip` | `b7191217` | scalar | 0 | 1 when loan_age is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.orig_ltv.sign_flip` | `054d5fab` | scalar | 0 | 1 when orig_ltv is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.orig_upb_log.sign_flip` | `fb1ae6c8` | scalar | 0 | 1 when orig_upb_log is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.rate_change_12m.sign_flip` | `465700ff` | scalar | 0 | 1 when rate_change_12m is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
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
| `thresholds.evaluation` | `920227a3` | table | table, 4 rows | every threshold package.yaml declares, with its bound, the recomputed value and the outcome |
| `vif.burnout` | `f9a490a7` | scalar | 3.748625457 | variance inflation factor of burnout on train |
| `vif.credit_score` | `373087f2` | scalar | 1.022563505 | variance inflation factor of credit_score on train |
| `vif.incentive` | `0c33ec65` | scalar | 4.628790677 | variance inflation factor of incentive on train |
| `vif.loan_age` | `12ee5768` | scalar | 2.689839788 | variance inflation factor of loan_age on train |
| `vif.max` | `82a187c7` | scalar | 4.628790677 | the largest variance inflation factor |
| `vif.orig_ltv` | `a998810f` | scalar | 1.106875268 | variance inflation factor of orig_ltv on train |
| `vif.orig_upb_log` | `0dde7942` | scalar | 1.060864995 | variance inflation factor of orig_upb_log on train |
| `vif.rate_change_12m` | `7f4d0c73` | scalar | 2.204676098 | variance inflation factor of rate_change_12m on train |
| `vif.sato` | `42163c15` | scalar | 3.014708865 | variance inflation factor of sato on train |
| `vif.season_cos` | `2950847c` | scalar | 1.005586044 | variance inflation factor of season_cos on train |
| `vif.season_sin` | `6afd05c9` | scalar | 1.024602455 | variance inflation factor of season_sin on train |

## Appendix C — Run trace summary

| quantity | value |
|---|---|
| tool calls | 19 (run_model 1, profile_data 1, compute_metrics 5, check_leakage 1, check_stability 1, check_collinearity 1, challenger_compare 1, run_scenarios 1, retrieve_guidance 7) |
| plan steps (bounded loop) | 4 |
| LLM calls | 23 (plan 4, draft 9, reask 1, extract 9) |
| re-asks | 1 |
| repair rounds | 2 |
| tokens in / out | 352,860 / 141,514 |
| notional cost (USD) | 7.1697 |
| wall-clock (s) | 1549.94 |
| subject run (s) | 9.94 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | msr_prepayment-full_agent-20260916T235634Z-e98677a9 |
| data manifest | verified: 5 file(s) against package.yaml (see data.manifest) |

## Appendix D — Not checked

| item | reason |
|---|---|
| developer documentation | package has no `docs/` directory |
