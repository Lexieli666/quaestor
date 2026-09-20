---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: rules_only
model: fake
run_id: credit_default-rules_only-20260918T065314Z-bd5861e9
data_mode: synthetic
synthetic_n: 5000
grounding_precision_pre: 1.0000
grounding_precision_post: 1.0000
n_claims: 215
n_findings_by_severity: {high: 1, medium: 1, low: 1, info: 0}
generated: "2026-09-18T06:53:14Z"
illustrative: false
---

# Validation report — `credit_default` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `credit_default` v1.0 | `rules_only` | fake | synthetic, n = 5000 | 1.0000 → 1.0000 | 1 / 1 / 1 / 0 |
<!-- quaestor:renderer:end -->

This section follows the model risk management guidance at [[reg:SR26-2:V.1.b]].
The value of `calibration_slope.test` is 0.7952 [[art:b2bc94fc:calibration_slope.test]].
The value of `calibration_slope.train` is 0.7656 [[art:1151c8e4:calibration_slope.train]].
The value of `challenger.delta_auc` is 0.0476 [[art:a86db8b1:challenger.delta_auc]].
The value of `condition_number` is 5.547 [[art:e41b9562:condition_number]].
The value of `csi.max` is 0.03295 [[art:e1f1ad3d:csi.max]].
The value of `metrics.test.auc` is 0.7764 [[art:06c7c666:metrics.test.auc]].
The value of `metrics.test.brier` is 0.1929 [[art:2f64a7ce:metrics.test.brier]].
The value of `metrics.test.event_rate` is 0.2247 [[art:9209d200:metrics.test.event_rate]].
The value of `metrics.test.gini` is 0.5527 [[art:bc939097:metrics.test.gini]].
The value of `metrics.test.ks` is 0.4656 [[art:f4b92d62:metrics.test.ks]].
The value of `metrics.test.logloss` is 0.5935 [[art:6ac37fc1:metrics.test.logloss]].
The value of `metrics.test.mean_predicted` is 0.4379 [[art:aa68c658:metrics.test.mean_predicted]].
The value of `metrics.test.n` is 1500 [[art:64fcf14d:metrics.test.n]].
The value of `metrics.train.auc` is 0.7765 [[art:0e7355aa:metrics.train.auc]].
The value of `metrics.train.brier` is 0.1969 [[art:f118c784:metrics.train.brier]].
The value of `metrics.train.event_rate` is 0.2246 [[art:133a5ff8:metrics.train.event_rate]].
The value of `metrics.train.gini` is 0.553 [[art:1e398595:metrics.train.gini]].
The value of `metrics.train.ks` is 0.4801 [[art:97bd5dab:metrics.train.ks]].
The value of `metrics.train.logloss` is 0.6031 [[art:dcbefb71:metrics.train.logloss]].
The value of `metrics.train.mean_predicted` is 0.4427 [[art:bbe07926:metrics.train.mean_predicted]].
The value of `metrics.train.n` is 3500 [[art:564683ee:metrics.train.n]].
The value of `profile.test.n` is 1500 [[art:2193cf5f:profile.test.n]].
The value of `profile.train.n` is 3500 [[art:2510d49d:profile.train.n]].
The value of `psi.max` is 0.01095 [[art:381b2570:psi.max]].
The value of `runtime.max_seconds` is 300 [[art:2ad8d1a5:runtime.max_seconds]].
The value of `threshold.package.auc.test.min` is 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]].
The value of `threshold.package.brier.test.max` is 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]].
The value of `threshold.package.calibration_slope.test.max` is 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The value of `threshold.package.calibration_slope.test.min` is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
The value of `vif.max` is 7.295 [[art:9ae7c45b:vif.max]].

## 2. Conceptual soundness

This section follows the model risk management guidance at [[reg:SR26-2:V.1.a]].
The value of `ablation.age.delta_auc` is 0.00008675 [[art:59398b1b:ablation.age.delta_auc]].
The value of `ablation.baseline_auc` is 0.748 [[art:3a44e438:ablation.baseline_auc]].
The value of `ablation.bill_mean_6m.delta_auc` is -0.0016 [[art:3b91a889:ablation.bill_mean_6m.delta_auc]].
The value of `ablation.bill_trend_6m.delta_auc` is 0.003279 [[art:096d7f98:ablation.bill_trend_6m.delta_auc]].
The value of `ablation.delinq_count_6m.delta_auc` is 0.0006812 [[art:c5659def:ablation.delinq_count_6m.delta_auc]].
The value of `ablation.delinq_last.delta_auc` is -0.07585 [[art:3150b111:ablation.delinq_last.delta_auc]].
The value of `ablation.delinq_max_6m.delta_auc` is 0.0003598 [[art:3a0d3a0c:ablation.delinq_max_6m.delta_auc]].
The value of `ablation.limit_bal.delta_auc` is 0.0004286 [[art:63faa640:ablation.limit_bal.delta_auc]].
The value of `ablation.pay_ratio_last.delta_auc` is 0.002411 [[art:5f39089e:ablation.pay_ratio_last.delta_auc]].
The value of `ablation.pay_ratio_mean_6m.delta_auc` is 0.006603 [[art:90fa1178:ablation.pay_ratio_mean_6m.delta_auc]].
The value of `ablation.utilisation.delta_auc` is -0.01977 [[art:d4ad2039:ablation.utilisation.delta_auc]].
The value of `challenger.auc` is 0.824 [[art:bf5be719:challenger.auc]].
The value of `challenger.brier` is 0.1258 [[art:f9e0583d:challenger.brier]].
The value of `challenger.delta_auc` is 0.0476 [[art:a86db8b1:challenger.delta_auc]].
The value of `metrics.test.auc` is 0.7764 [[art:06c7c666:metrics.test.auc]].
The value of `metrics.test.brier` is 0.1929 [[art:2f64a7ce:metrics.test.brier]].
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
The value of `sign_check.delinq_max_6m.agrees` is 1 [[art:da92a015:sign_check.delinq_max_6m.agrees]].
The value of `sign_check.delinq_max_6m.coef_sign` is 1 [[art:53560657:sign_check.delinq_max_6m.coef_sign]].
The value of `sign_check.delinq_max_6m.univariate_direction` is 1 [[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]].
The value of `sign_check.limit_bal.agrees` is 0 [[art:0278aad1:sign_check.limit_bal.agrees]].
The value of `sign_check.limit_bal.coef_sign` is 1 [[art:6af6aef2:sign_check.limit_bal.coef_sign]].
The value of `sign_check.limit_bal.univariate_direction` is -1 [[art:56d284d6:sign_check.limit_bal.univariate_direction]].
The value of `sign_check.n_disagreements` is 1 [[art:f96ece96:sign_check.n_disagreements]].
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
The value of `csi.age` is 0.001075 [[art:1642e34e:csi.age]].
The value of `csi.bill_mean_6m` is 0.001757 [[art:278c2a6d:csi.bill_mean_6m]].
The value of `csi.bill_trend_6m` is 0.006203 [[art:2567a75c:csi.bill_trend_6m]].
The value of `csi.delinq_count_6m` is 0.002804 [[art:b0282e56:csi.delinq_count_6m]].
The value of `csi.delinq_last` is 0.03295 [[art:39b31d8e:csi.delinq_last]].
The value of `csi.delinq_max_6m` is 0.0003766 [[art:3fc49a03:csi.delinq_max_6m]].
The value of `csi.limit_bal` is 0.0002712 [[art:bc85c1c5:csi.limit_bal]].
The value of `csi.max` is 0.03295 [[art:e1f1ad3d:csi.max]].
The value of `csi.pay_ratio_last` is 0.001721 [[art:fd186b68:csi.pay_ratio_last]].
The value of `csi.pay_ratio_mean_6m` is 0.0008584 [[art:659995f7:csi.pay_ratio_mean_6m]].
The value of `csi.utilisation` is 0.00724 [[art:0a1f2306:csi.utilisation]].
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
The value of `psi.bill_mean_6m` is 0.007124 [[art:028e4281:psi.bill_mean_6m]].
The value of `psi.bill_trend_6m` is 0.00958 [[art:c247a6f2:psi.bill_trend_6m]].
The value of `psi.delinq_count_6m` is 0.002069 [[art:61491d02:psi.delinq_count_6m]].
The value of `psi.delinq_last` is 0.00285 [[art:03bd52e7:psi.delinq_last]].
The value of `psi.delinq_max_6m` is 0.005498 [[art:7a82e7f3:psi.delinq_max_6m]].
The value of `psi.limit_bal` is 0.01095 [[art:601cdba2:psi.limit_bal]].
The value of `psi.max` is 0.01095 [[art:381b2570:psi.max]].
The value of `psi.pay_ratio_last` is 0.004966 [[art:3af2ca29:psi.pay_ratio_last]].
The value of `psi.pay_ratio_mean_6m` is 0.0055 [[art:2c5baeb2:psi.pay_ratio_mean_6m]].
The value of `psi.utilisation` is 0.004244 [[art:451e0780:psi.utilisation]].
The value of `psi.y_score` is 0.005049 [[art:a8375d0f:psi.y_score]].
The value of `threshold.D1.missing_gap` is 0.1 [[art:9cce25ea:threshold.D1.missing_gap]].
The value of `threshold.L1.single_feature_auc` is 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]].
The value of `threshold.L2.overlap` is 0.005 [[art:9f336eaf:threshold.L2.overlap]].
The value of `threshold.L2.overlap.features_effective` is 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].
The value of `threshold.S1.psi` is 0.25 [[art:278b9016:threshold.S1.psi]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].

## 4. Outcomes analysis

This section follows the model risk management guidance at [[reg:SR26-2:V.1.b]].
The value of `calibration.mean_rel_gap.test` is 0.9491 [[art:376ae2d7:calibration.mean_rel_gap.test]].
The value of `calibration.mean_rel_gap.train` is 0.9715 [[art:0abea673:calibration.mean_rel_gap.train]].
The value of `calibration_intercept.test` is -1.217 [[art:62851316:calibration_intercept.test]].
The value of `calibration_intercept.train` is -1.241 [[art:849b7b2e:calibration_intercept.train]].
The value of `calibration_slope.test` is 0.7952 [[art:b2bc94fc:calibration_slope.test]].
The value of `calibration_slope.train` is 0.7656 [[art:1151c8e4:calibration_slope.train]].
The value of `deciles.test.top2_capture` is 0.4451 [[art:e3b6058b:deciles.test.top2_capture]].
The value of `deciles.train.top2_capture` is 0.4262 [[art:1693b145:deciles.train.top2_capture]].
The value of `metrics.test.auc` is 0.7764 [[art:06c7c666:metrics.test.auc]].
The value of `metrics.test.brier` is 0.1929 [[art:2f64a7ce:metrics.test.brier]].
The value of `metrics.test.event_rate` is 0.2247 [[art:9209d200:metrics.test.event_rate]].
The value of `metrics.test.gini` is 0.5527 [[art:bc939097:metrics.test.gini]].
The value of `metrics.test.ks` is 0.4656 [[art:f4b92d62:metrics.test.ks]].
The value of `metrics.test.logloss` is 0.5935 [[art:6ac37fc1:metrics.test.logloss]].
The value of `metrics.test.mean_predicted` is 0.4379 [[art:aa68c658:metrics.test.mean_predicted]].
The value of `metrics.test.n` is 1500 [[art:64fcf14d:metrics.test.n]].
The value of `metrics.train.auc` is 0.7765 [[art:0e7355aa:metrics.train.auc]].
The value of `metrics.train.brier` is 0.1969 [[art:f118c784:metrics.train.brier]].
The value of `metrics.train.event_rate` is 0.2246 [[art:133a5ff8:metrics.train.event_rate]].
The value of `metrics.train.gini` is 0.553 [[art:1e398595:metrics.train.gini]].
The value of `metrics.train.ks` is 0.4801 [[art:97bd5dab:metrics.train.ks]].
The value of `metrics.train.logloss` is 0.6031 [[art:dcbefb71:metrics.train.logloss]].
The value of `metrics.train.mean_predicted` is 0.4427 [[art:bbe07926:metrics.train.mean_predicted]].
The value of `metrics.train.n` is 3500 [[art:564683ee:metrics.train.n]].
The value of `psi.age` is 0.008124 [[art:f9255a0a:psi.age]].
The value of `psi.bill_mean_6m` is 0.007124 [[art:028e4281:psi.bill_mean_6m]].
The value of `psi.bill_trend_6m` is 0.00958 [[art:c247a6f2:psi.bill_trend_6m]].
The value of `psi.delinq_count_6m` is 0.002069 [[art:61491d02:psi.delinq_count_6m]].
The value of `psi.delinq_last` is 0.00285 [[art:03bd52e7:psi.delinq_last]].
The value of `psi.delinq_max_6m` is 0.005498 [[art:7a82e7f3:psi.delinq_max_6m]].
The value of `psi.limit_bal` is 0.01095 [[art:601cdba2:psi.limit_bal]].
The value of `psi.max` is 0.01095 [[art:381b2570:psi.max]].
The value of `psi.pay_ratio_last` is 0.004966 [[art:3af2ca29:psi.pay_ratio_last]].
The value of `psi.pay_ratio_mean_6m` is 0.0055 [[art:2c5baeb2:psi.pay_ratio_mean_6m]].
The value of `psi.utilisation` is 0.004244 [[art:451e0780:psi.utilisation]].
The value of `psi.y_score` is 0.005049 [[art:a8375d0f:psi.y_score]].
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
Candidates raised on this section's material: T1; C1; C1 (see the findings section).

## 5. Sensitivity and scenario analysis

This section follows the model risk management guidance at [[reg:SR26-2:V.1.a]].
The value of `condition_number` is 5.547 [[art:e41b9562:condition_number]].
The value of `threshold.M1.condition_number` is 30 [[art:7e52fd7a:threshold.M1.condition_number]].
The value of `threshold.M1.vif` is 10 [[art:aeb4f33c:threshold.M1.vif]].
The value of `vif.age` is 1.002 [[art:74c06cad:vif.age]].
The value of `vif.bill_mean_6m` is 7.295 [[art:f0a2f865:vif.bill_mean_6m]].
The value of `vif.bill_trend_6m` is 1.201 [[art:9356a256:vif.bill_trend_6m]].
The value of `vif.delinq_count_6m` is 2.561 [[art:38974def:vif.delinq_count_6m]].
The value of `vif.delinq_last` is 1.412 [[art:48733638:vif.delinq_last]].
The value of `vif.delinq_max_6m` is 2.408 [[art:71aaaf11:vif.delinq_max_6m]].
The value of `vif.limit_bal` is 4.803 [[art:ddfdcc3c:vif.limit_bal]].
The value of `vif.max` is 7.295 [[art:9ae7c45b:vif.max]].
The value of `vif.pay_ratio_last` is 7.264 [[art:c2de8dfe:vif.pay_ratio_last]].
The value of `vif.pay_ratio_mean_6m` is 7.259 [[art:e39c3e82:vif.pay_ratio_mean_6m]].
The value of `vif.utilisation` is 3.215 [[art:536fdb6f:vif.utilisation]].

## 6. Findings and recommendations

This section follows the model risk management guidance at [[reg:SR26-2:VI.3]].

### F-001 · T1 declared threshold · severity **high**

**A `T1` finding, raised by `compute_metrics` at severity `high`.**
Its evidence is the artifacts cited in this section; the check's own account of it is recorded in `findings.json`.

### F-002 · C1 calibration · severity **medium**

**A `C1` finding, raised by `compute_metrics` at severity `medium`.**
Its evidence is the artifacts cited in this section; the check's own account of it is recorded in `findings.json`.

### F-003 · E1 effective challenge · severity **low**

**A `E1` finding, raised by `challenger_compare` at severity `low`.**
Its evidence is the artifacts cited in this section; the check's own account of it is recorded in `findings.json`.
The value of `calibration.mean_rel_gap.test` is 0.9491 [[art:376ae2d7:calibration.mean_rel_gap.test]].
The value of `calibration.mean_rel_gap.train` is 0.9715 [[art:0abea673:calibration.mean_rel_gap.train]].
The value of `calibration_slope.test` is 0.7952 [[art:b2bc94fc:calibration_slope.test]].
The value of `calibration_slope.train` is 0.7656 [[art:1151c8e4:calibration_slope.train]].
The value of `challenger.auc` is 0.824 [[art:bf5be719:challenger.auc]].
The value of `challenger.delta_auc` is 0.0476 [[art:a86db8b1:challenger.delta_auc]].
The value of `metrics.test.auc` is 0.7764 [[art:06c7c666:metrics.test.auc]].
The value of `metrics.test.event_rate` is 0.2247 [[art:9209d200:metrics.test.event_rate]].
The value of `metrics.test.mean_predicted` is 0.4379 [[art:aa68c658:metrics.test.mean_predicted]].
The value of `metrics.train.event_rate` is 0.2246 [[art:133a5ff8:metrics.train.event_rate]].
The value of `metrics.train.mean_predicted` is 0.4427 [[art:bbe07926:metrics.train.mean_predicted]].
The value of `sign_check.limit_bal.agrees` is 0 [[art:0278aad1:sign_check.limit_bal.agrees]].
The value of `sign_check.limit_bal.coef_sign` is 1 [[art:6af6aef2:sign_check.limit_bal.coef_sign]].
The value of `sign_check.limit_bal.univariate_direction` is -1 [[art:56d284d6:sign_check.limit_bal.univariate_direction]].
The value of `threshold.C1.calibration_slope.min` is 0.8 [[art:749634ae:threshold.C1.calibration_slope.min]].
The value of `threshold.C1.mean_ratio_rel` is 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
The value of `threshold.E1.delta_auc` is 0.03 [[art:e042774c:threshold.E1.delta_auc]].
The value of `threshold.package.calibration_slope.test.min` is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]].
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

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1, S1), `compute_metrics` (O1), `check_leakage` (L1, L2), `check_collinearity` (M1).

### Open items

No open item was recorded for this validation.

## 7. Ongoing monitoring recommendations

This section follows the model risk management guidance at [[reg:SR26-2:V.2]].
The value of `calibration_slope.test` is 0.7952 [[art:b2bc94fc:calibration_slope.test]].
The value of `metrics.test.auc` is 0.7764 [[art:06c7c666:metrics.test.auc]].
The value of `metrics.test.brier` is 0.1929 [[art:2f64a7ce:metrics.test.brier]].
The value of `psi.max` is 0.01095 [[art:381b2570:psi.max]].
The value of `rule.calibration_first_event_rate` is 0.05 [[art:42f1351e:rule.calibration_first_event_rate]].
The value of `threshold.package.auc.test.min` is 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]].
The value of `threshold.package.brier.test.max` is 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]].
The value of `threshold.package.calibration_slope.test.max` is 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The value of `threshold.package.calibration_slope.test.min` is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].

## Appendix A — Claims

Grounding precision 1.0000 before repair (215 of 215 claims verified) and 1.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 31/31; conceptual_soundness 48/48; data_integrity 40/40; outcomes 54/54; sensitivity 14/14; findings 18/18; monitoring 10/10.

Developer claims: The package declares 2 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). See Appendix D.

Excluded numeric tokens (not claims): citation_hash (b2bc94fc, 1151c8e4, a86db8b1, e41b9562); regulatory_section_id (SR26-2:V.1.b, SR26-2:V.1.a, SR26-2:VI.3, SR26-2:V.2); finding_id (F-001, F-002, F-003).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The value of `calibration_slope.test` is 0.7952 . | 0.7952 | ratio | calibration_slope |  | eq | `[[art:b2bc94fc:calibration_slope.test]]` | verified | 0.7952064062 |
| 2 | summary | The value of `calibration_slope.train` is 0.7656 . | 0.7656 | ratio | calibration_slope |  | eq | `[[art:1151c8e4:calibration_slope.train]]` | verified | 0.7656065242 |
| 3 | summary | The value of `challenger.delta_auc` is 0.0476 . | 0.0476 | ratio | challenger |  | eq | `[[art:a86db8b1:challenger.delta_auc]]` | verified | 0.04759766387 |
| 4 | summary | The value of `condition_number` is 5.547 . | 5.547 | ratio | condition_number |  | eq | `[[art:e41b9562:condition_number]]` | verified | 5.546934633 |
| 5 | summary | The value of `csi.max` is 0.03295 . | 0.03295 | ratio | csi |  | eq | `[[art:e1f1ad3d:csi.max]]` | verified | 0.0329489964 |
| 6 | summary | The value of `metrics.test.auc` is 0.7764 . | 0.7764 | ratio | metrics |  | eq | `[[art:06c7c666:metrics.test.auc]]` | verified | 0.7763713511 |
| 7 | summary | The value of `metrics.test.brier` is 0.1929 . | 0.1929 | ratio | metrics |  | eq | `[[art:2f64a7ce:metrics.test.brier]]` | verified | 0.1928760509 |
| 8 | summary | The value of `metrics.test.event_rate` is 0.2247 . | 0.2247 | ratio | metrics |  | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 9 | summary | The value of `metrics.test.gini` is 0.5527 . | 0.5527 | ratio | metrics |  | eq | `[[art:bc939097:metrics.test.gini]]` | verified | 0.5527427022 |
| 10 | summary | The value of `metrics.test.ks` is 0.4656 . | 0.4656 | ratio | metrics |  | eq | `[[art:f4b92d62:metrics.test.ks]]` | verified | 0.4656278784 |
| 11 | summary | The value of `metrics.test.logloss` is 0.5935 . | 0.5935 | ratio | metrics |  | eq | `[[art:6ac37fc1:metrics.test.logloss]]` | verified | 0.5935045602 |
| 12 | summary | The value of `metrics.test.mean_predicted` is 0.4379 . | 0.4379 | ratio | metrics |  | eq | `[[art:aa68c658:metrics.test.mean_predicted]]` | verified | 0.4379028765 |
| 13 | summary | The value of `metrics.test.n` is 1500 . | 1500 | ratio | metrics |  | eq | `[[art:64fcf14d:metrics.test.n]]` | verified | 1500 |
| 14 | summary | The value of `metrics.train.auc` is 0.7765 . | 0.7765 | ratio | metrics |  | eq | `[[art:0e7355aa:metrics.train.auc]]` | verified | 0.7765019192 |
| 15 | summary | The value of `metrics.train.brier` is 0.1969 . | 0.1969 | ratio | metrics |  | eq | `[[art:f118c784:metrics.train.brier]]` | verified | 0.1968893522 |
| 16 | summary | The value of `metrics.train.event_rate` is 0.2246 . | 0.2246 | ratio | metrics |  | eq | `[[art:133a5ff8:metrics.train.event_rate]]` | verified | 0.2245714286 |
| 17 | summary | The value of `metrics.train.gini` is 0.553 . | 0.553 | ratio | metrics |  | eq | `[[art:1e398595:metrics.train.gini]]` | verified | 0.5530038384 |
| 18 | summary | The value of `metrics.train.ks` is 0.4801 . | 0.4801 | ratio | metrics |  | eq | `[[art:97bd5dab:metrics.train.ks]]` | verified | 0.4800544158 |
| 19 | summary | The value of `metrics.train.logloss` is 0.6031 . | 0.6031 | ratio | metrics |  | eq | `[[art:dcbefb71:metrics.train.logloss]]` | verified | 0.6031246073 |
| 20 | summary | The value of `metrics.train.mean_predicted` is 0.4427 . | 0.4427 | ratio | metrics |  | eq | `[[art:bbe07926:metrics.train.mean_predicted]]` | verified | 0.4427489586 |
| 21 | summary | The value of `metrics.train.n` is 3500 . | 3500 | ratio | metrics |  | eq | `[[art:564683ee:metrics.train.n]]` | verified | 3500 |
| 22 | summary | The value of `profile.test.n` is 1500 . | 1500 | ratio | profile |  | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 23 | summary | The value of `profile.train.n` is 3500 . | 3500 | ratio | profile |  | eq | `[[art:2510d49d:profile.train.n]]` | verified | 3500 |
| 24 | summary | The value of `psi.max` is 0.01095 . | 0.01095 | ratio | psi |  | eq | `[[art:381b2570:psi.max]]` | verified | 0.01095273358 |
| 25 | summary | The value of `runtime.max_seconds` is 300 . | 300 | ratio | runtime |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 26 | summary | The value of `threshold.package.auc.test.min` is 0.7 . | 0.7 | ratio | threshold |  | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 27 | summary | The value of `threshold.package.brier.test.max` is 0.2 . | 0.2 | ratio | threshold |  | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 28 | summary | The value of `threshold.package.calibration_slope.test.max`… | 1.2 | ratio | threshold |  | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 29 | summary | The value of `threshold.package.calibration_slope.test.min`… | 0.8 | ratio | threshold |  | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 30 | summary | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 31 | summary | The value of `vif.max` is 7.295 . | 7.295 | ratio | vif |  | eq | `[[art:9ae7c45b:vif.max]]` | verified | 7.295299885 |
| 32 | conceptual_soundness | The value of `ablation.age.delta_auc` is 0.00008675 . | 8.675e-05 | ratio | ablation |  | eq | `[[art:59398b1b:ablation.age.delta_auc]]` | verified | 8.674996364e-05 |
| 33 | conceptual_soundness | The value of `ablation.baseline_auc` is 0.748 . | 0.748 | ratio | ablation |  | eq | `[[art:3a44e438:ablation.baseline_auc]]` | verified | 0.7479888042 |
| 34 | conceptual_soundness | The value of `ablation.bill_mean_6m.delta_auc` is -0.0016 . | -0.0016 | ratio | ablation |  | eq | `[[art:3b91a889:ablation.bill_mean_6m.delta_auc]]` | verified | -0.001599771388 |
| 35 | conceptual_soundness | The value of `ablation.bill_trend_6m.delta_auc` is 0.003279… | 0.003279 | ratio | ablation |  | eq | `[[art:096d7f98:ablation.bill_trend_6m.delta_auc]]` | verified | 0.003278638332 |
| 36 | conceptual_soundness | The value of `ablation.delinq_count_6m.delta_auc` is 0.00068… | 0.0006812 | ratio | ablation |  | eq | `[[art:c5659def:ablation.delinq_count_6m.delta_auc]]` | verified | 0.0006812423615 |
| 37 | conceptual_soundness | The value of `ablation.delinq_last.delta_auc` is -0.07585 . | -0.07585 | ratio | ablation |  | eq | `[[art:3150b111:ablation.delinq_last.delta_auc]]` | verified | -0.07585263733 |
| 38 | conceptual_soundness | The value of `ablation.delinq_max_6m.delta_auc` is 0.0003598… | 0.0003598 | ratio | ablation |  | eq | `[[art:3a0d3a0c:ablation.delinq_max_6m.delta_auc]]` | verified | 0.0003597572022 |
| 39 | conceptual_soundness | The value of `ablation.limit_bal.delta_auc` is 0.0004286 . | 0.0004286 | ratio | ablation |  | eq | `[[art:63faa640:ablation.limit_bal.delta_auc]]` | verified | 0.0004286468792 |
| 40 | conceptual_soundness | The value of `ablation.pay_ratio_last.delta_auc` is 0.002411… | 0.002411 | ratio | ablation |  | eq | `[[art:5f39089e:ablation.pay_ratio_last.delta_auc]]` | verified | 0.002411138695 |
| 41 | conceptual_soundness | The value of `ablation.pay_ratio_mean_6m.delta_auc` is 0.006… | 0.006603 | ratio | ablation |  | eq | `[[art:90fa1178:ablation.pay_ratio_mean_6m.delta_auc]]` | verified | 0.006603203115 |
| 42 | conceptual_soundness | The value of `ablation.utilisation.delta_auc` is -0.01977 . | -0.01977 | ratio | ablation |  | eq | `[[art:d4ad2039:ablation.utilisation.delta_auc]]` | verified | -0.01976623436 |
| 43 | conceptual_soundness | The value of `challenger.auc` is 0.824 . | 0.824 | ratio | challenger |  | eq | `[[art:bf5be719:challenger.auc]]` | verified | 0.823969015 |
| 44 | conceptual_soundness | The value of `challenger.brier` is 0.1258 . | 0.1258 | ratio | challenger |  | eq | `[[art:f9e0583d:challenger.brier]]` | verified | 0.1258050391 |
| 45 | conceptual_soundness | The value of `challenger.delta_auc` is 0.0476 . | 0.0476 | ratio | challenger |  | eq | `[[art:a86db8b1:challenger.delta_auc]]` | verified | 0.04759766387 |
| 46 | conceptual_soundness | The value of `metrics.test.auc` is 0.7764 . | 0.7764 | ratio | metrics |  | eq | `[[art:06c7c666:metrics.test.auc]]` | verified | 0.7763713511 |
| 47 | conceptual_soundness | The value of `metrics.test.brier` is 0.1929 . | 0.1929 | ratio | metrics |  | eq | `[[art:2f64a7ce:metrics.test.brier]]` | verified | 0.1928760509 |
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
| 63 | conceptual_soundness | The value of `sign_check.delinq_max_6m.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:da92a015:sign_check.delinq_max_6m.agrees]]` | verified | 1 |
| 64 | conceptual_soundness | The value of `sign_check.delinq_max_6m.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:53560657:sign_check.delinq_max_6m.coef_sign]]` | verified | 1 |
| 65 | conceptual_soundness | The value of `sign_check.delinq_max_6m.univariate_direction`… | 1 | ratio | sign_check |  | eq | `[[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]]` | verified | 1 |
| 66 | conceptual_soundness | The value of `sign_check.limit_bal.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:0278aad1:sign_check.limit_bal.agrees]]` | verified | 0 |
| 67 | conceptual_soundness | The value of `sign_check.limit_bal.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:6af6aef2:sign_check.limit_bal.coef_sign]]` | verified | 1 |
| 68 | conceptual_soundness | The value of `sign_check.limit_bal.univariate_direction` is… | -1 | ratio | sign_check |  | eq | `[[art:56d284d6:sign_check.limit_bal.univariate_direction]]` | verified | -1 |
| 69 | conceptual_soundness | The value of `sign_check.n_disagreements` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:f96ece96:sign_check.n_disagreements]]` | verified | 1 |
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
| 80 | data_integrity | The value of `csi.age` is 0.001075 . | 0.001075 | ratio | csi |  | eq | `[[art:1642e34e:csi.age]]` | verified | 0.001074651834 |
| 81 | data_integrity | The value of `csi.bill_mean_6m` is 0.001757 . | 0.001757 | ratio | csi |  | eq | `[[art:278c2a6d:csi.bill_mean_6m]]` | verified | 0.00175661912 |
| 82 | data_integrity | The value of `csi.bill_trend_6m` is 0.006203 . | 0.006203 | ratio | csi |  | eq | `[[art:2567a75c:csi.bill_trend_6m]]` | verified | 0.006203453095 |
| 83 | data_integrity | The value of `csi.delinq_count_6m` is 0.002804 . | 0.002804 | ratio | csi |  | eq | `[[art:b0282e56:csi.delinq_count_6m]]` | verified | 0.002804356526 |
| 84 | data_integrity | The value of `csi.delinq_last` is 0.03295 . | 0.03295 | ratio | csi |  | eq | `[[art:39b31d8e:csi.delinq_last]]` | verified | 0.0329489964 |
| 85 | data_integrity | The value of `csi.delinq_max_6m` is 0.0003766 . | 0.0003766 | ratio | csi |  | eq | `[[art:3fc49a03:csi.delinq_max_6m]]` | verified | 0.0003766337845 |
| 86 | data_integrity | The value of `csi.limit_bal` is 0.0002712 . | 0.0002712 | ratio | csi |  | eq | `[[art:bc85c1c5:csi.limit_bal]]` | verified | 0.0002712443929 |
| 87 | data_integrity | The value of `csi.max` is 0.03295 . | 0.03295 | ratio | csi |  | eq | `[[art:e1f1ad3d:csi.max]]` | verified | 0.0329489964 |
| 88 | data_integrity | The value of `csi.pay_ratio_last` is 0.001721 . | 0.001721 | ratio | csi |  | eq | `[[art:fd186b68:csi.pay_ratio_last]]` | verified | 0.001720891957 |
| 89 | data_integrity | The value of `csi.pay_ratio_mean_6m` is 0.0008584 . | 0.0008584 | ratio | csi |  | eq | `[[art:659995f7:csi.pay_ratio_mean_6m]]` | verified | 0.0008583980615 |
| 90 | data_integrity | The value of `csi.utilisation` is 0.00724 . | 0.00724 | ratio | csi |  | eq | `[[art:0a1f2306:csi.utilisation]]` | verified | 0.007240075813 |
| 91 | data_integrity | The value of `leakage.duplicates.train` is 0 . | 0 | ratio | leakage |  | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 92 | data_integrity | The value of `leakage.name_screen.n_matched` is 0 . | 0 | ratio | leakage |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 93 | data_integrity | The value of `leakage.overlap` is 0 . | 0 | ratio | leakage |  | eq | `[[art:4c9fcd09:leakage.overlap]]` | verified | 0 |
| 94 | data_integrity | The value of `leakage.overlap.features` is 0 . | 0 | ratio | leakage |  | eq | `[[art:0fec8048:leakage.overlap.features]]` | verified | 0 |
| 95 | data_integrity | The value of `leakage.overlap.ids` is 0 . | 0 | ratio | leakage |  | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 96 | data_integrity | The value of `leakage.target_corr.max_single_feature_auc` is… | 0.6831 | ratio | leakage |  | eq | `[[art:fd829fc4:leakage.target_corr.max_single_feature_auc]]` | verified | 0.6831414154 |
| 97 | data_integrity | The value of `leakage.timing.n_flagged` is 0 . | 0 | ratio | leakage |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 98 | data_integrity | The value of `profile.test.missing.max` is 0 . | 0 | ratio | profile |  | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 99 | data_integrity | The value of `profile.test.n` is 1500 . | 1500 | ratio | profile |  | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 100 | data_integrity | The value of `profile.train.missing.max` is 0 . | 0 | ratio | profile |  | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 101 | data_integrity | The value of `profile.train.n` is 3500 . | 3500 | ratio | profile |  | eq | `[[art:2510d49d:profile.train.n]]` | verified | 3500 |
| 102 | data_integrity | The value of `psi.age` is 0.008124 . | 0.008124 | ratio | psi |  | eq | `[[art:f9255a0a:psi.age]]` | verified | 0.008124281436 |
| 103 | data_integrity | The value of `psi.bill_mean_6m` is 0.007124 . | 0.007124 | ratio | psi |  | eq | `[[art:028e4281:psi.bill_mean_6m]]` | verified | 0.007124196275 |
| 104 | data_integrity | The value of `psi.bill_trend_6m` is 0.00958 . | 0.00958 | ratio | psi |  | eq | `[[art:c247a6f2:psi.bill_trend_6m]]` | verified | 0.009579614525 |
| 105 | data_integrity | The value of `psi.delinq_count_6m` is 0.002069 . | 0.002069 | ratio | psi |  | eq | `[[art:61491d02:psi.delinq_count_6m]]` | verified | 0.002069275496 |
| 106 | data_integrity | The value of `psi.delinq_last` is 0.00285 . | 0.00285 | ratio | psi |  | eq | `[[art:03bd52e7:psi.delinq_last]]` | verified | 0.002849633848 |
| 107 | data_integrity | The value of `psi.delinq_max_6m` is 0.005498 . | 0.005498 | ratio | psi |  | eq | `[[art:7a82e7f3:psi.delinq_max_6m]]` | verified | 0.005498249408 |
| 108 | data_integrity | The value of `psi.limit_bal` is 0.01095 . | 0.01095 | ratio | psi |  | eq | `[[art:601cdba2:psi.limit_bal]]` | verified | 0.01095273358 |
| 109 | data_integrity | The value of `psi.max` is 0.01095 . | 0.01095 | ratio | psi |  | eq | `[[art:381b2570:psi.max]]` | verified | 0.01095273358 |
| 110 | data_integrity | The value of `psi.pay_ratio_last` is 0.004966 . | 0.004966 | ratio | psi |  | eq | `[[art:3af2ca29:psi.pay_ratio_last]]` | verified | 0.00496591109 |
| 111 | data_integrity | The value of `psi.pay_ratio_mean_6m` is 0.0055 . | 0.0055 | ratio | psi |  | eq | `[[art:2c5baeb2:psi.pay_ratio_mean_6m]]` | verified | 0.005500252946 |
| 112 | data_integrity | The value of `psi.utilisation` is 0.004244 . | 0.004244 | ratio | psi |  | eq | `[[art:451e0780:psi.utilisation]]` | verified | 0.0042440485 |
| 113 | data_integrity | The value of `psi.y_score` is 0.005049 . | 0.005049 | ratio | psi |  | eq | `[[art:a8375d0f:psi.y_score]]` | verified | 0.005049433774 |
| 114 | data_integrity | The value of `threshold.D1.missing_gap` is 0.1 . | 0.1 | ratio | threshold |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 115 | data_integrity | The value of `threshold.L1.single_feature_auc` is 0.9 . | 0.9 | ratio | threshold |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 116 | data_integrity | The value of `threshold.L2.overlap` is 0.005 . | 0.005 | ratio | threshold |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 117 | data_integrity | The value of `threshold.L2.overlap.features_effective` is 0.… | 0.005 | ratio | threshold |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 118 | data_integrity | The value of `threshold.S1.psi` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 119 | data_integrity | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 120 | outcomes | The value of `calibration.mean_rel_gap.test` is 0.9491 . | 0.9491 | ratio | calibration |  | eq | `[[art:376ae2d7:calibration.mean_rel_gap.test]]` | verified | 0.9491225955 |
| 121 | outcomes | The value of `calibration.mean_rel_gap.train` is 0.9715 . | 0.9715 | ratio | calibration |  | eq | `[[art:0abea673:calibration.mean_rel_gap.train]]` | verified | 0.9715284416 |
| 122 | outcomes | The value of `calibration_intercept.test` is -1.217 . | -1.217 | ratio | calibration_intercept |  | eq | `[[art:62851316:calibration_intercept.test]]` | verified | -1.21748713 |
| 123 | outcomes | The value of `calibration_intercept.train` is -1.241 . | -1.241 | ratio | calibration_intercept |  | eq | `[[art:849b7b2e:calibration_intercept.train]]` | verified | -1.240800979 |
| 124 | outcomes | The value of `calibration_slope.test` is 0.7952 . | 0.7952 | ratio | calibration_slope |  | eq | `[[art:b2bc94fc:calibration_slope.test]]` | verified | 0.7952064062 |
| 125 | outcomes | The value of `calibration_slope.train` is 0.7656 . | 0.7656 | ratio | calibration_slope |  | eq | `[[art:1151c8e4:calibration_slope.train]]` | verified | 0.7656065242 |
| 126 | outcomes | The value of `deciles.test.top2_capture` is 0.4451 . | 0.4451 | ratio | deciles |  | eq | `[[art:e3b6058b:deciles.test.top2_capture]]` | verified | 0.4451038576 |
| 127 | outcomes | The value of `deciles.train.top2_capture` is 0.4262 . | 0.4262 | ratio | deciles |  | eq | `[[art:1693b145:deciles.train.top2_capture]]` | verified | 0.4262086514 |
| 128 | outcomes | The value of `metrics.test.auc` is 0.7764 . | 0.7764 | ratio | metrics |  | eq | `[[art:06c7c666:metrics.test.auc]]` | verified | 0.7763713511 |
| 129 | outcomes | The value of `metrics.test.brier` is 0.1929 . | 0.1929 | ratio | metrics |  | eq | `[[art:2f64a7ce:metrics.test.brier]]` | verified | 0.1928760509 |
| 130 | outcomes | The value of `metrics.test.event_rate` is 0.2247 . | 0.2247 | ratio | metrics |  | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 131 | outcomes | The value of `metrics.test.gini` is 0.5527 . | 0.5527 | ratio | metrics |  | eq | `[[art:bc939097:metrics.test.gini]]` | verified | 0.5527427022 |
| 132 | outcomes | The value of `metrics.test.ks` is 0.4656 . | 0.4656 | ratio | metrics |  | eq | `[[art:f4b92d62:metrics.test.ks]]` | verified | 0.4656278784 |
| 133 | outcomes | The value of `metrics.test.logloss` is 0.5935 . | 0.5935 | ratio | metrics |  | eq | `[[art:6ac37fc1:metrics.test.logloss]]` | verified | 0.5935045602 |
| 134 | outcomes | The value of `metrics.test.mean_predicted` is 0.4379 . | 0.4379 | ratio | metrics |  | eq | `[[art:aa68c658:metrics.test.mean_predicted]]` | verified | 0.4379028765 |
| 135 | outcomes | The value of `metrics.test.n` is 1500 . | 1500 | ratio | metrics |  | eq | `[[art:64fcf14d:metrics.test.n]]` | verified | 1500 |
| 136 | outcomes | The value of `metrics.train.auc` is 0.7765 . | 0.7765 | ratio | metrics |  | eq | `[[art:0e7355aa:metrics.train.auc]]` | verified | 0.7765019192 |
| 137 | outcomes | The value of `metrics.train.brier` is 0.1969 . | 0.1969 | ratio | metrics |  | eq | `[[art:f118c784:metrics.train.brier]]` | verified | 0.1968893522 |
| 138 | outcomes | The value of `metrics.train.event_rate` is 0.2246 . | 0.2246 | ratio | metrics |  | eq | `[[art:133a5ff8:metrics.train.event_rate]]` | verified | 0.2245714286 |
| 139 | outcomes | The value of `metrics.train.gini` is 0.553 . | 0.553 | ratio | metrics |  | eq | `[[art:1e398595:metrics.train.gini]]` | verified | 0.5530038384 |
| 140 | outcomes | The value of `metrics.train.ks` is 0.4801 . | 0.4801 | ratio | metrics |  | eq | `[[art:97bd5dab:metrics.train.ks]]` | verified | 0.4800544158 |
| 141 | outcomes | The value of `metrics.train.logloss` is 0.6031 . | 0.6031 | ratio | metrics |  | eq | `[[art:dcbefb71:metrics.train.logloss]]` | verified | 0.6031246073 |
| 142 | outcomes | The value of `metrics.train.mean_predicted` is 0.4427 . | 0.4427 | ratio | metrics |  | eq | `[[art:bbe07926:metrics.train.mean_predicted]]` | verified | 0.4427489586 |
| 143 | outcomes | The value of `metrics.train.n` is 3500 . | 3500 | ratio | metrics |  | eq | `[[art:564683ee:metrics.train.n]]` | verified | 3500 |
| 144 | outcomes | The value of `psi.age` is 0.008124 . | 0.008124 | ratio | psi |  | eq | `[[art:f9255a0a:psi.age]]` | verified | 0.008124281436 |
| 145 | outcomes | The value of `psi.bill_mean_6m` is 0.007124 . | 0.007124 | ratio | psi |  | eq | `[[art:028e4281:psi.bill_mean_6m]]` | verified | 0.007124196275 |
| 146 | outcomes | The value of `psi.bill_trend_6m` is 0.00958 . | 0.00958 | ratio | psi |  | eq | `[[art:c247a6f2:psi.bill_trend_6m]]` | verified | 0.009579614525 |
| 147 | outcomes | The value of `psi.delinq_count_6m` is 0.002069 . | 0.002069 | ratio | psi |  | eq | `[[art:61491d02:psi.delinq_count_6m]]` | verified | 0.002069275496 |
| 148 | outcomes | The value of `psi.delinq_last` is 0.00285 . | 0.00285 | ratio | psi |  | eq | `[[art:03bd52e7:psi.delinq_last]]` | verified | 0.002849633848 |
| 149 | outcomes | The value of `psi.delinq_max_6m` is 0.005498 . | 0.005498 | ratio | psi |  | eq | `[[art:7a82e7f3:psi.delinq_max_6m]]` | verified | 0.005498249408 |
| 150 | outcomes | The value of `psi.limit_bal` is 0.01095 . | 0.01095 | ratio | psi |  | eq | `[[art:601cdba2:psi.limit_bal]]` | verified | 0.01095273358 |
| 151 | outcomes | The value of `psi.max` is 0.01095 . | 0.01095 | ratio | psi |  | eq | `[[art:381b2570:psi.max]]` | verified | 0.01095273358 |
| 152 | outcomes | The value of `psi.pay_ratio_last` is 0.004966 . | 0.004966 | ratio | psi |  | eq | `[[art:3af2ca29:psi.pay_ratio_last]]` | verified | 0.00496591109 |
| 153 | outcomes | The value of `psi.pay_ratio_mean_6m` is 0.0055 . | 0.0055 | ratio | psi |  | eq | `[[art:2c5baeb2:psi.pay_ratio_mean_6m]]` | verified | 0.005500252946 |
| 154 | outcomes | The value of `psi.utilisation` is 0.004244 . | 0.004244 | ratio | psi |  | eq | `[[art:451e0780:psi.utilisation]]` | verified | 0.0042440485 |
| 155 | outcomes | The value of `psi.y_score` is 0.005049 . | 0.005049 | ratio | psi |  | eq | `[[art:a8375d0f:psi.y_score]]` | verified | 0.005049433774 |
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
| 174 | sensitivity | The value of `condition_number` is 5.547 . | 5.547 | ratio | condition_number |  | eq | `[[art:e41b9562:condition_number]]` | verified | 5.546934633 |
| 175 | sensitivity | The value of `threshold.M1.condition_number` is 30 . | 30 | ratio | threshold |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 176 | sensitivity | The value of `threshold.M1.vif` is 10 . | 10 | ratio | threshold |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 177 | sensitivity | The value of `vif.age` is 1.002 . | 1.002 | ratio | vif |  | eq | `[[art:74c06cad:vif.age]]` | verified | 1.001957997 |
| 178 | sensitivity | The value of `vif.bill_mean_6m` is 7.295 . | 7.295 | ratio | vif |  | eq | `[[art:f0a2f865:vif.bill_mean_6m]]` | verified | 7.295299885 |
| 179 | sensitivity | The value of `vif.bill_trend_6m` is 1.201 . | 1.201 | ratio | vif |  | eq | `[[art:9356a256:vif.bill_trend_6m]]` | verified | 1.201449441 |
| 180 | sensitivity | The value of `vif.delinq_count_6m` is 2.561 . | 2.561 | ratio | vif |  | eq | `[[art:38974def:vif.delinq_count_6m]]` | verified | 2.561484187 |
| 181 | sensitivity | The value of `vif.delinq_last` is 1.412 . | 1.412 | ratio | vif |  | eq | `[[art:48733638:vif.delinq_last]]` | verified | 1.411555667 |
| 182 | sensitivity | The value of `vif.delinq_max_6m` is 2.408 . | 2.408 | ratio | vif |  | eq | `[[art:71aaaf11:vif.delinq_max_6m]]` | verified | 2.40773 |
| 183 | sensitivity | The value of `vif.limit_bal` is 4.803 . | 4.803 | ratio | vif |  | eq | `[[art:ddfdcc3c:vif.limit_bal]]` | verified | 4.803401129 |
| 184 | sensitivity | The value of `vif.max` is 7.295 . | 7.295 | ratio | vif |  | eq | `[[art:9ae7c45b:vif.max]]` | verified | 7.295299885 |
| 185 | sensitivity | The value of `vif.pay_ratio_last` is 7.264 . | 7.264 | ratio | vif |  | eq | `[[art:c2de8dfe:vif.pay_ratio_last]]` | verified | 7.264342098 |
| 186 | sensitivity | The value of `vif.pay_ratio_mean_6m` is 7.259 . | 7.259 | ratio | vif |  | eq | `[[art:e39c3e82:vif.pay_ratio_mean_6m]]` | verified | 7.25926398 |
| 187 | sensitivity | The value of `vif.utilisation` is 3.215 . | 3.215 | ratio | vif |  | eq | `[[art:536fdb6f:vif.utilisation]]` | verified | 3.215148369 |
| 188 | findings | The value of `calibration.mean_rel_gap.test` is 0.9491 . | 0.9491 | ratio | calibration |  | eq | `[[art:376ae2d7:calibration.mean_rel_gap.test]]` | verified | 0.9491225955 |
| 189 | findings | The value of `calibration.mean_rel_gap.train` is 0.9715 . | 0.9715 | ratio | calibration |  | eq | `[[art:0abea673:calibration.mean_rel_gap.train]]` | verified | 0.9715284416 |
| 190 | findings | The value of `calibration_slope.test` is 0.7952 . | 0.7952 | ratio | calibration_slope |  | eq | `[[art:b2bc94fc:calibration_slope.test]]` | verified | 0.7952064062 |
| 191 | findings | The value of `calibration_slope.train` is 0.7656 . | 0.7656 | ratio | calibration_slope |  | eq | `[[art:1151c8e4:calibration_slope.train]]` | verified | 0.7656065242 |
| 192 | findings | The value of `challenger.auc` is 0.824 . | 0.824 | ratio | challenger |  | eq | `[[art:bf5be719:challenger.auc]]` | verified | 0.823969015 |
| 193 | findings | The value of `challenger.delta_auc` is 0.0476 . | 0.0476 | ratio | challenger |  | eq | `[[art:a86db8b1:challenger.delta_auc]]` | verified | 0.04759766387 |
| 194 | findings | The value of `metrics.test.auc` is 0.7764 . | 0.7764 | ratio | metrics |  | eq | `[[art:06c7c666:metrics.test.auc]]` | verified | 0.7763713511 |
| 195 | findings | The value of `metrics.test.event_rate` is 0.2247 . | 0.2247 | ratio | metrics |  | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 196 | findings | The value of `metrics.test.mean_predicted` is 0.4379 . | 0.4379 | ratio | metrics |  | eq | `[[art:aa68c658:metrics.test.mean_predicted]]` | verified | 0.4379028765 |
| 197 | findings | The value of `metrics.train.event_rate` is 0.2246 . | 0.2246 | ratio | metrics |  | eq | `[[art:133a5ff8:metrics.train.event_rate]]` | verified | 0.2245714286 |
| 198 | findings | The value of `metrics.train.mean_predicted` is 0.4427 . | 0.4427 | ratio | metrics |  | eq | `[[art:bbe07926:metrics.train.mean_predicted]]` | verified | 0.4427489586 |
| 199 | findings | The value of `sign_check.limit_bal.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:0278aad1:sign_check.limit_bal.agrees]]` | verified | 0 |
| 200 | findings | The value of `sign_check.limit_bal.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:6af6aef2:sign_check.limit_bal.coef_sign]]` | verified | 1 |
| 201 | findings | The value of `sign_check.limit_bal.univariate_direction` is… | -1 | ratio | sign_check |  | eq | `[[art:56d284d6:sign_check.limit_bal.univariate_direction]]` | verified | -1 |
| 202 | findings | The value of `threshold.C1.calibration_slope.min` is 0.8 . | 0.8 | ratio | threshold |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 203 | findings | The value of `threshold.C1.mean_ratio_rel` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 204 | findings | The value of `threshold.E1.delta_auc` is 0.03 . | 0.03 | ratio | threshold |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 205 | findings | The value of `threshold.package.calibration_slope.test.min`… | 0.8 | ratio | threshold |  | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 206 | monitoring | The value of `calibration_slope.test` is 0.7952 . | 0.7952 | ratio | calibration_slope |  | eq | `[[art:b2bc94fc:calibration_slope.test]]` | verified | 0.7952064062 |
| 207 | monitoring | The value of `metrics.test.auc` is 0.7764 . | 0.7764 | ratio | metrics |  | eq | `[[art:06c7c666:metrics.test.auc]]` | verified | 0.7763713511 |
| 208 | monitoring | The value of `metrics.test.brier` is 0.1929 . | 0.1929 | ratio | metrics |  | eq | `[[art:2f64a7ce:metrics.test.brier]]` | verified | 0.1928760509 |
| 209 | monitoring | The value of `psi.max` is 0.01095 . | 0.01095 | ratio | psi |  | eq | `[[art:381b2570:psi.max]]` | verified | 0.01095273358 |
| 210 | monitoring | The value of `rule.calibration_first_event_rate` is 0.05 . | 0.05 | ratio | rule |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 211 | monitoring | The value of `threshold.package.auc.test.min` is 0.7 . | 0.7 | ratio | threshold |  | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 212 | monitoring | The value of `threshold.package.brier.test.max` is 0.2 . | 0.2 | ratio | threshold |  | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 213 | monitoring | The value of `threshold.package.calibration_slope.test.max`… | 1.2 | ratio | threshold |  | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 214 | monitoring | The value of `threshold.package.calibration_slope.test.min`… | 0.8 | ratio | threshold |  | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 215 | monitoring | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |

## Appendix B — Artifact index

The store holds 168 artifacts; the 138 this report cites or rests a finding on are indexed here.

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
| `sign_check.delinq_max_6m.agrees` | `da92a015` | scalar | 1 | 1 when the fitted sign on delinq_max_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.delinq_max_6m.coef_sign` | `53560657` | scalar | 1 | the sign of the fitted coefficient on delinq_max_6m |
| `sign_check.delinq_max_6m.univariate_direction` | `b9088f4a` | scalar | 1 | the sign of delinq_max_6m's own single-feature AUC on train minus 0.5 |
| `sign_check.limit_bal.agrees` | `0278aad1` | scalar | 0 | 1 when the fitted sign on limit_bal agrees with its univariate direction, 0 when it does not |
| `sign_check.limit_bal.coef_sign` | `6af6aef2` | scalar | 1 | the sign of the fitted coefficient on limit_bal |
| `sign_check.limit_bal.univariate_direction` | `56d284d6` | scalar | -1 | the sign of limit_bal's own single-feature AUC on train minus 0.5 |
| `sign_check.n_disagreements` | `f96ece96` | scalar | 1 | retained features whose fitted sign contradicts their univariate direction, of 10 checked |
| `sign_check.pay_ratio_last.agrees` | `7837941a` | scalar | 1 | 1 when the fitted sign on pay_ratio_last agrees with its univariate direction, 0 when it does not |
| `sign_check.pay_ratio_last.coef_sign` | `489c3e67` | scalar | -1 | the sign of the fitted coefficient on pay_ratio_last |
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
| tool calls | 13 (run_model 1, profile_data 1, compute_metrics 1, check_leakage 1, check_collinearity 1, challenger_compare 1, retrieve_guidance 7) |
| plan steps (bounded loop) | 0 |
| LLM calls | 0 () |
| re-asks | 0 |
| repair rounds | 0 |
| tokens in / out | 0 / 0 |
| notional cost (USD) | 0.0000 |
| wall-clock (s) | 1.27 |
| subject run (s) | 1.20 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | fake |
| model | none: no model answered |
| run id | credit_default-rules_only-20260918T065314Z-bd5861e9 |

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
