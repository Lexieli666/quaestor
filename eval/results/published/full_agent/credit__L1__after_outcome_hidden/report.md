---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: full_agent
model: claude-opus-5[1m]
run_id: credit_default-full_agent-20260920T071109Z-e2e51e00
data_mode: synthetic
synthetic_n: 5000
grounding_precision_pre: 0.9963
grounding_precision_post: 1.0000
n_claims: 270
n_findings_by_severity: {high: 1, medium: 1, low: 0, info: 0}
generated: "2026-09-20T07:11:09Z"
illustrative: false
---

# Validation report — `credit_default` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `credit_default` v1.0 | `full_agent` | claude-opus-5[1m] | synthetic, n = 5000 | 0.9963 → 1.0000 | 1 / 1 / 0 / 0 |
<!-- quaestor:renderer:end -->

The subject of this validation is the model package credit_default version 1.0, a binary classification model that predicts the probability that an account defaults, and this report follows the structure of the Federal Reserve's model risk management guidance on model validation and monitoring [[reg:SR26-2:V]].

The assessment here is an outcomes-analysis review: model output recomputed from the subject's own predictions is compared against realised outcomes and against the thresholds the developer declared in the package manifest [[reg:SR26-2:V.1.b]].
The subject was run under the wall-clock cap of 300 seconds [[art:2ad8d1a5:runtime.max_seconds]] that its manifest declares, and every metric quoted below was recomputed by the validator rather than taken from the developer's own report.
The fit split holds 3500 rows [[art:2510d49d:profile.train.n]] and the held-out split holds 1500 rows [[art:2193cf5f:profile.test.n]].

Discrimination on the held-out split reaches an AUC of 0.9755 [[art:8f522f3b:metrics.test.auc]], above the declared floor of 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]].
The Brier score on the held-out split is 0.04247 [[art:d4f27e13:metrics.test.brier]], below the declared ceiling of 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]].
The largest train-to-test population stability index, score included, is 0.01789 [[art:1b87de3e:psi.max]], below the declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
The calibration slope on the held-out split is 1.197 [[art:c9a03fe6:calibration_slope.test]], above the declared floor of 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] and below the declared ceiling of 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]], leaving it inside the declared band but close to its upper edge.
On that reading, the subject meets each threshold its developer declared.

This validation published F-001, a L1 leakage finding at high severity, and F-002, a C1 calibration finding at medium severity.
Each is set out in full, with its evidence and its recommended disposition, in the findings section of this report.

## 2. Conceptual soundness

Assessing conceptual soundness means assessing and documenting the model's design, construction, and developmental testing, and subjecting the modelling choices to critical analysis of both the quality and the extent of the developmental evidence [[reg:SR26-2:V.1.a]].

### Design and feature timing

The champion is a coefficient-based scoring model: each retained feature enters linearly through a fitted coefficient, over an intercept of -6.103 [[art:e4b3fd0e:run.model_summary#intercept]], estimated on 3500 [[art:e4b3fd0e:run.model_summary#n_train]] training rows.
The subject's feature specification carries 13 [[art:b85c116d:run.features#n]] features in total.
Of those, 2 [[art:b85c116d:run.features#at_origination]] are declared known at origination and 11 [[art:b85c116d:run.features#before_period_start]] are declared known before the performance period begins.
The specification declares 0 [[art:b85c116d:run.features#during_period]] features known only during the performance period and 0 [[art:b85c116d:run.features#after_outcome]] known only after the outcome is observed, so on the subject's own declaration no input postdates the moment the score would be used.
That declaration is an assertion by the developer about timing rather than a measurement of it, and the naming of pay_amt_next, which reads as a forward-looking payment quantity, is the place where a reviewer should want to see the timing evidence behind the declaration.

The subject's own collinearity screen removed two features before fitting.
It removed bill_last, whose variance inflation factor was 162.9 [[art:e4b3fd0e:run.model_summary#removed.bill_last.vif]], and utilisation_mean_6m, at 36.78 [[art:e4b3fd0e:run.model_summary#removed.utilisation_mean_6m.vif]], both above the screen's cut-off of 10 [[art:e4b3fd0e:run.model_summary#vif_threshold]].
Both removals are defensible on their face: a last bill and a six-month mean utilisation are close restatements of the six-month bill mean and the point-in-time utilisation that were kept, so the screen dropped the redundant member of each pair rather than the more general one.

### Coefficients and expected signs

The largest coefficient in magnitude is the -12.37 [[art:e4b3fd0e:run.model_summary#coefficients.pay_amt_next.value]] on pay_amt_next, far larger in magnitude than any other coefficient in the fit.
The next largest are 1.651 [[art:e4b3fd0e:run.model_summary#coefficients.bill_mean_6m.value]] on bill_mean_6m, 0.9159 [[art:e4b3fd0e:run.model_summary#coefficients.delinq_last.value]] on delinq_last, 0.8591 [[art:e4b3fd0e:run.model_summary#coefficients.utilisation.value]] on utilisation, 0.7072 [[art:e4b3fd0e:run.model_summary#coefficients.pay_ratio_mean_6m.value]] on pay_ratio_mean_6m and 0.4311 [[art:e4b3fd0e:run.model_summary#coefficients.limit_bal.value]] on limit_bal.
The smaller terms are 0.2086 [[art:e4b3fd0e:run.model_summary#coefficients.pay_ratio_last.value]] on pay_ratio_last, 0.1993 [[art:e4b3fd0e:run.model_summary#coefficients.bill_trend_6m.value]] on bill_trend_6m, 0.1073 [[art:e4b3fd0e:run.model_summary#coefficients.delinq_count_6m.value]] on delinq_count_6m, -0.09998 [[art:e4b3fd0e:run.model_summary#coefficients.delinq_max_6m.value]] on delinq_max_6m and -0.08872 [[art:e4b3fd0e:run.model_summary#coefficients.age.value]] on age.

Against subject-matter expectation, several of these signs are what a credit reviewer would predict.
Utilisation raises the fitted odds of default and a recent delinquency raises them, which is the direction lending experience expects, and a larger upcoming payment lowers them, which is also the expected direction.
Three signs run against the usual expectation: a higher credit limit raising the fitted odds of default, a higher mean payment ratio raising them, and a worse six-month maximum delinquency lowering them are each the opposite of what the underlying credit story would suggest in isolation.
In a fit with correlated balance, payment and delinquency measures, signs of this kind are commonly the result of one term conditioning on another rather than a statement about the feature's own relationship with default, which is what the sign evidence below is for.

### Sign evidence against univariate direction

The count of retained features whose fitted sign contradicts the direction of their own single-feature relationship with the outcome on train is 6 [[art:75159a84:sign_check.n_disagreements]].
The fitted sign on limit_bal is 1 [[art:6af6aef2:sign_check.limit_bal.coef_sign]] while its own univariate direction is -1 [[art:56d284d6:sign_check.limit_bal.univariate_direction]], and refitting the champion's form without it moves test discrimination by 0.0006175 [[art:4b976d60:ablation.limit_bal.delta_auc]], so the model is not leaning on the feature the disagreement sits on.
The fitted sign on pay_ratio_mean_6m is 1 [[art:8547787e:sign_check.pay_ratio_mean_6m.coef_sign]] against a univariate direction of -1 [[art:24dcef24:sign_check.pay_ratio_mean_6m.univariate_direction]], and dropping it changes test discrimination by -0.0009594 [[art:54c168fb:ablation.pay_ratio_mean_6m.delta_auc]].
The fitted sign on pay_ratio_last is 1 [[art:f018263e:sign_check.pay_ratio_last.coef_sign]] against a univariate direction of -1 [[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]], and dropping it changes test discrimination by 0.0001863 [[art:c577925a:ablation.pay_ratio_last.delta_auc]].
The fitted sign on bill_mean_6m is 1 [[art:a457c04a:sign_check.bill_mean_6m.coef_sign]] against a univariate direction of -1 [[art:23b89c5d:sign_check.bill_mean_6m.univariate_direction]], and dropping it changes test discrimination by -0.005228 [[art:a4586b58:ablation.bill_mean_6m.delta_auc]], the largest such movement among the disagreeing features.
The fitted sign on bill_trend_6m is 1 [[art:abd4aaba:sign_check.bill_trend_6m.coef_sign]] against a univariate direction of -1 [[art:a9bff389:sign_check.bill_trend_6m.univariate_direction]], and dropping it changes test discrimination by -0.0005537 [[art:54e6a418:ablation.bill_trend_6m.delta_auc]].
The fitted sign on delinq_max_6m is -1 [[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]] against a univariate direction of 1 [[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]], and dropping it changes test discrimination by 0.0001607 [[art:b1793491:ablation.delinq_max_6m.delta_auc]].
Taken together, every disagreement sits on a feature whose removal moves test discrimination only slightly, and two of them are removals after which the refit scores marginally higher rather than lower.
That pattern is consistent with the signs being artefacts of correlation among the retained balance, payment and delinquency measures rather than evidence that the model's treatment of any one of these drivers is doing material work in the wrong direction.

The features whose fitted signs agree with their univariate directions include utilisation, at 1 [[art:85badc3c:sign_check.utilisation.coef_sign]] and 1 [[art:f0995196:sign_check.utilisation.univariate_direction]], delinq_last, at 1 [[art:50d352f8:sign_check.delinq_last.coef_sign]] and 1 [[art:a78648ba:sign_check.delinq_last.univariate_direction]], delinq_count_6m, at 1 [[art:17afb6f9:sign_check.delinq_count_6m.coef_sign]] and 1 [[art:549e904e:sign_check.delinq_count_6m.univariate_direction]], age, at -1 [[art:6172eb93:sign_check.age.coef_sign]] and -1 [[art:66364583:sign_check.age.univariate_direction]], and pay_amt_next, at -1 [[art:6fc540c1:sign_check.pay_amt_next.coef_sign]] and -1 [[art:1bec400a:sign_check.pay_amt_next.univariate_direction]].

### Where the discrimination sits

Refitting the champion's functional form on every retained feature scores 0.9755 [[art:8e58476a:ablation.baseline_auc]] on test, the level from which each ablation is measured, and this coincides with the champion's recomputed test discrimination of 0.9755 [[art:8f522f3b:metrics.test.auc]].
Removing pay_amt_next moves test discrimination by -0.2275 [[art:cf6c0563:ablation.pay_amt_next.delta_auc]], far the largest movement of any single removal.
Every other removal moves it by a small amount in either direction, the next largest being the -0.005228 [[art:a4586b58:ablation.bill_mean_6m.delta_auc]] on bill_mean_6m, then -0.0009594 [[art:54c168fb:ablation.pay_ratio_mean_6m.delta_auc]] on pay_ratio_mean_6m, -0.0009211 [[art:43d4225a:ablation.delinq_last.delta_auc]] on delinq_last and -0.0004235 [[art:009bc4f1:ablation.utilisation.delta_auc]] on utilisation.
Removing age moves it by 5.613e-05 [[art:786b509d:ablation.age.delta_auc]] and removing delinq_count_6m by 5.103e-06 [[art:3730f6e2:ablation.delinq_count_6m.delta_auc]], both in the direction of a slightly better refit.
The design implication for conceptual soundness is that the champion's discrimination rests on one feature, with the rest of the specification contributing little once that feature is present, and a design that concentrates its power this way inherits whatever timing and availability risk attaches to that single input.

### Effective challenge

The challenger scores 0.9877 [[art:d2646bc7:challenger.auc]] on test against the champion's 0.9755 [[art:8f522f3b:metrics.test.auc]], a lead of 0.01222 [[art:2ab4af27:challenger.delta_auc]] in the challenger's favour.
The threshold that decides whether such a lead matters is 0.03 [[art:e042774c:threshold.E1.delta_auc]], and the observed lead is below it.
On calibration the challenger's Brier score is 0.02542 [[art:0a224a0a:challenger.brier]] against the champion's 0.04247 [[art:d4f27e13:metrics.test.brier]], so the challenger is the better of the two on that measure as well, comparing the two levels directly rather than their ratio.
The direction of both comparisons favours the challenger, but on the declared threshold the discrimination gap is not large enough to displace the champion on benchmarking grounds alone.
The more useful conclusion from the challenge is qualitative: a benchmark of a different form reaching a similar level of discrimination on the same data reinforces that the discrimination available here is driven by the data rather than by the champion's particular functional form.

## 3. Data integrity and drift

Model testing includes a critical assessment of data quality, relevance, and inputs, and this section reviews the input data of the package against the bounds declared for it [[reg:SR26-2:IV.1]].

### Missingness

The training split holds 3500 [[art:2510d49d:profile.train.n]] rows and the test split holds 1500 [[art:2193cf5f:profile.test.n]] rows.
The largest missing fraction over the columns of the training split is 0 [[art:050a3099:profile.train.missing.max]].
The largest missing fraction over the columns of the test split is 0 [[art:f813848d:profile.test.missing.max]].
Comparing the two splits by difference, the two worst-column figures are equal, so the between-split gap cannot reach the declared bound of 0.1 [[art:9cce25ea:threshold.D1.missing_gap]]; comparing them by ratio is not meaningful when both sit at the floor.
No column in either split is degraded by absent values, so nothing in the missingness screen qualifies the results that follow.

### Population and characteristic stability

The largest train-to-test population shift over all features and the score is 0.01789 [[art:1b87de3e:psi.max]], well below the declared stability bound of 0.25 [[art:278b9016:threshold.S1.psi]], which matches the bound declared in the package manifest at 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
That largest shift is carried by `pay_amt_next` at 0.01789 [[art:996bb509:psi.pay_amt_next]].
The score itself shifts by 0.01199 [[art:05f120d2:psi.y_score]], also far below the declared bound.
The remaining per-feature population shifts between the training split and the test split are:

- `age` at 0.008124 [[art:f9255a0a:psi.age]]
- `bill_mean_6m` at 0.007124 [[art:028e4281:psi.bill_mean_6m]]
- `bill_trend_6m` at 0.00958 [[art:c247a6f2:psi.bill_trend_6m]]
- `delinq_count_6m` at 0.002069 [[art:61491d02:psi.delinq_count_6m]]
- `delinq_last` at 0.00285 [[art:03bd52e7:psi.delinq_last]]
- `delinq_max_6m` at 0.005498 [[art:7a82e7f3:psi.delinq_max_6m]]
- `limit_bal` at 0.01095 [[art:601cdba2:psi.limit_bal]]
- `pay_ratio_last` at 0.004966 [[art:3af2ca29:psi.pay_ratio_last]]
- `pay_ratio_mean_6m` at 0.0055 [[art:2c5baeb2:psi.pay_ratio_mean_6m]]
- `utilisation` at 0.004244 [[art:451e0780:psi.utilisation]]

Every one of these sits below the declared bound of 0.25 [[art:278b9016:threshold.S1.psi]], and the marginal distributions of the two splits are therefore close on this measure.

The characteristic stability picture is not as uniform.
The largest contribution to the shift in the linear predictor is 0.4064 [[art:3f7f79cf:csi.max]], carried by `pay_amt_next` at 0.4064 [[art:e708fa25:csi.pay_amt_next]].
The next largest contribution belongs to `delinq_last` at 0.0295 [[art:cd29d613:csi.delinq_last]], and the remaining features contribute:

- `age` at 0.00125 [[art:584faff4:csi.age]]
- `bill_mean_6m` at 0.0105 [[art:f374dbd7:csi.bill_mean_6m]]
- `bill_trend_6m` at 0.00567 [[art:8bb46253:csi.bill_trend_6m]]
- `delinq_count_6m` at 0.002143 [[art:4564aa47:csi.delinq_count_6m]]
- `delinq_max_6m` at 0.002782 [[art:2fe28db6:csi.delinq_max_6m]]
- `limit_bal` at 0.007188 [[art:cb617a64:csi.limit_bal]]
- `pay_ratio_last` at 0.003912 [[art:c083b28c:csi.pay_ratio_last]]
- `pay_ratio_mean_6m` at 0.003519 [[art:8f1dbe89:csi.pay_ratio_mean_6m]]
- `utilisation` at 0.01304 [[art:b1f362df:csi.utilisation]]

The contribution of `pay_amt_next` stands above every other feature's contribution by a wide margin on both the difference and the ratio, and it is the same feature that carries the largest marginal population shift.
A feature whose marginal distribution barely moves yet dominates the movement of the linear predictor is one whose weight in the score, not whose distribution, drives the result, and the validator reads this alongside the leakage evidence below.

### Leakage and contamination screens

The count of features declared as observed during the performance period or after the outcome is 0 [[art:742bcd24:leakage.timing.n_flagged]], so the declared timings raise no concern on their own.
The count of feature names matching the target-adjacent lexicon is 0 [[art:407e62be:leakage.name_screen.n_matched]], so the name screen is clean.

The strongest single feature reaches an AUC of 0.945 [[art:5b5e98c2:leakage.target_corr.max_single_feature_auc]] against the declared single-feature bound of 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]].
That value is above the bound, and it is `pay_amt_next` that attains it, the same feature that dominates the characteristic stability decomposition.
This is finding L1, raised at high severity: a single predictor that separates the outcome this sharply on its own is the signature of information that would not have been available at scoring time, and the timing and name screens above are not sufficient to rule that out, because neither inspects the values.

The contamination screen has two arms, each read against its own bound.
The share of test rows whose identifiers also identify a row of the training split is 0 [[art:63d37fc5:leakage.overlap.ids]], against the declared overlap bound of 0.005 [[art:9f336eaf:threshold.L2.overlap]], and so the identifier arm passes.
The share of test rows whose feature values also appear in the training split is 0 [[art:0fec8048:leakage.overlap.features]], against the bound the feature-overlap rule actually applied, 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]], and so the feature-vector arm passes.
That effective bound is the larger of the declared overlap bound and an allowance derived from the rate of non-unique rows inside the training split, on the reasoning that two different subjects writing the same discrete row is coincidence rather than contamination; here the share of training rows whose feature values are not unique within the training split is 0 [[art:4474c227:leakage.duplicates.train]], and the applied bound and the declared bound coincide.
The row-level overlap between the splits is likewise 0 [[art:4c9fcd09:leakage.overlap]], read against the same effective bound of 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].

### Assessment

Missingness, population stability and the contamination screens all sit inside the bounds declared for them, and the two splits are drawn from populations that are close on every distributional measure reviewed here.
The single-feature discrimination screen is the exception, and finding L1 records it.
The concentration of the characteristic stability decomposition in the same feature that triggers that screen is consistent with it, and the validator recommends that the provenance and observation timing of `pay_amt_next` be established from the source system before the performance results elsewhere in this report are relied on.

## 4. Outcomes analysis

Outcomes analysis compares model outputs to the corresponding real-world outcomes to assess model performance relative to model objectives and business use [[reg:SR26-2:V.1.b]].

This section reports discrimination first and calibration after it.
The reason is the observed event rate on the evaluation split, 0.2247 [[art:9209d200:metrics.test.event_rate]], which sits at or above 0.05 [[art:42f1351e:rule.calibration_first_event_rate]], the rate below which this report would lead with calibration instead.

### Discrimination

The recomputed metrics on each split are set out below, one row per metric.

| metric | train | test |
| --- | --- | --- |
| observations | 3500 [[art:564683ee:metrics.train.n]] | 1500 [[art:64fcf14d:metrics.test.n]] |
| observed event rate | 0.2246 [[art:133a5ff8:metrics.train.event_rate]] | 0.2247 [[art:9209d200:metrics.test.event_rate]] |
| AUC | 0.9812 [[art:da2cd01d:metrics.train.auc]] | 0.9755 [[art:8f522f3b:metrics.test.auc]] |
| Gini | 0.9624 [[art:23cb4057:metrics.train.gini]] | 0.951 [[art:f927e3cd:metrics.test.gini]] |
| KS | 0.8895 [[art:7a126f15:metrics.train.ks]] | 0.8784 [[art:81bee194:metrics.test.ks]] |
| Brier | 0.03817 [[art:959b3159:metrics.train.brier]] | 0.04247 [[art:d4f27e13:metrics.test.brier]] |
| log loss | 0.1505 [[art:417d98d9:metrics.train.logloss]] | 0.167 [[art:aa620b5e:metrics.test.logloss]] |
| mean predicted probability | 0.2246 [[art:1fa024a6:metrics.train.mean_predicted]] | 0.233 [[art:0b9b6a1e:metrics.test.mean_predicted]] |

Rank ordering by decile of predicted probability on the evaluation split is set out in the table that follows.

<!-- quaestor:renderer:begin table deciles.test -->
Decile separation on test; decile 1 holds the highest probabilities [[art:ffdb3017:deciles.test]]:

| decile | count | events | event_rate | lift |
|---|---|---|---|---|
| 1 | 150 | 145 | 0.9667 | 4.303 |
| 2 | 150 | 132 | 0.88 | 3.917 |
| 3 | 150 | 44 | 0.2933 | 1.306 |
| 4 | 150 | 10 | 0.06667 | 0.2967 |
| 5 | 150 | 2 | 0.01333 | 0.05935 |
| 6 | 150 | 0 | 0 | 0 |
| 7 | 150 | 0 | 0 | 0 |
| 8 | 150 | 4 | 0.02667 | 0.1187 |
| 9 | 150 | 0 | 0 | 0 |
| 10 | 150 | 0 | 0 | 0 |
<!-- quaestor:renderer:end -->

The share of evaluation-split events captured in the highest deciles of predicted probability is 0.822 [[art:5690757b:deciles.test.top2_capture]], against 0.8422 [[art:55242963:deciles.train.top2_capture]] on the development split, the larger of the two.

Discrimination is higher on the development split, 0.9812 [[art:da2cd01d:metrics.train.auc]], than on the evaluation split, 0.9755 [[art:8f522f3b:metrics.test.auc]], and that pair was read against the train-to-test AUC bound of 0.08 [[art:630f28f4:threshold.O1.auc_gap]].
The candidate list for this section carries no item raised on that bound.

### Calibration

The logistic regression of the outcome on the logit of the predicted probability gives a slope of 1.197 [[art:c9a03fe6:calibration_slope.test]] on the evaluation split and 1.383 [[art:45dafd11:calibration_slope.train]] on the development split.
The declared band runs from 0.8 [[art:749634ae:threshold.C1.calibration_slope.min]] to 1.2 [[art:b6672579:threshold.C1.calibration_slope.max]], and the evaluation-split slope sits inside it while the development-split slope sits above its top; the latter is the calibration finding carried by this report.
The corresponding intercepts are -0.0558 [[art:56745cf2:calibration_intercept.test]] on the evaluation split and 0.2246 [[art:d556f341:calibration_intercept.train]] on the development split.

On the evaluation split the mean predicted probability is 0.233 [[art:0b9b6a1e:metrics.test.mean_predicted]] against an observed rate of 0.2247 [[art:9209d200:metrics.test.event_rate]], predictions standing above outcomes in level.
That separation expressed relative to the observed rate is 0.03717 [[art:6a845d81:calibration.mean_rel_gap.test]], below the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
On the development split the mean predicted probability is 0.2246 [[art:1fa024a6:metrics.train.mean_predicted]] against an observed rate of 0.2246 [[art:133a5ff8:metrics.train.event_rate]], with a relative separation of 8.632e-05 [[art:f7447f34:calibration.mean_rel_gap.train]], also below that tolerance.
Calibration by decile of predicted probability on the evaluation split is set out below.

<!-- quaestor:renderer:begin table calibration.test -->
Calibration by decile of predicted probability on test [[art:1744d380:calibration.test]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 1.335e-08 | 0 | 150 |
| 2 | 1.357e-05 | 0 | 150 |
| 3 | 0.0005755 | 0.02667 | 150 |
| 4 | 0.005974 | 0 | 150 |
| 5 | 0.02678 | 0 | 150 |
| 6 | 0.06532 | 0.01333 | 150 |
| 7 | 0.1319 | 0.06667 | 150 |
| 8 | 0.3384 | 0.2933 | 150 |
| 9 | 0.7901 | 0.88 | 150 |
| 10 | 0.971 | 0.9667 | 150 |
<!-- quaestor:renderer:end -->

### Developer-declared thresholds

<!-- quaestor:renderer:begin table thresholds.evaluation -->
Every threshold package.yaml declares, with its bound, the recomputed value and the outcome [[art:f41614b5:thresholds.evaluation]]:

| metric | split | bound | value | result |
|---|---|---|---|---|
| auc | test | minimum 0.7 | 0.9755 | pass |
| brier | test | maximum 0.2 | 0.04247 | pass |
| calibration_slope | test | minimum 0.8 | 1.197 | pass |
| calibration_slope | test | maximum 1.2 | 1.197 | pass |
| psi |  | maximum 0.25 | 0.01789 | pass |
<!-- quaestor:renderer:end -->

The rows are the bounds the model package declares, each placed beside the value recomputed in this run and the outcome of that comparison.
Because the table is assembled from the same recomputed values reported above, it states the outcome of each declared bound without restating it in prose.

### Follow-up analyses

**`pay_amt_next <= median(pay_amt_next)`**

The planning loop asked for every metric to be recomputed on the sub-population where this feature sits at or below its median, on both splits, to test whether discrimination and the development-split calibration slope survive once the near-perfectly predictive leakage-suspect feature is restricted to the lower part of its range, separating a single-feature effect from genuine signal.

<!-- quaestor:renderer:begin table metrics.train.sub.pay_amt_next_low -->
Every metric on the pay_amt_next below_median slice of train [[art:51a4a15f:metrics.train.sub.pay_amt_next_low]]:

| metric | value |
|---|---|
| n | 1750 |
| event_rate | 0.432 |
| auc | 0.978 |
| gini | 0.956 |
| ks | 0.8618 |
| brier | 0.06186 |
| logloss | 0.2255 |
| mean_predicted | 0.4288 |
| mean_rel_gap | 0.007435 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.pay_amt_next_low -->
Every metric on the pay_amt_next below_median slice of test [[art:369588e4:metrics.test.sub.pay_amt_next_low]]:

| metric | value |
|---|---|
| n | 750 |
| event_rate | 0.424 |
| auc | 0.9667 |
| gini | 0.9335 |
| ks | 0.8528 |
| brier | 0.06877 |
| logloss | 0.2517 |
| mean_predicted | 0.4452 |
| mean_rel_gap | 0.04997 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

On the evaluation split this sub-population's AUC falls below the split's own by 0.008772 [[art:cd5172fc:metrics.test.sub.pay_amt_next_low.auc_gap]], within the slice bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]], and it holds 0.5 [[art:18eac95f:metrics.test.sub.pay_amt_next_low.share]] of the split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] at which a sub-population may raise an open item.
On the development split the same sub-population falls below that split's own AUC by 0.003167 [[art:4b2a3b88:metrics.train.sub.pay_amt_next_low.auc_gap]], also within that bound, on 0.5 [[art:01d5682e:metrics.train.sub.pay_amt_next_low.share]] of the split.
Mean predicted against observed reads 0.4452 [[art:036756aa:metrics.test.sub.pay_amt_next_low.mean_predicted]] against 0.424 [[art:c5cd207d:metrics.test.sub.pay_amt_next_low.event_rate]] on the evaluation split, a relative separation of 0.04997 [[art:a89da41c:metrics.test.sub.pay_amt_next_low.mean_rel_gap]], and 0.4288 [[art:9ebffd6f:metrics.train.sub.pay_amt_next_low.mean_predicted]] against 0.432 [[art:20cb26cd:metrics.train.sub.pay_amt_next_low.event_rate]] on the development split, a relative separation of 0.007435 [[art:3afbd6e4:metrics.train.sub.pay_amt_next_low.mean_rel_gap]].
Ordering therefore holds up on this sub-population, and what departure there is sits in the level of the probabilities rather than in their ordering.

**`pay_amt_next > median(pay_amt_next)`**

The loop then asked for the same recomputation on the complementary sub-population, completing the partition so that the leakage-suspect feature's effect on discrimination and on the calibration slope can be read on the upper part of its range as well.

<!-- quaestor:renderer:begin table metrics.train.sub.pay_amt_next_high -->
Every metric on the pay_amt_next above_median slice of train [[art:ad425b34:metrics.train.sub.pay_amt_next_high]]:

| metric | value |
|---|---|
| n | 1750 |
| event_rate | 0.01714 |
| auc | 0.8745 |
| gini | 0.749 |
| ks | 0.6672 |
| brier | 0.01448 |
| logloss | 0.07543 |
| mean_predicted | 0.02032 |
| mean_rel_gap | 0.1851 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.pay_amt_next_high -->
Every metric on the pay_amt_next above_median slice of test [[art:c78a69bf:metrics.test.sub.pay_amt_next_high]]:

| metric | value |
|---|---|
| n | 750 |
| event_rate | 0.02533 |
| auc | 0.8821 |
| gini | 0.7641 |
| ks | 0.7498 |
| brier | 0.01618 |
| logloss | 0.08232 |
| mean_predicted | 0.02085 |
| mean_rel_gap | 0.177 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

On the evaluation split this sub-population's AUC is 0.8821 [[art:e2b8b0f2:metrics.test.sub.pay_amt_next_high.auc]] and falls below the split's own by 0.09344 [[art:ad693cad:metrics.test.sub.pay_amt_next_high.auc_gap]], above the slice bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]], on 0.5 [[art:21c17ed0:metrics.test.sub.pay_amt_next_high.share]] of the split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].
On the development split it falls below that split's own AUC by 0.1067 [[art:30718a8b:metrics.train.sub.pay_amt_next_high.auc_gap]], also above that bound, on 0.5 [[art:c4cc28b1:metrics.train.sub.pay_amt_next_high.share]] of the split.
That excess over the slice bound is not among the candidates this section may describe, and it is left to the findings section as an open item for the model developer.
Mean predicted against observed reads 0.02085 [[art:dcacb7a5:metrics.test.sub.pay_amt_next_high.mean_predicted]] against 0.02533 [[art:9702492a:metrics.test.sub.pay_amt_next_high.event_rate]] on the evaluation split, a relative separation of 0.177 [[art:5a35c2f9:metrics.test.sub.pay_amt_next_high.mean_rel_gap]], below the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]], and 0.02032 [[art:968cddfe:metrics.train.sub.pay_amt_next_high.mean_predicted]] against 0.01714 [[art:81517b8d:metrics.train.sub.pay_amt_next_high.event_rate]] on the development split, a relative separation of 0.1851 [[art:2d65d0bd:metrics.train.sub.pay_amt_next_high.mean_rel_gap]], also below that tolerance.
Here the level of the probabilities stays inside its tolerance while the ordering does not stay inside its bound, so the weakness on this sub-population is in the ordering rather than the level.

**`limit_bal <= median(limit_bal)`**

The loop asked for every metric on the sub-population where the credit limit sits at or below its median, on both splits, to test whether the development-split calibration-slope excursion concentrates in the lower-limit part of the book rather than running uniformly across it.

<!-- quaestor:renderer:begin table metrics.train.sub.limit_bal_low -->
Every metric on the limit_bal below_median slice of train [[art:81d20ff9:metrics.train.sub.limit_bal_low]]:

| metric | value |
|---|---|
| n | 1763 |
| event_rate | 0.2439 |
| auc | 0.9723 |
| gini | 0.9446 |
| ks | 0.8534 |
| brier | 0.05257 |
| logloss | 0.1924 |
| mean_predicted | 0.2458 |
| mean_rel_gap | 0.007657 |
| share | 0.5037 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.limit_bal_low -->
Every metric on the limit_bal below_median slice of test [[art:668296df:metrics.test.sub.limit_bal_low]]:

| metric | value |
|---|---|
| n | 756 |
| event_rate | 0.2487 |
| auc | 0.967 |
| gini | 0.9339 |
| ks | 0.8339 |
| brier | 0.05755 |
| logloss | 0.2074 |
| mean_predicted | 0.2585 |
| mean_rel_gap | 0.03933 |
| share | 0.504 |
<!-- quaestor:renderer:end -->

On the evaluation split this sub-population's AUC falls below the split's own by 0.008535 [[art:6990b76c:metrics.test.sub.limit_bal_low.auc_gap]], within the slice bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]], on 0.504 [[art:bac689cc:metrics.test.sub.limit_bal_low.share]] of the split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].
On the development split it falls below that split's own AUC by 0.008866 [[art:999aab9c:metrics.train.sub.limit_bal_low.auc_gap]], also within that bound, on 0.5037 [[art:45c51f9e:metrics.train.sub.limit_bal_low.share]] of the split.
Mean predicted against observed reads 0.2585 [[art:c1a37d64:metrics.test.sub.limit_bal_low.mean_predicted]] against 0.2487 [[art:de78adb5:metrics.test.sub.limit_bal_low.event_rate]] on the evaluation split, a relative separation of 0.03933 [[art:2b29e325:metrics.test.sub.limit_bal_low.mean_rel_gap]], and 0.2458 [[art:2086a25d:metrics.train.sub.limit_bal_low.mean_predicted]] against 0.2439 [[art:0ae85aa6:metrics.train.sub.limit_bal_low.event_rate]] on the development split, a relative separation of 0.007657 [[art:a93d065e:metrics.train.sub.limit_bal_low.mean_rel_gap]].
Ordering on this sub-population stays within its bound, so what movement there is sits in the level of the probabilities.

**`limit_bal > median(limit_bal)`**

The loop completed the credit-limit partition with the same recomputation on the upper-limit sub-population, so that the calibration-slope drift could be attributed to one part of the book or shown to run across both.

<!-- quaestor:renderer:begin table metrics.train.sub.limit_bal_high -->
Every metric on the limit_bal above_median slice of train [[art:1d76466a:metrics.train.sub.limit_bal_high]]:

| metric | value |
|---|---|
| n | 1737 |
| event_rate | 0.205 |
| auc | 0.9876 |
| gini | 0.9752 |
| ks | 0.9297 |
| brier | 0.02355 |
| logloss | 0.1079 |
| mean_predicted | 0.203 |
| mean_rel_gap | 0.00944 |
| share | 0.4963 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.limit_bal_high -->
Every metric on the limit_bal above_median slice of test [[art:be320de3:metrics.test.sub.limit_bal_high]]:

| metric | value |
|---|---|
| n | 744 |
| event_rate | 0.2003 |
| auc | 0.9814 |
| gini | 0.9627 |
| ks | 0.9261 |
| brier | 0.02716 |
| logloss | 0.126 |
| mean_predicted | 0.2072 |
| mean_rel_gap | 0.03445 |
| share | 0.496 |
<!-- quaestor:renderer:end -->

On the evaluation split this sub-population's AUC gap against the split's own is -0.00586 [[art:e37bc8d6:metrics.test.sub.limit_bal_high.auc_gap]], that is, it orders above the split as a whole and so sits within the slice bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]], on 0.496 [[art:ac383ccb:metrics.test.sub.limit_bal_high.share]] of the split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].
On the development split the corresponding gap is -0.006442 [[art:52a49712:metrics.train.sub.limit_bal_high.auc_gap]], likewise above the split's own AUC and within that bound, on 0.4963 [[art:2de2a90a:metrics.train.sub.limit_bal_high.share]] of the split.
Mean predicted against observed reads 0.2072 [[art:f80c93c0:metrics.test.sub.limit_bal_high.mean_predicted]] against 0.2003 [[art:5e9aab40:metrics.test.sub.limit_bal_high.event_rate]] on the evaluation split, a relative separation of 0.03445 [[art:679e4d84:metrics.test.sub.limit_bal_high.mean_rel_gap]], and 0.203 [[art:b1995539:metrics.train.sub.limit_bal_high.mean_predicted]] against 0.205 [[art:9de459ef:metrics.train.sub.limit_bal_high.event_rate]] on the development split, a relative separation of 0.00944 [[art:58ae0f50:metrics.train.sub.limit_bal_high.mean_rel_gap]].
Both credit-limit sub-populations order within the slice bound and both keep their level separations below the calibration tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]], so the development-split slope excursion does not read as a failure of ordering confined to either part of the book.

## 5. Sensitivity and scenario analysis

Sensitivity work in this section supports the assessment of conceptual soundness, which covers key modelling choices, assumptions, and the quality and extent of developmental evidence [[reg:SR26-2:V.1.a]].

The superseded guidance is explicit on the purpose of this testing in a way the revision does not spell out: sensitivity analysis checks the impact of small changes in inputs and parameter values on model outputs, and unexpectedly large output changes in response to small input changes indicate an unstable model [[reg:SR11-7:V.1.a]].

The largest variance inflation factor across the retained features is 8.181 [[art:4afdc4f1:vif.max]], which sits below the declared threshold of 10 [[art:aeb4f33c:threshold.M1.vif]].

That largest value belongs to the six-month mean bill balance, at 8.181 [[art:d5ab7306:vif.bill_mean_6m]].

The next values down are the six-month mean payment ratio at 7.526 [[art:000b6208:vif.pay_ratio_mean_6m]], the most recent payment ratio at 7.268 [[art:bec24796:vif.pay_ratio_last]], and the credit limit at 4.81 [[art:8209ea46:vif.limit_bal]], each below the same threshold.

The remaining retained features fall further below it: utilisation at 3.215 [[art:ec978947:vif.utilisation]], the six-month delinquency count at 2.561 [[art:87890613:vif.delinq_count_6m]], the six-month maximum delinquency at 2.408 [[art:4b239ec5:vif.delinq_max_6m]], the next scheduled payment amount at 2.206 [[art:68806d80:vif.pay_amt_next]], the most recent delinquency at 1.422 [[art:c18221d4:vif.delinq_last]], the six-month bill trend at 1.225 [[art:0cb3df89:vif.bill_trend_6m]], and age at 1.002 [[art:8021b06e:vif.age]].

Belsley's condition number of the column-standardised design is 6.185 [[art:36392379:condition_number]], below the declared threshold of 30 [[art:7e52fd7a:threshold.M1.condition_number]].

On both of the multicollinearity measures the design therefore stays on the passing side of its declared threshold, and the condition number is the further of the two from its limit relative to the spread of the feature-level values.

The margin is nonetheless narrowest for the three balance- and payment-ratio features named above, which are mutually related by construction; if those features are reworked or new ones of the same family are added, the variance inflation factors should be recomputed before the design is relied upon.

The measures above are computed on the training design, so they describe the conditioning of the estimation sample rather than the conditioning of any later population.

Two of the analyses named in the section scope do not apply to this model and are listed in Appendix D on that basis rather than as exercises that were carried out.

Stability across declared regimes is one of them: the subject is not partitioned by a declared regime column, so there is no regime-to-regime comparison of the sensitivity measures to report here.

The rate-shock scenarios are the other: the subject is a binary default classifier rather than a hazard model, so there is no shocked-value change at the extremes, no shock-response curve whose monotonicity could be assessed, and no convexity to compare against a declared direction.

Neither omission should be read as a shock-response curve that behaved well, and neither should be read as a regime comparison that showed stability; the analyses are outside the model type's scope.

No result reported in this section is carried as a finding.

## 6. Findings and recommendations

Findings below are ordered by severity, highest first, and each carries the recomputed quantity, the declared bound it was read against, and the evidence the check drew on, so that the source and extent of the model risk it represents can be judged and corrective action considered [[reg:SR26-2:V]].

### F-001 · L1 leakage · severity **high**

**One input feature separates the outcome on its own at a strength the leakage rule treats as contamination of the target rather than as legitimate predictive signal.**

The strongest single feature, `pay_amt_next`, reaches an AUC of 0.945 [[art:5b5e98c2:leakage.target_corr.max_single_feature_auc]] by itself, above the bound of 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]] that any one feature may reach.

The declared-timing evidence flags 0 [[art:742bcd24:leakage.timing.n_flagged]] features as observed during or after the outcome period, so the declared timing of the inputs does not on its own explain a separation of this size.

<!-- quaestor:renderer:begin table leakage.target_corr -->
Each feature against the outcome on train, on its own [[art:12cb4333:leakage.target_corr]]:

| feature | abs_corr | single_feature_auc | numeric |
|---|---|---|---|
| limit_bal | 0.0536 | 0.5417 | true |
| age | 0.01687 | 0.5073 | true |
| utilisation | 0.02702 | 0.5134 | true |
| pay_ratio_last | 0.07687 | 0.5525 | true |
| pay_ratio_mean_6m | 0.09208 | 0.5614 | true |
| delinq_last | 0.3585 | 0.6831 | true |
| delinq_count_6m | 0.2158 | 0.6369 | true |
| delinq_max_6m | 0.1832 | 0.6221 | true |
| bill_mean_6m | 0.03389 | 0.524 | true |
| bill_trend_6m | 0.03665 | 0.5058 | true |
| pay_amt_next | 0.346 | 0.945 | true |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table leakage.timing -->
Each feature's declared timing; flagged means during or after the outcome [[art:878d82fa:leakage.timing]]:

| feature | timing | flagged |
|---|---|---|
| limit_bal | at_origination | false |
| age | at_origination | false |
| utilisation | before_period_start | false |
| utilisation_mean_6m | before_period_start | false |
| pay_ratio_last | before_period_start | false |
| pay_ratio_mean_6m | before_period_start | false |
| delinq_last | before_period_start | false |
| delinq_count_6m | before_period_start | false |
| delinq_max_6m | before_period_start | false |
| bill_mean_6m | before_period_start | false |
| bill_last | before_period_start | false |
| bill_trend_6m | before_period_start | false |
| pay_amt_next | before_period_start | false |
<!-- quaestor:renderer:end -->

The validator concludes that the headline discrimination of 0.9755 [[art:8f522f3b:metrics.test.auc]] on test cannot be read as evidence of genuine predictive power while a feature of this strength sits in the design matrix, because the feature's name and its univariate strength together point to information about the payment that the outcome itself is defined on.

The developer should establish, from the source system and the observation window, the point in time at which `pay_amt_next` becomes known relative to the outcome date, and either restate its timing with support or drop the feature and refit, reporting the performance of the refitted model.

### F-002 · C1 calibration · severity **medium**

**The fitted probabilities are miscalibrated on the training split: the outcome moves with the logit of the prediction more steeply than the accepted band allows.**

The logistic regression of the outcome on the logit of the predicted probability gives a slope on train of 1.383 [[art:45dafd11:calibration_slope.train]], above the top of the accepted band at 1.2 [[art:b6672579:threshold.C1.calibration_slope.max]].

<!-- quaestor:renderer:begin table calibration.train -->
Calibration by decile of predicted probability on train [[art:309e30bb:calibration.train]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 2.708e-09 | 0 | 350 |
| 2 | 1.404e-05 | 0.005714 | 350 |
| 3 | 0.0005028 | 0.005714 | 350 |
| 4 | 0.004695 | 0.008571 | 350 |
| 5 | 0.02105 | 0.01143 | 350 |
| 6 | 0.05843 | 0.01714 | 350 |
| 7 | 0.119 | 0.02571 | 350 |
| 8 | 0.3153 | 0.28 | 350 |
| 9 | 0.755 | 0.9 | 350 |
| 10 | 0.9716 | 0.9914 | 350 |
<!-- quaestor:renderer:end -->

The validator concludes that the scores are under-dispersed relative to the realised outcome on the split the model was fitted on, so the predicted probabilities are not usable as levels for pricing, provisioning or cut-off setting until they are corrected, even where the ranking they induce is retained.

The developer should recalibrate the scores, report the slope of the recalibrated scores on a split held out from the calibration fit, and state which downstream uses depend on the probability level rather than on the rank.

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1, S1), `compute_metrics` (T1, O1), `check_leakage` (L2), `check_collinearity` (M1), `challenger_compare` (E1).

### Open items

On test the sub-population `pay_amt_next > median(pay_amt_next)` scores an AUC of 0.8821 [[art:e2b8b0f2:metrics.test.sub.pay_amt_next_high.auc]] against 0.9755 [[art:8f522f3b:metrics.test.auc]] on all of test, a difference of 0.09344 [[art:ad693cad:metrics.test.sub.pay_amt_next_high.auc_gap]] read against a bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] on a slice holding 0.5 [[art:21c17ed0:metrics.test.sub.pay_amt_next_high.share]] of the split, at or above the minimum share of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]]: what does the model developer understand the model to be discriminating on inside a segment selected on that payment amount, where that feature and whatever is correlated with it are held to one side of their median?

On train the same sub-population `pay_amt_next > median(pay_amt_next)` scores an AUC of 0.8745 [[art:649333b3:metrics.train.sub.pay_amt_next_high.auc]] against 0.9812 [[art:da2cd01d:metrics.train.auc]] on all of train, a difference of 0.1067 [[art:30718a8b:metrics.train.sub.pay_amt_next_high.auc_gap]] read against the same bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] on a slice holding 0.5 [[art:c4cc28b1:metrics.train.sub.pay_amt_next_high.share]] of the split, at or above the minimum share of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]]: comparing the two splits as differences and not as ratios, the train difference is the larger of the two, and what does the model developer take that ordering to say about how much of the whole-split separation rests on the very feature the slice is defined by?

The fitted coefficient on `bill_mean_6m` carries sign 1 [[art:a457c04a:sign_check.bill_mean_6m.coef_sign]] where that feature's own univariate direction on train is -1 [[art:23b89c5d:sign_check.bill_mean_6m.univariate_direction]], and the agreement flag read against that univariate direction is 0 [[art:4df8b747:sign_check.bill_mean_6m.agrees]]: what does the model developer expect this coefficient to be carrying once the other features are conditioned on, given that conditioning on one feature also conditions on everything correlated with it?

The fitted coefficient on `bill_trend_6m` carries sign 1 [[art:abd4aaba:sign_check.bill_trend_6m.coef_sign]] where that feature's own univariate direction on train is -1 [[art:a9bff389:sign_check.bill_trend_6m.univariate_direction]], and the agreement flag read against that univariate direction is 0 [[art:c0f6d07d:sign_check.bill_trend_6m.agrees]]: can the model developer state the business reading of the conditional direction and say whether it is the intended one?

The fitted coefficient on `delinq_max_6m` carries sign -1 [[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]] where that feature's own univariate direction on train is 1 [[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]], and the agreement flag read against that univariate direction is 0 [[art:c946359c:sign_check.delinq_max_6m.agrees]]: what does the model developer understand to be absorbing the delinquency signal such that, holding the rest of the inputs fixed, worse delinquency history moves the score the other way?

The fitted coefficient on `limit_bal` carries sign 1 [[art:6af6aef2:sign_check.limit_bal.coef_sign]] where that feature's own univariate direction on train is -1 [[art:56d284d6:sign_check.limit_bal.univariate_direction]], and the agreement flag read against that univariate direction is 0 [[art:0278aad1:sign_check.limit_bal.agrees]]: how does the model developer read the conditional direction on credit limit once exposure and payment behaviour are already in the model?

The fitted coefficient on `pay_ratio_last` carries sign 1 [[art:f018263e:sign_check.pay_ratio_last.coef_sign]] where that feature's own univariate direction on train is -1 [[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]], and the agreement flag read against that univariate direction is 0 [[art:79abee77:sign_check.pay_ratio_last.agrees]]: can the model developer say what the conditional direction on the most recent payment ratio represents when the longer-run payment features are held fixed?

The fitted coefficient on `pay_ratio_mean_6m` carries sign 1 [[art:8547787e:sign_check.pay_ratio_mean_6m.coef_sign]] where that feature's own univariate direction on train is -1 [[art:24dcef24:sign_check.pay_ratio_mean_6m.univariate_direction]], and the agreement flag read against that univariate direction is 0 [[art:51914c14:sign_check.pay_ratio_mean_6m.agrees]]: what does the model developer expect the six-month payment ratio to be standing in for alongside the other payment and balance features, and is that reading one the users of the model would accept?

## 7. Ongoing monitoring recommendations

Ongoing monitoring evaluates the extent to which the model continues to perform as expected given changes in products, exposures, activities, clients, data relevance, or market conditions, and the frequency and scope of monitoring reports depend on the nature of the model and its materiality [[reg:SR26-2:V.2]].
The recommendations below reuse the bounds the validation checks already applied, so that a production reading is comparable to the reading recorded here rather than to a newly invented target.

### Quantities, cadence, and bounds

Discrimination on each scored production vintage should be tracked against the declared floor of 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]], with the evaluation-split reading of 0.9755 [[art:8f522f3b:metrics.test.auc]] serving as the reference level that a deteriorating vintage would be expected to fall away from.
Because discrimination can only be scored once outcomes are observed, this reading should be produced each time a vintage's performance window closes, at a cadence matched to that window rather than to the reporting calendar.
Probability accuracy should be tracked against the declared ceiling of 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]], with the evaluation-split reading of 0.04247 [[art:d4f27e13:metrics.test.brier]] as the reference level, on the same outcome-driven cadence.
Calibration should be tracked against the declared band whose lower bound is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] and whose upper bound is 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
This quantity warrants the closest watch of the three, because the evaluation-split reading of 1.197 [[art:c9a03fe6:calibration_slope.test]] sits inside the band but near its upper bound, so a small drift in the same direction would carry it outside.
An escalation trigger set inside the band, rather than at it, is therefore the sensible control for this quantity.
Input and score stability should be tracked against the declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]], with the train-to-test reading of 0.01789 [[art:1b87de3e:psi.max]] as the reference level.
Stability does not depend on realized outcomes, so it should be recomputed at every scoring refresh and reported on the regular monitoring cycle, well ahead of the outcome-dependent quantities.
The stability reading carried here compares the development split to the evaluation split; monitoring should recompute the same quantity from the development distribution to each production vintage, which is the comparison that matters for drift in live use and the one a held-out split cannot supply.

### Ordering of a future monitoring report

Section 4 of this report reported discrimination before calibration, because the observed event rate on the evaluation split is at or above the ordering bound of 0.05 [[art:42f1351e:rule.calibration_first_event_rate]].
If a future production cohort has an observed event rate below that same bound of 0.05 [[art:42f1351e:rule.calibration_first_event_rate]], the monitoring report for that cohort should lead with calibration instead, so that the ordering rule is applied to the cohort in hand rather than inherited from this one.
The cohort event rate should therefore be recorded in each monitoring report alongside the performance quantities, since it determines that ordering.

### Benchmarking

Monitoring adds a comparison the development data cannot give, and the comparison recommended here is against the challenger refitted on production vintages, not against the challenger as fitted in this validation.
Section 2 of this report compares the champion with a challenger fitted on the development data, so the open question monitoring answers is whether the champion's advantage survives when the alternative is re-estimated on data drawn after deployment.
Benchmarking is the comparison of a model's inputs and outputs to estimates from alternative internal or external data or models, and discrepancies should trigger investigation into the sources and degree of the differences rather than being read directly as model error [[reg:SR11-7:V.1.b]].
A close match between the refitted challenger and the champion is evidence in favour of the champion, but it should be read with caution, since the benchmark is itself an alternative prediction [[reg:SR11-7:V.1.b]].

### What monitoring should watch that this validation could not

This validation was conducted on development and evaluation splits drawn from the same period, so it speaks to performance under the conditions represented in that data and not to performance under conditions that arise after deployment.
Monitoring should therefore carry the out-of-time comparison of model forecasts to realized outcomes on cohorts scored in production, which is the test this validation's held-out split does not substitute for [[reg:SR11-7:V.1.c]].
Monitoring should track overrides of model output, the reasons given for them, and how overridden cases subsequently perform, since a high override rate or an override process that consistently improves on the model indicates the model needs revision [[reg:SR11-7:V.1.b]].
Monitoring should also cover process verification in the production environment: that input feeds remain accurate, complete, and consistent with the model's intended use, and that the deployed scoring code matches the reviewed artifact under change control [[reg:SR11-7:V.1.b]].
Sub-population stability over time should be tracked as production volumes accumulate, since the mix of a production vintage can move even while the aggregate stability reading stays inside its declared ceiling.
Where performance deviates meaningfully from expectations on any of these, the response should be considered in terms of overlays, adjustment, recalibration, or redevelopment under the organization's model risk policy [[reg:SR26-2:V.2]].

## Appendix A — Claims

Grounding precision 0.9963 before repair (269 of 270 claims verified; 1 dangling) and 1.0000 after 1 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 12/12; conceptual_soundness 65/65; data_integrity 44/44; outcomes 87/87; sensitivity 15/15; findings 36/36; monitoring 11/11.

Repairs:

| section | before | after | instruction to the drafter |
|---|---|---|---|
| findings | 1 (dangling) | 1 (verified) | ⟪art:abdaaba:sign_check.bill_trend_6m.coef_sign⟫ quotes 'abdaaba', which is shorter than the 8 characters a citation carries; 'sign_check.bill_trend_6m.coef_sign' is abd4aaba -- the token is quoted as ⟪…⟫ and not in its double brackets because this is a diagnostic about a citation and not a citation: a report that printed it as it was written would be refused for carrying a token that is not a well-formed citation |

Developer claims: The package declares 2 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). See Appendix D.

Excluded numeric tokens (not claims): section_number (Section 4, Section 2); citation_hash (2ad8d1a5, 2510d49d, 2193cf5f, 8f522f3b); regulatory_section_id (SR26-2:V, SR26-2:V.1.b, SR26-2:V.1.a, SR26-2:IV.1); finding_id (F-001, F-002); package_version (1.0); extractor_returned_excluded_token (1.0, 001,, 002,, 2.0).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The subject was run under the wall-clock cap of 300 seconds… | 300 | ratio | runtime.max_seconds |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 2 | summary | The fit split holds 3500 rows and the held-out split holds 1… | 3500 | count | profile.n | train | eq | `[[art:2510d49d:profile.train.n]]` | verified | 3500 |
| 3 | summary | The fit split holds 3500 rows and the held-out split holds 1… | 1500 | count | profile.n | test | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 4 | summary | Discrimination on the held-out split reaches an AUC of 0.975… | 0.9755 | ratio | auc | test | eq | `[[art:8f522f3b:metrics.test.auc]]` | verified | 0.9755058926 |
| 5 | summary | Discrimination on the held-out split reaches an AUC of 0.975… | 0.7 | ratio | auc | test | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 6 | summary | The Brier score on the held-out split is 0.04247 , below the… | 0.04247 | ratio | brier | test | eq | `[[art:d4f27e13:metrics.test.brier]]` | verified | 0.04247487168 |
| 7 | summary | The Brier score on the held-out split is 0.04247 , below the… | 0.2 | ratio | brier | test | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 8 | summary | The largest train-to-test population stability index, score… | 0.01789 | ratio | psi |  | eq | `[[art:1b87de3e:psi.max]]` | verified | 0.01789488592 |
| 9 | summary | The largest train-to-test population stability index, score… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 10 | summary | The calibration slope on the held-out split is 1.197 , above… | 1.197 | ratio | calibration_slope | test | eq | `[[art:c9a03fe6:calibration_slope.test]]` | verified | 1.19744242 |
| 11 | summary | The calibration slope on the held-out split is 1.197 , above… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 12 | summary | The calibration slope on the held-out split is 1.197 , above… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 13 | conceptual_soundness | The champion is a coefficient-based scoring model: each reta… | -6.103 | ratio | intercept |  | eq | `[[art:e4b3fd0e:run.model_summary#intercept]]` | verified | -6.102832939 |
| 14 | conceptual_soundness | The champion is a coefficient-based scoring model: each reta… | 3500 | count | n_train | train | eq | `[[art:e4b3fd0e:run.model_summary#n_train]]` | verified | 3500 |
| 15 | conceptual_soundness | The subject's feature specification carries 13 features in t… | 13 | count | n |  | eq | `[[art:b85c116d:run.features#n]]` | verified | 13 |
| 16 | conceptual_soundness | Of those, 2 are declared known at origination and 11 are dec… | 2 | count | at_origination |  | eq | `[[art:b85c116d:run.features#at_origination]]` | verified | 2 |
| 17 | conceptual_soundness | Of those, 2 are declared known at origination and 11 are dec… | 11 | count | before_period_start |  | eq | `[[art:b85c116d:run.features#before_period_start]]` | verified | 11 |
| 18 | conceptual_soundness | The specification declares 0 features known only during the… | 0 | count | during_period |  | eq | `[[art:b85c116d:run.features#during_period]]` | verified | 0 |
| 19 | conceptual_soundness | The specification declares 0 features known only during the… | 0 | count | after_outcome |  | eq | `[[art:b85c116d:run.features#after_outcome]]` | verified | 0 |
| 20 | conceptual_soundness | It removed bill_last, whose variance inflation factor was 16… | 162.9 | ratio | vif |  | eq | `[[art:e4b3fd0e:run.model_summary#removed.bill_last.vif]]` | verified | 162.931494 |
| 21 | conceptual_soundness | It removed bill_last, whose variance inflation factor was 16… | 36.78 | ratio | vif |  | eq | `[[art:e4b3fd0e:run.model_summary#removed.utilisation_mean_6m.vif]]` | verified | 36.782216 |
| 22 | conceptual_soundness | It removed bill_last, whose variance inflation factor was 16… | 10 | ratio | vif_threshold |  | eq | `[[art:e4b3fd0e:run.model_summary#vif_threshold]]` | verified | 10 |
| 23 | conceptual_soundness | The largest coefficient in magnitude is the -12.37 on pay_am… | -12.37 | ratio | coefficient |  | eq | `[[art:e4b3fd0e:run.model_summary#coefficients.pay_amt_next.value]]` | verified | -12.36667537 |
| 24 | conceptual_soundness | The next largest are 1.651 on bill_mean_6m, 0.9159 on delinq… | 1.651 | ratio | coefficient |  | eq | `[[art:e4b3fd0e:run.model_summary#coefficients.bill_mean_6m.value]]` | verified | 1.651229182 |
| 25 | conceptual_soundness | The next largest are 1.651 on bill_mean_6m, 0.9159 on delinq… | 0.9159 | ratio | coefficient |  | eq | `[[art:e4b3fd0e:run.model_summary#coefficients.delinq_last.value]]` | verified | 0.9159219077 |
| 26 | conceptual_soundness | The next largest are 1.651 on bill_mean_6m, 0.9159 on delinq… | 0.8591 | ratio | coefficient |  | eq | `[[art:e4b3fd0e:run.model_summary#coefficients.utilisation.value]]` | verified | 0.8591255354 |
| 27 | conceptual_soundness | The next largest are 1.651 on bill_mean_6m, 0.9159 on delinq… | 0.7072 | ratio | coefficient |  | eq | `[[art:e4b3fd0e:run.model_summary#coefficients.pay_ratio_mean_6m.value]]` | verified | 0.7071884027 |
| 28 | conceptual_soundness | The next largest are 1.651 on bill_mean_6m, 0.9159 on delinq… | 0.4311 | ratio | coefficient |  | eq | `[[art:e4b3fd0e:run.model_summary#coefficients.limit_bal.value]]` | verified | 0.4311198001 |
| 29 | conceptual_soundness | The smaller terms are 0.2086 on pay_ratio_last, 0.1993 on bi… | 0.2086 | ratio | coefficient |  | eq | `[[art:e4b3fd0e:run.model_summary#coefficients.pay_ratio_last.value]]` | verified | 0.2086444371 |
| 30 | conceptual_soundness | The smaller terms are 0.2086 on pay_ratio_last, 0.1993 on bi… | 0.1993 | ratio | coefficient |  | eq | `[[art:e4b3fd0e:run.model_summary#coefficients.bill_trend_6m.value]]` | verified | 0.1992999704 |
| 31 | conceptual_soundness | The smaller terms are 0.2086 on pay_ratio_last, 0.1993 on bi… | 0.1073 | ratio | coefficient |  | eq | `[[art:e4b3fd0e:run.model_summary#coefficients.delinq_count_6m.value]]` | verified | 0.1072548632 |
| 32 | conceptual_soundness | The smaller terms are 0.2086 on pay_ratio_last, 0.1993 on bi… | -0.09998 | ratio | coefficient |  | eq | `[[art:e4b3fd0e:run.model_summary#coefficients.delinq_max_6m.value]]` | verified | -0.09997986467 |
| 33 | conceptual_soundness | The smaller terms are 0.2086 on pay_ratio_last, 0.1993 on bi… | -0.08872 | ratio | coefficient |  | eq | `[[art:e4b3fd0e:run.model_summary#coefficients.age.value]]` | verified | -0.08872433211 |
| 34 | conceptual_soundness | The count of retained features whose fitted sign contradicts… | 6 | count | n_disagreements | train | eq | `[[art:75159a84:sign_check.n_disagreements]]` | verified | 6 |
| 35 | conceptual_soundness | The fitted sign on limit_bal is 1 while its own univariate d… | 1 | ratio | coef_sign |  | eq | `[[art:6af6aef2:sign_check.limit_bal.coef_sign]]` | verified | 1 |
| 36 | conceptual_soundness | The fitted sign on limit_bal is 1 while its own univariate d… | -1 | ratio | univariate_direction |  | eq | `[[art:56d284d6:sign_check.limit_bal.univariate_direction]]` | verified | -1 |
| 37 | conceptual_soundness | The fitted sign on limit_bal is 1 while its own univariate d… | 0.0006175 | ratio | delta_auc | test | eq | `[[art:4b976d60:ablation.limit_bal.delta_auc]]` | verified | 0.0006174556236 |
| 38 | conceptual_soundness | The fitted sign on pay_ratio_mean_6m is 1 against a univaria… | 1 | ratio | coef_sign |  | eq | `[[art:8547787e:sign_check.pay_ratio_mean_6m.coef_sign]]` | verified | 1 |
| 39 | conceptual_soundness | The fitted sign on pay_ratio_mean_6m is 1 against a univaria… | -1 | ratio | univariate_direction |  | eq | `[[art:24dcef24:sign_check.pay_ratio_mean_6m.univariate_direction]]` | verified | -1 |
| 40 | conceptual_soundness | The fitted sign on pay_ratio_mean_6m is 1 against a univaria… | -0.0009594 | ratio | delta_auc | test | eq | `[[art:54c168fb:ablation.pay_ratio_mean_6m.delta_auc]]` | verified | -0.0009593525391 |
| 41 | conceptual_soundness | The fitted sign on pay_ratio_last is 1 against a univariate… | 1 | ratio | coef_sign |  | eq | `[[art:f018263e:sign_check.pay_ratio_last.coef_sign]]` | verified | 1 |
| 42 | conceptual_soundness | The fitted sign on pay_ratio_last is 1 against a univariate… | -1 | ratio | univariate_direction |  | eq | `[[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]]` | verified | -1 |
| 43 | conceptual_soundness | The fitted sign on pay_ratio_last is 1 against a univariate… | 0.0001863 | ratio | delta_auc | test | eq | `[[art:c577925a:ablation.pay_ratio_last.delta_auc]]` | verified | 0.0001862572749 |
| 44 | conceptual_soundness | The fitted sign on bill_mean_6m is 1 against a univariate di… | 1 | ratio | coef_sign |  | eq | `[[art:a457c04a:sign_check.bill_mean_6m.coef_sign]]` | verified | 1 |
| 45 | conceptual_soundness | The fitted sign on bill_mean_6m is 1 against a univariate di… | -1 | ratio | univariate_direction |  | eq | `[[art:23b89c5d:sign_check.bill_mean_6m.univariate_direction]]` | verified | -1 |
| 46 | conceptual_soundness | The fitted sign on bill_mean_6m is 1 against a univariate di… | -0.005228 | ratio | delta_auc | test | eq | `[[art:a4586b58:ablation.bill_mean_6m.delta_auc]]` | verified | -0.005227961044 |
| 47 | conceptual_soundness | The fitted sign on bill_trend_6m is 1 against a univariate d… | 1 | ratio | coef_sign |  | eq | `[[art:abd4aaba:sign_check.bill_trend_6m.coef_sign]]` | verified | 1 |
| 48 | conceptual_soundness | The fitted sign on bill_trend_6m is 1 against a univariate d… | -1 | ratio | univariate_direction |  | eq | `[[art:a9bff389:sign_check.bill_trend_6m.univariate_direction]]` | verified | -1 |
| 49 | conceptual_soundness | The fitted sign on bill_trend_6m is 1 against a univariate d… | -0.0005537 | ratio | delta_auc | test | eq | `[[art:54e6a418:ablation.bill_trend_6m.delta_auc]]` | verified | -0.0005536688856 |
| 50 | conceptual_soundness | The fitted sign on delinq_max_6m is -1 against a univariate… | -1 | ratio | coef_sign |  | eq | `[[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]]` | verified | -1 |
| 51 | conceptual_soundness | The fitted sign on delinq_max_6m is -1 against a univariate… | 1 | ratio | univariate_direction |  | eq | `[[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]]` | verified | 1 |
| 52 | conceptual_soundness | The fitted sign on delinq_max_6m is -1 against a univariate… | 0.0001607 | ratio | delta_auc | test | eq | `[[art:b1793491:ablation.delinq_max_6m.delta_auc]]` | verified | 0.0001607425797 |
| 53 | conceptual_soundness | The features whose fitted signs agree with their univariate… | 1 | ratio | coef_sign |  | eq | `[[art:85badc3c:sign_check.utilisation.coef_sign]]` | verified | 1 |
| 54 | conceptual_soundness | The features whose fitted signs agree with their univariate… | 1 | ratio | univariate_direction |  | eq | `[[art:f0995196:sign_check.utilisation.univariate_direction]]` | verified | 1 |
| 55 | conceptual_soundness | The features whose fitted signs agree with their univariate… | 1 | ratio | coef_sign |  | eq | `[[art:50d352f8:sign_check.delinq_last.coef_sign]]` | verified | 1 |
| 56 | conceptual_soundness | The features whose fitted signs agree with their univariate… | 1 | ratio | univariate_direction |  | eq | `[[art:a78648ba:sign_check.delinq_last.univariate_direction]]` | verified | 1 |
| 57 | conceptual_soundness | The features whose fitted signs agree with their univariate… | 1 | ratio | coef_sign |  | eq | `[[art:17afb6f9:sign_check.delinq_count_6m.coef_sign]]` | verified | 1 |
| 58 | conceptual_soundness | The features whose fitted signs agree with their univariate… | 1 | ratio | univariate_direction |  | eq | `[[art:549e904e:sign_check.delinq_count_6m.univariate_direction]]` | verified | 1 |
| 59 | conceptual_soundness | The features whose fitted signs agree with their univariate… | -1 | ratio | coef_sign |  | eq | `[[art:6172eb93:sign_check.age.coef_sign]]` | verified | -1 |
| 60 | conceptual_soundness | The features whose fitted signs agree with their univariate… | -1 | ratio | univariate_direction |  | eq | `[[art:66364583:sign_check.age.univariate_direction]]` | verified | -1 |
| 61 | conceptual_soundness | The features whose fitted signs agree with their univariate… | -1 | ratio | coef_sign |  | eq | `[[art:6fc540c1:sign_check.pay_amt_next.coef_sign]]` | verified | -1 |
| 62 | conceptual_soundness | The features whose fitted signs agree with their univariate… | -1 | ratio | univariate_direction |  | eq | `[[art:1bec400a:sign_check.pay_amt_next.univariate_direction]]` | verified | -1 |
| 63 | conceptual_soundness | Refitting the champion's functional form on every retained f… | 0.9755 | ratio | baseline_auc | test | eq | `[[art:8e58476a:ablation.baseline_auc]]` | verified | 0.9755058926 |
| 64 | conceptual_soundness | Refitting the champion's functional form on every retained f… | 0.9755 | ratio | auc | test | eq | `[[art:8f522f3b:metrics.test.auc]]` | verified | 0.9755058926 |
| 65 | conceptual_soundness | Removing pay_amt_next moves test discrimination by -0.2275 ,… | -0.2275 | ratio | delta_auc | test | eq | `[[art:cf6c0563:ablation.pay_amt_next.delta_auc]]` | verified | -0.2275170885 |
| 66 | conceptual_soundness | Every other removal moves it by a small amount in either dir… | -0.005228 | ratio | delta_auc | test | eq | `[[art:a4586b58:ablation.bill_mean_6m.delta_auc]]` | verified | -0.005227961044 |
| 67 | conceptual_soundness | Every other removal moves it by a small amount in either dir… | -0.0009594 | ratio | delta_auc | test | eq | `[[art:54c168fb:ablation.pay_ratio_mean_6m.delta_auc]]` | verified | -0.0009593525391 |
| 68 | conceptual_soundness | Every other removal moves it by a small amount in either dir… | -0.0009211 | ratio | delta_auc | test | eq | `[[art:43d4225a:ablation.delinq_last.delta_auc]]` | verified | -0.0009210804963 |
| 69 | conceptual_soundness | Every other removal moves it by a small amount in either dir… | -0.0004235 | ratio | delta_auc | test | eq | `[[art:009bc4f1:ablation.utilisation.delta_auc]]` | verified | -0.0004235439401 |
| 70 | conceptual_soundness | Removing age moves it by 5.613e-05 and removing delinq_count… | 5.613e-05 | ratio | delta_auc | test | eq | `[[art:786b509d:ablation.age.delta_auc]]` | verified | 5.613232942e-05 |
| 71 | conceptual_soundness | Removing age moves it by 5.613e-05 and removing delinq_count… | 5.103e-06 | ratio | delta_auc | test | eq | `[[art:3730f6e2:ablation.delinq_count_6m.delta_auc]]` | verified | 5.102939038e-06 |
| 72 | conceptual_soundness | The challenger scores 0.9877 on test against the champion's… | 0.9877 | ratio | auc | test | eq | `[[art:d2646bc7:challenger.auc]]` | verified | 0.9877299831 |
| 73 | conceptual_soundness | The challenger scores 0.9877 on test against the champion's… | 0.9755 | ratio | auc | test | eq | `[[art:8f522f3b:metrics.test.auc]]` | verified | 0.9755058926 |
| 74 | conceptual_soundness | The challenger scores 0.9877 on test against the champion's… | 0.01222 | ratio | delta_auc | test | eq | `[[art:2ab4af27:challenger.delta_auc]]` | verified | 0.01222409046 |
| 75 | conceptual_soundness | The threshold that decides whether such a lead matters is 0.… | 0.03 | ratio | delta_auc |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 76 | conceptual_soundness | On calibration the challenger's Brier score is 0.02542 again… | 0.02542 | ratio | brier | test | eq | `[[art:0a224a0a:challenger.brier]]` | verified | 0.02542316584 |
| 77 | conceptual_soundness | On calibration the challenger's Brier score is 0.02542 again… | 0.04247 | ratio | brier | test | eq | `[[art:d4f27e13:metrics.test.brier]]` | verified | 0.04247487168 |
| 78 | data_integrity | The training split holds 3500 rows and the test split holds… | 3500 | count | n | train | eq | `[[art:2510d49d:profile.train.n]]` | verified | 3500 |
| 79 | data_integrity | The training split holds 3500 rows and the test split holds… | 1500 | count | n | test | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 80 | data_integrity | The largest missing fraction over the columns of the trainin… | 0 | ratio | missing.max | train | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 81 | data_integrity | The largest missing fraction over the columns of the test sp… | 0 | ratio | missing.max | test | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 82 | data_integrity | Comparing the two splits by difference, the two worst-column… | 0.1 | ratio | missing_gap |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 83 | data_integrity | The largest train-to-test population shift over all features… | 0.01789 | ratio | psi |  | eq | `[[art:1b87de3e:psi.max]]` | verified | 0.01789488592 |
| 84 | data_integrity | The largest train-to-test population shift over all features… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 85 | data_integrity | The largest train-to-test population shift over all features… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 86 | data_integrity | That largest shift is carried by `pay_amt_next` at 0.01789 . | 0.01789 | ratio | psi |  | eq | `[[art:996bb509:psi.pay_amt_next]]` | verified | 0.01789488592 |
| 87 | data_integrity | The score itself shifts by 0.01199 , also far below the decl… | 0.01199 | ratio | psi |  | eq | `[[art:05f120d2:psi.y_score]]` | verified | 0.01198828928 |
| 88 | data_integrity | - `age` at 0.008124 | 0.008124 | ratio | psi |  | eq | `[[art:f9255a0a:psi.age]]` | verified | 0.008124281436 |
| 89 | data_integrity | - `bill_mean_6m` at 0.007124 | 0.007124 | ratio | psi |  | eq | `[[art:028e4281:psi.bill_mean_6m]]` | verified | 0.007124196275 |
| 90 | data_integrity | - `bill_trend_6m` at 0.00958 | 0.00958 | ratio | psi |  | eq | `[[art:c247a6f2:psi.bill_trend_6m]]` | verified | 0.009579614525 |
| 91 | data_integrity | - `delinq_count_6m` at 0.002069 | 0.002069 | ratio | psi |  | eq | `[[art:61491d02:psi.delinq_count_6m]]` | verified | 0.002069275496 |
| 92 | data_integrity | - `delinq_last` at 0.00285 | 0.00285 | ratio | psi |  | eq | `[[art:03bd52e7:psi.delinq_last]]` | verified | 0.002849633848 |
| 93 | data_integrity | - `delinq_max_6m` at 0.005498 | 0.005498 | ratio | psi |  | eq | `[[art:7a82e7f3:psi.delinq_max_6m]]` | verified | 0.005498249408 |
| 94 | data_integrity | - `limit_bal` at 0.01095 | 0.01095 | ratio | psi |  | eq | `[[art:601cdba2:psi.limit_bal]]` | verified | 0.01095273358 |
| 95 | data_integrity | - `pay_ratio_last` at 0.004966 | 0.004966 | ratio | psi |  | eq | `[[art:3af2ca29:psi.pay_ratio_last]]` | verified | 0.00496591109 |
| 96 | data_integrity | - `pay_ratio_mean_6m` at 0.0055 | 0.0055 | ratio | psi |  | eq | `[[art:2c5baeb2:psi.pay_ratio_mean_6m]]` | verified | 0.005500252946 |
| 97 | data_integrity | - `utilisation` at 0.004244 | 0.004244 | ratio | psi |  | eq | `[[art:451e0780:psi.utilisation]]` | verified | 0.0042440485 |
| 98 | data_integrity | Every one of these sits below the declared bound of 0.25 , a… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 99 | data_integrity | The largest contribution to the shift in the linear predicto… | 0.4064 | ratio | csi |  | eq | `[[art:3f7f79cf:csi.max]]` | verified | 0.4063916509 |
| 100 | data_integrity | The largest contribution to the shift in the linear predicto… | 0.4064 | ratio | csi |  | eq | `[[art:e708fa25:csi.pay_amt_next]]` | verified | 0.4063916509 |
| 101 | data_integrity | The next largest contribution belongs to `delinq_last` at 0.… | 0.0295 | ratio | csi |  | eq | `[[art:cd29d613:csi.delinq_last]]` | verified | 0.02950471301 |
| 102 | data_integrity | - `age` at 0.00125 | 0.00125 | ratio | csi |  | eq | `[[art:584faff4:csi.age]]` | verified | 0.00125000439 |
| 103 | data_integrity | - `bill_mean_6m` at 0.0105 | 0.0105 | ratio | csi |  | eq | `[[art:f374dbd7:csi.bill_mean_6m]]` | verified | 0.01049921023 |
| 104 | data_integrity | - `bill_trend_6m` at 0.00567 | 0.00567 | ratio | csi |  | eq | `[[art:8bb46253:csi.bill_trend_6m]]` | verified | 0.005670244137 |
| 105 | data_integrity | - `delinq_count_6m` at 0.002143 | 0.002143 | ratio | csi |  | eq | `[[art:4564aa47:csi.delinq_count_6m]]` | verified | 0.00214274047 |
| 106 | data_integrity | - `delinq_max_6m` at 0.002782 | 0.002782 | ratio | csi |  | eq | `[[art:2fe28db6:csi.delinq_max_6m]]` | verified | 0.002782289452 |
| 107 | data_integrity | - `limit_bal` at 0.007188 | 0.007188 | ratio | csi |  | eq | `[[art:cb617a64:csi.limit_bal]]` | verified | 0.007188476411 |
| 108 | data_integrity | - `pay_ratio_last` at 0.003912 | 0.003912 | ratio | csi |  | eq | `[[art:c083b28c:csi.pay_ratio_last]]` | verified | 0.003912462231 |
| 109 | data_integrity | - `pay_ratio_mean_6m` at 0.003519 | 0.003519 | ratio | csi |  | eq | `[[art:8f1dbe89:csi.pay_ratio_mean_6m]]` | verified | 0.003518997237 |
| 110 | data_integrity | - `utilisation` at 0.01304 | 0.01304 | ratio | csi |  | eq | `[[art:b1f362df:csi.utilisation]]` | verified | 0.01304415209 |
| 111 | data_integrity | The count of features declared as observed during the perfor… | 0 | count | leakage.timing.n_flagged |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 112 | data_integrity | The count of feature names matching the target-adjacent lexi… | 0 | count | leakage.name_screen.n_matched |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 113 | data_integrity | The strongest single feature reaches an AUC of 0.945 against… | 0.945 | ratio | max_single_feature_auc |  | eq | `[[art:5b5e98c2:leakage.target_corr.max_single_feature_auc]]` | verified | 0.9449621321 |
| 114 | data_integrity | The strongest single feature reaches an AUC of 0.945 against… | 0.9 | ratio | single_feature_auc |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 115 | data_integrity | The share of test rows whose identifiers also identify a row… | 0 | ratio | overlap.ids |  | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 116 | data_integrity | The share of test rows whose identifiers also identify a row… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 117 | data_integrity | The share of test rows whose feature values also appear in t… | 0 | ratio | overlap.features |  | eq | `[[art:0fec8048:leakage.overlap.features]]` | verified | 0 |
| 118 | data_integrity | The share of test rows whose feature values also appear in t… | 0.005 | ratio | overlap.features_effective |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 119 | data_integrity | That effective bound is the larger of the declared overlap b… | 0 | ratio | duplicates | train | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 120 | data_integrity | The row-level overlap between the splits is likewise 0 , rea… | 0 | ratio | overlap |  | eq | `[[art:4c9fcd09:leakage.overlap]]` | verified | 0 |
| 121 | data_integrity | The row-level overlap between the splits is likewise 0 , rea… | 0.005 | ratio | overlap.features_effective |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 122 | outcomes | The reason is the observed event rate on the evaluation spli… | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 123 | outcomes | The reason is the observed event rate on the evaluation spli… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 124 | outcomes | \| observations \| 3500 \| 1500 \| | 3500 | count | n | train | eq | `[[art:564683ee:metrics.train.n]]` | verified | 3500 |
| 125 | outcomes | \| observations \| 3500 \| 1500 \| | 1500 | count | n | test | eq | `[[art:64fcf14d:metrics.test.n]]` | verified | 1500 |
| 126 | outcomes | \| observed event rate \| 0.2246 \| 0.2247 \| | 0.2246 | ratio | event_rate | train | eq | `[[art:133a5ff8:metrics.train.event_rate]]` | verified | 0.2245714286 |
| 127 | outcomes | \| observed event rate \| 0.2246 \| 0.2247 \| | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 128 | outcomes | \| AUC \| 0.9812 \| 0.9755 \| | 0.9812 | ratio | auc | train | eq | `[[art:da2cd01d:metrics.train.auc]]` | verified | 0.9811790152 |
| 129 | outcomes | \| AUC \| 0.9812 \| 0.9755 \| | 0.9755 | ratio | auc | test | eq | `[[art:8f522f3b:metrics.test.auc]]` | verified | 0.9755058926 |
| 130 | outcomes | \| Gini \| 0.9624 \| 0.951 \| | 0.9624 | ratio | gini | train | eq | `[[art:23cb4057:metrics.train.gini]]` | verified | 0.9623580305 |
| 131 | outcomes | \| Gini \| 0.9624 \| 0.951 \| | 0.951 | ratio | gini | test | eq | `[[art:f927e3cd:metrics.test.gini]]` | verified | 0.9510117852 |
| 132 | outcomes | \| KS \| 0.8895 \| 0.8784 \| | 0.8895 | ratio | ks | train | eq | `[[art:7a126f15:metrics.train.ks]]` | verified | 0.8894536106 |
| 133 | outcomes | \| KS \| 0.8895 \| 0.8784 \| | 0.8784 | ratio | ks | test | eq | `[[art:81bee194:metrics.test.ks]]` | verified | 0.8784403377 |
| 134 | outcomes | \| Brier \| 0.03817 \| 0.04247 \| | 0.03817 | ratio | brier | train | eq | `[[art:959b3159:metrics.train.brier]]` | verified | 0.03816687592 |
| 135 | outcomes | \| Brier \| 0.03817 \| 0.04247 \| | 0.04247 | ratio | brier | test | eq | `[[art:d4f27e13:metrics.test.brier]]` | verified | 0.04247487168 |
| 136 | outcomes | \| log loss \| 0.1505 \| 0.167 \| | 0.1505 | ratio | logloss | train | eq | `[[art:417d98d9:metrics.train.logloss]]` | verified | 0.1504741108 |
| 137 | outcomes | \| log loss \| 0.1505 \| 0.167 \| | 0.167 | ratio | logloss | test | eq | `[[art:aa620b5e:metrics.test.logloss]]` | verified | 0.1670045909 |
| 138 | outcomes | \| mean predicted probability \| 0.2246 \| 0.233 \| | 0.2246 | ratio | mean_predicted | train | eq | `[[art:1fa024a6:metrics.train.mean_predicted]]` | verified | 0.2245520437 |
| 139 | outcomes | \| mean predicted probability \| 0.2246 \| 0.233 \| | 0.233 | ratio | mean_predicted | test | eq | `[[art:0b9b6a1e:metrics.test.mean_predicted]]` | verified | 0.2330182196 |
| 140 | outcomes | The share of evaluation-split events captured in the highest… | 0.822 | ratio | top2_capture | test | eq | `[[art:5690757b:deciles.test.top2_capture]]` | verified | 0.821958457 |
| 141 | outcomes | The share of evaluation-split events captured in the highest… | 0.8422 | ratio | top2_capture | train | eq | `[[art:55242963:deciles.train.top2_capture]]` | verified | 0.8422391858 |
| 142 | outcomes | Discrimination is higher on the development split, 0.9812 ,… | 0.9812 | ratio | auc | train | eq | `[[art:da2cd01d:metrics.train.auc]]` | verified | 0.9811790152 |
| 143 | outcomes | Discrimination is higher on the development split, 0.9812 ,… | 0.9755 | ratio | auc | test | eq | `[[art:8f522f3b:metrics.test.auc]]` | verified | 0.9755058926 |
| 144 | outcomes | Discrimination is higher on the development split, 0.9812 ,… | 0.08 | ratio | auc_gap |  | eq | `[[art:630f28f4:threshold.O1.auc_gap]]` | verified | 0.08 |
| 145 | outcomes | The logistic regression of the outcome on the logit of the p… | 1.197 | ratio | calibration_slope | test | eq | `[[art:c9a03fe6:calibration_slope.test]]` | verified | 1.19744242 |
| 146 | outcomes | The logistic regression of the outcome on the logit of the p… | 1.383 | ratio | calibration_slope | train | eq | `[[art:45dafd11:calibration_slope.train]]` | verified | 1.383137681 |
| 147 | outcomes | The declared band runs from 0.8 to 1.2 , and the evaluation-… | 0.8 | ratio | calibration_slope |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 148 | outcomes | The declared band runs from 0.8 to 1.2 , and the evaluation-… | 1.2 | ratio | calibration_slope |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 149 | outcomes | The corresponding intercepts are -0.0558 on the evaluation s… | -0.0558 | ratio | calibration_intercept | test | eq | `[[art:56745cf2:calibration_intercept.test]]` | verified | -0.05579737693 |
| 150 | outcomes | The corresponding intercepts are -0.0558 on the evaluation s… | 0.2246 | ratio | calibration_intercept | train | eq | `[[art:d556f341:calibration_intercept.train]]` | verified | 0.2245889138 |
| 151 | outcomes | On the evaluation split the mean predicted probability is 0.… | 0.233 | ratio | mean_predicted | test | eq | `[[art:0b9b6a1e:metrics.test.mean_predicted]]` | verified | 0.2330182196 |
| 152 | outcomes | On the evaluation split the mean predicted probability is 0.… | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 153 | outcomes | That separation expressed relative to the observed rate is 0… | 0.03717 | ratio | mean_rel_gap | test | eq | `[[art:6a845d81:calibration.mean_rel_gap.test]]` | verified | 0.0371730842 |
| 154 | outcomes | That separation expressed relative to the observed rate is 0… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 155 | outcomes | On the development split the mean predicted probability is 0… | 0.2246 | ratio | mean_predicted | train | eq | `[[art:1fa024a6:metrics.train.mean_predicted]]` | verified | 0.2245520437 |
| 156 | outcomes | On the development split the mean predicted probability is 0… | 0.2246 | ratio | event_rate | train | eq | `[[art:133a5ff8:metrics.train.event_rate]]` | verified | 0.2245714286 |
| 157 | outcomes | On the development split the mean predicted probability is 0… | 8.632e-05 | ratio | mean_rel_gap | train | eq | `[[art:f7447f34:calibration.mean_rel_gap.train]]` | verified | 8.631936949e-05 |
| 158 | outcomes | On the evaluation split this sub-population's AUC falls belo… | 0.008772 | ratio | auc_gap | test | eq | `[[art:cd5172fc:metrics.test.sub.pay_amt_next_low.auc_gap]]` | verified | 0.008772256467 |
| 159 | outcomes | On the evaluation split this sub-population's AUC falls belo… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 160 | outcomes | On the evaluation split this sub-population's AUC falls belo… | 0.5 | ratio | share | test | eq | `[[art:18eac95f:metrics.test.sub.pay_amt_next_low.share]]` | verified | 0.5 |
| 161 | outcomes | On the evaluation split this sub-population's AUC falls belo… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 162 | outcomes | On the development split the same sub-population falls below… | 0.003167 | ratio | auc_gap | train | eq | `[[art:4b2a3b88:metrics.train.sub.pay_amt_next_low.auc_gap]]` | verified | 0.003166761813 |
| 163 | outcomes | On the development split the same sub-population falls below… | 0.5 | ratio | share | train | eq | `[[art:01d5682e:metrics.train.sub.pay_amt_next_low.share]]` | verified | 0.5 |
| 164 | outcomes | Mean predicted against observed reads 0.4452 against 0.424 o… | 0.4452 | ratio | mean_predicted | test | eq | `[[art:036756aa:metrics.test.sub.pay_amt_next_low.mean_predicted]]` | verified | 0.4451864624 |
| 165 | outcomes | Mean predicted against observed reads 0.4452 against 0.424 o… | 0.424 | ratio | event_rate | test | eq | `[[art:c5cd207d:metrics.test.sub.pay_amt_next_low.event_rate]]` | verified | 0.424 |
| 166 | outcomes | Mean predicted against observed reads 0.4452 against 0.424 o… | 0.04997 | ratio | mean_rel_gap | test | eq | `[[art:a89da41c:metrics.test.sub.pay_amt_next_low.mean_rel_gap]]` | verified | 0.04996807166 |
| 167 | outcomes | Mean predicted against observed reads 0.4452 against 0.424 o… | 0.4288 | ratio | mean_predicted | train | eq | `[[art:9ebffd6f:metrics.train.sub.pay_amt_next_low.mean_predicted]]` | verified | 0.4287879929 |
| 168 | outcomes | Mean predicted against observed reads 0.4452 against 0.424 o… | 0.432 | ratio | event_rate | train | eq | `[[art:20cb26cd:metrics.train.sub.pay_amt_next_low.event_rate]]` | verified | 0.432 |
| 169 | outcomes | Mean predicted against observed reads 0.4452 against 0.424 o… | 0.007435 | ratio | mean_rel_gap | train | eq | `[[art:3afbd6e4:metrics.train.sub.pay_amt_next_low.mean_rel_gap]]` | verified | 0.007435201539 |
| 170 | outcomes | On the evaluation split this sub-population's AUC is 0.8821… | 0.8821 | ratio | auc | test | eq | `[[art:e2b8b0f2:metrics.test.sub.pay_amt_next_high.auc]]` | verified | 0.8820649435 |
| 171 | outcomes | On the evaluation split this sub-population's AUC is 0.8821… | 0.09344 | ratio | auc_gap | test | eq | `[[art:ad693cad:metrics.test.sub.pay_amt_next_high.auc_gap]]` | verified | 0.09344094914 |
| 172 | outcomes | On the evaluation split this sub-population's AUC is 0.8821… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 173 | outcomes | On the evaluation split this sub-population's AUC is 0.8821… | 0.5 | ratio | share | test | eq | `[[art:21c17ed0:metrics.test.sub.pay_amt_next_high.share]]` | verified | 0.5 |
| 174 | outcomes | On the evaluation split this sub-population's AUC is 0.8821… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 175 | outcomes | On the development split it falls below that split's own AUC… | 0.1067 | ratio | auc_gap | train | eq | `[[art:30718a8b:metrics.train.sub.pay_amt_next_high.auc_gap]]` | verified | 0.1066635114 |
| 176 | outcomes | On the development split it falls below that split's own AUC… | 0.5 | ratio | share | train | eq | `[[art:c4cc28b1:metrics.train.sub.pay_amt_next_high.share]]` | verified | 0.5 |
| 177 | outcomes | Mean predicted against observed reads 0.02085 against 0.0253… | 0.02085 | ratio | mean_predicted | test | eq | `[[art:dcacb7a5:metrics.test.sub.pay_amt_next_high.mean_predicted]]` | verified | 0.02084997678 |
| 178 | outcomes | Mean predicted against observed reads 0.02085 against 0.0253… | 0.02533 | ratio | event_rate | test | eq | `[[art:9702492a:metrics.test.sub.pay_amt_next_high.event_rate]]` | verified | 0.02533333333 |
| 179 | outcomes | Mean predicted against observed reads 0.02085 against 0.0253… | 0.177 | ratio | mean_rel_gap | test | eq | `[[art:5a35c2f9:metrics.test.sub.pay_amt_next_high.mean_rel_gap]]` | verified | 0.1769746007 |
| 180 | outcomes | Mean predicted against observed reads 0.02085 against 0.0253… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 181 | outcomes | Mean predicted against observed reads 0.02085 against 0.0253… | 0.02032 | ratio | mean_predicted | train | eq | `[[art:968cddfe:metrics.train.sub.pay_amt_next_high.mean_predicted]]` | verified | 0.02031609448 |
| 182 | outcomes | Mean predicted against observed reads 0.02085 against 0.0253… | 0.01714 | ratio | event_rate | train | eq | `[[art:81517b8d:metrics.train.sub.pay_amt_next_high.event_rate]]` | verified | 0.01714285714 |
| 183 | outcomes | Mean predicted against observed reads 0.02085 against 0.0253… | 0.1851 | ratio | mean_rel_gap | train | eq | `[[art:2d65d0bd:metrics.train.sub.pay_amt_next_high.mean_rel_gap]]` | verified | 0.1851055113 |
| 184 | outcomes | On the evaluation split this sub-population's AUC falls belo… | 0.008535 | ratio | auc_gap | test | eq | `[[art:6990b76c:metrics.test.sub.limit_bal_low.auc_gap]]` | verified | 0.008535185397 |
| 185 | outcomes | On the evaluation split this sub-population's AUC falls belo… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 186 | outcomes | On the evaluation split this sub-population's AUC falls belo… | 0.504 | ratio | share | test | eq | `[[art:bac689cc:metrics.test.sub.limit_bal_low.share]]` | verified | 0.504 |
| 187 | outcomes | On the evaluation split this sub-population's AUC falls belo… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 188 | outcomes | On the development split it falls below that split's own AUC… | 0.008866 | ratio | auc_gap | train | eq | `[[art:999aab9c:metrics.train.sub.limit_bal_low.auc_gap]]` | verified | 0.008866169575 |
| 189 | outcomes | On the development split it falls below that split's own AUC… | 0.5037 | ratio | share | train | eq | `[[art:45c51f9e:metrics.train.sub.limit_bal_low.share]]` | verified | 0.5037142857 |
| 190 | outcomes | Mean predicted against observed reads 0.2585 against 0.2487… | 0.2585 | ratio | mean_predicted | test | eq | `[[art:c1a37d64:metrics.test.sub.limit_bal_low.mean_predicted]]` | verified | 0.2584577028 |
| 191 | outcomes | Mean predicted against observed reads 0.2585 against 0.2487… | 0.2487 | ratio | event_rate | test | eq | `[[art:de78adb5:metrics.test.sub.limit_bal_low.event_rate]]` | verified | 0.2486772487 |
| 192 | outcomes | Mean predicted against observed reads 0.2585 against 0.2487… | 0.03933 | ratio | mean_rel_gap | test | eq | `[[art:2b29e325:metrics.test.sub.limit_bal_low.mean_rel_gap]]` | verified | 0.03932991131 |
| 193 | outcomes | Mean predicted against observed reads 0.2585 against 0.2487… | 0.2458 | ratio | mean_predicted | train | eq | `[[art:2086a25d:metrics.train.sub.limit_bal_low.mean_predicted]]` | verified | 0.2457700925 |
| 194 | outcomes | Mean predicted against observed reads 0.2585 against 0.2487… | 0.2439 | ratio | event_rate | train | eq | `[[art:0ae85aa6:metrics.train.sub.limit_bal_low.event_rate]]` | verified | 0.243902439 |
| 195 | outcomes | Mean predicted against observed reads 0.2585 against 0.2487… | 0.007657 | ratio | mean_rel_gap | train | eq | `[[art:a93d065e:metrics.train.sub.limit_bal_low.mean_rel_gap]]` | verified | 0.007657379338 |
| 196 | outcomes | On the evaluation split this sub-population's AUC gap agains… | -0.00586 | ratio | auc_gap | test | eq | `[[art:e37bc8d6:metrics.test.sub.limit_bal_high.auc_gap]]` | verified | -0.005860076588 |
| 197 | outcomes | On the evaluation split this sub-population's AUC gap agains… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 198 | outcomes | On the evaluation split this sub-population's AUC gap agains… | 0.496 | ratio | share | test | eq | `[[art:ac383ccb:metrics.test.sub.limit_bal_high.share]]` | verified | 0.496 |
| 199 | outcomes | On the evaluation split this sub-population's AUC gap agains… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 200 | outcomes | On the development split the corresponding gap is -0.006442… | -0.006442 | ratio | auc_gap | train | eq | `[[art:52a49712:metrics.train.sub.limit_bal_high.auc_gap]]` | verified | -0.006441907569 |
| 201 | outcomes | On the development split the corresponding gap is -0.006442… | 0.4963 | ratio | share | train | eq | `[[art:2de2a90a:metrics.train.sub.limit_bal_high.share]]` | verified | 0.4962857143 |
| 202 | outcomes | Mean predicted against observed reads 0.2072 against 0.2003… | 0.2072 | ratio | mean_predicted | test | eq | `[[art:f80c93c0:metrics.test.sub.limit_bal_high.mean_predicted]]` | verified | 0.2071684221 |
| 203 | outcomes | Mean predicted against observed reads 0.2072 against 0.2003… | 0.2003 | ratio | event_rate | test | eq | `[[art:5e9aab40:metrics.test.sub.limit_bal_high.event_rate]]` | verified | 0.2002688172 |
| 204 | outcomes | Mean predicted against observed reads 0.2072 against 0.2003… | 0.03445 | ratio | mean_rel_gap | test | eq | `[[art:679e4d84:metrics.test.sub.limit_bal_high.mean_rel_gap]]` | verified | 0.03445171844 |
| 205 | outcomes | Mean predicted against observed reads 0.2072 against 0.2003… | 0.203 | ratio | mean_predicted | train | eq | `[[art:b1995539:metrics.train.sub.limit_bal_high.mean_predicted]]` | verified | 0.203016396 |
| 206 | outcomes | Mean predicted against observed reads 0.2072 against 0.2003… | 0.205 | ratio | event_rate | train | eq | `[[art:9de459ef:metrics.train.sub.limit_bal_high.event_rate]]` | verified | 0.2049510651 |
| 207 | outcomes | Mean predicted against observed reads 0.2072 against 0.2003… | 0.00944 | ratio | mean_rel_gap | train | eq | `[[art:58ae0f50:metrics.train.sub.limit_bal_high.mean_rel_gap]]` | verified | 0.009439663314 |
| 208 | outcomes | Both credit-limit sub-populations order within the slice bou… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 209 | sensitivity | The largest variance inflation factor across the retained fe… | 8.181 | ratio | vif |  | eq | `[[art:4afdc4f1:vif.max]]` | verified | 8.181114607 |
| 210 | sensitivity | The largest variance inflation factor across the retained fe… | 10 | ratio | vif |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 211 | sensitivity | That largest value belongs to the six-month mean bill balanc… | 8.181 | ratio | vif |  | eq | `[[art:d5ab7306:vif.bill_mean_6m]]` | verified | 8.181114607 |
| 212 | sensitivity | The next values down are the six-month mean payment ratio at… | 7.526 | ratio | vif |  | eq | `[[art:000b6208:vif.pay_ratio_mean_6m]]` | verified | 7.525569541 |
| 213 | sensitivity | The next values down are the six-month mean payment ratio at… | 7.268 | ratio | vif |  | eq | `[[art:bec24796:vif.pay_ratio_last]]` | verified | 7.267755553 |
| 214 | sensitivity | The next values down are the six-month mean payment ratio at… | 4.81 | ratio | vif |  | eq | `[[art:8209ea46:vif.limit_bal]]` | verified | 4.809808481 |
| 215 | sensitivity | The remaining retained features fall further below it: utili… | 3.215 | ratio | vif |  | eq | `[[art:ec978947:vif.utilisation]]` | verified | 3.215174221 |
| 216 | sensitivity | The remaining retained features fall further below it: utili… | 2.561 | ratio | vif |  | eq | `[[art:87890613:vif.delinq_count_6m]]` | verified | 2.56148636 |
| 217 | sensitivity | The remaining retained features fall further below it: utili… | 2.408 | ratio | vif |  | eq | `[[art:4b239ec5:vif.delinq_max_6m]]` | verified | 2.408148028 |
| 218 | sensitivity | The remaining retained features fall further below it: utili… | 2.206 | ratio | vif |  | eq | `[[art:68806d80:vif.pay_amt_next]]` | verified | 2.206074628 |
| 219 | sensitivity | The remaining retained features fall further below it: utili… | 1.422 | ratio | vif |  | eq | `[[art:c18221d4:vif.delinq_last]]` | verified | 1.422439811 |
| 220 | sensitivity | The remaining retained features fall further below it: utili… | 1.225 | ratio | vif |  | eq | `[[art:0cb3df89:vif.bill_trend_6m]]` | verified | 1.225337779 |
| 221 | sensitivity | The remaining retained features fall further below it: utili… | 1.002 | ratio | vif |  | eq | `[[art:8021b06e:vif.age]]` | verified | 1.002328679 |
| 222 | sensitivity | Belsley's condition number of the column-standardised design… | 6.185 | ratio | condition_number |  | eq | `[[art:36392379:condition_number]]` | verified | 6.185189657 |
| 223 | sensitivity | Belsley's condition number of the column-standardised design… | 30 | ratio | condition_number |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 224 | findings | The strongest single feature, `pay_amt_next`, reaches an AUC… | 0.945 | ratio | max_single_feature_auc |  | eq | `[[art:5b5e98c2:leakage.target_corr.max_single_feature_auc]]` | verified | 0.9449621321 |
| 225 | findings | The strongest single feature, `pay_amt_next`, reaches an AUC… | 0.9 | ratio | single_feature_auc |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 226 | findings | The declared-timing evidence flags 0 features as observed du… | 0 | count | n_flagged |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 227 | findings | The validator concludes that the headline discrimination of… | 0.9755 | ratio | auc | test | eq | `[[art:8f522f3b:metrics.test.auc]]` | verified | 0.9755058926 |
| 228 | findings | The logistic regression of the outcome on the logit of the p… | 1.383 | ratio | calibration_slope | train | eq | `[[art:45dafd11:calibration_slope.train]]` | verified | 1.383137681 |
| 229 | findings | The logistic regression of the outcome on the logit of the p… | 1.2 | ratio | calibration_slope |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 230 | findings | On test the sub-population `pay_amt_next > median(pay_amt_ne… | 0.8821 | ratio | auc | test | eq | `[[art:e2b8b0f2:metrics.test.sub.pay_amt_next_high.auc]]` | verified | 0.8820649435 |
| 231 | findings | On test the sub-population `pay_amt_next > median(pay_amt_ne… | 0.9755 | ratio | auc | test | eq | `[[art:8f522f3b:metrics.test.auc]]` | verified | 0.9755058926 |
| 232 | findings | On test the sub-population `pay_amt_next > median(pay_amt_ne… | 0.09344 | ratio | auc_gap | test | eq | `[[art:ad693cad:metrics.test.sub.pay_amt_next_high.auc_gap]]` | verified | 0.09344094914 |
| 233 | findings | On test the sub-population `pay_amt_next > median(pay_amt_ne… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 234 | findings | On test the sub-population `pay_amt_next > median(pay_amt_ne… | 0.5 | ratio | share | test | eq | `[[art:21c17ed0:metrics.test.sub.pay_amt_next_high.share]]` | verified | 0.5 |
| 235 | findings | On test the sub-population `pay_amt_next > median(pay_amt_ne… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 236 | findings | On train the same sub-population `pay_amt_next > median(pay_… | 0.8745 | ratio | auc | train | eq | `[[art:649333b3:metrics.train.sub.pay_amt_next_high.auc]]` | verified | 0.8745155039 |
| 237 | findings | On train the same sub-population `pay_amt_next > median(pay_… | 0.9812 | ratio | auc | train | eq | `[[art:da2cd01d:metrics.train.auc]]` | verified | 0.9811790152 |
| 238 | findings | On train the same sub-population `pay_amt_next > median(pay_… | 0.1067 | ratio | auc_gap | train | eq | `[[art:30718a8b:metrics.train.sub.pay_amt_next_high.auc_gap]]` | verified | 0.1066635114 |
| 239 | findings | On train the same sub-population `pay_amt_next > median(pay_… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 240 | findings | On train the same sub-population `pay_amt_next > median(pay_… | 0.5 | ratio | share | train | eq | `[[art:c4cc28b1:metrics.train.sub.pay_amt_next_high.share]]` | verified | 0.5 |
| 241 | findings | On train the same sub-population `pay_amt_next > median(pay_… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 242 | findings | The fitted coefficient on `bill_mean_6m` carries sign 1 wher… | 1 | ratio | coef_sign |  | eq | `[[art:a457c04a:sign_check.bill_mean_6m.coef_sign]]` | verified | 1 |
| 243 | findings | The fitted coefficient on `bill_mean_6m` carries sign 1 wher… | -1 | ratio | univariate_direction | train | eq | `[[art:23b89c5d:sign_check.bill_mean_6m.univariate_direction]]` | verified | -1 |
| 244 | findings | The fitted coefficient on `bill_mean_6m` carries sign 1 wher… | 0 | ratio | agrees |  | eq | `[[art:4df8b747:sign_check.bill_mean_6m.agrees]]` | verified | 0 |
| 245 | findings | The fitted coefficient on `bill_trend_6m` carries sign 1 whe… | 1 | ratio | coef_sign |  | eq | `[[art:abd4aaba:sign_check.bill_trend_6m.coef_sign]]` | verified | 1 |
| 246 | findings | The fitted coefficient on `bill_trend_6m` carries sign 1 whe… | -1 | ratio | univariate_direction | train | eq | `[[art:a9bff389:sign_check.bill_trend_6m.univariate_direction]]` | verified | -1 |
| 247 | findings | The fitted coefficient on `bill_trend_6m` carries sign 1 whe… | 0 | ratio | agrees |  | eq | `[[art:c0f6d07d:sign_check.bill_trend_6m.agrees]]` | verified | 0 |
| 248 | findings | The fitted coefficient on `delinq_max_6m` carries sign -1 wh… | -1 | ratio | coef_sign |  | eq | `[[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]]` | verified | -1 |
| 249 | findings | The fitted coefficient on `delinq_max_6m` carries sign -1 wh… | 1 | ratio | univariate_direction | train | eq | `[[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]]` | verified | 1 |
| 250 | findings | The fitted coefficient on `delinq_max_6m` carries sign -1 wh… | 0 | ratio | agrees |  | eq | `[[art:c946359c:sign_check.delinq_max_6m.agrees]]` | verified | 0 |
| 251 | findings | The fitted coefficient on `limit_bal` carries sign 1 where t… | 1 | ratio | coef_sign |  | eq | `[[art:6af6aef2:sign_check.limit_bal.coef_sign]]` | verified | 1 |
| 252 | findings | The fitted coefficient on `limit_bal` carries sign 1 where t… | -1 | ratio | univariate_direction | train | eq | `[[art:56d284d6:sign_check.limit_bal.univariate_direction]]` | verified | -1 |
| 253 | findings | The fitted coefficient on `limit_bal` carries sign 1 where t… | 0 | ratio | agrees |  | eq | `[[art:0278aad1:sign_check.limit_bal.agrees]]` | verified | 0 |
| 254 | findings | The fitted coefficient on `pay_ratio_last` carries sign 1 wh… | 1 | ratio | coef_sign |  | eq | `[[art:f018263e:sign_check.pay_ratio_last.coef_sign]]` | verified | 1 |
| 255 | findings | The fitted coefficient on `pay_ratio_last` carries sign 1 wh… | -1 | ratio | univariate_direction | train | eq | `[[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]]` | verified | -1 |
| 256 | findings | The fitted coefficient on `pay_ratio_last` carries sign 1 wh… | 0 | ratio | agrees |  | eq | `[[art:79abee77:sign_check.pay_ratio_last.agrees]]` | verified | 0 |
| 257 | findings | The fitted coefficient on `pay_ratio_mean_6m` carries sign 1… | 1 | ratio | coef_sign |  | eq | `[[art:8547787e:sign_check.pay_ratio_mean_6m.coef_sign]]` | verified | 1 |
| 258 | findings | The fitted coefficient on `pay_ratio_mean_6m` carries sign 1… | -1 | ratio | univariate_direction | train | eq | `[[art:24dcef24:sign_check.pay_ratio_mean_6m.univariate_direction]]` | verified | -1 |
| 259 | findings | The fitted coefficient on `pay_ratio_mean_6m` carries sign 1… | 0 | ratio | agrees |  | eq | `[[art:51914c14:sign_check.pay_ratio_mean_6m.agrees]]` | verified | 0 |
| 260 | monitoring | Discrimination on each scored production vintage should be t… | 0.7 | ratio | auc | test | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 261 | monitoring | Discrimination on each scored production vintage should be t… | 0.9755 | ratio | auc | test | eq | `[[art:8f522f3b:metrics.test.auc]]` | verified | 0.9755058926 |
| 262 | monitoring | Probability accuracy should be tracked against the declared… | 0.2 | ratio | brier | test | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 263 | monitoring | Probability accuracy should be tracked against the declared… | 0.04247 | ratio | brier | test | eq | `[[art:d4f27e13:metrics.test.brier]]` | verified | 0.04247487168 |
| 264 | monitoring | Calibration should be tracked against the declared band whos… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 265 | monitoring | Calibration should be tracked against the declared band whos… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 266 | monitoring | This quantity warrants the closest watch of the three, becau… | 1.197 | ratio | calibration_slope | test | eq | `[[art:c9a03fe6:calibration_slope.test]]` | verified | 1.19744242 |
| 267 | monitoring | Input and score stability should be tracked against the decl… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 268 | monitoring | Input and score stability should be tracked against the decl… | 0.01789 | ratio | psi |  | eq | `[[art:1b87de3e:psi.max]]` | verified | 0.01789488592 |
| 269 | monitoring | Section 4 of this report reported discrimination before cali… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 270 | monitoring | If a future production cohort has an observed event rate bel… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |

## Appendix B — Artifact index

The store holds 274 artifacts; the 196 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `ablation.age.delta_auc` | `786b509d` | scalar | 5.613232942e-05 | change in test AUC when the champion's form is refitted without age |
| `ablation.baseline_auc` | `8e58476a` | scalar | 0.9755058926 | AUC on test of a refit of the champion's functional form on every retained feature, the level each ablation delta is measured from |
| `ablation.bill_mean_6m.delta_auc` | `a4586b58` | scalar | -0.005227961044 | change in test AUC when the champion's form is refitted without bill_mean_6m |
| `ablation.bill_trend_6m.delta_auc` | `54e6a418` | scalar | -0.0005536688856 | change in test AUC when the champion's form is refitted without bill_trend_6m |
| `ablation.delinq_count_6m.delta_auc` | `3730f6e2` | scalar | 5.102939038e-06 | change in test AUC when the champion's form is refitted without delinq_count_6m |
| `ablation.delinq_last.delta_auc` | `43d4225a` | scalar | -0.0009210804963 | change in test AUC when the champion's form is refitted without delinq_last |
| `ablation.delinq_max_6m.delta_auc` | `b1793491` | scalar | 0.0001607425797 | change in test AUC when the champion's form is refitted without delinq_max_6m |
| `ablation.limit_bal.delta_auc` | `4b976d60` | scalar | 0.0006174556236 | change in test AUC when the champion's form is refitted without limit_bal |
| `ablation.pay_amt_next.delta_auc` | `cf6c0563` | scalar | -0.2275170885 | change in test AUC when the champion's form is refitted without pay_amt_next |
| `ablation.pay_ratio_last.delta_auc` | `c577925a` | scalar | 0.0001862572749 | change in test AUC when the champion's form is refitted without pay_ratio_last |
| `ablation.pay_ratio_mean_6m.delta_auc` | `54c168fb` | scalar | -0.0009593525391 | change in test AUC when the champion's form is refitted without pay_ratio_mean_6m |
| `ablation.utilisation.delta_auc` | `009bc4f1` | scalar | -0.0004235439401 | change in test AUC when the champion's form is refitted without utilisation |
| `calibration.mean_rel_gap.test` | `6a845d81` | scalar | 0.0371730842 | mean predicted against observed on test, relative |
| `calibration.mean_rel_gap.train` | `f7447f34` | scalar | 8.631936949e-05 | mean predicted against observed on train, relative |
| `calibration.test` | `1744d380` | table | table, 10 rows | calibration by decile of predicted probability on test |
| `calibration.train` | `309e30bb` | table | table, 10 rows | calibration by decile of predicted probability on train |
| `calibration_intercept.test` | `56745cf2` | scalar | -0.05579737693 | logistic regression of the outcome on logit(p) on test: the intercept |
| `calibration_intercept.train` | `d556f341` | scalar | 0.2245889138 | logistic regression of the outcome on logit(p) on train: the intercept |
| `calibration_slope.test` | `c9a03fe6` | scalar | 1.19744242 | logistic regression of the outcome on logit(p) on test: the slope |
| `calibration_slope.train` | `45dafd11` | scalar | 1.383137681 | logistic regression of the outcome on logit(p) on train: the slope |
| `challenger.auc` | `d2646bc7` | scalar | 0.9877299831 | the challenger's AUC on test |
| `challenger.brier` | `0a224a0a` | scalar | 0.02542316584 | the challenger's Brier score on test |
| `challenger.delta_auc` | `2ab4af27` | scalar | 0.01222409046 | the challenger's AUC on test minus the champion's |
| `condition_number` | `36392379` | scalar | 6.185189657 | Belsley's condition number of the column-standardised design |
| `csi.age` | `584faff4` | scalar | 0.00125000439 | CSI of age: its contribution to the shift in the linear predictor |
| `csi.bill_mean_6m` | `f374dbd7` | scalar | 0.01049921023 | CSI of bill_mean_6m: its contribution to the shift in the linear predictor |
| `csi.bill_trend_6m` | `8bb46253` | scalar | 0.005670244137 | CSI of bill_trend_6m: its contribution to the shift in the linear predictor |
| `csi.delinq_count_6m` | `4564aa47` | scalar | 0.00214274047 | CSI of delinq_count_6m: its contribution to the shift in the linear predictor |
| `csi.delinq_last` | `cd29d613` | scalar | 0.02950471301 | CSI of delinq_last: its contribution to the shift in the linear predictor |
| `csi.delinq_max_6m` | `2fe28db6` | scalar | 0.002782289452 | CSI of delinq_max_6m: its contribution to the shift in the linear predictor |
| `csi.limit_bal` | `cb617a64` | scalar | 0.007188476411 | CSI of limit_bal: its contribution to the shift in the linear predictor |
| `csi.max` | `3f7f79cf` | scalar | 0.4063916509 | the largest characteristic stability index |
| `csi.pay_amt_next` | `e708fa25` | scalar | 0.4063916509 | CSI of pay_amt_next: its contribution to the shift in the linear predictor |
| `csi.pay_ratio_last` | `c083b28c` | scalar | 0.003912462231 | CSI of pay_ratio_last: its contribution to the shift in the linear predictor |
| `csi.pay_ratio_mean_6m` | `8f1dbe89` | scalar | 0.003518997237 | CSI of pay_ratio_mean_6m: its contribution to the shift in the linear predictor |
| `csi.utilisation` | `b1f362df` | scalar | 0.01304415209 | CSI of utilisation: its contribution to the shift in the linear predictor |
| `deciles.test` | `ffdb3017` | table | table, 10 rows | decile separation on test; decile 1 holds the highest probabilities |
| `deciles.test.top2_capture` | `5690757b` | scalar | 0.821958457 | share of test events in the top two deciles |
| `deciles.train.top2_capture` | `55242963` | scalar | 0.8422391858 | share of train events in the top two deciles |
| `leakage.duplicates.train` | `4474c227` | scalar | 0 | share of train rows whose feature values are not unique within train |
| `leakage.name_screen.n_matched` | `407e62be` | scalar | 0 | feature names matching the target-adjacent lexicon |
| `leakage.overlap` | `4c9fcd09` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.features` | `0fec8048` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.ids` | `63d37fc5` | scalar | 0 | share of test rows whose ['client_id'] also identify a row of train |
| `leakage.target_corr` | `12cb4333` | table | table, 11 rows | each feature against the outcome on train, on its own |
| `leakage.target_corr.max_single_feature_auc` | `5b5e98c2` | scalar | 0.9449621321 | the AUC of the strongest single feature |
| `leakage.timing` | `878d82fa` | table | table, 13 rows | each feature's declared timing; flagged means during or after the outcome |
| `leakage.timing.n_flagged` | `742bcd24` | scalar | 0 | features declared during_period or after_outcome |
| `metrics.test.auc` | `8f522f3b` | scalar | 0.9755058926 | auc on test, recomputed by quaestor |
| `metrics.test.brier` | `d4f27e13` | scalar | 0.04247487168 | brier on test, recomputed by quaestor |
| `metrics.test.event_rate` | `9209d200` | scalar | 0.2246666667 | event_rate on test, recomputed by quaestor |
| `metrics.test.gini` | `f927e3cd` | scalar | 0.9510117852 | gini on test, recomputed by quaestor |
| `metrics.test.ks` | `81bee194` | scalar | 0.8784403377 | ks on test, recomputed by quaestor |
| `metrics.test.logloss` | `aa620b5e` | scalar | 0.1670045909 | logloss on test, recomputed by quaestor |
| `metrics.test.mean_predicted` | `0b9b6a1e` | scalar | 0.2330182196 | mean_predicted on test, recomputed by quaestor |
| `metrics.test.n` | `64fcf14d` | scalar | 1500 | n on test, recomputed by quaestor |
| `metrics.test.sub.limit_bal_high` | `be320de3` | table | table, 10 rows | every metric on the limit_bal above_median slice of test |
| `metrics.test.sub.limit_bal_high.auc_gap` | `e37bc8d6` | scalar | -0.005860076588 | how far AUC on the limit_bal above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.limit_bal_high.event_rate` | `5e9aab40` | scalar | 0.2002688172 | event_rate on the limit_bal above_median slice of test |
| `metrics.test.sub.limit_bal_high.mean_predicted` | `f80c93c0` | scalar | 0.2071684221 | mean_predicted on the limit_bal above_median slice of test |
| `metrics.test.sub.limit_bal_high.mean_rel_gap` | `679e4d84` | scalar | 0.03445171844 | mean predicted against observed on the limit_bal above_median slice of test, relative |
| `metrics.test.sub.limit_bal_high.share` | `ac383ccb` | scalar | 0.496 | the share of test the limit_bal above_median slice holds |
| `metrics.test.sub.limit_bal_low` | `668296df` | table | table, 10 rows | every metric on the limit_bal below_median slice of test |
| `metrics.test.sub.limit_bal_low.auc_gap` | `6990b76c` | scalar | 0.008535185397 | how far AUC on the limit_bal below_median slice of test falls below AUC on all of test |
| `metrics.test.sub.limit_bal_low.event_rate` | `de78adb5` | scalar | 0.2486772487 | event_rate on the limit_bal below_median slice of test |
| `metrics.test.sub.limit_bal_low.mean_predicted` | `c1a37d64` | scalar | 0.2584577028 | mean_predicted on the limit_bal below_median slice of test |
| `metrics.test.sub.limit_bal_low.mean_rel_gap` | `2b29e325` | scalar | 0.03932991131 | mean predicted against observed on the limit_bal below_median slice of test, relative |
| `metrics.test.sub.limit_bal_low.share` | `bac689cc` | scalar | 0.504 | the share of test the limit_bal below_median slice holds |
| `metrics.test.sub.pay_amt_next_high` | `c78a69bf` | table | table, 10 rows | every metric on the pay_amt_next above_median slice of test |
| `metrics.test.sub.pay_amt_next_high.auc` | `e2b8b0f2` | scalar | 0.8820649435 | auc on the pay_amt_next above_median slice of test |
| `metrics.test.sub.pay_amt_next_high.auc_gap` | `ad693cad` | scalar | 0.09344094914 | how far AUC on the pay_amt_next above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.pay_amt_next_high.event_rate` | `9702492a` | scalar | 0.02533333333 | event_rate on the pay_amt_next above_median slice of test |
| `metrics.test.sub.pay_amt_next_high.mean_predicted` | `dcacb7a5` | scalar | 0.02084997678 | mean_predicted on the pay_amt_next above_median slice of test |
| `metrics.test.sub.pay_amt_next_high.mean_rel_gap` | `5a35c2f9` | scalar | 0.1769746007 | mean predicted against observed on the pay_amt_next above_median slice of test, relative |
| `metrics.test.sub.pay_amt_next_high.share` | `21c17ed0` | scalar | 0.5 | the share of test the pay_amt_next above_median slice holds |
| `metrics.test.sub.pay_amt_next_low` | `369588e4` | table | table, 10 rows | every metric on the pay_amt_next below_median slice of test |
| `metrics.test.sub.pay_amt_next_low.auc_gap` | `cd5172fc` | scalar | 0.008772256467 | how far AUC on the pay_amt_next below_median slice of test falls below AUC on all of test |
| `metrics.test.sub.pay_amt_next_low.event_rate` | `c5cd207d` | scalar | 0.424 | event_rate on the pay_amt_next below_median slice of test |
| `metrics.test.sub.pay_amt_next_low.mean_predicted` | `036756aa` | scalar | 0.4451864624 | mean_predicted on the pay_amt_next below_median slice of test |
| `metrics.test.sub.pay_amt_next_low.mean_rel_gap` | `a89da41c` | scalar | 0.04996807166 | mean predicted against observed on the pay_amt_next below_median slice of test, relative |
| `metrics.test.sub.pay_amt_next_low.share` | `18eac95f` | scalar | 0.5 | the share of test the pay_amt_next below_median slice holds |
| `metrics.train.auc` | `da2cd01d` | scalar | 0.9811790152 | auc on train, recomputed by quaestor |
| `metrics.train.brier` | `959b3159` | scalar | 0.03816687592 | brier on train, recomputed by quaestor |
| `metrics.train.event_rate` | `133a5ff8` | scalar | 0.2245714286 | event_rate on train, recomputed by quaestor |
| `metrics.train.gini` | `23cb4057` | scalar | 0.9623580305 | gini on train, recomputed by quaestor |
| `metrics.train.ks` | `7a126f15` | scalar | 0.8894536106 | ks on train, recomputed by quaestor |
| `metrics.train.logloss` | `417d98d9` | scalar | 0.1504741108 | logloss on train, recomputed by quaestor |
| `metrics.train.mean_predicted` | `1fa024a6` | scalar | 0.2245520437 | mean_predicted on train, recomputed by quaestor |
| `metrics.train.n` | `564683ee` | scalar | 3500 | n on train, recomputed by quaestor |
| `metrics.train.sub.limit_bal_high` | `1d76466a` | table | table, 10 rows | every metric on the limit_bal above_median slice of train |
| `metrics.train.sub.limit_bal_high.auc_gap` | `52a49712` | scalar | -0.006441907569 | how far AUC on the limit_bal above_median slice of train falls below AUC on all of train |
| `metrics.train.sub.limit_bal_high.event_rate` | `9de459ef` | scalar | 0.2049510651 | event_rate on the limit_bal above_median slice of train |
| `metrics.train.sub.limit_bal_high.mean_predicted` | `b1995539` | scalar | 0.203016396 | mean_predicted on the limit_bal above_median slice of train |
| `metrics.train.sub.limit_bal_high.mean_rel_gap` | `58ae0f50` | scalar | 0.009439663314 | mean predicted against observed on the limit_bal above_median slice of train, relative |
| `metrics.train.sub.limit_bal_high.share` | `2de2a90a` | scalar | 0.4962857143 | the share of train the limit_bal above_median slice holds |
| `metrics.train.sub.limit_bal_low` | `81d20ff9` | table | table, 10 rows | every metric on the limit_bal below_median slice of train |
| `metrics.train.sub.limit_bal_low.auc_gap` | `999aab9c` | scalar | 0.008866169575 | how far AUC on the limit_bal below_median slice of train falls below AUC on all of train |
| `metrics.train.sub.limit_bal_low.event_rate` | `0ae85aa6` | scalar | 0.243902439 | event_rate on the limit_bal below_median slice of train |
| `metrics.train.sub.limit_bal_low.mean_predicted` | `2086a25d` | scalar | 0.2457700925 | mean_predicted on the limit_bal below_median slice of train |
| `metrics.train.sub.limit_bal_low.mean_rel_gap` | `a93d065e` | scalar | 0.007657379338 | mean predicted against observed on the limit_bal below_median slice of train, relative |
| `metrics.train.sub.limit_bal_low.share` | `45c51f9e` | scalar | 0.5037142857 | the share of train the limit_bal below_median slice holds |
| `metrics.train.sub.pay_amt_next_high` | `ad425b34` | table | table, 10 rows | every metric on the pay_amt_next above_median slice of train |
| `metrics.train.sub.pay_amt_next_high.auc` | `649333b3` | scalar | 0.8745155039 | auc on the pay_amt_next above_median slice of train |
| `metrics.train.sub.pay_amt_next_high.auc_gap` | `30718a8b` | scalar | 0.1066635114 | how far AUC on the pay_amt_next above_median slice of train falls below AUC on all of train |
| `metrics.train.sub.pay_amt_next_high.event_rate` | `81517b8d` | scalar | 0.01714285714 | event_rate on the pay_amt_next above_median slice of train |
| `metrics.train.sub.pay_amt_next_high.mean_predicted` | `968cddfe` | scalar | 0.02031609448 | mean_predicted on the pay_amt_next above_median slice of train |
| `metrics.train.sub.pay_amt_next_high.mean_rel_gap` | `2d65d0bd` | scalar | 0.1851055113 | mean predicted against observed on the pay_amt_next above_median slice of train, relative |
| `metrics.train.sub.pay_amt_next_high.share` | `c4cc28b1` | scalar | 0.5 | the share of train the pay_amt_next above_median slice holds |
| `metrics.train.sub.pay_amt_next_low` | `51a4a15f` | table | table, 10 rows | every metric on the pay_amt_next below_median slice of train |
| `metrics.train.sub.pay_amt_next_low.auc_gap` | `4b2a3b88` | scalar | 0.003166761813 | how far AUC on the pay_amt_next below_median slice of train falls below AUC on all of train |
| `metrics.train.sub.pay_amt_next_low.event_rate` | `20cb26cd` | scalar | 0.432 | event_rate on the pay_amt_next below_median slice of train |
| `metrics.train.sub.pay_amt_next_low.mean_predicted` | `9ebffd6f` | scalar | 0.4287879929 | mean_predicted on the pay_amt_next below_median slice of train |
| `metrics.train.sub.pay_amt_next_low.mean_rel_gap` | `3afbd6e4` | scalar | 0.007435201539 | mean predicted against observed on the pay_amt_next below_median slice of train, relative |
| `metrics.train.sub.pay_amt_next_low.share` | `01d5682e` | scalar | 0.5 | the share of train the pay_amt_next below_median slice holds |
| `profile.test.missing.max` | `f813848d` | scalar | 0 | the largest missing fraction in test |
| `profile.test.n` | `2193cf5f` | scalar | 1500 | rows in test |
| `profile.train.missing.max` | `050a3099` | scalar | 0 | the largest missing fraction in train |
| `profile.train.n` | `2510d49d` | scalar | 3500 | rows in train |
| `psi.age` | `f9255a0a` | scalar | 0.008124281436 | PSI of age between train and test |
| `psi.bill_mean_6m` | `028e4281` | scalar | 0.007124196275 | PSI of bill_mean_6m between train and test |
| `psi.bill_trend_6m` | `c247a6f2` | scalar | 0.009579614525 | PSI of bill_trend_6m between train and test |
| `psi.delinq_count_6m` | `61491d02` | scalar | 0.002069275496 | PSI of delinq_count_6m between train and test |
| `psi.delinq_last` | `03bd52e7` | scalar | 0.002849633848 | PSI of delinq_last between train and test |
| `psi.delinq_max_6m` | `7a82e7f3` | scalar | 0.005498249408 | PSI of delinq_max_6m between train and test |
| `psi.limit_bal` | `601cdba2` | scalar | 0.01095273358 | PSI of limit_bal between train and test |
| `psi.max` | `1b87de3e` | scalar | 0.01789488592 | the largest train-to-test PSI, score included |
| `psi.pay_amt_next` | `996bb509` | scalar | 0.01789488592 | PSI of pay_amt_next between train and test |
| `psi.pay_ratio_last` | `3af2ca29` | scalar | 0.00496591109 | PSI of pay_ratio_last between train and test |
| `psi.pay_ratio_mean_6m` | `2c5baeb2` | scalar | 0.005500252946 | PSI of pay_ratio_mean_6m between train and test |
| `psi.utilisation` | `451e0780` | scalar | 0.0042440485 | PSI of utilisation between train and test |
| `psi.y_score` | `05f120d2` | scalar | 0.01198828928 | PSI of the score between train and test |
| `rule.calibration_first_event_rate` | `42f1351e` | scalar | 0.05 | the event rate below which the report puts calibration before discrimination |
| `run.features` | `b85c116d` | json | json | the subject's features.json |
| `run.model_summary` | `e4b3fd0e` | json | json | the subject's model_summary.json |
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |
| `sign_check.age.coef_sign` | `6172eb93` | scalar | -1 | the sign of the fitted coefficient on age |
| `sign_check.age.univariate_direction` | `66364583` | scalar | -1 | the sign of age's own single-feature AUC on train minus 0.5 |
| `sign_check.bill_mean_6m.agrees` | `4df8b747` | scalar | 0 | 1 when the fitted sign on bill_mean_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.bill_mean_6m.coef_sign` | `a457c04a` | scalar | 1 | the sign of the fitted coefficient on bill_mean_6m |
| `sign_check.bill_mean_6m.univariate_direction` | `23b89c5d` | scalar | -1 | the sign of bill_mean_6m's own single-feature AUC on train minus 0.5 |
| `sign_check.bill_trend_6m.agrees` | `c0f6d07d` | scalar | 0 | 1 when the fitted sign on bill_trend_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.bill_trend_6m.coef_sign` | `abd4aaba` | scalar | 1 | the sign of the fitted coefficient on bill_trend_6m |
| `sign_check.bill_trend_6m.univariate_direction` | `a9bff389` | scalar | -1 | the sign of bill_trend_6m's own single-feature AUC on train minus 0.5 |
| `sign_check.delinq_count_6m.coef_sign` | `17afb6f9` | scalar | 1 | the sign of the fitted coefficient on delinq_count_6m |
| `sign_check.delinq_count_6m.univariate_direction` | `549e904e` | scalar | 1 | the sign of delinq_count_6m's own single-feature AUC on train minus 0.5 |
| `sign_check.delinq_last.coef_sign` | `50d352f8` | scalar | 1 | the sign of the fitted coefficient on delinq_last |
| `sign_check.delinq_last.univariate_direction` | `a78648ba` | scalar | 1 | the sign of delinq_last's own single-feature AUC on train minus 0.5 |
| `sign_check.delinq_max_6m.agrees` | `c946359c` | scalar | 0 | 1 when the fitted sign on delinq_max_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.delinq_max_6m.coef_sign` | `a07d68ab` | scalar | -1 | the sign of the fitted coefficient on delinq_max_6m |
| `sign_check.delinq_max_6m.univariate_direction` | `b9088f4a` | scalar | 1 | the sign of delinq_max_6m's own single-feature AUC on train minus 0.5 |
| `sign_check.limit_bal.agrees` | `0278aad1` | scalar | 0 | 1 when the fitted sign on limit_bal agrees with its univariate direction, 0 when it does not |
| `sign_check.limit_bal.coef_sign` | `6af6aef2` | scalar | 1 | the sign of the fitted coefficient on limit_bal |
| `sign_check.limit_bal.univariate_direction` | `56d284d6` | scalar | -1 | the sign of limit_bal's own single-feature AUC on train minus 0.5 |
| `sign_check.n_disagreements` | `75159a84` | scalar | 6 | retained features whose fitted sign contradicts their univariate direction, of 11 checked |
| `sign_check.pay_amt_next.coef_sign` | `6fc540c1` | scalar | -1 | the sign of the fitted coefficient on pay_amt_next |
| `sign_check.pay_amt_next.univariate_direction` | `1bec400a` | scalar | -1 | the sign of pay_amt_next's own single-feature AUC on train minus 0.5 |
| `sign_check.pay_ratio_last.agrees` | `79abee77` | scalar | 0 | 1 when the fitted sign on pay_ratio_last agrees with its univariate direction, 0 when it does not |
| `sign_check.pay_ratio_last.coef_sign` | `f018263e` | scalar | 1 | the sign of the fitted coefficient on pay_ratio_last |
| `sign_check.pay_ratio_last.univariate_direction` | `f8e46d75` | scalar | -1 | the sign of pay_ratio_last's own single-feature AUC on train minus 0.5 |
| `sign_check.pay_ratio_mean_6m.agrees` | `51914c14` | scalar | 0 | 1 when the fitted sign on pay_ratio_mean_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.pay_ratio_mean_6m.coef_sign` | `8547787e` | scalar | 1 | the sign of the fitted coefficient on pay_ratio_mean_6m |
| `sign_check.pay_ratio_mean_6m.univariate_direction` | `24dcef24` | scalar | -1 | the sign of pay_ratio_mean_6m's own single-feature AUC on train minus 0.5 |
| `sign_check.utilisation.coef_sign` | `85badc3c` | scalar | 1 | the sign of the fitted coefficient on utilisation |
| `sign_check.utilisation.univariate_direction` | `f0995196` | scalar | 1 | the sign of utilisation's own single-feature AUC on train minus 0.5 |
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
| `threshold.S1.psi` | `278b9016` | scalar | 0.25 | S1: the population stability index, train against test |
| `threshold.package.auc.test.min` | `8bfd02cc` | scalar | 0.7 | package.yaml declares auc min 0.7 |
| `threshold.package.brier.test.max` | `d0f98b9c` | scalar | 0.2 | package.yaml declares brier max 0.2 |
| `threshold.package.calibration_slope.test.max` | `0adb7a89` | scalar | 1.2 | package.yaml declares calibration_slope max 1.2 |
| `threshold.package.calibration_slope.test.min` | `95fdb848` | scalar | 0.8 | package.yaml declares calibration_slope min 0.8 |
| `threshold.package.psi.max` | `fbb5a9d1` | scalar | 0.25 | package.yaml declares psi max 0.25 |
| `thresholds.evaluation` | `f41614b5` | table | table, 5 rows | every threshold package.yaml declares, with its bound, the recomputed value and the outcome |
| `vif.age` | `8021b06e` | scalar | 1.002328679 | variance inflation factor of age on train |
| `vif.bill_mean_6m` | `d5ab7306` | scalar | 8.181114607 | variance inflation factor of bill_mean_6m on train |
| `vif.bill_trend_6m` | `0cb3df89` | scalar | 1.225337779 | variance inflation factor of bill_trend_6m on train |
| `vif.delinq_count_6m` | `87890613` | scalar | 2.56148636 | variance inflation factor of delinq_count_6m on train |
| `vif.delinq_last` | `c18221d4` | scalar | 1.422439811 | variance inflation factor of delinq_last on train |
| `vif.delinq_max_6m` | `4b239ec5` | scalar | 2.408148028 | variance inflation factor of delinq_max_6m on train |
| `vif.limit_bal` | `8209ea46` | scalar | 4.809808481 | variance inflation factor of limit_bal on train |
| `vif.max` | `4afdc4f1` | scalar | 8.181114607 | the largest variance inflation factor |
| `vif.pay_amt_next` | `68806d80` | scalar | 2.206074628 | variance inflation factor of pay_amt_next on train |
| `vif.pay_ratio_last` | `bec24796` | scalar | 7.267755553 | variance inflation factor of pay_ratio_last on train |
| `vif.pay_ratio_mean_6m` | `000b6208` | scalar | 7.525569541 | variance inflation factor of pay_ratio_mean_6m on train |
| `vif.utilisation` | `ec978947` | scalar | 3.215174221 | variance inflation factor of utilisation on train |

## Appendix C — Run trace summary

| quantity | value |
|---|---|
| tool calls | 17 (run_model 1, profile_data 1, compute_metrics 5, check_leakage 1, check_collinearity 1, challenger_compare 1, retrieve_guidance 7) |
| plan steps (bounded loop) | 4 |
| LLM calls | 20 (plan 4, draft 8, extract 8) |
| re-asks | 0 |
| repair rounds | 1 |
| tokens in / out | 257,249 / 110,961 |
| notional cost (USD) | 5.3994 |
| wall-clock (s) | 1215.58 |
| subject run (s) | 1.36 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | credit_default-full_agent-20260920T071109Z-e2e51e00 |

## Appendix D — Not checked

| item | reason |
|---|---|
| `check_stability` (R1) | package declares no `regime.column` |
| `run_scenarios` (X1) | not applicable to `binary_classification` |
| out-of-time and vintage-holdout metrics (O1, second rule) | package declares neither split |
| developer claims (T1, claim channel) | The package declares 2 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
