---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: full_agent
model: claude-opus-5[1m]
run_id: credit_default-full_agent-20260920T171411Z-e2e51e00
data_mode: synthetic
synthetic_n: 5000
grounding_precision_pre: 1.0000
grounding_precision_post: 1.0000
n_claims: 228
n_findings_by_severity: {high: 1, medium: 0, low: 1, info: 0}
generated: "2026-09-20T17:14:11Z"
illustrative: false
---

# Validation report — `credit_default` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `credit_default` v1.0 | `full_agent` | claude-opus-5[1m] | synthetic, n = 5000 | 1.0000 → 1.0000 | 1 / 0 / 1 / 0 |
<!-- quaestor:renderer:end -->

This report reviews the credit_default model package at version 1.0, a model that predicts the probability that a borrower defaults, and it follows the structure of the Federal Reserve's model risk management guidance on validation [[reg:SR26-2:V]].
The subject was executed by the validation harness under the wall-clock cap of 300 [[art:2ad8d1a5:runtime.max_seconds]] seconds declared in its package manifest, and the performance figures quoted here were recomputed from the subject's own scored output rather than carried over from developer documentation.
The development split holds 3500 [[art:2510d49d:profile.train.n]] rows and the held-out test split holds 1500 [[art:2193cf5f:profile.test.n]] rows.

Of the developer-declared thresholds, the model passes the Brier bound: the recomputed value on test is 0.1489 [[art:bbe69430:metrics.test.brier]], below the declared maximum of 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]].
It passes the calibration slope bounds: the slope on test is 1.003 [[art:b7dbb687:calibration_slope.test]], above the declared minimum of 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] and below the declared maximum of 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
It passes the population stability bound: the largest train-to-test index, the score included, is 0.01095 [[art:381b2570:psi.max]], below the declared maximum of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].

This validation raised F-001, a T1 declared threshold finding at high severity, and F-002, a E1 effective challenge finding at low severity.
Each is set out in full, with its evidence and its proposed disposition, in the findings section of this report.

## 2. Conceptual soundness

Validating conceptual soundness means assessing and documenting the model's design, construction, and developmental testing, and subjecting the modeling choices to critical analysis of both the quality and the extent of the developmental evidence [[reg:SR26-2:V.1.a]].

### Design and inputs

The champion is a single linear score in the log-odds, with an intercept of -1.396 [[art:74c10f15:run.model_summary#intercept]] and one coefficient per retained feature, fitted on 3500 [[art:74c10f15:run.model_summary#n_train]] training rows.
A form of this kind is legible by construction: each input enters once, monotonically, and its coefficient can be read directly against what the subject matter expects.
The feature inventory holds 12 [[art:abbb748e:run.features#n]] features.
Of these, 2 [[art:abbb748e:run.features#at_origination]] are known at origination and 10 [[art:abbb748e:run.features#before_period_start]] are known before the performance period opens.
No input is drawn from inside the performance period, 0 [[art:abbb748e:run.features#during_period]], and none is drawn from after the outcome is observed, 0 [[art:abbb748e:run.features#after_outcome]].
On timing alone the design is therefore usable at the decision point it is meant to serve, and the inventory shows no input that would only be knowable once the outcome had already occurred.

The developer's own collinearity screen removed bill_last, whose variance inflation was 160.9 [[art:74c10f15:run.model_summary#removed.bill_last.vif]], and utilisation_mean_6m, whose variance inflation was 36.36 [[art:74c10f15:run.model_summary#removed.utilisation_mean_6m.vif]], each read against a declared variance-inflation threshold of 10 [[art:74c10f15:run.model_summary#vif_threshold]].
Both removals are in the direction sound practice expects for a model whose coefficients are meant to be interpreted: near-duplicate billing and utilisation measures inflate each other's standard errors and make the individual signs unreadable.
The screen is a defensible piece of developmental evidence, and the retained design is the one on which every statement below is made.

### Coefficients and expected signs

The largest coefficient in the retained form sits on the most recent delinquency status, at 0.7334 [[art:74c10f15:run.model_summary#coefficients.delinq_last.value]], and its positive sign is what credit subject matter expects: a borrower currently behind is more likely to default.
The next largest are the six-month mean bill at -0.3726 [[art:74c10f15:run.model_summary#coefficients.bill_mean_6m.value]], the six-month mean payment ratio at -0.3554 [[art:74c10f15:run.model_summary#coefficients.pay_ratio_mean_6m.value]], utilisation at 0.2662 [[art:74c10f15:run.model_summary#coefficients.utilisation.value]], and the six-month bill trend at -0.2225 [[art:74c10f15:run.model_summary#coefficients.bill_trend_6m.value]].
The payment-ratio mean and the utilisation coefficients carry the expected signs: paying down more of the balance lowers risk, and drawing more of the line raises it.
The negative signs on the mean bill and on the bill trend are conditional signs, read with utilisation already in the model, and they are best understood as the balance level net of how much of the limit it consumes rather than as a claim that larger bills are safer in isolation.
The smaller coefficients are the six-month delinquency count at 0.1226 [[art:74c10f15:run.model_summary#coefficients.delinq_count_6m.value]], the most recent payment ratio at 0.1026 [[art:74c10f15:run.model_summary#coefficients.pay_ratio_last.value]], the credit limit at 0.07266 [[art:74c10f15:run.model_summary#coefficients.limit_bal.value]], age at -0.06726 [[art:74c10f15:run.model_summary#coefficients.age.value]], and the six-month maximum delinquency at -0.03221 [[art:74c10f15:run.model_summary#coefficients.delinq_max_6m.value]].
The delinquency count and age signs are as expected; a positive coefficient on the credit limit and a negative one on the worst delinquency in the window are not, since larger limits are normally extended to stronger borrowers and a worse delinquency peak should not lower risk.

### Fitted signs against univariate direction

The fitted sign on each retained feature was compared with the direction of that feature's own single-feature relationship with the outcome on train, and 3 [[art:e223cd4a:sign_check.n_disagreements]] of the retained features disagree.
These comparisons are evidence supporting the judgement in this section and no rule is read against them.
The credit limit is fitted positive, 1 [[art:6af6aef2:sign_check.limit_bal.coef_sign]], while on its own it points the other way, -1 [[art:56d284d6:sign_check.limit_bal.univariate_direction]]; refitting the champion's form without it changes test AUC by 0.0004286 [[art:63faa640:ablation.limit_bal.delta_auc]], so the flip sits on a feature the model was not relying on for discrimination.
The most recent payment ratio is fitted positive, 1 [[art:f018263e:sign_check.pay_ratio_last.coef_sign]], against a univariate direction of -1 [[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]]; dropping it changes test AUC by 0.002411 [[art:5f39089e:ablation.pay_ratio_last.delta_auc]], again in the direction of a feature whose removal does not cost discrimination.
The six-month maximum delinquency is fitted negative, -1 [[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]], against a univariate direction of 1 [[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]]; dropping it changes test AUC by 0.0003598 [[art:3a0d3a0c:ablation.delinq_max_6m.delta_auc]], the smallest of the three disagreeing features' deltas.
All three sign flips therefore fall on features the fitted model barely uses, which points to collinearity with the retained delinquency and payment measures rather than to a reversal the model depends on.
The remaining retained features agree with their own direction, including the most recent delinquency at 1 [[art:a8ba9372:sign_check.delinq_last.agrees]] and utilisation at 1 [[art:d0c9a130:sign_check.utilisation.agrees]], so the inputs carrying the weight are the ones whose direction is uncontested.

### What the model actually leans on

Refitting the champion's functional form on every retained feature reproduces a test AUC of 0.748 [[art:3a44e438:ablation.baseline_auc]], and each ablation delta is measured from that level.
Removing the most recent delinquency status costs the most, at -0.07585 [[art:3150b111:ablation.delinq_last.delta_auc]], followed by utilisation at -0.01977 [[art:d4ad2039:ablation.utilisation.delta_auc]] and the six-month mean bill at -0.0016 [[art:3b91a889:ablation.bill_mean_6m.delta_auc]].
Those are the inputs actually carrying discrimination, and each of them has a coefficient sign that agrees with its own univariate direction.
Every other retained feature has a non-negative delta: the six-month payment-ratio mean at 0.006603 [[art:90fa1178:ablation.pay_ratio_mean_6m.delta_auc]], the bill trend at 0.003279 [[art:096d7f98:ablation.bill_trend_6m.delta_auc]], the delinquency count at 0.0006812 [[art:c5659def:ablation.delinq_count_6m.delta_auc]], and age at 8.675e-05 [[art:59398b1b:ablation.age.delta_auc]].
A model whose discrimination rests on so narrow a base is legible, but it is also one whose conceptual case stands or falls with the delinquency and utilisation measures rather than with the breadth of the retained set.

### Effective challenge

A hist_gradient_boosting challenger was fitted on the same retained inputs and reaches a test AUC of 0.824 [[art:bf5be719:challenger.auc]] against the champion's 0.748 [[art:5c6c2bfc:metrics.test.auc]].
The challenger's lead on discrimination is 0.07598 [[art:c9e502ae:challenger.delta_auc]], read against a declared effective-challenge threshold of 0.03 [[art:e042774c:threshold.E1.delta_auc]], and the lead is above that threshold.
On calibration error the same ordering holds: the challenger's Brier score on test is 0.1258 [[art:f9e0583d:challenger.brier]], below the champion's 0.1489 [[art:bbe69430:metrics.test.brier]], so the comparison is not one where a discrimination gain is bought back by worse probability accuracy.
This comparison holds the inputs fixed and varies only the functional form, so the gap is evidence about the champion's functional form and not about its data or its feature timing: a linear score in the log-odds is leaving structure on the table that a tree ensemble recovers.
That is the substance of E1, raised here as a finding at low suggested severity, and the findings section reports it; a reader assessing whether the champion's form should be retained, extended with interactions or non-linear terms, or replaced should follow it there.
Nothing else in this section is a finding: the sign disagreements and the ablation deltas above are developmental evidence weighed in this judgement, and no rule is read against them.

### Judgement

The design is sound on the points that most often break a credit model of this kind: the inputs are all knowable before the performance period opens, the collinearity screen removed the inflated billing measures and documented the threshold it used, and the coefficients carrying the discrimination have the signs the subject matter expects.
The weaknesses are that discrimination rests on a narrow set of delinquency and utilisation inputs, that three fitted signs contradict their own univariate direction on features the model barely uses, and that the challenger's lead over the champion is above the declared effective-challenge threshold.
On the developmental evidence available to this section, the champion's conceptual design is defensible for its stated use, but the choice of functional form is the open question, and it is the finding above that carries it.

## 3. Data integrity and drift

Sound development practice includes a critical assessment of data quality, relevance, and inputs, and this section reviews the data the package was trained and tested on against the thresholds the package declares [[reg:SR26-2:IV.1]].

### Missingness

The training split holds 3500 rows [[art:2510d49d:profile.train.n]] and the test split holds 1500 rows [[art:2193cf5f:profile.test.n]].
The largest missing fraction of any column in the training split is 0 [[art:050a3099:profile.train.missing.max]].
The largest missing fraction of any column in the test split is 0 [[art:f813848d:profile.test.missing.max]].
The two splits stand at the same value on this measure, so the gap between them sits below the bound of 0.1 [[art:9cce25ea:threshold.D1.missing_gap]] that the rule places on the difference in missingness across splits.
No column in either split carries enough absent values for an imputation choice to drive the comparison between the splits.

### Population and characteristic stability

The largest train-to-test population stability index, the score included among the quantities screened, is 0.01095 [[art:381b2570:psi.max]], which is far below the declared bound of 0.25 [[art:278b9016:threshold.S1.psi]].
That bound agrees with the value carried in the package declaration, 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
The per-feature values between train and test are as follows.

- age: 0.008124 [[art:f9255a0a:psi.age]]
- bill_mean_6m: 0.007124 [[art:028e4281:psi.bill_mean_6m]]
- bill_trend_6m: 0.00958 [[art:c247a6f2:psi.bill_trend_6m]]
- delinq_count_6m: 0.002069 [[art:61491d02:psi.delinq_count_6m]]
- delinq_last: 0.00285 [[art:03bd52e7:psi.delinq_last]]
- delinq_max_6m: 0.005498 [[art:7a82e7f3:psi.delinq_max_6m]]
- limit_bal: 0.01095 [[art:601cdba2:psi.limit_bal]]
- pay_ratio_last: 0.004966 [[art:3af2ca29:psi.pay_ratio_last]]
- pay_ratio_mean_6m: 0.0055 [[art:2c5baeb2:psi.pay_ratio_mean_6m]]
- utilisation: 0.004244 [[art:451e0780:psi.utilisation]]
- score: 0.007023 [[art:a2885abf:psi.y_score]]

The credit limit is the feature that sets the maximum, at 0.01095 [[art:601cdba2:psi.limit_bal]], and every other feature sits below it, so the whole set is well inside the declared bound of 0.25 [[art:278b9016:threshold.S1.psi]].
The shift in the score itself, at 0.007023 [[art:a2885abf:psi.y_score]], is smaller than the largest feature shift, which is consistent with a score whose inputs have not moved between the splits.

The characteristic stability indices measure each feature's contribution to the shift in the linear predictor rather than the shift in its own marginal distribution, and the largest of them is 0.02363 [[art:e56cb179:csi.max]].
That maximum is carried by the most recent delinquency indicator, at 0.02363 [[art:5babe364:csi.delinq_last]], and it too sits below the declared stability bound of 0.25 [[art:278b9016:threshold.S1.psi]].
The remaining contributions are as follows.

- age: 0.0009476 [[art:a78e58f6:csi.age]]
- bill_mean_6m: 0.002369 [[art:48df6cc9:csi.bill_mean_6m]]
- bill_trend_6m: 0.00633 [[art:59948e6d:csi.bill_trend_6m]]
- delinq_count_6m: 0.002449 [[art:69346f52:csi.delinq_count_6m]]
- delinq_max_6m: 0.0008965 [[art:7244960d:csi.delinq_max_6m]]
- limit_bal: 0.001211 [[art:5b77b34b:csi.limit_bal]]
- pay_ratio_last: 0.001924 [[art:aff2b4bf:csi.pay_ratio_last]]
- pay_ratio_mean_6m: 0.001768 [[art:f567818e:csi.pay_ratio_mean_6m]]
- utilisation: 0.004042 [[art:10f0f9e7:csi.utilisation]]

The ordering of the two families differs: the credit limit leads on the marginal shift while the most recent delinquency indicator leads on the contribution to the predictor, and the delinquency indicator's marginal shift of 0.00285 [[art:03bd52e7:psi.delinq_last]] is smaller than its contribution of 0.02363 [[art:5babe364:csi.delinq_last]].
A modest marginal move on a heavily weighted feature can therefore matter more to the score than a larger marginal move elsewhere, and this is the pattern to watch in ongoing monitoring even though both quantities are well inside the bound here.

### Leakage screens

The count of features declared as observed during the performance period or after the outcome is 0 [[art:742bcd24:leakage.timing.n_flagged]], so the declared timings place every input before the outcome window.
The strongest single feature reaches an AUC of 0.6831 [[art:fd829fc4:leakage.target_corr.max_single_feature_auc]] on its own, below the bound of 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]] that would suggest one input reproduces the target.
That figure is high enough to show the feature set carries genuine signal and far enough from the bound to leave no single input under suspicion of standing in for the outcome.

The contamination screen has two arms, and each is read against its own bound rather than against the other arm.
The share of test rows whose identifiers also identify a row of the training split is 0 [[art:63d37fc5:leakage.overlap.ids]], against the declared bound of 0.005 [[art:9f336eaf:threshold.L2.overlap]].
The share of test rows whose feature values also appear in the training split is 0 [[art:0fec8048:leakage.overlap.features]], and the bound that arm applied is 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]], being the larger of the declared bound and a multiple of the in-train duplicate share, since two different subjects writing the same discrete row is coincidence rather than contamination.
The share of training rows whose feature values are not unique within the training split is 0 [[art:4474c227:leakage.duplicates.train]], so the applied bound for the feature arm coincides with the declared bound of 0.005 [[art:9f336eaf:threshold.L2.overlap]] and the relaxation it allows was not exercised.
The overlap of test rows with the training split on feature values is likewise 0 [[art:4c9fcd09:leakage.overlap]], read against the applied bound of 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].
Both arms therefore clear the bound each was read against, and because they stand at the same value no comparison between the arms themselves separates one from the other.

The number of feature names matching the target-adjacent lexicon is 0 [[art:407e62be:leakage.name_screen.n_matched]], so nothing in the naming suggests an input built from the outcome.
The name screen is a lexical check and does not detect a leaking feature under an innocuous name, so it supports the timing declarations and the single-feature discrimination screen rather than substituting for them.

### Assessment

On the evidence assembled here the splits are complete, the train-to-test distributions are stable on both the marginal and the predictor-contribution views, and none of the leakage screens reaches the bound it was read against.
The stability evidence covers the training split against the test split, and the guidance's expectation of out-of-time testing means these results speak to the data as partitioned rather than to how the population will move after deployment [[reg:SR26-2:IV.1]].

## 4. Outcomes analysis

Outcomes analysis here compares the model's recomputed outputs with the realised outcomes on the development and holdout splits, in the sense of [[reg:SR26-2:V.1.b]].

This section reports discrimination first and calibration after it, because the observed event rate on the evaluation split, 0.2247 [[art:9209d200:metrics.test.event_rate]], is at or above 0.05 [[art:42f1351e:rule.calibration_first_event_rate]], the rate below which this report would lead with calibration instead.

The recomputed metrics on each split are as follows, one row per metric.

| Metric | Train | Test |
| --- | --- | --- |
| Rows | 3500 [[art:564683ee:metrics.train.n]] | 1500 [[art:64fcf14d:metrics.test.n]] |
| Observed event rate | 0.2246 [[art:133a5ff8:metrics.train.event_rate]] | 0.2247 [[art:9209d200:metrics.test.event_rate]] |
| Mean predicted probability | 0.2246 [[art:605cce58:metrics.train.mean_predicted]] | 0.2211 [[art:4d2f8a37:metrics.test.mean_predicted]] |
| AUC | 0.7584 [[art:14b38a2b:metrics.train.auc]] | 0.748 [[art:5c6c2bfc:metrics.test.auc]] |
| Gini | 0.5169 [[art:b4da846e:metrics.train.gini]] | 0.496 [[art:8e5918d8:metrics.test.gini]] |
| KS | 0.4451 [[art:ccc12729:metrics.train.ks]] | 0.4183 [[art:90751047:metrics.test.ks]] |
| Brier | 0.1489 [[art:be669a99:metrics.train.brier]] | 0.1489 [[art:bbe69430:metrics.test.brier]] |
| Log loss | 0.465 [[art:4f02e465:metrics.train.logloss]] | 0.4673 [[art:dda8da69:metrics.test.logloss]] |

Rank-ordering is weaker on the holdout than in sample: AUC is 0.7584 [[art:14b38a2b:metrics.train.auc]] on train against 0.748 [[art:5c6c2bfc:metrics.test.auc]] on test, and the same direction holds for Gini and KS.
The train-to-test movement in AUC was read against a bound of 0.08 [[art:630f28f4:threshold.O1.auc_gap]], and the separation between the two split values stays inside that bound, so the holdout shortfall is a level effect rather than an overfitting effect.
The top two deciles of predicted probability capture 0.4718 [[art:d4a1cf7d:deciles.test.top2_capture]] of test events, above the 0.4517 [[art:1d20c762:deciles.train.top2_capture]] they capture on train.

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

Turning to calibration, the logistic regression of the outcome on the logit of the predicted probability has a slope of 1.003 [[art:b7dbb687:calibration_slope.test]] on test and 1.002 [[art:d02e3091:calibration_slope.train]] on train.
Both slopes sit inside the declared band, whose bottom is 0.8 [[art:749634ae:threshold.C1.calibration_slope.min]] and whose top is 1.2 [[art:b6672579:threshold.C1.calibration_slope.max]].
The intercept of that regression is 0.02729 [[art:b69c6b52:calibration_intercept.test]] on test and 0.002062 [[art:ed381a81:calibration_intercept.train]] on train.
Mean predicted probability on test is 0.2211 [[art:4d2f8a37:metrics.test.mean_predicted]] against an observed event rate of 0.2247 [[art:9209d200:metrics.test.event_rate]], the predicted level sitting just below the observed one.
Expressed relative to the observed rate, that discrepancy is 0.01585 [[art:d8ffb3d0:calibration.mean_rel_gap.test]] on test and 0.0002283 [[art:53738d45:calibration.mean_rel_gap.train]] on train, the test value being the larger of the two and both below the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].

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

The bounds the developer declared in the package manifest, each with the value recomputed here and the outcome of the comparison, are set out below.

<!-- quaestor:renderer:begin table thresholds.evaluation -->
Every threshold package.yaml declares, with its bound, the recomputed value and the outcome [[art:f67e8fcc:thresholds.evaluation]]:

| metric | split | bound | value | result |
|---|---|---|---|---|
| auc | test | minimum 0.78 | 0.748 | fail |
| brier | test | maximum 0.2 | 0.1489 | pass |
| calibration_slope | test | minimum 0.8 | 1.003 | pass |
| calibration_slope | test | maximum 1.2 | 1.003 | pass |
| psi |  | maximum 0.25 | 0.01095 | pass |
<!-- quaestor:renderer:end -->

The table records the recomputed test AUC of 0.748 [[art:5c6c2bfc:metrics.test.auc]] falling below the declared minimum of 0.78 [[art:5487ddda:threshold.package.auc.test.min]], and that shortfall is the finding this section raises.
The remaining declared bounds, on Brier, on the calibration slope and on population stability, are met by the recomputed values shown in the same table.

### Follow-up analyses

The first follow-up asked for every metric on the test split restricted to `delinq_last > median(delinq_last)`.
It was run to check whether the champion's sub-threshold test AUC, and the challenger's AUC lead over it, are concentrated in the recently delinquent segment, where a linear model is most likely to misfit.

<!-- quaestor:renderer:begin table metrics.test.sub.delinq_last_high -->
Every metric on the delinq_last above_median slice of test [[art:6ae225dc:metrics.test.sub.delinq_last_high]]:

| metric | value |
|---|---|
| n | 339 |
| event_rate | 0.5103 |
| auc | 0.5859 |
| gini | 0.1718 |
| ks | 0.1545 |
| brier | 0.2545 |
| logloss | 0.71 |
| mean_predicted | 0.4664 |
| mean_rel_gap | 0.08613 |
| share | 0.226 |
<!-- quaestor:renderer:end -->

AUC on this slice is 0.5859 [[art:43fc7536:metrics.test.sub.delinq_last_high.auc]], falling 0.1621 [[art:5886871a:metrics.test.sub.delinq_last_high.auc_gap]] below the split's own AUC, above the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] at which a sub-population result is carried as an open item.
The slice holds 0.226 [[art:e795e8a9:metrics.test.sub.delinq_last_high.share]] of the split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] a sub-population must hold and below the 0.95 [[art:a928a05c:threshold.O1.slice_max_share]] at which it would be refused as the whole split.
Mean predicted on the slice is 0.4664 [[art:360fa59b:metrics.test.sub.delinq_last_high.mean_predicted]] against an observed rate of 0.5103 [[art:c9cb7610:metrics.test.sub.delinq_last_high.event_rate]], a relative discrepancy of 0.08613 [[art:1a238a3e:metrics.test.sub.delinq_last_high.mean_rel_gap]] that stays below the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]], so the weakness on this segment is in the ordering of the probabilities rather than in their level.
This result is not among the findings this section raises; it is left to the findings section as an open item and a question for the model developer.

The second follow-up asked for every metric on the test split restricted to `delinq_last <= median(delinq_last)`.
It was run as the complementary half of the same partition, to show whether the holdout AUC shortfall and the challenger's lead are concentrated in the delinquent tail or hold across the whole split.

<!-- quaestor:renderer:begin table metrics.test.sub.delinq_last_low -->
Every metric on the delinq_last below_median slice of test [[art:64a1c670:metrics.test.sub.delinq_last_low]]:

| metric | value |
|---|---|
| n | 1161 |
| event_rate | 0.1413 |
| auc | 0.6333 |
| gini | 0.2665 |
| ks | 0.2508 |
| brier | 0.118 |
| logloss | 0.3964 |
| mean_predicted | 0.1495 |
| mean_rel_gap | 0.05828 |
| share | 0.774 |
<!-- quaestor:renderer:end -->

AUC on this slice is 0.6333 [[art:0a7e2c66:metrics.test.sub.delinq_last_low.auc]], falling 0.1147 [[art:b25b1c4c:metrics.test.sub.delinq_last_low.auc_gap]] below the split's own AUC, again above the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]], so the shortfall is not confined to the delinquent tail.
The slice holds 0.774 [[art:cd49d716:metrics.test.sub.delinq_last_low.share]] of the split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] and below the 0.95 [[art:a928a05c:threshold.O1.slice_max_share]] ceiling.
Mean predicted here is 0.1495 [[art:77d4b87f:metrics.test.sub.delinq_last_low.mean_predicted]] against an observed rate of 0.1413 [[art:2fb6f9a6:metrics.test.sub.delinq_last_low.event_rate]], a relative discrepancy of 0.05828 [[art:7d8102b1:metrics.test.sub.delinq_last_low.mean_rel_gap]] and below the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]], the level again being broadly right while the ordering is not.
Comparing the two halves of this partition on the relative discrepancy between predicted and observed, the delinquent half is the further from its observed rate; on the AUC shortfall against the split, the delinquent half is also the larger, and this result likewise belongs with the open items rather than with the findings.

The third follow-up asked for every metric on the test split restricted to `utilisation > median(utilisation)`.
It was run to check whether the AUC shortfall and the challenger's lead concentrate in high-utilisation accounts, an axis the delinquency slices did not cover.

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

AUC on this slice is 0.5689 [[art:13b21546:metrics.test.sub.utilisation_high.auc]], falling 0.1791 [[art:e0dc4aa9:metrics.test.sub.utilisation_high.auc_gap]] below the split's own AUC, the largest of the three slice shortfalls and above the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].
The slice holds 0.5 [[art:9404484e:metrics.test.sub.utilisation_high.share]] of the split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] and below the 0.95 [[art:a928a05c:threshold.O1.slice_max_share]] ceiling.
Mean predicted here is 0.2286 [[art:2d88d7b5:metrics.test.sub.utilisation_high.mean_predicted]] against an observed rate of 0.2333 [[art:8e66209c:metrics.test.sub.utilisation_high.event_rate]], a relative discrepancy of 0.02024 [[art:e33a14d6:metrics.test.sub.utilisation_high.mean_rel_gap]] and the smallest of the three slices on that measure, well below the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
On this segment the average level of the probabilities tracks the observed rate closely while the ranking within the segment is weak, and this result too is left to the findings section as an open item rather than reported here as a finding.

## 5. Sensitivity and scenario analysis

Sensitivity evidence is presented here as part of the critical analysis of the model's design choices and the developmental evidence supporting them [[reg:SR26-2:V.1.a]].
The superseded guidance states the purpose of that work more specifically, asking that sensitivity analysis check how small changes in inputs and parameter values move model outputs, and that stress testing probe extreme values to establish where a model becomes unstable [[reg:SR11-7:V.1.a]].

### 5.1 Multicollinearity among the retained features

The largest variance inflation factor over the retained features is 7.295 [[art:9ae7c45b:vif.max]], which sits below the declared ceiling of 10 [[art:aeb4f33c:threshold.M1.vif]].
That maximum belongs to the six-month mean bill feature, at 7.295 [[art:f0a2f865:vif.bill_mean_6m]].
The two payment-ratio features sit just beneath it, at 7.264 [[art:c2de8dfe:vif.pay_ratio_last]] for the last-period ratio and 7.259 [[art:e39c3e82:vif.pay_ratio_mean_6m]] for its six-month mean, so the upper end of the distribution is formed by the balance and payment-ratio block rather than by any single isolated feature.
The credit limit follows at 4.803 [[art:ddfdcc3c:vif.limit_bal]] and utilisation at 3.215 [[art:536fdb6f:vif.utilisation]].
The delinquency features are lower still, at 2.561 [[art:38974def:vif.delinq_count_6m]] for the six-month count, 2.408 [[art:71aaaf11:vif.delinq_max_6m]] for the six-month maximum and 1.412 [[art:48733638:vif.delinq_last]] for the last-period indicator.
The bill trend is at 1.201 [[art:9356a256:vif.bill_trend_6m]] and age at 1.002 [[art:74c06cad:vif.age]], the latter being the closest of the retained features to the no-collinearity floor.
Every one of these factors is below the declared ceiling of 10 [[art:aeb4f33c:threshold.M1.vif]], and the largest of them is further from that ceiling than it is from the factors of the two payment-ratio features.

Belsley's condition number of the column-standardised design is 5.547 [[art:e41b9562:condition_number]], below the declared limit of 30 [[art:7e52fd7a:threshold.M1.condition_number]].
The two diagnostics therefore point the same way: the retained design shows correlated but not degenerate columns, with the shared variance concentrated in the balance and payment-ratio block, and the coefficient estimates on those features should be read as less sharply identified than those on the delinquency, trend and age features.

### 5.2 Procedures that do not apply to this model type

Appendix D lists the sensitivity procedures that are out of scope for a model package of this type, and they were not run for this submission.
The rate-shock scenario suite belongs to hazard models, and the subject of this report is not one, so no value change at an extreme shock, no judgement on whether a shock curve is monotone, and no comparison of curve convexity against a declared direction is reported here or implied by anything above.
The regime-partitioned stability comparison likewise depends on a declared regime column for this package, and no regime-to-regime comparison of model behaviour appears in this section.
Readers should treat the multicollinearity diagnostics above as the whole of the sensitivity evidence carried in this section, and should not read the absence of shock or regime results as a negative result on either.

### 5.3 Disposition

No finding was raised against the sensitivity evidence in this section.

## 6. Findings and recommendations

Findings are ordered by severity and each carries the recomputed quantity, the declared bound it was read against, and the artifact citation for both, so that limitations and any warranted corrective action are stated with the evidence attached [[reg:SR26-2:V]].

### F-001 · T1 declared threshold · severity **high**

**The model's discrimination on the test split falls below the minimum the package itself declares.**
The package declares a minimum AUC on test of 0.78 [[art:5487ddda:threshold.package.auc.test.min]].
This validation's own recomputation of AUC on the test split returns 0.748 [[art:5c6c2bfc:metrics.test.auc]], which is below that declared minimum.
The validator concludes that the model does not meet the performance bound its own package sets for it, and that this is a deficiency in the model as submitted rather than in the way it is reported.
The model developer should either retrain or recalibrate until the recomputed test AUC clears the declared minimum, or revise the declared minimum with a documented justification tied to intended use and resubmit the package for validation.

### F-002 · E1 effective challenge · severity **low**

**A simple challenger model outperforms the champion by a margin wider than the effective-challenge threshold, which indicates the champion's specification has not been adequately challenged.**
A gradient-boosting challenger reaches an AUC on test of 0.824 [[art:bf5be719:challenger.auc]] against the champion's 0.748 [[art:5c6c2bfc:metrics.test.auc]].
The challenger's lead over the champion is 0.07598 [[art:c9e502ae:challenger.delta_auc]], which is above the effective-challenge threshold of 0.03 [[art:e042774c:threshold.E1.delta_auc]].
The validator concludes that available alternative specifications extract signal the champion does not, so the choice of the incumbent form is not supported by the evidence in the package.
The model developer should document why the champion form was retained in the face of the stronger alternative, or adopt a specification that closes the lead, and record the comparison in the development evidence [[reg:SR26-2:VI.3]].

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1, S1), `compute_metrics` (C1, O1), `check_leakage` (L1, L2), `check_collinearity` (M1).

### Open items

On the segment `delinq_last > median(delinq_last)`, which holds 0.226 [[art:e795e8a9:metrics.test.sub.delinq_last_high.share]] of the test split and so sits at or above the share bound of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]], AUC is 0.5859 [[art:43fc7536:metrics.test.sub.delinq_last_high.auc]] against 0.748 [[art:5c6c2bfc:metrics.test.auc]] on the whole split, a shortfall of 0.1621 [[art:5886871a:metrics.test.sub.delinq_last_high.auc_gap]] read against the gap bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] — can the model developer say what the model still discriminates on once delinquency history is held high and near-constant, and whether ranking within that segment is relied on in use?
On the segment `delinq_last <= median(delinq_last)`, which holds 0.774 [[art:cd49d716:metrics.test.sub.delinq_last_low.share]] of the test split and so sits at or above the share bound of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]], AUC is 0.6333 [[art:0a7e2c66:metrics.test.sub.delinq_last_low.auc]] against 0.748 [[art:5c6c2bfc:metrics.test.auc]] on the whole split, a shortfall of 0.1147 [[art:b25b1c4c:metrics.test.sub.delinq_last_low.auc_gap]] read against the gap bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] — comparing absolute shortfalls rather than their ratio, this one is the smaller of the pair on the delinquency split while resting on the larger share, so can the model developer account for how much of the split-level ranking comes from the contrast between the segments rather than from ordering inside either?
On the segment `utilisation > median(utilisation)`, which holds 0.5 [[art:9404484e:metrics.test.sub.utilisation_high.share]] of the test split and so sits at or above the share bound of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]], AUC is 0.5689 [[art:13b21546:metrics.test.sub.utilisation_high.auc]] against 0.748 [[art:5c6c2bfc:metrics.test.auc]] on the whole split, an absolute shortfall of 0.1791 [[art:e0dc4aa9:metrics.test.sub.utilisation_high.auc_gap]] read against the gap bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] — can the model developer say which drivers carry the ranking among high-utilisation borrowers, where utilisation and whatever moves with it are held to one side of the median?
The fitted coefficient on `delinq_max_6m` carries sign -1 [[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]] where that feature's own univariate direction is 1 [[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]], an agreement indicator of 0 [[art:c946359c:sign_check.delinq_max_6m.agrees]] when read against that univariate direction — can the model developer explain what the fitted sign means once the correlated features in the specification are conditioned on, and confirm the direction is intended?
The fitted coefficient on `limit_bal` carries sign 1 [[art:6af6aef2:sign_check.limit_bal.coef_sign]] where that feature's own univariate direction is -1 [[art:56d284d6:sign_check.limit_bal.univariate_direction]], an agreement indicator of 0 [[art:0278aad1:sign_check.limit_bal.agrees]] when read against that univariate direction — can the model developer explain the conditional interpretation of that sign and confirm it is intended rather than an artefact of collinearity among the credit-capacity features?
The fitted coefficient on `pay_ratio_last` carries sign 1 [[art:f018263e:sign_check.pay_ratio_last.coef_sign]] where that feature's own univariate direction is -1 [[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]], an agreement indicator of 0 [[art:79abee77:sign_check.pay_ratio_last.agrees]] when read against that univariate direction — can the model developer explain what this feature contributes once repayment and balance terms are held fixed, and confirm the direction is intended?

## 7. Ongoing monitoring recommendations

Ongoing monitoring evaluates the extent to which this model continues to perform as expected given potential changes in products, exposures, activities, clients, data relevance, or market conditions, and the plan below is scoped to that purpose [[reg:SR26-2:V.2]].

### Quantities, bounds and cadence

No new bounds are proposed here: the thresholds below are the ones the package declares and the ones the checks in this report were run against.

Rank-ordering should be recomputed on each production cohort and read against the declared floor of 0.78 [[art:5487ddda:threshold.package.auc.test.min]], with the value recomputed on the evaluation split, 0.748 [[art:5c6c2bfc:metrics.test.auc]], as the starting point; that starting point sits below the declared floor, which is why this quantity warrants the tightest cadence of the set.

Recompute it as soon as each cohort's performance window closes and its outcomes mature, rather than deferring it to the scheduled revalidation.

Probability accuracy should be recomputed on the same cadence and read against the declared ceiling of 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]], with the value recomputed on the evaluation split, 0.1489 [[art:bbe69430:metrics.test.brier]], sitting below that ceiling.

The slope of the outcome regressed on the logit of the predicted probability should be recomputed on the same cadence and read against the declared band from 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] to 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]], with the value recomputed on the evaluation split, 1.003 [[art:b7dbb687:calibration_slope.test]], inside that band and above its lower edge.

Population and score stability should be read against the declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]], with the largest train-to-test shift measured in this validation, 0.01095 [[art:381b2570:psi.max]], far below that ceiling.

Stability needs only the scored population and not realized outcomes, so it can be refreshed on every scoring run and serves as the early-warning quantity in the interval before a cohort's outcomes mature.

When comparing a shift across two populations, state whether the comparison is the difference between the two shift values or their ratio, and report the one named rather than letting a small absolute movement stand in for a large relative one.

Section 4 of this report reported discrimination before calibration because the observed event rate on the evaluation split is at or above 0.05 [[art:42f1351e:rule.calibration_first_event_rate]]; a monitoring report covering a future cohort whose event rate falls below that bound should lead with calibration instead.

Persistent deviation outside these declared bounds, rather than a single cohort's excursion, is the signal that warrants considering model adjustment, recalibration, or redevelopment [[reg:SR26-2:V.1.b]].

### Benchmarking that monitoring adds

Section 2 of this report compares the champion with a challenger, but that comparison is bounded by the development data both were fitted and scored on.

What monitoring adds is the benchmark that data cannot give: the challenger refitted on production vintages and scored on the same matured cohorts as the champion, so that the ranking between the two is re-established on data neither was fitted on.

That refit and comparison should be repeated each time a monitoring cohort's outcomes mature, and a reversal of the ranking should trigger investigation of the sources and degree of the difference before it triggers replacement [[reg:SR11-7:V.1.b]].

### What this validation could not cover

This validation observed the model on fixed development and evaluation splits, so it cannot speak to how the scored population moves once the model is in production use; the stability quantity above is the standing proxy monitoring should watch for that.

It also cannot speak to override behaviour, which arises only in use, so monitoring should track the rate of overrides, document the reasons, and analyse whether the override process consistently improves on model output [[reg:SR11-7:V.1.b]].

Implementation and data-feed integrity — that the production scoring path consumes the same inputs, in the same encoding and with the same treatment of missing values, as the pipeline evaluated here — is a process-verification question that monitoring should re-verify on a recurring basis and after any change to upstream systems [[reg:SR11-7:V.1.b]].

Stability of performance within the sub-populations the model is used on cannot be established from a single split over time, so monitoring should recompute the discrimination and calibration quantities above within those sub-populations, against the same declared bounds cited above.

Finally, the model's behaviour under market or macroeconomic conditions outside the range represented in the development sample is outside what this validation could observe; monitoring should identify cohorts where those input ranges are approached or exceeded and treat results from them with correspondingly greater caution [[reg:SR26-2:V]].

## Appendix A — Claims

Grounding precision 1.0000 before repair (228 of 228 claims verified) and 1.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 10/10; conceptual_soundness 46/46; data_integrity 48/48; outcomes 66/66; sensitivity 15/15; findings 33/33; monitoring 10/10.

Developer claims: The package declares 2 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). See Appendix D.

Excluded numeric tokens (not claims): section_number (5.1, 5.2, 5.3, Section 4); citation_hash (2ad8d1a5, 2510d49d, 2193cf5f, bbe69430); regulatory_section_id (SR26-2:V, SR26-2:V.1.a, SR26-2:IV.1, SR26-2:V.1.b); finding_id (F-001, F-002); package_version (1.0); extractor_returned_excluded_token (1.0, 001,, 002,, 6.0).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The subject was executed by the validation harness under the… | 300 | count | runtime.max_seconds |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 2 | summary | The development split holds 3500 rows and the held-out test… | 3500 | count | n | train | eq | `[[art:2510d49d:profile.train.n]]` | verified | 3500 |
| 3 | summary | The development split holds 3500 rows and the held-out test… | 1500 | count | n | test | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 4 | summary | Of the developer-declared thresholds, the model passes the B… | 0.1489 | ratio | brier | test | eq | `[[art:bbe69430:metrics.test.brier]]` | verified | 0.148850901 |
| 5 | summary | Of the developer-declared thresholds, the model passes the B… | 0.2 | ratio | brier | test | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 6 | summary | It passes the calibration slope bounds: the slope on test is… | 1.003 | ratio | calibration_slope | test | eq | `[[art:b7dbb687:calibration_slope.test]]` | verified | 1.002737656 |
| 7 | summary | It passes the calibration slope bounds: the slope on test is… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 8 | summary | It passes the calibration slope bounds: the slope on test is… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 9 | summary | It passes the population stability bound: the largest train-… | 0.01095 | ratio | psi |  | eq | `[[art:381b2570:psi.max]]` | verified | 0.01095273358 |
| 10 | summary | It passes the population stability bound: the largest train-… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 11 | conceptual_soundness | The champion is a single linear score in the log-odds, with… | -1.396 | ratio | intercept |  | eq | `[[art:74c10f15:run.model_summary#intercept]]` | verified | -1.395828048 |
| 12 | conceptual_soundness | The champion is a single linear score in the log-odds, with… | 3500 | count | n_train | train | eq | `[[art:74c10f15:run.model_summary#n_train]]` | verified | 3500 |
| 13 | conceptual_soundness | The feature inventory holds 12 features. | 12 | count | n |  | eq | `[[art:abbb748e:run.features#n]]` | verified | 12 |
| 14 | conceptual_soundness | Of these, 2 are known at origination and 10 are known before… | 2 | count | at_origination |  | eq | `[[art:abbb748e:run.features#at_origination]]` | verified | 2 |
| 15 | conceptual_soundness | Of these, 2 are known at origination and 10 are known before… | 10 | count | before_period_start |  | eq | `[[art:abbb748e:run.features#before_period_start]]` | verified | 10 |
| 16 | conceptual_soundness | No input is drawn from inside the performance period, 0 , an… | 0 | count | during_period |  | eq | `[[art:abbb748e:run.features#during_period]]` | verified | 0 |
| 17 | conceptual_soundness | No input is drawn from inside the performance period, 0 , an… | 0 | count | after_outcome |  | eq | `[[art:abbb748e:run.features#after_outcome]]` | verified | 0 |
| 18 | conceptual_soundness | The developer's own collinearity screen removed bill_last, w… | 160.9 | ratio | vif |  | eq | `[[art:74c10f15:run.model_summary#removed.bill_last.vif]]` | verified | 160.888514 |
| 19 | conceptual_soundness | The developer's own collinearity screen removed bill_last, w… | 36.36 | ratio | vif |  | eq | `[[art:74c10f15:run.model_summary#removed.utilisation_mean_6m.vif]]` | verified | 36.356335 |
| 20 | conceptual_soundness | The developer's own collinearity screen removed bill_last, w… | 10 | ratio | vif_threshold |  | eq | `[[art:74c10f15:run.model_summary#vif_threshold]]` | verified | 10 |
| 21 | conceptual_soundness | The largest coefficient in the retained form sits on the mos… | 0.7334 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.delinq_last.value]]` | verified | 0.7334219534 |
| 22 | conceptual_soundness | The next largest are the six-month mean bill at -0.3726 , th… | -0.3726 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.bill_mean_6m.value]]` | verified | -0.3726281079 |
| 23 | conceptual_soundness | The next largest are the six-month mean bill at -0.3726 , th… | -0.3554 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.pay_ratio_mean_6m.value]]` | verified | -0.3553721566 |
| 24 | conceptual_soundness | The next largest are the six-month mean bill at -0.3726 , th… | 0.2662 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.utilisation.value]]` | verified | 0.2662083574 |
| 25 | conceptual_soundness | The next largest are the six-month mean bill at -0.3726 , th… | -0.2225 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.bill_trend_6m.value]]` | verified | -0.2224749257 |
| 26 | conceptual_soundness | The smaller coefficients are the six-month delinquency count… | 0.1226 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.delinq_count_6m.value]]` | verified | 0.1225797828 |
| 27 | conceptual_soundness | The smaller coefficients are the six-month delinquency count… | 0.1026 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.pay_ratio_last.value]]` | verified | 0.1025909773 |
| 28 | conceptual_soundness | The smaller coefficients are the six-month delinquency count… | 0.07266 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.limit_bal.value]]` | verified | 0.07265585996 |
| 29 | conceptual_soundness | The smaller coefficients are the six-month delinquency count… | -0.06726 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.age.value]]` | verified | -0.06725800744 |
| 30 | conceptual_soundness | The smaller coefficients are the six-month delinquency count… | -0.03221 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.delinq_max_6m.value]]` | verified | -0.03221440242 |
| 31 | conceptual_soundness | The fitted sign on each retained feature was compared with t… | 3 | count | n_disagreements |  | eq | `[[art:e223cd4a:sign_check.n_disagreements]]` | verified | 3 |
| 32 | conceptual_soundness | The credit limit is fitted positive, 1 , while on its own it… | 1 | ratio | coef_sign |  | eq | `[[art:6af6aef2:sign_check.limit_bal.coef_sign]]` | verified | 1 |
| 33 | conceptual_soundness | The credit limit is fitted positive, 1 , while on its own it… | -1 | ratio | univariate_direction |  | eq | `[[art:56d284d6:sign_check.limit_bal.univariate_direction]]` | verified | -1 |
| 34 | conceptual_soundness | The credit limit is fitted positive, 1 , while on its own it… | 0.0004286 | ratio | delta_auc | test | eq | `[[art:63faa640:ablation.limit_bal.delta_auc]]` | verified | 0.0004286468792 |
| 35 | conceptual_soundness | The most recent payment ratio is fitted positive, 1 , agains… | 1 | ratio | coef_sign |  | eq | `[[art:f018263e:sign_check.pay_ratio_last.coef_sign]]` | verified | 1 |
| 36 | conceptual_soundness | The most recent payment ratio is fitted positive, 1 , agains… | -1 | ratio | univariate_direction |  | eq | `[[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]]` | verified | -1 |
| 37 | conceptual_soundness | The most recent payment ratio is fitted positive, 1 , agains… | 0.002411 | ratio | delta_auc | test | eq | `[[art:5f39089e:ablation.pay_ratio_last.delta_auc]]` | verified | 0.002411138695 |
| 38 | conceptual_soundness | The six-month maximum delinquency is fitted negative, -1 , a… | -1 | ratio | coef_sign |  | eq | `[[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]]` | verified | -1 |
| 39 | conceptual_soundness | The six-month maximum delinquency is fitted negative, -1 , a… | 1 | ratio | univariate_direction |  | eq | `[[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]]` | verified | 1 |
| 40 | conceptual_soundness | The six-month maximum delinquency is fitted negative, -1 , a… | 0.0003598 | ratio | delta_auc | test | eq | `[[art:3a0d3a0c:ablation.delinq_max_6m.delta_auc]]` | verified | 0.0003597572022 |
| 41 | conceptual_soundness | The remaining retained features agree with their own directi… | 1 | ratio | agrees |  | eq | `[[art:a8ba9372:sign_check.delinq_last.agrees]]` | verified | 1 |
| 42 | conceptual_soundness | The remaining retained features agree with their own directi… | 1 | ratio | agrees |  | eq | `[[art:d0c9a130:sign_check.utilisation.agrees]]` | verified | 1 |
| 43 | conceptual_soundness | Refitting the champion's functional form on every retained f… | 0.748 | ratio | baseline_auc | test | eq | `[[art:3a44e438:ablation.baseline_auc]]` | verified | 0.7479888042 |
| 44 | conceptual_soundness | Removing the most recent delinquency status costs the most,… | -0.07585 | ratio | delta_auc | test | eq | `[[art:3150b111:ablation.delinq_last.delta_auc]]` | verified | -0.07585263733 |
| 45 | conceptual_soundness | Removing the most recent delinquency status costs the most,… | -0.01977 | ratio | delta_auc | test | eq | `[[art:d4ad2039:ablation.utilisation.delta_auc]]` | verified | -0.01976623436 |
| 46 | conceptual_soundness | Removing the most recent delinquency status costs the most,… | -0.0016 | ratio | delta_auc | test | eq | `[[art:3b91a889:ablation.bill_mean_6m.delta_auc]]` | verified | -0.001599771388 |
| 47 | conceptual_soundness | Every other retained feature has a non-negative delta: the s… | 0.006603 | ratio | delta_auc | test | eq | `[[art:90fa1178:ablation.pay_ratio_mean_6m.delta_auc]]` | verified | 0.006603203115 |
| 48 | conceptual_soundness | Every other retained feature has a non-negative delta: the s… | 0.003279 | ratio | delta_auc | test | eq | `[[art:096d7f98:ablation.bill_trend_6m.delta_auc]]` | verified | 0.003278638332 |
| 49 | conceptual_soundness | Every other retained feature has a non-negative delta: the s… | 0.0006812 | ratio | delta_auc | test | eq | `[[art:c5659def:ablation.delinq_count_6m.delta_auc]]` | verified | 0.0006812423615 |
| 50 | conceptual_soundness | Every other retained feature has a non-negative delta: the s… | 8.675e-05 | ratio | delta_auc | test | eq | `[[art:59398b1b:ablation.age.delta_auc]]` | verified | 8.674996364e-05 |
| 51 | conceptual_soundness | A hist_gradient_boosting challenger was fitted on the same r… | 0.824 | ratio | auc | test | eq | `[[art:bf5be719:challenger.auc]]` | verified | 0.823969015 |
| 52 | conceptual_soundness | A hist_gradient_boosting challenger was fitted on the same r… | 0.748 | ratio | auc | test | eq | `[[art:5c6c2bfc:metrics.test.auc]]` | verified | 0.7479888042 |
| 53 | conceptual_soundness | The challenger's lead on discrimination is 0.07598 , read ag… | 0.07598 | ratio | delta_auc | test | eq | `[[art:c9e502ae:challenger.delta_auc]]` | verified | 0.0759802108 |
| 54 | conceptual_soundness | The challenger's lead on discrimination is 0.07598 , read ag… | 0.03 | ratio | delta_auc |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 55 | conceptual_soundness | On calibration error the same ordering holds: the challenger… | 0.1258 | ratio | brier | test | eq | `[[art:f9e0583d:challenger.brier]]` | verified | 0.1258050391 |
| 56 | conceptual_soundness | On calibration error the same ordering holds: the challenger… | 0.1489 | ratio | brier | test | eq | `[[art:bbe69430:metrics.test.brier]]` | verified | 0.148850901 |
| 57 | data_integrity | The training split holds 3500 rows and the test split holds… | 3500 | count | n | train | eq | `[[art:2510d49d:profile.train.n]]` | verified | 3500 |
| 58 | data_integrity | The training split holds 3500 rows and the test split holds… | 1500 | count | n | test | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 59 | data_integrity | The largest missing fraction of any column in the training s… | 0 | ratio | missing | train | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 60 | data_integrity | The largest missing fraction of any column in the test split… | 0 | ratio | missing | test | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 61 | data_integrity | The two splits stand at the same value on this measure, so t… | 0.1 | ratio | missing_gap |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 62 | data_integrity | The largest train-to-test population stability index, the sc… | 0.01095 | ratio | psi |  | eq | `[[art:381b2570:psi.max]]` | verified | 0.01095273358 |
| 63 | data_integrity | The largest train-to-test population stability index, the sc… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 64 | data_integrity | That bound agrees with the value carried in the package decl… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 65 | data_integrity | - age: 0.008124 | 0.008124 | ratio | psi |  | eq | `[[art:f9255a0a:psi.age]]` | verified | 0.008124281436 |
| 66 | data_integrity | - bill_mean_6m: 0.007124 | 0.007124 | ratio | psi |  | eq | `[[art:028e4281:psi.bill_mean_6m]]` | verified | 0.007124196275 |
| 67 | data_integrity | - bill_trend_6m: 0.00958 | 0.00958 | ratio | psi |  | eq | `[[art:c247a6f2:psi.bill_trend_6m]]` | verified | 0.009579614525 |
| 68 | data_integrity | - delinq_count_6m: 0.002069 | 0.002069 | ratio | psi |  | eq | `[[art:61491d02:psi.delinq_count_6m]]` | verified | 0.002069275496 |
| 69 | data_integrity | - delinq_last: 0.00285 | 0.00285 | ratio | psi |  | eq | `[[art:03bd52e7:psi.delinq_last]]` | verified | 0.002849633848 |
| 70 | data_integrity | - delinq_max_6m: 0.005498 | 0.005498 | ratio | psi |  | eq | `[[art:7a82e7f3:psi.delinq_max_6m]]` | verified | 0.005498249408 |
| 71 | data_integrity | - limit_bal: 0.01095 | 0.01095 | ratio | psi |  | eq | `[[art:601cdba2:psi.limit_bal]]` | verified | 0.01095273358 |
| 72 | data_integrity | - pay_ratio_last: 0.004966 | 0.004966 | ratio | psi |  | eq | `[[art:3af2ca29:psi.pay_ratio_last]]` | verified | 0.00496591109 |
| 73 | data_integrity | - pay_ratio_mean_6m: 0.0055 | 0.0055 | ratio | psi |  | eq | `[[art:2c5baeb2:psi.pay_ratio_mean_6m]]` | verified | 0.005500252946 |
| 74 | data_integrity | - utilisation: 0.004244 | 0.004244 | ratio | psi |  | eq | `[[art:451e0780:psi.utilisation]]` | verified | 0.0042440485 |
| 75 | data_integrity | - score: 0.007023 | 0.007023 | ratio | psi |  | eq | `[[art:a2885abf:psi.y_score]]` | verified | 0.007023143302 |
| 76 | data_integrity | The credit limit is the feature that sets the maximum, at 0.… | 0.01095 | ratio | psi |  | eq | `[[art:601cdba2:psi.limit_bal]]` | verified | 0.01095273358 |
| 77 | data_integrity | The credit limit is the feature that sets the maximum, at 0.… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 78 | data_integrity | The shift in the score itself, at 0.007023 , is smaller than… | 0.007023 | ratio | psi |  | eq | `[[art:a2885abf:psi.y_score]]` | verified | 0.007023143302 |
| 79 | data_integrity | The characteristic stability indices measure each feature's… | 0.02363 | ratio | csi |  | eq | `[[art:e56cb179:csi.max]]` | verified | 0.02362581795 |
| 80 | data_integrity | That maximum is carried by the most recent delinquency indic… | 0.02363 | ratio | csi |  | eq | `[[art:5babe364:csi.delinq_last]]` | verified | 0.02362581795 |
| 81 | data_integrity | That maximum is carried by the most recent delinquency indic… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 82 | data_integrity | - age: 0.0009476 | 0.0009476 | ratio | csi |  | eq | `[[art:a78e58f6:csi.age]]` | verified | 0.0009475732594 |
| 83 | data_integrity | - bill_mean_6m: 0.002369 | 0.002369 | ratio | csi |  | eq | `[[art:48df6cc9:csi.bill_mean_6m]]` | verified | 0.002369326368 |
| 84 | data_integrity | - bill_trend_6m: 0.00633 | 0.00633 | ratio | csi |  | eq | `[[art:59948e6d:csi.bill_trend_6m]]` | verified | 0.006329590221 |
| 85 | data_integrity | - delinq_count_6m: 0.002449 | 0.002449 | ratio | csi |  | eq | `[[art:69346f52:csi.delinq_count_6m]]` | verified | 0.002448902116 |
| 86 | data_integrity | - delinq_max_6m: 0.0008965 | 0.0008965 | ratio | csi |  | eq | `[[art:7244960d:csi.delinq_max_6m]]` | verified | 0.0008964784296 |
| 87 | data_integrity | - limit_bal: 0.001211 | 0.001211 | ratio | csi |  | eq | `[[art:5b77b34b:csi.limit_bal]]` | verified | 0.001211461258 |
| 88 | data_integrity | - pay_ratio_last: 0.001924 | 0.001924 | ratio | csi |  | eq | `[[art:aff2b4bf:csi.pay_ratio_last]]` | verified | 0.001923767196 |
| 89 | data_integrity | - pay_ratio_mean_6m: 0.001768 | 0.001768 | ratio | csi |  | eq | `[[art:f567818e:csi.pay_ratio_mean_6m]]` | verified | 0.001768345794 |
| 90 | data_integrity | - utilisation: 0.004042 | 0.004042 | ratio | csi |  | eq | `[[art:10f0f9e7:csi.utilisation]]` | verified | 0.004041856699 |
| 91 | data_integrity | The ordering of the two families differs: the credit limit l… | 0.00285 | ratio | psi |  | eq | `[[art:03bd52e7:psi.delinq_last]]` | verified | 0.002849633848 |
| 92 | data_integrity | The ordering of the two families differs: the credit limit l… | 0.02363 | ratio | csi |  | eq | `[[art:5babe364:csi.delinq_last]]` | verified | 0.02362581795 |
| 93 | data_integrity | The count of features declared as observed during the perfor… | 0 | count | n_flagged |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 94 | data_integrity | The strongest single feature reaches an AUC of 0.6831 on its… | 0.6831 | ratio | auc |  | eq | `[[art:fd829fc4:leakage.target_corr.max_single_feature_auc]]` | verified | 0.6831414154 |
| 95 | data_integrity | The strongest single feature reaches an AUC of 0.6831 on its… | 0.9 | ratio | auc |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 96 | data_integrity | The share of test rows whose identifiers also identify a row… | 0 | ratio | overlap |  | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 97 | data_integrity | The share of test rows whose identifiers also identify a row… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 98 | data_integrity | The share of test rows whose feature values also appear in t… | 0 | ratio | overlap |  | eq | `[[art:0fec8048:leakage.overlap.features]]` | verified | 0 |
| 99 | data_integrity | The share of test rows whose feature values also appear in t… | 0.005 | ratio | overlap |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 100 | data_integrity | The share of training rows whose feature values are not uniq… | 0 | ratio | duplicates | train | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 101 | data_integrity | The share of training rows whose feature values are not uniq… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 102 | data_integrity | The overlap of test rows with the training split on feature… | 0 | ratio | overlap |  | eq | `[[art:4c9fcd09:leakage.overlap]]` | verified | 0 |
| 103 | data_integrity | The overlap of test rows with the training split on feature… | 0.005 | ratio | overlap |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 104 | data_integrity | The number of feature names matching the target-adjacent lex… | 0 | count | n_matched |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 105 | outcomes | This section reports discrimination first and calibration af… | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 106 | outcomes | This section reports discrimination first and calibration af… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 107 | outcomes | \| Rows \| 3500 \| 1500 \| | 3500 | count | n | train | eq | `[[art:564683ee:metrics.train.n]]` | verified | 3500 |
| 108 | outcomes | \| Rows \| 3500 \| 1500 \| | 1500 | count | n | test | eq | `[[art:64fcf14d:metrics.test.n]]` | verified | 1500 |
| 109 | outcomes | \| Observed event rate \| 0.2246 \| 0.2247 \| | 0.2246 | ratio | event_rate | train | eq | `[[art:133a5ff8:metrics.train.event_rate]]` | verified | 0.2245714286 |
| 110 | outcomes | \| Observed event rate \| 0.2246 \| 0.2247 \| | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 111 | outcomes | \| Mean predicted probability \| 0.2246 \| 0.2211 \| | 0.2246 | ratio | mean_predicted | train | eq | `[[art:605cce58:metrics.train.mean_predicted]]` | verified | 0.2246226934 |
| 112 | outcomes | \| Mean predicted probability \| 0.2246 \| 0.2211 \| | 0.2211 | ratio | mean_predicted | test | eq | `[[art:4d2f8a37:metrics.test.mean_predicted]]` | verified | 0.2211048954 |
| 113 | outcomes | \| AUC \| 0.7584 \| 0.748 \| | 0.7584 | ratio | auc | train | eq | `[[art:14b38a2b:metrics.train.auc]]` | verified | 0.7584356677 |
| 114 | outcomes | \| AUC \| 0.7584 \| 0.748 \| | 0.748 | ratio | auc | test | eq | `[[art:5c6c2bfc:metrics.test.auc]]` | verified | 0.7479888042 |
| 115 | outcomes | \| Gini \| 0.5169 \| 0.496 \| | 0.5169 | ratio | gini | train | eq | `[[art:b4da846e:metrics.train.gini]]` | verified | 0.5168713353 |
| 116 | outcomes | \| Gini \| 0.5169 \| 0.496 \| | 0.496 | ratio | gini | test | eq | `[[art:8e5918d8:metrics.test.gini]]` | verified | 0.4959776083 |
| 117 | outcomes | \| KS \| 0.4451 \| 0.4183 \| | 0.4451 | ratio | ks | train | eq | `[[art:ccc12729:metrics.train.ks]]` | verified | 0.4451397991 |
| 118 | outcomes | \| KS \| 0.4451 \| 0.4183 \| | 0.4183 | ratio | ks | test | eq | `[[art:90751047:metrics.test.ks]]` | verified | 0.4182675012 |
| 119 | outcomes | \| Brier \| 0.1489 \| 0.1489 \| | 0.1489 | ratio | brier | train | eq | `[[art:be669a99:metrics.train.brier]]` | verified | 0.1489149059 |
| 120 | outcomes | \| Brier \| 0.1489 \| 0.1489 \| | 0.1489 | ratio | brier | test | eq | `[[art:bbe69430:metrics.test.brier]]` | verified | 0.148850901 |
| 121 | outcomes | \| Log loss \| 0.465 \| 0.4673 \| | 0.465 | ratio | logloss | train | eq | `[[art:4f02e465:metrics.train.logloss]]` | verified | 0.4650014911 |
| 122 | outcomes | \| Log loss \| 0.465 \| 0.4673 \| | 0.4673 | ratio | logloss | test | eq | `[[art:dda8da69:metrics.test.logloss]]` | verified | 0.4672914712 |
| 123 | outcomes | Rank-ordering is weaker on the holdout than in sample: AUC i… | 0.7584 | ratio | auc | train | eq | `[[art:14b38a2b:metrics.train.auc]]` | verified | 0.7584356677 |
| 124 | outcomes | Rank-ordering is weaker on the holdout than in sample: AUC i… | 0.748 | ratio | auc | test | eq | `[[art:5c6c2bfc:metrics.test.auc]]` | verified | 0.7479888042 |
| 125 | outcomes | The train-to-test movement in AUC was read against a bound o… | 0.08 | ratio | auc_gap |  | eq | `[[art:630f28f4:threshold.O1.auc_gap]]` | verified | 0.08 |
| 126 | outcomes | The top two deciles of predicted probability capture 0.4718… | 0.4718 | ratio | top2_capture | test | eq | `[[art:d4a1cf7d:deciles.test.top2_capture]]` | verified | 0.471810089 |
| 127 | outcomes | The top two deciles of predicted probability capture 0.4718… | 0.4517 | ratio | top2_capture | train | eq | `[[art:1d20c762:deciles.train.top2_capture]]` | verified | 0.451653944 |
| 128 | outcomes | Turning to calibration, the logistic regression of the outco… | 1.003 | ratio | calibration_slope | test | eq | `[[art:b7dbb687:calibration_slope.test]]` | verified | 1.002737656 |
| 129 | outcomes | Turning to calibration, the logistic regression of the outco… | 1.002 | ratio | calibration_slope | train | eq | `[[art:d02e3091:calibration_slope.train]]` | verified | 1.002102954 |
| 130 | outcomes | Both slopes sit inside the declared band, whose bottom is 0.… | 0.8 | ratio | calibration_slope |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 131 | outcomes | Both slopes sit inside the declared band, whose bottom is 0.… | 1.2 | ratio | calibration_slope |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 132 | outcomes | The intercept of that regression is 0.02729 on test and 0.00… | 0.02729 | ratio | calibration_intercept | test | eq | `[[art:b69c6b52:calibration_intercept.test]]` | verified | 0.0272850692 |
| 133 | outcomes | The intercept of that regression is 0.02729 on test and 0.00… | 0.002062 | ratio | calibration_intercept | train | eq | `[[art:ed381a81:calibration_intercept.train]]` | verified | 0.002061562686 |
| 134 | outcomes | Mean predicted probability on test is 0.2211 against an obse… | 0.2211 | ratio | mean_predicted | test | eq | `[[art:4d2f8a37:metrics.test.mean_predicted]]` | verified | 0.2211048954 |
| 135 | outcomes | Mean predicted probability on test is 0.2211 against an obse… | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 136 | outcomes | Expressed relative to the observed rate, that discrepancy is… | 0.01585 | ratio | mean_rel_gap | test | eq | `[[art:d8ffb3d0:calibration.mean_rel_gap.test]]` | verified | 0.01585358118 |
| 137 | outcomes | Expressed relative to the observed rate, that discrepancy is… | 0.0002283 | ratio | mean_rel_gap | train | eq | `[[art:53738d45:calibration.mean_rel_gap.train]]` | verified | 0.0002282786273 |
| 138 | outcomes | Expressed relative to the observed rate, that discrepancy is… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 139 | outcomes | The table records the recomputed test AUC of 0.748 falling b… | 0.748 | ratio | auc | test | eq | `[[art:5c6c2bfc:metrics.test.auc]]` | verified | 0.7479888042 |
| 140 | outcomes | The table records the recomputed test AUC of 0.748 falling b… | 0.78 | ratio | auc | test | eq | `[[art:5487ddda:threshold.package.auc.test.min]]` | verified | 0.78 |
| 141 | outcomes | AUC on this slice is 0.5859 , falling 0.1621 below the split… | 0.5859 | ratio | auc | test | eq | `[[art:43fc7536:metrics.test.sub.delinq_last_high.auc]]` | verified | 0.5859043109 |
| 142 | outcomes | AUC on this slice is 0.5859 , falling 0.1621 below the split… | 0.1621 | ratio | auc_gap | test | eq | `[[art:5886871a:metrics.test.sub.delinq_last_high.auc_gap]]` | verified | 0.1620844933 |
| 143 | outcomes | AUC on this slice is 0.5859 , falling 0.1621 below the split… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 144 | outcomes | The slice holds 0.226 of the split, above the floor of 0.1 a… | 0.226 | ratio | share | test | eq | `[[art:e795e8a9:metrics.test.sub.delinq_last_high.share]]` | verified | 0.226 |
| 145 | outcomes | The slice holds 0.226 of the split, above the floor of 0.1 a… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 146 | outcomes | The slice holds 0.226 of the split, above the floor of 0.1 a… | 0.95 | ratio | slice_max_share |  | eq | `[[art:a928a05c:threshold.O1.slice_max_share]]` | verified | 0.95 |
| 147 | outcomes | Mean predicted on the slice is 0.4664 against an observed ra… | 0.4664 | ratio | mean_predicted | test | eq | `[[art:360fa59b:metrics.test.sub.delinq_last_high.mean_predicted]]` | verified | 0.4663690519 |
| 148 | outcomes | Mean predicted on the slice is 0.4664 against an observed ra… | 0.5103 | ratio | event_rate | test | eq | `[[art:c9cb7610:metrics.test.sub.delinq_last_high.event_rate]]` | verified | 0.5103244838 |
| 149 | outcomes | Mean predicted on the slice is 0.4664 against an observed ra… | 0.08613 | ratio | mean_rel_gap | test | eq | `[[art:1a238a3e:metrics.test.sub.delinq_last_high.mean_rel_gap]]` | verified | 0.08613232036 |
| 150 | outcomes | Mean predicted on the slice is 0.4664 against an observed ra… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 151 | outcomes | AUC on this slice is 0.6333 , falling 0.1147 below the split… | 0.6333 | ratio | auc | test | eq | `[[art:0a7e2c66:metrics.test.sub.delinq_last_low.auc]]` | verified | 0.6332595347 |
| 152 | outcomes | AUC on this slice is 0.6333 , falling 0.1147 below the split… | 0.1147 | ratio | auc_gap | test | eq | `[[art:b25b1c4c:metrics.test.sub.delinq_last_low.auc_gap]]` | verified | 0.1147292695 |
| 153 | outcomes | AUC on this slice is 0.6333 , falling 0.1147 below the split… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 154 | outcomes | The slice holds 0.774 of the split, above the floor of 0.1 a… | 0.774 | ratio | share | test | eq | `[[art:cd49d716:metrics.test.sub.delinq_last_low.share]]` | verified | 0.774 |
| 155 | outcomes | The slice holds 0.774 of the split, above the floor of 0.1 a… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 156 | outcomes | The slice holds 0.774 of the split, above the floor of 0.1 a… | 0.95 | ratio | slice_max_share |  | eq | `[[art:a928a05c:threshold.O1.slice_max_share]]` | verified | 0.95 |
| 157 | outcomes | Mean predicted here is 0.1495 against an observed rate of 0.… | 0.1495 | ratio | mean_predicted | test | eq | `[[art:77d4b87f:metrics.test.sub.delinq_last_low.mean_predicted]]` | verified | 0.1494902968 |
| 158 | outcomes | Mean predicted here is 0.1495 against an observed rate of 0.… | 0.1413 | ratio | event_rate | test | eq | `[[art:2fb6f9a6:metrics.test.sub.delinq_last_low.event_rate]]` | verified | 0.1412575366 |
| 159 | outcomes | Mean predicted here is 0.1495 against an observed rate of 0.… | 0.05828 | ratio | mean_rel_gap | test | eq | `[[art:7d8102b1:metrics.test.sub.delinq_last_low.mean_rel_gap]]` | verified | 0.05828191807 |
| 160 | outcomes | Mean predicted here is 0.1495 against an observed rate of 0.… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 161 | outcomes | AUC on this slice is 0.5689 , falling 0.1791 below the split… | 0.5689 | ratio | auc | test | eq | `[[art:13b21546:metrics.test.sub.utilisation_high.auc]]` | verified | 0.5688944099 |
| 162 | outcomes | AUC on this slice is 0.5689 , falling 0.1791 below the split… | 0.1791 | ratio | auc_gap | test | eq | `[[art:e0dc4aa9:metrics.test.sub.utilisation_high.auc_gap]]` | verified | 0.1790943942 |
| 163 | outcomes | AUC on this slice is 0.5689 , falling 0.1791 below the split… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 164 | outcomes | The slice holds 0.5 of the split, above the floor of 0.1 and… | 0.5 | ratio | share | test | eq | `[[art:9404484e:metrics.test.sub.utilisation_high.share]]` | verified | 0.5 |
| 165 | outcomes | The slice holds 0.5 of the split, above the floor of 0.1 and… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 166 | outcomes | The slice holds 0.5 of the split, above the floor of 0.1 and… | 0.95 | ratio | slice_max_share |  | eq | `[[art:a928a05c:threshold.O1.slice_max_share]]` | verified | 0.95 |
| 167 | outcomes | Mean predicted here is 0.2286 against an observed rate of 0.… | 0.2286 | ratio | mean_predicted | test | eq | `[[art:2d88d7b5:metrics.test.sub.utilisation_high.mean_predicted]]` | verified | 0.2286105275 |
| 168 | outcomes | Mean predicted here is 0.2286 against an observed rate of 0.… | 0.2333 | ratio | event_rate | test | eq | `[[art:8e66209c:metrics.test.sub.utilisation_high.event_rate]]` | verified | 0.2333333333 |
| 169 | outcomes | Mean predicted here is 0.2286 against an observed rate of 0.… | 0.02024 | ratio | mean_rel_gap | test | eq | `[[art:e33a14d6:metrics.test.sub.utilisation_high.mean_rel_gap]]` | verified | 0.02024059629 |
| 170 | outcomes | Mean predicted here is 0.2286 against an observed rate of 0.… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 171 | sensitivity | The largest variance inflation factor over the retained feat… | 7.295 | ratio | vif |  | eq | `[[art:9ae7c45b:vif.max]]` | verified | 7.295299885 |
| 172 | sensitivity | The largest variance inflation factor over the retained feat… | 10 | ratio | vif |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 173 | sensitivity | That maximum belongs to the six-month mean bill feature, at… | 7.295 | ratio | vif |  | eq | `[[art:f0a2f865:vif.bill_mean_6m]]` | verified | 7.295299885 |
| 174 | sensitivity | The two payment-ratio features sit just beneath it, at 7.264… | 7.264 | ratio | vif |  | eq | `[[art:c2de8dfe:vif.pay_ratio_last]]` | verified | 7.264342098 |
| 175 | sensitivity | The two payment-ratio features sit just beneath it, at 7.264… | 7.259 | ratio | vif |  | eq | `[[art:e39c3e82:vif.pay_ratio_mean_6m]]` | verified | 7.25926398 |
| 176 | sensitivity | The credit limit follows at 4.803 and utilisation at 3.215 . | 4.803 | ratio | vif |  | eq | `[[art:ddfdcc3c:vif.limit_bal]]` | verified | 4.803401129 |
| 177 | sensitivity | The credit limit follows at 4.803 and utilisation at 3.215 . | 3.215 | ratio | vif |  | eq | `[[art:536fdb6f:vif.utilisation]]` | verified | 3.215148369 |
| 178 | sensitivity | The delinquency features are lower still, at 2.561 for the s… | 2.561 | ratio | vif |  | eq | `[[art:38974def:vif.delinq_count_6m]]` | verified | 2.561484187 |
| 179 | sensitivity | The delinquency features are lower still, at 2.561 for the s… | 2.408 | ratio | vif |  | eq | `[[art:71aaaf11:vif.delinq_max_6m]]` | verified | 2.40773 |
| 180 | sensitivity | The delinquency features are lower still, at 2.561 for the s… | 1.412 | ratio | vif |  | eq | `[[art:48733638:vif.delinq_last]]` | verified | 1.411555667 |
| 181 | sensitivity | The bill trend is at 1.201 and age at 1.002 , the latter bei… | 1.201 | ratio | vif |  | eq | `[[art:9356a256:vif.bill_trend_6m]]` | verified | 1.201449441 |
| 182 | sensitivity | The bill trend is at 1.201 and age at 1.002 , the latter bei… | 1.002 | ratio | vif |  | eq | `[[art:74c06cad:vif.age]]` | verified | 1.001957997 |
| 183 | sensitivity | Every one of these factors is below the declared ceiling of… | 10 | ratio | vif |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 184 | sensitivity | Belsley's condition number of the column-standardised design… | 5.547 | ratio | condition_number |  | eq | `[[art:e41b9562:condition_number]]` | verified | 5.546934633 |
| 185 | sensitivity | Belsley's condition number of the column-standardised design… | 30 | ratio | condition_number |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 186 | findings | The package declares a minimum AUC on test of 0.78 . | 0.78 | ratio | auc | test | eq | `[[art:5487ddda:threshold.package.auc.test.min]]` | verified | 0.78 |
| 187 | findings | This validation's own recomputation of AUC on the test split… | 0.748 | ratio | auc | test | eq | `[[art:5c6c2bfc:metrics.test.auc]]` | verified | 0.7479888042 |
| 188 | findings | A gradient-boosting challenger reaches an AUC on test of 0.8… | 0.824 | ratio | auc | test | eq | `[[art:bf5be719:challenger.auc]]` | verified | 0.823969015 |
| 189 | findings | A gradient-boosting challenger reaches an AUC on test of 0.8… | 0.748 | ratio | auc | test | eq | `[[art:5c6c2bfc:metrics.test.auc]]` | verified | 0.7479888042 |
| 190 | findings | The challenger's lead over the champion is 0.07598 , which i… | 0.07598 | ratio | delta_auc | test | eq | `[[art:c9e502ae:challenger.delta_auc]]` | verified | 0.0759802108 |
| 191 | findings | The challenger's lead over the champion is 0.07598 , which i… | 0.03 | ratio | delta_auc |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 192 | findings | On the segment `delinq_last > median(delinq_last)`, which ho… | 0.226 | ratio | share | test | eq | `[[art:e795e8a9:metrics.test.sub.delinq_last_high.share]]` | verified | 0.226 |
| 193 | findings | On the segment `delinq_last > median(delinq_last)`, which ho… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 194 | findings | On the segment `delinq_last > median(delinq_last)`, which ho… | 0.5859 | ratio | auc | test | eq | `[[art:43fc7536:metrics.test.sub.delinq_last_high.auc]]` | verified | 0.5859043109 |
| 195 | findings | On the segment `delinq_last > median(delinq_last)`, which ho… | 0.748 | ratio | auc | test | eq | `[[art:5c6c2bfc:metrics.test.auc]]` | verified | 0.7479888042 |
| 196 | findings | On the segment `delinq_last > median(delinq_last)`, which ho… | 0.1621 | ratio | auc_gap | test | eq | `[[art:5886871a:metrics.test.sub.delinq_last_high.auc_gap]]` | verified | 0.1620844933 |
| 197 | findings | On the segment `delinq_last > median(delinq_last)`, which ho… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 198 | findings | On the segment `delinq_last <= median(delinq_last)`, which h… | 0.774 | ratio | share | test | eq | `[[art:cd49d716:metrics.test.sub.delinq_last_low.share]]` | verified | 0.774 |
| 199 | findings | On the segment `delinq_last <= median(delinq_last)`, which h… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 200 | findings | On the segment `delinq_last <= median(delinq_last)`, which h… | 0.6333 | ratio | auc | test | eq | `[[art:0a7e2c66:metrics.test.sub.delinq_last_low.auc]]` | verified | 0.6332595347 |
| 201 | findings | On the segment `delinq_last <= median(delinq_last)`, which h… | 0.748 | ratio | auc | test | eq | `[[art:5c6c2bfc:metrics.test.auc]]` | verified | 0.7479888042 |
| 202 | findings | On the segment `delinq_last <= median(delinq_last)`, which h… | 0.1147 | ratio | auc_gap | test | eq | `[[art:b25b1c4c:metrics.test.sub.delinq_last_low.auc_gap]]` | verified | 0.1147292695 |
| 203 | findings | On the segment `delinq_last <= median(delinq_last)`, which h… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 204 | findings | On the segment `utilisation > median(utilisation)`, which ho… | 0.5 | ratio | share | test | eq | `[[art:9404484e:metrics.test.sub.utilisation_high.share]]` | verified | 0.5 |
| 205 | findings | On the segment `utilisation > median(utilisation)`, which ho… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 206 | findings | On the segment `utilisation > median(utilisation)`, which ho… | 0.5689 | ratio | auc | test | eq | `[[art:13b21546:metrics.test.sub.utilisation_high.auc]]` | verified | 0.5688944099 |
| 207 | findings | On the segment `utilisation > median(utilisation)`, which ho… | 0.748 | ratio | auc | test | eq | `[[art:5c6c2bfc:metrics.test.auc]]` | verified | 0.7479888042 |
| 208 | findings | On the segment `utilisation > median(utilisation)`, which ho… | 0.1791 | ratio | auc_gap | test | eq | `[[art:e0dc4aa9:metrics.test.sub.utilisation_high.auc_gap]]` | verified | 0.1790943942 |
| 209 | findings | On the segment `utilisation > median(utilisation)`, which ho… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 210 | findings | The fitted coefficient on `delinq_max_6m` carries sign -1 wh… | -1 | ratio | coef_sign |  | eq | `[[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]]` | verified | -1 |
| 211 | findings | The fitted coefficient on `delinq_max_6m` carries sign -1 wh… | 1 | ratio | univariate_direction |  | eq | `[[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]]` | verified | 1 |
| 212 | findings | The fitted coefficient on `delinq_max_6m` carries sign -1 wh… | 0 | ratio | agrees |  | eq | `[[art:c946359c:sign_check.delinq_max_6m.agrees]]` | verified | 0 |
| 213 | findings | The fitted coefficient on `limit_bal` carries sign 1 where t… | 1 | ratio | coef_sign |  | eq | `[[art:6af6aef2:sign_check.limit_bal.coef_sign]]` | verified | 1 |
| 214 | findings | The fitted coefficient on `limit_bal` carries sign 1 where t… | -1 | ratio | univariate_direction |  | eq | `[[art:56d284d6:sign_check.limit_bal.univariate_direction]]` | verified | -1 |
| 215 | findings | The fitted coefficient on `limit_bal` carries sign 1 where t… | 0 | ratio | agrees |  | eq | `[[art:0278aad1:sign_check.limit_bal.agrees]]` | verified | 0 |
| 216 | findings | The fitted coefficient on `pay_ratio_last` carries sign 1 wh… | 1 | ratio | coef_sign |  | eq | `[[art:f018263e:sign_check.pay_ratio_last.coef_sign]]` | verified | 1 |
| 217 | findings | The fitted coefficient on `pay_ratio_last` carries sign 1 wh… | -1 | ratio | univariate_direction |  | eq | `[[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]]` | verified | -1 |
| 218 | findings | The fitted coefficient on `pay_ratio_last` carries sign 1 wh… | 0 | ratio | agrees |  | eq | `[[art:79abee77:sign_check.pay_ratio_last.agrees]]` | verified | 0 |
| 219 | monitoring | Rank-ordering should be recomputed on each production cohort… | 0.78 | ratio | auc | test | eq | `[[art:5487ddda:threshold.package.auc.test.min]]` | verified | 0.78 |
| 220 | monitoring | Rank-ordering should be recomputed on each production cohort… | 0.748 | ratio | auc | test | eq | `[[art:5c6c2bfc:metrics.test.auc]]` | verified | 0.7479888042 |
| 221 | monitoring | Probability accuracy should be recomputed on the same cadenc… | 0.2 | ratio | brier | test | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 222 | monitoring | Probability accuracy should be recomputed on the same cadenc… | 0.1489 | ratio | brier | test | eq | `[[art:bbe69430:metrics.test.brier]]` | verified | 0.148850901 |
| 223 | monitoring | The slope of the outcome regressed on the logit of the predi… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 224 | monitoring | The slope of the outcome regressed on the logit of the predi… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 225 | monitoring | The slope of the outcome regressed on the logit of the predi… | 1.003 | ratio | calibration_slope | test | eq | `[[art:b7dbb687:calibration_slope.test]]` | verified | 1.002737656 |
| 226 | monitoring | Population and score stability should be read against the de… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 227 | monitoring | Population and score stability should be read against the de… | 0.01095 | ratio | psi |  | eq | `[[art:381b2570:psi.max]]` | verified | 0.01095273358 |
| 228 | monitoring | Section 4 of this report reported discrimination before cali… | 0.05 | ratio | event_rate | test | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |

## Appendix B — Artifact index

The store holds 207 artifacts; the 144 this report cites or rests a finding on are indexed here.

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
| `metrics.test.sub.delinq_last_high` | `6ae225dc` | table | table, 10 rows | every metric on the delinq_last above_median slice of test |
| `metrics.test.sub.delinq_last_high.auc` | `43fc7536` | scalar | 0.5859043109 | auc on the delinq_last above_median slice of test |
| `metrics.test.sub.delinq_last_high.auc_gap` | `5886871a` | scalar | 0.1620844933 | how far AUC on the delinq_last above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.delinq_last_high.event_rate` | `c9cb7610` | scalar | 0.5103244838 | event_rate on the delinq_last above_median slice of test |
| `metrics.test.sub.delinq_last_high.mean_predicted` | `360fa59b` | scalar | 0.4663690519 | mean_predicted on the delinq_last above_median slice of test |
| `metrics.test.sub.delinq_last_high.mean_rel_gap` | `1a238a3e` | scalar | 0.08613232036 | mean predicted against observed on the delinq_last above_median slice of test, relative |
| `metrics.test.sub.delinq_last_high.share` | `e795e8a9` | scalar | 0.226 | the share of test the delinq_last above_median slice holds |
| `metrics.test.sub.delinq_last_low` | `64a1c670` | table | table, 10 rows | every metric on the delinq_last below_median slice of test |
| `metrics.test.sub.delinq_last_low.auc` | `0a7e2c66` | scalar | 0.6332595347 | auc on the delinq_last below_median slice of test |
| `metrics.test.sub.delinq_last_low.auc_gap` | `b25b1c4c` | scalar | 0.1147292695 | how far AUC on the delinq_last below_median slice of test falls below AUC on all of test |
| `metrics.test.sub.delinq_last_low.event_rate` | `2fb6f9a6` | scalar | 0.1412575366 | event_rate on the delinq_last below_median slice of test |
| `metrics.test.sub.delinq_last_low.mean_predicted` | `77d4b87f` | scalar | 0.1494902968 | mean_predicted on the delinq_last below_median slice of test |
| `metrics.test.sub.delinq_last_low.mean_rel_gap` | `7d8102b1` | scalar | 0.05828191807 | mean predicted against observed on the delinq_last below_median slice of test, relative |
| `metrics.test.sub.delinq_last_low.share` | `cd49d716` | scalar | 0.774 | the share of test the delinq_last below_median slice holds |
| `metrics.test.sub.utilisation_high` | `ab9ef6ac` | table | table, 10 rows | every metric on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.auc` | `13b21546` | scalar | 0.5688944099 | auc on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.auc_gap` | `e0dc4aa9` | scalar | 0.1790943942 | how far AUC on the utilisation above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.utilisation_high.event_rate` | `8e66209c` | scalar | 0.2333333333 | event_rate on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.mean_predicted` | `2d88d7b5` | scalar | 0.2286105275 | mean_predicted on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.mean_rel_gap` | `e33a14d6` | scalar | 0.02024059629 | mean predicted against observed on the utilisation above_median slice of test, relative |
| `metrics.test.sub.utilisation_high.share` | `9404484e` | scalar | 0.5 | the share of test the utilisation above_median slice holds |
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
| `sign_check.delinq_last.agrees` | `a8ba9372` | scalar | 1 | 1 when the fitted sign on delinq_last agrees with its univariate direction, 0 when it does not |
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
| `sign_check.utilisation.agrees` | `d0c9a130` | scalar | 1 | 1 when the fitted sign on utilisation agrees with its univariate direction, 0 when it does not |
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
| `threshold.package.auc.test.min` | `5487ddda` | scalar | 0.78 | package.yaml declares auc min 0.78 |
| `threshold.package.brier.test.max` | `d0f98b9c` | scalar | 0.2 | package.yaml declares brier max 0.2 |
| `threshold.package.calibration_slope.test.max` | `0adb7a89` | scalar | 1.2 | package.yaml declares calibration_slope max 1.2 |
| `threshold.package.calibration_slope.test.min` | `95fdb848` | scalar | 0.8 | package.yaml declares calibration_slope min 0.8 |
| `threshold.package.psi.max` | `fbb5a9d1` | scalar | 0.25 | package.yaml declares psi max 0.25 |
| `thresholds.evaluation` | `f67e8fcc` | table | table, 5 rows | every threshold package.yaml declares, with its bound, the recomputed value and the outcome |
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
| tool calls | 17 (run_model 1, profile_data 1, compute_metrics 4, check_leakage 1, check_collinearity 1, challenger_compare 2, retrieve_guidance 7) |
| plan steps (bounded loop) | 4 |
| LLM calls | 18 (plan 4, draft 7, extract 7) |
| re-asks | 0 |
| repair rounds | 0 |
| tokens in / out | 204,831 / 92,821 |
| notional cost (USD) | 4.4008 |
| wall-clock (s) | 1000.57 |
| subject run (s) | 1.17 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | credit_default-full_agent-20260920T171411Z-e2e51e00 |

## Appendix D — Not checked

| item | reason |
|---|---|
| `check_stability` (R1) | package declares no `regime.column` |
| `run_scenarios` (X1) | not applicable to `binary_classification` |
| out-of-time and vintage-holdout metrics (O1, second rule) | package declares neither split |
| developer claims (T1, claim channel) | The package declares 2 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
