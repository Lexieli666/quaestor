---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: full_agent
model: claude-opus-5[1m]
run_id: credit_default-full_agent-20260920T034326Z-e2e51e00
data_mode: synthetic
synthetic_n: 5000
grounding_precision_pre: 1.0000
grounding_precision_post: 1.0000
n_claims: 212
n_findings_by_severity: {high: 0, medium: 1, low: 1, info: 0}
generated: "2026-09-20T03:43:26Z"
illustrative: false
---

# Validation report — `credit_default` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `credit_default` v1.0 | `full_agent` | claude-opus-5[1m] | synthetic, n = 5000 | 1.0000 → 1.0000 | 0 / 1 / 1 / 0 |
<!-- quaestor:renderer:end -->

The subject of this review is the credit_default model package at version 1.0, a scored classifier that predicts the probability a borrower defaults, and this report follows the structure of the Federal Reserve's model risk management guidance on model validation and monitoring [[reg:SR26-2:V]].
The packaged subject was executed as delivered and its performance metrics were recomputed independently from the resulting predictions, under the wall-clock cap of 300 [[art:2ad8d1a5:runtime.max_seconds]] seconds the package declares.
The development split holds 3500 [[art:2510d49d:profile.train.n]] rows and the held-out test split holds 1500 [[art:2193cf5f:profile.test.n]] rows, and the recomputed evaluation on test covers 1500 [[art:64fcf14d:metrics.test.n]] rows.
The observed event rate on test is 0.2247 [[art:9209d200:metrics.test.event_rate]], against a mean predicted probability of 0.2127 [[art:5cd71007:metrics.test.mean_predicted]], so the model scores slightly below the observed incidence on average across the split.
On the headline result, the model passes each of the developer-declared thresholds carried into this section.
Discrimination on test is 0.7446 [[art:21514080:metrics.test.auc]], above the declared floor of 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]], and below the recomputed value on train of 0.7584 [[art:14b38a2b:metrics.train.auc]].
The Brier score on test is 0.1494 [[art:61f24b2a:metrics.test.brier]], below the declared ceiling of 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]].
The calibration slope on test is 0.9778 [[art:c07e2c62:calibration_slope.test]], inside the declared band whose floor is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] and whose ceiling is 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The largest train-to-test population stability index, the score included, is 0.03973 [[art:9dec5a22:psi.max]], below the declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
This validation raised F-001, a D1 data integrity finding at medium severity, arising from the data profiling of the delivered splits.
It also raised F-002, an E1 effective challenge finding at low severity, arising from the comparison of the subject against a challenger.
Each is written out in full in the findings section below, and this section records only their identifiers, classes and severities.

## 2. Conceptual soundness

Model design, key modeling choices, and the quality and extent of developmental evidence are assessed here, including the benchmarking of the champion against an alternative form [[reg:SR26-2:V.1.a]].

The champion is a linear, one-coefficient-per-feature scoring form with an intercept of -1.396 [[art:74c10f15:run.model_summary#intercept]], fitted on 3500 [[art:74c10f15:run.model_summary#n_train]] training rows.
The feature inventory carries 12 [[art:abbb748e:run.features#n]] features in total, of which 2 [[art:abbb748e:run.features#at_origination]] are known at origination and 10 [[art:abbb748e:run.features#before_period_start]] are known before the performance period starts.
No feature is dated to the performance period itself, at 0 [[art:abbb748e:run.features#during_period]], and none is dated after the outcome, at 0 [[art:abbb748e:run.features#after_outcome]], so on the timing evidence the inputs are all observable at scoring time and none of them post-dates the event being predicted.

The developer's own collinearity screen removed two features before fitting, judged against a variance-inflation threshold of 10 [[art:74c10f15:run.model_summary#vif_threshold]].
The balance level at the last observed month was removed at a variance inflation of 160.9 [[art:74c10f15:run.model_summary#removed.bill_last.vif]], far above that threshold, and the six-month mean utilisation was removed at 36.36 [[art:74c10f15:run.model_summary#removed.utilisation_mean_6m.vif]], also above it.
Both removals are consistent with the screen's stated purpose: each duplicates information already carried by a retained sibling feature, and leaving them in would have made the retained coefficients unstable rather than adding independent signal.

The largest coefficient by magnitude is on the most recent delinquency status, at 0.7334 [[art:74c10f15:run.model_summary#coefficients.delinq_last.value]], and it is positive, which is what credit subject matter expects, since a borrower who is already behind is the borrower most likely to default.
The next largest are the six-month mean bill level at -0.3726 [[art:74c10f15:run.model_summary#coefficients.bill_mean_6m.value]] and the six-month mean payment ratio at -0.3554 [[art:74c10f15:run.model_summary#coefficients.pay_ratio_mean_6m.value]], both negative; a higher sustained payment ratio meaning a borrower who clears more of the statement is expected to lower risk, and the negative sign on the mean bill level is read as a proxy for an established, actively used account rather than as a statement that larger balances are safer.
Utilisation enters positively at 0.2662 [[art:74c10f15:run.model_summary#coefficients.utilisation.value]], which matches the expectation that a borrower closer to the limit has less headroom, and the six-month bill trend enters negatively at -0.2225 [[art:74c10f15:run.model_summary#coefficients.bill_trend_6m.value]].
The remaining coefficients are smaller: the delinquency count over six months at 0.1226 [[art:74c10f15:run.model_summary#coefficients.delinq_count_6m.value]], the last payment ratio at 0.1026 [[art:74c10f15:run.model_summary#coefficients.pay_ratio_last.value]], the credit limit at 0.07266 [[art:74c10f15:run.model_summary#coefficients.limit_bal.value]], age at -0.06726 [[art:74c10f15:run.model_summary#coefficients.age.value]], and the six-month maximum delinquency at -0.03221 [[art:74c10f15:run.model_summary#coefficients.delinq_max_6m.value]].

Each fitted sign was compared with the direction of that feature's own single-feature relationship with the outcome on train, and 3 [[art:e223cd4a:sign_check.n_disagreements]] of the retained features have a fitted sign that contradicts that direction.
The credit limit is fitted positive at 1 [[art:6af6aef2:sign_check.limit_bal.coef_sign]] while its own direction on train is -1 [[art:56d284d6:sign_check.limit_bal.univariate_direction]], so the two disagree at 0 [[art:0278aad1:sign_check.limit_bal.agrees]]; the coefficient it carries, 0.07266 [[art:74c10f15:run.model_summary#coefficients.limit_bal.value]], is among the smaller ones in the model, so the reversal sits on a feature the fitted form leans on lightly.
The last payment ratio is fitted positive at 1 [[art:f018263e:sign_check.pay_ratio_last.coef_sign]] against an own direction of -1 [[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]], disagreeing at 0 [[art:79abee77:sign_check.pay_ratio_last.agrees]], and this one is harder to read past, because a higher single-month payment ratio raising the fitted score runs against the subject-matter expectation and against the negative sign on the six-month mean payment ratio, -0.3554 [[art:74c10f15:run.model_summary#coefficients.pay_ratio_mean_6m.value]], which the same model fits on the smoothed version of the same quantity.
The six-month maximum delinquency is fitted negative at -1 [[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]] against an own direction of 1 [[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]], disagreeing at 0 [[art:c946359c:sign_check.delinq_max_6m.agrees]], and on its own a worse delinquency peak should raise risk, not lower it; its coefficient, -0.03221 [[art:74c10f15:run.model_summary#coefficients.delinq_max_6m.value]], is the smallest in the model, and it sits alongside two other delinquency measures that are both fitted positive.
In all three cases the pattern is the signature of correlated inputs sharing a signal rather than of a feature behaving perversely on its own, and the weight the model places on each is what governs how much the reversal matters in use.

The features whose fitted signs agree with their own directions are the remainder: the most recent delinquency at 1 [[art:a8ba9372:sign_check.delinq_last.agrees]], the delinquency count at 1 [[art:a337d16b:sign_check.delinq_count_6m.agrees]], utilisation at 1 [[art:d0c9a130:sign_check.utilisation.agrees]], the six-month mean payment ratio at 1 [[art:7e9a76ca:sign_check.pay_ratio_mean_6m.agrees]], the six-month mean bill level at 1 [[art:89279c3b:sign_check.bill_mean_6m.agrees]], the six-month bill trend at 1 [[art:ff3cb24a:sign_check.bill_trend_6m.agrees]], and age at 1 [[art:4116add1:sign_check.age.agrees]], the last of these fitted negative at -1 [[art:6172eb93:sign_check.age.coef_sign]] with an own direction of -1 [[art:66364583:sign_check.age.univariate_direction]], consistent with older borrowers defaulting less.
This sign evidence and the refit-without-one-feature evidence are developmental evidence bearing on the design, and no declared bound is read against either family in this section.

On effective challenge, an alternative functional form was fitted as a challenger and scored on the same test split.
The challenger reaches an AUC of 0.8249 [[art:6db67e77:challenger.auc]] against the champion's 0.7446 [[art:21514080:metrics.test.auc]], and the comparison declared for this test is the difference in test AUC, which is 0.08022 [[art:19982ff0:challenger.delta_auc]] in the challenger's favour.
The bound that decides whether that difference matters is an effective-challenge lead of 0.03 [[art:e042774c:threshold.E1.delta_auc]], and the observed difference is above it.
The challenger's Brier score, 0.1248 [[art:67796f7f:challenger.brier]], is also lower than the champion's, 0.1494 [[art:61f24b2a:metrics.test.brier]], so the challenger is better on calibrated accuracy as well as on ranking and the gap is not an artefact of the discrimination metric alone.
Because the challenger differs from the champion in functional form rather than in its inputs, this result is a statement about the champion's functional form: the linear-in-log-odds specification leaves discrimination on the table that a more flexible form recovers from the same features.
That result is the finding raised for this section, and it is reported with its severity in the findings section.

Taken together, the design evidence supports the champion as an interpretable and timing-clean specification whose screen and whose largest coefficients are defensible on subject-matter grounds, with the reversed signs on three of its smaller-weighted inputs and the challenger's margin as the two qualifications a reader should carry forward.

## 3. Data integrity and drift

Sound development practice includes a critical assessment of data quality, relevance, and inputs, and the screens below examine the splits on which this package was fitted and tested [[reg:SR26-2:IV.1]].

The training split holds 3500 [[art:2510d49d:profile.train.n]] rows and the test split holds 1500 [[art:2193cf5f:profile.test.n]] rows.

### Missingness

The largest missing fraction in the training split is 0 [[art:050a3099:profile.train.missing.max]].
The largest missing fraction in the test split is 0.3 [[art:7b5c0c01:profile.test.missing.max]].
The integrity screen reads the difference in missingness between the two splits, feature by feature, against a declared bound of 0.1 [[art:9cce25ea:threshold.D1.missing_gap]], and that difference is above the bound; the comparison made here is the difference between the splits, not their ratio.
The gap is carried by pay_ratio_last, which is present throughout the training split and incomplete in the test split, and it is raised as finding D1 at a suggested severity of medium.
Because the shortfall is confined to the test split, the feature was learned on complete data and scored on data that is not complete in the same way, which is a limitation of the evidence rather than a defect of the fitting sample.

### Population and characteristic stability

The largest train-to-test population stability index, the score included, is 0.03973 [[art:9dec5a22:psi.max]], below the declared stability bound of 0.25 [[art:278b9016:threshold.S1.psi]], which the package restates at 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
The score carries that maximum, at 0.03973 [[art:828961f6:psi.y_score]], so the shift in the output distribution is larger than the shift in any single input and still well under the declared bound.
Among the inputs, the stability indices are 0.01095 [[art:601cdba2:psi.limit_bal]] for limit_bal, 0.00958 [[art:c247a6f2:psi.bill_trend_6m]] for bill_trend_6m, 0.008124 [[art:f9255a0a:psi.age]] for age, 0.007124 [[art:028e4281:psi.bill_mean_6m]] for bill_mean_6m and 0.005498 [[art:7a82e7f3:psi.delinq_max_6m]] for delinq_max_6m.
The remainder are smaller still, at 0.0055 [[art:2c5baeb2:psi.pay_ratio_mean_6m]] for pay_ratio_mean_6m, 0.005424 [[art:4f6eddcb:psi.pay_ratio_last]] for pay_ratio_last, 0.004244 [[art:451e0780:psi.utilisation]] for utilisation, 0.00285 [[art:03bd52e7:psi.delinq_last]] for delinq_last and 0.002069 [[art:61491d02:psi.delinq_count_6m]] for delinq_count_6m.
The largest characteristic contribution to the shift in the linear predictor is 0.02363 [[art:e56cb179:csi.max]], likewise below the declared stability bound of 0.25 [[art:278b9016:threshold.S1.psi]].
That contribution belongs to delinq_last, at 0.02363 [[art:5babe364:csi.delinq_last]], followed by bill_trend_6m at 0.00633 [[art:59948e6d:csi.bill_trend_6m]], pay_ratio_last at 0.004524 [[art:5eec4717:csi.pay_ratio_last]] and utilisation at 0.004042 [[art:10f0f9e7:csi.utilisation]].
The remaining contributions are 0.002449 [[art:69346f52:csi.delinq_count_6m]] for delinq_count_6m, 0.002369 [[art:48df6cc9:csi.bill_mean_6m]] for bill_mean_6m, 0.001768 [[art:f567818e:csi.pay_ratio_mean_6m]] for pay_ratio_mean_6m, 0.001211 [[art:5b77b34b:csi.limit_bal]] for limit_bal, 0.0009476 [[art:a78e58f6:csi.age]] for age and 0.0008965 [[art:7244960d:csi.delinq_max_6m]] for delinq_max_6m.
Notably, delinq_last is quiet on the population measure and the loudest on the characteristic measure, which indicates that its weight in the predictor, rather than a marked move in its own distribution, drives its contribution.

### Leakage screens

The number of features declared as observed during the performance period or after the outcome is 0 [[art:742bcd24:leakage.timing.n_flagged]], so the declared timings raise no objection on their own.
The strongest single feature reaches an area under the curve of 0.6831 [[art:fd829fc4:leakage.target_corr.max_single_feature_auc]], below the bound of 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]] that one feature may reach alone, which is the pattern expected of a genuine predictor rather than a restatement of the target.
The contamination screen has two arms, each read against its own bound.
On identifiers, the share of test rows whose client_id also identifies a row of the training split is 0 [[art:63d37fc5:leakage.overlap.ids]], against the declared bound of 0.005 [[art:9f336eaf:threshold.L2.overlap]].
On feature vectors, the share of test rows whose feature values also appear in the training split is 0 [[art:0fec8048:leakage.overlap.features]], against the bound the rule actually applied, 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]], which is the larger of the declared bound and a floor derived from the within-train duplicate share, since two distinct subjects recording the same discrete row is coincidence rather than contamination.
That duplicate share, the fraction of training rows whose feature values are not unique within the training split, is 0 [[art:4474c227:leakage.duplicates.train]], so the applied bound rests on the declared value rather than on the duplicate-derived floor.
The overall share of test rows whose feature values also appear in the training split is 0 [[art:4c9fcd09:leakage.overlap]], read against the same applied bound of 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].
The name screen matches 0 [[art:407e62be:leakage.name_screen.n_matched]] feature names against the target-adjacent lexicon.

### Assessment

The stability and leakage screens in this section all sit within the bounds they were read against, and the only matter raised here as a finding is D1, the missingness gap on pay_ratio_last between the training and test splits.
The consequence for the rest of the report is that test-split evidence involving pay_ratio_last should be read with that gap in mind, since the split on which performance is measured does not carry the same completeness as the split on which the model was fitted.

## 4. Outcomes analysis

Outcomes analysis compares the model's outputs with the realised outcomes on the splits at hand, as the current guidance on outcomes analysis describes [[reg:SR26-2:V.1.b]].
This section reports discrimination first and calibration second.
The reason is the observed event rate on the evaluation split, 0.2247 [[art:9209d200:metrics.test.event_rate]], which sits above 0.05 [[art:42f1351e:rule.calibration_first_event_rate]], the rate below which this report would lead with calibration instead.

The recomputed metrics by split are as follows, one row per metric.

| Metric | Train | Test |
| --- | --- | --- |
| Observations | 3500 [[art:564683ee:metrics.train.n]] | 1500 [[art:64fcf14d:metrics.test.n]] |
| Event rate | 0.2246 [[art:133a5ff8:metrics.train.event_rate]] | 0.2247 [[art:9209d200:metrics.test.event_rate]] |
| AUC | 0.7584 [[art:14b38a2b:metrics.train.auc]] | 0.7446 [[art:21514080:metrics.test.auc]] |
| Gini | 0.5169 [[art:b4da846e:metrics.train.gini]] | 0.4893 [[art:6d62a3df:metrics.test.gini]] |
| KS | 0.4451 [[art:ccc12729:metrics.train.ks]] | 0.41 [[art:2bfec7c8:metrics.test.ks]] |
| Brier | 0.1489 [[art:be669a99:metrics.train.brier]] | 0.1494 [[art:61f24b2a:metrics.test.brier]] |
| Log loss | 0.465 [[art:4f02e465:metrics.train.logloss]] | 0.4684 [[art:92c35262:metrics.test.logloss]] |
| Mean predicted probability | 0.2246 [[art:605cce58:metrics.train.mean_predicted]] | 0.2127 [[art:5cd71007:metrics.test.mean_predicted]] |
| Share of events in the top two deciles | 0.4517 [[art:1d20c762:deciles.train.top2_capture]] | 0.4688 [[art:17d2971c:deciles.test.top2_capture]] |

The rank-ordering behind those figures is set out by decile of predicted probability on the evaluation split.

<!-- quaestor:renderer:begin table deciles.test -->
Decile separation on test; decile 1 holds the highest probabilities [[art:c922f3a3:deciles.test]]:

| decile | count | events | event_rate | lift |
|---|---|---|---|---|
| 1 | 150 | 87 | 0.58 | 2.582 |
| 2 | 150 | 71 | 0.4733 | 2.107 |
| 3 | 150 | 49 | 0.3267 | 1.454 |
| 4 | 150 | 30 | 0.2 | 0.8902 |
| 5 | 150 | 27 | 0.18 | 0.8012 |
| 6 | 150 | 15 | 0.1 | 0.4451 |
| 7 | 150 | 12 | 0.08 | 0.3561 |
| 8 | 150 | 17 | 0.1133 | 0.5045 |
| 9 | 150 | 13 | 0.08667 | 0.3858 |
| 10 | 150 | 16 | 0.1067 | 0.4748 |
<!-- quaestor:renderer:end -->

Rank-ordering is weaker on the evaluation split than in sample: AUC is 0.7584 [[art:14b38a2b:metrics.train.auc]] on train against 0.7446 [[art:21514080:metrics.test.auc]] on test, and the same direction holds for Gini and for KS.
The tolerance the review applies to the train-to-test AUC gap is 0.08 [[art:630f28f4:threshold.O1.auc_gap]], and the drop from the train figure to the test figure is smaller than that tolerance.

Turning to calibration, the logistic regression of the outcome on the logit of the predicted probability gives a slope of 0.9778 [[art:c07e2c62:calibration_slope.test]] on test, inside a band bounded below by 0.8 [[art:749634ae:threshold.C1.calibration_slope.min]] and above by 1.2 [[art:b6672579:threshold.C1.calibration_slope.max]].
The corresponding intercept on test is 0.05554 [[art:f4d4ef2b:calibration_intercept.test]].
On train the slope is 1.002 [[art:d02e3091:calibration_slope.train]] and the intercept is 0.002062 [[art:ed381a81:calibration_intercept.train]], so the in-sample fit sits closer to the identity line than the out-of-sample fit does.
In level terms, the mean predicted probability on test is 0.2127 [[art:5cd71007:metrics.test.mean_predicted]] against an observed rate of 0.2247 [[art:9209d200:metrics.test.event_rate]], so the model under-predicts the level of risk on that split.
The relative gap between the two is 0.05348 [[art:64a3c99e:calibration.mean_rel_gap.test]], below the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]] the review applies to it.
Comparing the two relative gaps as values rather than as a difference or a ratio between them, the test value of 0.05348 [[art:64a3c99e:calibration.mean_rel_gap.test]] is the larger and the train value of 0.0002283 [[art:53738d45:calibration.mean_rel_gap.train]] the smaller, which is what an in-sample fit on the same mean would be expected to show.
Calibration by decile of predicted probability on the evaluation split is set out below.

<!-- quaestor:renderer:begin table calibration.test -->
Calibration by decile of predicted probability on test [[art:f03c533a:calibration.test]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.07216 | 0.1067 | 150 |
| 2 | 0.09763 | 0.08667 | 150 |
| 3 | 0.1146 | 0.1133 | 150 |
| 4 | 0.1289 | 0.08 | 150 |
| 5 | 0.1471 | 0.1 | 150 |
| 6 | 0.1667 | 0.18 | 150 |
| 7 | 0.1909 | 0.2 | 150 |
| 8 | 0.2401 | 0.3267 | 150 |
| 9 | 0.3688 | 0.4733 | 150 |
| 10 | 0.5997 | 0.58 | 150 |
<!-- quaestor:renderer:end -->

The developer-declared thresholds, each with its bound, the value recomputed here and the outcome, are set out below.

<!-- quaestor:renderer:begin table thresholds.evaluation -->
Every threshold package.yaml declares, with its bound, the recomputed value and the outcome [[art:9ff847ca:thresholds.evaluation]]:

| metric | split | bound | value | result |
|---|---|---|---|---|
| auc | test | minimum 0.7 | 0.7446 | pass |
| brier | test | maximum 0.2 | 0.1494 | pass |
| calibration_slope | test | minimum 0.8 | 0.9778 | pass |
| calibration_slope | test | maximum 1.2 | 0.9778 | pass |
| psi |  | maximum 0.25 | 0.03973 | pass |
<!-- quaestor:renderer:end -->

Each row of that table pairs a bound declared in package.yaml with the value this run recomputed for it and the outcome of that comparison.
The values it compares are the same recomputed quantities reported above, so its outcomes are the outcomes of this section's numbers.

### Follow-up analyses

The bounded planning loop ran two further metric computations, each on one half of a median split of the pay_ratio_last feature.

The first asked for the full metric set on the slice `pay_ratio_last > median(pay_ratio_last)`, on both splits.
It was asked in order to test whether the model's weaker discrimination concentrates in the part of the pay_ratio_last range affected by the missingness difference between train and test that the review examined under the developer's D1 rule, and so whether the challenger's reported AUC lead is driven by that region.

<!-- quaestor:renderer:begin table metrics.train.sub.pay_ratio_last_high -->
Every metric on the pay_ratio_last above_median slice of train [[art:432527b1:metrics.train.sub.pay_ratio_last_high]]:

| metric | value |
|---|---|
| n | 1750 |
| event_rate | 0.2017 |
| auc | 0.761 |
| gini | 0.5219 |
| ks | 0.4712 |
| brier | 0.1384 |
| logloss | 0.4378 |
| mean_predicted | 0.1973 |
| mean_rel_gap | 0.02206 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.pay_ratio_last_high -->
Every metric on the pay_ratio_last above_median slice of test [[art:96288929:metrics.test.sub.pay_ratio_last_high]]:

| metric | value |
|---|---|
| n | 525 |
| event_rate | 0.2 |
| auc | 0.7683 |
| gini | 0.5367 |
| ks | 0.5167 |
| brier | 0.1271 |
| logloss | 0.4124 |
| mean_predicted | 0.1949 |
| mean_rel_gap | 0.02545 |
| share | 0.35 |
<!-- quaestor:renderer:end -->

On train this slice's AUC of 0.761 [[art:aefc6bf2:metrics.train.sub.pay_ratio_last_high.auc]] stands above the split's own, its shortfall being -0.002517 [[art:114f7785:metrics.train.sub.pay_ratio_last_high.auc_gap]] against a bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].
On test its AUC of 0.7683 [[art:e011e41a:metrics.test.sub.pay_ratio_last_high.auc]] likewise stands above the split's own, with a shortfall of -0.0237 [[art:2e0fdc88:metrics.test.sub.pay_ratio_last_high.auc_gap]] against the same bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].
The slice holds 0.5 [[art:885c90a0:metrics.train.sub.pay_ratio_last_high.share]] of train on 1750 [[art:6caa2b34:metrics.train.sub.pay_ratio_last_high.n]] rows and 0.35 [[art:a02902d1:metrics.test.sub.pay_ratio_last_high.share]] of test on 525 [[art:01944702:metrics.test.sub.pay_ratio_last_high.n]] rows, both above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] a sub-population must reach and below the ceiling of 0.95 [[art:a928a05c:threshold.O1.slice_max_share]] at which it would be the whole split.
On level, mean predicted on this slice of test is 0.1949 [[art:9f99173b:metrics.test.sub.pay_ratio_last_high.mean_predicted]] against an observed rate of 0.2 [[art:12a48470:metrics.test.sub.pay_ratio_last_high.event_rate]], a relative gap of 0.02545 [[art:0b1e3e54:metrics.test.sub.pay_ratio_last_high.mean_rel_gap]], so on this half the probabilities track the observed level closely and the ordering is no weaker than on the split as a whole.

The second asked for the same metric set on the complementary slice `pay_ratio_last <= median(pay_ratio_last)`, on both splits.
It was asked so that the two halves of the partition could be read together, showing whether the missingness drift across splits coincides with performance differing across that feature's range.

<!-- quaestor:renderer:begin table metrics.train.sub.pay_ratio_last_low -->
Every metric on the pay_ratio_last below_median slice of train [[art:70335bfe:metrics.train.sub.pay_ratio_last_low]]:

| metric | value |
|---|---|
| n | 1750 |
| event_rate | 0.2474 |
| auc | 0.7585 |
| gini | 0.517 |
| ks | 0.4383 |
| brier | 0.1594 |
| logloss | 0.4922 |
| mean_predicted | 0.252 |
| mean_rel_gap | 0.0184 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.pay_ratio_last_low -->
Every metric on the pay_ratio_last below_median slice of test [[art:0f69d233:metrics.test.sub.pay_ratio_last_low]]:

| metric | value |
|---|---|
| n | 525 |
| event_rate | 0.2514 |
| auc | 0.7028 |
| gini | 0.4055 |
| ks | 0.354 |
| brier | 0.1726 |
| logloss | 0.5286 |
| mean_predicted | 0.2565 |
| mean_rel_gap | 0.0201 |
| share | 0.35 |
<!-- quaestor:renderer:end -->

On train this slice's AUC of 0.7585 [[art:8ceea245:metrics.train.sub.pay_ratio_last_low.auc]] sits level with the split's own, its shortfall being -4.51e-05 [[art:1eebca8c:metrics.train.sub.pay_ratio_last_low.auc_gap]] against a bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].
On test its AUC of 0.7028 [[art:e2d27a4b:metrics.test.sub.pay_ratio_last_low.auc]] falls below the split's own by 0.04189 [[art:59764abf:metrics.test.sub.pay_ratio_last_low.auc_gap]], still within the same bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].
Comparing the two halves on test by their AUC shortfalls as gaps rather than as a ratio between them, the shortfall of 0.04189 [[art:59764abf:metrics.test.sub.pay_ratio_last_low.auc_gap]] on this half is the larger and the shortfall of -0.0237 [[art:2e0fdc88:metrics.test.sub.pay_ratio_last_high.auc_gap]] on the other half is the smaller, the latter being an excess rather than a deficit.
The slice holds 0.5 [[art:7ffa8f3d:metrics.train.sub.pay_ratio_last_low.share]] of train on 1750 [[art:3edfedd7:metrics.train.sub.pay_ratio_last_low.n]] rows and 0.35 [[art:30c17bde:metrics.test.sub.pay_ratio_last_low.share]] of test on 525 [[art:07df56e1:metrics.test.sub.pay_ratio_last_low.n]] rows, both above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] and below the ceiling of 0.95 [[art:a928a05c:threshold.O1.slice_max_share]].
On level, mean predicted on this slice of test is 0.2565 [[art:a258ff37:metrics.test.sub.pay_ratio_last_low.mean_predicted]] against an observed rate of 0.2514 [[art:f772d438:metrics.test.sub.pay_ratio_last_low.event_rate]], a relative gap of 0.0201 [[art:5cbda8a4:metrics.test.sub.pay_ratio_last_low.mean_rel_gap]], which is smaller than the relative gap of 0.05348 [[art:64a3c99e:calibration.mean_rel_gap.test]] on the split as a whole when the two are compared as values.
Taken together, the level of the probabilities on this half is close to what was observed while its ordering is the weaker of the two halves, so the weakness this slice shows is in the ordering rather than in the level.

## 5. Sensitivity and scenario analysis

Sensitivity analysis checks the impact of small changes in inputs and parameter values on model outputs, and stress testing over a wide range of inputs, including extreme values, establishes the boundaries within which the model remains stable [[reg:SR11-7:V.1.a]].

### Multicollinearity among the retained features

The largest variance inflation factor across the retained features is 7.295 [[art:9ae7c45b:vif.max]], below the declared threshold of 10 [[art:aeb4f33c:threshold.M1.vif]].
Belsley's condition number of the column-standardised design is 5.547 [[art:e41b9562:condition_number]], below the declared threshold of 30 [[art:7e52fd7a:threshold.M1.condition_number]].
Because the largest of the per-feature factors sits below its threshold, every retained feature sits below it.

The per-feature factors on the training sample are as follows.

- The factor for bill_mean_6m is 7.295 [[art:f0a2f865:vif.bill_mean_6m]].
- The factor for pay_ratio_last is 7.264 [[art:c2de8dfe:vif.pay_ratio_last]].
- The factor for pay_ratio_mean_6m is 7.259 [[art:e39c3e82:vif.pay_ratio_mean_6m]].
- The factor for limit_bal is 4.803 [[art:ddfdcc3c:vif.limit_bal]].
- The factor for utilisation is 3.215 [[art:536fdb6f:vif.utilisation]].
- The factor for delinq_count_6m is 2.561 [[art:38974def:vif.delinq_count_6m]].
- The factor for delinq_max_6m is 2.408 [[art:71aaaf11:vif.delinq_max_6m]].
- The factor for delinq_last is 1.412 [[art:48733638:vif.delinq_last]].
- The factor for bill_trend_6m is 1.201 [[art:9356a256:vif.bill_trend_6m]].
- The factor for age is 1.002 [[art:74c06cad:vif.age]].

The values for bill_mean_6m, pay_ratio_last and pay_ratio_mean_6m sit close to one another at the top of the range, which is consistent with the billing level and the two payment-ratio features carrying overlapping information about the same repayment behaviour.
The features drawn from delinquency history, together with the billing trend and age, sit lower in the range, with age showing the least inflation of the retained set.
The two diagnostics point in the same direction: the conditioning of the standardised design is further from its threshold than the largest per-feature factor is from its own, and neither approaches the level at which the coefficient estimates would be treated as unstable under collinearity.
Because the design is comfortably inside both limits, the coefficient standard errors and the attribution of effect between the correlated billing and payment-ratio features can be read at face value, though the closeness of those three values remains the aspect of the design most worth re-checking when the feature set changes.

### Checks conditional on the subject

Two of the analyses that this section would otherwise carry are conditional on properties of the subject rather than on the evidence assembled for it.
Stability across declared regimes applies only where the package declares a regime column, and it is carried in Appendix D among the checks conditioned in that way.
The rate-shock scenarios apply only where the subject is a hazard model, which a credit default classifier of this construction is not.
Accordingly, the value change at the extreme shocks, the monotonicity of the shock curve and the convexity of that curve against the direction the package declares do not apply to this model type.
Those items appear in Appendix D as checks that do not apply, and nothing in this section should be read as reporting a shock grid, a monotonicity verdict, a convexity direction or a regime comparison that was run.

Nothing in this section is raised as a finding.

## 6. Findings and recommendations

Findings below are ordered by severity, the more material first, and each carries the recomputed evidence on which it rests, consistent with validation that identifies model limitations and errors and clarifies whether corrective actions may be warranted [[reg:SR26-2:V]].

### F-001 · D1 data integrity · severity **medium**

**The training and test splits do not share the same missingness structure: the feature `pay_ratio_last` is missing at materially different rates across the two splits, so the test split is not a clean read on the population the model was fitted to.**

The per-feature missingness of the two splits is set out below, and the difference on that feature is larger than the declared split-gap limit of 0.1 [[art:9cce25ea:threshold.D1.missing_gap]].

<!-- quaestor:renderer:begin table profile.train.missing -->
Missingness per feature in train [[art:0c6f5686:profile.train.missing]]:

| feature | n_missing | missing_fraction |
|---|---|---|
| limit_bal | 0 | 0 |
| age | 0 | 0 |
| utilisation | 0 | 0 |
| pay_ratio_last | 0 | 0 |
| pay_ratio_mean_6m | 0 | 0 |
| delinq_last | 0 | 0 |
| delinq_count_6m | 0 | 0 |
| delinq_max_6m | 0 | 0 |
| bill_mean_6m | 0 | 0 |
| bill_trend_6m | 0 | 0 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table profile.test.missing -->
Missingness per feature in test [[art:2dbb3988:profile.test.missing]]:

| feature | n_missing | missing_fraction |
|---|---|---|
| limit_bal | 0 | 0 |
| age | 0 | 0 |
| utilisation | 0 | 0 |
| pay_ratio_last | 450 | 0.3 |
| pay_ratio_mean_6m | 0 | 0 |
| delinq_last | 0 | 0 |
| delinq_count_6m | 0 | 0 |
| delinq_max_6m | 0 | 0 |
| bill_mean_6m | 0 | 0 |
| bill_trend_6m | 0 | 0 |
<!-- quaestor:renderer:end -->

The comparison drawn here is the absolute difference in missingness rate between the two splits on a single feature, not a ratio between them.

The validator concludes that test-split performance on this package is read through a feature whose availability differs from the one the estimator saw in training, which weakens any inference drawn from the test split about live behaviour.

The model developer should establish why the missingness on that feature diverges across splits, state whether the divergence reflects the sampling of the splits or the upstream source, and either reconstitute the splits on a common basis or re-estimate and re-evaluate with an imputation and missing-indicator treatment that is identical on both sides.

### F-002 · E1 effective challenge · severity **low**

**A routine challenger outperforms the champion on the held-out test split by a margin wider than the threshold set for effective challenge, so the champion's specification is not demonstrated to be the better choice on this data.**

A history-gradient-boosting challenger reaches an AUC of 0.8249 [[art:6db67e77:challenger.auc]] on test, above the champion's recomputed AUC of 0.7446 [[art:21514080:metrics.test.auc]].

Expressed as the difference between the two, and not as their ratio, the challenger's lead is 0.08022 [[art:19982ff0:challenger.delta_auc]], above the effective-challenge threshold of 0.03 [[art:e042774c:threshold.E1.delta_auc]].

The validator concludes that the discriminatory power left on the table by the champion specification is wide enough on this data that the choice of the champion form cannot rest on performance alone.

The model developer should document the grounds on which the champion form was selected over a more flexible alternative, whether interpretability, stability, implementation constraint or use-case requirement, and record that rationale and the challenger comparison so the trade-off can be tracked and revisited [[reg:SR26-2:VI.3]].

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (S1), `compute_metrics` (T1, C1, O1), `check_leakage` (L1, L2), `check_collinearity` (M1).

### Open items

Within the segment on which `delinq_max_6m` is fitted with coefficient sign -1 [[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]], read against that feature's own univariate direction of 1 [[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]] with an agreement indicator of 0 [[art:c946359c:sign_check.delinq_max_6m.agrees]], what is the model actually discriminating on once the correlated features held alongside it are accounted for, and can the model developer show that the opposed sign is the intended conditional behaviour rather than an artefact of collinearity?

Within the segment on which `limit_bal` is fitted with coefficient sign 1 [[art:6af6aef2:sign_check.limit_bal.coef_sign]], read against that feature's own univariate direction of -1 [[art:56d284d6:sign_check.limit_bal.univariate_direction]] with an agreement indicator of 0 [[art:0278aad1:sign_check.limit_bal.agrees]], what conditional relationship does the model developer expect to hold once exposure and utilisation move together, and what evidence supports it?

Within the segment on which `pay_ratio_last` is fitted with coefficient sign 1 [[art:f018263e:sign_check.pay_ratio_last.coef_sign]], read against that feature's own univariate direction of -1 [[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]] with an agreement indicator of 0 [[art:79abee77:sign_check.pay_ratio_last.agrees]], can the model developer explain what the fitted sign represents conditional on the rest of the payment-history block, and is that explanation stable under the split-missingness noted above?

## 7. Ongoing monitoring recommendations

Ongoing monitoring evaluates the extent to which this model keeps performing as expected given potential changes in products, exposures, activities, clients, data relevance, or market conditions, and the plan below is scoped to that purpose [[reg:SR26-2:V.2]].
The plan tracks the same quantities this validation recomputed, against the same declared bounds the checks used, so that movement in production is read on a scale already fixed for this package rather than on a new one.
Rank-ordering on scored production cohorts should be reported monthly once outcomes have matured, against the declared floor of 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]], with the evaluation-split value of 0.7446 [[art:21514080:metrics.test.auc]] as the reference point each cohort is read against.
Probability accuracy should be reported on the same monthly cadence against the declared ceiling of 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]], with the evaluation-split value of 0.1494 [[art:61f24b2a:metrics.test.brier]] as its reference point.
Calibration on the logit scale should be reported quarterly, or sooner after any repricing or policy change, against the declared band whose lower bound is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] and whose upper bound is 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]], with the evaluation-split slope of 0.9778 [[art:c07e2c62:calibration_slope.test]] sitting above the lower bound and below the upper one.
Input and score stability should be reported monthly against the declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]], measured from the development population to the production vintage rather than from train to test, with the largest train-to-test value seen in validation, 0.03973 [[art:9dec5a22:psi.max]], well below that ceiling and therefore a demanding reference for what normal drift has looked like so far.
Stability should be reported per feature and for the score itself, since a stable score can conceal offsetting movement in the inputs that feed it.
Where a monitoring cohort's observed event rate falls below 0.05 [[art:42f1351e:rule.calibration_first_event_rate]], that cohort's report should lead with calibration and treat discrimination as the secondary view; this report presented discrimination before calibration because the observed event rate on the evaluation split was at or above that bound, and the ordering should follow the cohort rather than the precedent.
When a cohort crosses any of these declared bounds, or drifts toward one persistently across consecutive reports without crossing it, the escalation path should be an investigation of the cause followed by consideration of overlays, adjustment, recalibration, or redevelopment [[reg:SR26-2:V.1.b]].
The monitoring reports themselves should carry indicators of model performance and of the limitations named here, so that a reader of the output sees the caveats alongside the numbers [[reg:SR26-2:V]].
Several things this validation could not cover fall to monitoring instead.
The first is an external benchmark: the champion-versus-challenger comparison reported earlier in this report is bounded by the development data, and what monitoring adds is a comparison against an external or vendor reference — a credit bureau score or a vendor default model scored on the same production cohort — whose discrepancies against this model should be investigated for source and degree rather than read as error on either side [[reg:SR11-7:V.1.b]].
Where that reference is a third-party product, the plan should also confirm that the vendor's own performance monitoring and disclosure continue to reach the institution, and should assess the vendor's development data for representativeness of this portfolio [[reg:SR11-7:V.2]].
The second is behaviour on vintages originated after the development window, including macroeconomic conditions and product or policy changes with no analogue in the data this validation examined; back-testing on those vintages at an observation frequency matching the performance window is the instrument for it.
The third is sub-population behaviour that appears only in production, including segments too thin in the evaluation split to read reliably, which the plan should track by reporting rank-ordering and calibration by segment rather than on the portfolio alone.
The fourth is overrides, where model output is ignored, altered, or reversed by users: this validation examined scored outputs, so the plan should log overrides, track their realised performance, and treat a rising override rate or a systematic improvement from overriding as a signal that revision is warranted.
The fifth is implementation and data-feed integrity in the production environment, which process verification should confirm on an ongoing basis by checking that inputs remain accurate, complete, and consistent with the model's purpose and design, and that code changes are controlled and auditable.
Finally, the scope and frequency proposed here should be revisited at each annual review, since the appropriate cadence depends on the materiality of the model, the pace of change in the portfolio, and the availability of new data or modelling approaches.

## Appendix A — Claims

Grounding precision 1.0000 before repair (212 of 212 claims verified) and 1.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 16/16; conceptual_soundness 48/48; data_integrity 42/42; outcomes 68/68; sensitivity 14/14; findings 14/14; monitoring 10/10.

Developer claims: The package declares 2 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). See Appendix D.

Excluded numeric tokens (not claims): citation_hash (2ad8d1a5, 2510d49d, 2193cf5f, 64fcf14d); regulatory_section_id (SR26-2:V, SR26-2:V.1.a, SR26-2:IV.1, SR26-2:V.1.b); finding_id (F-001, F-002); package_version (1.0); extractor_returned_excluded_token (1.0, 6.0, 2.0, 1).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The packaged subject was executed as delivered and its perfo… | 300 | ratio | runtime.max_seconds |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 2 | summary | The development split holds 3500 rows and the held-out test… | 3500 | count | n | train | eq | `[[art:2510d49d:profile.train.n]]` | verified | 3500 |
| 3 | summary | The development split holds 3500 rows and the held-out test… | 1500 | count | n | test | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 4 | summary | The development split holds 3500 rows and the held-out test… | 1500 | count | n | test | eq | `[[art:64fcf14d:metrics.test.n]]` | verified | 1500 |
| 5 | summary | The observed event rate on test is 0.2247 , against a mean p… | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 6 | summary | The observed event rate on test is 0.2247 , against a mean p… | 0.2127 | ratio | mean_predicted | test | eq | `[[art:5cd71007:metrics.test.mean_predicted]]` | verified | 0.212652548 |
| 7 | summary | Discrimination on test is 0.7446 , above the declared floor… | 0.7446 | ratio | auc | test | eq | `[[art:21514080:metrics.test.auc]]` | verified | 0.7446438276 |
| 8 | summary | Discrimination on test is 0.7446 , above the declared floor… | 0.7 | ratio | auc | test | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 9 | summary | Discrimination on test is 0.7446 , above the declared floor… | 0.7584 | ratio | auc | train | eq | `[[art:14b38a2b:metrics.train.auc]]` | verified | 0.7584356677 |
| 10 | summary | The Brier score on test is 0.1494 , below the declared ceili… | 0.1494 | ratio | brier | test | eq | `[[art:61f24b2a:metrics.test.brier]]` | verified | 0.1494192524 |
| 11 | summary | The Brier score on test is 0.1494 , below the declared ceili… | 0.2 | ratio | brier | test | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 12 | summary | The calibration slope on test is 0.9778 , inside the declare… | 0.9778 | ratio | calibration_slope | test | eq | `[[art:c07e2c62:calibration_slope.test]]` | verified | 0.9778208366 |
| 13 | summary | The calibration slope on test is 0.9778 , inside the declare… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 14 | summary | The calibration slope on test is 0.9778 , inside the declare… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 15 | summary | The largest train-to-test population stability index, the sc… | 0.03973 | ratio | psi |  | eq | `[[art:9dec5a22:psi.max]]` | verified | 0.03973352816 |
| 16 | summary | The largest train-to-test population stability index, the sc… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 17 | conceptual_soundness | The champion is a linear, one-coefficient-per-feature scorin… | -1.396 | ratio | intercept |  | eq | `[[art:74c10f15:run.model_summary#intercept]]` | verified | -1.395828048 |
| 18 | conceptual_soundness | The champion is a linear, one-coefficient-per-feature scorin… | 3500 | count | n_train | train | eq | `[[art:74c10f15:run.model_summary#n_train]]` | verified | 3500 |
| 19 | conceptual_soundness | The feature inventory carries 12 features in total, of which… | 12 | count | n |  | eq | `[[art:abbb748e:run.features#n]]` | verified | 12 |
| 20 | conceptual_soundness | The feature inventory carries 12 features in total, of which… | 2 | count | at_origination |  | eq | `[[art:abbb748e:run.features#at_origination]]` | verified | 2 |
| 21 | conceptual_soundness | The feature inventory carries 12 features in total, of which… | 10 | count | before_period_start |  | eq | `[[art:abbb748e:run.features#before_period_start]]` | verified | 10 |
| 22 | conceptual_soundness | No feature is dated to the performance period itself, at 0 ,… | 0 | count | during_period |  | eq | `[[art:abbb748e:run.features#during_period]]` | verified | 0 |
| 23 | conceptual_soundness | No feature is dated to the performance period itself, at 0 ,… | 0 | count | after_outcome |  | eq | `[[art:abbb748e:run.features#after_outcome]]` | verified | 0 |
| 24 | conceptual_soundness | The developer's own collinearity screen removed two features… | 10 | ratio | vif_threshold |  | eq | `[[art:74c10f15:run.model_summary#vif_threshold]]` | verified | 10 |
| 25 | conceptual_soundness | The balance level at the last observed month was removed at… | 160.9 | ratio | vif |  | eq | `[[art:74c10f15:run.model_summary#removed.bill_last.vif]]` | verified | 160.888514 |
| 26 | conceptual_soundness | The balance level at the last observed month was removed at… | 36.36 | ratio | vif |  | eq | `[[art:74c10f15:run.model_summary#removed.utilisation_mean_6m.vif]]` | verified | 36.356335 |
| 27 | conceptual_soundness | The largest coefficient by magnitude is on the most recent d… | 0.7334 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.delinq_last.value]]` | verified | 0.7334219534 |
| 28 | conceptual_soundness | The next largest are the six-month mean bill level at -0.372… | -0.3726 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.bill_mean_6m.value]]` | verified | -0.3726281079 |
| 29 | conceptual_soundness | The next largest are the six-month mean bill level at -0.372… | -0.3554 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.pay_ratio_mean_6m.value]]` | verified | -0.3553721566 |
| 30 | conceptual_soundness | Utilisation enters positively at 0.2662 , which matches the… | 0.2662 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.utilisation.value]]` | verified | 0.2662083574 |
| 31 | conceptual_soundness | Utilisation enters positively at 0.2662 , which matches the… | -0.2225 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.bill_trend_6m.value]]` | verified | -0.2224749257 |
| 32 | conceptual_soundness | The remaining coefficients are smaller: the delinquency coun… | 0.1226 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.delinq_count_6m.value]]` | verified | 0.1225797828 |
| 33 | conceptual_soundness | The remaining coefficients are smaller: the delinquency coun… | 0.1026 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.pay_ratio_last.value]]` | verified | 0.1025909773 |
| 34 | conceptual_soundness | The remaining coefficients are smaller: the delinquency coun… | 0.07266 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.limit_bal.value]]` | verified | 0.07265585996 |
| 35 | conceptual_soundness | The remaining coefficients are smaller: the delinquency coun… | -0.06726 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.age.value]]` | verified | -0.06725800744 |
| 36 | conceptual_soundness | The remaining coefficients are smaller: the delinquency coun… | -0.03221 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.delinq_max_6m.value]]` | verified | -0.03221440242 |
| 37 | conceptual_soundness | Each fitted sign was compared with the direction of that fea… | 3 | count | n_disagreements | train | eq | `[[art:e223cd4a:sign_check.n_disagreements]]` | verified | 3 |
| 38 | conceptual_soundness | The credit limit is fitted positive at 1 while its own direc… | 1 | ratio | coef_sign |  | eq | `[[art:6af6aef2:sign_check.limit_bal.coef_sign]]` | verified | 1 |
| 39 | conceptual_soundness | The credit limit is fitted positive at 1 while its own direc… | -1 | ratio | univariate_direction | train | eq | `[[art:56d284d6:sign_check.limit_bal.univariate_direction]]` | verified | -1 |
| 40 | conceptual_soundness | The credit limit is fitted positive at 1 while its own direc… | 0 | ratio | agrees |  | eq | `[[art:0278aad1:sign_check.limit_bal.agrees]]` | verified | 0 |
| 41 | conceptual_soundness | The credit limit is fitted positive at 1 while its own direc… | 0.07266 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.limit_bal.value]]` | verified | 0.07265585996 |
| 42 | conceptual_soundness | The last payment ratio is fitted positive at 1 against an ow… | 1 | ratio | coef_sign |  | eq | `[[art:f018263e:sign_check.pay_ratio_last.coef_sign]]` | verified | 1 |
| 43 | conceptual_soundness | The last payment ratio is fitted positive at 1 against an ow… | -1 | ratio | univariate_direction | train | eq | `[[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]]` | verified | -1 |
| 44 | conceptual_soundness | The last payment ratio is fitted positive at 1 against an ow… | 0 | ratio | agrees |  | eq | `[[art:79abee77:sign_check.pay_ratio_last.agrees]]` | verified | 0 |
| 45 | conceptual_soundness | The last payment ratio is fitted positive at 1 against an ow… | -0.3554 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.pay_ratio_mean_6m.value]]` | verified | -0.3553721566 |
| 46 | conceptual_soundness | The six-month maximum delinquency is fitted negative at -1 a… | -1 | ratio | coef_sign |  | eq | `[[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]]` | verified | -1 |
| 47 | conceptual_soundness | The six-month maximum delinquency is fitted negative at -1 a… | 1 | ratio | univariate_direction | train | eq | `[[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]]` | verified | 1 |
| 48 | conceptual_soundness | The six-month maximum delinquency is fitted negative at -1 a… | 0 | ratio | agrees |  | eq | `[[art:c946359c:sign_check.delinq_max_6m.agrees]]` | verified | 0 |
| 49 | conceptual_soundness | The six-month maximum delinquency is fitted negative at -1 a… | -0.03221 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary#coefficients.delinq_max_6m.value]]` | verified | -0.03221440242 |
| 50 | conceptual_soundness | The features whose fitted signs agree with their own directi… | 1 | ratio | agrees |  | eq | `[[art:a8ba9372:sign_check.delinq_last.agrees]]` | verified | 1 |
| 51 | conceptual_soundness | The features whose fitted signs agree with their own directi… | 1 | ratio | agrees |  | eq | `[[art:a337d16b:sign_check.delinq_count_6m.agrees]]` | verified | 1 |
| 52 | conceptual_soundness | The features whose fitted signs agree with their own directi… | 1 | ratio | agrees |  | eq | `[[art:d0c9a130:sign_check.utilisation.agrees]]` | verified | 1 |
| 53 | conceptual_soundness | The features whose fitted signs agree with their own directi… | 1 | ratio | agrees |  | eq | `[[art:7e9a76ca:sign_check.pay_ratio_mean_6m.agrees]]` | verified | 1 |
| 54 | conceptual_soundness | The features whose fitted signs agree with their own directi… | 1 | ratio | agrees |  | eq | `[[art:89279c3b:sign_check.bill_mean_6m.agrees]]` | verified | 1 |
| 55 | conceptual_soundness | The features whose fitted signs agree with their own directi… | 1 | ratio | agrees |  | eq | `[[art:ff3cb24a:sign_check.bill_trend_6m.agrees]]` | verified | 1 |
| 56 | conceptual_soundness | The features whose fitted signs agree with their own directi… | 1 | ratio | agrees |  | eq | `[[art:4116add1:sign_check.age.agrees]]` | verified | 1 |
| 57 | conceptual_soundness | The features whose fitted signs agree with their own directi… | -1 | ratio | coef_sign |  | eq | `[[art:6172eb93:sign_check.age.coef_sign]]` | verified | -1 |
| 58 | conceptual_soundness | The features whose fitted signs agree with their own directi… | -1 | ratio | univariate_direction | train | eq | `[[art:66364583:sign_check.age.univariate_direction]]` | verified | -1 |
| 59 | conceptual_soundness | The challenger reaches an AUC of 0.8249 against the champion… | 0.8249 | ratio | auc | test | eq | `[[art:6db67e77:challenger.auc]]` | verified | 0.8248645808 |
| 60 | conceptual_soundness | The challenger reaches an AUC of 0.8249 against the champion… | 0.7446 | ratio | auc | test | eq | `[[art:21514080:metrics.test.auc]]` | verified | 0.7446438276 |
| 61 | conceptual_soundness | The challenger reaches an AUC of 0.8249 against the champion… | 0.08022 | ratio | delta_auc | test | eq | `[[art:19982ff0:challenger.delta_auc]]` | verified | 0.08022075314 |
| 62 | conceptual_soundness | The bound that decides whether that difference matters is an… | 0.03 | ratio | delta_auc |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 63 | conceptual_soundness | The challenger's Brier score, 0.1248 , is also lower than th… | 0.1248 | ratio | brier | test | eq | `[[art:67796f7f:challenger.brier]]` | verified | 0.1247605055 |
| 64 | conceptual_soundness | The challenger's Brier score, 0.1248 , is also lower than th… | 0.1494 | ratio | brier | test | eq | `[[art:61f24b2a:metrics.test.brier]]` | verified | 0.1494192524 |
| 65 | data_integrity | The training split holds 3500 rows and the test split holds… | 3500 | count | n | train | eq | `[[art:2510d49d:profile.train.n]]` | verified | 3500 |
| 66 | data_integrity | The training split holds 3500 rows and the test split holds… | 1500 | count | n | test | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 67 | data_integrity | The largest missing fraction in the training split is 0 . | 0 | ratio | missing | train | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 68 | data_integrity | The largest missing fraction in the test split is 0.3 . | 0.3 | ratio | missing | test | eq | `[[art:7b5c0c01:profile.test.missing.max]]` | verified | 0.3 |
| 69 | data_integrity | The integrity screen reads the difference in missingness bet… | 0.1 | ratio | missing_gap |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 70 | data_integrity | The largest train-to-test population stability index, the sc… | 0.03973 | ratio | psi |  | eq | `[[art:9dec5a22:psi.max]]` | verified | 0.03973352816 |
| 71 | data_integrity | The largest train-to-test population stability index, the sc… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 72 | data_integrity | The largest train-to-test population stability index, the sc… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 73 | data_integrity | The score carries that maximum, at 0.03973 , so the shift in… | 0.03973 | ratio | psi |  | eq | `[[art:828961f6:psi.y_score]]` | verified | 0.03973352816 |
| 74 | data_integrity | Among the inputs, the stability indices are 0.01095 for limi… | 0.01095 | ratio | psi |  | eq | `[[art:601cdba2:psi.limit_bal]]` | verified | 0.01095273358 |
| 75 | data_integrity | Among the inputs, the stability indices are 0.01095 for limi… | 0.00958 | ratio | psi |  | eq | `[[art:c247a6f2:psi.bill_trend_6m]]` | verified | 0.009579614525 |
| 76 | data_integrity | Among the inputs, the stability indices are 0.01095 for limi… | 0.008124 | ratio | psi |  | eq | `[[art:f9255a0a:psi.age]]` | verified | 0.008124281436 |
| 77 | data_integrity | Among the inputs, the stability indices are 0.01095 for limi… | 0.007124 | ratio | psi |  | eq | `[[art:028e4281:psi.bill_mean_6m]]` | verified | 0.007124196275 |
| 78 | data_integrity | Among the inputs, the stability indices are 0.01095 for limi… | 0.005498 | ratio | psi |  | eq | `[[art:7a82e7f3:psi.delinq_max_6m]]` | verified | 0.005498249408 |
| 79 | data_integrity | The remainder are smaller still, at 0.0055 for pay_ratio_mea… | 0.0055 | ratio | psi |  | eq | `[[art:2c5baeb2:psi.pay_ratio_mean_6m]]` | verified | 0.005500252946 |
| 80 | data_integrity | The remainder are smaller still, at 0.0055 for pay_ratio_mea… | 0.005424 | ratio | psi |  | eq | `[[art:4f6eddcb:psi.pay_ratio_last]]` | verified | 0.005423736698 |
| 81 | data_integrity | The remainder are smaller still, at 0.0055 for pay_ratio_mea… | 0.004244 | ratio | psi |  | eq | `[[art:451e0780:psi.utilisation]]` | verified | 0.0042440485 |
| 82 | data_integrity | The remainder are smaller still, at 0.0055 for pay_ratio_mea… | 0.00285 | ratio | psi |  | eq | `[[art:03bd52e7:psi.delinq_last]]` | verified | 0.002849633848 |
| 83 | data_integrity | The remainder are smaller still, at 0.0055 for pay_ratio_mea… | 0.002069 | ratio | psi |  | eq | `[[art:61491d02:psi.delinq_count_6m]]` | verified | 0.002069275496 |
| 84 | data_integrity | The largest characteristic contribution to the shift in the… | 0.02363 | ratio | csi |  | eq | `[[art:e56cb179:csi.max]]` | verified | 0.02362581795 |
| 85 | data_integrity | The largest characteristic contribution to the shift in the… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 86 | data_integrity | That contribution belongs to delinq_last, at 0.02363 , follo… | 0.02363 | ratio | csi |  | eq | `[[art:5babe364:csi.delinq_last]]` | verified | 0.02362581795 |
| 87 | data_integrity | That contribution belongs to delinq_last, at 0.02363 , follo… | 0.00633 | ratio | csi |  | eq | `[[art:59948e6d:csi.bill_trend_6m]]` | verified | 0.006329590221 |
| 88 | data_integrity | That contribution belongs to delinq_last, at 0.02363 , follo… | 0.004524 | ratio | csi |  | eq | `[[art:5eec4717:csi.pay_ratio_last]]` | verified | 0.004524002665 |
| 89 | data_integrity | That contribution belongs to delinq_last, at 0.02363 , follo… | 0.004042 | ratio | csi |  | eq | `[[art:10f0f9e7:csi.utilisation]]` | verified | 0.004041856699 |
| 90 | data_integrity | The remaining contributions are 0.002449 for delinq_count_6m… | 0.002449 | ratio | csi |  | eq | `[[art:69346f52:csi.delinq_count_6m]]` | verified | 0.002448902116 |
| 91 | data_integrity | The remaining contributions are 0.002449 for delinq_count_6m… | 0.002369 | ratio | csi |  | eq | `[[art:48df6cc9:csi.bill_mean_6m]]` | verified | 0.002369326368 |
| 92 | data_integrity | The remaining contributions are 0.002449 for delinq_count_6m… | 0.001768 | ratio | csi |  | eq | `[[art:f567818e:csi.pay_ratio_mean_6m]]` | verified | 0.001768345794 |
| 93 | data_integrity | The remaining contributions are 0.002449 for delinq_count_6m… | 0.001211 | ratio | csi |  | eq | `[[art:5b77b34b:csi.limit_bal]]` | verified | 0.001211461258 |
| 94 | data_integrity | The remaining contributions are 0.002449 for delinq_count_6m… | 0.0009476 | ratio | csi |  | eq | `[[art:a78e58f6:csi.age]]` | verified | 0.0009475732594 |
| 95 | data_integrity | The remaining contributions are 0.002449 for delinq_count_6m… | 0.0008965 | ratio | csi |  | eq | `[[art:7244960d:csi.delinq_max_6m]]` | verified | 0.0008964784296 |
| 96 | data_integrity | The number of features declared as observed during the perfo… | 0 | count | n_flagged |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 97 | data_integrity | The strongest single feature reaches an area under the curve… | 0.6831 | ratio | auc |  | eq | `[[art:fd829fc4:leakage.target_corr.max_single_feature_auc]]` | verified | 0.6831414154 |
| 98 | data_integrity | The strongest single feature reaches an area under the curve… | 0.9 | ratio | auc |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 99 | data_integrity | On identifiers, the share of test rows whose client_id also… | 0 | ratio | overlap | test | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 100 | data_integrity | On identifiers, the share of test rows whose client_id also… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 101 | data_integrity | On feature vectors, the share of test rows whose feature val… | 0 | ratio | overlap | test | eq | `[[art:0fec8048:leakage.overlap.features]]` | verified | 0 |
| 102 | data_integrity | On feature vectors, the share of test rows whose feature val… | 0.005 | ratio | overlap |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 103 | data_integrity | That duplicate share, the fraction of training rows whose fe… | 0 | ratio | duplicates | train | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 104 | data_integrity | The overall share of test rows whose feature values also app… | 0 | ratio | overlap | test | eq | `[[art:4c9fcd09:leakage.overlap]]` | verified | 0 |
| 105 | data_integrity | The overall share of test rows whose feature values also app… | 0.005 | ratio | overlap |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 106 | data_integrity | The name screen matches 0 feature names against the target-a… | 0 | count | n_matched |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 107 | outcomes | The reason is the observed event rate on the evaluation spli… | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 108 | outcomes | The reason is the observed event rate on the evaluation spli… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 109 | outcomes | \| Observations \| 3500 \| 1500 \| | 3500 | count | n | train | eq | `[[art:564683ee:metrics.train.n]]` | verified | 3500 |
| 110 | outcomes | \| Observations \| 3500 \| 1500 \| | 1500 | count | n | test | eq | `[[art:64fcf14d:metrics.test.n]]` | verified | 1500 |
| 111 | outcomes | \| Event rate \| 0.2246 \| 0.2247 \| | 0.2246 | ratio | event_rate | train | eq | `[[art:133a5ff8:metrics.train.event_rate]]` | verified | 0.2245714286 |
| 112 | outcomes | \| Event rate \| 0.2246 \| 0.2247 \| | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 113 | outcomes | \| AUC \| 0.7584 \| 0.7446 \| | 0.7584 | ratio | auc | train | eq | `[[art:14b38a2b:metrics.train.auc]]` | verified | 0.7584356677 |
| 114 | outcomes | \| AUC \| 0.7584 \| 0.7446 \| | 0.7446 | ratio | auc | test | eq | `[[art:21514080:metrics.test.auc]]` | verified | 0.7446438276 |
| 115 | outcomes | \| Gini \| 0.5169 \| 0.4893 \| | 0.5169 | ratio | gini | train | eq | `[[art:b4da846e:metrics.train.gini]]` | verified | 0.5168713353 |
| 116 | outcomes | \| Gini \| 0.5169 \| 0.4893 \| | 0.4893 | ratio | gini | test | eq | `[[art:6d62a3df:metrics.test.gini]]` | verified | 0.4892876552 |
| 117 | outcomes | \| KS \| 0.4451 \| 0.41 \| | 0.4451 | ratio | ks | train | eq | `[[art:ccc12729:metrics.train.ks]]` | verified | 0.4451397991 |
| 118 | outcomes | \| KS \| 0.4451 \| 0.41 \| | 0.41 | ratio | ks | test | eq | `[[art:2bfec7c8:metrics.test.ks]]` | verified | 0.4100058429 |
| 119 | outcomes | \| Brier \| 0.1489 \| 0.1494 \| | 0.1489 | ratio | brier | train | eq | `[[art:be669a99:metrics.train.brier]]` | verified | 0.1489149059 |
| 120 | outcomes | \| Brier \| 0.1489 \| 0.1494 \| | 0.1494 | ratio | brier | test | eq | `[[art:61f24b2a:metrics.test.brier]]` | verified | 0.1494192524 |
| 121 | outcomes | \| Log loss \| 0.465 \| 0.4684 \| | 0.465 | ratio | logloss | train | eq | `[[art:4f02e465:metrics.train.logloss]]` | verified | 0.4650014911 |
| 122 | outcomes | \| Log loss \| 0.465 \| 0.4684 \| | 0.4684 | ratio | logloss | test | eq | `[[art:92c35262:metrics.test.logloss]]` | verified | 0.4684227558 |
| 123 | outcomes | \| Mean predicted probability \| 0.2246 \| 0.2127 \| | 0.2246 | ratio | mean_predicted | train | eq | `[[art:605cce58:metrics.train.mean_predicted]]` | verified | 0.2246226934 |
| 124 | outcomes | \| Mean predicted probability \| 0.2246 \| 0.2127 \| | 0.2127 | ratio | mean_predicted | test | eq | `[[art:5cd71007:metrics.test.mean_predicted]]` | verified | 0.212652548 |
| 125 | outcomes | \| Share of events in the top two deciles \| 0.4517 \| 0.4688 \| | 0.4517 | ratio | top2_capture | train | eq | `[[art:1d20c762:deciles.train.top2_capture]]` | verified | 0.451653944 |
| 126 | outcomes | \| Share of events in the top two deciles \| 0.4517 \| 0.4688 \| | 0.4688 | ratio | top2_capture | test | eq | `[[art:17d2971c:deciles.test.top2_capture]]` | verified | 0.46884273 |
| 127 | outcomes | Rank-ordering is weaker on the evaluation split than in samp… | 0.7584 | ratio | auc | train | eq | `[[art:14b38a2b:metrics.train.auc]]` | verified | 0.7584356677 |
| 128 | outcomes | Rank-ordering is weaker on the evaluation split than in samp… | 0.7446 | ratio | auc | test | eq | `[[art:21514080:metrics.test.auc]]` | verified | 0.7446438276 |
| 129 | outcomes | The tolerance the review applies to the train-to-test AUC ga… | 0.08 | ratio | auc_gap |  | eq | `[[art:630f28f4:threshold.O1.auc_gap]]` | verified | 0.08 |
| 130 | outcomes | Turning to calibration, the logistic regression of the outco… | 0.9778 | ratio | calibration_slope | test | eq | `[[art:c07e2c62:calibration_slope.test]]` | verified | 0.9778208366 |
| 131 | outcomes | Turning to calibration, the logistic regression of the outco… | 0.8 | ratio | calibration_slope |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 132 | outcomes | Turning to calibration, the logistic regression of the outco… | 1.2 | ratio | calibration_slope |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 133 | outcomes | The corresponding intercept on test is 0.05554 . | 0.05554 | ratio | calibration_intercept | test | eq | `[[art:f4d4ef2b:calibration_intercept.test]]` | verified | 0.05553669436 |
| 134 | outcomes | On train the slope is 1.002 and the intercept is 0.002062 ,… | 1.002 | ratio | calibration_slope | train | eq | `[[art:d02e3091:calibration_slope.train]]` | verified | 1.002102954 |
| 135 | outcomes | On train the slope is 1.002 and the intercept is 0.002062 ,… | 0.002062 | ratio | calibration_intercept | train | eq | `[[art:ed381a81:calibration_intercept.train]]` | verified | 0.002061562686 |
| 136 | outcomes | In level terms, the mean predicted probability on test is 0.… | 0.2127 | ratio | mean_predicted | test | eq | `[[art:5cd71007:metrics.test.mean_predicted]]` | verified | 0.212652548 |
| 137 | outcomes | In level terms, the mean predicted probability on test is 0.… | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 138 | outcomes | The relative gap between the two is 0.05348 , below the tole… | 0.05348 | ratio | mean_rel_gap | test | eq | `[[art:64a3c99e:calibration.mean_rel_gap.test]]` | verified | 0.05347530574 |
| 139 | outcomes | The relative gap between the two is 0.05348 , below the tole… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 140 | outcomes | Comparing the two relative gaps as values rather than as a d… | 0.05348 | ratio | mean_rel_gap | test | eq | `[[art:64a3c99e:calibration.mean_rel_gap.test]]` | verified | 0.05347530574 |
| 141 | outcomes | Comparing the two relative gaps as values rather than as a d… | 0.0002283 | ratio | mean_rel_gap | train | eq | `[[art:53738d45:calibration.mean_rel_gap.train]]` | verified | 0.0002282786273 |
| 142 | outcomes | On train this slice's AUC of 0.761 stands above the split's… | 0.761 | ratio | auc | train | eq | `[[art:aefc6bf2:metrics.train.sub.pay_ratio_last_high.auc]]` | verified | 0.7609527498 |
| 143 | outcomes | On train this slice's AUC of 0.761 stands above the split's… | -0.002517 | ratio | auc_gap | train | eq | `[[art:114f7785:metrics.train.sub.pay_ratio_last_high.auc_gap]]` | verified | -0.00251708216 |
| 144 | outcomes | On train this slice's AUC of 0.761 stands above the split's… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 145 | outcomes | On test its AUC of 0.7683 likewise stands above the split's… | 0.7683 | ratio | auc | test | eq | `[[art:e011e41a:metrics.test.sub.pay_ratio_last_high.auc]]` | verified | 0.7683446712 |
| 146 | outcomes | On test its AUC of 0.7683 likewise stands above the split's… | -0.0237 | ratio | auc_gap | test | eq | `[[art:2e0fdc88:metrics.test.sub.pay_ratio_last_high.auc_gap]]` | verified | -0.02370084359 |
| 147 | outcomes | On test its AUC of 0.7683 likewise stands above the split's… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 148 | outcomes | The slice holds 0.5 of train on 1750 rows and 0.35 of test o… | 0.5 | ratio | share | train | eq | `[[art:885c90a0:metrics.train.sub.pay_ratio_last_high.share]]` | verified | 0.5 |
| 149 | outcomes | The slice holds 0.5 of train on 1750 rows and 0.35 of test o… | 1750 | count | n | train | eq | `[[art:6caa2b34:metrics.train.sub.pay_ratio_last_high.n]]` | verified | 1750 |
| 150 | outcomes | The slice holds 0.5 of train on 1750 rows and 0.35 of test o… | 0.35 | ratio | share | test | eq | `[[art:a02902d1:metrics.test.sub.pay_ratio_last_high.share]]` | verified | 0.35 |
| 151 | outcomes | The slice holds 0.5 of train on 1750 rows and 0.35 of test o… | 525 | count | n | test | eq | `[[art:01944702:metrics.test.sub.pay_ratio_last_high.n]]` | verified | 525 |
| 152 | outcomes | The slice holds 0.5 of train on 1750 rows and 0.35 of test o… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 153 | outcomes | The slice holds 0.5 of train on 1750 rows and 0.35 of test o… | 0.95 | ratio | slice_max_share |  | eq | `[[art:a928a05c:threshold.O1.slice_max_share]]` | verified | 0.95 |
| 154 | outcomes | On level, mean predicted on this slice of test is 0.1949 aga… | 0.1949 | ratio | mean_predicted | test | eq | `[[art:9f99173b:metrics.test.sub.pay_ratio_last_high.mean_predicted]]` | verified | 0.1949101214 |
| 155 | outcomes | On level, mean predicted on this slice of test is 0.1949 aga… | 0.2 | ratio | event_rate | test | eq | `[[art:12a48470:metrics.test.sub.pay_ratio_last_high.event_rate]]` | verified | 0.2 |
| 156 | outcomes | On level, mean predicted on this slice of test is 0.1949 aga… | 0.02545 | ratio | mean_rel_gap | test | eq | `[[art:0b1e3e54:metrics.test.sub.pay_ratio_last_high.mean_rel_gap]]` | verified | 0.02544939285 |
| 157 | outcomes | On train this slice's AUC of 0.7585 sits level with the spli… | 0.7585 | ratio | auc | train | eq | `[[art:8ceea245:metrics.train.sub.pay_ratio_last_low.auc]]` | verified | 0.7584807658 |
| 158 | outcomes | On train this slice's AUC of 0.7585 sits level with the spli… | -4.51e-05 | ratio | auc_gap | train | eq | `[[art:1eebca8c:metrics.train.sub.pay_ratio_last_low.auc_gap]]` | verified | -4.509816242e-05 |
| 159 | outcomes | On train this slice's AUC of 0.7585 sits level with the spli… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 160 | outcomes | On test its AUC of 0.7028 falls below the split's own by 0.0… | 0.7028 | ratio | auc | test | eq | `[[art:e2d27a4b:metrics.test.sub.pay_ratio_last_low.auc]]` | verified | 0.702752718 |
| 161 | outcomes | On test its AUC of 0.7028 falls below the split's own by 0.0… | 0.04189 | ratio | auc_gap | test | eq | `[[art:59764abf:metrics.test.sub.pay_ratio_last_low.auc_gap]]` | verified | 0.04189110959 |
| 162 | outcomes | On test its AUC of 0.7028 falls below the split's own by 0.0… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 163 | outcomes | Comparing the two halves on test by their AUC shortfalls as… | 0.04189 | ratio | auc_gap | test | eq | `[[art:59764abf:metrics.test.sub.pay_ratio_last_low.auc_gap]]` | verified | 0.04189110959 |
| 164 | outcomes | Comparing the two halves on test by their AUC shortfalls as… | -0.0237 | ratio | auc_gap | test | eq | `[[art:2e0fdc88:metrics.test.sub.pay_ratio_last_high.auc_gap]]` | verified | -0.02370084359 |
| 165 | outcomes | The slice holds 0.5 of train on 1750 rows and 0.35 of test o… | 0.5 | ratio | share | train | eq | `[[art:7ffa8f3d:metrics.train.sub.pay_ratio_last_low.share]]` | verified | 0.5 |
| 166 | outcomes | The slice holds 0.5 of train on 1750 rows and 0.35 of test o… | 1750 | count | n | train | eq | `[[art:3edfedd7:metrics.train.sub.pay_ratio_last_low.n]]` | verified | 1750 |
| 167 | outcomes | The slice holds 0.5 of train on 1750 rows and 0.35 of test o… | 0.35 | ratio | share | test | eq | `[[art:30c17bde:metrics.test.sub.pay_ratio_last_low.share]]` | verified | 0.35 |
| 168 | outcomes | The slice holds 0.5 of train on 1750 rows and 0.35 of test o… | 525 | count | n | test | eq | `[[art:07df56e1:metrics.test.sub.pay_ratio_last_low.n]]` | verified | 525 |
| 169 | outcomes | The slice holds 0.5 of train on 1750 rows and 0.35 of test o… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 170 | outcomes | The slice holds 0.5 of train on 1750 rows and 0.35 of test o… | 0.95 | ratio | slice_max_share |  | eq | `[[art:a928a05c:threshold.O1.slice_max_share]]` | verified | 0.95 |
| 171 | outcomes | On level, mean predicted on this slice of test is 0.2565 aga… | 0.2565 | ratio | mean_predicted | test | eq | `[[art:a258ff37:metrics.test.sub.pay_ratio_last_low.mean_predicted]]` | verified | 0.256481542 |
| 172 | outcomes | On level, mean predicted on this slice of test is 0.2565 aga… | 0.2514 | ratio | event_rate | test | eq | `[[art:f772d438:metrics.test.sub.pay_ratio_last_low.event_rate]]` | verified | 0.2514285714 |
| 173 | outcomes | On level, mean predicted on this slice of test is 0.2565 aga… | 0.0201 | ratio | mean_rel_gap | test | eq | `[[art:5cbda8a4:metrics.test.sub.pay_ratio_last_low.mean_rel_gap]]` | verified | 0.0200970422 |
| 174 | outcomes | On level, mean predicted on this slice of test is 0.2565 aga… | 0.05348 | ratio | mean_rel_gap | test | eq | `[[art:64a3c99e:calibration.mean_rel_gap.test]]` | verified | 0.05347530574 |
| 175 | sensitivity | The largest variance inflation factor across the retained fe… | 7.295 | ratio | vif |  | eq | `[[art:9ae7c45b:vif.max]]` | verified | 7.295299885 |
| 176 | sensitivity | The largest variance inflation factor across the retained fe… | 10 | ratio | vif |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 177 | sensitivity | Belsley's condition number of the column-standardised design… | 5.547 | ratio | condition_number |  | eq | `[[art:e41b9562:condition_number]]` | verified | 5.546934633 |
| 178 | sensitivity | Belsley's condition number of the column-standardised design… | 30 | ratio | condition_number |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 179 | sensitivity | - The factor for bill_mean_6m is 7.295 . | 7.295 | ratio | vif | train | eq | `[[art:f0a2f865:vif.bill_mean_6m]]` | verified | 7.295299885 |
| 180 | sensitivity | - The factor for pay_ratio_last is 7.264 . | 7.264 | ratio | vif | train | eq | `[[art:c2de8dfe:vif.pay_ratio_last]]` | verified | 7.264342098 |
| 181 | sensitivity | - The factor for pay_ratio_mean_6m is 7.259 . | 7.259 | ratio | vif | train | eq | `[[art:e39c3e82:vif.pay_ratio_mean_6m]]` | verified | 7.25926398 |
| 182 | sensitivity | - The factor for limit_bal is 4.803 . | 4.803 | ratio | vif | train | eq | `[[art:ddfdcc3c:vif.limit_bal]]` | verified | 4.803401129 |
| 183 | sensitivity | - The factor for utilisation is 3.215 . | 3.215 | ratio | vif | train | eq | `[[art:536fdb6f:vif.utilisation]]` | verified | 3.215148369 |
| 184 | sensitivity | - The factor for delinq_count_6m is 2.561 . | 2.561 | ratio | vif | train | eq | `[[art:38974def:vif.delinq_count_6m]]` | verified | 2.561484187 |
| 185 | sensitivity | - The factor for delinq_max_6m is 2.408 . | 2.408 | ratio | vif | train | eq | `[[art:71aaaf11:vif.delinq_max_6m]]` | verified | 2.40773 |
| 186 | sensitivity | - The factor for delinq_last is 1.412 . | 1.412 | ratio | vif | train | eq | `[[art:48733638:vif.delinq_last]]` | verified | 1.411555667 |
| 187 | sensitivity | - The factor for bill_trend_6m is 1.201 . | 1.201 | ratio | vif | train | eq | `[[art:9356a256:vif.bill_trend_6m]]` | verified | 1.201449441 |
| 188 | sensitivity | - The factor for age is 1.002 . | 1.002 | ratio | vif | train | eq | `[[art:74c06cad:vif.age]]` | verified | 1.001957997 |
| 189 | findings | The per-feature missingness of the two splits is set out bel… | 0.1 | ratio | missing_gap |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 190 | findings | A history-gradient-boosting challenger reaches an AUC of 0.8… | 0.8249 | ratio | auc | test | eq | `[[art:6db67e77:challenger.auc]]` | verified | 0.8248645808 |
| 191 | findings | A history-gradient-boosting challenger reaches an AUC of 0.8… | 0.7446 | ratio | auc | test | eq | `[[art:21514080:metrics.test.auc]]` | verified | 0.7446438276 |
| 192 | findings | Expressed as the difference between the two, and not as thei… | 0.08022 | ratio | delta_auc | test | eq | `[[art:19982ff0:challenger.delta_auc]]` | verified | 0.08022075314 |
| 193 | findings | Expressed as the difference between the two, and not as thei… | 0.03 | ratio | delta_auc |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 194 | findings | Within the segment on which `delinq_max_6m` is fitted with c… | -1 | ratio | coef_sign |  | eq | `[[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]]` | verified | -1 |
| 195 | findings | Within the segment on which `delinq_max_6m` is fitted with c… | 1 | ratio | univariate_direction |  | eq | `[[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]]` | verified | 1 |
| 196 | findings | Within the segment on which `delinq_max_6m` is fitted with c… | 0 | ratio | agrees |  | eq | `[[art:c946359c:sign_check.delinq_max_6m.agrees]]` | verified | 0 |
| 197 | findings | Within the segment on which `limit_bal` is fitted with coeff… | 1 | ratio | coef_sign |  | eq | `[[art:6af6aef2:sign_check.limit_bal.coef_sign]]` | verified | 1 |
| 198 | findings | Within the segment on which `limit_bal` is fitted with coeff… | -1 | ratio | univariate_direction |  | eq | `[[art:56d284d6:sign_check.limit_bal.univariate_direction]]` | verified | -1 |
| 199 | findings | Within the segment on which `limit_bal` is fitted with coeff… | 0 | ratio | agrees |  | eq | `[[art:0278aad1:sign_check.limit_bal.agrees]]` | verified | 0 |
| 200 | findings | Within the segment on which `pay_ratio_last` is fitted with… | 1 | ratio | coef_sign |  | eq | `[[art:f018263e:sign_check.pay_ratio_last.coef_sign]]` | verified | 1 |
| 201 | findings | Within the segment on which `pay_ratio_last` is fitted with… | -1 | ratio | univariate_direction |  | eq | `[[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]]` | verified | -1 |
| 202 | findings | Within the segment on which `pay_ratio_last` is fitted with… | 0 | ratio | agrees |  | eq | `[[art:79abee77:sign_check.pay_ratio_last.agrees]]` | verified | 0 |
| 203 | monitoring | Rank-ordering on scored production cohorts should be reporte… | 0.7 | ratio | auc | test | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 204 | monitoring | Rank-ordering on scored production cohorts should be reporte… | 0.7446 | ratio | auc | test | eq | `[[art:21514080:metrics.test.auc]]` | verified | 0.7446438276 |
| 205 | monitoring | Probability accuracy should be reported on the same monthly… | 0.2 | ratio | brier | test | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 206 | monitoring | Probability accuracy should be reported on the same monthly… | 0.1494 | ratio | brier | test | eq | `[[art:61f24b2a:metrics.test.brier]]` | verified | 0.1494192524 |
| 207 | monitoring | Calibration on the logit scale should be reported quarterly,… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 208 | monitoring | Calibration on the logit scale should be reported quarterly,… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 209 | monitoring | Calibration on the logit scale should be reported quarterly,… | 0.9778 | ratio | calibration_slope | test | eq | `[[art:c07e2c62:calibration_slope.test]]` | verified | 0.9778208366 |
| 210 | monitoring | Input and score stability should be reported monthly against… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 211 | monitoring | Input and score stability should be reported monthly against… | 0.03973 | ratio | psi |  | eq | `[[art:9dec5a22:psi.max]]` | verified | 0.03973352816 |
| 212 | monitoring | Where a monitoring cohort's observed event rate falls below… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |

## Appendix B — Artifact index

The store holds 210 artifacts; the 147 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `calibration.mean_rel_gap.test` | `64a3c99e` | scalar | 0.05347530574 | mean predicted against observed on test, relative |
| `calibration.mean_rel_gap.train` | `53738d45` | scalar | 0.0002282786273 | mean predicted against observed on train, relative |
| `calibration.test` | `f03c533a` | table | table, 10 rows | calibration by decile of predicted probability on test |
| `calibration_intercept.test` | `f4d4ef2b` | scalar | 0.05553669436 | logistic regression of the outcome on logit(p) on test: the intercept |
| `calibration_intercept.train` | `ed381a81` | scalar | 0.002061562686 | logistic regression of the outcome on logit(p) on train: the intercept |
| `calibration_slope.test` | `c07e2c62` | scalar | 0.9778208366 | logistic regression of the outcome on logit(p) on test: the slope |
| `calibration_slope.train` | `d02e3091` | scalar | 1.002102954 | logistic regression of the outcome on logit(p) on train: the slope |
| `challenger.auc` | `6db67e77` | scalar | 0.8248645808 | the challenger's AUC on test |
| `challenger.brier` | `67796f7f` | scalar | 0.1247605055 | the challenger's Brier score on test |
| `challenger.delta_auc` | `19982ff0` | scalar | 0.08022075314 | the challenger's AUC on test minus the champion's |
| `condition_number` | `e41b9562` | scalar | 5.546934633 | Belsley's condition number of the column-standardised design |
| `csi.age` | `a78e58f6` | scalar | 0.0009475732594 | CSI of age: its contribution to the shift in the linear predictor |
| `csi.bill_mean_6m` | `48df6cc9` | scalar | 0.002369326368 | CSI of bill_mean_6m: its contribution to the shift in the linear predictor |
| `csi.bill_trend_6m` | `59948e6d` | scalar | 0.006329590221 | CSI of bill_trend_6m: its contribution to the shift in the linear predictor |
| `csi.delinq_count_6m` | `69346f52` | scalar | 0.002448902116 | CSI of delinq_count_6m: its contribution to the shift in the linear predictor |
| `csi.delinq_last` | `5babe364` | scalar | 0.02362581795 | CSI of delinq_last: its contribution to the shift in the linear predictor |
| `csi.delinq_max_6m` | `7244960d` | scalar | 0.0008964784296 | CSI of delinq_max_6m: its contribution to the shift in the linear predictor |
| `csi.limit_bal` | `5b77b34b` | scalar | 0.001211461258 | CSI of limit_bal: its contribution to the shift in the linear predictor |
| `csi.max` | `e56cb179` | scalar | 0.02362581795 | the largest characteristic stability index |
| `csi.pay_ratio_last` | `5eec4717` | scalar | 0.004524002665 | CSI of pay_ratio_last: its contribution to the shift in the linear predictor |
| `csi.pay_ratio_mean_6m` | `f567818e` | scalar | 0.001768345794 | CSI of pay_ratio_mean_6m: its contribution to the shift in the linear predictor |
| `csi.utilisation` | `10f0f9e7` | scalar | 0.004041856699 | CSI of utilisation: its contribution to the shift in the linear predictor |
| `deciles.test` | `c922f3a3` | table | table, 10 rows | decile separation on test; decile 1 holds the highest probabilities |
| `deciles.test.top2_capture` | `17d2971c` | scalar | 0.46884273 | share of test events in the top two deciles |
| `deciles.train.top2_capture` | `1d20c762` | scalar | 0.451653944 | share of train events in the top two deciles |
| `leakage.duplicates.train` | `4474c227` | scalar | 0 | share of train rows whose feature values are not unique within train |
| `leakage.name_screen.n_matched` | `407e62be` | scalar | 0 | feature names matching the target-adjacent lexicon |
| `leakage.overlap` | `4c9fcd09` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.features` | `0fec8048` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.ids` | `63d37fc5` | scalar | 0 | share of test rows whose ['client_id'] also identify a row of train |
| `leakage.target_corr.max_single_feature_auc` | `fd829fc4` | scalar | 0.6831414154 | the AUC of the strongest single feature |
| `leakage.timing.n_flagged` | `742bcd24` | scalar | 0 | features declared during_period or after_outcome |
| `metrics.test.auc` | `21514080` | scalar | 0.7446438276 | auc on test, recomputed by quaestor |
| `metrics.test.brier` | `61f24b2a` | scalar | 0.1494192524 | brier on test, recomputed by quaestor |
| `metrics.test.event_rate` | `9209d200` | scalar | 0.2246666667 | event_rate on test, recomputed by quaestor |
| `metrics.test.gini` | `6d62a3df` | scalar | 0.4892876552 | gini on test, recomputed by quaestor |
| `metrics.test.ks` | `2bfec7c8` | scalar | 0.4100058429 | ks on test, recomputed by quaestor |
| `metrics.test.logloss` | `92c35262` | scalar | 0.4684227558 | logloss on test, recomputed by quaestor |
| `metrics.test.mean_predicted` | `5cd71007` | scalar | 0.212652548 | mean_predicted on test, recomputed by quaestor |
| `metrics.test.n` | `64fcf14d` | scalar | 1500 | n on test, recomputed by quaestor |
| `metrics.test.sub.pay_ratio_last_high` | `96288929` | table | table, 10 rows | every metric on the pay_ratio_last above_median slice of test |
| `metrics.test.sub.pay_ratio_last_high.auc` | `e011e41a` | scalar | 0.7683446712 | auc on the pay_ratio_last above_median slice of test |
| `metrics.test.sub.pay_ratio_last_high.auc_gap` | `2e0fdc88` | scalar | -0.02370084359 | how far AUC on the pay_ratio_last above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.pay_ratio_last_high.event_rate` | `12a48470` | scalar | 0.2 | event_rate on the pay_ratio_last above_median slice of test |
| `metrics.test.sub.pay_ratio_last_high.mean_predicted` | `9f99173b` | scalar | 0.1949101214 | mean_predicted on the pay_ratio_last above_median slice of test |
| `metrics.test.sub.pay_ratio_last_high.mean_rel_gap` | `0b1e3e54` | scalar | 0.02544939285 | mean predicted against observed on the pay_ratio_last above_median slice of test, relative |
| `metrics.test.sub.pay_ratio_last_high.n` | `01944702` | scalar | 525 | n on the pay_ratio_last above_median slice of test |
| `metrics.test.sub.pay_ratio_last_high.share` | `a02902d1` | scalar | 0.35 | the share of test the pay_ratio_last above_median slice holds |
| `metrics.test.sub.pay_ratio_last_low` | `0f69d233` | table | table, 10 rows | every metric on the pay_ratio_last below_median slice of test |
| `metrics.test.sub.pay_ratio_last_low.auc` | `e2d27a4b` | scalar | 0.702752718 | auc on the pay_ratio_last below_median slice of test |
| `metrics.test.sub.pay_ratio_last_low.auc_gap` | `59764abf` | scalar | 0.04189110959 | how far AUC on the pay_ratio_last below_median slice of test falls below AUC on all of test |
| `metrics.test.sub.pay_ratio_last_low.event_rate` | `f772d438` | scalar | 0.2514285714 | event_rate on the pay_ratio_last below_median slice of test |
| `metrics.test.sub.pay_ratio_last_low.mean_predicted` | `a258ff37` | scalar | 0.256481542 | mean_predicted on the pay_ratio_last below_median slice of test |
| `metrics.test.sub.pay_ratio_last_low.mean_rel_gap` | `5cbda8a4` | scalar | 0.0200970422 | mean predicted against observed on the pay_ratio_last below_median slice of test, relative |
| `metrics.test.sub.pay_ratio_last_low.n` | `07df56e1` | scalar | 525 | n on the pay_ratio_last below_median slice of test |
| `metrics.test.sub.pay_ratio_last_low.share` | `30c17bde` | scalar | 0.35 | the share of test the pay_ratio_last below_median slice holds |
| `metrics.train.auc` | `14b38a2b` | scalar | 0.7584356677 | auc on train, recomputed by quaestor |
| `metrics.train.brier` | `be669a99` | scalar | 0.1489149059 | brier on train, recomputed by quaestor |
| `metrics.train.event_rate` | `133a5ff8` | scalar | 0.2245714286 | event_rate on train, recomputed by quaestor |
| `metrics.train.gini` | `b4da846e` | scalar | 0.5168713353 | gini on train, recomputed by quaestor |
| `metrics.train.ks` | `ccc12729` | scalar | 0.4451397991 | ks on train, recomputed by quaestor |
| `metrics.train.logloss` | `4f02e465` | scalar | 0.4650014911 | logloss on train, recomputed by quaestor |
| `metrics.train.mean_predicted` | `605cce58` | scalar | 0.2246226934 | mean_predicted on train, recomputed by quaestor |
| `metrics.train.n` | `564683ee` | scalar | 3500 | n on train, recomputed by quaestor |
| `metrics.train.sub.pay_ratio_last_high` | `432527b1` | table | table, 10 rows | every metric on the pay_ratio_last above_median slice of train |
| `metrics.train.sub.pay_ratio_last_high.auc` | `aefc6bf2` | scalar | 0.7609527498 | auc on the pay_ratio_last above_median slice of train |
| `metrics.train.sub.pay_ratio_last_high.auc_gap` | `114f7785` | scalar | -0.00251708216 | how far AUC on the pay_ratio_last above_median slice of train falls below AUC on all of train |
| `metrics.train.sub.pay_ratio_last_high.n` | `6caa2b34` | scalar | 1750 | n on the pay_ratio_last above_median slice of train |
| `metrics.train.sub.pay_ratio_last_high.share` | `885c90a0` | scalar | 0.5 | the share of train the pay_ratio_last above_median slice holds |
| `metrics.train.sub.pay_ratio_last_low` | `70335bfe` | table | table, 10 rows | every metric on the pay_ratio_last below_median slice of train |
| `metrics.train.sub.pay_ratio_last_low.auc` | `8ceea245` | scalar | 0.7584807658 | auc on the pay_ratio_last below_median slice of train |
| `metrics.train.sub.pay_ratio_last_low.auc_gap` | `1eebca8c` | scalar | -4.509816242e-05 | how far AUC on the pay_ratio_last below_median slice of train falls below AUC on all of train |
| `metrics.train.sub.pay_ratio_last_low.n` | `3edfedd7` | scalar | 1750 | n on the pay_ratio_last below_median slice of train |
| `metrics.train.sub.pay_ratio_last_low.share` | `7ffa8f3d` | scalar | 0.5 | the share of train the pay_ratio_last below_median slice holds |
| `profile.test.missing` | `2dbb3988` | table | table, 10 rows | missingness per feature in test |
| `profile.test.missing.max` | `7b5c0c01` | scalar | 0.3 | the largest missing fraction in test |
| `profile.test.n` | `2193cf5f` | scalar | 1500 | rows in test |
| `profile.train.missing` | `0c6f5686` | table | table, 10 rows | missingness per feature in train |
| `profile.train.missing.max` | `050a3099` | scalar | 0 | the largest missing fraction in train |
| `profile.train.n` | `2510d49d` | scalar | 3500 | rows in train |
| `psi.age` | `f9255a0a` | scalar | 0.008124281436 | PSI of age between train and test |
| `psi.bill_mean_6m` | `028e4281` | scalar | 0.007124196275 | PSI of bill_mean_6m between train and test |
| `psi.bill_trend_6m` | `c247a6f2` | scalar | 0.009579614525 | PSI of bill_trend_6m between train and test |
| `psi.delinq_count_6m` | `61491d02` | scalar | 0.002069275496 | PSI of delinq_count_6m between train and test |
| `psi.delinq_last` | `03bd52e7` | scalar | 0.002849633848 | PSI of delinq_last between train and test |
| `psi.delinq_max_6m` | `7a82e7f3` | scalar | 0.005498249408 | PSI of delinq_max_6m between train and test |
| `psi.limit_bal` | `601cdba2` | scalar | 0.01095273358 | PSI of limit_bal between train and test |
| `psi.max` | `9dec5a22` | scalar | 0.03973352816 | the largest train-to-test PSI, score included |
| `psi.pay_ratio_last` | `4f6eddcb` | scalar | 0.005423736698 | PSI of pay_ratio_last between train and test |
| `psi.pay_ratio_mean_6m` | `2c5baeb2` | scalar | 0.005500252946 | PSI of pay_ratio_mean_6m between train and test |
| `psi.utilisation` | `451e0780` | scalar | 0.0042440485 | PSI of utilisation between train and test |
| `psi.y_score` | `828961f6` | scalar | 0.03973352816 | PSI of the score between train and test |
| `rule.calibration_first_event_rate` | `42f1351e` | scalar | 0.05 | the event rate below which the report puts calibration before discrimination |
| `run.features` | `abbb748e` | json | json | the subject's features.json |
| `run.model_summary` | `74c10f15` | json | json | the subject's model_summary.json |
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |
| `sign_check.age.agrees` | `4116add1` | scalar | 1 | 1 when the fitted sign on age agrees with its univariate direction, 0 when it does not |
| `sign_check.age.coef_sign` | `6172eb93` | scalar | -1 | the sign of the fitted coefficient on age |
| `sign_check.age.univariate_direction` | `66364583` | scalar | -1 | the sign of age's own single-feature AUC on train minus 0.5 |
| `sign_check.bill_mean_6m.agrees` | `89279c3b` | scalar | 1 | 1 when the fitted sign on bill_mean_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.bill_trend_6m.agrees` | `ff3cb24a` | scalar | 1 | 1 when the fitted sign on bill_trend_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.delinq_count_6m.agrees` | `a337d16b` | scalar | 1 | 1 when the fitted sign on delinq_count_6m agrees with its univariate direction, 0 when it does not |
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
| `sign_check.pay_ratio_mean_6m.agrees` | `7e9a76ca` | scalar | 1 | 1 when the fitted sign on pay_ratio_mean_6m agrees with its univariate direction, 0 when it does not |
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
| `threshold.package.auc.test.min` | `8bfd02cc` | scalar | 0.7 | package.yaml declares auc min 0.7 |
| `threshold.package.brier.test.max` | `d0f98b9c` | scalar | 0.2 | package.yaml declares brier max 0.2 |
| `threshold.package.calibration_slope.test.max` | `0adb7a89` | scalar | 1.2 | package.yaml declares calibration_slope max 1.2 |
| `threshold.package.calibration_slope.test.min` | `95fdb848` | scalar | 0.8 | package.yaml declares calibration_slope min 0.8 |
| `threshold.package.psi.max` | `fbb5a9d1` | scalar | 0.25 | package.yaml declares psi max 0.25 |
| `thresholds.evaluation` | `9ff847ca` | table | table, 5 rows | every threshold package.yaml declares, with its bound, the recomputed value and the outcome |
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
| tool calls | 15 (run_model 1, profile_data 1, compute_metrics 3, check_leakage 1, check_collinearity 1, challenger_compare 1, retrieve_guidance 7) |
| plan steps (bounded loop) | 3 |
| LLM calls | 18 (plan 3, draft 7, reask 1, extract 7) |
| re-asks | 1 |
| repair rounds | 0 |
| tokens in / out | 233,329 / 100,864 |
| notional cost (USD) | 4.9010 |
| wall-clock (s) | 1114.38 |
| subject run (s) | 1.20 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | credit_default-full_agent-20260920T034326Z-e2e51e00 |

## Appendix D — Not checked

| item | reason |
|---|---|
| `check_stability` (R1) | package declares no `regime.column` |
| `run_scenarios` (X1) | not applicable to `binary_classification` |
| out-of-time and vintage-holdout metrics (O1, second rule) | package declares neither split |
| developer claims (T1, claim channel) | The package declares 2 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
