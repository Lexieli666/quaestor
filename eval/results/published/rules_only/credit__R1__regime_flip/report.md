---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: rules_only
model: fake
run_id: credit_default-rules_only-20260918T065329Z-bd5861e9
data_mode: synthetic
synthetic_n: 5000
grounding_precision_pre: 1.0000
grounding_precision_post: 1.0000
n_claims: 229
n_findings_by_severity: {high: 0, medium: 1, low: 1, info: 0}
generated: "2026-09-18T06:53:29Z"
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
The value of `calibration_slope.test` is 0.8701 [[art:7002f467:calibration_slope.test]].
The value of `calibration_slope.train` is 1.002 [[art:7e7849d9:calibration_slope.train]].
The value of `challenger.delta_auc` is 0.05613 [[art:9cbcc544:challenger.delta_auc]].
The value of `condition_number` is 5.647 [[art:8dc0c2f1:condition_number]].
The value of `csi.max` is 0.01811 [[art:28c0a604:csi.max]].
The value of `metrics.test.auc` is 0.7337 [[art:3255122a:metrics.test.auc]].
The value of `metrics.test.brier` is 0.1536 [[art:3cd28a53:metrics.test.brier]].
The value of `metrics.test.event_rate` is 0.224 [[art:5f15df2a:metrics.test.event_rate]].
The value of `metrics.test.gini` is 0.4673 [[art:621c8cf3:metrics.test.gini]].
The value of `metrics.test.ks` is 0.4096 [[art:984fc4f0:metrics.test.ks]].
The value of `metrics.test.logloss` is 0.4788 [[art:1362ad67:metrics.test.logloss]].
The value of `metrics.test.mean_predicted` is 0.2292 [[art:f067e003:metrics.test.mean_predicted]].
The value of `metrics.test.n` is 1500 [[art:64fcf14d:metrics.test.n]].
The value of `metrics.train.auc` is 0.769 [[art:197f9521:metrics.train.auc]].
The value of `metrics.train.brier` is 0.1489 [[art:cf19f7b7:metrics.train.brier]].
The value of `metrics.train.event_rate` is 0.2243 [[art:8a78b455:metrics.train.event_rate]].
The value of `metrics.train.gini` is 0.5381 [[art:4208816b:metrics.train.gini]].
The value of `metrics.train.ks` is 0.4426 [[art:f1d489d8:metrics.train.ks]].
The value of `metrics.train.logloss` is 0.4632 [[art:a2852b4a:metrics.train.logloss]].
The value of `metrics.train.mean_predicted` is 0.2243 [[art:5ec77e91:metrics.train.mean_predicted]].
The value of `metrics.train.n` is 3500 [[art:564683ee:metrics.train.n]].
The value of `profile.test.n` is 1500 [[art:2193cf5f:profile.test.n]].
The value of `profile.train.n` is 3500 [[art:2510d49d:profile.train.n]].
The value of `psi.max` is 0.02385 [[art:4a5ae1a0:psi.max]].
The value of `runtime.max_seconds` is 300 [[art:2ad8d1a5:runtime.max_seconds]].
The value of `threshold.package.auc.test.min` is 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]].
The value of `threshold.package.brier.test.max` is 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]].
The value of `threshold.package.calibration_slope.test.max` is 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The value of `threshold.package.calibration_slope.test.min` is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
The value of `vif.max` is 7.512 [[art:2d17cd9e:vif.max]].

## 2. Conceptual soundness

This section follows the model risk management guidance at [[reg:SR26-2:V.1.a]].
The value of `ablation.age.delta_auc` is -0.0005472 [[art:03f2c15c:ablation.age.delta_auc]].
The value of `ablation.baseline_auc` is 0.7337 [[art:89f9f36a:ablation.baseline_auc]].
The value of `ablation.bill_mean_6m.delta_auc` is 0.005428 [[art:e4786496:ablation.bill_mean_6m.delta_auc]].
The value of `ablation.bill_trend_6m.delta_auc` is 0.002866 [[art:bb1f5508:ablation.bill_trend_6m.delta_auc]].
The value of `ablation.delinq_count_6m.delta_auc` is -0.0007824 [[art:5db921e5:ablation.delinq_count_6m.delta_auc]].
The value of `ablation.delinq_last.delta_auc` is -0.08354 [[art:e986cd7d:ablation.delinq_last.delta_auc]].
The value of `ablation.delinq_max_6m.delta_auc` is 0.0005906 [[art:76f922d7:ablation.delinq_max_6m.delta_auc]].
The value of `ablation.limit_bal.delta_auc` is 0.001337 [[art:5002902a:ablation.limit_bal.delta_auc]].
The value of `ablation.pay_ratio_last.delta_auc` is -0.0004117 [[art:04295c71:ablation.pay_ratio_last.delta_auc]].
The value of `ablation.pay_ratio_mean_6m.delta_auc` is 0.001726 [[art:5cb2a089:ablation.pay_ratio_mean_6m.delta_auc]].
The value of `ablation.utilisation.delta_auc` is -0.006451 [[art:8621db24:ablation.utilisation.delta_auc]].
The value of `challenger.auc` is 0.7898 [[art:2b3381be:challenger.auc]].
The value of `challenger.brier` is 0.1392 [[art:9599fce0:challenger.brier]].
The value of `challenger.delta_auc` is 0.05613 [[art:9cbcc544:challenger.delta_auc]].
The value of `metrics.test.auc` is 0.7337 [[art:3255122a:metrics.test.auc]].
The value of `metrics.test.brier` is 0.1536 [[art:3cd28a53:metrics.test.brier]].
The value of `sign_check.age.agrees` is 0 [[art:5c2c50b8:sign_check.age.agrees]].
The value of `sign_check.age.coef_sign` is -1 [[art:6172eb93:sign_check.age.coef_sign]].
The value of `sign_check.age.univariate_direction` is 1 [[art:cac34cd5:sign_check.age.univariate_direction]].
The value of `sign_check.bill_mean_6m.agrees` is 0 [[art:4df8b747:sign_check.bill_mean_6m.agrees]].
The value of `sign_check.bill_mean_6m.coef_sign` is -1 [[art:cee1a18f:sign_check.bill_mean_6m.coef_sign]].
The value of `sign_check.bill_mean_6m.univariate_direction` is 1 [[art:82ba9862:sign_check.bill_mean_6m.univariate_direction]].
The value of `sign_check.bill_trend_6m.agrees` is 1 [[art:ff3cb24a:sign_check.bill_trend_6m.agrees]].
The value of `sign_check.bill_trend_6m.coef_sign` is -1 [[art:7fd8474e:sign_check.bill_trend_6m.coef_sign]].
The value of `sign_check.bill_trend_6m.univariate_direction` is -1 [[art:a9bff389:sign_check.bill_trend_6m.univariate_direction]].
The value of `sign_check.delinq_count_6m.agrees` is 1 [[art:a337d16b:sign_check.delinq_count_6m.agrees]].
The value of `sign_check.delinq_count_6m.coef_sign` is 1 [[art:17afb6f9:sign_check.delinq_count_6m.coef_sign]].
The value of `sign_check.delinq_count_6m.univariate_direction` is 1 [[art:549e904e:sign_check.delinq_count_6m.univariate_direction]].
The value of `sign_check.delinq_last.agrees` is 1 [[art:a8ba9372:sign_check.delinq_last.agrees]].
The value of `sign_check.delinq_last.coef_sign` is 1 [[art:50d352f8:sign_check.delinq_last.coef_sign]].
The value of `sign_check.delinq_last.univariate_direction` is 1 [[art:a78648ba:sign_check.delinq_last.univariate_direction]].
The value of `sign_check.delinq_max_6m.agrees` is 1 [[art:da92a015:sign_check.delinq_max_6m.agrees]].
The value of `sign_check.delinq_max_6m.coef_sign` is 1 [[art:53560657:sign_check.delinq_max_6m.coef_sign]].
The value of `sign_check.delinq_max_6m.univariate_direction` is 1 [[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]].
The value of `sign_check.limit_bal.agrees` is 0 [[art:0278aad1:sign_check.limit_bal.agrees]].
The value of `sign_check.limit_bal.coef_sign` is 1 [[art:6af6aef2:sign_check.limit_bal.coef_sign]].
The value of `sign_check.limit_bal.univariate_direction` is -1 [[art:56d284d6:sign_check.limit_bal.univariate_direction]].
The value of `sign_check.n_disagreements` is 3 [[art:e223cd4a:sign_check.n_disagreements]].
The value of `sign_check.pay_ratio_last.agrees` is 1 [[art:7837941a:sign_check.pay_ratio_last.agrees]].
The value of `sign_check.pay_ratio_last.coef_sign` is -1 [[art:489c3e67:sign_check.pay_ratio_last.coef_sign]].
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
The value of `csi.age` is 0.0002175 [[art:0aad0eb8:csi.age]].
The value of `csi.bill_mean_6m` is 0.005952 [[art:4ceb65ea:csi.bill_mean_6m]].
The value of `csi.bill_trend_6m` is 0.0004864 [[art:93317930:csi.bill_trend_6m]].
The value of `csi.delinq_count_6m` is 0.0001786 [[art:8359c176:csi.delinq_count_6m]].
The value of `csi.delinq_last` is 0.01811 [[art:c0b3fffe:csi.delinq_last]].
The value of `csi.delinq_max_6m` is 0.0002075 [[art:0bc44634:csi.delinq_max_6m]].
The value of `csi.limit_bal` is 0.0002442 [[art:443540b2:csi.limit_bal]].
The value of `csi.max` is 0.01811 [[art:28c0a604:csi.max]].
The value of `csi.pay_ratio_last` is 0.0000146 [[art:e06dbc50:csi.pay_ratio_last]].
The value of `csi.pay_ratio_mean_6m` is 0.0045 [[art:adf83ef4:csi.pay_ratio_mean_6m]].
The value of `csi.utilisation` is 0.01788 [[art:54e8c0d5:csi.utilisation]].
The value of `leakage.duplicates.train` is 0 [[art:4474c227:leakage.duplicates.train]].
The value of `leakage.name_screen.n_matched` is 0 [[art:407e62be:leakage.name_screen.n_matched]].
The value of `leakage.overlap` is 0 [[art:4c9fcd09:leakage.overlap]].
The value of `leakage.overlap.features` is 0 [[art:0fec8048:leakage.overlap.features]].
The value of `leakage.overlap.ids` is 0 [[art:63d37fc5:leakage.overlap.ids]].
The value of `leakage.target_corr.max_single_feature_auc` is 0.6841 [[art:f39d22de:leakage.target_corr.max_single_feature_auc]].
The value of `leakage.timing.n_flagged` is 0 [[art:742bcd24:leakage.timing.n_flagged]].
The value of `profile.test.missing.max` is 0 [[art:f813848d:profile.test.missing.max]].
The value of `profile.test.n` is 1500 [[art:2193cf5f:profile.test.n]].
The value of `profile.train.missing.max` is 0 [[art:050a3099:profile.train.missing.max]].
The value of `profile.train.n` is 3500 [[art:2510d49d:profile.train.n]].
The value of `psi.age` is 0.01198 [[art:2e7b9ead:psi.age]].
The value of `psi.bill_mean_6m` is 0.008018 [[art:a0afce85:psi.bill_mean_6m]].
The value of `psi.bill_trend_6m` is 0.008579 [[art:b80e3091:psi.bill_trend_6m]].
The value of `psi.delinq_count_6m` is 0.001414 [[art:4b7439f2:psi.delinq_count_6m]].
The value of `psi.delinq_last` is 0.003062 [[art:7662ef2e:psi.delinq_last]].
The value of `psi.delinq_max_6m` is 0.003729 [[art:b6668567:psi.delinq_max_6m]].
The value of `psi.limit_bal` is 0.004676 [[art:09a00724:psi.limit_bal]].
The value of `psi.max` is 0.02385 [[art:4a5ae1a0:psi.max]].
The value of `psi.pay_ratio_last` is 0.006835 [[art:96c52004:psi.pay_ratio_last]].
The value of `psi.pay_ratio_mean_6m` is 0.02385 [[art:e3761732:psi.pay_ratio_mean_6m]].
The value of `psi.utilisation` is 0.01248 [[art:3c68d5ee:psi.utilisation]].
The value of `psi.y_score` is 0.006306 [[art:4a23b13e:psi.y_score]].
The value of `threshold.D1.missing_gap` is 0.1 [[art:9cce25ea:threshold.D1.missing_gap]].
The value of `threshold.L1.single_feature_auc` is 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]].
The value of `threshold.L2.overlap` is 0.005 [[art:9f336eaf:threshold.L2.overlap]].
The value of `threshold.L2.overlap.features_effective` is 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].
The value of `threshold.S1.psi` is 0.25 [[art:278b9016:threshold.S1.psi]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].

## 4. Outcomes analysis

This section follows the model risk management guidance at [[reg:SR26-2:V.1.b]].
The value of `calibration.mean_rel_gap.test` is 0.02344 [[art:fd64775d:calibration.mean_rel_gap.test]].
The value of `calibration.mean_rel_gap.train` is 0.00003599 [[art:ac0572fe:calibration.mean_rel_gap.train]].
The value of `calibration_intercept.test` is -0.1809 [[art:386a6083:calibration_intercept.test]].
The value of `calibration_intercept.train` is 0.002422 [[art:e1230838:calibration_intercept.train]].
The value of `calibration_slope.test` is 0.8701 [[art:7002f467:calibration_slope.test]].
The value of `calibration_slope.train` is 1.002 [[art:7e7849d9:calibration_slope.train]].
The value of `deciles.test.top2_capture` is 0.4345 [[art:c7670b9d:deciles.test.top2_capture]].
The value of `deciles.train.top2_capture` is 0.4459 [[art:0511095f:deciles.train.top2_capture]].
The value of `metrics.test.auc` is 0.7337 [[art:3255122a:metrics.test.auc]].
The value of `metrics.test.brier` is 0.1536 [[art:3cd28a53:metrics.test.brier]].
The value of `metrics.test.event_rate` is 0.224 [[art:5f15df2a:metrics.test.event_rate]].
The value of `metrics.test.gini` is 0.4673 [[art:621c8cf3:metrics.test.gini]].
The value of `metrics.test.ks` is 0.4096 [[art:984fc4f0:metrics.test.ks]].
The value of `metrics.test.logloss` is 0.4788 [[art:1362ad67:metrics.test.logloss]].
The value of `metrics.test.mean_predicted` is 0.2292 [[art:f067e003:metrics.test.mean_predicted]].
The value of `metrics.test.n` is 1500 [[art:64fcf14d:metrics.test.n]].
The value of `metrics.train.auc` is 0.769 [[art:197f9521:metrics.train.auc]].
The value of `metrics.train.brier` is 0.1489 [[art:cf19f7b7:metrics.train.brier]].
The value of `metrics.train.event_rate` is 0.2243 [[art:8a78b455:metrics.train.event_rate]].
The value of `metrics.train.gini` is 0.5381 [[art:4208816b:metrics.train.gini]].
The value of `metrics.train.ks` is 0.4426 [[art:f1d489d8:metrics.train.ks]].
The value of `metrics.train.logloss` is 0.4632 [[art:a2852b4a:metrics.train.logloss]].
The value of `metrics.train.mean_predicted` is 0.2243 [[art:5ec77e91:metrics.train.mean_predicted]].
The value of `metrics.train.n` is 3500 [[art:564683ee:metrics.train.n]].
The value of `psi.age` is 0.01198 [[art:2e7b9ead:psi.age]].
The value of `psi.bill_mean_6m` is 0.008018 [[art:a0afce85:psi.bill_mean_6m]].
The value of `psi.bill_trend_6m` is 0.008579 [[art:b80e3091:psi.bill_trend_6m]].
The value of `psi.delinq_count_6m` is 0.001414 [[art:4b7439f2:psi.delinq_count_6m]].
The value of `psi.delinq_last` is 0.003062 [[art:7662ef2e:psi.delinq_last]].
The value of `psi.delinq_max_6m` is 0.003729 [[art:b6668567:psi.delinq_max_6m]].
The value of `psi.limit_bal` is 0.004676 [[art:09a00724:psi.limit_bal]].
The value of `psi.max` is 0.02385 [[art:4a5ae1a0:psi.max]].
The value of `psi.pay_ratio_last` is 0.006835 [[art:96c52004:psi.pay_ratio_last]].
The value of `psi.pay_ratio_mean_6m` is 0.02385 [[art:e3761732:psi.pay_ratio_mean_6m]].
The value of `psi.utilisation` is 0.01248 [[art:3c68d5ee:psi.utilisation]].
The value of `psi.y_score` is 0.006306 [[art:4a23b13e:psi.y_score]].
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
The value of `threshold.R1.auc_gap` is 0.1 [[art:b64213d7:threshold.R1.auc_gap]].
The value of `threshold.R1.sign_flip_coef` is 0.05 [[art:aca84377:threshold.R1.sign_flip_coef]].
The value of `threshold.R1.sign_flip_z` is 2 [[art:2e4428c7:threshold.R1.sign_flip_z]].
The value of `threshold.S1.psi` is 0.25 [[art:278b9016:threshold.S1.psi]].
The value of `threshold.package.auc.test.min` is 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]].
The value of `threshold.package.brier.test.max` is 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]].
The value of `threshold.package.calibration_slope.test.max` is 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The value of `threshold.package.calibration_slope.test.min` is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
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

## 5. Sensitivity and scenario analysis

This section follows the model risk management guidance at [[reg:SR26-2:V.1.a]].
The value of `condition_number` is 5.647 [[art:8dc0c2f1:condition_number]].
The value of `stability.age.sign_flip` is 0 [[art:af9b1d06:stability.age.sign_flip]].
The value of `stability.bill_mean_6m.sign_flip` is 0 [[art:df546086:stability.bill_mean_6m.sign_flip]].
The value of `stability.bill_trend_6m.sign_flip` is 1 [[art:4dc17324:stability.bill_trend_6m.sign_flip]].
The value of `stability.delinq_count_6m.sign_flip` is 0 [[art:40d78102:stability.delinq_count_6m.sign_flip]].
The value of `stability.delinq_last.sign_flip` is 0 [[art:a7adedc7:stability.delinq_last.sign_flip]].
The value of `stability.delinq_max_6m.sign_flip` is 0 [[art:908eec36:stability.delinq_max_6m.sign_flip]].
The value of `stability.limit_bal.sign_flip` is 0 [[art:3a0e7e0d:stability.limit_bal.sign_flip]].
The value of `stability.pay_ratio_last.sign_flip` is 0 [[art:77aa667a:stability.pay_ratio_last.sign_flip]].
The value of `stability.pay_ratio_mean_6m.sign_flip` is 0 [[art:f8da40ca:stability.pay_ratio_mean_6m.sign_flip]].
The value of `stability.utilisation.sign_flip` is 0 [[art:5b813a1b:stability.utilisation.sign_flip]].
The value of `threshold.M1.condition_number` is 30 [[art:7e52fd7a:threshold.M1.condition_number]].
The value of `threshold.M1.vif` is 10 [[art:aeb4f33c:threshold.M1.vif]].
The value of `threshold.R1.auc_gap` is 0.1 [[art:b64213d7:threshold.R1.auc_gap]].
The value of `threshold.R1.sign_flip_coef` is 0.05 [[art:aca84377:threshold.R1.sign_flip_coef]].
The value of `threshold.R1.sign_flip_z` is 2 [[art:2e4428c7:threshold.R1.sign_flip_z]].
The value of `vif.age` is 1.003 [[art:193052e1:vif.age]].
The value of `vif.bill_mean_6m` is 7.512 [[art:19127172:vif.bill_mean_6m]].
The value of `vif.bill_trend_6m` is 1.217 [[art:36ec368c:vif.bill_trend_6m]].
The value of `vif.delinq_count_6m` is 2.527 [[art:063976d6:vif.delinq_count_6m]].
The value of `vif.delinq_last` is 1.433 [[art:1d3a39df:vif.delinq_last]].
The value of `vif.delinq_max_6m` is 2.375 [[art:fa4a6cf4:vif.delinq_max_6m]].
The value of `vif.limit_bal` is 4.832 [[art:f19a1ae6:vif.limit_bal]].
The value of `vif.max` is 7.512 [[art:2d17cd9e:vif.max]].
The value of `vif.pay_ratio_last` is 7.213 [[art:a9b805e2:vif.pay_ratio_last]].
The value of `vif.pay_ratio_mean_6m` is 7.206 [[art:76a555ef:vif.pay_ratio_mean_6m]].
The value of `vif.utilisation` is 3.408 [[art:87292dc8:vif.utilisation]].
<!-- quaestor:renderer:begin table stability.auc_by_regime -->
The champion's AUC within each application_cohort on train [[art:395a801f:stability.auc_by_regime]]:

| regime | n | event_rate | auc |
|---|---|---|---|
| 2013 | 1734 | 0.2065 | 0.7382 |
| 2016 | 1766 | 0.2418 | 0.7963 |
<!-- quaestor:renderer:end -->
Candidates raised on this section's material: R1 (see the findings section).

## 6. Findings and recommendations

This section follows the model risk management guidance at [[reg:SR26-2:VI.3]].

### F-001 · R1 regime stability · severity **medium**

**A `R1` finding, raised by `check_stability` at severity `medium`.**
Its evidence is the artifacts cited in this section; the check's own account of it is recorded in `findings.json`.

### F-002 · E1 effective challenge · severity **low**

**A `E1` finding, raised by `challenger_compare` at severity `low`.**
Its evidence is the artifacts cited in this section; the check's own account of it is recorded in `findings.json`.
The value of `challenger.auc` is 0.7898 [[art:2b3381be:challenger.auc]].
The value of `challenger.delta_auc` is 0.05613 [[art:9cbcc544:challenger.delta_auc]].
The value of `metrics.test.auc` is 0.7337 [[art:3255122a:metrics.test.auc]].
The value of `sign_check.age.agrees` is 0 [[art:5c2c50b8:sign_check.age.agrees]].
The value of `sign_check.age.coef_sign` is -1 [[art:6172eb93:sign_check.age.coef_sign]].
The value of `sign_check.age.univariate_direction` is 1 [[art:cac34cd5:sign_check.age.univariate_direction]].
The value of `sign_check.bill_mean_6m.agrees` is 0 [[art:4df8b747:sign_check.bill_mean_6m.agrees]].
The value of `sign_check.bill_mean_6m.coef_sign` is -1 [[art:cee1a18f:sign_check.bill_mean_6m.coef_sign]].
The value of `sign_check.bill_mean_6m.univariate_direction` is 1 [[art:82ba9862:sign_check.bill_mean_6m.univariate_direction]].
The value of `sign_check.limit_bal.agrees` is 0 [[art:0278aad1:sign_check.limit_bal.agrees]].
The value of `sign_check.limit_bal.coef_sign` is 1 [[art:6af6aef2:sign_check.limit_bal.coef_sign]].
The value of `sign_check.limit_bal.univariate_direction` is -1 [[art:56d284d6:sign_check.limit_bal.univariate_direction]].
The value of `stability.bill_trend_6m.sign_flip` is 1 [[art:4dc17324:stability.bill_trend_6m.sign_flip]].
The value of `threshold.E1.delta_auc` is 0.03 [[art:e042774c:threshold.E1.delta_auc]].
The value of `threshold.R1.sign_flip_coef` is 0.05 [[art:aca84377:threshold.R1.sign_flip_coef]].
The value of `threshold.R1.sign_flip_z` is 2 [[art:2e4428c7:threshold.R1.sign_flip_z]].
<!-- quaestor:renderer:begin table stability.bill_trend_6m.coef_or_importance_by_regime -->
Bill_trend_6m's coefficient in a per-regime refit, standardised, with the standard error and z of each [[art:4114d577:stability.bill_trend_6m.coef_or_importance_by_regime]]:

| regime | coefficient | se | z |
|---|---|---|---|
| 2013 | 0.9089 | 0.117 | 7.766 |
| 2016 | -1.171 | 0.1052 | -11.13 |
<!-- quaestor:renderer:end -->

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1, S1), `compute_metrics` (T1, C1, O1), `check_leakage` (L1, L2), `check_collinearity` (M1).

### Open items

No open item was recorded for this validation.

## 7. Ongoing monitoring recommendations

This section follows the model risk management guidance at [[reg:SR26-2:V.2]].
The value of `calibration_slope.test` is 0.8701 [[art:7002f467:calibration_slope.test]].
The value of `metrics.test.auc` is 0.7337 [[art:3255122a:metrics.test.auc]].
The value of `metrics.test.brier` is 0.1536 [[art:3cd28a53:metrics.test.brier]].
The value of `psi.max` is 0.02385 [[art:4a5ae1a0:psi.max]].
The value of `rule.calibration_first_event_rate` is 0.05 [[art:42f1351e:rule.calibration_first_event_rate]].
The value of `threshold.package.auc.test.min` is 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]].
The value of `threshold.package.brier.test.max` is 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]].
The value of `threshold.package.calibration_slope.test.max` is 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The value of `threshold.package.calibration_slope.test.min` is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].

## Appendix A — Claims

Grounding precision 1.0000 before repair (229 of 229 claims verified) and 1.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 31/31; conceptual_soundness 48/48; data_integrity 40/40; outcomes 57/57; sensitivity 27/27; findings 16/16; monitoring 10/10.

Developer claims: The package declares 2 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). See Appendix D.

Excluded numeric tokens (not claims): citation_hash (7002f467, 7e7849d9, 9cbcc544, 8dc0c2f1); regulatory_section_id (SR26-2:V.1.b, SR26-2:V.1.a, SR26-2:VI.3, SR26-2:V.2); finding_id (F-001, F-002).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The value of `calibration_slope.test` is 0.8701 . | 0.8701 | ratio | calibration_slope |  | eq | `[[art:7002f467:calibration_slope.test]]` | verified | 0.8701260273 |
| 2 | summary | The value of `calibration_slope.train` is 1.002 . | 1.002 | ratio | calibration_slope |  | eq | `[[art:7e7849d9:calibration_slope.train]]` | verified | 1.002056925 |
| 3 | summary | The value of `challenger.delta_auc` is 0.05613 . | 0.05613 | ratio | challenger |  | eq | `[[art:9cbcc544:challenger.delta_auc]]` | verified | 0.05613085011 |
| 4 | summary | The value of `condition_number` is 5.647 . | 5.647 | ratio | condition_number |  | eq | `[[art:8dc0c2f1:condition_number]]` | verified | 5.646537667 |
| 5 | summary | The value of `csi.max` is 0.01811 . | 0.01811 | ratio | csi |  | eq | `[[art:28c0a604:csi.max]]` | verified | 0.01811466703 |
| 6 | summary | The value of `metrics.test.auc` is 0.7337 . | 0.7337 | ratio | metrics |  | eq | `[[art:3255122a:metrics.test.auc]]` | verified | 0.7336641916 |
| 7 | summary | The value of `metrics.test.brier` is 0.1536 . | 0.1536 | ratio | metrics |  | eq | `[[art:3cd28a53:metrics.test.brier]]` | verified | 0.1535518185 |
| 8 | summary | The value of `metrics.test.event_rate` is 0.224 . | 0.224 | ratio | metrics |  | eq | `[[art:5f15df2a:metrics.test.event_rate]]` | verified | 0.224 |
| 9 | summary | The value of `metrics.test.gini` is 0.4673 . | 0.4673 | ratio | metrics |  | eq | `[[art:621c8cf3:metrics.test.gini]]` | verified | 0.4673283832 |
| 10 | summary | The value of `metrics.test.ks` is 0.4096 . | 0.4096 | ratio | metrics |  | eq | `[[art:984fc4f0:metrics.test.ks]]` | verified | 0.4095790378 |
| 11 | summary | The value of `metrics.test.logloss` is 0.4788 . | 0.4788 | ratio | metrics |  | eq | `[[art:1362ad67:metrics.test.logloss]]` | verified | 0.4787760084 |
| 12 | summary | The value of `metrics.test.mean_predicted` is 0.2292 . | 0.2292 | ratio | metrics |  | eq | `[[art:f067e003:metrics.test.mean_predicted]]` | verified | 0.2292494944 |
| 13 | summary | The value of `metrics.test.n` is 1500 . | 1500 | ratio | metrics |  | eq | `[[art:64fcf14d:metrics.test.n]]` | verified | 1500 |
| 14 | summary | The value of `metrics.train.auc` is 0.769 . | 0.769 | ratio | metrics |  | eq | `[[art:197f9521:metrics.train.auc]]` | verified | 0.7690391902 |
| 15 | summary | The value of `metrics.train.brier` is 0.1489 . | 0.1489 | ratio | metrics |  | eq | `[[art:cf19f7b7:metrics.train.brier]]` | verified | 0.1488512538 |
| 16 | summary | The value of `metrics.train.event_rate` is 0.2243 . | 0.2243 | ratio | metrics |  | eq | `[[art:8a78b455:metrics.train.event_rate]]` | verified | 0.2242857143 |
| 17 | summary | The value of `metrics.train.gini` is 0.5381 . | 0.5381 | ratio | metrics |  | eq | `[[art:4208816b:metrics.train.gini]]` | verified | 0.5380783803 |
| 18 | summary | The value of `metrics.train.ks` is 0.4426 . | 0.4426 | ratio | metrics |  | eq | `[[art:f1d489d8:metrics.train.ks]]` | verified | 0.4425801457 |
| 19 | summary | The value of `metrics.train.logloss` is 0.4632 . | 0.4632 | ratio | metrics |  | eq | `[[art:a2852b4a:metrics.train.logloss]]` | verified | 0.4632349902 |
| 20 | summary | The value of `metrics.train.mean_predicted` is 0.2243 . | 0.2243 | ratio | metrics |  | eq | `[[art:5ec77e91:metrics.train.mean_predicted]]` | verified | 0.2242776431 |
| 21 | summary | The value of `metrics.train.n` is 3500 . | 3500 | ratio | metrics |  | eq | `[[art:564683ee:metrics.train.n]]` | verified | 3500 |
| 22 | summary | The value of `profile.test.n` is 1500 . | 1500 | ratio | profile |  | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 23 | summary | The value of `profile.train.n` is 3500 . | 3500 | ratio | profile |  | eq | `[[art:2510d49d:profile.train.n]]` | verified | 3500 |
| 24 | summary | The value of `psi.max` is 0.02385 . | 0.02385 | ratio | psi |  | eq | `[[art:4a5ae1a0:psi.max]]` | verified | 0.02385256621 |
| 25 | summary | The value of `runtime.max_seconds` is 300 . | 300 | ratio | runtime |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 26 | summary | The value of `threshold.package.auc.test.min` is 0.7 . | 0.7 | ratio | threshold |  | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 27 | summary | The value of `threshold.package.brier.test.max` is 0.2 . | 0.2 | ratio | threshold |  | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 28 | summary | The value of `threshold.package.calibration_slope.test.max`… | 1.2 | ratio | threshold |  | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 29 | summary | The value of `threshold.package.calibration_slope.test.min`… | 0.8 | ratio | threshold |  | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 30 | summary | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 31 | summary | The value of `vif.max` is 7.512 . | 7.512 | ratio | vif |  | eq | `[[art:2d17cd9e:vif.max]]` | verified | 7.511880286 |
| 32 | conceptual_soundness | The value of `ablation.age.delta_auc` is -0.0005472 . | -0.0005472 | ratio | ablation |  | eq | `[[art:03f2c15c:ablation.age.delta_auc]]` | verified | -0.0005471690394 |
| 33 | conceptual_soundness | The value of `ablation.baseline_auc` is 0.7337 . | 0.7337 | ratio | ablation |  | eq | `[[art:89f9f36a:ablation.baseline_auc]]` | verified | 0.7336641916 |
| 34 | conceptual_soundness | The value of `ablation.bill_mean_6m.delta_auc` is 0.005428 . | 0.005428 | ratio | ablation |  | eq | `[[art:e4786496:ablation.bill_mean_6m.delta_auc]]` | verified | 0.005428223695 |
| 35 | conceptual_soundness | The value of `ablation.bill_trend_6m.delta_auc` is 0.002866… | 0.002866 | ratio | ablation |  | eq | `[[art:bb1f5508:ablation.bill_trend_6m.delta_auc]]` | verified | 0.002866245295 |
| 36 | conceptual_soundness | The value of `ablation.delinq_count_6m.delta_auc` is -0.0007… | -0.0007824 | ratio | ablation |  | eq | `[[art:5db921e5:ablation.delinq_count_6m.delta_auc]]` | verified | -0.0007824005891 |
| 37 | conceptual_soundness | The value of `ablation.delinq_last.delta_auc` is -0.08354 . | -0.08354 | ratio | ablation |  | eq | `[[art:e986cd7d:ablation.delinq_last.delta_auc]]` | verified | -0.08354299624 |
| 38 | conceptual_soundness | The value of `ablation.delinq_max_6m.delta_auc` is 0.0005906… | 0.0005906 | ratio | ablation |  | eq | `[[art:76f922d7:ablation.delinq_max_6m.delta_auc]]` | verified | 0.0005906357388 |
| 39 | conceptual_soundness | The value of `ablation.limit_bal.delta_auc` is 0.001337 . | 0.001337 | ratio | ablation |  | eq | `[[art:5002902a:ablation.limit_bal.delta_auc]]` | verified | 0.001337240223 |
| 40 | conceptual_soundness | The value of `ablation.pay_ratio_last.delta_auc` is -0.00041… | -0.0004117 | ratio | ablation |  | eq | `[[art:04295c71:ablation.pay_ratio_last.delta_auc]]` | verified | -0.0004116552119 |
| 41 | conceptual_soundness | The value of `ablation.pay_ratio_mean_6m.delta_auc` is 0.001… | 0.001726 | ratio | ablation |  | eq | `[[art:5cb2a089:ablation.pay_ratio_mean_6m.delta_auc]]` | verified | 0.001725883652 |
| 42 | conceptual_soundness | The value of `ablation.utilisation.delta_auc` is -0.006451 . | -0.006451 | ratio | ablation |  | eq | `[[art:8621db24:ablation.utilisation.delta_auc]]` | verified | -0.006450969563 |
| 43 | conceptual_soundness | The value of `challenger.auc` is 0.7898 . | 0.7898 | ratio | challenger |  | eq | `[[art:2b3381be:challenger.auc]]` | verified | 0.7897950417 |
| 44 | conceptual_soundness | The value of `challenger.brier` is 0.1392 . | 0.1392 | ratio | challenger |  | eq | `[[art:9599fce0:challenger.brier]]` | verified | 0.1391775952 |
| 45 | conceptual_soundness | The value of `challenger.delta_auc` is 0.05613 . | 0.05613 | ratio | challenger |  | eq | `[[art:9cbcc544:challenger.delta_auc]]` | verified | 0.05613085011 |
| 46 | conceptual_soundness | The value of `metrics.test.auc` is 0.7337 . | 0.7337 | ratio | metrics |  | eq | `[[art:3255122a:metrics.test.auc]]` | verified | 0.7336641916 |
| 47 | conceptual_soundness | The value of `metrics.test.brier` is 0.1536 . | 0.1536 | ratio | metrics |  | eq | `[[art:3cd28a53:metrics.test.brier]]` | verified | 0.1535518185 |
| 48 | conceptual_soundness | The value of `sign_check.age.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:5c2c50b8:sign_check.age.agrees]]` | verified | 0 |
| 49 | conceptual_soundness | The value of `sign_check.age.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:6172eb93:sign_check.age.coef_sign]]` | verified | -1 |
| 50 | conceptual_soundness | The value of `sign_check.age.univariate_direction` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:cac34cd5:sign_check.age.univariate_direction]]` | verified | 1 |
| 51 | conceptual_soundness | The value of `sign_check.bill_mean_6m.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:4df8b747:sign_check.bill_mean_6m.agrees]]` | verified | 0 |
| 52 | conceptual_soundness | The value of `sign_check.bill_mean_6m.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:cee1a18f:sign_check.bill_mean_6m.coef_sign]]` | verified | -1 |
| 53 | conceptual_soundness | The value of `sign_check.bill_mean_6m.univariate_direction`… | 1 | ratio | sign_check |  | eq | `[[art:82ba9862:sign_check.bill_mean_6m.univariate_direction]]` | verified | 1 |
| 54 | conceptual_soundness | The value of `sign_check.bill_trend_6m.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:ff3cb24a:sign_check.bill_trend_6m.agrees]]` | verified | 1 |
| 55 | conceptual_soundness | The value of `sign_check.bill_trend_6m.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:7fd8474e:sign_check.bill_trend_6m.coef_sign]]` | verified | -1 |
| 56 | conceptual_soundness | The value of `sign_check.bill_trend_6m.univariate_direction`… | -1 | ratio | sign_check |  | eq | `[[art:a9bff389:sign_check.bill_trend_6m.univariate_direction]]` | verified | -1 |
| 57 | conceptual_soundness | The value of `sign_check.delinq_count_6m.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:a337d16b:sign_check.delinq_count_6m.agrees]]` | verified | 1 |
| 58 | conceptual_soundness | The value of `sign_check.delinq_count_6m.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:17afb6f9:sign_check.delinq_count_6m.coef_sign]]` | verified | 1 |
| 59 | conceptual_soundness | The value of `sign_check.delinq_count_6m.univariate_directio… | 1 | ratio | sign_check |  | eq | `[[art:549e904e:sign_check.delinq_count_6m.univariate_direction]]` | verified | 1 |
| 60 | conceptual_soundness | The value of `sign_check.delinq_last.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:a8ba9372:sign_check.delinq_last.agrees]]` | verified | 1 |
| 61 | conceptual_soundness | The value of `sign_check.delinq_last.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:50d352f8:sign_check.delinq_last.coef_sign]]` | verified | 1 |
| 62 | conceptual_soundness | The value of `sign_check.delinq_last.univariate_direction` i… | 1 | ratio | sign_check |  | eq | `[[art:a78648ba:sign_check.delinq_last.univariate_direction]]` | verified | 1 |
| 63 | conceptual_soundness | The value of `sign_check.delinq_max_6m.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:da92a015:sign_check.delinq_max_6m.agrees]]` | verified | 1 |
| 64 | conceptual_soundness | The value of `sign_check.delinq_max_6m.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:53560657:sign_check.delinq_max_6m.coef_sign]]` | verified | 1 |
| 65 | conceptual_soundness | The value of `sign_check.delinq_max_6m.univariate_direction`… | 1 | ratio | sign_check |  | eq | `[[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]]` | verified | 1 |
| 66 | conceptual_soundness | The value of `sign_check.limit_bal.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:0278aad1:sign_check.limit_bal.agrees]]` | verified | 0 |
| 67 | conceptual_soundness | The value of `sign_check.limit_bal.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:6af6aef2:sign_check.limit_bal.coef_sign]]` | verified | 1 |
| 68 | conceptual_soundness | The value of `sign_check.limit_bal.univariate_direction` is… | -1 | ratio | sign_check |  | eq | `[[art:56d284d6:sign_check.limit_bal.univariate_direction]]` | verified | -1 |
| 69 | conceptual_soundness | The value of `sign_check.n_disagreements` is 3 . | 3 | ratio | sign_check |  | eq | `[[art:e223cd4a:sign_check.n_disagreements]]` | verified | 3 |
| 70 | conceptual_soundness | The value of `sign_check.pay_ratio_last.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:7837941a:sign_check.pay_ratio_last.agrees]]` | verified | 1 |
| 71 | conceptual_soundness | The value of `sign_check.pay_ratio_last.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:489c3e67:sign_check.pay_ratio_last.coef_sign]]` | verified | -1 |
| 72 | conceptual_soundness | The value of `sign_check.pay_ratio_last.univariate_direction… | -1 | ratio | sign_check |  | eq | `[[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]]` | verified | -1 |
| 73 | conceptual_soundness | The value of `sign_check.pay_ratio_mean_6m.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:7e9a76ca:sign_check.pay_ratio_mean_6m.agrees]]` | verified | 1 |
| 74 | conceptual_soundness | The value of `sign_check.pay_ratio_mean_6m.coef_sign` is -1… | -1 | ratio | sign_check |  | eq | `[[art:077bb6b2:sign_check.pay_ratio_mean_6m.coef_sign]]` | verified | -1 |
| 75 | conceptual_soundness | The value of `sign_check.pay_ratio_mean_6m.univariate_direct… | -1 | ratio | sign_check |  | eq | `[[art:24dcef24:sign_check.pay_ratio_mean_6m.univariate_direction]]` | verified | -1 |
| 76 | conceptual_soundness | The value of `sign_check.utilisation.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:d0c9a130:sign_check.utilisation.agrees]]` | verified | 1 |
| 77 | conceptual_soundness | The value of `sign_check.utilisation.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:85badc3c:sign_check.utilisation.coef_sign]]` | verified | 1 |
| 78 | conceptual_soundness | The value of `sign_check.utilisation.univariate_direction` i… | 1 | ratio | sign_check |  | eq | `[[art:f0995196:sign_check.utilisation.univariate_direction]]` | verified | 1 |
| 79 | conceptual_soundness | The value of `threshold.E1.delta_auc` is 0.03 . | 0.03 | ratio | threshold |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 80 | data_integrity | The value of `csi.age` is 0.0002175 . | 0.0002175 | ratio | csi |  | eq | `[[art:0aad0eb8:csi.age]]` | verified | 0.0002174582447 |
| 81 | data_integrity | The value of `csi.bill_mean_6m` is 0.005952 . | 0.005952 | ratio | csi |  | eq | `[[art:4ceb65ea:csi.bill_mean_6m]]` | verified | 0.00595223424 |
| 82 | data_integrity | The value of `csi.bill_trend_6m` is 0.0004864 . | 0.0004864 | ratio | csi |  | eq | `[[art:93317930:csi.bill_trend_6m]]` | verified | 0.0004863886573 |
| 83 | data_integrity | The value of `csi.delinq_count_6m` is 0.0001786 . | 0.0001786 | ratio | csi |  | eq | `[[art:8359c176:csi.delinq_count_6m]]` | verified | 0.0001785733233 |
| 84 | data_integrity | The value of `csi.delinq_last` is 0.01811 . | 0.01811 | ratio | csi |  | eq | `[[art:c0b3fffe:csi.delinq_last]]` | verified | 0.01811466703 |
| 85 | data_integrity | The value of `csi.delinq_max_6m` is 0.0002075 . | 0.0002075 | ratio | csi |  | eq | `[[art:0bc44634:csi.delinq_max_6m]]` | verified | 0.0002075152658 |
| 86 | data_integrity | The value of `csi.limit_bal` is 0.0002442 . | 0.0002442 | ratio | csi |  | eq | `[[art:443540b2:csi.limit_bal]]` | verified | 0.0002441546194 |
| 87 | data_integrity | The value of `csi.max` is 0.01811 . | 0.01811 | ratio | csi |  | eq | `[[art:28c0a604:csi.max]]` | verified | 0.01811466703 |
| 88 | data_integrity | The value of `csi.pay_ratio_last` is 0.0000146 . | 1.46e-05 | ratio | csi |  | eq | `[[art:e06dbc50:csi.pay_ratio_last]]` | verified | 1.459725993e-05 |
| 89 | data_integrity | The value of `csi.pay_ratio_mean_6m` is 0.0045 . | 0.0045 | ratio | csi |  | eq | `[[art:adf83ef4:csi.pay_ratio_mean_6m]]` | verified | 0.004500399242 |
| 90 | data_integrity | The value of `csi.utilisation` is 0.01788 . | 0.01788 | ratio | csi |  | eq | `[[art:54e8c0d5:csi.utilisation]]` | verified | 0.01787504902 |
| 91 | data_integrity | The value of `leakage.duplicates.train` is 0 . | 0 | ratio | leakage |  | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 92 | data_integrity | The value of `leakage.name_screen.n_matched` is 0 . | 0 | ratio | leakage |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 93 | data_integrity | The value of `leakage.overlap` is 0 . | 0 | ratio | leakage |  | eq | `[[art:4c9fcd09:leakage.overlap]]` | verified | 0 |
| 94 | data_integrity | The value of `leakage.overlap.features` is 0 . | 0 | ratio | leakage |  | eq | `[[art:0fec8048:leakage.overlap.features]]` | verified | 0 |
| 95 | data_integrity | The value of `leakage.overlap.ids` is 0 . | 0 | ratio | leakage |  | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 96 | data_integrity | The value of `leakage.target_corr.max_single_feature_auc` is… | 0.6841 | ratio | leakage |  | eq | `[[art:f39d22de:leakage.target_corr.max_single_feature_auc]]` | verified | 0.6841001279 |
| 97 | data_integrity | The value of `leakage.timing.n_flagged` is 0 . | 0 | ratio | leakage |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 98 | data_integrity | The value of `profile.test.missing.max` is 0 . | 0 | ratio | profile |  | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 99 | data_integrity | The value of `profile.test.n` is 1500 . | 1500 | ratio | profile |  | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 100 | data_integrity | The value of `profile.train.missing.max` is 0 . | 0 | ratio | profile |  | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 101 | data_integrity | The value of `profile.train.n` is 3500 . | 3500 | ratio | profile |  | eq | `[[art:2510d49d:profile.train.n]]` | verified | 3500 |
| 102 | data_integrity | The value of `psi.age` is 0.01198 . | 0.01198 | ratio | psi |  | eq | `[[art:2e7b9ead:psi.age]]` | verified | 0.01198203437 |
| 103 | data_integrity | The value of `psi.bill_mean_6m` is 0.008018 . | 0.008018 | ratio | psi |  | eq | `[[art:a0afce85:psi.bill_mean_6m]]` | verified | 0.00801839524 |
| 104 | data_integrity | The value of `psi.bill_trend_6m` is 0.008579 . | 0.008579 | ratio | psi |  | eq | `[[art:b80e3091:psi.bill_trend_6m]]` | verified | 0.008579333007 |
| 105 | data_integrity | The value of `psi.delinq_count_6m` is 0.001414 . | 0.001414 | ratio | psi |  | eq | `[[art:4b7439f2:psi.delinq_count_6m]]` | verified | 0.001413525134 |
| 106 | data_integrity | The value of `psi.delinq_last` is 0.003062 . | 0.003062 | ratio | psi |  | eq | `[[art:7662ef2e:psi.delinq_last]]` | verified | 0.003062063118 |
| 107 | data_integrity | The value of `psi.delinq_max_6m` is 0.003729 . | 0.003729 | ratio | psi |  | eq | `[[art:b6668567:psi.delinq_max_6m]]` | verified | 0.00372909277 |
| 108 | data_integrity | The value of `psi.limit_bal` is 0.004676 . | 0.004676 | ratio | psi |  | eq | `[[art:09a00724:psi.limit_bal]]` | verified | 0.004675866811 |
| 109 | data_integrity | The value of `psi.max` is 0.02385 . | 0.02385 | ratio | psi |  | eq | `[[art:4a5ae1a0:psi.max]]` | verified | 0.02385256621 |
| 110 | data_integrity | The value of `psi.pay_ratio_last` is 0.006835 . | 0.006835 | ratio | psi |  | eq | `[[art:96c52004:psi.pay_ratio_last]]` | verified | 0.006835339118 |
| 111 | data_integrity | The value of `psi.pay_ratio_mean_6m` is 0.02385 . | 0.02385 | ratio | psi |  | eq | `[[art:e3761732:psi.pay_ratio_mean_6m]]` | verified | 0.02385256621 |
| 112 | data_integrity | The value of `psi.utilisation` is 0.01248 . | 0.01248 | ratio | psi |  | eq | `[[art:3c68d5ee:psi.utilisation]]` | verified | 0.01247544421 |
| 113 | data_integrity | The value of `psi.y_score` is 0.006306 . | 0.006306 | ratio | psi |  | eq | `[[art:4a23b13e:psi.y_score]]` | verified | 0.006306336141 |
| 114 | data_integrity | The value of `threshold.D1.missing_gap` is 0.1 . | 0.1 | ratio | threshold |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 115 | data_integrity | The value of `threshold.L1.single_feature_auc` is 0.9 . | 0.9 | ratio | threshold |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 116 | data_integrity | The value of `threshold.L2.overlap` is 0.005 . | 0.005 | ratio | threshold |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 117 | data_integrity | The value of `threshold.L2.overlap.features_effective` is 0.… | 0.005 | ratio | threshold |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 118 | data_integrity | The value of `threshold.S1.psi` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 119 | data_integrity | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 120 | outcomes | The value of `calibration.mean_rel_gap.test` is 0.02344 . | 0.02344 | ratio | calibration |  | eq | `[[art:fd64775d:calibration.mean_rel_gap.test]]` | verified | 0.02343524279 |
| 121 | outcomes | The value of `calibration.mean_rel_gap.train` is 0.00003599… | 3.599e-05 | ratio | calibration |  | eq | `[[art:ac0572fe:calibration.mean_rel_gap.train]]` | verified | 3.598625145e-05 |
| 122 | outcomes | The value of `calibration_intercept.test` is -0.1809 . | -0.1809 | ratio | calibration_intercept |  | eq | `[[art:386a6083:calibration_intercept.test]]` | verified | -0.1808989409 |
| 123 | outcomes | The value of `calibration_intercept.train` is 0.002422 . | 0.002422 | ratio | calibration_intercept |  | eq | `[[art:e1230838:calibration_intercept.train]]` | verified | 0.002421734739 |
| 124 | outcomes | The value of `calibration_slope.test` is 0.8701 . | 0.8701 | ratio | calibration_slope |  | eq | `[[art:7002f467:calibration_slope.test]]` | verified | 0.8701260273 |
| 125 | outcomes | The value of `calibration_slope.train` is 1.002 . | 1.002 | ratio | calibration_slope |  | eq | `[[art:7e7849d9:calibration_slope.train]]` | verified | 1.002056925 |
| 126 | outcomes | The value of `deciles.test.top2_capture` is 0.4345 . | 0.4345 | ratio | deciles |  | eq | `[[art:c7670b9d:deciles.test.top2_capture]]` | verified | 0.4345238095 |
| 127 | outcomes | The value of `deciles.train.top2_capture` is 0.4459 . | 0.4459 | ratio | deciles |  | eq | `[[art:0511095f:deciles.train.top2_capture]]` | verified | 0.4458598726 |
| 128 | outcomes | The value of `metrics.test.auc` is 0.7337 . | 0.7337 | ratio | metrics |  | eq | `[[art:3255122a:metrics.test.auc]]` | verified | 0.7336641916 |
| 129 | outcomes | The value of `metrics.test.brier` is 0.1536 . | 0.1536 | ratio | metrics |  | eq | `[[art:3cd28a53:metrics.test.brier]]` | verified | 0.1535518185 |
| 130 | outcomes | The value of `metrics.test.event_rate` is 0.224 . | 0.224 | ratio | metrics |  | eq | `[[art:5f15df2a:metrics.test.event_rate]]` | verified | 0.224 |
| 131 | outcomes | The value of `metrics.test.gini` is 0.4673 . | 0.4673 | ratio | metrics |  | eq | `[[art:621c8cf3:metrics.test.gini]]` | verified | 0.4673283832 |
| 132 | outcomes | The value of `metrics.test.ks` is 0.4096 . | 0.4096 | ratio | metrics |  | eq | `[[art:984fc4f0:metrics.test.ks]]` | verified | 0.4095790378 |
| 133 | outcomes | The value of `metrics.test.logloss` is 0.4788 . | 0.4788 | ratio | metrics |  | eq | `[[art:1362ad67:metrics.test.logloss]]` | verified | 0.4787760084 |
| 134 | outcomes | The value of `metrics.test.mean_predicted` is 0.2292 . | 0.2292 | ratio | metrics |  | eq | `[[art:f067e003:metrics.test.mean_predicted]]` | verified | 0.2292494944 |
| 135 | outcomes | The value of `metrics.test.n` is 1500 . | 1500 | ratio | metrics |  | eq | `[[art:64fcf14d:metrics.test.n]]` | verified | 1500 |
| 136 | outcomes | The value of `metrics.train.auc` is 0.769 . | 0.769 | ratio | metrics |  | eq | `[[art:197f9521:metrics.train.auc]]` | verified | 0.7690391902 |
| 137 | outcomes | The value of `metrics.train.brier` is 0.1489 . | 0.1489 | ratio | metrics |  | eq | `[[art:cf19f7b7:metrics.train.brier]]` | verified | 0.1488512538 |
| 138 | outcomes | The value of `metrics.train.event_rate` is 0.2243 . | 0.2243 | ratio | metrics |  | eq | `[[art:8a78b455:metrics.train.event_rate]]` | verified | 0.2242857143 |
| 139 | outcomes | The value of `metrics.train.gini` is 0.5381 . | 0.5381 | ratio | metrics |  | eq | `[[art:4208816b:metrics.train.gini]]` | verified | 0.5380783803 |
| 140 | outcomes | The value of `metrics.train.ks` is 0.4426 . | 0.4426 | ratio | metrics |  | eq | `[[art:f1d489d8:metrics.train.ks]]` | verified | 0.4425801457 |
| 141 | outcomes | The value of `metrics.train.logloss` is 0.4632 . | 0.4632 | ratio | metrics |  | eq | `[[art:a2852b4a:metrics.train.logloss]]` | verified | 0.4632349902 |
| 142 | outcomes | The value of `metrics.train.mean_predicted` is 0.2243 . | 0.2243 | ratio | metrics |  | eq | `[[art:5ec77e91:metrics.train.mean_predicted]]` | verified | 0.2242776431 |
| 143 | outcomes | The value of `metrics.train.n` is 3500 . | 3500 | ratio | metrics |  | eq | `[[art:564683ee:metrics.train.n]]` | verified | 3500 |
| 144 | outcomes | The value of `psi.age` is 0.01198 . | 0.01198 | ratio | psi |  | eq | `[[art:2e7b9ead:psi.age]]` | verified | 0.01198203437 |
| 145 | outcomes | The value of `psi.bill_mean_6m` is 0.008018 . | 0.008018 | ratio | psi |  | eq | `[[art:a0afce85:psi.bill_mean_6m]]` | verified | 0.00801839524 |
| 146 | outcomes | The value of `psi.bill_trend_6m` is 0.008579 . | 0.008579 | ratio | psi |  | eq | `[[art:b80e3091:psi.bill_trend_6m]]` | verified | 0.008579333007 |
| 147 | outcomes | The value of `psi.delinq_count_6m` is 0.001414 . | 0.001414 | ratio | psi |  | eq | `[[art:4b7439f2:psi.delinq_count_6m]]` | verified | 0.001413525134 |
| 148 | outcomes | The value of `psi.delinq_last` is 0.003062 . | 0.003062 | ratio | psi |  | eq | `[[art:7662ef2e:psi.delinq_last]]` | verified | 0.003062063118 |
| 149 | outcomes | The value of `psi.delinq_max_6m` is 0.003729 . | 0.003729 | ratio | psi |  | eq | `[[art:b6668567:psi.delinq_max_6m]]` | verified | 0.00372909277 |
| 150 | outcomes | The value of `psi.limit_bal` is 0.004676 . | 0.004676 | ratio | psi |  | eq | `[[art:09a00724:psi.limit_bal]]` | verified | 0.004675866811 |
| 151 | outcomes | The value of `psi.max` is 0.02385 . | 0.02385 | ratio | psi |  | eq | `[[art:4a5ae1a0:psi.max]]` | verified | 0.02385256621 |
| 152 | outcomes | The value of `psi.pay_ratio_last` is 0.006835 . | 0.006835 | ratio | psi |  | eq | `[[art:96c52004:psi.pay_ratio_last]]` | verified | 0.006835339118 |
| 153 | outcomes | The value of `psi.pay_ratio_mean_6m` is 0.02385 . | 0.02385 | ratio | psi |  | eq | `[[art:e3761732:psi.pay_ratio_mean_6m]]` | verified | 0.02385256621 |
| 154 | outcomes | The value of `psi.utilisation` is 0.01248 . | 0.01248 | ratio | psi |  | eq | `[[art:3c68d5ee:psi.utilisation]]` | verified | 0.01247544421 |
| 155 | outcomes | The value of `psi.y_score` is 0.006306 . | 0.006306 | ratio | psi |  | eq | `[[art:4a23b13e:psi.y_score]]` | verified | 0.006306336141 |
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
| 168 | outcomes | The value of `threshold.R1.auc_gap` is 0.1 . | 0.1 | ratio | threshold |  | eq | `[[art:b64213d7:threshold.R1.auc_gap]]` | verified | 0.1 |
| 169 | outcomes | The value of `threshold.R1.sign_flip_coef` is 0.05 . | 0.05 | ratio | threshold |  | eq | `[[art:aca84377:threshold.R1.sign_flip_coef]]` | verified | 0.05 |
| 170 | outcomes | The value of `threshold.R1.sign_flip_z` is 2 . | 2 | ratio | threshold |  | eq | `[[art:2e4428c7:threshold.R1.sign_flip_z]]` | verified | 2 |
| 171 | outcomes | The value of `threshold.S1.psi` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 172 | outcomes | The value of `threshold.package.auc.test.min` is 0.7 . | 0.7 | ratio | threshold |  | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 173 | outcomes | The value of `threshold.package.brier.test.max` is 0.2 . | 0.2 | ratio | threshold |  | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 174 | outcomes | The value of `threshold.package.calibration_slope.test.max`… | 1.2 | ratio | threshold |  | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 175 | outcomes | The value of `threshold.package.calibration_slope.test.min`… | 0.8 | ratio | threshold |  | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 176 | outcomes | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 177 | sensitivity | The value of `condition_number` is 5.647 . | 5.647 | ratio | condition_number |  | eq | `[[art:8dc0c2f1:condition_number]]` | verified | 5.646537667 |
| 178 | sensitivity | The value of `stability.age.sign_flip` is 0 . | 0 | ratio | stability |  | eq | `[[art:af9b1d06:stability.age.sign_flip]]` | verified | 0 |
| 179 | sensitivity | The value of `stability.bill_mean_6m.sign_flip` is 0 . | 0 | ratio | stability |  | eq | `[[art:df546086:stability.bill_mean_6m.sign_flip]]` | verified | 0 |
| 180 | sensitivity | The value of `stability.bill_trend_6m.sign_flip` is 1 . | 1 | ratio | stability |  | eq | `[[art:4dc17324:stability.bill_trend_6m.sign_flip]]` | verified | 1 |
| 181 | sensitivity | The value of `stability.delinq_count_6m.sign_flip` is 0 . | 0 | ratio | stability |  | eq | `[[art:40d78102:stability.delinq_count_6m.sign_flip]]` | verified | 0 |
| 182 | sensitivity | The value of `stability.delinq_last.sign_flip` is 0 . | 0 | ratio | stability |  | eq | `[[art:a7adedc7:stability.delinq_last.sign_flip]]` | verified | 0 |
| 183 | sensitivity | The value of `stability.delinq_max_6m.sign_flip` is 0 . | 0 | ratio | stability |  | eq | `[[art:908eec36:stability.delinq_max_6m.sign_flip]]` | verified | 0 |
| 184 | sensitivity | The value of `stability.limit_bal.sign_flip` is 0 . | 0 | ratio | stability |  | eq | `[[art:3a0e7e0d:stability.limit_bal.sign_flip]]` | verified | 0 |
| 185 | sensitivity | The value of `stability.pay_ratio_last.sign_flip` is 0 . | 0 | ratio | stability |  | eq | `[[art:77aa667a:stability.pay_ratio_last.sign_flip]]` | verified | 0 |
| 186 | sensitivity | The value of `stability.pay_ratio_mean_6m.sign_flip` is 0 . | 0 | ratio | stability |  | eq | `[[art:f8da40ca:stability.pay_ratio_mean_6m.sign_flip]]` | verified | 0 |
| 187 | sensitivity | The value of `stability.utilisation.sign_flip` is 0 . | 0 | ratio | stability |  | eq | `[[art:5b813a1b:stability.utilisation.sign_flip]]` | verified | 0 |
| 188 | sensitivity | The value of `threshold.M1.condition_number` is 30 . | 30 | ratio | threshold |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 189 | sensitivity | The value of `threshold.M1.vif` is 10 . | 10 | ratio | threshold |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 190 | sensitivity | The value of `threshold.R1.auc_gap` is 0.1 . | 0.1 | ratio | threshold |  | eq | `[[art:b64213d7:threshold.R1.auc_gap]]` | verified | 0.1 |
| 191 | sensitivity | The value of `threshold.R1.sign_flip_coef` is 0.05 . | 0.05 | ratio | threshold |  | eq | `[[art:aca84377:threshold.R1.sign_flip_coef]]` | verified | 0.05 |
| 192 | sensitivity | The value of `threshold.R1.sign_flip_z` is 2 . | 2 | ratio | threshold |  | eq | `[[art:2e4428c7:threshold.R1.sign_flip_z]]` | verified | 2 |
| 193 | sensitivity | The value of `vif.age` is 1.003 . | 1.003 | ratio | vif |  | eq | `[[art:193052e1:vif.age]]` | verified | 1.003158787 |
| 194 | sensitivity | The value of `vif.bill_mean_6m` is 7.512 . | 7.512 | ratio | vif |  | eq | `[[art:19127172:vif.bill_mean_6m]]` | verified | 7.511880286 |
| 195 | sensitivity | The value of `vif.bill_trend_6m` is 1.217 . | 1.217 | ratio | vif |  | eq | `[[art:36ec368c:vif.bill_trend_6m]]` | verified | 1.217478854 |
| 196 | sensitivity | The value of `vif.delinq_count_6m` is 2.527 . | 2.527 | ratio | vif |  | eq | `[[art:063976d6:vif.delinq_count_6m]]` | verified | 2.527119253 |
| 197 | sensitivity | The value of `vif.delinq_last` is 1.433 . | 1.433 | ratio | vif |  | eq | `[[art:1d3a39df:vif.delinq_last]]` | verified | 1.433233823 |
| 198 | sensitivity | The value of `vif.delinq_max_6m` is 2.375 . | 2.375 | ratio | vif |  | eq | `[[art:fa4a6cf4:vif.delinq_max_6m]]` | verified | 2.374670872 |
| 199 | sensitivity | The value of `vif.limit_bal` is 4.832 . | 4.832 | ratio | vif |  | eq | `[[art:f19a1ae6:vif.limit_bal]]` | verified | 4.831600304 |
| 200 | sensitivity | The value of `vif.max` is 7.512 . | 7.512 | ratio | vif |  | eq | `[[art:2d17cd9e:vif.max]]` | verified | 7.511880286 |
| 201 | sensitivity | The value of `vif.pay_ratio_last` is 7.213 . | 7.213 | ratio | vif |  | eq | `[[art:a9b805e2:vif.pay_ratio_last]]` | verified | 7.212565743 |
| 202 | sensitivity | The value of `vif.pay_ratio_mean_6m` is 7.206 . | 7.206 | ratio | vif |  | eq | `[[art:76a555ef:vif.pay_ratio_mean_6m]]` | verified | 7.205620957 |
| 203 | sensitivity | The value of `vif.utilisation` is 3.408 . | 3.408 | ratio | vif |  | eq | `[[art:87292dc8:vif.utilisation]]` | verified | 3.407876506 |
| 204 | findings | The value of `challenger.auc` is 0.7898 . | 0.7898 | ratio | challenger |  | eq | `[[art:2b3381be:challenger.auc]]` | verified | 0.7897950417 |
| 205 | findings | The value of `challenger.delta_auc` is 0.05613 . | 0.05613 | ratio | challenger |  | eq | `[[art:9cbcc544:challenger.delta_auc]]` | verified | 0.05613085011 |
| 206 | findings | The value of `metrics.test.auc` is 0.7337 . | 0.7337 | ratio | metrics |  | eq | `[[art:3255122a:metrics.test.auc]]` | verified | 0.7336641916 |
| 207 | findings | The value of `sign_check.age.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:5c2c50b8:sign_check.age.agrees]]` | verified | 0 |
| 208 | findings | The value of `sign_check.age.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:6172eb93:sign_check.age.coef_sign]]` | verified | -1 |
| 209 | findings | The value of `sign_check.age.univariate_direction` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:cac34cd5:sign_check.age.univariate_direction]]` | verified | 1 |
| 210 | findings | The value of `sign_check.bill_mean_6m.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:4df8b747:sign_check.bill_mean_6m.agrees]]` | verified | 0 |
| 211 | findings | The value of `sign_check.bill_mean_6m.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:cee1a18f:sign_check.bill_mean_6m.coef_sign]]` | verified | -1 |
| 212 | findings | The value of `sign_check.bill_mean_6m.univariate_direction`… | 1 | ratio | sign_check |  | eq | `[[art:82ba9862:sign_check.bill_mean_6m.univariate_direction]]` | verified | 1 |
| 213 | findings | The value of `sign_check.limit_bal.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:0278aad1:sign_check.limit_bal.agrees]]` | verified | 0 |
| 214 | findings | The value of `sign_check.limit_bal.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:6af6aef2:sign_check.limit_bal.coef_sign]]` | verified | 1 |
| 215 | findings | The value of `sign_check.limit_bal.univariate_direction` is… | -1 | ratio | sign_check |  | eq | `[[art:56d284d6:sign_check.limit_bal.univariate_direction]]` | verified | -1 |
| 216 | findings | The value of `stability.bill_trend_6m.sign_flip` is 1 . | 1 | ratio | stability |  | eq | `[[art:4dc17324:stability.bill_trend_6m.sign_flip]]` | verified | 1 |
| 217 | findings | The value of `threshold.E1.delta_auc` is 0.03 . | 0.03 | ratio | threshold |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 218 | findings | The value of `threshold.R1.sign_flip_coef` is 0.05 . | 0.05 | ratio | threshold |  | eq | `[[art:aca84377:threshold.R1.sign_flip_coef]]` | verified | 0.05 |
| 219 | findings | The value of `threshold.R1.sign_flip_z` is 2 . | 2 | ratio | threshold |  | eq | `[[art:2e4428c7:threshold.R1.sign_flip_z]]` | verified | 2 |
| 220 | monitoring | The value of `calibration_slope.test` is 0.8701 . | 0.8701 | ratio | calibration_slope |  | eq | `[[art:7002f467:calibration_slope.test]]` | verified | 0.8701260273 |
| 221 | monitoring | The value of `metrics.test.auc` is 0.7337 . | 0.7337 | ratio | metrics |  | eq | `[[art:3255122a:metrics.test.auc]]` | verified | 0.7336641916 |
| 222 | monitoring | The value of `metrics.test.brier` is 0.1536 . | 0.1536 | ratio | metrics |  | eq | `[[art:3cd28a53:metrics.test.brier]]` | verified | 0.1535518185 |
| 223 | monitoring | The value of `psi.max` is 0.02385 . | 0.02385 | ratio | psi |  | eq | `[[art:4a5ae1a0:psi.max]]` | verified | 0.02385256621 |
| 224 | monitoring | The value of `rule.calibration_first_event_rate` is 0.05 . | 0.05 | ratio | rule |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 225 | monitoring | The value of `threshold.package.auc.test.min` is 0.7 . | 0.7 | ratio | threshold |  | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 226 | monitoring | The value of `threshold.package.brier.test.max` is 0.2 . | 0.2 | ratio | threshold |  | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 227 | monitoring | The value of `threshold.package.calibration_slope.test.max`… | 1.2 | ratio | threshold |  | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 228 | monitoring | The value of `threshold.package.calibration_slope.test.min`… | 0.8 | ratio | threshold |  | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 229 | monitoring | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |

## Appendix B — Artifact index

The store holds 192 artifacts; the 152 this report cites or rests a finding on are indexed here.

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
| `metrics.train.auc` | `197f9521` | scalar | 0.7690391902 | auc on train, recomputed by quaestor |
| `metrics.train.brier` | `cf19f7b7` | scalar | 0.1488512538 | brier on train, recomputed by quaestor |
| `metrics.train.event_rate` | `8a78b455` | scalar | 0.2242857143 | event_rate on train, recomputed by quaestor |
| `metrics.train.gini` | `4208816b` | scalar | 0.5380783803 | gini on train, recomputed by quaestor |
| `metrics.train.ks` | `f1d489d8` | scalar | 0.4425801457 | ks on train, recomputed by quaestor |
| `metrics.train.logloss` | `a2852b4a` | scalar | 0.4632349902 | logloss on train, recomputed by quaestor |
| `metrics.train.mean_predicted` | `5ec77e91` | scalar | 0.2242776431 | mean_predicted on train, recomputed by quaestor |
| `metrics.train.n` | `564683ee` | scalar | 3500 | n on train, recomputed by quaestor |
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
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |
| `sign_check.age.agrees` | `5c2c50b8` | scalar | 0 | 1 when the fitted sign on age agrees with its univariate direction, 0 when it does not |
| `sign_check.age.coef_sign` | `6172eb93` | scalar | -1 | the sign of the fitted coefficient on age |
| `sign_check.age.univariate_direction` | `cac34cd5` | scalar | 1 | the sign of age's own single-feature AUC on train minus 0.5 |
| `sign_check.bill_mean_6m.agrees` | `4df8b747` | scalar | 0 | 1 when the fitted sign on bill_mean_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.bill_mean_6m.coef_sign` | `cee1a18f` | scalar | -1 | the sign of the fitted coefficient on bill_mean_6m |
| `sign_check.bill_mean_6m.univariate_direction` | `82ba9862` | scalar | 1 | the sign of bill_mean_6m's own single-feature AUC on train minus 0.5 |
| `sign_check.bill_trend_6m.agrees` | `ff3cb24a` | scalar | 1 | 1 when the fitted sign on bill_trend_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.bill_trend_6m.coef_sign` | `7fd8474e` | scalar | -1 | the sign of the fitted coefficient on bill_trend_6m |
| `sign_check.bill_trend_6m.univariate_direction` | `a9bff389` | scalar | -1 | the sign of bill_trend_6m's own single-feature AUC on train minus 0.5 |
| `sign_check.delinq_count_6m.agrees` | `a337d16b` | scalar | 1 | 1 when the fitted sign on delinq_count_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.delinq_count_6m.coef_sign` | `17afb6f9` | scalar | 1 | the sign of the fitted coefficient on delinq_count_6m |
| `sign_check.delinq_count_6m.univariate_direction` | `549e904e` | scalar | 1 | the sign of delinq_count_6m's own single-feature AUC on train minus 0.5 |
| `sign_check.delinq_last.agrees` | `a8ba9372` | scalar | 1 | 1 when the fitted sign on delinq_last agrees with its univariate direction, 0 when it does not |
| `sign_check.delinq_last.coef_sign` | `50d352f8` | scalar | 1 | the sign of the fitted coefficient on delinq_last |
| `sign_check.delinq_last.univariate_direction` | `a78648ba` | scalar | 1 | the sign of delinq_last's own single-feature AUC on train minus 0.5 |
| `sign_check.delinq_max_6m.agrees` | `da92a015` | scalar | 1 | 1 when the fitted sign on delinq_max_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.delinq_max_6m.coef_sign` | `53560657` | scalar | 1 | the sign of the fitted coefficient on delinq_max_6m |
| `sign_check.delinq_max_6m.univariate_direction` | `b9088f4a` | scalar | 1 | the sign of delinq_max_6m's own single-feature AUC on train minus 0.5 |
| `sign_check.limit_bal.agrees` | `0278aad1` | scalar | 0 | 1 when the fitted sign on limit_bal agrees with its univariate direction, 0 when it does not |
| `sign_check.limit_bal.coef_sign` | `6af6aef2` | scalar | 1 | the sign of the fitted coefficient on limit_bal |
| `sign_check.limit_bal.univariate_direction` | `56d284d6` | scalar | -1 | the sign of limit_bal's own single-feature AUC on train minus 0.5 |
| `sign_check.n_disagreements` | `e223cd4a` | scalar | 3 | retained features whose fitted sign contradicts their univariate direction, of 10 checked |
| `sign_check.pay_ratio_last.agrees` | `7837941a` | scalar | 1 | 1 when the fitted sign on pay_ratio_last agrees with its univariate direction, 0 when it does not |
| `sign_check.pay_ratio_last.coef_sign` | `489c3e67` | scalar | -1 | the sign of the fitted coefficient on pay_ratio_last |
| `sign_check.pay_ratio_last.univariate_direction` | `f8e46d75` | scalar | -1 | the sign of pay_ratio_last's own single-feature AUC on train minus 0.5 |
| `sign_check.pay_ratio_mean_6m.agrees` | `7e9a76ca` | scalar | 1 | 1 when the fitted sign on pay_ratio_mean_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.pay_ratio_mean_6m.coef_sign` | `077bb6b2` | scalar | -1 | the sign of the fitted coefficient on pay_ratio_mean_6m |
| `sign_check.pay_ratio_mean_6m.univariate_direction` | `24dcef24` | scalar | -1 | the sign of pay_ratio_mean_6m's own single-feature AUC on train minus 0.5 |
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
| tool calls | 14 (run_model 1, profile_data 1, compute_metrics 1, check_leakage 1, check_stability 1, check_collinearity 1, challenger_compare 1, retrieve_guidance 7) |
| plan steps (bounded loop) | 0 |
| LLM calls | 0 () |
| re-asks | 0 |
| repair rounds | 0 |
| tokens in / out | 0 / 0 |
| notional cost (USD) | 0.0000 |
| wall-clock (s) | 1.27 |
| subject run (s) | 1.18 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | fake |
| model | none: no model answered |
| run id | credit_default-rules_only-20260918T065329Z-bd5861e9 |

## Appendix D — Not checked

| item | reason |
|---|---|
| `run_scenarios` (X1) | not applicable to `binary_classification` |
| out-of-time and vintage-holdout metrics (O1, second rule) | package declares neither split |
| developer claims (T1, claim channel) | The package declares 2 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
| drafted narrative and the repair loop | `rules_only` calls no model; the narrative is a template |
