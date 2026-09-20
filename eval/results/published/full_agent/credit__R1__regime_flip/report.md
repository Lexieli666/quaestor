---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: full_agent
model: claude-opus-5[1m]
run_id: credit_default-full_agent-20260920T092037Z-e2e51e00
data_mode: synthetic
synthetic_n: 5000
grounding_precision_pre: 1.0000
grounding_precision_post: 1.0000
n_claims: 239
n_findings_by_severity: {high: 0, medium: 1, low: 1, info: 0}
generated: "2026-09-20T09:20:37Z"
illustrative: false
---

# Validation report — `credit_default` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `credit_default` v1.0 | `full_agent` | claude-opus-5[1m] | synthetic, n = 5000 | 1.0000 → 1.0000 | 0 / 1 / 1 / 0 |
<!-- quaestor:renderer:end -->

The subject of this report is the credit_default model package at version 1.0, a borrower-level credit scoring model whose output is the probability of default, and the report follows the structure of the Federal Reserve's model risk management guidance on model validation and monitoring [[reg:SR26-2:V]].

The subject was run by quaestor from the package manifest, under the declared wall-clock cap of 300 [[art:2ad8d1a5:runtime.max_seconds]] seconds, with the performance quantities below recomputed from the subject's own predictions rather than read from the developer's report.

Fitting used a training split of 3500 [[art:2510d49d:profile.train.n]] rows, and evaluation used a held-out test split of 1500 [[art:2193cf5f:profile.test.n]] rows.

Discrimination on test reaches an AUC of 0.7337 [[art:3255122a:metrics.test.auc]], above the developer-declared floor of 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]].

The Brier score on test is 0.1536 [[art:3cd28a53:metrics.test.brier]], below the developer-declared ceiling of 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]].

The calibration slope on test is 0.8701 [[art:7002f467:calibration_slope.test]], above the declared floor of 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] and below the declared ceiling of 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]], sitting nearer the floor than the ceiling.

The largest train-to-test population stability index is 0.02385 [[art:4a5ae1a0:psi.max]], below the declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].

On the evidence recomputed here, the model meets every performance and stability threshold the developer declared in the package manifest.

Meeting those declared thresholds is not the whole of the review, and outcomes analysis may still identify deviations that warrant adjustment, recalibration, or redevelopment [[reg:SR26-2:V.1.b]].

This validation raised F-001, a R1 regime stability finding at medium severity, and F-002, a E1 effective challenge finding at low severity.

Each is written out in full in section 6, and the severity breakdown is printed in the scope table above.

## 2. Conceptual soundness

Assessing conceptual soundness means assessing and documenting the model's design, key modelling choices and developmental evidence, with interpretability measures and benchmarking against an alternative model as practical means of doing so [[reg:SR26-2:V.1.a]].

The champion is a linear scorecard in logistic form, fitted on 3500 [[art:15071cdb:run.model_summary#n_train]] training rows, with an intercept of -1.397 [[art:15071cdb:run.model_summary#intercept]] and a coefficient on each retained feature.
Its declared feature inventory holds 12 [[art:abbb748e:run.features#n]] features.
Of these, 10 [[art:abbb748e:run.features#before_period_start]] are known before the performance period starts and 2 [[art:abbb748e:run.features#at_origination]] are known at origination.
The inventory places 0 [[art:abbb748e:run.features#during_period]] features inside the performance period and 0 [[art:abbb748e:run.features#after_outcome]] after the outcome, so on the declared timing nothing enters the score that is observed only after the event it predicts.

The developer's own collinearity screen removed the last billed amount and the rolling utilisation average before fitting.
Their variance inflation factors, 164.1 [[art:15071cdb:run.model_summary#removed.bill_last.vif]] and 38.98 [[art:15071cdb:run.model_summary#removed.utilisation_mean_6m.vif]], both sit above the screen's cut of 10 [[art:15071cdb:run.model_summary#vif_threshold]], which is the bound they were read against.
Both removals are redundancy against retained balance and utilisation terms rather than evidence about the outcome, and the retained specification is the one everything below is read on.

The largest coefficient by magnitude is on the most recent delinquency status, at 0.7518 [[art:15071cdb:run.model_summary#coefficients.delinq_last.value]], and its positive sign is what a credit reviewer expects: recent delinquency raises fitted default odds.
Utilisation carries the next largest positive weight at 0.2801 [[art:15071cdb:run.model_summary#coefficients.utilisation.value]], again in the expected direction, with higher drawn balance against limit raising risk.
The billed-amount level at -0.2543 [[art:15071cdb:run.model_summary#coefficients.bill_mean_6m.value]] and the billed-amount trend at -0.2207 [[art:15071cdb:run.model_summary#coefficients.bill_trend_6m.value]] are both negative, so on this fit a higher and a rising bill each reduce fitted risk, which is not the direction subject matter expects of exposure growth taken on its own.
The average payment ratio at -0.2204 [[art:15071cdb:run.model_summary#coefficients.pay_ratio_mean_6m.value]] and the latest payment ratio at -0.05754 [[art:15071cdb:run.model_summary#coefficients.pay_ratio_last.value]] are negative as expected, since paying down more of the bill lowers risk.
The remaining weights are small: the credit limit at 0.07934 [[art:15071cdb:run.model_summary#coefficients.limit_bal.value]], the delinquency count at 0.0638 [[art:15071cdb:run.model_summary#coefficients.delinq_count_6m.value]], the worst delinquency over the window at 0.03128 [[art:15071cdb:run.model_summary#coefficients.delinq_max_6m.value]], and age at -0.008833 [[art:15071cdb:run.model_summary#coefficients.age.value]].
A positive weight on the credit limit runs against the usual underwriting reading, in which a larger granted limit marks a stronger borrower.

The sign screen compares each fitted sign with the direction of that feature's own relationship with the outcome on train, and it counts 3 [[art:e223cd4a:sign_check.n_disagreements]] retained features where the two disagree.
These comparisons, and the ablation deltas below, are developmental evidence for the design judgement in this section; they are not findings and no rule was read against them.
The ablation deltas are measured from a refit of the champion's form on every retained feature, which scores 0.7337 [[art:89f9f36a:ablation.baseline_auc]] on test.

On age the fitted sign is -1 [[art:6172eb93:sign_check.age.coef_sign]] while its own direction on train is 1 [[art:cac34cd5:sign_check.age.univariate_direction]], so the screen records disagreement at 0 [[art:5c2c50b8:sign_check.age.agrees]].
Dropping age changes test AUC by -0.0005472 [[art:03f2c15c:ablation.age.delta_auc]], so the model is carrying only a little discrimination on the feature whose sign flipped, and the disagreement is materially small.
On the billed-amount level the fitted sign is -1 [[art:cee1a18f:sign_check.bill_mean_6m.coef_sign]] against an own direction of 1 [[art:82ba9862:sign_check.bill_mean_6m.univariate_direction]], recorded as disagreement at 0 [[art:4df8b747:sign_check.bill_mean_6m.agrees]].
Refitting without it changes test AUC by 0.005428 [[art:e4786496:ablation.bill_mean_6m.delta_auc]], a gain rather than a loss, so the sign flip sits on a term the refit does not need for discrimination and which appears to be acting as a correction on the other balance terms.
On the credit limit the fitted sign is 1 [[art:6af6aef2:sign_check.limit_bal.coef_sign]] against an own direction of -1 [[art:56d284d6:sign_check.limit_bal.univariate_direction]], recorded as disagreement at 0 [[art:0278aad1:sign_check.limit_bal.agrees]].
Refitting without the credit limit changes test AUC by 0.001337 [[art:5002902a:ablation.limit_bal.delta_auc]], again a gain, so this reversal too falls on a term the fitted form is not relying on for rank ordering.
Taken together, every sign reversal here lands on a feature whose removal either helps test discrimination or costs very little of it, which is the pattern of conditional suppression among correlated balance and demographic terms rather than a reversal in the features the score actually leans on.

The features the score does lean on agree with expectation.
The most recent delinquency status has a fitted sign of 1 [[art:50d352f8:sign_check.delinq_last.coef_sign]] matching its own direction of 1 [[art:a78648ba:sign_check.delinq_last.univariate_direction]], agreement recorded at 1 [[art:a8ba9372:sign_check.delinq_last.agrees]], and removing it changes test AUC by -0.08354 [[art:e986cd7d:ablation.delinq_last.delta_auc]], by far the largest loss among the ablations and the clearest evidence of where the model's discrimination comes from.
Utilisation agrees likewise at 1 [[art:d0c9a130:sign_check.utilisation.agrees]], with fitted sign 1 [[art:85badc3c:sign_check.utilisation.coef_sign]] and own direction 1 [[art:f0995196:sign_check.utilisation.univariate_direction]], and its removal changes test AUC by -0.006451 [[art:8621db24:ablation.utilisation.delta_auc]].
The delinquency count agrees at 1 [[art:a337d16b:sign_check.delinq_count_6m.agrees]] with a removal effect of -0.0007824 [[art:5db921e5:ablation.delinq_count_6m.delta_auc]], and the latest payment ratio agrees at 1 [[art:7837941a:sign_check.pay_ratio_last.agrees]] with a removal effect of -0.0004117 [[art:04295c71:ablation.pay_ratio_last.delta_auc]].
The worst delinquency over the window agrees at 1 [[art:da92a015:sign_check.delinq_max_6m.agrees]] but its removal changes test AUC by 0.0005906 [[art:76f922d7:ablation.delinq_max_6m.delta_auc]], the billed-amount trend agrees at 1 [[art:ff3cb24a:sign_check.bill_trend_6m.agrees]] with 0.002866 [[art:bb1f5508:ablation.bill_trend_6m.delta_auc]], and the average payment ratio agrees at 1 [[art:7e9a76ca:sign_check.pay_ratio_mean_6m.agrees]] with 0.001726 [[art:5cb2a089:ablation.pay_ratio_mean_6m.delta_auc]], so several correctly signed terms are nonetheless not earning their place on test.
The design is therefore interpretable and dominated by a delinquency signal in the expected direction, with a tail of balance and payment terms whose contribution is small and in places negative.

Effective challenge was exercised by benchmarking against an alternative form, which the guidance treats as a practical assessment for models of this kind [[reg:SR26-2:V.1.a]].
The challenger, a histogram gradient boosting model, reaches an AUC on test of 0.7898 [[art:2b3381be:challenger.auc]] against the champion's 0.7337 [[art:3255122a:metrics.test.auc]].
Stated as a difference in AUC rather than a ratio, the challenger's lead is 0.05613 [[art:9cbcc544:challenger.delta_auc]], which is above the effective-challenge threshold of 0.03 [[art:e042774c:threshold.E1.delta_auc]] that decides whether such a difference matters.
The Brier score points the same way, with the challenger at 0.1392 [[art:9599fce0:challenger.brier]] below the champion's 0.1536 [[art:3cd28a53:metrics.test.brier]], so the challenger is better on both discrimination and this accuracy measure.
This is finding E1, and because the challenger is fitted on the same subject data with a different functional form, the gap is evidence about the champion's functional form itself rather than about its inputs: the linear specification is leaving recoverable signal, most plausibly non-linearity and interaction among the delinquency and balance terms, on the table.
The findings section carries E1 and its disposition.

On the evidence reviewed here the champion's design is defensible in its timing, its collinearity screen and the direction of the terms it relies on, while the effective challenge shows its functional form is the weaker of the two compared.

## 3. Data integrity and drift

Sound development practice includes a critical assessment of data quality, relevance, and inputs alongside out-of-sample testing, and this section examines the splits on that basis [[reg:SR26-2:IV.1]].

### Missingness

The training split holds 3500 [[art:2510d49d:profile.train.n]] rows and the test split holds 1500 [[art:2193cf5f:profile.test.n]] rows.
The largest missing fraction of any column in train is 0 [[art:050a3099:profile.train.missing.max]].
The largest missing fraction of any column in test is 0 [[art:f813848d:profile.test.missing.max]].
The two maxima are equal, so no column can separate the splits on missingness at all, and the declared bound on the between-split missingness gap is 0.1 [[art:9cce25ea:threshold.D1.missing_gap]].
On absolute level the splits are alike, and because both maxima sit at the floor the comparison in ratio adds nothing beyond the comparison in difference.

### Population and characteristic stability

The declared stability bound is 0.25 [[art:278b9016:threshold.S1.psi]], and the package declares the same bound at 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
The largest train-to-test population stability index, with the score included, is 0.02385 [[art:4a5ae1a0:psi.max]], well below that bound.
The feature carrying that largest value is pay_ratio_mean_6m at 0.02385 [[art:e3761732:psi.pay_ratio_mean_6m]].
The remaining per-feature values sit below it:

- age, 0.01198 [[art:2e7b9ead:psi.age]]
- utilisation, 0.01248 [[art:3c68d5ee:psi.utilisation]]
- bill_trend_6m, 0.008579 [[art:b80e3091:psi.bill_trend_6m]]
- bill_mean_6m, 0.008018 [[art:a0afce85:psi.bill_mean_6m]]
- pay_ratio_last, 0.006835 [[art:96c52004:psi.pay_ratio_last]]
- limit_bal, 0.004676 [[art:09a00724:psi.limit_bal]]
- delinq_max_6m, 0.003729 [[art:b6668567:psi.delinq_max_6m]]
- delinq_last, 0.003062 [[art:7662ef2e:psi.delinq_last]]
- delinq_count_6m, 0.001414 [[art:4b7439f2:psi.delinq_count_6m]]

The score itself shifts less between the splits than the most-shifted input, at 0.006306 [[art:4a23b13e:psi.y_score]].

Characteristic stability, which attributes the shift in the linear predictor to individual inputs, peaks at 0.01811 [[art:28c0a604:csi.max]], again far below the declared stability bound of 0.25 [[art:278b9016:threshold.S1.psi]].
That peak belongs to delinq_last at 0.01811 [[art:c0b3fffe:csi.delinq_last]], with utilisation close behind at 0.01788 [[art:54e8c0d5:csi.utilisation]].
The other contributions are smaller:

- bill_mean_6m, 0.005952 [[art:4ceb65ea:csi.bill_mean_6m]]
- pay_ratio_mean_6m, 0.0045 [[art:adf83ef4:csi.pay_ratio_mean_6m]]
- bill_trend_6m, 0.0004864 [[art:93317930:csi.bill_trend_6m]]
- limit_bal, 0.0002442 [[art:443540b2:csi.limit_bal]]
- age, 0.0002175 [[art:0aad0eb8:csi.age]]
- delinq_max_6m, 0.0002075 [[art:0bc44634:csi.delinq_max_6m]]
- delinq_count_6m, 0.0001786 [[art:8359c176:csi.delinq_count_6m]]
- pay_ratio_last, 1.46e-05 [[art:e06dbc50:csi.pay_ratio_last]]

The ordering of the two screens differs: the input that moves most in distribution is not the input that contributes most to the shift in the linear predictor, and delinq_last ranks low on the former while ranking first on the latter.

### Leakage screens

Features declared as observed during the performance period or after the outcome number 0 [[art:742bcd24:leakage.timing.n_flagged]], so the declared timings raise nothing for review.
The strongest single feature reaches an AUC of 0.6841 [[art:f39d22de:leakage.target_corr.max_single_feature_auc]], below the bound of 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]] that one feature may reach on its own, which is the pattern expected of a genuine predictor rather than an echo of the target.

The contamination screen has two arms, each read against its own bound.
The identifier arm finds a share of 0 [[art:63d37fc5:leakage.overlap.ids]] of test rows whose client identifier also identifies a row of train, against the declared contamination bound of 0.005 [[art:9f336eaf:threshold.L2.overlap]].
The feature-vector arm finds a share of 0 [[art:0fec8048:leakage.overlap.features]] of test rows whose feature values also appear in train, against the bound the rule actually applied, 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].
That applied bound is the larger of the declared contamination bound and an allowance scaled to the duplicate rate within train, on the reasoning that two different subjects writing the same discrete row is coincidence rather than contamination.
The duplicate rate that feeds the allowance is 0 [[art:4474c227:leakage.duplicates.train]], the share of train rows whose feature values are not unique within train, so the allowance does not lift the applied bound above the declared one and the two coincide.
The overall share of test rows whose feature values also appear in train is likewise 0 [[art:4c9fcd09:leakage.overlap]], read against the applied feature-overlap bound of 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].
The name screen matches 0 [[art:407e62be:leakage.name_screen.n_matched]] feature names against the target-adjacent lexicon.

### Assessment

Both splits are complete on the columns screened, and the missingness comparison holds in difference and in ratio alike because neither split carries any.
Distributional movement between train and test is small relative to the declared bound on both the population and the characteristic view, and the score moves less than the most-shifted input.
Every leakage arm returns at or below its own bound, with the strongest single feature well short of the level at which a feature would be suspected of encoding the outcome.
The validator notes that the stability evidence here compares the training split against the test split, and that stability against data drawn after the development window bears on continued use rather than on the splits examined above.

## 4. Outcomes analysis

Outcomes analysis compares model output with the real-world outcomes the model is meant to anticipate, and this section reports that comparison for the model package credit_default version 1.0 [[reg:SR26-2:V.1.b]].
This section reports discrimination before calibration, because the observed event rate on the evaluation split is 0.224 [[art:5f15df2a:metrics.test.event_rate]], at or above 0.05 [[art:42f1351e:rule.calibration_first_event_rate]], the rate below which this report would lead with calibration instead.

The recomputed metrics on each split are as follows, one row per metric.

| Metric | Train | Test |
| --- | --- | --- |
| Rows | 3500 [[art:564683ee:metrics.train.n]] | 1500 [[art:64fcf14d:metrics.test.n]] |
| Event rate | 0.2243 [[art:8a78b455:metrics.train.event_rate]] | 0.224 [[art:5f15df2a:metrics.test.event_rate]] |
| Mean predicted | 0.2243 [[art:5ec77e91:metrics.train.mean_predicted]] | 0.2292 [[art:f067e003:metrics.test.mean_predicted]] |
| AUC | 0.769 [[art:197f9521:metrics.train.auc]] | 0.7337 [[art:3255122a:metrics.test.auc]] |
| Gini | 0.5381 [[art:4208816b:metrics.train.gini]] | 0.4673 [[art:621c8cf3:metrics.test.gini]] |
| KS | 0.4426 [[art:f1d489d8:metrics.train.ks]] | 0.4096 [[art:984fc4f0:metrics.test.ks]] |
| Brier | 0.1489 [[art:cf19f7b7:metrics.train.brier]] | 0.1536 [[art:3cd28a53:metrics.test.brier]] |
| Log loss | 0.4632 [[art:a2852b4a:metrics.train.logloss]] | 0.4788 [[art:1362ad67:metrics.test.logloss]] |

Rank-ordering on the evaluation split is set out by decile of predicted probability in the table below.

<!-- quaestor:renderer:begin table deciles.test -->
Decile separation on test; decile 1 holds the highest probabilities [[art:9212d403:deciles.test]]:

| decile | count | events | event_rate | lift |
|---|---|---|---|---|
| 1 | 150 | 78 | 0.52 | 2.321 |
| 2 | 150 | 68 | 0.4533 | 2.024 |
| 3 | 150 | 55 | 0.3667 | 1.637 |
| 4 | 150 | 36 | 0.24 | 1.071 |
| 5 | 150 | 21 | 0.14 | 0.625 |
| 6 | 150 | 19 | 0.1267 | 0.5655 |
| 7 | 150 | 16 | 0.1067 | 0.4762 |
| 8 | 150 | 13 | 0.08667 | 0.3869 |
| 9 | 150 | 13 | 0.08667 | 0.3869 |
| 10 | 150 | 17 | 0.1133 | 0.506 |
<!-- quaestor:renderer:end -->

The top two deciles hold 0.4345 [[art:c7670b9d:deciles.test.top2_capture]] of the events on test, below the corresponding share on train of 0.4459 [[art:0511095f:deciles.train.top2_capture]].

Discrimination is weaker on test than on train: AUC is 0.769 [[art:197f9521:metrics.train.auc]] on train against 0.7337 [[art:3255122a:metrics.test.auc]] on test, and that decline from train to test is judged against a bound of 0.08 [[art:630f28f4:threshold.O1.auc_gap]].
The test value stays above the developer-declared floor of 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]], and the test Brier score of 0.1536 [[art:3cd28a53:metrics.test.brier]] stays below the developer-declared ceiling of 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]].

Turning to calibration, the logistic regression of the outcome on the logit of the predicted probability gives a slope of 0.8701 [[art:7002f467:calibration_slope.test]] on test and 1.002 [[art:7e7849d9:calibration_slope.train]] on train, the test slope being the lower of the two.
The test slope sits inside the band running from 0.8 [[art:749634ae:threshold.C1.calibration_slope.min]] to 1.2 [[art:b6672579:threshold.C1.calibration_slope.max]], the same bounds the package declares at 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] and 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The intercept of that regression is -0.1809 [[art:386a6083:calibration_intercept.test]] on test and 0.002422 [[art:e1230838:calibration_intercept.train]] on train.
Mean predicted probability on test is 0.2292 [[art:f067e003:metrics.test.mean_predicted]] against an observed rate of 0.224 [[art:5f15df2a:metrics.test.event_rate]], predicted standing above observed.
The relative gap between those two is 0.02344 [[art:fd64775d:calibration.mean_rel_gap.test]], within the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
Comparing the two splits on that relative gap rather than on any absolute difference, the train value of 3.599e-05 [[art:ac0572fe:calibration.mean_rel_gap.train]] lies below the test value of 0.02344 [[art:fd64775d:calibration.mean_rel_gap.test]], so the level of the probabilities is looser out of sample than in sample while remaining inside the tolerance.

Calibration by decile of predicted probability on the evaluation split is set out below.

<!-- quaestor:renderer:begin table calibration.test -->
Calibration by decile of predicted probability on test [[art:28aa9ae3:calibration.test]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.08741 | 0.1133 | 150 |
| 2 | 0.1087 | 0.08667 | 150 |
| 3 | 0.1234 | 0.08667 | 150 |
| 4 | 0.139 | 0.1067 | 150 |
| 5 | 0.1557 | 0.1267 | 150 |
| 6 | 0.1769 | 0.14 | 150 |
| 7 | 0.2046 | 0.24 | 150 |
| 8 | 0.2666 | 0.3667 | 150 |
| 9 | 0.4026 | 0.4533 | 150 |
| 10 | 0.6276 | 0.52 | 150 |
<!-- quaestor:renderer:end -->

The bounds the package declares, each with its recomputed value and its outcome, are set out below as the tool computed them.

<!-- quaestor:renderer:begin table thresholds.evaluation -->
Every threshold package.yaml declares, with its bound, the recomputed value and the outcome [[art:d1a5d9c8:thresholds.evaluation]]:

| metric | split | bound | value | result |
|---|---|---|---|---|
| auc | test | minimum 0.7 | 0.7337 | pass |
| brier | test | maximum 0.2 | 0.1536 | pass |
| calibration_slope | test | minimum 0.8 | 0.8701 | pass |
| calibration_slope | test | maximum 1.2 | 0.8701 | pass |
| psi |  | maximum 0.25 | 0.02385 | pass |
<!-- quaestor:renderer:end -->

The table is the tool's own evaluation of every bound the developers declared, set against the values recomputed in this run, so it cannot diverge from the metrics and calibration results reported above.
Read alongside those results, it is this report's record of where the model stands against what its developers committed to.

### Follow-up analyses

The first follow-up step recomputed the full metric set on both splits for the sub-population `bill_trend_6m > median(bill_trend_6m)`.
It was asked because the coefficient on that feature reverses sign between regimes, and the question was whether that instability shows up on the outcomes side as degraded discrimination or calibration on the portion of the population the feature separates.

<!-- quaestor:renderer:begin table metrics.train.sub.bill_trend_6m_high -->
Every metric on the bill_trend_6m above_median slice of train [[art:5489c988:metrics.train.sub.bill_trend_6m_high]]:

| metric | value |
|---|---|
| n | 1750 |
| event_rate | 0.2229 |
| auc | 0.7733 |
| gini | 0.5465 |
| ks | 0.4669 |
| brier | 0.1451 |
| logloss | 0.4545 |
| mean_predicted | 0.2182 |
| mean_rel_gap | 0.0208 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.bill_trend_6m_high -->
Every metric on the bill_trend_6m above_median slice of test [[art:480cbefc:metrics.test.sub.bill_trend_6m_high]]:

| metric | value |
|---|---|
| n | 750 |
| event_rate | 0.2093 |
| auc | 0.7207 |
| gini | 0.4414 |
| ks | 0.4014 |
| brier | 0.1427 |
| logloss | 0.4537 |
| mean_predicted | 0.214 |
| mean_rel_gap | 0.02217 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

On test this sub-population's AUC falls 0.01294 [[art:97e3e918:metrics.test.sub.bill_trend_6m_high.auc_gap]] below the split's own, within the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] at which a sub-population would become an open item.
On train it falls -0.004217 [[art:44fe1e49:metrics.train.sub.bill_trend_6m_high.auc_gap]] below the split's own, that is, it stands above the split, and this is likewise within that bound.
The sub-population holds 0.5 [[art:31f43354:metrics.test.sub.bill_trend_6m_high.share]] of test and 0.5 [[art:35313c05:metrics.train.sub.bill_trend_6m_high.share]] of train, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] a sub-population must hold before it can raise an open item and below the share of 0.95 [[art:a928a05c:threshold.O1.slice_max_share]] at which it would be refused as the whole split.
Mean predicted on the test sub-population is 0.214 [[art:725cd1c7:metrics.test.sub.bill_trend_6m_high.mean_predicted]] against an observed rate of 0.2093 [[art:9a8a6f36:metrics.test.sub.bill_trend_6m_high.event_rate]], a relative gap of 0.02217 [[art:b2206639:metrics.test.sub.bill_trend_6m_high.mean_rel_gap]] that is within the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
On train the same comparison gives mean predicted of 0.2182 [[art:c1479a5f:metrics.train.sub.bill_trend_6m_high.mean_predicted]] against an observed rate of 0.2229 [[art:5c13b21d:metrics.train.sub.bill_trend_6m_high.event_rate]], a relative gap of 0.0208 [[art:dec79ccf:metrics.train.sub.bill_trend_6m_high.mean_rel_gap]].
Since the level comparison stays within tolerance on both splits and the ordering comparison stays within its own bound on both, this sub-population points to neither a weakness in the level of the probabilities nor one in their ordering.

The second follow-up step recomputed the same metric set on both splits for the complementary sub-population `bill_trend_6m <= median(bill_trend_6m)`.
It was asked so that the other side of the sign-reversing feature could be read as well, to tell whether the coefficient instability surfaces as an outcomes-side performance gap rather than only as an artefact of the fitted coefficients.

<!-- quaestor:renderer:begin table metrics.train.sub.bill_trend_6m_low -->
Every metric on the bill_trend_6m below_median slice of train [[art:61850b8b:metrics.train.sub.bill_trend_6m_low]]:

| metric | value |
|---|---|
| n | 1750 |
| event_rate | 0.2257 |
| auc | 0.764 |
| gini | 0.5279 |
| ks | 0.4226 |
| brier | 0.1526 |
| logloss | 0.472 |
| mean_predicted | 0.2303 |
| mean_rel_gap | 0.02046 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.bill_trend_6m_low -->
Every metric on the bill_trend_6m below_median slice of test [[art:064648eb:metrics.test.sub.bill_trend_6m_low]]:

| metric | value |
|---|---|
| n | 750 |
| event_rate | 0.2387 |
| auc | 0.7407 |
| gini | 0.4813 |
| ks | 0.4198 |
| brier | 0.1644 |
| logloss | 0.5039 |
| mean_predicted | 0.2445 |
| mean_rel_gap | 0.02455 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

On test this sub-population's AUC falls -0.006995 [[art:a6dacfd1:metrics.test.sub.bill_trend_6m_low.auc_gap]] below the split's own, that is, it stands above the split, within the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].
On train it falls 0.005086 [[art:51a4dd85:metrics.train.sub.bill_trend_6m_low.auc_gap]] below the split's own, also within that bound.
The sub-population holds 0.5 [[art:56a82f85:metrics.test.sub.bill_trend_6m_low.share]] of test and 0.5 [[art:1a2d7b50:metrics.train.sub.bill_trend_6m_low.share]] of train, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] and below the share of 0.95 [[art:a928a05c:threshold.O1.slice_max_share]] at which it would be refused.
Mean predicted on the test sub-population is 0.2445 [[art:11cfcac7:metrics.test.sub.bill_trend_6m_low.mean_predicted]] against an observed rate of 0.2387 [[art:4fa19590:metrics.test.sub.bill_trend_6m_low.event_rate]], a relative gap of 0.02455 [[art:855d5668:metrics.test.sub.bill_trend_6m_low.mean_rel_gap]] that is within the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
On train the comparison gives mean predicted of 0.2303 [[art:249e2db2:metrics.train.sub.bill_trend_6m_low.mean_predicted]] against an observed rate of 0.2257 [[art:1acba5e5:metrics.train.sub.bill_trend_6m_low.event_rate]], a relative gap of 0.02046 [[art:e2bddb91:metrics.train.sub.bill_trend_6m_low.mean_rel_gap]].
Here too the level comparison stays within tolerance and the ordering comparison within its bound, so neither the level of the probabilities nor their ordering is the weaker of the two on this sub-population.
Comparing the two sub-populations on test as differences from the split's own AUC, the above-median one at 0.01294 [[art:97e3e918:metrics.test.sub.bill_trend_6m_high.auc_gap]] is the further below the split and the below-median one at -0.006995 [[art:a6dacfd1:metrics.test.sub.bill_trend_6m_low.auc_gap]] stands above it, both within the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].
Comparing them on their relative level gaps on test, each already scaled by its own observed rate, the below-median value of 0.02455 [[art:855d5668:metrics.test.sub.bill_trend_6m_low.mean_rel_gap]] is above the above-median value of 0.02217 [[art:b2206639:metrics.test.sub.bill_trend_6m_high.mean_rel_gap]].

## 5. Sensitivity and scenario analysis

This section sets out the sensitivity and scenario evidence for the subject model package, as part of the critical analysis that validation applies to model design, key assumptions, variable selection and the developmental testing behind them [[reg:SR26-2:V.1.a]].
The superseded guidance states the expectation for these particular tests more directly, asking that sensitivity analysis check the effect of small changes in inputs and parameter values on model outputs, and that robustness and stability checks be repeated rather than treated as a one-off [[reg:SR11-7:V.1.a]].

### Multicollinearity among the retained features

The largest variance inflation factor among the retained features is 7.512 [[art:2d17cd9e:vif.max]], below the declared bound of 10 [[art:aeb4f33c:threshold.M1.vif]].
That largest value coincides with the mean bill amount feature, whose factor is 7.512 [[art:19127172:vif.bill_mean_6m]], with the last payment ratio at 7.213 [[art:a9b805e2:vif.pay_ratio_last]] and the mean payment ratio at 7.206 [[art:76a555ef:vif.pay_ratio_mean_6m]] just behind it.
The remaining retained features sit further from the bound: the credit limit at 4.832 [[art:f19a1ae6:vif.limit_bal]], utilisation at 3.408 [[art:87292dc8:vif.utilisation]], the delinquency count at 2.527 [[art:063976d6:vif.delinq_count_6m]], the maximum delinquency at 2.375 [[art:fa4a6cf4:vif.delinq_max_6m]], the most recent delinquency at 1.433 [[art:1d3a39df:vif.delinq_last]], the bill trend at 1.217 [[art:36ec368c:vif.bill_trend_6m]] and age at 1.003 [[art:193052e1:vif.age]].
Belsley's condition number of the column-standardised design is 5.647 [[art:8dc0c2f1:condition_number]], below the declared bound of 30 [[art:7e52fd7a:threshold.M1.condition_number]].
Both diagnostics therefore read below the bounds declared for them, though the billing and payment-ratio features cluster at the upper end of the observed factor range while the delinquency and demographic features sit well away from it.

### Stability across the declared regimes

The package declares a regime column, the application cohort, so the regime tests apply to this model and were run across those cohorts.

<!-- quaestor:renderer:begin table stability.auc_by_regime -->
The champion's AUC within each application_cohort on train [[art:395a801f:stability.auc_by_regime]]:

| regime | n | event_rate | auc |
|---|---|---|---|
| 2013 | 1734 | 0.2065 | 0.7382 |
| 2016 | 1766 | 0.2418 | 0.7963 |
<!-- quaestor:renderer:end -->

The declared bound on the AUC difference across regimes is 0.1 [[art:b64213d7:threshold.R1.auc_gap]], and it is the per-cohort discrimination values above that this bound is read against.
A sign flip is counted only where the feature is among the highest-ranked features and its coefficient exceeds 0.05 [[art:aca84377:threshold.R1.sign_flip_coef]] with a |z| reaching 2 [[art:2e4428c7:threshold.R1.sign_flip_z]] in each regime, so the test speaks to reversals that are both material and statistically resolved rather than to noise around zero.
On that definition the indicator reads 1 for the bill trend feature [[art:4dc17324:stability.bill_trend_6m.sign_flip]].
The indicator reads 0 for age [[art:af9b1d06:stability.age.sign_flip]], 0 for the mean bill amount [[art:df546086:stability.bill_mean_6m.sign_flip]], 0 for the delinquency count [[art:40d78102:stability.delinq_count_6m.sign_flip]], 0 for the most recent delinquency [[art:a7adedc7:stability.delinq_last.sign_flip]], 0 for the maximum delinquency [[art:908eec36:stability.delinq_max_6m.sign_flip]], 0 for the credit limit [[art:3a0e7e0d:stability.limit_bal.sign_flip]], 0 for the last payment ratio [[art:77aa667a:stability.pay_ratio_last.sign_flip]], 0 for the mean payment ratio [[art:f8da40ca:stability.pay_ratio_mean_6m.sign_flip]] and 0 for utilisation [[art:5b813a1b:stability.utilisation.sign_flip]].
The reversal on the bill trend feature is raised here as a finding (R1, regime stability, suggested severity medium): its coefficient changes sign across application cohorts while clearing both the coefficient and the |z| bounds cited above in every regime.
The direction of the bill trend effect is therefore not stable across cohorts, and reliance on that coefficient for explanation or for any cohort-specific use should be qualified accordingly, even though the collinearity diagnostics above give no indication that the feature's own factor is inflated.

### Rate-shock scenarios

The rate-shock scenarios do not apply to this model, because they are defined for hazard models and this subject is not one.
The value change at the extreme shocks, the monotonicity of the shock curve and the convexity read against the direction the package declares are accordingly listed in Appendix D as not applicable to this model type.
No shock grid was run for this package, and nothing in this section should be read as reporting the outcome of one.

## 6. Findings and recommendations

Findings are ordered by severity, the medium before the low, and each one below carries the recomputed values and the declared bounds its check fired against, so that the limitation is stated with the evidence that identifies it and with what corrective action may be warranted [[reg:SR26-2:V]].

### F-001 · R1 regime stability · severity **medium**

**The coefficient on `bill_trend_6m`, a top-ranked feature, reverses sign between application cohorts while staying large and sharply resolved in each of them, so the relationship the model fits to this feature does not hold across the regimes the model is applied in.**

The regime sign-reversal condition for this feature evaluates to 1 [[art:4dc17324:stability.bill_trend_6m.sign_flip]], which requires the per-regime refit coefficient to exceed the declared magnitude bound of 0.05 [[art:aca84377:threshold.R1.sign_flip_coef]] and to reach the declared absolute-z bound of 2 [[art:2e4428c7:threshold.R1.sign_flip_z]] in every regime while changing sign between them.

The per-regime standardised refit, with the standard error and z of each coefficient, is reproduced below.

<!-- quaestor:renderer:begin table stability.bill_trend_6m.coef_or_importance_by_regime -->
Bill_trend_6m's coefficient in a per-regime refit, standardised, with the standard error and z of each [[art:4114d577:stability.bill_trend_6m.coef_or_importance_by_regime]]:

| regime | coefficient | se | z |
|---|---|---|---|
| 2013 | 0.9089 | 0.117 | 7.766 |
| 2016 | -1.171 | 0.1052 | -11.13 |
<!-- quaestor:renderer:end -->

Because both cohort refits clear the magnitude bound and the significance bound, the validator concludes that the reversal is not an artefact of weak identification in one regime but a genuine change in the fitted direction, and that predictions for a cohort therefore inherit a direction estimated partly from a cohort where the direction is opposite.

The developer should establish whether the cohort variable belongs in the specification as an interaction or a stratification, re-estimate with that structure, and if the reversal survives, either drop the feature or document the cohort range over which the fitted direction is asserted to hold and constrain use accordingly.

### F-002 · E1 effective challenge · severity **low**

**A routine hist_gradient_boosting challenger outperforms the champion on the test split by more than the margin the effective-challenge rule tolerates, so the champion's functional form is not supported as the best available for this use.**

The challenger reaches an AUC on test of 0.7898 [[art:2b3381be:challenger.auc]] against the champion's recomputed 0.7337 [[art:3255122a:metrics.test.auc]].

The comparison the rule makes is the difference between the two, which is 0.05613 [[art:9cbcc544:challenger.delta_auc]] and lies above the declared effective-challenge bound of 0.03 [[art:e042774c:threshold.E1.delta_auc]].

The validator concludes that discriminatory power is being left on the table by the chosen specification rather than by the data, and that the loss is large enough to require a stated reason for keeping the champion.

The developer should either record the interpretability, stability or implementation grounds on which the champion is preferred despite the gap, or bring the challenger forward as a candidate and subject it to the same validation, noting that the regime instability in F-001 is one such ground only if it is shown to be absent from the challenger.

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1, S1), `compute_metrics` (T1, C1, O1), `check_leakage` (L1, L2), `check_collinearity` (M1).

### Open items

- Why does the fitted coefficient on `age` carry sign -1 [[art:6172eb93:sign_check.age.coef_sign]] where that feature's own single-feature direction on train is 1 [[art:cac34cd5:sign_check.age.univariate_direction]], a disagreement the sign check flags as 0 [[art:5c2c50b8:sign_check.age.agrees]], and what does the model discriminate on in age once the features correlated with it are held fixed — owner: model developer.
- Why does the fitted coefficient on `bill_mean_6m` carry sign -1 [[art:cee1a18f:sign_check.bill_mean_6m.coef_sign]] where that feature's own single-feature direction on train is 1 [[art:82ba9862:sign_check.bill_mean_6m.univariate_direction]], a disagreement the sign check flags as 0 [[art:4df8b747:sign_check.bill_mean_6m.agrees]], and what does the model discriminate on in billed amount once the exposure and repayment features correlated with it are held fixed — owner: model developer.
- Why does the fitted coefficient on `limit_bal` carry sign 1 [[art:6af6aef2:sign_check.limit_bal.coef_sign]] where that feature's own single-feature direction on train is -1 [[art:56d284d6:sign_check.limit_bal.univariate_direction]], a disagreement the sign check flags as 0 [[art:0278aad1:sign_check.limit_bal.agrees]], and what does the model discriminate on in the credit limit once the features correlated with it are held fixed — owner: model developer.

## 7. Ongoing monitoring recommendations

Ongoing monitoring evaluates the extent to which this model continues to perform as expected given potential changes in products, exposures, activities, clients, data relevance, or market conditions, and it is the mechanism by which the limitations recorded in this report are reassessed over time [[reg:SR26-2:V.2]].

### Quantities, frequencies, and bounds

The monitoring plan should recompute the same quantities this validation checked, on each production vintage, against the bounds already declared in the package rather than against new ones introduced at monitoring time.

Rank-ordering performance should be recomputed on each scored cohort once outcomes mature and compared with the declared floor of 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]], the bound against which the evaluation-split value of 0.7337 [[art:3255122a:metrics.test.auc]] was assessed here.
Because the evaluation-split value sits above that floor but within the range where ordinary vintage-to-vintage variation could carry it down to the floor, a quarterly cadence for this quantity is appropriate, with escalation on the first cohort that reaches or crosses the floor rather than on a trailing average alone.

Probabilistic accuracy should be recomputed on the same cadence and compared with the declared ceiling of 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]], the bound under which the evaluation-split value of 0.1536 [[art:3cd28a53:metrics.test.brier]] fell.

The regression of the outcome on the logit of the predicted probability should be refitted on each cohort and compared with the declared band whose lower edge is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] and whose upper edge is 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The evaluation-split slope of 0.8701 [[art:7002f467:calibration_slope.test]] lies above the lower edge and below the upper edge, and monitoring should treat movement toward either edge as grounds for review, since drift downward and drift upward carry different consequences for how scores are used in cutoffs and pricing.
When the slope leaves the declared band on a cohort, the response should be considered in the terms the guidance sets out for persistent deviations outside established performance thresholds: overlay, recalibration, or redevelopment [[reg:SR26-2:V.1.b]].

Population shift should be recomputed monthly, at a higher frequency than the outcome-dependent quantities above, because it can be measured before outcomes mature and therefore serves as the early indicator for the rest of the panel.
The comparison population should be the production vintage against the development population, and the bound remains the declared cap of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]], against which the largest train-to-test shift observed here, 0.02385 [[art:4a5ae1a0:psi.max]], was assessed.
Monitoring should report the per-feature shifts and the score shift separately rather than the maximum alone, and should state for each cohort whether it is reporting the shift of a feature or of the score, so that a moving score distribution is not masked by stable inputs or the reverse.

### Ordering of the monitoring report

This report ordered discrimination ahead of calibration for the evaluation split, because the observed event rate on that split was at or above 0.05 [[art:42f1351e:rule.calibration_first_event_rate]].
For any future cohort whose observed event rate falls below 0.05 [[art:42f1351e:rule.calibration_first_event_rate]], the monitoring report covering that cohort should lead with calibration instead, since at low event rates the absolute accuracy of the predicted probabilities, not the rank-ordering, is what governs whether the scores can still be read as probabilities.
The monitoring report should record the observed event rate for each cohort alongside that bound, so the ordering decision is auditable rather than implicit.

### Benchmarking

This validation compared the champion with a challenger, and monitoring should extend that comparison in the way development data cannot: by refitting the challenger on production vintages and comparing its outputs with the champion's on the same cohorts.
That is the benchmark meant here — the challenger refitted on production vintages, not an external or vendor reference — because it isolates the effect of the newer data from the effect of a different modeling approach.
Discrepancies between the champion and the refitted challenger should trigger investigation into the sources and degree of the differences and an examination of whether they fall within an expected range given the nature of the comparison, and close agreement should be interpreted with caution rather than taken as confirmation [[reg:SR11-7:V.1.b]].

### What this validation could not cover

This validation was conducted on fixed development and evaluation splits, so it could not observe the model's behavior on cohorts booked after those splits, and monitoring must supply that evidence through back-testing over the full performance window rather than through holdout analysis alone.
Process verification was outside the scope of the checks reported here: whether the production scoring code reproduces the validated model, whether the input feeds remain accurate and complete, and whether changes to either are logged and controlled are matters monitoring should verify on an ongoing basis [[reg:SR11-7:V.1.b]].
User overrides of model output cannot be observed before deployment, and monitoring should track the override rate and the realized performance of overridden cases, since a high override rate or overrides that consistently improve outcomes indicates the model itself needs revision.
Stability of performance across sub-populations over time is likewise something a static evaluation split cannot establish; monitoring should report sub-population results cohort by cohort, and when it compares a gap across sub-populations it should state whether it is reporting the difference or the ratio, because sub-populations with matching absolute gaps can differ materially on the ratio.
The frequency and scope of these reports should be revisited as the model's materiality, the availability of new data, and the availability of new modeling approaches change, and the plan itself should be reassessed at each periodic review rather than fixed at approval [[reg:SR26-2:V.2]].

## Appendix A — Claims

Grounding precision 1.0000 before repair (239 of 239 claims verified) and 1.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 12/12; conceptual_soundness 58/58; data_integrity 42/42; outcomes 73/73; sensitivity 27/27; findings 16/16; monitoring 11/11.

Developer claims: The package declares 2 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). See Appendix D.

Excluded numeric tokens (not claims): section_number (section 6); citation_hash (2ad8d1a5, 2510d49d, 2193cf5f, 3255122a); regulatory_section_id (SR26-2:V, SR26-2:V.1.b, SR26-2:V.1.a, SR26-2:IV.1); finding_id (F-001, F-002); package_version (1.0); extractor_returned_excluded_token (1.0, 6,, 26.0, 2).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The subject was run by quaestor from the package manifest, u… | 300 | ratio | runtime.max_seconds |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 2 | summary | Fitting used a training split of 3500 rows, and evaluation u… | 3500 | count | n | train | eq | `[[art:2510d49d:profile.train.n]]` | verified | 3500 |
| 3 | summary | Fitting used a training split of 3500 rows, and evaluation u… | 1500 | count | n | test | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 4 | summary | Discrimination on test reaches an AUC of 0.7337 , above the… | 0.7337 | ratio | auc | test | eq | `[[art:3255122a:metrics.test.auc]]` | verified | 0.7336641916 |
| 5 | summary | Discrimination on test reaches an AUC of 0.7337 , above the… | 0.7 | ratio | auc | test | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 6 | summary | The Brier score on test is 0.1536 , below the developer-decl… | 0.1536 | ratio | brier | test | eq | `[[art:3cd28a53:metrics.test.brier]]` | verified | 0.1535518185 |
| 7 | summary | The Brier score on test is 0.1536 , below the developer-decl… | 0.2 | ratio | brier | test | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 8 | summary | The calibration slope on test is 0.8701 , above the declared… | 0.8701 | ratio | calibration_slope | test | eq | `[[art:7002f467:calibration_slope.test]]` | verified | 0.8701260273 |
| 9 | summary | The calibration slope on test is 0.8701 , above the declared… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 10 | summary | The calibration slope on test is 0.8701 , above the declared… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 11 | summary | The largest train-to-test population stability index is 0.02… | 0.02385 | ratio | psi |  | eq | `[[art:4a5ae1a0:psi.max]]` | verified | 0.02385256621 |
| 12 | summary | The largest train-to-test population stability index is 0.02… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 13 | conceptual_soundness | The champion is a linear scorecard in logistic form, fitted… | 3500 | count | n_train | train | eq | `[[art:15071cdb:run.model_summary#n_train]]` | verified | 3500 |
| 14 | conceptual_soundness | The champion is a linear scorecard in logistic form, fitted… | -1.397 | ratio | intercept |  | eq | `[[art:15071cdb:run.model_summary#intercept]]` | verified | -1.396666676 |
| 15 | conceptual_soundness | Its declared feature inventory holds 12 features. | 12 | count | n_features |  | eq | `[[art:abbb748e:run.features#n]]` | verified | 12 |
| 16 | conceptual_soundness | Of these, 10 are known before the performance period starts… | 10 | count | before_period_start |  | eq | `[[art:abbb748e:run.features#before_period_start]]` | verified | 10 |
| 17 | conceptual_soundness | Of these, 10 are known before the performance period starts… | 2 | count | at_origination |  | eq | `[[art:abbb748e:run.features#at_origination]]` | verified | 2 |
| 18 | conceptual_soundness | The inventory places 0 features inside the performance perio… | 0 | count | during_period |  | eq | `[[art:abbb748e:run.features#during_period]]` | verified | 0 |
| 19 | conceptual_soundness | The inventory places 0 features inside the performance perio… | 0 | count | after_outcome |  | eq | `[[art:abbb748e:run.features#after_outcome]]` | verified | 0 |
| 20 | conceptual_soundness | Their variance inflation factors, 164.1 and 38.98 , both sit… | 164.1 | ratio | vif |  | eq | `[[art:15071cdb:run.model_summary#removed.bill_last.vif]]` | verified | 164.111678 |
| 21 | conceptual_soundness | Their variance inflation factors, 164.1 and 38.98 , both sit… | 38.98 | ratio | vif |  | eq | `[[art:15071cdb:run.model_summary#removed.utilisation_mean_6m.vif]]` | verified | 38.981169 |
| 22 | conceptual_soundness | Their variance inflation factors, 164.1 and 38.98 , both sit… | 10 | ratio | vif_threshold |  | eq | `[[art:15071cdb:run.model_summary#vif_threshold]]` | verified | 10 |
| 23 | conceptual_soundness | The largest coefficient by magnitude is on the most recent d… | 0.7518 | ratio | coefficient |  | eq | `[[art:15071cdb:run.model_summary#coefficients.delinq_last.value]]` | verified | 0.7517560606 |
| 24 | conceptual_soundness | Utilisation carries the next largest positive weight at 0.28… | 0.2801 | ratio | coefficient |  | eq | `[[art:15071cdb:run.model_summary#coefficients.utilisation.value]]` | verified | 0.280140069 |
| 25 | conceptual_soundness | The billed-amount level at -0.2543 and the billed-amount tre… | -0.2543 | ratio | coefficient |  | eq | `[[art:15071cdb:run.model_summary#coefficients.bill_mean_6m.value]]` | verified | -0.2542857667 |
| 26 | conceptual_soundness | The billed-amount level at -0.2543 and the billed-amount tre… | -0.2207 | ratio | coefficient |  | eq | `[[art:15071cdb:run.model_summary#coefficients.bill_trend_6m.value]]` | verified | -0.2207143578 |
| 27 | conceptual_soundness | The average payment ratio at -0.2204 and the latest payment… | -0.2204 | ratio | coefficient |  | eq | `[[art:15071cdb:run.model_summary#coefficients.pay_ratio_mean_6m.value]]` | verified | -0.2203592118 |
| 28 | conceptual_soundness | The average payment ratio at -0.2204 and the latest payment… | -0.05754 | ratio | coefficient |  | eq | `[[art:15071cdb:run.model_summary#coefficients.pay_ratio_last.value]]` | verified | -0.05753914749 |
| 29 | conceptual_soundness | The remaining weights are small: the credit limit at 0.07934… | 0.07934 | ratio | coefficient |  | eq | `[[art:15071cdb:run.model_summary#coefficients.limit_bal.value]]` | verified | 0.07933978186 |
| 30 | conceptual_soundness | The remaining weights are small: the credit limit at 0.07934… | 0.0638 | ratio | coefficient |  | eq | `[[art:15071cdb:run.model_summary#coefficients.delinq_count_6m.value]]` | verified | 0.06379577362 |
| 31 | conceptual_soundness | The remaining weights are small: the credit limit at 0.07934… | 0.03128 | ratio | coefficient |  | eq | `[[art:15071cdb:run.model_summary#coefficients.delinq_max_6m.value]]` | verified | 0.03128476916 |
| 32 | conceptual_soundness | The remaining weights are small: the credit limit at 0.07934… | -0.008833 | ratio | coefficient |  | eq | `[[art:15071cdb:run.model_summary#coefficients.age.value]]` | verified | -0.008833428765 |
| 33 | conceptual_soundness | The sign screen compares each fitted sign with the direction… | 3 | count | n_disagreements |  | eq | `[[art:e223cd4a:sign_check.n_disagreements]]` | verified | 3 |
| 34 | conceptual_soundness | The ablation deltas are measured from a refit of the champio… | 0.7337 | ratio | auc | test | eq | `[[art:89f9f36a:ablation.baseline_auc]]` | verified | 0.7336641916 |
| 35 | conceptual_soundness | On age the fitted sign is -1 while its own direction on trai… | -1 | ratio | coef_sign |  | eq | `[[art:6172eb93:sign_check.age.coef_sign]]` | verified | -1 |
| 36 | conceptual_soundness | On age the fitted sign is -1 while its own direction on trai… | 1 | ratio | univariate_direction | train | eq | `[[art:cac34cd5:sign_check.age.univariate_direction]]` | verified | 1 |
| 37 | conceptual_soundness | On age the fitted sign is -1 while its own direction on trai… | 0 | ratio | agrees |  | eq | `[[art:5c2c50b8:sign_check.age.agrees]]` | verified | 0 |
| 38 | conceptual_soundness | Dropping age changes test AUC by -0.0005472 , so the model i… | -0.0005472 | ratio | delta_auc | test | eq | `[[art:03f2c15c:ablation.age.delta_auc]]` | verified | -0.0005471690394 |
| 39 | conceptual_soundness | On the billed-amount level the fitted sign is -1 against an… | -1 | ratio | coef_sign |  | eq | `[[art:cee1a18f:sign_check.bill_mean_6m.coef_sign]]` | verified | -1 |
| 40 | conceptual_soundness | On the billed-amount level the fitted sign is -1 against an… | 1 | ratio | univariate_direction |  | eq | `[[art:82ba9862:sign_check.bill_mean_6m.univariate_direction]]` | verified | 1 |
| 41 | conceptual_soundness | On the billed-amount level the fitted sign is -1 against an… | 0 | ratio | agrees |  | eq | `[[art:4df8b747:sign_check.bill_mean_6m.agrees]]` | verified | 0 |
| 42 | conceptual_soundness | Refitting without it changes test AUC by 0.005428 , a gain r… | 0.005428 | ratio | delta_auc | test | eq | `[[art:e4786496:ablation.bill_mean_6m.delta_auc]]` | verified | 0.005428223695 |
| 43 | conceptual_soundness | On the credit limit the fitted sign is 1 against an own dire… | 1 | ratio | coef_sign |  | eq | `[[art:6af6aef2:sign_check.limit_bal.coef_sign]]` | verified | 1 |
| 44 | conceptual_soundness | On the credit limit the fitted sign is 1 against an own dire… | -1 | ratio | univariate_direction |  | eq | `[[art:56d284d6:sign_check.limit_bal.univariate_direction]]` | verified | -1 |
| 45 | conceptual_soundness | On the credit limit the fitted sign is 1 against an own dire… | 0 | ratio | agrees |  | eq | `[[art:0278aad1:sign_check.limit_bal.agrees]]` | verified | 0 |
| 46 | conceptual_soundness | Refitting without the credit limit changes test AUC by 0.001… | 0.001337 | ratio | delta_auc | test | eq | `[[art:5002902a:ablation.limit_bal.delta_auc]]` | verified | 0.001337240223 |
| 47 | conceptual_soundness | The most recent delinquency status has a fitted sign of 1 ma… | 1 | ratio | coef_sign |  | eq | `[[art:50d352f8:sign_check.delinq_last.coef_sign]]` | verified | 1 |
| 48 | conceptual_soundness | The most recent delinquency status has a fitted sign of 1 ma… | 1 | ratio | univariate_direction |  | eq | `[[art:a78648ba:sign_check.delinq_last.univariate_direction]]` | verified | 1 |
| 49 | conceptual_soundness | The most recent delinquency status has a fitted sign of 1 ma… | 1 | ratio | agrees |  | eq | `[[art:a8ba9372:sign_check.delinq_last.agrees]]` | verified | 1 |
| 50 | conceptual_soundness | The most recent delinquency status has a fitted sign of 1 ma… | -0.08354 | ratio | delta_auc | test | eq | `[[art:e986cd7d:ablation.delinq_last.delta_auc]]` | verified | -0.08354299624 |
| 51 | conceptual_soundness | Utilisation agrees likewise at 1 , with fitted sign 1 and ow… | 1 | ratio | agrees |  | eq | `[[art:d0c9a130:sign_check.utilisation.agrees]]` | verified | 1 |
| 52 | conceptual_soundness | Utilisation agrees likewise at 1 , with fitted sign 1 and ow… | 1 | ratio | coef_sign |  | eq | `[[art:85badc3c:sign_check.utilisation.coef_sign]]` | verified | 1 |
| 53 | conceptual_soundness | Utilisation agrees likewise at 1 , with fitted sign 1 and ow… | 1 | ratio | univariate_direction |  | eq | `[[art:f0995196:sign_check.utilisation.univariate_direction]]` | verified | 1 |
| 54 | conceptual_soundness | Utilisation agrees likewise at 1 , with fitted sign 1 and ow… | -0.006451 | ratio | delta_auc | test | eq | `[[art:8621db24:ablation.utilisation.delta_auc]]` | verified | -0.006450969563 |
| 55 | conceptual_soundness | The delinquency count agrees at 1 with a removal effect of -… | 1 | ratio | agrees |  | eq | `[[art:a337d16b:sign_check.delinq_count_6m.agrees]]` | verified | 1 |
| 56 | conceptual_soundness | The delinquency count agrees at 1 with a removal effect of -… | -0.0007824 | ratio | delta_auc | test | eq | `[[art:5db921e5:ablation.delinq_count_6m.delta_auc]]` | verified | -0.0007824005891 |
| 57 | conceptual_soundness | The delinquency count agrees at 1 with a removal effect of -… | 1 | ratio | agrees |  | eq | `[[art:7837941a:sign_check.pay_ratio_last.agrees]]` | verified | 1 |
| 58 | conceptual_soundness | The delinquency count agrees at 1 with a removal effect of -… | -0.0004117 | ratio | delta_auc | test | eq | `[[art:04295c71:ablation.pay_ratio_last.delta_auc]]` | verified | -0.0004116552119 |
| 59 | conceptual_soundness | The worst delinquency over the window agrees at 1 but its re… | 1 | ratio | agrees |  | eq | `[[art:da92a015:sign_check.delinq_max_6m.agrees]]` | verified | 1 |
| 60 | conceptual_soundness | The worst delinquency over the window agrees at 1 but its re… | 0.0005906 | ratio | delta_auc | test | eq | `[[art:76f922d7:ablation.delinq_max_6m.delta_auc]]` | verified | 0.0005906357388 |
| 61 | conceptual_soundness | The worst delinquency over the window agrees at 1 but its re… | 1 | ratio | agrees |  | eq | `[[art:ff3cb24a:sign_check.bill_trend_6m.agrees]]` | verified | 1 |
| 62 | conceptual_soundness | The worst delinquency over the window agrees at 1 but its re… | 0.002866 | ratio | delta_auc | test | eq | `[[art:bb1f5508:ablation.bill_trend_6m.delta_auc]]` | verified | 0.002866245295 |
| 63 | conceptual_soundness | The worst delinquency over the window agrees at 1 but its re… | 1 | ratio | agrees |  | eq | `[[art:7e9a76ca:sign_check.pay_ratio_mean_6m.agrees]]` | verified | 1 |
| 64 | conceptual_soundness | The worst delinquency over the window agrees at 1 but its re… | 0.001726 | ratio | delta_auc | test | eq | `[[art:5cb2a089:ablation.pay_ratio_mean_6m.delta_auc]]` | verified | 0.001725883652 |
| 65 | conceptual_soundness | The challenger, a histogram gradient boosting model, reaches… | 0.7898 | ratio | auc | test | eq | `[[art:2b3381be:challenger.auc]]` | verified | 0.7897950417 |
| 66 | conceptual_soundness | The challenger, a histogram gradient boosting model, reaches… | 0.7337 | ratio | auc | test | eq | `[[art:3255122a:metrics.test.auc]]` | verified | 0.7336641916 |
| 67 | conceptual_soundness | Stated as a difference in AUC rather than a ratio, the chall… | 0.05613 | ratio | delta_auc | test | eq | `[[art:9cbcc544:challenger.delta_auc]]` | verified | 0.05613085011 |
| 68 | conceptual_soundness | Stated as a difference in AUC rather than a ratio, the chall… | 0.03 | ratio | delta_auc |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 69 | conceptual_soundness | The Brier score points the same way, with the challenger at… | 0.1392 | ratio | brier | test | eq | `[[art:9599fce0:challenger.brier]]` | verified | 0.1391775952 |
| 70 | conceptual_soundness | The Brier score points the same way, with the challenger at… | 0.1536 | ratio | brier | test | eq | `[[art:3cd28a53:metrics.test.brier]]` | verified | 0.1535518185 |
| 71 | data_integrity | The training split holds 3500 rows and the test split holds… | 3500 | count | n | train | eq | `[[art:2510d49d:profile.train.n]]` | verified | 3500 |
| 72 | data_integrity | The training split holds 3500 rows and the test split holds… | 1500 | count | n | test | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 73 | data_integrity | The largest missing fraction of any column in train is 0 . | 0 | ratio | missing | train | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 74 | data_integrity | The largest missing fraction of any column in test is 0 . | 0 | ratio | missing | test | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 75 | data_integrity | The two maxima are equal, so no column can separate the spli… | 0.1 | ratio | missing_gap |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 76 | data_integrity | The declared stability bound is 0.25 , and the package decla… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 77 | data_integrity | The declared stability bound is 0.25 , and the package decla… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 78 | data_integrity | The largest train-to-test population stability index, with t… | 0.02385 | ratio | psi |  | eq | `[[art:4a5ae1a0:psi.max]]` | verified | 0.02385256621 |
| 79 | data_integrity | The feature carrying that largest value is pay_ratio_mean_6m… | 0.02385 | ratio | psi |  | eq | `[[art:e3761732:psi.pay_ratio_mean_6m]]` | verified | 0.02385256621 |
| 80 | data_integrity | - age, 0.01198 | 0.01198 | ratio | psi |  | eq | `[[art:2e7b9ead:psi.age]]` | verified | 0.01198203437 |
| 81 | data_integrity | - utilisation, 0.01248 | 0.01248 | ratio | psi |  | eq | `[[art:3c68d5ee:psi.utilisation]]` | verified | 0.01247544421 |
| 82 | data_integrity | - bill_trend_6m, 0.008579 | 0.008579 | ratio | psi |  | eq | `[[art:b80e3091:psi.bill_trend_6m]]` | verified | 0.008579333007 |
| 83 | data_integrity | - bill_mean_6m, 0.008018 | 0.008018 | ratio | psi |  | eq | `[[art:a0afce85:psi.bill_mean_6m]]` | verified | 0.00801839524 |
| 84 | data_integrity | - pay_ratio_last, 0.006835 | 0.006835 | ratio | psi |  | eq | `[[art:96c52004:psi.pay_ratio_last]]` | verified | 0.006835339118 |
| 85 | data_integrity | - limit_bal, 0.004676 | 0.004676 | ratio | psi |  | eq | `[[art:09a00724:psi.limit_bal]]` | verified | 0.004675866811 |
| 86 | data_integrity | - delinq_max_6m, 0.003729 | 0.003729 | ratio | psi |  | eq | `[[art:b6668567:psi.delinq_max_6m]]` | verified | 0.00372909277 |
| 87 | data_integrity | - delinq_last, 0.003062 | 0.003062 | ratio | psi |  | eq | `[[art:7662ef2e:psi.delinq_last]]` | verified | 0.003062063118 |
| 88 | data_integrity | - delinq_count_6m, 0.001414 | 0.001414 | ratio | psi |  | eq | `[[art:4b7439f2:psi.delinq_count_6m]]` | verified | 0.001413525134 |
| 89 | data_integrity | The score itself shifts less between the splits than the mos… | 0.006306 | ratio | psi |  | eq | `[[art:4a23b13e:psi.y_score]]` | verified | 0.006306336141 |
| 90 | data_integrity | Characteristic stability, which attributes the shift in the… | 0.01811 | ratio | csi |  | eq | `[[art:28c0a604:csi.max]]` | verified | 0.01811466703 |
| 91 | data_integrity | Characteristic stability, which attributes the shift in the… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 92 | data_integrity | That peak belongs to delinq_last at 0.01811 , with utilisati… | 0.01811 | ratio | csi |  | eq | `[[art:c0b3fffe:csi.delinq_last]]` | verified | 0.01811466703 |
| 93 | data_integrity | That peak belongs to delinq_last at 0.01811 , with utilisati… | 0.01788 | ratio | csi |  | eq | `[[art:54e8c0d5:csi.utilisation]]` | verified | 0.01787504902 |
| 94 | data_integrity | - bill_mean_6m, 0.005952 | 0.005952 | ratio | csi |  | eq | `[[art:4ceb65ea:csi.bill_mean_6m]]` | verified | 0.00595223424 |
| 95 | data_integrity | - pay_ratio_mean_6m, 0.0045 | 0.0045 | ratio | csi |  | eq | `[[art:adf83ef4:csi.pay_ratio_mean_6m]]` | verified | 0.004500399242 |
| 96 | data_integrity | - bill_trend_6m, 0.0004864 | 0.0004864 | ratio | csi |  | eq | `[[art:93317930:csi.bill_trend_6m]]` | verified | 0.0004863886573 |
| 97 | data_integrity | - limit_bal, 0.0002442 | 0.0002442 | ratio | csi |  | eq | `[[art:443540b2:csi.limit_bal]]` | verified | 0.0002441546194 |
| 98 | data_integrity | - age, 0.0002175 | 0.0002175 | ratio | csi |  | eq | `[[art:0aad0eb8:csi.age]]` | verified | 0.0002174582447 |
| 99 | data_integrity | - delinq_max_6m, 0.0002075 | 0.0002075 | ratio | csi |  | eq | `[[art:0bc44634:csi.delinq_max_6m]]` | verified | 0.0002075152658 |
| 100 | data_integrity | - delinq_count_6m, 0.0001786 | 0.0001786 | ratio | csi |  | eq | `[[art:8359c176:csi.delinq_count_6m]]` | verified | 0.0001785733233 |
| 101 | data_integrity | - pay_ratio_last, 1.46e-05 | 1.46e-05 | ratio | csi |  | eq | `[[art:e06dbc50:csi.pay_ratio_last]]` | verified | 1.459725993e-05 |
| 102 | data_integrity | Features declared as observed during the performance period… | 0 | count | n_flagged |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 103 | data_integrity | The strongest single feature reaches an AUC of 0.6841 , belo… | 0.6841 | ratio | auc |  | eq | `[[art:f39d22de:leakage.target_corr.max_single_feature_auc]]` | verified | 0.6841001279 |
| 104 | data_integrity | The strongest single feature reaches an AUC of 0.6841 , belo… | 0.9 | ratio | auc |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 105 | data_integrity | The identifier arm finds a share of 0 of test rows whose cli… | 0 | ratio | overlap |  | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 106 | data_integrity | The identifier arm finds a share of 0 of test rows whose cli… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 107 | data_integrity | The feature-vector arm finds a share of 0 of test rows whose… | 0 | ratio | overlap |  | eq | `[[art:0fec8048:leakage.overlap.features]]` | verified | 0 |
| 108 | data_integrity | The feature-vector arm finds a share of 0 of test rows whose… | 0.005 | ratio | overlap |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 109 | data_integrity | The duplicate rate that feeds the allowance is 0 , the share… | 0 | ratio | duplicates | train | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 110 | data_integrity | The overall share of test rows whose feature values also app… | 0 | ratio | overlap |  | eq | `[[art:4c9fcd09:leakage.overlap]]` | verified | 0 |
| 111 | data_integrity | The overall share of test rows whose feature values also app… | 0.005 | ratio | overlap |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 112 | data_integrity | The name screen matches 0 feature names against the target-a… | 0 | count | n_matched |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 113 | outcomes | This section reports discrimination before calibration, beca… | 0.224 | ratio | event_rate | test | eq | `[[art:5f15df2a:metrics.test.event_rate]]` | verified | 0.224 |
| 114 | outcomes | This section reports discrimination before calibration, beca… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 115 | outcomes | \| Rows \| 3500 \| 1500 \| | 3500 | count | n | train | eq | `[[art:564683ee:metrics.train.n]]` | verified | 3500 |
| 116 | outcomes | \| Rows \| 3500 \| 1500 \| | 1500 | count | n | test | eq | `[[art:64fcf14d:metrics.test.n]]` | verified | 1500 |
| 117 | outcomes | \| Event rate \| 0.2243 \| 0.224 \| | 0.2243 | ratio | event_rate | train | eq | `[[art:8a78b455:metrics.train.event_rate]]` | verified | 0.2242857143 |
| 118 | outcomes | \| Event rate \| 0.2243 \| 0.224 \| | 0.224 | ratio | event_rate | test | eq | `[[art:5f15df2a:metrics.test.event_rate]]` | verified | 0.224 |
| 119 | outcomes | \| Mean predicted \| 0.2243 \| 0.2292 \| | 0.2243 | ratio | mean_predicted | train | eq | `[[art:5ec77e91:metrics.train.mean_predicted]]` | verified | 0.2242776431 |
| 120 | outcomes | \| Mean predicted \| 0.2243 \| 0.2292 \| | 0.2292 | ratio | mean_predicted | test | eq | `[[art:f067e003:metrics.test.mean_predicted]]` | verified | 0.2292494944 |
| 121 | outcomes | \| AUC \| 0.769 \| 0.7337 \| | 0.769 | ratio | auc | train | eq | `[[art:197f9521:metrics.train.auc]]` | verified | 0.7690391902 |
| 122 | outcomes | \| AUC \| 0.769 \| 0.7337 \| | 0.7337 | ratio | auc | test | eq | `[[art:3255122a:metrics.test.auc]]` | verified | 0.7336641916 |
| 123 | outcomes | \| Gini \| 0.5381 \| 0.4673 \| | 0.5381 | ratio | gini | train | eq | `[[art:4208816b:metrics.train.gini]]` | verified | 0.5380783803 |
| 124 | outcomes | \| Gini \| 0.5381 \| 0.4673 \| | 0.4673 | ratio | gini | test | eq | `[[art:621c8cf3:metrics.test.gini]]` | verified | 0.4673283832 |
| 125 | outcomes | \| KS \| 0.4426 \| 0.4096 \| | 0.4426 | ratio | ks | train | eq | `[[art:f1d489d8:metrics.train.ks]]` | verified | 0.4425801457 |
| 126 | outcomes | \| KS \| 0.4426 \| 0.4096 \| | 0.4096 | ratio | ks | test | eq | `[[art:984fc4f0:metrics.test.ks]]` | verified | 0.4095790378 |
| 127 | outcomes | \| Brier \| 0.1489 \| 0.1536 \| | 0.1489 | ratio | brier | train | eq | `[[art:cf19f7b7:metrics.train.brier]]` | verified | 0.1488512538 |
| 128 | outcomes | \| Brier \| 0.1489 \| 0.1536 \| | 0.1536 | ratio | brier | test | eq | `[[art:3cd28a53:metrics.test.brier]]` | verified | 0.1535518185 |
| 129 | outcomes | \| Log loss \| 0.4632 \| 0.4788 \| | 0.4632 | ratio | logloss | train | eq | `[[art:a2852b4a:metrics.train.logloss]]` | verified | 0.4632349902 |
| 130 | outcomes | \| Log loss \| 0.4632 \| 0.4788 \| | 0.4788 | ratio | logloss | test | eq | `[[art:1362ad67:metrics.test.logloss]]` | verified | 0.4787760084 |
| 131 | outcomes | The top two deciles hold 0.4345 of the events on test, below… | 0.4345 | ratio | top2_capture | test | eq | `[[art:c7670b9d:deciles.test.top2_capture]]` | verified | 0.4345238095 |
| 132 | outcomes | The top two deciles hold 0.4345 of the events on test, below… | 0.4459 | ratio | top2_capture | train | eq | `[[art:0511095f:deciles.train.top2_capture]]` | verified | 0.4458598726 |
| 133 | outcomes | Discrimination is weaker on test than on train: AUC is 0.769… | 0.769 | ratio | auc | train | eq | `[[art:197f9521:metrics.train.auc]]` | verified | 0.7690391902 |
| 134 | outcomes | Discrimination is weaker on test than on train: AUC is 0.769… | 0.7337 | ratio | auc | test | eq | `[[art:3255122a:metrics.test.auc]]` | verified | 0.7336641916 |
| 135 | outcomes | Discrimination is weaker on test than on train: AUC is 0.769… | 0.08 | ratio | auc_gap |  | eq | `[[art:630f28f4:threshold.O1.auc_gap]]` | verified | 0.08 |
| 136 | outcomes | The test value stays above the developer-declared floor of 0… | 0.7 | ratio | auc | test | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 137 | outcomes | The test value stays above the developer-declared floor of 0… | 0.1536 | ratio | brier | test | eq | `[[art:3cd28a53:metrics.test.brier]]` | verified | 0.1535518185 |
| 138 | outcomes | The test value stays above the developer-declared floor of 0… | 0.2 | ratio | brier | test | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 139 | outcomes | Turning to calibration, the logistic regression of the outco… | 0.8701 | ratio | calibration_slope | test | eq | `[[art:7002f467:calibration_slope.test]]` | verified | 0.8701260273 |
| 140 | outcomes | Turning to calibration, the logistic regression of the outco… | 1.002 | ratio | calibration_slope | train | eq | `[[art:7e7849d9:calibration_slope.train]]` | verified | 1.002056925 |
| 141 | outcomes | The test slope sits inside the band running from 0.8 to 1.2… | 0.8 | ratio | calibration_slope |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 142 | outcomes | The test slope sits inside the band running from 0.8 to 1.2… | 1.2 | ratio | calibration_slope |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 143 | outcomes | The test slope sits inside the band running from 0.8 to 1.2… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 144 | outcomes | The test slope sits inside the band running from 0.8 to 1.2… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 145 | outcomes | The intercept of that regression is -0.1809 on test and 0.00… | -0.1809 | ratio | calibration_intercept | test | eq | `[[art:386a6083:calibration_intercept.test]]` | verified | -0.1808989409 |
| 146 | outcomes | The intercept of that regression is -0.1809 on test and 0.00… | 0.002422 | ratio | calibration_intercept | train | eq | `[[art:e1230838:calibration_intercept.train]]` | verified | 0.002421734739 |
| 147 | outcomes | Mean predicted probability on test is 0.2292 against an obse… | 0.2292 | ratio | mean_predicted | test | eq | `[[art:f067e003:metrics.test.mean_predicted]]` | verified | 0.2292494944 |
| 148 | outcomes | Mean predicted probability on test is 0.2292 against an obse… | 0.224 | ratio | event_rate | test | eq | `[[art:5f15df2a:metrics.test.event_rate]]` | verified | 0.224 |
| 149 | outcomes | The relative gap between those two is 0.02344 , within the t… | 0.02344 | ratio | mean_rel_gap | test | eq | `[[art:fd64775d:calibration.mean_rel_gap.test]]` | verified | 0.02343524279 |
| 150 | outcomes | The relative gap between those two is 0.02344 , within the t… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 151 | outcomes | Comparing the two splits on that relative gap rather than on… | 3.599e-05 | ratio | mean_rel_gap | train | eq | `[[art:ac0572fe:calibration.mean_rel_gap.train]]` | verified | 3.598625145e-05 |
| 152 | outcomes | Comparing the two splits on that relative gap rather than on… | 0.02344 | ratio | mean_rel_gap | test | eq | `[[art:fd64775d:calibration.mean_rel_gap.test]]` | verified | 0.02343524279 |
| 153 | outcomes | On test this sub-population's AUC falls 0.01294 below the sp… | 0.01294 | ratio | auc_gap | test | eq | `[[art:97e3e918:metrics.test.sub.bill_trend_6m_high.auc_gap]]` | verified | 0.01294153558 |
| 154 | outcomes | On test this sub-population's AUC falls 0.01294 below the sp… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 155 | outcomes | On train it falls -0.004217 below the split's own, that is,… | -0.004217 | ratio | auc_gap | train | eq | `[[art:44fe1e49:metrics.train.sub.bill_trend_6m_high.auc_gap]]` | verified | -0.004216843026 |
| 156 | outcomes | The sub-population holds 0.5 of test and 0.5 of train, above… | 0.5 | ratio | share | test | eq | `[[art:31f43354:metrics.test.sub.bill_trend_6m_high.share]]` | verified | 0.5 |
| 157 | outcomes | The sub-population holds 0.5 of test and 0.5 of train, above… | 0.5 | ratio | share | train | eq | `[[art:35313c05:metrics.train.sub.bill_trend_6m_high.share]]` | verified | 0.5 |
| 158 | outcomes | The sub-population holds 0.5 of test and 0.5 of train, above… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 159 | outcomes | The sub-population holds 0.5 of test and 0.5 of train, above… | 0.95 | ratio | slice_max_share |  | eq | `[[art:a928a05c:threshold.O1.slice_max_share]]` | verified | 0.95 |
| 160 | outcomes | Mean predicted on the test sub-population is 0.214 against a… | 0.214 | ratio | mean_predicted | test | eq | `[[art:725cd1c7:metrics.test.sub.bill_trend_6m_high.mean_predicted]]` | verified | 0.2139732835 |
| 161 | outcomes | Mean predicted on the test sub-population is 0.214 against a… | 0.2093 | ratio | event_rate | test | eq | `[[art:9a8a6f36:metrics.test.sub.bill_trend_6m_high.event_rate]]` | verified | 0.2093333333 |
| 162 | outcomes | Mean predicted on the test sub-population is 0.214 against a… | 0.02217 | ratio | mean_rel_gap | test | eq | `[[art:b2206639:metrics.test.sub.bill_trend_6m_high.mean_rel_gap]]` | verified | 0.02216536683 |
| 163 | outcomes | Mean predicted on the test sub-population is 0.214 against a… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 164 | outcomes | On train the same comparison gives mean predicted of 0.2182… | 0.2182 | ratio | mean_predicted | train | eq | `[[art:c1479a5f:metrics.train.sub.bill_trend_6m_high.mean_predicted]]` | verified | 0.2182222572 |
| 165 | outcomes | On train the same comparison gives mean predicted of 0.2182… | 0.2229 | ratio | event_rate | train | eq | `[[art:5c13b21d:metrics.train.sub.bill_trend_6m_high.event_rate]]` | verified | 0.2228571429 |
| 166 | outcomes | On train the same comparison gives mean predicted of 0.2182… | 0.0208 | ratio | mean_rel_gap | train | eq | `[[art:dec79ccf:metrics.train.sub.bill_trend_6m_high.mean_rel_gap]]` | verified | 0.02079756374 |
| 167 | outcomes | On test this sub-population's AUC falls -0.006995 below the… | -0.006995 | ratio | auc_gap | test | eq | `[[art:a6dacfd1:metrics.test.sub.bill_trend_6m_low.auc_gap]]` | verified | -0.006994654468 |
| 168 | outcomes | On test this sub-population's AUC falls -0.006995 below the… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 169 | outcomes | On train it falls 0.005086 below the split's own, also withi… | 0.005086 | ratio | auc_gap | train | eq | `[[art:51a4dd85:metrics.train.sub.bill_trend_6m_low.auc_gap]]` | verified | 0.005085712647 |
| 170 | outcomes | The sub-population holds 0.5 of test and 0.5 of train, above… | 0.5 | ratio | share | test | eq | `[[art:56a82f85:metrics.test.sub.bill_trend_6m_low.share]]` | verified | 0.5 |
| 171 | outcomes | The sub-population holds 0.5 of test and 0.5 of train, above… | 0.5 | ratio | share | train | eq | `[[art:1a2d7b50:metrics.train.sub.bill_trend_6m_low.share]]` | verified | 0.5 |
| 172 | outcomes | The sub-population holds 0.5 of test and 0.5 of train, above… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 173 | outcomes | The sub-population holds 0.5 of test and 0.5 of train, above… | 0.95 | ratio | slice_max_share |  | eq | `[[art:a928a05c:threshold.O1.slice_max_share]]` | verified | 0.95 |
| 174 | outcomes | Mean predicted on the test sub-population is 0.2445 against… | 0.2445 | ratio | mean_predicted | test | eq | `[[art:11cfcac7:metrics.test.sub.bill_trend_6m_low.mean_predicted]]` | verified | 0.2445257053 |
| 175 | outcomes | Mean predicted on the test sub-population is 0.2445 against… | 0.2387 | ratio | event_rate | test | eq | `[[art:4fa19590:metrics.test.sub.bill_trend_6m_low.event_rate]]` | verified | 0.2386666667 |
| 176 | outcomes | Mean predicted on the test sub-population is 0.2445 against… | 0.02455 | ratio | mean_rel_gap | test | eq | `[[art:855d5668:metrics.test.sub.bill_trend_6m_low.mean_rel_gap]]` | verified | 0.0245490446 |
| 177 | outcomes | Mean predicted on the test sub-population is 0.2445 against… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 178 | outcomes | On train the comparison gives mean predicted of 0.2303 again… | 0.2303 | ratio | mean_predicted | train | eq | `[[art:249e2db2:metrics.train.sub.bill_trend_6m_low.mean_predicted]]` | verified | 0.2303330289 |
| 179 | outcomes | On train the comparison gives mean predicted of 0.2303 again… | 0.2257 | ratio | event_rate | train | eq | `[[art:1acba5e5:metrics.train.sub.bill_trend_6m_low.event_rate]]` | verified | 0.2257142857 |
| 180 | outcomes | On train the comparison gives mean predicted of 0.2303 again… | 0.02046 | ratio | mean_rel_gap | train | eq | `[[art:e2bddb91:metrics.train.sub.bill_trend_6m_low.mean_rel_gap]]` | verified | 0.02046278646 |
| 181 | outcomes | Comparing the two sub-populations on test as differences fro… | 0.01294 | ratio | auc_gap | test | eq | `[[art:97e3e918:metrics.test.sub.bill_trend_6m_high.auc_gap]]` | verified | 0.01294153558 |
| 182 | outcomes | Comparing the two sub-populations on test as differences fro… | -0.006995 | ratio | auc_gap | test | eq | `[[art:a6dacfd1:metrics.test.sub.bill_trend_6m_low.auc_gap]]` | verified | -0.006994654468 |
| 183 | outcomes | Comparing the two sub-populations on test as differences fro… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 184 | outcomes | Comparing them on their relative level gaps on test, each al… | 0.02455 | ratio | mean_rel_gap | test | eq | `[[art:855d5668:metrics.test.sub.bill_trend_6m_low.mean_rel_gap]]` | verified | 0.0245490446 |
| 185 | outcomes | Comparing them on their relative level gaps on test, each al… | 0.02217 | ratio | mean_rel_gap | test | eq | `[[art:b2206639:metrics.test.sub.bill_trend_6m_high.mean_rel_gap]]` | verified | 0.02216536683 |
| 186 | sensitivity | The largest variance inflation factor among the retained fea… | 7.512 | ratio | vif |  | eq | `[[art:2d17cd9e:vif.max]]` | verified | 7.511880286 |
| 187 | sensitivity | The largest variance inflation factor among the retained fea… | 10 | ratio | vif |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 188 | sensitivity | That largest value coincides with the mean bill amount featu… | 7.512 | ratio | vif |  | eq | `[[art:19127172:vif.bill_mean_6m]]` | verified | 7.511880286 |
| 189 | sensitivity | That largest value coincides with the mean bill amount featu… | 7.213 | ratio | vif |  | eq | `[[art:a9b805e2:vif.pay_ratio_last]]` | verified | 7.212565743 |
| 190 | sensitivity | That largest value coincides with the mean bill amount featu… | 7.206 | ratio | vif |  | eq | `[[art:76a555ef:vif.pay_ratio_mean_6m]]` | verified | 7.205620957 |
| 191 | sensitivity | The remaining retained features sit further from the bound:… | 4.832 | ratio | vif |  | eq | `[[art:f19a1ae6:vif.limit_bal]]` | verified | 4.831600304 |
| 192 | sensitivity | The remaining retained features sit further from the bound:… | 3.408 | ratio | vif |  | eq | `[[art:87292dc8:vif.utilisation]]` | verified | 3.407876506 |
| 193 | sensitivity | The remaining retained features sit further from the bound:… | 2.527 | ratio | vif |  | eq | `[[art:063976d6:vif.delinq_count_6m]]` | verified | 2.527119253 |
| 194 | sensitivity | The remaining retained features sit further from the bound:… | 2.375 | ratio | vif |  | eq | `[[art:fa4a6cf4:vif.delinq_max_6m]]` | verified | 2.374670872 |
| 195 | sensitivity | The remaining retained features sit further from the bound:… | 1.433 | ratio | vif |  | eq | `[[art:1d3a39df:vif.delinq_last]]` | verified | 1.433233823 |
| 196 | sensitivity | The remaining retained features sit further from the bound:… | 1.217 | ratio | vif |  | eq | `[[art:36ec368c:vif.bill_trend_6m]]` | verified | 1.217478854 |
| 197 | sensitivity | The remaining retained features sit further from the bound:… | 1.003 | ratio | vif |  | eq | `[[art:193052e1:vif.age]]` | verified | 1.003158787 |
| 198 | sensitivity | Belsley's condition number of the column-standardised design… | 5.647 | ratio | condition_number |  | eq | `[[art:8dc0c2f1:condition_number]]` | verified | 5.646537667 |
| 199 | sensitivity | Belsley's condition number of the column-standardised design… | 30 | ratio | condition_number |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 200 | sensitivity | The declared bound on the AUC difference across regimes is 0… | 0.1 | ratio | auc_gap |  | eq | `[[art:b64213d7:threshold.R1.auc_gap]]` | verified | 0.1 |
| 201 | sensitivity | A sign flip is counted only where the feature is among the h… | 0.05 | ratio | sign_flip_coef |  | eq | `[[art:aca84377:threshold.R1.sign_flip_coef]]` | verified | 0.05 |
| 202 | sensitivity | A sign flip is counted only where the feature is among the h… | 2 | ratio | sign_flip_z |  | eq | `[[art:2e4428c7:threshold.R1.sign_flip_z]]` | verified | 2 |
| 203 | sensitivity | On that definition the indicator reads 1 for the bill trend… | 1 | ratio | sign_flip |  | eq | `[[art:4dc17324:stability.bill_trend_6m.sign_flip]]` | verified | 1 |
| 204 | sensitivity | The indicator reads 0 for age , 0 for the mean bill amount ,… | 0 | ratio | sign_flip |  | eq | `[[art:af9b1d06:stability.age.sign_flip]]` | verified | 0 |
| 205 | sensitivity | The indicator reads 0 for age , 0 for the mean bill amount ,… | 0 | ratio | sign_flip |  | eq | `[[art:df546086:stability.bill_mean_6m.sign_flip]]` | verified | 0 |
| 206 | sensitivity | The indicator reads 0 for age , 0 for the mean bill amount ,… | 0 | ratio | sign_flip |  | eq | `[[art:40d78102:stability.delinq_count_6m.sign_flip]]` | verified | 0 |
| 207 | sensitivity | The indicator reads 0 for age , 0 for the mean bill amount ,… | 0 | ratio | sign_flip |  | eq | `[[art:a7adedc7:stability.delinq_last.sign_flip]]` | verified | 0 |
| 208 | sensitivity | The indicator reads 0 for age , 0 for the mean bill amount ,… | 0 | ratio | sign_flip |  | eq | `[[art:908eec36:stability.delinq_max_6m.sign_flip]]` | verified | 0 |
| 209 | sensitivity | The indicator reads 0 for age , 0 for the mean bill amount ,… | 0 | ratio | sign_flip |  | eq | `[[art:3a0e7e0d:stability.limit_bal.sign_flip]]` | verified | 0 |
| 210 | sensitivity | The indicator reads 0 for age , 0 for the mean bill amount ,… | 0 | ratio | sign_flip |  | eq | `[[art:77aa667a:stability.pay_ratio_last.sign_flip]]` | verified | 0 |
| 211 | sensitivity | The indicator reads 0 for age , 0 for the mean bill amount ,… | 0 | ratio | sign_flip |  | eq | `[[art:f8da40ca:stability.pay_ratio_mean_6m.sign_flip]]` | verified | 0 |
| 212 | sensitivity | The indicator reads 0 for age , 0 for the mean bill amount ,… | 0 | ratio | sign_flip |  | eq | `[[art:5b813a1b:stability.utilisation.sign_flip]]` | verified | 0 |
| 213 | findings | The regime sign-reversal condition for this feature evaluate… | 1 | ratio | sign_flip |  | eq | `[[art:4dc17324:stability.bill_trend_6m.sign_flip]]` | verified | 1 |
| 214 | findings | The regime sign-reversal condition for this feature evaluate… | 0.05 | ratio | sign_flip_coef |  | eq | `[[art:aca84377:threshold.R1.sign_flip_coef]]` | verified | 0.05 |
| 215 | findings | The regime sign-reversal condition for this feature evaluate… | 2 | ratio | sign_flip_z |  | eq | `[[art:2e4428c7:threshold.R1.sign_flip_z]]` | verified | 2 |
| 216 | findings | The challenger reaches an AUC on test of 0.7898 against the… | 0.7898 | ratio | auc | test | eq | `[[art:2b3381be:challenger.auc]]` | verified | 0.7897950417 |
| 217 | findings | The challenger reaches an AUC on test of 0.7898 against the… | 0.7337 | ratio | auc | test | eq | `[[art:3255122a:metrics.test.auc]]` | verified | 0.7336641916 |
| 218 | findings | The comparison the rule makes is the difference between the… | 0.05613 | ratio | delta_auc | test | eq | `[[art:9cbcc544:challenger.delta_auc]]` | verified | 0.05613085011 |
| 219 | findings | The comparison the rule makes is the difference between the… | 0.03 | ratio | delta_auc |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 220 | findings | - Why does the fitted coefficient on `age` carry sign -1 whe… | -1 | ratio | coef_sign |  | eq | `[[art:6172eb93:sign_check.age.coef_sign]]` | verified | -1 |
| 221 | findings | - Why does the fitted coefficient on `age` carry sign -1 whe… | 1 | ratio | univariate_direction | train | eq | `[[art:cac34cd5:sign_check.age.univariate_direction]]` | verified | 1 |
| 222 | findings | - Why does the fitted coefficient on `age` carry sign -1 whe… | 0 | ratio | agrees |  | eq | `[[art:5c2c50b8:sign_check.age.agrees]]` | verified | 0 |
| 223 | findings | - Why does the fitted coefficient on `bill_mean_6m` carry si… | -1 | ratio | coef_sign |  | eq | `[[art:cee1a18f:sign_check.bill_mean_6m.coef_sign]]` | verified | -1 |
| 224 | findings | - Why does the fitted coefficient on `bill_mean_6m` carry si… | 1 | ratio | univariate_direction | train | eq | `[[art:82ba9862:sign_check.bill_mean_6m.univariate_direction]]` | verified | 1 |
| 225 | findings | - Why does the fitted coefficient on `bill_mean_6m` carry si… | 0 | ratio | agrees |  | eq | `[[art:4df8b747:sign_check.bill_mean_6m.agrees]]` | verified | 0 |
| 226 | findings | - Why does the fitted coefficient on `limit_bal` carry sign… | 1 | ratio | coef_sign |  | eq | `[[art:6af6aef2:sign_check.limit_bal.coef_sign]]` | verified | 1 |
| 227 | findings | - Why does the fitted coefficient on `limit_bal` carry sign… | -1 | ratio | univariate_direction | train | eq | `[[art:56d284d6:sign_check.limit_bal.univariate_direction]]` | verified | -1 |
| 228 | findings | - Why does the fitted coefficient on `limit_bal` carry sign… | 0 | ratio | agrees |  | eq | `[[art:0278aad1:sign_check.limit_bal.agrees]]` | verified | 0 |
| 229 | monitoring | Rank-ordering performance should be recomputed on each score… | 0.7 | ratio | auc | test | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 230 | monitoring | Rank-ordering performance should be recomputed on each score… | 0.7337 | ratio | auc | test | eq | `[[art:3255122a:metrics.test.auc]]` | verified | 0.7336641916 |
| 231 | monitoring | Probabilistic accuracy should be recomputed on the same cade… | 0.2 | ratio | brier | test | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 232 | monitoring | Probabilistic accuracy should be recomputed on the same cade… | 0.1536 | ratio | brier | test | eq | `[[art:3cd28a53:metrics.test.brier]]` | verified | 0.1535518185 |
| 233 | monitoring | The regression of the outcome on the logit of the predicted… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 234 | monitoring | The regression of the outcome on the logit of the predicted… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 235 | monitoring | The evaluation-split slope of 0.8701 lies above the lower ed… | 0.8701 | ratio | calibration_slope | test | eq | `[[art:7002f467:calibration_slope.test]]` | verified | 0.8701260273 |
| 236 | monitoring | The comparison population should be the production vintage a… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 237 | monitoring | The comparison population should be the production vintage a… | 0.02385 | ratio | psi |  | eq | `[[art:4a5ae1a0:psi.max]]` | verified | 0.02385256621 |
| 238 | monitoring | This report ordered discrimination ahead of calibration for… | 0.05 | ratio | event_rate | test | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 239 | monitoring | For any future cohort whose observed event rate falls below… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |

## Appendix B — Artifact index

The store holds 243 artifacts; the 171 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `ablation.age.delta_auc` | `03f2c15c` | scalar | -0.0005471690394 | change in test AUC when the champion's form is refitted without age |
| `ablation.baseline_auc` | `89f9f36a` | scalar | 0.7336641916 | AUC on test of a refit of the champion's functional form on every retained feature, the level each ablation delta is measured from |
| `ablation.bill_mean_6m.delta_auc` | `e4786496` | scalar | 0.005428223695 | change in test AUC when the champion's form is refitted without bill_mean_6m |
| `ablation.bill_trend_6m.delta_auc` | `bb1f5508` | scalar | 0.002866245295 | change in test AUC when the champion's form is refitted without bill_trend_6m |
| `ablation.delinq_count_6m.delta_auc` | `5db921e5` | scalar | -0.0007824005891 | change in test AUC when the champion's form is refitted without delinq_count_6m |
| `ablation.delinq_last.delta_auc` | `e986cd7d` | scalar | -0.08354299624 | change in test AUC when the champion's form is refitted without delinq_last |
| `ablation.delinq_max_6m.delta_auc` | `76f922d7` | scalar | 0.0005906357388 | change in test AUC when the champion's form is refitted without delinq_max_6m |
| `ablation.limit_bal.delta_auc` | `5002902a` | scalar | 0.001337240223 | change in test AUC when the champion's form is refitted without limit_bal |
| `ablation.pay_ratio_last.delta_auc` | `04295c71` | scalar | -0.0004116552119 | change in test AUC when the champion's form is refitted without pay_ratio_last |
| `ablation.pay_ratio_mean_6m.delta_auc` | `5cb2a089` | scalar | 0.001725883652 | change in test AUC when the champion's form is refitted without pay_ratio_mean_6m |
| `ablation.utilisation.delta_auc` | `8621db24` | scalar | -0.006450969563 | change in test AUC when the champion's form is refitted without utilisation |
| `calibration.mean_rel_gap.test` | `fd64775d` | scalar | 0.02343524279 | mean predicted against observed on test, relative |
| `calibration.mean_rel_gap.train` | `ac0572fe` | scalar | 3.598625145e-05 | mean predicted against observed on train, relative |
| `calibration.test` | `28aa9ae3` | table | table, 10 rows | calibration by decile of predicted probability on test |
| `calibration_intercept.test` | `386a6083` | scalar | -0.1808989409 | logistic regression of the outcome on logit(p) on test: the intercept |
| `calibration_intercept.train` | `e1230838` | scalar | 0.002421734739 | logistic regression of the outcome on logit(p) on train: the intercept |
| `calibration_slope.test` | `7002f467` | scalar | 0.8701260273 | logistic regression of the outcome on logit(p) on test: the slope |
| `calibration_slope.train` | `7e7849d9` | scalar | 1.002056925 | logistic regression of the outcome on logit(p) on train: the slope |
| `challenger.auc` | `2b3381be` | scalar | 0.7897950417 | the challenger's AUC on test |
| `challenger.brier` | `9599fce0` | scalar | 0.1391775952 | the challenger's Brier score on test |
| `challenger.delta_auc` | `9cbcc544` | scalar | 0.05613085011 | the challenger's AUC on test minus the champion's |
| `condition_number` | `8dc0c2f1` | scalar | 5.646537667 | Belsley's condition number of the column-standardised design |
| `csi.age` | `0aad0eb8` | scalar | 0.0002174582447 | CSI of age: its contribution to the shift in the linear predictor |
| `csi.bill_mean_6m` | `4ceb65ea` | scalar | 0.00595223424 | CSI of bill_mean_6m: its contribution to the shift in the linear predictor |
| `csi.bill_trend_6m` | `93317930` | scalar | 0.0004863886573 | CSI of bill_trend_6m: its contribution to the shift in the linear predictor |
| `csi.delinq_count_6m` | `8359c176` | scalar | 0.0001785733233 | CSI of delinq_count_6m: its contribution to the shift in the linear predictor |
| `csi.delinq_last` | `c0b3fffe` | scalar | 0.01811466703 | CSI of delinq_last: its contribution to the shift in the linear predictor |
| `csi.delinq_max_6m` | `0bc44634` | scalar | 0.0002075152658 | CSI of delinq_max_6m: its contribution to the shift in the linear predictor |
| `csi.limit_bal` | `443540b2` | scalar | 0.0002441546194 | CSI of limit_bal: its contribution to the shift in the linear predictor |
| `csi.max` | `28c0a604` | scalar | 0.01811466703 | the largest characteristic stability index |
| `csi.pay_ratio_last` | `e06dbc50` | scalar | 1.459725993e-05 | CSI of pay_ratio_last: its contribution to the shift in the linear predictor |
| `csi.pay_ratio_mean_6m` | `adf83ef4` | scalar | 0.004500399242 | CSI of pay_ratio_mean_6m: its contribution to the shift in the linear predictor |
| `csi.utilisation` | `54e8c0d5` | scalar | 0.01787504902 | CSI of utilisation: its contribution to the shift in the linear predictor |
| `deciles.test` | `9212d403` | table | table, 10 rows | decile separation on test; decile 1 holds the highest probabilities |
| `deciles.test.top2_capture` | `c7670b9d` | scalar | 0.4345238095 | share of test events in the top two deciles |
| `deciles.train.top2_capture` | `0511095f` | scalar | 0.4458598726 | share of train events in the top two deciles |
| `leakage.duplicates.train` | `4474c227` | scalar | 0 | share of train rows whose feature values are not unique within train |
| `leakage.name_screen.n_matched` | `407e62be` | scalar | 0 | feature names matching the target-adjacent lexicon |
| `leakage.overlap` | `4c9fcd09` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.features` | `0fec8048` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.ids` | `63d37fc5` | scalar | 0 | share of test rows whose ['client_id'] also identify a row of train |
| `leakage.target_corr.max_single_feature_auc` | `f39d22de` | scalar | 0.6841001279 | the AUC of the strongest single feature |
| `leakage.timing.n_flagged` | `742bcd24` | scalar | 0 | features declared during_period or after_outcome |
| `metrics.test.auc` | `3255122a` | scalar | 0.7336641916 | auc on test, recomputed by quaestor |
| `metrics.test.brier` | `3cd28a53` | scalar | 0.1535518185 | brier on test, recomputed by quaestor |
| `metrics.test.event_rate` | `5f15df2a` | scalar | 0.224 | event_rate on test, recomputed by quaestor |
| `metrics.test.gini` | `621c8cf3` | scalar | 0.4673283832 | gini on test, recomputed by quaestor |
| `metrics.test.ks` | `984fc4f0` | scalar | 0.4095790378 | ks on test, recomputed by quaestor |
| `metrics.test.logloss` | `1362ad67` | scalar | 0.4787760084 | logloss on test, recomputed by quaestor |
| `metrics.test.mean_predicted` | `f067e003` | scalar | 0.2292494944 | mean_predicted on test, recomputed by quaestor |
| `metrics.test.n` | `64fcf14d` | scalar | 1500 | n on test, recomputed by quaestor |
| `metrics.test.sub.bill_trend_6m_high` | `480cbefc` | table | table, 10 rows | every metric on the bill_trend_6m above_median slice of test |
| `metrics.test.sub.bill_trend_6m_high.auc_gap` | `97e3e918` | scalar | 0.01294153558 | how far AUC on the bill_trend_6m above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.bill_trend_6m_high.event_rate` | `9a8a6f36` | scalar | 0.2093333333 | event_rate on the bill_trend_6m above_median slice of test |
| `metrics.test.sub.bill_trend_6m_high.mean_predicted` | `725cd1c7` | scalar | 0.2139732835 | mean_predicted on the bill_trend_6m above_median slice of test |
| `metrics.test.sub.bill_trend_6m_high.mean_rel_gap` | `b2206639` | scalar | 0.02216536683 | mean predicted against observed on the bill_trend_6m above_median slice of test, relative |
| `metrics.test.sub.bill_trend_6m_high.share` | `31f43354` | scalar | 0.5 | the share of test the bill_trend_6m above_median slice holds |
| `metrics.test.sub.bill_trend_6m_low` | `064648eb` | table | table, 10 rows | every metric on the bill_trend_6m below_median slice of test |
| `metrics.test.sub.bill_trend_6m_low.auc_gap` | `a6dacfd1` | scalar | -0.006994654468 | how far AUC on the bill_trend_6m below_median slice of test falls below AUC on all of test |
| `metrics.test.sub.bill_trend_6m_low.event_rate` | `4fa19590` | scalar | 0.2386666667 | event_rate on the bill_trend_6m below_median slice of test |
| `metrics.test.sub.bill_trend_6m_low.mean_predicted` | `11cfcac7` | scalar | 0.2445257053 | mean_predicted on the bill_trend_6m below_median slice of test |
| `metrics.test.sub.bill_trend_6m_low.mean_rel_gap` | `855d5668` | scalar | 0.0245490446 | mean predicted against observed on the bill_trend_6m below_median slice of test, relative |
| `metrics.test.sub.bill_trend_6m_low.share` | `56a82f85` | scalar | 0.5 | the share of test the bill_trend_6m below_median slice holds |
| `metrics.train.auc` | `197f9521` | scalar | 0.7690391902 | auc on train, recomputed by quaestor |
| `metrics.train.brier` | `cf19f7b7` | scalar | 0.1488512538 | brier on train, recomputed by quaestor |
| `metrics.train.event_rate` | `8a78b455` | scalar | 0.2242857143 | event_rate on train, recomputed by quaestor |
| `metrics.train.gini` | `4208816b` | scalar | 0.5380783803 | gini on train, recomputed by quaestor |
| `metrics.train.ks` | `f1d489d8` | scalar | 0.4425801457 | ks on train, recomputed by quaestor |
| `metrics.train.logloss` | `a2852b4a` | scalar | 0.4632349902 | logloss on train, recomputed by quaestor |
| `metrics.train.mean_predicted` | `5ec77e91` | scalar | 0.2242776431 | mean_predicted on train, recomputed by quaestor |
| `metrics.train.n` | `564683ee` | scalar | 3500 | n on train, recomputed by quaestor |
| `metrics.train.sub.bill_trend_6m_high` | `5489c988` | table | table, 10 rows | every metric on the bill_trend_6m above_median slice of train |
| `metrics.train.sub.bill_trend_6m_high.auc_gap` | `44fe1e49` | scalar | -0.004216843026 | how far AUC on the bill_trend_6m above_median slice of train falls below AUC on all of train |
| `metrics.train.sub.bill_trend_6m_high.event_rate` | `5c13b21d` | scalar | 0.2228571429 | event_rate on the bill_trend_6m above_median slice of train |
| `metrics.train.sub.bill_trend_6m_high.mean_predicted` | `c1479a5f` | scalar | 0.2182222572 | mean_predicted on the bill_trend_6m above_median slice of train |
| `metrics.train.sub.bill_trend_6m_high.mean_rel_gap` | `dec79ccf` | scalar | 0.02079756374 | mean predicted against observed on the bill_trend_6m above_median slice of train, relative |
| `metrics.train.sub.bill_trend_6m_high.share` | `35313c05` | scalar | 0.5 | the share of train the bill_trend_6m above_median slice holds |
| `metrics.train.sub.bill_trend_6m_low` | `61850b8b` | table | table, 10 rows | every metric on the bill_trend_6m below_median slice of train |
| `metrics.train.sub.bill_trend_6m_low.auc_gap` | `51a4dd85` | scalar | 0.005085712647 | how far AUC on the bill_trend_6m below_median slice of train falls below AUC on all of train |
| `metrics.train.sub.bill_trend_6m_low.event_rate` | `1acba5e5` | scalar | 0.2257142857 | event_rate on the bill_trend_6m below_median slice of train |
| `metrics.train.sub.bill_trend_6m_low.mean_predicted` | `249e2db2` | scalar | 0.2303330289 | mean_predicted on the bill_trend_6m below_median slice of train |
| `metrics.train.sub.bill_trend_6m_low.mean_rel_gap` | `e2bddb91` | scalar | 0.02046278646 | mean predicted against observed on the bill_trend_6m below_median slice of train, relative |
| `metrics.train.sub.bill_trend_6m_low.share` | `1a2d7b50` | scalar | 0.5 | the share of train the bill_trend_6m below_median slice holds |
| `profile.test.missing.max` | `f813848d` | scalar | 0 | the largest missing fraction in test |
| `profile.test.n` | `2193cf5f` | scalar | 1500 | rows in test |
| `profile.train.missing.max` | `050a3099` | scalar | 0 | the largest missing fraction in train |
| `profile.train.n` | `2510d49d` | scalar | 3500 | rows in train |
| `psi.age` | `2e7b9ead` | scalar | 0.01198203437 | PSI of age between train and test |
| `psi.bill_mean_6m` | `a0afce85` | scalar | 0.00801839524 | PSI of bill_mean_6m between train and test |
| `psi.bill_trend_6m` | `b80e3091` | scalar | 0.008579333007 | PSI of bill_trend_6m between train and test |
| `psi.delinq_count_6m` | `4b7439f2` | scalar | 0.001413525134 | PSI of delinq_count_6m between train and test |
| `psi.delinq_last` | `7662ef2e` | scalar | 0.003062063118 | PSI of delinq_last between train and test |
| `psi.delinq_max_6m` | `b6668567` | scalar | 0.00372909277 | PSI of delinq_max_6m between train and test |
| `psi.limit_bal` | `09a00724` | scalar | 0.004675866811 | PSI of limit_bal between train and test |
| `psi.max` | `4a5ae1a0` | scalar | 0.02385256621 | the largest train-to-test PSI, score included |
| `psi.pay_ratio_last` | `96c52004` | scalar | 0.006835339118 | PSI of pay_ratio_last between train and test |
| `psi.pay_ratio_mean_6m` | `e3761732` | scalar | 0.02385256621 | PSI of pay_ratio_mean_6m between train and test |
| `psi.utilisation` | `3c68d5ee` | scalar | 0.01247544421 | PSI of utilisation between train and test |
| `psi.y_score` | `4a23b13e` | scalar | 0.006306336141 | PSI of the score between train and test |
| `rule.calibration_first_event_rate` | `42f1351e` | scalar | 0.05 | the event rate below which the report puts calibration before discrimination |
| `run.features` | `abbb748e` | json | json | the subject's features.json |
| `run.model_summary` | `15071cdb` | json | json | the subject's model_summary.json |
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |
| `sign_check.age.agrees` | `5c2c50b8` | scalar | 0 | 1 when the fitted sign on age agrees with its univariate direction, 0 when it does not |
| `sign_check.age.coef_sign` | `6172eb93` | scalar | -1 | the sign of the fitted coefficient on age |
| `sign_check.age.univariate_direction` | `cac34cd5` | scalar | 1 | the sign of age's own single-feature AUC on train minus 0.5 |
| `sign_check.bill_mean_6m.agrees` | `4df8b747` | scalar | 0 | 1 when the fitted sign on bill_mean_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.bill_mean_6m.coef_sign` | `cee1a18f` | scalar | -1 | the sign of the fitted coefficient on bill_mean_6m |
| `sign_check.bill_mean_6m.univariate_direction` | `82ba9862` | scalar | 1 | the sign of bill_mean_6m's own single-feature AUC on train minus 0.5 |
| `sign_check.bill_trend_6m.agrees` | `ff3cb24a` | scalar | 1 | 1 when the fitted sign on bill_trend_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.delinq_count_6m.agrees` | `a337d16b` | scalar | 1 | 1 when the fitted sign on delinq_count_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.delinq_last.agrees` | `a8ba9372` | scalar | 1 | 1 when the fitted sign on delinq_last agrees with its univariate direction, 0 when it does not |
| `sign_check.delinq_last.coef_sign` | `50d352f8` | scalar | 1 | the sign of the fitted coefficient on delinq_last |
| `sign_check.delinq_last.univariate_direction` | `a78648ba` | scalar | 1 | the sign of delinq_last's own single-feature AUC on train minus 0.5 |
| `sign_check.delinq_max_6m.agrees` | `da92a015` | scalar | 1 | 1 when the fitted sign on delinq_max_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.limit_bal.agrees` | `0278aad1` | scalar | 0 | 1 when the fitted sign on limit_bal agrees with its univariate direction, 0 when it does not |
| `sign_check.limit_bal.coef_sign` | `6af6aef2` | scalar | 1 | the sign of the fitted coefficient on limit_bal |
| `sign_check.limit_bal.univariate_direction` | `56d284d6` | scalar | -1 | the sign of limit_bal's own single-feature AUC on train minus 0.5 |
| `sign_check.n_disagreements` | `e223cd4a` | scalar | 3 | retained features whose fitted sign contradicts their univariate direction, of 10 checked |
| `sign_check.pay_ratio_last.agrees` | `7837941a` | scalar | 1 | 1 when the fitted sign on pay_ratio_last agrees with its univariate direction, 0 when it does not |
| `sign_check.pay_ratio_mean_6m.agrees` | `7e9a76ca` | scalar | 1 | 1 when the fitted sign on pay_ratio_mean_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.utilisation.agrees` | `d0c9a130` | scalar | 1 | 1 when the fitted sign on utilisation agrees with its univariate direction, 0 when it does not |
| `sign_check.utilisation.coef_sign` | `85badc3c` | scalar | 1 | the sign of the fitted coefficient on utilisation |
| `sign_check.utilisation.univariate_direction` | `f0995196` | scalar | 1 | the sign of utilisation's own single-feature AUC on train minus 0.5 |
| `stability.age.sign_flip` | `af9b1d06` | scalar | 0 | 1 when age is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.auc_by_regime` | `395a801f` | table | table, 2 rows | the champion's AUC within each application_cohort on train |
| `stability.bill_mean_6m.sign_flip` | `df546086` | scalar | 0 | 1 when bill_mean_6m is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.bill_trend_6m.coef_or_importance_by_regime` | `4114d577` | table | table, 2 rows | bill_trend_6m's coefficient in a per-regime refit, standardised, with the standard error and z of each |
| `stability.bill_trend_6m.sign_flip` | `4dc17324` | scalar | 1 | 1 when bill_trend_6m is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.delinq_count_6m.sign_flip` | `40d78102` | scalar | 0 | 1 when delinq_count_6m is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.delinq_last.sign_flip` | `a7adedc7` | scalar | 0 | 1 when delinq_last is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.delinq_max_6m.sign_flip` | `908eec36` | scalar | 0 | 1 when delinq_max_6m is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.limit_bal.sign_flip` | `3a0e7e0d` | scalar | 0 | 1 when limit_bal is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.pay_ratio_last.sign_flip` | `77aa667a` | scalar | 0 | 1 when pay_ratio_last is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.pay_ratio_mean_6m.sign_flip` | `f8da40ca` | scalar | 0 | 1 when pay_ratio_mean_6m is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.utilisation.sign_flip` | `5b813a1b` | scalar | 0 | 1 when utilisation is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
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
| `threshold.R1.auc_gap` | `b64213d7` | scalar | 0.1 | R1: the AUC difference across regimes |
| `threshold.R1.sign_flip_coef` | `aca84377` | scalar | 0.05 | R1: the coefficient a sign flip must exceed in both regimes |
| `threshold.R1.sign_flip_z` | `2e4428c7` | scalar | 2 | R1: the \|z\| a sign flip's coefficient must reach in both regimes |
| `threshold.S1.psi` | `278b9016` | scalar | 0.25 | S1: the population stability index, train against test |
| `threshold.package.auc.test.min` | `8bfd02cc` | scalar | 0.7 | package.yaml declares auc min 0.7 |
| `threshold.package.brier.test.max` | `d0f98b9c` | scalar | 0.2 | package.yaml declares brier max 0.2 |
| `threshold.package.calibration_slope.test.max` | `0adb7a89` | scalar | 1.2 | package.yaml declares calibration_slope max 1.2 |
| `threshold.package.calibration_slope.test.min` | `95fdb848` | scalar | 0.8 | package.yaml declares calibration_slope min 0.8 |
| `threshold.package.psi.max` | `fbb5a9d1` | scalar | 0.25 | package.yaml declares psi max 0.25 |
| `thresholds.evaluation` | `d1a5d9c8` | table | table, 5 rows | every threshold package.yaml declares, with its bound, the recomputed value and the outcome |
| `vif.age` | `193052e1` | scalar | 1.003158787 | variance inflation factor of age on train |
| `vif.bill_mean_6m` | `19127172` | scalar | 7.511880286 | variance inflation factor of bill_mean_6m on train |
| `vif.bill_trend_6m` | `36ec368c` | scalar | 1.217478854 | variance inflation factor of bill_trend_6m on train |
| `vif.delinq_count_6m` | `063976d6` | scalar | 2.527119253 | variance inflation factor of delinq_count_6m on train |
| `vif.delinq_last` | `1d3a39df` | scalar | 1.433233823 | variance inflation factor of delinq_last on train |
| `vif.delinq_max_6m` | `fa4a6cf4` | scalar | 2.374670872 | variance inflation factor of delinq_max_6m on train |
| `vif.limit_bal` | `f19a1ae6` | scalar | 4.831600304 | variance inflation factor of limit_bal on train |
| `vif.max` | `2d17cd9e` | scalar | 7.511880286 | the largest variance inflation factor |
| `vif.pay_ratio_last` | `a9b805e2` | scalar | 7.212565743 | variance inflation factor of pay_ratio_last on train |
| `vif.pay_ratio_mean_6m` | `76a555ef` | scalar | 7.205620957 | variance inflation factor of pay_ratio_mean_6m on train |
| `vif.utilisation` | `87292dc8` | scalar | 3.407876506 | variance inflation factor of utilisation on train |

## Appendix C — Run trace summary

| quantity | value |
|---|---|
| tool calls | 18 (run_model 1, profile_data 1, compute_metrics 4, check_leakage 1, check_stability 2, check_collinearity 1, challenger_compare 1, retrieve_guidance 7) |
| plan steps (bounded loop) | 4 |
| LLM calls | 18 (plan 4, draft 7, extract 7) |
| re-asks | 0 |
| repair rounds | 0 |
| tokens in / out | 210,736 / 92,971 |
| notional cost (USD) | 4.4625 |
| wall-clock (s) | 1011.97 |
| subject run (s) | 2.44 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | credit_default-full_agent-20260920T092037Z-e2e51e00 |

## Appendix D — Not checked

| item | reason |
|---|---|
| `run_scenarios` (X1) | not applicable to `binary_classification` |
| out-of-time and vintage-holdout metrics (O1, second rule) | package declares neither split |
| developer claims (T1, claim channel) | The package declares 2 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
