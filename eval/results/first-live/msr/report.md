---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: msr_prepayment
version: "1.0"
model_type: discrete_time_hazard
configuration: full_agent
model: claude-opus-5[1m]
run_id: msr_prepayment-full_agent-20260917T044453Z-e98677a9
data_mode: real
grounding_precision_pre: 0.9966
grounding_precision_post: 1.0000
n_claims: 297
n_findings_by_severity: {high: 0, medium: 1, low: 0, info: 0}
generated: "2026-09-17T04:44:53Z"
illustrative: false
---

# Validation report — `msr_prepayment` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `msr_prepayment` v1.0 | `full_agent` | claude-opus-5[1m] | real, Freddie Mac Single-Family Loan-Level Dataset, sample files for origination years 2014, 2017 and 2019 (20,000 loans, seed 20260901, built by sample_freddie.py); FRED MORTGAGE30US (Freddie Mac PMMS, weekly, month-start value). Synthetic mode: synthetic.py. No loan-level rows are redistributed. | 0.9966 → 1.0000 | 0 / 1 / 0 / 0 |
<!-- quaestor:renderer:end -->

This report reviews the msr_prepayment model package, a loan-level model that estimates the probability that a mortgage prepays, and it follows the structure of the Federal Reserve's model risk management guidance on model validation and monitoring [[reg:SR26-2:V]].

The subject was re-executed from its package and its metrics recomputed independently, under the wall-clock cap of 300 seconds [[art:2ad8d1a5:runtime.max_seconds]] the package declares.
The recomputation covers four splits: a training sample of 313538 [[art:72c7a6d2:metrics.train.n]] rows, a test sample of 135060 [[art:629740ff:metrics.test.n]] rows, a vintage holdout of 221779 [[art:faabc78e:metrics.vintage_holdout.n]] rows, and an out-of-time sample of 283343 [[art:c164ae00:metrics.out_of_time.n]] rows.

The model passes each of the three developer-declared thresholds carried into this section.
Discrimination on the test split, at 0.6549 [[art:f3890b65:metrics.test.auc]], clears the declared floor of 0.65 [[art:fececac1:threshold.package.auc.test.min]].
The calibration slope on the test split, at 1.017 [[art:9b1edaa3:calibration_slope.test]], sits inside the declared band running from 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] to 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The largest train-to-test population stability index, at 0.005703 [[art:f632d5d4:psi.max]], stays far below the declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].

This validation published F-001, a C1 calibration finding at medium severity, which section 6 sets out in full.

## 2. Conceptual soundness

Validation of conceptual soundness here assesses the champion's design and construction, the quality and extent of the developmental evidence behind its variable selection, and the benchmarking evidence from an alternative specification [[reg:SR26-2:V.1.a]].

### Design and inputs

The champion is a single fitted probability equation for monthly prepayment: a linear index with an intercept of -4.79 [[art:29028ebe:run.model_summary#intercept]] and one coefficient per retained term, with loan age entered through a set of spline segments rather than as a single linear effect.
It was estimated on 313538 [[art:29028ebe:run.model_summary#n_train]] loan-month records drawn from 8596 [[art:29028ebe:run.model_summary#n_train_loans]] loans.
The feature inventory carries 12 [[art:0849f814:run.features#n]] features, of which 5 [[art:0849f814:run.features#at_origination]] are fixed at origination and 7 [[art:0849f814:run.features#before_period_start]] are observed before the start of the period whose outcome is being predicted.
No feature is dated during the performance period, at 0 [[art:0849f814:run.features#during_period]], and none is dated after the outcome, at 0 [[art:0849f814:run.features#after_outcome]].
On timing alone, then, every input is available at the moment the model is asked to produce a forecast, which is the condition a forward-looking prepayment model has to meet if it is to be usable in production.

The developer's own screen removed terms on a variance-inflation criterion with a cutoff of 10 [[art:29028ebe:run.model_summary#vif_threshold]].
Beginning-of-month balance in logs was dropped at 16.5 [[art:29028ebe:run.model_summary#removed.bom_balance_log.vif]], and the note rate was dropped at 18.07 [[art:29028ebe:run.model_summary#removed.note_rate.vif]].
Both removals are intelligible on subject-matter grounds rather than purely mechanical ones: current balance is very nearly a deterministic function of original balance and loan age, both of which are retained, and the note rate is the dominant component of both the refinance incentive and the spread at origination, so retaining it would have split one economic signal across several collinear carriers.
The screen therefore trades a small amount of redundant information for coefficients that can be read individually, which is the property the rest of this section relies on.

### Coefficient magnitudes and signs

The largest coefficients are the leading loan-age spline segment at 0.611 [[art:29028ebe:run.model_summary#coefficients.loan_age_spline_1.value]], the refinance incentive at 0.3952 [[art:29028ebe:run.model_summary#coefficients.incentive.value]], and log original balance at 0.286 [[art:29028ebe:run.model_summary#coefficients.orig_upb_log.value]].
The remaining loan-age segments run negative, at -0.04263 [[art:29028ebe:run.model_summary#coefficients.loan_age_spline_2.value]], -0.1501 [[art:29028ebe:run.model_summary#coefficients.loan_age_spline_3.value]] and -0.254 [[art:29028ebe:run.model_summary#coefficients.loan_age_spline_4.value]], so the fitted age profile rises steeply out of origination and then flattens and turns down, which is the seasoning ramp and post-peak decay that prepayment practitioners expect.
The positive incentive coefficient is the central economic prior of any refinance model, and the positive coefficient on log original balance matches the standard observation that larger balances make the fixed costs of refinancing easier to recover.
The coefficient on the twelve-month rate change is -0.06772 [[art:29028ebe:run.model_summary#coefficients.rate_change_12m.value]], so rising rates dampen prepayment, again as expected, and credit score enters positively at 0.02917 [[art:29028ebe:run.model_summary#coefficients.credit_score.value]], consistent with stronger borrowers being better able to qualify for a new loan.
The seasonal terms, at 0.01281 [[art:29028ebe:run.model_summary#coefficients.season_sin.value]] and -0.04626 [[art:29028ebe:run.model_summary#coefficients.season_cos.value]], carry a modest within-year cycle on which the subject matter supplies no strong directional prior beyond the expectation that one should exist.
Burnout enters positively at 0.0008253 [[art:29028ebe:run.model_summary#coefficients.burnout.value]], which runs against the usual expectation that a pool which has already had its chance to refinance prepays more slowly, though the magnitude is close enough to zero that the fitted equation is effectively indifferent to it.

### Sign agreement and the sensitivity of the model to each feature

Refitting the champion's functional form with one feature withheld at a time is the sensitivity evidence that lets each variable choice be assessed for its actual impact on model output rather than on its coefficient alone [[reg:SR11-7:V.1.a]].
Those refits are measured from a level of 0.6391 [[art:ed55c319:ablation.baseline_auc]] on test, which is the all-feature refit rather than the champion's own reported discrimination, so the deltas below are read against that level.
The model's discrimination rests mainly on log original balance, whose removal costs -0.0171 [[art:d9fda2c8:ablation.orig_upb_log.delta_auc]], and on the refinance incentive, whose removal costs -0.0161 [[art:b1880518:ablation.incentive.delta_auc]]; both of these carry coefficient signs that agree with their own univariate direction, at 1 [[art:07a9d3e6:sign_check.orig_upb_log.agrees]] and 1 [[art:f7b2338e:sign_check.incentive.agrees]] respectively.
Loan age contributes -0.004572 [[art:0b5dcaeb:ablation.loan_age.delta_auc]], and the remaining terms contribute little or nothing: credit score at -0.0002604 [[art:9963f841:ablation.credit_score.delta_auc]], the twelve-month rate change at -0.0003635 [[art:f472749f:ablation.rate_change_12m.delta_auc]], burnout at 0.0005739 [[art:499cf97d:ablation.burnout.delta_auc]] and the cosine seasonal term at 0.001845 [[art:0931b2a0:ablation.season_cos.delta_auc]], the last two being improvements when the feature is withheld.

Of the retained features whose fitted sign was compared with its own univariate direction on train, 3 [[art:e223cd4a:sign_check.n_disagreements]] disagree, and each is set out below with the refit delta that measures how much the disagreement matters.
Original LTV is fitted with a sign of -1 [[art:7eec65ec:sign_check.orig_ltv.coef_sign]] against a univariate direction of 1 [[art:85aabf06:sign_check.orig_ltv.univariate_direction]], and withholding it moves test discrimination by -0.002233 [[art:acb0dcd5:ablation.orig_ltv.delta_auc]].
The negative fitted sign is the one the subject matter expects, since a borrower with less equity has less capacity to refinance, so the disagreement is most naturally read as the conditioning on original balance and credit score absorbing the positive marginal association, and the modest refit delta means the model does lean on the feature to a small degree.
Spread at origination is fitted with a sign of -1 [[art:265915cf:sign_check.sato.coef_sign]] against a univariate direction of 1 [[art:c08233a6:sign_check.sato.univariate_direction]], and withholding it moves test discrimination by -0.003026 [[art:f406b192:ablation.sato.delta_auc]].
This is the largest of the three disagreements by refit delta, and it is also the one where the subject matter genuinely cuts both ways: a wider spread at origination leaves more room to refinance, but it also marks a borrower less likely to qualify, and the fitted equation has chosen the second reading while the raw association favours the first.
The sine seasonal term is fitted with a sign of 1 [[art:761188ce:sign_check.season_sin.coef_sign]] against a univariate direction of -1 [[art:b75f0b9c:sign_check.season_sin.univariate_direction]], and withholding it moves test discrimination by 0.000108 [[art:47876c72:ablation.season_sin.delta_auc]].
That delta is positive and very small, so the model is not relying on this term at all, and the flipped sign on it is a statement about a seasonal phase that carries almost no discrimination rather than about the economics of prepayment.
Taken together, the sign disagreements sit on features the model uses lightly, and none of them falls on either of the two terms that carry the bulk of its discrimination.

### Effective challenge

Benchmarking against an alternative specification is the practical form that critical analysis of the modelling approach takes for a model of this kind [[reg:SR26-2:V.1.a]].
The champion scores 0.6549 [[art:f3890b65:metrics.test.auc]] on test and the challenger scores 0.6653 [[art:6f811314:challenger.auc]], a lead of 0.01042 [[art:10b988e8:challenger.delta_auc]].
The threshold at which a challenger's discrimination advantage is treated as material is 0.03 [[art:e042774c:threshold.E1.delta_auc]], and the observed lead is well inside it.
On squared error the ordering reverses, with the champion at 0.009063 [[art:21d0b581:metrics.test.brier]] against the challenger at 0.009119 [[art:0e717888:challenger.brier]], so the challenger's small ranking advantage does not come with better calibrated probabilities.
The effective challenge therefore does not displace the champion: an alternative approach was fitted and scored, it separates the outcome slightly better, and the margin is too small under the agreed threshold to justify abandoning a specification whose coefficients can be read and defended term by term.

## 3. Data integrity and drift

Sound development practice includes a critical assessment of data quality, relevance, and inputs, and this section reviews the data behind the model package on those terms [[reg:SR26-2:IV.1]].

The run resolved the declared input files and verified each one against its recorded cryptographic digest before any split was read.

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

The training split holds 313538 [[art:6582e5dd:profile.train.n]] rows, the test split 135060 [[art:75b5b833:profile.test.n]] rows, the vintage holdout 221779 [[art:fcb7e414:profile.vintage_holdout.n]] rows, and the out-of-time split 283343 [[art:a0103a06:profile.out_of_time.n]] rows.

### Missingness

The largest missing fraction over any column is 0 [[art:050a3099:profile.train.missing.max]] in train, 0 [[art:f813848d:profile.test.missing.max]] in test, 0 [[art:329bb430:profile.vintage_holdout.missing.max]] in the vintage holdout, and 0 [[art:4dafce11:profile.out_of_time.missing.max]] out of time.
Because those four values agree exactly, the gap in missingness between any pair of splits is nil, and the bound of 0.1 [[art:9cce25ea:threshold.D1.missing_gap]] on that gap is nowhere approached.
No split is therefore carrying an imputation or a coverage difference that the others do not.

### Population and characteristic stability

The declared stability bound is 0.25 [[art:278b9016:threshold.S1.psi]], and the model package declares the same value, 0.25 [[art:fbb5a9d1:threshold.package.psi.max]], for the maximum population stability index.

Between train and test the population stability index is 0.001567 [[art:40a3f946:psi.burnout]] for burnout, 0.003718 [[art:8a078965:psi.credit_score]] for credit score, 0.0003749 [[art:61538982:psi.incentive]] for incentive, and 8.302e-05 [[art:f548214d:psi.loan_age]] for loan age.
It is 0.005703 [[art:6ea40553:psi.orig_ltv]] for original LTV, 0.002753 [[art:4af07770:psi.orig_upb_log]] for log original balance, 3.589e-05 [[art:23b9e924:psi.rate_change_12m]] for the twelve-month rate change, and 0.002192 [[art:e68bfd2e:psi.sato]] for SATO.
The two seasonal terms move least, at 3.184e-06 [[art:9db38513:psi.season_cos]] and 3.366e-06 [[art:ae17ebba:psi.season_sin]], and the score itself shifts by 0.0006641 [[art:6e6c94e1:psi.y_score]].
The largest train-to-test value, score included, is 0.005703 [[art:f632d5d4:psi.max]], well inside the declared bound of 0.25 [[art:278b9016:threshold.S1.psi]], so the test split is drawn from effectively the same population as the training split.

The picture changes when the training split is compared with the vintage holdout.
There the index is 0.5116 [[art:e3a3122f:psi.vintage_holdout.burnout]] for burnout, 1.298 [[art:86f7884e:psi.vintage_holdout.incentive]] for incentive, 0.8816 [[art:2575a328:psi.vintage_holdout.rate_change_12m]] for the twelve-month rate change, and 0.7656 [[art:ae7b9c29:psi.vintage_holdout.y_score]] for the score, each of which sits above the declared bound of 0.25 [[art:278b9016:threshold.S1.psi]].
The remaining features stay inside that bound: 0.007218 [[art:341abd78:psi.vintage_holdout.credit_score]] for credit score, 0.1507 [[art:2de85f94:psi.vintage_holdout.loan_age]] for loan age, 0.01065 [[art:a5066c0f:psi.vintage_holdout.orig_ltv]] for original LTV, 0.03076 [[art:bd074d53:psi.vintage_holdout.orig_upb_log]] for log original balance, 0.2002 [[art:b34d2ebe:psi.vintage_holdout.sato]] for SATO, 0.000942 [[art:67aee1b5:psi.vintage_holdout.season_cos]] and 0.003659 [[art:dad1e65c:psi.vintage_holdout.season_sin]] for the seasonal terms.

Against the out-of-time split the separation is wider still, with 3.086 [[art:5f3c6bba:psi.out_of_time.loan_age]] for loan age, 1.726 [[art:73dfd106:psi.out_of_time.incentive]] for incentive, 1.551 [[art:5316f456:psi.out_of_time.burnout]] for burnout, 0.8254 [[art:09e68722:psi.out_of_time.rate_change_12m]] for the twelve-month rate change, and 1.54 [[art:75370112:psi.out_of_time.y_score]] for the score, all above the declared bound of 0.25 [[art:278b9016:threshold.S1.psi]].
The other out-of-time comparisons remain small: 0.004578 [[art:5341c0a9:psi.out_of_time.credit_score]] for credit score, 0.01598 [[art:7f6fab7a:psi.out_of_time.orig_ltv]] for original LTV, 0.02136 [[art:abf1e02d:psi.out_of_time.orig_upb_log]] for log original balance, 0.01473 [[art:85a8a904:psi.out_of_time.sato]] for SATO, 0.00591 [[art:8ef132e3:psi.out_of_time.season_cos]] and 0.02419 [[art:7388771e:psi.out_of_time.season_sin]] for the seasonal terms.
The features that move are the rate-driven and seasoning terms rather than the static underwriting characteristics, which is the signature of a later rate environment and an older book rather than a change in how the data were assembled, and the score moves with them.
These two splits are by construction drawn from periods and vintages the training split does not cover, so the declared bound, which is stated for the train-against-test comparison, is being read here outside the comparison it was written for; the magnitudes are recorded so that any use of those splits is understood to be an extrapolation.

Characteristic stability, measured as each feature's contribution to the shift in the linear predictor, is 3.43e-06 [[art:e4d3e34a:csi.burnout]] for burnout, 1.97e-05 [[art:0a280759:csi.credit_score]] for credit score, 0.001102 [[art:020f5ce2:csi.incentive]] for incentive, and 0 [[art:df52c920:csi.loan_age]] for loan age.
It is 0.0005902 [[art:1c9006f3:csi.orig_ltv]] for original LTV, 0.006455 [[art:7561e8b0:csi.orig_upb_log]] for log original balance, 0.0002237 [[art:ffdb6fdd:csi.rate_change_12m]] for the twelve-month rate change, 0.001116 [[art:a54b158e:csi.sato]] for SATO, 6.191e-05 [[art:c70e3aa4:csi.season_cos]] and 2.108e-05 [[art:fb3bf812:csi.season_sin]] for the seasonal terms.
The largest such contribution is 0.006455 [[art:131d42db:csi.max]], far below the declared stability bound of 0.25 [[art:278b9016:threshold.S1.psi]], so no single characteristic is driving a material shift in the linear predictor.

### Leakage screens

The timing declarations were screened first, and the count of features declared as observed during the performance period or after the outcome is 0 [[art:742bcd24:leakage.timing.n_flagged]].
The strongest single feature reaches an AUC of 0.5995 [[art:9e2ffad1:leakage.target_corr.max_single_feature_auc]] on its own, against the bound of 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]] on what one feature may achieve alone, so no individual input behaves like a restatement of the target.

The contamination screen has two arms, each read against its own bound.
The identifier arm, the share of test rows whose loan and period keys also identify a training row, is 0 [[art:63d37fc5:leakage.overlap.ids]], against the declared overlap bound of 0.005 [[art:9f336eaf:threshold.L2.overlap]].
The feature-vector arm, the share of test rows whose feature values also appear in train, is 0 [[art:0fec8048:leakage.overlap.features]], read against the bound that arm actually applied, 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].
That effective bound is the larger of the declared 0.005 [[art:9f336eaf:threshold.L2.overlap]] and twice the share of training rows whose feature values are not unique within train, 0.0001531 [[art:ce57652e:leakage.duplicates.train]], because two distinct subjects writing the same discrete row is coincidence rather than contamination, and on these inputs the declared value is the larger of the two.
Since both arms report no overlap at all, the distinction between the declared and the effective bound does not change the reading here.

The name screen matched 0 [[art:407e62be:leakage.name_screen.n_matched]] feature names against the target-adjacent lexicon.
Taken together, the timing declarations, the single-feature strength screen, the two contamination arms, and the name screen give no indication that the test split shares rows or target information with the training split.

### Assessment

The data are complete across every split, the train-to-test comparison is stable in both population and characteristic terms, and the leakage screens are clear, which supports the use of the test split as an honest out-of-sample measurement.
The vintage holdout and the out-of-time split are materially different populations from the training data on the rate-driven and seasoning features, and the performance read from them should be interpreted as evidence about behavior outside the development environment rather than as a repeat of the in-sample result.

## 4. Outcomes analysis

Outcomes analysis compares model outputs to corresponding real-world outcomes to assess performance relative to the model's objectives and business use [[reg:SR26-2:V.1.b]].

This section reports calibration before discrimination.
The ordering follows from the declared use: package.yaml states that this model's output is consumed as a probability and not only as a ranking, so whether the predicted probabilities mean what they say is the leading question, whatever the level of the event rate.

### Calibration

The logistic recalibration slope is 0.9971 [[art:28331672:calibration_slope.train]] on train and 1.017 [[art:9b1edaa3:calibration_slope.test]] on test, both inside the developer's band of 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] to 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
On the forward splits the slope falls to 0.8502 [[art:80fe61d2:calibration_slope.vintage_holdout]] on the vintage holdout and 0.4321 [[art:d9f87bb2:calibration_slope.out_of_time]] out of time, the latter well below the lower bound of 0.8 [[art:749634ae:threshold.C1.calibration_slope.min]].
The corresponding intercepts are -0.016 [[art:be40e0a7:calibration_intercept.train]] on train, 0.02905 [[art:1a8280dd:calibration_intercept.test]] on test, 0.06119 [[art:0d75b532:calibration_intercept.vintage_holdout]] on the vintage holdout and -1.762 [[art:53a8d76b:calibration_intercept.out_of_time]] out of time.
A slope far below one together with a large negative intercept out of time says the probabilities are both too flat and too low there, not merely shifted.

Mean predicted probability is 0.009503 [[art:716b94b2:metrics.train.mean_predicted]] against an observed rate of 0.009476 [[art:8ecc2809:metrics.train.event_rate]] on train, a relative gap of 0.002897 [[art:332fc4d9:calibration.mean_rel_gap.train]].
On test it is 0.009606 [[art:24595a04:metrics.test.mean_predicted]] against 0.009174 [[art:78206f7c:metrics.test.event_rate]], a relative gap of 0.04709 [[art:a173f6c5:calibration.mean_rel_gap.test]].
Both sit inside the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
On the vintage holdout mean predicted is 0.009873 [[art:c12c52f7:metrics.vintage_holdout.mean_predicted]] against an observed rate of 0.01948 [[art:bab66615:metrics.vintage_holdout.event_rate]], a relative gap of 0.4932 [[art:92b5a8c4:calibration.mean_rel_gap.vintage_holdout]], which exceeds that tolerance.
Out of time mean predicted is 0.01005 [[art:fd777cc4:metrics.out_of_time.mean_predicted]] against an observed rate of 0.01868 [[art:cf3a82aa:metrics.out_of_time.event_rate]], a relative gap of 0.4618 [[art:9e4c8750:calibration.mean_rel_gap.out_of_time]], also outside that tolerance.
Both breaches are raised as C1 calibration findings.
The model predicts roughly half the events that occur on each forward split, so a user reading the output as a probability would understate prepayment on both.

The decile view of calibration on test is below.

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

The portfolio-level restatement points the same way: mean absolute error between actual and predicted CPR is 0.02202 [[art:3487a403:cpr.train.mae]] on train and 0.02642 [[art:939c5fb9:cpr.test.mae]] on test, rising to 0.0785 [[art:0cc82390:cpr.vintage_holdout.mae]] on the vintage holdout and 0.08656 [[art:a467ad41:cpr.out_of_time.mae]] out of time.

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

AUC is 0.6504 [[art:40964132:metrics.train.auc]] on train, 0.6549 [[art:f3890b65:metrics.test.auc]] on test, 0.7388 [[art:95f87cc7:metrics.vintage_holdout.auc]] on the vintage holdout and 0.6898 [[art:cb57fe9a:metrics.out_of_time.auc]] out of time.
Gini is 0.3007 [[art:da0e7063:metrics.train.gini]] on train, 0.3099 [[art:5710cba3:metrics.test.gini]] on test, 0.4776 [[art:75ad81b1:metrics.vintage_holdout.gini]] on the vintage holdout and 0.3796 [[art:6c5edac7:metrics.out_of_time.gini]] out of time.
KS is 0.2262 [[art:96e91aee:metrics.train.ks]] on train, 0.2375 [[art:c35222f3:metrics.test.ks]] on test, 0.411 [[art:699a7598:metrics.vintage_holdout.ks]] on the vintage holdout and 0.3021 [[art:c486329f:metrics.out_of_time.ks]] out of time.
Brier score is 0.009359 [[art:574cf8a4:metrics.train.brier]] on train, 0.009063 [[art:21d0b581:metrics.test.brier]] on test, 0.01898 [[art:6a660ed9:metrics.vintage_holdout.brier]] on the vintage holdout and 0.01824 [[art:4ddcaaea:metrics.out_of_time.brier]] out of time.
Log loss is 0.05226 [[art:716b9dc1:metrics.train.logloss]] on train, 0.05083 [[art:048e9ca7:metrics.test.logloss]] on test, 0.09345 [[art:630a591b:metrics.vintage_holdout.logloss]] on the vintage holdout and 0.09576 [[art:8d53f72c:metrics.out_of_time.logloss]] out of time.
The share of events captured in the top two deciles is 0.38 [[art:b2f9e5d8:deciles.train.top2_capture]] on train, 0.3769 [[art:1d4dff05:deciles.test.top2_capture]] on test, 0.5116 [[art:3cd3b5a3:deciles.vintage_holdout.top2_capture]] on the vintage holdout and 0.4313 [[art:58f451c3:deciles.out_of_time.top2_capture]] out of time.
Row counts behind these figures are 313538 [[art:72c7a6d2:metrics.train.n]] on train, 135060 [[art:629740ff:metrics.test.n]] on test, 221779 [[art:faabc78e:metrics.vintage_holdout.n]] on the vintage holdout and 283343 [[art:c164ae00:metrics.out_of_time.n]] out of time.

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

The train-to-test AUC movement is from 0.6504 [[art:40964132:metrics.train.auc]] to 0.6549 [[art:f3890b65:metrics.test.auc]], comfortably inside the declared gap allowance of 0.08 [[art:630f28f4:threshold.O1.auc_gap]], and test AUC is slightly above train rather than below it, so there is no evidence of overfitting between those two splits.
Discrimination therefore holds up where calibration does not: the ordering of loans by predicted prepayment risk survives the move to the forward splits, while the level of the probabilities does not.

### Declared thresholds

<!-- quaestor:renderer:begin table thresholds.evaluation -->
Every threshold package.yaml declares, with its bound, the recomputed value and the outcome [[art:920227a3:thresholds.evaluation]]:

| metric | split | bound | value | result |
|---|---|---|---|---|
| auc | test | minimum 0.65 | 0.6549 | pass |
| calibration_slope | test | minimum 0.8 | 1.017 | pass |
| calibration_slope | test | maximum 1.2 | 1.017 | pass |
| psi |  | maximum 0.25 | 0.005703 | pass |
<!-- quaestor:renderer:end -->

The table sets each bound package.yaml declares against the value recomputed here and records the outcome for each.
It is the authoritative statement of which declared bounds this run met and which it did not.

### Follow-up analyses

The planning loop ran four sub-population analyses on the two forward splits, partitioning each by refinancing incentive and by loan age, to ask whether the under-prediction on those splits is a uniform level shift or concentrated in one half of the book.

**`incentive > median(incentive)`** — this slice was requested to test whether the roughly half-sized under-prediction out of time and on the vintage holdout is concentrated in the in-the-money half, which would distinguish a flat level shift from a failure of the refinancing-incentive response.

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

Out of time the slice's AUC of 0.6046 [[art:a1a6fd72:metrics.out_of_time.sub.incentive_high.auc]] falls 0.08523 [[art:e7b201c8:metrics.out_of_time.sub.incentive_high.auc_gap]] below the split's own, above the slice gap bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]], on 0.5 [[art:4787f68a:metrics.out_of_time.sub.incentive_high.share]] of the split, well clear of the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] a slice must hold and below the ceiling of 0.95 [[art:a928a05c:threshold.O1.slice_max_share]].
On the vintage holdout the slice's AUC of 0.6654 [[art:1d13a424:metrics.vintage_holdout.sub.incentive_high.auc]] falls 0.07345 [[art:dfc93d01:metrics.vintage_holdout.sub.incentive_high.auc_gap]] below the split's own, inside that same bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]], on 0.4991 [[art:6ee6cf53:metrics.vintage_holdout.sub.incentive_high.share]] of the split.
Mean predicted here is 0.0188 [[art:b7288bbc:metrics.out_of_time.sub.incentive_high.mean_predicted]] against an observed rate of 0.02949 [[art:f62f5a9c:metrics.out_of_time.sub.incentive_high.event_rate]] out of time and 0.01662 [[art:1f806ffc:metrics.vintage_holdout.sub.incentive_high.mean_predicted]] against 0.03165 [[art:7a446230:metrics.vintage_holdout.sub.incentive_high.event_rate]] on the vintage holdout, so in the in-the-money half the probabilities are too low in level, and on the out-of-time split their ordering weakens as well.

**`incentive <= median(incentive)`** — the complement was requested so that the two halves together show whether the under-prediction is a uniform level shift or concentrated in the in-the-money half.

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

Out of time the slice's AUC of 0.5198 [[art:5f017449:metrics.out_of_time.sub.incentive_low.auc]] falls 0.17 [[art:379c90f9:metrics.out_of_time.sub.incentive_low.auc_gap]] below the split's own, well above the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]], on 0.5 [[art:cc116fda:metrics.out_of_time.sub.incentive_low.share]] of the split against a floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].
On the vintage holdout the slice's AUC of 0.5956 [[art:e5b67962:metrics.vintage_holdout.sub.incentive_low.auc]] falls 0.1432 [[art:2b9eda62:metrics.vintage_holdout.sub.incentive_low.auc_gap]] below the split's own, also above that bound, on 0.5009 [[art:4e4aac59:metrics.vintage_holdout.sub.incentive_low.share]] of the split.
Mean predicted is 0.001307 [[art:e77d973c:metrics.out_of_time.sub.incentive_low.mean_predicted]] against an observed rate of 0.00787 [[art:b87e9246:metrics.out_of_time.sub.incentive_low.event_rate]] out of time and 0.003153 [[art:037a5534:metrics.vintage_holdout.sub.incentive_low.mean_predicted]] against 0.007346 [[art:8cd3a201:metrics.vintage_holdout.sub.incentive_low.event_rate]] on the vintage holdout, so in the out-of-the-money half both the level of the probabilities and their ordering are weak, the ordering barely better than chance out of time.
Taken with the in-the-money half, the under-prediction appears on both sides of the incentive median rather than in one of them alone, so it is not confined to the refinancing-incentive response.

**`loan_age > median(loan_age)`** — this slice was requested to test whether the forward-split under-prediction is concentrated in seasoned loans, which would point to a seasoning or hazard-shape defect rather than a flat level shift.

<!-- quaestor:renderer:begin table metrics.out_of_time.sub.loan_age_high -->
Every metric on the loan_age above_median slice of out_of_time [[art:fb175459:metrics.out_of_time.sub.loan_age_high]]:

| metric | value |
|---|---|
| n | 141030 |
| event_rate | 0.01229 |
| auc | 0.6568 |
| gini | 0.3135 |
| ks | 0.3082 |
| brier | 0.01215 |
| logloss | 0.07547 |
| mean_predicted | 0.003214 |
| share | 0.4977 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.vintage_holdout.sub.loan_age_high -->
Every metric on the loan_age above_median slice of vintage_holdout [[art:501301d6:metrics.vintage_holdout.sub.loan_age_high]]:

| metric | value |
|---|---|
| n | 110335 |
| event_rate | 0.01157 |
| auc | 0.7102 |
| gini | 0.4204 |
| ks | 0.3737 |
| brier | 0.01134 |
| logloss | 0.06242 |
| mean_predicted | 0.005655 |
| share | 0.4975 |
<!-- quaestor:renderer:end -->

Out of time the slice's AUC of 0.6568 [[art:f9940557:metrics.out_of_time.sub.loan_age_high.auc]] falls 0.03303 [[art:3375bb4a:metrics.out_of_time.sub.loan_age_high.auc_gap]] below the split's own, inside the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]], on 0.4977 [[art:2ea8628a:metrics.out_of_time.sub.loan_age_high.share]] of the split against a floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].
On the vintage holdout the slice's AUC of 0.7102 [[art:c882f305:metrics.vintage_holdout.sub.loan_age_high.auc]] falls 0.02861 [[art:9ed9d4d1:metrics.vintage_holdout.sub.loan_age_high.auc_gap]] below the split's own, also inside that bound, on 0.4975 [[art:dbe22405:metrics.vintage_holdout.sub.loan_age_high.share]] of the split.
Mean predicted is 0.003214 [[art:432adcfd:metrics.out_of_time.sub.loan_age_high.mean_predicted]] against an observed rate of 0.01229 [[art:90f73f7e:metrics.out_of_time.sub.loan_age_high.event_rate]] out of time and 0.005655 [[art:037855d3:metrics.vintage_holdout.sub.loan_age_high.mean_predicted]] against 0.01157 [[art:31f03683:metrics.vintage_holdout.sub.loan_age_high.event_rate]] on the vintage holdout, so for seasoned loans the weakness is in the level of the probabilities and not in their ordering, which holds within the slice bound on both splits.

**`loan_age <= median(loan_age)`** — the complementary half was requested to complete the loan-age partition and show whether the under-prediction is concentrated in seasoned loans or spread uniformly.

<!-- quaestor:renderer:begin table metrics.out_of_time.sub.loan_age_low -->
Every metric on the loan_age below_median slice of out_of_time [[art:5ab8bfd3:metrics.out_of_time.sub.loan_age_low]]:

| metric | value |
|---|---|
| n | 142313 |
| event_rate | 0.02502 |
| auc | 0.6665 |
| gini | 0.333 |
| ks | 0.2483 |
| brier | 0.02427 |
| logloss | 0.1159 |
| mean_predicted | 0.01683 |
| share | 0.5023 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.vintage_holdout.sub.loan_age_low -->
Every metric on the loan_age below_median slice of vintage_holdout [[art:a4b42f76:metrics.vintage_holdout.sub.loan_age_low]]:

| metric | value |
|---|---|
| n | 111444 |
| event_rate | 0.02731 |
| auc | 0.7112 |
| gini | 0.4223 |
| ks | 0.3376 |
| brier | 0.02653 |
| logloss | 0.1242 |
| mean_predicted | 0.01405 |
| share | 0.5025 |
<!-- quaestor:renderer:end -->

Out of time the slice's AUC of 0.6665 [[art:b30b38e0:metrics.out_of_time.sub.loan_age_low.auc]] falls 0.02328 [[art:3b05548e:metrics.out_of_time.sub.loan_age_low.auc_gap]] below the split's own, inside the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]], on 0.5023 [[art:50f06738:metrics.out_of_time.sub.loan_age_low.share]] of the split against a floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].
On the vintage holdout the slice's AUC of 0.7112 [[art:9e59bba3:metrics.vintage_holdout.sub.loan_age_low.auc]] falls 0.02765 [[art:69340c92:metrics.vintage_holdout.sub.loan_age_low.auc_gap]] below the split's own, also inside that bound, on 0.5025 [[art:38c62cb8:metrics.vintage_holdout.sub.loan_age_low.share]] of the split.
Mean predicted is 0.01683 [[art:e2794584:metrics.out_of_time.sub.loan_age_low.mean_predicted]] against an observed rate of 0.02502 [[art:f5c47c9d:metrics.out_of_time.sub.loan_age_low.event_rate]] out of time and 0.01405 [[art:4e34fc22:metrics.vintage_holdout.sub.loan_age_low.mean_predicted]] against 0.02731 [[art:1b4716c7:metrics.vintage_holdout.sub.loan_age_low.event_rate]] on the vintage holdout, so newer loans show the same shortfall in level with ordering intact, and across the loan-age partition the defect reads as a level shift rather than a seasoning-shape failure.

## 5. Sensitivity and scenario analysis

Sensitivity and scenario work is reported here as part of the critical analysis of developmental evidence that validating conceptual soundness calls for, covering key modeling choices and the assumptions behind them [[reg:SR26-2:V.1.a]].
The checks follow the long-standing expectation that sensitivity analysis and stress testing be run over a wide range of inputs, including extreme values, to establish the boundaries of model performance and to identify conditions under which a model may become unstable [[reg:SR11-7:V.1.a]].

### 5.1 Multicollinearity among the retained features

Collinearity among the retained features is mild on the training sample.
The largest variance inflation factor across the retained features is 4.629 [[art:82a187c7:vif.max]], well inside the review threshold of 10 [[art:aeb4f33c:threshold.M1.vif]].
That maximum belongs to the refinance incentive term at 4.629 [[art:0c33ec65:vif.incentive]], followed by burnout at 3.749 [[art:f9a490a7:vif.burnout]], the spread at origination at 3.015 [[art:42163c15:vif.sato]], loan age at 2.69 [[art:12ee5768:vif.loan_age]] and the twelve-month rate change at 2.205 [[art:7f4d0c73:vif.rate_change_12m]].
The remaining retained features sit close to unity, with original loan-to-value at 1.107 [[art:a998810f:vif.orig_ltv]], the sine seasonal term at 1.025 [[art:6afd05c9:vif.season_sin]], credit score at 1.023 [[art:373087f2:vif.credit_score]], the log original balance at 1.061 [[art:0dde7942:vif.orig_upb_log]] and the cosine seasonal term at 1.006 [[art:2950847c:vif.season_cos]].
Belsley's condition number of the column-standardised design is 4.565 [[art:87b61976:condition_number]] against a threshold of 30 [[art:7e52fd7a:threshold.M1.condition_number]], so the design is well conditioned and the coefficient estimates are not resting on near-dependence among the columns.
The incentive and burnout terms are the most entangled pair of drivers, which is expected in a prepayment specification, and their inflation factors remain far enough below the threshold that the individual coefficients can be read on their own terms.

### 5.2 Stability across the declared rate regimes

The development data carry a rate-regime label, so discrimination and coefficient signs were examined within each declared regime rather than only in the pooled sample.

<!-- quaestor:renderer:begin table stability.auc_by_regime -->
The champion's AUC within each rate_regime on train [[art:f293ebc6:stability.auc_by_regime]]:

| regime | n | event_rate | auc |
|---|---|---|---|
| falling | 162717 | 0.01121 | 0.6575 |
| rising | 150821 | 0.007605 | 0.6144 |
<!-- quaestor:renderer:end -->

The tolerance against which the across-regime difference in discrimination is read is 0.1 [[art:b64213d7:threshold.R1.auc_gap]].
No feature among the top ten changes sign across regimes under the test that requires a coefficient above 0.05 [[art:aca84377:threshold.R1.sign_flip_coef]] and a |z| of at least 2 [[art:2e4428c7:threshold.R1.sign_flip_z]] in both regimes.
The flip indicator stands at 0 [[art:0cc7a37d:stability.incentive.sign_flip]] for the refinance incentive, 0 [[art:6bc05e82:stability.burnout.sign_flip]] for burnout, 0 [[art:1f302ccd:stability.sato.sign_flip]] for the spread at origination, 0 [[art:b7191217:stability.loan_age.sign_flip]] for loan age, 0 [[art:465700ff:stability.rate_change_12m.sign_flip]] for the twelve-month rate change, 0 [[art:d956c276:stability.credit_score.sign_flip]] for credit score, 0 [[art:054d5fab:stability.orig_ltv.sign_flip]] for original loan-to-value, 0 [[art:fb1ae6c8:stability.orig_upb_log.sign_flip]] for the log original balance, 0 [[art:1850e2de:stability.season_cos.sign_flip]] for the cosine seasonal term and 0 [[art:6ba36a3b:stability.season_sin.sign_flip]] for the sine seasonal term.
The economic direction of the hazard's drivers therefore holds in each declared regime, and the regime-level discrimination reported in the table above is the evidence on which the stability of ranking across regimes rests.

### 5.3 Rate-shock scenarios

The subject is a prepayment hazard model feeding a servicing valuation, so the parallel rate-shock grid applies and its results are reported below.

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

At the downward extreme the change in servicing value is -1078000 [[art:9bab8e73:scenario.value_change.-300]], and at the upward extreme it is 167100 [[art:d7f60dfe:scenario.value_change.300]].
Across the grid the value change rises without reversal as the shock moves from the deepest rally to the largest sell-off, so the response curve is monotone increasing in the shock.
The convexity measure, which sums the change at the downward extreme and the change at the upward extreme, is -910600 [[art:67b742b1:scenario.convexity]], so the loss in the rally substantially outweighs the gain in the sell-off.
That negative sign agrees with the negatively convex response the package declares for servicing value under parallel rate shocks, and its magnitude shows the asymmetry is pronounced rather than marginal.
The practical consequence is that the model's valuation risk is concentrated on the downward side of the grid, where the prepayment hazard is most heavily exercised and where the reliability of the fitted incentive and burnout response matters most.
Users should read the downward shocks as the region in which the model is stressed hardest, and treat the upward shocks as the better-behaved half of the range.

### 5.4 Applicability

All three of the checks this section is asked to report — multicollinearity among the retained features, stability across the declared regimes, and the rate-shock scenarios — apply to a hazard model of this kind and are reported above from computed values, so none of them is described here as inapplicable to this model type.
The items Appendix D records as outside the scope of this validation are not represented anywhere in this section as though they had been run.

## 6. Findings and recommendations

Findings below are ordered by severity and each carries the recomputed quantities that raised it together with the threshold it was measured against, so that the limitations identified are traceable to evidence and to the judgment about whether corrective action is warranted [[reg:SR26-2:V]].

### F-001 · C1 calibration · severity **medium**

**The model under-predicts prepayment on both out-of-sample splits by roughly half and its scores are too compressed to track the outcome, so the calibration check fails.**

The calibration slope on the out-of-time split is 0.4321 [[art:d9f87bb2:calibration_slope.out_of_time]], well below the lower edge of the accepted band at 0.8 [[art:749634ae:threshold.C1.calibration_slope.min]].

On the out-of-time split the mean predicted probability is 0.01005 [[art:fd777cc4:metrics.out_of_time.mean_predicted]] against an observed event rate of 0.01868 [[art:cf3a82aa:metrics.out_of_time.event_rate]], a relative shortfall of 0.4618 [[art:9e4c8750:calibration.mean_rel_gap.out_of_time]] against a tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].

On the vintage holdout the mean predicted probability is 0.009873 [[art:c12c52f7:metrics.vintage_holdout.mean_predicted]] against an observed event rate of 0.01948 [[art:bab66615:metrics.vintage_holdout.event_rate]], a relative shortfall of 0.4932 [[art:92b5a8c4:calibration.mean_rel_gap.vintage_holdout]] against the same tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].

The validator concludes that the level error is not an artefact of one split but persists across both out-of-sample periods at a similar magnitude, and that the shallow slope means the shortfall is not a constant offset but widens as predicted risk rises, so predicted prepayment speeds understate realised speeds most where the model scores highest.

The model developer should recalibrate the predicted level against the out-of-sample periods, re-estimate the response so that the slope returns inside the accepted band rather than applying a flat scaling factor that would leave the compression in place, and re-present both the level and slope diagnostics on each split before the output is used for valuation.

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1, S1), `compute_metrics` (T1, O1), `check_leakage` (L1, L2), `check_stability` (R1), `check_collinearity` (M1), `challenger_compare` (E1), `run_scenarios` (X1).

### Open items

On the out-of-time split the segment `incentive > median(incentive)` has an AUC of 0.6046 [[art:a1a6fd72:metrics.out_of_time.sub.incentive_high.auc]], which is 0.08523 [[art:e7b201c8:metrics.out_of_time.sub.incentive_high.auc_gap]] below the split's own headline AUC and so past the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] on a segment holding 0.5 [[art:4787f68a:metrics.out_of_time.sub.incentive_high.share]] of the split, and because conditioning on refinancing incentive also narrows everything correlated with it the model developer is asked what the model is expected to discriminate on among borrowers who are already in the money, not to treat the segment as defective.

In the complementary segment `incentive <= median(incentive)` the AUC is 0.5198 [[art:5f017449:metrics.out_of_time.sub.incentive_low.auc]] on the out-of-time split, 0.17 [[art:379c90f9:metrics.out_of_time.sub.incentive_low.auc_gap]] below that split's headline AUC, and 0.5956 [[art:e5b67962:metrics.vintage_holdout.sub.incentive_low.auc]] on the vintage holdout, 0.1432 [[art:2b9eda62:metrics.vintage_holdout.sub.incentive_low.auc_gap]] below its headline AUC, both measured against the same bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] on segments holding 0.5 [[art:cc116fda:metrics.out_of_time.sub.incentive_low.share]] and 0.5009 [[art:4e4aac59:metrics.vintage_holdout.sub.incentive_low.share]] of their splits, and the model developer is asked what ranks a borrower inside a segment of near-constant out-of-the-money incentive, where turnover and other non-rate drivers rather than the rate response would have to carry the discrimination.

## 7. Ongoing monitoring recommendations

Ongoing monitoring evaluates the extent to which a model performs as expected given potential changes in products, exposures, activities, clients, data relevance, or market conditions, and a model that no longer performs as expected may warrant overlays, adjustment, or redevelopment [[reg:SR26-2:V.2]].

### Quantities to track and the bounds to track them against

Monitoring should reuse the thresholds this validation checked against rather than introduce new ones, so that a production breach and a validation breach mean the same thing.

- Calibration slope of the outcome on the logit of the predicted probability, recomputed on each seasoned production vintage and read against the declared band of 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] to 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]]; this validation recomputed a slope of 1.017 [[art:9b1edaa3:calibration_slope.test]] on the held-out sample, which sits near the centre of that band and gives monitoring a clear reference level for detecting drift in either direction.
- Discrimination, measured as area under the ROC curve on each seasoned vintage and read against the declared floor of 0.65 [[art:fececac1:threshold.package.auc.test.min]]; this validation recomputed 0.6549 [[art:f3890b65:metrics.test.auc]] on the held-out sample, which clears that floor by a thin margin, so monitoring should treat the trend across vintages, and not only the level in any single vintage, as the operative signal.
- Population stability of the model inputs and of the score itself, computed from each production vintage against the development population and read against the declared cap of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]]; the largest train-to-test value observed in this validation was 0.005703 [[art:f632d5d4:psi.max]], a very low baseline against which even modest production movement will be visible well before the cap is approached.

Because the margin between the recomputed discrimination and its declared floor is thin, the monitoring plan should set an internal review trigger inside each bound rather than waiting for the bound itself to be crossed, and should record the direction and persistence of movement so that a transient vintage is distinguished from deterioration.

### Frequency

Stability measures require no realised outcomes and should be produced on the servicing system's monthly reporting cycle, so that input drift and score drift are seen as they emerge.

Calibration and discrimination require realised prepayment outcomes and should be produced quarterly on vintages that have seasoned through the model's performance window, with a rolling multi-vintage view alongside the single-vintage figure so that sampling noise in a short window is not read as deterioration.

The scope and frequency of these reports should be revisited as the availability of new data or modelling approaches changes and in light of the model's materiality [[reg:SR26-2:V.2]].

### How the monitoring report should order its evidence

The monitoring report should present calibration before discrimination, as this report did in its model-performance section, because the package declaration states that this model's output is used as a probability and not only as a ranking.

On that use, a score that ranks loans correctly but mis-states the level of prepayment probability will mis-state servicing cash flows, so the absolute accuracy of the estimate is the primary question and rank-ordering ability is the secondary one; outcomes analysis should be chosen to match the model's objective and business use in exactly this way [[reg:SR26-2:V.1.b]].

### Benchmarking in production

An earlier section of this report compared the champion with a challenger on the development data, and monitoring should extend that comparison rather than repeat it.

What monitoring adds is the challenger refitted on successive production vintages, which the development data cannot give: a refit on live experience reveals whether the relationships the champion encodes are still the relationships the current book exhibits, and a widening gap between champion and refitted challenger is evidence about the champion's continued fitness rather than about the challenger's merits.

Discrepancies between the champion and this benchmark should trigger investigation into the sources and degree of the differences and an examination of whether they fall within an expected range, since the benchmark is itself an alternative prediction and differences do not by themselves indicate that the model is in error [[reg:SR11-7:V.1.b]].

### What this validation could not cover and monitoring should watch instead

This validation's performance evidence rests on a held-out sample drawn from the development data, so monitoring should carry the back-testing that only production experience can supply, comparing realised prepayment outcomes with the model's forecasts over the forecast horizon and investigating deviations that are material in magnitude or frequency [[reg:SR26-2:V.1.b]].

The development sample cannot speak to interest-rate regimes, refinancing waves, or servicing-transfer conditions that it did not contain, so monitoring should identify when input values or market conditions approach or exceed the ranges over which the model was estimated and should repeat sensitivity and stability checks periodically [[reg:SR11-7:V.1.b]].

Behaviour of the model in use lies outside a pre-implementation validation, so monitoring should track overrides of the model output with appropriate documentation, evaluate the reasons for them, and analyse override performance, since a high override rate or overrides that consistently improve results signals that the underlying model needs revision [[reg:SR11-7:V.1.b]].

Implementation in production systems likewise lies outside this exercise, so monitoring should include process verification that the data feeds remain accurate, complete, and consistent with the model's purpose and design, and that code changes are controlled, logged, and auditable [[reg:SR11-7:V.1.b]].

Segment-level behaviour on populations that emerge after deployment should be watched as well, with calibration and discrimination reported by the segments that matter to servicing economics rather than only in aggregate, so that offsetting movements within the portfolio are not hidden by a stable overall figure.

Even with sound modelling and rigorous validation, material model risk can remain, and users of this model's output benefit from understanding and communicating its limitations, monitoring performance, periodically reviewing relevance, and supplementing the output with complementary analysis [[reg:SR26-2:V]].

## Appendix A — Claims

Grounding precision 0.9966 before repair (297 of 298 claims verified; 1 unsupported) and 1.0000 after 0 claim(s) rewritten and 1 number(s) removed from the prose. Per section (post-repair): summary 12/12; conceptual_soundness 48/48; data_integrity 70/70; outcomes 109/109; sensitivity 30/30; findings 21/21; monitoring 7/7.

Developer claims: 3 of 3 declared in `package.yaml` verify against this run's artifacts.

Excluded numeric tokens (not claims): section_number (section 6, 5.1, 5.2, 5.3); citation_hash (2ad8d1a5, 72c7a6d2, 629740ff, faabc78e); regulatory_section_id (SR26-2:V, SR26-2:V.1.a, SR11-7:V.1.a, SR26-2:IV.1); finding_id (F-001); extractor_returned_excluded_token (26.0, 2, 001,, 6).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The subject was re-executed from its package and its metrics… | 300 | ratio | max_seconds |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 2 | summary | The recomputation covers four splits: a training sample of 3… | 313538 | count | n | train | eq | `[[art:72c7a6d2:metrics.train.n]]` | verified | 313538 |
| 3 | summary | The recomputation covers four splits: a training sample of 3… | 135060 | count | n | test | eq | `[[art:629740ff:metrics.test.n]]` | verified | 135060 |
| 4 | summary | The recomputation covers four splits: a training sample of 3… | 221779 | count | n | vintage_holdout | eq | `[[art:faabc78e:metrics.vintage_holdout.n]]` | verified | 221779 |
| 5 | summary | The recomputation covers four splits: a training sample of 3… | 283343 | count | n | out_of_time | eq | `[[art:c164ae00:metrics.out_of_time.n]]` | verified | 283343 |
| 6 | summary | Discrimination on the test split, at 0.6549 , clears the dec… | 0.6549 | ratio | auc | test | eq | `[[art:f3890b65:metrics.test.auc]]` | verified | 0.6549316245 |
| 7 | summary | Discrimination on the test split, at 0.6549 , clears the dec… | 0.65 | ratio | auc | test | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 8 | summary | The calibration slope on the test split, at 1.017 , sits ins… | 1.017 | ratio | calibration_slope | test | eq | `[[art:9b1edaa3:calibration_slope.test]]` | verified | 1.01683551 |
| 9 | summary | The calibration slope on the test split, at 1.017 , sits ins… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 10 | summary | The calibration slope on the test split, at 1.017 , sits ins… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 11 | summary | The largest train-to-test population stability index, at 0.0… | 0.005703 | ratio | psi |  | eq | `[[art:f632d5d4:psi.max]]` | verified | 0.005703237396 |
| 12 | summary | The largest train-to-test population stability index, at 0.0… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 13 | conceptual_soundness | The champion is a single fitted probability equation for mon… | -4.79 | ratio | intercept |  | eq | `[[art:29028ebe:run.model_summary#intercept]]` | verified | -4.790257858 |
| 14 | conceptual_soundness | It was estimated on 313538 loan-month records drawn from 859… | 313538 | count | n_train | train | eq | `[[art:29028ebe:run.model_summary#n_train]]` | verified | 313538 |
| 15 | conceptual_soundness | It was estimated on 313538 loan-month records drawn from 859… | 8596 | count | n_train_loans | train | eq | `[[art:29028ebe:run.model_summary#n_train_loans]]` | verified | 8596 |
| 16 | conceptual_soundness | The feature inventory carries 12 features, of which 5 are fi… | 12 | count | n |  | eq | `[[art:0849f814:run.features#n]]` | verified | 12 |
| 17 | conceptual_soundness | The feature inventory carries 12 features, of which 5 are fi… | 5 | count | at_origination |  | eq | `[[art:0849f814:run.features#at_origination]]` | verified | 5 |
| 18 | conceptual_soundness | The feature inventory carries 12 features, of which 5 are fi… | 7 | count | before_period_start |  | eq | `[[art:0849f814:run.features#before_period_start]]` | verified | 7 |
| 19 | conceptual_soundness | No feature is dated during the performance period, at 0 , an… | 0 | count | during_period |  | eq | `[[art:0849f814:run.features#during_period]]` | verified | 0 |
| 20 | conceptual_soundness | No feature is dated during the performance period, at 0 , an… | 0 | count | after_outcome |  | eq | `[[art:0849f814:run.features#after_outcome]]` | verified | 0 |
| 21 | conceptual_soundness | The developer's own screen removed terms on a variance-infla… | 10 | ratio | vif_threshold |  | eq | `[[art:29028ebe:run.model_summary#vif_threshold]]` | verified | 10 |
| 22 | conceptual_soundness | Beginning-of-month balance in logs was dropped at 16.5 , and… | 16.5 | ratio | vif |  | eq | `[[art:29028ebe:run.model_summary#removed.bom_balance_log.vif]]` | verified | 16.49621 |
| 23 | conceptual_soundness | Beginning-of-month balance in logs was dropped at 16.5 , and… | 18.07 | ratio | vif |  | eq | `[[art:29028ebe:run.model_summary#removed.note_rate.vif]]` | verified | 18.069373 |
| 24 | conceptual_soundness | The largest coefficients are the leading loan-age spline seg… | 0.611 | ratio | coefficient |  | eq | `[[art:29028ebe:run.model_summary#coefficients.loan_age_spline_1.value]]` | verified | 0.6109670628 |
| 25 | conceptual_soundness | The largest coefficients are the leading loan-age spline seg… | 0.3952 | ratio | coefficient |  | eq | `[[art:29028ebe:run.model_summary#coefficients.incentive.value]]` | verified | 0.3951616506 |
| 26 | conceptual_soundness | The largest coefficients are the leading loan-age spline seg… | 0.286 | ratio | coefficient |  | eq | `[[art:29028ebe:run.model_summary#coefficients.orig_upb_log.value]]` | verified | 0.2860296007 |
| 27 | conceptual_soundness | The remaining loan-age segments run negative, at -0.04263 ,… | -0.04263 | ratio | coefficient |  | eq | `[[art:29028ebe:run.model_summary#coefficients.loan_age_spline_2.value]]` | verified | -0.04262684642 |
| 28 | conceptual_soundness | The remaining loan-age segments run negative, at -0.04263 ,… | -0.1501 | ratio | coefficient |  | eq | `[[art:29028ebe:run.model_summary#coefficients.loan_age_spline_3.value]]` | verified | -0.1501198233 |
| 29 | conceptual_soundness | The remaining loan-age segments run negative, at -0.04263 ,… | -0.254 | ratio | coefficient |  | eq | `[[art:29028ebe:run.model_summary#coefficients.loan_age_spline_4.value]]` | verified | -0.2539751749 |
| 30 | conceptual_soundness | The coefficient on the twelve-month rate change is -0.06772… | -0.06772 | ratio | coefficient |  | eq | `[[art:29028ebe:run.model_summary#coefficients.rate_change_12m.value]]` | verified | -0.06772214655 |
| 31 | conceptual_soundness | The coefficient on the twelve-month rate change is -0.06772… | 0.02917 | ratio | coefficient |  | eq | `[[art:29028ebe:run.model_summary#coefficients.credit_score.value]]` | verified | 0.02916512564 |
| 32 | conceptual_soundness | The seasonal terms, at 0.01281 and -0.04626 , carry a modest… | 0.01281 | ratio | coefficient |  | eq | `[[art:29028ebe:run.model_summary#coefficients.season_sin.value]]` | verified | 0.01280983524 |
| 33 | conceptual_soundness | The seasonal terms, at 0.01281 and -0.04626 , carry a modest… | -0.04626 | ratio | coefficient |  | eq | `[[art:29028ebe:run.model_summary#coefficients.season_cos.value]]` | verified | -0.04626116305 |
| 34 | conceptual_soundness | Burnout enters positively at 0.0008253 , which runs against… | 0.0008253 | ratio | coefficient |  | eq | `[[art:29028ebe:run.model_summary#coefficients.burnout.value]]` | verified | 0.000825312491 |
| 35 | conceptual_soundness | Those refits are measured from a level of 0.6391 on test, wh… | 0.6391 | ratio | baseline_auc | test | eq | `[[art:ed55c319:ablation.baseline_auc]]` | verified | 0.6391430546 |
| 36 | conceptual_soundness | The model's discrimination rests mainly on log original bala… | -0.0171 | ratio | delta_auc | test | eq | `[[art:d9fda2c8:ablation.orig_upb_log.delta_auc]]` | verified | -0.01710427827 |
| 37 | conceptual_soundness | The model's discrimination rests mainly on log original bala… | -0.0161 | ratio | delta_auc | test | eq | `[[art:b1880518:ablation.incentive.delta_auc]]` | verified | -0.01609580876 |
| 38 | conceptual_soundness | The model's discrimination rests mainly on log original bala… | 1 | ratio | agrees |  | eq | `[[art:07a9d3e6:sign_check.orig_upb_log.agrees]]` | verified | 1 |
| 39 | conceptual_soundness | The model's discrimination rests mainly on log original bala… | 1 | ratio | agrees |  | eq | `[[art:f7b2338e:sign_check.incentive.agrees]]` | verified | 1 |
| 40 | conceptual_soundness | Loan age contributes -0.004572 , and the remaining terms con… | -0.004572 | ratio | delta_auc | test | eq | `[[art:0b5dcaeb:ablation.loan_age.delta_auc]]` | verified | -0.004571578483 |
| 41 | conceptual_soundness | Loan age contributes -0.004572 , and the remaining terms con… | -0.0002604 | ratio | delta_auc | test | eq | `[[art:9963f841:ablation.credit_score.delta_auc]]` | verified | -0.0002603974752 |
| 42 | conceptual_soundness | Loan age contributes -0.004572 , and the remaining terms con… | -0.0003635 | ratio | delta_auc | test | eq | `[[art:f472749f:ablation.rate_change_12m.delta_auc]]` | verified | -0.0003635311596 |
| 43 | conceptual_soundness | Loan age contributes -0.004572 , and the remaining terms con… | 0.0005739 | ratio | delta_auc | test | eq | `[[art:499cf97d:ablation.burnout.delta_auc]]` | verified | 0.0005738937198 |
| 44 | conceptual_soundness | Loan age contributes -0.004572 , and the remaining terms con… | 0.001845 | ratio | delta_auc | test | eq | `[[art:0931b2a0:ablation.season_cos.delta_auc]]` | verified | 0.001844627367 |
| 45 | conceptual_soundness | Of the retained features whose fitted sign was compared with… | 3 | count | n_disagreements | train | eq | `[[art:e223cd4a:sign_check.n_disagreements]]` | verified | 3 |
| 46 | conceptual_soundness | Original LTV is fitted with a sign of -1 against a univariat… | -1 | ratio | coef_sign |  | eq | `[[art:7eec65ec:sign_check.orig_ltv.coef_sign]]` | verified | -1 |
| 47 | conceptual_soundness | Original LTV is fitted with a sign of -1 against a univariat… | 1 | ratio | univariate_direction |  | eq | `[[art:85aabf06:sign_check.orig_ltv.univariate_direction]]` | verified | 1 |
| 48 | conceptual_soundness | Original LTV is fitted with a sign of -1 against a univariat… | -0.002233 | ratio | delta_auc | test | eq | `[[art:acb0dcd5:ablation.orig_ltv.delta_auc]]` | verified | -0.002233212172 |
| 49 | conceptual_soundness | Spread at origination is fitted with a sign of -1 against a… | -1 | ratio | coef_sign |  | eq | `[[art:265915cf:sign_check.sato.coef_sign]]` | verified | -1 |
| 50 | conceptual_soundness | Spread at origination is fitted with a sign of -1 against a… | 1 | ratio | univariate_direction |  | eq | `[[art:c08233a6:sign_check.sato.univariate_direction]]` | verified | 1 |
| 51 | conceptual_soundness | Spread at origination is fitted with a sign of -1 against a… | -0.003026 | ratio | delta_auc | test | eq | `[[art:f406b192:ablation.sato.delta_auc]]` | verified | -0.003026491141 |
| 52 | conceptual_soundness | The sine seasonal term is fitted with a sign of 1 against a… | 1 | ratio | coef_sign |  | eq | `[[art:761188ce:sign_check.season_sin.coef_sign]]` | verified | 1 |
| 53 | conceptual_soundness | The sine seasonal term is fitted with a sign of 1 against a… | -1 | ratio | univariate_direction |  | eq | `[[art:b75f0b9c:sign_check.season_sin.univariate_direction]]` | verified | -1 |
| 54 | conceptual_soundness | The sine seasonal term is fitted with a sign of 1 against a… | 0.000108 | ratio | delta_auc | test | eq | `[[art:47876c72:ablation.season_sin.delta_auc]]` | verified | 0.0001080069018 |
| 55 | conceptual_soundness | The champion scores 0.6549 on test and the challenger scores… | 0.6549 | ratio | auc | test | eq | `[[art:f3890b65:metrics.test.auc]]` | verified | 0.6549316245 |
| 56 | conceptual_soundness | The champion scores 0.6549 on test and the challenger scores… | 0.6653 | ratio | auc | test | eq | `[[art:6f811314:challenger.auc]]` | verified | 0.6653496435 |
| 57 | conceptual_soundness | The champion scores 0.6549 on test and the challenger scores… | 0.01042 | ratio | delta_auc | test | eq | `[[art:10b988e8:challenger.delta_auc]]` | verified | 0.01041801898 |
| 58 | conceptual_soundness | The threshold at which a challenger's discrimination advanta… | 0.03 | ratio | delta_auc |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 59 | conceptual_soundness | On squared error the ordering reverses, with the champion at… | 0.009063 | ratio | brier | test | eq | `[[art:21d0b581:metrics.test.brier]]` | verified | 0.009062660213 |
| 60 | conceptual_soundness | On squared error the ordering reverses, with the champion at… | 0.009119 | ratio | brier | test | eq | `[[art:0e717888:challenger.brier]]` | verified | 0.00911859482 |
| 61 | data_integrity | The training split holds 313538 rows, the test split 135060… | 313538 | count | n | train | eq | `[[art:6582e5dd:profile.train.n]]` | verified | 313538 |
| 62 | data_integrity | The training split holds 313538 rows, the test split 135060… | 135060 | count | n | test | eq | `[[art:75b5b833:profile.test.n]]` | verified | 135060 |
| 63 | data_integrity | The training split holds 313538 rows, the test split 135060… | 221779 | count | n | vintage_holdout | eq | `[[art:fcb7e414:profile.vintage_holdout.n]]` | verified | 221779 |
| 64 | data_integrity | The training split holds 313538 rows, the test split 135060… | 283343 | count | n | out_of_time | eq | `[[art:a0103a06:profile.out_of_time.n]]` | verified | 283343 |
| 65 | data_integrity | The largest missing fraction over any column is 0 in train,… | 0 | ratio | missing_max | train | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 66 | data_integrity | The largest missing fraction over any column is 0 in train,… | 0 | ratio | missing_max | test | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 67 | data_integrity | The largest missing fraction over any column is 0 in train,… | 0 | ratio | missing_max | vintage_holdout | eq | `[[art:329bb430:profile.vintage_holdout.missing.max]]` | verified | 0 |
| 68 | data_integrity | The largest missing fraction over any column is 0 in train,… | 0 | ratio | missing_max | out_of_time | eq | `[[art:4dafce11:profile.out_of_time.missing.max]]` | verified | 0 |
| 69 | data_integrity | Because those four values agree exactly, the gap in missingn… | 0.1 | ratio | missing_gap |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 70 | data_integrity | The declared stability bound is 0.25 , and the model package… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 71 | data_integrity | The declared stability bound is 0.25 , and the model package… | 0.25 | ratio | psi_max |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 72 | data_integrity | Between train and test the population stability index is 0.0… | 0.001567 | ratio | psi |  | eq | `[[art:40a3f946:psi.burnout]]` | verified | 0.001566859823 |
| 73 | data_integrity | Between train and test the population stability index is 0.0… | 0.003718 | ratio | psi |  | eq | `[[art:8a078965:psi.credit_score]]` | verified | 0.003717519291 |
| 74 | data_integrity | Between train and test the population stability index is 0.0… | 0.0003749 | ratio | psi |  | eq | `[[art:61538982:psi.incentive]]` | verified | 0.0003749417053 |
| 75 | data_integrity | Between train and test the population stability index is 0.0… | 8.302e-05 | ratio | psi |  | eq | `[[art:f548214d:psi.loan_age]]` | verified | 8.302102495e-05 |
| 76 | data_integrity | It is 0.005703 for original LTV, 0.002753 for log original b… | 0.005703 | ratio | psi |  | eq | `[[art:6ea40553:psi.orig_ltv]]` | verified | 0.005703237396 |
| 77 | data_integrity | It is 0.005703 for original LTV, 0.002753 for log original b… | 0.002753 | ratio | psi |  | eq | `[[art:4af07770:psi.orig_upb_log]]` | verified | 0.002752784614 |
| 78 | data_integrity | It is 0.005703 for original LTV, 0.002753 for log original b… | 3.589e-05 | ratio | psi |  | eq | `[[art:23b9e924:psi.rate_change_12m]]` | verified | 3.588607828e-05 |
| 79 | data_integrity | It is 0.005703 for original LTV, 0.002753 for log original b… | 0.002192 | ratio | psi |  | eq | `[[art:e68bfd2e:psi.sato]]` | verified | 0.002192276542 |
| 80 | data_integrity | The two seasonal terms move least, at 3.184e-06 and 3.366e-0… | 3.184e-06 | ratio | psi |  | eq | `[[art:9db38513:psi.season_cos]]` | verified | 3.183525037e-06 |
| 81 | data_integrity | The two seasonal terms move least, at 3.184e-06 and 3.366e-0… | 3.366e-06 | ratio | psi |  | eq | `[[art:ae17ebba:psi.season_sin]]` | verified | 3.365586451e-06 |
| 82 | data_integrity | The two seasonal terms move least, at 3.184e-06 and 3.366e-0… | 0.0006641 | ratio | psi |  | eq | `[[art:6e6c94e1:psi.y_score]]` | verified | 0.0006640882006 |
| 83 | data_integrity | The largest train-to-test value, score included, is 0.005703… | 0.005703 | ratio | psi_max |  | eq | `[[art:f632d5d4:psi.max]]` | verified | 0.005703237396 |
| 84 | data_integrity | The largest train-to-test value, score included, is 0.005703… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 85 | data_integrity | There the index is 0.5116 for burnout, 1.298 for incentive,… | 0.5116 | ratio | psi | vintage_holdout | eq | `[[art:e3a3122f:psi.vintage_holdout.burnout]]` | verified | 0.5116279641 |
| 86 | data_integrity | There the index is 0.5116 for burnout, 1.298 for incentive,… | 1.298 | ratio | psi | vintage_holdout | eq | `[[art:86f7884e:psi.vintage_holdout.incentive]]` | verified | 1.297995585 |
| 87 | data_integrity | There the index is 0.5116 for burnout, 1.298 for incentive,… | 0.8816 | ratio | psi | vintage_holdout | eq | `[[art:2575a328:psi.vintage_holdout.rate_change_12m]]` | verified | 0.8816315659 |
| 88 | data_integrity | There the index is 0.5116 for burnout, 1.298 for incentive,… | 0.7656 | ratio | psi | vintage_holdout | eq | `[[art:ae7b9c29:psi.vintage_holdout.y_score]]` | verified | 0.7656434406 |
| 89 | data_integrity | There the index is 0.5116 for burnout, 1.298 for incentive,… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 90 | data_integrity | The remaining features stay inside that bound: 0.007218 for… | 0.007218 | ratio | psi | vintage_holdout | eq | `[[art:341abd78:psi.vintage_holdout.credit_score]]` | verified | 0.007217892201 |
| 91 | data_integrity | The remaining features stay inside that bound: 0.007218 for… | 0.1507 | ratio | psi | vintage_holdout | eq | `[[art:2de85f94:psi.vintage_holdout.loan_age]]` | verified | 0.1506849325 |
| 92 | data_integrity | The remaining features stay inside that bound: 0.007218 for… | 0.01065 | ratio | psi | vintage_holdout | eq | `[[art:a5066c0f:psi.vintage_holdout.orig_ltv]]` | verified | 0.01065378135 |
| 93 | data_integrity | The remaining features stay inside that bound: 0.007218 for… | 0.03076 | ratio | psi | vintage_holdout | eq | `[[art:bd074d53:psi.vintage_holdout.orig_upb_log]]` | verified | 0.03076150585 |
| 94 | data_integrity | The remaining features stay inside that bound: 0.007218 for… | 0.2002 | ratio | psi | vintage_holdout | eq | `[[art:b34d2ebe:psi.vintage_holdout.sato]]` | verified | 0.2002005108 |
| 95 | data_integrity | The remaining features stay inside that bound: 0.007218 for… | 0.000942 | ratio | psi | vintage_holdout | eq | `[[art:67aee1b5:psi.vintage_holdout.season_cos]]` | verified | 0.0009420084002 |
| 96 | data_integrity | The remaining features stay inside that bound: 0.007218 for… | 0.003659 | ratio | psi | vintage_holdout | eq | `[[art:dad1e65c:psi.vintage_holdout.season_sin]]` | verified | 0.003658742975 |
| 97 | data_integrity | Against the out-of-time split the separation is wider still,… | 3.086 | ratio | psi | out_of_time | eq | `[[art:5f3c6bba:psi.out_of_time.loan_age]]` | verified | 3.085573352 |
| 98 | data_integrity | Against the out-of-time split the separation is wider still,… | 1.726 | ratio | psi | out_of_time | eq | `[[art:73dfd106:psi.out_of_time.incentive]]` | verified | 1.726005597 |
| 99 | data_integrity | Against the out-of-time split the separation is wider still,… | 1.551 | ratio | psi | out_of_time | eq | `[[art:5316f456:psi.out_of_time.burnout]]` | verified | 1.551357138 |
| 100 | data_integrity | Against the out-of-time split the separation is wider still,… | 0.8254 | ratio | psi | out_of_time | eq | `[[art:09e68722:psi.out_of_time.rate_change_12m]]` | verified | 0.8254176602 |
| 101 | data_integrity | Against the out-of-time split the separation is wider still,… | 1.54 | ratio | psi | out_of_time | eq | `[[art:75370112:psi.out_of_time.y_score]]` | verified | 1.539886915 |
| 102 | data_integrity | Against the out-of-time split the separation is wider still,… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 103 | data_integrity | The other out-of-time comparisons remain small: 0.004578 for… | 0.004578 | ratio | psi | out_of_time | eq | `[[art:5341c0a9:psi.out_of_time.credit_score]]` | verified | 0.004578346658 |
| 104 | data_integrity | The other out-of-time comparisons remain small: 0.004578 for… | 0.01598 | ratio | psi | out_of_time | eq | `[[art:7f6fab7a:psi.out_of_time.orig_ltv]]` | verified | 0.01597816452 |
| 105 | data_integrity | The other out-of-time comparisons remain small: 0.004578 for… | 0.02136 | ratio | psi | out_of_time | eq | `[[art:abf1e02d:psi.out_of_time.orig_upb_log]]` | verified | 0.02135726451 |
| 106 | data_integrity | The other out-of-time comparisons remain small: 0.004578 for… | 0.01473 | ratio | psi | out_of_time | eq | `[[art:85a8a904:psi.out_of_time.sato]]` | verified | 0.01472768815 |
| 107 | data_integrity | The other out-of-time comparisons remain small: 0.004578 for… | 0.00591 | ratio | psi | out_of_time | eq | `[[art:8ef132e3:psi.out_of_time.season_cos]]` | verified | 0.005910467488 |
| 108 | data_integrity | The other out-of-time comparisons remain small: 0.004578 for… | 0.02419 | ratio | psi | out_of_time | eq | `[[art:7388771e:psi.out_of_time.season_sin]]` | verified | 0.0241861509 |
| 109 | data_integrity | Characteristic stability, measured as each feature's contrib… | 3.43e-06 | ratio | csi |  | eq | `[[art:e4d3e34a:csi.burnout]]` | verified | 3.430062025e-06 |
| 110 | data_integrity | Characteristic stability, measured as each feature's contrib… | 1.97e-05 | ratio | csi |  | eq | `[[art:0a280759:csi.credit_score]]` | verified | 1.970189663e-05 |
| 111 | data_integrity | Characteristic stability, measured as each feature's contrib… | 0.001102 | ratio | csi |  | eq | `[[art:020f5ce2:csi.incentive]]` | verified | 0.001102078062 |
| 112 | data_integrity | Characteristic stability, measured as each feature's contrib… | 0 | ratio | csi |  | eq | `[[art:df52c920:csi.loan_age]]` | verified | 0 |
| 113 | data_integrity | It is 0.0005902 for original LTV, 0.006455 for log original… | 0.0005902 | ratio | csi |  | eq | `[[art:1c9006f3:csi.orig_ltv]]` | verified | 0.0005902054355 |
| 114 | data_integrity | It is 0.0005902 for original LTV, 0.006455 for log original… | 0.006455 | ratio | csi |  | eq | `[[art:7561e8b0:csi.orig_upb_log]]` | verified | 0.00645531823 |
| 115 | data_integrity | It is 0.0005902 for original LTV, 0.006455 for log original… | 0.0002237 | ratio | csi |  | eq | `[[art:ffdb6fdd:csi.rate_change_12m]]` | verified | 0.0002237020655 |
| 116 | data_integrity | It is 0.0005902 for original LTV, 0.006455 for log original… | 0.001116 | ratio | csi |  | eq | `[[art:a54b158e:csi.sato]]` | verified | 0.001115931346 |
| 117 | data_integrity | It is 0.0005902 for original LTV, 0.006455 for log original… | 6.191e-05 | ratio | csi |  | eq | `[[art:c70e3aa4:csi.season_cos]]` | verified | 6.190848201e-05 |
| 118 | data_integrity | It is 0.0005902 for original LTV, 0.006455 for log original… | 2.108e-05 | ratio | csi |  | eq | `[[art:fb3bf812:csi.season_sin]]` | verified | 2.108057316e-05 |
| 119 | data_integrity | The largest such contribution is 0.006455 , far below the de… | 0.006455 | ratio | csi_max |  | eq | `[[art:131d42db:csi.max]]` | verified | 0.00645531823 |
| 120 | data_integrity | The largest such contribution is 0.006455 , far below the de… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 121 | data_integrity | The timing declarations were screened first, and the count o… | 0 | count | n_flagged |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 122 | data_integrity | The strongest single feature reaches an AUC of 0.5995 on its… | 0.5995 | ratio | max_single_feature_auc |  | eq | `[[art:9e2ffad1:leakage.target_corr.max_single_feature_auc]]` | verified | 0.5994570075 |
| 123 | data_integrity | The strongest single feature reaches an AUC of 0.5995 on its… | 0.9 | ratio | single_feature_auc |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 124 | data_integrity | The identifier arm, the share of test rows whose loan and pe… | 0 | ratio | overlap_ids |  | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 125 | data_integrity | The identifier arm, the share of test rows whose loan and pe… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 126 | data_integrity | The feature-vector arm, the share of test rows whose feature… | 0 | ratio | overlap_features |  | eq | `[[art:0fec8048:leakage.overlap.features]]` | verified | 0 |
| 127 | data_integrity | The feature-vector arm, the share of test rows whose feature… | 0.005 | ratio | overlap_features_effective |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 128 | data_integrity | That effective bound is the larger of the declared 0.005 and… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 129 | data_integrity | That effective bound is the larger of the declared 0.005 and… | 0.0001531 | ratio | duplicates | train | eq | `[[art:ce57652e:leakage.duplicates.train]]` | verified | 0.0001530914913 |
| 130 | data_integrity | The name screen matched 0 feature names against the target-a… | 0 | count | n_matched |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 131 | outcomes | The logistic recalibration slope is 0.9971 on train and 1.01… | 0.9971 | ratio | calibration_slope | train | eq | `[[art:28331672:calibration_slope.train]]` | verified | 0.9971012419 |
| 132 | outcomes | The logistic recalibration slope is 0.9971 on train and 1.01… | 1.017 | ratio | calibration_slope | test | eq | `[[art:9b1edaa3:calibration_slope.test]]` | verified | 1.01683551 |
| 133 | outcomes | The logistic recalibration slope is 0.9971 on train and 1.01… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 134 | outcomes | The logistic recalibration slope is 0.9971 on train and 1.01… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 135 | outcomes | On the forward splits the slope falls to 0.8502 on the vinta… | 0.8502 | ratio | calibration_slope | vintage_holdout | eq | `[[art:80fe61d2:calibration_slope.vintage_holdout]]` | verified | 0.8501990162 |
| 136 | outcomes | On the forward splits the slope falls to 0.8502 on the vinta… | 0.4321 | ratio | calibration_slope | out_of_time | eq | `[[art:d9f87bb2:calibration_slope.out_of_time]]` | verified | 0.432125782 |
| 137 | outcomes | On the forward splits the slope falls to 0.8502 on the vinta… | 0.8 | ratio | calibration_slope |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 138 | outcomes | The corresponding intercepts are -0.016 on train, 0.02905 on… | -0.016 | ratio | calibration_intercept | train | eq | `[[art:be40e0a7:calibration_intercept.train]]` | verified | -0.01599765114 |
| 139 | outcomes | The corresponding intercepts are -0.016 on train, 0.02905 on… | 0.02905 | ratio | calibration_intercept | test | eq | `[[art:1a8280dd:calibration_intercept.test]]` | verified | 0.02905298382 |
| 140 | outcomes | The corresponding intercepts are -0.016 on train, 0.02905 on… | 0.06119 | ratio | calibration_intercept | vintage_holdout | eq | `[[art:0d75b532:calibration_intercept.vintage_holdout]]` | verified | 0.06118872124 |
| 141 | outcomes | The corresponding intercepts are -0.016 on train, 0.02905 on… | -1.762 | ratio | calibration_intercept | out_of_time | eq | `[[art:53a8d76b:calibration_intercept.out_of_time]]` | verified | -1.761998635 |
| 142 | outcomes | Mean predicted probability is 0.009503 against an observed r… | 0.009503 | ratio | mean_predicted | train | eq | `[[art:716b94b2:metrics.train.mean_predicted]]` | verified | 0.009503175968 |
| 143 | outcomes | Mean predicted probability is 0.009503 against an observed r… | 0.009476 | ratio | event_rate | train | eq | `[[art:8ecc2809:metrics.train.event_rate]]` | verified | 0.00947572543 |
| 144 | outcomes | Mean predicted probability is 0.009503 against an observed r… | 0.002897 | ratio | mean_rel_gap | train | eq | `[[art:332fc4d9:calibration.mean_rel_gap.train]]` | verified | 0.002896932549 |
| 145 | outcomes | On test it is 0.009606 against 0.009174 , a relative gap of… | 0.009606 | ratio | mean_predicted | test | eq | `[[art:24595a04:metrics.test.mean_predicted]]` | verified | 0.009605653506 |
| 146 | outcomes | On test it is 0.009606 against 0.009174 , a relative gap of… | 0.009174 | ratio | event_rate | test | eq | `[[art:78206f7c:metrics.test.event_rate]]` | verified | 0.009173700578 |
| 147 | outcomes | On test it is 0.009606 against 0.009174 , a relative gap of… | 0.04709 | ratio | mean_rel_gap | test | eq | `[[art:a173f6c5:calibration.mean_rel_gap.test]]` | verified | 0.04708600686 |
| 148 | outcomes | Both sit inside the tolerance of 0.25 . | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 149 | outcomes | On the vintage holdout mean predicted is 0.009873 against an… | 0.009873 | ratio | mean_predicted | vintage_holdout | eq | `[[art:c12c52f7:metrics.vintage_holdout.mean_predicted]]` | verified | 0.009872671801 |
| 150 | outcomes | On the vintage holdout mean predicted is 0.009873 against an… | 0.01948 | ratio | event_rate | vintage_holdout | eq | `[[art:bab66615:metrics.vintage_holdout.event_rate]]` | verified | 0.01947885057 |
| 151 | outcomes | On the vintage holdout mean predicted is 0.009873 against an… | 0.4932 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:92b5a8c4:calibration.mean_rel_gap.vintage_holdout]]` | verified | 0.4931594261 |
| 152 | outcomes | Out of time mean predicted is 0.01005 against an observed ra… | 0.01005 | ratio | mean_predicted | out_of_time | eq | `[[art:fd777cc4:metrics.out_of_time.mean_predicted]]` | verified | 0.01005421904 |
| 153 | outcomes | Out of time mean predicted is 0.01005 against an observed ra… | 0.01868 | ratio | event_rate | out_of_time | eq | `[[art:cf3a82aa:metrics.out_of_time.event_rate]]` | verified | 0.01868053913 |
| 154 | outcomes | Out of time mean predicted is 0.01005 against an observed ra… | 0.4618 | ratio | mean_rel_gap | out_of_time | eq | `[[art:9e4c8750:calibration.mean_rel_gap.out_of_time]]` | verified | 0.4617811099 |
| 155 | outcomes | The portfolio-level restatement points the same way: mean ab… | 0.02202 | ratio | cpr_mae | train | eq | `[[art:3487a403:cpr.train.mae]]` | verified | 0.02201633853 |
| 156 | outcomes | The portfolio-level restatement points the same way: mean ab… | 0.02642 | ratio | cpr_mae | test | eq | `[[art:939c5fb9:cpr.test.mae]]` | verified | 0.02641734834 |
| 157 | outcomes | The portfolio-level restatement points the same way: mean ab… | 0.0785 | ratio | cpr_mae | vintage_holdout | eq | `[[art:0cc82390:cpr.vintage_holdout.mae]]` | verified | 0.07850151406 |
| 158 | outcomes | The portfolio-level restatement points the same way: mean ab… | 0.08656 | ratio | cpr_mae | out_of_time | eq | `[[art:a467ad41:cpr.out_of_time.mae]]` | verified | 0.08656382516 |
| 159 | outcomes | AUC is 0.6504 on train, 0.6549 on test, 0.7388 on the vintag… | 0.6504 | ratio | auc | train | eq | `[[art:40964132:metrics.train.auc]]` | verified | 0.6503543409 |
| 160 | outcomes | AUC is 0.6504 on train, 0.6549 on test, 0.7388 on the vintag… | 0.6549 | ratio | auc | test | eq | `[[art:f3890b65:metrics.test.auc]]` | verified | 0.6549316245 |
| 161 | outcomes | AUC is 0.6504 on train, 0.6549 on test, 0.7388 on the vintag… | 0.7388 | ratio | auc | vintage_holdout | eq | `[[art:95f87cc7:metrics.vintage_holdout.auc]]` | verified | 0.7388200711 |
| 162 | outcomes | AUC is 0.6504 on train, 0.6549 on test, 0.7388 on the vintag… | 0.6898 | ratio | auc | out_of_time | eq | `[[art:cb57fe9a:metrics.out_of_time.auc]]` | verified | 0.6898015086 |
| 163 | outcomes | Gini is 0.3007 on train, 0.3099 on test, 0.4776 on the vinta… | 0.3007 | ratio | gini | train | eq | `[[art:da0e7063:metrics.train.gini]]` | verified | 0.3007086819 |
| 164 | outcomes | Gini is 0.3007 on train, 0.3099 on test, 0.4776 on the vinta… | 0.3099 | ratio | gini | test | eq | `[[art:5710cba3:metrics.test.gini]]` | verified | 0.309863249 |
| 165 | outcomes | Gini is 0.3007 on train, 0.3099 on test, 0.4776 on the vinta… | 0.4776 | ratio | gini | vintage_holdout | eq | `[[art:75ad81b1:metrics.vintage_holdout.gini]]` | verified | 0.4776401422 |
| 166 | outcomes | Gini is 0.3007 on train, 0.3099 on test, 0.4776 on the vinta… | 0.3796 | ratio | gini | out_of_time | eq | `[[art:6c5edac7:metrics.out_of_time.gini]]` | verified | 0.3796030172 |
| 167 | outcomes | KS is 0.2262 on train, 0.2375 on test, 0.411 on the vintage… | 0.2262 | ratio | ks | train | eq | `[[art:96e91aee:metrics.train.ks]]` | verified | 0.2261527235 |
| 168 | outcomes | KS is 0.2262 on train, 0.2375 on test, 0.411 on the vintage… | 0.2375 | ratio | ks | test | eq | `[[art:c35222f3:metrics.test.ks]]` | verified | 0.237529396 |
| 169 | outcomes | KS is 0.2262 on train, 0.2375 on test, 0.411 on the vintage… | 0.411 | ratio | ks | vintage_holdout | eq | `[[art:699a7598:metrics.vintage_holdout.ks]]` | verified | 0.4110310226 |
| 170 | outcomes | KS is 0.2262 on train, 0.2375 on test, 0.411 on the vintage… | 0.3021 | ratio | ks | out_of_time | eq | `[[art:c486329f:metrics.out_of_time.ks]]` | verified | 0.3020779889 |
| 171 | outcomes | Brier score is 0.009359 on train, 0.009063 on test, 0.01898… | 0.009359 | ratio | brier | train | eq | `[[art:574cf8a4:metrics.train.brier]]` | verified | 0.009358514597 |
| 172 | outcomes | Brier score is 0.009359 on train, 0.009063 on test, 0.01898… | 0.009063 | ratio | brier | test | eq | `[[art:21d0b581:metrics.test.brier]]` | verified | 0.009062660213 |
| 173 | outcomes | Brier score is 0.009359 on train, 0.009063 on test, 0.01898… | 0.01898 | ratio | brier | vintage_holdout | eq | `[[art:6a660ed9:metrics.vintage_holdout.brier]]` | verified | 0.01897762486 |
| 174 | outcomes | Brier score is 0.009359 on train, 0.009063 on test, 0.01898… | 0.01824 | ratio | brier | out_of_time | eq | `[[art:4ddcaaea:metrics.out_of_time.brier]]` | verified | 0.01823697645 |
| 175 | outcomes | Log loss is 0.05226 on train, 0.05083 on test, 0.09345 on th… | 0.05226 | ratio | logloss | train | eq | `[[art:716b9dc1:metrics.train.logloss]]` | verified | 0.05225625901 |
| 176 | outcomes | Log loss is 0.05226 on train, 0.05083 on test, 0.09345 on th… | 0.05083 | ratio | logloss | test | eq | `[[art:048e9ca7:metrics.test.logloss]]` | verified | 0.0508316292 |
| 177 | outcomes | Log loss is 0.05226 on train, 0.05083 on test, 0.09345 on th… | 0.09345 | ratio | logloss | vintage_holdout | eq | `[[art:630a591b:metrics.vintage_holdout.logloss]]` | verified | 0.09344516111 |
| 178 | outcomes | Log loss is 0.05226 on train, 0.05083 on test, 0.09345 on th… | 0.09576 | ratio | logloss | out_of_time | eq | `[[art:8d53f72c:metrics.out_of_time.logloss]]` | verified | 0.09576249258 |
| 179 | outcomes | The share of events captured in the top two deciles is 0.38… | 0.38 | ratio | top2_capture | train | eq | `[[art:b2f9e5d8:deciles.train.top2_capture]]` | verified | 0.3800067317 |
| 180 | outcomes | The share of events captured in the top two deciles is 0.38… | 0.3769 | ratio | top2_capture | test | eq | `[[art:1d4dff05:deciles.test.top2_capture]]` | verified | 0.3769168684 |
| 181 | outcomes | The share of events captured in the top two deciles is 0.38… | 0.5116 | ratio | top2_capture | vintage_holdout | eq | `[[art:3cd3b5a3:deciles.vintage_holdout.top2_capture]]` | verified | 0.5115740741 |
| 182 | outcomes | The share of events captured in the top two deciles is 0.38… | 0.4313 | ratio | top2_capture | out_of_time | eq | `[[art:58f451c3:deciles.out_of_time.top2_capture]]` | verified | 0.4313243907 |
| 183 | outcomes | Row counts behind these figures are 313538 on train, 135060… | 313538 | count | n | train | eq | `[[art:72c7a6d2:metrics.train.n]]` | verified | 313538 |
| 184 | outcomes | Row counts behind these figures are 313538 on train, 135060… | 135060 | count | n | test | eq | `[[art:629740ff:metrics.test.n]]` | verified | 135060 |
| 185 | outcomes | Row counts behind these figures are 313538 on train, 135060… | 221779 | count | n | vintage_holdout | eq | `[[art:faabc78e:metrics.vintage_holdout.n]]` | verified | 221779 |
| 186 | outcomes | Row counts behind these figures are 313538 on train, 135060… | 283343 | count | n | out_of_time | eq | `[[art:c164ae00:metrics.out_of_time.n]]` | verified | 283343 |
| 187 | outcomes | The train-to-test AUC movement is from 0.6504 to 0.6549 , co… | 0.6504 | ratio | auc | train | eq | `[[art:40964132:metrics.train.auc]]` | verified | 0.6503543409 |
| 188 | outcomes | The train-to-test AUC movement is from 0.6504 to 0.6549 , co… | 0.6549 | ratio | auc | test | eq | `[[art:f3890b65:metrics.test.auc]]` | verified | 0.6549316245 |
| 189 | outcomes | The train-to-test AUC movement is from 0.6504 to 0.6549 , co… | 0.08 | ratio | auc_gap |  | eq | `[[art:630f28f4:threshold.O1.auc_gap]]` | verified | 0.08 |
| 190 | outcomes | Out of time the slice's AUC of 0.6046 falls 0.08523 below th… | 0.6046 | ratio | auc | out_of_time | eq | `[[art:a1a6fd72:metrics.out_of_time.sub.incentive_high.auc]]` | verified | 0.6045716303 |
| 191 | outcomes | Out of time the slice's AUC of 0.6046 falls 0.08523 below th… | 0.08523 | ratio | auc_gap | out_of_time | eq | `[[art:e7b201c8:metrics.out_of_time.sub.incentive_high.auc_gap]]` | verified | 0.08522987832 |
| 192 | outcomes | Out of time the slice's AUC of 0.6046 falls 0.08523 below th… | 0.08 | ratio | auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 193 | outcomes | Out of time the slice's AUC of 0.6046 falls 0.08523 below th… | 0.5 | ratio | share | out_of_time | eq | `[[art:4787f68a:metrics.out_of_time.sub.incentive_high.share]]` | verified | 0.4999982354 |
| 194 | outcomes | Out of time the slice's AUC of 0.6046 falls 0.08523 below th… | 0.1 | ratio | share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 195 | outcomes | Out of time the slice's AUC of 0.6046 falls 0.08523 below th… | 0.95 | ratio | share |  | eq | `[[art:a928a05c:threshold.O1.slice_max_share]]` | verified | 0.95 |
| 196 | outcomes | On the vintage holdout the slice's AUC of 0.6654 falls 0.073… | 0.6654 | ratio | auc | vintage_holdout | eq | `[[art:1d13a424:metrics.vintage_holdout.sub.incentive_high.auc]]` | verified | 0.6653722393 |
| 197 | outcomes | On the vintage holdout the slice's AUC of 0.6654 falls 0.073… | 0.07345 | ratio | auc_gap | vintage_holdout | eq | `[[art:dfc93d01:metrics.vintage_holdout.sub.incentive_high.auc_gap]]` | verified | 0.07344783185 |
| 198 | outcomes | On the vintage holdout the slice's AUC of 0.6654 falls 0.073… | 0.08 | ratio | auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 199 | outcomes | On the vintage holdout the slice's AUC of 0.6654 falls 0.073… | 0.4991 | ratio | share | vintage_holdout | eq | `[[art:6ee6cf53:metrics.vintage_holdout.sub.incentive_high.share]]` | verified | 0.4991365278 |
| 200 | outcomes | Mean predicted here is 0.0188 against an observed rate of 0.… | 0.0188 | ratio | mean_predicted | out_of_time | eq | `[[art:b7288bbc:metrics.out_of_time.sub.incentive_high.mean_predicted]]` | verified | 0.01880179941 |
| 201 | outcomes | Mean predicted here is 0.0188 against an observed rate of 0.… | 0.02949 | ratio | event_rate | out_of_time | eq | `[[art:f62f5a9c:metrics.out_of_time.sub.incentive_high.event_rate]]` | verified | 0.02949086263 |
| 202 | outcomes | Mean predicted here is 0.0188 against an observed rate of 0.… | 0.01662 | ratio | mean_predicted | vintage_holdout | eq | `[[art:1f806ffc:metrics.vintage_holdout.sub.incentive_high.mean_predicted]]` | verified | 0.0166159798 |
| 203 | outcomes | Mean predicted here is 0.0188 against an observed rate of 0.… | 0.03165 | ratio | event_rate | vintage_holdout | eq | `[[art:7a446230:metrics.vintage_holdout.sub.incentive_high.event_rate]]` | verified | 0.03165368841 |
| 204 | outcomes | Out of time the slice's AUC of 0.5198 falls 0.17 below the s… | 0.5198 | ratio | auc | out_of_time | eq | `[[art:5f017449:metrics.out_of_time.sub.incentive_low.auc]]` | verified | 0.5198113489 |
| 205 | outcomes | Out of time the slice's AUC of 0.5198 falls 0.17 below the s… | 0.17 | ratio | auc_gap | out_of_time | eq | `[[art:379c90f9:metrics.out_of_time.sub.incentive_low.auc_gap]]` | verified | 0.1699901597 |
| 206 | outcomes | Out of time the slice's AUC of 0.5198 falls 0.17 below the s… | 0.08 | ratio | auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 207 | outcomes | Out of time the slice's AUC of 0.5198 falls 0.17 below the s… | 0.5 | ratio | share | out_of_time | eq | `[[art:cc116fda:metrics.out_of_time.sub.incentive_low.share]]` | verified | 0.5000017646 |
| 208 | outcomes | Out of time the slice's AUC of 0.5198 falls 0.17 below the s… | 0.1 | ratio | share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 209 | outcomes | On the vintage holdout the slice's AUC of 0.5956 falls 0.143… | 0.5956 | ratio | auc | vintage_holdout | eq | `[[art:e5b67962:metrics.vintage_holdout.sub.incentive_low.auc]]` | verified | 0.595613353 |
| 210 | outcomes | On the vintage holdout the slice's AUC of 0.5956 falls 0.143… | 0.1432 | ratio | auc_gap | vintage_holdout | eq | `[[art:2b9eda62:metrics.vintage_holdout.sub.incentive_low.auc_gap]]` | verified | 0.1432067181 |
| 211 | outcomes | On the vintage holdout the slice's AUC of 0.5956 falls 0.143… | 0.5009 | ratio | share | vintage_holdout | eq | `[[art:4e4aac59:metrics.vintage_holdout.sub.incentive_low.share]]` | verified | 0.5008634722 |
| 212 | outcomes | Mean predicted is 0.001307 against an observed rate of 0.007… | 0.001307 | ratio | mean_predicted | out_of_time | eq | `[[art:e77d973c:metrics.out_of_time.sub.incentive_low.mean_predicted]]` | verified | 0.001306700417 |
| 213 | outcomes | Mean predicted is 0.001307 against an observed rate of 0.007… | 0.00787 | ratio | event_rate | out_of_time | eq | `[[art:b87e9246:metrics.out_of_time.sub.incentive_low.event_rate]]` | verified | 0.007870291942 |
| 214 | outcomes | Mean predicted is 0.001307 against an observed rate of 0.007… | 0.003153 | ratio | mean_predicted | vintage_holdout | eq | `[[art:037a5534:metrics.vintage_holdout.sub.incentive_low.mean_predicted]]` | verified | 0.003152614288 |
| 215 | outcomes | Mean predicted is 0.001307 against an observed rate of 0.007… | 0.007346 | ratio | event_rate | vintage_holdout | eq | `[[art:8cd3a201:metrics.vintage_holdout.sub.incentive_low.event_rate]]` | verified | 0.007345990763 |
| 216 | outcomes | Out of time the slice's AUC of 0.6568 falls 0.03303 below th… | 0.6568 | ratio | auc | out_of_time | eq | `[[art:f9940557:metrics.out_of_time.sub.loan_age_high.auc]]` | verified | 0.6567747134 |
| 217 | outcomes | Out of time the slice's AUC of 0.6568 falls 0.03303 below th… | 0.03303 | ratio | auc_gap | out_of_time | eq | `[[art:3375bb4a:metrics.out_of_time.sub.loan_age_high.auc_gap]]` | verified | 0.03302679515 |
| 218 | outcomes | Out of time the slice's AUC of 0.6568 falls 0.03303 below th… | 0.08 | ratio | auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 219 | outcomes | Out of time the slice's AUC of 0.6568 falls 0.03303 below th… | 0.4977 | ratio | share | out_of_time | eq | `[[art:2ea8628a:metrics.out_of_time.sub.loan_age_high.share]]` | verified | 0.4977359596 |
| 220 | outcomes | Out of time the slice's AUC of 0.6568 falls 0.03303 below th… | 0.1 | ratio | share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 221 | outcomes | On the vintage holdout the slice's AUC of 0.7102 falls 0.028… | 0.7102 | ratio | auc | vintage_holdout | eq | `[[art:c882f305:metrics.vintage_holdout.sub.loan_age_high.auc]]` | verified | 0.7102086289 |
| 222 | outcomes | On the vintage holdout the slice's AUC of 0.7102 falls 0.028… | 0.02861 | ratio | auc_gap | vintage_holdout | eq | `[[art:9ed9d4d1:metrics.vintage_holdout.sub.loan_age_high.auc_gap]]` | verified | 0.02861144217 |
| 223 | outcomes | On the vintage holdout the slice's AUC of 0.7102 falls 0.028… | 0.4975 | ratio | share | vintage_holdout | eq | `[[art:dbe22405:metrics.vintage_holdout.sub.loan_age_high.share]]` | verified | 0.4974997633 |
| 224 | outcomes | Mean predicted is 0.003214 against an observed rate of 0.012… | 0.003214 | ratio | mean_predicted | out_of_time | eq | `[[art:432adcfd:metrics.out_of_time.sub.loan_age_high.mean_predicted]]` | verified | 0.003214253157 |
| 225 | outcomes | Mean predicted is 0.003214 against an observed rate of 0.012… | 0.01229 | ratio | event_rate | out_of_time | eq | `[[art:90f73f7e:metrics.out_of_time.sub.loan_age_high.event_rate]]` | verified | 0.01228816564 |
| 226 | outcomes | Mean predicted is 0.003214 against an observed rate of 0.012… | 0.005655 | ratio | mean_predicted | vintage_holdout | eq | `[[art:037855d3:metrics.vintage_holdout.sub.loan_age_high.mean_predicted]]` | verified | 0.005655264251 |
| 227 | outcomes | Mean predicted is 0.003214 against an observed rate of 0.012… | 0.01157 | ratio | event_rate | vintage_holdout | eq | `[[art:31f03683:metrics.vintage_holdout.sub.loan_age_high.event_rate]]` | verified | 0.0115738433 |
| 228 | outcomes | Out of time the slice's AUC of 0.6665 falls 0.02328 below th… | 0.6665 | ratio | auc | out_of_time | eq | `[[art:b30b38e0:metrics.out_of_time.sub.loan_age_low.auc]]` | verified | 0.6665223131 |
| 229 | outcomes | Out of time the slice's AUC of 0.6665 falls 0.02328 below th… | 0.02328 | ratio | auc_gap | out_of_time | eq | `[[art:3b05548e:metrics.out_of_time.sub.loan_age_low.auc_gap]]` | verified | 0.02327919553 |
| 230 | outcomes | Out of time the slice's AUC of 0.6665 falls 0.02328 below th… | 0.08 | ratio | auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 231 | outcomes | Out of time the slice's AUC of 0.6665 falls 0.02328 below th… | 0.5023 | ratio | share | out_of_time | eq | `[[art:50f06738:metrics.out_of_time.sub.loan_age_low.share]]` | verified | 0.5022640404 |
| 232 | outcomes | Out of time the slice's AUC of 0.6665 falls 0.02328 below th… | 0.1 | ratio | share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 233 | outcomes | On the vintage holdout the slice's AUC of 0.7112 falls 0.027… | 0.7112 | ratio | auc | vintage_holdout | eq | `[[art:9e59bba3:metrics.vintage_holdout.sub.loan_age_low.auc]]` | verified | 0.7111696947 |
| 234 | outcomes | On the vintage holdout the slice's AUC of 0.7112 falls 0.027… | 0.02765 | ratio | auc_gap | vintage_holdout | eq | `[[art:69340c92:metrics.vintage_holdout.sub.loan_age_low.auc_gap]]` | verified | 0.02765037637 |
| 235 | outcomes | On the vintage holdout the slice's AUC of 0.7112 falls 0.027… | 0.5025 | ratio | share | vintage_holdout | eq | `[[art:38c62cb8:metrics.vintage_holdout.sub.loan_age_low.share]]` | verified | 0.5025002367 |
| 236 | outcomes | Mean predicted is 0.01683 against an observed rate of 0.0250… | 0.01683 | ratio | mean_predicted | out_of_time | eq | `[[art:e2794584:metrics.out_of_time.sub.loan_age_low.mean_predicted]]` | verified | 0.01683252031 |
| 237 | outcomes | Mean predicted is 0.01683 against an observed rate of 0.0250… | 0.02502 | ratio | event_rate | out_of_time | eq | `[[art:f5c47c9d:metrics.out_of_time.sub.loan_age_low.event_rate]]` | verified | 0.02501528321 |
| 238 | outcomes | Mean predicted is 0.01683 against an observed rate of 0.0250… | 0.01405 | ratio | mean_predicted | vintage_holdout | eq | `[[art:4e34fc22:metrics.vintage_holdout.sub.loan_age_low.mean_predicted]]` | verified | 0.01404811114 |
| 239 | outcomes | Mean predicted is 0.01683 against an observed rate of 0.0250… | 0.02731 | ratio | event_rate | vintage_holdout | eq | `[[art:1b4716c7:metrics.vintage_holdout.sub.loan_age_low.event_rate]]` | verified | 0.02730519364 |
| 240 | sensitivity | The largest variance inflation factor across the retained fe… | 4.629 | ratio | vif | train | eq | `[[art:82a187c7:vif.max]]` | verified | 4.628790677 |
| 241 | sensitivity | The largest variance inflation factor across the retained fe… | 10 | ratio | vif |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 242 | sensitivity | That maximum belongs to the refinance incentive term at 4.62… | 4.629 | ratio | vif | train | eq | `[[art:0c33ec65:vif.incentive]]` | verified | 4.628790677 |
| 243 | sensitivity | That maximum belongs to the refinance incentive term at 4.62… | 3.749 | ratio | vif | train | eq | `[[art:f9a490a7:vif.burnout]]` | verified | 3.748625457 |
| 244 | sensitivity | That maximum belongs to the refinance incentive term at 4.62… | 3.015 | ratio | vif | train | eq | `[[art:42163c15:vif.sato]]` | verified | 3.014708865 |
| 245 | sensitivity | That maximum belongs to the refinance incentive term at 4.62… | 2.69 | ratio | vif | train | eq | `[[art:12ee5768:vif.loan_age]]` | verified | 2.689839788 |
| 246 | sensitivity | That maximum belongs to the refinance incentive term at 4.62… | 2.205 | ratio | vif | train | eq | `[[art:7f4d0c73:vif.rate_change_12m]]` | verified | 2.204676098 |
| 247 | sensitivity | The remaining retained features sit close to unity, with ori… | 1.107 | ratio | vif | train | eq | `[[art:a998810f:vif.orig_ltv]]` | verified | 1.106875268 |
| 248 | sensitivity | The remaining retained features sit close to unity, with ori… | 1.025 | ratio | vif | train | eq | `[[art:6afd05c9:vif.season_sin]]` | verified | 1.024602455 |
| 249 | sensitivity | The remaining retained features sit close to unity, with ori… | 1.023 | ratio | vif | train | eq | `[[art:373087f2:vif.credit_score]]` | verified | 1.022563505 |
| 250 | sensitivity | The remaining retained features sit close to unity, with ori… | 1.061 | ratio | vif | train | eq | `[[art:0dde7942:vif.orig_upb_log]]` | verified | 1.060864995 |
| 251 | sensitivity | The remaining retained features sit close to unity, with ori… | 1.006 | ratio | vif | train | eq | `[[art:2950847c:vif.season_cos]]` | verified | 1.005586044 |
| 252 | sensitivity | Belsley's condition number of the column-standardised design… | 4.565 | ratio | condition_number | train | eq | `[[art:87b61976:condition_number]]` | verified | 4.565343746 |
| 253 | sensitivity | Belsley's condition number of the column-standardised design… | 30 | ratio | condition_number |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 254 | sensitivity | The tolerance against which the across-regime difference in… | 0.1 | ratio | auc_gap |  | eq | `[[art:b64213d7:threshold.R1.auc_gap]]` | verified | 0.1 |
| 255 | sensitivity | No feature among the top ten changes sign across regimes und… | 0.05 | ratio | sign_flip_coef |  | eq | `[[art:aca84377:threshold.R1.sign_flip_coef]]` | verified | 0.05 |
| 256 | sensitivity | No feature among the top ten changes sign across regimes und… | 2 | ratio | sign_flip_z |  | eq | `[[art:2e4428c7:threshold.R1.sign_flip_z]]` | verified | 2 |
| 257 | sensitivity | The flip indicator stands at 0 for the refinance incentive,… | 0 | ratio | sign_flip |  | eq | `[[art:0cc7a37d:stability.incentive.sign_flip]]` | verified | 0 |
| 258 | sensitivity | The flip indicator stands at 0 for the refinance incentive,… | 0 | ratio | sign_flip |  | eq | `[[art:6bc05e82:stability.burnout.sign_flip]]` | verified | 0 |
| 259 | sensitivity | The flip indicator stands at 0 for the refinance incentive,… | 0 | ratio | sign_flip |  | eq | `[[art:1f302ccd:stability.sato.sign_flip]]` | verified | 0 |
| 260 | sensitivity | The flip indicator stands at 0 for the refinance incentive,… | 0 | ratio | sign_flip |  | eq | `[[art:b7191217:stability.loan_age.sign_flip]]` | verified | 0 |
| 261 | sensitivity | The flip indicator stands at 0 for the refinance incentive,… | 0 | ratio | sign_flip |  | eq | `[[art:465700ff:stability.rate_change_12m.sign_flip]]` | verified | 0 |
| 262 | sensitivity | The flip indicator stands at 0 for the refinance incentive,… | 0 | ratio | sign_flip |  | eq | `[[art:d956c276:stability.credit_score.sign_flip]]` | verified | 0 |
| 263 | sensitivity | The flip indicator stands at 0 for the refinance incentive,… | 0 | ratio | sign_flip |  | eq | `[[art:054d5fab:stability.orig_ltv.sign_flip]]` | verified | 0 |
| 264 | sensitivity | The flip indicator stands at 0 for the refinance incentive,… | 0 | ratio | sign_flip |  | eq | `[[art:fb1ae6c8:stability.orig_upb_log.sign_flip]]` | verified | 0 |
| 265 | sensitivity | The flip indicator stands at 0 for the refinance incentive,… | 0 | ratio | sign_flip |  | eq | `[[art:1850e2de:stability.season_cos.sign_flip]]` | verified | 0 |
| 266 | sensitivity | The flip indicator stands at 0 for the refinance incentive,… | 0 | ratio | sign_flip |  | eq | `[[art:6ba36a3b:stability.season_sin.sign_flip]]` | verified | 0 |
| 267 | sensitivity | At the downward extreme the change in servicing value is -10… | -1078000 | currency | value_change |  | eq | `[[art:9bab8e73:scenario.value_change.-300]]` | verified | -1077724.403 |
| 268 | sensitivity | At the downward extreme the change in servicing value is -10… | 167100 | currency | value_change |  | eq | `[[art:d7f60dfe:scenario.value_change.300]]` | verified | 167117.0554 |
| 269 | sensitivity | The convexity measure, which sums the change at the downward… | -910600 | currency | convexity |  | eq | `[[art:67b742b1:scenario.convexity]]` | verified | -910607.3477 |
| 270 | findings | The calibration slope on the out-of-time split is 0.4321 , w… | 0.4321 | ratio | calibration_slope | out_of_time | eq | `[[art:d9f87bb2:calibration_slope.out_of_time]]` | verified | 0.432125782 |
| 271 | findings | The calibration slope on the out-of-time split is 0.4321 , w… | 0.8 | ratio | calibration_slope |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 272 | findings | On the out-of-time split the mean predicted probability is 0… | 0.01005 | ratio | mean_predicted | out_of_time | eq | `[[art:fd777cc4:metrics.out_of_time.mean_predicted]]` | verified | 0.01005421904 |
| 273 | findings | On the out-of-time split the mean predicted probability is 0… | 0.01868 | ratio | event_rate | out_of_time | eq | `[[art:cf3a82aa:metrics.out_of_time.event_rate]]` | verified | 0.01868053913 |
| 274 | findings | On the out-of-time split the mean predicted probability is 0… | 0.4618 | ratio | mean_rel_gap | out_of_time | eq | `[[art:9e4c8750:calibration.mean_rel_gap.out_of_time]]` | verified | 0.4617811099 |
| 275 | findings | On the out-of-time split the mean predicted probability is 0… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 276 | findings | On the vintage holdout the mean predicted probability is 0.0… | 0.009873 | ratio | mean_predicted | vintage_holdout | eq | `[[art:c12c52f7:metrics.vintage_holdout.mean_predicted]]` | verified | 0.009872671801 |
| 277 | findings | On the vintage holdout the mean predicted probability is 0.0… | 0.01948 | ratio | event_rate | vintage_holdout | eq | `[[art:bab66615:metrics.vintage_holdout.event_rate]]` | verified | 0.01947885057 |
| 278 | findings | On the vintage holdout the mean predicted probability is 0.0… | 0.4932 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:92b5a8c4:calibration.mean_rel_gap.vintage_holdout]]` | verified | 0.4931594261 |
| 279 | findings | On the vintage holdout the mean predicted probability is 0.0… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 280 | findings | On the out-of-time split the segment `incentive > median(inc… | 0.6046 | ratio | auc | out_of_time | eq | `[[art:a1a6fd72:metrics.out_of_time.sub.incentive_high.auc]]` | verified | 0.6045716303 |
| 281 | findings | On the out-of-time split the segment `incentive > median(inc… | 0.08523 | ratio | auc_gap | out_of_time | eq | `[[art:e7b201c8:metrics.out_of_time.sub.incentive_high.auc_gap]]` | verified | 0.08522987832 |
| 282 | findings | On the out-of-time split the segment `incentive > median(inc… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 283 | findings | On the out-of-time split the segment `incentive > median(inc… | 0.5 | ratio | share | out_of_time | eq | `[[art:4787f68a:metrics.out_of_time.sub.incentive_high.share]]` | verified | 0.4999982354 |
| 284 | findings | In the complementary segment `incentive <= median(incentive)… | 0.5198 | ratio | auc | out_of_time | eq | `[[art:5f017449:metrics.out_of_time.sub.incentive_low.auc]]` | verified | 0.5198113489 |
| 285 | findings | In the complementary segment `incentive <= median(incentive)… | 0.17 | ratio | auc_gap | out_of_time | eq | `[[art:379c90f9:metrics.out_of_time.sub.incentive_low.auc_gap]]` | verified | 0.1699901597 |
| 286 | findings | In the complementary segment `incentive <= median(incentive)… | 0.5956 | ratio | auc | vintage_holdout | eq | `[[art:e5b67962:metrics.vintage_holdout.sub.incentive_low.auc]]` | verified | 0.595613353 |
| 287 | findings | In the complementary segment `incentive <= median(incentive)… | 0.1432 | ratio | auc_gap | vintage_holdout | eq | `[[art:2b9eda62:metrics.vintage_holdout.sub.incentive_low.auc_gap]]` | verified | 0.1432067181 |
| 288 | findings | In the complementary segment `incentive <= median(incentive)… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 289 | findings | In the complementary segment `incentive <= median(incentive)… | 0.5 | ratio | share | out_of_time | eq | `[[art:cc116fda:metrics.out_of_time.sub.incentive_low.share]]` | verified | 0.5000017646 |
| 290 | findings | In the complementary segment `incentive <= median(incentive)… | 0.5009 | ratio | share | vintage_holdout | eq | `[[art:4e4aac59:metrics.vintage_holdout.sub.incentive_low.share]]` | verified | 0.5008634722 |
| 291 | monitoring | - Calibration slope of the outcome on the logit of the predi… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 292 | monitoring | - Calibration slope of the outcome on the logit of the predi… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 293 | monitoring | - Calibration slope of the outcome on the logit of the predi… | 1.017 | ratio | calibration_slope | test | eq | `[[art:9b1edaa3:calibration_slope.test]]` | verified | 1.01683551 |
| 294 | monitoring | - Discrimination, measured as area under the ROC curve on ea… | 0.65 | ratio | auc | test | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 295 | monitoring | - Discrimination, measured as area under the ROC curve on ea… | 0.6549 | ratio | auc | test | eq | `[[art:f3890b65:metrics.test.auc]]` | verified | 0.6549316245 |
| 296 | monitoring | - Population stability of the model inputs and of the score… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 297 | monitoring | - Population stability of the model inputs and of the score… | 0.005703 | ratio | psi |  | eq | `[[art:f632d5d4:psi.max]]` | verified | 0.005703237396 |

## Appendix B — Artifact index

The store holds 364 artifacts; the 238 this report cites or rests a finding on are indexed here.

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
| `metrics.out_of_time.sub.loan_age_high` | `fb175459` | table | table, 9 rows | every metric on the loan_age above_median slice of out_of_time |
| `metrics.out_of_time.sub.loan_age_high.auc` | `f9940557` | scalar | 0.6567747134 | auc on the loan_age above_median slice of out_of_time |
| `metrics.out_of_time.sub.loan_age_high.auc_gap` | `3375bb4a` | scalar | 0.03302679515 | how far AUC on the loan_age above_median slice of out_of_time falls below AUC on all of out_of_time |
| `metrics.out_of_time.sub.loan_age_high.event_rate` | `90f73f7e` | scalar | 0.01228816564 | event_rate on the loan_age above_median slice of out_of_time |
| `metrics.out_of_time.sub.loan_age_high.mean_predicted` | `432adcfd` | scalar | 0.003214253157 | mean_predicted on the loan_age above_median slice of out_of_time |
| `metrics.out_of_time.sub.loan_age_high.share` | `2ea8628a` | scalar | 0.4977359596 | the share of out_of_time the loan_age above_median slice holds |
| `metrics.out_of_time.sub.loan_age_low` | `5ab8bfd3` | table | table, 9 rows | every metric on the loan_age below_median slice of out_of_time |
| `metrics.out_of_time.sub.loan_age_low.auc` | `b30b38e0` | scalar | 0.6665223131 | auc on the loan_age below_median slice of out_of_time |
| `metrics.out_of_time.sub.loan_age_low.auc_gap` | `3b05548e` | scalar | 0.02327919553 | how far AUC on the loan_age below_median slice of out_of_time falls below AUC on all of out_of_time |
| `metrics.out_of_time.sub.loan_age_low.event_rate` | `f5c47c9d` | scalar | 0.02501528321 | event_rate on the loan_age below_median slice of out_of_time |
| `metrics.out_of_time.sub.loan_age_low.mean_predicted` | `e2794584` | scalar | 0.01683252031 | mean_predicted on the loan_age below_median slice of out_of_time |
| `metrics.out_of_time.sub.loan_age_low.share` | `50f06738` | scalar | 0.5022640404 | the share of out_of_time the loan_age below_median slice holds |
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
| `metrics.vintage_holdout.sub.incentive_high.auc` | `1d13a424` | scalar | 0.6653722393 | auc on the incentive above_median slice of vintage_holdout |
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
| `metrics.vintage_holdout.sub.loan_age_high` | `501301d6` | table | table, 9 rows | every metric on the loan_age above_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.loan_age_high.auc` | `c882f305` | scalar | 0.7102086289 | auc on the loan_age above_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.loan_age_high.auc_gap` | `9ed9d4d1` | scalar | 0.02861144217 | how far AUC on the loan_age above_median slice of vintage_holdout falls below AUC on all of vintage_holdout |
| `metrics.vintage_holdout.sub.loan_age_high.event_rate` | `31f03683` | scalar | 0.0115738433 | event_rate on the loan_age above_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.loan_age_high.mean_predicted` | `037855d3` | scalar | 0.005655264251 | mean_predicted on the loan_age above_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.loan_age_high.share` | `dbe22405` | scalar | 0.4974997633 | the share of vintage_holdout the loan_age above_median slice holds |
| `metrics.vintage_holdout.sub.loan_age_low` | `a4b42f76` | table | table, 9 rows | every metric on the loan_age below_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.loan_age_low.auc` | `9e59bba3` | scalar | 0.7111696947 | auc on the loan_age below_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.loan_age_low.auc_gap` | `69340c92` | scalar | 0.02765037637 | how far AUC on the loan_age below_median slice of vintage_holdout falls below AUC on all of vintage_holdout |
| `metrics.vintage_holdout.sub.loan_age_low.event_rate` | `1b4716c7` | scalar | 0.02730519364 | event_rate on the loan_age below_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.loan_age_low.mean_predicted` | `4e34fc22` | scalar | 0.01404811114 | mean_predicted on the loan_age below_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.loan_age_low.share` | `38c62cb8` | scalar | 0.5025002367 | the share of vintage_holdout the loan_age below_median slice holds |
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
| `sign_check.incentive.agrees` | `f7b2338e` | scalar | 1 | 1 when the fitted sign on incentive agrees with its univariate direction, 0 when it does not |
| `sign_check.n_disagreements` | `e223cd4a` | scalar | 3 | retained features whose fitted sign contradicts their univariate direction, of 9 checked |
| `sign_check.orig_ltv.coef_sign` | `7eec65ec` | scalar | -1 | the sign of the fitted coefficient on orig_ltv |
| `sign_check.orig_ltv.univariate_direction` | `85aabf06` | scalar | 1 | the sign of orig_ltv's own single-feature AUC on train minus 0.5 |
| `sign_check.orig_upb_log.agrees` | `07a9d3e6` | scalar | 1 | 1 when the fitted sign on orig_upb_log agrees with its univariate direction, 0 when it does not |
| `sign_check.sato.coef_sign` | `265915cf` | scalar | -1 | the sign of the fitted coefficient on sato |
| `sign_check.sato.univariate_direction` | `c08233a6` | scalar | 1 | the sign of sato's own single-feature AUC on train minus 0.5 |
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
| LLM calls | 21 (plan 4, draft 8, reask 1, extract 8) |
| re-asks | 1 |
| repair rounds | 1 |
| tokens in / out | 333,584 / 122,054 |
| notional cost (USD) | 6.4858 |
| wall-clock (s) | 1373.77 |
| subject run (s) | 9.92 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | msr_prepayment-full_agent-20260917T044453Z-e98677a9 |
| data manifest | verified: 5 file(s) against package.yaml (see data.manifest) |

## Appendix D — Not checked

| item | reason |
|---|---|
| developer documentation | package has no `docs/` directory |
