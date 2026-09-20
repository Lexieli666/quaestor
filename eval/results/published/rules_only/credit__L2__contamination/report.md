---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: rules_only
model: fake
run_id: credit_default-rules_only-20260918T065324Z-bd5861e9
data_mode: synthetic
synthetic_n: 5000
grounding_precision_pre: 1.0000
grounding_precision_post: 1.0000
n_claims: 214
n_findings_by_severity: {high: 0, medium: 1, low: 1, info: 0}
generated: "2026-09-18T06:53:24Z"
illustrative: false
---

# Validation report — `credit_default` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `credit_default` v1.0 | `rules_only` | fake | synthetic, n = 5000 | 1.0000 → 1.0000 | 0 / 1 / 1 / 0 |
<!-- quaestor:renderer:end -->

This section follows the model risk management guidance at [[reg:SR26-2:V.1.b]].
The value of `calibration_slope.test` is 1.001 [[art:95a66bf5:calibration_slope.test]].
The value of `calibration_slope.train` is 1.002 [[art:9f4641a6:calibration_slope.train]].
The value of `challenger.delta_auc` is 0.08651 [[art:95cce9d6:challenger.delta_auc]].
The value of `condition_number` is 5.557 [[art:8029574b:condition_number]].
The value of `csi.max` is 0.02201 [[art:897f0064:csi.max]].
The value of `metrics.test.auc` is 0.748 [[art:33170ddf:metrics.test.auc]].
The value of `metrics.test.brier` is 0.149 [[art:3be8087d:metrics.test.brier]].
The value of `metrics.test.event_rate` is 0.2247 [[art:9209d200:metrics.test.event_rate]].
The value of `metrics.test.gini` is 0.4961 [[art:e7acec22:metrics.test.gini]].
The value of `metrics.test.ks` is 0.419 [[art:63623085:metrics.test.ks]].
The value of `metrics.test.logloss` is 0.4674 [[art:33a9bfcd:metrics.test.logloss]].
The value of `metrics.test.mean_predicted` is 0.2213 [[art:4920f430:metrics.test.mean_predicted]].
The value of `metrics.test.n` is 1500 [[art:64fcf14d:metrics.test.n]].
The value of `metrics.train.auc` is 0.7589 [[art:92ca327f:metrics.train.auc]].
The value of `metrics.train.brier` is 0.149 [[art:0215ac1d:metrics.train.brier]].
The value of `metrics.train.event_rate` is 0.2245 [[art:cf2ea9d7:metrics.train.event_rate]].
The value of `metrics.train.gini` is 0.5177 [[art:b7417c30:metrics.train.gini]].
The value of `metrics.train.ks` is 0.4447 [[art:39f29309:metrics.train.ks]].
The value of `metrics.train.logloss` is 0.465 [[art:a9dde81e:metrics.train.logloss]].
The value of `metrics.train.mean_predicted` is 0.2246 [[art:233a7dff:metrics.train.mean_predicted]].
The value of `metrics.train.n` is 3545 [[art:343c4301:metrics.train.n]].
The value of `profile.test.n` is 1500 [[art:2193cf5f:profile.test.n]].
The value of `profile.train.n` is 3545 [[art:1ff4e472:profile.train.n]].
The value of `psi.max` is 0.01082 [[art:9300bdd4:psi.max]].
The value of `runtime.max_seconds` is 300 [[art:2ad8d1a5:runtime.max_seconds]].
The value of `threshold.package.auc.test.min` is 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]].
The value of `threshold.package.brier.test.max` is 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]].
The value of `threshold.package.calibration_slope.test.max` is 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The value of `threshold.package.calibration_slope.test.min` is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
The value of `vif.max` is 7.31 [[art:d8e9619c:vif.max]].

## 2. Conceptual soundness

This section follows the model risk management guidance at [[reg:SR26-2:V.1.a]].
The value of `ablation.age.delta_auc` is -0.00006124 [[art:fa888618:ablation.age.delta_auc]].
The value of `ablation.baseline_auc` is 0.748 [[art:818e6d21:ablation.baseline_auc]].
The value of `ablation.bill_mean_6m.delta_auc` is -0.001513 [[art:0fff644e:ablation.bill_mean_6m.delta_auc]].
The value of `ablation.bill_trend_6m.delta_auc` is 0.003776 [[art:80be2a7e:ablation.bill_trend_6m.delta_auc]].
The value of `ablation.delinq_count_6m.delta_auc` is 0.000671 [[art:a35dafd6:ablation.delinq_count_6m.delta_auc]].
The value of `ablation.delinq_last.delta_auc` is -0.07609 [[art:9bdbb0b5:ablation.delinq_last.delta_auc]].
The value of `ablation.delinq_max_6m.delta_auc` is 0.000296 [[art:975f1df6:ablation.delinq_max_6m.delta_auc]].
The value of `ablation.limit_bal.delta_auc` is 0.0004695 [[art:d47e9a58:ablation.limit_bal.delta_auc]].
The value of `ablation.pay_ratio_last.delta_auc` is 0.002847 [[art:1918798e:ablation.pay_ratio_last.delta_auc]].
The value of `ablation.pay_ratio_mean_6m.delta_auc` is 0.007313 [[art:48fca3ba:ablation.pay_ratio_mean_6m.delta_auc]].
The value of `ablation.utilisation.delta_auc` is -0.01974 [[art:c8ce0123:ablation.utilisation.delta_auc]].
The value of `challenger.auc` is 0.8346 [[art:d1533f6e:challenger.auc]].
The value of `challenger.brier` is 0.1214 [[art:e580bfb4:challenger.brier]].
The value of `challenger.delta_auc` is 0.08651 [[art:95cce9d6:challenger.delta_auc]].
The value of `metrics.test.auc` is 0.748 [[art:33170ddf:metrics.test.auc]].
The value of `metrics.test.brier` is 0.149 [[art:3be8087d:metrics.test.brier]].
The value of `sign_check.age.agrees` is 1 [[art:4116add1:sign_check.age.agrees]].
The value of `sign_check.age.coef_sign` is -1 [[art:6172eb93:sign_check.age.coef_sign]].
The value of `sign_check.age.univariate_direction` is -1 [[art:66364583:sign_check.age.univariate_direction]].
The value of `sign_check.bill_mean_6m.agrees` is 1 [[art:89279c3b:sign_check.bill_mean_6m.agrees]].
The value of `sign_check.bill_mean_6m.coef_sign` is -1 [[art:cee1a18f:sign_check.bill_mean_6m.coef_sign]].
The value of `sign_check.bill_mean_6m.univariate_direction` is -1 [[art:23b89c5d:sign_check.bill_mean_6m.univariate_direction]].
The value of `sign_check.bill_trend_6m.agrees` is 1 [[art:ff3cb24a:sign_check.bill_trend_6m.agrees]].
The value of `sign_check.bill_trend_6m.coef_sign` is -1 [[art:7fd8474e:sign_check.bill_trend_6m.coef_sign]].
The value of `sign_check.bill_trend_6m.univariate_direction` is -1 [[art:a9bff389:sign_check.bill_trend_6m.univariate_direction]].
The value of `sign_check.delinq_count_6m.agrees` is 1 [[art:a337d16b:sign_check.delinq_count_6m.agrees]].
The value of `sign_check.delinq_count_6m.coef_sign` is 1 [[art:17afb6f9:sign_check.delinq_count_6m.coef_sign]].
The value of `sign_check.delinq_count_6m.univariate_direction` is 1 [[art:549e904e:sign_check.delinq_count_6m.univariate_direction]].
The value of `sign_check.delinq_last.agrees` is 1 [[art:a8ba9372:sign_check.delinq_last.agrees]].
The value of `sign_check.delinq_last.coef_sign` is 1 [[art:50d352f8:sign_check.delinq_last.coef_sign]].
The value of `sign_check.delinq_last.univariate_direction` is 1 [[art:a78648ba:sign_check.delinq_last.univariate_direction]].
The value of `sign_check.delinq_max_6m.agrees` is 0 [[art:c946359c:sign_check.delinq_max_6m.agrees]].
The value of `sign_check.delinq_max_6m.coef_sign` is -1 [[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]].
The value of `sign_check.delinq_max_6m.univariate_direction` is 1 [[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]].
The value of `sign_check.limit_bal.agrees` is 0 [[art:0278aad1:sign_check.limit_bal.agrees]].
The value of `sign_check.limit_bal.coef_sign` is 1 [[art:6af6aef2:sign_check.limit_bal.coef_sign]].
The value of `sign_check.limit_bal.univariate_direction` is -1 [[art:56d284d6:sign_check.limit_bal.univariate_direction]].
The value of `sign_check.n_disagreements` is 3 [[art:e223cd4a:sign_check.n_disagreements]].
The value of `sign_check.pay_ratio_last.agrees` is 0 [[art:79abee77:sign_check.pay_ratio_last.agrees]].
The value of `sign_check.pay_ratio_last.coef_sign` is 1 [[art:f018263e:sign_check.pay_ratio_last.coef_sign]].
The value of `sign_check.pay_ratio_last.univariate_direction` is -1 [[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]].
The value of `sign_check.pay_ratio_mean_6m.agrees` is 1 [[art:7e9a76ca:sign_check.pay_ratio_mean_6m.agrees]].
The value of `sign_check.pay_ratio_mean_6m.coef_sign` is -1 [[art:077bb6b2:sign_check.pay_ratio_mean_6m.coef_sign]].
The value of `sign_check.pay_ratio_mean_6m.univariate_direction` is -1 [[art:24dcef24:sign_check.pay_ratio_mean_6m.univariate_direction]].
The value of `sign_check.utilisation.agrees` is 1 [[art:d0c9a130:sign_check.utilisation.agrees]].
The value of `sign_check.utilisation.coef_sign` is 1 [[art:85badc3c:sign_check.utilisation.coef_sign]].
The value of `sign_check.utilisation.univariate_direction` is 1 [[art:f0995196:sign_check.utilisation.univariate_direction]].
The value of `threshold.E1.delta_auc` is 0.03 [[art:e042774c:threshold.E1.delta_auc]].
Candidates raised on this section's material: E1 (see the findings section).

## 3. Data integrity and drift

This section follows the model risk management guidance at [[reg:SR26-2:V.1.a]].
The value of `csi.age` is 0.0009881 [[art:76338ca5:csi.age]].
The value of `csi.bill_mean_6m` is 0.002641 [[art:9105b83f:csi.bill_mean_6m]].
The value of `csi.bill_trend_6m` is 0.006491 [[art:85619225:csi.bill_trend_6m]].
The value of `csi.delinq_count_6m` is 0.002326 [[art:77a551ed:csi.delinq_count_6m]].
The value of `csi.delinq_last` is 0.02201 [[art:55177f94:csi.delinq_last]].
The value of `csi.delinq_max_6m` is 0.0007952 [[art:e6506c3b:csi.delinq_max_6m]].
The value of `csi.limit_bal` is 0.001136 [[art:f96c2df9:csi.limit_bal]].
The value of `csi.max` is 0.02201 [[art:897f0064:csi.max]].
The value of `csi.pay_ratio_last` is 0.002204 [[art:e23fdafd:csi.pay_ratio_last]].
The value of `csi.pay_ratio_mean_6m` is 0.001619 [[art:ed28e38f:csi.pay_ratio_mean_6m]].
The value of `csi.utilisation` is 0.004851 [[art:dfb8439b:csi.utilisation]].
The value of `leakage.duplicates.train` is 0 [[art:4474c227:leakage.duplicates.train]].
The value of `leakage.name_screen.n_matched` is 0 [[art:407e62be:leakage.name_screen.n_matched]].
The value of `leakage.overlap` is 0.03 [[art:a2cd9767:leakage.overlap]].
The value of `leakage.overlap.features` is 0.03 [[art:dc2d0a43:leakage.overlap.features]].
The value of `leakage.overlap.ids` is 0 [[art:63d37fc5:leakage.overlap.ids]].
The value of `leakage.target_corr.max_single_feature_auc` is 0.6819 [[art:7c15f992:leakage.target_corr.max_single_feature_auc]].
The value of `leakage.timing.n_flagged` is 0 [[art:742bcd24:leakage.timing.n_flagged]].
The value of `profile.test.missing.max` is 0 [[art:f813848d:profile.test.missing.max]].
The value of `profile.test.n` is 1500 [[art:2193cf5f:profile.test.n]].
The value of `profile.train.missing.max` is 0 [[art:050a3099:profile.train.missing.max]].
The value of `profile.train.n` is 3545 [[art:1ff4e472:profile.train.n]].
The value of `psi.age` is 0.008244 [[art:54a6d5c8:psi.age]].
The value of `psi.bill_mean_6m` is 0.007417 [[art:05ce5247:psi.bill_mean_6m]].
The value of `psi.bill_trend_6m` is 0.009307 [[art:b8409498:psi.bill_trend_6m]].
The value of `psi.delinq_count_6m` is 0.001826 [[art:95ad0bbe:psi.delinq_count_6m]].
The value of `psi.delinq_last` is 0.002615 [[art:7298b08b:psi.delinq_last]].
The value of `psi.delinq_max_6m` is 0.004879 [[art:548e3455:psi.delinq_max_6m]].
The value of `psi.limit_bal` is 0.01082 [[art:5db122d3:psi.limit_bal]].
The value of `psi.max` is 0.01082 [[art:9300bdd4:psi.max]].
The value of `psi.pay_ratio_last` is 0.004465 [[art:ed34c7dc:psi.pay_ratio_last]].
The value of `psi.pay_ratio_mean_6m` is 0.005142 [[art:bca4bf06:psi.pay_ratio_mean_6m]].
The value of `psi.utilisation` is 0.004511 [[art:21c53bd0:psi.utilisation]].
The value of `psi.y_score` is 0.004938 [[art:63344faa:psi.y_score]].
The value of `threshold.D1.missing_gap` is 0.1 [[art:9cce25ea:threshold.D1.missing_gap]].
The value of `threshold.L1.single_feature_auc` is 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]].
The value of `threshold.L2.overlap` is 0.005 [[art:9f336eaf:threshold.L2.overlap]].
The value of `threshold.L2.overlap.features_effective` is 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].
The value of `threshold.S1.psi` is 0.25 [[art:278b9016:threshold.S1.psi]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
Candidates raised on this section's material: L2 (see the findings section).

## 4. Outcomes analysis

This section follows the model risk management guidance at [[reg:SR26-2:V.1.b]].
The value of `calibration.mean_rel_gap.test` is 0.01499 [[art:02e35a65:calibration.mean_rel_gap.test]].
The value of `calibration.mean_rel_gap.train` is 0.000327 [[art:060d5049:calibration.mean_rel_gap.train]].
The value of `calibration_intercept.test` is 0.02371 [[art:ec6ca742:calibration_intercept.test]].
The value of `calibration_intercept.train` is 0.001736 [[art:0b1e1ff9:calibration_intercept.train]].
The value of `calibration_slope.test` is 1.001 [[art:95a66bf5:calibration_slope.test]].
The value of `calibration_slope.train` is 1.002 [[art:9f4641a6:calibration_slope.train]].
The value of `deciles.test.top2_capture` is 0.4718 [[art:d4a1cf7d:deciles.test.top2_capture]].
The value of `deciles.train.top2_capture` is 0.4485 [[art:15637767:deciles.train.top2_capture]].
The value of `metrics.test.auc` is 0.748 [[art:33170ddf:metrics.test.auc]].
The value of `metrics.test.brier` is 0.149 [[art:3be8087d:metrics.test.brier]].
The value of `metrics.test.event_rate` is 0.2247 [[art:9209d200:metrics.test.event_rate]].
The value of `metrics.test.gini` is 0.4961 [[art:e7acec22:metrics.test.gini]].
The value of `metrics.test.ks` is 0.419 [[art:63623085:metrics.test.ks]].
The value of `metrics.test.logloss` is 0.4674 [[art:33a9bfcd:metrics.test.logloss]].
The value of `metrics.test.mean_predicted` is 0.2213 [[art:4920f430:metrics.test.mean_predicted]].
The value of `metrics.test.n` is 1500 [[art:64fcf14d:metrics.test.n]].
The value of `metrics.train.auc` is 0.7589 [[art:92ca327f:metrics.train.auc]].
The value of `metrics.train.brier` is 0.149 [[art:0215ac1d:metrics.train.brier]].
The value of `metrics.train.event_rate` is 0.2245 [[art:cf2ea9d7:metrics.train.event_rate]].
The value of `metrics.train.gini` is 0.5177 [[art:b7417c30:metrics.train.gini]].
The value of `metrics.train.ks` is 0.4447 [[art:39f29309:metrics.train.ks]].
The value of `metrics.train.logloss` is 0.465 [[art:a9dde81e:metrics.train.logloss]].
The value of `metrics.train.mean_predicted` is 0.2246 [[art:233a7dff:metrics.train.mean_predicted]].
The value of `metrics.train.n` is 3545 [[art:343c4301:metrics.train.n]].
The value of `psi.age` is 0.008244 [[art:54a6d5c8:psi.age]].
The value of `psi.bill_mean_6m` is 0.007417 [[art:05ce5247:psi.bill_mean_6m]].
The value of `psi.bill_trend_6m` is 0.009307 [[art:b8409498:psi.bill_trend_6m]].
The value of `psi.delinq_count_6m` is 0.001826 [[art:95ad0bbe:psi.delinq_count_6m]].
The value of `psi.delinq_last` is 0.002615 [[art:7298b08b:psi.delinq_last]].
The value of `psi.delinq_max_6m` is 0.004879 [[art:548e3455:psi.delinq_max_6m]].
The value of `psi.limit_bal` is 0.01082 [[art:5db122d3:psi.limit_bal]].
The value of `psi.max` is 0.01082 [[art:9300bdd4:psi.max]].
The value of `psi.pay_ratio_last` is 0.004465 [[art:ed34c7dc:psi.pay_ratio_last]].
The value of `psi.pay_ratio_mean_6m` is 0.005142 [[art:bca4bf06:psi.pay_ratio_mean_6m]].
The value of `psi.utilisation` is 0.004511 [[art:21c53bd0:psi.utilisation]].
The value of `psi.y_score` is 0.004938 [[art:63344faa:psi.y_score]].
The value of `rule.calibration_first_event_rate` is 0.05 [[art:42f1351e:rule.calibration_first_event_rate]].
The value of `threshold.C1.calibration_slope.max` is 1.2 [[art:b6672579:threshold.C1.calibration_slope.max]].
The value of `threshold.C1.calibration_slope.min` is 0.8 [[art:749634ae:threshold.C1.calibration_slope.min]].
The value of `threshold.C1.mean_ratio_rel` is 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
The value of `threshold.D1.missing_gap` is 0.1 [[art:9cce25ea:threshold.D1.missing_gap]].
The value of `threshold.E1.delta_auc` is 0.03 [[art:e042774c:threshold.E1.delta_auc]].
The value of `threshold.L1.single_feature_auc` is 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]].
The value of `threshold.L2.overlap` is 0.005 [[art:9f336eaf:threshold.L2.overlap]].
The value of `threshold.L2.overlap.features_effective` is 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].
The value of `threshold.M1.condition_number` is 30 [[art:7e52fd7a:threshold.M1.condition_number]].
The value of `threshold.M1.vif` is 10 [[art:aeb4f33c:threshold.M1.vif]].
The value of `threshold.O1.auc_gap` is 0.08 [[art:630f28f4:threshold.O1.auc_gap]].
The value of `threshold.S1.psi` is 0.25 [[art:278b9016:threshold.S1.psi]].
The value of `threshold.package.auc.test.min` is 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]].
The value of `threshold.package.brier.test.max` is 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]].
The value of `threshold.package.calibration_slope.test.max` is 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The value of `threshold.package.calibration_slope.test.min` is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
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

## 5. Sensitivity and scenario analysis

This section follows the model risk management guidance at [[reg:SR26-2:V.1.a]].
The value of `condition_number` is 5.557 [[art:8029574b:condition_number]].
The value of `threshold.M1.condition_number` is 30 [[art:7e52fd7a:threshold.M1.condition_number]].
The value of `threshold.M1.vif` is 10 [[art:aeb4f33c:threshold.M1.vif]].
The value of `vif.age` is 1.002 [[art:628d9c69:vif.age]].
The value of `vif.bill_mean_6m` is 7.31 [[art:1915242e:vif.bill_mean_6m]].
The value of `vif.bill_trend_6m` is 1.201 [[art:78a03a7b:vif.bill_trend_6m]].
The value of `vif.delinq_count_6m` is 2.567 [[art:ca9bf9ad:vif.delinq_count_6m]].
The value of `vif.delinq_last` is 1.414 [[art:a561c855:vif.delinq_last]].
The value of `vif.delinq_max_6m` is 2.403 [[art:95ebdd8f:vif.delinq_max_6m]].
The value of `vif.limit_bal` is 4.82 [[art:eeeb5c27:vif.limit_bal]].
The value of `vif.max` is 7.31 [[art:d8e9619c:vif.max]].
The value of `vif.pay_ratio_last` is 7.286 [[art:e30c6fbd:vif.pay_ratio_last]].
The value of `vif.pay_ratio_mean_6m` is 7.28 [[art:4d1589cd:vif.pay_ratio_mean_6m]].
The value of `vif.utilisation` is 3.215 [[art:7298e587:vif.utilisation]].

## 6. Findings and recommendations

This section follows the model risk management guidance at [[reg:SR26-2:VI.3]].

### F-001 · L2 contamination · severity **medium**

**A `L2` finding, raised by `check_leakage` at severity `medium`.**
Its evidence is the artifacts cited in this section; the check's own account of it is recorded in `findings.json`.

### F-002 · E1 effective challenge · severity **low**

**A `E1` finding, raised by `challenger_compare` at severity `low`.**
Its evidence is the artifacts cited in this section; the check's own account of it is recorded in `findings.json`.
The value of `challenger.auc` is 0.8346 [[art:d1533f6e:challenger.auc]].
The value of `challenger.delta_auc` is 0.08651 [[art:95cce9d6:challenger.delta_auc]].
The value of `leakage.duplicates.train` is 0 [[art:4474c227:leakage.duplicates.train]].
The value of `leakage.overlap.features` is 0.03 [[art:dc2d0a43:leakage.overlap.features]].
The value of `metrics.test.auc` is 0.748 [[art:33170ddf:metrics.test.auc]].
The value of `sign_check.delinq_max_6m.agrees` is 0 [[art:c946359c:sign_check.delinq_max_6m.agrees]].
The value of `sign_check.delinq_max_6m.coef_sign` is -1 [[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]].
The value of `sign_check.delinq_max_6m.univariate_direction` is 1 [[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]].
The value of `sign_check.limit_bal.agrees` is 0 [[art:0278aad1:sign_check.limit_bal.agrees]].
The value of `sign_check.limit_bal.coef_sign` is 1 [[art:6af6aef2:sign_check.limit_bal.coef_sign]].
The value of `sign_check.limit_bal.univariate_direction` is -1 [[art:56d284d6:sign_check.limit_bal.univariate_direction]].
The value of `sign_check.pay_ratio_last.agrees` is 0 [[art:79abee77:sign_check.pay_ratio_last.agrees]].
The value of `sign_check.pay_ratio_last.coef_sign` is 1 [[art:f018263e:sign_check.pay_ratio_last.coef_sign]].
The value of `sign_check.pay_ratio_last.univariate_direction` is -1 [[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]].
The value of `threshold.E1.delta_auc` is 0.03 [[art:e042774c:threshold.E1.delta_auc]].
The value of `threshold.L2.overlap` is 0.005 [[art:9f336eaf:threshold.L2.overlap]].
The value of `threshold.L2.overlap.features_effective` is 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1, S1), `compute_metrics` (T1, C1, O1), `check_leakage` (L1), `check_collinearity` (M1).

### Open items

No open item was recorded for this validation.

## 7. Ongoing monitoring recommendations

This section follows the model risk management guidance at [[reg:SR26-2:V.2]].
The value of `calibration_slope.test` is 1.001 [[art:95a66bf5:calibration_slope.test]].
The value of `metrics.test.auc` is 0.748 [[art:33170ddf:metrics.test.auc]].
The value of `metrics.test.brier` is 0.149 [[art:3be8087d:metrics.test.brier]].
The value of `psi.max` is 0.01082 [[art:9300bdd4:psi.max]].
The value of `rule.calibration_first_event_rate` is 0.05 [[art:42f1351e:rule.calibration_first_event_rate]].
The value of `threshold.package.auc.test.min` is 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]].
The value of `threshold.package.brier.test.max` is 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]].
The value of `threshold.package.calibration_slope.test.max` is 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The value of `threshold.package.calibration_slope.test.min` is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].

## Appendix A — Claims

Grounding precision 1.0000 before repair (214 of 214 claims verified) and 1.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 31/31; conceptual_soundness 48/48; data_integrity 40/40; outcomes 54/54; sensitivity 14/14; findings 17/17; monitoring 10/10.

Developer claims: The package declares 2 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). See Appendix D.

Excluded numeric tokens (not claims): citation_hash (95a66bf5, 9f4641a6, 95cce9d6, 8029574b); regulatory_section_id (SR26-2:V.1.b, SR26-2:V.1.a, SR26-2:VI.3, SR26-2:V.2); finding_id (F-001, F-002).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The value of `calibration_slope.test` is 1.001 . | 1.001 | ratio | calibration_slope |  | eq | `[[art:95a66bf5:calibration_slope.test]]` | verified | 1.000821291 |
| 2 | summary | The value of `calibration_slope.train` is 1.002 . | 1.002 | ratio | calibration_slope |  | eq | `[[art:9f4641a6:calibration_slope.train]]` | verified | 1.001952049 |
| 3 | summary | The value of `challenger.delta_auc` is 0.08651 . | 0.08651 | ratio | challenger |  | eq | `[[art:95cce9d6:challenger.delta_auc]]` | verified | 0.08651267698 |
| 4 | summary | The value of `condition_number` is 5.557 . | 5.557 | ratio | condition_number |  | eq | `[[art:8029574b:condition_number]]` | verified | 5.556505365 |
| 5 | summary | The value of `csi.max` is 0.02201 . | 0.02201 | ratio | csi |  | eq | `[[art:897f0064:csi.max]]` | verified | 0.02201119885 |
| 6 | summary | The value of `metrics.test.auc` is 0.748 . | 0.748 | ratio | metrics |  | eq | `[[art:33170ddf:metrics.test.auc]]` | verified | 0.748047488 |
| 7 | summary | The value of `metrics.test.brier` is 0.149 . | 0.149 | ratio | metrics |  | eq | `[[art:3be8087d:metrics.test.brier]]` | verified | 0.1489501682 |
| 8 | summary | The value of `metrics.test.event_rate` is 0.2247 . | 0.2247 | ratio | metrics |  | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 9 | summary | The value of `metrics.test.gini` is 0.4961 . | 0.4961 | ratio | metrics |  | eq | `[[art:e7acec22:metrics.test.gini]]` | verified | 0.4960949759 |
| 10 | summary | The value of `metrics.test.ks` is 0.419 . | 0.419 | ratio | metrics |  | eq | `[[art:63623085:metrics.test.ks]]` | verified | 0.4189589494 |
| 11 | summary | The value of `metrics.test.logloss` is 0.4674 . | 0.4674 | ratio | metrics |  | eq | `[[art:33a9bfcd:metrics.test.logloss]]` | verified | 0.4673916168 |
| 12 | summary | The value of `metrics.test.mean_predicted` is 0.2213 . | 0.2213 | ratio | metrics |  | eq | `[[art:4920f430:metrics.test.mean_predicted]]` | verified | 0.2212995331 |
| 13 | summary | The value of `metrics.test.n` is 1500 . | 1500 | ratio | metrics |  | eq | `[[art:64fcf14d:metrics.test.n]]` | verified | 1500 |
| 14 | summary | The value of `metrics.train.auc` is 0.7589 . | 0.7589 | ratio | metrics |  | eq | `[[art:92ca327f:metrics.train.auc]]` | verified | 0.7588597772 |
| 15 | summary | The value of `metrics.train.brier` is 0.149 . | 0.149 | ratio | metrics |  | eq | `[[art:0215ac1d:metrics.train.brier]]` | verified | 0.1490409093 |
| 16 | summary | The value of `metrics.train.event_rate` is 0.2245 . | 0.2245 | ratio | metrics |  | eq | `[[art:cf2ea9d7:metrics.train.event_rate]]` | verified | 0.2245416079 |
| 17 | summary | The value of `metrics.train.gini` is 0.5177 . | 0.5177 | ratio | metrics |  | eq | `[[art:b7417c30:metrics.train.gini]]` | verified | 0.5177195545 |
| 18 | summary | The value of `metrics.train.ks` is 0.4447 . | 0.4447 | ratio | metrics |  | eq | `[[art:39f29309:metrics.train.ks]]` | verified | 0.4447131072 |
| 19 | summary | The value of `metrics.train.logloss` is 0.465 . | 0.465 | ratio | metrics |  | eq | `[[art:a9dde81e:metrics.train.logloss]]` | verified | 0.4650342534 |
| 20 | summary | The value of `metrics.train.mean_predicted` is 0.2246 . | 0.2246 | ratio | metrics |  | eq | `[[art:233a7dff:metrics.train.mean_predicted]]` | verified | 0.2246150387 |
| 21 | summary | The value of `metrics.train.n` is 3545 . | 3545 | ratio | metrics |  | eq | `[[art:343c4301:metrics.train.n]]` | verified | 3545 |
| 22 | summary | The value of `profile.test.n` is 1500 . | 1500 | ratio | profile |  | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 23 | summary | The value of `profile.train.n` is 3545 . | 3545 | ratio | profile |  | eq | `[[art:1ff4e472:profile.train.n]]` | verified | 3545 |
| 24 | summary | The value of `psi.max` is 0.01082 . | 0.01082 | ratio | psi |  | eq | `[[art:9300bdd4:psi.max]]` | verified | 0.01081685833 |
| 25 | summary | The value of `runtime.max_seconds` is 300 . | 300 | ratio | runtime |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 26 | summary | The value of `threshold.package.auc.test.min` is 0.7 . | 0.7 | ratio | threshold |  | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 27 | summary | The value of `threshold.package.brier.test.max` is 0.2 . | 0.2 | ratio | threshold |  | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 28 | summary | The value of `threshold.package.calibration_slope.test.max`… | 1.2 | ratio | threshold |  | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 29 | summary | The value of `threshold.package.calibration_slope.test.min`… | 0.8 | ratio | threshold |  | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 30 | summary | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 31 | summary | The value of `vif.max` is 7.31 . | 7.31 | ratio | vif |  | eq | `[[art:d8e9619c:vif.max]]` | verified | 7.309956746 |
| 32 | conceptual_soundness | The value of `ablation.age.delta_auc` is -0.00006124 . | -6.124e-05 | ratio | ablation |  | eq | `[[art:fa888618:ablation.age.delta_auc]]` | verified | -6.123526845e-05 |
| 33 | conceptual_soundness | The value of `ablation.baseline_auc` is 0.748 . | 0.748 | ratio | ablation |  | eq | `[[art:818e6d21:ablation.baseline_auc]]` | verified | 0.748047488 |
| 34 | conceptual_soundness | The value of `ablation.bill_mean_6m.delta_auc` is -0.001513… | -0.001513 | ratio | ablation |  | eq | `[[art:0fff644e:ablation.bill_mean_6m.delta_auc]]` | verified | -0.001513021425 |
| 35 | conceptual_soundness | The value of `ablation.bill_trend_6m.delta_auc` is 0.003776… | 0.003776 | ratio | ablation |  | eq | `[[art:80be2a7e:ablation.bill_trend_6m.delta_auc]]` | verified | 0.003776174888 |
| 36 | conceptual_soundness | The value of `ablation.delinq_count_6m.delta_auc` is 0.00067… | 0.000671 | ratio | ablation |  | eq | `[[art:a35dafd6:ablation.delinq_count_6m.delta_auc]]` | verified | 0.0006710364835 |
| 37 | conceptual_soundness | The value of `ablation.delinq_last.delta_auc` is -0.07609 . | -0.07609 | ratio | ablation |  | eq | `[[art:9bdbb0b5:ablation.delinq_last.delta_auc]]` | verified | -0.07608737252 |
| 38 | conceptual_soundness | The value of `ablation.delinq_max_6m.delta_auc` is 0.000296… | 0.000296 | ratio | ablation |  | eq | `[[art:975f1df6:ablation.delinq_max_6m.delta_auc]]` | verified | 0.0002959704642 |
| 39 | conceptual_soundness | The value of `ablation.limit_bal.delta_auc` is 0.0004695 . | 0.0004695 | ratio | ablation |  | eq | `[[art:d47e9a58:ablation.limit_bal.delta_auc]]` | verified | 0.0004694703915 |
| 40 | conceptual_soundness | The value of `ablation.pay_ratio_last.delta_auc` is 0.002847… | 0.002847 | ratio | ablation |  | eq | `[[art:1918798e:ablation.pay_ratio_last.delta_auc]]` | verified | 0.002847439983 |
| 41 | conceptual_soundness | The value of `ablation.pay_ratio_mean_6m.delta_auc` is 0.007… | 0.007313 | ratio | ablation |  | eq | `[[art:48fca3ba:ablation.pay_ratio_mean_6m.delta_auc]]` | verified | 0.007312511641 |
| 42 | conceptual_soundness | The value of `ablation.utilisation.delta_auc` is -0.01974 . | -0.01974 | ratio | ablation |  | eq | `[[art:c8ce0123:ablation.utilisation.delta_auc]]` | verified | -0.01973561673 |
| 43 | conceptual_soundness | The value of `challenger.auc` is 0.8346 . | 0.8346 | ratio | challenger |  | eq | `[[art:d1533f6e:challenger.auc]]` | verified | 0.8345601649 |
| 44 | conceptual_soundness | The value of `challenger.brier` is 0.1214 . | 0.1214 | ratio | challenger |  | eq | `[[art:e580bfb4:challenger.brier]]` | verified | 0.1213893435 |
| 45 | conceptual_soundness | The value of `challenger.delta_auc` is 0.08651 . | 0.08651 | ratio | challenger |  | eq | `[[art:95cce9d6:challenger.delta_auc]]` | verified | 0.08651267698 |
| 46 | conceptual_soundness | The value of `metrics.test.auc` is 0.748 . | 0.748 | ratio | metrics |  | eq | `[[art:33170ddf:metrics.test.auc]]` | verified | 0.748047488 |
| 47 | conceptual_soundness | The value of `metrics.test.brier` is 0.149 . | 0.149 | ratio | metrics |  | eq | `[[art:3be8087d:metrics.test.brier]]` | verified | 0.1489501682 |
| 48 | conceptual_soundness | The value of `sign_check.age.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:4116add1:sign_check.age.agrees]]` | verified | 1 |
| 49 | conceptual_soundness | The value of `sign_check.age.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:6172eb93:sign_check.age.coef_sign]]` | verified | -1 |
| 50 | conceptual_soundness | The value of `sign_check.age.univariate_direction` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:66364583:sign_check.age.univariate_direction]]` | verified | -1 |
| 51 | conceptual_soundness | The value of `sign_check.bill_mean_6m.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:89279c3b:sign_check.bill_mean_6m.agrees]]` | verified | 1 |
| 52 | conceptual_soundness | The value of `sign_check.bill_mean_6m.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:cee1a18f:sign_check.bill_mean_6m.coef_sign]]` | verified | -1 |
| 53 | conceptual_soundness | The value of `sign_check.bill_mean_6m.univariate_direction`… | -1 | ratio | sign_check |  | eq | `[[art:23b89c5d:sign_check.bill_mean_6m.univariate_direction]]` | verified | -1 |
| 54 | conceptual_soundness | The value of `sign_check.bill_trend_6m.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:ff3cb24a:sign_check.bill_trend_6m.agrees]]` | verified | 1 |
| 55 | conceptual_soundness | The value of `sign_check.bill_trend_6m.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:7fd8474e:sign_check.bill_trend_6m.coef_sign]]` | verified | -1 |
| 56 | conceptual_soundness | The value of `sign_check.bill_trend_6m.univariate_direction`… | -1 | ratio | sign_check |  | eq | `[[art:a9bff389:sign_check.bill_trend_6m.univariate_direction]]` | verified | -1 |
| 57 | conceptual_soundness | The value of `sign_check.delinq_count_6m.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:a337d16b:sign_check.delinq_count_6m.agrees]]` | verified | 1 |
| 58 | conceptual_soundness | The value of `sign_check.delinq_count_6m.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:17afb6f9:sign_check.delinq_count_6m.coef_sign]]` | verified | 1 |
| 59 | conceptual_soundness | The value of `sign_check.delinq_count_6m.univariate_directio… | 1 | ratio | sign_check |  | eq | `[[art:549e904e:sign_check.delinq_count_6m.univariate_direction]]` | verified | 1 |
| 60 | conceptual_soundness | The value of `sign_check.delinq_last.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:a8ba9372:sign_check.delinq_last.agrees]]` | verified | 1 |
| 61 | conceptual_soundness | The value of `sign_check.delinq_last.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:50d352f8:sign_check.delinq_last.coef_sign]]` | verified | 1 |
| 62 | conceptual_soundness | The value of `sign_check.delinq_last.univariate_direction` i… | 1 | ratio | sign_check |  | eq | `[[art:a78648ba:sign_check.delinq_last.univariate_direction]]` | verified | 1 |
| 63 | conceptual_soundness | The value of `sign_check.delinq_max_6m.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:c946359c:sign_check.delinq_max_6m.agrees]]` | verified | 0 |
| 64 | conceptual_soundness | The value of `sign_check.delinq_max_6m.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]]` | verified | -1 |
| 65 | conceptual_soundness | The value of `sign_check.delinq_max_6m.univariate_direction`… | 1 | ratio | sign_check |  | eq | `[[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]]` | verified | 1 |
| 66 | conceptual_soundness | The value of `sign_check.limit_bal.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:0278aad1:sign_check.limit_bal.agrees]]` | verified | 0 |
| 67 | conceptual_soundness | The value of `sign_check.limit_bal.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:6af6aef2:sign_check.limit_bal.coef_sign]]` | verified | 1 |
| 68 | conceptual_soundness | The value of `sign_check.limit_bal.univariate_direction` is… | -1 | ratio | sign_check |  | eq | `[[art:56d284d6:sign_check.limit_bal.univariate_direction]]` | verified | -1 |
| 69 | conceptual_soundness | The value of `sign_check.n_disagreements` is 3 . | 3 | ratio | sign_check |  | eq | `[[art:e223cd4a:sign_check.n_disagreements]]` | verified | 3 |
| 70 | conceptual_soundness | The value of `sign_check.pay_ratio_last.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:79abee77:sign_check.pay_ratio_last.agrees]]` | verified | 0 |
| 71 | conceptual_soundness | The value of `sign_check.pay_ratio_last.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:f018263e:sign_check.pay_ratio_last.coef_sign]]` | verified | 1 |
| 72 | conceptual_soundness | The value of `sign_check.pay_ratio_last.univariate_direction… | -1 | ratio | sign_check |  | eq | `[[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]]` | verified | -1 |
| 73 | conceptual_soundness | The value of `sign_check.pay_ratio_mean_6m.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:7e9a76ca:sign_check.pay_ratio_mean_6m.agrees]]` | verified | 1 |
| 74 | conceptual_soundness | The value of `sign_check.pay_ratio_mean_6m.coef_sign` is -1… | -1 | ratio | sign_check |  | eq | `[[art:077bb6b2:sign_check.pay_ratio_mean_6m.coef_sign]]` | verified | -1 |
| 75 | conceptual_soundness | The value of `sign_check.pay_ratio_mean_6m.univariate_direct… | -1 | ratio | sign_check |  | eq | `[[art:24dcef24:sign_check.pay_ratio_mean_6m.univariate_direction]]` | verified | -1 |
| 76 | conceptual_soundness | The value of `sign_check.utilisation.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:d0c9a130:sign_check.utilisation.agrees]]` | verified | 1 |
| 77 | conceptual_soundness | The value of `sign_check.utilisation.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:85badc3c:sign_check.utilisation.coef_sign]]` | verified | 1 |
| 78 | conceptual_soundness | The value of `sign_check.utilisation.univariate_direction` i… | 1 | ratio | sign_check |  | eq | `[[art:f0995196:sign_check.utilisation.univariate_direction]]` | verified | 1 |
| 79 | conceptual_soundness | The value of `threshold.E1.delta_auc` is 0.03 . | 0.03 | ratio | threshold |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 80 | data_integrity | The value of `csi.age` is 0.0009881 . | 0.0009881 | ratio | csi |  | eq | `[[art:76338ca5:csi.age]]` | verified | 0.0009881212408 |
| 81 | data_integrity | The value of `csi.bill_mean_6m` is 0.002641 . | 0.002641 | ratio | csi |  | eq | `[[art:9105b83f:csi.bill_mean_6m]]` | verified | 0.002640859388 |
| 82 | data_integrity | The value of `csi.bill_trend_6m` is 0.006491 . | 0.006491 | ratio | csi |  | eq | `[[art:85619225:csi.bill_trend_6m]]` | verified | 0.00649133631 |
| 83 | data_integrity | The value of `csi.delinq_count_6m` is 0.002326 . | 0.002326 | ratio | csi |  | eq | `[[art:77a551ed:csi.delinq_count_6m]]` | verified | 0.002326112961 |
| 84 | data_integrity | The value of `csi.delinq_last` is 0.02201 . | 0.02201 | ratio | csi |  | eq | `[[art:55177f94:csi.delinq_last]]` | verified | 0.02201119885 |
| 85 | data_integrity | The value of `csi.delinq_max_6m` is 0.0007952 . | 0.0007952 | ratio | csi |  | eq | `[[art:e6506c3b:csi.delinq_max_6m]]` | verified | 0.0007951651536 |
| 86 | data_integrity | The value of `csi.limit_bal` is 0.001136 . | 0.001136 | ratio | csi |  | eq | `[[art:f96c2df9:csi.limit_bal]]` | verified | 0.001135997167 |
| 87 | data_integrity | The value of `csi.max` is 0.02201 . | 0.02201 | ratio | csi |  | eq | `[[art:897f0064:csi.max]]` | verified | 0.02201119885 |
| 88 | data_integrity | The value of `csi.pay_ratio_last` is 0.002204 . | 0.002204 | ratio | csi |  | eq | `[[art:e23fdafd:csi.pay_ratio_last]]` | verified | 0.00220408217 |
| 89 | data_integrity | The value of `csi.pay_ratio_mean_6m` is 0.001619 . | 0.001619 | ratio | csi |  | eq | `[[art:ed28e38f:csi.pay_ratio_mean_6m]]` | verified | 0.00161884206 |
| 90 | data_integrity | The value of `csi.utilisation` is 0.004851 . | 0.004851 | ratio | csi |  | eq | `[[art:dfb8439b:csi.utilisation]]` | verified | 0.004851339646 |
| 91 | data_integrity | The value of `leakage.duplicates.train` is 0 . | 0 | ratio | leakage |  | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 92 | data_integrity | The value of `leakage.name_screen.n_matched` is 0 . | 0 | ratio | leakage |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 93 | data_integrity | The value of `leakage.overlap` is 0.03 . | 0.03 | ratio | leakage |  | eq | `[[art:a2cd9767:leakage.overlap]]` | verified | 0.03 |
| 94 | data_integrity | The value of `leakage.overlap.features` is 0.03 . | 0.03 | ratio | leakage |  | eq | `[[art:dc2d0a43:leakage.overlap.features]]` | verified | 0.03 |
| 95 | data_integrity | The value of `leakage.overlap.ids` is 0 . | 0 | ratio | leakage |  | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 96 | data_integrity | The value of `leakage.target_corr.max_single_feature_auc` is… | 0.6819 | ratio | leakage |  | eq | `[[art:7c15f992:leakage.target_corr.max_single_feature_auc]]` | verified | 0.6819042009 |
| 97 | data_integrity | The value of `leakage.timing.n_flagged` is 0 . | 0 | ratio | leakage |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 98 | data_integrity | The value of `profile.test.missing.max` is 0 . | 0 | ratio | profile |  | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 99 | data_integrity | The value of `profile.test.n` is 1500 . | 1500 | ratio | profile |  | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 100 | data_integrity | The value of `profile.train.missing.max` is 0 . | 0 | ratio | profile |  | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 101 | data_integrity | The value of `profile.train.n` is 3545 . | 3545 | ratio | profile |  | eq | `[[art:1ff4e472:profile.train.n]]` | verified | 3545 |
| 102 | data_integrity | The value of `psi.age` is 0.008244 . | 0.008244 | ratio | psi |  | eq | `[[art:54a6d5c8:psi.age]]` | verified | 0.008244342439 |
| 103 | data_integrity | The value of `psi.bill_mean_6m` is 0.007417 . | 0.007417 | ratio | psi |  | eq | `[[art:05ce5247:psi.bill_mean_6m]]` | verified | 0.007416663518 |
| 104 | data_integrity | The value of `psi.bill_trend_6m` is 0.009307 . | 0.009307 | ratio | psi |  | eq | `[[art:b8409498:psi.bill_trend_6m]]` | verified | 0.009307267944 |
| 105 | data_integrity | The value of `psi.delinq_count_6m` is 0.001826 . | 0.001826 | ratio | psi |  | eq | `[[art:95ad0bbe:psi.delinq_count_6m]]` | verified | 0.001825647083 |
| 106 | data_integrity | The value of `psi.delinq_last` is 0.002615 . | 0.002615 | ratio | psi |  | eq | `[[art:7298b08b:psi.delinq_last]]` | verified | 0.002615317622 |
| 107 | data_integrity | The value of `psi.delinq_max_6m` is 0.004879 . | 0.004879 | ratio | psi |  | eq | `[[art:548e3455:psi.delinq_max_6m]]` | verified | 0.0048789971 |
| 108 | data_integrity | The value of `psi.limit_bal` is 0.01082 . | 0.01082 | ratio | psi |  | eq | `[[art:5db122d3:psi.limit_bal]]` | verified | 0.01081685833 |
| 109 | data_integrity | The value of `psi.max` is 0.01082 . | 0.01082 | ratio | psi |  | eq | `[[art:9300bdd4:psi.max]]` | verified | 0.01081685833 |
| 110 | data_integrity | The value of `psi.pay_ratio_last` is 0.004465 . | 0.004465 | ratio | psi |  | eq | `[[art:ed34c7dc:psi.pay_ratio_last]]` | verified | 0.004465097584 |
| 111 | data_integrity | The value of `psi.pay_ratio_mean_6m` is 0.005142 . | 0.005142 | ratio | psi |  | eq | `[[art:bca4bf06:psi.pay_ratio_mean_6m]]` | verified | 0.00514221474 |
| 112 | data_integrity | The value of `psi.utilisation` is 0.004511 . | 0.004511 | ratio | psi |  | eq | `[[art:21c53bd0:psi.utilisation]]` | verified | 0.004510827349 |
| 113 | data_integrity | The value of `psi.y_score` is 0.004938 . | 0.004938 | ratio | psi |  | eq | `[[art:63344faa:psi.y_score]]` | verified | 0.004937814025 |
| 114 | data_integrity | The value of `threshold.D1.missing_gap` is 0.1 . | 0.1 | ratio | threshold |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 115 | data_integrity | The value of `threshold.L1.single_feature_auc` is 0.9 . | 0.9 | ratio | threshold |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 116 | data_integrity | The value of `threshold.L2.overlap` is 0.005 . | 0.005 | ratio | threshold |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 117 | data_integrity | The value of `threshold.L2.overlap.features_effective` is 0.… | 0.005 | ratio | threshold |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 118 | data_integrity | The value of `threshold.S1.psi` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 119 | data_integrity | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 120 | outcomes | The value of `calibration.mean_rel_gap.test` is 0.01499 . | 0.01499 | ratio | calibration |  | eq | `[[art:02e35a65:calibration.mean_rel_gap.test]]` | verified | 0.01498724157 |
| 121 | outcomes | The value of `calibration.mean_rel_gap.train` is 0.000327 . | 0.000327 | ratio | calibration |  | eq | `[[art:060d5049:calibration.mean_rel_gap.train]]` | verified | 0.0003270253632 |
| 122 | outcomes | The value of `calibration_intercept.test` is 0.02371 . | 0.02371 | ratio | calibration_intercept |  | eq | `[[art:ec6ca742:calibration_intercept.test]]` | verified | 0.02371386382 |
| 123 | outcomes | The value of `calibration_intercept.train` is 0.001736 . | 0.001736 | ratio | calibration_intercept |  | eq | `[[art:0b1e1ff9:calibration_intercept.train]]` | verified | 0.001736218384 |
| 124 | outcomes | The value of `calibration_slope.test` is 1.001 . | 1.001 | ratio | calibration_slope |  | eq | `[[art:95a66bf5:calibration_slope.test]]` | verified | 1.000821291 |
| 125 | outcomes | The value of `calibration_slope.train` is 1.002 . | 1.002 | ratio | calibration_slope |  | eq | `[[art:9f4641a6:calibration_slope.train]]` | verified | 1.001952049 |
| 126 | outcomes | The value of `deciles.test.top2_capture` is 0.4718 . | 0.4718 | ratio | deciles |  | eq | `[[art:d4a1cf7d:deciles.test.top2_capture]]` | verified | 0.471810089 |
| 127 | outcomes | The value of `deciles.train.top2_capture` is 0.4485 . | 0.4485 | ratio | deciles |  | eq | `[[art:15637767:deciles.train.top2_capture]]` | verified | 0.4484924623 |
| 128 | outcomes | The value of `metrics.test.auc` is 0.748 . | 0.748 | ratio | metrics |  | eq | `[[art:33170ddf:metrics.test.auc]]` | verified | 0.748047488 |
| 129 | outcomes | The value of `metrics.test.brier` is 0.149 . | 0.149 | ratio | metrics |  | eq | `[[art:3be8087d:metrics.test.brier]]` | verified | 0.1489501682 |
| 130 | outcomes | The value of `metrics.test.event_rate` is 0.2247 . | 0.2247 | ratio | metrics |  | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 131 | outcomes | The value of `metrics.test.gini` is 0.4961 . | 0.4961 | ratio | metrics |  | eq | `[[art:e7acec22:metrics.test.gini]]` | verified | 0.4960949759 |
| 132 | outcomes | The value of `metrics.test.ks` is 0.419 . | 0.419 | ratio | metrics |  | eq | `[[art:63623085:metrics.test.ks]]` | verified | 0.4189589494 |
| 133 | outcomes | The value of `metrics.test.logloss` is 0.4674 . | 0.4674 | ratio | metrics |  | eq | `[[art:33a9bfcd:metrics.test.logloss]]` | verified | 0.4673916168 |
| 134 | outcomes | The value of `metrics.test.mean_predicted` is 0.2213 . | 0.2213 | ratio | metrics |  | eq | `[[art:4920f430:metrics.test.mean_predicted]]` | verified | 0.2212995331 |
| 135 | outcomes | The value of `metrics.test.n` is 1500 . | 1500 | ratio | metrics |  | eq | `[[art:64fcf14d:metrics.test.n]]` | verified | 1500 |
| 136 | outcomes | The value of `metrics.train.auc` is 0.7589 . | 0.7589 | ratio | metrics |  | eq | `[[art:92ca327f:metrics.train.auc]]` | verified | 0.7588597772 |
| 137 | outcomes | The value of `metrics.train.brier` is 0.149 . | 0.149 | ratio | metrics |  | eq | `[[art:0215ac1d:metrics.train.brier]]` | verified | 0.1490409093 |
| 138 | outcomes | The value of `metrics.train.event_rate` is 0.2245 . | 0.2245 | ratio | metrics |  | eq | `[[art:cf2ea9d7:metrics.train.event_rate]]` | verified | 0.2245416079 |
| 139 | outcomes | The value of `metrics.train.gini` is 0.5177 . | 0.5177 | ratio | metrics |  | eq | `[[art:b7417c30:metrics.train.gini]]` | verified | 0.5177195545 |
| 140 | outcomes | The value of `metrics.train.ks` is 0.4447 . | 0.4447 | ratio | metrics |  | eq | `[[art:39f29309:metrics.train.ks]]` | verified | 0.4447131072 |
| 141 | outcomes | The value of `metrics.train.logloss` is 0.465 . | 0.465 | ratio | metrics |  | eq | `[[art:a9dde81e:metrics.train.logloss]]` | verified | 0.4650342534 |
| 142 | outcomes | The value of `metrics.train.mean_predicted` is 0.2246 . | 0.2246 | ratio | metrics |  | eq | `[[art:233a7dff:metrics.train.mean_predicted]]` | verified | 0.2246150387 |
| 143 | outcomes | The value of `metrics.train.n` is 3545 . | 3545 | ratio | metrics |  | eq | `[[art:343c4301:metrics.train.n]]` | verified | 3545 |
| 144 | outcomes | The value of `psi.age` is 0.008244 . | 0.008244 | ratio | psi |  | eq | `[[art:54a6d5c8:psi.age]]` | verified | 0.008244342439 |
| 145 | outcomes | The value of `psi.bill_mean_6m` is 0.007417 . | 0.007417 | ratio | psi |  | eq | `[[art:05ce5247:psi.bill_mean_6m]]` | verified | 0.007416663518 |
| 146 | outcomes | The value of `psi.bill_trend_6m` is 0.009307 . | 0.009307 | ratio | psi |  | eq | `[[art:b8409498:psi.bill_trend_6m]]` | verified | 0.009307267944 |
| 147 | outcomes | The value of `psi.delinq_count_6m` is 0.001826 . | 0.001826 | ratio | psi |  | eq | `[[art:95ad0bbe:psi.delinq_count_6m]]` | verified | 0.001825647083 |
| 148 | outcomes | The value of `psi.delinq_last` is 0.002615 . | 0.002615 | ratio | psi |  | eq | `[[art:7298b08b:psi.delinq_last]]` | verified | 0.002615317622 |
| 149 | outcomes | The value of `psi.delinq_max_6m` is 0.004879 . | 0.004879 | ratio | psi |  | eq | `[[art:548e3455:psi.delinq_max_6m]]` | verified | 0.0048789971 |
| 150 | outcomes | The value of `psi.limit_bal` is 0.01082 . | 0.01082 | ratio | psi |  | eq | `[[art:5db122d3:psi.limit_bal]]` | verified | 0.01081685833 |
| 151 | outcomes | The value of `psi.max` is 0.01082 . | 0.01082 | ratio | psi |  | eq | `[[art:9300bdd4:psi.max]]` | verified | 0.01081685833 |
| 152 | outcomes | The value of `psi.pay_ratio_last` is 0.004465 . | 0.004465 | ratio | psi |  | eq | `[[art:ed34c7dc:psi.pay_ratio_last]]` | verified | 0.004465097584 |
| 153 | outcomes | The value of `psi.pay_ratio_mean_6m` is 0.005142 . | 0.005142 | ratio | psi |  | eq | `[[art:bca4bf06:psi.pay_ratio_mean_6m]]` | verified | 0.00514221474 |
| 154 | outcomes | The value of `psi.utilisation` is 0.004511 . | 0.004511 | ratio | psi |  | eq | `[[art:21c53bd0:psi.utilisation]]` | verified | 0.004510827349 |
| 155 | outcomes | The value of `psi.y_score` is 0.004938 . | 0.004938 | ratio | psi |  | eq | `[[art:63344faa:psi.y_score]]` | verified | 0.004937814025 |
| 156 | outcomes | The value of `rule.calibration_first_event_rate` is 0.05 . | 0.05 | ratio | rule |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 157 | outcomes | The value of `threshold.C1.calibration_slope.max` is 1.2 . | 1.2 | ratio | threshold |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 158 | outcomes | The value of `threshold.C1.calibration_slope.min` is 0.8 . | 0.8 | ratio | threshold |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 159 | outcomes | The value of `threshold.C1.mean_ratio_rel` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 160 | outcomes | The value of `threshold.D1.missing_gap` is 0.1 . | 0.1 | ratio | threshold |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 161 | outcomes | The value of `threshold.E1.delta_auc` is 0.03 . | 0.03 | ratio | threshold |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 162 | outcomes | The value of `threshold.L1.single_feature_auc` is 0.9 . | 0.9 | ratio | threshold |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 163 | outcomes | The value of `threshold.L2.overlap` is 0.005 . | 0.005 | ratio | threshold |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 164 | outcomes | The value of `threshold.L2.overlap.features_effective` is 0.… | 0.005 | ratio | threshold |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 165 | outcomes | The value of `threshold.M1.condition_number` is 30 . | 30 | ratio | threshold |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 166 | outcomes | The value of `threshold.M1.vif` is 10 . | 10 | ratio | threshold |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 167 | outcomes | The value of `threshold.O1.auc_gap` is 0.08 . | 0.08 | ratio | threshold |  | eq | `[[art:630f28f4:threshold.O1.auc_gap]]` | verified | 0.08 |
| 168 | outcomes | The value of `threshold.S1.psi` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 169 | outcomes | The value of `threshold.package.auc.test.min` is 0.7 . | 0.7 | ratio | threshold |  | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 170 | outcomes | The value of `threshold.package.brier.test.max` is 0.2 . | 0.2 | ratio | threshold |  | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 171 | outcomes | The value of `threshold.package.calibration_slope.test.max`… | 1.2 | ratio | threshold |  | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 172 | outcomes | The value of `threshold.package.calibration_slope.test.min`… | 0.8 | ratio | threshold |  | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 173 | outcomes | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 174 | sensitivity | The value of `condition_number` is 5.557 . | 5.557 | ratio | condition_number |  | eq | `[[art:8029574b:condition_number]]` | verified | 5.556505365 |
| 175 | sensitivity | The value of `threshold.M1.condition_number` is 30 . | 30 | ratio | threshold |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 176 | sensitivity | The value of `threshold.M1.vif` is 10 . | 10 | ratio | threshold |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 177 | sensitivity | The value of `vif.age` is 1.002 . | 1.002 | ratio | vif |  | eq | `[[art:628d9c69:vif.age]]` | verified | 1.002128816 |
| 178 | sensitivity | The value of `vif.bill_mean_6m` is 7.31 . | 7.31 | ratio | vif |  | eq | `[[art:1915242e:vif.bill_mean_6m]]` | verified | 7.309956746 |
| 179 | sensitivity | The value of `vif.bill_trend_6m` is 1.201 . | 1.201 | ratio | vif |  | eq | `[[art:78a03a7b:vif.bill_trend_6m]]` | verified | 1.20121523 |
| 180 | sensitivity | The value of `vif.delinq_count_6m` is 2.567 . | 2.567 | ratio | vif |  | eq | `[[art:ca9bf9ad:vif.delinq_count_6m]]` | verified | 2.56680207 |
| 181 | sensitivity | The value of `vif.delinq_last` is 1.414 . | 1.414 | ratio | vif |  | eq | `[[art:a561c855:vif.delinq_last]]` | verified | 1.413950115 |
| 182 | sensitivity | The value of `vif.delinq_max_6m` is 2.403 . | 2.403 | ratio | vif |  | eq | `[[art:95ebdd8f:vif.delinq_max_6m]]` | verified | 2.403293321 |
| 183 | sensitivity | The value of `vif.limit_bal` is 4.82 . | 4.82 | ratio | vif |  | eq | `[[art:eeeb5c27:vif.limit_bal]]` | verified | 4.819728893 |
| 184 | sensitivity | The value of `vif.max` is 7.31 . | 7.31 | ratio | vif |  | eq | `[[art:d8e9619c:vif.max]]` | verified | 7.309956746 |
| 185 | sensitivity | The value of `vif.pay_ratio_last` is 7.286 . | 7.286 | ratio | vif |  | eq | `[[art:e30c6fbd:vif.pay_ratio_last]]` | verified | 7.285574881 |
| 186 | sensitivity | The value of `vif.pay_ratio_mean_6m` is 7.28 . | 7.28 | ratio | vif |  | eq | `[[art:4d1589cd:vif.pay_ratio_mean_6m]]` | verified | 7.279863906 |
| 187 | sensitivity | The value of `vif.utilisation` is 3.215 . | 3.215 | ratio | vif |  | eq | `[[art:7298e587:vif.utilisation]]` | verified | 3.214614007 |
| 188 | findings | The value of `challenger.auc` is 0.8346 . | 0.8346 | ratio | challenger |  | eq | `[[art:d1533f6e:challenger.auc]]` | verified | 0.8345601649 |
| 189 | findings | The value of `challenger.delta_auc` is 0.08651 . | 0.08651 | ratio | challenger |  | eq | `[[art:95cce9d6:challenger.delta_auc]]` | verified | 0.08651267698 |
| 190 | findings | The value of `leakage.duplicates.train` is 0 . | 0 | ratio | leakage |  | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 191 | findings | The value of `leakage.overlap.features` is 0.03 . | 0.03 | ratio | leakage |  | eq | `[[art:dc2d0a43:leakage.overlap.features]]` | verified | 0.03 |
| 192 | findings | The value of `metrics.test.auc` is 0.748 . | 0.748 | ratio | metrics |  | eq | `[[art:33170ddf:metrics.test.auc]]` | verified | 0.748047488 |
| 193 | findings | The value of `sign_check.delinq_max_6m.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:c946359c:sign_check.delinq_max_6m.agrees]]` | verified | 0 |
| 194 | findings | The value of `sign_check.delinq_max_6m.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]]` | verified | -1 |
| 195 | findings | The value of `sign_check.delinq_max_6m.univariate_direction`… | 1 | ratio | sign_check |  | eq | `[[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]]` | verified | 1 |
| 196 | findings | The value of `sign_check.limit_bal.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:0278aad1:sign_check.limit_bal.agrees]]` | verified | 0 |
| 197 | findings | The value of `sign_check.limit_bal.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:6af6aef2:sign_check.limit_bal.coef_sign]]` | verified | 1 |
| 198 | findings | The value of `sign_check.limit_bal.univariate_direction` is… | -1 | ratio | sign_check |  | eq | `[[art:56d284d6:sign_check.limit_bal.univariate_direction]]` | verified | -1 |
| 199 | findings | The value of `sign_check.pay_ratio_last.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:79abee77:sign_check.pay_ratio_last.agrees]]` | verified | 0 |
| 200 | findings | The value of `sign_check.pay_ratio_last.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:f018263e:sign_check.pay_ratio_last.coef_sign]]` | verified | 1 |
| 201 | findings | The value of `sign_check.pay_ratio_last.univariate_direction… | -1 | ratio | sign_check |  | eq | `[[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]]` | verified | -1 |
| 202 | findings | The value of `threshold.E1.delta_auc` is 0.03 . | 0.03 | ratio | threshold |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 203 | findings | The value of `threshold.L2.overlap` is 0.005 . | 0.005 | ratio | threshold |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 204 | findings | The value of `threshold.L2.overlap.features_effective` is 0.… | 0.005 | ratio | threshold |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 205 | monitoring | The value of `calibration_slope.test` is 1.001 . | 1.001 | ratio | calibration_slope |  | eq | `[[art:95a66bf5:calibration_slope.test]]` | verified | 1.000821291 |
| 206 | monitoring | The value of `metrics.test.auc` is 0.748 . | 0.748 | ratio | metrics |  | eq | `[[art:33170ddf:metrics.test.auc]]` | verified | 0.748047488 |
| 207 | monitoring | The value of `metrics.test.brier` is 0.149 . | 0.149 | ratio | metrics |  | eq | `[[art:3be8087d:metrics.test.brier]]` | verified | 0.1489501682 |
| 208 | monitoring | The value of `psi.max` is 0.01082 . | 0.01082 | ratio | psi |  | eq | `[[art:9300bdd4:psi.max]]` | verified | 0.01081685833 |
| 209 | monitoring | The value of `rule.calibration_first_event_rate` is 0.05 . | 0.05 | ratio | rule |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 210 | monitoring | The value of `threshold.package.auc.test.min` is 0.7 . | 0.7 | ratio | threshold |  | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 211 | monitoring | The value of `threshold.package.brier.test.max` is 0.2 . | 0.2 | ratio | threshold |  | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 212 | monitoring | The value of `threshold.package.calibration_slope.test.max`… | 1.2 | ratio | threshold |  | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 213 | monitoring | The value of `threshold.package.calibration_slope.test.min`… | 0.8 | ratio | threshold |  | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 214 | monitoring | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |

## Appendix B — Artifact index

The store holds 168 artifacts; the 137 this report cites or rests a finding on are indexed here.

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
| `metrics.train.auc` | `92ca327f` | scalar | 0.7588597772 | auc on train, recomputed by quaestor |
| `metrics.train.brier` | `0215ac1d` | scalar | 0.1490409093 | brier on train, recomputed by quaestor |
| `metrics.train.event_rate` | `cf2ea9d7` | scalar | 0.2245416079 | event_rate on train, recomputed by quaestor |
| `metrics.train.gini` | `b7417c30` | scalar | 0.5177195545 | gini on train, recomputed by quaestor |
| `metrics.train.ks` | `39f29309` | scalar | 0.4447131072 | ks on train, recomputed by quaestor |
| `metrics.train.logloss` | `a9dde81e` | scalar | 0.4650342534 | logloss on train, recomputed by quaestor |
| `metrics.train.mean_predicted` | `233a7dff` | scalar | 0.2246150387 | mean_predicted on train, recomputed by quaestor |
| `metrics.train.n` | `343c4301` | scalar | 3545 | n on train, recomputed by quaestor |
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
| tool calls | 13 (run_model 1, profile_data 1, compute_metrics 1, check_leakage 1, check_collinearity 1, challenger_compare 1, retrieve_guidance 7) |
| plan steps (bounded loop) | 0 |
| LLM calls | 0 () |
| re-asks | 0 |
| repair rounds | 0 |
| tokens in / out | 0 / 0 |
| notional cost (USD) | 0.0000 |
| wall-clock (s) | 1.06 |
| subject run (s) | 1.18 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | fake |
| model | none: no model answered |
| run id | credit_default-rules_only-20260918T065324Z-bd5861e9 |

## Appendix D — Not checked

| item | reason |
|---|---|
| `check_stability` (R1) | package declares no `regime.column` |
| `run_scenarios` (X1) | not applicable to `binary_classification` |
| out-of-time and vintage-holdout metrics (O1, second rule) | package declares neither split |
| developer claims (T1, claim channel) | The package declares 2 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
| drafted narrative and the repair loop | `rules_only` calls no model; the narrative is a template |
