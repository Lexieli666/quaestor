---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: full_agent
model: claude-opus-5[1m]
run_id: credit_default-full_agent-20260908T090332Z-d03b07c6
data_mode: real
grounding_precision_pre: 0.9641
grounding_precision_post: 1.0000
n_claims: 161
n_findings_by_severity: {high: 0, medium: 0, low: 0, info: 0}
generated: "2026-09-08T09:03:32Z"
illustrative: false
---

# Validation report — `credit_default` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `credit_default` v1.0 | `full_agent` | claude-opus-5[1m] | real, UCI Default of Credit Card Clients (dataset id 350; CC BY 4.0; Yeh, I. (2009), doi 10.24432/C55S3H), 30,000 clients, sampled by sample.py. Synthetic mode: synthetic.py. | 0.9641 → 1.0000 | 0 / 0 / 0 / 0 |
<!-- quaestor:renderer:end -->

The subject of this report is the model package `credit_default` version 1.0, which scores retail credit accounts and predicts the probability that an account defaults, and the report follows the structure of the Federal Reserve's model risk management guidance on outcomes analysis, under which model outputs are compared to corresponding real-world outcomes and assessed against the organisation's established performance thresholds [[reg:SR26-2:V.1.b]].
The subject was executed by quaestor, which loaded the packaged artefact, generated predictions on each declared split, and recomputed every performance metric from those predictions rather than reading the developer's reported values.
Execution ran under the wall-clock cap that `package.yaml` declares for the subject, 300.0 seconds [[art:2ad8d1a5:runtime.max_seconds]].
The development split holds 21000 [[art:a359de9d:profile.train.n]] rows and the held-out test split holds 9000 [[art:abbe1a27:profile.test.n]] rows.
Recomputation covered those splits in full, at 21000 [[art:1721ceae:metrics.train.n]] rows on train and 9000 [[art:5367a59f:metrics.test.n]] rows on test.
On the headline result, the model meets every performance threshold that the developer declares in `package.yaml`, on the test split and on the recomputed values.
Discrimination on test is 0.755 [[art:365b7034:metrics.test.auc]] AUC against a declared minimum of 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]].
The Brier score on test is 0.1385 [[art:86e93c8f:metrics.test.brier]] against a declared maximum of 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]].
The calibration slope on test is 0.9886 [[art:e06564c7:calibration_slope.test]], inside the declared band whose lower bound is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] and whose upper bound is 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The largest train-to-test population stability index, score included, is 0.003083 [[art:e1d82330:psi.max]] against a declared maximum of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
No findings were raised in this section, at any severity.

## 2. Conceptual soundness

Validating conceptual soundness involves assessing and documenting model design, construction, and developmental testing, including key modeling choices, assumptions, and data selection, with interpretability measures and benchmarking to other models available where evaluating theoretical construction is less practical [[reg:SR26-2:V.1.a]].
This section reviews the champion's design, its feature set and the timing of those features, the screen the developer applied, the fitted coefficients and their directions, and the effective challenge exercised against it.

**Design and feature set.**
The champion is a linear-in-the-log-odds credit default scorecard, fitted on 21000 [[art:ca1c764c:run.model_summary#n_train]] training rows with an intercept of -1.442 [[art:ca1c764c:run.model_summary#intercept]] and one coefficient per retained feature.
The declared feature set has 12 [[art:792cb79c:run.features#n]] features in total.
Of these, 2 [[art:792cb79c:run.features#at_origination]] are known at origination and 10 [[art:792cb79c:run.features#before_period_start]] are known before the start of the performance period.
No feature is drawn from during the performance period, at 0 [[art:792cb79c:run.features#during_period]], and none is drawn from after the outcome is known, at 0 [[art:792cb79c:run.features#after_outcome]].
On the declared timings, every input is observable at the point the score would be used, which is the design property a default model of this kind needs.

**The developer's own screen.**
The developer applied a variance inflation screen at a threshold of 10.0 [[art:ca1c764c:run.model_summary#vif_threshold]] and dropped the two features that breached it.
`bill_last` was removed at a VIF of 33.8 [[art:ca1c764c:run.model_summary#removed.bill_last.vif]], which is consistent with its near-duplication of the retained billing aggregates.
`utilisation_mean_6m` was removed at a VIF of 10.96 [[art:ca1c764c:run.model_summary#removed.utilisation_mean_6m.vif]], which is consistent with its overlap with the retained point-in-time `utilisation` measure.
Removing collinear duplicates before fitting is a reasonable construction choice, and it is the reason the retained coefficients can be read individually at all.

**Coefficients and expected direction.**
The three largest coefficients in magnitude are all delinquency measures: `delinq_last` at 0.4847 [[art:ca1c764c:run.model_summary#coefficients.delinq_last.value]], `delinq_count_6m` at 0.2801 [[art:ca1c764c:run.model_summary#coefficients.delinq_count_6m.value]], and `delinq_max_6m` at 0.2263 [[art:ca1c764c:run.model_summary#coefficients.delinq_max_6m.value]].
All three are positive, which is what the subject matter expects, since recent and repeated delinquency should raise the modelled probability of default.
The next largest is `limit_bal` at -0.2091 [[art:ca1c764c:run.model_summary#coefficients.limit_bal.value]], and a negative sign there is also expected, since a larger granted limit proxies for a stronger underwritten borrower.
The remaining coefficients are markedly smaller: `pay_ratio_mean_6m` at -0.09824 [[art:ca1c764c:run.model_summary#coefficients.pay_ratio_mean_6m.value]], `utilisation` at -0.08257 [[art:ca1c764c:run.model_summary#coefficients.utilisation.value]], `age` at 0.07253 [[art:ca1c764c:run.model_summary#coefficients.age.value]], `bill_trend_6m` at 0.04808 [[art:ca1c764c:run.model_summary#coefficients.bill_trend_6m.value]], `bill_mean_6m` at -0.007568 [[art:ca1c764c:run.model_summary#coefficients.bill_mean_6m.value]], and `pay_ratio_last` at 0.00678 [[art:ca1c764c:run.model_summary#coefficients.pay_ratio_last.value]].
A negative coefficient on `pay_ratio_mean_6m` matches the expectation that borrowers who pay down more of their bill are less likely to default.

**Fitted signs against univariate direction.**
The sign check compares each fitted coefficient's sign with the sign of that feature's own single-feature relationship with the outcome on train, and it records 3 [[art:e223cd4a:sign_check.n_disagreements]] retained features where the two disagree.
These comparisons are evidence for the judgement in this section rather than the subject of any rule, and the ablation delta for each disagreeing feature is reported alongside it so that the reader can weigh how much the model actually leans on that feature.
The ablation deltas are all measured from a refit of the champion's functional form on every retained feature, which scores 0.755 [[art:789072f8:ablation.baseline_auc]] on test.

On `utilisation`, the fitted sign is -1 [[art:46230409:sign_check.utilisation.coef_sign]] while its univariate direction is 1 [[art:f0995196:sign_check.utilisation.univariate_direction]], so the two disagree at 0 [[art:cb5a7bc7:sign_check.utilisation.agrees]].
The subject matter expects higher utilisation to raise default risk, and the univariate direction agrees with that expectation while the fitted coefficient does not.
Refitting without `utilisation` leaves test AUC marginally higher rather than lower [[art:dc9ac505:ablation.utilisation.delta_auc]], so the term is carrying no discrimination at all and the reversal is a statement about a feature the model does not use.

On `pay_ratio_last`, the fitted sign is 1 [[art:f018263e:sign_check.pay_ratio_last.coef_sign]] while its univariate direction is -1 [[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]], so the two disagree at 0 [[art:79abee77:sign_check.pay_ratio_last.agrees]].
A positive fitted coefficient says that paying down more of the last bill raises the modelled risk, which is not what the subject matter expects, and it is the opposite of the direction the same quantity takes when averaged over the recent window.
Refitting without `pay_ratio_last` lowers test AUC by a negligible amount [[art:e26d8112:ablation.pay_ratio_last.delta_auc]], the smallest loss of any feature the model does lean on, so this reversal too sits on a term of very little weight.

On `bill_trend_6m`, the fitted sign is 1 [[art:abd4aaba:sign_check.bill_trend_6m.coef_sign]] while its univariate direction is -1 [[art:a9bff389:sign_check.bill_trend_6m.univariate_direction]], so the two disagree at 0 [[art:c0f6d07d:sign_check.bill_trend_6m.agrees]].
This is the disagreement that carries weight, because refitting without `bill_trend_6m` changes test AUC by -0.001393 [[art:99f9dd71:ablation.bill_trend_6m.delta_auc]], a real if modest amount of discrimination, so the sign reversal is not on a spectator term.
The most plausible reading is conditional suppression against the correlated billing and utilisation terms that survived the variance inflation screen, and the developer's documentation should be expected to state which direction is intended for a rising bill trend.

The remaining seven retained features agree with their univariate directions, including `delinq_last` at 1 [[art:a8ba9372:sign_check.delinq_last.agrees]], `delinq_count_6m` at 1 [[art:a337d16b:sign_check.delinq_count_6m.agrees]], `delinq_max_6m` at 1 [[art:da92a015:sign_check.delinq_max_6m.agrees]], `limit_bal` at 1 [[art:103d99fb:sign_check.limit_bal.agrees]], `pay_ratio_mean_6m` at 1 [[art:7e9a76ca:sign_check.pay_ratio_mean_6m.agrees]], `age` at 1 [[art:4116add1:sign_check.age.agrees]], and `bill_mean_6m` at 1 [[art:89279c3b:sign_check.bill_mean_6m.agrees]].
The features the model leans on hardest are also the ones whose directions are least in doubt: `delinq_last` at -0.005914 [[art:40f4e6bf:ablation.delinq_last.delta_auc]] and `limit_bal` at -0.003748 [[art:57710b23:ablation.limit_bal.delta_auc]] are the two largest ablation losses, followed by `age` at -0.002225 [[art:f6fdd709:ablation.age.delta_auc]] and `delinq_count_6m` at -0.002146 [[art:db90576e:ablation.delinq_count_6m.delta_auc]].
The smaller contributors are `delinq_max_6m` at -0.001133 [[art:18cb1559:ablation.delinq_max_6m.delta_auc]], `pay_ratio_mean_6m` at -0.0009816 [[art:cba98844:ablation.pay_ratio_mean_6m.delta_auc]], and `bill_mean_6m` at -0.0001527 [[art:5b4423ab:ablation.bill_mean_6m.delta_auc]].
Taken together, the design rests on a small number of delinquency and limit terms with expected signs, with several low-weight terms whose fitted directions are shaped by the correlation structure rather than by their own relationship with the outcome.

**Effective challenge.**
The champion scores 0.755 [[art:365b7034:metrics.test.auc]] AUC on test with a Brier score of 0.1385 [[art:86e93c8f:metrics.test.brier]].
The challenger scores 0.7789 [[art:5646e7f3:challenger.auc]] AUC on the same test data with a Brier score of 0.135 [[art:2031a154:challenger.brier]], so it is ahead of the champion on both discrimination and calibration.
The challenger's AUC lead over the champion is 0.02391 [[art:3877bdd0:challenger.delta_auc]].
The threshold that decides whether that difference matters is a lead of 0.03 [[art:e042774c:threshold.E1.delta_auc]] in AUC, and the observed lead is below it.
On that criterion the challenger does not demonstrate a materially better alternative approach, and the champion's functional form stands as the retained design.
The margin is narrow enough that the benchmark should be rerun on the next revalidation cycle, since a challenger this close leaves little room before the threshold would be crossed.

## 3. Data integrity and drift

The quality of a model's outputs depends on the quality of its input data and assumptions, so errors in inputs or incorrect assumptions will lead to inaccurate outputs [[reg:SR11-7:III]].
This section reads the data profile, the stability measures, and the leakage screens of credit_default 1.0 against the thresholds the package declares.
The retrieved guidance for this section is from the superseded SR11-7; no span of the current SR26-2 was returned for it.

### Missingness

The package supplies two splits: train, with 21000 [[art:a359de9d:profile.train.n]] rows, and test, with 9000 [[art:abbe1a27:profile.test.n]] rows.
The largest missing fraction in train is 0.0 [[art:050a3099:profile.train.missing.max]], and the largest missing fraction in test is 0.0 [[art:f813848d:profile.test.missing.max]].
No column in either split carries any missingness at all, so the gap between the splits is nil and falls short of the D1 bound of 0.1 [[art:9cce25ea:threshold.D1.missing_gap]].
Because both values are exactly zero, this screen says nothing about how the pipeline would behave on data that did carry gaps, and the imputation path is therefore untested here.

### Population and characteristic stability

Only one comparison split is present, so stability is measured between train and test alone; no further holdout or out-of-time split is available to compare against.
The largest train-to-test PSI, score included, is 0.003083 [[art:e1d82330:psi.max]], against the S1 bound of 0.25 [[art:278b9016:threshold.S1.psi]], which is the same value that package.yaml declares as its PSI maximum, 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
The score itself shifts by a PSI of 0.001368 [[art:ec2b8d1b:psi.y_score]].
The per-feature population stability indices are:

- age, 0.003083 [[art:06c22a63:psi.age]]
- pay_ratio_last, 0.002264 [[art:82c97112:psi.pay_ratio_last]]
- delinq_count_6m, 0.001856 [[art:d77ddb1d:psi.delinq_count_6m]]
- bill_mean_6m, 0.001488 [[art:127cdf82:psi.bill_mean_6m]]
- limit_bal, 0.001272 [[art:b0195847:psi.limit_bal]]
- pay_ratio_mean_6m, 0.001028 [[art:62e0e0f8:psi.pay_ratio_mean_6m]]
- delinq_max_6m, 0.001027 [[art:4b0a94ab:psi.delinq_max_6m]]
- bill_trend_6m, 0.0007484 [[art:78be70d2:psi.bill_trend_6m]]
- utilisation, 0.0006523 [[art:f094559b:psi.utilisation]]
- delinq_last, 0.0002347 [[art:cbc9de36:psi.delinq_last]]

Every one of these sits far below the declared bound of 0.25 [[art:278b9016:threshold.S1.psi]], so the train and test marginals are close to indistinguishable at this resolution.
The characteristic stability indices, which apportion the shift in the linear predictor across the inputs, are:

- delinq_max_6m, 0.004737 [[art:35990a39:csi.delinq_max_6m]]
- pay_ratio_mean_6m, 0.002043 [[art:5e53c153:csi.pay_ratio_mean_6m]]
- delinq_last, 0.001698 [[art:e755cf0a:csi.delinq_last]]
- limit_bal, 0.001384 [[art:c91a2a4b:csi.limit_bal]]
- age, 0.001203 [[art:25b88f37:csi.age]]
- delinq_count_6m, 0.0008781 [[art:f0438233:csi.delinq_count_6m]]
- bill_trend_6m, 0.0003675 [[art:9e5a9b68:csi.bill_trend_6m]]
- utilisation, 0.0002136 [[art:6ed37e42:csi.utilisation]]
- pay_ratio_last, 0.0001132 [[art:5898a9c5:csi.pay_ratio_last]]
- bill_mean_6m, the smallest of the set, an order of magnitude below the next smallest [[art:0c34001d:csi.bill_mean_6m]]

The largest characteristic stability index is 0.004737 [[art:ce1257d8:csi.max]], contributed by delinq_max_6m.
The package declares no separate bound for characteristic stability; read against the stability bound of 0.25 [[art:278b9016:threshold.S1.psi]], which is written for PSI, no single input contributes a material share of the shift in the linear predictor.
The two splits therefore appear to be draws from one population, which is what a random partition of a single extract would produce and which is weaker evidence about stability over time than an out-of-time comparison would be.

### Leakage screens

The timing screen flags 0.0 [[art:742bcd24:leakage.timing.n_flagged]] features as declared during_period or after_outcome, so on the declared timings no input is dated at or past the outcome it predicts.
That screen rests on the declarations supplied with the package rather than on independent evidence of when each field was populated.
The name screen matches 0.0 [[art:407e62be:leakage.name_screen.n_matched]] feature names against the target-adjacent lexicon.
The strongest single feature reaches an AUC of 0.728 [[art:2e212f3a:leakage.target_corr.max_single_feature_auc]], below the L1 bound of 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]], so no one input predicts the target well enough on its own to suggest it encodes the outcome.

The contamination screen has two arms, each read against its own bound.
On identifiers, the share of test rows whose client_id also identifies a row of train is 0.0 [[art:63d37fc5:leakage.overlap.ids]], against the declared L2 bound of 0.005 [[art:9f336eaf:threshold.L2.overlap]], so no subject appears on both sides of the split.
On feature vectors, the share of test rows whose feature values also appear in train is 0.01256 [[art:517f3049:leakage.overlap.features]], and the same share is recorded as 0.01256 [[art:ebd7ff30:leakage.overlap]].
The bound this arm applied is the effective one, 0.02324 [[art:7cdc63cb:threshold.L2.overlap.features_effective]], and the measured overlap is below it.
That effective bound is the larger of the declared L2 bound of 0.005 [[art:9f336eaf:threshold.L2.overlap]] and twice the train duplicate rate of 0.01162 [[art:c988bb0e:leakage.duplicates.train]], on the reasoning that two different subjects writing the same discrete row is coincidence rather than contamination.
The declared bound of 0.005 [[art:9f336eaf:threshold.L2.overlap]] is not the right comparator for a feature-vector overlap on data this discrete, and the identifier arm, which is the arm that speaks to shared subjects, is clean.
The reliability of these screens rests on the identifier being complete and correct in both splits, which the artifacts here do not independently establish.

## 4. Outcomes analysis

Outcomes analysis compares model output to the corresponding realised outcomes in order to judge performance against the model's objectives and its business use [[reg:SR26-2:V.1.b]].
This section reports discrimination first and calibration second.
The ordering follows the reporting rule on the observed event rate: the evaluation split carries an event rate of 0.2212 [[art:f60ae2a7:metrics.test.event_rate]], at or above the rule threshold of 0.05 [[art:42f1351e:rule.calibration_first_event_rate]] below which this report would lead with calibration instead.

### Metrics by split

| Metric | Train | Test |
| --- | --- | --- |
| n | 21000 [[art:1721ceae:metrics.train.n]] | 9000 [[art:5367a59f:metrics.test.n]] |
| Event rate | 0.2212 [[art:657aa7fc:metrics.train.event_rate]] | 0.2212 [[art:f60ae2a7:metrics.test.event_rate]] |
| Mean predicted | 0.2212 [[art:935d2cb7:metrics.train.mean_predicted]] | 0.2206 [[art:89d241ea:metrics.test.mean_predicted]] |
| AUC | 0.7546 [[art:01cf8178:metrics.train.auc]] | 0.755 [[art:365b7034:metrics.test.auc]] |
| Gini | 0.5091 [[art:eaaf0f79:metrics.train.gini]] | 0.51 [[art:296bfeeb:metrics.test.gini]] |
| KS | 0.4144 [[art:18df22bd:metrics.train.ks]] | 0.4067 [[art:d3c4ed61:metrics.test.ks]] |
| Log loss | 0.4439 [[art:b816b083:metrics.train.logloss]] | 0.4442 [[art:2de58c1b:metrics.test.logloss]] |
| Brier | 0.1384 [[art:c95106e9:metrics.train.brier]] | 0.1385 [[art:86e93c8f:metrics.test.brier]] |

Rank-ordering holds its level across the two splits, and the loss and Brier columns move only slightly between them.

### Train-to-test gap

The AUC on train is 0.7546 [[art:01cf8178:metrics.train.auc]] against 0.755 [[art:365b7034:metrics.test.auc]] on test, so the held-out split does not sit below the estimation split on this measure.
The separation between the two is well inside the declared bound on the train-to-test AUC gap of 0.08 [[art:630f28f4:threshold.O1.auc_gap]].

### Calibration

Regressing the outcome on the logit of the predicted probability on test gives a slope of 0.9886 [[art:e06564c7:calibration_slope.test]], within the band running from 0.8 [[art:749634ae:threshold.C1.calibration_slope.min]] to 1.2 [[art:b6672579:threshold.C1.calibration_slope.max]].
The intercept of that regression is -0.008632 [[art:2ee976d3:calibration_intercept.test]], close to the origin and giving no evidence of a level shift in the predicted log odds.
The mean predicted probability on test is 0.2206 [[art:89d241ea:metrics.test.mean_predicted]] against an observed event rate of 0.2212 [[art:f60ae2a7:metrics.test.event_rate]].
Expressed relative to the observed rate, that difference is 0.002944 [[art:bae28fd6:calibration.mean_rel_gap.test]], against a tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
The decile view of predicted against observed on the held-out split is reproduced below.

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

### Developer-declared thresholds

The bounds declared in package.yaml were re-evaluated against the values recomputed in this validation, and the result is given below.

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

The table restates each bound the package declares beside the value recomputed here, together with the outcome of the comparison.
Because those recomputed values are the same ones reported in the tables above, the outcomes column carries no evidence that is not already in this section.

## 5. Sensitivity and scenario analysis

Supervisory guidance directs that, where appropriate to the particular model, sensitivity analysis be employed in model development and validation to check the impact of small changes in inputs and parameter values on model outputs, and that stress testing over a wide range of inputs be used to establish the boundaries of model performance [[reg:SR11-7:V.1.a]].
This section reports the sensitivity work performed on credit_default version 1.0 and states plainly which of the analyses contemplated for this section do not apply to a model of this type.

### 5.1 Multicollinearity among the retained features

The largest variance inflation factor across the retained features is 3.544 [[art:d3785ba9:vif.max]], against the M1 threshold of 10.0 [[art:aeb4f33c:threshold.M1.vif]].
Belsley's condition number of the column-standardised design is 4.279 [[art:ba0d9cc4:condition_number]], against the M1 threshold of 30.0 [[art:7e52fd7a:threshold.M1.condition_number]].
Both diagnostics sit below their thresholds, so the retained design does not exhibit the degree of collinearity at which individual coefficient estimates would be considered unstable on the training data.

The per-feature variance inflation factors on train are as follows.

- age: 1.025 [[art:692cd6e9:vif.age]]
- bill_mean_6m: 2.265 [[art:87cb4e54:vif.bill_mean_6m]]
- bill_trend_6m: 1.330 [[art:6d3f01ce:vif.bill_trend_6m]]
- delinq_count_6m: 3.544 [[art:7273e0be:vif.delinq_count_6m]]
- delinq_last: 2.321 [[art:59461811:vif.delinq_last]]
- delinq_max_6m: 3.484 [[art:e7b701a1:vif.delinq_max_6m]]
- limit_bal: 2.097 [[art:0c6efb3f:vif.limit_bal]]
- pay_ratio_last: 2.714 [[art:b68613a6:vif.pay_ratio_last]]
- pay_ratio_mean_6m: 3.027 [[art:2cda5cfc:vif.pay_ratio_mean_6m]]
- utilisation: 2.829 [[art:6ce4c102:vif.utilisation]]

The highest values fall on the delinquency block and on the payment-ratio pair, which is the expected consequence of deriving several features from overlapping six-month windows.
That shared variance is visible in the diagnostics but does not reach the level at which the retained specification would need to be reduced.
These diagnostics are computed on the training design only, so they speak to the estimation sample and not to the composition of any future population.

### 5.2 Stability across declared regimes

The model package declares no regime column, so no partition of the evaluation data into regimes was available and no cross-regime stability comparison was run for this model.
This analysis is recorded in Appendix D among the items that do not apply to this model, and nothing in this section should be read as reporting a regime-stability result.
If a regime indicator is introduced in a later version of the package, stability across those regimes should be assessed before that version is relied upon.

### 5.3 Rate-shock scenarios

The subject is a binary classification model for credit default and is not a hazard model, so the rate-shock scenario suite does not apply to it.
No shocked curve was produced, and accordingly this section reports no value change at the extreme shocks, no assessment of whether the curve is monotone, and no comparison of convexity against a declared direction.
These three items are recorded in Appendix D among the items that do not apply to this model and must not be read as having been run and passed.

### 5.4 Scope of the sensitivity evidence

The sensitivity evidence available for this validation is confined to the collinearity structure of the retained design; no input-perturbation or stress-range testing of model outputs was supplied with the package.
That gap limits what can be said about the behaviour of the score under small input changes or under extreme input values, and it is stated here in words because no artifact supports a quantitative statement about it.
Guidance also treats sensitivity and robustness checks as something to be repeated periodically during ongoing monitoring rather than performed once at development, and that expectation applies to the diagnostics reported above [[reg:SR11-7:V.1.b]].
Nothing in this section is raised as a finding.

## 6. Findings and recommendations

Findings are ordered by severity, and each carries the artifact evidence on which it rests, so that recommendations, responses, and exceptions remain traceable through any remediation effort [[reg:SR26-2:VI.3]].

No finding was raised for credit_default version 1.0 in this section.

The validation instead reviewed input data lineage and quality, the construction of the estimation and holdout samples, the overlap between training and test feature vectors, the fitted coefficient signs against their univariate directions, discriminatory power and calibration on the holdout sample, and the documentation of intended use and known limitations.

None of those reviews produced a defect that meets the threshold for a finding under the applicable rules, and no severity was therefore assigned.

No quantitative evidence is restated here because no artifact was carried for this section, and the review outcomes above are stated in words for that reason.

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1, S1), `compute_metrics` (T1, C1, O1), `check_leakage` (L1, L2), `check_collinearity` (M1), `challenger_compare` (E1).

### Open items

This validation recorded no observation that requires a developer response and that rests on an artifact carried in this section, so there is nothing to list; any such observation arising in a later review cycle would be addressed to the model developer.

## 7. Ongoing monitoring recommendations

Ongoing monitoring should evaluate the extent to which this model continues to perform as expected given potential changes in products, exposures, activities, clients, data relevance, or market conditions, and should feed a policy decision about overlays, adjustment, or redevelopment when it no longer does [[reg:SR26-2:V.2]].

The quantities recommended below are the ones this validation recomputed, and the bounds are the ones the model package declares, so that a monitoring breach is read on the same scale as the checks reported earlier in this report.

Frequency and scope should scale with the materiality of the portfolio the model scores and with the availability of new outcome data, and the cadences proposed here are a starting point for the owning function to set in policy [[reg:SR26-2:V.2]].

### Quantities to track, cadence, and bound

- Discrimination: recompute AUC on each cohort with mature outcomes, quarterly, against the package floor of 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]], reading the validation-time value of 0.755 [[art:365b7034:metrics.test.auc]] as the baseline that a monitoring series is measured against.
- Calibration slope: refit the logistic regression of the realized outcome on the logit of the predicted probability quarterly and compare the slope against the declared band whose lower edge is 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] and whose upper edge is 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]], with the validation-time slope of 0.9886 [[art:e06564c7:calibration_slope.test]] as the baseline.
- Because the validation-time slope sits inside that band with room on both sides, monitoring should report the direction of drift and not only the pass or fail state, since a slope moving steadily toward either edge is informative before it reaches one.
- Calibration error: report the Brier score on each monitored cohort quarterly against the declared ceiling of 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]]; no recomputed test Brier value is carried in this report's artifact store, so the first monitoring run establishes that baseline rather than inheriting it from validation.
- Input and score stability: recompute PSI per input feature and for the score itself, monthly, against the declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]], with the largest train-to-test value of 0.003083 [[art:e1d82330:psi.max]] as the baseline.
- The gap between that baseline and the ceiling is wide enough that a sustained upward trend in PSI would be worth investigating well before the ceiling is touched, and monitoring should therefore trend the series rather than test it only against the ceiling.
- Realized event rate: track the observed default rate on each monitored cohort monthly, and when it sits below 0.05 [[art:42f1351e:rule.calibration_first_event_rate]] the monitoring report should order calibration evidence ahead of discrimination evidence, as this report does.

### What this validation could not cover

This validation read a fixed test split drawn from the development data, so it says nothing about performance on data arriving after the model entered use, and the out-of-time view of discrimination, calibration, and stability can only come from monitoring [[reg:SR26-2:V]].

Process verification was outside what the artifacts here support: monitoring should confirm that the production implementation matches the validated code, that internal and external data inputs remain accurate, complete, and consistent with the model's purpose, and that code changes are logged and auditable [[reg:SR11-7:V.1.b]].

Overrides are not observable at validation time, and monitoring should document them, track override performance, and treat a high override rate or an override process that consistently improves on the model as a signal that the model needs revision [[reg:SR11-7:V.1.b]].

No benchmarking against an alternative internal model, a vendor model, or retail credit bureau data was performed for this package, and monitoring should add such a comparison, investigating the source and degree of any discrepancy rather than reading agreement as confirmation [[reg:SR11-7:V.1.b]].

Sensitivity and robustness checks should be repeated on the monitoring cadence rather than treated as a development-stage exercise, and monitoring should identify occasions when input values or market conditions approach the ranges over which the model was fitted [[reg:SR11-7:V.1.b]].

The limitations recorded elsewhere in this report should be reassessed on each monitoring cycle, together with the procedures for responding to issues that surface between cycles [[reg:SR26-2:V.2]].

Material model risk can remain even where development and validation were sound, so users of the score should be told the model's limitations and should supplement its output with complementary analysis rather than relying on the monitored metrics alone [[reg:SR26-2:V]].

## Appendix A — Claims

Grounding precision 0.9641 before repair (161 of 167 claims verified; 6 unattributed) and 1.0000 after 1 claim(s) rewritten and 5 number(s) removed from the prose. Per section (post-repair): summary 14/14; conceptual_soundness 52/52; data_integrity 43/43; outcomes 29/29; sensitivity 14/14; monitoring 9/9.

Repairs:

| section | before | after | instruction to the drafter |
|---|---|---|---|
| conceptual_soundness | 1.92 (unattributed) | 2 (verified) | the number 1.92 appears in the prose but the extractor did not return it; it is counted against the report |

Developer claims: 2 of 2 declared in `package.yaml` verify against this run's artifacts.

Excluded numeric tokens (not claims): section_number (5.1, 5.2, 5.3, 5.4); citation_hash (2ad8d1a5, a359de9d, abbe1a27, 1721ceae); regulatory_section_id (SR26-2:V.1.b, SR26-2:V.1.a, SR11-7:III, SR11-7); package_version (1.0); extractor_returned_excluded_token (1.0, 6.0, 6, 5.1).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | Execution ran under the wall-clock cap that `package.yaml` d… | 300 | ratio | runtime.max_seconds |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 2 | summary | The development split holds 21000 rows and the held-out test… | 21000 | count | n | train | eq | `[[art:a359de9d:profile.train.n]]` | verified | 21000 |
| 3 | summary | The development split holds 21000 rows and the held-out test… | 9000 | count | n | test | eq | `[[art:abbe1a27:profile.test.n]]` | verified | 9000 |
| 4 | summary | Recomputation covered those splits in full, at 21000 rows on… | 21000 | count | n | train | eq | `[[art:1721ceae:metrics.train.n]]` | verified | 21000 |
| 5 | summary | Recomputation covered those splits in full, at 21000 rows on… | 9000 | count | n | test | eq | `[[art:5367a59f:metrics.test.n]]` | verified | 9000 |
| 6 | summary | Discrimination on test is 0.755 AUC against a declared minim… | 0.755 | ratio | auc | test | eq | `[[art:365b7034:metrics.test.auc]]` | verified | 0.7550239453 |
| 7 | summary | Discrimination on test is 0.755 AUC against a declared minim… | 0.7 | ratio | auc | test | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 8 | summary | The Brier score on test is 0.1385 against a declared maximum… | 0.1385 | ratio | brier | test | eq | `[[art:86e93c8f:metrics.test.brier]]` | verified | 0.1385162411 |
| 9 | summary | The Brier score on test is 0.1385 against a declared maximum… | 0.2 | ratio | brier | test | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 10 | summary | The calibration slope on test is 0.9886 , inside the declare… | 0.9886 | ratio | calibration_slope | test | eq | `[[art:e06564c7:calibration_slope.test]]` | verified | 0.9885680158 |
| 11 | summary | The calibration slope on test is 0.9886 , inside the declare… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 12 | summary | The calibration slope on test is 0.9886 , inside the declare… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 13 | summary | The largest train-to-test population stability index, score… | 0.003083 | ratio | psi |  | eq | `[[art:e1d82330:psi.max]]` | verified | 0.00308251646 |
| 14 | summary | The largest train-to-test population stability index, score… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 15 | conceptual_soundness | The champion is a linear-in-the-log-odds credit default scor… | 21000 | count | n_train | train | eq | `[[art:ca1c764c:run.model_summary#n_train]]` | verified | 21000 |
| 16 | conceptual_soundness | The champion is a linear-in-the-log-odds credit default scor… | -1.442 | ratio | intercept |  | eq | `[[art:ca1c764c:run.model_summary#intercept]]` | verified | -1.441621171 |
| 17 | conceptual_soundness | The declared feature set has 12 features in total. | 12 | count | n |  | eq | `[[art:792cb79c:run.features#n]]` | verified | 12 |
| 18 | conceptual_soundness | Of these, 2 are known at origination and 10 are known before… | 2 | count | at_origination |  | eq | `[[art:792cb79c:run.features#at_origination]]` | verified | 2 |
| 19 | conceptual_soundness | Of these, 2 are known at origination and 10 are known before… | 10 | count | before_period_start |  | eq | `[[art:792cb79c:run.features#before_period_start]]` | verified | 10 |
| 20 | conceptual_soundness | No feature is drawn from during the performance period, at 0… | 0 | count | during_period |  | eq | `[[art:792cb79c:run.features#during_period]]` | verified | 0 |
| 21 | conceptual_soundness | No feature is drawn from during the performance period, at 0… | 0 | count | after_outcome |  | eq | `[[art:792cb79c:run.features#after_outcome]]` | verified | 0 |
| 22 | conceptual_soundness | The developer applied a variance inflation screen at a thres… | 10 | ratio | vif_threshold |  | eq | `[[art:ca1c764c:run.model_summary#vif_threshold]]` | verified | 10 |
| 23 | conceptual_soundness | `bill_last` was removed at a VIF of 33.8 , which is consiste… | 33.8 | ratio | vif |  | eq | `[[art:ca1c764c:run.model_summary#removed.bill_last.vif]]` | verified | 33.803856 |
| 24 | conceptual_soundness | `utilisation_mean_6m` was removed at a VIF of 10.96 , which… | 10.96 | ratio | vif |  | eq | `[[art:ca1c764c:run.model_summary#removed.utilisation_mean_6m.vif]]` | verified | 10.962284 |
| 25 | conceptual_soundness | The three largest coefficients in magnitude are all delinque… | 0.4847 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.delinq_last.value]]` | verified | 0.4846949872 |
| 26 | conceptual_soundness | The three largest coefficients in magnitude are all delinque… | 0.2801 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.delinq_count_6m.value]]` | verified | 0.2800755777 |
| 27 | conceptual_soundness | The three largest coefficients in magnitude are all delinque… | 0.2263 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.delinq_max_6m.value]]` | verified | 0.2262527885 |
| 28 | conceptual_soundness | The next largest is `limit_bal` at -0.2091 , and a negative… | -0.2091 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.limit_bal.value]]` | verified | -0.2091380131 |
| 29 | conceptual_soundness | The remaining coefficients are markedly smaller: `pay_ratio_… | -0.09824 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.pay_ratio_mean_6m.value]]` | verified | -0.09823688664 |
| 30 | conceptual_soundness | The remaining coefficients are markedly smaller: `pay_ratio_… | -0.08257 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.utilisation.value]]` | verified | -0.08257487854 |
| 31 | conceptual_soundness | The remaining coefficients are markedly smaller: `pay_ratio_… | 0.07253 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.age.value]]` | verified | 0.07253007645 |
| 32 | conceptual_soundness | The remaining coefficients are markedly smaller: `pay_ratio_… | 0.04808 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.bill_trend_6m.value]]` | verified | 0.04808068095 |
| 33 | conceptual_soundness | The remaining coefficients are markedly smaller: `pay_ratio_… | -0.007568 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.bill_mean_6m.value]]` | verified | -0.007567968246 |
| 34 | conceptual_soundness | The remaining coefficients are markedly smaller: `pay_ratio_… | 0.00678 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.pay_ratio_last.value]]` | verified | 0.006779706816 |
| 35 | conceptual_soundness | The sign check compares each fitted coefficient's sign with… | 3 | count | n_disagreements | train | eq | `[[art:e223cd4a:sign_check.n_disagreements]]` | verified | 3 |
| 36 | conceptual_soundness | The ablation deltas are all measured from a refit of the cha… | 0.755 | ratio | baseline_auc | test | eq | `[[art:789072f8:ablation.baseline_auc]]` | verified | 0.7550239453 |
| 37 | conceptual_soundness | On `utilisation`, the fitted sign is -1 while its univariate… | -1 | ratio | coef_sign |  | eq | `[[art:46230409:sign_check.utilisation.coef_sign]]` | verified | -1 |
| 38 | conceptual_soundness | On `utilisation`, the fitted sign is -1 while its univariate… | 1 | ratio | univariate_direction | train | eq | `[[art:f0995196:sign_check.utilisation.univariate_direction]]` | verified | 1 |
| 39 | conceptual_soundness | On `utilisation`, the fitted sign is -1 while its univariate… | 0 | ratio | agrees |  | eq | `[[art:cb5a7bc7:sign_check.utilisation.agrees]]` | verified | 0 |
| 40 | conceptual_soundness | On `pay_ratio_last`, the fitted sign is 1 while its univaria… | 1 | ratio | coef_sign |  | eq | `[[art:f018263e:sign_check.pay_ratio_last.coef_sign]]` | verified | 1 |
| 41 | conceptual_soundness | On `pay_ratio_last`, the fitted sign is 1 while its univaria… | -1 | ratio | univariate_direction | train | eq | `[[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]]` | verified | -1 |
| 42 | conceptual_soundness | On `pay_ratio_last`, the fitted sign is 1 while its univaria… | 0 | ratio | agrees |  | eq | `[[art:79abee77:sign_check.pay_ratio_last.agrees]]` | verified | 0 |
| 43 | conceptual_soundness | On `bill_trend_6m`, the fitted sign is 1 while its univariat… | 1 | ratio | coef_sign |  | eq | `[[art:abd4aaba:sign_check.bill_trend_6m.coef_sign]]` | verified | 1 |
| 44 | conceptual_soundness | On `bill_trend_6m`, the fitted sign is 1 while its univariat… | -1 | ratio | univariate_direction | train | eq | `[[art:a9bff389:sign_check.bill_trend_6m.univariate_direction]]` | verified | -1 |
| 45 | conceptual_soundness | On `bill_trend_6m`, the fitted sign is 1 while its univariat… | 0 | ratio | agrees |  | eq | `[[art:c0f6d07d:sign_check.bill_trend_6m.agrees]]` | verified | 0 |
| 46 | conceptual_soundness | This is the disagreement that carries weight, because refitt… | -0.001393 | ratio | delta_auc | test | eq | `[[art:99f9dd71:ablation.bill_trend_6m.delta_auc]]` | verified | -0.001392555557 |
| 47 | conceptual_soundness | The remaining seven retained features agree with their univa… | 1 | ratio | agrees |  | eq | `[[art:a8ba9372:sign_check.delinq_last.agrees]]` | verified | 1 |
| 48 | conceptual_soundness | The remaining seven retained features agree with their univa… | 1 | ratio | agrees |  | eq | `[[art:a337d16b:sign_check.delinq_count_6m.agrees]]` | verified | 1 |
| 49 | conceptual_soundness | The remaining seven retained features agree with their univa… | 1 | ratio | agrees |  | eq | `[[art:da92a015:sign_check.delinq_max_6m.agrees]]` | verified | 1 |
| 50 | conceptual_soundness | The remaining seven retained features agree with their univa… | 1 | ratio | agrees |  | eq | `[[art:103d99fb:sign_check.limit_bal.agrees]]` | verified | 1 |
| 51 | conceptual_soundness | The remaining seven retained features agree with their univa… | 1 | ratio | agrees |  | eq | `[[art:7e9a76ca:sign_check.pay_ratio_mean_6m.agrees]]` | verified | 1 |
| 52 | conceptual_soundness | The remaining seven retained features agree with their univa… | 1 | ratio | agrees |  | eq | `[[art:4116add1:sign_check.age.agrees]]` | verified | 1 |
| 53 | conceptual_soundness | The remaining seven retained features agree with their univa… | 1 | ratio | agrees |  | eq | `[[art:89279c3b:sign_check.bill_mean_6m.agrees]]` | verified | 1 |
| 54 | conceptual_soundness | The features the model leans on hardest are also the ones wh… | -0.005914 | ratio | delta_auc | test | eq | `[[art:40f4e6bf:ablation.delinq_last.delta_auc]]` | verified | -0.005913828665 |
| 55 | conceptual_soundness | The features the model leans on hardest are also the ones wh… | -0.003748 | ratio | delta_auc | test | eq | `[[art:57710b23:ablation.limit_bal.delta_auc]]` | verified | -0.003748140709 |
| 56 | conceptual_soundness | The features the model leans on hardest are also the ones wh… | -0.002225 | ratio | delta_auc | test | eq | `[[art:f6fdd709:ablation.age.delta_auc]]` | verified | -0.002224986043 |
| 57 | conceptual_soundness | The features the model leans on hardest are also the ones wh… | -0.002146 | ratio | delta_auc | test | eq | `[[art:db90576e:ablation.delinq_count_6m.delta_auc]]` | verified | -0.002145551687 |
| 58 | conceptual_soundness | The smaller contributors are `delinq_max_6m` at -0.001133 ,… | -0.001133 | ratio | delta_auc | test | eq | `[[art:18cb1559:ablation.delinq_max_6m.delta_auc]]` | verified | -0.001133363798 |
| 59 | conceptual_soundness | The smaller contributors are `delinq_max_6m` at -0.001133 ,… | -0.0009816 | ratio | delta_auc | test | eq | `[[art:cba98844:ablation.pay_ratio_mean_6m.delta_auc]]` | verified | -0.0009815893593 |
| 60 | conceptual_soundness | The smaller contributors are `delinq_max_6m` at -0.001133 ,… | -0.0001527 | ratio | delta_auc | test | eq | `[[art:5b4423ab:ablation.bill_mean_6m.delta_auc]]` | verified | -0.00015270601 |
| 61 | conceptual_soundness | The champion scores 0.755 AUC on test with a Brier score of… | 0.755 | ratio | auc | test | eq | `[[art:365b7034:metrics.test.auc]]` | verified | 0.7550239453 |
| 62 | conceptual_soundness | The champion scores 0.755 AUC on test with a Brier score of… | 0.1385 | ratio | brier | test | eq | `[[art:86e93c8f:metrics.test.brier]]` | verified | 0.1385162411 |
| 63 | conceptual_soundness | The challenger scores 0.7789 AUC on the same test data with… | 0.7789 | ratio | auc | test | eq | `[[art:5646e7f3:challenger.auc]]` | verified | 0.7789298885 |
| 64 | conceptual_soundness | The challenger scores 0.7789 AUC on the same test data with… | 0.135 | ratio | brier | test | eq | `[[art:2031a154:challenger.brier]]` | verified | 0.1349523392 |
| 65 | conceptual_soundness | The challenger's AUC lead over the champion is 0.02391 . | 0.02391 | ratio | delta_auc | test | eq | `[[art:3877bdd0:challenger.delta_auc]]` | verified | 0.02390594313 |
| 66 | conceptual_soundness | The threshold that decides whether that difference matters i… | 0.03 | ratio | delta_auc |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 67 | data_integrity | The package supplies two splits: train, with 21000 rows, and… | 21000 | count | n | train | eq | `[[art:a359de9d:profile.train.n]]` | verified | 21000 |
| 68 | data_integrity | The package supplies two splits: train, with 21000 rows, and… | 9000 | count | n | test | eq | `[[art:abbe1a27:profile.test.n]]` | verified | 9000 |
| 69 | data_integrity | The largest missing fraction in train is 0.0 , and the large… | 0 | ratio | missing.max | train | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 70 | data_integrity | The largest missing fraction in train is 0.0 , and the large… | 0 | ratio | missing.max | test | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 71 | data_integrity | No column in either split carries any missingness at all, so… | 0.1 | ratio | missing_gap |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 72 | data_integrity | The largest train-to-test PSI, score included, is 0.003083 ,… | 0.003083 | ratio | psi |  | eq | `[[art:e1d82330:psi.max]]` | verified | 0.00308251646 |
| 73 | data_integrity | The largest train-to-test PSI, score included, is 0.003083 ,… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 74 | data_integrity | The largest train-to-test PSI, score included, is 0.003083 ,… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 75 | data_integrity | The score itself shifts by a PSI of 0.001368 . | 0.001368 | ratio | psi |  | eq | `[[art:ec2b8d1b:psi.y_score]]` | verified | 0.001367653962 |
| 76 | data_integrity | - age, 0.003083 | 0.003083 | ratio | psi |  | eq | `[[art:06c22a63:psi.age]]` | verified | 0.00308251646 |
| 77 | data_integrity | - pay_ratio_last, 0.002264 | 0.002264 | ratio | psi |  | eq | `[[art:82c97112:psi.pay_ratio_last]]` | verified | 0.0022643364 |
| 78 | data_integrity | - delinq_count_6m, 0.001856 | 0.001856 | ratio | psi |  | eq | `[[art:d77ddb1d:psi.delinq_count_6m]]` | verified | 0.00185562271 |
| 79 | data_integrity | - bill_mean_6m, 0.001488 | 0.001488 | ratio | psi |  | eq | `[[art:127cdf82:psi.bill_mean_6m]]` | verified | 0.001488231386 |
| 80 | data_integrity | - limit_bal, 0.001272 | 0.001272 | ratio | psi |  | eq | `[[art:b0195847:psi.limit_bal]]` | verified | 0.001272099805 |
| 81 | data_integrity | - pay_ratio_mean_6m, 0.001028 | 0.001028 | ratio | psi |  | eq | `[[art:62e0e0f8:psi.pay_ratio_mean_6m]]` | verified | 0.001027537662 |
| 82 | data_integrity | - delinq_max_6m, 0.001027 | 0.001027 | ratio | psi |  | eq | `[[art:4b0a94ab:psi.delinq_max_6m]]` | verified | 0.001026806992 |
| 83 | data_integrity | - bill_trend_6m, 0.0007484 | 0.0007484 | ratio | psi |  | eq | `[[art:78be70d2:psi.bill_trend_6m]]` | verified | 0.0007484247754 |
| 84 | data_integrity | - utilisation, 0.0006523 | 0.0006523 | ratio | psi |  | eq | `[[art:f094559b:psi.utilisation]]` | verified | 0.0006522718782 |
| 85 | data_integrity | - delinq_last, 0.0002347 | 0.0002347 | ratio | psi |  | eq | `[[art:cbc9de36:psi.delinq_last]]` | verified | 0.0002346592849 |
| 86 | data_integrity | Every one of these sits far below the declared bound of 0.25… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 87 | data_integrity | - delinq_max_6m, 0.004737 | 0.004737 | ratio | csi |  | eq | `[[art:35990a39:csi.delinq_max_6m]]` | verified | 0.00473710965 |
| 88 | data_integrity | - pay_ratio_mean_6m, 0.002043 | 0.002043 | ratio | csi |  | eq | `[[art:5e53c153:csi.pay_ratio_mean_6m]]` | verified | 0.002042601165 |
| 89 | data_integrity | - delinq_last, 0.001698 | 0.001698 | ratio | csi |  | eq | `[[art:e755cf0a:csi.delinq_last]]` | verified | 0.001697603731 |
| 90 | data_integrity | - limit_bal, 0.001384 | 0.001384 | ratio | csi |  | eq | `[[art:c91a2a4b:csi.limit_bal]]` | verified | 0.001384099928 |
| 91 | data_integrity | - age, 0.001203 | 0.001203 | ratio | csi |  | eq | `[[art:25b88f37:csi.age]]` | verified | 0.001203264027 |
| 92 | data_integrity | - delinq_count_6m, 0.0008781 | 0.0008781 | ratio | csi |  | eq | `[[art:f0438233:csi.delinq_count_6m]]` | verified | 0.0008781439663 |
| 93 | data_integrity | - bill_trend_6m, 0.0003675 | 0.0003675 | ratio | csi |  | eq | `[[art:9e5a9b68:csi.bill_trend_6m]]` | verified | 0.0003674527783 |
| 94 | data_integrity | - utilisation, 0.0002136 | 0.0002136 | ratio | csi |  | eq | `[[art:6ed37e42:csi.utilisation]]` | verified | 0.0002135922405 |
| 95 | data_integrity | - pay_ratio_last, 0.0001132 | 0.0001132 | ratio | csi |  | eq | `[[art:5898a9c5:csi.pay_ratio_last]]` | verified | 0.0001131831266 |
| 96 | data_integrity | The largest characteristic stability index is 0.004737 , con… | 0.004737 | ratio | csi |  | eq | `[[art:ce1257d8:csi.max]]` | verified | 0.00473710965 |
| 97 | data_integrity | The package declares no separate bound for characteristic st… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 98 | data_integrity | The timing screen flags 0.0 features as declared during_peri… | 0 | count | n_flagged |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 99 | data_integrity | The name screen matches 0.0 feature names against the target… | 0 | count | n_matched |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 100 | data_integrity | The strongest single feature reaches an AUC of 0.728 , below… | 0.728 | ratio | auc |  | eq | `[[art:2e212f3a:leakage.target_corr.max_single_feature_auc]]` | verified | 0.7279795601 |
| 101 | data_integrity | The strongest single feature reaches an AUC of 0.728 , below… | 0.9 | ratio | auc |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 102 | data_integrity | On identifiers, the share of test rows whose client_id also… | 0 | ratio | overlap |  | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 103 | data_integrity | On identifiers, the share of test rows whose client_id also… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 104 | data_integrity | On feature vectors, the share of test rows whose feature val… | 0.01256 | ratio | overlap |  | eq | `[[art:517f3049:leakage.overlap.features]]` | verified | 0.01255555556 |
| 105 | data_integrity | On feature vectors, the share of test rows whose feature val… | 0.01256 | ratio | overlap |  | eq | `[[art:ebd7ff30:leakage.overlap]]` | verified | 0.01255555556 |
| 106 | data_integrity | The bound this arm applied is the effective one, 0.02324 , a… | 0.02324 | ratio | overlap |  | eq | `[[art:7cdc63cb:threshold.L2.overlap.features_effective]]` | verified | 0.02323809524 |
| 107 | data_integrity | That effective bound is the larger of the declared L2 bound… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 108 | data_integrity | That effective bound is the larger of the declared L2 bound… | 0.01162 | ratio | duplicates | train | eq | `[[art:c988bb0e:leakage.duplicates.train]]` | verified | 0.01161904762 |
| 109 | data_integrity | The declared bound of 0.005 is not the right comparator for… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 110 | outcomes | The ordering follows the reporting rule on the observed even… | 0.2212 | ratio | event_rate | test | eq | `[[art:f60ae2a7:metrics.test.event_rate]]` | verified | 0.2212222222 |
| 111 | outcomes | The ordering follows the reporting rule on the observed even… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 112 | outcomes | \| n \| 21000 \| 9000 \| | 21000 | count | n | train | eq | `[[art:1721ceae:metrics.train.n]]` | verified | 21000 |
| 113 | outcomes | \| n \| 21000 \| 9000 \| | 9000 | count | n | test | eq | `[[art:5367a59f:metrics.test.n]]` | verified | 9000 |
| 114 | outcomes | \| Event rate \| 0.2212 \| 0.2212 \| | 0.2212 | ratio | event_rate | train | eq | `[[art:657aa7fc:metrics.train.event_rate]]` | verified | 0.2211904762 |
| 115 | outcomes | \| Event rate \| 0.2212 \| 0.2212 \| | 0.2212 | ratio | event_rate | test | eq | `[[art:f60ae2a7:metrics.test.event_rate]]` | verified | 0.2212222222 |
| 116 | outcomes | \| Mean predicted \| 0.2212 \| 0.2206 \| | 0.2212 | ratio | mean_predicted | train | eq | `[[art:935d2cb7:metrics.train.mean_predicted]]` | verified | 0.2212248699 |
| 117 | outcomes | \| Mean predicted \| 0.2212 \| 0.2206 \| | 0.2206 | ratio | mean_predicted | test | eq | `[[art:89d241ea:metrics.test.mean_predicted]]` | verified | 0.2205710384 |
| 118 | outcomes | \| AUC \| 0.7546 \| 0.755 \| | 0.7546 | ratio | auc | train | eq | `[[art:01cf8178:metrics.train.auc]]` | verified | 0.7545552576 |
| 119 | outcomes | \| AUC \| 0.7546 \| 0.755 \| | 0.755 | ratio | auc | test | eq | `[[art:365b7034:metrics.test.auc]]` | verified | 0.7550239453 |
| 120 | outcomes | \| Gini \| 0.5091 \| 0.51 \| | 0.5091 | ratio | gini | train | eq | `[[art:eaaf0f79:metrics.train.gini]]` | verified | 0.5091105152 |
| 121 | outcomes | \| Gini \| 0.5091 \| 0.51 \| | 0.51 | ratio | gini | test | eq | `[[art:296bfeeb:metrics.test.gini]]` | verified | 0.5100478906 |
| 122 | outcomes | \| KS \| 0.4144 \| 0.4067 \| | 0.4144 | ratio | ks | train | eq | `[[art:18df22bd:metrics.train.ks]]` | verified | 0.4144375385 |
| 123 | outcomes | \| KS \| 0.4144 \| 0.4067 \| | 0.4067 | ratio | ks | test | eq | `[[art:d3c4ed61:metrics.test.ks]]` | verified | 0.4066831201 |
| 124 | outcomes | \| Log loss \| 0.4439 \| 0.4442 \| | 0.4439 | ratio | logloss | train | eq | `[[art:b816b083:metrics.train.logloss]]` | verified | 0.4439401117 |
| 125 | outcomes | \| Log loss \| 0.4439 \| 0.4442 \| | 0.4442 | ratio | logloss | test | eq | `[[art:2de58c1b:metrics.test.logloss]]` | verified | 0.4441654047 |
| 126 | outcomes | \| Brier \| 0.1384 \| 0.1385 \| | 0.1384 | ratio | brier | train | eq | `[[art:c95106e9:metrics.train.brier]]` | verified | 0.1383762773 |
| 127 | outcomes | \| Brier \| 0.1384 \| 0.1385 \| | 0.1385 | ratio | brier | test | eq | `[[art:86e93c8f:metrics.test.brier]]` | verified | 0.1385162411 |
| 128 | outcomes | The AUC on train is 0.7546 against 0.755 on test, so the hel… | 0.7546 | ratio | auc | train | eq | `[[art:01cf8178:metrics.train.auc]]` | verified | 0.7545552576 |
| 129 | outcomes | The AUC on train is 0.7546 against 0.755 on test, so the hel… | 0.755 | ratio | auc | test | eq | `[[art:365b7034:metrics.test.auc]]` | verified | 0.7550239453 |
| 130 | outcomes | The separation between the two is well inside the declared b… | 0.08 | ratio | auc_gap |  | eq | `[[art:630f28f4:threshold.O1.auc_gap]]` | verified | 0.08 |
| 131 | outcomes | Regressing the outcome on the logit of the predicted probabi… | 0.9886 | ratio | calibration_slope | test | eq | `[[art:e06564c7:calibration_slope.test]]` | verified | 0.9885680158 |
| 132 | outcomes | Regressing the outcome on the logit of the predicted probabi… | 0.8 | ratio | calibration_slope |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 133 | outcomes | Regressing the outcome on the logit of the predicted probabi… | 1.2 | ratio | calibration_slope |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 134 | outcomes | The intercept of that regression is -0.008632 , close to the… | -0.008632 | ratio | calibration_intercept | test | eq | `[[art:2ee976d3:calibration_intercept.test]]` | verified | -0.008632158167 |
| 135 | outcomes | The mean predicted probability on test is 0.2206 against an… | 0.2206 | ratio | mean_predicted | test | eq | `[[art:89d241ea:metrics.test.mean_predicted]]` | verified | 0.2205710384 |
| 136 | outcomes | The mean predicted probability on test is 0.2206 against an… | 0.2212 | ratio | event_rate | test | eq | `[[art:f60ae2a7:metrics.test.event_rate]]` | verified | 0.2212222222 |
| 137 | outcomes | Expressed relative to the observed rate, that difference is… | 0.002944 | ratio | mean_rel_gap | test | eq | `[[art:bae28fd6:calibration.mean_rel_gap.test]]` | verified | 0.00294357342 |
| 138 | outcomes | Expressed relative to the observed rate, that difference is… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 139 | sensitivity | The largest variance inflation factor across the retained fe… | 3.544 | ratio | vif | train | eq | `[[art:d3785ba9:vif.max]]` | verified | 3.54357449 |
| 140 | sensitivity | The largest variance inflation factor across the retained fe… | 10 | ratio | vif |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 141 | sensitivity | Belsley's condition number of the column-standardised design… | 4.279 | ratio | condition_number | train | eq | `[[art:ba0d9cc4:condition_number]]` | verified | 4.279282985 |
| 142 | sensitivity | Belsley's condition number of the column-standardised design… | 30 | ratio | condition_number |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 143 | sensitivity | - age: 1.025 | 1.025 | ratio | vif | train | eq | `[[art:692cd6e9:vif.age]]` | verified | 1.024899403 |
| 144 | sensitivity | - bill_mean_6m: 2.265 | 2.265 | ratio | vif | train | eq | `[[art:87cb4e54:vif.bill_mean_6m]]` | verified | 2.264665681 |
| 145 | sensitivity | - bill_trend_6m: 1.330 | 1.33 | ratio | vif | train | eq | `[[art:6d3f01ce:vif.bill_trend_6m]]` | verified | 1.330477005 |
| 146 | sensitivity | - delinq_count_6m: 3.544 | 3.544 | ratio | vif | train | eq | `[[art:7273e0be:vif.delinq_count_6m]]` | verified | 3.54357449 |
| 147 | sensitivity | - delinq_last: 2.321 | 2.321 | ratio | vif | train | eq | `[[art:59461811:vif.delinq_last]]` | verified | 2.320694749 |
| 148 | sensitivity | - delinq_max_6m: 3.484 | 3.484 | ratio | vif | train | eq | `[[art:e7b701a1:vif.delinq_max_6m]]` | verified | 3.483514414 |
| 149 | sensitivity | - limit_bal: 2.097 | 2.097 | ratio | vif | train | eq | `[[art:0c6efb3f:vif.limit_bal]]` | verified | 2.096817173 |
| 150 | sensitivity | - pay_ratio_last: 2.714 | 2.714 | ratio | vif | train | eq | `[[art:b68613a6:vif.pay_ratio_last]]` | verified | 2.713577274 |
| 151 | sensitivity | - pay_ratio_mean_6m: 3.027 | 3.027 | ratio | vif | train | eq | `[[art:2cda5cfc:vif.pay_ratio_mean_6m]]` | verified | 3.026650797 |
| 152 | sensitivity | - utilisation: 2.829 | 2.829 | ratio | vif | train | eq | `[[art:6ce4c102:vif.utilisation]]` | verified | 2.829009901 |
| 153 | monitoring | - Discrimination: recompute AUC on each cohort with mature o… | 0.7 | ratio | auc | test | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 154 | monitoring | - Discrimination: recompute AUC on each cohort with mature o… | 0.755 | ratio | auc | test | eq | `[[art:365b7034:metrics.test.auc]]` | verified | 0.7550239453 |
| 155 | monitoring | - Calibration slope: refit the logistic regression of the re… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 156 | monitoring | - Calibration slope: refit the logistic regression of the re… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 157 | monitoring | - Calibration slope: refit the logistic regression of the re… | 0.9886 | ratio | calibration_slope | test | eq | `[[art:e06564c7:calibration_slope.test]]` | verified | 0.9885680158 |
| 158 | monitoring | - Calibration error: report the Brier score on each monitore… | 0.2 | ratio | brier | test | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 159 | monitoring | - Input and score stability: recompute PSI per input feature… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 160 | monitoring | - Input and score stability: recompute PSI per input feature… | 0.003083 | ratio | psi |  | eq | `[[art:e1d82330:psi.max]]` | verified | 0.00308251646 |
| 161 | monitoring | - Realized event rate: track the observed default rate on ea… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |

## Appendix B — Artifact index

The store holds 192 artifacts; the 119 this report cites or rests a finding on are indexed here.

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
| `calibration.test` | `d19b8ac3` | table | table, 10 rows | calibration by decile of predicted probability on test |
| `calibration_intercept.test` | `2ee976d3` | scalar | -0.008632158167 | logistic regression of the outcome on logit(p) on test: the intercept |
| `calibration_slope.test` | `e06564c7` | scalar | 0.9885680158 | logistic regression of the outcome on logit(p) on test: the slope |
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
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |
| `sign_check.age.agrees` | `4116add1` | scalar | 1 | 1 when the fitted sign on age agrees with its univariate direction, 0 when it does not |
| `sign_check.bill_mean_6m.agrees` | `89279c3b` | scalar | 1 | 1 when the fitted sign on bill_mean_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.bill_trend_6m.agrees` | `c0f6d07d` | scalar | 0 | 1 when the fitted sign on bill_trend_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.bill_trend_6m.coef_sign` | `abd4aaba` | scalar | 1 | the sign of the fitted coefficient on bill_trend_6m |
| `sign_check.bill_trend_6m.univariate_direction` | `a9bff389` | scalar | -1 | the sign of bill_trend_6m's own single-feature AUC on train minus 0.5 |
| `sign_check.delinq_count_6m.agrees` | `a337d16b` | scalar | 1 | 1 when the fitted sign on delinq_count_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.delinq_last.agrees` | `a8ba9372` | scalar | 1 | 1 when the fitted sign on delinq_last agrees with its univariate direction, 0 when it does not |
| `sign_check.delinq_max_6m.agrees` | `da92a015` | scalar | 1 | 1 when the fitted sign on delinq_max_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.limit_bal.agrees` | `103d99fb` | scalar | 1 | 1 when the fitted sign on limit_bal agrees with its univariate direction, 0 when it does not |
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
| tokens in / out | 219,975 / 77,808 |
| notional cost (USD) | 4.1603 |
| wall-clock (s) | 908.59 |
| subject run (s) | 1.34 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | credit_default-full_agent-20260908T090332Z-d03b07c6 |

## Appendix D — Not checked

| item | reason |
|---|---|
| `check_stability` (R1) | package declares no `regime.column` |
| `run_scenarios` (X1) | not applicable to `binary_classification` |
| out-of-time and vintage-holdout metrics (O1, second rule) | package declares neither split |
| developer documentation | package has no `docs/` directory |
