---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: full_agent
model: claude-opus-5[1m]
run_id: credit_default-full_agent-20260908T212049Z-d03b07c6
data_mode: real
grounding_precision_pre: 0.9827
grounding_precision_post: 1.0000
n_claims: 285
n_findings_by_severity: {high: 0, medium: 0, low: 0, info: 0}
generated: "2026-09-08T21:20:49Z"
illustrative: false
---

# Validation report — `credit_default` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `credit_default` v1.0 | `full_agent` | claude-opus-5[1m] | real, UCI Default of Credit Card Clients (dataset id 350; CC BY 4.0; Yeh, I. (2009), doi 10.24432/C55S3H), 30,000 clients, sampled by sample.py. Synthetic mode: synthetic.py. | 0.9827 → 1.0000 | 0 / 0 / 0 / 0 |
<!-- quaestor:renderer:end -->

This report reviews the credit_default model package, a binary classifier that scores borrower accounts for the probability of default, and follows the structure of the Federal Reserve's model risk management guidance on model validation and monitoring [[reg:SR26-2:V]].
The evidence below is outcomes analysis in the sense of that guidance: recomputed model outputs compared against the realised default outcomes on the developer's own splits [[reg:SR26-2:V.1.b]].
The subject was re-executed from the packaged artefacts under the wall-clock cap of 300 [[art:2ad8d1a5:runtime.max_seconds]] seconds that package.yaml declares, and every metric reported here was recomputed by quaestor from the model's own predictions rather than read from the developer's write-up.
The training split holds 21000 [[art:a359de9d:profile.train.n]] rows and the test split holds 9000 [[art:abbe1a27:profile.test.n]] rows.
The recomputation scored the same populations, 21000 [[art:1721ceae:metrics.train.n]] rows on train and 9000 [[art:5367a59f:metrics.test.n]] rows on test.
The outcome is close to evenly distributed between the splits, with an event rate of 0.2212 [[art:657aa7fc:metrics.train.event_rate]] on train and 0.2212 [[art:f60ae2a7:metrics.test.event_rate]] on test.
The model passes the developer-declared discrimination floor: test AUC is 0.755 [[art:365b7034:metrics.test.auc]] against the declared minimum of 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]].
It passes the declared accuracy ceiling: the test Brier score is 0.1385 [[art:86e93c8f:metrics.test.brier]] against the declared maximum of 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]].
It passes the declared calibration band: the test calibration slope is 0.9886 [[art:e06564c7:calibration_slope.test]], inside the declared minimum of 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] and the declared maximum of 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
It passes the declared stability ceiling: the largest train-to-test population stability index, score included, is 0.003083 [[art:e1d82330:psi.max]] against the declared maximum of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
Discrimination is consistent across the two splits, with train AUC at 0.7546 [[art:01cf8178:metrics.train.auc]] and test AUC at 0.755 [[art:365b7034:metrics.test.auc]], and the calibration slope moves from 1.001 [[art:85461245:calibration_slope.train]] on train to 0.9886 [[art:e06564c7:calibration_slope.test]] on test.
No findings were raised in this section, at any severity.

## 2. Conceptual soundness

Validating conceptual soundness involves assessing model design, key modeling choices, and developmental evidence, and it admits interpretability measures and benchmarking to other models as practical forms of that assessment [[reg:SR26-2:V.1.a]].
This section assesses the champion's design, its feature set and their timing, the collinearity screen it applied to itself, the fitted coefficients against subject-matter expectation, and the effective challenge.

### Design and feature timing

The champion is a linear-in-logit scoring model: a single intercept of -1.442 [[art:ca1c764c:run.model_summary#intercept]] plus one coefficient per retained feature, fitted on 21000 [[art:ca1c764c:run.model_summary#n_train]] training rows.
The functional form is additive and monotone in each input, so each coefficient is directly readable as the direction and relative weight the model assigns to its feature.
The package carries 12 [[art:792cb79c:run.features#n]] features in total.
Of these, 2 [[art:792cb79c:run.features#at_origination]] are known at origination and 10 [[art:792cb79c:run.features#before_period_start]] are known before the performance period starts.
None are dated during the period, at 0 [[art:792cb79c:run.features#during_period]], and none are dated after the outcome, at 0 [[art:792cb79c:run.features#after_outcome]].
On the timing declared in the package, every input is therefore observable at the moment the score would be used, which is the design property that a scoring model of this kind needs.

### The developer's own screen

The developer applied a variance-inflation screen at a threshold of 10 [[art:ca1c764c:run.model_summary#vif_threshold]] and dropped the features that exceeded it.
bill_last was removed at a VIF of 33.8 [[art:ca1c764c:run.model_summary#removed.bill_last.vif]], far above the threshold, and it is the kind of near-duplicate of the six-month bill aggregates that a collinearity screen exists to catch.
utilisation_mean_6m was removed at a VIF of 10.96 [[art:ca1c764c:run.model_summary#removed.utilisation_mean_6m.vif]], only just above the threshold, so its removal is a marginal call rather than a clear one; a screen that turns on a bright line will sometimes drop a feature that a slightly different line would have kept.
Both removals are consistent with the rule the developer stated, and the rule itself is a defensible one for a linear model whose coefficients are meant to be interpreted.

### Coefficients against subject-matter expectation

The largest coefficient by magnitude is delinq_last at 0.4847 [[art:ca1c764c:run.model_summary#coefficients.delinq_last.value]], followed by delinq_count_6m at 0.2801 [[art:ca1c764c:run.model_summary#coefficients.delinq_count_6m.value]], delinq_max_6m at 0.2263 [[art:ca1c764c:run.model_summary#coefficients.delinq_max_6m.value]], and limit_bal at -0.2091 [[art:ca1c764c:run.model_summary#coefficients.limit_bal.value]].
The three delinquency terms carrying the largest positive weights is what a credit analyst would expect: recent and repeated delinquency is the strongest available signal of imminent default, and the model leans on it hardest.
The negative weight on limit_bal is likewise expected, since a granted credit limit encodes the lender's own prior assessment of the borrower and higher limits go to better risks.
The remaining weights are materially smaller: pay_ratio_mean_6m at -0.09824 [[art:ca1c764c:run.model_summary#coefficients.pay_ratio_mean_6m.value]], utilisation at -0.08257 [[art:ca1c764c:run.model_summary#coefficients.utilisation.value]], age at 0.07253 [[art:ca1c764c:run.model_summary#coefficients.age.value]], bill_trend_6m at 0.04808 [[art:ca1c764c:run.model_summary#coefficients.bill_trend_6m.value]], bill_mean_6m at -0.007568 [[art:ca1c764c:run.model_summary#coefficients.bill_mean_6m.value]], and pay_ratio_last at 0.00678 [[art:ca1c764c:run.model_summary#coefficients.pay_ratio_last.value]].
The negative sign on pay_ratio_mean_6m reads as expected, since a borrower who has been paying down a larger share of the bill over six months is the safer one.
The positive sign on utilisation is contrary to the usual credit expectation that a borrower closer to their limit is the riskier one, and the coefficient's negative value places the fitted model against that expectation for this feature.
The positive coefficient on age also runs against the common expectation that default risk falls with borrower age, and it deserves a note in the model's documentation of assumptions even though its weight is small.

### Fitted signs against univariate direction

The evidence in this subsection is diagnostic of design quality rather than the subject of any rule, and nothing in it is described here as a finding.
Across the retained features, the count of fitted coefficients whose sign contradicts the feature's own univariate direction on train is 3 [[art:e223cd4a:sign_check.n_disagreements]].
The ablation deltas below are measured from a refit of the champion's form on every retained feature, whose test AUC is 0.755 [[art:789072f8:ablation.baseline_auc]].

utilisation is one of the disagreements: its fitted coefficient sign is -1 [[art:46230409:sign_check.utilisation.coef_sign]] while its univariate direction is 1 [[art:f0995196:sign_check.utilisation.univariate_direction]], so agreement is 0 [[art:cb5a7bc7:sign_check.utilisation.agrees]].
Refitting the champion's form without utilisation changes test AUC by 1.92e-05 [[art:dc9ac505:ablation.utilisation.delta_auc]], a positive number, meaning the model discriminates no worse without it.
That is the mildest reading available for a sign flip: the feature enters with a sign opposite to its own relationship with the outcome and contributes no discrimination, so the flip is a sign that utilisation is absorbing correlation with other terms rather than that the model depends on an inverted relationship.

pay_ratio_last is the second disagreement: its fitted coefficient sign is 1 [[art:f018263e:sign_check.pay_ratio_last.coef_sign]] against a univariate direction of -1 [[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]], with agreement 0 [[art:79abee77:sign_check.pay_ratio_last.agrees]].
Its ablation delta is -5.589e-05 [[art:e26d8112:ablation.pay_ratio_last.delta_auc]], a loss too small to represent discrimination the model relies on.
Combined with a coefficient of 0.00678 [[art:ca1c764c:run.model_summary#coefficients.pay_ratio_last.value]], this is a sign flip on a feature the model barely uses.

bill_trend_6m is the third and the one that matters most: its fitted sign is 1 [[art:abd4aaba:sign_check.bill_trend_6m.coef_sign]] against a univariate direction of -1 [[art:a9bff389:sign_check.bill_trend_6m.univariate_direction]], with agreement 0 [[art:c0f6d07d:sign_check.bill_trend_6m.agrees]].
Removing it costs -0.001393 [[art:99f9dd71:ablation.bill_trend_6m.delta_auc]] of test AUC, an order of magnitude more than the other two flips and enough that the model is drawing real discrimination through a term whose fitted direction contradicts its own bivariate relationship with default.
A feature carrying discrimination in the direction opposite to its standalone relationship is the classic signature of a suppressor variable in a linear specification, and the developer's documentation should state what interaction with the bill and delinquency terms is doing the work.

The other retained features agree with their univariate directions: delinq_last at 1 [[art:a8ba9372:sign_check.delinq_last.agrees]], delinq_count_6m at 1 [[art:a337d16b:sign_check.delinq_count_6m.agrees]], delinq_max_6m at 1 [[art:da92a015:sign_check.delinq_max_6m.agrees]], limit_bal at 1 [[art:103d99fb:sign_check.limit_bal.agrees]], pay_ratio_mean_6m at 1 [[art:7e9a76ca:sign_check.pay_ratio_mean_6m.agrees]], bill_mean_6m at 1 [[art:89279c3b:sign_check.bill_mean_6m.agrees]], and age at 1 [[art:4116add1:sign_check.age.agrees]].
The fitted signs on the features the model leans on hardest are the coherent ones: delinq_last is 1 [[art:50d352f8:sign_check.delinq_last.coef_sign]] against a univariate direction of 1 [[art:a78648ba:sign_check.delinq_last.univariate_direction]], and limit_bal is -1 [[art:a6d01381:sign_check.limit_bal.coef_sign]] against a univariate direction of -1 [[art:56d284d6:sign_check.limit_bal.univariate_direction]].

### What the model actually leans on

The ablation deltas rank the features by the discrimination they carry within the champion's own form.
delinq_last is the largest single contributor at -0.005914 [[art:40f4e6bf:ablation.delinq_last.delta_auc]], followed by limit_bal at -0.003748 [[art:57710b23:ablation.limit_bal.delta_auc]], age at -0.002225 [[art:f6fdd709:ablation.age.delta_auc]], and delinq_count_6m at -0.002146 [[art:db90576e:ablation.delinq_count_6m.delta_auc]].
Below those, delinq_max_6m contributes -0.001133 [[art:18cb1559:ablation.delinq_max_6m.delta_auc]], pay_ratio_mean_6m -0.0009816 [[art:cba98844:ablation.pay_ratio_mean_6m.delta_auc]], and bill_mean_6m -0.0001527 [[art:5b4423ab:ablation.bill_mean_6m.delta_auc]].
No single feature's removal costs more than a small fraction of the baseline, so the model's discrimination is spread across the delinquency and limit terms rather than resting on any one of them, which is a stability property in the model's favour.

### Effective challenge

The champion's recomputed test AUC is 0.755 [[art:365b7034:metrics.test.auc]] with a Brier score of 0.1385 [[art:86e93c8f:metrics.test.brier]].
The challenger reaches a test AUC of 0.7789 [[art:5646e7f3:challenger.auc]] and a Brier score of 0.135 [[art:2031a154:challenger.brier]], so it is both the better ranker and the better-calibrated of the two on test.
The challenger's AUC lead over the champion is 0.02391 [[art:3877bdd0:challenger.delta_auc]].
The threshold that decides whether such a lead matters is a challenger AUC lead of 0.03 [[art:e042774c:threshold.E1.delta_auc]].
The observed lead sits below that threshold, so on this criterion the challenger does not displace the champion, and the effective challenge supports retaining the current specification.
The margin is not comfortable, however: the challenger recovers most of the lead the threshold would require, and the direction of that gap is the direction a more flexible functional form would be expected to move if the champion's additive linear form were leaving structure on the table.
That reading is consistent with the bill_trend_6m sign behaviour described above, and it is the aspect of the design most worth revisiting at the next model review.

### Assessment

The design is coherent for its stated purpose: the timing of every input is compatible with the point of use, the collinearity screen was applied against a stated threshold and its removals are explicable, and the largest weights fall on the features credit judgement would put them on with the signs credit judgement would expect.
The qualifications are the fitted signs that contradict their own univariate directions, of which the one on bill_trend_6m carries enough discrimination to warrant a documented explanation, and the narrowness of the margin by which the champion survives the effective challenge.
No item raised for this section is designated a finding; the findings section reports the run's findings.

## 3. Data integrity and drift

SR26-2 places a critical assessment of data quality, relevance, and inputs among the core testing activities of model development, and the screens below carry that assessment for the credit_default 1.0 package [[reg:SR26-2:IV.1]].
Data selection is likewise part of what the conceptual-soundness review documents and subjects to critical analysis [[reg:SR26-2:V.1.a]].

### Missingness

The training split holds 21000 [[art:a359de9d:profile.train.n]] rows and the test split holds 9000 [[art:abbe1a27:profile.test.n]] rows.
The largest missing fraction in train is 0 [[art:050a3099:profile.train.missing.max]], and the largest missing fraction in test is 0 [[art:f813848d:profile.test.missing.max]].
The two maxima are equal, so no gap separates the splits, and the D1 bound on the missingness gap of 0.1 [[art:9cce25ea:threshold.D1.missing_gap]] is not approached from either side.
No column in either split is therefore carrying an imputation burden that differs across the split boundary.

### Population and characteristic stability

The largest train-to-test population stability index, score included, is 0.003083 [[art:e1d82330:psi.max]], against the S1 bound of 0.25 [[art:278b9016:threshold.S1.psi]], which is the same value the package declares at 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
That maximum is attributable to age, whose PSI between train and test is 0.003083 [[art:06c22a63:psi.age]].
Among the remaining inputs, pay_ratio_last reaches 0.002264 [[art:82c97112:psi.pay_ratio_last]], delinq_count_6m 0.001856 [[art:d77ddb1d:psi.delinq_count_6m]], bill_mean_6m 0.001488 [[art:127cdf82:psi.bill_mean_6m]], and limit_bal 0.001272 [[art:b0195847:psi.limit_bal]].
The rest sit lower still: pay_ratio_mean_6m at 0.001028 [[art:62e0e0f8:psi.pay_ratio_mean_6m]], delinq_max_6m at 0.001027 [[art:4b0a94ab:psi.delinq_max_6m]], bill_trend_6m at 0.0007484 [[art:78be70d2:psi.bill_trend_6m]], utilisation at 0.0006523 [[art:f094559b:psi.utilisation]], and delinq_last at 0.0002347 [[art:cbc9de36:psi.delinq_last]].
The score itself shifts by a PSI of 0.001368 [[art:ec2b8d1b:psi.y_score]], so the output distribution moves no more than its inputs do.
Every one of these values is two orders of magnitude inside the declared bound of 0.25 [[art:278b9016:threshold.S1.psi]].

The largest characteristic stability index is 0.004737 [[art:ce1257d8:csi.max]], carried by delinq_max_6m at 0.004737 [[art:35990a39:csi.delinq_max_6m]].
The next largest contributions to the shift in the linear predictor come from pay_ratio_mean_6m at 0.002043 [[art:5e53c153:csi.pay_ratio_mean_6m]], delinq_last at 0.001698 [[art:e755cf0a:csi.delinq_last]], limit_bal at 0.001384 [[art:c91a2a4b:csi.limit_bal]], and age at 0.001203 [[art:25b88f37:csi.age]].
The remainder are smaller again: delinq_count_6m at 0.0008781 [[art:f0438233:csi.delinq_count_6m]], bill_trend_6m at 0.0003675 [[art:9e5a9b68:csi.bill_trend_6m]], utilisation at 0.0002136 [[art:6ed37e42:csi.utilisation]], pay_ratio_last at 0.0001132 [[art:5898a9c5:csi.pay_ratio_last]], and bill_mean_6m at 9.982e-06 [[art:0c34001d:csi.bill_mean_6m]].
Read against the same declared stability bound of 0.25 [[art:278b9016:threshold.S1.psi]], no single characteristic contributes a material share of the movement in the linear predictor, and the ordering of contributions is consistent with the per-feature PSI above.

### Leakage screens

The timing screen reads the declared timing of each feature and flags 0 [[art:742bcd24:leakage.timing.n_flagged]] features as during_period or after_outcome, so nothing in the design is declared to be observed at or after the outcome it predicts.
The strongest single feature reaches an AUC of 0.728 [[art:2e212f3a:leakage.target_corr.max_single_feature_auc]] on its own, below the L1 bound of 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]], which is the level at which a lone predictor would be treated as a proxy for the target rather than a driver of it.

The contamination screen has two arms, and each is read against its own bound.
The identifier arm finds that 0 [[art:63d37fc5:leakage.overlap.ids]] of test rows carry a client_id that also identifies a row of train, against the declared L2 bound of 0.005 [[art:9f336eaf:threshold.L2.overlap]], so the split is clean on subject identity.
The feature-vector arm finds that 0.01256 [[art:517f3049:leakage.overlap.features]] of test rows have feature values that also appear in train, and the bound the rule actually applied is the effective bound of 0.02324 [[art:7cdc63cb:threshold.L2.overlap.features_effective]], so this arm also sits inside its bound.
That effective bound is the larger of the declared 0.005 [[art:9f336eaf:threshold.L2.overlap]] and twice the train duplicate share of 0.01162 [[art:c988bb0e:leakage.duplicates.train]], the share of train rows whose feature values are not unique within train.
The widening is deliberate: where the feature space is discrete, two different subjects can write the same row by coincidence, and the base rate of such coincidence inside train is the right yardstick for how much of it to expect across the split.
The headline overlap figure of 0.01256 [[art:ebd7ff30:leakage.overlap]] is the same feature-value quantity and is read against the same effective bound of 0.02324 [[art:7cdc63cb:threshold.L2.overlap.features_effective]] rather than against the declared threshold, since comparing a feature-vector overlap with the identifier bound would mistake duplication for contamination.
Because the identifier arm is at 0 [[art:63d37fc5:leakage.overlap.ids]] while the feature arm is non-zero, the observed coincidence is between distinct subjects, which is the reading the widened bound anticipates.

The name screen matches feature names against a target-adjacent lexicon and returns 0 [[art:407e62be:leakage.name_screen.n_matched]] matches, so no input is named in a way that suggests it encodes the outcome.

### Assessment

Every quantity above sits inside the bound it was read against, with missingness identical across splits, stability well inside the declared 0.25 [[art:278b9016:threshold.S1.psi]], and both contamination arms inside their respective bounds.
The one screen worth carrying forward as a documented assumption is the widened feature-overlap bound, since its value depends on the train duplicate share of 0.01162 [[art:c988bb0e:leakage.duplicates.train]] and would tighten toward the declared 0.005 [[art:9f336eaf:threshold.L2.overlap]] if the feature space became more nearly continuous in a later version.
On the evidence in this section, the data feeding the package supports the developmental testing described in the guidance, and the residual risk on this dimension is the ordinary one that split-time stability need not persist in use [[reg:SR26-2:V.1.b]].

## 4. Outcomes analysis

Outcomes analysis here compares the model's recomputed outputs with the realised default outcomes on the training and evaluation splits, and reviews those results against the performance thresholds the developer declared for the package [[reg:SR26-2:V.1.b]].
This section reports discrimination first and calibration second.
The reason is the observed event rate on the evaluation split, 0.2212 [[art:f60ae2a7:metrics.test.event_rate]], which stands at or above rule.calibration_first_event_rate at 0.05 [[art:42f1351e:rule.calibration_first_event_rate]], the rate below which this report would lead with calibration instead.
Rank-ordering and absolute forecast accuracy are distinct tests with distinct weaknesses, so both are reported and neither is read as a substitute for the other [[reg:SR11-7:V.1.c]].

### Metrics by split

Every figure below was recomputed by the tool from the subject's own predictions.

| Metric | Train | Test |
| --- | --- | --- |
| n | 21000 [[art:1721ceae:metrics.train.n]] | 9000 [[art:5367a59f:metrics.test.n]] |
| event_rate | 0.2212 [[art:657aa7fc:metrics.train.event_rate]] | 0.2212 [[art:f60ae2a7:metrics.test.event_rate]] |
| auc | 0.7546 [[art:01cf8178:metrics.train.auc]] | 0.755 [[art:365b7034:metrics.test.auc]] |
| gini | 0.5091 [[art:eaaf0f79:metrics.train.gini]] | 0.51 [[art:296bfeeb:metrics.test.gini]] |
| ks | 0.4144 [[art:18df22bd:metrics.train.ks]] | 0.4067 [[art:d3c4ed61:metrics.test.ks]] |
| brier | 0.1384 [[art:c95106e9:metrics.train.brier]] | 0.1385 [[art:86e93c8f:metrics.test.brier]] |
| logloss | 0.4439 [[art:b816b083:metrics.train.logloss]] | 0.4442 [[art:2de58c1b:metrics.test.logloss]] |
| mean_predicted | 0.2212 [[art:935d2cb7:metrics.train.mean_predicted]] | 0.2206 [[art:89d241ea:metrics.test.mean_predicted]] |

Separation across the ranked deciles of predicted probability on test is set out in the table that follows.

<!-- quaestor:renderer:begin table deciles.test -->
Decile separation on test; decile 1 holds the highest probabilities [[art:4396db6f:deciles.test]]:

| decile | count | events | event_rate | lift |
|---|---|---|---|---|
| 1 | 900 | 617 | 0.6856 | 3.099 |
| 2 | 900 | 369 | 0.41 | 1.853 |
| 3 | 900 | 226 | 0.2511 | 1.135 |
| 4 | 900 | 154 | 0.1711 | 0.7735 |
| 5 | 900 | 159 | 0.1767 | 0.7986 |
| 6 | 900 | 119 | 0.1322 | 0.5977 |
| 7 | 900 | 98 | 0.1089 | 0.4922 |
| 8 | 900 | 87 | 0.09667 | 0.437 |
| 9 | 900 | 90 | 0.1 | 0.452 |
| 10 | 900 | 72 | 0.08 | 0.3616 |
<!-- quaestor:renderer:end -->

The capture of test events in the highest-ranked deciles is 0.4952 [[art:e2c0ad9f:deciles.test.top2_capture]], against 0.5031 [[art:5131afa7:deciles.train.top2_capture]] on the training split, so the ordering the score imposes carries over to the held-out data.

### Train-to-test gap

The gap between the splits is bounded by threshold.O1.auc_gap at 0.08 [[art:630f28f4:threshold.O1.auc_gap]].
Train AUC of 0.7546 [[art:01cf8178:metrics.train.auc]] and test AUC of 0.755 [[art:365b7034:metrics.test.auc]] sit within that bound, with the held-out split marginally the higher of the pair, so this run shows no loss of discrimination out of sample.
The same pattern holds on the rank statistics, where train ks of 0.4144 [[art:18df22bd:metrics.train.ks]] and test ks of 0.4067 [[art:d3c4ed61:metrics.test.ks]] differ only slightly.

### Calibration

The calibration slope on test, from the logistic regression of the outcome on the logit of the predicted probability, is 0.9886 [[art:e06564c7:calibration_slope.test]], inside the band running from 0.8 [[art:749634ae:threshold.C1.calibration_slope.min]] to 1.2 [[art:b6672579:threshold.C1.calibration_slope.max]].
The corresponding intercept is -0.008632 [[art:2ee976d3:calibration_intercept.test]], close enough to the origin that the fitted line is near the identity over the score range.
On train the slope is 1.001 [[art:85461245:calibration_slope.train]] and the intercept is 0.0003779 [[art:2ce8cd09:calibration_intercept.train]], as expected on the data the model was fitted to.
Mean predicted probability on test is 0.2206 [[art:89d241ea:metrics.test.mean_predicted]] against an observed event rate of 0.2212 [[art:f60ae2a7:metrics.test.event_rate]].
The relative gap between the two is 0.002944 [[art:bae28fd6:calibration.mean_rel_gap.test]], inside the tolerance threshold.C1.mean_ratio_rel at 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]]; the same relative gap on train is 0.0001555 [[art:a03ea014:calibration.mean_rel_gap.train]].
Calibration decile by decile on test is set out below, which is where any local departure from the aggregate agreement would show.

<!-- quaestor:renderer:begin table calibration.test -->
Calibration by decile of predicted probability on test [[art:d19b8ac3:calibration.test]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.08333 | 0.08 | 900 |
| 2 | 0.1032 | 0.1 | 900 |
| 3 | 0.1144 | 0.09667 | 900 |
| 4 | 0.1242 | 0.1089 | 900 |
| 5 | 0.1324 | 0.1322 | 900 |
| 6 | 0.1416 | 0.1767 | 900 |
| 7 | 0.1654 | 0.1711 | 900 |
| 8 | 0.2513 | 0.2511 | 900 |
| 9 | 0.4104 | 0.41 | 900 |
| 10 | 0.6796 | 0.6856 | 900 |
<!-- quaestor:renderer:end -->

### Declared thresholds

<!-- quaestor:renderer:begin table thresholds.evaluation -->
Every threshold package.yaml declares, with its bound, the recomputed value and the outcome [[art:5c58fa84:thresholds.evaluation]]:

| metric | split | bound | value | result |
|---|---|---|---|---|
| auc | test | minimum 0.7 | 0.755 | pass |
| brier | test | maximum 0.2 | 0.1385 | pass |
| calibration_slope | test | minimum 0.8 | 0.9886 | pass |
| calibration_slope | test | maximum 1.2 | 0.9886 | pass |
| psi |  | maximum 0.25 | 0.003083 | pass |
<!-- quaestor:renderer:end -->

The table pairs each bound package.yaml declares with the split it applies to, the value recomputed for this run, and the outcome of that comparison.
It is the tool's own evaluation of those bounds, so it governs wherever the prose of this report and the declared thresholds could be read differently.

### Follow-up analyses

The planning loop ran the sub-population analyses below after the aggregate metrics cleared every declared bound, on the reasoning that a pooled result can mask weakness in a segment.
A sub-population's AUC may fall below its split's own AUC by up to threshold.O1.slice_auc_gap at 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] before the result becomes an open item, and it must hold at least threshold.O1.slice_min_share at 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] of the split to raise one.

**limit_bal below median.** Metrics were recomputed on the low-limit half of each split, asked because a pooled AUC could hide weaker discrimination and calibration among borrowers with the smallest credit lines.
On test the slice holds 0.487 [[art:e7847e2b:metrics.test.sub.limit_bal_low.share]] of the split with n of 4383 [[art:686cad5e:metrics.test.sub.limit_bal_low.n]], an event rate of 0.2877 [[art:9629805c:metrics.test.sub.limit_bal_low.event_rate]] against mean predicted of 0.2802 [[art:e3d342d5:metrics.test.sub.limit_bal_low.mean_predicted]], AUC of 0.7477 [[art:26da9c77:metrics.test.sub.limit_bal_low.auc]], gini of 0.4955 [[art:1d9599c6:metrics.test.sub.limit_bal_low.gini]], ks of 0.4047 [[art:39f5214d:metrics.test.sub.limit_bal_low.ks]], brier of 0.1675 [[art:68867046:metrics.test.sub.limit_bal_low.brier]] and logloss of 0.5165 [[art:194532b1:metrics.test.sub.limit_bal_low.logloss]].
On train the slice holds 0.4837 [[art:d4eb837c:metrics.train.sub.limit_bal_low.share]] of the split, with an event rate of 0.2846 [[art:815577c8:metrics.train.sub.limit_bal_low.event_rate]] against mean predicted of 0.282 [[art:03370fd4:metrics.train.sub.limit_bal_low.mean_predicted]], AUC of 0.7557 [[art:d3864be2:metrics.train.sub.limit_bal_low.auc]], gini of 0.5113 [[art:efffd200:metrics.train.sub.limit_bal_low.gini]], ks of 0.4305 [[art:a95d8865:metrics.train.sub.limit_bal_low.ks]], brier of 0.1623 [[art:58d900b3:metrics.train.sub.limit_bal_low.brier]] and logloss of 0.5042 [[art:c0e7dc4c:metrics.train.sub.limit_bal_low.logloss]].
The slice AUC falls below its split's by 0.007286 [[art:15e1edcb:metrics.test.sub.limit_bal_low.auc_gap]] on test and by -0.02732 [[art:41fca294:metrics.train.sub.utilisation_high.auc_gap]] is not the figure for this slice; on train the gap is -0.001109 [[art:021950a5:metrics.train.sub.limit_bal_low.auc_gap]], and both splits sit within the allowance, so this slice stands as supporting evidence for the aggregate result.

**delinq_last equal to zero.** Metrics were recomputed on the never-recently-delinquent majority, asked because the low-limit half raised nothing and a delinquency-driven score may lose its edge among clean payers.
On test the slice holds 0.775 [[art:2caf0a26:metrics.test.sub.delinq_last_eq_0.share]] of the split with n of 6975 [[art:cd0a7adb:metrics.test.sub.delinq_last_eq_0.n]], an event rate of 0.1405 [[art:46acca95:metrics.test.sub.delinq_last_eq_0.event_rate]] against mean predicted of 0.1371 [[art:3d1e089a:metrics.test.sub.delinq_last_eq_0.mean_predicted]], AUC of 0.6312 [[art:1b96a24d:metrics.test.sub.delinq_last_eq_0.auc]], gini of 0.2624 [[art:1183089b:metrics.test.sub.delinq_last_eq_0.gini]], ks of 0.2105 [[art:4d6488ce:metrics.test.sub.delinq_last_eq_0.ks]], brier of 0.1168 [[art:2bce5eb5:metrics.test.sub.delinq_last_eq_0.brier]] and logloss of 0.3918 [[art:26913d06:metrics.test.sub.delinq_last_eq_0.logloss]].
On train the slice holds 0.7718 [[art:39ead1e5:metrics.train.sub.delinq_last_eq_0.share]] of the split, with an event rate of 0.1374 [[art:b158c0fb:metrics.train.sub.delinq_last_eq_0.event_rate]] against mean predicted of 0.138 [[art:121d5b67:metrics.train.sub.delinq_last_eq_0.mean_predicted]], AUC of 0.6205 [[art:f1c7d62f:metrics.train.sub.delinq_last_eq_0.auc]], gini of 0.241 [[art:43a02d18:metrics.train.sub.delinq_last_eq_0.gini]], ks of 0.1768 [[art:792e2044:metrics.train.sub.delinq_last_eq_0.ks]], brier of 0.1146 [[art:8583b4e5:metrics.train.sub.delinq_last_eq_0.brier]] and logloss of 0.3864 [[art:cd7b90e8:metrics.train.sub.delinq_last_eq_0.logloss]].
The slice AUC falls below its split's by 0.1238 [[art:90bff412:metrics.test.sub.delinq_last_eq_0.auc_gap]] on test and by 0.1341 [[art:9bd52249:metrics.train.sub.delinq_last_eq_0.auc_gap]] on train, in both cases beyond the allowance and on a majority share of each split, so the result is materially worse than the headline and the run carries it forward as a question for the model developer alongside its report here.
Mean predicted and observed rates on this slice remain close on both splits, so the weakness shown is in ordering rather than in level.

**delinq_last equal to one.** Metrics were recomputed on the recently delinquent segment, asked because the low-limit and clean-payer slices left the high-risk end of the delinquency split untested and discrimination and calibration are most likely to break down there.
On test the slice holds 0.1218 [[art:ba192c04:metrics.test.sub.delinq_last_eq_1.share]] of the split with n of 1096 [[art:664c19bf:metrics.test.sub.delinq_last_eq_1.n]], an event rate of 0.3321 [[art:3d353862:metrics.test.sub.delinq_last_eq_1.event_rate]] against mean predicted of 0.3858 [[art:6411ed69:metrics.test.sub.delinq_last_eq_1.mean_predicted]], AUC of 0.6513 [[art:1d01d834:metrics.test.sub.delinq_last_eq_1.auc]], gini of 0.3027 [[art:aeb8f8a5:metrics.test.sub.delinq_last_eq_1.gini]], ks of 0.2587 [[art:343e93a8:metrics.test.sub.delinq_last_eq_1.ks]], brier of 0.2105 [[art:82c35e29:metrics.test.sub.delinq_last_eq_1.brier]] and logloss of 0.6103 [[art:089e61ce:metrics.test.sub.delinq_last_eq_1.logloss]].
On train the slice holds 0.1234 [[art:3b48f1bc:metrics.train.sub.delinq_last_eq_1.share]] with n of 2592 [[art:7dfec1a7:metrics.train.sub.delinq_last_eq_1.n]], an event rate of 0.3426 [[art:d1e0caab:metrics.train.sub.delinq_last_eq_1.event_rate]] against mean predicted of 0.3841 [[art:90c4acea:metrics.train.sub.delinq_last_eq_1.mean_predicted]], AUC of 0.6441 [[art:5a17ab4a:metrics.train.sub.delinq_last_eq_1.auc]], gini of 0.2883 [[art:539c7e22:metrics.train.sub.delinq_last_eq_1.gini]], ks of 0.2314 [[art:4c6c5159:metrics.train.sub.delinq_last_eq_1.ks]], brier of 0.214 [[art:b31f006a:metrics.train.sub.delinq_last_eq_1.brier]] and logloss of 0.6179 [[art:1f5cba97:metrics.train.sub.delinq_last_eq_1.logloss]].
The slice AUC falls below its split's by 0.1037 [[art:7e196964:metrics.test.sub.delinq_last_eq_1.auc_gap]] on test and by 0.1104 [[art:d6cf38ec:metrics.train.sub.delinq_last_eq_1.auc_gap]] on train, beyond the allowance on a share of each split large enough to matter, so this result too is carried forward as a question for the model developer.
Here the mean predicted probability sits above the observed rate on both splits, so predictions on the recently delinquent are conservative in level while ordering within the segment is weak.

**utilisation above median.** Metrics were recomputed on the high-utilisation half of each split, asked because it is the risk-relevant segment none of the earlier slices covers and one where performance often degrades.
On test the slice holds 0.5 [[art:9404484e:metrics.test.sub.utilisation_high.share]] of the split with n of 4500 [[art:ee72f76a:metrics.test.sub.utilisation_high.n]], an event rate of 0.2658 [[art:e4a00a59:metrics.test.sub.utilisation_high.event_rate]] against mean predicted of 0.2608 [[art:e68f1a3d:metrics.test.sub.utilisation_high.mean_predicted]], AUC of 0.7781 [[art:7a00057d:metrics.test.sub.utilisation_high.auc]], gini of 0.5562 [[art:0500c179:metrics.test.sub.utilisation_high.gini]], ks of 0.4739 [[art:096c8d60:metrics.test.sub.utilisation_high.ks]], brier of 0.1492 [[art:80c11b34:metrics.test.sub.utilisation_high.brier]] and logloss of 0.4717 [[art:24970875:metrics.test.sub.utilisation_high.logloss]].
On train the slice holds 0.5 [[art:0ff76e00:metrics.train.sub.utilisation_high.share]] with n of 10500 [[art:fe8f2ffa:metrics.train.sub.utilisation_high.n]], an event rate of 0.255 [[art:b4c36e0f:metrics.train.sub.utilisation_high.event_rate]] against mean predicted of 0.2577 [[art:ef3c0e39:metrics.train.sub.utilisation_high.mean_predicted]], AUC of 0.7819 [[art:fc9a70a0:metrics.train.sub.utilisation_high.auc]], gini of 0.5638 [[art:02cc4283:metrics.train.sub.utilisation_high.gini]], ks of 0.4801 [[art:7bdb48f3:metrics.train.sub.utilisation_high.ks]], brier of 0.1455 [[art:2e9ceb3c:metrics.train.sub.utilisation_high.brier]] and logloss of 0.4626 [[art:33a65c49:metrics.train.sub.utilisation_high.logloss]].
The slice AUC falls below its split's by -0.02309 [[art:7132f197:metrics.test.sub.utilisation_high.auc_gap]] on test and by -0.02732 [[art:41fca294:metrics.train.sub.utilisation_high.auc_gap]] on train, that is, above the split in each case and comfortably within the allowance, so this slice supports the aggregate result.

## 5. Sensitivity and scenario analysis

Assessment of conceptual soundness rests on critical analysis of key modelling choices and on the quality and extent of the developmental evidence, and the sensitivity work reported below forms part of that evidence for credit_default version 1.0 [[reg:SR26-2:V.1.a]].
The superseded guidance is more specific about the mechanics of this work, asking that sensitivity analysis check the impact of small changes in inputs and parameter values on model outputs and that testing extend to extreme values to establish the boundaries of model performance [[reg:SR11-7:V.1.a]].

### 5.1 Multicollinearity among the retained features

The largest variance inflation factor across the retained features is 3.544 [[art:d3785ba9:vif.max]], against the M1 threshold of 10 [[art:aeb4f33c:threshold.M1.vif]].
That maximum is attained by delinq_count_6m, whose variance inflation factor on train is 3.544 [[art:7273e0be:vif.delinq_count_6m]], followed by delinq_max_6m at 3.484 [[art:e7b701a1:vif.delinq_max_6m]] and pay_ratio_mean_6m at 3.027 [[art:2cda5cfc:vif.pay_ratio_mean_6m]].
The next group comprises utilisation at 2.829 [[art:6ce4c102:vif.utilisation]], pay_ratio_last at 2.714 [[art:b68613a6:vif.pay_ratio_last]], delinq_last at 2.321 [[art:59461811:vif.delinq_last]] and bill_mean_6m at 2.265 [[art:87cb4e54:vif.bill_mean_6m]].
The least inflated features are limit_bal at 2.097 [[art:0c6efb3f:vif.limit_bal]], bill_trend_6m at 1.330 [[art:6d3f01ce:vif.bill_trend_6m]] and age at 1.025 [[art:692cd6e9:vif.age]].
No retained feature reaches even half the M1 threshold, so the design does not exhibit the near-dependence that would make individual coefficient magnitudes and signs unstable under resampling.
The clustering of the three largest values around the delinquency and payment-ratio blocks is consistent with those features sharing a common repayment-behaviour signal, which is a design property of the feature set rather than a defect in it.

Belsley's condition number of the column-standardised design is 4.279 [[art:ba0d9cc4:condition_number]], against the M1 threshold of 30 [[art:7e52fd7a:threshold.M1.condition_number]].
Taken with the variance inflation factors, the conditioning of the design supports reading the fitted coefficients individually rather than only as a block.

### 5.2 Stability across declared regimes

Stability is assessed by partitioning on the regime column the package declares, and is reported for the regimes so declared.
Appendix D is the record of which analyses in this section fall outside the model type of the subject package, and the regime treatment for credit_default version 1.0 should be read against that record rather than inferred from this section alone.

### 5.3 Rate-shock scenarios

credit_default version 1.0 is a credit default model and not a hazard model, so the rate-shock scenario analysis does not apply to it.
That analysis comprises the value change at the extreme upward and downward shocks, whether the shock curve is monotone across the shock grid, and whether the curvature of that curve agrees with the direction of convexity the package declares.
All three are listed in Appendix D as not applicable to this model type, and none of them was run for this package; no statement in this section should be read as reporting a shock, a monotonicity check or a convexity comparison for this model.
The sensitivity evidence carried for this model type is therefore the multicollinearity and conditioning evidence above, together with the regime treatment recorded in Appendix D.

## 6. Findings and recommendations

Findings are ordered by severity, and each carries the artifact values, thresholds and guidance that establish it, in keeping with the expectation that sound validation identifies model limitations and errors and clarifies appropriate use and whether corrective actions may be warranted [[reg:SR26-2:V]].

This validation raised no finding.

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1, S1), `compute_metrics` (T1, C1, O1), `check_leakage` (L1, L2), `check_collinearity` (M1), `challenger_compare` (E1).

### Open items

Neither observation below is a defect under any rule applied in this validation, and each is a question the model developer should answer rather than a defect to remediate.

On the never-delinquent segment (delinq_last equal to zero), what does the score discriminate on inside a population that is also near-constant in delinquency history, given a slice AUC of 0.6312 [[art:1b96a24d:metrics.test.sub.delinq_last_eq_0.auc]] on test falling 0.1238 [[art:90bff412:metrics.test.sub.delinq_last_eq_0.auc_gap]] below the split's own headline AUC and 0.6205 [[art:f1c7d62f:metrics.train.sub.delinq_last_eq_0.auc]] on train falling 0.1341 [[art:9bd52249:metrics.train.sub.delinq_last_eq_0.auc_gap]] below its split's own headline AUC, both compared against a bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] on a segment holding 0.775 [[art:2caf0a26:metrics.test.sub.delinq_last_eq_0.share]] of test and 0.7718 [[art:39ead1e5:metrics.train.sub.delinq_last_eq_0.share]] of train against a minimum share of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]]; owner: model developer.

On the recently-delinquent segment (delinq_last equal to one), what does the score discriminate on inside a population selected on the delinquency count itself, given a slice AUC of 0.6513 [[art:1d01d834:metrics.test.sub.delinq_last_eq_1.auc]] on test falling 0.1037 [[art:7e196964:metrics.test.sub.delinq_last_eq_1.auc_gap]] below the split's own headline AUC and 0.6441 [[art:5a17ab4a:metrics.train.sub.delinq_last_eq_1.auc]] on train falling 0.1104 [[art:d6cf38ec:metrics.train.sub.delinq_last_eq_1.auc_gap]] below its split's own headline AUC, both compared against a bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] on a segment holding 0.1218 [[art:ba192c04:metrics.test.sub.delinq_last_eq_1.share]] of test and 0.1234 [[art:3b48f1bc:metrics.train.sub.delinq_last_eq_1.share]] of train against a minimum share of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]]; owner: model developer.

Documenting the developer's response to each open item supports the tracking of recommendations, responses and exceptions [[reg:SR26-2:VI.3]].

## 7. Ongoing monitoring recommendations

Ongoing monitoring for credit_default 1.0 should evaluate the extent to which the model continues to perform as expected given potential changes in products, exposures, activities, clients, data relevance, or market conditions, with a frequency and scope proportionate to the model's materiality [[reg:SR26-2:V.2]].

### Quantities, frequency, and bound

The recommendations below reuse the threshold artifacts the checks in this report cited, so that a monitoring exception means the same thing as a validation exception.

- Discrimination: recompute AUC on each outcome-complete monitoring cohort and compare it to the declared minimum of 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]], reading the validation value of 0.755 [[art:365b7034:metrics.test.auc]] as the reference point from which deterioration is measured.
- Accuracy: recompute the Brier score on the same cohorts against the declared maximum of 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]], with 0.1385 [[art:86e93c8f:metrics.test.brier]] as the reference point.
- Calibration: refit the logistic regression of the outcome on logit(p) and require the slope to stay inside the declared band from 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] to 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]], against a validation slope of 0.9886 [[art:e06564c7:calibration_slope.test]].
- Population stability: recompute the maximum PSI, score included, for each production vintage against the development reference and compare it to the declared maximum of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]], against the train-to-test value of 0.003083 [[art:e1d82330:psi.max]].

Because PSI needs only scores and input distributions, it can be produced monthly and serves as the early-warning quantity that leads each cycle.

AUC, Brier, and the calibration slope depend on realized outcomes and should be produced quarterly, or on the first cycle at which a cohort's performance window has closed, whichever is later.

The train-to-test PSI is far inside its bound, so the practical monitoring risk is not a single large jump but a slow drift, and the report should therefore trend each quantity across cycles rather than only testing the current value against its bound.

Persistent deviation outside these declared bounds, or a trend moving steadily toward one, is the trigger for considering overlays, adjustment, recalibration, or redevelopment under the organization's model risk management policy [[reg:SR26-2:V.1.b]].

### Ordering of the monitoring report

The performance section of this report presented discrimination before calibration, because the observed event rate on the evaluation split is at or above the ordering rule's bound of 0.05 [[art:42f1351e:rule.calibration_first_event_rate]].

For a future monitoring cohort whose observed event rate falls below 0.05 [[art:42f1351e:rule.calibration_first_event_rate]], the monitoring report should lead with calibration instead, since the slope and the Brier score carry more information than rank-ordering statistics on a sparse-event cohort.

The monitoring report should state the cohort's observed event rate alongside the ordering it chose, so that a reader can see which branch of the rule was taken.

### What this validation could not cover

The stability evidence available to this section compares the training and test splits of the development data, which is a weaker statement than a comparison of production vintages against the development reference, and monitoring should carry the latter.

This validation evaluated the model on a held-out split rather than over a realized post-implementation window, so back-testing against outcomes observed after the model entered use remains for monitoring, supplemented by early-warning trend analysis over shorter periods until enough outcome data accumulates [[reg:SR11-7:V.1.b]].

Process verification of the production implementation, including that data inputs remain accurate, complete, and consistent with model purpose, and that scoring code is under change control, was outside the scope of the quantities reviewed here and should be part of each monitoring cycle [[reg:SR11-7:V.1.b]].

Override behavior cannot be observed from development data at all, so monitoring should track the rate of overrides and the performance of overridden decisions, since a high rate or a consistently performance-improving override process indicates the model needs revision [[reg:SR11-7:V.1.b]].

Benchmarking against an alternative internal or vendor model, or against retail credit bureau data, was not part of this validation and would give monitoring an independent reference when the model's own quantities drift [[reg:SR11-7:V.1.b]].

Segment-level behavior is not visible in the aggregate quantities recommended above, so monitoring should recompute discrimination and calibration within the portfolio segments on which the model is used, since an aggregate value inside its bound can conceal a segment outside it.

The declared bounds are package-level thresholds carried from development rather than acceptable-performance ranges derived from live experience, and monitoring should revisit whether they remain the right expectations as outcome data accumulates [[reg:SR26-2:V]].

Material model risk can remain even where every monitored quantity sits inside its bound, so users of the output should be told these limitations and should supplement the score with complementary analysis rather than treating a passing monitoring cycle as evidence that no risk remains [[reg:SR26-2:V]].

## Appendix A — Claims

Grounding precision 0.9827 before repair (284 of 289 claims verified; 2 mismatch, 3 unsupported) and 1.0000 after 1 claim(s) rewritten and 4 number(s) removed from the prose. Per section (post-repair): summary 20/20; conceptual_soundness 59/59; data_integrity 48/48; outcomes 117/117; sensitivity 14/14; findings 16/16; monitoring 11/11.

Repairs:

| section | before | after | instruction to the drafter |
|---|---|---|---|
| outcomes | 10160 (mismatch) | 10500 (verified) | you wrote 10160 for metrics.train.sub.limit_bal_low.n; the artifact says 10158 (tolerance 0.5); cite the right artifact, correct the number, or remove it |

Developer claims: 2 of 2 declared in `package.yaml` verify against this run's artifacts.

Excluded numeric tokens (not claims): section_number (5.1, 5.2, 5.3); citation_hash (2ad8d1a5, a359de9d, abbe1a27, 1721ceae); regulatory_section_id (SR26-2:V, SR26-2:V.1.b, SR26-2:V.1.a, SR26-2:IV.1); package_version (1.0); extractor_returned_excluded_token (1.0, 5.1, 5.2, 5.3).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The subject was re-executed from the packaged artefacts unde… | 300 | ratio | runtime |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 2 | summary | The training split holds 21000 rows and the test split holds… | 21000 | count | n | train | eq | `[[art:a359de9d:profile.train.n]]` | verified | 21000 |
| 3 | summary | The training split holds 21000 rows and the test split holds… | 9000 | count | n | test | eq | `[[art:abbe1a27:profile.test.n]]` | verified | 9000 |
| 4 | summary | The recomputation scored the same populations, 21000 rows on… | 21000 | count | n | train | eq | `[[art:1721ceae:metrics.train.n]]` | verified | 21000 |
| 5 | summary | The recomputation scored the same populations, 21000 rows on… | 9000 | count | n | test | eq | `[[art:5367a59f:metrics.test.n]]` | verified | 9000 |
| 6 | summary | The outcome is close to evenly distributed between the split… | 0.2212 | ratio | event_rate | train | eq | `[[art:657aa7fc:metrics.train.event_rate]]` | verified | 0.2211904762 |
| 7 | summary | The outcome is close to evenly distributed between the split… | 0.2212 | ratio | event_rate | test | eq | `[[art:f60ae2a7:metrics.test.event_rate]]` | verified | 0.2212222222 |
| 8 | summary | The model passes the developer-declared discrimination floor… | 0.755 | ratio | auc | test | eq | `[[art:365b7034:metrics.test.auc]]` | verified | 0.7550239453 |
| 9 | summary | The model passes the developer-declared discrimination floor… | 0.7 | ratio | auc | test | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 10 | summary | It passes the declared accuracy ceiling: the test Brier scor… | 0.1385 | ratio | brier | test | eq | `[[art:86e93c8f:metrics.test.brier]]` | verified | 0.1385162411 |
| 11 | summary | It passes the declared accuracy ceiling: the test Brier scor… | 0.2 | ratio | brier | test | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 12 | summary | It passes the declared calibration band: the test calibratio… | 0.9886 | ratio | calibration_slope | test | eq | `[[art:e06564c7:calibration_slope.test]]` | verified | 0.9885680158 |
| 13 | summary | It passes the declared calibration band: the test calibratio… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 14 | summary | It passes the declared calibration band: the test calibratio… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 15 | summary | It passes the declared stability ceiling: the largest train-… | 0.003083 | ratio | psi |  | eq | `[[art:e1d82330:psi.max]]` | verified | 0.00308251646 |
| 16 | summary | It passes the declared stability ceiling: the largest train-… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 17 | summary | Discrimination is consistent across the two splits, with tra… | 0.7546 | ratio | auc | train | eq | `[[art:01cf8178:metrics.train.auc]]` | verified | 0.7545552576 |
| 18 | summary | Discrimination is consistent across the two splits, with tra… | 0.755 | ratio | auc | test | eq | `[[art:365b7034:metrics.test.auc]]` | verified | 0.7550239453 |
| 19 | summary | Discrimination is consistent across the two splits, with tra… | 1.001 | ratio | calibration_slope | train | eq | `[[art:85461245:calibration_slope.train]]` | verified | 1.000539237 |
| 20 | summary | Discrimination is consistent across the two splits, with tra… | 0.9886 | ratio | calibration_slope | test | eq | `[[art:e06564c7:calibration_slope.test]]` | verified | 0.9885680158 |
| 21 | conceptual_soundness | The champion is a linear-in-logit scoring model: a single in… | -1.442 | ratio | intercept |  | eq | `[[art:ca1c764c:run.model_summary#intercept]]` | verified | -1.441621171 |
| 22 | conceptual_soundness | The champion is a linear-in-logit scoring model: a single in… | 21000 | count | n_train | train | eq | `[[art:ca1c764c:run.model_summary#n_train]]` | verified | 21000 |
| 23 | conceptual_soundness | The package carries 12 features in total. | 12 | count | n |  | eq | `[[art:792cb79c:run.features#n]]` | verified | 12 |
| 24 | conceptual_soundness | Of these, 2 are known at origination and 10 are known before… | 2 | count | at_origination |  | eq | `[[art:792cb79c:run.features#at_origination]]` | verified | 2 |
| 25 | conceptual_soundness | Of these, 2 are known at origination and 10 are known before… | 10 | count | before_period_start |  | eq | `[[art:792cb79c:run.features#before_period_start]]` | verified | 10 |
| 26 | conceptual_soundness | None are dated during the period, at 0 , and none are dated… | 0 | count | during_period |  | eq | `[[art:792cb79c:run.features#during_period]]` | verified | 0 |
| 27 | conceptual_soundness | None are dated during the period, at 0 , and none are dated… | 0 | count | after_outcome |  | eq | `[[art:792cb79c:run.features#after_outcome]]` | verified | 0 |
| 28 | conceptual_soundness | The developer applied a variance-inflation screen at a thres… | 10 | ratio | vif_threshold |  | eq | `[[art:ca1c764c:run.model_summary#vif_threshold]]` | verified | 10 |
| 29 | conceptual_soundness | bill_last was removed at a VIF of 33.8 , far above the thres… | 33.8 | ratio | vif |  | eq | `[[art:ca1c764c:run.model_summary#removed.bill_last.vif]]` | verified | 33.803856 |
| 30 | conceptual_soundness | utilisation_mean_6m was removed at a VIF of 10.96 , only jus… | 10.96 | ratio | vif |  | eq | `[[art:ca1c764c:run.model_summary#removed.utilisation_mean_6m.vif]]` | verified | 10.962284 |
| 31 | conceptual_soundness | The largest coefficient by magnitude is delinq_last at 0.484… | 0.4847 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.delinq_last.value]]` | verified | 0.4846949872 |
| 32 | conceptual_soundness | The largest coefficient by magnitude is delinq_last at 0.484… | 0.2801 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.delinq_count_6m.value]]` | verified | 0.2800755777 |
| 33 | conceptual_soundness | The largest coefficient by magnitude is delinq_last at 0.484… | 0.2263 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.delinq_max_6m.value]]` | verified | 0.2262527885 |
| 34 | conceptual_soundness | The largest coefficient by magnitude is delinq_last at 0.484… | -0.2091 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.limit_bal.value]]` | verified | -0.2091380131 |
| 35 | conceptual_soundness | The remaining weights are materially smaller: pay_ratio_mean… | -0.09824 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.pay_ratio_mean_6m.value]]` | verified | -0.09823688664 |
| 36 | conceptual_soundness | The remaining weights are materially smaller: pay_ratio_mean… | -0.08257 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.utilisation.value]]` | verified | -0.08257487854 |
| 37 | conceptual_soundness | The remaining weights are materially smaller: pay_ratio_mean… | 0.07253 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.age.value]]` | verified | 0.07253007645 |
| 38 | conceptual_soundness | The remaining weights are materially smaller: pay_ratio_mean… | 0.04808 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.bill_trend_6m.value]]` | verified | 0.04808068095 |
| 39 | conceptual_soundness | The remaining weights are materially smaller: pay_ratio_mean… | -0.007568 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.bill_mean_6m.value]]` | verified | -0.007567968246 |
| 40 | conceptual_soundness | The remaining weights are materially smaller: pay_ratio_mean… | 0.00678 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.pay_ratio_last.value]]` | verified | 0.006779706816 |
| 41 | conceptual_soundness | Across the retained features, the count of fitted coefficien… | 3 | count | n_disagreements | train | eq | `[[art:e223cd4a:sign_check.n_disagreements]]` | verified | 3 |
| 42 | conceptual_soundness | The ablation deltas below are measured from a refit of the c… | 0.755 | ratio | auc | test | eq | `[[art:789072f8:ablation.baseline_auc]]` | verified | 0.7550239453 |
| 43 | conceptual_soundness | utilisation is one of the disagreements: its fitted coeffici… | -1 | ratio | coef_sign |  | eq | `[[art:46230409:sign_check.utilisation.coef_sign]]` | verified | -1 |
| 44 | conceptual_soundness | utilisation is one of the disagreements: its fitted coeffici… | 1 | ratio | univariate_direction |  | eq | `[[art:f0995196:sign_check.utilisation.univariate_direction]]` | verified | 1 |
| 45 | conceptual_soundness | utilisation is one of the disagreements: its fitted coeffici… | 0 | ratio | agrees |  | eq | `[[art:cb5a7bc7:sign_check.utilisation.agrees]]` | verified | 0 |
| 46 | conceptual_soundness | Refitting the champion's form without utilisation changes te… | 1.92e-05 | ratio | delta_auc | test | eq | `[[art:dc9ac505:ablation.utilisation.delta_auc]]` | verified | 1.920469764e-05 |
| 47 | conceptual_soundness | pay_ratio_last is the second disagreement: its fitted coeffi… | 1 | ratio | coef_sign |  | eq | `[[art:f018263e:sign_check.pay_ratio_last.coef_sign]]` | verified | 1 |
| 48 | conceptual_soundness | pay_ratio_last is the second disagreement: its fitted coeffi… | -1 | ratio | univariate_direction |  | eq | `[[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]]` | verified | -1 |
| 49 | conceptual_soundness | pay_ratio_last is the second disagreement: its fitted coeffi… | 0 | ratio | agrees |  | eq | `[[art:79abee77:sign_check.pay_ratio_last.agrees]]` | verified | 0 |
| 50 | conceptual_soundness | Its ablation delta is -5.589e-05 , a loss too small to repre… | -5.589e-05 | ratio | delta_auc | test | eq | `[[art:e26d8112:ablation.pay_ratio_last.delta_auc]]` | verified | -5.589426925e-05 |
| 51 | conceptual_soundness | Combined with a coefficient of 0.00678 , this is a sign flip… | 0.00678 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.pay_ratio_last.value]]` | verified | 0.006779706816 |
| 52 | conceptual_soundness | bill_trend_6m is the third and the one that matters most: it… | 1 | ratio | coef_sign |  | eq | `[[art:abd4aaba:sign_check.bill_trend_6m.coef_sign]]` | verified | 1 |
| 53 | conceptual_soundness | bill_trend_6m is the third and the one that matters most: it… | -1 | ratio | univariate_direction |  | eq | `[[art:a9bff389:sign_check.bill_trend_6m.univariate_direction]]` | verified | -1 |
| 54 | conceptual_soundness | bill_trend_6m is the third and the one that matters most: it… | 0 | ratio | agrees |  | eq | `[[art:c0f6d07d:sign_check.bill_trend_6m.agrees]]` | verified | 0 |
| 55 | conceptual_soundness | Removing it costs -0.001393 of test AUC, an order of magnitu… | -0.001393 | ratio | delta_auc | test | eq | `[[art:99f9dd71:ablation.bill_trend_6m.delta_auc]]` | verified | -0.001392555557 |
| 56 | conceptual_soundness | The other retained features agree with their univariate dire… | 1 | ratio | agrees |  | eq | `[[art:a8ba9372:sign_check.delinq_last.agrees]]` | verified | 1 |
| 57 | conceptual_soundness | The other retained features agree with their univariate dire… | 1 | ratio | agrees |  | eq | `[[art:a337d16b:sign_check.delinq_count_6m.agrees]]` | verified | 1 |
| 58 | conceptual_soundness | The other retained features agree with their univariate dire… | 1 | ratio | agrees |  | eq | `[[art:da92a015:sign_check.delinq_max_6m.agrees]]` | verified | 1 |
| 59 | conceptual_soundness | The other retained features agree with their univariate dire… | 1 | ratio | agrees |  | eq | `[[art:103d99fb:sign_check.limit_bal.agrees]]` | verified | 1 |
| 60 | conceptual_soundness | The other retained features agree with their univariate dire… | 1 | ratio | agrees |  | eq | `[[art:7e9a76ca:sign_check.pay_ratio_mean_6m.agrees]]` | verified | 1 |
| 61 | conceptual_soundness | The other retained features agree with their univariate dire… | 1 | ratio | agrees |  | eq | `[[art:89279c3b:sign_check.bill_mean_6m.agrees]]` | verified | 1 |
| 62 | conceptual_soundness | The other retained features agree with their univariate dire… | 1 | ratio | agrees |  | eq | `[[art:4116add1:sign_check.age.agrees]]` | verified | 1 |
| 63 | conceptual_soundness | The fitted signs on the features the model leans on hardest… | 1 | ratio | coef_sign |  | eq | `[[art:50d352f8:sign_check.delinq_last.coef_sign]]` | verified | 1 |
| 64 | conceptual_soundness | The fitted signs on the features the model leans on hardest… | 1 | ratio | univariate_direction |  | eq | `[[art:a78648ba:sign_check.delinq_last.univariate_direction]]` | verified | 1 |
| 65 | conceptual_soundness | The fitted signs on the features the model leans on hardest… | -1 | ratio | coef_sign |  | eq | `[[art:a6d01381:sign_check.limit_bal.coef_sign]]` | verified | -1 |
| 66 | conceptual_soundness | The fitted signs on the features the model leans on hardest… | -1 | ratio | univariate_direction |  | eq | `[[art:56d284d6:sign_check.limit_bal.univariate_direction]]` | verified | -1 |
| 67 | conceptual_soundness | delinq_last is the largest single contributor at -0.005914 ,… | -0.005914 | ratio | delta_auc | test | eq | `[[art:40f4e6bf:ablation.delinq_last.delta_auc]]` | verified | -0.005913828665 |
| 68 | conceptual_soundness | delinq_last is the largest single contributor at -0.005914 ,… | -0.003748 | ratio | delta_auc | test | eq | `[[art:57710b23:ablation.limit_bal.delta_auc]]` | verified | -0.003748140709 |
| 69 | conceptual_soundness | delinq_last is the largest single contributor at -0.005914 ,… | -0.002225 | ratio | delta_auc | test | eq | `[[art:f6fdd709:ablation.age.delta_auc]]` | verified | -0.002224986043 |
| 70 | conceptual_soundness | delinq_last is the largest single contributor at -0.005914 ,… | -0.002146 | ratio | delta_auc | test | eq | `[[art:db90576e:ablation.delinq_count_6m.delta_auc]]` | verified | -0.002145551687 |
| 71 | conceptual_soundness | Below those, delinq_max_6m contributes -0.001133 , pay_ratio… | -0.001133 | ratio | delta_auc | test | eq | `[[art:18cb1559:ablation.delinq_max_6m.delta_auc]]` | verified | -0.001133363798 |
| 72 | conceptual_soundness | Below those, delinq_max_6m contributes -0.001133 , pay_ratio… | -0.0009816 | ratio | delta_auc | test | eq | `[[art:cba98844:ablation.pay_ratio_mean_6m.delta_auc]]` | verified | -0.0009815893593 |
| 73 | conceptual_soundness | Below those, delinq_max_6m contributes -0.001133 , pay_ratio… | -0.0001527 | ratio | delta_auc | test | eq | `[[art:5b4423ab:ablation.bill_mean_6m.delta_auc]]` | verified | -0.00015270601 |
| 74 | conceptual_soundness | The champion's recomputed test AUC is 0.755 with a Brier sco… | 0.755 | ratio | auc | test | eq | `[[art:365b7034:metrics.test.auc]]` | verified | 0.7550239453 |
| 75 | conceptual_soundness | The champion's recomputed test AUC is 0.755 with a Brier sco… | 0.1385 | ratio | brier | test | eq | `[[art:86e93c8f:metrics.test.brier]]` | verified | 0.1385162411 |
| 76 | conceptual_soundness | The challenger reaches a test AUC of 0.7789 and a Brier scor… | 0.7789 | ratio | auc | test | eq | `[[art:5646e7f3:challenger.auc]]` | verified | 0.7789298885 |
| 77 | conceptual_soundness | The challenger reaches a test AUC of 0.7789 and a Brier scor… | 0.135 | ratio | brier | test | eq | `[[art:2031a154:challenger.brier]]` | verified | 0.1349523392 |
| 78 | conceptual_soundness | The challenger's AUC lead over the champion is 0.02391 . | 0.02391 | ratio | delta_auc | test | eq | `[[art:3877bdd0:challenger.delta_auc]]` | verified | 0.02390594313 |
| 79 | conceptual_soundness | The threshold that decides whether such a lead matters is a… | 0.03 | ratio | delta_auc |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 80 | data_integrity | The training split holds 21000 rows and the test split holds… | 21000 | count | n | train | eq | `[[art:a359de9d:profile.train.n]]` | verified | 21000 |
| 81 | data_integrity | The training split holds 21000 rows and the test split holds… | 9000 | count | n | test | eq | `[[art:abbe1a27:profile.test.n]]` | verified | 9000 |
| 82 | data_integrity | The largest missing fraction in train is 0 , and the largest… | 0 | ratio | missing | train | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 83 | data_integrity | The largest missing fraction in train is 0 , and the largest… | 0 | ratio | missing | test | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 84 | data_integrity | The two maxima are equal, so no gap separates the splits, an… | 0.1 | ratio | missing_gap |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 85 | data_integrity | The largest train-to-test population stability index, score… | 0.003083 | ratio | psi |  | eq | `[[art:e1d82330:psi.max]]` | verified | 0.00308251646 |
| 86 | data_integrity | The largest train-to-test population stability index, score… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 87 | data_integrity | The largest train-to-test population stability index, score… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 88 | data_integrity | That maximum is attributable to age, whose PSI between train… | 0.003083 | ratio | psi |  | eq | `[[art:06c22a63:psi.age]]` | verified | 0.00308251646 |
| 89 | data_integrity | Among the remaining inputs, pay_ratio_last reaches 0.002264… | 0.002264 | ratio | psi |  | eq | `[[art:82c97112:psi.pay_ratio_last]]` | verified | 0.0022643364 |
| 90 | data_integrity | Among the remaining inputs, pay_ratio_last reaches 0.002264… | 0.001856 | ratio | psi |  | eq | `[[art:d77ddb1d:psi.delinq_count_6m]]` | verified | 0.00185562271 |
| 91 | data_integrity | Among the remaining inputs, pay_ratio_last reaches 0.002264… | 0.001488 | ratio | psi |  | eq | `[[art:127cdf82:psi.bill_mean_6m]]` | verified | 0.001488231386 |
| 92 | data_integrity | Among the remaining inputs, pay_ratio_last reaches 0.002264… | 0.001272 | ratio | psi |  | eq | `[[art:b0195847:psi.limit_bal]]` | verified | 0.001272099805 |
| 93 | data_integrity | The rest sit lower still: pay_ratio_mean_6m at 0.001028 , de… | 0.001028 | ratio | psi |  | eq | `[[art:62e0e0f8:psi.pay_ratio_mean_6m]]` | verified | 0.001027537662 |
| 94 | data_integrity | The rest sit lower still: pay_ratio_mean_6m at 0.001028 , de… | 0.001027 | ratio | psi |  | eq | `[[art:4b0a94ab:psi.delinq_max_6m]]` | verified | 0.001026806992 |
| 95 | data_integrity | The rest sit lower still: pay_ratio_mean_6m at 0.001028 , de… | 0.0007484 | ratio | psi |  | eq | `[[art:78be70d2:psi.bill_trend_6m]]` | verified | 0.0007484247754 |
| 96 | data_integrity | The rest sit lower still: pay_ratio_mean_6m at 0.001028 , de… | 0.0006523 | ratio | psi |  | eq | `[[art:f094559b:psi.utilisation]]` | verified | 0.0006522718782 |
| 97 | data_integrity | The rest sit lower still: pay_ratio_mean_6m at 0.001028 , de… | 0.0002347 | ratio | psi |  | eq | `[[art:cbc9de36:psi.delinq_last]]` | verified | 0.0002346592849 |
| 98 | data_integrity | The score itself shifts by a PSI of 0.001368 , so the output… | 0.001368 | ratio | psi |  | eq | `[[art:ec2b8d1b:psi.y_score]]` | verified | 0.001367653962 |
| 99 | data_integrity | Every one of these values is two orders of magnitude inside… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 100 | data_integrity | The largest characteristic stability index is 0.004737 , car… | 0.004737 | ratio | csi |  | eq | `[[art:ce1257d8:csi.max]]` | verified | 0.00473710965 |
| 101 | data_integrity | The largest characteristic stability index is 0.004737 , car… | 0.004737 | ratio | csi |  | eq | `[[art:35990a39:csi.delinq_max_6m]]` | verified | 0.00473710965 |
| 102 | data_integrity | The next largest contributions to the shift in the linear pr… | 0.002043 | ratio | csi |  | eq | `[[art:5e53c153:csi.pay_ratio_mean_6m]]` | verified | 0.002042601165 |
| 103 | data_integrity | The next largest contributions to the shift in the linear pr… | 0.001698 | ratio | csi |  | eq | `[[art:e755cf0a:csi.delinq_last]]` | verified | 0.001697603731 |
| 104 | data_integrity | The next largest contributions to the shift in the linear pr… | 0.001384 | ratio | csi |  | eq | `[[art:c91a2a4b:csi.limit_bal]]` | verified | 0.001384099928 |
| 105 | data_integrity | The next largest contributions to the shift in the linear pr… | 0.001203 | ratio | csi |  | eq | `[[art:25b88f37:csi.age]]` | verified | 0.001203264027 |
| 106 | data_integrity | The remainder are smaller again: delinq_count_6m at 0.000878… | 0.0008781 | ratio | csi |  | eq | `[[art:f0438233:csi.delinq_count_6m]]` | verified | 0.0008781439663 |
| 107 | data_integrity | The remainder are smaller again: delinq_count_6m at 0.000878… | 0.0003675 | ratio | csi |  | eq | `[[art:9e5a9b68:csi.bill_trend_6m]]` | verified | 0.0003674527783 |
| 108 | data_integrity | The remainder are smaller again: delinq_count_6m at 0.000878… | 0.0002136 | ratio | csi |  | eq | `[[art:6ed37e42:csi.utilisation]]` | verified | 0.0002135922405 |
| 109 | data_integrity | The remainder are smaller again: delinq_count_6m at 0.000878… | 0.0001132 | ratio | csi |  | eq | `[[art:5898a9c5:csi.pay_ratio_last]]` | verified | 0.0001131831266 |
| 110 | data_integrity | The remainder are smaller again: delinq_count_6m at 0.000878… | 9.982e-06 | ratio | csi |  | eq | `[[art:0c34001d:csi.bill_mean_6m]]` | verified | 9.982086887e-06 |
| 111 | data_integrity | Read against the same declared stability bound of 0.25 , no… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 112 | data_integrity | The timing screen reads the declared timing of each feature… | 0 | count | n_flagged |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 113 | data_integrity | The strongest single feature reaches an AUC of 0.728 on its… | 0.728 | ratio | auc |  | eq | `[[art:2e212f3a:leakage.target_corr.max_single_feature_auc]]` | verified | 0.7279795601 |
| 114 | data_integrity | The strongest single feature reaches an AUC of 0.728 on its… | 0.9 | ratio | auc |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 115 | data_integrity | The identifier arm finds that 0 of test rows carry a client_… | 0 | ratio | overlap |  | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 116 | data_integrity | The identifier arm finds that 0 of test rows carry a client_… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 117 | data_integrity | The feature-vector arm finds that 0.01256 of test rows have… | 0.01256 | ratio | overlap |  | eq | `[[art:517f3049:leakage.overlap.features]]` | verified | 0.01255555556 |
| 118 | data_integrity | The feature-vector arm finds that 0.01256 of test rows have… | 0.02324 | ratio | overlap |  | eq | `[[art:7cdc63cb:threshold.L2.overlap.features_effective]]` | verified | 0.02323809524 |
| 119 | data_integrity | That effective bound is the larger of the declared 0.005 and… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 120 | data_integrity | That effective bound is the larger of the declared 0.005 and… | 0.01162 | ratio | duplicates | train | eq | `[[art:c988bb0e:leakage.duplicates.train]]` | verified | 0.01161904762 |
| 121 | data_integrity | The headline overlap figure of 0.01256 is the same feature-v… | 0.01256 | ratio | overlap |  | eq | `[[art:ebd7ff30:leakage.overlap]]` | verified | 0.01255555556 |
| 122 | data_integrity | The headline overlap figure of 0.01256 is the same feature-v… | 0.02324 | ratio | overlap |  | eq | `[[art:7cdc63cb:threshold.L2.overlap.features_effective]]` | verified | 0.02323809524 |
| 123 | data_integrity | Because the identifier arm is at 0 while the feature arm is… | 0 | ratio | overlap |  | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 124 | data_integrity | The name screen matches feature names against a target-adjac… | 0 | count | n_matched |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 125 | data_integrity | Every quantity above sits inside the bound it was read again… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 126 | data_integrity | The one screen worth carrying forward as a documented assump… | 0.01162 | ratio | duplicates | train | eq | `[[art:c988bb0e:leakage.duplicates.train]]` | verified | 0.01161904762 |
| 127 | data_integrity | The one screen worth carrying forward as a documented assump… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 128 | outcomes | The reason is the observed event rate on the evaluation spli… | 0.2212 | ratio | event_rate | test | eq | `[[art:f60ae2a7:metrics.test.event_rate]]` | verified | 0.2212222222 |
| 129 | outcomes | The reason is the observed event rate on the evaluation spli… | 0.05 | ratio | calibration_first_event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 130 | outcomes | \| n \| 21000 \| 9000 \| | 21000 | count | n | train | eq | `[[art:1721ceae:metrics.train.n]]` | verified | 21000 |
| 131 | outcomes | \| n \| 21000 \| 9000 \| | 9000 | count | n | test | eq | `[[art:5367a59f:metrics.test.n]]` | verified | 9000 |
| 132 | outcomes | \| event_rate \| 0.2212 \| 0.2212 \| | 0.2212 | ratio | event_rate | train | eq | `[[art:657aa7fc:metrics.train.event_rate]]` | verified | 0.2211904762 |
| 133 | outcomes | \| event_rate \| 0.2212 \| 0.2212 \| | 0.2212 | ratio | event_rate | test | eq | `[[art:f60ae2a7:metrics.test.event_rate]]` | verified | 0.2212222222 |
| 134 | outcomes | \| auc \| 0.7546 \| 0.755 \| | 0.7546 | ratio | auc | train | eq | `[[art:01cf8178:metrics.train.auc]]` | verified | 0.7545552576 |
| 135 | outcomes | \| auc \| 0.7546 \| 0.755 \| | 0.755 | ratio | auc | test | eq | `[[art:365b7034:metrics.test.auc]]` | verified | 0.7550239453 |
| 136 | outcomes | \| gini \| 0.5091 \| 0.51 \| | 0.5091 | ratio | gini | train | eq | `[[art:eaaf0f79:metrics.train.gini]]` | verified | 0.5091105152 |
| 137 | outcomes | \| gini \| 0.5091 \| 0.51 \| | 0.51 | ratio | gini | test | eq | `[[art:296bfeeb:metrics.test.gini]]` | verified | 0.5100478906 |
| 138 | outcomes | \| ks \| 0.4144 \| 0.4067 \| | 0.4144 | ratio | ks | train | eq | `[[art:18df22bd:metrics.train.ks]]` | verified | 0.4144375385 |
| 139 | outcomes | \| ks \| 0.4144 \| 0.4067 \| | 0.4067 | ratio | ks | test | eq | `[[art:d3c4ed61:metrics.test.ks]]` | verified | 0.4066831201 |
| 140 | outcomes | \| brier \| 0.1384 \| 0.1385 \| | 0.1384 | ratio | brier | train | eq | `[[art:c95106e9:metrics.train.brier]]` | verified | 0.1383762773 |
| 141 | outcomes | \| brier \| 0.1384 \| 0.1385 \| | 0.1385 | ratio | brier | test | eq | `[[art:86e93c8f:metrics.test.brier]]` | verified | 0.1385162411 |
| 142 | outcomes | \| logloss \| 0.4439 \| 0.4442 \| | 0.4439 | ratio | logloss | train | eq | `[[art:b816b083:metrics.train.logloss]]` | verified | 0.4439401117 |
| 143 | outcomes | \| logloss \| 0.4439 \| 0.4442 \| | 0.4442 | ratio | logloss | test | eq | `[[art:2de58c1b:metrics.test.logloss]]` | verified | 0.4441654047 |
| 144 | outcomes | \| mean_predicted \| 0.2212 \| 0.2206 \| | 0.2212 | ratio | mean_predicted | train | eq | `[[art:935d2cb7:metrics.train.mean_predicted]]` | verified | 0.2212248699 |
| 145 | outcomes | \| mean_predicted \| 0.2212 \| 0.2206 \| | 0.2206 | ratio | mean_predicted | test | eq | `[[art:89d241ea:metrics.test.mean_predicted]]` | verified | 0.2205710384 |
| 146 | outcomes | The capture of test events in the highest-ranked deciles is… | 0.4952 | ratio | top2_capture | test | eq | `[[art:e2c0ad9f:deciles.test.top2_capture]]` | verified | 0.4952285284 |
| 147 | outcomes | The capture of test events in the highest-ranked deciles is… | 0.5031 | ratio | top2_capture | train | eq | `[[art:5131afa7:deciles.train.top2_capture]]` | verified | 0.5031216362 |
| 148 | outcomes | The gap between the splits is bounded by threshold.O1.auc_ga… | 0.08 | ratio | auc_gap |  | eq | `[[art:630f28f4:threshold.O1.auc_gap]]` | verified | 0.08 |
| 149 | outcomes | Train AUC of 0.7546 and test AUC of 0.755 sit within that bo… | 0.7546 | ratio | auc | train | eq | `[[art:01cf8178:metrics.train.auc]]` | verified | 0.7545552576 |
| 150 | outcomes | Train AUC of 0.7546 and test AUC of 0.755 sit within that bo… | 0.755 | ratio | auc | test | eq | `[[art:365b7034:metrics.test.auc]]` | verified | 0.7550239453 |
| 151 | outcomes | The same pattern holds on the rank statistics, where train k… | 0.4144 | ratio | ks | train | eq | `[[art:18df22bd:metrics.train.ks]]` | verified | 0.4144375385 |
| 152 | outcomes | The same pattern holds on the rank statistics, where train k… | 0.4067 | ratio | ks | test | eq | `[[art:d3c4ed61:metrics.test.ks]]` | verified | 0.4066831201 |
| 153 | outcomes | The calibration slope on test, from the logistic regression… | 0.9886 | ratio | calibration_slope | test | eq | `[[art:e06564c7:calibration_slope.test]]` | verified | 0.9885680158 |
| 154 | outcomes | The calibration slope on test, from the logistic regression… | 0.8 | ratio | calibration_slope |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 155 | outcomes | The calibration slope on test, from the logistic regression… | 1.2 | ratio | calibration_slope |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 156 | outcomes | The corresponding intercept is -0.008632 , close enough to t… | -0.008632 | ratio | calibration_intercept | test | eq | `[[art:2ee976d3:calibration_intercept.test]]` | verified | -0.008632158167 |
| 157 | outcomes | On train the slope is 1.001 and the intercept is 0.0003779 ,… | 1.001 | ratio | calibration_slope | train | eq | `[[art:85461245:calibration_slope.train]]` | verified | 1.000539237 |
| 158 | outcomes | On train the slope is 1.001 and the intercept is 0.0003779 ,… | 0.0003779 | ratio | calibration_intercept | train | eq | `[[art:2ce8cd09:calibration_intercept.train]]` | verified | 0.0003779479547 |
| 159 | outcomes | Mean predicted probability on test is 0.2206 against an obse… | 0.2206 | ratio | mean_predicted | test | eq | `[[art:89d241ea:metrics.test.mean_predicted]]` | verified | 0.2205710384 |
| 160 | outcomes | Mean predicted probability on test is 0.2206 against an obse… | 0.2212 | ratio | event_rate | test | eq | `[[art:f60ae2a7:metrics.test.event_rate]]` | verified | 0.2212222222 |
| 161 | outcomes | The relative gap between the two is 0.002944 , inside the to… | 0.002944 | ratio | mean_rel_gap | test | eq | `[[art:bae28fd6:calibration.mean_rel_gap.test]]` | verified | 0.00294357342 |
| 162 | outcomes | The relative gap between the two is 0.002944 , inside the to… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 163 | outcomes | The relative gap between the two is 0.002944 , inside the to… | 0.0001555 | ratio | mean_rel_gap | train | eq | `[[art:a03ea014:calibration.mean_rel_gap.train]]` | verified | 0.0001554936592 |
| 164 | outcomes | A sub-population's AUC may fall below its split's own AUC by… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 165 | outcomes | A sub-population's AUC may fall below its split's own AUC by… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 166 | outcomes | On test the slice holds 0.487 of the split with n of 4383 ,… | 0.487 | ratio | share | test | eq | `[[art:e7847e2b:metrics.test.sub.limit_bal_low.share]]` | verified | 0.487 |
| 167 | outcomes | On test the slice holds 0.487 of the split with n of 4383 ,… | 4383 | count | n | test | eq | `[[art:686cad5e:metrics.test.sub.limit_bal_low.n]]` | verified | 4383 |
| 168 | outcomes | On test the slice holds 0.487 of the split with n of 4383 ,… | 0.2877 | ratio | event_rate | test | eq | `[[art:9629805c:metrics.test.sub.limit_bal_low.event_rate]]` | verified | 0.2877024869 |
| 169 | outcomes | On test the slice holds 0.487 of the split with n of 4383 ,… | 0.2802 | ratio | mean_predicted | test | eq | `[[art:e3d342d5:metrics.test.sub.limit_bal_low.mean_predicted]]` | verified | 0.2801722167 |
| 170 | outcomes | On test the slice holds 0.487 of the split with n of 4383 ,… | 0.7477 | ratio | auc | test | eq | `[[art:26da9c77:metrics.test.sub.limit_bal_low.auc]]` | verified | 0.7477379077 |
| 171 | outcomes | On test the slice holds 0.487 of the split with n of 4383 ,… | 0.4955 | ratio | gini | test | eq | `[[art:1d9599c6:metrics.test.sub.limit_bal_low.gini]]` | verified | 0.4954758154 |
| 172 | outcomes | On test the slice holds 0.487 of the split with n of 4383 ,… | 0.4047 | ratio | ks | test | eq | `[[art:39f5214d:metrics.test.sub.limit_bal_low.ks]]` | verified | 0.4047386204 |
| 173 | outcomes | On test the slice holds 0.487 of the split with n of 4383 ,… | 0.1675 | ratio | brier | test | eq | `[[art:68867046:metrics.test.sub.limit_bal_low.brier]]` | verified | 0.1674846594 |
| 174 | outcomes | On test the slice holds 0.487 of the split with n of 4383 ,… | 0.5165 | ratio | logloss | test | eq | `[[art:194532b1:metrics.test.sub.limit_bal_low.logloss]]` | verified | 0.5164924891 |
| 175 | outcomes | On train the slice holds 0.4837 of the split, with an event… | 0.4837 | ratio | share | train | eq | `[[art:d4eb837c:metrics.train.sub.limit_bal_low.share]]` | verified | 0.4837142857 |
| 176 | outcomes | On train the slice holds 0.4837 of the split, with an event… | 0.2846 | ratio | event_rate | train | eq | `[[art:815577c8:metrics.train.sub.limit_bal_low.event_rate]]` | verified | 0.2846032684 |
| 177 | outcomes | On train the slice holds 0.4837 of the split, with an event… | 0.282 | ratio | mean_predicted | train | eq | `[[art:03370fd4:metrics.train.sub.limit_bal_low.mean_predicted]]` | verified | 0.2820440763 |
| 178 | outcomes | On train the slice holds 0.4837 of the split, with an event… | 0.7557 | ratio | auc | train | eq | `[[art:d3864be2:metrics.train.sub.limit_bal_low.auc]]` | verified | 0.755664374 |
| 179 | outcomes | On train the slice holds 0.4837 of the split, with an event… | 0.5113 | ratio | gini | train | eq | `[[art:efffd200:metrics.train.sub.limit_bal_low.gini]]` | verified | 0.511328748 |
| 180 | outcomes | On train the slice holds 0.4837 of the split, with an event… | 0.4305 | ratio | ks | train | eq | `[[art:a95d8865:metrics.train.sub.limit_bal_low.ks]]` | verified | 0.4304590098 |
| 181 | outcomes | On train the slice holds 0.4837 of the split, with an event… | 0.1623 | ratio | brier | train | eq | `[[art:58d900b3:metrics.train.sub.limit_bal_low.brier]]` | verified | 0.1623351934 |
| 182 | outcomes | On train the slice holds 0.4837 of the split, with an event… | 0.5042 | ratio | logloss | train | eq | `[[art:c0e7dc4c:metrics.train.sub.limit_bal_low.logloss]]` | verified | 0.5041966841 |
| 183 | outcomes | The slice AUC falls below its split's by 0.007286 on test an… | 0.007286 | ratio | auc_gap | test | eq | `[[art:15e1edcb:metrics.test.sub.limit_bal_low.auc_gap]]` | verified | 0.007286037626 |
| 184 | outcomes | The slice AUC falls below its split's by 0.007286 on test an… | -0.02732 | ratio | auc_gap | train | eq | `[[art:41fca294:metrics.train.sub.utilisation_high.auc_gap]]` | verified | -0.02732151154 |
| 185 | outcomes | The slice AUC falls below its split's by 0.007286 on test an… | -0.001109 | ratio | auc_gap | train | eq | `[[art:021950a5:metrics.train.sub.limit_bal_low.auc_gap]]` | verified | -0.001109116413 |
| 186 | outcomes | On test the slice holds 0.775 of the split with n of 6975 ,… | 0.775 | ratio | share | test | eq | `[[art:2caf0a26:metrics.test.sub.delinq_last_eq_0.share]]` | verified | 0.775 |
| 187 | outcomes | On test the slice holds 0.775 of the split with n of 6975 ,… | 6975 | count | n | test | eq | `[[art:cd0a7adb:metrics.test.sub.delinq_last_eq_0.n]]` | verified | 6975 |
| 188 | outcomes | On test the slice holds 0.775 of the split with n of 6975 ,… | 0.1405 | ratio | event_rate | test | eq | `[[art:46acca95:metrics.test.sub.delinq_last_eq_0.event_rate]]` | verified | 0.1405017921 |
| 189 | outcomes | On test the slice holds 0.775 of the split with n of 6975 ,… | 0.1371 | ratio | mean_predicted | test | eq | `[[art:3d1e089a:metrics.test.sub.delinq_last_eq_0.mean_predicted]]` | verified | 0.137076189 |
| 190 | outcomes | On test the slice holds 0.775 of the split with n of 6975 ,… | 0.6312 | ratio | auc | test | eq | `[[art:1b96a24d:metrics.test.sub.delinq_last_eq_0.auc]]` | verified | 0.6311898521 |
| 191 | outcomes | On test the slice holds 0.775 of the split with n of 6975 ,… | 0.2624 | ratio | gini | test | eq | `[[art:1183089b:metrics.test.sub.delinq_last_eq_0.gini]]` | verified | 0.2623797042 |
| 192 | outcomes | On test the slice holds 0.775 of the split with n of 6975 ,… | 0.2105 | ratio | ks | test | eq | `[[art:4d6488ce:metrics.test.sub.delinq_last_eq_0.ks]]` | verified | 0.2105487566 |
| 193 | outcomes | On test the slice holds 0.775 of the split with n of 6975 ,… | 0.1168 | ratio | brier | test | eq | `[[art:2bce5eb5:metrics.test.sub.delinq_last_eq_0.brier]]` | verified | 0.1168254801 |
| 194 | outcomes | On test the slice holds 0.775 of the split with n of 6975 ,… | 0.3918 | ratio | logloss | test | eq | `[[art:26913d06:metrics.test.sub.delinq_last_eq_0.logloss]]` | verified | 0.391800392 |
| 195 | outcomes | On train the slice holds 0.7718 of the split, with an event… | 0.7718 | ratio | share | train | eq | `[[art:39ead1e5:metrics.train.sub.delinq_last_eq_0.share]]` | verified | 0.7717619048 |
| 196 | outcomes | On train the slice holds 0.7718 of the split, with an event… | 0.1374 | ratio | event_rate | train | eq | `[[art:b158c0fb:metrics.train.sub.delinq_last_eq_0.event_rate]]` | verified | 0.1374097612 |
| 197 | outcomes | On train the slice holds 0.7718 of the split, with an event… | 0.138 | ratio | mean_predicted | train | eq | `[[art:121d5b67:metrics.train.sub.delinq_last_eq_0.mean_predicted]]` | verified | 0.1380373247 |
| 198 | outcomes | On train the slice holds 0.7718 of the split, with an event… | 0.6205 | ratio | auc | train | eq | `[[art:f1c7d62f:metrics.train.sub.delinq_last_eq_0.auc]]` | verified | 0.6205034872 |
| 199 | outcomes | On train the slice holds 0.7718 of the split, with an event… | 0.241 | ratio | gini | train | eq | `[[art:43a02d18:metrics.train.sub.delinq_last_eq_0.gini]]` | verified | 0.2410069745 |
| 200 | outcomes | On train the slice holds 0.7718 of the split, with an event… | 0.1768 | ratio | ks | train | eq | `[[art:792e2044:metrics.train.sub.delinq_last_eq_0.ks]]` | verified | 0.176800619 |
| 201 | outcomes | On train the slice holds 0.7718 of the split, with an event… | 0.1146 | ratio | brier | train | eq | `[[art:8583b4e5:metrics.train.sub.delinq_last_eq_0.brier]]` | verified | 0.1146044072 |
| 202 | outcomes | On train the slice holds 0.7718 of the split, with an event… | 0.3864 | ratio | logloss | train | eq | `[[art:cd7b90e8:metrics.train.sub.delinq_last_eq_0.logloss]]` | verified | 0.38638584 |
| 203 | outcomes | The slice AUC falls below its split's by 0.1238 on test and… | 0.1238 | ratio | auc_gap | test | eq | `[[art:90bff412:metrics.test.sub.delinq_last_eq_0.auc_gap]]` | verified | 0.1238340932 |
| 204 | outcomes | The slice AUC falls below its split's by 0.1238 on test and… | 0.1341 | ratio | auc_gap | train | eq | `[[art:9bd52249:metrics.train.sub.delinq_last_eq_0.auc_gap]]` | verified | 0.1340517703 |
| 205 | outcomes | On test the slice holds 0.1218 of the split with n of 1096 ,… | 0.1218 | ratio | share | test | eq | `[[art:ba192c04:metrics.test.sub.delinq_last_eq_1.share]]` | verified | 0.1217777778 |
| 206 | outcomes | On test the slice holds 0.1218 of the split with n of 1096 ,… | 1096 | count | n | test | eq | `[[art:664c19bf:metrics.test.sub.delinq_last_eq_1.n]]` | verified | 1096 |
| 207 | outcomes | On test the slice holds 0.1218 of the split with n of 1096 ,… | 0.3321 | ratio | event_rate | test | eq | `[[art:3d353862:metrics.test.sub.delinq_last_eq_1.event_rate]]` | verified | 0.3321167883 |
| 208 | outcomes | On test the slice holds 0.1218 of the split with n of 1096 ,… | 0.3858 | ratio | mean_predicted | test | eq | `[[art:6411ed69:metrics.test.sub.delinq_last_eq_1.mean_predicted]]` | verified | 0.3858491811 |
| 209 | outcomes | On test the slice holds 0.1218 of the split with n of 1096 ,… | 0.6513 | ratio | auc | test | eq | `[[art:1d01d834:metrics.test.sub.delinq_last_eq_1.auc]]` | verified | 0.6513372215 |
| 210 | outcomes | On test the slice holds 0.1218 of the split with n of 1096 ,… | 0.3027 | ratio | gini | test | eq | `[[art:aeb8f8a5:metrics.test.sub.delinq_last_eq_1.gini]]` | verified | 0.302674443 |
| 211 | outcomes | On test the slice holds 0.1218 of the split with n of 1096 ,… | 0.2587 | ratio | ks | test | eq | `[[art:343e93a8:metrics.test.sub.delinq_last_eq_1.ks]]` | verified | 0.2587071399 |
| 212 | outcomes | On test the slice holds 0.1218 of the split with n of 1096 ,… | 0.2105 | ratio | brier | test | eq | `[[art:82c35e29:metrics.test.sub.delinq_last_eq_1.brier]]` | verified | 0.2104514634 |
| 213 | outcomes | On test the slice holds 0.1218 of the split with n of 1096 ,… | 0.6103 | ratio | logloss | test | eq | `[[art:089e61ce:metrics.test.sub.delinq_last_eq_1.logloss]]` | verified | 0.6102554962 |
| 214 | outcomes | On train the slice holds 0.1234 with n of 2592 , an event ra… | 0.1234 | ratio | share | train | eq | `[[art:3b48f1bc:metrics.train.sub.delinq_last_eq_1.share]]` | verified | 0.1234285714 |
| 215 | outcomes | On train the slice holds 0.1234 with n of 2592 , an event ra… | 2592 | count | n | train | eq | `[[art:7dfec1a7:metrics.train.sub.delinq_last_eq_1.n]]` | verified | 2592 |
| 216 | outcomes | On train the slice holds 0.1234 with n of 2592 , an event ra… | 0.3426 | ratio | event_rate | train | eq | `[[art:d1e0caab:metrics.train.sub.delinq_last_eq_1.event_rate]]` | verified | 0.3425925926 |
| 217 | outcomes | On train the slice holds 0.1234 with n of 2592 , an event ra… | 0.3841 | ratio | mean_predicted | train | eq | `[[art:90c4acea:metrics.train.sub.delinq_last_eq_1.mean_predicted]]` | verified | 0.3841118294 |
| 218 | outcomes | On train the slice holds 0.1234 with n of 2592 , an event ra… | 0.6441 | ratio | auc | train | eq | `[[art:5a17ab4a:metrics.train.sub.delinq_last_eq_1.auc]]` | verified | 0.6441484398 |
| 219 | outcomes | On train the slice holds 0.1234 with n of 2592 , an event ra… | 0.2883 | ratio | gini | train | eq | `[[art:539c7e22:metrics.train.sub.delinq_last_eq_1.gini]]` | verified | 0.2882968796 |
| 220 | outcomes | On train the slice holds 0.1234 with n of 2592 , an event ra… | 0.2314 | ratio | ks | train | eq | `[[art:4c6c5159:metrics.train.sub.delinq_last_eq_1.ks]]` | verified | 0.2313951275 |
| 221 | outcomes | On train the slice holds 0.1234 with n of 2592 , an event ra… | 0.214 | ratio | brier | train | eq | `[[art:b31f006a:metrics.train.sub.delinq_last_eq_1.brier]]` | verified | 0.2139999197 |
| 222 | outcomes | On train the slice holds 0.1234 with n of 2592 , an event ra… | 0.6179 | ratio | logloss | train | eq | `[[art:1f5cba97:metrics.train.sub.delinq_last_eq_1.logloss]]` | verified | 0.6178764991 |
| 223 | outcomes | The slice AUC falls below its split's by 0.1037 on test and… | 0.1037 | ratio | auc_gap | test | eq | `[[art:7e196964:metrics.test.sub.delinq_last_eq_1.auc_gap]]` | verified | 0.1036867238 |
| 224 | outcomes | The slice AUC falls below its split's by 0.1037 on test and… | 0.1104 | ratio | auc_gap | train | eq | `[[art:d6cf38ec:metrics.train.sub.delinq_last_eq_1.auc_gap]]` | verified | 0.1104068178 |
| 225 | outcomes | On test the slice holds 0.5 of the split with n of 4500 , an… | 0.5 | ratio | share | test | eq | `[[art:9404484e:metrics.test.sub.utilisation_high.share]]` | verified | 0.5 |
| 226 | outcomes | On test the slice holds 0.5 of the split with n of 4500 , an… | 4500 | count | n | test | eq | `[[art:ee72f76a:metrics.test.sub.utilisation_high.n]]` | verified | 4500 |
| 227 | outcomes | On test the slice holds 0.5 of the split with n of 4500 , an… | 0.2658 | ratio | event_rate | test | eq | `[[art:e4a00a59:metrics.test.sub.utilisation_high.event_rate]]` | verified | 0.2657777778 |
| 228 | outcomes | On test the slice holds 0.5 of the split with n of 4500 , an… | 0.2608 | ratio | mean_predicted | test | eq | `[[art:e68f1a3d:metrics.test.sub.utilisation_high.mean_predicted]]` | verified | 0.2608314072 |
| 229 | outcomes | On test the slice holds 0.5 of the split with n of 4500 , an… | 0.7781 | ratio | auc | test | eq | `[[art:7a00057d:metrics.test.sub.utilisation_high.auc]]` | verified | 0.7781142954 |
| 230 | outcomes | On test the slice holds 0.5 of the split with n of 4500 , an… | 0.5562 | ratio | gini | test | eq | `[[art:0500c179:metrics.test.sub.utilisation_high.gini]]` | verified | 0.5562285909 |
| 231 | outcomes | On test the slice holds 0.5 of the split with n of 4500 , an… | 0.4739 | ratio | ks | test | eq | `[[art:096c8d60:metrics.test.sub.utilisation_high.ks]]` | verified | 0.4738747803 |
| 232 | outcomes | On test the slice holds 0.5 of the split with n of 4500 , an… | 0.1492 | ratio | brier | test | eq | `[[art:80c11b34:metrics.test.sub.utilisation_high.brier]]` | verified | 0.1491771843 |
| 233 | outcomes | On test the slice holds 0.5 of the split with n of 4500 , an… | 0.4717 | ratio | logloss | test | eq | `[[art:24970875:metrics.test.sub.utilisation_high.logloss]]` | verified | 0.4716985136 |
| 234 | outcomes | On train the slice holds 0.5 with n of 10500 , an event rate… | 0.5 | ratio | share | train | eq | `[[art:0ff76e00:metrics.train.sub.utilisation_high.share]]` | verified | 0.5 |
| 235 | outcomes | On train the slice holds 0.5 with n of 10500 , an event rate… | 10500 | count | n | train | eq | `[[art:fe8f2ffa:metrics.train.sub.utilisation_high.n]]` | verified | 10500 |
| 236 | outcomes | On train the slice holds 0.5 with n of 10500 , an event rate… | 0.255 | ratio | event_rate | train | eq | `[[art:b4c36e0f:metrics.train.sub.utilisation_high.event_rate]]` | verified | 0.254952381 |
| 237 | outcomes | On train the slice holds 0.5 with n of 10500 , an event rate… | 0.2577 | ratio | mean_predicted | train | eq | `[[art:ef3c0e39:metrics.train.sub.utilisation_high.mean_predicted]]` | verified | 0.2576557643 |
| 238 | outcomes | On train the slice holds 0.5 with n of 10500 , an event rate… | 0.7819 | ratio | auc | train | eq | `[[art:fc9a70a0:metrics.train.sub.utilisation_high.auc]]` | verified | 0.7818767691 |
| 239 | outcomes | On train the slice holds 0.5 with n of 10500 , an event rate… | 0.5638 | ratio | gini | train | eq | `[[art:02cc4283:metrics.train.sub.utilisation_high.gini]]` | verified | 0.5637535383 |
| 240 | outcomes | On train the slice holds 0.5 with n of 10500 , an event rate… | 0.4801 | ratio | ks | train | eq | `[[art:7bdb48f3:metrics.train.sub.utilisation_high.ks]]` | verified | 0.4801287316 |
| 241 | outcomes | On train the slice holds 0.5 with n of 10500 , an event rate… | 0.1455 | ratio | brier | train | eq | `[[art:2e9ceb3c:metrics.train.sub.utilisation_high.brier]]` | verified | 0.1455417851 |
| 242 | outcomes | On train the slice holds 0.5 with n of 10500 , an event rate… | 0.4626 | ratio | logloss | train | eq | `[[art:33a65c49:metrics.train.sub.utilisation_high.logloss]]` | verified | 0.4625503637 |
| 243 | outcomes | The slice AUC falls below its split's by -0.02309 on test an… | -0.02309 | ratio | auc_gap | test | eq | `[[art:7132f197:metrics.test.sub.utilisation_high.auc_gap]]` | verified | -0.02309035011 |
| 244 | outcomes | The slice AUC falls below its split's by -0.02309 on test an… | -0.02732 | ratio | auc_gap | train | eq | `[[art:41fca294:metrics.train.sub.utilisation_high.auc_gap]]` | verified | -0.02732151154 |
| 245 | sensitivity | The largest variance inflation factor across the retained fe… | 3.544 | ratio | vif |  | eq | `[[art:d3785ba9:vif.max]]` | verified | 3.54357449 |
| 246 | sensitivity | The largest variance inflation factor across the retained fe… | 10 | ratio | vif |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 247 | sensitivity | That maximum is attained by delinq_count_6m, whose variance… | 3.544 | ratio | vif | train | eq | `[[art:7273e0be:vif.delinq_count_6m]]` | verified | 3.54357449 |
| 248 | sensitivity | That maximum is attained by delinq_count_6m, whose variance… | 3.484 | ratio | vif |  | eq | `[[art:e7b701a1:vif.delinq_max_6m]]` | verified | 3.483514414 |
| 249 | sensitivity | That maximum is attained by delinq_count_6m, whose variance… | 3.027 | ratio | vif |  | eq | `[[art:2cda5cfc:vif.pay_ratio_mean_6m]]` | verified | 3.026650797 |
| 250 | sensitivity | The next group comprises utilisation at 2.829 , pay_ratio_la… | 2.829 | ratio | vif |  | eq | `[[art:6ce4c102:vif.utilisation]]` | verified | 2.829009901 |
| 251 | sensitivity | The next group comprises utilisation at 2.829 , pay_ratio_la… | 2.714 | ratio | vif |  | eq | `[[art:b68613a6:vif.pay_ratio_last]]` | verified | 2.713577274 |
| 252 | sensitivity | The next group comprises utilisation at 2.829 , pay_ratio_la… | 2.321 | ratio | vif |  | eq | `[[art:59461811:vif.delinq_last]]` | verified | 2.320694749 |
| 253 | sensitivity | The next group comprises utilisation at 2.829 , pay_ratio_la… | 2.265 | ratio | vif |  | eq | `[[art:87cb4e54:vif.bill_mean_6m]]` | verified | 2.264665681 |
| 254 | sensitivity | The least inflated features are limit_bal at 2.097 , bill_tr… | 2.097 | ratio | vif |  | eq | `[[art:0c6efb3f:vif.limit_bal]]` | verified | 2.096817173 |
| 255 | sensitivity | The least inflated features are limit_bal at 2.097 , bill_tr… | 1.33 | ratio | vif |  | eq | `[[art:6d3f01ce:vif.bill_trend_6m]]` | verified | 1.330477005 |
| 256 | sensitivity | The least inflated features are limit_bal at 2.097 , bill_tr… | 1.025 | ratio | vif |  | eq | `[[art:692cd6e9:vif.age]]` | verified | 1.024899403 |
| 257 | sensitivity | Belsley's condition number of the column-standardised design… | 4.279 | ratio | condition_number |  | eq | `[[art:ba0d9cc4:condition_number]]` | verified | 4.279282985 |
| 258 | sensitivity | Belsley's condition number of the column-standardised design… | 30 | ratio | condition_number |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 259 | findings | On the never-delinquent segment (delinq_last equal to zero),… | 0.6312 | ratio | auc | test | eq | `[[art:1b96a24d:metrics.test.sub.delinq_last_eq_0.auc]]` | verified | 0.6311898521 |
| 260 | findings | On the never-delinquent segment (delinq_last equal to zero),… | 0.1238 | ratio | auc_gap | test | eq | `[[art:90bff412:metrics.test.sub.delinq_last_eq_0.auc_gap]]` | verified | 0.1238340932 |
| 261 | findings | On the never-delinquent segment (delinq_last equal to zero),… | 0.6205 | ratio | auc | train | eq | `[[art:f1c7d62f:metrics.train.sub.delinq_last_eq_0.auc]]` | verified | 0.6205034872 |
| 262 | findings | On the never-delinquent segment (delinq_last equal to zero),… | 0.1341 | ratio | auc_gap | train | eq | `[[art:9bd52249:metrics.train.sub.delinq_last_eq_0.auc_gap]]` | verified | 0.1340517703 |
| 263 | findings | On the never-delinquent segment (delinq_last equal to zero),… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 264 | findings | On the never-delinquent segment (delinq_last equal to zero),… | 0.775 | ratio | share | test | eq | `[[art:2caf0a26:metrics.test.sub.delinq_last_eq_0.share]]` | verified | 0.775 |
| 265 | findings | On the never-delinquent segment (delinq_last equal to zero),… | 0.7718 | ratio | share | train | eq | `[[art:39ead1e5:metrics.train.sub.delinq_last_eq_0.share]]` | verified | 0.7717619048 |
| 266 | findings | On the never-delinquent segment (delinq_last equal to zero),… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 267 | findings | On the recently-delinquent segment (delinq_last equal to one… | 0.6513 | ratio | auc | test | eq | `[[art:1d01d834:metrics.test.sub.delinq_last_eq_1.auc]]` | verified | 0.6513372215 |
| 268 | findings | On the recently-delinquent segment (delinq_last equal to one… | 0.1037 | ratio | auc_gap | test | eq | `[[art:7e196964:metrics.test.sub.delinq_last_eq_1.auc_gap]]` | verified | 0.1036867238 |
| 269 | findings | On the recently-delinquent segment (delinq_last equal to one… | 0.6441 | ratio | auc | train | eq | `[[art:5a17ab4a:metrics.train.sub.delinq_last_eq_1.auc]]` | verified | 0.6441484398 |
| 270 | findings | On the recently-delinquent segment (delinq_last equal to one… | 0.1104 | ratio | auc_gap | train | eq | `[[art:d6cf38ec:metrics.train.sub.delinq_last_eq_1.auc_gap]]` | verified | 0.1104068178 |
| 271 | findings | On the recently-delinquent segment (delinq_last equal to one… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 272 | findings | On the recently-delinquent segment (delinq_last equal to one… | 0.1218 | ratio | share | test | eq | `[[art:ba192c04:metrics.test.sub.delinq_last_eq_1.share]]` | verified | 0.1217777778 |
| 273 | findings | On the recently-delinquent segment (delinq_last equal to one… | 0.1234 | ratio | share | train | eq | `[[art:3b48f1bc:metrics.train.sub.delinq_last_eq_1.share]]` | verified | 0.1234285714 |
| 274 | findings | On the recently-delinquent segment (delinq_last equal to one… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 275 | monitoring | - Discrimination: recompute AUC on each outcome-complete mon… | 0.7 | ratio | auc | test | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 276 | monitoring | - Discrimination: recompute AUC on each outcome-complete mon… | 0.755 | ratio | auc | test | eq | `[[art:365b7034:metrics.test.auc]]` | verified | 0.7550239453 |
| 277 | monitoring | - Accuracy: recompute the Brier score on the same cohorts ag… | 0.2 | ratio | brier | test | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 278 | monitoring | - Accuracy: recompute the Brier score on the same cohorts ag… | 0.1385 | ratio | brier | test | eq | `[[art:86e93c8f:metrics.test.brier]]` | verified | 0.1385162411 |
| 279 | monitoring | - Calibration: refit the logistic regression of the outcome… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 280 | monitoring | - Calibration: refit the logistic regression of the outcome… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 281 | monitoring | - Calibration: refit the logistic regression of the outcome… | 0.9886 | ratio | calibration_slope | test | eq | `[[art:e06564c7:calibration_slope.test]]` | verified | 0.9885680158 |
| 282 | monitoring | - Population stability: recompute the maximum PSI, score inc… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 283 | monitoring | - Population stability: recompute the maximum PSI, score inc… | 0.003083 | ratio | psi |  | eq | `[[art:e1d82330:psi.max]]` | verified | 0.00308251646 |
| 284 | monitoring | The performance section of this report presented discriminat… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 285 | monitoring | For a future monitoring cohort whose observed event rate fal… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |

## Appendix B — Artifact index

The store holds 250 artifacts; the 209 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `ablation.age.delta_auc` | `f6fdd709` | scalar | -0.002224986043 | change in test AUC when the champion's form is refitted without age |
| `ablation.baseline_auc` | `789072f8` | scalar | 0.7550239453 | AUC on test of a refit of the champion's functional form on every retained feature, the level each ablation delta is measured from |
| `ablation.bill_mean_6m.delta_auc` | `5b4423ab` | scalar | -0.00015270601 | change in test AUC when the champion's form is refitted without bill_mean_6m |
| `ablation.bill_trend_6m.delta_auc` | `99f9dd71` | scalar | -0.001392555557 | change in test AUC when the champion's form is refitted without bill_trend_6m |
| `ablation.delinq_count_6m.delta_auc` | `db90576e` | scalar | -0.002145551687 | change in test AUC when the champion's form is refitted without delinq_count_6m |
| `ablation.delinq_last.delta_auc` | `40f4e6bf` | scalar | -0.005913828665 | change in test AUC when the champion's form is refitted without delinq_last |
| `ablation.delinq_max_6m.delta_auc` | `18cb1559` | scalar | -0.001133363798 | change in test AUC when the champion's form is refitted without delinq_max_6m |
| `ablation.limit_bal.delta_auc` | `57710b23` | scalar | -0.003748140709 | change in test AUC when the champion's form is refitted without limit_bal |
| `ablation.pay_ratio_last.delta_auc` | `e26d8112` | scalar | -5.589426925e-05 | change in test AUC when the champion's form is refitted without pay_ratio_last |
| `ablation.pay_ratio_mean_6m.delta_auc` | `cba98844` | scalar | -0.0009815893593 | change in test AUC when the champion's form is refitted without pay_ratio_mean_6m |
| `ablation.utilisation.delta_auc` | `dc9ac505` | scalar | 1.920469764e-05 | change in test AUC when the champion's form is refitted without utilisation |
| `calibration.mean_rel_gap.test` | `bae28fd6` | scalar | 0.00294357342 | mean predicted against observed on test, relative |
| `calibration.mean_rel_gap.train` | `a03ea014` | scalar | 0.0001554936592 | mean predicted against observed on train, relative |
| `calibration.test` | `d19b8ac3` | table | table, 10 rows | calibration by decile of predicted probability on test |
| `calibration_intercept.test` | `2ee976d3` | scalar | -0.008632158167 | logistic regression of the outcome on logit(p) on test: the intercept |
| `calibration_intercept.train` | `2ce8cd09` | scalar | 0.0003779479547 | logistic regression of the outcome on logit(p) on train: the intercept |
| `calibration_slope.test` | `e06564c7` | scalar | 0.9885680158 | logistic regression of the outcome on logit(p) on test: the slope |
| `calibration_slope.train` | `85461245` | scalar | 1.000539237 | logistic regression of the outcome on logit(p) on train: the slope |
| `challenger.auc` | `5646e7f3` | scalar | 0.7789298885 | the challenger's AUC on test |
| `challenger.brier` | `2031a154` | scalar | 0.1349523392 | the challenger's Brier score on test |
| `challenger.delta_auc` | `3877bdd0` | scalar | 0.02390594313 | the challenger's AUC on test minus the champion's |
| `condition_number` | `ba0d9cc4` | scalar | 4.279282985 | Belsley's condition number of the column-standardised design (D-035) |
| `csi.age` | `25b88f37` | scalar | 0.001203264027 | CSI of age: its contribution to the shift in the linear predictor |
| `csi.bill_mean_6m` | `0c34001d` | scalar | 9.982086887e-06 | CSI of bill_mean_6m: its contribution to the shift in the linear predictor |
| `csi.bill_trend_6m` | `9e5a9b68` | scalar | 0.0003674527783 | CSI of bill_trend_6m: its contribution to the shift in the linear predictor |
| `csi.delinq_count_6m` | `f0438233` | scalar | 0.0008781439663 | CSI of delinq_count_6m: its contribution to the shift in the linear predictor |
| `csi.delinq_last` | `e755cf0a` | scalar | 0.001697603731 | CSI of delinq_last: its contribution to the shift in the linear predictor |
| `csi.delinq_max_6m` | `35990a39` | scalar | 0.00473710965 | CSI of delinq_max_6m: its contribution to the shift in the linear predictor |
| `csi.limit_bal` | `c91a2a4b` | scalar | 0.001384099928 | CSI of limit_bal: its contribution to the shift in the linear predictor |
| `csi.max` | `ce1257d8` | scalar | 0.00473710965 | the largest characteristic stability index |
| `csi.pay_ratio_last` | `5898a9c5` | scalar | 0.0001131831266 | CSI of pay_ratio_last: its contribution to the shift in the linear predictor |
| `csi.pay_ratio_mean_6m` | `5e53c153` | scalar | 0.002042601165 | CSI of pay_ratio_mean_6m: its contribution to the shift in the linear predictor |
| `csi.utilisation` | `6ed37e42` | scalar | 0.0002135922405 | CSI of utilisation: its contribution to the shift in the linear predictor |
| `deciles.test` | `4396db6f` | table | table, 10 rows | decile separation on test; decile 1 holds the highest probabilities |
| `deciles.test.top2_capture` | `e2c0ad9f` | scalar | 0.4952285284 | share of test events in the top two deciles |
| `deciles.train.top2_capture` | `5131afa7` | scalar | 0.5031216362 | share of train events in the top two deciles |
| `leakage.duplicates.train` | `c988bb0e` | scalar | 0.01161904762 | share of train rows whose feature values are not unique within train |
| `leakage.name_screen.n_matched` | `407e62be` | scalar | 0 | feature names matching the target-adjacent lexicon |
| `leakage.overlap` | `ebd7ff30` | scalar | 0.01255555556 | share of test rows whose feature values also appear in train |
| `leakage.overlap.features` | `517f3049` | scalar | 0.01255555556 | share of test rows whose feature values also appear in train |
| `leakage.overlap.ids` | `63d37fc5` | scalar | 0 | share of test rows whose ['client_id'] also identify a row of train |
| `leakage.target_corr.max_single_feature_auc` | `2e212f3a` | scalar | 0.7279795601 | the AUC of the strongest single feature |
| `leakage.timing.n_flagged` | `742bcd24` | scalar | 0 | features declared during_period or after_outcome |
| `metrics.test.auc` | `365b7034` | scalar | 0.7550239453 | auc on test, recomputed by quaestor |
| `metrics.test.brier` | `86e93c8f` | scalar | 0.1385162411 | brier on test, recomputed by quaestor |
| `metrics.test.event_rate` | `f60ae2a7` | scalar | 0.2212222222 | event_rate on test, recomputed by quaestor |
| `metrics.test.gini` | `296bfeeb` | scalar | 0.5100478906 | gini on test, recomputed by quaestor |
| `metrics.test.ks` | `d3c4ed61` | scalar | 0.4066831201 | ks on test, recomputed by quaestor |
| `metrics.test.logloss` | `2de58c1b` | scalar | 0.4441654047 | logloss on test, recomputed by quaestor |
| `metrics.test.mean_predicted` | `89d241ea` | scalar | 0.2205710384 | mean_predicted on test, recomputed by quaestor |
| `metrics.test.n` | `5367a59f` | scalar | 9000 | n on test, recomputed by quaestor |
| `metrics.test.sub.delinq_last_eq_0.auc` | `1b96a24d` | scalar | 0.6311898521 | auc on the delinq_last equals:0 slice of test |
| `metrics.test.sub.delinq_last_eq_0.auc_gap` | `90bff412` | scalar | 0.1238340932 | how far AUC on the delinq_last equals:0 slice of test falls below AUC on all of test |
| `metrics.test.sub.delinq_last_eq_0.brier` | `2bce5eb5` | scalar | 0.1168254801 | brier on the delinq_last equals:0 slice of test |
| `metrics.test.sub.delinq_last_eq_0.event_rate` | `46acca95` | scalar | 0.1405017921 | event_rate on the delinq_last equals:0 slice of test |
| `metrics.test.sub.delinq_last_eq_0.gini` | `1183089b` | scalar | 0.2623797042 | gini on the delinq_last equals:0 slice of test |
| `metrics.test.sub.delinq_last_eq_0.ks` | `4d6488ce` | scalar | 0.2105487566 | ks on the delinq_last equals:0 slice of test |
| `metrics.test.sub.delinq_last_eq_0.logloss` | `26913d06` | scalar | 0.391800392 | logloss on the delinq_last equals:0 slice of test |
| `metrics.test.sub.delinq_last_eq_0.mean_predicted` | `3d1e089a` | scalar | 0.137076189 | mean_predicted on the delinq_last equals:0 slice of test |
| `metrics.test.sub.delinq_last_eq_0.n` | `cd0a7adb` | scalar | 6975 | n on the delinq_last equals:0 slice of test |
| `metrics.test.sub.delinq_last_eq_0.share` | `2caf0a26` | scalar | 0.775 | the share of test the delinq_last equals:0 slice holds |
| `metrics.test.sub.delinq_last_eq_1.auc` | `1d01d834` | scalar | 0.6513372215 | auc on the delinq_last equals:1 slice of test |
| `metrics.test.sub.delinq_last_eq_1.auc_gap` | `7e196964` | scalar | 0.1036867238 | how far AUC on the delinq_last equals:1 slice of test falls below AUC on all of test |
| `metrics.test.sub.delinq_last_eq_1.brier` | `82c35e29` | scalar | 0.2104514634 | brier on the delinq_last equals:1 slice of test |
| `metrics.test.sub.delinq_last_eq_1.event_rate` | `3d353862` | scalar | 0.3321167883 | event_rate on the delinq_last equals:1 slice of test |
| `metrics.test.sub.delinq_last_eq_1.gini` | `aeb8f8a5` | scalar | 0.302674443 | gini on the delinq_last equals:1 slice of test |
| `metrics.test.sub.delinq_last_eq_1.ks` | `343e93a8` | scalar | 0.2587071399 | ks on the delinq_last equals:1 slice of test |
| `metrics.test.sub.delinq_last_eq_1.logloss` | `089e61ce` | scalar | 0.6102554962 | logloss on the delinq_last equals:1 slice of test |
| `metrics.test.sub.delinq_last_eq_1.mean_predicted` | `6411ed69` | scalar | 0.3858491811 | mean_predicted on the delinq_last equals:1 slice of test |
| `metrics.test.sub.delinq_last_eq_1.n` | `664c19bf` | scalar | 1096 | n on the delinq_last equals:1 slice of test |
| `metrics.test.sub.delinq_last_eq_1.share` | `ba192c04` | scalar | 0.1217777778 | the share of test the delinq_last equals:1 slice holds |
| `metrics.test.sub.limit_bal_low.auc` | `26da9c77` | scalar | 0.7477379077 | auc on the limit_bal below_median slice of test |
| `metrics.test.sub.limit_bal_low.auc_gap` | `15e1edcb` | scalar | 0.007286037626 | how far AUC on the limit_bal below_median slice of test falls below AUC on all of test |
| `metrics.test.sub.limit_bal_low.brier` | `68867046` | scalar | 0.1674846594 | brier on the limit_bal below_median slice of test |
| `metrics.test.sub.limit_bal_low.event_rate` | `9629805c` | scalar | 0.2877024869 | event_rate on the limit_bal below_median slice of test |
| `metrics.test.sub.limit_bal_low.gini` | `1d9599c6` | scalar | 0.4954758154 | gini on the limit_bal below_median slice of test |
| `metrics.test.sub.limit_bal_low.ks` | `39f5214d` | scalar | 0.4047386204 | ks on the limit_bal below_median slice of test |
| `metrics.test.sub.limit_bal_low.logloss` | `194532b1` | scalar | 0.5164924891 | logloss on the limit_bal below_median slice of test |
| `metrics.test.sub.limit_bal_low.mean_predicted` | `e3d342d5` | scalar | 0.2801722167 | mean_predicted on the limit_bal below_median slice of test |
| `metrics.test.sub.limit_bal_low.n` | `686cad5e` | scalar | 4383 | n on the limit_bal below_median slice of test |
| `metrics.test.sub.limit_bal_low.share` | `e7847e2b` | scalar | 0.487 | the share of test the limit_bal below_median slice holds |
| `metrics.test.sub.utilisation_high.auc` | `7a00057d` | scalar | 0.7781142954 | auc on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.auc_gap` | `7132f197` | scalar | -0.02309035011 | how far AUC on the utilisation above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.utilisation_high.brier` | `80c11b34` | scalar | 0.1491771843 | brier on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.event_rate` | `e4a00a59` | scalar | 0.2657777778 | event_rate on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.gini` | `0500c179` | scalar | 0.5562285909 | gini on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.ks` | `096c8d60` | scalar | 0.4738747803 | ks on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.logloss` | `24970875` | scalar | 0.4716985136 | logloss on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.mean_predicted` | `e68f1a3d` | scalar | 0.2608314072 | mean_predicted on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.n` | `ee72f76a` | scalar | 4500 | n on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.share` | `9404484e` | scalar | 0.5 | the share of test the utilisation above_median slice holds |
| `metrics.train.auc` | `01cf8178` | scalar | 0.7545552576 | auc on train, recomputed by quaestor |
| `metrics.train.brier` | `c95106e9` | scalar | 0.1383762773 | brier on train, recomputed by quaestor |
| `metrics.train.event_rate` | `657aa7fc` | scalar | 0.2211904762 | event_rate on train, recomputed by quaestor |
| `metrics.train.gini` | `eaaf0f79` | scalar | 0.5091105152 | gini on train, recomputed by quaestor |
| `metrics.train.ks` | `18df22bd` | scalar | 0.4144375385 | ks on train, recomputed by quaestor |
| `metrics.train.logloss` | `b816b083` | scalar | 0.4439401117 | logloss on train, recomputed by quaestor |
| `metrics.train.mean_predicted` | `935d2cb7` | scalar | 0.2212248699 | mean_predicted on train, recomputed by quaestor |
| `metrics.train.n` | `1721ceae` | scalar | 21000 | n on train, recomputed by quaestor |
| `metrics.train.sub.delinq_last_eq_0.auc` | `f1c7d62f` | scalar | 0.6205034872 | auc on the delinq_last equals:0 slice of train |
| `metrics.train.sub.delinq_last_eq_0.auc_gap` | `9bd52249` | scalar | 0.1340517703 | how far AUC on the delinq_last equals:0 slice of train falls below AUC on all of train |
| `metrics.train.sub.delinq_last_eq_0.brier` | `8583b4e5` | scalar | 0.1146044072 | brier on the delinq_last equals:0 slice of train |
| `metrics.train.sub.delinq_last_eq_0.event_rate` | `b158c0fb` | scalar | 0.1374097612 | event_rate on the delinq_last equals:0 slice of train |
| `metrics.train.sub.delinq_last_eq_0.gini` | `43a02d18` | scalar | 0.2410069745 | gini on the delinq_last equals:0 slice of train |
| `metrics.train.sub.delinq_last_eq_0.ks` | `792e2044` | scalar | 0.176800619 | ks on the delinq_last equals:0 slice of train |
| `metrics.train.sub.delinq_last_eq_0.logloss` | `cd7b90e8` | scalar | 0.38638584 | logloss on the delinq_last equals:0 slice of train |
| `metrics.train.sub.delinq_last_eq_0.mean_predicted` | `121d5b67` | scalar | 0.1380373247 | mean_predicted on the delinq_last equals:0 slice of train |
| `metrics.train.sub.delinq_last_eq_0.share` | `39ead1e5` | scalar | 0.7717619048 | the share of train the delinq_last equals:0 slice holds |
| `metrics.train.sub.delinq_last_eq_1.auc` | `5a17ab4a` | scalar | 0.6441484398 | auc on the delinq_last equals:1 slice of train |
| `metrics.train.sub.delinq_last_eq_1.auc_gap` | `d6cf38ec` | scalar | 0.1104068178 | how far AUC on the delinq_last equals:1 slice of train falls below AUC on all of train |
| `metrics.train.sub.delinq_last_eq_1.brier` | `b31f006a` | scalar | 0.2139999197 | brier on the delinq_last equals:1 slice of train |
| `metrics.train.sub.delinq_last_eq_1.event_rate` | `d1e0caab` | scalar | 0.3425925926 | event_rate on the delinq_last equals:1 slice of train |
| `metrics.train.sub.delinq_last_eq_1.gini` | `539c7e22` | scalar | 0.2882968796 | gini on the delinq_last equals:1 slice of train |
| `metrics.train.sub.delinq_last_eq_1.ks` | `4c6c5159` | scalar | 0.2313951275 | ks on the delinq_last equals:1 slice of train |
| `metrics.train.sub.delinq_last_eq_1.logloss` | `1f5cba97` | scalar | 0.6178764991 | logloss on the delinq_last equals:1 slice of train |
| `metrics.train.sub.delinq_last_eq_1.mean_predicted` | `90c4acea` | scalar | 0.3841118294 | mean_predicted on the delinq_last equals:1 slice of train |
| `metrics.train.sub.delinq_last_eq_1.n` | `7dfec1a7` | scalar | 2592 | n on the delinq_last equals:1 slice of train |
| `metrics.train.sub.delinq_last_eq_1.share` | `3b48f1bc` | scalar | 0.1234285714 | the share of train the delinq_last equals:1 slice holds |
| `metrics.train.sub.limit_bal_low.auc` | `d3864be2` | scalar | 0.755664374 | auc on the limit_bal below_median slice of train |
| `metrics.train.sub.limit_bal_low.auc_gap` | `021950a5` | scalar | -0.001109116413 | how far AUC on the limit_bal below_median slice of train falls below AUC on all of train |
| `metrics.train.sub.limit_bal_low.brier` | `58d900b3` | scalar | 0.1623351934 | brier on the limit_bal below_median slice of train |
| `metrics.train.sub.limit_bal_low.event_rate` | `815577c8` | scalar | 0.2846032684 | event_rate on the limit_bal below_median slice of train |
| `metrics.train.sub.limit_bal_low.gini` | `efffd200` | scalar | 0.511328748 | gini on the limit_bal below_median slice of train |
| `metrics.train.sub.limit_bal_low.ks` | `a95d8865` | scalar | 0.4304590098 | ks on the limit_bal below_median slice of train |
| `metrics.train.sub.limit_bal_low.logloss` | `c0e7dc4c` | scalar | 0.5041966841 | logloss on the limit_bal below_median slice of train |
| `metrics.train.sub.limit_bal_low.mean_predicted` | `03370fd4` | scalar | 0.2820440763 | mean_predicted on the limit_bal below_median slice of train |
| `metrics.train.sub.limit_bal_low.share` | `d4eb837c` | scalar | 0.4837142857 | the share of train the limit_bal below_median slice holds |
| `metrics.train.sub.utilisation_high.auc` | `fc9a70a0` | scalar | 0.7818767691 | auc on the utilisation above_median slice of train |
| `metrics.train.sub.utilisation_high.auc_gap` | `41fca294` | scalar | -0.02732151154 | how far AUC on the utilisation above_median slice of train falls below AUC on all of train |
| `metrics.train.sub.utilisation_high.brier` | `2e9ceb3c` | scalar | 0.1455417851 | brier on the utilisation above_median slice of train |
| `metrics.train.sub.utilisation_high.event_rate` | `b4c36e0f` | scalar | 0.254952381 | event_rate on the utilisation above_median slice of train |
| `metrics.train.sub.utilisation_high.gini` | `02cc4283` | scalar | 0.5637535383 | gini on the utilisation above_median slice of train |
| `metrics.train.sub.utilisation_high.ks` | `7bdb48f3` | scalar | 0.4801287316 | ks on the utilisation above_median slice of train |
| `metrics.train.sub.utilisation_high.logloss` | `33a65c49` | scalar | 0.4625503637 | logloss on the utilisation above_median slice of train |
| `metrics.train.sub.utilisation_high.mean_predicted` | `ef3c0e39` | scalar | 0.2576557643 | mean_predicted on the utilisation above_median slice of train |
| `metrics.train.sub.utilisation_high.n` | `fe8f2ffa` | scalar | 10500 | n on the utilisation above_median slice of train |
| `metrics.train.sub.utilisation_high.share` | `0ff76e00` | scalar | 0.5 | the share of train the utilisation above_median slice holds |
| `profile.test.missing.max` | `f813848d` | scalar | 0 | the largest missing fraction in test |
| `profile.test.n` | `abbe1a27` | scalar | 9000 | rows in test |
| `profile.train.missing.max` | `050a3099` | scalar | 0 | the largest missing fraction in train |
| `profile.train.n` | `a359de9d` | scalar | 21000 | rows in train |
| `psi.age` | `06c22a63` | scalar | 0.00308251646 | PSI of age between train and test |
| `psi.bill_mean_6m` | `127cdf82` | scalar | 0.001488231386 | PSI of bill_mean_6m between train and test |
| `psi.bill_trend_6m` | `78be70d2` | scalar | 0.0007484247754 | PSI of bill_trend_6m between train and test |
| `psi.delinq_count_6m` | `d77ddb1d` | scalar | 0.00185562271 | PSI of delinq_count_6m between train and test |
| `psi.delinq_last` | `cbc9de36` | scalar | 0.0002346592849 | PSI of delinq_last between train and test |
| `psi.delinq_max_6m` | `4b0a94ab` | scalar | 0.001026806992 | PSI of delinq_max_6m between train and test |
| `psi.limit_bal` | `b0195847` | scalar | 0.001272099805 | PSI of limit_bal between train and test |
| `psi.max` | `e1d82330` | scalar | 0.00308251646 | the largest train-to-test PSI, score included |
| `psi.pay_ratio_last` | `82c97112` | scalar | 0.0022643364 | PSI of pay_ratio_last between train and test |
| `psi.pay_ratio_mean_6m` | `62e0e0f8` | scalar | 0.001027537662 | PSI of pay_ratio_mean_6m between train and test |
| `psi.utilisation` | `f094559b` | scalar | 0.0006522718782 | PSI of utilisation between train and test |
| `psi.y_score` | `ec2b8d1b` | scalar | 0.001367653962 | PSI of the score between train and test |
| `rule.calibration_first_event_rate` | `42f1351e` | scalar | 0.05 | the event rate below which the report puts calibration before discrimination |
| `run.features` | `792cb79c` | json | json | the subject's features.json |
| `run.model_summary` | `ca1c764c` | json | json | the subject's model_summary.json |
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |
| `sign_check.age.agrees` | `4116add1` | scalar | 1 | 1 when the fitted sign on age agrees with its univariate direction, 0 when it does not |
| `sign_check.bill_mean_6m.agrees` | `89279c3b` | scalar | 1 | 1 when the fitted sign on bill_mean_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.bill_trend_6m.agrees` | `c0f6d07d` | scalar | 0 | 1 when the fitted sign on bill_trend_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.bill_trend_6m.coef_sign` | `abd4aaba` | scalar | 1 | the sign of the fitted coefficient on bill_trend_6m |
| `sign_check.bill_trend_6m.univariate_direction` | `a9bff389` | scalar | -1 | the sign of bill_trend_6m's own single-feature AUC on train minus 0.5 |
| `sign_check.delinq_count_6m.agrees` | `a337d16b` | scalar | 1 | 1 when the fitted sign on delinq_count_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.delinq_last.agrees` | `a8ba9372` | scalar | 1 | 1 when the fitted sign on delinq_last agrees with its univariate direction, 0 when it does not |
| `sign_check.delinq_last.coef_sign` | `50d352f8` | scalar | 1 | the sign of the fitted coefficient on delinq_last |
| `sign_check.delinq_last.univariate_direction` | `a78648ba` | scalar | 1 | the sign of delinq_last's own single-feature AUC on train minus 0.5 |
| `sign_check.delinq_max_6m.agrees` | `da92a015` | scalar | 1 | 1 when the fitted sign on delinq_max_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.limit_bal.agrees` | `103d99fb` | scalar | 1 | 1 when the fitted sign on limit_bal agrees with its univariate direction, 0 when it does not |
| `sign_check.limit_bal.coef_sign` | `a6d01381` | scalar | -1 | the sign of the fitted coefficient on limit_bal |
| `sign_check.limit_bal.univariate_direction` | `56d284d6` | scalar | -1 | the sign of limit_bal's own single-feature AUC on train minus 0.5 |
| `sign_check.n_disagreements` | `e223cd4a` | scalar | 3 | retained features whose fitted sign contradicts their univariate direction, of 10 checked |
| `sign_check.pay_ratio_last.agrees` | `79abee77` | scalar | 0 | 1 when the fitted sign on pay_ratio_last agrees with its univariate direction, 0 when it does not |
| `sign_check.pay_ratio_last.coef_sign` | `f018263e` | scalar | 1 | the sign of the fitted coefficient on pay_ratio_last |
| `sign_check.pay_ratio_last.univariate_direction` | `f8e46d75` | scalar | -1 | the sign of pay_ratio_last's own single-feature AUC on train minus 0.5 |
| `sign_check.pay_ratio_mean_6m.agrees` | `7e9a76ca` | scalar | 1 | 1 when the fitted sign on pay_ratio_mean_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.utilisation.agrees` | `cb5a7bc7` | scalar | 0 | 1 when the fitted sign on utilisation agrees with its univariate direction, 0 when it does not |
| `sign_check.utilisation.coef_sign` | `46230409` | scalar | -1 | the sign of the fitted coefficient on utilisation |
| `sign_check.utilisation.univariate_direction` | `f0995196` | scalar | 1 | the sign of utilisation's own single-feature AUC on train minus 0.5 |
| `threshold.C1.calibration_slope.max` | `b6672579` | scalar | 1.2 | C1: the top of the calibration slope band |
| `threshold.C1.calibration_slope.min` | `749634ae` | scalar | 0.8 | C1: the bottom of the calibration slope band |
| `threshold.C1.mean_ratio_rel` | `20e93a8c` | scalar | 0.25 | C1: mean predicted against observed, relative |
| `threshold.D1.missing_gap` | `9cce25ea` | scalar | 0.1 | D1: the missingness gap between splits, as a fraction |
| `threshold.E1.delta_auc` | `e042774c` | scalar | 0.03 | E1: the challenger's AUC lead over the champion |
| `threshold.L1.single_feature_auc` | `c29e7a34` | scalar | 0.9 | L1: the AUC one feature may reach on its own |
| `threshold.L2.overlap` | `9f336eaf` | scalar | 0.005 | L2: the fraction of test rows that may also be in train |
| `threshold.L2.overlap.features_effective` | `7cdc63cb` | scalar | 0.02323809524 | L2: the bound the feature-overlap rule applied, the larger of threshold.L2.overlap and 2 x leakage.duplicates.train |
| `threshold.M1.condition_number` | `7e52fd7a` | scalar | 30 | M1: Belsley's condition number of the design (D-035) |
| `threshold.M1.vif` | `aeb4f33c` | scalar | 10 | M1: the variance inflation factor of any retained feature |
| `threshold.O1.auc_gap` | `630f28f4` | scalar | 0.08 | O1: the train-to-test AUC gap (D-050) |
| `threshold.O1.slice_auc_gap` | `0a827b87` | scalar | 0.08 | how far a sub-population's AUC may fall below the split's before the result is an open item (D-102); it raises no candidate |
| `threshold.O1.slice_min_share` | `9a6f1a87` | scalar | 0.1 | the share of a split a sub-population must hold before it can raise an open item (D-102) |
| `threshold.S1.psi` | `278b9016` | scalar | 0.25 | S1: the population stability index, train against test (D-046) |
| `threshold.package.auc.test.min` | `8bfd02cc` | scalar | 0.7 | package.yaml declares auc min 0.7 |
| `threshold.package.brier.test.max` | `d0f98b9c` | scalar | 0.2 | package.yaml declares brier max 0.2 |
| `threshold.package.calibration_slope.test.max` | `0adb7a89` | scalar | 1.2 | package.yaml declares calibration_slope max 1.2 |
| `threshold.package.calibration_slope.test.min` | `95fdb848` | scalar | 0.8 | package.yaml declares calibration_slope min 0.8 |
| `threshold.package.psi.max` | `fbb5a9d1` | scalar | 0.25 | package.yaml declares psi max 0.25 |
| `thresholds.evaluation` | `5c58fa84` | table | table, 5 rows | every threshold package.yaml declares, with its bound, the recomputed value and the outcome |
| `vif.age` | `692cd6e9` | scalar | 1.024899403 | variance inflation factor of age on train |
| `vif.bill_mean_6m` | `87cb4e54` | scalar | 2.264665681 | variance inflation factor of bill_mean_6m on train |
| `vif.bill_trend_6m` | `6d3f01ce` | scalar | 1.330477005 | variance inflation factor of bill_trend_6m on train |
| `vif.delinq_count_6m` | `7273e0be` | scalar | 3.54357449 | variance inflation factor of delinq_count_6m on train |
| `vif.delinq_last` | `59461811` | scalar | 2.320694749 | variance inflation factor of delinq_last on train |
| `vif.delinq_max_6m` | `e7b701a1` | scalar | 3.483514414 | variance inflation factor of delinq_max_6m on train |
| `vif.limit_bal` | `0c6efb3f` | scalar | 2.096817173 | variance inflation factor of limit_bal on train |
| `vif.max` | `d3785ba9` | scalar | 3.54357449 | the largest variance inflation factor |
| `vif.pay_ratio_last` | `b68613a6` | scalar | 2.713577274 | variance inflation factor of pay_ratio_last on train |
| `vif.pay_ratio_mean_6m` | `2cda5cfc` | scalar | 3.026650797 | variance inflation factor of pay_ratio_mean_6m on train |
| `vif.utilisation` | `6ce4c102` | scalar | 2.829009901 | variance inflation factor of utilisation on train |

## Appendix C — Run trace summary

| quantity | value |
|---|---|
| tool calls | 17 (run_model 1, profile_data 1, compute_metrics 5, check_leakage 1, check_collinearity 1, challenger_compare 1, retrieve_guidance 7) |
| plan steps (bounded loop) | 4 |
| LLM calls | 22 (plan 4, draft 9, extract 9) |
| re-asks | 0 |
| repair rounds | 2 |
| tokens in / out | 290,392 / 123,170 |
| notional cost (USD) | 6.0535 |
| wall-clock (s) | 1328.47 |
| subject run (s) | 1.35 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | credit_default-full_agent-20260908T212049Z-d03b07c6 |

## Appendix D — Not checked

| item | reason |
|---|---|
| `check_stability` (R1) | package declares no `regime.column` |
| `run_scenarios` (X1) | not applicable to `binary_classification` |
| out-of-time and vintage-holdout metrics (O1, second rule) | package declares neither split |
| developer documentation | package has no `docs/` directory |
