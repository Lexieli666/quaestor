---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: msr_prepayment
version: "1.0"
model_type: discrete_time_hazard
configuration: rules_only
model: fake
run_id: msr_prepayment-rules_only-20260918T065347Z-568d25f5
data_mode: synthetic
synthetic_n: 2000
grounding_precision_pre: 1.0000
grounding_precision_post: 1.0000
n_claims: 315
n_findings_by_severity: {high: 0, medium: 1, low: 0, info: 0}
generated: "2026-09-18T06:53:47Z"
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
The value of `calibration_slope.out_of_time` is 1.008 [[art:860e5dd2:calibration_slope.out_of_time]].
The value of `calibration_slope.test` is 0.939 [[art:80d029cc:calibration_slope.test]].
The value of `calibration_slope.train` is 0.9958 [[art:a10d9430:calibration_slope.train]].
The value of `calibration_slope.vintage_holdout` is 0.8363 [[art:20da9c88:calibration_slope.vintage_holdout]].
The value of `challenger.delta_auc` is -0.03936 [[art:46dde851:challenger.delta_auc]].
The value of `condition_number` is 4.941 [[art:cf4a0dab:condition_number]].
The value of `csi.max` is 0.03602 [[art:cf5a5274:csi.max]].
The value of `metrics.out_of_time.auc` is 0.7871 [[art:2e910103:metrics.out_of_time.auc]].
The value of `metrics.out_of_time.brier` is 0.01712 [[art:9dbe134b:metrics.out_of_time.brier]].
The value of `metrics.out_of_time.event_rate` is 0.01795 [[art:83ccf5c0:metrics.out_of_time.event_rate]].
The value of `metrics.out_of_time.gini` is 0.5742 [[art:442c1e75:metrics.out_of_time.gini]].
The value of `metrics.out_of_time.ks` is 0.4422 [[art:c8dd3c8a:metrics.out_of_time.ks]].
The value of `metrics.out_of_time.logloss` is 0.0796 [[art:793f94ec:metrics.out_of_time.logloss]].
The value of `metrics.out_of_time.mean_predicted` is 0.01945 [[art:3cc343ae:metrics.out_of_time.mean_predicted]].
The value of `metrics.out_of_time.n` is 12257 [[art:7898809e:metrics.out_of_time.n]].
The value of `metrics.test.auc` is 0.7759 [[art:225b99b5:metrics.test.auc]].
The value of `metrics.test.brier` is 0.007893 [[art:66eaf26f:metrics.test.brier]].
The value of `metrics.test.event_rate` is 0.008061 [[art:570cc08a:metrics.test.event_rate]].
The value of `metrics.test.gini` is 0.5519 [[art:0aebb8a9:metrics.test.gini]].
The value of `metrics.test.ks` is 0.4195 [[art:3abd1f94:metrics.test.ks]].
The value of `metrics.test.logloss` is 0.04261 [[art:a801271e:metrics.test.logloss]].
The value of `metrics.test.mean_predicted` is 0.008364 [[art:542ddc6b:metrics.test.mean_predicted]].
The value of `metrics.test.n` is 15382 [[art:e55953e1:metrics.test.n]].
The value of `metrics.train.auc` is 0.7888 [[art:88da2e97:metrics.train.auc]].
The value of `metrics.train.brier` is 0.008396 [[art:a3ddd3d7:metrics.train.brier]].
The value of `metrics.train.event_rate` is 0.008609 [[art:73327d6c:metrics.train.event_rate]].
The value of `metrics.train.gini` is 0.5775 [[art:a786960b:metrics.train.gini]].
The value of `metrics.train.ks` is 0.4561 [[art:12bd02b0:metrics.train.ks]].
The value of `metrics.train.logloss` is 0.04442 [[art:fce5969c:metrics.train.logloss]].
The value of `metrics.train.mean_predicted` is 0.008694 [[art:3eee0092:metrics.train.mean_predicted]].
The value of `metrics.train.n` is 36474 [[art:82d2c58e:metrics.train.n]].
The value of `metrics.vintage_holdout.auc` is 0.7722 [[art:ff084e89:metrics.vintage_holdout.auc]].
The value of `metrics.vintage_holdout.brier` is 0.004765 [[art:31ac126b:metrics.vintage_holdout.brier]].
The value of `metrics.vintage_holdout.event_rate` is 0.004817 [[art:e3590a16:metrics.vintage_holdout.event_rate]].
The value of `metrics.vintage_holdout.gini` is 0.5443 [[art:14144a5d:metrics.vintage_holdout.gini]].
The value of `metrics.vintage_holdout.ks` is 0.4492 [[art:178bbe36:metrics.vintage_holdout.ks]].
The value of `metrics.vintage_holdout.logloss` is 0.02814 [[art:e1b4f0f1:metrics.vintage_holdout.logloss]].
The value of `metrics.vintage_holdout.mean_predicted` is 0.005914 [[art:08dbc56d:metrics.vintage_holdout.mean_predicted]].
The value of `metrics.vintage_holdout.n` is 32177 [[art:37a92951:metrics.vintage_holdout.n]].
The value of `profile.test.n` is 15382 [[art:e3abc1b8:profile.test.n]].
The value of `profile.train.n` is 36474 [[art:7e94d818:profile.train.n]].
The value of `psi.max` is 0.06021 [[art:e09026cf:psi.max]].
The value of `runtime.max_seconds` is 300 [[art:2ad8d1a5:runtime.max_seconds]].
The value of `threshold.package.auc.test.min` is 0.65 [[art:fececac1:threshold.package.auc.test.min]].
The value of `threshold.package.calibration_slope.test.max` is 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The value of `threshold.package.calibration_slope.test.min` is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
The value of `vif.max` is 4.973 [[art:d9b015aa:vif.max]].

## 2. Conceptual soundness

This section follows the model risk management guidance at [[reg:SR26-2:V.1.a]].
The value of `ablation.baseline_auc` is 0.7674 [[art:fdbd1084:ablation.baseline_auc]].
The value of `ablation.burnout.delta_auc` is -0.0003018 [[art:177952dc:ablation.burnout.delta_auc]].
The value of `ablation.credit_score.delta_auc` is -0.01477 [[art:479f419e:ablation.credit_score.delta_auc]].
The value of `ablation.incentive.delta_auc` is -0.04119 [[art:7213d612:ablation.incentive.delta_auc]].
The value of `ablation.loan_age.delta_auc` is 0.000814 [[art:863965a3:ablation.loan_age.delta_auc]].
The value of `ablation.note_rate.delta_auc` is -0.002577 [[art:730edeaf:ablation.note_rate.delta_auc]].
The value of `ablation.orig_ltv.delta_auc` is -0.002215 [[art:6b1c5d74:ablation.orig_ltv.delta_auc]].
The value of `ablation.orig_upb_log.delta_auc` is -0.01961 [[art:5bc33417:ablation.orig_upb_log.delta_auc]].
The value of `ablation.sato.delta_auc` is 0.0005941 [[art:c477ddcb:ablation.sato.delta_auc]].
The value of `ablation.season_cos.delta_auc` is -0.000481 [[art:655cfcbe:ablation.season_cos.delta_auc]].
The value of `ablation.season_sin.delta_auc` is -0.0003927 [[art:0b5a4b1b:ablation.season_sin.delta_auc]].
The value of `challenger.auc` is 0.7366 [[art:abe111e2:challenger.auc]].
The value of `challenger.brier` is 0.009228 [[art:acd8735a:challenger.brier]].
The value of `challenger.delta_auc` is -0.03936 [[art:46dde851:challenger.delta_auc]].
The value of `metrics.test.auc` is 0.7759 [[art:225b99b5:metrics.test.auc]].
The value of `metrics.test.brier` is 0.007893 [[art:66eaf26f:metrics.test.brier]].
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
The value of `csi.burnout` is 0.001163 [[art:2af1e79a:csi.burnout]].
The value of `csi.credit_score` is 0.008069 [[art:17137aa1:csi.credit_score]].
The value of `csi.incentive` is 0.005099 [[art:4fb0f08d:csi.incentive]].
The value of `csi.loan_age` is 0 [[art:df52c920:csi.loan_age]].
The value of `csi.max` is 0.03602 [[art:cf5a5274:csi.max]].
The value of `csi.note_rate` is 0.01445 [[art:d8ee67a8:csi.note_rate]].
The value of `csi.orig_ltv` is 0.03602 [[art:5ce12077:csi.orig_ltv]].
The value of `csi.orig_upb_log` is 0.003374 [[art:d6de1f4a:csi.orig_upb_log]].
The value of `csi.sato` is 0.0005107 [[art:5d9bf44b:csi.sato]].
The value of `csi.season_cos` is 0.0006697 [[art:f8939193:csi.season_cos]].
The value of `csi.season_sin` is 0.00005589 [[art:eef3a546:csi.season_sin]].
The value of `leakage.duplicates.train` is 0 [[art:4474c227:leakage.duplicates.train]].
The value of `leakage.name_screen.n_matched` is 0 [[art:407e62be:leakage.name_screen.n_matched]].
The value of `leakage.overlap` is 0.02997 [[art:4fb7c6b6:leakage.overlap]].
The value of `leakage.overlap.features` is 0.02997 [[art:bcbccff8:leakage.overlap.features]].
The value of `leakage.overlap.ids` is 0 [[art:63d37fc5:leakage.overlap.ids]].
The value of `leakage.target_corr.max_single_feature_auc` is 0.7245 [[art:6db1c162:leakage.target_corr.max_single_feature_auc]].
The value of `leakage.timing.n_flagged` is 0 [[art:742bcd24:leakage.timing.n_flagged]].
The value of `profile.out_of_time.missing.max` is 0 [[art:4dafce11:profile.out_of_time.missing.max]].
The value of `profile.out_of_time.n` is 12257 [[art:fa39c5cf:profile.out_of_time.n]].
The value of `profile.test.missing.max` is 0 [[art:f813848d:profile.test.missing.max]].
The value of `profile.test.n` is 15382 [[art:e3abc1b8:profile.test.n]].
The value of `profile.train.missing.max` is 0 [[art:050a3099:profile.train.missing.max]].
The value of `profile.train.n` is 36474 [[art:7e94d818:profile.train.n]].
The value of `profile.vintage_holdout.missing.max` is 0 [[art:329bb430:profile.vintage_holdout.missing.max]].
The value of `profile.vintage_holdout.n` is 32177 [[art:426e712a:profile.vintage_holdout.n]].
The value of `psi.burnout` is 0.004931 [[art:33f5ebc2:psi.burnout]].
The value of `psi.credit_score` is 0.06021 [[art:d18c84c9:psi.credit_score]].
The value of `psi.incentive` is 0.0008807 [[art:68e58ed4:psi.incentive]].
The value of `psi.loan_age` is 0.0001936 [[art:0de705ab:psi.loan_age]].
The value of `psi.max` is 0.06021 [[art:e09026cf:psi.max]].
The value of `psi.note_rate` is 0.009204 [[art:c7f1a67b:psi.note_rate]].
The value of `psi.orig_ltv` is 0.03525 [[art:5a52f767:psi.orig_ltv]].
The value of `psi.orig_upb_log` is 0.04276 [[art:a8060a5e:psi.orig_upb_log]].
The value of `psi.out_of_time.burnout` is 2.941 [[art:2f1775e6:psi.out_of_time.burnout]].
The value of `psi.out_of_time.credit_score` is 0.05907 [[art:736d4786:psi.out_of_time.credit_score]].
The value of `psi.out_of_time.incentive` is 0.496 [[art:8f1aad44:psi.out_of_time.incentive]].
The value of `psi.out_of_time.loan_age` is 2.483 [[art:a53fe5b7:psi.out_of_time.loan_age]].
The value of `psi.out_of_time.note_rate` is 0.698 [[art:41ec908a:psi.out_of_time.note_rate]].
The value of `psi.out_of_time.orig_ltv` is 0.04224 [[art:3e1cfd51:psi.out_of_time.orig_ltv]].
The value of `psi.out_of_time.orig_upb_log` is 0.06798 [[art:bd610e8f:psi.out_of_time.orig_upb_log]].
The value of `psi.out_of_time.sato` is 0.01229 [[art:8c2d71b1:psi.out_of_time.sato]].
The value of `psi.out_of_time.season_cos` is 0.01068 [[art:9bb91b1d:psi.out_of_time.season_cos]].
The value of `psi.out_of_time.season_sin` is 0.02791 [[art:1c848842:psi.out_of_time.season_sin]].
The value of `psi.out_of_time.y_score` is 0.7067 [[art:926393e5:psi.out_of_time.y_score]].
The value of `psi.sato` is 0.02937 [[art:d035c9fe:psi.sato]].
The value of `psi.season_cos` is 0.00002852 [[art:4c164ad6:psi.season_cos]].
The value of `psi.season_sin` is 0.000003361 [[art:34445e67:psi.season_sin]].
The value of `psi.vintage_holdout.burnout` is 0.04787 [[art:d7eb40ee:psi.vintage_holdout.burnout]].
The value of `psi.vintage_holdout.credit_score` is 0.03957 [[art:eb8b579f:psi.vintage_holdout.credit_score]].
The value of `psi.vintage_holdout.incentive` is 0.4468 [[art:a5809fbc:psi.vintage_holdout.incentive]].
The value of `psi.vintage_holdout.loan_age` is 0.07104 [[art:880920e4:psi.vintage_holdout.loan_age]].
The value of `psi.vintage_holdout.note_rate` is 0.6036 [[art:8903dffa:psi.vintage_holdout.note_rate]].
The value of `psi.vintage_holdout.orig_ltv` is 0.02878 [[art:e538a378:psi.vintage_holdout.orig_ltv]].
The value of `psi.vintage_holdout.orig_upb_log` is 0.03584 [[art:983493d4:psi.vintage_holdout.orig_upb_log]].
The value of `psi.vintage_holdout.sato` is 0.03244 [[art:9cde942f:psi.vintage_holdout.sato]].
The value of `psi.vintage_holdout.season_cos` is 0.001415 [[art:0b2e1ed1:psi.vintage_holdout.season_cos]].
The value of `psi.vintage_holdout.season_sin` is 0.0007471 [[art:accfeb86:psi.vintage_holdout.season_sin]].
The value of `psi.vintage_holdout.y_score` is 0.1381 [[art:b7edb3fa:psi.vintage_holdout.y_score]].
The value of `psi.y_score` is 0.001802 [[art:b90e64c8:psi.y_score]].
The value of `threshold.D1.missing_gap` is 0.1 [[art:9cce25ea:threshold.D1.missing_gap]].
The value of `threshold.L1.single_feature_auc` is 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]].
The value of `threshold.L2.overlap` is 0.005 [[art:9f336eaf:threshold.L2.overlap]].
The value of `threshold.L2.overlap.features_effective` is 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].
The value of `threshold.S1.psi` is 0.25 [[art:278b9016:threshold.S1.psi]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
Candidates raised on this section's material: L2 (see the findings section).

## 4. Outcomes analysis

This section follows the model risk management guidance at [[reg:SR26-2:V.1.b]].
The value of `calibration.mean_rel_gap.out_of_time` is 0.08366 [[art:4084ccd4:calibration.mean_rel_gap.out_of_time]].
The value of `calibration.mean_rel_gap.test` is 0.03754 [[art:40409705:calibration.mean_rel_gap.test]].
The value of `calibration.mean_rel_gap.train` is 0.009844 [[art:0b47f454:calibration.mean_rel_gap.train]].
The value of `calibration.mean_rel_gap.vintage_holdout` is 0.2277 [[art:4b6b5371:calibration.mean_rel_gap.vintage_holdout]].
The value of `calibration_intercept.out_of_time` is -0.05834 [[art:e50f09e0:calibration_intercept.out_of_time]].
The value of `calibration_intercept.test` is -0.2952 [[art:f2adc1ec:calibration_intercept.test]].
The value of `calibration_intercept.train` is -0.02732 [[art:f381282b:calibration_intercept.train]].
The value of `calibration_intercept.vintage_holdout` is -0.9462 [[art:1256d464:calibration_intercept.vintage_holdout]].
The value of `calibration_slope.out_of_time` is 1.008 [[art:860e5dd2:calibration_slope.out_of_time]].
The value of `calibration_slope.test` is 0.939 [[art:80d029cc:calibration_slope.test]].
The value of `calibration_slope.train` is 0.9958 [[art:a10d9430:calibration_slope.train]].
The value of `calibration_slope.vintage_holdout` is 0.8363 [[art:20da9c88:calibration_slope.vintage_holdout]].
The value of `cpr.out_of_time.mae` is 0.05671 [[art:6699b093:cpr.out_of_time.mae]].
The value of `cpr.test.mae` is 0.04285 [[art:13564933:cpr.test.mae]].
The value of `cpr.train.mae` is 0.02615 [[art:1baf9f3a:cpr.train.mae]].
The value of `cpr.vintage_holdout.mae` is 0.03048 [[art:34f4c62c:cpr.vintage_holdout.mae]].
The value of `deciles.out_of_time.top2_capture` is 0.5864 [[art:e28ccabb:deciles.out_of_time.top2_capture]].
The value of `deciles.test.top2_capture` is 0.5806 [[art:43c4adc5:deciles.test.top2_capture]].
The value of `deciles.train.top2_capture` is 0.5955 [[art:adaecbab:deciles.train.top2_capture]].
The value of `deciles.vintage_holdout.top2_capture` is 0.5806 [[art:0d0c0310:deciles.vintage_holdout.top2_capture]].
The value of `metrics.out_of_time.auc` is 0.7871 [[art:2e910103:metrics.out_of_time.auc]].
The value of `metrics.out_of_time.brier` is 0.01712 [[art:9dbe134b:metrics.out_of_time.brier]].
The value of `metrics.out_of_time.event_rate` is 0.01795 [[art:83ccf5c0:metrics.out_of_time.event_rate]].
The value of `metrics.out_of_time.gini` is 0.5742 [[art:442c1e75:metrics.out_of_time.gini]].
The value of `metrics.out_of_time.ks` is 0.4422 [[art:c8dd3c8a:metrics.out_of_time.ks]].
The value of `metrics.out_of_time.logloss` is 0.0796 [[art:793f94ec:metrics.out_of_time.logloss]].
The value of `metrics.out_of_time.mean_predicted` is 0.01945 [[art:3cc343ae:metrics.out_of_time.mean_predicted]].
The value of `metrics.out_of_time.n` is 12257 [[art:7898809e:metrics.out_of_time.n]].
The value of `metrics.test.auc` is 0.7759 [[art:225b99b5:metrics.test.auc]].
The value of `metrics.test.brier` is 0.007893 [[art:66eaf26f:metrics.test.brier]].
The value of `metrics.test.event_rate` is 0.008061 [[art:570cc08a:metrics.test.event_rate]].
The value of `metrics.test.gini` is 0.5519 [[art:0aebb8a9:metrics.test.gini]].
The value of `metrics.test.ks` is 0.4195 [[art:3abd1f94:metrics.test.ks]].
The value of `metrics.test.logloss` is 0.04261 [[art:a801271e:metrics.test.logloss]].
The value of `metrics.test.mean_predicted` is 0.008364 [[art:542ddc6b:metrics.test.mean_predicted]].
The value of `metrics.test.n` is 15382 [[art:e55953e1:metrics.test.n]].
The value of `metrics.train.auc` is 0.7888 [[art:88da2e97:metrics.train.auc]].
The value of `metrics.train.brier` is 0.008396 [[art:a3ddd3d7:metrics.train.brier]].
The value of `metrics.train.event_rate` is 0.008609 [[art:73327d6c:metrics.train.event_rate]].
The value of `metrics.train.gini` is 0.5775 [[art:a786960b:metrics.train.gini]].
The value of `metrics.train.ks` is 0.4561 [[art:12bd02b0:metrics.train.ks]].
The value of `metrics.train.logloss` is 0.04442 [[art:fce5969c:metrics.train.logloss]].
The value of `metrics.train.mean_predicted` is 0.008694 [[art:3eee0092:metrics.train.mean_predicted]].
The value of `metrics.train.n` is 36474 [[art:82d2c58e:metrics.train.n]].
The value of `metrics.vintage_holdout.auc` is 0.7722 [[art:ff084e89:metrics.vintage_holdout.auc]].
The value of `metrics.vintage_holdout.brier` is 0.004765 [[art:31ac126b:metrics.vintage_holdout.brier]].
The value of `metrics.vintage_holdout.event_rate` is 0.004817 [[art:e3590a16:metrics.vintage_holdout.event_rate]].
The value of `metrics.vintage_holdout.gini` is 0.5443 [[art:14144a5d:metrics.vintage_holdout.gini]].
The value of `metrics.vintage_holdout.ks` is 0.4492 [[art:178bbe36:metrics.vintage_holdout.ks]].
The value of `metrics.vintage_holdout.logloss` is 0.02814 [[art:e1b4f0f1:metrics.vintage_holdout.logloss]].
The value of `metrics.vintage_holdout.mean_predicted` is 0.005914 [[art:08dbc56d:metrics.vintage_holdout.mean_predicted]].
The value of `metrics.vintage_holdout.n` is 32177 [[art:37a92951:metrics.vintage_holdout.n]].
The value of `psi.burnout` is 0.004931 [[art:33f5ebc2:psi.burnout]].
The value of `psi.credit_score` is 0.06021 [[art:d18c84c9:psi.credit_score]].
The value of `psi.incentive` is 0.0008807 [[art:68e58ed4:psi.incentive]].
The value of `psi.loan_age` is 0.0001936 [[art:0de705ab:psi.loan_age]].
The value of `psi.max` is 0.06021 [[art:e09026cf:psi.max]].
The value of `psi.note_rate` is 0.009204 [[art:c7f1a67b:psi.note_rate]].
The value of `psi.orig_ltv` is 0.03525 [[art:5a52f767:psi.orig_ltv]].
The value of `psi.orig_upb_log` is 0.04276 [[art:a8060a5e:psi.orig_upb_log]].
The value of `psi.out_of_time.burnout` is 2.941 [[art:2f1775e6:psi.out_of_time.burnout]].
The value of `psi.out_of_time.credit_score` is 0.05907 [[art:736d4786:psi.out_of_time.credit_score]].
The value of `psi.out_of_time.incentive` is 0.496 [[art:8f1aad44:psi.out_of_time.incentive]].
The value of `psi.out_of_time.loan_age` is 2.483 [[art:a53fe5b7:psi.out_of_time.loan_age]].
The value of `psi.out_of_time.note_rate` is 0.698 [[art:41ec908a:psi.out_of_time.note_rate]].
The value of `psi.out_of_time.orig_ltv` is 0.04224 [[art:3e1cfd51:psi.out_of_time.orig_ltv]].
The value of `psi.out_of_time.orig_upb_log` is 0.06798 [[art:bd610e8f:psi.out_of_time.orig_upb_log]].
The value of `psi.out_of_time.sato` is 0.01229 [[art:8c2d71b1:psi.out_of_time.sato]].
The value of `psi.out_of_time.season_cos` is 0.01068 [[art:9bb91b1d:psi.out_of_time.season_cos]].
The value of `psi.out_of_time.season_sin` is 0.02791 [[art:1c848842:psi.out_of_time.season_sin]].
The value of `psi.out_of_time.y_score` is 0.7067 [[art:926393e5:psi.out_of_time.y_score]].
The value of `psi.sato` is 0.02937 [[art:d035c9fe:psi.sato]].
The value of `psi.season_cos` is 0.00002852 [[art:4c164ad6:psi.season_cos]].
The value of `psi.season_sin` is 0.000003361 [[art:34445e67:psi.season_sin]].
The value of `psi.vintage_holdout.burnout` is 0.04787 [[art:d7eb40ee:psi.vintage_holdout.burnout]].
The value of `psi.vintage_holdout.credit_score` is 0.03957 [[art:eb8b579f:psi.vintage_holdout.credit_score]].
The value of `psi.vintage_holdout.incentive` is 0.4468 [[art:a5809fbc:psi.vintage_holdout.incentive]].
The value of `psi.vintage_holdout.loan_age` is 0.07104 [[art:880920e4:psi.vintage_holdout.loan_age]].
The value of `psi.vintage_holdout.note_rate` is 0.6036 [[art:8903dffa:psi.vintage_holdout.note_rate]].
The value of `psi.vintage_holdout.orig_ltv` is 0.02878 [[art:e538a378:psi.vintage_holdout.orig_ltv]].
The value of `psi.vintage_holdout.orig_upb_log` is 0.03584 [[art:983493d4:psi.vintage_holdout.orig_upb_log]].
The value of `psi.vintage_holdout.sato` is 0.03244 [[art:9cde942f:psi.vintage_holdout.sato]].
The value of `psi.vintage_holdout.season_cos` is 0.001415 [[art:0b2e1ed1:psi.vintage_holdout.season_cos]].
The value of `psi.vintage_holdout.season_sin` is 0.0007471 [[art:accfeb86:psi.vintage_holdout.season_sin]].
The value of `psi.vintage_holdout.y_score` is 0.1381 [[art:b7edb3fa:psi.vintage_holdout.y_score]].
The value of `psi.y_score` is 0.001802 [[art:b90e64c8:psi.y_score]].
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
Calibration by decile of predicted probability on test [[art:9633f335:calibration.test]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.000432 | 0.0006498 | 1539 |
| 2 | 0.0009024 | 0.001949 | 1539 |
| 3 | 0.001508 | 0.002601 | 1538 |
| 4 | 0.00238 | 0.002601 | 1538 |
| 5 | 0.003578 | 0.003251 | 1538 |
| 6 | 0.005278 | 0.005202 | 1538 |
| 7 | 0.007781 | 0.009103 | 1538 |
| 8 | 0.01156 | 0.008453 | 1538 |
| 9 | 0.01744 | 0.01235 | 1538 |
| 10 | 0.03278 | 0.03446 | 1538 |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table cpr.test -->
Actual against predicted CPR by period on test [[art:28397851:cpr.test]]:

| period | n | actual_cpr | predicted_cpr |
|---|---|---|---|
| 201402 | 15 | 0 | 0.03606 |
| 201403 | 28 | 0 | 0.03138 |
| 201404 | 56 | 0 | 0.02273 |
| 201405 | 68 | 0 | 0.0225 |
| 201406 | 80 | 0 | 0.02227 |
| 201407 | 97 | 0.1169 | 0.01873 |
| 201408 | 111 | 0 | 0.0162 |
| 201409 | 133 | 0.08659 | 0.01253 |
| 201410 | 145 | 0 | 0.01034 |
| 201411 | 161 | 0 | 0.00803 |
| 201412 | 175 | 0 | 0.007633 |
| 201501 | 198 | 0 | 0.007151 |
| 201502 | 198 | 0 | 0.006816 |
| 201503 | 198 | 0.05895 | 0.008539 |
| 201504 | 197 | 0 | 0.009596 |
| 201505 | 197 | 0 | 0.01364 |
| 201506 | 197 | 0 | 0.0157 |
| 201507 | 197 | 0 | 0.02068 |
| 201508 | 197 | 0 | 0.02857 |
| 201509 | 197 | 0.05924 | 0.03113 |
| 201510 | 196 | 0.05954 | 0.03822 |
| 201511 | 195 | 0 | 0.04848 |
| 201512 | 195 | 0 | 0.04981 |
| 201601 | 195 | 0.1698 | 0.07096 |
| 201602 | 192 | 0.06074 | 0.1045 |
| 201603 | 191 | 0.1187 | 0.1404 |
| 201604 | 189 | 0.1198 | 0.1581 |
| 201605 | 187 | 0.3673 | 0.2184 |
| 201606 | 180 | 0.1255 | 0.2176 |
| 201607 | 178 | 0.1268 | 0.2298 |
| 201608 | 176 | 0.06609 | 0.2104 |
| 201609 | 175 | 0.1288 | 0.1657 |
| 201610 | 173 | 0.1893 | 0.1199 |
| 201611 | 170 | 0.06835 | 0.09839 |
| 201612 | 169 | 0.06874 | 0.06992 |
| 201701 | 168 | 0.1339 | 0.05696 |
| 201702 | 176 | 0.2924 | 0.04801 |
| 201703 | 191 | 0.06105 | 0.04173 |
| 201704 | 199 | 0 | 0.03695 |
| 201705 | 218 | 0.05368 | 0.03717 |
| 201706 | 238 | 0.04927 | 0.03395 |
| 201707 | 248 | 0 | 0.02939 |
| 201708 | 274 | 0 | 0.02284 |
| 201709 | 284 | 0.08131 | 0.0233 |
| 201710 | 300 | 0 | 0.01748 |
| 201711 | 323 | 0.03653 | 0.01692 |
| 201712 | 334 | 0.03534 | 0.02102 |
| 201801 | 354 | 0.03338 | 0.02394 |
| 201802 | 353 | 0.06591 | 0.03304 |
| 201803 | 351 | 0.03366 | 0.05231 |
| 201804 | 350 | 0.06646 | 0.08342 |
| 201805 | 348 | 0.1594 | 0.1294 |
| 201806 | 343 | 0.1616 | 0.1561 |
| 201807 | 338 | 0.1638 | 0.1696 |
| 201808 | 333 | 0.06974 | 0.182 |
| 201809 | 331 | 0.2544 | 0.19 |
| 201810 | 323 | 0.1707 | 0.1805 |
| 201811 | 318 | 0.07292 | 0.1608 |
| 201812 | 316 | 0.1742 | 0.1784 |
| 201901 | 311 | 0.1098 | 0.1883 |
| 201902 | 300 | 0.1488 | 0.2245 |
| 201903 | 285 | 0.2253 | 0.2431 |
| 201904 | 258 | 0.246 | 0.2381 |
| 201905 | 243 | 0.1385 | 0.215 |
| 201906 | 233 | 0.2688 | 0.1787 |
| 201907 | 219 | 0.1984 | 0.1289 |
| 201908 | 206 | 0 | 0.09191 |
| 201909 | 191 | 0.06105 | 0.06184 |
| 201910 | 182 | 0.06398 | 0.04343 |
| 201911 | 171 | 0.06796 | 0.0377 |
| 201912 | 166 | 0 | 0.0362 |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table deciles.test -->
Decile separation on test; decile 1 holds the highest probabilities [[art:8e91a22f:deciles.test]]:

| decile | count | events | event_rate | lift |
|---|---|---|---|---|
| 1 | 1539 | 53 | 0.03444 | 4.272 |
| 2 | 1539 | 19 | 0.01235 | 1.531 |
| 3 | 1538 | 13 | 0.008453 | 1.049 |
| 4 | 1538 | 14 | 0.009103 | 1.129 |
| 5 | 1538 | 8 | 0.005202 | 0.6452 |
| 6 | 1538 | 5 | 0.003251 | 0.4033 |
| 7 | 1538 | 4 | 0.002601 | 0.3226 |
| 8 | 1538 | 4 | 0.002601 | 0.3226 |
| 9 | 1538 | 3 | 0.001951 | 0.242 |
| 10 | 1538 | 1 | 0.0006502 | 0.08066 |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table thresholds.evaluation -->
Every threshold package.yaml declares, with its bound, the recomputed value and the outcome [[art:6eb162e0:thresholds.evaluation]]:

| metric | split | bound | value | result |
|---|---|---|---|---|
| auc | test | minimum 0.65 | 0.7759 | pass |
| calibration_slope | test | minimum 0.8 | 0.939 | pass |
| calibration_slope | test | maximum 1.2 | 0.939 | pass |
| psi |  | maximum 0.25 | 0.06021 | pass |
<!-- quaestor:renderer:end -->

## 5. Sensitivity and scenario analysis

This section follows the model risk management guidance at [[reg:SR26-2:V.1.a]].
The value of `condition_number` is 4.941 [[art:cf4a0dab:condition_number]].
The value of `scenario.convexity` is -1154000 [[art:e6e5c89b:scenario.convexity]].
The value of `scenario.value_change.-100` is -295200 [[art:8d716ed3:scenario.value_change.-100]].
The value of `scenario.value_change.-200` is -821800 [[art:fc515a18:scenario.value_change.-200]].
The value of `scenario.value_change.-300` is -1300000 [[art:1bb5faa9:scenario.value_change.-300]].
The value of `scenario.value_change.0` is 0 [[art:1e1b0b88:scenario.value_change.0]].
The value of `scenario.value_change.100` is 103800 [[art:32d76ec2:scenario.value_change.100]].
The value of `scenario.value_change.200` is 135900 [[art:9ff1104d:scenario.value_change.200]].
The value of `scenario.value_change.300` is 145400 [[art:a5bb5830:scenario.value_change.300]].
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
The value of `vif.burnout` is 3.442 [[art:15d2d2b7:vif.burnout]].
The value of `vif.credit_score` is 1.008 [[art:8908e744:vif.credit_score]].
The value of `vif.incentive` is 2.226 [[art:13d92899:vif.incentive]].
The value of `vif.loan_age` is 2.929 [[art:da5f6107:vif.loan_age]].
The value of `vif.max` is 4.973 [[art:d9b015aa:vif.max]].
The value of `vif.note_rate` is 4.973 [[art:dfd3d0c7:vif.note_rate]].
The value of `vif.orig_ltv` is 1.004 [[art:ca78c9fc:vif.orig_ltv]].
The value of `vif.orig_upb_log` is 1.006 [[art:127ff775:vif.orig_upb_log]].
The value of `vif.sato` is 1.708 [[art:4802c713:vif.sato]].
The value of `vif.season_cos` is 1.018 [[art:0046feb1:vif.season_cos]].
The value of `vif.season_sin` is 1.004 [[art:c19a5e9a:vif.season_sin]].
<!-- quaestor:renderer:begin table scenario.value_by_shock -->
Servicing value, its change from the base case and first-year CPR, by shock [[art:51e09003:scenario.value_by_shock]]:

| shock_bp | value | value_change | cpr |
|---|---|---|---|
| -300 | 320300 | -1.3e+06 | 0.6116 |
| -200 | 798200 | -821800 | 0.2468 |
| -100 | 1.325e+06 | -295200 | 0.07814 |
| 0 | 1.62e+06 | 0 | 0.02294 |
| 100 | 1.724e+06 | 103800 | 0.006652 |
| 200 | 1.756e+06 | 135900 | 0.001921 |
| 300 | 1.765e+06 | 145400 | 0.0005536 |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table stability.auc_by_regime -->
The champion's AUC within each rate_regime on train [[art:411b1cfe:stability.auc_by_regime]]:

| regime | n | event_rate | auc |
|---|---|---|---|
| falling | 18092 | 0.01443 | 0.7249 |
| rising | 18382 | 0.002883 | 0.7323 |
<!-- quaestor:renderer:end -->

## 6. Findings and recommendations

This section follows the model risk management guidance at [[reg:SR26-2:VI.3]].

### F-001 · L2 contamination · severity **medium**

**A `L2` finding, raised by `check_leakage` at severity `medium`.**
Its evidence is the artifacts cited in this section; the check's own account of it is recorded in `findings.json`.
The value of `leakage.duplicates.train` is 0 [[art:4474c227:leakage.duplicates.train]].
The value of `leakage.overlap.features` is 0.02997 [[art:bcbccff8:leakage.overlap.features]].
The value of `sign_check.note_rate.agrees` is 0 [[art:a453463d:sign_check.note_rate.agrees]].
The value of `sign_check.note_rate.coef_sign` is -1 [[art:aecf7ccb:sign_check.note_rate.coef_sign]].
The value of `sign_check.note_rate.univariate_direction` is 1 [[art:61f6e1ac:sign_check.note_rate.univariate_direction]].
The value of `threshold.L2.overlap` is 0.005 [[art:9f336eaf:threshold.L2.overlap]].
The value of `threshold.L2.overlap.features_effective` is 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1, S1), `compute_metrics` (T1, C1, O1), `check_leakage` (L1), `check_stability` (R1), `check_collinearity` (M1), `challenger_compare` (E1), `run_scenarios` (X1).

### Open items

No open item was recorded for this validation.

## 7. Ongoing monitoring recommendations

This section follows the model risk management guidance at [[reg:SR26-2:V.2]].
The value of `calibration_slope.test` is 0.939 [[art:80d029cc:calibration_slope.test]].
The value of `metrics.test.auc` is 0.7759 [[art:225b99b5:metrics.test.auc]].
The value of `psi.max` is 0.06021 [[art:e09026cf:psi.max]].
The value of `rule.calibration_first_event_rate` is 0.05 [[art:42f1351e:rule.calibration_first_event_rate]].
The value of `threshold.package.auc.test.min` is 0.65 [[art:fececac1:threshold.package.auc.test.min]].
The value of `threshold.package.calibration_slope.test.max` is 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The value of `threshold.package.calibration_slope.test.min` is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].

## Appendix A — Claims

Grounding precision 1.0000 before repair (315 of 315 claims verified) and 1.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 48/48; conceptual_soundness 45/45; data_integrity 66/66; outcomes 106/106; sensitivity 35/35; findings 7/7; monitoring 8/8.

Developer claims: The package declares 3 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). See Appendix D.

Excluded numeric tokens (not claims): inline_code (`scenario.value_change.-100`, `scenario.value_change.-200`, `scenario.value_change.-300`); citation_hash (860e5dd2, 80d029cc, a10d9430, 20da9c88); regulatory_section_id (SR26-2:V.1.b, SR26-2:V.1.a, SR26-2:VI.3, SR26-2:V.2); finding_id (F-001).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The value of `calibration_slope.out_of_time` is 1.008 . | 1.008 | ratio | calibration_slope |  | eq | `[[art:860e5dd2:calibration_slope.out_of_time]]` | verified | 1.007762878 |
| 2 | summary | The value of `calibration_slope.test` is 0.939 . | 0.939 | ratio | calibration_slope |  | eq | `[[art:80d029cc:calibration_slope.test]]` | verified | 0.9389856921 |
| 3 | summary | The value of `calibration_slope.train` is 0.9958 . | 0.9958 | ratio | calibration_slope |  | eq | `[[art:a10d9430:calibration_slope.train]]` | verified | 0.9958299755 |
| 4 | summary | The value of `calibration_slope.vintage_holdout` is 0.8363 . | 0.8363 | ratio | calibration_slope |  | eq | `[[art:20da9c88:calibration_slope.vintage_holdout]]` | verified | 0.8363376022 |
| 5 | summary | The value of `challenger.delta_auc` is -0.03936 . | -0.03936 | ratio | challenger |  | eq | `[[art:46dde851:challenger.delta_auc]]` | verified | -0.03936168863 |
| 6 | summary | The value of `condition_number` is 4.941 . | 4.941 | ratio | condition_number |  | eq | `[[art:cf4a0dab:condition_number]]` | verified | 4.941319585 |
| 7 | summary | The value of `csi.max` is 0.03602 . | 0.03602 | ratio | csi |  | eq | `[[art:cf5a5274:csi.max]]` | verified | 0.0360163058 |
| 8 | summary | The value of `metrics.out_of_time.auc` is 0.7871 . | 0.7871 | ratio | metrics |  | eq | `[[art:2e910103:metrics.out_of_time.auc]]` | verified | 0.7871132191 |
| 9 | summary | The value of `metrics.out_of_time.brier` is 0.01712 . | 0.01712 | ratio | metrics |  | eq | `[[art:9dbe134b:metrics.out_of_time.brier]]` | verified | 0.01712189167 |
| 10 | summary | The value of `metrics.out_of_time.event_rate` is 0.01795 . | 0.01795 | ratio | metrics |  | eq | `[[art:83ccf5c0:metrics.out_of_time.event_rate]]` | verified | 0.01794892714 |
| 11 | summary | The value of `metrics.out_of_time.gini` is 0.5742 . | 0.5742 | ratio | metrics |  | eq | `[[art:442c1e75:metrics.out_of_time.gini]]` | verified | 0.5742264382 |
| 12 | summary | The value of `metrics.out_of_time.ks` is 0.4422 . | 0.4422 | ratio | metrics |  | eq | `[[art:c8dd3c8a:metrics.out_of_time.ks]]` | verified | 0.4421873466 |
| 13 | summary | The value of `metrics.out_of_time.logloss` is 0.0796 . | 0.0796 | ratio | metrics |  | eq | `[[art:793f94ec:metrics.out_of_time.logloss]]` | verified | 0.07960455821 |
| 14 | summary | The value of `metrics.out_of_time.mean_predicted` is 0.01945… | 0.01945 | ratio | metrics |  | eq | `[[art:3cc343ae:metrics.out_of_time.mean_predicted]]` | verified | 0.01945061747 |
| 15 | summary | The value of `metrics.out_of_time.n` is 12257 . | 12257 | ratio | metrics |  | eq | `[[art:7898809e:metrics.out_of_time.n]]` | verified | 12257 |
| 16 | summary | The value of `metrics.test.auc` is 0.7759 . | 0.7759 | ratio | metrics |  | eq | `[[art:225b99b5:metrics.test.auc]]` | verified | 0.7759451414 |
| 17 | summary | The value of `metrics.test.brier` is 0.007893 . | 0.007893 | ratio | metrics |  | eq | `[[art:66eaf26f:metrics.test.brier]]` | verified | 0.007892754939 |
| 18 | summary | The value of `metrics.test.event_rate` is 0.008061 . | 0.008061 | ratio | metrics |  | eq | `[[art:570cc08a:metrics.test.event_rate]]` | verified | 0.008061370433 |
| 19 | summary | The value of `metrics.test.gini` is 0.5519 . | 0.5519 | ratio | metrics |  | eq | `[[art:0aebb8a9:metrics.test.gini]]` | verified | 0.5518902828 |
| 20 | summary | The value of `metrics.test.ks` is 0.4195 . | 0.4195 | ratio | metrics |  | eq | `[[art:3abd1f94:metrics.test.ks]]` | verified | 0.4194605474 |
| 21 | summary | The value of `metrics.test.logloss` is 0.04261 . | 0.04261 | ratio | metrics |  | eq | `[[art:a801271e:metrics.test.logloss]]` | verified | 0.04261094263 |
| 22 | summary | The value of `metrics.test.mean_predicted` is 0.008364 . | 0.008364 | ratio | metrics |  | eq | `[[art:542ddc6b:metrics.test.mean_predicted]]` | verified | 0.008363991555 |
| 23 | summary | The value of `metrics.test.n` is 15382 . | 15382 | ratio | metrics |  | eq | `[[art:e55953e1:metrics.test.n]]` | verified | 15382 |
| 24 | summary | The value of `metrics.train.auc` is 0.7888 . | 0.7888 | ratio | metrics |  | eq | `[[art:88da2e97:metrics.train.auc]]` | verified | 0.7887583845 |
| 25 | summary | The value of `metrics.train.brier` is 0.008396 . | 0.008396 | ratio | metrics |  | eq | `[[art:a3ddd3d7:metrics.train.brier]]` | verified | 0.008396301302 |
| 26 | summary | The value of `metrics.train.event_rate` is 0.008609 . | 0.008609 | ratio | metrics |  | eq | `[[art:73327d6c:metrics.train.event_rate]]` | verified | 0.008608872073 |
| 27 | summary | The value of `metrics.train.gini` is 0.5775 . | 0.5775 | ratio | metrics |  | eq | `[[art:a786960b:metrics.train.gini]]` | verified | 0.5775167691 |
| 28 | summary | The value of `metrics.train.ks` is 0.4561 . | 0.4561 | ratio | metrics |  | eq | `[[art:12bd02b0:metrics.train.ks]]` | verified | 0.4560599388 |
| 29 | summary | The value of `metrics.train.logloss` is 0.04442 . | 0.04442 | ratio | metrics |  | eq | `[[art:fce5969c:metrics.train.logloss]]` | verified | 0.04441572278 |
| 30 | summary | The value of `metrics.train.mean_predicted` is 0.008694 . | 0.008694 | ratio | metrics |  | eq | `[[art:3eee0092:metrics.train.mean_predicted]]` | verified | 0.008693620795 |
| 31 | summary | The value of `metrics.train.n` is 36474 . | 36474 | ratio | metrics |  | eq | `[[art:82d2c58e:metrics.train.n]]` | verified | 36474 |
| 32 | summary | The value of `metrics.vintage_holdout.auc` is 0.7722 . | 0.7722 | ratio | metrics |  | eq | `[[art:ff084e89:metrics.vintage_holdout.auc]]` | verified | 0.7721582541 |
| 33 | summary | The value of `metrics.vintage_holdout.brier` is 0.004765 . | 0.004765 | ratio | metrics |  | eq | `[[art:31ac126b:metrics.vintage_holdout.brier]]` | verified | 0.00476513883 |
| 34 | summary | The value of `metrics.vintage_holdout.event_rate` is 0.00481… | 0.004817 | ratio | metrics |  | eq | `[[art:e3590a16:metrics.vintage_holdout.event_rate]]` | verified | 0.004817105386 |
| 35 | summary | The value of `metrics.vintage_holdout.gini` is 0.5443 . | 0.5443 | ratio | metrics |  | eq | `[[art:14144a5d:metrics.vintage_holdout.gini]]` | verified | 0.5443165082 |
| 36 | summary | The value of `metrics.vintage_holdout.ks` is 0.4492 . | 0.4492 | ratio | metrics |  | eq | `[[art:178bbe36:metrics.vintage_holdout.ks]]` | verified | 0.4492226111 |
| 37 | summary | The value of `metrics.vintage_holdout.logloss` is 0.02814 . | 0.02814 | ratio | metrics |  | eq | `[[art:e1b4f0f1:metrics.vintage_holdout.logloss]]` | verified | 0.02814470369 |
| 38 | summary | The value of `metrics.vintage_holdout.mean_predicted` is 0.0… | 0.005914 | ratio | metrics |  | eq | `[[art:08dbc56d:metrics.vintage_holdout.mean_predicted]]` | verified | 0.005913917042 |
| 39 | summary | The value of `metrics.vintage_holdout.n` is 32177 . | 32177 | ratio | metrics |  | eq | `[[art:37a92951:metrics.vintage_holdout.n]]` | verified | 32177 |
| 40 | summary | The value of `profile.test.n` is 15382 . | 15382 | ratio | profile |  | eq | `[[art:e3abc1b8:profile.test.n]]` | verified | 15382 |
| 41 | summary | The value of `profile.train.n` is 36474 . | 36474 | ratio | profile |  | eq | `[[art:7e94d818:profile.train.n]]` | verified | 36474 |
| 42 | summary | The value of `psi.max` is 0.06021 . | 0.06021 | ratio | psi |  | eq | `[[art:e09026cf:psi.max]]` | verified | 0.06021122495 |
| 43 | summary | The value of `runtime.max_seconds` is 300 . | 300 | ratio | runtime |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 44 | summary | The value of `threshold.package.auc.test.min` is 0.65 . | 0.65 | ratio | threshold |  | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 45 | summary | The value of `threshold.package.calibration_slope.test.max`… | 1.2 | ratio | threshold |  | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 46 | summary | The value of `threshold.package.calibration_slope.test.min`… | 0.8 | ratio | threshold |  | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 47 | summary | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 48 | summary | The value of `vif.max` is 4.973 . | 4.973 | ratio | vif |  | eq | `[[art:d9b015aa:vif.max]]` | verified | 4.973309839 |
| 49 | conceptual_soundness | The value of `ablation.baseline_auc` is 0.7674 . | 0.7674 | ratio | ablation |  | eq | `[[art:fdbd1084:ablation.baseline_auc]]` | verified | 0.7674403486 |
| 50 | conceptual_soundness | The value of `ablation.burnout.delta_auc` is -0.0003018 . | -0.0003018 | ratio | ablation |  | eq | `[[art:177952dc:ablation.burnout.delta_auc]]` | verified | -0.0003017983163 |
| 51 | conceptual_soundness | The value of `ablation.credit_score.delta_auc` is -0.01477 . | -0.01477 | ratio | ablation |  | eq | `[[art:479f419e:ablation.credit_score.delta_auc]]` | verified | -0.01477490391 |
| 52 | conceptual_soundness | The value of `ablation.incentive.delta_auc` is -0.04119 . | -0.04119 | ratio | ablation |  | eq | `[[art:7213d612:ablation.incentive.delta_auc]]` | verified | -0.04118780629 |
| 53 | conceptual_soundness | The value of `ablation.loan_age.delta_auc` is 0.000814 . | 0.000814 | ratio | ablation |  | eq | `[[art:863965a3:ablation.loan_age.delta_auc]]` | verified | 0.0008139569301 |
| 54 | conceptual_soundness | The value of `ablation.note_rate.delta_auc` is -0.002577 . | -0.002577 | ratio | ablation |  | eq | `[[art:730edeaf:ablation.note_rate.delta_auc]]` | verified | -0.002577177916 |
| 55 | conceptual_soundness | The value of `ablation.orig_ltv.delta_auc` is -0.002215 . | -0.002215 | ratio | ablation |  | eq | `[[art:6b1c5d74:ablation.orig_ltv.delta_auc]]` | verified | -0.002214597102 |
| 56 | conceptual_soundness | The value of `ablation.orig_upb_log.delta_auc` is -0.01961 . | -0.01961 | ratio | ablation |  | eq | `[[art:5bc33417:ablation.orig_upb_log.delta_auc]]` | verified | -0.01960949095 |
| 57 | conceptual_soundness | The value of `ablation.sato.delta_auc` is 0.0005941 . | 0.0005941 | ratio | ablation |  | eq | `[[art:c477ddcb:ablation.sato.delta_auc]]` | verified | 0.0005940828502 |
| 58 | conceptual_soundness | The value of `ablation.season_cos.delta_auc` is -0.000481 . | -0.000481 | ratio | ablation |  | eq | `[[art:655cfcbe:ablation.season_cos.delta_auc]]` | verified | -0.0004809745496 |
| 59 | conceptual_soundness | The value of `ablation.season_sin.delta_auc` is -0.0003927 . | -0.0003927 | ratio | ablation |  | eq | `[[art:0b5a4b1b:ablation.season_sin.delta_auc]]` | verified | -0.0003927077916 |
| 60 | conceptual_soundness | The value of `challenger.auc` is 0.7366 . | 0.7366 | ratio | challenger |  | eq | `[[art:abe111e2:challenger.auc]]` | verified | 0.7365834528 |
| 61 | conceptual_soundness | The value of `challenger.brier` is 0.009228 . | 0.009228 | ratio | challenger |  | eq | `[[art:acd8735a:challenger.brier]]` | verified | 0.009228035552 |
| 62 | conceptual_soundness | The value of `challenger.delta_auc` is -0.03936 . | -0.03936 | ratio | challenger |  | eq | `[[art:46dde851:challenger.delta_auc]]` | verified | -0.03936168863 |
| 63 | conceptual_soundness | The value of `metrics.test.auc` is 0.7759 . | 0.7759 | ratio | metrics |  | eq | `[[art:225b99b5:metrics.test.auc]]` | verified | 0.7759451414 |
| 64 | conceptual_soundness | The value of `metrics.test.brier` is 0.007893 . | 0.007893 | ratio | metrics |  | eq | `[[art:66eaf26f:metrics.test.brier]]` | verified | 0.007892754939 |
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
| 94 | data_integrity | The value of `csi.burnout` is 0.001163 . | 0.001163 | ratio | csi |  | eq | `[[art:2af1e79a:csi.burnout]]` | verified | 0.001162803488 |
| 95 | data_integrity | The value of `csi.credit_score` is 0.008069 . | 0.008069 | ratio | csi |  | eq | `[[art:17137aa1:csi.credit_score]]` | verified | 0.008068926476 |
| 96 | data_integrity | The value of `csi.incentive` is 0.005099 . | 0.005099 | ratio | csi |  | eq | `[[art:4fb0f08d:csi.incentive]]` | verified | 0.005098722582 |
| 97 | data_integrity | The value of `csi.loan_age` is 0 . | 0 | ratio | csi |  | eq | `[[art:df52c920:csi.loan_age]]` | verified | 0 |
| 98 | data_integrity | The value of `csi.max` is 0.03602 . | 0.03602 | ratio | csi |  | eq | `[[art:cf5a5274:csi.max]]` | verified | 0.0360163058 |
| 99 | data_integrity | The value of `csi.note_rate` is 0.01445 . | 0.01445 | ratio | csi |  | eq | `[[art:d8ee67a8:csi.note_rate]]` | verified | 0.01444840152 |
| 100 | data_integrity | The value of `csi.orig_ltv` is 0.03602 . | 0.03602 | ratio | csi |  | eq | `[[art:5ce12077:csi.orig_ltv]]` | verified | 0.0360163058 |
| 101 | data_integrity | The value of `csi.orig_upb_log` is 0.003374 . | 0.003374 | ratio | csi |  | eq | `[[art:d6de1f4a:csi.orig_upb_log]]` | verified | 0.003374084917 |
| 102 | data_integrity | The value of `csi.sato` is 0.0005107 . | 0.0005107 | ratio | csi |  | eq | `[[art:5d9bf44b:csi.sato]]` | verified | 0.0005107233981 |
| 103 | data_integrity | The value of `csi.season_cos` is 0.0006697 . | 0.0006697 | ratio | csi |  | eq | `[[art:f8939193:csi.season_cos]]` | verified | 0.0006696922627 |
| 104 | data_integrity | The value of `csi.season_sin` is 0.00005589 . | 5.589e-05 | ratio | csi |  | eq | `[[art:eef3a546:csi.season_sin]]` | verified | 5.589052952e-05 |
| 105 | data_integrity | The value of `leakage.duplicates.train` is 0 . | 0 | ratio | leakage |  | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 106 | data_integrity | The value of `leakage.name_screen.n_matched` is 0 . | 0 | ratio | leakage |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 107 | data_integrity | The value of `leakage.overlap` is 0.02997 . | 0.02997 | ratio | leakage |  | eq | `[[art:4fb7c6b6:leakage.overlap]]` | verified | 0.02997009492 |
| 108 | data_integrity | The value of `leakage.overlap.features` is 0.02997 . | 0.02997 | ratio | leakage |  | eq | `[[art:bcbccff8:leakage.overlap.features]]` | verified | 0.02997009492 |
| 109 | data_integrity | The value of `leakage.overlap.ids` is 0 . | 0 | ratio | leakage |  | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 110 | data_integrity | The value of `leakage.target_corr.max_single_feature_auc` is… | 0.7245 | ratio | leakage |  | eq | `[[art:6db1c162:leakage.target_corr.max_single_feature_auc]]` | verified | 0.7244788731 |
| 111 | data_integrity | The value of `leakage.timing.n_flagged` is 0 . | 0 | ratio | leakage |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 112 | data_integrity | The value of `profile.out_of_time.missing.max` is 0 . | 0 | ratio | profile |  | eq | `[[art:4dafce11:profile.out_of_time.missing.max]]` | verified | 0 |
| 113 | data_integrity | The value of `profile.out_of_time.n` is 12257 . | 12257 | ratio | profile |  | eq | `[[art:fa39c5cf:profile.out_of_time.n]]` | verified | 12257 |
| 114 | data_integrity | The value of `profile.test.missing.max` is 0 . | 0 | ratio | profile |  | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 115 | data_integrity | The value of `profile.test.n` is 15382 . | 15382 | ratio | profile |  | eq | `[[art:e3abc1b8:profile.test.n]]` | verified | 15382 |
| 116 | data_integrity | The value of `profile.train.missing.max` is 0 . | 0 | ratio | profile |  | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 117 | data_integrity | The value of `profile.train.n` is 36474 . | 36474 | ratio | profile |  | eq | `[[art:7e94d818:profile.train.n]]` | verified | 36474 |
| 118 | data_integrity | The value of `profile.vintage_holdout.missing.max` is 0 . | 0 | ratio | profile |  | eq | `[[art:329bb430:profile.vintage_holdout.missing.max]]` | verified | 0 |
| 119 | data_integrity | The value of `profile.vintage_holdout.n` is 32177 . | 32177 | ratio | profile |  | eq | `[[art:426e712a:profile.vintage_holdout.n]]` | verified | 32177 |
| 120 | data_integrity | The value of `psi.burnout` is 0.004931 . | 0.004931 | ratio | psi |  | eq | `[[art:33f5ebc2:psi.burnout]]` | verified | 0.004931216889 |
| 121 | data_integrity | The value of `psi.credit_score` is 0.06021 . | 0.06021 | ratio | psi |  | eq | `[[art:d18c84c9:psi.credit_score]]` | verified | 0.06021122495 |
| 122 | data_integrity | The value of `psi.incentive` is 0.0008807 . | 0.0008807 | ratio | psi |  | eq | `[[art:68e58ed4:psi.incentive]]` | verified | 0.0008807210511 |
| 123 | data_integrity | The value of `psi.loan_age` is 0.0001936 . | 0.0001936 | ratio | psi |  | eq | `[[art:0de705ab:psi.loan_age]]` | verified | 0.0001935522768 |
| 124 | data_integrity | The value of `psi.max` is 0.06021 . | 0.06021 | ratio | psi |  | eq | `[[art:e09026cf:psi.max]]` | verified | 0.06021122495 |
| 125 | data_integrity | The value of `psi.note_rate` is 0.009204 . | 0.009204 | ratio | psi |  | eq | `[[art:c7f1a67b:psi.note_rate]]` | verified | 0.009203799735 |
| 126 | data_integrity | The value of `psi.orig_ltv` is 0.03525 . | 0.03525 | ratio | psi |  | eq | `[[art:5a52f767:psi.orig_ltv]]` | verified | 0.03524928958 |
| 127 | data_integrity | The value of `psi.orig_upb_log` is 0.04276 . | 0.04276 | ratio | psi |  | eq | `[[art:a8060a5e:psi.orig_upb_log]]` | verified | 0.04275593453 |
| 128 | data_integrity | The value of `psi.out_of_time.burnout` is 2.941 . | 2.941 | ratio | psi |  | eq | `[[art:2f1775e6:psi.out_of_time.burnout]]` | verified | 2.940517648 |
| 129 | data_integrity | The value of `psi.out_of_time.credit_score` is 0.05907 . | 0.05907 | ratio | psi |  | eq | `[[art:736d4786:psi.out_of_time.credit_score]]` | verified | 0.05906553221 |
| 130 | data_integrity | The value of `psi.out_of_time.incentive` is 0.496 . | 0.496 | ratio | psi |  | eq | `[[art:8f1aad44:psi.out_of_time.incentive]]` | verified | 0.4959842347 |
| 131 | data_integrity | The value of `psi.out_of_time.loan_age` is 2.483 . | 2.483 | ratio | psi |  | eq | `[[art:a53fe5b7:psi.out_of_time.loan_age]]` | verified | 2.482521703 |
| 132 | data_integrity | The value of `psi.out_of_time.note_rate` is 0.698 . | 0.698 | ratio | psi |  | eq | `[[art:41ec908a:psi.out_of_time.note_rate]]` | verified | 0.6979848935 |
| 133 | data_integrity | The value of `psi.out_of_time.orig_ltv` is 0.04224 . | 0.04224 | ratio | psi |  | eq | `[[art:3e1cfd51:psi.out_of_time.orig_ltv]]` | verified | 0.04223900725 |
| 134 | data_integrity | The value of `psi.out_of_time.orig_upb_log` is 0.06798 . | 0.06798 | ratio | psi |  | eq | `[[art:bd610e8f:psi.out_of_time.orig_upb_log]]` | verified | 0.0679791761 |
| 135 | data_integrity | The value of `psi.out_of_time.sato` is 0.01229 . | 0.01229 | ratio | psi |  | eq | `[[art:8c2d71b1:psi.out_of_time.sato]]` | verified | 0.01229057251 |
| 136 | data_integrity | The value of `psi.out_of_time.season_cos` is 0.01068 . | 0.01068 | ratio | psi |  | eq | `[[art:9bb91b1d:psi.out_of_time.season_cos]]` | verified | 0.01068186712 |
| 137 | data_integrity | The value of `psi.out_of_time.season_sin` is 0.02791 . | 0.02791 | ratio | psi |  | eq | `[[art:1c848842:psi.out_of_time.season_sin]]` | verified | 0.02790812853 |
| 138 | data_integrity | The value of `psi.out_of_time.y_score` is 0.7067 . | 0.7067 | ratio | psi |  | eq | `[[art:926393e5:psi.out_of_time.y_score]]` | verified | 0.706727876 |
| 139 | data_integrity | The value of `psi.sato` is 0.02937 . | 0.02937 | ratio | psi |  | eq | `[[art:d035c9fe:psi.sato]]` | verified | 0.02937047655 |
| 140 | data_integrity | The value of `psi.season_cos` is 0.00002852 . | 2.852e-05 | ratio | psi |  | eq | `[[art:4c164ad6:psi.season_cos]]` | verified | 2.852014247e-05 |
| 141 | data_integrity | The value of `psi.season_sin` is 0.000003361 . | 3.361e-06 | ratio | psi |  | eq | `[[art:34445e67:psi.season_sin]]` | verified | 3.360751567e-06 |
| 142 | data_integrity | The value of `psi.vintage_holdout.burnout` is 0.04787 . | 0.04787 | ratio | psi |  | eq | `[[art:d7eb40ee:psi.vintage_holdout.burnout]]` | verified | 0.04787342519 |
| 143 | data_integrity | The value of `psi.vintage_holdout.credit_score` is 0.03957 . | 0.03957 | ratio | psi |  | eq | `[[art:eb8b579f:psi.vintage_holdout.credit_score]]` | verified | 0.03956501951 |
| 144 | data_integrity | The value of `psi.vintage_holdout.incentive` is 0.4468 . | 0.4468 | ratio | psi |  | eq | `[[art:a5809fbc:psi.vintage_holdout.incentive]]` | verified | 0.4467844664 |
| 145 | data_integrity | The value of `psi.vintage_holdout.loan_age` is 0.07104 . | 0.07104 | ratio | psi |  | eq | `[[art:880920e4:psi.vintage_holdout.loan_age]]` | verified | 0.07103580061 |
| 146 | data_integrity | The value of `psi.vintage_holdout.note_rate` is 0.6036 . | 0.6036 | ratio | psi |  | eq | `[[art:8903dffa:psi.vintage_holdout.note_rate]]` | verified | 0.6035871138 |
| 147 | data_integrity | The value of `psi.vintage_holdout.orig_ltv` is 0.02878 . | 0.02878 | ratio | psi |  | eq | `[[art:e538a378:psi.vintage_holdout.orig_ltv]]` | verified | 0.0287751179 |
| 148 | data_integrity | The value of `psi.vintage_holdout.orig_upb_log` is 0.03584 . | 0.03584 | ratio | psi |  | eq | `[[art:983493d4:psi.vintage_holdout.orig_upb_log]]` | verified | 0.03584175044 |
| 149 | data_integrity | The value of `psi.vintage_holdout.sato` is 0.03244 . | 0.03244 | ratio | psi |  | eq | `[[art:9cde942f:psi.vintage_holdout.sato]]` | verified | 0.03244197722 |
| 150 | data_integrity | The value of `psi.vintage_holdout.season_cos` is 0.001415 . | 0.001415 | ratio | psi |  | eq | `[[art:0b2e1ed1:psi.vintage_holdout.season_cos]]` | verified | 0.001415335964 |
| 151 | data_integrity | The value of `psi.vintage_holdout.season_sin` is 0.0007471 . | 0.0007471 | ratio | psi |  | eq | `[[art:accfeb86:psi.vintage_holdout.season_sin]]` | verified | 0.0007471395641 |
| 152 | data_integrity | The value of `psi.vintage_holdout.y_score` is 0.1381 . | 0.1381 | ratio | psi |  | eq | `[[art:b7edb3fa:psi.vintage_holdout.y_score]]` | verified | 0.1381257303 |
| 153 | data_integrity | The value of `psi.y_score` is 0.001802 . | 0.001802 | ratio | psi |  | eq | `[[art:b90e64c8:psi.y_score]]` | verified | 0.001802030258 |
| 154 | data_integrity | The value of `threshold.D1.missing_gap` is 0.1 . | 0.1 | ratio | threshold |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 155 | data_integrity | The value of `threshold.L1.single_feature_auc` is 0.9 . | 0.9 | ratio | threshold |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 156 | data_integrity | The value of `threshold.L2.overlap` is 0.005 . | 0.005 | ratio | threshold |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 157 | data_integrity | The value of `threshold.L2.overlap.features_effective` is 0.… | 0.005 | ratio | threshold |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 158 | data_integrity | The value of `threshold.S1.psi` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 159 | data_integrity | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 160 | outcomes | The value of `calibration.mean_rel_gap.out_of_time` is 0.083… | 0.08366 | ratio | calibration |  | eq | `[[art:4084ccd4:calibration.mean_rel_gap.out_of_time]]` | verified | 0.08366462899 |
| 161 | outcomes | The value of `calibration.mean_rel_gap.test` is 0.03754 . | 0.03754 | ratio | calibration |  | eq | `[[art:40409705:calibration.mean_rel_gap.test]]` | verified | 0.03753966213 |
| 162 | outcomes | The value of `calibration.mean_rel_gap.train` is 0.009844 . | 0.009844 | ratio | calibration |  | eq | `[[art:0b47f454:calibration.mean_rel_gap.train]]` | verified | 0.009844346741 |
| 163 | outcomes | The value of `calibration.mean_rel_gap.vintage_holdout` is 0… | 0.2277 | ratio | calibration |  | eq | `[[art:4b6b5371:calibration.mean_rel_gap.vintage_holdout]]` | verified | 0.2276910236 |
| 164 | outcomes | The value of `calibration_intercept.out_of_time` is -0.05834… | -0.05834 | ratio | calibration_intercept |  | eq | `[[art:e50f09e0:calibration_intercept.out_of_time]]` | verified | -0.0583358688 |
| 165 | outcomes | The value of `calibration_intercept.test` is -0.2952 . | -0.2952 | ratio | calibration_intercept |  | eq | `[[art:f2adc1ec:calibration_intercept.test]]` | verified | -0.2952175968 |
| 166 | outcomes | The value of `calibration_intercept.train` is -0.02732 . | -0.02732 | ratio | calibration_intercept |  | eq | `[[art:f381282b:calibration_intercept.train]]` | verified | -0.02732327203 |
| 167 | outcomes | The value of `calibration_intercept.vintage_holdout` is -0.9… | -0.9462 | ratio | calibration_intercept |  | eq | `[[art:1256d464:calibration_intercept.vintage_holdout]]` | verified | -0.9462036021 |
| 168 | outcomes | The value of `calibration_slope.out_of_time` is 1.008 . | 1.008 | ratio | calibration_slope |  | eq | `[[art:860e5dd2:calibration_slope.out_of_time]]` | verified | 1.007762878 |
| 169 | outcomes | The value of `calibration_slope.test` is 0.939 . | 0.939 | ratio | calibration_slope |  | eq | `[[art:80d029cc:calibration_slope.test]]` | verified | 0.9389856921 |
| 170 | outcomes | The value of `calibration_slope.train` is 0.9958 . | 0.9958 | ratio | calibration_slope |  | eq | `[[art:a10d9430:calibration_slope.train]]` | verified | 0.9958299755 |
| 171 | outcomes | The value of `calibration_slope.vintage_holdout` is 0.8363 . | 0.8363 | ratio | calibration_slope |  | eq | `[[art:20da9c88:calibration_slope.vintage_holdout]]` | verified | 0.8363376022 |
| 172 | outcomes | The value of `cpr.out_of_time.mae` is 0.05671 . | 0.05671 | ratio | cpr |  | eq | `[[art:6699b093:cpr.out_of_time.mae]]` | verified | 0.05670843092 |
| 173 | outcomes | The value of `cpr.test.mae` is 0.04285 . | 0.04285 | ratio | cpr |  | eq | `[[art:13564933:cpr.test.mae]]` | verified | 0.04285359689 |
| 174 | outcomes | The value of `cpr.train.mae` is 0.02615 . | 0.02615 | ratio | cpr |  | eq | `[[art:1baf9f3a:cpr.train.mae]]` | verified | 0.02615146691 |
| 175 | outcomes | The value of `cpr.vintage_holdout.mae` is 0.03048 . | 0.03048 | ratio | cpr |  | eq | `[[art:34f4c62c:cpr.vintage_holdout.mae]]` | verified | 0.03048231099 |
| 176 | outcomes | The value of `deciles.out_of_time.top2_capture` is 0.5864 . | 0.5864 | ratio | deciles |  | eq | `[[art:e28ccabb:deciles.out_of_time.top2_capture]]` | verified | 0.5863636364 |
| 177 | outcomes | The value of `deciles.test.top2_capture` is 0.5806 . | 0.5806 | ratio | deciles |  | eq | `[[art:43c4adc5:deciles.test.top2_capture]]` | verified | 0.5806451613 |
| 178 | outcomes | The value of `deciles.train.top2_capture` is 0.5955 . | 0.5955 | ratio | deciles |  | eq | `[[art:adaecbab:deciles.train.top2_capture]]` | verified | 0.5955414013 |
| 179 | outcomes | The value of `deciles.vintage_holdout.top2_capture` is 0.580… | 0.5806 | ratio | deciles |  | eq | `[[art:0d0c0310:deciles.vintage_holdout.top2_capture]]` | verified | 0.5806451613 |
| 180 | outcomes | The value of `metrics.out_of_time.auc` is 0.7871 . | 0.7871 | ratio | metrics |  | eq | `[[art:2e910103:metrics.out_of_time.auc]]` | verified | 0.7871132191 |
| 181 | outcomes | The value of `metrics.out_of_time.brier` is 0.01712 . | 0.01712 | ratio | metrics |  | eq | `[[art:9dbe134b:metrics.out_of_time.brier]]` | verified | 0.01712189167 |
| 182 | outcomes | The value of `metrics.out_of_time.event_rate` is 0.01795 . | 0.01795 | ratio | metrics |  | eq | `[[art:83ccf5c0:metrics.out_of_time.event_rate]]` | verified | 0.01794892714 |
| 183 | outcomes | The value of `metrics.out_of_time.gini` is 0.5742 . | 0.5742 | ratio | metrics |  | eq | `[[art:442c1e75:metrics.out_of_time.gini]]` | verified | 0.5742264382 |
| 184 | outcomes | The value of `metrics.out_of_time.ks` is 0.4422 . | 0.4422 | ratio | metrics |  | eq | `[[art:c8dd3c8a:metrics.out_of_time.ks]]` | verified | 0.4421873466 |
| 185 | outcomes | The value of `metrics.out_of_time.logloss` is 0.0796 . | 0.0796 | ratio | metrics |  | eq | `[[art:793f94ec:metrics.out_of_time.logloss]]` | verified | 0.07960455821 |
| 186 | outcomes | The value of `metrics.out_of_time.mean_predicted` is 0.01945… | 0.01945 | ratio | metrics |  | eq | `[[art:3cc343ae:metrics.out_of_time.mean_predicted]]` | verified | 0.01945061747 |
| 187 | outcomes | The value of `metrics.out_of_time.n` is 12257 . | 12257 | ratio | metrics |  | eq | `[[art:7898809e:metrics.out_of_time.n]]` | verified | 12257 |
| 188 | outcomes | The value of `metrics.test.auc` is 0.7759 . | 0.7759 | ratio | metrics |  | eq | `[[art:225b99b5:metrics.test.auc]]` | verified | 0.7759451414 |
| 189 | outcomes | The value of `metrics.test.brier` is 0.007893 . | 0.007893 | ratio | metrics |  | eq | `[[art:66eaf26f:metrics.test.brier]]` | verified | 0.007892754939 |
| 190 | outcomes | The value of `metrics.test.event_rate` is 0.008061 . | 0.008061 | ratio | metrics |  | eq | `[[art:570cc08a:metrics.test.event_rate]]` | verified | 0.008061370433 |
| 191 | outcomes | The value of `metrics.test.gini` is 0.5519 . | 0.5519 | ratio | metrics |  | eq | `[[art:0aebb8a9:metrics.test.gini]]` | verified | 0.5518902828 |
| 192 | outcomes | The value of `metrics.test.ks` is 0.4195 . | 0.4195 | ratio | metrics |  | eq | `[[art:3abd1f94:metrics.test.ks]]` | verified | 0.4194605474 |
| 193 | outcomes | The value of `metrics.test.logloss` is 0.04261 . | 0.04261 | ratio | metrics |  | eq | `[[art:a801271e:metrics.test.logloss]]` | verified | 0.04261094263 |
| 194 | outcomes | The value of `metrics.test.mean_predicted` is 0.008364 . | 0.008364 | ratio | metrics |  | eq | `[[art:542ddc6b:metrics.test.mean_predicted]]` | verified | 0.008363991555 |
| 195 | outcomes | The value of `metrics.test.n` is 15382 . | 15382 | ratio | metrics |  | eq | `[[art:e55953e1:metrics.test.n]]` | verified | 15382 |
| 196 | outcomes | The value of `metrics.train.auc` is 0.7888 . | 0.7888 | ratio | metrics |  | eq | `[[art:88da2e97:metrics.train.auc]]` | verified | 0.7887583845 |
| 197 | outcomes | The value of `metrics.train.brier` is 0.008396 . | 0.008396 | ratio | metrics |  | eq | `[[art:a3ddd3d7:metrics.train.brier]]` | verified | 0.008396301302 |
| 198 | outcomes | The value of `metrics.train.event_rate` is 0.008609 . | 0.008609 | ratio | metrics |  | eq | `[[art:73327d6c:metrics.train.event_rate]]` | verified | 0.008608872073 |
| 199 | outcomes | The value of `metrics.train.gini` is 0.5775 . | 0.5775 | ratio | metrics |  | eq | `[[art:a786960b:metrics.train.gini]]` | verified | 0.5775167691 |
| 200 | outcomes | The value of `metrics.train.ks` is 0.4561 . | 0.4561 | ratio | metrics |  | eq | `[[art:12bd02b0:metrics.train.ks]]` | verified | 0.4560599388 |
| 201 | outcomes | The value of `metrics.train.logloss` is 0.04442 . | 0.04442 | ratio | metrics |  | eq | `[[art:fce5969c:metrics.train.logloss]]` | verified | 0.04441572278 |
| 202 | outcomes | The value of `metrics.train.mean_predicted` is 0.008694 . | 0.008694 | ratio | metrics |  | eq | `[[art:3eee0092:metrics.train.mean_predicted]]` | verified | 0.008693620795 |
| 203 | outcomes | The value of `metrics.train.n` is 36474 . | 36474 | ratio | metrics |  | eq | `[[art:82d2c58e:metrics.train.n]]` | verified | 36474 |
| 204 | outcomes | The value of `metrics.vintage_holdout.auc` is 0.7722 . | 0.7722 | ratio | metrics |  | eq | `[[art:ff084e89:metrics.vintage_holdout.auc]]` | verified | 0.7721582541 |
| 205 | outcomes | The value of `metrics.vintage_holdout.brier` is 0.004765 . | 0.004765 | ratio | metrics |  | eq | `[[art:31ac126b:metrics.vintage_holdout.brier]]` | verified | 0.00476513883 |
| 206 | outcomes | The value of `metrics.vintage_holdout.event_rate` is 0.00481… | 0.004817 | ratio | metrics |  | eq | `[[art:e3590a16:metrics.vintage_holdout.event_rate]]` | verified | 0.004817105386 |
| 207 | outcomes | The value of `metrics.vintage_holdout.gini` is 0.5443 . | 0.5443 | ratio | metrics |  | eq | `[[art:14144a5d:metrics.vintage_holdout.gini]]` | verified | 0.5443165082 |
| 208 | outcomes | The value of `metrics.vintage_holdout.ks` is 0.4492 . | 0.4492 | ratio | metrics |  | eq | `[[art:178bbe36:metrics.vintage_holdout.ks]]` | verified | 0.4492226111 |
| 209 | outcomes | The value of `metrics.vintage_holdout.logloss` is 0.02814 . | 0.02814 | ratio | metrics |  | eq | `[[art:e1b4f0f1:metrics.vintage_holdout.logloss]]` | verified | 0.02814470369 |
| 210 | outcomes | The value of `metrics.vintage_holdout.mean_predicted` is 0.0… | 0.005914 | ratio | metrics |  | eq | `[[art:08dbc56d:metrics.vintage_holdout.mean_predicted]]` | verified | 0.005913917042 |
| 211 | outcomes | The value of `metrics.vintage_holdout.n` is 32177 . | 32177 | ratio | metrics |  | eq | `[[art:37a92951:metrics.vintage_holdout.n]]` | verified | 32177 |
| 212 | outcomes | The value of `psi.burnout` is 0.004931 . | 0.004931 | ratio | psi |  | eq | `[[art:33f5ebc2:psi.burnout]]` | verified | 0.004931216889 |
| 213 | outcomes | The value of `psi.credit_score` is 0.06021 . | 0.06021 | ratio | psi |  | eq | `[[art:d18c84c9:psi.credit_score]]` | verified | 0.06021122495 |
| 214 | outcomes | The value of `psi.incentive` is 0.0008807 . | 0.0008807 | ratio | psi |  | eq | `[[art:68e58ed4:psi.incentive]]` | verified | 0.0008807210511 |
| 215 | outcomes | The value of `psi.loan_age` is 0.0001936 . | 0.0001936 | ratio | psi |  | eq | `[[art:0de705ab:psi.loan_age]]` | verified | 0.0001935522768 |
| 216 | outcomes | The value of `psi.max` is 0.06021 . | 0.06021 | ratio | psi |  | eq | `[[art:e09026cf:psi.max]]` | verified | 0.06021122495 |
| 217 | outcomes | The value of `psi.note_rate` is 0.009204 . | 0.009204 | ratio | psi |  | eq | `[[art:c7f1a67b:psi.note_rate]]` | verified | 0.009203799735 |
| 218 | outcomes | The value of `psi.orig_ltv` is 0.03525 . | 0.03525 | ratio | psi |  | eq | `[[art:5a52f767:psi.orig_ltv]]` | verified | 0.03524928958 |
| 219 | outcomes | The value of `psi.orig_upb_log` is 0.04276 . | 0.04276 | ratio | psi |  | eq | `[[art:a8060a5e:psi.orig_upb_log]]` | verified | 0.04275593453 |
| 220 | outcomes | The value of `psi.out_of_time.burnout` is 2.941 . | 2.941 | ratio | psi |  | eq | `[[art:2f1775e6:psi.out_of_time.burnout]]` | verified | 2.940517648 |
| 221 | outcomes | The value of `psi.out_of_time.credit_score` is 0.05907 . | 0.05907 | ratio | psi |  | eq | `[[art:736d4786:psi.out_of_time.credit_score]]` | verified | 0.05906553221 |
| 222 | outcomes | The value of `psi.out_of_time.incentive` is 0.496 . | 0.496 | ratio | psi |  | eq | `[[art:8f1aad44:psi.out_of_time.incentive]]` | verified | 0.4959842347 |
| 223 | outcomes | The value of `psi.out_of_time.loan_age` is 2.483 . | 2.483 | ratio | psi |  | eq | `[[art:a53fe5b7:psi.out_of_time.loan_age]]` | verified | 2.482521703 |
| 224 | outcomes | The value of `psi.out_of_time.note_rate` is 0.698 . | 0.698 | ratio | psi |  | eq | `[[art:41ec908a:psi.out_of_time.note_rate]]` | verified | 0.6979848935 |
| 225 | outcomes | The value of `psi.out_of_time.orig_ltv` is 0.04224 . | 0.04224 | ratio | psi |  | eq | `[[art:3e1cfd51:psi.out_of_time.orig_ltv]]` | verified | 0.04223900725 |
| 226 | outcomes | The value of `psi.out_of_time.orig_upb_log` is 0.06798 . | 0.06798 | ratio | psi |  | eq | `[[art:bd610e8f:psi.out_of_time.orig_upb_log]]` | verified | 0.0679791761 |
| 227 | outcomes | The value of `psi.out_of_time.sato` is 0.01229 . | 0.01229 | ratio | psi |  | eq | `[[art:8c2d71b1:psi.out_of_time.sato]]` | verified | 0.01229057251 |
| 228 | outcomes | The value of `psi.out_of_time.season_cos` is 0.01068 . | 0.01068 | ratio | psi |  | eq | `[[art:9bb91b1d:psi.out_of_time.season_cos]]` | verified | 0.01068186712 |
| 229 | outcomes | The value of `psi.out_of_time.season_sin` is 0.02791 . | 0.02791 | ratio | psi |  | eq | `[[art:1c848842:psi.out_of_time.season_sin]]` | verified | 0.02790812853 |
| 230 | outcomes | The value of `psi.out_of_time.y_score` is 0.7067 . | 0.7067 | ratio | psi |  | eq | `[[art:926393e5:psi.out_of_time.y_score]]` | verified | 0.706727876 |
| 231 | outcomes | The value of `psi.sato` is 0.02937 . | 0.02937 | ratio | psi |  | eq | `[[art:d035c9fe:psi.sato]]` | verified | 0.02937047655 |
| 232 | outcomes | The value of `psi.season_cos` is 0.00002852 . | 2.852e-05 | ratio | psi |  | eq | `[[art:4c164ad6:psi.season_cos]]` | verified | 2.852014247e-05 |
| 233 | outcomes | The value of `psi.season_sin` is 0.000003361 . | 3.361e-06 | ratio | psi |  | eq | `[[art:34445e67:psi.season_sin]]` | verified | 3.360751567e-06 |
| 234 | outcomes | The value of `psi.vintage_holdout.burnout` is 0.04787 . | 0.04787 | ratio | psi |  | eq | `[[art:d7eb40ee:psi.vintage_holdout.burnout]]` | verified | 0.04787342519 |
| 235 | outcomes | The value of `psi.vintage_holdout.credit_score` is 0.03957 . | 0.03957 | ratio | psi |  | eq | `[[art:eb8b579f:psi.vintage_holdout.credit_score]]` | verified | 0.03956501951 |
| 236 | outcomes | The value of `psi.vintage_holdout.incentive` is 0.4468 . | 0.4468 | ratio | psi |  | eq | `[[art:a5809fbc:psi.vintage_holdout.incentive]]` | verified | 0.4467844664 |
| 237 | outcomes | The value of `psi.vintage_holdout.loan_age` is 0.07104 . | 0.07104 | ratio | psi |  | eq | `[[art:880920e4:psi.vintage_holdout.loan_age]]` | verified | 0.07103580061 |
| 238 | outcomes | The value of `psi.vintage_holdout.note_rate` is 0.6036 . | 0.6036 | ratio | psi |  | eq | `[[art:8903dffa:psi.vintage_holdout.note_rate]]` | verified | 0.6035871138 |
| 239 | outcomes | The value of `psi.vintage_holdout.orig_ltv` is 0.02878 . | 0.02878 | ratio | psi |  | eq | `[[art:e538a378:psi.vintage_holdout.orig_ltv]]` | verified | 0.0287751179 |
| 240 | outcomes | The value of `psi.vintage_holdout.orig_upb_log` is 0.03584 . | 0.03584 | ratio | psi |  | eq | `[[art:983493d4:psi.vintage_holdout.orig_upb_log]]` | verified | 0.03584175044 |
| 241 | outcomes | The value of `psi.vintage_holdout.sato` is 0.03244 . | 0.03244 | ratio | psi |  | eq | `[[art:9cde942f:psi.vintage_holdout.sato]]` | verified | 0.03244197722 |
| 242 | outcomes | The value of `psi.vintage_holdout.season_cos` is 0.001415 . | 0.001415 | ratio | psi |  | eq | `[[art:0b2e1ed1:psi.vintage_holdout.season_cos]]` | verified | 0.001415335964 |
| 243 | outcomes | The value of `psi.vintage_holdout.season_sin` is 0.0007471 . | 0.0007471 | ratio | psi |  | eq | `[[art:accfeb86:psi.vintage_holdout.season_sin]]` | verified | 0.0007471395641 |
| 244 | outcomes | The value of `psi.vintage_holdout.y_score` is 0.1381 . | 0.1381 | ratio | psi |  | eq | `[[art:b7edb3fa:psi.vintage_holdout.y_score]]` | verified | 0.1381257303 |
| 245 | outcomes | The value of `psi.y_score` is 0.001802 . | 0.001802 | ratio | psi |  | eq | `[[art:b90e64c8:psi.y_score]]` | verified | 0.001802030258 |
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
| 266 | sensitivity | The value of `condition_number` is 4.941 . | 4.941 | ratio | condition_number |  | eq | `[[art:cf4a0dab:condition_number]]` | verified | 4.941319585 |
| 267 | sensitivity | The value of `scenario.convexity` is -1154000 . | -1154000 | ratio | scenario |  | eq | `[[art:e6e5c89b:scenario.convexity]]` | verified | -1154347.998 |
| 268 | sensitivity | The value of `scenario.value_change.-100` is -295200 . | -295200 | ratio | scenario |  | eq | `[[art:8d716ed3:scenario.value_change.-100]]` | verified | -295185.0824 |
| 269 | sensitivity | The value of `scenario.value_change.-200` is -821800 . | -821800 | ratio | scenario |  | eq | `[[art:fc515a18:scenario.value_change.-200]]` | verified | -821809.3771 |
| 270 | sensitivity | The value of `scenario.value_change.-300` is -1300000 . | -1300000 | ratio | scenario |  | eq | `[[art:1bb5faa9:scenario.value_change.-300]]` | verified | -1299764.383 |
| 271 | sensitivity | The value of `scenario.value_change.0` is 0 . | 0 | ratio | scenario |  | eq | `[[art:1e1b0b88:scenario.value_change.0]]` | verified | 0 |
| 272 | sensitivity | The value of `scenario.value_change.100` is 103800 . | 103800 | ratio | scenario |  | eq | `[[art:32d76ec2:scenario.value_change.100]]` | verified | 103821.8979 |
| 273 | sensitivity | The value of `scenario.value_change.200` is 135900 . | 135900 | ratio | scenario |  | eq | `[[art:9ff1104d:scenario.value_change.200]]` | verified | 135913.6115 |
| 274 | sensitivity | The value of `scenario.value_change.300` is 145400 . | 145400 | ratio | scenario |  | eq | `[[art:a5bb5830:scenario.value_change.300]]` | verified | 145416.3854 |
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
| 290 | sensitivity | The value of `vif.burnout` is 3.442 . | 3.442 | ratio | vif |  | eq | `[[art:15d2d2b7:vif.burnout]]` | verified | 3.441796277 |
| 291 | sensitivity | The value of `vif.credit_score` is 1.008 . | 1.008 | ratio | vif |  | eq | `[[art:8908e744:vif.credit_score]]` | verified | 1.007807025 |
| 292 | sensitivity | The value of `vif.incentive` is 2.226 . | 2.226 | ratio | vif |  | eq | `[[art:13d92899:vif.incentive]]` | verified | 2.225948498 |
| 293 | sensitivity | The value of `vif.loan_age` is 2.929 . | 2.929 | ratio | vif |  | eq | `[[art:da5f6107:vif.loan_age]]` | verified | 2.928894489 |
| 294 | sensitivity | The value of `vif.max` is 4.973 . | 4.973 | ratio | vif |  | eq | `[[art:d9b015aa:vif.max]]` | verified | 4.973309839 |
| 295 | sensitivity | The value of `vif.note_rate` is 4.973 . | 4.973 | ratio | vif |  | eq | `[[art:dfd3d0c7:vif.note_rate]]` | verified | 4.973309839 |
| 296 | sensitivity | The value of `vif.orig_ltv` is 1.004 . | 1.004 | ratio | vif |  | eq | `[[art:ca78c9fc:vif.orig_ltv]]` | verified | 1.004492604 |
| 297 | sensitivity | The value of `vif.orig_upb_log` is 1.006 . | 1.006 | ratio | vif |  | eq | `[[art:127ff775:vif.orig_upb_log]]` | verified | 1.005824647 |
| 298 | sensitivity | The value of `vif.sato` is 1.708 . | 1.708 | ratio | vif |  | eq | `[[art:4802c713:vif.sato]]` | verified | 1.70802752 |
| 299 | sensitivity | The value of `vif.season_cos` is 1.018 . | 1.018 | ratio | vif |  | eq | `[[art:0046feb1:vif.season_cos]]` | verified | 1.017677402 |
| 300 | sensitivity | The value of `vif.season_sin` is 1.004 . | 1.004 | ratio | vif |  | eq | `[[art:c19a5e9a:vif.season_sin]]` | verified | 1.004122258 |
| 301 | findings | The value of `leakage.duplicates.train` is 0 . | 0 | ratio | leakage |  | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 302 | findings | The value of `leakage.overlap.features` is 0.02997 . | 0.02997 | ratio | leakage |  | eq | `[[art:bcbccff8:leakage.overlap.features]]` | verified | 0.02997009492 |
| 303 | findings | The value of `sign_check.note_rate.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:a453463d:sign_check.note_rate.agrees]]` | verified | 0 |
| 304 | findings | The value of `sign_check.note_rate.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:aecf7ccb:sign_check.note_rate.coef_sign]]` | verified | -1 |
| 305 | findings | The value of `sign_check.note_rate.univariate_direction` is… | 1 | ratio | sign_check |  | eq | `[[art:61f6e1ac:sign_check.note_rate.univariate_direction]]` | verified | 1 |
| 306 | findings | The value of `threshold.L2.overlap` is 0.005 . | 0.005 | ratio | threshold |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 307 | findings | The value of `threshold.L2.overlap.features_effective` is 0.… | 0.005 | ratio | threshold |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 308 | monitoring | The value of `calibration_slope.test` is 0.939 . | 0.939 | ratio | calibration_slope |  | eq | `[[art:80d029cc:calibration_slope.test]]` | verified | 0.9389856921 |
| 309 | monitoring | The value of `metrics.test.auc` is 0.7759 . | 0.7759 | ratio | metrics |  | eq | `[[art:225b99b5:metrics.test.auc]]` | verified | 0.7759451414 |
| 310 | monitoring | The value of `psi.max` is 0.06021 . | 0.06021 | ratio | psi |  | eq | `[[art:e09026cf:psi.max]]` | verified | 0.06021122495 |
| 311 | monitoring | The value of `rule.calibration_first_event_rate` is 0.05 . | 0.05 | ratio | rule |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 312 | monitoring | The value of `threshold.package.auc.test.min` is 0.65 . | 0.65 | ratio | threshold |  | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 313 | monitoring | The value of `threshold.package.calibration_slope.test.max`… | 1.2 | ratio | threshold |  | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 314 | monitoring | The value of `threshold.package.calibration_slope.test.min`… | 0.8 | ratio | threshold |  | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 315 | monitoring | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |

## Appendix B — Artifact index

The store holds 272 artifacts; the 212 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `ablation.baseline_auc` | `fdbd1084` | scalar | 0.7674403486 | AUC on test of a refit of the champion's functional form on every retained feature, the level each ablation delta is measured from |
| `ablation.burnout.delta_auc` | `177952dc` | scalar | -0.0003017983163 | change in test AUC when the champion's form is refitted without burnout |
| `ablation.credit_score.delta_auc` | `479f419e` | scalar | -0.01477490391 | change in test AUC when the champion's form is refitted without credit_score |
| `ablation.incentive.delta_auc` | `7213d612` | scalar | -0.04118780629 | change in test AUC when the champion's form is refitted without incentive |
| `ablation.loan_age.delta_auc` | `863965a3` | scalar | 0.0008139569301 | change in test AUC when the champion's form is refitted without loan_age |
| `ablation.note_rate.delta_auc` | `730edeaf` | scalar | -0.002577177916 | change in test AUC when the champion's form is refitted without note_rate |
| `ablation.orig_ltv.delta_auc` | `6b1c5d74` | scalar | -0.002214597102 | change in test AUC when the champion's form is refitted without orig_ltv |
| `ablation.orig_upb_log.delta_auc` | `5bc33417` | scalar | -0.01960949095 | change in test AUC when the champion's form is refitted without orig_upb_log |
| `ablation.sato.delta_auc` | `c477ddcb` | scalar | 0.0005940828502 | change in test AUC when the champion's form is refitted without sato |
| `ablation.season_cos.delta_auc` | `655cfcbe` | scalar | -0.0004809745496 | change in test AUC when the champion's form is refitted without season_cos |
| `ablation.season_sin.delta_auc` | `0b5a4b1b` | scalar | -0.0003927077916 | change in test AUC when the champion's form is refitted without season_sin |
| `calibration.mean_rel_gap.out_of_time` | `4084ccd4` | scalar | 0.08366462899 | mean predicted against observed on out_of_time, relative |
| `calibration.mean_rel_gap.test` | `40409705` | scalar | 0.03753966213 | mean predicted against observed on test, relative |
| `calibration.mean_rel_gap.train` | `0b47f454` | scalar | 0.009844346741 | mean predicted against observed on train, relative |
| `calibration.mean_rel_gap.vintage_holdout` | `4b6b5371` | scalar | 0.2276910236 | mean predicted against observed on vintage_holdout, relative |
| `calibration.test` | `9633f335` | table | table, 10 rows | calibration by decile of predicted probability on test |
| `calibration_intercept.out_of_time` | `e50f09e0` | scalar | -0.0583358688 | logistic regression of the outcome on logit(p) on out_of_time: the intercept |
| `calibration_intercept.test` | `f2adc1ec` | scalar | -0.2952175968 | logistic regression of the outcome on logit(p) on test: the intercept |
| `calibration_intercept.train` | `f381282b` | scalar | -0.02732327203 | logistic regression of the outcome on logit(p) on train: the intercept |
| `calibration_intercept.vintage_holdout` | `1256d464` | scalar | -0.9462036021 | logistic regression of the outcome on logit(p) on vintage_holdout: the intercept |
| `calibration_slope.out_of_time` | `860e5dd2` | scalar | 1.007762878 | logistic regression of the outcome on logit(p) on out_of_time: the slope |
| `calibration_slope.test` | `80d029cc` | scalar | 0.9389856921 | logistic regression of the outcome on logit(p) on test: the slope |
| `calibration_slope.train` | `a10d9430` | scalar | 0.9958299755 | logistic regression of the outcome on logit(p) on train: the slope |
| `calibration_slope.vintage_holdout` | `20da9c88` | scalar | 0.8363376022 | logistic regression of the outcome on logit(p) on vintage_holdout: the slope |
| `challenger.auc` | `abe111e2` | scalar | 0.7365834528 | the challenger's AUC on test |
| `challenger.brier` | `acd8735a` | scalar | 0.009228035552 | the challenger's Brier score on test |
| `challenger.delta_auc` | `46dde851` | scalar | -0.03936168863 | the challenger's AUC on test minus the champion's |
| `condition_number` | `cf4a0dab` | scalar | 4.941319585 | Belsley's condition number of the column-standardised design |
| `cpr.out_of_time.mae` | `6699b093` | scalar | 0.05670843092 | mean absolute difference between actual and predicted CPR on out_of_time |
| `cpr.test` | `28397851` | table | table, 71 rows | actual against predicted CPR by period on test |
| `cpr.test.mae` | `13564933` | scalar | 0.04285359689 | mean absolute difference between actual and predicted CPR on test |
| `cpr.train.mae` | `1baf9f3a` | scalar | 0.02615146691 | mean absolute difference between actual and predicted CPR on train |
| `cpr.vintage_holdout.mae` | `34f4c62c` | scalar | 0.03048231099 | mean absolute difference between actual and predicted CPR on vintage_holdout |
| `csi.burnout` | `2af1e79a` | scalar | 0.001162803488 | CSI of burnout: its contribution to the shift in the linear predictor |
| `csi.credit_score` | `17137aa1` | scalar | 0.008068926476 | CSI of credit_score: its contribution to the shift in the linear predictor |
| `csi.incentive` | `4fb0f08d` | scalar | 0.005098722582 | CSI of incentive: its contribution to the shift in the linear predictor |
| `csi.loan_age` | `df52c920` | scalar | 0 | CSI of loan_age: its contribution to the shift in the linear predictor |
| `csi.max` | `cf5a5274` | scalar | 0.0360163058 | the largest characteristic stability index |
| `csi.note_rate` | `d8ee67a8` | scalar | 0.01444840152 | CSI of note_rate: its contribution to the shift in the linear predictor |
| `csi.orig_ltv` | `5ce12077` | scalar | 0.0360163058 | CSI of orig_ltv: its contribution to the shift in the linear predictor |
| `csi.orig_upb_log` | `d6de1f4a` | scalar | 0.003374084917 | CSI of orig_upb_log: its contribution to the shift in the linear predictor |
| `csi.sato` | `5d9bf44b` | scalar | 0.0005107233981 | CSI of sato: its contribution to the shift in the linear predictor |
| `csi.season_cos` | `f8939193` | scalar | 0.0006696922627 | CSI of season_cos: its contribution to the shift in the linear predictor |
| `csi.season_sin` | `eef3a546` | scalar | 5.589052952e-05 | CSI of season_sin: its contribution to the shift in the linear predictor |
| `deciles.out_of_time.top2_capture` | `e28ccabb` | scalar | 0.5863636364 | share of out_of_time events in the top two deciles |
| `deciles.test` | `8e91a22f` | table | table, 10 rows | decile separation on test; decile 1 holds the highest probabilities |
| `deciles.test.top2_capture` | `43c4adc5` | scalar | 0.5806451613 | share of test events in the top two deciles |
| `deciles.train.top2_capture` | `adaecbab` | scalar | 0.5955414013 | share of train events in the top two deciles |
| `deciles.vintage_holdout.top2_capture` | `0d0c0310` | scalar | 0.5806451613 | share of vintage_holdout events in the top two deciles |
| `leakage.duplicates.train` | `4474c227` | scalar | 0 | share of train rows whose feature values are not unique within train |
| `leakage.name_screen.n_matched` | `407e62be` | scalar | 0 | feature names matching the target-adjacent lexicon |
| `leakage.overlap` | `4fb7c6b6` | scalar | 0.02997009492 | share of test rows whose feature values also appear in train |
| `leakage.overlap.features` | `bcbccff8` | scalar | 0.02997009492 | share of test rows whose feature values also appear in train |
| `leakage.overlap.ids` | `63d37fc5` | scalar | 0 | share of test rows whose ['loan_id', 'period'] also identify a row of train |
| `leakage.target_corr.max_single_feature_auc` | `6db1c162` | scalar | 0.7244788731 | the AUC of the strongest single feature |
| `leakage.timing.n_flagged` | `742bcd24` | scalar | 0 | features declared during_period or after_outcome |
| `metrics.out_of_time.auc` | `2e910103` | scalar | 0.7871132191 | auc on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.brier` | `9dbe134b` | scalar | 0.01712189167 | brier on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.event_rate` | `83ccf5c0` | scalar | 0.01794892714 | event_rate on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.gini` | `442c1e75` | scalar | 0.5742264382 | gini on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.ks` | `c8dd3c8a` | scalar | 0.4421873466 | ks on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.logloss` | `793f94ec` | scalar | 0.07960455821 | logloss on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.mean_predicted` | `3cc343ae` | scalar | 0.01945061747 | mean_predicted on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.n` | `7898809e` | scalar | 12257 | n on out_of_time, recomputed by quaestor |
| `metrics.test.auc` | `225b99b5` | scalar | 0.7759451414 | auc on test, recomputed by quaestor |
| `metrics.test.brier` | `66eaf26f` | scalar | 0.007892754939 | brier on test, recomputed by quaestor |
| `metrics.test.event_rate` | `570cc08a` | scalar | 0.008061370433 | event_rate on test, recomputed by quaestor |
| `metrics.test.gini` | `0aebb8a9` | scalar | 0.5518902828 | gini on test, recomputed by quaestor |
| `metrics.test.ks` | `3abd1f94` | scalar | 0.4194605474 | ks on test, recomputed by quaestor |
| `metrics.test.logloss` | `a801271e` | scalar | 0.04261094263 | logloss on test, recomputed by quaestor |
| `metrics.test.mean_predicted` | `542ddc6b` | scalar | 0.008363991555 | mean_predicted on test, recomputed by quaestor |
| `metrics.test.n` | `e55953e1` | scalar | 15382 | n on test, recomputed by quaestor |
| `metrics.train.auc` | `88da2e97` | scalar | 0.7887583845 | auc on train, recomputed by quaestor |
| `metrics.train.brier` | `a3ddd3d7` | scalar | 0.008396301302 | brier on train, recomputed by quaestor |
| `metrics.train.event_rate` | `73327d6c` | scalar | 0.008608872073 | event_rate on train, recomputed by quaestor |
| `metrics.train.gini` | `a786960b` | scalar | 0.5775167691 | gini on train, recomputed by quaestor |
| `metrics.train.ks` | `12bd02b0` | scalar | 0.4560599388 | ks on train, recomputed by quaestor |
| `metrics.train.logloss` | `fce5969c` | scalar | 0.04441572278 | logloss on train, recomputed by quaestor |
| `metrics.train.mean_predicted` | `3eee0092` | scalar | 0.008693620795 | mean_predicted on train, recomputed by quaestor |
| `metrics.train.n` | `82d2c58e` | scalar | 36474 | n on train, recomputed by quaestor |
| `metrics.vintage_holdout.auc` | `ff084e89` | scalar | 0.7721582541 | auc on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.brier` | `31ac126b` | scalar | 0.00476513883 | brier on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.event_rate` | `e3590a16` | scalar | 0.004817105386 | event_rate on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.gini` | `14144a5d` | scalar | 0.5443165082 | gini on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.ks` | `178bbe36` | scalar | 0.4492226111 | ks on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.logloss` | `e1b4f0f1` | scalar | 0.02814470369 | logloss on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.mean_predicted` | `08dbc56d` | scalar | 0.005913917042 | mean_predicted on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.n` | `37a92951` | scalar | 32177 | n on vintage_holdout, recomputed by quaestor |
| `profile.out_of_time.missing.max` | `4dafce11` | scalar | 0 | the largest missing fraction in out_of_time |
| `profile.out_of_time.n` | `fa39c5cf` | scalar | 12257 | rows in out_of_time |
| `profile.test.missing.max` | `f813848d` | scalar | 0 | the largest missing fraction in test |
| `profile.test.n` | `e3abc1b8` | scalar | 15382 | rows in test |
| `profile.train.missing.max` | `050a3099` | scalar | 0 | the largest missing fraction in train |
| `profile.train.n` | `7e94d818` | scalar | 36474 | rows in train |
| `profile.vintage_holdout.missing.max` | `329bb430` | scalar | 0 | the largest missing fraction in vintage_holdout |
| `profile.vintage_holdout.n` | `426e712a` | scalar | 32177 | rows in vintage_holdout |
| `psi.burnout` | `33f5ebc2` | scalar | 0.004931216889 | PSI of burnout between train and test |
| `psi.credit_score` | `d18c84c9` | scalar | 0.06021122495 | PSI of credit_score between train and test |
| `psi.incentive` | `68e58ed4` | scalar | 0.0008807210511 | PSI of incentive between train and test |
| `psi.loan_age` | `0de705ab` | scalar | 0.0001935522768 | PSI of loan_age between train and test |
| `psi.max` | `e09026cf` | scalar | 0.06021122495 | the largest train-to-test PSI, score included |
| `psi.note_rate` | `c7f1a67b` | scalar | 0.009203799735 | PSI of note_rate between train and test |
| `psi.orig_ltv` | `5a52f767` | scalar | 0.03524928958 | PSI of orig_ltv between train and test |
| `psi.orig_upb_log` | `a8060a5e` | scalar | 0.04275593453 | PSI of orig_upb_log between train and test |
| `psi.out_of_time.burnout` | `2f1775e6` | scalar | 2.940517648 | PSI of burnout between train and out_of_time |
| `psi.out_of_time.credit_score` | `736d4786` | scalar | 0.05906553221 | PSI of credit_score between train and out_of_time |
| `psi.out_of_time.incentive` | `8f1aad44` | scalar | 0.4959842347 | PSI of incentive between train and out_of_time |
| `psi.out_of_time.loan_age` | `a53fe5b7` | scalar | 2.482521703 | PSI of loan_age between train and out_of_time |
| `psi.out_of_time.note_rate` | `41ec908a` | scalar | 0.6979848935 | PSI of note_rate between train and out_of_time |
| `psi.out_of_time.orig_ltv` | `3e1cfd51` | scalar | 0.04223900725 | PSI of orig_ltv between train and out_of_time |
| `psi.out_of_time.orig_upb_log` | `bd610e8f` | scalar | 0.0679791761 | PSI of orig_upb_log between train and out_of_time |
| `psi.out_of_time.sato` | `8c2d71b1` | scalar | 0.01229057251 | PSI of sato between train and out_of_time |
| `psi.out_of_time.season_cos` | `9bb91b1d` | scalar | 0.01068186712 | PSI of season_cos between train and out_of_time |
| `psi.out_of_time.season_sin` | `1c848842` | scalar | 0.02790812853 | PSI of season_sin between train and out_of_time |
| `psi.out_of_time.y_score` | `926393e5` | scalar | 0.706727876 | PSI of the score between train and out_of_time |
| `psi.sato` | `d035c9fe` | scalar | 0.02937047655 | PSI of sato between train and test |
| `psi.season_cos` | `4c164ad6` | scalar | 2.852014247e-05 | PSI of season_cos between train and test |
| `psi.season_sin` | `34445e67` | scalar | 3.360751567e-06 | PSI of season_sin between train and test |
| `psi.vintage_holdout.burnout` | `d7eb40ee` | scalar | 0.04787342519 | PSI of burnout between train and vintage_holdout |
| `psi.vintage_holdout.credit_score` | `eb8b579f` | scalar | 0.03956501951 | PSI of credit_score between train and vintage_holdout |
| `psi.vintage_holdout.incentive` | `a5809fbc` | scalar | 0.4467844664 | PSI of incentive between train and vintage_holdout |
| `psi.vintage_holdout.loan_age` | `880920e4` | scalar | 0.07103580061 | PSI of loan_age between train and vintage_holdout |
| `psi.vintage_holdout.note_rate` | `8903dffa` | scalar | 0.6035871138 | PSI of note_rate between train and vintage_holdout |
| `psi.vintage_holdout.orig_ltv` | `e538a378` | scalar | 0.0287751179 | PSI of orig_ltv between train and vintage_holdout |
| `psi.vintage_holdout.orig_upb_log` | `983493d4` | scalar | 0.03584175044 | PSI of orig_upb_log between train and vintage_holdout |
| `psi.vintage_holdout.sato` | `9cde942f` | scalar | 0.03244197722 | PSI of sato between train and vintage_holdout |
| `psi.vintage_holdout.season_cos` | `0b2e1ed1` | scalar | 0.001415335964 | PSI of season_cos between train and vintage_holdout |
| `psi.vintage_holdout.season_sin` | `accfeb86` | scalar | 0.0007471395641 | PSI of season_sin between train and vintage_holdout |
| `psi.vintage_holdout.y_score` | `b7edb3fa` | scalar | 0.1381257303 | PSI of the score between train and vintage_holdout |
| `psi.y_score` | `b90e64c8` | scalar | 0.001802030258 | PSI of the score between train and test |
| `rule.calibration_first_event_rate` | `42f1351e` | scalar | 0.05 | the event rate below which the report puts calibration before discrimination |
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |
| `scenario.convexity` | `e6e5c89b` | scalar | -1154347.998 | the value change at -300 bp plus the change at 300 bp; negative when the fall outweighs the rise |
| `scenario.value_by_shock` | `51e09003` | table | table, 7 rows | servicing value, its change from the base case and first-year CPR, by shock |
| `scenario.value_change.-100` | `8d716ed3` | scalar | -295185.0824 | change in servicing value at -100 bp |
| `scenario.value_change.-200` | `fc515a18` | scalar | -821809.3771 | change in servicing value at -200 bp |
| `scenario.value_change.-300` | `1bb5faa9` | scalar | -1299764.383 | change in servicing value at -300 bp |
| `scenario.value_change.0` | `1e1b0b88` | scalar | 0 | change in servicing value at 0 bp |
| `scenario.value_change.100` | `32d76ec2` | scalar | 103821.8979 | change in servicing value at 100 bp |
| `scenario.value_change.200` | `9ff1104d` | scalar | 135913.6115 | change in servicing value at 200 bp |
| `scenario.value_change.300` | `a5bb5830` | scalar | 145416.3854 | change in servicing value at 300 bp |
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
| `stability.auc_by_regime` | `411b1cfe` | table | table, 2 rows | the champion's AUC within each rate_regime on train |
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
| `thresholds.evaluation` | `6eb162e0` | table | table, 4 rows | every threshold package.yaml declares, with its bound, the recomputed value and the outcome |
| `vif.burnout` | `15d2d2b7` | scalar | 3.441796277 | variance inflation factor of burnout on train |
| `vif.credit_score` | `8908e744` | scalar | 1.007807025 | variance inflation factor of credit_score on train |
| `vif.incentive` | `13d92899` | scalar | 2.225948498 | variance inflation factor of incentive on train |
| `vif.loan_age` | `da5f6107` | scalar | 2.928894489 | variance inflation factor of loan_age on train |
| `vif.max` | `d9b015aa` | scalar | 4.973309839 | the largest variance inflation factor |
| `vif.note_rate` | `dfd3d0c7` | scalar | 4.973309839 | variance inflation factor of note_rate on train |
| `vif.orig_ltv` | `ca78c9fc` | scalar | 1.004492604 | variance inflation factor of orig_ltv on train |
| `vif.orig_upb_log` | `127ff775` | scalar | 1.005824647 | variance inflation factor of orig_upb_log on train |
| `vif.sato` | `4802c713` | scalar | 1.70802752 | variance inflation factor of sato on train |
| `vif.season_cos` | `0046feb1` | scalar | 1.017677402 | variance inflation factor of season_cos on train |
| `vif.season_sin` | `c19a5e9a` | scalar | 1.004122258 | variance inflation factor of season_sin on train |

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
| wall-clock (s) | 1.84 |
| subject run (s) | 2.44 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | fake |
| model | none: no model answered |
| run id | msr_prepayment-rules_only-20260918T065347Z-568d25f5 |

## Appendix D — Not checked

| item | reason |
|---|---|
| developer claims (T1, claim channel) | The package declares 3 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
| drafted narrative and the repair loop | `rules_only` calls no model; the narrative is a template |
