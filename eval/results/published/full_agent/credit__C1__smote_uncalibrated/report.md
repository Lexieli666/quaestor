---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: full_agent
model: claude-opus-5[1m]
run_id: credit_default-full_agent-20260920T012036Z-e2e51e00
data_mode: synthetic
synthetic_n: 5000
grounding_precision_pre: 0.9956
grounding_precision_post: 1.0000
n_claims: 226
n_findings_by_severity: {high: 1, medium: 1, low: 1, info: 0}
generated: "2026-09-20T01:20:36Z"
illustrative: false
---

# Validation report — `credit_default` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `credit_default` v1.0 | `full_agent` | claude-opus-5[1m] | synthetic, n = 5000 | 0.9956 → 1.0000 | 1 / 1 / 1 / 0 |
<!-- quaestor:renderer:end -->

The subject of this report is the credit_default model package, a credit scoring model that predicts the probability that an obligor defaults, and this report follows the structure of the Federal Reserve's model risk management guidance on validation [[reg:SR26-2:V]].
Quaestor re-executed the packaged subject and recomputed the metrics below from the subject's own predictions, within the wall-clock cap of 300 [[art:2ad8d1a5:runtime.max_seconds]] seconds that the package declares.
The development split holds 3500 [[art:2510d49d:profile.train.n]] rows and the held-out split holds 1500 [[art:2193cf5f:profile.test.n]] rows.
On the held-out split, discrimination of 0.7764 [[art:06c7c666:metrics.test.auc]] is above the declared floor of 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]], so that bound is met.
The Brier score on the held-out split of 0.1929 [[art:2f64a7ce:metrics.test.brier]] is below the declared ceiling of 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]], so that bound is met as well.
The largest population stability index measured from the development split to the held-out split, 0.01095 [[art:381b2570:psi.max]], is below the declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]], so that bound is met.
The calibration slope on the held-out split, 0.7952 [[art:b2bc94fc:calibration_slope.test]], sits below the declared upper bound of 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]] but also below the declared lower bound of 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]], so the declared calibration band is not satisfied from below.
Outcomes analysis of this kind is the point at which deviations outside established performance thresholds are expected to surface and to be weighed for adjustment, recalibration, or redevelopment [[reg:SR26-2:V.1.b]].
This validation raised F-001, a T1 declared threshold finding at high severity; F-002, a C1 calibration finding at medium severity; and F-003, a E1 effective challenge finding at low severity.
Each is written out in full in the findings section, with its evidence and its disposition.

## 2. Conceptual soundness

Model design is assessed here as a matter of conceptual soundness, covering the champion's key modeling choices, the developmental evidence behind its variable selection, and its benchmarking against an alternative model [[reg:SR26-2:V.1.a]].

The champion is a linear, coefficient-based scoring form fitted on 3500 [[art:3986de2e:run.model_summary#n_train]] training rows, with an intercept of 0.0674 [[art:3986de2e:run.model_summary#intercept]] and one fitted weight per retained feature.
The subject's feature inventory carries 12 [[art:abbb748e:run.features#n]] features, of which 2 [[art:abbb748e:run.features#at_origination]] are known at origination and 10 [[art:abbb748e:run.features#before_period_start]] are known before the performance period starts.
The inventory carries 0 [[art:abbb748e:run.features#during_period]] features drawn from inside the performance period and 0 [[art:abbb748e:run.features#after_outcome]] features known only after the outcome, so on the timing evidence nothing in the design is observed later than the point at which the score would be used.

The developer's own collinearity screen removed bill_last, whose variance inflation factor was 160.9 [[art:3986de2e:run.model_summary#removed.bill_last.vif]], and utilisation_mean_6m, whose inflation factor was 36.36 [[art:3986de2e:run.model_summary#removed.utilisation_mean_6m.vif]].
Each was read against the screen's declared cut-off of 10 [[art:3986de2e:run.model_summary#vif_threshold]], and each sits above it, the larger inflation factor being the one on bill_last.
Both removals are of features that restate balance and utilisation information already carried by retained terms, so dropping them is consistent with the stated rationale for the screen.

The largest fitted weight in magnitude is on delinq_last at 1.023 [[art:3986de2e:run.model_summary#coefficients.delinq_last.value]], followed by utilisation at 0.4769 [[art:3986de2e:run.model_summary#coefficients.utilisation.value]], bill_mean_6m at -0.2763 [[art:3986de2e:run.model_summary#coefficients.bill_mean_6m.value]], bill_trend_6m at -0.218 [[art:3986de2e:run.model_summary#coefficients.bill_trend_6m.value]] and pay_ratio_mean_6m at -0.1725 [[art:3986de2e:run.model_summary#coefficients.pay_ratio_mean_6m.value]].
The smaller weights are on delinq_count_6m at 0.1404 [[art:3986de2e:run.model_summary#coefficients.delinq_count_6m.value]], pay_ratio_last at -0.09177 [[art:3986de2e:run.model_summary#coefficients.pay_ratio_last.value]], age at -0.07628 [[art:3986de2e:run.model_summary#coefficients.age.value]], limit_bal at 0.01627 [[art:3986de2e:run.model_summary#coefficients.limit_bal.value]] and delinq_max_6m at 0.01353 [[art:3986de2e:run.model_summary#coefficients.delinq_max_6m.value]].
The directions on the large weights are what credit subject matter expects: a recent delinquency and a fuller drawn line raise modelled default risk, while a larger share of the bill repaid lowers it.

Fitted signs were compared against each feature's own univariate direction on train, and 1 [[art:f96ece96:sign_check.n_disagreements]] retained feature disagrees.
That feature is limit_bal, whose fitted coefficient carries sign 1 [[art:6af6aef2:sign_check.limit_bal.coef_sign]] against a univariate direction of -1 [[art:56d284d6:sign_check.limit_bal.univariate_direction]], recorded as a disagreement at 0 [[art:0278aad1:sign_check.limit_bal.agrees]].
In plain terms, a larger credit limit is associated with lower default on its own, but enters the fitted model as raising risk once utilisation, billing and delinquency terms are held alongside it, which is the sign pattern a conditioned-on-utilisation specification can produce.
The weight of that disagreement is small: refitting the champion's form without limit_bal moves test AUC by 0.0004286 [[art:63faa640:ablation.limit_bal.delta_auc]] from a refit level of 0.748 [[art:3a44e438:ablation.baseline_auc]], so the flipped sign sits on a feature the model does not lean on for discrimination.
Every other retained feature agrees with its univariate direction, including delinq_last at 1 [[art:a8ba9372:sign_check.delinq_last.agrees]], utilisation at 1 [[art:d0c9a130:sign_check.utilisation.agrees]], pay_ratio_mean_6m at 1 [[art:7e9a76ca:sign_check.pay_ratio_mean_6m.agrees]], bill_mean_6m at 1 [[art:89279c3b:sign_check.bill_mean_6m.agrees]] and age at 1 [[art:4116add1:sign_check.age.agrees]].

The features carrying discrimination, judged by refitting the champion's form without each in turn from the same refit level of 0.748 [[art:3a44e438:ablation.baseline_auc]], are delinq_last at -0.07585 [[art:3150b111:ablation.delinq_last.delta_auc]], utilisation at -0.01977 [[art:d4ad2039:ablation.utilisation.delta_auc]] and bill_mean_6m at -0.0016 [[art:3b91a889:ablation.bill_mean_6m.delta_auc]].
Dropping any of the remaining features leaves test AUC no lower, with pay_ratio_mean_6m at 0.006603 [[art:90fa1178:ablation.pay_ratio_mean_6m.delta_auc]], bill_trend_6m at 0.003279 [[art:096d7f98:ablation.bill_trend_6m.delta_auc]], pay_ratio_last at 0.002411 [[art:5f39089e:ablation.pay_ratio_last.delta_auc]], delinq_count_6m at 0.0006812 [[art:c5659def:ablation.delinq_count_6m.delta_auc]], limit_bal at 0.0004286 [[art:63faa640:ablation.limit_bal.delta_auc]], delinq_max_6m at 0.0003598 [[art:3a0d3a0c:ablation.delinq_max_6m.delta_auc]] and age at 8.675e-05 [[art:59398b1b:ablation.age.delta_auc]].
The design therefore concentrates its discrimination in the delinquency and utilisation terms, with the remaining features contributing little on this measure.
The sign comparison and the ablation evidence above are developmental evidence for this section's judgement, and neither is reported here as a finding.

Effective challenge was exercised by benchmarking the champion against a hist_gradient_boosting challenger fitted on the same data.
The challenger reaches a test AUC of 0.824 [[art:bf5be719:challenger.auc]] against the champion's 0.7764 [[art:06c7c666:metrics.test.auc]], and the comparison drawn is the difference between the two, at 0.0476 [[art:a86db8b1:challenger.delta_auc]].
That difference is read against the declared effective-challenge threshold of 0.03 [[art:e042774c:threshold.E1.delta_auc]], and it sits above the threshold, so the gap is treated as material rather than incidental.
On the scoring-rule comparison the challenger is also the better of the two, with a Brier score of 0.1258 [[art:f9e0583d:challenger.brier]] against the champion's 0.1929 [[art:2f64a7ce:metrics.test.brier]], where a lower score is better.
This is finding E1, raised at low suggested severity, and because a challenger of a different functional form outperforms the champion by more than the declared margin the finding bears directly on the champion's linear functional form; the findings section carries it and its disposition.

Taken together, the design is coherent on the evidence in this section: the feature timing is consistent with the point of use, the collinearity screen is applied as stated and against a declared cut-off, and the fitted directions match subject-matter expectation apart from the flip on limit_bal described above, which sits on a feature the model barely uses.
The open question for conceptual soundness is the functional form itself, which the effective-challenge comparison raises and the findings section carries.

## 3. Data integrity and drift

Sound development practice includes a critical assessment of data quality, relevance, and inputs, and this section records what the data screens returned for this package. [[reg:SR26-2:IV.1]]

### Missingness

The training split holds 3500 rows [[art:2510d49d:profile.train.n]] and the test split holds 1500 rows [[art:2193cf5f:profile.test.n]].
The largest missing fraction in the training split is 0 [[art:050a3099:profile.train.missing.max]], and the largest missing fraction in the test split is likewise 0 [[art:f813848d:profile.test.missing.max]].
The two maxima stand at the same value, so the gap between the splits lies below the bound of 0.1 [[art:9cce25ea:threshold.D1.missing_gap]] that the missingness rule holds it to.

### Population and characteristic stability

Stability is read from the training split against the other split, and both the population measure and the per-feature contributions are compared with the declared stability bound of 0.25 [[art:278b9016:threshold.S1.psi]], which the package itself declares at the same value of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
The largest train-to-test population stability index, the score included, is 0.01095 [[art:381b2570:psi.max]], well below that bound.
Among the individual features, the population stability index is 0.01095 [[art:601cdba2:psi.limit_bal]] for limit_bal, 0.00958 [[art:c247a6f2:psi.bill_trend_6m]] for bill_trend_6m, 0.008124 [[art:f9255a0a:psi.age]] for age, 0.007124 [[art:028e4281:psi.bill_mean_6m]] for bill_mean_6m, 0.0055 [[art:2c5baeb2:psi.pay_ratio_mean_6m]] for pay_ratio_mean_6m and 0.005498 [[art:7a82e7f3:psi.delinq_max_6m]] for delinq_max_6m.
The remainder are smaller still, at 0.004966 [[art:3af2ca29:psi.pay_ratio_last]] for pay_ratio_last, 0.004244 [[art:451e0780:psi.utilisation]] for utilisation, 0.00285 [[art:03bd52e7:psi.delinq_last]] for delinq_last and 0.002069 [[art:61491d02:psi.delinq_count_6m]] for delinq_count_6m, while the score itself shifts by 0.005049 [[art:a8375d0f:psi.y_score]].
The largest movement in the population measure is therefore carried by limit_bal, and the score moves less than that feature does.

The largest characteristic stability index, measuring a feature's contribution to the shift in the linear predictor, is 0.03295 [[art:e1f1ad3d:csi.max]], and it is contributed by delinq_last at 0.03295 [[art:39b31d8e:csi.delinq_last]].
That value sits below the declared stability bound of 0.25 [[art:278b9016:threshold.S1.psi]], as do the remaining contributions: 0.00724 [[art:0a1f2306:csi.utilisation]] for utilisation, 0.006203 [[art:2567a75c:csi.bill_trend_6m]] for bill_trend_6m, 0.002804 [[art:b0282e56:csi.delinq_count_6m]] for delinq_count_6m, 0.001757 [[art:278c2a6d:csi.bill_mean_6m]] for bill_mean_6m, 0.001721 [[art:fd186b68:csi.pay_ratio_last]] for pay_ratio_last, 0.001075 [[art:1642e34e:csi.age]] for age, 0.0008584 [[art:659995f7:csi.pay_ratio_mean_6m]] for pay_ratio_mean_6m, 0.0003766 [[art:3fc49a03:csi.delinq_max_6m]] for delinq_max_6m and 0.0002712 [[art:bc85c1c5:csi.limit_bal]] for limit_bal.
The two views rank the features differently: limit_bal moves the distribution most but contributes least to the shift in the linear predictor, while delinq_last moves the distribution little yet contributes the most to that shift.

### Leakage screens

The timing screen counts 0 features [[art:742bcd24:leakage.timing.n_flagged]] declared as observed during the performance period or after the outcome, so no declared timing places a feature after the event it is used to predict.
The strongest single feature reaches an area under the curve of 0.6831 [[art:fd829fc4:leakage.target_corr.max_single_feature_auc]] on its own, below the bound of 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]] above which a lone feature would be treated as standing in for the target.

The contamination screen is read on two arms, each against its own bound.
On the identifier arm, the share of test rows whose client identifier also identifies a row of the training split is 0 [[art:63d37fc5:leakage.overlap.ids]], below the declared contamination bound of 0.005 [[art:9f336eaf:threshold.L2.overlap]].
On the feature-vector arm, the share of test rows whose feature values also appear in the training split is 0 [[art:0fec8048:leakage.overlap.features]], below the bound of 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]] that this arm actually applied.
That applied bound takes the declared contamination bound as its floor and rises with the share of training rows whose feature values are not unique within the training split, on the reasoning that two different subjects writing the same discrete row is coincidence rather than contamination; here that duplicate share is 0 [[art:4474c227:leakage.duplicates.train]], so the applied bound rests on its floor of 0.005 [[art:9f336eaf:threshold.L2.overlap]].
The overall overlap screen returns the same share of test rows carrying feature values seen in the training split, 0 [[art:4c9fcd09:leakage.overlap]], below the applied bound of 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].
The name screen matches 0 feature names [[art:407e62be:leakage.name_screen.n_matched]] against the target-adjacent lexicon.

On the evidence assembled here, the splits agree on missingness, the distributions and their contributions to the linear predictor move by margins far short of the declared stability bound, and every leakage arm sits on the permitted side of the bound it was read against.
This section raises nothing for the findings section.

## 4. Outcomes analysis

Outcomes analysis compares model outputs to the corresponding real-world outcomes in order to assess performance relative to the model's objectives and business use, and where results fall persistently outside established performance thresholds, adjustment, recalibration, or redevelopment may be warranted [[reg:SR26-2:V.1.b]].
This section reports discrimination first and calibration second, because the observed event rate on the evaluation split, 0.2247 [[art:9209d200:metrics.test.event_rate]], is at or above 0.05 [[art:42f1351e:rule.calibration_first_event_rate]], the event rate below which this report would lead with calibration instead.

### Metrics by split

| Metric | Train | Test |
| --- | --- | --- |
| Rows | 3500 [[art:564683ee:metrics.train.n]] | 1500 [[art:64fcf14d:metrics.test.n]] |
| Observed event rate | 0.2246 [[art:133a5ff8:metrics.train.event_rate]] | 0.2247 [[art:9209d200:metrics.test.event_rate]] |
| AUC | 0.7765 [[art:0e7355aa:metrics.train.auc]] | 0.7764 [[art:06c7c666:metrics.test.auc]] |
| Gini | 0.553 [[art:1e398595:metrics.train.gini]] | 0.5527 [[art:bc939097:metrics.test.gini]] |
| KS | 0.4801 [[art:97bd5dab:metrics.train.ks]] | 0.4656 [[art:f4b92d62:metrics.test.ks]] |
| Brier | 0.1969 [[art:f118c784:metrics.train.brier]] | 0.1929 [[art:2f64a7ce:metrics.test.brier]] |
| Log loss | 0.6031 [[art:dcbefb71:metrics.train.logloss]] | 0.5935 [[art:6ac37fc1:metrics.test.logloss]] |
| Mean predicted probability | 0.4427 [[art:bbe07926:metrics.train.mean_predicted]] | 0.4379 [[art:aa68c658:metrics.test.mean_predicted]] |

Rank-ordering on the evaluation split is set out by decile of predicted probability, the first decile holding the highest probabilities.

<!-- quaestor:renderer:begin table deciles.test -->
Decile separation on test; decile 1 holds the highest probabilities [[art:cc3eddec:deciles.test]]:

| decile | count | events | event_rate | lift |
|---|---|---|---|---|
| 1 | 150 | 73 | 0.4867 | 2.166 |
| 2 | 150 | 77 | 0.5133 | 2.285 |
| 3 | 150 | 66 | 0.44 | 1.958 |
| 4 | 150 | 37 | 0.2467 | 1.098 |
| 5 | 150 | 27 | 0.18 | 0.8012 |
| 6 | 150 | 19 | 0.1267 | 0.5638 |
| 7 | 150 | 9 | 0.06 | 0.2671 |
| 8 | 150 | 12 | 0.08 | 0.3561 |
| 9 | 150 | 10 | 0.06667 | 0.2967 |
| 10 | 150 | 7 | 0.04667 | 0.2077 |
<!-- quaestor:renderer:end -->

The top two deciles hold 0.4451 [[art:e3b6058b:deciles.test.top2_capture]] of the events on test and 0.4262 [[art:1693b145:deciles.train.top2_capture]] of the events on train, the test share being the larger of the two.

### Train-to-test gap

The movement in AUC between the two splits is read against a bound of 0.08 [[art:630f28f4:threshold.O1.auc_gap]].
AUC is 0.7765 [[art:0e7355aa:metrics.train.auc]] on train and 0.7764 [[art:06c7c666:metrics.test.auc]] on test, so the evaluation figure sits level with the development figure and does not fall below it by anything approaching that bound.
KS is lower on test at 0.4656 [[art:f4b92d62:metrics.test.ks]] than on train at 0.4801 [[art:97bd5dab:metrics.train.ks]], while Brier and log loss are both lower on test than on train, so there is no sign of the ordering degrading out of sample.

### Calibration

Calibration is assessed by regressing the outcome on the logit of the predicted probability, and by comparing the mean predicted probability to the observed rate.

<!-- quaestor:renderer:begin table calibration.test -->
Calibration by decile of predicted probability on test [[art:ffcc3994:calibration.test]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.1863 | 0.04667 | 150 |
| 2 | 0.2354 | 0.06667 | 150 |
| 3 | 0.2744 | 0.08 | 150 |
| 4 | 0.3126 | 0.06 | 150 |
| 5 | 0.3533 | 0.1267 | 150 |
| 6 | 0.4002 | 0.18 | 150 |
| 7 | 0.4652 | 0.2467 | 150 |
| 8 | 0.5561 | 0.44 | 150 |
| 9 | 0.715 | 0.5133 | 150 |
| 10 | 0.8806 | 0.4867 | 150 |
<!-- quaestor:renderer:end -->

On test the slope is 0.7952 [[art:b2bc94fc:calibration_slope.test]], below the developer-declared minimum of 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] and below the bottom of the internal band at 0.8 [[art:749634ae:threshold.C1.calibration_slope.min]], whose top is 1.2 [[art:b6672579:threshold.C1.calibration_slope.max]].
On train the slope is 0.7656 [[art:1151c8e4:calibration_slope.train]], also below that band, and it is the lower of the two slopes.
The intercept of the same regression is -1.217 [[art:62851316:calibration_intercept.test]] on test and -1.241 [[art:849b7b2e:calibration_intercept.train]] on train, both well below zero, which is the signature of a level shift rather than of a failure to order.
The mean predicted probability on test, 0.4379 [[art:aa68c658:metrics.test.mean_predicted]], stands above the observed rate of 0.2247 [[art:9209d200:metrics.test.event_rate]], and the relative gap between them is 0.9491 [[art:376ae2d7:calibration.mean_rel_gap.test]] against a tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
On train the mean predicted probability is 0.4427 [[art:bbe07926:metrics.train.mean_predicted]] against an observed rate of 0.2246 [[art:133a5ff8:metrics.train.event_rate]], a relative gap of 0.9715 [[art:0abea673:calibration.mean_rel_gap.train]] against the same tolerance; comparing the two splits on the relative gap, the train figure is the larger, and this report makes no claim about how their absolute differences compare.
These results carry the calibration finding C1, raised on both splits, and the declared-threshold finding T1 on the test slope; the model over-predicts the level of risk while retaining its ability to rank.

### Developer-declared thresholds

<!-- quaestor:renderer:begin table thresholds.evaluation -->
Every threshold package.yaml declares, with its bound, the recomputed value and the outcome [[art:f50831dc:thresholds.evaluation]]:

| metric | split | bound | value | result |
|---|---|---|---|---|
| auc | test | minimum 0.7 | 0.7764 | pass |
| brier | test | maximum 0.2 | 0.1929 | pass |
| calibration_slope | test | minimum 0.8 | 0.7952 | fail |
| calibration_slope | test | maximum 1.2 | 0.7952 | pass |
| psi |  | maximum 0.25 | 0.01095 | pass |
<!-- quaestor:renderer:end -->

The table sets every bound the package declares beside the value recomputed in this run and the outcome of the comparison, so the bounds and the recomputed values in it are the same ones reported above.
The calibration slope on the evaluation split is the only declared bound whose recomputed value falls outside it, and the discrimination, error and stability bounds are met.

### Follow-up analyses

Four follow-up runs recomputed the full metric set on sub-populations of the evaluation split, each asking whether the over-prediction of the level and the sub-band slope are uniform across the book or concentrated in one segment.

The first asked for every metric on the `utilisation > median(utilisation)` slice of test, to test whether the over-prediction and the sub-band calibration slope are uniform or concentrated in the high-utilisation, higher-risk half, which bears on whether the miscalibration is a global level shift or segment-specific.

<!-- quaestor:renderer:begin table metrics.test.sub.utilisation_high -->
Every metric on the utilisation above_median slice of test [[art:7fb0faad:metrics.test.sub.utilisation_high]]:

| metric | value |
|---|---|
| n | 750 |
| event_rate | 0.2333 |
| auc | 0.5865 |
| gini | 0.173 |
| ks | 0.1861 |
| brier | 0.2688 |
| logloss | 0.7801 |
| mean_predicted | 0.4918 |
| mean_rel_gap | 1.108 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

AUC on this slice is 0.5865 [[art:015b00e8:metrics.test.sub.utilisation_high.auc]], falling below the split's own AUC by 0.1898 [[art:fcca7c35:metrics.test.sub.utilisation_high.auc_gap]], above the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] at which a sub-population becomes an open item.
The slice holds 0.5 [[art:9404484e:metrics.test.sub.utilisation_high.share]] of the split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] a sub-population must hold and below the share of 0.95 [[art:a928a05c:threshold.O1.slice_max_share]] at which it would be refused as the whole split.
Mean predicted probability here is 0.4918 [[art:f1d1d4d2:metrics.test.sub.utilisation_high.mean_predicted]] against an observed rate of 0.2333 [[art:8e66209c:metrics.test.sub.utilisation_high.event_rate]], a relative gap of 1.108 [[art:40cb08f4:metrics.test.sub.utilisation_high.mean_rel_gap]], so this segment is weak in both the level of its probabilities and their ordering, and the AUC shortfall is a question for the model developer rather than something recalibration alone would reach.

The second asked for every metric on the `utilisation <= median(utilisation)` slice of test, completing the partition so that the over-prediction can be seen either as a uniform level shift or as something concentrated in the half measured first.

<!-- quaestor:renderer:begin table metrics.test.sub.utilisation_low -->
Every metric on the utilisation below_median slice of test [[art:ad3af41c:metrics.test.sub.utilisation_low]]:

| metric | value |
|---|---|
| n | 750 |
| event_rate | 0.216 |
| auc | 0.9086 |
| gini | 0.8171 |
| ks | 0.7642 |
| brier | 0.117 |
| logloss | 0.4069 |
| mean_predicted | 0.384 |
| mean_rel_gap | 0.7777 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

AUC on this slice is 0.9086 [[art:d408b939:metrics.test.sub.utilisation_low.auc]] and does not fall below the split's own AUC at all, the shortfall being recorded as -0.1322 [[art:bf57d590:metrics.test.sub.utilisation_low.auc_gap]], within the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]], so it is supporting evidence here and not an open item.
The slice holds 0.5 [[art:7860a748:metrics.test.sub.utilisation_low.share]] of the split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].
Mean predicted probability is 0.384 [[art:5d54c6cf:metrics.test.sub.utilisation_low.mean_predicted]] against an observed rate of 0.216 [[art:b0ad49be:metrics.test.sub.utilisation_low.event_rate]], a relative gap of 0.7777 [[art:d873908a:metrics.test.sub.utilisation_low.mean_rel_gap]]; comparing the two halves of this partition on the relative gap, the high-utilisation half's is the larger, so the over-prediction is present in both halves but not evenly, and the weakness in this half is in the level of the probabilities and not in their ordering.

The third asked for every metric on the `limit_bal <= median(limit_bal)` slice of test, because the over-prediction is close to identical on train and test, and a low-limit slice tests whether it is a uniform intercept shift or concentrated in the higher-risk half.

<!-- quaestor:renderer:begin table metrics.test.sub.limit_bal_low -->
Every metric on the limit_bal below_median slice of test [[art:2ae9e510:metrics.test.sub.limit_bal_low]]:

| metric | value |
|---|---|
| n | 756 |
| event_rate | 0.2487 |
| auc | 0.7838 |
| gini | 0.5677 |
| ks | 0.4549 |
| brier | 0.2054 |
| logloss | 0.6309 |
| mean_predicted | 0.4709 |
| mean_rel_gap | 0.8935 |
| share | 0.504 |
<!-- quaestor:renderer:end -->

AUC on this slice is 0.7838 [[art:b14bb20b:metrics.test.sub.limit_bal_low.auc]] and does not fall below the split's own AUC, the shortfall being recorded as -0.007454 [[art:69d61c38:metrics.test.sub.limit_bal_low.auc_gap]], within the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].
The slice holds 0.504 [[art:bac689cc:metrics.test.sub.limit_bal_low.share]] of the split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].
Mean predicted probability is 0.4709 [[art:1cae8978:metrics.test.sub.limit_bal_low.mean_predicted]] against an observed rate of 0.2487 [[art:de78adb5:metrics.test.sub.limit_bal_low.event_rate]], a relative gap of 0.8935 [[art:07e1da50:metrics.test.sub.limit_bal_low.mean_rel_gap]], so the weakness on this slice is in the level of the probabilities while the ordering holds up.

The fourth asked for every metric on the `delinq_count_6m > median(delinq_count_6m)` slice of test, to test whether the over-prediction is uniform across risk strata, and so curable by recalibration, or concentrated in the delinquent segment, which would bear on the severity of the calibration finding.

<!-- quaestor:renderer:begin table metrics.test.sub.delinq_count_6m_high -->
Every metric on the delinq_count_6m above_median slice of test [[art:a11954ab:metrics.test.sub.delinq_count_6m_high]]:

| metric | value |
|---|---|
| n | 550 |
| event_rate | 0.3455 |
| auc | 0.735 |
| gini | 0.4701 |
| ks | 0.4557 |
| brier | 0.2485 |
| logloss | 0.7378 |
| mean_predicted | 0.5805 |
| mean_rel_gap | 0.6803 |
| share | 0.3667 |
<!-- quaestor:renderer:end -->

AUC on this slice is 0.735 [[art:8578b988:metrics.test.sub.delinq_count_6m_high.auc]], falling below the split's own AUC by 0.04134 [[art:39738a6e:metrics.test.sub.delinq_count_6m_high.auc_gap]], within the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]], so it too is supporting evidence rather than an open item.
The slice holds 0.3667 [[art:22847310:metrics.test.sub.delinq_count_6m_high.share]] of the split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].
Mean predicted probability is 0.5805 [[art:6e2677ac:metrics.test.sub.delinq_count_6m_high.mean_predicted]] against an observed rate of 0.3455 [[art:ef17c303:metrics.test.sub.delinq_count_6m_high.event_rate]], a relative gap of 0.6803 [[art:58e32501:metrics.test.sub.delinq_count_6m_high.mean_rel_gap]], the smallest of the four relative gaps reported in this subsection, so on this comparison of relative gaps the delinquent segment is where the level of the probabilities is closest to the observed experience, and its weakness is one of level rather than of ordering.

Taken together, the four slices say that the over-prediction of the level is present across every segment measured rather than confined to one, and that the ordering holds everywhere except the high-utilisation half, where it does not.

## 5. Sensitivity and scenario analysis

Sensitivity analysis is reported here in the sense that validation should check the effect of changes in inputs and parameter values on model outputs, and should probe behaviour at extreme values to establish the conditions under which a model becomes unstable or inaccurate [[reg:SR11-7:V.1.a]].

### 5.1 Multicollinearity among the retained features

Collinearity in the retained feature set was assessed through per-feature variance inflation factors on the training sample and through Belsley's condition number of the column-standardised design.

The largest variance inflation factor over the retained features is 7.295 [[art:9ae7c45b:vif.max]], which falls below the declared ceiling of 10 [[art:aeb4f33c:threshold.M1.vif]].

That maximum is attained by the six-month mean billed amount at 7.295 [[art:f0a2f865:vif.bill_mean_6m]], with the last payment ratio close behind at 7.264 [[art:c2de8dfe:vif.pay_ratio_last]] and the six-month mean payment ratio at 7.259 [[art:e39c3e82:vif.pay_ratio_mean_6m]].

These three sit together at the top of the range and are mutually close, which is consistent with the billing and payment-ratio constructions sharing much of the same underlying account history.

The credit limit follows at 4.803 [[art:ddfdcc3c:vif.limit_bal]] and utilisation at 3.215 [[art:536fdb6f:vif.utilisation]], both further from the ceiling than the payment-ratio group.

The delinquency features are lower still, at 2.561 [[art:38974def:vif.delinq_count_6m]] for the six-month delinquency count, 2.408 [[art:71aaaf11:vif.delinq_max_6m]] for the six-month maximum and 1.412 [[art:48733638:vif.delinq_last]] for the most recent delinquency.

The six-month billing trend at 1.201 [[art:9356a256:vif.bill_trend_6m]] and age at 1.002 [[art:74c06cad:vif.age]] are the least entangled with the rest of the design, with age near the floor of the statistic.

Belsley's condition number of the column-standardised design is 5.547 [[art:e41b9562:condition_number]], below the declared ceiling of 30 [[art:7e52fd7a:threshold.M1.condition_number]].

Both diagnostics therefore fall on the acceptable side of their declared ceilings, and the condition number in particular indicates no near-degeneracy in the design that would make the fitted coefficients numerically fragile.

The coefficients on the billing and payment-ratio features should nonetheless be read as a group rather than individually, since their variance inflation factors are the largest in the set and are close to one another.

### 5.2 Analyses that do not apply to this model

The package declares no regime column for this model, so stability of the model across declared regimes is not in scope for this section and is recorded as such in Appendix D.

Nothing below should be read as a regime comparison, and no regime-wise result is reported here.

The subject is not a hazard model, so the rate-shock scenarios are likewise out of scope and are recorded in Appendix D.

This means the value change at the extreme shocks, the monotonicity of the shock curve, and the convexity of that curve against the direction the package declares were not exercises applicable to this model type, and no statement in this section should be read as reporting them.

The sensitivity evidence carried by this section is therefore the collinearity evidence set out above.

Nothing in this section is carried forward as a finding.

## 6. Findings and recommendations

Findings are ordered by severity, highest first, and each carries the quantity this validation recomputed together with the declared bound it was read against, so that identified limitations and errors are stated alongside whether corrective action may be warranted [[reg:SR26-2:V]].

### F-001 · T1 declared threshold · severity **high**

**The model package breaches a bound it declares for itself: the calibration slope on test sits below the package's own stated minimum.**
The package declares a minimum calibration slope on test of 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]].
The slope recomputed by this validation on test is 0.7952 [[art:b2bc94fc:calibration_slope.test]], below that minimum.
The validator concludes that the model does not meet an acceptance limit the developer set for it, so the breach is measured against the developer's own standard rather than one introduced by this review.
The developer should either recalibrate so that the slope on test returns above the declared minimum, or restate the declared minimum with a documented rationale for the wider limit, recording the change and the response so the exception can be tracked [[reg:SR26-2:VI.3]].

### F-002 · C1 calibration · severity **medium**

**Predicted probabilities are miscalibrated on both splits, in slope and in level, and the level error is large.**
The calibration slope on train is 0.7656 [[art:1151c8e4:calibration_slope.train]] and on test is 0.7952 [[art:b2bc94fc:calibration_slope.test]], each below the bottom of the acceptable slope band at 0.8 [[art:749634ae:threshold.C1.calibration_slope.min]].
On train the mean predicted probability is 0.4427 [[art:bbe07926:metrics.train.mean_predicted]] against an observed event rate of 0.2246 [[art:133a5ff8:metrics.train.event_rate]], a relative gap of 0.9715 [[art:0abea673:calibration.mean_rel_gap.train]] against a tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
On test the mean predicted probability is 0.4379 [[art:aa68c658:metrics.test.mean_predicted]] against an observed event rate of 0.2247 [[art:9209d200:metrics.test.event_rate]], a relative gap of 0.9491 [[art:376ae2d7:calibration.mean_rel_gap.test]], likewise above that tolerance.
Ranked rather than differenced or ratioed, the relative level gap on train is the larger of the two, and the slope on train is the further below the band's lower edge.
The decile tables below show where in the predicted range the level error concentrates.

<!-- quaestor:renderer:begin table calibration.train -->
Calibration by decile of predicted probability on train [[art:34673c01:calibration.train]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.1857 | 0.04857 | 350 |
| 2 | 0.241 | 0.04857 | 350 |
| 3 | 0.2803 | 0.06 | 350 |
| 4 | 0.3174 | 0.1057 | 350 |
| 5 | 0.3564 | 0.09429 | 350 |
| 6 | 0.4025 | 0.1657 | 350 |
| 7 | 0.463 | 0.2829 | 350 |
| 8 | 0.5617 | 0.4829 | 350 |
| 9 | 0.7317 | 0.4914 | 350 |
| 10 | 0.8877 | 0.4657 | 350 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table calibration.test -->
Calibration by decile of predicted probability on test [[art:ffcc3994:calibration.test]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.1863 | 0.04667 | 150 |
| 2 | 0.2354 | 0.06667 | 150 |
| 3 | 0.2744 | 0.08 | 150 |
| 4 | 0.3126 | 0.06 | 150 |
| 5 | 0.3533 | 0.1267 | 150 |
| 6 | 0.4002 | 0.18 | 150 |
| 7 | 0.4652 | 0.2467 | 150 |
| 8 | 0.5561 | 0.44 | 150 |
| 9 | 0.715 | 0.5133 | 150 |
| 10 | 0.8806 | 0.4867 | 150 |
<!-- quaestor:renderer:end -->

The validator concludes that the scores overstate risk in level on both splits and are too flat in slope on both splits, so the output is usable as a ranking only with an explicit caveat and is not usable as a probability of default without correction.
The developer should refit or post-fit the score to the observed base rate, re-examine the training objective and any class weighting or resampling that could produce a systematic level shift of this size, and report the slope and the level gap on both splits after the correction.

### F-003 · E1 effective challenge · severity **low**

**A routine benchmark challenger beats the champion on test by more than the margin at which effective challenge is treated as unmet.**
The champion's AUC on test is 0.7764 [[art:06c7c666:metrics.test.auc]], while a histogram gradient boosting challenger reaches 0.824 [[art:bf5be719:challenger.auc]] on the same split.
The challenger's lead over the champion is 0.0476 [[art:a86db8b1:challenger.delta_auc]], above the effective-challenge threshold of 0.03 [[art:e042774c:threshold.E1.delta_auc]].
The validator concludes that an alternative specification available at low cost delivers materially better discrimination, so the choice of the current form has not been shown to be the better one on evidence.
The developer should document why the champion form was selected over this alternative on grounds other than discrimination, such as interpretability, stability or implementation constraints, or else promote the stronger specification and validate it in turn.

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1, S1), `compute_metrics` (O1), `check_leakage` (L1, L2), `check_collinearity` (M1).

### Open items

For the model developer: within the test segment defined by `utilisation > median(utilisation)`, which holds 0.5 [[art:9404484e:metrics.test.sub.utilisation_high.share]] of the split and so sits at or above the minimum share of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] at which such an observation is raised, AUC is 0.5865 [[art:015b00e8:metrics.test.sub.utilisation_high.auc]] against 0.7764 [[art:06c7c666:metrics.test.auc]] on the whole split, a shortfall of 0.1898 [[art:fcca7c35:metrics.test.sub.utilisation_high.auc_gap]] read against a bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] — given that selecting on utilisation also holds utilisation and everything correlated with it close to constant inside the segment, what signal does the model still separate borrowers on there, and is that separation adequate for the intended use on this half of the population?
For the model developer: the fitted coefficient on `limit_bal` carries sign 1 [[art:6af6aef2:sign_check.limit_bal.coef_sign]] where that feature's own univariate direction is -1 [[art:56d284d6:sign_check.limit_bal.univariate_direction]], and the agreement indicator read against that univariate direction is 0 [[art:0278aad1:sign_check.limit_bal.agrees]] — what does the coefficient represent once the remaining features are held fixed, and which correlated feature is carrying the direction the single-feature view shows?

## 7. Ongoing monitoring recommendations

Ongoing monitoring is framed here as the guidance frames it, as a continuing evaluation of whether the model performs as expected given potential changes in products, exposures, activities, clients, data relevance, or market conditions [[reg:SR26-2:V.2]].

### Quantities to track, at what frequency, against which bound

Rank-ordering should be recomputed on each production vintage as its performance window matures and compared with the declared floor of 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]], the same floor the checks in this report applied.
The validation-time discrimination value of 0.7764 [[art:06c7c666:metrics.test.auc]] is the reference point against which vintage-to-vintage movement should be read, and a sustained downward trend that has not yet reached the floor still warrants investigation.
A quarterly recomputation is appropriate once the window has matured, supplemented by a monthly early-warning trend on scored volumes and score distributions so that deterioration becomes visible before a full window closes [[reg:SR11-7:V.1.c]].

Probability accuracy should be tracked with the Brier score against the declared ceiling of 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]], with the validation-time value of 0.1929 [[art:2f64a7ce:metrics.test.brier]] as the reference point.
That reference sits below the ceiling, so monitoring should treat sustained movement toward the ceiling, and not only a crossing of it, as grounds for review.

Calibration should be tracked with the regression slope of the outcome on the logit of the predicted probability, compared against the declared band that runs from a lower end of 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] to an upper end of 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The validation-time slope of 0.7952 [[art:b2bc94fc:calibration_slope.test]] lies below the lower end of that band, which makes calibration the quantity most worth watching at the highest frequency the outcome data allow: monthly where a matured performance window permits it, quarterly otherwise.
A monitoring report should pair the slope with observed-versus-expected event rates by score band, because a slope that returns inside the band can still coexist with level error concentrated in a single band.

Population stability should be tracked with the same shift statistic used in this validation, whose largest train-to-test value across the inputs and the score was 0.01095 [[art:381b2570:psi.max]], well below the declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
Monitoring should recompute that statistic monthly for every model input and for the score itself, holding the development sample fixed as the baseline rather than comparing each month with the month before, and compare the result with 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].

### Ordering of the monitoring report

The observed event rate on the evaluation split used in this validation was at or above the rate below which calibration is reported ahead of discrimination, which is 0.05 [[art:42f1351e:rule.calibration_first_event_rate]], and section 4 accordingly reported discrimination before calibration.
For a future production cohort whose observed event rate falls below 0.05 [[art:42f1351e:rule.calibration_first_event_rate]], the monitoring report covering that cohort should lead with calibration instead, so that the ordering follows the cohort rather than the precedent set by this report.

### Sub-population reporting

Where a monitoring report breaks performance out by sub-population, by acquisition channel, or by score decile, it should state for each comparison whether it is reporting the absolute difference or the ratio of the two populations' shortfalls, and it should report both rather than one alone.
Two sub-populations whose absolute gaps look alike can stand in a very different ratio to each other, so a report that concludes parity from one of those measures while leaving the other unstated is not sound evidence of parity.

### Benchmarking, and what monitoring adds

Section 2 of this report compares the champion with a challenger, and monitoring is not being asked to repeat that internal, same-vintage comparison.
What monitoring adds is the comparison the development data cannot supply: a benchmark of the score against an external vendor or credit-bureau reference scored on the same accounts.
The external reference is what is meant here, specifically, rather than a refit of the challenger on production vintages.
Discrepancies between the score and that reference should trigger investigation into the sources and degree of the difference, while close agreement should be read with caution, since the reference is itself an alternative prediction built on different data and methods [[reg:SR11-7:V.1.b]].
If the reference is a vendor product, its own developmental evidence, its input data, and its relevance to this portfolio should be assessed before its output is used as a yardstick [[reg:SR11-7:V.2]].

### What this validation could not cover and monitoring should watch instead

This validation observed the model on fixed development and evaluation splits, so it cannot speak to how the implemented model behaves once it is scoring live accounts, and process verification of the production scoring pipeline, its data feeds, and its change control belongs to monitoring [[reg:SR11-7:V.1.b]].
Overrides arise only once the model is in use, so monitoring should log every override with its rationale, track the override rate, and test whether overridden decisions outperform the model, since a high rate or a consistent improvement points toward revision or redevelopment [[reg:SR11-7:V.1.b]].
The evaluation split represents the conditions present in the development data and cannot represent a credit cycle or a macroeconomic regime that has not yet occurred, so back-testing across successive production vintages is the mechanism that will surface such a shift [[reg:SR26-2:V.1.b]].
Any extension of the model to a new portfolio, channel, or population beyond its intended use was outside what this validation examined, and monitoring should verify that such an extension remains valid before it is relied on [[reg:SR11-7:V.1.b]].
The model limitations identified at the development stage should be reassessed on a regular cadence rather than treated as settled by this exercise, with an annual review of whether the declared bounds themselves remain the right ones [[reg:SR26-2:V.2]].

### Escalation

Where monitoring shows material error or persistent deviation outside the declared bounds cited above, the response should be considered in the order of overlay, adjustment, recalibration, and redevelopment, according to the organization's model risk management policy on model deterioration [[reg:SR26-2:V.1.b]].
The frequencies proposed above are a starting point and should be revisited in light of the model's materiality, the availability of new outcome data, and the pace of change in the portfolio [[reg:SR26-2:V.2]].

## Appendix A — Claims

Grounding precision 0.9956 before repair (226 of 227 claims verified; 1 unsupported) and 1.0000 after 0 claim(s) rewritten and 1 number(s) removed from the prose. Per section (post-repair): summary 12/12; conceptual_soundness 48/48; data_integrity 43/43; outcomes 72/72; sensitivity 14/14; findings 25/25; monitoring 12/12.

Developer claims: The package declares 2 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). See Appendix D.

Excluded numeric tokens (not claims): section_number (5.1, 5.2, section 4, Section 2); citation_hash (2ad8d1a5, 2510d49d, 2193cf5f, 06c7c666); regulatory_section_id (SR26-2:V, SR26-2:V.1.b, SR26-2:V.1.a, SR26-2:IV.1); finding_id (F-001, F-002, F-003); extractor_returned_excluded_token (2.0, 1.0, 6.0, 5.1).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | Quaestor re-executed the packaged subject and recomputed the… | 300 | ratio | runtime.max_seconds |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 2 | summary | The development split holds 3500 rows and the held-out split… | 3500 | count | n | train | eq | `[[art:2510d49d:profile.train.n]]` | verified | 3500 |
| 3 | summary | The development split holds 3500 rows and the held-out split… | 1500 | count | n | test | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 4 | summary | On the held-out split, discrimination of 0.7764 is above the… | 0.7764 | ratio | auc | test | eq | `[[art:06c7c666:metrics.test.auc]]` | verified | 0.7763713511 |
| 5 | summary | On the held-out split, discrimination of 0.7764 is above the… | 0.7 | ratio | auc | test | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 6 | summary | The Brier score on the held-out split of 0.1929 is below the… | 0.1929 | ratio | brier | test | eq | `[[art:2f64a7ce:metrics.test.brier]]` | verified | 0.1928760509 |
| 7 | summary | The Brier score on the held-out split of 0.1929 is below the… | 0.2 | ratio | brier | test | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 8 | summary | The largest population stability index measured from the dev… | 0.01095 | ratio | psi |  | eq | `[[art:381b2570:psi.max]]` | verified | 0.01095273358 |
| 9 | summary | The largest population stability index measured from the dev… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 10 | summary | The calibration slope on the held-out split, 0.7952 , sits b… | 0.7952 | ratio | calibration_slope | test | eq | `[[art:b2bc94fc:calibration_slope.test]]` | verified | 0.7952064062 |
| 11 | summary | The calibration slope on the held-out split, 0.7952 , sits b… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 12 | summary | The calibration slope on the held-out split, 0.7952 , sits b… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 13 | conceptual_soundness | The champion is a linear, coefficient-based scoring form fit… | 3500 | count | n_train | train | eq | `[[art:3986de2e:run.model_summary#n_train]]` | verified | 3500 |
| 14 | conceptual_soundness | The champion is a linear, coefficient-based scoring form fit… | 0.0674 | ratio | intercept |  | eq | `[[art:3986de2e:run.model_summary#intercept]]` | verified | 0.06740330428 |
| 15 | conceptual_soundness | The subject's feature inventory carries 12 features, of whic… | 12 | count | n_features |  | eq | `[[art:abbb748e:run.features#n]]` | verified | 12 |
| 16 | conceptual_soundness | The subject's feature inventory carries 12 features, of whic… | 2 | count | at_origination |  | eq | `[[art:abbb748e:run.features#at_origination]]` | verified | 2 |
| 17 | conceptual_soundness | The subject's feature inventory carries 12 features, of whic… | 10 | count | before_period_start |  | eq | `[[art:abbb748e:run.features#before_period_start]]` | verified | 10 |
| 18 | conceptual_soundness | The inventory carries 0 features drawn from inside the perfo… | 0 | count | during_period |  | eq | `[[art:abbb748e:run.features#during_period]]` | verified | 0 |
| 19 | conceptual_soundness | The inventory carries 0 features drawn from inside the perfo… | 0 | count | after_outcome |  | eq | `[[art:abbb748e:run.features#after_outcome]]` | verified | 0 |
| 20 | conceptual_soundness | The developer's own collinearity screen removed bill_last, w… | 160.9 | ratio | vif |  | eq | `[[art:3986de2e:run.model_summary#removed.bill_last.vif]]` | verified | 160.888514 |
| 21 | conceptual_soundness | The developer's own collinearity screen removed bill_last, w… | 36.36 | ratio | vif |  | eq | `[[art:3986de2e:run.model_summary#removed.utilisation_mean_6m.vif]]` | verified | 36.356335 |
| 22 | conceptual_soundness | Each was read against the screen's declared cut-off of 10 ,… | 10 | ratio | vif_threshold |  | eq | `[[art:3986de2e:run.model_summary#vif_threshold]]` | verified | 10 |
| 23 | conceptual_soundness | The largest fitted weight in magnitude is on delinq_last at… | 1.023 | ratio | coefficient |  | eq | `[[art:3986de2e:run.model_summary#coefficients.delinq_last.value]]` | verified | 1.022843626 |
| 24 | conceptual_soundness | The largest fitted weight in magnitude is on delinq_last at… | 0.4769 | ratio | coefficient |  | eq | `[[art:3986de2e:run.model_summary#coefficients.utilisation.value]]` | verified | 0.4768523065 |
| 25 | conceptual_soundness | The largest fitted weight in magnitude is on delinq_last at… | -0.2763 | ratio | coefficient |  | eq | `[[art:3986de2e:run.model_summary#coefficients.bill_mean_6m.value]]` | verified | -0.2762665658 |
| 26 | conceptual_soundness | The largest fitted weight in magnitude is on delinq_last at… | -0.218 | ratio | coefficient |  | eq | `[[art:3986de2e:run.model_summary#coefficients.bill_trend_6m.value]]` | verified | -0.2180414084 |
| 27 | conceptual_soundness | The largest fitted weight in magnitude is on delinq_last at… | -0.1725 | ratio | coefficient |  | eq | `[[art:3986de2e:run.model_summary#coefficients.pay_ratio_mean_6m.value]]` | verified | -0.1725062889 |
| 28 | conceptual_soundness | The smaller weights are on delinq_count_6m at 0.1404 , pay_r… | 0.1404 | ratio | coefficient |  | eq | `[[art:3986de2e:run.model_summary#coefficients.delinq_count_6m.value]]` | verified | 0.1403720514 |
| 29 | conceptual_soundness | The smaller weights are on delinq_count_6m at 0.1404 , pay_r… | -0.09177 | ratio | coefficient |  | eq | `[[art:3986de2e:run.model_summary#coefficients.pay_ratio_last.value]]` | verified | -0.09177201276 |
| 30 | conceptual_soundness | The smaller weights are on delinq_count_6m at 0.1404 , pay_r… | -0.07628 | ratio | coefficient |  | eq | `[[art:3986de2e:run.model_summary#coefficients.age.value]]` | verified | -0.07627794505 |
| 31 | conceptual_soundness | The smaller weights are on delinq_count_6m at 0.1404 , pay_r… | 0.01627 | ratio | coefficient |  | eq | `[[art:3986de2e:run.model_summary#coefficients.limit_bal.value]]` | verified | 0.01626754012 |
| 32 | conceptual_soundness | The smaller weights are on delinq_count_6m at 0.1404 , pay_r… | 0.01353 | ratio | coefficient |  | eq | `[[art:3986de2e:run.model_summary#coefficients.delinq_max_6m.value]]` | verified | 0.013534104 |
| 33 | conceptual_soundness | Fitted signs were compared against each feature's own univar… | 1 | count | n_disagreements | train | eq | `[[art:f96ece96:sign_check.n_disagreements]]` | verified | 1 |
| 34 | conceptual_soundness | That feature is limit_bal, whose fitted coefficient carries… | 1 | ratio | coef_sign | train | eq | `[[art:6af6aef2:sign_check.limit_bal.coef_sign]]` | verified | 1 |
| 35 | conceptual_soundness | That feature is limit_bal, whose fitted coefficient carries… | -1 | ratio | univariate_direction | train | eq | `[[art:56d284d6:sign_check.limit_bal.univariate_direction]]` | verified | -1 |
| 36 | conceptual_soundness | That feature is limit_bal, whose fitted coefficient carries… | 0 | ratio | agrees | train | eq | `[[art:0278aad1:sign_check.limit_bal.agrees]]` | verified | 0 |
| 37 | conceptual_soundness | The weight of that disagreement is small: refitting the cham… | 0.0004286 | ratio | delta_auc | test | eq | `[[art:63faa640:ablation.limit_bal.delta_auc]]` | verified | 0.0004286468792 |
| 38 | conceptual_soundness | The weight of that disagreement is small: refitting the cham… | 0.748 | ratio | baseline_auc | test | eq | `[[art:3a44e438:ablation.baseline_auc]]` | verified | 0.7479888042 |
| 39 | conceptual_soundness | Every other retained feature agrees with its univariate dire… | 1 | ratio | agrees | train | eq | `[[art:a8ba9372:sign_check.delinq_last.agrees]]` | verified | 1 |
| 40 | conceptual_soundness | Every other retained feature agrees with its univariate dire… | 1 | ratio | agrees | train | eq | `[[art:d0c9a130:sign_check.utilisation.agrees]]` | verified | 1 |
| 41 | conceptual_soundness | Every other retained feature agrees with its univariate dire… | 1 | ratio | agrees | train | eq | `[[art:7e9a76ca:sign_check.pay_ratio_mean_6m.agrees]]` | verified | 1 |
| 42 | conceptual_soundness | Every other retained feature agrees with its univariate dire… | 1 | ratio | agrees | train | eq | `[[art:89279c3b:sign_check.bill_mean_6m.agrees]]` | verified | 1 |
| 43 | conceptual_soundness | Every other retained feature agrees with its univariate dire… | 1 | ratio | agrees | train | eq | `[[art:4116add1:sign_check.age.agrees]]` | verified | 1 |
| 44 | conceptual_soundness | The features carrying discrimination, judged by refitting th… | 0.748 | ratio | baseline_auc | test | eq | `[[art:3a44e438:ablation.baseline_auc]]` | verified | 0.7479888042 |
| 45 | conceptual_soundness | The features carrying discrimination, judged by refitting th… | -0.07585 | ratio | delta_auc | test | eq | `[[art:3150b111:ablation.delinq_last.delta_auc]]` | verified | -0.07585263733 |
| 46 | conceptual_soundness | The features carrying discrimination, judged by refitting th… | -0.01977 | ratio | delta_auc | test | eq | `[[art:d4ad2039:ablation.utilisation.delta_auc]]` | verified | -0.01976623436 |
| 47 | conceptual_soundness | The features carrying discrimination, judged by refitting th… | -0.0016 | ratio | delta_auc | test | eq | `[[art:3b91a889:ablation.bill_mean_6m.delta_auc]]` | verified | -0.001599771388 |
| 48 | conceptual_soundness | Dropping any of the remaining features leaves test AUC no lo… | 0.006603 | ratio | delta_auc | test | eq | `[[art:90fa1178:ablation.pay_ratio_mean_6m.delta_auc]]` | verified | 0.006603203115 |
| 49 | conceptual_soundness | Dropping any of the remaining features leaves test AUC no lo… | 0.003279 | ratio | delta_auc | test | eq | `[[art:096d7f98:ablation.bill_trend_6m.delta_auc]]` | verified | 0.003278638332 |
| 50 | conceptual_soundness | Dropping any of the remaining features leaves test AUC no lo… | 0.002411 | ratio | delta_auc | test | eq | `[[art:5f39089e:ablation.pay_ratio_last.delta_auc]]` | verified | 0.002411138695 |
| 51 | conceptual_soundness | Dropping any of the remaining features leaves test AUC no lo… | 0.0006812 | ratio | delta_auc | test | eq | `[[art:c5659def:ablation.delinq_count_6m.delta_auc]]` | verified | 0.0006812423615 |
| 52 | conceptual_soundness | Dropping any of the remaining features leaves test AUC no lo… | 0.0004286 | ratio | delta_auc | test | eq | `[[art:63faa640:ablation.limit_bal.delta_auc]]` | verified | 0.0004286468792 |
| 53 | conceptual_soundness | Dropping any of the remaining features leaves test AUC no lo… | 0.0003598 | ratio | delta_auc | test | eq | `[[art:3a0d3a0c:ablation.delinq_max_6m.delta_auc]]` | verified | 0.0003597572022 |
| 54 | conceptual_soundness | Dropping any of the remaining features leaves test AUC no lo… | 8.675e-05 | ratio | delta_auc | test | eq | `[[art:59398b1b:ablation.age.delta_auc]]` | verified | 8.674996364e-05 |
| 55 | conceptual_soundness | The challenger reaches a test AUC of 0.824 against the champ… | 0.824 | ratio | auc | test | eq | `[[art:bf5be719:challenger.auc]]` | verified | 0.823969015 |
| 56 | conceptual_soundness | The challenger reaches a test AUC of 0.824 against the champ… | 0.7764 | ratio | auc | test | eq | `[[art:06c7c666:metrics.test.auc]]` | verified | 0.7763713511 |
| 57 | conceptual_soundness | The challenger reaches a test AUC of 0.824 against the champ… | 0.0476 | ratio | delta_auc | test | eq | `[[art:a86db8b1:challenger.delta_auc]]` | verified | 0.04759766387 |
| 58 | conceptual_soundness | That difference is read against the declared effective-chall… | 0.03 | ratio | delta_auc | test | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 59 | conceptual_soundness | On the scoring-rule comparison the challenger is also the be… | 0.1258 | ratio | brier | test | eq | `[[art:f9e0583d:challenger.brier]]` | verified | 0.1258050391 |
| 60 | conceptual_soundness | On the scoring-rule comparison the challenger is also the be… | 0.1929 | ratio | brier | test | eq | `[[art:2f64a7ce:metrics.test.brier]]` | verified | 0.1928760509 |
| 61 | data_integrity | The training split holds 3500 rows and the test split holds… | 3500 | count | n | train | eq | `[[art:2510d49d:profile.train.n]]` | verified | 3500 |
| 62 | data_integrity | The training split holds 3500 rows and the test split holds… | 1500 | count | n | test | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 63 | data_integrity | The largest missing fraction in the training split is 0 , an… | 0 | ratio | missing_max | train | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 64 | data_integrity | The largest missing fraction in the training split is 0 , an… | 0 | ratio | missing_max | test | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 65 | data_integrity | The two maxima stand at the same value, so the gap between t… | 0.1 | ratio | missing_gap |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 66 | data_integrity | Stability is read from the training split against the other… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 67 | data_integrity | Stability is read from the training split against the other… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 68 | data_integrity | The largest train-to-test population stability index, the sc… | 0.01095 | ratio | psi |  | eq | `[[art:381b2570:psi.max]]` | verified | 0.01095273358 |
| 69 | data_integrity | Among the individual features, the population stability inde… | 0.01095 | ratio | psi |  | eq | `[[art:601cdba2:psi.limit_bal]]` | verified | 0.01095273358 |
| 70 | data_integrity | Among the individual features, the population stability inde… | 0.00958 | ratio | psi |  | eq | `[[art:c247a6f2:psi.bill_trend_6m]]` | verified | 0.009579614525 |
| 71 | data_integrity | Among the individual features, the population stability inde… | 0.008124 | ratio | psi |  | eq | `[[art:f9255a0a:psi.age]]` | verified | 0.008124281436 |
| 72 | data_integrity | Among the individual features, the population stability inde… | 0.007124 | ratio | psi |  | eq | `[[art:028e4281:psi.bill_mean_6m]]` | verified | 0.007124196275 |
| 73 | data_integrity | Among the individual features, the population stability inde… | 0.0055 | ratio | psi |  | eq | `[[art:2c5baeb2:psi.pay_ratio_mean_6m]]` | verified | 0.005500252946 |
| 74 | data_integrity | Among the individual features, the population stability inde… | 0.005498 | ratio | psi |  | eq | `[[art:7a82e7f3:psi.delinq_max_6m]]` | verified | 0.005498249408 |
| 75 | data_integrity | The remainder are smaller still, at 0.004966 for pay_ratio_l… | 0.004966 | ratio | psi |  | eq | `[[art:3af2ca29:psi.pay_ratio_last]]` | verified | 0.00496591109 |
| 76 | data_integrity | The remainder are smaller still, at 0.004966 for pay_ratio_l… | 0.004244 | ratio | psi |  | eq | `[[art:451e0780:psi.utilisation]]` | verified | 0.0042440485 |
| 77 | data_integrity | The remainder are smaller still, at 0.004966 for pay_ratio_l… | 0.00285 | ratio | psi |  | eq | `[[art:03bd52e7:psi.delinq_last]]` | verified | 0.002849633848 |
| 78 | data_integrity | The remainder are smaller still, at 0.004966 for pay_ratio_l… | 0.002069 | ratio | psi |  | eq | `[[art:61491d02:psi.delinq_count_6m]]` | verified | 0.002069275496 |
| 79 | data_integrity | The remainder are smaller still, at 0.004966 for pay_ratio_l… | 0.005049 | ratio | psi |  | eq | `[[art:a8375d0f:psi.y_score]]` | verified | 0.005049433774 |
| 80 | data_integrity | The largest characteristic stability index, measuring a feat… | 0.03295 | ratio | csi |  | eq | `[[art:e1f1ad3d:csi.max]]` | verified | 0.0329489964 |
| 81 | data_integrity | The largest characteristic stability index, measuring a feat… | 0.03295 | ratio | csi |  | eq | `[[art:39b31d8e:csi.delinq_last]]` | verified | 0.0329489964 |
| 82 | data_integrity | That value sits below the declared stability bound of 0.25 ,… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 83 | data_integrity | That value sits below the declared stability bound of 0.25 ,… | 0.00724 | ratio | csi |  | eq | `[[art:0a1f2306:csi.utilisation]]` | verified | 0.007240075813 |
| 84 | data_integrity | That value sits below the declared stability bound of 0.25 ,… | 0.006203 | ratio | csi |  | eq | `[[art:2567a75c:csi.bill_trend_6m]]` | verified | 0.006203453095 |
| 85 | data_integrity | That value sits below the declared stability bound of 0.25 ,… | 0.002804 | ratio | csi |  | eq | `[[art:b0282e56:csi.delinq_count_6m]]` | verified | 0.002804356526 |
| 86 | data_integrity | That value sits below the declared stability bound of 0.25 ,… | 0.001757 | ratio | csi |  | eq | `[[art:278c2a6d:csi.bill_mean_6m]]` | verified | 0.00175661912 |
| 87 | data_integrity | That value sits below the declared stability bound of 0.25 ,… | 0.001721 | ratio | csi |  | eq | `[[art:fd186b68:csi.pay_ratio_last]]` | verified | 0.001720891957 |
| 88 | data_integrity | That value sits below the declared stability bound of 0.25 ,… | 0.001075 | ratio | csi |  | eq | `[[art:1642e34e:csi.age]]` | verified | 0.001074651834 |
| 89 | data_integrity | That value sits below the declared stability bound of 0.25 ,… | 0.0008584 | ratio | csi |  | eq | `[[art:659995f7:csi.pay_ratio_mean_6m]]` | verified | 0.0008583980615 |
| 90 | data_integrity | That value sits below the declared stability bound of 0.25 ,… | 0.0003766 | ratio | csi |  | eq | `[[art:3fc49a03:csi.delinq_max_6m]]` | verified | 0.0003766337845 |
| 91 | data_integrity | That value sits below the declared stability bound of 0.25 ,… | 0.0002712 | ratio | csi |  | eq | `[[art:bc85c1c5:csi.limit_bal]]` | verified | 0.0002712443929 |
| 92 | data_integrity | The timing screen counts 0 features declared as observed dur… | 0 | count | n_flagged |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 93 | data_integrity | The strongest single feature reaches an area under the curve… | 0.6831 | ratio | auc |  | eq | `[[art:fd829fc4:leakage.target_corr.max_single_feature_auc]]` | verified | 0.6831414154 |
| 94 | data_integrity | The strongest single feature reaches an area under the curve… | 0.9 | ratio | auc |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 95 | data_integrity | On the identifier arm, the share of test rows whose client i… | 0 | ratio | overlap |  | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 96 | data_integrity | On the identifier arm, the share of test rows whose client i… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 97 | data_integrity | On the feature-vector arm, the share of test rows whose feat… | 0 | ratio | overlap |  | eq | `[[art:0fec8048:leakage.overlap.features]]` | verified | 0 |
| 98 | data_integrity | On the feature-vector arm, the share of test rows whose feat… | 0.005 | ratio | overlap |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 99 | data_integrity | That applied bound takes the declared contamination bound as… | 0 | ratio | duplicates | train | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 100 | data_integrity | That applied bound takes the declared contamination bound as… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 101 | data_integrity | The overall overlap screen returns the same share of test ro… | 0 | ratio | overlap |  | eq | `[[art:4c9fcd09:leakage.overlap]]` | verified | 0 |
| 102 | data_integrity | The overall overlap screen returns the same share of test ro… | 0.005 | ratio | overlap |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 103 | data_integrity | The name screen matches 0 feature names against the target-a… | 0 | count | n_matched |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 104 | outcomes | This section reports discrimination first and calibration se… | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 105 | outcomes | This section reports discrimination first and calibration se… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 106 | outcomes | \| Rows \| 3500 \| 1500 \| | 3500 | count | n | train | eq | `[[art:564683ee:metrics.train.n]]` | verified | 3500 |
| 107 | outcomes | \| Rows \| 3500 \| 1500 \| | 1500 | count | n | test | eq | `[[art:64fcf14d:metrics.test.n]]` | verified | 1500 |
| 108 | outcomes | \| Observed event rate \| 0.2246 \| 0.2247 \| | 0.2246 | ratio | event_rate | train | eq | `[[art:133a5ff8:metrics.train.event_rate]]` | verified | 0.2245714286 |
| 109 | outcomes | \| Observed event rate \| 0.2246 \| 0.2247 \| | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 110 | outcomes | \| AUC \| 0.7765 \| 0.7764 \| | 0.7765 | ratio | auc | train | eq | `[[art:0e7355aa:metrics.train.auc]]` | verified | 0.7765019192 |
| 111 | outcomes | \| AUC \| 0.7765 \| 0.7764 \| | 0.7764 | ratio | auc | test | eq | `[[art:06c7c666:metrics.test.auc]]` | verified | 0.7763713511 |
| 112 | outcomes | \| Gini \| 0.553 \| 0.5527 \| | 0.553 | ratio | gini | train | eq | `[[art:1e398595:metrics.train.gini]]` | verified | 0.5530038384 |
| 113 | outcomes | \| Gini \| 0.553 \| 0.5527 \| | 0.5527 | ratio | gini | test | eq | `[[art:bc939097:metrics.test.gini]]` | verified | 0.5527427022 |
| 114 | outcomes | \| KS \| 0.4801 \| 0.4656 \| | 0.4801 | ratio | ks | train | eq | `[[art:97bd5dab:metrics.train.ks]]` | verified | 0.4800544158 |
| 115 | outcomes | \| KS \| 0.4801 \| 0.4656 \| | 0.4656 | ratio | ks | test | eq | `[[art:f4b92d62:metrics.test.ks]]` | verified | 0.4656278784 |
| 116 | outcomes | \| Brier \| 0.1969 \| 0.1929 \| | 0.1969 | ratio | brier | train | eq | `[[art:f118c784:metrics.train.brier]]` | verified | 0.1968893522 |
| 117 | outcomes | \| Brier \| 0.1969 \| 0.1929 \| | 0.1929 | ratio | brier | test | eq | `[[art:2f64a7ce:metrics.test.brier]]` | verified | 0.1928760509 |
| 118 | outcomes | \| Log loss \| 0.6031 \| 0.5935 \| | 0.6031 | ratio | logloss | train | eq | `[[art:dcbefb71:metrics.train.logloss]]` | verified | 0.6031246073 |
| 119 | outcomes | \| Log loss \| 0.6031 \| 0.5935 \| | 0.5935 | ratio | logloss | test | eq | `[[art:6ac37fc1:metrics.test.logloss]]` | verified | 0.5935045602 |
| 120 | outcomes | \| Mean predicted probability \| 0.4427 \| 0.4379 \| | 0.4427 | ratio | mean_predicted | train | eq | `[[art:bbe07926:metrics.train.mean_predicted]]` | verified | 0.4427489586 |
| 121 | outcomes | \| Mean predicted probability \| 0.4427 \| 0.4379 \| | 0.4379 | ratio | mean_predicted | test | eq | `[[art:aa68c658:metrics.test.mean_predicted]]` | verified | 0.4379028765 |
| 122 | outcomes | The top two deciles hold 0.4451 of the events on test and 0.… | 0.4451 | ratio | top2_capture | test | eq | `[[art:e3b6058b:deciles.test.top2_capture]]` | verified | 0.4451038576 |
| 123 | outcomes | The top two deciles hold 0.4451 of the events on test and 0.… | 0.4262 | ratio | top2_capture | train | eq | `[[art:1693b145:deciles.train.top2_capture]]` | verified | 0.4262086514 |
| 124 | outcomes | The movement in AUC between the two splits is read against a… | 0.08 | ratio | auc_gap |  | eq | `[[art:630f28f4:threshold.O1.auc_gap]]` | verified | 0.08 |
| 125 | outcomes | AUC is 0.7765 on train and 0.7764 on test, so the evaluation… | 0.7765 | ratio | auc | train | eq | `[[art:0e7355aa:metrics.train.auc]]` | verified | 0.7765019192 |
| 126 | outcomes | AUC is 0.7765 on train and 0.7764 on test, so the evaluation… | 0.7764 | ratio | auc | test | eq | `[[art:06c7c666:metrics.test.auc]]` | verified | 0.7763713511 |
| 127 | outcomes | KS is lower on test at 0.4656 than on train at 0.4801 , whil… | 0.4656 | ratio | ks | test | eq | `[[art:f4b92d62:metrics.test.ks]]` | verified | 0.4656278784 |
| 128 | outcomes | KS is lower on test at 0.4656 than on train at 0.4801 , whil… | 0.4801 | ratio | ks | train | eq | `[[art:97bd5dab:metrics.train.ks]]` | verified | 0.4800544158 |
| 129 | outcomes | On test the slope is 0.7952 , below the developer-declared m… | 0.7952 | ratio | calibration_slope | test | eq | `[[art:b2bc94fc:calibration_slope.test]]` | verified | 0.7952064062 |
| 130 | outcomes | On test the slope is 0.7952 , below the developer-declared m… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 131 | outcomes | On test the slope is 0.7952 , below the developer-declared m… | 0.8 | ratio | calibration_slope |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 132 | outcomes | On test the slope is 0.7952 , below the developer-declared m… | 1.2 | ratio | calibration_slope |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 133 | outcomes | On train the slope is 0.7656 , also below that band, and it… | 0.7656 | ratio | calibration_slope | train | eq | `[[art:1151c8e4:calibration_slope.train]]` | verified | 0.7656065242 |
| 134 | outcomes | The intercept of the same regression is -1.217 on test and -… | -1.217 | ratio | calibration_intercept | test | eq | `[[art:62851316:calibration_intercept.test]]` | verified | -1.21748713 |
| 135 | outcomes | The intercept of the same regression is -1.217 on test and -… | -1.241 | ratio | calibration_intercept | train | eq | `[[art:849b7b2e:calibration_intercept.train]]` | verified | -1.240800979 |
| 136 | outcomes | The mean predicted probability on test, 0.4379 , stands abov… | 0.4379 | ratio | mean_predicted | test | eq | `[[art:aa68c658:metrics.test.mean_predicted]]` | verified | 0.4379028765 |
| 137 | outcomes | The mean predicted probability on test, 0.4379 , stands abov… | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 138 | outcomes | The mean predicted probability on test, 0.4379 , stands abov… | 0.9491 | ratio | mean_rel_gap | test | eq | `[[art:376ae2d7:calibration.mean_rel_gap.test]]` | verified | 0.9491225955 |
| 139 | outcomes | The mean predicted probability on test, 0.4379 , stands abov… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 140 | outcomes | On train the mean predicted probability is 0.4427 against an… | 0.4427 | ratio | mean_predicted | train | eq | `[[art:bbe07926:metrics.train.mean_predicted]]` | verified | 0.4427489586 |
| 141 | outcomes | On train the mean predicted probability is 0.4427 against an… | 0.2246 | ratio | event_rate | train | eq | `[[art:133a5ff8:metrics.train.event_rate]]` | verified | 0.2245714286 |
| 142 | outcomes | On train the mean predicted probability is 0.4427 against an… | 0.9715 | ratio | mean_rel_gap | train | eq | `[[art:0abea673:calibration.mean_rel_gap.train]]` | verified | 0.9715284416 |
| 143 | outcomes | AUC on this slice is 0.5865 , falling below the split's own… | 0.5865 | ratio | auc | test | eq | `[[art:015b00e8:metrics.test.sub.utilisation_high.auc]]` | verified | 0.5865242236 |
| 144 | outcomes | AUC on this slice is 0.5865 , falling below the split's own… | 0.1898 | ratio | auc_gap | test | eq | `[[art:fcca7c35:metrics.test.sub.utilisation_high.auc_gap]]` | verified | 0.1898471275 |
| 145 | outcomes | AUC on this slice is 0.5865 , falling below the split's own… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 146 | outcomes | The slice holds 0.5 of the split, above the floor of 0.1 a s… | 0.5 | ratio | share | test | eq | `[[art:9404484e:metrics.test.sub.utilisation_high.share]]` | verified | 0.5 |
| 147 | outcomes | The slice holds 0.5 of the split, above the floor of 0.1 a s… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 148 | outcomes | The slice holds 0.5 of the split, above the floor of 0.1 a s… | 0.95 | ratio | slice_max_share |  | eq | `[[art:a928a05c:threshold.O1.slice_max_share]]` | verified | 0.95 |
| 149 | outcomes | Mean predicted probability here is 0.4918 against an observe… | 0.4918 | ratio | mean_predicted | test | eq | `[[art:f1d1d4d2:metrics.test.sub.utilisation_high.mean_predicted]]` | verified | 0.4918161846 |
| 150 | outcomes | Mean predicted probability here is 0.4918 against an observe… | 0.2333 | ratio | event_rate | test | eq | `[[art:8e66209c:metrics.test.sub.utilisation_high.event_rate]]` | verified | 0.2333333333 |
| 151 | outcomes | Mean predicted probability here is 0.4918 against an observe… | 1.108 | ratio | mean_rel_gap | test | eq | `[[art:40cb08f4:metrics.test.sub.utilisation_high.mean_rel_gap]]` | verified | 1.107783648 |
| 152 | outcomes | AUC on this slice is 0.9086 and does not fall below the spli… | 0.9086 | ratio | auc | test | eq | `[[art:d408b939:metrics.test.sub.utilisation_low.auc]]` | verified | 0.9085726883 |
| 153 | outcomes | AUC on this slice is 0.9086 and does not fall below the spli… | -0.1322 | ratio | auc_gap | test | eq | `[[art:bf57d590:metrics.test.sub.utilisation_low.auc_gap]]` | verified | -0.1322013373 |
| 154 | outcomes | AUC on this slice is 0.9086 and does not fall below the spli… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 155 | outcomes | The slice holds 0.5 of the split, above the floor of 0.1 . | 0.5 | ratio | share | test | eq | `[[art:7860a748:metrics.test.sub.utilisation_low.share]]` | verified | 0.5 |
| 156 | outcomes | The slice holds 0.5 of the split, above the floor of 0.1 . | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 157 | outcomes | Mean predicted probability is 0.384 against an observed rate… | 0.384 | ratio | mean_predicted | test | eq | `[[art:5d54c6cf:metrics.test.sub.utilisation_low.mean_predicted]]` | verified | 0.3839895683 |
| 158 | outcomes | Mean predicted probability is 0.384 against an observed rate… | 0.216 | ratio | event_rate | test | eq | `[[art:b0ad49be:metrics.test.sub.utilisation_low.event_rate]]` | verified | 0.216 |
| 159 | outcomes | Mean predicted probability is 0.384 against an observed rate… | 0.7777 | ratio | mean_rel_gap | test | eq | `[[art:d873908a:metrics.test.sub.utilisation_low.mean_rel_gap]]` | verified | 0.777729483 |
| 160 | outcomes | AUC on this slice is 0.7838 and does not fall below the spli… | 0.7838 | ratio | auc | test | eq | `[[art:b14bb20b:metrics.test.sub.limit_bal_low.auc]]` | verified | 0.7838252922 |
| 161 | outcomes | AUC on this slice is 0.7838 and does not fall below the spli… | -0.007454 | ratio | auc_gap | test | eq | `[[art:69d61c38:metrics.test.sub.limit_bal_low.auc_gap]]` | verified | -0.007453941099 |
| 162 | outcomes | AUC on this slice is 0.7838 and does not fall below the spli… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 163 | outcomes | The slice holds 0.504 of the split, above the floor of 0.1 . | 0.504 | ratio | share | test | eq | `[[art:bac689cc:metrics.test.sub.limit_bal_low.share]]` | verified | 0.504 |
| 164 | outcomes | The slice holds 0.504 of the split, above the floor of 0.1 . | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 165 | outcomes | Mean predicted probability is 0.4709 against an observed rat… | 0.4709 | ratio | mean_predicted | test | eq | `[[art:1cae8978:metrics.test.sub.limit_bal_low.mean_predicted]]` | verified | 0.4708680099 |
| 166 | outcomes | Mean predicted probability is 0.4709 against an observed rat… | 0.2487 | ratio | event_rate | test | eq | `[[art:de78adb5:metrics.test.sub.limit_bal_low.event_rate]]` | verified | 0.2486772487 |
| 167 | outcomes | Mean predicted probability is 0.4709 against an observed rat… | 0.8935 | ratio | mean_rel_gap | test | eq | `[[art:07e1da50:metrics.test.sub.limit_bal_low.mean_rel_gap]]` | verified | 0.8934905081 |
| 168 | outcomes | AUC on this slice is 0.735 , falling below the split's own A… | 0.735 | ratio | auc | test | eq | `[[art:8578b988:metrics.test.sub.delinq_count_6m_high.auc]]` | verified | 0.7350292398 |
| 169 | outcomes | AUC on this slice is 0.735 , falling below the split's own A… | 0.04134 | ratio | auc_gap | test | eq | `[[art:39738a6e:metrics.test.sub.delinq_count_6m_high.auc_gap]]` | verified | 0.04134211131 |
| 170 | outcomes | AUC on this slice is 0.735 , falling below the split's own A… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 171 | outcomes | The slice holds 0.3667 of the split, above the floor of 0.1… | 0.3667 | ratio | share | test | eq | `[[art:22847310:metrics.test.sub.delinq_count_6m_high.share]]` | verified | 0.3666666667 |
| 172 | outcomes | The slice holds 0.3667 of the split, above the floor of 0.1… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 173 | outcomes | Mean predicted probability is 0.5805 against an observed rat… | 0.5805 | ratio | mean_predicted | test | eq | `[[art:6e2677ac:metrics.test.sub.delinq_count_6m_high.mean_predicted]]` | verified | 0.5804689313 |
| 174 | outcomes | Mean predicted probability is 0.5805 against an observed rat… | 0.3455 | ratio | event_rate | test | eq | `[[art:ef17c303:metrics.test.sub.delinq_count_6m_high.event_rate]]` | verified | 0.3454545455 |
| 175 | outcomes | Mean predicted probability is 0.5805 against an observed rat… | 0.6803 | ratio | mean_rel_gap | test | eq | `[[art:58e32501:metrics.test.sub.delinq_count_6m_high.mean_rel_gap]]` | verified | 0.6803048011 |
| 176 | sensitivity | The largest variance inflation factor over the retained feat… | 7.295 | ratio | vif | train | eq | `[[art:9ae7c45b:vif.max]]` | verified | 7.295299885 |
| 177 | sensitivity | The largest variance inflation factor over the retained feat… | 10 | ratio | vif |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 178 | sensitivity | That maximum is attained by the six-month mean billed amount… | 7.295 | ratio | vif | train | eq | `[[art:f0a2f865:vif.bill_mean_6m]]` | verified | 7.295299885 |
| 179 | sensitivity | That maximum is attained by the six-month mean billed amount… | 7.264 | ratio | vif | train | eq | `[[art:c2de8dfe:vif.pay_ratio_last]]` | verified | 7.264342098 |
| 180 | sensitivity | That maximum is attained by the six-month mean billed amount… | 7.259 | ratio | vif | train | eq | `[[art:e39c3e82:vif.pay_ratio_mean_6m]]` | verified | 7.25926398 |
| 181 | sensitivity | The credit limit follows at 4.803 and utilisation at 3.215 ,… | 4.803 | ratio | vif | train | eq | `[[art:ddfdcc3c:vif.limit_bal]]` | verified | 4.803401129 |
| 182 | sensitivity | The credit limit follows at 4.803 and utilisation at 3.215 ,… | 3.215 | ratio | vif | train | eq | `[[art:536fdb6f:vif.utilisation]]` | verified | 3.215148369 |
| 183 | sensitivity | The delinquency features are lower still, at 2.561 for the s… | 2.561 | ratio | vif | train | eq | `[[art:38974def:vif.delinq_count_6m]]` | verified | 2.561484187 |
| 184 | sensitivity | The delinquency features are lower still, at 2.561 for the s… | 2.408 | ratio | vif | train | eq | `[[art:71aaaf11:vif.delinq_max_6m]]` | verified | 2.40773 |
| 185 | sensitivity | The delinquency features are lower still, at 2.561 for the s… | 1.412 | ratio | vif | train | eq | `[[art:48733638:vif.delinq_last]]` | verified | 1.411555667 |
| 186 | sensitivity | The six-month billing trend at 1.201 and age at 1.002 are th… | 1.201 | ratio | vif | train | eq | `[[art:9356a256:vif.bill_trend_6m]]` | verified | 1.201449441 |
| 187 | sensitivity | The six-month billing trend at 1.201 and age at 1.002 are th… | 1.002 | ratio | vif | train | eq | `[[art:74c06cad:vif.age]]` | verified | 1.001957997 |
| 188 | sensitivity | Belsley's condition number of the column-standardised design… | 5.547 | ratio | condition_number |  | eq | `[[art:e41b9562:condition_number]]` | verified | 5.546934633 |
| 189 | sensitivity | Belsley's condition number of the column-standardised design… | 30 | ratio | condition_number |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 190 | findings | The package declares a minimum calibration slope on test of… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 191 | findings | The slope recomputed by this validation on test is 0.7952 ,… | 0.7952 | ratio | calibration_slope | test | eq | `[[art:b2bc94fc:calibration_slope.test]]` | verified | 0.7952064062 |
| 192 | findings | The calibration slope on train is 0.7656 and on test is 0.79… | 0.7656 | ratio | calibration_slope | train | eq | `[[art:1151c8e4:calibration_slope.train]]` | verified | 0.7656065242 |
| 193 | findings | The calibration slope on train is 0.7656 and on test is 0.79… | 0.7952 | ratio | calibration_slope | test | eq | `[[art:b2bc94fc:calibration_slope.test]]` | verified | 0.7952064062 |
| 194 | findings | The calibration slope on train is 0.7656 and on test is 0.79… | 0.8 | ratio | calibration_slope |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 195 | findings | On train the mean predicted probability is 0.4427 against an… | 0.4427 | ratio | mean_predicted | train | eq | `[[art:bbe07926:metrics.train.mean_predicted]]` | verified | 0.4427489586 |
| 196 | findings | On train the mean predicted probability is 0.4427 against an… | 0.2246 | ratio | event_rate | train | eq | `[[art:133a5ff8:metrics.train.event_rate]]` | verified | 0.2245714286 |
| 197 | findings | On train the mean predicted probability is 0.4427 against an… | 0.9715 | ratio | mean_rel_gap | train | eq | `[[art:0abea673:calibration.mean_rel_gap.train]]` | verified | 0.9715284416 |
| 198 | findings | On train the mean predicted probability is 0.4427 against an… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 199 | findings | On test the mean predicted probability is 0.4379 against an… | 0.4379 | ratio | mean_predicted | test | eq | `[[art:aa68c658:metrics.test.mean_predicted]]` | verified | 0.4379028765 |
| 200 | findings | On test the mean predicted probability is 0.4379 against an… | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 201 | findings | On test the mean predicted probability is 0.4379 against an… | 0.9491 | ratio | mean_rel_gap | test | eq | `[[art:376ae2d7:calibration.mean_rel_gap.test]]` | verified | 0.9491225955 |
| 202 | findings | The champion's AUC on test is 0.7764 , while a histogram gra… | 0.7764 | ratio | auc | test | eq | `[[art:06c7c666:metrics.test.auc]]` | verified | 0.7763713511 |
| 203 | findings | The champion's AUC on test is 0.7764 , while a histogram gra… | 0.824 | ratio | auc | test | eq | `[[art:bf5be719:challenger.auc]]` | verified | 0.823969015 |
| 204 | findings | The challenger's lead over the champion is 0.0476 , above th… | 0.0476 | ratio | delta_auc | test | eq | `[[art:a86db8b1:challenger.delta_auc]]` | verified | 0.04759766387 |
| 205 | findings | The challenger's lead over the champion is 0.0476 , above th… | 0.03 | ratio | delta_auc |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 206 | findings | For the model developer: within the test segment defined by… | 0.5 | ratio | share | test | eq | `[[art:9404484e:metrics.test.sub.utilisation_high.share]]` | verified | 0.5 |
| 207 | findings | For the model developer: within the test segment defined by… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 208 | findings | For the model developer: within the test segment defined by… | 0.5865 | ratio | auc | test | eq | `[[art:015b00e8:metrics.test.sub.utilisation_high.auc]]` | verified | 0.5865242236 |
| 209 | findings | For the model developer: within the test segment defined by… | 0.7764 | ratio | auc | test | eq | `[[art:06c7c666:metrics.test.auc]]` | verified | 0.7763713511 |
| 210 | findings | For the model developer: within the test segment defined by… | 0.1898 | ratio | auc_gap | test | eq | `[[art:fcca7c35:metrics.test.sub.utilisation_high.auc_gap]]` | verified | 0.1898471275 |
| 211 | findings | For the model developer: within the test segment defined by… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 212 | findings | For the model developer: the fitted coefficient on `limit_ba… | 1 | ratio | coef_sign |  | eq | `[[art:6af6aef2:sign_check.limit_bal.coef_sign]]` | verified | 1 |
| 213 | findings | For the model developer: the fitted coefficient on `limit_ba… | -1 | ratio | univariate_direction |  | eq | `[[art:56d284d6:sign_check.limit_bal.univariate_direction]]` | verified | -1 |
| 214 | findings | For the model developer: the fitted coefficient on `limit_ba… | 0 | ratio | agrees |  | eq | `[[art:0278aad1:sign_check.limit_bal.agrees]]` | verified | 0 |
| 215 | monitoring | Rank-ordering should be recomputed on each production vintag… | 0.7 | ratio | auc | test | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 216 | monitoring | The validation-time discrimination value of 0.7764 is the re… | 0.7764 | ratio | auc | test | eq | `[[art:06c7c666:metrics.test.auc]]` | verified | 0.7763713511 |
| 217 | monitoring | Probability accuracy should be tracked with the Brier score… | 0.2 | ratio | brier | test | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 218 | monitoring | Probability accuracy should be tracked with the Brier score… | 0.1929 | ratio | brier | test | eq | `[[art:2f64a7ce:metrics.test.brier]]` | verified | 0.1928760509 |
| 219 | monitoring | Calibration should be tracked with the regression slope of t… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 220 | monitoring | Calibration should be tracked with the regression slope of t… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 221 | monitoring | The validation-time slope of 0.7952 lies below the lower end… | 0.7952 | ratio | calibration_slope | test | eq | `[[art:b2bc94fc:calibration_slope.test]]` | verified | 0.7952064062 |
| 222 | monitoring | Population stability should be tracked with the same shift s… | 0.01095 | ratio | psi |  | eq | `[[art:381b2570:psi.max]]` | verified | 0.01095273358 |
| 223 | monitoring | Population stability should be tracked with the same shift s… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 224 | monitoring | Monitoring should recompute that statistic monthly for every… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 225 | monitoring | The observed event rate on the evaluation split used in this… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 226 | monitoring | For a future production cohort whose observed event rate fal… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |

## Appendix B — Artifact index

The store holds 219 artifacts; the 149 this report cites or rests a finding on are indexed here.

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
| `calibration.mean_rel_gap.test` | `376ae2d7` | scalar | 0.9491225955 | mean predicted against observed on test, relative |
| `calibration.mean_rel_gap.train` | `0abea673` | scalar | 0.9715284416 | mean predicted against observed on train, relative |
| `calibration.test` | `ffcc3994` | table | table, 10 rows | calibration by decile of predicted probability on test |
| `calibration.train` | `34673c01` | table | table, 10 rows | calibration by decile of predicted probability on train |
| `calibration_intercept.test` | `62851316` | scalar | -1.21748713 | logistic regression of the outcome on logit(p) on test: the intercept |
| `calibration_intercept.train` | `849b7b2e` | scalar | -1.240800979 | logistic regression of the outcome on logit(p) on train: the intercept |
| `calibration_slope.test` | `b2bc94fc` | scalar | 0.7952064062 | logistic regression of the outcome on logit(p) on test: the slope |
| `calibration_slope.train` | `1151c8e4` | scalar | 0.7656065242 | logistic regression of the outcome on logit(p) on train: the slope |
| `challenger.auc` | `bf5be719` | scalar | 0.823969015 | the challenger's AUC on test |
| `challenger.brier` | `f9e0583d` | scalar | 0.1258050391 | the challenger's Brier score on test |
| `challenger.delta_auc` | `a86db8b1` | scalar | 0.04759766387 | the challenger's AUC on test minus the champion's |
| `condition_number` | `e41b9562` | scalar | 5.546934633 | Belsley's condition number of the column-standardised design |
| `csi.age` | `1642e34e` | scalar | 0.001074651834 | CSI of age: its contribution to the shift in the linear predictor |
| `csi.bill_mean_6m` | `278c2a6d` | scalar | 0.00175661912 | CSI of bill_mean_6m: its contribution to the shift in the linear predictor |
| `csi.bill_trend_6m` | `2567a75c` | scalar | 0.006203453095 | CSI of bill_trend_6m: its contribution to the shift in the linear predictor |
| `csi.delinq_count_6m` | `b0282e56` | scalar | 0.002804356526 | CSI of delinq_count_6m: its contribution to the shift in the linear predictor |
| `csi.delinq_last` | `39b31d8e` | scalar | 0.0329489964 | CSI of delinq_last: its contribution to the shift in the linear predictor |
| `csi.delinq_max_6m` | `3fc49a03` | scalar | 0.0003766337845 | CSI of delinq_max_6m: its contribution to the shift in the linear predictor |
| `csi.limit_bal` | `bc85c1c5` | scalar | 0.0002712443929 | CSI of limit_bal: its contribution to the shift in the linear predictor |
| `csi.max` | `e1f1ad3d` | scalar | 0.0329489964 | the largest characteristic stability index |
| `csi.pay_ratio_last` | `fd186b68` | scalar | 0.001720891957 | CSI of pay_ratio_last: its contribution to the shift in the linear predictor |
| `csi.pay_ratio_mean_6m` | `659995f7` | scalar | 0.0008583980615 | CSI of pay_ratio_mean_6m: its contribution to the shift in the linear predictor |
| `csi.utilisation` | `0a1f2306` | scalar | 0.007240075813 | CSI of utilisation: its contribution to the shift in the linear predictor |
| `deciles.test` | `cc3eddec` | table | table, 10 rows | decile separation on test; decile 1 holds the highest probabilities |
| `deciles.test.top2_capture` | `e3b6058b` | scalar | 0.4451038576 | share of test events in the top two deciles |
| `deciles.train.top2_capture` | `1693b145` | scalar | 0.4262086514 | share of train events in the top two deciles |
| `leakage.duplicates.train` | `4474c227` | scalar | 0 | share of train rows whose feature values are not unique within train |
| `leakage.name_screen.n_matched` | `407e62be` | scalar | 0 | feature names matching the target-adjacent lexicon |
| `leakage.overlap` | `4c9fcd09` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.features` | `0fec8048` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.ids` | `63d37fc5` | scalar | 0 | share of test rows whose ['client_id'] also identify a row of train |
| `leakage.target_corr.max_single_feature_auc` | `fd829fc4` | scalar | 0.6831414154 | the AUC of the strongest single feature |
| `leakage.timing.n_flagged` | `742bcd24` | scalar | 0 | features declared during_period or after_outcome |
| `metrics.test.auc` | `06c7c666` | scalar | 0.7763713511 | auc on test, recomputed by quaestor |
| `metrics.test.brier` | `2f64a7ce` | scalar | 0.1928760509 | brier on test, recomputed by quaestor |
| `metrics.test.event_rate` | `9209d200` | scalar | 0.2246666667 | event_rate on test, recomputed by quaestor |
| `metrics.test.gini` | `bc939097` | scalar | 0.5527427022 | gini on test, recomputed by quaestor |
| `metrics.test.ks` | `f4b92d62` | scalar | 0.4656278784 | ks on test, recomputed by quaestor |
| `metrics.test.logloss` | `6ac37fc1` | scalar | 0.5935045602 | logloss on test, recomputed by quaestor |
| `metrics.test.mean_predicted` | `aa68c658` | scalar | 0.4379028765 | mean_predicted on test, recomputed by quaestor |
| `metrics.test.n` | `64fcf14d` | scalar | 1500 | n on test, recomputed by quaestor |
| `metrics.test.sub.delinq_count_6m_high` | `a11954ab` | table | table, 10 rows | every metric on the delinq_count_6m above_median slice of test |
| `metrics.test.sub.delinq_count_6m_high.auc` | `8578b988` | scalar | 0.7350292398 | auc on the delinq_count_6m above_median slice of test |
| `metrics.test.sub.delinq_count_6m_high.auc_gap` | `39738a6e` | scalar | 0.04134211131 | how far AUC on the delinq_count_6m above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.delinq_count_6m_high.event_rate` | `ef17c303` | scalar | 0.3454545455 | event_rate on the delinq_count_6m above_median slice of test |
| `metrics.test.sub.delinq_count_6m_high.mean_predicted` | `6e2677ac` | scalar | 0.5804689313 | mean_predicted on the delinq_count_6m above_median slice of test |
| `metrics.test.sub.delinq_count_6m_high.mean_rel_gap` | `58e32501` | scalar | 0.6803048011 | mean predicted against observed on the delinq_count_6m above_median slice of test, relative |
| `metrics.test.sub.delinq_count_6m_high.share` | `22847310` | scalar | 0.3666666667 | the share of test the delinq_count_6m above_median slice holds |
| `metrics.test.sub.limit_bal_low` | `2ae9e510` | table | table, 10 rows | every metric on the limit_bal below_median slice of test |
| `metrics.test.sub.limit_bal_low.auc` | `b14bb20b` | scalar | 0.7838252922 | auc on the limit_bal below_median slice of test |
| `metrics.test.sub.limit_bal_low.auc_gap` | `69d61c38` | scalar | -0.007453941099 | how far AUC on the limit_bal below_median slice of test falls below AUC on all of test |
| `metrics.test.sub.limit_bal_low.event_rate` | `de78adb5` | scalar | 0.2486772487 | event_rate on the limit_bal below_median slice of test |
| `metrics.test.sub.limit_bal_low.mean_predicted` | `1cae8978` | scalar | 0.4708680099 | mean_predicted on the limit_bal below_median slice of test |
| `metrics.test.sub.limit_bal_low.mean_rel_gap` | `07e1da50` | scalar | 0.8934905081 | mean predicted against observed on the limit_bal below_median slice of test, relative |
| `metrics.test.sub.limit_bal_low.share` | `bac689cc` | scalar | 0.504 | the share of test the limit_bal below_median slice holds |
| `metrics.test.sub.utilisation_high` | `7fb0faad` | table | table, 10 rows | every metric on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.auc` | `015b00e8` | scalar | 0.5865242236 | auc on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.auc_gap` | `fcca7c35` | scalar | 0.1898471275 | how far AUC on the utilisation above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.utilisation_high.event_rate` | `8e66209c` | scalar | 0.2333333333 | event_rate on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.mean_predicted` | `f1d1d4d2` | scalar | 0.4918161846 | mean_predicted on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.mean_rel_gap` | `40cb08f4` | scalar | 1.107783648 | mean predicted against observed on the utilisation above_median slice of test, relative |
| `metrics.test.sub.utilisation_high.share` | `9404484e` | scalar | 0.5 | the share of test the utilisation above_median slice holds |
| `metrics.test.sub.utilisation_low` | `ad3af41c` | table | table, 10 rows | every metric on the utilisation below_median slice of test |
| `metrics.test.sub.utilisation_low.auc` | `d408b939` | scalar | 0.9085726883 | auc on the utilisation below_median slice of test |
| `metrics.test.sub.utilisation_low.auc_gap` | `bf57d590` | scalar | -0.1322013373 | how far AUC on the utilisation below_median slice of test falls below AUC on all of test |
| `metrics.test.sub.utilisation_low.event_rate` | `b0ad49be` | scalar | 0.216 | event_rate on the utilisation below_median slice of test |
| `metrics.test.sub.utilisation_low.mean_predicted` | `5d54c6cf` | scalar | 0.3839895683 | mean_predicted on the utilisation below_median slice of test |
| `metrics.test.sub.utilisation_low.mean_rel_gap` | `d873908a` | scalar | 0.777729483 | mean predicted against observed on the utilisation below_median slice of test, relative |
| `metrics.test.sub.utilisation_low.share` | `7860a748` | scalar | 0.5 | the share of test the utilisation below_median slice holds |
| `metrics.train.auc` | `0e7355aa` | scalar | 0.7765019192 | auc on train, recomputed by quaestor |
| `metrics.train.brier` | `f118c784` | scalar | 0.1968893522 | brier on train, recomputed by quaestor |
| `metrics.train.event_rate` | `133a5ff8` | scalar | 0.2245714286 | event_rate on train, recomputed by quaestor |
| `metrics.train.gini` | `1e398595` | scalar | 0.5530038384 | gini on train, recomputed by quaestor |
| `metrics.train.ks` | `97bd5dab` | scalar | 0.4800544158 | ks on train, recomputed by quaestor |
| `metrics.train.logloss` | `dcbefb71` | scalar | 0.6031246073 | logloss on train, recomputed by quaestor |
| `metrics.train.mean_predicted` | `bbe07926` | scalar | 0.4427489586 | mean_predicted on train, recomputed by quaestor |
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
| `psi.y_score` | `a8375d0f` | scalar | 0.005049433774 | PSI of the score between train and test |
| `rule.calibration_first_event_rate` | `42f1351e` | scalar | 0.05 | the event rate below which the report puts calibration before discrimination |
| `run.features` | `abbb748e` | json | json | the subject's features.json |
| `run.model_summary` | `3986de2e` | json | json | the subject's model_summary.json |
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |
| `sign_check.age.agrees` | `4116add1` | scalar | 1 | 1 when the fitted sign on age agrees with its univariate direction, 0 when it does not |
| `sign_check.bill_mean_6m.agrees` | `89279c3b` | scalar | 1 | 1 when the fitted sign on bill_mean_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.delinq_last.agrees` | `a8ba9372` | scalar | 1 | 1 when the fitted sign on delinq_last agrees with its univariate direction, 0 when it does not |
| `sign_check.limit_bal.agrees` | `0278aad1` | scalar | 0 | 1 when the fitted sign on limit_bal agrees with its univariate direction, 0 when it does not |
| `sign_check.limit_bal.coef_sign` | `6af6aef2` | scalar | 1 | the sign of the fitted coefficient on limit_bal |
| `sign_check.limit_bal.univariate_direction` | `56d284d6` | scalar | -1 | the sign of limit_bal's own single-feature AUC on train minus 0.5 |
| `sign_check.n_disagreements` | `f96ece96` | scalar | 1 | retained features whose fitted sign contradicts their univariate direction, of 10 checked |
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
| `thresholds.evaluation` | `f50831dc` | table | table, 5 rows | every threshold package.yaml declares, with its bound, the recomputed value and the outcome |
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
| LLM calls | 20 (plan 4, draft 8, extract 8) |
| re-asks | 0 |
| repair rounds | 1 |
| tokens in / out | 260,220 / 112,400 |
| notional cost (USD) | 5.4071 |
| wall-clock (s) | 1226.10 |
| subject run (s) | 1.50 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | credit_default-full_agent-20260920T012036Z-e2e51e00 |

## Appendix D — Not checked

| item | reason |
|---|---|
| `check_stability` (R1) | package declares no `regime.column` |
| `run_scenarios` (X1) | not applicable to `binary_classification` |
| out-of-time and vintage-holdout metrics (O1, second rule) | package declares neither split |
| developer claims (T1, claim channel) | The package declares 2 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
