---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: msr_prepayment
version: "1.0"
model_type: discrete_time_hazard
configuration: rules_only
model: fake
run_id: msr_prepayment-rules_only-20260918T065309Z-568d25f5
data_mode: synthetic
synthetic_n: 2000
grounding_precision_pre: 1.0000
grounding_precision_post: 1.0000
n_claims: 311
n_findings_by_severity: {high: 0, medium: 0, low: 0, info: 0}
generated: "2026-09-18T06:53:09Z"
illustrative: false
---

# Validation report — `msr_prepayment` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `msr_prepayment` v1.0 | `rules_only` | fake | synthetic, n = 2000 | 1.0000 → 1.0000 | 0 / 0 / 0 / 0 |
<!-- quaestor:renderer:end -->

This section follows the model risk management guidance at [[reg:SR26-2:V.1.b]].
The value of `calibration_slope.out_of_time` is 0.9969 [[art:a49b2789:calibration_slope.out_of_time]].
The value of `calibration_slope.test` is 0.9365 [[art:3e42ee62:calibration_slope.test]].
The value of `calibration_slope.train` is 0.9937 [[art:534cb102:calibration_slope.train]].
The value of `calibration_slope.vintage_holdout` is 0.8373 [[art:08d6b321:calibration_slope.vintage_holdout]].
The value of `challenger.delta_auc` is -0.07528 [[art:89de5f90:challenger.delta_auc]].
The value of `condition_number` is 4.943 [[art:4f06a3c5:condition_number]].
The value of `csi.max` is 0.03438 [[art:54bd75b0:csi.max]].
The value of `metrics.out_of_time.auc` is 0.7846 [[art:6f2a2d99:metrics.out_of_time.auc]].
The value of `metrics.out_of_time.brier` is 0.01713 [[art:40d244d4:metrics.out_of_time.brier]].
The value of `metrics.out_of_time.event_rate` is 0.01795 [[art:83ccf5c0:metrics.out_of_time.event_rate]].
The value of `metrics.out_of_time.gini` is 0.5691 [[art:890252d7:metrics.out_of_time.gini]].
The value of `metrics.out_of_time.ks` is 0.4321 [[art:16d3e4fe:metrics.out_of_time.ks]].
The value of `metrics.out_of_time.logloss` is 0.07975 [[art:2b7c9b2d:metrics.out_of_time.logloss]].
The value of `metrics.out_of_time.mean_predicted` is 0.01887 [[art:3833e0c5:metrics.out_of_time.mean_predicted]].
The value of `metrics.out_of_time.n` is 12257 [[art:7898809e:metrics.out_of_time.n]].
The value of `metrics.test.auc` is 0.7753 [[art:57066271:metrics.test.auc]].
The value of `metrics.test.brier` is 0.007894 [[art:7d3583cd:metrics.test.brier]].
The value of `metrics.test.event_rate` is 0.008061 [[art:570cc08a:metrics.test.event_rate]].
The value of `metrics.test.gini` is 0.5505 [[art:fe7f75d7:metrics.test.gini]].
The value of `metrics.test.ks` is 0.4162 [[art:c569c301:metrics.test.ks]].
The value of `metrics.test.logloss` is 0.04263 [[art:320e4c6b:metrics.test.logloss]].
The value of `metrics.test.mean_predicted` is 0.008116 [[art:3bc93911:metrics.test.mean_predicted]].
The value of `metrics.test.n` is 15382 [[art:e55953e1:metrics.test.n]].
The value of `metrics.train.auc` is 0.7883 [[art:fa609ae1:metrics.train.auc]].
The value of `metrics.train.brier` is 0.008317 [[art:83666c70:metrics.train.brier]].
The value of `metrics.train.event_rate` is 0.008525 [[art:b9ef3327:metrics.train.event_rate]].
The value of `metrics.train.gini` is 0.5767 [[art:0b6b2058:metrics.train.gini]].
The value of `metrics.train.ks` is 0.4562 [[art:c355478b:metrics.train.ks]].
The value of `metrics.train.logloss` is 0.04408 [[art:199c7db5:metrics.train.logloss]].
The value of `metrics.train.mean_predicted` is 0.008427 [[art:a63f6555:metrics.train.mean_predicted]].
The value of `metrics.train.n` is 36013 [[art:6fdfeabb:metrics.train.n]].
The value of `metrics.vintage_holdout.auc` is 0.7718 [[art:ac6794c5:metrics.vintage_holdout.auc]].
The value of `metrics.vintage_holdout.brier` is 0.004763 [[art:f3c6bdcc:metrics.vintage_holdout.brier]].
The value of `metrics.vintage_holdout.event_rate` is 0.004817 [[art:e3590a16:metrics.vintage_holdout.event_rate]].
The value of `metrics.vintage_holdout.gini` is 0.5436 [[art:a4a532f0:metrics.vintage_holdout.gini]].
The value of `metrics.vintage_holdout.ks` is 0.4516 [[art:b5b9e888:metrics.vintage_holdout.ks]].
The value of `metrics.vintage_holdout.logloss` is 0.02811 [[art:c32e3713:metrics.vintage_holdout.logloss]].
The value of `metrics.vintage_holdout.mean_predicted` is 0.005647 [[art:5ae28866:metrics.vintage_holdout.mean_predicted]].
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
The value of `ablation.f_burnout.delta_auc` is -0.0001876 [[art:4c92a645:ablation.f_burnout.delta_auc]].
The value of `ablation.f_credit_score.delta_auc` is -0.01474 [[art:302cee1d:ablation.f_credit_score.delta_auc]].
The value of `ablation.f_incentive.delta_auc` is -0.04117 [[art:cc8b34d4:ablation.f_incentive.delta_auc]].
The value of `ablation.f_loan_age.delta_auc` is 0.0008166 [[art:cd3be5c5:ablation.f_loan_age.delta_auc]].
The value of `ablation.f_note_rate.delta_auc` is -0.002585 [[art:034cea8e:ablation.f_note_rate.delta_auc]].
The value of `ablation.f_orig_ltv.delta_auc` is -0.002294 [[art:45bbe28a:ablation.f_orig_ltv.delta_auc]].
The value of `ablation.f_orig_upb_log.delta_auc` is -0.01927 [[art:dbd54a4a:ablation.f_orig_upb_log.delta_auc]].
The value of `ablation.f_sato.delta_auc` is 0.0005201 [[art:452f8833:ablation.f_sato.delta_auc]].
The value of `ablation.f_season_cos.delta_auc` is -0.0004826 [[art:f01715f5:ablation.f_season_cos.delta_auc]].
The value of `ablation.f_season_sin.delta_auc` is -0.0003885 [[art:a81a1fce:ablation.f_season_sin.delta_auc]].
The value of `challenger.auc` is 0.7 [[art:a55c39c9:challenger.auc]].
The value of `challenger.brier` is 0.008371 [[art:57c3e2f5:challenger.brier]].
The value of `challenger.delta_auc` is -0.07528 [[art:89de5f90:challenger.delta_auc]].
The value of `metrics.test.auc` is 0.7753 [[art:57066271:metrics.test.auc]].
The value of `metrics.test.brier` is 0.007894 [[art:7d3583cd:metrics.test.brier]].
The value of `sign_check.f_burnout.agrees` is 1 [[art:a7b47126:sign_check.f_burnout.agrees]].
The value of `sign_check.f_burnout.coef_sign` is 1 [[art:434a2eb4:sign_check.f_burnout.coef_sign]].
The value of `sign_check.f_burnout.univariate_direction` is 1 [[art:6c04f9a3:sign_check.f_burnout.univariate_direction]].
The value of `sign_check.f_credit_score.agrees` is 1 [[art:6a693a4d:sign_check.f_credit_score.agrees]].
The value of `sign_check.f_credit_score.coef_sign` is 1 [[art:4893edbf:sign_check.f_credit_score.coef_sign]].
The value of `sign_check.f_credit_score.univariate_direction` is 1 [[art:5364f2d9:sign_check.f_credit_score.univariate_direction]].
The value of `sign_check.f_incentive.agrees` is 1 [[art:aab920d4:sign_check.f_incentive.agrees]].
The value of `sign_check.f_incentive.coef_sign` is 1 [[art:34fbc238:sign_check.f_incentive.coef_sign]].
The value of `sign_check.f_incentive.univariate_direction` is 1 [[art:284b2d7c:sign_check.f_incentive.univariate_direction]].
The value of `sign_check.f_note_rate.agrees` is 0 [[art:e3173464:sign_check.f_note_rate.agrees]].
The value of `sign_check.f_note_rate.coef_sign` is -1 [[art:9a57eeb9:sign_check.f_note_rate.coef_sign]].
The value of `sign_check.f_note_rate.univariate_direction` is 1 [[art:33e2a051:sign_check.f_note_rate.univariate_direction]].
The value of `sign_check.f_orig_ltv.agrees` is 1 [[art:56d6495e:sign_check.f_orig_ltv.agrees]].
The value of `sign_check.f_orig_ltv.coef_sign` is -1 [[art:eb67b95a:sign_check.f_orig_ltv.coef_sign]].
The value of `sign_check.f_orig_ltv.univariate_direction` is -1 [[art:1883c240:sign_check.f_orig_ltv.univariate_direction]].
The value of `sign_check.f_orig_upb_log.agrees` is 1 [[art:57b59c6a:sign_check.f_orig_upb_log.agrees]].
The value of `sign_check.f_orig_upb_log.coef_sign` is 1 [[art:5165217f:sign_check.f_orig_upb_log.coef_sign]].
The value of `sign_check.f_orig_upb_log.univariate_direction` is 1 [[art:901ddb38:sign_check.f_orig_upb_log.univariate_direction]].
The value of `sign_check.f_sato.agrees` is 1 [[art:44052838:sign_check.f_sato.agrees]].
The value of `sign_check.f_sato.coef_sign` is 1 [[art:55450fdb:sign_check.f_sato.coef_sign]].
The value of `sign_check.f_sato.univariate_direction` is 1 [[art:5cc2f196:sign_check.f_sato.univariate_direction]].
The value of `sign_check.f_season_cos.agrees` is 1 [[art:e02a4777:sign_check.f_season_cos.agrees]].
The value of `sign_check.f_season_cos.coef_sign` is -1 [[art:25dfa200:sign_check.f_season_cos.coef_sign]].
The value of `sign_check.f_season_cos.univariate_direction` is -1 [[art:7f6fd623:sign_check.f_season_cos.univariate_direction]].
The value of `sign_check.f_season_sin.agrees` is 1 [[art:caceebf9:sign_check.f_season_sin.agrees]].
The value of `sign_check.f_season_sin.coef_sign` is 1 [[art:a6b9d22d:sign_check.f_season_sin.coef_sign]].
The value of `sign_check.f_season_sin.univariate_direction` is 1 [[art:8a2dc987:sign_check.f_season_sin.univariate_direction]].
The value of `sign_check.n_disagreements` is 1 [[art:f96ece96:sign_check.n_disagreements]].
The value of `threshold.E1.delta_auc` is 0.03 [[art:e042774c:threshold.E1.delta_auc]].

## 3. Data integrity and drift

This section follows the model risk management guidance at [[reg:SR26-2:V.1.a]].
The value of `csi.f_burnout` is 0.0009851 [[art:94a1612f:csi.f_burnout]].
The value of `csi.f_credit_score` is 0.007909 [[art:70748e80:csi.f_credit_score]].
The value of `csi.f_incentive` is 0.005804 [[art:ac5ee43b:csi.f_incentive]].
The value of `csi.f_loan_age` is 0 [[art:53ae3ece:csi.f_loan_age]].
The value of `csi.f_note_rate` is 0.01822 [[art:06292416:csi.f_note_rate]].
The value of `csi.f_orig_ltv` is 0.03438 [[art:1f963d83:csi.f_orig_ltv]].
The value of `csi.f_orig_upb_log` is 0.002969 [[art:a10d20d5:csi.f_orig_upb_log]].
The value of `csi.f_sato` is 0.001487 [[art:ce21936e:csi.f_sato]].
The value of `csi.f_season_cos` is 0.0004785 [[art:15fe2d99:csi.f_season_cos]].
The value of `csi.f_season_sin` is 0.00007624 [[art:81e8dbf0:csi.f_season_sin]].
The value of `csi.max` is 0.03438 [[art:54bd75b0:csi.max]].
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
The value of `psi.f_burnout` is 0.004614 [[art:445ec3e0:psi.f_burnout]].
The value of `psi.f_credit_score` is 0.06189 [[art:5829d6ed:psi.f_credit_score]].
The value of `psi.f_incentive` is 0.0009923 [[art:8075e035:psi.f_incentive]].
The value of `psi.f_loan_age` is 0.0001994 [[art:6ec631ed:psi.f_loan_age]].
The value of `psi.f_note_rate` is 0.01371 [[art:63c68948:psi.f_note_rate]].
The value of `psi.f_orig_ltv` is 0.03617 [[art:212acb3a:psi.f_orig_ltv]].
The value of `psi.f_orig_upb_log` is 0.04817 [[art:75026ee2:psi.f_orig_upb_log]].
The value of `psi.f_sato` is 0.02773 [[art:2beb335c:psi.f_sato]].
The value of `psi.f_season_cos` is 0.0000179 [[art:cb2ce435:psi.f_season_cos]].
The value of `psi.f_season_sin` is 0.000002939 [[art:44d14048:psi.f_season_sin]].
The value of `psi.max` is 0.06189 [[art:c2e8c8fd:psi.max]].
The value of `psi.out_of_time.f_burnout` is 2.945 [[art:a696b6ff:psi.out_of_time.f_burnout]].
The value of `psi.out_of_time.f_credit_score` is 0.05988 [[art:e02f8367:psi.out_of_time.f_credit_score]].
The value of `psi.out_of_time.f_incentive` is 0.4958 [[art:58b6089b:psi.out_of_time.f_incentive]].
The value of `psi.out_of_time.f_loan_age` is 2.484 [[art:eec03fdd:psi.out_of_time.f_loan_age]].
The value of `psi.out_of_time.f_note_rate` is 0.6977 [[art:b0278c59:psi.out_of_time.f_note_rate]].
The value of `psi.out_of_time.f_orig_ltv` is 0.04301 [[art:3422cd60:psi.out_of_time.f_orig_ltv]].
The value of `psi.out_of_time.f_orig_upb_log` is 0.07136 [[art:fddf2a0a:psi.out_of_time.f_orig_upb_log]].
The value of `psi.out_of_time.f_sato` is 0.01299 [[art:5090c358:psi.out_of_time.f_sato]].
The value of `psi.out_of_time.f_season_cos` is 0.007524 [[art:3487f524:psi.out_of_time.f_season_cos]].
The value of `psi.out_of_time.f_season_sin` is 0.02789 [[art:eb28b9bb:psi.out_of_time.f_season_sin]].
The value of `psi.out_of_time.y_score` is 0.7056 [[art:2dc61374:psi.out_of_time.y_score]].
The value of `psi.vintage_holdout.f_burnout` is 0.04749 [[art:b76fb2b0:psi.vintage_holdout.f_burnout]].
The value of `psi.vintage_holdout.f_credit_score` is 0.03996 [[art:abf4e0aa:psi.vintage_holdout.f_credit_score]].
The value of `psi.vintage_holdout.f_incentive` is 0.4475 [[art:81260b55:psi.vintage_holdout.f_incentive]].
The value of `psi.vintage_holdout.f_loan_age` is 0.07112 [[art:256aaeda:psi.vintage_holdout.f_loan_age]].
The value of `psi.vintage_holdout.f_note_rate` is 0.6088 [[art:c1ffae38:psi.vintage_holdout.f_note_rate]].
The value of `psi.vintage_holdout.f_orig_ltv` is 0.02942 [[art:09f015f3:psi.vintage_holdout.f_orig_ltv]].
The value of `psi.vintage_holdout.f_orig_upb_log` is 0.0404 [[art:ce7dc6c5:psi.vintage_holdout.f_orig_upb_log]].
The value of `psi.vintage_holdout.f_sato` is 0.02989 [[art:17126bd4:psi.vintage_holdout.f_sato]].
The value of `psi.vintage_holdout.f_season_cos` is 0.001288 [[art:5123c902:psi.vintage_holdout.f_season_cos]].
The value of `psi.vintage_holdout.f_season_sin` is 0.0007309 [[art:403ec3c2:psi.vintage_holdout.f_season_sin]].
The value of `psi.vintage_holdout.y_score` is 0.1421 [[art:3713457e:psi.vintage_holdout.y_score]].
The value of `psi.y_score` is 0.001953 [[art:3b9dee2d:psi.y_score]].
The value of `threshold.D1.missing_gap` is 0.1 [[art:9cce25ea:threshold.D1.missing_gap]].
The value of `threshold.L1.single_feature_auc` is 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]].
The value of `threshold.L2.overlap` is 0.005 [[art:9f336eaf:threshold.L2.overlap]].
The value of `threshold.L2.overlap.features_effective` is 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].
The value of `threshold.S1.psi` is 0.25 [[art:278b9016:threshold.S1.psi]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].

## 4. Outcomes analysis

This section follows the model risk management guidance at [[reg:SR26-2:V.1.b]].
The value of `calibration.mean_rel_gap.out_of_time` is 0.05109 [[art:c599bd89:calibration.mean_rel_gap.out_of_time]].
The value of `calibration.mean_rel_gap.test` is 0.006755 [[art:d1b269ea:calibration.mean_rel_gap.test]].
The value of `calibration.mean_rel_gap.train` is 0.01152 [[art:e28c45a9:calibration.mean_rel_gap.train]].
The value of `calibration.mean_rel_gap.vintage_holdout` is 0.1722 [[art:55a672c2:calibration.mean_rel_gap.vintage_holdout]].
The value of `calibration_intercept.out_of_time` is -0.06272 [[art:fc7ece3a:calibration_intercept.out_of_time]].
The value of `calibration_intercept.test` is -0.277 [[art:e87b5c13:calibration_intercept.test]].
The value of `calibration_intercept.train` is -0.01454 [[art:11d7a3ca:calibration_intercept.train]].
The value of `calibration_intercept.vintage_holdout` is -0.9028 [[art:44715143:calibration_intercept.vintage_holdout]].
The value of `calibration_slope.out_of_time` is 0.9969 [[art:a49b2789:calibration_slope.out_of_time]].
The value of `calibration_slope.test` is 0.9365 [[art:3e42ee62:calibration_slope.test]].
The value of `calibration_slope.train` is 0.9937 [[art:534cb102:calibration_slope.train]].
The value of `calibration_slope.vintage_holdout` is 0.8373 [[art:08d6b321:calibration_slope.vintage_holdout]].
The value of `cpr.out_of_time.mae` is 0.05857 [[art:a7ecd72b:cpr.out_of_time.mae]].
The value of `cpr.test.mae` is 0.04264 [[art:ff266c97:cpr.test.mae]].
The value of `cpr.train.mae` is 0.02658 [[art:f2c3683c:cpr.train.mae]].
The value of `cpr.vintage_holdout.mae` is 0.0289 [[art:172ebed4:cpr.vintage_holdout.mae]].
The value of `deciles.out_of_time.top2_capture` is 0.5773 [[art:df63152b:deciles.out_of_time.top2_capture]].
The value of `deciles.test.top2_capture` is 0.5806 [[art:43c4adc5:deciles.test.top2_capture]].
The value of `deciles.train.top2_capture` is 0.5961 [[art:e8dd0c53:deciles.train.top2_capture]].
The value of `deciles.vintage_holdout.top2_capture` is 0.5871 [[art:8b59f312:deciles.vintage_holdout.top2_capture]].
The value of `metrics.out_of_time.auc` is 0.7846 [[art:6f2a2d99:metrics.out_of_time.auc]].
The value of `metrics.out_of_time.brier` is 0.01713 [[art:40d244d4:metrics.out_of_time.brier]].
The value of `metrics.out_of_time.event_rate` is 0.01795 [[art:83ccf5c0:metrics.out_of_time.event_rate]].
The value of `metrics.out_of_time.gini` is 0.5691 [[art:890252d7:metrics.out_of_time.gini]].
The value of `metrics.out_of_time.ks` is 0.4321 [[art:16d3e4fe:metrics.out_of_time.ks]].
The value of `metrics.out_of_time.logloss` is 0.07975 [[art:2b7c9b2d:metrics.out_of_time.logloss]].
The value of `metrics.out_of_time.mean_predicted` is 0.01887 [[art:3833e0c5:metrics.out_of_time.mean_predicted]].
The value of `metrics.out_of_time.n` is 12257 [[art:7898809e:metrics.out_of_time.n]].
The value of `metrics.test.auc` is 0.7753 [[art:57066271:metrics.test.auc]].
The value of `metrics.test.brier` is 0.007894 [[art:7d3583cd:metrics.test.brier]].
The value of `metrics.test.event_rate` is 0.008061 [[art:570cc08a:metrics.test.event_rate]].
The value of `metrics.test.gini` is 0.5505 [[art:fe7f75d7:metrics.test.gini]].
The value of `metrics.test.ks` is 0.4162 [[art:c569c301:metrics.test.ks]].
The value of `metrics.test.logloss` is 0.04263 [[art:320e4c6b:metrics.test.logloss]].
The value of `metrics.test.mean_predicted` is 0.008116 [[art:3bc93911:metrics.test.mean_predicted]].
The value of `metrics.test.n` is 15382 [[art:e55953e1:metrics.test.n]].
The value of `metrics.train.auc` is 0.7883 [[art:fa609ae1:metrics.train.auc]].
The value of `metrics.train.brier` is 0.008317 [[art:83666c70:metrics.train.brier]].
The value of `metrics.train.event_rate` is 0.008525 [[art:b9ef3327:metrics.train.event_rate]].
The value of `metrics.train.gini` is 0.5767 [[art:0b6b2058:metrics.train.gini]].
The value of `metrics.train.ks` is 0.4562 [[art:c355478b:metrics.train.ks]].
The value of `metrics.train.logloss` is 0.04408 [[art:199c7db5:metrics.train.logloss]].
The value of `metrics.train.mean_predicted` is 0.008427 [[art:a63f6555:metrics.train.mean_predicted]].
The value of `metrics.train.n` is 36013 [[art:6fdfeabb:metrics.train.n]].
The value of `metrics.vintage_holdout.auc` is 0.7718 [[art:ac6794c5:metrics.vintage_holdout.auc]].
The value of `metrics.vintage_holdout.brier` is 0.004763 [[art:f3c6bdcc:metrics.vintage_holdout.brier]].
The value of `metrics.vintage_holdout.event_rate` is 0.004817 [[art:e3590a16:metrics.vintage_holdout.event_rate]].
The value of `metrics.vintage_holdout.gini` is 0.5436 [[art:a4a532f0:metrics.vintage_holdout.gini]].
The value of `metrics.vintage_holdout.ks` is 0.4516 [[art:b5b9e888:metrics.vintage_holdout.ks]].
The value of `metrics.vintage_holdout.logloss` is 0.02811 [[art:c32e3713:metrics.vintage_holdout.logloss]].
The value of `metrics.vintage_holdout.mean_predicted` is 0.005647 [[art:5ae28866:metrics.vintage_holdout.mean_predicted]].
The value of `metrics.vintage_holdout.n` is 32177 [[art:37a92951:metrics.vintage_holdout.n]].
The value of `psi.f_burnout` is 0.004614 [[art:445ec3e0:psi.f_burnout]].
The value of `psi.f_credit_score` is 0.06189 [[art:5829d6ed:psi.f_credit_score]].
The value of `psi.f_incentive` is 0.0009923 [[art:8075e035:psi.f_incentive]].
The value of `psi.f_loan_age` is 0.0001994 [[art:6ec631ed:psi.f_loan_age]].
The value of `psi.f_note_rate` is 0.01371 [[art:63c68948:psi.f_note_rate]].
The value of `psi.f_orig_ltv` is 0.03617 [[art:212acb3a:psi.f_orig_ltv]].
The value of `psi.f_orig_upb_log` is 0.04817 [[art:75026ee2:psi.f_orig_upb_log]].
The value of `psi.f_sato` is 0.02773 [[art:2beb335c:psi.f_sato]].
The value of `psi.f_season_cos` is 0.0000179 [[art:cb2ce435:psi.f_season_cos]].
The value of `psi.f_season_sin` is 0.000002939 [[art:44d14048:psi.f_season_sin]].
The value of `psi.max` is 0.06189 [[art:c2e8c8fd:psi.max]].
The value of `psi.out_of_time.f_burnout` is 2.945 [[art:a696b6ff:psi.out_of_time.f_burnout]].
The value of `psi.out_of_time.f_credit_score` is 0.05988 [[art:e02f8367:psi.out_of_time.f_credit_score]].
The value of `psi.out_of_time.f_incentive` is 0.4958 [[art:58b6089b:psi.out_of_time.f_incentive]].
The value of `psi.out_of_time.f_loan_age` is 2.484 [[art:eec03fdd:psi.out_of_time.f_loan_age]].
The value of `psi.out_of_time.f_note_rate` is 0.6977 [[art:b0278c59:psi.out_of_time.f_note_rate]].
The value of `psi.out_of_time.f_orig_ltv` is 0.04301 [[art:3422cd60:psi.out_of_time.f_orig_ltv]].
The value of `psi.out_of_time.f_orig_upb_log` is 0.07136 [[art:fddf2a0a:psi.out_of_time.f_orig_upb_log]].
The value of `psi.out_of_time.f_sato` is 0.01299 [[art:5090c358:psi.out_of_time.f_sato]].
The value of `psi.out_of_time.f_season_cos` is 0.007524 [[art:3487f524:psi.out_of_time.f_season_cos]].
The value of `psi.out_of_time.f_season_sin` is 0.02789 [[art:eb28b9bb:psi.out_of_time.f_season_sin]].
The value of `psi.out_of_time.y_score` is 0.7056 [[art:2dc61374:psi.out_of_time.y_score]].
The value of `psi.vintage_holdout.f_burnout` is 0.04749 [[art:b76fb2b0:psi.vintage_holdout.f_burnout]].
The value of `psi.vintage_holdout.f_credit_score` is 0.03996 [[art:abf4e0aa:psi.vintage_holdout.f_credit_score]].
The value of `psi.vintage_holdout.f_incentive` is 0.4475 [[art:81260b55:psi.vintage_holdout.f_incentive]].
The value of `psi.vintage_holdout.f_loan_age` is 0.07112 [[art:256aaeda:psi.vintage_holdout.f_loan_age]].
The value of `psi.vintage_holdout.f_note_rate` is 0.6088 [[art:c1ffae38:psi.vintage_holdout.f_note_rate]].
The value of `psi.vintage_holdout.f_orig_ltv` is 0.02942 [[art:09f015f3:psi.vintage_holdout.f_orig_ltv]].
The value of `psi.vintage_holdout.f_orig_upb_log` is 0.0404 [[art:ce7dc6c5:psi.vintage_holdout.f_orig_upb_log]].
The value of `psi.vintage_holdout.f_sato` is 0.02989 [[art:17126bd4:psi.vintage_holdout.f_sato]].
The value of `psi.vintage_holdout.f_season_cos` is 0.001288 [[art:5123c902:psi.vintage_holdout.f_season_cos]].
The value of `psi.vintage_holdout.f_season_sin` is 0.0007309 [[art:403ec3c2:psi.vintage_holdout.f_season_sin]].
The value of `psi.vintage_holdout.y_score` is 0.1421 [[art:3713457e:psi.vintage_holdout.y_score]].
The value of `psi.y_score` is 0.001953 [[art:3b9dee2d:psi.y_score]].
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
Calibration by decile of predicted probability on test [[art:dcbc44e6:calibration.test]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.0004313 | 0.0006498 | 1539 |
| 2 | 0.0008926 | 0.0013 | 1539 |
| 3 | 0.001466 | 0.003251 | 1538 |
| 4 | 0.002302 | 0.002601 | 1538 |
| 5 | 0.003457 | 0.003251 | 1538 |
| 6 | 0.00511 | 0.005202 | 1538 |
| 7 | 0.007546 | 0.009103 | 1538 |
| 8 | 0.01122 | 0.008453 | 1538 |
| 9 | 0.01694 | 0.01235 | 1538 |
| 10 | 0.0318 | 0.03446 | 1538 |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table cpr.test -->
Actual against predicted CPR by period on test [[art:ecbd1494:cpr.test]]:

| period | n | actual_cpr | predicted_cpr |
|---|---|---|---|
| 201402 | 15 | 0 | 0.03798 |
| 201403 | 28 | 0 | 0.03254 |
| 201404 | 56 | 0 | 0.02309 |
| 201405 | 68 | 0 | 0.02233 |
| 201406 | 80 | 0 | 0.02166 |
| 201407 | 97 | 0.1169 | 0.01797 |
| 201408 | 111 | 0 | 0.01554 |
| 201409 | 133 | 0.08659 | 0.01216 |
| 201410 | 145 | 0 | 0.01021 |
| 201411 | 161 | 0 | 0.008095 |
| 201412 | 175 | 0 | 0.007842 |
| 201501 | 198 | 0 | 0.007428 |
| 201502 | 198 | 0 | 0.007044 |
| 201503 | 198 | 0.05895 | 0.008695 |
| 201504 | 197 | 0 | 0.009549 |
| 201505 | 197 | 0 | 0.01325 |
| 201506 | 197 | 0 | 0.01494 |
| 201507 | 197 | 0 | 0.01945 |
| 201508 | 197 | 0 | 0.02688 |
| 201509 | 197 | 0.05924 | 0.02957 |
| 201510 | 196 | 0.05954 | 0.03698 |
| 201511 | 195 | 0 | 0.04786 |
| 201512 | 195 | 0 | 0.04992 |
| 201601 | 195 | 0.1698 | 0.07173 |
| 201602 | 192 | 0.06074 | 0.1054 |
| 201603 | 191 | 0.1187 | 0.1396 |
| 201604 | 189 | 0.1198 | 0.1539 |
| 201605 | 187 | 0.3673 | 0.2084 |
| 201606 | 180 | 0.1255 | 0.2036 |
| 201607 | 178 | 0.1268 | 0.2127 |
| 201608 | 176 | 0.06609 | 0.1941 |
| 201609 | 175 | 0.1288 | 0.1538 |
| 201610 | 173 | 0.1893 | 0.1126 |
| 201611 | 170 | 0.06835 | 0.09407 |
| 201612 | 169 | 0.06874 | 0.06776 |
| 201701 | 168 | 0.1339 | 0.0556 |
| 201702 | 176 | 0.2924 | 0.04679 |
| 201703 | 191 | 0.06105 | 0.04026 |
| 201704 | 199 | 0 | 0.03496 |
| 201705 | 218 | 0.05368 | 0.03454 |
| 201706 | 238 | 0.04927 | 0.03104 |
| 201707 | 248 | 0 | 0.02665 |
| 201708 | 274 | 0 | 0.02081 |
| 201709 | 284 | 0.08131 | 0.02157 |
| 201710 | 300 | 0 | 0.01654 |
| 201711 | 323 | 0.03653 | 0.01645 |
| 201712 | 334 | 0.03534 | 0.0209 |
| 201801 | 354 | 0.03338 | 0.02414 |
| 201802 | 353 | 0.06591 | 0.03339 |
| 201803 | 351 | 0.03366 | 0.05241 |
| 201804 | 350 | 0.06646 | 0.0823 |
| 201805 | 348 | 0.1594 | 0.1256 |
| 201806 | 343 | 0.1616 | 0.1493 |
| 201807 | 338 | 0.1638 | 0.161 |
| 201808 | 333 | 0.06974 | 0.1733 |
| 201809 | 331 | 0.2544 | 0.1831 |
| 201810 | 323 | 0.1707 | 0.177 |
| 201811 | 318 | 0.07292 | 0.1609 |
| 201812 | 316 | 0.1742 | 0.1816 |
| 201901 | 311 | 0.1098 | 0.1932 |
| 201902 | 300 | 0.1488 | 0.2297 |
| 201903 | 285 | 0.2253 | 0.2456 |
| 201904 | 258 | 0.246 | 0.2356 |
| 201905 | 243 | 0.1385 | 0.2078 |
| 201906 | 233 | 0.2688 | 0.169 |
| 201907 | 219 | 0.1984 | 0.1198 |
| 201908 | 206 | 0 | 0.08499 |
| 201909 | 191 | 0.06105 | 0.05731 |
| 201910 | 182 | 0.06398 | 0.04077 |
| 201911 | 171 | 0.06796 | 0.03594 |
| 201912 | 166 | 0 | 0.03505 |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table deciles.test -->
Decile separation on test; decile 1 holds the highest probabilities [[art:309fa6f3:deciles.test]]:

| decile | count | events | event_rate | lift |
|---|---|---|---|---|
| 1 | 1539 | 53 | 0.03444 | 4.272 |
| 2 | 1539 | 19 | 0.01235 | 1.531 |
| 3 | 1538 | 13 | 0.008453 | 1.049 |
| 4 | 1538 | 14 | 0.009103 | 1.129 |
| 5 | 1538 | 8 | 0.005202 | 0.6452 |
| 6 | 1538 | 5 | 0.003251 | 0.4033 |
| 7 | 1538 | 4 | 0.002601 | 0.3226 |
| 8 | 1538 | 5 | 0.003251 | 0.4033 |
| 9 | 1538 | 2 | 0.0013 | 0.1613 |
| 10 | 1538 | 1 | 0.0006502 | 0.08066 |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table thresholds.evaluation -->
Every threshold package.yaml declares, with its bound, the recomputed value and the outcome [[art:f71ddec9:thresholds.evaluation]]:

| metric | split | bound | value | result |
|---|---|---|---|---|
| auc | test | minimum 0.65 | 0.7753 | pass |
| calibration_slope | test | minimum 0.8 | 0.9365 | pass |
| calibration_slope | test | maximum 1.2 | 0.9365 | pass |
| psi |  | maximum 0.25 | 0.06189 | pass |
<!-- quaestor:renderer:end -->

## 5. Sensitivity and scenario analysis

This section follows the model risk management guidance at [[reg:SR26-2:V.1.a]].
The value of `condition_number` is 4.943 [[art:4f06a3c5:condition_number]].
The value of `scenario.convexity` is -1130000 [[art:538e0e09:scenario.convexity]].
The value of `scenario.value_change.-100` is -322600 [[art:d33e8e3c:scenario.value_change.-100]].
The value of `scenario.value_change.-200` is -854300 [[art:03816874:scenario.value_change.-200]].
The value of `scenario.value_change.-300` is -1298000 [[art:4829926e:scenario.value_change.-300]].
The value of `scenario.value_change.0` is 0 [[art:1e1b0b88:scenario.value_change.0]].
The value of `scenario.value_change.100` is 119600 [[art:d0970bd9:scenario.value_change.100]].
The value of `scenario.value_change.200` is 157000 [[art:d69c2be1:scenario.value_change.200]].
The value of `scenario.value_change.300` is 168100 [[art:38e75872:scenario.value_change.300]].
The value of `stability.f_burnout.sign_flip` is 0 [[art:ffc296b7:stability.f_burnout.sign_flip]].
The value of `stability.f_credit_score.sign_flip` is 0 [[art:453c8949:stability.f_credit_score.sign_flip]].
The value of `stability.f_incentive.sign_flip` is 0 [[art:1e3dbc9b:stability.f_incentive.sign_flip]].
The value of `stability.f_loan_age.sign_flip` is 0 [[art:02339bed:stability.f_loan_age.sign_flip]].
The value of `stability.f_note_rate.sign_flip` is 0 [[art:4a9e3c32:stability.f_note_rate.sign_flip]].
The value of `stability.f_orig_ltv.sign_flip` is 0 [[art:bb5e04ca:stability.f_orig_ltv.sign_flip]].
The value of `stability.f_orig_upb_log.sign_flip` is 0 [[art:5a5daefb:stability.f_orig_upb_log.sign_flip]].
The value of `stability.f_sato.sign_flip` is 0 [[art:a7092419:stability.f_sato.sign_flip]].
The value of `stability.f_season_cos.sign_flip` is 0 [[art:4c9ae175:stability.f_season_cos.sign_flip]].
The value of `stability.f_season_sin.sign_flip` is 0 [[art:3c609ed8:stability.f_season_sin.sign_flip]].
The value of `threshold.M1.condition_number` is 30 [[art:7e52fd7a:threshold.M1.condition_number]].
The value of `threshold.M1.vif` is 10 [[art:aeb4f33c:threshold.M1.vif]].
The value of `threshold.R1.auc_gap` is 0.1 [[art:b64213d7:threshold.R1.auc_gap]].
The value of `threshold.R1.sign_flip_coef` is 0.05 [[art:aca84377:threshold.R1.sign_flip_coef]].
The value of `threshold.R1.sign_flip_z` is 2 [[art:2e4428c7:threshold.R1.sign_flip_z]].
The value of `vif.f_burnout` is 3.439 [[art:3f7564f6:vif.f_burnout]].
The value of `vif.f_credit_score` is 1.008 [[art:59d19ea1:vif.f_credit_score]].
The value of `vif.f_incentive` is 2.226 [[art:31179b0a:vif.f_incentive]].
The value of `vif.f_loan_age` is 2.929 [[art:903503b0:vif.f_loan_age]].
The value of `vif.f_note_rate` is 4.976 [[art:f6dfe789:vif.f_note_rate]].
The value of `vif.f_orig_ltv` is 1.005 [[art:d0eadaeb:vif.f_orig_ltv]].
The value of `vif.f_orig_upb_log` is 1.006 [[art:8b0886fe:vif.f_orig_upb_log]].
The value of `vif.f_sato` is 1.713 [[art:9a173f4f:vif.f_sato]].
The value of `vif.f_season_cos` is 1.018 [[art:77f16218:vif.f_season_cos]].
The value of `vif.f_season_sin` is 1.004 [[art:3d38c119:vif.f_season_sin]].
The value of `vif.max` is 4.976 [[art:f9e0db60:vif.max]].
<!-- quaestor:renderer:begin table scenario.value_by_shock -->
Servicing value, its change from the base case and first-year CPR, by shock [[art:1143879d:scenario.value_by_shock]]:

| shock_bp | value | value_change | cpr |
|---|---|---|---|
| -300 | 298800 | -1.298e+06 | 0.6219 |
| -200 | 742500 | -854300 | 0.2519 |
| -100 | 1.274e+06 | -322600 | 0.07951 |
| 0 | 1.597e+06 | 0 | 0.02322 |
| 100 | 1.716e+06 | 119600 | 0.006683 |
| 200 | 1.754e+06 | 157000 | 0.001915 |
| 300 | 1.765e+06 | 168100 | 0.0005476 |
<!-- quaestor:renderer:end -->
<!-- quaestor:renderer:begin table stability.auc_by_regime -->
The champion's AUC within each rate_regime on train [[art:960f708f:stability.auc_by_regime]]:

| regime | n | event_rate | auc |
|---|---|---|---|
| falling | 17873 | 0.01438 | 0.7227 |
| rising | 18140 | 0.002756 | 0.7238 |
<!-- quaestor:renderer:end -->

## 6. Findings and recommendations

This section follows the model risk management guidance at [[reg:SR26-2:VI.3]].
No finding was raised by the checks that ran.
The value of `sign_check.f_note_rate.agrees` is 0 [[art:e3173464:sign_check.f_note_rate.agrees]].
The value of `sign_check.f_note_rate.coef_sign` is -1 [[art:9a57eeb9:sign_check.f_note_rate.coef_sign]].
The value of `sign_check.f_note_rate.univariate_direction` is 1 [[art:33e2a051:sign_check.f_note_rate.univariate_direction]].

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1, S1), `compute_metrics` (T1, C1, O1), `check_leakage` (L1, L2), `check_stability` (R1), `check_collinearity` (M1), `challenger_compare` (E1), `run_scenarios` (X1).

### Open items

No open item was recorded for this validation.

## 7. Ongoing monitoring recommendations

This section follows the model risk management guidance at [[reg:SR26-2:V.2]].
The value of `calibration_slope.test` is 0.9365 [[art:3e42ee62:calibration_slope.test]].
The value of `metrics.test.auc` is 0.7753 [[art:57066271:metrics.test.auc]].
The value of `psi.max` is 0.06189 [[art:c2e8c8fd:psi.max]].
The value of `rule.calibration_first_event_rate` is 0.05 [[art:42f1351e:rule.calibration_first_event_rate]].
The value of `threshold.package.auc.test.min` is 0.65 [[art:fececac1:threshold.package.auc.test.min]].
The value of `threshold.package.calibration_slope.test.max` is 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The value of `threshold.package.calibration_slope.test.min` is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]].
The value of `threshold.package.psi.max` is 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].

## Appendix A — Claims

Grounding precision 1.0000 before repair (311 of 311 claims verified) and 1.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 48/48; conceptual_soundness 45/45; data_integrity 66/66; outcomes 106/106; sensitivity 35/35; findings 3/3; monitoring 8/8.

Developer claims: The package declares 3 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). See Appendix D.

Excluded numeric tokens (not claims): inline_code (`scenario.value_change.-100`, `scenario.value_change.-200`, `scenario.value_change.-300`); citation_hash (a49b2789, 3e42ee62, 534cb102, 08d6b321); regulatory_section_id (SR26-2:V.1.b, SR26-2:V.1.a, SR26-2:VI.3, SR26-2:V.2).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The value of `calibration_slope.out_of_time` is 0.9969 . | 0.9969 | ratio | calibration_slope |  | eq | `[[art:a49b2789:calibration_slope.out_of_time]]` | verified | 0.9969389246 |
| 2 | summary | The value of `calibration_slope.test` is 0.9365 . | 0.9365 | ratio | calibration_slope |  | eq | `[[art:3e42ee62:calibration_slope.test]]` | verified | 0.9365180494 |
| 3 | summary | The value of `calibration_slope.train` is 0.9937 . | 0.9937 | ratio | calibration_slope |  | eq | `[[art:534cb102:calibration_slope.train]]` | verified | 0.9936945557 |
| 4 | summary | The value of `calibration_slope.vintage_holdout` is 0.8373 . | 0.8373 | ratio | calibration_slope |  | eq | `[[art:08d6b321:calibration_slope.vintage_holdout]]` | verified | 0.837279841 |
| 5 | summary | The value of `challenger.delta_auc` is -0.07528 . | -0.07528 | ratio | challenger |  | eq | `[[art:89de5f90:challenger.delta_auc]]` | verified | -0.07528493778 |
| 6 | summary | The value of `condition_number` is 4.943 . | 4.943 | ratio | condition_number |  | eq | `[[art:4f06a3c5:condition_number]]` | verified | 4.942565522 |
| 7 | summary | The value of `csi.max` is 0.03438 . | 0.03438 | ratio | csi |  | eq | `[[art:54bd75b0:csi.max]]` | verified | 0.03438094941 |
| 8 | summary | The value of `metrics.out_of_time.auc` is 0.7846 . | 0.7846 | ratio | metrics |  | eq | `[[art:6f2a2d99:metrics.out_of_time.auc]]` | verified | 0.7845616168 |
| 9 | summary | The value of `metrics.out_of_time.brier` is 0.01713 . | 0.01713 | ratio | metrics |  | eq | `[[art:40d244d4:metrics.out_of_time.brier]]` | verified | 0.0171279495 |
| 10 | summary | The value of `metrics.out_of_time.event_rate` is 0.01795 . | 0.01795 | ratio | metrics |  | eq | `[[art:83ccf5c0:metrics.out_of_time.event_rate]]` | verified | 0.01794892714 |
| 11 | summary | The value of `metrics.out_of_time.gini` is 0.5691 . | 0.5691 | ratio | metrics |  | eq | `[[art:890252d7:metrics.out_of_time.gini]]` | verified | 0.5691232337 |
| 12 | summary | The value of `metrics.out_of_time.ks` is 0.4321 . | 0.4321 | ratio | metrics |  | eq | `[[art:16d3e4fe:metrics.out_of_time.ks]]` | verified | 0.4321115953 |
| 13 | summary | The value of `metrics.out_of_time.logloss` is 0.07975 . | 0.07975 | ratio | metrics |  | eq | `[[art:2b7c9b2d:metrics.out_of_time.logloss]]` | verified | 0.07975283787 |
| 14 | summary | The value of `metrics.out_of_time.mean_predicted` is 0.01887… | 0.01887 | ratio | metrics |  | eq | `[[art:3833e0c5:metrics.out_of_time.mean_predicted]]` | verified | 0.01886588953 |
| 15 | summary | The value of `metrics.out_of_time.n` is 12257 . | 12257 | ratio | metrics |  | eq | `[[art:7898809e:metrics.out_of_time.n]]` | verified | 12257 |
| 16 | summary | The value of `metrics.test.auc` is 0.7753 . | 0.7753 | ratio | metrics |  | eq | `[[art:57066271:metrics.test.auc]]` | verified | 0.7752553922 |
| 17 | summary | The value of `metrics.test.brier` is 0.007894 . | 0.007894 | ratio | metrics |  | eq | `[[art:7d3583cd:metrics.test.brier]]` | verified | 0.00789356705 |
| 18 | summary | The value of `metrics.test.event_rate` is 0.008061 . | 0.008061 | ratio | metrics |  | eq | `[[art:570cc08a:metrics.test.event_rate]]` | verified | 0.008061370433 |
| 19 | summary | The value of `metrics.test.gini` is 0.5505 . | 0.5505 | ratio | metrics |  | eq | `[[art:fe7f75d7:metrics.test.gini]]` | verified | 0.5505107844 |
| 20 | summary | The value of `metrics.test.ks` is 0.4162 . | 0.4162 | ratio | metrics |  | eq | `[[art:c569c301:metrics.test.ks]]` | verified | 0.4161772354 |
| 21 | summary | The value of `metrics.test.logloss` is 0.04263 . | 0.04263 | ratio | metrics |  | eq | `[[art:320e4c6b:metrics.test.logloss]]` | verified | 0.04263297829 |
| 22 | summary | The value of `metrics.test.mean_predicted` is 0.008116 . | 0.008116 | ratio | metrics |  | eq | `[[art:3bc93911:metrics.test.mean_predicted]]` | verified | 0.008115821785 |
| 23 | summary | The value of `metrics.test.n` is 15382 . | 15382 | ratio | metrics |  | eq | `[[art:e55953e1:metrics.test.n]]` | verified | 15382 |
| 24 | summary | The value of `metrics.train.auc` is 0.7883 . | 0.7883 | ratio | metrics |  | eq | `[[art:fa609ae1:metrics.train.auc]]` | verified | 0.7883327303 |
| 25 | summary | The value of `metrics.train.brier` is 0.008317 . | 0.008317 | ratio | metrics |  | eq | `[[art:83666c70:metrics.train.brier]]` | verified | 0.008317491392 |
| 26 | summary | The value of `metrics.train.event_rate` is 0.008525 . | 0.008525 | ratio | metrics |  | eq | `[[art:b9ef3327:metrics.train.event_rate]]` | verified | 0.008524699414 |
| 27 | summary | The value of `metrics.train.gini` is 0.5767 . | 0.5767 | ratio | metrics |  | eq | `[[art:0b6b2058:metrics.train.gini]]` | verified | 0.5766654607 |
| 28 | summary | The value of `metrics.train.ks` is 0.4562 . | 0.4562 | ratio | metrics |  | eq | `[[art:c355478b:metrics.train.ks]]` | verified | 0.4562056834 |
| 29 | summary | The value of `metrics.train.logloss` is 0.04408 . | 0.04408 | ratio | metrics |  | eq | `[[art:199c7db5:metrics.train.logloss]]` | verified | 0.04408402922 |
| 30 | summary | The value of `metrics.train.mean_predicted` is 0.008427 . | 0.008427 | ratio | metrics |  | eq | `[[art:a63f6555:metrics.train.mean_predicted]]` | verified | 0.008426526894 |
| 31 | summary | The value of `metrics.train.n` is 36013 . | 36013 | ratio | metrics |  | eq | `[[art:6fdfeabb:metrics.train.n]]` | verified | 36013 |
| 32 | summary | The value of `metrics.vintage_holdout.auc` is 0.7718 . | 0.7718 | ratio | metrics |  | eq | `[[art:ac6794c5:metrics.vintage_holdout.auc]]` | verified | 0.7717974135 |
| 33 | summary | The value of `metrics.vintage_holdout.brier` is 0.004763 . | 0.004763 | ratio | metrics |  | eq | `[[art:f3c6bdcc:metrics.vintage_holdout.brier]]` | verified | 0.004763025704 |
| 34 | summary | The value of `metrics.vintage_holdout.event_rate` is 0.00481… | 0.004817 | ratio | metrics |  | eq | `[[art:e3590a16:metrics.vintage_holdout.event_rate]]` | verified | 0.004817105386 |
| 35 | summary | The value of `metrics.vintage_holdout.gini` is 0.5436 . | 0.5436 | ratio | metrics |  | eq | `[[art:a4a532f0:metrics.vintage_holdout.gini]]` | verified | 0.5435948269 |
| 36 | summary | The value of `metrics.vintage_holdout.ks` is 0.4516 . | 0.4516 | ratio | metrics |  | eq | `[[art:b5b9e888:metrics.vintage_holdout.ks]]` | verified | 0.4515647508 |
| 37 | summary | The value of `metrics.vintage_holdout.logloss` is 0.02811 . | 0.02811 | ratio | metrics |  | eq | `[[art:c32e3713:metrics.vintage_holdout.logloss]]` | verified | 0.02810570342 |
| 38 | summary | The value of `metrics.vintage_holdout.mean_predicted` is 0.0… | 0.005647 | ratio | metrics |  | eq | `[[art:5ae28866:metrics.vintage_holdout.mean_predicted]]` | verified | 0.005646788012 |
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
| 50 | conceptual_soundness | The value of `ablation.f_burnout.delta_auc` is -0.0001876 . | -0.0001876 | ratio | ablation |  | eq | `[[art:4c92a645:ablation.f_burnout.delta_auc]]` | verified | -0.0001876329287 |
| 51 | conceptual_soundness | The value of `ablation.f_credit_score.delta_auc` is -0.01474… | -0.01474 | ratio | ablation |  | eq | `[[art:302cee1d:ablation.f_credit_score.delta_auc]]` | verified | -0.0147431913 |
| 52 | conceptual_soundness | The value of `ablation.f_incentive.delta_auc` is -0.04117 . | -0.04117 | ratio | ablation |  | eq | `[[art:cc8b34d4:ablation.f_incentive.delta_auc]]` | verified | -0.0411745927 |
| 53 | conceptual_soundness | The value of `ablation.f_loan_age.delta_auc` is 0.0008166 . | 0.0008166 | ratio | ablation |  | eq | `[[art:cd3be5c5:ablation.f_loan_age.delta_auc]]` | verified | 0.0008165996474 |
| 54 | conceptual_soundness | The value of `ablation.f_note_rate.delta_auc` is -0.002585 . | -0.002585 | ratio | ablation |  | eq | `[[art:034cea8e:ablation.f_note_rate.delta_auc]]` | verified | -0.002585106068 |
| 55 | conceptual_soundness | The value of `ablation.f_orig_ltv.delta_auc` is -0.002294 . | -0.002294 | ratio | ablation |  | eq | `[[art:45bbe28a:ablation.f_orig_ltv.delta_auc]]` | verified | -0.002294407165 |
| 56 | conceptual_soundness | The value of `ablation.f_orig_upb_log.delta_auc` is -0.01927… | -0.01927 | ratio | ablation |  | eq | `[[art:dbd54a4a:ablation.f_orig_upb_log.delta_auc]]` | verified | -0.01926646624 |
| 57 | conceptual_soundness | The value of `ablation.f_sato.delta_auc` is 0.0005201 . | 0.0005201 | ratio | ablation |  | eq | `[[art:452f8833:ablation.f_sato.delta_auc]]` | verified | 0.0005200867657 |
| 58 | conceptual_soundness | The value of `ablation.f_season_cos.delta_auc` is -0.0004826… | -0.0004826 | ratio | ablation |  | eq | `[[art:f01715f5:ablation.f_season_cos.delta_auc]]` | verified | -0.00048256018 |
| 59 | conceptual_soundness | The value of `ablation.f_season_sin.delta_auc` is -0.0003885… | -0.0003885 | ratio | ablation |  | eq | `[[art:a81a1fce:ablation.f_season_sin.delta_auc]]` | verified | -0.0003884794439 |
| 60 | conceptual_soundness | The value of `challenger.auc` is 0.7 . | 0.7 | ratio | challenger |  | eq | `[[art:a55c39c9:challenger.auc]]` | verified | 0.6999704544 |
| 61 | conceptual_soundness | The value of `challenger.brier` is 0.008371 . | 0.008371 | ratio | challenger |  | eq | `[[art:57c3e2f5:challenger.brier]]` | verified | 0.008371219123 |
| 62 | conceptual_soundness | The value of `challenger.delta_auc` is -0.07528 . | -0.07528 | ratio | challenger |  | eq | `[[art:89de5f90:challenger.delta_auc]]` | verified | -0.07528493778 |
| 63 | conceptual_soundness | The value of `metrics.test.auc` is 0.7753 . | 0.7753 | ratio | metrics |  | eq | `[[art:57066271:metrics.test.auc]]` | verified | 0.7752553922 |
| 64 | conceptual_soundness | The value of `metrics.test.brier` is 0.007894 . | 0.007894 | ratio | metrics |  | eq | `[[art:7d3583cd:metrics.test.brier]]` | verified | 0.00789356705 |
| 65 | conceptual_soundness | The value of `sign_check.f_burnout.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:a7b47126:sign_check.f_burnout.agrees]]` | verified | 1 |
| 66 | conceptual_soundness | The value of `sign_check.f_burnout.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:434a2eb4:sign_check.f_burnout.coef_sign]]` | verified | 1 |
| 67 | conceptual_soundness | The value of `sign_check.f_burnout.univariate_direction` is… | 1 | ratio | sign_check |  | eq | `[[art:6c04f9a3:sign_check.f_burnout.univariate_direction]]` | verified | 1 |
| 68 | conceptual_soundness | The value of `sign_check.f_credit_score.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:6a693a4d:sign_check.f_credit_score.agrees]]` | verified | 1 |
| 69 | conceptual_soundness | The value of `sign_check.f_credit_score.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:4893edbf:sign_check.f_credit_score.coef_sign]]` | verified | 1 |
| 70 | conceptual_soundness | The value of `sign_check.f_credit_score.univariate_direction… | 1 | ratio | sign_check |  | eq | `[[art:5364f2d9:sign_check.f_credit_score.univariate_direction]]` | verified | 1 |
| 71 | conceptual_soundness | The value of `sign_check.f_incentive.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:aab920d4:sign_check.f_incentive.agrees]]` | verified | 1 |
| 72 | conceptual_soundness | The value of `sign_check.f_incentive.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:34fbc238:sign_check.f_incentive.coef_sign]]` | verified | 1 |
| 73 | conceptual_soundness | The value of `sign_check.f_incentive.univariate_direction` i… | 1 | ratio | sign_check |  | eq | `[[art:284b2d7c:sign_check.f_incentive.univariate_direction]]` | verified | 1 |
| 74 | conceptual_soundness | The value of `sign_check.f_note_rate.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:e3173464:sign_check.f_note_rate.agrees]]` | verified | 0 |
| 75 | conceptual_soundness | The value of `sign_check.f_note_rate.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:9a57eeb9:sign_check.f_note_rate.coef_sign]]` | verified | -1 |
| 76 | conceptual_soundness | The value of `sign_check.f_note_rate.univariate_direction` i… | 1 | ratio | sign_check |  | eq | `[[art:33e2a051:sign_check.f_note_rate.univariate_direction]]` | verified | 1 |
| 77 | conceptual_soundness | The value of `sign_check.f_orig_ltv.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:56d6495e:sign_check.f_orig_ltv.agrees]]` | verified | 1 |
| 78 | conceptual_soundness | The value of `sign_check.f_orig_ltv.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:eb67b95a:sign_check.f_orig_ltv.coef_sign]]` | verified | -1 |
| 79 | conceptual_soundness | The value of `sign_check.f_orig_ltv.univariate_direction` is… | -1 | ratio | sign_check |  | eq | `[[art:1883c240:sign_check.f_orig_ltv.univariate_direction]]` | verified | -1 |
| 80 | conceptual_soundness | The value of `sign_check.f_orig_upb_log.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:57b59c6a:sign_check.f_orig_upb_log.agrees]]` | verified | 1 |
| 81 | conceptual_soundness | The value of `sign_check.f_orig_upb_log.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:5165217f:sign_check.f_orig_upb_log.coef_sign]]` | verified | 1 |
| 82 | conceptual_soundness | The value of `sign_check.f_orig_upb_log.univariate_direction… | 1 | ratio | sign_check |  | eq | `[[art:901ddb38:sign_check.f_orig_upb_log.univariate_direction]]` | verified | 1 |
| 83 | conceptual_soundness | The value of `sign_check.f_sato.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:44052838:sign_check.f_sato.agrees]]` | verified | 1 |
| 84 | conceptual_soundness | The value of `sign_check.f_sato.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:55450fdb:sign_check.f_sato.coef_sign]]` | verified | 1 |
| 85 | conceptual_soundness | The value of `sign_check.f_sato.univariate_direction` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:5cc2f196:sign_check.f_sato.univariate_direction]]` | verified | 1 |
| 86 | conceptual_soundness | The value of `sign_check.f_season_cos.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:e02a4777:sign_check.f_season_cos.agrees]]` | verified | 1 |
| 87 | conceptual_soundness | The value of `sign_check.f_season_cos.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:25dfa200:sign_check.f_season_cos.coef_sign]]` | verified | -1 |
| 88 | conceptual_soundness | The value of `sign_check.f_season_cos.univariate_direction`… | -1 | ratio | sign_check |  | eq | `[[art:7f6fd623:sign_check.f_season_cos.univariate_direction]]` | verified | -1 |
| 89 | conceptual_soundness | The value of `sign_check.f_season_sin.agrees` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:caceebf9:sign_check.f_season_sin.agrees]]` | verified | 1 |
| 90 | conceptual_soundness | The value of `sign_check.f_season_sin.coef_sign` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:a6b9d22d:sign_check.f_season_sin.coef_sign]]` | verified | 1 |
| 91 | conceptual_soundness | The value of `sign_check.f_season_sin.univariate_direction`… | 1 | ratio | sign_check |  | eq | `[[art:8a2dc987:sign_check.f_season_sin.univariate_direction]]` | verified | 1 |
| 92 | conceptual_soundness | The value of `sign_check.n_disagreements` is 1 . | 1 | ratio | sign_check |  | eq | `[[art:f96ece96:sign_check.n_disagreements]]` | verified | 1 |
| 93 | conceptual_soundness | The value of `threshold.E1.delta_auc` is 0.03 . | 0.03 | ratio | threshold |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 94 | data_integrity | The value of `csi.f_burnout` is 0.0009851 . | 0.0009851 | ratio | csi |  | eq | `[[art:94a1612f:csi.f_burnout]]` | verified | 0.0009851123767 |
| 95 | data_integrity | The value of `csi.f_credit_score` is 0.007909 . | 0.007909 | ratio | csi |  | eq | `[[art:70748e80:csi.f_credit_score]]` | verified | 0.007908848663 |
| 96 | data_integrity | The value of `csi.f_incentive` is 0.005804 . | 0.005804 | ratio | csi |  | eq | `[[art:ac5ee43b:csi.f_incentive]]` | verified | 0.005803522882 |
| 97 | data_integrity | The value of `csi.f_loan_age` is 0 . | 0 | ratio | csi |  | eq | `[[art:53ae3ece:csi.f_loan_age]]` | verified | 0 |
| 98 | data_integrity | The value of `csi.f_note_rate` is 0.01822 . | 0.01822 | ratio | csi |  | eq | `[[art:06292416:csi.f_note_rate]]` | verified | 0.01822065751 |
| 99 | data_integrity | The value of `csi.f_orig_ltv` is 0.03438 . | 0.03438 | ratio | csi |  | eq | `[[art:1f963d83:csi.f_orig_ltv]]` | verified | 0.03438094941 |
| 100 | data_integrity | The value of `csi.f_orig_upb_log` is 0.002969 . | 0.002969 | ratio | csi |  | eq | `[[art:a10d20d5:csi.f_orig_upb_log]]` | verified | 0.00296903904 |
| 101 | data_integrity | The value of `csi.f_sato` is 0.001487 . | 0.001487 | ratio | csi |  | eq | `[[art:ce21936e:csi.f_sato]]` | verified | 0.001487358985 |
| 102 | data_integrity | The value of `csi.f_season_cos` is 0.0004785 . | 0.0004785 | ratio | csi |  | eq | `[[art:15fe2d99:csi.f_season_cos]]` | verified | 0.0004785421555 |
| 103 | data_integrity | The value of `csi.f_season_sin` is 0.00007624 . | 7.624e-05 | ratio | csi |  | eq | `[[art:81e8dbf0:csi.f_season_sin]]` | verified | 7.624273793e-05 |
| 104 | data_integrity | The value of `csi.max` is 0.03438 . | 0.03438 | ratio | csi |  | eq | `[[art:54bd75b0:csi.max]]` | verified | 0.03438094941 |
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
| 120 | data_integrity | The value of `psi.f_burnout` is 0.004614 . | 0.004614 | ratio | psi |  | eq | `[[art:445ec3e0:psi.f_burnout]]` | verified | 0.004614338236 |
| 121 | data_integrity | The value of `psi.f_credit_score` is 0.06189 . | 0.06189 | ratio | psi |  | eq | `[[art:5829d6ed:psi.f_credit_score]]` | verified | 0.06188985797 |
| 122 | data_integrity | The value of `psi.f_incentive` is 0.0009923 . | 0.0009923 | ratio | psi |  | eq | `[[art:8075e035:psi.f_incentive]]` | verified | 0.0009922551416 |
| 123 | data_integrity | The value of `psi.f_loan_age` is 0.0001994 . | 0.0001994 | ratio | psi |  | eq | `[[art:6ec631ed:psi.f_loan_age]]` | verified | 0.0001993816816 |
| 124 | data_integrity | The value of `psi.f_note_rate` is 0.01371 . | 0.01371 | ratio | psi |  | eq | `[[art:63c68948:psi.f_note_rate]]` | verified | 0.01370911382 |
| 125 | data_integrity | The value of `psi.f_orig_ltv` is 0.03617 . | 0.03617 | ratio | psi |  | eq | `[[art:212acb3a:psi.f_orig_ltv]]` | verified | 0.03617297258 |
| 126 | data_integrity | The value of `psi.f_orig_upb_log` is 0.04817 . | 0.04817 | ratio | psi |  | eq | `[[art:75026ee2:psi.f_orig_upb_log]]` | verified | 0.04817081196 |
| 127 | data_integrity | The value of `psi.f_sato` is 0.02773 . | 0.02773 | ratio | psi |  | eq | `[[art:2beb335c:psi.f_sato]]` | verified | 0.02772829856 |
| 128 | data_integrity | The value of `psi.f_season_cos` is 0.0000179 . | 1.79e-05 | ratio | psi |  | eq | `[[art:cb2ce435:psi.f_season_cos]]` | verified | 1.790085913e-05 |
| 129 | data_integrity | The value of `psi.f_season_sin` is 0.000002939 . | 2.939e-06 | ratio | psi |  | eq | `[[art:44d14048:psi.f_season_sin]]` | verified | 2.939045338e-06 |
| 130 | data_integrity | The value of `psi.max` is 0.06189 . | 0.06189 | ratio | psi |  | eq | `[[art:c2e8c8fd:psi.max]]` | verified | 0.06188985797 |
| 131 | data_integrity | The value of `psi.out_of_time.f_burnout` is 2.945 . | 2.945 | ratio | psi |  | eq | `[[art:a696b6ff:psi.out_of_time.f_burnout]]` | verified | 2.944521522 |
| 132 | data_integrity | The value of `psi.out_of_time.f_credit_score` is 0.05988 . | 0.05988 | ratio | psi |  | eq | `[[art:e02f8367:psi.out_of_time.f_credit_score]]` | verified | 0.05987964443 |
| 133 | data_integrity | The value of `psi.out_of_time.f_incentive` is 0.4958 . | 0.4958 | ratio | psi |  | eq | `[[art:58b6089b:psi.out_of_time.f_incentive]]` | verified | 0.4958065489 |
| 134 | data_integrity | The value of `psi.out_of_time.f_loan_age` is 2.484 . | 2.484 | ratio | psi |  | eq | `[[art:eec03fdd:psi.out_of_time.f_loan_age]]` | verified | 2.483993033 |
| 135 | data_integrity | The value of `psi.out_of_time.f_note_rate` is 0.6977 . | 0.6977 | ratio | psi |  | eq | `[[art:b0278c59:psi.out_of_time.f_note_rate]]` | verified | 0.6976589281 |
| 136 | data_integrity | The value of `psi.out_of_time.f_orig_ltv` is 0.04301 . | 0.04301 | ratio | psi |  | eq | `[[art:3422cd60:psi.out_of_time.f_orig_ltv]]` | verified | 0.04300793312 |
| 137 | data_integrity | The value of `psi.out_of_time.f_orig_upb_log` is 0.07136 . | 0.07136 | ratio | psi |  | eq | `[[art:fddf2a0a:psi.out_of_time.f_orig_upb_log]]` | verified | 0.07136421414 |
| 138 | data_integrity | The value of `psi.out_of_time.f_sato` is 0.01299 . | 0.01299 | ratio | psi |  | eq | `[[art:5090c358:psi.out_of_time.f_sato]]` | verified | 0.01298850667 |
| 139 | data_integrity | The value of `psi.out_of_time.f_season_cos` is 0.007524 . | 0.007524 | ratio | psi |  | eq | `[[art:3487f524:psi.out_of_time.f_season_cos]]` | verified | 0.00752368457 |
| 140 | data_integrity | The value of `psi.out_of_time.f_season_sin` is 0.02789 . | 0.02789 | ratio | psi |  | eq | `[[art:eb28b9bb:psi.out_of_time.f_season_sin]]` | verified | 0.02788988464 |
| 141 | data_integrity | The value of `psi.out_of_time.y_score` is 0.7056 . | 0.7056 | ratio | psi |  | eq | `[[art:2dc61374:psi.out_of_time.y_score]]` | verified | 0.7055906656 |
| 142 | data_integrity | The value of `psi.vintage_holdout.f_burnout` is 0.04749 . | 0.04749 | ratio | psi |  | eq | `[[art:b76fb2b0:psi.vintage_holdout.f_burnout]]` | verified | 0.04749372789 |
| 143 | data_integrity | The value of `psi.vintage_holdout.f_credit_score` is 0.03996… | 0.03996 | ratio | psi |  | eq | `[[art:abf4e0aa:psi.vintage_holdout.f_credit_score]]` | verified | 0.03995819732 |
| 144 | data_integrity | The value of `psi.vintage_holdout.f_incentive` is 0.4475 . | 0.4475 | ratio | psi |  | eq | `[[art:81260b55:psi.vintage_holdout.f_incentive]]` | verified | 0.4475226601 |
| 145 | data_integrity | The value of `psi.vintage_holdout.f_loan_age` is 0.07112 . | 0.07112 | ratio | psi |  | eq | `[[art:256aaeda:psi.vintage_holdout.f_loan_age]]` | verified | 0.07111526296 |
| 146 | data_integrity | The value of `psi.vintage_holdout.f_note_rate` is 0.6088 . | 0.6088 | ratio | psi |  | eq | `[[art:c1ffae38:psi.vintage_holdout.f_note_rate]]` | verified | 0.608822927 |
| 147 | data_integrity | The value of `psi.vintage_holdout.f_orig_ltv` is 0.02942 . | 0.02942 | ratio | psi |  | eq | `[[art:09f015f3:psi.vintage_holdout.f_orig_ltv]]` | verified | 0.0294150369 |
| 148 | data_integrity | The value of `psi.vintage_holdout.f_orig_upb_log` is 0.0404… | 0.0404 | ratio | psi |  | eq | `[[art:ce7dc6c5:psi.vintage_holdout.f_orig_upb_log]]` | verified | 0.04039645306 |
| 149 | data_integrity | The value of `psi.vintage_holdout.f_sato` is 0.02989 . | 0.02989 | ratio | psi |  | eq | `[[art:17126bd4:psi.vintage_holdout.f_sato]]` | verified | 0.02989256711 |
| 150 | data_integrity | The value of `psi.vintage_holdout.f_season_cos` is 0.001288… | 0.001288 | ratio | psi |  | eq | `[[art:5123c902:psi.vintage_holdout.f_season_cos]]` | verified | 0.0012879007 |
| 151 | data_integrity | The value of `psi.vintage_holdout.f_season_sin` is 0.0007309… | 0.0007309 | ratio | psi |  | eq | `[[art:403ec3c2:psi.vintage_holdout.f_season_sin]]` | verified | 0.0007309374015 |
| 152 | data_integrity | The value of `psi.vintage_holdout.y_score` is 0.1421 . | 0.1421 | ratio | psi |  | eq | `[[art:3713457e:psi.vintage_holdout.y_score]]` | verified | 0.142110315 |
| 153 | data_integrity | The value of `psi.y_score` is 0.001953 . | 0.001953 | ratio | psi |  | eq | `[[art:3b9dee2d:psi.y_score]]` | verified | 0.001952903716 |
| 154 | data_integrity | The value of `threshold.D1.missing_gap` is 0.1 . | 0.1 | ratio | threshold |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 155 | data_integrity | The value of `threshold.L1.single_feature_auc` is 0.9 . | 0.9 | ratio | threshold |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 156 | data_integrity | The value of `threshold.L2.overlap` is 0.005 . | 0.005 | ratio | threshold |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 157 | data_integrity | The value of `threshold.L2.overlap.features_effective` is 0.… | 0.005 | ratio | threshold |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 158 | data_integrity | The value of `threshold.S1.psi` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 159 | data_integrity | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 160 | outcomes | The value of `calibration.mean_rel_gap.out_of_time` is 0.051… | 0.05109 | ratio | calibration |  | eq | `[[art:c599bd89:calibration.mean_rel_gap.out_of_time]]` | verified | 0.05108730888 |
| 161 | outcomes | The value of `calibration.mean_rel_gap.test` is 0.006755 . | 0.006755 | ratio | calibration |  | eq | `[[art:d1b269ea:calibration.mean_rel_gap.test]]` | verified | 0.006754602373 |
| 162 | outcomes | The value of `calibration.mean_rel_gap.train` is 0.01152 . | 0.01152 | ratio | calibration |  | eq | `[[art:e28c45a9:calibration.mean_rel_gap.train]]` | verified | 0.01151624417 |
| 163 | outcomes | The value of `calibration.mean_rel_gap.vintage_holdout` is 0… | 0.1722 | ratio | calibration |  | eq | `[[art:55a672c2:calibration.mean_rel_gap.vintage_holdout]]` | verified | 0.1722367603 |
| 164 | outcomes | The value of `calibration_intercept.out_of_time` is -0.06272… | -0.06272 | ratio | calibration_intercept |  | eq | `[[art:fc7ece3a:calibration_intercept.out_of_time]]` | verified | -0.06272473851 |
| 165 | outcomes | The value of `calibration_intercept.test` is -0.277 . | -0.277 | ratio | calibration_intercept |  | eq | `[[art:e87b5c13:calibration_intercept.test]]` | verified | -0.2769708146 |
| 166 | outcomes | The value of `calibration_intercept.train` is -0.01454 . | -0.01454 | ratio | calibration_intercept |  | eq | `[[art:11d7a3ca:calibration_intercept.train]]` | verified | -0.01453793696 |
| 167 | outcomes | The value of `calibration_intercept.vintage_holdout` is -0.9… | -0.9028 | ratio | calibration_intercept |  | eq | `[[art:44715143:calibration_intercept.vintage_holdout]]` | verified | -0.9028328443 |
| 168 | outcomes | The value of `calibration_slope.out_of_time` is 0.9969 . | 0.9969 | ratio | calibration_slope |  | eq | `[[art:a49b2789:calibration_slope.out_of_time]]` | verified | 0.9969389246 |
| 169 | outcomes | The value of `calibration_slope.test` is 0.9365 . | 0.9365 | ratio | calibration_slope |  | eq | `[[art:3e42ee62:calibration_slope.test]]` | verified | 0.9365180494 |
| 170 | outcomes | The value of `calibration_slope.train` is 0.9937 . | 0.9937 | ratio | calibration_slope |  | eq | `[[art:534cb102:calibration_slope.train]]` | verified | 0.9936945557 |
| 171 | outcomes | The value of `calibration_slope.vintage_holdout` is 0.8373 . | 0.8373 | ratio | calibration_slope |  | eq | `[[art:08d6b321:calibration_slope.vintage_holdout]]` | verified | 0.837279841 |
| 172 | outcomes | The value of `cpr.out_of_time.mae` is 0.05857 . | 0.05857 | ratio | cpr |  | eq | `[[art:a7ecd72b:cpr.out_of_time.mae]]` | verified | 0.05856944955 |
| 173 | outcomes | The value of `cpr.test.mae` is 0.04264 . | 0.04264 | ratio | cpr |  | eq | `[[art:ff266c97:cpr.test.mae]]` | verified | 0.042636033 |
| 174 | outcomes | The value of `cpr.train.mae` is 0.02658 . | 0.02658 | ratio | cpr |  | eq | `[[art:f2c3683c:cpr.train.mae]]` | verified | 0.02657629251 |
| 175 | outcomes | The value of `cpr.vintage_holdout.mae` is 0.0289 . | 0.0289 | ratio | cpr |  | eq | `[[art:172ebed4:cpr.vintage_holdout.mae]]` | verified | 0.0289048118 |
| 176 | outcomes | The value of `deciles.out_of_time.top2_capture` is 0.5773 . | 0.5773 | ratio | deciles |  | eq | `[[art:df63152b:deciles.out_of_time.top2_capture]]` | verified | 0.5772727273 |
| 177 | outcomes | The value of `deciles.test.top2_capture` is 0.5806 . | 0.5806 | ratio | deciles |  | eq | `[[art:43c4adc5:deciles.test.top2_capture]]` | verified | 0.5806451613 |
| 178 | outcomes | The value of `deciles.train.top2_capture` is 0.5961 . | 0.5961 | ratio | deciles |  | eq | `[[art:e8dd0c53:deciles.train.top2_capture]]` | verified | 0.5960912052 |
| 179 | outcomes | The value of `deciles.vintage_holdout.top2_capture` is 0.587… | 0.5871 | ratio | deciles |  | eq | `[[art:8b59f312:deciles.vintage_holdout.top2_capture]]` | verified | 0.5870967742 |
| 180 | outcomes | The value of `metrics.out_of_time.auc` is 0.7846 . | 0.7846 | ratio | metrics |  | eq | `[[art:6f2a2d99:metrics.out_of_time.auc]]` | verified | 0.7845616168 |
| 181 | outcomes | The value of `metrics.out_of_time.brier` is 0.01713 . | 0.01713 | ratio | metrics |  | eq | `[[art:40d244d4:metrics.out_of_time.brier]]` | verified | 0.0171279495 |
| 182 | outcomes | The value of `metrics.out_of_time.event_rate` is 0.01795 . | 0.01795 | ratio | metrics |  | eq | `[[art:83ccf5c0:metrics.out_of_time.event_rate]]` | verified | 0.01794892714 |
| 183 | outcomes | The value of `metrics.out_of_time.gini` is 0.5691 . | 0.5691 | ratio | metrics |  | eq | `[[art:890252d7:metrics.out_of_time.gini]]` | verified | 0.5691232337 |
| 184 | outcomes | The value of `metrics.out_of_time.ks` is 0.4321 . | 0.4321 | ratio | metrics |  | eq | `[[art:16d3e4fe:metrics.out_of_time.ks]]` | verified | 0.4321115953 |
| 185 | outcomes | The value of `metrics.out_of_time.logloss` is 0.07975 . | 0.07975 | ratio | metrics |  | eq | `[[art:2b7c9b2d:metrics.out_of_time.logloss]]` | verified | 0.07975283787 |
| 186 | outcomes | The value of `metrics.out_of_time.mean_predicted` is 0.01887… | 0.01887 | ratio | metrics |  | eq | `[[art:3833e0c5:metrics.out_of_time.mean_predicted]]` | verified | 0.01886588953 |
| 187 | outcomes | The value of `metrics.out_of_time.n` is 12257 . | 12257 | ratio | metrics |  | eq | `[[art:7898809e:metrics.out_of_time.n]]` | verified | 12257 |
| 188 | outcomes | The value of `metrics.test.auc` is 0.7753 . | 0.7753 | ratio | metrics |  | eq | `[[art:57066271:metrics.test.auc]]` | verified | 0.7752553922 |
| 189 | outcomes | The value of `metrics.test.brier` is 0.007894 . | 0.007894 | ratio | metrics |  | eq | `[[art:7d3583cd:metrics.test.brier]]` | verified | 0.00789356705 |
| 190 | outcomes | The value of `metrics.test.event_rate` is 0.008061 . | 0.008061 | ratio | metrics |  | eq | `[[art:570cc08a:metrics.test.event_rate]]` | verified | 0.008061370433 |
| 191 | outcomes | The value of `metrics.test.gini` is 0.5505 . | 0.5505 | ratio | metrics |  | eq | `[[art:fe7f75d7:metrics.test.gini]]` | verified | 0.5505107844 |
| 192 | outcomes | The value of `metrics.test.ks` is 0.4162 . | 0.4162 | ratio | metrics |  | eq | `[[art:c569c301:metrics.test.ks]]` | verified | 0.4161772354 |
| 193 | outcomes | The value of `metrics.test.logloss` is 0.04263 . | 0.04263 | ratio | metrics |  | eq | `[[art:320e4c6b:metrics.test.logloss]]` | verified | 0.04263297829 |
| 194 | outcomes | The value of `metrics.test.mean_predicted` is 0.008116 . | 0.008116 | ratio | metrics |  | eq | `[[art:3bc93911:metrics.test.mean_predicted]]` | verified | 0.008115821785 |
| 195 | outcomes | The value of `metrics.test.n` is 15382 . | 15382 | ratio | metrics |  | eq | `[[art:e55953e1:metrics.test.n]]` | verified | 15382 |
| 196 | outcomes | The value of `metrics.train.auc` is 0.7883 . | 0.7883 | ratio | metrics |  | eq | `[[art:fa609ae1:metrics.train.auc]]` | verified | 0.7883327303 |
| 197 | outcomes | The value of `metrics.train.brier` is 0.008317 . | 0.008317 | ratio | metrics |  | eq | `[[art:83666c70:metrics.train.brier]]` | verified | 0.008317491392 |
| 198 | outcomes | The value of `metrics.train.event_rate` is 0.008525 . | 0.008525 | ratio | metrics |  | eq | `[[art:b9ef3327:metrics.train.event_rate]]` | verified | 0.008524699414 |
| 199 | outcomes | The value of `metrics.train.gini` is 0.5767 . | 0.5767 | ratio | metrics |  | eq | `[[art:0b6b2058:metrics.train.gini]]` | verified | 0.5766654607 |
| 200 | outcomes | The value of `metrics.train.ks` is 0.4562 . | 0.4562 | ratio | metrics |  | eq | `[[art:c355478b:metrics.train.ks]]` | verified | 0.4562056834 |
| 201 | outcomes | The value of `metrics.train.logloss` is 0.04408 . | 0.04408 | ratio | metrics |  | eq | `[[art:199c7db5:metrics.train.logloss]]` | verified | 0.04408402922 |
| 202 | outcomes | The value of `metrics.train.mean_predicted` is 0.008427 . | 0.008427 | ratio | metrics |  | eq | `[[art:a63f6555:metrics.train.mean_predicted]]` | verified | 0.008426526894 |
| 203 | outcomes | The value of `metrics.train.n` is 36013 . | 36013 | ratio | metrics |  | eq | `[[art:6fdfeabb:metrics.train.n]]` | verified | 36013 |
| 204 | outcomes | The value of `metrics.vintage_holdout.auc` is 0.7718 . | 0.7718 | ratio | metrics |  | eq | `[[art:ac6794c5:metrics.vintage_holdout.auc]]` | verified | 0.7717974135 |
| 205 | outcomes | The value of `metrics.vintage_holdout.brier` is 0.004763 . | 0.004763 | ratio | metrics |  | eq | `[[art:f3c6bdcc:metrics.vintage_holdout.brier]]` | verified | 0.004763025704 |
| 206 | outcomes | The value of `metrics.vintage_holdout.event_rate` is 0.00481… | 0.004817 | ratio | metrics |  | eq | `[[art:e3590a16:metrics.vintage_holdout.event_rate]]` | verified | 0.004817105386 |
| 207 | outcomes | The value of `metrics.vintage_holdout.gini` is 0.5436 . | 0.5436 | ratio | metrics |  | eq | `[[art:a4a532f0:metrics.vintage_holdout.gini]]` | verified | 0.5435948269 |
| 208 | outcomes | The value of `metrics.vintage_holdout.ks` is 0.4516 . | 0.4516 | ratio | metrics |  | eq | `[[art:b5b9e888:metrics.vintage_holdout.ks]]` | verified | 0.4515647508 |
| 209 | outcomes | The value of `metrics.vintage_holdout.logloss` is 0.02811 . | 0.02811 | ratio | metrics |  | eq | `[[art:c32e3713:metrics.vintage_holdout.logloss]]` | verified | 0.02810570342 |
| 210 | outcomes | The value of `metrics.vintage_holdout.mean_predicted` is 0.0… | 0.005647 | ratio | metrics |  | eq | `[[art:5ae28866:metrics.vintage_holdout.mean_predicted]]` | verified | 0.005646788012 |
| 211 | outcomes | The value of `metrics.vintage_holdout.n` is 32177 . | 32177 | ratio | metrics |  | eq | `[[art:37a92951:metrics.vintage_holdout.n]]` | verified | 32177 |
| 212 | outcomes | The value of `psi.f_burnout` is 0.004614 . | 0.004614 | ratio | psi |  | eq | `[[art:445ec3e0:psi.f_burnout]]` | verified | 0.004614338236 |
| 213 | outcomes | The value of `psi.f_credit_score` is 0.06189 . | 0.06189 | ratio | psi |  | eq | `[[art:5829d6ed:psi.f_credit_score]]` | verified | 0.06188985797 |
| 214 | outcomes | The value of `psi.f_incentive` is 0.0009923 . | 0.0009923 | ratio | psi |  | eq | `[[art:8075e035:psi.f_incentive]]` | verified | 0.0009922551416 |
| 215 | outcomes | The value of `psi.f_loan_age` is 0.0001994 . | 0.0001994 | ratio | psi |  | eq | `[[art:6ec631ed:psi.f_loan_age]]` | verified | 0.0001993816816 |
| 216 | outcomes | The value of `psi.f_note_rate` is 0.01371 . | 0.01371 | ratio | psi |  | eq | `[[art:63c68948:psi.f_note_rate]]` | verified | 0.01370911382 |
| 217 | outcomes | The value of `psi.f_orig_ltv` is 0.03617 . | 0.03617 | ratio | psi |  | eq | `[[art:212acb3a:psi.f_orig_ltv]]` | verified | 0.03617297258 |
| 218 | outcomes | The value of `psi.f_orig_upb_log` is 0.04817 . | 0.04817 | ratio | psi |  | eq | `[[art:75026ee2:psi.f_orig_upb_log]]` | verified | 0.04817081196 |
| 219 | outcomes | The value of `psi.f_sato` is 0.02773 . | 0.02773 | ratio | psi |  | eq | `[[art:2beb335c:psi.f_sato]]` | verified | 0.02772829856 |
| 220 | outcomes | The value of `psi.f_season_cos` is 0.0000179 . | 1.79e-05 | ratio | psi |  | eq | `[[art:cb2ce435:psi.f_season_cos]]` | verified | 1.790085913e-05 |
| 221 | outcomes | The value of `psi.f_season_sin` is 0.000002939 . | 2.939e-06 | ratio | psi |  | eq | `[[art:44d14048:psi.f_season_sin]]` | verified | 2.939045338e-06 |
| 222 | outcomes | The value of `psi.max` is 0.06189 . | 0.06189 | ratio | psi |  | eq | `[[art:c2e8c8fd:psi.max]]` | verified | 0.06188985797 |
| 223 | outcomes | The value of `psi.out_of_time.f_burnout` is 2.945 . | 2.945 | ratio | psi |  | eq | `[[art:a696b6ff:psi.out_of_time.f_burnout]]` | verified | 2.944521522 |
| 224 | outcomes | The value of `psi.out_of_time.f_credit_score` is 0.05988 . | 0.05988 | ratio | psi |  | eq | `[[art:e02f8367:psi.out_of_time.f_credit_score]]` | verified | 0.05987964443 |
| 225 | outcomes | The value of `psi.out_of_time.f_incentive` is 0.4958 . | 0.4958 | ratio | psi |  | eq | `[[art:58b6089b:psi.out_of_time.f_incentive]]` | verified | 0.4958065489 |
| 226 | outcomes | The value of `psi.out_of_time.f_loan_age` is 2.484 . | 2.484 | ratio | psi |  | eq | `[[art:eec03fdd:psi.out_of_time.f_loan_age]]` | verified | 2.483993033 |
| 227 | outcomes | The value of `psi.out_of_time.f_note_rate` is 0.6977 . | 0.6977 | ratio | psi |  | eq | `[[art:b0278c59:psi.out_of_time.f_note_rate]]` | verified | 0.6976589281 |
| 228 | outcomes | The value of `psi.out_of_time.f_orig_ltv` is 0.04301 . | 0.04301 | ratio | psi |  | eq | `[[art:3422cd60:psi.out_of_time.f_orig_ltv]]` | verified | 0.04300793312 |
| 229 | outcomes | The value of `psi.out_of_time.f_orig_upb_log` is 0.07136 . | 0.07136 | ratio | psi |  | eq | `[[art:fddf2a0a:psi.out_of_time.f_orig_upb_log]]` | verified | 0.07136421414 |
| 230 | outcomes | The value of `psi.out_of_time.f_sato` is 0.01299 . | 0.01299 | ratio | psi |  | eq | `[[art:5090c358:psi.out_of_time.f_sato]]` | verified | 0.01298850667 |
| 231 | outcomes | The value of `psi.out_of_time.f_season_cos` is 0.007524 . | 0.007524 | ratio | psi |  | eq | `[[art:3487f524:psi.out_of_time.f_season_cos]]` | verified | 0.00752368457 |
| 232 | outcomes | The value of `psi.out_of_time.f_season_sin` is 0.02789 . | 0.02789 | ratio | psi |  | eq | `[[art:eb28b9bb:psi.out_of_time.f_season_sin]]` | verified | 0.02788988464 |
| 233 | outcomes | The value of `psi.out_of_time.y_score` is 0.7056 . | 0.7056 | ratio | psi |  | eq | `[[art:2dc61374:psi.out_of_time.y_score]]` | verified | 0.7055906656 |
| 234 | outcomes | The value of `psi.vintage_holdout.f_burnout` is 0.04749 . | 0.04749 | ratio | psi |  | eq | `[[art:b76fb2b0:psi.vintage_holdout.f_burnout]]` | verified | 0.04749372789 |
| 235 | outcomes | The value of `psi.vintage_holdout.f_credit_score` is 0.03996… | 0.03996 | ratio | psi |  | eq | `[[art:abf4e0aa:psi.vintage_holdout.f_credit_score]]` | verified | 0.03995819732 |
| 236 | outcomes | The value of `psi.vintage_holdout.f_incentive` is 0.4475 . | 0.4475 | ratio | psi |  | eq | `[[art:81260b55:psi.vintage_holdout.f_incentive]]` | verified | 0.4475226601 |
| 237 | outcomes | The value of `psi.vintage_holdout.f_loan_age` is 0.07112 . | 0.07112 | ratio | psi |  | eq | `[[art:256aaeda:psi.vintage_holdout.f_loan_age]]` | verified | 0.07111526296 |
| 238 | outcomes | The value of `psi.vintage_holdout.f_note_rate` is 0.6088 . | 0.6088 | ratio | psi |  | eq | `[[art:c1ffae38:psi.vintage_holdout.f_note_rate]]` | verified | 0.608822927 |
| 239 | outcomes | The value of `psi.vintage_holdout.f_orig_ltv` is 0.02942 . | 0.02942 | ratio | psi |  | eq | `[[art:09f015f3:psi.vintage_holdout.f_orig_ltv]]` | verified | 0.0294150369 |
| 240 | outcomes | The value of `psi.vintage_holdout.f_orig_upb_log` is 0.0404… | 0.0404 | ratio | psi |  | eq | `[[art:ce7dc6c5:psi.vintage_holdout.f_orig_upb_log]]` | verified | 0.04039645306 |
| 241 | outcomes | The value of `psi.vintage_holdout.f_sato` is 0.02989 . | 0.02989 | ratio | psi |  | eq | `[[art:17126bd4:psi.vintage_holdout.f_sato]]` | verified | 0.02989256711 |
| 242 | outcomes | The value of `psi.vintage_holdout.f_season_cos` is 0.001288… | 0.001288 | ratio | psi |  | eq | `[[art:5123c902:psi.vintage_holdout.f_season_cos]]` | verified | 0.0012879007 |
| 243 | outcomes | The value of `psi.vintage_holdout.f_season_sin` is 0.0007309… | 0.0007309 | ratio | psi |  | eq | `[[art:403ec3c2:psi.vintage_holdout.f_season_sin]]` | verified | 0.0007309374015 |
| 244 | outcomes | The value of `psi.vintage_holdout.y_score` is 0.1421 . | 0.1421 | ratio | psi |  | eq | `[[art:3713457e:psi.vintage_holdout.y_score]]` | verified | 0.142110315 |
| 245 | outcomes | The value of `psi.y_score` is 0.001953 . | 0.001953 | ratio | psi |  | eq | `[[art:3b9dee2d:psi.y_score]]` | verified | 0.001952903716 |
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
| 267 | sensitivity | The value of `scenario.convexity` is -1130000 . | -1130000 | ratio | scenario |  | eq | `[[art:538e0e09:scenario.convexity]]` | verified | -1129931.654 |
| 268 | sensitivity | The value of `scenario.value_change.-100` is -322600 . | -322600 | ratio | scenario |  | eq | `[[art:d33e8e3c:scenario.value_change.-100]]` | verified | -322648.7678 |
| 269 | sensitivity | The value of `scenario.value_change.-200` is -854300 . | -854300 | ratio | scenario |  | eq | `[[art:03816874:scenario.value_change.-200]]` | verified | -854265.8614 |
| 270 | sensitivity | The value of `scenario.value_change.-300` is -1298000 . | -1298000 | ratio | scenario |  | eq | `[[art:4829926e:scenario.value_change.-300]]` | verified | -1297986.399 |
| 271 | sensitivity | The value of `scenario.value_change.0` is 0 . | 0 | ratio | scenario |  | eq | `[[art:1e1b0b88:scenario.value_change.0]]` | verified | 0 |
| 272 | sensitivity | The value of `scenario.value_change.100` is 119600 . | 119600 | ratio | scenario |  | eq | `[[art:d0970bd9:scenario.value_change.100]]` | verified | 119555.7352 |
| 273 | sensitivity | The value of `scenario.value_change.200` is 157000 . | 157000 | ratio | scenario |  | eq | `[[art:d69c2be1:scenario.value_change.200]]` | verified | 156987.0553 |
| 274 | sensitivity | The value of `scenario.value_change.300` is 168100 . | 168100 | ratio | scenario |  | eq | `[[art:38e75872:scenario.value_change.300]]` | verified | 168054.7452 |
| 275 | sensitivity | The value of `stability.f_burnout.sign_flip` is 0 . | 0 | ratio | stability |  | eq | `[[art:ffc296b7:stability.f_burnout.sign_flip]]` | verified | 0 |
| 276 | sensitivity | The value of `stability.f_credit_score.sign_flip` is 0 . | 0 | ratio | stability |  | eq | `[[art:453c8949:stability.f_credit_score.sign_flip]]` | verified | 0 |
| 277 | sensitivity | The value of `stability.f_incentive.sign_flip` is 0 . | 0 | ratio | stability |  | eq | `[[art:1e3dbc9b:stability.f_incentive.sign_flip]]` | verified | 0 |
| 278 | sensitivity | The value of `stability.f_loan_age.sign_flip` is 0 . | 0 | ratio | stability |  | eq | `[[art:02339bed:stability.f_loan_age.sign_flip]]` | verified | 0 |
| 279 | sensitivity | The value of `stability.f_note_rate.sign_flip` is 0 . | 0 | ratio | stability |  | eq | `[[art:4a9e3c32:stability.f_note_rate.sign_flip]]` | verified | 0 |
| 280 | sensitivity | The value of `stability.f_orig_ltv.sign_flip` is 0 . | 0 | ratio | stability |  | eq | `[[art:bb5e04ca:stability.f_orig_ltv.sign_flip]]` | verified | 0 |
| 281 | sensitivity | The value of `stability.f_orig_upb_log.sign_flip` is 0 . | 0 | ratio | stability |  | eq | `[[art:5a5daefb:stability.f_orig_upb_log.sign_flip]]` | verified | 0 |
| 282 | sensitivity | The value of `stability.f_sato.sign_flip` is 0 . | 0 | ratio | stability |  | eq | `[[art:a7092419:stability.f_sato.sign_flip]]` | verified | 0 |
| 283 | sensitivity | The value of `stability.f_season_cos.sign_flip` is 0 . | 0 | ratio | stability |  | eq | `[[art:4c9ae175:stability.f_season_cos.sign_flip]]` | verified | 0 |
| 284 | sensitivity | The value of `stability.f_season_sin.sign_flip` is 0 . | 0 | ratio | stability |  | eq | `[[art:3c609ed8:stability.f_season_sin.sign_flip]]` | verified | 0 |
| 285 | sensitivity | The value of `threshold.M1.condition_number` is 30 . | 30 | ratio | threshold |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 286 | sensitivity | The value of `threshold.M1.vif` is 10 . | 10 | ratio | threshold |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 287 | sensitivity | The value of `threshold.R1.auc_gap` is 0.1 . | 0.1 | ratio | threshold |  | eq | `[[art:b64213d7:threshold.R1.auc_gap]]` | verified | 0.1 |
| 288 | sensitivity | The value of `threshold.R1.sign_flip_coef` is 0.05 . | 0.05 | ratio | threshold |  | eq | `[[art:aca84377:threshold.R1.sign_flip_coef]]` | verified | 0.05 |
| 289 | sensitivity | The value of `threshold.R1.sign_flip_z` is 2 . | 2 | ratio | threshold |  | eq | `[[art:2e4428c7:threshold.R1.sign_flip_z]]` | verified | 2 |
| 290 | sensitivity | The value of `vif.f_burnout` is 3.439 . | 3.439 | ratio | vif |  | eq | `[[art:3f7564f6:vif.f_burnout]]` | verified | 3.439328594 |
| 291 | sensitivity | The value of `vif.f_credit_score` is 1.008 . | 1.008 | ratio | vif |  | eq | `[[art:59d19ea1:vif.f_credit_score]]` | verified | 1.007978309 |
| 292 | sensitivity | The value of `vif.f_incentive` is 2.226 . | 2.226 | ratio | vif |  | eq | `[[art:31179b0a:vif.f_incentive]]` | verified | 2.22632259 |
| 293 | sensitivity | The value of `vif.f_loan_age` is 2.929 . | 2.929 | ratio | vif |  | eq | `[[art:903503b0:vif.f_loan_age]]` | verified | 2.928871763 |
| 294 | sensitivity | The value of `vif.f_note_rate` is 4.976 . | 4.976 | ratio | vif |  | eq | `[[art:f6dfe789:vif.f_note_rate]]` | verified | 4.975500767 |
| 295 | sensitivity | The value of `vif.f_orig_ltv` is 1.005 . | 1.005 | ratio | vif |  | eq | `[[art:d0eadaeb:vif.f_orig_ltv]]` | verified | 1.004506143 |
| 296 | sensitivity | The value of `vif.f_orig_upb_log` is 1.006 . | 1.006 | ratio | vif |  | eq | `[[art:8b0886fe:vif.f_orig_upb_log]]` | verified | 1.005846447 |
| 297 | sensitivity | The value of `vif.f_sato` is 1.713 . | 1.713 | ratio | vif |  | eq | `[[art:9a173f4f:vif.f_sato]]` | verified | 1.71256814 |
| 298 | sensitivity | The value of `vif.f_season_cos` is 1.018 . | 1.018 | ratio | vif |  | eq | `[[art:77f16218:vif.f_season_cos]]` | verified | 1.017653349 |
| 299 | sensitivity | The value of `vif.f_season_sin` is 1.004 . | 1.004 | ratio | vif |  | eq | `[[art:3d38c119:vif.f_season_sin]]` | verified | 1.004128844 |
| 300 | sensitivity | The value of `vif.max` is 4.976 . | 4.976 | ratio | vif |  | eq | `[[art:f9e0db60:vif.max]]` | verified | 4.975500767 |
| 301 | findings | The value of `sign_check.f_note_rate.agrees` is 0 . | 0 | ratio | sign_check |  | eq | `[[art:e3173464:sign_check.f_note_rate.agrees]]` | verified | 0 |
| 302 | findings | The value of `sign_check.f_note_rate.coef_sign` is -1 . | -1 | ratio | sign_check |  | eq | `[[art:9a57eeb9:sign_check.f_note_rate.coef_sign]]` | verified | -1 |
| 303 | findings | The value of `sign_check.f_note_rate.univariate_direction` i… | 1 | ratio | sign_check |  | eq | `[[art:33e2a051:sign_check.f_note_rate.univariate_direction]]` | verified | 1 |
| 304 | monitoring | The value of `calibration_slope.test` is 0.9365 . | 0.9365 | ratio | calibration_slope |  | eq | `[[art:3e42ee62:calibration_slope.test]]` | verified | 0.9365180494 |
| 305 | monitoring | The value of `metrics.test.auc` is 0.7753 . | 0.7753 | ratio | metrics |  | eq | `[[art:57066271:metrics.test.auc]]` | verified | 0.7752553922 |
| 306 | monitoring | The value of `psi.max` is 0.06189 . | 0.06189 | ratio | psi |  | eq | `[[art:c2e8c8fd:psi.max]]` | verified | 0.06188985797 |
| 307 | monitoring | The value of `rule.calibration_first_event_rate` is 0.05 . | 0.05 | ratio | rule |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 308 | monitoring | The value of `threshold.package.auc.test.min` is 0.65 . | 0.65 | ratio | threshold |  | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 309 | monitoring | The value of `threshold.package.calibration_slope.test.max`… | 1.2 | ratio | threshold |  | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 310 | monitoring | The value of `threshold.package.calibration_slope.test.min`… | 0.8 | ratio | threshold |  | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 311 | monitoring | The value of `threshold.package.psi.max` is 0.25 . | 0.25 | ratio | threshold |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |

## Appendix B — Artifact index

The store holds 272 artifacts; the 212 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `ablation.baseline_auc` | `54367df6` | scalar | 0.7672992275 | AUC on test of a refit of the champion's functional form on every retained feature, the level each ablation delta is measured from |
| `ablation.f_burnout.delta_auc` | `4c92a645` | scalar | -0.0001876329287 | change in test AUC when the champion's form is refitted without f_burnout |
| `ablation.f_credit_score.delta_auc` | `302cee1d` | scalar | -0.0147431913 | change in test AUC when the champion's form is refitted without f_credit_score |
| `ablation.f_incentive.delta_auc` | `cc8b34d4` | scalar | -0.0411745927 | change in test AUC when the champion's form is refitted without f_incentive |
| `ablation.f_loan_age.delta_auc` | `cd3be5c5` | scalar | 0.0008165996474 | change in test AUC when the champion's form is refitted without f_loan_age |
| `ablation.f_note_rate.delta_auc` | `034cea8e` | scalar | -0.002585106068 | change in test AUC when the champion's form is refitted without f_note_rate |
| `ablation.f_orig_ltv.delta_auc` | `45bbe28a` | scalar | -0.002294407165 | change in test AUC when the champion's form is refitted without f_orig_ltv |
| `ablation.f_orig_upb_log.delta_auc` | `dbd54a4a` | scalar | -0.01926646624 | change in test AUC when the champion's form is refitted without f_orig_upb_log |
| `ablation.f_sato.delta_auc` | `452f8833` | scalar | 0.0005200867657 | change in test AUC when the champion's form is refitted without f_sato |
| `ablation.f_season_cos.delta_auc` | `f01715f5` | scalar | -0.00048256018 | change in test AUC when the champion's form is refitted without f_season_cos |
| `ablation.f_season_sin.delta_auc` | `a81a1fce` | scalar | -0.0003884794439 | change in test AUC when the champion's form is refitted without f_season_sin |
| `calibration.mean_rel_gap.out_of_time` | `c599bd89` | scalar | 0.05108730888 | mean predicted against observed on out_of_time, relative |
| `calibration.mean_rel_gap.test` | `d1b269ea` | scalar | 0.006754602373 | mean predicted against observed on test, relative |
| `calibration.mean_rel_gap.train` | `e28c45a9` | scalar | 0.01151624417 | mean predicted against observed on train, relative |
| `calibration.mean_rel_gap.vintage_holdout` | `55a672c2` | scalar | 0.1722367603 | mean predicted against observed on vintage_holdout, relative |
| `calibration.test` | `dcbc44e6` | table | table, 10 rows | calibration by decile of predicted probability on test |
| `calibration_intercept.out_of_time` | `fc7ece3a` | scalar | -0.06272473851 | logistic regression of the outcome on logit(p) on out_of_time: the intercept |
| `calibration_intercept.test` | `e87b5c13` | scalar | -0.2769708146 | logistic regression of the outcome on logit(p) on test: the intercept |
| `calibration_intercept.train` | `11d7a3ca` | scalar | -0.01453793696 | logistic regression of the outcome on logit(p) on train: the intercept |
| `calibration_intercept.vintage_holdout` | `44715143` | scalar | -0.9028328443 | logistic regression of the outcome on logit(p) on vintage_holdout: the intercept |
| `calibration_slope.out_of_time` | `a49b2789` | scalar | 0.9969389246 | logistic regression of the outcome on logit(p) on out_of_time: the slope |
| `calibration_slope.test` | `3e42ee62` | scalar | 0.9365180494 | logistic regression of the outcome on logit(p) on test: the slope |
| `calibration_slope.train` | `534cb102` | scalar | 0.9936945557 | logistic regression of the outcome on logit(p) on train: the slope |
| `calibration_slope.vintage_holdout` | `08d6b321` | scalar | 0.837279841 | logistic regression of the outcome on logit(p) on vintage_holdout: the slope |
| `challenger.auc` | `a55c39c9` | scalar | 0.6999704544 | the challenger's AUC on test |
| `challenger.brier` | `57c3e2f5` | scalar | 0.008371219123 | the challenger's Brier score on test |
| `challenger.delta_auc` | `89de5f90` | scalar | -0.07528493778 | the challenger's AUC on test minus the champion's |
| `condition_number` | `4f06a3c5` | scalar | 4.942565522 | Belsley's condition number of the column-standardised design |
| `cpr.out_of_time.mae` | `a7ecd72b` | scalar | 0.05856944955 | mean absolute difference between actual and predicted CPR on out_of_time |
| `cpr.test` | `ecbd1494` | table | table, 71 rows | actual against predicted CPR by period on test |
| `cpr.test.mae` | `ff266c97` | scalar | 0.042636033 | mean absolute difference between actual and predicted CPR on test |
| `cpr.train.mae` | `f2c3683c` | scalar | 0.02657629251 | mean absolute difference between actual and predicted CPR on train |
| `cpr.vintage_holdout.mae` | `172ebed4` | scalar | 0.0289048118 | mean absolute difference between actual and predicted CPR on vintage_holdout |
| `csi.f_burnout` | `94a1612f` | scalar | 0.0009851123767 | CSI of f_burnout: its contribution to the shift in the linear predictor |
| `csi.f_credit_score` | `70748e80` | scalar | 0.007908848663 | CSI of f_credit_score: its contribution to the shift in the linear predictor |
| `csi.f_incentive` | `ac5ee43b` | scalar | 0.005803522882 | CSI of f_incentive: its contribution to the shift in the linear predictor |
| `csi.f_loan_age` | `53ae3ece` | scalar | 0 | CSI of f_loan_age: its contribution to the shift in the linear predictor |
| `csi.f_note_rate` | `06292416` | scalar | 0.01822065751 | CSI of f_note_rate: its contribution to the shift in the linear predictor |
| `csi.f_orig_ltv` | `1f963d83` | scalar | 0.03438094941 | CSI of f_orig_ltv: its contribution to the shift in the linear predictor |
| `csi.f_orig_upb_log` | `a10d20d5` | scalar | 0.00296903904 | CSI of f_orig_upb_log: its contribution to the shift in the linear predictor |
| `csi.f_sato` | `ce21936e` | scalar | 0.001487358985 | CSI of f_sato: its contribution to the shift in the linear predictor |
| `csi.f_season_cos` | `15fe2d99` | scalar | 0.0004785421555 | CSI of f_season_cos: its contribution to the shift in the linear predictor |
| `csi.f_season_sin` | `81e8dbf0` | scalar | 7.624273793e-05 | CSI of f_season_sin: its contribution to the shift in the linear predictor |
| `csi.max` | `54bd75b0` | scalar | 0.03438094941 | the largest characteristic stability index |
| `deciles.out_of_time.top2_capture` | `df63152b` | scalar | 0.5772727273 | share of out_of_time events in the top two deciles |
| `deciles.test` | `309fa6f3` | table | table, 10 rows | decile separation on test; decile 1 holds the highest probabilities |
| `deciles.test.top2_capture` | `43c4adc5` | scalar | 0.5806451613 | share of test events in the top two deciles |
| `deciles.train.top2_capture` | `e8dd0c53` | scalar | 0.5960912052 | share of train events in the top two deciles |
| `deciles.vintage_holdout.top2_capture` | `8b59f312` | scalar | 0.5870967742 | share of vintage_holdout events in the top two deciles |
| `leakage.duplicates.train` | `4474c227` | scalar | 0 | share of train rows whose feature values are not unique within train |
| `leakage.name_screen.n_matched` | `407e62be` | scalar | 0 | feature names matching the target-adjacent lexicon |
| `leakage.overlap` | `4c9fcd09` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.features` | `0fec8048` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.ids` | `63d37fc5` | scalar | 0 | share of test rows whose ['loan_id', 'period'] also identify a row of train |
| `leakage.target_corr.max_single_feature_auc` | `1fe630dd` | scalar | 0.7238936567 | the AUC of the strongest single feature |
| `leakage.timing.n_flagged` | `742bcd24` | scalar | 0 | features declared during_period or after_outcome |
| `metrics.out_of_time.auc` | `6f2a2d99` | scalar | 0.7845616168 | auc on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.brier` | `40d244d4` | scalar | 0.0171279495 | brier on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.event_rate` | `83ccf5c0` | scalar | 0.01794892714 | event_rate on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.gini` | `890252d7` | scalar | 0.5691232337 | gini on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.ks` | `16d3e4fe` | scalar | 0.4321115953 | ks on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.logloss` | `2b7c9b2d` | scalar | 0.07975283787 | logloss on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.mean_predicted` | `3833e0c5` | scalar | 0.01886588953 | mean_predicted on out_of_time, recomputed by quaestor |
| `metrics.out_of_time.n` | `7898809e` | scalar | 12257 | n on out_of_time, recomputed by quaestor |
| `metrics.test.auc` | `57066271` | scalar | 0.7752553922 | auc on test, recomputed by quaestor |
| `metrics.test.brier` | `7d3583cd` | scalar | 0.00789356705 | brier on test, recomputed by quaestor |
| `metrics.test.event_rate` | `570cc08a` | scalar | 0.008061370433 | event_rate on test, recomputed by quaestor |
| `metrics.test.gini` | `fe7f75d7` | scalar | 0.5505107844 | gini on test, recomputed by quaestor |
| `metrics.test.ks` | `c569c301` | scalar | 0.4161772354 | ks on test, recomputed by quaestor |
| `metrics.test.logloss` | `320e4c6b` | scalar | 0.04263297829 | logloss on test, recomputed by quaestor |
| `metrics.test.mean_predicted` | `3bc93911` | scalar | 0.008115821785 | mean_predicted on test, recomputed by quaestor |
| `metrics.test.n` | `e55953e1` | scalar | 15382 | n on test, recomputed by quaestor |
| `metrics.train.auc` | `fa609ae1` | scalar | 0.7883327303 | auc on train, recomputed by quaestor |
| `metrics.train.brier` | `83666c70` | scalar | 0.008317491392 | brier on train, recomputed by quaestor |
| `metrics.train.event_rate` | `b9ef3327` | scalar | 0.008524699414 | event_rate on train, recomputed by quaestor |
| `metrics.train.gini` | `0b6b2058` | scalar | 0.5766654607 | gini on train, recomputed by quaestor |
| `metrics.train.ks` | `c355478b` | scalar | 0.4562056834 | ks on train, recomputed by quaestor |
| `metrics.train.logloss` | `199c7db5` | scalar | 0.04408402922 | logloss on train, recomputed by quaestor |
| `metrics.train.mean_predicted` | `a63f6555` | scalar | 0.008426526894 | mean_predicted on train, recomputed by quaestor |
| `metrics.train.n` | `6fdfeabb` | scalar | 36013 | n on train, recomputed by quaestor |
| `metrics.vintage_holdout.auc` | `ac6794c5` | scalar | 0.7717974135 | auc on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.brier` | `f3c6bdcc` | scalar | 0.004763025704 | brier on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.event_rate` | `e3590a16` | scalar | 0.004817105386 | event_rate on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.gini` | `a4a532f0` | scalar | 0.5435948269 | gini on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.ks` | `b5b9e888` | scalar | 0.4515647508 | ks on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.logloss` | `c32e3713` | scalar | 0.02810570342 | logloss on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.mean_predicted` | `5ae28866` | scalar | 0.005646788012 | mean_predicted on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.n` | `37a92951` | scalar | 32177 | n on vintage_holdout, recomputed by quaestor |
| `profile.out_of_time.missing.max` | `4dafce11` | scalar | 0 | the largest missing fraction in out_of_time |
| `profile.out_of_time.n` | `fa39c5cf` | scalar | 12257 | rows in out_of_time |
| `profile.test.missing.max` | `f813848d` | scalar | 0 | the largest missing fraction in test |
| `profile.test.n` | `e3abc1b8` | scalar | 15382 | rows in test |
| `profile.train.missing.max` | `050a3099` | scalar | 0 | the largest missing fraction in train |
| `profile.train.n` | `c5ebd9c9` | scalar | 36013 | rows in train |
| `profile.vintage_holdout.missing.max` | `329bb430` | scalar | 0 | the largest missing fraction in vintage_holdout |
| `profile.vintage_holdout.n` | `426e712a` | scalar | 32177 | rows in vintage_holdout |
| `psi.f_burnout` | `445ec3e0` | scalar | 0.004614338236 | PSI of f_burnout between train and test |
| `psi.f_credit_score` | `5829d6ed` | scalar | 0.06188985797 | PSI of f_credit_score between train and test |
| `psi.f_incentive` | `8075e035` | scalar | 0.0009922551416 | PSI of f_incentive between train and test |
| `psi.f_loan_age` | `6ec631ed` | scalar | 0.0001993816816 | PSI of f_loan_age between train and test |
| `psi.f_note_rate` | `63c68948` | scalar | 0.01370911382 | PSI of f_note_rate between train and test |
| `psi.f_orig_ltv` | `212acb3a` | scalar | 0.03617297258 | PSI of f_orig_ltv between train and test |
| `psi.f_orig_upb_log` | `75026ee2` | scalar | 0.04817081196 | PSI of f_orig_upb_log between train and test |
| `psi.f_sato` | `2beb335c` | scalar | 0.02772829856 | PSI of f_sato between train and test |
| `psi.f_season_cos` | `cb2ce435` | scalar | 1.790085913e-05 | PSI of f_season_cos between train and test |
| `psi.f_season_sin` | `44d14048` | scalar | 2.939045338e-06 | PSI of f_season_sin between train and test |
| `psi.max` | `c2e8c8fd` | scalar | 0.06188985797 | the largest train-to-test PSI, score included |
| `psi.out_of_time.f_burnout` | `a696b6ff` | scalar | 2.944521522 | PSI of f_burnout between train and out_of_time |
| `psi.out_of_time.f_credit_score` | `e02f8367` | scalar | 0.05987964443 | PSI of f_credit_score between train and out_of_time |
| `psi.out_of_time.f_incentive` | `58b6089b` | scalar | 0.4958065489 | PSI of f_incentive between train and out_of_time |
| `psi.out_of_time.f_loan_age` | `eec03fdd` | scalar | 2.483993033 | PSI of f_loan_age between train and out_of_time |
| `psi.out_of_time.f_note_rate` | `b0278c59` | scalar | 0.6976589281 | PSI of f_note_rate between train and out_of_time |
| `psi.out_of_time.f_orig_ltv` | `3422cd60` | scalar | 0.04300793312 | PSI of f_orig_ltv between train and out_of_time |
| `psi.out_of_time.f_orig_upb_log` | `fddf2a0a` | scalar | 0.07136421414 | PSI of f_orig_upb_log between train and out_of_time |
| `psi.out_of_time.f_sato` | `5090c358` | scalar | 0.01298850667 | PSI of f_sato between train and out_of_time |
| `psi.out_of_time.f_season_cos` | `3487f524` | scalar | 0.00752368457 | PSI of f_season_cos between train and out_of_time |
| `psi.out_of_time.f_season_sin` | `eb28b9bb` | scalar | 0.02788988464 | PSI of f_season_sin between train and out_of_time |
| `psi.out_of_time.y_score` | `2dc61374` | scalar | 0.7055906656 | PSI of the score between train and out_of_time |
| `psi.vintage_holdout.f_burnout` | `b76fb2b0` | scalar | 0.04749372789 | PSI of f_burnout between train and vintage_holdout |
| `psi.vintage_holdout.f_credit_score` | `abf4e0aa` | scalar | 0.03995819732 | PSI of f_credit_score between train and vintage_holdout |
| `psi.vintage_holdout.f_incentive` | `81260b55` | scalar | 0.4475226601 | PSI of f_incentive between train and vintage_holdout |
| `psi.vintage_holdout.f_loan_age` | `256aaeda` | scalar | 0.07111526296 | PSI of f_loan_age between train and vintage_holdout |
| `psi.vintage_holdout.f_note_rate` | `c1ffae38` | scalar | 0.608822927 | PSI of f_note_rate between train and vintage_holdout |
| `psi.vintage_holdout.f_orig_ltv` | `09f015f3` | scalar | 0.0294150369 | PSI of f_orig_ltv between train and vintage_holdout |
| `psi.vintage_holdout.f_orig_upb_log` | `ce7dc6c5` | scalar | 0.04039645306 | PSI of f_orig_upb_log between train and vintage_holdout |
| `psi.vintage_holdout.f_sato` | `17126bd4` | scalar | 0.02989256711 | PSI of f_sato between train and vintage_holdout |
| `psi.vintage_holdout.f_season_cos` | `5123c902` | scalar | 0.0012879007 | PSI of f_season_cos between train and vintage_holdout |
| `psi.vintage_holdout.f_season_sin` | `403ec3c2` | scalar | 0.0007309374015 | PSI of f_season_sin between train and vintage_holdout |
| `psi.vintage_holdout.y_score` | `3713457e` | scalar | 0.142110315 | PSI of the score between train and vintage_holdout |
| `psi.y_score` | `3b9dee2d` | scalar | 0.001952903716 | PSI of the score between train and test |
| `rule.calibration_first_event_rate` | `42f1351e` | scalar | 0.05 | the event rate below which the report puts calibration before discrimination |
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |
| `scenario.convexity` | `538e0e09` | scalar | -1129931.654 | the value change at -300 bp plus the change at 300 bp; negative when the fall outweighs the rise |
| `scenario.value_by_shock` | `1143879d` | table | table, 7 rows | servicing value, its change from the base case and first-year CPR, by shock |
| `scenario.value_change.-100` | `d33e8e3c` | scalar | -322648.7678 | change in servicing value at -100 bp |
| `scenario.value_change.-200` | `03816874` | scalar | -854265.8614 | change in servicing value at -200 bp |
| `scenario.value_change.-300` | `4829926e` | scalar | -1297986.399 | change in servicing value at -300 bp |
| `scenario.value_change.0` | `1e1b0b88` | scalar | 0 | change in servicing value at 0 bp |
| `scenario.value_change.100` | `d0970bd9` | scalar | 119555.7352 | change in servicing value at 100 bp |
| `scenario.value_change.200` | `d69c2be1` | scalar | 156987.0553 | change in servicing value at 200 bp |
| `scenario.value_change.300` | `38e75872` | scalar | 168054.7452 | change in servicing value at 300 bp |
| `sign_check.f_burnout.agrees` | `a7b47126` | scalar | 1 | 1 when the fitted sign on f_burnout agrees with its univariate direction, 0 when it does not |
| `sign_check.f_burnout.coef_sign` | `434a2eb4` | scalar | 1 | the sign of the fitted coefficient on f_burnout |
| `sign_check.f_burnout.univariate_direction` | `6c04f9a3` | scalar | 1 | the sign of f_burnout's own single-feature AUC on train minus 0.5 |
| `sign_check.f_credit_score.agrees` | `6a693a4d` | scalar | 1 | 1 when the fitted sign on f_credit_score agrees with its univariate direction, 0 when it does not |
| `sign_check.f_credit_score.coef_sign` | `4893edbf` | scalar | 1 | the sign of the fitted coefficient on f_credit_score |
| `sign_check.f_credit_score.univariate_direction` | `5364f2d9` | scalar | 1 | the sign of f_credit_score's own single-feature AUC on train minus 0.5 |
| `sign_check.f_incentive.agrees` | `aab920d4` | scalar | 1 | 1 when the fitted sign on f_incentive agrees with its univariate direction, 0 when it does not |
| `sign_check.f_incentive.coef_sign` | `34fbc238` | scalar | 1 | the sign of the fitted coefficient on f_incentive |
| `sign_check.f_incentive.univariate_direction` | `284b2d7c` | scalar | 1 | the sign of f_incentive's own single-feature AUC on train minus 0.5 |
| `sign_check.f_note_rate.agrees` | `e3173464` | scalar | 0 | 1 when the fitted sign on f_note_rate agrees with its univariate direction, 0 when it does not |
| `sign_check.f_note_rate.coef_sign` | `9a57eeb9` | scalar | -1 | the sign of the fitted coefficient on f_note_rate |
| `sign_check.f_note_rate.univariate_direction` | `33e2a051` | scalar | 1 | the sign of f_note_rate's own single-feature AUC on train minus 0.5 |
| `sign_check.f_orig_ltv.agrees` | `56d6495e` | scalar | 1 | 1 when the fitted sign on f_orig_ltv agrees with its univariate direction, 0 when it does not |
| `sign_check.f_orig_ltv.coef_sign` | `eb67b95a` | scalar | -1 | the sign of the fitted coefficient on f_orig_ltv |
| `sign_check.f_orig_ltv.univariate_direction` | `1883c240` | scalar | -1 | the sign of f_orig_ltv's own single-feature AUC on train minus 0.5 |
| `sign_check.f_orig_upb_log.agrees` | `57b59c6a` | scalar | 1 | 1 when the fitted sign on f_orig_upb_log agrees with its univariate direction, 0 when it does not |
| `sign_check.f_orig_upb_log.coef_sign` | `5165217f` | scalar | 1 | the sign of the fitted coefficient on f_orig_upb_log |
| `sign_check.f_orig_upb_log.univariate_direction` | `901ddb38` | scalar | 1 | the sign of f_orig_upb_log's own single-feature AUC on train minus 0.5 |
| `sign_check.f_sato.agrees` | `44052838` | scalar | 1 | 1 when the fitted sign on f_sato agrees with its univariate direction, 0 when it does not |
| `sign_check.f_sato.coef_sign` | `55450fdb` | scalar | 1 | the sign of the fitted coefficient on f_sato |
| `sign_check.f_sato.univariate_direction` | `5cc2f196` | scalar | 1 | the sign of f_sato's own single-feature AUC on train minus 0.5 |
| `sign_check.f_season_cos.agrees` | `e02a4777` | scalar | 1 | 1 when the fitted sign on f_season_cos agrees with its univariate direction, 0 when it does not |
| `sign_check.f_season_cos.coef_sign` | `25dfa200` | scalar | -1 | the sign of the fitted coefficient on f_season_cos |
| `sign_check.f_season_cos.univariate_direction` | `7f6fd623` | scalar | -1 | the sign of f_season_cos's own single-feature AUC on train minus 0.5 |
| `sign_check.f_season_sin.agrees` | `caceebf9` | scalar | 1 | 1 when the fitted sign on f_season_sin agrees with its univariate direction, 0 when it does not |
| `sign_check.f_season_sin.coef_sign` | `a6b9d22d` | scalar | 1 | the sign of the fitted coefficient on f_season_sin |
| `sign_check.f_season_sin.univariate_direction` | `8a2dc987` | scalar | 1 | the sign of f_season_sin's own single-feature AUC on train minus 0.5 |
| `sign_check.n_disagreements` | `f96ece96` | scalar | 1 | retained features whose fitted sign contradicts their univariate direction, of 9 checked |
| `stability.auc_by_regime` | `960f708f` | table | table, 2 rows | the champion's AUC within each rate_regime on train |
| `stability.f_burnout.sign_flip` | `ffc296b7` | scalar | 0 | 1 when f_burnout is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.f_credit_score.sign_flip` | `453c8949` | scalar | 0 | 1 when f_credit_score is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.f_incentive.sign_flip` | `1e3dbc9b` | scalar | 0 | 1 when f_incentive is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.f_loan_age.sign_flip` | `02339bed` | scalar | 0 | 1 when f_loan_age is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.f_note_rate.sign_flip` | `4a9e3c32` | scalar | 0 | 1 when f_note_rate is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.f_orig_ltv.sign_flip` | `bb5e04ca` | scalar | 0 | 1 when f_orig_ltv is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.f_orig_upb_log.sign_flip` | `5a5daefb` | scalar | 0 | 1 when f_orig_upb_log is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.f_sato.sign_flip` | `a7092419` | scalar | 0 | 1 when f_sato is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.f_season_cos.sign_flip` | `4c9ae175` | scalar | 0 | 1 when f_season_cos is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
| `stability.f_season_sin.sign_flip` | `3c609ed8` | scalar | 0 | 1 when f_season_sin is among the top 10 features and changes sign across regimes with a coefficient above 0.05 and a \|z\| of at least 2.0 in each |
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
| `thresholds.evaluation` | `f71ddec9` | table | table, 4 rows | every threshold package.yaml declares, with its bound, the recomputed value and the outcome |
| `vif.f_burnout` | `3f7564f6` | scalar | 3.439328594 | variance inflation factor of f_burnout on train |
| `vif.f_credit_score` | `59d19ea1` | scalar | 1.007978309 | variance inflation factor of f_credit_score on train |
| `vif.f_incentive` | `31179b0a` | scalar | 2.22632259 | variance inflation factor of f_incentive on train |
| `vif.f_loan_age` | `903503b0` | scalar | 2.928871763 | variance inflation factor of f_loan_age on train |
| `vif.f_note_rate` | `f6dfe789` | scalar | 4.975500767 | variance inflation factor of f_note_rate on train |
| `vif.f_orig_ltv` | `d0eadaeb` | scalar | 1.004506143 | variance inflation factor of f_orig_ltv on train |
| `vif.f_orig_upb_log` | `8b0886fe` | scalar | 1.005846447 | variance inflation factor of f_orig_upb_log on train |
| `vif.f_sato` | `9a173f4f` | scalar | 1.71256814 | variance inflation factor of f_sato on train |
| `vif.f_season_cos` | `77f16218` | scalar | 1.017653349 | variance inflation factor of f_season_cos on train |
| `vif.f_season_sin` | `3d38c119` | scalar | 1.004128844 | variance inflation factor of f_season_sin on train |
| `vif.max` | `f9e0db60` | scalar | 4.975500767 | the largest variance inflation factor |

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
| wall-clock (s) | 1.71 |
| subject run (s) | 2.47 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | fake |
| model | none: no model answered |
| run id | msr_prepayment-rules_only-20260918T065309Z-568d25f5 |

## Appendix D — Not checked

| item | reason |
|---|---|
| developer claims (T1, claim channel) | The package declares 3 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
| drafted narrative and the repair loop | `rules_only` calls no model; the narrative is a template |
