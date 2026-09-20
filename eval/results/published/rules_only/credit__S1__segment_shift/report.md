---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: rules_only
model: fake
run_id: credit_default-rules_only-20260918T065332Z-bd5861e9
data_mode: synthetic
synthetic_n: 5000
grounding_precision_pre: 1.0000
grounding_precision_post: 1.0000
n_claims: 203
n_findings_by_severity: {high: 1, medium: 1, low: 1, info: 0}
generated: "2026-09-18T06:53:32Z"
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
The value of `calibration_slope.test` is 1.008 [[art:b918ce48:calibration_slope.test]].
The value of `calibration_slope.train` is 1.004 [[art:4c796937:calibration_slope.train]].
The value of `challenger.delta_auc` is 0.06961 [[art:ce2a1ab8:challenger.delta_auc]].
The value of `condition_number` is 5.647 [[art:81de583f:condition_number]].
The value of `csi.max` is 0.06466 [[art:b2e113ad:csi.max]].
The value of `metrics.test.auc` is 0.7525 [[art:2a5ea4af:metrics.test.auc]].
The value of `metrics.test.brier` is 0.1524 [[art:7da5c034:metrics.test.brier]].
The value of `metrics.test.event_rate` is 0.2247 [[art:9209d200:metrics.test.event_rate]].
The value of `metrics.test.gini` is 0.505 [[art:f00e967c:metrics.test.gini]].
The value of `metrics.test.ks` is 0.4306 [[art:c3789b0d:metrics.test.ks]].
The value of `metrics.test.logloss` is 0.4717 [[art:46b23175:metrics.test.logloss]].
The value of `metrics.test.mean_predicted` is 0.2122 [[art:f06b1724:metrics.test.mean_predicted]].
The value of `metrics.test.n` is 1500 [[art:64fcf14d:metrics.test.n]].
The value of `metrics.train.auc` is 0.7599 [[art:3d5f30fa:metrics.train.auc]].
The value of `metrics.train.brier` is 0.1636 [[art:46973259:metrics.train.brier]].
The value of `metrics.train.event_rate` is 0.2437 [[art:25e9afa5:metrics.train.event_rate]].
The value of `metrics.train.gini` is 0.5198 [[art:3198b731:metrics.train.gini]].
The value of `metrics.train.ks` is 0.4559 [[art:c2dc79a4:metrics.train.ks]].
The value of `metrics.train.logloss` is 0.4967 [[art:73e399ed:metrics.train.logloss]].
The value of `metrics.train.mean_predicted` is 0.2437 [[art:7bfcb165:metrics.train.mean_predicted]].
The value of `metrics.train.n` is 1789 [[art:eae7a256:metrics.train.n]].
The value of `profile.test.n` is 1500 [[art:2193cf5f:profile.test.n]].
The value of `profile.train.n` is 1789 [[art:0f89a4f1:profile.train.n]].
The value of `psi.max` is 1.196 [[art:5a6a40fb:psi.max]].
The value of `runtime.max_seconds` is 300 [[art:2ad8d1a5:runtime.max_seconds]].
The value of `threshold.package.auc.test.min` is 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]].
The value of `threshold.package.brier.test.max` is 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]].
The value of `threshold.package.calibration_slope.test.max` is 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The value of `threshold.package.calibration_slope.test.min` is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
The value of `vif.max` is 7.662 [[art:3a027a9e:vif.max]].

## 2. Conceptual soundness

This section follows the model risk management guidance at [[reg:SR26-2:V.1.a]].
The value of `ablation.age.delta_auc` is 0.001077 [[art:223939e9:ablation.age.delta_auc]].
The value of `ablation.baseline_auc` is 0.7525 [[art:6b970cd1:ablation.baseline_auc]].
The value of `ablation.bill_trend_6m.delta_auc` is 0.007121 [[art:b56721dc:ablation.bill_trend_6m.delta_auc]].
The value of `ablation.delinq_count_6m.delta_auc` is -0.0001378 [[art:478e5417:ablation.delinq_count_6m.delta_auc]].
The value of `ablation.delinq_last.delta_auc` is -0.09255 [[art:562511ba:ablation.delinq_last.delta_auc]].
The value of `ablation.delinq_max_6m.delta_auc` is 0.00008165 [[art:1d41dd41:ablation.delinq_max_6m.delta_auc]].
The value of `ablation.limit_bal.delta_auc` is 0.004218 [[art:6f97302c:ablation.limit_bal.delta_auc]].
The value of `ablation.pay_ratio_last.delta_auc` is 0.003621 [[art:cc45633b:ablation.pay_ratio_last.delta_auc]].
The value of `ablation.pay_ratio_mean_6m.delta_auc` is 0.007129 [[art:53d51307:ablation.pay_ratio_mean_6m.delta_auc]].
The value of `ablation.utilisation.delta_auc` is -0.02697 [[art:2a417d0d:ablation.utilisation.delta_auc]].
The value of `challenger.auc` is 0.8221 [[art:9a3da49b:challenger.auc]].
The value of `challenger.brier` is 0.125 [[art:01fa79a9:challenger.brier]].
The value of `challenger.delta_auc` is 0.06961 [[art:ce2a1ab8:challenger.delta_auc]].
The value of `metrics.test.auc` is 0.7525 [[art:2a5ea4af:metrics.test.auc]].
The value of `metrics.test.brier` is 0.1524 [[art:7da5c034:metrics.test.brier]].
The value of `sign_check.age.agrees` is 1 [[art:4116add1:sign_check.age.agrees]].
The value of `sign_check.age.coef_sign` is -1 [[art:6172eb93:sign_check.age.coef_sign]].
The value of `sign_check.age.univariate_direction` is -1 [[art:66364583:sign_check.age.univariate_direction]].
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
The value of `sign_check.limit_bal.agrees` is 1 [[art:103d99fb:sign_check.limit_bal.agrees]].
The value of `sign_check.limit_bal.coef_sign` is -1 [[art:a6d01381:sign_check.limit_bal.coef_sign]].
The value of `sign_check.limit_bal.univariate_direction` is -1 [[art:56d284d6:sign_check.limit_bal.univariate_direction]].
The value of `sign_check.n_disagreements` is 2 [[art:66ce738a:sign_check.n_disagreements]].
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
The value of `csi.age` is 0.0009235 [[art:c3bb7175:csi.age]].
The value of `csi.bill_trend_6m` is 0.002501 [[art:6d4f0d7b:csi.bill_trend_6m]].
The value of `csi.delinq_count_6m` is 0.002246 [[art:7ee6f613:csi.delinq_count_6m]].
The value of `csi.delinq_last` is 0.01505 [[art:4e9b1ec3:csi.delinq_last]].
The value of `csi.delinq_max_6m` is 0.0001002 [[art:f775c7df:csi.delinq_max_6m]].
The value of `csi.limit_bal` is 0.06466 [[art:44fa93ba:csi.limit_bal]].
The value of `csi.max` is 0.06466 [[art:b2e113ad:csi.max]].
The value of `csi.pay_ratio_last` is 0.001222 [[art:547b3f3e:csi.pay_ratio_last]].
The value of `csi.pay_ratio_mean_6m` is 0.00576 [[art:d7a50342:csi.pay_ratio_mean_6m]].
The value of `csi.utilisation` is 0.005503 [[art:b506bc4b:csi.utilisation]].
The value of `leakage.duplicates.train` is 0 [[art:4474c227:leakage.duplicates.train]].
The value of `leakage.name_screen.n_matched` is 0 [[art:407e62be:leakage.name_screen.n_matched]].
The value of `leakage.overlap` is 0 [[art:4c9fcd09:leakage.overlap]].
The value of `leakage.overlap.features` is 0 [[art:0fec8048:leakage.overlap.features]].
The value of `leakage.overlap.ids` is 0 [[art:63d37fc5:leakage.overlap.ids]].
The value of `leakage.target_corr.max_single_feature_auc` is 0.6626 [[art:4c34a594:leakage.target_corr.max_single_feature_auc]].
The value of `leakage.timing.n_flagged` is 0 [[art:742bcd24:leakage.timing.n_flagged]].
The value of `profile.test.missing.max` is 0 [[art:f813848d:profile.test.missing.max]].
The value of `profile.test.n` is 1500 [[art:2193cf5f:profile.test.n]].
The value of `profile.train.missing.max` is 0 [[art:050a3099:profile.train.missing.max]].
The value of `profile.train.n` is 1789 [[art:0f89a4f1:profile.train.n]].
The value of `psi.age` is 0.005867 [[art:c35c14b6:psi.age]].
The value of `psi.bill_trend_6m` is 0.1334 [[art:41ee0c35:psi.bill_trend_6m]].
The value of `psi.delinq_count_6m` is 0.002943 [[art:f5c55e59:psi.delinq_count_6m]].
The value of `psi.delinq_last` is 0.0008258 [[art:da6a07f2:psi.delinq_last]].
The value of `psi.delinq_max_6m` is 0.007293 [[art:85162d6e:psi.delinq_max_6m]].
The value of `psi.limit_bal` is 1.196 [[art:c312ae78:psi.limit_bal]].
The value of `psi.max` is 1.196 [[art:5a6a40fb:psi.max]].
The value of `psi.pay_ratio_last` is 0.002965 [[art:35f2b74b:psi.pay_ratio_last]].
The value of `psi.pay_ratio_mean_6m` is 0.008826 [[art:1e74f864:psi.pay_ratio_mean_6m]].
The value of `psi.utilisation` is 0.01936 [[art:e45cb5af:psi.utilisation]].
The value of `psi.y_score` is 0.1866 [[art:1ecde7e0:psi.y_score]].
The value of `threshold.D1.missing_gap` is 0.1 [[art:9cce25ea:threshold.D1.missing_gap]].
The value of `threshold.L1.single_feature_auc` is 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]].
The value of `threshold.L2.overlap` is 0.005 [[art:9f336eaf:threshold.L2.overlap]].
The value of `threshold.L2.overlap.features_effective` is 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].
The value of `threshold.S1.psi` is 0.25 [[art:278b9016:threshold.S1.psi]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
Candidates raised on this section's material: S1 (see the findings section).

## 4. Outcomes analysis

This section follows the model risk management guidance at [[reg:SR26-2:V.1.b]].
The value of `calibration.mean_rel_gap.test` is 0.05556 [[art:844dbd0c:calibration.mean_rel_gap.test]].
The value of `calibration.mean_rel_gap.train` is 0.00009752 [[art:d0dfeed7:calibration.mean_rel_gap.train]].
The value of `calibration_intercept.test` is 0.09438 [[art:9a0ff160:calibration_intercept.test]].
The value of `calibration_intercept.train` is 0.004013 [[art:16a633d0:calibration_intercept.train]].
The value of `calibration_slope.test` is 1.008 [[art:b918ce48:calibration_slope.test]].
The value of `calibration_slope.train` is 1.004 [[art:4c796937:calibration_slope.train]].
The value of `deciles.test.top2_capture` is 0.4392 [[art:293e7437:deciles.test.top2_capture]].
The value of `deciles.train.top2_capture` is 0.3899 [[art:a16b6639:deciles.train.top2_capture]].
The value of `metrics.test.auc` is 0.7525 [[art:2a5ea4af:metrics.test.auc]].
The value of `metrics.test.brier` is 0.1524 [[art:7da5c034:metrics.test.brier]].
The value of `metrics.test.event_rate` is 0.2247 [[art:9209d200:metrics.test.event_rate]].
The value of `metrics.test.gini` is 0.505 [[art:f00e967c:metrics.test.gini]].
The value of `metrics.test.ks` is 0.4306 [[art:c3789b0d:metrics.test.ks]].
The value of `metrics.test.logloss` is 0.4717 [[art:46b23175:metrics.test.logloss]].
The value of `metrics.test.mean_predicted` is 0.2122 [[art:f06b1724:metrics.test.mean_predicted]].
The value of `metrics.test.n` is 1500 [[art:64fcf14d:metrics.test.n]].
The value of `metrics.train.auc` is 0.7599 [[art:3d5f30fa:metrics.train.auc]].
The value of `metrics.train.brier` is 0.1636 [[art:46973259:metrics.train.brier]].
The value of `metrics.train.event_rate` is 0.2437 [[art:25e9afa5:metrics.train.event_rate]].
The value of `metrics.train.gini` is 0.5198 [[art:3198b731:metrics.train.gini]].
The value of `metrics.train.ks` is 0.4559 [[art:c2dc79a4:metrics.train.ks]].
The value of `metrics.train.logloss` is 0.4967 [[art:73e399ed:metrics.train.logloss]].
The value of `metrics.train.mean_predicted` is 0.2437 [[art:7bfcb165:metrics.train.mean_predicted]].
The value of `metrics.train.n` is 1789 [[art:eae7a256:metrics.train.n]].
The value of `psi.age` is 0.005867 [[art:c35c14b6:psi.age]].
The value of `psi.bill_trend_6m` is 0.1334 [[art:41ee0c35:psi.bill_trend_6m]].
The value of `psi.delinq_count_6m` is 0.002943 [[art:f5c55e59:psi.delinq_count_6m]].
The value of `psi.delinq_last` is 0.0008258 [[art:da6a07f2:psi.delinq_last]].
The value of `psi.delinq_max_6m` is 0.007293 [[art:85162d6e:psi.delinq_max_6m]].
The value of `psi.limit_bal` is 1.196 [[art:c312ae78:psi.limit_bal]].
The value of `psi.max` is 1.196 [[art:5a6a40fb:psi.max]].
The value of `psi.pay_ratio_last` is 0.002965 [[art:35f2b74b:psi.pay_ratio_last]].
The value of `psi.pay_ratio_mean_6m` is 0.008826 [[art:1e74f864:psi.pay_ratio_mean_6m]].
The value of `psi.utilisation` is 0.01936 [[art:e45cb5af:psi.utilisation]].
The value of `psi.y_score` is 0.1866 [[art:1ecde7e0:psi.y_score]].
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
Candidates raised on this section's material: T1 (see the findings section).

## 5. Sensitivity and scenario analysis

This section follows the model risk management guidance at [[reg:SR26-2:V.1.a]].
The value of `condition_number` is 5.647 [[art:81de583f:condition_number]].
The value of `threshold.M1.condition_number` is 30 [[art:7e52fd7a:threshold.M1.condition_number]].
The value of `threshold.M1.vif` is 10 [[art:aeb4f33c:threshold.M1.vif]].
The value of `vif.age` is 1.002 [[art:4c6350d4:vif.age]].
The value of `vif.bill_trend_6m` is 1.01 [[art:e9e68e9c:vif.bill_trend_6m]].
The value of `vif.delinq_count_6m` is 2.482 [[art:ca8684a5:vif.delinq_count_6m]].
The value of `vif.delinq_last` is 1.366 [[art:610d9380:vif.delinq_last]].
The value of `vif.delinq_max_6m` is 2.36 [[art:21212f86:vif.delinq_max_6m]].
The value of `vif.limit_bal` is 1.005 [[art:f6c05005:vif.limit_bal]].
The value of `vif.max` is 7.662 [[art:3a027a9e:vif.max]].
The value of `vif.pay_ratio_last` is 7.662 [[art:906f9c92:vif.pay_ratio_last]].
The value of `vif.pay_ratio_mean_6m` is 7.649 [[art:d5c149e7:vif.pay_ratio_mean_6m]].
The value of `vif.utilisation` is 1.003 [[art:f810d89d:vif.utilisation]].

## 6. Findings and recommendations

This section follows the model risk management guidance at [[reg:SR26-2:VI.3]].

### F-001 · T1 declared threshold · severity **high**

**A `T1` finding, raised by `compute_metrics` at severity `high`.**
Its evidence is the artifacts cited in this section; the check's own account of it is recorded in `findings.json`.

### F-002 · S1 population drift · severity **medium**

**A `S1` finding, raised by `profile_data` at severity `medium`.**
Its evidence is the artifacts cited in this section; the check's own account of it is recorded in `findings.json`.

### F-003 · E1 effective challenge · severity **low**

**A `E1` finding, raised by `challenger_compare` at severity `low`.**
Its evidence is the artifacts cited in this section; the check's own account of it is recorded in `findings.json`.
The value of `challenger.auc` is 0.8221 [[art:9a3da49b:challenger.auc]].
The value of `challenger.delta_auc` is 0.06961 [[art:ce2a1ab8:challenger.delta_auc]].
The value of `metrics.test.auc` is 0.7525 [[art:2a5ea4af:metrics.test.auc]].
The value of `psi.limit_bal` is 1.196 [[art:c312ae78:psi.limit_bal]].
The value of `psi.max` is 1.196 [[art:5a6a40fb:psi.max]].
The value of `sign_check.delinq_max_6m.agrees` is 0 [[art:c946359c:sign_check.delinq_max_6m.agrees]].
The value of `sign_check.delinq_max_6m.coef_sign` is -1 [[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]].
The value of `sign_check.delinq_max_6m.univariate_direction` is 1 [[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]].
The value of `sign_check.pay_ratio_last.agrees` is 0 [[art:79abee77:sign_check.pay_ratio_last.agrees]].
The value of `sign_check.pay_ratio_last.coef_sign` is 1 [[art:f018263e:sign_check.pay_ratio_last.coef_sign]].
The value of `sign_check.pay_ratio_last.univariate_direction` is -1 [[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]].
The value of `threshold.E1.delta_auc` is 0.03 [[art:e042774c:threshold.E1.delta_auc]].
The value of `threshold.S1.psi` is 0.25 [[art:278b9016:threshold.S1.psi]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1), `compute_metrics` (C1, O1), `check_leakage` (L1, L2), `check_collinearity` (M1).

### Open items

No open item was recorded for this validation.

## 7. Ongoing monitoring recommendations

This section follows the model risk management guidance at [[reg:SR26-2:V.2]].
The value of `calibration_slope.test` is 1.008 [[art:b918ce48:calibration_slope.test]].
The value of `metrics.test.auc` is 0.7525 [[art:2a5ea4af:metrics.test.auc]].
The value of `metrics.test.brier` is 0.1524 [[art:7da5c034:metrics.test.brier]].
The value of `psi.max` is 1.196 [[art:5a6a40fb:psi.max]].
The value of `rule.calibration_first_event_rate` is 0.05 [[art:42f1351e:rule.calibration_first_event_rate]].
The value of `threshold.package.auc.test.min` is 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]].
The value of `threshold.package.brier.test.max` is 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]].
The value of `threshold.package.calibration_slope.test.max` is 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The value of `threshold.package.calibration_slope.test.min` is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].

## Appendix A — Claims

Grounding precision 1.0000 before repair (203 of 203 claims verified) and 1.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 31/31; conceptual_soundness 44/44; data_integrity 38/38; outcomes 53/53; sensitivity 13/13; findings 14/14; monitoring 10/10.

Developer claims: The package declares 2 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). See Appendix D.

Excluded numeric tokens (not claims): citation_hash (b918ce48, 4c796937, ce2a1ab8, 81de583f); regulatory_section_id (SR26-2:V.1.b, SR26-2:V.1.a, SR26-2:VI.3, SR26-2:V.2); finding_id (F-001, F-002, F-003).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The value of `calibration_slope.test` is 1.008 . | 1.008 | ratio | calibration_slope |  | eq | `[[art:b918ce48:calibration_slope.test]]` | verified | 1.008335252 |
| 2 | summary | The value of `calibration_slope.train` is 1.004 . | 1.004 | ratio | calibration_slope |  | eq | `[[art:4c796937:calibration_slope.train]]` | verified | 1.003641864 |
| 3 | summary | The value of `challenger.delta_auc` is 0.06961 . | 0.06961 | ratio | challenger |  | eq | `[[art:ce2a1ab8:challenger.delta_auc]]` | verified | 0.06960663994 |
| 4 | summary | The value of `condition_number` is 5.647 . | 5.647 | ratio | condition_number |  | eq | `[[art:81de583f:condition_number]]` | verified | 5.646856643 |
| 5 | summary | The value of `csi.max` is 0.06466 . | 0.06466 | ratio | csi |  | eq | `[[art:b2e113ad:csi.max]]` | verified | 0.06466414354 |
| 6 | summary | The value of `metrics.test.auc` is 0.7525 . | 0.7525 | ratio | metrics |  | eq | `[[art:2a5ea4af:metrics.test.auc]]` | verified | 0.7525227655 |
| 7 | summary | The value of `metrics.test.brier` is 0.1524 . | 0.1524 | ratio | metrics |  | eq | `[[art:7da5c034:metrics.test.brier]]` | verified | 0.1523576419 |
| 8 | summary | The value of `metrics.test.event_rate` is 0.2247 . | 0.2247 | ratio | metrics |  | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 9 | summary | The value of `metrics.test.gini` is 0.505 . | 0.505 | ratio | metrics |  | eq | `[[art:f00e967c:metrics.test.gini]]` | verified | 0.505045531 |
| 10 | summary | The value of `metrics.test.ks` is 0.4306 . | 0.4306 | ratio | metrics |  | eq | `[[art:c3789b0d:metrics.test.ks]]` | verified | 0.4305579298 |
| 11 | summary | The value of `metrics.test.logloss` is 0.4717 . | 0.4717 | ratio | metrics |  | eq | `[[art:46b23175:metrics.test.logloss]]` | verified | 0.4717272727 |
| 12 | summary | The value of `metrics.test.mean_predicted` is 0.2122 . | 0.2122 | ratio | metrics |  | eq | `[[art:f06b1724:metrics.test.mean_predicted]]` | verified | 0.2121848053 |
| 13 | summary | The value of `metrics.test.n` is 1500 . | 1500 | ratio | metrics |  | eq | `[[art:64fcf14d:metrics.test.n]]` | verified | 1500 |
| 14 | summary | The value of `metrics.train.auc` is 0.7599 . | 0.7599 | ratio | metrics |  | eq | `[[art:3d5f30fa:metrics.train.auc]]` | verified | 0.7599201909 |
| 15 | summary | The value of `metrics.train.brier` is 0.1636 . | 0.1636 | ratio | metrics |  | eq | `[[art:46973259:metrics.train.brier]]` | verified | 0.1636435165 |
| 16 | summary | The value of `metrics.train.event_rate` is 0.2437 . | 0.2437 | ratio | metrics |  | eq | `[[art:25e9afa5:metrics.train.event_rate]]` | verified | 0.2437115707 |
| 17 | summary | The value of `metrics.train.gini` is 0.5198 . | 0.5198 | ratio | metrics |  | eq | `[[art:3198b731:metrics.train.gini]]` | verified | 0.5198403819 |
| 18 | summary | The value of `metrics.train.ks` is 0.4559 . | 0.4559 | ratio | metrics |  | eq | `[[art:c2dc79a4:metrics.train.ks]]` | verified | 0.4558914271 |
| 19 | summary | The value of `metrics.train.logloss` is 0.4967 . | 0.4967 | ratio | metrics |  | eq | `[[art:73e399ed:metrics.train.logloss]]` | verified | 0.4967129472 |
| 20 | summary | The value of `metrics.train.mean_predicted` is 0.2437 . | 0.2437 | ratio | metrics |  | eq | `[[art:7bfcb165:metrics.train.mean_predicted]]` | verified | 0.2436878042 |
| 21 | summary | The value of `metrics.train.n` is 1789 . | 1789 | ratio | metrics |  | eq | `[[art:eae7a256:metrics.train.n]]` | verified | 1789 |
| 22 | summary | The value of `profile.test.n` is 1500 . | 1500 | ratio | profile |  | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 23 | summary | The value of `profile.train.n` is 1789 . | 1789 | ratio | profile |  | eq | `[[art:0f89a4f1:profile.train.n]]` | verified | 1789 |
| 24 | summary | The value of `psi.max` is 1.196 . | 1.196 | ratio | psi |  | eq | `[[art:5a6a40fb:psi.max]]` | verified | 1.195887841 |
| 25 | summary | The value of `runtime.max_seconds` is 300 . | 300 | ratio | runtime |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 26 | summary | The value of `threshold.package.auc.test.min` is 0.7 . | 0.7 | ratio | threshold |  | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 27 | summary | The value of `threshold.package.brier.test.max` is 0.2 . | 0.2 | ratio | threshold |  | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 28 | summary | The value of `threshold.package.calibration_slope.test.max`… | 1.2 | ratio | threshold |  | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 29 | summary | The value of `threshold.package.calibration_slope.test.min`… | 0.8 | ratio | threshold |  | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 30 | summary | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 31 | summary | The value of `vif.max` is 7.662 . | 7.662 | ratio | vif |  | eq | `[[art:3a027a9e:vif.max]]` | verified | 7.661689317 |
| 32 | conceptual_soundness | The value of `ablation.age.delta_auc` is 0.001077 . | 0.001077 | ratio | ablation |  | eq | `[[art:223939e9:ablation.age.delta_auc]]` | verified | 0.001076720137 |
| 33 | conceptual_soundness | The value of `ablation.baseline_auc` is 0.7525 . | 0.7525 | ratio | ablation |  | eq | `[[art:6b970cd1:ablation.baseline_auc]]` | verified | 0.7525227655 |
| 34 | conceptual_soundness | The value of `ablation.bill_trend_6m.delta_auc` is 0.007121… | 0.007121 | ratio | ablation |  | eq | `[[art:b56721dc:ablation.bill_trend_6m.delta_auc]]` | verified | 0.007121151427 |
| 35 | conceptual_soundness | The value of `ablation.delinq_count_6m.delta_auc` is -0.0001… | -0.0001378 | ratio | ablation |  | eq | `[[art:478e5417:ablation.delinq_count_6m.delta_auc]]` | verified | -0.000137779354 |
| 36 | conceptual_soundness | The value of `ablation.delinq_last.delta_auc` is -0.09255 . | -0.09255 | ratio | ablation |  | eq | `[[art:562511ba:ablation.delinq_last.delta_auc]]` | verified | -0.09254945386 |
| 37 | conceptual_soundness | The value of `ablation.delinq_max_6m.delta_auc` is 0.0000816… | 8.165e-05 | ratio | ablation |  | eq | `[[art:1d41dd41:ablation.delinq_max_6m.delta_auc]]` | verified | 8.16470246e-05 |
| 38 | conceptual_soundness | The value of `ablation.limit_bal.delta_auc` is 0.004218 . | 0.004218 | ratio | ablation |  | eq | `[[art:6f97302c:ablation.limit_bal.delta_auc]]` | verified | 0.004217579115 |
| 39 | conceptual_soundness | The value of `ablation.pay_ratio_last.delta_auc` is 0.003621… | 0.003621 | ratio | ablation |  | eq | `[[art:cc45633b:ablation.pay_ratio_last.delta_auc]]` | verified | 0.003620535247 |
| 40 | conceptual_soundness | The value of `ablation.pay_ratio_mean_6m.delta_auc` is 0.007… | 0.007129 | ratio | ablation |  | eq | `[[art:53d51307:ablation.pay_ratio_mean_6m.delta_auc]]` | verified | 0.007128805836 |
| 41 | conceptual_soundness | The value of `ablation.utilisation.delta_auc` is -0.02697 . | -0.02697 | ratio | ablation |  | eq | `[[art:2a417d0d:ablation.utilisation.delta_auc]]` | verified | -0.02697158428 |
| 42 | conceptual_soundness | The value of `challenger.auc` is 0.8221 . | 0.8221 | ratio | challenger |  | eq | `[[art:9a3da49b:challenger.auc]]` | verified | 0.8221294054 |
| 43 | conceptual_soundness | The value of `challenger.brier` is 0.125 . | 0.125 | ratio | challenger |  | eq | `[[art:01fa79a9:challenger.brier]]` | verified | 0.1250082176 |
| 44 | conceptual_soundness | The value of `challenger.delta_auc` is 0.06961 . | 0.06961 | ratio | challenger |  | eq | `[[art:ce2a1ab8:challenger.delta_auc]]` | verified | 0.06960663994 |
| 45 | conceptual_soundness | The value of `metrics.test.auc` is 0.7525 . | 0.7525 | ratio | metrics |  | eq | `[[art:2a5ea4af:metrics.test.auc]]` | verified | 0.7525227655 |
| 46 | conceptual_soundness | The value of `metrics.test.brier` is 0.1524 . | 0.1524 | ratio | metrics |  | eq | `[[art:7da5c034:metrics.test.brier]]` | verified | 0.1523576419 |
| 47 | conceptual_soundness | The value of `sign_check.age.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:4116add1:sign_check.age.agrees]]` | verified | 1 |
| 48 | conceptual_soundness | The value of `sign_check.age.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:6172eb93:sign_check.age.coef_sign]]` | verified | -1 |
| 49 | conceptual_soundness | The value of `sign_check.age.univariate_direction` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:66364583:sign_check.age.univariate_direction]]` | verified | -1 |
| 50 | conceptual_soundness | The value of `sign_check.bill_trend_6m.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:ff3cb24a:sign_check.bill_trend_6m.agrees]]` | verified | 1 |
| 51 | conceptual_soundness | The value of `sign_check.bill_trend_6m.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:7fd8474e:sign_check.bill_trend_6m.coef_sign]]` | verified | -1 |
| 52 | conceptual_soundness | The value of `sign_check.bill_trend_6m.univariate_direction`… | -1 | ratio | sign_check |  | eq | `[[art:a9bff389:sign_check.bill_trend_6m.univariate_direction]]` | verified | -1 |
| 53 | conceptual_soundness | The value of `sign_check.delinq_count_6m.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:a337d16b:sign_check.delinq_count_6m.agrees]]` | verified | 1 |
| 54 | conceptual_soundness | The value of `sign_check.delinq_count_6m.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:17afb6f9:sign_check.delinq_count_6m.coef_sign]]` | verified | 1 |
| 55 | conceptual_soundness | The value of `sign_check.delinq_count_6m.univariate_directio… | 1 | ratio | sign_check |  | eq | `[[art:549e904e:sign_check.delinq_count_6m.univariate_direction]]` | verified | 1 |
| 56 | conceptual_soundness | The value of `sign_check.delinq_last.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:a8ba9372:sign_check.delinq_last.agrees]]` | verified | 1 |
| 57 | conceptual_soundness | The value of `sign_check.delinq_last.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:50d352f8:sign_check.delinq_last.coef_sign]]` | verified | 1 |
| 58 | conceptual_soundness | The value of `sign_check.delinq_last.univariate_direction` i… | 1 | ratio | sign_check |  | eq | `[[art:a78648ba:sign_check.delinq_last.univariate_direction]]` | verified | 1 |
| 59 | conceptual_soundness | The value of `sign_check.delinq_max_6m.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:c946359c:sign_check.delinq_max_6m.agrees]]` | verified | 0 |
| 60 | conceptual_soundness | The value of `sign_check.delinq_max_6m.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]]` | verified | -1 |
| 61 | conceptual_soundness | The value of `sign_check.delinq_max_6m.univariate_direction`… | 1 | ratio | sign_check |  | eq | `[[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]]` | verified | 1 |
| 62 | conceptual_soundness | The value of `sign_check.limit_bal.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:103d99fb:sign_check.limit_bal.agrees]]` | verified | 1 |
| 63 | conceptual_soundness | The value of `sign_check.limit_bal.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:a6d01381:sign_check.limit_bal.coef_sign]]` | verified | -1 |
| 64 | conceptual_soundness | The value of `sign_check.limit_bal.univariate_direction` is… | -1 | ratio | sign_check |  | eq | `[[art:56d284d6:sign_check.limit_bal.univariate_direction]]` | verified | -1 |
| 65 | conceptual_soundness | The value of `sign_check.n_disagreements` is 2 . | 2 | ratio | sign_check |  | eq | `[[art:66ce738a:sign_check.n_disagreements]]` | verified | 2 |
| 66 | conceptual_soundness | The value of `sign_check.pay_ratio_last.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:79abee77:sign_check.pay_ratio_last.agrees]]` | verified | 0 |
| 67 | conceptual_soundness | The value of `sign_check.pay_ratio_last.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:f018263e:sign_check.pay_ratio_last.coef_sign]]` | verified | 1 |
| 68 | conceptual_soundness | The value of `sign_check.pay_ratio_last.univariate_direction… | -1 | ratio | sign_check |  | eq | `[[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]]` | verified | -1 |
| 69 | conceptual_soundness | The value of `sign_check.pay_ratio_mean_6m.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:7e9a76ca:sign_check.pay_ratio_mean_6m.agrees]]` | verified | 1 |
| 70 | conceptual_soundness | The value of `sign_check.pay_ratio_mean_6m.coef_sign` is -1… | -1 | ratio | sign_check |  | eq | `[[art:077bb6b2:sign_check.pay_ratio_mean_6m.coef_sign]]` | verified | -1 |
| 71 | conceptual_soundness | The value of `sign_check.pay_ratio_mean_6m.univariate_direct… | -1 | ratio | sign_check |  | eq | `[[art:24dcef24:sign_check.pay_ratio_mean_6m.univariate_direction]]` | verified | -1 |
| 72 | conceptual_soundness | The value of `sign_check.utilisation.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:d0c9a130:sign_check.utilisation.agrees]]` | verified | 1 |
| 73 | conceptual_soundness | The value of `sign_check.utilisation.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:85badc3c:sign_check.utilisation.coef_sign]]` | verified | 1 |
| 74 | conceptual_soundness | The value of `sign_check.utilisation.univariate_direction` i… | 1 | ratio | sign_check |  | eq | `[[art:f0995196:sign_check.utilisation.univariate_direction]]` | verified | 1 |
| 75 | conceptual_soundness | The value of `threshold.E1.delta_auc` is 0.03 . | 0.03 | ratio | threshold |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 76 | data_integrity | The value of `csi.age` is 0.0009235 . | 0.0009235 | ratio | csi |  | eq | `[[art:c3bb7175:csi.age]]` | verified | 0.0009235432986 |
| 77 | data_integrity | The value of `csi.bill_trend_6m` is 0.002501 . | 0.002501 | ratio | csi |  | eq | `[[art:6d4f0d7b:csi.bill_trend_6m]]` | verified | 0.002501452355 |
| 78 | data_integrity | The value of `csi.delinq_count_6m` is 0.002246 . | 0.002246 | ratio | csi |  | eq | `[[art:7ee6f613:csi.delinq_count_6m]]` | verified | 0.002246336405 |
| 79 | data_integrity | The value of `csi.delinq_last` is 0.01505 . | 0.01505 | ratio | csi |  | eq | `[[art:4e9b1ec3:csi.delinq_last]]` | verified | 0.01504852065 |
| 80 | data_integrity | The value of `csi.delinq_max_6m` is 0.0001002 . | 0.0001002 | ratio | csi |  | eq | `[[art:f775c7df:csi.delinq_max_6m]]` | verified | 0.0001001969452 |
| 81 | data_integrity | The value of `csi.limit_bal` is 0.06466 . | 0.06466 | ratio | csi |  | eq | `[[art:44fa93ba:csi.limit_bal]]` | verified | 0.06466414354 |
| 82 | data_integrity | The value of `csi.max` is 0.06466 . | 0.06466 | ratio | csi |  | eq | `[[art:b2e113ad:csi.max]]` | verified | 0.06466414354 |
| 83 | data_integrity | The value of `csi.pay_ratio_last` is 0.001222 . | 0.001222 | ratio | csi |  | eq | `[[art:547b3f3e:csi.pay_ratio_last]]` | verified | 0.00122248434 |
| 84 | data_integrity | The value of `csi.pay_ratio_mean_6m` is 0.00576 . | 0.00576 | ratio | csi |  | eq | `[[art:d7a50342:csi.pay_ratio_mean_6m]]` | verified | 0.005759760061 |
| 85 | data_integrity | The value of `csi.utilisation` is 0.005503 . | 0.005503 | ratio | csi |  | eq | `[[art:b506bc4b:csi.utilisation]]` | verified | 0.005503189472 |
| 86 | data_integrity | The value of `leakage.duplicates.train` is 0 . | 0 | ratio | leakage |  | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 87 | data_integrity | The value of `leakage.name_screen.n_matched` is 0 . | 0 | ratio | leakage |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 88 | data_integrity | The value of `leakage.overlap` is 0 . | 0 | ratio | leakage |  | eq | `[[art:4c9fcd09:leakage.overlap]]` | verified | 0 |
| 89 | data_integrity | The value of `leakage.overlap.features` is 0 . | 0 | ratio | leakage |  | eq | `[[art:0fec8048:leakage.overlap.features]]` | verified | 0 |
| 90 | data_integrity | The value of `leakage.overlap.ids` is 0 . | 0 | ratio | leakage |  | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 91 | data_integrity | The value of `leakage.target_corr.max_single_feature_auc` is… | 0.6626 | ratio | leakage |  | eq | `[[art:4c34a594:leakage.target_corr.max_single_feature_auc]]` | verified | 0.6626279013 |
| 92 | data_integrity | The value of `leakage.timing.n_flagged` is 0 . | 0 | ratio | leakage |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 93 | data_integrity | The value of `profile.test.missing.max` is 0 . | 0 | ratio | profile |  | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 94 | data_integrity | The value of `profile.test.n` is 1500 . | 1500 | ratio | profile |  | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 95 | data_integrity | The value of `profile.train.missing.max` is 0 . | 0 | ratio | profile |  | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 96 | data_integrity | The value of `profile.train.n` is 1789 . | 1789 | ratio | profile |  | eq | `[[art:0f89a4f1:profile.train.n]]` | verified | 1789 |
| 97 | data_integrity | The value of `psi.age` is 0.005867 . | 0.005867 | ratio | psi |  | eq | `[[art:c35c14b6:psi.age]]` | verified | 0.005867466098 |
| 98 | data_integrity | The value of `psi.bill_trend_6m` is 0.1334 . | 0.1334 | ratio | psi |  | eq | `[[art:41ee0c35:psi.bill_trend_6m]]` | verified | 0.1333601749 |
| 99 | data_integrity | The value of `psi.delinq_count_6m` is 0.002943 . | 0.002943 | ratio | psi |  | eq | `[[art:f5c55e59:psi.delinq_count_6m]]` | verified | 0.002943407989 |
| 100 | data_integrity | The value of `psi.delinq_last` is 0.0008258 . | 0.0008258 | ratio | psi |  | eq | `[[art:da6a07f2:psi.delinq_last]]` | verified | 0.000825781607 |
| 101 | data_integrity | The value of `psi.delinq_max_6m` is 0.007293 . | 0.007293 | ratio | psi |  | eq | `[[art:85162d6e:psi.delinq_max_6m]]` | verified | 0.007293474501 |
| 102 | data_integrity | The value of `psi.limit_bal` is 1.196 . | 1.196 | ratio | psi |  | eq | `[[art:c312ae78:psi.limit_bal]]` | verified | 1.195887841 |
| 103 | data_integrity | The value of `psi.max` is 1.196 . | 1.196 | ratio | psi |  | eq | `[[art:5a6a40fb:psi.max]]` | verified | 1.195887841 |
| 104 | data_integrity | The value of `psi.pay_ratio_last` is 0.002965 . | 0.002965 | ratio | psi |  | eq | `[[art:35f2b74b:psi.pay_ratio_last]]` | verified | 0.002964692875 |
| 105 | data_integrity | The value of `psi.pay_ratio_mean_6m` is 0.008826 . | 0.008826 | ratio | psi |  | eq | `[[art:1e74f864:psi.pay_ratio_mean_6m]]` | verified | 0.008826121484 |
| 106 | data_integrity | The value of `psi.utilisation` is 0.01936 . | 0.01936 | ratio | psi |  | eq | `[[art:e45cb5af:psi.utilisation]]` | verified | 0.01935892092 |
| 107 | data_integrity | The value of `psi.y_score` is 0.1866 . | 0.1866 | ratio | psi |  | eq | `[[art:1ecde7e0:psi.y_score]]` | verified | 0.1866241345 |
| 108 | data_integrity | The value of `threshold.D1.missing_gap` is 0.1 . | 0.1 | ratio | threshold |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 109 | data_integrity | The value of `threshold.L1.single_feature_auc` is 0.9 . | 0.9 | ratio | threshold |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 110 | data_integrity | The value of `threshold.L2.overlap` is 0.005 . | 0.005 | ratio | threshold |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 111 | data_integrity | The value of `threshold.L2.overlap.features_effective` is 0.… | 0.005 | ratio | threshold |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 112 | data_integrity | The value of `threshold.S1.psi` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 113 | data_integrity | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 114 | outcomes | The value of `calibration.mean_rel_gap.test` is 0.05556 . | 0.05556 | ratio | calibration |  | eq | `[[art:844dbd0c:calibration.mean_rel_gap.test]]` | verified | 0.05555724643 |
| 115 | outcomes | The value of `calibration.mean_rel_gap.train` is 0.00009752… | 9.752e-05 | ratio | calibration |  | eq | `[[art:d0dfeed7:calibration.mean_rel_gap.train]]` | verified | 9.751887447e-05 |
| 116 | outcomes | The value of `calibration_intercept.test` is 0.09438 . | 0.09438 | ratio | calibration_intercept |  | eq | `[[art:9a0ff160:calibration_intercept.test]]` | verified | 0.09437539159 |
| 117 | outcomes | The value of `calibration_intercept.train` is 0.004013 . | 0.004013 | ratio | calibration_intercept |  | eq | `[[art:16a633d0:calibration_intercept.train]]` | verified | 0.004013103211 |
| 118 | outcomes | The value of `calibration_slope.test` is 1.008 . | 1.008 | ratio | calibration_slope |  | eq | `[[art:b918ce48:calibration_slope.test]]` | verified | 1.008335252 |
| 119 | outcomes | The value of `calibration_slope.train` is 1.004 . | 1.004 | ratio | calibration_slope |  | eq | `[[art:4c796937:calibration_slope.train]]` | verified | 1.003641864 |
| 120 | outcomes | The value of `deciles.test.top2_capture` is 0.4392 . | 0.4392 | ratio | deciles |  | eq | `[[art:293e7437:deciles.test.top2_capture]]` | verified | 0.4391691395 |
| 121 | outcomes | The value of `deciles.train.top2_capture` is 0.3899 . | 0.3899 | ratio | deciles |  | eq | `[[art:a16b6639:deciles.train.top2_capture]]` | verified | 0.3899082569 |
| 122 | outcomes | The value of `metrics.test.auc` is 0.7525 . | 0.7525 | ratio | metrics |  | eq | `[[art:2a5ea4af:metrics.test.auc]]` | verified | 0.7525227655 |
| 123 | outcomes | The value of `metrics.test.brier` is 0.1524 . | 0.1524 | ratio | metrics |  | eq | `[[art:7da5c034:metrics.test.brier]]` | verified | 0.1523576419 |
| 124 | outcomes | The value of `metrics.test.event_rate` is 0.2247 . | 0.2247 | ratio | metrics |  | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 125 | outcomes | The value of `metrics.test.gini` is 0.505 . | 0.505 | ratio | metrics |  | eq | `[[art:f00e967c:metrics.test.gini]]` | verified | 0.505045531 |
| 126 | outcomes | The value of `metrics.test.ks` is 0.4306 . | 0.4306 | ratio | metrics |  | eq | `[[art:c3789b0d:metrics.test.ks]]` | verified | 0.4305579298 |
| 127 | outcomes | The value of `metrics.test.logloss` is 0.4717 . | 0.4717 | ratio | metrics |  | eq | `[[art:46b23175:metrics.test.logloss]]` | verified | 0.4717272727 |
| 128 | outcomes | The value of `metrics.test.mean_predicted` is 0.2122 . | 0.2122 | ratio | metrics |  | eq | `[[art:f06b1724:metrics.test.mean_predicted]]` | verified | 0.2121848053 |
| 129 | outcomes | The value of `metrics.test.n` is 1500 . | 1500 | ratio | metrics |  | eq | `[[art:64fcf14d:metrics.test.n]]` | verified | 1500 |
| 130 | outcomes | The value of `metrics.train.auc` is 0.7599 . | 0.7599 | ratio | metrics |  | eq | `[[art:3d5f30fa:metrics.train.auc]]` | verified | 0.7599201909 |
| 131 | outcomes | The value of `metrics.train.brier` is 0.1636 . | 0.1636 | ratio | metrics |  | eq | `[[art:46973259:metrics.train.brier]]` | verified | 0.1636435165 |
| 132 | outcomes | The value of `metrics.train.event_rate` is 0.2437 . | 0.2437 | ratio | metrics |  | eq | `[[art:25e9afa5:metrics.train.event_rate]]` | verified | 0.2437115707 |
| 133 | outcomes | The value of `metrics.train.gini` is 0.5198 . | 0.5198 | ratio | metrics |  | eq | `[[art:3198b731:metrics.train.gini]]` | verified | 0.5198403819 |
| 134 | outcomes | The value of `metrics.train.ks` is 0.4559 . | 0.4559 | ratio | metrics |  | eq | `[[art:c2dc79a4:metrics.train.ks]]` | verified | 0.4558914271 |
| 135 | outcomes | The value of `metrics.train.logloss` is 0.4967 . | 0.4967 | ratio | metrics |  | eq | `[[art:73e399ed:metrics.train.logloss]]` | verified | 0.4967129472 |
| 136 | outcomes | The value of `metrics.train.mean_predicted` is 0.2437 . | 0.2437 | ratio | metrics |  | eq | `[[art:7bfcb165:metrics.train.mean_predicted]]` | verified | 0.2436878042 |
| 137 | outcomes | The value of `metrics.train.n` is 1789 . | 1789 | ratio | metrics |  | eq | `[[art:eae7a256:metrics.train.n]]` | verified | 1789 |
| 138 | outcomes | The value of `psi.age` is 0.005867 . | 0.005867 | ratio | psi |  | eq | `[[art:c35c14b6:psi.age]]` | verified | 0.005867466098 |
| 139 | outcomes | The value of `psi.bill_trend_6m` is 0.1334 . | 0.1334 | ratio | psi |  | eq | `[[art:41ee0c35:psi.bill_trend_6m]]` | verified | 0.1333601749 |
| 140 | outcomes | The value of `psi.delinq_count_6m` is 0.002943 . | 0.002943 | ratio | psi |  | eq | `[[art:f5c55e59:psi.delinq_count_6m]]` | verified | 0.002943407989 |
| 141 | outcomes | The value of `psi.delinq_last` is 0.0008258 . | 0.0008258 | ratio | psi |  | eq | `[[art:da6a07f2:psi.delinq_last]]` | verified | 0.000825781607 |
| 142 | outcomes | The value of `psi.delinq_max_6m` is 0.007293 . | 0.007293 | ratio | psi |  | eq | `[[art:85162d6e:psi.delinq_max_6m]]` | verified | 0.007293474501 |
| 143 | outcomes | The value of `psi.limit_bal` is 1.196 . | 1.196 | ratio | psi |  | eq | `[[art:c312ae78:psi.limit_bal]]` | verified | 1.195887841 |
| 144 | outcomes | The value of `psi.max` is 1.196 . | 1.196 | ratio | psi |  | eq | `[[art:5a6a40fb:psi.max]]` | verified | 1.195887841 |
| 145 | outcomes | The value of `psi.pay_ratio_last` is 0.002965 . | 0.002965 | ratio | psi |  | eq | `[[art:35f2b74b:psi.pay_ratio_last]]` | verified | 0.002964692875 |
| 146 | outcomes | The value of `psi.pay_ratio_mean_6m` is 0.008826 . | 0.008826 | ratio | psi |  | eq | `[[art:1e74f864:psi.pay_ratio_mean_6m]]` | verified | 0.008826121484 |
| 147 | outcomes | The value of `psi.utilisation` is 0.01936 . | 0.01936 | ratio | psi |  | eq | `[[art:e45cb5af:psi.utilisation]]` | verified | 0.01935892092 |
| 148 | outcomes | The value of `psi.y_score` is 0.1866 . | 0.1866 | ratio | psi |  | eq | `[[art:1ecde7e0:psi.y_score]]` | verified | 0.1866241345 |
| 149 | outcomes | The value of `rule.calibration_first_event_rate` is 0.05 . | 0.05 | ratio | rule |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 150 | outcomes | The value of `threshold.C1.calibration_slope.max` is 1.2 . | 1.2 | ratio | threshold |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 151 | outcomes | The value of `threshold.C1.calibration_slope.min` is 0.8 . | 0.8 | ratio | threshold |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 152 | outcomes | The value of `threshold.C1.mean_ratio_rel` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 153 | outcomes | The value of `threshold.D1.missing_gap` is 0.1 . | 0.1 | ratio | threshold |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 154 | outcomes | The value of `threshold.E1.delta_auc` is 0.03 . | 0.03 | ratio | threshold |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 155 | outcomes | The value of `threshold.L1.single_feature_auc` is 0.9 . | 0.9 | ratio | threshold |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 156 | outcomes | The value of `threshold.L2.overlap` is 0.005 . | 0.005 | ratio | threshold |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 157 | outcomes | The value of `threshold.L2.overlap.features_effective` is 0.… | 0.005 | ratio | threshold |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 158 | outcomes | The value of `threshold.M1.condition_number` is 30 . | 30 | ratio | threshold |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 159 | outcomes | The value of `threshold.M1.vif` is 10 . | 10 | ratio | threshold |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 160 | outcomes | The value of `threshold.O1.auc_gap` is 0.08 . | 0.08 | ratio | threshold |  | eq | `[[art:630f28f4:threshold.O1.auc_gap]]` | verified | 0.08 |
| 161 | outcomes | The value of `threshold.S1.psi` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 162 | outcomes | The value of `threshold.package.auc.test.min` is 0.7 . | 0.7 | ratio | threshold |  | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 163 | outcomes | The value of `threshold.package.brier.test.max` is 0.2 . | 0.2 | ratio | threshold |  | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 164 | outcomes | The value of `threshold.package.calibration_slope.test.max`… | 1.2 | ratio | threshold |  | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 165 | outcomes | The value of `threshold.package.calibration_slope.test.min`… | 0.8 | ratio | threshold |  | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 166 | outcomes | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 167 | sensitivity | The value of `condition_number` is 5.647 . | 5.647 | ratio | condition_number |  | eq | `[[art:81de583f:condition_number]]` | verified | 5.646856643 |
| 168 | sensitivity | The value of `threshold.M1.condition_number` is 30 . | 30 | ratio | threshold |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 169 | sensitivity | The value of `threshold.M1.vif` is 10 . | 10 | ratio | threshold |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 170 | sensitivity | The value of `vif.age` is 1.002 . | 1.002 | ratio | vif |  | eq | `[[art:4c6350d4:vif.age]]` | verified | 1.001975689 |
| 171 | sensitivity | The value of `vif.bill_trend_6m` is 1.01 . | 1.01 | ratio | vif |  | eq | `[[art:e9e68e9c:vif.bill_trend_6m]]` | verified | 1.010358598 |
| 172 | sensitivity | The value of `vif.delinq_count_6m` is 2.482 . | 2.482 | ratio | vif |  | eq | `[[art:ca8684a5:vif.delinq_count_6m]]` | verified | 2.48208755 |
| 173 | sensitivity | The value of `vif.delinq_last` is 1.366 . | 1.366 | ratio | vif |  | eq | `[[art:610d9380:vif.delinq_last]]` | verified | 1.365552784 |
| 174 | sensitivity | The value of `vif.delinq_max_6m` is 2.36 . | 2.36 | ratio | vif |  | eq | `[[art:21212f86:vif.delinq_max_6m]]` | verified | 2.359652386 |
| 175 | sensitivity | The value of `vif.limit_bal` is 1.005 . | 1.005 | ratio | vif |  | eq | `[[art:f6c05005:vif.limit_bal]]` | verified | 1.005403299 |
| 176 | sensitivity | The value of `vif.max` is 7.662 . | 7.662 | ratio | vif |  | eq | `[[art:3a027a9e:vif.max]]` | verified | 7.661689317 |
| 177 | sensitivity | The value of `vif.pay_ratio_last` is 7.662 . | 7.662 | ratio | vif |  | eq | `[[art:906f9c92:vif.pay_ratio_last]]` | verified | 7.661689317 |
| 178 | sensitivity | The value of `vif.pay_ratio_mean_6m` is 7.649 . | 7.649 | ratio | vif |  | eq | `[[art:d5c149e7:vif.pay_ratio_mean_6m]]` | verified | 7.649492506 |
| 179 | sensitivity | The value of `vif.utilisation` is 1.003 . | 1.003 | ratio | vif |  | eq | `[[art:f810d89d:vif.utilisation]]` | verified | 1.003462873 |
| 180 | findings | The value of `challenger.auc` is 0.8221 . | 0.8221 | ratio | challenger |  | eq | `[[art:9a3da49b:challenger.auc]]` | verified | 0.8221294054 |
| 181 | findings | The value of `challenger.delta_auc` is 0.06961 . | 0.06961 | ratio | challenger |  | eq | `[[art:ce2a1ab8:challenger.delta_auc]]` | verified | 0.06960663994 |
| 182 | findings | The value of `metrics.test.auc` is 0.7525 . | 0.7525 | ratio | metrics |  | eq | `[[art:2a5ea4af:metrics.test.auc]]` | verified | 0.7525227655 |
| 183 | findings | The value of `psi.limit_bal` is 1.196 . | 1.196 | ratio | psi |  | eq | `[[art:c312ae78:psi.limit_bal]]` | verified | 1.195887841 |
| 184 | findings | The value of `psi.max` is 1.196 . | 1.196 | ratio | psi |  | eq | `[[art:5a6a40fb:psi.max]]` | verified | 1.195887841 |
| 185 | findings | The value of `sign_check.delinq_max_6m.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:c946359c:sign_check.delinq_max_6m.agrees]]` | verified | 0 |
| 186 | findings | The value of `sign_check.delinq_max_6m.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]]` | verified | -1 |
| 187 | findings | The value of `sign_check.delinq_max_6m.univariate_direction`… | 1 | ratio | sign_check |  | eq | `[[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]]` | verified | 1 |
| 188 | findings | The value of `sign_check.pay_ratio_last.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:79abee77:sign_check.pay_ratio_last.agrees]]` | verified | 0 |
| 189 | findings | The value of `sign_check.pay_ratio_last.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:f018263e:sign_check.pay_ratio_last.coef_sign]]` | verified | 1 |
| 190 | findings | The value of `sign_check.pay_ratio_last.univariate_direction… | -1 | ratio | sign_check |  | eq | `[[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]]` | verified | -1 |
| 191 | findings | The value of `threshold.E1.delta_auc` is 0.03 . | 0.03 | ratio | threshold |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 192 | findings | The value of `threshold.S1.psi` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 193 | findings | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 194 | monitoring | The value of `calibration_slope.test` is 1.008 . | 1.008 | ratio | calibration_slope |  | eq | `[[art:b918ce48:calibration_slope.test]]` | verified | 1.008335252 |
| 195 | monitoring | The value of `metrics.test.auc` is 0.7525 . | 0.7525 | ratio | metrics |  | eq | `[[art:2a5ea4af:metrics.test.auc]]` | verified | 0.7525227655 |
| 196 | monitoring | The value of `metrics.test.brier` is 0.1524 . | 0.1524 | ratio | metrics |  | eq | `[[art:7da5c034:metrics.test.brier]]` | verified | 0.1523576419 |
| 197 | monitoring | The value of `psi.max` is 1.196 . | 1.196 | ratio | psi |  | eq | `[[art:5a6a40fb:psi.max]]` | verified | 1.195887841 |
| 198 | monitoring | The value of `rule.calibration_first_event_rate` is 0.05 . | 0.05 | ratio | rule |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 199 | monitoring | The value of `threshold.package.auc.test.min` is 0.7 . | 0.7 | ratio | threshold |  | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 200 | monitoring | The value of `threshold.package.brier.test.max` is 0.2 . | 0.2 | ratio | threshold |  | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 201 | monitoring | The value of `threshold.package.calibration_slope.test.max`… | 1.2 | ratio | threshold |  | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 202 | monitoring | The value of `threshold.package.calibration_slope.test.min`… | 0.8 | ratio | threshold |  | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 203 | monitoring | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |

## Appendix B — Artifact index

The store holds 161 artifacts; the 130 this report cites or rests a finding on are indexed here.

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
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |
| `sign_check.age.agrees` | `4116add1` | scalar | 1 | 1 when the fitted sign on age agrees with its univariate direction, 0 when it does not |
| `sign_check.age.coef_sign` | `6172eb93` | scalar | -1 | the sign of the fitted coefficient on age |
| `sign_check.age.univariate_direction` | `66364583` | scalar | -1 | the sign of age's own single-feature AUC on train minus 0.5 |
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
| `sign_check.limit_bal.agrees` | `103d99fb` | scalar | 1 | 1 when the fitted sign on limit_bal agrees with its univariate direction, 0 when it does not |
| `sign_check.limit_bal.coef_sign` | `a6d01381` | scalar | -1 | the sign of the fitted coefficient on limit_bal |
| `sign_check.limit_bal.univariate_direction` | `56d284d6` | scalar | -1 | the sign of limit_bal's own single-feature AUC on train minus 0.5 |
| `sign_check.n_disagreements` | `66ce738a` | scalar | 2 | retained features whose fitted sign contradicts their univariate direction, of 9 checked |
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
| tool calls | 13 (run_model 1, profile_data 1, compute_metrics 1, check_leakage 1, check_collinearity 1, challenger_compare 1, retrieve_guidance 7) |
| plan steps (bounded loop) | 0 |
| LLM calls | 0 () |
| re-asks | 0 |
| repair rounds | 0 |
| tokens in / out | 0 / 0 |
| notional cost (USD) | 0.0000 |
| wall-clock (s) | 1.02 |
| subject run (s) | 1.17 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | fake |
| model | none: no model answered |
| run id | credit_default-rules_only-20260918T065332Z-bd5861e9 |

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
