---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: full_agent
model: illustrative
run_id: illustrative-0000
data_mode: synthetic
synthetic_n: 5000
grounding_precision_pre: 0.9783
grounding_precision_post: 1.0000
n_claims: 92
n_findings_by_severity: {high: 0, medium: 0, low: 1, info: 0}
generated: "2026-09-07T00:00:00Z"
illustrative: true
---

# Validation report — `credit_default` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `credit_default` v1.0 | `full_agent` | illustrative | synthetic, n = 5000 | 0.9783 → 1.0000 | 0 / 0 / 1 / 0 |
<!-- quaestor:renderer:end -->

This report validates `credit_default` version 1.0, a binary-classification model that scores the probability that a credit-card client defaults on next month's payment, following the structure of the Federal Reserve's model risk management guidance [[reg:SR11-7:V]] and the elements of comprehensive validation it names [[reg:SR11-7:V.1]].
The subject ran in synthetic mode, drawing its data from the package's documented generating process; the training split holds 3,500 [[art:42612024:profile.train.n]] clients and the test split 1,500 [[art:96315a22:profile.test.n]], with an observed default rate of 22.0% [[art:d51a015c:metrics.train.event_rate]] in training and 22.0% [[art:54418164:metrics.test.event_rate]] in test.
Configuration `full_agent`: the rule-based plan ran seven tools; the bounded follow-up loop requested one additional check and stopped; every section below was drafted from the resulting artifacts, and every numeric claim in it was extracted and matched against the artifact store (Appendix A).
Headline: the model passes all four developer-declared thresholds — test AUC 0.7412 [[art:4bb1344e:metrics.test.auc]] against a floor of 0.70 [[art:af7a11b2:threshold.package.auc.test.min]], Brier score 0.1428 [[art:2c220200:metrics.test.brier]] against a ceiling of 0.20 [[art:06b3d754:threshold.package.brier.test.max]], calibration slope 0.9712 [[art:ab09adf2:calibration_slope.test]] inside [0.80 [[art:f495f499:threshold.package.calibration_slope.test.min]], 1.20 [[art:c3cc3580:threshold.package.calibration_slope.test.max]]], and a maximum feature PSI of 0.021 [[art:b9e6b86f:psi.max]] against a ceiling of 0.25 [[art:0c87f8b4:threshold.package.psi.max]].
One finding is raised, at low severity: a gradient-boosting challenger outperforms the logistic champion by more than the effective-challenge threshold (F-001, §6). No finding of high or medium severity was raised; the leakage, contamination, drift, integrity and collinearity checks produced no candidate.

## 2. Conceptual soundness

The guidance asks the validator to assess the quality of the model design and construction, the choice of variables and the logic that connects them to the outcome [[reg:SR11-7:V.1.a]].
The champion is a logistic regression fitted on a stratified training split with default class weights, with probabilities taken directly from the fitted model; the package declares 12 [[art:8b373477:run.features#n]] engineered features, of which 2 [[art:8b373477:run.features#at_origination]] are known at origination and 10 [[art:8b373477:run.features#before_period_start]] are computed from statements that close before the observation month begins, and none is declared as observed during or after the outcome window.
The subject's own VIF screen removed one feature before fitting, `bill_last`, whose variance inflation factor of 41.7 [[art:843f4548:run.model_summary#removed.bill_last.vif]] reflects its near-duplication of `bill_mean_6m`; the eleven retained features are the ones every check below examines.
The three largest standardised coefficients are on `delinq_last` (0.612 [[art:843f4548:run.model_summary#coefficients.delinq_last.value]]), `utilisation` (0.487 [[art:843f4548:run.model_summary#coefficients.utilisation.value]]) and `delinq_count_6m` (0.298 [[art:843f4548:run.model_summary#coefficients.delinq_count_6m.value]]), all positive; `pay_ratio_mean_6m` (-0.244 [[art:843f4548:run.model_summary#coefficients.pay_ratio_mean_6m.value]]) and `limit_bal` (-0.171 [[art:843f4548:run.model_summary#coefficients.limit_bal.value]]) are negative, which is the direction credit intuition expects.
As effective challenge, a histogram gradient-boosting classifier fitted on the same eleven features reaches a test AUC of 0.7735 [[art:d995c29d:challenger.auc]] against the champion's 0.7412 [[art:4bb1344e:metrics.test.auc]], a difference of 0.0323 [[art:02d4d1a8:challenger.delta_auc]] that exceeds the effective-challenge threshold of 0.03 [[art:de8d94b3:threshold.E1.delta_auc]]; the challenger's Brier score is 0.1392 [[art:6bfc68f5:challenger.brier]].
The gap is consistent with a non-linearity the additive logit does not capture, most plausibly an interaction between utilisation and current delinquency; this is finding F-001 (§6). It is a question about the champion's functional form, not about its data.

## 3. Data integrity and drift

Sound model development depends on data that is suitable for the model's purpose and is checked for accuracy and completeness [[reg:SR11-7:IV.1]]; the validator should confirm that the data used in development and testing are representative [[reg:SR11-7:V.1.a]].
No feature has any missing value in either split (maximum missing fraction 0.0 [[art:36356ec7:profile.train.missing.max]] in training and 0.0 [[art:fc3dde37:profile.test.missing.max]] in test), so the data-integrity screen, which fires when missingness differs between splits by more than 10% [[art:527fd926:threshold.D1.missing_gap]] (ten percentage points) on any feature, raised no candidate.
Population stability between the training and test splits is high: the largest feature PSI is 0.021 [[art:0cd1eb2f:psi.utilisation]] on `utilisation`, the PSI of the score itself is 0.014 [[art:d5ad1386:psi.y_score]], and the largest characteristic stability index is 0.018 [[art:7daee19d:csi.max]]; all are far below the 0.25 [[art:0c87f8b4:threshold.package.psi.max]] threshold the package declares.
The leakage screens are clean: no feature is declared during or after the outcome window (0 [[art:ceda5706:leakage.timing.n_flagged]] flagged), the strongest single feature, `delinq_last`, has an AUC of 0.6812 [[art:949c3049:leakage.target_corr.max_single_feature_auc]] on its own against a leakage threshold of 0.90 [[art:8e765a47:threshold.L1.single_feature_auc]], the fraction of test rows whose hash appears in training is 0.0000 [[art:b2c21e16:leakage.overlap]] against a contamination threshold of 0.5% [[art:6ff7c573:threshold.L2.overlap]], and 0 [[art:535e256a:leakage.name_screen.n_matched]] feature names match the target-adjacent lexicon.

## 4. Outcomes analysis

Outcomes analysis compares model outputs to corresponding actual outcomes [[reg:SR11-7:V.1.c]]; because the observed default rate is 22.0% [[art:54418164:metrics.test.event_rate]], well above the 5% [[art:5acffd33:rule.calibration_first_event_rate]] below which this report would place calibration before discrimination, discrimination is reported before calibration.

| metric | train | test |
|---|---|---|
| AUC | 0.7538 [[art:dd1bb63e:metrics.train.auc]] | 0.7412 [[art:4bb1344e:metrics.test.auc]] |
| Gini | 0.5076 [[art:970da634:metrics.train.gini]] | 0.4824 [[art:0c3e4bc9:metrics.test.gini]] |
| KS | 0.3702 [[art:db884f7a:metrics.train.ks]] | 0.3617 [[art:5fdb3051:metrics.test.ks]] |
| Brier | 0.1401 [[art:707e58aa:metrics.train.brier]] | 0.1428 [[art:2c220200:metrics.test.brier]] |
| log loss | 0.4407 [[art:595f5afb:metrics.train.logloss]] | 0.4471 [[art:e06c9ee8:metrics.test.logloss]] |
| n | 3,500 [[art:f696a6ea:metrics.train.n]] | 1,500 [[art:2dd7648b:metrics.test.n]] |

The train-to-test AUC gap is 0.0126 [[art:4bb1344e:metrics.test.auc]][[art:dd1bb63e:metrics.train.auc]], against a generalisation-gap threshold of 0.08 [[art:a13c0174:threshold.O1.auc_gap]]; there is no evidence of overfitting.
Calibration is close to the identity: the slope of a logistic regression of the outcome on the logit of the predicted probability is 0.9712 [[art:ab09adf2:calibration_slope.test]] with intercept -0.021 [[art:e53b6ceb:calibration_intercept.test]], and the mean predicted probability of 0.2213 [[art:5e0d91b1:metrics.test.mean_predicted]] differs from the observed rate of 0.2200 [[art:54418164:metrics.test.event_rate]] by 0.6% [[art:ba1b605e:calibration.mean_rel_gap.test]] relative, inside the 25% [[art:92720b9b:threshold.C1.mean_ratio_rel]] tolerance of the miscalibration check.

<!-- quaestor:renderer:begin table calibration.test -->
Calibration by decile of predicted probability, test split [[art:1c01dc55:calibration.test]]:

| bin | mean predicted | observed | count |
|---|---|---|---|
| 1 | 0.052 | 0.047 | 150 |
| 2 | 0.089 | 0.087 | 150 |
| 3 | 0.118 | 0.120 | 150 |
| 4 | 0.149 | 0.153 | 150 |
| 5 | 0.183 | 0.187 | 150 |
| 6 | 0.218 | 0.220 | 150 |
| 7 | 0.256 | 0.253 | 150 |
| 8 | 0.298 | 0.293 | 150 |
| 9 | 0.352 | 0.347 | 150 |
| 10 | 0.498 | 0.493 | 150 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table deciles.test -->
Decile separation, test split; the first decile holds the highest predicted probabilities [[art:20368492:deciles.test]]:

| decile | count | events | event rate | lift |
|---|---|---|---|---|
| 1 | 150 | 74 | 0.493 | 2.24 |
| 2 | 150 | 52 | 0.347 | 1.58 |
| 3 | 150 | 44 | 0.293 | 1.33 |
| 4 | 150 | 38 | 0.253 | 1.15 |
| 5 | 150 | 33 | 0.220 | 1.00 |
| 6 | 150 | 28 | 0.187 | 0.85 |
| 7 | 150 | 23 | 0.153 | 0.70 |
| 8 | 150 | 18 | 0.120 | 0.55 |
| 9 | 150 | 13 | 0.087 | 0.40 |
| 10 | 150 | 7 | 0.047 | 0.21 |
<!-- quaestor:renderer:end -->

The top decile has a default rate of 0.493 [[art:20368492:deciles.test#1.event_rate]], a lift of 2.24 [[art:20368492:deciles.test#1.lift]] over the base rate, and the top two deciles together capture 38.2% [[art:9d783477:deciles.test.top2_capture]] of all defaults.

Developer-declared thresholds:

| metric | split | rule | Quaestor value | result |
|---|---|---|---|---|
| AUC | test | ≥ 0.70 [[art:af7a11b2:threshold.package.auc.test.min]] | 0.7412 [[art:4bb1344e:metrics.test.auc]] | pass |
| Brier | test | ≤ 0.20 [[art:06b3d754:threshold.package.brier.test.max]] | 0.1428 [[art:2c220200:metrics.test.brier]] | pass |
| calibration slope | test | in [0.80 [[art:f495f499:threshold.package.calibration_slope.test.min]], 1.20 [[art:c3cc3580:threshold.package.calibration_slope.test.max]]] | 0.9712 [[art:ab09adf2:calibration_slope.test]] | pass |
| PSI | all features | ≤ 0.25 [[art:0c87f8b4:threshold.package.psi.max]] | max 0.021 [[art:b9e6b86f:psi.max]] | pass |

The developer's own `metrics.json` reports a test AUC of 0.7412 [[art:557c701c:run.metrics#test.auc]] and a Brier score of 0.1428 [[art:557c701c:run.metrics#test.brier]], which agree with Quaestor's independent computation above; developer-computed metrics are never used in place of Quaestor's own.
Follow-up requested by the planner: discrimination by credit-limit half. On the 750 [[art:73bf248c:metrics.test.sub.limit_bal_low.n]] test clients with `limit_bal` below the median the AUC is 0.7188 [[art:718aed91:metrics.test.sub.limit_bal_low.auc]], against 0.7590 [[art:60ef92d1:metrics.test.sub.limit_bal_high.auc]] on the upper half; the model discriminates less well among low-limit clients, which is recorded as a monitoring recommendation (§7) rather than a finding because no threshold governs it.

## 5. Sensitivity and scenario analysis

Sensitivity analysis and the assessment of a model's stability across the range of inputs it will meet are part of the evaluation of conceptual soundness [[reg:SR11-7:V.1.a]]; benchmarking against alternative models supports ongoing monitoring [[reg:SR11-7:V.1.b]].
After the subject's own screen, multicollinearity among the eleven retained features is moderate: the largest variance inflation factor is 4.31 [[art:9a9e9f38:vif.utilisation]] on `utilisation` (against `utilisation_mean_6m`), well below the 10 [[art:76a42f3d:threshold.M1.vif]] threshold, and the condition number of the standardised design matrix is 18.6 [[art:10f3ad32:condition_number]] against a threshold of 30 [[art:8abf1a99:threshold.M1.condition_number]].
Regime stability was not assessed because the package declares no regime column, and rate-shock scenarios do not apply to a binary classifier; both are listed in Appendix D. The challenger comparison in §2 stands as this report's benchmarking exercise.

## 6. Findings and recommendations

Findings are listed in severity order. Each is a structured object whose evidence is the artifacts cited; a candidate raised by a check that the validator judged not to warrant a finding is listed after the findings with the reason [[reg:SR11-7:V.1]].

### F-001 · E1 effective challenge · severity **low**

**A gradient-boosting challenger outperforms the champion by 0.0323 [[art:02d4d1a8:challenger.delta_auc]] AUC.** The challenger's test AUC of 0.7735 [[art:d995c29d:challenger.auc]] exceeds the champion's 0.7412 [[art:4bb1344e:metrics.test.auc]] by more than the 0.03 [[art:de8d94b3:threshold.E1.delta_auc]] effective-challenge threshold.
The champion's additive logit appears to miss an interaction, most plausibly between utilisation and current delinquency. Severity is kept at the check's suggested level, low, because the champion passes every declared threshold and the gap does not by itself indicate a defect. Recommendation: the developer should test an interaction term or a spline on `utilisation` in the champion and document the choice; if the gap persists, the choice of a linear form should be justified in the model documentation.

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1, S1), `compute_metrics` (T1, C1, O1), `check_leakage` (L1, L2), `check_collinearity` (M1).

## 7. Ongoing monitoring recommendations

Ongoing monitoring confirms that the model is implemented appropriately and continues to perform as intended as products, exposures and market conditions change [[reg:SR11-7:V.1.b]].
Recommended: (a) monthly PSI on every retained feature and on the score, alarmed at the package's own 0.25 [[art:0c87f8b4:threshold.package.psi.max]]; (b) quarterly recalibration checks with the slope held inside [0.80 [[art:f495f499:threshold.package.calibration_slope.test.min]], 1.20 [[art:c3cc3580:threshold.package.calibration_slope.test.max]]] and the AUC above 0.70 [[art:af7a11b2:threshold.package.auc.test.min]]; (c) AUC tracked separately for clients below the median credit limit, where it was 0.7188 [[art:718aed91:metrics.test.sub.limit_bal_low.auc]] in this validation; (d) if the probability is mapped to a credit-score scale for decisioning, the mapping should be validated separately with an interpretability review, which is outside this report's scope.

## Appendix A — Claims

Grounding precision 0.9783 before repair (90 of 92 claims verified; 1 mismatch, 1 unsupported) and 1.0000 after 2 repaired claims in 1 round. Per section (post-repair): summary 13/13; conceptual_soundness 14/14; data_integrity 13/13; outcomes 39/39; sensitivity 4/4; findings 4/4; monitoring 5/5.

Repairs:

| section | before | after | instruction to the drafter |
|---|---|---|---|
| summary | 3500 (unsupported) | 3500 (verified) | you wrote 3,500 with no citation; the artifact profile.train.n has value 3500; cite or remove |
| outcomes | 0.0136 (mismatch) | 0.0126 (verified) | you wrote 0.0136 for the delta of metrics.test.auc and metrics.train.auc; the artifacts give 0.0126; cite or remove |

Developer claims: none declared in `package.yaml`; synthetic mode does not evaluate them (Appendix D).

Excluded numeric tokens (not claims): section_number (1., §6, F-001); regulatory_section_id (SR 11-7, V.1.c, IV.1); citation_hash (the eight hex characters inside an artifact citation); package_version (1.0); inline_code (`utilisation_mean_6m`, `bill_mean_6m`); renderer_block (scope block under section 1, table directives for calibration.test and deciles.test, expanded from the artifact store); finding_id (F-001).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The subject ran in synthetic mode, drawing its data from th… | 3500 | count |  |  | eq | `[[art:42612024:profile.train.n]]` | verified | 3500 |
| 2 | summary | The subject ran in synthetic mode, drawing its data from th… | 1500 | count |  |  | eq | `[[art:96315a22:profile.test.n]]` | verified | 1500 |
| 3 | summary | The subject ran in synthetic mode, drawing its data from th… | 22 | percent | event_rate | train | eq | `[[art:d51a015c:metrics.train.event_rate]]` | verified | 0.22 |
| 4 | summary | The subject ran in synthetic mode, drawing its data from th… | 22 | percent | event_rate | test | eq | `[[art:54418164:metrics.test.event_rate]]` | verified | 0.22 |
| 5 | summary | Headline: the model passes all four developer-declared thre… | 0.7412 | ratio | auc | test | eq | `[[art:4bb1344e:metrics.test.auc]]` | verified | 0.7412 |
| 6 | summary | Headline: the model passes all four developer-declared thre… | 0.7 | ratio | auc | test | eq | `[[art:af7a11b2:threshold.package.auc.test.min]]` | verified | 0.7 |
| 7 | summary | Headline: the model passes all four developer-declared thre… | 0.1428 | ratio | brier | test | eq | `[[art:2c220200:metrics.test.brier]]` | verified | 0.1428 |
| 8 | summary | Headline: the model passes all four developer-declared thre… | 0.2 | ratio | brier | test | eq | `[[art:06b3d754:threshold.package.brier.test.max]]` | verified | 0.2 |
| 9 | summary | Headline: the model passes all four developer-declared thre… | 0.9712 | ratio | calibration_slope | test | eq | `[[art:ab09adf2:calibration_slope.test]]` | verified | 0.9712 |
| 10 | summary | Headline: the model passes all four developer-declared thre… | 0.8 | ratio | calibration_slope |  | eq | `[[art:f495f499:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 11 | summary | Headline: the model passes all four developer-declared thre… | 1.2 | ratio | calibration_slope |  | eq | `[[art:c3cc3580:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 12 | summary | Headline: the model passes all four developer-declared thre… | 0.021 | ratio | psi |  | eq | `[[art:b9e6b86f:psi.max]]` | verified | 0.021 |
| 13 | summary | Headline: the model passes all four developer-declared thre… | 0.25 | ratio | psi |  | eq | `[[art:0c87f8b4:threshold.package.psi.max]]` | verified | 0.25 |
| 14 | conceptual_soundness | The champion is a logistic regression fitted on a stratifie… | 12 | count |  |  | eq | `[[art:8b373477:run.features#n]]` | verified | 12 |
| 15 | conceptual_soundness | The champion is a logistic regression fitted on a stratifie… | 2 | count |  |  | eq | `[[art:8b373477:run.features#at_origination]]` | verified | 2 |
| 16 | conceptual_soundness | The champion is a logistic regression fitted on a stratifie… | 10 | count |  |  | eq | `[[art:8b373477:run.features#before_period_start]]` | verified | 10 |
| 17 | conceptual_soundness | The subject's own VIF screen removed one feature before fit… | 41.7 | ratio | vif |  | eq | `[[art:843f4548:run.model_summary#removed.bill_last.vif]]` | verified | 41.7 |
| 18 | conceptual_soundness | The three largest standardised coefficients are on `delinq_… | 0.612 | ratio | coefficient |  | eq | `[[art:843f4548:run.model_summary#coefficients.delinq_last.value]]` | verified | 0.612 |
| 19 | conceptual_soundness | The three largest standardised coefficients are on `delinq_… | 0.487 | ratio | coefficient |  | eq | `[[art:843f4548:run.model_summary#coefficients.utilisation.value]]` | verified | 0.487 |
| 20 | conceptual_soundness | The three largest standardised coefficients are on `delinq_… | 0.298 | ratio | coefficient |  | eq | `[[art:843f4548:run.model_summary#coefficients.delinq_count_6m.value]]` | verified | 0.298 |
| 21 | conceptual_soundness | The three largest standardised coefficients are on `delinq_… | -0.244 | ratio | coefficient |  | eq | `[[art:843f4548:run.model_summary#coefficients.pay_ratio_mean_6m.value]]` | verified | -0.244 |
| 22 | conceptual_soundness | The three largest standardised coefficients are on `delinq_… | -0.171 | ratio | coefficient |  | eq | `[[art:843f4548:run.model_summary#coefficients.limit_bal.value]]` | verified | -0.171 |
| 23 | conceptual_soundness | As effective challenge, a histogram gradient-boosting class… | 0.7735 | ratio | auc | test | eq | `[[art:d995c29d:challenger.auc]]` | verified | 0.7735 |
| 24 | conceptual_soundness | As effective challenge, a histogram gradient-boosting class… | 0.7412 | ratio | auc | test | eq | `[[art:4bb1344e:metrics.test.auc]]` | verified | 0.7412 |
| 25 | conceptual_soundness | As effective challenge, a histogram gradient-boosting class… | 0.0323 | ratio | delta_auc | test | eq | `[[art:02d4d1a8:challenger.delta_auc]]` | verified | 0.0323 |
| 26 | conceptual_soundness | As effective challenge, a histogram gradient-boosting class… | 0.03 | ratio | delta_auc |  | eq | `[[art:de8d94b3:threshold.E1.delta_auc]]` | verified | 0.03 |
| 27 | conceptual_soundness | As effective challenge, a histogram gradient-boosting class… | 0.1392 | ratio | brier | test | eq | `[[art:6bfc68f5:challenger.brier]]` | verified | 0.1392 |
| 28 | data_integrity | No feature has any missing value in either split (maximum m… | 0 | ratio | missing_fraction | train | eq | `[[art:36356ec7:profile.train.missing.max]]` | verified | 0 |
| 29 | data_integrity | No feature has any missing value in either split (maximum m… | 0 | ratio | missing_fraction | test | eq | `[[art:fc3dde37:profile.test.missing.max]]` | verified | 0 |
| 30 | data_integrity | No feature has any missing value in either split (maximum m… | 10 | percent | missing_gap |  | eq | `[[art:527fd926:threshold.D1.missing_gap]]` | verified | 0.1 |
| 31 | data_integrity | Population stability between the training and test splits i… | 0.021 | ratio | psi |  | eq | `[[art:0cd1eb2f:psi.utilisation]]` | verified | 0.021 |
| 32 | data_integrity | Population stability between the training and test splits i… | 0.014 | ratio | psi | test | eq | `[[art:d5ad1386:psi.y_score]]` | verified | 0.014 |
| 33 | data_integrity | Population stability between the training and test splits i… | 0.018 | ratio | csi |  | eq | `[[art:7daee19d:csi.max]]` | verified | 0.018 |
| 34 | data_integrity | Population stability between the training and test splits i… | 0.25 | ratio | psi |  | eq | `[[art:0c87f8b4:threshold.package.psi.max]]` | verified | 0.25 |
| 35 | data_integrity | The leakage screens are clean: no feature is declared durin… | 0 | count |  |  | eq | `[[art:ceda5706:leakage.timing.n_flagged]]` | verified | 0 |
| 36 | data_integrity | The leakage screens are clean: no feature is declared durin… | 0.6812 | ratio | auc | train | eq | `[[art:949c3049:leakage.target_corr.max_single_feature_auc]]` | verified | 0.6812 |
| 37 | data_integrity | The leakage screens are clean: no feature is declared durin… | 0.9 | ratio | auc |  | eq | `[[art:8e765a47:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 38 | data_integrity | The leakage screens are clean: no feature is declared durin… | 0 | ratio | overlap |  | eq | `[[art:b2c21e16:leakage.overlap]]` | verified | 0 |
| 39 | data_integrity | The leakage screens are clean: no feature is declared durin… | 0.5 | percent | overlap |  | eq | `[[art:6ff7c573:threshold.L2.overlap]]` | verified | 0.005 |
| 40 | data_integrity | The leakage screens are clean: no feature is declared durin… | 0 | count |  |  | eq | `[[art:535e256a:leakage.name_screen.n_matched]]` | verified | 0 |
| 41 | outcomes | Outcomes analysis compares model outputs to corresponding a… | 22 | percent | event_rate | test | eq | `[[art:54418164:metrics.test.event_rate]]` | verified | 0.22 |
| 42 | outcomes | Outcomes analysis compares model outputs to corresponding a… | 5 | percent | event_rate |  | eq | `[[art:5acffd33:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 43 | outcomes | \| AUC \| 0.7538 \| 0.7412 \| | 0.7538 | ratio | auc | train | eq | `[[art:dd1bb63e:metrics.train.auc]]` | verified | 0.7538 |
| 44 | outcomes | \| AUC \| 0.7538 \| 0.7412 \| | 0.7412 | ratio | auc | test | eq | `[[art:4bb1344e:metrics.test.auc]]` | verified | 0.7412 |
| 45 | outcomes | \| Gini \| 0.5076 \| 0.4824 \| | 0.5076 | ratio | gini | train | eq | `[[art:970da634:metrics.train.gini]]` | verified | 0.5076 |
| 46 | outcomes | \| Gini \| 0.5076 \| 0.4824 \| | 0.4824 | ratio | gini | test | eq | `[[art:0c3e4bc9:metrics.test.gini]]` | verified | 0.4824 |
| 47 | outcomes | \| KS \| 0.3702 \| 0.3617 \| | 0.3702 | ratio | ks | train | eq | `[[art:db884f7a:metrics.train.ks]]` | verified | 0.3702 |
| 48 | outcomes | \| KS \| 0.3702 \| 0.3617 \| | 0.3617 | ratio | ks | test | eq | `[[art:5fdb3051:metrics.test.ks]]` | verified | 0.3617 |
| 49 | outcomes | \| Brier \| 0.1401 \| 0.1428 \| | 0.1401 | ratio | brier | train | eq | `[[art:707e58aa:metrics.train.brier]]` | verified | 0.1401 |
| 50 | outcomes | \| Brier \| 0.1401 \| 0.1428 \| | 0.1428 | ratio | brier | test | eq | `[[art:2c220200:metrics.test.brier]]` | verified | 0.1428 |
| 51 | outcomes | \| log loss \| 0.4407 \| 0.4471 \| | 0.4407 | ratio | logloss | train | eq | `[[art:595f5afb:metrics.train.logloss]]` | verified | 0.4407 |
| 52 | outcomes | \| log loss \| 0.4407 \| 0.4471 \| | 0.4471 | ratio | logloss | test | eq | `[[art:e06c9ee8:metrics.test.logloss]]` | verified | 0.4471 |
| 53 | outcomes | \| n \| 3,500 \| 1,500 \| | 3500 | count | n | train | eq | `[[art:f696a6ea:metrics.train.n]]` | verified | 3500 |
| 54 | outcomes | \| n \| 3,500 \| 1,500 \| | 1500 | count | n | test | eq | `[[art:2dd7648b:metrics.test.n]]` | verified | 1500 |
| 55 | outcomes | The train-to-test AUC gap is 0.0126, against a generalisati… | 0.0126 | ratio | auc |  | delta | `[[art:4bb1344e:metrics.test.auc]][[art:dd1bb63e:metrics.train.auc]]` | verified | 0.0126 |
| 56 | outcomes | The train-to-test AUC gap is 0.0126, against a generalisati… | 0.08 | ratio | auc_gap |  | eq | `[[art:a13c0174:threshold.O1.auc_gap]]` | verified | 0.08 |
| 57 | outcomes | Calibration is close to the identity: the slope of a logist… | 0.9712 | ratio | calibration_slope | test | eq | `[[art:ab09adf2:calibration_slope.test]]` | verified | 0.9712 |
| 58 | outcomes | Calibration is close to the identity: the slope of a logist… | -0.021 | ratio | calibration_intercept | test | eq | `[[art:e53b6ceb:calibration_intercept.test]]` | verified | -0.021 |
| 59 | outcomes | Calibration is close to the identity: the slope of a logist… | 0.2213 | ratio | mean_predicted | test | eq | `[[art:5e0d91b1:metrics.test.mean_predicted]]` | verified | 0.2213 |
| 60 | outcomes | Calibration is close to the identity: the slope of a logist… | 0.22 | ratio | event_rate | test | eq | `[[art:54418164:metrics.test.event_rate]]` | verified | 0.22 |
| 61 | outcomes | Calibration is close to the identity: the slope of a logist… | 0.6 | percent | mean_rel_gap | test | eq | `[[art:ba1b605e:calibration.mean_rel_gap.test]]` | verified | 0.0059 |
| 62 | outcomes | Calibration is close to the identity: the slope of a logist… | 25 | percent | mean_ratio_rel |  | eq | `[[art:92720b9b:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 63 | outcomes | The top decile has a default rate of 0.493, a lift of 2.24 … | 0.493 | ratio | event_rate | test | eq | `[[art:20368492:deciles.test#1.event_rate]]` | verified | 0.493 |
| 64 | outcomes | The top decile has a default rate of 0.493, a lift of 2.24 … | 2.24 | ratio | lift | test | eq | `[[art:20368492:deciles.test#1.lift]]` | verified | 2.24 |
| 65 | outcomes | The top decile has a default rate of 0.493, a lift of 2.24 … | 38.2 | percent | capture | test | eq | `[[art:9d783477:deciles.test.top2_capture]]` | verified | 0.3818 |
| 66 | outcomes | \| AUC \| test \| ≥ 0.70 \| 0.7412 \| pass \| | 0.7 | ratio | auc | test | eq | `[[art:af7a11b2:threshold.package.auc.test.min]]` | verified | 0.7 |
| 67 | outcomes | \| AUC \| test \| ≥ 0.70 \| 0.7412 \| pass \| | 0.7412 | ratio | auc | test | eq | `[[art:4bb1344e:metrics.test.auc]]` | verified | 0.7412 |
| 68 | outcomes | \| Brier \| test \| ≤ 0.20 \| 0.1428 \| pass \| | 0.2 | ratio | brier | test | eq | `[[art:06b3d754:threshold.package.brier.test.max]]` | verified | 0.2 |
| 69 | outcomes | \| Brier \| test \| ≤ 0.20 \| 0.1428 \| pass \| | 0.1428 | ratio | brier | test | eq | `[[art:2c220200:metrics.test.brier]]` | verified | 0.1428 |
| 70 | outcomes | \| calibration slope \| test \| in [0.80, 1.20] \| 0.9712 \… | 0.8 | ratio | calibration_slope |  | eq | `[[art:f495f499:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 71 | outcomes | \| calibration slope \| test \| in [0.80, 1.20] \| 0.9712 \… | 1.2 | ratio | calibration_slope |  | eq | `[[art:c3cc3580:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 72 | outcomes | \| calibration slope \| test \| in [0.80, 1.20] \| 0.9712 \… | 0.9712 | ratio | calibration_slope | test | eq | `[[art:ab09adf2:calibration_slope.test]]` | verified | 0.9712 |
| 73 | outcomes | \| PSI \| all features \| ≤ 0.25 \| max 0.021 \| pass \| | 0.25 | ratio | psi |  | eq | `[[art:0c87f8b4:threshold.package.psi.max]]` | verified | 0.25 |
| 74 | outcomes | \| PSI \| all features \| ≤ 0.25 \| max 0.021 \| pass \| | 0.021 | ratio | psi |  | eq | `[[art:b9e6b86f:psi.max]]` | verified | 0.021 |
| 75 | outcomes | The developer's own `metrics.json` reports a test AUC of 0.… | 0.7412 | ratio | auc | test | eq | `[[art:557c701c:run.metrics#test.auc]]` | verified | 0.7412 |
| 76 | outcomes | The developer's own `metrics.json` reports a test AUC of 0.… | 0.1428 | ratio | brier | test | eq | `[[art:557c701c:run.metrics#test.brier]]` | verified | 0.1428 |
| 77 | outcomes | Follow-up requested by the planner: discrimination by credi… | 750 | count | n | test | eq | `[[art:73bf248c:metrics.test.sub.limit_bal_low.n]]` | verified | 750 |
| 78 | outcomes | Follow-up requested by the planner: discrimination by credi… | 0.7188 | ratio | auc | test | eq | `[[art:718aed91:metrics.test.sub.limit_bal_low.auc]]` | verified | 0.7188 |
| 79 | outcomes | Follow-up requested by the planner: discrimination by credi… | 0.759 | ratio | auc | test | eq | `[[art:60ef92d1:metrics.test.sub.limit_bal_high.auc]]` | verified | 0.759 |
| 80 | sensitivity | After the subject's own screen, multicollinearity among the… | 4.31 | ratio | vif |  | eq | `[[art:9a9e9f38:vif.utilisation]]` | verified | 4.31 |
| 81 | sensitivity | After the subject's own screen, multicollinearity among the… | 10 | ratio | vif |  | eq | `[[art:76a42f3d:threshold.M1.vif]]` | verified | 10 |
| 82 | sensitivity | After the subject's own screen, multicollinearity among the… | 18.6 | ratio | condition_number |  | eq | `[[art:10f3ad32:condition_number]]` | verified | 18.6 |
| 83 | sensitivity | After the subject's own screen, multicollinearity among the… | 30 | ratio | condition_number |  | eq | `[[art:8abf1a99:threshold.M1.condition_number]]` | verified | 30 |
| 84 | findings | **A gradient-boosting challenger outperforms the champion b… | 0.0323 | ratio | delta_auc | test | eq | `[[art:02d4d1a8:challenger.delta_auc]]` | verified | 0.0323 |
| 85 | findings | **A gradient-boosting challenger outperforms the champion b… | 0.7735 | ratio | auc | test | eq | `[[art:d995c29d:challenger.auc]]` | verified | 0.7735 |
| 86 | findings | **A gradient-boosting challenger outperforms the champion b… | 0.7412 | ratio | auc | test | eq | `[[art:4bb1344e:metrics.test.auc]]` | verified | 0.7412 |
| 87 | findings | **A gradient-boosting challenger outperforms the champion b… | 0.03 | ratio | delta_auc |  | eq | `[[art:de8d94b3:threshold.E1.delta_auc]]` | verified | 0.03 |
| 88 | monitoring | Recommended: (a) monthly PSI on every retained feature and … | 0.25 | ratio | psi |  | eq | `[[art:0c87f8b4:threshold.package.psi.max]]` | verified | 0.25 |
| 89 | monitoring | Recommended: (a) monthly PSI on every retained feature and … | 0.8 | ratio | calibration_slope |  | eq | `[[art:f495f499:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 90 | monitoring | Recommended: (a) monthly PSI on every retained feature and … | 1.2 | ratio | calibration_slope |  | eq | `[[art:c3cc3580:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 91 | monitoring | Recommended: (a) monthly PSI on every retained feature and … | 0.7 | ratio | auc |  | eq | `[[art:af7a11b2:threshold.package.auc.test.min]]` | verified | 0.7 |
| 92 | monitoring | Recommended: (a) monthly PSI on every retained feature and … | 0.7188 | ratio | auc | test | eq | `[[art:718aed91:metrics.test.sub.limit_bal_low.auc]]` | verified | 0.7188 |

## Appendix B — Artifact index

| logical name | hash | kind | value |
|---|---|---|---|
| `calibration.mean_rel_gap.test` | `ba1b605e` | scalar | 0.0059 |
| `calibration.test` | `1c01dc55` | table | table, 10 rows |
| `calibration_intercept.test` | `e53b6ceb` | scalar | -0.021 |
| `calibration_slope.test` | `ab09adf2` | scalar | 0.9712 |
| `challenger.auc` | `d995c29d` | scalar | 0.7735 |
| `challenger.brier` | `6bfc68f5` | scalar | 0.1392 |
| `challenger.delta_auc` | `02d4d1a8` | scalar | 0.0323 |
| `condition_number` | `10f3ad32` | scalar | 18.6 |
| `csi.max` | `7daee19d` | scalar | 0.018 |
| `deciles.test` | `20368492` | table | table, 10 rows |
| `deciles.test.top2_capture` | `9d783477` | scalar | 0.3818 |
| `guidance.outcomes_analysis` | `f60ae585` | json | json |
| `leakage.name_screen.n_matched` | `535e256a` | scalar | 0 |
| `leakage.overlap` | `b2c21e16` | scalar | 0.0 |
| `leakage.target_corr.max_single_feature_auc` | `949c3049` | scalar | 0.6812 |
| `leakage.timing.n_flagged` | `ceda5706` | scalar | 0 |
| `metrics.test.auc` | `4bb1344e` | scalar | 0.7412 |
| `metrics.test.brier` | `2c220200` | scalar | 0.1428 |
| `metrics.test.event_rate` | `54418164` | scalar | 0.22 |
| `metrics.test.gini` | `0c3e4bc9` | scalar | 0.4824 |
| `metrics.test.ks` | `5fdb3051` | scalar | 0.3617 |
| `metrics.test.logloss` | `e06c9ee8` | scalar | 0.4471 |
| `metrics.test.mean_predicted` | `5e0d91b1` | scalar | 0.2213 |
| `metrics.test.n` | `2dd7648b` | scalar | 1500 |
| `metrics.test.sub.limit_bal_high.auc` | `60ef92d1` | scalar | 0.759 |
| `metrics.test.sub.limit_bal_low.auc` | `718aed91` | scalar | 0.7188 |
| `metrics.test.sub.limit_bal_low.n` | `73bf248c` | scalar | 750 |
| `metrics.train.auc` | `dd1bb63e` | scalar | 0.7538 |
| `metrics.train.brier` | `707e58aa` | scalar | 0.1401 |
| `metrics.train.event_rate` | `d51a015c` | scalar | 0.22 |
| `metrics.train.gini` | `970da634` | scalar | 0.5076 |
| `metrics.train.ks` | `db884f7a` | scalar | 0.3702 |
| `metrics.train.logloss` | `595f5afb` | scalar | 0.4407 |
| `metrics.train.n` | `f696a6ea` | scalar | 3500 |
| `profile.test.missing.max` | `fc3dde37` | scalar | 0.0 |
| `profile.test.n` | `96315a22` | scalar | 1500 |
| `profile.train.missing.max` | `36356ec7` | scalar | 0.0 |
| `profile.train.n` | `42612024` | scalar | 3500 |
| `psi.max` | `b9e6b86f` | scalar | 0.021 |
| `psi.utilisation` | `0cd1eb2f` | scalar | 0.021 |
| `psi.y_score` | `d5ad1386` | scalar | 0.014 |
| `rule.calibration_first_event_rate` | `5acffd33` | scalar | 0.05 |
| `run.duration_s` | `9b3b4fba` | scalar | 23.4 |
| `run.features` | `8b373477` | json | json |
| `run.metrics` | `557c701c` | json | json |
| `run.model_summary` | `843f4548` | json | json |
| `run.splits` | `cc603ae0` | json | json |
| `threshold.C1.mean_ratio_rel` | `92720b9b` | scalar | 0.25 |
| `threshold.D1.missing_gap` | `527fd926` | scalar | 0.1 |
| `threshold.E1.delta_auc` | `de8d94b3` | scalar | 0.03 |
| `threshold.L1.single_feature_auc` | `8e765a47` | scalar | 0.9 |
| `threshold.L2.overlap` | `6ff7c573` | scalar | 0.005 |
| `threshold.M1.condition_number` | `8abf1a99` | scalar | 30 |
| `threshold.M1.vif` | `76a42f3d` | scalar | 10 |
| `threshold.O1.auc_gap` | `a13c0174` | scalar | 0.08 |
| `threshold.package.auc.test.min` | `af7a11b2` | scalar | 0.7 |
| `threshold.package.brier.test.max` | `06b3d754` | scalar | 0.2 |
| `threshold.package.calibration_slope.test.max` | `c3cc3580` | scalar | 1.2 |
| `threshold.package.calibration_slope.test.min` | `f495f499` | scalar | 0.8 |
| `threshold.package.psi.max` | `0c87f8b4` | scalar | 0.25 |
| `vif.max` | `123cfaee` | scalar | 4.31 |
| `vif.utilisation` | `9a9e9f38` | scalar | 4.31 |

## Appendix C — Run trace summary

| quantity | value |
|---|---|
| tool calls | 14 (run_model 1, profile_data 1, compute_metrics 2, check_leakage 1, check_collinearity 1, challenger_compare 1, retrieve_guidance 7) |
| plan steps (bounded loop) | 2 (one follow-up: compute_metrics on limit_bal halves; then stop) |
| LLM calls | 18 (7 section drafts, 7 extractions, 1 repair draft, 1 re-extraction, 2 plan steps) |
| re-asks | 0 |
| repair rounds | 1 |
| tokens in / out | 61,240 / 9,870 |
| notional cost (USD) | 0.41 |
| wall-clock (s) | 214 |
| subject run (s) | 23.4 |
| memory cap | enforced (RLIMIT_AS 4096 MB) |
| model | illustrative |

## Appendix D — Not checked

| item | reason |
|---|---|
| `check_stability` (R1) | package declares no `regime.column` |
| `run_scenarios` (X1) | not applicable to `binary_classification` |
| out-of-time and vintage-holdout metrics (O1, second rule) | package declares neither split |
| developer claims (T1, claim channel) | `package.yaml` declares none; synthetic mode does not evaluate developer claims |
| developer documentation | package has no `docs/` directory |
| data manifest | `data.manifest` is null in synthetic mode |
