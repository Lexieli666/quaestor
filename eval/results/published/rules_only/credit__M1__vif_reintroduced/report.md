---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: rules_only
model: fake
run_id: credit_default-rules_only-20260918T065327Z-bd5861e9
data_mode: synthetic
synthetic_n: 5000
grounding_precision_pre: 1.0000
grounding_precision_post: 1.0000
n_claims: 246
n_findings_by_severity: {high: 0, medium: 1, low: 1, info: 0}
generated: "2026-09-18T06:53:27Z"
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
The value of `calibration_slope.test` is 0.9988 [[art:6d8bca25:calibration_slope.test]].
The value of `calibration_slope.train` is 1.005 [[art:79d5244e:calibration_slope.train]].
The value of `challenger.delta_auc` is 0.07444 [[art:d7dbe8ff:challenger.delta_auc]].
The value of `condition_number` is 1023 [[art:36c154df:condition_number]].
The value of `csi.max` is 0.0237 [[art:aa2ba789:csi.max]].
The value of `metrics.test.auc` is 0.7505 [[art:3bbb3e37:metrics.test.auc]].
The value of `metrics.test.brier` is 0.1486 [[art:08bbf5ff:metrics.test.brier]].
The value of `metrics.test.event_rate` is 0.2247 [[art:9209d200:metrics.test.event_rate]].
The value of `metrics.test.gini` is 0.5009 [[art:1456c955:metrics.test.gini]].
The value of `metrics.test.ks` is 0.4317 [[art:414deaff:metrics.test.ks]].
The value of `metrics.test.logloss` is 0.467 [[art:dee4fde4:metrics.test.logloss]].
The value of `metrics.test.mean_predicted` is 0.2215 [[art:461086da:metrics.test.mean_predicted]].
The value of `metrics.test.n` is 1500 [[art:64fcf14d:metrics.test.n]].
The value of `metrics.train.auc` is 0.7607 [[art:9b2be514:metrics.train.auc]].
The value of `metrics.train.brier` is 0.1486 [[art:2fe86f99:metrics.train.brier]].
The value of `metrics.train.event_rate` is 0.2246 [[art:133a5ff8:metrics.train.event_rate]].
The value of `metrics.train.gini` is 0.5215 [[art:94b21017:metrics.train.gini]].
The value of `metrics.train.ks` is 0.4489 [[art:a3928b90:metrics.train.ks]].
The value of `metrics.train.logloss` is 0.464 [[art:522ccdcf:metrics.train.logloss]].
The value of `metrics.train.mean_predicted` is 0.2246 [[art:4103f0d8:metrics.train.mean_predicted]].
The value of `metrics.train.n` is 3500 [[art:564683ee:metrics.train.n]].
The value of `profile.test.n` is 1500 [[art:2193cf5f:profile.test.n]].
The value of `profile.train.n` is 3500 [[art:2510d49d:profile.train.n]].
The value of `psi.max` is 0.01372 [[art:d34e2b0f:psi.max]].
The value of `runtime.max_seconds` is 300 [[art:2ad8d1a5:runtime.max_seconds]].
The value of `threshold.package.auc.test.min` is 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]].
The value of `threshold.package.brier.test.max` is 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]].
The value of `threshold.package.calibration_slope.test.max` is 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The value of `threshold.package.calibration_slope.test.min` is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
The value of `vif.max` is 121900 [[art:e6655d27:vif.max]].

## 2. Conceptual soundness

This section follows the model risk management guidance at [[reg:SR26-2:V.1.a]].
The value of `ablation.age.delta_auc` is -0.0004261 [[art:4bde085d:ablation.age.delta_auc]].
The value of `ablation.baseline_auc` is 0.7505 [[art:2166cf12:ablation.baseline_auc]].
The value of `ablation.bill_last.delta_auc` is 0.0001786 [[art:eea44d10:ablation.bill_last.delta_auc]].
The value of `ablation.bill_last_adj.delta_auc` is 0.00001531 [[art:8e9d6dcc:ablation.bill_last_adj.delta_auc]].
The value of `ablation.bill_mean_6m.delta_auc` is -0.0002909 [[art:52f6233e:ablation.bill_mean_6m.delta_auc]].
The value of `ablation.bill_trend_6m.delta_auc` is 0.0002526 [[art:994f00bc:ablation.bill_trend_6m.delta_auc]].
The value of `ablation.delinq_count_6m.delta_auc` is 0.001526 [[art:5da50826:ablation.delinq_count_6m.delta_auc]].
The value of `ablation.delinq_last.delta_auc` is -0.07782 [[art:8eca80c6:ablation.delinq_last.delta_auc]].
The value of `ablation.delinq_max_6m.delta_auc` is 0.0003572 [[art:16dcea2b:ablation.delinq_max_6m.delta_auc]].
The value of `ablation.limit_bal.delta_auc` is 0.0001786 [[art:6bf0f1c3:ablation.limit_bal.delta_auc]].
The value of `ablation.pay_ratio_last.delta_auc` is 0.002437 [[art:9639fcbd:ablation.pay_ratio_last.delta_auc]].
The value of `ablation.pay_ratio_mean_6m.delta_auc` is 0.007333 [[art:5e7307e8:ablation.pay_ratio_mean_6m.delta_auc]].
The value of `ablation.utilisation.delta_auc` is -0.0003113 [[art:90093ed9:ablation.utilisation.delta_auc]].
The value of `ablation.utilisation_mean_6m.delta_auc` is -0.0005231 [[art:c63504c6:ablation.utilisation_mean_6m.delta_auc]].
The value of `challenger.auc` is 0.8249 [[art:9727c6a9:challenger.auc]].
The value of `challenger.brier` is 0.1242 [[art:79d61058:challenger.brier]].
The value of `challenger.delta_auc` is 0.07444 [[art:d7dbe8ff:challenger.delta_auc]].
The value of `metrics.test.auc` is 0.7505 [[art:3bbb3e37:metrics.test.auc]].
The value of `metrics.test.brier` is 0.1486 [[art:08bbf5ff:metrics.test.brier]].
The value of `sign_check.age.agrees` is 1 [[art:4116add1:sign_check.age.agrees]].
The value of `sign_check.age.coef_sign` is -1 [[art:6172eb93:sign_check.age.coef_sign]].
The value of `sign_check.age.univariate_direction` is -1 [[art:66364583:sign_check.age.univariate_direction]].
The value of `sign_check.bill_last.agrees` is 1 [[art:98c00451:sign_check.bill_last.agrees]].
The value of `sign_check.bill_last.coef_sign` is -1 [[art:4a9f78da:sign_check.bill_last.coef_sign]].
The value of `sign_check.bill_last.univariate_direction` is -1 [[art:9e67bc2c:sign_check.bill_last.univariate_direction]].
The value of `sign_check.bill_last_adj.agrees` is 1 [[art:fb9031bc:sign_check.bill_last_adj.agrees]].
The value of `sign_check.bill_last_adj.coef_sign` is -1 [[art:6b02e9dc:sign_check.bill_last_adj.coef_sign]].
The value of `sign_check.bill_last_adj.univariate_direction` is -1 [[art:cfadf2b7:sign_check.bill_last_adj.univariate_direction]].
The value of `sign_check.bill_mean_6m.agrees` is 0 [[art:4df8b747:sign_check.bill_mean_6m.agrees]].
The value of `sign_check.bill_mean_6m.coef_sign` is 1 [[art:a457c04a:sign_check.bill_mean_6m.coef_sign]].
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
The value of `sign_check.n_disagreements` is 4 [[art:b9e93d79:sign_check.n_disagreements]].
The value of `sign_check.pay_ratio_last.agrees` is 0 [[art:79abee77:sign_check.pay_ratio_last.agrees]].
The value of `sign_check.pay_ratio_last.coef_sign` is 1 [[art:f018263e:sign_check.pay_ratio_last.coef_sign]].
The value of `sign_check.pay_ratio_last.univariate_direction` is -1 [[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]].
The value of `sign_check.pay_ratio_mean_6m.agrees` is 1 [[art:7e9a76ca:sign_check.pay_ratio_mean_6m.agrees]].
The value of `sign_check.pay_ratio_mean_6m.coef_sign` is -1 [[art:077bb6b2:sign_check.pay_ratio_mean_6m.coef_sign]].
The value of `sign_check.pay_ratio_mean_6m.univariate_direction` is -1 [[art:24dcef24:sign_check.pay_ratio_mean_6m.univariate_direction]].
The value of `sign_check.utilisation.agrees` is 1 [[art:d0c9a130:sign_check.utilisation.agrees]].
The value of `sign_check.utilisation.coef_sign` is 1 [[art:85badc3c:sign_check.utilisation.coef_sign]].
The value of `sign_check.utilisation.univariate_direction` is 1 [[art:f0995196:sign_check.utilisation.univariate_direction]].
The value of `sign_check.utilisation_mean_6m.agrees` is 1 [[art:c2848161:sign_check.utilisation_mean_6m.agrees]].
The value of `sign_check.utilisation_mean_6m.coef_sign` is 1 [[art:cf902b59:sign_check.utilisation_mean_6m.coef_sign]].
The value of `sign_check.utilisation_mean_6m.univariate_direction` is 1 [[art:35612306:sign_check.utilisation_mean_6m.univariate_direction]].
The value of `threshold.E1.delta_auc` is 0.03 [[art:e042774c:threshold.E1.delta_auc]].
Candidates raised on this section's material: E1 (see the findings section).

## 3. Data integrity and drift

This section follows the model risk management guidance at [[reg:SR26-2:V.1.a]].
The value of `csi.age` is 0.0009462 [[art:a1e9712b:csi.age]].
The value of `csi.bill_last` is 0.00755 [[art:609757f9:csi.bill_last]].
The value of `csi.bill_last_adj` is 0.007981 [[art:3945402b:csi.bill_last_adj]].
The value of `csi.bill_mean_6m` is 0.004327 [[art:a221465d:csi.bill_mean_6m]].
The value of `csi.bill_trend_6m` is 0.0006834 [[art:c7ef6238:csi.bill_trend_6m]].
The value of `csi.delinq_count_6m` is 0.002436 [[art:4bcd65c1:csi.delinq_count_6m]].
The value of `csi.delinq_last` is 0.0237 [[art:471433c6:csi.delinq_last]].
The value of `csi.delinq_max_6m` is 0.0008971 [[art:0cd543bd:csi.delinq_max_6m]].
The value of `csi.limit_bal` is 0.001916 [[art:d25f5a77:csi.limit_bal]].
The value of `csi.max` is 0.0237 [[art:aa2ba789:csi.max]].
The value of `csi.pay_ratio_last` is 0.00205 [[art:4461bc3a:csi.pay_ratio_last]].
The value of `csi.pay_ratio_mean_6m` is 0.001802 [[art:dc5c1bb6:csi.pay_ratio_mean_6m]].
The value of `csi.utilisation` is 0.00249 [[art:b5e8df76:csi.utilisation]].
The value of `csi.utilisation_mean_6m` is 0.00214 [[art:71b78094:csi.utilisation_mean_6m]].
The value of `leakage.duplicates.train` is 0 [[art:4474c227:leakage.duplicates.train]].
The value of `leakage.name_screen.n_matched` is 0 [[art:407e62be:leakage.name_screen.n_matched]].
The value of `leakage.overlap` is 0 [[art:4c9fcd09:leakage.overlap]].
The value of `leakage.overlap.features` is 0 [[art:0fec8048:leakage.overlap.features]].
The value of `leakage.overlap.ids` is 0 [[art:63d37fc5:leakage.overlap.ids]].
The value of `leakage.target_corr.max_single_feature_auc` is 0.6831 [[art:fd829fc4:leakage.target_corr.max_single_feature_auc]].
The value of `leakage.timing.n_flagged` is 0 [[art:742bcd24:leakage.timing.n_flagged]].
The value of `profile.test.missing.max` is 0 [[art:f813848d:profile.test.missing.max]].
The value of `profile.test.n` is 1500 [[art:2193cf5f:profile.test.n]].
The value of `profile.train.missing.max` is 0 [[art:050a3099:profile.train.missing.max]].
The value of `profile.train.n` is 3500 [[art:2510d49d:profile.train.n]].
The value of `psi.age` is 0.008124 [[art:f9255a0a:psi.age]].
The value of `psi.bill_last` is 0.01302 [[art:cd0c79c3:psi.bill_last]].
The value of `psi.bill_last_adj` is 0.01372 [[art:e87eb6d6:psi.bill_last_adj]].
The value of `psi.bill_mean_6m` is 0.007124 [[art:028e4281:psi.bill_mean_6m]].
The value of `psi.bill_trend_6m` is 0.00958 [[art:c247a6f2:psi.bill_trend_6m]].
The value of `psi.delinq_count_6m` is 0.002069 [[art:61491d02:psi.delinq_count_6m]].
The value of `psi.delinq_last` is 0.00285 [[art:03bd52e7:psi.delinq_last]].
The value of `psi.delinq_max_6m` is 0.005498 [[art:7a82e7f3:psi.delinq_max_6m]].
The value of `psi.limit_bal` is 0.01095 [[art:601cdba2:psi.limit_bal]].
The value of `psi.max` is 0.01372 [[art:d34e2b0f:psi.max]].
The value of `psi.pay_ratio_last` is 0.004966 [[art:3af2ca29:psi.pay_ratio_last]].
The value of `psi.pay_ratio_mean_6m` is 0.0055 [[art:2c5baeb2:psi.pay_ratio_mean_6m]].
The value of `psi.utilisation` is 0.004244 [[art:451e0780:psi.utilisation]].
The value of `psi.utilisation_mean_6m` is 0.002875 [[art:d562032d:psi.utilisation_mean_6m]].
The value of `psi.y_score` is 0.004589 [[art:8d23655e:psi.y_score]].
The value of `threshold.D1.missing_gap` is 0.1 [[art:9cce25ea:threshold.D1.missing_gap]].
The value of `threshold.L1.single_feature_auc` is 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]].
The value of `threshold.L2.overlap` is 0.005 [[art:9f336eaf:threshold.L2.overlap]].
The value of `threshold.L2.overlap.features_effective` is 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].
The value of `threshold.S1.psi` is 0.25 [[art:278b9016:threshold.S1.psi]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].

## 4. Outcomes analysis

This section follows the model risk management guidance at [[reg:SR26-2:V.1.b]].
The value of `calibration.mean_rel_gap.test` is 0.01419 [[art:22eeaff2:calibration.mean_rel_gap.test]].
The value of `calibration.mean_rel_gap.train` is 0.00008266 [[art:ca4e4c16:calibration.mean_rel_gap.train]].
The value of `calibration_intercept.test` is 0.02018 [[art:a813ed8b:calibration_intercept.test]].
The value of `calibration_intercept.train` is 0.005847 [[art:79bab09a:calibration_intercept.train]].
The value of `calibration_slope.test` is 0.9988 [[art:6d8bca25:calibration_slope.test]].
The value of `calibration_slope.train` is 1.005 [[art:79d5244e:calibration_slope.train]].
The value of `deciles.test.top2_capture` is 0.4659 [[art:b4ba6281:deciles.test.top2_capture]].
The value of `deciles.train.top2_capture` is 0.4504 [[art:250e62bc:deciles.train.top2_capture]].
The value of `metrics.test.auc` is 0.7505 [[art:3bbb3e37:metrics.test.auc]].
The value of `metrics.test.brier` is 0.1486 [[art:08bbf5ff:metrics.test.brier]].
The value of `metrics.test.event_rate` is 0.2247 [[art:9209d200:metrics.test.event_rate]].
The value of `metrics.test.gini` is 0.5009 [[art:1456c955:metrics.test.gini]].
The value of `metrics.test.ks` is 0.4317 [[art:414deaff:metrics.test.ks]].
The value of `metrics.test.logloss` is 0.467 [[art:dee4fde4:metrics.test.logloss]].
The value of `metrics.test.mean_predicted` is 0.2215 [[art:461086da:metrics.test.mean_predicted]].
The value of `metrics.test.n` is 1500 [[art:64fcf14d:metrics.test.n]].
The value of `metrics.train.auc` is 0.7607 [[art:9b2be514:metrics.train.auc]].
The value of `metrics.train.brier` is 0.1486 [[art:2fe86f99:metrics.train.brier]].
The value of `metrics.train.event_rate` is 0.2246 [[art:133a5ff8:metrics.train.event_rate]].
The value of `metrics.train.gini` is 0.5215 [[art:94b21017:metrics.train.gini]].
The value of `metrics.train.ks` is 0.4489 [[art:a3928b90:metrics.train.ks]].
The value of `metrics.train.logloss` is 0.464 [[art:522ccdcf:metrics.train.logloss]].
The value of `metrics.train.mean_predicted` is 0.2246 [[art:4103f0d8:metrics.train.mean_predicted]].
The value of `metrics.train.n` is 3500 [[art:564683ee:metrics.train.n]].
The value of `psi.age` is 0.008124 [[art:f9255a0a:psi.age]].
The value of `psi.bill_last` is 0.01302 [[art:cd0c79c3:psi.bill_last]].
The value of `psi.bill_last_adj` is 0.01372 [[art:e87eb6d6:psi.bill_last_adj]].
The value of `psi.bill_mean_6m` is 0.007124 [[art:028e4281:psi.bill_mean_6m]].
The value of `psi.bill_trend_6m` is 0.00958 [[art:c247a6f2:psi.bill_trend_6m]].
The value of `psi.delinq_count_6m` is 0.002069 [[art:61491d02:psi.delinq_count_6m]].
The value of `psi.delinq_last` is 0.00285 [[art:03bd52e7:psi.delinq_last]].
The value of `psi.delinq_max_6m` is 0.005498 [[art:7a82e7f3:psi.delinq_max_6m]].
The value of `psi.limit_bal` is 0.01095 [[art:601cdba2:psi.limit_bal]].
The value of `psi.max` is 0.01372 [[art:d34e2b0f:psi.max]].
The value of `psi.pay_ratio_last` is 0.004966 [[art:3af2ca29:psi.pay_ratio_last]].
The value of `psi.pay_ratio_mean_6m` is 0.0055 [[art:2c5baeb2:psi.pay_ratio_mean_6m]].
The value of `psi.utilisation` is 0.004244 [[art:451e0780:psi.utilisation]].
The value of `psi.utilisation_mean_6m` is 0.002875 [[art:d562032d:psi.utilisation_mean_6m]].
The value of `psi.y_score` is 0.004589 [[art:8d23655e:psi.y_score]].
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
Calibration by decile of predicted probability on test [[art:f4024126:calibration.test]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.0811 | 0.12 | 150 |
| 2 | 0.1058 | 0.07333 | 150 |
| 3 | 0.1214 | 0.07333 | 150 |
| 4 | 0.1363 | 0.1 | 150 |
| 5 | 0.1549 | 0.12 | 150 |
| 6 | 0.1737 | 0.1933 | 150 |
| 7 | 0.1986 | 0.16 | 150 |
| 8 | 0.2498 | 0.36 | 150 |
| 9 | 0.3836 | 0.4533 | 150 |
| 10 | 0.6095 | 0.5933 | 150 |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table deciles.test -->
Decile separation on test; decile 1 holds the highest probabilities [[art:b1875fbd:deciles.test]]:

| decile | count | events | event_rate | lift |
|---|---|---|---|---|
| 1 | 150 | 89 | 0.5933 | 2.641 |
| 2 | 150 | 68 | 0.4533 | 2.018 |
| 3 | 150 | 54 | 0.36 | 1.602 |
| 4 | 150 | 24 | 0.16 | 0.7122 |
| 5 | 150 | 29 | 0.1933 | 0.8605 |
| 6 | 150 | 18 | 0.12 | 0.5341 |
| 7 | 150 | 15 | 0.1 | 0.4451 |
| 8 | 150 | 11 | 0.07333 | 0.3264 |
| 9 | 150 | 11 | 0.07333 | 0.3264 |
| 10 | 150 | 18 | 0.12 | 0.5341 |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table thresholds.evaluation -->
Every threshold package.yaml declares, with its bound, the recomputed value and the outcome [[art:5b16d3a6:thresholds.evaluation]]:

| metric | split | bound | value | result |
|---|---|---|---|---|
| auc | test | minimum 0.7 | 0.7505 | pass |
| brier | test | maximum 0.2 | 0.1486 | pass |
| calibration_slope | test | minimum 0.8 | 0.9988 | pass |
| calibration_slope | test | maximum 1.2 | 0.9988 | pass |
| psi |  | maximum 0.25 | 0.01372 | pass |
<!-- quaestor:renderer:end -->

## 5. Sensitivity and scenario analysis

This section follows the model risk management guidance at [[reg:SR26-2:V.1.a]].
The value of `condition_number` is 1023 [[art:36c154df:condition_number]].
The value of `threshold.M1.condition_number` is 30 [[art:7e52fd7a:threshold.M1.condition_number]].
The value of `threshold.M1.vif` is 10 [[art:aeb4f33c:threshold.M1.vif]].
The value of `vif.age` is 1.002 [[art:c4867fa9:vif.age]].
The value of `vif.bill_last` is 121600 [[art:9139aeac:vif.bill_last]].
The value of `vif.bill_last_adj` is 121900 [[art:5216ecf3:vif.bill_last_adj]].
The value of `vif.bill_mean_6m` is 175.6 [[art:964ad8e8:vif.bill_mean_6m]].
The value of `vif.bill_trend_6m` is 5.551 [[art:2d1864b3:vif.bill_trend_6m]].
The value of `vif.delinq_count_6m` is 2.562 [[art:0e627a7d:vif.delinq_count_6m]].
The value of `vif.delinq_last` is 1.411 [[art:5fce8331:vif.delinq_last]].
The value of `vif.delinq_max_6m` is 2.409 [[art:c31719bd:vif.delinq_max_6m]].
The value of `vif.limit_bal` is 4.845 [[art:ffa16c31:vif.limit_bal]].
The value of `vif.max` is 121900 [[art:e6655d27:vif.max]].
The value of `vif.pay_ratio_last` is 7.269 [[art:6fb2f509:vif.pay_ratio_last]].
The value of `vif.pay_ratio_mean_6m` is 7.261 [[art:76c577a1:vif.pay_ratio_mean_6m]].
The value of `vif.utilisation` is 49.46 [[art:09540d95:vif.utilisation]].
The value of `vif.utilisation_mean_6m` is 50.25 [[art:5233c25b:vif.utilisation_mean_6m]].
Candidates raised on this section's material: M1 (see the findings section).

## 6. Findings and recommendations

This section follows the model risk management guidance at [[reg:SR26-2:VI.3]].

### F-001 · M1 collinearity · severity **medium**

**A `M1` finding, raised by `check_collinearity` at severity `medium`.**
Its evidence is the artifacts cited in this section; the check's own account of it is recorded in `findings.json`.

### F-002 · E1 effective challenge · severity **low**

**A `E1` finding, raised by `challenger_compare` at severity `low`.**
Its evidence is the artifacts cited in this section; the check's own account of it is recorded in `findings.json`.
The value of `challenger.auc` is 0.8249 [[art:9727c6a9:challenger.auc]].
The value of `challenger.delta_auc` is 0.07444 [[art:d7dbe8ff:challenger.delta_auc]].
The value of `condition_number` is 1023 [[art:36c154df:condition_number]].
The value of `metrics.test.auc` is 0.7505 [[art:3bbb3e37:metrics.test.auc]].
The value of `sign_check.bill_mean_6m.agrees` is 0 [[art:4df8b747:sign_check.bill_mean_6m.agrees]].
The value of `sign_check.bill_mean_6m.coef_sign` is 1 [[art:a457c04a:sign_check.bill_mean_6m.coef_sign]].
The value of `sign_check.bill_mean_6m.univariate_direction` is -1 [[art:23b89c5d:sign_check.bill_mean_6m.univariate_direction]].
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
The value of `threshold.M1.condition_number` is 30 [[art:7e52fd7a:threshold.M1.condition_number]].
The value of `threshold.M1.vif` is 10 [[art:aeb4f33c:threshold.M1.vif]].
The value of `vif.bill_last` is 121600 [[art:9139aeac:vif.bill_last]].
The value of `vif.bill_last_adj` is 121900 [[art:5216ecf3:vif.bill_last_adj]].
The value of `vif.bill_mean_6m` is 175.6 [[art:964ad8e8:vif.bill_mean_6m]].
The value of `vif.max` is 121900 [[art:e6655d27:vif.max]].
The value of `vif.utilisation` is 49.46 [[art:09540d95:vif.utilisation]].
The value of `vif.utilisation_mean_6m` is 50.25 [[art:5233c25b:vif.utilisation_mean_6m]].

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1, S1), `compute_metrics` (T1, C1, O1), `check_leakage` (L1, L2).

### Open items

No open item was recorded for this validation.

## 7. Ongoing monitoring recommendations

This section follows the model risk management guidance at [[reg:SR26-2:V.2]].
The value of `calibration_slope.test` is 0.9988 [[art:6d8bca25:calibration_slope.test]].
The value of `metrics.test.auc` is 0.7505 [[art:3bbb3e37:metrics.test.auc]].
The value of `metrics.test.brier` is 0.1486 [[art:08bbf5ff:metrics.test.brier]].
The value of `psi.max` is 0.01372 [[art:d34e2b0f:psi.max]].
The value of `rule.calibration_first_event_rate` is 0.05 [[art:42f1351e:rule.calibration_first_event_rate]].
The value of `threshold.package.auc.test.min` is 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]].
The value of `threshold.package.brier.test.max` is 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]].
The value of `threshold.package.calibration_slope.test.max` is 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The value of `threshold.package.calibration_slope.test.min` is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].

## Appendix A — Claims

Grounding precision 1.0000 before repair (246 of 246 claims verified) and 1.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 31/31; conceptual_soundness 60/60; data_integrity 46/46; outcomes 57/57; sensitivity 17/17; findings 25/25; monitoring 10/10.

Developer claims: The package declares 2 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). See Appendix D.

Excluded numeric tokens (not claims): citation_hash (6d8bca25, 79d5244e, d7dbe8ff, 36c154df); regulatory_section_id (SR26-2:V.1.b, SR26-2:V.1.a, SR26-2:VI.3, SR26-2:V.2); finding_id (F-001, F-002).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The value of `calibration_slope.test` is 0.9988 . | 0.9988 | ratio | calibration_slope |  | eq | `[[art:6d8bca25:calibration_slope.test]]` | verified | 0.9988191006 |
| 2 | summary | The value of `calibration_slope.train` is 1.005 . | 1.005 | ratio | calibration_slope |  | eq | `[[art:79d5244e:calibration_slope.train]]` | verified | 1.005002582 |
| 3 | summary | The value of `challenger.delta_auc` is 0.07444 . | 0.07444 | ratio | challenger |  | eq | `[[art:d7dbe8ff:challenger.delta_auc]]` | verified | 0.07444422615 |
| 4 | summary | The value of `condition_number` is 1023 . | 1023 | ratio | condition_number |  | eq | `[[art:36c154df:condition_number]]` | verified | 1023.412969 |
| 5 | summary | The value of `csi.max` is 0.0237 . | 0.0237 | ratio | csi |  | eq | `[[art:aa2ba789:csi.max]]` | verified | 0.02369768527 |
| 6 | summary | The value of `metrics.test.auc` is 0.7505 . | 0.7505 | ratio | metrics |  | eq | `[[art:3bbb3e37:metrics.test.auc]]` | verified | 0.7504688325 |
| 7 | summary | The value of `metrics.test.brier` is 0.1486 . | 0.1486 | ratio | metrics |  | eq | `[[art:08bbf5ff:metrics.test.brier]]` | verified | 0.1486259309 |
| 8 | summary | The value of `metrics.test.event_rate` is 0.2247 . | 0.2247 | ratio | metrics |  | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 9 | summary | The value of `metrics.test.gini` is 0.5009 . | 0.5009 | ratio | metrics |  | eq | `[[art:1456c955:metrics.test.gini]]` | verified | 0.500937665 |
| 10 | summary | The value of `metrics.test.ks` is 0.4317 . | 0.4317 | ratio | metrics |  | eq | `[[art:414deaff:metrics.test.ks]]` | verified | 0.4316703705 |
| 11 | summary | The value of `metrics.test.logloss` is 0.467 . | 0.467 | ratio | metrics |  | eq | `[[art:dee4fde4:metrics.test.logloss]]` | verified | 0.4669720314 |
| 12 | summary | The value of `metrics.test.mean_predicted` is 0.2215 . | 0.2215 | ratio | metrics |  | eq | `[[art:461086da:metrics.test.mean_predicted]]` | verified | 0.2214797296 |
| 13 | summary | The value of `metrics.test.n` is 1500 . | 1500 | ratio | metrics |  | eq | `[[art:64fcf14d:metrics.test.n]]` | verified | 1500 |
| 14 | summary | The value of `metrics.train.auc` is 0.7607 . | 0.7607 | ratio | metrics |  | eq | `[[art:9b2be514:metrics.train.auc]]` | verified | 0.7607383073 |
| 15 | summary | The value of `metrics.train.brier` is 0.1486 . | 0.1486 | ratio | metrics |  | eq | `[[art:2fe86f99:metrics.train.brier]]` | verified | 0.1486066513 |
| 16 | summary | The value of `metrics.train.event_rate` is 0.2246 . | 0.2246 | ratio | metrics |  | eq | `[[art:133a5ff8:metrics.train.event_rate]]` | verified | 0.2245714286 |
| 17 | summary | The value of `metrics.train.gini` is 0.5215 . | 0.5215 | ratio | metrics |  | eq | `[[art:94b21017:metrics.train.gini]]` | verified | 0.5214766145 |
| 18 | summary | The value of `metrics.train.ks` is 0.4489 . | 0.4489 | ratio | metrics |  | eq | `[[art:a3928b90:metrics.train.ks]]` | verified | 0.4489284663 |
| 19 | summary | The value of `metrics.train.logloss` is 0.464 . | 0.464 | ratio | metrics |  | eq | `[[art:522ccdcf:metrics.train.logloss]]` | verified | 0.4639849916 |
| 20 | summary | The value of `metrics.train.mean_predicted` is 0.2246 . | 0.2246 | ratio | metrics |  | eq | `[[art:4103f0d8:metrics.train.mean_predicted]]` | verified | 0.2245528647 |
| 21 | summary | The value of `metrics.train.n` is 3500 . | 3500 | ratio | metrics |  | eq | `[[art:564683ee:metrics.train.n]]` | verified | 3500 |
| 22 | summary | The value of `profile.test.n` is 1500 . | 1500 | ratio | profile |  | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 23 | summary | The value of `profile.train.n` is 3500 . | 3500 | ratio | profile |  | eq | `[[art:2510d49d:profile.train.n]]` | verified | 3500 |
| 24 | summary | The value of `psi.max` is 0.01372 . | 0.01372 | ratio | psi |  | eq | `[[art:d34e2b0f:psi.max]]` | verified | 0.01371561255 |
| 25 | summary | The value of `runtime.max_seconds` is 300 . | 300 | ratio | runtime |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 26 | summary | The value of `threshold.package.auc.test.min` is 0.7 . | 0.7 | ratio | threshold |  | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 27 | summary | The value of `threshold.package.brier.test.max` is 0.2 . | 0.2 | ratio | threshold |  | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 28 | summary | The value of `threshold.package.calibration_slope.test.max`… | 1.2 | ratio | threshold |  | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 29 | summary | The value of `threshold.package.calibration_slope.test.min`… | 0.8 | ratio | threshold |  | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 30 | summary | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 31 | summary | The value of `vif.max` is 121900 . | 121900 | ratio | vif |  | eq | `[[art:e6655d27:vif.max]]` | verified | 121913.6293 |
| 32 | conceptual_soundness | The value of `ablation.age.delta_auc` is -0.0004261 . | -0.0004261 | ratio | ablation |  | eq | `[[art:4bde085d:ablation.age.delta_auc]]` | verified | -0.0004260954097 |
| 33 | conceptual_soundness | The value of `ablation.baseline_auc` is 0.7505 . | 0.7505 | ratio | ablation |  | eq | `[[art:2166cf12:ablation.baseline_auc]]` | verified | 0.7504688325 |
| 34 | conceptual_soundness | The value of `ablation.bill_last.delta_auc` is 0.0001786 . | 0.0001786 | ratio | ablation |  | eq | `[[art:eea44d10:ablation.bill_last.delta_auc]]` | verified | 0.0001786028663 |
| 35 | conceptual_soundness | The value of `ablation.bill_last_adj.delta_auc` is 0.0000153… | 1.531e-05 | ratio | ablation |  | eq | `[[art:8e9d6dcc:ablation.bill_last_adj.delta_auc]]` | verified | 1.530881711e-05 |
| 36 | conceptual_soundness | The value of `ablation.bill_mean_6m.delta_auc` is -0.0002909… | -0.0002909 | ratio | ablation |  | eq | `[[art:52f6233e:ablation.bill_mean_6m.delta_auc]]` | verified | -0.0002908675252 |
| 37 | conceptual_soundness | The value of `ablation.bill_trend_6m.delta_auc` is 0.0002526… | 0.0002526 | ratio | ablation |  | eq | `[[art:994f00bc:ablation.bill_trend_6m.delta_auc]]` | verified | 0.0002525954824 |
| 38 | conceptual_soundness | The value of `ablation.delinq_count_6m.delta_auc` is 0.00152… | 0.001526 | ratio | ablation |  | eq | `[[art:5da50826:ablation.delinq_count_6m.delta_auc]]` | verified | 0.001525778772 |
| 39 | conceptual_soundness | The value of `ablation.delinq_last.delta_auc` is -0.07782 . | -0.07782 | ratio | ablation |  | eq | `[[art:8eca80c6:ablation.delinq_last.delta_auc]]` | verified | -0.07782492326 |
| 40 | conceptual_soundness | The value of `ablation.delinq_max_6m.delta_auc` is 0.0003572… | 0.0003572 | ratio | ablation |  | eq | `[[art:16dcea2b:ablation.delinq_max_6m.delta_auc]]` | verified | 0.0003572057326 |
| 41 | conceptual_soundness | The value of `ablation.limit_bal.delta_auc` is 0.0001786 . | 0.0001786 | ratio | ablation |  | eq | `[[art:6bf0f1c3:ablation.limit_bal.delta_auc]]` | verified | 0.0001786028663 |
| 42 | conceptual_soundness | The value of `ablation.pay_ratio_last.delta_auc` is 0.002437… | 0.002437 | ratio | ablation |  | eq | `[[art:9639fcbd:ablation.pay_ratio_last.delta_auc]]` | verified | 0.002436653391 |
| 43 | conceptual_soundness | The value of `ablation.pay_ratio_mean_6m.delta_auc` is 0.007… | 0.007333 | ratio | ablation |  | eq | `[[art:5e7307e8:ablation.pay_ratio_mean_6m.delta_auc]]` | verified | 0.007332923397 |
| 44 | conceptual_soundness | The value of `ablation.utilisation.delta_auc` is -0.0003113… | -0.0003113 | ratio | ablation |  | eq | `[[art:90093ed9:ablation.utilisation.delta_auc]]` | verified | -0.0003112792813 |
| 45 | conceptual_soundness | The value of `ablation.utilisation_mean_6m.delta_auc` is -0.… | -0.0005231 | ratio | ablation |  | eq | `[[art:c63504c6:ablation.utilisation_mean_6m.delta_auc]]` | verified | -0.0005230512514 |
| 46 | conceptual_soundness | The value of `challenger.auc` is 0.8249 . | 0.8249 | ratio | challenger |  | eq | `[[art:9727c6a9:challenger.auc]]` | verified | 0.8249130587 |
| 47 | conceptual_soundness | The value of `challenger.brier` is 0.1242 . | 0.1242 | ratio | challenger |  | eq | `[[art:79d61058:challenger.brier]]` | verified | 0.1241756222 |
| 48 | conceptual_soundness | The value of `challenger.delta_auc` is 0.07444 . | 0.07444 | ratio | challenger |  | eq | `[[art:d7dbe8ff:challenger.delta_auc]]` | verified | 0.07444422615 |
| 49 | conceptual_soundness | The value of `metrics.test.auc` is 0.7505 . | 0.7505 | ratio | metrics |  | eq | `[[art:3bbb3e37:metrics.test.auc]]` | verified | 0.7504688325 |
| 50 | conceptual_soundness | The value of `metrics.test.brier` is 0.1486 . | 0.1486 | ratio | metrics |  | eq | `[[art:08bbf5ff:metrics.test.brier]]` | verified | 0.1486259309 |
| 51 | conceptual_soundness | The value of `sign_check.age.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:4116add1:sign_check.age.agrees]]` | verified | 1 |
| 52 | conceptual_soundness | The value of `sign_check.age.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:6172eb93:sign_check.age.coef_sign]]` | verified | -1 |
| 53 | conceptual_soundness | The value of `sign_check.age.univariate_direction` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:66364583:sign_check.age.univariate_direction]]` | verified | -1 |
| 54 | conceptual_soundness | The value of `sign_check.bill_last.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:98c00451:sign_check.bill_last.agrees]]` | verified | 1 |
| 55 | conceptual_soundness | The value of `sign_check.bill_last.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:4a9f78da:sign_check.bill_last.coef_sign]]` | verified | -1 |
| 56 | conceptual_soundness | The value of `sign_check.bill_last.univariate_direction` is… | -1 | ratio | sign_check |  | eq | `[[art:9e67bc2c:sign_check.bill_last.univariate_direction]]` | verified | -1 |
| 57 | conceptual_soundness | The value of `sign_check.bill_last_adj.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:fb9031bc:sign_check.bill_last_adj.agrees]]` | verified | 1 |
| 58 | conceptual_soundness | The value of `sign_check.bill_last_adj.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:6b02e9dc:sign_check.bill_last_adj.coef_sign]]` | verified | -1 |
| 59 | conceptual_soundness | The value of `sign_check.bill_last_adj.univariate_direction`… | -1 | ratio | sign_check |  | eq | `[[art:cfadf2b7:sign_check.bill_last_adj.univariate_direction]]` | verified | -1 |
| 60 | conceptual_soundness | The value of `sign_check.bill_mean_6m.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:4df8b747:sign_check.bill_mean_6m.agrees]]` | verified | 0 |
| 61 | conceptual_soundness | The value of `sign_check.bill_mean_6m.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:a457c04a:sign_check.bill_mean_6m.coef_sign]]` | verified | 1 |
| 62 | conceptual_soundness | The value of `sign_check.bill_mean_6m.univariate_direction`… | -1 | ratio | sign_check |  | eq | `[[art:23b89c5d:sign_check.bill_mean_6m.univariate_direction]]` | verified | -1 |
| 63 | conceptual_soundness | The value of `sign_check.bill_trend_6m.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:ff3cb24a:sign_check.bill_trend_6m.agrees]]` | verified | 1 |
| 64 | conceptual_soundness | The value of `sign_check.bill_trend_6m.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:7fd8474e:sign_check.bill_trend_6m.coef_sign]]` | verified | -1 |
| 65 | conceptual_soundness | The value of `sign_check.bill_trend_6m.univariate_direction`… | -1 | ratio | sign_check |  | eq | `[[art:a9bff389:sign_check.bill_trend_6m.univariate_direction]]` | verified | -1 |
| 66 | conceptual_soundness | The value of `sign_check.delinq_count_6m.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:a337d16b:sign_check.delinq_count_6m.agrees]]` | verified | 1 |
| 67 | conceptual_soundness | The value of `sign_check.delinq_count_6m.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:17afb6f9:sign_check.delinq_count_6m.coef_sign]]` | verified | 1 |
| 68 | conceptual_soundness | The value of `sign_check.delinq_count_6m.univariate_directio… | 1 | ratio | sign_check |  | eq | `[[art:549e904e:sign_check.delinq_count_6m.univariate_direction]]` | verified | 1 |
| 69 | conceptual_soundness | The value of `sign_check.delinq_last.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:a8ba9372:sign_check.delinq_last.agrees]]` | verified | 1 |
| 70 | conceptual_soundness | The value of `sign_check.delinq_last.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:50d352f8:sign_check.delinq_last.coef_sign]]` | verified | 1 |
| 71 | conceptual_soundness | The value of `sign_check.delinq_last.univariate_direction` i… | 1 | ratio | sign_check |  | eq | `[[art:a78648ba:sign_check.delinq_last.univariate_direction]]` | verified | 1 |
| 72 | conceptual_soundness | The value of `sign_check.delinq_max_6m.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:c946359c:sign_check.delinq_max_6m.agrees]]` | verified | 0 |
| 73 | conceptual_soundness | The value of `sign_check.delinq_max_6m.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]]` | verified | -1 |
| 74 | conceptual_soundness | The value of `sign_check.delinq_max_6m.univariate_direction`… | 1 | ratio | sign_check |  | eq | `[[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]]` | verified | 1 |
| 75 | conceptual_soundness | The value of `sign_check.limit_bal.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:0278aad1:sign_check.limit_bal.agrees]]` | verified | 0 |
| 76 | conceptual_soundness | The value of `sign_check.limit_bal.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:6af6aef2:sign_check.limit_bal.coef_sign]]` | verified | 1 |
| 77 | conceptual_soundness | The value of `sign_check.limit_bal.univariate_direction` is… | -1 | ratio | sign_check |  | eq | `[[art:56d284d6:sign_check.limit_bal.univariate_direction]]` | verified | -1 |
| 78 | conceptual_soundness | The value of `sign_check.n_disagreements` is 4 . | 4 | ratio | sign_check |  | eq | `[[art:b9e93d79:sign_check.n_disagreements]]` | verified | 4 |
| 79 | conceptual_soundness | The value of `sign_check.pay_ratio_last.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:79abee77:sign_check.pay_ratio_last.agrees]]` | verified | 0 |
| 80 | conceptual_soundness | The value of `sign_check.pay_ratio_last.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:f018263e:sign_check.pay_ratio_last.coef_sign]]` | verified | 1 |
| 81 | conceptual_soundness | The value of `sign_check.pay_ratio_last.univariate_direction… | -1 | ratio | sign_check |  | eq | `[[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]]` | verified | -1 |
| 82 | conceptual_soundness | The value of `sign_check.pay_ratio_mean_6m.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:7e9a76ca:sign_check.pay_ratio_mean_6m.agrees]]` | verified | 1 |
| 83 | conceptual_soundness | The value of `sign_check.pay_ratio_mean_6m.coef_sign` is -1… | -1 | ratio | sign_check |  | eq | `[[art:077bb6b2:sign_check.pay_ratio_mean_6m.coef_sign]]` | verified | -1 |
| 84 | conceptual_soundness | The value of `sign_check.pay_ratio_mean_6m.univariate_direct… | -1 | ratio | sign_check |  | eq | `[[art:24dcef24:sign_check.pay_ratio_mean_6m.univariate_direction]]` | verified | -1 |
| 85 | conceptual_soundness | The value of `sign_check.utilisation.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:d0c9a130:sign_check.utilisation.agrees]]` | verified | 1 |
| 86 | conceptual_soundness | The value of `sign_check.utilisation.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:85badc3c:sign_check.utilisation.coef_sign]]` | verified | 1 |
| 87 | conceptual_soundness | The value of `sign_check.utilisation.univariate_direction` i… | 1 | ratio | sign_check |  | eq | `[[art:f0995196:sign_check.utilisation.univariate_direction]]` | verified | 1 |
| 88 | conceptual_soundness | The value of `sign_check.utilisation_mean_6m.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:c2848161:sign_check.utilisation_mean_6m.agrees]]` | verified | 1 |
| 89 | conceptual_soundness | The value of `sign_check.utilisation_mean_6m.coef_sign` is 1… | 1 | ratio | sign_check |  | eq | `[[art:cf902b59:sign_check.utilisation_mean_6m.coef_sign]]` | verified | 1 |
| 90 | conceptual_soundness | The value of `sign_check.utilisation_mean_6m.univariate_dire… | 1 | ratio | sign_check |  | eq | `[[art:35612306:sign_check.utilisation_mean_6m.univariate_direction]]` | verified | 1 |
| 91 | conceptual_soundness | The value of `threshold.E1.delta_auc` is 0.03 . | 0.03 | ratio | threshold |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 92 | data_integrity | The value of `csi.age` is 0.0009462 . | 0.0009462 | ratio | csi |  | eq | `[[art:a1e9712b:csi.age]]` | verified | 0.0009461826658 |
| 93 | data_integrity | The value of `csi.bill_last` is 0.00755 . | 0.00755 | ratio | csi |  | eq | `[[art:609757f9:csi.bill_last]]` | verified | 0.007550351324 |
| 94 | data_integrity | The value of `csi.bill_last_adj` is 0.007981 . | 0.007981 | ratio | csi |  | eq | `[[art:3945402b:csi.bill_last_adj]]` | verified | 0.007981166323 |
| 95 | data_integrity | The value of `csi.bill_mean_6m` is 0.004327 . | 0.004327 | ratio | csi |  | eq | `[[art:a221465d:csi.bill_mean_6m]]` | verified | 0.004326645937 |
| 96 | data_integrity | The value of `csi.bill_trend_6m` is 0.0006834 . | 0.0006834 | ratio | csi |  | eq | `[[art:c7ef6238:csi.bill_trend_6m]]` | verified | 0.000683370174 |
| 97 | data_integrity | The value of `csi.delinq_count_6m` is 0.002436 . | 0.002436 | ratio | csi |  | eq | `[[art:4bcd65c1:csi.delinq_count_6m]]` | verified | 0.00243601263 |
| 98 | data_integrity | The value of `csi.delinq_last` is 0.0237 . | 0.0237 | ratio | csi |  | eq | `[[art:471433c6:csi.delinq_last]]` | verified | 0.02369768527 |
| 99 | data_integrity | The value of `csi.delinq_max_6m` is 0.0008971 . | 0.0008971 | ratio | csi |  | eq | `[[art:0cd543bd:csi.delinq_max_6m]]` | verified | 0.0008970973047 |
| 100 | data_integrity | The value of `csi.limit_bal` is 0.001916 . | 0.001916 | ratio | csi |  | eq | `[[art:d25f5a77:csi.limit_bal]]` | verified | 0.001915717336 |
| 101 | data_integrity | The value of `csi.max` is 0.0237 . | 0.0237 | ratio | csi |  | eq | `[[art:aa2ba789:csi.max]]` | verified | 0.02369768527 |
| 102 | data_integrity | The value of `csi.pay_ratio_last` is 0.00205 . | 0.00205 | ratio | csi |  | eq | `[[art:4461bc3a:csi.pay_ratio_last]]` | verified | 0.002050246889 |
| 103 | data_integrity | The value of `csi.pay_ratio_mean_6m` is 0.001802 . | 0.001802 | ratio | csi |  | eq | `[[art:dc5c1bb6:csi.pay_ratio_mean_6m]]` | verified | 0.001801777591 |
| 104 | data_integrity | The value of `csi.utilisation` is 0.00249 . | 0.00249 | ratio | csi |  | eq | `[[art:b5e8df76:csi.utilisation]]` | verified | 0.002490106313 |
| 105 | data_integrity | The value of `csi.utilisation_mean_6m` is 0.00214 . | 0.00214 | ratio | csi |  | eq | `[[art:71b78094:csi.utilisation_mean_6m]]` | verified | 0.002140004407 |
| 106 | data_integrity | The value of `leakage.duplicates.train` is 0 . | 0 | ratio | leakage |  | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 107 | data_integrity | The value of `leakage.name_screen.n_matched` is 0 . | 0 | ratio | leakage |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 108 | data_integrity | The value of `leakage.overlap` is 0 . | 0 | ratio | leakage |  | eq | `[[art:4c9fcd09:leakage.overlap]]` | verified | 0 |
| 109 | data_integrity | The value of `leakage.overlap.features` is 0 . | 0 | ratio | leakage |  | eq | `[[art:0fec8048:leakage.overlap.features]]` | verified | 0 |
| 110 | data_integrity | The value of `leakage.overlap.ids` is 0 . | 0 | ratio | leakage |  | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 111 | data_integrity | The value of `leakage.target_corr.max_single_feature_auc` is… | 0.6831 | ratio | leakage |  | eq | `[[art:fd829fc4:leakage.target_corr.max_single_feature_auc]]` | verified | 0.6831414154 |
| 112 | data_integrity | The value of `leakage.timing.n_flagged` is 0 . | 0 | ratio | leakage |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 113 | data_integrity | The value of `profile.test.missing.max` is 0 . | 0 | ratio | profile |  | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 114 | data_integrity | The value of `profile.test.n` is 1500 . | 1500 | ratio | profile |  | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 115 | data_integrity | The value of `profile.train.missing.max` is 0 . | 0 | ratio | profile |  | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 116 | data_integrity | The value of `profile.train.n` is 3500 . | 3500 | ratio | profile |  | eq | `[[art:2510d49d:profile.train.n]]` | verified | 3500 |
| 117 | data_integrity | The value of `psi.age` is 0.008124 . | 0.008124 | ratio | psi |  | eq | `[[art:f9255a0a:psi.age]]` | verified | 0.008124281436 |
| 118 | data_integrity | The value of `psi.bill_last` is 0.01302 . | 0.01302 | ratio | psi |  | eq | `[[art:cd0c79c3:psi.bill_last]]` | verified | 0.01302192576 |
| 119 | data_integrity | The value of `psi.bill_last_adj` is 0.01372 . | 0.01372 | ratio | psi |  | eq | `[[art:e87eb6d6:psi.bill_last_adj]]` | verified | 0.01371561255 |
| 120 | data_integrity | The value of `psi.bill_mean_6m` is 0.007124 . | 0.007124 | ratio | psi |  | eq | `[[art:028e4281:psi.bill_mean_6m]]` | verified | 0.007124196275 |
| 121 | data_integrity | The value of `psi.bill_trend_6m` is 0.00958 . | 0.00958 | ratio | psi |  | eq | `[[art:c247a6f2:psi.bill_trend_6m]]` | verified | 0.009579614525 |
| 122 | data_integrity | The value of `psi.delinq_count_6m` is 0.002069 . | 0.002069 | ratio | psi |  | eq | `[[art:61491d02:psi.delinq_count_6m]]` | verified | 0.002069275496 |
| 123 | data_integrity | The value of `psi.delinq_last` is 0.00285 . | 0.00285 | ratio | psi |  | eq | `[[art:03bd52e7:psi.delinq_last]]` | verified | 0.002849633848 |
| 124 | data_integrity | The value of `psi.delinq_max_6m` is 0.005498 . | 0.005498 | ratio | psi |  | eq | `[[art:7a82e7f3:psi.delinq_max_6m]]` | verified | 0.005498249408 |
| 125 | data_integrity | The value of `psi.limit_bal` is 0.01095 . | 0.01095 | ratio | psi |  | eq | `[[art:601cdba2:psi.limit_bal]]` | verified | 0.01095273358 |
| 126 | data_integrity | The value of `psi.max` is 0.01372 . | 0.01372 | ratio | psi |  | eq | `[[art:d34e2b0f:psi.max]]` | verified | 0.01371561255 |
| 127 | data_integrity | The value of `psi.pay_ratio_last` is 0.004966 . | 0.004966 | ratio | psi |  | eq | `[[art:3af2ca29:psi.pay_ratio_last]]` | verified | 0.00496591109 |
| 128 | data_integrity | The value of `psi.pay_ratio_mean_6m` is 0.0055 . | 0.0055 | ratio | psi |  | eq | `[[art:2c5baeb2:psi.pay_ratio_mean_6m]]` | verified | 0.005500252946 |
| 129 | data_integrity | The value of `psi.utilisation` is 0.004244 . | 0.004244 | ratio | psi |  | eq | `[[art:451e0780:psi.utilisation]]` | verified | 0.0042440485 |
| 130 | data_integrity | The value of `psi.utilisation_mean_6m` is 0.002875 . | 0.002875 | ratio | psi |  | eq | `[[art:d562032d:psi.utilisation_mean_6m]]` | verified | 0.002874891089 |
| 131 | data_integrity | The value of `psi.y_score` is 0.004589 . | 0.004589 | ratio | psi |  | eq | `[[art:8d23655e:psi.y_score]]` | verified | 0.004589417025 |
| 132 | data_integrity | The value of `threshold.D1.missing_gap` is 0.1 . | 0.1 | ratio | threshold |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 133 | data_integrity | The value of `threshold.L1.single_feature_auc` is 0.9 . | 0.9 | ratio | threshold |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 134 | data_integrity | The value of `threshold.L2.overlap` is 0.005 . | 0.005 | ratio | threshold |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 135 | data_integrity | The value of `threshold.L2.overlap.features_effective` is 0.… | 0.005 | ratio | threshold |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 136 | data_integrity | The value of `threshold.S1.psi` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 137 | data_integrity | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 138 | outcomes | The value of `calibration.mean_rel_gap.test` is 0.01419 . | 0.01419 | ratio | calibration |  | eq | `[[art:22eeaff2:calibration.mean_rel_gap.test]]` | verified | 0.01418517963 |
| 139 | outcomes | The value of `calibration.mean_rel_gap.train` is 0.00008266… | 8.266e-05 | ratio | calibration |  | eq | `[[art:ca4e4c16:calibration.mean_rel_gap.train]]` | verified | 8.26634452e-05 |
| 140 | outcomes | The value of `calibration_intercept.test` is 0.02018 . | 0.02018 | ratio | calibration_intercept |  | eq | `[[art:a813ed8b:calibration_intercept.test]]` | verified | 0.02018153799 |
| 141 | outcomes | The value of `calibration_intercept.train` is 0.005847 . | 0.005847 | ratio | calibration_intercept |  | eq | `[[art:79bab09a:calibration_intercept.train]]` | verified | 0.005846934312 |
| 142 | outcomes | The value of `calibration_slope.test` is 0.9988 . | 0.9988 | ratio | calibration_slope |  | eq | `[[art:6d8bca25:calibration_slope.test]]` | verified | 0.9988191006 |
| 143 | outcomes | The value of `calibration_slope.train` is 1.005 . | 1.005 | ratio | calibration_slope |  | eq | `[[art:79d5244e:calibration_slope.train]]` | verified | 1.005002582 |
| 144 | outcomes | The value of `deciles.test.top2_capture` is 0.4659 . | 0.4659 | ratio | deciles |  | eq | `[[art:b4ba6281:deciles.test.top2_capture]]` | verified | 0.4658753709 |
| 145 | outcomes | The value of `deciles.train.top2_capture` is 0.4504 . | 0.4504 | ratio | deciles |  | eq | `[[art:250e62bc:deciles.train.top2_capture]]` | verified | 0.4503816794 |
| 146 | outcomes | The value of `metrics.test.auc` is 0.7505 . | 0.7505 | ratio | metrics |  | eq | `[[art:3bbb3e37:metrics.test.auc]]` | verified | 0.7504688325 |
| 147 | outcomes | The value of `metrics.test.brier` is 0.1486 . | 0.1486 | ratio | metrics |  | eq | `[[art:08bbf5ff:metrics.test.brier]]` | verified | 0.1486259309 |
| 148 | outcomes | The value of `metrics.test.event_rate` is 0.2247 . | 0.2247 | ratio | metrics |  | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 149 | outcomes | The value of `metrics.test.gini` is 0.5009 . | 0.5009 | ratio | metrics |  | eq | `[[art:1456c955:metrics.test.gini]]` | verified | 0.500937665 |
| 150 | outcomes | The value of `metrics.test.ks` is 0.4317 . | 0.4317 | ratio | metrics |  | eq | `[[art:414deaff:metrics.test.ks]]` | verified | 0.4316703705 |
| 151 | outcomes | The value of `metrics.test.logloss` is 0.467 . | 0.467 | ratio | metrics |  | eq | `[[art:dee4fde4:metrics.test.logloss]]` | verified | 0.4669720314 |
| 152 | outcomes | The value of `metrics.test.mean_predicted` is 0.2215 . | 0.2215 | ratio | metrics |  | eq | `[[art:461086da:metrics.test.mean_predicted]]` | verified | 0.2214797296 |
| 153 | outcomes | The value of `metrics.test.n` is 1500 . | 1500 | ratio | metrics |  | eq | `[[art:64fcf14d:metrics.test.n]]` | verified | 1500 |
| 154 | outcomes | The value of `metrics.train.auc` is 0.7607 . | 0.7607 | ratio | metrics |  | eq | `[[art:9b2be514:metrics.train.auc]]` | verified | 0.7607383073 |
| 155 | outcomes | The value of `metrics.train.brier` is 0.1486 . | 0.1486 | ratio | metrics |  | eq | `[[art:2fe86f99:metrics.train.brier]]` | verified | 0.1486066513 |
| 156 | outcomes | The value of `metrics.train.event_rate` is 0.2246 . | 0.2246 | ratio | metrics |  | eq | `[[art:133a5ff8:metrics.train.event_rate]]` | verified | 0.2245714286 |
| 157 | outcomes | The value of `metrics.train.gini` is 0.5215 . | 0.5215 | ratio | metrics |  | eq | `[[art:94b21017:metrics.train.gini]]` | verified | 0.5214766145 |
| 158 | outcomes | The value of `metrics.train.ks` is 0.4489 . | 0.4489 | ratio | metrics |  | eq | `[[art:a3928b90:metrics.train.ks]]` | verified | 0.4489284663 |
| 159 | outcomes | The value of `metrics.train.logloss` is 0.464 . | 0.464 | ratio | metrics |  | eq | `[[art:522ccdcf:metrics.train.logloss]]` | verified | 0.4639849916 |
| 160 | outcomes | The value of `metrics.train.mean_predicted` is 0.2246 . | 0.2246 | ratio | metrics |  | eq | `[[art:4103f0d8:metrics.train.mean_predicted]]` | verified | 0.2245528647 |
| 161 | outcomes | The value of `metrics.train.n` is 3500 . | 3500 | ratio | metrics |  | eq | `[[art:564683ee:metrics.train.n]]` | verified | 3500 |
| 162 | outcomes | The value of `psi.age` is 0.008124 . | 0.008124 | ratio | psi |  | eq | `[[art:f9255a0a:psi.age]]` | verified | 0.008124281436 |
| 163 | outcomes | The value of `psi.bill_last` is 0.01302 . | 0.01302 | ratio | psi |  | eq | `[[art:cd0c79c3:psi.bill_last]]` | verified | 0.01302192576 |
| 164 | outcomes | The value of `psi.bill_last_adj` is 0.01372 . | 0.01372 | ratio | psi |  | eq | `[[art:e87eb6d6:psi.bill_last_adj]]` | verified | 0.01371561255 |
| 165 | outcomes | The value of `psi.bill_mean_6m` is 0.007124 . | 0.007124 | ratio | psi |  | eq | `[[art:028e4281:psi.bill_mean_6m]]` | verified | 0.007124196275 |
| 166 | outcomes | The value of `psi.bill_trend_6m` is 0.00958 . | 0.00958 | ratio | psi |  | eq | `[[art:c247a6f2:psi.bill_trend_6m]]` | verified | 0.009579614525 |
| 167 | outcomes | The value of `psi.delinq_count_6m` is 0.002069 . | 0.002069 | ratio | psi |  | eq | `[[art:61491d02:psi.delinq_count_6m]]` | verified | 0.002069275496 |
| 168 | outcomes | The value of `psi.delinq_last` is 0.00285 . | 0.00285 | ratio | psi |  | eq | `[[art:03bd52e7:psi.delinq_last]]` | verified | 0.002849633848 |
| 169 | outcomes | The value of `psi.delinq_max_6m` is 0.005498 . | 0.005498 | ratio | psi |  | eq | `[[art:7a82e7f3:psi.delinq_max_6m]]` | verified | 0.005498249408 |
| 170 | outcomes | The value of `psi.limit_bal` is 0.01095 . | 0.01095 | ratio | psi |  | eq | `[[art:601cdba2:psi.limit_bal]]` | verified | 0.01095273358 |
| 171 | outcomes | The value of `psi.max` is 0.01372 . | 0.01372 | ratio | psi |  | eq | `[[art:d34e2b0f:psi.max]]` | verified | 0.01371561255 |
| 172 | outcomes | The value of `psi.pay_ratio_last` is 0.004966 . | 0.004966 | ratio | psi |  | eq | `[[art:3af2ca29:psi.pay_ratio_last]]` | verified | 0.00496591109 |
| 173 | outcomes | The value of `psi.pay_ratio_mean_6m` is 0.0055 . | 0.0055 | ratio | psi |  | eq | `[[art:2c5baeb2:psi.pay_ratio_mean_6m]]` | verified | 0.005500252946 |
| 174 | outcomes | The value of `psi.utilisation` is 0.004244 . | 0.004244 | ratio | psi |  | eq | `[[art:451e0780:psi.utilisation]]` | verified | 0.0042440485 |
| 175 | outcomes | The value of `psi.utilisation_mean_6m` is 0.002875 . | 0.002875 | ratio | psi |  | eq | `[[art:d562032d:psi.utilisation_mean_6m]]` | verified | 0.002874891089 |
| 176 | outcomes | The value of `psi.y_score` is 0.004589 . | 0.004589 | ratio | psi |  | eq | `[[art:8d23655e:psi.y_score]]` | verified | 0.004589417025 |
| 177 | outcomes | The value of `rule.calibration_first_event_rate` is 0.05 . | 0.05 | ratio | rule |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 178 | outcomes | The value of `threshold.C1.calibration_slope.max` is 1.2 . | 1.2 | ratio | threshold |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 179 | outcomes | The value of `threshold.C1.calibration_slope.min` is 0.8 . | 0.8 | ratio | threshold |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 180 | outcomes | The value of `threshold.C1.mean_ratio_rel` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 181 | outcomes | The value of `threshold.D1.missing_gap` is 0.1 . | 0.1 | ratio | threshold |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 182 | outcomes | The value of `threshold.E1.delta_auc` is 0.03 . | 0.03 | ratio | threshold |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 183 | outcomes | The value of `threshold.L1.single_feature_auc` is 0.9 . | 0.9 | ratio | threshold |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 184 | outcomes | The value of `threshold.L2.overlap` is 0.005 . | 0.005 | ratio | threshold |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 185 | outcomes | The value of `threshold.L2.overlap.features_effective` is 0.… | 0.005 | ratio | threshold |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 186 | outcomes | The value of `threshold.M1.condition_number` is 30 . | 30 | ratio | threshold |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 187 | outcomes | The value of `threshold.M1.vif` is 10 . | 10 | ratio | threshold |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 188 | outcomes | The value of `threshold.O1.auc_gap` is 0.08 . | 0.08 | ratio | threshold |  | eq | `[[art:630f28f4:threshold.O1.auc_gap]]` | verified | 0.08 |
| 189 | outcomes | The value of `threshold.S1.psi` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 190 | outcomes | The value of `threshold.package.auc.test.min` is 0.7 . | 0.7 | ratio | threshold |  | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 191 | outcomes | The value of `threshold.package.brier.test.max` is 0.2 . | 0.2 | ratio | threshold |  | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 192 | outcomes | The value of `threshold.package.calibration_slope.test.max`… | 1.2 | ratio | threshold |  | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 193 | outcomes | The value of `threshold.package.calibration_slope.test.min`… | 0.8 | ratio | threshold |  | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 194 | outcomes | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 195 | sensitivity | The value of `condition_number` is 1023 . | 1023 | ratio | condition_number |  | eq | `[[art:36c154df:condition_number]]` | verified | 1023.412969 |
| 196 | sensitivity | The value of `threshold.M1.condition_number` is 30 . | 30 | ratio | threshold |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 197 | sensitivity | The value of `threshold.M1.vif` is 10 . | 10 | ratio | threshold |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 198 | sensitivity | The value of `vif.age` is 1.002 . | 1.002 | ratio | vif |  | eq | `[[art:c4867fa9:vif.age]]` | verified | 1.001693015 |
| 199 | sensitivity | The value of `vif.bill_last` is 121600 . | 121600 | ratio | vif |  | eq | `[[art:9139aeac:vif.bill_last]]` | verified | 121617.0493 |
| 200 | sensitivity | The value of `vif.bill_last_adj` is 121900 . | 121900 | ratio | vif |  | eq | `[[art:5216ecf3:vif.bill_last_adj]]` | verified | 121913.6293 |
| 201 | sensitivity | The value of `vif.bill_mean_6m` is 175.6 . | 175.6 | ratio | vif |  | eq | `[[art:964ad8e8:vif.bill_mean_6m]]` | verified | 175.5853575 |
| 202 | sensitivity | The value of `vif.bill_trend_6m` is 5.551 . | 5.551 | ratio | vif |  | eq | `[[art:2d1864b3:vif.bill_trend_6m]]` | verified | 5.551420006 |
| 203 | sensitivity | The value of `vif.delinq_count_6m` is 2.562 . | 2.562 | ratio | vif |  | eq | `[[art:0e627a7d:vif.delinq_count_6m]]` | verified | 2.561994785 |
| 204 | sensitivity | The value of `vif.delinq_last` is 1.411 . | 1.411 | ratio | vif |  | eq | `[[art:5fce8331:vif.delinq_last]]` | verified | 1.411351267 |
| 205 | sensitivity | The value of `vif.delinq_max_6m` is 2.409 . | 2.409 | ratio | vif |  | eq | `[[art:c31719bd:vif.delinq_max_6m]]` | verified | 2.408601442 |
| 206 | sensitivity | The value of `vif.limit_bal` is 4.845 . | 4.845 | ratio | vif |  | eq | `[[art:ffa16c31:vif.limit_bal]]` | verified | 4.844965888 |
| 207 | sensitivity | The value of `vif.max` is 121900 . | 121900 | ratio | vif |  | eq | `[[art:e6655d27:vif.max]]` | verified | 121913.6293 |
| 208 | sensitivity | The value of `vif.pay_ratio_last` is 7.269 . | 7.269 | ratio | vif |  | eq | `[[art:6fb2f509:vif.pay_ratio_last]]` | verified | 7.268502144 |
| 209 | sensitivity | The value of `vif.pay_ratio_mean_6m` is 7.261 . | 7.261 | ratio | vif |  | eq | `[[art:76c577a1:vif.pay_ratio_mean_6m]]` | verified | 7.261019162 |
| 210 | sensitivity | The value of `vif.utilisation` is 49.46 . | 49.46 | ratio | vif |  | eq | `[[art:09540d95:vif.utilisation]]` | verified | 49.45982893 |
| 211 | sensitivity | The value of `vif.utilisation_mean_6m` is 50.25 . | 50.25 | ratio | vif |  | eq | `[[art:5233c25b:vif.utilisation_mean_6m]]` | verified | 50.24869902 |
| 212 | findings | The value of `challenger.auc` is 0.8249 . | 0.8249 | ratio | challenger |  | eq | `[[art:9727c6a9:challenger.auc]]` | verified | 0.8249130587 |
| 213 | findings | The value of `challenger.delta_auc` is 0.07444 . | 0.07444 | ratio | challenger |  | eq | `[[art:d7dbe8ff:challenger.delta_auc]]` | verified | 0.07444422615 |
| 214 | findings | The value of `condition_number` is 1023 . | 1023 | ratio | condition_number |  | eq | `[[art:36c154df:condition_number]]` | verified | 1023.412969 |
| 215 | findings | The value of `metrics.test.auc` is 0.7505 . | 0.7505 | ratio | metrics |  | eq | `[[art:3bbb3e37:metrics.test.auc]]` | verified | 0.7504688325 |
| 216 | findings | The value of `sign_check.bill_mean_6m.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:4df8b747:sign_check.bill_mean_6m.agrees]]` | verified | 0 |
| 217 | findings | The value of `sign_check.bill_mean_6m.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:a457c04a:sign_check.bill_mean_6m.coef_sign]]` | verified | 1 |
| 218 | findings | The value of `sign_check.bill_mean_6m.univariate_direction`… | -1 | ratio | sign_check |  | eq | `[[art:23b89c5d:sign_check.bill_mean_6m.univariate_direction]]` | verified | -1 |
| 219 | findings | The value of `sign_check.delinq_max_6m.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:c946359c:sign_check.delinq_max_6m.agrees]]` | verified | 0 |
| 220 | findings | The value of `sign_check.delinq_max_6m.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]]` | verified | -1 |
| 221 | findings | The value of `sign_check.delinq_max_6m.univariate_direction`… | 1 | ratio | sign_check |  | eq | `[[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]]` | verified | 1 |
| 222 | findings | The value of `sign_check.limit_bal.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:0278aad1:sign_check.limit_bal.agrees]]` | verified | 0 |
| 223 | findings | The value of `sign_check.limit_bal.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:6af6aef2:sign_check.limit_bal.coef_sign]]` | verified | 1 |
| 224 | findings | The value of `sign_check.limit_bal.univariate_direction` is… | -1 | ratio | sign_check |  | eq | `[[art:56d284d6:sign_check.limit_bal.univariate_direction]]` | verified | -1 |
| 225 | findings | The value of `sign_check.pay_ratio_last.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:79abee77:sign_check.pay_ratio_last.agrees]]` | verified | 0 |
| 226 | findings | The value of `sign_check.pay_ratio_last.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:f018263e:sign_check.pay_ratio_last.coef_sign]]` | verified | 1 |
| 227 | findings | The value of `sign_check.pay_ratio_last.univariate_direction… | -1 | ratio | sign_check |  | eq | `[[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]]` | verified | -1 |
| 228 | findings | The value of `threshold.E1.delta_auc` is 0.03 . | 0.03 | ratio | threshold |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 229 | findings | The value of `threshold.M1.condition_number` is 30 . | 30 | ratio | threshold |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 230 | findings | The value of `threshold.M1.vif` is 10 . | 10 | ratio | threshold |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 231 | findings | The value of `vif.bill_last` is 121600 . | 121600 | ratio | vif |  | eq | `[[art:9139aeac:vif.bill_last]]` | verified | 121617.0493 |
| 232 | findings | The value of `vif.bill_last_adj` is 121900 . | 121900 | ratio | vif |  | eq | `[[art:5216ecf3:vif.bill_last_adj]]` | verified | 121913.6293 |
| 233 | findings | The value of `vif.bill_mean_6m` is 175.6 . | 175.6 | ratio | vif |  | eq | `[[art:964ad8e8:vif.bill_mean_6m]]` | verified | 175.5853575 |
| 234 | findings | The value of `vif.max` is 121900 . | 121900 | ratio | vif |  | eq | `[[art:e6655d27:vif.max]]` | verified | 121913.6293 |
| 235 | findings | The value of `vif.utilisation` is 49.46 . | 49.46 | ratio | vif |  | eq | `[[art:09540d95:vif.utilisation]]` | verified | 49.45982893 |
| 236 | findings | The value of `vif.utilisation_mean_6m` is 50.25 . | 50.25 | ratio | vif |  | eq | `[[art:5233c25b:vif.utilisation_mean_6m]]` | verified | 50.24869902 |
| 237 | monitoring | The value of `calibration_slope.test` is 0.9988 . | 0.9988 | ratio | calibration_slope |  | eq | `[[art:6d8bca25:calibration_slope.test]]` | verified | 0.9988191006 |
| 238 | monitoring | The value of `metrics.test.auc` is 0.7505 . | 0.7505 | ratio | metrics |  | eq | `[[art:3bbb3e37:metrics.test.auc]]` | verified | 0.7504688325 |
| 239 | monitoring | The value of `metrics.test.brier` is 0.1486 . | 0.1486 | ratio | metrics |  | eq | `[[art:08bbf5ff:metrics.test.brier]]` | verified | 0.1486259309 |
| 240 | monitoring | The value of `psi.max` is 0.01372 . | 0.01372 | ratio | psi |  | eq | `[[art:d34e2b0f:psi.max]]` | verified | 0.01371561255 |
| 241 | monitoring | The value of `rule.calibration_first_event_rate` is 0.05 . | 0.05 | ratio | rule |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 242 | monitoring | The value of `threshold.package.auc.test.min` is 0.7 . | 0.7 | ratio | threshold |  | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 243 | monitoring | The value of `threshold.package.brier.test.max` is 0.2 . | 0.2 | ratio | threshold |  | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 244 | monitoring | The value of `threshold.package.calibration_slope.test.max`… | 1.2 | ratio | threshold |  | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 245 | monitoring | The value of `threshold.package.calibration_slope.test.min`… | 0.8 | ratio | threshold |  | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 246 | monitoring | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |

## Appendix B — Artifact index

The store holds 189 artifacts; the 158 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `ablation.age.delta_auc` | `4bde085d` | scalar | -0.0004260954097 | change in test AUC when the champion's form is refitted without age |
| `ablation.baseline_auc` | `2166cf12` | scalar | 0.7504688325 | AUC on test of a refit of the champion's functional form on every retained feature, the level each ablation delta is measured from |
| `ablation.bill_last.delta_auc` | `eea44d10` | scalar | 0.0001786028663 | change in test AUC when the champion's form is refitted without bill_last |
| `ablation.bill_last_adj.delta_auc` | `8e9d6dcc` | scalar | 1.530881711e-05 | change in test AUC when the champion's form is refitted without bill_last_adj |
| `ablation.bill_mean_6m.delta_auc` | `52f6233e` | scalar | -0.0002908675252 | change in test AUC when the champion's form is refitted without bill_mean_6m |
| `ablation.bill_trend_6m.delta_auc` | `994f00bc` | scalar | 0.0002525954824 | change in test AUC when the champion's form is refitted without bill_trend_6m |
| `ablation.delinq_count_6m.delta_auc` | `5da50826` | scalar | 0.001525778772 | change in test AUC when the champion's form is refitted without delinq_count_6m |
| `ablation.delinq_last.delta_auc` | `8eca80c6` | scalar | -0.07782492326 | change in test AUC when the champion's form is refitted without delinq_last |
| `ablation.delinq_max_6m.delta_auc` | `16dcea2b` | scalar | 0.0003572057326 | change in test AUC when the champion's form is refitted without delinq_max_6m |
| `ablation.limit_bal.delta_auc` | `6bf0f1c3` | scalar | 0.0001786028663 | change in test AUC when the champion's form is refitted without limit_bal |
| `ablation.pay_ratio_last.delta_auc` | `9639fcbd` | scalar | 0.002436653391 | change in test AUC when the champion's form is refitted without pay_ratio_last |
| `ablation.pay_ratio_mean_6m.delta_auc` | `5e7307e8` | scalar | 0.007332923397 | change in test AUC when the champion's form is refitted without pay_ratio_mean_6m |
| `ablation.utilisation.delta_auc` | `90093ed9` | scalar | -0.0003112792813 | change in test AUC when the champion's form is refitted without utilisation |
| `ablation.utilisation_mean_6m.delta_auc` | `c63504c6` | scalar | -0.0005230512514 | change in test AUC when the champion's form is refitted without utilisation_mean_6m |
| `calibration.mean_rel_gap.test` | `22eeaff2` | scalar | 0.01418517963 | mean predicted against observed on test, relative |
| `calibration.mean_rel_gap.train` | `ca4e4c16` | scalar | 8.26634452e-05 | mean predicted against observed on train, relative |
| `calibration.test` | `f4024126` | table | table, 10 rows | calibration by decile of predicted probability on test |
| `calibration_intercept.test` | `a813ed8b` | scalar | 0.02018153799 | logistic regression of the outcome on logit(p) on test: the intercept |
| `calibration_intercept.train` | `79bab09a` | scalar | 0.005846934312 | logistic regression of the outcome on logit(p) on train: the intercept |
| `calibration_slope.test` | `6d8bca25` | scalar | 0.9988191006 | logistic regression of the outcome on logit(p) on test: the slope |
| `calibration_slope.train` | `79d5244e` | scalar | 1.005002582 | logistic regression of the outcome on logit(p) on train: the slope |
| `challenger.auc` | `9727c6a9` | scalar | 0.8249130587 | the challenger's AUC on test |
| `challenger.brier` | `79d61058` | scalar | 0.1241756222 | the challenger's Brier score on test |
| `challenger.delta_auc` | `d7dbe8ff` | scalar | 0.07444422615 | the challenger's AUC on test minus the champion's |
| `condition_number` | `36c154df` | scalar | 1023.412969 | Belsley's condition number of the column-standardised design |
| `csi.age` | `a1e9712b` | scalar | 0.0009461826658 | CSI of age: its contribution to the shift in the linear predictor |
| `csi.bill_last` | `609757f9` | scalar | 0.007550351324 | CSI of bill_last: its contribution to the shift in the linear predictor |
| `csi.bill_last_adj` | `3945402b` | scalar | 0.007981166323 | CSI of bill_last_adj: its contribution to the shift in the linear predictor |
| `csi.bill_mean_6m` | `a221465d` | scalar | 0.004326645937 | CSI of bill_mean_6m: its contribution to the shift in the linear predictor |
| `csi.bill_trend_6m` | `c7ef6238` | scalar | 0.000683370174 | CSI of bill_trend_6m: its contribution to the shift in the linear predictor |
| `csi.delinq_count_6m` | `4bcd65c1` | scalar | 0.00243601263 | CSI of delinq_count_6m: its contribution to the shift in the linear predictor |
| `csi.delinq_last` | `471433c6` | scalar | 0.02369768527 | CSI of delinq_last: its contribution to the shift in the linear predictor |
| `csi.delinq_max_6m` | `0cd543bd` | scalar | 0.0008970973047 | CSI of delinq_max_6m: its contribution to the shift in the linear predictor |
| `csi.limit_bal` | `d25f5a77` | scalar | 0.001915717336 | CSI of limit_bal: its contribution to the shift in the linear predictor |
| `csi.max` | `aa2ba789` | scalar | 0.02369768527 | the largest characteristic stability index |
| `csi.pay_ratio_last` | `4461bc3a` | scalar | 0.002050246889 | CSI of pay_ratio_last: its contribution to the shift in the linear predictor |
| `csi.pay_ratio_mean_6m` | `dc5c1bb6` | scalar | 0.001801777591 | CSI of pay_ratio_mean_6m: its contribution to the shift in the linear predictor |
| `csi.utilisation` | `b5e8df76` | scalar | 0.002490106313 | CSI of utilisation: its contribution to the shift in the linear predictor |
| `csi.utilisation_mean_6m` | `71b78094` | scalar | 0.002140004407 | CSI of utilisation_mean_6m: its contribution to the shift in the linear predictor |
| `deciles.test` | `b1875fbd` | table | table, 10 rows | decile separation on test; decile 1 holds the highest probabilities |
| `deciles.test.top2_capture` | `b4ba6281` | scalar | 0.4658753709 | share of test events in the top two deciles |
| `deciles.train.top2_capture` | `250e62bc` | scalar | 0.4503816794 | share of train events in the top two deciles |
| `leakage.duplicates.train` | `4474c227` | scalar | 0 | share of train rows whose feature values are not unique within train |
| `leakage.name_screen.n_matched` | `407e62be` | scalar | 0 | feature names matching the target-adjacent lexicon |
| `leakage.overlap` | `4c9fcd09` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.features` | `0fec8048` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.ids` | `63d37fc5` | scalar | 0 | share of test rows whose ['client_id'] also identify a row of train |
| `leakage.target_corr.max_single_feature_auc` | `fd829fc4` | scalar | 0.6831414154 | the AUC of the strongest single feature |
| `leakage.timing.n_flagged` | `742bcd24` | scalar | 0 | features declared during_period or after_outcome |
| `metrics.test.auc` | `3bbb3e37` | scalar | 0.7504688325 | auc on test, recomputed by quaestor |
| `metrics.test.brier` | `08bbf5ff` | scalar | 0.1486259309 | brier on test, recomputed by quaestor |
| `metrics.test.event_rate` | `9209d200` | scalar | 0.2246666667 | event_rate on test, recomputed by quaestor |
| `metrics.test.gini` | `1456c955` | scalar | 0.500937665 | gini on test, recomputed by quaestor |
| `metrics.test.ks` | `414deaff` | scalar | 0.4316703705 | ks on test, recomputed by quaestor |
| `metrics.test.logloss` | `dee4fde4` | scalar | 0.4669720314 | logloss on test, recomputed by quaestor |
| `metrics.test.mean_predicted` | `461086da` | scalar | 0.2214797296 | mean_predicted on test, recomputed by quaestor |
| `metrics.test.n` | `64fcf14d` | scalar | 1500 | n on test, recomputed by quaestor |
| `metrics.train.auc` | `9b2be514` | scalar | 0.7607383073 | auc on train, recomputed by quaestor |
| `metrics.train.brier` | `2fe86f99` | scalar | 0.1486066513 | brier on train, recomputed by quaestor |
| `metrics.train.event_rate` | `133a5ff8` | scalar | 0.2245714286 | event_rate on train, recomputed by quaestor |
| `metrics.train.gini` | `94b21017` | scalar | 0.5214766145 | gini on train, recomputed by quaestor |
| `metrics.train.ks` | `a3928b90` | scalar | 0.4489284663 | ks on train, recomputed by quaestor |
| `metrics.train.logloss` | `522ccdcf` | scalar | 0.4639849916 | logloss on train, recomputed by quaestor |
| `metrics.train.mean_predicted` | `4103f0d8` | scalar | 0.2245528647 | mean_predicted on train, recomputed by quaestor |
| `metrics.train.n` | `564683ee` | scalar | 3500 | n on train, recomputed by quaestor |
| `profile.test.missing.max` | `f813848d` | scalar | 0 | the largest missing fraction in test |
| `profile.test.n` | `2193cf5f` | scalar | 1500 | rows in test |
| `profile.train.missing.max` | `050a3099` | scalar | 0 | the largest missing fraction in train |
| `profile.train.n` | `2510d49d` | scalar | 3500 | rows in train |
| `psi.age` | `f9255a0a` | scalar | 0.008124281436 | PSI of age between train and test |
| `psi.bill_last` | `cd0c79c3` | scalar | 0.01302192576 | PSI of bill_last between train and test |
| `psi.bill_last_adj` | `e87eb6d6` | scalar | 0.01371561255 | PSI of bill_last_adj between train and test |
| `psi.bill_mean_6m` | `028e4281` | scalar | 0.007124196275 | PSI of bill_mean_6m between train and test |
| `psi.bill_trend_6m` | `c247a6f2` | scalar | 0.009579614525 | PSI of bill_trend_6m between train and test |
| `psi.delinq_count_6m` | `61491d02` | scalar | 0.002069275496 | PSI of delinq_count_6m between train and test |
| `psi.delinq_last` | `03bd52e7` | scalar | 0.002849633848 | PSI of delinq_last between train and test |
| `psi.delinq_max_6m` | `7a82e7f3` | scalar | 0.005498249408 | PSI of delinq_max_6m between train and test |
| `psi.limit_bal` | `601cdba2` | scalar | 0.01095273358 | PSI of limit_bal between train and test |
| `psi.max` | `d34e2b0f` | scalar | 0.01371561255 | the largest train-to-test PSI, score included |
| `psi.pay_ratio_last` | `3af2ca29` | scalar | 0.00496591109 | PSI of pay_ratio_last between train and test |
| `psi.pay_ratio_mean_6m` | `2c5baeb2` | scalar | 0.005500252946 | PSI of pay_ratio_mean_6m between train and test |
| `psi.utilisation` | `451e0780` | scalar | 0.0042440485 | PSI of utilisation between train and test |
| `psi.utilisation_mean_6m` | `d562032d` | scalar | 0.002874891089 | PSI of utilisation_mean_6m between train and test |
| `psi.y_score` | `8d23655e` | scalar | 0.004589417025 | PSI of the score between train and test |
| `rule.calibration_first_event_rate` | `42f1351e` | scalar | 0.05 | the event rate below which the report puts calibration before discrimination |
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |
| `sign_check.age.agrees` | `4116add1` | scalar | 1 | 1 when the fitted sign on age agrees with its univariate direction, 0 when it does not |
| `sign_check.age.coef_sign` | `6172eb93` | scalar | -1 | the sign of the fitted coefficient on age |
| `sign_check.age.univariate_direction` | `66364583` | scalar | -1 | the sign of age's own single-feature AUC on train minus 0.5 |
| `sign_check.bill_last.agrees` | `98c00451` | scalar | 1 | 1 when the fitted sign on bill_last agrees with its univariate direction, 0 when it does not |
| `sign_check.bill_last.coef_sign` | `4a9f78da` | scalar | -1 | the sign of the fitted coefficient on bill_last |
| `sign_check.bill_last.univariate_direction` | `9e67bc2c` | scalar | -1 | the sign of bill_last's own single-feature AUC on train minus 0.5 |
| `sign_check.bill_last_adj.agrees` | `fb9031bc` | scalar | 1 | 1 when the fitted sign on bill_last_adj agrees with its univariate direction, 0 when it does not |
| `sign_check.bill_last_adj.coef_sign` | `6b02e9dc` | scalar | -1 | the sign of the fitted coefficient on bill_last_adj |
| `sign_check.bill_last_adj.univariate_direction` | `cfadf2b7` | scalar | -1 | the sign of bill_last_adj's own single-feature AUC on train minus 0.5 |
| `sign_check.bill_mean_6m.agrees` | `4df8b747` | scalar | 0 | 1 when the fitted sign on bill_mean_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.bill_mean_6m.coef_sign` | `a457c04a` | scalar | 1 | the sign of the fitted coefficient on bill_mean_6m |
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
| `sign_check.n_disagreements` | `b9e93d79` | scalar | 4 | retained features whose fitted sign contradicts their univariate direction, of 13 checked |
| `sign_check.pay_ratio_last.agrees` | `79abee77` | scalar | 0 | 1 when the fitted sign on pay_ratio_last agrees with its univariate direction, 0 when it does not |
| `sign_check.pay_ratio_last.coef_sign` | `f018263e` | scalar | 1 | the sign of the fitted coefficient on pay_ratio_last |
| `sign_check.pay_ratio_last.univariate_direction` | `f8e46d75` | scalar | -1 | the sign of pay_ratio_last's own single-feature AUC on train minus 0.5 |
| `sign_check.pay_ratio_mean_6m.agrees` | `7e9a76ca` | scalar | 1 | 1 when the fitted sign on pay_ratio_mean_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.pay_ratio_mean_6m.coef_sign` | `077bb6b2` | scalar | -1 | the sign of the fitted coefficient on pay_ratio_mean_6m |
| `sign_check.pay_ratio_mean_6m.univariate_direction` | `24dcef24` | scalar | -1 | the sign of pay_ratio_mean_6m's own single-feature AUC on train minus 0.5 |
| `sign_check.utilisation.agrees` | `d0c9a130` | scalar | 1 | 1 when the fitted sign on utilisation agrees with its univariate direction, 0 when it does not |
| `sign_check.utilisation.coef_sign` | `85badc3c` | scalar | 1 | the sign of the fitted coefficient on utilisation |
| `sign_check.utilisation.univariate_direction` | `f0995196` | scalar | 1 | the sign of utilisation's own single-feature AUC on train minus 0.5 |
| `sign_check.utilisation_mean_6m.agrees` | `c2848161` | scalar | 1 | 1 when the fitted sign on utilisation_mean_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.utilisation_mean_6m.coef_sign` | `cf902b59` | scalar | 1 | the sign of the fitted coefficient on utilisation_mean_6m |
| `sign_check.utilisation_mean_6m.univariate_direction` | `35612306` | scalar | 1 | the sign of utilisation_mean_6m's own single-feature AUC on train minus 0.5 |
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
| `thresholds.evaluation` | `5b16d3a6` | table | table, 5 rows | every threshold package.yaml declares, with its bound, the recomputed value and the outcome |
| `vif.age` | `c4867fa9` | scalar | 1.001693015 | variance inflation factor of age on train |
| `vif.bill_last` | `9139aeac` | scalar | 121617.0493 | variance inflation factor of bill_last on train |
| `vif.bill_last_adj` | `5216ecf3` | scalar | 121913.6293 | variance inflation factor of bill_last_adj on train |
| `vif.bill_mean_6m` | `964ad8e8` | scalar | 175.5853575 | variance inflation factor of bill_mean_6m on train |
| `vif.bill_trend_6m` | `2d1864b3` | scalar | 5.551420006 | variance inflation factor of bill_trend_6m on train |
| `vif.delinq_count_6m` | `0e627a7d` | scalar | 2.561994785 | variance inflation factor of delinq_count_6m on train |
| `vif.delinq_last` | `5fce8331` | scalar | 1.411351267 | variance inflation factor of delinq_last on train |
| `vif.delinq_max_6m` | `c31719bd` | scalar | 2.408601442 | variance inflation factor of delinq_max_6m on train |
| `vif.limit_bal` | `ffa16c31` | scalar | 4.844965888 | variance inflation factor of limit_bal on train |
| `vif.max` | `e6655d27` | scalar | 121913.6293 | the largest variance inflation factor |
| `vif.pay_ratio_last` | `6fb2f509` | scalar | 7.268502144 | variance inflation factor of pay_ratio_last on train |
| `vif.pay_ratio_mean_6m` | `76c577a1` | scalar | 7.261019162 | variance inflation factor of pay_ratio_mean_6m on train |
| `vif.utilisation` | `09540d95` | scalar | 49.45982893 | variance inflation factor of utilisation on train |
| `vif.utilisation_mean_6m` | `5233c25b` | scalar | 50.24869902 | variance inflation factor of utilisation_mean_6m on train |

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
| wall-clock (s) | 1.20 |
| subject run (s) | 1.22 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | fake |
| model | none: no model answered |
| run id | credit_default-rules_only-20260918T065327Z-bd5861e9 |

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
