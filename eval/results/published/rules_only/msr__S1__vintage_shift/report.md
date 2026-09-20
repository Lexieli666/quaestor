---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: msr_prepayment
version: "1.0"
model_type: discrete_time_hazard
configuration: rules_only
model: fake
run_id: msr_prepayment-rules_only-20260918T065352Z-568d25f5
data_mode: synthetic
synthetic_n: 2000
grounding_precision_pre: 1.0000
grounding_precision_post: 1.0000
n_claims: 329
n_findings_by_severity: {high: 1, medium: 2, low: 0, info: 0}
generated: "2026-09-18T06:53:52Z"
illustrative: false
---

# Validation report — `msr_prepayment` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `msr_prepayment` v1.0 | `rules_only` | fake | synthetic, n = 2000 | 1.0000 → 1.0000 | 1 / 2 / 0 / 0 |
<!-- quaestor:renderer:end -->

This section follows the model risk management guidance at [[reg:SR26-2:V.1.b]].
The value of `calibration_slope.out_of_time` is 0.9369 [[art:994798d5:calibration_slope.out_of_time]].
The value of `calibration_slope.test` is 0.9369 [[art:290cccd9:calibration_slope.test]].
The value of `calibration_slope.train` is 1.015 [[art:6ee05ed8:calibration_slope.train]].
The value of `calibration_slope.vintage_holdout` is 0.8554 [[art:6b42345a:calibration_slope.vintage_holdout]].
The value of `challenger.delta_auc` is -0.06356 [[art:7e119a34:challenger.delta_auc]].
The value of `condition_number` is 4.778 [[art:5e2416a9:condition_number]].
The value of `csi.max` is 0.9221 [[art:d4b08859:csi.max]].
The value of `metrics.out_of_time.auc` is 0.7846 [[art:ee898745:metrics.out_of_time.auc]].
The value of `metrics.out_of_time.brier` is 0.01725 [[art:f0fd020a:metrics.out_of_time.brier]].
The value of `metrics.out_of_time.event_rate` is 0.01795 [[art:83ccf5c0:metrics.out_of_time.event_rate]].
The value of `metrics.out_of_time.gini` is 0.5692 [[art:46899ec9:metrics.out_of_time.gini]].
The value of `metrics.out_of_time.ks` is 0.4373 [[art:6360ccf9:metrics.out_of_time.ks]].
The value of `metrics.out_of_time.logloss` is 0.0805 [[art:205ce509:metrics.out_of_time.logloss]].
The value of `metrics.out_of_time.mean_predicted` is 0.02283 [[art:4d7aa98b:metrics.out_of_time.mean_predicted]].
The value of `metrics.out_of_time.n` is 12257 [[art:7898809e:metrics.out_of_time.n]].
The value of `metrics.test.auc` is 0.7846 [[art:d57b2552:metrics.test.auc]].
The value of `metrics.test.brier` is 0.01725 [[art:68e8b1cf:metrics.test.brier]].
The value of `metrics.test.event_rate` is 0.01795 [[art:d222aedf:metrics.test.event_rate]].
The value of `metrics.test.gini` is 0.5692 [[art:1291e305:metrics.test.gini]].
The value of `metrics.test.ks` is 0.4373 [[art:857a0cf9:metrics.test.ks]].
The value of `metrics.test.logloss` is 0.0805 [[art:c576b630:metrics.test.logloss]].
The value of `metrics.test.mean_predicted` is 0.02283 [[art:1c1a1d8d:metrics.test.mean_predicted]].
The value of `metrics.test.n` is 12257 [[art:90b46eb1:metrics.test.n]].
The value of `metrics.train.auc` is 0.8003 [[art:41d3c4e6:metrics.train.auc]].
The value of `metrics.train.brier` is 0.008111 [[art:e9077291:metrics.train.brier]].
The value of `metrics.train.event_rate` is 0.008323 [[art:b0cf2348:metrics.train.event_rate]].
The value of `metrics.train.gini` is 0.6006 [[art:66b6cc81:metrics.train.gini]].
The value of `metrics.train.ks` is 0.474 [[art:3e0b8829:metrics.train.ks]].
The value of `metrics.train.logloss` is 0.04279 [[art:e62507ab:metrics.train.logloss]].
The value of `metrics.train.mean_predicted` is 0.008333 [[art:4ea7b930:metrics.train.mean_predicted]].
The value of `metrics.train.n` is 33522 [[art:dd20fa4c:metrics.train.n]].
The value of `metrics.vintage_holdout.auc` is 0.7716 [[art:610c13fd:metrics.vintage_holdout.auc]].
The value of `metrics.vintage_holdout.brier` is 0.004767 [[art:115af096:metrics.vintage_holdout.brier]].
The value of `metrics.vintage_holdout.event_rate` is 0.004817 [[art:e3590a16:metrics.vintage_holdout.event_rate]].
The value of `metrics.vintage_holdout.gini` is 0.5432 [[art:4b1525bb:metrics.vintage_holdout.gini]].
The value of `metrics.vintage_holdout.ks` is 0.4618 [[art:c3ac5a54:metrics.vintage_holdout.ks]].
The value of `metrics.vintage_holdout.logloss` is 0.02818 [[art:96a19aae:metrics.vintage_holdout.logloss]].
The value of `metrics.vintage_holdout.mean_predicted` is 0.006157 [[art:914aeeba:metrics.vintage_holdout.mean_predicted]].
The value of `metrics.vintage_holdout.n` is 32177 [[art:37a92951:metrics.vintage_holdout.n]].
The value of `profile.test.n` is 12257 [[art:3b91ffcc:profile.test.n]].
The value of `profile.train.n` is 33522 [[art:60d3a086:profile.train.n]].
The value of `psi.max` is 3.016 [[art:4fae32c6:psi.max]].
The value of `runtime.max_seconds` is 300 [[art:2ad8d1a5:runtime.max_seconds]].
The value of `threshold.package.auc.test.min` is 0.65 [[art:fececac1:threshold.package.auc.test.min]].
The value of `threshold.package.calibration_slope.test.max` is 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The value of `threshold.package.calibration_slope.test.min` is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
The value of `vif.max` is 4.288 [[art:fecfb289:vif.max]].

## 2. Conceptual soundness

This section follows the model risk management guidance at [[reg:SR26-2:V.1.a]].
The value of `ablation.baseline_auc` is 0.7802 [[art:93dda83a:ablation.baseline_auc]].
The value of `ablation.burnout.delta_auc` is 0.004292 [[art:8aa8bccf:ablation.burnout.delta_auc]].
The value of `ablation.credit_score.delta_auc` is -0.0298 [[art:a2d10cd7:ablation.credit_score.delta_auc]].
The value of `ablation.incentive.delta_auc` is -0.07943 [[art:46802ce1:ablation.incentive.delta_auc]].
The value of `ablation.loan_age.delta_auc` is -0.009946 [[art:ca8fa8e9:ablation.loan_age.delta_auc]].
The value of `ablation.note_rate.delta_auc` is 0.005792 [[art:338b461a:ablation.note_rate.delta_auc]].
The value of `ablation.orig_ltv.delta_auc` is -0.01199 [[art:84275e57:ablation.orig_ltv.delta_auc]].
The value of `ablation.orig_upb_log.delta_auc` is -0.01681 [[art:6158bf75:ablation.orig_upb_log.delta_auc]].
The value of `ablation.sato.delta_auc` is -0.004237 [[art:c9eb03ef:ablation.sato.delta_auc]].
The value of `ablation.season_cos.delta_auc` is -0.005672 [[art:bdbbba37:ablation.season_cos.delta_auc]].
The value of `ablation.season_sin.delta_auc` is 0.00054 [[art:95e1e0c6:ablation.season_sin.delta_auc]].
The value of `challenger.auc` is 0.7211 [[art:489cd7a6:challenger.auc]].
The value of `challenger.brier` is 0.02173 [[art:36aa75c4:challenger.brier]].
The value of `challenger.delta_auc` is -0.06356 [[art:7e119a34:challenger.delta_auc]].
The value of `metrics.test.auc` is 0.7846 [[art:d57b2552:metrics.test.auc]].
The value of `metrics.test.brier` is 0.01725 [[art:68e8b1cf:metrics.test.brier]].
The value of `sign_check.burnout.agrees` is 1 [[art:2eec20ab:sign_check.burnout.agrees]].
The value of `sign_check.burnout.coef_sign` is 1 [[art:a3063608:sign_check.burnout.coef_sign]].
The value of `sign_check.burnout.univariate_direction` is 1 [[art:bfc96bb2:sign_check.burnout.univariate_direction]].
The value of `sign_check.credit_score.agrees` is 1 [[art:915bf8eb:sign_check.credit_score.agrees]].
The value of `sign_check.credit_score.coef_sign` is 1 [[art:1ec1078b:sign_check.credit_score.coef_sign]].
The value of `sign_check.credit_score.univariate_direction` is 1 [[art:42303896:sign_check.credit_score.univariate_direction]].
The value of `sign_check.incentive.agrees` is 1 [[art:f7b2338e:sign_check.incentive.agrees]].
The value of `sign_check.incentive.coef_sign` is 1 [[art:684cf11a:sign_check.incentive.coef_sign]].
The value of `sign_check.incentive.univariate_direction` is 1 [[art:8098d951:sign_check.incentive.univariate_direction]].
The value of `sign_check.n_disagreements` is 1 [[art:f96ece96:sign_check.n_disagreements]].
The value of `sign_check.note_rate.agrees` is 0 [[art:a453463d:sign_check.note_rate.agrees]].
The value of `sign_check.note_rate.coef_sign` is -1 [[art:aecf7ccb:sign_check.note_rate.coef_sign]].
The value of `sign_check.note_rate.univariate_direction` is 1 [[art:61f6e1ac:sign_check.note_rate.univariate_direction]].
The value of `sign_check.orig_ltv.agrees` is 1 [[art:7021aeb0:sign_check.orig_ltv.agrees]].
The value of `sign_check.orig_ltv.coef_sign` is -1 [[art:7eec65ec:sign_check.orig_ltv.coef_sign]].
The value of `sign_check.orig_ltv.univariate_direction` is -1 [[art:76dbc708:sign_check.orig_ltv.univariate_direction]].
The value of `sign_check.orig_upb_log.agrees` is 1 [[art:07a9d3e6:sign_check.orig_upb_log.agrees]].
The value of `sign_check.orig_upb_log.coef_sign` is 1 [[art:5aa309fc:sign_check.orig_upb_log.coef_sign]].
The value of `sign_check.orig_upb_log.univariate_direction` is 1 [[art:b9743ecb:sign_check.orig_upb_log.univariate_direction]].
The value of `sign_check.sato.agrees` is 1 [[art:2401eba2:sign_check.sato.agrees]].
The value of `sign_check.sato.coef_sign` is 1 [[art:c031d0d5:sign_check.sato.coef_sign]].
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
The value of `csi.burnout` is 0.3489 [[art:e0f86ff2:csi.burnout]].
The value of `csi.credit_score` is 0.09087 [[art:4fbc434e:csi.credit_score]].
The value of `csi.incentive` is 0.9221 [[art:f430cc2d:csi.incentive]].
The value of `csi.loan_age` is 0 [[art:df52c920:csi.loan_age]].
The value of `csi.max` is 0.9221 [[art:d4b08859:csi.max]].
The value of `csi.note_rate` is 0.4832 [[art:a2be3f30:csi.note_rate]].
The value of `csi.orig_ltv` is 0.02303 [[art:af80429c:csi.orig_ltv]].
The value of `csi.orig_upb_log` is 0.06562 [[art:ba82e949:csi.orig_upb_log]].
The value of `csi.sato` is 0.0001468 [[art:7d563a3f:csi.sato]].
The value of `csi.season_cos` is 0.003265 [[art:49e6d56e:csi.season_cos]].
The value of `csi.season_sin` is 0.01316 [[art:ff10caf4:csi.season_sin]].
The value of `leakage.duplicates.train` is 0 [[art:4474c227:leakage.duplicates.train]].
The value of `leakage.name_screen.n_matched` is 0 [[art:407e62be:leakage.name_screen.n_matched]].
The value of `leakage.overlap` is 0 [[art:4c9fcd09:leakage.overlap]].
The value of `leakage.overlap.features` is 0 [[art:0fec8048:leakage.overlap.features]].
The value of `leakage.overlap.ids` is 0 [[art:63d37fc5:leakage.overlap.ids]].
The value of `leakage.target_corr.max_single_feature_auc` is 0.7422 [[art:b6b29a14:leakage.target_corr.max_single_feature_auc]].
The value of `leakage.timing.n_flagged` is 0 [[art:742bcd24:leakage.timing.n_flagged]].
The value of `profile.out_of_time.missing.max` is 0 [[art:4dafce11:profile.out_of_time.missing.max]].
The value of `profile.out_of_time.n` is 12257 [[art:fa39c5cf:profile.out_of_time.n]].
The value of `profile.test.missing.max` is 0 [[art:f813848d:profile.test.missing.max]].
The value of `profile.test.n` is 12257 [[art:3b91ffcc:profile.test.n]].
The value of `profile.train.missing.max` is 0 [[art:050a3099:profile.train.missing.max]].
The value of `profile.train.n` is 33522 [[art:60d3a086:profile.train.n]].
The value of `profile.vintage_holdout.missing.max` is 0 [[art:329bb430:profile.vintage_holdout.missing.max]].
The value of `profile.vintage_holdout.n` is 32177 [[art:426e712a:profile.vintage_holdout.n]].
The value of `psi.burnout` is 3.016 [[art:1d35a583:psi.burnout]].
The value of `psi.credit_score` is 0.07088 [[art:91c4ab83:psi.credit_score]].
The value of `psi.incentive` is 0.8734 [[art:0f61188c:psi.incentive]].
The value of `psi.loan_age` is 1.68 [[art:987aabe4:psi.loan_age]].
The value of `psi.max` is 3.016 [[art:4fae32c6:psi.max]].
The value of `psi.note_rate` is 1.342 [[art:2f1cb70b:psi.note_rate]].
The value of `psi.orig_ltv` is 0.04332 [[art:85842fd0:psi.orig_ltv]].
The value of `psi.orig_upb_log` is 0.08171 [[art:f075546d:psi.orig_upb_log]].
The value of `psi.out_of_time.burnout` is 3.016 [[art:8cedaf79:psi.out_of_time.burnout]].
The value of `psi.out_of_time.credit_score` is 0.07088 [[art:a7ef717f:psi.out_of_time.credit_score]].
The value of `psi.out_of_time.incentive` is 0.8734 [[art:ec6da34d:psi.out_of_time.incentive]].
The value of `psi.out_of_time.loan_age` is 1.68 [[art:ab2af3f2:psi.out_of_time.loan_age]].
The value of `psi.out_of_time.note_rate` is 1.342 [[art:fc610fd1:psi.out_of_time.note_rate]].
The value of `psi.out_of_time.orig_ltv` is 0.04332 [[art:7eedf98f:psi.out_of_time.orig_ltv]].
The value of `psi.out_of_time.orig_upb_log` is 0.08171 [[art:9ca9c306:psi.out_of_time.orig_upb_log]].
The value of `psi.out_of_time.sato` is 0.02284 [[art:79f6f94a:psi.out_of_time.sato]].
The value of `psi.out_of_time.season_cos` is 0.004988 [[art:ef947d09:psi.out_of_time.season_cos]].
The value of `psi.out_of_time.season_sin` is 0.01631 [[art:fe2b0197:psi.out_of_time.season_sin]].
The value of `psi.out_of_time.y_score` is 0.8372 [[art:d39a4ced:psi.out_of_time.y_score]].
The value of `psi.sato` is 0.02284 [[art:4809116c:psi.sato]].
The value of `psi.season_cos` is 0.004988 [[art:62ae6c81:psi.season_cos]].
The value of `psi.season_sin` is 0.01631 [[art:46fec014:psi.season_sin]].
The value of `psi.vintage_holdout.burnout` is 0.03122 [[art:b2dacb71:psi.vintage_holdout.burnout]].
The value of `psi.vintage_holdout.credit_score` is 0.01929 [[art:16906529:psi.vintage_holdout.credit_score]].
The value of `psi.vintage_holdout.incentive` is 0.2101 [[art:1d339225:psi.vintage_holdout.incentive]].
The value of `psi.vintage_holdout.loan_age` is 0.03489 [[art:e579422e:psi.vintage_holdout.loan_age]].
The value of `psi.vintage_holdout.note_rate` is 0.2743 [[art:d4e6aa9a:psi.vintage_holdout.note_rate]].
The value of `psi.vintage_holdout.orig_ltv` is 0.03575 [[art:1f0e3df0:psi.vintage_holdout.orig_ltv]].
The value of `psi.vintage_holdout.orig_upb_log` is 0.03038 [[art:10fd298a:psi.vintage_holdout.orig_upb_log]].
The value of `psi.vintage_holdout.sato` is 0.02841 [[art:6c4e561c:psi.vintage_holdout.sato]].
The value of `psi.vintage_holdout.season_cos` is 0.00164 [[art:4482dc21:psi.vintage_holdout.season_cos]].
The value of `psi.vintage_holdout.season_sin` is 0.001971 [[art:836b68bf:psi.vintage_holdout.season_sin]].
The value of `psi.vintage_holdout.y_score` is 0.08202 [[art:5d010092:psi.vintage_holdout.y_score]].
The value of `psi.y_score` is 0.8372 [[art:92ac1652:psi.y_score]].
The value of `threshold.D1.missing_gap` is 0.1 [[art:9cce25ea:threshold.D1.missing_gap]].
The value of `threshold.L1.single_feature_auc` is 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]].
The value of `threshold.L2.overlap` is 0.005 [[art:9f336eaf:threshold.L2.overlap]].
The value of `threshold.L2.overlap.features_effective` is 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].
The value of `threshold.S1.psi` is 0.25 [[art:278b9016:threshold.S1.psi]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
Candidates raised on this section's material: S1 (see the findings section).

## 4. Outcomes analysis

This section follows the model risk management guidance at [[reg:SR26-2:V.1.b]].
The value of `calibration.mean_rel_gap.out_of_time` is 0.2718 [[art:c5239af4:calibration.mean_rel_gap.out_of_time]].
The value of `calibration.mean_rel_gap.test` is 0.2718 [[art:04dcea16:calibration.mean_rel_gap.test]].
The value of `calibration.mean_rel_gap.train` is 0.001197 [[art:7d19dc79:calibration.mean_rel_gap.train]].
The value of `calibration.mean_rel_gap.vintage_holdout` is 0.2782 [[art:2eba48c2:calibration.mean_rel_gap.vintage_holdout]].
The value of `calibration_intercept.out_of_time` is -0.4556 [[art:8dc58882:calibration_intercept.out_of_time]].
The value of `calibration_intercept.test` is -0.4556 [[art:256e21c4:calibration_intercept.test]].
The value of `calibration_intercept.train` is 0.06177 [[art:7184b1c0:calibration_intercept.train]].
The value of `calibration_intercept.vintage_holdout` is -0.8976 [[art:21c5b98a:calibration_intercept.vintage_holdout]].
The value of `calibration_slope.out_of_time` is 0.9369 [[art:994798d5:calibration_slope.out_of_time]].
The value of `calibration_slope.test` is 0.9369 [[art:290cccd9:calibration_slope.test]].
The value of `calibration_slope.train` is 1.015 [[art:6ee05ed8:calibration_slope.train]].
The value of `calibration_slope.vintage_holdout` is 0.8554 [[art:6b42345a:calibration_slope.vintage_holdout]].
The value of `cpr.out_of_time.mae` is 0.06724 [[art:ed058023:cpr.out_of_time.mae]].
The value of `cpr.test.mae` is 0.06724 [[art:fe0e020a:cpr.test.mae]].
The value of `cpr.train.mae` is 0.03373 [[art:609b1f19:cpr.train.mae]].
The value of `cpr.vintage_holdout.mae` is 0.03062 [[art:10b5118d:cpr.vintage_holdout.mae]].
The value of `deciles.out_of_time.top2_capture` is 0.5773 [[art:df63152b:deciles.out_of_time.top2_capture]].
The value of `deciles.test.top2_capture` is 0.5773 [[art:88c7c389:deciles.test.top2_capture]].
The value of `deciles.train.top2_capture` is 0.638 [[art:3ac2e5fd:deciles.train.top2_capture]].
The value of `deciles.vintage_holdout.top2_capture` is 0.5806 [[art:0d0c0310:deciles.vintage_holdout.top2_capture]].
The value of `metrics.out_of_time.auc` is 0.7846 [[art:ee898745:metrics.out_of_time.auc]].
The value of `metrics.out_of_time.brier` is 0.01725 [[art:f0fd020a:metrics.out_of_time.brier]].
The value of `metrics.out_of_time.event_rate` is 0.01795 [[art:83ccf5c0:metrics.out_of_time.event_rate]].
The value of `metrics.out_of_time.gini` is 0.5692 [[art:46899ec9:metrics.out_of_time.gini]].
The value of `metrics.out_of_time.ks` is 0.4373 [[art:6360ccf9:metrics.out_of_time.ks]].
The value of `metrics.out_of_time.logloss` is 0.0805 [[art:205ce509:metrics.out_of_time.logloss]].
The value of `metrics.out_of_time.mean_predicted` is 0.02283 [[art:4d7aa98b:metrics.out_of_time.mean_predicted]].
The value of `metrics.out_of_time.n` is 12257 [[art:7898809e:metrics.out_of_time.n]].
The value of `metrics.test.auc` is 0.7846 [[art:d57b2552:metrics.test.auc]].
The value of `metrics.test.brier` is 0.01725 [[art:68e8b1cf:metrics.test.brier]].
The value of `metrics.test.event_rate` is 0.01795 [[art:d222aedf:metrics.test.event_rate]].
The value of `metrics.test.gini` is 0.5692 [[art:1291e305:metrics.test.gini]].
The value of `metrics.test.ks` is 0.4373 [[art:857a0cf9:metrics.test.ks]].
The value of `metrics.test.logloss` is 0.0805 [[art:c576b630:metrics.test.logloss]].
The value of `metrics.test.mean_predicted` is 0.02283 [[art:1c1a1d8d:metrics.test.mean_predicted]].
The value of `metrics.test.n` is 12257 [[art:90b46eb1:metrics.test.n]].
The value of `metrics.train.auc` is 0.8003 [[art:41d3c4e6:metrics.train.auc]].
The value of `metrics.train.brier` is 0.008111 [[art:e9077291:metrics.train.brier]].
The value of `metrics.train.event_rate` is 0.008323 [[art:b0cf2348:metrics.train.event_rate]].
The value of `metrics.train.gini` is 0.6006 [[art:66b6cc81:metrics.train.gini]].
The value of `metrics.train.ks` is 0.474 [[art:3e0b8829:metrics.train.ks]].
The value of `metrics.train.logloss` is 0.04279 [[art:e62507ab:metrics.train.logloss]].
The value of `metrics.train.mean_predicted` is 0.008333 [[art:4ea7b930:metrics.train.mean_predicted]].
The value of `metrics.train.n` is 33522 [[art:dd20fa4c:metrics.train.n]].
The value of `metrics.vintage_holdout.auc` is 0.7716 [[art:610c13fd:metrics.vintage_holdout.auc]].
The value of `metrics.vintage_holdout.brier` is 0.004767 [[art:115af096:metrics.vintage_holdout.brier]].
The value of `metrics.vintage_holdout.event_rate` is 0.004817 [[art:e3590a16:metrics.vintage_holdout.event_rate]].
The value of `metrics.vintage_holdout.gini` is 0.5432 [[art:4b1525bb:metrics.vintage_holdout.gini]].
The value of `metrics.vintage_holdout.ks` is 0.4618 [[art:c3ac5a54:metrics.vintage_holdout.ks]].
The value of `metrics.vintage_holdout.logloss` is 0.02818 [[art:96a19aae:metrics.vintage_holdout.logloss]].
The value of `metrics.vintage_holdout.mean_predicted` is 0.006157 [[art:914aeeba:metrics.vintage_holdout.mean_predicted]].
The value of `metrics.vintage_holdout.n` is 32177 [[art:37a92951:metrics.vintage_holdout.n]].
The value of `psi.burnout` is 3.016 [[art:1d35a583:psi.burnout]].
The value of `psi.credit_score` is 0.07088 [[art:91c4ab83:psi.credit_score]].
The value of `psi.incentive` is 0.8734 [[art:0f61188c:psi.incentive]].
The value of `psi.loan_age` is 1.68 [[art:987aabe4:psi.loan_age]].
The value of `psi.max` is 3.016 [[art:4fae32c6:psi.max]].
The value of `psi.note_rate` is 1.342 [[art:2f1cb70b:psi.note_rate]].
The value of `psi.orig_ltv` is 0.04332 [[art:85842fd0:psi.orig_ltv]].
The value of `psi.orig_upb_log` is 0.08171 [[art:f075546d:psi.orig_upb_log]].
The value of `psi.out_of_time.burnout` is 3.016 [[art:8cedaf79:psi.out_of_time.burnout]].
The value of `psi.out_of_time.credit_score` is 0.07088 [[art:a7ef717f:psi.out_of_time.credit_score]].
The value of `psi.out_of_time.incentive` is 0.8734 [[art:ec6da34d:psi.out_of_time.incentive]].
The value of `psi.out_of_time.loan_age` is 1.68 [[art:ab2af3f2:psi.out_of_time.loan_age]].
The value of `psi.out_of_time.note_rate` is 1.342 [[art:fc610fd1:psi.out_of_time.note_rate]].
The value of `psi.out_of_time.orig_ltv` is 0.04332 [[art:7eedf98f:psi.out_of_time.orig_ltv]].
The value of `psi.out_of_time.orig_upb_log` is 0.08171 [[art:9ca9c306:psi.out_of_time.orig_upb_log]].
The value of `psi.out_of_time.sato` is 0.02284 [[art:79f6f94a:psi.out_of_time.sato]].
The value of `psi.out_of_time.season_cos` is 0.004988 [[art:ef947d09:psi.out_of_time.season_cos]].
The value of `psi.out_of_time.season_sin` is 0.01631 [[art:fe2b0197:psi.out_of_time.season_sin]].
The value of `psi.out_of_time.y_score` is 0.8372 [[art:d39a4ced:psi.out_of_time.y_score]].
The value of `psi.sato` is 0.02284 [[art:4809116c:psi.sato]].
The value of `psi.season_cos` is 0.004988 [[art:62ae6c81:psi.season_cos]].
The value of `psi.season_sin` is 0.01631 [[art:46fec014:psi.season_sin]].
The value of `psi.vintage_holdout.burnout` is 0.03122 [[art:b2dacb71:psi.vintage_holdout.burnout]].
The value of `psi.vintage_holdout.credit_score` is 0.01929 [[art:16906529:psi.vintage_holdout.credit_score]].
The value of `psi.vintage_holdout.incentive` is 0.2101 [[art:1d339225:psi.vintage_holdout.incentive]].
The value of `psi.vintage_holdout.loan_age` is 0.03489 [[art:e579422e:psi.vintage_holdout.loan_age]].
The value of `psi.vintage_holdout.note_rate` is 0.2743 [[art:d4e6aa9a:psi.vintage_holdout.note_rate]].
The value of `psi.vintage_holdout.orig_ltv` is 0.03575 [[art:1f0e3df0:psi.vintage_holdout.orig_ltv]].
The value of `psi.vintage_holdout.orig_upb_log` is 0.03038 [[art:10fd298a:psi.vintage_holdout.orig_upb_log]].
The value of `psi.vintage_holdout.sato` is 0.02841 [[art:6c4e561c:psi.vintage_holdout.sato]].
The value of `psi.vintage_holdout.season_cos` is 0.00164 [[art:4482dc21:psi.vintage_holdout.season_cos]].
The value of `psi.vintage_holdout.season_sin` is 0.001971 [[art:836b68bf:psi.vintage_holdout.season_sin]].
The value of `psi.vintage_holdout.y_score` is 0.08202 [[art:5d010092:psi.vintage_holdout.y_score]].
The value of `psi.y_score` is 0.8372 [[art:92ac1652:psi.y_score]].
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
Calibration by decile of predicted probability on test [[art:07848a4c:calibration.test]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.001873 | 0 | 1226 |
| 2 | 0.003677 | 0.002447 | 1226 |
| 3 | 0.005318 | 0.002447 | 1226 |
| 4 | 0.007303 | 0.0106 | 1226 |
| 5 | 0.009752 | 0.009788 | 1226 |
| 6 | 0.01306 | 0.01223 | 1226 |
| 7 | 0.01816 | 0.01142 | 1226 |
| 8 | 0.02727 | 0.02694 | 1225 |
| 9 | 0.04395 | 0.02857 | 1225 |
| 10 | 0.09799 | 0.0751 | 1225 |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table cpr.test -->
Actual against predicted CPR by period on test [[art:81cf8976:cpr.test]]:

| period | n | actual_cpr | predicted_cpr |
|---|---|---|---|
| 202001 | 515 | 0 | 0.04662 |
| 202002 | 515 | 0.04562 | 0.05737 |
| 202003 | 513 | 0 | 0.06594 |
| 202004 | 513 | 0.08966 | 0.09018 |
| 202005 | 509 | 0.06848 | 0.09956 |
| 202006 | 506 | 0.1539 | 0.1084 |
| 202007 | 499 | 0.1962 | 0.09795 |
| 202008 | 490 | 0.1158 | 0.09853 |
| 202009 | 485 | 0.04838 | 0.1064 |
| 202010 | 483 | 0.222 | 0.1265 |
| 202011 | 473 | 0.246 | 0.1732 |
| 202012 | 462 | 0.1674 | 0.2402 |
| 202101 | 455 | 0.2938 | 0.3149 |
| 202102 | 442 | 0.3204 | 0.4631 |
| 202103 | 428 | 0.3669 | 0.5622 |
| 202104 | 412 | 0.5703 | 0.6164 |
| 202105 | 384 | 0.539 | 0.6034 |
| 202106 | 360 | 0.5308 | 0.5455 |
| 202107 | 338 | 0.4412 | 0.466 |
| 202108 | 322 | 0.1712 | 0.3364 |
| 202109 | 317 | 0.1737 | 0.2921 |
| 202110 | 312 | 0.03779 | 0.2473 |
| 202111 | 311 | 0.0745 | 0.2087 |
| 202112 | 309 | 0.1105 | 0.2077 |
| 202201 | 306 | 0.1115 | 0.1809 |
| 202202 | 272 | 0.08475 | 0.1934 |
| 202203 | 244 | 0.04809 | 0.1364 |
| 202204 | 221 | 0.1513 | 0.113 |
| 202205 | 194 | 0 | 0.08172 |
| 202206 | 167 | 0.06954 | 0.05779 |
| 202207 | 145 | 0.07969 | 0.03948 |
| 202208 | 119 | 0 | 0.03001 |
| 202209 | 98 | 0 | 0.02484 |
| 202210 | 68 | 0 | 0.02792 |
| 202211 | 45 | 0 | 0.02572 |
| 202212 | 25 | 0 | 0.02416 |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table deciles.test -->
Decile separation on test; decile 1 holds the highest probabilities [[art:26b0ba93:deciles.test]]:

| decile | count | events | event_rate | lift |
|---|---|---|---|---|
| 1 | 1226 | 92 | 0.07504 | 4.181 |
| 2 | 1226 | 35 | 0.02855 | 1.591 |
| 3 | 1226 | 33 | 0.02692 | 1.5 |
| 4 | 1226 | 14 | 0.01142 | 0.6362 |
| 5 | 1226 | 15 | 0.01223 | 0.6817 |
| 6 | 1226 | 12 | 0.009788 | 0.5453 |
| 7 | 1226 | 13 | 0.0106 | 0.5908 |
| 8 | 1225 | 3 | 0.002449 | 0.1364 |
| 9 | 1225 | 3 | 0.002449 | 0.1364 |
| 10 | 1225 | 0 | 0 | 0 |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table thresholds.evaluation -->
Every threshold package.yaml declares, with its bound, the recomputed value and the outcome [[art:9aea64d5:thresholds.evaluation]]:

| metric | split | bound | value | result |
|---|---|---|---|---|
| auc | test | minimum 0.65 | 0.7846 | pass |
| calibration_slope | test | minimum 0.8 | 0.9369 | pass |
| calibration_slope | test | maximum 1.2 | 0.9369 | pass |
| psi |  | maximum 0.25 | 3.016 | fail |
<!-- quaestor:renderer:end -->
Candidates raised on this section's material: T1; C1; C1; C1 (see the findings section).

## 5. Sensitivity and scenario analysis

This section follows the model risk management guidance at [[reg:SR26-2:V.1.a]].
The value of `condition_number` is 4.778 [[art:5e2416a9:condition_number]].
The value of `scenario.convexity` is -1095000 [[art:70b14b4a:scenario.convexity]].
The value of `scenario.value_change.-100` is -171500 [[art:56c3d7c6:scenario.value_change.-100]].
The value of `scenario.value_change.-200` is -587900 [[art:fc12530a:scenario.value_change.-200]].
The value of `scenario.value_change.-300` is -1166000 [[art:dfaf9b49:scenario.value_change.-300]].
The value of `scenario.value_change.0` is 0 [[art:1e1b0b88:scenario.value_change.0]].
The value of `scenario.value_change.100` is 51210 [[art:c5393b58:scenario.value_change.100]].
The value of `scenario.value_change.200` is 66660 [[art:8b1b5955:scenario.value_change.200]].
The value of `scenario.value_change.300` is 71320 [[art:1bebd745:scenario.value_change.300]].
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
The value of `vif.burnout` is 3.601 [[art:127bbabe:vif.burnout]].
The value of `vif.credit_score` is 1.011 [[art:1f19769b:vif.credit_score]].
The value of `vif.incentive` is 2.195 [[art:60c8eef8:vif.incentive]].
The value of `vif.loan_age` is 2.593 [[art:b30f78aa:vif.loan_age]].
The value of `vif.max` is 4.288 [[art:fecfb289:vif.max]].
The value of `vif.note_rate` is 4.288 [[art:1113d019:vif.note_rate]].
The value of `vif.orig_ltv` is 1.014 [[art:d9449fe2:vif.orig_ltv]].
The value of `vif.orig_upb_log` is 1.012 [[art:59e2ab98:vif.orig_upb_log]].
The value of `vif.sato` is 1.627 [[art:4b2ebef2:vif.sato]].
The value of `vif.season_cos` is 1.007 [[art:f741ba51:vif.season_cos]].
The value of `vif.season_sin` is 1.011 [[art:3b05b05a:vif.season_sin]].
<!-- quaestor:renderer:begin table scenario.value_by_shock -->
Servicing value, its change from the base case and first-year CPR, by shock [[art:7ca37cab:scenario.value_by_shock]]:

| shock_bp | value | value_change | cpr |
|---|---|---|---|
| -300 | 529900 | -1.166e+06 | 0.5407 |
| -200 | 1.108e+06 | -587900 | 0.2095 |
| -100 | 1.525e+06 | -171500 | 0.06584 |
| 0 | 1.696e+06 | 0 | 0.01955 |
| 100 | 1.747e+06 | 51210 | 0.005826 |
| 200 | 1.763e+06 | 66660 | 0.001738 |
| 300 | 1.767e+06 | 71320 | 0.0005173 |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table stability.auc_by_regime -->
The champion's AUC within each rate_regime on train [[art:3b0ee961:stability.auc_by_regime]]:

| regime | n | event_rate | auc |
|---|---|---|---|
| falling | 16370 | 0.01411 | 0.7415 |
| rising | 17152 | 0.002799 | 0.7306 |
<!-- quaestor:renderer:end -->

## 6. Findings and recommendations

This section follows the model risk management guidance at [[reg:SR26-2:VI.3]].

### F-001 · T1 declared threshold · severity **high**

**A `T1` finding, raised by `compute_metrics` at severity `high`.**
Its evidence is the artifacts cited in this section; the check's own account of it is recorded in `findings.json`.

### F-002 · S1 population drift · severity **medium**

**A `S1` finding, raised by `profile_data` at severity `medium`.**
Its evidence is the artifacts cited in this section; the check's own account of it is recorded in `findings.json`.

### F-003 · C1 calibration · severity **medium**

**A `C1` finding, raised by `compute_metrics` at severity `medium`.**
Its evidence is the artifacts cited in this section; the check's own account of it is recorded in `findings.json`.
The value of `calibration.mean_rel_gap.out_of_time` is 0.2718 [[art:c5239af4:calibration.mean_rel_gap.out_of_time]].
The value of `calibration.mean_rel_gap.test` is 0.2718 [[art:04dcea16:calibration.mean_rel_gap.test]].
The value of `calibration.mean_rel_gap.vintage_holdout` is 0.2782 [[art:2eba48c2:calibration.mean_rel_gap.vintage_holdout]].
The value of `metrics.out_of_time.event_rate` is 0.01795 [[art:83ccf5c0:metrics.out_of_time.event_rate]].
The value of `metrics.out_of_time.mean_predicted` is 0.02283 [[art:4d7aa98b:metrics.out_of_time.mean_predicted]].
The value of `metrics.test.event_rate` is 0.01795 [[art:d222aedf:metrics.test.event_rate]].
The value of `metrics.test.mean_predicted` is 0.02283 [[art:1c1a1d8d:metrics.test.mean_predicted]].
The value of `metrics.vintage_holdout.event_rate` is 0.004817 [[art:e3590a16:metrics.vintage_holdout.event_rate]].
The value of `metrics.vintage_holdout.mean_predicted` is 0.006157 [[art:914aeeba:metrics.vintage_holdout.mean_predicted]].
The value of `psi.burnout` is 3.016 [[art:1d35a583:psi.burnout]].
The value of `psi.incentive` is 0.8734 [[art:0f61188c:psi.incentive]].
The value of `psi.loan_age` is 1.68 [[art:987aabe4:psi.loan_age]].
The value of `psi.max` is 3.016 [[art:4fae32c6:psi.max]].
The value of `psi.note_rate` is 1.342 [[art:2f1cb70b:psi.note_rate]].
The value of `psi.y_score` is 0.8372 [[art:92ac1652:psi.y_score]].
The value of `sign_check.note_rate.agrees` is 0 [[art:a453463d:sign_check.note_rate.agrees]].
The value of `sign_check.note_rate.coef_sign` is -1 [[art:aecf7ccb:sign_check.note_rate.coef_sign]].
The value of `sign_check.note_rate.univariate_direction` is 1 [[art:61f6e1ac:sign_check.note_rate.univariate_direction]].
The value of `threshold.C1.mean_ratio_rel` is 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
The value of `threshold.S1.psi` is 0.25 [[art:278b9016:threshold.S1.psi]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
<!-- quaestor:renderer:begin table calibration.out_of_time -->
Calibration by decile of predicted probability on out_of_time [[art:a16e1248:calibration.out_of_time]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.001873 | 0 | 1226 |
| 2 | 0.003677 | 0.002447 | 1226 |
| 3 | 0.005318 | 0.002447 | 1226 |
| 4 | 0.007303 | 0.0106 | 1226 |
| 5 | 0.009752 | 0.009788 | 1226 |
| 6 | 0.01306 | 0.01223 | 1226 |
| 7 | 0.01816 | 0.01142 | 1226 |
| 8 | 0.02727 | 0.02694 | 1225 |
| 9 | 0.04395 | 0.02857 | 1225 |
| 10 | 0.09799 | 0.0751 | 1225 |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table calibration.test -->
Calibration by decile of predicted probability on test [[art:07848a4c:calibration.test]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.001873 | 0 | 1226 |
| 2 | 0.003677 | 0.002447 | 1226 |
| 3 | 0.005318 | 0.002447 | 1226 |
| 4 | 0.007303 | 0.0106 | 1226 |
| 5 | 0.009752 | 0.009788 | 1226 |
| 6 | 0.01306 | 0.01223 | 1226 |
| 7 | 0.01816 | 0.01142 | 1226 |
| 8 | 0.02727 | 0.02694 | 1225 |
| 9 | 0.04395 | 0.02857 | 1225 |
| 10 | 0.09799 | 0.0751 | 1225 |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table calibration.vintage_holdout -->
Calibration by decile of predicted probability on vintage_holdout [[art:a402f077:calibration.vintage_holdout]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.0004637 | 0.001243 | 3218 |
| 2 | 0.0008609 | 0.001554 | 3218 |
| 3 | 0.001234 | 0.0003108 | 3218 |
| 4 | 0.001671 | 0.001554 | 3218 |
| 5 | 0.002261 | 0.001865 | 3218 |
| 6 | 0.003137 | 0.002797 | 3218 |
| 7 | 0.004596 | 0.002486 | 3218 |
| 8 | 0.007083 | 0.008393 | 3217 |
| 9 | 0.01187 | 0.008082 | 3217 |
| 10 | 0.02841 | 0.01989 | 3217 |
<!-- quaestor:renderer:end -->

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1), `compute_metrics` (O1), `check_leakage` (L1, L2), `check_stability` (R1), `check_collinearity` (M1), `challenger_compare` (E1), `run_scenarios` (X1).

### Open items

No open item was recorded for this validation.

## 7. Ongoing monitoring recommendations

This section follows the model risk management guidance at [[reg:SR26-2:V.2]].
The value of `calibration_slope.test` is 0.9369 [[art:290cccd9:calibration_slope.test]].
The value of `metrics.test.auc` is 0.7846 [[art:d57b2552:metrics.test.auc]].
The value of `psi.max` is 3.016 [[art:4fae32c6:psi.max]].
The value of `rule.calibration_first_event_rate` is 0.05 [[art:42f1351e:rule.calibration_first_event_rate]].
The value of `threshold.package.auc.test.min` is 0.65 [[art:fececac1:threshold.package.auc.test.min]].
The value of `threshold.package.calibration_slope.test.max` is 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The value of `threshold.package.calibration_slope.test.min` is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].

## Appendix A — Claims

Grounding precision 1.0000 before repair (329 of 329 claims verified) and 1.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 48/48; conceptual_soundness 45/45; data_integrity 66/66; outcomes 106/106; sensitivity 35/35; findings 21/21; monitoring 8/8.

Developer claims: The package declares 3 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). See Appendix D.

Excluded numeric tokens (not claims): inline_code (`scenario.value_change.-100`, `scenario.value_change.-200`, `scenario.value_change.-300`); citation_hash (994798d5, 290cccd9, 6ee05ed8, 6b42345a); regulatory_section_id (SR26-2:V.1.b, SR26-2:V.1.a, SR26-2:VI.3, SR26-2:V.2); finding_id (F-001, F-002, F-003).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The value of `calibration_slope.out_of_time` is 0.9369 . | 0.9369 | ratio | calibration_slope |  | eq | `[[art:994798d5:calibration_slope.out_of_time]]` | verified | 0.9368866293 |
| 2 | summary | The value of `calibration_slope.test` is 0.9369 . | 0.9369 | ratio | calibration_slope |  | eq | `[[art:290cccd9:calibration_slope.test]]` | verified | 0.9368866293 |
| 3 | summary | The value of `calibration_slope.train` is 1.015 . | 1.015 | ratio | calibration_slope |  | eq | `[[art:6ee05ed8:calibration_slope.train]]` | verified | 1.015165743 |
| 4 | summary | The value of `calibration_slope.vintage_holdout` is 0.8554 . | 0.8554 | ratio | calibration_slope |  | eq | `[[art:6b42345a:calibration_slope.vintage_holdout]]` | verified | 0.8553956316 |
| 5 | summary | The value of `challenger.delta_auc` is -0.06356 . | -0.06356 | ratio | challenger |  | eq | `[[art:7e119a34:challenger.delta_auc]]` | verified | -0.06356159418 |
| 6 | summary | The value of `condition_number` is 4.778 . | 4.778 | ratio | condition_number |  | eq | `[[art:5e2416a9:condition_number]]` | verified | 4.777601017 |
| 7 | summary | The value of `csi.max` is 0.9221 . | 0.9221 | ratio | csi |  | eq | `[[art:d4b08859:csi.max]]` | verified | 0.9220903461 |
| 8 | summary | The value of `metrics.out_of_time.auc` is 0.7846 . | 0.7846 | ratio | metrics |  | eq | `[[art:ee898745:metrics.out_of_time.auc]]` | verified | 0.7846182604 |
| 9 | summary | The value of `metrics.out_of_time.brier` is 0.01725 . | 0.01725 | ratio | metrics |  | eq | `[[art:f0fd020a:metrics.out_of_time.brier]]` | verified | 0.01725186302 |
| 10 | summary | The value of `metrics.out_of_time.event_rate` is 0.01795 . | 0.01795 | ratio | metrics |  | eq | `[[art:83ccf5c0:metrics.out_of_time.event_rate]]` | verified | 0.01794892714 |
| 11 | summary | The value of `metrics.out_of_time.gini` is 0.5692 . | 0.5692 | ratio | metrics |  | eq | `[[art:46899ec9:metrics.out_of_time.gini]]` | verified | 0.5692365207 |
| 12 | summary | The value of `metrics.out_of_time.ks` is 0.4373 . | 0.4373 | ratio | metrics |  | eq | `[[art:6360ccf9:metrics.out_of_time.ks]]` | verified | 0.4373216673 |
| 13 | summary | The value of `metrics.out_of_time.logloss` is 0.0805 . | 0.0805 | ratio | metrics |  | eq | `[[art:205ce509:metrics.out_of_time.logloss]]` | verified | 0.08050056271 |
| 14 | summary | The value of `metrics.out_of_time.mean_predicted` is 0.02283… | 0.02283 | ratio | metrics |  | eq | `[[art:4d7aa98b:metrics.out_of_time.mean_predicted]]` | verified | 0.02282661269 |
| 15 | summary | The value of `metrics.out_of_time.n` is 12257 . | 12257 | ratio | metrics |  | eq | `[[art:7898809e:metrics.out_of_time.n]]` | verified | 12257 |
| 16 | summary | The value of `metrics.test.auc` is 0.7846 . | 0.7846 | ratio | metrics |  | eq | `[[art:d57b2552:metrics.test.auc]]` | verified | 0.7846182604 |
| 17 | summary | The value of `metrics.test.brier` is 0.01725 . | 0.01725 | ratio | metrics |  | eq | `[[art:68e8b1cf:metrics.test.brier]]` | verified | 0.01725186302 |
| 18 | summary | The value of `metrics.test.event_rate` is 0.01795 . | 0.01795 | ratio | metrics |  | eq | `[[art:d222aedf:metrics.test.event_rate]]` | verified | 0.01794892714 |
| 19 | summary | The value of `metrics.test.gini` is 0.5692 . | 0.5692 | ratio | metrics |  | eq | `[[art:1291e305:metrics.test.gini]]` | verified | 0.5692365207 |
| 20 | summary | The value of `metrics.test.ks` is 0.4373 . | 0.4373 | ratio | metrics |  | eq | `[[art:857a0cf9:metrics.test.ks]]` | verified | 0.4373216673 |
| 21 | summary | The value of `metrics.test.logloss` is 0.0805 . | 0.0805 | ratio | metrics |  | eq | `[[art:c576b630:metrics.test.logloss]]` | verified | 0.08050056271 |
| 22 | summary | The value of `metrics.test.mean_predicted` is 0.02283 . | 0.02283 | ratio | metrics |  | eq | `[[art:1c1a1d8d:metrics.test.mean_predicted]]` | verified | 0.02282661269 |
| 23 | summary | The value of `metrics.test.n` is 12257 . | 12257 | ratio | metrics |  | eq | `[[art:90b46eb1:metrics.test.n]]` | verified | 12257 |
| 24 | summary | The value of `metrics.train.auc` is 0.8003 . | 0.8003 | ratio | metrics |  | eq | `[[art:41d3c4e6:metrics.train.auc]]` | verified | 0.8002919094 |
| 25 | summary | The value of `metrics.train.brier` is 0.008111 . | 0.008111 | ratio | metrics |  | eq | `[[art:e9077291:metrics.train.brier]]` | verified | 0.008111422906 |
| 26 | summary | The value of `metrics.train.event_rate` is 0.008323 . | 0.008323 | ratio | metrics |  | eq | `[[art:b0cf2348:metrics.train.event_rate]]` | verified | 0.008322892429 |
| 27 | summary | The value of `metrics.train.gini` is 0.6006 . | 0.6006 | ratio | metrics |  | eq | `[[art:66b6cc81:metrics.train.gini]]` | verified | 0.6005838187 |
| 28 | summary | The value of `metrics.train.ks` is 0.474 . | 0.474 | ratio | metrics |  | eq | `[[art:3e0b8829:metrics.train.ks]]` | verified | 0.4740174906 |
| 29 | summary | The value of `metrics.train.logloss` is 0.04279 . | 0.04279 | ratio | metrics |  | eq | `[[art:e62507ab:metrics.train.logloss]]` | verified | 0.04279363896 |
| 30 | summary | The value of `metrics.train.mean_predicted` is 0.008333 . | 0.008333 | ratio | metrics |  | eq | `[[art:4ea7b930:metrics.train.mean_predicted]]` | verified | 0.008332856538 |
| 31 | summary | The value of `metrics.train.n` is 33522 . | 33522 | ratio | metrics |  | eq | `[[art:dd20fa4c:metrics.train.n]]` | verified | 33522 |
| 32 | summary | The value of `metrics.vintage_holdout.auc` is 0.7716 . | 0.7716 | ratio | metrics |  | eq | `[[art:610c13fd:metrics.vintage_holdout.auc]]` | verified | 0.7716058113 |
| 33 | summary | The value of `metrics.vintage_holdout.brier` is 0.004767 . | 0.004767 | ratio | metrics |  | eq | `[[art:115af096:metrics.vintage_holdout.brier]]` | verified | 0.004766820283 |
| 34 | summary | The value of `metrics.vintage_holdout.event_rate` is 0.00481… | 0.004817 | ratio | metrics |  | eq | `[[art:e3590a16:metrics.vintage_holdout.event_rate]]` | verified | 0.004817105386 |
| 35 | summary | The value of `metrics.vintage_holdout.gini` is 0.5432 . | 0.5432 | ratio | metrics |  | eq | `[[art:4b1525bb:metrics.vintage_holdout.gini]]` | verified | 0.5432116227 |
| 36 | summary | The value of `metrics.vintage_holdout.ks` is 0.4618 . | 0.4618 | ratio | metrics |  | eq | `[[art:c3ac5a54:metrics.vintage_holdout.ks]]` | verified | 0.4617647948 |
| 37 | summary | The value of `metrics.vintage_holdout.logloss` is 0.02818 . | 0.02818 | ratio | metrics |  | eq | `[[art:96a19aae:metrics.vintage_holdout.logloss]]` | verified | 0.02818314174 |
| 38 | summary | The value of `metrics.vintage_holdout.mean_predicted` is 0.0… | 0.006157 | ratio | metrics |  | eq | `[[art:914aeeba:metrics.vintage_holdout.mean_predicted]]` | verified | 0.006157456637 |
| 39 | summary | The value of `metrics.vintage_holdout.n` is 32177 . | 32177 | ratio | metrics |  | eq | `[[art:37a92951:metrics.vintage_holdout.n]]` | verified | 32177 |
| 40 | summary | The value of `profile.test.n` is 12257 . | 12257 | ratio | profile |  | eq | `[[art:3b91ffcc:profile.test.n]]` | verified | 12257 |
| 41 | summary | The value of `profile.train.n` is 33522 . | 33522 | ratio | profile |  | eq | `[[art:60d3a086:profile.train.n]]` | verified | 33522 |
| 42 | summary | The value of `psi.max` is 3.016 . | 3.016 | ratio | psi |  | eq | `[[art:4fae32c6:psi.max]]` | verified | 3.016020048 |
| 43 | summary | The value of `runtime.max_seconds` is 300 . | 300 | ratio | runtime |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 44 | summary | The value of `threshold.package.auc.test.min` is 0.65 . | 0.65 | ratio | threshold |  | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 45 | summary | The value of `threshold.package.calibration_slope.test.max`… | 1.2 | ratio | threshold |  | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 46 | summary | The value of `threshold.package.calibration_slope.test.min`… | 0.8 | ratio | threshold |  | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 47 | summary | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 48 | summary | The value of `vif.max` is 4.288 . | 4.288 | ratio | vif |  | eq | `[[art:fecfb289:vif.max]]` | verified | 4.288168629 |
| 49 | conceptual_soundness | The value of `ablation.baseline_auc` is 0.7802 . | 0.7802 | ratio | ablation |  | eq | `[[art:93dda83a:ablation.baseline_auc]]` | verified | 0.7802163028 |
| 50 | conceptual_soundness | The value of `ablation.burnout.delta_auc` is 0.004292 . | 0.004292 | ratio | ablation |  | eq | `[[art:8aa8bccf:ablation.burnout.delta_auc]]` | verified | 0.00429206915 |
| 51 | conceptual_soundness | The value of `ablation.credit_score.delta_auc` is -0.0298 . | -0.0298 | ratio | ablation |  | eq | `[[art:a2d10cd7:ablation.credit_score.delta_auc]]` | verified | -0.02980393786 |
| 52 | conceptual_soundness | The value of `ablation.incentive.delta_auc` is -0.07943 . | -0.07943 | ratio | ablation |  | eq | `[[art:46802ce1:ablation.incentive.delta_auc]]` | verified | -0.07943499966 |
| 53 | conceptual_soundness | The value of `ablation.loan_age.delta_auc` is -0.009946 . | -0.009946 | ratio | ablation |  | eq | `[[art:ca8fa8e9:ablation.loan_age.delta_auc]]` | verified | -0.009945848784 |
| 54 | conceptual_soundness | The value of `ablation.note_rate.delta_auc` is 0.005792 . | 0.005792 | ratio | ablation |  | eq | `[[art:338b461a:ablation.note_rate.delta_auc]]` | verified | 0.005792367473 |
| 55 | conceptual_soundness | The value of `ablation.orig_ltv.delta_auc` is -0.01199 . | -0.01199 | ratio | ablation |  | eq | `[[art:84275e57:ablation.orig_ltv.delta_auc]]` | verified | -0.01199332362 |
| 56 | conceptual_soundness | The value of `ablation.orig_upb_log.delta_auc` is -0.01681 . | -0.01681 | ratio | ablation |  | eq | `[[art:6158bf75:ablation.orig_upb_log.delta_auc]]` | verified | -0.01681104473 |
| 57 | conceptual_soundness | The value of `ablation.sato.delta_auc` is -0.004237 . | -0.004237 | ratio | ablation |  | eq | `[[art:c9eb03ef:ablation.sato.delta_auc]]` | verified | -0.004237313737 |
| 58 | conceptual_soundness | The value of `ablation.season_cos.delta_auc` is -0.005672 . | -0.005672 | ratio | ablation |  | eq | `[[art:bdbbba37:ablation.season_cos.delta_auc]]` | verified | -0.005672283187 |
| 59 | conceptual_soundness | The value of `ablation.season_sin.delta_auc` is 0.00054 . | 0.00054 | ratio | ablation |  | eq | `[[art:95e1e0c6:ablation.season_sin.delta_auc]]` | verified | 0.0005400016615 |
| 60 | conceptual_soundness | The value of `challenger.auc` is 0.7211 . | 0.7211 | ratio | challenger |  | eq | `[[art:489cd7a6:challenger.auc]]` | verified | 0.7210566662 |
| 61 | conceptual_soundness | The value of `challenger.brier` is 0.02173 . | 0.02173 | ratio | challenger |  | eq | `[[art:36aa75c4:challenger.brier]]` | verified | 0.02173012265 |
| 62 | conceptual_soundness | The value of `challenger.delta_auc` is -0.06356 . | -0.06356 | ratio | challenger |  | eq | `[[art:7e119a34:challenger.delta_auc]]` | verified | -0.06356159418 |
| 63 | conceptual_soundness | The value of `metrics.test.auc` is 0.7846 . | 0.7846 | ratio | metrics |  | eq | `[[art:d57b2552:metrics.test.auc]]` | verified | 0.7846182604 |
| 64 | conceptual_soundness | The value of `metrics.test.brier` is 0.01725 . | 0.01725 | ratio | metrics |  | eq | `[[art:68e8b1cf:metrics.test.brier]]` | verified | 0.01725186302 |
| 65 | conceptual_soundness | The value of `sign_check.burnout.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:2eec20ab:sign_check.burnout.agrees]]` | verified | 1 |
| 66 | conceptual_soundness | The value of `sign_check.burnout.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:a3063608:sign_check.burnout.coef_sign]]` | verified | 1 |
| 67 | conceptual_soundness | The value of `sign_check.burnout.univariate_direction` is 1… | 1 | ratio | sign_check |  | eq | `[[art:bfc96bb2:sign_check.burnout.univariate_direction]]` | verified | 1 |
| 68 | conceptual_soundness | The value of `sign_check.credit_score.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:915bf8eb:sign_check.credit_score.agrees]]` | verified | 1 |
| 69 | conceptual_soundness | The value of `sign_check.credit_score.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:1ec1078b:sign_check.credit_score.coef_sign]]` | verified | 1 |
| 70 | conceptual_soundness | The value of `sign_check.credit_score.univariate_direction`… | 1 | ratio | sign_check |  | eq | `[[art:42303896:sign_check.credit_score.univariate_direction]]` | verified | 1 |
| 71 | conceptual_soundness | The value of `sign_check.incentive.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:f7b2338e:sign_check.incentive.agrees]]` | verified | 1 |
| 72 | conceptual_soundness | The value of `sign_check.incentive.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:684cf11a:sign_check.incentive.coef_sign]]` | verified | 1 |
| 73 | conceptual_soundness | The value of `sign_check.incentive.univariate_direction` is… | 1 | ratio | sign_check |  | eq | `[[art:8098d951:sign_check.incentive.univariate_direction]]` | verified | 1 |
| 74 | conceptual_soundness | The value of `sign_check.n_disagreements` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:f96ece96:sign_check.n_disagreements]]` | verified | 1 |
| 75 | conceptual_soundness | The value of `sign_check.note_rate.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:a453463d:sign_check.note_rate.agrees]]` | verified | 0 |
| 76 | conceptual_soundness | The value of `sign_check.note_rate.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:aecf7ccb:sign_check.note_rate.coef_sign]]` | verified | -1 |
| 77 | conceptual_soundness | The value of `sign_check.note_rate.univariate_direction` is… | 1 | ratio | sign_check |  | eq | `[[art:61f6e1ac:sign_check.note_rate.univariate_direction]]` | verified | 1 |
| 78 | conceptual_soundness | The value of `sign_check.orig_ltv.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:7021aeb0:sign_check.orig_ltv.agrees]]` | verified | 1 |
| 79 | conceptual_soundness | The value of `sign_check.orig_ltv.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:7eec65ec:sign_check.orig_ltv.coef_sign]]` | verified | -1 |
| 80 | conceptual_soundness | The value of `sign_check.orig_ltv.univariate_direction` is -… | -1 | ratio | sign_check |  | eq | `[[art:76dbc708:sign_check.orig_ltv.univariate_direction]]` | verified | -1 |
| 81 | conceptual_soundness | The value of `sign_check.orig_upb_log.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:07a9d3e6:sign_check.orig_upb_log.agrees]]` | verified | 1 |
| 82 | conceptual_soundness | The value of `sign_check.orig_upb_log.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:5aa309fc:sign_check.orig_upb_log.coef_sign]]` | verified | 1 |
| 83 | conceptual_soundness | The value of `sign_check.orig_upb_log.univariate_direction`… | 1 | ratio | sign_check |  | eq | `[[art:b9743ecb:sign_check.orig_upb_log.univariate_direction]]` | verified | 1 |
| 84 | conceptual_soundness | The value of `sign_check.sato.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:2401eba2:sign_check.sato.agrees]]` | verified | 1 |
| 85 | conceptual_soundness | The value of `sign_check.sato.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:c031d0d5:sign_check.sato.coef_sign]]` | verified | 1 |
| 86 | conceptual_soundness | The value of `sign_check.sato.univariate_direction` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:c08233a6:sign_check.sato.univariate_direction]]` | verified | 1 |
| 87 | conceptual_soundness | The value of `sign_check.season_cos.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:7f18ddf7:sign_check.season_cos.agrees]]` | verified | 1 |
| 88 | conceptual_soundness | The value of `sign_check.season_cos.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:7dbb1ffc:sign_check.season_cos.coef_sign]]` | verified | -1 |
| 89 | conceptual_soundness | The value of `sign_check.season_cos.univariate_direction` is… | -1 | ratio | sign_check |  | eq | `[[art:03e931f0:sign_check.season_cos.univariate_direction]]` | verified | -1 |
| 90 | conceptual_soundness | The value of `sign_check.season_sin.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:e110f357:sign_check.season_sin.agrees]]` | verified | 1 |
| 91 | conceptual_soundness | The value of `sign_check.season_sin.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:761188ce:sign_check.season_sin.coef_sign]]` | verified | 1 |
| 92 | conceptual_soundness | The value of `sign_check.season_sin.univariate_direction` is… | 1 | ratio | sign_check |  | eq | `[[art:cae6b096:sign_check.season_sin.univariate_direction]]` | verified | 1 |
| 93 | conceptual_soundness | The value of `threshold.E1.delta_auc` is 0.03 . | 0.03 | ratio | threshold |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 94 | data_integrity | The value of `csi.burnout` is 0.3489 . | 0.3489 | ratio | csi |  | eq | `[[art:e0f86ff2:csi.burnout]]` | verified | 0.3488802555 |
| 95 | data_integrity | The value of `csi.credit_score` is 0.09087 . | 0.09087 | ratio | csi |  | eq | `[[art:4fbc434e:csi.credit_score]]` | verified | 0.09086513179 |
| 96 | data_integrity | The value of `csi.incentive` is 0.9221 . | 0.9221 | ratio | csi |  | eq | `[[art:f430cc2d:csi.incentive]]` | verified | 0.9220903461 |
| 97 | data_integrity | The value of `csi.loan_age` is 0 . | 0 | ratio | csi |  | eq | `[[art:df52c920:csi.loan_age]]` | verified | 0 |
| 98 | data_integrity | The value of `csi.max` is 0.9221 . | 0.9221 | ratio | csi |  | eq | `[[art:d4b08859:csi.max]]` | verified | 0.9220903461 |
| 99 | data_integrity | The value of `csi.note_rate` is 0.4832 . | 0.4832 | ratio | csi |  | eq | `[[art:a2be3f30:csi.note_rate]]` | verified | 0.4831662682 |
| 100 | data_integrity | The value of `csi.orig_ltv` is 0.02303 . | 0.02303 | ratio | csi |  | eq | `[[art:af80429c:csi.orig_ltv]]` | verified | 0.02302783458 |
| 101 | data_integrity | The value of `csi.orig_upb_log` is 0.06562 . | 0.06562 | ratio | csi |  | eq | `[[art:ba82e949:csi.orig_upb_log]]` | verified | 0.06561601038 |
| 102 | data_integrity | The value of `csi.sato` is 0.0001468 . | 0.0001468 | ratio | csi |  | eq | `[[art:7d563a3f:csi.sato]]` | verified | 0.0001467991037 |
| 103 | data_integrity | The value of `csi.season_cos` is 0.003265 . | 0.003265 | ratio | csi |  | eq | `[[art:49e6d56e:csi.season_cos]]` | verified | 0.003265173321 |
| 104 | data_integrity | The value of `csi.season_sin` is 0.01316 . | 0.01316 | ratio | csi |  | eq | `[[art:ff10caf4:csi.season_sin]]` | verified | 0.01315757493 |
| 105 | data_integrity | The value of `leakage.duplicates.train` is 0 . | 0 | ratio | leakage |  | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 106 | data_integrity | The value of `leakage.name_screen.n_matched` is 0 . | 0 | ratio | leakage |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 107 | data_integrity | The value of `leakage.overlap` is 0 . | 0 | ratio | leakage |  | eq | `[[art:4c9fcd09:leakage.overlap]]` | verified | 0 |
| 108 | data_integrity | The value of `leakage.overlap.features` is 0 . | 0 | ratio | leakage |  | eq | `[[art:0fec8048:leakage.overlap.features]]` | verified | 0 |
| 109 | data_integrity | The value of `leakage.overlap.ids` is 0 . | 0 | ratio | leakage |  | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 110 | data_integrity | The value of `leakage.target_corr.max_single_feature_auc` is… | 0.7422 | ratio | leakage |  | eq | `[[art:b6b29a14:leakage.target_corr.max_single_feature_auc]]` | verified | 0.7422083739 |
| 111 | data_integrity | The value of `leakage.timing.n_flagged` is 0 . | 0 | ratio | leakage |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 112 | data_integrity | The value of `profile.out_of_time.missing.max` is 0 . | 0 | ratio | profile |  | eq | `[[art:4dafce11:profile.out_of_time.missing.max]]` | verified | 0 |
| 113 | data_integrity | The value of `profile.out_of_time.n` is 12257 . | 12257 | ratio | profile |  | eq | `[[art:fa39c5cf:profile.out_of_time.n]]` | verified | 12257 |
| 114 | data_integrity | The value of `profile.test.missing.max` is 0 . | 0 | ratio | profile |  | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 115 | data_integrity | The value of `profile.test.n` is 12257 . | 12257 | ratio | profile |  | eq | `[[art:3b91ffcc:profile.test.n]]` | verified | 12257 |
| 116 | data_integrity | The value of `profile.train.missing.max` is 0 . | 0 | ratio | profile |  | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 117 | data_integrity | The value of `profile.train.n` is 33522 . | 33522 | ratio | profile |  | eq | `[[art:60d3a086:profile.train.n]]` | verified | 33522 |
| 118 | data_integrity | The value of `profile.vintage_holdout.missing.max` is 0 . | 0 | ratio | profile |  | eq | `[[art:329bb430:profile.vintage_holdout.missing.max]]` | verified | 0 |
| 119 | data_integrity | The value of `profile.vintage_holdout.n` is 32177 . | 32177 | ratio | profile |  | eq | `[[art:426e712a:profile.vintage_holdout.n]]` | verified | 32177 |
| 120 | data_integrity | The value of `psi.burnout` is 3.016 . | 3.016 | ratio | psi |  | eq | `[[art:1d35a583:psi.burnout]]` | verified | 3.016020048 |
| 121 | data_integrity | The value of `psi.credit_score` is 0.07088 . | 0.07088 | ratio | psi |  | eq | `[[art:91c4ab83:psi.credit_score]]` | verified | 0.07088355626 |
| 122 | data_integrity | The value of `psi.incentive` is 0.8734 . | 0.8734 | ratio | psi |  | eq | `[[art:0f61188c:psi.incentive]]` | verified | 0.8734495361 |
| 123 | data_integrity | The value of `psi.loan_age` is 1.68 . | 1.68 | ratio | psi |  | eq | `[[art:987aabe4:psi.loan_age]]` | verified | 1.679868562 |
| 124 | data_integrity | The value of `psi.max` is 3.016 . | 3.016 | ratio | psi |  | eq | `[[art:4fae32c6:psi.max]]` | verified | 3.016020048 |
| 125 | data_integrity | The value of `psi.note_rate` is 1.342 . | 1.342 | ratio | psi |  | eq | `[[art:2f1cb70b:psi.note_rate]]` | verified | 1.341893523 |
| 126 | data_integrity | The value of `psi.orig_ltv` is 0.04332 . | 0.04332 | ratio | psi |  | eq | `[[art:85842fd0:psi.orig_ltv]]` | verified | 0.04331914243 |
| 127 | data_integrity | The value of `psi.orig_upb_log` is 0.08171 . | 0.08171 | ratio | psi |  | eq | `[[art:f075546d:psi.orig_upb_log]]` | verified | 0.08171063787 |
| 128 | data_integrity | The value of `psi.out_of_time.burnout` is 3.016 . | 3.016 | ratio | psi |  | eq | `[[art:8cedaf79:psi.out_of_time.burnout]]` | verified | 3.016020048 |
| 129 | data_integrity | The value of `psi.out_of_time.credit_score` is 0.07088 . | 0.07088 | ratio | psi |  | eq | `[[art:a7ef717f:psi.out_of_time.credit_score]]` | verified | 0.07088355626 |
| 130 | data_integrity | The value of `psi.out_of_time.incentive` is 0.8734 . | 0.8734 | ratio | psi |  | eq | `[[art:ec6da34d:psi.out_of_time.incentive]]` | verified | 0.8734495361 |
| 131 | data_integrity | The value of `psi.out_of_time.loan_age` is 1.68 . | 1.68 | ratio | psi |  | eq | `[[art:ab2af3f2:psi.out_of_time.loan_age]]` | verified | 1.679868562 |
| 132 | data_integrity | The value of `psi.out_of_time.note_rate` is 1.342 . | 1.342 | ratio | psi |  | eq | `[[art:fc610fd1:psi.out_of_time.note_rate]]` | verified | 1.341893523 |
| 133 | data_integrity | The value of `psi.out_of_time.orig_ltv` is 0.04332 . | 0.04332 | ratio | psi |  | eq | `[[art:7eedf98f:psi.out_of_time.orig_ltv]]` | verified | 0.04331914243 |
| 134 | data_integrity | The value of `psi.out_of_time.orig_upb_log` is 0.08171 . | 0.08171 | ratio | psi |  | eq | `[[art:9ca9c306:psi.out_of_time.orig_upb_log]]` | verified | 0.08171063787 |
| 135 | data_integrity | The value of `psi.out_of_time.sato` is 0.02284 . | 0.02284 | ratio | psi |  | eq | `[[art:79f6f94a:psi.out_of_time.sato]]` | verified | 0.02284102604 |
| 136 | data_integrity | The value of `psi.out_of_time.season_cos` is 0.004988 . | 0.004988 | ratio | psi |  | eq | `[[art:ef947d09:psi.out_of_time.season_cos]]` | verified | 0.004987781308 |
| 137 | data_integrity | The value of `psi.out_of_time.season_sin` is 0.01631 . | 0.01631 | ratio | psi |  | eq | `[[art:fe2b0197:psi.out_of_time.season_sin]]` | verified | 0.01631255179 |
| 138 | data_integrity | The value of `psi.out_of_time.y_score` is 0.8372 . | 0.8372 | ratio | psi |  | eq | `[[art:d39a4ced:psi.out_of_time.y_score]]` | verified | 0.8371883582 |
| 139 | data_integrity | The value of `psi.sato` is 0.02284 . | 0.02284 | ratio | psi |  | eq | `[[art:4809116c:psi.sato]]` | verified | 0.02284102604 |
| 140 | data_integrity | The value of `psi.season_cos` is 0.004988 . | 0.004988 | ratio | psi |  | eq | `[[art:62ae6c81:psi.season_cos]]` | verified | 0.004987781308 |
| 141 | data_integrity | The value of `psi.season_sin` is 0.01631 . | 0.01631 | ratio | psi |  | eq | `[[art:46fec014:psi.season_sin]]` | verified | 0.01631255179 |
| 142 | data_integrity | The value of `psi.vintage_holdout.burnout` is 0.03122 . | 0.03122 | ratio | psi |  | eq | `[[art:b2dacb71:psi.vintage_holdout.burnout]]` | verified | 0.03122017454 |
| 143 | data_integrity | The value of `psi.vintage_holdout.credit_score` is 0.01929 . | 0.01929 | ratio | psi |  | eq | `[[art:16906529:psi.vintage_holdout.credit_score]]` | verified | 0.01928865688 |
| 144 | data_integrity | The value of `psi.vintage_holdout.incentive` is 0.2101 . | 0.2101 | ratio | psi |  | eq | `[[art:1d339225:psi.vintage_holdout.incentive]]` | verified | 0.2100590512 |
| 145 | data_integrity | The value of `psi.vintage_holdout.loan_age` is 0.03489 . | 0.03489 | ratio | psi |  | eq | `[[art:e579422e:psi.vintage_holdout.loan_age]]` | verified | 0.03488721615 |
| 146 | data_integrity | The value of `psi.vintage_holdout.note_rate` is 0.2743 . | 0.2743 | ratio | psi |  | eq | `[[art:d4e6aa9a:psi.vintage_holdout.note_rate]]` | verified | 0.2742521405 |
| 147 | data_integrity | The value of `psi.vintage_holdout.orig_ltv` is 0.03575 . | 0.03575 | ratio | psi |  | eq | `[[art:1f0e3df0:psi.vintage_holdout.orig_ltv]]` | verified | 0.03575446718 |
| 148 | data_integrity | The value of `psi.vintage_holdout.orig_upb_log` is 0.03038 . | 0.03038 | ratio | psi |  | eq | `[[art:10fd298a:psi.vintage_holdout.orig_upb_log]]` | verified | 0.03037586387 |
| 149 | data_integrity | The value of `psi.vintage_holdout.sato` is 0.02841 . | 0.02841 | ratio | psi |  | eq | `[[art:6c4e561c:psi.vintage_holdout.sato]]` | verified | 0.02840898929 |
| 150 | data_integrity | The value of `psi.vintage_holdout.season_cos` is 0.00164 . | 0.00164 | ratio | psi |  | eq | `[[art:4482dc21:psi.vintage_holdout.season_cos]]` | verified | 0.001640289708 |
| 151 | data_integrity | The value of `psi.vintage_holdout.season_sin` is 0.001971 . | 0.001971 | ratio | psi |  | eq | `[[art:836b68bf:psi.vintage_holdout.season_sin]]` | verified | 0.001971264046 |
| 152 | data_integrity | The value of `psi.vintage_holdout.y_score` is 0.08202 . | 0.08202 | ratio | psi |  | eq | `[[art:5d010092:psi.vintage_holdout.y_score]]` | verified | 0.0820229283 |
| 153 | data_integrity | The value of `psi.y_score` is 0.8372 . | 0.8372 | ratio | psi |  | eq | `[[art:92ac1652:psi.y_score]]` | verified | 0.8371883582 |
| 154 | data_integrity | The value of `threshold.D1.missing_gap` is 0.1 . | 0.1 | ratio | threshold |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 155 | data_integrity | The value of `threshold.L1.single_feature_auc` is 0.9 . | 0.9 | ratio | threshold |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 156 | data_integrity | The value of `threshold.L2.overlap` is 0.005 . | 0.005 | ratio | threshold |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 157 | data_integrity | The value of `threshold.L2.overlap.features_effective` is 0.… | 0.005 | ratio | threshold |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 158 | data_integrity | The value of `threshold.S1.psi` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 159 | data_integrity | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 160 | outcomes | The value of `calibration.mean_rel_gap.out_of_time` is 0.271… | 0.2718 | ratio | calibration |  | eq | `[[art:c5239af4:calibration.mean_rel_gap.out_of_time]]` | verified | 0.2717535987 |
| 161 | outcomes | The value of `calibration.mean_rel_gap.test` is 0.2718 . | 0.2718 | ratio | calibration |  | eq | `[[art:04dcea16:calibration.mean_rel_gap.test]]` | verified | 0.2717535987 |
| 162 | outcomes | The value of `calibration.mean_rel_gap.train` is 0.001197 . | 0.001197 | ratio | calibration |  | eq | `[[art:7d19dc79:calibration.mean_rel_gap.train]]` | verified | 0.001197193051 |
| 163 | outcomes | The value of `calibration.mean_rel_gap.vintage_holdout` is 0… | 0.2782 | ratio | calibration |  | eq | `[[art:2eba48c2:calibration.mean_rel_gap.vintage_holdout]]` | verified | 0.2782482723 |
| 164 | outcomes | The value of `calibration_intercept.out_of_time` is -0.4556… | -0.4556 | ratio | calibration_intercept |  | eq | `[[art:8dc58882:calibration_intercept.out_of_time]]` | verified | -0.4555664421 |
| 165 | outcomes | The value of `calibration_intercept.test` is -0.4556 . | -0.4556 | ratio | calibration_intercept |  | eq | `[[art:256e21c4:calibration_intercept.test]]` | verified | -0.4555664421 |
| 166 | outcomes | The value of `calibration_intercept.train` is 0.06177 . | 0.06177 | ratio | calibration_intercept |  | eq | `[[art:7184b1c0:calibration_intercept.train]]` | verified | 0.06176828223 |
| 167 | outcomes | The value of `calibration_intercept.vintage_holdout` is -0.8… | -0.8976 | ratio | calibration_intercept |  | eq | `[[art:21c5b98a:calibration_intercept.vintage_holdout]]` | verified | -0.8976276791 |
| 168 | outcomes | The value of `calibration_slope.out_of_time` is 0.9369 . | 0.9369 | ratio | calibration_slope |  | eq | `[[art:994798d5:calibration_slope.out_of_time]]` | verified | 0.9368866293 |
| 169 | outcomes | The value of `calibration_slope.test` is 0.9369 . | 0.9369 | ratio | calibration_slope |  | eq | `[[art:290cccd9:calibration_slope.test]]` | verified | 0.9368866293 |
| 170 | outcomes | The value of `calibration_slope.train` is 1.015 . | 1.015 | ratio | calibration_slope |  | eq | `[[art:6ee05ed8:calibration_slope.train]]` | verified | 1.015165743 |
| 171 | outcomes | The value of `calibration_slope.vintage_holdout` is 0.8554 . | 0.8554 | ratio | calibration_slope |  | eq | `[[art:6b42345a:calibration_slope.vintage_holdout]]` | verified | 0.8553956316 |
| 172 | outcomes | The value of `cpr.out_of_time.mae` is 0.06724 . | 0.06724 | ratio | cpr |  | eq | `[[art:ed058023:cpr.out_of_time.mae]]` | verified | 0.06723889098 |
| 173 | outcomes | The value of `cpr.test.mae` is 0.06724 . | 0.06724 | ratio | cpr |  | eq | `[[art:fe0e020a:cpr.test.mae]]` | verified | 0.06723889098 |
| 174 | outcomes | The value of `cpr.train.mae` is 0.03373 . | 0.03373 | ratio | cpr |  | eq | `[[art:609b1f19:cpr.train.mae]]` | verified | 0.03373481364 |
| 175 | outcomes | The value of `cpr.vintage_holdout.mae` is 0.03062 . | 0.03062 | ratio | cpr |  | eq | `[[art:10b5118d:cpr.vintage_holdout.mae]]` | verified | 0.03061840342 |
| 176 | outcomes | The value of `deciles.out_of_time.top2_capture` is 0.5773 . | 0.5773 | ratio | deciles |  | eq | `[[art:df63152b:deciles.out_of_time.top2_capture]]` | verified | 0.5772727273 |
| 177 | outcomes | The value of `deciles.test.top2_capture` is 0.5773 . | 0.5773 | ratio | deciles |  | eq | `[[art:88c7c389:deciles.test.top2_capture]]` | verified | 0.5772727273 |
| 178 | outcomes | The value of `deciles.train.top2_capture` is 0.638 . | 0.638 | ratio | deciles |  | eq | `[[art:3ac2e5fd:deciles.train.top2_capture]]` | verified | 0.6379928315 |
| 179 | outcomes | The value of `deciles.vintage_holdout.top2_capture` is 0.580… | 0.5806 | ratio | deciles |  | eq | `[[art:0d0c0310:deciles.vintage_holdout.top2_capture]]` | verified | 0.5806451613 |
| 180 | outcomes | The value of `metrics.out_of_time.auc` is 0.7846 . | 0.7846 | ratio | metrics |  | eq | `[[art:ee898745:metrics.out_of_time.auc]]` | verified | 0.7846182604 |
| 181 | outcomes | The value of `metrics.out_of_time.brier` is 0.01725 . | 0.01725 | ratio | metrics |  | eq | `[[art:f0fd020a:metrics.out_of_time.brier]]` | verified | 0.01725186302 |
| 182 | outcomes | The value of `metrics.out_of_time.event_rate` is 0.01795 . | 0.01795 | ratio | metrics |  | eq | `[[art:83ccf5c0:metrics.out_of_time.event_rate]]` | verified | 0.01794892714 |
| 183 | outcomes | The value of `metrics.out_of_time.gini` is 0.5692 . | 0.5692 | ratio | metrics |  | eq | `[[art:46899ec9:metrics.out_of_time.gini]]` | verified | 0.5692365207 |
| 184 | outcomes | The value of `metrics.out_of_time.ks` is 0.4373 . | 0.4373 | ratio | metrics |  | eq | `[[art:6360ccf9:metrics.out_of_time.ks]]` | verified | 0.4373216673 |
| 185 | outcomes | The value of `metrics.out_of_time.logloss` is 0.0805 . | 0.0805 | ratio | metrics |  | eq | `[[art:205ce509:metrics.out_of_time.logloss]]` | verified | 0.08050056271 |
| 186 | outcomes | The value of `metrics.out_of_time.mean_predicted` is 0.02283… | 0.02283 | ratio | metrics |  | eq | `[[art:4d7aa98b:metrics.out_of_time.mean_predicted]]` | verified | 0.02282661269 |
| 187 | outcomes | The value of `metrics.out_of_time.n` is 12257 . | 12257 | ratio | metrics |  | eq | `[[art:7898809e:metrics.out_of_time.n]]` | verified | 12257 |
| 188 | outcomes | The value of `metrics.test.auc` is 0.7846 . | 0.7846 | ratio | metrics |  | eq | `[[art:d57b2552:metrics.test.auc]]` | verified | 0.7846182604 |
| 189 | outcomes | The value of `metrics.test.brier` is 0.01725 . | 0.01725 | ratio | metrics |  | eq | `[[art:68e8b1cf:metrics.test.brier]]` | verified | 0.01725186302 |
| 190 | outcomes | The value of `metrics.test.event_rate` is 0.01795 . | 0.01795 | ratio | metrics |  | eq | `[[art:d222aedf:metrics.test.event_rate]]` | verified | 0.01794892714 |
| 191 | outcomes | The value of `metrics.test.gini` is 0.5692 . | 0.5692 | ratio | metrics |  | eq | `[[art:1291e305:metrics.test.gini]]` | verified | 0.5692365207 |
| 192 | outcomes | The value of `metrics.test.ks` is 0.4373 . | 0.4373 | ratio | metrics |  | eq | `[[art:857a0cf9:metrics.test.ks]]` | verified | 0.4373216673 |
| 193 | outcomes | The value of `metrics.test.logloss` is 0.0805 . | 0.0805 | ratio | metrics |  | eq | `[[art:c576b630:metrics.test.logloss]]` | verified | 0.08050056271 |
| 194 | outcomes | The value of `metrics.test.mean_predicted` is 0.02283 . | 0.02283 | ratio | metrics |  | eq | `[[art:1c1a1d8d:metrics.test.mean_predicted]]` | verified | 0.02282661269 |
| 195 | outcomes | The value of `metrics.test.n` is 12257 . | 12257 | ratio | metrics |  | eq | `[[art:90b46eb1:metrics.test.n]]` | verified | 12257 |
| 196 | outcomes | The value of `metrics.train.auc` is 0.8003 . | 0.8003 | ratio | metrics |  | eq | `[[art:41d3c4e6:metrics.train.auc]]` | verified | 0.8002919094 |
| 197 | outcomes | The value of `metrics.train.brier` is 0.008111 . | 0.008111 | ratio | metrics |  | eq | `[[art:e9077291:metrics.train.brier]]` | verified | 0.008111422906 |
| 198 | outcomes | The value of `metrics.train.event_rate` is 0.008323 . | 0.008323 | ratio | metrics |  | eq | `[[art:b0cf2348:metrics.train.event_rate]]` | verified | 0.008322892429 |
| 199 | outcomes | The value of `metrics.train.gini` is 0.6006 . | 0.6006 | ratio | metrics |  | eq | `[[art:66b6cc81:metrics.train.gini]]` | verified | 0.6005838187 |
| 200 | outcomes | The value of `metrics.train.ks` is 0.474 . | 0.474 | ratio | metrics |  | eq | `[[art:3e0b8829:metrics.train.ks]]` | verified | 0.4740174906 |
| 201 | outcomes | The value of `metrics.train.logloss` is 0.04279 . | 0.04279 | ratio | metrics |  | eq | `[[art:e62507ab:metrics.train.logloss]]` | verified | 0.04279363896 |
| 202 | outcomes | The value of `metrics.train.mean_predicted` is 0.008333 . | 0.008333 | ratio | metrics |  | eq | `[[art:4ea7b930:metrics.train.mean_predicted]]` | verified | 0.008332856538 |
| 203 | outcomes | The value of `metrics.train.n` is 33522 . | 33522 | ratio | metrics |  | eq | `[[art:dd20fa4c:metrics.train.n]]` | verified | 33522 |
| 204 | outcomes | The value of `metrics.vintage_holdout.auc` is 0.7716 . | 0.7716 | ratio | metrics |  | eq | `[[art:610c13fd:metrics.vintage_holdout.auc]]` | verified | 0.7716058113 |
| 205 | outcomes | The value of `metrics.vintage_holdout.brier` is 0.004767 . | 0.004767 | ratio | metrics |  | eq | `[[art:115af096:metrics.vintage_holdout.brier]]` | verified | 0.004766820283 |
| 206 | outcomes | The value of `metrics.vintage_holdout.event_rate` is 0.00481… | 0.004817 | ratio | metrics |  | eq | `[[art:e3590a16:metrics.vintage_holdout.event_rate]]` | verified | 0.004817105386 |
| 207 | outcomes | The value of `metrics.vintage_holdout.gini` is 0.5432 . | 0.5432 | ratio | metrics |  | eq | `[[art:4b1525bb:metrics.vintage_holdout.gini]]` | verified | 0.5432116227 |
| 208 | outcomes | The value of `metrics.vintage_holdout.ks` is 0.4618 . | 0.4618 | ratio | metrics |  | eq | `[[art:c3ac5a54:metrics.vintage_holdout.ks]]` | verified | 0.4617647948 |
| 209 | outcomes | The value of `metrics.vintage_holdout.logloss` is 0.02818 . | 0.02818 | ratio | metrics |  | eq | `[[art:96a19aae:metrics.vintage_holdout.logloss]]` | verified | 0.02818314174 |
| 210 | outcomes | The value of `metrics.vintage_holdout.mean_predicted` is 0.0… | 0.006157 | ratio | metrics |  | eq | `[[art:914aeeba:metrics.vintage_holdout.mean_predicted]]` | verified | 0.006157456637 |
| 211 | outcomes | The value of `metrics.vintage_holdout.n` is 32177 . | 32177 | ratio | metrics |  | eq | `[[art:37a92951:metrics.vintage_holdout.n]]` | verified | 32177 |
| 212 | outcomes | The value of `psi.burnout` is 3.016 . | 3.016 | ratio | psi |  | eq | `[[art:1d35a583:psi.burnout]]` | verified | 3.016020048 |
| 213 | outcomes | The value of `psi.credit_score` is 0.07088 . | 0.07088 | ratio | psi |  | eq | `[[art:91c4ab83:psi.credit_score]]` | verified | 0.07088355626 |
| 214 | outcomes | The value of `psi.incentive` is 0.8734 . | 0.8734 | ratio | psi |  | eq | `[[art:0f61188c:psi.incentive]]` | verified | 0.8734495361 |
| 215 | outcomes | The value of `psi.loan_age` is 1.68 . | 1.68 | ratio | psi |  | eq | `[[art:987aabe4:psi.loan_age]]` | verified | 1.679868562 |
| 216 | outcomes | The value of `psi.max` is 3.016 . | 3.016 | ratio | psi |  | eq | `[[art:4fae32c6:psi.max]]` | verified | 3.016020048 |
| 217 | outcomes | The value of `psi.note_rate` is 1.342 . | 1.342 | ratio | psi |  | eq | `[[art:2f1cb70b:psi.note_rate]]` | verified | 1.341893523 |
| 218 | outcomes | The value of `psi.orig_ltv` is 0.04332 . | 0.04332 | ratio | psi |  | eq | `[[art:85842fd0:psi.orig_ltv]]` | verified | 0.04331914243 |
| 219 | outcomes | The value of `psi.orig_upb_log` is 0.08171 . | 0.08171 | ratio | psi |  | eq | `[[art:f075546d:psi.orig_upb_log]]` | verified | 0.08171063787 |
| 220 | outcomes | The value of `psi.out_of_time.burnout` is 3.016 . | 3.016 | ratio | psi |  | eq | `[[art:8cedaf79:psi.out_of_time.burnout]]` | verified | 3.016020048 |
| 221 | outcomes | The value of `psi.out_of_time.credit_score` is 0.07088 . | 0.07088 | ratio | psi |  | eq | `[[art:a7ef717f:psi.out_of_time.credit_score]]` | verified | 0.07088355626 |
| 222 | outcomes | The value of `psi.out_of_time.incentive` is 0.8734 . | 0.8734 | ratio | psi |  | eq | `[[art:ec6da34d:psi.out_of_time.incentive]]` | verified | 0.8734495361 |
| 223 | outcomes | The value of `psi.out_of_time.loan_age` is 1.68 . | 1.68 | ratio | psi |  | eq | `[[art:ab2af3f2:psi.out_of_time.loan_age]]` | verified | 1.679868562 |
| 224 | outcomes | The value of `psi.out_of_time.note_rate` is 1.342 . | 1.342 | ratio | psi |  | eq | `[[art:fc610fd1:psi.out_of_time.note_rate]]` | verified | 1.341893523 |
| 225 | outcomes | The value of `psi.out_of_time.orig_ltv` is 0.04332 . | 0.04332 | ratio | psi |  | eq | `[[art:7eedf98f:psi.out_of_time.orig_ltv]]` | verified | 0.04331914243 |
| 226 | outcomes | The value of `psi.out_of_time.orig_upb_log` is 0.08171 . | 0.08171 | ratio | psi |  | eq | `[[art:9ca9c306:psi.out_of_time.orig_upb_log]]` | verified | 0.08171063787 |
| 227 | outcomes | The value of `psi.out_of_time.sato` is 0.02284 . | 0.02284 | ratio | psi |  | eq | `[[art:79f6f94a:psi.out_of_time.sato]]` | verified | 0.02284102604 |
| 228 | outcomes | The value of `psi.out_of_time.season_cos` is 0.004988 . | 0.004988 | ratio | psi |  | eq | `[[art:ef947d09:psi.out_of_time.season_cos]]` | verified | 0.004987781308 |
| 229 | outcomes | The value of `psi.out_of_time.season_sin` is 0.01631 . | 0.01631 | ratio | psi |  | eq | `[[art:fe2b0197:psi.out_of_time.season_sin]]` | verified | 0.01631255179 |
| 230 | outcomes | The value of `psi.out_of_time.y_score` is 0.8372 . | 0.8372 | ratio | psi |  | eq | `[[art:d39a4ced:psi.out_of_time.y_score]]` | verified | 0.8371883582 |
| 231 | outcomes | The value of `psi.sato` is 0.02284 . | 0.02284 | ratio | psi |  | eq | `[[art:4809116c:psi.sato]]` | verified | 0.02284102604 |
| 232 | outcomes | The value of `psi.season_cos` is 0.004988 . | 0.004988 | ratio | psi |  | eq | `[[art:62ae6c81:psi.season_cos]]` | verified | 0.004987781308 |
| 233 | outcomes | The value of `psi.season_sin` is 0.01631 . | 0.01631 | ratio | psi |  | eq | `[[art:46fec014:psi.season_sin]]` | verified | 0.01631255179 |
| 234 | outcomes | The value of `psi.vintage_holdout.burnout` is 0.03122 . | 0.03122 | ratio | psi |  | eq | `[[art:b2dacb71:psi.vintage_holdout.burnout]]` | verified | 0.03122017454 |
| 235 | outcomes | The value of `psi.vintage_holdout.credit_score` is 0.01929 . | 0.01929 | ratio | psi |  | eq | `[[art:16906529:psi.vintage_holdout.credit_score]]` | verified | 0.01928865688 |
| 236 | outcomes | The value of `psi.vintage_holdout.incentive` is 0.2101 . | 0.2101 | ratio | psi |  | eq | `[[art:1d339225:psi.vintage_holdout.incentive]]` | verified | 0.2100590512 |
| 237 | outcomes | The value of `psi.vintage_holdout.loan_age` is 0.03489 . | 0.03489 | ratio | psi |  | eq | `[[art:e579422e:psi.vintage_holdout.loan_age]]` | verified | 0.03488721615 |
| 238 | outcomes | The value of `psi.vintage_holdout.note_rate` is 0.2743 . | 0.2743 | ratio | psi |  | eq | `[[art:d4e6aa9a:psi.vintage_holdout.note_rate]]` | verified | 0.2742521405 |
| 239 | outcomes | The value of `psi.vintage_holdout.orig_ltv` is 0.03575 . | 0.03575 | ratio | psi |  | eq | `[[art:1f0e3df0:psi.vintage_holdout.orig_ltv]]` | verified | 0.03575446718 |
| 240 | outcomes | The value of `psi.vintage_holdout.orig_upb_log` is 0.03038 . | 0.03038 | ratio | psi |  | eq | `[[art:10fd298a:psi.vintage_holdout.orig_upb_log]]` | verified | 0.03037586387 |
| 241 | outcomes | The value of `psi.vintage_holdout.sato` is 0.02841 . | 0.02841 | ratio | psi |  | eq | `[[art:6c4e561c:psi.vintage_holdout.sato]]` | verified | 0.02840898929 |
| 242 | outcomes | The value of `psi.vintage_holdout.season_cos` is 0.00164 . | 0.00164 | ratio | psi |  | eq | `[[art:4482dc21:psi.vintage_holdout.season_cos]]` | verified | 0.001640289708 |
| 243 | outcomes | The value of `psi.vintage_holdout.season_sin` is 0.001971 . | 0.001971 | ratio | psi |  | eq | `[[art:836b68bf:psi.vintage_holdout.season_sin]]` | verified | 0.001971264046 |
| 244 | outcomes | The value of `psi.vintage_holdout.y_score` is 0.08202 . | 0.08202 | ratio | psi |  | eq | `[[art:5d010092:psi.vintage_holdout.y_score]]` | verified | 0.0820229283 |
| 245 | outcomes | The value of `psi.y_score` is 0.8372 . | 0.8372 | ratio | psi |  | eq | `[[art:92ac1652:psi.y_score]]` | verified | 0.8371883582 |
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
| 266 | sensitivity | The value of `condition_number` is 4.778 . | 4.778 | ratio | condition_number |  | eq | `[[art:5e2416a9:condition_number]]` | verified | 4.777601017 |
| 267 | sensitivity | The value of `scenario.convexity` is -1095000 . | -1095000 | ratio | scenario |  | eq | `[[art:70b14b4a:scenario.convexity]]` | verified | -1094856.426 |
| 268 | sensitivity | The value of `scenario.value_change.-100` is -171500 . | -171500 | ratio | scenario |  | eq | `[[art:56c3d7c6:scenario.value_change.-100]]` | verified | -171515.6127 |
| 269 | sensitivity | The value of `scenario.value_change.-200` is -587900 . | -587900 | ratio | scenario |  | eq | `[[art:fc12530a:scenario.value_change.-200]]` | verified | -587861.1403 |
| 270 | sensitivity | The value of `scenario.value_change.-300` is -1166000 . | -1166000 | ratio | scenario |  | eq | `[[art:dfaf9b49:scenario.value_change.-300]]` | verified | -1166173.182 |
| 271 | sensitivity | The value of `scenario.value_change.0` is 0 . | 0 | ratio | scenario |  | eq | `[[art:1e1b0b88:scenario.value_change.0]]` | verified | 0 |
| 272 | sensitivity | The value of `scenario.value_change.100` is 51210 . | 51210 | ratio | scenario |  | eq | `[[art:c5393b58:scenario.value_change.100]]` | verified | 51212.01224 |
| 273 | sensitivity | The value of `scenario.value_change.200` is 66660 . | 66660 | ratio | scenario |  | eq | `[[art:8b1b5955:scenario.value_change.200]]` | verified | 66659.08481 |
| 274 | sensitivity | The value of `scenario.value_change.300` is 71320 . | 71320 | ratio | scenario |  | eq | `[[art:1bebd745:scenario.value_change.300]]` | verified | 71316.75564 |
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
| 290 | sensitivity | The value of `vif.burnout` is 3.601 . | 3.601 | ratio | vif |  | eq | `[[art:127bbabe:vif.burnout]]` | verified | 3.601072256 |
| 291 | sensitivity | The value of `vif.credit_score` is 1.011 . | 1.011 | ratio | vif |  | eq | `[[art:1f19769b:vif.credit_score]]` | verified | 1.011319432 |
| 292 | sensitivity | The value of `vif.incentive` is 2.195 . | 2.195 | ratio | vif |  | eq | `[[art:60c8eef8:vif.incentive]]` | verified | 2.195314756 |
| 293 | sensitivity | The value of `vif.loan_age` is 2.593 . | 2.593 | ratio | vif |  | eq | `[[art:b30f78aa:vif.loan_age]]` | verified | 2.593200289 |
| 294 | sensitivity | The value of `vif.max` is 4.288 . | 4.288 | ratio | vif |  | eq | `[[art:fecfb289:vif.max]]` | verified | 4.288168629 |
| 295 | sensitivity | The value of `vif.note_rate` is 4.288 . | 4.288 | ratio | vif |  | eq | `[[art:1113d019:vif.note_rate]]` | verified | 4.288168629 |
| 296 | sensitivity | The value of `vif.orig_ltv` is 1.014 . | 1.014 | ratio | vif |  | eq | `[[art:d9449fe2:vif.orig_ltv]]` | verified | 1.013521613 |
| 297 | sensitivity | The value of `vif.orig_upb_log` is 1.012 . | 1.012 | ratio | vif |  | eq | `[[art:59e2ab98:vif.orig_upb_log]]` | verified | 1.012256745 |
| 298 | sensitivity | The value of `vif.sato` is 1.627 . | 1.627 | ratio | vif |  | eq | `[[art:4b2ebef2:vif.sato]]` | verified | 1.627027838 |
| 299 | sensitivity | The value of `vif.season_cos` is 1.007 . | 1.007 | ratio | vif |  | eq | `[[art:f741ba51:vif.season_cos]]` | verified | 1.007021417 |
| 300 | sensitivity | The value of `vif.season_sin` is 1.011 . | 1.011 | ratio | vif |  | eq | `[[art:3b05b05a:vif.season_sin]]` | verified | 1.010543525 |
| 301 | findings | The value of `calibration.mean_rel_gap.out_of_time` is 0.271… | 0.2718 | ratio | calibration |  | eq | `[[art:c5239af4:calibration.mean_rel_gap.out_of_time]]` | verified | 0.2717535987 |
| 302 | findings | The value of `calibration.mean_rel_gap.test` is 0.2718 . | 0.2718 | ratio | calibration |  | eq | `[[art:04dcea16:calibration.mean_rel_gap.test]]` | verified | 0.2717535987 |
| 303 | findings | The value of `calibration.mean_rel_gap.vintage_holdout` is 0… | 0.2782 | ratio | calibration |  | eq | `[[art:2eba48c2:calibration.mean_rel_gap.vintage_holdout]]` | verified | 0.2782482723 |
| 304 | findings | The value of `metrics.out_of_time.event_rate` is 0.01795 . | 0.01795 | ratio | metrics |  | eq | `[[art:83ccf5c0:metrics.out_of_time.event_rate]]` | verified | 0.01794892714 |
| 305 | findings | The value of `metrics.out_of_time.mean_predicted` is 0.02283… | 0.02283 | ratio | metrics |  | eq | `[[art:4d7aa98b:metrics.out_of_time.mean_predicted]]` | verified | 0.02282661269 |
| 306 | findings | The value of `metrics.test.event_rate` is 0.01795 . | 0.01795 | ratio | metrics |  | eq | `[[art:d222aedf:metrics.test.event_rate]]` | verified | 0.01794892714 |
| 307 | findings | The value of `metrics.test.mean_predicted` is 0.02283 . | 0.02283 | ratio | metrics |  | eq | `[[art:1c1a1d8d:metrics.test.mean_predicted]]` | verified | 0.02282661269 |
| 308 | findings | The value of `metrics.vintage_holdout.event_rate` is 0.00481… | 0.004817 | ratio | metrics |  | eq | `[[art:e3590a16:metrics.vintage_holdout.event_rate]]` | verified | 0.004817105386 |
| 309 | findings | The value of `metrics.vintage_holdout.mean_predicted` is 0.0… | 0.006157 | ratio | metrics |  | eq | `[[art:914aeeba:metrics.vintage_holdout.mean_predicted]]` | verified | 0.006157456637 |
| 310 | findings | The value of `psi.burnout` is 3.016 . | 3.016 | ratio | psi |  | eq | `[[art:1d35a583:psi.burnout]]` | verified | 3.016020048 |
| 311 | findings | The value of `psi.incentive` is 0.8734 . | 0.8734 | ratio | psi |  | eq | `[[art:0f61188c:psi.incentive]]` | verified | 0.8734495361 |
| 312 | findings | The value of `psi.loan_age` is 1.68 . | 1.68 | ratio | psi |  | eq | `[[art:987aabe4:psi.loan_age]]` | verified | 1.679868562 |
| 313 | findings | The value of `psi.max` is 3.016 . | 3.016 | ratio | psi |  | eq | `[[art:4fae32c6:psi.max]]` | verified | 3.016020048 |
| 314 | findings | The value of `psi.note_rate` is 1.342 . | 1.342 | ratio | psi |  | eq | `[[art:2f1cb70b:psi.note_rate]]` | verified | 1.341893523 |
| 315 | findings | The value of `psi.y_score` is 0.8372 . | 0.8372 | ratio | psi |  | eq | `[[art:92ac1652:psi.y_score]]` | verified | 0.8371883582 |
| 316 | findings | The value of `sign_check.note_rate.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:a453463d:sign_check.note_rate.agrees]]` | verified | 0 |
| 317 | findings | The value of `sign_check.note_rate.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:aecf7ccb:sign_check.note_rate.coef_sign]]` | verified | -1 |
| 318 | findings | The value of `sign_check.note_rate.univariate_direction` is… | 1 | ratio | sign_check |  | eq | `[[art:61f6e1ac:sign_check.note_rate.univariate_direction]]` | verified | 1 |
| 319 | findings | The value of `threshold.C1.mean_ratio_rel` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 320 | findings | The value of `threshold.S1.psi` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 321 | findings | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 322 | monitoring | The value of `calibration_slope.test` is 0.9369 . | 0.9369 | ratio | calibration_slope |  | eq | `[[art:290cccd9:calibration_slope.test]]` | verified | 0.9368866293 |
| 323 | monitoring | The value of `metrics.test.auc` is 0.7846 . | 0.7846 | ratio | metrics |  | eq | `[[art:d57b2552:metrics.test.auc]]` | verified | 0.7846182604 |
| 324 | monitoring | The value of `psi.max` is 3.016 . | 3.016 | ratio | psi |  | eq | `[[art:4fae32c6:psi.max]]` | verified | 3.016020048 |
| 325 | monitoring | The value of `rule.calibration_first_event_rate` is 0.05 . | 0.05 | ratio | rule |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 326 | monitoring | The value of `threshold.package.auc.test.min` is 0.65 . | 0.65 | ratio | threshold |  | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 327 | monitoring | The value of `threshold.package.calibration_slope.test.max`… | 1.2 | ratio | threshold |  | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 328 | monitoring | The value of `threshold.package.calibration_slope.test.min`… | 0.8 | ratio | threshold |  | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 329 | monitoring | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |

## Appendix B — Artifact index

The store holds 272 artifacts; the 214 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `ablation.baseline_auc` | `93dda83a` | scalar | 0.7802163028 | AUC on test of a refit of the champion's functional form on every retained feature, the level each ablation delta is measured from |
| `ablation.burnout.delta_auc` | `8aa8bccf` | scalar | 0.00429206915 | change in test AUC when the champion's form is refitted without burnout |
| `ablation.credit_score.delta_auc` | `a2d10cd7` | scalar | -0.02980393786 | change in test AUC when the champion's form is refitted without credit_score |
| `ablation.incentive.delta_auc` | `46802ce1` | scalar | -0.07943499966 | change in test AUC when the champion's form is refitted without incentive |
| `ablation.loan_age.delta_auc` | `ca8fa8e9` | scalar | -0.009945848784 | change in test AUC when the champion's form is refitted without loan_age |
| `ablation.note_rate.delta_auc` | `338b461a` | scalar | 0.005792367473 | change in test AUC when the champion's form is refitted without note_rate |
| `ablation.orig_ltv.delta_auc` | `84275e57` | scalar | -0.01199332362 | change in test AUC when the champion's form is refitted without orig_ltv |
| `ablation.orig_upb_log.delta_auc` | `6158bf75` | scalar | -0.01681104473 | change in test AUC when the champion's form is refitted without orig_upb_log |
| `ablation.sato.delta_auc` | `c9eb03ef` | scalar | -0.004237313737 | change in test AUC when the champion's form is refitted without sato |
| `ablation.season_cos.delta_auc` | `bdbbba37` | scalar | -0.005672283187 | change in test AUC when the champion's form is refitted without season_cos |
| `ablation.season_sin.delta_auc` | `95e1e0c6` | scalar | 0.0005400016615 | change in test AUC when the champion's form is refitted without season_sin |
| `calibration.mean_rel_gap.out_of_time` | `c5239af4` | scalar | 0.2717535987 | mean predicted against observed on out_of_time, relative |
| `calibration.mean_rel_gap.test` | `04dcea16` | scalar | 0.2717535987 | mean predicted against observed on test, relative |
| `calibration.mean_rel_gap.train` | `7d19dc79` | scalar | 0.001197193051 | mean predicted against observed on train, relative |
| `calibration.mean_rel_gap.vintage_holdout` | `2eba48c2` | scalar | 0.2782482723 | mean predicted against observed on vintage_holdout, relative |
| `calibration.out_of_time` | `a16e1248` | table | table, 10 rows | calibration by decile of predicted probability on out_of_time |
| `calibration.test` | `07848a4c` | table | table, 10 rows | calibration by decile of predicted probability on test |
| `calibration.vintage_holdout` | `a402f077` | table | table, 10 rows | calibration by decile of predicted probability on vintage_holdout |
| `calibration_intercept.out_of_time` | `8dc58882` | scalar | -0.4555664421 | logistic regression of the outcome on logit(p) on out_of_time: the intercept |
| `calibration_intercept.test` | `256e21c4` | scalar | -0.4555664421 | logistic regression of the outcome on logit(p) on test: the intercept |
| `calibration_intercept.train` | `7184b1c0` | scalar | 0.06176828223 | logistic regression of the outcome on logit(p) on train: the intercept |
| `calibration_intercept.vintage_holdout` | `21c5b98a` | scalar | -0.8976276791 | logistic regression of the outcome on logit(p) on vintage_holdout: the intercept |
| `calibration_slope.out_of_time` | `994798d5` | scalar | 0.9368866293 | logistic regression of the outcome on logit(p) on out_of_time: the slope |
| `calibration_slope.test` | `290cccd9` | scalar | 0.9368866293 | logistic regression of the outcome on logit(p) on test: the slope |
| `calibration_slope.train` | `6ee05ed8` | scalar | 1.015165743 | logistic regression of the outcome on logit(p) on train: the slope |
| `calibration_slope.vintage_holdout` | `6b42345a` | scalar | 0.8553956316 | logistic regression of the outcome on logit(p) on vintage_holdout: the slope |
| `challenger.auc` | `489cd7a6` | scalar | 0.7210566662 | the challenger's AUC on test |
| `challenger.brier` | `36aa75c4` | scalar | 0.02173012265 | the challenger's Brier score on test |
| `challenger.delta_auc` | `7e119a34` | scalar | -0.06356159418 | the challenger's AUC on test minus the champion's |
| `condition_number` | `5e2416a9` | scalar | 4.777601017 | Belsley's condition number of the column-standardised design |
| `cpr.out_of_time.mae` | `ed058023` | scalar | 0.06723889098 | mean absolute difference between actual and predicted CPR on out_of_time |
| `cpr.test` | `81cf8976` | table | table, 36 rows | actual against predicted CPR by period on test |
| `cpr.test.mae` | `fe0e020a` | scalar | 0.06723889098 | mean absolute difference between actual and predicted CPR on test |
| `cpr.train.mae` | `609b1f19` | scalar | 0.03373481364 | mean absolute difference between actual and predicted CPR on train |
| `cpr.vintage_holdout.mae` | `10b5118d` | scalar | 0.03061840342 | mean absolute difference between actual and predicted CPR on vintage_holdout |
| `csi.burnout` | `e0f86ff2` | scalar | 0.3488802555 | CSI of burnout: its contribution to the shift in the linear predictor |
| `csi.credit_score` | `4fbc434e` | scalar | 0.09086513179 | CSI of credit_score: its contribution to the shift in the linear predictor |
| `csi.incentive` | `f430cc2d` | scalar | 0.9220903461 | CSI of incentive: its contribution to the shift in the linear predictor |
| `csi.loan_age` | `df52c920` | scalar | 0 | CSI of loan_age: its contribution to the shift in the linear predictor |
| `csi.max` | `d4b08859` | scalar | 0.9220903461 | the largest characteristic stability index |
| `csi.note_rate` | `a2be3f30` | scalar | 0.4831662682 | CSI of note_rate: its contribution to the shift in the linear predictor |
| `csi.orig_ltv` | `af80429c` | scalar | 0.02302783458 | CSI of orig_ltv: its contribution to the shift in the linear predictor |
| `csi.orig_upb_log` | `ba82e949` | scalar | 0.06561601038 | CSI of orig_upb_log: its contribution to the shift in the linear predictor |
| `csi.sato` | `7d563a3f` | scalar | 0.0001467991037 | CSI of sato: its contribution to the shift in the linear predictor |
| `csi.season_cos` | `49e6d56e` | scalar | 0.003265173321 | CSI of season_cos: its contribution to the shift in the linear predictor |
| `csi.season_sin` | `ff10caf4` | scalar | 0.01315757493 | CSI of season_sin: its contribution to the shift in the linear predictor |
| `deciles.out_of_time.top2_capture` | `df63152b` | scalar | 0.5772727273 | share of out_of_time events in the top two deciles |
| `deciles.test` | `26b0ba93` | table | table, 10 rows | decile separation on test; decile 1 holds the highest probabilities |
| `deciles.test.top2_capture` | `88c7c389` | scalar | 0.5772727273 | share of test events in the top two deciles |
| `deciles.train.top2_capture` | `3ac2e5fd` | scalar | 0.6379928315 | share of train events in the top two deciles |
| `deciles.vintage_holdout.top2_capture` | `0d0c0310` | scalar | 0.5806451613 | share of vintage_holdout events in the top two deciles |
| `leakage.duplicates.train` | `4474c227` | scalar | 0 | share of train rows whose feature values are not unique within train |
| `leakage.name_screen.n_matched` | `407e62be` | scalar | 0 | feature names matching the target-adjacent lexicon |
| `leakage.overlap` | `4c9fcd09` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.features` | `0fec8048` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.ids` | `63d37fc5` | scalar | 0 | share of test rows whose ['loan_id', 'period'] also identify a row of train |
| `leakage.target_corr.max_single_feature_auc` | `b6b29a14` | scalar | 0.7422083739 | the AUC of the strongest single feature |
| `leakage.timing.n_flagged` | `742bcd24` | scalar | 0 | features declared during_period or after_outcome |
| `metrics.out_of_time.auc` | `ee898745` | scalar | 0.7846182604 | auc on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.brier` | `f0fd020a` | scalar | 0.01725186302 | brier on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.event_rate` | `83ccf5c0` | scalar | 0.01794892714 | event_rate on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.gini` | `46899ec9` | scalar | 0.5692365207 | gini on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.ks` | `6360ccf9` | scalar | 0.4373216673 | ks on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.logloss` | `205ce509` | scalar | 0.08050056271 | logloss on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.mean_predicted` | `4d7aa98b` | scalar | 0.02282661269 | mean_predicted on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.n` | `7898809e` | scalar | 12257 | n on out_of_time, recomputed by quaestor |
| `metrics.test.auc` | `d57b2552` | scalar | 0.7846182604 | auc on test, recomputed by quaestor |
| `metrics.test.brier` | `68e8b1cf` | scalar | 0.01725186302 | brier on test, recomputed by quaestor |
| `metrics.test.event_rate` | `d222aedf` | scalar | 0.01794892714 | event_rate on test, recomputed by quaestor |
| `metrics.test.gini` | `1291e305` | scalar | 0.5692365207 | gini on test, recomputed by quaestor |
| `metrics.test.ks` | `857a0cf9` | scalar | 0.4373216673 | ks on test, recomputed by quaestor |
| `metrics.test.logloss` | `c576b630` | scalar | 0.08050056271 | logloss on test, recomputed by quaestor |
| `metrics.test.mean_predicted` | `1c1a1d8d` | scalar | 0.02282661269 | mean_predicted on test, recomputed by quaestor |
| `metrics.test.n` | `90b46eb1` | scalar | 12257 | n on test, recomputed by quaestor |
| `metrics.train.auc` | `41d3c4e6` | scalar | 0.8002919094 | auc on train, recomputed by quaestor |
| `metrics.train.brier` | `e9077291` | scalar | 0.008111422906 | brier on train, recomputed by quaestor |
| `metrics.train.event_rate` | `b0cf2348` | scalar | 0.008322892429 | event_rate on train, recomputed by quaestor |
| `metrics.train.gini` | `66b6cc81` | scalar | 0.6005838187 | gini on train, recomputed by quaestor |
| `metrics.train.ks` | `3e0b8829` | scalar | 0.4740174906 | ks on train, recomputed by quaestor |
| `metrics.train.logloss` | `e62507ab` | scalar | 0.04279363896 | logloss on train, recomputed by quaestor |
| `metrics.train.mean_predicted` | `4ea7b930` | scalar | 0.008332856538 | mean_predicted on train, recomputed by quaestor |
| `metrics.train.n` | `dd20fa4c` | scalar | 33522 | n on train, recomputed by quaestor |
| `metrics.vintage_holdout.auc` | `610c13fd` | scalar | 0.7716058113 | auc on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.brier` | `115af096` | scalar | 0.004766820283 | brier on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.event_rate` | `e3590a16` | scalar | 0.004817105386 | event_rate on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.gini` | `4b1525bb` | scalar | 0.5432116227 | gini on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.ks` | `c3ac5a54` | scalar | 0.4617647948 | ks on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.logloss` | `96a19aae` | scalar | 0.02818314174 | logloss on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.mean_predicted` | `914aeeba` | scalar | 0.006157456637 | mean_predicted on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.n` | `37a92951` | scalar | 32177 | n on vintage_holdout, recomputed by quaestor |
| `profile.out_of_time.missing.max` | `4dafce11` | scalar | 0 | the largest missing fraction in out_of_time |
| `profile.out_of_time.n` | `fa39c5cf` | scalar | 12257 | rows in out_of_time |
| `profile.test.missing.max` | `f813848d` | scalar | 0 | the largest missing fraction in test |
| `profile.test.n` | `3b91ffcc` | scalar | 12257 | rows in test |
| `profile.train.missing.max` | `050a3099` | scalar | 0 | the largest missing fraction in train |
| `profile.train.n` | `60d3a086` | scalar | 33522 | rows in train |
| `profile.vintage_holdout.missing.max` | `329bb430` | scalar | 0 | the largest missing fraction in vintage_holdout |
| `profile.vintage_holdout.n` | `426e712a` | scalar | 32177 | rows in vintage_holdout |
| `psi.burnout` | `1d35a583` | scalar | 3.016020048 | PSI of burnout between train and test |
| `psi.credit_score` | `91c4ab83` | scalar | 0.07088355626 | PSI of credit_score between train and test |
| `psi.incentive` | `0f61188c` | scalar | 0.8734495361 | PSI of incentive between train and test |
| `psi.loan_age` | `987aabe4` | scalar | 1.679868562 | PSI of loan_age between train and test |
| `psi.max` | `4fae32c6` | scalar | 3.016020048 | the largest train-to-test PSI, score included |
| `psi.note_rate` | `2f1cb70b` | scalar | 1.341893523 | PSI of note_rate between train and test |
| `psi.orig_ltv` | `85842fd0` | scalar | 0.04331914243 | PSI of orig_ltv between train and test |
| `psi.orig_upb_log` | `f075546d` | scalar | 0.08171063787 | PSI of orig_upb_log between train and test |
| `psi.out_of_time.burnout` | `8cedaf79` | scalar | 3.016020048 | PSI of burnout between train and out_of_time |
| `psi.out_of_time.credit_score` | `a7ef717f` | scalar | 0.07088355626 | PSI of credit_score between train and out_of_time |
| `psi.out_of_time.incentive` | `ec6da34d` | scalar | 0.8734495361 | PSI of incentive between train and out_of_time |
| `psi.out_of_time.loan_age` | `ab2af3f2` | scalar | 1.679868562 | PSI of loan_age between train and out_of_time |
| `psi.out_of_time.note_rate` | `fc610fd1` | scalar | 1.341893523 | PSI of note_rate between train and out_of_time |
| `psi.out_of_time.orig_ltv` | `7eedf98f` | scalar | 0.04331914243 | PSI of orig_ltv between train and out_of_time |
| `psi.out_of_time.orig_upb_log` | `9ca9c306` | scalar | 0.08171063787 | PSI of orig_upb_log between train and out_of_time |
| `psi.out_of_time.sato` | `79f6f94a` | scalar | 0.02284102604 | PSI of sato between train and out_of_time |
| `psi.out_of_time.season_cos` | `ef947d09` | scalar | 0.004987781308 | PSI of season_cos between train and out_of_time |
| `psi.out_of_time.season_sin` | `fe2b0197` | scalar | 0.01631255179 | PSI of season_sin between train and out_of_time |
| `psi.out_of_time.y_score` | `d39a4ced` | scalar | 0.8371883582 | PSI of the score between train and out_of_time |
| `psi.sato` | `4809116c` | scalar | 0.02284102604 | PSI of sato between train and test |
| `psi.season_cos` | `62ae6c81` | scalar | 0.004987781308 | PSI of season_cos between train and test |
| `psi.season_sin` | `46fec014` | scalar | 0.01631255179 | PSI of season_sin between train and test |
| `psi.vintage_holdout.burnout` | `b2dacb71` | scalar | 0.03122017454 | PSI of burnout between train and vintage_holdout |
| `psi.vintage_holdout.credit_score` | `16906529` | scalar | 0.01928865688 | PSI of credit_score between train and vintage_holdout |
| `psi.vintage_holdout.incentive` | `1d339225` | scalar | 0.2100590512 | PSI of incentive between train and vintage_holdout |
| `psi.vintage_holdout.loan_age` | `e579422e` | scalar | 0.03488721615 | PSI of loan_age between train and vintage_holdout |
| `psi.vintage_holdout.note_rate` | `d4e6aa9a` | scalar | 0.2742521405 | PSI of note_rate between train and vintage_holdout |
| `psi.vintage_holdout.orig_ltv` | `1f0e3df0` | scalar | 0.03575446718 | PSI of orig_ltv between train and vintage_holdout |
| `psi.vintage_holdout.orig_upb_log` | `10fd298a` | scalar | 0.03037586387 | PSI of orig_upb_log between train and vintage_holdout |
| `psi.vintage_holdout.sato` | `6c4e561c` | scalar | 0.02840898929 | PSI of sato between train and vintage_holdout |
| `psi.vintage_holdout.season_cos` | `4482dc21` | scalar | 0.001640289708 | PSI of season_cos between train and vintage_holdout |
| `psi.vintage_holdout.season_sin` | `836b68bf` | scalar | 0.001971264046 | PSI of season_sin between train and vintage_holdout |
| `psi.vintage_holdout.y_score` | `5d010092` | scalar | 0.0820229283 | PSI of the score between train and vintage_holdout |
| `psi.y_score` | `92ac1652` | scalar | 0.8371883582 | PSI of the score between train and test |
| `rule.calibration_first_event_rate` | `42f1351e` | scalar | 0.05 | the event rate below which the report puts calibration before discrimination |
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |
| `scenario.convexity` | `70b14b4a` | scalar | -1094856.426 | the value change at -300 bp plus the change at 300 bp; negative when the fall outweighs the rise |
| `scenario.value_by_shock` | `7ca37cab` | table | table, 7 rows | servicing value, its change from the base case and first-year CPR, by shock |
| `scenario.value_change.-100` | `56c3d7c6` | scalar | -171515.6127 | change in servicing value at -100 bp |
| `scenario.value_change.-200` | `fc12530a` | scalar | -587861.1403 | change in servicing value at -200 bp |
| `scenario.value_change.-300` | `dfaf9b49` | scalar | -1166173.182 | change in servicing value at -300 bp |
| `scenario.value_change.0` | `1e1b0b88` | scalar | 0 | change in servicing value at 0 bp |
| `scenario.value_change.100` | `c5393b58` | scalar | 51212.01224 | change in servicing value at 100 bp |
| `scenario.value_change.200` | `8b1b5955` | scalar | 66659.08481 | change in servicing value at 200 bp |
| `scenario.value_change.300` | `1bebd745` | scalar | 71316.75564 | change in servicing value at 300 bp |
| `sign_check.burnout.agrees` | `2eec20ab` | scalar | 1 | 1 when the fitted sign on burnout agrees with its univariate direction, 0 when it does not |
| `sign_check.burnout.coef_sign` | `a3063608` | scalar | 1 | the sign of the fitted coefficient on burnout |
| `sign_check.burnout.univariate_direction` | `bfc96bb2` | scalar | 1 | the sign of burnout's own single-feature AUC on train minus 0.5 |
| `sign_check.credit_score.agrees` | `915bf8eb` | scalar | 1 | 1 when the fitted sign on credit_score agrees with its univariate direction, 0 when it does not |
| `sign_check.credit_score.coef_sign` | `1ec1078b` | scalar | 1 | the sign of the fitted coefficient on credit_score |
| `sign_check.credit_score.univariate_direction` | `42303896` | scalar | 1 | the sign of credit_score's own single-feature AUC on train minus 0.5 |
| `sign_check.incentive.agrees` | `f7b2338e` | scalar | 1 | 1 when the fitted sign on incentive agrees with its univariate direction, 0 when it does not |
| `sign_check.incentive.coef_sign` | `684cf11a` | scalar | 1 | the sign of the fitted coefficient on incentive |
| `sign_check.incentive.univariate_direction` | `8098d951` | scalar | 1 | the sign of incentive's own single-feature AUC on train minus 0.5 |
| `sign_check.n_disagreements` | `f96ece96` | scalar | 1 | retained features whose fitted sign contradicts their univariate direction, of 9 checked |
| `sign_check.note_rate.agrees` | `a453463d` | scalar | 0 | 1 when the fitted sign on note_rate agrees with its univariate direction, 0 when it does not |
| `sign_check.note_rate.coef_sign` | `aecf7ccb` | scalar | -1 | the sign of the fitted coefficient on note_rate |
| `sign_check.note_rate.univariate_direction` | `61f6e1ac` | scalar | 1 | the sign of note_rate's own single-feature AUC on train minus 0.5 |
| `sign_check.orig_ltv.agrees` | `7021aeb0` | scalar | 1 | 1 when the fitted sign on orig_ltv agrees with its univariate direction, 0 when it does not |
| `sign_check.orig_ltv.coef_sign` | `7eec65ec` | scalar | -1 | the sign of the fitted coefficient on orig_ltv |
| `sign_check.orig_ltv.univariate_direction` | `76dbc708` | scalar | -1 | the sign of orig_ltv's own single-feature AUC on train minus 0.5 |
| `sign_check.orig_upb_log.agrees` | `07a9d3e6` | scalar | 1 | 1 when the fitted sign on orig_upb_log agrees with its univariate direction, 0 when it does not |
| `sign_check.orig_upb_log.coef_sign` | `5aa309fc` | scalar | 1 | the sign of the fitted coefficient on orig_upb_log |
| `sign_check.orig_upb_log.univariate_direction` | `b9743ecb` | scalar | 1 | the sign of orig_upb_log's own single-feature AUC on train minus 0.5 |
| `sign_check.sato.agrees` | `2401eba2` | scalar | 1 | 1 when the fitted sign on sato agrees with its univariate direction, 0 when it does not |
| `sign_check.sato.coef_sign` | `c031d0d5` | scalar | 1 | the sign of the fitted coefficient on sato |
| `sign_check.sato.univariate_direction` | `c08233a6` | scalar | 1 | the sign of sato's own single-feature AUC on train minus 0.5 |
| `sign_check.season_cos.agrees` | `7f18ddf7` | scalar | 1 | 1 when the fitted sign on season_cos agrees with its univariate direction, 0 when it does not |
| `sign_check.season_cos.coef_sign` | `7dbb1ffc` | scalar | -1 | the sign of the fitted coefficient on season_cos |
| `sign_check.season_cos.univariate_direction` | `03e931f0` | scalar | -1 | the sign of season_cos's own single-feature AUC on train minus 0.5 |
| `sign_check.season_sin.agrees` | `e110f357` | scalar | 1 | 1 when the fitted sign on season_sin agrees with its univariate direction, 0 when it does not |
| `sign_check.season_sin.coef_sign` | `761188ce` | scalar | 1 | the sign of the fitted coefficient on season_sin |
| `sign_check.season_sin.univariate_direction` | `cae6b096` | scalar | 1 | the sign of season_sin's own single-feature AUC on train minus 0.5 |
| `stability.auc_by_regime` | `3b0ee961` | table | table, 2 rows | the champion's AUC within each rate_regime on train |
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
| `thresholds.evaluation` | `9aea64d5` | table | table, 4 rows | every threshold package.yaml declares, with its bound, the recomputed value and the outcome |
| `vif.burnout` | `127bbabe` | scalar | 3.601072256 | variance inflation factor of burnout on train |
| `vif.credit_score` | `1f19769b` | scalar | 1.011319432 | variance inflation factor of credit_score on train |
| `vif.incentive` | `60c8eef8` | scalar | 2.195314756 | variance inflation factor of incentive on train |
| `vif.loan_age` | `b30f78aa` | scalar | 2.593200289 | variance inflation factor of loan_age on train |
| `vif.max` | `fecfb289` | scalar | 4.288168629 | the largest variance inflation factor |
| `vif.note_rate` | `1113d019` | scalar | 4.288168629 | variance inflation factor of note_rate on train |
| `vif.orig_ltv` | `d9449fe2` | scalar | 1.013521613 | variance inflation factor of orig_ltv on train |
| `vif.orig_upb_log` | `59e2ab98` | scalar | 1.012256745 | variance inflation factor of orig_upb_log on train |
| `vif.sato` | `4b2ebef2` | scalar | 1.627027838 | variance inflation factor of sato on train |
| `vif.season_cos` | `f741ba51` | scalar | 1.007021417 | variance inflation factor of season_cos on train |
| `vif.season_sin` | `3b05b05a` | scalar | 1.010543525 | variance inflation factor of season_sin on train |

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
| wall-clock (s) | 1.42 |
| subject run (s) | 2.33 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | fake |
| model | none: no model answered |
| run id | msr_prepayment-rules_only-20260918T065352Z-568d25f5 |

## Appendix D — Not checked

| item | reason |
|---|---|
| developer claims (T1, claim channel) | The package declares 3 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
| drafted narrative and the repair loop | `rules_only` calls no model; the narrative is a template |
