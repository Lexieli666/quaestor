---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: full_agent
model: claude-opus-5[1m]
run_id: credit_default-full_agent-20260920T093731Z-e2e51e00
data_mode: synthetic
synthetic_n: 5000
grounding_precision_pre: 0.9951
grounding_precision_post: 1.0000
n_claims: 204
n_findings_by_severity: {high: 1, medium: 1, low: 1, info: 0}
generated: "2026-09-20T09:37:31Z"
illustrative: false
---

# Validation report — `credit_default` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `credit_default` v1.0 | `full_agent` | claude-opus-5[1m] | synthetic, n = 5000 | 0.9951 → 1.0000 | 1 / 1 / 1 / 0 |
<!-- quaestor:renderer:end -->

The subject of this report is the model package credit_default version 1.0, a binary classification model that predicts the probability that an obligor defaults, and this report is organised to follow the Federal Reserve's model risk management guidance on model validation [[reg:SR26-2:V]].

The subject was run by the validation harness under the wall-clock cap the package declares, 300 [[art:2ad8d1a5:runtime.max_seconds]] seconds, and every performance quantity cited here was recomputed by the harness from the subject's own outputs rather than taken from the developer's report.
The run covers two splits: the training split holds 1789 [[art:0f89a4f1:profile.train.n]] rows and the test split holds 1500 [[art:2193cf5f:profile.test.n]] rows.
The observed event rate is 0.2437 [[art:25e9afa5:metrics.train.event_rate]] on train and 0.2247 [[art:9209d200:metrics.test.event_rate]] on test, so the outcome is the less frequent of the two classes on both splits.

On the headline result, discrimination on test clears the declared floor: the recomputed AUC is 0.7525 [[art:2a5ea4af:metrics.test.auc]], above the declared minimum of 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]].
The recomputed Brier score on test is 0.1524 [[art:7da5c034:metrics.test.brier]], below the declared maximum of 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]].
The calibration slope on test is 1.008 [[art:b918ce48:calibration_slope.test]], inside the declared band running from 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] to 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]], and the corresponding slope on train is 1.004 [[art:4c796937:calibration_slope.train]].
Those are the declared thresholds the evidence selected for this section shows the subject meeting; the declared bounds not named in that list are treated in the findings section below.

This validation raised F-001, a T1 declared threshold finding at high severity, F-002, a S1 population drift finding at medium severity, and F-003, a E1 effective challenge finding at low severity.
Each of those is set out in full, with its evidence and its disposition, in section 6, and the scope table above this prose carries the breakdown by severity.

## 2. Conceptual soundness

Validation of conceptual soundness assesses and documents the model's design, construction and developmental evidence, including key modelling choices and, where more practical than theoretical review, interpretability measures and benchmarking against other models. [[reg:SR26-2:V.1.a]]

### Design and inputs

The champion is a coefficient-based classifier scored from a fitted weight on each retained feature plus an intercept of -1.251 [[art:b82670e1:run.model_summary#intercept]], estimated on 1789 [[art:b82670e1:run.model_summary#n_train]] training rows.
The subject's feature declaration carries 12 [[art:abbb748e:run.features#n]] features.
Of those, 2 [[art:abbb748e:run.features#at_origination]] are known at origination and 10 [[art:abbb748e:run.features#before_period_start]] are known before the performance period opens.
The declaration places 0 [[art:abbb748e:run.features#during_period]] features inside the performance period and 0 [[art:abbb748e:run.features#after_outcome]] after the outcome is known.
On the timing declaration alone, then, every input is observable at or before the moment the score would be used, and no declared input postdates the outcome it predicts.

The developer's own screen removed features on a variance-inflation criterion set at 10 [[art:b82670e1:run.model_summary#vif_threshold]].
It dropped bill_last at a variance inflation of 331 [[art:b82670e1:run.model_summary#removed.bill_last.vif]], utilisation_mean_6m at 59.82 [[art:b82670e1:run.model_summary#removed.utilisation_mean_6m.vif]] and bill_mean_6m at 15.57 [[art:b82670e1:run.model_summary#removed.bill_mean_6m.vif]], each above that criterion.
The removed features are balance- and utilisation-level measures that restate information already carried by the retained utilisation and bill-trend terms, so their removal is the expected response to that overlap rather than a discretionary choice, and the retained equation is easier to read for it.

### Coefficients and expected signs

The largest weight falls on delinq_last at 0.6395 [[art:b82670e1:run.model_summary#coefficients.delinq_last.value]], positive, which is the direction credit subject matter expects: a borrower delinquent most recently is the more likely to default.
The next largest is pay_ratio_mean_6m at -0.4569 [[art:b82670e1:run.model_summary#coefficients.pay_ratio_mean_6m.value]], negative, and a borrower who has been paying down more of the balance being scored as safer is also what the subject matter expects.
utilisation carries 0.1902 [[art:b82670e1:run.model_summary#coefficients.utilisation.value]], positive, consistent with higher line usage indicating strain.
delinq_count_6m carries 0.1046 [[art:b82670e1:run.model_summary#coefficients.delinq_count_6m.value]], positive, again the expected direction for a count of recent delinquencies.
limit_bal carries -0.07911 [[art:b82670e1:run.model_summary#coefficients.limit_bal.value]] and age carries -0.08596 [[art:b82670e1:run.model_summary#coefficients.age.value]], both modest and both in directions an underwriter would accept, larger granted limits and older borrowers scoring safer.
bill_trend_6m carries -0.07872 [[art:b82670e1:run.model_summary#coefficients.bill_trend_6m.value]], negative, which reads against a naive expectation that rising balances signal strain, though it matches the direction the feature shows on its own in training.
Two weights run against expectation: pay_ratio_last at 0.1877 [[art:b82670e1:run.model_summary#coefficients.pay_ratio_last.value]] scores a borrower who paid more of the last bill as riskier, and delinq_max_6m at -0.003169 [[art:b82670e1:run.model_summary#coefficients.delinq_max_6m.value]] scores a worse recent delinquency peak as safer.

### Fitted signs against univariate direction

The count of retained features whose fitted sign contradicts the direction of their own single-feature relationship with the outcome on train is 2 [[art:66ce738a:sign_check.n_disagreements]].
The fitted sign on pay_ratio_last is +1 [[art:f018263e:sign_check.pay_ratio_last.coef_sign]] while its univariate direction is -1 [[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]], giving an agreement flag of 0 [[art:79abee77:sign_check.pay_ratio_last.agrees]].
Refitting the champion's functional form without that feature changes test AUC by 0.003621 [[art:cc45633b:ablation.pay_ratio_last.delta_auc]], and because a negative change would mark a feature that was carrying discrimination, a positive one says discrimination did not fall when it was dropped.
The fitted sign on delinq_max_6m is -1 [[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]] against a univariate direction of +1 [[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]], with an agreement flag of 0 [[art:c946359c:sign_check.delinq_max_6m.agrees]], and refitting without it changes test AUC by 8.165e-05 [[art:1d41dd41:ablation.delinq_max_6m.delta_auc]].
Of the two sign reversals, the one on delinq_max_6m sits on a feature the model barely uses, its ablation change being the smaller of the two and close to zero, so the reversal is an artefact of a term doing almost no work.
The reversal on pay_ratio_last sits on a feature the model also does not depend on for discrimination, since dropping it did not lower test AUC either, but its weight is the larger of the two and the sign is the one an underwriter would query, so the term is better read as absorbing correlation with the other payment-ratio measure than as a statement about payment behaviour.
Where fitted sign and univariate direction do agree, the agreement is on the terms the model actually leans on: the flag on delinq_last is 1 [[art:a8ba9372:sign_check.delinq_last.agrees]] and the flag on utilisation is 1 [[art:d0c9a130:sign_check.utilisation.agrees]].
Neither the sign comparison nor the ablation evidence is the subject of a rule here, and nothing in this paragraph is offered as a finding; it is evidence bearing on the design judgement.

### What the model leans on

Each ablation change is measured from a refit of the champion's functional form on every retained feature, whose test AUC is 0.7525 [[art:6b970cd1:ablation.baseline_auc]], the same level as the champion's recomputed test AUC of 0.7525 [[art:2a5ea4af:metrics.test.auc]].
Refitting without delinq_last changes test AUC by -0.09255 [[art:562511ba:ablation.delinq_last.delta_auc]] and without utilisation by -0.02697 [[art:2a417d0d:ablation.utilisation.delta_auc]], each negative and so each carrying discrimination, with the delinquency term much the larger drop.
Refitting without delinq_count_6m changes test AUC by -0.0001378 [[art:478e5417:ablation.delinq_count_6m.delta_auc]], negative but slight.
The remaining changes are positive: 0.007129 [[art:53d51307:ablation.pay_ratio_mean_6m.delta_auc]] for pay_ratio_mean_6m, 0.007121 [[art:b56721dc:ablation.bill_trend_6m.delta_auc]] for bill_trend_6m, 0.004218 [[art:6f97302c:ablation.limit_bal.delta_auc]] for limit_bal and 0.001077 [[art:223939e9:ablation.age.delta_auc]] for age.
Notably the feature with the second largest weight, pay_ratio_mean_6m, is one whose removal did not lower test AUC, so coefficient magnitude here does not track marginal discrimination and should not be read as an importance ranking.
The design is therefore concentrated: the recent delinquency indicator supplies most of the separation, utilisation supplies a further share, and the rest of the equation contributes little discrimination on test even where its signs are sensible.

### Effective challenge

A hist_gradient_boosting challenger was fitted as the benchmark against the champion, a comparison of alternative methodology of the kind sound development testing calls for. [[reg:SR26-2:IV.1]]
The challenger's test AUC is 0.8221 [[art:9a3da49b:challenger.auc]] against the champion's 0.7525 [[art:2a5ea4af:metrics.test.auc]].
Expressed as a difference in AUC, the challenger's lead is 0.06961 [[art:ce2a1ab8:challenger.delta_auc]], read against an effective-challenge threshold of 0.03 [[art:e042774c:threshold.E1.delta_auc]], and the lead is above that threshold.
Comparing the two on probability accuracy by level rather than by difference or ratio, the challenger's Brier score is 0.125 [[art:01fa79a9:challenger.brier]] and the champion's is 0.1524 [[art:7da5c034:metrics.test.brier]], the challenger's being the lower and so the better calibrated-and-sharper of the two on test.
The challenger differs from the champion in functional form rather than in its inputs, so the gap is evidence about the champion's functional form: a flexible learner extracts separation from the same retained features that the coefficient-based equation does not reach.
That gap is raised as finding E1, effective challenge, at a suggested severity of low, and it is reported in the findings section; this section points the reader there rather than restating its disposition.
Read together with the concentration seen in the ablation evidence, the challenger's lead is consistent with interaction or non-linear structure among the retained features that a linear-in-the-features form cannot represent, which is the aspect of the design most in need of further developmental evidence before the champion's form is relied on.

## 3. Data integrity and drift

Data integrity is assessed here as part of the critical assessment of data quality, relevance, and inputs that belongs to sound model testing [[reg:SR26-2:IV.1]].
The training split holds 1789 [[art:0f89a4f1:profile.train.n]] rows and the test split holds 1500 [[art:2193cf5f:profile.test.n]] rows.

### Missingness

The largest missing fraction in the training split is 0 [[art:050a3099:profile.train.missing.max]].
The largest missing fraction in the test split is 0 [[art:f813848d:profile.test.missing.max]].
The declared bound is stated as a gap, so the comparison made here is the difference between the two splits and not their ratio, and with the largest fraction in each split standing at the same value that difference lies below the bound of 0.1 [[art:9cce25ea:threshold.D1.missing_gap]].

### Population and characteristic stability

The largest train-to-test population stability index, the score included, is 1.196 [[art:5a6a40fb:psi.max]], which stands above the declared stability bound of 0.25 [[art:278b9016:threshold.S1.psi]] and above the bound carried in the package manifest, 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
That maximum is carried by `limit_bal`, whose index between train and test is 1.196 [[art:c312ae78:psi.limit_bal]], and this breach is raised as finding S1 at medium severity.
The breach is confined to that one variable; every other index listed for this section sits below the declared bound.
The score itself shifts by 0.1866 [[art:1ecde7e0:psi.y_score]] and `bill_trend_6m` by 0.1334 [[art:41ee0c35:psi.bill_trend_6m]], both below 0.25 [[art:278b9016:threshold.S1.psi]] but further from it than the remaining variables.
The rest are smaller again: `utilisation` at 0.01936 [[art:e45cb5af:psi.utilisation]], `pay_ratio_mean_6m` at 0.008826 [[art:1e74f864:psi.pay_ratio_mean_6m]], `delinq_max_6m` at 0.007293 [[art:85162d6e:psi.delinq_max_6m]], `age` at 0.005867 [[art:c35c14b6:psi.age]], `pay_ratio_last` at 0.002965 [[art:35f2b74b:psi.pay_ratio_last]], `delinq_count_6m` at 0.002943 [[art:f5c55e59:psi.delinq_count_6m]] and `delinq_last` at 0.0008258 [[art:da6a07f2:psi.delinq_last]].

Characteristic stability, the per-feature contribution to the shift in the linear predictor, is read here against the same declared stability bound of 0.25 [[art:278b9016:threshold.S1.psi]], and the largest such contribution, 0.06466 [[art:b2e113ad:csi.max]], sits below it.
That largest contribution belongs to `limit_bal` at 0.06466 [[art:44fa93ba:csi.limit_bal]], the same variable that carries the population breach, so the shift shows far more strongly in the marginal distribution of that variable than in its pull on the linear predictor.
The remaining contributions are smaller: `delinq_last` at 0.01505 [[art:4e9b1ec3:csi.delinq_last]], `pay_ratio_mean_6m` at 0.00576 [[art:d7a50342:csi.pay_ratio_mean_6m]], `utilisation` at 0.005503 [[art:b506bc4b:csi.utilisation]], `bill_trend_6m` at 0.002501 [[art:6d4f0d7b:csi.bill_trend_6m]], `delinq_count_6m` at 0.002246 [[art:7ee6f613:csi.delinq_count_6m]], `pay_ratio_last` at 0.001222 [[art:547b3f3e:csi.pay_ratio_last]], `age` at 0.0009235 [[art:c3bb7175:csi.age]] and `delinq_max_6m` at 0.0001002 [[art:f775c7df:csi.delinq_max_6m]].

### Leakage screens

The declared-timing screen flags features whose declared timing is during the performance period or after the outcome, and it flags 0 [[art:742bcd24:leakage.timing.n_flagged]] of the model's inputs.
The strongest single feature reaches an AUC of 0.6626 [[art:4c34a594:leakage.target_corr.max_single_feature_auc]] on its own, below the bound of 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]] that one feature may reach.

The contamination screen has two arms, each read against its own bound.
The identifier arm reports a share of 0 [[art:63d37fc5:leakage.overlap.ids]] of test rows whose client identifier also identifies a row of train, below the declared bound of 0.005 [[art:9f336eaf:threshold.L2.overlap]].
The feature-vector arm is read against the bound that rule actually applied, the larger of the declared overlap bound and a multiple of the in-train duplicate share, on the reasoning that two different subjects writing the same discrete row is coincidence rather than contamination.
The share of train rows whose feature values are not unique within train is 0 [[art:4474c227:leakage.duplicates.train]], and the bound the feature-overlap rule applied is 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]], which coincides with the declared bound.
Against that applied bound of 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]], the share of test rows whose feature values also appear in train is 0 [[art:0fec8048:leakage.overlap.features]], and the row-level share reported for the screen as a whole is likewise 0 [[art:4c9fcd09:leakage.overlap]].
The name screen matches feature names against a target-adjacent lexicon and matches 0 [[art:407e62be:leakage.name_screen.n_matched]] of them.

### Assessment

Missingness and every leakage arm sit within the bounds each was read against, and the identifier and feature-vector arms agree in showing no shared rows between the splits.
The open exposure in this section is distributional rather than structural: one input has moved between train and test by an amount above the declared stability bound, while its contribution to the linear predictor remains small, and that movement is carried forward as finding S1.
Because the score's own shift sits below the declared bound while the input's does not, the drift is best read as a change in the input population that the scoring function has so far absorbed, and it warrants monitoring of that input in use rather than an inference about output performance, which belongs to outcomes analysis [[reg:SR26-2:V.1.b]].

## 4. Outcomes analysis

Outcomes analysis here compares the model's recomputed outputs against realised outcomes on the evaluation data, in the sense of the current guidance on outcomes analysis [[reg:SR26-2:V.1.b]].
This section leads with discrimination and turns to calibration after it, because the observed event rate on the evaluation split is 0.2247 [[art:9209d200:metrics.test.event_rate]], at or above the rate of 0.05 [[art:42f1351e:rule.calibration_first_event_rate]] below which this report would take calibration first.

### Metrics by split

| Metric | Train | Test |
| --- | --- | --- |
| Rows | 1789 [[art:eae7a256:metrics.train.n]] | 1500 [[art:64fcf14d:metrics.test.n]] |
| Event rate | 0.2437 [[art:25e9afa5:metrics.train.event_rate]] | 0.2247 [[art:9209d200:metrics.test.event_rate]] |
| AUC | 0.7599 [[art:3d5f30fa:metrics.train.auc]] | 0.7525 [[art:2a5ea4af:metrics.test.auc]] |
| Gini | 0.5198 [[art:3198b731:metrics.train.gini]] | 0.5050 [[art:f00e967c:metrics.test.gini]] |
| KS | 0.4559 [[art:c2dc79a4:metrics.train.ks]] | 0.4306 [[art:c3789b0d:metrics.test.ks]] |
| Brier | 0.1636 [[art:46973259:metrics.train.brier]] | 0.1524 [[art:7da5c034:metrics.test.brier]] |
| Log loss | 0.4967 [[art:73e399ed:metrics.train.logloss]] | 0.4717 [[art:46b23175:metrics.test.logloss]] |
| Mean predicted | 0.2437 [[art:7bfcb165:metrics.train.mean_predicted]] | 0.2122 [[art:f06b1724:metrics.test.mean_predicted]] |

Rank-ordering carries over from the fitting data to the evaluation data: on every discrimination measure the test value sits below its train counterpart, and on the loss measures the test value sits below the train value as well.
Separation at the top of the score distribution is visible in the decile table below.

<!-- quaestor:renderer:begin table deciles.test -->
Decile separation on test; decile 1 holds the highest probabilities [[art:97ae0549:deciles.test]]:

| decile | count | events | event_rate | lift |
|---|---|---|---|---|
| 1 | 150 | 80 | 0.5333 | 2.374 |
| 2 | 150 | 68 | 0.4533 | 2.018 |
| 3 | 150 | 58 | 0.3867 | 1.721 |
| 4 | 150 | 37 | 0.2467 | 1.098 |
| 5 | 150 | 24 | 0.16 | 0.7122 |
| 6 | 150 | 18 | 0.12 | 0.5341 |
| 7 | 150 | 18 | 0.12 | 0.5341 |
| 8 | 150 | 8 | 0.05333 | 0.2374 |
| 9 | 150 | 17 | 0.1133 | 0.5045 |
| 10 | 150 | 9 | 0.06 | 0.2671 |
<!-- quaestor:renderer:end -->

The share of test events falling in the top two deciles is 0.4392 [[art:293e7437:deciles.test.top2_capture]], above the corresponding train share of 0.3899 [[art:a16b6639:deciles.train.top2_capture]], comparing the two as absolute shares of events rather than as a ratio.

### Train-to-test gap

The train-to-test movement in discrimination is the distance between the train AUC of 0.7599 [[art:3d5f30fa:metrics.train.auc]] and the test AUC of 0.7525 [[art:2a5ea4af:metrics.test.auc]], read against a bound of 0.08 [[art:630f28f4:threshold.O1.auc_gap]].
The test value lies below the train value, and the two recomputed values are near neighbours, so the bound is not approached.

### Calibration

Regressing the outcome on the logit of the predicted probability gives a slope on test of 1.008 [[art:b918ce48:calibration_slope.test]], inside the band whose bottom is 0.8 [[art:749634ae:threshold.C1.calibration_slope.min]] and whose top is 1.2 [[art:b6672579:threshold.C1.calibration_slope.max]].
The same regression on train gives a slope of 1.004 [[art:4c796937:calibration_slope.train]], also inside that band.
The intercept of that regression on test is 0.09438 [[art:9a0ff160:calibration_intercept.test]], above the train intercept of 0.004013 [[art:16a633d0:calibration_intercept.train]].
Mean predicted probability on test is 0.2122 [[art:f06b1724:metrics.test.mean_predicted]] against an observed rate of 0.2247 [[art:9209d200:metrics.test.event_rate]], so the model predicts below what was observed on that split.
Expressed as a relative gap that difference is 0.05556 [[art:844dbd0c:calibration.mean_rel_gap.test]], below the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
On train the same relative gap is 9.752e-05 [[art:d0dfeed7:calibration.mean_rel_gap.train]], far below the test figure when the two are compared as relative gaps.
Calibration decile by decile of predicted probability on test is set out below.

<!-- quaestor:renderer:begin table calibration.test -->
Calibration by decile of predicted probability on test [[art:e84a960d:calibration.test]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.06654 | 0.06 | 150 |
| 2 | 0.09497 | 0.1133 | 150 |
| 3 | 0.1147 | 0.05333 | 150 |
| 4 | 0.1334 | 0.12 | 150 |
| 5 | 0.1552 | 0.12 | 150 |
| 6 | 0.1785 | 0.16 | 150 |
| 7 | 0.2066 | 0.2467 | 150 |
| 8 | 0.2506 | 0.3867 | 150 |
| 9 | 0.3554 | 0.4533 | 150 |
| 10 | 0.566 | 0.5333 | 150 |
<!-- quaestor:renderer:end -->

### Declared thresholds

<!-- quaestor:renderer:begin table thresholds.evaluation -->
Every threshold package.yaml declares, with its bound, the recomputed value and the outcome [[art:7633a313:thresholds.evaluation]]:

| metric | split | bound | value | result |
|---|---|---|---|---|
| auc | test | minimum 0.7 | 0.7525 | pass |
| brier | test | maximum 0.2 | 0.1524 | pass |
| calibration_slope | test | minimum 0.8 | 1.008 | pass |
| calibration_slope | test | maximum 1.2 | 1.008 | pass |
| psi |  | maximum 0.25 | 1.196 | fail |
<!-- quaestor:renderer:end -->

The table reads each bound package.yaml declares against the value recomputed for this run, and the discrimination, loss and calibration-slope bounds are met on the evaluation split.
The exception is stability: the largest train-to-test population stability index is 1.196 [[art:5a6a40fb:psi.max]], above the declared maximum of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]], and that breach is raised as a finding.

### Follow-up analyses

The planning loop ran four sub-population analyses on the evaluation split, each of them a compute-metrics step over a half of test defined by a median split.

The first asked for every metric on the slice `limit_bal > median(limit_bal)`, because the stability index of 1.196 [[art:c312ae78:psi.limit_bal]] on that feature says the population shifted, and the question was whether discrimination and calibration hold in the region it shifted into.

<!-- quaestor:renderer:begin table metrics.test.sub.limit_bal_high -->
Every metric on the limit_bal above_median slice of test [[art:aaa6b180:metrics.test.sub.limit_bal_high]]:

| metric | value |
|---|---|
| n | 744 |
| event_rate | 0.2003 |
| auc | 0.7411 |
| gini | 0.4822 |
| ks | 0.4242 |
| brier | 0.1422 |
| logloss | 0.4471 |
| mean_predicted | 0.1785 |
| mean_rel_gap | 0.1089 |
| share | 0.496 |
<!-- quaestor:renderer:end -->

AUC on this slice falls 0.01144 [[art:b05474b5:metrics.test.sub.limit_bal_high.auc_gap]] below the AUC of the split as a whole, within the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] beyond which the result would be an open item.
The slice holds 0.4960 [[art:ac383ccb:metrics.test.sub.limit_bal_high.share]] of the split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] and below the ceiling of 0.95 [[art:a928a05c:threshold.O1.slice_max_share]], so it is large enough to read and not a restatement of the whole split.
Mean predicted here is 0.1785 [[art:1538f9f0:metrics.test.sub.limit_bal_high.mean_predicted]] against an observed rate of 0.2003 [[art:5e9aab40:metrics.test.sub.limit_bal_high.event_rate]], a relative gap of 0.1089 [[art:4a80a9ee:metrics.test.sub.limit_bal_high.mean_rel_gap]], so what weakness there is sits in the level of the probabilities rather than in their ordering.

The second asked for the same metrics on the complementary slice `limit_bal <= median(limit_bal)`, since the drift on that feature can only be read as one-sided or two-sided with both halves in hand.

<!-- quaestor:renderer:begin table metrics.test.sub.limit_bal_low -->
Every metric on the limit_bal below_median slice of test [[art:fd28f3a8:metrics.test.sub.limit_bal_low]]:

| metric | value |
|---|---|
| n | 756 |
| event_rate | 0.2487 |
| auc | 0.7597 |
| gini | 0.5193 |
| ks | 0.4328 |
| brier | 0.1624 |
| logloss | 0.496 |
| mean_predicted | 0.2454 |
| mean_rel_gap | 0.01325 |
| share | 0.504 |
<!-- quaestor:renderer:end -->

AUC on this slice falls -0.007142 [[art:da638efa:metrics.test.sub.limit_bal_low.auc_gap]] below the AUC of the split as a whole, that is, it sits above the split's own, and it is within the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].
The slice holds 0.5040 [[art:bac689cc:metrics.test.sub.limit_bal_low.share]] of the split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].
Mean predicted is 0.2454 [[art:f220a724:metrics.test.sub.limit_bal_low.mean_predicted]] against an observed rate of 0.2487 [[art:de78adb5:metrics.test.sub.limit_bal_low.event_rate]], a relative gap of 0.01325 [[art:66be0220:metrics.test.sub.limit_bal_low.mean_rel_gap]], so neither the level of the probabilities nor their ordering is weak on this half.
Comparing the two halves of that feature as absolute shortfalls in AUC, the high half carries the larger of the two; comparing them as relative gaps of mean predicted against observed, the high half is again the larger.

The third asked for every metric on the slice `delinq_count_6m > median(delinq_count_6m)`, to see whether weakness on test concentrates in the delinquent sub-population rather than following only the drift already probed.

<!-- quaestor:renderer:begin table metrics.test.sub.delinq_count_6m_high -->
Every metric on the delinq_count_6m above_median slice of test [[art:ebc1557e:metrics.test.sub.delinq_count_6m_high]]:

| metric | value |
|---|---|
| n | 550 |
| event_rate | 0.3455 |
| auc | 0.7315 |
| gini | 0.4629 |
| ks | 0.4121 |
| brier | 0.2025 |
| logloss | 0.5863 |
| mean_predicted | 0.301 |
| mean_rel_gap | 0.1287 |
| share | 0.3667 |
<!-- quaestor:renderer:end -->

AUC on this slice falls 0.02106 [[art:c9b40bd7:metrics.test.sub.delinq_count_6m_high.auc_gap]] below the AUC of the split as a whole, within the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].
The slice holds 0.3667 [[art:22847310:metrics.test.sub.delinq_count_6m_high.share]] of the split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].
Mean predicted is 0.3010 [[art:59654f0e:metrics.test.sub.delinq_count_6m_high.mean_predicted]] against an observed rate of 0.3455 [[art:ef17c303:metrics.test.sub.delinq_count_6m_high.event_rate]], a relative gap of 0.1287 [[art:24f57004:metrics.test.sub.delinq_count_6m_high.mean_rel_gap]], so the probabilities sit below the outcomes in level while their ordering holds.

The fourth asked for the same metrics on the complementary slice `delinq_count_6m <= median(delinq_count_6m)`, because the high-delinquency half cannot be read without the half it is being compared against.

<!-- quaestor:renderer:begin table metrics.test.sub.delinq_count_6m_low -->
Every metric on the delinq_count_6m below_median slice of test [[art:ae54b16c:metrics.test.sub.delinq_count_6m_low]]:

| metric | value |
|---|---|
| n | 950 |
| event_rate | 0.1547 |
| auc | 0.6864 |
| gini | 0.3728 |
| ks | 0.2958 |
| brier | 0.1233 |
| logloss | 0.4054 |
| mean_predicted | 0.1608 |
| mean_rel_gap | 0.039 |
| share | 0.6333 |
<!-- quaestor:renderer:end -->

AUC on this slice falls 0.06612 [[art:2df7bb74:metrics.test.sub.delinq_count_6m_low.auc_gap]] below the AUC of the split as a whole, still within the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] but the largest of the four shortfalls when they are compared as absolute differences in AUC.
The slice holds 0.6333 [[art:3257b2f3:metrics.test.sub.delinq_count_6m_low.share]] of the split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].
Mean predicted is 0.1608 [[art:4e8141df:metrics.test.sub.delinq_count_6m_low.mean_predicted]] against an observed rate of 0.1547 [[art:9690f94d:metrics.test.sub.delinq_count_6m_low.event_rate]] — the probabilities sit above the outcomes in level here, with a relative gap of 0.0390 [[art:d450f3dd:metrics.test.sub.delinq_count_6m_low.mean_rel_gap]] that is the smaller of the two halves of that feature — so on this half the weakness is in the ordering rather than in the level.

## 5. Sensitivity and scenario analysis

Sensitivity analysis is understood here as the check that small changes in inputs and parameter values move outputs within an expected range, together with testing over a wide range of conditions including extreme values, so that the boundaries of stable model behaviour can be established [[reg:SR11-7:V.1.a]].
The diagnostics reported below are presented as developmental evidence subject to critical analysis, not as a verdict [[reg:SR26-2:V.1.a]].

### Multicollinearity among the retained features

The largest variance inflation factor across the retained features is 7.662 [[art:3a027a9e:vif.max]], which is below the declared ceiling of 10 [[art:aeb4f33c:threshold.M1.vif]].
That maximum is attained by the last-period payment ratio at 7.662 [[art:906f9c92:vif.pay_ratio_last]], with the trailing mean payment ratio close behind at 7.649 [[art:d5c149e7:vif.pay_ratio_mean_6m]].
The payment-ratio features are therefore the most strongly co-determined pair in the design, and both sit further from the ceiling than any other retained feature but well above the rest of the distribution.
The delinquency-count feature over the trailing window follows at 2.482 [[art:ca8684a5:vif.delinq_count_6m]] and the delinquency-maximum feature over the same window at 2.36 [[art:21212f86:vif.delinq_max_6m]], both far below the ceiling.
The most recent delinquency indicator is lower still at 1.366 [[art:610d9380:vif.delinq_last]].
The remaining retained features sit close to the no-inflation floor: the bill trend at 1.01 [[art:e9e68e9c:vif.bill_trend_6m]], the credit limit at 1.005 [[art:f6c05005:vif.limit_bal]], utilisation at 1.003 [[art:f810d89d:vif.utilisation]], and age at 1.002 [[art:4c6350d4:vif.age]].
Belsley's condition number of the column-standardised design is 5.647 [[art:81de583f:condition_number]], below the declared ceiling of 30 [[art:7e52fd7a:threshold.M1.condition_number]].
The design-level measure and the worst single-feature measure therefore point the same way, each remaining on the permissible side of its declared ceiling; the comparison made here is of each statistic against its own ceiling, not of one statistic against the other.
The practical reading is that coefficient variances are not inflated to the point where the declared thresholds would treat the design as ill-conditioned, while attribution of effect between the payment-ratio features should still be read with care given that they carry the largest shared variance in the design.

### Stability across declared regimes

Stability across declared regimes is a partition-dependent check that bears on this subject only where the model package declares a regime column, and the applicability determination for this model is recorded in Appendix D.
Nothing written in this section should be read as a regime-partitioned result, and the multicollinearity evidence above is computed on the training design as a whole rather than within any regime.

### Rate-shock scenarios

The rate-shock battery — the value change at the extreme shocks, whether the shock curve is monotone, and the sign of its convexity against the direction the package declares — is a hazard-model diagnostic.
The subject of this review is not a hazard model, so no shock grid was run against it, no shock curve exists to be inspected for monotonicity, and no convexity direction was compared with a declared one.
These checks are listed in Appendix D among the diagnostics that do not apply to a model of this type, and they should not be read as procedures that were performed and passed.

### Reading

On the evidence carried in this section, neither the worst-feature collinearity measure nor the design-level conditioning measure reaches its declared ceiling, and the sensitivity evidence therefore gives no indication of an unstable design at the thresholds the package declares.
That conclusion is scoped to the collinearity diagnostics reported above and to the model type's applicable checks; it does not extend to behaviour under the scenario families that Appendix D places outside this model's scope.

## 6. Findings and recommendations

Findings are ordered by severity, and each one is stated with the quantity quaestor recomputed, the declared bound it was read against, and the citation of every number it rests on, in keeping with validation's role in identifying model limitations and errors and clarifying whether corrective actions may be warranted [[reg:SR26-2:V]].

### F-001 · T1 declared threshold · severity **high**

**The package's own declared ceiling on population stability is breached by the drift quaestor recomputed.**

The largest recomputed train-to-test population stability index, with the score included, is 1.196 [[art:5a6a40fb:psi.max]].

That value sits above the ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]] declared in package.yaml, and the comparison here is the level of the index against the declared bound rather than any ratio between them.

The validator concludes that the model package does not hold to a limit it sets for itself, which is the most material of the defects recorded in this section because the bound is the developer's own statement of acceptable drift.

The developer should either re-establish a training population whose stability against the evaluation population falls under the declared ceiling, or revise the declared ceiling with a documented rationale and re-run the comparison so that the package and the recomputed evidence agree.

### F-002 · S1 population drift · severity **medium**

**The train-to-test distribution of the credit-limit feature has shifted far enough to put the evaluation population outside the one the model was fitted on.**

The population stability index between train and test on `limit_bal` is 1.196 [[art:c312ae78:psi.limit_bal]].

It is read against the stability threshold of 0.25 [[art:278b9016:threshold.S1.psi]], and again the comparison is the level of the index against that threshold, not a ratio.

The breach is carried by the credit-limit feature rather than being spread evenly across the compared features, which points at a shift in that one input's distribution rather than a wholesale change of population.

The validator concludes that performance measured on the test split cannot be read as performance on the training population, and any monitoring built on this split inherits that gap.

The developer should document why the credit-limit distribution differs between the two splits, state whether the split was drawn by time or by some other key, and show that the intended use population resembles one of the two rather than neither.

### F-003 · E1 effective challenge · severity **low**

**A routine challenger outperforms the champion on the test split by a margin larger than the one the package treats as evidence of inadequate challenge.**

A hist_gradient_boosting challenger reaches an AUC on test of 0.8221 [[art:9a3da49b:challenger.auc]], while the champion's recomputed AUC on the same split is 0.7525 [[art:2a5ea4af:metrics.test.auc]].

The difference between the two, which is the comparison recorded here rather than their ratio, is 0.06961 [[art:ce2a1ab8:challenger.delta_auc]], and it is above the effective-challenge threshold of 0.03 [[art:e042774c:threshold.E1.delta_auc]].

The validator concludes that the champion's discriminatory power on this split is the smaller of the two and that the search over alternatives behind the champion selection has not been shown to be adequate; severity is low because the challenger was fitted for comparison and not proposed for use.

The developer should document the model selection that produced the champion, state what was traded away against the challenger's stronger test performance, such as interpretability or the sign constraints a scorecard form allows, and record that reasoning where it can be tracked alongside this report [[reg:SR26-2:VI.3]].

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1), `compute_metrics` (C1, O1), `check_leakage` (L1, L2), `check_collinearity` (M1).

### Open items

Model developer: what does the model discriminate on within the segment where the fitted coefficient on `delinq_max_6m` carries sign -1 [[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]], read against that feature's own univariate direction of 1 [[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]], with the agreement flag between the two standing at 0 [[art:c946359c:sign_check.delinq_max_6m.agrees]], given that conditioning on a delinquency count also conditions on everything correlated with it?

Model developer: what does the model discriminate on within the segment where the fitted coefficient on `pay_ratio_last` carries sign 1 [[art:f018263e:sign_check.pay_ratio_last.coef_sign]], read against that feature's own univariate direction of -1 [[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]], with the agreement flag between the two standing at 0 [[art:79abee77:sign_check.pay_ratio_last.agrees]], and which correlated inputs carry the payment behaviour that the univariate direction reflects?

## 7. Ongoing monitoring recommendations

Ongoing monitoring is an evaluation of the extent to which the model continues to perform as expected given potential changes in products, exposures, activities, clients, data relevance, or market conditions, and its frequency and scope depend on the nature of the model and its materiality [[reg:SR26-2:V.2]].
The plan below re-uses the bounds this package already declares, so that a production reading is judged against the same thresholds the validation checks used rather than against a fresh set invented for monitoring.

### Quantities, cadence, and bounds

Track rank-ordering performance on each production vintage once its performance window closes, against the declared floor of 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]], taking the evaluation-split reading of 0.7525 [[art:2a5ea4af:metrics.test.auc]] as the reference point the model entered production with.
Track the mean squared probability error on the same vintages against the declared ceiling of 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]], with the evaluation-split reading of 0.1524 [[art:7da5c034:metrics.test.brier]] as the entry reference.
Track the regression slope of the outcome on the model's logit against the declared lower bound of 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] and the declared upper bound of 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]], with the evaluation-split reading of 1.008 [[art:b918ce48:calibration_slope.test]] as the entry reference; drift of this slope toward either bound is the earliest signal that the score's spread no longer matches realized risk.
Track the train-to-production population stability of each input and of the score itself against the declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]]; the largest train-to-test value carried into this report, 1.196 [[art:5a6a40fb:psi.max]], already sits above that ceiling, so the monitoring report should present the shifted quantity by name each cycle and state whether the shift is widening, holding, or receding rather than reporting only whether the ceiling was crossed.
Run the stability comparison at a shorter cadence than the outcome-based metrics, because input distributions are observable as soon as a vintage is scored while discrimination and calibration cannot be read until outcomes mature.
Run the outcome-based metrics on every vintage whose performance window has closed, and repeat the full set at each periodic revalidation of the package.
Where a shift is reported above the stability ceiling, compare it across sub-populations and state explicitly whether the comparison being made is the difference in stability between populations or the ratio, since populations whose absolute shifts look alike can differ sharply on the ratio.

### Ordering of the monitoring report

Because the observed event rate on the evaluation split was at or above 0.05 [[art:42f1351e:rule.calibration_first_event_rate]], section 4 of this report presented discrimination before calibration.
If a future monitored cohort has an observed event rate below 0.05 [[art:42f1351e:rule.calibration_first_event_rate]], that cohort's monitoring report should lead with calibration instead, since rank-ordering statistics become unstable as events thin out.

### Escalation

Outcomes analysis performed as part of ongoing monitoring may identify material errors or persistent deviations outside established performance thresholds, in which case model adjustment, recalibration, or redevelopment may be warranted [[reg:SR26-2:V.1.b]].
A reading outside any declared bound should therefore be treated as an escalation trigger with a named owner and a response deadline, and a reading that stays outside its bound across consecutive cycles should be escalated further than one that recovers.

### What monitoring must watch that this validation could not

This validation observed the model on fixed development and evaluation splits, so it could not observe performance on production vintages drawn after the development window, nor realized outcomes accumulated over a full production performance window; back-testing on those vintages is monitoring's job, not this report's.
It likewise could not observe behavior under market or portfolio conditions absent from the development sample, so monitoring should record the range of input values and conditions each vintage occupies and flag cycles that approach or exceed the range the model was fit over.
Process verification — that inputs remain accurate, complete, and consistent with the model's design, and that the deployed code matches the reviewed package under change control — belongs to monitoring, together with analysis of overrides, whose rate and performance indicate whether the model is being used as intended [[reg:SR11-7:V.1.b]].

### Benchmarking

Section 2 of this report compares the champion with a challenger, so benchmarking against an alternative model was part of this validation.
What monitoring adds is the comparison the development data cannot give: the challenger refitted on production vintages and scored against the champion on the same realized outcomes, so that any advantage reflects the population the model now sees rather than the population it was fit on.
Where the refitted challenger outperforms the champion on the same vintage, the discrepancy should trigger investigation into its source and degree before any conclusion about replacement, since a difference may stem from the differing data or method rather than from error in the champion [[reg:SR11-7:V.1.b]].

## Appendix A — Claims

Grounding precision 0.9951 before repair (203 of 204 claims verified; 1 dangling) and 1.0000 after 0 claim(s) rewritten and 1 number(s) removed from the prose. Per section (post-repair): summary 13/13; conceptual_soundness 46/46; data_integrity 41/41; outcomes 66/66; sensitivity 13/13; findings 14/14; monitoring 11/11.

Developer claims: The package declares 2 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). See Appendix D.

Excluded numeric tokens (not claims): section_number (section 6, section 4, Section 2); citation_hash (2ad8d1a5, 0f89a4f1, 2193cf5f, 25e9afa5); regulatory_section_id (SR26-2:V, SR26-2:V.1.a, SR26-2:IV.1, SR26-2:V.1.b); finding_id (F-001, F-002, F-003); package_version (1.0); extractor_returned_excluded_token (1.0, 001,, 002,, 003,).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The subject was run by the validation harness under the wall… | 300 | ratio | max_seconds |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 2 | summary | The run covers two splits: the training split holds 1789 row… | 1789 | count | n | train | eq | `[[art:0f89a4f1:profile.train.n]]` | verified | 1789 |
| 3 | summary | The run covers two splits: the training split holds 1789 row… | 1500 | count | n | test | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 4 | summary | The observed event rate is 0.2437 on train and 0.2247 on tes… | 0.2437 | ratio | event_rate | train | eq | `[[art:25e9afa5:metrics.train.event_rate]]` | verified | 0.2437115707 |
| 5 | summary | The observed event rate is 0.2437 on train and 0.2247 on tes… | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 6 | summary | On the headline result, discrimination on test clears the de… | 0.7525 | ratio | auc | test | eq | `[[art:2a5ea4af:metrics.test.auc]]` | verified | 0.7525227655 |
| 7 | summary | On the headline result, discrimination on test clears the de… | 0.7 | ratio | auc | test | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 8 | summary | The recomputed Brier score on test is 0.1524 , below the dec… | 0.1524 | ratio | brier | test | eq | `[[art:7da5c034:metrics.test.brier]]` | verified | 0.1523576419 |
| 9 | summary | The recomputed Brier score on test is 0.1524 , below the dec… | 0.2 | ratio | brier | test | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 10 | summary | The calibration slope on test is 1.008 , inside the declared… | 1.008 | ratio | calibration_slope | test | eq | `[[art:b918ce48:calibration_slope.test]]` | verified | 1.008335252 |
| 11 | summary | The calibration slope on test is 1.008 , inside the declared… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 12 | summary | The calibration slope on test is 1.008 , inside the declared… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 13 | summary | The calibration slope on test is 1.008 , inside the declared… | 1.004 | ratio | calibration_slope | train | eq | `[[art:4c796937:calibration_slope.train]]` | verified | 1.003641864 |
| 14 | conceptual_soundness | The champion is a coefficient-based classifier scored from a… | -1.251 | ratio | intercept |  | eq | `[[art:b82670e1:run.model_summary#intercept]]` | verified | -1.251222675 |
| 15 | conceptual_soundness | The champion is a coefficient-based classifier scored from a… | 1789 | count | n_train | train | eq | `[[art:b82670e1:run.model_summary#n_train]]` | verified | 1789 |
| 16 | conceptual_soundness | The subject's feature declaration carries 12 features. | 12 | count | n |  | eq | `[[art:abbb748e:run.features#n]]` | verified | 12 |
| 17 | conceptual_soundness | Of those, 2 are known at origination and 10 are known before… | 2 | count | at_origination |  | eq | `[[art:abbb748e:run.features#at_origination]]` | verified | 2 |
| 18 | conceptual_soundness | Of those, 2 are known at origination and 10 are known before… | 10 | count | before_period_start |  | eq | `[[art:abbb748e:run.features#before_period_start]]` | verified | 10 |
| 19 | conceptual_soundness | The declaration places 0 features inside the performance per… | 0 | count | during_period |  | eq | `[[art:abbb748e:run.features#during_period]]` | verified | 0 |
| 20 | conceptual_soundness | The declaration places 0 features inside the performance per… | 0 | count | after_outcome |  | eq | `[[art:abbb748e:run.features#after_outcome]]` | verified | 0 |
| 21 | conceptual_soundness | The developer's own screen removed features on a variance-in… | 10 | ratio | vif_threshold |  | eq | `[[art:b82670e1:run.model_summary#vif_threshold]]` | verified | 10 |
| 22 | conceptual_soundness | It dropped bill_last at a variance inflation of 331 , utilis… | 331 | ratio | vif |  | eq | `[[art:b82670e1:run.model_summary#removed.bill_last.vif]]` | verified | 331.003849 |
| 23 | conceptual_soundness | It dropped bill_last at a variance inflation of 331 , utilis… | 59.82 | ratio | vif |  | eq | `[[art:b82670e1:run.model_summary#removed.utilisation_mean_6m.vif]]` | verified | 59.822468 |
| 24 | conceptual_soundness | It dropped bill_last at a variance inflation of 331 , utilis… | 15.57 | ratio | vif |  | eq | `[[art:b82670e1:run.model_summary#removed.bill_mean_6m.vif]]` | verified | 15.569894 |
| 25 | conceptual_soundness | The largest weight falls on delinq_last at 0.6395 , positive… | 0.6395 | ratio | coefficient |  | eq | `[[art:b82670e1:run.model_summary#coefficients.delinq_last.value]]` | verified | 0.6394907151 |
| 26 | conceptual_soundness | The next largest is pay_ratio_mean_6m at -0.4569 , negative,… | -0.4569 | ratio | coefficient |  | eq | `[[art:b82670e1:run.model_summary#coefficients.pay_ratio_mean_6m.value]]` | verified | -0.4568918073 |
| 27 | conceptual_soundness | utilisation carries 0.1902 , positive, consistent with highe… | 0.1902 | ratio | coefficient |  | eq | `[[art:b82670e1:run.model_summary#coefficients.utilisation.value]]` | verified | 0.190177703 |
| 28 | conceptual_soundness | delinq_count_6m carries 0.1046 , positive, again the expecte… | 0.1046 | ratio | coefficient |  | eq | `[[art:b82670e1:run.model_summary#coefficients.delinq_count_6m.value]]` | verified | 0.1046073096 |
| 29 | conceptual_soundness | limit_bal carries -0.07911 and age carries -0.08596 , both m… | -0.07911 | ratio | coefficient |  | eq | `[[art:b82670e1:run.model_summary#coefficients.limit_bal.value]]` | verified | -0.07910795311 |
| 30 | conceptual_soundness | limit_bal carries -0.07911 and age carries -0.08596 , both m… | -0.08596 | ratio | coefficient |  | eq | `[[art:b82670e1:run.model_summary#coefficients.age.value]]` | verified | -0.08596127432 |
| 31 | conceptual_soundness | bill_trend_6m carries -0.07872 , negative, which reads again… | -0.07872 | ratio | coefficient |  | eq | `[[art:b82670e1:run.model_summary#coefficients.bill_trend_6m.value]]` | verified | -0.07871984129 |
| 32 | conceptual_soundness | Two weights run against expectation: pay_ratio_last at 0.187… | 0.1877 | ratio | coefficient |  | eq | `[[art:b82670e1:run.model_summary#coefficients.pay_ratio_last.value]]` | verified | 0.1876796271 |
| 33 | conceptual_soundness | Two weights run against expectation: pay_ratio_last at 0.187… | -0.003169 | ratio | coefficient |  | eq | `[[art:b82670e1:run.model_summary#coefficients.delinq_max_6m.value]]` | verified | -0.003169008451 |
| 34 | conceptual_soundness | The count of retained features whose fitted sign contradicts… | 2 | count | n_disagreements | train | eq | `[[art:66ce738a:sign_check.n_disagreements]]` | verified | 2 |
| 35 | conceptual_soundness | The fitted sign on pay_ratio_last is +1 while its univariate… | 1 | ratio | coef_sign |  | eq | `[[art:f018263e:sign_check.pay_ratio_last.coef_sign]]` | verified | 1 |
| 36 | conceptual_soundness | The fitted sign on pay_ratio_last is +1 while its univariate… | -1 | ratio | univariate_direction | train | eq | `[[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]]` | verified | -1 |
| 37 | conceptual_soundness | The fitted sign on pay_ratio_last is +1 while its univariate… | 0 | ratio | agrees |  | eq | `[[art:79abee77:sign_check.pay_ratio_last.agrees]]` | verified | 0 |
| 38 | conceptual_soundness | Refitting the champion's functional form without that featur… | 0.003621 | ratio | delta_auc | test | eq | `[[art:cc45633b:ablation.pay_ratio_last.delta_auc]]` | verified | 0.003620535247 |
| 39 | conceptual_soundness | The fitted sign on delinq_max_6m is -1 against a univariate… | -1 | ratio | coef_sign |  | eq | `[[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]]` | verified | -1 |
| 40 | conceptual_soundness | The fitted sign on delinq_max_6m is -1 against a univariate… | 1 | ratio | univariate_direction | train | eq | `[[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]]` | verified | 1 |
| 41 | conceptual_soundness | The fitted sign on delinq_max_6m is -1 against a univariate… | 0 | ratio | agrees |  | eq | `[[art:c946359c:sign_check.delinq_max_6m.agrees]]` | verified | 0 |
| 42 | conceptual_soundness | The fitted sign on delinq_max_6m is -1 against a univariate… | 8.165e-05 | ratio | delta_auc | test | eq | `[[art:1d41dd41:ablation.delinq_max_6m.delta_auc]]` | verified | 8.16470246e-05 |
| 43 | conceptual_soundness | Where fitted sign and univariate direction do agree, the agr… | 1 | ratio | agrees |  | eq | `[[art:a8ba9372:sign_check.delinq_last.agrees]]` | verified | 1 |
| 44 | conceptual_soundness | Where fitted sign and univariate direction do agree, the agr… | 1 | ratio | agrees |  | eq | `[[art:d0c9a130:sign_check.utilisation.agrees]]` | verified | 1 |
| 45 | conceptual_soundness | Each ablation change is measured from a refit of the champio… | 0.7525 | ratio | baseline_auc | test | eq | `[[art:6b970cd1:ablation.baseline_auc]]` | verified | 0.7525227655 |
| 46 | conceptual_soundness | Each ablation change is measured from a refit of the champio… | 0.7525 | ratio | auc | test | eq | `[[art:2a5ea4af:metrics.test.auc]]` | verified | 0.7525227655 |
| 47 | conceptual_soundness | Refitting without delinq_last changes test AUC by -0.09255 a… | -0.09255 | ratio | delta_auc | test | eq | `[[art:562511ba:ablation.delinq_last.delta_auc]]` | verified | -0.09254945386 |
| 48 | conceptual_soundness | Refitting without delinq_last changes test AUC by -0.09255 a… | -0.02697 | ratio | delta_auc | test | eq | `[[art:2a417d0d:ablation.utilisation.delta_auc]]` | verified | -0.02697158428 |
| 49 | conceptual_soundness | Refitting without delinq_count_6m changes test AUC by -0.000… | -0.0001378 | ratio | delta_auc | test | eq | `[[art:478e5417:ablation.delinq_count_6m.delta_auc]]` | verified | -0.000137779354 |
| 50 | conceptual_soundness | The remaining changes are positive: 0.007129 for pay_ratio_m… | 0.007129 | ratio | delta_auc | test | eq | `[[art:53d51307:ablation.pay_ratio_mean_6m.delta_auc]]` | verified | 0.007128805836 |
| 51 | conceptual_soundness | The remaining changes are positive: 0.007129 for pay_ratio_m… | 0.007121 | ratio | delta_auc | test | eq | `[[art:b56721dc:ablation.bill_trend_6m.delta_auc]]` | verified | 0.007121151427 |
| 52 | conceptual_soundness | The remaining changes are positive: 0.007129 for pay_ratio_m… | 0.004218 | ratio | delta_auc | test | eq | `[[art:6f97302c:ablation.limit_bal.delta_auc]]` | verified | 0.004217579115 |
| 53 | conceptual_soundness | The remaining changes are positive: 0.007129 for pay_ratio_m… | 0.001077 | ratio | delta_auc | test | eq | `[[art:223939e9:ablation.age.delta_auc]]` | verified | 0.001076720137 |
| 54 | conceptual_soundness | The challenger's test AUC is 0.8221 against the champion's 0… | 0.8221 | ratio | auc | test | eq | `[[art:9a3da49b:challenger.auc]]` | verified | 0.8221294054 |
| 55 | conceptual_soundness | The challenger's test AUC is 0.8221 against the champion's 0… | 0.7525 | ratio | auc | test | eq | `[[art:2a5ea4af:metrics.test.auc]]` | verified | 0.7525227655 |
| 56 | conceptual_soundness | Expressed as a difference in AUC, the challenger's lead is 0… | 0.06961 | ratio | delta_auc | test | eq | `[[art:ce2a1ab8:challenger.delta_auc]]` | verified | 0.06960663994 |
| 57 | conceptual_soundness | Expressed as a difference in AUC, the challenger's lead is 0… | 0.03 | ratio | delta_auc |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 58 | conceptual_soundness | Comparing the two on probability accuracy by level rather th… | 0.125 | ratio | brier | test | eq | `[[art:01fa79a9:challenger.brier]]` | verified | 0.1250082176 |
| 59 | conceptual_soundness | Comparing the two on probability accuracy by level rather th… | 0.1524 | ratio | brier | test | eq | `[[art:7da5c034:metrics.test.brier]]` | verified | 0.1523576419 |
| 60 | data_integrity | The training split holds 1789 rows and the test split holds… | 1789 | count | n | train | eq | `[[art:0f89a4f1:profile.train.n]]` | verified | 1789 |
| 61 | data_integrity | The training split holds 1789 rows and the test split holds… | 1500 | count | n | test | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 62 | data_integrity | The largest missing fraction in the training split is 0 . | 0 | ratio | missing_max | train | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 63 | data_integrity | The largest missing fraction in the test split is 0 . | 0 | ratio | missing_max | test | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 64 | data_integrity | The declared bound is stated as a gap, so the comparison mad… | 0.1 | ratio | missing_gap |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 65 | data_integrity | The largest train-to-test population stability index, the sc… | 1.196 | ratio | psi |  | eq | `[[art:5a6a40fb:psi.max]]` | verified | 1.195887841 |
| 66 | data_integrity | The largest train-to-test population stability index, the sc… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 67 | data_integrity | The largest train-to-test population stability index, the sc… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 68 | data_integrity | That maximum is carried by `limit_bal`, whose index between… | 1.196 | ratio | psi |  | eq | `[[art:c312ae78:psi.limit_bal]]` | verified | 1.195887841 |
| 69 | data_integrity | The score itself shifts by 0.1866 and `bill_trend_6m` by 0.1… | 0.1866 | ratio | psi |  | eq | `[[art:1ecde7e0:psi.y_score]]` | verified | 0.1866241345 |
| 70 | data_integrity | The score itself shifts by 0.1866 and `bill_trend_6m` by 0.1… | 0.1334 | ratio | psi |  | eq | `[[art:41ee0c35:psi.bill_trend_6m]]` | verified | 0.1333601749 |
| 71 | data_integrity | The score itself shifts by 0.1866 and `bill_trend_6m` by 0.1… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 72 | data_integrity | The rest are smaller again: `utilisation` at 0.01936 , `pay_… | 0.01936 | ratio | psi |  | eq | `[[art:e45cb5af:psi.utilisation]]` | verified | 0.01935892092 |
| 73 | data_integrity | The rest are smaller again: `utilisation` at 0.01936 , `pay_… | 0.008826 | ratio | psi |  | eq | `[[art:1e74f864:psi.pay_ratio_mean_6m]]` | verified | 0.008826121484 |
| 74 | data_integrity | The rest are smaller again: `utilisation` at 0.01936 , `pay_… | 0.007293 | ratio | psi |  | eq | `[[art:85162d6e:psi.delinq_max_6m]]` | verified | 0.007293474501 |
| 75 | data_integrity | The rest are smaller again: `utilisation` at 0.01936 , `pay_… | 0.005867 | ratio | psi |  | eq | `[[art:c35c14b6:psi.age]]` | verified | 0.005867466098 |
| 76 | data_integrity | The rest are smaller again: `utilisation` at 0.01936 , `pay_… | 0.002965 | ratio | psi |  | eq | `[[art:35f2b74b:psi.pay_ratio_last]]` | verified | 0.002964692875 |
| 77 | data_integrity | The rest are smaller again: `utilisation` at 0.01936 , `pay_… | 0.002943 | ratio | psi |  | eq | `[[art:f5c55e59:psi.delinq_count_6m]]` | verified | 0.002943407989 |
| 78 | data_integrity | The rest are smaller again: `utilisation` at 0.01936 , `pay_… | 0.0008258 | ratio | psi |  | eq | `[[art:da6a07f2:psi.delinq_last]]` | verified | 0.000825781607 |
| 79 | data_integrity | Characteristic stability, the per-feature contribution to th… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 80 | data_integrity | Characteristic stability, the per-feature contribution to th… | 0.06466 | ratio | csi |  | eq | `[[art:b2e113ad:csi.max]]` | verified | 0.06466414354 |
| 81 | data_integrity | That largest contribution belongs to `limit_bal` at 0.06466… | 0.06466 | ratio | csi |  | eq | `[[art:44fa93ba:csi.limit_bal]]` | verified | 0.06466414354 |
| 82 | data_integrity | The remaining contributions are smaller: `delinq_last` at 0.… | 0.01505 | ratio | csi |  | eq | `[[art:4e9b1ec3:csi.delinq_last]]` | verified | 0.01504852065 |
| 83 | data_integrity | The remaining contributions are smaller: `delinq_last` at 0.… | 0.00576 | ratio | csi |  | eq | `[[art:d7a50342:csi.pay_ratio_mean_6m]]` | verified | 0.005759760061 |
| 84 | data_integrity | The remaining contributions are smaller: `delinq_last` at 0.… | 0.005503 | ratio | csi |  | eq | `[[art:b506bc4b:csi.utilisation]]` | verified | 0.005503189472 |
| 85 | data_integrity | The remaining contributions are smaller: `delinq_last` at 0.… | 0.002501 | ratio | csi |  | eq | `[[art:6d4f0d7b:csi.bill_trend_6m]]` | verified | 0.002501452355 |
| 86 | data_integrity | The remaining contributions are smaller: `delinq_last` at 0.… | 0.002246 | ratio | csi |  | eq | `[[art:7ee6f613:csi.delinq_count_6m]]` | verified | 0.002246336405 |
| 87 | data_integrity | The remaining contributions are smaller: `delinq_last` at 0.… | 0.001222 | ratio | csi |  | eq | `[[art:547b3f3e:csi.pay_ratio_last]]` | verified | 0.00122248434 |
| 88 | data_integrity | The remaining contributions are smaller: `delinq_last` at 0.… | 0.0009235 | ratio | csi |  | eq | `[[art:c3bb7175:csi.age]]` | verified | 0.0009235432986 |
| 89 | data_integrity | The remaining contributions are smaller: `delinq_last` at 0.… | 0.0001002 | ratio | csi |  | eq | `[[art:f775c7df:csi.delinq_max_6m]]` | verified | 0.0001001969452 |
| 90 | data_integrity | The declared-timing screen flags features whose declared tim… | 0 | count | n_flagged |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 91 | data_integrity | The strongest single feature reaches an AUC of 0.6626 on its… | 0.6626 | ratio | auc |  | eq | `[[art:4c34a594:leakage.target_corr.max_single_feature_auc]]` | verified | 0.6626279013 |
| 92 | data_integrity | The strongest single feature reaches an AUC of 0.6626 on its… | 0.9 | ratio | auc |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 93 | data_integrity | The identifier arm reports a share of 0 of test rows whose c… | 0 | ratio | overlap_ids |  | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 94 | data_integrity | The identifier arm reports a share of 0 of test rows whose c… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 95 | data_integrity | The share of train rows whose feature values are not unique… | 0 | ratio | duplicates | train | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 96 | data_integrity | The share of train rows whose feature values are not unique… | 0.005 | ratio | overlap |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 97 | data_integrity | Against that applied bound of 0.005 , the share of test rows… | 0.005 | ratio | overlap |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 98 | data_integrity | Against that applied bound of 0.005 , the share of test rows… | 0 | ratio | overlap_features |  | eq | `[[art:0fec8048:leakage.overlap.features]]` | verified | 0 |
| 99 | data_integrity | Against that applied bound of 0.005 , the share of test rows… | 0 | ratio | overlap |  | eq | `[[art:4c9fcd09:leakage.overlap]]` | verified | 0 |
| 100 | data_integrity | The name screen matches feature names against a target-adjac… | 0 | count | n_matched |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 101 | outcomes | This section leads with discrimination and turns to calibrat… | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 102 | outcomes | This section leads with discrimination and turns to calibrat… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 103 | outcomes | \| Rows \| 1789 \| 1500 \| | 1789 | count | n | train | eq | `[[art:eae7a256:metrics.train.n]]` | verified | 1789 |
| 104 | outcomes | \| Rows \| 1789 \| 1500 \| | 1500 | count | n | test | eq | `[[art:64fcf14d:metrics.test.n]]` | verified | 1500 |
| 105 | outcomes | \| Event rate \| 0.2437 \| 0.2247 \| | 0.2437 | ratio | event_rate | train | eq | `[[art:25e9afa5:metrics.train.event_rate]]` | verified | 0.2437115707 |
| 106 | outcomes | \| Event rate \| 0.2437 \| 0.2247 \| | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 107 | outcomes | \| AUC \| 0.7599 \| 0.7525 \| | 0.7599 | ratio | auc | train | eq | `[[art:3d5f30fa:metrics.train.auc]]` | verified | 0.7599201909 |
| 108 | outcomes | \| AUC \| 0.7599 \| 0.7525 \| | 0.7525 | ratio | auc | test | eq | `[[art:2a5ea4af:metrics.test.auc]]` | verified | 0.7525227655 |
| 109 | outcomes | \| Gini \| 0.5198 \| 0.5050 \| | 0.5198 | ratio | gini | train | eq | `[[art:3198b731:metrics.train.gini]]` | verified | 0.5198403819 |
| 110 | outcomes | \| Gini \| 0.5198 \| 0.5050 \| | 0.505 | ratio | gini | test | eq | `[[art:f00e967c:metrics.test.gini]]` | verified | 0.505045531 |
| 111 | outcomes | \| KS \| 0.4559 \| 0.4306 \| | 0.4559 | ratio | ks | train | eq | `[[art:c2dc79a4:metrics.train.ks]]` | verified | 0.4558914271 |
| 112 | outcomes | \| KS \| 0.4559 \| 0.4306 \| | 0.4306 | ratio | ks | test | eq | `[[art:c3789b0d:metrics.test.ks]]` | verified | 0.4305579298 |
| 113 | outcomes | \| Brier \| 0.1636 \| 0.1524 \| | 0.1636 | ratio | brier | train | eq | `[[art:46973259:metrics.train.brier]]` | verified | 0.1636435165 |
| 114 | outcomes | \| Brier \| 0.1636 \| 0.1524 \| | 0.1524 | ratio | brier | test | eq | `[[art:7da5c034:metrics.test.brier]]` | verified | 0.1523576419 |
| 115 | outcomes | \| Log loss \| 0.4967 \| 0.4717 \| | 0.4967 | ratio | logloss | train | eq | `[[art:73e399ed:metrics.train.logloss]]` | verified | 0.4967129472 |
| 116 | outcomes | \| Log loss \| 0.4967 \| 0.4717 \| | 0.4717 | ratio | logloss | test | eq | `[[art:46b23175:metrics.test.logloss]]` | verified | 0.4717272727 |
| 117 | outcomes | \| Mean predicted \| 0.2437 \| 0.2122 \| | 0.2437 | ratio | mean_predicted | train | eq | `[[art:7bfcb165:metrics.train.mean_predicted]]` | verified | 0.2436878042 |
| 118 | outcomes | \| Mean predicted \| 0.2437 \| 0.2122 \| | 0.2122 | ratio | mean_predicted | test | eq | `[[art:f06b1724:metrics.test.mean_predicted]]` | verified | 0.2121848053 |
| 119 | outcomes | The share of test events falling in the top two deciles is 0… | 0.4392 | ratio | top2_capture | test | eq | `[[art:293e7437:deciles.test.top2_capture]]` | verified | 0.4391691395 |
| 120 | outcomes | The share of test events falling in the top two deciles is 0… | 0.3899 | ratio | top2_capture | train | eq | `[[art:a16b6639:deciles.train.top2_capture]]` | verified | 0.3899082569 |
| 121 | outcomes | The train-to-test movement in discrimination is the distance… | 0.7599 | ratio | auc | train | eq | `[[art:3d5f30fa:metrics.train.auc]]` | verified | 0.7599201909 |
| 122 | outcomes | The train-to-test movement in discrimination is the distance… | 0.7525 | ratio | auc | test | eq | `[[art:2a5ea4af:metrics.test.auc]]` | verified | 0.7525227655 |
| 123 | outcomes | The train-to-test movement in discrimination is the distance… | 0.08 | ratio | auc_gap |  | eq | `[[art:630f28f4:threshold.O1.auc_gap]]` | verified | 0.08 |
| 124 | outcomes | Regressing the outcome on the logit of the predicted probabi… | 1.008 | ratio | calibration_slope | test | eq | `[[art:b918ce48:calibration_slope.test]]` | verified | 1.008335252 |
| 125 | outcomes | Regressing the outcome on the logit of the predicted probabi… | 0.8 | ratio | calibration_slope |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 126 | outcomes | Regressing the outcome on the logit of the predicted probabi… | 1.2 | ratio | calibration_slope |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 127 | outcomes | The same regression on train gives a slope of 1.004 , also i… | 1.004 | ratio | calibration_slope | train | eq | `[[art:4c796937:calibration_slope.train]]` | verified | 1.003641864 |
| 128 | outcomes | The intercept of that regression on test is 0.09438 , above… | 0.09438 | ratio | calibration_intercept | test | eq | `[[art:9a0ff160:calibration_intercept.test]]` | verified | 0.09437539159 |
| 129 | outcomes | The intercept of that regression on test is 0.09438 , above… | 0.004013 | ratio | calibration_intercept | train | eq | `[[art:16a633d0:calibration_intercept.train]]` | verified | 0.004013103211 |
| 130 | outcomes | Mean predicted probability on test is 0.2122 against an obse… | 0.2122 | ratio | mean_predicted | test | eq | `[[art:f06b1724:metrics.test.mean_predicted]]` | verified | 0.2121848053 |
| 131 | outcomes | Mean predicted probability on test is 0.2122 against an obse… | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 132 | outcomes | Expressed as a relative gap that difference is 0.05556 , bel… | 0.05556 | ratio | mean_rel_gap | test | eq | `[[art:844dbd0c:calibration.mean_rel_gap.test]]` | verified | 0.05555724643 |
| 133 | outcomes | Expressed as a relative gap that difference is 0.05556 , bel… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 134 | outcomes | On train the same relative gap is 9.752e-05 , far below the… | 9.752e-05 | ratio | mean_rel_gap | train | eq | `[[art:d0dfeed7:calibration.mean_rel_gap.train]]` | verified | 9.751887447e-05 |
| 135 | outcomes | The exception is stability: the largest train-to-test popula… | 1.196 | ratio | psi |  | eq | `[[art:5a6a40fb:psi.max]]` | verified | 1.195887841 |
| 136 | outcomes | The exception is stability: the largest train-to-test popula… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 137 | outcomes | The first asked for every metric on the slice `limit_bal > m… | 1.196 | ratio | psi |  | eq | `[[art:c312ae78:psi.limit_bal]]` | verified | 1.195887841 |
| 138 | outcomes | AUC on this slice falls 0.01144 below the AUC of the split a… | 0.01144 | ratio | auc_gap | test | eq | `[[art:b05474b5:metrics.test.sub.limit_bal_high.auc_gap]]` | verified | 0.01143653234 |
| 139 | outcomes | AUC on this slice falls 0.01144 below the AUC of the split a… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 140 | outcomes | The slice holds 0.4960 of the split, above the floor of 0.1… | 0.496 | ratio | share | test | eq | `[[art:ac383ccb:metrics.test.sub.limit_bal_high.share]]` | verified | 0.496 |
| 141 | outcomes | The slice holds 0.4960 of the split, above the floor of 0.1… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 142 | outcomes | The slice holds 0.4960 of the split, above the floor of 0.1… | 0.95 | ratio | slice_max_share |  | eq | `[[art:a928a05c:threshold.O1.slice_max_share]]` | verified | 0.95 |
| 143 | outcomes | Mean predicted here is 0.1785 against an observed rate of 0.… | 0.1785 | ratio | mean_predicted | test | eq | `[[art:1538f9f0:metrics.test.sub.limit_bal_high.mean_predicted]]` | verified | 0.1784526975 |
| 144 | outcomes | Mean predicted here is 0.1785 against an observed rate of 0.… | 0.2003 | ratio | event_rate | test | eq | `[[art:5e9aab40:metrics.test.sub.limit_bal_high.event_rate]]` | verified | 0.2002688172 |
| 145 | outcomes | Mean predicted here is 0.1785 against an observed rate of 0.… | 0.1089 | ratio | mean_rel_gap | test | eq | `[[art:4a80a9ee:metrics.test.sub.limit_bal_high.mean_rel_gap]]` | verified | 0.1089341816 |
| 146 | outcomes | AUC on this slice falls -0.007142 below the AUC of the split… | -0.007142 | ratio | auc_gap | test | eq | `[[art:da638efa:metrics.test.sub.limit_bal_low.auc_gap]]` | verified | -0.007141603707 |
| 147 | outcomes | AUC on this slice falls -0.007142 below the AUC of the split… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 148 | outcomes | The slice holds 0.5040 of the split, above the floor of 0.1… | 0.504 | ratio | share | test | eq | `[[art:bac689cc:metrics.test.sub.limit_bal_low.share]]` | verified | 0.504 |
| 149 | outcomes | The slice holds 0.5040 of the split, above the floor of 0.1… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 150 | outcomes | Mean predicted is 0.2454 against an observed rate of 0.2487… | 0.2454 | ratio | mean_predicted | test | eq | `[[art:f220a724:metrics.test.sub.limit_bal_low.mean_predicted]]` | verified | 0.2453814828 |
| 151 | outcomes | Mean predicted is 0.2454 against an observed rate of 0.2487… | 0.2487 | ratio | event_rate | test | eq | `[[art:de78adb5:metrics.test.sub.limit_bal_low.event_rate]]` | verified | 0.2486772487 |
| 152 | outcomes | Mean predicted is 0.2454 against an observed rate of 0.2487… | 0.01325 | ratio | mean_rel_gap | test | eq | `[[art:66be0220:metrics.test.sub.limit_bal_low.mean_rel_gap]]` | verified | 0.01325318612 |
| 153 | outcomes | AUC on this slice falls 0.02106 below the AUC of the split a… | 0.02106 | ratio | auc_gap | test | eq | `[[art:c9b40bd7:metrics.test.sub.delinq_count_6m_high.auc_gap]]` | verified | 0.02106077718 |
| 154 | outcomes | AUC on this slice falls 0.02106 below the AUC of the split a… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 155 | outcomes | The slice holds 0.3667 of the split, above the floor of 0.1… | 0.3667 | ratio | share | test | eq | `[[art:22847310:metrics.test.sub.delinq_count_6m_high.share]]` | verified | 0.3666666667 |
| 156 | outcomes | The slice holds 0.3667 of the split, above the floor of 0.1… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 157 | outcomes | Mean predicted is 0.3010 against an observed rate of 0.3455… | 0.301 | ratio | mean_predicted | test | eq | `[[art:59654f0e:metrics.test.sub.delinq_count_6m_high.mean_predicted]]` | verified | 0.30099024 |
| 158 | outcomes | Mean predicted is 0.3010 against an observed rate of 0.3455… | 0.3455 | ratio | event_rate | test | eq | `[[art:ef17c303:metrics.test.sub.delinq_count_6m_high.event_rate]]` | verified | 0.3454545455 |
| 159 | outcomes | Mean predicted is 0.3010 against an observed rate of 0.3455… | 0.1287 | ratio | mean_rel_gap | test | eq | `[[art:24f57004:metrics.test.sub.delinq_count_6m_high.mean_rel_gap]]` | verified | 0.1287124632 |
| 160 | outcomes | AUC on this slice falls 0.06612 below the AUC of the split a… | 0.06612 | ratio | auc_gap | test | eq | `[[art:2df7bb74:metrics.test.sub.delinq_count_6m_low.auc_gap]]` | verified | 0.06611719454 |
| 161 | outcomes | AUC on this slice falls 0.06612 below the AUC of the split a… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 162 | outcomes | The slice holds 0.6333 of the split, above the floor of 0.1… | 0.6333 | ratio | share | test | eq | `[[art:3257b2f3:metrics.test.sub.delinq_count_6m_low.share]]` | verified | 0.6333333333 |
| 163 | outcomes | The slice holds 0.6333 of the split, above the floor of 0.1… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 164 | outcomes | Mean predicted is 0.1608 against an observed rate of 0.1547… | 0.1608 | ratio | mean_predicted | test | eq | `[[art:4e8141df:metrics.test.sub.delinq_count_6m_low.mean_predicted]]` | verified | 0.1607711326 |
| 165 | outcomes | Mean predicted is 0.1608 against an observed rate of 0.1547… | 0.1547 | ratio | event_rate | test | eq | `[[art:9690f94d:metrics.test.sub.delinq_count_6m_low.event_rate]]` | verified | 0.1547368421 |
| 166 | outcomes | Mean predicted is 0.1608 against an observed rate of 0.1547… | 0.039 | ratio | mean_rel_gap | test | eq | `[[art:d450f3dd:metrics.test.sub.delinq_count_6m_low.mean_rel_gap]]` | verified | 0.03899711543 |
| 167 | sensitivity | The largest variance inflation factor across the retained fe… | 7.662 | ratio | vif |  | eq | `[[art:3a027a9e:vif.max]]` | verified | 7.661689317 |
| 168 | sensitivity | The largest variance inflation factor across the retained fe… | 10 | ratio | vif |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 169 | sensitivity | That maximum is attained by the last-period payment ratio at… | 7.662 | ratio | vif |  | eq | `[[art:906f9c92:vif.pay_ratio_last]]` | verified | 7.661689317 |
| 170 | sensitivity | That maximum is attained by the last-period payment ratio at… | 7.649 | ratio | vif |  | eq | `[[art:d5c149e7:vif.pay_ratio_mean_6m]]` | verified | 7.649492506 |
| 171 | sensitivity | The delinquency-count feature over the trailing window follo… | 2.482 | ratio | vif |  | eq | `[[art:ca8684a5:vif.delinq_count_6m]]` | verified | 2.48208755 |
| 172 | sensitivity | The delinquency-count feature over the trailing window follo… | 2.36 | ratio | vif |  | eq | `[[art:21212f86:vif.delinq_max_6m]]` | verified | 2.359652386 |
| 173 | sensitivity | The most recent delinquency indicator is lower still at 1.36… | 1.366 | ratio | vif |  | eq | `[[art:610d9380:vif.delinq_last]]` | verified | 1.365552784 |
| 174 | sensitivity | The remaining retained features sit close to the no-inflatio… | 1.01 | ratio | vif |  | eq | `[[art:e9e68e9c:vif.bill_trend_6m]]` | verified | 1.010358598 |
| 175 | sensitivity | The remaining retained features sit close to the no-inflatio… | 1.005 | ratio | vif |  | eq | `[[art:f6c05005:vif.limit_bal]]` | verified | 1.005403299 |
| 176 | sensitivity | The remaining retained features sit close to the no-inflatio… | 1.003 | ratio | vif |  | eq | `[[art:f810d89d:vif.utilisation]]` | verified | 1.003462873 |
| 177 | sensitivity | The remaining retained features sit close to the no-inflatio… | 1.002 | ratio | vif |  | eq | `[[art:4c6350d4:vif.age]]` | verified | 1.001975689 |
| 178 | sensitivity | Belsley's condition number of the column-standardised design… | 5.647 | ratio | condition_number |  | eq | `[[art:81de583f:condition_number]]` | verified | 5.646856643 |
| 179 | sensitivity | Belsley's condition number of the column-standardised design… | 30 | ratio | condition_number |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 180 | findings | The largest recomputed train-to-test population stability in… | 1.196 | ratio | psi |  | eq | `[[art:5a6a40fb:psi.max]]` | verified | 1.195887841 |
| 181 | findings | That value sits above the ceiling of 0.25 declared in packag… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 182 | findings | The population stability index between train and test on `li… | 1.196 | ratio | psi |  | eq | `[[art:c312ae78:psi.limit_bal]]` | verified | 1.195887841 |
| 183 | findings | It is read against the stability threshold of 0.25 , and aga… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 184 | findings | A hist_gradient_boosting challenger reaches an AUC on test o… | 0.8221 | ratio | auc | test | eq | `[[art:9a3da49b:challenger.auc]]` | verified | 0.8221294054 |
| 185 | findings | A hist_gradient_boosting challenger reaches an AUC on test o… | 0.7525 | ratio | auc | test | eq | `[[art:2a5ea4af:metrics.test.auc]]` | verified | 0.7525227655 |
| 186 | findings | The difference between the two, which is the comparison reco… | 0.06961 | ratio | delta_auc | test | eq | `[[art:ce2a1ab8:challenger.delta_auc]]` | verified | 0.06960663994 |
| 187 | findings | The difference between the two, which is the comparison reco… | 0.03 | ratio | delta_auc |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 188 | findings | Model developer: what does the model discriminate on within… | -1 | ratio | coef_sign |  | eq | `[[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]]` | verified | -1 |
| 189 | findings | Model developer: what does the model discriminate on within… | 1 | ratio | univariate_direction |  | eq | `[[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]]` | verified | 1 |
| 190 | findings | Model developer: what does the model discriminate on within… | 0 | ratio | agrees |  | eq | `[[art:c946359c:sign_check.delinq_max_6m.agrees]]` | verified | 0 |
| 191 | findings | Model developer: what does the model discriminate on within… | 1 | ratio | coef_sign |  | eq | `[[art:f018263e:sign_check.pay_ratio_last.coef_sign]]` | verified | 1 |
| 192 | findings | Model developer: what does the model discriminate on within… | -1 | ratio | univariate_direction |  | eq | `[[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]]` | verified | -1 |
| 193 | findings | Model developer: what does the model discriminate on within… | 0 | ratio | agrees |  | eq | `[[art:79abee77:sign_check.pay_ratio_last.agrees]]` | verified | 0 |
| 194 | monitoring | Track rank-ordering performance on each production vintage o… | 0.7 | ratio | auc | test | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 195 | monitoring | Track rank-ordering performance on each production vintage o… | 0.7525 | ratio | auc | test | eq | `[[art:2a5ea4af:metrics.test.auc]]` | verified | 0.7525227655 |
| 196 | monitoring | Track the mean squared probability error on the same vintage… | 0.2 | ratio | brier | test | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 197 | monitoring | Track the mean squared probability error on the same vintage… | 0.1524 | ratio | brier | test | eq | `[[art:7da5c034:metrics.test.brier]]` | verified | 0.1523576419 |
| 198 | monitoring | Track the regression slope of the outcome on the model's log… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 199 | monitoring | Track the regression slope of the outcome on the model's log… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 200 | monitoring | Track the regression slope of the outcome on the model's log… | 1.008 | ratio | calibration_slope | test | eq | `[[art:b918ce48:calibration_slope.test]]` | verified | 1.008335252 |
| 201 | monitoring | Track the train-to-production population stability of each i… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 202 | monitoring | Track the train-to-production population stability of each i… | 1.196 | ratio | psi |  | eq | `[[art:5a6a40fb:psi.max]]` | verified | 1.195887841 |
| 203 | monitoring | Because the observed event rate on the evaluation split was… | 0.05 | ratio | event_rate | test | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 204 | monitoring | If a future monitored cohort has an observed event rate belo… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |

## Appendix B — Artifact index

The store holds 212 artifacts; the 140 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `ablation.age.delta_auc` | `223939e9` | scalar | 0.001076720137 | change in test AUC when the champion's form is refitted without age |
| `ablation.baseline_auc` | `6b970cd1` | scalar | 0.7525227655 | AUC on test of a refit of the champion's functional form on every retained feature, the level each ablation delta is measured from |
| `ablation.bill_trend_6m.delta_auc` | `b56721dc` | scalar | 0.007121151427 | change in test AUC when the champion's form is refitted without bill_trend_6m |
| `ablation.delinq_count_6m.delta_auc` | `478e5417` | scalar | -0.000137779354 | change in test AUC when the champion's form is refitted without delinq_count_6m |
| `ablation.delinq_last.delta_auc` | `562511ba` | scalar | -0.09254945386 | change in test AUC when the champion's form is refitted without delinq_last |
| `ablation.delinq_max_6m.delta_auc` | `1d41dd41` | scalar | 8.16470246e-05 | change in test AUC when the champion's form is refitted without delinq_max_6m |
| `ablation.limit_bal.delta_auc` | `6f97302c` | scalar | 0.004217579115 | change in test AUC when the champion's form is refitted without limit_bal |
| `ablation.pay_ratio_last.delta_auc` | `cc45633b` | scalar | 0.003620535247 | change in test AUC when the champion's form is refitted without pay_ratio_last |
| `ablation.pay_ratio_mean_6m.delta_auc` | `53d51307` | scalar | 0.007128805836 | change in test AUC when the champion's form is refitted without pay_ratio_mean_6m |
| `ablation.utilisation.delta_auc` | `2a417d0d` | scalar | -0.02697158428 | change in test AUC when the champion's form is refitted without utilisation |
| `calibration.mean_rel_gap.test` | `844dbd0c` | scalar | 0.05555724643 | mean predicted against observed on test, relative |
| `calibration.mean_rel_gap.train` | `d0dfeed7` | scalar | 9.751887447e-05 | mean predicted against observed on train, relative |
| `calibration.test` | `e84a960d` | table | table, 10 rows | calibration by decile of predicted probability on test |
| `calibration_intercept.test` | `9a0ff160` | scalar | 0.09437539159 | logistic regression of the outcome on logit(p) on test: the intercept |
| `calibration_intercept.train` | `16a633d0` | scalar | 0.004013103211 | logistic regression of the outcome on logit(p) on train: the intercept |
| `calibration_slope.test` | `b918ce48` | scalar | 1.008335252 | logistic regression of the outcome on logit(p) on test: the slope |
| `calibration_slope.train` | `4c796937` | scalar | 1.003641864 | logistic regression of the outcome on logit(p) on train: the slope |
| `challenger.auc` | `9a3da49b` | scalar | 0.8221294054 | the challenger's AUC on test |
| `challenger.brier` | `01fa79a9` | scalar | 0.1250082176 | the challenger's Brier score on test |
| `challenger.delta_auc` | `ce2a1ab8` | scalar | 0.06960663994 | the challenger's AUC on test minus the champion's |
| `condition_number` | `81de583f` | scalar | 5.646856643 | Belsley's condition number of the column-standardised design |
| `csi.age` | `c3bb7175` | scalar | 0.0009235432986 | CSI of age: its contribution to the shift in the linear predictor |
| `csi.bill_trend_6m` | `6d4f0d7b` | scalar | 0.002501452355 | CSI of bill_trend_6m: its contribution to the shift in the linear predictor |
| `csi.delinq_count_6m` | `7ee6f613` | scalar | 0.002246336405 | CSI of delinq_count_6m: its contribution to the shift in the linear predictor |
| `csi.delinq_last` | `4e9b1ec3` | scalar | 0.01504852065 | CSI of delinq_last: its contribution to the shift in the linear predictor |
| `csi.delinq_max_6m` | `f775c7df` | scalar | 0.0001001969452 | CSI of delinq_max_6m: its contribution to the shift in the linear predictor |
| `csi.limit_bal` | `44fa93ba` | scalar | 0.06466414354 | CSI of limit_bal: its contribution to the shift in the linear predictor |
| `csi.max` | `b2e113ad` | scalar | 0.06466414354 | the largest characteristic stability index |
| `csi.pay_ratio_last` | `547b3f3e` | scalar | 0.00122248434 | CSI of pay_ratio_last: its contribution to the shift in the linear predictor |
| `csi.pay_ratio_mean_6m` | `d7a50342` | scalar | 0.005759760061 | CSI of pay_ratio_mean_6m: its contribution to the shift in the linear predictor |
| `csi.utilisation` | `b506bc4b` | scalar | 0.005503189472 | CSI of utilisation: its contribution to the shift in the linear predictor |
| `deciles.test` | `97ae0549` | table | table, 10 rows | decile separation on test; decile 1 holds the highest probabilities |
| `deciles.test.top2_capture` | `293e7437` | scalar | 0.4391691395 | share of test events in the top two deciles |
| `deciles.train.top2_capture` | `a16b6639` | scalar | 0.3899082569 | share of train events in the top two deciles |
| `leakage.duplicates.train` | `4474c227` | scalar | 0 | share of train rows whose feature values are not unique within train |
| `leakage.name_screen.n_matched` | `407e62be` | scalar | 0 | feature names matching the target-adjacent lexicon |
| `leakage.overlap` | `4c9fcd09` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.features` | `0fec8048` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.ids` | `63d37fc5` | scalar | 0 | share of test rows whose ['client_id'] also identify a row of train |
| `leakage.target_corr.max_single_feature_auc` | `4c34a594` | scalar | 0.6626279013 | the AUC of the strongest single feature |
| `leakage.timing.n_flagged` | `742bcd24` | scalar | 0 | features declared during_period or after_outcome |
| `metrics.test.auc` | `2a5ea4af` | scalar | 0.7525227655 | auc on test, recomputed by quaestor |
| `metrics.test.brier` | `7da5c034` | scalar | 0.1523576419 | brier on test, recomputed by quaestor |
| `metrics.test.event_rate` | `9209d200` | scalar | 0.2246666667 | event_rate on test, recomputed by quaestor |
| `metrics.test.gini` | `f00e967c` | scalar | 0.505045531 | gini on test, recomputed by quaestor |
| `metrics.test.ks` | `c3789b0d` | scalar | 0.4305579298 | ks on test, recomputed by quaestor |
| `metrics.test.logloss` | `46b23175` | scalar | 0.4717272727 | logloss on test, recomputed by quaestor |
| `metrics.test.mean_predicted` | `f06b1724` | scalar | 0.2121848053 | mean_predicted on test, recomputed by quaestor |
| `metrics.test.n` | `64fcf14d` | scalar | 1500 | n on test, recomputed by quaestor |
| `metrics.test.sub.delinq_count_6m_high` | `ebc1557e` | table | table, 10 rows | every metric on the delinq_count_6m above_median slice of test |
| `metrics.test.sub.delinq_count_6m_high.auc_gap` | `c9b40bd7` | scalar | 0.02106077718 | how far AUC on the delinq_count_6m above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.delinq_count_6m_high.event_rate` | `ef17c303` | scalar | 0.3454545455 | event_rate on the delinq_count_6m above_median slice of test |
| `metrics.test.sub.delinq_count_6m_high.mean_predicted` | `59654f0e` | scalar | 0.30099024 | mean_predicted on the delinq_count_6m above_median slice of test |
| `metrics.test.sub.delinq_count_6m_high.mean_rel_gap` | `24f57004` | scalar | 0.1287124632 | mean predicted against observed on the delinq_count_6m above_median slice of test, relative |
| `metrics.test.sub.delinq_count_6m_high.share` | `22847310` | scalar | 0.3666666667 | the share of test the delinq_count_6m above_median slice holds |
| `metrics.test.sub.delinq_count_6m_low` | `ae54b16c` | table | table, 10 rows | every metric on the delinq_count_6m below_median slice of test |
| `metrics.test.sub.delinq_count_6m_low.auc_gap` | `2df7bb74` | scalar | 0.06611719454 | how far AUC on the delinq_count_6m below_median slice of test falls below AUC on all of test |
| `metrics.test.sub.delinq_count_6m_low.event_rate` | `9690f94d` | scalar | 0.1547368421 | event_rate on the delinq_count_6m below_median slice of test |
| `metrics.test.sub.delinq_count_6m_low.mean_predicted` | `4e8141df` | scalar | 0.1607711326 | mean_predicted on the delinq_count_6m below_median slice of test |
| `metrics.test.sub.delinq_count_6m_low.mean_rel_gap` | `d450f3dd` | scalar | 0.03899711543 | mean predicted against observed on the delinq_count_6m below_median slice of test, relative |
| `metrics.test.sub.delinq_count_6m_low.share` | `3257b2f3` | scalar | 0.6333333333 | the share of test the delinq_count_6m below_median slice holds |
| `metrics.test.sub.limit_bal_high` | `aaa6b180` | table | table, 10 rows | every metric on the limit_bal above_median slice of test |
| `metrics.test.sub.limit_bal_high.auc_gap` | `b05474b5` | scalar | 0.01143653234 | how far AUC on the limit_bal above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.limit_bal_high.event_rate` | `5e9aab40` | scalar | 0.2002688172 | event_rate on the limit_bal above_median slice of test |
| `metrics.test.sub.limit_bal_high.mean_predicted` | `1538f9f0` | scalar | 0.1784526975 | mean_predicted on the limit_bal above_median slice of test |
| `metrics.test.sub.limit_bal_high.mean_rel_gap` | `4a80a9ee` | scalar | 0.1089341816 | mean predicted against observed on the limit_bal above_median slice of test, relative |
| `metrics.test.sub.limit_bal_high.share` | `ac383ccb` | scalar | 0.496 | the share of test the limit_bal above_median slice holds |
| `metrics.test.sub.limit_bal_low` | `fd28f3a8` | table | table, 10 rows | every metric on the limit_bal below_median slice of test |
| `metrics.test.sub.limit_bal_low.auc_gap` | `da638efa` | scalar | -0.007141603707 | how far AUC on the limit_bal below_median slice of test falls below AUC on all of test |
| `metrics.test.sub.limit_bal_low.event_rate` | `de78adb5` | scalar | 0.2486772487 | event_rate on the limit_bal below_median slice of test |
| `metrics.test.sub.limit_bal_low.mean_predicted` | `f220a724` | scalar | 0.2453814828 | mean_predicted on the limit_bal below_median slice of test |
| `metrics.test.sub.limit_bal_low.mean_rel_gap` | `66be0220` | scalar | 0.01325318612 | mean predicted against observed on the limit_bal below_median slice of test, relative |
| `metrics.test.sub.limit_bal_low.share` | `bac689cc` | scalar | 0.504 | the share of test the limit_bal below_median slice holds |
| `metrics.train.auc` | `3d5f30fa` | scalar | 0.7599201909 | auc on train, recomputed by quaestor |
| `metrics.train.brier` | `46973259` | scalar | 0.1636435165 | brier on train, recomputed by quaestor |
| `metrics.train.event_rate` | `25e9afa5` | scalar | 0.2437115707 | event_rate on train, recomputed by quaestor |
| `metrics.train.gini` | `3198b731` | scalar | 0.5198403819 | gini on train, recomputed by quaestor |
| `metrics.train.ks` | `c2dc79a4` | scalar | 0.4558914271 | ks on train, recomputed by quaestor |
| `metrics.train.logloss` | `73e399ed` | scalar | 0.4967129472 | logloss on train, recomputed by quaestor |
| `metrics.train.mean_predicted` | `7bfcb165` | scalar | 0.2436878042 | mean_predicted on train, recomputed by quaestor |
| `metrics.train.n` | `eae7a256` | scalar | 1789 | n on train, recomputed by quaestor |
| `profile.test.missing.max` | `f813848d` | scalar | 0 | the largest missing fraction in test |
| `profile.test.n` | `2193cf5f` | scalar | 1500 | rows in test |
| `profile.train.missing.max` | `050a3099` | scalar | 0 | the largest missing fraction in train |
| `profile.train.n` | `0f89a4f1` | scalar | 1789 | rows in train |
| `psi.age` | `c35c14b6` | scalar | 0.005867466098 | PSI of age between train and test |
| `psi.bill_trend_6m` | `41ee0c35` | scalar | 0.1333601749 | PSI of bill_trend_6m between train and test |
| `psi.delinq_count_6m` | `f5c55e59` | scalar | 0.002943407989 | PSI of delinq_count_6m between train and test |
| `psi.delinq_last` | `da6a07f2` | scalar | 0.000825781607 | PSI of delinq_last between train and test |
| `psi.delinq_max_6m` | `85162d6e` | scalar | 0.007293474501 | PSI of delinq_max_6m between train and test |
| `psi.limit_bal` | `c312ae78` | scalar | 1.195887841 | PSI of limit_bal between train and test |
| `psi.max` | `5a6a40fb` | scalar | 1.195887841 | the largest train-to-test PSI, score included |
| `psi.pay_ratio_last` | `35f2b74b` | scalar | 0.002964692875 | PSI of pay_ratio_last between train and test |
| `psi.pay_ratio_mean_6m` | `1e74f864` | scalar | 0.008826121484 | PSI of pay_ratio_mean_6m between train and test |
| `psi.utilisation` | `e45cb5af` | scalar | 0.01935892092 | PSI of utilisation between train and test |
| `psi.y_score` | `1ecde7e0` | scalar | 0.1866241345 | PSI of the score between train and test |
| `rule.calibration_first_event_rate` | `42f1351e` | scalar | 0.05 | the event rate below which the report puts calibration before discrimination |
| `run.features` | `abbb748e` | json | json | the subject's features.json |
| `run.model_summary` | `b82670e1` | json | json | the subject's model_summary.json |
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |
| `sign_check.delinq_last.agrees` | `a8ba9372` | scalar | 1 | 1 when the fitted sign on delinq_last agrees with its univariate direction, 0 when it does not |
| `sign_check.delinq_max_6m.agrees` | `c946359c` | scalar | 0 | 1 when the fitted sign on delinq_max_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.delinq_max_6m.coef_sign` | `a07d68ab` | scalar | -1 | the sign of the fitted coefficient on delinq_max_6m |
| `sign_check.delinq_max_6m.univariate_direction` | `b9088f4a` | scalar | 1 | the sign of delinq_max_6m's own single-feature AUC on train minus 0.5 |
| `sign_check.n_disagreements` | `66ce738a` | scalar | 2 | retained features whose fitted sign contradicts their univariate direction, of 9 checked |
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
| `threshold.package.auc.test.min` | `8bfd02cc` | scalar | 0.7 | package.yaml declares auc min 0.7 |
| `threshold.package.brier.test.max` | `d0f98b9c` | scalar | 0.2 | package.yaml declares brier max 0.2 |
| `threshold.package.calibration_slope.test.max` | `0adb7a89` | scalar | 1.2 | package.yaml declares calibration_slope max 1.2 |
| `threshold.package.calibration_slope.test.min` | `95fdb848` | scalar | 0.8 | package.yaml declares calibration_slope min 0.8 |
| `threshold.package.psi.max` | `fbb5a9d1` | scalar | 0.25 | package.yaml declares psi max 0.25 |
| `thresholds.evaluation` | `7633a313` | table | table, 5 rows | every threshold package.yaml declares, with its bound, the recomputed value and the outcome |
| `vif.age` | `4c6350d4` | scalar | 1.001975689 | variance inflation factor of age on train |
| `vif.bill_trend_6m` | `e9e68e9c` | scalar | 1.010358598 | variance inflation factor of bill_trend_6m on train |
| `vif.delinq_count_6m` | `ca8684a5` | scalar | 2.48208755 | variance inflation factor of delinq_count_6m on train |
| `vif.delinq_last` | `610d9380` | scalar | 1.365552784 | variance inflation factor of delinq_last on train |
| `vif.delinq_max_6m` | `21212f86` | scalar | 2.359652386 | variance inflation factor of delinq_max_6m on train |
| `vif.limit_bal` | `f6c05005` | scalar | 1.005403299 | variance inflation factor of limit_bal on train |
| `vif.max` | `3a027a9e` | scalar | 7.661689317 | the largest variance inflation factor |
| `vif.pay_ratio_last` | `906f9c92` | scalar | 7.661689317 | variance inflation factor of pay_ratio_last on train |
| `vif.pay_ratio_mean_6m` | `d5c149e7` | scalar | 7.649492506 | variance inflation factor of pay_ratio_mean_6m on train |
| `vif.utilisation` | `f810d89d` | scalar | 1.003462873 | variance inflation factor of utilisation on train |

## Appendix C — Run trace summary

| quantity | value |
|---|---|
| tool calls | 17 (run_model 1, profile_data 1, compute_metrics 5, check_leakage 1, check_collinearity 1, challenger_compare 1, retrieve_guidance 7) |
| plan steps (bounded loop) | 4 |
| LLM calls | 20 (plan 4, draft 8, extract 8) |
| re-asks | 0 |
| repair rounds | 1 |
| tokens in / out | 247,946 / 105,343 |
| notional cost (USD) | 5.1587 |
| wall-clock (s) | 1196.98 |
| subject run (s) | 1.54 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | credit_default-full_agent-20260920T093731Z-e2e51e00 |

## Appendix D — Not checked

| item | reason |
|---|---|
| `check_stability` (R1) | package declares no `regime.column` |
| `run_scenarios` (X1) | not applicable to `binary_classification` |
| out-of-time and vintage-holdout metrics (O1, second rule) | package declares neither split |
| developer claims (T1, claim channel) | The package declares 2 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
