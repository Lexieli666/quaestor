---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: full_agent
model: claude-opus-5[1m]
run_id: credit_default-full_agent-20260920T074524Z-e2e51e00
data_mode: synthetic
synthetic_n: 5000
grounding_precision_pre: 1.0000
grounding_precision_post: 1.0000
n_claims: 263
n_findings_by_severity: {high: 0, medium: 1, low: 1, info: 0}
generated: "2026-09-20T07:45:24Z"
illustrative: false
---

# Validation report — `credit_default` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `credit_default` v1.0 | `full_agent` | claude-opus-5[1m] | synthetic, n = 5000 | 1.0000 → 1.0000 | 0 / 1 / 1 / 0 |
<!-- quaestor:renderer:end -->

The subject of this report is the model package credit_default version 1.0, a binary classifier that predicts the probability that a borrower defaults, and this report follows the structure of the Federal Reserve's model risk management guidance on validation and monitoring [[reg:SR26-2:V]].
The subject was run end to end by the validation harness under the wall-clock cap of 300 [[art:2ad8d1a5:runtime.max_seconds]] seconds that the package declares, and every performance figure quoted here was recomputed by the harness from the subject's scored output rather than taken from the developer's own reporting.
The fitting split holds 3545 [[art:1ff4e472:profile.train.n]] rows and the held-out split holds 1500 [[art:2193cf5f:profile.test.n]] rows.

On the held-out split the model clears each developer-declared threshold exercised in this section.
Discrimination reaches 0.748 [[art:33170ddf:metrics.test.auc]], above the declared floor of 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]].
The Brier score is 0.149 [[art:3be8087d:metrics.test.brier]], below the declared ceiling of 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]].
The calibration slope of the outcome on the logit of the prediction is 1.001 [[art:95a66bf5:calibration_slope.test]], inside the declared band running from 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] to 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The largest population stability index measured from the fitting split to the held-out split, the score included, is 0.01082 [[art:9300bdd4:psi.max]], well below the declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
Discrimination on the held-out split, at 0.748 [[art:33170ddf:metrics.test.auc]], sits below the fitting-split figure of 0.7589 [[art:92ca327f:metrics.train.auc]], a direction consistent with ordinary out-of-sample attenuation rather than with a break in performance.

The assessment of outcomes against declared performance thresholds that this section summarises is the activity described at [[reg:SR26-2:V.1.b]], and the threshold results above are not the whole of this validation's conclusion.
This validation published F-001, a L2 contamination finding at medium severity, and F-002, an E1 effective challenge finding at low severity.
Both are written out in full, with their evidence and their disposition, in the findings section of this report.

## 2. Conceptual soundness

Validating conceptual soundness involves assessing model design, construction and developmental evidence, and where theoretical construction is hard to judge directly, interpretability measures and benchmarking to other models carry the assessment [[reg:SR26-2:V.1.a]].
The champion is a linear scoring form with one coefficient per retained feature and an intercept of -1.397 [[art:259cdde6:run.model_summary#intercept]], fitted on 3545 [[art:259cdde6:run.model_summary#n_train]] training rows, and it scores 0.7480 [[art:33170ddf:metrics.test.auc]] on test with a Brier score of 0.1490 [[art:3be8087d:metrics.test.brier]].

### Features and their timing

The feature inventory the subject declares holds 12 [[art:abbb748e:run.features#n]] features in total.
Of those, 2 [[art:abbb748e:run.features#at_origination]] are known at origination and 10 [[art:abbb748e:run.features#before_period_start]] are known before the performance period starts.
None are observed during the performance period, at 0 [[art:abbb748e:run.features#during_period]], and none are observed after the outcome, at 0 [[art:abbb748e:run.features#after_outcome]].
On the timing declared, then, every input is knowable at scoring time, and the design carries no input that would only be available once the outcome is known.

### The collinearity screen

The developer's own screen dropped two candidate features for variance inflation, against a screen threshold of 10 [[art:259cdde6:run.model_summary#vif_threshold]].
The last bill amount was removed at a variance inflation factor of 161.1 [[art:259cdde6:run.model_summary#removed.bill_last.vif]], far above that threshold.
The six-month mean utilisation was removed at 36.45 [[art:259cdde6:run.model_summary#removed.utilisation_mean_6m.vif]], also above it and the smaller of the two.
Both removals are the expected consequence of retaining a level, a mean and a trend built from the same billing and utilisation series, and dropping the two most redundant of them is a defensible design choice rather than a substantive loss of information.

### Coefficients and expected signs

The largest coefficient in the fitted model is on the most recent delinquency status, at 0.7279 [[art:259cdde6:run.model_summary#coefficients.delinq_last.value]], positive as credit subject matter expects: a worse recent repayment status raises modelled default risk.
The next largest in magnitude are the six-month mean payment ratio at -0.3768 [[art:259cdde6:run.model_summary#coefficients.pay_ratio_mean_6m.value]] and the six-month mean bill amount at -0.3703 [[art:259cdde6:run.model_summary#coefficients.bill_mean_6m.value]], and the negative sign on the payment ratio is what a lender would expect, since paying down more of the balance should lower risk.
Utilisation carries 0.2700 [[art:259cdde6:run.model_summary#coefficients.utilisation.value]], positive and consistent with the expectation that borrowers closer to their limit are riskier, and the six-month bill trend carries -0.2243 [[art:259cdde6:run.model_summary#coefficients.bill_trend_6m.value]].
Age carries -0.06933 [[art:259cdde6:run.model_summary#coefficients.age.value]], the direction conventionally expected on this portfolio, and the six-month delinquency count carries 0.1244 [[art:259cdde6:run.model_summary#coefficients.delinq_count_6m.value]], also in the expected direction.
Two coefficients run against what the subject matter would predict: the credit limit at 0.07419 [[art:259cdde6:run.model_summary#coefficients.limit_bal.value]], where a larger granted limit ordinarily signals a better risk, and the most recent payment ratio at 0.1180 [[art:259cdde6:run.model_summary#coefficients.pay_ratio_last.value]], where paying a larger share of the bill ordinarily signals a better risk.
The six-month maximum delinquency carries -0.03047 [[art:259cdde6:run.model_summary#coefficients.delinq_max_6m.value]], negative where a worse delinquency peak should, on its own, raise risk.

### Fitted signs against univariate directions

The sign diagnostic counts 3 [[art:e223cd4a:sign_check.n_disagreements]] retained features whose fitted coefficient sign contradicts the sign of that feature's own single-feature relationship with the outcome on train.
Each ablation delta below is measured from a refit of the champion's functional form on every retained feature, which scores 0.7480 [[art:818e6d21:ablation.baseline_auc]] on test, the same level as the recomputed champion AUC.
The credit limit is one of the three: its fitted sign is +1 [[art:6af6aef2:sign_check.limit_bal.coef_sign]] while its univariate direction is -1 [[art:56d284d6:sign_check.limit_bal.univariate_direction]], recorded as a disagreement at 0 [[art:0278aad1:sign_check.limit_bal.agrees]].
Refitting without the credit limit changes test AUC by 0.0004695 [[art:d47e9a58:ablation.limit_bal.delta_auc]], an improvement rather than a loss, so the flipped sign sits on a feature the model was not drawing discrimination from.
The most recent payment ratio is the second: its fitted sign is +1 [[art:f018263e:sign_check.pay_ratio_last.coef_sign]] against a univariate direction of -1 [[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]], recorded as a disagreement at 0 [[art:79abee77:sign_check.pay_ratio_last.agrees]].
Refitting without it changes test AUC by 0.002847 [[art:1918798e:ablation.pay_ratio_last.delta_auc]], again an improvement, and the largest such improvement among the three disagreeing features.
The six-month maximum delinquency is the third: its fitted sign is -1 [[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]] against a univariate direction of +1 [[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]], recorded as a disagreement at 0 [[art:c946359c:sign_check.delinq_max_6m.agrees]].
Refitting without it changes test AUC by 0.000296 [[art:975f1df6:ablation.delinq_max_6m.delta_auc]], the smallest of the three improvements, so this disagreement sits on a feature of negligible contribution.
Read together, all three sign flips fall on features whose removal does not cost discrimination, which points to collinearity among the delinquency and payment-ratio blocks reallocating sign rather than to a feature whose contribution the model depends on being fitted backwards.
The remaining features agree: the most recent delinquency status at 1 [[art:a8ba9372:sign_check.delinq_last.agrees]], utilisation at 1 [[art:d0c9a130:sign_check.utilisation.agrees]], the six-month delinquency count at 1 [[art:a337d16b:sign_check.delinq_count_6m.agrees]], the six-month mean payment ratio at 1 [[art:7e9a76ca:sign_check.pay_ratio_mean_6m.agrees]], the six-month mean bill at 1 [[art:89279c3b:sign_check.bill_mean_6m.agrees]], the six-month bill trend at 1 [[art:ff3cb24a:sign_check.bill_trend_6m.agrees]] and age at 1 [[art:4116add1:sign_check.age.agrees]].
The fitted and univariate signs coincide on the most recent delinquency status at +1 [[art:50d352f8:sign_check.delinq_last.coef_sign]] and +1 [[art:a78648ba:sign_check.delinq_last.univariate_direction]], on utilisation at +1 [[art:85badc3c:sign_check.utilisation.coef_sign]] and +1 [[art:f0995196:sign_check.utilisation.univariate_direction]], and on the six-month delinquency count at +1 [[art:17afb6f9:sign_check.delinq_count_6m.coef_sign]] and +1 [[art:549e904e:sign_check.delinq_count_6m.univariate_direction]].
They likewise coincide on the six-month mean payment ratio at -1 [[art:077bb6b2:sign_check.pay_ratio_mean_6m.coef_sign]] and -1 [[art:24dcef24:sign_check.pay_ratio_mean_6m.univariate_direction]], on the six-month mean bill at -1 [[art:cee1a18f:sign_check.bill_mean_6m.coef_sign]] and -1 [[art:23b89c5d:sign_check.bill_mean_6m.univariate_direction]], on the six-month bill trend at -1 [[art:7fd8474e:sign_check.bill_trend_6m.coef_sign]] and -1 [[art:a9bff389:sign_check.bill_trend_6m.univariate_direction]], and on age at -1 [[art:6172eb93:sign_check.age.coef_sign]] and -1 [[art:66364583:sign_check.age.univariate_direction]].

### What the model actually leans on

The ablation evidence concentrates the model's discrimination in a small part of the design.
Removing the most recent delinquency status changes test AUC by -0.07609 [[art:9bdbb0b5:ablation.delinq_last.delta_auc]], by far the largest loss, and removing utilisation changes it by -0.01974 [[art:c8ce0123:ablation.utilisation.delta_auc]], the next largest.
The six-month mean bill contributes a smaller loss at -0.001513 [[art:0fff644e:ablation.bill_mean_6m.delta_auc]] and age a loss smaller still at -6.124e-05 [[art:fa888618:ablation.age.delta_auc]].
The rest do not carry discrimination in this refit: the six-month bill trend at 0.003776 [[art:80be2a7e:ablation.bill_trend_6m.delta_auc]], the six-month mean payment ratio at 0.007313 [[art:48fca3ba:ablation.pay_ratio_mean_6m.delta_auc]] and the six-month delinquency count at 0.000671 [[art:a35dafd6:ablation.delinq_count_6m.delta_auc]] each improve test AUC when dropped, as do the credit limit, the most recent payment ratio and the six-month maximum delinquency cited above.
That the largest fitted coefficient and the largest ablation loss both fall on the most recent delinquency status is a point in the design's favour, since the model's weight and its measured reliance agree on the driver a credit analyst would name first.
These ablation and sign diagnostics are evidence bearing on the design judgement here, and no rule is evaluated against them in this section.

### Effective challenge

A hist_gradient_boosting challenger was fitted as the benchmark, reaching 0.8346 [[art:d1533f6e:challenger.auc]] on test against the champion's 0.7480 [[art:33170ddf:metrics.test.auc]].
The comparison that decides effective challenge is the difference in test AUC, and that difference is 0.08651 [[art:95cce9d6:challenger.delta_auc]] in the challenger's favour, read against a declared effective-challenge bound on the same difference of 0.03 [[art:e042774c:threshold.E1.delta_auc]].
The challenger's lead is above that bound, and the challenger's Brier score of 0.1214 [[art:e580bfb4:challenger.brier]] is also below the champion's 0.1490 [[art:3be8087d:metrics.test.brier]], so the challenger is the better of the two on both the discrimination and the calibration measure recorded here.
This is a finding, E1, and because a flexible non-linear benchmark opens a gap of this size over the champion's linear-in-the-coefficients specification, it is a finding about the champion's functional form rather than about any single feature; it is reported in the findings section.
The conceptual-soundness judgement follows from that: the design is defensible in its timing, its collinearity screen and the direction of its leading coefficients, but the additive linear form it commits to leaves discrimination on the table that a benchmark of the same inputs recovers.

## 3. Data integrity and drift

Sound development practice includes a critical assessment of data quality, relevance, and inputs, alongside out-of-sample testing [[reg:SR26-2:IV.1]]; this section reads the data checks for this package against the thresholds the package declares.

### 3.1 Coverage and missingness

The training split holds 3545 rows [[art:1ff4e472:profile.train.n]] and the test split holds 1500 rows [[art:2193cf5f:profile.test.n]].
The largest missing fraction in any training column is 0 [[art:050a3099:profile.train.missing.max]].
The largest missing fraction in any test column is likewise 0 [[art:f813848d:profile.test.missing.max]].
Neither split's worst column stands above the other's, and the bound on the missingness gap between splits is 0.1 [[art:9cce25ea:threshold.D1.missing_gap]], which neither of these two maxima approaches.

### 3.2 Population and characteristic stability

The largest train-to-test population stability index, the score included, is 0.01082 [[art:9300bdd4:psi.max]], well below the declared stability bound of 0.25 [[art:278b9016:threshold.S1.psi]], a bound the package restates at 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
The per-feature indices between the training split and the test split are:

- limit_bal at 0.01082 [[art:5db122d3:psi.limit_bal]], the largest of the features;
- bill_trend_6m at 0.009307 [[art:b8409498:psi.bill_trend_6m]];
- age at 0.008244 [[art:54a6d5c8:psi.age]];
- bill_mean_6m at 0.007417 [[art:05ce5247:psi.bill_mean_6m]];
- pay_ratio_mean_6m at 0.005142 [[art:bca4bf06:psi.pay_ratio_mean_6m]];
- delinq_max_6m at 0.004879 [[art:548e3455:psi.delinq_max_6m]];
- utilisation at 0.004511 [[art:21c53bd0:psi.utilisation]];
- pay_ratio_last at 0.004465 [[art:ed34c7dc:psi.pay_ratio_last]];
- delinq_last at 0.002615 [[art:7298b08b:psi.delinq_last]];
- delinq_count_6m at 0.001826 [[art:95ad0bbe:psi.delinq_count_6m]].

The score itself shifts by 0.004938 [[art:63344faa:psi.y_score]] between the two splits, below the largest of the feature shifts.
Every one of these values sits far below the declared bound of 0.25 [[art:278b9016:threshold.S1.psi]], so the test split is drawn from substantially the same population as the training split.

Turning from the marginal distributions to their pull on the linear predictor, the largest characteristic index is 0.02201 [[art:897f0064:csi.max]], carried by delinq_last at 0.02201 [[art:55177f94:csi.delinq_last]].
The remaining contributions are bill_trend_6m at 0.006491 [[art:85619225:csi.bill_trend_6m]], utilisation at 0.004851 [[art:dfb8439b:csi.utilisation]], bill_mean_6m at 0.002641 [[art:9105b83f:csi.bill_mean_6m]], delinq_count_6m at 0.002326 [[art:77a551ed:csi.delinq_count_6m]], pay_ratio_last at 0.002204 [[art:e23fdafd:csi.pay_ratio_last]], pay_ratio_mean_6m at 0.001619 [[art:ed28e38f:csi.pay_ratio_mean_6m]], limit_bal at 0.001136 [[art:f96c2df9:csi.limit_bal]], age at 0.0009881 [[art:76338ca5:csi.age]] and delinq_max_6m at 0.0007952 [[art:e6506c3b:csi.delinq_max_6m]].
The ordering differs from the marginal one: delinq_last moves the predictor most while its marginal shift of 0.002615 [[art:7298b08b:psi.delinq_last]] is among the smaller ones, and limit_bal carries the largest marginal shift at 0.01082 [[art:5db122d3:psi.limit_bal]] while contributing 0.001136 [[art:f96c2df9:csi.limit_bal]] to the predictor.
No characteristic contribution reaches the declared stability bound of 0.25 [[art:278b9016:threshold.S1.psi]].

### 3.3 Leakage screens

The declared-timing screen flags 0 features [[art:742bcd24:leakage.timing.n_flagged]] as measured during the performance period or after the outcome.
The strongest single feature reaches an AUC of 0.6819 [[art:7c15f992:leakage.target_corr.max_single_feature_auc]], below the bound of 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]] that one feature may reach on its own, so no single input behaves like a restatement of the target.
The name screen matches 0 feature names [[art:407e62be:leakage.name_screen.n_matched]] against the target-adjacent lexicon.

The contamination screen has two arms, and each is read against its own bound.
On the identifier arm, the share of test rows whose client identifier also identifies a training row is 0 [[art:63d37fc5:leakage.overlap.ids]], against the declared contamination bound of 0.005 [[art:9f336eaf:threshold.L2.overlap]].
On the feature arm, the share of test rows whose feature values also appear in train is 0.03 [[art:a2cd9767:leakage.overlap]].
That arm is read not against the declared bound but against the bound the rule actually applied, which is the larger of the declared contamination bound and a term derived from the share of training rows whose feature values are not unique within train, the latter being 0 [[art:4474c227:leakage.duplicates.train]].
The applied bound therefore took the value 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]], and the feature-vector overlap of 0.03 [[art:dc2d0a43:leakage.overlap.features]] stands above it.
This is a finding, L2 (contamination), at suggested severity medium.
The two arms point in opposite directions: the identifier arm is at 0 [[art:63d37fc5:leakage.overlap.ids]] while the feature arm is at 0.03 [[art:dc2d0a43:leakage.overlap.features]], so the repeated rows carry identifiers of their own, which is the pattern a re-keyed copy of training data would leave.
Because the within-train duplicate share is 0 [[art:4474c227:leakage.duplicates.train]], the coincidence explanation that would have raised the applied bound does not arise here, and the repeated feature vectors cannot be attributed to two subjects writing the same discrete row.
Test metrics computed on this split should be read with that overlap in mind, since the affected rows are not out-of-sample in the sense the split intends.

## 4. Outcomes analysis

Outcomes analysis compares the model's outputs with the outcomes actually observed, and reads the comparison against the performance thresholds the model owner established [[reg:SR26-2:V.1.b]].

This section reports discrimination first and calibration second.
The reason is the observed event rate on the evaluation split, 0.2247 [[art:9209d200:metrics.test.event_rate]], which sits at or above 0.05 [[art:42f1351e:rule.calibration_first_event_rate]], the event rate below which this report would lead with calibration instead.

The recomputed metrics by split are as follows, one row per metric.

| Metric | Train | Test |
| --- | --- | --- |
| Rows | 3545 [[art:343c4301:metrics.train.n]] | 1500 [[art:64fcf14d:metrics.test.n]] |
| Observed event rate | 0.2245 [[art:cf2ea9d7:metrics.train.event_rate]] | 0.2247 [[art:9209d200:metrics.test.event_rate]] |
| AUC | 0.7589 [[art:92ca327f:metrics.train.auc]] | 0.748 [[art:33170ddf:metrics.test.auc]] |
| Gini | 0.5177 [[art:b7417c30:metrics.train.gini]] | 0.4961 [[art:e7acec22:metrics.test.gini]] |
| KS | 0.4447 [[art:39f29309:metrics.train.ks]] | 0.419 [[art:63623085:metrics.test.ks]] |
| Brier | 0.149 [[art:0215ac1d:metrics.train.brier]] | 0.149 [[art:3be8087d:metrics.test.brier]] |
| Log loss | 0.465 [[art:a9dde81e:metrics.train.logloss]] | 0.4674 [[art:33a9bfcd:metrics.test.logloss]] |
| Mean predicted probability | 0.2246 [[art:233a7dff:metrics.train.mean_predicted]] | 0.2213 [[art:4920f430:metrics.test.mean_predicted]] |

Rank-ordering was also read decile by decile on the evaluation split.

<!-- quaestor:renderer:begin table deciles.test -->
Decile separation on test; decile 1 holds the highest probabilities [[art:93732a5e:deciles.test]]:

| decile | count | events | event_rate | lift |
|---|---|---|---|---|
| 1 | 150 | 87 | 0.58 | 2.582 |
| 2 | 150 | 72 | 0.48 | 2.136 |
| 3 | 150 | 47 | 0.3133 | 1.395 |
| 4 | 150 | 35 | 0.2333 | 1.039 |
| 5 | 150 | 22 | 0.1467 | 0.6528 |
| 6 | 150 | 17 | 0.1133 | 0.5045 |
| 7 | 150 | 17 | 0.1133 | 0.5045 |
| 8 | 150 | 9 | 0.06 | 0.2671 |
| 9 | 150 | 12 | 0.08 | 0.3561 |
| 10 | 150 | 19 | 0.1267 | 0.5638 |
<!-- quaestor:renderer:end -->

The two highest-probability deciles of the evaluation split hold 0.4718 [[art:d4a1cf7d:deciles.test.top2_capture]] of its events, against 0.4485 [[art:15637767:deciles.train.top2_capture]] on the development split, so capture in the top of the ranking is higher on the evaluation split than on the development split.

The train-to-test AUC gap is read against a bound of 0.08 [[art:630f28f4:threshold.O1.auc_gap]].
AUC is 0.7589 [[art:92ca327f:metrics.train.auc]] on the development split and 0.748 [[art:33170ddf:metrics.test.auc]] on the evaluation split, the larger of the two being on the development split.
The largest train-to-test population stability index across the features and the score is 0.01082 [[art:9300bdd4:psi.max]], below the stability bound of 0.25 [[art:278b9016:threshold.S1.psi]].

Calibration on the evaluation split was then examined, decile by decile and in the aggregate.

<!-- quaestor:renderer:begin table calibration.test -->
Calibration by decile of predicted probability on test [[art:851ef21d:calibration.test]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.08175 | 0.1267 | 150 |
| 2 | 0.1067 | 0.08 | 150 |
| 3 | 0.1222 | 0.06 | 150 |
| 4 | 0.1364 | 0.1133 | 150 |
| 5 | 0.1545 | 0.1133 | 150 |
| 6 | 0.174 | 0.1467 | 150 |
| 7 | 0.1985 | 0.2333 | 150 |
| 8 | 0.2496 | 0.3133 | 150 |
| 9 | 0.3815 | 0.48 | 150 |
| 10 | 0.6078 | 0.58 | 150 |
<!-- quaestor:renderer:end -->

The logistic regression of the outcome on the logit of the predicted probability gives a slope of 1.001 [[art:95a66bf5:calibration_slope.test]] on the evaluation split and 1.002 [[art:9f4641a6:calibration_slope.train]] on the development split, both inside a band running from 0.8 [[art:749634ae:threshold.C1.calibration_slope.min]] to 1.2 [[art:b6672579:threshold.C1.calibration_slope.max]].
The intercept of that same regression is 0.02371 [[art:ec6ca742:calibration_intercept.test]] on the evaluation split and 0.001736 [[art:0b1e1ff9:calibration_intercept.train]] on the development split, the smaller of the two being on the development split.
Mean predicted probability on the evaluation split is 0.2213 [[art:4920f430:metrics.test.mean_predicted]] against an observed rate of 0.2247 [[art:9209d200:metrics.test.event_rate]], the prediction being the lower of the two.
Expressed relative to the observed rate, that gap is 0.01499 [[art:02e35a65:calibration.mean_rel_gap.test]] on the evaluation split and 0.000327 [[art:060d5049:calibration.mean_rel_gap.train]] on the development split, both below the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].

The thresholds the developer declared in package.yaml, each with its bound, the value recomputed here and the outcome, are set out below.

<!-- quaestor:renderer:begin table thresholds.evaluation -->
Every threshold package.yaml declares, with its bound, the recomputed value and the outcome [[art:1dbd7569:thresholds.evaluation]]:

| metric | split | bound | value | result |
|---|---|---|---|---|
| auc | test | minimum 0.7 | 0.748 | pass |
| brier | test | maximum 0.2 | 0.149 | pass |
| calibration_slope | test | minimum 0.8 | 1.001 | pass |
| calibration_slope | test | maximum 1.2 | 1.001 | pass |
| psi |  | maximum 0.25 | 0.01082 | pass |
<!-- quaestor:renderer:end -->

The table pairs every declared bound with the recomputed value it was read against and the outcome that comparison produced.
Its entries come from the same recomputation reported above, so the outcomes it records and the figures in this section describe one run.

### Follow-up analyses

The planning loop asked for metrics on the slice `limit_bal <= median(limit_bal)`, because a challenger AUC lead suggested the champion's discrimination might collapse on a sub-population, and the low-limit half is the clean half-and-half slice on which to test that.

<!-- quaestor:renderer:begin table metrics.train.sub.limit_bal_low -->
Every metric on the limit_bal below_median slice of train [[art:b2a797ce:metrics.train.sub.limit_bal_low]]:

| metric | value |
|---|---|
| n | 1783 |
| event_rate | 0.2445 |
| auc | 0.7566 |
| gini | 0.5132 |
| ks | 0.4457 |
| brier | 0.1642 |
| logloss | 0.4994 |
| mean_predicted | 0.2416 |
| mean_rel_gap | 0.01216 |
| share | 0.503 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.limit_bal_low -->
Every metric on the limit_bal below_median slice of test [[art:e46a4670:metrics.test.sub.limit_bal_low]]:

| metric | value |
|---|---|
| n | 756 |
| event_rate | 0.2487 |
| auc | 0.7609 |
| gini | 0.5218 |
| ks | 0.4236 |
| brier | 0.1609 |
| logloss | 0.4941 |
| mean_predicted | 0.2442 |
| mean_rel_gap | 0.01799 |
| share | 0.504 |
<!-- quaestor:renderer:end -->

On the development split this slice's AUC falls 0.002284 [[art:bee2f92d:metrics.train.sub.limit_bal_low.auc_gap]] below the split's own, and on the evaluation split it falls -0.01283 [[art:73357597:metrics.test.sub.limit_bal_low.auc_gap]] below it, both within the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] at which a slice becomes an open item.
The slice holds 0.503 [[art:41a3d52e:metrics.train.sub.limit_bal_low.share]] of the development split and 0.504 [[art:bac689cc:metrics.test.sub.limit_bal_low.share]] of the evaluation split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] a slice must hold before it can raise an open item.
Mean predicted probability on the evaluation split slice is 0.2442 [[art:8308df9e:metrics.test.sub.limit_bal_low.mean_predicted]] against an observed rate of 0.2487 [[art:de78adb5:metrics.test.sub.limit_bal_low.event_rate]], a relative gap of 0.01799 [[art:b07ef9b1:metrics.test.sub.limit_bal_low.mean_rel_gap]] against 0.01216 [[art:dfe3d86c:metrics.train.sub.limit_bal_low.mean_rel_gap]] on the development split, both below the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]], so neither the level of the probabilities nor their ordering shows weakness on this slice.

The loop then asked for metrics on the slice `limit_bal > median(limit_bal)`, to complete the partition so that the low-limit half could be read against its complement rather than only against the whole split.

<!-- quaestor:renderer:begin table metrics.train.sub.limit_bal_high -->
Every metric on the limit_bal above_median slice of train [[art:68a13fc7:metrics.train.sub.limit_bal_high]]:

| metric | value |
|---|---|
| n | 1762 |
| event_rate | 0.2043 |
| auc | 0.7535 |
| gini | 0.5069 |
| ks | 0.4403 |
| brier | 0.1337 |
| logloss | 0.4303 |
| mean_predicted | 0.2075 |
| mean_rel_gap | 0.01545 |
| share | 0.497 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.limit_bal_high -->
Every metric on the limit_bal above_median slice of test [[art:23e111d4:metrics.test.sub.limit_bal_high]]:

| metric | value |
|---|---|
| n | 744 |
| event_rate | 0.2003 |
| auc | 0.7201 |
| gini | 0.4402 |
| ks | 0.4157 |
| brier | 0.1369 |
| logloss | 0.4402 |
| mean_predicted | 0.198 |
| mean_rel_gap | 0.0112 |
| share | 0.496 |
<!-- quaestor:renderer:end -->

This slice's AUC falls 0.005408 [[art:4f0231ad:metrics.train.sub.limit_bal_high.auc_gap]] below the development split's own and 0.02796 [[art:677dd01a:metrics.test.sub.limit_bal_high.auc_gap]] below the evaluation split's own, both within the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].
It holds 0.497 [[art:63a6b099:metrics.train.sub.limit_bal_high.share]] of the development split and 0.496 [[art:ac383ccb:metrics.test.sub.limit_bal_high.share]] of the evaluation split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].
Mean predicted probability on the evaluation split slice is 0.198 [[art:43036bf7:metrics.test.sub.limit_bal_high.mean_predicted]] against an observed rate of 0.2003 [[art:5e9aab40:metrics.test.sub.limit_bal_high.event_rate]], a relative gap of 0.0112 [[art:c0862d76:metrics.test.sub.limit_bal_high.mean_rel_gap]] against 0.01545 [[art:64fe2acf:metrics.train.sub.limit_bal_high.mean_rel_gap]] on the development split, both below the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]], so on this slice the level of the probabilities tracks the observed rate and the ordering holds within its bound.

The loop next asked for metrics on the slice `delinq_count_6m > median(delinq_count_6m)`, because the limit halves showed nothing and the delinquency-history segment is where a linear champion is likeliest to misfit and so to give up ground to the challenger.

<!-- quaestor:renderer:begin table metrics.train.sub.delinq_count_6m_high -->
Every metric on the delinq_count_6m above_median slice of train [[art:19032a97:metrics.train.sub.delinq_count_6m_high]]:

| metric | value |
|---|---|
| n | 1335 |
| event_rate | 0.3169 |
| auc | 0.7448 |
| gini | 0.4897 |
| ks | 0.4047 |
| brier | 0.1861 |
| logloss | 0.5503 |
| mean_predicted | 0.3186 |
| mean_rel_gap | 0.00564 |
| share | 0.3766 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.delinq_count_6m_high -->
Every metric on the delinq_count_6m above_median slice of test [[art:d7849ad5:metrics.test.sub.delinq_count_6m_high]]:

| metric | value |
|---|---|
| n | 550 |
| event_rate | 0.3455 |
| auc | 0.7499 |
| gini | 0.4998 |
| ks | 0.4292 |
| brier | 0.1934 |
| logloss | 0.5685 |
| mean_predicted | 0.3202 |
| mean_rel_gap | 0.07308 |
| share | 0.3667 |
<!-- quaestor:renderer:end -->

This slice's AUC falls 0.01403 [[art:253a83c0:metrics.train.sub.delinq_count_6m_high.auc_gap]] below the development split's own and -0.001865 [[art:49275c9b:metrics.test.sub.delinq_count_6m_high.auc_gap]] below the evaluation split's own, both within the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].
It holds 0.3766 [[art:ef2e70bf:metrics.train.sub.delinq_count_6m_high.share]] of the development split and 0.3667 [[art:22847310:metrics.test.sub.delinq_count_6m_high.share]] of the evaluation split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].
Mean predicted probability on the evaluation split slice is 0.3202 [[art:5c3b7d30:metrics.test.sub.delinq_count_6m_high.mean_predicted]] against an observed rate of 0.3455 [[art:ef17c303:metrics.test.sub.delinq_count_6m_high.event_rate]], the prediction being the lower of the two, and the gap relative to the observed rate is 0.07308 [[art:7f0a352c:metrics.test.sub.delinq_count_6m_high.mean_rel_gap]] against 0.00564 [[art:b1995733:metrics.train.sub.delinq_count_6m_high.mean_rel_gap]] on the development split, both below the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
Read on that relative comparison, this slice carries the larger shortfall in the level of the probabilities of the two delinquency halves on the evaluation split, while its ordering stays within its own bound.

The loop finally asked for metrics on the slice `delinq_count_6m <= median(delinq_count_6m)`, to complete the delinquency partition and show whether the champion's shortfall behind the challenger sits in the low-delinquency majority or in the high-delinquency tail.

<!-- quaestor:renderer:begin table metrics.train.sub.delinq_count_6m_low -->
Every metric on the delinq_count_6m below_median slice of train [[art:c74040cc:metrics.train.sub.delinq_count_6m_low]]:

| metric | value |
|---|---|
| n | 2210 |
| event_rate | 0.1688 |
| auc | 0.7226 |
| gini | 0.4452 |
| ks | 0.3788 |
| brier | 0.1267 |
| logloss | 0.4135 |
| mean_predicted | 0.1678 |
| mean_rel_gap | 0.005699 |
| share | 0.6234 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.delinq_count_6m_low -->
Every metric on the delinq_count_6m below_median slice of test [[art:4808d857:metrics.test.sub.delinq_count_6m_low]]:

| metric | value |
|---|---|
| n | 950 |
| event_rate | 0.1547 |
| auc | 0.6597 |
| gini | 0.3194 |
| ks | 0.2857 |
| brier | 0.1232 |
| logloss | 0.4089 |
| mean_predicted | 0.164 |
| mean_rel_gap | 0.0601 |
| share | 0.6333 |
<!-- quaestor:renderer:end -->

On the development split this slice's AUC falls 0.03626 [[art:b720a1d0:metrics.train.sub.delinq_count_6m_low.auc_gap]] below the split's own, within the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].
On the evaluation split it falls 0.08836 [[art:9b3b5b67:metrics.test.sub.delinq_count_6m_low.auc_gap]] below the split's own, above that same bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]], with slice AUC at 0.6597 [[art:2dd8f8e5:metrics.test.sub.delinq_count_6m_low.auc]] against 0.748 [[art:33170ddf:metrics.test.auc]] on the whole split.
The slice holds 0.6234 [[art:3501db92:metrics.train.sub.delinq_count_6m_low.share]] of the development split and 0.6333 [[art:3257b2f3:metrics.test.sub.delinq_count_6m_low.share]] of the evaluation split, well above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]], so the weaker ranking sits on the majority of the split rather than on a thin corner of it.
Mean predicted probability on the evaluation split slice is 0.164 [[art:642f1e64:metrics.test.sub.delinq_count_6m_low.mean_predicted]] against an observed rate of 0.1547 [[art:9690f94d:metrics.test.sub.delinq_count_6m_low.event_rate]], a relative gap of 0.0601 [[art:b51086d6:metrics.test.sub.delinq_count_6m_low.mean_rel_gap]] against 0.005699 [[art:238a7795:metrics.train.sub.delinq_count_6m_low.mean_rel_gap]] on the development split, both below the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
Since the level of the probabilities stays within its tolerance while the AUC shortfall exceeds its bound, the weakness on this slice is in the ordering of the probabilities rather than in their level, and it is carried to the open items of this report as a question for the model developer.

## 5. Sensitivity and scenario analysis

Sensitivity work in this section follows the guidance's expectation that key assumptions and the choice of variables be subjected to critical analysis, with attention to their impact on model outputs and to any potential limitations [[reg:SR26-2:V.1.a]].
The narrower expectation that validation check the effect of small changes in inputs and parameter values, and extend testing toward extreme values to establish where a model becomes unstable, is stated in the superseded guidance and is the frame used for the scenario work described below [[reg:SR11-7:V.1.a]].

### Multicollinearity among the retained features

The largest variance inflation factor across the retained features is 7.31 [[art:d8e9619c:vif.max]], below the declared ceiling of 10 [[art:aeb4f33c:threshold.M1.vif]].
That maximum is attained on the six-month mean bill amount, at 7.31 [[art:1915242e:vif.bill_mean_6m]].
Close beneath it sit the most recent payment ratio at 7.286 [[art:e30c6fbd:vif.pay_ratio_last]] and the six-month mean payment ratio at 7.28 [[art:4d1589cd:vif.pay_ratio_mean_6m]], a clustering consistent with the two payment-ratio features carrying substantially overlapping information.
The credit limit follows at 4.82 [[art:eeeb5c27:vif.limit_bal]], and utilisation at 3.215 [[art:7298e587:vif.utilisation]].
The delinquency block sits lower: 2.567 [[art:ca9bf9ad:vif.delinq_count_6m]] for the six-month count, 2.403 [[art:95ebdd8f:vif.delinq_max_6m]] for the six-month maximum, and 1.414 [[art:a561c855:vif.delinq_last]] for the most recent value.
The six-month bill trend at 1.201 [[art:78a03a7b:vif.bill_trend_6m]] and age at 1.002 [[art:628d9c69:vif.age]] are the least entangled of the retained features, with age close to orthogonal to the remainder of the design.
No retained feature reaches the declared ceiling, so on this diagnostic the design does not require a feature to be dropped or combined.

The condition number of the column-standardised design is 5.557 [[art:8029574b:condition_number]], well below the declared limit of 30 [[art:7e52fd7a:threshold.M1.condition_number]].
The two diagnostics point the same way: the strongest single-feature inflation stays under its ceiling, and the design taken as a whole stays far from the ill-conditioning limit, so coefficient estimates are not expected to be unstable on account of collinearity.
The residual caution is qualitative rather than numeric: the bill-level and payment-ratio features are the most mutually explained of the retained set, and any future addition of a further balance- or payment-derived feature should be re-checked against both diagnostics before it is retained.

### Checks out of scope for this model type

Stability across declared regimes is not in scope for this subject, which is not partitioned by a regime column, and the carve-out is recorded in Appendix D.
The rate-shock scenarios — the value change at the extreme shocks, whether the shocked curve is monotone, and the convexity of that curve against the direction the package declares — are exercises for a hazard model, and the subject of this report is not one; that carve-out is likewise recorded in Appendix D.
Neither exercise was performed for this model package, and nothing in this section should be read as reporting a regime comparison or a shocked valuation.

On the sensitivity evidence in scope, the retained design is well conditioned against both declared limits, and this section raises no issue for escalation.

## 6. Findings and recommendations

Findings are ordered by severity, medium before low, and each carries the recomputed artifacts the check fired on together with the bound it was read against, in keeping with validation that identifies model limitations and errors and clarifies whether corrective actions may be warranted [[reg:SR26-2:V]].

### F-001 · L2 contamination · severity **medium**

**Rows of the test split repeat feature vectors of the training split while carrying identifiers of their own, so the test split is contaminated.**

The share of test rows whose feature values also appear in train is 0.03 [[art:dc2d0a43:leakage.overlap.features]], above the bound the rule applied of 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].

That applied bound sits at the declared contamination threshold of 0.005 [[art:9f336eaf:threshold.L2.overlap]], because the share of train rows whose feature values are not unique within train is 0 [[art:4474c227:leakage.duplicates.train]].

The validator concludes that repetition inside the training split does not account for the overlap, so the recomputed test metrics are measured in part on rows the model has already seen and overstate held-out performance by an amount this validation cannot bound.

The developer should trace how the repeated feature vectors came to carry distinct identifiers, rebuild the splits so that no test row reproduces a training feature vector, and re-report test performance on the rebuilt split before the model is relied on.

### F-002 · E1 effective challenge · severity **low**

**A gradient-boosting challenger outperforms the champion on test by a margin past the effective-challenge threshold.**

The challenger reaches an AUC on test of 0.8346 [[art:d1533f6e:challenger.auc]], against the champion's 0.748 [[art:33170ddf:metrics.test.auc]].

The challenger's lead over the champion is 0.08651 [[art:95cce9d6:challenger.delta_auc]], above the effective-challenge threshold of 0.03 [[art:e042774c:threshold.E1.delta_auc]].

The validator concludes that signal available in the same features is not captured by the champion's functional form, and notes that both AUCs were computed on the split addressed in F-001, so the comparison should be repeated once that split is rebuilt.

The developer should document the rationale for retaining the champion over a better-performing alternative, or adopt the alternative, and record that rationale where recommendations, responses, and exceptions are tracked [[reg:SR26-2:VI.3]].

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1, S1), `compute_metrics` (T1, C1, O1), `check_leakage` (L1), `check_collinearity` (M1).

### Open items

On the segment `delinq_count_6m <= median(delinq_count_6m)`, which holds 0.6333 [[art:3257b2f3:metrics.test.sub.delinq_count_6m_low.share]] of the test split and so sits at or above the minimum share of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]], AUC is 0.6597 [[art:2dd8f8e5:metrics.test.sub.delinq_count_6m_low.auc]] against 0.748 [[art:33170ddf:metrics.test.auc]] on the whole split, a difference rather than a ratio of 0.08836 [[art:9b3b5b67:metrics.test.sub.delinq_count_6m_low.auc_gap]] read against a bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] — since selecting on a delinquency count also selects a near-constant delinquency history, what does the model developer expect the model to discriminate on inside that segment?

Can the model developer account for the fitted coefficient on `delinq_max_6m` carrying sign -1 [[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]] where the direction it was read against, that feature's own univariate direction, is 1 [[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]] and agreement is recorded as 0 [[art:c946359c:sign_check.delinq_max_6m.agrees]], given that a fitted coefficient conditions on everything correlated with the feature and not on the feature alone?

Can the model developer account for the fitted coefficient on `limit_bal` carrying sign 1 [[art:6af6aef2:sign_check.limit_bal.coef_sign]] where the direction it was read against, that feature's own univariate direction, is -1 [[art:56d284d6:sign_check.limit_bal.univariate_direction]] and agreement is recorded as 0 [[art:0278aad1:sign_check.limit_bal.agrees]], and say which correlated quantities the fitted sign is holding fixed?

Can the model developer account for the fitted coefficient on `pay_ratio_last` carrying sign 1 [[art:f018263e:sign_check.pay_ratio_last.coef_sign]] where the direction it was read against, that feature's own univariate direction, is -1 [[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]] and agreement is recorded as 0 [[art:79abee77:sign_check.pay_ratio_last.agrees]], and state whether that conditional direction is the one the business intends?

## 7. Ongoing monitoring recommendations

Ongoing monitoring should evaluate the extent to which this model continues to perform as expected given changes in products, exposures, activities, clients, data relevance, or market conditions, with the frequency and scope of monitoring reports set by the nature and materiality of the model [[reg:SR26-2:V.2]].

The quantities recommended below are the ones this validation recomputed, compared against the same declared bounds, so that a monitoring report and this report can be read against each other without introducing new acceptance levels.

### Quantities, cadence, and bound

- Rank-ordering: track discrimination on each production cohort against the declared floor of 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]], whose value on the evaluation split in this validation was 0.748 [[art:33170ddf:metrics.test.auc]], computed monthly as outcome windows mature and reported quarterly.
- Probability accuracy: track the mean squared error of the predicted probabilities against the declared ceiling of 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]], whose validation value was 0.149 [[art:3be8087d:metrics.test.brier]], on the same quarterly report.
- Calibration: track the slope of the logistic regression of the realised outcome on the log-odds of the score against the declared band running from 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] to 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]], whose validation value was 1.001 [[art:95a66bf5:calibration_slope.test]], quarterly and after any recalibration.
- Population stability: recompute the largest shift across the model inputs and the score itself, development vintage to production vintage, against the declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]], where the train-to-test value in this validation was 0.01082 [[art:9300bdd4:psi.max]]; this is cheap enough to run monthly and is the earliest of the recommended signals, since it does not wait on outcomes.
- Sub-population performance: track discrimination and calibration for the reported sub-populations on the quarterly cadence, and when a shortfall is compared across two sub-populations, state explicitly whether the comparison is of the difference between their gaps or of the ratio, because two populations whose absolute gaps agree can have ratios that do not.

### Ordering of the monitoring report

Section 4 of this report reported discrimination before calibration, because the observed event rate on the evaluation split is at or above 0.05 [[art:42f1351e:rule.calibration_first_event_rate]].

If a future cohort's observed event rate falls below 0.05 [[art:42f1351e:rule.calibration_first_event_rate]], the monitoring report for that cohort should lead with calibration and read discrimination after it, since rank-ordering measured on a sparse-event cohort is the less stable of the two readings.

### Benchmarking that monitoring adds

Section 2 compares the champion with a challenger fit on the development data, and monitoring should add the comparison that development data cannot give: the same challenger specification refitted on successive production vintages, scored on those vintages' realised outcomes alongside the champion.

Run that parallel comparison on each refit cycle, and treat a persistent advantage to the refitted challenger as evidence about the champion's aging rather than as an immediate replacement decision.

Discrepancies between the champion and the benchmark should trigger investigation into the source and degree of the difference, and a close match should be read with caution rather than as confirmation, because the benchmark is itself only an alternative prediction [[reg:SR11-7:V.1.b]].

### What this validation could not cover

This validation observed the model on a fixed evaluation split, so it cannot speak to how the score behaves across successive production vintages, and trend analysis of the tracked quantities over time is what monitoring must supply in its place.

Outcome labels mature only after scores are issued, so early production cohorts should be watched with early-warning quantities and then back-tested once the performance window closes, with the back-test observation frequency matched to that window [[reg:SR26-2:V.1.b]].

Process verification belongs to the ongoing program and should be reported on the same cadence: that inputs remain accurate, complete, and consistent with the model's design, that code changes are controlled, logged, and auditable, and that overrides are tracked and their performance analysed [[reg:SR11-7:V.1.b]].

A sustained or rising override rate, or an override process that consistently improves on the score, should be escalated as a signal about the model rather than absorbed into business-as-usual reporting [[reg:SR11-7:V.1.b]].

The robustness and sensitivity checks performed here should be repeated periodically, and the input ranges over which the model was exercised should be monitored so that cohorts approaching or exceeding those ranges are identified when they arise rather than after the fact.

### Escalation

When any tracked quantity moves outside its declared bound, or drifts persistently toward it across consecutive reports, the response should be considered under the organisation's model risk policy as an overlay, an adjustment, a recalibration, or redevelopment [[reg:SR26-2:V.2]].

Revalidation should be scheduled periodically and triggered earlier by a breach of any declared bound, by material change in products, exposures, or client mix, or by a change in model structure or technique [[reg:SR26-2:V]].

## Appendix A — Claims

Grounding precision 1.0000 before repair (263 of 263 claims verified) and 1.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 14/14; conceptual_soundness 70/70; data_integrity 48/48; outcomes 83/83; sensitivity 14/14; findings 23/23; monitoring 11/11.

Developer claims: The package declares 2 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). See Appendix D.

Excluded numeric tokens (not claims): section_number (3.1, 3.2, 3.3, Section 4); citation_hash (2ad8d1a5, 1ff4e472, 2193cf5f, 33170ddf); regulatory_section_id (SR26-2:V, SR26-2:V.1.b, SR26-2:V.1.a, SR26-2:IV.1); finding_id (F-001, F-002); package_version (1.0); extractor_returned_excluded_token (1.0, 26.0, 2, 6.0).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The subject was run end to end by the validation harness und… | 300 | count | max_seconds |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 2 | summary | The fitting split holds 3545 rows and the held-out split hol… | 3545 | count | n | train | eq | `[[art:1ff4e472:profile.train.n]]` | verified | 3545 |
| 3 | summary | The fitting split holds 3545 rows and the held-out split hol… | 1500 | count | n | test | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 4 | summary | Discrimination reaches 0.748 , above the declared floor of 0… | 0.748 | ratio | auc | test | eq | `[[art:33170ddf:metrics.test.auc]]` | verified | 0.748047488 |
| 5 | summary | Discrimination reaches 0.748 , above the declared floor of 0… | 0.7 | ratio | auc | test | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 6 | summary | The Brier score is 0.149 , below the declared ceiling of 0.2… | 0.149 | ratio | brier | test | eq | `[[art:3be8087d:metrics.test.brier]]` | verified | 0.1489501682 |
| 7 | summary | The Brier score is 0.149 , below the declared ceiling of 0.2… | 0.2 | ratio | brier | test | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 8 | summary | The calibration slope of the outcome on the logit of the pre… | 1.001 | ratio | calibration_slope | test | eq | `[[art:95a66bf5:calibration_slope.test]]` | verified | 1.000821291 |
| 9 | summary | The calibration slope of the outcome on the logit of the pre… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 10 | summary | The calibration slope of the outcome on the logit of the pre… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 11 | summary | The largest population stability index measured from the fit… | 0.01082 | ratio | psi |  | eq | `[[art:9300bdd4:psi.max]]` | verified | 0.01081685833 |
| 12 | summary | The largest population stability index measured from the fit… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 13 | summary | Discrimination on the held-out split, at 0.748 , sits below… | 0.748 | ratio | auc | test | eq | `[[art:33170ddf:metrics.test.auc]]` | verified | 0.748047488 |
| 14 | summary | Discrimination on the held-out split, at 0.748 , sits below… | 0.7589 | ratio | auc | train | eq | `[[art:92ca327f:metrics.train.auc]]` | verified | 0.7588597772 |
| 15 | conceptual_soundness | The champion is a linear scoring form with one coefficient p… | -1.397 | ratio | intercept |  | eq | `[[art:259cdde6:run.model_summary#intercept]]` | verified | -1.396773245 |
| 16 | conceptual_soundness | The champion is a linear scoring form with one coefficient p… | 3545 | count | n_train | train | eq | `[[art:259cdde6:run.model_summary#n_train]]` | verified | 3545 |
| 17 | conceptual_soundness | The champion is a linear scoring form with one coefficient p… | 0.748 | ratio | auc | test | eq | `[[art:33170ddf:metrics.test.auc]]` | verified | 0.748047488 |
| 18 | conceptual_soundness | The champion is a linear scoring form with one coefficient p… | 0.149 | ratio | brier | test | eq | `[[art:3be8087d:metrics.test.brier]]` | verified | 0.1489501682 |
| 19 | conceptual_soundness | The feature inventory the subject declares holds 12 features… | 12 | count | n |  | eq | `[[art:abbb748e:run.features#n]]` | verified | 12 |
| 20 | conceptual_soundness | Of those, 2 are known at origination and 10 are known before… | 2 | count | at_origination |  | eq | `[[art:abbb748e:run.features#at_origination]]` | verified | 2 |
| 21 | conceptual_soundness | Of those, 2 are known at origination and 10 are known before… | 10 | count | before_period_start |  | eq | `[[art:abbb748e:run.features#before_period_start]]` | verified | 10 |
| 22 | conceptual_soundness | None are observed during the performance period, at 0 , and… | 0 | count | during_period |  | eq | `[[art:abbb748e:run.features#during_period]]` | verified | 0 |
| 23 | conceptual_soundness | None are observed during the performance period, at 0 , and… | 0 | count | after_outcome |  | eq | `[[art:abbb748e:run.features#after_outcome]]` | verified | 0 |
| 24 | conceptual_soundness | The developer's own screen dropped two candidate features fo… | 10 | ratio | vif_threshold |  | eq | `[[art:259cdde6:run.model_summary#vif_threshold]]` | verified | 10 |
| 25 | conceptual_soundness | The last bill amount was removed at a variance inflation fac… | 161.1 | ratio | vif |  | eq | `[[art:259cdde6:run.model_summary#removed.bill_last.vif]]` | verified | 161.126489 |
| 26 | conceptual_soundness | The six-month mean utilisation was removed at 36.45 , also a… | 36.45 | ratio | vif |  | eq | `[[art:259cdde6:run.model_summary#removed.utilisation_mean_6m.vif]]` | verified | 36.450766 |
| 27 | conceptual_soundness | The largest coefficient in the fitted model is on the most r… | 0.7279 | ratio | coefficient |  | eq | `[[art:259cdde6:run.model_summary#coefficients.delinq_last.value]]` | verified | 0.7278908925 |
| 28 | conceptual_soundness | The next largest in magnitude are the six-month mean payment… | -0.3768 | ratio | coefficient |  | eq | `[[art:259cdde6:run.model_summary#coefficients.pay_ratio_mean_6m.value]]` | verified | -0.3767989079 |
| 29 | conceptual_soundness | The next largest in magnitude are the six-month mean payment… | -0.3703 | ratio | coefficient |  | eq | `[[art:259cdde6:run.model_summary#coefficients.bill_mean_6m.value]]` | verified | -0.3703441056 |
| 30 | conceptual_soundness | Utilisation carries 0.2700 , positive and consistent with th… | 0.27 | ratio | coefficient |  | eq | `[[art:259cdde6:run.model_summary#coefficients.utilisation.value]]` | verified | 0.2699882382 |
| 31 | conceptual_soundness | Utilisation carries 0.2700 , positive and consistent with th… | -0.2243 | ratio | coefficient |  | eq | `[[art:259cdde6:run.model_summary#coefficients.bill_trend_6m.value]]` | verified | -0.2243370232 |
| 32 | conceptual_soundness | Age carries -0.06933 , the direction conventionally expected… | -0.06933 | ratio | coefficient |  | eq | `[[art:259cdde6:run.model_summary#coefficients.age.value]]` | verified | -0.06932783634 |
| 33 | conceptual_soundness | Age carries -0.06933 , the direction conventionally expected… | 0.1244 | ratio | coefficient |  | eq | `[[art:259cdde6:run.model_summary#coefficients.delinq_count_6m.value]]` | verified | 0.1243857453 |
| 34 | conceptual_soundness | Two coefficients run against what the subject matter would p… | 0.07419 | ratio | coefficient |  | eq | `[[art:259cdde6:run.model_summary#coefficients.limit_bal.value]]` | verified | 0.0741919533 |
| 35 | conceptual_soundness | Two coefficients run against what the subject matter would p… | 0.118 | ratio | coefficient |  | eq | `[[art:259cdde6:run.model_summary#coefficients.pay_ratio_last.value]]` | verified | 0.1179582832 |
| 36 | conceptual_soundness | The six-month maximum delinquency carries -0.03047 , negativ… | -0.03047 | ratio | coefficient |  | eq | `[[art:259cdde6:run.model_summary#coefficients.delinq_max_6m.value]]` | verified | -0.03047140858 |
| 37 | conceptual_soundness | The sign diagnostic counts 3 retained features whose fitted… | 3 | count | n_disagreements | train | eq | `[[art:e223cd4a:sign_check.n_disagreements]]` | verified | 3 |
| 38 | conceptual_soundness | Each ablation delta below is measured from a refit of the ch… | 0.748 | ratio | baseline_auc | test | eq | `[[art:818e6d21:ablation.baseline_auc]]` | verified | 0.748047488 |
| 39 | conceptual_soundness | The credit limit is one of the three: its fitted sign is +1… | 1 | ratio | coef_sign |  | eq | `[[art:6af6aef2:sign_check.limit_bal.coef_sign]]` | verified | 1 |
| 40 | conceptual_soundness | The credit limit is one of the three: its fitted sign is +1… | -1 | ratio | univariate_direction |  | eq | `[[art:56d284d6:sign_check.limit_bal.univariate_direction]]` | verified | -1 |
| 41 | conceptual_soundness | The credit limit is one of the three: its fitted sign is +1… | 0 | ratio | agrees |  | eq | `[[art:0278aad1:sign_check.limit_bal.agrees]]` | verified | 0 |
| 42 | conceptual_soundness | Refitting without the credit limit changes test AUC by 0.000… | 0.0004695 | ratio | delta_auc | test | eq | `[[art:d47e9a58:ablation.limit_bal.delta_auc]]` | verified | 0.0004694703915 |
| 43 | conceptual_soundness | The most recent payment ratio is the second: its fitted sign… | 1 | ratio | coef_sign |  | eq | `[[art:f018263e:sign_check.pay_ratio_last.coef_sign]]` | verified | 1 |
| 44 | conceptual_soundness | The most recent payment ratio is the second: its fitted sign… | -1 | ratio | univariate_direction |  | eq | `[[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]]` | verified | -1 |
| 45 | conceptual_soundness | The most recent payment ratio is the second: its fitted sign… | 0 | ratio | agrees |  | eq | `[[art:79abee77:sign_check.pay_ratio_last.agrees]]` | verified | 0 |
| 46 | conceptual_soundness | Refitting without it changes test AUC by 0.002847 , again an… | 0.002847 | ratio | delta_auc | test | eq | `[[art:1918798e:ablation.pay_ratio_last.delta_auc]]` | verified | 0.002847439983 |
| 47 | conceptual_soundness | The six-month maximum delinquency is the third: its fitted s… | -1 | ratio | coef_sign |  | eq | `[[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]]` | verified | -1 |
| 48 | conceptual_soundness | The six-month maximum delinquency is the third: its fitted s… | 1 | ratio | univariate_direction |  | eq | `[[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]]` | verified | 1 |
| 49 | conceptual_soundness | The six-month maximum delinquency is the third: its fitted s… | 0 | ratio | agrees |  | eq | `[[art:c946359c:sign_check.delinq_max_6m.agrees]]` | verified | 0 |
| 50 | conceptual_soundness | Refitting without it changes test AUC by 0.000296 , the smal… | 0.000296 | ratio | delta_auc | test | eq | `[[art:975f1df6:ablation.delinq_max_6m.delta_auc]]` | verified | 0.0002959704642 |
| 51 | conceptual_soundness | The remaining features agree: the most recent delinquency st… | 1 | ratio | agrees |  | eq | `[[art:a8ba9372:sign_check.delinq_last.agrees]]` | verified | 1 |
| 52 | conceptual_soundness | The remaining features agree: the most recent delinquency st… | 1 | ratio | agrees |  | eq | `[[art:d0c9a130:sign_check.utilisation.agrees]]` | verified | 1 |
| 53 | conceptual_soundness | The remaining features agree: the most recent delinquency st… | 1 | ratio | agrees |  | eq | `[[art:a337d16b:sign_check.delinq_count_6m.agrees]]` | verified | 1 |
| 54 | conceptual_soundness | The remaining features agree: the most recent delinquency st… | 1 | ratio | agrees |  | eq | `[[art:7e9a76ca:sign_check.pay_ratio_mean_6m.agrees]]` | verified | 1 |
| 55 | conceptual_soundness | The remaining features agree: the most recent delinquency st… | 1 | ratio | agrees |  | eq | `[[art:89279c3b:sign_check.bill_mean_6m.agrees]]` | verified | 1 |
| 56 | conceptual_soundness | The remaining features agree: the most recent delinquency st… | 1 | ratio | agrees |  | eq | `[[art:ff3cb24a:sign_check.bill_trend_6m.agrees]]` | verified | 1 |
| 57 | conceptual_soundness | The remaining features agree: the most recent delinquency st… | 1 | ratio | agrees |  | eq | `[[art:4116add1:sign_check.age.agrees]]` | verified | 1 |
| 58 | conceptual_soundness | The fitted and univariate signs coincide on the most recent… | 1 | ratio | coef_sign |  | eq | `[[art:50d352f8:sign_check.delinq_last.coef_sign]]` | verified | 1 |
| 59 | conceptual_soundness | The fitted and univariate signs coincide on the most recent… | 1 | ratio | univariate_direction |  | eq | `[[art:a78648ba:sign_check.delinq_last.univariate_direction]]` | verified | 1 |
| 60 | conceptual_soundness | The fitted and univariate signs coincide on the most recent… | 1 | ratio | coef_sign |  | eq | `[[art:85badc3c:sign_check.utilisation.coef_sign]]` | verified | 1 |
| 61 | conceptual_soundness | The fitted and univariate signs coincide on the most recent… | 1 | ratio | univariate_direction |  | eq | `[[art:f0995196:sign_check.utilisation.univariate_direction]]` | verified | 1 |
| 62 | conceptual_soundness | The fitted and univariate signs coincide on the most recent… | 1 | ratio | coef_sign |  | eq | `[[art:17afb6f9:sign_check.delinq_count_6m.coef_sign]]` | verified | 1 |
| 63 | conceptual_soundness | The fitted and univariate signs coincide on the most recent… | 1 | ratio | univariate_direction |  | eq | `[[art:549e904e:sign_check.delinq_count_6m.univariate_direction]]` | verified | 1 |
| 64 | conceptual_soundness | They likewise coincide on the six-month mean payment ratio a… | -1 | ratio | coef_sign |  | eq | `[[art:077bb6b2:sign_check.pay_ratio_mean_6m.coef_sign]]` | verified | -1 |
| 65 | conceptual_soundness | They likewise coincide on the six-month mean payment ratio a… | -1 | ratio | univariate_direction |  | eq | `[[art:24dcef24:sign_check.pay_ratio_mean_6m.univariate_direction]]` | verified | -1 |
| 66 | conceptual_soundness | They likewise coincide on the six-month mean payment ratio a… | -1 | ratio | coef_sign |  | eq | `[[art:cee1a18f:sign_check.bill_mean_6m.coef_sign]]` | verified | -1 |
| 67 | conceptual_soundness | They likewise coincide on the six-month mean payment ratio a… | -1 | ratio | univariate_direction |  | eq | `[[art:23b89c5d:sign_check.bill_mean_6m.univariate_direction]]` | verified | -1 |
| 68 | conceptual_soundness | They likewise coincide on the six-month mean payment ratio a… | -1 | ratio | coef_sign |  | eq | `[[art:7fd8474e:sign_check.bill_trend_6m.coef_sign]]` | verified | -1 |
| 69 | conceptual_soundness | They likewise coincide on the six-month mean payment ratio a… | -1 | ratio | univariate_direction |  | eq | `[[art:a9bff389:sign_check.bill_trend_6m.univariate_direction]]` | verified | -1 |
| 70 | conceptual_soundness | They likewise coincide on the six-month mean payment ratio a… | -1 | ratio | coef_sign |  | eq | `[[art:6172eb93:sign_check.age.coef_sign]]` | verified | -1 |
| 71 | conceptual_soundness | They likewise coincide on the six-month mean payment ratio a… | -1 | ratio | univariate_direction |  | eq | `[[art:66364583:sign_check.age.univariate_direction]]` | verified | -1 |
| 72 | conceptual_soundness | Removing the most recent delinquency status changes test AUC… | -0.07609 | ratio | delta_auc | test | eq | `[[art:9bdbb0b5:ablation.delinq_last.delta_auc]]` | verified | -0.07608737252 |
| 73 | conceptual_soundness | Removing the most recent delinquency status changes test AUC… | -0.01974 | ratio | delta_auc | test | eq | `[[art:c8ce0123:ablation.utilisation.delta_auc]]` | verified | -0.01973561673 |
| 74 | conceptual_soundness | The six-month mean bill contributes a smaller loss at -0.001… | -0.001513 | ratio | delta_auc | test | eq | `[[art:0fff644e:ablation.bill_mean_6m.delta_auc]]` | verified | -0.001513021425 |
| 75 | conceptual_soundness | The six-month mean bill contributes a smaller loss at -0.001… | -6.124e-05 | ratio | delta_auc | test | eq | `[[art:fa888618:ablation.age.delta_auc]]` | verified | -6.123526845e-05 |
| 76 | conceptual_soundness | The rest do not carry discrimination in this refit: the six-… | 0.003776 | ratio | delta_auc | test | eq | `[[art:80be2a7e:ablation.bill_trend_6m.delta_auc]]` | verified | 0.003776174888 |
| 77 | conceptual_soundness | The rest do not carry discrimination in this refit: the six-… | 0.007313 | ratio | delta_auc | test | eq | `[[art:48fca3ba:ablation.pay_ratio_mean_6m.delta_auc]]` | verified | 0.007312511641 |
| 78 | conceptual_soundness | The rest do not carry discrimination in this refit: the six-… | 0.000671 | ratio | delta_auc | test | eq | `[[art:a35dafd6:ablation.delinq_count_6m.delta_auc]]` | verified | 0.0006710364835 |
| 79 | conceptual_soundness | A hist_gradient_boosting challenger was fitted as the benchm… | 0.8346 | ratio | auc | test | eq | `[[art:d1533f6e:challenger.auc]]` | verified | 0.8345601649 |
| 80 | conceptual_soundness | A hist_gradient_boosting challenger was fitted as the benchm… | 0.748 | ratio | auc | test | eq | `[[art:33170ddf:metrics.test.auc]]` | verified | 0.748047488 |
| 81 | conceptual_soundness | The comparison that decides effective challenge is the diffe… | 0.08651 | ratio | delta_auc | test | eq | `[[art:95cce9d6:challenger.delta_auc]]` | verified | 0.08651267698 |
| 82 | conceptual_soundness | The comparison that decides effective challenge is the diffe… | 0.03 | ratio | delta_auc | test | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 83 | conceptual_soundness | The challenger's lead is above that bound, and the challenge… | 0.1214 | ratio | brier | test | eq | `[[art:e580bfb4:challenger.brier]]` | verified | 0.1213893435 |
| 84 | conceptual_soundness | The challenger's lead is above that bound, and the challenge… | 0.149 | ratio | brier | test | eq | `[[art:3be8087d:metrics.test.brier]]` | verified | 0.1489501682 |
| 85 | data_integrity | The training split holds 3545 rows and the test split holds… | 3545 | count | n | train | eq | `[[art:1ff4e472:profile.train.n]]` | verified | 3545 |
| 86 | data_integrity | The training split holds 3545 rows and the test split holds… | 1500 | count | n | test | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 87 | data_integrity | The largest missing fraction in any training column is 0 . | 0 | ratio | missing_max | train | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 88 | data_integrity | The largest missing fraction in any test column is likewise… | 0 | ratio | missing_max | test | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 89 | data_integrity | Neither split's worst column stands above the other's, and t… | 0.1 | ratio | missing_gap |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 90 | data_integrity | The largest train-to-test population stability index, the sc… | 0.01082 | ratio | psi |  | eq | `[[art:9300bdd4:psi.max]]` | verified | 0.01081685833 |
| 91 | data_integrity | The largest train-to-test population stability index, the sc… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 92 | data_integrity | The largest train-to-test population stability index, the sc… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 93 | data_integrity | - limit_bal at 0.01082 , the largest of the features; | 0.01082 | ratio | psi |  | eq | `[[art:5db122d3:psi.limit_bal]]` | verified | 0.01081685833 |
| 94 | data_integrity | - bill_trend_6m at 0.009307 ; | 0.009307 | ratio | psi |  | eq | `[[art:b8409498:psi.bill_trend_6m]]` | verified | 0.009307267944 |
| 95 | data_integrity | - age at 0.008244 ; | 0.008244 | ratio | psi |  | eq | `[[art:54a6d5c8:psi.age]]` | verified | 0.008244342439 |
| 96 | data_integrity | - bill_mean_6m at 0.007417 ; | 0.007417 | ratio | psi |  | eq | `[[art:05ce5247:psi.bill_mean_6m]]` | verified | 0.007416663518 |
| 97 | data_integrity | - pay_ratio_mean_6m at 0.005142 ; | 0.005142 | ratio | psi |  | eq | `[[art:bca4bf06:psi.pay_ratio_mean_6m]]` | verified | 0.00514221474 |
| 98 | data_integrity | - delinq_max_6m at 0.004879 ; | 0.004879 | ratio | psi |  | eq | `[[art:548e3455:psi.delinq_max_6m]]` | verified | 0.0048789971 |
| 99 | data_integrity | - utilisation at 0.004511 ; | 0.004511 | ratio | psi |  | eq | `[[art:21c53bd0:psi.utilisation]]` | verified | 0.004510827349 |
| 100 | data_integrity | - pay_ratio_last at 0.004465 ; | 0.004465 | ratio | psi |  | eq | `[[art:ed34c7dc:psi.pay_ratio_last]]` | verified | 0.004465097584 |
| 101 | data_integrity | - delinq_last at 0.002615 ; | 0.002615 | ratio | psi |  | eq | `[[art:7298b08b:psi.delinq_last]]` | verified | 0.002615317622 |
| 102 | data_integrity | - delinq_count_6m at 0.001826 . | 0.001826 | ratio | psi |  | eq | `[[art:95ad0bbe:psi.delinq_count_6m]]` | verified | 0.001825647083 |
| 103 | data_integrity | The score itself shifts by 0.004938 between the two splits,… | 0.004938 | ratio | psi |  | eq | `[[art:63344faa:psi.y_score]]` | verified | 0.004937814025 |
| 104 | data_integrity | Every one of these values sits far below the declared bound… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 105 | data_integrity | Turning from the marginal distributions to their pull on the… | 0.02201 | ratio | csi |  | eq | `[[art:897f0064:csi.max]]` | verified | 0.02201119885 |
| 106 | data_integrity | Turning from the marginal distributions to their pull on the… | 0.02201 | ratio | csi |  | eq | `[[art:55177f94:csi.delinq_last]]` | verified | 0.02201119885 |
| 107 | data_integrity | The remaining contributions are bill_trend_6m at 0.006491 ,… | 0.006491 | ratio | csi |  | eq | `[[art:85619225:csi.bill_trend_6m]]` | verified | 0.00649133631 |
| 108 | data_integrity | The remaining contributions are bill_trend_6m at 0.006491 ,… | 0.004851 | ratio | csi |  | eq | `[[art:dfb8439b:csi.utilisation]]` | verified | 0.004851339646 |
| 109 | data_integrity | The remaining contributions are bill_trend_6m at 0.006491 ,… | 0.002641 | ratio | csi |  | eq | `[[art:9105b83f:csi.bill_mean_6m]]` | verified | 0.002640859388 |
| 110 | data_integrity | The remaining contributions are bill_trend_6m at 0.006491 ,… | 0.002326 | ratio | csi |  | eq | `[[art:77a551ed:csi.delinq_count_6m]]` | verified | 0.002326112961 |
| 111 | data_integrity | The remaining contributions are bill_trend_6m at 0.006491 ,… | 0.002204 | ratio | csi |  | eq | `[[art:e23fdafd:csi.pay_ratio_last]]` | verified | 0.00220408217 |
| 112 | data_integrity | The remaining contributions are bill_trend_6m at 0.006491 ,… | 0.001619 | ratio | csi |  | eq | `[[art:ed28e38f:csi.pay_ratio_mean_6m]]` | verified | 0.00161884206 |
| 113 | data_integrity | The remaining contributions are bill_trend_6m at 0.006491 ,… | 0.001136 | ratio | csi |  | eq | `[[art:f96c2df9:csi.limit_bal]]` | verified | 0.001135997167 |
| 114 | data_integrity | The remaining contributions are bill_trend_6m at 0.006491 ,… | 0.0009881 | ratio | csi |  | eq | `[[art:76338ca5:csi.age]]` | verified | 0.0009881212408 |
| 115 | data_integrity | The remaining contributions are bill_trend_6m at 0.006491 ,… | 0.0007952 | ratio | csi |  | eq | `[[art:e6506c3b:csi.delinq_max_6m]]` | verified | 0.0007951651536 |
| 116 | data_integrity | The ordering differs from the marginal one: delinq_last move… | 0.002615 | ratio | psi |  | eq | `[[art:7298b08b:psi.delinq_last]]` | verified | 0.002615317622 |
| 117 | data_integrity | The ordering differs from the marginal one: delinq_last move… | 0.01082 | ratio | psi |  | eq | `[[art:5db122d3:psi.limit_bal]]` | verified | 0.01081685833 |
| 118 | data_integrity | The ordering differs from the marginal one: delinq_last move… | 0.001136 | ratio | csi |  | eq | `[[art:f96c2df9:csi.limit_bal]]` | verified | 0.001135997167 |
| 119 | data_integrity | No characteristic contribution reaches the declared stabilit… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 120 | data_integrity | The declared-timing screen flags 0 features as measured duri… | 0 | count | n_flagged |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 121 | data_integrity | The strongest single feature reaches an AUC of 0.6819 , belo… | 0.6819 | ratio | auc |  | eq | `[[art:7c15f992:leakage.target_corr.max_single_feature_auc]]` | verified | 0.6819042009 |
| 122 | data_integrity | The strongest single feature reaches an AUC of 0.6819 , belo… | 0.9 | ratio | auc |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 123 | data_integrity | The name screen matches 0 feature names against the target-a… | 0 | count | n_matched |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 124 | data_integrity | On the identifier arm, the share of test rows whose client i… | 0 | ratio | overlap_ids |  | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 125 | data_integrity | On the identifier arm, the share of test rows whose client i… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 126 | data_integrity | On the feature arm, the share of test rows whose feature val… | 0.03 | ratio | overlap |  | eq | `[[art:a2cd9767:leakage.overlap]]` | verified | 0.03 |
| 127 | data_integrity | That arm is read not against the declared bound but against… | 0 | ratio | duplicates | train | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 128 | data_integrity | The applied bound therefore took the value 0.005 , and the f… | 0.005 | ratio | overlap |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 129 | data_integrity | The applied bound therefore took the value 0.005 , and the f… | 0.03 | ratio | overlap |  | eq | `[[art:dc2d0a43:leakage.overlap.features]]` | verified | 0.03 |
| 130 | data_integrity | The two arms point in opposite directions: the identifier ar… | 0 | ratio | overlap_ids |  | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 131 | data_integrity | The two arms point in opposite directions: the identifier ar… | 0.03 | ratio | overlap |  | eq | `[[art:dc2d0a43:leakage.overlap.features]]` | verified | 0.03 |
| 132 | data_integrity | Because the within-train duplicate share is 0 , the coincide… | 0 | ratio | duplicates | train | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 133 | outcomes | The reason is the observed event rate on the evaluation spli… | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 134 | outcomes | The reason is the observed event rate on the evaluation spli… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 135 | outcomes | \| Rows \| 3545 \| 1500 \| | 3545 | count | n | train | eq | `[[art:343c4301:metrics.train.n]]` | verified | 3545 |
| 136 | outcomes | \| Rows \| 3545 \| 1500 \| | 1500 | count | n | test | eq | `[[art:64fcf14d:metrics.test.n]]` | verified | 1500 |
| 137 | outcomes | \| Observed event rate \| 0.2245 \| 0.2247 \| | 0.2245 | ratio | event_rate | train | eq | `[[art:cf2ea9d7:metrics.train.event_rate]]` | verified | 0.2245416079 |
| 138 | outcomes | \| Observed event rate \| 0.2245 \| 0.2247 \| | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 139 | outcomes | \| AUC \| 0.7589 \| 0.748 \| | 0.7589 | ratio | auc | train | eq | `[[art:92ca327f:metrics.train.auc]]` | verified | 0.7588597772 |
| 140 | outcomes | \| AUC \| 0.7589 \| 0.748 \| | 0.748 | ratio | auc | test | eq | `[[art:33170ddf:metrics.test.auc]]` | verified | 0.748047488 |
| 141 | outcomes | \| Gini \| 0.5177 \| 0.4961 \| | 0.5177 | ratio | gini | train | eq | `[[art:b7417c30:metrics.train.gini]]` | verified | 0.5177195545 |
| 142 | outcomes | \| Gini \| 0.5177 \| 0.4961 \| | 0.4961 | ratio | gini | test | eq | `[[art:e7acec22:metrics.test.gini]]` | verified | 0.4960949759 |
| 143 | outcomes | \| KS \| 0.4447 \| 0.419 \| | 0.4447 | ratio | ks | train | eq | `[[art:39f29309:metrics.train.ks]]` | verified | 0.4447131072 |
| 144 | outcomes | \| KS \| 0.4447 \| 0.419 \| | 0.419 | ratio | ks | test | eq | `[[art:63623085:metrics.test.ks]]` | verified | 0.4189589494 |
| 145 | outcomes | \| Brier \| 0.149 \| 0.149 \| | 0.149 | ratio | brier | train | eq | `[[art:0215ac1d:metrics.train.brier]]` | verified | 0.1490409093 |
| 146 | outcomes | \| Brier \| 0.149 \| 0.149 \| | 0.149 | ratio | brier | test | eq | `[[art:3be8087d:metrics.test.brier]]` | verified | 0.1489501682 |
| 147 | outcomes | \| Log loss \| 0.465 \| 0.4674 \| | 0.465 | ratio | logloss | train | eq | `[[art:a9dde81e:metrics.train.logloss]]` | verified | 0.4650342534 |
| 148 | outcomes | \| Log loss \| 0.465 \| 0.4674 \| | 0.4674 | ratio | logloss | test | eq | `[[art:33a9bfcd:metrics.test.logloss]]` | verified | 0.4673916168 |
| 149 | outcomes | \| Mean predicted probability \| 0.2246 \| 0.2213 \| | 0.2246 | ratio | mean_predicted | train | eq | `[[art:233a7dff:metrics.train.mean_predicted]]` | verified | 0.2246150387 |
| 150 | outcomes | \| Mean predicted probability \| 0.2246 \| 0.2213 \| | 0.2213 | ratio | mean_predicted | test | eq | `[[art:4920f430:metrics.test.mean_predicted]]` | verified | 0.2212995331 |
| 151 | outcomes | The two highest-probability deciles of the evaluation split… | 0.4718 | ratio | top2_capture | test | eq | `[[art:d4a1cf7d:deciles.test.top2_capture]]` | verified | 0.471810089 |
| 152 | outcomes | The two highest-probability deciles of the evaluation split… | 0.4485 | ratio | top2_capture | train | eq | `[[art:15637767:deciles.train.top2_capture]]` | verified | 0.4484924623 |
| 153 | outcomes | The train-to-test AUC gap is read against a bound of 0.08 . | 0.08 | ratio | auc_gap |  | eq | `[[art:630f28f4:threshold.O1.auc_gap]]` | verified | 0.08 |
| 154 | outcomes | AUC is 0.7589 on the development split and 0.748 on the eval… | 0.7589 | ratio | auc | train | eq | `[[art:92ca327f:metrics.train.auc]]` | verified | 0.7588597772 |
| 155 | outcomes | AUC is 0.7589 on the development split and 0.748 on the eval… | 0.748 | ratio | auc | test | eq | `[[art:33170ddf:metrics.test.auc]]` | verified | 0.748047488 |
| 156 | outcomes | The largest train-to-test population stability index across… | 0.01082 | ratio | psi |  | eq | `[[art:9300bdd4:psi.max]]` | verified | 0.01081685833 |
| 157 | outcomes | The largest train-to-test population stability index across… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 158 | outcomes | The logistic regression of the outcome on the logit of the p… | 1.001 | ratio | calibration_slope | test | eq | `[[art:95a66bf5:calibration_slope.test]]` | verified | 1.000821291 |
| 159 | outcomes | The logistic regression of the outcome on the logit of the p… | 1.002 | ratio | calibration_slope | train | eq | `[[art:9f4641a6:calibration_slope.train]]` | verified | 1.001952049 |
| 160 | outcomes | The logistic regression of the outcome on the logit of the p… | 0.8 | ratio | calibration_slope |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 161 | outcomes | The logistic regression of the outcome on the logit of the p… | 1.2 | ratio | calibration_slope |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 162 | outcomes | The intercept of that same regression is 0.02371 on the eval… | 0.02371 | ratio | calibration_intercept | test | eq | `[[art:ec6ca742:calibration_intercept.test]]` | verified | 0.02371386382 |
| 163 | outcomes | The intercept of that same regression is 0.02371 on the eval… | 0.001736 | ratio | calibration_intercept | train | eq | `[[art:0b1e1ff9:calibration_intercept.train]]` | verified | 0.001736218384 |
| 164 | outcomes | Mean predicted probability on the evaluation split is 0.2213… | 0.2213 | ratio | mean_predicted | test | eq | `[[art:4920f430:metrics.test.mean_predicted]]` | verified | 0.2212995331 |
| 165 | outcomes | Mean predicted probability on the evaluation split is 0.2213… | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 166 | outcomes | Expressed relative to the observed rate, that gap is 0.01499… | 0.01499 | ratio | mean_rel_gap | test | eq | `[[art:02e35a65:calibration.mean_rel_gap.test]]` | verified | 0.01498724157 |
| 167 | outcomes | Expressed relative to the observed rate, that gap is 0.01499… | 0.000327 | ratio | mean_rel_gap | train | eq | `[[art:060d5049:calibration.mean_rel_gap.train]]` | verified | 0.0003270253632 |
| 168 | outcomes | Expressed relative to the observed rate, that gap is 0.01499… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 169 | outcomes | On the development split this slice's AUC falls 0.002284 bel… | 0.002284 | ratio | auc_gap | train | eq | `[[art:bee2f92d:metrics.train.sub.limit_bal_low.auc_gap]]` | verified | 0.002283832056 |
| 170 | outcomes | On the development split this slice's AUC falls 0.002284 bel… | -0.01283 | ratio | auc_gap | test | eq | `[[art:73357597:metrics.test.sub.limit_bal_low.auc_gap]]` | verified | -0.01283429209 |
| 171 | outcomes | On the development split this slice's AUC falls 0.002284 bel… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 172 | outcomes | The slice holds 0.503 of the development split and 0.504 of… | 0.503 | ratio | share | train | eq | `[[art:41a3d52e:metrics.train.sub.limit_bal_low.share]]` | verified | 0.5029619182 |
| 173 | outcomes | The slice holds 0.503 of the development split and 0.504 of… | 0.504 | ratio | share | test | eq | `[[art:bac689cc:metrics.test.sub.limit_bal_low.share]]` | verified | 0.504 |
| 174 | outcomes | The slice holds 0.503 of the development split and 0.504 of… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 175 | outcomes | Mean predicted probability on the evaluation split slice is… | 0.2442 | ratio | mean_predicted | test | eq | `[[art:8308df9e:metrics.test.sub.limit_bal_low.mean_predicted]]` | verified | 0.2442035495 |
| 176 | outcomes | Mean predicted probability on the evaluation split slice is… | 0.2487 | ratio | event_rate | test | eq | `[[art:de78adb5:metrics.test.sub.limit_bal_low.event_rate]]` | verified | 0.2486772487 |
| 177 | outcomes | Mean predicted probability on the evaluation split slice is… | 0.01799 | ratio | mean_rel_gap | test | eq | `[[art:b07ef9b1:metrics.test.sub.limit_bal_low.mean_rel_gap]]` | verified | 0.01798998187 |
| 178 | outcomes | Mean predicted probability on the evaluation split slice is… | 0.01216 | ratio | mean_rel_gap | train | eq | `[[art:dfe3d86c:metrics.train.sub.limit_bal_low.mean_rel_gap]]` | verified | 0.01215608518 |
| 179 | outcomes | Mean predicted probability on the evaluation split slice is… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 180 | outcomes | This slice's AUC falls 0.005408 below the development split'… | 0.005408 | ratio | auc_gap | train | eq | `[[art:4f0231ad:metrics.train.sub.limit_bal_high.auc_gap]]` | verified | 0.005408358634 |
| 181 | outcomes | This slice's AUC falls 0.005408 below the development split'… | 0.02796 | ratio | auc_gap | test | eq | `[[art:677dd01a:metrics.test.sub.limit_bal_high.auc_gap]]` | verified | 0.02796401832 |
| 182 | outcomes | This slice's AUC falls 0.005408 below the development split'… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 183 | outcomes | It holds 0.497 of the development split and 0.496 of the eva… | 0.497 | ratio | share | train | eq | `[[art:63a6b099:metrics.train.sub.limit_bal_high.share]]` | verified | 0.4970380818 |
| 184 | outcomes | It holds 0.497 of the development split and 0.496 of the eva… | 0.496 | ratio | share | test | eq | `[[art:ac383ccb:metrics.test.sub.limit_bal_high.share]]` | verified | 0.496 |
| 185 | outcomes | It holds 0.497 of the development split and 0.496 of the eva… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 186 | outcomes | Mean predicted probability on the evaluation split slice is… | 0.198 | ratio | mean_predicted | test | eq | `[[art:43036bf7:metrics.test.sub.limit_bal_high.mean_predicted]]` | verified | 0.198026097 |
| 187 | outcomes | Mean predicted probability on the evaluation split slice is… | 0.2003 | ratio | event_rate | test | eq | `[[art:5e9aab40:metrics.test.sub.limit_bal_high.event_rate]]` | verified | 0.2002688172 |
| 188 | outcomes | Mean predicted probability on the evaluation split slice is… | 0.0112 | ratio | mean_rel_gap | test | eq | `[[art:c0862d76:metrics.test.sub.limit_bal_high.mean_rel_gap]]` | verified | 0.0111985491 |
| 189 | outcomes | Mean predicted probability on the evaluation split slice is… | 0.01545 | ratio | mean_rel_gap | train | eq | `[[art:64fe2acf:metrics.train.sub.limit_bal_high.mean_rel_gap]]` | verified | 0.01544545924 |
| 190 | outcomes | Mean predicted probability on the evaluation split slice is… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 191 | outcomes | This slice's AUC falls 0.01403 below the development split's… | 0.01403 | ratio | auc_gap | train | eq | `[[art:253a83c0:metrics.train.sub.delinq_count_6m_high.auc_gap]]` | verified | 0.01403117204 |
| 192 | outcomes | This slice's AUC falls 0.01403 below the development split's… | -0.001865 | ratio | auc_gap | test | eq | `[[art:49275c9b:metrics.test.sub.delinq_count_6m_high.auc_gap]]` | verified | -0.001864792751 |
| 193 | outcomes | This slice's AUC falls 0.01403 below the development split's… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 194 | outcomes | It holds 0.3766 of the development split and 0.3667 of the e… | 0.3766 | ratio | share | train | eq | `[[art:ef2e70bf:metrics.train.sub.delinq_count_6m_high.share]]` | verified | 0.3765867419 |
| 195 | outcomes | It holds 0.3766 of the development split and 0.3667 of the e… | 0.3667 | ratio | share | test | eq | `[[art:22847310:metrics.test.sub.delinq_count_6m_high.share]]` | verified | 0.3666666667 |
| 196 | outcomes | It holds 0.3766 of the development split and 0.3667 of the e… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 197 | outcomes | Mean predicted probability on the evaluation split slice is… | 0.3202 | ratio | mean_predicted | test | eq | `[[art:5c3b7d30:metrics.test.sub.delinq_count_6m_high.mean_predicted]]` | verified | 0.3202088318 |
| 198 | outcomes | Mean predicted probability on the evaluation split slice is… | 0.3455 | ratio | event_rate | test | eq | `[[art:ef17c303:metrics.test.sub.delinq_count_6m_high.event_rate]]` | verified | 0.3454545455 |
| 199 | outcomes | Mean predicted probability on the evaluation split slice is… | 0.07308 | ratio | mean_rel_gap | test | eq | `[[art:7f0a352c:metrics.test.sub.delinq_count_6m_high.mean_rel_gap]]` | verified | 0.07307969733 |
| 200 | outcomes | Mean predicted probability on the evaluation split slice is… | 0.00564 | ratio | mean_rel_gap | train | eq | `[[art:b1995733:metrics.train.sub.delinq_count_6m_high.mean_rel_gap]]` | verified | 0.00564035353 |
| 201 | outcomes | Mean predicted probability on the evaluation split slice is… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 202 | outcomes | On the development split this slice's AUC falls 0.03626 belo… | 0.03626 | ratio | auc_gap | train | eq | `[[art:b720a1d0:metrics.train.sub.delinq_count_6m_low.auc_gap]]` | verified | 0.03625867187 |
| 203 | outcomes | On the development split this slice's AUC falls 0.03626 belo… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 204 | outcomes | On the evaluation split it falls 0.08836 below the split's o… | 0.08836 | ratio | auc_gap | test | eq | `[[art:9b3b5b67:metrics.test.sub.delinq_count_6m_low.auc_gap]]` | verified | 0.08836144666 |
| 205 | outcomes | On the evaluation split it falls 0.08836 below the split's o… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 206 | outcomes | On the evaluation split it falls 0.08836 below the split's o… | 0.6597 | ratio | auc | test | eq | `[[art:2dd8f8e5:metrics.test.sub.delinq_count_6m_low.auc]]` | verified | 0.6596860413 |
| 207 | outcomes | On the evaluation split it falls 0.08836 below the split's o… | 0.748 | ratio | auc | test | eq | `[[art:33170ddf:metrics.test.auc]]` | verified | 0.748047488 |
| 208 | outcomes | The slice holds 0.6234 of the development split and 0.6333 o… | 0.6234 | ratio | share | train | eq | `[[art:3501db92:metrics.train.sub.delinq_count_6m_low.share]]` | verified | 0.6234132581 |
| 209 | outcomes | The slice holds 0.6234 of the development split and 0.6333 o… | 0.6333 | ratio | share | test | eq | `[[art:3257b2f3:metrics.test.sub.delinq_count_6m_low.share]]` | verified | 0.6333333333 |
| 210 | outcomes | The slice holds 0.6234 of the development split and 0.6333 o… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 211 | outcomes | Mean predicted probability on the evaluation split slice is… | 0.164 | ratio | mean_predicted | test | eq | `[[art:642f1e64:metrics.test.sub.delinq_count_6m_low.mean_predicted]]` | verified | 0.1640362548 |
| 212 | outcomes | Mean predicted probability on the evaluation split slice is… | 0.1547 | ratio | event_rate | test | eq | `[[art:9690f94d:metrics.test.sub.delinq_count_6m_low.event_rate]]` | verified | 0.1547368421 |
| 213 | outcomes | Mean predicted probability on the evaluation split slice is… | 0.0601 | ratio | mean_rel_gap | test | eq | `[[art:b51086d6:metrics.test.sub.delinq_count_6m_low.mean_rel_gap]]` | verified | 0.06009824547 |
| 214 | outcomes | Mean predicted probability on the evaluation split slice is… | 0.005699 | ratio | mean_rel_gap | train | eq | `[[art:238a7795:metrics.train.sub.delinq_count_6m_low.mean_rel_gap]]` | verified | 0.005698545185 |
| 215 | outcomes | Mean predicted probability on the evaluation split slice is… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 216 | sensitivity | The largest variance inflation factor across the retained fe… | 7.31 | ratio | vif |  | eq | `[[art:d8e9619c:vif.max]]` | verified | 7.309956746 |
| 217 | sensitivity | The largest variance inflation factor across the retained fe… | 10 | ratio | vif |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 218 | sensitivity | That maximum is attained on the six-month mean bill amount,… | 7.31 | ratio | vif |  | eq | `[[art:1915242e:vif.bill_mean_6m]]` | verified | 7.309956746 |
| 219 | sensitivity | Close beneath it sit the most recent payment ratio at 7.286… | 7.286 | ratio | vif |  | eq | `[[art:e30c6fbd:vif.pay_ratio_last]]` | verified | 7.285574881 |
| 220 | sensitivity | Close beneath it sit the most recent payment ratio at 7.286… | 7.28 | ratio | vif |  | eq | `[[art:4d1589cd:vif.pay_ratio_mean_6m]]` | verified | 7.279863906 |
| 221 | sensitivity | The credit limit follows at 4.82 , and utilisation at 3.215… | 4.82 | ratio | vif |  | eq | `[[art:eeeb5c27:vif.limit_bal]]` | verified | 4.819728893 |
| 222 | sensitivity | The credit limit follows at 4.82 , and utilisation at 3.215… | 3.215 | ratio | vif |  | eq | `[[art:7298e587:vif.utilisation]]` | verified | 3.214614007 |
| 223 | sensitivity | The delinquency block sits lower: 2.567 for the six-month co… | 2.567 | ratio | vif |  | eq | `[[art:ca9bf9ad:vif.delinq_count_6m]]` | verified | 2.56680207 |
| 224 | sensitivity | The delinquency block sits lower: 2.567 for the six-month co… | 2.403 | ratio | vif |  | eq | `[[art:95ebdd8f:vif.delinq_max_6m]]` | verified | 2.403293321 |
| 225 | sensitivity | The delinquency block sits lower: 2.567 for the six-month co… | 1.414 | ratio | vif |  | eq | `[[art:a561c855:vif.delinq_last]]` | verified | 1.413950115 |
| 226 | sensitivity | The six-month bill trend at 1.201 and age at 1.002 are the l… | 1.201 | ratio | vif |  | eq | `[[art:78a03a7b:vif.bill_trend_6m]]` | verified | 1.20121523 |
| 227 | sensitivity | The six-month bill trend at 1.201 and age at 1.002 are the l… | 1.002 | ratio | vif |  | eq | `[[art:628d9c69:vif.age]]` | verified | 1.002128816 |
| 228 | sensitivity | The condition number of the column-standardised design is 5.… | 5.557 | ratio | condition_number |  | eq | `[[art:8029574b:condition_number]]` | verified | 5.556505365 |
| 229 | sensitivity | The condition number of the column-standardised design is 5.… | 30 | ratio | condition_number |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 230 | findings | The share of test rows whose feature values also appear in t… | 0.03 | ratio | overlap.features | test | eq | `[[art:dc2d0a43:leakage.overlap.features]]` | verified | 0.03 |
| 231 | findings | The share of test rows whose feature values also appear in t… | 0.005 | ratio | overlap.features_effective |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 232 | findings | That applied bound sits at the declared contamination thresh… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 233 | findings | That applied bound sits at the declared contamination thresh… | 0 | ratio | duplicates | train | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 234 | findings | The challenger reaches an AUC on test of 0.8346 , against th… | 0.8346 | ratio | auc | test | eq | `[[art:d1533f6e:challenger.auc]]` | verified | 0.8345601649 |
| 235 | findings | The challenger reaches an AUC on test of 0.8346 , against th… | 0.748 | ratio | auc | test | eq | `[[art:33170ddf:metrics.test.auc]]` | verified | 0.748047488 |
| 236 | findings | The challenger's lead over the champion is 0.08651 , above t… | 0.08651 | ratio | delta_auc | test | eq | `[[art:95cce9d6:challenger.delta_auc]]` | verified | 0.08651267698 |
| 237 | findings | The challenger's lead over the champion is 0.08651 , above t… | 0.03 | ratio | delta_auc |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 238 | findings | On the segment `delinq_count_6m <= median(delinq_count_6m)`,… | 0.6333 | ratio | share | test | eq | `[[art:3257b2f3:metrics.test.sub.delinq_count_6m_low.share]]` | verified | 0.6333333333 |
| 239 | findings | On the segment `delinq_count_6m <= median(delinq_count_6m)`,… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 240 | findings | On the segment `delinq_count_6m <= median(delinq_count_6m)`,… | 0.6597 | ratio | auc | test | eq | `[[art:2dd8f8e5:metrics.test.sub.delinq_count_6m_low.auc]]` | verified | 0.6596860413 |
| 241 | findings | On the segment `delinq_count_6m <= median(delinq_count_6m)`,… | 0.748 | ratio | auc | test | eq | `[[art:33170ddf:metrics.test.auc]]` | verified | 0.748047488 |
| 242 | findings | On the segment `delinq_count_6m <= median(delinq_count_6m)`,… | 0.08836 | ratio | auc_gap | test | eq | `[[art:9b3b5b67:metrics.test.sub.delinq_count_6m_low.auc_gap]]` | verified | 0.08836144666 |
| 243 | findings | On the segment `delinq_count_6m <= median(delinq_count_6m)`,… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 244 | findings | Can the model developer account for the fitted coefficient o… | -1 | ratio | coef_sign |  | eq | `[[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]]` | verified | -1 |
| 245 | findings | Can the model developer account for the fitted coefficient o… | 1 | ratio | univariate_direction |  | eq | `[[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]]` | verified | 1 |
| 246 | findings | Can the model developer account for the fitted coefficient o… | 0 | ratio | agrees |  | eq | `[[art:c946359c:sign_check.delinq_max_6m.agrees]]` | verified | 0 |
| 247 | findings | Can the model developer account for the fitted coefficient o… | 1 | ratio | coef_sign |  | eq | `[[art:6af6aef2:sign_check.limit_bal.coef_sign]]` | verified | 1 |
| 248 | findings | Can the model developer account for the fitted coefficient o… | -1 | ratio | univariate_direction |  | eq | `[[art:56d284d6:sign_check.limit_bal.univariate_direction]]` | verified | -1 |
| 249 | findings | Can the model developer account for the fitted coefficient o… | 0 | ratio | agrees |  | eq | `[[art:0278aad1:sign_check.limit_bal.agrees]]` | verified | 0 |
| 250 | findings | Can the model developer account for the fitted coefficient o… | 1 | ratio | coef_sign |  | eq | `[[art:f018263e:sign_check.pay_ratio_last.coef_sign]]` | verified | 1 |
| 251 | findings | Can the model developer account for the fitted coefficient o… | -1 | ratio | univariate_direction |  | eq | `[[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]]` | verified | -1 |
| 252 | findings | Can the model developer account for the fitted coefficient o… | 0 | ratio | agrees |  | eq | `[[art:79abee77:sign_check.pay_ratio_last.agrees]]` | verified | 0 |
| 253 | monitoring | - Rank-ordering: track discrimination on each production coh… | 0.7 | ratio | auc | test | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 254 | monitoring | - Rank-ordering: track discrimination on each production coh… | 0.748 | ratio | auc | test | eq | `[[art:33170ddf:metrics.test.auc]]` | verified | 0.748047488 |
| 255 | monitoring | - Probability accuracy: track the mean squared error of the… | 0.2 | ratio | brier | test | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 256 | monitoring | - Probability accuracy: track the mean squared error of the… | 0.149 | ratio | brier | test | eq | `[[art:3be8087d:metrics.test.brier]]` | verified | 0.1489501682 |
| 257 | monitoring | - Calibration: track the slope of the logistic regression of… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 258 | monitoring | - Calibration: track the slope of the logistic regression of… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 259 | monitoring | - Calibration: track the slope of the logistic regression of… | 1.001 | ratio | calibration_slope | test | eq | `[[art:95a66bf5:calibration_slope.test]]` | verified | 1.000821291 |
| 260 | monitoring | - Population stability: recompute the largest shift across t… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 261 | monitoring | - Population stability: recompute the largest shift across t… | 0.01082 | ratio | psi |  | eq | `[[art:9300bdd4:psi.max]]` | verified | 0.01081685833 |
| 262 | monitoring | Section 4 of this report reported discrimination before cali… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 263 | monitoring | If a future cohort's observed event rate falls below 0.05 ,… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |

## Appendix B — Artifact index

The store holds 267 artifacts; the 182 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `ablation.age.delta_auc` | `fa888618` | scalar | -6.123526845e-05 | change in test AUC when the champion's form is refitted without age |
| `ablation.baseline_auc` | `818e6d21` | scalar | 0.748047488 | AUC on test of a refit of the champion's functional form on every retained feature, the level each ablation delta is measured from |
| `ablation.bill_mean_6m.delta_auc` | `0fff644e` | scalar | -0.001513021425 | change in test AUC when the champion's form is refitted without bill_mean_6m |
| `ablation.bill_trend_6m.delta_auc` | `80be2a7e` | scalar | 0.003776174888 | change in test AUC when the champion's form is refitted without bill_trend_6m |
| `ablation.delinq_count_6m.delta_auc` | `a35dafd6` | scalar | 0.0006710364835 | change in test AUC when the champion's form is refitted without delinq_count_6m |
| `ablation.delinq_last.delta_auc` | `9bdbb0b5` | scalar | -0.07608737252 | change in test AUC when the champion's form is refitted without delinq_last |
| `ablation.delinq_max_6m.delta_auc` | `975f1df6` | scalar | 0.0002959704642 | change in test AUC when the champion's form is refitted without delinq_max_6m |
| `ablation.limit_bal.delta_auc` | `d47e9a58` | scalar | 0.0004694703915 | change in test AUC when the champion's form is refitted without limit_bal |
| `ablation.pay_ratio_last.delta_auc` | `1918798e` | scalar | 0.002847439983 | change in test AUC when the champion's form is refitted without pay_ratio_last |
| `ablation.pay_ratio_mean_6m.delta_auc` | `48fca3ba` | scalar | 0.007312511641 | change in test AUC when the champion's form is refitted without pay_ratio_mean_6m |
| `ablation.utilisation.delta_auc` | `c8ce0123` | scalar | -0.01973561673 | change in test AUC when the champion's form is refitted without utilisation |
| `calibration.mean_rel_gap.test` | `02e35a65` | scalar | 0.01498724157 | mean predicted against observed on test, relative |
| `calibration.mean_rel_gap.train` | `060d5049` | scalar | 0.0003270253632 | mean predicted against observed on train, relative |
| `calibration.test` | `851ef21d` | table | table, 10 rows | calibration by decile of predicted probability on test |
| `calibration_intercept.test` | `ec6ca742` | scalar | 0.02371386382 | logistic regression of the outcome on logit(p) on test: the intercept |
| `calibration_intercept.train` | `0b1e1ff9` | scalar | 0.001736218384 | logistic regression of the outcome on logit(p) on train: the intercept |
| `calibration_slope.test` | `95a66bf5` | scalar | 1.000821291 | logistic regression of the outcome on logit(p) on test: the slope |
| `calibration_slope.train` | `9f4641a6` | scalar | 1.001952049 | logistic regression of the outcome on logit(p) on train: the slope |
| `challenger.auc` | `d1533f6e` | scalar | 0.8345601649 | the challenger's AUC on test |
| `challenger.brier` | `e580bfb4` | scalar | 0.1213893435 | the challenger's Brier score on test |
| `challenger.delta_auc` | `95cce9d6` | scalar | 0.08651267698 | the challenger's AUC on test minus the champion's |
| `condition_number` | `8029574b` | scalar | 5.556505365 | Belsley's condition number of the column-standardised design |
| `csi.age` | `76338ca5` | scalar | 0.0009881212408 | CSI of age: its contribution to the shift in the linear predictor |
| `csi.bill_mean_6m` | `9105b83f` | scalar | 0.002640859388 | CSI of bill_mean_6m: its contribution to the shift in the linear predictor |
| `csi.bill_trend_6m` | `85619225` | scalar | 0.00649133631 | CSI of bill_trend_6m: its contribution to the shift in the linear predictor |
| `csi.delinq_count_6m` | `77a551ed` | scalar | 0.002326112961 | CSI of delinq_count_6m: its contribution to the shift in the linear predictor |
| `csi.delinq_last` | `55177f94` | scalar | 0.02201119885 | CSI of delinq_last: its contribution to the shift in the linear predictor |
| `csi.delinq_max_6m` | `e6506c3b` | scalar | 0.0007951651536 | CSI of delinq_max_6m: its contribution to the shift in the linear predictor |
| `csi.limit_bal` | `f96c2df9` | scalar | 0.001135997167 | CSI of limit_bal: its contribution to the shift in the linear predictor |
| `csi.max` | `897f0064` | scalar | 0.02201119885 | the largest characteristic stability index |
| `csi.pay_ratio_last` | `e23fdafd` | scalar | 0.00220408217 | CSI of pay_ratio_last: its contribution to the shift in the linear predictor |
| `csi.pay_ratio_mean_6m` | `ed28e38f` | scalar | 0.00161884206 | CSI of pay_ratio_mean_6m: its contribution to the shift in the linear predictor |
| `csi.utilisation` | `dfb8439b` | scalar | 0.004851339646 | CSI of utilisation: its contribution to the shift in the linear predictor |
| `deciles.test` | `93732a5e` | table | table, 10 rows | decile separation on test; decile 1 holds the highest probabilities |
| `deciles.test.top2_capture` | `d4a1cf7d` | scalar | 0.471810089 | share of test events in the top two deciles |
| `deciles.train.top2_capture` | `15637767` | scalar | 0.4484924623 | share of train events in the top two deciles |
| `leakage.duplicates.train` | `4474c227` | scalar | 0 | share of train rows whose feature values are not unique within train |
| `leakage.name_screen.n_matched` | `407e62be` | scalar | 0 | feature names matching the target-adjacent lexicon |
| `leakage.overlap` | `a2cd9767` | scalar | 0.03 | share of test rows whose feature values also appear in train |
| `leakage.overlap.features` | `dc2d0a43` | scalar | 0.03 | share of test rows whose feature values also appear in train |
| `leakage.overlap.ids` | `63d37fc5` | scalar | 0 | share of test rows whose ['client_id'] also identify a row of train |
| `leakage.target_corr.max_single_feature_auc` | `7c15f992` | scalar | 0.6819042009 | the AUC of the strongest single feature |
| `leakage.timing.n_flagged` | `742bcd24` | scalar | 0 | features declared during_period or after_outcome |
| `metrics.test.auc` | `33170ddf` | scalar | 0.748047488 | auc on test, recomputed by quaestor |
| `metrics.test.brier` | `3be8087d` | scalar | 0.1489501682 | brier on test, recomputed by quaestor |
| `metrics.test.event_rate` | `9209d200` | scalar | 0.2246666667 | event_rate on test, recomputed by quaestor |
| `metrics.test.gini` | `e7acec22` | scalar | 0.4960949759 | gini on test, recomputed by quaestor |
| `metrics.test.ks` | `63623085` | scalar | 0.4189589494 | ks on test, recomputed by quaestor |
| `metrics.test.logloss` | `33a9bfcd` | scalar | 0.4673916168 | logloss on test, recomputed by quaestor |
| `metrics.test.mean_predicted` | `4920f430` | scalar | 0.2212995331 | mean_predicted on test, recomputed by quaestor |
| `metrics.test.n` | `64fcf14d` | scalar | 1500 | n on test, recomputed by quaestor |
| `metrics.test.sub.delinq_count_6m_high` | `d7849ad5` | table | table, 10 rows | every metric on the delinq_count_6m above_median slice of test |
| `metrics.test.sub.delinq_count_6m_high.auc_gap` | `49275c9b` | scalar | -0.001864792751 | how far AUC on the delinq_count_6m above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.delinq_count_6m_high.event_rate` | `ef17c303` | scalar | 0.3454545455 | event_rate on the delinq_count_6m above_median slice of test |
| `metrics.test.sub.delinq_count_6m_high.mean_predicted` | `5c3b7d30` | scalar | 0.3202088318 | mean_predicted on the delinq_count_6m above_median slice of test |
| `metrics.test.sub.delinq_count_6m_high.mean_rel_gap` | `7f0a352c` | scalar | 0.07307969733 | mean predicted against observed on the delinq_count_6m above_median slice of test, relative |
| `metrics.test.sub.delinq_count_6m_high.share` | `22847310` | scalar | 0.3666666667 | the share of test the delinq_count_6m above_median slice holds |
| `metrics.test.sub.delinq_count_6m_low` | `4808d857` | table | table, 10 rows | every metric on the delinq_count_6m below_median slice of test |
| `metrics.test.sub.delinq_count_6m_low.auc` | `2dd8f8e5` | scalar | 0.6596860413 | auc on the delinq_count_6m below_median slice of test |
| `metrics.test.sub.delinq_count_6m_low.auc_gap` | `9b3b5b67` | scalar | 0.08836144666 | how far AUC on the delinq_count_6m below_median slice of test falls below AUC on all of test |
| `metrics.test.sub.delinq_count_6m_low.event_rate` | `9690f94d` | scalar | 0.1547368421 | event_rate on the delinq_count_6m below_median slice of test |
| `metrics.test.sub.delinq_count_6m_low.mean_predicted` | `642f1e64` | scalar | 0.1640362548 | mean_predicted on the delinq_count_6m below_median slice of test |
| `metrics.test.sub.delinq_count_6m_low.mean_rel_gap` | `b51086d6` | scalar | 0.06009824547 | mean predicted against observed on the delinq_count_6m below_median slice of test, relative |
| `metrics.test.sub.delinq_count_6m_low.share` | `3257b2f3` | scalar | 0.6333333333 | the share of test the delinq_count_6m below_median slice holds |
| `metrics.test.sub.limit_bal_high` | `23e111d4` | table | table, 10 rows | every metric on the limit_bal above_median slice of test |
| `metrics.test.sub.limit_bal_high.auc_gap` | `677dd01a` | scalar | 0.02796401832 | how far AUC on the limit_bal above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.limit_bal_high.event_rate` | `5e9aab40` | scalar | 0.2002688172 | event_rate on the limit_bal above_median slice of test |
| `metrics.test.sub.limit_bal_high.mean_predicted` | `43036bf7` | scalar | 0.198026097 | mean_predicted on the limit_bal above_median slice of test |
| `metrics.test.sub.limit_bal_high.mean_rel_gap` | `c0862d76` | scalar | 0.0111985491 | mean predicted against observed on the limit_bal above_median slice of test, relative |
| `metrics.test.sub.limit_bal_high.share` | `ac383ccb` | scalar | 0.496 | the share of test the limit_bal above_median slice holds |
| `metrics.test.sub.limit_bal_low` | `e46a4670` | table | table, 10 rows | every metric on the limit_bal below_median slice of test |
| `metrics.test.sub.limit_bal_low.auc_gap` | `73357597` | scalar | -0.01283429209 | how far AUC on the limit_bal below_median slice of test falls below AUC on all of test |
| `metrics.test.sub.limit_bal_low.event_rate` | `de78adb5` | scalar | 0.2486772487 | event_rate on the limit_bal below_median slice of test |
| `metrics.test.sub.limit_bal_low.mean_predicted` | `8308df9e` | scalar | 0.2442035495 | mean_predicted on the limit_bal below_median slice of test |
| `metrics.test.sub.limit_bal_low.mean_rel_gap` | `b07ef9b1` | scalar | 0.01798998187 | mean predicted against observed on the limit_bal below_median slice of test, relative |
| `metrics.test.sub.limit_bal_low.share` | `bac689cc` | scalar | 0.504 | the share of test the limit_bal below_median slice holds |
| `metrics.train.auc` | `92ca327f` | scalar | 0.7588597772 | auc on train, recomputed by quaestor |
| `metrics.train.brier` | `0215ac1d` | scalar | 0.1490409093 | brier on train, recomputed by quaestor |
| `metrics.train.event_rate` | `cf2ea9d7` | scalar | 0.2245416079 | event_rate on train, recomputed by quaestor |
| `metrics.train.gini` | `b7417c30` | scalar | 0.5177195545 | gini on train, recomputed by quaestor |
| `metrics.train.ks` | `39f29309` | scalar | 0.4447131072 | ks on train, recomputed by quaestor |
| `metrics.train.logloss` | `a9dde81e` | scalar | 0.4650342534 | logloss on train, recomputed by quaestor |
| `metrics.train.mean_predicted` | `233a7dff` | scalar | 0.2246150387 | mean_predicted on train, recomputed by quaestor |
| `metrics.train.n` | `343c4301` | scalar | 3545 | n on train, recomputed by quaestor |
| `metrics.train.sub.delinq_count_6m_high` | `19032a97` | table | table, 10 rows | every metric on the delinq_count_6m above_median slice of train |
| `metrics.train.sub.delinq_count_6m_high.auc_gap` | `253a83c0` | scalar | 0.01403117204 | how far AUC on the delinq_count_6m above_median slice of train falls below AUC on all of train |
| `metrics.train.sub.delinq_count_6m_high.mean_rel_gap` | `b1995733` | scalar | 0.00564035353 | mean predicted against observed on the delinq_count_6m above_median slice of train, relative |
| `metrics.train.sub.delinq_count_6m_high.share` | `ef2e70bf` | scalar | 0.3765867419 | the share of train the delinq_count_6m above_median slice holds |
| `metrics.train.sub.delinq_count_6m_low` | `c74040cc` | table | table, 10 rows | every metric on the delinq_count_6m below_median slice of train |
| `metrics.train.sub.delinq_count_6m_low.auc_gap` | `b720a1d0` | scalar | 0.03625867187 | how far AUC on the delinq_count_6m below_median slice of train falls below AUC on all of train |
| `metrics.train.sub.delinq_count_6m_low.mean_rel_gap` | `238a7795` | scalar | 0.005698545185 | mean predicted against observed on the delinq_count_6m below_median slice of train, relative |
| `metrics.train.sub.delinq_count_6m_low.share` | `3501db92` | scalar | 0.6234132581 | the share of train the delinq_count_6m below_median slice holds |
| `metrics.train.sub.limit_bal_high` | `68a13fc7` | table | table, 10 rows | every metric on the limit_bal above_median slice of train |
| `metrics.train.sub.limit_bal_high.auc_gap` | `4f0231ad` | scalar | 0.005408358634 | how far AUC on the limit_bal above_median slice of train falls below AUC on all of train |
| `metrics.train.sub.limit_bal_high.mean_rel_gap` | `64fe2acf` | scalar | 0.01544545924 | mean predicted against observed on the limit_bal above_median slice of train, relative |
| `metrics.train.sub.limit_bal_high.share` | `63a6b099` | scalar | 0.4970380818 | the share of train the limit_bal above_median slice holds |
| `metrics.train.sub.limit_bal_low` | `b2a797ce` | table | table, 10 rows | every metric on the limit_bal below_median slice of train |
| `metrics.train.sub.limit_bal_low.auc_gap` | `bee2f92d` | scalar | 0.002283832056 | how far AUC on the limit_bal below_median slice of train falls below AUC on all of train |
| `metrics.train.sub.limit_bal_low.mean_rel_gap` | `dfe3d86c` | scalar | 0.01215608518 | mean predicted against observed on the limit_bal below_median slice of train, relative |
| `metrics.train.sub.limit_bal_low.share` | `41a3d52e` | scalar | 0.5029619182 | the share of train the limit_bal below_median slice holds |
| `profile.test.missing.max` | `f813848d` | scalar | 0 | the largest missing fraction in test |
| `profile.test.n` | `2193cf5f` | scalar | 1500 | rows in test |
| `profile.train.missing.max` | `050a3099` | scalar | 0 | the largest missing fraction in train |
| `profile.train.n` | `1ff4e472` | scalar | 3545 | rows in train |
| `psi.age` | `54a6d5c8` | scalar | 0.008244342439 | PSI of age between train and test |
| `psi.bill_mean_6m` | `05ce5247` | scalar | 0.007416663518 | PSI of bill_mean_6m between train and test |
| `psi.bill_trend_6m` | `b8409498` | scalar | 0.009307267944 | PSI of bill_trend_6m between train and test |
| `psi.delinq_count_6m` | `95ad0bbe` | scalar | 0.001825647083 | PSI of delinq_count_6m between train and test |
| `psi.delinq_last` | `7298b08b` | scalar | 0.002615317622 | PSI of delinq_last between train and test |
| `psi.delinq_max_6m` | `548e3455` | scalar | 0.0048789971 | PSI of delinq_max_6m between train and test |
| `psi.limit_bal` | `5db122d3` | scalar | 0.01081685833 | PSI of limit_bal between train and test |
| `psi.max` | `9300bdd4` | scalar | 0.01081685833 | the largest train-to-test PSI, score included |
| `psi.pay_ratio_last` | `ed34c7dc` | scalar | 0.004465097584 | PSI of pay_ratio_last between train and test |
| `psi.pay_ratio_mean_6m` | `bca4bf06` | scalar | 0.00514221474 | PSI of pay_ratio_mean_6m between train and test |
| `psi.utilisation` | `21c53bd0` | scalar | 0.004510827349 | PSI of utilisation between train and test |
| `psi.y_score` | `63344faa` | scalar | 0.004937814025 | PSI of the score between train and test |
| `rule.calibration_first_event_rate` | `42f1351e` | scalar | 0.05 | the event rate below which the report puts calibration before discrimination |
| `run.features` | `abbb748e` | json | json | the subject's features.json |
| `run.model_summary` | `259cdde6` | json | json | the subject's model_summary.json |
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
| `threshold.O1.slice_min_share` | `9a6f1a87` | scalar | 0.1 | the share of a split a sub-population must hold before it can raise an open item |
| `threshold.S1.psi` | `278b9016` | scalar | 0.25 | S1: the population stability index, train against test |
| `threshold.package.auc.test.min` | `8bfd02cc` | scalar | 0.7 | package.yaml declares auc min 0.7 |
| `threshold.package.brier.test.max` | `d0f98b9c` | scalar | 0.2 | package.yaml declares brier max 0.2 |
| `threshold.package.calibration_slope.test.max` | `0adb7a89` | scalar | 1.2 | package.yaml declares calibration_slope max 1.2 |
| `threshold.package.calibration_slope.test.min` | `95fdb848` | scalar | 0.8 | package.yaml declares calibration_slope min 0.8 |
| `threshold.package.psi.max` | `fbb5a9d1` | scalar | 0.25 | package.yaml declares psi max 0.25 |
| `thresholds.evaluation` | `1dbd7569` | table | table, 5 rows | every threshold package.yaml declares, with its bound, the recomputed value and the outcome |
| `vif.age` | `628d9c69` | scalar | 1.002128816 | variance inflation factor of age on train |
| `vif.bill_mean_6m` | `1915242e` | scalar | 7.309956746 | variance inflation factor of bill_mean_6m on train |
| `vif.bill_trend_6m` | `78a03a7b` | scalar | 1.20121523 | variance inflation factor of bill_trend_6m on train |
| `vif.delinq_count_6m` | `ca9bf9ad` | scalar | 2.56680207 | variance inflation factor of delinq_count_6m on train |
| `vif.delinq_last` | `a561c855` | scalar | 1.413950115 | variance inflation factor of delinq_last on train |
| `vif.delinq_max_6m` | `95ebdd8f` | scalar | 2.403293321 | variance inflation factor of delinq_max_6m on train |
| `vif.limit_bal` | `eeeb5c27` | scalar | 4.819728893 | variance inflation factor of limit_bal on train |
| `vif.max` | `d8e9619c` | scalar | 7.309956746 | the largest variance inflation factor |
| `vif.pay_ratio_last` | `e30c6fbd` | scalar | 7.285574881 | variance inflation factor of pay_ratio_last on train |
| `vif.pay_ratio_mean_6m` | `4d1589cd` | scalar | 7.279863906 | variance inflation factor of pay_ratio_mean_6m on train |
| `vif.utilisation` | `7298e587` | scalar | 3.214614007 | variance inflation factor of utilisation on train |

## Appendix C — Run trace summary

| quantity | value |
|---|---|
| tool calls | 17 (run_model 1, profile_data 1, compute_metrics 5, check_leakage 1, check_collinearity 1, challenger_compare 1, retrieve_guidance 7) |
| plan steps (bounded loop) | 4 |
| LLM calls | 18 (plan 4, draft 7, extract 7) |
| re-asks | 0 |
| repair rounds | 0 |
| tokens in / out | 223,137 / 101,047 |
| notional cost (USD) | 4.7991 |
| wall-clock (s) | 1091.70 |
| subject run (s) | 1.16 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | credit_default-full_agent-20260920T074524Z-e2e51e00 |

## Appendix D — Not checked

| item | reason |
|---|---|
| `check_stability` (R1) | package declares no `regime.column` |
| `run_scenarios` (X1) | not applicable to `binary_classification` |
| out-of-time and vintage-holdout metrics (O1, second rule) | package declares neither split |
| developer claims (T1, claim channel) | The package declares 2 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
