---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: full_agent
model: claude-opus-5[1m]
run_id: credit_default-full_agent-20260920T080337Z-e2e51e00
data_mode: synthetic
synthetic_n: 5000
grounding_precision_pre: 0.9840
grounding_precision_post: 1.0000
n_claims: 310
n_findings_by_severity: {high: 0, medium: 1, low: 1, info: 0}
generated: "2026-09-20T08:03:37Z"
illustrative: false
---

# Validation report — `credit_default` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `credit_default` v1.0 | `full_agent` | claude-opus-5[1m] | synthetic, n = 5000 | 0.9840 → 1.0000 | 0 / 1 / 1 / 0 |
<!-- quaestor:renderer:end -->

The model package credit_default version 1.0 is a credit default model that predicts the probability of borrower default, and this report follows the structure of the Federal Reserve's model risk management guidance on validation and monitoring [[reg:SR26-2:V]].

The subject was executed under a declared wall-clock cap of 300 [[art:2ad8d1a5:runtime.max_seconds]] seconds, and its outputs were recomputed independently on both splits.
The training split holds 3500 [[art:2510d49d:profile.train.n]] rows and the test split holds 1500 [[art:2193cf5f:profile.test.n]] rows, matching the row counts over which the metrics were recomputed, 3500 [[art:564683ee:metrics.train.n]] and 1500 [[art:64fcf14d:metrics.test.n]] respectively.
The event rate is close between the two splits, at 0.2246 [[art:133a5ff8:metrics.train.event_rate]] on train and 0.2247 [[art:9209d200:metrics.test.event_rate]] on test.

The model passes every developer-declared threshold recomputed here.
Discrimination on test is 0.7505 [[art:3bbb3e37:metrics.test.auc]], above the declared floor of 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]].
The Brier score on test is 0.1486 [[art:08bbf5ff:metrics.test.brier]], below the declared ceiling of 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]].
The calibration slope on test is 0.9988 [[art:6d8bca25:calibration_slope.test]], inside the declared band running from 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] to 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]], and the corresponding slope on train is 1.005 [[art:79d5244e:calibration_slope.train]].
The largest train-to-test population stability index, score included, is 0.01372 [[art:d34e2b0f:psi.max]], below the declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]], and the largest characteristic stability index is 0.0237 [[art:aa2ba789:csi.max]].

Supporting test-split measures are a Gini of 0.5009 [[art:1456c955:metrics.test.gini]], a Kolmogorov-Smirnov statistic of 0.4317 [[art:414deaff:metrics.test.ks]], a log loss of 0.467 [[art:dee4fde4:metrics.test.logloss]] and a mean predicted probability of 0.2215 [[art:461086da:metrics.test.mean_predicted]], against train values of 0.7607 [[art:9b2be514:metrics.train.auc]] for AUC, 0.5215 [[art:94b21017:metrics.train.gini]] for Gini, 0.4489 [[art:a3928b90:metrics.train.ks]] for the Kolmogorov-Smirnov statistic, 0.1486 [[art:2fe86f99:metrics.train.brier]] for Brier, 0.464 [[art:522ccdcf:metrics.train.logloss]] for log loss and 0.2246 [[art:4103f0d8:metrics.train.mean_predicted]] for mean predicted probability.
Discrimination on test sits below discrimination on train, and the two log loss values are close to one another.

Discrimination is uneven across the sub-populations examined on test.
On the above-median utilisation slice, which holds 750 [[art:ea5b0084:metrics.test.sub.utilisation_high.n]] rows and a share of 0.5 [[art:9404484e:metrics.test.sub.utilisation_high.share]] of test, AUC is 0.5721 [[art:218a0547:metrics.test.sub.utilisation_high.auc]], falling below AUC on all of test by 0.1783 [[art:951b2d25:metrics.test.sub.utilisation_high.auc_gap]].
On the below-median utilisation slice, of the same size at 750 [[art:5b0bae29:metrics.test.sub.utilisation_low.n]] rows and a share of 0.5 [[art:7860a748:metrics.test.sub.utilisation_low.share]], AUC is 0.8998 [[art:024542ae:metrics.test.sub.utilisation_low.auc]], standing above AUC on all of test, a relation recorded as a gap of -0.1493 [[art:70a562d2:metrics.test.sub.utilisation_low.auc_gap]].
On the above-median delinquency slice, which holds 339 [[art:04716bec:metrics.test.sub.delinq_last_high.n]] rows and a share of 0.226 [[art:e795e8a9:metrics.test.sub.delinq_last_high.share]] of test, AUC is 0.5882 [[art:18b3a939:metrics.test.sub.delinq_last_high.auc]], falling below AUC on all of test by 0.1622 [[art:509039a7:metrics.test.sub.delinq_last_high.auc_gap]]; comparing the two shortfalls as absolute differences from the whole-test figure, the utilisation shortfall is the larger of the two.
On the same slices the Brier score is 0.1942 [[art:c584f815:metrics.test.sub.utilisation_high.brier]], 0.1031 [[art:39a0bd66:metrics.test.sub.utilisation_low.brier]] and 0.2545 [[art:52704467:metrics.test.sub.delinq_last_high.brier]], and log loss is 0.5853 [[art:b9f7b201:metrics.test.sub.utilisation_high.logloss]], 0.3486 [[art:896b4831:metrics.test.sub.utilisation_low.logloss]] and 0.711 [[art:9c722397:metrics.test.sub.delinq_last_high.logloss]].
Mean predicted against observed, taken as a relative gap, is 0.01696 [[art:5d3f4d10:metrics.test.sub.utilisation_high.mean_rel_gap]] on the above-median utilisation slice, 0.01119 [[art:088b852d:metrics.test.sub.utilisation_low.mean_rel_gap]] on the below-median utilisation slice and 0.08419 [[art:30d42145:metrics.test.sub.delinq_last_high.mean_rel_gap]] on the above-median delinquency slice, the last of these the furthest from agreement of the three on that relative comparison.
The observed event rate on those slices is 0.2333 [[art:8e66209c:metrics.test.sub.utilisation_high.event_rate]], 0.216 [[art:b0ad49be:metrics.test.sub.utilisation_low.event_rate]] and 0.5103 [[art:c9cb7610:metrics.test.sub.delinq_last_high.event_rate]], against mean predicted probabilities of 0.2294 [[art:baa1ca0c:metrics.test.sub.utilisation_high.mean_predicted]], 0.2136 [[art:3da81c7f:metrics.test.sub.utilisation_low.mean_predicted]] and 0.4674 [[art:281b9e4c:metrics.test.sub.delinq_last_high.mean_predicted]], with slice Gini at 0.1442 [[art:cc2438a9:metrics.test.sub.utilisation_high.gini]], 0.7996 [[art:39c7fd9b:metrics.test.sub.utilisation_low.gini]] and 0.1765 [[art:18db302d:metrics.test.sub.delinq_last_high.gini]] and slice Kolmogorov-Smirnov at 0.1491 [[art:9b8e4cad:metrics.test.sub.utilisation_high.ks]], 0.7642 [[art:0be83ffa:metrics.test.sub.utilisation_low.ks]] and 0.1701 [[art:cb7c41a9:metrics.test.sub.delinq_last_high.ks]].

The design matrix diagnostics show a Belsley condition number of 1023 [[art:36c154df:condition_number]] on the column-standardised design and a largest variance inflation factor of 121900 [[art:e6655d27:vif.max]].
On effective challenge, the challenger's AUC on test exceeds the champion's by 0.07444 [[art:d7dbe8ff:challenger.delta_auc]], the kind of deviation from expected performance that the guidance treats as a prompt to consider adjustment, recalibration or redevelopment [[reg:SR26-2:V.1.b]].

This validation raised F-001, a M1 collinearity finding at medium severity, and F-002, a E1 effective challenge finding at low severity.
Each is written out in full in the findings section of this report.

## 2. Conceptual soundness

Design, construction and developmental evidence are assessed here through interpretability measures and benchmarking against an alternative model, the practical instruments the guidance points to when theoretical construction alone is not the binding question [[reg:SR26-2:V.1.a]].

The champion is a single scoring equation linear in the log-odds, one coefficient per retained feature, with an intercept of -1.4 [[art:f2e0e9a7:run.model_summary#intercept]] fitted on 3500 [[art:f2e0e9a7:run.model_summary#n_train]] training rows.
It carries 13 [[art:f79bb8bb:run.features#n]] features into the score.
Of those, 2 [[art:f79bb8bb:run.features#at_origination]] are known at origination and 11 [[art:f79bb8bb:run.features#before_period_start]] are known before the performance period opens.
Features first observable only inside the performance period number 0 [[art:f79bb8bb:run.features#during_period]], and features observable only after the outcome number 0 [[art:f79bb8bb:run.features#after_outcome]].
On that timing evidence every input is available at the moment a score would be produced, which is the design property a credit application model needs.

The model's own feature screen is a collinearity screen run at a variance-inflation threshold of 10 [[art:f2e0e9a7:run.model_summary#vif_threshold]], and the retained set above is what survived it.
That screen left in place both a raw last-bill term and an adjusted version of the same last-bill quantity, whose fitted coefficients are -0.5348 [[art:f2e0e9a7:run.model_summary#coefficients.bill_last.value]] and -0.5619 [[art:f2e0e9a7:run.model_summary#coefficients.bill_last_adj.value]], close to each other in size and alike in direction.
A validator should read the two as near-duplicate inputs whose individual weights are therefore weakly identified, even though the screen at that threshold admitted them.

The largest weight in the equation is on the most recent delinquency state, at 0.7357 [[art:f2e0e9a7:run.model_summary#coefficients.delinq_last.value]].
Next is the six-month mean bill level, at 0.6805 [[art:f2e0e9a7:run.model_summary#coefficients.bill_mean_6m.value]], followed by the adjusted and raw last-bill terms cited above and by the six-month mean payment ratio at -0.3621 [[art:f2e0e9a7:run.model_summary#coefficients.pay_ratio_mean_6m.value]].
The remaining weights are smaller: current utilisation at 0.164 [[art:f2e0e9a7:run.model_summary#coefficients.utilisation.value]], six-month mean utilisation at 0.1425 [[art:f2e0e9a7:run.model_summary#coefficients.utilisation_mean_6m.value]], the six-month delinquency count at 0.1219 [[art:f2e0e9a7:run.model_summary#coefficients.delinq_count_6m.value]], the credit limit at 0.1149 [[art:f2e0e9a7:run.model_summary#coefficients.limit_bal.value]], the last payment ratio at 0.1093 [[art:f2e0e9a7:run.model_summary#coefficients.pay_ratio_last.value]], age at -0.06716 [[art:f2e0e9a7:run.model_summary#coefficients.age.value]], the six-month maximum delinquency at -0.03224 [[art:f2e0e9a7:run.model_summary#coefficients.delinq_max_6m.value]] and the six-month bill trend at -0.02402 [[art:f2e0e9a7:run.model_summary#coefficients.bill_trend_6m.value]].
On subject matter grounds the directions that a credit reviewer would expect are present in the largest terms: recent delinquency pushes the score toward default, higher utilisation does the same, a higher sustained payment ratio pulls it away, and older borrowers score safer.
The credit-limit weight runs the other way from the usual expectation that larger lines are extended to stronger borrowers, the last-payment-ratio weight runs the other way from the expectation that paying more of the bill reduces risk, and the six-month maximum delinquency carries a protective weight where a reviewer would expect an adverse one.

The fitted signs were compared against each feature's own single-feature direction on train, and the fitted sign contradicts that direction for 4 [[art:b9e93d79:sign_check.n_disagreements]] of the retained features.
These comparisons and the refit-without-feature evidence below are developmental evidence for the judgement in this section, and no rule is applied to either, so nothing in this paragraph or the next is a finding.
The level each refit is measured from is a test AUC of 0.7505 [[art:2166cf12:ablation.baseline_auc]], and a negative change means dropping the feature cost discrimination while a positive change means dropping it did not.

On the credit limit the fitted sign is 1 [[art:6af6aef2:sign_check.limit_bal.coef_sign]] against a univariate direction of -1 [[art:56d284d6:sign_check.limit_bal.univariate_direction]], recorded as a disagreement at 0 [[art:0278aad1:sign_check.limit_bal.agrees]]; refitting without it changes test AUC by 0.0001786 [[art:6bf0f1c3:ablation.limit_bal.delta_auc]], so the reversal sits on a feature the model is not leaning on.
On the last payment ratio the fitted sign is 1 [[art:f018263e:sign_check.pay_ratio_last.coef_sign]] against a univariate direction of -1 [[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]], recorded as a disagreement at 0 [[art:79abee77:sign_check.pay_ratio_last.agrees]]; refitting without it changes test AUC by 0.002437 [[art:9639fcbd:ablation.pay_ratio_last.delta_auc]], again in the direction of no loss.
On the six-month maximum delinquency the fitted sign is -1 [[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]] against a univariate direction of 1 [[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]], recorded as a disagreement at 0 [[art:c946359c:sign_check.delinq_max_6m.agrees]]; refitting without it changes test AUC by 0.0003572 [[art:16dcea2b:ablation.delinq_max_6m.delta_auc]].
On the six-month mean bill level the fitted sign is 1 [[art:a457c04a:sign_check.bill_mean_6m.coef_sign]] against a univariate direction of -1 [[art:23b89c5d:sign_check.bill_mean_6m.univariate_direction]], recorded as a disagreement at 0 [[art:4df8b747:sign_check.bill_mean_6m.agrees]]; refitting without it changes test AUC by -0.0002909 [[art:52f6233e:ablation.bill_mean_6m.delta_auc]], so this is the one reversal that sits on a term the refit does draw discrimination from, and it is also the second largest weight in the equation.
That combination — a large weight, a sign opposed to the feature's own direction, and a small but negative refit change — is the signature of a suppressor acting against the near-duplicate last-bill terms rather than of an independently interpretable bill effect.

The remaining features agree with their own directions: recent delinquency at 1 [[art:a8ba9372:sign_check.delinq_last.agrees]], the delinquency count at 1 [[art:a337d16b:sign_check.delinq_count_6m.agrees]], current utilisation at 1 [[art:d0c9a130:sign_check.utilisation.agrees]], mean utilisation at 1 [[art:c2848161:sign_check.utilisation_mean_6m.agrees]], the mean payment ratio at 1 [[art:7e9a76ca:sign_check.pay_ratio_mean_6m.agrees]], age at 1 [[art:4116add1:sign_check.age.agrees]], the bill trend at 1 [[art:ff3cb24a:sign_check.bill_trend_6m.agrees]], the raw last bill at 1 [[art:98c00451:sign_check.bill_last.agrees]] and the adjusted last bill at 1 [[art:fb9031bc:sign_check.bill_last_adj.agrees]].
The refit evidence puts almost all of the discrimination in one place: dropping the most recent delinquency state changes test AUC by -0.07782 [[art:8eca80c6:ablation.delinq_last.delta_auc]], while dropping mean utilisation changes it by -0.0005231 [[art:c63504c6:ablation.utilisation_mean_6m.delta_auc]], age by -0.0004261 [[art:4bde085d:ablation.age.delta_auc]] and current utilisation by -0.0003113 [[art:90093ed9:ablation.utilisation.delta_auc]].
Dropping the mean payment ratio changes it by 0.007333 [[art:5e7307e8:ablation.pay_ratio_mean_6m.delta_auc]], the delinquency count by 0.001526 [[art:5da50826:ablation.delinq_count_6m.delta_auc]], the bill trend by 0.0002526 [[art:994f00bc:ablation.bill_trend_6m.delta_auc]], the raw last bill by 0.0001786 [[art:eea44d10:ablation.bill_last.delta_auc]] and the adjusted last bill by 1.531e-05 [[art:8e9d6dcc:ablation.bill_last_adj.delta_auc]].
A design in which one input carries a refit change of -0.07782 [[art:8eca80c6:ablation.delinq_last.delta_auc]] and every other input changes test AUC by a far smaller amount in either direction is, in substance, close to a one-variable model wrapped in a wider specification.

The effective challenge is a gradient-boosted challenger fitted for comparison against the champion on the same test split.
The challenger reaches an AUC of 0.8249 [[art:9727c6a9:challenger.auc]] against the champion's 0.7505 [[art:3bbb3e37:metrics.test.auc]], a lead recorded as 0.07444 [[art:d7dbe8ff:challenger.delta_auc]].
The bound that decides whether such a lead matters is an effective-challenge threshold of 0.03 [[art:e042774c:threshold.E1.delta_auc]], and the observed lead is above it.
The same ordering holds on calibration loss, where the challenger's Brier score of 0.1242 [[art:79d61058:challenger.brier]] is below the champion's 0.1486 [[art:08bbf5ff:metrics.test.brier]], the lower score being the better of the two; that comparison is stated as a difference in level, and no ratio between the two is asserted here.
Because a flexible challenger recovers discrimination the linear-in-log-odds champion does not, this is evidence about the champion's functional form rather than about any single input, and it is raised as finding E1 and reported in full in the findings section.
The sign reversals and the concentration of discrimination described above are not findings and are left to the findings section's open items, read against the expectations of subject matter direction rather than against any declared bound.

## 3. Data integrity and drift

Sound development practice includes a critical assessment of data quality, relevance, and inputs, and the evidence below is reviewed in that light [[reg:SR26-2:IV.1]].

### Missingness

The training split holds 3500 [[art:2510d49d:profile.train.n]] rows and the test split holds 1500 [[art:2193cf5f:profile.test.n]] rows.
The worst-affected column in train carries a missing fraction of 0 [[art:050a3099:profile.train.missing.max]], and the worst-affected column in test carries a missing fraction of 0 [[art:f813848d:profile.test.missing.max]].
The split-to-split missingness gap is bounded at 0.1 [[art:9cce25ea:threshold.D1.missing_gap]], and taken as a difference the comparison between the splits stays within that bound, since neither split records any missingness at its most affected column.
Taken as a ratio the same comparison has no informative denominator, because the train maximum sits at 0 [[art:050a3099:profile.train.missing.max]].

### Population and characteristic stability

Population stability between train and test is bounded at 0.25 [[art:278b9016:threshold.S1.psi]], the same value the package declares at 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
The largest train-to-test population stability index, the score included, is 0.01372 [[art:d34e2b0f:psi.max]], which is below that bound and well inside it.
That maximum is attributable to the adjusted last-bill feature at 0.01372 [[art:e87eb6d6:psi.bill_last_adj]].
The per-feature values, and the score, are as follows.

- age: 0.008124 [[art:f9255a0a:psi.age]]
- bill_last: 0.01302 [[art:cd0c79c3:psi.bill_last]]
- bill_last_adj: 0.01372 [[art:e87eb6d6:psi.bill_last_adj]]
- bill_mean_6m: 0.007124 [[art:028e4281:psi.bill_mean_6m]]
- bill_trend_6m: 0.00958 [[art:c247a6f2:psi.bill_trend_6m]]
- delinq_count_6m: 0.002069 [[art:61491d02:psi.delinq_count_6m]]
- delinq_last: 0.00285 [[art:03bd52e7:psi.delinq_last]]
- delinq_max_6m: 0.005498 [[art:7a82e7f3:psi.delinq_max_6m]]
- limit_bal: 0.01095 [[art:601cdba2:psi.limit_bal]]
- pay_ratio_last: 0.004966 [[art:3af2ca29:psi.pay_ratio_last]]
- pay_ratio_mean_6m: 0.0055 [[art:2c5baeb2:psi.pay_ratio_mean_6m]]
- utilisation: 0.004244 [[art:451e0780:psi.utilisation]]
- utilisation_mean_6m: 0.002875 [[art:d562032d:psi.utilisation_mean_6m]]
- score: 0.004589 [[art:8d23655e:psi.y_score]]

Every feature listed, and the score at 0.004589 [[art:8d23655e:psi.y_score]], sits below the bound of 0.25 [[art:278b9016:threshold.S1.psi]].
The score shift is smaller than the largest feature shift, so the movement in the output distribution is not being driven by any one input moving further than the rest.

Characteristic stability decomposes the shift in the linear predictor into per-feature contributions, and the largest of these is 0.0237 [[art:aa2ba789:csi.max]].
That largest contribution comes from the last delinquency feature at 0.0237 [[art:471433c6:csi.delinq_last]].
The per-feature contributions are as follows.

- age: 0.0009462 [[art:a1e9712b:csi.age]]
- bill_last: 0.00755 [[art:609757f9:csi.bill_last]]
- bill_last_adj: 0.007981 [[art:3945402b:csi.bill_last_adj]]
- bill_mean_6m: 0.004327 [[art:a221465d:csi.bill_mean_6m]]
- bill_trend_6m: 0.0006834 [[art:c7ef6238:csi.bill_trend_6m]]
- delinq_count_6m: 0.002436 [[art:4bcd65c1:csi.delinq_count_6m]]
- delinq_last: 0.0237 [[art:471433c6:csi.delinq_last]]
- delinq_max_6m: 0.0008971 [[art:0cd543bd:csi.delinq_max_6m]]
- limit_bal: 0.001916 [[art:d25f5a77:csi.limit_bal]]
- pay_ratio_last: 0.00205 [[art:4461bc3a:csi.pay_ratio_last]]
- pay_ratio_mean_6m: 0.001802 [[art:dc5c1bb6:csi.pay_ratio_mean_6m]]
- utilisation: 0.00249 [[art:b5e8df76:csi.utilisation]]
- utilisation_mean_6m: 0.00214 [[art:71b78094:csi.utilisation_mean_6m]]

The last delinquency feature contributes more to the shift in the linear predictor at 0.0237 [[art:471433c6:csi.delinq_last]] than its own distributional movement between the splits would suggest at 0.00285 [[art:03bd52e7:psi.delinq_last]], which reflects the weight the model places on it rather than an unstable input.
The two bill-level features are the next largest contributors, at 0.007981 [[art:3945402b:csi.bill_last_adj]] and 0.00755 [[art:609757f9:csi.bill_last]], and these are also the features with the largest distributional movement.

### Leakage screens

Features declared as observed during the performance period or after the outcome number 0 [[art:742bcd24:leakage.timing.n_flagged]], so the declared timings raise no objection on their own, though the screen rests on the declarations as given rather than on independent confirmation of when each field was captured.
The strongest single feature reaches an AUC of 0.6831 [[art:fd829fc4:leakage.target_corr.max_single_feature_auc]], below the bound of 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]] above which a lone feature would be treated as standing in for the outcome.
The share of test rows whose feature values also appear in train is 0 [[art:4c9fcd09:leakage.overlap]].

The contamination screen is read on an identifier arm and a feature-vector arm, each against its own bound.
On the identifier arm, the share of test rows whose client identifier also identifies a row of train is 0 [[art:63d37fc5:leakage.overlap.ids]], below the declared contamination bound of 0.005 [[art:9f336eaf:threshold.L2.overlap]].
On the feature-vector arm, the share of test rows whose feature values also appear in train is 0 [[art:0fec8048:leakage.overlap.features]], below the bound the rule actually applied, 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].
That applied bound is whichever is larger of the declared contamination bound and a term scaled from the within-train duplicate share, so that distinct subjects writing the same discrete row are read as coincidence rather than as contamination.
The within-train duplicate share, the share of train rows whose feature values are not unique within train, is 0 [[art:4474c227:leakage.duplicates.train]], so the applied bound rests at the declared value of 0.005 [[art:9f336eaf:threshold.L2.overlap]] rather than being widened by duplication in the training data.
Feature names matching the target-adjacent lexicon number 0 [[art:407e62be:leakage.name_screen.n_matched]], so the name screen surfaces no input whose label suggests it encodes the outcome.

### Assessment

On the evidence above, the splits are clean of missingness at their worst-affected columns, the train-to-test distributional movement sits well inside the declared bound on both the input and the score side, and each leakage screen returns a result inside the bound it is read against.
The residual reservations are qualitative rather than quantitative: the timing screen and the name screen both depend on developer declarations and on the lexicon chosen, and neither would detect a leaked field that was correctly typed and conventionally named.
Stability here is measured between the training split and the test split drawn from the same period, so it speaks to the construction of the splits rather than to the durability of the input distribution in use, and ongoing monitoring against production data remains the means of establishing that.

## 4. Outcomes analysis

Outcomes analysis compares the model's outputs with the outcomes actually realised, assessing rank-ordering and forecast accuracy as distinct questions about performance against the model's objectives [[reg:SR26-2:V.1.b]].

This section reports discrimination first and calibration after it.

The order follows the observed event rate on the evaluation split, 0.2247 [[art:9209d200:metrics.test.event_rate]], which stands above 0.05 [[art:42f1351e:rule.calibration_first_event_rate]], the rate below which this report would lead with calibration instead.

The metrics recomputed by this validation on each split are set out below, one row per metric.

| Metric | Train | Test |
| --- | --- | --- |
| Rows | 3500 [[art:564683ee:metrics.train.n]] | 1500 [[art:64fcf14d:metrics.test.n]] |
| Observed event rate | 0.2246 [[art:133a5ff8:metrics.train.event_rate]] | 0.2247 [[art:9209d200:metrics.test.event_rate]] |
| AUC | 0.7607 [[art:9b2be514:metrics.train.auc]] | 0.7505 [[art:3bbb3e37:metrics.test.auc]] |
| Gini | 0.5215 [[art:94b21017:metrics.train.gini]] | 0.5009 [[art:1456c955:metrics.test.gini]] |
| KS | 0.4489 [[art:a3928b90:metrics.train.ks]] | 0.4317 [[art:414deaff:metrics.test.ks]] |
| Brier | 0.1486 [[art:2fe86f99:metrics.train.brier]] | 0.1486 [[art:08bbf5ff:metrics.test.brier]] |
| Log loss | 0.464 [[art:522ccdcf:metrics.train.logloss]] | 0.467 [[art:dee4fde4:metrics.test.logloss]] |
| Mean predicted | 0.2246 [[art:4103f0d8:metrics.train.mean_predicted]] | 0.2215 [[art:461086da:metrics.test.mean_predicted]] |

Train reads above test on AUC, on Gini and on KS, and test reads above train on log loss, the ordering expected when a model is scored on data it did not see.

Separation by decile of predicted probability on test is carried in the table below, with decile 1 holding the highest probabilities.

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

The top two deciles capture 0.4659 [[art:b4ba6281:deciles.test.top2_capture]] of the events on test, against 0.4504 [[art:250e62bc:deciles.train.top2_capture]] on train.

On the train-to-test gap, AUC on train is 0.7607 [[art:9b2be514:metrics.train.auc]] and AUC on test is 0.7505 [[art:3bbb3e37:metrics.test.auc]], the training figure the higher of the two, and the bound this validation applies to the distance between them is 0.08 [[art:630f28f4:threshold.O1.auc_gap]].

Turning to calibration, the logistic regression of the outcome on the logit of the predicted probability gives a slope on test of 0.9988 [[art:6d8bca25:calibration_slope.test]], inside the band that runs from 0.8 [[art:749634ae:threshold.C1.calibration_slope.min]] to 1.2 [[art:b6672579:threshold.C1.calibration_slope.max]].

The same regression on train gives a slope of 1.005 [[art:79d5244e:calibration_slope.train]], also inside that band.

The intercept of that regression is 0.02018 [[art:a813ed8b:calibration_intercept.test]] on test and 0.005847 [[art:79bab09a:calibration_intercept.train]] on train, both close to the origin a well-centred score would give.

Mean predicted probability on test is 0.2215 [[art:461086da:metrics.test.mean_predicted]] against an observed rate of 0.2247 [[art:9209d200:metrics.test.event_rate]], the prediction the lower of the two.

Expressed relative to the observed rate that difference is 0.01419 [[art:22eeaff2:calibration.mean_rel_gap.test]], well inside the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].

The same relative comparison on train is 8.266e-05 [[art:ca4e4c16:calibration.mean_rel_gap.train]].

Calibration by decile of predicted probability on test is carried in the table below.

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

The thresholds the developer declared in the package manifest, each with its bound, the value this validation recomputed for it and the outcome, are set out below.

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

Each row pairs a bound the manifest declares with the figure this validation recomputed for it, so the outcome rests on the recomputed value rather than on the value the developer reported.

The bounds it covers span discrimination, calibration and population stability, and the recomputed figures behind the first two are the ones reported above.

### Follow-up analyses

The planning loop ran three further recomputations of the metric set on sub-populations of test, each reported here.

The first recomputed every metric on test for the sub-population `utilisation > median(utilisation)`.

It was asked to check whether the champion's AUC shortfall against the challenger concentrates in the high-utilisation half, where a linear score would miss the non-linearity.

<!-- quaestor:renderer:begin table metrics.test.sub.utilisation_high -->
Every metric on the utilisation above_median slice of test [[art:a5faad4f:metrics.test.sub.utilisation_high]]:

| metric | value |
|---|---|
| n | 750 |
| event_rate | 0.2333 |
| auc | 0.5721 |
| gini | 0.1442 |
| ks | 0.1491 |
| brier | 0.1942 |
| logloss | 0.5853 |
| mean_predicted | 0.2294 |
| mean_rel_gap | 0.01696 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

AUC on this slice is 0.5721 [[art:218a0547:metrics.test.sub.utilisation_high.auc]], falling 0.1783 [[art:951b2d25:metrics.test.sub.utilisation_high.auc_gap]] below AUC on all of test, above the 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] by which a sub-population may fall short before the result is carried forward as an open question for the model developer.

The slice holds 0.5 [[art:9404484e:metrics.test.sub.utilisation_high.share]] of the split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] a sub-population must hold before it can raise one and below the 0.95 [[art:a928a05c:threshold.O1.slice_max_share]] at which it would be refused as the whole split.

Mean predicted on the slice is 0.2294 [[art:baa1ca0c:metrics.test.sub.utilisation_high.mean_predicted]] against an observed rate of 0.2333 [[art:8e66209c:metrics.test.sub.utilisation_high.event_rate]], a relative difference of 0.01696 [[art:5d3f4d10:metrics.test.sub.utilisation_high.mean_rel_gap]] against a tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]], so the level of the probabilities tracks the outcome on this half and the weakness sits in their ordering.

The second recomputed every metric on test for the sub-population `utilisation <= median(utilisation)`.

It was asked to complete the partition, so that the above-median half could be read against its complement rather than only against the whole split.

<!-- quaestor:renderer:begin table metrics.test.sub.utilisation_low -->
Every metric on the utilisation below_median slice of test [[art:37b022cf:metrics.test.sub.utilisation_low]]:

| metric | value |
|---|---|
| n | 750 |
| event_rate | 0.216 |
| auc | 0.8998 |
| gini | 0.7996 |
| ks | 0.7642 |
| brier | 0.1031 |
| logloss | 0.3486 |
| mean_predicted | 0.2136 |
| mean_rel_gap | 0.01119 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

AUC on this slice is 0.8998 [[art:024542ae:metrics.test.sub.utilisation_low.auc]], and the shortfall against AUC on all of test is -0.1493 [[art:70a562d2:metrics.test.sub.utilisation_low.auc_gap]], the slice reading above the split rather than below it and so within the 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] bound.

The slice holds 0.5 [[art:7860a748:metrics.test.sub.utilisation_low.share]] of the split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] and below the 0.95 [[art:a928a05c:threshold.O1.slice_max_share]] ceiling.

Mean predicted here is 0.2136 [[art:3da81c7f:metrics.test.sub.utilisation_low.mean_predicted]] against an observed rate of 0.216 [[art:b0ad49be:metrics.test.sub.utilisation_low.event_rate]], a relative difference of 0.01119 [[art:088b852d:metrics.test.sub.utilisation_low.mean_rel_gap]] against the same tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]], so both the level and the ordering hold on this half.

The third recomputed every metric on test for the sub-population `delinq_last > median(delinq_last)`.

It was asked to test whether the weakness behind the challenger's AUC lead concentrates in the delinquent sub-population, which the two utilisation halves did not address.

<!-- quaestor:renderer:begin table metrics.test.sub.delinq_last_high -->
Every metric on the delinq_last above_median slice of test [[art:2dbecccd:metrics.test.sub.delinq_last_high]]:

| metric | value |
|---|---|
| n | 339 |
| event_rate | 0.5103 |
| auc | 0.5882 |
| gini | 0.1765 |
| ks | 0.1701 |
| brier | 0.2545 |
| logloss | 0.711 |
| mean_predicted | 0.4674 |
| mean_rel_gap | 0.08419 |
| share | 0.226 |
<!-- quaestor:renderer:end -->

AUC on this slice is 0.5882 [[art:18b3a939:metrics.test.sub.delinq_last_high.auc]], falling 0.1622 [[art:509039a7:metrics.test.sub.delinq_last_high.auc_gap]] below AUC on all of test, again above the 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] bound and so carried forward as an open question for the model developer.

The slice covers 0.226 [[art:e795e8a9:metrics.test.sub.delinq_last_high.share]] of the split on 339 [[art:04716bec:metrics.test.sub.delinq_last_high.n]] rows, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] and below the 0.95 [[art:a928a05c:threshold.O1.slice_max_share]] ceiling.

Mean predicted on the slice is 0.4674 [[art:281b9e4c:metrics.test.sub.delinq_last_high.mean_predicted]] against an observed rate of 0.5103 [[art:c9cb7610:metrics.test.sub.delinq_last_high.event_rate]], the prediction the lower of the two, and the relative difference is 0.08419 [[art:30d42145:metrics.test.sub.delinq_last_high.mean_rel_gap]] against a tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].

The level of the probabilities therefore remains inside the tolerance on this slice while the ordering does not, which places the weakness in the ranking rather than in the calibration of the level.

## 5. Sensitivity and scenario analysis

Sensitivity analysis here follows the guidance that validation should check the effect of small changes in inputs and parameter values on model outputs, and should establish the conditions under which a model may become unstable [[reg:SR11-7:V.1.a]].

### Multicollinearity among the retained features

The largest variance inflation factor across the retained features belongs to `bill_last_adj` [[art:e6655d27:vif.max]], and it sits far above the declared bound of 10 [[art:aeb4f33c:threshold.M1.vif]].
The closely related `bill_last` sits just below it [[art:9139aeac:vif.bill_last]], and the pair of near-duplicate billing columns is the dominant source of the inflation.
The six-month billing mean is also above the bound at 175.6 [[art:964ad8e8:vif.bill_mean_6m]], as are the two utilisation columns at 49.46 [[art:09540d95:vif.utilisation]] and 50.25 [[art:5233c25b:vif.utilisation_mean_6m]], the latter being the larger of the two.
The remaining retained features sit below the bound: `pay_ratio_last` at 7.269 [[art:6fb2f509:vif.pay_ratio_last]], `pay_ratio_mean_6m` at 7.261 [[art:76c577a1:vif.pay_ratio_mean_6m]], `bill_trend_6m` at 5.551 [[art:2d1864b3:vif.bill_trend_6m]], `limit_bal` at 4.845 [[art:ffa16c31:vif.limit_bal]], `delinq_count_6m` at 2.562 [[art:0e627a7d:vif.delinq_count_6m]], `delinq_max_6m` at 2.409 [[art:c31719bd:vif.delinq_max_6m]], `delinq_last` at 1.411 [[art:5fce8331:vif.delinq_last]] and `age` at 1.002 [[art:c4867fa9:vif.age]].
Belsley's condition number of the column-standardised design is 1023 [[art:36c154df:condition_number]], above its declared bound of 30 [[art:7e52fd7a:threshold.M1.condition_number]], which corroborates the picture from the individual inflation factors rather than adding an independent one.
Taken together these two readings support the collinearity finding raised for this section at medium severity: the design matrix is close to rank-deficient in the billing and utilisation block, so individual coefficient estimates in that block are unstable in sign and magnitude even where the fitted probabilities are not.
The practical consequence for use is that coefficient-level interpretation of the billing and utilisation terms should not be relied on, and any attribution or reason-code logic built on those coefficients inherits the instability.

### Analyses that do not apply to this model

Stability across declared regimes is not applicable to this subject, because the package declares no regime column against which the sample could be partitioned; it is recorded in Appendix D as out of scope rather than as an analysis that returned a benign result.
The rate-shock scenarios — the change in value at the extreme shocks, the monotonicity of the shock curve and the sign of its convexity against the declared direction — are specific to hazard models, and the subject of this report is not one; they are likewise listed in Appendix D as out of scope for this model type and were not exercised.
No conclusion in this section should be read as evidence that the subject is stable across regimes or well behaved under rate shocks, since neither question was posed to it.

## 6. Findings and recommendations

Findings are set out below in order of severity, the medium before the low, and each carries the recomputed quantities and the declared bounds its check read, so that the limitation, its extent and whether corrective action is warranted can be judged from that evidence [[reg:SR26-2:V]].

### F-001 · M1 collinearity · severity **medium**

**The design matrix is near-singular, so the fitted coefficients are not separately identified and no single one of them can be read as the contribution of its own feature.**

The largest variance inflation factor on train is 121913.6293 [[art:e6655d27:vif.max]], carried by the adjusted last-bill column at 121913.6293 [[art:5216ecf3:vif.bill_last_adj]], against a declared ceiling of 10 [[art:aeb4f33c:threshold.M1.vif]].

The raw last-bill column stands at 121617.0493 [[art:9139aeac:vif.bill_last]], the six-month mean bill at 175.6 [[art:964ad8e8:vif.bill_mean_6m]], the six-month mean utilisation at 50.25 [[art:5233c25b:vif.utilisation_mean_6m]] and utilisation at 49.46 [[art:09540d95:vif.utilisation]], each above that same ceiling.

Belsley's condition number of the column-standardised design is 1023 [[art:36c154df:condition_number]], above the declared bound of 30 [[art:7e52fd7a:threshold.M1.condition_number]].

The validator concludes that the two bill columns are close to duplicates of one another and that the two utilisation columns overlap heavily, leaving the coefficient vector unstable under small perturbations of the training sample and leaving any economic reading of an individual coefficient unsupported.

The developer should drop or combine the redundant bill and utilisation columns, refit the model, and report the variance inflation factors and the condition number of the reduced design against those same declared bounds before any coefficient is interpreted or relied on for attribution.

### F-002 · E1 effective challenge · severity **low**

**A standard gradient-boosting challenger trained on the same data discriminates materially better than the champion, so the champion does not represent the discriminatory power available from its own inputs.**

The challenger reaches an AUC on test of 0.8249 [[art:9727c6a9:challenger.auc]] against the champion's 0.7505 [[art:3bbb3e37:metrics.test.auc]].

The challenger's lead over the champion is 0.07444 [[art:d7dbe8ff:challenger.delta_auc]], above the declared effective-challenge bound of 0.03 [[art:e042774c:threshold.E1.delta_auc]].

The validator concludes that severity is low because the challenger is a benchmark rather than a proposed replacement, but that the margin is wide enough to show predictive structure the champion's functional form does not capture.

The developer should record the reasons the simpler form was retained over the challenger, in terms of interpretability, stability or deployment constraints, and should either evidence those reasons or bring the challenger forward as a candidate.

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1, S1), `compute_metrics` (T1, C1, O1), `check_leakage` (L1, L2).

### Open items

Can the model developer explain what the model discriminates on inside `delinq_last > median(delinq_last)`, where AUC is 0.5882 [[art:18b3a939:metrics.test.sub.delinq_last_high.auc]] against 0.7505 [[art:3bbb3e37:metrics.test.auc]] on all of test, a shortfall compared as a difference of 0.1622 [[art:509039a7:metrics.test.sub.delinq_last_high.auc_gap]] read against a bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]], on a segment holding 0.226 [[art:e795e8a9:metrics.test.sub.delinq_last_high.share]] of the split and so at or above the 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] share needed to be raised here, given that selecting on a delinquency count also selects a near-constant delinquency history?

Can the model developer explain what the model discriminates on inside `utilisation > median(utilisation)`, where AUC is 0.5721 [[art:218a0547:metrics.test.sub.utilisation_high.auc]] against 0.7505 [[art:3bbb3e37:metrics.test.auc]] on all of test, a shortfall compared as a difference of 0.1783 [[art:951b2d25:metrics.test.sub.utilisation_high.auc_gap]] read against a bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] and the larger of the two segment shortfalls on that comparison, on a segment holding 0.5 [[art:9404484e:metrics.test.sub.utilisation_high.share]] of the split and so at or above the 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] share needed to be raised here?

Can the model developer say what makes the fitted coefficient on `bill_mean_6m` carry sign 1 [[art:a457c04a:sign_check.bill_mean_6m.coef_sign]] where that feature's own univariate direction on train is -1 [[art:23b89c5d:sign_check.bill_mean_6m.univariate_direction]], an agreement flag of 0 [[art:4df8b747:sign_check.bill_mean_6m.agrees]] read against that univariate direction, and whether the reversal is the intended conditional effect once the correlated columns are held fixed?

Can the model developer say what makes the fitted coefficient on `delinq_max_6m` carry sign -1 [[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]] where that feature's own univariate direction on train is 1 [[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]], an agreement flag of 0 [[art:c946359c:sign_check.delinq_max_6m.agrees]] read against that univariate direction, and whether the reversal is the intended conditional effect once the correlated columns are held fixed?

Can the model developer say what makes the fitted coefficient on `limit_bal` carry sign 1 [[art:6af6aef2:sign_check.limit_bal.coef_sign]] where that feature's own univariate direction on train is -1 [[art:56d284d6:sign_check.limit_bal.univariate_direction]], an agreement flag of 0 [[art:0278aad1:sign_check.limit_bal.agrees]] read against that univariate direction, and whether the reversal is the intended conditional effect once the correlated columns are held fixed?

Can the model developer say what makes the fitted coefficient on `pay_ratio_last` carry sign 1 [[art:f018263e:sign_check.pay_ratio_last.coef_sign]] where that feature's own univariate direction on train is -1 [[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]], an agreement flag of 0 [[art:79abee77:sign_check.pay_ratio_last.agrees]] read against that univariate direction, and whether the reversal is the intended conditional effect once the correlated columns are held fixed?

## 7. Ongoing monitoring recommendations

Ongoing monitoring is what tells the organization whether this package continues to perform as expected once products, exposures, activities, clients, data relevance, or market conditions move away from the conditions under which it was validated [[reg:SR26-2:V.2]].

The recommendations below reuse the bounds the checks in this report were run against, so that a monitoring breach and a validation failure carry the same meaning and require no new agreement on what "acceptable" means.

### Quantities to track, at what cadence, against which bound

- Recompute rank-ordering performance on each production cohort whose outcomes have matured, and compare it with the declared floor of 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]], reading deterioration against the evaluation-split level of 0.7505 [[art:3bbb3e37:metrics.test.auc]], which sat above that floor.
- Recompute the mean squared error of the predicted probabilities on the same cadence and compare it with the declared ceiling of 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]], against the evaluation-split level of 0.1486 [[art:08bbf5ff:metrics.test.brier]], which sat below that ceiling.
- Refit the logistic regression of the outcome on the log-odds of the score for each matured cohort and require the slope to remain inside the declared band running from 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] to 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]], the evaluation-split slope having been 0.9988 [[art:6d8bca25:calibration_slope.test]], which lies inside that band.
- Track the largest population stability index across the scored features and the score itself, measured from the development sample to each incoming production vintage, against the declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
- Run that stability measurement on the fastest cycle the scoring pipeline supports, more frequently than the outcome-based metrics above, because it requires no realized outcomes; the train-to-test value observed in this validation was 0.01372 [[art:d34e2b0f:psi.max]], far below the declared ceiling, so early movement should be visible well before the bound is approached.
- Report the observed event rate of each monitoring cohort alongside these metrics, since it governs which view of performance a monitoring report should lead with.
- Where a future cohort's event rate falls below 0.05 [[art:42f1351e:rule.calibration_first_event_rate]], that monitoring report should present calibration before discrimination; the evaluation split used here sat at or above that bound, which is why section 4 of this report presented discrimination first.
- Track the outcome-based metrics by portfolio segment as well as in aggregate, so that a stable aggregate does not conceal a segment moving toward one of the declared bounds; when comparing two segments, state whether the comparison is the difference in the metric or its ratio, because two segments with matching absolute gaps can differ substantially in relative terms.

Persistent deviation outside these declared bounds, rather than a single cohort's excursion, is the trigger for considering overlays, adjustment, recalibration, or redevelopment [[reg:SR26-2:V.1.b]].

### What this validation could not cover, and monitoring should

- Drift was assessed here as a train-to-test comparison inside the development data, which cannot speak to how the scored population moves after deployment; monitoring must re-measure stability vintage by vintage against the declared ceiling above.
- Back-testing against realized outcomes over a production performance window can begin only once production cohorts season, and it is the principal form of outcomes analysis that this report could not supply [[reg:SR26-2:V.1.b]].
- Process verification in the production environment — that inputs arriving at the scorer remain accurate, complete and consistent with the model's design, and that the deployed code is the code reviewed here — sits outside a validation performed on a frozen package and belongs to the monitoring program [[reg:SR11-7:V.1.b]].
- Override behaviour cannot be observed before the model is used in decisions, so monitoring should log overrides, evaluate the reasons for them, and track whether overridden decisions outperform the model, since a rising override rate is itself evidence that the model needs revision [[reg:SR11-7:V.1.b]].
- Section 2 of this report compares the champion with a challenger, but that comparison is bounded by the development data both were fitted on; monitoring should add the benchmark that data cannot give, namely the challenger refitted on successive production vintages and scored against the champion on the same cohort, with material discrepancies investigated for their source rather than read directly as champion error [[reg:SR11-7:V.1.b]].

The cadence and scope of these reports should follow the model's materiality and the rate at which new data arrives, and should be revisited whenever the product, the applicant population, or the decision policy the score feeds changes [[reg:SR26-2:V.2]].

## Appendix A — Claims

Grounding precision 0.9840 before repair (307 of 312 claims verified; 5 mismatch) and 1.0000 after 2 claim(s) rewritten and 2 number(s) removed from the prose. Per section (post-repair): summary 64/64; conceptual_soundness 64/64; data_integrity 56/56; outcomes 65/65; sensitivity 14/14; findings 37/37; monitoring 10/10.

Repairs:

| section | before | after | instruction to the drafter |
|---|---|---|---|
| findings | 121900 (mismatch) | 121913.6293 (verified) | you wrote 121900 for vif.max; the artifact says 121913.6293 (tolerance 0.5); cite the right artifact, correct the number, or remove it |
| findings | 121900 (mismatch) | 121913.6293 (verified) | you wrote 121900 for vif.bill_last_adj; the artifact says 121913.6293 (tolerance 0.5); cite the right artifact, correct the number, or remove it |
| findings | 121600 (mismatch) | 121617.0493 (verified) | you wrote 121600 for vif.bill_last; the artifact says 121617.0493 (tolerance 0.5); cite the right artifact, correct the number, or remove it |

Developer claims: The package declares 2 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). See Appendix D.

Excluded numeric tokens (not claims): section_number (section 4, Section 2); label_number (decile 1); citation_hash (2ad8d1a5, 2510d49d, 2193cf5f, 564683ee); regulatory_section_id (SR26-2:V, SR26-2:V.1.b, SR26-2:V.1.a, SR26-2:IV.1); finding_id (F-001, F-002); package_version (1.0); extractor_returned_excluded_token (1.0, 001,, 002,, 1).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The subject was executed under a declared wall-clock cap of… | 300 | ratio | runtime.max_seconds |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 2 | summary | The training split holds 3500 rows and the test split holds… | 3500 | count | n | train | eq | `[[art:2510d49d:profile.train.n]]` | verified | 3500 |
| 3 | summary | The training split holds 3500 rows and the test split holds… | 1500 | count | n | test | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 4 | summary | The training split holds 3500 rows and the test split holds… | 3500 | count | n | train | eq | `[[art:564683ee:metrics.train.n]]` | verified | 3500 |
| 5 | summary | The training split holds 3500 rows and the test split holds… | 1500 | count | n | test | eq | `[[art:64fcf14d:metrics.test.n]]` | verified | 1500 |
| 6 | summary | The event rate is close between the two splits, at 0.2246 on… | 0.2246 | ratio | event_rate | train | eq | `[[art:133a5ff8:metrics.train.event_rate]]` | verified | 0.2245714286 |
| 7 | summary | The event rate is close between the two splits, at 0.2246 on… | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 8 | summary | Discrimination on test is 0.7505 , above the declared floor… | 0.7505 | ratio | auc | test | eq | `[[art:3bbb3e37:metrics.test.auc]]` | verified | 0.7504688325 |
| 9 | summary | Discrimination on test is 0.7505 , above the declared floor… | 0.7 | ratio | auc | test | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 10 | summary | The Brier score on test is 0.1486 , below the declared ceili… | 0.1486 | ratio | brier | test | eq | `[[art:08bbf5ff:metrics.test.brier]]` | verified | 0.1486259309 |
| 11 | summary | The Brier score on test is 0.1486 , below the declared ceili… | 0.2 | ratio | brier | test | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 12 | summary | The calibration slope on test is 0.9988 , inside the declare… | 0.9988 | ratio | calibration_slope | test | eq | `[[art:6d8bca25:calibration_slope.test]]` | verified | 0.9988191006 |
| 13 | summary | The calibration slope on test is 0.9988 , inside the declare… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 14 | summary | The calibration slope on test is 0.9988 , inside the declare… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 15 | summary | The calibration slope on test is 0.9988 , inside the declare… | 1.005 | ratio | calibration_slope | train | eq | `[[art:79d5244e:calibration_slope.train]]` | verified | 1.005002582 |
| 16 | summary | The largest train-to-test population stability index, score… | 0.01372 | ratio | psi |  | eq | `[[art:d34e2b0f:psi.max]]` | verified | 0.01371561255 |
| 17 | summary | The largest train-to-test population stability index, score… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 18 | summary | The largest train-to-test population stability index, score… | 0.0237 | ratio | csi |  | eq | `[[art:aa2ba789:csi.max]]` | verified | 0.02369768527 |
| 19 | summary | Supporting test-split measures are a Gini of 0.5009 , a Kolm… | 0.5009 | ratio | gini | test | eq | `[[art:1456c955:metrics.test.gini]]` | verified | 0.500937665 |
| 20 | summary | Supporting test-split measures are a Gini of 0.5009 , a Kolm… | 0.4317 | ratio | ks | test | eq | `[[art:414deaff:metrics.test.ks]]` | verified | 0.4316703705 |
| 21 | summary | Supporting test-split measures are a Gini of 0.5009 , a Kolm… | 0.467 | ratio | logloss | test | eq | `[[art:dee4fde4:metrics.test.logloss]]` | verified | 0.4669720314 |
| 22 | summary | Supporting test-split measures are a Gini of 0.5009 , a Kolm… | 0.2215 | ratio | mean_predicted | test | eq | `[[art:461086da:metrics.test.mean_predicted]]` | verified | 0.2214797296 |
| 23 | summary | Supporting test-split measures are a Gini of 0.5009 , a Kolm… | 0.7607 | ratio | auc | train | eq | `[[art:9b2be514:metrics.train.auc]]` | verified | 0.7607383073 |
| 24 | summary | Supporting test-split measures are a Gini of 0.5009 , a Kolm… | 0.5215 | ratio | gini | train | eq | `[[art:94b21017:metrics.train.gini]]` | verified | 0.5214766145 |
| 25 | summary | Supporting test-split measures are a Gini of 0.5009 , a Kolm… | 0.4489 | ratio | ks | train | eq | `[[art:a3928b90:metrics.train.ks]]` | verified | 0.4489284663 |
| 26 | summary | Supporting test-split measures are a Gini of 0.5009 , a Kolm… | 0.1486 | ratio | brier | train | eq | `[[art:2fe86f99:metrics.train.brier]]` | verified | 0.1486066513 |
| 27 | summary | Supporting test-split measures are a Gini of 0.5009 , a Kolm… | 0.464 | ratio | logloss | train | eq | `[[art:522ccdcf:metrics.train.logloss]]` | verified | 0.4639849916 |
| 28 | summary | Supporting test-split measures are a Gini of 0.5009 , a Kolm… | 0.2246 | ratio | mean_predicted | train | eq | `[[art:4103f0d8:metrics.train.mean_predicted]]` | verified | 0.2245528647 |
| 29 | summary | On the above-median utilisation slice, which holds 750 rows… | 750 | count | n | test | eq | `[[art:ea5b0084:metrics.test.sub.utilisation_high.n]]` | verified | 750 |
| 30 | summary | On the above-median utilisation slice, which holds 750 rows… | 0.5 | ratio | share | test | eq | `[[art:9404484e:metrics.test.sub.utilisation_high.share]]` | verified | 0.5 |
| 31 | summary | On the above-median utilisation slice, which holds 750 rows… | 0.5721 | ratio | auc | test | eq | `[[art:218a0547:metrics.test.sub.utilisation_high.auc]]` | verified | 0.5721242236 |
| 32 | summary | On the above-median utilisation slice, which holds 750 rows… | 0.1783 | ratio | auc_gap | test | eq | `[[art:951b2d25:metrics.test.sub.utilisation_high.auc_gap]]` | verified | 0.1783446089 |
| 33 | summary | On the below-median utilisation slice, of the same size at 7… | 750 | count | n | test | eq | `[[art:5b0bae29:metrics.test.sub.utilisation_low.n]]` | verified | 750 |
| 34 | summary | On the below-median utilisation slice, of the same size at 7… | 0.5 | ratio | share | test | eq | `[[art:7860a748:metrics.test.sub.utilisation_low.share]]` | verified | 0.5 |
| 35 | summary | On the below-median utilisation slice, of the same size at 7… | 0.8998 | ratio | auc | test | eq | `[[art:024542ae:metrics.test.sub.utilisation_low.auc]]` | verified | 0.8997753422 |
| 36 | summary | On the below-median utilisation slice, of the same size at 7… | -0.1493 | ratio | auc_gap | test | eq | `[[art:70a562d2:metrics.test.sub.utilisation_low.auc_gap]]` | verified | -0.1493065097 |
| 37 | summary | On the above-median delinquency slice, which holds 339 rows… | 339 | count | n | test | eq | `[[art:04716bec:metrics.test.sub.delinq_last_high.n]]` | verified | 339 |
| 38 | summary | On the above-median delinquency slice, which holds 339 rows… | 0.226 | ratio | share | test | eq | `[[art:e795e8a9:metrics.test.sub.delinq_last_high.share]]` | verified | 0.226 |
| 39 | summary | On the above-median delinquency slice, which holds 339 rows… | 0.5882 | ratio | auc | test | eq | `[[art:18b3a939:metrics.test.sub.delinq_last_high.auc]]` | verified | 0.5882373424 |
| 40 | summary | On the above-median delinquency slice, which holds 339 rows… | 0.1622 | ratio | auc_gap | test | eq | `[[art:509039a7:metrics.test.sub.delinq_last_high.auc_gap]]` | verified | 0.1622314901 |
| 41 | summary | On the same slices the Brier score is 0.1942 , 0.1031 and 0.… | 0.1942 | ratio | brier | test | eq | `[[art:c584f815:metrics.test.sub.utilisation_high.brier]]` | verified | 0.1941849919 |
| 42 | summary | On the same slices the Brier score is 0.1942 , 0.1031 and 0.… | 0.1031 | ratio | brier | test | eq | `[[art:39a0bd66:metrics.test.sub.utilisation_low.brier]]` | verified | 0.10306687 |
| 43 | summary | On the same slices the Brier score is 0.1942 , 0.1031 and 0.… | 0.2545 | ratio | brier | test | eq | `[[art:52704467:metrics.test.sub.delinq_last_high.brier]]` | verified | 0.2544916143 |
| 44 | summary | On the same slices the Brier score is 0.1942 , 0.1031 and 0.… | 0.5853 | ratio | logloss | test | eq | `[[art:b9f7b201:metrics.test.sub.utilisation_high.logloss]]` | verified | 0.585308331 |
| 45 | summary | On the same slices the Brier score is 0.1942 , 0.1031 and 0.… | 0.3486 | ratio | logloss | test | eq | `[[art:896b4831:metrics.test.sub.utilisation_low.logloss]]` | verified | 0.3486357318 |
| 46 | summary | On the same slices the Brier score is 0.1942 , 0.1031 and 0.… | 0.711 | ratio | logloss | test | eq | `[[art:9c722397:metrics.test.sub.delinq_last_high.logloss]]` | verified | 0.7110097275 |
| 47 | summary | Mean predicted against observed, taken as a relative gap, is… | 0.01696 | ratio | mean_rel_gap | test | eq | `[[art:5d3f4d10:metrics.test.sub.utilisation_high.mean_rel_gap]]` | verified | 0.01696193476 |
| 48 | summary | Mean predicted against observed, taken as a relative gap, is… | 0.01119 | ratio | mean_rel_gap | test | eq | `[[art:088b852d:metrics.test.sub.utilisation_low.mean_rel_gap]]` | verified | 0.01118559847 |
| 49 | summary | Mean predicted against observed, taken as a relative gap, is… | 0.08419 | ratio | mean_rel_gap | test | eq | `[[art:30d42145:metrics.test.sub.delinq_last_high.mean_rel_gap]]` | verified | 0.08419397297 |
| 50 | summary | The observed event rate on those slices is 0.2333 , 0.216 an… | 0.2333 | ratio | event_rate | test | eq | `[[art:8e66209c:metrics.test.sub.utilisation_high.event_rate]]` | verified | 0.2333333333 |
| 51 | summary | The observed event rate on those slices is 0.2333 , 0.216 an… | 0.216 | ratio | event_rate | test | eq | `[[art:b0ad49be:metrics.test.sub.utilisation_low.event_rate]]` | verified | 0.216 |
| 52 | summary | The observed event rate on those slices is 0.2333 , 0.216 an… | 0.5103 | ratio | event_rate | test | eq | `[[art:c9cb7610:metrics.test.sub.delinq_last_high.event_rate]]` | verified | 0.5103244838 |
| 53 | summary | The observed event rate on those slices is 0.2333 , 0.216 an… | 0.2294 | ratio | mean_predicted | test | eq | `[[art:baa1ca0c:metrics.test.sub.utilisation_high.mean_predicted]]` | verified | 0.2293755486 |
| 54 | summary | The observed event rate on those slices is 0.2333 , 0.216 an… | 0.2136 | ratio | mean_predicted | test | eq | `[[art:3da81c7f:metrics.test.sub.utilisation_low.mean_predicted]]` | verified | 0.2135839107 |
| 55 | summary | The observed event rate on those slices is 0.2333 , 0.216 an… | 0.4674 | ratio | mean_predicted | test | eq | `[[art:281b9e4c:metrics.test.sub.delinq_last_high.mean_predicted]]` | verified | 0.467358238 |
| 56 | summary | The observed event rate on those slices is 0.2333 , 0.216 an… | 0.1442 | ratio | gini | test | eq | `[[art:cc2438a9:metrics.test.sub.utilisation_high.gini]]` | verified | 0.1442484472 |
| 57 | summary | The observed event rate on those slices is 0.2333 , 0.216 an… | 0.7996 | ratio | gini | test | eq | `[[art:39c7fd9b:metrics.test.sub.utilisation_low.gini]]` | verified | 0.7995506845 |
| 58 | summary | The observed event rate on those slices is 0.2333 , 0.216 an… | 0.1765 | ratio | gini | test | eq | `[[art:18db302d:metrics.test.sub.delinq_last_high.gini]]` | verified | 0.1764746849 |
| 59 | summary | The observed event rate on those slices is 0.2333 , 0.216 an… | 0.1491 | ratio | ks | test | eq | `[[art:9b8e4cad:metrics.test.sub.utilisation_high.ks]]` | verified | 0.149068323 |
| 60 | summary | The observed event rate on those slices is 0.2333 , 0.216 an… | 0.7642 | ratio | ks | test | eq | `[[art:0be83ffa:metrics.test.sub.utilisation_low.ks]]` | verified | 0.7642353238 |
| 61 | summary | The observed event rate on those slices is 0.2333 , 0.216 an… | 0.1701 | ratio | ks | test | eq | `[[art:cb7c41a9:metrics.test.sub.delinq_last_high.ks]]` | verified | 0.1701023748 |
| 62 | summary | The design matrix diagnostics show a Belsley condition numbe… | 1023 | ratio | condition_number |  | eq | `[[art:36c154df:condition_number]]` | verified | 1023.412969 |
| 63 | summary | The design matrix diagnostics show a Belsley condition numbe… | 121900 | ratio | vif |  | eq | `[[art:e6655d27:vif.max]]` | verified | 121913.6293 |
| 64 | summary | On effective challenge, the challenger's AUC on test exceeds… | 0.07444 | ratio | delta_auc | test | eq | `[[art:d7dbe8ff:challenger.delta_auc]]` | verified | 0.07444422615 |
| 65 | conceptual_soundness | The champion is a single scoring equation linear in the log-… | -1.4 | ratio | intercept |  | eq | `[[art:f2e0e9a7:run.model_summary#intercept]]` | verified | -1.399732573 |
| 66 | conceptual_soundness | The champion is a single scoring equation linear in the log-… | 3500 | count | n_train | train | eq | `[[art:f2e0e9a7:run.model_summary#n_train]]` | verified | 3500 |
| 67 | conceptual_soundness | It carries 13 features into the score. | 13 | count | n |  | eq | `[[art:f79bb8bb:run.features#n]]` | verified | 13 |
| 68 | conceptual_soundness | Of those, 2 are known at origination and 11 are known before… | 2 | count | at_origination |  | eq | `[[art:f79bb8bb:run.features#at_origination]]` | verified | 2 |
| 69 | conceptual_soundness | Of those, 2 are known at origination and 11 are known before… | 11 | count | before_period_start |  | eq | `[[art:f79bb8bb:run.features#before_period_start]]` | verified | 11 |
| 70 | conceptual_soundness | Features first observable only inside the performance period… | 0 | count | during_period |  | eq | `[[art:f79bb8bb:run.features#during_period]]` | verified | 0 |
| 71 | conceptual_soundness | Features first observable only inside the performance period… | 0 | count | after_outcome |  | eq | `[[art:f79bb8bb:run.features#after_outcome]]` | verified | 0 |
| 72 | conceptual_soundness | The model's own feature screen is a collinearity screen run… | 10 | ratio | vif_threshold |  | eq | `[[art:f2e0e9a7:run.model_summary#vif_threshold]]` | verified | 10 |
| 73 | conceptual_soundness | That screen left in place both a raw last-bill term and an a… | -0.5348 | ratio | coefficient |  | eq | `[[art:f2e0e9a7:run.model_summary#coefficients.bill_last.value]]` | verified | -0.5347728097 |
| 74 | conceptual_soundness | That screen left in place both a raw last-bill term and an a… | -0.5619 | ratio | coefficient |  | eq | `[[art:f2e0e9a7:run.model_summary#coefficients.bill_last_adj.value]]` | verified | -0.5619372399 |
| 75 | conceptual_soundness | The largest weight in the equation is on the most recent del… | 0.7357 | ratio | coefficient |  | eq | `[[art:f2e0e9a7:run.model_summary#coefficients.delinq_last.value]]` | verified | 0.7356529478 |
| 76 | conceptual_soundness | Next is the six-month mean bill level, at 0.6805 , followed… | 0.6805 | ratio | coefficient |  | eq | `[[art:f2e0e9a7:run.model_summary#coefficients.bill_mean_6m.value]]` | verified | 0.6804591847 |
| 77 | conceptual_soundness | Next is the six-month mean bill level, at 0.6805 , followed… | -0.3621 | ratio | coefficient |  | eq | `[[art:f2e0e9a7:run.model_summary#coefficients.pay_ratio_mean_6m.value]]` | verified | -0.3620907123 |
| 78 | conceptual_soundness | The remaining weights are smaller: current utilisation at 0.… | 0.164 | ratio | coefficient |  | eq | `[[art:f2e0e9a7:run.model_summary#coefficients.utilisation.value]]` | verified | 0.1640055946 |
| 79 | conceptual_soundness | The remaining weights are smaller: current utilisation at 0.… | 0.1425 | ratio | coefficient |  | eq | `[[art:f2e0e9a7:run.model_summary#coefficients.utilisation_mean_6m.value]]` | verified | 0.1424538267 |
| 80 | conceptual_soundness | The remaining weights are smaller: current utilisation at 0.… | 0.1219 | ratio | coefficient |  | eq | `[[art:f2e0e9a7:run.model_summary#coefficients.delinq_count_6m.value]]` | verified | 0.1219345996 |
| 81 | conceptual_soundness | The remaining weights are smaller: current utilisation at 0.… | 0.1149 | ratio | coefficient |  | eq | `[[art:f2e0e9a7:run.model_summary#coefficients.limit_bal.value]]` | verified | 0.1148927294 |
| 82 | conceptual_soundness | The remaining weights are smaller: current utilisation at 0.… | 0.1093 | ratio | coefficient |  | eq | `[[art:f2e0e9a7:run.model_summary#coefficients.pay_ratio_last.value]]` | verified | 0.1093359074 |
| 83 | conceptual_soundness | The remaining weights are smaller: current utilisation at 0.… | -0.06716 | ratio | coefficient |  | eq | `[[art:f2e0e9a7:run.model_summary#coefficients.age.value]]` | verified | -0.0671593042 |
| 84 | conceptual_soundness | The remaining weights are smaller: current utilisation at 0.… | -0.03224 | ratio | coefficient |  | eq | `[[art:f2e0e9a7:run.model_summary#coefficients.delinq_max_6m.value]]` | verified | -0.03223664132 |
| 85 | conceptual_soundness | The remaining weights are smaller: current utilisation at 0.… | -0.02402 | ratio | coefficient |  | eq | `[[art:f2e0e9a7:run.model_summary#coefficients.bill_trend_6m.value]]` | verified | -0.02401936356 |
| 86 | conceptual_soundness | The fitted signs were compared against each feature's own si… | 4 | count | n_disagreements | train | eq | `[[art:b9e93d79:sign_check.n_disagreements]]` | verified | 4 |
| 87 | conceptual_soundness | The level each refit is measured from is a test AUC of 0.750… | 0.7505 | ratio | baseline_auc | test | eq | `[[art:2166cf12:ablation.baseline_auc]]` | verified | 0.7504688325 |
| 88 | conceptual_soundness | On the credit limit the fitted sign is 1 against a univariat… | 1 | ratio | coef_sign |  | eq | `[[art:6af6aef2:sign_check.limit_bal.coef_sign]]` | verified | 1 |
| 89 | conceptual_soundness | On the credit limit the fitted sign is 1 against a univariat… | -1 | ratio | univariate_direction |  | eq | `[[art:56d284d6:sign_check.limit_bal.univariate_direction]]` | verified | -1 |
| 90 | conceptual_soundness | On the credit limit the fitted sign is 1 against a univariat… | 0 | ratio | agrees |  | eq | `[[art:0278aad1:sign_check.limit_bal.agrees]]` | verified | 0 |
| 91 | conceptual_soundness | On the credit limit the fitted sign is 1 against a univariat… | 0.0001786 | ratio | delta_auc | test | eq | `[[art:6bf0f1c3:ablation.limit_bal.delta_auc]]` | verified | 0.0001786028663 |
| 92 | conceptual_soundness | On the last payment ratio the fitted sign is 1 against a uni… | 1 | ratio | coef_sign |  | eq | `[[art:f018263e:sign_check.pay_ratio_last.coef_sign]]` | verified | 1 |
| 93 | conceptual_soundness | On the last payment ratio the fitted sign is 1 against a uni… | -1 | ratio | univariate_direction |  | eq | `[[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]]` | verified | -1 |
| 94 | conceptual_soundness | On the last payment ratio the fitted sign is 1 against a uni… | 0 | ratio | agrees |  | eq | `[[art:79abee77:sign_check.pay_ratio_last.agrees]]` | verified | 0 |
| 95 | conceptual_soundness | On the last payment ratio the fitted sign is 1 against a uni… | 0.002437 | ratio | delta_auc | test | eq | `[[art:9639fcbd:ablation.pay_ratio_last.delta_auc]]` | verified | 0.002436653391 |
| 96 | conceptual_soundness | On the six-month maximum delinquency the fitted sign is -1 a… | -1 | ratio | coef_sign |  | eq | `[[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]]` | verified | -1 |
| 97 | conceptual_soundness | On the six-month maximum delinquency the fitted sign is -1 a… | 1 | ratio | univariate_direction |  | eq | `[[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]]` | verified | 1 |
| 98 | conceptual_soundness | On the six-month maximum delinquency the fitted sign is -1 a… | 0 | ratio | agrees |  | eq | `[[art:c946359c:sign_check.delinq_max_6m.agrees]]` | verified | 0 |
| 99 | conceptual_soundness | On the six-month maximum delinquency the fitted sign is -1 a… | 0.0003572 | ratio | delta_auc | test | eq | `[[art:16dcea2b:ablation.delinq_max_6m.delta_auc]]` | verified | 0.0003572057326 |
| 100 | conceptual_soundness | On the six-month mean bill level the fitted sign is 1 agains… | 1 | ratio | coef_sign |  | eq | `[[art:a457c04a:sign_check.bill_mean_6m.coef_sign]]` | verified | 1 |
| 101 | conceptual_soundness | On the six-month mean bill level the fitted sign is 1 agains… | -1 | ratio | univariate_direction |  | eq | `[[art:23b89c5d:sign_check.bill_mean_6m.univariate_direction]]` | verified | -1 |
| 102 | conceptual_soundness | On the six-month mean bill level the fitted sign is 1 agains… | 0 | ratio | agrees |  | eq | `[[art:4df8b747:sign_check.bill_mean_6m.agrees]]` | verified | 0 |
| 103 | conceptual_soundness | On the six-month mean bill level the fitted sign is 1 agains… | -0.0002909 | ratio | delta_auc | test | eq | `[[art:52f6233e:ablation.bill_mean_6m.delta_auc]]` | verified | -0.0002908675252 |
| 104 | conceptual_soundness | The remaining features agree with their own directions: rece… | 1 | ratio | agrees |  | eq | `[[art:a8ba9372:sign_check.delinq_last.agrees]]` | verified | 1 |
| 105 | conceptual_soundness | The remaining features agree with their own directions: rece… | 1 | ratio | agrees |  | eq | `[[art:a337d16b:sign_check.delinq_count_6m.agrees]]` | verified | 1 |
| 106 | conceptual_soundness | The remaining features agree with their own directions: rece… | 1 | ratio | agrees |  | eq | `[[art:d0c9a130:sign_check.utilisation.agrees]]` | verified | 1 |
| 107 | conceptual_soundness | The remaining features agree with their own directions: rece… | 1 | ratio | agrees |  | eq | `[[art:c2848161:sign_check.utilisation_mean_6m.agrees]]` | verified | 1 |
| 108 | conceptual_soundness | The remaining features agree with their own directions: rece… | 1 | ratio | agrees |  | eq | `[[art:7e9a76ca:sign_check.pay_ratio_mean_6m.agrees]]` | verified | 1 |
| 109 | conceptual_soundness | The remaining features agree with their own directions: rece… | 1 | ratio | agrees |  | eq | `[[art:4116add1:sign_check.age.agrees]]` | verified | 1 |
| 110 | conceptual_soundness | The remaining features agree with their own directions: rece… | 1 | ratio | agrees |  | eq | `[[art:ff3cb24a:sign_check.bill_trend_6m.agrees]]` | verified | 1 |
| 111 | conceptual_soundness | The remaining features agree with their own directions: rece… | 1 | ratio | agrees |  | eq | `[[art:98c00451:sign_check.bill_last.agrees]]` | verified | 1 |
| 112 | conceptual_soundness | The remaining features agree with their own directions: rece… | 1 | ratio | agrees |  | eq | `[[art:fb9031bc:sign_check.bill_last_adj.agrees]]` | verified | 1 |
| 113 | conceptual_soundness | The refit evidence puts almost all of the discrimination in… | -0.07782 | ratio | delta_auc | test | eq | `[[art:8eca80c6:ablation.delinq_last.delta_auc]]` | verified | -0.07782492326 |
| 114 | conceptual_soundness | The refit evidence puts almost all of the discrimination in… | -0.0005231 | ratio | delta_auc | test | eq | `[[art:c63504c6:ablation.utilisation_mean_6m.delta_auc]]` | verified | -0.0005230512514 |
| 115 | conceptual_soundness | The refit evidence puts almost all of the discrimination in… | -0.0004261 | ratio | delta_auc | test | eq | `[[art:4bde085d:ablation.age.delta_auc]]` | verified | -0.0004260954097 |
| 116 | conceptual_soundness | The refit evidence puts almost all of the discrimination in… | -0.0003113 | ratio | delta_auc | test | eq | `[[art:90093ed9:ablation.utilisation.delta_auc]]` | verified | -0.0003112792813 |
| 117 | conceptual_soundness | Dropping the mean payment ratio changes it by 0.007333 , the… | 0.007333 | ratio | delta_auc | test | eq | `[[art:5e7307e8:ablation.pay_ratio_mean_6m.delta_auc]]` | verified | 0.007332923397 |
| 118 | conceptual_soundness | Dropping the mean payment ratio changes it by 0.007333 , the… | 0.001526 | ratio | delta_auc | test | eq | `[[art:5da50826:ablation.delinq_count_6m.delta_auc]]` | verified | 0.001525778772 |
| 119 | conceptual_soundness | Dropping the mean payment ratio changes it by 0.007333 , the… | 0.0002526 | ratio | delta_auc | test | eq | `[[art:994f00bc:ablation.bill_trend_6m.delta_auc]]` | verified | 0.0002525954824 |
| 120 | conceptual_soundness | Dropping the mean payment ratio changes it by 0.007333 , the… | 0.0001786 | ratio | delta_auc | test | eq | `[[art:eea44d10:ablation.bill_last.delta_auc]]` | verified | 0.0001786028663 |
| 121 | conceptual_soundness | Dropping the mean payment ratio changes it by 0.007333 , the… | 1.531e-05 | ratio | delta_auc | test | eq | `[[art:8e9d6dcc:ablation.bill_last_adj.delta_auc]]` | verified | 1.530881711e-05 |
| 122 | conceptual_soundness | A design in which one input carries a refit change of -0.077… | -0.07782 | ratio | delta_auc | test | eq | `[[art:8eca80c6:ablation.delinq_last.delta_auc]]` | verified | -0.07782492326 |
| 123 | conceptual_soundness | The challenger reaches an AUC of 0.8249 against the champion… | 0.8249 | ratio | auc | test | eq | `[[art:9727c6a9:challenger.auc]]` | verified | 0.8249130587 |
| 124 | conceptual_soundness | The challenger reaches an AUC of 0.8249 against the champion… | 0.7505 | ratio | auc | test | eq | `[[art:3bbb3e37:metrics.test.auc]]` | verified | 0.7504688325 |
| 125 | conceptual_soundness | The challenger reaches an AUC of 0.8249 against the champion… | 0.07444 | ratio | delta_auc | test | eq | `[[art:d7dbe8ff:challenger.delta_auc]]` | verified | 0.07444422615 |
| 126 | conceptual_soundness | The bound that decides whether such a lead matters is an eff… | 0.03 | ratio | delta_auc |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 127 | conceptual_soundness | The same ordering holds on calibration loss, where the chall… | 0.1242 | ratio | brier | test | eq | `[[art:79d61058:challenger.brier]]` | verified | 0.1241756222 |
| 128 | conceptual_soundness | The same ordering holds on calibration loss, where the chall… | 0.1486 | ratio | brier | test | eq | `[[art:08bbf5ff:metrics.test.brier]]` | verified | 0.1486259309 |
| 129 | data_integrity | The training split holds 3500 rows and the test split holds… | 3500 | count | n | train | eq | `[[art:2510d49d:profile.train.n]]` | verified | 3500 |
| 130 | data_integrity | The training split holds 3500 rows and the test split holds… | 1500 | count | n | test | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 131 | data_integrity | The worst-affected column in train carries a missing fractio… | 0 | ratio | missing_max | train | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 132 | data_integrity | The worst-affected column in train carries a missing fractio… | 0 | ratio | missing_max | test | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 133 | data_integrity | The split-to-split missingness gap is bounded at 0.1 , and t… | 0.1 | ratio | missing_gap |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 134 | data_integrity | Taken as a ratio the same comparison has no informative deno… | 0 | ratio | missing_max | train | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 135 | data_integrity | Population stability between train and test is bounded at 0.… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 136 | data_integrity | Population stability between train and test is bounded at 0.… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 137 | data_integrity | The largest train-to-test population stability index, the sc… | 0.01372 | ratio | psi |  | eq | `[[art:d34e2b0f:psi.max]]` | verified | 0.01371561255 |
| 138 | data_integrity | That maximum is attributable to the adjusted last-bill featu… | 0.01372 | ratio | psi |  | eq | `[[art:e87eb6d6:psi.bill_last_adj]]` | verified | 0.01371561255 |
| 139 | data_integrity | - age: 0.008124 | 0.008124 | ratio | psi |  | eq | `[[art:f9255a0a:psi.age]]` | verified | 0.008124281436 |
| 140 | data_integrity | - bill_last: 0.01302 | 0.01302 | ratio | psi |  | eq | `[[art:cd0c79c3:psi.bill_last]]` | verified | 0.01302192576 |
| 141 | data_integrity | - bill_last_adj: 0.01372 | 0.01372 | ratio | psi |  | eq | `[[art:e87eb6d6:psi.bill_last_adj]]` | verified | 0.01371561255 |
| 142 | data_integrity | - bill_mean_6m: 0.007124 | 0.007124 | ratio | psi |  | eq | `[[art:028e4281:psi.bill_mean_6m]]` | verified | 0.007124196275 |
| 143 | data_integrity | - bill_trend_6m: 0.00958 | 0.00958 | ratio | psi |  | eq | `[[art:c247a6f2:psi.bill_trend_6m]]` | verified | 0.009579614525 |
| 144 | data_integrity | - delinq_count_6m: 0.002069 | 0.002069 | ratio | psi |  | eq | `[[art:61491d02:psi.delinq_count_6m]]` | verified | 0.002069275496 |
| 145 | data_integrity | - delinq_last: 0.00285 | 0.00285 | ratio | psi |  | eq | `[[art:03bd52e7:psi.delinq_last]]` | verified | 0.002849633848 |
| 146 | data_integrity | - delinq_max_6m: 0.005498 | 0.005498 | ratio | psi |  | eq | `[[art:7a82e7f3:psi.delinq_max_6m]]` | verified | 0.005498249408 |
| 147 | data_integrity | - limit_bal: 0.01095 | 0.01095 | ratio | psi |  | eq | `[[art:601cdba2:psi.limit_bal]]` | verified | 0.01095273358 |
| 148 | data_integrity | - pay_ratio_last: 0.004966 | 0.004966 | ratio | psi |  | eq | `[[art:3af2ca29:psi.pay_ratio_last]]` | verified | 0.00496591109 |
| 149 | data_integrity | - pay_ratio_mean_6m: 0.0055 | 0.0055 | ratio | psi |  | eq | `[[art:2c5baeb2:psi.pay_ratio_mean_6m]]` | verified | 0.005500252946 |
| 150 | data_integrity | - utilisation: 0.004244 | 0.004244 | ratio | psi |  | eq | `[[art:451e0780:psi.utilisation]]` | verified | 0.0042440485 |
| 151 | data_integrity | - utilisation_mean_6m: 0.002875 | 0.002875 | ratio | psi |  | eq | `[[art:d562032d:psi.utilisation_mean_6m]]` | verified | 0.002874891089 |
| 152 | data_integrity | - score: 0.004589 | 0.004589 | ratio | psi |  | eq | `[[art:8d23655e:psi.y_score]]` | verified | 0.004589417025 |
| 153 | data_integrity | Every feature listed, and the score at 0.004589 , sits below… | 0.004589 | ratio | psi |  | eq | `[[art:8d23655e:psi.y_score]]` | verified | 0.004589417025 |
| 154 | data_integrity | Every feature listed, and the score at 0.004589 , sits below… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 155 | data_integrity | Characteristic stability decomposes the shift in the linear… | 0.0237 | ratio | csi |  | eq | `[[art:aa2ba789:csi.max]]` | verified | 0.02369768527 |
| 156 | data_integrity | That largest contribution comes from the last delinquency fe… | 0.0237 | ratio | csi |  | eq | `[[art:471433c6:csi.delinq_last]]` | verified | 0.02369768527 |
| 157 | data_integrity | - age: 0.0009462 | 0.0009462 | ratio | csi |  | eq | `[[art:a1e9712b:csi.age]]` | verified | 0.0009461826658 |
| 158 | data_integrity | - bill_last: 0.00755 | 0.00755 | ratio | csi |  | eq | `[[art:609757f9:csi.bill_last]]` | verified | 0.007550351324 |
| 159 | data_integrity | - bill_last_adj: 0.007981 | 0.007981 | ratio | csi |  | eq | `[[art:3945402b:csi.bill_last_adj]]` | verified | 0.007981166323 |
| 160 | data_integrity | - bill_mean_6m: 0.004327 | 0.004327 | ratio | csi |  | eq | `[[art:a221465d:csi.bill_mean_6m]]` | verified | 0.004326645937 |
| 161 | data_integrity | - bill_trend_6m: 0.0006834 | 0.0006834 | ratio | csi |  | eq | `[[art:c7ef6238:csi.bill_trend_6m]]` | verified | 0.000683370174 |
| 162 | data_integrity | - delinq_count_6m: 0.002436 | 0.002436 | ratio | csi |  | eq | `[[art:4bcd65c1:csi.delinq_count_6m]]` | verified | 0.00243601263 |
| 163 | data_integrity | - delinq_last: 0.0237 | 0.0237 | ratio | csi |  | eq | `[[art:471433c6:csi.delinq_last]]` | verified | 0.02369768527 |
| 164 | data_integrity | - delinq_max_6m: 0.0008971 | 0.0008971 | ratio | csi |  | eq | `[[art:0cd543bd:csi.delinq_max_6m]]` | verified | 0.0008970973047 |
| 165 | data_integrity | - limit_bal: 0.001916 | 0.001916 | ratio | csi |  | eq | `[[art:d25f5a77:csi.limit_bal]]` | verified | 0.001915717336 |
| 166 | data_integrity | - pay_ratio_last: 0.00205 | 0.00205 | ratio | csi |  | eq | `[[art:4461bc3a:csi.pay_ratio_last]]` | verified | 0.002050246889 |
| 167 | data_integrity | - pay_ratio_mean_6m: 0.001802 | 0.001802 | ratio | csi |  | eq | `[[art:dc5c1bb6:csi.pay_ratio_mean_6m]]` | verified | 0.001801777591 |
| 168 | data_integrity | - utilisation: 0.00249 | 0.00249 | ratio | csi |  | eq | `[[art:b5e8df76:csi.utilisation]]` | verified | 0.002490106313 |
| 169 | data_integrity | - utilisation_mean_6m: 0.00214 | 0.00214 | ratio | csi |  | eq | `[[art:71b78094:csi.utilisation_mean_6m]]` | verified | 0.002140004407 |
| 170 | data_integrity | The last delinquency feature contributes more to the shift i… | 0.0237 | ratio | csi |  | eq | `[[art:471433c6:csi.delinq_last]]` | verified | 0.02369768527 |
| 171 | data_integrity | The last delinquency feature contributes more to the shift i… | 0.00285 | ratio | psi |  | eq | `[[art:03bd52e7:psi.delinq_last]]` | verified | 0.002849633848 |
| 172 | data_integrity | The two bill-level features are the next largest contributor… | 0.007981 | ratio | csi |  | eq | `[[art:3945402b:csi.bill_last_adj]]` | verified | 0.007981166323 |
| 173 | data_integrity | The two bill-level features are the next largest contributor… | 0.00755 | ratio | csi |  | eq | `[[art:609757f9:csi.bill_last]]` | verified | 0.007550351324 |
| 174 | data_integrity | Features declared as observed during the performance period… | 0 | count | n_flagged |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 175 | data_integrity | The strongest single feature reaches an AUC of 0.6831 , belo… | 0.6831 | ratio | auc |  | eq | `[[art:fd829fc4:leakage.target_corr.max_single_feature_auc]]` | verified | 0.6831414154 |
| 176 | data_integrity | The strongest single feature reaches an AUC of 0.6831 , belo… | 0.9 | ratio | auc |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 177 | data_integrity | The share of test rows whose feature values also appear in t… | 0 | ratio | overlap |  | eq | `[[art:4c9fcd09:leakage.overlap]]` | verified | 0 |
| 178 | data_integrity | On the identifier arm, the share of test rows whose client i… | 0 | ratio | overlap |  | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 179 | data_integrity | On the identifier arm, the share of test rows whose client i… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 180 | data_integrity | On the feature-vector arm, the share of test rows whose feat… | 0 | ratio | overlap |  | eq | `[[art:0fec8048:leakage.overlap.features]]` | verified | 0 |
| 181 | data_integrity | On the feature-vector arm, the share of test rows whose feat… | 0.005 | ratio | overlap |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 182 | data_integrity | The within-train duplicate share, the share of train rows wh… | 0 | ratio | duplicates | train | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 183 | data_integrity | The within-train duplicate share, the share of train rows wh… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 184 | data_integrity | Feature names matching the target-adjacent lexicon number 0… | 0 | count | n_matched |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 185 | outcomes | The order follows the observed event rate on the evaluation… | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 186 | outcomes | The order follows the observed event rate on the evaluation… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 187 | outcomes | \| Rows \| 3500 \| 1500 \| | 3500 | count | n | train | eq | `[[art:564683ee:metrics.train.n]]` | verified | 3500 |
| 188 | outcomes | \| Rows \| 3500 \| 1500 \| | 1500 | count | n | test | eq | `[[art:64fcf14d:metrics.test.n]]` | verified | 1500 |
| 189 | outcomes | \| Observed event rate \| 0.2246 \| 0.2247 \| | 0.2246 | ratio | event_rate | train | eq | `[[art:133a5ff8:metrics.train.event_rate]]` | verified | 0.2245714286 |
| 190 | outcomes | \| Observed event rate \| 0.2246 \| 0.2247 \| | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 191 | outcomes | \| AUC \| 0.7607 \| 0.7505 \| | 0.7607 | ratio | auc | train | eq | `[[art:9b2be514:metrics.train.auc]]` | verified | 0.7607383073 |
| 192 | outcomes | \| AUC \| 0.7607 \| 0.7505 \| | 0.7505 | ratio | auc | test | eq | `[[art:3bbb3e37:metrics.test.auc]]` | verified | 0.7504688325 |
| 193 | outcomes | \| Gini \| 0.5215 \| 0.5009 \| | 0.5215 | ratio | gini | train | eq | `[[art:94b21017:metrics.train.gini]]` | verified | 0.5214766145 |
| 194 | outcomes | \| Gini \| 0.5215 \| 0.5009 \| | 0.5009 | ratio | gini | test | eq | `[[art:1456c955:metrics.test.gini]]` | verified | 0.500937665 |
| 195 | outcomes | \| KS \| 0.4489 \| 0.4317 \| | 0.4489 | ratio | ks | train | eq | `[[art:a3928b90:metrics.train.ks]]` | verified | 0.4489284663 |
| 196 | outcomes | \| KS \| 0.4489 \| 0.4317 \| | 0.4317 | ratio | ks | test | eq | `[[art:414deaff:metrics.test.ks]]` | verified | 0.4316703705 |
| 197 | outcomes | \| Brier \| 0.1486 \| 0.1486 \| | 0.1486 | ratio | brier | train | eq | `[[art:2fe86f99:metrics.train.brier]]` | verified | 0.1486066513 |
| 198 | outcomes | \| Brier \| 0.1486 \| 0.1486 \| | 0.1486 | ratio | brier | test | eq | `[[art:08bbf5ff:metrics.test.brier]]` | verified | 0.1486259309 |
| 199 | outcomes | \| Log loss \| 0.464 \| 0.467 \| | 0.464 | ratio | logloss | train | eq | `[[art:522ccdcf:metrics.train.logloss]]` | verified | 0.4639849916 |
| 200 | outcomes | \| Log loss \| 0.464 \| 0.467 \| | 0.467 | ratio | logloss | test | eq | `[[art:dee4fde4:metrics.test.logloss]]` | verified | 0.4669720314 |
| 201 | outcomes | \| Mean predicted \| 0.2246 \| 0.2215 \| | 0.2246 | ratio | mean_predicted | train | eq | `[[art:4103f0d8:metrics.train.mean_predicted]]` | verified | 0.2245528647 |
| 202 | outcomes | \| Mean predicted \| 0.2246 \| 0.2215 \| | 0.2215 | ratio | mean_predicted | test | eq | `[[art:461086da:metrics.test.mean_predicted]]` | verified | 0.2214797296 |
| 203 | outcomes | The top two deciles capture 0.4659 of the events on test, ag… | 0.4659 | ratio | top2_capture | test | eq | `[[art:b4ba6281:deciles.test.top2_capture]]` | verified | 0.4658753709 |
| 204 | outcomes | The top two deciles capture 0.4659 of the events on test, ag… | 0.4504 | ratio | top2_capture | train | eq | `[[art:250e62bc:deciles.train.top2_capture]]` | verified | 0.4503816794 |
| 205 | outcomes | On the train-to-test gap, AUC on train is 0.7607 and AUC on… | 0.7607 | ratio | auc | train | eq | `[[art:9b2be514:metrics.train.auc]]` | verified | 0.7607383073 |
| 206 | outcomes | On the train-to-test gap, AUC on train is 0.7607 and AUC on… | 0.7505 | ratio | auc | test | eq | `[[art:3bbb3e37:metrics.test.auc]]` | verified | 0.7504688325 |
| 207 | outcomes | On the train-to-test gap, AUC on train is 0.7607 and AUC on… | 0.08 | ratio | auc_gap |  | eq | `[[art:630f28f4:threshold.O1.auc_gap]]` | verified | 0.08 |
| 208 | outcomes | Turning to calibration, the logistic regression of the outco… | 0.9988 | ratio | calibration_slope | test | eq | `[[art:6d8bca25:calibration_slope.test]]` | verified | 0.9988191006 |
| 209 | outcomes | Turning to calibration, the logistic regression of the outco… | 0.8 | ratio | calibration_slope |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 210 | outcomes | Turning to calibration, the logistic regression of the outco… | 1.2 | ratio | calibration_slope |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 211 | outcomes | The same regression on train gives a slope of 1.005 , also i… | 1.005 | ratio | calibration_slope | train | eq | `[[art:79d5244e:calibration_slope.train]]` | verified | 1.005002582 |
| 212 | outcomes | The intercept of that regression is 0.02018 on test and 0.00… | 0.02018 | ratio | calibration_intercept | test | eq | `[[art:a813ed8b:calibration_intercept.test]]` | verified | 0.02018153799 |
| 213 | outcomes | The intercept of that regression is 0.02018 on test and 0.00… | 0.005847 | ratio | calibration_intercept | train | eq | `[[art:79bab09a:calibration_intercept.train]]` | verified | 0.005846934312 |
| 214 | outcomes | Mean predicted probability on test is 0.2215 against an obse… | 0.2215 | ratio | mean_predicted | test | eq | `[[art:461086da:metrics.test.mean_predicted]]` | verified | 0.2214797296 |
| 215 | outcomes | Mean predicted probability on test is 0.2215 against an obse… | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 216 | outcomes | Expressed relative to the observed rate that difference is 0… | 0.01419 | ratio | mean_rel_gap | test | eq | `[[art:22eeaff2:calibration.mean_rel_gap.test]]` | verified | 0.01418517963 |
| 217 | outcomes | Expressed relative to the observed rate that difference is 0… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 218 | outcomes | The same relative comparison on train is 8.266e-05 . | 8.266e-05 | ratio | mean_rel_gap | train | eq | `[[art:ca4e4c16:calibration.mean_rel_gap.train]]` | verified | 8.26634452e-05 |
| 219 | outcomes | AUC on this slice is 0.5721 , falling 0.1783 below AUC on al… | 0.5721 | ratio | auc | test | eq | `[[art:218a0547:metrics.test.sub.utilisation_high.auc]]` | verified | 0.5721242236 |
| 220 | outcomes | AUC on this slice is 0.5721 , falling 0.1783 below AUC on al… | 0.1783 | ratio | auc_gap | test | eq | `[[art:951b2d25:metrics.test.sub.utilisation_high.auc_gap]]` | verified | 0.1783446089 |
| 221 | outcomes | AUC on this slice is 0.5721 , falling 0.1783 below AUC on al… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 222 | outcomes | The slice holds 0.5 of the split, above the floor of 0.1 a s… | 0.5 | ratio | share | test | eq | `[[art:9404484e:metrics.test.sub.utilisation_high.share]]` | verified | 0.5 |
| 223 | outcomes | The slice holds 0.5 of the split, above the floor of 0.1 a s… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 224 | outcomes | The slice holds 0.5 of the split, above the floor of 0.1 a s… | 0.95 | ratio | slice_max_share |  | eq | `[[art:a928a05c:threshold.O1.slice_max_share]]` | verified | 0.95 |
| 225 | outcomes | Mean predicted on the slice is 0.2294 against an observed ra… | 0.2294 | ratio | mean_predicted | test | eq | `[[art:baa1ca0c:metrics.test.sub.utilisation_high.mean_predicted]]` | verified | 0.2293755486 |
| 226 | outcomes | Mean predicted on the slice is 0.2294 against an observed ra… | 0.2333 | ratio | event_rate | test | eq | `[[art:8e66209c:metrics.test.sub.utilisation_high.event_rate]]` | verified | 0.2333333333 |
| 227 | outcomes | Mean predicted on the slice is 0.2294 against an observed ra… | 0.01696 | ratio | mean_rel_gap | test | eq | `[[art:5d3f4d10:metrics.test.sub.utilisation_high.mean_rel_gap]]` | verified | 0.01696193476 |
| 228 | outcomes | Mean predicted on the slice is 0.2294 against an observed ra… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 229 | outcomes | AUC on this slice is 0.8998 , and the shortfall against AUC… | 0.8998 | ratio | auc | test | eq | `[[art:024542ae:metrics.test.sub.utilisation_low.auc]]` | verified | 0.8997753422 |
| 230 | outcomes | AUC on this slice is 0.8998 , and the shortfall against AUC… | -0.1493 | ratio | auc_gap | test | eq | `[[art:70a562d2:metrics.test.sub.utilisation_low.auc_gap]]` | verified | -0.1493065097 |
| 231 | outcomes | AUC on this slice is 0.8998 , and the shortfall against AUC… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 232 | outcomes | The slice holds 0.5 of the split, above the floor of 0.1 and… | 0.5 | ratio | share | test | eq | `[[art:7860a748:metrics.test.sub.utilisation_low.share]]` | verified | 0.5 |
| 233 | outcomes | The slice holds 0.5 of the split, above the floor of 0.1 and… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 234 | outcomes | The slice holds 0.5 of the split, above the floor of 0.1 and… | 0.95 | ratio | slice_max_share |  | eq | `[[art:a928a05c:threshold.O1.slice_max_share]]` | verified | 0.95 |
| 235 | outcomes | Mean predicted here is 0.2136 against an observed rate of 0.… | 0.2136 | ratio | mean_predicted | test | eq | `[[art:3da81c7f:metrics.test.sub.utilisation_low.mean_predicted]]` | verified | 0.2135839107 |
| 236 | outcomes | Mean predicted here is 0.2136 against an observed rate of 0.… | 0.216 | ratio | event_rate | test | eq | `[[art:b0ad49be:metrics.test.sub.utilisation_low.event_rate]]` | verified | 0.216 |
| 237 | outcomes | Mean predicted here is 0.2136 against an observed rate of 0.… | 0.01119 | ratio | mean_rel_gap | test | eq | `[[art:088b852d:metrics.test.sub.utilisation_low.mean_rel_gap]]` | verified | 0.01118559847 |
| 238 | outcomes | Mean predicted here is 0.2136 against an observed rate of 0.… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 239 | outcomes | AUC on this slice is 0.5882 , falling 0.1622 below AUC on al… | 0.5882 | ratio | auc | test | eq | `[[art:18b3a939:metrics.test.sub.delinq_last_high.auc]]` | verified | 0.5882373424 |
| 240 | outcomes | AUC on this slice is 0.5882 , falling 0.1622 below AUC on al… | 0.1622 | ratio | auc_gap | test | eq | `[[art:509039a7:metrics.test.sub.delinq_last_high.auc_gap]]` | verified | 0.1622314901 |
| 241 | outcomes | AUC on this slice is 0.5882 , falling 0.1622 below AUC on al… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 242 | outcomes | The slice covers 0.226 of the split on 339 rows, above the f… | 0.226 | ratio | share | test | eq | `[[art:e795e8a9:metrics.test.sub.delinq_last_high.share]]` | verified | 0.226 |
| 243 | outcomes | The slice covers 0.226 of the split on 339 rows, above the f… | 339 | count | n | test | eq | `[[art:04716bec:metrics.test.sub.delinq_last_high.n]]` | verified | 339 |
| 244 | outcomes | The slice covers 0.226 of the split on 339 rows, above the f… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 245 | outcomes | The slice covers 0.226 of the split on 339 rows, above the f… | 0.95 | ratio | slice_max_share |  | eq | `[[art:a928a05c:threshold.O1.slice_max_share]]` | verified | 0.95 |
| 246 | outcomes | Mean predicted on the slice is 0.4674 against an observed ra… | 0.4674 | ratio | mean_predicted | test | eq | `[[art:281b9e4c:metrics.test.sub.delinq_last_high.mean_predicted]]` | verified | 0.467358238 |
| 247 | outcomes | Mean predicted on the slice is 0.4674 against an observed ra… | 0.5103 | ratio | event_rate | test | eq | `[[art:c9cb7610:metrics.test.sub.delinq_last_high.event_rate]]` | verified | 0.5103244838 |
| 248 | outcomes | Mean predicted on the slice is 0.4674 against an observed ra… | 0.08419 | ratio | mean_rel_gap | test | eq | `[[art:30d42145:metrics.test.sub.delinq_last_high.mean_rel_gap]]` | verified | 0.08419397297 |
| 249 | outcomes | Mean predicted on the slice is 0.4674 against an observed ra… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 250 | sensitivity | The largest variance inflation factor across the retained fe… | 10 | ratio | vif |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 251 | sensitivity | The six-month billing mean is also above the bound at 175.6… | 175.6 | ratio | vif |  | eq | `[[art:964ad8e8:vif.bill_mean_6m]]` | verified | 175.5853575 |
| 252 | sensitivity | The six-month billing mean is also above the bound at 175.6… | 49.46 | ratio | vif |  | eq | `[[art:09540d95:vif.utilisation]]` | verified | 49.45982893 |
| 253 | sensitivity | The six-month billing mean is also above the bound at 175.6… | 50.25 | ratio | vif |  | eq | `[[art:5233c25b:vif.utilisation_mean_6m]]` | verified | 50.24869902 |
| 254 | sensitivity | The remaining retained features sit below the bound: `pay_ra… | 7.269 | ratio | vif |  | eq | `[[art:6fb2f509:vif.pay_ratio_last]]` | verified | 7.268502144 |
| 255 | sensitivity | The remaining retained features sit below the bound: `pay_ra… | 7.261 | ratio | vif |  | eq | `[[art:76c577a1:vif.pay_ratio_mean_6m]]` | verified | 7.261019162 |
| 256 | sensitivity | The remaining retained features sit below the bound: `pay_ra… | 5.551 | ratio | vif |  | eq | `[[art:2d1864b3:vif.bill_trend_6m]]` | verified | 5.551420006 |
| 257 | sensitivity | The remaining retained features sit below the bound: `pay_ra… | 4.845 | ratio | vif |  | eq | `[[art:ffa16c31:vif.limit_bal]]` | verified | 4.844965888 |
| 258 | sensitivity | The remaining retained features sit below the bound: `pay_ra… | 2.562 | ratio | vif |  | eq | `[[art:0e627a7d:vif.delinq_count_6m]]` | verified | 2.561994785 |
| 259 | sensitivity | The remaining retained features sit below the bound: `pay_ra… | 2.409 | ratio | vif |  | eq | `[[art:c31719bd:vif.delinq_max_6m]]` | verified | 2.408601442 |
| 260 | sensitivity | The remaining retained features sit below the bound: `pay_ra… | 1.411 | ratio | vif |  | eq | `[[art:5fce8331:vif.delinq_last]]` | verified | 1.411351267 |
| 261 | sensitivity | The remaining retained features sit below the bound: `pay_ra… | 1.002 | ratio | vif |  | eq | `[[art:c4867fa9:vif.age]]` | verified | 1.001693015 |
| 262 | sensitivity | Belsley's condition number of the column-standardised design… | 1023 | ratio | condition_number |  | eq | `[[art:36c154df:condition_number]]` | verified | 1023.412969 |
| 263 | sensitivity | Belsley's condition number of the column-standardised design… | 30 | ratio | condition_number |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 264 | findings | The largest variance inflation factor on train is 121913.629… | 121913.6293 | ratio | vif | train | eq | `[[art:e6655d27:vif.max]]` | verified | 121913.6293 |
| 265 | findings | The largest variance inflation factor on train is 121913.629… | 121913.6293 | ratio | vif | train | eq | `[[art:5216ecf3:vif.bill_last_adj]]` | verified | 121913.6293 |
| 266 | findings | The largest variance inflation factor on train is 121913.629… | 10 | ratio | vif |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 267 | findings | The raw last-bill column stands at 121617.0493 , the six-mon… | 121617.0493 | ratio | vif | train | eq | `[[art:9139aeac:vif.bill_last]]` | verified | 121617.0493 |
| 268 | findings | The raw last-bill column stands at 121617.0493 , the six-mon… | 175.6 | ratio | vif | train | eq | `[[art:964ad8e8:vif.bill_mean_6m]]` | verified | 175.5853575 |
| 269 | findings | The raw last-bill column stands at 121617.0493 , the six-mon… | 50.25 | ratio | vif | train | eq | `[[art:5233c25b:vif.utilisation_mean_6m]]` | verified | 50.24869902 |
| 270 | findings | The raw last-bill column stands at 121617.0493 , the six-mon… | 49.46 | ratio | vif | train | eq | `[[art:09540d95:vif.utilisation]]` | verified | 49.45982893 |
| 271 | findings | Belsley's condition number of the column-standardised design… | 1023 | ratio | condition_number | train | eq | `[[art:36c154df:condition_number]]` | verified | 1023.412969 |
| 272 | findings | Belsley's condition number of the column-standardised design… | 30 | ratio | condition_number |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 273 | findings | The challenger reaches an AUC on test of 0.8249 against the… | 0.8249 | ratio | auc | test | eq | `[[art:9727c6a9:challenger.auc]]` | verified | 0.8249130587 |
| 274 | findings | The challenger reaches an AUC on test of 0.8249 against the… | 0.7505 | ratio | auc | test | eq | `[[art:3bbb3e37:metrics.test.auc]]` | verified | 0.7504688325 |
| 275 | findings | The challenger's lead over the champion is 0.07444 , above t… | 0.07444 | ratio | delta_auc | test | eq | `[[art:d7dbe8ff:challenger.delta_auc]]` | verified | 0.07444422615 |
| 276 | findings | The challenger's lead over the champion is 0.07444 , above t… | 0.03 | ratio | delta_auc |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 277 | findings | Can the model developer explain what the model discriminates… | 0.5882 | ratio | auc | test | eq | `[[art:18b3a939:metrics.test.sub.delinq_last_high.auc]]` | verified | 0.5882373424 |
| 278 | findings | Can the model developer explain what the model discriminates… | 0.7505 | ratio | auc | test | eq | `[[art:3bbb3e37:metrics.test.auc]]` | verified | 0.7504688325 |
| 279 | findings | Can the model developer explain what the model discriminates… | 0.1622 | ratio | auc_gap | test | eq | `[[art:509039a7:metrics.test.sub.delinq_last_high.auc_gap]]` | verified | 0.1622314901 |
| 280 | findings | Can the model developer explain what the model discriminates… | 0.08 | ratio | auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 281 | findings | Can the model developer explain what the model discriminates… | 0.226 | ratio | share | test | eq | `[[art:e795e8a9:metrics.test.sub.delinq_last_high.share]]` | verified | 0.226 |
| 282 | findings | Can the model developer explain what the model discriminates… | 0.1 | ratio | share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 283 | findings | Can the model developer explain what the model discriminates… | 0.5721 | ratio | auc | test | eq | `[[art:218a0547:metrics.test.sub.utilisation_high.auc]]` | verified | 0.5721242236 |
| 284 | findings | Can the model developer explain what the model discriminates… | 0.7505 | ratio | auc | test | eq | `[[art:3bbb3e37:metrics.test.auc]]` | verified | 0.7504688325 |
| 285 | findings | Can the model developer explain what the model discriminates… | 0.1783 | ratio | auc_gap | test | eq | `[[art:951b2d25:metrics.test.sub.utilisation_high.auc_gap]]` | verified | 0.1783446089 |
| 286 | findings | Can the model developer explain what the model discriminates… | 0.08 | ratio | auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 287 | findings | Can the model developer explain what the model discriminates… | 0.5 | ratio | share | test | eq | `[[art:9404484e:metrics.test.sub.utilisation_high.share]]` | verified | 0.5 |
| 288 | findings | Can the model developer explain what the model discriminates… | 0.1 | ratio | share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 289 | findings | Can the model developer say what makes the fitted coefficien… | 1 | ratio | coef_sign |  | eq | `[[art:a457c04a:sign_check.bill_mean_6m.coef_sign]]` | verified | 1 |
| 290 | findings | Can the model developer say what makes the fitted coefficien… | -1 | ratio | univariate_direction | train | eq | `[[art:23b89c5d:sign_check.bill_mean_6m.univariate_direction]]` | verified | -1 |
| 291 | findings | Can the model developer say what makes the fitted coefficien… | 0 | ratio | agrees |  | eq | `[[art:4df8b747:sign_check.bill_mean_6m.agrees]]` | verified | 0 |
| 292 | findings | Can the model developer say what makes the fitted coefficien… | -1 | ratio | coef_sign |  | eq | `[[art:a07d68ab:sign_check.delinq_max_6m.coef_sign]]` | verified | -1 |
| 293 | findings | Can the model developer say what makes the fitted coefficien… | 1 | ratio | univariate_direction | train | eq | `[[art:b9088f4a:sign_check.delinq_max_6m.univariate_direction]]` | verified | 1 |
| 294 | findings | Can the model developer say what makes the fitted coefficien… | 0 | ratio | agrees |  | eq | `[[art:c946359c:sign_check.delinq_max_6m.agrees]]` | verified | 0 |
| 295 | findings | Can the model developer say what makes the fitted coefficien… | 1 | ratio | coef_sign |  | eq | `[[art:6af6aef2:sign_check.limit_bal.coef_sign]]` | verified | 1 |
| 296 | findings | Can the model developer say what makes the fitted coefficien… | -1 | ratio | univariate_direction | train | eq | `[[art:56d284d6:sign_check.limit_bal.univariate_direction]]` | verified | -1 |
| 297 | findings | Can the model developer say what makes the fitted coefficien… | 0 | ratio | agrees |  | eq | `[[art:0278aad1:sign_check.limit_bal.agrees]]` | verified | 0 |
| 298 | findings | Can the model developer say what makes the fitted coefficien… | 1 | ratio | coef_sign |  | eq | `[[art:f018263e:sign_check.pay_ratio_last.coef_sign]]` | verified | 1 |
| 299 | findings | Can the model developer say what makes the fitted coefficien… | -1 | ratio | univariate_direction | train | eq | `[[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]]` | verified | -1 |
| 300 | findings | Can the model developer say what makes the fitted coefficien… | 0 | ratio | agrees |  | eq | `[[art:79abee77:sign_check.pay_ratio_last.agrees]]` | verified | 0 |
| 301 | monitoring | - Recompute rank-ordering performance on each production coh… | 0.7 | ratio | auc | test | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 302 | monitoring | - Recompute rank-ordering performance on each production coh… | 0.7505 | ratio | auc | test | eq | `[[art:3bbb3e37:metrics.test.auc]]` | verified | 0.7504688325 |
| 303 | monitoring | - Recompute the mean squared error of the predicted probabil… | 0.2 | ratio | brier | test | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 304 | monitoring | - Recompute the mean squared error of the predicted probabil… | 0.1486 | ratio | brier | test | eq | `[[art:08bbf5ff:metrics.test.brier]]` | verified | 0.1486259309 |
| 305 | monitoring | - Refit the logistic regression of the outcome on the log-od… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 306 | monitoring | - Refit the logistic regression of the outcome on the log-od… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 307 | monitoring | - Refit the logistic regression of the outcome on the log-od… | 0.9988 | ratio | calibration_slope | test | eq | `[[art:6d8bca25:calibration_slope.test]]` | verified | 0.9988191006 |
| 308 | monitoring | - Track the largest population stability index across the sc… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 309 | monitoring | - Run that stability measurement on the fastest cycle the sc… | 0.01372 | ratio | psi |  | eq | `[[art:d34e2b0f:psi.max]]` | verified | 0.01371561255 |
| 310 | monitoring | - Where a future cohort's event rate falls below 0.05 , that… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |

## Appendix B — Artifact index

The store holds 228 artifacts; the 181 this report cites or rests a finding on are indexed here.

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
| `metrics.test.sub.delinq_last_high` | `2dbecccd` | table | table, 10 rows | every metric on the delinq_last above_median slice of test |
| `metrics.test.sub.delinq_last_high.auc` | `18b3a939` | scalar | 0.5882373424 | auc on the delinq_last above_median slice of test |
| `metrics.test.sub.delinq_last_high.auc_gap` | `509039a7` | scalar | 0.1622314901 | how far AUC on the delinq_last above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.delinq_last_high.brier` | `52704467` | scalar | 0.2544916143 | brier on the delinq_last above_median slice of test |
| `metrics.test.sub.delinq_last_high.event_rate` | `c9cb7610` | scalar | 0.5103244838 | event_rate on the delinq_last above_median slice of test |
| `metrics.test.sub.delinq_last_high.gini` | `18db302d` | scalar | 0.1764746849 | gini on the delinq_last above_median slice of test |
| `metrics.test.sub.delinq_last_high.ks` | `cb7c41a9` | scalar | 0.1701023748 | ks on the delinq_last above_median slice of test |
| `metrics.test.sub.delinq_last_high.logloss` | `9c722397` | scalar | 0.7110097275 | logloss on the delinq_last above_median slice of test |
| `metrics.test.sub.delinq_last_high.mean_predicted` | `281b9e4c` | scalar | 0.467358238 | mean_predicted on the delinq_last above_median slice of test |
| `metrics.test.sub.delinq_last_high.mean_rel_gap` | `30d42145` | scalar | 0.08419397297 | mean predicted against observed on the delinq_last above_median slice of test, relative |
| `metrics.test.sub.delinq_last_high.n` | `04716bec` | scalar | 339 | n on the delinq_last above_median slice of test |
| `metrics.test.sub.delinq_last_high.share` | `e795e8a9` | scalar | 0.226 | the share of test the delinq_last above_median slice holds |
| `metrics.test.sub.utilisation_high` | `a5faad4f` | table | table, 10 rows | every metric on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.auc` | `218a0547` | scalar | 0.5721242236 | auc on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.auc_gap` | `951b2d25` | scalar | 0.1783446089 | how far AUC on the utilisation above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.utilisation_high.brier` | `c584f815` | scalar | 0.1941849919 | brier on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.event_rate` | `8e66209c` | scalar | 0.2333333333 | event_rate on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.gini` | `cc2438a9` | scalar | 0.1442484472 | gini on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.ks` | `9b8e4cad` | scalar | 0.149068323 | ks on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.logloss` | `b9f7b201` | scalar | 0.585308331 | logloss on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.mean_predicted` | `baa1ca0c` | scalar | 0.2293755486 | mean_predicted on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.mean_rel_gap` | `5d3f4d10` | scalar | 0.01696193476 | mean predicted against observed on the utilisation above_median slice of test, relative |
| `metrics.test.sub.utilisation_high.n` | `ea5b0084` | scalar | 750 | n on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.share` | `9404484e` | scalar | 0.5 | the share of test the utilisation above_median slice holds |
| `metrics.test.sub.utilisation_low` | `37b022cf` | table | table, 10 rows | every metric on the utilisation below_median slice of test |
| `metrics.test.sub.utilisation_low.auc` | `024542ae` | scalar | 0.8997753422 | auc on the utilisation below_median slice of test |
| `metrics.test.sub.utilisation_low.auc_gap` | `70a562d2` | scalar | -0.1493065097 | how far AUC on the utilisation below_median slice of test falls below AUC on all of test |
| `metrics.test.sub.utilisation_low.brier` | `39a0bd66` | scalar | 0.10306687 | brier on the utilisation below_median slice of test |
| `metrics.test.sub.utilisation_low.event_rate` | `b0ad49be` | scalar | 0.216 | event_rate on the utilisation below_median slice of test |
| `metrics.test.sub.utilisation_low.gini` | `39c7fd9b` | scalar | 0.7995506845 | gini on the utilisation below_median slice of test |
| `metrics.test.sub.utilisation_low.ks` | `0be83ffa` | scalar | 0.7642353238 | ks on the utilisation below_median slice of test |
| `metrics.test.sub.utilisation_low.logloss` | `896b4831` | scalar | 0.3486357318 | logloss on the utilisation below_median slice of test |
| `metrics.test.sub.utilisation_low.mean_predicted` | `3da81c7f` | scalar | 0.2135839107 | mean_predicted on the utilisation below_median slice of test |
| `metrics.test.sub.utilisation_low.mean_rel_gap` | `088b852d` | scalar | 0.01118559847 | mean predicted against observed on the utilisation below_median slice of test, relative |
| `metrics.test.sub.utilisation_low.n` | `5b0bae29` | scalar | 750 | n on the utilisation below_median slice of test |
| `metrics.test.sub.utilisation_low.share` | `7860a748` | scalar | 0.5 | the share of test the utilisation below_median slice holds |
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
| `run.features` | `f79bb8bb` | json | json | the subject's features.json |
| `run.model_summary` | `f2e0e9a7` | json | json | the subject's model_summary.json |
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |
| `sign_check.age.agrees` | `4116add1` | scalar | 1 | 1 when the fitted sign on age agrees with its univariate direction, 0 when it does not |
| `sign_check.bill_last.agrees` | `98c00451` | scalar | 1 | 1 when the fitted sign on bill_last agrees with its univariate direction, 0 when it does not |
| `sign_check.bill_last_adj.agrees` | `fb9031bc` | scalar | 1 | 1 when the fitted sign on bill_last_adj agrees with its univariate direction, 0 when it does not |
| `sign_check.bill_mean_6m.agrees` | `4df8b747` | scalar | 0 | 1 when the fitted sign on bill_mean_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.bill_mean_6m.coef_sign` | `a457c04a` | scalar | 1 | the sign of the fitted coefficient on bill_mean_6m |
| `sign_check.bill_mean_6m.univariate_direction` | `23b89c5d` | scalar | -1 | the sign of bill_mean_6m's own single-feature AUC on train minus 0.5 |
| `sign_check.bill_trend_6m.agrees` | `ff3cb24a` | scalar | 1 | 1 when the fitted sign on bill_trend_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.delinq_count_6m.agrees` | `a337d16b` | scalar | 1 | 1 when the fitted sign on delinq_count_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.delinq_last.agrees` | `a8ba9372` | scalar | 1 | 1 when the fitted sign on delinq_last agrees with its univariate direction, 0 when it does not |
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
| `sign_check.utilisation.agrees` | `d0c9a130` | scalar | 1 | 1 when the fitted sign on utilisation agrees with its univariate direction, 0 when it does not |
| `sign_check.utilisation_mean_6m.agrees` | `c2848161` | scalar | 1 | 1 when the fitted sign on utilisation_mean_6m agrees with its univariate direction, 0 when it does not |
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
| `threshold.O1.slice_auc_gap` | `0a827b87` | scalar | 0.08 | how far a sub-population's AUC may fall below the split's before the result is an open item; it raises no candidate |
| `threshold.O1.slice_max_share` | `a928a05c` | scalar | 0.95 | the share of a split at which a sub-population is the whole split and is refused |
| `threshold.O1.slice_min_share` | `9a6f1a87` | scalar | 0.1 | the share of a split a sub-population must hold before it can raise an open item |
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
| tool calls | 17 (run_model 1, profile_data 1, compute_metrics 4, check_leakage 1, check_collinearity 2, challenger_compare 1, retrieve_guidance 7) |
| plan steps (bounded loop) | 4 |
| LLM calls | 22 (plan 4, draft 9, extract 9) |
| re-asks | 0 |
| repair rounds | 2 |
| tokens in / out | 259,791 / 135,200 |
| notional cost (USD) | 6.0171 |
| wall-clock (s) | 1464.45 |
| subject run (s) | 1.38 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | credit_default-full_agent-20260920T080337Z-e2e51e00 |

## Appendix D — Not checked

| item | reason |
|---|---|
| `check_stability` (R1) | package declares no `regime.column` |
| `run_scenarios` (X1) | not applicable to `binary_classification` |
| out-of-time and vintage-holdout metrics (O1, second rule) | package declares neither split |
| developer claims (T1, claim channel) | The package declares 2 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
