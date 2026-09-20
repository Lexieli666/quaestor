---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: msr_prepayment
version: "1.0"
model_type: discrete_time_hazard
configuration: rules_only
model: fake
run_id: msr_prepayment-rules_only-20260918T065337Z-568d25f5
data_mode: synthetic
synthetic_n: 2000
grounding_precision_pre: 1.0000
grounding_precision_post: 1.0000
n_claims: 330
n_findings_by_severity: {high: 0, medium: 1, low: 0, info: 0}
generated: "2026-09-18T06:53:37Z"
illustrative: false
---

# Validation report — `msr_prepayment` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `msr_prepayment` v1.0 | `rules_only` | fake | synthetic, n = 2000 | 1.0000 → 1.0000 | 0 / 1 / 0 / 0 |
<!-- quaestor:renderer:end -->

This section follows the model risk management guidance at [[reg:SR26-2:V.1.b]].
The value of `calibration_slope.out_of_time` is 1.066 [[art:ea7d5696:calibration_slope.out_of_time]].
The value of `calibration_slope.test` is 0.9537 [[art:f8ef2beb:calibration_slope.test]].
The value of `calibration_slope.train` is 1.015 [[art:ffabb935:calibration_slope.train]].
The value of `calibration_slope.vintage_holdout` is 0.8562 [[art:010c0ec4:calibration_slope.vintage_holdout]].
The value of `challenger.delta_auc` is -0.04213 [[art:1e990f53:challenger.delta_auc]].
The value of `condition_number` is 4.943 [[art:4f06a3c5:condition_number]].
The value of `csi.max` is 0.03331 [[art:a8ca288d:csi.max]].
The value of `metrics.out_of_time.auc` is 0.7898 [[art:aa836722:metrics.out_of_time.auc]].
The value of `metrics.out_of_time.brier` is 0.02402 [[art:a8a8d3a5:metrics.out_of_time.brier]].
The value of `metrics.out_of_time.event_rate` is 0.01795 [[art:83ccf5c0:metrics.out_of_time.event_rate]].
The value of `metrics.out_of_time.gini` is 0.5796 [[art:3dc07327:metrics.out_of_time.gini]].
The value of `metrics.out_of_time.ks` is 0.4368 [[art:00bf02ed:metrics.out_of_time.ks]].
The value of `metrics.out_of_time.logloss` is 0.1174 [[art:5198f968:metrics.out_of_time.logloss]].
The value of `metrics.out_of_time.mean_predicted` is 0.07793 [[art:921d185b:metrics.out_of_time.mean_predicted]].
The value of `metrics.out_of_time.n` is 12257 [[art:7898809e:metrics.out_of_time.n]].
The value of `metrics.test.auc` is 0.7758 [[art:2f4cab3e:metrics.test.auc]].
The value of `metrics.test.brier` is 0.009864 [[art:1e4aab51:metrics.test.brier]].
The value of `metrics.test.event_rate` is 0.008061 [[art:570cc08a:metrics.test.event_rate]].
The value of `metrics.test.gini` is 0.5517 [[art:8593585c:metrics.test.gini]].
The value of `metrics.test.ks` is 0.428 [[art:554f1e19:metrics.test.ks]].
The value of `metrics.test.logloss` is 0.06118 [[art:b9424e16:metrics.test.logloss]].
The value of `metrics.test.mean_predicted` is 0.03802 [[art:122af437:metrics.test.mean_predicted]].
The value of `metrics.test.n` is 15382 [[art:e55953e1:metrics.test.n]].
The value of `metrics.train.auc` is 0.7892 [[art:39508266:metrics.train.auc]].
The value of `metrics.train.brier` is 0.01036 [[art:d56a10b2:metrics.train.brier]].
The value of `metrics.train.event_rate` is 0.008525 [[art:b9ef3327:metrics.train.event_rate]].
The value of `metrics.train.gini` is 0.5783 [[art:d618ff0f:metrics.train.gini]].
The value of `metrics.train.ks` is 0.4542 [[art:e8d4ae61:metrics.train.ks]].
The value of `metrics.train.logloss` is 0.06297 [[art:2bff29d3:metrics.train.logloss]].
The value of `metrics.train.mean_predicted` is 0.03925 [[art:68f41b88:metrics.train.mean_predicted]].
The value of `metrics.train.n` is 36013 [[art:6fdfeabb:metrics.train.n]].
The value of `metrics.vintage_holdout.auc` is 0.7743 [[art:25db8aa3:metrics.vintage_holdout.auc]].
The value of `metrics.vintage_holdout.brier` is 0.006101 [[art:55737812:metrics.vintage_holdout.brier]].
The value of `metrics.vintage_holdout.event_rate` is 0.004817 [[art:e3590a16:metrics.vintage_holdout.event_rate]].
The value of `metrics.vintage_holdout.gini` is 0.5486 [[art:eff9b345:metrics.vintage_holdout.gini]].
The value of `metrics.vintage_holdout.ks` is 0.4531 [[art:a2ee5005:metrics.vintage_holdout.ks]].
The value of `metrics.vintage_holdout.logloss` is 0.04161 [[art:9f19871a:metrics.vintage_holdout.logloss]].
The value of `metrics.vintage_holdout.mean_predicted` is 0.02582 [[art:348107ae:metrics.vintage_holdout.mean_predicted]].
The value of `metrics.vintage_holdout.n` is 32177 [[art:37a92951:metrics.vintage_holdout.n]].
The value of `profile.test.n` is 15382 [[art:e3abc1b8:profile.test.n]].
The value of `profile.train.n` is 36013 [[art:c5ebd9c9:profile.train.n]].
The value of `psi.max` is 0.06189 [[art:c2e8c8fd:psi.max]].
The value of `runtime.max_seconds` is 300 [[art:2ad8d1a5:runtime.max_seconds]].
The value of `threshold.package.auc.test.min` is 0.65 [[art:fececac1:threshold.package.auc.test.min]].
The value of `threshold.package.calibration_slope.test.max` is 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The value of `threshold.package.calibration_slope.test.min` is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
The value of `vif.max` is 4.976 [[art:f9e0db60:vif.max]].

## 2. Conceptual soundness

This section follows the model risk management guidance at [[reg:SR26-2:V.1.a]].
The value of `ablation.baseline_auc` is 0.7673 [[art:54367df6:ablation.baseline_auc]].
The value of `ablation.burnout.delta_auc` is -0.0001876 [[art:3cba039b:ablation.burnout.delta_auc]].
The value of `ablation.credit_score.delta_auc` is -0.01474 [[art:9bdeb0df:ablation.credit_score.delta_auc]].
The value of `ablation.incentive.delta_auc` is -0.04117 [[art:78108590:ablation.incentive.delta_auc]].
The value of `ablation.loan_age.delta_auc` is 0.0008166 [[art:be669163:ablation.loan_age.delta_auc]].
The value of `ablation.note_rate.delta_auc` is -0.002585 [[art:14558b82:ablation.note_rate.delta_auc]].
The value of `ablation.orig_ltv.delta_auc` is -0.002294 [[art:57ea66c5:ablation.orig_ltv.delta_auc]].
The value of `ablation.orig_upb_log.delta_auc` is -0.01927 [[art:0ddb11a9:ablation.orig_upb_log.delta_auc]].
The value of `ablation.sato.delta_auc` is 0.0005201 [[art:57703504:ablation.sato.delta_auc]].
The value of `ablation.season_cos.delta_auc` is -0.0004826 [[art:a288439d:ablation.season_cos.delta_auc]].
The value of `ablation.season_sin.delta_auc` is -0.0003885 [[art:e54c8581:ablation.season_sin.delta_auc]].
The value of `challenger.auc` is 0.7337 [[art:705b66f0:challenger.auc]].
The value of `challenger.brier` is 0.00863 [[art:85a89ef9:challenger.brier]].
The value of `challenger.delta_auc` is -0.04213 [[art:1e990f53:challenger.delta_auc]].
The value of `metrics.test.auc` is 0.7758 [[art:2f4cab3e:metrics.test.auc]].
The value of `metrics.test.brier` is 0.009864 [[art:1e4aab51:metrics.test.brier]].
The value of `sign_check.burnout.agrees` is 0 [[art:56826e40:sign_check.burnout.agrees]].
The value of `sign_check.burnout.coef_sign` is -1 [[art:dcfb2de4:sign_check.burnout.coef_sign]].
The value of `sign_check.burnout.univariate_direction` is 1 [[art:bfc96bb2:sign_check.burnout.univariate_direction]].
The value of `sign_check.credit_score.agrees` is 1 [[art:915bf8eb:sign_check.credit_score.agrees]].
The value of `sign_check.credit_score.coef_sign` is 1 [[art:1ec1078b:sign_check.credit_score.coef_sign]].
The value of `sign_check.credit_score.univariate_direction` is 1 [[art:42303896:sign_check.credit_score.univariate_direction]].
The value of `sign_check.incentive.agrees` is 1 [[art:f7b2338e:sign_check.incentive.agrees]].
The value of `sign_check.incentive.coef_sign` is 1 [[art:684cf11a:sign_check.incentive.coef_sign]].
The value of `sign_check.incentive.univariate_direction` is 1 [[art:8098d951:sign_check.incentive.univariate_direction]].
The value of `sign_check.n_disagreements` is 3 [[art:e223cd4a:sign_check.n_disagreements]].
The value of `sign_check.note_rate.agrees` is 0 [[art:a453463d:sign_check.note_rate.agrees]].
The value of `sign_check.note_rate.coef_sign` is -1 [[art:aecf7ccb:sign_check.note_rate.coef_sign]].
The value of `sign_check.note_rate.univariate_direction` is 1 [[art:61f6e1ac:sign_check.note_rate.univariate_direction]].
The value of `sign_check.orig_ltv.agrees` is 1 [[art:7021aeb0:sign_check.orig_ltv.agrees]].
The value of `sign_check.orig_ltv.coef_sign` is -1 [[art:7eec65ec:sign_check.orig_ltv.coef_sign]].
The value of `sign_check.orig_ltv.univariate_direction` is -1 [[art:76dbc708:sign_check.orig_ltv.univariate_direction]].
The value of `sign_check.orig_upb_log.agrees` is 1 [[art:07a9d3e6:sign_check.orig_upb_log.agrees]].
The value of `sign_check.orig_upb_log.coef_sign` is 1 [[art:5aa309fc:sign_check.orig_upb_log.coef_sign]].
The value of `sign_check.orig_upb_log.univariate_direction` is 1 [[art:b9743ecb:sign_check.orig_upb_log.univariate_direction]].
The value of `sign_check.sato.agrees` is 0 [[art:b3755963:sign_check.sato.agrees]].
The value of `sign_check.sato.coef_sign` is -1 [[art:265915cf:sign_check.sato.coef_sign]].
The value of `sign_check.sato.univariate_direction` is 1 [[art:c08233a6:sign_check.sato.univariate_direction]].
The value of `sign_check.season_cos.agrees` is 1 [[art:7f18ddf7:sign_check.season_cos.agrees]].
The value of `sign_check.season_cos.coef_sign` is -1 [[art:7dbb1ffc:sign_check.season_cos.coef_sign]].
The value of `sign_check.season_cos.univariate_direction` is -1 [[art:03e931f0:sign_check.season_cos.univariate_direction]].
The value of `sign_check.season_sin.agrees` is 1 [[art:e110f357:sign_check.season_sin.agrees]].
The value of `sign_check.season_sin.coef_sign` is 1 [[art:761188ce:sign_check.season_sin.coef_sign]].
The value of `sign_check.season_sin.univariate_direction` is 1 [[art:cae6b096:sign_check.season_sin.univariate_direction]].
The value of `threshold.E1.delta_auc` is 0.03 [[art:e042774c:threshold.E1.delta_auc]].

## 3. Data integrity and drift

This section follows the model risk management guidance at [[reg:SR26-2:V.1.a]].
The value of `csi.burnout` is 0.0001326 [[art:640f9435:csi.burnout]].
The value of `csi.credit_score` is 0.007707 [[art:6653968a:csi.credit_score]].
The value of `csi.incentive` is 0.005686 [[art:3bfa986b:csi.incentive]].
The value of `csi.loan_age` is 0 [[art:df52c920:csi.loan_age]].
The value of `csi.max` is 0.03331 [[art:a8ca288d:csi.max]].
The value of `csi.note_rate` is 0.01372 [[art:e06d8658:csi.note_rate]].
The value of `csi.orig_ltv` is 0.03331 [[art:7a941368:csi.orig_ltv]].
The value of `csi.orig_upb_log` is 0.002863 [[art:bbbec9d2:csi.orig_upb_log]].
The value of `csi.sato` is 0.0009305 [[art:c9bad372:csi.sato]].
The value of `csi.season_cos` is 0.0005034 [[art:78d740c8:csi.season_cos]].
The value of `csi.season_sin` is 0.0000694 [[art:d16ad42f:csi.season_sin]].
The value of `leakage.duplicates.train` is 0 [[art:4474c227:leakage.duplicates.train]].
The value of `leakage.name_screen.n_matched` is 0 [[art:407e62be:leakage.name_screen.n_matched]].
The value of `leakage.overlap` is 0 [[art:4c9fcd09:leakage.overlap]].
The value of `leakage.overlap.features` is 0 [[art:0fec8048:leakage.overlap.features]].
The value of `leakage.overlap.ids` is 0 [[art:63d37fc5:leakage.overlap.ids]].
The value of `leakage.target_corr.max_single_feature_auc` is 0.7239 [[art:1fe630dd:leakage.target_corr.max_single_feature_auc]].
The value of `leakage.timing.n_flagged` is 0 [[art:742bcd24:leakage.timing.n_flagged]].
The value of `profile.out_of_time.missing.max` is 0 [[art:4dafce11:profile.out_of_time.missing.max]].
The value of `profile.out_of_time.n` is 12257 [[art:fa39c5cf:profile.out_of_time.n]].
The value of `profile.test.missing.max` is 0 [[art:f813848d:profile.test.missing.max]].
The value of `profile.test.n` is 15382 [[art:e3abc1b8:profile.test.n]].
The value of `profile.train.missing.max` is 0 [[art:050a3099:profile.train.missing.max]].
The value of `profile.train.n` is 36013 [[art:c5ebd9c9:profile.train.n]].
The value of `profile.vintage_holdout.missing.max` is 0 [[art:329bb430:profile.vintage_holdout.missing.max]].
The value of `profile.vintage_holdout.n` is 32177 [[art:426e712a:profile.vintage_holdout.n]].
The value of `psi.burnout` is 0.004614 [[art:9dc7ecc2:psi.burnout]].
The value of `psi.credit_score` is 0.06189 [[art:7e87527c:psi.credit_score]].
The value of `psi.incentive` is 0.0009923 [[art:2da5570f:psi.incentive]].
The value of `psi.loan_age` is 0.0001994 [[art:2202b157:psi.loan_age]].
The value of `psi.max` is 0.06189 [[art:c2e8c8fd:psi.max]].
The value of `psi.note_rate` is 0.01371 [[art:ecc6adf3:psi.note_rate]].
The value of `psi.orig_ltv` is 0.03617 [[art:cd1ff136:psi.orig_ltv]].
The value of `psi.orig_upb_log` is 0.04817 [[art:55030a3b:psi.orig_upb_log]].
The value of `psi.out_of_time.burnout` is 2.945 [[art:7b0bbebb:psi.out_of_time.burnout]].
The value of `psi.out_of_time.credit_score` is 0.05988 [[art:d7249e47:psi.out_of_time.credit_score]].
The value of `psi.out_of_time.incentive` is 0.4958 [[art:42076ed1:psi.out_of_time.incentive]].
The value of `psi.out_of_time.loan_age` is 2.484 [[art:d6eaaaf5:psi.out_of_time.loan_age]].
The value of `psi.out_of_time.note_rate` is 0.6977 [[art:cabd371d:psi.out_of_time.note_rate]].
The value of `psi.out_of_time.orig_ltv` is 0.04301 [[art:3eee5db4:psi.out_of_time.orig_ltv]].
The value of `psi.out_of_time.orig_upb_log` is 0.07136 [[art:ac349b67:psi.out_of_time.orig_upb_log]].
The value of `psi.out_of_time.sato` is 0.01299 [[art:c2233ce6:psi.out_of_time.sato]].
The value of `psi.out_of_time.season_cos` is 0.007524 [[art:25cf6b85:psi.out_of_time.season_cos]].
The value of `psi.out_of_time.season_sin` is 0.02789 [[art:144e1bd9:psi.out_of_time.season_sin]].
The value of `psi.out_of_time.y_score` is 0.6985 [[art:6f080528:psi.out_of_time.y_score]].
The value of `psi.sato` is 0.02773 [[art:584da64f:psi.sato]].
The value of `psi.season_cos` is 0.0000179 [[art:addec503:psi.season_cos]].
The value of `psi.season_sin` is 0.000002939 [[art:4d2ed98d:psi.season_sin]].
The value of `psi.vintage_holdout.burnout` is 0.04749 [[art:e29067e6:psi.vintage_holdout.burnout]].
The value of `psi.vintage_holdout.credit_score` is 0.03996 [[art:3498d307:psi.vintage_holdout.credit_score]].
The value of `psi.vintage_holdout.incentive` is 0.4475 [[art:5e61b6f9:psi.vintage_holdout.incentive]].
The value of `psi.vintage_holdout.loan_age` is 0.07112 [[art:6d92c48b:psi.vintage_holdout.loan_age]].
The value of `psi.vintage_holdout.note_rate` is 0.6088 [[art:f281f8a7:psi.vintage_holdout.note_rate]].
The value of `psi.vintage_holdout.orig_ltv` is 0.02942 [[art:d07cfb7d:psi.vintage_holdout.orig_ltv]].
The value of `psi.vintage_holdout.orig_upb_log` is 0.0404 [[art:77ec758a:psi.vintage_holdout.orig_upb_log]].
The value of `psi.vintage_holdout.sato` is 0.02989 [[art:eea64c25:psi.vintage_holdout.sato]].
The value of `psi.vintage_holdout.season_cos` is 0.001288 [[art:9fe842a8:psi.vintage_holdout.season_cos]].
The value of `psi.vintage_holdout.season_sin` is 0.0007309 [[art:b0dc9745:psi.vintage_holdout.season_sin]].
The value of `psi.vintage_holdout.y_score` is 0.1604 [[art:c71062d6:psi.vintage_holdout.y_score]].
The value of `psi.y_score` is 0.001869 [[art:aa10164c:psi.y_score]].
The value of `threshold.D1.missing_gap` is 0.1 [[art:9cce25ea:threshold.D1.missing_gap]].
The value of `threshold.L1.single_feature_auc` is 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]].
The value of `threshold.L2.overlap` is 0.005 [[art:9f336eaf:threshold.L2.overlap]].
The value of `threshold.L2.overlap.features_effective` is 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].
The value of `threshold.S1.psi` is 0.25 [[art:278b9016:threshold.S1.psi]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].

## 4. Outcomes analysis

This section follows the model risk management guidance at [[reg:SR26-2:V.1.b]].
The value of `calibration.mean_rel_gap.out_of_time` is 3.342 [[art:5b8375ec:calibration.mean_rel_gap.out_of_time]].
The value of `calibration.mean_rel_gap.test` is 3.716 [[art:15d5555b:calibration.mean_rel_gap.test]].
The value of `calibration.mean_rel_gap.train` is 3.604 [[art:324eb124:calibration.mean_rel_gap.train]].
The value of `calibration.mean_rel_gap.vintage_holdout` is 4.36 [[art:a691b5ed:calibration.mean_rel_gap.vintage_holdout]].
The value of `calibration_intercept.out_of_time` is -1.497 [[art:db324216:calibration_intercept.out_of_time]].
The value of `calibration_intercept.test` is -1.748 [[art:257fb817:calibration_intercept.test]].
The value of `calibration_intercept.train` is -1.566 [[art:57309d7d:calibration_intercept.train]].
The value of `calibration_intercept.vintage_holdout` is -2.176 [[art:6f00dbc2:calibration_intercept.vintage_holdout]].
The value of `calibration_slope.out_of_time` is 1.066 [[art:ea7d5696:calibration_slope.out_of_time]].
The value of `calibration_slope.test` is 0.9537 [[art:f8ef2beb:calibration_slope.test]].
The value of `calibration_slope.train` is 1.015 [[art:ffabb935:calibration_slope.train]].
The value of `calibration_slope.vintage_holdout` is 0.8562 [[art:010c0ec4:calibration_slope.vintage_holdout]].
The value of `cpr.out_of_time.mae` is 0.318 [[art:8ac7bfbc:cpr.out_of_time.mae]].
The value of `cpr.test.mae` is 0.222 [[art:b7587aed:cpr.test.mae]].
The value of `cpr.train.mae` is 0.224 [[art:8d8e2c42:cpr.train.mae]].
The value of `cpr.vintage_holdout.mae` is 0.172 [[art:2d48e163:cpr.vintage_holdout.mae]].
The value of `deciles.out_of_time.top2_capture` is 0.5909 [[art:95c24730:deciles.out_of_time.top2_capture]].
The value of `deciles.test.top2_capture` is 0.5806 [[art:43c4adc5:deciles.test.top2_capture]].
The value of `deciles.train.top2_capture` is 0.6059 [[art:eb38637b:deciles.train.top2_capture]].
The value of `deciles.vintage_holdout.top2_capture` is 0.5935 [[art:4a376307:deciles.vintage_holdout.top2_capture]].
The value of `metrics.out_of_time.auc` is 0.7898 [[art:aa836722:metrics.out_of_time.auc]].
The value of `metrics.out_of_time.brier` is 0.02402 [[art:a8a8d3a5:metrics.out_of_time.brier]].
The value of `metrics.out_of_time.event_rate` is 0.01795 [[art:83ccf5c0:metrics.out_of_time.event_rate]].
The value of `metrics.out_of_time.gini` is 0.5796 [[art:3dc07327:metrics.out_of_time.gini]].
The value of `metrics.out_of_time.ks` is 0.4368 [[art:00bf02ed:metrics.out_of_time.ks]].
The value of `metrics.out_of_time.logloss` is 0.1174 [[art:5198f968:metrics.out_of_time.logloss]].
The value of `metrics.out_of_time.mean_predicted` is 0.07793 [[art:921d185b:metrics.out_of_time.mean_predicted]].
The value of `metrics.out_of_time.n` is 12257 [[art:7898809e:metrics.out_of_time.n]].
The value of `metrics.test.auc` is 0.7758 [[art:2f4cab3e:metrics.test.auc]].
The value of `metrics.test.brier` is 0.009864 [[art:1e4aab51:metrics.test.brier]].
The value of `metrics.test.event_rate` is 0.008061 [[art:570cc08a:metrics.test.event_rate]].
The value of `metrics.test.gini` is 0.5517 [[art:8593585c:metrics.test.gini]].
The value of `metrics.test.ks` is 0.428 [[art:554f1e19:metrics.test.ks]].
The value of `metrics.test.logloss` is 0.06118 [[art:b9424e16:metrics.test.logloss]].
The value of `metrics.test.mean_predicted` is 0.03802 [[art:122af437:metrics.test.mean_predicted]].
The value of `metrics.test.n` is 15382 [[art:e55953e1:metrics.test.n]].
The value of `metrics.train.auc` is 0.7892 [[art:39508266:metrics.train.auc]].
The value of `metrics.train.brier` is 0.01036 [[art:d56a10b2:metrics.train.brier]].
The value of `metrics.train.event_rate` is 0.008525 [[art:b9ef3327:metrics.train.event_rate]].
The value of `metrics.train.gini` is 0.5783 [[art:d618ff0f:metrics.train.gini]].
The value of `metrics.train.ks` is 0.4542 [[art:e8d4ae61:metrics.train.ks]].
The value of `metrics.train.logloss` is 0.06297 [[art:2bff29d3:metrics.train.logloss]].
The value of `metrics.train.mean_predicted` is 0.03925 [[art:68f41b88:metrics.train.mean_predicted]].
The value of `metrics.train.n` is 36013 [[art:6fdfeabb:metrics.train.n]].
The value of `metrics.vintage_holdout.auc` is 0.7743 [[art:25db8aa3:metrics.vintage_holdout.auc]].
The value of `metrics.vintage_holdout.brier` is 0.006101 [[art:55737812:metrics.vintage_holdout.brier]].
The value of `metrics.vintage_holdout.event_rate` is 0.004817 [[art:e3590a16:metrics.vintage_holdout.event_rate]].
The value of `metrics.vintage_holdout.gini` is 0.5486 [[art:eff9b345:metrics.vintage_holdout.gini]].
The value of `metrics.vintage_holdout.ks` is 0.4531 [[art:a2ee5005:metrics.vintage_holdout.ks]].
The value of `metrics.vintage_holdout.logloss` is 0.04161 [[art:9f19871a:metrics.vintage_holdout.logloss]].
The value of `metrics.vintage_holdout.mean_predicted` is 0.02582 [[art:348107ae:metrics.vintage_holdout.mean_predicted]].
The value of `metrics.vintage_holdout.n` is 32177 [[art:37a92951:metrics.vintage_holdout.n]].
The value of `psi.burnout` is 0.004614 [[art:9dc7ecc2:psi.burnout]].
The value of `psi.credit_score` is 0.06189 [[art:7e87527c:psi.credit_score]].
The value of `psi.incentive` is 0.0009923 [[art:2da5570f:psi.incentive]].
The value of `psi.loan_age` is 0.0001994 [[art:2202b157:psi.loan_age]].
The value of `psi.max` is 0.06189 [[art:c2e8c8fd:psi.max]].
The value of `psi.note_rate` is 0.01371 [[art:ecc6adf3:psi.note_rate]].
The value of `psi.orig_ltv` is 0.03617 [[art:cd1ff136:psi.orig_ltv]].
The value of `psi.orig_upb_log` is 0.04817 [[art:55030a3b:psi.orig_upb_log]].
The value of `psi.out_of_time.burnout` is 2.945 [[art:7b0bbebb:psi.out_of_time.burnout]].
The value of `psi.out_of_time.credit_score` is 0.05988 [[art:d7249e47:psi.out_of_time.credit_score]].
The value of `psi.out_of_time.incentive` is 0.4958 [[art:42076ed1:psi.out_of_time.incentive]].
The value of `psi.out_of_time.loan_age` is 2.484 [[art:d6eaaaf5:psi.out_of_time.loan_age]].
The value of `psi.out_of_time.note_rate` is 0.6977 [[art:cabd371d:psi.out_of_time.note_rate]].
The value of `psi.out_of_time.orig_ltv` is 0.04301 [[art:3eee5db4:psi.out_of_time.orig_ltv]].
The value of `psi.out_of_time.orig_upb_log` is 0.07136 [[art:ac349b67:psi.out_of_time.orig_upb_log]].
The value of `psi.out_of_time.sato` is 0.01299 [[art:c2233ce6:psi.out_of_time.sato]].
The value of `psi.out_of_time.season_cos` is 0.007524 [[art:25cf6b85:psi.out_of_time.season_cos]].
The value of `psi.out_of_time.season_sin` is 0.02789 [[art:144e1bd9:psi.out_of_time.season_sin]].
The value of `psi.out_of_time.y_score` is 0.6985 [[art:6f080528:psi.out_of_time.y_score]].
The value of `psi.sato` is 0.02773 [[art:584da64f:psi.sato]].
The value of `psi.season_cos` is 0.0000179 [[art:addec503:psi.season_cos]].
The value of `psi.season_sin` is 0.000002939 [[art:4d2ed98d:psi.season_sin]].
The value of `psi.vintage_holdout.burnout` is 0.04749 [[art:e29067e6:psi.vintage_holdout.burnout]].
The value of `psi.vintage_holdout.credit_score` is 0.03996 [[art:3498d307:psi.vintage_holdout.credit_score]].
The value of `psi.vintage_holdout.incentive` is 0.4475 [[art:5e61b6f9:psi.vintage_holdout.incentive]].
The value of `psi.vintage_holdout.loan_age` is 0.07112 [[art:6d92c48b:psi.vintage_holdout.loan_age]].
The value of `psi.vintage_holdout.note_rate` is 0.6088 [[art:f281f8a7:psi.vintage_holdout.note_rate]].
The value of `psi.vintage_holdout.orig_ltv` is 0.02942 [[art:d07cfb7d:psi.vintage_holdout.orig_ltv]].
The value of `psi.vintage_holdout.orig_upb_log` is 0.0404 [[art:77ec758a:psi.vintage_holdout.orig_upb_log]].
The value of `psi.vintage_holdout.sato` is 0.02989 [[art:eea64c25:psi.vintage_holdout.sato]].
The value of `psi.vintage_holdout.season_cos` is 0.001288 [[art:9fe842a8:psi.vintage_holdout.season_cos]].
The value of `psi.vintage_holdout.season_sin` is 0.0007309 [[art:b0dc9745:psi.vintage_holdout.season_sin]].
The value of `psi.vintage_holdout.y_score` is 0.1604 [[art:c71062d6:psi.vintage_holdout.y_score]].
The value of `psi.y_score` is 0.001869 [[art:aa10164c:psi.y_score]].
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
The value of `threshold.O1.holdout_gap` is 0.05 [[art:90f8b6d9:threshold.O1.holdout_gap]].
The value of `threshold.R1.auc_gap` is 0.1 [[art:b64213d7:threshold.R1.auc_gap]].
The value of `threshold.R1.sign_flip_coef` is 0.05 [[art:aca84377:threshold.R1.sign_flip_coef]].
The value of `threshold.R1.sign_flip_z` is 2 [[art:2e4428c7:threshold.R1.sign_flip_z]].
The value of `threshold.S1.psi` is 0.25 [[art:278b9016:threshold.S1.psi]].
The value of `threshold.package.auc.test.min` is 0.65 [[art:fececac1:threshold.package.auc.test.min]].
The value of `threshold.package.calibration_slope.test.max` is 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The value of `threshold.package.calibration_slope.test.min` is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
<!-- quaestor:renderer:begin table calibration.test -->
Calibration by decile of predicted probability on test [[art:8417f6b7:calibration.test]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.002089 | 0.0006498 | 1539 |
| 2 | 0.004414 | 0.0013 | 1539 |
| 3 | 0.007429 | 0.003901 | 1538 |
| 4 | 0.01186 | 0.001951 | 1538 |
| 5 | 0.01785 | 0.002601 | 1538 |
| 6 | 0.02599 | 0.004551 | 1538 |
| 7 | 0.03753 | 0.009753 | 1538 |
| 8 | 0.05466 | 0.009103 | 1538 |
| 9 | 0.08015 | 0.01365 | 1538 |
| 10 | 0.1383 | 0.03316 | 1538 |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table cpr.test -->
Actual against predicted CPR by period on test [[art:ee6d2090:cpr.test]]:

| period | n | actual_cpr | predicted_cpr |
|---|---|---|---|
| 201402 | 15 | 0 | 0.1368 |
| 201403 | 28 | 0 | 0.1194 |
| 201404 | 56 | 0 | 0.08868 |
| 201405 | 68 | 0 | 0.08852 |
| 201406 | 80 | 0 | 0.08786 |
| 201407 | 97 | 0.1169 | 0.07477 |
| 201408 | 111 | 0 | 0.0662 |
| 201409 | 133 | 0.08659 | 0.05285 |
| 201410 | 145 | 0 | 0.04497 |
| 201411 | 161 | 0 | 0.03631 |
| 201412 | 175 | 0 | 0.03572 |
| 201501 | 198 | 0 | 0.03448 |
| 201502 | 198 | 0 | 0.03316 |
| 201503 | 198 | 0.05895 | 0.04122 |
| 201504 | 197 | 0 | 0.04587 |
| 201505 | 197 | 0 | 0.06373 |
| 201506 | 197 | 0 | 0.07241 |
| 201507 | 197 | 0 | 0.09378 |
| 201508 | 197 | 0 | 0.1274 |
| 201509 | 197 | 0.05924 | 0.1394 |
| 201510 | 196 | 0.05954 | 0.1707 |
| 201511 | 195 | 0 | 0.2145 |
| 201512 | 195 | 0 | 0.2228 |
| 201601 | 195 | 0.1698 | 0.3043 |
| 201602 | 192 | 0.06074 | 0.4154 |
| 201603 | 191 | 0.1187 | 0.5133 |
| 201604 | 189 | 0.1198 | 0.5524 |
| 201605 | 187 | 0.3673 | 0.6701 |
| 201606 | 180 | 0.1255 | 0.6637 |
| 201607 | 178 | 0.1268 | 0.6819 |
| 201608 | 176 | 0.06609 | 0.6476 |
| 201609 | 175 | 0.1288 | 0.5592 |
| 201610 | 173 | 0.1893 | 0.4488 |
| 201611 | 170 | 0.06835 | 0.391 |
| 201612 | 169 | 0.06874 | 0.3006 |
| 201701 | 168 | 0.1339 | 0.2555 |
| 201702 | 176 | 0.2924 | 0.2214 |
| 201703 | 191 | 0.06105 | 0.1945 |
| 201704 | 199 | 0 | 0.1731 |
| 201705 | 218 | 0.05368 | 0.1722 |
| 201706 | 238 | 0.04927 | 0.1571 |
| 201707 | 248 | 0 | 0.1373 |
| 201708 | 274 | 0 | 0.109 |
| 201709 | 284 | 0.08131 | 0.1122 |
| 201710 | 300 | 0 | 0.08701 |
| 201711 | 323 | 0.03653 | 0.08585 |
| 201712 | 334 | 0.03534 | 0.1069 |
| 201801 | 354 | 0.03338 | 0.1216 |
| 201802 | 353 | 0.06591 | 0.1636 |
| 201803 | 351 | 0.03366 | 0.2442 |
| 201804 | 350 | 0.06646 | 0.3557 |
| 201805 | 348 | 0.1594 | 0.4904 |
| 201806 | 343 | 0.1616 | 0.5521 |
| 201807 | 338 | 0.1638 | 0.5789 |
| 201808 | 333 | 0.06974 | 0.6036 |
| 201809 | 331 | 0.2544 | 0.6206 |
| 201810 | 323 | 0.1707 | 0.6032 |
| 201811 | 318 | 0.07292 | 0.5628 |
| 201812 | 316 | 0.1742 | 0.6044 |
| 201901 | 311 | 0.1098 | 0.6257 |
| 201902 | 300 | 0.1488 | 0.6911 |
| 201903 | 285 | 0.2253 | 0.7179 |
| 201904 | 258 | 0.246 | 0.7039 |
| 201905 | 243 | 0.1385 | 0.6579 |
| 201906 | 233 | 0.2688 | 0.5808 |
| 201907 | 219 | 0.1984 | 0.4595 |
| 201908 | 206 | 0 | 0.3531 |
| 201909 | 191 | 0.06105 | 0.2547 |
| 201910 | 182 | 0.06398 | 0.1893 |
| 201911 | 171 | 0.06796 | 0.17 |
| 201912 | 166 | 0 | 0.1674 |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table deciles.test -->
Decile separation on test; decile 1 holds the highest probabilities [[art:9246d1cd:deciles.test]]:

| decile | count | events | event_rate | lift |
|---|---|---|---|---|
| 1 | 1539 | 51 | 0.03314 | 4.111 |
| 2 | 1539 | 21 | 0.01365 | 1.693 |
| 3 | 1538 | 14 | 0.009103 | 1.129 |
| 4 | 1538 | 15 | 0.009753 | 1.21 |
| 5 | 1538 | 7 | 0.004551 | 0.5646 |
| 6 | 1538 | 4 | 0.002601 | 0.3226 |
| 7 | 1538 | 3 | 0.001951 | 0.242 |
| 8 | 1538 | 6 | 0.003901 | 0.4839 |
| 9 | 1538 | 2 | 0.0013 | 0.1613 |
| 10 | 1538 | 1 | 0.0006502 | 0.08066 |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table thresholds.evaluation -->
Every threshold package.yaml declares, with its bound, the recomputed value and the outcome [[art:2fc2a920:thresholds.evaluation]]:

| metric | split | bound | value | result |
|---|---|---|---|---|
| auc | test | minimum 0.65 | 0.7758 | pass |
| calibration_slope | test | minimum 0.8 | 0.9537 | pass |
| calibration_slope | test | maximum 1.2 | 0.9537 | pass |
| psi |  | maximum 0.25 | 0.06189 | pass |
<!-- quaestor:renderer:end -->
Candidates raised on this section's material: C1; C1; C1; C1 (see the findings section).

## 5. Sensitivity and scenario analysis

This section follows the model risk management guidance at [[reg:SR26-2:V.1.a]].
The value of `condition_number` is 4.943 [[art:4f06a3c5:condition_number]].
The value of `scenario.convexity` is -541800 [[art:42ad3e3e:scenario.convexity]].
The value of `scenario.value_change.-100` is -517800 [[art:b3c09ea9:scenario.value_change.-100]].
The value of `scenario.value_change.-200` is -927100 [[art:59e2f8a4:scenario.value_change.-200]].
The value of `scenario.value_change.-300` is -1099000 [[art:ff90f8c1:scenario.value_change.-300]].
The value of `scenario.value_change.0` is 0 [[art:1e1b0b88:scenario.value_change.0]].
The value of `scenario.value_change.100` is 352800 [[art:95da798d:scenario.value_change.100]].
The value of `scenario.value_change.200` is 505800 [[art:be13cc25:scenario.value_change.200]].
The value of `scenario.value_change.300` is 557600 [[art:0b43db3b:scenario.value_change.300]].
The value of `stability.burnout.sign_flip` is 0 [[art:6bc05e82:stability.burnout.sign_flip]].
The value of `stability.credit_score.sign_flip` is 0 [[art:d956c276:stability.credit_score.sign_flip]].
The value of `stability.incentive.sign_flip` is 0 [[art:0cc7a37d:stability.incentive.sign_flip]].
The value of `stability.loan_age.sign_flip` is 0 [[art:b7191217:stability.loan_age.sign_flip]].
The value of `stability.note_rate.sign_flip` is 0 [[art:e7ce4912:stability.note_rate.sign_flip]].
The value of `stability.orig_ltv.sign_flip` is 0 [[art:054d5fab:stability.orig_ltv.sign_flip]].
The value of `stability.orig_upb_log.sign_flip` is 0 [[art:fb1ae6c8:stability.orig_upb_log.sign_flip]].
The value of `stability.sato.sign_flip` is 0 [[art:1f302ccd:stability.sato.sign_flip]].
The value of `stability.season_cos.sign_flip` is 0 [[art:1850e2de:stability.season_cos.sign_flip]].
The value of `stability.season_sin.sign_flip` is 0 [[art:6ba36a3b:stability.season_sin.sign_flip]].
The value of `threshold.M1.condition_number` is 30 [[art:7e52fd7a:threshold.M1.condition_number]].
The value of `threshold.M1.vif` is 10 [[art:aeb4f33c:threshold.M1.vif]].
The value of `threshold.R1.auc_gap` is 0.1 [[art:b64213d7:threshold.R1.auc_gap]].
The value of `threshold.R1.sign_flip_coef` is 0.05 [[art:aca84377:threshold.R1.sign_flip_coef]].
The value of `threshold.R1.sign_flip_z` is 2 [[art:2e4428c7:threshold.R1.sign_flip_z]].
The value of `vif.burnout` is 3.439 [[art:88879cb2:vif.burnout]].
The value of `vif.credit_score` is 1.008 [[art:f05d536a:vif.credit_score]].
The value of `vif.incentive` is 2.226 [[art:2da1b19c:vif.incentive]].
The value of `vif.loan_age` is 2.929 [[art:5573d536:vif.loan_age]].
The value of `vif.max` is 4.976 [[art:f9e0db60:vif.max]].
The value of `vif.note_rate` is 4.976 [[art:37532fa8:vif.note_rate]].
The value of `vif.orig_ltv` is 1.005 [[art:65b35f3b:vif.orig_ltv]].
The value of `vif.orig_upb_log` is 1.006 [[art:24f8e4d1:vif.orig_upb_log]].
The value of `vif.sato` is 1.713 [[art:a6c55fce:vif.sato]].
The value of `vif.season_cos` is 1.018 [[art:a9cfa7eb:vif.season_cos]].
The value of `vif.season_sin` is 1.004 [[art:669c5fcb:vif.season_sin]].
<!-- quaestor:renderer:begin table scenario.value_by_shock -->
Servicing value, its change from the base case and first-year CPR, by shock [[art:89b33839:scenario.value_by_shock]]:

| shock_bp | value | value_change | cpr |
|---|---|---|---|
| -300 | 89610 | -1.099e+06 | 0.9686 |
| -200 | 262000 | -927100 | 0.7096 |
| -100 | 671200 | -517800 | 0.3268 |
| 0 | 1.189e+06 | 0 | 0.113 |
| 100 | 1.542e+06 | 352800 | 0.03497 |
| 200 | 1.695e+06 | 505800 | 0.01044 |
| 300 | 1.747e+06 | 557600 | 0.003084 |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table stability.auc_by_regime -->
The champion's AUC within each rate_regime on train [[art:0b789c1f:stability.auc_by_regime]]:

| regime | n | event_rate | auc |
|---|---|---|---|
| falling | 17873 | 0.01438 | 0.7243 |
| rising | 18140 | 0.002756 | 0.7236 |
<!-- quaestor:renderer:end -->

## 6. Findings and recommendations

This section follows the model risk management guidance at [[reg:SR26-2:VI.3]].

### F-001 · C1 calibration · severity **medium**

**A `C1` finding, raised by `compute_metrics` at severity `medium`.**
Its evidence is the artifacts cited in this section; the check's own account of it is recorded in `findings.json`.
The value of `calibration.mean_rel_gap.out_of_time` is 3.342 [[art:5b8375ec:calibration.mean_rel_gap.out_of_time]].
The value of `calibration.mean_rel_gap.test` is 3.716 [[art:15d5555b:calibration.mean_rel_gap.test]].
The value of `calibration.mean_rel_gap.train` is 3.604 [[art:324eb124:calibration.mean_rel_gap.train]].
The value of `calibration.mean_rel_gap.vintage_holdout` is 4.36 [[art:a691b5ed:calibration.mean_rel_gap.vintage_holdout]].
The value of `metrics.out_of_time.event_rate` is 0.01795 [[art:83ccf5c0:metrics.out_of_time.event_rate]].
The value of `metrics.out_of_time.mean_predicted` is 0.07793 [[art:921d185b:metrics.out_of_time.mean_predicted]].
The value of `metrics.test.event_rate` is 0.008061 [[art:570cc08a:metrics.test.event_rate]].
The value of `metrics.test.mean_predicted` is 0.03802 [[art:122af437:metrics.test.mean_predicted]].
The value of `metrics.train.event_rate` is 0.008525 [[art:b9ef3327:metrics.train.event_rate]].
The value of `metrics.train.mean_predicted` is 0.03925 [[art:68f41b88:metrics.train.mean_predicted]].
The value of `metrics.vintage_holdout.event_rate` is 0.004817 [[art:e3590a16:metrics.vintage_holdout.event_rate]].
The value of `metrics.vintage_holdout.mean_predicted` is 0.02582 [[art:348107ae:metrics.vintage_holdout.mean_predicted]].
The value of `sign_check.burnout.agrees` is 0 [[art:56826e40:sign_check.burnout.agrees]].
The value of `sign_check.burnout.coef_sign` is -1 [[art:dcfb2de4:sign_check.burnout.coef_sign]].
The value of `sign_check.burnout.univariate_direction` is 1 [[art:bfc96bb2:sign_check.burnout.univariate_direction]].
The value of `sign_check.note_rate.agrees` is 0 [[art:a453463d:sign_check.note_rate.agrees]].
The value of `sign_check.note_rate.coef_sign` is -1 [[art:aecf7ccb:sign_check.note_rate.coef_sign]].
The value of `sign_check.note_rate.univariate_direction` is 1 [[art:61f6e1ac:sign_check.note_rate.univariate_direction]].
The value of `sign_check.sato.agrees` is 0 [[art:b3755963:sign_check.sato.agrees]].
The value of `sign_check.sato.coef_sign` is -1 [[art:265915cf:sign_check.sato.coef_sign]].
The value of `sign_check.sato.univariate_direction` is 1 [[art:c08233a6:sign_check.sato.univariate_direction]].
The value of `threshold.C1.mean_ratio_rel` is 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
<!-- quaestor:renderer:begin table calibration.out_of_time -->
Calibration by decile of predicted probability on out_of_time [[art:392a629c:calibration.out_of_time]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.008744 | 0 | 1226 |
| 2 | 0.01645 | 0.002447 | 1226 |
| 3 | 0.02357 | 0.003263 | 1226 |
| 4 | 0.03155 | 0.008157 | 1226 |
| 5 | 0.04144 | 0.0106 | 1226 |
| 6 | 0.0546 | 0.01223 | 1226 |
| 7 | 0.07307 | 0.01468 | 1226 |
| 8 | 0.1034 | 0.02204 | 1225 |
| 9 | 0.1546 | 0.02449 | 1225 |
| 10 | 0.2721 | 0.08163 | 1225 |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table calibration.test -->
Calibration by decile of predicted probability on test [[art:8417f6b7:calibration.test]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.002089 | 0.0006498 | 1539 |
| 2 | 0.004414 | 0.0013 | 1539 |
| 3 | 0.007429 | 0.003901 | 1538 |
| 4 | 0.01186 | 0.001951 | 1538 |
| 5 | 0.01785 | 0.002601 | 1538 |
| 6 | 0.02599 | 0.004551 | 1538 |
| 7 | 0.03753 | 0.009753 | 1538 |
| 8 | 0.05466 | 0.009103 | 1538 |
| 9 | 0.08015 | 0.01365 | 1538 |
| 10 | 0.1383 | 0.03316 | 1538 |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table calibration.train -->
Calibration by decile of predicted probability on train [[art:a8585045:calibration.train]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.002166 | 0.0008329 | 3602 |
| 2 | 0.004511 | 0.001943 | 3602 |
| 3 | 0.007472 | 0.00111 | 3602 |
| 4 | 0.01183 | 0.002499 | 3601 |
| 5 | 0.0181 | 0.00361 | 3601 |
| 6 | 0.02708 | 0.004443 | 3601 |
| 7 | 0.03949 | 0.007498 | 3601 |
| 8 | 0.05611 | 0.01166 | 3601 |
| 9 | 0.08192 | 0.01805 | 3601 |
| 10 | 0.1439 | 0.0336 | 3601 |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table calibration.vintage_holdout -->
Calibration by decile of predicted probability on vintage_holdout [[art:fd5aec5a:calibration.vintage_holdout]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.001905 | 0.0006215 | 3218 |
| 2 | 0.003662 | 0.002175 | 3218 |
| 3 | 0.005429 | 0.0006215 | 3218 |
| 4 | 0.007464 | 0.001243 | 3218 |
| 5 | 0.0101 | 0.0009323 | 3218 |
| 6 | 0.01391 | 0.003108 | 3218 |
| 7 | 0.01993 | 0.00404 | 3218 |
| 8 | 0.0306 | 0.006839 | 3217 |
| 9 | 0.05066 | 0.008082 | 3217 |
| 10 | 0.1146 | 0.02052 | 3217 |
<!-- quaestor:renderer:end -->

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1, S1), `compute_metrics` (T1, O1), `check_leakage` (L1, L2), `check_stability` (R1), `check_collinearity` (M1), `challenger_compare` (E1), `run_scenarios` (X1).

### Open items

No open item was recorded for this validation.

## 7. Ongoing monitoring recommendations

This section follows the model risk management guidance at [[reg:SR26-2:V.2]].
The value of `calibration_slope.test` is 0.9537 [[art:f8ef2beb:calibration_slope.test]].
The value of `metrics.test.auc` is 0.7758 [[art:2f4cab3e:metrics.test.auc]].
The value of `psi.max` is 0.06189 [[art:c2e8c8fd:psi.max]].
The value of `rule.calibration_first_event_rate` is 0.05 [[art:42f1351e:rule.calibration_first_event_rate]].
The value of `threshold.package.auc.test.min` is 0.65 [[art:fececac1:threshold.package.auc.test.min]].
The value of `threshold.package.calibration_slope.test.max` is 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The value of `threshold.package.calibration_slope.test.min` is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].

## Appendix A — Claims

Grounding precision 1.0000 before repair (330 of 330 claims verified) and 1.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 48/48; conceptual_soundness 45/45; data_integrity 66/66; outcomes 106/106; sensitivity 35/35; findings 22/22; monitoring 8/8.

Developer claims: The package declares 3 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). See Appendix D.

Excluded numeric tokens (not claims): inline_code (`scenario.value_change.-100`, `scenario.value_change.-200`, `scenario.value_change.-300`); citation_hash (ea7d5696, f8ef2beb, ffabb935, 010c0ec4); regulatory_section_id (SR26-2:V.1.b, SR26-2:V.1.a, SR26-2:VI.3, SR26-2:V.2); finding_id (F-001).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The value of `calibration_slope.out_of_time` is 1.066 . | 1.066 | ratio | calibration_slope |  | eq | `[[art:ea7d5696:calibration_slope.out_of_time]]` | verified | 1.066358183 |
| 2 | summary | The value of `calibration_slope.test` is 0.9537 . | 0.9537 | ratio | calibration_slope |  | eq | `[[art:f8ef2beb:calibration_slope.test]]` | verified | 0.9536630305 |
| 3 | summary | The value of `calibration_slope.train` is 1.015 . | 1.015 | ratio | calibration_slope |  | eq | `[[art:ffabb935:calibration_slope.train]]` | verified | 1.014728573 |
| 4 | summary | The value of `calibration_slope.vintage_holdout` is 0.8562 . | 0.8562 | ratio | calibration_slope |  | eq | `[[art:010c0ec4:calibration_slope.vintage_holdout]]` | verified | 0.8561504457 |
| 5 | summary | The value of `challenger.delta_auc` is -0.04213 . | -0.04213 | ratio | challenger |  | eq | `[[art:1e990f53:challenger.delta_auc]]` | verified | -0.04212940647 |
| 6 | summary | The value of `condition_number` is 4.943 . | 4.943 | ratio | condition_number |  | eq | `[[art:4f06a3c5:condition_number]]` | verified | 4.942565522 |
| 7 | summary | The value of `csi.max` is 0.03331 . | 0.03331 | ratio | csi |  | eq | `[[art:a8ca288d:csi.max]]` | verified | 0.03331391493 |
| 8 | summary | The value of `metrics.out_of_time.auc` is 0.7898 . | 0.7898 | ratio | metrics |  | eq | `[[art:aa836722:metrics.out_of_time.auc]]` | verified | 0.7897867937 |
| 9 | summary | The value of `metrics.out_of_time.brier` is 0.02402 . | 0.02402 | ratio | metrics |  | eq | `[[art:a8a8d3a5:metrics.out_of_time.brier]]` | verified | 0.02402096444 |
| 10 | summary | The value of `metrics.out_of_time.event_rate` is 0.01795 . | 0.01795 | ratio | metrics |  | eq | `[[art:83ccf5c0:metrics.out_of_time.event_rate]]` | verified | 0.01794892714 |
| 11 | summary | The value of `metrics.out_of_time.gini` is 0.5796 . | 0.5796 | ratio | metrics |  | eq | `[[art:3dc07327:metrics.out_of_time.gini]]` | verified | 0.5795735875 |
| 12 | summary | The value of `metrics.out_of_time.ks` is 0.4368 . | 0.4368 | ratio | metrics |  | eq | `[[art:00bf02ed:metrics.out_of_time.ks]]` | verified | 0.43678733 |
| 13 | summary | The value of `metrics.out_of_time.logloss` is 0.1174 . | 0.1174 | ratio | metrics |  | eq | `[[art:5198f968:metrics.out_of_time.logloss]]` | verified | 0.1173954835 |
| 14 | summary | The value of `metrics.out_of_time.mean_predicted` is 0.07793… | 0.07793 | ratio | metrics |  | eq | `[[art:921d185b:metrics.out_of_time.mean_predicted]]` | verified | 0.07792752696 |
| 15 | summary | The value of `metrics.out_of_time.n` is 12257 . | 12257 | ratio | metrics |  | eq | `[[art:7898809e:metrics.out_of_time.n]]` | verified | 12257 |
| 16 | summary | The value of `metrics.test.auc` is 0.7758 . | 0.7758 | ratio | metrics |  | eq | `[[art:2f4cab3e:metrics.test.auc]]` | verified | 0.7758373186 |
| 17 | summary | The value of `metrics.test.brier` is 0.009864 . | 0.009864 | ratio | metrics |  | eq | `[[art:1e4aab51:metrics.test.brier]]` | verified | 0.009863834665 |
| 18 | summary | The value of `metrics.test.event_rate` is 0.008061 . | 0.008061 | ratio | metrics |  | eq | `[[art:570cc08a:metrics.test.event_rate]]` | verified | 0.008061370433 |
| 19 | summary | The value of `metrics.test.gini` is 0.5517 . | 0.5517 | ratio | metrics |  | eq | `[[art:8593585c:metrics.test.gini]]` | verified | 0.5516746371 |
| 20 | summary | The value of `metrics.test.ks` is 0.428 . | 0.428 | ratio | metrics |  | eq | `[[art:554f1e19:metrics.test.ks]]` | verified | 0.4280398649 |
| 21 | summary | The value of `metrics.test.logloss` is 0.06118 . | 0.06118 | ratio | metrics |  | eq | `[[art:b9424e16:metrics.test.logloss]]` | verified | 0.06118235348 |
| 22 | summary | The value of `metrics.test.mean_predicted` is 0.03802 . | 0.03802 | ratio | metrics |  | eq | `[[art:122af437:metrics.test.mean_predicted]]` | verified | 0.038020619 |
| 23 | summary | The value of `metrics.test.n` is 15382 . | 15382 | ratio | metrics |  | eq | `[[art:e55953e1:metrics.test.n]]` | verified | 15382 |
| 24 | summary | The value of `metrics.train.auc` is 0.7892 . | 0.7892 | ratio | metrics |  | eq | `[[art:39508266:metrics.train.auc]]` | verified | 0.7891607921 |
| 25 | summary | The value of `metrics.train.brier` is 0.01036 . | 0.01036 | ratio | metrics |  | eq | `[[art:d56a10b2:metrics.train.brier]]` | verified | 0.01035868886 |
| 26 | summary | The value of `metrics.train.event_rate` is 0.008525 . | 0.008525 | ratio | metrics |  | eq | `[[art:b9ef3327:metrics.train.event_rate]]` | verified | 0.008524699414 |
| 27 | summary | The value of `metrics.train.gini` is 0.5783 . | 0.5783 | ratio | metrics |  | eq | `[[art:d618ff0f:metrics.train.gini]]` | verified | 0.5783215843 |
| 28 | summary | The value of `metrics.train.ks` is 0.4542 . | 0.4542 | ratio | metrics |  | eq | `[[art:e8d4ae61:metrics.train.ks]]` | verified | 0.4541800929 |
| 29 | summary | The value of `metrics.train.logloss` is 0.06297 . | 0.06297 | ratio | metrics |  | eq | `[[art:2bff29d3:metrics.train.logloss]]` | verified | 0.06296558061 |
| 30 | summary | The value of `metrics.train.mean_predicted` is 0.03925 . | 0.03925 | ratio | metrics |  | eq | `[[art:68f41b88:metrics.train.mean_predicted]]` | verified | 0.03925176105 |
| 31 | summary | The value of `metrics.train.n` is 36013 . | 36013 | ratio | metrics |  | eq | `[[art:6fdfeabb:metrics.train.n]]` | verified | 36013 |
| 32 | summary | The value of `metrics.vintage_holdout.auc` is 0.7743 . | 0.7743 | ratio | metrics |  | eq | `[[art:25db8aa3:metrics.vintage_holdout.auc]]` | verified | 0.7742985165 |
| 33 | summary | The value of `metrics.vintage_holdout.brier` is 0.006101 . | 0.006101 | ratio | metrics |  | eq | `[[art:55737812:metrics.vintage_holdout.brier]]` | verified | 0.006100676477 |
| 34 | summary | The value of `metrics.vintage_holdout.event_rate` is 0.00481… | 0.004817 | ratio | metrics |  | eq | `[[art:e3590a16:metrics.vintage_holdout.event_rate]]` | verified | 0.004817105386 |
| 35 | summary | The value of `metrics.vintage_holdout.gini` is 0.5486 . | 0.5486 | ratio | metrics |  | eq | `[[art:eff9b345:metrics.vintage_holdout.gini]]` | verified | 0.5485970331 |
| 36 | summary | The value of `metrics.vintage_holdout.ks` is 0.4531 . | 0.4531 | ratio | metrics |  | eq | `[[art:a2ee5005:metrics.vintage_holdout.ks]]` | verified | 0.4530637203 |
| 37 | summary | The value of `metrics.vintage_holdout.logloss` is 0.04161 . | 0.04161 | ratio | metrics |  | eq | `[[art:9f19871a:metrics.vintage_holdout.logloss]]` | verified | 0.04161346969 |
| 38 | summary | The value of `metrics.vintage_holdout.mean_predicted` is 0.0… | 0.02582 | ratio | metrics |  | eq | `[[art:348107ae:metrics.vintage_holdout.mean_predicted]]` | verified | 0.02582080379 |
| 39 | summary | The value of `metrics.vintage_holdout.n` is 32177 . | 32177 | ratio | metrics |  | eq | `[[art:37a92951:metrics.vintage_holdout.n]]` | verified | 32177 |
| 40 | summary | The value of `profile.test.n` is 15382 . | 15382 | ratio | profile |  | eq | `[[art:e3abc1b8:profile.test.n]]` | verified | 15382 |
| 41 | summary | The value of `profile.train.n` is 36013 . | 36013 | ratio | profile |  | eq | `[[art:c5ebd9c9:profile.train.n]]` | verified | 36013 |
| 42 | summary | The value of `psi.max` is 0.06189 . | 0.06189 | ratio | psi |  | eq | `[[art:c2e8c8fd:psi.max]]` | verified | 0.06188985797 |
| 43 | summary | The value of `runtime.max_seconds` is 300 . | 300 | ratio | runtime |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 44 | summary | The value of `threshold.package.auc.test.min` is 0.65 . | 0.65 | ratio | threshold |  | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 45 | summary | The value of `threshold.package.calibration_slope.test.max`… | 1.2 | ratio | threshold |  | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 46 | summary | The value of `threshold.package.calibration_slope.test.min`… | 0.8 | ratio | threshold |  | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 47 | summary | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 48 | summary | The value of `vif.max` is 4.976 . | 4.976 | ratio | vif |  | eq | `[[art:f9e0db60:vif.max]]` | verified | 4.975500767 |
| 49 | conceptual_soundness | The value of `ablation.baseline_auc` is 0.7673 . | 0.7673 | ratio | ablation |  | eq | `[[art:54367df6:ablation.baseline_auc]]` | verified | 0.7672992275 |
| 50 | conceptual_soundness | The value of `ablation.burnout.delta_auc` is -0.0001876 . | -0.0001876 | ratio | ablation |  | eq | `[[art:3cba039b:ablation.burnout.delta_auc]]` | verified | -0.0001876329287 |
| 51 | conceptual_soundness | The value of `ablation.credit_score.delta_auc` is -0.01474 . | -0.01474 | ratio | ablation |  | eq | `[[art:9bdeb0df:ablation.credit_score.delta_auc]]` | verified | -0.0147431913 |
| 52 | conceptual_soundness | The value of `ablation.incentive.delta_auc` is -0.04117 . | -0.04117 | ratio | ablation |  | eq | `[[art:78108590:ablation.incentive.delta_auc]]` | verified | -0.0411745927 |
| 53 | conceptual_soundness | The value of `ablation.loan_age.delta_auc` is 0.0008166 . | 0.0008166 | ratio | ablation |  | eq | `[[art:be669163:ablation.loan_age.delta_auc]]` | verified | 0.0008165996474 |
| 54 | conceptual_soundness | The value of `ablation.note_rate.delta_auc` is -0.002585 . | -0.002585 | ratio | ablation |  | eq | `[[art:14558b82:ablation.note_rate.delta_auc]]` | verified | -0.002585106068 |
| 55 | conceptual_soundness | The value of `ablation.orig_ltv.delta_auc` is -0.002294 . | -0.002294 | ratio | ablation |  | eq | `[[art:57ea66c5:ablation.orig_ltv.delta_auc]]` | verified | -0.002294407165 |
| 56 | conceptual_soundness | The value of `ablation.orig_upb_log.delta_auc` is -0.01927 . | -0.01927 | ratio | ablation |  | eq | `[[art:0ddb11a9:ablation.orig_upb_log.delta_auc]]` | verified | -0.01926646624 |
| 57 | conceptual_soundness | The value of `ablation.sato.delta_auc` is 0.0005201 . | 0.0005201 | ratio | ablation |  | eq | `[[art:57703504:ablation.sato.delta_auc]]` | verified | 0.0005200867657 |
| 58 | conceptual_soundness | The value of `ablation.season_cos.delta_auc` is -0.0004826 . | -0.0004826 | ratio | ablation |  | eq | `[[art:a288439d:ablation.season_cos.delta_auc]]` | verified | -0.00048256018 |
| 59 | conceptual_soundness | The value of `ablation.season_sin.delta_auc` is -0.0003885 . | -0.0003885 | ratio | ablation |  | eq | `[[art:e54c8581:ablation.season_sin.delta_auc]]` | verified | -0.0003884794439 |
| 60 | conceptual_soundness | The value of `challenger.auc` is 0.7337 . | 0.7337 | ratio | challenger |  | eq | `[[art:705b66f0:challenger.auc]]` | verified | 0.7337079121 |
| 61 | conceptual_soundness | The value of `challenger.brier` is 0.00863 . | 0.00863 | ratio | challenger |  | eq | `[[art:85a89ef9:challenger.brier]]` | verified | 0.008629514666 |
| 62 | conceptual_soundness | The value of `challenger.delta_auc` is -0.04213 . | -0.04213 | ratio | challenger |  | eq | `[[art:1e990f53:challenger.delta_auc]]` | verified | -0.04212940647 |
| 63 | conceptual_soundness | The value of `metrics.test.auc` is 0.7758 . | 0.7758 | ratio | metrics |  | eq | `[[art:2f4cab3e:metrics.test.auc]]` | verified | 0.7758373186 |
| 64 | conceptual_soundness | The value of `metrics.test.brier` is 0.009864 . | 0.009864 | ratio | metrics |  | eq | `[[art:1e4aab51:metrics.test.brier]]` | verified | 0.009863834665 |
| 65 | conceptual_soundness | The value of `sign_check.burnout.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:56826e40:sign_check.burnout.agrees]]` | verified | 0 |
| 66 | conceptual_soundness | The value of `sign_check.burnout.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:dcfb2de4:sign_check.burnout.coef_sign]]` | verified | -1 |
| 67 | conceptual_soundness | The value of `sign_check.burnout.univariate_direction` is 1… | 1 | ratio | sign_check |  | eq | `[[art:bfc96bb2:sign_check.burnout.univariate_direction]]` | verified | 1 |
| 68 | conceptual_soundness | The value of `sign_check.credit_score.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:915bf8eb:sign_check.credit_score.agrees]]` | verified | 1 |
| 69 | conceptual_soundness | The value of `sign_check.credit_score.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:1ec1078b:sign_check.credit_score.coef_sign]]` | verified | 1 |
| 70 | conceptual_soundness | The value of `sign_check.credit_score.univariate_direction`… | 1 | ratio | sign_check |  | eq | `[[art:42303896:sign_check.credit_score.univariate_direction]]` | verified | 1 |
| 71 | conceptual_soundness | The value of `sign_check.incentive.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:f7b2338e:sign_check.incentive.agrees]]` | verified | 1 |
| 72 | conceptual_soundness | The value of `sign_check.incentive.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:684cf11a:sign_check.incentive.coef_sign]]` | verified | 1 |
| 73 | conceptual_soundness | The value of `sign_check.incentive.univariate_direction` is… | 1 | ratio | sign_check |  | eq | `[[art:8098d951:sign_check.incentive.univariate_direction]]` | verified | 1 |
| 74 | conceptual_soundness | The value of `sign_check.n_disagreements` is 3 . | 3 | ratio | sign_check |  | eq | `[[art:e223cd4a:sign_check.n_disagreements]]` | verified | 3 |
| 75 | conceptual_soundness | The value of `sign_check.note_rate.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:a453463d:sign_check.note_rate.agrees]]` | verified | 0 |
| 76 | conceptual_soundness | The value of `sign_check.note_rate.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:aecf7ccb:sign_check.note_rate.coef_sign]]` | verified | -1 |
| 77 | conceptual_soundness | The value of `sign_check.note_rate.univariate_direction` is… | 1 | ratio | sign_check |  | eq | `[[art:61f6e1ac:sign_check.note_rate.univariate_direction]]` | verified | 1 |
| 78 | conceptual_soundness | The value of `sign_check.orig_ltv.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:7021aeb0:sign_check.orig_ltv.agrees]]` | verified | 1 |
| 79 | conceptual_soundness | The value of `sign_check.orig_ltv.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:7eec65ec:sign_check.orig_ltv.coef_sign]]` | verified | -1 |
| 80 | conceptual_soundness | The value of `sign_check.orig_ltv.univariate_direction` is -… | -1 | ratio | sign_check |  | eq | `[[art:76dbc708:sign_check.orig_ltv.univariate_direction]]` | verified | -1 |
| 81 | conceptual_soundness | The value of `sign_check.orig_upb_log.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:07a9d3e6:sign_check.orig_upb_log.agrees]]` | verified | 1 |
| 82 | conceptual_soundness | The value of `sign_check.orig_upb_log.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:5aa309fc:sign_check.orig_upb_log.coef_sign]]` | verified | 1 |
| 83 | conceptual_soundness | The value of `sign_check.orig_upb_log.univariate_direction`… | 1 | ratio | sign_check |  | eq | `[[art:b9743ecb:sign_check.orig_upb_log.univariate_direction]]` | verified | 1 |
| 84 | conceptual_soundness | The value of `sign_check.sato.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:b3755963:sign_check.sato.agrees]]` | verified | 0 |
| 85 | conceptual_soundness | The value of `sign_check.sato.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:265915cf:sign_check.sato.coef_sign]]` | verified | -1 |
| 86 | conceptual_soundness | The value of `sign_check.sato.univariate_direction` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:c08233a6:sign_check.sato.univariate_direction]]` | verified | 1 |
| 87 | conceptual_soundness | The value of `sign_check.season_cos.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:7f18ddf7:sign_check.season_cos.agrees]]` | verified | 1 |
| 88 | conceptual_soundness | The value of `sign_check.season_cos.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:7dbb1ffc:sign_check.season_cos.coef_sign]]` | verified | -1 |
| 89 | conceptual_soundness | The value of `sign_check.season_cos.univariate_direction` is… | -1 | ratio | sign_check |  | eq | `[[art:03e931f0:sign_check.season_cos.univariate_direction]]` | verified | -1 |
| 90 | conceptual_soundness | The value of `sign_check.season_sin.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:e110f357:sign_check.season_sin.agrees]]` | verified | 1 |
| 91 | conceptual_soundness | The value of `sign_check.season_sin.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:761188ce:sign_check.season_sin.coef_sign]]` | verified | 1 |
| 92 | conceptual_soundness | The value of `sign_check.season_sin.univariate_direction` is… | 1 | ratio | sign_check |  | eq | `[[art:cae6b096:sign_check.season_sin.univariate_direction]]` | verified | 1 |
| 93 | conceptual_soundness | The value of `threshold.E1.delta_auc` is 0.03 . | 0.03 | ratio | threshold |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 94 | data_integrity | The value of `csi.burnout` is 0.0001326 . | 0.0001326 | ratio | csi |  | eq | `[[art:640f9435:csi.burnout]]` | verified | 0.0001325955583 |
| 95 | data_integrity | The value of `csi.credit_score` is 0.007707 . | 0.007707 | ratio | csi |  | eq | `[[art:6653968a:csi.credit_score]]` | verified | 0.007706951731 |
| 96 | data_integrity | The value of `csi.incentive` is 0.005686 . | 0.005686 | ratio | csi |  | eq | `[[art:3bfa986b:csi.incentive]]` | verified | 0.005685694124 |
| 97 | data_integrity | The value of `csi.loan_age` is 0 . | 0 | ratio | csi |  | eq | `[[art:df52c920:csi.loan_age]]` | verified | 0 |
| 98 | data_integrity | The value of `csi.max` is 0.03331 . | 0.03331 | ratio | csi |  | eq | `[[art:a8ca288d:csi.max]]` | verified | 0.03331391493 |
| 99 | data_integrity | The value of `csi.note_rate` is 0.01372 . | 0.01372 | ratio | csi |  | eq | `[[art:e06d8658:csi.note_rate]]` | verified | 0.01371659455 |
| 100 | data_integrity | The value of `csi.orig_ltv` is 0.03331 . | 0.03331 | ratio | csi |  | eq | `[[art:7a941368:csi.orig_ltv]]` | verified | 0.03331391493 |
| 101 | data_integrity | The value of `csi.orig_upb_log` is 0.002863 . | 0.002863 | ratio | csi |  | eq | `[[art:bbbec9d2:csi.orig_upb_log]]` | verified | 0.002863276289 |
| 102 | data_integrity | The value of `csi.sato` is 0.0009305 . | 0.0009305 | ratio | csi |  | eq | `[[art:c9bad372:csi.sato]]` | verified | 0.0009304918233 |
| 103 | data_integrity | The value of `csi.season_cos` is 0.0005034 . | 0.0005034 | ratio | csi |  | eq | `[[art:78d740c8:csi.season_cos]]` | verified | 0.0005033620785 |
| 104 | data_integrity | The value of `csi.season_sin` is 0.0000694 . | 6.94e-05 | ratio | csi |  | eq | `[[art:d16ad42f:csi.season_sin]]` | verified | 6.939549558e-05 |
| 105 | data_integrity | The value of `leakage.duplicates.train` is 0 . | 0 | ratio | leakage |  | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 106 | data_integrity | The value of `leakage.name_screen.n_matched` is 0 . | 0 | ratio | leakage |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 107 | data_integrity | The value of `leakage.overlap` is 0 . | 0 | ratio | leakage |  | eq | `[[art:4c9fcd09:leakage.overlap]]` | verified | 0 |
| 108 | data_integrity | The value of `leakage.overlap.features` is 0 . | 0 | ratio | leakage |  | eq | `[[art:0fec8048:leakage.overlap.features]]` | verified | 0 |
| 109 | data_integrity | The value of `leakage.overlap.ids` is 0 . | 0 | ratio | leakage |  | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 110 | data_integrity | The value of `leakage.target_corr.max_single_feature_auc` is… | 0.7239 | ratio | leakage |  | eq | `[[art:1fe630dd:leakage.target_corr.max_single_feature_auc]]` | verified | 0.7238936567 |
| 111 | data_integrity | The value of `leakage.timing.n_flagged` is 0 . | 0 | ratio | leakage |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 112 | data_integrity | The value of `profile.out_of_time.missing.max` is 0 . | 0 | ratio | profile |  | eq | `[[art:4dafce11:profile.out_of_time.missing.max]]` | verified | 0 |
| 113 | data_integrity | The value of `profile.out_of_time.n` is 12257 . | 12257 | ratio | profile |  | eq | `[[art:fa39c5cf:profile.out_of_time.n]]` | verified | 12257 |
| 114 | data_integrity | The value of `profile.test.missing.max` is 0 . | 0 | ratio | profile |  | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 115 | data_integrity | The value of `profile.test.n` is 15382 . | 15382 | ratio | profile |  | eq | `[[art:e3abc1b8:profile.test.n]]` | verified | 15382 |
| 116 | data_integrity | The value of `profile.train.missing.max` is 0 . | 0 | ratio | profile |  | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 117 | data_integrity | The value of `profile.train.n` is 36013 . | 36013 | ratio | profile |  | eq | `[[art:c5ebd9c9:profile.train.n]]` | verified | 36013 |
| 118 | data_integrity | The value of `profile.vintage_holdout.missing.max` is 0 . | 0 | ratio | profile |  | eq | `[[art:329bb430:profile.vintage_holdout.missing.max]]` | verified | 0 |
| 119 | data_integrity | The value of `profile.vintage_holdout.n` is 32177 . | 32177 | ratio | profile |  | eq | `[[art:426e712a:profile.vintage_holdout.n]]` | verified | 32177 |
| 120 | data_integrity | The value of `psi.burnout` is 0.004614 . | 0.004614 | ratio | psi |  | eq | `[[art:9dc7ecc2:psi.burnout]]` | verified | 0.004614338236 |
| 121 | data_integrity | The value of `psi.credit_score` is 0.06189 . | 0.06189 | ratio | psi |  | eq | `[[art:7e87527c:psi.credit_score]]` | verified | 0.06188985797 |
| 122 | data_integrity | The value of `psi.incentive` is 0.0009923 . | 0.0009923 | ratio | psi |  | eq | `[[art:2da5570f:psi.incentive]]` | verified | 0.0009922551416 |
| 123 | data_integrity | The value of `psi.loan_age` is 0.0001994 . | 0.0001994 | ratio | psi |  | eq | `[[art:2202b157:psi.loan_age]]` | verified | 0.0001993816816 |
| 124 | data_integrity | The value of `psi.max` is 0.06189 . | 0.06189 | ratio | psi |  | eq | `[[art:c2e8c8fd:psi.max]]` | verified | 0.06188985797 |
| 125 | data_integrity | The value of `psi.note_rate` is 0.01371 . | 0.01371 | ratio | psi |  | eq | `[[art:ecc6adf3:psi.note_rate]]` | verified | 0.01370911382 |
| 126 | data_integrity | The value of `psi.orig_ltv` is 0.03617 . | 0.03617 | ratio | psi |  | eq | `[[art:cd1ff136:psi.orig_ltv]]` | verified | 0.03617297258 |
| 127 | data_integrity | The value of `psi.orig_upb_log` is 0.04817 . | 0.04817 | ratio | psi |  | eq | `[[art:55030a3b:psi.orig_upb_log]]` | verified | 0.04817081196 |
| 128 | data_integrity | The value of `psi.out_of_time.burnout` is 2.945 . | 2.945 | ratio | psi |  | eq | `[[art:7b0bbebb:psi.out_of_time.burnout]]` | verified | 2.944521522 |
| 129 | data_integrity | The value of `psi.out_of_time.credit_score` is 0.05988 . | 0.05988 | ratio | psi |  | eq | `[[art:d7249e47:psi.out_of_time.credit_score]]` | verified | 0.05987964443 |
| 130 | data_integrity | The value of `psi.out_of_time.incentive` is 0.4958 . | 0.4958 | ratio | psi |  | eq | `[[art:42076ed1:psi.out_of_time.incentive]]` | verified | 0.4958065489 |
| 131 | data_integrity | The value of `psi.out_of_time.loan_age` is 2.484 . | 2.484 | ratio | psi |  | eq | `[[art:d6eaaaf5:psi.out_of_time.loan_age]]` | verified | 2.483993033 |
| 132 | data_integrity | The value of `psi.out_of_time.note_rate` is 0.6977 . | 0.6977 | ratio | psi |  | eq | `[[art:cabd371d:psi.out_of_time.note_rate]]` | verified | 0.6976589281 |
| 133 | data_integrity | The value of `psi.out_of_time.orig_ltv` is 0.04301 . | 0.04301 | ratio | psi |  | eq | `[[art:3eee5db4:psi.out_of_time.orig_ltv]]` | verified | 0.04300793312 |
| 134 | data_integrity | The value of `psi.out_of_time.orig_upb_log` is 0.07136 . | 0.07136 | ratio | psi |  | eq | `[[art:ac349b67:psi.out_of_time.orig_upb_log]]` | verified | 0.07136421414 |
| 135 | data_integrity | The value of `psi.out_of_time.sato` is 0.01299 . | 0.01299 | ratio | psi |  | eq | `[[art:c2233ce6:psi.out_of_time.sato]]` | verified | 0.01298850667 |
| 136 | data_integrity | The value of `psi.out_of_time.season_cos` is 0.007524 . | 0.007524 | ratio | psi |  | eq | `[[art:25cf6b85:psi.out_of_time.season_cos]]` | verified | 0.00752368457 |
| 137 | data_integrity | The value of `psi.out_of_time.season_sin` is 0.02789 . | 0.02789 | ratio | psi |  | eq | `[[art:144e1bd9:psi.out_of_time.season_sin]]` | verified | 0.02788988464 |
| 138 | data_integrity | The value of `psi.out_of_time.y_score` is 0.6985 . | 0.6985 | ratio | psi |  | eq | `[[art:6f080528:psi.out_of_time.y_score]]` | verified | 0.6984990823 |
| 139 | data_integrity | The value of `psi.sato` is 0.02773 . | 0.02773 | ratio | psi |  | eq | `[[art:584da64f:psi.sato]]` | verified | 0.02772829856 |
| 140 | data_integrity | The value of `psi.season_cos` is 0.0000179 . | 1.79e-05 | ratio | psi |  | eq | `[[art:addec503:psi.season_cos]]` | verified | 1.790085913e-05 |
| 141 | data_integrity | The value of `psi.season_sin` is 0.000002939 . | 2.939e-06 | ratio | psi |  | eq | `[[art:4d2ed98d:psi.season_sin]]` | verified | 2.939045338e-06 |
| 142 | data_integrity | The value of `psi.vintage_holdout.burnout` is 0.04749 . | 0.04749 | ratio | psi |  | eq | `[[art:e29067e6:psi.vintage_holdout.burnout]]` | verified | 0.04749372789 |
| 143 | data_integrity | The value of `psi.vintage_holdout.credit_score` is 0.03996 . | 0.03996 | ratio | psi |  | eq | `[[art:3498d307:psi.vintage_holdout.credit_score]]` | verified | 0.03995819732 |
| 144 | data_integrity | The value of `psi.vintage_holdout.incentive` is 0.4475 . | 0.4475 | ratio | psi |  | eq | `[[art:5e61b6f9:psi.vintage_holdout.incentive]]` | verified | 0.4475226601 |
| 145 | data_integrity | The value of `psi.vintage_holdout.loan_age` is 0.07112 . | 0.07112 | ratio | psi |  | eq | `[[art:6d92c48b:psi.vintage_holdout.loan_age]]` | verified | 0.07111526296 |
| 146 | data_integrity | The value of `psi.vintage_holdout.note_rate` is 0.6088 . | 0.6088 | ratio | psi |  | eq | `[[art:f281f8a7:psi.vintage_holdout.note_rate]]` | verified | 0.608822927 |
| 147 | data_integrity | The value of `psi.vintage_holdout.orig_ltv` is 0.02942 . | 0.02942 | ratio | psi |  | eq | `[[art:d07cfb7d:psi.vintage_holdout.orig_ltv]]` | verified | 0.0294150369 |
| 148 | data_integrity | The value of `psi.vintage_holdout.orig_upb_log` is 0.0404 . | 0.0404 | ratio | psi |  | eq | `[[art:77ec758a:psi.vintage_holdout.orig_upb_log]]` | verified | 0.04039645306 |
| 149 | data_integrity | The value of `psi.vintage_holdout.sato` is 0.02989 . | 0.02989 | ratio | psi |  | eq | `[[art:eea64c25:psi.vintage_holdout.sato]]` | verified | 0.02989256711 |
| 150 | data_integrity | The value of `psi.vintage_holdout.season_cos` is 0.001288 . | 0.001288 | ratio | psi |  | eq | `[[art:9fe842a8:psi.vintage_holdout.season_cos]]` | verified | 0.0012879007 |
| 151 | data_integrity | The value of `psi.vintage_holdout.season_sin` is 0.0007309 . | 0.0007309 | ratio | psi |  | eq | `[[art:b0dc9745:psi.vintage_holdout.season_sin]]` | verified | 0.0007309374015 |
| 152 | data_integrity | The value of `psi.vintage_holdout.y_score` is 0.1604 . | 0.1604 | ratio | psi |  | eq | `[[art:c71062d6:psi.vintage_holdout.y_score]]` | verified | 0.1603916415 |
| 153 | data_integrity | The value of `psi.y_score` is 0.001869 . | 0.001869 | ratio | psi |  | eq | `[[art:aa10164c:psi.y_score]]` | verified | 0.001868586849 |
| 154 | data_integrity | The value of `threshold.D1.missing_gap` is 0.1 . | 0.1 | ratio | threshold |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 155 | data_integrity | The value of `threshold.L1.single_feature_auc` is 0.9 . | 0.9 | ratio | threshold |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 156 | data_integrity | The value of `threshold.L2.overlap` is 0.005 . | 0.005 | ratio | threshold |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 157 | data_integrity | The value of `threshold.L2.overlap.features_effective` is 0.… | 0.005 | ratio | threshold |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 158 | data_integrity | The value of `threshold.S1.psi` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 159 | data_integrity | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 160 | outcomes | The value of `calibration.mean_rel_gap.out_of_time` is 3.342… | 3.342 | ratio | calibration |  | eq | `[[art:5b8375ec:calibration.mean_rel_gap.out_of_time]]` | verified | 3.3416259 |
| 161 | outcomes | The value of `calibration.mean_rel_gap.test` is 3.716 . | 3.716 | ratio | calibration |  | eq | `[[art:15d5555b:calibration.mean_rel_gap.test]]` | verified | 3.716396464 |
| 162 | outcomes | The value of `calibration.mean_rel_gap.train` is 3.604 . | 3.604 | ratio | calibration |  | eq | `[[art:324eb124:calibration.mean_rel_gap.train]]` | verified | 3.604474497 |
| 163 | outcomes | The value of `calibration.mean_rel_gap.vintage_holdout` is 4… | 4.36 | ratio | calibration |  | eq | `[[art:a691b5ed:calibration.mean_rel_gap.vintage_holdout]]` | verified | 4.360232281 |
| 164 | outcomes | The value of `calibration_intercept.out_of_time` is -1.497 . | -1.497 | ratio | calibration_intercept |  | eq | `[[art:db324216:calibration_intercept.out_of_time]]` | verified | -1.496633503 |
| 165 | outcomes | The value of `calibration_intercept.test` is -1.748 . | -1.748 | ratio | calibration_intercept |  | eq | `[[art:257fb817:calibration_intercept.test]]` | verified | -1.747805271 |
| 166 | outcomes | The value of `calibration_intercept.train` is -1.566 . | -1.566 | ratio | calibration_intercept |  | eq | `[[art:57309d7d:calibration_intercept.train]]` | verified | -1.566304198 |
| 167 | outcomes | The value of `calibration_intercept.vintage_holdout` is -2.1… | -2.176 | ratio | calibration_intercept |  | eq | `[[art:6f00dbc2:calibration_intercept.vintage_holdout]]` | verified | -2.175702334 |
| 168 | outcomes | The value of `calibration_slope.out_of_time` is 1.066 . | 1.066 | ratio | calibration_slope |  | eq | `[[art:ea7d5696:calibration_slope.out_of_time]]` | verified | 1.066358183 |
| 169 | outcomes | The value of `calibration_slope.test` is 0.9537 . | 0.9537 | ratio | calibration_slope |  | eq | `[[art:f8ef2beb:calibration_slope.test]]` | verified | 0.9536630305 |
| 170 | outcomes | The value of `calibration_slope.train` is 1.015 . | 1.015 | ratio | calibration_slope |  | eq | `[[art:ffabb935:calibration_slope.train]]` | verified | 1.014728573 |
| 171 | outcomes | The value of `calibration_slope.vintage_holdout` is 0.8562 . | 0.8562 | ratio | calibration_slope |  | eq | `[[art:010c0ec4:calibration_slope.vintage_holdout]]` | verified | 0.8561504457 |
| 172 | outcomes | The value of `cpr.out_of_time.mae` is 0.318 . | 0.318 | ratio | cpr |  | eq | `[[art:8ac7bfbc:cpr.out_of_time.mae]]` | verified | 0.3179874584 |
| 173 | outcomes | The value of `cpr.test.mae` is 0.222 . | 0.222 | ratio | cpr |  | eq | `[[art:b7587aed:cpr.test.mae]]` | verified | 0.222029929 |
| 174 | outcomes | The value of `cpr.train.mae` is 0.224 . | 0.224 | ratio | cpr |  | eq | `[[art:8d8e2c42:cpr.train.mae]]` | verified | 0.2239621374 |
| 175 | outcomes | The value of `cpr.vintage_holdout.mae` is 0.172 . | 0.172 | ratio | cpr |  | eq | `[[art:2d48e163:cpr.vintage_holdout.mae]]` | verified | 0.1720007526 |
| 176 | outcomes | The value of `deciles.out_of_time.top2_capture` is 0.5909 . | 0.5909 | ratio | deciles |  | eq | `[[art:95c24730:deciles.out_of_time.top2_capture]]` | verified | 0.5909090909 |
| 177 | outcomes | The value of `deciles.test.top2_capture` is 0.5806 . | 0.5806 | ratio | deciles |  | eq | `[[art:43c4adc5:deciles.test.top2_capture]]` | verified | 0.5806451613 |
| 178 | outcomes | The value of `deciles.train.top2_capture` is 0.6059 . | 0.6059 | ratio | deciles |  | eq | `[[art:eb38637b:deciles.train.top2_capture]]` | verified | 0.6058631922 |
| 179 | outcomes | The value of `deciles.vintage_holdout.top2_capture` is 0.593… | 0.5935 | ratio | deciles |  | eq | `[[art:4a376307:deciles.vintage_holdout.top2_capture]]` | verified | 0.5935483871 |
| 180 | outcomes | The value of `metrics.out_of_time.auc` is 0.7898 . | 0.7898 | ratio | metrics |  | eq | `[[art:aa836722:metrics.out_of_time.auc]]` | verified | 0.7897867937 |
| 181 | outcomes | The value of `metrics.out_of_time.brier` is 0.02402 . | 0.02402 | ratio | metrics |  | eq | `[[art:a8a8d3a5:metrics.out_of_time.brier]]` | verified | 0.02402096444 |
| 182 | outcomes | The value of `metrics.out_of_time.event_rate` is 0.01795 . | 0.01795 | ratio | metrics |  | eq | `[[art:83ccf5c0:metrics.out_of_time.event_rate]]` | verified | 0.01794892714 |
| 183 | outcomes | The value of `metrics.out_of_time.gini` is 0.5796 . | 0.5796 | ratio | metrics |  | eq | `[[art:3dc07327:metrics.out_of_time.gini]]` | verified | 0.5795735875 |
| 184 | outcomes | The value of `metrics.out_of_time.ks` is 0.4368 . | 0.4368 | ratio | metrics |  | eq | `[[art:00bf02ed:metrics.out_of_time.ks]]` | verified | 0.43678733 |
| 185 | outcomes | The value of `metrics.out_of_time.logloss` is 0.1174 . | 0.1174 | ratio | metrics |  | eq | `[[art:5198f968:metrics.out_of_time.logloss]]` | verified | 0.1173954835 |
| 186 | outcomes | The value of `metrics.out_of_time.mean_predicted` is 0.07793… | 0.07793 | ratio | metrics |  | eq | `[[art:921d185b:metrics.out_of_time.mean_predicted]]` | verified | 0.07792752696 |
| 187 | outcomes | The value of `metrics.out_of_time.n` is 12257 . | 12257 | ratio | metrics |  | eq | `[[art:7898809e:metrics.out_of_time.n]]` | verified | 12257 |
| 188 | outcomes | The value of `metrics.test.auc` is 0.7758 . | 0.7758 | ratio | metrics |  | eq | `[[art:2f4cab3e:metrics.test.auc]]` | verified | 0.7758373186 |
| 189 | outcomes | The value of `metrics.test.brier` is 0.009864 . | 0.009864 | ratio | metrics |  | eq | `[[art:1e4aab51:metrics.test.brier]]` | verified | 0.009863834665 |
| 190 | outcomes | The value of `metrics.test.event_rate` is 0.008061 . | 0.008061 | ratio | metrics |  | eq | `[[art:570cc08a:metrics.test.event_rate]]` | verified | 0.008061370433 |
| 191 | outcomes | The value of `metrics.test.gini` is 0.5517 . | 0.5517 | ratio | metrics |  | eq | `[[art:8593585c:metrics.test.gini]]` | verified | 0.5516746371 |
| 192 | outcomes | The value of `metrics.test.ks` is 0.428 . | 0.428 | ratio | metrics |  | eq | `[[art:554f1e19:metrics.test.ks]]` | verified | 0.4280398649 |
| 193 | outcomes | The value of `metrics.test.logloss` is 0.06118 . | 0.06118 | ratio | metrics |  | eq | `[[art:b9424e16:metrics.test.logloss]]` | verified | 0.06118235348 |
| 194 | outcomes | The value of `metrics.test.mean_predicted` is 0.03802 . | 0.03802 | ratio | metrics |  | eq | `[[art:122af437:metrics.test.mean_predicted]]` | verified | 0.038020619 |
| 195 | outcomes | The value of `metrics.test.n` is 15382 . | 15382 | ratio | metrics |  | eq | `[[art:e55953e1:metrics.test.n]]` | verified | 15382 |
| 196 | outcomes | The value of `metrics.train.auc` is 0.7892 . | 0.7892 | ratio | metrics |  | eq | `[[art:39508266:metrics.train.auc]]` | verified | 0.7891607921 |
| 197 | outcomes | The value of `metrics.train.brier` is 0.01036 . | 0.01036 | ratio | metrics |  | eq | `[[art:d56a10b2:metrics.train.brier]]` | verified | 0.01035868886 |
| 198 | outcomes | The value of `metrics.train.event_rate` is 0.008525 . | 0.008525 | ratio | metrics |  | eq | `[[art:b9ef3327:metrics.train.event_rate]]` | verified | 0.008524699414 |
| 199 | outcomes | The value of `metrics.train.gini` is 0.5783 . | 0.5783 | ratio | metrics |  | eq | `[[art:d618ff0f:metrics.train.gini]]` | verified | 0.5783215843 |
| 200 | outcomes | The value of `metrics.train.ks` is 0.4542 . | 0.4542 | ratio | metrics |  | eq | `[[art:e8d4ae61:metrics.train.ks]]` | verified | 0.4541800929 |
| 201 | outcomes | The value of `metrics.train.logloss` is 0.06297 . | 0.06297 | ratio | metrics |  | eq | `[[art:2bff29d3:metrics.train.logloss]]` | verified | 0.06296558061 |
| 202 | outcomes | The value of `metrics.train.mean_predicted` is 0.03925 . | 0.03925 | ratio | metrics |  | eq | `[[art:68f41b88:metrics.train.mean_predicted]]` | verified | 0.03925176105 |
| 203 | outcomes | The value of `metrics.train.n` is 36013 . | 36013 | ratio | metrics |  | eq | `[[art:6fdfeabb:metrics.train.n]]` | verified | 36013 |
| 204 | outcomes | The value of `metrics.vintage_holdout.auc` is 0.7743 . | 0.7743 | ratio | metrics |  | eq | `[[art:25db8aa3:metrics.vintage_holdout.auc]]` | verified | 0.7742985165 |
| 205 | outcomes | The value of `metrics.vintage_holdout.brier` is 0.006101 . | 0.006101 | ratio | metrics |  | eq | `[[art:55737812:metrics.vintage_holdout.brier]]` | verified | 0.006100676477 |
| 206 | outcomes | The value of `metrics.vintage_holdout.event_rate` is 0.00481… | 0.004817 | ratio | metrics |  | eq | `[[art:e3590a16:metrics.vintage_holdout.event_rate]]` | verified | 0.004817105386 |
| 207 | outcomes | The value of `metrics.vintage_holdout.gini` is 0.5486 . | 0.5486 | ratio | metrics |  | eq | `[[art:eff9b345:metrics.vintage_holdout.gini]]` | verified | 0.5485970331 |
| 208 | outcomes | The value of `metrics.vintage_holdout.ks` is 0.4531 . | 0.4531 | ratio | metrics |  | eq | `[[art:a2ee5005:metrics.vintage_holdout.ks]]` | verified | 0.4530637203 |
| 209 | outcomes | The value of `metrics.vintage_holdout.logloss` is 0.04161 . | 0.04161 | ratio | metrics |  | eq | `[[art:9f19871a:metrics.vintage_holdout.logloss]]` | verified | 0.04161346969 |
| 210 | outcomes | The value of `metrics.vintage_holdout.mean_predicted` is 0.0… | 0.02582 | ratio | metrics |  | eq | `[[art:348107ae:metrics.vintage_holdout.mean_predicted]]` | verified | 0.02582080379 |
| 211 | outcomes | The value of `metrics.vintage_holdout.n` is 32177 . | 32177 | ratio | metrics |  | eq | `[[art:37a92951:metrics.vintage_holdout.n]]` | verified | 32177 |
| 212 | outcomes | The value of `psi.burnout` is 0.004614 . | 0.004614 | ratio | psi |  | eq | `[[art:9dc7ecc2:psi.burnout]]` | verified | 0.004614338236 |
| 213 | outcomes | The value of `psi.credit_score` is 0.06189 . | 0.06189 | ratio | psi |  | eq | `[[art:7e87527c:psi.credit_score]]` | verified | 0.06188985797 |
| 214 | outcomes | The value of `psi.incentive` is 0.0009923 . | 0.0009923 | ratio | psi |  | eq | `[[art:2da5570f:psi.incentive]]` | verified | 0.0009922551416 |
| 215 | outcomes | The value of `psi.loan_age` is 0.0001994 . | 0.0001994 | ratio | psi |  | eq | `[[art:2202b157:psi.loan_age]]` | verified | 0.0001993816816 |
| 216 | outcomes | The value of `psi.max` is 0.06189 . | 0.06189 | ratio | psi |  | eq | `[[art:c2e8c8fd:psi.max]]` | verified | 0.06188985797 |
| 217 | outcomes | The value of `psi.note_rate` is 0.01371 . | 0.01371 | ratio | psi |  | eq | `[[art:ecc6adf3:psi.note_rate]]` | verified | 0.01370911382 |
| 218 | outcomes | The value of `psi.orig_ltv` is 0.03617 . | 0.03617 | ratio | psi |  | eq | `[[art:cd1ff136:psi.orig_ltv]]` | verified | 0.03617297258 |
| 219 | outcomes | The value of `psi.orig_upb_log` is 0.04817 . | 0.04817 | ratio | psi |  | eq | `[[art:55030a3b:psi.orig_upb_log]]` | verified | 0.04817081196 |
| 220 | outcomes | The value of `psi.out_of_time.burnout` is 2.945 . | 2.945 | ratio | psi |  | eq | `[[art:7b0bbebb:psi.out_of_time.burnout]]` | verified | 2.944521522 |
| 221 | outcomes | The value of `psi.out_of_time.credit_score` is 0.05988 . | 0.05988 | ratio | psi |  | eq | `[[art:d7249e47:psi.out_of_time.credit_score]]` | verified | 0.05987964443 |
| 222 | outcomes | The value of `psi.out_of_time.incentive` is 0.4958 . | 0.4958 | ratio | psi |  | eq | `[[art:42076ed1:psi.out_of_time.incentive]]` | verified | 0.4958065489 |
| 223 | outcomes | The value of `psi.out_of_time.loan_age` is 2.484 . | 2.484 | ratio | psi |  | eq | `[[art:d6eaaaf5:psi.out_of_time.loan_age]]` | verified | 2.483993033 |
| 224 | outcomes | The value of `psi.out_of_time.note_rate` is 0.6977 . | 0.6977 | ratio | psi |  | eq | `[[art:cabd371d:psi.out_of_time.note_rate]]` | verified | 0.6976589281 |
| 225 | outcomes | The value of `psi.out_of_time.orig_ltv` is 0.04301 . | 0.04301 | ratio | psi |  | eq | `[[art:3eee5db4:psi.out_of_time.orig_ltv]]` | verified | 0.04300793312 |
| 226 | outcomes | The value of `psi.out_of_time.orig_upb_log` is 0.07136 . | 0.07136 | ratio | psi |  | eq | `[[art:ac349b67:psi.out_of_time.orig_upb_log]]` | verified | 0.07136421414 |
| 227 | outcomes | The value of `psi.out_of_time.sato` is 0.01299 . | 0.01299 | ratio | psi |  | eq | `[[art:c2233ce6:psi.out_of_time.sato]]` | verified | 0.01298850667 |
| 228 | outcomes | The value of `psi.out_of_time.season_cos` is 0.007524 . | 0.007524 | ratio | psi |  | eq | `[[art:25cf6b85:psi.out_of_time.season_cos]]` | verified | 0.00752368457 |
| 229 | outcomes | The value of `psi.out_of_time.season_sin` is 0.02789 . | 0.02789 | ratio | psi |  | eq | `[[art:144e1bd9:psi.out_of_time.season_sin]]` | verified | 0.02788988464 |
| 230 | outcomes | The value of `psi.out_of_time.y_score` is 0.6985 . | 0.6985 | ratio | psi |  | eq | `[[art:6f080528:psi.out_of_time.y_score]]` | verified | 0.6984990823 |
| 231 | outcomes | The value of `psi.sato` is 0.02773 . | 0.02773 | ratio | psi |  | eq | `[[art:584da64f:psi.sato]]` | verified | 0.02772829856 |
| 232 | outcomes | The value of `psi.season_cos` is 0.0000179 . | 1.79e-05 | ratio | psi |  | eq | `[[art:addec503:psi.season_cos]]` | verified | 1.790085913e-05 |
| 233 | outcomes | The value of `psi.season_sin` is 0.000002939 . | 2.939e-06 | ratio | psi |  | eq | `[[art:4d2ed98d:psi.season_sin]]` | verified | 2.939045338e-06 |
| 234 | outcomes | The value of `psi.vintage_holdout.burnout` is 0.04749 . | 0.04749 | ratio | psi |  | eq | `[[art:e29067e6:psi.vintage_holdout.burnout]]` | verified | 0.04749372789 |
| 235 | outcomes | The value of `psi.vintage_holdout.credit_score` is 0.03996 . | 0.03996 | ratio | psi |  | eq | `[[art:3498d307:psi.vintage_holdout.credit_score]]` | verified | 0.03995819732 |
| 236 | outcomes | The value of `psi.vintage_holdout.incentive` is 0.4475 . | 0.4475 | ratio | psi |  | eq | `[[art:5e61b6f9:psi.vintage_holdout.incentive]]` | verified | 0.4475226601 |
| 237 | outcomes | The value of `psi.vintage_holdout.loan_age` is 0.07112 . | 0.07112 | ratio | psi |  | eq | `[[art:6d92c48b:psi.vintage_holdout.loan_age]]` | verified | 0.07111526296 |
| 238 | outcomes | The value of `psi.vintage_holdout.note_rate` is 0.6088 . | 0.6088 | ratio | psi |  | eq | `[[art:f281f8a7:psi.vintage_holdout.note_rate]]` | verified | 0.608822927 |
| 239 | outcomes | The value of `psi.vintage_holdout.orig_ltv` is 0.02942 . | 0.02942 | ratio | psi |  | eq | `[[art:d07cfb7d:psi.vintage_holdout.orig_ltv]]` | verified | 0.0294150369 |
| 240 | outcomes | The value of `psi.vintage_holdout.orig_upb_log` is 0.0404 . | 0.0404 | ratio | psi |  | eq | `[[art:77ec758a:psi.vintage_holdout.orig_upb_log]]` | verified | 0.04039645306 |
| 241 | outcomes | The value of `psi.vintage_holdout.sato` is 0.02989 . | 0.02989 | ratio | psi |  | eq | `[[art:eea64c25:psi.vintage_holdout.sato]]` | verified | 0.02989256711 |
| 242 | outcomes | The value of `psi.vintage_holdout.season_cos` is 0.001288 . | 0.001288 | ratio | psi |  | eq | `[[art:9fe842a8:psi.vintage_holdout.season_cos]]` | verified | 0.0012879007 |
| 243 | outcomes | The value of `psi.vintage_holdout.season_sin` is 0.0007309 . | 0.0007309 | ratio | psi |  | eq | `[[art:b0dc9745:psi.vintage_holdout.season_sin]]` | verified | 0.0007309374015 |
| 244 | outcomes | The value of `psi.vintage_holdout.y_score` is 0.1604 . | 0.1604 | ratio | psi |  | eq | `[[art:c71062d6:psi.vintage_holdout.y_score]]` | verified | 0.1603916415 |
| 245 | outcomes | The value of `psi.y_score` is 0.001869 . | 0.001869 | ratio | psi |  | eq | `[[art:aa10164c:psi.y_score]]` | verified | 0.001868586849 |
| 246 | outcomes | The value of `threshold.C1.calibration_slope.max` is 1.2 . | 1.2 | ratio | threshold |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 247 | outcomes | The value of `threshold.C1.calibration_slope.min` is 0.8 . | 0.8 | ratio | threshold |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 248 | outcomes | The value of `threshold.C1.mean_ratio_rel` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 249 | outcomes | The value of `threshold.D1.missing_gap` is 0.1 . | 0.1 | ratio | threshold |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 250 | outcomes | The value of `threshold.E1.delta_auc` is 0.03 . | 0.03 | ratio | threshold |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 251 | outcomes | The value of `threshold.L1.single_feature_auc` is 0.9 . | 0.9 | ratio | threshold |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 252 | outcomes | The value of `threshold.L2.overlap` is 0.005 . | 0.005 | ratio | threshold |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 253 | outcomes | The value of `threshold.L2.overlap.features_effective` is 0.… | 0.005 | ratio | threshold |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 254 | outcomes | The value of `threshold.M1.condition_number` is 30 . | 30 | ratio | threshold |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 255 | outcomes | The value of `threshold.M1.vif` is 10 . | 10 | ratio | threshold |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 256 | outcomes | The value of `threshold.O1.auc_gap` is 0.08 . | 0.08 | ratio | threshold |  | eq | `[[art:630f28f4:threshold.O1.auc_gap]]` | verified | 0.08 |
| 257 | outcomes | The value of `threshold.O1.holdout_gap` is 0.05 . | 0.05 | ratio | threshold |  | eq | `[[art:90f8b6d9:threshold.O1.holdout_gap]]` | verified | 0.05 |
| 258 | outcomes | The value of `threshold.R1.auc_gap` is 0.1 . | 0.1 | ratio | threshold |  | eq | `[[art:b64213d7:threshold.R1.auc_gap]]` | verified | 0.1 |
| 259 | outcomes | The value of `threshold.R1.sign_flip_coef` is 0.05 . | 0.05 | ratio | threshold |  | eq | `[[art:aca84377:threshold.R1.sign_flip_coef]]` | verified | 0.05 |
| 260 | outcomes | The value of `threshold.R1.sign_flip_z` is 2 . | 2 | ratio | threshold |  | eq | `[[art:2e4428c7:threshold.R1.sign_flip_z]]` | verified | 2 |
| 261 | outcomes | The value of `threshold.S1.psi` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 262 | outcomes | The value of `threshold.package.auc.test.min` is 0.65 . | 0.65 | ratio | threshold |  | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 263 | outcomes | The value of `threshold.package.calibration_slope.test.max`… | 1.2 | ratio | threshold |  | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 264 | outcomes | The value of `threshold.package.calibration_slope.test.min`… | 0.8 | ratio | threshold |  | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 265 | outcomes | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 266 | sensitivity | The value of `condition_number` is 4.943 . | 4.943 | ratio | condition_number |  | eq | `[[art:4f06a3c5:condition_number]]` | verified | 4.942565522 |
| 267 | sensitivity | The value of `scenario.convexity` is -541800 . | -541800 | ratio | scenario |  | eq | `[[art:42ad3e3e:scenario.convexity]]` | verified | -541831.8779 |
| 268 | sensitivity | The value of `scenario.value_change.-100` is -517800 . | -517800 | ratio | scenario |  | eq | `[[art:b3c09ea9:scenario.value_change.-100]]` | verified | -517824.9714 |
| 269 | sensitivity | The value of `scenario.value_change.-200` is -927100 . | -927100 | ratio | scenario |  | eq | `[[art:59e2f8a4:scenario.value_change.-200]]` | verified | -927073.1975 |
| 270 | sensitivity | The value of `scenario.value_change.-300` is -1099000 . | -1099000 | ratio | scenario |  | eq | `[[art:ff90f8c1:scenario.value_change.-300]]` | verified | -1099446.442 |
| 271 | sensitivity | The value of `scenario.value_change.0` is 0 . | 0 | ratio | scenario |  | eq | `[[art:1e1b0b88:scenario.value_change.0]]` | verified | 0 |
| 272 | sensitivity | The value of `scenario.value_change.100` is 352800 . | 352800 | ratio | scenario |  | eq | `[[art:95da798d:scenario.value_change.100]]` | verified | 352845.0358 |
| 273 | sensitivity | The value of `scenario.value_change.200` is 505800 . | 505800 | ratio | scenario |  | eq | `[[art:be13cc25:scenario.value_change.200]]` | verified | 505801.2473 |
| 274 | sensitivity | The value of `scenario.value_change.300` is 557600 . | 557600 | ratio | scenario |  | eq | `[[art:0b43db3b:scenario.value_change.300]]` | verified | 557614.5638 |
| 275 | sensitivity | The value of `stability.burnout.sign_flip` is 0 . | 0 | ratio | stability |  | eq | `[[art:6bc05e82:stability.burnout.sign_flip]]` | verified | 0 |
| 276 | sensitivity | The value of `stability.credit_score.sign_flip` is 0 . | 0 | ratio | stability |  | eq | `[[art:d956c276:stability.credit_score.sign_flip]]` | verified | 0 |
| 277 | sensitivity | The value of `stability.incentive.sign_flip` is 0 . | 0 | ratio | stability |  | eq | `[[art:0cc7a37d:stability.incentive.sign_flip]]` | verified | 0 |
| 278 | sensitivity | The value of `stability.loan_age.sign_flip` is 0 . | 0 | ratio | stability |  | eq | `[[art:b7191217:stability.loan_age.sign_flip]]` | verified | 0 |
| 279 | sensitivity | The value of `stability.note_rate.sign_flip` is 0 . | 0 | ratio | stability |  | eq | `[[art:e7ce4912:stability.note_rate.sign_flip]]` | verified | 0 |
| 280 | sensitivity | The value of `stability.orig_ltv.sign_flip` is 0 . | 0 | ratio | stability |  | eq | `[[art:054d5fab:stability.orig_ltv.sign_flip]]` | verified | 0 |
| 281 | sensitivity | The value of `stability.orig_upb_log.sign_flip` is 0 . | 0 | ratio | stability |  | eq | `[[art:fb1ae6c8:stability.orig_upb_log.sign_flip]]` | verified | 0 |
| 282 | sensitivity | The value of `stability.sato.sign_flip` is 0 . | 0 | ratio | stability |  | eq | `[[art:1f302ccd:stability.sato.sign_flip]]` | verified | 0 |
| 283 | sensitivity | The value of `stability.season_cos.sign_flip` is 0 . | 0 | ratio | stability |  | eq | `[[art:1850e2de:stability.season_cos.sign_flip]]` | verified | 0 |
| 284 | sensitivity | The value of `stability.season_sin.sign_flip` is 0 . | 0 | ratio | stability |  | eq | `[[art:6ba36a3b:stability.season_sin.sign_flip]]` | verified | 0 |
| 285 | sensitivity | The value of `threshold.M1.condition_number` is 30 . | 30 | ratio | threshold |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 286 | sensitivity | The value of `threshold.M1.vif` is 10 . | 10 | ratio | threshold |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 287 | sensitivity | The value of `threshold.R1.auc_gap` is 0.1 . | 0.1 | ratio | threshold |  | eq | `[[art:b64213d7:threshold.R1.auc_gap]]` | verified | 0.1 |
| 288 | sensitivity | The value of `threshold.R1.sign_flip_coef` is 0.05 . | 0.05 | ratio | threshold |  | eq | `[[art:aca84377:threshold.R1.sign_flip_coef]]` | verified | 0.05 |
| 289 | sensitivity | The value of `threshold.R1.sign_flip_z` is 2 . | 2 | ratio | threshold |  | eq | `[[art:2e4428c7:threshold.R1.sign_flip_z]]` | verified | 2 |
| 290 | sensitivity | The value of `vif.burnout` is 3.439 . | 3.439 | ratio | vif |  | eq | `[[art:88879cb2:vif.burnout]]` | verified | 3.439328594 |
| 291 | sensitivity | The value of `vif.credit_score` is 1.008 . | 1.008 | ratio | vif |  | eq | `[[art:f05d536a:vif.credit_score]]` | verified | 1.007978309 |
| 292 | sensitivity | The value of `vif.incentive` is 2.226 . | 2.226 | ratio | vif |  | eq | `[[art:2da1b19c:vif.incentive]]` | verified | 2.22632259 |
| 293 | sensitivity | The value of `vif.loan_age` is 2.929 . | 2.929 | ratio | vif |  | eq | `[[art:5573d536:vif.loan_age]]` | verified | 2.928871763 |
| 294 | sensitivity | The value of `vif.max` is 4.976 . | 4.976 | ratio | vif |  | eq | `[[art:f9e0db60:vif.max]]` | verified | 4.975500767 |
| 295 | sensitivity | The value of `vif.note_rate` is 4.976 . | 4.976 | ratio | vif |  | eq | `[[art:37532fa8:vif.note_rate]]` | verified | 4.975500767 |
| 296 | sensitivity | The value of `vif.orig_ltv` is 1.005 . | 1.005 | ratio | vif |  | eq | `[[art:65b35f3b:vif.orig_ltv]]` | verified | 1.004506143 |
| 297 | sensitivity | The value of `vif.orig_upb_log` is 1.006 . | 1.006 | ratio | vif |  | eq | `[[art:24f8e4d1:vif.orig_upb_log]]` | verified | 1.005846447 |
| 298 | sensitivity | The value of `vif.sato` is 1.713 . | 1.713 | ratio | vif |  | eq | `[[art:a6c55fce:vif.sato]]` | verified | 1.71256814 |
| 299 | sensitivity | The value of `vif.season_cos` is 1.018 . | 1.018 | ratio | vif |  | eq | `[[art:a9cfa7eb:vif.season_cos]]` | verified | 1.017653349 |
| 300 | sensitivity | The value of `vif.season_sin` is 1.004 . | 1.004 | ratio | vif |  | eq | `[[art:669c5fcb:vif.season_sin]]` | verified | 1.004128844 |
| 301 | findings | The value of `calibration.mean_rel_gap.out_of_time` is 3.342… | 3.342 | ratio | calibration |  | eq | `[[art:5b8375ec:calibration.mean_rel_gap.out_of_time]]` | verified | 3.3416259 |
| 302 | findings | The value of `calibration.mean_rel_gap.test` is 3.716 . | 3.716 | ratio | calibration |  | eq | `[[art:15d5555b:calibration.mean_rel_gap.test]]` | verified | 3.716396464 |
| 303 | findings | The value of `calibration.mean_rel_gap.train` is 3.604 . | 3.604 | ratio | calibration |  | eq | `[[art:324eb124:calibration.mean_rel_gap.train]]` | verified | 3.604474497 |
| 304 | findings | The value of `calibration.mean_rel_gap.vintage_holdout` is 4… | 4.36 | ratio | calibration |  | eq | `[[art:a691b5ed:calibration.mean_rel_gap.vintage_holdout]]` | verified | 4.360232281 |
| 305 | findings | The value of `metrics.out_of_time.event_rate` is 0.01795 . | 0.01795 | ratio | metrics |  | eq | `[[art:83ccf5c0:metrics.out_of_time.event_rate]]` | verified | 0.01794892714 |
| 306 | findings | The value of `metrics.out_of_time.mean_predicted` is 0.07793… | 0.07793 | ratio | metrics |  | eq | `[[art:921d185b:metrics.out_of_time.mean_predicted]]` | verified | 0.07792752696 |
| 307 | findings | The value of `metrics.test.event_rate` is 0.008061 . | 0.008061 | ratio | metrics |  | eq | `[[art:570cc08a:metrics.test.event_rate]]` | verified | 0.008061370433 |
| 308 | findings | The value of `metrics.test.mean_predicted` is 0.03802 . | 0.03802 | ratio | metrics |  | eq | `[[art:122af437:metrics.test.mean_predicted]]` | verified | 0.038020619 |
| 309 | findings | The value of `metrics.train.event_rate` is 0.008525 . | 0.008525 | ratio | metrics |  | eq | `[[art:b9ef3327:metrics.train.event_rate]]` | verified | 0.008524699414 |
| 310 | findings | The value of `metrics.train.mean_predicted` is 0.03925 . | 0.03925 | ratio | metrics |  | eq | `[[art:68f41b88:metrics.train.mean_predicted]]` | verified | 0.03925176105 |
| 311 | findings | The value of `metrics.vintage_holdout.event_rate` is 0.00481… | 0.004817 | ratio | metrics |  | eq | `[[art:e3590a16:metrics.vintage_holdout.event_rate]]` | verified | 0.004817105386 |
| 312 | findings | The value of `metrics.vintage_holdout.mean_predicted` is 0.0… | 0.02582 | ratio | metrics |  | eq | `[[art:348107ae:metrics.vintage_holdout.mean_predicted]]` | verified | 0.02582080379 |
| 313 | findings | The value of `sign_check.burnout.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:56826e40:sign_check.burnout.agrees]]` | verified | 0 |
| 314 | findings | The value of `sign_check.burnout.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:dcfb2de4:sign_check.burnout.coef_sign]]` | verified | -1 |
| 315 | findings | The value of `sign_check.burnout.univariate_direction` is 1… | 1 | ratio | sign_check |  | eq | `[[art:bfc96bb2:sign_check.burnout.univariate_direction]]` | verified | 1 |
| 316 | findings | The value of `sign_check.note_rate.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:a453463d:sign_check.note_rate.agrees]]` | verified | 0 |
| 317 | findings | The value of `sign_check.note_rate.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:aecf7ccb:sign_check.note_rate.coef_sign]]` | verified | -1 |
| 318 | findings | The value of `sign_check.note_rate.univariate_direction` is… | 1 | ratio | sign_check |  | eq | `[[art:61f6e1ac:sign_check.note_rate.univariate_direction]]` | verified | 1 |
| 319 | findings | The value of `sign_check.sato.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:b3755963:sign_check.sato.agrees]]` | verified | 0 |
| 320 | findings | The value of `sign_check.sato.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:265915cf:sign_check.sato.coef_sign]]` | verified | -1 |
| 321 | findings | The value of `sign_check.sato.univariate_direction` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:c08233a6:sign_check.sato.univariate_direction]]` | verified | 1 |
| 322 | findings | The value of `threshold.C1.mean_ratio_rel` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 323 | monitoring | The value of `calibration_slope.test` is 0.9537 . | 0.9537 | ratio | calibration_slope |  | eq | `[[art:f8ef2beb:calibration_slope.test]]` | verified | 0.9536630305 |
| 324 | monitoring | The value of `metrics.test.auc` is 0.7758 . | 0.7758 | ratio | metrics |  | eq | `[[art:2f4cab3e:metrics.test.auc]]` | verified | 0.7758373186 |
| 325 | monitoring | The value of `psi.max` is 0.06189 . | 0.06189 | ratio | psi |  | eq | `[[art:c2e8c8fd:psi.max]]` | verified | 0.06188985797 |
| 326 | monitoring | The value of `rule.calibration_first_event_rate` is 0.05 . | 0.05 | ratio | rule |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 327 | monitoring | The value of `threshold.package.auc.test.min` is 0.65 . | 0.65 | ratio | threshold |  | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 328 | monitoring | The value of `threshold.package.calibration_slope.test.max`… | 1.2 | ratio | threshold |  | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 329 | monitoring | The value of `threshold.package.calibration_slope.test.min`… | 0.8 | ratio | threshold |  | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 330 | monitoring | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |

## Appendix B — Artifact index

The store holds 272 artifacts; the 215 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `ablation.baseline_auc` | `54367df6` | scalar | 0.7672992275 | AUC on test of a refit of the champion's functional form on every retained feature, the level each ablation delta is measured from |
| `ablation.burnout.delta_auc` | `3cba039b` | scalar | -0.0001876329287 | change in test AUC when the champion's form is refitted without burnout |
| `ablation.credit_score.delta_auc` | `9bdeb0df` | scalar | -0.0147431913 | change in test AUC when the champion's form is refitted without credit_score |
| `ablation.incentive.delta_auc` | `78108590` | scalar | -0.0411745927 | change in test AUC when the champion's form is refitted without incentive |
| `ablation.loan_age.delta_auc` | `be669163` | scalar | 0.0008165996474 | change in test AUC when the champion's form is refitted without loan_age |
| `ablation.note_rate.delta_auc` | `14558b82` | scalar | -0.002585106068 | change in test AUC when the champion's form is refitted without note_rate |
| `ablation.orig_ltv.delta_auc` | `57ea66c5` | scalar | -0.002294407165 | change in test AUC when the champion's form is refitted without orig_ltv |
| `ablation.orig_upb_log.delta_auc` | `0ddb11a9` | scalar | -0.01926646624 | change in test AUC when the champion's form is refitted without orig_upb_log |
| `ablation.sato.delta_auc` | `57703504` | scalar | 0.0005200867657 | change in test AUC when the champion's form is refitted without sato |
| `ablation.season_cos.delta_auc` | `a288439d` | scalar | -0.00048256018 | change in test AUC when the champion's form is refitted without season_cos |
| `ablation.season_sin.delta_auc` | `e54c8581` | scalar | -0.0003884794439 | change in test AUC when the champion's form is refitted without season_sin |
| `calibration.mean_rel_gap.out_of_time` | `5b8375ec` | scalar | 3.3416259 | mean predicted against observed on out_of_time, relative |
| `calibration.mean_rel_gap.test` | `15d5555b` | scalar | 3.716396464 | mean predicted against observed on test, relative |
| `calibration.mean_rel_gap.train` | `324eb124` | scalar | 3.604474497 | mean predicted against observed on train, relative |
| `calibration.mean_rel_gap.vintage_holdout` | `a691b5ed` | scalar | 4.360232281 | mean predicted against observed on vintage_holdout, relative |
| `calibration.out_of_time` | `392a629c` | table | table, 10 rows | calibration by decile of predicted probability on out_of_time |
| `calibration.test` | `8417f6b7` | table | table, 10 rows | calibration by decile of predicted probability on test |
| `calibration.train` | `a8585045` | table | table, 10 rows | calibration by decile of predicted probability on train |
| `calibration.vintage_holdout` | `fd5aec5a` | table | table, 10 rows | calibration by decile of predicted probability on vintage_holdout |
| `calibration_intercept.out_of_time` | `db324216` | scalar | -1.496633503 | logistic regression of the outcome on logit(p) on out_of_time: the intercept |
| `calibration_intercept.test` | `257fb817` | scalar | -1.747805271 | logistic regression of the outcome on logit(p) on test: the intercept |
| `calibration_intercept.train` | `57309d7d` | scalar | -1.566304198 | logistic regression of the outcome on logit(p) on train: the intercept |
| `calibration_intercept.vintage_holdout` | `6f00dbc2` | scalar | -2.175702334 | logistic regression of the outcome on logit(p) on vintage_holdout: the intercept |
| `calibration_slope.out_of_time` | `ea7d5696` | scalar | 1.066358183 | logistic regression of the outcome on logit(p) on out_of_time: the slope |
| `calibration_slope.test` | `f8ef2beb` | scalar | 0.9536630305 | logistic regression of the outcome on logit(p) on test: the slope |
| `calibration_slope.train` | `ffabb935` | scalar | 1.014728573 | logistic regression of the outcome on logit(p) on train: the slope |
| `calibration_slope.vintage_holdout` | `010c0ec4` | scalar | 0.8561504457 | logistic regression of the outcome on logit(p) on vintage_holdout: the slope |
| `challenger.auc` | `705b66f0` | scalar | 0.7337079121 | the challenger's AUC on test |
| `challenger.brier` | `85a89ef9` | scalar | 0.008629514666 | the challenger's Brier score on test |
| `challenger.delta_auc` | `1e990f53` | scalar | -0.04212940647 | the challenger's AUC on test minus the champion's |
| `condition_number` | `4f06a3c5` | scalar | 4.942565522 | Belsley's condition number of the column-standardised design |
| `cpr.out_of_time.mae` | `8ac7bfbc` | scalar | 0.3179874584 | mean absolute difference between actual and predicted CPR on out_of_time |
| `cpr.test` | `ee6d2090` | table | table, 71 rows | actual against predicted CPR by period on test |
| `cpr.test.mae` | `b7587aed` | scalar | 0.222029929 | mean absolute difference between actual and predicted CPR on test |
| `cpr.train.mae` | `8d8e2c42` | scalar | 0.2239621374 | mean absolute difference between actual and predicted CPR on train |
| `cpr.vintage_holdout.mae` | `2d48e163` | scalar | 0.1720007526 | mean absolute difference between actual and predicted CPR on vintage_holdout |
| `csi.burnout` | `640f9435` | scalar | 0.0001325955583 | CSI of burnout: its contribution to the shift in the linear predictor |
| `csi.credit_score` | `6653968a` | scalar | 0.007706951731 | CSI of credit_score: its contribution to the shift in the linear predictor |
| `csi.incentive` | `3bfa986b` | scalar | 0.005685694124 | CSI of incentive: its contribution to the shift in the linear predictor |
| `csi.loan_age` | `df52c920` | scalar | 0 | CSI of loan_age: its contribution to the shift in the linear predictor |
| `csi.max` | `a8ca288d` | scalar | 0.03331391493 | the largest characteristic stability index |
| `csi.note_rate` | `e06d8658` | scalar | 0.01371659455 | CSI of note_rate: its contribution to the shift in the linear predictor |
| `csi.orig_ltv` | `7a941368` | scalar | 0.03331391493 | CSI of orig_ltv: its contribution to the shift in the linear predictor |
| `csi.orig_upb_log` | `bbbec9d2` | scalar | 0.002863276289 | CSI of orig_upb_log: its contribution to the shift in the linear predictor |
| `csi.sato` | `c9bad372` | scalar | 0.0009304918233 | CSI of sato: its contribution to the shift in the linear predictor |
| `csi.season_cos` | `78d740c8` | scalar | 0.0005033620785 | CSI of season_cos: its contribution to the shift in the linear predictor |
| `csi.season_sin` | `d16ad42f` | scalar | 6.939549558e-05 | CSI of season_sin: its contribution to the shift in the linear predictor |
| `deciles.out_of_time.top2_capture` | `95c24730` | scalar | 0.5909090909 | share of out_of_time events in the top two deciles |
| `deciles.test` | `9246d1cd` | table | table, 10 rows | decile separation on test; decile 1 holds the highest probabilities |
| `deciles.test.top2_capture` | `43c4adc5` | scalar | 0.5806451613 | share of test events in the top two deciles |
| `deciles.train.top2_capture` | `eb38637b` | scalar | 0.6058631922 | share of train events in the top two deciles |
| `deciles.vintage_holdout.top2_capture` | `4a376307` | scalar | 0.5935483871 | share of vintage_holdout events in the top two deciles |
| `leakage.duplicates.train` | `4474c227` | scalar | 0 | share of train rows whose feature values are not unique within train |
| `leakage.name_screen.n_matched` | `407e62be` | scalar | 0 | feature names matching the target-adjacent lexicon |
| `leakage.overlap` | `4c9fcd09` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.features` | `0fec8048` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.ids` | `63d37fc5` | scalar | 0 | share of test rows whose ['loan_id', 'period'] also identify a row of train |
| `leakage.target_corr.max_single_feature_auc` | `1fe630dd` | scalar | 0.7238936567 | the AUC of the strongest single feature |
| `leakage.timing.n_flagged` | `742bcd24` | scalar | 0 | features declared during_period or after_outcome |
| `metrics.out_of_time.auc` | `aa836722` | scalar | 0.7897867937 | auc on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.brier` | `a8a8d3a5` | scalar | 0.02402096444 | brier on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.event_rate` | `83ccf5c0` | scalar | 0.01794892714 | event_rate on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.gini` | `3dc07327` | scalar | 0.5795735875 | gini on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.ks` | `00bf02ed` | scalar | 0.43678733 | ks on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.logloss` | `5198f968` | scalar | 0.1173954835 | logloss on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.mean_predicted` | `921d185b` | scalar | 0.07792752696 | mean_predicted on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.n` | `7898809e` | scalar | 12257 | n on out_of_time, recomputed by quaestor |
| `metrics.test.auc` | `2f4cab3e` | scalar | 0.7758373186 | auc on test, recomputed by quaestor |
| `metrics.test.brier` | `1e4aab51` | scalar | 0.009863834665 | brier on test, recomputed by quaestor |
| `metrics.test.event_rate` | `570cc08a` | scalar | 0.008061370433 | event_rate on test, recomputed by quaestor |
| `metrics.test.gini` | `8593585c` | scalar | 0.5516746371 | gini on test, recomputed by quaestor |
| `metrics.test.ks` | `554f1e19` | scalar | 0.4280398649 | ks on test, recomputed by quaestor |
| `metrics.test.logloss` | `b9424e16` | scalar | 0.06118235348 | logloss on test, recomputed by quaestor |
| `metrics.test.mean_predicted` | `122af437` | scalar | 0.038020619 | mean_predicted on test, recomputed by quaestor |
| `metrics.test.n` | `e55953e1` | scalar | 15382 | n on test, recomputed by quaestor |
| `metrics.train.auc` | `39508266` | scalar | 0.7891607921 | auc on train, recomputed by quaestor |
| `metrics.train.brier` | `d56a10b2` | scalar | 0.01035868886 | brier on train, recomputed by quaestor |
| `metrics.train.event_rate` | `b9ef3327` | scalar | 0.008524699414 | event_rate on train, recomputed by quaestor |
| `metrics.train.gini` | `d618ff0f` | scalar | 0.5783215843 | gini on train, recomputed by quaestor |
| `metrics.train.ks` | `e8d4ae61` | scalar | 0.4541800929 | ks on train, recomputed by quaestor |
| `metrics.train.logloss` | `2bff29d3` | scalar | 0.06296558061 | logloss on train, recomputed by quaestor |
| `metrics.train.mean_predicted` | `68f41b88` | scalar | 0.03925176105 | mean_predicted on train, recomputed by quaestor |
| `metrics.train.n` | `6fdfeabb` | scalar | 36013 | n on train, recomputed by quaestor |
| `metrics.vintage_holdout.auc` | `25db8aa3` | scalar | 0.7742985165 | auc on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.brier` | `55737812` | scalar | 0.006100676477 | brier on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.event_rate` | `e3590a16` | scalar | 0.004817105386 | event_rate on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.gini` | `eff9b345` | scalar | 0.5485970331 | gini on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.ks` | `a2ee5005` | scalar | 0.4530637203 | ks on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.logloss` | `9f19871a` | scalar | 0.04161346969 | logloss on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.mean_predicted` | `348107ae` | scalar | 0.02582080379 | mean_predicted on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.n` | `37a92951` | scalar | 32177 | n on vintage_holdout, recomputed by quaestor |
| `profile.out_of_time.missing.max` | `4dafce11` | scalar | 0 | the largest missing fraction in out_of_time |
| `profile.out_of_time.n` | `fa39c5cf` | scalar | 12257 | rows in out_of_time |
| `profile.test.missing.max` | `f813848d` | scalar | 0 | the largest missing fraction in test |
| `profile.test.n` | `e3abc1b8` | scalar | 15382 | rows in test |
| `profile.train.missing.max` | `050a3099` | scalar | 0 | the largest missing fraction in train |
| `profile.train.n` | `c5ebd9c9` | scalar | 36013 | rows in train |
| `profile.vintage_holdout.missing.max` | `329bb430` | scalar | 0 | the largest missing fraction in vintage_holdout |
| `profile.vintage_holdout.n` | `426e712a` | scalar | 32177 | rows in vintage_holdout |
| `psi.burnout` | `9dc7ecc2` | scalar | 0.004614338236 | PSI of burnout between train and test |
| `psi.credit_score` | `7e87527c` | scalar | 0.06188985797 | PSI of credit_score between train and test |
| `psi.incentive` | `2da5570f` | scalar | 0.0009922551416 | PSI of incentive between train and test |
| `psi.loan_age` | `2202b157` | scalar | 0.0001993816816 | PSI of loan_age between train and test |
| `psi.max` | `c2e8c8fd` | scalar | 0.06188985797 | the largest train-to-test PSI, score included |
| `psi.note_rate` | `ecc6adf3` | scalar | 0.01370911382 | PSI of note_rate between train and test |
| `psi.orig_ltv` | `cd1ff136` | scalar | 0.03617297258 | PSI of orig_ltv between train and test |
| `psi.orig_upb_log` | `55030a3b` | scalar | 0.04817081196 | PSI of orig_upb_log between train and test |
| `psi.out_of_time.burnout` | `7b0bbebb` | scalar | 2.944521522 | PSI of burnout between train and out_of_time |
| `psi.out_of_time.credit_score` | `d7249e47` | scalar | 0.05987964443 | PSI of credit_score between train and out_of_time |
| `psi.out_of_time.incentive` | `42076ed1` | scalar | 0.4958065489 | PSI of incentive between train and out_of_time |
| `psi.out_of_time.loan_age` | `d6eaaaf5` | scalar | 2.483993033 | PSI of loan_age between train and out_of_time |
| `psi.out_of_time.note_rate` | `cabd371d` | scalar | 0.6976589281 | PSI of note_rate between train and out_of_time |
| `psi.out_of_time.orig_ltv` | `3eee5db4` | scalar | 0.04300793312 | PSI of orig_ltv between train and out_of_time |
| `psi.out_of_time.orig_upb_log` | `ac349b67` | scalar | 0.07136421414 | PSI of orig_upb_log between train and out_of_time |
| `psi.out_of_time.sato` | `c2233ce6` | scalar | 0.01298850667 | PSI of sato between train and out_of_time |
| `psi.out_of_time.season_cos` | `25cf6b85` | scalar | 0.00752368457 | PSI of season_cos between train and out_of_time |
| `psi.out_of_time.season_sin` | `144e1bd9` | scalar | 0.02788988464 | PSI of season_sin between train and out_of_time |
| `psi.out_of_time.y_score` | `6f080528` | scalar | 0.6984990823 | PSI of the score between train and out_of_time |
| `psi.sato` | `584da64f` | scalar | 0.02772829856 | PSI of sato between train and test |
| `psi.season_cos` | `addec503` | scalar | 1.790085913e-05 | PSI of season_cos between train and test |
| `psi.season_sin` | `4d2ed98d` | scalar | 2.939045338e-06 | PSI of season_sin between train and test |
| `psi.vintage_holdout.burnout` | `e29067e6` | scalar | 0.04749372789 | PSI of burnout between train and vintage_holdout |
| `psi.vintage_holdout.credit_score` | `3498d307` | scalar | 0.03995819732 | PSI of credit_score between train and vintage_holdout |
| `psi.vintage_holdout.incentive` | `5e61b6f9` | scalar | 0.4475226601 | PSI of incentive between train and vintage_holdout |
| `psi.vintage_holdout.loan_age` | `6d92c48b` | scalar | 0.07111526296 | PSI of loan_age between train and vintage_holdout |
| `psi.vintage_holdout.note_rate` | `f281f8a7` | scalar | 0.608822927 | PSI of note_rate between train and vintage_holdout |
| `psi.vintage_holdout.orig_ltv` | `d07cfb7d` | scalar | 0.0294150369 | PSI of orig_ltv between train and vintage_holdout |
| `psi.vintage_holdout.orig_upb_log` | `77ec758a` | scalar | 0.04039645306 | PSI of orig_upb_log between train and vintage_holdout |
| `psi.vintage_holdout.sato` | `eea64c25` | scalar | 0.02989256711 | PSI of sato between train and vintage_holdout |
| `psi.vintage_holdout.season_cos` | `9fe842a8` | scalar | 0.0012879007 | PSI of season_cos between train and vintage_holdout |
| `psi.vintage_holdout.season_sin` | `b0dc9745` | scalar | 0.0007309374015 | PSI of season_sin between train and vintage_holdout |
| `psi.vintage_holdout.y_score` | `c71062d6` | scalar | 0.1603916415 | PSI of the score between train and vintage_holdout |
| `psi.y_score` | `aa10164c` | scalar | 0.001868586849 | PSI of the score between train and test |
| `rule.calibration_first_event_rate` | `42f1351e` | scalar | 0.05 | the event rate below which the report puts calibration before discrimination |
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |
| `scenario.convexity` | `42ad3e3e` | scalar | -541831.8779 | the value change at -300 bp plus the change at 300 bp; negative when the fall outweighs the rise |
| `scenario.value_by_shock` | `89b33839` | table | table, 7 rows | servicing value, its change from the base case and first-year CPR, by shock |
| `scenario.value_change.-100` | `b3c09ea9` | scalar | -517824.9714 | change in servicing value at -100 bp |
| `scenario.value_change.-200` | `59e2f8a4` | scalar | -927073.1975 | change in servicing value at -200 bp |
| `scenario.value_change.-300` | `ff90f8c1` | scalar | -1099446.442 | change in servicing value at -300 bp |
| `scenario.value_change.0` | `1e1b0b88` | scalar | 0 | change in servicing value at 0 bp |
| `scenario.value_change.100` | `95da798d` | scalar | 352845.0358 | change in servicing value at 100 bp |
| `scenario.value_change.200` | `be13cc25` | scalar | 505801.2473 | change in servicing value at 200 bp |
| `scenario.value_change.300` | `0b43db3b` | scalar | 557614.5638 | change in servicing value at 300 bp |
| `sign_check.burnout.agrees` | `56826e40` | scalar | 0 | 1 when the fitted sign on burnout agrees with its univariate direction, 0 when it does not |
| `sign_check.burnout.coef_sign` | `dcfb2de4` | scalar | -1 | the sign of the fitted coefficient on burnout |
| `sign_check.burnout.univariate_direction` | `bfc96bb2` | scalar | 1 | the sign of burnout's own single-feature AUC on train minus 0.5 |
| `sign_check.credit_score.agrees` | `915bf8eb` | scalar | 1 | 1 when the fitted sign on credit_score agrees with its univariate direction, 0 when it does not |
| `sign_check.credit_score.coef_sign` | `1ec1078b` | scalar | 1 | the sign of the fitted coefficient on credit_score |
| `sign_check.credit_score.univariate_direction` | `42303896` | scalar | 1 | the sign of credit_score's own single-feature AUC on train minus 0.5 |
| `sign_check.incentive.agrees` | `f7b2338e` | scalar | 1 | 1 when the fitted sign on incentive agrees with its univariate direction, 0 when it does not |
| `sign_check.incentive.coef_sign` | `684cf11a` | scalar | 1 | the sign of the fitted coefficient on incentive |
| `sign_check.incentive.univariate_direction` | `8098d951` | scalar | 1 | the sign of incentive's own single-feature AUC on train minus 0.5 |
| `sign_check.n_disagreements` | `e223cd4a` | scalar | 3 | retained features whose fitted sign contradicts their univariate direction, of 9 checked |
| `sign_check.note_rate.agrees` | `a453463d` | scalar | 0 | 1 when the fitted sign on note_rate agrees with its univariate direction, 0 when it does not |
| `sign_check.note_rate.coef_sign` | `aecf7ccb` | scalar | -1 | the sign of the fitted coefficient on note_rate |
| `sign_check.note_rate.univariate_direction` | `61f6e1ac` | scalar | 1 | the sign of note_rate's own single-feature AUC on train minus 0.5 |
| `sign_check.orig_ltv.agrees` | `7021aeb0` | scalar | 1 | 1 when the fitted sign on orig_ltv agrees with its univariate direction, 0 when it does not |
| `sign_check.orig_ltv.coef_sign` | `7eec65ec` | scalar | -1 | the sign of the fitted coefficient on orig_ltv |
| `sign_check.orig_ltv.univariate_direction` | `76dbc708` | scalar | -1 | the sign of orig_ltv's own single-feature AUC on train minus 0.5 |
| `sign_check.orig_upb_log.agrees` | `07a9d3e6` | scalar | 1 | 1 when the fitted sign on orig_upb_log agrees with its univariate direction, 0 when it does not |
| `sign_check.orig_upb_log.coef_sign` | `5aa309fc` | scalar | 1 | the sign of the fitted coefficient on orig_upb_log |
| `sign_check.orig_upb_log.univariate_direction` | `b9743ecb` | scalar | 1 | the sign of orig_upb_log's own single-feature AUC on train minus 0.5 |
| `sign_check.sato.agrees` | `b3755963` | scalar | 0 | 1 when the fitted sign on sato agrees with its univariate direction, 0 when it does not |
| `sign_check.sato.coef_sign` | `265915cf` | scalar | -1 | the sign of the fitted coefficient on sato |
| `sign_check.sato.univariate_direction` | `c08233a6` | scalar | 1 | the sign of sato's own single-feature AUC on train minus 0.5 |
| `sign_check.season_cos.agrees` | `7f18ddf7` | scalar | 1 | 1 when the fitted sign on season_cos agrees with its univariate direction, 0 when it does not |
| `sign_check.season_cos.coef_sign` | `7dbb1ffc` | scalar | -1 | the sign of the fitted coefficient on season_cos |
| `sign_check.season_cos.univariate_direction` | `03e931f0` | scalar | -1 | the sign of season_cos's own single-feature AUC on train minus 0.5 |
| `sign_check.season_sin.agrees` | `e110f357` | scalar | 1 | 1 when the fitted sign on season_sin agrees with its univariate direction, 0 when it does not |
| `sign_check.season_sin.coef_sign` | `761188ce` | scalar | 1 | the sign of the fitted coefficient on season_sin |
| `sign_check.season_sin.univariate_direction` | `cae6b096` | scalar | 1 | the sign of season_sin's own single-feature AUC on train minus 0.5 |
| `stability.auc_by_regime` | `0b789c1f` | table | table, 2 rows | the champion's AUC within each rate_regime on train |
| `stability.burnout.sign_flip` | `6bc05e82` | scalar | 0 | 1 when burnout is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.credit_score.sign_flip` | `d956c276` | scalar | 0 | 1 when credit_score is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.incentive.sign_flip` | `0cc7a37d` | scalar | 0 | 1 when incentive is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.loan_age.sign_flip` | `b7191217` | scalar | 0 | 1 when loan_age is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.note_rate.sign_flip` | `e7ce4912` | scalar | 0 | 1 when note_rate is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.orig_ltv.sign_flip` | `054d5fab` | scalar | 0 | 1 when orig_ltv is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.orig_upb_log.sign_flip` | `fb1ae6c8` | scalar | 0 | 1 when orig_upb_log is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.sato.sign_flip` | `1f302ccd` | scalar | 0 | 1 when sato is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.season_cos.sign_flip` | `1850e2de` | scalar | 0 | 1 when season_cos is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.season_sin.sign_flip` | `6ba36a3b` | scalar | 0 | 1 when season_sin is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
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
| `threshold.O1.holdout_gap` | `90f8b6d9` | scalar | 0.05 | O1: how far a period split's AUC may fall below test |
| `threshold.R1.auc_gap` | `b64213d7` | scalar | 0.1 | R1: the AUC difference across regimes |
| `threshold.R1.sign_flip_coef` | `aca84377` | scalar | 0.05 | R1: the coefficient a sign flip must exceed in both regimes |
| `threshold.R1.sign_flip_z` | `2e4428c7` | scalar | 2 | R1: the \|z\| a sign flip's coefficient must reach in both regimes |
| `threshold.S1.psi` | `278b9016` | scalar | 0.25 | S1: the population stability index, train against test |
| `threshold.package.auc.test.min` | `fececac1` | scalar | 0.65 | package.yaml declares auc min 0.65 |
| `threshold.package.calibration_slope.test.max` | `0adb7a89` | scalar | 1.2 | package.yaml declares calibration_slope max 1.2 |
| `threshold.package.calibration_slope.test.min` | `95fdb848` | scalar | 0.8 | package.yaml declares calibration_slope min 0.8 |
| `threshold.package.psi.max` | `fbb5a9d1` | scalar | 0.25 | package.yaml declares psi max 0.25 |
| `thresholds.evaluation` | `2fc2a920` | table | table, 4 rows | every threshold package.yaml declares, with its bound, the recomputed value and the outcome |
| `vif.burnout` | `88879cb2` | scalar | 3.439328594 | variance inflation factor of burnout on train |
| `vif.credit_score` | `f05d536a` | scalar | 1.007978309 | variance inflation factor of credit_score on train |
| `vif.incentive` | `2da1b19c` | scalar | 2.22632259 | variance inflation factor of incentive on train |
| `vif.loan_age` | `5573d536` | scalar | 2.928871763 | variance inflation factor of loan_age on train |
| `vif.max` | `f9e0db60` | scalar | 4.975500767 | the largest variance inflation factor |
| `vif.note_rate` | `37532fa8` | scalar | 4.975500767 | variance inflation factor of note_rate on train |
| `vif.orig_ltv` | `65b35f3b` | scalar | 1.004506143 | variance inflation factor of orig_ltv on train |
| `vif.orig_upb_log` | `24f8e4d1` | scalar | 1.005846447 | variance inflation factor of orig_upb_log on train |
| `vif.sato` | `a6c55fce` | scalar | 1.71256814 | variance inflation factor of sato on train |
| `vif.season_cos` | `a9cfa7eb` | scalar | 1.017653349 | variance inflation factor of season_cos on train |
| `vif.season_sin` | `669c5fcb` | scalar | 1.004128844 | variance inflation factor of season_sin on train |

## Appendix C — Run trace summary

| quantity | value |
|---|---|
| tool calls | 15 (run_model 1, profile_data 1, compute_metrics 1, check_leakage 1, check_stability 1, check_collinearity 1, challenger_compare 1, run_scenarios 1, retrieve_guidance 7) |
| plan steps (bounded loop) | 0 |
| LLM calls | 0 () |
| re-asks | 0 |
| repair rounds | 0 |
| tokens in / out | 0 / 0 |
| notional cost (USD) | 0.0000 |
| wall-clock (s) | 1.76 |
| subject run (s) | 2.96 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | fake |
| model | none: no model answered |
| run id | msr_prepayment-rules_only-20260918T065337Z-568d25f5 |

## Appendix D — Not checked

| item | reason |
|---|---|
| developer claims (T1, claim channel) | The package declares 3 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
| drafted narrative and the repair loop | `rules_only` calls no model; the narrative is a template |
