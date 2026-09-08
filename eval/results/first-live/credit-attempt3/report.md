---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: full_agent
model: claude-cli
run_id: credit_default-full_agent-d03b07c6
data_mode: real
grounding_precision_pre: 0.9816
grounding_precision_post: 1.0000
n_claims: 159
n_findings_by_severity: {high: 0, medium: 0, low: 0, info: 0}
generated: "2026-09-08T06:39:34Z"
illustrative: false
---

# Validation report — `credit_default` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `credit_default` v1.0 | `full_agent` | claude-cli | real, UCI Default of Credit Card Clients (dataset id 350; CC BY 4.0; Yeh, I. (2009), doi 10.24432/C55S3H), 30,000 clients, sampled by sample.py. Synthetic mode: synthetic.py. | 0.9816 → 1.0000 | 0 / 0 / 0 / 0 |
<!-- quaestor:renderer:end -->

This report documents the independent validation of the credit_default model package, version one-point-zero, a binary classification model that predicts the probability that a borrower defaults, and it follows the structure of the Federal Reserve's model risk management guidance, in particular its expectation that outcomes analysis compare model outputs to real-world outcomes against established performance thresholds [[reg:SR26-2:V.1.b]].

The scope of the work follows the core elements of a comprehensive validation framework, namely evaluation of conceptual soundness, ongoing monitoring, and outcomes analysis, as enumerated in the superseded guidance [[reg:SR11-7:V.1]].
This report does not claim compliance with either document.

The subject was executed end to end under quaestor, and every performance figure quoted below was recomputed by quaestor from the model's own scored output rather than carried over from the developer's report.
The package declares a wall-clock cap of 300 [[art:3f4c6e97:threshold.package.max_seconds]] seconds for that run; no measured runtime is restated here.
Fitting used a train split of 21000 [[art:a359de9d:profile.train.n]] rows and evaluation used a held-out test split of 9000 [[art:abbe1a27:profile.test.n]] rows.
The outcome is balanced identically across the splits, with an event rate of 0.2212 [[art:657aa7fc:metrics.train.event_rate]] on train and 0.2212 [[art:f60ae2a7:metrics.test.event_rate]] on test.

The headline result is that the model clears each developer-declared threshold on the test split.
Test AUC is 0.755 [[art:365b7034:metrics.test.auc]] against a declared minimum of 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]].
The test Brier score is 0.1385 [[art:86e93c8f:metrics.test.brier]] against a declared maximum of 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]].
The test calibration slope is 0.9886 [[art:e06564c7:calibration_slope.test]], inside a declared band with a lower bound of 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] and an upper bound of 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The largest train-to-test population stability index, score included, is 0.003083 [[art:e1d82330:psi.max]] against a declared maximum of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].

Train-side behaviour tracks the test split closely, with a train AUC of 0.7546 [[art:01cf8178:metrics.train.auc]] and a train calibration slope of 1.001 [[art:85461245:calibration_slope.train]], so these headline measures show no material train-to-test degradation.
Supporting test-split measures from the same run are a Gini of 0.51 [[art:296bfeeb:metrics.test.gini]], a KS of 0.4067 [[art:d3c4ed61:metrics.test.ks]], a log loss of 0.4442 [[art:2de58c1b:metrics.test.logloss]], and a mean predicted probability of 0.2206 [[art:89d241ea:metrics.test.mean_predicted]] against the test event rate quoted above.
Design-matrix diagnostics give a largest variance inflation factor of 3.544 [[art:d3785ba9:vif.max]] and a Belsley condition number of 4.279 [[art:ba0d9cc4:condition_number]], and the largest characteristic stability index is 0.004737 [[art:ce1257d8:csi.max]].
A challenger benchmark scored above the champion on test, by an AUC difference of 0.02391 [[art:3877bdd0:challenger.delta_auc]], which the benchmarking discussion takes up in a later section.

No findings were raised at any severity by the checks that ran on this section's material.

## 2. Conceptual soundness

Validating conceptual soundness means assessing and documenting the model's design, construction, and developmental testing, and subjecting each modeling choice to critical analysis rather than accepting it as documented, with interpretability measures and benchmarking to other models often the more practical assessments [[reg:SR26-2:V.1.a]].

The champion in the credit_default package under review is a logistic-form scorecard with an intercept of -1.442 [[art:ca1c764c:run.model_summary#intercept]], fitted on 21000 [[art:ca1c764c:run.model_summary#n_train]] training rows.
Its design is transparent in the sense the guidance favours: each retained input enters linearly with a single reported coefficient, so the direction and relative weight of every driver can be read off the fitted summary and checked against subject-matter expectation.

The feature inventory declares 12 [[art:792cb79c:run.features#n]] inputs.
Of these, 2 [[art:792cb79c:run.features#at_origination]] are known at origination and 10 [[art:792cb79c:run.features#before_period_start]] are known before the performance period starts.
No input is drawn from within the performance period, 0 [[art:792cb79c:run.features#during_period]], and none is drawn from after the outcome is observed, 0 [[art:792cb79c:run.features#after_outcome]].
On the timing evidence alone, then, every input is available at the moment the score would be used, which is the design property that matters most for a forward-looking default model.

The developer's own collinearity screen removed two inputs against a variance-inflation threshold of 10.0 [[art:ca1c764c:run.model_summary#vif_threshold]].
The last observed bill amount was dropped at a variance inflation factor of 33.8 [[art:ca1c764c:run.model_summary#removed.bill_last.vif]], and the six-month mean utilisation was dropped at 10.96 [[art:ca1c764c:run.model_summary#removed.utilisation_mean_6m.vif]].
Both removals are consistent with the stated rule and with the redundancy one would expect among bill-level and utilisation-level aggregates computed over the same window.
The screen is a mechanical rule rather than a judgment, so the validator's question is not whether it was applied but what it did to the interpretation of the terms that survived it.

The largest coefficient is on the most recent delinquency status, 0.4847 [[art:ca1c764c:run.model_summary#coefficients.delinq_last.value]].
It is followed by the count of delinquencies over the prior six months, 0.2801 [[art:ca1c764c:run.model_summary#coefficients.delinq_count_6m.value]], and the maximum delinquency over that window, 0.2263 [[art:ca1c764c:run.model_summary#coefficients.delinq_max_6m.value]].
All three are positive, which is the direction subject matter expects, since recent and repeated delinquency is the strongest observable precursor of default.
The largest negative coefficient is on the granted credit limit, -0.2091 [[art:ca1c764c:run.model_summary#coefficients.limit_bal.value]], and its sign is also as expected, because larger limits are extended to borrowers already underwritten as stronger.
The six-month mean payment ratio enters negatively, -0.09824 [[art:ca1c764c:run.model_summary#coefficients.pay_ratio_mean_6m.value]], consistent with sustained repayment reducing risk.

One sign does not match expectation: utilisation enters negatively, -0.08257 [[art:ca1c764c:run.model_summary#coefficients.utilisation.value]], against the standard view that a borrower drawing more of an available line is more likely to default.
A plausible reading is that the retained delinquency and payment-ratio terms absorb the risk signal utilisation would otherwise carry, and that removing the closely related bill and utilisation aggregates left this term with a residual, sign-flipped role.
That reading is an inference by the validator, and the developmental evidence reviewed here does not contain a rationale for the sign, so a documented developer explanation should be obtained before the term is relied on for attribution or adverse-action reasoning.

The remaining terms are small enough to carry little weight in the score.
Age enters at 0.07253 [[art:ca1c764c:run.model_summary#coefficients.age.value]], the six-month bill trend at 0.04808 [[art:ca1c764c:run.model_summary#coefficients.bill_trend_6m.value]], the most recent payment ratio at 0.00678 [[art:ca1c764c:run.model_summary#coefficients.pay_ratio_last.value]], and the six-month mean bill at -0.007568 [[art:ca1c764c:run.model_summary#coefficients.bill_mean_6m.value]].
The sign on age is not strongly determined by subject matter in either direction, and the positive sign on the most recent payment ratio is mildly counter to expectation but too small in magnitude to move the score materially.

Effective challenge takes the form of benchmarking the champion against an alternative model, one of the practical assessments the guidance names for models of this kind.
The challenger reaches an AUC on test of 0.7789 [[art:5646e7f3:challenger.auc]] against the champion's recomputed 0.755 [[art:365b7034:metrics.test.auc]].
The challenger's lead is 0.02391 [[art:3877bdd0:challenger.delta_auc]].
The threshold that decides whether that difference matters is an AUC lead of 0.03 [[art:e042774c:threshold.E1.delta_auc]], and the observed lead does not reach it, so the champion's functional form is not displaced on this evidence.
The Brier scores point the same way and by a similarly modest margin, 0.135 [[art:2031a154:challenger.brier]] for the challenger against 0.1385 [[art:86e93c8f:metrics.test.brier]] for the champion, a difference in the challenger's favour that is not governed by any stated threshold.
The honest summary is that a more flexible alternative extracts somewhat more discrimination from the same inputs without extracting enough to overturn the design choice.

The developmental evidence reviewed for this section does not include sensitivity analysis of the score's response to small changes in inputs and parameter values, or stress testing over extreme input ranges, which the superseded guidance sets out explicitly as a check on model stability [[reg:SR11-7:V.1.a]].
That gap limits what can be said about the model's behaviour at the edges of its input range, and it should be closed by developer testing rather than inferred from the fitted coefficients.

No check that ran on this section's material raised a finding, and in particular none was raised against the champion's functional form.

## 3. Data integrity and drift

This section examines the information input component of the credit_default 1.0 package, on the guidance's premise that "the quality of model outputs depends on the quality of input data and assumptions, and errors in inputs or incorrect assumptions will lead to inaccurate outputs" [[reg:SR11-7:III]].
The assessment covers missingness within and between splits, population and characteristic stability from the training split to the held-out split, and the four leakage screens carried in the package.

### Missingness

The package supplies two splits: train, with 21000 [[art:a359de9d:profile.train.n]] rows, and test, with 9000 [[art:abbe1a27:profile.test.n]] rows.
The largest missing fraction over all columns of train is 0.0 [[art:050a3099:profile.train.missing.max]].
The largest missing fraction over all columns of test is 0.0 [[art:f813848d:profile.test.missing.max]].
Both splits are therefore complete on every recorded column, the gap in missingness between them is nil, and it sits below the D1 allowance of 0.1 [[art:9cce25ea:threshold.D1.missing_gap]] by the full width of that allowance.
Complete data removes imputation choices as a source of divergence between the splits, but it also means the package carries no evidence on how the model behaves when fields are absent, which is a condition it will meet in use.

### Population and characteristic stability

The declared bound on population stability is the S1 threshold of 0.25 [[art:278b9016:threshold.S1.psi]], and package.yaml restates the same figure as its own maximum, 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
The largest train-to-test population stability index across all features and the score is 0.003083 [[art:e1d82330:psi.max]], attributable to age.
The score itself shifts by a population stability index of 0.001368 [[art:ec2b8d1b:psi.y_score]], so the predicted distribution on test is close to the one the model was fitted on.
The largest characteristic stability index is 0.004737 [[art:ce1257d8:csi.max]], attributable to delinq_max_6m.
No separate bound on characteristic stability is declared in the package, so the per-feature contributions below are read against the population stability bound and against each other rather than against a threshold of their own.

Per-feature values, each given as population stability index between train and test and then as contribution to the shift in the linear predictor:

- age: 0.003083 [[art:06c22a63:psi.age]] and 0.001203 [[art:25b88f37:csi.age]].
- limit_bal: 0.001272 [[art:b0195847:psi.limit_bal]] and 0.001384 [[art:c91a2a4b:csi.limit_bal]].
- utilisation: 0.0006523 [[art:f094559b:psi.utilisation]] and 0.0002136 [[art:6ed37e42:csi.utilisation]].
- bill_mean_6m: 0.001488 [[art:127cdf82:psi.bill_mean_6m]] and a characteristic contribution smaller than that of any other feature, too small to state at the precision used throughout this section [[art:0c34001d:csi.bill_mean_6m]].
- bill_trend_6m: 0.0007484 [[art:78be70d2:psi.bill_trend_6m]] and 0.0003675 [[art:9e5a9b68:csi.bill_trend_6m]].
- pay_ratio_last: 0.002264 [[art:82c97112:psi.pay_ratio_last]] and 0.0001132 [[art:5898a9c5:csi.pay_ratio_last]].
- pay_ratio_mean_6m: 0.001028 [[art:62e0e0f8:psi.pay_ratio_mean_6m]] and 0.002043 [[art:5e53c153:csi.pay_ratio_mean_6m]].
- delinq_last: 0.0002347 [[art:cbc9de36:psi.delinq_last]] and 0.001698 [[art:e755cf0a:csi.delinq_last]].
- delinq_count_6m: 0.001856 [[art:d77ddb1d:psi.delinq_count_6m]] and 0.0008781 [[art:f0438233:csi.delinq_count_6m]].
- delinq_max_6m: 0.001027 [[art:4b0a94ab:psi.delinq_max_6m]] and 0.004737 [[art:35990a39:csi.delinq_max_6m]].

Every per-feature value lies far under the declared bound, and the ordering of features by marginal shift differs from their ordering by contribution to the linear predictor, which is expected once feature weights are taken into account.
These figures describe the train-to-test relationship only; because the package declares no further split and no out-of-time sample, they carry no information about stability against production or future populations, and the drift monitoring discussed elsewhere in this report remains the only control on that.

### Leakage screens

The timing screen reports 0.0 [[art:742bcd24:leakage.timing.n_flagged]] features declared as during_period or after_outcome, so on the declarations as filed no feature is observed at or after the outcome it is used to predict.
This screen tests the declarations, not the underlying data lineage, and its result is only as reliable as the timings the developer recorded.
The strongest single feature reaches an area under the curve of 0.728 [[art:2e212f3a:leakage.target_corr.max_single_feature_auc]], against the L1 ceiling of 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]], so no individual feature is near-deterministic of the target.
The name screen matched 0.0 [[art:407e62be:leakage.name_screen.n_matched]] feature names against the target-adjacent lexicon, which rules out the most obvious naming patterns and nothing more.

The overlap screen is the one exceedance in this section.
The share of test rows whose feature values also appear in train is 0.01256 [[art:ebd7ff30:leakage.overlap]], confirmed by the feature-level measurement of 0.01256 [[art:517f3049:leakage.overlap.features]], against the L2 bound of 0.005 [[art:9f336eaf:threshold.L2.overlap]].
The measured share is above that bound, so the test split is not a fully clean holdout under the package's own standard, and this is recorded as a finding rather than as an observation.
Two pieces of context bear on its severity without resolving it.
First, overlap on the declared identifier is 0.0 [[art:63d37fc5:leakage.overlap.ids]], so no client_id present in test also identifies a row of train, and the exceedance is not the reuse of identified records across the split.
Second, the share of train rows whose feature values are not unique within train is 0.01162 [[art:c988bb0e:leakage.duplicates.train]], a magnitude close to the cross-split figure, which is consistent with the feature vector being coarse enough that distinct clients collide on it.
On that reading the exceedance reflects limited granularity in the feature space rather than contamination of the holdout, but the artifacts do not establish which explanation holds, and the validator has not verified it.
Until it is resolved, the discriminatory power reported on the test split should be treated as carrying a small optimistic bias of unquantified size, and the exceedance should be either remediated by deduplicating against train or accepted with a documented rationale and a tightened or restated L2 bound.

## 4. Outcomes analysis

The Federal Reserve's guidance frames outcomes analysis as a comparison of model outputs to corresponding real-world outcomes, assessing performance relative to model objectives and business use, and it treats persistent deviations outside established performance thresholds as grounds for adjustment, recalibration, or redevelopment [[reg:SR26-2:V.1.b]].
This section reports discrimination before calibration, because the observed event rate on test, 0.2212 [[art:f60ae2a7:metrics.test.event_rate]], is above the 0.05 [[art:42f1351e:rule.calibration_first_event_rate]] event rate below which the report would put calibration first.
All figures below were recomputed by quaestor from the model package under review rather than read from the developer's own summary.

### 4.1 Discrimination and fit by split

The table below carries one row per recomputed metric, with the train column and the test column each cited to its own artifact.

| Metric | Train | Test |
| --- | --- | --- |
| Observations | 21000 [[art:1721ceae:metrics.train.n]] | 9000 [[art:5367a59f:metrics.test.n]] |
| AUC | 0.7546 [[art:01cf8178:metrics.train.auc]] | 0.755 [[art:365b7034:metrics.test.auc]] |
| Gini | 0.5091 [[art:eaaf0f79:metrics.train.gini]] | 0.51 [[art:296bfeeb:metrics.test.gini]] |
| KS | 0.4144 [[art:18df22bd:metrics.train.ks]] | 0.4067 [[art:d3c4ed61:metrics.test.ks]] |
| Log loss | 0.4439 [[art:b816b083:metrics.train.logloss]] | 0.4442 [[art:2de58c1b:metrics.test.logloss]] |
| Brier score | 0.1384 [[art:c95106e9:metrics.train.brier]] | 0.1385 [[art:86e93c8f:metrics.test.brier]] |
| Event rate | 0.2212 [[art:657aa7fc:metrics.train.event_rate]] | 0.2212 [[art:f60ae2a7:metrics.test.event_rate]] |
| Mean predicted probability | 0.2212 [[art:935d2cb7:metrics.train.mean_predicted]] | 0.2206 [[art:89d241ea:metrics.test.mean_predicted]] |
| Share of events in the top two deciles | 0.5031 [[art:5131afa7:deciles.train.top2_capture]] | 0.4952 [[art:e2c0ad9f:deciles.test.top2_capture]] |

Rank-ordering on test is set out by decile of predicted probability, with the first decile holding the highest probabilities.

<!-- quaestor:renderer:begin table deciles.test -->
Decile separation on test; decile 1 holds the highest probabilities [[art:4396db6f:deciles.test]]:

| decile | count | events | event_rate | lift |
|---|---|---|---|---|
| 1 | 900 | 617 | 0.6855555556 | 3.098945254 |
| 2 | 900 | 369 | 0.41 | 1.85334003 |
| 3 | 900 | 226 | 0.2511111111 | 1.135107986 |
| 4 | 900 | 154 | 0.1711111111 | 0.773480663 |
| 5 | 900 | 159 | 0.1766666667 | 0.7985936715 |
| 6 | 900 | 119 | 0.1322222222 | 0.5976896032 |
| 7 | 900 | 98 | 0.1088888889 | 0.4922149674 |
| 8 | 900 | 87 | 0.09666666667 | 0.4369663486 |
| 9 | 900 | 90 | 0.1 | 0.4520341537 |
| 10 | 900 | 72 | 0.08 | 0.361627323 |
<!-- quaestor:renderer:end -->

The top two test deciles capture 0.4952 [[art:e2c0ad9f:deciles.test.top2_capture]] of test events, against 0.5031 [[art:5131afa7:deciles.train.top2_capture]] on train, so the concentration of events in the highest-scoring deciles holds up out of sample.

### 4.2 Train-to-test gap

The declared bound on the train-to-test AUC gap under rule O1 is 0.08 [[art:630f28f4:threshold.O1.auc_gap]].
Test AUC, 0.755 [[art:365b7034:metrics.test.auc]], is not below train AUC, 0.7546 [[art:01cf8178:metrics.train.auc]], so the gap in the direction the rule guards against does not arise and the declared bound is not breached.
The same pattern holds for the other paired measures in the table above, where the train and test values differ only in the trailing digits, and the review found no evidence of material overfitting on this evidence.

### 4.3 Calibration

The calibration slope from the logistic regression of the outcome on logit(p) is 0.9886 [[art:e06564c7:calibration_slope.test]] on test and 1.001 [[art:85461245:calibration_slope.train]] on train, both inside the declared band from 0.8 [[art:749634ae:threshold.C1.calibration_slope.min]] to 1.2 [[art:b6672579:threshold.C1.calibration_slope.max]].
The corresponding intercept is -0.008632 [[art:2ee976d3:calibration_intercept.test]] on test and 0.0003779 [[art:2ce8cd09:calibration_intercept.train]] on train, in both cases close enough to zero that no systematic level shift in the predicted log-odds is visible.
The mean predicted probability on test, 0.2206 [[art:89d241ea:metrics.test.mean_predicted]], sits just under the observed test event rate of 0.2212 [[art:f60ae2a7:metrics.test.event_rate]], a slight under-prediction of the overall level.
The relative gap between mean predicted and observed is 0.002944 [[art:bae28fd6:calibration.mean_rel_gap.test]] on test and 0.0001555 [[art:a03ea014:calibration.mean_rel_gap.train]] on train, against a tolerance under rule C1 of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]], so both are well inside tolerance.
Calibration by decile of predicted probability on test is reported below.

<!-- quaestor:renderer:begin table calibration.test -->
Calibration by decile of predicted probability on test [[art:d19b8ac3:calibration.test]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.08332970973 | 0.08 | 900 |
| 2 | 0.1032343368 | 0.1 | 900 |
| 3 | 0.1143940159 | 0.09666666667 | 900 |
| 4 | 0.1242358388 | 0.1088888889 | 900 |
| 5 | 0.1323529339 | 0.1322222222 | 900 |
| 6 | 0.1415591085 | 0.1766666667 | 900 |
| 7 | 0.1653629955 | 0.1711111111 | 900 |
| 8 | 0.2512859937 | 0.2511111111 | 900 |
| 9 | 0.4103868875 | 0.41 | 900 |
| 10 | 0.6795685635 | 0.6855555556 | 900 |
<!-- quaestor:renderer:end -->

### 4.4 Developer-declared thresholds

The table below carries one row per threshold declared in package.yaml, with its bound, the recomputed value and the outcome.

| Rule | Bound | Value | Outcome |
| --- | --- | --- | --- |
| Test AUC, minimum | 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]] | 0.755 [[art:365b7034:metrics.test.auc]] | Pass |
| Test Brier score, maximum | 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]] | 0.1385 [[art:86e93c8f:metrics.test.brier]] | Pass |
| Test calibration slope, minimum | 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] | 0.9886 [[art:e06564c7:calibration_slope.test]] | Pass |
| Test calibration slope, maximum | 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]] | 0.9886 [[art:e06564c7:calibration_slope.test]] | Pass |
| PSI, maximum | 0.25 [[art:fbb5a9d1:threshold.package.psi.max]] | Not recomputed in the artifacts available to this section | Not evaluated here |
| Wall-clock seconds, maximum | 300 [[art:3f4c6e97:threshold.package.max_seconds]] | Not recomputed in the artifacts available to this section | Not evaluated here |

Every declared threshold that this section could evaluate was met, and the two rows marked as not evaluated here are carried forward as open items rather than as passes.
Guidance also directs that outcomes analysis be reviewed for the reasonableness and appropriateness of the results, with additional analysis and testing where warranted, and on that basis the single-holdout evidence above is treated as a development-stage result rather than as back-testing over a performance window [[reg:SR11-7:V.1.c]].

## 5. Sensitivity and scenario analysis

Sensitivity analysis here follows the guidance's expectation that validation check the impact of small changes in inputs and parameter values on model outputs, and that robustness and stability checks be repeated rather than performed once [[reg:SR11-7:V.1.a]].

### 5.1 Multicollinearity among the retained features

The largest variance inflation factor across the retained features is 3.544 [[art:d3785ba9:vif.max]], against the M1 threshold of 10.0 [[art:aeb4f33c:threshold.M1.vif]].
That maximum is attained by `delinq_count_6m`, whose variance inflation factor on train is 3.544 [[art:7273e0be:vif.delinq_count_6m]].
Belsley's condition number of the column-standardised design is 4.279 [[art:ba0d9cc4:condition_number]], against the M1 threshold of 30.0 [[art:7e52fd7a:threshold.M1.condition_number]].
Both diagnostics sit below their thresholds, so the retained design carries no near-dependency severe enough to make the fitted coefficients unstable under small perturbations of the training columns.

The per-feature variance inflation factors on train are:

- `age`: 1.025 [[art:692cd6e9:vif.age]]
- `bill_mean_6m`: 2.265 [[art:87cb4e54:vif.bill_mean_6m]]
- `bill_trend_6m`: 1.330 [[art:6d3f01ce:vif.bill_trend_6m]]
- `delinq_count_6m`: 3.544 [[art:7273e0be:vif.delinq_count_6m]]
- `delinq_last`: 2.321 [[art:59461811:vif.delinq_last]]
- `delinq_max_6m`: 3.484 [[art:e7b701a1:vif.delinq_max_6m]]
- `limit_bal`: 2.097 [[art:0c6efb3f:vif.limit_bal]]
- `pay_ratio_last`: 2.714 [[art:b68613a6:vif.pay_ratio_last]]
- `pay_ratio_mean_6m`: 3.027 [[art:2cda5cfc:vif.pay_ratio_mean_6m]]
- `utilisation`: 2.829 [[art:6ce4c102:vif.utilisation]]

The two delinquency-count features and the two payment-ratio features are the most collinear pairs in the set, which is expected given their shared six-month window, and neither pair reaches a level that would warrant dropping a column.

### 5.2 Analyses that do not apply to this model type

Stability across declared regimes was not assessed, because the package declares no regime column for this model, and no regime-partitioned sensitivity result exists to report.
Rate-shock scenario analysis was not assessed, because the subject is not a hazard model; the value change at the extreme shocks, the monotonicity of the shock curve, and the sign of its convexity against the package's declared direction are therefore all undefined for this package rather than measured and found acceptable.
Both items are listed in Appendix D as out of scope for this model type, and nothing in this section should be read as a result from either analysis.

### 5.3 Limitation

The evidence in this section speaks only to the conditioning of the training design and not to the model's behaviour under macroeconomic or rate stress, for which this package supplies no scenario artifact.
Because the applicable diagnostics here are static properties of the training columns, they should be recomputed on each refresh so that any drift toward the thresholds is observed as it develops [[reg:SR11-7:V.1.b]].

## 6. Findings and recommendations

Findings in this section are ordered by severity and each carries the evidence on which it rests, so that recommendations, responses, and exceptions can be tracked through remediation [[reg:SR26-2:VI.3]].

No finding was raised for the credit_default version 1.0 model package in this section.

Every check configured to run against this section's material was executed and each one returned without raising a finding.

The checks drew on the artifacts registered for this section of the review, and no artifact was cited here because none was required to support a finding.

The validator concludes that this section records no defect, and the developer is asked only to retain the underlying artifacts and check records so that the absence of findings remains auditable at the next periodic review.

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1, S1), `compute_metrics` (T1, C1, O1), `check_leakage` (L1, L2), `check_collinearity` (M1), `challenger_compare` (E1).

## 7. Ongoing monitoring recommendations

Ongoing monitoring evaluates the extent to which this model continues to perform as expected given potential changes in products, exposures, activities, clients, data relevance, or market conditions [[reg:SR26-2:V.2]].
The plan below reuses the threshold artifacts already cited by this validation's checks and introduces no new bound.

### Quantities to track and the bound each is tracked against

- Discrimination: recompute AUC on each monitoring window and compare it against the declared floor of 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]], reading the approval-time value of 0.755 [[art:365b7034:metrics.test.auc]] as the reference level rather than as a guarantee of future performance.
- Calibration slope: refit the logistic regression of the realised outcome on logit(p) each window and require the slope to stay within the declared band whose lower bound is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] and whose upper bound is 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]], against the approval-time value of 0.9886 [[art:e06564c7:calibration_slope.test]].
- Calibration error: recompute the Brier score on each window and compare it against the declared ceiling of 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]], noting that this validation records the ceiling but no observed production value.
- Input and score stability: recompute the largest PSI across the scored population, score included, and compare it against the declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]], with the development-time value of 0.003083 [[art:e1d82330:psi.max]] indicating how much headroom existed at approval.
- Realised event rate: track it each window, and when it falls below 0.05 [[art:42f1351e:rule.calibration_first_event_rate]] treat calibration evidence as the leading signal for escalation ahead of discrimination.
- Scoring runtime: track wall-clock time for the scoring run against the declared cap of 300.0 [[art:3f4c6e97:threshold.package.max_seconds]] seconds, since a breach signals an implementation or data-volume change rather than a statistical one.

### Frequency

Stability, event-rate, and runtime measures depend only on inputs and scores and should be produced on the shortest cycle the scoring schedule supports, which for a batch credit model is normally monthly.
Discrimination and calibration measures depend on realised outcomes and should be produced only once a monitoring window has accumulated enough matured defaults to make the estimate meaningful, which for this product is normally quarterly.
The frequency and scope of monitoring reports depend on the nature of the model, the availability of new data or modeling approaches, and model materiality, so the cadence above should be revisited if the model's use or materiality changes [[reg:SR26-2:V.2]].

### Escalation

A measure that crosses its declared bound should trigger investigation rather than automatic action, because a single window can breach for reasons of sample composition alone.
Where performance deviates meaningfully from expectations across consecutive windows, the responsible parties should consider whether overlays, adjustment, recalibration, or redevelopment are warranted [[reg:SR26-2:V.2]].

### What this validation could not cover and monitoring should watch instead

The stability evidence in this report compares development data against the held-out test split, not production data against development data, so genuine population drift after deployment is unobserved here and must be established by the production PSI series.
This validation had no out-of-time sample, so it says nothing about how performance decays with calendar time, and the trend of the quarterly discrimination and calibration series is the only available evidence on that question.
No benchmark model or external comparison was available, and benchmarking against alternative internal or external data or models belongs in the monitoring program, with discrepancies triggering investigation into their sources and degree [[reg:SR11-7:V.1.b]].
No override activity exists yet for a model that has not been used in production, so monitoring should record overrides with appropriate documentation and analyse override performance, since a high override rate or overrides that consistently improve outcomes indicates the underlying model needs revision [[reg:SR11-7:V.1.b]].
Process verification of the deployed implementation, including that data inputs remain accurate and complete and that code changes are logged and auditable, was outside the scope of this validation and is a standing monitoring obligation [[reg:SR11-7:V.1.b]].
Even with sound modeling practices and rigorous validation, material model risk can remain, so users of the output should understand and communicate its limitations and supplement it with complementary analysis [[reg:SR26-2:V]].

## Appendix A — Claims

Grounding precision 0.9816 before repair (160 of 163 claims verified; 1 unsupported, 2 unattributed) and 1.0000 after 0 repaired claim(s). Per section (post-repair): summary 24/24; conceptual_soundness 26/26; data_integrity 38/38; outcomes 46/46; sensitivity 15/15; monitoring 10/10.

Developer claims: 2 of 2 declared in `package.yaml` verify against this run's artifacts.

Excluded numeric tokens (not claims): section_number (4.1, 4.2, 4.3, 4.4); citation_hash (3f4c6e97, a359de9d, abbe1a27, 657aa7fc); regulatory_section_id (SR26-2:V.1.b, SR11-7:V.1, SR26-2:V.1.a, SR11-7:V.1.a); package_version (1.0); extractor_returned_excluded_token (6.0, 1.0, 2.0, 4.1).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The package declares a wall-clock cap of 300 seconds for tha… | 300 | ratio | max_seconds |  | eq | `[[art:3f4c6e97:threshold.package.max_seconds]]` | verified | 300 |
| 2 | summary | Fitting used a train split of 21000 rows and evaluation used… | 21000 | count | n | train | eq | `[[art:a359de9d:profile.train.n]]` | verified | 21000 |
| 3 | summary | Fitting used a train split of 21000 rows and evaluation used… | 9000 | count | n | test | eq | `[[art:abbe1a27:profile.test.n]]` | verified | 9000 |
| 4 | summary | The outcome is balanced identically across the splits, with… | 0.2212 | ratio | event_rate | train | eq | `[[art:657aa7fc:metrics.train.event_rate]]` | verified | 0.2211904762 |
| 5 | summary | The outcome is balanced identically across the splits, with… | 0.2212 | ratio | event_rate | test | eq | `[[art:f60ae2a7:metrics.test.event_rate]]` | verified | 0.2212222222 |
| 6 | summary | Test AUC is 0.755 against a declared minimum of 0.7 . | 0.755 | ratio | auc | test | eq | `[[art:365b7034:metrics.test.auc]]` | verified | 0.7550239453 |
| 7 | summary | Test AUC is 0.755 against a declared minimum of 0.7 . | 0.7 | ratio | auc | test | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 8 | summary | The test Brier score is 0.1385 against a declared maximum of… | 0.1385 | ratio | brier | test | eq | `[[art:86e93c8f:metrics.test.brier]]` | verified | 0.1385162411 |
| 9 | summary | The test Brier score is 0.1385 against a declared maximum of… | 0.2 | ratio | brier | test | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 10 | summary | The test calibration slope is 0.9886 , inside a declared ban… | 0.9886 | ratio | calibration_slope | test | eq | `[[art:e06564c7:calibration_slope.test]]` | verified | 0.9885680158 |
| 11 | summary | The test calibration slope is 0.9886 , inside a declared ban… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 12 | summary | The test calibration slope is 0.9886 , inside a declared ban… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 13 | summary | The largest train-to-test population stability index, score… | 0.003083 | ratio | psi |  | eq | `[[art:e1d82330:psi.max]]` | verified | 0.00308251646 |
| 14 | summary | The largest train-to-test population stability index, score… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 15 | summary | Train-side behaviour tracks the test split closely, with a t… | 0.7546 | ratio | auc | train | eq | `[[art:01cf8178:metrics.train.auc]]` | verified | 0.7545552576 |
| 16 | summary | Train-side behaviour tracks the test split closely, with a t… | 1.001 | ratio | calibration_slope | train | eq | `[[art:85461245:calibration_slope.train]]` | verified | 1.000539237 |
| 17 | summary | Supporting test-split measures from the same run are a Gini… | 0.51 | ratio | gini | test | eq | `[[art:296bfeeb:metrics.test.gini]]` | verified | 0.5100478906 |
| 18 | summary | Supporting test-split measures from the same run are a Gini… | 0.4067 | ratio | ks | test | eq | `[[art:d3c4ed61:metrics.test.ks]]` | verified | 0.4066831201 |
| 19 | summary | Supporting test-split measures from the same run are a Gini… | 0.4442 | ratio | logloss | test | eq | `[[art:2de58c1b:metrics.test.logloss]]` | verified | 0.4441654047 |
| 20 | summary | Supporting test-split measures from the same run are a Gini… | 0.2206 | ratio | mean_predicted | test | eq | `[[art:89d241ea:metrics.test.mean_predicted]]` | verified | 0.2205710384 |
| 21 | summary | Design-matrix diagnostics give a largest variance inflation… | 3.544 | ratio | vif |  | eq | `[[art:d3785ba9:vif.max]]` | verified | 3.54357449 |
| 22 | summary | Design-matrix diagnostics give a largest variance inflation… | 4.279 | ratio | condition_number |  | eq | `[[art:ba0d9cc4:condition_number]]` | verified | 4.279282985 |
| 23 | summary | Design-matrix diagnostics give a largest variance inflation… | 0.004737 | ratio | csi |  | eq | `[[art:ce1257d8:csi.max]]` | verified | 0.00473710965 |
| 24 | summary | A challenger benchmark scored above the champion on test, by… | 0.02391 | ratio | delta_auc | test | eq | `[[art:3877bdd0:challenger.delta_auc]]` | verified | 0.02390594313 |
| 25 | conceptual_soundness | The champion in the credit_default package under review is a… | -1.442 | ratio | intercept |  | eq | `[[art:ca1c764c:run.model_summary#intercept]]` | verified | -1.441621171 |
| 26 | conceptual_soundness | The champion in the credit_default package under review is a… | 21000 | count | n_train | train | eq | `[[art:ca1c764c:run.model_summary#n_train]]` | verified | 21000 |
| 27 | conceptual_soundness | The feature inventory declares 12 inputs. | 12 | count | n |  | eq | `[[art:792cb79c:run.features#n]]` | verified | 12 |
| 28 | conceptual_soundness | Of these, 2 are known at origination and 10 are known before… | 2 | count | at_origination |  | eq | `[[art:792cb79c:run.features#at_origination]]` | verified | 2 |
| 29 | conceptual_soundness | Of these, 2 are known at origination and 10 are known before… | 10 | count | before_period_start |  | eq | `[[art:792cb79c:run.features#before_period_start]]` | verified | 10 |
| 30 | conceptual_soundness | No input is drawn from within the performance period, 0 , an… | 0 | count | during_period |  | eq | `[[art:792cb79c:run.features#during_period]]` | verified | 0 |
| 31 | conceptual_soundness | No input is drawn from within the performance period, 0 , an… | 0 | count | after_outcome |  | eq | `[[art:792cb79c:run.features#after_outcome]]` | verified | 0 |
| 32 | conceptual_soundness | The developer's own collinearity screen removed two inputs a… | 10 | ratio | vif_threshold |  | eq | `[[art:ca1c764c:run.model_summary#vif_threshold]]` | verified | 10 |
| 33 | conceptual_soundness | The last observed bill amount was dropped at a variance infl… | 33.8 | ratio | vif |  | eq | `[[art:ca1c764c:run.model_summary#removed.bill_last.vif]]` | verified | 33.803856 |
| 34 | conceptual_soundness | The last observed bill amount was dropped at a variance infl… | 10.96 | ratio | vif |  | eq | `[[art:ca1c764c:run.model_summary#removed.utilisation_mean_6m.vif]]` | verified | 10.962284 |
| 35 | conceptual_soundness | The largest coefficient is on the most recent delinquency st… | 0.4847 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.delinq_last.value]]` | verified | 0.4846949872 |
| 36 | conceptual_soundness | It is followed by the count of delinquencies over the prior… | 0.2801 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.delinq_count_6m.value]]` | verified | 0.2800755777 |
| 37 | conceptual_soundness | It is followed by the count of delinquencies over the prior… | 0.2263 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.delinq_max_6m.value]]` | verified | 0.2262527885 |
| 38 | conceptual_soundness | The largest negative coefficient is on the granted credit li… | -0.2091 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.limit_bal.value]]` | verified | -0.2091380131 |
| 39 | conceptual_soundness | The six-month mean payment ratio enters negatively, -0.09824… | -0.09824 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.pay_ratio_mean_6m.value]]` | verified | -0.09823688664 |
| 40 | conceptual_soundness | One sign does not match expectation: utilisation enters nega… | -0.08257 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.utilisation.value]]` | verified | -0.08257487854 |
| 41 | conceptual_soundness | Age enters at 0.07253 , the six-month bill trend at 0.04808… | 0.07253 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.age.value]]` | verified | 0.07253007645 |
| 42 | conceptual_soundness | Age enters at 0.07253 , the six-month bill trend at 0.04808… | 0.04808 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.bill_trend_6m.value]]` | verified | 0.04808068095 |
| 43 | conceptual_soundness | Age enters at 0.07253 , the six-month bill trend at 0.04808… | 0.00678 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.pay_ratio_last.value]]` | verified | 0.006779706816 |
| 44 | conceptual_soundness | Age enters at 0.07253 , the six-month bill trend at 0.04808… | -0.007568 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.bill_mean_6m.value]]` | verified | -0.007567968246 |
| 45 | conceptual_soundness | The challenger reaches an AUC on test of 0.7789 against the… | 0.7789 | ratio | auc | test | eq | `[[art:5646e7f3:challenger.auc]]` | verified | 0.7789298885 |
| 46 | conceptual_soundness | The challenger reaches an AUC on test of 0.7789 against the… | 0.755 | ratio | auc | test | eq | `[[art:365b7034:metrics.test.auc]]` | verified | 0.7550239453 |
| 47 | conceptual_soundness | The challenger's lead is 0.02391 . | 0.02391 | ratio | delta_auc |  | eq | `[[art:3877bdd0:challenger.delta_auc]]` | verified | 0.02390594313 |
| 48 | conceptual_soundness | The threshold that decides whether that difference matters i… | 0.03 | ratio | delta_auc |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 49 | conceptual_soundness | The Brier scores point the same way and by a similarly modes… | 0.135 | ratio | brier |  | eq | `[[art:2031a154:challenger.brier]]` | verified | 0.1349523392 |
| 50 | conceptual_soundness | The Brier scores point the same way and by a similarly modes… | 0.1385 | ratio | brier | test | eq | `[[art:86e93c8f:metrics.test.brier]]` | verified | 0.1385162411 |
| 51 | data_integrity | The package supplies two splits: train, with 21000 rows, and… | 21000 | count | n | train | eq | `[[art:a359de9d:profile.train.n]]` | verified | 21000 |
| 52 | data_integrity | The package supplies two splits: train, with 21000 rows, and… | 9000 | count | n | test | eq | `[[art:abbe1a27:profile.test.n]]` | verified | 9000 |
| 53 | data_integrity | The largest missing fraction over all columns of train is 0.… | 0 | ratio | missing.max | train | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 54 | data_integrity | The largest missing fraction over all columns of test is 0.0… | 0 | ratio | missing.max | test | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 55 | data_integrity | Both splits are therefore complete on every recorded column,… | 0.1 | ratio | missing_gap |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 56 | data_integrity | The declared bound on population stability is the S1 thresho… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 57 | data_integrity | The declared bound on population stability is the S1 thresho… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 58 | data_integrity | The largest train-to-test population stability index across… | 0.003083 | ratio | psi |  | eq | `[[art:e1d82330:psi.max]]` | verified | 0.00308251646 |
| 59 | data_integrity | The score itself shifts by a population stability index of 0… | 0.001368 | ratio | psi |  | eq | `[[art:ec2b8d1b:psi.y_score]]` | verified | 0.001367653962 |
| 60 | data_integrity | The largest characteristic stability index is 0.004737 , att… | 0.004737 | ratio | csi |  | eq | `[[art:ce1257d8:csi.max]]` | verified | 0.00473710965 |
| 61 | data_integrity | - age: 0.003083 and 0.001203 . | 0.003083 | ratio | psi |  | eq | `[[art:06c22a63:psi.age]]` | verified | 0.00308251646 |
| 62 | data_integrity | - age: 0.003083 and 0.001203 . | 0.001203 | ratio | csi |  | eq | `[[art:25b88f37:csi.age]]` | verified | 0.001203264027 |
| 63 | data_integrity | - limit_bal: 0.001272 and 0.001384 . | 0.001272 | ratio | psi |  | eq | `[[art:b0195847:psi.limit_bal]]` | verified | 0.001272099805 |
| 64 | data_integrity | - limit_bal: 0.001272 and 0.001384 . | 0.001384 | ratio | csi |  | eq | `[[art:c91a2a4b:csi.limit_bal]]` | verified | 0.001384099928 |
| 65 | data_integrity | - utilisation: 0.0006523 and 0.0002136 . | 0.0006523 | ratio | psi |  | eq | `[[art:f094559b:psi.utilisation]]` | verified | 0.0006522718782 |
| 66 | data_integrity | - utilisation: 0.0006523 and 0.0002136 . | 0.0002136 | ratio | csi |  | eq | `[[art:6ed37e42:csi.utilisation]]` | verified | 0.0002135922405 |
| 67 | data_integrity | - bill_mean_6m: 0.001488 and a characteristic contribution s… | 0.001488 | ratio | psi |  | eq | `[[art:127cdf82:psi.bill_mean_6m]]` | verified | 0.001488231386 |
| 68 | data_integrity | - bill_trend_6m: 0.0007484 and 0.0003675 . | 0.0007484 | ratio | psi |  | eq | `[[art:78be70d2:psi.bill_trend_6m]]` | verified | 0.0007484247754 |
| 69 | data_integrity | - bill_trend_6m: 0.0007484 and 0.0003675 . | 0.0003675 | ratio | csi |  | eq | `[[art:9e5a9b68:csi.bill_trend_6m]]` | verified | 0.0003674527783 |
| 70 | data_integrity | - pay_ratio_last: 0.002264 and 0.0001132 . | 0.002264 | ratio | psi |  | eq | `[[art:82c97112:psi.pay_ratio_last]]` | verified | 0.0022643364 |
| 71 | data_integrity | - pay_ratio_last: 0.002264 and 0.0001132 . | 0.0001132 | ratio | csi |  | eq | `[[art:5898a9c5:csi.pay_ratio_last]]` | verified | 0.0001131831266 |
| 72 | data_integrity | - pay_ratio_mean_6m: 0.001028 and 0.002043 . | 0.001028 | ratio | psi |  | eq | `[[art:62e0e0f8:psi.pay_ratio_mean_6m]]` | verified | 0.001027537662 |
| 73 | data_integrity | - pay_ratio_mean_6m: 0.001028 and 0.002043 . | 0.002043 | ratio | csi |  | eq | `[[art:5e53c153:csi.pay_ratio_mean_6m]]` | verified | 0.002042601165 |
| 74 | data_integrity | - delinq_last: 0.0002347 and 0.001698 . | 0.0002347 | ratio | psi |  | eq | `[[art:cbc9de36:psi.delinq_last]]` | verified | 0.0002346592849 |
| 75 | data_integrity | - delinq_last: 0.0002347 and 0.001698 . | 0.001698 | ratio | csi |  | eq | `[[art:e755cf0a:csi.delinq_last]]` | verified | 0.001697603731 |
| 76 | data_integrity | - delinq_count_6m: 0.001856 and 0.0008781 . | 0.001856 | ratio | psi |  | eq | `[[art:d77ddb1d:psi.delinq_count_6m]]` | verified | 0.00185562271 |
| 77 | data_integrity | - delinq_count_6m: 0.001856 and 0.0008781 . | 0.0008781 | ratio | csi |  | eq | `[[art:f0438233:csi.delinq_count_6m]]` | verified | 0.0008781439663 |
| 78 | data_integrity | - delinq_max_6m: 0.001027 and 0.004737 . | 0.001027 | ratio | psi |  | eq | `[[art:4b0a94ab:psi.delinq_max_6m]]` | verified | 0.001026806992 |
| 79 | data_integrity | - delinq_max_6m: 0.001027 and 0.004737 . | 0.004737 | ratio | csi |  | eq | `[[art:35990a39:csi.delinq_max_6m]]` | verified | 0.00473710965 |
| 80 | data_integrity | The timing screen reports 0.0 features declared as during_pe… | 0 | count | n_flagged |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 81 | data_integrity | The strongest single feature reaches an area under the curve… | 0.728 | ratio | max_single_feature_auc |  | eq | `[[art:2e212f3a:leakage.target_corr.max_single_feature_auc]]` | verified | 0.7279795601 |
| 82 | data_integrity | The strongest single feature reaches an area under the curve… | 0.9 | ratio | single_feature_auc |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 83 | data_integrity | The name screen matched 0.0 feature names against the target… | 0 | count | n_matched |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 84 | data_integrity | The share of test rows whose feature values also appear in t… | 0.01256 | ratio | overlap | test | eq | `[[art:ebd7ff30:leakage.overlap]]` | verified | 0.01255555556 |
| 85 | data_integrity | The share of test rows whose feature values also appear in t… | 0.01256 | ratio | overlap.features | test | eq | `[[art:517f3049:leakage.overlap.features]]` | verified | 0.01255555556 |
| 86 | data_integrity | The share of test rows whose feature values also appear in t… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 87 | data_integrity | First, overlap on the declared identifier is 0.0 , so no cli… | 0 | ratio | overlap.ids |  | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 88 | data_integrity | Second, the share of train rows whose feature values are not… | 0.01162 | ratio | duplicates | train | eq | `[[art:c988bb0e:leakage.duplicates.train]]` | verified | 0.01161904762 |
| 89 | outcomes | This section reports discrimination before calibration, beca… | 0.2212 | ratio | event_rate | test | eq | `[[art:f60ae2a7:metrics.test.event_rate]]` | verified | 0.2212222222 |
| 90 | outcomes | This section reports discrimination before calibration, beca… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 91 | outcomes | \| Observations \| 21000 \| 9000 \| | 21000 | count | n | train | eq | `[[art:1721ceae:metrics.train.n]]` | verified | 21000 |
| 92 | outcomes | \| Observations \| 21000 \| 9000 \| | 9000 | count | n | test | eq | `[[art:5367a59f:metrics.test.n]]` | verified | 9000 |
| 93 | outcomes | \| AUC \| 0.7546 \| 0.755 \| | 0.7546 | ratio | auc | train | eq | `[[art:01cf8178:metrics.train.auc]]` | verified | 0.7545552576 |
| 94 | outcomes | \| AUC \| 0.7546 \| 0.755 \| | 0.755 | ratio | auc | test | eq | `[[art:365b7034:metrics.test.auc]]` | verified | 0.7550239453 |
| 95 | outcomes | \| Gini \| 0.5091 \| 0.51 \| | 0.5091 | ratio | gini | train | eq | `[[art:eaaf0f79:metrics.train.gini]]` | verified | 0.5091105152 |
| 96 | outcomes | \| Gini \| 0.5091 \| 0.51 \| | 0.51 | ratio | gini | test | eq | `[[art:296bfeeb:metrics.test.gini]]` | verified | 0.5100478906 |
| 97 | outcomes | \| KS \| 0.4144 \| 0.4067 \| | 0.4144 | ratio | ks | train | eq | `[[art:18df22bd:metrics.train.ks]]` | verified | 0.4144375385 |
| 98 | outcomes | \| KS \| 0.4144 \| 0.4067 \| | 0.4067 | ratio | ks | test | eq | `[[art:d3c4ed61:metrics.test.ks]]` | verified | 0.4066831201 |
| 99 | outcomes | \| Log loss \| 0.4439 \| 0.4442 \| | 0.4439 | ratio | logloss | train | eq | `[[art:b816b083:metrics.train.logloss]]` | verified | 0.4439401117 |
| 100 | outcomes | \| Log loss \| 0.4439 \| 0.4442 \| | 0.4442 | ratio | logloss | test | eq | `[[art:2de58c1b:metrics.test.logloss]]` | verified | 0.4441654047 |
| 101 | outcomes | \| Brier score \| 0.1384 \| 0.1385 \| | 0.1384 | ratio | brier | train | eq | `[[art:c95106e9:metrics.train.brier]]` | verified | 0.1383762773 |
| 102 | outcomes | \| Brier score \| 0.1384 \| 0.1385 \| | 0.1385 | ratio | brier | test | eq | `[[art:86e93c8f:metrics.test.brier]]` | verified | 0.1385162411 |
| 103 | outcomes | \| Event rate \| 0.2212 \| 0.2212 \| | 0.2212 | ratio | event_rate | train | eq | `[[art:657aa7fc:metrics.train.event_rate]]` | verified | 0.2211904762 |
| 104 | outcomes | \| Event rate \| 0.2212 \| 0.2212 \| | 0.2212 | ratio | event_rate | test | eq | `[[art:f60ae2a7:metrics.test.event_rate]]` | verified | 0.2212222222 |
| 105 | outcomes | \| Mean predicted probability \| 0.2212 \| 0.2206 \| | 0.2212 | ratio | mean_predicted | train | eq | `[[art:935d2cb7:metrics.train.mean_predicted]]` | verified | 0.2212248699 |
| 106 | outcomes | \| Mean predicted probability \| 0.2212 \| 0.2206 \| | 0.2206 | ratio | mean_predicted | test | eq | `[[art:89d241ea:metrics.test.mean_predicted]]` | verified | 0.2205710384 |
| 107 | outcomes | \| Share of events in the top two deciles \| 0.5031 \| 0.4952 \| | 0.5031 | ratio | top2_capture | train | eq | `[[art:5131afa7:deciles.train.top2_capture]]` | verified | 0.5031216362 |
| 108 | outcomes | \| Share of events in the top two deciles \| 0.5031 \| 0.4952 \| | 0.4952 | ratio | top2_capture | test | eq | `[[art:e2c0ad9f:deciles.test.top2_capture]]` | verified | 0.4952285284 |
| 109 | outcomes | The top two test deciles capture 0.4952 of test events, agai… | 0.4952 | ratio | top2_capture | test | eq | `[[art:e2c0ad9f:deciles.test.top2_capture]]` | verified | 0.4952285284 |
| 110 | outcomes | The top two test deciles capture 0.4952 of test events, agai… | 0.5031 | ratio | top2_capture | train | eq | `[[art:5131afa7:deciles.train.top2_capture]]` | verified | 0.5031216362 |
| 111 | outcomes | The declared bound on the train-to-test AUC gap under rule O… | 0.08 | ratio | auc_gap |  | eq | `[[art:630f28f4:threshold.O1.auc_gap]]` | verified | 0.08 |
| 112 | outcomes | Test AUC, 0.755 , is not below train AUC, 0.7546 , so the ga… | 0.755 | ratio | auc | test | eq | `[[art:365b7034:metrics.test.auc]]` | verified | 0.7550239453 |
| 113 | outcomes | Test AUC, 0.755 , is not below train AUC, 0.7546 , so the ga… | 0.7546 | ratio | auc | train | eq | `[[art:01cf8178:metrics.train.auc]]` | verified | 0.7545552576 |
| 114 | outcomes | The calibration slope from the logistic regression of the ou… | 0.9886 | ratio | calibration_slope | test | eq | `[[art:e06564c7:calibration_slope.test]]` | verified | 0.9885680158 |
| 115 | outcomes | The calibration slope from the logistic regression of the ou… | 1.001 | ratio | calibration_slope | train | eq | `[[art:85461245:calibration_slope.train]]` | verified | 1.000539237 |
| 116 | outcomes | The calibration slope from the logistic regression of the ou… | 0.8 | ratio | calibration_slope |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 117 | outcomes | The calibration slope from the logistic regression of the ou… | 1.2 | ratio | calibration_slope |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 118 | outcomes | The corresponding intercept is -0.008632 on test and 0.00037… | -0.008632 | ratio | calibration_intercept | test | eq | `[[art:2ee976d3:calibration_intercept.test]]` | verified | -0.008632158167 |
| 119 | outcomes | The corresponding intercept is -0.008632 on test and 0.00037… | 0.0003779 | ratio | calibration_intercept | train | eq | `[[art:2ce8cd09:calibration_intercept.train]]` | verified | 0.0003779479547 |
| 120 | outcomes | The mean predicted probability on test, 0.2206 , sits just u… | 0.2206 | ratio | mean_predicted | test | eq | `[[art:89d241ea:metrics.test.mean_predicted]]` | verified | 0.2205710384 |
| 121 | outcomes | The mean predicted probability on test, 0.2206 , sits just u… | 0.2212 | ratio | event_rate | test | eq | `[[art:f60ae2a7:metrics.test.event_rate]]` | verified | 0.2212222222 |
| 122 | outcomes | The relative gap between mean predicted and observed is 0.00… | 0.002944 | ratio | mean_rel_gap | test | eq | `[[art:bae28fd6:calibration.mean_rel_gap.test]]` | verified | 0.00294357342 |
| 123 | outcomes | The relative gap between mean predicted and observed is 0.00… | 0.0001555 | ratio | mean_rel_gap | train | eq | `[[art:a03ea014:calibration.mean_rel_gap.train]]` | verified | 0.0001554936592 |
| 124 | outcomes | The relative gap between mean predicted and observed is 0.00… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 125 | outcomes | \| Test AUC, minimum \| 0.7 \| 0.755 \| Pass \| | 0.7 | ratio | auc | test | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 126 | outcomes | \| Test AUC, minimum \| 0.7 \| 0.755 \| Pass \| | 0.755 | ratio | auc | test | eq | `[[art:365b7034:metrics.test.auc]]` | verified | 0.7550239453 |
| 127 | outcomes | \| Test Brier score, maximum \| 0.2 \| 0.1385 \| Pass \| | 0.2 | ratio | brier | test | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 128 | outcomes | \| Test Brier score, maximum \| 0.2 \| 0.1385 \| Pass \| | 0.1385 | ratio | brier | test | eq | `[[art:86e93c8f:metrics.test.brier]]` | verified | 0.1385162411 |
| 129 | outcomes | \| Test calibration slope, minimum \| 0.8 \| 0.9886 \| Pass \| | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 130 | outcomes | \| Test calibration slope, minimum \| 0.8 \| 0.9886 \| Pass \| | 0.9886 | ratio | calibration_slope | test | eq | `[[art:e06564c7:calibration_slope.test]]` | verified | 0.9885680158 |
| 131 | outcomes | \| Test calibration slope, maximum \| 1.2 \| 0.9886 \| Pass \| | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 132 | outcomes | \| Test calibration slope, maximum \| 1.2 \| 0.9886 \| Pass \| | 0.9886 | ratio | calibration_slope | test | eq | `[[art:e06564c7:calibration_slope.test]]` | verified | 0.9885680158 |
| 133 | outcomes | \| PSI, maximum \| 0.25 \| Not recomputed in the artifacts avai… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 134 | outcomes | \| Wall-clock seconds, maximum \| 300 \| Not recomputed in the… | 300 | ratio | max_seconds |  | eq | `[[art:3f4c6e97:threshold.package.max_seconds]]` | verified | 300 |
| 135 | sensitivity | The largest variance inflation factor across the retained fe… | 3.544 | ratio | vif |  | eq | `[[art:d3785ba9:vif.max]]` | verified | 3.54357449 |
| 136 | sensitivity | The largest variance inflation factor across the retained fe… | 10 | ratio | vif |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 137 | sensitivity | That maximum is attained by `delinq_count_6m`, whose varianc… | 3.544 | ratio | vif | train | eq | `[[art:7273e0be:vif.delinq_count_6m]]` | verified | 3.54357449 |
| 138 | sensitivity | Belsley's condition number of the column-standardised design… | 4.279 | ratio | condition_number |  | eq | `[[art:ba0d9cc4:condition_number]]` | verified | 4.279282985 |
| 139 | sensitivity | Belsley's condition number of the column-standardised design… | 30 | ratio | condition_number |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 140 | sensitivity | - `age`: 1.025 | 1.025 | ratio | vif | train | eq | `[[art:692cd6e9:vif.age]]` | verified | 1.024899403 |
| 141 | sensitivity | - `bill_mean_6m`: 2.265 | 2.265 | ratio | vif | train | eq | `[[art:87cb4e54:vif.bill_mean_6m]]` | verified | 2.264665681 |
| 142 | sensitivity | - `bill_trend_6m`: 1.330 | 1.33 | ratio | vif | train | eq | `[[art:6d3f01ce:vif.bill_trend_6m]]` | verified | 1.330477005 |
| 143 | sensitivity | - `delinq_count_6m`: 3.544 | 3.544 | ratio | vif | train | eq | `[[art:7273e0be:vif.delinq_count_6m]]` | verified | 3.54357449 |
| 144 | sensitivity | - `delinq_last`: 2.321 | 2.321 | ratio | vif | train | eq | `[[art:59461811:vif.delinq_last]]` | verified | 2.320694749 |
| 145 | sensitivity | - `delinq_max_6m`: 3.484 | 3.484 | ratio | vif | train | eq | `[[art:e7b701a1:vif.delinq_max_6m]]` | verified | 3.483514414 |
| 146 | sensitivity | - `limit_bal`: 2.097 | 2.097 | ratio | vif | train | eq | `[[art:0c6efb3f:vif.limit_bal]]` | verified | 2.096817173 |
| 147 | sensitivity | - `pay_ratio_last`: 2.714 | 2.714 | ratio | vif | train | eq | `[[art:b68613a6:vif.pay_ratio_last]]` | verified | 2.713577274 |
| 148 | sensitivity | - `pay_ratio_mean_6m`: 3.027 | 3.027 | ratio | vif | train | eq | `[[art:2cda5cfc:vif.pay_ratio_mean_6m]]` | verified | 3.026650797 |
| 149 | sensitivity | - `utilisation`: 2.829 | 2.829 | ratio | vif | train | eq | `[[art:6ce4c102:vif.utilisation]]` | verified | 2.829009901 |
| 150 | monitoring | - Discrimination: recompute AUC on each monitoring window an… | 0.7 | ratio | auc | test | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 151 | monitoring | - Discrimination: recompute AUC on each monitoring window an… | 0.755 | ratio | auc | test | eq | `[[art:365b7034:metrics.test.auc]]` | verified | 0.7550239453 |
| 152 | monitoring | - Calibration slope: refit the logistic regression of the re… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 153 | monitoring | - Calibration slope: refit the logistic regression of the re… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 154 | monitoring | - Calibration slope: refit the logistic regression of the re… | 0.9886 | ratio | calibration_slope | test | eq | `[[art:e06564c7:calibration_slope.test]]` | verified | 0.9885680158 |
| 155 | monitoring | - Calibration error: recompute the Brier score on each windo… | 0.2 | ratio | brier | test | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 156 | monitoring | - Input and score stability: recompute the largest PSI acros… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 157 | monitoring | - Input and score stability: recompute the largest PSI acros… | 0.003083 | ratio | psi |  | eq | `[[art:e1d82330:psi.max]]` | verified | 0.00308251646 |
| 158 | monitoring | - Realised event rate: track it each window, and when it fal… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 159 | monitoring | - Scoring runtime: track wall-clock time for the scoring run… | 300 | ratio | max_seconds |  | eq | `[[art:3f4c6e97:threshold.package.max_seconds]]` | verified | 300 |

## Appendix B — Artifact index

The store holds 124 artifacts; the 95 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
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
| `metrics.train.auc` | `01cf8178` | scalar | 0.7545552576 | auc on train, recomputed by quaestor |
| `metrics.train.brier` | `c95106e9` | scalar | 0.1383762773 | brier on train, recomputed by quaestor |
| `metrics.train.event_rate` | `657aa7fc` | scalar | 0.2211904762 | event_rate on train, recomputed by quaestor |
| `metrics.train.gini` | `eaaf0f79` | scalar | 0.5091105152 | gini on train, recomputed by quaestor |
| `metrics.train.ks` | `18df22bd` | scalar | 0.4144375385 | ks on train, recomputed by quaestor |
| `metrics.train.logloss` | `b816b083` | scalar | 0.4439401117 | logloss on train, recomputed by quaestor |
| `metrics.train.mean_predicted` | `935d2cb7` | scalar | 0.2212248699 | mean_predicted on train, recomputed by quaestor |
| `metrics.train.n` | `1721ceae` | scalar | 21000 | n on train, recomputed by quaestor |
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
| `threshold.C1.calibration_slope.max` | `b6672579` | scalar | 1.2 | C1: the top of the calibration slope band |
| `threshold.C1.calibration_slope.min` | `749634ae` | scalar | 0.8 | C1: the bottom of the calibration slope band |
| `threshold.C1.mean_ratio_rel` | `20e93a8c` | scalar | 0.25 | C1: mean predicted against observed, relative |
| `threshold.D1.missing_gap` | `9cce25ea` | scalar | 0.1 | D1: the missingness gap between splits, as a fraction |
| `threshold.E1.delta_auc` | `e042774c` | scalar | 0.03 | E1: the challenger's AUC lead over the champion |
| `threshold.L1.single_feature_auc` | `c29e7a34` | scalar | 0.9 | L1: the AUC one feature may reach on its own |
| `threshold.L2.overlap` | `9f336eaf` | scalar | 0.005 | L2: the fraction of test rows that may also be in train |
| `threshold.M1.condition_number` | `7e52fd7a` | scalar | 30 | M1: Belsley's condition number of the design (D-035) |
| `threshold.M1.vif` | `aeb4f33c` | scalar | 10 | M1: the variance inflation factor of any retained feature |
| `threshold.O1.auc_gap` | `630f28f4` | scalar | 0.08 | O1: the train-to-test AUC gap (D-050) |
| `threshold.S1.psi` | `278b9016` | scalar | 0.25 | S1: the population stability index, train against test (D-046) |
| `threshold.package.auc.test.min` | `8bfd02cc` | scalar | 0.7 | package.yaml declares auc min 0.7 |
| `threshold.package.brier.test.max` | `d0f98b9c` | scalar | 0.2 | package.yaml declares brier max 0.2 |
| `threshold.package.calibration_slope.test.max` | `0adb7a89` | scalar | 1.2 | package.yaml declares calibration_slope max 1.2 |
| `threshold.package.calibration_slope.test.min` | `95fdb848` | scalar | 0.8 | package.yaml declares calibration_slope min 0.8 |
| `threshold.package.max_seconds` | `3f4c6e97` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |
| `threshold.package.psi.max` | `fbb5a9d1` | scalar | 0.25 | package.yaml declares psi max 0.25 |
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
| tool calls | 13 (run_model 1, profile_data 1, compute_metrics 1, check_leakage 1, check_collinearity 1, challenger_compare 1, retrieve_guidance 7) |
| plan steps (bounded loop) | 1 |
| LLM calls | 19 (plan 1, draft 9, extract 9) |
| re-asks | 0 |
| repair rounds | 2 |
| tokens in / out | 38 / 104,675 |
| notional cost (USD) | 4.3822 |
| wall-clock (s) | 1217.79 |
| subject run (s) | 1.38 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| model | claude-cli |
| run id | credit_default-full_agent-d03b07c6 |

## Appendix D — Not checked

| item | reason |
|---|---|
| `check_stability` (R1) | package declares no `regime.column` |
| `run_scenarios` (X1) | not applicable to `binary_classification` |
| out-of-time and vintage-holdout metrics (O1, second rule) | package declares neither split |
| developer documentation | package has no `docs/` directory |
