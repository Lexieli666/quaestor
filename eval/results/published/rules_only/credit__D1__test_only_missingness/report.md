---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: rules_only
model: fake
run_id: credit_default-rules_only-20260918T065317Z-bd5861e9
data_mode: synthetic
synthetic_n: 5000
grounding_precision_pre: 1.0000
grounding_precision_post: 1.0000
n_claims: 200
n_findings_by_severity: {high: 0, medium: 1, low: 1, info: 0}
generated: "2026-09-18T06:53:17Z"
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
The value of `calibration_slope.test` is 0.9778 [[art:c07e2c62:calibration_slope.test]].
The value of `calibration_slope.train` is 1.002 [[art:d02e3091:calibration_slope.train]].
The value of `challenger.delta_auc` is 0.08022 [[art:19982ff0:challenger.delta_auc]].
The value of `condition_number` is 5.547 [[art:e41b9562:condition_number]].
The value of `csi.max` is 0.02363 [[art:e56cb179:csi.max]].
The value of `metrics.test.auc` is 0.7446 [[art:21514080:metrics.test.auc]].
The value of `metrics.test.brier` is 0.1494 [[art:61f24b2a:metrics.test.brier]].
The value of `metrics.test.event_rate` is 0.2247 [[art:9209d200:metrics.test.event_rate]].
The value of `metrics.test.gini` is 0.4893 [[art:6d62a3df:metrics.test.gini]].
The value of `metrics.test.ks` is 0.41 [[art:2bfec7c8:metrics.test.ks]].
The value of `metrics.test.logloss` is 0.4684 [[art:92c35262:metrics.test.logloss]].
The value of `metrics.test.mean_predicted` is 0.2127 [[art:5cd71007:metrics.test.mean_predicted]].
The value of `metrics.test.n` is 1500 [[art:64fcf14d:metrics.test.n]].
The value of `metrics.train.auc` is 0.7584 [[art:14b38a2b:metrics.train.auc]].
The value of `metrics.train.brier` is 0.1489 [[art:be669a99:metrics.train.brier]].
The value of `metrics.train.event_rate` is 0.2246 [[art:133a5ff8:metrics.train.event_rate]].
The value of `metrics.train.gini` is 0.5169 [[art:b4da846e:metrics.train.gini]].
The value of `metrics.train.ks` is 0.4451 [[art:ccc12729:metrics.train.ks]].
The value of `metrics.train.logloss` is 0.465 [[art:4f02e465:metrics.train.logloss]].
The value of `metrics.train.mean_predicted` is 0.2246 [[art:605cce58:metrics.train.mean_predicted]].
The value of `metrics.train.n` is 3500 [[art:564683ee:metrics.train.n]].
The value of `profile.test.n` is 1500 [[art:2193cf5f:profile.test.n]].
The value of `profile.train.n` is 3500 [[art:2510d49d:profile.train.n]].
The value of `psi.max` is 0.03973 [[art:9dec5a22:psi.max]].
The value of `runtime.max_seconds` is 300 [[art:2ad8d1a5:runtime.max_seconds]].
The value of `threshold.package.auc.test.min` is 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]].
The value of `threshold.package.brier.test.max` is 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]].
The value of `threshold.package.calibration_slope.test.max` is 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The value of `threshold.package.calibration_slope.test.min` is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
The value of `vif.max` is 7.295 [[art:9ae7c45b:vif.max]].

## 2. Conceptual soundness

This section follows the model risk management guidance at [[reg:SR26-2:V.1.a]].
The value of `challenger.auc` is 0.8249 [[art:6db67e77:challenger.auc]].
The value of `challenger.brier` is 0.1248 [[art:67796f7f:challenger.brier]].
The value of `challenger.delta_auc` is 0.08022 [[art:19982ff0:challenger.delta_auc]].
The value of `metrics.test.auc` is 0.7446 [[art:21514080:metrics.test.auc]].
The value of `metrics.test.brier` is 0.1494 [[art:61f24b2a:metrics.test.brier]].
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
The value of `csi.age` is 0.0009476 [[art:a78e58f6:csi.age]].
The value of `csi.bill_mean_6m` is 0.002369 [[art:48df6cc9:csi.bill_mean_6m]].
The value of `csi.bill_trend_6m` is 0.00633 [[art:59948e6d:csi.bill_trend_6m]].
The value of `csi.delinq_count_6m` is 0.002449 [[art:69346f52:csi.delinq_count_6m]].
The value of `csi.delinq_last` is 0.02363 [[art:5babe364:csi.delinq_last]].
The value of `csi.delinq_max_6m` is 0.0008965 [[art:7244960d:csi.delinq_max_6m]].
The value of `csi.limit_bal` is 0.001211 [[art:5b77b34b:csi.limit_bal]].
The value of `csi.max` is 0.02363 [[art:e56cb179:csi.max]].
The value of `csi.pay_ratio_last` is 0.004524 [[art:5eec4717:csi.pay_ratio_last]].
The value of `csi.pay_ratio_mean_6m` is 0.001768 [[art:f567818e:csi.pay_ratio_mean_6m]].
The value of `csi.utilisation` is 0.004042 [[art:10f0f9e7:csi.utilisation]].
The value of `leakage.duplicates.train` is 0 [[art:4474c227:leakage.duplicates.train]].
The value of `leakage.name_screen.n_matched` is 0 [[art:407e62be:leakage.name_screen.n_matched]].
The value of `leakage.overlap` is 0 [[art:4c9fcd09:leakage.overlap]].
The value of `leakage.overlap.features` is 0 [[art:0fec8048:leakage.overlap.features]].
The value of `leakage.overlap.ids` is 0 [[art:63d37fc5:leakage.overlap.ids]].
The value of `leakage.target_corr.max_single_feature_auc` is 0.6831 [[art:fd829fc4:leakage.target_corr.max_single_feature_auc]].
The value of `leakage.timing.n_flagged` is 0 [[art:742bcd24:leakage.timing.n_flagged]].
The value of `profile.test.missing.max` is 0.3 [[art:7b5c0c01:profile.test.missing.max]].
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
The value of `psi.max` is 0.03973 [[art:9dec5a22:psi.max]].
The value of `psi.pay_ratio_last` is 0.005424 [[art:4f6eddcb:psi.pay_ratio_last]].
The value of `psi.pay_ratio_mean_6m` is 0.0055 [[art:2c5baeb2:psi.pay_ratio_mean_6m]].
The value of `psi.utilisation` is 0.004244 [[art:451e0780:psi.utilisation]].
The value of `psi.y_score` is 0.03973 [[art:828961f6:psi.y_score]].
The value of `threshold.D1.missing_gap` is 0.1 [[art:9cce25ea:threshold.D1.missing_gap]].
The value of `threshold.L1.single_feature_auc` is 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]].
The value of `threshold.L2.overlap` is 0.005 [[art:9f336eaf:threshold.L2.overlap]].
The value of `threshold.L2.overlap.features_effective` is 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].
The value of `threshold.S1.psi` is 0.25 [[art:278b9016:threshold.S1.psi]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
Candidates raised on this section's material: D1 (see the findings section).

## 4. Outcomes analysis

This section follows the model risk management guidance at [[reg:SR26-2:V.1.b]].
The value of `calibration.mean_rel_gap.test` is 0.05348 [[art:64a3c99e:calibration.mean_rel_gap.test]].
The value of `calibration.mean_rel_gap.train` is 0.0002283 [[art:53738d45:calibration.mean_rel_gap.train]].
The value of `calibration_intercept.test` is 0.05554 [[art:f4d4ef2b:calibration_intercept.test]].
The value of `calibration_intercept.train` is 0.002062 [[art:ed381a81:calibration_intercept.train]].
The value of `calibration_slope.test` is 0.9778 [[art:c07e2c62:calibration_slope.test]].
The value of `calibration_slope.train` is 1.002 [[art:d02e3091:calibration_slope.train]].
The value of `deciles.test.top2_capture` is 0.4688 [[art:17d2971c:deciles.test.top2_capture]].
The value of `deciles.train.top2_capture` is 0.4517 [[art:1d20c762:deciles.train.top2_capture]].
The value of `metrics.test.auc` is 0.7446 [[art:21514080:metrics.test.auc]].
The value of `metrics.test.brier` is 0.1494 [[art:61f24b2a:metrics.test.brier]].
The value of `metrics.test.event_rate` is 0.2247 [[art:9209d200:metrics.test.event_rate]].
The value of `metrics.test.gini` is 0.4893 [[art:6d62a3df:metrics.test.gini]].
The value of `metrics.test.ks` is 0.41 [[art:2bfec7c8:metrics.test.ks]].
The value of `metrics.test.logloss` is 0.4684 [[art:92c35262:metrics.test.logloss]].
The value of `metrics.test.mean_predicted` is 0.2127 [[art:5cd71007:metrics.test.mean_predicted]].
The value of `metrics.test.n` is 1500 [[art:64fcf14d:metrics.test.n]].
The value of `metrics.train.auc` is 0.7584 [[art:14b38a2b:metrics.train.auc]].
The value of `metrics.train.brier` is 0.1489 [[art:be669a99:metrics.train.brier]].
The value of `metrics.train.event_rate` is 0.2246 [[art:133a5ff8:metrics.train.event_rate]].
The value of `metrics.train.gini` is 0.5169 [[art:b4da846e:metrics.train.gini]].
The value of `metrics.train.ks` is 0.4451 [[art:ccc12729:metrics.train.ks]].
The value of `metrics.train.logloss` is 0.465 [[art:4f02e465:metrics.train.logloss]].
The value of `metrics.train.mean_predicted` is 0.2246 [[art:605cce58:metrics.train.mean_predicted]].
The value of `metrics.train.n` is 3500 [[art:564683ee:metrics.train.n]].
The value of `psi.age` is 0.008124 [[art:f9255a0a:psi.age]].
The value of `psi.bill_mean_6m` is 0.007124 [[art:028e4281:psi.bill_mean_6m]].
The value of `psi.bill_trend_6m` is 0.00958 [[art:c247a6f2:psi.bill_trend_6m]].
The value of `psi.delinq_count_6m` is 0.002069 [[art:61491d02:psi.delinq_count_6m]].
The value of `psi.delinq_last` is 0.00285 [[art:03bd52e7:psi.delinq_last]].
The value of `psi.delinq_max_6m` is 0.005498 [[art:7a82e7f3:psi.delinq_max_6m]].
The value of `psi.limit_bal` is 0.01095 [[art:601cdba2:psi.limit_bal]].
The value of `psi.max` is 0.03973 [[art:9dec5a22:psi.max]].
The value of `psi.pay_ratio_last` is 0.005424 [[art:4f6eddcb:psi.pay_ratio_last]].
The value of `psi.pay_ratio_mean_6m` is 0.0055 [[art:2c5baeb2:psi.pay_ratio_mean_6m]].
The value of `psi.utilisation` is 0.004244 [[art:451e0780:psi.utilisation]].
The value of `psi.y_score` is 0.03973 [[art:828961f6:psi.y_score]].
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

### F-001 · D1 data integrity · severity **medium**

**A `D1` finding, raised by `profile_data` at severity `medium`.**
Its evidence is the artifacts cited in this section; the check's own account of it is recorded in `findings.json`.

### F-002 · E1 effective challenge · severity **low**

**A `E1` finding, raised by `challenger_compare` at severity `low`.**
Its evidence is the artifacts cited in this section; the check's own account of it is recorded in `findings.json`.
The value of `challenger.auc` is 0.8249 [[art:6db67e77:challenger.auc]].
The value of `challenger.delta_auc` is 0.08022 [[art:19982ff0:challenger.delta_auc]].
The value of `metrics.test.auc` is 0.7446 [[art:21514080:metrics.test.auc]].
The value of `sign_check.delinq_max_6m.agrees` is 0 [[art:c946359c:sign_check.delinq_max_6m.agrees]].
The value of `sign_check.delinq_max_6m.coef_sign` is -1 [[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]].
The value of `sign_check.delinq_max_6m.univariate_direction` is 1 [[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]].
The value of `sign_check.limit_bal.agrees` is 0 [[art:0278aad1:sign_check.limit_bal.agrees]].
The value of `sign_check.limit_bal.coef_sign` is 1 [[art:6af6aef2:sign_check.limit_bal.coef_sign]].
The value of `sign_check.limit_bal.univariate_direction` is -1 [[art:56d284d6:sign_check.limit_bal.univariate_direction]].
The value of `sign_check.pay_ratio_last.agrees` is 0 [[art:79abee77:sign_check.pay_ratio_last.agrees]].
The value of `sign_check.pay_ratio_last.coef_sign` is 1 [[art:f018263e:sign_check.pay_ratio_last.coef_sign]].
The value of `sign_check.pay_ratio_last.univariate_direction` is -1 [[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]].
The value of `threshold.D1.missing_gap` is 0.1 [[art:9cce25ea:threshold.D1.missing_gap]].
The value of `threshold.E1.delta_auc` is 0.03 [[art:e042774c:threshold.E1.delta_auc]].
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

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (S1), `compute_metrics` (T1, C1, O1), `check_leakage` (L1, L2), `check_collinearity` (M1).

### Open items

No open item was recorded for this validation.

## 7. Ongoing monitoring recommendations

This section follows the model risk management guidance at [[reg:SR26-2:V.2]].
The value of `calibration_slope.test` is 0.9778 [[art:c07e2c62:calibration_slope.test]].
The value of `metrics.test.auc` is 0.7446 [[art:21514080:metrics.test.auc]].
The value of `metrics.test.brier` is 0.1494 [[art:61f24b2a:metrics.test.brier]].
The value of `psi.max` is 0.03973 [[art:9dec5a22:psi.max]].
The value of `rule.calibration_first_event_rate` is 0.05 [[art:42f1351e:rule.calibration_first_event_rate]].
The value of `threshold.package.auc.test.min` is 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]].
The value of `threshold.package.brier.test.max` is 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]].
The value of `threshold.package.calibration_slope.test.max` is 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The value of `threshold.package.calibration_slope.test.min` is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].

## Appendix A — Claims

Grounding precision 1.0000 before repair (200 of 200 claims verified) and 1.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 31/31; conceptual_soundness 37/37; data_integrity 40/40; outcomes 54/54; sensitivity 14/14; findings 14/14; monitoring 10/10.

Developer claims: The package declares 2 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). See Appendix D.

Excluded numeric tokens (not claims): citation_hash (c07e2c62, d02e3091, 19982ff0, e41b9562); regulatory_section_id (SR26-2:V.1.b, SR26-2:V.1.a, SR26-2:VI.3, SR26-2:V.2); finding_id (F-001, F-002).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The value of `calibration_slope.test` is 0.9778 . | 0.9778 | ratio | calibration_slope |  | eq | `[[art:c07e2c62:calibration_slope.test]]` | verified | 0.9778208366 |
| 2 | summary | The value of `calibration_slope.train` is 1.002 . | 1.002 | ratio | calibration_slope |  | eq | `[[art:d02e3091:calibration_slope.train]]` | verified | 1.002102954 |
| 3 | summary | The value of `challenger.delta_auc` is 0.08022 . | 0.08022 | ratio | challenger |  | eq | `[[art:19982ff0:challenger.delta_auc]]` | verified | 0.08022075314 |
| 4 | summary | The value of `condition_number` is 5.547 . | 5.547 | ratio | condition_number |  | eq | `[[art:e41b9562:condition_number]]` | verified | 5.546934633 |
| 5 | summary | The value of `csi.max` is 0.02363 . | 0.02363 | ratio | csi |  | eq | `[[art:e56cb179:csi.max]]` | verified | 0.02362581795 |
| 6 | summary | The value of `metrics.test.auc` is 0.7446 . | 0.7446 | ratio | metrics |  | eq | `[[art:21514080:metrics.test.auc]]` | verified | 0.7446438276 |
| 7 | summary | The value of `metrics.test.brier` is 0.1494 . | 0.1494 | ratio | metrics |  | eq | `[[art:61f24b2a:metrics.test.brier]]` | verified | 0.1494192524 |
| 8 | summary | The value of `metrics.test.event_rate` is 0.2247 . | 0.2247 | ratio | metrics |  | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 9 | summary | The value of `metrics.test.gini` is 0.4893 . | 0.4893 | ratio | metrics |  | eq | `[[art:6d62a3df:metrics.test.gini]]` | verified | 0.4892876552 |
| 10 | summary | The value of `metrics.test.ks` is 0.41 . | 0.41 | ratio | metrics |  | eq | `[[art:2bfec7c8:metrics.test.ks]]` | verified | 0.4100058429 |
| 11 | summary | The value of `metrics.test.logloss` is 0.4684 . | 0.4684 | ratio | metrics |  | eq | `[[art:92c35262:metrics.test.logloss]]` | verified | 0.4684227558 |
| 12 | summary | The value of `metrics.test.mean_predicted` is 0.2127 . | 0.2127 | ratio | metrics |  | eq | `[[art:5cd71007:metrics.test.mean_predicted]]` | verified | 0.212652548 |
| 13 | summary | The value of `metrics.test.n` is 1500 . | 1500 | ratio | metrics |  | eq | `[[art:64fcf14d:metrics.test.n]]` | verified | 1500 |
| 14 | summary | The value of `metrics.train.auc` is 0.7584 . | 0.7584 | ratio | metrics |  | eq | `[[art:14b38a2b:metrics.train.auc]]` | verified | 0.7584356677 |
| 15 | summary | The value of `metrics.train.brier` is 0.1489 . | 0.1489 | ratio | metrics |  | eq | `[[art:be669a99:metrics.train.brier]]` | verified | 0.1489149059 |
| 16 | summary | The value of `metrics.train.event_rate` is 0.2246 . | 0.2246 | ratio | metrics |  | eq | `[[art:133a5ff8:metrics.train.event_rate]]` | verified | 0.2245714286 |
| 17 | summary | The value of `metrics.train.gini` is 0.5169 . | 0.5169 | ratio | metrics |  | eq | `[[art:b4da846e:metrics.train.gini]]` | verified | 0.5168713353 |
| 18 | summary | The value of `metrics.train.ks` is 0.4451 . | 0.4451 | ratio | metrics |  | eq | `[[art:ccc12729:metrics.train.ks]]` | verified | 0.4451397991 |
| 19 | summary | The value of `metrics.train.logloss` is 0.465 . | 0.465 | ratio | metrics |  | eq | `[[art:4f02e465:metrics.train.logloss]]` | verified | 0.4650014911 |
| 20 | summary | The value of `metrics.train.mean_predicted` is 0.2246 . | 0.2246 | ratio | metrics |  | eq | `[[art:605cce58:metrics.train.mean_predicted]]` | verified | 0.2246226934 |
| 21 | summary | The value of `metrics.train.n` is 3500 . | 3500 | ratio | metrics |  | eq | `[[art:564683ee:metrics.train.n]]` | verified | 3500 |
| 22 | summary | The value of `profile.test.n` is 1500 . | 1500 | ratio | profile |  | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 23 | summary | The value of `profile.train.n` is 3500 . | 3500 | ratio | profile |  | eq | `[[art:2510d49d:profile.train.n]]` | verified | 3500 |
| 24 | summary | The value of `psi.max` is 0.03973 . | 0.03973 | ratio | psi |  | eq | `[[art:9dec5a22:psi.max]]` | verified | 0.03973352816 |
| 25 | summary | The value of `runtime.max_seconds` is 300 . | 300 | ratio | runtime |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 26 | summary | The value of `threshold.package.auc.test.min` is 0.7 . | 0.7 | ratio | threshold |  | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 27 | summary | The value of `threshold.package.brier.test.max` is 0.2 . | 0.2 | ratio | threshold |  | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 28 | summary | The value of `threshold.package.calibration_slope.test.max`… | 1.2 | ratio | threshold |  | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 29 | summary | The value of `threshold.package.calibration_slope.test.min`… | 0.8 | ratio | threshold |  | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 30 | summary | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 31 | summary | The value of `vif.max` is 7.295 . | 7.295 | ratio | vif |  | eq | `[[art:9ae7c45b:vif.max]]` | verified | 7.295299885 |
| 32 | conceptual_soundness | The value of `challenger.auc` is 0.8249 . | 0.8249 | ratio | challenger |  | eq | `[[art:6db67e77:challenger.auc]]` | verified | 0.8248645808 |
| 33 | conceptual_soundness | The value of `challenger.brier` is 0.1248 . | 0.1248 | ratio | challenger |  | eq | `[[art:67796f7f:challenger.brier]]` | verified | 0.1247605055 |
| 34 | conceptual_soundness | The value of `challenger.delta_auc` is 0.08022 . | 0.08022 | ratio | challenger |  | eq | `[[art:19982ff0:challenger.delta_auc]]` | verified | 0.08022075314 |
| 35 | conceptual_soundness | The value of `metrics.test.auc` is 0.7446 . | 0.7446 | ratio | metrics |  | eq | `[[art:21514080:metrics.test.auc]]` | verified | 0.7446438276 |
| 36 | conceptual_soundness | The value of `metrics.test.brier` is 0.1494 . | 0.1494 | ratio | metrics |  | eq | `[[art:61f24b2a:metrics.test.brier]]` | verified | 0.1494192524 |
| 37 | conceptual_soundness | The value of `sign_check.age.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:4116add1:sign_check.age.agrees]]` | verified | 1 |
| 38 | conceptual_soundness | The value of `sign_check.age.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:6172eb93:sign_check.age.coef_sign]]` | verified | -1 |
| 39 | conceptual_soundness | The value of `sign_check.age.univariate_direction` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:66364583:sign_check.age.univariate_direction]]` | verified | -1 |
| 40 | conceptual_soundness | The value of `sign_check.bill_mean_6m.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:89279c3b:sign_check.bill_mean_6m.agrees]]` | verified | 1 |
| 41 | conceptual_soundness | The value of `sign_check.bill_mean_6m.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:cee1a18f:sign_check.bill_mean_6m.coef_sign]]` | verified | -1 |
| 42 | conceptual_soundness | The value of `sign_check.bill_mean_6m.univariate_direction`… | -1 | ratio | sign_check |  | eq | `[[art:23b89c5d:sign_check.bill_mean_6m.univariate_direction]]` | verified | -1 |
| 43 | conceptual_soundness | The value of `sign_check.bill_trend_6m.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:ff3cb24a:sign_check.bill_trend_6m.agrees]]` | verified | 1 |
| 44 | conceptual_soundness | The value of `sign_check.bill_trend_6m.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:7fd8474e:sign_check.bill_trend_6m.coef_sign]]` | verified | -1 |
| 45 | conceptual_soundness | The value of `sign_check.bill_trend_6m.univariate_direction`… | -1 | ratio | sign_check |  | eq | `[[art:a9bff389:sign_check.bill_trend_6m.univariate_direction]]` | verified | -1 |
| 46 | conceptual_soundness | The value of `sign_check.delinq_count_6m.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:a337d16b:sign_check.delinq_count_6m.agrees]]` | verified | 1 |
| 47 | conceptual_soundness | The value of `sign_check.delinq_count_6m.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:17afb6f9:sign_check.delinq_count_6m.coef_sign]]` | verified | 1 |
| 48 | conceptual_soundness | The value of `sign_check.delinq_count_6m.univariate_directio… | 1 | ratio | sign_check |  | eq | `[[art:549e904e:sign_check.delinq_count_6m.univariate_direction]]` | verified | 1 |
| 49 | conceptual_soundness | The value of `sign_check.delinq_last.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:a8ba9372:sign_check.delinq_last.agrees]]` | verified | 1 |
| 50 | conceptual_soundness | The value of `sign_check.delinq_last.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:50d352f8:sign_check.delinq_last.coef_sign]]` | verified | 1 |
| 51 | conceptual_soundness | The value of `sign_check.delinq_last.univariate_direction` i… | 1 | ratio | sign_check |  | eq | `[[art:a78648ba:sign_check.delinq_last.univariate_direction]]` | verified | 1 |
| 52 | conceptual_soundness | The value of `sign_check.delinq_max_6m.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:c946359c:sign_check.delinq_max_6m.agrees]]` | verified | 0 |
| 53 | conceptual_soundness | The value of `sign_check.delinq_max_6m.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]]` | verified | -1 |
| 54 | conceptual_soundness | The value of `sign_check.delinq_max_6m.univariate_direction`… | 1 | ratio | sign_check |  | eq | `[[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]]` | verified | 1 |
| 55 | conceptual_soundness | The value of `sign_check.limit_bal.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:0278aad1:sign_check.limit_bal.agrees]]` | verified | 0 |
| 56 | conceptual_soundness | The value of `sign_check.limit_bal.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:6af6aef2:sign_check.limit_bal.coef_sign]]` | verified | 1 |
| 57 | conceptual_soundness | The value of `sign_check.limit_bal.univariate_direction` is… | -1 | ratio | sign_check |  | eq | `[[art:56d284d6:sign_check.limit_bal.univariate_direction]]` | verified | -1 |
| 58 | conceptual_soundness | The value of `sign_check.n_disagreements` is 3 . | 3 | ratio | sign_check |  | eq | `[[art:e223cd4a:sign_check.n_disagreements]]` | verified | 3 |
| 59 | conceptual_soundness | The value of `sign_check.pay_ratio_last.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:79abee77:sign_check.pay_ratio_last.agrees]]` | verified | 0 |
| 60 | conceptual_soundness | The value of `sign_check.pay_ratio_last.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:f018263e:sign_check.pay_ratio_last.coef_sign]]` | verified | 1 |
| 61 | conceptual_soundness | The value of `sign_check.pay_ratio_last.univariate_direction… | -1 | ratio | sign_check |  | eq | `[[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]]` | verified | -1 |
| 62 | conceptual_soundness | The value of `sign_check.pay_ratio_mean_6m.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:7e9a76ca:sign_check.pay_ratio_mean_6m.agrees]]` | verified | 1 |
| 63 | conceptual_soundness | The value of `sign_check.pay_ratio_mean_6m.coef_sign` is -1… | -1 | ratio | sign_check |  | eq | `[[art:077bb6b2:sign_check.pay_ratio_mean_6m.coef_sign]]` | verified | -1 |
| 64 | conceptual_soundness | The value of `sign_check.pay_ratio_mean_6m.univariate_direct… | -1 | ratio | sign_check |  | eq | `[[art:24dcef24:sign_check.pay_ratio_mean_6m.univariate_direction]]` | verified | -1 |
| 65 | conceptual_soundness | The value of `sign_check.utilisation.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:d0c9a130:sign_check.utilisation.agrees]]` | verified | 1 |
| 66 | conceptual_soundness | The value of `sign_check.utilisation.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:85badc3c:sign_check.utilisation.coef_sign]]` | verified | 1 |
| 67 | conceptual_soundness | The value of `sign_check.utilisation.univariate_direction` i… | 1 | ratio | sign_check |  | eq | `[[art:f0995196:sign_check.utilisation.univariate_direction]]` | verified | 1 |
| 68 | conceptual_soundness | The value of `threshold.E1.delta_auc` is 0.03 . | 0.03 | ratio | threshold |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 69 | data_integrity | The value of `csi.age` is 0.0009476 . | 0.0009476 | ratio | csi |  | eq | `[[art:a78e58f6:csi.age]]` | verified | 0.0009475732594 |
| 70 | data_integrity | The value of `csi.bill_mean_6m` is 0.002369 . | 0.002369 | ratio | csi |  | eq | `[[art:48df6cc9:csi.bill_mean_6m]]` | verified | 0.002369326368 |
| 71 | data_integrity | The value of `csi.bill_trend_6m` is 0.00633 . | 0.00633 | ratio | csi |  | eq | `[[art:59948e6d:csi.bill_trend_6m]]` | verified | 0.006329590221 |
| 72 | data_integrity | The value of `csi.delinq_count_6m` is 0.002449 . | 0.002449 | ratio | csi |  | eq | `[[art:69346f52:csi.delinq_count_6m]]` | verified | 0.002448902116 |
| 73 | data_integrity | The value of `csi.delinq_last` is 0.02363 . | 0.02363 | ratio | csi |  | eq | `[[art:5babe364:csi.delinq_last]]` | verified | 0.02362581795 |
| 74 | data_integrity | The value of `csi.delinq_max_6m` is 0.0008965 . | 0.0008965 | ratio | csi |  | eq | `[[art:7244960d:csi.delinq_max_6m]]` | verified | 0.0008964784296 |
| 75 | data_integrity | The value of `csi.limit_bal` is 0.001211 . | 0.001211 | ratio | csi |  | eq | `[[art:5b77b34b:csi.limit_bal]]` | verified | 0.001211461258 |
| 76 | data_integrity | The value of `csi.max` is 0.02363 . | 0.02363 | ratio | csi |  | eq | `[[art:e56cb179:csi.max]]` | verified | 0.02362581795 |
| 77 | data_integrity | The value of `csi.pay_ratio_last` is 0.004524 . | 0.004524 | ratio | csi |  | eq | `[[art:5eec4717:csi.pay_ratio_last]]` | verified | 0.004524002665 |
| 78 | data_integrity | The value of `csi.pay_ratio_mean_6m` is 0.001768 . | 0.001768 | ratio | csi |  | eq | `[[art:f567818e:csi.pay_ratio_mean_6m]]` | verified | 0.001768345794 |
| 79 | data_integrity | The value of `csi.utilisation` is 0.004042 . | 0.004042 | ratio | csi |  | eq | `[[art:10f0f9e7:csi.utilisation]]` | verified | 0.004041856699 |
| 80 | data_integrity | The value of `leakage.duplicates.train` is 0 . | 0 | ratio | leakage |  | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 81 | data_integrity | The value of `leakage.name_screen.n_matched` is 0 . | 0 | ratio | leakage |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 82 | data_integrity | The value of `leakage.overlap` is 0 . | 0 | ratio | leakage |  | eq | `[[art:4c9fcd09:leakage.overlap]]` | verified | 0 |
| 83 | data_integrity | The value of `leakage.overlap.features` is 0 . | 0 | ratio | leakage |  | eq | `[[art:0fec8048:leakage.overlap.features]]` | verified | 0 |
| 84 | data_integrity | The value of `leakage.overlap.ids` is 0 . | 0 | ratio | leakage |  | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 85 | data_integrity | The value of `leakage.target_corr.max_single_feature_auc` is… | 0.6831 | ratio | leakage |  | eq | `[[art:fd829fc4:leakage.target_corr.max_single_feature_auc]]` | verified | 0.6831414154 |
| 86 | data_integrity | The value of `leakage.timing.n_flagged` is 0 . | 0 | ratio | leakage |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 87 | data_integrity | The value of `profile.test.missing.max` is 0.3 . | 0.3 | ratio | profile |  | eq | `[[art:7b5c0c01:profile.test.missing.max]]` | verified | 0.3 |
| 88 | data_integrity | The value of `profile.test.n` is 1500 . | 1500 | ratio | profile |  | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 89 | data_integrity | The value of `profile.train.missing.max` is 0 . | 0 | ratio | profile |  | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 90 | data_integrity | The value of `profile.train.n` is 3500 . | 3500 | ratio | profile |  | eq | `[[art:2510d49d:profile.train.n]]` | verified | 3500 |
| 91 | data_integrity | The value of `psi.age` is 0.008124 . | 0.008124 | ratio | psi |  | eq | `[[art:f9255a0a:psi.age]]` | verified | 0.008124281436 |
| 92 | data_integrity | The value of `psi.bill_mean_6m` is 0.007124 . | 0.007124 | ratio | psi |  | eq | `[[art:028e4281:psi.bill_mean_6m]]` | verified | 0.007124196275 |
| 93 | data_integrity | The value of `psi.bill_trend_6m` is 0.00958 . | 0.00958 | ratio | psi |  | eq | `[[art:c247a6f2:psi.bill_trend_6m]]` | verified | 0.009579614525 |
| 94 | data_integrity | The value of `psi.delinq_count_6m` is 0.002069 . | 0.002069 | ratio | psi |  | eq | `[[art:61491d02:psi.delinq_count_6m]]` | verified | 0.002069275496 |
| 95 | data_integrity | The value of `psi.delinq_last` is 0.00285 . | 0.00285 | ratio | psi |  | eq | `[[art:03bd52e7:psi.delinq_last]]` | verified | 0.002849633848 |
| 96 | data_integrity | The value of `psi.delinq_max_6m` is 0.005498 . | 0.005498 | ratio | psi |  | eq | `[[art:7a82e7f3:psi.delinq_max_6m]]` | verified | 0.005498249408 |
| 97 | data_integrity | The value of `psi.limit_bal` is 0.01095 . | 0.01095 | ratio | psi |  | eq | `[[art:601cdba2:psi.limit_bal]]` | verified | 0.01095273358 |
| 98 | data_integrity | The value of `psi.max` is 0.03973 . | 0.03973 | ratio | psi |  | eq | `[[art:9dec5a22:psi.max]]` | verified | 0.03973352816 |
| 99 | data_integrity | The value of `psi.pay_ratio_last` is 0.005424 . | 0.005424 | ratio | psi |  | eq | `[[art:4f6eddcb:psi.pay_ratio_last]]` | verified | 0.005423736698 |
| 100 | data_integrity | The value of `psi.pay_ratio_mean_6m` is 0.0055 . | 0.0055 | ratio | psi |  | eq | `[[art:2c5baeb2:psi.pay_ratio_mean_6m]]` | verified | 0.005500252946 |
| 101 | data_integrity | The value of `psi.utilisation` is 0.004244 . | 0.004244 | ratio | psi |  | eq | `[[art:451e0780:psi.utilisation]]` | verified | 0.0042440485 |
| 102 | data_integrity | The value of `psi.y_score` is 0.03973 . | 0.03973 | ratio | psi |  | eq | `[[art:828961f6:psi.y_score]]` | verified | 0.03973352816 |
| 103 | data_integrity | The value of `threshold.D1.missing_gap` is 0.1 . | 0.1 | ratio | threshold |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 104 | data_integrity | The value of `threshold.L1.single_feature_auc` is 0.9 . | 0.9 | ratio | threshold |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 105 | data_integrity | The value of `threshold.L2.overlap` is 0.005 . | 0.005 | ratio | threshold |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 106 | data_integrity | The value of `threshold.L2.overlap.features_effective` is 0.… | 0.005 | ratio | threshold |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 107 | data_integrity | The value of `threshold.S1.psi` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 108 | data_integrity | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 109 | outcomes | The value of `calibration.mean_rel_gap.test` is 0.05348 . | 0.05348 | ratio | calibration |  | eq | `[[art:64a3c99e:calibration.mean_rel_gap.test]]` | verified | 0.05347530574 |
| 110 | outcomes | The value of `calibration.mean_rel_gap.train` is 0.0002283 . | 0.0002283 | ratio | calibration |  | eq | `[[art:53738d45:calibration.mean_rel_gap.train]]` | verified | 0.0002282786273 |
| 111 | outcomes | The value of `calibration_intercept.test` is 0.05554 . | 0.05554 | ratio | calibration_intercept |  | eq | `[[art:f4d4ef2b:calibration_intercept.test]]` | verified | 0.05553669436 |
| 112 | outcomes | The value of `calibration_intercept.train` is 0.002062 . | 0.002062 | ratio | calibration_intercept |  | eq | `[[art:ed381a81:calibration_intercept.train]]` | verified | 0.002061562686 |
| 113 | outcomes | The value of `calibration_slope.test` is 0.9778 . | 0.9778 | ratio | calibration_slope |  | eq | `[[art:c07e2c62:calibration_slope.test]]` | verified | 0.9778208366 |
| 114 | outcomes | The value of `calibration_slope.train` is 1.002 . | 1.002 | ratio | calibration_slope |  | eq | `[[art:d02e3091:calibration_slope.train]]` | verified | 1.002102954 |
| 115 | outcomes | The value of `deciles.test.top2_capture` is 0.4688 . | 0.4688 | ratio | deciles |  | eq | `[[art:17d2971c:deciles.test.top2_capture]]` | verified | 0.46884273 |
| 116 | outcomes | The value of `deciles.train.top2_capture` is 0.4517 . | 0.4517 | ratio | deciles |  | eq | `[[art:1d20c762:deciles.train.top2_capture]]` | verified | 0.451653944 |
| 117 | outcomes | The value of `metrics.test.auc` is 0.7446 . | 0.7446 | ratio | metrics |  | eq | `[[art:21514080:metrics.test.auc]]` | verified | 0.7446438276 |
| 118 | outcomes | The value of `metrics.test.brier` is 0.1494 . | 0.1494 | ratio | metrics |  | eq | `[[art:61f24b2a:metrics.test.brier]]` | verified | 0.1494192524 |
| 119 | outcomes | The value of `metrics.test.event_rate` is 0.2247 . | 0.2247 | ratio | metrics |  | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 120 | outcomes | The value of `metrics.test.gini` is 0.4893 . | 0.4893 | ratio | metrics |  | eq | `[[art:6d62a3df:metrics.test.gini]]` | verified | 0.4892876552 |
| 121 | outcomes | The value of `metrics.test.ks` is 0.41 . | 0.41 | ratio | metrics |  | eq | `[[art:2bfec7c8:metrics.test.ks]]` | verified | 0.4100058429 |
| 122 | outcomes | The value of `metrics.test.logloss` is 0.4684 . | 0.4684 | ratio | metrics |  | eq | `[[art:92c35262:metrics.test.logloss]]` | verified | 0.4684227558 |
| 123 | outcomes | The value of `metrics.test.mean_predicted` is 0.2127 . | 0.2127 | ratio | metrics |  | eq | `[[art:5cd71007:metrics.test.mean_predicted]]` | verified | 0.212652548 |
| 124 | outcomes | The value of `metrics.test.n` is 1500 . | 1500 | ratio | metrics |  | eq | `[[art:64fcf14d:metrics.test.n]]` | verified | 1500 |
| 125 | outcomes | The value of `metrics.train.auc` is 0.7584 . | 0.7584 | ratio | metrics |  | eq | `[[art:14b38a2b:metrics.train.auc]]` | verified | 0.7584356677 |
| 126 | outcomes | The value of `metrics.train.brier` is 0.1489 . | 0.1489 | ratio | metrics |  | eq | `[[art:be669a99:metrics.train.brier]]` | verified | 0.1489149059 |
| 127 | outcomes | The value of `metrics.train.event_rate` is 0.2246 . | 0.2246 | ratio | metrics |  | eq | `[[art:133a5ff8:metrics.train.event_rate]]` | verified | 0.2245714286 |
| 128 | outcomes | The value of `metrics.train.gini` is 0.5169 . | 0.5169 | ratio | metrics |  | eq | `[[art:b4da846e:metrics.train.gini]]` | verified | 0.5168713353 |
| 129 | outcomes | The value of `metrics.train.ks` is 0.4451 . | 0.4451 | ratio | metrics |  | eq | `[[art:ccc12729:metrics.train.ks]]` | verified | 0.4451397991 |
| 130 | outcomes | The value of `metrics.train.logloss` is 0.465 . | 0.465 | ratio | metrics |  | eq | `[[art:4f02e465:metrics.train.logloss]]` | verified | 0.4650014911 |
| 131 | outcomes | The value of `metrics.train.mean_predicted` is 0.2246 . | 0.2246 | ratio | metrics |  | eq | `[[art:605cce58:metrics.train.mean_predicted]]` | verified | 0.2246226934 |
| 132 | outcomes | The value of `metrics.train.n` is 3500 . | 3500 | ratio | metrics |  | eq | `[[art:564683ee:metrics.train.n]]` | verified | 3500 |
| 133 | outcomes | The value of `psi.age` is 0.008124 . | 0.008124 | ratio | psi |  | eq | `[[art:f9255a0a:psi.age]]` | verified | 0.008124281436 |
| 134 | outcomes | The value of `psi.bill_mean_6m` is 0.007124 . | 0.007124 | ratio | psi |  | eq | `[[art:028e4281:psi.bill_mean_6m]]` | verified | 0.007124196275 |
| 135 | outcomes | The value of `psi.bill_trend_6m` is 0.00958 . | 0.00958 | ratio | psi |  | eq | `[[art:c247a6f2:psi.bill_trend_6m]]` | verified | 0.009579614525 |
| 136 | outcomes | The value of `psi.delinq_count_6m` is 0.002069 . | 0.002069 | ratio | psi |  | eq | `[[art:61491d02:psi.delinq_count_6m]]` | verified | 0.002069275496 |
| 137 | outcomes | The value of `psi.delinq_last` is 0.00285 . | 0.00285 | ratio | psi |  | eq | `[[art:03bd52e7:psi.delinq_last]]` | verified | 0.002849633848 |
| 138 | outcomes | The value of `psi.delinq_max_6m` is 0.005498 . | 0.005498 | ratio | psi |  | eq | `[[art:7a82e7f3:psi.delinq_max_6m]]` | verified | 0.005498249408 |
| 139 | outcomes | The value of `psi.limit_bal` is 0.01095 . | 0.01095 | ratio | psi |  | eq | `[[art:601cdba2:psi.limit_bal]]` | verified | 0.01095273358 |
| 140 | outcomes | The value of `psi.max` is 0.03973 . | 0.03973 | ratio | psi |  | eq | `[[art:9dec5a22:psi.max]]` | verified | 0.03973352816 |
| 141 | outcomes | The value of `psi.pay_ratio_last` is 0.005424 . | 0.005424 | ratio | psi |  | eq | `[[art:4f6eddcb:psi.pay_ratio_last]]` | verified | 0.005423736698 |
| 142 | outcomes | The value of `psi.pay_ratio_mean_6m` is 0.0055 . | 0.0055 | ratio | psi |  | eq | `[[art:2c5baeb2:psi.pay_ratio_mean_6m]]` | verified | 0.005500252946 |
| 143 | outcomes | The value of `psi.utilisation` is 0.004244 . | 0.004244 | ratio | psi |  | eq | `[[art:451e0780:psi.utilisation]]` | verified | 0.0042440485 |
| 144 | outcomes | The value of `psi.y_score` is 0.03973 . | 0.03973 | ratio | psi |  | eq | `[[art:828961f6:psi.y_score]]` | verified | 0.03973352816 |
| 145 | outcomes | The value of `rule.calibration_first_event_rate` is 0.05 . | 0.05 | ratio | rule |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 146 | outcomes | The value of `threshold.C1.calibration_slope.max` is 1.2 . | 1.2 | ratio | threshold |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 147 | outcomes | The value of `threshold.C1.calibration_slope.min` is 0.8 . | 0.8 | ratio | threshold |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 148 | outcomes | The value of `threshold.C1.mean_ratio_rel` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 149 | outcomes | The value of `threshold.D1.missing_gap` is 0.1 . | 0.1 | ratio | threshold |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 150 | outcomes | The value of `threshold.E1.delta_auc` is 0.03 . | 0.03 | ratio | threshold |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 151 | outcomes | The value of `threshold.L1.single_feature_auc` is 0.9 . | 0.9 | ratio | threshold |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 152 | outcomes | The value of `threshold.L2.overlap` is 0.005 . | 0.005 | ratio | threshold |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 153 | outcomes | The value of `threshold.L2.overlap.features_effective` is 0.… | 0.005 | ratio | threshold |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 154 | outcomes | The value of `threshold.M1.condition_number` is 30 . | 30 | ratio | threshold |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 155 | outcomes | The value of `threshold.M1.vif` is 10 . | 10 | ratio | threshold |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 156 | outcomes | The value of `threshold.O1.auc_gap` is 0.08 . | 0.08 | ratio | threshold |  | eq | `[[art:630f28f4:threshold.O1.auc_gap]]` | verified | 0.08 |
| 157 | outcomes | The value of `threshold.S1.psi` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 158 | outcomes | The value of `threshold.package.auc.test.min` is 0.7 . | 0.7 | ratio | threshold |  | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 159 | outcomes | The value of `threshold.package.brier.test.max` is 0.2 . | 0.2 | ratio | threshold |  | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 160 | outcomes | The value of `threshold.package.calibration_slope.test.max`… | 1.2 | ratio | threshold |  | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 161 | outcomes | The value of `threshold.package.calibration_slope.test.min`… | 0.8 | ratio | threshold |  | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 162 | outcomes | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 163 | sensitivity | The value of `condition_number` is 5.547 . | 5.547 | ratio | condition_number |  | eq | `[[art:e41b9562:condition_number]]` | verified | 5.546934633 |
| 164 | sensitivity | The value of `threshold.M1.condition_number` is 30 . | 30 | ratio | threshold |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 165 | sensitivity | The value of `threshold.M1.vif` is 10 . | 10 | ratio | threshold |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 166 | sensitivity | The value of `vif.age` is 1.002 . | 1.002 | ratio | vif |  | eq | `[[art:74c06cad:vif.age]]` | verified | 1.001957997 |
| 167 | sensitivity | The value of `vif.bill_mean_6m` is 7.295 . | 7.295 | ratio | vif |  | eq | `[[art:f0a2f865:vif.bill_mean_6m]]` | verified | 7.295299885 |
| 168 | sensitivity | The value of `vif.bill_trend_6m` is 1.201 . | 1.201 | ratio | vif |  | eq | `[[art:9356a256:vif.bill_trend_6m]]` | verified | 1.201449441 |
| 169 | sensitivity | The value of `vif.delinq_count_6m` is 2.561 . | 2.561 | ratio | vif |  | eq | `[[art:38974def:vif.delinq_count_6m]]` | verified | 2.561484187 |
| 170 | sensitivity | The value of `vif.delinq_last` is 1.412 . | 1.412 | ratio | vif |  | eq | `[[art:48733638:vif.delinq_last]]` | verified | 1.411555667 |
| 171 | sensitivity | The value of `vif.delinq_max_6m` is 2.408 . | 2.408 | ratio | vif |  | eq | `[[art:71aaaf11:vif.delinq_max_6m]]` | verified | 2.40773 |
| 172 | sensitivity | The value of `vif.limit_bal` is 4.803 . | 4.803 | ratio | vif |  | eq | `[[art:ddfdcc3c:vif.limit_bal]]` | verified | 4.803401129 |
| 173 | sensitivity | The value of `vif.max` is 7.295 . | 7.295 | ratio | vif |  | eq | `[[art:9ae7c45b:vif.max]]` | verified | 7.295299885 |
| 174 | sensitivity | The value of `vif.pay_ratio_last` is 7.264 . | 7.264 | ratio | vif |  | eq | `[[art:c2de8dfe:vif.pay_ratio_last]]` | verified | 7.264342098 |
| 175 | sensitivity | The value of `vif.pay_ratio_mean_6m` is 7.259 . | 7.259 | ratio | vif |  | eq | `[[art:e39c3e82:vif.pay_ratio_mean_6m]]` | verified | 7.25926398 |
| 176 | sensitivity | The value of `vif.utilisation` is 3.215 . | 3.215 | ratio | vif |  | eq | `[[art:536fdb6f:vif.utilisation]]` | verified | 3.215148369 |
| 177 | findings | The value of `challenger.auc` is 0.8249 . | 0.8249 | ratio | challenger |  | eq | `[[art:6db67e77:challenger.auc]]` | verified | 0.8248645808 |
| 178 | findings | The value of `challenger.delta_auc` is 0.08022 . | 0.08022 | ratio | challenger |  | eq | `[[art:19982ff0:challenger.delta_auc]]` | verified | 0.08022075314 |
| 179 | findings | The value of `metrics.test.auc` is 0.7446 . | 0.7446 | ratio | metrics |  | eq | `[[art:21514080:metrics.test.auc]]` | verified | 0.7446438276 |
| 180 | findings | The value of `sign_check.delinq_max_6m.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:c946359c:sign_check.delinq_max_6m.agrees]]` | verified | 0 |
| 181 | findings | The value of `sign_check.delinq_max_6m.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]]` | verified | -1 |
| 182 | findings | The value of `sign_check.delinq_max_6m.univariate_direction`… | 1 | ratio | sign_check |  | eq | `[[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]]` | verified | 1 |
| 183 | findings | The value of `sign_check.limit_bal.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:0278aad1:sign_check.limit_bal.agrees]]` | verified | 0 |
| 184 | findings | The value of `sign_check.limit_bal.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:6af6aef2:sign_check.limit_bal.coef_sign]]` | verified | 1 |
| 185 | findings | The value of `sign_check.limit_bal.univariate_direction` is… | -1 | ratio | sign_check |  | eq | `[[art:56d284d6:sign_check.limit_bal.univariate_direction]]` | verified | -1 |
| 186 | findings | The value of `sign_check.pay_ratio_last.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:79abee77:sign_check.pay_ratio_last.agrees]]` | verified | 0 |
| 187 | findings | The value of `sign_check.pay_ratio_last.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:f018263e:sign_check.pay_ratio_last.coef_sign]]` | verified | 1 |
| 188 | findings | The value of `sign_check.pay_ratio_last.univariate_direction… | -1 | ratio | sign_check |  | eq | `[[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]]` | verified | -1 |
| 189 | findings | The value of `threshold.D1.missing_gap` is 0.1 . | 0.1 | ratio | threshold |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 190 | findings | The value of `threshold.E1.delta_auc` is 0.03 . | 0.03 | ratio | threshold |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 191 | monitoring | The value of `calibration_slope.test` is 0.9778 . | 0.9778 | ratio | calibration_slope |  | eq | `[[art:c07e2c62:calibration_slope.test]]` | verified | 0.9778208366 |
| 192 | monitoring | The value of `metrics.test.auc` is 0.7446 . | 0.7446 | ratio | metrics |  | eq | `[[art:21514080:metrics.test.auc]]` | verified | 0.7446438276 |
| 193 | monitoring | The value of `metrics.test.brier` is 0.1494 . | 0.1494 | ratio | metrics |  | eq | `[[art:61f24b2a:metrics.test.brier]]` | verified | 0.1494192524 |
| 194 | monitoring | The value of `psi.max` is 0.03973 . | 0.03973 | ratio | psi |  | eq | `[[art:9dec5a22:psi.max]]` | verified | 0.03973352816 |
| 195 | monitoring | The value of `rule.calibration_first_event_rate` is 0.05 . | 0.05 | ratio | rule |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 196 | monitoring | The value of `threshold.package.auc.test.min` is 0.7 . | 0.7 | ratio | threshold |  | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 197 | monitoring | The value of `threshold.package.brier.test.max` is 0.2 . | 0.2 | ratio | threshold |  | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 198 | monitoring | The value of `threshold.package.calibration_slope.test.max`… | 1.2 | ratio | threshold |  | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 199 | monitoring | The value of `threshold.package.calibration_slope.test.min`… | 0.8 | ratio | threshold |  | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 200 | monitoring | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |

## Appendix B — Artifact index

The store holds 159 artifacts; the 128 this report cites or rests a finding on are indexed here.

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
| `metrics.train.auc` | `14b38a2b` | scalar | 0.7584356677 | auc on train, recomputed by quaestor |
| `metrics.train.brier` | `be669a99` | scalar | 0.1489149059 | brier on train, recomputed by quaestor |
| `metrics.train.event_rate` | `133a5ff8` | scalar | 0.2245714286 | event_rate on train, recomputed by quaestor |
| `metrics.train.gini` | `b4da846e` | scalar | 0.5168713353 | gini on train, recomputed by quaestor |
| `metrics.train.ks` | `ccc12729` | scalar | 0.4451397991 | ks on train, recomputed by quaestor |
| `metrics.train.logloss` | `4f02e465` | scalar | 0.4650014911 | logloss on train, recomputed by quaestor |
| `metrics.train.mean_predicted` | `605cce58` | scalar | 0.2246226934 | mean_predicted on train, recomputed by quaestor |
| `metrics.train.n` | `564683ee` | scalar | 3500 | n on train, recomputed by quaestor |
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
| tool calls | 13 (run_model 1, profile_data 1, compute_metrics 1, check_leakage 1, check_collinearity 1, challenger_compare 1, retrieve_guidance 7) |
| plan steps (bounded loop) | 0 |
| LLM calls | 0 () |
| re-asks | 0 |
| repair rounds | 0 |
| tokens in / out | 0 / 0 |
| notional cost (USD) | 0.0000 |
| wall-clock (s) | 1.49 |
| subject run (s) | 1.18 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | fake |
| model | none: no model answered |
| run id | credit_default-rules_only-20260918T065317Z-bd5861e9 |

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
