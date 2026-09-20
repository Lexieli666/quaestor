---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: rules_only
model: fake
run_id: credit_default-rules_only-20260918T065319Z-bd5861e9
data_mode: synthetic
synthetic_n: 5000
grounding_precision_pre: 1.0000
grounding_precision_post: 1.0000
n_claims: 228
n_findings_by_severity: {high: 1, medium: 1, low: 0, info: 0}
generated: "2026-09-18T06:53:19Z"
illustrative: false
---

# Validation report — `credit_default` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `credit_default` v1.0 | `rules_only` | fake | synthetic, n = 5000 | 1.0000 → 1.0000 | 1 / 1 / 0 / 0 |
<!-- quaestor:renderer:end -->

This section follows the model risk management guidance at [[reg:SR26-2:V.1.b]].
The value of `calibration_slope.test` is 1.197 [[art:c9a03fe6:calibration_slope.test]].
The value of `calibration_slope.train` is 1.383 [[art:45dafd11:calibration_slope.train]].
The value of `challenger.delta_auc` is 0.01222 [[art:2ab4af27:challenger.delta_auc]].
The value of `condition_number` is 6.185 [[art:36392379:condition_number]].
The value of `csi.max` is 0.4064 [[art:3f7f79cf:csi.max]].
The value of `metrics.test.auc` is 0.9755 [[art:8f522f3b:metrics.test.auc]].
The value of `metrics.test.brier` is 0.04247 [[art:d4f27e13:metrics.test.brier]].
The value of `metrics.test.event_rate` is 0.2247 [[art:9209d200:metrics.test.event_rate]].
The value of `metrics.test.gini` is 0.951 [[art:f927e3cd:metrics.test.gini]].
The value of `metrics.test.ks` is 0.8784 [[art:81bee194:metrics.test.ks]].
The value of `metrics.test.logloss` is 0.167 [[art:aa620b5e:metrics.test.logloss]].
The value of `metrics.test.mean_predicted` is 0.233 [[art:0b9b6a1e:metrics.test.mean_predicted]].
The value of `metrics.test.n` is 1500 [[art:64fcf14d:metrics.test.n]].
The value of `metrics.train.auc` is 0.9812 [[art:da2cd01d:metrics.train.auc]].
The value of `metrics.train.brier` is 0.03817 [[art:959b3159:metrics.train.brier]].
The value of `metrics.train.event_rate` is 0.2246 [[art:133a5ff8:metrics.train.event_rate]].
The value of `metrics.train.gini` is 0.9624 [[art:23cb4057:metrics.train.gini]].
The value of `metrics.train.ks` is 0.8895 [[art:7a126f15:metrics.train.ks]].
The value of `metrics.train.logloss` is 0.1505 [[art:417d98d9:metrics.train.logloss]].
The value of `metrics.train.mean_predicted` is 0.2246 [[art:1fa024a6:metrics.train.mean_predicted]].
The value of `metrics.train.n` is 3500 [[art:564683ee:metrics.train.n]].
The value of `profile.test.n` is 1500 [[art:2193cf5f:profile.test.n]].
The value of `profile.train.n` is 3500 [[art:2510d49d:profile.train.n]].
The value of `psi.max` is 0.01789 [[art:1b87de3e:psi.max]].
The value of `runtime.max_seconds` is 300 [[art:2ad8d1a5:runtime.max_seconds]].
The value of `threshold.package.auc.test.min` is 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]].
The value of `threshold.package.brier.test.max` is 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]].
The value of `threshold.package.calibration_slope.test.max` is 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The value of `threshold.package.calibration_slope.test.min` is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
The value of `vif.max` is 8.181 [[art:4afdc4f1:vif.max]].

## 2. Conceptual soundness

This section follows the model risk management guidance at [[reg:SR26-2:V.1.a]].
The value of `ablation.age.delta_auc` is 0.00005613 [[art:786b509d:ablation.age.delta_auc]].
The value of `ablation.baseline_auc` is 0.9755 [[art:8e58476a:ablation.baseline_auc]].
The value of `ablation.bill_mean_6m.delta_auc` is -0.005228 [[art:a4586b58:ablation.bill_mean_6m.delta_auc]].
The value of `ablation.bill_trend_6m.delta_auc` is -0.0005537 [[art:54e6a418:ablation.bill_trend_6m.delta_auc]].
The value of `ablation.delinq_count_6m.delta_auc` is 0.000005103 [[art:3730f6e2:ablation.delinq_count_6m.delta_auc]].
The value of `ablation.delinq_last.delta_auc` is -0.0009211 [[art:43d4225a:ablation.delinq_last.delta_auc]].
The value of `ablation.delinq_max_6m.delta_auc` is 0.0001607 [[art:b1793491:ablation.delinq_max_6m.delta_auc]].
The value of `ablation.limit_bal.delta_auc` is 0.0006175 [[art:4b976d60:ablation.limit_bal.delta_auc]].
The value of `ablation.pay_amt_next.delta_auc` is -0.2275 [[art:cf6c0563:ablation.pay_amt_next.delta_auc]].
The value of `ablation.pay_ratio_last.delta_auc` is 0.0001863 [[art:c577925a:ablation.pay_ratio_last.delta_auc]].
The value of `ablation.pay_ratio_mean_6m.delta_auc` is -0.0009594 [[art:54c168fb:ablation.pay_ratio_mean_6m.delta_auc]].
The value of `ablation.utilisation.delta_auc` is -0.0004235 [[art:009bc4f1:ablation.utilisation.delta_auc]].
The value of `challenger.auc` is 0.9877 [[art:d2646bc7:challenger.auc]].
The value of `challenger.brier` is 0.02542 [[art:0a224a0a:challenger.brier]].
The value of `challenger.delta_auc` is 0.01222 [[art:2ab4af27:challenger.delta_auc]].
The value of `metrics.test.auc` is 0.9755 [[art:8f522f3b:metrics.test.auc]].
The value of `metrics.test.brier` is 0.04247 [[art:d4f27e13:metrics.test.brier]].
The value of `sign_check.age.agrees` is 1 [[art:4116add1:sign_check.age.agrees]].
The value of `sign_check.age.coef_sign` is -1 [[art:6172eb93:sign_check.age.coef_sign]].
The value of `sign_check.age.univariate_direction` is -1 [[art:66364583:sign_check.age.univariate_direction]].
The value of `sign_check.bill_mean_6m.agrees` is 0 [[art:4df8b747:sign_check.bill_mean_6m.agrees]].
The value of `sign_check.bill_mean_6m.coef_sign` is 1 [[art:a457c04a:sign_check.bill_mean_6m.coef_sign]].
The value of `sign_check.bill_mean_6m.univariate_direction` is -1 [[art:23b89c5d:sign_check.bill_mean_6m.univariate_direction]].
The value of `sign_check.bill_trend_6m.agrees` is 0 [[art:c0f6d07d:sign_check.bill_trend_6m.agrees]].
The value of `sign_check.bill_trend_6m.coef_sign` is 1 [[art:abd4aaba:sign_check.bill_trend_6m.coef_sign]].
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
The value of `sign_check.n_disagreements` is 6 [[art:75159a84:sign_check.n_disagreements]].
The value of `sign_check.pay_amt_next.agrees` is 1 [[art:01bd6313:sign_check.pay_amt_next.agrees]].
The value of `sign_check.pay_amt_next.coef_sign` is -1 [[art:6fc540c1:sign_check.pay_amt_next.coef_sign]].
The value of `sign_check.pay_amt_next.univariate_direction` is -1 [[art:1bec400a:sign_check.pay_amt_next.univariate_direction]].
The value of `sign_check.pay_ratio_last.agrees` is 0 [[art:79abee77:sign_check.pay_ratio_last.agrees]].
The value of `sign_check.pay_ratio_last.coef_sign` is 1 [[art:f018263e:sign_check.pay_ratio_last.coef_sign]].
The value of `sign_check.pay_ratio_last.univariate_direction` is -1 [[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]].
The value of `sign_check.pay_ratio_mean_6m.agrees` is 0 [[art:51914c14:sign_check.pay_ratio_mean_6m.agrees]].
The value of `sign_check.pay_ratio_mean_6m.coef_sign` is 1 [[art:8547787e:sign_check.pay_ratio_mean_6m.coef_sign]].
The value of `sign_check.pay_ratio_mean_6m.univariate_direction` is -1 [[art:24dcef24:sign_check.pay_ratio_mean_6m.univariate_direction]].
The value of `sign_check.utilisation.agrees` is 1 [[art:d0c9a130:sign_check.utilisation.agrees]].
The value of `sign_check.utilisation.coef_sign` is 1 [[art:85badc3c:sign_check.utilisation.coef_sign]].
The value of `sign_check.utilisation.univariate_direction` is 1 [[art:f0995196:sign_check.utilisation.univariate_direction]].
The value of `threshold.E1.delta_auc` is 0.03 [[art:e042774c:threshold.E1.delta_auc]].

## 3. Data integrity and drift

This section follows the model risk management guidance at [[reg:SR26-2:V.1.a]].
The value of `csi.age` is 0.00125 [[art:584faff4:csi.age]].
The value of `csi.bill_mean_6m` is 0.0105 [[art:f374dbd7:csi.bill_mean_6m]].
The value of `csi.bill_trend_6m` is 0.00567 [[art:8bb46253:csi.bill_trend_6m]].
The value of `csi.delinq_count_6m` is 0.002143 [[art:4564aa47:csi.delinq_count_6m]].
The value of `csi.delinq_last` is 0.0295 [[art:cd29d613:csi.delinq_last]].
The value of `csi.delinq_max_6m` is 0.002782 [[art:2fe28db6:csi.delinq_max_6m]].
The value of `csi.limit_bal` is 0.007188 [[art:cb617a64:csi.limit_bal]].
The value of `csi.max` is 0.4064 [[art:3f7f79cf:csi.max]].
The value of `csi.pay_amt_next` is 0.4064 [[art:e708fa25:csi.pay_amt_next]].
The value of `csi.pay_ratio_last` is 0.003912 [[art:c083b28c:csi.pay_ratio_last]].
The value of `csi.pay_ratio_mean_6m` is 0.003519 [[art:8f1dbe89:csi.pay_ratio_mean_6m]].
The value of `csi.utilisation` is 0.01304 [[art:b1f362df:csi.utilisation]].
The value of `leakage.duplicates.train` is 0 [[art:4474c227:leakage.duplicates.train]].
The value of `leakage.name_screen.n_matched` is 0 [[art:407e62be:leakage.name_screen.n_matched]].
The value of `leakage.overlap` is 0 [[art:4c9fcd09:leakage.overlap]].
The value of `leakage.overlap.features` is 0 [[art:0fec8048:leakage.overlap.features]].
The value of `leakage.overlap.ids` is 0 [[art:63d37fc5:leakage.overlap.ids]].
The value of `leakage.target_corr.max_single_feature_auc` is 0.945 [[art:5b5e98c2:leakage.target_corr.max_single_feature_auc]].
The value of `leakage.timing.n_flagged` is 1 [[art:e3a31f6a:leakage.timing.n_flagged]].
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
The value of `psi.max` is 0.01789 [[art:1b87de3e:psi.max]].
The value of `psi.pay_amt_next` is 0.01789 [[art:996bb509:psi.pay_amt_next]].
The value of `psi.pay_ratio_last` is 0.004966 [[art:3af2ca29:psi.pay_ratio_last]].
The value of `psi.pay_ratio_mean_6m` is 0.0055 [[art:2c5baeb2:psi.pay_ratio_mean_6m]].
The value of `psi.utilisation` is 0.004244 [[art:451e0780:psi.utilisation]].
The value of `psi.y_score` is 0.01199 [[art:05f120d2:psi.y_score]].
The value of `threshold.D1.missing_gap` is 0.1 [[art:9cce25ea:threshold.D1.missing_gap]].
The value of `threshold.L1.single_feature_auc` is 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]].
The value of `threshold.L2.overlap` is 0.005 [[art:9f336eaf:threshold.L2.overlap]].
The value of `threshold.L2.overlap.features_effective` is 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].
The value of `threshold.S1.psi` is 0.25 [[art:278b9016:threshold.S1.psi]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
Candidates raised on this section's material: L1; L1 (see the findings section).

## 4. Outcomes analysis

This section follows the model risk management guidance at [[reg:SR26-2:V.1.b]].
The value of `calibration.mean_rel_gap.test` is 0.03717 [[art:6a845d81:calibration.mean_rel_gap.test]].
The value of `calibration.mean_rel_gap.train` is 0.00008632 [[art:f7447f34:calibration.mean_rel_gap.train]].
The value of `calibration_intercept.test` is -0.0558 [[art:56745cf2:calibration_intercept.test]].
The value of `calibration_intercept.train` is 0.2246 [[art:d556f341:calibration_intercept.train]].
The value of `calibration_slope.test` is 1.197 [[art:c9a03fe6:calibration_slope.test]].
The value of `calibration_slope.train` is 1.383 [[art:45dafd11:calibration_slope.train]].
The value of `deciles.test.top2_capture` is 0.822 [[art:5690757b:deciles.test.top2_capture]].
The value of `deciles.train.top2_capture` is 0.8422 [[art:55242963:deciles.train.top2_capture]].
The value of `metrics.test.auc` is 0.9755 [[art:8f522f3b:metrics.test.auc]].
The value of `metrics.test.brier` is 0.04247 [[art:d4f27e13:metrics.test.brier]].
The value of `metrics.test.event_rate` is 0.2247 [[art:9209d200:metrics.test.event_rate]].
The value of `metrics.test.gini` is 0.951 [[art:f927e3cd:metrics.test.gini]].
The value of `metrics.test.ks` is 0.8784 [[art:81bee194:metrics.test.ks]].
The value of `metrics.test.logloss` is 0.167 [[art:aa620b5e:metrics.test.logloss]].
The value of `metrics.test.mean_predicted` is 0.233 [[art:0b9b6a1e:metrics.test.mean_predicted]].
The value of `metrics.test.n` is 1500 [[art:64fcf14d:metrics.test.n]].
The value of `metrics.train.auc` is 0.9812 [[art:da2cd01d:metrics.train.auc]].
The value of `metrics.train.brier` is 0.03817 [[art:959b3159:metrics.train.brier]].
The value of `metrics.train.event_rate` is 0.2246 [[art:133a5ff8:metrics.train.event_rate]].
The value of `metrics.train.gini` is 0.9624 [[art:23cb4057:metrics.train.gini]].
The value of `metrics.train.ks` is 0.8895 [[art:7a126f15:metrics.train.ks]].
The value of `metrics.train.logloss` is 0.1505 [[art:417d98d9:metrics.train.logloss]].
The value of `metrics.train.mean_predicted` is 0.2246 [[art:1fa024a6:metrics.train.mean_predicted]].
The value of `metrics.train.n` is 3500 [[art:564683ee:metrics.train.n]].
The value of `psi.age` is 0.008124 [[art:f9255a0a:psi.age]].
The value of `psi.bill_mean_6m` is 0.007124 [[art:028e4281:psi.bill_mean_6m]].
The value of `psi.bill_trend_6m` is 0.00958 [[art:c247a6f2:psi.bill_trend_6m]].
The value of `psi.delinq_count_6m` is 0.002069 [[art:61491d02:psi.delinq_count_6m]].
The value of `psi.delinq_last` is 0.00285 [[art:03bd52e7:psi.delinq_last]].
The value of `psi.delinq_max_6m` is 0.005498 [[art:7a82e7f3:psi.delinq_max_6m]].
The value of `psi.limit_bal` is 0.01095 [[art:601cdba2:psi.limit_bal]].
The value of `psi.max` is 0.01789 [[art:1b87de3e:psi.max]].
The value of `psi.pay_amt_next` is 0.01789 [[art:996bb509:psi.pay_amt_next]].
The value of `psi.pay_ratio_last` is 0.004966 [[art:3af2ca29:psi.pay_ratio_last]].
The value of `psi.pay_ratio_mean_6m` is 0.0055 [[art:2c5baeb2:psi.pay_ratio_mean_6m]].
The value of `psi.utilisation` is 0.004244 [[art:451e0780:psi.utilisation]].
The value of `psi.y_score` is 0.01199 [[art:05f120d2:psi.y_score]].
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
Calibration by decile of predicted probability on test [[art:1744d380:calibration.test]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 1.335e-08 | 0 | 150 |
| 2 | 1.357e-05 | 0 | 150 |
| 3 | 0.0005755 | 0.02667 | 150 |
| 4 | 0.005974 | 0 | 150 |
| 5 | 0.02678 | 0 | 150 |
| 6 | 0.06532 | 0.01333 | 150 |
| 7 | 0.1319 | 0.06667 | 150 |
| 8 | 0.3384 | 0.2933 | 150 |
| 9 | 0.7901 | 0.88 | 150 |
| 10 | 0.971 | 0.9667 | 150 |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table deciles.test -->
Decile separation on test; decile 1 holds the highest probabilities [[art:ffdb3017:deciles.test]]:

| decile | count | events | event_rate | lift |
|---|---|---|---|---|
| 1 | 150 | 145 | 0.9667 | 4.303 |
| 2 | 150 | 132 | 0.88 | 3.917 |
| 3 | 150 | 44 | 0.2933 | 1.306 |
| 4 | 150 | 10 | 0.06667 | 0.2967 |
| 5 | 150 | 2 | 0.01333 | 0.05935 |
| 6 | 150 | 0 | 0 | 0 |
| 7 | 150 | 0 | 0 | 0 |
| 8 | 150 | 4 | 0.02667 | 0.1187 |
| 9 | 150 | 0 | 0 | 0 |
| 10 | 150 | 0 | 0 | 0 |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table thresholds.evaluation -->
Every threshold package.yaml declares, with its bound, the recomputed value and the outcome [[art:f41614b5:thresholds.evaluation]]:

| metric | split | bound | value | result |
|---|---|---|---|---|
| auc | test | minimum 0.7 | 0.9755 | pass |
| brier | test | maximum 0.2 | 0.04247 | pass |
| calibration_slope | test | minimum 0.8 | 1.197 | pass |
| calibration_slope | test | maximum 1.2 | 1.197 | pass |
| psi |  | maximum 0.25 | 0.01789 | pass |
<!-- quaestor:renderer:end -->
Candidates raised on this section's material: C1 (see the findings section).

## 5. Sensitivity and scenario analysis

This section follows the model risk management guidance at [[reg:SR26-2:V.1.a]].
The value of `condition_number` is 6.185 [[art:36392379:condition_number]].
The value of `threshold.M1.condition_number` is 30 [[art:7e52fd7a:threshold.M1.condition_number]].
The value of `threshold.M1.vif` is 10 [[art:aeb4f33c:threshold.M1.vif]].
The value of `vif.age` is 1.002 [[art:8021b06e:vif.age]].
The value of `vif.bill_mean_6m` is 8.181 [[art:d5ab7306:vif.bill_mean_6m]].
The value of `vif.bill_trend_6m` is 1.225 [[art:0cb3df89:vif.bill_trend_6m]].
The value of `vif.delinq_count_6m` is 2.561 [[art:87890613:vif.delinq_count_6m]].
The value of `vif.delinq_last` is 1.422 [[art:c18221d4:vif.delinq_last]].
The value of `vif.delinq_max_6m` is 2.408 [[art:4b239ec5:vif.delinq_max_6m]].
The value of `vif.limit_bal` is 4.81 [[art:8209ea46:vif.limit_bal]].
The value of `vif.max` is 8.181 [[art:4afdc4f1:vif.max]].
The value of `vif.pay_amt_next` is 2.206 [[art:68806d80:vif.pay_amt_next]].
The value of `vif.pay_ratio_last` is 7.268 [[art:bec24796:vif.pay_ratio_last]].
The value of `vif.pay_ratio_mean_6m` is 7.526 [[art:000b6208:vif.pay_ratio_mean_6m]].
The value of `vif.utilisation` is 3.215 [[art:ec978947:vif.utilisation]].

## 6. Findings and recommendations

This section follows the model risk management guidance at [[reg:SR26-2:VI.3]].

### F-001 · L1 leakage · severity **high**

**A `L1` finding, raised by `check_leakage+load_package` at severity `high`.**
Its evidence is the artifacts cited in this section; the check's own account of it is recorded in `findings.json`.

### F-002 · C1 calibration · severity **medium**

**A `C1` finding, raised by `compute_metrics` at severity `medium`.**
Its evidence is the artifacts cited in this section; the check's own account of it is recorded in `findings.json`.
The value of `calibration_slope.train` is 1.383 [[art:45dafd11:calibration_slope.train]].
The value of `leakage.target_corr.max_single_feature_auc` is 0.945 [[art:5b5e98c2:leakage.target_corr.max_single_feature_auc]].
The value of `leakage.timing.n_flagged` is 1 [[art:e3a31f6a:leakage.timing.n_flagged]].
The value of `sign_check.bill_mean_6m.agrees` is 0 [[art:4df8b747:sign_check.bill_mean_6m.agrees]].
The value of `sign_check.bill_mean_6m.coef_sign` is 1 [[art:a457c04a:sign_check.bill_mean_6m.coef_sign]].
The value of `sign_check.bill_mean_6m.univariate_direction` is -1 [[art:23b89c5d:sign_check.bill_mean_6m.univariate_direction]].
The value of `sign_check.bill_trend_6m.agrees` is 0 [[art:c0f6d07d:sign_check.bill_trend_6m.agrees]].
The value of `sign_check.bill_trend_6m.coef_sign` is 1 [[art:abd4aaba:sign_check.bill_trend_6m.coef_sign]].
The value of `sign_check.bill_trend_6m.univariate_direction` is -1 [[art:a9bff389:sign_check.bill_trend_6m.univariate_direction]].
The value of `sign_check.delinq_max_6m.agrees` is 0 [[art:c946359c:sign_check.delinq_max_6m.agrees]].
The value of `sign_check.delinq_max_6m.coef_sign` is -1 [[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]].
The value of `sign_check.delinq_max_6m.univariate_direction` is 1 [[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]].
The value of `sign_check.limit_bal.agrees` is 0 [[art:0278aad1:sign_check.limit_bal.agrees]].
The value of `sign_check.limit_bal.coef_sign` is 1 [[art:6af6aef2:sign_check.limit_bal.coef_sign]].
The value of `sign_check.limit_bal.univariate_direction` is -1 [[art:56d284d6:sign_check.limit_bal.univariate_direction]].
The value of `sign_check.pay_ratio_last.agrees` is 0 [[art:79abee77:sign_check.pay_ratio_last.agrees]].
The value of `sign_check.pay_ratio_last.coef_sign` is 1 [[art:f018263e:sign_check.pay_ratio_last.coef_sign]].
The value of `sign_check.pay_ratio_last.univariate_direction` is -1 [[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]].
The value of `sign_check.pay_ratio_mean_6m.agrees` is 0 [[art:51914c14:sign_check.pay_ratio_mean_6m.agrees]].
The value of `sign_check.pay_ratio_mean_6m.coef_sign` is 1 [[art:8547787e:sign_check.pay_ratio_mean_6m.coef_sign]].
The value of `sign_check.pay_ratio_mean_6m.univariate_direction` is -1 [[art:24dcef24:sign_check.pay_ratio_mean_6m.univariate_direction]].
The value of `threshold.C1.calibration_slope.max` is 1.2 [[art:b6672579:threshold.C1.calibration_slope.max]].
The value of `threshold.L1.single_feature_auc` is 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]].
<!-- quaestor:renderer:begin table calibration.train -->
Calibration by decile of predicted probability on train [[art:309e30bb:calibration.train]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 2.708e-09 | 0 | 350 |
| 2 | 1.404e-05 | 0.005714 | 350 |
| 3 | 0.0005028 | 0.005714 | 350 |
| 4 | 0.004695 | 0.008571 | 350 |
| 5 | 0.02105 | 0.01143 | 350 |
| 6 | 0.05843 | 0.01714 | 350 |
| 7 | 0.119 | 0.02571 | 350 |
| 8 | 0.3153 | 0.28 | 350 |
| 9 | 0.755 | 0.9 | 350 |
| 10 | 0.9716 | 0.9914 | 350 |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table leakage.target_corr -->
Each feature against the outcome on train, on its own [[art:12cb4333:leakage.target_corr]]:

| feature | abs_corr | single_feature_auc | numeric |
|---|---|---|---|
| limit_bal | 0.0536 | 0.5417 | true |
| age | 0.01687 | 0.5073 | true |
| utilisation | 0.02702 | 0.5134 | true |
| pay_ratio_last | 0.07687 | 0.5525 | true |
| pay_ratio_mean_6m | 0.09208 | 0.5614 | true |
| delinq_last | 0.3585 | 0.6831 | true |
| delinq_count_6m | 0.2158 | 0.6369 | true |
| delinq_max_6m | 0.1832 | 0.6221 | true |
| bill_mean_6m | 0.03389 | 0.524 | true |
| bill_trend_6m | 0.03665 | 0.5058 | true |
| pay_amt_next | 0.346 | 0.945 | true |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table leakage.timing -->
Each feature's declared timing; flagged means during or after the outcome [[art:0dad290e:leakage.timing]]:

| feature | timing | flagged |
|---|---|---|
| limit_bal | at_origination | false |
| age | at_origination | false |
| utilisation | before_period_start | false |
| utilisation_mean_6m | before_period_start | false |
| pay_ratio_last | before_period_start | false |
| pay_ratio_mean_6m | before_period_start | false |
| delinq_last | before_period_start | false |
| delinq_count_6m | before_period_start | false |
| delinq_max_6m | before_period_start | false |
| bill_mean_6m | before_period_start | false |
| bill_last | before_period_start | false |
| bill_trend_6m | before_period_start | false |
| pay_amt_next | after_outcome | true |
<!-- quaestor:renderer:end -->

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1, S1), `compute_metrics` (T1, O1), `check_leakage` (L2), `check_collinearity` (M1), `challenger_compare` (E1).

### Open items

No open item was recorded for this validation.

## 7. Ongoing monitoring recommendations

This section follows the model risk management guidance at [[reg:SR26-2:V.2]].
The value of `calibration_slope.test` is 1.197 [[art:c9a03fe6:calibration_slope.test]].
The value of `metrics.test.auc` is 0.9755 [[art:8f522f3b:metrics.test.auc]].
The value of `metrics.test.brier` is 0.04247 [[art:d4f27e13:metrics.test.brier]].
The value of `psi.max` is 0.01789 [[art:1b87de3e:psi.max]].
The value of `rule.calibration_first_event_rate` is 0.05 [[art:42f1351e:rule.calibration_first_event_rate]].
The value of `threshold.package.auc.test.min` is 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]].
The value of `threshold.package.brier.test.max` is 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]].
The value of `threshold.package.calibration_slope.test.max` is 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The value of `threshold.package.calibration_slope.test.min` is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].

## Appendix A — Claims

Grounding precision 1.0000 before repair (228 of 228 claims verified) and 1.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 31/31; conceptual_soundness 52/52; data_integrity 42/42; outcomes 55/55; sensitivity 15/15; findings 23/23; monitoring 10/10.

Developer claims: The package declares 2 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). See Appendix D.

Excluded numeric tokens (not claims): citation_hash (c9a03fe6, 45dafd11, 2ab4af27, 36392379); regulatory_section_id (SR26-2:V.1.b, SR26-2:V.1.a, SR26-2:VI.3, SR26-2:V.2); finding_id (F-001, F-002).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The value of `calibration_slope.test` is 1.197 . | 1.197 | ratio | calibration_slope |  | eq | `[[art:c9a03fe6:calibration_slope.test]]` | verified | 1.19744242 |
| 2 | summary | The value of `calibration_slope.train` is 1.383 . | 1.383 | ratio | calibration_slope |  | eq | `[[art:45dafd11:calibration_slope.train]]` | verified | 1.383137681 |
| 3 | summary | The value of `challenger.delta_auc` is 0.01222 . | 0.01222 | ratio | challenger |  | eq | `[[art:2ab4af27:challenger.delta_auc]]` | verified | 0.01222409046 |
| 4 | summary | The value of `condition_number` is 6.185 . | 6.185 | ratio | condition_number |  | eq | `[[art:36392379:condition_number]]` | verified | 6.185189657 |
| 5 | summary | The value of `csi.max` is 0.4064 . | 0.4064 | ratio | csi |  | eq | `[[art:3f7f79cf:csi.max]]` | verified | 0.4063916509 |
| 6 | summary | The value of `metrics.test.auc` is 0.9755 . | 0.9755 | ratio | metrics |  | eq | `[[art:8f522f3b:metrics.test.auc]]` | verified | 0.9755058926 |
| 7 | summary | The value of `metrics.test.brier` is 0.04247 . | 0.04247 | ratio | metrics |  | eq | `[[art:d4f27e13:metrics.test.brier]]` | verified | 0.04247487168 |
| 8 | summary | The value of `metrics.test.event_rate` is 0.2247 . | 0.2247 | ratio | metrics |  | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 9 | summary | The value of `metrics.test.gini` is 0.951 . | 0.951 | ratio | metrics |  | eq | `[[art:f927e3cd:metrics.test.gini]]` | verified | 0.9510117852 |
| 10 | summary | The value of `metrics.test.ks` is 0.8784 . | 0.8784 | ratio | metrics |  | eq | `[[art:81bee194:metrics.test.ks]]` | verified | 0.8784403377 |
| 11 | summary | The value of `metrics.test.logloss` is 0.167 . | 0.167 | ratio | metrics |  | eq | `[[art:aa620b5e:metrics.test.logloss]]` | verified | 0.1670045909 |
| 12 | summary | The value of `metrics.test.mean_predicted` is 0.233 . | 0.233 | ratio | metrics |  | eq | `[[art:0b9b6a1e:metrics.test.mean_predicted]]` | verified | 0.2330182196 |
| 13 | summary | The value of `metrics.test.n` is 1500 . | 1500 | ratio | metrics |  | eq | `[[art:64fcf14d:metrics.test.n]]` | verified | 1500 |
| 14 | summary | The value of `metrics.train.auc` is 0.9812 . | 0.9812 | ratio | metrics |  | eq | `[[art:da2cd01d:metrics.train.auc]]` | verified | 0.9811790152 |
| 15 | summary | The value of `metrics.train.brier` is 0.03817 . | 0.03817 | ratio | metrics |  | eq | `[[art:959b3159:metrics.train.brier]]` | verified | 0.03816687592 |
| 16 | summary | The value of `metrics.train.event_rate` is 0.2246 . | 0.2246 | ratio | metrics |  | eq | `[[art:133a5ff8:metrics.train.event_rate]]` | verified | 0.2245714286 |
| 17 | summary | The value of `metrics.train.gini` is 0.9624 . | 0.9624 | ratio | metrics |  | eq | `[[art:23cb4057:metrics.train.gini]]` | verified | 0.9623580305 |
| 18 | summary | The value of `metrics.train.ks` is 0.8895 . | 0.8895 | ratio | metrics |  | eq | `[[art:7a126f15:metrics.train.ks]]` | verified | 0.8894536106 |
| 19 | summary | The value of `metrics.train.logloss` is 0.1505 . | 0.1505 | ratio | metrics |  | eq | `[[art:417d98d9:metrics.train.logloss]]` | verified | 0.1504741108 |
| 20 | summary | The value of `metrics.train.mean_predicted` is 0.2246 . | 0.2246 | ratio | metrics |  | eq | `[[art:1fa024a6:metrics.train.mean_predicted]]` | verified | 0.2245520437 |
| 21 | summary | The value of `metrics.train.n` is 3500 . | 3500 | ratio | metrics |  | eq | `[[art:564683ee:metrics.train.n]]` | verified | 3500 |
| 22 | summary | The value of `profile.test.n` is 1500 . | 1500 | ratio | profile |  | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 23 | summary | The value of `profile.train.n` is 3500 . | 3500 | ratio | profile |  | eq | `[[art:2510d49d:profile.train.n]]` | verified | 3500 |
| 24 | summary | The value of `psi.max` is 0.01789 . | 0.01789 | ratio | psi |  | eq | `[[art:1b87de3e:psi.max]]` | verified | 0.01789488592 |
| 25 | summary | The value of `runtime.max_seconds` is 300 . | 300 | ratio | runtime |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 26 | summary | The value of `threshold.package.auc.test.min` is 0.7 . | 0.7 | ratio | threshold |  | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 27 | summary | The value of `threshold.package.brier.test.max` is 0.2 . | 0.2 | ratio | threshold |  | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 28 | summary | The value of `threshold.package.calibration_slope.test.max`… | 1.2 | ratio | threshold |  | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 29 | summary | The value of `threshold.package.calibration_slope.test.min`… | 0.8 | ratio | threshold |  | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 30 | summary | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 31 | summary | The value of `vif.max` is 8.181 . | 8.181 | ratio | vif |  | eq | `[[art:4afdc4f1:vif.max]]` | verified | 8.181114607 |
| 32 | conceptual_soundness | The value of `ablation.age.delta_auc` is 0.00005613 . | 5.613e-05 | ratio | ablation |  | eq | `[[art:786b509d:ablation.age.delta_auc]]` | verified | 5.613232942e-05 |
| 33 | conceptual_soundness | The value of `ablation.baseline_auc` is 0.9755 . | 0.9755 | ratio | ablation |  | eq | `[[art:8e58476a:ablation.baseline_auc]]` | verified | 0.9755058926 |
| 34 | conceptual_soundness | The value of `ablation.bill_mean_6m.delta_auc` is -0.005228… | -0.005228 | ratio | ablation |  | eq | `[[art:a4586b58:ablation.bill_mean_6m.delta_auc]]` | verified | -0.005227961044 |
| 35 | conceptual_soundness | The value of `ablation.bill_trend_6m.delta_auc` is -0.000553… | -0.0005537 | ratio | ablation |  | eq | `[[art:54e6a418:ablation.bill_trend_6m.delta_auc]]` | verified | -0.0005536688856 |
| 36 | conceptual_soundness | The value of `ablation.delinq_count_6m.delta_auc` is 0.00000… | 5.103e-06 | ratio | ablation |  | eq | `[[art:3730f6e2:ablation.delinq_count_6m.delta_auc]]` | verified | 5.102939038e-06 |
| 37 | conceptual_soundness | The value of `ablation.delinq_last.delta_auc` is -0.0009211… | -0.0009211 | ratio | ablation |  | eq | `[[art:43d4225a:ablation.delinq_last.delta_auc]]` | verified | -0.0009210804963 |
| 38 | conceptual_soundness | The value of `ablation.delinq_max_6m.delta_auc` is 0.0001607… | 0.0001607 | ratio | ablation |  | eq | `[[art:b1793491:ablation.delinq_max_6m.delta_auc]]` | verified | 0.0001607425797 |
| 39 | conceptual_soundness | The value of `ablation.limit_bal.delta_auc` is 0.0006175 . | 0.0006175 | ratio | ablation |  | eq | `[[art:4b976d60:ablation.limit_bal.delta_auc]]` | verified | 0.0006174556236 |
| 40 | conceptual_soundness | The value of `ablation.pay_amt_next.delta_auc` is -0.2275 . | -0.2275 | ratio | ablation |  | eq | `[[art:cf6c0563:ablation.pay_amt_next.delta_auc]]` | verified | -0.2275170885 |
| 41 | conceptual_soundness | The value of `ablation.pay_ratio_last.delta_auc` is 0.000186… | 0.0001863 | ratio | ablation |  | eq | `[[art:c577925a:ablation.pay_ratio_last.delta_auc]]` | verified | 0.0001862572749 |
| 42 | conceptual_soundness | The value of `ablation.pay_ratio_mean_6m.delta_auc` is -0.00… | -0.0009594 | ratio | ablation |  | eq | `[[art:54c168fb:ablation.pay_ratio_mean_6m.delta_auc]]` | verified | -0.0009593525391 |
| 43 | conceptual_soundness | The value of `ablation.utilisation.delta_auc` is -0.0004235… | -0.0004235 | ratio | ablation |  | eq | `[[art:009bc4f1:ablation.utilisation.delta_auc]]` | verified | -0.0004235439401 |
| 44 | conceptual_soundness | The value of `challenger.auc` is 0.9877 . | 0.9877 | ratio | challenger |  | eq | `[[art:d2646bc7:challenger.auc]]` | verified | 0.9877299831 |
| 45 | conceptual_soundness | The value of `challenger.brier` is 0.02542 . | 0.02542 | ratio | challenger |  | eq | `[[art:0a224a0a:challenger.brier]]` | verified | 0.02542316584 |
| 46 | conceptual_soundness | The value of `challenger.delta_auc` is 0.01222 . | 0.01222 | ratio | challenger |  | eq | `[[art:2ab4af27:challenger.delta_auc]]` | verified | 0.01222409046 |
| 47 | conceptual_soundness | The value of `metrics.test.auc` is 0.9755 . | 0.9755 | ratio | metrics |  | eq | `[[art:8f522f3b:metrics.test.auc]]` | verified | 0.9755058926 |
| 48 | conceptual_soundness | The value of `metrics.test.brier` is 0.04247 . | 0.04247 | ratio | metrics |  | eq | `[[art:d4f27e13:metrics.test.brier]]` | verified | 0.04247487168 |
| 49 | conceptual_soundness | The value of `sign_check.age.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:4116add1:sign_check.age.agrees]]` | verified | 1 |
| 50 | conceptual_soundness | The value of `sign_check.age.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:6172eb93:sign_check.age.coef_sign]]` | verified | -1 |
| 51 | conceptual_soundness | The value of `sign_check.age.univariate_direction` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:66364583:sign_check.age.univariate_direction]]` | verified | -1 |
| 52 | conceptual_soundness | The value of `sign_check.bill_mean_6m.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:4df8b747:sign_check.bill_mean_6m.agrees]]` | verified | 0 |
| 53 | conceptual_soundness | The value of `sign_check.bill_mean_6m.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:a457c04a:sign_check.bill_mean_6m.coef_sign]]` | verified | 1 |
| 54 | conceptual_soundness | The value of `sign_check.bill_mean_6m.univariate_direction`… | -1 | ratio | sign_check |  | eq | `[[art:23b89c5d:sign_check.bill_mean_6m.univariate_direction]]` | verified | -1 |
| 55 | conceptual_soundness | The value of `sign_check.bill_trend_6m.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:c0f6d07d:sign_check.bill_trend_6m.agrees]]` | verified | 0 |
| 56 | conceptual_soundness | The value of `sign_check.bill_trend_6m.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:abd4aaba:sign_check.bill_trend_6m.coef_sign]]` | verified | 1 |
| 57 | conceptual_soundness | The value of `sign_check.bill_trend_6m.univariate_direction`… | -1 | ratio | sign_check |  | eq | `[[art:a9bff389:sign_check.bill_trend_6m.univariate_direction]]` | verified | -1 |
| 58 | conceptual_soundness | The value of `sign_check.delinq_count_6m.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:a337d16b:sign_check.delinq_count_6m.agrees]]` | verified | 1 |
| 59 | conceptual_soundness | The value of `sign_check.delinq_count_6m.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:17afb6f9:sign_check.delinq_count_6m.coef_sign]]` | verified | 1 |
| 60 | conceptual_soundness | The value of `sign_check.delinq_count_6m.univariate_directio… | 1 | ratio | sign_check |  | eq | `[[art:549e904e:sign_check.delinq_count_6m.univariate_direction]]` | verified | 1 |
| 61 | conceptual_soundness | The value of `sign_check.delinq_last.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:a8ba9372:sign_check.delinq_last.agrees]]` | verified | 1 |
| 62 | conceptual_soundness | The value of `sign_check.delinq_last.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:50d352f8:sign_check.delinq_last.coef_sign]]` | verified | 1 |
| 63 | conceptual_soundness | The value of `sign_check.delinq_last.univariate_direction` i… | 1 | ratio | sign_check |  | eq | `[[art:a78648ba:sign_check.delinq_last.univariate_direction]]` | verified | 1 |
| 64 | conceptual_soundness | The value of `sign_check.delinq_max_6m.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:c946359c:sign_check.delinq_max_6m.agrees]]` | verified | 0 |
| 65 | conceptual_soundness | The value of `sign_check.delinq_max_6m.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]]` | verified | -1 |
| 66 | conceptual_soundness | The value of `sign_check.delinq_max_6m.univariate_direction`… | 1 | ratio | sign_check |  | eq | `[[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]]` | verified | 1 |
| 67 | conceptual_soundness | The value of `sign_check.limit_bal.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:0278aad1:sign_check.limit_bal.agrees]]` | verified | 0 |
| 68 | conceptual_soundness | The value of `sign_check.limit_bal.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:6af6aef2:sign_check.limit_bal.coef_sign]]` | verified | 1 |
| 69 | conceptual_soundness | The value of `sign_check.limit_bal.univariate_direction` is… | -1 | ratio | sign_check |  | eq | `[[art:56d284d6:sign_check.limit_bal.univariate_direction]]` | verified | -1 |
| 70 | conceptual_soundness | The value of `sign_check.n_disagreements` is 6 . | 6 | ratio | sign_check |  | eq | `[[art:75159a84:sign_check.n_disagreements]]` | verified | 6 |
| 71 | conceptual_soundness | The value of `sign_check.pay_amt_next.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:01bd6313:sign_check.pay_amt_next.agrees]]` | verified | 1 |
| 72 | conceptual_soundness | The value of `sign_check.pay_amt_next.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:6fc540c1:sign_check.pay_amt_next.coef_sign]]` | verified | -1 |
| 73 | conceptual_soundness | The value of `sign_check.pay_amt_next.univariate_direction`… | -1 | ratio | sign_check |  | eq | `[[art:1bec400a:sign_check.pay_amt_next.univariate_direction]]` | verified | -1 |
| 74 | conceptual_soundness | The value of `sign_check.pay_ratio_last.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:79abee77:sign_check.pay_ratio_last.agrees]]` | verified | 0 |
| 75 | conceptual_soundness | The value of `sign_check.pay_ratio_last.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:f018263e:sign_check.pay_ratio_last.coef_sign]]` | verified | 1 |
| 76 | conceptual_soundness | The value of `sign_check.pay_ratio_last.univariate_direction… | -1 | ratio | sign_check |  | eq | `[[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]]` | verified | -1 |
| 77 | conceptual_soundness | The value of `sign_check.pay_ratio_mean_6m.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:51914c14:sign_check.pay_ratio_mean_6m.agrees]]` | verified | 0 |
| 78 | conceptual_soundness | The value of `sign_check.pay_ratio_mean_6m.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:8547787e:sign_check.pay_ratio_mean_6m.coef_sign]]` | verified | 1 |
| 79 | conceptual_soundness | The value of `sign_check.pay_ratio_mean_6m.univariate_direct… | -1 | ratio | sign_check |  | eq | `[[art:24dcef24:sign_check.pay_ratio_mean_6m.univariate_direction]]` | verified | -1 |
| 80 | conceptual_soundness | The value of `sign_check.utilisation.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:d0c9a130:sign_check.utilisation.agrees]]` | verified | 1 |
| 81 | conceptual_soundness | The value of `sign_check.utilisation.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:85badc3c:sign_check.utilisation.coef_sign]]` | verified | 1 |
| 82 | conceptual_soundness | The value of `sign_check.utilisation.univariate_direction` i… | 1 | ratio | sign_check |  | eq | `[[art:f0995196:sign_check.utilisation.univariate_direction]]` | verified | 1 |
| 83 | conceptual_soundness | The value of `threshold.E1.delta_auc` is 0.03 . | 0.03 | ratio | threshold |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 84 | data_integrity | The value of `csi.age` is 0.00125 . | 0.00125 | ratio | csi |  | eq | `[[art:584faff4:csi.age]]` | verified | 0.00125000439 |
| 85 | data_integrity | The value of `csi.bill_mean_6m` is 0.0105 . | 0.0105 | ratio | csi |  | eq | `[[art:f374dbd7:csi.bill_mean_6m]]` | verified | 0.01049921023 |
| 86 | data_integrity | The value of `csi.bill_trend_6m` is 0.00567 . | 0.00567 | ratio | csi |  | eq | `[[art:8bb46253:csi.bill_trend_6m]]` | verified | 0.005670244137 |
| 87 | data_integrity | The value of `csi.delinq_count_6m` is 0.002143 . | 0.002143 | ratio | csi |  | eq | `[[art:4564aa47:csi.delinq_count_6m]]` | verified | 0.00214274047 |
| 88 | data_integrity | The value of `csi.delinq_last` is 0.0295 . | 0.0295 | ratio | csi |  | eq | `[[art:cd29d613:csi.delinq_last]]` | verified | 0.02950471301 |
| 89 | data_integrity | The value of `csi.delinq_max_6m` is 0.002782 . | 0.002782 | ratio | csi |  | eq | `[[art:2fe28db6:csi.delinq_max_6m]]` | verified | 0.002782289452 |
| 90 | data_integrity | The value of `csi.limit_bal` is 0.007188 . | 0.007188 | ratio | csi |  | eq | `[[art:cb617a64:csi.limit_bal]]` | verified | 0.007188476411 |
| 91 | data_integrity | The value of `csi.max` is 0.4064 . | 0.4064 | ratio | csi |  | eq | `[[art:3f7f79cf:csi.max]]` | verified | 0.4063916509 |
| 92 | data_integrity | The value of `csi.pay_amt_next` is 0.4064 . | 0.4064 | ratio | csi |  | eq | `[[art:e708fa25:csi.pay_amt_next]]` | verified | 0.4063916509 |
| 93 | data_integrity | The value of `csi.pay_ratio_last` is 0.003912 . | 0.003912 | ratio | csi |  | eq | `[[art:c083b28c:csi.pay_ratio_last]]` | verified | 0.003912462231 |
| 94 | data_integrity | The value of `csi.pay_ratio_mean_6m` is 0.003519 . | 0.003519 | ratio | csi |  | eq | `[[art:8f1dbe89:csi.pay_ratio_mean_6m]]` | verified | 0.003518997237 |
| 95 | data_integrity | The value of `csi.utilisation` is 0.01304 . | 0.01304 | ratio | csi |  | eq | `[[art:b1f362df:csi.utilisation]]` | verified | 0.01304415209 |
| 96 | data_integrity | The value of `leakage.duplicates.train` is 0 . | 0 | ratio | leakage |  | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 97 | data_integrity | The value of `leakage.name_screen.n_matched` is 0 . | 0 | ratio | leakage |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 98 | data_integrity | The value of `leakage.overlap` is 0 . | 0 | ratio | leakage |  | eq | `[[art:4c9fcd09:leakage.overlap]]` | verified | 0 |
| 99 | data_integrity | The value of `leakage.overlap.features` is 0 . | 0 | ratio | leakage |  | eq | `[[art:0fec8048:leakage.overlap.features]]` | verified | 0 |
| 100 | data_integrity | The value of `leakage.overlap.ids` is 0 . | 0 | ratio | leakage |  | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 101 | data_integrity | The value of `leakage.target_corr.max_single_feature_auc` is… | 0.945 | ratio | leakage |  | eq | `[[art:5b5e98c2:leakage.target_corr.max_single_feature_auc]]` | verified | 0.9449621321 |
| 102 | data_integrity | The value of `leakage.timing.n_flagged` is 1 . | 1 | ratio | leakage |  | eq | `[[art:e3a31f6a:leakage.timing.n_flagged]]` | verified | 1 |
| 103 | data_integrity | The value of `profile.test.missing.max` is 0 . | 0 | ratio | profile |  | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 104 | data_integrity | The value of `profile.test.n` is 1500 . | 1500 | ratio | profile |  | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 105 | data_integrity | The value of `profile.train.missing.max` is 0 . | 0 | ratio | profile |  | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 106 | data_integrity | The value of `profile.train.n` is 3500 . | 3500 | ratio | profile |  | eq | `[[art:2510d49d:profile.train.n]]` | verified | 3500 |
| 107 | data_integrity | The value of `psi.age` is 0.008124 . | 0.008124 | ratio | psi |  | eq | `[[art:f9255a0a:psi.age]]` | verified | 0.008124281436 |
| 108 | data_integrity | The value of `psi.bill_mean_6m` is 0.007124 . | 0.007124 | ratio | psi |  | eq | `[[art:028e4281:psi.bill_mean_6m]]` | verified | 0.007124196275 |
| 109 | data_integrity | The value of `psi.bill_trend_6m` is 0.00958 . | 0.00958 | ratio | psi |  | eq | `[[art:c247a6f2:psi.bill_trend_6m]]` | verified | 0.009579614525 |
| 110 | data_integrity | The value of `psi.delinq_count_6m` is 0.002069 . | 0.002069 | ratio | psi |  | eq | `[[art:61491d02:psi.delinq_count_6m]]` | verified | 0.002069275496 |
| 111 | data_integrity | The value of `psi.delinq_last` is 0.00285 . | 0.00285 | ratio | psi |  | eq | `[[art:03bd52e7:psi.delinq_last]]` | verified | 0.002849633848 |
| 112 | data_integrity | The value of `psi.delinq_max_6m` is 0.005498 . | 0.005498 | ratio | psi |  | eq | `[[art:7a82e7f3:psi.delinq_max_6m]]` | verified | 0.005498249408 |
| 113 | data_integrity | The value of `psi.limit_bal` is 0.01095 . | 0.01095 | ratio | psi |  | eq | `[[art:601cdba2:psi.limit_bal]]` | verified | 0.01095273358 |
| 114 | data_integrity | The value of `psi.max` is 0.01789 . | 0.01789 | ratio | psi |  | eq | `[[art:1b87de3e:psi.max]]` | verified | 0.01789488592 |
| 115 | data_integrity | The value of `psi.pay_amt_next` is 0.01789 . | 0.01789 | ratio | psi |  | eq | `[[art:996bb509:psi.pay_amt_next]]` | verified | 0.01789488592 |
| 116 | data_integrity | The value of `psi.pay_ratio_last` is 0.004966 . | 0.004966 | ratio | psi |  | eq | `[[art:3af2ca29:psi.pay_ratio_last]]` | verified | 0.00496591109 |
| 117 | data_integrity | The value of `psi.pay_ratio_mean_6m` is 0.0055 . | 0.0055 | ratio | psi |  | eq | `[[art:2c5baeb2:psi.pay_ratio_mean_6m]]` | verified | 0.005500252946 |
| 118 | data_integrity | The value of `psi.utilisation` is 0.004244 . | 0.004244 | ratio | psi |  | eq | `[[art:451e0780:psi.utilisation]]` | verified | 0.0042440485 |
| 119 | data_integrity | The value of `psi.y_score` is 0.01199 . | 0.01199 | ratio | psi |  | eq | `[[art:05f120d2:psi.y_score]]` | verified | 0.01198828928 |
| 120 | data_integrity | The value of `threshold.D1.missing_gap` is 0.1 . | 0.1 | ratio | threshold |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 121 | data_integrity | The value of `threshold.L1.single_feature_auc` is 0.9 . | 0.9 | ratio | threshold |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 122 | data_integrity | The value of `threshold.L2.overlap` is 0.005 . | 0.005 | ratio | threshold |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 123 | data_integrity | The value of `threshold.L2.overlap.features_effective` is 0.… | 0.005 | ratio | threshold |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 124 | data_integrity | The value of `threshold.S1.psi` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 125 | data_integrity | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 126 | outcomes | The value of `calibration.mean_rel_gap.test` is 0.03717 . | 0.03717 | ratio | calibration |  | eq | `[[art:6a845d81:calibration.mean_rel_gap.test]]` | verified | 0.0371730842 |
| 127 | outcomes | The value of `calibration.mean_rel_gap.train` is 0.00008632… | 8.632e-05 | ratio | calibration |  | eq | `[[art:f7447f34:calibration.mean_rel_gap.train]]` | verified | 8.631936949e-05 |
| 128 | outcomes | The value of `calibration_intercept.test` is -0.0558 . | -0.0558 | ratio | calibration_intercept |  | eq | `[[art:56745cf2:calibration_intercept.test]]` | verified | -0.05579737693 |
| 129 | outcomes | The value of `calibration_intercept.train` is 0.2246 . | 0.2246 | ratio | calibration_intercept |  | eq | `[[art:d556f341:calibration_intercept.train]]` | verified | 0.2245889138 |
| 130 | outcomes | The value of `calibration_slope.test` is 1.197 . | 1.197 | ratio | calibration_slope |  | eq | `[[art:c9a03fe6:calibration_slope.test]]` | verified | 1.19744242 |
| 131 | outcomes | The value of `calibration_slope.train` is 1.383 . | 1.383 | ratio | calibration_slope |  | eq | `[[art:45dafd11:calibration_slope.train]]` | verified | 1.383137681 |
| 132 | outcomes | The value of `deciles.test.top2_capture` is 0.822 . | 0.822 | ratio | deciles |  | eq | `[[art:5690757b:deciles.test.top2_capture]]` | verified | 0.821958457 |
| 133 | outcomes | The value of `deciles.train.top2_capture` is 0.8422 . | 0.8422 | ratio | deciles |  | eq | `[[art:55242963:deciles.train.top2_capture]]` | verified | 0.8422391858 |
| 134 | outcomes | The value of `metrics.test.auc` is 0.9755 . | 0.9755 | ratio | metrics |  | eq | `[[art:8f522f3b:metrics.test.auc]]` | verified | 0.9755058926 |
| 135 | outcomes | The value of `metrics.test.brier` is 0.04247 . | 0.04247 | ratio | metrics |  | eq | `[[art:d4f27e13:metrics.test.brier]]` | verified | 0.04247487168 |
| 136 | outcomes | The value of `metrics.test.event_rate` is 0.2247 . | 0.2247 | ratio | metrics |  | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 137 | outcomes | The value of `metrics.test.gini` is 0.951 . | 0.951 | ratio | metrics |  | eq | `[[art:f927e3cd:metrics.test.gini]]` | verified | 0.9510117852 |
| 138 | outcomes | The value of `metrics.test.ks` is 0.8784 . | 0.8784 | ratio | metrics |  | eq | `[[art:81bee194:metrics.test.ks]]` | verified | 0.8784403377 |
| 139 | outcomes | The value of `metrics.test.logloss` is 0.167 . | 0.167 | ratio | metrics |  | eq | `[[art:aa620b5e:metrics.test.logloss]]` | verified | 0.1670045909 |
| 140 | outcomes | The value of `metrics.test.mean_predicted` is 0.233 . | 0.233 | ratio | metrics |  | eq | `[[art:0b9b6a1e:metrics.test.mean_predicted]]` | verified | 0.2330182196 |
| 141 | outcomes | The value of `metrics.test.n` is 1500 . | 1500 | ratio | metrics |  | eq | `[[art:64fcf14d:metrics.test.n]]` | verified | 1500 |
| 142 | outcomes | The value of `metrics.train.auc` is 0.9812 . | 0.9812 | ratio | metrics |  | eq | `[[art:da2cd01d:metrics.train.auc]]` | verified | 0.9811790152 |
| 143 | outcomes | The value of `metrics.train.brier` is 0.03817 . | 0.03817 | ratio | metrics |  | eq | `[[art:959b3159:metrics.train.brier]]` | verified | 0.03816687592 |
| 144 | outcomes | The value of `metrics.train.event_rate` is 0.2246 . | 0.2246 | ratio | metrics |  | eq | `[[art:133a5ff8:metrics.train.event_rate]]` | verified | 0.2245714286 |
| 145 | outcomes | The value of `metrics.train.gini` is 0.9624 . | 0.9624 | ratio | metrics |  | eq | `[[art:23cb4057:metrics.train.gini]]` | verified | 0.9623580305 |
| 146 | outcomes | The value of `metrics.train.ks` is 0.8895 . | 0.8895 | ratio | metrics |  | eq | `[[art:7a126f15:metrics.train.ks]]` | verified | 0.8894536106 |
| 147 | outcomes | The value of `metrics.train.logloss` is 0.1505 . | 0.1505 | ratio | metrics |  | eq | `[[art:417d98d9:metrics.train.logloss]]` | verified | 0.1504741108 |
| 148 | outcomes | The value of `metrics.train.mean_predicted` is 0.2246 . | 0.2246 | ratio | metrics |  | eq | `[[art:1fa024a6:metrics.train.mean_predicted]]` | verified | 0.2245520437 |
| 149 | outcomes | The value of `metrics.train.n` is 3500 . | 3500 | ratio | metrics |  | eq | `[[art:564683ee:metrics.train.n]]` | verified | 3500 |
| 150 | outcomes | The value of `psi.age` is 0.008124 . | 0.008124 | ratio | psi |  | eq | `[[art:f9255a0a:psi.age]]` | verified | 0.008124281436 |
| 151 | outcomes | The value of `psi.bill_mean_6m` is 0.007124 . | 0.007124 | ratio | psi |  | eq | `[[art:028e4281:psi.bill_mean_6m]]` | verified | 0.007124196275 |
| 152 | outcomes | The value of `psi.bill_trend_6m` is 0.00958 . | 0.00958 | ratio | psi |  | eq | `[[art:c247a6f2:psi.bill_trend_6m]]` | verified | 0.009579614525 |
| 153 | outcomes | The value of `psi.delinq_count_6m` is 0.002069 . | 0.002069 | ratio | psi |  | eq | `[[art:61491d02:psi.delinq_count_6m]]` | verified | 0.002069275496 |
| 154 | outcomes | The value of `psi.delinq_last` is 0.00285 . | 0.00285 | ratio | psi |  | eq | `[[art:03bd52e7:psi.delinq_last]]` | verified | 0.002849633848 |
| 155 | outcomes | The value of `psi.delinq_max_6m` is 0.005498 . | 0.005498 | ratio | psi |  | eq | `[[art:7a82e7f3:psi.delinq_max_6m]]` | verified | 0.005498249408 |
| 156 | outcomes | The value of `psi.limit_bal` is 0.01095 . | 0.01095 | ratio | psi |  | eq | `[[art:601cdba2:psi.limit_bal]]` | verified | 0.01095273358 |
| 157 | outcomes | The value of `psi.max` is 0.01789 . | 0.01789 | ratio | psi |  | eq | `[[art:1b87de3e:psi.max]]` | verified | 0.01789488592 |
| 158 | outcomes | The value of `psi.pay_amt_next` is 0.01789 . | 0.01789 | ratio | psi |  | eq | `[[art:996bb509:psi.pay_amt_next]]` | verified | 0.01789488592 |
| 159 | outcomes | The value of `psi.pay_ratio_last` is 0.004966 . | 0.004966 | ratio | psi |  | eq | `[[art:3af2ca29:psi.pay_ratio_last]]` | verified | 0.00496591109 |
| 160 | outcomes | The value of `psi.pay_ratio_mean_6m` is 0.0055 . | 0.0055 | ratio | psi |  | eq | `[[art:2c5baeb2:psi.pay_ratio_mean_6m]]` | verified | 0.005500252946 |
| 161 | outcomes | The value of `psi.utilisation` is 0.004244 . | 0.004244 | ratio | psi |  | eq | `[[art:451e0780:psi.utilisation]]` | verified | 0.0042440485 |
| 162 | outcomes | The value of `psi.y_score` is 0.01199 . | 0.01199 | ratio | psi |  | eq | `[[art:05f120d2:psi.y_score]]` | verified | 0.01198828928 |
| 163 | outcomes | The value of `rule.calibration_first_event_rate` is 0.05 . | 0.05 | ratio | rule |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 164 | outcomes | The value of `threshold.C1.calibration_slope.max` is 1.2 . | 1.2 | ratio | threshold |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 165 | outcomes | The value of `threshold.C1.calibration_slope.min` is 0.8 . | 0.8 | ratio | threshold |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 166 | outcomes | The value of `threshold.C1.mean_ratio_rel` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 167 | outcomes | The value of `threshold.D1.missing_gap` is 0.1 . | 0.1 | ratio | threshold |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 168 | outcomes | The value of `threshold.E1.delta_auc` is 0.03 . | 0.03 | ratio | threshold |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 169 | outcomes | The value of `threshold.L1.single_feature_auc` is 0.9 . | 0.9 | ratio | threshold |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 170 | outcomes | The value of `threshold.L2.overlap` is 0.005 . | 0.005 | ratio | threshold |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 171 | outcomes | The value of `threshold.L2.overlap.features_effective` is 0.… | 0.005 | ratio | threshold |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 172 | outcomes | The value of `threshold.M1.condition_number` is 30 . | 30 | ratio | threshold |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 173 | outcomes | The value of `threshold.M1.vif` is 10 . | 10 | ratio | threshold |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 174 | outcomes | The value of `threshold.O1.auc_gap` is 0.08 . | 0.08 | ratio | threshold |  | eq | `[[art:630f28f4:threshold.O1.auc_gap]]` | verified | 0.08 |
| 175 | outcomes | The value of `threshold.S1.psi` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 176 | outcomes | The value of `threshold.package.auc.test.min` is 0.7 . | 0.7 | ratio | threshold |  | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 177 | outcomes | The value of `threshold.package.brier.test.max` is 0.2 . | 0.2 | ratio | threshold |  | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 178 | outcomes | The value of `threshold.package.calibration_slope.test.max`… | 1.2 | ratio | threshold |  | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 179 | outcomes | The value of `threshold.package.calibration_slope.test.min`… | 0.8 | ratio | threshold |  | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 180 | outcomes | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 181 | sensitivity | The value of `condition_number` is 6.185 . | 6.185 | ratio | condition_number |  | eq | `[[art:36392379:condition_number]]` | verified | 6.185189657 |
| 182 | sensitivity | The value of `threshold.M1.condition_number` is 30 . | 30 | ratio | threshold |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 183 | sensitivity | The value of `threshold.M1.vif` is 10 . | 10 | ratio | threshold |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 184 | sensitivity | The value of `vif.age` is 1.002 . | 1.002 | ratio | vif |  | eq | `[[art:8021b06e:vif.age]]` | verified | 1.002328679 |
| 185 | sensitivity | The value of `vif.bill_mean_6m` is 8.181 . | 8.181 | ratio | vif |  | eq | `[[art:d5ab7306:vif.bill_mean_6m]]` | verified | 8.181114607 |
| 186 | sensitivity | The value of `vif.bill_trend_6m` is 1.225 . | 1.225 | ratio | vif |  | eq | `[[art:0cb3df89:vif.bill_trend_6m]]` | verified | 1.225337779 |
| 187 | sensitivity | The value of `vif.delinq_count_6m` is 2.561 . | 2.561 | ratio | vif |  | eq | `[[art:87890613:vif.delinq_count_6m]]` | verified | 2.56148636 |
| 188 | sensitivity | The value of `vif.delinq_last` is 1.422 . | 1.422 | ratio | vif |  | eq | `[[art:c18221d4:vif.delinq_last]]` | verified | 1.422439811 |
| 189 | sensitivity | The value of `vif.delinq_max_6m` is 2.408 . | 2.408 | ratio | vif |  | eq | `[[art:4b239ec5:vif.delinq_max_6m]]` | verified | 2.408148028 |
| 190 | sensitivity | The value of `vif.limit_bal` is 4.81 . | 4.81 | ratio | vif |  | eq | `[[art:8209ea46:vif.limit_bal]]` | verified | 4.809808481 |
| 191 | sensitivity | The value of `vif.max` is 8.181 . | 8.181 | ratio | vif |  | eq | `[[art:4afdc4f1:vif.max]]` | verified | 8.181114607 |
| 192 | sensitivity | The value of `vif.pay_amt_next` is 2.206 . | 2.206 | ratio | vif |  | eq | `[[art:68806d80:vif.pay_amt_next]]` | verified | 2.206074628 |
| 193 | sensitivity | The value of `vif.pay_ratio_last` is 7.268 . | 7.268 | ratio | vif |  | eq | `[[art:bec24796:vif.pay_ratio_last]]` | verified | 7.267755553 |
| 194 | sensitivity | The value of `vif.pay_ratio_mean_6m` is 7.526 . | 7.526 | ratio | vif |  | eq | `[[art:000b6208:vif.pay_ratio_mean_6m]]` | verified | 7.525569541 |
| 195 | sensitivity | The value of `vif.utilisation` is 3.215 . | 3.215 | ratio | vif |  | eq | `[[art:ec978947:vif.utilisation]]` | verified | 3.215174221 |
| 196 | findings | The value of `calibration_slope.train` is 1.383 . | 1.383 | ratio | calibration_slope |  | eq | `[[art:45dafd11:calibration_slope.train]]` | verified | 1.383137681 |
| 197 | findings | The value of `leakage.target_corr.max_single_feature_auc` is… | 0.945 | ratio | leakage |  | eq | `[[art:5b5e98c2:leakage.target_corr.max_single_feature_auc]]` | verified | 0.9449621321 |
| 198 | findings | The value of `leakage.timing.n_flagged` is 1 . | 1 | ratio | leakage |  | eq | `[[art:e3a31f6a:leakage.timing.n_flagged]]` | verified | 1 |
| 199 | findings | The value of `sign_check.bill_mean_6m.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:4df8b747:sign_check.bill_mean_6m.agrees]]` | verified | 0 |
| 200 | findings | The value of `sign_check.bill_mean_6m.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:a457c04a:sign_check.bill_mean_6m.coef_sign]]` | verified | 1 |
| 201 | findings | The value of `sign_check.bill_mean_6m.univariate_direction`… | -1 | ratio | sign_check |  | eq | `[[art:23b89c5d:sign_check.bill_mean_6m.univariate_direction]]` | verified | -1 |
| 202 | findings | The value of `sign_check.bill_trend_6m.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:c0f6d07d:sign_check.bill_trend_6m.agrees]]` | verified | 0 |
| 203 | findings | The value of `sign_check.bill_trend_6m.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:abd4aaba:sign_check.bill_trend_6m.coef_sign]]` | verified | 1 |
| 204 | findings | The value of `sign_check.bill_trend_6m.univariate_direction`… | -1 | ratio | sign_check |  | eq | `[[art:a9bff389:sign_check.bill_trend_6m.univariate_direction]]` | verified | -1 |
| 205 | findings | The value of `sign_check.delinq_max_6m.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:c946359c:sign_check.delinq_max_6m.agrees]]` | verified | 0 |
| 206 | findings | The value of `sign_check.delinq_max_6m.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]]` | verified | -1 |
| 207 | findings | The value of `sign_check.delinq_max_6m.univariate_direction`… | 1 | ratio | sign_check |  | eq | `[[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]]` | verified | 1 |
| 208 | findings | The value of `sign_check.limit_bal.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:0278aad1:sign_check.limit_bal.agrees]]` | verified | 0 |
| 209 | findings | The value of `sign_check.limit_bal.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:6af6aef2:sign_check.limit_bal.coef_sign]]` | verified | 1 |
| 210 | findings | The value of `sign_check.limit_bal.univariate_direction` is… | -1 | ratio | sign_check |  | eq | `[[art:56d284d6:sign_check.limit_bal.univariate_direction]]` | verified | -1 |
| 211 | findings | The value of `sign_check.pay_ratio_last.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:79abee77:sign_check.pay_ratio_last.agrees]]` | verified | 0 |
| 212 | findings | The value of `sign_check.pay_ratio_last.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:f018263e:sign_check.pay_ratio_last.coef_sign]]` | verified | 1 |
| 213 | findings | The value of `sign_check.pay_ratio_last.univariate_direction… | -1 | ratio | sign_check |  | eq | `[[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]]` | verified | -1 |
| 214 | findings | The value of `sign_check.pay_ratio_mean_6m.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:51914c14:sign_check.pay_ratio_mean_6m.agrees]]` | verified | 0 |
| 215 | findings | The value of `sign_check.pay_ratio_mean_6m.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:8547787e:sign_check.pay_ratio_mean_6m.coef_sign]]` | verified | 1 |
| 216 | findings | The value of `sign_check.pay_ratio_mean_6m.univariate_direct… | -1 | ratio | sign_check |  | eq | `[[art:24dcef24:sign_check.pay_ratio_mean_6m.univariate_direction]]` | verified | -1 |
| 217 | findings | The value of `threshold.C1.calibration_slope.max` is 1.2 . | 1.2 | ratio | threshold |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 218 | findings | The value of `threshold.L1.single_feature_auc` is 0.9 . | 0.9 | ratio | threshold |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 219 | monitoring | The value of `calibration_slope.test` is 1.197 . | 1.197 | ratio | calibration_slope |  | eq | `[[art:c9a03fe6:calibration_slope.test]]` | verified | 1.19744242 |
| 220 | monitoring | The value of `metrics.test.auc` is 0.9755 . | 0.9755 | ratio | metrics |  | eq | `[[art:8f522f3b:metrics.test.auc]]` | verified | 0.9755058926 |
| 221 | monitoring | The value of `metrics.test.brier` is 0.04247 . | 0.04247 | ratio | metrics |  | eq | `[[art:d4f27e13:metrics.test.brier]]` | verified | 0.04247487168 |
| 222 | monitoring | The value of `psi.max` is 0.01789 . | 0.01789 | ratio | psi |  | eq | `[[art:1b87de3e:psi.max]]` | verified | 0.01789488592 |
| 223 | monitoring | The value of `rule.calibration_first_event_rate` is 0.05 . | 0.05 | ratio | rule |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 224 | monitoring | The value of `threshold.package.auc.test.min` is 0.7 . | 0.7 | ratio | threshold |  | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 225 | monitoring | The value of `threshold.package.brier.test.max` is 0.2 . | 0.2 | ratio | threshold |  | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 226 | monitoring | The value of `threshold.package.calibration_slope.test.max`… | 1.2 | ratio | threshold |  | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 227 | monitoring | The value of `threshold.package.calibration_slope.test.min`… | 0.8 | ratio | threshold |  | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 228 | monitoring | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |

## Appendix B — Artifact index

The store holds 175 artifacts; the 147 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `ablation.age.delta_auc` | `786b509d` | scalar | 5.613232942e-05 | change in test AUC when the champion's form is refitted without age |
| `ablation.baseline_auc` | `8e58476a` | scalar | 0.9755058926 | AUC on test of a refit of the champion's functional form on every retained feature, the level each ablation delta is measured from |
| `ablation.bill_mean_6m.delta_auc` | `a4586b58` | scalar | -0.005227961044 | change in test AUC when the champion's form is refitted without bill_mean_6m |
| `ablation.bill_trend_6m.delta_auc` | `54e6a418` | scalar | -0.0005536688856 | change in test AUC when the champion's form is refitted without bill_trend_6m |
| `ablation.delinq_count_6m.delta_auc` | `3730f6e2` | scalar | 5.102939038e-06 | change in test AUC when the champion's form is refitted without delinq_count_6m |
| `ablation.delinq_last.delta_auc` | `43d4225a` | scalar | -0.0009210804963 | change in test AUC when the champion's form is refitted without delinq_last |
| `ablation.delinq_max_6m.delta_auc` | `b1793491` | scalar | 0.0001607425797 | change in test AUC when the champion's form is refitted without delinq_max_6m |
| `ablation.limit_bal.delta_auc` | `4b976d60` | scalar | 0.0006174556236 | change in test AUC when the champion's form is refitted without limit_bal |
| `ablation.pay_amt_next.delta_auc` | `cf6c0563` | scalar | -0.2275170885 | change in test AUC when the champion's form is refitted without pay_amt_next |
| `ablation.pay_ratio_last.delta_auc` | `c577925a` | scalar | 0.0001862572749 | change in test AUC when the champion's form is refitted without pay_ratio_last |
| `ablation.pay_ratio_mean_6m.delta_auc` | `54c168fb` | scalar | -0.0009593525391 | change in test AUC when the champion's form is refitted without pay_ratio_mean_6m |
| `ablation.utilisation.delta_auc` | `009bc4f1` | scalar | -0.0004235439401 | change in test AUC when the champion's form is refitted without utilisation |
| `calibration.mean_rel_gap.test` | `6a845d81` | scalar | 0.0371730842 | mean predicted against observed on test, relative |
| `calibration.mean_rel_gap.train` | `f7447f34` | scalar | 8.631936949e-05 | mean predicted against observed on train, relative |
| `calibration.test` | `1744d380` | table | table, 10 rows | calibration by decile of predicted probability on test |
| `calibration.train` | `309e30bb` | table | table, 10 rows | calibration by decile of predicted probability on train |
| `calibration_intercept.test` | `56745cf2` | scalar | -0.05579737693 | logistic regression of the outcome on logit(p) on test: the intercept |
| `calibration_intercept.train` | `d556f341` | scalar | 0.2245889138 | logistic regression of the outcome on logit(p) on train: the intercept |
| `calibration_slope.test` | `c9a03fe6` | scalar | 1.19744242 | logistic regression of the outcome on logit(p) on test: the slope |
| `calibration_slope.train` | `45dafd11` | scalar | 1.383137681 | logistic regression of the outcome on logit(p) on train: the slope |
| `challenger.auc` | `d2646bc7` | scalar | 0.9877299831 | the challenger's AUC on test |
| `challenger.brier` | `0a224a0a` | scalar | 0.02542316584 | the challenger's Brier score on test |
| `challenger.delta_auc` | `2ab4af27` | scalar | 0.01222409046 | the challenger's AUC on test minus the champion's |
| `condition_number` | `36392379` | scalar | 6.185189657 | Belsley's condition number of the column-standardised design |
| `csi.age` | `584faff4` | scalar | 0.00125000439 | CSI of age: its contribution to the shift in the linear predictor |
| `csi.bill_mean_6m` | `f374dbd7` | scalar | 0.01049921023 | CSI of bill_mean_6m: its contribution to the shift in the linear predictor |
| `csi.bill_trend_6m` | `8bb46253` | scalar | 0.005670244137 | CSI of bill_trend_6m: its contribution to the shift in the linear predictor |
| `csi.delinq_count_6m` | `4564aa47` | scalar | 0.00214274047 | CSI of delinq_count_6m: its contribution to the shift in the linear predictor |
| `csi.delinq_last` | `cd29d613` | scalar | 0.02950471301 | CSI of delinq_last: its contribution to the shift in the linear predictor |
| `csi.delinq_max_6m` | `2fe28db6` | scalar | 0.002782289452 | CSI of delinq_max_6m: its contribution to the shift in the linear predictor |
| `csi.limit_bal` | `cb617a64` | scalar | 0.007188476411 | CSI of limit_bal: its contribution to the shift in the linear predictor |
| `csi.max` | `3f7f79cf` | scalar | 0.4063916509 | the largest characteristic stability index |
| `csi.pay_amt_next` | `e708fa25` | scalar | 0.4063916509 | CSI of pay_amt_next: its contribution to the shift in the linear predictor |
| `csi.pay_ratio_last` | `c083b28c` | scalar | 0.003912462231 | CSI of pay_ratio_last: its contribution to the shift in the linear predictor |
| `csi.pay_ratio_mean_6m` | `8f1dbe89` | scalar | 0.003518997237 | CSI of pay_ratio_mean_6m: its contribution to the shift in the linear predictor |
| `csi.utilisation` | `b1f362df` | scalar | 0.01304415209 | CSI of utilisation: its contribution to the shift in the linear predictor |
| `deciles.test` | `ffdb3017` | table | table, 10 rows | decile separation on test; decile 1 holds the highest probabilities |
| `deciles.test.top2_capture` | `5690757b` | scalar | 0.821958457 | share of test events in the top two deciles |
| `deciles.train.top2_capture` | `55242963` | scalar | 0.8422391858 | share of train events in the top two deciles |
| `leakage.duplicates.train` | `4474c227` | scalar | 0 | share of train rows whose feature values are not unique within train |
| `leakage.name_screen.n_matched` | `407e62be` | scalar | 0 | feature names matching the target-adjacent lexicon |
| `leakage.overlap` | `4c9fcd09` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.features` | `0fec8048` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.ids` | `63d37fc5` | scalar | 0 | share of test rows whose ['client_id'] also identify a row of train |
| `leakage.target_corr` | `12cb4333` | table | table, 11 rows | each feature against the outcome on train, on its own |
| `leakage.target_corr.max_single_feature_auc` | `5b5e98c2` | scalar | 0.9449621321 | the AUC of the strongest single feature |
| `leakage.timing` | `0dad290e` | table | table, 13 rows | each feature's declared timing; flagged means during or after the outcome |
| `leakage.timing.n_flagged` | `e3a31f6a` | scalar | 1 | features declared during_period or after_outcome |
| `metrics.test.auc` | `8f522f3b` | scalar | 0.9755058926 | auc on test, recomputed by quaestor |
| `metrics.test.brier` | `d4f27e13` | scalar | 0.04247487168 | brier on test, recomputed by quaestor |
| `metrics.test.event_rate` | `9209d200` | scalar | 0.2246666667 | event_rate on test, recomputed by quaestor |
| `metrics.test.gini` | `f927e3cd` | scalar | 0.9510117852 | gini on test, recomputed by quaestor |
| `metrics.test.ks` | `81bee194` | scalar | 0.8784403377 | ks on test, recomputed by quaestor |
| `metrics.test.logloss` | `aa620b5e` | scalar | 0.1670045909 | logloss on test, recomputed by quaestor |
| `metrics.test.mean_predicted` | `0b9b6a1e` | scalar | 0.2330182196 | mean_predicted on test, recomputed by quaestor |
| `metrics.test.n` | `64fcf14d` | scalar | 1500 | n on test, recomputed by quaestor |
| `metrics.train.auc` | `da2cd01d` | scalar | 0.9811790152 | auc on train, recomputed by quaestor |
| `metrics.train.brier` | `959b3159` | scalar | 0.03816687592 | brier on train, recomputed by quaestor |
| `metrics.train.event_rate` | `133a5ff8` | scalar | 0.2245714286 | event_rate on train, recomputed by quaestor |
| `metrics.train.gini` | `23cb4057` | scalar | 0.9623580305 | gini on train, recomputed by quaestor |
| `metrics.train.ks` | `7a126f15` | scalar | 0.8894536106 | ks on train, recomputed by quaestor |
| `metrics.train.logloss` | `417d98d9` | scalar | 0.1504741108 | logloss on train, recomputed by quaestor |
| `metrics.train.mean_predicted` | `1fa024a6` | scalar | 0.2245520437 | mean_predicted on train, recomputed by quaestor |
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
| `psi.max` | `1b87de3e` | scalar | 0.01789488592 | the largest train-to-test PSI, score included |
| `psi.pay_amt_next` | `996bb509` | scalar | 0.01789488592 | PSI of pay_amt_next between train and test |
| `psi.pay_ratio_last` | `3af2ca29` | scalar | 0.00496591109 | PSI of pay_ratio_last between train and test |
| `psi.pay_ratio_mean_6m` | `2c5baeb2` | scalar | 0.005500252946 | PSI of pay_ratio_mean_6m between train and test |
| `psi.utilisation` | `451e0780` | scalar | 0.0042440485 | PSI of utilisation between train and test |
| `psi.y_score` | `05f120d2` | scalar | 0.01198828928 | PSI of the score between train and test |
| `rule.calibration_first_event_rate` | `42f1351e` | scalar | 0.05 | the event rate below which the report puts calibration before discrimination |
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |
| `sign_check.age.agrees` | `4116add1` | scalar | 1 | 1 when the fitted sign on age agrees with its univariate direction, 0 when it does not |
| `sign_check.age.coef_sign` | `6172eb93` | scalar | -1 | the sign of the fitted coefficient on age |
| `sign_check.age.univariate_direction` | `66364583` | scalar | -1 | the sign of age's own single-feature AUC on train minus 0.5 |
| `sign_check.bill_mean_6m.agrees` | `4df8b747` | scalar | 0 | 1 when the fitted sign on bill_mean_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.bill_mean_6m.coef_sign` | `a457c04a` | scalar | 1 | the sign of the fitted coefficient on bill_mean_6m |
| `sign_check.bill_mean_6m.univariate_direction` | `23b89c5d` | scalar | -1 | the sign of bill_mean_6m's own single-feature AUC on train minus 0.5 |
| `sign_check.bill_trend_6m.agrees` | `c0f6d07d` | scalar | 0 | 1 when the fitted sign on bill_trend_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.bill_trend_6m.coef_sign` | `abd4aaba` | scalar | 1 | the sign of the fitted coefficient on bill_trend_6m |
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
| `sign_check.n_disagreements` | `75159a84` | scalar | 6 | retained features whose fitted sign contradicts their univariate direction, of 11 checked |
| `sign_check.pay_amt_next.agrees` | `01bd6313` | scalar | 1 | 1 when the fitted sign on pay_amt_next agrees with its univariate direction, 0 when it does not |
| `sign_check.pay_amt_next.coef_sign` | `6fc540c1` | scalar | -1 | the sign of the fitted coefficient on pay_amt_next |
| `sign_check.pay_amt_next.univariate_direction` | `1bec400a` | scalar | -1 | the sign of pay_amt_next's own single-feature AUC on train minus 0.5 |
| `sign_check.pay_ratio_last.agrees` | `79abee77` | scalar | 0 | 1 when the fitted sign on pay_ratio_last agrees with its univariate direction, 0 when it does not |
| `sign_check.pay_ratio_last.coef_sign` | `f018263e` | scalar | 1 | the sign of the fitted coefficient on pay_ratio_last |
| `sign_check.pay_ratio_last.univariate_direction` | `f8e46d75` | scalar | -1 | the sign of pay_ratio_last's own single-feature AUC on train minus 0.5 |
| `sign_check.pay_ratio_mean_6m.agrees` | `51914c14` | scalar | 0 | 1 when the fitted sign on pay_ratio_mean_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.pay_ratio_mean_6m.coef_sign` | `8547787e` | scalar | 1 | the sign of the fitted coefficient on pay_ratio_mean_6m |
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
| `thresholds.evaluation` | `f41614b5` | table | table, 5 rows | every threshold package.yaml declares, with its bound, the recomputed value and the outcome |
| `vif.age` | `8021b06e` | scalar | 1.002328679 | variance inflation factor of age on train |
| `vif.bill_mean_6m` | `d5ab7306` | scalar | 8.181114607 | variance inflation factor of bill_mean_6m on train |
| `vif.bill_trend_6m` | `0cb3df89` | scalar | 1.225337779 | variance inflation factor of bill_trend_6m on train |
| `vif.delinq_count_6m` | `87890613` | scalar | 2.56148636 | variance inflation factor of delinq_count_6m on train |
| `vif.delinq_last` | `c18221d4` | scalar | 1.422439811 | variance inflation factor of delinq_last on train |
| `vif.delinq_max_6m` | `4b239ec5` | scalar | 2.408148028 | variance inflation factor of delinq_max_6m on train |
| `vif.limit_bal` | `8209ea46` | scalar | 4.809808481 | variance inflation factor of limit_bal on train |
| `vif.max` | `4afdc4f1` | scalar | 8.181114607 | the largest variance inflation factor |
| `vif.pay_amt_next` | `68806d80` | scalar | 2.206074628 | variance inflation factor of pay_amt_next on train |
| `vif.pay_ratio_last` | `bec24796` | scalar | 7.267755553 | variance inflation factor of pay_ratio_last on train |
| `vif.pay_ratio_mean_6m` | `000b6208` | scalar | 7.525569541 | variance inflation factor of pay_ratio_mean_6m on train |
| `vif.utilisation` | `ec978947` | scalar | 3.215174221 | variance inflation factor of utilisation on train |

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
| subject run (s) | 1.20 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | fake |
| model | none: no model answered |
| run id | credit_default-rules_only-20260918T065319Z-bd5861e9 |

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
