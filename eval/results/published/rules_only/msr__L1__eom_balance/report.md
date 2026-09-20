---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: msr_prepayment
version: "1.0"
model_type: discrete_time_hazard
configuration: rules_only
model: fake
run_id: msr_prepayment-rules_only-20260918T065342Z-568d25f5
data_mode: synthetic
synthetic_n: 2000
grounding_precision_pre: 1.0000
grounding_precision_post: 1.0000
n_claims: 318
n_findings_by_severity: {high: 2, medium: 0, low: 0, info: 0}
generated: "2026-09-18T06:53:42Z"
illustrative: false
---

# Validation report — `msr_prepayment` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `msr_prepayment` v1.0 | `rules_only` | fake | synthetic, n = 2000 | 1.0000 → 1.0000 | 2 / 0 / 0 / 0 |
<!-- quaestor:renderer:end -->

This section follows the model risk management guidance at [[reg:SR26-2:V.1.b]].
The value of `challenger.delta_auc` is 0 [[art:d8eca8f5:challenger.delta_auc]].
The value of `condition_number` is 4.954 [[art:d0edbe6f:condition_number]].
The value of `csi.max` is 0.03215 [[art:b2440ca1:csi.max]].
The value of `metrics.out_of_time.auc` is 1 [[art:bcb747a3:metrics.out_of_time.auc]].
The value of `metrics.out_of_time.brier` is 0.00000001376 [[art:44f11124:metrics.out_of_time.brier]].
The value of `metrics.out_of_time.event_rate` is 0.01795 [[art:83ccf5c0:metrics.out_of_time.event_rate]].
The value of `metrics.out_of_time.gini` is 1 [[art:6d939d01:metrics.out_of_time.gini]].
The value of `metrics.out_of_time.ks` is 1 [[art:e3aa3687:metrics.out_of_time.ks]].
The value of `metrics.out_of_time.logloss` is 0.00009057 [[art:4ff30655:metrics.out_of_time.logloss]].
The value of `metrics.out_of_time.mean_predicted` is 0.01802 [[art:276f106a:metrics.out_of_time.mean_predicted]].
The value of `metrics.out_of_time.n` is 12257 [[art:7898809e:metrics.out_of_time.n]].
The value of `metrics.test.auc` is 1 [[art:4619bd69:metrics.test.auc]].
The value of `metrics.test.brier` is 0.00000001011 [[art:67fd4fea:metrics.test.brier]].
The value of `metrics.test.event_rate` is 0.008061 [[art:570cc08a:metrics.test.event_rate]].
The value of `metrics.test.gini` is 1 [[art:35acd744:metrics.test.gini]].
The value of `metrics.test.ks` is 1 [[art:a13846c8:metrics.test.ks]].
The value of `metrics.test.logloss` is 0.00009043 [[art:db4e6b76:metrics.test.logloss]].
The value of `metrics.test.mean_predicted` is 0.008144 [[art:83863be2:metrics.test.mean_predicted]].
The value of `metrics.test.n` is 15382 [[art:e55953e1:metrics.test.n]].
The value of `metrics.train.auc` is 1 [[art:6269694d:metrics.train.auc]].
The value of `metrics.train.brier` is 0.00000001096 [[art:0c2c4489:metrics.train.brier]].
The value of `metrics.train.event_rate` is 0.008525 [[art:b9ef3327:metrics.train.event_rate]].
The value of `metrics.train.gini` is 1 [[art:e2084e07:metrics.train.gini]].
The value of `metrics.train.ks` is 1 [[art:24c2277d:metrics.train.ks]].
The value of `metrics.train.logloss` is 0.00009128 [[art:1761d10c:metrics.train.logloss]].
The value of `metrics.train.mean_predicted` is 0.008607 [[art:6f9330ed:metrics.train.mean_predicted]].
The value of `metrics.train.n` is 36013 [[art:6fdfeabb:metrics.train.n]].
The value of `metrics.vintage_holdout.auc` is 1 [[art:00749c11:metrics.vintage_holdout.auc]].
The value of `metrics.vintage_holdout.brier` is 0.000000008646 [[art:c58e369c:metrics.vintage_holdout.brier]].
The value of `metrics.vintage_holdout.event_rate` is 0.004817 [[art:e3590a16:metrics.vintage_holdout.event_rate]].
The value of `metrics.vintage_holdout.gini` is 1 [[art:f4aa377a:metrics.vintage_holdout.gini]].
The value of `metrics.vintage_holdout.ks` is 1 [[art:cb4509f6:metrics.vintage_holdout.ks]].
The value of `metrics.vintage_holdout.logloss` is 0.00008629 [[art:85bdc089:metrics.vintage_holdout.logloss]].
The value of `metrics.vintage_holdout.mean_predicted` is 0.004899 [[art:af925790:metrics.vintage_holdout.mean_predicted]].
The value of `metrics.vintage_holdout.n` is 32177 [[art:37a92951:metrics.vintage_holdout.n]].
The value of `profile.test.n` is 15382 [[art:e3abc1b8:profile.test.n]].
The value of `profile.train.n` is 36013 [[art:c5ebd9c9:profile.train.n]].
The value of `psi.max` is 0.06189 [[art:c2e8c8fd:psi.max]].
The value of `runtime.max_seconds` is 300 [[art:2ad8d1a5:runtime.max_seconds]].
The value of `threshold.package.auc.test.min` is 0.65 [[art:fececac1:threshold.package.auc.test.min]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
The value of `vif.max` is 4.978 [[art:b1d416c0:vif.max]].

## 2. Conceptual soundness

This section follows the model risk management guidance at [[reg:SR26-2:V.1.a]].
The value of `ablation.baseline_auc` is 1 [[art:7610ff35:ablation.baseline_auc]].
The value of `ablation.bom_balance_log.delta_auc` is -0.2327 [[art:c226f60f:ablation.bom_balance_log.delta_auc]].
The value of `ablation.burnout.delta_auc` is 0 [[art:d50de877:ablation.burnout.delta_auc]].
The value of `ablation.credit_score.delta_auc` is 0 [[art:d1dff006:ablation.credit_score.delta_auc]].
The value of `ablation.incentive.delta_auc` is 0 [[art:33a25e3c:ablation.incentive.delta_auc]].
The value of `ablation.loan_age.delta_auc` is 0 [[art:1a789b08:ablation.loan_age.delta_auc]].
The value of `ablation.note_rate.delta_auc` is 0 [[art:65b3f07a:ablation.note_rate.delta_auc]].
The value of `ablation.orig_ltv.delta_auc` is 0 [[art:370eaea8:ablation.orig_ltv.delta_auc]].
The value of `ablation.orig_upb_log.delta_auc` is 0 [[art:e245ef14:ablation.orig_upb_log.delta_auc]].
The value of `ablation.sato.delta_auc` is 0 [[art:2bbb0015:ablation.sato.delta_auc]].
The value of `ablation.season_cos.delta_auc` is 0 [[art:9453331c:ablation.season_cos.delta_auc]].
The value of `ablation.season_sin.delta_auc` is 0 [[art:a4f7b0c1:ablation.season_sin.delta_auc]].
The value of `challenger.auc` is 1 [[art:5aeaf534:challenger.auc]].
The value of `challenger.brier` is 0.0000000000003226 [[art:0b5236ca:challenger.brier]].
The value of `challenger.delta_auc` is 0 [[art:d8eca8f5:challenger.delta_auc]].
The value of `metrics.test.auc` is 1 [[art:4619bd69:metrics.test.auc]].
The value of `metrics.test.brier` is 0.00000001011 [[art:67fd4fea:metrics.test.brier]].
The value of `sign_check.bom_balance_log.agrees` is 1 [[art:26b1789b:sign_check.bom_balance_log.agrees]].
The value of `sign_check.bom_balance_log.coef_sign` is -1 [[art:d2e88db3:sign_check.bom_balance_log.coef_sign]].
The value of `sign_check.bom_balance_log.univariate_direction` is -1 [[art:8ee4f8fe:sign_check.bom_balance_log.univariate_direction]].
The value of `sign_check.burnout.agrees` is 0 [[art:56826e40:sign_check.burnout.agrees]].
The value of `sign_check.burnout.coef_sign` is -1 [[art:dcfb2de4:sign_check.burnout.coef_sign]].
The value of `sign_check.burnout.univariate_direction` is 1 [[art:bfc96bb2:sign_check.burnout.univariate_direction]].
The value of `sign_check.credit_score.agrees` is 1 [[art:915bf8eb:sign_check.credit_score.agrees]].
The value of `sign_check.credit_score.coef_sign` is 1 [[art:1ec1078b:sign_check.credit_score.coef_sign]].
The value of `sign_check.credit_score.univariate_direction` is 1 [[art:42303896:sign_check.credit_score.univariate_direction]].
The value of `sign_check.incentive.agrees` is 1 [[art:f7b2338e:sign_check.incentive.agrees]].
The value of `sign_check.incentive.coef_sign` is 1 [[art:684cf11a:sign_check.incentive.coef_sign]].
The value of `sign_check.incentive.univariate_direction` is 1 [[art:8098d951:sign_check.incentive.univariate_direction]].
The value of `sign_check.n_disagreements` is 2 [[art:66ce738a:sign_check.n_disagreements]].
The value of `sign_check.note_rate.agrees` is 1 [[art:ca18290e:sign_check.note_rate.agrees]].
The value of `sign_check.note_rate.coef_sign` is 1 [[art:0e3296a5:sign_check.note_rate.coef_sign]].
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
The value of `sign_check.season_sin.agrees` is 0 [[art:74f2d0e0:sign_check.season_sin.agrees]].
The value of `sign_check.season_sin.coef_sign` is -1 [[art:92ed5b5f:sign_check.season_sin.coef_sign]].
The value of `sign_check.season_sin.univariate_direction` is 1 [[art:cae6b096:sign_check.season_sin.univariate_direction]].
The value of `threshold.E1.delta_auc` is 0.03 [[art:e042774c:threshold.E1.delta_auc]].

## 3. Data integrity and drift

This section follows the model risk management guidance at [[reg:SR26-2:V.1.a]].
The value of `csi.bom_balance_log` is 0.03215 [[art:60a10892:csi.bom_balance_log]].
The value of `csi.burnout` is 0.0001016 [[art:a5da1daa:csi.burnout]].
The value of `csi.credit_score` is 0.000223 [[art:d87a2d40:csi.credit_score]].
The value of `csi.incentive` is 0.00009278 [[art:41325258:csi.incentive]].
The value of `csi.loan_age` is 0 [[art:df52c920:csi.loan_age]].
The value of `csi.max` is 0.03215 [[art:b2440ca1:csi.max]].
The value of `csi.note_rate` is 0.0003806 [[art:587b33e9:csi.note_rate]].
The value of `csi.orig_ltv` is 0.0008996 [[art:7ea837e1:csi.orig_ltv]].
The value of `csi.orig_upb_log` is 0.004636 [[art:5d1c16f2:csi.orig_upb_log]].
The value of `csi.sato` is 0.000449 [[art:fb71eb9e:csi.sato]].
The value of `csi.season_cos` is 0.00001935 [[art:de66f2c6:csi.season_cos]].
The value of `csi.season_sin` is 0.000001386 [[art:4c3f0dd9:csi.season_sin]].
The value of `leakage.duplicates.train` is 0 [[art:4474c227:leakage.duplicates.train]].
The value of `leakage.name_screen.n_matched` is 0 [[art:407e62be:leakage.name_screen.n_matched]].
The value of `leakage.overlap` is 0 [[art:4c9fcd09:leakage.overlap]].
The value of `leakage.overlap.features` is 0 [[art:0fec8048:leakage.overlap.features]].
The value of `leakage.overlap.ids` is 0 [[art:63d37fc5:leakage.overlap.ids]].
The value of `leakage.target_corr.max_single_feature_auc` is 1 [[art:7f74c0d5:leakage.target_corr.max_single_feature_auc]].
The value of `leakage.timing.n_flagged` is 0 [[art:742bcd24:leakage.timing.n_flagged]].
The value of `profile.out_of_time.missing.max` is 0 [[art:4dafce11:profile.out_of_time.missing.max]].
The value of `profile.out_of_time.n` is 12257 [[art:fa39c5cf:profile.out_of_time.n]].
The value of `profile.test.missing.max` is 0 [[art:f813848d:profile.test.missing.max]].
The value of `profile.test.n` is 15382 [[art:e3abc1b8:profile.test.n]].
The value of `profile.train.missing.max` is 0 [[art:050a3099:profile.train.missing.max]].
The value of `profile.train.n` is 36013 [[art:c5ebd9c9:profile.train.n]].
The value of `profile.vintage_holdout.missing.max` is 0 [[art:329bb430:profile.vintage_holdout.missing.max]].
The value of `profile.vintage_holdout.n` is 32177 [[art:426e712a:profile.vintage_holdout.n]].
The value of `psi.bom_balance_log` is 0.03018 [[art:ce3c425c:psi.bom_balance_log]].
The value of `psi.burnout` is 0.004614 [[art:9dc7ecc2:psi.burnout]].
The value of `psi.credit_score` is 0.06189 [[art:7e87527c:psi.credit_score]].
The value of `psi.incentive` is 0.0009923 [[art:2da5570f:psi.incentive]].
The value of `psi.loan_age` is 0.0001994 [[art:2202b157:psi.loan_age]].
The value of `psi.max` is 0.06189 [[art:c2e8c8fd:psi.max]].
The value of `psi.note_rate` is 0.01371 [[art:ecc6adf3:psi.note_rate]].
The value of `psi.orig_ltv` is 0.03617 [[art:cd1ff136:psi.orig_ltv]].
The value of `psi.orig_upb_log` is 0.04817 [[art:55030a3b:psi.orig_upb_log]].
The value of `psi.out_of_time.bom_balance_log` is 0.08708 [[art:9fa682d1:psi.out_of_time.bom_balance_log]].
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
The value of `psi.out_of_time.y_score` is 0.1451 [[art:12620838:psi.out_of_time.y_score]].
The value of `psi.sato` is 0.02773 [[art:584da64f:psi.sato]].
The value of `psi.season_cos` is 0.0000179 [[art:addec503:psi.season_cos]].
The value of `psi.season_sin` is 0.000002939 [[art:4d2ed98d:psi.season_sin]].
The value of `psi.vintage_holdout.bom_balance_log` is 0.03707 [[art:b3073b46:psi.vintage_holdout.bom_balance_log]].
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
The value of `psi.vintage_holdout.y_score` is 0.05813 [[art:33ffbed6:psi.vintage_holdout.y_score]].
The value of `psi.y_score` is 0.01874 [[art:2ad82680:psi.y_score]].
The value of `threshold.D1.missing_gap` is 0.1 [[art:9cce25ea:threshold.D1.missing_gap]].
The value of `threshold.L1.single_feature_auc` is 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]].
The value of `threshold.L2.overlap` is 0.005 [[art:9f336eaf:threshold.L2.overlap]].
The value of `threshold.L2.overlap.features_effective` is 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].
The value of `threshold.S1.psi` is 0.25 [[art:278b9016:threshold.S1.psi]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
Candidates raised on this section's material: L1 (see the findings section).

## 4. Outcomes analysis

This section follows the model risk management guidance at [[reg:SR26-2:V.1.b]].
The value of `calibration.mean_rel_gap.out_of_time` is 0.003913 [[art:68619260:calibration.mean_rel_gap.out_of_time]].
The value of `calibration.mean_rel_gap.test` is 0.01026 [[art:4e1854b1:calibration.mean_rel_gap.test]].
The value of `calibration.mean_rel_gap.train` is 0.009654 [[art:db1bca38:calibration.mean_rel_gap.train]].
The value of `calibration.mean_rel_gap.vintage_holdout` is 0.01696 [[art:1438e44d:calibration.mean_rel_gap.vintage_holdout]].
The value of `calibration.separable.out_of_time` is 1 [[art:258b7972:calibration.separable.out_of_time]].
The value of `calibration.separable.test` is 1 [[art:81c3fa7a:calibration.separable.test]].
The value of `calibration.separable.train` is 1 [[art:d7ee2241:calibration.separable.train]].
The value of `calibration.separable.vintage_holdout` is 1 [[art:137e2c39:calibration.separable.vintage_holdout]].
The value of `cpr.out_of_time.mae` is 0.0007118 [[art:bdc9d54f:cpr.out_of_time.mae]].
The value of `cpr.test.mae` is 0.0009292 [[art:be219b85:cpr.test.mae]].
The value of `cpr.train.mae` is 0.000928 [[art:99b2b87f:cpr.train.mae]].
The value of `cpr.vintage_holdout.mae` is 0.0009299 [[art:d1a19e91:cpr.vintage_holdout.mae]].
The value of `deciles.out_of_time.top2_capture` is 1 [[art:d3114d7a:deciles.out_of_time.top2_capture]].
The value of `deciles.test.top2_capture` is 1 [[art:466bfdc8:deciles.test.top2_capture]].
The value of `deciles.train.top2_capture` is 1 [[art:194d1fbd:deciles.train.top2_capture]].
The value of `deciles.vintage_holdout.top2_capture` is 1 [[art:db275674:deciles.vintage_holdout.top2_capture]].
The value of `metrics.out_of_time.auc` is 1 [[art:bcb747a3:metrics.out_of_time.auc]].
The value of `metrics.out_of_time.brier` is 0.00000001376 [[art:44f11124:metrics.out_of_time.brier]].
The value of `metrics.out_of_time.event_rate` is 0.01795 [[art:83ccf5c0:metrics.out_of_time.event_rate]].
The value of `metrics.out_of_time.gini` is 1 [[art:6d939d01:metrics.out_of_time.gini]].
The value of `metrics.out_of_time.ks` is 1 [[art:e3aa3687:metrics.out_of_time.ks]].
The value of `metrics.out_of_time.logloss` is 0.00009057 [[art:4ff30655:metrics.out_of_time.logloss]].
The value of `metrics.out_of_time.mean_predicted` is 0.01802 [[art:276f106a:metrics.out_of_time.mean_predicted]].
The value of `metrics.out_of_time.n` is 12257 [[art:7898809e:metrics.out_of_time.n]].
The value of `metrics.test.auc` is 1 [[art:4619bd69:metrics.test.auc]].
The value of `metrics.test.brier` is 0.00000001011 [[art:67fd4fea:metrics.test.brier]].
The value of `metrics.test.event_rate` is 0.008061 [[art:570cc08a:metrics.test.event_rate]].
The value of `metrics.test.gini` is 1 [[art:35acd744:metrics.test.gini]].
The value of `metrics.test.ks` is 1 [[art:a13846c8:metrics.test.ks]].
The value of `metrics.test.logloss` is 0.00009043 [[art:db4e6b76:metrics.test.logloss]].
The value of `metrics.test.mean_predicted` is 0.008144 [[art:83863be2:metrics.test.mean_predicted]].
The value of `metrics.test.n` is 15382 [[art:e55953e1:metrics.test.n]].
The value of `metrics.train.auc` is 1 [[art:6269694d:metrics.train.auc]].
The value of `metrics.train.brier` is 0.00000001096 [[art:0c2c4489:metrics.train.brier]].
The value of `metrics.train.event_rate` is 0.008525 [[art:b9ef3327:metrics.train.event_rate]].
The value of `metrics.train.gini` is 1 [[art:e2084e07:metrics.train.gini]].
The value of `metrics.train.ks` is 1 [[art:24c2277d:metrics.train.ks]].
The value of `metrics.train.logloss` is 0.00009128 [[art:1761d10c:metrics.train.logloss]].
The value of `metrics.train.mean_predicted` is 0.008607 [[art:6f9330ed:metrics.train.mean_predicted]].
The value of `metrics.train.n` is 36013 [[art:6fdfeabb:metrics.train.n]].
The value of `metrics.vintage_holdout.auc` is 1 [[art:00749c11:metrics.vintage_holdout.auc]].
The value of `metrics.vintage_holdout.brier` is 0.000000008646 [[art:c58e369c:metrics.vintage_holdout.brier]].
The value of `metrics.vintage_holdout.event_rate` is 0.004817 [[art:e3590a16:metrics.vintage_holdout.event_rate]].
The value of `metrics.vintage_holdout.gini` is 1 [[art:f4aa377a:metrics.vintage_holdout.gini]].
The value of `metrics.vintage_holdout.ks` is 1 [[art:cb4509f6:metrics.vintage_holdout.ks]].
The value of `metrics.vintage_holdout.logloss` is 0.00008629 [[art:85bdc089:metrics.vintage_holdout.logloss]].
The value of `metrics.vintage_holdout.mean_predicted` is 0.004899 [[art:af925790:metrics.vintage_holdout.mean_predicted]].
The value of `metrics.vintage_holdout.n` is 32177 [[art:37a92951:metrics.vintage_holdout.n]].
The value of `psi.bom_balance_log` is 0.03018 [[art:ce3c425c:psi.bom_balance_log]].
The value of `psi.burnout` is 0.004614 [[art:9dc7ecc2:psi.burnout]].
The value of `psi.credit_score` is 0.06189 [[art:7e87527c:psi.credit_score]].
The value of `psi.incentive` is 0.0009923 [[art:2da5570f:psi.incentive]].
The value of `psi.loan_age` is 0.0001994 [[art:2202b157:psi.loan_age]].
The value of `psi.max` is 0.06189 [[art:c2e8c8fd:psi.max]].
The value of `psi.note_rate` is 0.01371 [[art:ecc6adf3:psi.note_rate]].
The value of `psi.orig_ltv` is 0.03617 [[art:cd1ff136:psi.orig_ltv]].
The value of `psi.orig_upb_log` is 0.04817 [[art:55030a3b:psi.orig_upb_log]].
The value of `psi.out_of_time.bom_balance_log` is 0.08708 [[art:9fa682d1:psi.out_of_time.bom_balance_log]].
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
The value of `psi.out_of_time.y_score` is 0.1451 [[art:12620838:psi.out_of_time.y_score]].
The value of `psi.sato` is 0.02773 [[art:584da64f:psi.sato]].
The value of `psi.season_cos` is 0.0000179 [[art:addec503:psi.season_cos]].
The value of `psi.season_sin` is 0.000002939 [[art:4d2ed98d:psi.season_sin]].
The value of `psi.vintage_holdout.bom_balance_log` is 0.03707 [[art:b3073b46:psi.vintage_holdout.bom_balance_log]].
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
The value of `psi.vintage_holdout.y_score` is 0.05813 [[art:33ffbed6:psi.vintage_holdout.y_score]].
The value of `psi.y_score` is 0.01874 [[art:2ad82680:psi.y_score]].
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
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
<!-- quaestor:renderer:begin table calibration.test -->
Calibration by decile of predicted probability on test [[art:a3f4f35f:calibration.test]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 6.427e-05 | 0 | 1539 |
| 2 | 7.269e-05 | 0 | 1539 |
| 3 | 7.745e-05 | 0 | 1538 |
| 4 | 8.161e-05 | 0 | 1538 |
| 5 | 8.541e-05 | 0 | 1538 |
| 6 | 8.919e-05 | 0 | 1538 |
| 7 | 9.302e-05 | 0 | 1538 |
| 8 | 9.697e-05 | 0 | 1538 |
| 9 | 0.0001019 | 0 | 1538 |
| 10 | 0.08069 | 0.08062 | 1538 |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table cpr.test -->
Actual against predicted CPR by period on test [[art:0aa376c9:cpr.test]]:

| period | n | actual_cpr | predicted_cpr |
|---|---|---|---|
| 201402 | 15 | 0 | 0.001003 |
| 201403 | 28 | 0 | 0.001005 |
| 201404 | 56 | 0 | 0.001001 |
| 201405 | 68 | 0 | 0.001008 |
| 201406 | 80 | 0 | 0.001017 |
| 201407 | 97 | 0.1169 | 0.1178 |
| 201408 | 111 | 0 | 0.001024 |
| 201409 | 133 | 0.08659 | 0.08747 |
| 201410 | 145 | 0 | 0.001017 |
| 201411 | 161 | 0 | 0.00102 |
| 201412 | 175 | 0 | 0.001019 |
| 201501 | 198 | 0 | 0.001022 |
| 201502 | 198 | 0 | 0.001023 |
| 201503 | 198 | 0.05895 | 0.05989 |
| 201504 | 197 | 0 | 0.001036 |
| 201505 | 197 | 0 | 0.001046 |
| 201506 | 197 | 0 | 0.001053 |
| 201507 | 197 | 0 | 0.00106 |
| 201508 | 197 | 0 | 0.001067 |
| 201509 | 197 | 0.05924 | 0.06022 |
| 201510 | 196 | 0.05954 | 0.06053 |
| 201511 | 195 | 0 | 0.001074 |
| 201512 | 195 | 0 | 0.001073 |
| 201601 | 195 | 0.1698 | 0.1706 |
| 201602 | 192 | 0.06074 | 0.06175 |
| 201603 | 191 | 0.1187 | 0.1196 |
| 201604 | 189 | 0.1198 | 0.1208 |
| 201605 | 187 | 0.3673 | 0.3679 |
| 201606 | 180 | 0.1255 | 0.1264 |
| 201607 | 178 | 0.1268 | 0.1277 |
| 201608 | 176 | 0.06609 | 0.06712 |
| 201609 | 175 | 0.1288 | 0.1298 |
| 201610 | 173 | 0.1893 | 0.1902 |
| 201611 | 170 | 0.06835 | 0.06932 |
| 201612 | 169 | 0.06874 | 0.0697 |
| 201701 | 168 | 0.1339 | 0.1347 |
| 201702 | 176 | 0.2924 | 0.293 |
| 201703 | 191 | 0.06105 | 0.062 |
| 201704 | 199 | 0 | 0.001051 |
| 201705 | 218 | 0.05368 | 0.05465 |
| 201706 | 238 | 0.04927 | 0.05024 |
| 201707 | 248 | 0 | 0.001041 |
| 201708 | 274 | 0 | 0.001035 |
| 201709 | 284 | 0.08131 | 0.08222 |
| 201710 | 300 | 0 | 0.001024 |
| 201711 | 323 | 0.03653 | 0.03749 |
| 201712 | 334 | 0.03534 | 0.03629 |
| 201801 | 354 | 0.03338 | 0.03435 |
| 201802 | 353 | 0.06591 | 0.06684 |
| 201803 | 351 | 0.03366 | 0.03464 |
| 201804 | 350 | 0.06646 | 0.06741 |
| 201805 | 348 | 0.1594 | 0.1602 |
| 201806 | 343 | 0.1616 | 0.1624 |
| 201807 | 338 | 0.1638 | 0.1646 |
| 201808 | 333 | 0.06974 | 0.07068 |
| 201809 | 331 | 0.2544 | 0.2551 |
| 201810 | 323 | 0.1707 | 0.1715 |
| 201811 | 318 | 0.07292 | 0.07384 |
| 201812 | 316 | 0.1742 | 0.1749 |
| 201901 | 311 | 0.1098 | 0.1106 |
| 201902 | 300 | 0.1488 | 0.1496 |
| 201903 | 285 | 0.2253 | 0.2261 |
| 201904 | 258 | 0.246 | 0.2467 |
| 201905 | 243 | 0.1385 | 0.1393 |
| 201906 | 233 | 0.2688 | 0.2694 |
| 201907 | 219 | 0.1984 | 0.1992 |
| 201908 | 206 | 0 | 0.001056 |
| 201909 | 191 | 0.06105 | 0.06202 |
| 201910 | 182 | 0.06398 | 0.06495 |
| 201911 | 171 | 0.06796 | 0.06895 |
| 201912 | 166 | 0 | 0.001076 |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table deciles.test -->
Decile separation on test; decile 1 holds the highest probabilities [[art:a859c712:deciles.test]]:

| decile | count | events | event_rate | lift |
|---|---|---|---|---|
| 1 | 1539 | 124 | 0.08057 | 9.995 |
| 2 | 1539 | 0 | 0 | 0 |
| 3 | 1538 | 0 | 0 | 0 |
| 4 | 1538 | 0 | 0 | 0 |
| 5 | 1538 | 0 | 0 | 0 |
| 6 | 1538 | 0 | 0 | 0 |
| 7 | 1538 | 0 | 0 | 0 |
| 8 | 1538 | 0 | 0 | 0 |
| 9 | 1538 | 0 | 0 | 0 |
| 10 | 1538 | 0 | 0 | 0 |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table thresholds.evaluation -->
Every threshold package.yaml declares, with its bound, the recomputed value and the outcome [[art:25af6e79:thresholds.evaluation]]:

| metric | split | bound | value | result |
|---|---|---|---|---|
| auc | test | minimum 0.65 | 1 | pass |
| calibration_slope | test | minimum 0.8 | not evaluated: calibration_slope.test is not in the store | not evaluated |
| calibration_slope | test | maximum 1.2 | not evaluated: calibration_slope.test is not in the store | not evaluated |
| psi |  | maximum 0.25 | 0.06189 | pass |
<!-- quaestor:renderer:end -->

## 5. Sensitivity and scenario analysis

This section follows the model risk management guidance at [[reg:SR26-2:V.1.a]].
The value of `condition_number` is 4.954 [[art:d0edbe6f:condition_number]].
The value of `scenario.convexity` is 140.7 [[art:4451c907:scenario.convexity]].
The value of `scenario.value_change.-100` is -57.15 [[art:0445ffec:scenario.value_change.-100]].
The value of `scenario.value_change.-200` is -83.78 [[art:75d82514:scenario.value_change.-200]].
The value of `scenario.value_change.-300` is -92.11 [[art:0f83fead:scenario.value_change.-300]].
The value of `scenario.value_change.0` is 0 [[art:1e1b0b88:scenario.value_change.0]].
The value of `scenario.value_change.100` is 77.18 [[art:d16cc2a1:scenario.value_change.100]].
The value of `scenario.value_change.200` is 155.8 [[art:4871ddee:scenario.value_change.200]].
The value of `scenario.value_change.300` is 232.8 [[art:a0678af4:scenario.value_change.300]].
The value of `stability.bom_balance_log.sign_flip` is 0 [[art:a9b4364d:stability.bom_balance_log.sign_flip]].
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
The value of `vif.bom_balance_log` is 1.143 [[art:0b30efbf:vif.bom_balance_log]].
The value of `vif.burnout` is 3.44 [[art:91e7ce55:vif.burnout]].
The value of `vif.credit_score` is 1.009 [[art:b8652149:vif.credit_score]].
The value of `vif.incentive` is 2.234 [[art:d924a341:vif.incentive]].
The value of `vif.loan_age` is 2.93 [[art:43980218:vif.loan_age]].
The value of `vif.max` is 4.978 [[art:b1d416c0:vif.max]].
The value of `vif.note_rate` is 4.978 [[art:71e8f3f6:vif.note_rate]].
The value of `vif.orig_ltv` is 1.005 [[art:10f2f018:vif.orig_ltv]].
The value of `vif.orig_upb_log` is 1.134 [[art:347761f6:vif.orig_upb_log]].
The value of `vif.sato` is 1.713 [[art:08e0ca20:vif.sato]].
The value of `vif.season_cos` is 1.018 [[art:a2dc57c7:vif.season_cos]].
The value of `vif.season_sin` is 1.004 [[art:5069e43c:vif.season_sin]].
<!-- quaestor:renderer:begin table scenario.value_by_shock -->
Servicing value, its change from the base case and first-year CPR, by shock [[art:c4d5cb25:scenario.value_by_shock]]:

| shock_bp | value | value_change | cpr |
|---|---|---|---|
| -300 | 1.762e+06 | -92.11 | 0.0007734 |
| -200 | 1.762e+06 | -83.78 | 0.0007603 |
| -100 | 1.762e+06 | -57.15 | 0.0007469 |
| 0 | 1.762e+06 | 0 | 0.0007328 |
| 100 | 1.762e+06 | 77.18 | 0.0007184 |
| 200 | 1.762e+06 | 155.8 | 0.0007041 |
| 300 | 1.762e+06 | 232.8 | 0.0006902 |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table stability.auc_by_regime -->
The champion's AUC within each rate_regime on train [[art:9edbf2d0:stability.auc_by_regime]]:

| regime | n | event_rate | auc |
|---|---|---|---|
| falling | 17873 | 0.01438 | 1 |
| rising | 18140 | 0.002756 | 1 |
<!-- quaestor:renderer:end -->
Candidates raised on this section's material: X1 (see the findings section).

## 6. Findings and recommendations

This section follows the model risk management guidance at [[reg:SR26-2:VI.3]].

### F-001 · L1 leakage · severity **high**

**A `L1` finding, raised by `check_leakage` at severity `high`.**
Its evidence is the artifacts cited in this section; the check's own account of it is recorded in `findings.json`.

### F-002 · X1 scenario analysis · severity **high**

**A `X1` finding, raised by `run_scenarios` at severity `high`.**
Its evidence is the artifacts cited in this section; the check's own account of it is recorded in `findings.json`.
The value of `leakage.target_corr.max_single_feature_auc` is 1 [[art:7f74c0d5:leakage.target_corr.max_single_feature_auc]].
The value of `leakage.timing.n_flagged` is 0 [[art:742bcd24:leakage.timing.n_flagged]].
The value of `scenario.convexity` is 140.7 [[art:4451c907:scenario.convexity]].
The value of `scenario.value_change.-300` is -92.11 [[art:0f83fead:scenario.value_change.-300]].
The value of `scenario.value_change.300` is 232.8 [[art:a0678af4:scenario.value_change.300]].
The value of `sign_check.burnout.agrees` is 0 [[art:56826e40:sign_check.burnout.agrees]].
The value of `sign_check.burnout.coef_sign` is -1 [[art:dcfb2de4:sign_check.burnout.coef_sign]].
The value of `sign_check.burnout.univariate_direction` is 1 [[art:bfc96bb2:sign_check.burnout.univariate_direction]].
The value of `sign_check.season_sin.agrees` is 0 [[art:74f2d0e0:sign_check.season_sin.agrees]].
The value of `sign_check.season_sin.coef_sign` is -1 [[art:92ed5b5f:sign_check.season_sin.coef_sign]].
The value of `sign_check.season_sin.univariate_direction` is 1 [[art:cae6b096:sign_check.season_sin.univariate_direction]].
The value of `threshold.L1.single_feature_auc` is 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]].
<!-- quaestor:renderer:begin table leakage.target_corr -->
Each feature against the outcome on train, on its own [[art:ce82a409:leakage.target_corr]]:

| feature | abs_corr | single_feature_auc | numeric |
|---|---|---|---|
| note_rate | 0.0272 | 0.5826 | true |
| orig_ltv | 0.01822 | 0.5572 | true |
| credit_score | 0.03009 | 0.5959 | true |
| orig_upb_log | 0.02222 | 0.5675 | true |
| sato | 0.01787 | 0.5525 | true |
| loan_age | 0.04014 | 0.6284 | true |
| incentive | 0.07061 | 0.7239 | true |
| burnout | 0.05248 | 0.6732 | true |
| bom_balance_log | 0.9317 | 1 | true |
| season_sin | 0.005124 | 0.5149 | true |
| season_cos | 0.01658 | 0.553 | true |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table leakage.timing -->
Each feature's declared timing; flagged means during or after the outcome [[art:8cdad1c5:leakage.timing]]:

| feature | timing | flagged |
|---|---|---|
| note_rate | at_origination | false |
| orig_ltv | at_origination | false |
| credit_score | at_origination | false |
| orig_upb_log | at_origination | false |
| sato | at_origination | false |
| loan_age | before_period_start | false |
| incentive | before_period_start | false |
| burnout | before_period_start | false |
| bom_balance_log | before_period_start | false |
| rate_change_12m | before_period_start | false |
| season_sin | before_period_start | false |
| season_cos | before_period_start | false |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table scenario.value_by_shock -->
Servicing value, its change from the base case and first-year CPR, by shock [[art:c4d5cb25:scenario.value_by_shock]]:

| shock_bp | value | value_change | cpr |
|---|---|---|---|
| -300 | 1.762e+06 | -92.11 | 0.0007734 |
| -200 | 1.762e+06 | -83.78 | 0.0007603 |
| -100 | 1.762e+06 | -57.15 | 0.0007469 |
| 0 | 1.762e+06 | 0 | 0.0007328 |
| 100 | 1.762e+06 | 77.18 | 0.0007184 |
| 200 | 1.762e+06 | 155.8 | 0.0007041 |
| 300 | 1.762e+06 | 232.8 | 0.0006902 |
<!-- quaestor:renderer:end -->

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1, S1), `compute_metrics` (T1, C1, O1), `check_leakage` (L2), `check_stability` (R1), `check_collinearity` (M1), `challenger_compare` (E1).

### Open items

No open item was recorded for this validation.

## 7. Ongoing monitoring recommendations

This section follows the model risk management guidance at [[reg:SR26-2:V.2]].
The value of `metrics.test.auc` is 1 [[art:4619bd69:metrics.test.auc]].
The value of `psi.max` is 0.06189 [[art:c2e8c8fd:psi.max]].
The value of `rule.calibration_first_event_rate` is 0.05 [[art:42f1351e:rule.calibration_first_event_rate]].
The value of `threshold.package.auc.test.min` is 0.65 [[art:fececac1:threshold.package.auc.test.min]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].

## Appendix A — Claims

Grounding precision 1.0000 before repair (318 of 318 claims verified) and 1.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 42/42; conceptual_soundness 49/49; data_integrity 70/70; outcomes 103/103; sensitivity 37/37; findings 12/12; monitoring 5/5.

Developer claims: The package declares 3 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). See Appendix D.

Excluded numeric tokens (not claims): inline_code (`scenario.value_change.-100`, `scenario.value_change.-200`, `scenario.value_change.-300`); citation_hash (d8eca8f5, d0edbe6f, b2440ca1, bcb747a3); regulatory_section_id (SR26-2:V.1.b, SR26-2:V.1.a, SR26-2:VI.3, SR26-2:V.2); finding_id (F-001, F-002).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The value of `challenger.delta_auc` is 0 . | 0 | ratio | challenger |  | eq | `[[art:d8eca8f5:challenger.delta_auc]]` | verified | 0 |
| 2 | summary | The value of `condition_number` is 4.954 . | 4.954 | ratio | condition_number |  | eq | `[[art:d0edbe6f:condition_number]]` | verified | 4.953837779 |
| 3 | summary | The value of `csi.max` is 0.03215 . | 0.03215 | ratio | csi |  | eq | `[[art:b2440ca1:csi.max]]` | verified | 0.03214820108 |
| 4 | summary | The value of `metrics.out_of_time.auc` is 1 . | 1 | ratio | metrics |  | eq | `[[art:bcb747a3:metrics.out_of_time.auc]]` | verified | 1 |
| 5 | summary | The value of `metrics.out_of_time.brier` is 0.00000001376 . | 1.376e-08 | ratio | metrics |  | eq | `[[art:44f11124:metrics.out_of_time.brier]]` | verified | 1.375799568e-08 |
| 6 | summary | The value of `metrics.out_of_time.event_rate` is 0.01795 . | 0.01795 | ratio | metrics |  | eq | `[[art:83ccf5c0:metrics.out_of_time.event_rate]]` | verified | 0.01794892714 |
| 7 | summary | The value of `metrics.out_of_time.gini` is 1 . | 1 | ratio | metrics |  | eq | `[[art:6d939d01:metrics.out_of_time.gini]]` | verified | 1 |
| 8 | summary | The value of `metrics.out_of_time.ks` is 1 . | 1 | ratio | metrics |  | eq | `[[art:e3aa3687:metrics.out_of_time.ks]]` | verified | 1 |
| 9 | summary | The value of `metrics.out_of_time.logloss` is 0.00009057 . | 9.057e-05 | ratio | metrics |  | eq | `[[art:4ff30655:metrics.out_of_time.logloss]]` | verified | 9.056637435e-05 |
| 10 | summary | The value of `metrics.out_of_time.mean_predicted` is 0.01802… | 0.01802 | ratio | metrics |  | eq | `[[art:276f106a:metrics.out_of_time.mean_predicted]]` | verified | 0.01801915996 |
| 11 | summary | The value of `metrics.out_of_time.n` is 12257 . | 12257 | ratio | metrics |  | eq | `[[art:7898809e:metrics.out_of_time.n]]` | verified | 12257 |
| 12 | summary | The value of `metrics.test.auc` is 1 . | 1 | ratio | metrics |  | eq | `[[art:4619bd69:metrics.test.auc]]` | verified | 1 |
| 13 | summary | The value of `metrics.test.brier` is 0.00000001011 . | 1.011e-08 | ratio | metrics |  | eq | `[[art:67fd4fea:metrics.test.brier]]` | verified | 1.01061577e-08 |
| 14 | summary | The value of `metrics.test.event_rate` is 0.008061 . | 0.008061 | ratio | metrics |  | eq | `[[art:570cc08a:metrics.test.event_rate]]` | verified | 0.008061370433 |
| 15 | summary | The value of `metrics.test.gini` is 1 . | 1 | ratio | metrics |  | eq | `[[art:35acd744:metrics.test.gini]]` | verified | 1 |
| 16 | summary | The value of `metrics.test.ks` is 1 . | 1 | ratio | metrics |  | eq | `[[art:a13846c8:metrics.test.ks]]` | verified | 1 |
| 17 | summary | The value of `metrics.test.logloss` is 0.00009043 . | 9.043e-05 | ratio | metrics |  | eq | `[[art:db4e6b76:metrics.test.logloss]]` | verified | 9.04295748e-05 |
| 18 | summary | The value of `metrics.test.mean_predicted` is 0.008144 . | 0.008144 | ratio | metrics |  | eq | `[[art:83863be2:metrics.test.mean_predicted]]` | verified | 0.008144072878 |
| 19 | summary | The value of `metrics.test.n` is 15382 . | 15382 | ratio | metrics |  | eq | `[[art:e55953e1:metrics.test.n]]` | verified | 15382 |
| 20 | summary | The value of `metrics.train.auc` is 1 . | 1 | ratio | metrics |  | eq | `[[art:6269694d:metrics.train.auc]]` | verified | 1 |
| 21 | summary | The value of `metrics.train.brier` is 0.00000001096 . | 1.096e-08 | ratio | metrics |  | eq | `[[art:0c2c4489:metrics.train.brier]]` | verified | 1.095784085e-08 |
| 22 | summary | The value of `metrics.train.event_rate` is 0.008525 . | 0.008525 | ratio | metrics |  | eq | `[[art:b9ef3327:metrics.train.event_rate]]` | verified | 0.008524699414 |
| 23 | summary | The value of `metrics.train.gini` is 1 . | 1 | ratio | metrics |  | eq | `[[art:e2084e07:metrics.train.gini]]` | verified | 1 |
| 24 | summary | The value of `metrics.train.ks` is 1 . | 1 | ratio | metrics |  | eq | `[[art:24c2277d:metrics.train.ks]]` | verified | 1 |
| 25 | summary | The value of `metrics.train.logloss` is 0.00009128 . | 9.128e-05 | ratio | metrics |  | eq | `[[art:1761d10c:metrics.train.logloss]]` | verified | 9.128014231e-05 |
| 26 | summary | The value of `metrics.train.mean_predicted` is 0.008607 . | 0.008607 | ratio | metrics |  | eq | `[[art:6f9330ed:metrics.train.mean_predicted]]` | verified | 0.008606994732 |
| 27 | summary | The value of `metrics.train.n` is 36013 . | 36013 | ratio | metrics |  | eq | `[[art:6fdfeabb:metrics.train.n]]` | verified | 36013 |
| 28 | summary | The value of `metrics.vintage_holdout.auc` is 1 . | 1 | ratio | metrics |  | eq | `[[art:00749c11:metrics.vintage_holdout.auc]]` | verified | 1 |
| 29 | summary | The value of `metrics.vintage_holdout.brier` is 0.0000000086… | 8.646e-09 | ratio | metrics |  | eq | `[[art:c58e369c:metrics.vintage_holdout.brier]]` | verified | 8.645548253e-09 |
| 30 | summary | The value of `metrics.vintage_holdout.event_rate` is 0.00481… | 0.004817 | ratio | metrics |  | eq | `[[art:e3590a16:metrics.vintage_holdout.event_rate]]` | verified | 0.004817105386 |
| 31 | summary | The value of `metrics.vintage_holdout.gini` is 1 . | 1 | ratio | metrics |  | eq | `[[art:f4aa377a:metrics.vintage_holdout.gini]]` | verified | 1 |
| 32 | summary | The value of `metrics.vintage_holdout.ks` is 1 . | 1 | ratio | metrics |  | eq | `[[art:cb4509f6:metrics.vintage_holdout.ks]]` | verified | 1 |
| 33 | summary | The value of `metrics.vintage_holdout.logloss` is 0.00008629… | 8.629e-05 | ratio | metrics |  | eq | `[[art:85bdc089:metrics.vintage_holdout.logloss]]` | verified | 8.629383814e-05 |
| 34 | summary | The value of `metrics.vintage_holdout.mean_predicted` is 0.0… | 0.004899 | ratio | metrics |  | eq | `[[art:af925790:metrics.vintage_holdout.mean_predicted]]` | verified | 0.004898804843 |
| 35 | summary | The value of `metrics.vintage_holdout.n` is 32177 . | 32177 | ratio | metrics |  | eq | `[[art:37a92951:metrics.vintage_holdout.n]]` | verified | 32177 |
| 36 | summary | The value of `profile.test.n` is 15382 . | 15382 | ratio | profile |  | eq | `[[art:e3abc1b8:profile.test.n]]` | verified | 15382 |
| 37 | summary | The value of `profile.train.n` is 36013 . | 36013 | ratio | profile |  | eq | `[[art:c5ebd9c9:profile.train.n]]` | verified | 36013 |
| 38 | summary | The value of `psi.max` is 0.06189 . | 0.06189 | ratio | psi |  | eq | `[[art:c2e8c8fd:psi.max]]` | verified | 0.06188985797 |
| 39 | summary | The value of `runtime.max_seconds` is 300 . | 300 | ratio | runtime |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 40 | summary | The value of `threshold.package.auc.test.min` is 0.65 . | 0.65 | ratio | threshold |  | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 41 | summary | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 42 | summary | The value of `vif.max` is 4.978 . | 4.978 | ratio | vif |  | eq | `[[art:b1d416c0:vif.max]]` | verified | 4.977599595 |
| 43 | conceptual_soundness | The value of `ablation.baseline_auc` is 1 . | 1 | ratio | ablation |  | eq | `[[art:7610ff35:ablation.baseline_auc]]` | verified | 1 |
| 44 | conceptual_soundness | The value of `ablation.bom_balance_log.delta_auc` is -0.2327… | -0.2327 | ratio | ablation |  | eq | `[[art:c226f60f:ablation.bom_balance_log.delta_auc]]` | verified | -0.2327007725 |
| 45 | conceptual_soundness | The value of `ablation.burnout.delta_auc` is 0 . | 0 | ratio | ablation |  | eq | `[[art:d50de877:ablation.burnout.delta_auc]]` | verified | 0 |
| 46 | conceptual_soundness | The value of `ablation.credit_score.delta_auc` is 0 . | 0 | ratio | ablation |  | eq | `[[art:d1dff006:ablation.credit_score.delta_auc]]` | verified | 0 |
| 47 | conceptual_soundness | The value of `ablation.incentive.delta_auc` is 0 . | 0 | ratio | ablation |  | eq | `[[art:33a25e3c:ablation.incentive.delta_auc]]` | verified | 0 |
| 48 | conceptual_soundness | The value of `ablation.loan_age.delta_auc` is 0 . | 0 | ratio | ablation |  | eq | `[[art:1a789b08:ablation.loan_age.delta_auc]]` | verified | 0 |
| 49 | conceptual_soundness | The value of `ablation.note_rate.delta_auc` is 0 . | 0 | ratio | ablation |  | eq | `[[art:65b3f07a:ablation.note_rate.delta_auc]]` | verified | 0 |
| 50 | conceptual_soundness | The value of `ablation.orig_ltv.delta_auc` is 0 . | 0 | ratio | ablation |  | eq | `[[art:370eaea8:ablation.orig_ltv.delta_auc]]` | verified | 0 |
| 51 | conceptual_soundness | The value of `ablation.orig_upb_log.delta_auc` is 0 . | 0 | ratio | ablation |  | eq | `[[art:e245ef14:ablation.orig_upb_log.delta_auc]]` | verified | 0 |
| 52 | conceptual_soundness | The value of `ablation.sato.delta_auc` is 0 . | 0 | ratio | ablation |  | eq | `[[art:2bbb0015:ablation.sato.delta_auc]]` | verified | 0 |
| 53 | conceptual_soundness | The value of `ablation.season_cos.delta_auc` is 0 . | 0 | ratio | ablation |  | eq | `[[art:9453331c:ablation.season_cos.delta_auc]]` | verified | 0 |
| 54 | conceptual_soundness | The value of `ablation.season_sin.delta_auc` is 0 . | 0 | ratio | ablation |  | eq | `[[art:a4f7b0c1:ablation.season_sin.delta_auc]]` | verified | 0 |
| 55 | conceptual_soundness | The value of `challenger.auc` is 1 . | 1 | ratio | challenger |  | eq | `[[art:5aeaf534:challenger.auc]]` | verified | 1 |
| 56 | conceptual_soundness | The value of `challenger.brier` is 0.0000000000003226 . | 3.226e-13 | ratio | challenger |  | eq | `[[art:0b5236ca:challenger.brier]]` | verified | 3.226460021e-13 |
| 57 | conceptual_soundness | The value of `challenger.delta_auc` is 0 . | 0 | ratio | challenger |  | eq | `[[art:d8eca8f5:challenger.delta_auc]]` | verified | 0 |
| 58 | conceptual_soundness | The value of `metrics.test.auc` is 1 . | 1 | ratio | metrics |  | eq | `[[art:4619bd69:metrics.test.auc]]` | verified | 1 |
| 59 | conceptual_soundness | The value of `metrics.test.brier` is 0.00000001011 . | 1.011e-08 | ratio | metrics |  | eq | `[[art:67fd4fea:metrics.test.brier]]` | verified | 1.01061577e-08 |
| 60 | conceptual_soundness | The value of `sign_check.bom_balance_log.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:26b1789b:sign_check.bom_balance_log.agrees]]` | verified | 1 |
| 61 | conceptual_soundness | The value of `sign_check.bom_balance_log.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:d2e88db3:sign_check.bom_balance_log.coef_sign]]` | verified | -1 |
| 62 | conceptual_soundness | The value of `sign_check.bom_balance_log.univariate_directio… | -1 | ratio | sign_check |  | eq | `[[art:8ee4f8fe:sign_check.bom_balance_log.univariate_direction]]` | verified | -1 |
| 63 | conceptual_soundness | The value of `sign_check.burnout.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:56826e40:sign_check.burnout.agrees]]` | verified | 0 |
| 64 | conceptual_soundness | The value of `sign_check.burnout.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:dcfb2de4:sign_check.burnout.coef_sign]]` | verified | -1 |
| 65 | conceptual_soundness | The value of `sign_check.burnout.univariate_direction` is 1… | 1 | ratio | sign_check |  | eq | `[[art:bfc96bb2:sign_check.burnout.univariate_direction]]` | verified | 1 |
| 66 | conceptual_soundness | The value of `sign_check.credit_score.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:915bf8eb:sign_check.credit_score.agrees]]` | verified | 1 |
| 67 | conceptual_soundness | The value of `sign_check.credit_score.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:1ec1078b:sign_check.credit_score.coef_sign]]` | verified | 1 |
| 68 | conceptual_soundness | The value of `sign_check.credit_score.univariate_direction`… | 1 | ratio | sign_check |  | eq | `[[art:42303896:sign_check.credit_score.univariate_direction]]` | verified | 1 |
| 69 | conceptual_soundness | The value of `sign_check.incentive.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:f7b2338e:sign_check.incentive.agrees]]` | verified | 1 |
| 70 | conceptual_soundness | The value of `sign_check.incentive.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:684cf11a:sign_check.incentive.coef_sign]]` | verified | 1 |
| 71 | conceptual_soundness | The value of `sign_check.incentive.univariate_direction` is… | 1 | ratio | sign_check |  | eq | `[[art:8098d951:sign_check.incentive.univariate_direction]]` | verified | 1 |
| 72 | conceptual_soundness | The value of `sign_check.n_disagreements` is 2 . | 2 | ratio | sign_check |  | eq | `[[art:66ce738a:sign_check.n_disagreements]]` | verified | 2 |
| 73 | conceptual_soundness | The value of `sign_check.note_rate.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:ca18290e:sign_check.note_rate.agrees]]` | verified | 1 |
| 74 | conceptual_soundness | The value of `sign_check.note_rate.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:0e3296a5:sign_check.note_rate.coef_sign]]` | verified | 1 |
| 75 | conceptual_soundness | The value of `sign_check.note_rate.univariate_direction` is… | 1 | ratio | sign_check |  | eq | `[[art:61f6e1ac:sign_check.note_rate.univariate_direction]]` | verified | 1 |
| 76 | conceptual_soundness | The value of `sign_check.orig_ltv.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:7021aeb0:sign_check.orig_ltv.agrees]]` | verified | 1 |
| 77 | conceptual_soundness | The value of `sign_check.orig_ltv.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:7eec65ec:sign_check.orig_ltv.coef_sign]]` | verified | -1 |
| 78 | conceptual_soundness | The value of `sign_check.orig_ltv.univariate_direction` is -… | -1 | ratio | sign_check |  | eq | `[[art:76dbc708:sign_check.orig_ltv.univariate_direction]]` | verified | -1 |
| 79 | conceptual_soundness | The value of `sign_check.orig_upb_log.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:07a9d3e6:sign_check.orig_upb_log.agrees]]` | verified | 1 |
| 80 | conceptual_soundness | The value of `sign_check.orig_upb_log.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:5aa309fc:sign_check.orig_upb_log.coef_sign]]` | verified | 1 |
| 81 | conceptual_soundness | The value of `sign_check.orig_upb_log.univariate_direction`… | 1 | ratio | sign_check |  | eq | `[[art:b9743ecb:sign_check.orig_upb_log.univariate_direction]]` | verified | 1 |
| 82 | conceptual_soundness | The value of `sign_check.sato.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:2401eba2:sign_check.sato.agrees]]` | verified | 1 |
| 83 | conceptual_soundness | The value of `sign_check.sato.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:c031d0d5:sign_check.sato.coef_sign]]` | verified | 1 |
| 84 | conceptual_soundness | The value of `sign_check.sato.univariate_direction` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:c08233a6:sign_check.sato.univariate_direction]]` | verified | 1 |
| 85 | conceptual_soundness | The value of `sign_check.season_cos.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:7f18ddf7:sign_check.season_cos.agrees]]` | verified | 1 |
| 86 | conceptual_soundness | The value of `sign_check.season_cos.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:7dbb1ffc:sign_check.season_cos.coef_sign]]` | verified | -1 |
| 87 | conceptual_soundness | The value of `sign_check.season_cos.univariate_direction` is… | -1 | ratio | sign_check |  | eq | `[[art:03e931f0:sign_check.season_cos.univariate_direction]]` | verified | -1 |
| 88 | conceptual_soundness | The value of `sign_check.season_sin.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:74f2d0e0:sign_check.season_sin.agrees]]` | verified | 0 |
| 89 | conceptual_soundness | The value of `sign_check.season_sin.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:92ed5b5f:sign_check.season_sin.coef_sign]]` | verified | -1 |
| 90 | conceptual_soundness | The value of `sign_check.season_sin.univariate_direction` is… | 1 | ratio | sign_check |  | eq | `[[art:cae6b096:sign_check.season_sin.univariate_direction]]` | verified | 1 |
| 91 | conceptual_soundness | The value of `threshold.E1.delta_auc` is 0.03 . | 0.03 | ratio | threshold |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 92 | data_integrity | The value of `csi.bom_balance_log` is 0.03215 . | 0.03215 | ratio | csi |  | eq | `[[art:60a10892:csi.bom_balance_log]]` | verified | 0.03214820108 |
| 93 | data_integrity | The value of `csi.burnout` is 0.0001016 . | 0.0001016 | ratio | csi |  | eq | `[[art:a5da1daa:csi.burnout]]` | verified | 0.0001015529196 |
| 94 | data_integrity | The value of `csi.credit_score` is 0.000223 . | 0.000223 | ratio | csi |  | eq | `[[art:d87a2d40:csi.credit_score]]` | verified | 0.000223048204 |
| 95 | data_integrity | The value of `csi.incentive` is 0.00009278 . | 9.278e-05 | ratio | csi |  | eq | `[[art:41325258:csi.incentive]]` | verified | 9.278494663e-05 |
| 96 | data_integrity | The value of `csi.loan_age` is 0 . | 0 | ratio | csi |  | eq | `[[art:df52c920:csi.loan_age]]` | verified | 0 |
| 97 | data_integrity | The value of `csi.max` is 0.03215 . | 0.03215 | ratio | csi |  | eq | `[[art:b2440ca1:csi.max]]` | verified | 0.03214820108 |
| 98 | data_integrity | The value of `csi.note_rate` is 0.0003806 . | 0.0003806 | ratio | csi |  | eq | `[[art:587b33e9:csi.note_rate]]` | verified | 0.0003806385501 |
| 99 | data_integrity | The value of `csi.orig_ltv` is 0.0008996 . | 0.0008996 | ratio | csi |  | eq | `[[art:7ea837e1:csi.orig_ltv]]` | verified | 0.0008996218814 |
| 100 | data_integrity | The value of `csi.orig_upb_log` is 0.004636 . | 0.004636 | ratio | csi |  | eq | `[[art:5d1c16f2:csi.orig_upb_log]]` | verified | 0.004635722963 |
| 101 | data_integrity | The value of `csi.sato` is 0.000449 . | 0.000449 | ratio | csi |  | eq | `[[art:fb71eb9e:csi.sato]]` | verified | 0.0004490205147 |
| 102 | data_integrity | The value of `csi.season_cos` is 0.00001935 . | 1.935e-05 | ratio | csi |  | eq | `[[art:de66f2c6:csi.season_cos]]` | verified | 1.934566399e-05 |
| 103 | data_integrity | The value of `csi.season_sin` is 0.000001386 . | 1.386e-06 | ratio | csi |  | eq | `[[art:4c3f0dd9:csi.season_sin]]` | verified | 1.386212619e-06 |
| 104 | data_integrity | The value of `leakage.duplicates.train` is 0 . | 0 | ratio | leakage |  | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 105 | data_integrity | The value of `leakage.name_screen.n_matched` is 0 . | 0 | ratio | leakage |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 106 | data_integrity | The value of `leakage.overlap` is 0 . | 0 | ratio | leakage |  | eq | `[[art:4c9fcd09:leakage.overlap]]` | verified | 0 |
| 107 | data_integrity | The value of `leakage.overlap.features` is 0 . | 0 | ratio | leakage |  | eq | `[[art:0fec8048:leakage.overlap.features]]` | verified | 0 |
| 108 | data_integrity | The value of `leakage.overlap.ids` is 0 . | 0 | ratio | leakage |  | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 109 | data_integrity | The value of `leakage.target_corr.max_single_feature_auc` is… | 1 | ratio | leakage |  | eq | `[[art:7f74c0d5:leakage.target_corr.max_single_feature_auc]]` | verified | 1 |
| 110 | data_integrity | The value of `leakage.timing.n_flagged` is 0 . | 0 | ratio | leakage |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 111 | data_integrity | The value of `profile.out_of_time.missing.max` is 0 . | 0 | ratio | profile |  | eq | `[[art:4dafce11:profile.out_of_time.missing.max]]` | verified | 0 |
| 112 | data_integrity | The value of `profile.out_of_time.n` is 12257 . | 12257 | ratio | profile |  | eq | `[[art:fa39c5cf:profile.out_of_time.n]]` | verified | 12257 |
| 113 | data_integrity | The value of `profile.test.missing.max` is 0 . | 0 | ratio | profile |  | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 114 | data_integrity | The value of `profile.test.n` is 15382 . | 15382 | ratio | profile |  | eq | `[[art:e3abc1b8:profile.test.n]]` | verified | 15382 |
| 115 | data_integrity | The value of `profile.train.missing.max` is 0 . | 0 | ratio | profile |  | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 116 | data_integrity | The value of `profile.train.n` is 36013 . | 36013 | ratio | profile |  | eq | `[[art:c5ebd9c9:profile.train.n]]` | verified | 36013 |
| 117 | data_integrity | The value of `profile.vintage_holdout.missing.max` is 0 . | 0 | ratio | profile |  | eq | `[[art:329bb430:profile.vintage_holdout.missing.max]]` | verified | 0 |
| 118 | data_integrity | The value of `profile.vintage_holdout.n` is 32177 . | 32177 | ratio | profile |  | eq | `[[art:426e712a:profile.vintage_holdout.n]]` | verified | 32177 |
| 119 | data_integrity | The value of `psi.bom_balance_log` is 0.03018 . | 0.03018 | ratio | psi |  | eq | `[[art:ce3c425c:psi.bom_balance_log]]` | verified | 0.03017956995 |
| 120 | data_integrity | The value of `psi.burnout` is 0.004614 . | 0.004614 | ratio | psi |  | eq | `[[art:9dc7ecc2:psi.burnout]]` | verified | 0.004614338236 |
| 121 | data_integrity | The value of `psi.credit_score` is 0.06189 . | 0.06189 | ratio | psi |  | eq | `[[art:7e87527c:psi.credit_score]]` | verified | 0.06188985797 |
| 122 | data_integrity | The value of `psi.incentive` is 0.0009923 . | 0.0009923 | ratio | psi |  | eq | `[[art:2da5570f:psi.incentive]]` | verified | 0.0009922551416 |
| 123 | data_integrity | The value of `psi.loan_age` is 0.0001994 . | 0.0001994 | ratio | psi |  | eq | `[[art:2202b157:psi.loan_age]]` | verified | 0.0001993816816 |
| 124 | data_integrity | The value of `psi.max` is 0.06189 . | 0.06189 | ratio | psi |  | eq | `[[art:c2e8c8fd:psi.max]]` | verified | 0.06188985797 |
| 125 | data_integrity | The value of `psi.note_rate` is 0.01371 . | 0.01371 | ratio | psi |  | eq | `[[art:ecc6adf3:psi.note_rate]]` | verified | 0.01370911382 |
| 126 | data_integrity | The value of `psi.orig_ltv` is 0.03617 . | 0.03617 | ratio | psi |  | eq | `[[art:cd1ff136:psi.orig_ltv]]` | verified | 0.03617297258 |
| 127 | data_integrity | The value of `psi.orig_upb_log` is 0.04817 . | 0.04817 | ratio | psi |  | eq | `[[art:55030a3b:psi.orig_upb_log]]` | verified | 0.04817081196 |
| 128 | data_integrity | The value of `psi.out_of_time.bom_balance_log` is 0.08708 . | 0.08708 | ratio | psi |  | eq | `[[art:9fa682d1:psi.out_of_time.bom_balance_log]]` | verified | 0.08707630682 |
| 129 | data_integrity | The value of `psi.out_of_time.burnout` is 2.945 . | 2.945 | ratio | psi |  | eq | `[[art:7b0bbebb:psi.out_of_time.burnout]]` | verified | 2.944521522 |
| 130 | data_integrity | The value of `psi.out_of_time.credit_score` is 0.05988 . | 0.05988 | ratio | psi |  | eq | `[[art:d7249e47:psi.out_of_time.credit_score]]` | verified | 0.05987964443 |
| 131 | data_integrity | The value of `psi.out_of_time.incentive` is 0.4958 . | 0.4958 | ratio | psi |  | eq | `[[art:42076ed1:psi.out_of_time.incentive]]` | verified | 0.4958065489 |
| 132 | data_integrity | The value of `psi.out_of_time.loan_age` is 2.484 . | 2.484 | ratio | psi |  | eq | `[[art:d6eaaaf5:psi.out_of_time.loan_age]]` | verified | 2.483993033 |
| 133 | data_integrity | The value of `psi.out_of_time.note_rate` is 0.6977 . | 0.6977 | ratio | psi |  | eq | `[[art:cabd371d:psi.out_of_time.note_rate]]` | verified | 0.6976589281 |
| 134 | data_integrity | The value of `psi.out_of_time.orig_ltv` is 0.04301 . | 0.04301 | ratio | psi |  | eq | `[[art:3eee5db4:psi.out_of_time.orig_ltv]]` | verified | 0.04300793312 |
| 135 | data_integrity | The value of `psi.out_of_time.orig_upb_log` is 0.07136 . | 0.07136 | ratio | psi |  | eq | `[[art:ac349b67:psi.out_of_time.orig_upb_log]]` | verified | 0.07136421414 |
| 136 | data_integrity | The value of `psi.out_of_time.sato` is 0.01299 . | 0.01299 | ratio | psi |  | eq | `[[art:c2233ce6:psi.out_of_time.sato]]` | verified | 0.01298850667 |
| 137 | data_integrity | The value of `psi.out_of_time.season_cos` is 0.007524 . | 0.007524 | ratio | psi |  | eq | `[[art:25cf6b85:psi.out_of_time.season_cos]]` | verified | 0.00752368457 |
| 138 | data_integrity | The value of `psi.out_of_time.season_sin` is 0.02789 . | 0.02789 | ratio | psi |  | eq | `[[art:144e1bd9:psi.out_of_time.season_sin]]` | verified | 0.02788988464 |
| 139 | data_integrity | The value of `psi.out_of_time.y_score` is 0.1451 . | 0.1451 | ratio | psi |  | eq | `[[art:12620838:psi.out_of_time.y_score]]` | verified | 0.1450932669 |
| 140 | data_integrity | The value of `psi.sato` is 0.02773 . | 0.02773 | ratio | psi |  | eq | `[[art:584da64f:psi.sato]]` | verified | 0.02772829856 |
| 141 | data_integrity | The value of `psi.season_cos` is 0.0000179 . | 1.79e-05 | ratio | psi |  | eq | `[[art:addec503:psi.season_cos]]` | verified | 1.790085913e-05 |
| 142 | data_integrity | The value of `psi.season_sin` is 0.000002939 . | 2.939e-06 | ratio | psi |  | eq | `[[art:4d2ed98d:psi.season_sin]]` | verified | 2.939045338e-06 |
| 143 | data_integrity | The value of `psi.vintage_holdout.bom_balance_log` is 0.0370… | 0.03707 | ratio | psi |  | eq | `[[art:b3073b46:psi.vintage_holdout.bom_balance_log]]` | verified | 0.03706738664 |
| 144 | data_integrity | The value of `psi.vintage_holdout.burnout` is 0.04749 . | 0.04749 | ratio | psi |  | eq | `[[art:e29067e6:psi.vintage_holdout.burnout]]` | verified | 0.04749372789 |
| 145 | data_integrity | The value of `psi.vintage_holdout.credit_score` is 0.03996 . | 0.03996 | ratio | psi |  | eq | `[[art:3498d307:psi.vintage_holdout.credit_score]]` | verified | 0.03995819732 |
| 146 | data_integrity | The value of `psi.vintage_holdout.incentive` is 0.4475 . | 0.4475 | ratio | psi |  | eq | `[[art:5e61b6f9:psi.vintage_holdout.incentive]]` | verified | 0.4475226601 |
| 147 | data_integrity | The value of `psi.vintage_holdout.loan_age` is 0.07112 . | 0.07112 | ratio | psi |  | eq | `[[art:6d92c48b:psi.vintage_holdout.loan_age]]` | verified | 0.07111526296 |
| 148 | data_integrity | The value of `psi.vintage_holdout.note_rate` is 0.6088 . | 0.6088 | ratio | psi |  | eq | `[[art:f281f8a7:psi.vintage_holdout.note_rate]]` | verified | 0.608822927 |
| 149 | data_integrity | The value of `psi.vintage_holdout.orig_ltv` is 0.02942 . | 0.02942 | ratio | psi |  | eq | `[[art:d07cfb7d:psi.vintage_holdout.orig_ltv]]` | verified | 0.0294150369 |
| 150 | data_integrity | The value of `psi.vintage_holdout.orig_upb_log` is 0.0404 . | 0.0404 | ratio | psi |  | eq | `[[art:77ec758a:psi.vintage_holdout.orig_upb_log]]` | verified | 0.04039645306 |
| 151 | data_integrity | The value of `psi.vintage_holdout.sato` is 0.02989 . | 0.02989 | ratio | psi |  | eq | `[[art:eea64c25:psi.vintage_holdout.sato]]` | verified | 0.02989256711 |
| 152 | data_integrity | The value of `psi.vintage_holdout.season_cos` is 0.001288 . | 0.001288 | ratio | psi |  | eq | `[[art:9fe842a8:psi.vintage_holdout.season_cos]]` | verified | 0.0012879007 |
| 153 | data_integrity | The value of `psi.vintage_holdout.season_sin` is 0.0007309 . | 0.0007309 | ratio | psi |  | eq | `[[art:b0dc9745:psi.vintage_holdout.season_sin]]` | verified | 0.0007309374015 |
| 154 | data_integrity | The value of `psi.vintage_holdout.y_score` is 0.05813 . | 0.05813 | ratio | psi |  | eq | `[[art:33ffbed6:psi.vintage_holdout.y_score]]` | verified | 0.05813498782 |
| 155 | data_integrity | The value of `psi.y_score` is 0.01874 . | 0.01874 | ratio | psi |  | eq | `[[art:2ad82680:psi.y_score]]` | verified | 0.01873789359 |
| 156 | data_integrity | The value of `threshold.D1.missing_gap` is 0.1 . | 0.1 | ratio | threshold |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 157 | data_integrity | The value of `threshold.L1.single_feature_auc` is 0.9 . | 0.9 | ratio | threshold |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 158 | data_integrity | The value of `threshold.L2.overlap` is 0.005 . | 0.005 | ratio | threshold |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 159 | data_integrity | The value of `threshold.L2.overlap.features_effective` is 0.… | 0.005 | ratio | threshold |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 160 | data_integrity | The value of `threshold.S1.psi` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 161 | data_integrity | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 162 | outcomes | The value of `calibration.mean_rel_gap.out_of_time` is 0.003… | 0.003913 | ratio | calibration |  | eq | `[[art:68619260:calibration.mean_rel_gap.out_of_time]]` | verified | 0.003912925468 |
| 163 | outcomes | The value of `calibration.mean_rel_gap.test` is 0.01026 . | 0.01026 | ratio | calibration |  | eq | `[[art:4e1854b1:calibration.mean_rel_gap.test]]` | verified | 0.01025910486 |
| 164 | outcomes | The value of `calibration.mean_rel_gap.train` is 0.009654 . | 0.009654 | ratio | calibration |  | eq | `[[art:db1bca38:calibration.mean_rel_gap.train]]` | verified | 0.009653750145 |
| 165 | outcomes | The value of `calibration.mean_rel_gap.vintage_holdout` is 0… | 0.01696 | ratio | calibration |  | eq | `[[art:1438e44d:calibration.mean_rel_gap.vintage_holdout]]` | verified | 0.01696028022 |
| 166 | outcomes | The value of `calibration.separable.out_of_time` is 1 . | 1 | ratio | calibration |  | eq | `[[art:258b7972:calibration.separable.out_of_time]]` | verified | 1 |
| 167 | outcomes | The value of `calibration.separable.test` is 1 . | 1 | ratio | calibration |  | eq | `[[art:81c3fa7a:calibration.separable.test]]` | verified | 1 |
| 168 | outcomes | The value of `calibration.separable.train` is 1 . | 1 | ratio | calibration |  | eq | `[[art:d7ee2241:calibration.separable.train]]` | verified | 1 |
| 169 | outcomes | The value of `calibration.separable.vintage_holdout` is 1 . | 1 | ratio | calibration |  | eq | `[[art:137e2c39:calibration.separable.vintage_holdout]]` | verified | 1 |
| 170 | outcomes | The value of `cpr.out_of_time.mae` is 0.0007118 . | 0.0007118 | ratio | cpr |  | eq | `[[art:bdc9d54f:cpr.out_of_time.mae]]` | verified | 0.0007117577187 |
| 171 | outcomes | The value of `cpr.test.mae` is 0.0009292 . | 0.0009292 | ratio | cpr |  | eq | `[[art:be219b85:cpr.test.mae]]` | verified | 0.0009292114418 |
| 172 | outcomes | The value of `cpr.train.mae` is 0.000928 . | 0.000928 | ratio | cpr |  | eq | `[[art:99b2b87f:cpr.train.mae]]` | verified | 0.0009279500644 |
| 173 | outcomes | The value of `cpr.vintage_holdout.mae` is 0.0009299 . | 0.0009299 | ratio | cpr |  | eq | `[[art:d1a19e91:cpr.vintage_holdout.mae]]` | verified | 0.0009298655279 |
| 174 | outcomes | The value of `deciles.out_of_time.top2_capture` is 1 . | 1 | ratio | deciles |  | eq | `[[art:d3114d7a:deciles.out_of_time.top2_capture]]` | verified | 1 |
| 175 | outcomes | The value of `deciles.test.top2_capture` is 1 . | 1 | ratio | deciles |  | eq | `[[art:466bfdc8:deciles.test.top2_capture]]` | verified | 1 |
| 176 | outcomes | The value of `deciles.train.top2_capture` is 1 . | 1 | ratio | deciles |  | eq | `[[art:194d1fbd:deciles.train.top2_capture]]` | verified | 1 |
| 177 | outcomes | The value of `deciles.vintage_holdout.top2_capture` is 1 . | 1 | ratio | deciles |  | eq | `[[art:db275674:deciles.vintage_holdout.top2_capture]]` | verified | 1 |
| 178 | outcomes | The value of `metrics.out_of_time.auc` is 1 . | 1 | ratio | metrics |  | eq | `[[art:bcb747a3:metrics.out_of_time.auc]]` | verified | 1 |
| 179 | outcomes | The value of `metrics.out_of_time.brier` is 0.00000001376 . | 1.376e-08 | ratio | metrics |  | eq | `[[art:44f11124:metrics.out_of_time.brier]]` | verified | 1.375799568e-08 |
| 180 | outcomes | The value of `metrics.out_of_time.event_rate` is 0.01795 . | 0.01795 | ratio | metrics |  | eq | `[[art:83ccf5c0:metrics.out_of_time.event_rate]]` | verified | 0.01794892714 |
| 181 | outcomes | The value of `metrics.out_of_time.gini` is 1 . | 1 | ratio | metrics |  | eq | `[[art:6d939d01:metrics.out_of_time.gini]]` | verified | 1 |
| 182 | outcomes | The value of `metrics.out_of_time.ks` is 1 . | 1 | ratio | metrics |  | eq | `[[art:e3aa3687:metrics.out_of_time.ks]]` | verified | 1 |
| 183 | outcomes | The value of `metrics.out_of_time.logloss` is 0.00009057 . | 9.057e-05 | ratio | metrics |  | eq | `[[art:4ff30655:metrics.out_of_time.logloss]]` | verified | 9.056637435e-05 |
| 184 | outcomes | The value of `metrics.out_of_time.mean_predicted` is 0.01802… | 0.01802 | ratio | metrics |  | eq | `[[art:276f106a:metrics.out_of_time.mean_predicted]]` | verified | 0.01801915996 |
| 185 | outcomes | The value of `metrics.out_of_time.n` is 12257 . | 12257 | ratio | metrics |  | eq | `[[art:7898809e:metrics.out_of_time.n]]` | verified | 12257 |
| 186 | outcomes | The value of `metrics.test.auc` is 1 . | 1 | ratio | metrics |  | eq | `[[art:4619bd69:metrics.test.auc]]` | verified | 1 |
| 187 | outcomes | The value of `metrics.test.brier` is 0.00000001011 . | 1.011e-08 | ratio | metrics |  | eq | `[[art:67fd4fea:metrics.test.brier]]` | verified | 1.01061577e-08 |
| 188 | outcomes | The value of `metrics.test.event_rate` is 0.008061 . | 0.008061 | ratio | metrics |  | eq | `[[art:570cc08a:metrics.test.event_rate]]` | verified | 0.008061370433 |
| 189 | outcomes | The value of `metrics.test.gini` is 1 . | 1 | ratio | metrics |  | eq | `[[art:35acd744:metrics.test.gini]]` | verified | 1 |
| 190 | outcomes | The value of `metrics.test.ks` is 1 . | 1 | ratio | metrics |  | eq | `[[art:a13846c8:metrics.test.ks]]` | verified | 1 |
| 191 | outcomes | The value of `metrics.test.logloss` is 0.00009043 . | 9.043e-05 | ratio | metrics |  | eq | `[[art:db4e6b76:metrics.test.logloss]]` | verified | 9.04295748e-05 |
| 192 | outcomes | The value of `metrics.test.mean_predicted` is 0.008144 . | 0.008144 | ratio | metrics |  | eq | `[[art:83863be2:metrics.test.mean_predicted]]` | verified | 0.008144072878 |
| 193 | outcomes | The value of `metrics.test.n` is 15382 . | 15382 | ratio | metrics |  | eq | `[[art:e55953e1:metrics.test.n]]` | verified | 15382 |
| 194 | outcomes | The value of `metrics.train.auc` is 1 . | 1 | ratio | metrics |  | eq | `[[art:6269694d:metrics.train.auc]]` | verified | 1 |
| 195 | outcomes | The value of `metrics.train.brier` is 0.00000001096 . | 1.096e-08 | ratio | metrics |  | eq | `[[art:0c2c4489:metrics.train.brier]]` | verified | 1.095784085e-08 |
| 196 | outcomes | The value of `metrics.train.event_rate` is 0.008525 . | 0.008525 | ratio | metrics |  | eq | `[[art:b9ef3327:metrics.train.event_rate]]` | verified | 0.008524699414 |
| 197 | outcomes | The value of `metrics.train.gini` is 1 . | 1 | ratio | metrics |  | eq | `[[art:e2084e07:metrics.train.gini]]` | verified | 1 |
| 198 | outcomes | The value of `metrics.train.ks` is 1 . | 1 | ratio | metrics |  | eq | `[[art:24c2277d:metrics.train.ks]]` | verified | 1 |
| 199 | outcomes | The value of `metrics.train.logloss` is 0.00009128 . | 9.128e-05 | ratio | metrics |  | eq | `[[art:1761d10c:metrics.train.logloss]]` | verified | 9.128014231e-05 |
| 200 | outcomes | The value of `metrics.train.mean_predicted` is 0.008607 . | 0.008607 | ratio | metrics |  | eq | `[[art:6f9330ed:metrics.train.mean_predicted]]` | verified | 0.008606994732 |
| 201 | outcomes | The value of `metrics.train.n` is 36013 . | 36013 | ratio | metrics |  | eq | `[[art:6fdfeabb:metrics.train.n]]` | verified | 36013 |
| 202 | outcomes | The value of `metrics.vintage_holdout.auc` is 1 . | 1 | ratio | metrics |  | eq | `[[art:00749c11:metrics.vintage_holdout.auc]]` | verified | 1 |
| 203 | outcomes | The value of `metrics.vintage_holdout.brier` is 0.0000000086… | 8.646e-09 | ratio | metrics |  | eq | `[[art:c58e369c:metrics.vintage_holdout.brier]]` | verified | 8.645548253e-09 |
| 204 | outcomes | The value of `metrics.vintage_holdout.event_rate` is 0.00481… | 0.004817 | ratio | metrics |  | eq | `[[art:e3590a16:metrics.vintage_holdout.event_rate]]` | verified | 0.004817105386 |
| 205 | outcomes | The value of `metrics.vintage_holdout.gini` is 1 . | 1 | ratio | metrics |  | eq | `[[art:f4aa377a:metrics.vintage_holdout.gini]]` | verified | 1 |
| 206 | outcomes | The value of `metrics.vintage_holdout.ks` is 1 . | 1 | ratio | metrics |  | eq | `[[art:cb4509f6:metrics.vintage_holdout.ks]]` | verified | 1 |
| 207 | outcomes | The value of `metrics.vintage_holdout.logloss` is 0.00008629… | 8.629e-05 | ratio | metrics |  | eq | `[[art:85bdc089:metrics.vintage_holdout.logloss]]` | verified | 8.629383814e-05 |
| 208 | outcomes | The value of `metrics.vintage_holdout.mean_predicted` is 0.0… | 0.004899 | ratio | metrics |  | eq | `[[art:af925790:metrics.vintage_holdout.mean_predicted]]` | verified | 0.004898804843 |
| 209 | outcomes | The value of `metrics.vintage_holdout.n` is 32177 . | 32177 | ratio | metrics |  | eq | `[[art:37a92951:metrics.vintage_holdout.n]]` | verified | 32177 |
| 210 | outcomes | The value of `psi.bom_balance_log` is 0.03018 . | 0.03018 | ratio | psi |  | eq | `[[art:ce3c425c:psi.bom_balance_log]]` | verified | 0.03017956995 |
| 211 | outcomes | The value of `psi.burnout` is 0.004614 . | 0.004614 | ratio | psi |  | eq | `[[art:9dc7ecc2:psi.burnout]]` | verified | 0.004614338236 |
| 212 | outcomes | The value of `psi.credit_score` is 0.06189 . | 0.06189 | ratio | psi |  | eq | `[[art:7e87527c:psi.credit_score]]` | verified | 0.06188985797 |
| 213 | outcomes | The value of `psi.incentive` is 0.0009923 . | 0.0009923 | ratio | psi |  | eq | `[[art:2da5570f:psi.incentive]]` | verified | 0.0009922551416 |
| 214 | outcomes | The value of `psi.loan_age` is 0.0001994 . | 0.0001994 | ratio | psi |  | eq | `[[art:2202b157:psi.loan_age]]` | verified | 0.0001993816816 |
| 215 | outcomes | The value of `psi.max` is 0.06189 . | 0.06189 | ratio | psi |  | eq | `[[art:c2e8c8fd:psi.max]]` | verified | 0.06188985797 |
| 216 | outcomes | The value of `psi.note_rate` is 0.01371 . | 0.01371 | ratio | psi |  | eq | `[[art:ecc6adf3:psi.note_rate]]` | verified | 0.01370911382 |
| 217 | outcomes | The value of `psi.orig_ltv` is 0.03617 . | 0.03617 | ratio | psi |  | eq | `[[art:cd1ff136:psi.orig_ltv]]` | verified | 0.03617297258 |
| 218 | outcomes | The value of `psi.orig_upb_log` is 0.04817 . | 0.04817 | ratio | psi |  | eq | `[[art:55030a3b:psi.orig_upb_log]]` | verified | 0.04817081196 |
| 219 | outcomes | The value of `psi.out_of_time.bom_balance_log` is 0.08708 . | 0.08708 | ratio | psi |  | eq | `[[art:9fa682d1:psi.out_of_time.bom_balance_log]]` | verified | 0.08707630682 |
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
| 230 | outcomes | The value of `psi.out_of_time.y_score` is 0.1451 . | 0.1451 | ratio | psi |  | eq | `[[art:12620838:psi.out_of_time.y_score]]` | verified | 0.1450932669 |
| 231 | outcomes | The value of `psi.sato` is 0.02773 . | 0.02773 | ratio | psi |  | eq | `[[art:584da64f:psi.sato]]` | verified | 0.02772829856 |
| 232 | outcomes | The value of `psi.season_cos` is 0.0000179 . | 1.79e-05 | ratio | psi |  | eq | `[[art:addec503:psi.season_cos]]` | verified | 1.790085913e-05 |
| 233 | outcomes | The value of `psi.season_sin` is 0.000002939 . | 2.939e-06 | ratio | psi |  | eq | `[[art:4d2ed98d:psi.season_sin]]` | verified | 2.939045338e-06 |
| 234 | outcomes | The value of `psi.vintage_holdout.bom_balance_log` is 0.0370… | 0.03707 | ratio | psi |  | eq | `[[art:b3073b46:psi.vintage_holdout.bom_balance_log]]` | verified | 0.03706738664 |
| 235 | outcomes | The value of `psi.vintage_holdout.burnout` is 0.04749 . | 0.04749 | ratio | psi |  | eq | `[[art:e29067e6:psi.vintage_holdout.burnout]]` | verified | 0.04749372789 |
| 236 | outcomes | The value of `psi.vintage_holdout.credit_score` is 0.03996 . | 0.03996 | ratio | psi |  | eq | `[[art:3498d307:psi.vintage_holdout.credit_score]]` | verified | 0.03995819732 |
| 237 | outcomes | The value of `psi.vintage_holdout.incentive` is 0.4475 . | 0.4475 | ratio | psi |  | eq | `[[art:5e61b6f9:psi.vintage_holdout.incentive]]` | verified | 0.4475226601 |
| 238 | outcomes | The value of `psi.vintage_holdout.loan_age` is 0.07112 . | 0.07112 | ratio | psi |  | eq | `[[art:6d92c48b:psi.vintage_holdout.loan_age]]` | verified | 0.07111526296 |
| 239 | outcomes | The value of `psi.vintage_holdout.note_rate` is 0.6088 . | 0.6088 | ratio | psi |  | eq | `[[art:f281f8a7:psi.vintage_holdout.note_rate]]` | verified | 0.608822927 |
| 240 | outcomes | The value of `psi.vintage_holdout.orig_ltv` is 0.02942 . | 0.02942 | ratio | psi |  | eq | `[[art:d07cfb7d:psi.vintage_holdout.orig_ltv]]` | verified | 0.0294150369 |
| 241 | outcomes | The value of `psi.vintage_holdout.orig_upb_log` is 0.0404 . | 0.0404 | ratio | psi |  | eq | `[[art:77ec758a:psi.vintage_holdout.orig_upb_log]]` | verified | 0.04039645306 |
| 242 | outcomes | The value of `psi.vintage_holdout.sato` is 0.02989 . | 0.02989 | ratio | psi |  | eq | `[[art:eea64c25:psi.vintage_holdout.sato]]` | verified | 0.02989256711 |
| 243 | outcomes | The value of `psi.vintage_holdout.season_cos` is 0.001288 . | 0.001288 | ratio | psi |  | eq | `[[art:9fe842a8:psi.vintage_holdout.season_cos]]` | verified | 0.0012879007 |
| 244 | outcomes | The value of `psi.vintage_holdout.season_sin` is 0.0007309 . | 0.0007309 | ratio | psi |  | eq | `[[art:b0dc9745:psi.vintage_holdout.season_sin]]` | verified | 0.0007309374015 |
| 245 | outcomes | The value of `psi.vintage_holdout.y_score` is 0.05813 . | 0.05813 | ratio | psi |  | eq | `[[art:33ffbed6:psi.vintage_holdout.y_score]]` | verified | 0.05813498782 |
| 246 | outcomes | The value of `psi.y_score` is 0.01874 . | 0.01874 | ratio | psi |  | eq | `[[art:2ad82680:psi.y_score]]` | verified | 0.01873789359 |
| 247 | outcomes | The value of `threshold.C1.calibration_slope.max` is 1.2 . | 1.2 | ratio | threshold |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 248 | outcomes | The value of `threshold.C1.calibration_slope.min` is 0.8 . | 0.8 | ratio | threshold |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 249 | outcomes | The value of `threshold.C1.mean_ratio_rel` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 250 | outcomes | The value of `threshold.D1.missing_gap` is 0.1 . | 0.1 | ratio | threshold |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 251 | outcomes | The value of `threshold.E1.delta_auc` is 0.03 . | 0.03 | ratio | threshold |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 252 | outcomes | The value of `threshold.L1.single_feature_auc` is 0.9 . | 0.9 | ratio | threshold |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 253 | outcomes | The value of `threshold.L2.overlap` is 0.005 . | 0.005 | ratio | threshold |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 254 | outcomes | The value of `threshold.L2.overlap.features_effective` is 0.… | 0.005 | ratio | threshold |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 255 | outcomes | The value of `threshold.M1.condition_number` is 30 . | 30 | ratio | threshold |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 256 | outcomes | The value of `threshold.M1.vif` is 10 . | 10 | ratio | threshold |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 257 | outcomes | The value of `threshold.O1.auc_gap` is 0.08 . | 0.08 | ratio | threshold |  | eq | `[[art:630f28f4:threshold.O1.auc_gap]]` | verified | 0.08 |
| 258 | outcomes | The value of `threshold.O1.holdout_gap` is 0.05 . | 0.05 | ratio | threshold |  | eq | `[[art:90f8b6d9:threshold.O1.holdout_gap]]` | verified | 0.05 |
| 259 | outcomes | The value of `threshold.R1.auc_gap` is 0.1 . | 0.1 | ratio | threshold |  | eq | `[[art:b64213d7:threshold.R1.auc_gap]]` | verified | 0.1 |
| 260 | outcomes | The value of `threshold.R1.sign_flip_coef` is 0.05 . | 0.05 | ratio | threshold |  | eq | `[[art:aca84377:threshold.R1.sign_flip_coef]]` | verified | 0.05 |
| 261 | outcomes | The value of `threshold.R1.sign_flip_z` is 2 . | 2 | ratio | threshold |  | eq | `[[art:2e4428c7:threshold.R1.sign_flip_z]]` | verified | 2 |
| 262 | outcomes | The value of `threshold.S1.psi` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 263 | outcomes | The value of `threshold.package.auc.test.min` is 0.65 . | 0.65 | ratio | threshold |  | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 264 | outcomes | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 265 | sensitivity | The value of `condition_number` is 4.954 . | 4.954 | ratio | condition_number |  | eq | `[[art:d0edbe6f:condition_number]]` | verified | 4.953837779 |
| 266 | sensitivity | The value of `scenario.convexity` is 140.7 . | 140.7 | ratio | scenario |  | eq | `[[art:4451c907:scenario.convexity]]` | verified | 140.7189167 |
| 267 | sensitivity | The value of `scenario.value_change.-100` is -57.15 . | -57.15 | ratio | scenario |  | eq | `[[art:0445ffec:scenario.value_change.-100]]` | verified | -57.14884469 |
| 268 | sensitivity | The value of `scenario.value_change.-200` is -83.78 . | -83.78 | ratio | scenario |  | eq | `[[art:75d82514:scenario.value_change.-200]]` | verified | -83.77616324 |
| 269 | sensitivity | The value of `scenario.value_change.-300` is -92.11 . | -92.11 | ratio | scenario |  | eq | `[[art:0f83fead:scenario.value_change.-300]]` | verified | -92.10987115 |
| 270 | sensitivity | The value of `scenario.value_change.0` is 0 . | 0 | ratio | scenario |  | eq | `[[art:1e1b0b88:scenario.value_change.0]]` | verified | 0 |
| 271 | sensitivity | The value of `scenario.value_change.100` is 77.18 . | 77.18 | ratio | scenario |  | eq | `[[art:d16cc2a1:scenario.value_change.100]]` | verified | 77.1836951 |
| 272 | sensitivity | The value of `scenario.value_change.200` is 155.8 . | 155.8 | ratio | scenario |  | eq | `[[art:4871ddee:scenario.value_change.200]]` | verified | 155.7824864 |
| 273 | sensitivity | The value of `scenario.value_change.300` is 232.8 . | 232.8 | ratio | scenario |  | eq | `[[art:a0678af4:scenario.value_change.300]]` | verified | 232.8287879 |
| 274 | sensitivity | The value of `stability.bom_balance_log.sign_flip` is 0 . | 0 | ratio | stability |  | eq | `[[art:a9b4364d:stability.bom_balance_log.sign_flip]]` | verified | 0 |
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
| 290 | sensitivity | The value of `vif.bom_balance_log` is 1.143 . | 1.143 | ratio | vif |  | eq | `[[art:0b30efbf:vif.bom_balance_log]]` | verified | 1.142939813 |
| 291 | sensitivity | The value of `vif.burnout` is 3.44 . | 3.44 | ratio | vif |  | eq | `[[art:91e7ce55:vif.burnout]]` | verified | 3.439982425 |
| 292 | sensitivity | The value of `vif.credit_score` is 1.009 . | 1.009 | ratio | vif |  | eq | `[[art:b8652149:vif.credit_score]]` | verified | 1.009199828 |
| 293 | sensitivity | The value of `vif.incentive` is 2.234 . | 2.234 | ratio | vif |  | eq | `[[art:d924a341:vif.incentive]]` | verified | 2.234058893 |
| 294 | sensitivity | The value of `vif.loan_age` is 2.93 . | 2.93 | ratio | vif |  | eq | `[[art:43980218:vif.loan_age]]` | verified | 2.930049511 |
| 295 | sensitivity | The value of `vif.max` is 4.978 . | 4.978 | ratio | vif |  | eq | `[[art:b1d416c0:vif.max]]` | verified | 4.977599595 |
| 296 | sensitivity | The value of `vif.note_rate` is 4.978 . | 4.978 | ratio | vif |  | eq | `[[art:71e8f3f6:vif.note_rate]]` | verified | 4.977599595 |
| 297 | sensitivity | The value of `vif.orig_ltv` is 1.005 . | 1.005 | ratio | vif |  | eq | `[[art:10f2f018:vif.orig_ltv]]` | verified | 1.004907818 |
| 298 | sensitivity | The value of `vif.orig_upb_log` is 1.134 . | 1.134 | ratio | vif |  | eq | `[[art:347761f6:vif.orig_upb_log]]` | verified | 1.134478986 |
| 299 | sensitivity | The value of `vif.sato` is 1.713 . | 1.713 | ratio | vif |  | eq | `[[art:08e0ca20:vif.sato]]` | verified | 1.712581428 |
| 300 | sensitivity | The value of `vif.season_cos` is 1.018 . | 1.018 | ratio | vif |  | eq | `[[art:a2dc57c7:vif.season_cos]]` | verified | 1.01775523 |
| 301 | sensitivity | The value of `vif.season_sin` is 1.004 . | 1.004 | ratio | vif |  | eq | `[[art:5069e43c:vif.season_sin]]` | verified | 1.004179036 |
| 302 | findings | The value of `leakage.target_corr.max_single_feature_auc` is… | 1 | ratio | leakage |  | eq | `[[art:7f74c0d5:leakage.target_corr.max_single_feature_auc]]` | verified | 1 |
| 303 | findings | The value of `leakage.timing.n_flagged` is 0 . | 0 | ratio | leakage |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 304 | findings | The value of `scenario.convexity` is 140.7 . | 140.7 | ratio | scenario |  | eq | `[[art:4451c907:scenario.convexity]]` | verified | 140.7189167 |
| 305 | findings | The value of `scenario.value_change.-300` is -92.11 . | -92.11 | ratio | scenario |  | eq | `[[art:0f83fead:scenario.value_change.-300]]` | verified | -92.10987115 |
| 306 | findings | The value of `scenario.value_change.300` is 232.8 . | 232.8 | ratio | scenario |  | eq | `[[art:a0678af4:scenario.value_change.300]]` | verified | 232.8287879 |
| 307 | findings | The value of `sign_check.burnout.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:56826e40:sign_check.burnout.agrees]]` | verified | 0 |
| 308 | findings | The value of `sign_check.burnout.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:dcfb2de4:sign_check.burnout.coef_sign]]` | verified | -1 |
| 309 | findings | The value of `sign_check.burnout.univariate_direction` is 1… | 1 | ratio | sign_check |  | eq | `[[art:bfc96bb2:sign_check.burnout.univariate_direction]]` | verified | 1 |
| 310 | findings | The value of `sign_check.season_sin.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:74f2d0e0:sign_check.season_sin.agrees]]` | verified | 0 |
| 311 | findings | The value of `sign_check.season_sin.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:92ed5b5f:sign_check.season_sin.coef_sign]]` | verified | -1 |
| 312 | findings | The value of `sign_check.season_sin.univariate_direction` is… | 1 | ratio | sign_check |  | eq | `[[art:cae6b096:sign_check.season_sin.univariate_direction]]` | verified | 1 |
| 313 | findings | The value of `threshold.L1.single_feature_auc` is 0.9 . | 0.9 | ratio | threshold |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 314 | monitoring | The value of `metrics.test.auc` is 1 . | 1 | ratio | metrics |  | eq | `[[art:4619bd69:metrics.test.auc]]` | verified | 1 |
| 315 | monitoring | The value of `psi.max` is 0.06189 . | 0.06189 | ratio | psi |  | eq | `[[art:c2e8c8fd:psi.max]]` | verified | 0.06188985797 |
| 316 | monitoring | The value of `rule.calibration_first_event_rate` is 0.05 . | 0.05 | ratio | rule |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 317 | monitoring | The value of `threshold.package.auc.test.min` is 0.65 . | 0.65 | ratio | threshold |  | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 318 | monitoring | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |

## Appendix B — Artifact index

The store holds 277 artifacts; the 219 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `ablation.baseline_auc` | `7610ff35` | scalar | 1 | AUC on test of a refit of the champion's functional form on every retained feature, the level each ablation delta is measured from |
| `ablation.bom_balance_log.delta_auc` | `c226f60f` | scalar | -0.2327007725 | change in test AUC when the champion's form is refitted without bom_balance_log |
| `ablation.burnout.delta_auc` | `d50de877` | scalar | 0 | change in test AUC when the champion's form is refitted without burnout |
| `ablation.credit_score.delta_auc` | `d1dff006` | scalar | 0 | change in test AUC when the champion's form is refitted without credit_score |
| `ablation.incentive.delta_auc` | `33a25e3c` | scalar | 0 | change in test AUC when the champion's form is refitted without incentive |
| `ablation.loan_age.delta_auc` | `1a789b08` | scalar | 0 | change in test AUC when the champion's form is refitted without loan_age |
| `ablation.note_rate.delta_auc` | `65b3f07a` | scalar | 0 | change in test AUC when the champion's form is refitted without note_rate |
| `ablation.orig_ltv.delta_auc` | `370eaea8` | scalar | 0 | change in test AUC when the champion's form is refitted without orig_ltv |
| `ablation.orig_upb_log.delta_auc` | `e245ef14` | scalar | 0 | change in test AUC when the champion's form is refitted without orig_upb_log |
| `ablation.sato.delta_auc` | `2bbb0015` | scalar | 0 | change in test AUC when the champion's form is refitted without sato |
| `ablation.season_cos.delta_auc` | `9453331c` | scalar | 0 | change in test AUC when the champion's form is refitted without season_cos |
| `ablation.season_sin.delta_auc` | `a4f7b0c1` | scalar | 0 | change in test AUC when the champion's form is refitted without season_sin |
| `calibration.mean_rel_gap.out_of_time` | `68619260` | scalar | 0.003912925468 | mean predicted against observed on out_of_time, relative |
| `calibration.mean_rel_gap.test` | `4e1854b1` | scalar | 0.01025910486 | mean predicted against observed on test, relative |
| `calibration.mean_rel_gap.train` | `db1bca38` | scalar | 0.009653750145 | mean predicted against observed on train, relative |
| `calibration.mean_rel_gap.vintage_holdout` | `1438e44d` | scalar | 0.01696028022 | mean predicted against observed on vintage_holdout, relative |
| `calibration.separable.out_of_time` | `258b7972` | scalar | 1 | the predictions on out_of_time separate the outcome, so the calibration slope has no finite maximum likelihood estimate and was not computed |
| `calibration.separable.test` | `81c3fa7a` | scalar | 1 | the predictions on test separate the outcome, so the calibration slope has no finite maximum likelihood estimate and was not computed |
| `calibration.separable.train` | `d7ee2241` | scalar | 1 | the predictions on train separate the outcome, so the calibration slope has no finite maximum likelihood estimate and was not computed |
| `calibration.separable.vintage_holdout` | `137e2c39` | scalar | 1 | the predictions on vintage_holdout separate the outcome, so the calibration slope has no finite maximum likelihood estimate and was not computed |
| `calibration.test` | `a3f4f35f` | table | table, 10 rows | calibration by decile of predicted probability on test |
| `challenger.auc` | `5aeaf534` | scalar | 1 | the challenger's AUC on test |
| `challenger.brier` | `0b5236ca` | scalar | 3.226460021e-13 | the challenger's Brier score on test |
| `challenger.delta_auc` | `d8eca8f5` | scalar | 0 | the challenger's AUC on test minus the champion's |
| `condition_number` | `d0edbe6f` | scalar | 4.953837779 | Belsley's condition number of the column-standardised design |
| `cpr.out_of_time.mae` | `bdc9d54f` | scalar | 0.0007117577187 | mean absolute difference between actual and predicted CPR on out_of_time |
| `cpr.test` | `0aa376c9` | table | table, 71 rows | actual against predicted CPR by period on test |
| `cpr.test.mae` | `be219b85` | scalar | 0.0009292114418 | mean absolute difference between actual and predicted CPR on test |
| `cpr.train.mae` | `99b2b87f` | scalar | 0.0009279500644 | mean absolute difference between actual and predicted CPR on train |
| `cpr.vintage_holdout.mae` | `d1a19e91` | scalar | 0.0009298655279 | mean absolute difference between actual and predicted CPR on vintage_holdout |
| `csi.bom_balance_log` | `60a10892` | scalar | 0.03214820108 | CSI of bom_balance_log: its contribution to the shift in the linear predictor |
| `csi.burnout` | `a5da1daa` | scalar | 0.0001015529196 | CSI of burnout: its contribution to the shift in the linear predictor |
| `csi.credit_score` | `d87a2d40` | scalar | 0.000223048204 | CSI of credit_score: its contribution to the shift in the linear predictor |
| `csi.incentive` | `41325258` | scalar | 9.278494663e-05 | CSI of incentive: its contribution to the shift in the linear predictor |
| `csi.loan_age` | `df52c920` | scalar | 0 | CSI of loan_age: its contribution to the shift in the linear predictor |
| `csi.max` | `b2440ca1` | scalar | 0.03214820108 | the largest characteristic stability index |
| `csi.note_rate` | `587b33e9` | scalar | 0.0003806385501 | CSI of note_rate: its contribution to the shift in the linear predictor |
| `csi.orig_ltv` | `7ea837e1` | scalar | 0.0008996218814 | CSI of orig_ltv: its contribution to the shift in the linear predictor |
| `csi.orig_upb_log` | `5d1c16f2` | scalar | 0.004635722963 | CSI of orig_upb_log: its contribution to the shift in the linear predictor |
| `csi.sato` | `fb71eb9e` | scalar | 0.0004490205147 | CSI of sato: its contribution to the shift in the linear predictor |
| `csi.season_cos` | `de66f2c6` | scalar | 1.934566399e-05 | CSI of season_cos: its contribution to the shift in the linear predictor |
| `csi.season_sin` | `4c3f0dd9` | scalar | 1.386212619e-06 | CSI of season_sin: its contribution to the shift in the linear predictor |
| `deciles.out_of_time.top2_capture` | `d3114d7a` | scalar | 1 | share of out_of_time events in the top two deciles |
| `deciles.test` | `a859c712` | table | table, 10 rows | decile separation on test; decile 1 holds the highest probabilities |
| `deciles.test.top2_capture` | `466bfdc8` | scalar | 1 | share of test events in the top two deciles |
| `deciles.train.top2_capture` | `194d1fbd` | scalar | 1 | share of train events in the top two deciles |
| `deciles.vintage_holdout.top2_capture` | `db275674` | scalar | 1 | share of vintage_holdout events in the top two deciles |
| `leakage.duplicates.train` | `4474c227` | scalar | 0 | share of train rows whose feature values are not unique within train |
| `leakage.name_screen.n_matched` | `407e62be` | scalar | 0 | feature names matching the target-adjacent lexicon |
| `leakage.overlap` | `4c9fcd09` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.features` | `0fec8048` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.ids` | `63d37fc5` | scalar | 0 | share of test rows whose ['loan_id', 'period'] also identify a row of train |
| `leakage.target_corr` | `ce82a409` | table | table, 11 rows | each feature against the outcome on train, on its own |
| `leakage.target_corr.max_single_feature_auc` | `7f74c0d5` | scalar | 1 | the AUC of the strongest single feature |
| `leakage.timing` | `8cdad1c5` | table | table, 12 rows | each feature's declared timing; flagged means during or after the outcome |
| `leakage.timing.n_flagged` | `742bcd24` | scalar | 0 | features declared during_period or after_outcome |
| `metrics.out_of_time.auc` | `bcb747a3` | scalar | 1 | auc on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.brier` | `44f11124` | scalar | 1.375799568e-08 | brier on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.event_rate` | `83ccf5c0` | scalar | 0.01794892714 | event_rate on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.gini` | `6d939d01` | scalar | 1 | gini on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.ks` | `e3aa3687` | scalar | 1 | ks on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.logloss` | `4ff30655` | scalar | 9.056637435e-05 | logloss on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.mean_predicted` | `276f106a` | scalar | 0.01801915996 | mean_predicted on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.n` | `7898809e` | scalar | 12257 | n on out_of_time, recomputed by quaestor |
| `metrics.test.auc` | `4619bd69` | scalar | 1 | auc on test, recomputed by quaestor |
| `metrics.test.brier` | `67fd4fea` | scalar | 1.01061577e-08 | brier on test, recomputed by quaestor |
| `metrics.test.event_rate` | `570cc08a` | scalar | 0.008061370433 | event_rate on test, recomputed by quaestor |
| `metrics.test.gini` | `35acd744` | scalar | 1 | gini on test, recomputed by quaestor |
| `metrics.test.ks` | `a13846c8` | scalar | 1 | ks on test, recomputed by quaestor |
| `metrics.test.logloss` | `db4e6b76` | scalar | 9.04295748e-05 | logloss on test, recomputed by quaestor |
| `metrics.test.mean_predicted` | `83863be2` | scalar | 0.008144072878 | mean_predicted on test, recomputed by quaestor |
| `metrics.test.n` | `e55953e1` | scalar | 15382 | n on test, recomputed by quaestor |
| `metrics.train.auc` | `6269694d` | scalar | 1 | auc on train, recomputed by quaestor |
| `metrics.train.brier` | `0c2c4489` | scalar | 1.095784085e-08 | brier on train, recomputed by quaestor |
| `metrics.train.event_rate` | `b9ef3327` | scalar | 0.008524699414 | event_rate on train, recomputed by quaestor |
| `metrics.train.gini` | `e2084e07` | scalar | 1 | gini on train, recomputed by quaestor |
| `metrics.train.ks` | `24c2277d` | scalar | 1 | ks on train, recomputed by quaestor |
| `metrics.train.logloss` | `1761d10c` | scalar | 9.128014231e-05 | logloss on train, recomputed by quaestor |
| `metrics.train.mean_predicted` | `6f9330ed` | scalar | 0.008606994732 | mean_predicted on train, recomputed by quaestor |
| `metrics.train.n` | `6fdfeabb` | scalar | 36013 | n on train, recomputed by quaestor |
| `metrics.vintage_holdout.auc` | `00749c11` | scalar | 1 | auc on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.brier` | `c58e369c` | scalar | 8.645548253e-09 | brier on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.event_rate` | `e3590a16` | scalar | 0.004817105386 | event_rate on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.gini` | `f4aa377a` | scalar | 1 | gini on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.ks` | `cb4509f6` | scalar | 1 | ks on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.logloss` | `85bdc089` | scalar | 8.629383814e-05 | logloss on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.mean_predicted` | `af925790` | scalar | 0.004898804843 | mean_predicted on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.n` | `37a92951` | scalar | 32177 | n on vintage_holdout, recomputed by quaestor |
| `profile.out_of_time.missing.max` | `4dafce11` | scalar | 0 | the largest missing fraction in out_of_time |
| `profile.out_of_time.n` | `fa39c5cf` | scalar | 12257 | rows in out_of_time |
| `profile.test.missing.max` | `f813848d` | scalar | 0 | the largest missing fraction in test |
| `profile.test.n` | `e3abc1b8` | scalar | 15382 | rows in test |
| `profile.train.missing.max` | `050a3099` | scalar | 0 | the largest missing fraction in train |
| `profile.train.n` | `c5ebd9c9` | scalar | 36013 | rows in train |
| `profile.vintage_holdout.missing.max` | `329bb430` | scalar | 0 | the largest missing fraction in vintage_holdout |
| `profile.vintage_holdout.n` | `426e712a` | scalar | 32177 | rows in vintage_holdout |
| `psi.bom_balance_log` | `ce3c425c` | scalar | 0.03017956995 | PSI of bom_balance_log between train and test |
| `psi.burnout` | `9dc7ecc2` | scalar | 0.004614338236 | PSI of burnout between train and test |
| `psi.credit_score` | `7e87527c` | scalar | 0.06188985797 | PSI of credit_score between train and test |
| `psi.incentive` | `2da5570f` | scalar | 0.0009922551416 | PSI of incentive between train and test |
| `psi.loan_age` | `2202b157` | scalar | 0.0001993816816 | PSI of loan_age between train and test |
| `psi.max` | `c2e8c8fd` | scalar | 0.06188985797 | the largest train-to-test PSI, score included |
| `psi.note_rate` | `ecc6adf3` | scalar | 0.01370911382 | PSI of note_rate between train and test |
| `psi.orig_ltv` | `cd1ff136` | scalar | 0.03617297258 | PSI of orig_ltv between train and test |
| `psi.orig_upb_log` | `55030a3b` | scalar | 0.04817081196 | PSI of orig_upb_log between train and test |
| `psi.out_of_time.bom_balance_log` | `9fa682d1` | scalar | 0.08707630682 | PSI of bom_balance_log between train and out_of_time |
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
| `psi.out_of_time.y_score` | `12620838` | scalar | 0.1450932669 | PSI of the score between train and out_of_time |
| `psi.sato` | `584da64f` | scalar | 0.02772829856 | PSI of sato between train and test |
| `psi.season_cos` | `addec503` | scalar | 1.790085913e-05 | PSI of season_cos between train and test |
| `psi.season_sin` | `4d2ed98d` | scalar | 2.939045338e-06 | PSI of season_sin between train and test |
| `psi.vintage_holdout.bom_balance_log` | `b3073b46` | scalar | 0.03706738664 | PSI of bom_balance_log between train and vintage_holdout |
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
| `psi.vintage_holdout.y_score` | `33ffbed6` | scalar | 0.05813498782 | PSI of the score between train and vintage_holdout |
| `psi.y_score` | `2ad82680` | scalar | 0.01873789359 | PSI of the score between train and test |
| `rule.calibration_first_event_rate` | `42f1351e` | scalar | 0.05 | the event rate below which the report puts calibration before discrimination |
| `run.projection` | `7d3ba32d` | json | json | the subject's projection.json |
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |
| `scenario.convexity` | `4451c907` | scalar | 140.7189167 | the value change at -300 bp plus the change at 300 bp; negative when the fall outweighs the rise |
| `scenario.value_by_shock` | `c4d5cb25` | table | table, 7 rows | servicing value, its change from the base case and first-year CPR, by shock |
| `scenario.value_change.-100` | `0445ffec` | scalar | -57.14884469 | change in servicing value at -100 bp |
| `scenario.value_change.-200` | `75d82514` | scalar | -83.77616324 | change in servicing value at -200 bp |
| `scenario.value_change.-300` | `0f83fead` | scalar | -92.10987115 | change in servicing value at -300 bp |
| `scenario.value_change.0` | `1e1b0b88` | scalar | 0 | change in servicing value at 0 bp |
| `scenario.value_change.100` | `d16cc2a1` | scalar | 77.1836951 | change in servicing value at 100 bp |
| `scenario.value_change.200` | `4871ddee` | scalar | 155.7824864 | change in servicing value at 200 bp |
| `scenario.value_change.300` | `a0678af4` | scalar | 232.8287879 | change in servicing value at 300 bp |
| `sign_check.bom_balance_log.agrees` | `26b1789b` | scalar | 1 | 1 when the fitted sign on bom_balance_log agrees with its univariate direction, 0 when it does not |
| `sign_check.bom_balance_log.coef_sign` | `d2e88db3` | scalar | -1 | the sign of the fitted coefficient on bom_balance_log |
| `sign_check.bom_balance_log.univariate_direction` | `8ee4f8fe` | scalar | -1 | the sign of bom_balance_log's own single-feature AUC on train minus 0.5 |
| `sign_check.burnout.agrees` | `56826e40` | scalar | 0 | 1 when the fitted sign on burnout agrees with its univariate direction, 0 when it does not |
| `sign_check.burnout.coef_sign` | `dcfb2de4` | scalar | -1 | the sign of the fitted coefficient on burnout |
| `sign_check.burnout.univariate_direction` | `bfc96bb2` | scalar | 1 | the sign of burnout's own single-feature AUC on train minus 0.5 |
| `sign_check.credit_score.agrees` | `915bf8eb` | scalar | 1 | 1 when the fitted sign on credit_score agrees with its univariate direction, 0 when it does not |
| `sign_check.credit_score.coef_sign` | `1ec1078b` | scalar | 1 | the sign of the fitted coefficient on credit_score |
| `sign_check.credit_score.univariate_direction` | `42303896` | scalar | 1 | the sign of credit_score's own single-feature AUC on train minus 0.5 |
| `sign_check.incentive.agrees` | `f7b2338e` | scalar | 1 | 1 when the fitted sign on incentive agrees with its univariate direction, 0 when it does not |
| `sign_check.incentive.coef_sign` | `684cf11a` | scalar | 1 | the sign of the fitted coefficient on incentive |
| `sign_check.incentive.univariate_direction` | `8098d951` | scalar | 1 | the sign of incentive's own single-feature AUC on train minus 0.5 |
| `sign_check.n_disagreements` | `66ce738a` | scalar | 2 | retained features whose fitted sign contradicts their univariate direction, of 10 checked |
| `sign_check.note_rate.agrees` | `ca18290e` | scalar | 1 | 1 when the fitted sign on note_rate agrees with its univariate direction, 0 when it does not |
| `sign_check.note_rate.coef_sign` | `0e3296a5` | scalar | 1 | the sign of the fitted coefficient on note_rate |
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
| `sign_check.season_sin.agrees` | `74f2d0e0` | scalar | 0 | 1 when the fitted sign on season_sin agrees with its univariate direction, 0 when it does not |
| `sign_check.season_sin.coef_sign` | `92ed5b5f` | scalar | -1 | the sign of the fitted coefficient on season_sin |
| `sign_check.season_sin.univariate_direction` | `cae6b096` | scalar | 1 | the sign of season_sin's own single-feature AUC on train minus 0.5 |
| `stability.auc_by_regime` | `9edbf2d0` | table | table, 2 rows | the champion's AUC within each rate_regime on train |
| `stability.bom_balance_log.sign_flip` | `a9b4364d` | scalar | 0 | 1 when bom_balance_log is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
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
| `threshold.package.psi.max` | `fbb5a9d1` | scalar | 0.25 | package.yaml declares psi max 0.25 |
| `thresholds.evaluation` | `25af6e79` | table | table, 4 rows | every threshold package.yaml declares, with its bound, the recomputed value and the outcome |
| `vif.bom_balance_log` | `0b30efbf` | scalar | 1.142939813 | variance inflation factor of bom_balance_log on train |
| `vif.burnout` | `91e7ce55` | scalar | 3.439982425 | variance inflation factor of burnout on train |
| `vif.credit_score` | `b8652149` | scalar | 1.009199828 | variance inflation factor of credit_score on train |
| `vif.incentive` | `d924a341` | scalar | 2.234058893 | variance inflation factor of incentive on train |
| `vif.loan_age` | `43980218` | scalar | 2.930049511 | variance inflation factor of loan_age on train |
| `vif.max` | `b1d416c0` | scalar | 4.977599595 | the largest variance inflation factor |
| `vif.note_rate` | `71e8f3f6` | scalar | 4.977599595 | variance inflation factor of note_rate on train |
| `vif.orig_ltv` | `10f2f018` | scalar | 1.004907818 | variance inflation factor of orig_ltv on train |
| `vif.orig_upb_log` | `347761f6` | scalar | 1.134478986 | variance inflation factor of orig_upb_log on train |
| `vif.sato` | `08e0ca20` | scalar | 1.712581428 | variance inflation factor of sato on train |
| `vif.season_cos` | `a2dc57c7` | scalar | 1.01775523 | variance inflation factor of season_cos on train |
| `vif.season_sin` | `5069e43c` | scalar | 1.004179036 | variance inflation factor of season_sin on train |

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
| wall-clock (s) | 1.91 |
| subject run (s) | 2.48 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | fake |
| model | none: no model answered |
| run id | msr_prepayment-rules_only-20260918T065342Z-568d25f5 |

## Appendix D — Not checked

| item | reason |
|---|---|
| developer claims (T1, claim channel) | The package declares 3 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
| drafted narrative and the repair loop | `rules_only` calls no model; the narrative is a template |
