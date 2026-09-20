---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: full_agent
model: claude-opus-5[1m]
run_id: credit_default-full_agent-20260918T222547Z-e2e51e00
data_mode: synthetic
synthetic_n: 5000
grounding_precision_pre: 0.9924
grounding_precision_post: 1.0000
n_claims: 264
n_findings_by_severity: {high: 0, medium: 0, low: 1, info: 0}
generated: "2026-09-18T22:25:47Z"
illustrative: false
---

# Validation report — `credit_default` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `credit_default` v1.0 | `full_agent` | claude-opus-5[1m] | synthetic, n = 5000 | 0.9924 → 1.0000 | 0 / 0 / 1 / 0 |
<!-- quaestor:renderer:end -->

The subject of this report is the credit_default model package, a binary classification model that predicts the probability a borrower defaults, and this review is organised around the Federal Reserve's guidance on model validation and monitoring [[reg:SR26-2:V]].

The subject was run under the wall-clock cap of 300 [[art:2ad8d1a5:runtime.max_seconds]] seconds that the package declares, and the metrics reported here were recomputed by the validator from the subject's own scored outputs rather than taken from the developer's reported values, in the spirit of outcomes analysis [[reg:SR26-2:V.1.b]].
The training split holds 3500 [[art:2510d49d:profile.train.n]] rows and the test split holds 1500 [[art:2193cf5f:profile.test.n]] rows.

The model passes the developer-declared discrimination floor, with an AUC on test of 0.748 [[art:5c6c2bfc:metrics.test.auc]] against a declared minimum of 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]].
It passes the declared accuracy ceiling, with a Brier score on test of 0.1489 [[art:bbe69430:metrics.test.brier]] against a declared maximum of 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]].
It passes the declared calibration band, with a calibration slope on test of 1.003 [[art:b7dbb687:calibration_slope.test]] sitting inside a declared floor of 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] and a declared ceiling of 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
It passes the declared stability ceiling, with a largest train-to-test population stability index of 0.01095 [[art:381b2570:psi.max]] against a declared maximum of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].

Discrimination on train, at 0.7584 [[art:14b38a2b:metrics.train.auc]], stands above discrimination on test, at 0.748 [[art:5c6c2bfc:metrics.test.auc]].
In aggregate the mean predicted probability on test, at 0.2211 [[art:4d2f8a37:metrics.test.mean_predicted]], falls just below the observed event rate on test, at 0.2247 [[art:9209d200:metrics.test.event_rate]].
Discrimination is not uniform across the utilisation sub-populations of test: AUC is 0.8986 [[art:f85acc05:metrics.test.sub.utilisation_low.auc]] on the below-median slice and 0.5689 [[art:13b21546:metrics.test.sub.utilisation_high.auc]] on the above-median slice, and taken as a difference against AUC on all of test those slices stand at -0.1506 [[art:f391975a:metrics.test.sub.utilisation_low.auc_gap]] and 0.1791 [[art:e0dc4aa9:metrics.test.sub.utilisation_high.auc_gap]] respectively.

The findings this validation raised are counted by severity in the scope table above and written out in full in the findings section below.
They consist of F-001, a E1 effective challenge finding at low severity, raised by the challenger comparison.

## 2. Conceptual soundness

Validating conceptual soundness means assessing and documenting model design, construction, and developmental evidence, and subjecting the key modeling choices to critical analysis [[reg:SR26-2:V.1.a]].

### Design and feature timing

The champion is a logistic regression with an intercept of -1.396 [[art:74c10f15:run.model_summary#intercept]] fitted on 3500 [[art:74c10f15:run.model_summary#n_train]] training rows, scoring 0.748 [[art:5c6c2bfc:metrics.test.auc]] on test by AUC and 0.1489 [[art:bbe69430:metrics.test.brier]] by Brier score.
The subject's feature inventory carries 12 [[art:abbb748e:run.features#n]] features in total.
Of these, 2 [[art:abbb748e:run.features#at_origination]] are known at origination and 10 [[art:abbb748e:run.features#before_period_start]] are known before the performance period starts.
The inventory records 0 [[art:abbb748e:run.features#during_period]] features observed during the performance period and 0 [[art:abbb748e:run.features#after_outcome]] observed after the outcome, so on the timing evidence in this inventory no input is dated later than the point at which the model is meant to score.

### The developer's own screen

The developer applied a variance-inflation screen at a threshold of 10 [[art:74c10f15:run.model_summary#vif_threshold]] and dropped two collinear billing features on that basis.
The last bill amount was removed at a variance inflation of 160.9 [[art:74c10f15:run.model_summary#removed.bill_last.vif]], far above that threshold, and the six-month mean utilisation at 36.36 [[art:74c10f15:run.model_summary#removed.utilisation_mean_6m.vif]], also above it.
Both removals are consistent with the stated screen, and both dropped features have near-substitutes still in the model, so the screen removed redundancy rather than information.

### Coefficients and expected direction

The largest coefficient in magnitude is on the most recent delinquency status at 0.7334 [[art:74c10f15:run.model_summary#coefficients.delinq_last.value]], positive, which is what credit subject matter expects: more recent delinquency raises default risk.
Next in magnitude are the six-month mean bill amount at -0.3726 [[art:74c10f15:run.model_summary#coefficients.bill_mean_6m.value]], the six-month mean payment ratio at -0.3554 [[art:74c10f15:run.model_summary#coefficients.pay_ratio_mean_6m.value]], utilisation at 0.2662 [[art:74c10f15:run.model_summary#coefficients.utilisation.value]] and the six-month bill trend at -0.2225 [[art:74c10f15:run.model_summary#coefficients.bill_trend_6m.value]].
A negative weight on the mean payment ratio and a positive weight on utilisation both match the expectation that paying down more of the balance lowers risk while drawing more of the line raises it.
The remaining weights are smaller: the credit limit at 0.07266 [[art:74c10f15:run.model_summary#coefficients.limit_bal.value]], age at -0.06726 [[art:74c10f15:run.model_summary#coefficients.age.value]], the six-month delinquency count at 0.1226 [[art:74c10f15:run.model_summary#coefficients.delinq_count_6m.value]], the last payment ratio at 0.1026 [[art:74c10f15:run.model_summary#coefficients.pay_ratio_last.value]] and the six-month maximum delinquency at -0.03221 [[art:74c10f15:run.model_summary#coefficients.delinq_max_6m.value]].

### Fitted signs against univariate direction

The sign comparison records 3 [[art:e223cd4a:sign_check.n_disagreements]] retained features whose fitted sign contradicts the direction of their own single-feature relationship with the outcome on train.
These comparisons are evidence about the design, not the subject of any declared bound, and nothing here is reported as a finding.

The credit limit is fitted positive, at a coefficient sign of 1 [[art:6af6aef2:sign_check.limit_bal.coef_sign]], while on its own it points the other way, at -1 [[art:56d284d6:sign_check.limit_bal.univariate_direction]], so the agreement flag is 0 [[art:0278aad1:sign_check.limit_bal.agrees]].
Refitting the champion's form without the credit limit changes test AUC by 0.0004286 [[art:63faa640:ablation.limit_bal.delta_auc]] from a baseline of 0.748 [[art:3a44e438:ablation.baseline_auc]], an improvement rather than a loss, so the model is not leaning on this feature and the sign reversal carries little weight in the score.

The most recent payment ratio is likewise fitted positive, at 1 [[art:f018263e:sign_check.pay_ratio_last.coef_sign]], against a univariate direction of -1 [[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]], with an agreement flag of 0 [[art:79abee77:sign_check.pay_ratio_last.agrees]].
This is the harder one to defend in subject-matter terms, since a higher recent payment ratio raising the fitted probability of default runs against the credit intuition, and the six-month mean of the same quantity is fitted negative at -0.3554 [[art:74c10f15:run.model_summary#coefficients.pay_ratio_mean_6m.value]], a pattern consistent with the two correlated payment-ratio terms splitting a single effect between them.
Dropping the most recent payment ratio and refitting changes test AUC by 0.002411 [[art:5f39089e:ablation.pay_ratio_last.delta_auc]], again an increase from the baseline of 0.748 [[art:3a44e438:ablation.baseline_auc]], so the reversed sign sits on a term the model does not need for discrimination.

The six-month maximum delinquency is fitted negative, at -1 [[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]], against a univariate direction of 1 [[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]], with an agreement flag of 0 [[art:c946359c:sign_check.delinq_max_6m.agrees]].
A negative weight on the worst delinquency seen in six months contradicts the expectation that worse delinquency raises risk, and it is plausibly absorbed by the most recent delinquency status, whose weight of 0.7334 [[art:74c10f15:run.model_summary#coefficients.delinq_last.value]] dominates the model.
Removing it changes test AUC by 0.0003598 [[art:3a0d3a0c:ablation.delinq_max_6m.delta_auc]], an increase, so the discrimination lost by dropping the contrary term is nil and the reversal is a presentational rather than a predictive problem.

The other seven retained features agree with their own direction: age at -1 [[art:6172eb93:sign_check.age.coef_sign]] against -1 [[art:66364583:sign_check.age.univariate_direction]], flag 1 [[art:4116add1:sign_check.age.agrees]]; utilisation at 1 [[art:85badc3c:sign_check.utilisation.coef_sign]] against 1 [[art:f0995196:sign_check.utilisation.univariate_direction]], flag 1 [[art:d0c9a130:sign_check.utilisation.agrees]]; the mean payment ratio at -1 [[art:077bb6b2:sign_check.pay_ratio_mean_6m.coef_sign]] against -1 [[art:24dcef24:sign_check.pay_ratio_mean_6m.univariate_direction]], flag 1 [[art:7e9a76ca:sign_check.pay_ratio_mean_6m.agrees]]; the most recent delinquency at 1 [[art:50d352f8:sign_check.delinq_last.coef_sign]] against 1 [[art:a78648ba:sign_check.delinq_last.univariate_direction]], flag 1 [[art:a8ba9372:sign_check.delinq_last.agrees]]; the delinquency count at 1 [[art:17afb6f9:sign_check.delinq_count_6m.coef_sign]] against 1 [[art:549e904e:sign_check.delinq_count_6m.univariate_direction]], flag 1 [[art:a337d16b:sign_check.delinq_count_6m.agrees]]; the mean bill amount at -1 [[art:cee1a18f:sign_check.bill_mean_6m.coef_sign]] against -1 [[art:23b89c5d:sign_check.bill_mean_6m.univariate_direction]], flag 1 [[art:89279c3b:sign_check.bill_mean_6m.agrees]]; and the bill trend at -1 [[art:7fd8474e:sign_check.bill_trend_6m.coef_sign]] against -1 [[art:a9bff389:sign_check.bill_trend_6m.univariate_direction]], flag 1 [[art:ff3cb24a:sign_check.bill_trend_6m.agrees]].

### What the model actually leans on

The leave-one-out refits, all measured against a baseline test AUC of 0.748 [[art:3a44e438:ablation.baseline_auc]], show the discrimination concentrated in very few terms.
Dropping the most recent delinquency status changes test AUC by -0.07585 [[art:3150b111:ablation.delinq_last.delta_auc]], and dropping utilisation changes it by -0.01977 [[art:d4ad2039:ablation.utilisation.delta_auc]]; these are the two features the model genuinely depends on, and both carry signs the subject matter expects.
The six-month mean bill amount contributes as well, at -0.0016 [[art:3b91a889:ablation.bill_mean_6m.delta_auc]], a smaller loss than either of those two.
Every other retained feature has a non-negative ablation delta — age at 8.675e-05 [[art:59398b1b:ablation.age.delta_auc]], the delinquency count at 0.0006812 [[art:c5659def:ablation.delinq_count_6m.delta_auc]], the delinquency maximum at 0.0003598 [[art:3a0d3a0c:ablation.delinq_max_6m.delta_auc]], the credit limit at 0.0004286 [[art:63faa640:ablation.limit_bal.delta_auc]], the last payment ratio at 0.002411 [[art:5f39089e:ablation.pay_ratio_last.delta_auc]], the mean payment ratio at 0.006603 [[art:90fa1178:ablation.pay_ratio_mean_6m.delta_auc]] and the bill trend at 0.003279 [[art:096d7f98:ablation.bill_trend_6m.delta_auc]] — meaning the refit scores at least as well without them.
The largest such increase is on the six-month mean payment ratio at 0.006603 [[art:90fa1178:ablation.pay_ratio_mean_6m.delta_auc]], which is also the feature with the second-largest fitted weight in magnitude, and the combination of a large weight with a positive ablation delta is the signature of collinearity the variance-inflation screen did not fully clear.
A specification carrying several terms whose removal improves out-of-sample discrimination is over-parameterised for the signal it contains, and a validator should read the retained feature set as broader than the evidence supports.

### Effective challenge

A gradient-boosting challenger was fitted on the same data and reaches a test AUC of 0.824 [[art:bf5be719:challenger.auc]] against the champion's 0.748 [[art:5c6c2bfc:metrics.test.auc]], a lead of 0.07598 [[art:c9e502ae:challenger.delta_auc]].
That lead is read against a declared effective-challenge bound of 0.03 [[art:e042774c:threshold.E1.delta_auc]], and it sits above that bound.
The challenger is also better calibrated on test, with a Brier score of 0.1258 [[art:f9e0583d:challenger.brier]] against the champion's 0.1489 [[art:bbe69430:metrics.test.brier]]; the challenger leads on both the discrimination and the calibration comparison, and each is a difference in the challenger's favour rather than a ratio.
This exceedance is raised as finding E1, and it is a statement about the champion's functional form: a linear-in-log-odds specification is leaving structure on the table that a non-linear learner recovers from the same inputs.
The conclusion belongs to the design of the model rather than to its implementation or its data, and the reader is referred to the findings section for E1 and its disposition.

### Judgement

The feature timing in the subject's own inventory is clean, the collinearity screen was applied at its stated bound and removed two features well above it, and the two terms carrying almost all of the discrimination have signs that match credit subject-matter expectation.
Against that, 3 [[art:e223cd4a:sign_check.n_disagreements]] retained features are fitted against their own univariate direction, each of them on a term whose removal leaves test AUC no worse, and a further group of retained terms likewise contributes nothing to out-of-sample discrimination.
The design is defensible in its core but loose at its edges, and the margin by which the challenger clears the effective-challenge bound puts the linear functional form itself in question.

## 3. Data integrity and drift

Model testing includes a critical assessment of data quality, relevance, and inputs, and this section reports the data checks run on the package's splits [[reg:SR26-2:IV.1]].

### Splits and missingness

The training split holds 3500 rows [[art:2510d49d:profile.train.n]] and the test split holds 1500 rows [[art:2193cf5f:profile.test.n]].
The largest missing fraction in the training split is 0 [[art:050a3099:profile.train.missing.max]], and the largest missing fraction in the test split is 0 [[art:f813848d:profile.test.missing.max]].
The comparison the rule makes across the two splits is the difference between those split maxima, not their ratio, and because the two readings are equal that difference falls below the bound of 0.1 [[art:9cce25ea:threshold.D1.missing_gap]].

### Population and characteristic stability

The largest train-to-test population stability reading, the score included, is 0.01095 [[art:381b2570:psi.max]], below the stability bound of 0.25 [[art:278b9016:threshold.S1.psi]], which the package declares at 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
That maximum is carried by the credit-limit characteristic at 0.01095 [[art:601cdba2:psi.limit_bal]], and the score itself shifts by 0.007023 [[art:a2885abf:psi.y_score]].
The remaining population readings are 0.008124 [[art:f9255a0a:psi.age]] for age, 0.004244 [[art:451e0780:psi.utilisation]] for utilisation, 0.004966 [[art:3af2ca29:psi.pay_ratio_last]] and 0.0055 [[art:2c5baeb2:psi.pay_ratio_mean_6m]] for the payment-ratio characteristics, 0.00285 [[art:03bd52e7:psi.delinq_last]], 0.002069 [[art:61491d02:psi.delinq_count_6m]] and 0.005498 [[art:7a82e7f3:psi.delinq_max_6m]] for the delinquency characteristics, and 0.007124 [[art:028e4281:psi.bill_mean_6m]] and 0.00958 [[art:c247a6f2:psi.bill_trend_6m]] for the billing characteristics.
Each of those readings sits below the stability bound of 0.25 [[art:278b9016:threshold.S1.psi]].

The largest characteristic contribution to the shift in the linear predictor is 0.02363 [[art:e56cb179:csi.max]], carried by the most recent delinquency characteristic at 0.02363 [[art:5babe364:csi.delinq_last]], below the same declared bound of 0.25 [[art:278b9016:threshold.S1.psi]].
The other contributions are 0.00633 [[art:59948e6d:csi.bill_trend_6m]] and 0.002369 [[art:48df6cc9:csi.bill_mean_6m]] for the billing characteristics, 0.004042 [[art:10f0f9e7:csi.utilisation]] for utilisation, 0.002449 [[art:69346f52:csi.delinq_count_6m]] and 0.0008965 [[art:7244960d:csi.delinq_max_6m]] for the other delinquency characteristics, 0.001924 [[art:aff2b4bf:csi.pay_ratio_last]] and 0.001768 [[art:f567818e:csi.pay_ratio_mean_6m]] for the payment-ratio characteristics, 0.001211 [[art:5b77b34b:csi.limit_bal]] for the credit limit, and 0.0009476 [[art:a78e58f6:csi.age]] for age.
The two views rank the characteristics differently: the most recent delinquency characteristic leads on its contribution to the predictor shift while its marginal distribution moves less than the credit limit's, so neither ordering should be read as the other.

### Leakage screens

No feature is declared as observed during the performance period or after the outcome, that count standing at 0 [[art:742bcd24:leakage.timing.n_flagged]].
No feature name matches the target-adjacent lexicon, that count standing at 0 [[art:407e62be:leakage.name_screen.n_matched]].
The strongest single feature reaches an AUC of 0.6831 [[art:fd829fc4:leakage.target_corr.max_single_feature_auc]], below the bound of 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]] that one feature may reach on its own.

The contamination screen has two arms, and each is read against its own bound.
The identity arm, the share of test rows whose subject identifier also identifies a training row, reads 0 [[art:63d37fc5:leakage.overlap.ids]] against the declared contamination bound of 0.005 [[art:9f336eaf:threshold.L2.overlap]].
The feature-vector arm, the share of test rows whose feature values also appear in train, reads 0 [[art:0fec8048:leakage.overlap.features]] against the bound that arm actually applied, 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].
That applied bound is the larger of the declared contamination bound and an allowance driven by the share of training rows whose feature values are not unique within train, on the reasoning that two different subjects writing the same discrete row is coincidence rather than contamination.
That duplicate share is 0 [[art:4474c227:leakage.duplicates.train]], so the allowance adds nothing and the applied bound rests at the declared level.
The overall share of test rows whose feature values also appear in train is 0 [[art:4c9fcd09:leakage.overlap]], likewise below the bound the feature-vector arm applied at 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].

Every reading reported above sits on the permitted side of the bound it was compared against, and this section carries nothing forward for the findings section.

## 4. Outcomes analysis

Outcomes analysis here compares the model's outputs with the corresponding realised outcomes on the held-out split, which the guidance describes as the means of assessing performance relative to model objectives and business use [[reg:SR26-2:V.1.b]].
This section reports discrimination first and calibration second.
The reason is the observed event rate on the evaluation split, 0.2247 [[art:9209d200:metrics.test.event_rate]], which sits at or above 0.05 [[art:42f1351e:rule.calibration_first_event_rate]], the rate below which this report would lead with calibration instead.

### Metrics by split

| Metric | Train | Test |
| --- | --- | --- |
| Rows | 3500 [[art:564683ee:metrics.train.n]] | 1500 [[art:64fcf14d:metrics.test.n]] |
| Event rate | 0.2246 [[art:133a5ff8:metrics.train.event_rate]] | 0.2247 [[art:9209d200:metrics.test.event_rate]] |
| AUC | 0.7584 [[art:14b38a2b:metrics.train.auc]] | 0.748 [[art:5c6c2bfc:metrics.test.auc]] |
| Gini | 0.5169 [[art:b4da846e:metrics.train.gini]] | 0.496 [[art:8e5918d8:metrics.test.gini]] |
| KS | 0.4451 [[art:ccc12729:metrics.train.ks]] | 0.4183 [[art:90751047:metrics.test.ks]] |
| Brier | 0.1489 [[art:be669a99:metrics.train.brier]] | 0.1489 [[art:bbe69430:metrics.test.brier]] |
| Log loss | 0.465 [[art:4f02e465:metrics.train.logloss]] | 0.4673 [[art:dda8da69:metrics.test.logloss]] |
| Mean predicted | 0.2246 [[art:605cce58:metrics.train.mean_predicted]] | 0.2211 [[art:4d2f8a37:metrics.test.mean_predicted]] |

Rank-ordering carries through to the tails: the top two deciles of predicted probability hold 0.4718 [[art:d4a1cf7d:deciles.test.top2_capture]] of test events, against 0.4517 [[art:1d20c762:deciles.train.top2_capture]] of train events, and the decile detail is below.

<!-- quaestor:renderer:begin table deciles.test -->
Decile separation on test; decile 1 holds the highest probabilities [[art:15d50c28:deciles.test]]:

| decile | count | events | event_rate | lift |
|---|---|---|---|---|
| 1 | 150 | 87 | 0.58 | 2.582 |
| 2 | 150 | 72 | 0.48 | 2.136 |
| 3 | 150 | 47 | 0.3133 | 1.395 |
| 4 | 150 | 35 | 0.2333 | 1.039 |
| 5 | 150 | 24 | 0.16 | 0.7122 |
| 6 | 150 | 15 | 0.1 | 0.4451 |
| 7 | 150 | 16 | 0.1067 | 0.4748 |
| 8 | 150 | 11 | 0.07333 | 0.3264 |
| 9 | 150 | 11 | 0.07333 | 0.3264 |
| 10 | 150 | 19 | 0.1267 | 0.5638 |
<!-- quaestor:renderer:end -->

### Train-to-test gap

AUC on train, 0.7584 [[art:14b38a2b:metrics.train.auc]], sits above AUC on test, 0.748 [[art:5c6c2bfc:metrics.test.auc]], so the split-to-split movement is in the expected direction for a held-out sample.
The bound against which that train-to-test AUC gap is judged is 0.08 [[art:630f28f4:threshold.O1.auc_gap]], and the two AUCs above are the quantities it is applied to.
The largest train-to-test population stability index across the inputs and the score is 0.01095 [[art:381b2570:psi.max]], to be read against the stability bound of 0.25 [[art:278b9016:threshold.S1.psi]], so the two splits are drawn from populations that moved little between them.

### Calibration

The logistic regression of the outcome on the logit of the predicted probability gives a slope on test of 1.003 [[art:b7dbb687:calibration_slope.test]], inside the declared band running from 0.8 [[art:749634ae:threshold.C1.calibration_slope.min]] to 1.2 [[art:b6672579:threshold.C1.calibration_slope.max]].
The intercept of that same regression on test is 0.02729 [[art:b69c6b52:calibration_intercept.test]], and on train the slope is 1.002 [[art:d02e3091:calibration_slope.train]] with an intercept of 0.002062 [[art:ed381a81:calibration_intercept.train]].
Mean predicted probability on test, 0.2211 [[art:4d2f8a37:metrics.test.mean_predicted]], sits just below the observed event rate of 0.2247 [[art:9209d200:metrics.test.event_rate]], so the model under-states the average level of risk on the evaluation split rather than over-stating it.
Expressed relatively, that discrepancy is 0.01585 [[art:d8ffb3d0:calibration.mean_rel_gap.test]], well within the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
Comparing the same relative discrepancy across the two splits, the test figure of 0.01585 [[art:d8ffb3d0:calibration.mean_rel_gap.test]] is the larger of the two, the train figure being 0.0002283 [[art:53738d45:calibration.mean_rel_gap.train]], which is what an in-sample fit against a held-out sample would lead a reviewer to expect.
The decile-by-decile picture on test is below.

<!-- quaestor:renderer:begin table calibration.test -->
Calibration by decile of predicted probability on test [[art:508ffcf8:calibration.test]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.08255 | 0.1267 | 150 |
| 2 | 0.1076 | 0.07333 | 150 |
| 3 | 0.1227 | 0.07333 | 150 |
| 4 | 0.1364 | 0.1067 | 150 |
| 5 | 0.1543 | 0.1 | 150 |
| 6 | 0.1732 | 0.16 | 150 |
| 7 | 0.1972 | 0.2333 | 150 |
| 8 | 0.248 | 0.3133 | 150 |
| 9 | 0.3812 | 0.48 | 150 |
| 10 | 0.608 | 0.58 | 150 |
<!-- quaestor:renderer:end -->

### Developer-declared thresholds

<!-- quaestor:renderer:begin table thresholds.evaluation -->
Every threshold package.yaml declares, with its bound, the recomputed value and the outcome [[art:bc507a88:thresholds.evaluation]]:

| metric | split | bound | value | result |
|---|---|---|---|---|
| auc | test | minimum 0.7 | 0.748 | pass |
| brier | test | maximum 0.2 | 0.1489 | pass |
| calibration_slope | test | minimum 0.8 | 1.003 | pass |
| calibration_slope | test | maximum 1.2 | 1.003 | pass |
| psi |  | maximum 0.25 | 0.01095 | pass |
<!-- quaestor:renderer:end -->

The table sets each bound the package declares beside the value recomputed in this validation and the outcome of that comparison, one row per declared bound.
Its rows, not the narrative above, are the record of where the model stands against the developer's own limits.

### Follow-up analyses

The bounded planning loop ran four further metric computations, each restricted to a sub-population of the test split, to see whether performance is uniform across the portfolio or concentrated.

**`utilisation > median(utilisation)`** — metrics were recomputed on the high-utilisation half of test, asked in order to locate where the champion's discrimination shortfall against the challenger concentrates.

<!-- quaestor:renderer:begin table metrics.test.sub.utilisation_high -->
Every metric on the utilisation above_median slice of test [[art:ab9ef6ac:metrics.test.sub.utilisation_high]]:

| metric | value |
|---|---|
| n | 750 |
| event_rate | 0.2333 |
| auc | 0.5689 |
| gini | 0.1378 |
| ks | 0.156 |
| brier | 0.1945 |
| logloss | 0.5856 |
| mean_predicted | 0.2286 |
| mean_rel_gap | 0.02024 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

AUC on this slice, 0.5689 [[art:13b21546:metrics.test.sub.utilisation_high.auc]], falls 0.1791 [[art:e0dc4aa9:metrics.test.sub.utilisation_high.auc_gap]] below AUC on all of test, above the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] at which a sub-population result is carried forward as an open item.
The slice holds 0.5 [[art:9404484e:metrics.test.sub.utilisation_high.share]] of the split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] a sub-population must hold to be read this way and below the ceiling of 0.95 [[art:a928a05c:threshold.O1.slice_max_share]] at which it would be refused as the whole split.
Mean predicted probability here, 0.2286 [[art:2d88d7b5:metrics.test.sub.utilisation_high.mean_predicted]], sits close to the observed rate of 0.2333 [[art:8e66209c:metrics.test.sub.utilisation_high.event_rate]], a relative discrepancy of 0.02024 [[art:e33a14d6:metrics.test.sub.utilisation_high.mean_rel_gap]], so the weakness on this slice is in the ordering of the probabilities and not in their average level.

**`utilisation <= median(utilisation)`** — the complementary half was computed so that the high-utilisation result could be read against its complement rather than only against the full split.

<!-- quaestor:renderer:begin table metrics.test.sub.utilisation_low -->
Every metric on the utilisation below_median slice of test [[art:8e1db133:metrics.test.sub.utilisation_low]]:

| metric | value |
|---|---|
| n | 750 |
| event_rate | 0.216 |
| auc | 0.8986 |
| gini | 0.7972 |
| ks | 0.7659 |
| brier | 0.1032 |
| logloss | 0.349 |
| mean_predicted | 0.2136 |
| mean_rel_gap | 0.01111 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

AUC on this slice, 0.8986 [[art:f85acc05:metrics.test.sub.utilisation_low.auc]], stands above AUC on all of test, its recorded shortfall being -0.1506 [[art:f391975a:metrics.test.sub.utilisation_low.auc_gap]], and so within the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].
The slice holds 0.5 [[art:7860a748:metrics.test.sub.utilisation_low.share]] of the split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].
Mean predicted probability, 0.2136 [[art:705aaaaa:metrics.test.sub.utilisation_low.mean_predicted]], sits just below the observed rate of 0.216 [[art:b0ad49be:metrics.test.sub.utilisation_low.event_rate]], a relative discrepancy of 0.01111 [[art:5c974ecf:metrics.test.sub.utilisation_low.mean_rel_gap]], so neither the level nor the ordering of the probabilities is in question on this half.

**`delinq_count_6m > median(delinq_count_6m)`** — metrics were recomputed on the higher-delinquency half of test, asked because a linear champion would be expected to miss nonlinearity there if the shortfall behind the challenger concentrated in that region.

<!-- quaestor:renderer:begin table metrics.test.sub.delinq_count_6m_high -->
Every metric on the delinq_count_6m above_median slice of test [[art:2a7e6e1d:metrics.test.sub.delinq_count_6m_high]]:

| metric | value |
|---|---|
| n | 550 |
| event_rate | 0.3455 |
| auc | 0.75 |
| gini | 0.4999 |
| ks | 0.4298 |
| brier | 0.1932 |
| logloss | 0.5683 |
| mean_predicted | 0.3198 |
| mean_rel_gap | 0.07415 |
| share | 0.3667 |
<!-- quaestor:renderer:end -->

AUC on this slice, 0.75 [[art:cce9cb57:metrics.test.sub.delinq_count_6m_high.auc]], stands marginally above AUC on all of test, its recorded shortfall being -0.001967 [[art:e1299157:metrics.test.sub.delinq_count_6m_high.auc_gap]], and so within the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].
The slice holds 0.3667 [[art:22847310:metrics.test.sub.delinq_count_6m_high.share]] of the split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].
Mean predicted probability here, 0.3198 [[art:56c1526c:metrics.test.sub.delinq_count_6m_high.mean_predicted]], sits below the observed rate of 0.3455 [[art:ef17c303:metrics.test.sub.delinq_count_6m_high.event_rate]], a relative discrepancy of 0.07415 [[art:a9cbcc36:metrics.test.sub.delinq_count_6m_high.mean_rel_gap]], so what the slice shows is under-statement of the level of risk while the ordering holds up as well as it does on the split as a whole.

**`delinq_count_6m <= median(delinq_count_6m)`** — the complementary half completes the delinquency partition, so that the above-median result is read against its complement and not only against the headline.

<!-- quaestor:renderer:begin table metrics.test.sub.delinq_count_6m_low -->
Every metric on the delinq_count_6m below_median slice of test [[art:ee4d42af:metrics.test.sub.delinq_count_6m_low]]:

| metric | value |
|---|---|
| n | 950 |
| event_rate | 0.1547 |
| auc | 0.6599 |
| gini | 0.3197 |
| ks | 0.287 |
| brier | 0.1232 |
| logloss | 0.4088 |
| mean_predicted | 0.1639 |
| mean_rel_gap | 0.0595 |
| share | 0.6333 |
<!-- quaestor:renderer:end -->

AUC on this slice, 0.6599 [[art:7f51de37:metrics.test.sub.delinq_count_6m_low.auc]], falls 0.08813 [[art:bcc5022d:metrics.test.sub.delinq_count_6m_low.auc_gap]] below AUC on all of test, above the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].
The slice holds 0.6333 [[art:3257b2f3:metrics.test.sub.delinq_count_6m_low.share]] of the split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] and below the ceiling of 0.95 [[art:a928a05c:threshold.O1.slice_max_share]].
Mean predicted probability here, 0.1639 [[art:5f0fb0df:metrics.test.sub.delinq_count_6m_low.mean_predicted]], sits above the observed rate of 0.1547 [[art:9690f94d:metrics.test.sub.delinq_count_6m_low.event_rate]], a relative discrepancy of 0.0595 [[art:016ca7c3:metrics.test.sub.delinq_count_6m_low.mean_rel_gap]], so this slice is over-stated in level as well as weaker in ordering than the split it is drawn from.
Comparing the relative level discrepancies across the two halves of the delinquency partition, and taking that comparison as a difference between the two figures rather than as their ratio, the above-median figure of 0.07415 [[art:a9cbcc36:metrics.test.sub.delinq_count_6m_high.mean_rel_gap]] is the larger of the two and the below-median figure of 0.0595 [[art:016ca7c3:metrics.test.sub.delinq_count_6m_low.mean_rel_gap]] the smaller, and they run in opposite directions against their respective observed rates.

## 5. Sensitivity and scenario analysis

Sensitivity analysis in validation checks how model outputs respond to small changes in inputs and parameter values, and how they behave at extreme values, so that the conditions under which a model is stable can be established and documented [[reg:SR11-7:V.1.a]].
This section reports the multicollinearity diagnostics computed on the retained design and states plainly which of the exercises in its scope do not apply to a model of this type.

The largest variance inflation factor across the retained features is 7.295 [[art:9ae7c45b:vif.max]], below the declared ceiling of 10 [[art:aeb4f33c:threshold.M1.vif]].
That maximum is attained by `bill_mean_6m`, at 7.295 [[art:f0a2f865:vif.bill_mean_6m]], with `pay_ratio_last` at 7.264 [[art:c2de8dfe:vif.pay_ratio_last]] and `pay_ratio_mean_6m` at 7.259 [[art:e39c3e82:vif.pay_ratio_mean_6m]] sitting just below it.
The remaining retained features fall further from the ceiling: `limit_bal` at 4.803 [[art:ddfdcc3c:vif.limit_bal]], `utilisation` at 3.215 [[art:536fdb6f:vif.utilisation]], `delinq_count_6m` at 2.561 [[art:38974def:vif.delinq_count_6m]], `delinq_max_6m` at 2.408 [[art:71aaaf11:vif.delinq_max_6m]], `delinq_last` at 1.412 [[art:48733638:vif.delinq_last]], `bill_trend_6m` at 1.201 [[art:9356a256:vif.bill_trend_6m]] and `age` at 1.002 [[art:74c06cad:vif.age]].
No retained feature reaches the declared ceiling, and the values cluster into a group of billing and payment-ratio terms that share structure and a group of delinquency, utilisation and demographic terms that are close to independent of the rest of the design.

The condition number of the column-standardised design is 5.547 [[art:e41b9562:condition_number]], below the declared limit of 30 [[art:7e52fd7a:threshold.M1.condition_number]].
The multicollinearity diagnostics point the same way: the correlation visible among the billing and payment-ratio features raises their variance inflation factors relative to the rest of the design without bringing the design as a whole near either declared limit.
On the evidence reported here, coefficient variances on the retained features are not inflated to the point where the declared limits would call the specification into question, though the closeness of the three highest variance inflation factors means that substituting or re-scaling any one of those features can be expected to move the others.

Stability across declared regimes and the rate-shock scenario suite do not apply to a model of this type and were not run for this package.
The rate-shock exercise — the change in value at the extreme shocks, whether the shock curve is monotone, and the convexity of that curve against the direction the package declares — is defined for hazard models, and the subject of this validation is not one, so no statement in this section should be read as reporting a shocked value, a monotonicity check or a convexity direction.
No regime column is declared for this model either, so the cross-regime stability comparison has no partition to run over and no regime-to-regime difference or ratio is asserted here.
These exercises are recorded in Appendix D as out of scope for this model type rather than as exercises that were attempted.

## 6. Findings and recommendations

Findings are ordered by severity, and each carries the recomputed values and declared thresholds it rests on, in keeping with validation that identifies model limitations and clarifies whether corrective actions may be warranted [[reg:SR26-2:V]].

### F-001 · E1 effective challenge · severity **low**

**The champion carried in this package is outperformed on the test split by a gradient-boosting challenger by a margin wider than the package's own effective-challenge bound.**

The challenger reaches an AUC of 0.824 [[art:bf5be719:challenger.auc]] on test, against the champion's recomputed AUC of 0.748 [[art:5c6c2bfc:metrics.test.auc]] on the same split.

Taken as a difference, the challenger's lead is 0.07598 [[art:c9e502ae:challenger.delta_auc]], which sits above the effective-challenge bound of 0.03 [[art:e042774c:threshold.E1.delta_auc]].

The validator concludes that an alternative specification discriminates better on the test split than the specification put forward, and that the package does not carry a recorded reason for preferring the weaker one; the severity stays low because the challenger is a benchmark fitted for comparison rather than a submitted production candidate, and the result speaks to the adequacy of the challenge rather than to an error inside the champion.

The model developer should record an explicit rationale for retaining the champion in the face of this lead, covering interpretability, stability and implementation constraints where those drive the choice, or else bring the stronger specification forward for validation in its own right.

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1, S1), `compute_metrics` (T1, C1, O1), `check_leakage` (L1, L2), `check_collinearity` (M1).

### Open items

Model developer: within `delinq_count_6m <= median(delinq_count_6m)`, where the model's AUC is 0.6599 [[art:7f51de37:metrics.test.sub.delinq_count_6m_low.auc]] and falls, as a difference, 0.08813 [[art:bcc5022d:metrics.test.sub.delinq_count_6m_low.auc_gap]] below the test split's own AUC of 0.748 [[art:5c6c2bfc:metrics.test.auc]], past the open-item bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] on a share of 0.6333 [[art:3257b2f3:metrics.test.sub.delinq_count_6m_low.share]] that is at or above the minimum share of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]], what does the model still discriminate on once delinquency history is held near-constant by the selection itself?

Model developer: within `utilisation > median(utilisation)`, where the model's AUC is 0.5689 [[art:13b21546:metrics.test.sub.utilisation_high.auc]] and falls, as a difference, 0.1791 [[art:e0dc4aa9:metrics.test.sub.utilisation_high.auc_gap]] below the test split's own AUC of 0.748 [[art:5c6c2bfc:metrics.test.auc]], past the open-item bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] on a share of 0.5 [[art:9404484e:metrics.test.sub.utilisation_high.share]] that is at or above the minimum share of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]], which features are expected to separate defaulters among high-utilisation borrowers once utilisation and everything correlated with it are conditioned on?

Model developer: what drives the fitted coefficient on `delinq_max_6m` to carry sign -1 [[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]] when that feature's own univariate direction on train is 1 [[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]], the disagreement being flagged at 0 [[art:c946359c:sign_check.delinq_max_6m.agrees]] when read against that univariate direction, and which correlated features absorb the direction the feature shows on its own?

Model developer: what drives the fitted coefficient on `limit_bal` to carry sign 1 [[art:6af6aef2:sign_check.limit_bal.coef_sign]] when that feature's own univariate direction on train is -1 [[art:56d284d6:sign_check.limit_bal.univariate_direction]], the disagreement being flagged at 0 [[art:0278aad1:sign_check.limit_bal.agrees]] when read against that univariate direction, and is the reversal an intended conditional effect given the other credit-exposure features in the specification?

Model developer: what drives the fitted coefficient on `pay_ratio_last` to carry sign 1 [[art:f018263e:sign_check.pay_ratio_last.coef_sign]] when that feature's own univariate direction on train is -1 [[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]], the disagreement being flagged at 0 [[art:79abee77:sign_check.pay_ratio_last.agrees]] when read against that univariate direction, and how is that conditional direction explained to users of the model output?

## 7. Ongoing monitoring recommendations

Ongoing monitoring evaluates whether a model continues to perform as expected given potential changes in products, exposures, activities, clients, data relevance, or market conditions, and the recommendations below are framed on that basis [[reg:SR26-2:V.2]].

### Quantities to track and the bounds to track them against

Monitoring should recompute, on each production vintage, the same four quantities this validation checked, and should judge each against the bound the package declares rather than against any new number introduced by the monitoring process.

Rank-ordering ability should be recomputed and compared with the declared floor of 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]], with the evaluation-split value of 0.748 [[art:5c6c2bfc:metrics.test.auc]] serving as the reference point against which drift in production is read.

The mean squared error of the predicted probabilities should be compared with the declared ceiling of 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]], against a reference value of 0.1489 [[art:bbe69430:metrics.test.brier]] on the evaluation split.

The slope of the logistic regression of the outcome on the logit of the predicted probability should be kept inside the declared band running from 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] to 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]], against a reference value of 1.003 [[art:b7dbb687:calibration_slope.test]], which sits near the middle of that band and closer to its upper edge than to its lower one.

Population stability across the scored features and the score itself should be compared with the declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]]; the largest shift measured here was 0.01095 [[art:381b2570:psi.max]], far below that ceiling, so a production reading that approaches the ceiling would represent a change of character relative to what this validation observed and not merely a change of degree.

Because the stability reading available here is a train-to-test comparison within the development data, monitoring should recompute the same statistic as a development-to-production comparison and as a vintage-to-vintage comparison, reporting both the shift between the two populations and the direction of that shift rather than a single summary of the two.

### Frequency

Input-side stability should be recomputed at every batch scoring run, because input drift can be observed before any outcome has matured and is therefore the earliest warning the monitoring program can give.

Rank-ordering ability, the mean squared error of the predicted probabilities, and the calibration slope should be recomputed as each cohort's performance window closes, since outcomes analysis compares model outputs with corresponding realized outcomes and cannot run ahead of those outcomes [[reg:SR26-2:V.1.b]].

A fuller review that revisits the model's development-stage limitations alongside the tracked quantities should run at the periodic cadence the model risk policy assigns to a model of this materiality, since the frequency and scope of monitoring reports depend on the nature of the model, the availability of new data or modeling approaches, and model materiality [[reg:SR26-2:V.2]].

When a tracked quantity crosses its declared bound, or drifts persistently toward it across consecutive vintages without crossing, the monitoring report should treat that as grounds to consider overlays, adjustment, recalibration, or redevelopment rather than waiting for the next scheduled review [[reg:SR26-2:V.2]].

### Ordering of the monitoring report

Section 4 of this report presented discrimination before calibration for the evaluation split examined here.

If a future production cohort has an observed event rate below 0.05 [[art:42f1351e:rule.calibration_first_event_rate]], the monitoring report for that cohort should lead with calibration instead, because at low event rates the absolute accuracy of the predicted probabilities is the more fragile property and the one that governs the downstream use of the score.

### Benchmarking

Section 2 of this report compares the champion with a challenger, and monitoring should extend rather than repeat that comparison.

What monitoring can add, and what the development data cannot supply, is a benchmark against an external or vendor reference score — a bureau score or a vendor credit risk model run on the same production population — so that the champion's rank-ordering and its predicted probabilities are compared with an alternative prediction built from data this model does not see [[reg:SR11-7:V.1.b]].

Discrepancies against such a reference should trigger investigation into the sources and degree of the differences rather than an automatic conclusion that either model is in error, since the benchmark is itself an alternative prediction resting on different data and methods [[reg:SR11-7:V.1.b]].

If the reference is a vendor product, the monitoring program should also assess the relevance of the vendor's development population to the institution's own book and should conduct outcomes analysis of the vendor score using the institution's realized outcomes [[reg:SR11-7:V.2]].

### What this validation could not cover and monitoring should watch instead

This validation examined the packaged model on the data splits supplied with it, so the behavior of the deployed implementation — the integrity, completeness, and timeliness of the production data feeds, the equivalence of production scoring code to the packaged artifact, and change control over that code — is outside what the evidence here can speak to and belongs to process verification within monitoring.

No production vintage and no macroeconomic regime other than the one embedded in the development data were observed, so monitoring must be the mechanism that detects deterioration arising from changed exposures, changed origination mix, or changed market conditions.

Overrides of the score by users were not observable in this package, and their rate, their documented reasons, and the realized performance of overridden cases should be tracked, since a high override rate or overrides that consistently improve on the model point toward revision or redevelopment.

The stability of performance across sub-populations over time cannot be established from a single evaluation split, so monitoring should report the tracked quantities by the segments that matter for the model's business use and should state, for each comparison between two segments, whether it is reporting the difference or the ratio between them.

Even with sound development and rigorous validation, material model risk can remain, and users of the output benefit from understanding and communicating these limitations, monitoring performance, periodically reviewing relevance, and supplementing model output with complementary analysis [[reg:SR26-2:V]].

## Appendix A — Claims

Grounding precision 0.9924 before repair (262 of 264 claims verified; 2 mismatch) and 1.0000 after 0 claim(s) rewritten and 2 number(s) removed from the prose. Per section (post-repair): summary 20/20; conceptual_soundness 79/79; data_integrity 43/43; outcomes 73/73; sensitivity 14/14; findings 25/25; monitoring 10/10.

Developer claims: The package declares 2 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). See Appendix D.

Excluded numeric tokens (not claims): section_number (Section 4, Section 2); citation_hash (2ad8d1a5, 2510d49d, 2193cf5f, 5c6c2bfc); regulatory_section_id (SR26-2:V, SR26-2:V.1.b, SR26-2:V.1.a, SR26-2:IV.1); finding_id (F-001); extractor_returned_excluded_token (6.0, 1.0, 4, 2).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The subject was run under the wall-clock cap of 300 seconds… | 300 | ratio | runtime.max_seconds |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 2 | summary | The training split holds 3500 rows and the test split holds… | 3500 | count | n | train | eq | `[[art:2510d49d:profile.train.n]]` | verified | 3500 |
| 3 | summary | The training split holds 3500 rows and the test split holds… | 1500 | count | n | test | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 4 | summary | The model passes the developer-declared discrimination floor… | 0.748 | ratio | auc | test | eq | `[[art:5c6c2bfc:metrics.test.auc]]` | verified | 0.7479888042 |
| 5 | summary | The model passes the developer-declared discrimination floor… | 0.7 | ratio | auc | test | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 6 | summary | It passes the declared accuracy ceiling, with a Brier score… | 0.1489 | ratio | brier | test | eq | `[[art:bbe69430:metrics.test.brier]]` | verified | 0.148850901 |
| 7 | summary | It passes the declared accuracy ceiling, with a Brier score… | 0.2 | ratio | brier | test | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 8 | summary | It passes the declared calibration band, with a calibration… | 1.003 | ratio | calibration_slope | test | eq | `[[art:b7dbb687:calibration_slope.test]]` | verified | 1.002737656 |
| 9 | summary | It passes the declared calibration band, with a calibration… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 10 | summary | It passes the declared calibration band, with a calibration… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 11 | summary | It passes the declared stability ceiling, with a largest tra… | 0.01095 | ratio | psi |  | eq | `[[art:381b2570:psi.max]]` | verified | 0.01095273358 |
| 12 | summary | It passes the declared stability ceiling, with a largest tra… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 13 | summary | Discrimination on train, at 0.7584 , stands above discrimina… | 0.7584 | ratio | auc | train | eq | `[[art:14b38a2b:metrics.train.auc]]` | verified | 0.7584356677 |
| 14 | summary | Discrimination on train, at 0.7584 , stands above discrimina… | 0.748 | ratio | auc | test | eq | `[[art:5c6c2bfc:metrics.test.auc]]` | verified | 0.7479888042 |
| 15 | summary | In aggregate the mean predicted probability on test, at 0.22… | 0.2211 | ratio | mean_predicted | test | eq | `[[art:4d2f8a37:metrics.test.mean_predicted]]` | verified | 0.2211048954 |
| 16 | summary | In aggregate the mean predicted probability on test, at 0.22… | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 17 | summary | Discrimination is not uniform across the utilisation sub-pop… | 0.8986 | ratio | auc | test | eq | `[[art:f85acc05:metrics.test.sub.utilisation_low.auc]]` | verified | 0.8985890653 |
| 18 | summary | Discrimination is not uniform across the utilisation sub-pop… | 0.5689 | ratio | auc | test | eq | `[[art:13b21546:metrics.test.sub.utilisation_high.auc]]` | verified | 0.5688944099 |
| 19 | summary | Discrimination is not uniform across the utilisation sub-pop… | -0.1506 | ratio | auc_gap | test | eq | `[[art:f391975a:metrics.test.sub.utilisation_low.auc_gap]]` | verified | -0.1506002611 |
| 20 | summary | Discrimination is not uniform across the utilisation sub-pop… | 0.1791 | ratio | auc_gap | test | eq | `[[art:e0dc4aa9:metrics.test.sub.utilisation_high.auc_gap]]` | verified | 0.1790943942 |
| 21 | conceptual_soundness | The champion is a logistic regression with an intercept of -… | -1.396 | ratio | intercept |  | eq | `[[art:74c10f15:run.model_summary#intercept]]` | verified | -1.395828048 |
| 22 | conceptual_soundness | The champion is a logistic regression with an intercept of -… | 3500 | count | n_train | train | eq | `[[art:74c10f15:run.model_summary#n_train]]` | verified | 3500 |
| 23 | conceptual_soundness | The champion is a logistic regression with an intercept of -… | 0.748 | ratio | auc | test | eq | `[[art:5c6c2bfc:metrics.test.auc]]` | verified | 0.7479888042 |
| 24 | conceptual_soundness | The champion is a logistic regression with an intercept of -… | 0.1489 | ratio | brier | test | eq | `[[art:bbe69430:metrics.test.brier]]` | verified | 0.148850901 |
| 25 | conceptual_soundness | The subject's feature inventory carries 12 features in total… | 12 | count | n |  | eq | `[[art:abbb748e:run.features#n]]` | verified | 12 |
| 26 | conceptual_soundness | Of these, 2 are known at origination and 10 are known before… | 2 | count | at_origination |  | eq | `[[art:abbb748e:run.features#at_origination]]` | verified | 2 |
| 27 | conceptual_soundness | Of these, 2 are known at origination and 10 are known before… | 10 | count | before_period_start |  | eq | `[[art:abbb748e:run.features#before_period_start]]` | verified | 10 |
| 28 | conceptual_soundness | The inventory records 0 features observed during the perform… | 0 | count | during_period |  | eq | `[[art:abbb748e:run.features#during_period]]` | verified | 0 |
| 29 | conceptual_soundness | The inventory records 0 features observed during the perform… | 0 | count | after_outcome |  | eq | `[[art:abbb748e:run.features#after_outcome]]` | verified | 0 |
| 30 | conceptual_soundness | The developer applied a variance-inflation screen at a thres… | 10 | ratio | vif_threshold |  | eq | `[[art:74c10f15:run.model_summary#vif_threshold]]` | verified | 10 |
| 31 | conceptual_soundness | The last bill amount was removed at a variance inflation of… | 160.9 | ratio | vif |  | eq | `[[art:74c10f15:run.model_summary#removed.bill_last.vif]]` | verified | 160.888514 |
| 32 | conceptual_soundness | The last bill amount was removed at a variance inflation of… | 36.36 | ratio | vif |  | eq | `[[art:74c10f15:run.model_summary#removed.utilisation_mean_6m.vif]]` | verified | 36.356335 |
| 33 | conceptual_soundness | The largest coefficient in magnitude is on the most recent d… | 0.7334 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.delinq_last.value]]` | verified | 0.7334219534 |
| 34 | conceptual_soundness | Next in magnitude are the six-month mean bill amount at -0.3… | -0.3726 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.bill_mean_6m.value]]` | verified | -0.3726281079 |
| 35 | conceptual_soundness | Next in magnitude are the six-month mean bill amount at -0.3… | -0.3554 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.pay_ratio_mean_6m.value]]` | verified | -0.3553721566 |
| 36 | conceptual_soundness | Next in magnitude are the six-month mean bill amount at -0.3… | 0.2662 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.utilisation.value]]` | verified | 0.2662083574 |
| 37 | conceptual_soundness | Next in magnitude are the six-month mean bill amount at -0.3… | -0.2225 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.bill_trend_6m.value]]` | verified | -0.2224749257 |
| 38 | conceptual_soundness | The remaining weights are smaller: the credit limit at 0.072… | 0.07266 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.limit_bal.value]]` | verified | 0.07265585996 |
| 39 | conceptual_soundness | The remaining weights are smaller: the credit limit at 0.072… | -0.06726 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.age.value]]` | verified | -0.06725800744 |
| 40 | conceptual_soundness | The remaining weights are smaller: the credit limit at 0.072… | 0.1226 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.delinq_count_6m.value]]` | verified | 0.1225797828 |
| 41 | conceptual_soundness | The remaining weights are smaller: the credit limit at 0.072… | 0.1026 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.pay_ratio_last.value]]` | verified | 0.1025909773 |
| 42 | conceptual_soundness | The remaining weights are smaller: the credit limit at 0.072… | -0.03221 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.delinq_max_6m.value]]` | verified | -0.03221440242 |
| 43 | conceptual_soundness | The sign comparison records 3 retained features whose fitted… | 3 | count | n_disagreements |  | eq | `[[art:e223cd4a:sign_check.n_disagreements]]` | verified | 3 |
| 44 | conceptual_soundness | The credit limit is fitted positive, at a coefficient sign o… | 1 | ratio | coef_sign |  | eq | `[[art:6af6aef2:sign_check.limit_bal.coef_sign]]` | verified | 1 |
| 45 | conceptual_soundness | The credit limit is fitted positive, at a coefficient sign o… | -1 | ratio | univariate_direction |  | eq | `[[art:56d284d6:sign_check.limit_bal.univariate_direction]]` | verified | -1 |
| 46 | conceptual_soundness | The credit limit is fitted positive, at a coefficient sign o… | 0 | ratio | agrees |  | eq | `[[art:0278aad1:sign_check.limit_bal.agrees]]` | verified | 0 |
| 47 | conceptual_soundness | Refitting the champion's form without the credit limit chang… | 0.0004286 | ratio | delta_auc | test | eq | `[[art:63faa640:ablation.limit_bal.delta_auc]]` | verified | 0.0004286468792 |
| 48 | conceptual_soundness | Refitting the champion's form without the credit limit chang… | 0.748 | ratio | baseline_auc | test | eq | `[[art:3a44e438:ablation.baseline_auc]]` | verified | 0.7479888042 |
| 49 | conceptual_soundness | The most recent payment ratio is likewise fitted positive, a… | 1 | ratio | coef_sign |  | eq | `[[art:f018263e:sign_check.pay_ratio_last.coef_sign]]` | verified | 1 |
| 50 | conceptual_soundness | The most recent payment ratio is likewise fitted positive, a… | -1 | ratio | univariate_direction |  | eq | `[[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]]` | verified | -1 |
| 51 | conceptual_soundness | The most recent payment ratio is likewise fitted positive, a… | 0 | ratio | agrees |  | eq | `[[art:79abee77:sign_check.pay_ratio_last.agrees]]` | verified | 0 |
| 52 | conceptual_soundness | This is the harder one to defend in subject-matter terms, si… | -0.3554 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.pay_ratio_mean_6m.value]]` | verified | -0.3553721566 |
| 53 | conceptual_soundness | Dropping the most recent payment ratio and refitting changes… | 0.002411 | ratio | delta_auc | test | eq | `[[art:5f39089e:ablation.pay_ratio_last.delta_auc]]` | verified | 0.002411138695 |
| 54 | conceptual_soundness | Dropping the most recent payment ratio and refitting changes… | 0.748 | ratio | baseline_auc | test | eq | `[[art:3a44e438:ablation.baseline_auc]]` | verified | 0.7479888042 |
| 55 | conceptual_soundness | The six-month maximum delinquency is fitted negative, at -1… | -1 | ratio | coef_sign |  | eq | `[[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]]` | verified | -1 |
| 56 | conceptual_soundness | The six-month maximum delinquency is fitted negative, at -1… | 1 | ratio | univariate_direction |  | eq | `[[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]]` | verified | 1 |
| 57 | conceptual_soundness | The six-month maximum delinquency is fitted negative, at -1… | 0 | ratio | agrees |  | eq | `[[art:c946359c:sign_check.delinq_max_6m.agrees]]` | verified | 0 |
| 58 | conceptual_soundness | A negative weight on the worst delinquency seen in six month… | 0.7334 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.delinq_last.value]]` | verified | 0.7334219534 |
| 59 | conceptual_soundness | Removing it changes test AUC by 0.0003598 , an increase, so… | 0.0003598 | ratio | delta_auc | test | eq | `[[art:3a0d3a0c:ablation.delinq_max_6m.delta_auc]]` | verified | 0.0003597572022 |
| 60 | conceptual_soundness | The other seven retained features agree with their own direc… | -1 | ratio | coef_sign |  | eq | `[[art:6172eb93:sign_check.age.coef_sign]]` | verified | -1 |
| 61 | conceptual_soundness | The other seven retained features agree with their own direc… | -1 | ratio | univariate_direction |  | eq | `[[art:66364583:sign_check.age.univariate_direction]]` | verified | -1 |
| 62 | conceptual_soundness | The other seven retained features agree with their own direc… | 1 | ratio | agrees |  | eq | `[[art:4116add1:sign_check.age.agrees]]` | verified | 1 |
| 63 | conceptual_soundness | The other seven retained features agree with their own direc… | 1 | ratio | coef_sign |  | eq | `[[art:85badc3c:sign_check.utilisation.coef_sign]]` | verified | 1 |
| 64 | conceptual_soundness | The other seven retained features agree with their own direc… | 1 | ratio | univariate_direction |  | eq | `[[art:f0995196:sign_check.utilisation.univariate_direction]]` | verified | 1 |
| 65 | conceptual_soundness | The other seven retained features agree with their own direc… | 1 | ratio | agrees |  | eq | `[[art:d0c9a130:sign_check.utilisation.agrees]]` | verified | 1 |
| 66 | conceptual_soundness | The other seven retained features agree with their own direc… | -1 | ratio | coef_sign |  | eq | `[[art:077bb6b2:sign_check.pay_ratio_mean_6m.coef_sign]]` | verified | -1 |
| 67 | conceptual_soundness | The other seven retained features agree with their own direc… | -1 | ratio | univariate_direction |  | eq | `[[art:24dcef24:sign_check.pay_ratio_mean_6m.univariate_direction]]` | verified | -1 |
| 68 | conceptual_soundness | The other seven retained features agree with their own direc… | 1 | ratio | agrees |  | eq | `[[art:7e9a76ca:sign_check.pay_ratio_mean_6m.agrees]]` | verified | 1 |
| 69 | conceptual_soundness | The other seven retained features agree with their own direc… | 1 | ratio | coef_sign |  | eq | `[[art:50d352f8:sign_check.delinq_last.coef_sign]]` | verified | 1 |
| 70 | conceptual_soundness | The other seven retained features agree with their own direc… | 1 | ratio | univariate_direction |  | eq | `[[art:a78648ba:sign_check.delinq_last.univariate_direction]]` | verified | 1 |
| 71 | conceptual_soundness | The other seven retained features agree with their own direc… | 1 | ratio | agrees |  | eq | `[[art:a8ba9372:sign_check.delinq_last.agrees]]` | verified | 1 |
| 72 | conceptual_soundness | The other seven retained features agree with their own direc… | 1 | ratio | coef_sign |  | eq | `[[art:17afb6f9:sign_check.delinq_count_6m.coef_sign]]` | verified | 1 |
| 73 | conceptual_soundness | The other seven retained features agree with their own direc… | 1 | ratio | univariate_direction |  | eq | `[[art:549e904e:sign_check.delinq_count_6m.univariate_direction]]` | verified | 1 |
| 74 | conceptual_soundness | The other seven retained features agree with their own direc… | 1 | ratio | agrees |  | eq | `[[art:a337d16b:sign_check.delinq_count_6m.agrees]]` | verified | 1 |
| 75 | conceptual_soundness | The other seven retained features agree with their own direc… | -1 | ratio | coef_sign |  | eq | `[[art:cee1a18f:sign_check.bill_mean_6m.coef_sign]]` | verified | -1 |
| 76 | conceptual_soundness | The other seven retained features agree with their own direc… | -1 | ratio | univariate_direction |  | eq | `[[art:23b89c5d:sign_check.bill_mean_6m.univariate_direction]]` | verified | -1 |
| 77 | conceptual_soundness | The other seven retained features agree with their own direc… | 1 | ratio | agrees |  | eq | `[[art:89279c3b:sign_check.bill_mean_6m.agrees]]` | verified | 1 |
| 78 | conceptual_soundness | The other seven retained features agree with their own direc… | -1 | ratio | coef_sign |  | eq | `[[art:7fd8474e:sign_check.bill_trend_6m.coef_sign]]` | verified | -1 |
| 79 | conceptual_soundness | The other seven retained features agree with their own direc… | -1 | ratio | univariate_direction |  | eq | `[[art:a9bff389:sign_check.bill_trend_6m.univariate_direction]]` | verified | -1 |
| 80 | conceptual_soundness | The other seven retained features agree with their own direc… | 1 | ratio | agrees |  | eq | `[[art:ff3cb24a:sign_check.bill_trend_6m.agrees]]` | verified | 1 |
| 81 | conceptual_soundness | The leave-one-out refits, all measured against a baseline te… | 0.748 | ratio | baseline_auc | test | eq | `[[art:3a44e438:ablation.baseline_auc]]` | verified | 0.7479888042 |
| 82 | conceptual_soundness | Dropping the most recent delinquency status changes test AUC… | -0.07585 | ratio | delta_auc | test | eq | `[[art:3150b111:ablation.delinq_last.delta_auc]]` | verified | -0.07585263733 |
| 83 | conceptual_soundness | Dropping the most recent delinquency status changes test AUC… | -0.01977 | ratio | delta_auc | test | eq | `[[art:d4ad2039:ablation.utilisation.delta_auc]]` | verified | -0.01976623436 |
| 84 | conceptual_soundness | The six-month mean bill amount contributes as well, at -0.00… | -0.0016 | ratio | delta_auc | test | eq | `[[art:3b91a889:ablation.bill_mean_6m.delta_auc]]` | verified | -0.001599771388 |
| 85 | conceptual_soundness | Every other retained feature has a non-negative ablation del… | 8.675e-05 | ratio | delta_auc | test | eq | `[[art:59398b1b:ablation.age.delta_auc]]` | verified | 8.674996364e-05 |
| 86 | conceptual_soundness | Every other retained feature has a non-negative ablation del… | 0.0006812 | ratio | delta_auc | test | eq | `[[art:c5659def:ablation.delinq_count_6m.delta_auc]]` | verified | 0.0006812423615 |
| 87 | conceptual_soundness | Every other retained feature has a non-negative ablation del… | 0.0003598 | ratio | delta_auc | test | eq | `[[art:3a0d3a0c:ablation.delinq_max_6m.delta_auc]]` | verified | 0.0003597572022 |
| 88 | conceptual_soundness | Every other retained feature has a non-negative ablation del… | 0.0004286 | ratio | delta_auc | test | eq | `[[art:63faa640:ablation.limit_bal.delta_auc]]` | verified | 0.0004286468792 |
| 89 | conceptual_soundness | Every other retained feature has a non-negative ablation del… | 0.002411 | ratio | delta_auc | test | eq | `[[art:5f39089e:ablation.pay_ratio_last.delta_auc]]` | verified | 0.002411138695 |
| 90 | conceptual_soundness | Every other retained feature has a non-negative ablation del… | 0.006603 | ratio | delta_auc | test | eq | `[[art:90fa1178:ablation.pay_ratio_mean_6m.delta_auc]]` | verified | 0.006603203115 |
| 91 | conceptual_soundness | Every other retained feature has a non-negative ablation del… | 0.003279 | ratio | delta_auc | test | eq | `[[art:096d7f98:ablation.bill_trend_6m.delta_auc]]` | verified | 0.003278638332 |
| 92 | conceptual_soundness | The largest such increase is on the six-month mean payment r… | 0.006603 | ratio | delta_auc | test | eq | `[[art:90fa1178:ablation.pay_ratio_mean_6m.delta_auc]]` | verified | 0.006603203115 |
| 93 | conceptual_soundness | A gradient-boosting challenger was fitted on the same data a… | 0.824 | ratio | auc | test | eq | `[[art:bf5be719:challenger.auc]]` | verified | 0.823969015 |
| 94 | conceptual_soundness | A gradient-boosting challenger was fitted on the same data a… | 0.748 | ratio | auc | test | eq | `[[art:5c6c2bfc:metrics.test.auc]]` | verified | 0.7479888042 |
| 95 | conceptual_soundness | A gradient-boosting challenger was fitted on the same data a… | 0.07598 | ratio | delta_auc | test | eq | `[[art:c9e502ae:challenger.delta_auc]]` | verified | 0.0759802108 |
| 96 | conceptual_soundness | That lead is read against a declared effective-challenge bou… | 0.03 | ratio | delta_auc |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 97 | conceptual_soundness | The challenger is also better calibrated on test, with a Bri… | 0.1258 | ratio | brier | test | eq | `[[art:f9e0583d:challenger.brier]]` | verified | 0.1258050391 |
| 98 | conceptual_soundness | The challenger is also better calibrated on test, with a Bri… | 0.1489 | ratio | brier | test | eq | `[[art:bbe69430:metrics.test.brier]]` | verified | 0.148850901 |
| 99 | conceptual_soundness | Against that, 3 retained features are fitted against their o… | 3 | count | n_disagreements |  | eq | `[[art:e223cd4a:sign_check.n_disagreements]]` | verified | 3 |
| 100 | data_integrity | The training split holds 3500 rows and the test split holds… | 3500 | count | n | train | eq | `[[art:2510d49d:profile.train.n]]` | verified | 3500 |
| 101 | data_integrity | The training split holds 3500 rows and the test split holds… | 1500 | count | n | test | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 102 | data_integrity | The largest missing fraction in the training split is 0 , an… | 0 | ratio | missing.max | train | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 103 | data_integrity | The largest missing fraction in the training split is 0 , an… | 0 | ratio | missing.max | test | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 104 | data_integrity | The comparison the rule makes across the two splits is the d… | 0.1 | ratio | missing_gap |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 105 | data_integrity | The largest train-to-test population stability reading, the… | 0.01095 | ratio | psi |  | eq | `[[art:381b2570:psi.max]]` | verified | 0.01095273358 |
| 106 | data_integrity | The largest train-to-test population stability reading, the… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 107 | data_integrity | The largest train-to-test population stability reading, the… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 108 | data_integrity | That maximum is carried by the credit-limit characteristic a… | 0.01095 | ratio | psi |  | eq | `[[art:601cdba2:psi.limit_bal]]` | verified | 0.01095273358 |
| 109 | data_integrity | That maximum is carried by the credit-limit characteristic a… | 0.007023 | ratio | psi |  | eq | `[[art:a2885abf:psi.y_score]]` | verified | 0.007023143302 |
| 110 | data_integrity | The remaining population readings are 0.008124 for age, 0.00… | 0.008124 | ratio | psi |  | eq | `[[art:f9255a0a:psi.age]]` | verified | 0.008124281436 |
| 111 | data_integrity | The remaining population readings are 0.008124 for age, 0.00… | 0.004244 | ratio | psi |  | eq | `[[art:451e0780:psi.utilisation]]` | verified | 0.0042440485 |
| 112 | data_integrity | The remaining population readings are 0.008124 for age, 0.00… | 0.004966 | ratio | psi |  | eq | `[[art:3af2ca29:psi.pay_ratio_last]]` | verified | 0.00496591109 |
| 113 | data_integrity | The remaining population readings are 0.008124 for age, 0.00… | 0.0055 | ratio | psi |  | eq | `[[art:2c5baeb2:psi.pay_ratio_mean_6m]]` | verified | 0.005500252946 |
| 114 | data_integrity | The remaining population readings are 0.008124 for age, 0.00… | 0.00285 | ratio | psi |  | eq | `[[art:03bd52e7:psi.delinq_last]]` | verified | 0.002849633848 |
| 115 | data_integrity | The remaining population readings are 0.008124 for age, 0.00… | 0.002069 | ratio | psi |  | eq | `[[art:61491d02:psi.delinq_count_6m]]` | verified | 0.002069275496 |
| 116 | data_integrity | The remaining population readings are 0.008124 for age, 0.00… | 0.005498 | ratio | psi |  | eq | `[[art:7a82e7f3:psi.delinq_max_6m]]` | verified | 0.005498249408 |
| 117 | data_integrity | The remaining population readings are 0.008124 for age, 0.00… | 0.007124 | ratio | psi |  | eq | `[[art:028e4281:psi.bill_mean_6m]]` | verified | 0.007124196275 |
| 118 | data_integrity | The remaining population readings are 0.008124 for age, 0.00… | 0.00958 | ratio | psi |  | eq | `[[art:c247a6f2:psi.bill_trend_6m]]` | verified | 0.009579614525 |
| 119 | data_integrity | Each of those readings sits below the stability bound of 0.2… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 120 | data_integrity | The largest characteristic contribution to the shift in the… | 0.02363 | ratio | csi |  | eq | `[[art:e56cb179:csi.max]]` | verified | 0.02362581795 |
| 121 | data_integrity | The largest characteristic contribution to the shift in the… | 0.02363 | ratio | csi |  | eq | `[[art:5babe364:csi.delinq_last]]` | verified | 0.02362581795 |
| 122 | data_integrity | The largest characteristic contribution to the shift in the… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 123 | data_integrity | The other contributions are 0.00633 and 0.002369 for the bil… | 0.00633 | ratio | csi |  | eq | `[[art:59948e6d:csi.bill_trend_6m]]` | verified | 0.006329590221 |
| 124 | data_integrity | The other contributions are 0.00633 and 0.002369 for the bil… | 0.002369 | ratio | csi |  | eq | `[[art:48df6cc9:csi.bill_mean_6m]]` | verified | 0.002369326368 |
| 125 | data_integrity | The other contributions are 0.00633 and 0.002369 for the bil… | 0.004042 | ratio | csi |  | eq | `[[art:10f0f9e7:csi.utilisation]]` | verified | 0.004041856699 |
| 126 | data_integrity | The other contributions are 0.00633 and 0.002369 for the bil… | 0.002449 | ratio | csi |  | eq | `[[art:69346f52:csi.delinq_count_6m]]` | verified | 0.002448902116 |
| 127 | data_integrity | The other contributions are 0.00633 and 0.002369 for the bil… | 0.0008965 | ratio | csi |  | eq | `[[art:7244960d:csi.delinq_max_6m]]` | verified | 0.0008964784296 |
| 128 | data_integrity | The other contributions are 0.00633 and 0.002369 for the bil… | 0.001924 | ratio | csi |  | eq | `[[art:aff2b4bf:csi.pay_ratio_last]]` | verified | 0.001923767196 |
| 129 | data_integrity | The other contributions are 0.00633 and 0.002369 for the bil… | 0.001768 | ratio | csi |  | eq | `[[art:f567818e:csi.pay_ratio_mean_6m]]` | verified | 0.001768345794 |
| 130 | data_integrity | The other contributions are 0.00633 and 0.002369 for the bil… | 0.001211 | ratio | csi |  | eq | `[[art:5b77b34b:csi.limit_bal]]` | verified | 0.001211461258 |
| 131 | data_integrity | The other contributions are 0.00633 and 0.002369 for the bil… | 0.0009476 | ratio | csi |  | eq | `[[art:a78e58f6:csi.age]]` | verified | 0.0009475732594 |
| 132 | data_integrity | No feature is declared as observed during the performance pe… | 0 | count | leakage.timing.n_flagged |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 133 | data_integrity | No feature name matches the target-adjacent lexicon, that co… | 0 | count | leakage.name_screen.n_matched |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 134 | data_integrity | The strongest single feature reaches an AUC of 0.6831 , belo… | 0.6831 | ratio | auc |  | eq | `[[art:fd829fc4:leakage.target_corr.max_single_feature_auc]]` | verified | 0.6831414154 |
| 135 | data_integrity | The strongest single feature reaches an AUC of 0.6831 , belo… | 0.9 | ratio | auc |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 136 | data_integrity | The identity arm, the share of test rows whose subject ident… | 0 | ratio | overlap |  | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 137 | data_integrity | The identity arm, the share of test rows whose subject ident… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 138 | data_integrity | The feature-vector arm, the share of test rows whose feature… | 0 | ratio | overlap |  | eq | `[[art:0fec8048:leakage.overlap.features]]` | verified | 0 |
| 139 | data_integrity | The feature-vector arm, the share of test rows whose feature… | 0.005 | ratio | overlap |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 140 | data_integrity | That duplicate share is 0 , so the allowance adds nothing an… | 0 | ratio | duplicates | train | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 141 | data_integrity | The overall share of test rows whose feature values also app… | 0 | ratio | overlap |  | eq | `[[art:4c9fcd09:leakage.overlap]]` | verified | 0 |
| 142 | data_integrity | The overall share of test rows whose feature values also app… | 0.005 | ratio | overlap |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 143 | outcomes | The reason is the observed event rate on the evaluation spli… | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 144 | outcomes | The reason is the observed event rate on the evaluation spli… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 145 | outcomes | \| Rows \| 3500 \| 1500 \| | 3500 | count | n | train | eq | `[[art:564683ee:metrics.train.n]]` | verified | 3500 |
| 146 | outcomes | \| Rows \| 3500 \| 1500 \| | 1500 | count | n | test | eq | `[[art:64fcf14d:metrics.test.n]]` | verified | 1500 |
| 147 | outcomes | \| Event rate \| 0.2246 \| 0.2247 \| | 0.2246 | ratio | event_rate | train | eq | `[[art:133a5ff8:metrics.train.event_rate]]` | verified | 0.2245714286 |
| 148 | outcomes | \| Event rate \| 0.2246 \| 0.2247 \| | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 149 | outcomes | \| AUC \| 0.7584 \| 0.748 \| | 0.7584 | ratio | auc | train | eq | `[[art:14b38a2b:metrics.train.auc]]` | verified | 0.7584356677 |
| 150 | outcomes | \| AUC \| 0.7584 \| 0.748 \| | 0.748 | ratio | auc | test | eq | `[[art:5c6c2bfc:metrics.test.auc]]` | verified | 0.7479888042 |
| 151 | outcomes | \| Gini \| 0.5169 \| 0.496 \| | 0.5169 | ratio | gini | train | eq | `[[art:b4da846e:metrics.train.gini]]` | verified | 0.5168713353 |
| 152 | outcomes | \| Gini \| 0.5169 \| 0.496 \| | 0.496 | ratio | gini | test | eq | `[[art:8e5918d8:metrics.test.gini]]` | verified | 0.4959776083 |
| 153 | outcomes | \| KS \| 0.4451 \| 0.4183 \| | 0.4451 | ratio | ks | train | eq | `[[art:ccc12729:metrics.train.ks]]` | verified | 0.4451397991 |
| 154 | outcomes | \| KS \| 0.4451 \| 0.4183 \| | 0.4183 | ratio | ks | test | eq | `[[art:90751047:metrics.test.ks]]` | verified | 0.4182675012 |
| 155 | outcomes | \| Brier \| 0.1489 \| 0.1489 \| | 0.1489 | ratio | brier | train | eq | `[[art:be669a99:metrics.train.brier]]` | verified | 0.1489149059 |
| 156 | outcomes | \| Brier \| 0.1489 \| 0.1489 \| | 0.1489 | ratio | brier | test | eq | `[[art:bbe69430:metrics.test.brier]]` | verified | 0.148850901 |
| 157 | outcomes | \| Log loss \| 0.465 \| 0.4673 \| | 0.465 | ratio | logloss | train | eq | `[[art:4f02e465:metrics.train.logloss]]` | verified | 0.4650014911 |
| 158 | outcomes | \| Log loss \| 0.465 \| 0.4673 \| | 0.4673 | ratio | logloss | test | eq | `[[art:dda8da69:metrics.test.logloss]]` | verified | 0.4672914712 |
| 159 | outcomes | \| Mean predicted \| 0.2246 \| 0.2211 \| | 0.2246 | ratio | mean_predicted | train | eq | `[[art:605cce58:metrics.train.mean_predicted]]` | verified | 0.2246226934 |
| 160 | outcomes | \| Mean predicted \| 0.2246 \| 0.2211 \| | 0.2211 | ratio | mean_predicted | test | eq | `[[art:4d2f8a37:metrics.test.mean_predicted]]` | verified | 0.2211048954 |
| 161 | outcomes | Rank-ordering carries through to the tails: the top two deci… | 0.4718 | ratio | top2_capture | test | eq | `[[art:d4a1cf7d:deciles.test.top2_capture]]` | verified | 0.471810089 |
| 162 | outcomes | Rank-ordering carries through to the tails: the top two deci… | 0.4517 | ratio | top2_capture | train | eq | `[[art:1d20c762:deciles.train.top2_capture]]` | verified | 0.451653944 |
| 163 | outcomes | AUC on train, 0.7584 , sits above AUC on test, 0.748 , so th… | 0.7584 | ratio | auc | train | eq | `[[art:14b38a2b:metrics.train.auc]]` | verified | 0.7584356677 |
| 164 | outcomes | AUC on train, 0.7584 , sits above AUC on test, 0.748 , so th… | 0.748 | ratio | auc | test | eq | `[[art:5c6c2bfc:metrics.test.auc]]` | verified | 0.7479888042 |
| 165 | outcomes | The bound against which that train-to-test AUC gap is judged… | 0.08 | ratio | auc_gap |  | eq | `[[art:630f28f4:threshold.O1.auc_gap]]` | verified | 0.08 |
| 166 | outcomes | The largest train-to-test population stability index across… | 0.01095 | ratio | psi |  | eq | `[[art:381b2570:psi.max]]` | verified | 0.01095273358 |
| 167 | outcomes | The largest train-to-test population stability index across… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 168 | outcomes | The logistic regression of the outcome on the logit of the p… | 1.003 | ratio | calibration_slope | test | eq | `[[art:b7dbb687:calibration_slope.test]]` | verified | 1.002737656 |
| 169 | outcomes | The logistic regression of the outcome on the logit of the p… | 0.8 | ratio | calibration_slope |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 170 | outcomes | The logistic regression of the outcome on the logit of the p… | 1.2 | ratio | calibration_slope |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 171 | outcomes | The intercept of that same regression on test is 0.02729 , a… | 0.02729 | ratio | calibration_intercept | test | eq | `[[art:b69c6b52:calibration_intercept.test]]` | verified | 0.0272850692 |
| 172 | outcomes | The intercept of that same regression on test is 0.02729 , a… | 1.002 | ratio | calibration_slope | train | eq | `[[art:d02e3091:calibration_slope.train]]` | verified | 1.002102954 |
| 173 | outcomes | The intercept of that same regression on test is 0.02729 , a… | 0.002062 | ratio | calibration_intercept | train | eq | `[[art:ed381a81:calibration_intercept.train]]` | verified | 0.002061562686 |
| 174 | outcomes | Mean predicted probability on test, 0.2211 , sits just below… | 0.2211 | ratio | mean_predicted | test | eq | `[[art:4d2f8a37:metrics.test.mean_predicted]]` | verified | 0.2211048954 |
| 175 | outcomes | Mean predicted probability on test, 0.2211 , sits just below… | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 176 | outcomes | Expressed relatively, that discrepancy is 0.01585 , well wit… | 0.01585 | ratio | mean_rel_gap | test | eq | `[[art:d8ffb3d0:calibration.mean_rel_gap.test]]` | verified | 0.01585358118 |
| 177 | outcomes | Expressed relatively, that discrepancy is 0.01585 , well wit… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 178 | outcomes | Comparing the same relative discrepancy across the two split… | 0.01585 | ratio | mean_rel_gap | test | eq | `[[art:d8ffb3d0:calibration.mean_rel_gap.test]]` | verified | 0.01585358118 |
| 179 | outcomes | Comparing the same relative discrepancy across the two split… | 0.0002283 | ratio | mean_rel_gap | train | eq | `[[art:53738d45:calibration.mean_rel_gap.train]]` | verified | 0.0002282786273 |
| 180 | outcomes | AUC on this slice, 0.5689 , falls 0.1791 below AUC on all of… | 0.5689 | ratio | auc | test | eq | `[[art:13b21546:metrics.test.sub.utilisation_high.auc]]` | verified | 0.5688944099 |
| 181 | outcomes | AUC on this slice, 0.5689 , falls 0.1791 below AUC on all of… | 0.1791 | ratio | auc_gap | test | eq | `[[art:e0dc4aa9:metrics.test.sub.utilisation_high.auc_gap]]` | verified | 0.1790943942 |
| 182 | outcomes | AUC on this slice, 0.5689 , falls 0.1791 below AUC on all of… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 183 | outcomes | The slice holds 0.5 of the split, above the floor of 0.1 a s… | 0.5 | ratio | share | test | eq | `[[art:9404484e:metrics.test.sub.utilisation_high.share]]` | verified | 0.5 |
| 184 | outcomes | The slice holds 0.5 of the split, above the floor of 0.1 a s… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 185 | outcomes | The slice holds 0.5 of the split, above the floor of 0.1 a s… | 0.95 | ratio | slice_max_share |  | eq | `[[art:a928a05c:threshold.O1.slice_max_share]]` | verified | 0.95 |
| 186 | outcomes | Mean predicted probability here, 0.2286 , sits close to the… | 0.2286 | ratio | mean_predicted | test | eq | `[[art:2d88d7b5:metrics.test.sub.utilisation_high.mean_predicted]]` | verified | 0.2286105275 |
| 187 | outcomes | Mean predicted probability here, 0.2286 , sits close to the… | 0.2333 | ratio | event_rate | test | eq | `[[art:8e66209c:metrics.test.sub.utilisation_high.event_rate]]` | verified | 0.2333333333 |
| 188 | outcomes | Mean predicted probability here, 0.2286 , sits close to the… | 0.02024 | ratio | mean_rel_gap | test | eq | `[[art:e33a14d6:metrics.test.sub.utilisation_high.mean_rel_gap]]` | verified | 0.02024059629 |
| 189 | outcomes | AUC on this slice, 0.8986 , stands above AUC on all of test,… | 0.8986 | ratio | auc | test | eq | `[[art:f85acc05:metrics.test.sub.utilisation_low.auc]]` | verified | 0.8985890653 |
| 190 | outcomes | AUC on this slice, 0.8986 , stands above AUC on all of test,… | -0.1506 | ratio | auc_gap | test | eq | `[[art:f391975a:metrics.test.sub.utilisation_low.auc_gap]]` | verified | -0.1506002611 |
| 191 | outcomes | AUC on this slice, 0.8986 , stands above AUC on all of test,… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 192 | outcomes | The slice holds 0.5 of the split, above the floor of 0.1 . | 0.5 | ratio | share | test | eq | `[[art:7860a748:metrics.test.sub.utilisation_low.share]]` | verified | 0.5 |
| 193 | outcomes | The slice holds 0.5 of the split, above the floor of 0.1 . | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 194 | outcomes | Mean predicted probability, 0.2136 , sits just below the obs… | 0.2136 | ratio | mean_predicted | test | eq | `[[art:705aaaaa:metrics.test.sub.utilisation_low.mean_predicted]]` | verified | 0.2135992633 |
| 195 | outcomes | Mean predicted probability, 0.2136 , sits just below the obs… | 0.216 | ratio | event_rate | test | eq | `[[art:b0ad49be:metrics.test.sub.utilisation_low.event_rate]]` | verified | 0.216 |
| 196 | outcomes | Mean predicted probability, 0.2136 , sits just below the obs… | 0.01111 | ratio | mean_rel_gap | test | eq | `[[art:5c974ecf:metrics.test.sub.utilisation_low.mean_rel_gap]]` | verified | 0.01111452166 |
| 197 | outcomes | AUC on this slice, 0.75 , stands marginally above AUC on all… | 0.75 | ratio | auc | test | eq | `[[art:cce9cb57:metrics.test.sub.delinq_count_6m_high.auc]]` | verified | 0.7499561404 |
| 198 | outcomes | AUC on this slice, 0.75 , stands marginally above AUC on all… | -0.001967 | ratio | auc_gap | test | eq | `[[art:e1299157:metrics.test.sub.delinq_count_6m_high.auc_gap]]` | verified | -0.001967336199 |
| 199 | outcomes | AUC on this slice, 0.75 , stands marginally above AUC on all… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 200 | outcomes | The slice holds 0.3667 of the split, above the floor of 0.1… | 0.3667 | ratio | share | test | eq | `[[art:22847310:metrics.test.sub.delinq_count_6m_high.share]]` | verified | 0.3666666667 |
| 201 | outcomes | The slice holds 0.3667 of the split, above the floor of 0.1… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 202 | outcomes | Mean predicted probability here, 0.3198 , sits below the obs… | 0.3198 | ratio | mean_predicted | test | eq | `[[art:56c1526c:metrics.test.sub.delinq_count_6m_high.mean_predicted]]` | verified | 0.3198382924 |
| 203 | outcomes | Mean predicted probability here, 0.3198 , sits below the obs… | 0.3455 | ratio | event_rate | test | eq | `[[art:ef17c303:metrics.test.sub.delinq_count_6m_high.event_rate]]` | verified | 0.3454545455 |
| 204 | outcomes | Mean predicted probability here, 0.3198 , sits below the obs… | 0.07415 | ratio | mean_rel_gap | test | eq | `[[art:a9cbcc36:metrics.test.sub.delinq_count_6m_high.mean_rel_gap]]` | verified | 0.07415231158 |
| 205 | outcomes | AUC on this slice, 0.6599 , falls 0.08813 below AUC on all o… | 0.6599 | ratio | auc | test | eq | `[[art:7f51de37:metrics.test.sub.delinq_count_6m_low.auc]]` | verified | 0.6598554739 |
| 206 | outcomes | AUC on this slice, 0.6599 , falls 0.08813 below AUC on all o… | 0.08813 | ratio | auc_gap | test | eq | `[[art:bcc5022d:metrics.test.sub.delinq_count_6m_low.auc_gap]]` | verified | 0.08813333021 |
| 207 | outcomes | AUC on this slice, 0.6599 , falls 0.08813 below AUC on all o… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 208 | outcomes | The slice holds 0.6333 of the split, above the floor of 0.1… | 0.6333 | ratio | share | test | eq | `[[art:3257b2f3:metrics.test.sub.delinq_count_6m_low.share]]` | verified | 0.6333333333 |
| 209 | outcomes | The slice holds 0.6333 of the split, above the floor of 0.1… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 210 | outcomes | The slice holds 0.6333 of the split, above the floor of 0.1… | 0.95 | ratio | slice_max_share |  | eq | `[[art:a928a05c:threshold.O1.slice_max_share]]` | verified | 0.95 |
| 211 | outcomes | Mean predicted probability here, 0.1639 , sits above the obs… | 0.1639 | ratio | mean_predicted | test | eq | `[[art:5f0fb0df:metrics.test.sub.delinq_count_6m_low.mean_predicted]]` | verified | 0.1639434551 |
| 212 | outcomes | Mean predicted probability here, 0.1639 , sits above the obs… | 0.1547 | ratio | event_rate | test | eq | `[[art:9690f94d:metrics.test.sub.delinq_count_6m_low.event_rate]]` | verified | 0.1547368421 |
| 213 | outcomes | Mean predicted probability here, 0.1639 , sits above the obs… | 0.0595 | ratio | mean_rel_gap | test | eq | `[[art:016ca7c3:metrics.test.sub.delinq_count_6m_low.mean_rel_gap]]` | verified | 0.05949851933 |
| 214 | outcomes | Comparing the relative level discrepancies across the two ha… | 0.07415 | ratio | mean_rel_gap | test | eq | `[[art:a9cbcc36:metrics.test.sub.delinq_count_6m_high.mean_rel_gap]]` | verified | 0.07415231158 |
| 215 | outcomes | Comparing the relative level discrepancies across the two ha… | 0.0595 | ratio | mean_rel_gap | test | eq | `[[art:016ca7c3:metrics.test.sub.delinq_count_6m_low.mean_rel_gap]]` | verified | 0.05949851933 |
| 216 | sensitivity | The largest variance inflation factor across the retained fe… | 7.295 | ratio | vif |  | eq | `[[art:9ae7c45b:vif.max]]` | verified | 7.295299885 |
| 217 | sensitivity | The largest variance inflation factor across the retained fe… | 10 | ratio | vif |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 218 | sensitivity | That maximum is attained by `bill_mean_6m`, at 7.295 , with… | 7.295 | ratio | vif |  | eq | `[[art:f0a2f865:vif.bill_mean_6m]]` | verified | 7.295299885 |
| 219 | sensitivity | That maximum is attained by `bill_mean_6m`, at 7.295 , with… | 7.264 | ratio | vif |  | eq | `[[art:c2de8dfe:vif.pay_ratio_last]]` | verified | 7.264342098 |
| 220 | sensitivity | That maximum is attained by `bill_mean_6m`, at 7.295 , with… | 7.259 | ratio | vif |  | eq | `[[art:e39c3e82:vif.pay_ratio_mean_6m]]` | verified | 7.25926398 |
| 221 | sensitivity | The remaining retained features fall further from the ceilin… | 4.803 | ratio | vif |  | eq | `[[art:ddfdcc3c:vif.limit_bal]]` | verified | 4.803401129 |
| 222 | sensitivity | The remaining retained features fall further from the ceilin… | 3.215 | ratio | vif |  | eq | `[[art:536fdb6f:vif.utilisation]]` | verified | 3.215148369 |
| 223 | sensitivity | The remaining retained features fall further from the ceilin… | 2.561 | ratio | vif |  | eq | `[[art:38974def:vif.delinq_count_6m]]` | verified | 2.561484187 |
| 224 | sensitivity | The remaining retained features fall further from the ceilin… | 2.408 | ratio | vif |  | eq | `[[art:71aaaf11:vif.delinq_max_6m]]` | verified | 2.40773 |
| 225 | sensitivity | The remaining retained features fall further from the ceilin… | 1.412 | ratio | vif |  | eq | `[[art:48733638:vif.delinq_last]]` | verified | 1.411555667 |
| 226 | sensitivity | The remaining retained features fall further from the ceilin… | 1.201 | ratio | vif |  | eq | `[[art:9356a256:vif.bill_trend_6m]]` | verified | 1.201449441 |
| 227 | sensitivity | The remaining retained features fall further from the ceilin… | 1.002 | ratio | vif |  | eq | `[[art:74c06cad:vif.age]]` | verified | 1.001957997 |
| 228 | sensitivity | The condition number of the column-standardised design is 5.… | 5.547 | ratio | condition_number |  | eq | `[[art:e41b9562:condition_number]]` | verified | 5.546934633 |
| 229 | sensitivity | The condition number of the column-standardised design is 5.… | 30 | ratio | condition_number |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 230 | findings | The challenger reaches an AUC of 0.824 on test, against the… | 0.824 | ratio | auc | test | eq | `[[art:bf5be719:challenger.auc]]` | verified | 0.823969015 |
| 231 | findings | The challenger reaches an AUC of 0.824 on test, against the… | 0.748 | ratio | auc | test | eq | `[[art:5c6c2bfc:metrics.test.auc]]` | verified | 0.7479888042 |
| 232 | findings | Taken as a difference, the challenger's lead is 0.07598 , wh… | 0.07598 | ratio | delta_auc | test | eq | `[[art:c9e502ae:challenger.delta_auc]]` | verified | 0.0759802108 |
| 233 | findings | Taken as a difference, the challenger's lead is 0.07598 , wh… | 0.03 | ratio | delta_auc |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 234 | findings | Model developer: within `delinq_count_6m <= median(delinq_co… | 0.6599 | ratio | auc | test | eq | `[[art:7f51de37:metrics.test.sub.delinq_count_6m_low.auc]]` | verified | 0.6598554739 |
| 235 | findings | Model developer: within `delinq_count_6m <= median(delinq_co… | 0.08813 | ratio | auc_gap | test | eq | `[[art:bcc5022d:metrics.test.sub.delinq_count_6m_low.auc_gap]]` | verified | 0.08813333021 |
| 236 | findings | Model developer: within `delinq_count_6m <= median(delinq_co… | 0.748 | ratio | auc | test | eq | `[[art:5c6c2bfc:metrics.test.auc]]` | verified | 0.7479888042 |
| 237 | findings | Model developer: within `delinq_count_6m <= median(delinq_co… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 238 | findings | Model developer: within `delinq_count_6m <= median(delinq_co… | 0.6333 | ratio | share | test | eq | `[[art:3257b2f3:metrics.test.sub.delinq_count_6m_low.share]]` | verified | 0.6333333333 |
| 239 | findings | Model developer: within `delinq_count_6m <= median(delinq_co… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 240 | findings | Model developer: within `utilisation > median(utilisation)`,… | 0.5689 | ratio | auc | test | eq | `[[art:13b21546:metrics.test.sub.utilisation_high.auc]]` | verified | 0.5688944099 |
| 241 | findings | Model developer: within `utilisation > median(utilisation)`,… | 0.1791 | ratio | auc_gap | test | eq | `[[art:e0dc4aa9:metrics.test.sub.utilisation_high.auc_gap]]` | verified | 0.1790943942 |
| 242 | findings | Model developer: within `utilisation > median(utilisation)`,… | 0.748 | ratio | auc | test | eq | `[[art:5c6c2bfc:metrics.test.auc]]` | verified | 0.7479888042 |
| 243 | findings | Model developer: within `utilisation > median(utilisation)`,… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 244 | findings | Model developer: within `utilisation > median(utilisation)`,… | 0.5 | ratio | share | test | eq | `[[art:9404484e:metrics.test.sub.utilisation_high.share]]` | verified | 0.5 |
| 245 | findings | Model developer: within `utilisation > median(utilisation)`,… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 246 | findings | Model developer: what drives the fitted coefficient on `deli… | -1 | ratio | coef_sign |  | eq | `[[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]]` | verified | -1 |
| 247 | findings | Model developer: what drives the fitted coefficient on `deli… | 1 | ratio | univariate_direction | train | eq | `[[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]]` | verified | 1 |
| 248 | findings | Model developer: what drives the fitted coefficient on `deli… | 0 | ratio | agrees |  | eq | `[[art:c946359c:sign_check.delinq_max_6m.agrees]]` | verified | 0 |
| 249 | findings | Model developer: what drives the fitted coefficient on `limi… | 1 | ratio | coef_sign |  | eq | `[[art:6af6aef2:sign_check.limit_bal.coef_sign]]` | verified | 1 |
| 250 | findings | Model developer: what drives the fitted coefficient on `limi… | -1 | ratio | univariate_direction | train | eq | `[[art:56d284d6:sign_check.limit_bal.univariate_direction]]` | verified | -1 |
| 251 | findings | Model developer: what drives the fitted coefficient on `limi… | 0 | ratio | agrees |  | eq | `[[art:0278aad1:sign_check.limit_bal.agrees]]` | verified | 0 |
| 252 | findings | Model developer: what drives the fitted coefficient on `pay_… | 1 | ratio | coef_sign |  | eq | `[[art:f018263e:sign_check.pay_ratio_last.coef_sign]]` | verified | 1 |
| 253 | findings | Model developer: what drives the fitted coefficient on `pay_… | -1 | ratio | univariate_direction | train | eq | `[[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]]` | verified | -1 |
| 254 | findings | Model developer: what drives the fitted coefficient on `pay_… | 0 | ratio | agrees |  | eq | `[[art:79abee77:sign_check.pay_ratio_last.agrees]]` | verified | 0 |
| 255 | monitoring | Rank-ordering ability should be recomputed and compared with… | 0.7 | ratio | auc | test | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 256 | monitoring | Rank-ordering ability should be recomputed and compared with… | 0.748 | ratio | auc | test | eq | `[[art:5c6c2bfc:metrics.test.auc]]` | verified | 0.7479888042 |
| 257 | monitoring | The mean squared error of the predicted probabilities should… | 0.2 | ratio | brier | test | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 258 | monitoring | The mean squared error of the predicted probabilities should… | 0.1489 | ratio | brier | test | eq | `[[art:bbe69430:metrics.test.brier]]` | verified | 0.148850901 |
| 259 | monitoring | The slope of the logistic regression of the outcome on the l… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 260 | monitoring | The slope of the logistic regression of the outcome on the l… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 261 | monitoring | The slope of the logistic regression of the outcome on the l… | 1.003 | ratio | calibration_slope | test | eq | `[[art:b7dbb687:calibration_slope.test]]` | verified | 1.002737656 |
| 262 | monitoring | Population stability across the scored features and the scor… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 263 | monitoring | Population stability across the scored features and the scor… | 0.01095 | ratio | psi |  | eq | `[[art:381b2570:psi.max]]` | verified | 0.01095273358 |
| 264 | monitoring | If a future production cohort has an observed event rate bel… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |

## Appendix B — Artifact index

The store holds 219 artifacts; the 170 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `ablation.age.delta_auc` | `59398b1b` | scalar | 8.674996364e-05 | change in test AUC when the champion's form is refitted without age |
| `ablation.baseline_auc` | `3a44e438` | scalar | 0.7479888042 | AUC on test of a refit of the champion's functional form on every retained feature, the level each ablation delta is measured from |
| `ablation.bill_mean_6m.delta_auc` | `3b91a889` | scalar | -0.001599771388 | change in test AUC when the champion's form is refitted without bill_mean_6m |
| `ablation.bill_trend_6m.delta_auc` | `096d7f98` | scalar | 0.003278638332 | change in test AUC when the champion's form is refitted without bill_trend_6m |
| `ablation.delinq_count_6m.delta_auc` | `c5659def` | scalar | 0.0006812423615 | change in test AUC when the champion's form is refitted without delinq_count_6m |
| `ablation.delinq_last.delta_auc` | `3150b111` | scalar | -0.07585263733 | change in test AUC when the champion's form is refitted without delinq_last |
| `ablation.delinq_max_6m.delta_auc` | `3a0d3a0c` | scalar | 0.0003597572022 | change in test AUC when the champion's form is refitted without delinq_max_6m |
| `ablation.limit_bal.delta_auc` | `63faa640` | scalar | 0.0004286468792 | change in test AUC when the champion's form is refitted without limit_bal |
| `ablation.pay_ratio_last.delta_auc` | `5f39089e` | scalar | 0.002411138695 | change in test AUC when the champion's form is refitted without pay_ratio_last |
| `ablation.pay_ratio_mean_6m.delta_auc` | `90fa1178` | scalar | 0.006603203115 | change in test AUC when the champion's form is refitted without pay_ratio_mean_6m |
| `ablation.utilisation.delta_auc` | `d4ad2039` | scalar | -0.01976623436 | change in test AUC when the champion's form is refitted without utilisation |
| `calibration.mean_rel_gap.test` | `d8ffb3d0` | scalar | 0.01585358118 | mean predicted against observed on test, relative |
| `calibration.mean_rel_gap.train` | `53738d45` | scalar | 0.0002282786273 | mean predicted against observed on train, relative |
| `calibration.test` | `508ffcf8` | table | table, 10 rows | calibration by decile of predicted probability on test |
| `calibration_intercept.test` | `b69c6b52` | scalar | 0.0272850692 | logistic regression of the outcome on logit(p) on test: the intercept |
| `calibration_intercept.train` | `ed381a81` | scalar | 0.002061562686 | logistic regression of the outcome on logit(p) on train: the intercept |
| `calibration_slope.test` | `b7dbb687` | scalar | 1.002737656 | logistic regression of the outcome on logit(p) on test: the slope |
| `calibration_slope.train` | `d02e3091` | scalar | 1.002102954 | logistic regression of the outcome on logit(p) on train: the slope |
| `challenger.auc` | `bf5be719` | scalar | 0.823969015 | the challenger's AUC on test |
| `challenger.brier` | `f9e0583d` | scalar | 0.1258050391 | the challenger's Brier score on test |
| `challenger.delta_auc` | `c9e502ae` | scalar | 0.0759802108 | the challenger's AUC on test minus the champion's |
| `condition_number` | `e41b9562` | scalar | 5.546934633 | Belsley's condition number of the column-standardised design |
| `csi.age` | `a78e58f6` | scalar | 0.0009475732594 | CSI of age: its contribution to the shift in the linear predictor |
| `csi.bill_mean_6m` | `48df6cc9` | scalar | 0.002369326368 | CSI of bill_mean_6m: its contribution to the shift in the linear predictor |
| `csi.bill_trend_6m` | `59948e6d` | scalar | 0.006329590221 | CSI of bill_trend_6m: its contribution to the shift in the linear predictor |
| `csi.delinq_count_6m` | `69346f52` | scalar | 0.002448902116 | CSI of delinq_count_6m: its contribution to the shift in the linear predictor |
| `csi.delinq_last` | `5babe364` | scalar | 0.02362581795 | CSI of delinq_last: its contribution to the shift in the linear predictor |
| `csi.delinq_max_6m` | `7244960d` | scalar | 0.0008964784296 | CSI of delinq_max_6m: its contribution to the shift in the linear predictor |
| `csi.limit_bal` | `5b77b34b` | scalar | 0.001211461258 | CSI of limit_bal: its contribution to the shift in the linear predictor |
| `csi.max` | `e56cb179` | scalar | 0.02362581795 | the largest characteristic stability index |
| `csi.pay_ratio_last` | `aff2b4bf` | scalar | 0.001923767196 | CSI of pay_ratio_last: its contribution to the shift in the linear predictor |
| `csi.pay_ratio_mean_6m` | `f567818e` | scalar | 0.001768345794 | CSI of pay_ratio_mean_6m: its contribution to the shift in the linear predictor |
| `csi.utilisation` | `10f0f9e7` | scalar | 0.004041856699 | CSI of utilisation: its contribution to the shift in the linear predictor |
| `deciles.test` | `15d50c28` | table | table, 10 rows | decile separation on test; decile 1 holds the highest probabilities |
| `deciles.test.top2_capture` | `d4a1cf7d` | scalar | 0.471810089 | share of test events in the top two deciles |
| `deciles.train.top2_capture` | `1d20c762` | scalar | 0.451653944 | share of train events in the top two deciles |
| `leakage.duplicates.train` | `4474c227` | scalar | 0 | share of train rows whose feature values are not unique within train |
| `leakage.name_screen.n_matched` | `407e62be` | scalar | 0 | feature names matching the target-adjacent lexicon |
| `leakage.overlap` | `4c9fcd09` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.features` | `0fec8048` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.ids` | `63d37fc5` | scalar | 0 | share of test rows whose ['client_id'] also identify a row of train |
| `leakage.target_corr.max_single_feature_auc` | `fd829fc4` | scalar | 0.6831414154 | the AUC of the strongest single feature |
| `leakage.timing.n_flagged` | `742bcd24` | scalar | 0 | features declared during_period or after_outcome |
| `metrics.test.auc` | `5c6c2bfc` | scalar | 0.7479888042 | auc on test, recomputed by quaestor |
| `metrics.test.brier` | `bbe69430` | scalar | 0.148850901 | brier on test, recomputed by quaestor |
| `metrics.test.event_rate` | `9209d200` | scalar | 0.2246666667 | event_rate on test, recomputed by quaestor |
| `metrics.test.gini` | `8e5918d8` | scalar | 0.4959776083 | gini on test, recomputed by quaestor |
| `metrics.test.ks` | `90751047` | scalar | 0.4182675012 | ks on test, recomputed by quaestor |
| `metrics.test.logloss` | `dda8da69` | scalar | 0.4672914712 | logloss on test, recomputed by quaestor |
| `metrics.test.mean_predicted` | `4d2f8a37` | scalar | 0.2211048954 | mean_predicted on test, recomputed by quaestor |
| `metrics.test.n` | `64fcf14d` | scalar | 1500 | n on test, recomputed by quaestor |
| `metrics.test.sub.delinq_count_6m_high` | `2a7e6e1d` | table | table, 10 rows | every metric on the delinq_count_6m above_median slice of test |
| `metrics.test.sub.delinq_count_6m_high.auc` | `cce9cb57` | scalar | 0.7499561404 | auc on the delinq_count_6m above_median slice of test |
| `metrics.test.sub.delinq_count_6m_high.auc_gap` | `e1299157` | scalar | -0.001967336199 | how far AUC on the delinq_count_6m above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.delinq_count_6m_high.event_rate` | `ef17c303` | scalar | 0.3454545455 | event_rate on the delinq_count_6m above_median slice of test |
| `metrics.test.sub.delinq_count_6m_high.mean_predicted` | `56c1526c` | scalar | 0.3198382924 | mean_predicted on the delinq_count_6m above_median slice of test |
| `metrics.test.sub.delinq_count_6m_high.mean_rel_gap` | `a9cbcc36` | scalar | 0.07415231158 | mean predicted against observed on the delinq_count_6m above_median slice of test, relative |
| `metrics.test.sub.delinq_count_6m_high.share` | `22847310` | scalar | 0.3666666667 | the share of test the delinq_count_6m above_median slice holds |
| `metrics.test.sub.delinq_count_6m_low` | `ee4d42af` | table | table, 10 rows | every metric on the delinq_count_6m below_median slice of test |
| `metrics.test.sub.delinq_count_6m_low.auc` | `7f51de37` | scalar | 0.6598554739 | auc on the delinq_count_6m below_median slice of test |
| `metrics.test.sub.delinq_count_6m_low.auc_gap` | `bcc5022d` | scalar | 0.08813333021 | how far AUC on the delinq_count_6m below_median slice of test falls below AUC on all of test |
| `metrics.test.sub.delinq_count_6m_low.event_rate` | `9690f94d` | scalar | 0.1547368421 | event_rate on the delinq_count_6m below_median slice of test |
| `metrics.test.sub.delinq_count_6m_low.mean_predicted` | `5f0fb0df` | scalar | 0.1639434551 | mean_predicted on the delinq_count_6m below_median slice of test |
| `metrics.test.sub.delinq_count_6m_low.mean_rel_gap` | `016ca7c3` | scalar | 0.05949851933 | mean predicted against observed on the delinq_count_6m below_median slice of test, relative |
| `metrics.test.sub.delinq_count_6m_low.share` | `3257b2f3` | scalar | 0.6333333333 | the share of test the delinq_count_6m below_median slice holds |
| `metrics.test.sub.utilisation_high` | `ab9ef6ac` | table | table, 10 rows | every metric on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.auc` | `13b21546` | scalar | 0.5688944099 | auc on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.auc_gap` | `e0dc4aa9` | scalar | 0.1790943942 | how far AUC on the utilisation above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.utilisation_high.event_rate` | `8e66209c` | scalar | 0.2333333333 | event_rate on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.mean_predicted` | `2d88d7b5` | scalar | 0.2286105275 | mean_predicted on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.mean_rel_gap` | `e33a14d6` | scalar | 0.02024059629 | mean predicted against observed on the utilisation above_median slice of test, relative |
| `metrics.test.sub.utilisation_high.share` | `9404484e` | scalar | 0.5 | the share of test the utilisation above_median slice holds |
| `metrics.test.sub.utilisation_low` | `8e1db133` | table | table, 10 rows | every metric on the utilisation below_median slice of test |
| `metrics.test.sub.utilisation_low.auc` | `f85acc05` | scalar | 0.8985890653 | auc on the utilisation below_median slice of test |
| `metrics.test.sub.utilisation_low.auc_gap` | `f391975a` | scalar | -0.1506002611 | how far AUC on the utilisation below_median slice of test falls below AUC on all of test |
| `metrics.test.sub.utilisation_low.event_rate` | `b0ad49be` | scalar | 0.216 | event_rate on the utilisation below_median slice of test |
| `metrics.test.sub.utilisation_low.mean_predicted` | `705aaaaa` | scalar | 0.2135992633 | mean_predicted on the utilisation below_median slice of test |
| `metrics.test.sub.utilisation_low.mean_rel_gap` | `5c974ecf` | scalar | 0.01111452166 | mean predicted against observed on the utilisation below_median slice of test, relative |
| `metrics.test.sub.utilisation_low.share` | `7860a748` | scalar | 0.5 | the share of test the utilisation below_median slice holds |
| `metrics.train.auc` | `14b38a2b` | scalar | 0.7584356677 | auc on train, recomputed by quaestor |
| `metrics.train.brier` | `be669a99` | scalar | 0.1489149059 | brier on train, recomputed by quaestor |
| `metrics.train.event_rate` | `133a5ff8` | scalar | 0.2245714286 | event_rate on train, recomputed by quaestor |
| `metrics.train.gini` | `b4da846e` | scalar | 0.5168713353 | gini on train, recomputed by quaestor |
| `metrics.train.ks` | `ccc12729` | scalar | 0.4451397991 | ks on train, recomputed by quaestor |
| `metrics.train.logloss` | `4f02e465` | scalar | 0.4650014911 | logloss on train, recomputed by quaestor |
| `metrics.train.mean_predicted` | `605cce58` | scalar | 0.2246226934 | mean_predicted on train, recomputed by quaestor |
| `metrics.train.n` | `564683ee` | scalar | 3500 | n on train, recomputed by quaestor |
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
| `psi.max` | `381b2570` | scalar | 0.01095273358 | the largest train-to-test PSI, score included |
| `psi.pay_ratio_last` | `3af2ca29` | scalar | 0.00496591109 | PSI of pay_ratio_last between train and test |
| `psi.pay_ratio_mean_6m` | `2c5baeb2` | scalar | 0.005500252946 | PSI of pay_ratio_mean_6m between train and test |
| `psi.utilisation` | `451e0780` | scalar | 0.0042440485 | PSI of utilisation between train and test |
| `psi.y_score` | `a2885abf` | scalar | 0.007023143302 | PSI of the score between train and test |
| `rule.calibration_first_event_rate` | `42f1351e` | scalar | 0.05 | the event rate below which the report puts calibration before discrimination |
| `run.features` | `abbb748e` | json | json | the subject's features.json |
| `run.model_summary` | `74c10f15` | json | json | the subject's model_summary.json |
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |
| `sign_check.age.agrees` | `4116add1` | scalar | 1 | 1 when the fitted sign on age agrees with its univariate direction, 0 when it does not |
| `sign_check.age.coef_sign` | `6172eb93` | scalar | -1 | the sign of the fitted coefficient on age |
| `sign_check.age.univariate_direction` | `66364583` | scalar | -1 | the sign of age's own single-feature AUC on train minus 0.5 |
| `sign_check.bill_mean_6m.agrees` | `89279c3b` | scalar | 1 | 1 when the fitted sign on bill_mean_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.bill_mean_6m.coef_sign` | `cee1a18f` | scalar | -1 | the sign of the fitted coefficient on bill_mean_6m |
| `sign_check.bill_mean_6m.univariate_direction` | `23b89c5d` | scalar | -1 | the sign of bill_mean_6m's own single-feature AUC on train minus 0.5 |
| `sign_check.bill_trend_6m.agrees` | `ff3cb24a` | scalar | 1 | 1 when the fitted sign on bill_trend_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.bill_trend_6m.coef_sign` | `7fd8474e` | scalar | -1 | the sign of the fitted coefficient on bill_trend_6m |
| `sign_check.bill_trend_6m.univariate_direction` | `a9bff389` | scalar | -1 | the sign of bill_trend_6m's own single-feature AUC on train minus 0.5 |
| `sign_check.delinq_count_6m.agrees` | `a337d16b` | scalar | 1 | 1 when the fitted sign on delinq_count_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.delinq_count_6m.coef_sign` | `17afb6f9` | scalar | 1 | the sign of the fitted coefficient on delinq_count_6m |
| `sign_check.delinq_count_6m.univariate_direction` | `549e904e` | scalar | 1 | the sign of delinq_count_6m's own single-feature AUC on train minus 0.5 |
| `sign_check.delinq_last.agrees` | `a8ba9372` | scalar | 1 | 1 when the fitted sign on delinq_last agrees with its univariate direction, 0 when it does not |
| `sign_check.delinq_last.coef_sign` | `50d352f8` | scalar | 1 | the sign of the fitted coefficient on delinq_last |
| `sign_check.delinq_last.univariate_direction` | `a78648ba` | scalar | 1 | the sign of delinq_last's own single-feature AUC on train minus 0.5 |
| `sign_check.delinq_max_6m.agrees` | `c946359c` | scalar | 0 | 1 when the fitted sign on delinq_max_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.delinq_max_6m.coef_sign` | `a07d68ab` | scalar | -1 | the sign of the fitted coefficient on delinq_max_6m |
| `sign_check.delinq_max_6m.univariate_direction` | `b9088f4a` | scalar | 1 | the sign of delinq_max_6m's own single-feature AUC on train minus 0.5 |
| `sign_check.limit_bal.agrees` | `0278aad1` | scalar | 0 | 1 when the fitted sign on limit_bal agrees with its univariate direction, 0 when it does not |
| `sign_check.limit_bal.coef_sign` | `6af6aef2` | scalar | 1 | the sign of the fitted coefficient on limit_bal |
| `sign_check.limit_bal.univariate_direction` | `56d284d6` | scalar | -1 | the sign of limit_bal's own single-feature AUC on train minus 0.5 |
| `sign_check.n_disagreements` | `e223cd4a` | scalar | 3 | retained features whose fitted sign contradicts their univariate direction, of 10 checked |
| `sign_check.pay_ratio_last.agrees` | `79abee77` | scalar | 0 | 1 when the fitted sign on pay_ratio_last agrees with its univariate direction, 0 when it does not |
| `sign_check.pay_ratio_last.coef_sign` | `f018263e` | scalar | 1 | the sign of the fitted coefficient on pay_ratio_last |
| `sign_check.pay_ratio_last.univariate_direction` | `f8e46d75` | scalar | -1 | the sign of pay_ratio_last's own single-feature AUC on train minus 0.5 |
| `sign_check.pay_ratio_mean_6m.agrees` | `7e9a76ca` | scalar | 1 | 1 when the fitted sign on pay_ratio_mean_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.pay_ratio_mean_6m.coef_sign` | `077bb6b2` | scalar | -1 | the sign of the fitted coefficient on pay_ratio_mean_6m |
| `sign_check.pay_ratio_mean_6m.univariate_direction` | `24dcef24` | scalar | -1 | the sign of pay_ratio_mean_6m's own single-feature AUC on train minus 0.5 |
| `sign_check.utilisation.agrees` | `d0c9a130` | scalar | 1 | 1 when the fitted sign on utilisation agrees with its univariate direction, 0 when it does not |
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
| `threshold.O1.slice_max_share` | `a928a05c` | scalar | 0.95 | the share of a split at which a sub-population is the whole split and is refused |
| `threshold.O1.slice_min_share` | `9a6f1a87` | scalar | 0.1 | the share of a split a sub-population must hold before it can raise an open item |
| `threshold.S1.psi` | `278b9016` | scalar | 0.25 | S1: the population stability index, train against test |
| `threshold.package.auc.test.min` | `8bfd02cc` | scalar | 0.7 | package.yaml declares auc min 0.7 |
| `threshold.package.brier.test.max` | `d0f98b9c` | scalar | 0.2 | package.yaml declares brier max 0.2 |
| `threshold.package.calibration_slope.test.max` | `0adb7a89` | scalar | 1.2 | package.yaml declares calibration_slope max 1.2 |
| `threshold.package.calibration_slope.test.min` | `95fdb848` | scalar | 0.8 | package.yaml declares calibration_slope min 0.8 |
| `threshold.package.psi.max` | `fbb5a9d1` | scalar | 0.25 | package.yaml declares psi max 0.25 |
| `thresholds.evaluation` | `bc507a88` | table | table, 5 rows | every threshold package.yaml declares, with its bound, the recomputed value and the outcome |
| `vif.age` | `74c06cad` | scalar | 1.001957997 | variance inflation factor of age on train |
| `vif.bill_mean_6m` | `f0a2f865` | scalar | 7.295299885 | variance inflation factor of bill_mean_6m on train |
| `vif.bill_trend_6m` | `9356a256` | scalar | 1.201449441 | variance inflation factor of bill_trend_6m on train |
| `vif.delinq_count_6m` | `38974def` | scalar | 2.561484187 | variance inflation factor of delinq_count_6m on train |
| `vif.delinq_last` | `48733638` | scalar | 1.411555667 | variance inflation factor of delinq_last on train |
| `vif.delinq_max_6m` | `71aaaf11` | scalar | 2.40773 | variance inflation factor of delinq_max_6m on train |
| `vif.limit_bal` | `ddfdcc3c` | scalar | 4.803401129 | variance inflation factor of limit_bal on train |
| `vif.max` | `9ae7c45b` | scalar | 7.295299885 | the largest variance inflation factor |
| `vif.pay_ratio_last` | `c2de8dfe` | scalar | 7.264342098 | variance inflation factor of pay_ratio_last on train |
| `vif.pay_ratio_mean_6m` | `e39c3e82` | scalar | 7.25926398 | variance inflation factor of pay_ratio_mean_6m on train |
| `vif.utilisation` | `536fdb6f` | scalar | 3.215148369 | variance inflation factor of utilisation on train |

## Appendix C — Run trace summary

| quantity | value |
|---|---|
| tool calls | 17 (run_model 1, profile_data 1, compute_metrics 5, check_leakage 1, check_collinearity 1, challenger_compare 1, retrieve_guidance 7) |
| plan steps (bounded loop) | 4 |
| LLM calls | 21 (plan 4, draft 8, reask 1, extract 8) |
| re-asks | 1 |
| repair rounds | 1 |
| tokens in / out | 265,971 / 121,283 |
| notional cost (USD) | 5.7352 |
| wall-clock (s) | 1355.81 |
| subject run (s) | 1.16 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | credit_default-full_agent-20260918T222547Z-e2e51e00 |

## Appendix D — Not checked

| item | reason |
|---|---|
| `check_stability` (R1) | package declares no `regime.column` |
| `run_scenarios` (X1) | not applicable to `binary_classification` |
| out-of-time and vintage-holdout metrics (O1, second rule) | package declares neither split |
| developer claims (T1, claim channel) | The package declares 2 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
