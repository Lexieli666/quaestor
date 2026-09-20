---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: full_agent
model: claude-opus-5[1m]
run_id: credit_default-full_agent-20260920T065312Z-e2e51e00
data_mode: synthetic
synthetic_n: 5000
grounding_precision_pre: 0.9922
grounding_precision_post: 1.0000
n_claims: 258
n_findings_by_severity: {high: 1, medium: 1, low: 0, info: 0}
generated: "2026-09-20T06:53:12Z"
illustrative: false
---

# Validation report — `credit_default` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `credit_default` v1.0 | `full_agent` | claude-opus-5[1m] | synthetic, n = 5000 | 0.9922 → 1.0000 | 1 / 1 / 0 / 0 |
<!-- quaestor:renderer:end -->

The credit_default model package, version 1.0, is a binary classification model that predicts the probability that a borrower defaults, and this report is organised around the Federal Reserve's model risk management guidance on model validation and monitoring [[reg:SR26-2:V]].
The subject was loaded from its package and scored by the validation harness, with the performance figures below recomputed independently from the scored outputs rather than taken from the developer's own reporting, under a declared wall-clock cap of 300 seconds [[art:2ad8d1a5:runtime.max_seconds]].
The development split holds 3500 rows [[art:2510d49d:profile.train.n]] and the holdout split holds 1500 rows [[art:2193cf5f:profile.test.n]].

On the holdout split, discrimination measured by the area under the ROC curve is 0.9755 [[art:8f522f3b:metrics.test.auc]], above the developer-declared floor of 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]].
The Brier score on the holdout split is 0.04247 [[art:d4f27e13:metrics.test.brier]], below the developer-declared ceiling of 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]].
The largest train-to-test population stability index, score included, is 0.01789 [[art:1b87de3e:psi.max]], below the developer-declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
The slope of the outcome regressed on the logit of the predicted probability, on the holdout split, is 1.197 [[art:c9a03fe6:calibration_slope.test]], above the developer-declared floor of 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] and below the developer-declared ceiling of 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]], though it sits nearer the ceiling than the floor.
The model therefore passes each of the developer-declared thresholds cited above, with the calibration bound the narrowest of the passes.

This validation raised F-001, a L1 leakage finding at high severity, and F-002, a C1 calibration finding at medium severity.
Each is written out in full, with its evidence and its disposition, in the findings section of this report.

## 2. Conceptual soundness

Conceptual soundness is assessed here as an evaluation of model design, construction, and developmental evidence, with modeling choices subjected to critical analysis [[reg:SR26-2:V.1.a]].

### Design and feature set

The champion is a regression carrying one fitted coefficient per retained feature over an intercept of -6.103 [[art:e4b3fd0e:run.model_summary#intercept]], estimated on a training sample of 3500 [[art:e4b3fd0e:run.model_summary#n_train]] rows.
The declared feature set counts 13 [[art:7276ca89:run.features#n]] features in total.
Of these, 2 [[art:7276ca89:run.features#at_origination]] are known at origination and 10 [[art:7276ca89:run.features#before_period_start]] are known before the performance period starts, which are the timings a scoring-time model can rely on.
None are timed during the period, at 0 [[art:7276ca89:run.features#during_period]].
One feature, 1 [[art:7276ca89:run.features#after_outcome]] of the set, is timed after the outcome, meaning its value is not available at the moment the score would be used.
That feature is pay_amt_next, and it carries the largest coefficient in the model by magnitude at -12.37 [[art:e4b3fd0e:run.model_summary#coefficients.pay_amt_next.value]], far above the next largest, bill_mean_6m at 1.651 [[art:e4b3fd0e:run.model_summary#coefficients.bill_mean_6m.value]].
Refitting the champion's functional form without pay_amt_next changes test AUC by -0.2275 [[art:cf6c0563:ablation.pay_amt_next.delta_auc]] against a refit baseline of 0.9755 [[art:8e58476a:ablation.baseline_auc]], so the model's discrimination rests substantially on information whose timing sits after the outcome.
That combination of timing and weight is the central design question for this champion, and the developmental evidence reviewed here does not resolve why a post-outcome quantity was admitted to the specification.

### The developer's own screen

The developer applied a collinearity screen at a variance inflation threshold of 10 [[art:e4b3fd0e:run.model_summary#vif_threshold]], removing bill_last, whose inflation factor was 162.9 [[art:e4b3fd0e:run.model_summary#removed.bill_last.vif]], and utilisation_mean_6m, at 36.78 [[art:e4b3fd0e:run.model_summary#removed.utilisation_mean_6m.vif]].
Both removed features sit above the declared threshold, the first by a wide margin and the second by less, so the screen acted as designed on the variables it flagged.
Removing near-duplicate balance and utilisation aggregates is a defensible choice, since it protects the interpretability of the coefficients that remain, which is what the sign review below depends on.

### Coefficient magnitudes and expected signs

Among the retained features, the largest coefficients after pay_amt_next and bill_mean_6m are delinq_last at 0.9159 [[art:e4b3fd0e:run.model_summary#coefficients.delinq_last.value]], utilisation at 0.8591 [[art:e4b3fd0e:run.model_summary#coefficients.utilisation.value]], pay_ratio_mean_6m at 0.7072 [[art:e4b3fd0e:run.model_summary#coefficients.pay_ratio_mean_6m.value]] and limit_bal at 0.4311 [[art:e4b3fd0e:run.model_summary#coefficients.limit_bal.value]].
The smaller weights are pay_ratio_last at 0.2086 [[art:e4b3fd0e:run.model_summary#coefficients.pay_ratio_last.value]], bill_trend_6m at 0.1993 [[art:e4b3fd0e:run.model_summary#coefficients.bill_trend_6m.value]], delinq_count_6m at 0.1073 [[art:e4b3fd0e:run.model_summary#coefficients.delinq_count_6m.value]], delinq_max_6m at -0.09998 [[art:e4b3fd0e:run.model_summary#coefficients.delinq_max_6m.value]] and age at -0.08872 [[art:e4b3fd0e:run.model_summary#coefficients.age.value]].
On subject matter grounds the recent-delinquency and utilisation weights are the ones a credit reviewer would expect to be positive, and they are: delinq_last takes a fitted sign of +1 [[art:50d352f8:sign_check.delinq_last.coef_sign]] and utilisation +1 [[art:85badc3c:sign_check.utilisation.coef_sign]], each matching its own direction against the outcome on train at +1 [[art:a78648ba:sign_check.delinq_last.univariate_direction]] and +1 [[art:f0995196:sign_check.utilisation.univariate_direction]] respectively.
The negative weight on age, at a fitted sign of -1 [[art:6172eb93:sign_check.age.coef_sign]], agrees with its direction on train at -1 [[art:66364583:sign_check.age.univariate_direction]] and is consistent with the usual expectation that default risk falls with borrower age.
The negative weight on delinq_max_6m is the one that reads against subject matter expectation, since a higher worst delinquency over six months would be expected to raise risk rather than lower it.

### Fitted signs against univariate directions

The count of retained features whose fitted sign contradicts the direction of that feature's own relationship with the outcome on train is 6 [[art:75159a84:sign_check.n_disagreements]].
Each of these is set out below with the change in test AUC when the champion's form is refitted without it, which is the measure of how much the model actually leans on the feature whose sign is in question.
On limit_bal the fitted sign is +1 [[art:6af6aef2:sign_check.limit_bal.coef_sign]] while its direction on train is -1 [[art:56d284d6:sign_check.limit_bal.univariate_direction]], and dropping it changes test AUC by 0.0006175 [[art:4b976d60:ablation.limit_bal.delta_auc]], an improvement rather than a loss, so the model gains nothing from it.
On pay_ratio_last the fitted sign is +1 [[art:f018263e:sign_check.pay_ratio_last.coef_sign]] against a direction on train of -1 [[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]], and dropping it changes test AUC by 0.0001863 [[art:c577925a:ablation.pay_ratio_last.delta_auc]], again not a loss.
On delinq_max_6m the fitted sign is -1 [[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]] against a direction on train of +1 [[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]], and dropping it changes test AUC by 0.0001607 [[art:b1793491:ablation.delinq_max_6m.delta_auc]].
These three carry sign reversals on features the model barely uses, which points to collinearity among the balance and repayment aggregates that survived the screen rather than to a weight the model is relying on.
On pay_ratio_mean_6m the fitted sign is +1 [[art:8547787e:sign_check.pay_ratio_mean_6m.coef_sign]] against a direction on train of -1 [[art:24dcef24:sign_check.pay_ratio_mean_6m.univariate_direction]], and dropping it changes test AUC by -0.0009594 [[art:54c168fb:ablation.pay_ratio_mean_6m.delta_auc]], so here the reversed weight is carrying some discrimination.
On bill_trend_6m the fitted sign is +1 [[art:abd4aaba:sign_check.bill_trend_6m.coef_sign]] against a direction on train of -1 [[art:a9bff389:sign_check.bill_trend_6m.univariate_direction]], with a change on removal of -0.0005537 [[art:54e6a418:ablation.bill_trend_6m.delta_auc]].
On bill_mean_6m the fitted sign is +1 [[art:a457c04a:sign_check.bill_mean_6m.coef_sign]] against a direction on train of -1 [[art:23b89c5d:sign_check.bill_mean_6m.univariate_direction]], and dropping it changes test AUC by -0.005228 [[art:a4586b58:ablation.bill_mean_6m.delta_auc]], the largest such loss among the reversed features and larger in magnitude than the losses on pay_ratio_mean_6m and bill_trend_6m.
That matters because bill_mean_6m also carries the largest coefficient of any feature available before the performance period, so the model both leans on it and weights it in the direction opposite to its standalone relationship with the outcome.
For completeness on the features whose signs do agree, removing delinq_last changes test AUC by -0.0009211 [[art:43d4225a:ablation.delinq_last.delta_auc]] and removing utilisation by -0.0004235 [[art:009bc4f1:ablation.utilisation.delta_auc]], while removing age changes it by 5.613e-05 [[art:786b509d:ablation.age.delta_auc]] and removing delinq_count_6m by 5.103e-06 [[art:3730f6e2:ablation.delinq_count_6m.delta_auc]], both of the latter being gains rather than losses.
Taken together the sign evidence says the specification is not behaving as an interpretable credit scorecard for the balance and repayment block, whatever its discrimination.

### Effective challenge

The challenger reaches an AUC on test of 0.9877 [[art:d2646bc7:challenger.auc]] against the champion's 0.9755 [[art:8f522f3b:metrics.test.auc]], an advantage to the challenger of 0.01222 [[art:2ab4af27:challenger.delta_auc]].
The threshold declared for deciding whether a challenger's lead in AUC matters is 0.03 [[art:e042774c:threshold.E1.delta_auc]], and the observed lead falls below it, so on the declared criterion the challenger does not displace the champion on discrimination.
On calibration the challenger's Brier score of 0.02542 [[art:0a224a0a:challenger.brier]] is lower, and so better, than the champion's 0.04247 [[art:d4f27e13:metrics.test.brier]]; no threshold was declared to this section for that comparison, and the ordering is reported here as evidence rather than as a decision.
The effective challenge is therefore inconclusive as a ranking exercise: the challenger does not beat the champion by the declared margin on discrimination while ranking better on calibration, and both models are being compared on a test set that the champion scores using a feature timed after the outcome.
Any weight placed on the champion's margin over the challenger should be read in light of that timing, since the discrimination being compared is not discrimination the champion could reproduce at scoring time.

## 3. Data integrity and drift

Sound model testing includes a critical assessment of data quality, relevance, and inputs [[reg:SR26-2:IV.1]], and this section reviews the package's data on that basis: missingness within and between splits, population and characteristic stability from the training split outward, and the leakage screens.

### Missingness

The training split holds 3500 [[art:2510d49d:profile.train.n]] rows and its largest missing fraction across features is 0 [[art:050a3099:profile.train.missing.max]].
The test split holds 1500 [[art:2193cf5f:profile.test.n]] rows and its largest missing fraction across features is 0 [[art:f813848d:profile.test.missing.max]].
The two splits report the same largest missing fraction, so the gap between them lies below the declared bound on the between-split missingness gap of 0.1 [[art:9cce25ea:threshold.D1.missing_gap]], and neither split shows missingness that would need imputation review.

### Population stability, train against test

The declared stability bound is 0.25 [[art:278b9016:threshold.S1.psi]], which the package restates at 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
The largest train-to-test population stability index, the score included, is 0.01789 [[art:1b87de3e:psi.max]], far below that bound.
The score's own train-to-test shift is 0.01199 [[art:05f120d2:psi.y_score]], also below the bound.
The per-feature train-to-test shifts are as follows.

- age: 0.008124 [[art:f9255a0a:psi.age]]
- bill_mean_6m: 0.007124 [[art:028e4281:psi.bill_mean_6m]]
- bill_trend_6m: 0.00958 [[art:c247a6f2:psi.bill_trend_6m]]
- delinq_count_6m: 0.002069 [[art:61491d02:psi.delinq_count_6m]]
- delinq_last: 0.00285 [[art:03bd52e7:psi.delinq_last]]
- delinq_max_6m: 0.005498 [[art:7a82e7f3:psi.delinq_max_6m]]
- limit_bal: 0.01095 [[art:601cdba2:psi.limit_bal]]
- pay_amt_next: 0.01789 [[art:996bb509:psi.pay_amt_next]]
- pay_ratio_last: 0.004966 [[art:3af2ca29:psi.pay_ratio_last]]
- pay_ratio_mean_6m: 0.0055 [[art:2c5baeb2:psi.pay_ratio_mean_6m]]
- utilisation: 0.004244 [[art:451e0780:psi.utilisation]]

Every one of these marginal shifts sits below the declared bound of 0.25 [[art:278b9016:threshold.S1.psi]], so the test split is drawn from a population the training split recognises.

### Characteristic stability

The per-feature contributions to the shift in the linear predictor are as follows.

- age: 0.00125 [[art:584faff4:csi.age]]
- bill_mean_6m: 0.0105 [[art:f374dbd7:csi.bill_mean_6m]]
- bill_trend_6m: 0.00567 [[art:8bb46253:csi.bill_trend_6m]]
- delinq_count_6m: 0.002143 [[art:4564aa47:csi.delinq_count_6m]]
- delinq_last: 0.0295 [[art:cd29d613:csi.delinq_last]]
- delinq_max_6m: 0.002782 [[art:2fe28db6:csi.delinq_max_6m]]
- limit_bal: 0.007188 [[art:cb617a64:csi.limit_bal]]
- pay_amt_next: 0.4064 [[art:e708fa25:csi.pay_amt_next]]
- pay_ratio_last: 0.003912 [[art:c083b28c:csi.pay_ratio_last]]
- pay_ratio_mean_6m: 0.003519 [[art:8f1dbe89:csi.pay_ratio_mean_6m]]
- utilisation: 0.01304 [[art:b1f362df:csi.utilisation]]

The largest of these contributions is 0.4064 [[art:3f7f79cf:csi.max]], carried by pay_amt_next at 0.4064 [[art:e708fa25:csi.pay_amt_next]], and read against the declared stability bound of 0.25 [[art:278b9016:threshold.S1.psi]] it stands above that bound; this exceedance is not among the findings raised for this section and is left to the findings section as an open item.
The comparison between the two stability measures for pay_amt_next is a comparison of levels against the same declared bound, not of one difference against another: its marginal train-to-test shift of 0.01789 [[art:996bb509:psi.pay_amt_next]] sits below the bound of 0.25 [[art:278b9016:threshold.S1.psi]] while its contribution to the shift in the linear predictor of 0.4064 [[art:e708fa25:csi.pay_amt_next]] sits above the same bound.
A feature whose marginal distribution barely moves can still dominate the predictor shift when the model leans heavily on it, and that is the pattern here.
No other feature's predictor contribution comes near the bound, the second largest being delinq_last at 0.0295 [[art:cd29d613:csi.delinq_last]].

### Leakage screens

The timing screen flags 1 [[art:e3a31f6a:leakage.timing.n_flagged]] feature declared during_period or after_outcome, namely pay_amt_next, declared after_outcome, whose value is therefore not known at the moment the model scores.
The strongest single feature reaches an AUC of 0.945 [[art:5b5e98c2:leakage.target_corr.max_single_feature_auc]] on its own, above the leakage bound on single-feature discrimination of 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]], and that feature is pay_amt_next.
These two results are the leakage findings raised for this section, and they point at the same feature from two directions: a declared timing that puts its value after the outcome, and a standalone discriminatory power above what any legitimate predictor in this package would be expected to reach.
The validator's view is that pay_amt_next should be removed from the feature set and the model refit before its performance figures are read as evidence of anything, since the stability result above is a further symptom of the same defect.

The contamination screen has two arms, each read against its own bound.
The share of test rows whose identifiers also identify a row of train is 0 [[art:63d37fc5:leakage.overlap.ids]], against the declared overlap bound of 0.005 [[art:9f336eaf:threshold.L2.overlap]], and so it is below that bound.
The share of test rows whose feature values also appear in train is 0 [[art:0fec8048:leakage.overlap.features]], against the bound the feature-overlap rule actually applied of 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]], and so it is below that bound.
That effective bound is the larger of the declared overlap bound and the doubled within-train duplicate share, on the reasoning that two different subjects writing the same discrete row is coincidence rather than contamination; the share of train rows whose feature values are not unique within train is 0 [[art:4474c227:leakage.duplicates.train]], so the declared bound is the larger of the two and is the one that governed.
The overall share of test rows also present in train is 0 [[art:4c9fcd09:leakage.overlap]], below the declared overlap bound of 0.005 [[art:9f336eaf:threshold.L2.overlap]].
The name screen matches 0 [[art:407e62be:leakage.name_screen.n_matched]] feature names against the target-adjacent lexicon, so the leakage exposure identified above comes from a declared timing and a measured discrimination rather than from anything visible in the naming.

### Assessment

Missingness and split overlap raise no concern against their bounds, and the marginal population shift from train to test is well within the declared bound throughout, score included.
The data integrity exposure in this package is concentrated in a single feature, which the timing declaration and the single-feature discrimination screen both reach, and which also carries the predictor-shift contribution standing above the declared stability bound.

## 4. Outcomes analysis

Outcomes analysis compares the model's outputs with the realised defaults on the evaluation data, which is the comparison the guidance on outcomes analysis asks a validation to review [[reg:SR26-2:V.1.b]].
This section reports discrimination first and calibration after it.
The reason is the observed event rate on the evaluation split, 0.2247 [[art:9209d200:metrics.test.event_rate]], which sits at or above 0.05 [[art:42f1351e:rule.calibration_first_event_rate]], the rate below which this report would lead with calibration instead.

The recomputed metrics by split are as follows, one row per metric.

| Metric | Train | Test |
| --- | --- | --- |
| Rows | 3500 [[art:564683ee:metrics.train.n]] | 1500 [[art:64fcf14d:metrics.test.n]] |
| Observed event rate | 0.2246 [[art:133a5ff8:metrics.train.event_rate]] | 0.2247 [[art:9209d200:metrics.test.event_rate]] |
| AUC | 0.9812 [[art:da2cd01d:metrics.train.auc]] | 0.9755 [[art:8f522f3b:metrics.test.auc]] |
| Gini | 0.9624 [[art:23cb4057:metrics.train.gini]] | 0.951 [[art:f927e3cd:metrics.test.gini]] |
| KS | 0.8895 [[art:7a126f15:metrics.train.ks]] | 0.8784 [[art:81bee194:metrics.test.ks]] |
| Brier | 0.03817 [[art:959b3159:metrics.train.brier]] | 0.04247 [[art:d4f27e13:metrics.test.brier]] |
| Log loss | 0.1505 [[art:417d98d9:metrics.train.logloss]] | 0.167 [[art:aa620b5e:metrics.test.logloss]] |
| Mean predicted probability | 0.2246 [[art:1fa024a6:metrics.train.mean_predicted]] | 0.233 [[art:0b9b6a1e:metrics.test.mean_predicted]] |

Separation by decile of predicted probability on the evaluation split is reported below.

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

Event capture in the highest deciles of predicted probability is 0.8422 [[art:55242963:deciles.train.top2_capture]] on train and 0.822 [[art:5690757b:deciles.test.top2_capture]] on test, so rank-ordering carries over from the development sample to the evaluation sample.

The train-to-test gap in discrimination was read against a bound of 0.08 [[art:630f28f4:threshold.O1.auc_gap]], with AUC 0.9812 [[art:da2cd01d:metrics.train.auc]] on train and 0.9755 [[art:8f522f3b:metrics.test.auc]] on test.
The evaluation split sits below the development split on AUC, on Gini and on KS, and above it on Brier and on log loss, the direction expected of a holdout.
That gap raised no candidate of its own; the only candidate this section's computation raised is the calibration one described next.

Calibration was read by regressing the outcome on the logit of the predicted probability.
The slope is 1.197 [[art:c9a03fe6:calibration_slope.test]] on test, inside the declared band whose bottom is 0.8 [[art:749634ae:threshold.C1.calibration_slope.min]] and whose top is 1.2 [[art:b6672579:threshold.C1.calibration_slope.max]].
The slope is 1.383 [[art:45dafd11:calibration_slope.train]] on train, above that top of 1.2 [[art:b6672579:threshold.C1.calibration_slope.max]], and this is the calibration finding raised for this section.
The intercept is -0.0558 [[art:56745cf2:calibration_intercept.test]] on test and 0.2246 [[art:d556f341:calibration_intercept.train]] on train.
Mean predicted probability on test is 0.233 [[art:0b9b6a1e:metrics.test.mean_predicted]] against an observed rate of 0.2247 [[art:9209d200:metrics.test.event_rate]], a relative gap of 0.03717 [[art:6a845d81:calibration.mean_rel_gap.test]] against a tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
The same comparison on train gives 0.2246 [[art:1fa024a6:metrics.train.mean_predicted]] against 0.2246 [[art:133a5ff8:metrics.train.event_rate]], a relative gap of 8.632e-05 [[art:f7447f34:calibration.mean_rel_gap.train]] against the same tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
Calibration by decile of predicted probability on the evaluation split is reported below.

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

The developer-declared thresholds, with the bound, the recomputed value and the outcome the tool recorded for each, are reported below.

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

The rows cover the discrimination, calibration and stability bounds that package.yaml declares, each beside the value recomputed against it.
The outcome column is the tool's own, computed from the same values this section reports, so it cannot disagree with them.

### Follow-up analyses

The planning loop asked for every metric on the slice `limit_bal <= median(limit_bal)`, on train and on test.
It was asked to test whether the out-of-range calibration slope is concentrated in the below-median limit group rather than spread evenly across the split.

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

The group's AUC falls below the split's own by 0.008866 [[art:999aab9c:metrics.train.sub.limit_bal_low.auc_gap]] on train and by 0.008535 [[art:6990b76c:metrics.test.sub.limit_bal_low.auc_gap]] on test, inside the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] in each case, so neither reading is an open item.
The group holds 0.5037 [[art:45c51f9e:metrics.train.sub.limit_bal_low.share]] of train and 0.504 [[art:bac689cc:metrics.test.sub.limit_bal_low.share]] of test, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] a sub-population must hold before it can raise an open item.
On train, mean predicted probability is 0.2458 [[art:2086a25d:metrics.train.sub.limit_bal_low.mean_predicted]] against an observed rate of 0.2439 [[art:0ae85aa6:metrics.train.sub.limit_bal_low.event_rate]], a relative gap of 0.007657 [[art:a93d065e:metrics.train.sub.limit_bal_low.mean_rel_gap]] against a tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
On test, mean predicted probability is 0.2585 [[art:c1a37d64:metrics.test.sub.limit_bal_low.mean_predicted]] against an observed rate of 0.2487 [[art:de78adb5:metrics.test.sub.limit_bal_low.event_rate]], a relative gap of 0.03933 [[art:2b29e325:metrics.test.sub.limit_bal_low.mean_rel_gap]] against the same tolerance.
These are relative comparisons of the level of the probabilities, and since the ordering gaps stay inside their bound, what this group shows is a level effect and not a loss of rank-ordering.

The planning loop asked for every metric on the slice `limit_bal > median(limit_bal)`, on train and on test.
It was asked to complete the partition by limit so that the calibration-slope miss could be read as split-wide or as concentrated in one group.

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

The group's AUC sits above the split's own, the recorded gaps being -0.006442 [[art:52a49712:metrics.train.sub.limit_bal_high.auc_gap]] on train and -0.00586 [[art:e37bc8d6:metrics.test.sub.limit_bal_high.auc_gap]] on test, inside the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].
The group holds 0.4963 [[art:2de2a90a:metrics.train.sub.limit_bal_high.share]] of train and 0.496 [[art:ac383ccb:metrics.test.sub.limit_bal_high.share]] of test, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].
On train, mean predicted probability is 0.203 [[art:b1995539:metrics.train.sub.limit_bal_high.mean_predicted]] against an observed rate of 0.205 [[art:9de459ef:metrics.train.sub.limit_bal_high.event_rate]], a relative gap of 0.00944 [[art:58ae0f50:metrics.train.sub.limit_bal_high.mean_rel_gap]] against a tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
On test, mean predicted probability is 0.2072 [[art:f80c93c0:metrics.test.sub.limit_bal_high.mean_predicted]] against an observed rate of 0.2003 [[art:5e9aab40:metrics.test.sub.limit_bal_high.event_rate]], a relative gap of 0.03445 [[art:679e4d84:metrics.test.sub.limit_bal_high.mean_rel_gap]] against the same tolerance.
Read on the relative comparison, both groups of the limit partition carry a level gap on test and a much smaller one on train, so the partition by limit does not localise the calibration miss to one side of it.

The planning loop asked for every metric on the slice `utilisation > median(utilisation)`, on train and on test.
It was asked to test whether the calibration miss is concentrated in the higher-risk, high-utilisation group, which the partition by limit had not resolved.

<!-- quaestor:renderer:begin table metrics.train.sub.utilisation_high -->
Every metric on the utilisation above_median slice of train [[art:ea5149a8:metrics.train.sub.utilisation_high]]:

| metric | value |
|---|---|
| n | 1750 |
| event_rate | 0.2246 |
| auc | 0.977 |
| gini | 0.954 |
| ks | 0.8717 |
| brier | 0.04239 |
| logloss | 0.1625 |
| mean_predicted | 0.225 |
| mean_rel_gap | 0.001828 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.utilisation_high -->
Every metric on the utilisation above_median slice of test [[art:2199f7de:metrics.test.sub.utilisation_high]]:

| metric | value |
|---|---|
| n | 750 |
| event_rate | 0.2333 |
| auc | 0.9665 |
| gini | 0.9331 |
| ks | 0.8492 |
| brier | 0.05272 |
| logloss | 0.2032 |
| mean_predicted | 0.2406 |
| mean_rel_gap | 0.03112 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

The group's AUC falls below the split's own by 0.004174 [[art:f90452de:metrics.train.sub.utilisation_high.auc_gap]] on train and by 0.008957 [[art:55113529:metrics.test.sub.utilisation_high.auc_gap]] on test, inside the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].
The group holds 0.5 [[art:0ff76e00:metrics.train.sub.utilisation_high.share]] of train and 0.5 [[art:9404484e:metrics.test.sub.utilisation_high.share]] of test, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].
On train, mean predicted probability is 0.225 [[art:c7975c20:metrics.train.sub.utilisation_high.mean_predicted]] against an observed rate of 0.2246 [[art:0055e6aa:metrics.train.sub.utilisation_high.event_rate]], a relative gap of 0.001828 [[art:86210ecf:metrics.train.sub.utilisation_high.mean_rel_gap]] against a tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
On test, mean predicted probability is 0.2406 [[art:893eaa1e:metrics.test.sub.utilisation_high.mean_predicted]] against an observed rate of 0.2333 [[art:8e66209c:metrics.test.sub.utilisation_high.event_rate]], a relative gap of 0.03112 [[art:e10c751a:metrics.test.sub.utilisation_high.mean_rel_gap]] against the same tolerance.
Here too the ordering holds within its bound and the departure is in the level of the probabilities.

The planning loop asked for every metric on the slice `utilisation <= median(utilisation)`, on train and on test.
It was asked to complete the partition by utilisation so that the out-of-band train calibration slope could be attributed to one group rather than to the split as a whole.

<!-- quaestor:renderer:begin table metrics.train.sub.utilisation_low -->
Every metric on the utilisation below_median slice of train [[art:db4b269d:metrics.train.sub.utilisation_low]]:

| metric | value |
|---|---|
| n | 1750 |
| event_rate | 0.2246 |
| auc | 0.9892 |
| gini | 0.9784 |
| ks | 0.9155 |
| brier | 0.03395 |
| logloss | 0.1384 |
| mean_predicted | 0.2241 |
| mean_rel_gap | 0.002 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.utilisation_low -->
Every metric on the utilisation below_median slice of test [[art:22a4e77a:metrics.test.sub.utilisation_low]]:

| metric | value |
|---|---|
| n | 750 |
| event_rate | 0.216 |
| auc | 0.9879 |
| gini | 0.9758 |
| ks | 0.9123 |
| brier | 0.03223 |
| logloss | 0.1308 |
| mean_predicted | 0.2254 |
| mean_rel_gap | 0.04371 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

The group's AUC sits above the split's own, the recorded gaps being -0.008041 [[art:6c1cbaed:metrics.train.sub.utilisation_low.auc_gap]] on train and -0.01238 [[art:469220d0:metrics.test.sub.utilisation_low.auc_gap]] on test, inside the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].
The group holds 0.5 [[art:31f26e20:metrics.train.sub.utilisation_low.share]] of train and 0.5 [[art:7860a748:metrics.test.sub.utilisation_low.share]] of test, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].
On train, mean predicted probability is 0.2241 [[art:7648c23f:metrics.train.sub.utilisation_low.mean_predicted]] against an observed rate of 0.2246 [[art:bbabdd5d:metrics.train.sub.utilisation_low.event_rate]], a relative gap of 0.002 [[art:de6fc46d:metrics.train.sub.utilisation_low.mean_rel_gap]] against a tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
On test, mean predicted probability is 0.2254 [[art:f2a826ca:metrics.test.sub.utilisation_low.mean_predicted]] against an observed rate of 0.216 [[art:b0ad49be:metrics.test.sub.utilisation_low.event_rate]], a relative gap of 0.04371 [[art:dfa4be18:metrics.test.sub.utilisation_low.mean_rel_gap]] against the same tolerance.
Comparing the groups of the utilisation partition on the relative gap between mean predicted and observed, the below-median group on test reads larger than the above-median group on test, while on train both read far smaller than either test value, so the level effect is a property of the evaluation split rather than of one utilisation group.
Across all four slices the ordering gaps stay inside their bound and the level gaps stay inside the calibration tolerance, so the calibration finding stands on the split-level slope rather than on any one sub-population.

## 5. Sensitivity and scenario analysis

Sensitivity analysis here follows the expectation that key assumptions and the choice of variables be subjected to critical analysis, with attention to the impact of those choices on model output [[reg:SR26-2:V.1.a]].

The collinearity diagnostics on the retained feature set are the substantive part of this section for a model of this type, and they are reported against the thresholds the package declares.
The largest variance inflation factor across the retained features is 8.181 [[art:4afdc4f1:vif.max]], which sits below the declared ceiling of 10 [[art:aeb4f33c:threshold.M1.vif]].
The condition number of the column-standardised design is 6.185 [[art:36392379:condition_number]], below the declared ceiling of 30 [[art:7e52fd7a:threshold.M1.condition_number]].
Both diagnostics therefore fall on the passing side of their respective thresholds, though the variance inflation factor is the nearer of the two to its limit.

The per-feature variance inflation factors show where the shared variance concentrates.
The six-month mean billing feature carries the largest value at 8.181 [[art:d5ab7306:vif.bill_mean_6m]], followed by the six-month mean payment-ratio feature at 7.526 [[art:000b6208:vif.pay_ratio_mean_6m]] and the most-recent payment-ratio feature at 7.268 [[art:bec24796:vif.pay_ratio_last]].
These three sit above the credit-limit feature at 4.81 [[art:8209ea46:vif.limit_bal]] and the utilisation feature at 3.215 [[art:ec978947:vif.utilisation]], and they form a cluster of payment- and balance-derived terms whose overlap is the main source of correlation in the design.
The delinquency block is more modest: the six-month delinquency count is at 2.561 [[art:87890613:vif.delinq_count_6m]], the six-month delinquency maximum at 2.408 [[art:4b239ec5:vif.delinq_max_6m]], and the most-recent delinquency indicator at 1.422 [[art:c18221d4:vif.delinq_last]].
The next-period payment amount is at 2.206 [[art:68806d80:vif.pay_amt_next]], the six-month billing trend at 1.225 [[art:0cb3df89:vif.bill_trend_6m]], and age is effectively orthogonal to the rest of the design at 1.002 [[art:8021b06e:vif.age]].
The reviewer's reading is that coefficient variances on the payment-ratio and billing-level terms are inflated enough to make individual coefficient interpretation less stable than the design as a whole, even though every feature clears the declared ceiling.

Two of the sensitivity exercises contemplated for this report do not apply to a model of this type and were not run.
Regime-partitioned stability is one of them: the package declares no regime column for this subject, so there are no declared regimes across which to compare performance, and the exercise is carried in Appendix D as not applicable rather than as an executed test.
The rate-shock scenarios are the other: they are defined for a hazard model, and the subject here is not one, so there is no value change at the extreme shocks to report, no shock curve whose monotonicity could be assessed, and no convexity to compare against a declared direction.
Appendix D lists both, and neither should be read anywhere in this report as an exercise that was performed and passed.

Because sensitivity and robustness checks are expected to be repeated over the life of the model rather than performed once, the collinearity diagnostics above should be recomputed on the monitoring cadence, with particular attention to whether the payment-ratio and billing-level cluster drifts toward the declared ceiling [[reg:SR11-7:V.1.b]].

## 6. Findings and recommendations

Findings below are ordered by severity, the more severe first, and each one carries the recomputed values and the declared bounds they were read against, in keeping with validation that identifies model limitations and errors and clarifies whether corrective actions may be warranted [[reg:SR26-2:V]].

### F-001 · L1 leakage · severity **high**

**The package scores on a feature whose declared timing places it during or after the outcome, so its value is not knowable at the moment the model is applied.**

The package declares `pay_amt_next` with a timing that falls during or after the outcome period, and the count of features so declared is 1 [[art:e3a31f6a:leakage.timing.n_flagged]].

<!-- quaestor:renderer:begin table leakage.timing -->
Each feature's declared timing; flagged means during or after the outcome [[art:0dad290e:leakage.timing]]:

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
| pay_amt_next | after_outcome | true |
<!-- quaestor:renderer:end -->

That same feature separates the outcome on its own at an AUC of 0.945 [[art:5b5e98c2:leakage.target_corr.max_single_feature_auc]], above the declared ceiling of 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]] for what any single feature may reach by itself.

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

The validator concludes that the declared timing and the single-feature separation point the same way: the discrimination attributed to this feature is not available at scoring time, so any performance the model shows while it is in the design matrix overstates what the model can do in use.

The model developer should remove `pay_amt_next` from the feature set, refit, and report the refitted performance and the refitted single-feature separation against the same declared ceiling; if the feature is retained, the developer should supply a timing declaration that shows the value is observable before the outcome window opens.

### F-002 · C1 calibration · severity **medium**

**The fitted probabilities on train are miscalibrated in slope, so the model's scores do not map onto observed outcome rates within the declared band.**

The logistic regression of the outcome on the model's logit has a slope on train of 1.383 [[art:45dafd11:calibration_slope.train]], above the top of the declared band at 1.2 [[art:b6672579:threshold.C1.calibration_slope.max]].

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

The validator concludes that the breach is in the direction of predictions that are too compressed relative to the outcomes they are fitted to, and that it appears on the very data the model was fitted on, which is where a slope closest to agreement would ordinarily be expected.

The model developer should recalibrate the score-to-probability mapping and report the recalibrated slope against the same declared band, and should state whether the breach is driven by the design matrix as fitted or by the link and estimation procedure, since a refit following F-001 will change this quantity.

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1, S1), `compute_metrics` (T1, O1), `check_leakage` (L2), `check_collinearity` (M1), `challenger_compare` (E1).

### Open items

Can the model developer explain what the model is discriminating on when the fitted coefficient on `bill_mean_6m` carries sign 1 [[art:a457c04a:sign_check.bill_mean_6m.coef_sign]], read against that feature's own univariate direction of -1 [[art:23b89c5d:sign_check.bill_mean_6m.univariate_direction]], the two agreeing at 0 [[art:4df8b747:sign_check.bill_mean_6m.agrees]], once the features correlated with it are held fixed?

Can the model developer explain what the model is discriminating on when the fitted coefficient on `bill_trend_6m` carries sign 1 [[art:abd4aaba:sign_check.bill_trend_6m.coef_sign]], read against that feature's own univariate direction of -1 [[art:a9bff389:sign_check.bill_trend_6m.univariate_direction]], the two agreeing at 0 [[art:c0f6d07d:sign_check.bill_trend_6m.agrees]], once the features correlated with it are held fixed?

Can the model developer explain what the model is discriminating on when the fitted coefficient on `delinq_max_6m` carries sign -1 [[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]], read against that feature's own univariate direction of 1 [[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]], the two agreeing at 0 [[art:c946359c:sign_check.delinq_max_6m.agrees]], given that a segment selected on a delinquency count is also a segment of near-constant delinquency history?

Can the model developer explain what the model is discriminating on when the fitted coefficient on `limit_bal` carries sign 1 [[art:6af6aef2:sign_check.limit_bal.coef_sign]], read against that feature's own univariate direction of -1 [[art:56d284d6:sign_check.limit_bal.univariate_direction]], the two agreeing at 0 [[art:0278aad1:sign_check.limit_bal.agrees]], once the features correlated with it are held fixed?

Can the model developer explain what the model is discriminating on when the fitted coefficient on `pay_ratio_last` carries sign 1 [[art:f018263e:sign_check.pay_ratio_last.coef_sign]], read against that feature's own univariate direction of -1 [[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]], the two agreeing at 0 [[art:79abee77:sign_check.pay_ratio_last.agrees]], once the features correlated with it are held fixed?

Can the model developer explain what the model is discriminating on when the fitted coefficient on `pay_ratio_mean_6m` carries sign 1 [[art:8547787e:sign_check.pay_ratio_mean_6m.coef_sign]], read against that feature's own univariate direction of -1 [[art:24dcef24:sign_check.pay_ratio_mean_6m.univariate_direction]], the two agreeing at 0 [[art:51914c14:sign_check.pay_ratio_mean_6m.agrees]], once the features correlated with it are held fixed?

Answers to these questions, together with the responses to the findings above, belong in the model documentation so that the exchange and its resolution can be tracked [[reg:SR26-2:VI.3]].

## 7. Ongoing monitoring recommendations

Ongoing monitoring should evaluate whether this package continues to perform as expected given potential changes in products, exposures, activities, clients, data relevance, or market conditions, with the frequency and scope of each monitoring report scaled to the model's materiality and use [[reg:SR26-2:V.2]].
The quantities below are the ones this validation recomputed, and the bounds are the ones the package already declares, so monitoring can extend the same checks onto production vintages rather than introduce new acceptance criteria.

**Discrimination.** Recompute AUC on each production vintage once outcomes have matured, and compare it against the declared floor of 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]].
The value on the evaluation split was 0.9755 [[art:8f522f3b:metrics.test.auc]], which lies above that floor, and it is the reference point against which vintage-over-vintage deterioration should be read rather than a level that a production cohort is expected to reproduce.
A quarterly cadence suits this quantity, since it depends on realized outcomes accumulating over the performance window.

**Accuracy of the probabilities.** Track the Brier score on the same quarterly cadence against the declared ceiling of 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]], with the evaluation-split value of 0.04247 [[art:d4f27e13:metrics.test.brier]] as the reference point.

**Calibration.** Refit the logistic regression of the outcome on the logit of the predicted probability for each vintage and compare the slope against the band whose lower edge is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] and whose upper edge is 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The slope on the evaluation split was 1.197 [[art:c9a03fe6:calibration_slope.test]], which lies inside that band and below its upper edge, and it is the upper edge that any further increase in slope would cross first, so this quantity warrants a tighter watch than the others and should be reviewed at every monitoring cycle rather than only at revalidation.
An escalation triggered by movement toward the upper edge should be treated as a candidate for recalibration rather than for redevelopment, consistent with the guidance that persistent deviation outside established performance thresholds may warrant adjustment, recalibration, or redevelopment [[reg:SR26-2:V.1.b]].

**Input and score stability.** Recompute the population stability index of each model input and of the score itself, monthly, comparing the production vintage against the development reference and against the prior vintage, and read it against the declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
The largest train-to-test value seen in this validation was 0.01789 [[art:1b87de3e:psi.max]], well below that ceiling, which means monitoring starts from a stable baseline and any material movement in a production vintage should be visible early.
This is the one quantity that does not wait on outcomes, so it is the appropriate early-warning signal between the quarterly outcome-based reviews.

**Ordering of the monitoring report.** A monitoring report for a future cohort whose observed event rate falls below 0.05 [[art:42f1351e:rule.calibration_first_event_rate]] should lead with calibration and treat discrimination as the secondary read, because rank ordering is the less informative of the two when events are scarce.
This report presented discrimination before calibration, since the observed event rate on the evaluation split was at or above that bound, and the ordering should be revisited per cohort rather than fixed once.

**Sub-population reporting.** Where monitoring compares a calibration error, a shortfall or a performance gap across sub-populations, deciles or splits, the report should state explicitly whether the comparison is the absolute difference or the ratio, and should show the other alongside it, since two sub-populations whose absolute gaps agree can differ materially on the ratio.
A sub-population should not be described as in line with another on one of those comparisons while the other goes unreported.

**Benchmarking.** The champion was compared with a challenger earlier in this report, and that comparison rests on the development data, so what monitoring adds is the comparison that data cannot give: the challenger refitted on production vintages and scored against the champion on the same realized outcomes, run at the annual revalidation or sooner if a drift or calibration trigger fires.
Separately from that internal comparison, the champion should be benchmarked against an external or vendor reference for this exposure type, such as a bureau score or a consortium model, with any discrepancy investigated for its source and magnitude rather than read as error in either model [[reg:SR11-7:V.1.b]].
A close match with a benchmark is evidence in favor of the model but should be interpreted with caution, since the benchmark is itself an alternative prediction [[reg:SR11-7:V.1.b]].

**What this validation could not cover and monitoring should watch instead.** This validation observed a held-out evaluation split drawn from the development period, so it could not observe outcomes realized after deployment; back-testing at an observation frequency matching the performance window is the monitoring activity that closes that gap.
The evaluation split reflects the economic and portfolio conditions of the development period, so shifts in product mix, acquisition channel, underwriting policy or macroeconomic conditions are outside what any number in this report speaks to and must be picked up by the drift and outcome monitoring described above.
This validation examined the model as packaged rather than as implemented in production systems, so process verification of the scoring pipeline, the upstream data feeds and the change control over the implementing code belongs to monitoring [[reg:SR11-7:V.1.b]].
Where third-party or vendor-supplied inputs feed the score, the integrity and continued applicability of those sources should be reassessed on a regular schedule, using the institution's own outcomes rather than the provider's reported performance [[reg:SR11-7:V.2]].
Overrides of the model output by users were outside the scope of this exercise and should be logged, counted and analyzed by monitoring, since a high override rate or an override process that consistently improves on the model is a signal that the model needs revision [[reg:SR11-7:V.1.b]].
Sub-populations that were thinly represented in the evaluation split cannot be assessed reliably from it, and monitoring should accumulate outcomes for them and report their performance separately as volume permits.
Model limitations identified at development should themselves be reassessed over time as part of the monitoring plan, alongside the procedures for responding to issues that arise [[reg:SR26-2:V.2]].
Material model risk can remain even after sound development and rigorous validation, so users of the output should be told the limitations above and should supplement the score with complementary analysis where a decision turns on a condition this validation did not observe [[reg:SR26-2:V]].

## Appendix A — Claims

Grounding precision 0.9922 before repair (256 of 258 claims verified; 2 dangling) and 1.0000 after 1 claim(s) rewritten and 1 number(s) removed from the prose. Per section (post-repair): summary 12/12; conceptual_soundness 58/58; data_integrity 50/50; outcomes 90/90; sensitivity 15/15; findings 23/23; monitoring 10/10.

Repairs:

| section | before | after | instruction to the drafter |
|---|---|---|---|
| conceptual_soundness | 10 (dangling) | 10 (verified) | you wrote 10 with the citation '[[art:e4b3fd0e:run.model_summary#vif_threshold}]', which names no artifact; a number is cited by an artifact citation carrying the hash and the logical name |

Developer claims: The package declares 2 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). See Appendix D.

Excluded numeric tokens (not claims): citation_hash (2ad8d1a5, 2510d49d, 2193cf5f, 8f522f3b); regulatory_section_id (SR26-2:V, SR26-2:V.1.a, SR26-2:IV.1, SR26-2:V.1.b); finding_id (F-001, F-002); package_version (1.0); extractor_returned_excluded_token (1.0, 26.0, 2, 2.0).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The subject was loaded from its package and scored by the va… | 300 | ratio | runtime.max_seconds |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 2 | summary | The development split holds 3500 rows and the holdout split… | 3500 | count | n | train | eq | `[[art:2510d49d:profile.train.n]]` | verified | 3500 |
| 3 | summary | The development split holds 3500 rows and the holdout split… | 1500 | count | n | test | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 4 | summary | On the holdout split, discrimination measured by the area un… | 0.9755 | ratio | auc | test | eq | `[[art:8f522f3b:metrics.test.auc]]` | verified | 0.9755058926 |
| 5 | summary | On the holdout split, discrimination measured by the area un… | 0.7 | ratio | auc | test | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 6 | summary | The Brier score on the holdout split is 0.04247 , below the… | 0.04247 | ratio | brier | test | eq | `[[art:d4f27e13:metrics.test.brier]]` | verified | 0.04247487168 |
| 7 | summary | The Brier score on the holdout split is 0.04247 , below the… | 0.2 | ratio | brier | test | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 8 | summary | The largest train-to-test population stability index, score… | 0.01789 | ratio | psi |  | eq | `[[art:1b87de3e:psi.max]]` | verified | 0.01789488592 |
| 9 | summary | The largest train-to-test population stability index, score… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 10 | summary | The slope of the outcome regressed on the logit of the predi… | 1.197 | ratio | calibration_slope | test | eq | `[[art:c9a03fe6:calibration_slope.test]]` | verified | 1.19744242 |
| 11 | summary | The slope of the outcome regressed on the logit of the predi… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 12 | summary | The slope of the outcome regressed on the logit of the predi… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 13 | conceptual_soundness | The champion is a regression carrying one fitted coefficient… | -6.103 | ratio | intercept |  | eq | `[[art:e4b3fd0e:run.model_summary#intercept]]` | verified | -6.102832939 |
| 14 | conceptual_soundness | The champion is a regression carrying one fitted coefficient… | 3500 | count | n_train | train | eq | `[[art:e4b3fd0e:run.model_summary#n_train]]` | verified | 3500 |
| 15 | conceptual_soundness | The declared feature set counts 13 features in total. | 13 | count | n |  | eq | `[[art:7276ca89:run.features#n]]` | verified | 13 |
| 16 | conceptual_soundness | Of these, 2 are known at origination and 10 are known before… | 2 | count | at_origination |  | eq | `[[art:7276ca89:run.features#at_origination]]` | verified | 2 |
| 17 | conceptual_soundness | Of these, 2 are known at origination and 10 are known before… | 10 | count | before_period_start |  | eq | `[[art:7276ca89:run.features#before_period_start]]` | verified | 10 |
| 18 | conceptual_soundness | None are timed during the period, at 0 . | 0 | count | during_period |  | eq | `[[art:7276ca89:run.features#during_period]]` | verified | 0 |
| 19 | conceptual_soundness | One feature, 1 of the set, is timed after the outcome, meani… | 1 | count | after_outcome |  | eq | `[[art:7276ca89:run.features#after_outcome]]` | verified | 1 |
| 20 | conceptual_soundness | That feature is pay_amt_next, and it carries the largest coe… | -12.37 | ratio | coefficient |  | eq | `[[art:e4b3fd0e:run.model_summary#coefficients.pay_amt_next.value]]` | verified | -12.36667537 |
| 21 | conceptual_soundness | That feature is pay_amt_next, and it carries the largest coe… | 1.651 | ratio | coefficient |  | eq | `[[art:e4b3fd0e:run.model_summary#coefficients.bill_mean_6m.value]]` | verified | 1.651229182 |
| 22 | conceptual_soundness | Refitting the champion's functional form without pay_amt_nex… | -0.2275 | ratio | delta_auc | test | eq | `[[art:cf6c0563:ablation.pay_amt_next.delta_auc]]` | verified | -0.2275170885 |
| 23 | conceptual_soundness | Refitting the champion's functional form without pay_amt_nex… | 0.9755 | ratio | baseline_auc | test | eq | `[[art:8e58476a:ablation.baseline_auc]]` | verified | 0.9755058926 |
| 24 | conceptual_soundness | The developer applied a collinearity screen at a variance in… | 10 | ratio | vif_threshold |  | eq | `[[art:e4b3fd0e:run.model_summary#vif_threshold]]` | verified | 10 |
| 25 | conceptual_soundness | The developer applied a collinearity screen at a variance in… | 162.9 | ratio | vif |  | eq | `[[art:e4b3fd0e:run.model_summary#removed.bill_last.vif]]` | verified | 162.931494 |
| 26 | conceptual_soundness | The developer applied a collinearity screen at a variance in… | 36.78 | ratio | vif |  | eq | `[[art:e4b3fd0e:run.model_summary#removed.utilisation_mean_6m.vif]]` | verified | 36.782216 |
| 27 | conceptual_soundness | Among the retained features, the largest coefficients after… | 0.9159 | ratio | coefficient |  | eq | `[[art:e4b3fd0e:run.model_summary#coefficients.delinq_last.value]]` | verified | 0.9159219077 |
| 28 | conceptual_soundness | Among the retained features, the largest coefficients after… | 0.8591 | ratio | coefficient |  | eq | `[[art:e4b3fd0e:run.model_summary#coefficients.utilisation.value]]` | verified | 0.8591255354 |
| 29 | conceptual_soundness | Among the retained features, the largest coefficients after… | 0.7072 | ratio | coefficient |  | eq | `[[art:e4b3fd0e:run.model_summary#coefficients.pay_ratio_mean_6m.value]]` | verified | 0.7071884027 |
| 30 | conceptual_soundness | Among the retained features, the largest coefficients after… | 0.4311 | ratio | coefficient |  | eq | `[[art:e4b3fd0e:run.model_summary#coefficients.limit_bal.value]]` | verified | 0.4311198001 |
| 31 | conceptual_soundness | The smaller weights are pay_ratio_last at 0.2086 , bill_tren… | 0.2086 | ratio | coefficient |  | eq | `[[art:e4b3fd0e:run.model_summary#coefficients.pay_ratio_last.value]]` | verified | 0.2086444371 |
| 32 | conceptual_soundness | The smaller weights are pay_ratio_last at 0.2086 , bill_tren… | 0.1993 | ratio | coefficient |  | eq | `[[art:e4b3fd0e:run.model_summary#coefficients.bill_trend_6m.value]]` | verified | 0.1992999704 |
| 33 | conceptual_soundness | The smaller weights are pay_ratio_last at 0.2086 , bill_tren… | 0.1073 | ratio | coefficient |  | eq | `[[art:e4b3fd0e:run.model_summary#coefficients.delinq_count_6m.value]]` | verified | 0.1072548632 |
| 34 | conceptual_soundness | The smaller weights are pay_ratio_last at 0.2086 , bill_tren… | -0.09998 | ratio | coefficient |  | eq | `[[art:e4b3fd0e:run.model_summary#coefficients.delinq_max_6m.value]]` | verified | -0.09997986467 |
| 35 | conceptual_soundness | The smaller weights are pay_ratio_last at 0.2086 , bill_tren… | -0.08872 | ratio | coefficient |  | eq | `[[art:e4b3fd0e:run.model_summary#coefficients.age.value]]` | verified | -0.08872433211 |
| 36 | conceptual_soundness | On subject matter grounds the recent-delinquency and utilisa… | 1 | ratio | coef_sign |  | eq | `[[art:50d352f8:sign_check.delinq_last.coef_sign]]` | verified | 1 |
| 37 | conceptual_soundness | On subject matter grounds the recent-delinquency and utilisa… | 1 | ratio | coef_sign |  | eq | `[[art:85badc3c:sign_check.utilisation.coef_sign]]` | verified | 1 |
| 38 | conceptual_soundness | On subject matter grounds the recent-delinquency and utilisa… | 1 | ratio | univariate_direction | train | eq | `[[art:a78648ba:sign_check.delinq_last.univariate_direction]]` | verified | 1 |
| 39 | conceptual_soundness | On subject matter grounds the recent-delinquency and utilisa… | 1 | ratio | univariate_direction | train | eq | `[[art:f0995196:sign_check.utilisation.univariate_direction]]` | verified | 1 |
| 40 | conceptual_soundness | The negative weight on age, at a fitted sign of -1 , agrees… | -1 | ratio | coef_sign |  | eq | `[[art:6172eb93:sign_check.age.coef_sign]]` | verified | -1 |
| 41 | conceptual_soundness | The negative weight on age, at a fitted sign of -1 , agrees… | -1 | ratio | univariate_direction | train | eq | `[[art:66364583:sign_check.age.univariate_direction]]` | verified | -1 |
| 42 | conceptual_soundness | The count of retained features whose fitted sign contradicts… | 6 | count | n_disagreements | train | eq | `[[art:75159a84:sign_check.n_disagreements]]` | verified | 6 |
| 43 | conceptual_soundness | On limit_bal the fitted sign is +1 while its direction on tr… | 1 | ratio | coef_sign |  | eq | `[[art:6af6aef2:sign_check.limit_bal.coef_sign]]` | verified | 1 |
| 44 | conceptual_soundness | On limit_bal the fitted sign is +1 while its direction on tr… | -1 | ratio | univariate_direction | train | eq | `[[art:56d284d6:sign_check.limit_bal.univariate_direction]]` | verified | -1 |
| 45 | conceptual_soundness | On limit_bal the fitted sign is +1 while its direction on tr… | 0.0006175 | ratio | delta_auc | test | eq | `[[art:4b976d60:ablation.limit_bal.delta_auc]]` | verified | 0.0006174556236 |
| 46 | conceptual_soundness | On pay_ratio_last the fitted sign is +1 against a direction… | 1 | ratio | coef_sign |  | eq | `[[art:f018263e:sign_check.pay_ratio_last.coef_sign]]` | verified | 1 |
| 47 | conceptual_soundness | On pay_ratio_last the fitted sign is +1 against a direction… | -1 | ratio | univariate_direction | train | eq | `[[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]]` | verified | -1 |
| 48 | conceptual_soundness | On pay_ratio_last the fitted sign is +1 against a direction… | 0.0001863 | ratio | delta_auc | test | eq | `[[art:c577925a:ablation.pay_ratio_last.delta_auc]]` | verified | 0.0001862572749 |
| 49 | conceptual_soundness | On delinq_max_6m the fitted sign is -1 against a direction o… | -1 | ratio | coef_sign |  | eq | `[[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]]` | verified | -1 |
| 50 | conceptual_soundness | On delinq_max_6m the fitted sign is -1 against a direction o… | 1 | ratio | univariate_direction | train | eq | `[[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]]` | verified | 1 |
| 51 | conceptual_soundness | On delinq_max_6m the fitted sign is -1 against a direction o… | 0.0001607 | ratio | delta_auc | test | eq | `[[art:b1793491:ablation.delinq_max_6m.delta_auc]]` | verified | 0.0001607425797 |
| 52 | conceptual_soundness | On pay_ratio_mean_6m the fitted sign is +1 against a directi… | 1 | ratio | coef_sign |  | eq | `[[art:8547787e:sign_check.pay_ratio_mean_6m.coef_sign]]` | verified | 1 |
| 53 | conceptual_soundness | On pay_ratio_mean_6m the fitted sign is +1 against a directi… | -1 | ratio | univariate_direction | train | eq | `[[art:24dcef24:sign_check.pay_ratio_mean_6m.univariate_direction]]` | verified | -1 |
| 54 | conceptual_soundness | On pay_ratio_mean_6m the fitted sign is +1 against a directi… | -0.0009594 | ratio | delta_auc | test | eq | `[[art:54c168fb:ablation.pay_ratio_mean_6m.delta_auc]]` | verified | -0.0009593525391 |
| 55 | conceptual_soundness | On bill_trend_6m the fitted sign is +1 against a direction o… | 1 | ratio | coef_sign |  | eq | `[[art:abd4aaba:sign_check.bill_trend_6m.coef_sign]]` | verified | 1 |
| 56 | conceptual_soundness | On bill_trend_6m the fitted sign is +1 against a direction o… | -1 | ratio | univariate_direction | train | eq | `[[art:a9bff389:sign_check.bill_trend_6m.univariate_direction]]` | verified | -1 |
| 57 | conceptual_soundness | On bill_trend_6m the fitted sign is +1 against a direction o… | -0.0005537 | ratio | delta_auc | test | eq | `[[art:54e6a418:ablation.bill_trend_6m.delta_auc]]` | verified | -0.0005536688856 |
| 58 | conceptual_soundness | On bill_mean_6m the fitted sign is +1 against a direction on… | 1 | ratio | coef_sign |  | eq | `[[art:a457c04a:sign_check.bill_mean_6m.coef_sign]]` | verified | 1 |
| 59 | conceptual_soundness | On bill_mean_6m the fitted sign is +1 against a direction on… | -1 | ratio | univariate_direction | train | eq | `[[art:23b89c5d:sign_check.bill_mean_6m.univariate_direction]]` | verified | -1 |
| 60 | conceptual_soundness | On bill_mean_6m the fitted sign is +1 against a direction on… | -0.005228 | ratio | delta_auc | test | eq | `[[art:a4586b58:ablation.bill_mean_6m.delta_auc]]` | verified | -0.005227961044 |
| 61 | conceptual_soundness | For completeness on the features whose signs do agree, remov… | -0.0009211 | ratio | delta_auc | test | eq | `[[art:43d4225a:ablation.delinq_last.delta_auc]]` | verified | -0.0009210804963 |
| 62 | conceptual_soundness | For completeness on the features whose signs do agree, remov… | -0.0004235 | ratio | delta_auc | test | eq | `[[art:009bc4f1:ablation.utilisation.delta_auc]]` | verified | -0.0004235439401 |
| 63 | conceptual_soundness | For completeness on the features whose signs do agree, remov… | 5.613e-05 | ratio | delta_auc | test | eq | `[[art:786b509d:ablation.age.delta_auc]]` | verified | 5.613232942e-05 |
| 64 | conceptual_soundness | For completeness on the features whose signs do agree, remov… | 5.103e-06 | ratio | delta_auc | test | eq | `[[art:3730f6e2:ablation.delinq_count_6m.delta_auc]]` | verified | 5.102939038e-06 |
| 65 | conceptual_soundness | The challenger reaches an AUC on test of 0.9877 against the… | 0.9877 | ratio | auc | test | eq | `[[art:d2646bc7:challenger.auc]]` | verified | 0.9877299831 |
| 66 | conceptual_soundness | The challenger reaches an AUC on test of 0.9877 against the… | 0.9755 | ratio | auc | test | eq | `[[art:8f522f3b:metrics.test.auc]]` | verified | 0.9755058926 |
| 67 | conceptual_soundness | The challenger reaches an AUC on test of 0.9877 against the… | 0.01222 | ratio | delta_auc | test | eq | `[[art:2ab4af27:challenger.delta_auc]]` | verified | 0.01222409046 |
| 68 | conceptual_soundness | The threshold declared for deciding whether a challenger's l… | 0.03 | ratio | delta_auc |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 69 | conceptual_soundness | On calibration the challenger's Brier score of 0.02542 is lo… | 0.02542 | ratio | brier | test | eq | `[[art:0a224a0a:challenger.brier]]` | verified | 0.02542316584 |
| 70 | conceptual_soundness | On calibration the challenger's Brier score of 0.02542 is lo… | 0.04247 | ratio | brier | test | eq | `[[art:d4f27e13:metrics.test.brier]]` | verified | 0.04247487168 |
| 71 | data_integrity | The training split holds 3500 rows and its largest missing f… | 3500 | count | n | train | eq | `[[art:2510d49d:profile.train.n]]` | verified | 3500 |
| 72 | data_integrity | The training split holds 3500 rows and its largest missing f… | 0 | ratio | missing.max | train | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 73 | data_integrity | The test split holds 1500 rows and its largest missing fract… | 1500 | count | n | test | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 74 | data_integrity | The test split holds 1500 rows and its largest missing fract… | 0 | ratio | missing.max | test | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 75 | data_integrity | The two splits report the same largest missing fraction, so… | 0.1 | ratio | missing_gap |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 76 | data_integrity | The declared stability bound is 0.25 , which the package res… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 77 | data_integrity | The declared stability bound is 0.25 , which the package res… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 78 | data_integrity | The largest train-to-test population stability index, the sc… | 0.01789 | ratio | psi |  | eq | `[[art:1b87de3e:psi.max]]` | verified | 0.01789488592 |
| 79 | data_integrity | The score's own train-to-test shift is 0.01199 , also below… | 0.01199 | ratio | psi |  | eq | `[[art:05f120d2:psi.y_score]]` | verified | 0.01198828928 |
| 80 | data_integrity | - age: 0.008124 | 0.008124 | ratio | psi |  | eq | `[[art:f9255a0a:psi.age]]` | verified | 0.008124281436 |
| 81 | data_integrity | - bill_mean_6m: 0.007124 | 0.007124 | ratio | psi |  | eq | `[[art:028e4281:psi.bill_mean_6m]]` | verified | 0.007124196275 |
| 82 | data_integrity | - bill_trend_6m: 0.00958 | 0.00958 | ratio | psi |  | eq | `[[art:c247a6f2:psi.bill_trend_6m]]` | verified | 0.009579614525 |
| 83 | data_integrity | - delinq_count_6m: 0.002069 | 0.002069 | ratio | psi |  | eq | `[[art:61491d02:psi.delinq_count_6m]]` | verified | 0.002069275496 |
| 84 | data_integrity | - delinq_last: 0.00285 | 0.00285 | ratio | psi |  | eq | `[[art:03bd52e7:psi.delinq_last]]` | verified | 0.002849633848 |
| 85 | data_integrity | - delinq_max_6m: 0.005498 | 0.005498 | ratio | psi |  | eq | `[[art:7a82e7f3:psi.delinq_max_6m]]` | verified | 0.005498249408 |
| 86 | data_integrity | - limit_bal: 0.01095 | 0.01095 | ratio | psi |  | eq | `[[art:601cdba2:psi.limit_bal]]` | verified | 0.01095273358 |
| 87 | data_integrity | - pay_amt_next: 0.01789 | 0.01789 | ratio | psi |  | eq | `[[art:996bb509:psi.pay_amt_next]]` | verified | 0.01789488592 |
| 88 | data_integrity | - pay_ratio_last: 0.004966 | 0.004966 | ratio | psi |  | eq | `[[art:3af2ca29:psi.pay_ratio_last]]` | verified | 0.00496591109 |
| 89 | data_integrity | - pay_ratio_mean_6m: 0.0055 | 0.0055 | ratio | psi |  | eq | `[[art:2c5baeb2:psi.pay_ratio_mean_6m]]` | verified | 0.005500252946 |
| 90 | data_integrity | - utilisation: 0.004244 | 0.004244 | ratio | psi |  | eq | `[[art:451e0780:psi.utilisation]]` | verified | 0.0042440485 |
| 91 | data_integrity | Every one of these marginal shifts sits below the declared b… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 92 | data_integrity | - age: 0.00125 | 0.00125 | ratio | csi |  | eq | `[[art:584faff4:csi.age]]` | verified | 0.00125000439 |
| 93 | data_integrity | - bill_mean_6m: 0.0105 | 0.0105 | ratio | csi |  | eq | `[[art:f374dbd7:csi.bill_mean_6m]]` | verified | 0.01049921023 |
| 94 | data_integrity | - bill_trend_6m: 0.00567 | 0.00567 | ratio | csi |  | eq | `[[art:8bb46253:csi.bill_trend_6m]]` | verified | 0.005670244137 |
| 95 | data_integrity | - delinq_count_6m: 0.002143 | 0.002143 | ratio | csi |  | eq | `[[art:4564aa47:csi.delinq_count_6m]]` | verified | 0.00214274047 |
| 96 | data_integrity | - delinq_last: 0.0295 | 0.0295 | ratio | csi |  | eq | `[[art:cd29d613:csi.delinq_last]]` | verified | 0.02950471301 |
| 97 | data_integrity | - delinq_max_6m: 0.002782 | 0.002782 | ratio | csi |  | eq | `[[art:2fe28db6:csi.delinq_max_6m]]` | verified | 0.002782289452 |
| 98 | data_integrity | - limit_bal: 0.007188 | 0.007188 | ratio | csi |  | eq | `[[art:cb617a64:csi.limit_bal]]` | verified | 0.007188476411 |
| 99 | data_integrity | - pay_amt_next: 0.4064 | 0.4064 | ratio | csi |  | eq | `[[art:e708fa25:csi.pay_amt_next]]` | verified | 0.4063916509 |
| 100 | data_integrity | - pay_ratio_last: 0.003912 | 0.003912 | ratio | csi |  | eq | `[[art:c083b28c:csi.pay_ratio_last]]` | verified | 0.003912462231 |
| 101 | data_integrity | - pay_ratio_mean_6m: 0.003519 | 0.003519 | ratio | csi |  | eq | `[[art:8f1dbe89:csi.pay_ratio_mean_6m]]` | verified | 0.003518997237 |
| 102 | data_integrity | - utilisation: 0.01304 | 0.01304 | ratio | csi |  | eq | `[[art:b1f362df:csi.utilisation]]` | verified | 0.01304415209 |
| 103 | data_integrity | The largest of these contributions is 0.4064 , carried by pa… | 0.4064 | ratio | csi |  | eq | `[[art:3f7f79cf:csi.max]]` | verified | 0.4063916509 |
| 104 | data_integrity | The largest of these contributions is 0.4064 , carried by pa… | 0.4064 | ratio | csi |  | eq | `[[art:e708fa25:csi.pay_amt_next]]` | verified | 0.4063916509 |
| 105 | data_integrity | The largest of these contributions is 0.4064 , carried by pa… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 106 | data_integrity | The comparison between the two stability measures for pay_am… | 0.01789 | ratio | psi |  | eq | `[[art:996bb509:psi.pay_amt_next]]` | verified | 0.01789488592 |
| 107 | data_integrity | The comparison between the two stability measures for pay_am… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 108 | data_integrity | The comparison between the two stability measures for pay_am… | 0.4064 | ratio | csi |  | eq | `[[art:e708fa25:csi.pay_amt_next]]` | verified | 0.4063916509 |
| 109 | data_integrity | No other feature's predictor contribution comes near the bou… | 0.0295 | ratio | csi |  | eq | `[[art:cd29d613:csi.delinq_last]]` | verified | 0.02950471301 |
| 110 | data_integrity | The timing screen flags 1 feature declared during_period or… | 1 | count | n_flagged |  | eq | `[[art:e3a31f6a:leakage.timing.n_flagged]]` | verified | 1 |
| 111 | data_integrity | The strongest single feature reaches an AUC of 0.945 on its… | 0.945 | ratio | max_single_feature_auc |  | eq | `[[art:5b5e98c2:leakage.target_corr.max_single_feature_auc]]` | verified | 0.9449621321 |
| 112 | data_integrity | The strongest single feature reaches an AUC of 0.945 on its… | 0.9 | ratio | single_feature_auc |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 113 | data_integrity | The share of test rows whose identifiers also identify a row… | 0 | ratio | overlap.ids |  | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 114 | data_integrity | The share of test rows whose identifiers also identify a row… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 115 | data_integrity | The share of test rows whose feature values also appear in t… | 0 | ratio | overlap.features |  | eq | `[[art:0fec8048:leakage.overlap.features]]` | verified | 0 |
| 116 | data_integrity | The share of test rows whose feature values also appear in t… | 0.005 | ratio | overlap.features_effective |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 117 | data_integrity | That effective bound is the larger of the declared overlap b… | 0 | ratio | duplicates | train | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 118 | data_integrity | The overall share of test rows also present in train is 0 ,… | 0 | ratio | overlap |  | eq | `[[art:4c9fcd09:leakage.overlap]]` | verified | 0 |
| 119 | data_integrity | The overall share of test rows also present in train is 0 ,… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 120 | data_integrity | The name screen matches 0 feature names against the target-a… | 0 | count | n_matched |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 121 | outcomes | The reason is the observed event rate on the evaluation spli… | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 122 | outcomes | The reason is the observed event rate on the evaluation spli… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 123 | outcomes | \| Rows \| 3500 \| 1500 \| | 3500 | count | n | train | eq | `[[art:564683ee:metrics.train.n]]` | verified | 3500 |
| 124 | outcomes | \| Rows \| 3500 \| 1500 \| | 1500 | count | n | test | eq | `[[art:64fcf14d:metrics.test.n]]` | verified | 1500 |
| 125 | outcomes | \| Observed event rate \| 0.2246 \| 0.2247 \| | 0.2246 | ratio | event_rate | train | eq | `[[art:133a5ff8:metrics.train.event_rate]]` | verified | 0.2245714286 |
| 126 | outcomes | \| Observed event rate \| 0.2246 \| 0.2247 \| | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 127 | outcomes | \| AUC \| 0.9812 \| 0.9755 \| | 0.9812 | ratio | auc | train | eq | `[[art:da2cd01d:metrics.train.auc]]` | verified | 0.9811790152 |
| 128 | outcomes | \| AUC \| 0.9812 \| 0.9755 \| | 0.9755 | ratio | auc | test | eq | `[[art:8f522f3b:metrics.test.auc]]` | verified | 0.9755058926 |
| 129 | outcomes | \| Gini \| 0.9624 \| 0.951 \| | 0.9624 | ratio | gini | train | eq | `[[art:23cb4057:metrics.train.gini]]` | verified | 0.9623580305 |
| 130 | outcomes | \| Gini \| 0.9624 \| 0.951 \| | 0.951 | ratio | gini | test | eq | `[[art:f927e3cd:metrics.test.gini]]` | verified | 0.9510117852 |
| 131 | outcomes | \| KS \| 0.8895 \| 0.8784 \| | 0.8895 | ratio | ks | train | eq | `[[art:7a126f15:metrics.train.ks]]` | verified | 0.8894536106 |
| 132 | outcomes | \| KS \| 0.8895 \| 0.8784 \| | 0.8784 | ratio | ks | test | eq | `[[art:81bee194:metrics.test.ks]]` | verified | 0.8784403377 |
| 133 | outcomes | \| Brier \| 0.03817 \| 0.04247 \| | 0.03817 | ratio | brier | train | eq | `[[art:959b3159:metrics.train.brier]]` | verified | 0.03816687592 |
| 134 | outcomes | \| Brier \| 0.03817 \| 0.04247 \| | 0.04247 | ratio | brier | test | eq | `[[art:d4f27e13:metrics.test.brier]]` | verified | 0.04247487168 |
| 135 | outcomes | \| Log loss \| 0.1505 \| 0.167 \| | 0.1505 | ratio | logloss | train | eq | `[[art:417d98d9:metrics.train.logloss]]` | verified | 0.1504741108 |
| 136 | outcomes | \| Log loss \| 0.1505 \| 0.167 \| | 0.167 | ratio | logloss | test | eq | `[[art:aa620b5e:metrics.test.logloss]]` | verified | 0.1670045909 |
| 137 | outcomes | \| Mean predicted probability \| 0.2246 \| 0.233 \| | 0.2246 | ratio | mean_predicted | train | eq | `[[art:1fa024a6:metrics.train.mean_predicted]]` | verified | 0.2245520437 |
| 138 | outcomes | \| Mean predicted probability \| 0.2246 \| 0.233 \| | 0.233 | ratio | mean_predicted | test | eq | `[[art:0b9b6a1e:metrics.test.mean_predicted]]` | verified | 0.2330182196 |
| 139 | outcomes | Event capture in the highest deciles of predicted probabilit… | 0.8422 | ratio | top2_capture | train | eq | `[[art:55242963:deciles.train.top2_capture]]` | verified | 0.8422391858 |
| 140 | outcomes | Event capture in the highest deciles of predicted probabilit… | 0.822 | ratio | top2_capture | test | eq | `[[art:5690757b:deciles.test.top2_capture]]` | verified | 0.821958457 |
| 141 | outcomes | The train-to-test gap in discrimination was read against a b… | 0.08 | ratio | auc_gap |  | eq | `[[art:630f28f4:threshold.O1.auc_gap]]` | verified | 0.08 |
| 142 | outcomes | The train-to-test gap in discrimination was read against a b… | 0.9812 | ratio | auc | train | eq | `[[art:da2cd01d:metrics.train.auc]]` | verified | 0.9811790152 |
| 143 | outcomes | The train-to-test gap in discrimination was read against a b… | 0.9755 | ratio | auc | test | eq | `[[art:8f522f3b:metrics.test.auc]]` | verified | 0.9755058926 |
| 144 | outcomes | The slope is 1.197 on test, inside the declared band whose b… | 1.197 | ratio | calibration_slope | test | eq | `[[art:c9a03fe6:calibration_slope.test]]` | verified | 1.19744242 |
| 145 | outcomes | The slope is 1.197 on test, inside the declared band whose b… | 0.8 | ratio | calibration_slope |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 146 | outcomes | The slope is 1.197 on test, inside the declared band whose b… | 1.2 | ratio | calibration_slope |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 147 | outcomes | The slope is 1.383 on train, above that top of 1.2 , and thi… | 1.383 | ratio | calibration_slope | train | eq | `[[art:45dafd11:calibration_slope.train]]` | verified | 1.383137681 |
| 148 | outcomes | The slope is 1.383 on train, above that top of 1.2 , and thi… | 1.2 | ratio | calibration_slope |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 149 | outcomes | The intercept is -0.0558 on test and 0.2246 on train. | -0.0558 | ratio | calibration_intercept | test | eq | `[[art:56745cf2:calibration_intercept.test]]` | verified | -0.05579737693 |
| 150 | outcomes | The intercept is -0.0558 on test and 0.2246 on train. | 0.2246 | ratio | calibration_intercept | train | eq | `[[art:d556f341:calibration_intercept.train]]` | verified | 0.2245889138 |
| 151 | outcomes | Mean predicted probability on test is 0.233 against an obser… | 0.233 | ratio | mean_predicted | test | eq | `[[art:0b9b6a1e:metrics.test.mean_predicted]]` | verified | 0.2330182196 |
| 152 | outcomes | Mean predicted probability on test is 0.233 against an obser… | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 153 | outcomes | Mean predicted probability on test is 0.233 against an obser… | 0.03717 | ratio | mean_rel_gap | test | eq | `[[art:6a845d81:calibration.mean_rel_gap.test]]` | verified | 0.0371730842 |
| 154 | outcomes | Mean predicted probability on test is 0.233 against an obser… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 155 | outcomes | The same comparison on train gives 0.2246 against 0.2246 , a… | 0.2246 | ratio | mean_predicted | train | eq | `[[art:1fa024a6:metrics.train.mean_predicted]]` | verified | 0.2245520437 |
| 156 | outcomes | The same comparison on train gives 0.2246 against 0.2246 , a… | 0.2246 | ratio | event_rate | train | eq | `[[art:133a5ff8:metrics.train.event_rate]]` | verified | 0.2245714286 |
| 157 | outcomes | The same comparison on train gives 0.2246 against 0.2246 , a… | 8.632e-05 | ratio | mean_rel_gap | train | eq | `[[art:f7447f34:calibration.mean_rel_gap.train]]` | verified | 8.631936949e-05 |
| 158 | outcomes | The same comparison on train gives 0.2246 against 0.2246 , a… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 159 | outcomes | The group's AUC falls below the split's own by 0.008866 on t… | 0.008866 | ratio | auc_gap | train | eq | `[[art:999aab9c:metrics.train.sub.limit_bal_low.auc_gap]]` | verified | 0.008866169575 |
| 160 | outcomes | The group's AUC falls below the split's own by 0.008866 on t… | 0.008535 | ratio | auc_gap | test | eq | `[[art:6990b76c:metrics.test.sub.limit_bal_low.auc_gap]]` | verified | 0.008535185397 |
| 161 | outcomes | The group's AUC falls below the split's own by 0.008866 on t… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 162 | outcomes | The group holds 0.5037 of train and 0.504 of test, above the… | 0.5037 | ratio | share | train | eq | `[[art:45c51f9e:metrics.train.sub.limit_bal_low.share]]` | verified | 0.5037142857 |
| 163 | outcomes | The group holds 0.5037 of train and 0.504 of test, above the… | 0.504 | ratio | share | test | eq | `[[art:bac689cc:metrics.test.sub.limit_bal_low.share]]` | verified | 0.504 |
| 164 | outcomes | The group holds 0.5037 of train and 0.504 of test, above the… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 165 | outcomes | On train, mean predicted probability is 0.2458 against an ob… | 0.2458 | ratio | mean_predicted | train | eq | `[[art:2086a25d:metrics.train.sub.limit_bal_low.mean_predicted]]` | verified | 0.2457700925 |
| 166 | outcomes | On train, mean predicted probability is 0.2458 against an ob… | 0.2439 | ratio | event_rate | train | eq | `[[art:0ae85aa6:metrics.train.sub.limit_bal_low.event_rate]]` | verified | 0.243902439 |
| 167 | outcomes | On train, mean predicted probability is 0.2458 against an ob… | 0.007657 | ratio | mean_rel_gap | train | eq | `[[art:a93d065e:metrics.train.sub.limit_bal_low.mean_rel_gap]]` | verified | 0.007657379338 |
| 168 | outcomes | On train, mean predicted probability is 0.2458 against an ob… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 169 | outcomes | On test, mean predicted probability is 0.2585 against an obs… | 0.2585 | ratio | mean_predicted | test | eq | `[[art:c1a37d64:metrics.test.sub.limit_bal_low.mean_predicted]]` | verified | 0.2584577028 |
| 170 | outcomes | On test, mean predicted probability is 0.2585 against an obs… | 0.2487 | ratio | event_rate | test | eq | `[[art:de78adb5:metrics.test.sub.limit_bal_low.event_rate]]` | verified | 0.2486772487 |
| 171 | outcomes | On test, mean predicted probability is 0.2585 against an obs… | 0.03933 | ratio | mean_rel_gap | test | eq | `[[art:2b29e325:metrics.test.sub.limit_bal_low.mean_rel_gap]]` | verified | 0.03932991131 |
| 172 | outcomes | The group's AUC sits above the split's own, the recorded gap… | -0.006442 | ratio | auc_gap | train | eq | `[[art:52a49712:metrics.train.sub.limit_bal_high.auc_gap]]` | verified | -0.006441907569 |
| 173 | outcomes | The group's AUC sits above the split's own, the recorded gap… | -0.00586 | ratio | auc_gap | test | eq | `[[art:e37bc8d6:metrics.test.sub.limit_bal_high.auc_gap]]` | verified | -0.005860076588 |
| 174 | outcomes | The group's AUC sits above the split's own, the recorded gap… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 175 | outcomes | The group holds 0.4963 of train and 0.496 of test, above the… | 0.4963 | ratio | share | train | eq | `[[art:2de2a90a:metrics.train.sub.limit_bal_high.share]]` | verified | 0.4962857143 |
| 176 | outcomes | The group holds 0.4963 of train and 0.496 of test, above the… | 0.496 | ratio | share | test | eq | `[[art:ac383ccb:metrics.test.sub.limit_bal_high.share]]` | verified | 0.496 |
| 177 | outcomes | The group holds 0.4963 of train and 0.496 of test, above the… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 178 | outcomes | On train, mean predicted probability is 0.203 against an obs… | 0.203 | ratio | mean_predicted | train | eq | `[[art:b1995539:metrics.train.sub.limit_bal_high.mean_predicted]]` | verified | 0.203016396 |
| 179 | outcomes | On train, mean predicted probability is 0.203 against an obs… | 0.205 | ratio | event_rate | train | eq | `[[art:9de459ef:metrics.train.sub.limit_bal_high.event_rate]]` | verified | 0.2049510651 |
| 180 | outcomes | On train, mean predicted probability is 0.203 against an obs… | 0.00944 | ratio | mean_rel_gap | train | eq | `[[art:58ae0f50:metrics.train.sub.limit_bal_high.mean_rel_gap]]` | verified | 0.009439663314 |
| 181 | outcomes | On train, mean predicted probability is 0.203 against an obs… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 182 | outcomes | On test, mean predicted probability is 0.2072 against an obs… | 0.2072 | ratio | mean_predicted | test | eq | `[[art:f80c93c0:metrics.test.sub.limit_bal_high.mean_predicted]]` | verified | 0.2071684221 |
| 183 | outcomes | On test, mean predicted probability is 0.2072 against an obs… | 0.2003 | ratio | event_rate | test | eq | `[[art:5e9aab40:metrics.test.sub.limit_bal_high.event_rate]]` | verified | 0.2002688172 |
| 184 | outcomes | On test, mean predicted probability is 0.2072 against an obs… | 0.03445 | ratio | mean_rel_gap | test | eq | `[[art:679e4d84:metrics.test.sub.limit_bal_high.mean_rel_gap]]` | verified | 0.03445171844 |
| 185 | outcomes | The group's AUC falls below the split's own by 0.004174 on t… | 0.004174 | ratio | auc_gap | train | eq | `[[art:f90452de:metrics.train.sub.utilisation_high.auc_gap]]` | verified | 0.004173534271 |
| 186 | outcomes | The group's AUC falls below the split's own by 0.004174 on t… | 0.008957 | ratio | auc_gap | test | eq | `[[art:55113529:metrics.test.sub.utilisation_high.auc_gap]]` | verified | 0.008956824296 |
| 187 | outcomes | The group's AUC falls below the split's own by 0.004174 on t… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 188 | outcomes | The group holds 0.5 of train and 0.5 of test, above the floo… | 0.5 | ratio | share | train | eq | `[[art:0ff76e00:metrics.train.sub.utilisation_high.share]]` | verified | 0.5 |
| 189 | outcomes | The group holds 0.5 of train and 0.5 of test, above the floo… | 0.5 | ratio | share | test | eq | `[[art:9404484e:metrics.test.sub.utilisation_high.share]]` | verified | 0.5 |
| 190 | outcomes | The group holds 0.5 of train and 0.5 of test, above the floo… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 191 | outcomes | On train, mean predicted probability is 0.225 against an obs… | 0.225 | ratio | mean_predicted | train | eq | `[[art:c7975c20:metrics.train.sub.utilisation_high.mean_predicted]]` | verified | 0.2249819108 |
| 192 | outcomes | On train, mean predicted probability is 0.225 against an obs… | 0.2246 | ratio | event_rate | train | eq | `[[art:0055e6aa:metrics.train.sub.utilisation_high.event_rate]]` | verified | 0.2245714286 |
| 193 | outcomes | On train, mean predicted probability is 0.225 against an obs… | 0.001828 | ratio | mean_rel_gap | train | eq | `[[art:86210ecf:metrics.train.sub.utilisation_high.mean_rel_gap]]` | verified | 0.001827847231 |
| 194 | outcomes | On train, mean predicted probability is 0.225 against an obs… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 195 | outcomes | On test, mean predicted probability is 0.2406 against an obs… | 0.2406 | ratio | mean_predicted | test | eq | `[[art:893eaa1e:metrics.test.sub.utilisation_high.mean_predicted]]` | verified | 0.2405954077 |
| 196 | outcomes | On test, mean predicted probability is 0.2406 against an obs… | 0.2333 | ratio | event_rate | test | eq | `[[art:8e66209c:metrics.test.sub.utilisation_high.event_rate]]` | verified | 0.2333333333 |
| 197 | outcomes | On test, mean predicted probability is 0.2406 against an obs… | 0.03112 | ratio | mean_rel_gap | test | eq | `[[art:e10c751a:metrics.test.sub.utilisation_high.mean_rel_gap]]` | verified | 0.03112317569 |
| 198 | outcomes | The group's AUC sits above the split's own, the recorded gap… | -0.008041 | ratio | auc_gap | train | eq | `[[art:6c1cbaed:metrics.train.sub.utilisation_low.auc_gap]]` | verified | -0.008040956233 |
| 199 | outcomes | The group's AUC sits above the split's own, the recorded gap… | -0.01238 | ratio | auc_gap | test | eq | `[[art:469220d0:metrics.test.sub.utilisation_low.auc_gap]]` | verified | -0.01237938495 |
| 200 | outcomes | The group's AUC sits above the split's own, the recorded gap… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 201 | outcomes | The group holds 0.5 of train and 0.5 of test, above the floo… | 0.5 | ratio | share | train | eq | `[[art:31f26e20:metrics.train.sub.utilisation_low.share]]` | verified | 0.5 |
| 202 | outcomes | The group holds 0.5 of train and 0.5 of test, above the floo… | 0.5 | ratio | share | test | eq | `[[art:7860a748:metrics.test.sub.utilisation_low.share]]` | verified | 0.5 |
| 203 | outcomes | The group holds 0.5 of train and 0.5 of test, above the floo… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 204 | outcomes | On train, mean predicted probability is 0.2241 against an ob… | 0.2241 | ratio | mean_predicted | train | eq | `[[art:7648c23f:metrics.train.sub.utilisation_low.mean_predicted]]` | verified | 0.2241221766 |
| 205 | outcomes | On train, mean predicted probability is 0.2241 against an ob… | 0.2246 | ratio | event_rate | train | eq | `[[art:bbabdd5d:metrics.train.sub.utilisation_low.event_rate]]` | verified | 0.2245714286 |
| 206 | outcomes | On train, mean predicted probability is 0.2241 against an ob… | 0.002 | ratio | mean_rel_gap | train | eq | `[[art:de6fc46d:metrics.train.sub.utilisation_low.mean_rel_gap]]` | verified | 0.00200048597 |
| 207 | outcomes | On train, mean predicted probability is 0.2241 against an ob… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 208 | outcomes | On test, mean predicted probability is 0.2254 against an obs… | 0.2254 | ratio | mean_predicted | test | eq | `[[art:f2a826ca:metrics.test.sub.utilisation_low.mean_predicted]]` | verified | 0.2254410315 |
| 209 | outcomes | On test, mean predicted probability is 0.2254 against an obs… | 0.216 | ratio | event_rate | test | eq | `[[art:b0ad49be:metrics.test.sub.utilisation_low.event_rate]]` | verified | 0.216 |
| 210 | outcomes | On test, mean predicted probability is 0.2254 against an obs… | 0.04371 | ratio | mean_rel_gap | test | eq | `[[art:dfa4be18:metrics.test.sub.utilisation_low.mean_rel_gap]]` | verified | 0.04370847918 |
| 211 | sensitivity | The largest variance inflation factor across the retained fe… | 8.181 | ratio | vif |  | eq | `[[art:4afdc4f1:vif.max]]` | verified | 8.181114607 |
| 212 | sensitivity | The largest variance inflation factor across the retained fe… | 10 | ratio | vif |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 213 | sensitivity | The condition number of the column-standardised design is 6.… | 6.185 | ratio | condition_number |  | eq | `[[art:36392379:condition_number]]` | verified | 6.185189657 |
| 214 | sensitivity | The condition number of the column-standardised design is 6.… | 30 | ratio | condition_number |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 215 | sensitivity | The six-month mean billing feature carries the largest value… | 8.181 | ratio | vif |  | eq | `[[art:d5ab7306:vif.bill_mean_6m]]` | verified | 8.181114607 |
| 216 | sensitivity | The six-month mean billing feature carries the largest value… | 7.526 | ratio | vif |  | eq | `[[art:000b6208:vif.pay_ratio_mean_6m]]` | verified | 7.525569541 |
| 217 | sensitivity | The six-month mean billing feature carries the largest value… | 7.268 | ratio | vif |  | eq | `[[art:bec24796:vif.pay_ratio_last]]` | verified | 7.267755553 |
| 218 | sensitivity | These three sit above the credit-limit feature at 4.81 and t… | 4.81 | ratio | vif |  | eq | `[[art:8209ea46:vif.limit_bal]]` | verified | 4.809808481 |
| 219 | sensitivity | These three sit above the credit-limit feature at 4.81 and t… | 3.215 | ratio | vif |  | eq | `[[art:ec978947:vif.utilisation]]` | verified | 3.215174221 |
| 220 | sensitivity | The delinquency block is more modest: the six-month delinque… | 2.561 | ratio | vif |  | eq | `[[art:87890613:vif.delinq_count_6m]]` | verified | 2.56148636 |
| 221 | sensitivity | The delinquency block is more modest: the six-month delinque… | 2.408 | ratio | vif |  | eq | `[[art:4b239ec5:vif.delinq_max_6m]]` | verified | 2.408148028 |
| 222 | sensitivity | The delinquency block is more modest: the six-month delinque… | 1.422 | ratio | vif |  | eq | `[[art:c18221d4:vif.delinq_last]]` | verified | 1.422439811 |
| 223 | sensitivity | The next-period payment amount is at 2.206 , the six-month b… | 2.206 | ratio | vif |  | eq | `[[art:68806d80:vif.pay_amt_next]]` | verified | 2.206074628 |
| 224 | sensitivity | The next-period payment amount is at 2.206 , the six-month b… | 1.225 | ratio | vif |  | eq | `[[art:0cb3df89:vif.bill_trend_6m]]` | verified | 1.225337779 |
| 225 | sensitivity | The next-period payment amount is at 2.206 , the six-month b… | 1.002 | ratio | vif |  | eq | `[[art:8021b06e:vif.age]]` | verified | 1.002328679 |
| 226 | findings | The package declares `pay_amt_next` with a timing that falls… | 1 | count | n_flagged |  | eq | `[[art:e3a31f6a:leakage.timing.n_flagged]]` | verified | 1 |
| 227 | findings | That same feature separates the outcome on its own at an AUC… | 0.945 | ratio | max_single_feature_auc |  | eq | `[[art:5b5e98c2:leakage.target_corr.max_single_feature_auc]]` | verified | 0.9449621321 |
| 228 | findings | That same feature separates the outcome on its own at an AUC… | 0.9 | ratio | single_feature_auc |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 229 | findings | The logistic regression of the outcome on the model's logit… | 1.383 | ratio | calibration_slope | train | eq | `[[art:45dafd11:calibration_slope.train]]` | verified | 1.383137681 |
| 230 | findings | The logistic regression of the outcome on the model's logit… | 1.2 | ratio | calibration_slope |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 231 | findings | Can the model developer explain what the model is discrimina… | 1 | ratio | coef_sign |  | eq | `[[art:a457c04a:sign_check.bill_mean_6m.coef_sign]]` | verified | 1 |
| 232 | findings | Can the model developer explain what the model is discrimina… | -1 | ratio | univariate_direction |  | eq | `[[art:23b89c5d:sign_check.bill_mean_6m.univariate_direction]]` | verified | -1 |
| 233 | findings | Can the model developer explain what the model is discrimina… | 0 | ratio | agrees |  | eq | `[[art:4df8b747:sign_check.bill_mean_6m.agrees]]` | verified | 0 |
| 234 | findings | Can the model developer explain what the model is discrimina… | 1 | ratio | coef_sign |  | eq | `[[art:abd4aaba:sign_check.bill_trend_6m.coef_sign]]` | verified | 1 |
| 235 | findings | Can the model developer explain what the model is discrimina… | -1 | ratio | univariate_direction |  | eq | `[[art:a9bff389:sign_check.bill_trend_6m.univariate_direction]]` | verified | -1 |
| 236 | findings | Can the model developer explain what the model is discrimina… | 0 | ratio | agrees |  | eq | `[[art:c0f6d07d:sign_check.bill_trend_6m.agrees]]` | verified | 0 |
| 237 | findings | Can the model developer explain what the model is discrimina… | -1 | ratio | coef_sign |  | eq | `[[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]]` | verified | -1 |
| 238 | findings | Can the model developer explain what the model is discrimina… | 1 | ratio | univariate_direction |  | eq | `[[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]]` | verified | 1 |
| 239 | findings | Can the model developer explain what the model is discrimina… | 0 | ratio | agrees |  | eq | `[[art:c946359c:sign_check.delinq_max_6m.agrees]]` | verified | 0 |
| 240 | findings | Can the model developer explain what the model is discrimina… | 1 | ratio | coef_sign |  | eq | `[[art:6af6aef2:sign_check.limit_bal.coef_sign]]` | verified | 1 |
| 241 | findings | Can the model developer explain what the model is discrimina… | -1 | ratio | univariate_direction |  | eq | `[[art:56d284d6:sign_check.limit_bal.univariate_direction]]` | verified | -1 |
| 242 | findings | Can the model developer explain what the model is discrimina… | 0 | ratio | agrees |  | eq | `[[art:0278aad1:sign_check.limit_bal.agrees]]` | verified | 0 |
| 243 | findings | Can the model developer explain what the model is discrimina… | 1 | ratio | coef_sign |  | eq | `[[art:f018263e:sign_check.pay_ratio_last.coef_sign]]` | verified | 1 |
| 244 | findings | Can the model developer explain what the model is discrimina… | -1 | ratio | univariate_direction |  | eq | `[[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]]` | verified | -1 |
| 245 | findings | Can the model developer explain what the model is discrimina… | 0 | ratio | agrees |  | eq | `[[art:79abee77:sign_check.pay_ratio_last.agrees]]` | verified | 0 |
| 246 | findings | Can the model developer explain what the model is discrimina… | 1 | ratio | coef_sign |  | eq | `[[art:8547787e:sign_check.pay_ratio_mean_6m.coef_sign]]` | verified | 1 |
| 247 | findings | Can the model developer explain what the model is discrimina… | -1 | ratio | univariate_direction |  | eq | `[[art:24dcef24:sign_check.pay_ratio_mean_6m.univariate_direction]]` | verified | -1 |
| 248 | findings | Can the model developer explain what the model is discrimina… | 0 | ratio | agrees |  | eq | `[[art:51914c14:sign_check.pay_ratio_mean_6m.agrees]]` | verified | 0 |
| 249 | monitoring | **Discrimination.** Recompute AUC on each production vintage… | 0.7 | ratio | auc | test | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 250 | monitoring | The value on the evaluation split was 0.9755 , which lies ab… | 0.9755 | ratio | auc | test | eq | `[[art:8f522f3b:metrics.test.auc]]` | verified | 0.9755058926 |
| 251 | monitoring | **Accuracy of the probabilities.** Track the Brier score on… | 0.2 | ratio | brier | test | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 252 | monitoring | **Accuracy of the probabilities.** Track the Brier score on… | 0.04247 | ratio | brier | test | eq | `[[art:d4f27e13:metrics.test.brier]]` | verified | 0.04247487168 |
| 253 | monitoring | **Calibration.** Refit the logistic regression of the outcom… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 254 | monitoring | **Calibration.** Refit the logistic regression of the outcom… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 255 | monitoring | The slope on the evaluation split was 1.197 , which lies ins… | 1.197 | ratio | calibration_slope | test | eq | `[[art:c9a03fe6:calibration_slope.test]]` | verified | 1.19744242 |
| 256 | monitoring | **Input and score stability.** Recompute the population stab… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 257 | monitoring | The largest train-to-test value seen in this validation was… | 0.01789 | ratio | psi |  | eq | `[[art:1b87de3e:psi.max]]` | verified | 0.01789488592 |
| 258 | monitoring | **Ordering of the monitoring report.** A monitoring report f… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |

## Appendix B — Artifact index

The store holds 274 artifacts; the 190 this report cites or rests a finding on are indexed here.

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
| `leakage.timing` | `0dad290e` | table | table, 13 rows | each feature's declared timing; flagged means during or after the outcome |
| `leakage.timing.n_flagged` | `e3a31f6a` | scalar | 1 | features declared during_period or after_outcome |
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
| `metrics.test.sub.utilisation_high` | `2199f7de` | table | table, 10 rows | every metric on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.auc_gap` | `55113529` | scalar | 0.008956824296 | how far AUC on the utilisation above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.utilisation_high.event_rate` | `8e66209c` | scalar | 0.2333333333 | event_rate on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.mean_predicted` | `893eaa1e` | scalar | 0.2405954077 | mean_predicted on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.mean_rel_gap` | `e10c751a` | scalar | 0.03112317569 | mean predicted against observed on the utilisation above_median slice of test, relative |
| `metrics.test.sub.utilisation_high.share` | `9404484e` | scalar | 0.5 | the share of test the utilisation above_median slice holds |
| `metrics.test.sub.utilisation_low` | `22a4e77a` | table | table, 10 rows | every metric on the utilisation below_median slice of test |
| `metrics.test.sub.utilisation_low.auc_gap` | `469220d0` | scalar | -0.01237938495 | how far AUC on the utilisation below_median slice of test falls below AUC on all of test |
| `metrics.test.sub.utilisation_low.event_rate` | `b0ad49be` | scalar | 0.216 | event_rate on the utilisation below_median slice of test |
| `metrics.test.sub.utilisation_low.mean_predicted` | `f2a826ca` | scalar | 0.2254410315 | mean_predicted on the utilisation below_median slice of test |
| `metrics.test.sub.utilisation_low.mean_rel_gap` | `dfa4be18` | scalar | 0.04370847918 | mean predicted against observed on the utilisation below_median slice of test, relative |
| `metrics.test.sub.utilisation_low.share` | `7860a748` | scalar | 0.5 | the share of test the utilisation below_median slice holds |
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
| `metrics.train.sub.utilisation_high` | `ea5149a8` | table | table, 10 rows | every metric on the utilisation above_median slice of train |
| `metrics.train.sub.utilisation_high.auc_gap` | `f90452de` | scalar | 0.004173534271 | how far AUC on the utilisation above_median slice of train falls below AUC on all of train |
| `metrics.train.sub.utilisation_high.event_rate` | `0055e6aa` | scalar | 0.2245714286 | event_rate on the utilisation above_median slice of train |
| `metrics.train.sub.utilisation_high.mean_predicted` | `c7975c20` | scalar | 0.2249819108 | mean_predicted on the utilisation above_median slice of train |
| `metrics.train.sub.utilisation_high.mean_rel_gap` | `86210ecf` | scalar | 0.001827847231 | mean predicted against observed on the utilisation above_median slice of train, relative |
| `metrics.train.sub.utilisation_high.share` | `0ff76e00` | scalar | 0.5 | the share of train the utilisation above_median slice holds |
| `metrics.train.sub.utilisation_low` | `db4b269d` | table | table, 10 rows | every metric on the utilisation below_median slice of train |
| `metrics.train.sub.utilisation_low.auc_gap` | `6c1cbaed` | scalar | -0.008040956233 | how far AUC on the utilisation below_median slice of train falls below AUC on all of train |
| `metrics.train.sub.utilisation_low.event_rate` | `bbabdd5d` | scalar | 0.2245714286 | event_rate on the utilisation below_median slice of train |
| `metrics.train.sub.utilisation_low.mean_predicted` | `7648c23f` | scalar | 0.2241221766 | mean_predicted on the utilisation below_median slice of train |
| `metrics.train.sub.utilisation_low.mean_rel_gap` | `de6fc46d` | scalar | 0.00200048597 | mean predicted against observed on the utilisation below_median slice of train, relative |
| `metrics.train.sub.utilisation_low.share` | `31f26e20` | scalar | 0.5 | the share of train the utilisation below_median slice holds |
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
| `run.features` | `7276ca89` | json | json | the subject's features.json |
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
| `sign_check.delinq_last.coef_sign` | `50d352f8` | scalar | 1 | the sign of the fitted coefficient on delinq_last |
| `sign_check.delinq_last.univariate_direction` | `a78648ba` | scalar | 1 | the sign of delinq_last's own single-feature AUC on train minus 0.5 |
| `sign_check.delinq_max_6m.agrees` | `c946359c` | scalar | 0 | 1 when the fitted sign on delinq_max_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.delinq_max_6m.coef_sign` | `a07d68ab` | scalar | -1 | the sign of the fitted coefficient on delinq_max_6m |
| `sign_check.delinq_max_6m.univariate_direction` | `b9088f4a` | scalar | 1 | the sign of delinq_max_6m's own single-feature AUC on train minus 0.5 |
| `sign_check.limit_bal.agrees` | `0278aad1` | scalar | 0 | 1 when the fitted sign on limit_bal agrees with its univariate direction, 0 when it does not |
| `sign_check.limit_bal.coef_sign` | `6af6aef2` | scalar | 1 | the sign of the fitted coefficient on limit_bal |
| `sign_check.limit_bal.univariate_direction` | `56d284d6` | scalar | -1 | the sign of limit_bal's own single-feature AUC on train minus 0.5 |
| `sign_check.n_disagreements` | `75159a84` | scalar | 6 | retained features whose fitted sign contradicts their univariate direction, of 11 checked |
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
| tokens in / out | 254,854 / 102,175 |
| notional cost (USD) | 5.1594 |
| wall-clock (s) | 1076.49 |
| subject run (s) | 1.17 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | credit_default-full_agent-20260920T065312Z-e2e51e00 |

## Appendix D — Not checked

| item | reason |
|---|---|
| `check_stability` (R1) | package declares no `regime.column` |
| `run_scenarios` (X1) | not applicable to `binary_classification` |
| out-of-time and vintage-holdout metrics (O1, second rule) | package declares neither split |
| developer claims (T1, claim channel) | The package declares 2 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
