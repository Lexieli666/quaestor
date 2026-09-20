---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: msr_prepayment
version: "1.0"
model_type: discrete_time_hazard
configuration: full_agent
model: claude-opus-5[1m]
run_id: msr_prepayment-full_agent-20260920T173052Z-e61d346a
data_mode: synthetic
synthetic_n: 2000
grounding_precision_pre: 0.9974
grounding_precision_post: 1.0000
n_claims: 379
n_findings_by_severity: {high: 0, medium: 1, low: 0, info: 0}
generated: "2026-09-20T17:30:52Z"
illustrative: false
---

# Validation report — `msr_prepayment` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `msr_prepayment` v1.0 | `full_agent` | claude-opus-5[1m] | synthetic, n = 2000 | 0.9974 → 1.0000 | 0 / 1 / 0 / 0 |
<!-- quaestor:renderer:end -->

The subject of this report is the model package msr_prepayment, version 1.0, a loan-level model that predicts the probability a mortgage prepays over the outcome window, and the report is organised around the validation expectations of the Federal Reserve's model risk management guidance [[reg:SR26-2:V]].
The validation re-executed the packaged scoring path and recomputed every performance quantity reported below from the scored rows, under the wall-clock cap of 300 [[art:2ad8d1a5:runtime.max_seconds]] seconds that the package manifest declares.
The development split carries 36013 [[art:6fdfeabb:metrics.train.n]] rows and the held-out test split carries 15382 [[art:e55953e1:metrics.test.n]] rows, consistent with the row counts profiled from the delivered data at 36013 [[art:c5ebd9c9:profile.train.n]] and 15382 [[art:e3abc1b8:profile.test.n]] respectively.
Two further splits extend the evidence beyond the development sample: the out-of-time split at 12257 [[art:7898809e:metrics.out_of_time.n]] rows and the vintage holdout at 32177 [[art:37a92951:metrics.vintage_holdout.n]] rows.

Against the developer-declared thresholds, the model passes on each one that the manifest sets.
Discrimination on test stands at 0.7758 [[art:2f4cab3e:metrics.test.auc]], above the declared floor of 0.65 [[art:fececac1:threshold.package.auc.test.min]].
The calibration slope on test is 0.9537 [[art:f8ef2beb:calibration_slope.test]], inside the declared band running from 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] to 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The largest population stability index measured from development to test is 0.06189 [[art:c2e8c8fd:psi.max]], below the declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].

Outcomes analysis reaching beyond the declared bounds is the part of the review that speaks to reliability in use [[reg:SR26-2:V.1.b]], and it is there that the calibration evidence spreads out across splits.
The calibration slope is 1.015 [[art:ffabb935:calibration_slope.train]] on the development split and 1.066 [[art:ea7d5696:calibration_slope.out_of_time]] out of time, while on the vintage holdout it falls to 0.8562 [[art:010c0ec4:calibration_slope.vintage_holdout]], the furthest from unity of the four.
On the level of the predictions rather than their ranking, mean predicted stands at 0.03802 [[art:122af437:metrics.test.mean_predicted]] on test against an observed event rate of 0.008061 [[art:570cc08a:metrics.test.event_rate]], and on the vintage holdout at 0.02582 [[art:348107ae:metrics.vintage_holdout.mean_predicted]] against an observed rate of 0.004817 [[art:e3590a16:metrics.vintage_holdout.event_rate]], predicted above observed in both.
The challenger scored on test lands below the champion on discrimination, by -0.04213 [[art:1e990f53:challenger.delta_auc]] in AUC.
The design is well conditioned on the collinearity diagnostics, with a largest variance inflation factor of 4.976 [[art:f9e0db60:vif.max]] and a condition number of 4.943 [[art:4f06a3c5:condition_number]], and the largest characteristic stability index is 0.03331 [[art:a8ca288d:csi.max]].

This validation published F-001, a C1 calibration finding at medium severity, raised by the metrics computation; it is written out in full in section 6.

## 2. Conceptual soundness

Assessing conceptual soundness here means examining the model's design, construction and developmental evidence, using interpretability measures and benchmarking against an alternative model alongside any evaluation of theoretical construction [[reg:SR26-2:V.1.a]].

The champion in this package is a logistic model of monthly prepayment, built as a linear index over loan characteristics, rate-environment terms and seasonality, with loan age entered through a four-term spline rather than a single linear effect.
It was fitted with an intercept of -3.836 [[art:a65c5723:run.model_summary#intercept]] on 36013 [[art:a65c5723:run.model_summary#n_train]] loan-months contributed by 934 [[art:a65c5723:run.model_summary#n_train_loans]] loans, so the effective number of independent units behind the fit is much smaller than the row count.

The feature inventory carries 12 [[art:61276a96:run.features#n]] features in total, of which 5 [[art:61276a96:run.features#at_origination]] are known at origination and 7 [[art:61276a96:run.features#before_period_start]] are known before the start of the performance period.
No feature is dated to the performance period itself, at 0 [[art:61276a96:run.features#during_period]], and none is dated after the outcome, at 0 [[art:61276a96:run.features#after_outcome]].
On the timing declarations as they stand, every input is observable before the month whose prepayment is being predicted, which is the alignment this use requires.

The developer's own collinearity screen dropped two candidates against a variance inflation threshold of 10 [[art:a65c5723:run.model_summary#vif_threshold]].
The rate-change term was removed at 12.38 [[art:a65c5723:run.model_summary#removed.rate_change_12m.vif]], which sits modestly above that threshold and overlaps with the refinance incentive term that was retained.
The log beginning-of-month balance was removed at 40090 [[art:a65c5723:run.model_summary#removed.bom_balance_log.vif]], a value far above the threshold and consistent with that variable being very nearly a deterministic function of original balance and loan age, both of which the model keeps.
Removing a near-duplicate of retained inputs is a defensible screen, but it means the retained original-balance and loan-age terms now absorb whatever the current balance would have carried.

The largest fitted coefficient is on the refinance incentive at 1.228 [[art:a65c5723:run.model_summary#coefficients.incentive.value]], followed by the first loan-age spline term at 0.7963 [[art:a65c5723:run.model_summary#coefficients.loan_age_spline_1.value]] and the credit score at 0.397 [[art:a65c5723:run.model_summary#coefficients.credit_score.value]].
The remaining sizeable terms are the fourth loan-age spline term at -0.3846 [[art:a65c5723:run.model_summary#coefficients.loan_age_spline_4.value]], the note rate at -0.3355 [[art:a65c5723:run.model_summary#coefficients.note_rate.value]], the log original balance at 0.2928 [[art:a65c5723:run.model_summary#coefficients.orig_upb_log.value]] and the original loan-to-value ratio at -0.2355 [[art:a65c5723:run.model_summary#coefficients.orig_ltv.value]].
The smaller terms are the cosine seasonal term at -0.1303 [[art:a65c5723:run.model_summary#coefficients.season_cos.value]], the second loan-age spline term at 0.125 [[art:a65c5723:run.model_summary#coefficients.loan_age_spline_2.value]], the third at -0.08435 [[art:a65c5723:run.model_summary#coefficients.loan_age_spline_3.value]], the sine seasonal term at 0.06389 [[art:a65c5723:run.model_summary#coefficients.season_sin.value]], burnout at -0.0107 [[art:a65c5723:run.model_summary#coefficients.burnout.value]] and the spread at origination at -0.00802 [[art:a65c5723:run.model_summary#coefficients.sato.value]].

On subject-matter expectations, the dominant terms behave as prepayment modelling would lead one to expect.
A positive incentive coefficient means borrowers refinance more when the rate gap favours them, and its fitted sign of 1 [[art:684cf11a:sign_check.incentive.coef_sign]] matches its own univariate direction of 1 [[art:8098d951:sign_check.incentive.univariate_direction]], recorded as agreement at 1 [[art:f7b2338e:sign_check.incentive.agrees]].
Higher credit scores are conventionally associated with a greater ability to refinance, and the fitted sign of 1 [[art:1ec1078b:sign_check.credit_score.coef_sign]] matches the univariate direction of 1 [[art:42303896:sign_check.credit_score.univariate_direction]], with agreement at 1 [[art:915bf8eb:sign_check.credit_score.agrees]].
Larger original balances give a larger dollar saving from any given rate gap, and the fitted sign of 1 [[art:5aa309fc:sign_check.orig_upb_log.coef_sign]] agrees with the univariate direction of 1 [[art:b9743ecb:sign_check.orig_upb_log.univariate_direction]], at 1 [[art:07a9d3e6:sign_check.orig_upb_log.agrees]].
Higher original loan-to-value impedes refinancing, and the negative fitted sign of -1 [[art:7eec65ec:sign_check.orig_ltv.coef_sign]] agrees with the univariate direction of -1 [[art:76dbc708:sign_check.orig_ltv.univariate_direction]], at 1 [[art:7021aeb0:sign_check.orig_ltv.agrees]].
Both seasonal terms also agree with their univariate directions, the sine term at 1 [[art:e110f357:sign_check.season_sin.agrees]] and the cosine term at 1 [[art:7f18ddf7:sign_check.season_cos.agrees]].

Three [[art:e223cd4a:sign_check.n_disagreements]] retained features carry a fitted sign that contradicts the direction of their own single-feature relationship with the outcome on train, and each is set out below with the discrimination it carries, so that a reversal on a term the model leans on can be told apart from one on a term it barely uses.
Ablation deltas are measured from a refit of the champion's form on every retained feature scoring 0.7673 [[art:54367df6:ablation.baseline_auc]] on test.

The note rate is fitted negative at -1 [[art:aecf7ccb:sign_check.note_rate.coef_sign]] against a univariate direction of 1 [[art:61f6e1ac:sign_check.note_rate.univariate_direction]], recorded as disagreement at 0 [[art:a453463d:sign_check.note_rate.agrees]].
On its own, a higher note rate goes with more prepayment, which is the standard refinance story; conditional on the incentive term the fitted effect points the other way, which is the behaviour one expects when the incentive variable is constructed from the note rate and the market rate and so already carries the refinance channel.
Dropping it moves test discrimination by -0.002585 [[art:14558b82:ablation.note_rate.delta_auc]], so the model is drawing a small but non-zero amount of discrimination from it, and the reversal is best read as a decomposition of the rate effect between two correlated terms rather than as an independent claim that higher-rate borrowers prepay less.

The spread at origination is fitted negative at -1 [[art:265915cf:sign_check.sato.coef_sign]] against a univariate direction of 1 [[art:c08233a6:sign_check.sato.univariate_direction]], recorded as disagreement at 0 [[art:b3755963:sign_check.sato.agrees]].
Removing it changes test discrimination by 0.0005201 [[art:57703504:ablation.sato.delta_auc]], a move in the direction of a slightly better score without the feature, so the sign reversal sits on a term the champion is not relying on for discrimination.

Burnout is fitted negative at -1 [[art:dcfb2de4:sign_check.burnout.coef_sign]] against a univariate direction of 1 [[art:bfc96bb2:sign_check.burnout.univariate_direction]], recorded as disagreement at 0 [[art:56826e40:sign_check.burnout.agrees]].
Here the fitted sign is the one prepayment practice expects, since a pool that has already had repeated refinance opportunities responds less to the next one, and the univariate direction most likely reflects burnout rising alongside seasoning and exposure to favourable rates rather than a causal relationship.
Removing it changes test discrimination by -0.0001876 [[art:3cba039b:ablation.burnout.delta_auc]], the smallest of the three in magnitude, so the model places very little weight on it either way.

Among the terms whose signs agree, the ablation evidence is concentrated in a few places: the incentive term at -0.04117 [[art:78108590:ablation.incentive.delta_auc]], the log original balance at -0.01927 [[art:0ddb11a9:ablation.orig_upb_log.delta_auc]] and the credit score at -0.01474 [[art:9bdeb0df:ablation.credit_score.delta_auc]] each carry materially more discrimination than the remaining features.
The original loan-to-value ratio contributes -0.002294 [[art:57ea66c5:ablation.orig_ltv.delta_auc]], and the two seasonal terms contribute -0.0004826 [[art:a288439d:ablation.season_cos.delta_auc]] and -0.0003885 [[art:e54c8581:ablation.season_sin.delta_auc]].
Loan age scores 0.0008166 [[art:be669163:ablation.loan_age.delta_auc]] when the spline is refitted out, meaning test discrimination does not fall without it, which is worth weighing against the size of the spline coefficients and the role seasoning is assumed to play in the design.

On effective challenge, the champion scores 0.7758 [[art:2f4cab3e:metrics.test.auc]] on test with a Brier score of 0.009864 [[art:1e4aab51:metrics.test.brier]].
The challenger scores 0.7337 [[art:705b66f0:challenger.auc]] on test with a Brier score of 0.00863 [[art:85a89ef9:challenger.brier]], so it discriminates worse than the champion while its Brier score is the lower of the two.
The difference in discrimination is -0.04213 [[art:1e990f53:challenger.delta_auc]], and the threshold that decides whether a challenger difference matters is a challenger lead of 0.03 [[art:e042774c:threshold.E1.delta_auc]].
The observed difference is negative and therefore not a lead at all, so it falls short of that threshold and the challenge does not displace the champion on discrimination.
Because the two Brier scores point the other way from the two AUCs, the challenge supports retaining the champion on ranking ability rather than on calibration, and the comparison made here is the difference in AUC, not a ratio.

Taken together, the design is coherent for its stated purpose: the inputs are timed ahead of the outcome, the collinearity screen removed a near-redundant balance term and a rate-change term that overlapped with the retained incentive, the dominant coefficients point the way prepayment behaviour would suggest, and the challenger does not beat the champion by the margin that would matter.
The qualifications a reader should carry forward are the small number of distinct loans behind the fit, the three sign reversals set out above with the discrimination each carries, and the loan-age spline whose ablation does not show it contributing to test discrimination despite its prominence in the functional form.

## 3. Data integrity and drift

Sound development practice includes a critical assessment of data quality, relevance, and inputs alongside out-of-sample and out-of-time testing, and the screens below examine the splits on which this model was fitted and evaluated [[reg:SR26-2:IV.1]].

### Missingness

The training split holds 36013 rows [[art:c5ebd9c9:profile.train.n]], the test split 15382 rows [[art:e3abc1b8:profile.test.n]], the vintage holdout 32177 rows [[art:426e712a:profile.vintage_holdout.n]], and the out-of-time split 12257 rows [[art:fa39c5cf:profile.out_of_time.n]].
The largest missing fraction over any column is 0 [[art:050a3099:profile.train.missing.max]] in the training split, 0 [[art:f813848d:profile.test.missing.max]] in the test split, 0 [[art:329bb430:profile.vintage_holdout.missing.max]] in the vintage holdout, and 0 [[art:4dafce11:profile.out_of_time.missing.max]] in the out-of-time split.
The declared bound on the missingness gap between splits is 0.1 [[art:9cce25ea:threshold.D1.missing_gap]], and because the four split maxima are identical no pair of splits differs enough on missingness to approach that bound.
No column in any split is therefore carrying an imputation burden that could differ by split and act as a silent covariate.

### Population stability

The declared stability bound is 0.25 [[art:278b9016:threshold.S1.psi]], stated for the training split against the test split, and the package declaration carries the same value at 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
The train-to-test indices are as follows.

- burnout: 0.004614 [[art:9dc7ecc2:psi.burnout]]
- credit_score: 0.06189 [[art:7e87527c:psi.credit_score]]
- incentive: 0.0009923 [[art:2da5570f:psi.incentive]]
- loan_age: 0.0001994 [[art:2202b157:psi.loan_age]]
- note_rate: 0.01371 [[art:ecc6adf3:psi.note_rate]]
- orig_ltv: 0.03617 [[art:cd1ff136:psi.orig_ltv]]
- orig_upb_log: 0.04817 [[art:55030a3b:psi.orig_upb_log]]
- sato: 0.02773 [[art:584da64f:psi.sato]]
- season_cos: 1.79e-05 [[art:addec503:psi.season_cos]]
- season_sin: 2.939e-06 [[art:4d2ed98d:psi.season_sin]]
- score: 0.001869 [[art:aa10164c:psi.y_score]]

The largest of these, score included, is 0.06189 [[art:c2e8c8fd:psi.max]], carried by credit_score at 0.06189 [[art:7e87527c:psi.credit_score]], and it sits below the declared bound of 0.25 [[art:278b9016:threshold.S1.psi]].
Every train-to-test index above, for the features and for the score alike, sits below that bound, so the test split is drawn from substantially the population the model was fitted on.

The train-to-vintage-holdout indices are as follows.

- burnout: 0.04749 [[art:e29067e6:psi.vintage_holdout.burnout]]
- credit_score: 0.03996 [[art:3498d307:psi.vintage_holdout.credit_score]]
- incentive: 0.4475 [[art:5e61b6f9:psi.vintage_holdout.incentive]]
- loan_age: 0.07112 [[art:6d92c48b:psi.vintage_holdout.loan_age]]
- note_rate: 0.6088 [[art:f281f8a7:psi.vintage_holdout.note_rate]]
- orig_ltv: 0.02942 [[art:d07cfb7d:psi.vintage_holdout.orig_ltv]]
- orig_upb_log: 0.0404 [[art:77ec758a:psi.vintage_holdout.orig_upb_log]]
- sato: 0.02989 [[art:eea64c25:psi.vintage_holdout.sato]]
- season_cos: 0.001288 [[art:9fe842a8:psi.vintage_holdout.season_cos]]
- season_sin: 0.0007309 [[art:b0dc9745:psi.vintage_holdout.season_sin]]
- score: 0.1604 [[art:c71062d6:psi.vintage_holdout.y_score]]

The train-to-out-of-time indices are as follows.

- burnout: 2.945 [[art:7b0bbebb:psi.out_of_time.burnout]]
- credit_score: 0.05988 [[art:d7249e47:psi.out_of_time.credit_score]]
- incentive: 0.4958 [[art:42076ed1:psi.out_of_time.incentive]]
- loan_age: 2.484 [[art:d6eaaaf5:psi.out_of_time.loan_age]]
- note_rate: 0.6977 [[art:cabd371d:psi.out_of_time.note_rate]]
- orig_ltv: 0.04301 [[art:3eee5db4:psi.out_of_time.orig_ltv]]
- orig_upb_log: 0.07136 [[art:ac349b67:psi.out_of_time.orig_upb_log]]
- sato: 0.01299 [[art:c2233ce6:psi.out_of_time.sato]]
- season_cos: 0.007524 [[art:25cf6b85:psi.out_of_time.season_cos]]
- season_sin: 0.02789 [[art:144e1bd9:psi.out_of_time.season_sin]]
- score: 0.6985 [[art:6f080528:psi.out_of_time.y_score]]

The declared bound of 0.25 [[art:278b9016:threshold.S1.psi]] is written for the training split against the test split, and the paragraphs that follow read the other two splits against that same declared value while noting that its stated scope is narrower.
Read that way, the vintage holdout stands above the bound on incentive at 0.4475 [[art:5e61b6f9:psi.vintage_holdout.incentive]] and on note_rate at 0.6088 [[art:f281f8a7:psi.vintage_holdout.note_rate]], while its score index of 0.1604 [[art:c71062d6:psi.vintage_holdout.y_score]] and its remaining feature indices stay below it.
Read the same way, the out-of-time split stands above the bound on burnout at 2.945 [[art:7b0bbebb:psi.out_of_time.burnout]], on loan_age at 2.484 [[art:d6eaaaf5:psi.out_of_time.loan_age]], on note_rate at 0.6977 [[art:cabd371d:psi.out_of_time.note_rate]], on incentive at 0.4958 [[art:42076ed1:psi.out_of_time.incentive]], and on the score itself at 0.6985 [[art:6f080528:psi.out_of_time.y_score]].
The burnout and loan_age indices in the out-of-time split are of a different order from anything the train-to-test comparison shows and are consistent with a split selected by calendar time, in which age and burnout advance mechanically rather than through any change in borrower behaviour.
The rate-linked drift on note_rate and incentive, and the score drift that accompanies it, means that model output in the out-of-time period is produced on input distributions the fitting sample does not cover, and any use of that period's results should be read with that in mind.
The vintage holdout drifts on the same rate-linked inputs while its score index stays below the bound, so the two out-of-sample splits are not interchangeable as evidence and neither substitutes for the other.

### Characteristic stability

Each feature's contribution to the shift in the linear predictor is as follows.

- burnout: 0.0001326 [[art:640f9435:csi.burnout]]
- credit_score: 0.007707 [[art:6653968a:csi.credit_score]]
- incentive: 0.005686 [[art:3bfa986b:csi.incentive]]
- loan_age: 0 [[art:df52c920:csi.loan_age]]
- note_rate: 0.01372 [[art:e06d8658:csi.note_rate]]
- orig_ltv: 0.03331 [[art:7a941368:csi.orig_ltv]]
- orig_upb_log: 0.002863 [[art:bbbec9d2:csi.orig_upb_log]]
- sato: 0.0009305 [[art:c9bad372:csi.sato]]
- season_cos: 0.0005034 [[art:78d740c8:csi.season_cos]]
- season_sin: 6.94e-05 [[art:d16ad42f:csi.season_sin]]

The largest characteristic contribution is 0.03331 [[art:a8ca288d:csi.max]], carried by orig_ltv at 0.03331 [[art:7a941368:csi.orig_ltv]], and it sits below the declared stability bound of 0.25 [[art:278b9016:threshold.S1.psi]].
Every other contribution above sits below that bound as well, so no single input is pushing the linear predictor by an amount the declared bound would treat as material.
The ordering of the contributions differs from the ordering of the population indices, and the largest population shifts are not the inputs that move the predictor most, which is what one expects when the most-shifted inputs carry modest weight.

### Leakage screens

Features declared as observed during the period or after the outcome number 0 [[art:742bcd24:leakage.timing.n_flagged]], so nothing in the input set is declared with a timing that would let outcome information reach the model.
This screen rests on the declared timings rather than on an independent reconstruction of when each value became observable, and it is only as strong as those declarations.
The strongest single feature reaches an AUC of 0.7239 [[art:1fe630dd:leakage.target_corr.max_single_feature_auc]], below the bound of 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]] that one feature may reach on its own, so no individual input stands close to reproducing the target by itself.
Feature names matching the target-adjacent lexicon number 0 [[art:407e62be:leakage.name_screen.n_matched]], though a name screen catches only leakage that announces itself in naming.

The contamination screen runs on two arms, each read against its own bound.
On the identifier arm, the share of test rows whose loan and period identifiers also identify a row of train is 0 [[art:63d37fc5:leakage.overlap.ids]], below the declared bound of 0.005 [[art:9f336eaf:threshold.L2.overlap]].
On the feature arm, the rule applies not the declared bound alone but the larger of that bound and a term scaled from the share of train rows whose feature values are not unique within train, which is 0 [[art:4474c227:leakage.duplicates.train]], on the reasoning that two different subjects writing the same discrete row is coincidence rather than contamination.
Here the declared value is the larger of the two, and the bound the feature-overlap rule applied is 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].
The share of test rows whose feature values also appear in train is 0 [[art:0fec8048:leakage.overlap.features]], below the bound that rule applied of 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].
The overall row-overlap screen reads 0 [[art:4c9fcd09:leakage.overlap]], likewise below the bound of 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]] that the feature-overlap rule applied.
Because the duplicate share within train is 0 [[art:4474c227:leakage.duplicates.train]], the widening allowance made no difference on this package and the feature arm was read against the declared value.

### Assessment

The missingness and contamination evidence is clean on the numbers reported, and the train-to-test stability evidence supports treating the test split as drawn from the fitting population [[reg:SR26-2:V.1.a]].
The weight of the data-integrity risk here sits in the out-of-time and vintage splits, where several inputs and, for the out-of-time split, the score itself stand above the declared stability bound, so results computed on those splits describe a population the training data does not cover.
The leakage evidence rests partly on declared timings and on a lexicon of names, and neither of those establishes by itself that no input encodes the outcome; the single-feature AUC screen is the arm of this evidence that does not depend on a declaration.

## 4. Outcomes analysis

Outcomes analysis compares model output with the real-world outcomes it was meant to predict, and results that fall outside established performance thresholds may warrant adjustment, recalibration, or redevelopment [[reg:SR26-2:V.1.b]].
This section reports calibration first and discrimination second.
The reason is the declared use: package.yaml states that this model's output is consumed as a probability and not only as a ranking, so whether the probabilities mean what they say is the leading question here, and that declared use, not the frequency of the event, is what fixes the ordering.

### Calibration

The logistic regression of the outcome on the logit of the predicted probability gives a slope of 1.015 [[art:ffabb935:calibration_slope.train]] on train, 0.9537 [[art:f8ef2beb:calibration_slope.test]] on test, 1.066 [[art:ea7d5696:calibration_slope.out_of_time]] on out of time and 0.8562 [[art:010c0ec4:calibration_slope.vintage_holdout]] on the vintage holdout.
Each of those slopes sits inside the declared band, which runs from 0.8 [[art:749634ae:threshold.C1.calibration_slope.min]] to 1.2 [[art:b6672579:threshold.C1.calibration_slope.max]].
The intercept of that same regression is -1.566 [[art:57309d7d:calibration_intercept.train]] on train, -1.748 [[art:257fb817:calibration_intercept.test]] on test, -1.497 [[art:db324216:calibration_intercept.out_of_time]] on out of time and -2.176 [[art:6f00dbc2:calibration_intercept.vintage_holdout]] on the vintage holdout, and on every split it is negative, which is the direction a systematically over-stated probability takes.
On train the mean predicted probability is 0.03925 [[art:68f41b88:metrics.train.mean_predicted]] against an observed rate of 0.008525 [[art:b9ef3327:metrics.train.event_rate]], a relative gap of 3.604 [[art:324eb124:calibration.mean_rel_gap.train]] against a tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
On test the mean predicted probability is 0.03802 [[art:122af437:metrics.test.mean_predicted]] against an observed rate of 0.008061 [[art:570cc08a:metrics.test.event_rate]], a relative gap of 3.716 [[art:15d5555b:calibration.mean_rel_gap.test]] against the same tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
On out of time the mean predicted probability is 0.07793 [[art:921d185b:metrics.out_of_time.mean_predicted]] against an observed rate of 0.01795 [[art:83ccf5c0:metrics.out_of_time.event_rate]], a relative gap of 3.342 [[art:5b8375ec:calibration.mean_rel_gap.out_of_time]].
On the vintage holdout the mean predicted probability is 0.02582 [[art:348107ae:metrics.vintage_holdout.mean_predicted]] against an observed rate of 0.004817 [[art:e3590a16:metrics.vintage_holdout.event_rate]], a relative gap of 4.36 [[art:a691b5ed:calibration.mean_rel_gap.vintage_holdout]], the largest of the four.
The relative gap is above the declared tolerance on every split, and that is the calibration finding this section carries forward.
The slopes inside the band alongside gaps of this size say the model orders risk on roughly the right scale while placing the whole probability level too high.
The same picture appears in the prepayment rate comparison, where the mean absolute difference between actual and predicted CPR is 0.224 [[art:8d8e2c42:cpr.train.mae]] on train, 0.222 [[art:b7587aed:cpr.test.mae]] on test, 0.318 [[art:8ac7bfbc:cpr.out_of_time.mae]] on out of time and 0.172 [[art:2d48e163:cpr.vintage_holdout.mae]] on the vintage holdout.
The decile-level view of predicted against observed on test and the period-level view of actual against predicted CPR on test are reproduced below.

<!-- quaestor:renderer:begin table calibration.test -->
Calibration by decile of predicted probability on test [[art:8417f6b7:calibration.test]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.002089 | 0.0006498 | 1539 |
| 2 | 0.004414 | 0.0013 | 1539 |
| 3 | 0.007429 | 0.003901 | 1538 |
| 4 | 0.01186 | 0.001951 | 1538 |
| 5 | 0.01785 | 0.002601 | 1538 |
| 6 | 0.02599 | 0.004551 | 1538 |
| 7 | 0.03753 | 0.009753 | 1538 |
| 8 | 0.05466 | 0.009103 | 1538 |
| 9 | 0.08015 | 0.01365 | 1538 |
| 10 | 0.1383 | 0.03316 | 1538 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table cpr.test -->
Actual against predicted CPR by period on test [[art:ee6d2090:cpr.test]]:

| period | n | actual_cpr | predicted_cpr |
|---|---|---|---|
| 201402 | 15 | 0 | 0.1368 |
| 201403 | 28 | 0 | 0.1194 |
| 201404 | 56 | 0 | 0.08868 |
| 201405 | 68 | 0 | 0.08852 |
| 201406 | 80 | 0 | 0.08786 |
| 201407 | 97 | 0.1169 | 0.07477 |
| 201408 | 111 | 0 | 0.0662 |
| 201409 | 133 | 0.08659 | 0.05285 |
| 201410 | 145 | 0 | 0.04497 |
| 201411 | 161 | 0 | 0.03631 |
| 201412 | 175 | 0 | 0.03572 |
| 201501 | 198 | 0 | 0.03448 |
| 201502 | 198 | 0 | 0.03316 |
| 201503 | 198 | 0.05895 | 0.04122 |
| 201504 | 197 | 0 | 0.04587 |
| 201505 | 197 | 0 | 0.06373 |
| 201506 | 197 | 0 | 0.07241 |
| 201507 | 197 | 0 | 0.09378 |
| 201508 | 197 | 0 | 0.1274 |
| 201509 | 197 | 0.05924 | 0.1394 |
| 201510 | 196 | 0.05954 | 0.1707 |
| 201511 | 195 | 0 | 0.2145 |
| 201512 | 195 | 0 | 0.2228 |
| 201601 | 195 | 0.1698 | 0.3043 |
| 201602 | 192 | 0.06074 | 0.4154 |
| 201603 | 191 | 0.1187 | 0.5133 |
| 201604 | 189 | 0.1198 | 0.5524 |
| 201605 | 187 | 0.3673 | 0.6701 |
| 201606 | 180 | 0.1255 | 0.6637 |
| 201607 | 178 | 0.1268 | 0.6819 |
| 201608 | 176 | 0.06609 | 0.6476 |
| 201609 | 175 | 0.1288 | 0.5592 |
| 201610 | 173 | 0.1893 | 0.4488 |
| 201611 | 170 | 0.06835 | 0.391 |
| 201612 | 169 | 0.06874 | 0.3006 |
| 201701 | 168 | 0.1339 | 0.2555 |
| 201702 | 176 | 0.2924 | 0.2214 |
| 201703 | 191 | 0.06105 | 0.1945 |
| 201704 | 199 | 0 | 0.1731 |
| 201705 | 218 | 0.05368 | 0.1722 |
| 201706 | 238 | 0.04927 | 0.1571 |
| 201707 | 248 | 0 | 0.1373 |
| 201708 | 274 | 0 | 0.109 |
| 201709 | 284 | 0.08131 | 0.1122 |
| 201710 | 300 | 0 | 0.08701 |
| 201711 | 323 | 0.03653 | 0.08585 |
| 201712 | 334 | 0.03534 | 0.1069 |
| 201801 | 354 | 0.03338 | 0.1216 |
| 201802 | 353 | 0.06591 | 0.1636 |
| 201803 | 351 | 0.03366 | 0.2442 |
| 201804 | 350 | 0.06646 | 0.3557 |
| 201805 | 348 | 0.1594 | 0.4904 |
| 201806 | 343 | 0.1616 | 0.5521 |
| 201807 | 338 | 0.1638 | 0.5789 |
| 201808 | 333 | 0.06974 | 0.6036 |
| 201809 | 331 | 0.2544 | 0.6206 |
| 201810 | 323 | 0.1707 | 0.6032 |
| 201811 | 318 | 0.07292 | 0.5628 |
| 201812 | 316 | 0.1742 | 0.6044 |
| 201901 | 311 | 0.1098 | 0.6257 |
| 201902 | 300 | 0.1488 | 0.6911 |
| 201903 | 285 | 0.2253 | 0.7179 |
| 201904 | 258 | 0.246 | 0.7039 |
| 201905 | 243 | 0.1385 | 0.6579 |
| 201906 | 233 | 0.2688 | 0.5808 |
| 201907 | 219 | 0.1984 | 0.4595 |
| 201908 | 206 | 0 | 0.3531 |
| 201909 | 191 | 0.06105 | 0.2547 |
| 201910 | 182 | 0.06398 | 0.1893 |
| 201911 | 171 | 0.06796 | 0.17 |
| 201912 | 166 | 0 | 0.1674 |
<!-- quaestor:renderer:end -->

### Discrimination

With the level of the probabilities established, the rank-ordering evidence follows, one row per metric and one column per split.

| Metric | train | test | out of time | vintage holdout |
| --- | --- | --- | --- | --- |
| AUC | 0.7892 [[art:39508266:metrics.train.auc]] | 0.7758 [[art:2f4cab3e:metrics.test.auc]] | 0.7898 [[art:aa836722:metrics.out_of_time.auc]] | 0.7743 [[art:25db8aa3:metrics.vintage_holdout.auc]] |
| Gini | 0.5783 [[art:d618ff0f:metrics.train.gini]] | 0.5517 [[art:8593585c:metrics.test.gini]] | 0.5796 [[art:3dc07327:metrics.out_of_time.gini]] | 0.5486 [[art:eff9b345:metrics.vintage_holdout.gini]] |
| KS | 0.4542 [[art:e8d4ae61:metrics.train.ks]] | 0.428 [[art:554f1e19:metrics.test.ks]] | 0.4368 [[art:00bf02ed:metrics.out_of_time.ks]] | 0.4531 [[art:a2ee5005:metrics.vintage_holdout.ks]] |
| Brier | 0.01036 [[art:d56a10b2:metrics.train.brier]] | 0.009864 [[art:1e4aab51:metrics.test.brier]] | 0.02402 [[art:a8a8d3a5:metrics.out_of_time.brier]] | 0.006101 [[art:55737812:metrics.vintage_holdout.brier]] |
| Log loss | 0.06297 [[art:2bff29d3:metrics.train.logloss]] | 0.06118 [[art:b9424e16:metrics.test.logloss]] | 0.1174 [[art:5198f968:metrics.out_of_time.logloss]] | 0.04161 [[art:9f19871a:metrics.vintage_holdout.logloss]] |
| Share of events in the top two deciles | 0.6059 [[art:eb38637b:deciles.train.top2_capture]] | 0.5806 [[art:43c4adc5:deciles.test.top2_capture]] | 0.5909 [[art:95c24730:deciles.out_of_time.top2_capture]] | 0.5935 [[art:4a376307:deciles.vintage_holdout.top2_capture]] |
| Rows | 36013 [[art:6fdfeabb:metrics.train.n]] | 15382 [[art:e55953e1:metrics.test.n]] | 12257 [[art:7898809e:metrics.out_of_time.n]] | 32177 [[art:37a92951:metrics.vintage_holdout.n]] |

The decile separation on test, with decile 1 holding the highest probabilities, is reproduced below.

<!-- quaestor:renderer:begin table deciles.test -->
Decile separation on test; decile 1 holds the highest probabilities [[art:9246d1cd:deciles.test]]:

| decile | count | events | event_rate | lift |
|---|---|---|---|---|
| 1 | 1539 | 51 | 0.03314 | 4.111 |
| 2 | 1539 | 21 | 0.01365 | 1.693 |
| 3 | 1538 | 14 | 0.009103 | 1.129 |
| 4 | 1538 | 15 | 0.009753 | 1.21 |
| 5 | 1538 | 7 | 0.004551 | 0.5646 |
| 6 | 1538 | 4 | 0.002601 | 0.3226 |
| 7 | 1538 | 3 | 0.001951 | 0.242 |
| 8 | 1538 | 6 | 0.003901 | 0.4839 |
| 9 | 1538 | 2 | 0.0013 | 0.1613 |
| 10 | 1538 | 1 | 0.0006502 | 0.08066 |
<!-- quaestor:renderer:end -->

AUC on train, at 0.7892 [[art:39508266:metrics.train.auc]], stands above AUC on test, at 0.7758 [[art:2f4cab3e:metrics.test.auc]], and that pair is read against a train-to-test AUC bound of 0.08 [[art:630f28f4:threshold.O1.auc_gap]].
The ordering evidence is the steadier part of the picture: discrimination holds up across the two held-out splits, while the probability level does not.

### Declared thresholds

<!-- quaestor:renderer:begin table thresholds.evaluation -->
Every threshold package.yaml declares, with its bound, the recomputed value and the outcome [[art:2fc2a920:thresholds.evaluation]]:

| metric | split | bound | value | result |
|---|---|---|---|---|
| auc | test | minimum 0.65 | 0.7758 | pass |
| calibration_slope | test | minimum 0.8 | 0.9537 | pass |
| calibration_slope | test | maximum 1.2 | 0.9537 | pass |
| psi |  | maximum 0.25 | 0.06189 | pass |
<!-- quaestor:renderer:end -->

The table sets each bound package.yaml declares against the value recomputed in this run: the minimum test AUC of 0.65 [[art:fececac1:threshold.package.auc.test.min]], the calibration slope band from 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] to 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]], and the population stability bound of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
The outcome column is the tool's own, computed from the same recomputed values reported above.

### Follow-up analyses

The first step recomputed every metric on the slice `incentive > median(incentive)` of each split.
It was asked to test whether the over-prediction of the probability level is a uniform scaling bias or is concentrated in the half of the book where the refinancing incentive is highest and prepayment risk actually varies.

<!-- quaestor:renderer:begin table metrics.train.sub.incentive_high -->
Every metric on the incentive above_median slice of train [[art:cb04026c:metrics.train.sub.incentive_high]]:

| metric | value |
|---|---|
| n | 18006 |
| event_rate | 0.01433 |
| auc | 0.7196 |
| gini | 0.4391 |
| ks | 0.3373 |
| brier | 0.01773 |
| logloss | 0.1013 |
| mean_predicted | 0.06474 |
| mean_rel_gap | 3.518 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.incentive_high -->
Every metric on the incentive above_median slice of test [[art:f51b482a:metrics.test.sub.incentive_high]]:

| metric | value |
|---|---|
| n | 7691 |
| event_rate | 0.01313 |
| auc | 0.7281 |
| gini | 0.4562 |
| ks | 0.3583 |
| brier | 0.01647 |
| logloss | 0.09646 |
| mean_predicted | 0.06268 |
| mean_rel_gap | 3.773 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.out_of_time.sub.incentive_high -->
Every metric on the incentive above_median slice of out_of_time [[art:80b7e1fa:metrics.out_of_time.sub.incentive_high]]:

| metric | value |
|---|---|
| n | 6127 |
| event_rate | 0.02824 |
| auc | 0.7536 |
| gini | 0.5071 |
| ks | 0.391 |
| brier | 0.03982 |
| logloss | 0.1809 |
| mean_predicted | 0.1257 |
| mean_rel_gap | 3.452 |
| share | 0.4999 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.vintage_holdout.sub.incentive_high -->
Every metric on the incentive above_median slice of vintage_holdout [[art:5d211b75:metrics.vintage_holdout.sub.incentive_high]]:

| metric | value |
|---|---|
| n | 16088 |
| event_rate | 0.007397 |
| auc | 0.7532 |
| gini | 0.5065 |
| ks | 0.3813 |
| brier | 0.009905 |
| logloss | 0.06468 |
| mean_predicted | 0.04321 |
| mean_rel_gap | 4.842 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

AUC on this slice falls below the split's own by 0.06959 [[art:572da87a:metrics.train.sub.incentive_high.auc_gap]] on train, 0.04774 [[art:d7fc769c:metrics.test.sub.incentive_high.auc_gap]] on test, 0.03623 [[art:ba620fbd:metrics.out_of_time.sub.incentive_high.auc_gap]] on out of time and 0.02106 [[art:6182ebaa:metrics.vintage_holdout.sub.incentive_high.auc_gap]] on the vintage holdout, each within the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] at which such a shortfall would become an open item.
The slice holds 0.5 [[art:277218fb:metrics.train.sub.incentive_high.share]] of train, 0.5 [[art:549aa934:metrics.test.sub.incentive_high.share]] of test, 0.4999 [[art:431d1ff2:metrics.out_of_time.sub.incentive_high.share]] of out of time and 0.5 [[art:cb627056:metrics.vintage_holdout.sub.incentive_high.share]] of the vintage holdout, all above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] a sub-population must hold to raise an open item.
Mean predicted against observed on the slice, relative, is 3.518 [[art:03dd3e85:metrics.train.sub.incentive_high.mean_rel_gap]] on train, 3.773 [[art:ddf406ce:metrics.test.sub.incentive_high.mean_rel_gap]] on test, 3.452 [[art:1db4a82a:metrics.out_of_time.sub.incentive_high.mean_rel_gap]] on out of time and 4.842 [[art:1aef21da:metrics.vintage_holdout.sub.incentive_high.mean_rel_gap]] on the vintage holdout, every one above the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]], so on the high-incentive half the weakness is in the level of the probabilities and not in their ordering.

The second step recomputed every metric on the complementary slice `incentive <= median(incentive)` of each split.
It was asked because the complement shows whether the over-prediction is an offset that applies across the whole incentive partition or something that lives in the refinanceable half alone.

<!-- quaestor:renderer:begin table metrics.train.sub.incentive_low -->
Every metric on the incentive below_median slice of train [[art:4bd37172:metrics.train.sub.incentive_low]]:

| metric | value |
|---|---|
| n | 18007 |
| event_rate | 0.002721 |
| auc | 0.7218 |
| gini | 0.4437 |
| ks | 0.3741 |
| brier | 0.00299 |
| logloss | 0.02464 |
| mean_predicted | 0.01377 |
| mean_rel_gap | 4.06 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.incentive_low -->
Every metric on the incentive below_median slice of test [[art:0e5269db:metrics.test.sub.incentive_low]]:

| metric | value |
|---|---|
| n | 7691 |
| event_rate | 0.002991 |
| auc | 0.6822 |
| gini | 0.3644 |
| ks | 0.3297 |
| brier | 0.003259 |
| logloss | 0.02591 |
| mean_predicted | 0.01336 |
| mean_rel_gap | 3.468 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.out_of_time.sub.incentive_low -->
Every metric on the incentive below_median slice of out_of_time [[art:15c7b72a:metrics.out_of_time.sub.incentive_low]]:

| metric | value |
|---|---|
| n | 6130 |
| event_rate | 0.007667 |
| auc | 0.7704 |
| gini | 0.5409 |
| ks | 0.4526 |
| brier | 0.008232 |
| logloss | 0.05396 |
| mean_predicted | 0.03016 |
| mean_rel_gap | 2.934 |
| share | 0.5001 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.vintage_holdout.sub.incentive_low -->
Every metric on the incentive below_median slice of vintage_holdout [[art:2fbef9c8:metrics.vintage_holdout.sub.incentive_low]]:

| metric | value |
|---|---|
| n | 16089 |
| event_rate | 0.002238 |
| auc | 0.6844 |
| gini | 0.3687 |
| ks | 0.3628 |
| brier | 0.002297 |
| logloss | 0.01855 |
| mean_predicted | 0.008434 |
| mean_rel_gap | 2.769 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

AUC on this slice falls below the split's own by 0.06733 [[art:bdcd3ce1:metrics.train.sub.incentive_low.auc_gap]] on train and 0.01935 [[art:6bcab8af:metrics.out_of_time.sub.incentive_low.auc_gap]] on out of time, both within the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].
On test the shortfall is 0.09364 [[art:b062501e:metrics.test.sub.incentive_low.auc_gap]] and on the vintage holdout 0.08994 [[art:40f8b479:metrics.vintage_holdout.sub.incentive_low.auc_gap]], both read against that same bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] and both above it, and both are left to the findings section as open items for the model developer.
The slice holds 0.5 [[art:d7af12f0:metrics.train.sub.incentive_low.share]] of train, 0.5 [[art:1d5dd4c2:metrics.test.sub.incentive_low.share]] of test, 0.5001 [[art:c7aaafd2:metrics.out_of_time.sub.incentive_low.share]] of out of time and 0.5 [[art:d94e6531:metrics.vintage_holdout.sub.incentive_low.share]] of the vintage holdout, all above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].
Mean predicted against observed on the slice, relative, is 4.06 [[art:48122349:metrics.train.sub.incentive_low.mean_rel_gap]] on train, 3.468 [[art:9d73c7ff:metrics.test.sub.incentive_low.mean_rel_gap]] on test, 2.934 [[art:d4df9d6d:metrics.out_of_time.sub.incentive_low.mean_rel_gap]] on out of time and 2.769 [[art:47d4921d:metrics.vintage_holdout.sub.incentive_low.mean_rel_gap]] on the vintage holdout, each above the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]], so the level of the probabilities is overstated on this half as well, and on test and on the vintage holdout the ordering is weak enough to be carried separately.

The third step recomputed every metric on the slice `loan_age > median(loan_age)` of each split.
It was asked because the over-prediction appears on all four splits, so partitioning on seasoning tests whether the bias is a uniform scaling of the hazard or varies with loan age in a way the incentive partition could not distinguish.

<!-- quaestor:renderer:begin table metrics.train.sub.loan_age_high -->
Every metric on the loan_age above_median slice of train [[art:3ca45feb:metrics.train.sub.loan_age_high]]:

| metric | value |
|---|---|
| n | 17925 |
| event_rate | 0.01144 |
| auc | 0.7715 |
| gini | 0.5431 |
| ks | 0.4099 |
| brier | 0.01396 |
| logloss | 0.0817 |
| mean_predicted | 0.05214 |
| mean_rel_gap | 3.559 |
| share | 0.4977 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.loan_age_high -->
Every metric on the loan_age above_median slice of test [[art:204983c3:metrics.test.sub.loan_age_high]]:

| metric | value |
|---|---|
| n | 7610 |
| event_rate | 0.0113 |
| auc | 0.7523 |
| gini | 0.5045 |
| ks | 0.3983 |
| brier | 0.01365 |
| logloss | 0.08033 |
| mean_predicted | 0.04993 |
| mean_rel_gap | 3.419 |
| share | 0.4947 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.out_of_time.sub.loan_age_high -->
Every metric on the loan_age above_median slice of out_of_time [[art:1dc983d8:metrics.out_of_time.sub.loan_age_high]]:

| metric | value |
|---|---|
| n | 6081 |
| event_rate | 0.02187 |
| auc | 0.7984 |
| gini | 0.5968 |
| ks | 0.4633 |
| brier | 0.0301 |
| logloss | 0.1427 |
| mean_predicted | 0.09906 |
| mean_rel_gap | 3.529 |
| share | 0.4961 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.vintage_holdout.sub.loan_age_high -->
Every metric on the loan_age above_median slice of vintage_holdout [[art:6e61b330:metrics.vintage_holdout.sub.loan_age_high]]:

| metric | value |
|---|---|
| n | 16066 |
| event_rate | 0.004793 |
| auc | 0.7034 |
| gini | 0.4069 |
| ks | 0.3589 |
| brier | 0.005394 |
| logloss | 0.03899 |
| mean_predicted | 0.02146 |
| mean_rel_gap | 3.477 |
| share | 0.4993 |
<!-- quaestor:renderer:end -->

AUC on this slice falls below the split's own by 0.01762 [[art:9e5dcedc:metrics.train.sub.loan_age_high.auc_gap]] on train, 0.02357 [[art:64c4287f:metrics.test.sub.loan_age_high.auc_gap]] on test and 0.07087 [[art:2366ea6e:metrics.vintage_holdout.sub.loan_age_high.auc_gap]] on the vintage holdout, all within the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]], while on out of time the shortfall is -0.0086 [[art:ae068d6e:metrics.out_of_time.sub.loan_age_high.auc_gap]], the slice ordering better than the split as a whole.
The slice holds 0.4977 [[art:52284cdc:metrics.train.sub.loan_age_high.share]] of train, 0.4947 [[art:e21962d4:metrics.test.sub.loan_age_high.share]] of test, 0.4961 [[art:b35469b9:metrics.out_of_time.sub.loan_age_high.share]] of out of time and 0.4993 [[art:6faede5c:metrics.vintage_holdout.sub.loan_age_high.share]] of the vintage holdout, all above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].
Mean predicted against observed on the slice, relative, is 3.559 [[art:6aa9321e:metrics.train.sub.loan_age_high.mean_rel_gap]] on train, 3.419 [[art:20d6b512:metrics.test.sub.loan_age_high.mean_rel_gap]] on test, 3.529 [[art:be1fdcf0:metrics.out_of_time.sub.loan_age_high.mean_rel_gap]] on out of time and 3.477 [[art:4a861a82:metrics.vintage_holdout.sub.loan_age_high.mean_rel_gap]] on the vintage holdout, each above the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]], so on seasoned loans the defect is again in the level of the probabilities rather than in their ordering.

The fourth step recomputed every metric on the complementary slice `loan_age <= median(loan_age)` of each split.
It was asked to complete the seasoning partition, so that the level bias can be read on both halves rather than inferred from one.

<!-- quaestor:renderer:begin table metrics.train.sub.loan_age_low -->
Every metric on the loan_age below_median slice of train [[art:b32d5a06:metrics.train.sub.loan_age_low]]:

| metric | value |
|---|---|
| n | 18088 |
| event_rate | 0.005639 |
| auc | 0.7846 |
| gini | 0.5693 |
| ks | 0.4485 |
| brier | 0.006789 |
| logloss | 0.0444 |
| mean_predicted | 0.02648 |
| mean_rel_gap | 3.695 |
| share | 0.5023 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.loan_age_low -->
Every metric on the loan_age below_median slice of test [[art:e9591084:metrics.test.sub.loan_age_low]]:

| metric | value |
|---|---|
| n | 7772 |
| event_rate | 0.004889 |
| auc | 0.7741 |
| gini | 0.5482 |
| ks | 0.4665 |
| brier | 0.006159 |
| logloss | 0.04244 |
| mean_predicted | 0.02635 |
| mean_rel_gap | 4.39 |
| share | 0.5053 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.out_of_time.sub.loan_age_low -->
Every metric on the loan_age below_median slice of out_of_time [[art:0997edbe:metrics.out_of_time.sub.loan_age_low]]:

| metric | value |
|---|---|
| n | 6176 |
| event_rate | 0.01409 |
| auc | 0.7852 |
| gini | 0.5704 |
| ks | 0.4394 |
| brier | 0.01804 |
| logloss | 0.09252 |
| mean_predicted | 0.05712 |
| mean_rel_gap | 3.055 |
| share | 0.5039 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.vintage_holdout.sub.loan_age_low -->
Every metric on the loan_age below_median slice of vintage_holdout [[art:69d53a03:metrics.vintage_holdout.sub.loan_age_low]]:

| metric | value |
|---|---|
| n | 16111 |
| event_rate | 0.004841 |
| auc | 0.8339 |
| gini | 0.6679 |
| ks | 0.5933 |
| brier | 0.006805 |
| logloss | 0.04422 |
| mean_predicted | 0.03017 |
| mean_rel_gap | 5.232 |
| share | 0.5007 |
<!-- quaestor:renderer:end -->

AUC on this slice falls below the split's own by 0.004516 [[art:c2656c63:metrics.train.sub.loan_age_low.auc_gap]] on train, 0.001757 [[art:cf8d7d74:metrics.test.sub.loan_age_low.auc_gap]] on test and 0.0046 [[art:cbec2b07:metrics.out_of_time.sub.loan_age_low.auc_gap]] on out of time, all within the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]], and on the vintage holdout the shortfall is -0.05963 [[art:373b0b83:metrics.vintage_holdout.sub.loan_age_low.auc_gap]], the slice ordering better than the split as a whole.
The slice holds 0.5023 [[art:705485e1:metrics.train.sub.loan_age_low.share]] of train, 0.5053 [[art:733f3324:metrics.test.sub.loan_age_low.share]] of test, 0.5039 [[art:77397e73:metrics.out_of_time.sub.loan_age_low.share]] of out of time and 0.5007 [[art:8b31e269:metrics.vintage_holdout.sub.loan_age_low.share]] of the vintage holdout, all above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].
Mean predicted against observed on the slice, relative, is 3.695 [[art:56cd77db:metrics.train.sub.loan_age_low.mean_rel_gap]] on train, 4.39 [[art:06bb2e76:metrics.test.sub.loan_age_low.mean_rel_gap]] on test, 3.055 [[art:db1b4d86:metrics.out_of_time.sub.loan_age_low.mean_rel_gap]] on out of time and 5.232 [[art:0406dec3:metrics.vintage_holdout.sub.loan_age_low.mean_rel_gap]] on the vintage holdout, every one above the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]], so on newer loans too the probabilities rank acceptably while sitting well above the rate actually observed.

## 5. Sensitivity and scenario analysis

Sensitivity and scenario work belongs to the critical analysis of developmental evidence that validation is expected to carry out, evaluating both the quality and the extent of that evidence [[reg:SR26-2:V.1.a]].
The superseded guidance is more specific about the mechanics, asking that sensitivity analysis check the impact of changes in inputs and parameter values on model outputs and that stress testing span a wide range of inputs, including extreme values, to establish the boundaries of model performance [[reg:SR11-7:V.1.a]].
All three checks described below apply to this model type: the design is a fitted linear-index hazard whose retained features can be screened for collinearity, the data carry a declared rate-regime column, and the package prices servicing value under a rate-shock grid, so none of the three is deferred to Appendix D as inapplicable.

### Multicollinearity among the retained features

The largest variance inflation factor among the retained features is 4.976 [[art:f9e0db60:vif.max]], carried by the note-rate term at 4.976 [[art:37532fa8:vif.note_rate]], and it sits below the declared limit of 10 [[art:aeb4f33c:threshold.M1.vif]].
The next-largest values, on burnout at 3.439 [[art:88879cb2:vif.burnout]], loan age at 2.929 [[art:5573d536:vif.loan_age]] and the refinance incentive at 2.226 [[art:2da1b19c:vif.incentive]], are further from the limit still, and the remaining terms are close to unity, at 1.713 [[art:a6c55fce:vif.sato]] for the spread at origination, 1.018 [[art:a9cfa7eb:vif.season_cos]] and 1.004 [[art:669c5fcb:vif.season_sin]] for the seasonal pair, 1.008 [[art:f05d536a:vif.credit_score]] for credit score, 1.006 [[art:24f8e4d1:vif.orig_upb_log]] for log original balance and 1.005 [[art:65b35f3b:vif.orig_ltv]] for original loan-to-value.
Belsley's condition number of the column-standardised design is 4.943 [[art:4f06a3c5:condition_number]], below the declared limit of 30 [[art:7e52fd7a:threshold.M1.condition_number]].
On both the feature-wise and the whole-design measures the retained set is well inside the package's own tolerances, so coefficient estimates are not being read off a near-singular design.

### Stability across the declared regimes

Discrimination was measured within each declared rate regime on the training data.

<!-- quaestor:renderer:begin table stability.auc_by_regime -->
The champion's AUC within each rate_regime on train [[art:0b789c1f:stability.auc_by_regime]]:

| regime | n | event_rate | auc |
|---|---|---|---|
| falling | 17873 | 0.01438 | 0.7243 |
| rising | 18140 | 0.002756 | 0.7236 |
<!-- quaestor:renderer:end -->

The package screens each of the top-ranked features for a sign change across regimes, counting a change only where the coefficient exceeds 0.05 [[art:aca84377:threshold.R1.sign_flip_coef]] in magnitude and reaches a |z| of at least 2 [[art:2e4428c7:threshold.R1.sign_flip_z]] in both regimes, and compares the across-regime difference in discrimination against a declared limit of 0.1 [[art:b64213d7:threshold.R1.auc_gap]].
The sign-flip indicator comes back 0 for the note rate [[art:e7ce4912:stability.note_rate.sign_flip]], 0 for the refinance incentive [[art:0cc7a37d:stability.incentive.sign_flip]], 0 for burnout [[art:6bc05e82:stability.burnout.sign_flip]], 0 for loan age [[art:b7191217:stability.loan_age.sign_flip]], 0 for the spread at origination [[art:1f302ccd:stability.sato.sign_flip]], 0 for credit score [[art:d956c276:stability.credit_score.sign_flip]], 0 for original loan-to-value [[art:054d5fab:stability.orig_ltv.sign_flip]], 0 for log original balance [[art:fb1ae6c8:stability.orig_upb_log.sign_flip]] and 0 for each of the two seasonal terms [[art:1850e2de:stability.season_cos.sign_flip]] [[art:6ba36a3b:stability.season_sin.sign_flip]].
No retained feature therefore reverses the direction of its effect between regimes at a magnitude and significance the package treats as material, which is the behaviour a prepayment hazard is expected to show if its rate-response terms are capturing the economics rather than the period.
The regime-wise discrimination figures in the table above should be read against the declared difference limit of 0.1 [[art:b64213d7:threshold.R1.auc_gap]]; the comparison being made there is the difference between regimes, not their ratio, and a difference inside the limit does not by itself say the regimes are alike in relative terms.

### Rate-shock scenarios

Servicing value was repriced across a parallel shock grid, and the change from the base case at each shock is set out below alongside first-year prepayment speeds.

<!-- quaestor:renderer:begin table scenario.value_by_shock -->
Servicing value, its change from the base case and first-year CPR, by shock [[art:89b33839:scenario.value_by_shock]]:

| shock_bp | value | value_change | cpr |
|---|---|---|---|
| -300 | 89610 | -1.099e+06 | 0.9686 |
| -200 | 262000 | -927100 | 0.7096 |
| -100 | 671200 | -517800 | 0.3268 |
| 0 | 1.189e+06 | 0 | 0.113 |
| 100 | 1.542e+06 | 352800 | 0.03497 |
| 200 | 1.695e+06 | 505800 | 0.01044 |
| 300 | 1.747e+06 | 557600 | 0.003084 |
<!-- quaestor:renderer:end -->

At the downward extreme the value change is -1099000 [[art:ff90f8c1:scenario.value_change.-300]], and at the upward extreme it is 557600 [[art:0b43db3b:scenario.value_change.300]], so the loss under a large rally is the larger of the two moves in absolute size.
The change is monotone increasing in the shock across the whole grid, running -1099000 [[art:ff90f8c1:scenario.value_change.-300]], -927100 [[art:59e2f8a4:scenario.value_change.-200]], -517800 [[art:b3c09ea9:scenario.value_change.-100]], 0 [[art:1e1b0b88:scenario.value_change.0]], 352800 [[art:95da798d:scenario.value_change.100]], 505800 [[art:be13cc25:scenario.value_change.200]] and 557600 [[art:0b43db3b:scenario.value_change.300]], with no reversal of direction anywhere along it.
The increments shrink as the shock moves up: the step sizes visible in that ladder are largest on the rally side and smallest between the two upward extremes, which is the shape of an asset whose upside is capped by the borrower's option to refinance.
The convexity statistic, the sum of the changes at the two extremes, is -541800 [[art:42ad3e3e:scenario.convexity]], negative because the fall under the downward shock outweighs the rise under the upward one.
That negative sign is the direction the package declares for this instrument, so the scenario run agrees with the stated convexity behaviour rather than contradicting it.
Taken together, the monotone response, the diminishing upside increments and the negative convexity are consistent with a prepayment hazard driving a servicing asset, and no instability in the sense of a large output move from a small input move appears in the grid as run.

## 6. Findings and recommendations

Findings below are ordered by severity, and each carries the recomputed values, the declared tolerance they were read against, and the decile evidence behind them, so that the reliability of the model and whether corrective action is warranted can be judged from the evidence itself [[reg:SR26-2:V]].

### F-001 · C1 calibration · severity **medium**

**The predicted prepayment level overstates the observed prepayment rate on every split evaluated, by a relative margin well beyond the declared calibration tolerance.**

On train, mean predicted is 0.03925 [[art:68f41b88:metrics.train.mean_predicted]] against an observed rate of 0.008525 [[art:b9ef3327:metrics.train.event_rate]], a relative gap of 3.604 [[art:324eb124:calibration.mean_rel_gap.train]] against a declared tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].

On test, mean predicted is 0.03802 [[art:122af437:metrics.test.mean_predicted]] against an observed rate of 0.008061 [[art:570cc08a:metrics.test.event_rate]], a relative gap of 3.716 [[art:15d5555b:calibration.mean_rel_gap.test]], again above the declared tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].

On out_of_time, mean predicted is 0.07793 [[art:921d185b:metrics.out_of_time.mean_predicted]] against an observed rate of 0.01795 [[art:83ccf5c0:metrics.out_of_time.event_rate]], a relative gap of 3.342 [[art:5b8375ec:calibration.mean_rel_gap.out_of_time]], above the same declared tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].

On vintage_holdout, mean predicted is 0.02582 [[art:348107ae:metrics.vintage_holdout.mean_predicted]] against an observed rate of 0.004817 [[art:e3590a16:metrics.vintage_holdout.event_rate]], a relative gap of 4.36 [[art:a691b5ed:calibration.mean_rel_gap.vintage_holdout]], the furthest above the declared tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]] of the four splits reported here.

The overstatement is in the same direction on the in-sample split and on each held-out split, so it is a property of the fitted level rather than a holdout artifact.

The decile evidence behind each split follows.

<!-- quaestor:renderer:begin table calibration.train -->
Calibration by decile of predicted probability on train [[art:a8585045:calibration.train]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.002166 | 0.0008329 | 3602 |
| 2 | 0.004511 | 0.001943 | 3602 |
| 3 | 0.007472 | 0.00111 | 3602 |
| 4 | 0.01183 | 0.002499 | 3601 |
| 5 | 0.0181 | 0.00361 | 3601 |
| 6 | 0.02708 | 0.004443 | 3601 |
| 7 | 0.03949 | 0.007498 | 3601 |
| 8 | 0.05611 | 0.01166 | 3601 |
| 9 | 0.08192 | 0.01805 | 3601 |
| 10 | 0.1439 | 0.0336 | 3601 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table calibration.test -->
Calibration by decile of predicted probability on test [[art:8417f6b7:calibration.test]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.002089 | 0.0006498 | 1539 |
| 2 | 0.004414 | 0.0013 | 1539 |
| 3 | 0.007429 | 0.003901 | 1538 |
| 4 | 0.01186 | 0.001951 | 1538 |
| 5 | 0.01785 | 0.002601 | 1538 |
| 6 | 0.02599 | 0.004551 | 1538 |
| 7 | 0.03753 | 0.009753 | 1538 |
| 8 | 0.05466 | 0.009103 | 1538 |
| 9 | 0.08015 | 0.01365 | 1538 |
| 10 | 0.1383 | 0.03316 | 1538 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table calibration.out_of_time -->
Calibration by decile of predicted probability on out_of_time [[art:392a629c:calibration.out_of_time]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.008744 | 0 | 1226 |
| 2 | 0.01645 | 0.002447 | 1226 |
| 3 | 0.02357 | 0.003263 | 1226 |
| 4 | 0.03155 | 0.008157 | 1226 |
| 5 | 0.04144 | 0.0106 | 1226 |
| 6 | 0.0546 | 0.01223 | 1226 |
| 7 | 0.07307 | 0.01468 | 1226 |
| 8 | 0.1034 | 0.02204 | 1225 |
| 9 | 0.1546 | 0.02449 | 1225 |
| 10 | 0.2721 | 0.08163 | 1225 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table calibration.vintage_holdout -->
Calibration by decile of predicted probability on vintage_holdout [[art:fd5aec5a:calibration.vintage_holdout]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.001905 | 0.0006215 | 3218 |
| 2 | 0.003662 | 0.002175 | 3218 |
| 3 | 0.005429 | 0.0006215 | 3218 |
| 4 | 0.007464 | 0.001243 | 3218 |
| 5 | 0.0101 | 0.0009323 | 3218 |
| 6 | 0.01391 | 0.003108 | 3218 |
| 7 | 0.01993 | 0.00404 | 3218 |
| 8 | 0.0306 | 0.006839 | 3217 |
| 9 | 0.05066 | 0.008082 | 3217 |
| 10 | 0.1146 | 0.02052 | 3217 |
<!-- quaestor:renderer:end -->

The validator concludes that the model's output cannot be read as a prepayment probability in a valuation that multiplies it by balances or cash flows, because a level biased this far above the observed rate propagates directly into servicing-run-off and MSR value, while rank ordering on test remains at an AUC of 0.7758 [[art:2f4cab3e:metrics.test.auc]] and is not what the defect concerns.

The model developer should identify the source of the level bias, recalibrate the predicted level against the observed rate, and re-report the relative gap and the decile calibration on each split against the declared tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]] before the package is used to produce valuation output.

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1, S1), `compute_metrics` (T1, O1), `check_leakage` (L1, L2), `check_stability` (R1), `check_collinearity` (M1), `challenger_compare` (E1), `run_scenarios` (X1).

### Open items

- Model developer: on the test split, what is the model discriminating on inside the sub-population defined by `incentive <= median(incentive)`, where that slice's AUC of 0.6822 [[art:4ca370cf:metrics.test.sub.incentive_low.auc]] falls 0.09364 [[art:b062501e:metrics.test.sub.incentive_low.auc_gap]] below the split's own AUC of 0.7758 [[art:2f4cab3e:metrics.test.auc]], read against a declared slice gap bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]], on a slice holding 0.5 [[art:1d5dd4c2:metrics.test.sub.incentive_low.share]] of the split against a minimum share bound of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]]?
- Model developer: on the vintage_holdout split, what is the model discriminating on inside the sub-population defined by `incentive <= median(incentive)`, where that slice's AUC of 0.6844 [[art:47e679fc:metrics.vintage_holdout.sub.incentive_low.auc]] falls 0.08994 [[art:40f8b479:metrics.vintage_holdout.sub.incentive_low.auc_gap]] below the split's own AUC of 0.7743 [[art:25db8aa3:metrics.vintage_holdout.auc]], read against a declared slice gap bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]], on a slice holding 0.5 [[art:d94e6531:metrics.vintage_holdout.sub.incentive_low.share]] of the split against a minimum share bound of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]]?
- Model developer: what behaviour is the fitted coefficient on `burnout` carrying, given its sign of -1 [[art:dcfb2de4:sign_check.burnout.coef_sign]] read against that feature's own univariate direction of 1 [[art:bfc96bb2:sign_check.burnout.univariate_direction]], a disagreement recorded as 0 [[art:56826e40:sign_check.burnout.agrees]], once the features correlated with it are conditioned on alongside it?
- Model developer: what behaviour is the fitted coefficient on `note_rate` carrying, given its sign of -1 [[art:aecf7ccb:sign_check.note_rate.coef_sign]] read against that feature's own univariate direction of 1 [[art:61f6e1ac:sign_check.note_rate.univariate_direction]], a disagreement recorded as 0 [[art:a453463d:sign_check.note_rate.agrees]], once the features correlated with it are conditioned on alongside it?
- Model developer: what behaviour is the fitted coefficient on `sato` carrying, given its sign of -1 [[art:265915cf:sign_check.sato.coef_sign]] read against that feature's own univariate direction of 1 [[art:c08233a6:sign_check.sato.univariate_direction]], a disagreement recorded as 0 [[art:b3755963:sign_check.sato.agrees]], once the features correlated with it are conditioned on alongside it?

## 7. Ongoing monitoring recommendations

Ongoing monitoring evaluates the extent to which this model keeps performing as expected given changes in products, exposures, activities, clients, data relevance, or market conditions, and the recommendations below are framed on that basis [[reg:SR26-2:V.2]].

### Quantities, cadence, and bounds

Monitoring should track the same quantities this validation recomputed and judge them against the same bounds package.yaml declares, so that a production reading and a validation reading are read on one scale rather than against a fresh set of numbers invented for the monitoring report.

The calibration slope should be recomputed on each monthly production cohort with realized outcomes and compared with the declared lower bound of 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] and the declared upper bound of 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].

The validation reading of 0.9537 [[art:f8ef2beb:calibration_slope.test]] sits inside that declared band and is the reference level against which a production series should be read.

Discrimination should be tracked as the AUC on each quarterly vintage whose performance window has closed, against the declared floor of 0.65 [[art:fececac1:threshold.package.auc.test.min]], with the validation reading of 0.7758 [[art:2f4cab3e:metrics.test.auc]] as the reference level above that floor.

Population stability should be recomputed monthly across the scored inputs and the score itself, against the declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].

The largest train-to-test reading in this validation was 0.06189 [[art:c2e8c8fd:psi.max]], below that ceiling, and monitoring should report the production reading alongside it rather than in isolation.

Calibration and discrimination should also be tracked within the segments used for reporting, and where a segment is set against the book as a whole the monitoring report should state explicitly whether it is reporting the difference or the ratio, because segments whose absolute gaps match can differ materially in relative terms.

### How the monitoring report should order its evidence

A monitoring report on this model should present calibration evidence before discrimination evidence, as this report does, because package.yaml declares that the output is used as a probability and not only as a ranking.

A slope that drifts toward either declared bound changes the loss forecast that consumes the output even while rank ordering holds, so that ordering is not cosmetic.

### Benchmarking

The challenger compared with the champion in this validation was fitted on development data, and what monitoring adds is the comparison that development data cannot give: the challenger refitted on production vintages, with its calibration and discrimination set against the champion's on those same vintages [[reg:SR11-7:V.1.b]].

Discrepancies between the champion and the refitted challenger should trigger investigation into their source and degree rather than an automatic change of model, since the benchmark is itself an alternative prediction and differences may follow from its data or method [[reg:SR11-7:V.1.b]].

### What monitoring must watch that this validation could not

This validation observed the model on data assembled before production use, so outcomes analysis on vintages originated after the package was frozen falls to monitoring, comparing realized prepayment outcomes with forecasts at an observation frequency matching the model's performance window [[reg:SR26-2:V.1.b]].

Drift here was measured as a single train-to-test comparison, whereas monitoring observes a series, and a slow movement that stays under the declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]] still warrants escalation when it runs in one direction across consecutive cycles.

Overrides of model output in production should be logged, analysed, and reported, because a rising override rate or an override process that consistently improves on the model indicates the model needs revision [[reg:SR11-7:V.1.b]].

Process verification — input feed accuracy and completeness, change control over the scoring code, and fidelity of the production scoring path to the packaged model — belongs to monitoring rather than to a recomputation on stored data [[reg:SR11-7:V.1.b]].

Shifts in the rate environment, servicer behaviour, or product mix can move the scored population toward the edges of the ranges seen in development, and monitoring should flag those situations as the ranges are approached rather than only once they are exceeded [[reg:SR11-7:V.1.b]].

### Response and review

A reading outside a declared bound in any cycle, or a persistent deviation across cycles even while readings remain inside the bounds, should trigger documented investigation and a decision on overlay, adjustment, recalibration, or redevelopment under the model risk management policy [[reg:SR26-2:V.1.b]].

The cadence and scope proposed here should themselves be revisited at each annual review, since the frequency and scope of monitoring reports depend on the nature of the model, the availability of new data or modelling approaches, and model materiality [[reg:SR26-2:V.2]].

## Appendix A — Claims

Grounding precision 0.9974 before repair (379 of 380 claims verified; 1 unsupported) and 1.0000 after 0 claim(s) rewritten and 1 number(s) removed from the prose. Per section (post-repair): summary 25/25; conceptual_soundness 64/64; data_integrity 82/82; outcomes 124/124; sensitivity 37/37; findings 39/39; monitoring 8/8.

Developer claims: The package declares 3 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). See Appendix D.

Excluded numeric tokens (not claims): section_number (section 6); label_number (decile 1); citation_hash (2ad8d1a5, 6fdfeabb, e55953e1, c5ebd9c9); regulatory_section_id (SR26-2:V, SR26-2:V.1.b, SR26-2:V.1.a, SR26-2:IV.1); finding_id (F-001); package_version (1.0); extractor_returned_excluded_token (1.0, 001,, 6, 12.0).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The validation re-executed the packaged scoring path and rec… | 300 | ratio | runtime.max_seconds |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 2 | summary | The development split carries 36013 rows and the held-out te… | 36013 | count | n | train | eq | `[[art:6fdfeabb:metrics.train.n]]` | verified | 36013 |
| 3 | summary | The development split carries 36013 rows and the held-out te… | 15382 | count | n | test | eq | `[[art:e55953e1:metrics.test.n]]` | verified | 15382 |
| 4 | summary | The development split carries 36013 rows and the held-out te… | 36013 | count | n | train | eq | `[[art:c5ebd9c9:profile.train.n]]` | verified | 36013 |
| 5 | summary | The development split carries 36013 rows and the held-out te… | 15382 | count | n | test | eq | `[[art:e3abc1b8:profile.test.n]]` | verified | 15382 |
| 6 | summary | Two further splits extend the evidence beyond the developmen… | 12257 | count | n | out_of_time | eq | `[[art:7898809e:metrics.out_of_time.n]]` | verified | 12257 |
| 7 | summary | Two further splits extend the evidence beyond the developmen… | 32177 | count | n | vintage_holdout | eq | `[[art:37a92951:metrics.vintage_holdout.n]]` | verified | 32177 |
| 8 | summary | Discrimination on test stands at 0.7758 , above the declared… | 0.7758 | ratio | auc | test | eq | `[[art:2f4cab3e:metrics.test.auc]]` | verified | 0.7758373186 |
| 9 | summary | Discrimination on test stands at 0.7758 , above the declared… | 0.65 | ratio | auc | test | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 10 | summary | The calibration slope on test is 0.9537 , inside the declare… | 0.9537 | ratio | calibration_slope | test | eq | `[[art:f8ef2beb:calibration_slope.test]]` | verified | 0.9536630305 |
| 11 | summary | The calibration slope on test is 0.9537 , inside the declare… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 12 | summary | The calibration slope on test is 0.9537 , inside the declare… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 13 | summary | The largest population stability index measured from develop… | 0.06189 | ratio | psi |  | eq | `[[art:c2e8c8fd:psi.max]]` | verified | 0.06188985797 |
| 14 | summary | The largest population stability index measured from develop… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 15 | summary | The calibration slope is 1.015 on the development split and… | 1.015 | ratio | calibration_slope | train | eq | `[[art:ffabb935:calibration_slope.train]]` | verified | 1.014728573 |
| 16 | summary | The calibration slope is 1.015 on the development split and… | 1.066 | ratio | calibration_slope | out_of_time | eq | `[[art:ea7d5696:calibration_slope.out_of_time]]` | verified | 1.066358183 |
| 17 | summary | The calibration slope is 1.015 on the development split and… | 0.8562 | ratio | calibration_slope | vintage_holdout | eq | `[[art:010c0ec4:calibration_slope.vintage_holdout]]` | verified | 0.8561504457 |
| 18 | summary | On the level of the predictions rather than their ranking, m… | 0.03802 | ratio | mean_predicted | test | eq | `[[art:122af437:metrics.test.mean_predicted]]` | verified | 0.038020619 |
| 19 | summary | On the level of the predictions rather than their ranking, m… | 0.008061 | ratio | event_rate | test | eq | `[[art:570cc08a:metrics.test.event_rate]]` | verified | 0.008061370433 |
| 20 | summary | On the level of the predictions rather than their ranking, m… | 0.02582 | ratio | mean_predicted | vintage_holdout | eq | `[[art:348107ae:metrics.vintage_holdout.mean_predicted]]` | verified | 0.02582080379 |
| 21 | summary | On the level of the predictions rather than their ranking, m… | 0.004817 | ratio | event_rate | vintage_holdout | eq | `[[art:e3590a16:metrics.vintage_holdout.event_rate]]` | verified | 0.004817105386 |
| 22 | summary | The challenger scored on test lands below the champion on di… | -0.04213 | ratio | delta_auc | test | eq | `[[art:1e990f53:challenger.delta_auc]]` | verified | -0.04212940647 |
| 23 | summary | The design is well conditioned on the collinearity diagnosti… | 4.976 | ratio | vif |  | eq | `[[art:f9e0db60:vif.max]]` | verified | 4.975500767 |
| 24 | summary | The design is well conditioned on the collinearity diagnosti… | 4.943 | ratio | condition_number |  | eq | `[[art:4f06a3c5:condition_number]]` | verified | 4.942565522 |
| 25 | summary | The design is well conditioned on the collinearity diagnosti… | 0.03331 | ratio | csi |  | eq | `[[art:a8ca288d:csi.max]]` | verified | 0.03331391493 |
| 26 | conceptual_soundness | It was fitted with an intercept of -3.836 on 36013 loan-mont… | -3.836 | ratio | intercept |  | eq | `[[art:a65c5723:run.model_summary#intercept]]` | verified | -3.835505224 |
| 27 | conceptual_soundness | It was fitted with an intercept of -3.836 on 36013 loan-mont… | 36013 | count | n_train | train | eq | `[[art:a65c5723:run.model_summary#n_train]]` | verified | 36013 |
| 28 | conceptual_soundness | It was fitted with an intercept of -3.836 on 36013 loan-mont… | 934 | count | n_train_loans | train | eq | `[[art:a65c5723:run.model_summary#n_train_loans]]` | verified | 934 |
| 29 | conceptual_soundness | The feature inventory carries 12 features in total, of which… | 12 | count | n |  | eq | `[[art:61276a96:run.features#n]]` | verified | 12 |
| 30 | conceptual_soundness | The feature inventory carries 12 features in total, of which… | 5 | count | at_origination |  | eq | `[[art:61276a96:run.features#at_origination]]` | verified | 5 |
| 31 | conceptual_soundness | The feature inventory carries 12 features in total, of which… | 7 | count | before_period_start |  | eq | `[[art:61276a96:run.features#before_period_start]]` | verified | 7 |
| 32 | conceptual_soundness | No feature is dated to the performance period itself, at 0 ,… | 0 | count | during_period |  | eq | `[[art:61276a96:run.features#during_period]]` | verified | 0 |
| 33 | conceptual_soundness | No feature is dated to the performance period itself, at 0 ,… | 0 | count | after_outcome |  | eq | `[[art:61276a96:run.features#after_outcome]]` | verified | 0 |
| 34 | conceptual_soundness | The developer's own collinearity screen dropped two candidat… | 10 | ratio | vif_threshold |  | eq | `[[art:a65c5723:run.model_summary#vif_threshold]]` | verified | 10 |
| 35 | conceptual_soundness | The rate-change term was removed at 12.38 , which sits modes… | 12.38 | ratio | vif |  | eq | `[[art:a65c5723:run.model_summary#removed.rate_change_12m.vif]]` | verified | 12.377209 |
| 36 | conceptual_soundness | The log beginning-of-month balance was removed at 40090 , a… | 40090 | ratio | vif |  | eq | `[[art:a65c5723:run.model_summary#removed.bom_balance_log.vif]]` | verified | 40090.39108 |
| 37 | conceptual_soundness | The largest fitted coefficient is on the refinance incentive… | 1.228 | ratio | coefficient |  | eq | `[[art:a65c5723:run.model_summary#coefficients.incentive.value]]` | verified | 1.227953185 |
| 38 | conceptual_soundness | The largest fitted coefficient is on the refinance incentive… | 0.7963 | ratio | coefficient |  | eq | `[[art:a65c5723:run.model_summary#coefficients.loan_age_spline_1.value]]` | verified | 0.7963374016 |
| 39 | conceptual_soundness | The largest fitted coefficient is on the refinance incentive… | 0.397 | ratio | coefficient |  | eq | `[[art:a65c5723:run.model_summary#coefficients.credit_score.value]]` | verified | 0.3969645316 |
| 40 | conceptual_soundness | The remaining sizeable terms are the fourth loan-age spline… | -0.3846 | ratio | coefficient |  | eq | `[[art:a65c5723:run.model_summary#coefficients.loan_age_spline_4.value]]` | verified | -0.3845926837 |
| 41 | conceptual_soundness | The remaining sizeable terms are the fourth loan-age spline… | -0.3355 | ratio | coefficient |  | eq | `[[art:a65c5723:run.model_summary#coefficients.note_rate.value]]` | verified | -0.3355432002 |
| 42 | conceptual_soundness | The remaining sizeable terms are the fourth loan-age spline… | 0.2928 | ratio | coefficient |  | eq | `[[art:a65c5723:run.model_summary#coefficients.orig_upb_log.value]]` | verified | 0.2928204596 |
| 43 | conceptual_soundness | The remaining sizeable terms are the fourth loan-age spline… | -0.2355 | ratio | coefficient |  | eq | `[[art:a65c5723:run.model_summary#coefficients.orig_ltv.value]]` | verified | -0.2354994959 |
| 44 | conceptual_soundness | The smaller terms are the cosine seasonal term at -0.1303 ,… | -0.1303 | ratio | coefficient |  | eq | `[[art:a65c5723:run.model_summary#coefficients.season_cos.value]]` | verified | -0.1302954851 |
| 45 | conceptual_soundness | The smaller terms are the cosine seasonal term at -0.1303 ,… | 0.125 | ratio | coefficient |  | eq | `[[art:a65c5723:run.model_summary#coefficients.loan_age_spline_2.value]]` | verified | 0.1249554905 |
| 46 | conceptual_soundness | The smaller terms are the cosine seasonal term at -0.1303 ,… | -0.08435 | ratio | coefficient |  | eq | `[[art:a65c5723:run.model_summary#coefficients.loan_age_spline_3.value]]` | verified | -0.08434971245 |
| 47 | conceptual_soundness | The smaller terms are the cosine seasonal term at -0.1303 ,… | 0.06389 | ratio | coefficient |  | eq | `[[art:a65c5723:run.model_summary#coefficients.season_sin.value]]` | verified | 0.06389474731 |
| 48 | conceptual_soundness | The smaller terms are the cosine seasonal term at -0.1303 ,… | -0.0107 | ratio | coefficient |  | eq | `[[art:a65c5723:run.model_summary#coefficients.burnout.value]]` | verified | -0.01070330408 |
| 49 | conceptual_soundness | The smaller terms are the cosine seasonal term at -0.1303 ,… | -0.00802 | ratio | coefficient |  | eq | `[[art:a65c5723:run.model_summary#coefficients.sato.value]]` | verified | -0.008020059641 |
| 50 | conceptual_soundness | A positive incentive coefficient means borrowers refinance m… | 1 | ratio | coef_sign |  | eq | `[[art:684cf11a:sign_check.incentive.coef_sign]]` | verified | 1 |
| 51 | conceptual_soundness | A positive incentive coefficient means borrowers refinance m… | 1 | ratio | univariate_direction |  | eq | `[[art:8098d951:sign_check.incentive.univariate_direction]]` | verified | 1 |
| 52 | conceptual_soundness | A positive incentive coefficient means borrowers refinance m… | 1 | ratio | agrees |  | eq | `[[art:f7b2338e:sign_check.incentive.agrees]]` | verified | 1 |
| 53 | conceptual_soundness | Higher credit scores are conventionally associated with a gr… | 1 | ratio | coef_sign |  | eq | `[[art:1ec1078b:sign_check.credit_score.coef_sign]]` | verified | 1 |
| 54 | conceptual_soundness | Higher credit scores are conventionally associated with a gr… | 1 | ratio | univariate_direction |  | eq | `[[art:42303896:sign_check.credit_score.univariate_direction]]` | verified | 1 |
| 55 | conceptual_soundness | Higher credit scores are conventionally associated with a gr… | 1 | ratio | agrees |  | eq | `[[art:915bf8eb:sign_check.credit_score.agrees]]` | verified | 1 |
| 56 | conceptual_soundness | Larger original balances give a larger dollar saving from an… | 1 | ratio | coef_sign |  | eq | `[[art:5aa309fc:sign_check.orig_upb_log.coef_sign]]` | verified | 1 |
| 57 | conceptual_soundness | Larger original balances give a larger dollar saving from an… | 1 | ratio | univariate_direction |  | eq | `[[art:b9743ecb:sign_check.orig_upb_log.univariate_direction]]` | verified | 1 |
| 58 | conceptual_soundness | Larger original balances give a larger dollar saving from an… | 1 | ratio | agrees |  | eq | `[[art:07a9d3e6:sign_check.orig_upb_log.agrees]]` | verified | 1 |
| 59 | conceptual_soundness | Higher original loan-to-value impedes refinancing, and the n… | -1 | ratio | coef_sign |  | eq | `[[art:7eec65ec:sign_check.orig_ltv.coef_sign]]` | verified | -1 |
| 60 | conceptual_soundness | Higher original loan-to-value impedes refinancing, and the n… | -1 | ratio | univariate_direction |  | eq | `[[art:76dbc708:sign_check.orig_ltv.univariate_direction]]` | verified | -1 |
| 61 | conceptual_soundness | Higher original loan-to-value impedes refinancing, and the n… | 1 | ratio | agrees |  | eq | `[[art:7021aeb0:sign_check.orig_ltv.agrees]]` | verified | 1 |
| 62 | conceptual_soundness | Both seasonal terms also agree with their univariate directi… | 1 | ratio | agrees |  | eq | `[[art:e110f357:sign_check.season_sin.agrees]]` | verified | 1 |
| 63 | conceptual_soundness | Both seasonal terms also agree with their univariate directi… | 1 | ratio | agrees |  | eq | `[[art:7f18ddf7:sign_check.season_cos.agrees]]` | verified | 1 |
| 64 | conceptual_soundness | Ablation deltas are measured from a refit of the champion's… | 0.7673 | ratio | baseline_auc | test | eq | `[[art:54367df6:ablation.baseline_auc]]` | verified | 0.7672992275 |
| 65 | conceptual_soundness | The note rate is fitted negative at -1 against a univariate… | -1 | ratio | coef_sign |  | eq | `[[art:aecf7ccb:sign_check.note_rate.coef_sign]]` | verified | -1 |
| 66 | conceptual_soundness | The note rate is fitted negative at -1 against a univariate… | 1 | ratio | univariate_direction |  | eq | `[[art:61f6e1ac:sign_check.note_rate.univariate_direction]]` | verified | 1 |
| 67 | conceptual_soundness | The note rate is fitted negative at -1 against a univariate… | 0 | ratio | agrees |  | eq | `[[art:a453463d:sign_check.note_rate.agrees]]` | verified | 0 |
| 68 | conceptual_soundness | Dropping it moves test discrimination by -0.002585 , so the… | -0.002585 | ratio | delta_auc | test | eq | `[[art:14558b82:ablation.note_rate.delta_auc]]` | verified | -0.002585106068 |
| 69 | conceptual_soundness | The spread at origination is fitted negative at -1 against a… | -1 | ratio | coef_sign |  | eq | `[[art:265915cf:sign_check.sato.coef_sign]]` | verified | -1 |
| 70 | conceptual_soundness | The spread at origination is fitted negative at -1 against a… | 1 | ratio | univariate_direction |  | eq | `[[art:c08233a6:sign_check.sato.univariate_direction]]` | verified | 1 |
| 71 | conceptual_soundness | The spread at origination is fitted negative at -1 against a… | 0 | ratio | agrees |  | eq | `[[art:b3755963:sign_check.sato.agrees]]` | verified | 0 |
| 72 | conceptual_soundness | Removing it changes test discrimination by 0.0005201 , a mov… | 0.0005201 | ratio | delta_auc | test | eq | `[[art:57703504:ablation.sato.delta_auc]]` | verified | 0.0005200867657 |
| 73 | conceptual_soundness | Burnout is fitted negative at -1 against a univariate direct… | -1 | ratio | coef_sign |  | eq | `[[art:dcfb2de4:sign_check.burnout.coef_sign]]` | verified | -1 |
| 74 | conceptual_soundness | Burnout is fitted negative at -1 against a univariate direct… | 1 | ratio | univariate_direction |  | eq | `[[art:bfc96bb2:sign_check.burnout.univariate_direction]]` | verified | 1 |
| 75 | conceptual_soundness | Burnout is fitted negative at -1 against a univariate direct… | 0 | ratio | agrees |  | eq | `[[art:56826e40:sign_check.burnout.agrees]]` | verified | 0 |
| 76 | conceptual_soundness | Removing it changes test discrimination by -0.0001876 , the… | -0.0001876 | ratio | delta_auc | test | eq | `[[art:3cba039b:ablation.burnout.delta_auc]]` | verified | -0.0001876329287 |
| 77 | conceptual_soundness | Among the terms whose signs agree, the ablation evidence is… | -0.04117 | ratio | delta_auc | test | eq | `[[art:78108590:ablation.incentive.delta_auc]]` | verified | -0.0411745927 |
| 78 | conceptual_soundness | Among the terms whose signs agree, the ablation evidence is… | -0.01927 | ratio | delta_auc | test | eq | `[[art:0ddb11a9:ablation.orig_upb_log.delta_auc]]` | verified | -0.01926646624 |
| 79 | conceptual_soundness | Among the terms whose signs agree, the ablation evidence is… | -0.01474 | ratio | delta_auc | test | eq | `[[art:9bdeb0df:ablation.credit_score.delta_auc]]` | verified | -0.0147431913 |
| 80 | conceptual_soundness | The original loan-to-value ratio contributes -0.002294 , and… | -0.002294 | ratio | delta_auc | test | eq | `[[art:57ea66c5:ablation.orig_ltv.delta_auc]]` | verified | -0.002294407165 |
| 81 | conceptual_soundness | The original loan-to-value ratio contributes -0.002294 , and… | -0.0004826 | ratio | delta_auc | test | eq | `[[art:a288439d:ablation.season_cos.delta_auc]]` | verified | -0.00048256018 |
| 82 | conceptual_soundness | The original loan-to-value ratio contributes -0.002294 , and… | -0.0003885 | ratio | delta_auc | test | eq | `[[art:e54c8581:ablation.season_sin.delta_auc]]` | verified | -0.0003884794439 |
| 83 | conceptual_soundness | Loan age scores 0.0008166 when the spline is refitted out, m… | 0.0008166 | ratio | delta_auc | test | eq | `[[art:be669163:ablation.loan_age.delta_auc]]` | verified | 0.0008165996474 |
| 84 | conceptual_soundness | On effective challenge, the champion scores 0.7758 on test w… | 0.7758 | ratio | auc | test | eq | `[[art:2f4cab3e:metrics.test.auc]]` | verified | 0.7758373186 |
| 85 | conceptual_soundness | On effective challenge, the champion scores 0.7758 on test w… | 0.009864 | ratio | brier | test | eq | `[[art:1e4aab51:metrics.test.brier]]` | verified | 0.009863834665 |
| 86 | conceptual_soundness | The challenger scores 0.7337 on test with a Brier score of 0… | 0.7337 | ratio | auc | test | eq | `[[art:705b66f0:challenger.auc]]` | verified | 0.7337079121 |
| 87 | conceptual_soundness | The challenger scores 0.7337 on test with a Brier score of 0… | 0.00863 | ratio | brier | test | eq | `[[art:85a89ef9:challenger.brier]]` | verified | 0.008629514666 |
| 88 | conceptual_soundness | The difference in discrimination is -0.04213 , and the thres… | -0.04213 | ratio | delta_auc | test | eq | `[[art:1e990f53:challenger.delta_auc]]` | verified | -0.04212940647 |
| 89 | conceptual_soundness | The difference in discrimination is -0.04213 , and the thres… | 0.03 | ratio | delta_auc |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 90 | data_integrity | The training split holds 36013 rows , the test split 15382 r… | 36013 | count | profile.n | train | eq | `[[art:c5ebd9c9:profile.train.n]]` | verified | 36013 |
| 91 | data_integrity | The training split holds 36013 rows , the test split 15382 r… | 15382 | count | profile.n | test | eq | `[[art:e3abc1b8:profile.test.n]]` | verified | 15382 |
| 92 | data_integrity | The training split holds 36013 rows , the test split 15382 r… | 32177 | count | profile.n | vintage_holdout | eq | `[[art:426e712a:profile.vintage_holdout.n]]` | verified | 32177 |
| 93 | data_integrity | The training split holds 36013 rows , the test split 15382 r… | 12257 | count | profile.n | out_of_time | eq | `[[art:fa39c5cf:profile.out_of_time.n]]` | verified | 12257 |
| 94 | data_integrity | The largest missing fraction over any column is 0 in the tra… | 0 | ratio | profile.missing.max | train | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 95 | data_integrity | The largest missing fraction over any column is 0 in the tra… | 0 | ratio | profile.missing.max | test | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 96 | data_integrity | The largest missing fraction over any column is 0 in the tra… | 0 | ratio | profile.missing.max | vintage_holdout | eq | `[[art:329bb430:profile.vintage_holdout.missing.max]]` | verified | 0 |
| 97 | data_integrity | The largest missing fraction over any column is 0 in the tra… | 0 | ratio | profile.missing.max | out_of_time | eq | `[[art:4dafce11:profile.out_of_time.missing.max]]` | verified | 0 |
| 98 | data_integrity | The declared bound on the missingness gap between splits is… | 0.1 | ratio | threshold.missing_gap |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 99 | data_integrity | The declared stability bound is 0.25 , stated for the traini… | 0.25 | ratio | threshold.psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 100 | data_integrity | The declared stability bound is 0.25 , stated for the traini… | 0.25 | ratio | threshold.psi.max |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 101 | data_integrity | - burnout: 0.004614 | 0.004614 | ratio | psi | test | eq | `[[art:9dc7ecc2:psi.burnout]]` | verified | 0.004614338236 |
| 102 | data_integrity | - credit_score: 0.06189 | 0.06189 | ratio | psi | test | eq | `[[art:7e87527c:psi.credit_score]]` | verified | 0.06188985797 |
| 103 | data_integrity | - incentive: 0.0009923 | 0.0009923 | ratio | psi | test | eq | `[[art:2da5570f:psi.incentive]]` | verified | 0.0009922551416 |
| 104 | data_integrity | - loan_age: 0.0001994 | 0.0001994 | ratio | psi | test | eq | `[[art:2202b157:psi.loan_age]]` | verified | 0.0001993816816 |
| 105 | data_integrity | - note_rate: 0.01371 | 0.01371 | ratio | psi | test | eq | `[[art:ecc6adf3:psi.note_rate]]` | verified | 0.01370911382 |
| 106 | data_integrity | - orig_ltv: 0.03617 | 0.03617 | ratio | psi | test | eq | `[[art:cd1ff136:psi.orig_ltv]]` | verified | 0.03617297258 |
| 107 | data_integrity | - orig_upb_log: 0.04817 | 0.04817 | ratio | psi | test | eq | `[[art:55030a3b:psi.orig_upb_log]]` | verified | 0.04817081196 |
| 108 | data_integrity | - sato: 0.02773 | 0.02773 | ratio | psi | test | eq | `[[art:584da64f:psi.sato]]` | verified | 0.02772829856 |
| 109 | data_integrity | - season_cos: 1.79e-05 | 1.79e-05 | ratio | psi | test | eq | `[[art:addec503:psi.season_cos]]` | verified | 1.790085913e-05 |
| 110 | data_integrity | - season_sin: 2.939e-06 | 2.939e-06 | ratio | psi | test | eq | `[[art:4d2ed98d:psi.season_sin]]` | verified | 2.939045338e-06 |
| 111 | data_integrity | - score: 0.001869 | 0.001869 | ratio | psi | test | eq | `[[art:aa10164c:psi.y_score]]` | verified | 0.001868586849 |
| 112 | data_integrity | The largest of these, score included, is 0.06189 , carried b… | 0.06189 | ratio | psi.max | test | eq | `[[art:c2e8c8fd:psi.max]]` | verified | 0.06188985797 |
| 113 | data_integrity | The largest of these, score included, is 0.06189 , carried b… | 0.06189 | ratio | psi | test | eq | `[[art:7e87527c:psi.credit_score]]` | verified | 0.06188985797 |
| 114 | data_integrity | The largest of these, score included, is 0.06189 , carried b… | 0.25 | ratio | threshold.psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 115 | data_integrity | - burnout: 0.04749 | 0.04749 | ratio | psi | vintage_holdout | eq | `[[art:e29067e6:psi.vintage_holdout.burnout]]` | verified | 0.04749372789 |
| 116 | data_integrity | - credit_score: 0.03996 | 0.03996 | ratio | psi | vintage_holdout | eq | `[[art:3498d307:psi.vintage_holdout.credit_score]]` | verified | 0.03995819732 |
| 117 | data_integrity | - incentive: 0.4475 | 0.4475 | ratio | psi | vintage_holdout | eq | `[[art:5e61b6f9:psi.vintage_holdout.incentive]]` | verified | 0.4475226601 |
| 118 | data_integrity | - loan_age: 0.07112 | 0.07112 | ratio | psi | vintage_holdout | eq | `[[art:6d92c48b:psi.vintage_holdout.loan_age]]` | verified | 0.07111526296 |
| 119 | data_integrity | - note_rate: 0.6088 | 0.6088 | ratio | psi | vintage_holdout | eq | `[[art:f281f8a7:psi.vintage_holdout.note_rate]]` | verified | 0.608822927 |
| 120 | data_integrity | - orig_ltv: 0.02942 | 0.02942 | ratio | psi | vintage_holdout | eq | `[[art:d07cfb7d:psi.vintage_holdout.orig_ltv]]` | verified | 0.0294150369 |
| 121 | data_integrity | - orig_upb_log: 0.0404 | 0.0404 | ratio | psi | vintage_holdout | eq | `[[art:77ec758a:psi.vintage_holdout.orig_upb_log]]` | verified | 0.04039645306 |
| 122 | data_integrity | - sato: 0.02989 | 0.02989 | ratio | psi | vintage_holdout | eq | `[[art:eea64c25:psi.vintage_holdout.sato]]` | verified | 0.02989256711 |
| 123 | data_integrity | - season_cos: 0.001288 | 0.001288 | ratio | psi | vintage_holdout | eq | `[[art:9fe842a8:psi.vintage_holdout.season_cos]]` | verified | 0.0012879007 |
| 124 | data_integrity | - season_sin: 0.0007309 | 0.0007309 | ratio | psi | vintage_holdout | eq | `[[art:b0dc9745:psi.vintage_holdout.season_sin]]` | verified | 0.0007309374015 |
| 125 | data_integrity | - score: 0.1604 | 0.1604 | ratio | psi | vintage_holdout | eq | `[[art:c71062d6:psi.vintage_holdout.y_score]]` | verified | 0.1603916415 |
| 126 | data_integrity | - burnout: 2.945 | 2.945 | ratio | psi | out_of_time | eq | `[[art:7b0bbebb:psi.out_of_time.burnout]]` | verified | 2.944521522 |
| 127 | data_integrity | - credit_score: 0.05988 | 0.05988 | ratio | psi | out_of_time | eq | `[[art:d7249e47:psi.out_of_time.credit_score]]` | verified | 0.05987964443 |
| 128 | data_integrity | - incentive: 0.4958 | 0.4958 | ratio | psi | out_of_time | eq | `[[art:42076ed1:psi.out_of_time.incentive]]` | verified | 0.4958065489 |
| 129 | data_integrity | - loan_age: 2.484 | 2.484 | ratio | psi | out_of_time | eq | `[[art:d6eaaaf5:psi.out_of_time.loan_age]]` | verified | 2.483993033 |
| 130 | data_integrity | - note_rate: 0.6977 | 0.6977 | ratio | psi | out_of_time | eq | `[[art:cabd371d:psi.out_of_time.note_rate]]` | verified | 0.6976589281 |
| 131 | data_integrity | - orig_ltv: 0.04301 | 0.04301 | ratio | psi | out_of_time | eq | `[[art:3eee5db4:psi.out_of_time.orig_ltv]]` | verified | 0.04300793312 |
| 132 | data_integrity | - orig_upb_log: 0.07136 | 0.07136 | ratio | psi | out_of_time | eq | `[[art:ac349b67:psi.out_of_time.orig_upb_log]]` | verified | 0.07136421414 |
| 133 | data_integrity | - sato: 0.01299 | 0.01299 | ratio | psi | out_of_time | eq | `[[art:c2233ce6:psi.out_of_time.sato]]` | verified | 0.01298850667 |
| 134 | data_integrity | - season_cos: 0.007524 | 0.007524 | ratio | psi | out_of_time | eq | `[[art:25cf6b85:psi.out_of_time.season_cos]]` | verified | 0.00752368457 |
| 135 | data_integrity | - season_sin: 0.02789 | 0.02789 | ratio | psi | out_of_time | eq | `[[art:144e1bd9:psi.out_of_time.season_sin]]` | verified | 0.02788988464 |
| 136 | data_integrity | - score: 0.6985 | 0.6985 | ratio | psi | out_of_time | eq | `[[art:6f080528:psi.out_of_time.y_score]]` | verified | 0.6984990823 |
| 137 | data_integrity | The declared bound of 0.25 is written for the training split… | 0.25 | ratio | threshold.psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 138 | data_integrity | Read that way, the vintage holdout stands above the bound on… | 0.4475 | ratio | psi | vintage_holdout | eq | `[[art:5e61b6f9:psi.vintage_holdout.incentive]]` | verified | 0.4475226601 |
| 139 | data_integrity | Read that way, the vintage holdout stands above the bound on… | 0.6088 | ratio | psi | vintage_holdout | eq | `[[art:f281f8a7:psi.vintage_holdout.note_rate]]` | verified | 0.608822927 |
| 140 | data_integrity | Read that way, the vintage holdout stands above the bound on… | 0.1604 | ratio | psi | vintage_holdout | eq | `[[art:c71062d6:psi.vintage_holdout.y_score]]` | verified | 0.1603916415 |
| 141 | data_integrity | Read the same way, the out-of-time split stands above the bo… | 2.945 | ratio | psi | out_of_time | eq | `[[art:7b0bbebb:psi.out_of_time.burnout]]` | verified | 2.944521522 |
| 142 | data_integrity | Read the same way, the out-of-time split stands above the bo… | 2.484 | ratio | psi | out_of_time | eq | `[[art:d6eaaaf5:psi.out_of_time.loan_age]]` | verified | 2.483993033 |
| 143 | data_integrity | Read the same way, the out-of-time split stands above the bo… | 0.6977 | ratio | psi | out_of_time | eq | `[[art:cabd371d:psi.out_of_time.note_rate]]` | verified | 0.6976589281 |
| 144 | data_integrity | Read the same way, the out-of-time split stands above the bo… | 0.4958 | ratio | psi | out_of_time | eq | `[[art:42076ed1:psi.out_of_time.incentive]]` | verified | 0.4958065489 |
| 145 | data_integrity | Read the same way, the out-of-time split stands above the bo… | 0.6985 | ratio | psi | out_of_time | eq | `[[art:6f080528:psi.out_of_time.y_score]]` | verified | 0.6984990823 |
| 146 | data_integrity | - burnout: 0.0001326 | 0.0001326 | ratio | csi |  | eq | `[[art:640f9435:csi.burnout]]` | verified | 0.0001325955583 |
| 147 | data_integrity | - credit_score: 0.007707 | 0.007707 | ratio | csi |  | eq | `[[art:6653968a:csi.credit_score]]` | verified | 0.007706951731 |
| 148 | data_integrity | - incentive: 0.005686 | 0.005686 | ratio | csi |  | eq | `[[art:3bfa986b:csi.incentive]]` | verified | 0.005685694124 |
| 149 | data_integrity | - loan_age: 0 | 0 | ratio | csi |  | eq | `[[art:df52c920:csi.loan_age]]` | verified | 0 |
| 150 | data_integrity | - note_rate: 0.01372 | 0.01372 | ratio | csi |  | eq | `[[art:e06d8658:csi.note_rate]]` | verified | 0.01371659455 |
| 151 | data_integrity | - orig_ltv: 0.03331 | 0.03331 | ratio | csi |  | eq | `[[art:7a941368:csi.orig_ltv]]` | verified | 0.03331391493 |
| 152 | data_integrity | - orig_upb_log: 0.002863 | 0.002863 | ratio | csi |  | eq | `[[art:bbbec9d2:csi.orig_upb_log]]` | verified | 0.002863276289 |
| 153 | data_integrity | - sato: 0.0009305 | 0.0009305 | ratio | csi |  | eq | `[[art:c9bad372:csi.sato]]` | verified | 0.0009304918233 |
| 154 | data_integrity | - season_cos: 0.0005034 | 0.0005034 | ratio | csi |  | eq | `[[art:78d740c8:csi.season_cos]]` | verified | 0.0005033620785 |
| 155 | data_integrity | - season_sin: 6.94e-05 | 6.94e-05 | ratio | csi |  | eq | `[[art:d16ad42f:csi.season_sin]]` | verified | 6.939549558e-05 |
| 156 | data_integrity | The largest characteristic contribution is 0.03331 , carried… | 0.03331 | ratio | csi.max |  | eq | `[[art:a8ca288d:csi.max]]` | verified | 0.03331391493 |
| 157 | data_integrity | The largest characteristic contribution is 0.03331 , carried… | 0.03331 | ratio | csi |  | eq | `[[art:7a941368:csi.orig_ltv]]` | verified | 0.03331391493 |
| 158 | data_integrity | The largest characteristic contribution is 0.03331 , carried… | 0.25 | ratio | threshold.psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 159 | data_integrity | Features declared as observed during the period or after the… | 0 | count | leakage.timing.n_flagged |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 160 | data_integrity | The strongest single feature reaches an AUC of 0.7239 , belo… | 0.7239 | ratio | leakage.target_corr.max_single_feature_auc |  | eq | `[[art:1fe630dd:leakage.target_corr.max_single_feature_auc]]` | verified | 0.7238936567 |
| 161 | data_integrity | The strongest single feature reaches an AUC of 0.7239 , belo… | 0.9 | ratio | threshold.single_feature_auc |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 162 | data_integrity | Feature names matching the target-adjacent lexicon number 0… | 0 | count | leakage.name_screen.n_matched |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 163 | data_integrity | On the identifier arm, the share of test rows whose loan and… | 0 | ratio | leakage.overlap.ids | test | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 164 | data_integrity | On the identifier arm, the share of test rows whose loan and… | 0.005 | ratio | threshold.overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 165 | data_integrity | On the feature arm, the rule applies not the declared bound… | 0 | ratio | leakage.duplicates | train | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 166 | data_integrity | Here the declared value is the larger of the two, and the bo… | 0.005 | ratio | threshold.overlap.features_effective |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 167 | data_integrity | The share of test rows whose feature values also appear in t… | 0 | ratio | leakage.overlap.features | test | eq | `[[art:0fec8048:leakage.overlap.features]]` | verified | 0 |
| 168 | data_integrity | The share of test rows whose feature values also appear in t… | 0.005 | ratio | threshold.overlap.features_effective |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 169 | data_integrity | The overall row-overlap screen reads 0 , likewise below the… | 0 | ratio | leakage.overlap |  | eq | `[[art:4c9fcd09:leakage.overlap]]` | verified | 0 |
| 170 | data_integrity | The overall row-overlap screen reads 0 , likewise below the… | 0.005 | ratio | threshold.overlap.features_effective |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 171 | data_integrity | Because the duplicate share within train is 0 , the widening… | 0 | ratio | leakage.duplicates | train | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 172 | outcomes | The logistic regression of the outcome on the logit of the p… | 1.015 | ratio | calibration_slope | train | eq | `[[art:ffabb935:calibration_slope.train]]` | verified | 1.014728573 |
| 173 | outcomes | The logistic regression of the outcome on the logit of the p… | 0.9537 | ratio | calibration_slope | test | eq | `[[art:f8ef2beb:calibration_slope.test]]` | verified | 0.9536630305 |
| 174 | outcomes | The logistic regression of the outcome on the logit of the p… | 1.066 | ratio | calibration_slope | out_of_time | eq | `[[art:ea7d5696:calibration_slope.out_of_time]]` | verified | 1.066358183 |
| 175 | outcomes | The logistic regression of the outcome on the logit of the p… | 0.8562 | ratio | calibration_slope | vintage_holdout | eq | `[[art:010c0ec4:calibration_slope.vintage_holdout]]` | verified | 0.8561504457 |
| 176 | outcomes | Each of those slopes sits inside the declared band, which ru… | 0.8 | ratio | calibration_slope |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 177 | outcomes | Each of those slopes sits inside the declared band, which ru… | 1.2 | ratio | calibration_slope |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 178 | outcomes | The intercept of that same regression is -1.566 on train, -1… | -1.566 | ratio | calibration_intercept | train | eq | `[[art:57309d7d:calibration_intercept.train]]` | verified | -1.566304198 |
| 179 | outcomes | The intercept of that same regression is -1.566 on train, -1… | -1.748 | ratio | calibration_intercept | test | eq | `[[art:257fb817:calibration_intercept.test]]` | verified | -1.747805271 |
| 180 | outcomes | The intercept of that same regression is -1.566 on train, -1… | -1.497 | ratio | calibration_intercept | out_of_time | eq | `[[art:db324216:calibration_intercept.out_of_time]]` | verified | -1.496633503 |
| 181 | outcomes | The intercept of that same regression is -1.566 on train, -1… | -2.176 | ratio | calibration_intercept | vintage_holdout | eq | `[[art:6f00dbc2:calibration_intercept.vintage_holdout]]` | verified | -2.175702334 |
| 182 | outcomes | On train the mean predicted probability is 0.03925 against a… | 0.03925 | ratio | mean_predicted | train | eq | `[[art:68f41b88:metrics.train.mean_predicted]]` | verified | 0.03925176105 |
| 183 | outcomes | On train the mean predicted probability is 0.03925 against a… | 0.008525 | ratio | event_rate | train | eq | `[[art:b9ef3327:metrics.train.event_rate]]` | verified | 0.008524699414 |
| 184 | outcomes | On train the mean predicted probability is 0.03925 against a… | 3.604 | ratio | mean_rel_gap | train | eq | `[[art:324eb124:calibration.mean_rel_gap.train]]` | verified | 3.604474497 |
| 185 | outcomes | On train the mean predicted probability is 0.03925 against a… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 186 | outcomes | On test the mean predicted probability is 0.03802 against an… | 0.03802 | ratio | mean_predicted | test | eq | `[[art:122af437:metrics.test.mean_predicted]]` | verified | 0.038020619 |
| 187 | outcomes | On test the mean predicted probability is 0.03802 against an… | 0.008061 | ratio | event_rate | test | eq | `[[art:570cc08a:metrics.test.event_rate]]` | verified | 0.008061370433 |
| 188 | outcomes | On test the mean predicted probability is 0.03802 against an… | 3.716 | ratio | mean_rel_gap | test | eq | `[[art:15d5555b:calibration.mean_rel_gap.test]]` | verified | 3.716396464 |
| 189 | outcomes | On test the mean predicted probability is 0.03802 against an… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 190 | outcomes | On out of time the mean predicted probability is 0.07793 aga… | 0.07793 | ratio | mean_predicted | out_of_time | eq | `[[art:921d185b:metrics.out_of_time.mean_predicted]]` | verified | 0.07792752696 |
| 191 | outcomes | On out of time the mean predicted probability is 0.07793 aga… | 0.01795 | ratio | event_rate | out_of_time | eq | `[[art:83ccf5c0:metrics.out_of_time.event_rate]]` | verified | 0.01794892714 |
| 192 | outcomes | On out of time the mean predicted probability is 0.07793 aga… | 3.342 | ratio | mean_rel_gap | out_of_time | eq | `[[art:5b8375ec:calibration.mean_rel_gap.out_of_time]]` | verified | 3.3416259 |
| 193 | outcomes | On the vintage holdout the mean predicted probability is 0.0… | 0.02582 | ratio | mean_predicted | vintage_holdout | eq | `[[art:348107ae:metrics.vintage_holdout.mean_predicted]]` | verified | 0.02582080379 |
| 194 | outcomes | On the vintage holdout the mean predicted probability is 0.0… | 0.004817 | ratio | event_rate | vintage_holdout | eq | `[[art:e3590a16:metrics.vintage_holdout.event_rate]]` | verified | 0.004817105386 |
| 195 | outcomes | On the vintage holdout the mean predicted probability is 0.0… | 4.36 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:a691b5ed:calibration.mean_rel_gap.vintage_holdout]]` | verified | 4.360232281 |
| 196 | outcomes | The same picture appears in the prepayment rate comparison,… | 0.224 | ratio | cpr_mae | train | eq | `[[art:8d8e2c42:cpr.train.mae]]` | verified | 0.2239621374 |
| 197 | outcomes | The same picture appears in the prepayment rate comparison,… | 0.222 | ratio | cpr_mae | test | eq | `[[art:b7587aed:cpr.test.mae]]` | verified | 0.222029929 |
| 198 | outcomes | The same picture appears in the prepayment rate comparison,… | 0.318 | ratio | cpr_mae | out_of_time | eq | `[[art:8ac7bfbc:cpr.out_of_time.mae]]` | verified | 0.3179874584 |
| 199 | outcomes | The same picture appears in the prepayment rate comparison,… | 0.172 | ratio | cpr_mae | vintage_holdout | eq | `[[art:2d48e163:cpr.vintage_holdout.mae]]` | verified | 0.1720007526 |
| 200 | outcomes | \| AUC \| 0.7892 \| 0.7758 \| 0.7898 \| 0.7743 \| | 0.7892 | ratio | auc | train | eq | `[[art:39508266:metrics.train.auc]]` | verified | 0.7891607921 |
| 201 | outcomes | \| AUC \| 0.7892 \| 0.7758 \| 0.7898 \| 0.7743 \| | 0.7758 | ratio | auc | test | eq | `[[art:2f4cab3e:metrics.test.auc]]` | verified | 0.7758373186 |
| 202 | outcomes | \| AUC \| 0.7892 \| 0.7758 \| 0.7898 \| 0.7743 \| | 0.7898 | ratio | auc | out_of_time | eq | `[[art:aa836722:metrics.out_of_time.auc]]` | verified | 0.7897867937 |
| 203 | outcomes | \| AUC \| 0.7892 \| 0.7758 \| 0.7898 \| 0.7743 \| | 0.7743 | ratio | auc | vintage_holdout | eq | `[[art:25db8aa3:metrics.vintage_holdout.auc]]` | verified | 0.7742985165 |
| 204 | outcomes | \| Gini \| 0.5783 \| 0.5517 \| 0.5796 \| 0.5486 \| | 0.5783 | ratio | gini | train | eq | `[[art:d618ff0f:metrics.train.gini]]` | verified | 0.5783215843 |
| 205 | outcomes | \| Gini \| 0.5783 \| 0.5517 \| 0.5796 \| 0.5486 \| | 0.5517 | ratio | gini | test | eq | `[[art:8593585c:metrics.test.gini]]` | verified | 0.5516746371 |
| 206 | outcomes | \| Gini \| 0.5783 \| 0.5517 \| 0.5796 \| 0.5486 \| | 0.5796 | ratio | gini | out_of_time | eq | `[[art:3dc07327:metrics.out_of_time.gini]]` | verified | 0.5795735875 |
| 207 | outcomes | \| Gini \| 0.5783 \| 0.5517 \| 0.5796 \| 0.5486 \| | 0.5486 | ratio | gini | vintage_holdout | eq | `[[art:eff9b345:metrics.vintage_holdout.gini]]` | verified | 0.5485970331 |
| 208 | outcomes | \| KS \| 0.4542 \| 0.428 \| 0.4368 \| 0.4531 \| | 0.4542 | ratio | ks | train | eq | `[[art:e8d4ae61:metrics.train.ks]]` | verified | 0.4541800929 |
| 209 | outcomes | \| KS \| 0.4542 \| 0.428 \| 0.4368 \| 0.4531 \| | 0.428 | ratio | ks | test | eq | `[[art:554f1e19:metrics.test.ks]]` | verified | 0.4280398649 |
| 210 | outcomes | \| KS \| 0.4542 \| 0.428 \| 0.4368 \| 0.4531 \| | 0.4368 | ratio | ks | out_of_time | eq | `[[art:00bf02ed:metrics.out_of_time.ks]]` | verified | 0.43678733 |
| 211 | outcomes | \| KS \| 0.4542 \| 0.428 \| 0.4368 \| 0.4531 \| | 0.4531 | ratio | ks | vintage_holdout | eq | `[[art:a2ee5005:metrics.vintage_holdout.ks]]` | verified | 0.4530637203 |
| 212 | outcomes | \| Brier \| 0.01036 \| 0.009864 \| 0.02402 \| 0.006101 \| | 0.01036 | ratio | brier | train | eq | `[[art:d56a10b2:metrics.train.brier]]` | verified | 0.01035868886 |
| 213 | outcomes | \| Brier \| 0.01036 \| 0.009864 \| 0.02402 \| 0.006101 \| | 0.009864 | ratio | brier | test | eq | `[[art:1e4aab51:metrics.test.brier]]` | verified | 0.009863834665 |
| 214 | outcomes | \| Brier \| 0.01036 \| 0.009864 \| 0.02402 \| 0.006101 \| | 0.02402 | ratio | brier | out_of_time | eq | `[[art:a8a8d3a5:metrics.out_of_time.brier]]` | verified | 0.02402096444 |
| 215 | outcomes | \| Brier \| 0.01036 \| 0.009864 \| 0.02402 \| 0.006101 \| | 0.006101 | ratio | brier | vintage_holdout | eq | `[[art:55737812:metrics.vintage_holdout.brier]]` | verified | 0.006100676477 |
| 216 | outcomes | \| Log loss \| 0.06297 \| 0.06118 \| 0.1174 \| 0.04161 \| | 0.06297 | ratio | logloss | train | eq | `[[art:2bff29d3:metrics.train.logloss]]` | verified | 0.06296558061 |
| 217 | outcomes | \| Log loss \| 0.06297 \| 0.06118 \| 0.1174 \| 0.04161 \| | 0.06118 | ratio | logloss | test | eq | `[[art:b9424e16:metrics.test.logloss]]` | verified | 0.06118235348 |
| 218 | outcomes | \| Log loss \| 0.06297 \| 0.06118 \| 0.1174 \| 0.04161 \| | 0.1174 | ratio | logloss | out_of_time | eq | `[[art:5198f968:metrics.out_of_time.logloss]]` | verified | 0.1173954835 |
| 219 | outcomes | \| Log loss \| 0.06297 \| 0.06118 \| 0.1174 \| 0.04161 \| | 0.04161 | ratio | logloss | vintage_holdout | eq | `[[art:9f19871a:metrics.vintage_holdout.logloss]]` | verified | 0.04161346969 |
| 220 | outcomes | \| Share of events in the top two deciles \| 0.6059 \| 0.5806 \|… | 0.6059 | ratio | top2_capture | train | eq | `[[art:eb38637b:deciles.train.top2_capture]]` | verified | 0.6058631922 |
| 221 | outcomes | \| Share of events in the top two deciles \| 0.6059 \| 0.5806 \|… | 0.5806 | ratio | top2_capture | test | eq | `[[art:43c4adc5:deciles.test.top2_capture]]` | verified | 0.5806451613 |
| 222 | outcomes | \| Share of events in the top two deciles \| 0.6059 \| 0.5806 \|… | 0.5909 | ratio | top2_capture | out_of_time | eq | `[[art:95c24730:deciles.out_of_time.top2_capture]]` | verified | 0.5909090909 |
| 223 | outcomes | \| Share of events in the top two deciles \| 0.6059 \| 0.5806 \|… | 0.5935 | ratio | top2_capture | vintage_holdout | eq | `[[art:4a376307:deciles.vintage_holdout.top2_capture]]` | verified | 0.5935483871 |
| 224 | outcomes | \| Rows \| 36013 \| 15382 \| 12257 \| 32177 \| | 36013 | count | n | train | eq | `[[art:6fdfeabb:metrics.train.n]]` | verified | 36013 |
| 225 | outcomes | \| Rows \| 36013 \| 15382 \| 12257 \| 32177 \| | 15382 | count | n | test | eq | `[[art:e55953e1:metrics.test.n]]` | verified | 15382 |
| 226 | outcomes | \| Rows \| 36013 \| 15382 \| 12257 \| 32177 \| | 12257 | count | n | out_of_time | eq | `[[art:7898809e:metrics.out_of_time.n]]` | verified | 12257 |
| 227 | outcomes | \| Rows \| 36013 \| 15382 \| 12257 \| 32177 \| | 32177 | count | n | vintage_holdout | eq | `[[art:37a92951:metrics.vintage_holdout.n]]` | verified | 32177 |
| 228 | outcomes | AUC on train, at 0.7892 , stands above AUC on test, at 0.775… | 0.7892 | ratio | auc | train | eq | `[[art:39508266:metrics.train.auc]]` | verified | 0.7891607921 |
| 229 | outcomes | AUC on train, at 0.7892 , stands above AUC on test, at 0.775… | 0.7758 | ratio | auc | test | eq | `[[art:2f4cab3e:metrics.test.auc]]` | verified | 0.7758373186 |
| 230 | outcomes | AUC on train, at 0.7892 , stands above AUC on test, at 0.775… | 0.08 | ratio | auc_gap |  | eq | `[[art:630f28f4:threshold.O1.auc_gap]]` | verified | 0.08 |
| 231 | outcomes | The table sets each bound package.yaml declares against the… | 0.65 | ratio | auc | test | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 232 | outcomes | The table sets each bound package.yaml declares against the… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 233 | outcomes | The table sets each bound package.yaml declares against the… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 234 | outcomes | The table sets each bound package.yaml declares against the… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 235 | outcomes | AUC on this slice falls below the split's own by 0.06959 on… | 0.06959 | ratio | auc_gap | train | eq | `[[art:572da87a:metrics.train.sub.incentive_high.auc_gap]]` | verified | 0.06958915791 |
| 236 | outcomes | AUC on this slice falls below the split's own by 0.06959 on… | 0.04774 | ratio | auc_gap | test | eq | `[[art:d7fc769c:metrics.test.sub.incentive_high.auc_gap]]` | verified | 0.04774016101 |
| 237 | outcomes | AUC on this slice falls below the split's own by 0.06959 on… | 0.03623 | ratio | auc_gap | out_of_time | eq | `[[art:ba620fbd:metrics.out_of_time.sub.incentive_high.auc_gap]]` | verified | 0.03623305516 |
| 238 | outcomes | AUC on this slice falls below the split's own by 0.06959 on… | 0.02106 | ratio | auc_gap | vintage_holdout | eq | `[[art:6182ebaa:metrics.vintage_holdout.sub.incentive_high.auc_gap]]` | verified | 0.02106338819 |
| 239 | outcomes | AUC on this slice falls below the split's own by 0.06959 on… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 240 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.4999 of out of… | 0.5 | ratio | share | train | eq | `[[art:277218fb:metrics.train.sub.incentive_high.share]]` | verified | 0.4999861161 |
| 241 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.4999 of out of… | 0.5 | ratio | share | test | eq | `[[art:549aa934:metrics.test.sub.incentive_high.share]]` | verified | 0.5 |
| 242 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.4999 of out of… | 0.4999 | ratio | share | out_of_time | eq | `[[art:431d1ff2:metrics.out_of_time.sub.incentive_high.share]]` | verified | 0.499877621 |
| 243 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.4999 of out of… | 0.5 | ratio | share | vintage_holdout | eq | `[[art:cb627056:metrics.vintage_holdout.sub.incentive_high.share]]` | verified | 0.499984461 |
| 244 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.4999 of out of… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 245 | outcomes | Mean predicted against observed on the slice, relative, is 3… | 3.518 | ratio | mean_rel_gap | train | eq | `[[art:03dd3e85:metrics.train.sub.incentive_high.mean_rel_gap]]` | verified | 3.51794689 |
| 246 | outcomes | Mean predicted against observed on the slice, relative, is 3… | 3.773 | ratio | mean_rel_gap | test | eq | `[[art:ddf406ce:metrics.test.sub.incentive_high.mean_rel_gap]]` | verified | 3.772978457 |
| 247 | outcomes | Mean predicted against observed on the slice, relative, is 3… | 3.452 | ratio | mean_rel_gap | out_of_time | eq | `[[art:1db4a82a:metrics.out_of_time.sub.incentive_high.mean_rel_gap]]` | verified | 3.452467592 |
| 248 | outcomes | Mean predicted against observed on the slice, relative, is 3… | 4.842 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:1aef21da:metrics.vintage_holdout.sub.incentive_high.mean_rel_gap]]` | verified | 4.841555374 |
| 249 | outcomes | Mean predicted against observed on the slice, relative, is 3… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 250 | outcomes | AUC on this slice falls below the split's own by 0.06733 on… | 0.06733 | ratio | auc_gap | train | eq | `[[art:bdcd3ce1:metrics.train.sub.incentive_low.auc_gap]]` | verified | 0.06733139884 |
| 251 | outcomes | AUC on this slice falls below the split's own by 0.06733 on… | 0.01935 | ratio | auc_gap | out_of_time | eq | `[[art:6bcab8af:metrics.out_of_time.sub.incentive_low.auc_gap]]` | verified | 0.01934527728 |
| 252 | outcomes | AUC on this slice falls below the split's own by 0.06733 on… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 253 | outcomes | On test the shortfall is 0.09364 and on the vintage holdout… | 0.09364 | ratio | auc_gap | test | eq | `[[art:b062501e:metrics.test.sub.incentive_low.auc_gap]]` | verified | 0.09364027153 |
| 254 | outcomes | On test the shortfall is 0.09364 and on the vintage holdout… | 0.08994 | ratio | auc_gap | vintage_holdout | eq | `[[art:40f8b479:metrics.vintage_holdout.sub.incentive_low.auc_gap]]` | verified | 0.08994391339 |
| 255 | outcomes | On test the shortfall is 0.09364 and on the vintage holdout… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 256 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.5001 of out of… | 0.5 | ratio | share | train | eq | `[[art:d7af12f0:metrics.train.sub.incentive_low.share]]` | verified | 0.5000138839 |
| 257 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.5001 of out of… | 0.5 | ratio | share | test | eq | `[[art:1d5dd4c2:metrics.test.sub.incentive_low.share]]` | verified | 0.5 |
| 258 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.5001 of out of… | 0.5001 | ratio | share | out_of_time | eq | `[[art:c7aaafd2:metrics.out_of_time.sub.incentive_low.share]]` | verified | 0.500122379 |
| 259 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.5001 of out of… | 0.5 | ratio | share | vintage_holdout | eq | `[[art:d94e6531:metrics.vintage_holdout.sub.incentive_low.share]]` | verified | 0.500015539 |
| 260 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.5001 of out of… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 261 | outcomes | Mean predicted against observed on the slice, relative, is 4… | 4.06 | ratio | mean_rel_gap | train | eq | `[[art:48122349:metrics.train.sub.incentive_low.mean_rel_gap]]` | verified | 4.060068838 |
| 262 | outcomes | Mean predicted against observed on the slice, relative, is 4… | 3.468 | ratio | mean_rel_gap | test | eq | `[[art:9d73c7ff:metrics.test.sub.incentive_low.mean_rel_gap]]` | verified | 3.46792771 |
| 263 | outcomes | Mean predicted against observed on the slice, relative, is 4… | 2.934 | ratio | mean_rel_gap | out_of_time | eq | `[[art:d4df9d6d:metrics.out_of_time.sub.incentive_low.mean_rel_gap]]` | verified | 2.93363414 |
| 264 | outcomes | Mean predicted against observed on the slice, relative, is 4… | 2.769 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:47d4921d:metrics.vintage_holdout.sub.incentive_low.mean_rel_gap]]` | verified | 2.769192057 |
| 265 | outcomes | Mean predicted against observed on the slice, relative, is 4… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 266 | outcomes | AUC on this slice falls below the split's own by 0.01762 on… | 0.01762 | ratio | auc_gap | train | eq | `[[art:9e5dcedc:metrics.train.sub.loan_age_high.auc_gap]]` | verified | 0.01762194944 |
| 267 | outcomes | AUC on this slice falls below the split's own by 0.01762 on… | 0.02357 | ratio | auc_gap | test | eq | `[[art:64c4287f:metrics.test.sub.loan_age_high.auc_gap]]` | verified | 0.02356551854 |
| 268 | outcomes | AUC on this slice falls below the split's own by 0.01762 on… | 0.07087 | ratio | auc_gap | vintage_holdout | eq | `[[art:2366ea6e:metrics.vintage_holdout.sub.loan_age_high.auc_gap]]` | verified | 0.07087172881 |
| 269 | outcomes | AUC on this slice falls below the split's own by 0.01762 on… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 270 | outcomes | AUC on this slice falls below the split's own by 0.01762 on… | -0.0086 | ratio | auc_gap | out_of_time | eq | `[[art:ae068d6e:metrics.out_of_time.sub.loan_age_high.auc_gap]]` | verified | -0.008599976808 |
| 271 | outcomes | The slice holds 0.4977 of train, 0.4947 of test, 0.4961 of o… | 0.4977 | ratio | share | train | eq | `[[art:52284cdc:metrics.train.sub.loan_age_high.share]]` | verified | 0.4977369283 |
| 272 | outcomes | The slice holds 0.4977 of train, 0.4947 of test, 0.4961 of o… | 0.4947 | ratio | share | test | eq | `[[art:e21962d4:metrics.test.sub.loan_age_high.share]]` | verified | 0.4947341048 |
| 273 | outcomes | The slice holds 0.4977 of train, 0.4947 of test, 0.4961 of o… | 0.4961 | ratio | share | out_of_time | eq | `[[art:b35469b9:metrics.out_of_time.sub.loan_age_high.share]]` | verified | 0.4961246635 |
| 274 | outcomes | The slice holds 0.4977 of train, 0.4947 of test, 0.4961 of o… | 0.4993 | ratio | share | vintage_holdout | eq | `[[art:6faede5c:metrics.vintage_holdout.sub.loan_age_high.share]]` | verified | 0.4993007428 |
| 275 | outcomes | The slice holds 0.4977 of train, 0.4947 of test, 0.4961 of o… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 276 | outcomes | Mean predicted against observed on the slice, relative, is 3… | 3.559 | ratio | mean_rel_gap | train | eq | `[[art:6aa9321e:metrics.train.sub.loan_age_high.mean_rel_gap]]` | verified | 3.559478471 |
| 277 | outcomes | Mean predicted against observed on the slice, relative, is 3… | 3.419 | ratio | mean_rel_gap | test | eq | `[[art:20d6b512:metrics.test.sub.loan_age_high.mean_rel_gap]]` | verified | 3.418648724 |
| 278 | outcomes | Mean predicted against observed on the slice, relative, is 3… | 3.529 | ratio | mean_rel_gap | out_of_time | eq | `[[art:be1fdcf0:metrics.out_of_time.sub.loan_age_high.mean_rel_gap]]` | verified | 3.529171663 |
| 279 | outcomes | Mean predicted against observed on the slice, relative, is 3… | 3.477 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:4a861a82:metrics.vintage_holdout.sub.loan_age_high.mean_rel_gap]]` | verified | 3.477115735 |
| 280 | outcomes | Mean predicted against observed on the slice, relative, is 3… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 281 | outcomes | AUC on this slice falls below the split's own by 0.004516 on… | 0.004516 | ratio | auc_gap | train | eq | `[[art:c2656c63:metrics.train.sub.loan_age_low.auc_gap]]` | verified | 0.004516199291 |
| 282 | outcomes | AUC on this slice falls below the split's own by 0.004516 on… | 0.001757 | ratio | auc_gap | test | eq | `[[art:cf8d7d74:metrics.test.sub.loan_age_low.auc_gap]]` | verified | 0.001757044165 |
| 283 | outcomes | AUC on this slice falls below the split's own by 0.004516 on… | 0.0046 | ratio | auc_gap | out_of_time | eq | `[[art:cbec2b07:metrics.out_of_time.sub.loan_age_low.auc_gap]]` | verified | 0.004600392042 |
| 284 | outcomes | AUC on this slice falls below the split's own by 0.004516 on… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 285 | outcomes | AUC on this slice falls below the split's own by 0.004516 on… | -0.05963 | ratio | auc_gap | vintage_holdout | eq | `[[art:373b0b83:metrics.vintage_holdout.sub.loan_age_low.auc_gap]]` | verified | -0.05963134286 |
| 286 | outcomes | The slice holds 0.5023 of train, 0.5053 of test, 0.5039 of o… | 0.5023 | ratio | share | train | eq | `[[art:705485e1:metrics.train.sub.loan_age_low.share]]` | verified | 0.5022630717 |
| 287 | outcomes | The slice holds 0.5023 of train, 0.5053 of test, 0.5039 of o… | 0.5053 | ratio | share | test | eq | `[[art:733f3324:metrics.test.sub.loan_age_low.share]]` | verified | 0.5052658952 |
| 288 | outcomes | The slice holds 0.5023 of train, 0.5053 of test, 0.5039 of o… | 0.5039 | ratio | share | out_of_time | eq | `[[art:77397e73:metrics.out_of_time.sub.loan_age_low.share]]` | verified | 0.5038753365 |
| 289 | outcomes | The slice holds 0.5023 of train, 0.5053 of test, 0.5039 of o… | 0.5007 | ratio | share | vintage_holdout | eq | `[[art:8b31e269:metrics.vintage_holdout.sub.loan_age_low.share]]` | verified | 0.5006992572 |
| 290 | outcomes | The slice holds 0.5023 of train, 0.5053 of test, 0.5039 of o… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 291 | outcomes | Mean predicted against observed on the slice, relative, is 3… | 3.695 | ratio | mean_rel_gap | train | eq | `[[art:56cd77db:metrics.train.sub.loan_age_low.mean_rel_gap]]` | verified | 3.694907687 |
| 292 | outcomes | Mean predicted against observed on the slice, relative, is 3… | 4.39 | ratio | mean_rel_gap | test | eq | `[[art:06bb2e76:metrics.test.sub.loan_age_low.mean_rel_gap]]` | verified | 4.390246612 |
| 293 | outcomes | Mean predicted against observed on the slice, relative, is 3… | 3.055 | ratio | mean_rel_gap | out_of_time | eq | `[[art:db1b4d86:metrics.out_of_time.sub.loan_age_low.mean_rel_gap]]` | verified | 3.054918009 |
| 294 | outcomes | Mean predicted against observed on the slice, relative, is 3… | 5.232 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:0406dec3:metrics.vintage_holdout.sub.loan_age_low.mean_rel_gap]]` | verified | 5.23202682 |
| 295 | outcomes | Mean predicted against observed on the slice, relative, is 3… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 296 | sensitivity | The largest variance inflation factor among the retained fea… | 4.976 | ratio | vif |  | eq | `[[art:f9e0db60:vif.max]]` | verified | 4.975500767 |
| 297 | sensitivity | The largest variance inflation factor among the retained fea… | 4.976 | ratio | vif |  | eq | `[[art:37532fa8:vif.note_rate]]` | verified | 4.975500767 |
| 298 | sensitivity | The largest variance inflation factor among the retained fea… | 10 | ratio | vif |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 299 | sensitivity | The next-largest values, on burnout at 3.439 , loan age at 2… | 3.439 | ratio | vif |  | eq | `[[art:88879cb2:vif.burnout]]` | verified | 3.439328594 |
| 300 | sensitivity | The next-largest values, on burnout at 3.439 , loan age at 2… | 2.929 | ratio | vif |  | eq | `[[art:5573d536:vif.loan_age]]` | verified | 2.928871763 |
| 301 | sensitivity | The next-largest values, on burnout at 3.439 , loan age at 2… | 2.226 | ratio | vif |  | eq | `[[art:2da1b19c:vif.incentive]]` | verified | 2.22632259 |
| 302 | sensitivity | The next-largest values, on burnout at 3.439 , loan age at 2… | 1.713 | ratio | vif |  | eq | `[[art:a6c55fce:vif.sato]]` | verified | 1.71256814 |
| 303 | sensitivity | The next-largest values, on burnout at 3.439 , loan age at 2… | 1.018 | ratio | vif |  | eq | `[[art:a9cfa7eb:vif.season_cos]]` | verified | 1.017653349 |
| 304 | sensitivity | The next-largest values, on burnout at 3.439 , loan age at 2… | 1.004 | ratio | vif |  | eq | `[[art:669c5fcb:vif.season_sin]]` | verified | 1.004128844 |
| 305 | sensitivity | The next-largest values, on burnout at 3.439 , loan age at 2… | 1.008 | ratio | vif |  | eq | `[[art:f05d536a:vif.credit_score]]` | verified | 1.007978309 |
| 306 | sensitivity | The next-largest values, on burnout at 3.439 , loan age at 2… | 1.006 | ratio | vif |  | eq | `[[art:24f8e4d1:vif.orig_upb_log]]` | verified | 1.005846447 |
| 307 | sensitivity | The next-largest values, on burnout at 3.439 , loan age at 2… | 1.005 | ratio | vif |  | eq | `[[art:65b35f3b:vif.orig_ltv]]` | verified | 1.004506143 |
| 308 | sensitivity | Belsley's condition number of the column-standardised design… | 4.943 | ratio | condition_number |  | eq | `[[art:4f06a3c5:condition_number]]` | verified | 4.942565522 |
| 309 | sensitivity | Belsley's condition number of the column-standardised design… | 30 | ratio | condition_number |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 310 | sensitivity | The package screens each of the top-ranked features for a si… | 0.05 | ratio | sign_flip_coef |  | eq | `[[art:aca84377:threshold.R1.sign_flip_coef]]` | verified | 0.05 |
| 311 | sensitivity | The package screens each of the top-ranked features for a si… | 2 | ratio | sign_flip_z |  | eq | `[[art:2e4428c7:threshold.R1.sign_flip_z]]` | verified | 2 |
| 312 | sensitivity | The package screens each of the top-ranked features for a si… | 0.1 | ratio | auc_gap |  | eq | `[[art:b64213d7:threshold.R1.auc_gap]]` | verified | 0.1 |
| 313 | sensitivity | The sign-flip indicator comes back 0 for the note rate , 0 f… | 0 | ratio | sign_flip |  | eq | `[[art:e7ce4912:stability.note_rate.sign_flip]]` | verified | 0 |
| 314 | sensitivity | The sign-flip indicator comes back 0 for the note rate , 0 f… | 0 | ratio | sign_flip |  | eq | `[[art:0cc7a37d:stability.incentive.sign_flip]]` | verified | 0 |
| 315 | sensitivity | The sign-flip indicator comes back 0 for the note rate , 0 f… | 0 | ratio | sign_flip |  | eq | `[[art:6bc05e82:stability.burnout.sign_flip]]` | verified | 0 |
| 316 | sensitivity | The sign-flip indicator comes back 0 for the note rate , 0 f… | 0 | ratio | sign_flip |  | eq | `[[art:b7191217:stability.loan_age.sign_flip]]` | verified | 0 |
| 317 | sensitivity | The sign-flip indicator comes back 0 for the note rate , 0 f… | 0 | ratio | sign_flip |  | eq | `[[art:1f302ccd:stability.sato.sign_flip]]` | verified | 0 |
| 318 | sensitivity | The sign-flip indicator comes back 0 for the note rate , 0 f… | 0 | ratio | sign_flip |  | eq | `[[art:d956c276:stability.credit_score.sign_flip]]` | verified | 0 |
| 319 | sensitivity | The sign-flip indicator comes back 0 for the note rate , 0 f… | 0 | ratio | sign_flip |  | eq | `[[art:054d5fab:stability.orig_ltv.sign_flip]]` | verified | 0 |
| 320 | sensitivity | The sign-flip indicator comes back 0 for the note rate , 0 f… | 0 | ratio | sign_flip |  | eq | `[[art:fb1ae6c8:stability.orig_upb_log.sign_flip]]` | verified | 0 |
| 321 | sensitivity | The sign-flip indicator comes back 0 for the note rate , 0 f… | 0 | ratio | sign_flip |  | eq | `[[art:1850e2de:stability.season_cos.sign_flip]]` | verified | 0 |
| 322 | sensitivity | The regime-wise discrimination figures in the table above sh… | 0.1 | ratio | auc_gap |  | eq | `[[art:b64213d7:threshold.R1.auc_gap]]` | verified | 0.1 |
| 323 | sensitivity | At the downward extreme the value change is -1099000 , and a… | -1099000 | currency | value_change |  | eq | `[[art:ff90f8c1:scenario.value_change.-300]]` | verified | -1099446.442 |
| 324 | sensitivity | At the downward extreme the value change is -1099000 , and a… | 557600 | currency | value_change |  | eq | `[[art:0b43db3b:scenario.value_change.300]]` | verified | 557614.5638 |
| 325 | sensitivity | The change is monotone increasing in the shock across the wh… | -1099000 | currency | value_change |  | eq | `[[art:ff90f8c1:scenario.value_change.-300]]` | verified | -1099446.442 |
| 326 | sensitivity | The change is monotone increasing in the shock across the wh… | -927100 | currency | value_change |  | eq | `[[art:59e2f8a4:scenario.value_change.-200]]` | verified | -927073.1975 |
| 327 | sensitivity | The change is monotone increasing in the shock across the wh… | -517800 | currency | value_change |  | eq | `[[art:b3c09ea9:scenario.value_change.-100]]` | verified | -517824.9714 |
| 328 | sensitivity | The change is monotone increasing in the shock across the wh… | 0 | currency | value_change |  | eq | `[[art:1e1b0b88:scenario.value_change.0]]` | verified | 0 |
| 329 | sensitivity | The change is monotone increasing in the shock across the wh… | 352800 | currency | value_change |  | eq | `[[art:95da798d:scenario.value_change.100]]` | verified | 352845.0358 |
| 330 | sensitivity | The change is monotone increasing in the shock across the wh… | 505800 | currency | value_change |  | eq | `[[art:be13cc25:scenario.value_change.200]]` | verified | 505801.2473 |
| 331 | sensitivity | The change is monotone increasing in the shock across the wh… | 557600 | currency | value_change |  | eq | `[[art:0b43db3b:scenario.value_change.300]]` | verified | 557614.5638 |
| 332 | sensitivity | The convexity statistic, the sum of the changes at the two e… | -541800 | currency | convexity |  | eq | `[[art:42ad3e3e:scenario.convexity]]` | verified | -541831.8779 |
| 333 | findings | On train, mean predicted is 0.03925 against an observed rate… | 0.03925 | ratio | mean_predicted | train | eq | `[[art:68f41b88:metrics.train.mean_predicted]]` | verified | 0.03925176105 |
| 334 | findings | On train, mean predicted is 0.03925 against an observed rate… | 0.008525 | ratio | event_rate | train | eq | `[[art:b9ef3327:metrics.train.event_rate]]` | verified | 0.008524699414 |
| 335 | findings | On train, mean predicted is 0.03925 against an observed rate… | 3.604 | ratio | mean_rel_gap | train | eq | `[[art:324eb124:calibration.mean_rel_gap.train]]` | verified | 3.604474497 |
| 336 | findings | On train, mean predicted is 0.03925 against an observed rate… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 337 | findings | On test, mean predicted is 0.03802 against an observed rate… | 0.03802 | ratio | mean_predicted | test | eq | `[[art:122af437:metrics.test.mean_predicted]]` | verified | 0.038020619 |
| 338 | findings | On test, mean predicted is 0.03802 against an observed rate… | 0.008061 | ratio | event_rate | test | eq | `[[art:570cc08a:metrics.test.event_rate]]` | verified | 0.008061370433 |
| 339 | findings | On test, mean predicted is 0.03802 against an observed rate… | 3.716 | ratio | mean_rel_gap | test | eq | `[[art:15d5555b:calibration.mean_rel_gap.test]]` | verified | 3.716396464 |
| 340 | findings | On test, mean predicted is 0.03802 against an observed rate… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 341 | findings | On out_of_time, mean predicted is 0.07793 against an observe… | 0.07793 | ratio | mean_predicted | out_of_time | eq | `[[art:921d185b:metrics.out_of_time.mean_predicted]]` | verified | 0.07792752696 |
| 342 | findings | On out_of_time, mean predicted is 0.07793 against an observe… | 0.01795 | ratio | event_rate | out_of_time | eq | `[[art:83ccf5c0:metrics.out_of_time.event_rate]]` | verified | 0.01794892714 |
| 343 | findings | On out_of_time, mean predicted is 0.07793 against an observe… | 3.342 | ratio | mean_rel_gap | out_of_time | eq | `[[art:5b8375ec:calibration.mean_rel_gap.out_of_time]]` | verified | 3.3416259 |
| 344 | findings | On out_of_time, mean predicted is 0.07793 against an observe… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 345 | findings | On vintage_holdout, mean predicted is 0.02582 against an obs… | 0.02582 | ratio | mean_predicted | vintage_holdout | eq | `[[art:348107ae:metrics.vintage_holdout.mean_predicted]]` | verified | 0.02582080379 |
| 346 | findings | On vintage_holdout, mean predicted is 0.02582 against an obs… | 0.004817 | ratio | event_rate | vintage_holdout | eq | `[[art:e3590a16:metrics.vintage_holdout.event_rate]]` | verified | 0.004817105386 |
| 347 | findings | On vintage_holdout, mean predicted is 0.02582 against an obs… | 4.36 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:a691b5ed:calibration.mean_rel_gap.vintage_holdout]]` | verified | 4.360232281 |
| 348 | findings | On vintage_holdout, mean predicted is 0.02582 against an obs… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 349 | findings | The validator concludes that the model's output cannot be re… | 0.7758 | ratio | auc | test | eq | `[[art:2f4cab3e:metrics.test.auc]]` | verified | 0.7758373186 |
| 350 | findings | The model developer should identify the source of the level… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 351 | findings | - Model developer: on the test split, what is the model disc… | 0.6822 | ratio | auc | test | eq | `[[art:4ca370cf:metrics.test.sub.incentive_low.auc]]` | verified | 0.682197047 |
| 352 | findings | - Model developer: on the test split, what is the model disc… | 0.09364 | ratio | auc_gap | test | eq | `[[art:b062501e:metrics.test.sub.incentive_low.auc_gap]]` | verified | 0.09364027153 |
| 353 | findings | - Model developer: on the test split, what is the model disc… | 0.7758 | ratio | auc | test | eq | `[[art:2f4cab3e:metrics.test.auc]]` | verified | 0.7758373186 |
| 354 | findings | - Model developer: on the test split, what is the model disc… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 355 | findings | - Model developer: on the test split, what is the model disc… | 0.5 | ratio | share | test | eq | `[[art:1d5dd4c2:metrics.test.sub.incentive_low.share]]` | verified | 0.5 |
| 356 | findings | - Model developer: on the test split, what is the model disc… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 357 | findings | - Model developer: on the vintage_holdout split, what is the… | 0.6844 | ratio | auc | vintage_holdout | eq | `[[art:47e679fc:metrics.vintage_holdout.sub.incentive_low.auc]]` | verified | 0.6843546032 |
| 358 | findings | - Model developer: on the vintage_holdout split, what is the… | 0.08994 | ratio | auc_gap | vintage_holdout | eq | `[[art:40f8b479:metrics.vintage_holdout.sub.incentive_low.auc_gap]]` | verified | 0.08994391339 |
| 359 | findings | - Model developer: on the vintage_holdout split, what is the… | 0.7743 | ratio | auc | vintage_holdout | eq | `[[art:25db8aa3:metrics.vintage_holdout.auc]]` | verified | 0.7742985165 |
| 360 | findings | - Model developer: on the vintage_holdout split, what is the… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 361 | findings | - Model developer: on the vintage_holdout split, what is the… | 0.5 | ratio | share | vintage_holdout | eq | `[[art:d94e6531:metrics.vintage_holdout.sub.incentive_low.share]]` | verified | 0.500015539 |
| 362 | findings | - Model developer: on the vintage_holdout split, what is the… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 363 | findings | - Model developer: what behaviour is the fitted coefficient… | -1 | ratio | coef_sign |  | eq | `[[art:dcfb2de4:sign_check.burnout.coef_sign]]` | verified | -1 |
| 364 | findings | - Model developer: what behaviour is the fitted coefficient… | 1 | ratio | univariate_direction |  | eq | `[[art:bfc96bb2:sign_check.burnout.univariate_direction]]` | verified | 1 |
| 365 | findings | - Model developer: what behaviour is the fitted coefficient… | 0 | ratio | agrees |  | eq | `[[art:56826e40:sign_check.burnout.agrees]]` | verified | 0 |
| 366 | findings | - Model developer: what behaviour is the fitted coefficient… | -1 | ratio | coef_sign |  | eq | `[[art:aecf7ccb:sign_check.note_rate.coef_sign]]` | verified | -1 |
| 367 | findings | - Model developer: what behaviour is the fitted coefficient… | 1 | ratio | univariate_direction |  | eq | `[[art:61f6e1ac:sign_check.note_rate.univariate_direction]]` | verified | 1 |
| 368 | findings | - Model developer: what behaviour is the fitted coefficient… | 0 | ratio | agrees |  | eq | `[[art:a453463d:sign_check.note_rate.agrees]]` | verified | 0 |
| 369 | findings | - Model developer: what behaviour is the fitted coefficient… | -1 | ratio | coef_sign |  | eq | `[[art:265915cf:sign_check.sato.coef_sign]]` | verified | -1 |
| 370 | findings | - Model developer: what behaviour is the fitted coefficient… | 1 | ratio | univariate_direction |  | eq | `[[art:c08233a6:sign_check.sato.univariate_direction]]` | verified | 1 |
| 371 | findings | - Model developer: what behaviour is the fitted coefficient… | 0 | ratio | agrees |  | eq | `[[art:b3755963:sign_check.sato.agrees]]` | verified | 0 |
| 372 | monitoring | The calibration slope should be recomputed on each monthly p… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 373 | monitoring | The calibration slope should be recomputed on each monthly p… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 374 | monitoring | The validation reading of 0.9537 sits inside that declared b… | 0.9537 | ratio | calibration_slope | test | eq | `[[art:f8ef2beb:calibration_slope.test]]` | verified | 0.9536630305 |
| 375 | monitoring | Discrimination should be tracked as the AUC on each quarterl… | 0.65 | ratio | auc | test | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 376 | monitoring | Discrimination should be tracked as the AUC on each quarterl… | 0.7758 | ratio | auc | test | eq | `[[art:2f4cab3e:metrics.test.auc]]` | verified | 0.7758373186 |
| 377 | monitoring | Population stability should be recomputed monthly across the… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 378 | monitoring | The largest train-to-test reading in this validation was 0.0… | 0.06189 | ratio | psi |  | eq | `[[art:c2e8c8fd:psi.max]]` | verified | 0.06188985797 |
| 379 | monitoring | Drift here was measured as a single train-to-test comparison… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |

## Appendix B — Artifact index

The store holds 467 artifacts; the 279 this report cites or rests a finding on are indexed here.

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
| `calibration.mean_rel_gap.out_of_time` | `5b8375ec` | scalar | 3.3416259 | mean predicted against observed on out_of_time, relative |
| `calibration.mean_rel_gap.test` | `15d5555b` | scalar | 3.716396464 | mean predicted against observed on test, relative |
| `calibration.mean_rel_gap.train` | `324eb124` | scalar | 3.604474497 | mean predicted against observed on train, relative |
| `calibration.mean_rel_gap.vintage_holdout` | `a691b5ed` | scalar | 4.360232281 | mean predicted against observed on vintage_holdout, relative |
| `calibration.out_of_time` | `392a629c` | table | table, 10 rows | calibration by decile of predicted probability on out_of_time |
| `calibration.test` | `8417f6b7` | table | table, 10 rows | calibration by decile of predicted probability on test |
| `calibration.train` | `a8585045` | table | table, 10 rows | calibration by decile of predicted probability on train |
| `calibration.vintage_holdout` | `fd5aec5a` | table | table, 10 rows | calibration by decile of predicted probability on vintage_holdout |
| `calibration_intercept.out_of_time` | `db324216` | scalar | -1.496633503 | logistic regression of the outcome on logit(p) on out_of_time: the intercept |
| `calibration_intercept.test` | `257fb817` | scalar | -1.747805271 | logistic regression of the outcome on logit(p) on test: the intercept |
| `calibration_intercept.train` | `57309d7d` | scalar | -1.566304198 | logistic regression of the outcome on logit(p) on train: the intercept |
| `calibration_intercept.vintage_holdout` | `6f00dbc2` | scalar | -2.175702334 | logistic regression of the outcome on logit(p) on vintage_holdout: the intercept |
| `calibration_slope.out_of_time` | `ea7d5696` | scalar | 1.066358183 | logistic regression of the outcome on logit(p) on out_of_time: the slope |
| `calibration_slope.test` | `f8ef2beb` | scalar | 0.9536630305 | logistic regression of the outcome on logit(p) on test: the slope |
| `calibration_slope.train` | `ffabb935` | scalar | 1.014728573 | logistic regression of the outcome on logit(p) on train: the slope |
| `calibration_slope.vintage_holdout` | `010c0ec4` | scalar | 0.8561504457 | logistic regression of the outcome on logit(p) on vintage_holdout: the slope |
| `challenger.auc` | `705b66f0` | scalar | 0.7337079121 | the challenger's AUC on test |
| `challenger.brier` | `85a89ef9` | scalar | 0.008629514666 | the challenger's Brier score on test |
| `challenger.delta_auc` | `1e990f53` | scalar | -0.04212940647 | the challenger's AUC on test minus the champion's |
| `condition_number` | `4f06a3c5` | scalar | 4.942565522 | Belsley's condition number of the column-standardised design |
| `cpr.out_of_time.mae` | `8ac7bfbc` | scalar | 0.3179874584 | mean absolute difference between actual and predicted CPR on out_of_time |
| `cpr.test` | `ee6d2090` | table | table, 71 rows | actual against predicted CPR by period on test |
| `cpr.test.mae` | `b7587aed` | scalar | 0.222029929 | mean absolute difference between actual and predicted CPR on test |
| `cpr.train.mae` | `8d8e2c42` | scalar | 0.2239621374 | mean absolute difference between actual and predicted CPR on train |
| `cpr.vintage_holdout.mae` | `2d48e163` | scalar | 0.1720007526 | mean absolute difference between actual and predicted CPR on vintage_holdout |
| `csi.burnout` | `640f9435` | scalar | 0.0001325955583 | CSI of burnout: its contribution to the shift in the linear predictor |
| `csi.credit_score` | `6653968a` | scalar | 0.007706951731 | CSI of credit_score: its contribution to the shift in the linear predictor |
| `csi.incentive` | `3bfa986b` | scalar | 0.005685694124 | CSI of incentive: its contribution to the shift in the linear predictor |
| `csi.loan_age` | `df52c920` | scalar | 0 | CSI of loan_age: its contribution to the shift in the linear predictor |
| `csi.max` | `a8ca288d` | scalar | 0.03331391493 | the largest characteristic stability index |
| `csi.note_rate` | `e06d8658` | scalar | 0.01371659455 | CSI of note_rate: its contribution to the shift in the linear predictor |
| `csi.orig_ltv` | `7a941368` | scalar | 0.03331391493 | CSI of orig_ltv: its contribution to the shift in the linear predictor |
| `csi.orig_upb_log` | `bbbec9d2` | scalar | 0.002863276289 | CSI of orig_upb_log: its contribution to the shift in the linear predictor |
| `csi.sato` | `c9bad372` | scalar | 0.0009304918233 | CSI of sato: its contribution to the shift in the linear predictor |
| `csi.season_cos` | `78d740c8` | scalar | 0.0005033620785 | CSI of season_cos: its contribution to the shift in the linear predictor |
| `csi.season_sin` | `d16ad42f` | scalar | 6.939549558e-05 | CSI of season_sin: its contribution to the shift in the linear predictor |
| `deciles.out_of_time.top2_capture` | `95c24730` | scalar | 0.5909090909 | share of out_of_time events in the top two deciles |
| `deciles.test` | `9246d1cd` | table | table, 10 rows | decile separation on test; decile 1 holds the highest probabilities |
| `deciles.test.top2_capture` | `43c4adc5` | scalar | 0.5806451613 | share of test events in the top two deciles |
| `deciles.train.top2_capture` | `eb38637b` | scalar | 0.6058631922 | share of train events in the top two deciles |
| `deciles.vintage_holdout.top2_capture` | `4a376307` | scalar | 0.5935483871 | share of vintage_holdout events in the top two deciles |
| `leakage.duplicates.train` | `4474c227` | scalar | 0 | share of train rows whose feature values are not unique within train |
| `leakage.name_screen.n_matched` | `407e62be` | scalar | 0 | feature names matching the target-adjacent lexicon |
| `leakage.overlap` | `4c9fcd09` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.features` | `0fec8048` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.ids` | `63d37fc5` | scalar | 0 | share of test rows whose ['loan_id', 'period'] also identify a row of train |
| `leakage.target_corr.max_single_feature_auc` | `1fe630dd` | scalar | 0.7238936567 | the AUC of the strongest single feature |
| `leakage.timing.n_flagged` | `742bcd24` | scalar | 0 | features declared during_period or after_outcome |
| `metrics.out_of_time.auc` | `aa836722` | scalar | 0.7897867937 | auc on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.brier` | `a8a8d3a5` | scalar | 0.02402096444 | brier on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.event_rate` | `83ccf5c0` | scalar | 0.01794892714 | event_rate on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.gini` | `3dc07327` | scalar | 0.5795735875 | gini on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.ks` | `00bf02ed` | scalar | 0.43678733 | ks on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.logloss` | `5198f968` | scalar | 0.1173954835 | logloss on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.mean_predicted` | `921d185b` | scalar | 0.07792752696 | mean_predicted on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.n` | `7898809e` | scalar | 12257 | n on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.sub.incentive_high` | `80b7e1fa` | table | table, 10 rows | every metric on the incentive above_median slice of out_of_time |
| `metrics.out_of_time.sub.incentive_high.auc_gap` | `ba620fbd` | scalar | 0.03623305516 | how far AUC on the incentive above_median slice of out_of_time falls below AUC on all of out_of_time |
| `metrics.out_of_time.sub.incentive_high.mean_rel_gap` | `1db4a82a` | scalar | 3.452467592 | mean predicted against observed on the incentive above_median slice of out_of_time, relative |
| `metrics.out_of_time.sub.incentive_high.share` | `431d1ff2` | scalar | 0.499877621 | the share of out_of_time the incentive above_median slice holds |
| `metrics.out_of_time.sub.incentive_low` | `15c7b72a` | table | table, 10 rows | every metric on the incentive below_median slice of out_of_time |
| `metrics.out_of_time.sub.incentive_low.auc_gap` | `6bcab8af` | scalar | 0.01934527728 | how far AUC on the incentive below_median slice of out_of_time falls below AUC on all of out_of_time |
| `metrics.out_of_time.sub.incentive_low.mean_rel_gap` | `d4df9d6d` | scalar | 2.93363414 | mean predicted against observed on the incentive below_median slice of out_of_time, relative |
| `metrics.out_of_time.sub.incentive_low.share` | `c7aaafd2` | scalar | 0.500122379 | the share of out_of_time the incentive below_median slice holds |
| `metrics.out_of_time.sub.loan_age_high` | `1dc983d8` | table | table, 10 rows | every metric on the loan_age above_median slice of out_of_time |
| `metrics.out_of_time.sub.loan_age_high.auc_gap` | `ae068d6e` | scalar | -0.008599976808 | how far AUC on the loan_age above_median slice of out_of_time falls below AUC on all of out_of_time |
| `metrics.out_of_time.sub.loan_age_high.mean_rel_gap` | `be1fdcf0` | scalar | 3.529171663 | mean predicted against observed on the loan_age above_median slice of out_of_time, relative |
| `metrics.out_of_time.sub.loan_age_high.share` | `b35469b9` | scalar | 0.4961246635 | the share of out_of_time the loan_age above_median slice holds |
| `metrics.out_of_time.sub.loan_age_low` | `0997edbe` | table | table, 10 rows | every metric on the loan_age below_median slice of out_of_time |
| `metrics.out_of_time.sub.loan_age_low.auc_gap` | `cbec2b07` | scalar | 0.004600392042 | how far AUC on the loan_age below_median slice of out_of_time falls below AUC on all of out_of_time |
| `metrics.out_of_time.sub.loan_age_low.mean_rel_gap` | `db1b4d86` | scalar | 3.054918009 | mean predicted against observed on the loan_age below_median slice of out_of_time, relative |
| `metrics.out_of_time.sub.loan_age_low.share` | `77397e73` | scalar | 0.5038753365 | the share of out_of_time the loan_age below_median slice holds |
| `metrics.test.auc` | `2f4cab3e` | scalar | 0.7758373186 | auc on test, recomputed by quaestor |
| `metrics.test.brier` | `1e4aab51` | scalar | 0.009863834665 | brier on test, recomputed by quaestor |
| `metrics.test.event_rate` | `570cc08a` | scalar | 0.008061370433 | event_rate on test, recomputed by quaestor |
| `metrics.test.gini` | `8593585c` | scalar | 0.5516746371 | gini on test, recomputed by quaestor |
| `metrics.test.ks` | `554f1e19` | scalar | 0.4280398649 | ks on test, recomputed by quaestor |
| `metrics.test.logloss` | `b9424e16` | scalar | 0.06118235348 | logloss on test, recomputed by quaestor |
| `metrics.test.mean_predicted` | `122af437` | scalar | 0.038020619 | mean_predicted on test, recomputed by quaestor |
| `metrics.test.n` | `e55953e1` | scalar | 15382 | n on test, recomputed by quaestor |
| `metrics.test.sub.incentive_high` | `f51b482a` | table | table, 10 rows | every metric on the incentive above_median slice of test |
| `metrics.test.sub.incentive_high.auc_gap` | `d7fc769c` | scalar | 0.04774016101 | how far AUC on the incentive above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.incentive_high.mean_rel_gap` | `ddf406ce` | scalar | 3.772978457 | mean predicted against observed on the incentive above_median slice of test, relative |
| `metrics.test.sub.incentive_high.share` | `549aa934` | scalar | 0.5 | the share of test the incentive above_median slice holds |
| `metrics.test.sub.incentive_low` | `0e5269db` | table | table, 10 rows | every metric on the incentive below_median slice of test |
| `metrics.test.sub.incentive_low.auc` | `4ca370cf` | scalar | 0.682197047 | auc on the incentive below_median slice of test |
| `metrics.test.sub.incentive_low.auc_gap` | `b062501e` | scalar | 0.09364027153 | how far AUC on the incentive below_median slice of test falls below AUC on all of test |
| `metrics.test.sub.incentive_low.mean_rel_gap` | `9d73c7ff` | scalar | 3.46792771 | mean predicted against observed on the incentive below_median slice of test, relative |
| `metrics.test.sub.incentive_low.share` | `1d5dd4c2` | scalar | 0.5 | the share of test the incentive below_median slice holds |
| `metrics.test.sub.loan_age_high` | `204983c3` | table | table, 10 rows | every metric on the loan_age above_median slice of test |
| `metrics.test.sub.loan_age_high.auc_gap` | `64c4287f` | scalar | 0.02356551854 | how far AUC on the loan_age above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.loan_age_high.mean_rel_gap` | `20d6b512` | scalar | 3.418648724 | mean predicted against observed on the loan_age above_median slice of test, relative |
| `metrics.test.sub.loan_age_high.share` | `e21962d4` | scalar | 0.4947341048 | the share of test the loan_age above_median slice holds |
| `metrics.test.sub.loan_age_low` | `e9591084` | table | table, 10 rows | every metric on the loan_age below_median slice of test |
| `metrics.test.sub.loan_age_low.auc_gap` | `cf8d7d74` | scalar | 0.001757044165 | how far AUC on the loan_age below_median slice of test falls below AUC on all of test |
| `metrics.test.sub.loan_age_low.mean_rel_gap` | `06bb2e76` | scalar | 4.390246612 | mean predicted against observed on the loan_age below_median slice of test, relative |
| `metrics.test.sub.loan_age_low.share` | `733f3324` | scalar | 0.5052658952 | the share of test the loan_age below_median slice holds |
| `metrics.train.auc` | `39508266` | scalar | 0.7891607921 | auc on train, recomputed by quaestor |
| `metrics.train.brier` | `d56a10b2` | scalar | 0.01035868886 | brier on train, recomputed by quaestor |
| `metrics.train.event_rate` | `b9ef3327` | scalar | 0.008524699414 | event_rate on train, recomputed by quaestor |
| `metrics.train.gini` | `d618ff0f` | scalar | 0.5783215843 | gini on train, recomputed by quaestor |
| `metrics.train.ks` | `e8d4ae61` | scalar | 0.4541800929 | ks on train, recomputed by quaestor |
| `metrics.train.logloss` | `2bff29d3` | scalar | 0.06296558061 | logloss on train, recomputed by quaestor |
| `metrics.train.mean_predicted` | `68f41b88` | scalar | 0.03925176105 | mean_predicted on train, recomputed by quaestor |
| `metrics.train.n` | `6fdfeabb` | scalar | 36013 | n on train, recomputed by quaestor |
| `metrics.train.sub.incentive_high` | `cb04026c` | table | table, 10 rows | every metric on the incentive above_median slice of train |
| `metrics.train.sub.incentive_high.auc_gap` | `572da87a` | scalar | 0.06958915791 | how far AUC on the incentive above_median slice of train falls below AUC on all of train |
| `metrics.train.sub.incentive_high.mean_rel_gap` | `03dd3e85` | scalar | 3.51794689 | mean predicted against observed on the incentive above_median slice of train, relative |
| `metrics.train.sub.incentive_high.share` | `277218fb` | scalar | 0.4999861161 | the share of train the incentive above_median slice holds |
| `metrics.train.sub.incentive_low` | `4bd37172` | table | table, 10 rows | every metric on the incentive below_median slice of train |
| `metrics.train.sub.incentive_low.auc_gap` | `bdcd3ce1` | scalar | 0.06733139884 | how far AUC on the incentive below_median slice of train falls below AUC on all of train |
| `metrics.train.sub.incentive_low.mean_rel_gap` | `48122349` | scalar | 4.060068838 | mean predicted against observed on the incentive below_median slice of train, relative |
| `metrics.train.sub.incentive_low.share` | `d7af12f0` | scalar | 0.5000138839 | the share of train the incentive below_median slice holds |
| `metrics.train.sub.loan_age_high` | `3ca45feb` | table | table, 10 rows | every metric on the loan_age above_median slice of train |
| `metrics.train.sub.loan_age_high.auc_gap` | `9e5dcedc` | scalar | 0.01762194944 | how far AUC on the loan_age above_median slice of train falls below AUC on all of train |
| `metrics.train.sub.loan_age_high.mean_rel_gap` | `6aa9321e` | scalar | 3.559478471 | mean predicted against observed on the loan_age above_median slice of train, relative |
| `metrics.train.sub.loan_age_high.share` | `52284cdc` | scalar | 0.4977369283 | the share of train the loan_age above_median slice holds |
| `metrics.train.sub.loan_age_low` | `b32d5a06` | table | table, 10 rows | every metric on the loan_age below_median slice of train |
| `metrics.train.sub.loan_age_low.auc_gap` | `c2656c63` | scalar | 0.004516199291 | how far AUC on the loan_age below_median slice of train falls below AUC on all of train |
| `metrics.train.sub.loan_age_low.mean_rel_gap` | `56cd77db` | scalar | 3.694907687 | mean predicted against observed on the loan_age below_median slice of train, relative |
| `metrics.train.sub.loan_age_low.share` | `705485e1` | scalar | 0.5022630717 | the share of train the loan_age below_median slice holds |
| `metrics.vintage_holdout.auc` | `25db8aa3` | scalar | 0.7742985165 | auc on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.brier` | `55737812` | scalar | 0.006100676477 | brier on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.event_rate` | `e3590a16` | scalar | 0.004817105386 | event_rate on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.gini` | `eff9b345` | scalar | 0.5485970331 | gini on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.ks` | `a2ee5005` | scalar | 0.4530637203 | ks on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.logloss` | `9f19871a` | scalar | 0.04161346969 | logloss on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.mean_predicted` | `348107ae` | scalar | 0.02582080379 | mean_predicted on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.n` | `37a92951` | scalar | 32177 | n on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.sub.incentive_high` | `5d211b75` | table | table, 10 rows | every metric on the incentive above_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.incentive_high.auc_gap` | `6182ebaa` | scalar | 0.02106338819 | how far AUC on the incentive above_median slice of vintage_holdout falls below AUC on all of vintage_holdout |
| `metrics.vintage_holdout.sub.incentive_high.mean_rel_gap` | `1aef21da` | scalar | 4.841555374 | mean predicted against observed on the incentive above_median slice of vintage_holdout, relative |
| `metrics.vintage_holdout.sub.incentive_high.share` | `cb627056` | scalar | 0.499984461 | the share of vintage_holdout the incentive above_median slice holds |
| `metrics.vintage_holdout.sub.incentive_low` | `2fbef9c8` | table | table, 10 rows | every metric on the incentive below_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.incentive_low.auc` | `47e679fc` | scalar | 0.6843546032 | auc on the incentive below_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.incentive_low.auc_gap` | `40f8b479` | scalar | 0.08994391339 | how far AUC on the incentive below_median slice of vintage_holdout falls below AUC on all of vintage_holdout |
| `metrics.vintage_holdout.sub.incentive_low.mean_rel_gap` | `47d4921d` | scalar | 2.769192057 | mean predicted against observed on the incentive below_median slice of vintage_holdout, relative |
| `metrics.vintage_holdout.sub.incentive_low.share` | `d94e6531` | scalar | 0.500015539 | the share of vintage_holdout the incentive below_median slice holds |
| `metrics.vintage_holdout.sub.loan_age_high` | `6e61b330` | table | table, 10 rows | every metric on the loan_age above_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.loan_age_high.auc_gap` | `2366ea6e` | scalar | 0.07087172881 | how far AUC on the loan_age above_median slice of vintage_holdout falls below AUC on all of vintage_holdout |
| `metrics.vintage_holdout.sub.loan_age_high.mean_rel_gap` | `4a861a82` | scalar | 3.477115735 | mean predicted against observed on the loan_age above_median slice of vintage_holdout, relative |
| `metrics.vintage_holdout.sub.loan_age_high.share` | `6faede5c` | scalar | 0.4993007428 | the share of vintage_holdout the loan_age above_median slice holds |
| `metrics.vintage_holdout.sub.loan_age_low` | `69d53a03` | table | table, 10 rows | every metric on the loan_age below_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.loan_age_low.auc_gap` | `373b0b83` | scalar | -0.05963134286 | how far AUC on the loan_age below_median slice of vintage_holdout falls below AUC on all of vintage_holdout |
| `metrics.vintage_holdout.sub.loan_age_low.mean_rel_gap` | `0406dec3` | scalar | 5.23202682 | mean predicted against observed on the loan_age below_median slice of vintage_holdout, relative |
| `metrics.vintage_holdout.sub.loan_age_low.share` | `8b31e269` | scalar | 0.5006992572 | the share of vintage_holdout the loan_age below_median slice holds |
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
| `psi.out_of_time.y_score` | `6f080528` | scalar | 0.6984990823 | PSI of the score between train and out_of_time |
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
| `psi.vintage_holdout.y_score` | `c71062d6` | scalar | 0.1603916415 | PSI of the score between train and vintage_holdout |
| `psi.y_score` | `aa10164c` | scalar | 0.001868586849 | PSI of the score between train and test |
| `run.features` | `61276a96` | json | json | the subject's features.json |
| `run.model_summary` | `a65c5723` | json | json | the subject's model_summary.json |
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |
| `scenario.convexity` | `42ad3e3e` | scalar | -541831.8779 | the value change at -300 bp plus the change at 300 bp; negative when the fall outweighs the rise |
| `scenario.value_by_shock` | `89b33839` | table | table, 7 rows | servicing value, its change from the base case and first-year CPR, by shock |
| `scenario.value_change.-100` | `b3c09ea9` | scalar | -517824.9714 | change in servicing value at -100 bp |
| `scenario.value_change.-200` | `59e2f8a4` | scalar | -927073.1975 | change in servicing value at -200 bp |
| `scenario.value_change.-300` | `ff90f8c1` | scalar | -1099446.442 | change in servicing value at -300 bp |
| `scenario.value_change.0` | `1e1b0b88` | scalar | 0 | change in servicing value at 0 bp |
| `scenario.value_change.100` | `95da798d` | scalar | 352845.0358 | change in servicing value at 100 bp |
| `scenario.value_change.200` | `be13cc25` | scalar | 505801.2473 | change in servicing value at 200 bp |
| `scenario.value_change.300` | `0b43db3b` | scalar | 557614.5638 | change in servicing value at 300 bp |
| `sign_check.burnout.agrees` | `56826e40` | scalar | 0 | 1 when the fitted sign on burnout agrees with its univariate direction, 0 when it does not |
| `sign_check.burnout.coef_sign` | `dcfb2de4` | scalar | -1 | the sign of the fitted coefficient on burnout |
| `sign_check.burnout.univariate_direction` | `bfc96bb2` | scalar | 1 | the sign of burnout's own single-feature AUC on train minus 0.5 |
| `sign_check.credit_score.agrees` | `915bf8eb` | scalar | 1 | 1 when the fitted sign on credit_score agrees with its univariate direction, 0 when it does not |
| `sign_check.credit_score.coef_sign` | `1ec1078b` | scalar | 1 | the sign of the fitted coefficient on credit_score |
| `sign_check.credit_score.univariate_direction` | `42303896` | scalar | 1 | the sign of credit_score's own single-feature AUC on train minus 0.5 |
| `sign_check.incentive.agrees` | `f7b2338e` | scalar | 1 | 1 when the fitted sign on incentive agrees with its univariate direction, 0 when it does not |
| `sign_check.incentive.coef_sign` | `684cf11a` | scalar | 1 | the sign of the fitted coefficient on incentive |
| `sign_check.incentive.univariate_direction` | `8098d951` | scalar | 1 | the sign of incentive's own single-feature AUC on train minus 0.5 |
| `sign_check.n_disagreements` | `e223cd4a` | scalar | 3 | retained features whose fitted sign contradicts their univariate direction, of 9 checked |
| `sign_check.note_rate.agrees` | `a453463d` | scalar | 0 | 1 when the fitted sign on note_rate agrees with its univariate direction, 0 when it does not |
| `sign_check.note_rate.coef_sign` | `aecf7ccb` | scalar | -1 | the sign of the fitted coefficient on note_rate |
| `sign_check.note_rate.univariate_direction` | `61f6e1ac` | scalar | 1 | the sign of note_rate's own single-feature AUC on train minus 0.5 |
| `sign_check.orig_ltv.agrees` | `7021aeb0` | scalar | 1 | 1 when the fitted sign on orig_ltv agrees with its univariate direction, 0 when it does not |
| `sign_check.orig_ltv.coef_sign` | `7eec65ec` | scalar | -1 | the sign of the fitted coefficient on orig_ltv |
| `sign_check.orig_ltv.univariate_direction` | `76dbc708` | scalar | -1 | the sign of orig_ltv's own single-feature AUC on train minus 0.5 |
| `sign_check.orig_upb_log.agrees` | `07a9d3e6` | scalar | 1 | 1 when the fitted sign on orig_upb_log agrees with its univariate direction, 0 when it does not |
| `sign_check.orig_upb_log.coef_sign` | `5aa309fc` | scalar | 1 | the sign of the fitted coefficient on orig_upb_log |
| `sign_check.orig_upb_log.univariate_direction` | `b9743ecb` | scalar | 1 | the sign of orig_upb_log's own single-feature AUC on train minus 0.5 |
| `sign_check.sato.agrees` | `b3755963` | scalar | 0 | 1 when the fitted sign on sato agrees with its univariate direction, 0 when it does not |
| `sign_check.sato.coef_sign` | `265915cf` | scalar | -1 | the sign of the fitted coefficient on sato |
| `sign_check.sato.univariate_direction` | `c08233a6` | scalar | 1 | the sign of sato's own single-feature AUC on train minus 0.5 |
| `sign_check.season_cos.agrees` | `7f18ddf7` | scalar | 1 | 1 when the fitted sign on season_cos agrees with its univariate direction, 0 when it does not |
| `sign_check.season_sin.agrees` | `e110f357` | scalar | 1 | 1 when the fitted sign on season_sin agrees with its univariate direction, 0 when it does not |
| `stability.auc_by_regime` | `0b789c1f` | table | table, 2 rows | the champion's AUC within each rate_regime on train |
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
| `threshold.O1.slice_min_share` | `9a6f1a87` | scalar | 0.1 | the share of a split a sub-population must hold before it can raise an open item |
| `threshold.R1.auc_gap` | `b64213d7` | scalar | 0.1 | R1: the AUC difference across regimes |
| `threshold.R1.sign_flip_coef` | `aca84377` | scalar | 0.05 | R1: the coefficient a sign flip must exceed in both regimes |
| `threshold.R1.sign_flip_z` | `2e4428c7` | scalar | 2 | R1: the \|z\| a sign flip's coefficient must reach in both regimes |
| `threshold.S1.psi` | `278b9016` | scalar | 0.25 | S1: the population stability index, train against test |
| `threshold.package.auc.test.min` | `fececac1` | scalar | 0.65 | package.yaml declares auc min 0.65 |
| `threshold.package.calibration_slope.test.max` | `0adb7a89` | scalar | 1.2 | package.yaml declares calibration_slope max 1.2 |
| `threshold.package.calibration_slope.test.min` | `95fdb848` | scalar | 0.8 | package.yaml declares calibration_slope min 0.8 |
| `threshold.package.psi.max` | `fbb5a9d1` | scalar | 0.25 | package.yaml declares psi max 0.25 |
| `thresholds.evaluation` | `2fc2a920` | table | table, 4 rows | every threshold package.yaml declares, with its bound, the recomputed value and the outcome |
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
| tool calls | 19 (run_model 1, profile_data 1, compute_metrics 5, check_leakage 1, check_stability 1, check_collinearity 1, challenger_compare 1, run_scenarios 1, retrieve_guidance 7) |
| plan steps (bounded loop) | 4 |
| LLM calls | 20 (plan 4, draft 8, extract 8) |
| re-asks | 0 |
| repair rounds | 1 |
| tokens in / out | 309,362 / 136,321 |
| notional cost (USD) | 6.5976 |
| wall-clock (s) | 1430.22 |
| subject run (s) | 2.90 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | msr_prepayment-full_agent-20260920T173052Z-e61d346a |

## Appendix D — Not checked

| item | reason |
|---|---|
| developer claims (T1, claim channel) | The package declares 3 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
