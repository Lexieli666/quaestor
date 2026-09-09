---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: full_agent
model: claude-opus-5[1m]
run_id: credit_default-full_agent-20260909T002419Z-d03b07c6
data_mode: real
grounding_precision_pre: 1.0000
grounding_precision_post: 1.0000
n_claims: 210
n_findings_by_severity: {high: 0, medium: 0, low: 0, info: 0}
generated: "2026-09-09T00:24:19Z"
illustrative: false
---

# Validation report — `credit_default` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `credit_default` v1.0 | `full_agent` | claude-opus-5[1m] | real, UCI Default of Credit Card Clients (dataset id 350; CC BY 4.0; Yeh, I. (2009), doi 10.24432/C55S3H), 30,000 clients, sampled by sample.py. Synthetic mode: synthetic.py. | 1.0000 → 1.0000 | 0 / 0 / 0 / 0 |
<!-- quaestor:renderer:end -->

This report reviews the credit_default model package, a credit scoring model that predicts the probability that an account defaults, and it follows the structure of the Federal Reserve's model risk management guidance on model validation and monitoring [[reg:SR26-2:V]].

The subject was executed on both of its declared splits under a wall-clock cap of 300 seconds [[art:2ad8d1a5:runtime.max_seconds]], and the performance figures below were recomputed independently from the subject's scored output rather than read from the developer's own report.
The development split holds 21000 [[art:a359de9d:profile.train.n]] rows and the held-out split holds 9000 [[art:abbe1a27:profile.test.n]] rows.

On the held-out split, discrimination clears the declared floor, at 0.755 [[art:365b7034:metrics.test.auc]] against a minimum of 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]].
The mean squared error of the predicted probabilities is 0.1385 [[art:86e93c8f:metrics.test.brier]], inside the declared ceiling of 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]].
The calibration slope is 0.9886 [[art:e06564c7:calibration_slope.test]], inside the declared band running from 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] to 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The largest development-to-holdout distribution shift, score included, is 0.003083 [[art:e1d82330:psi.max]] against a declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
Each developer-declared threshold carried in this section is therefore met, and every one of them is met with margin rather than marginally.

Discrimination on the development split, at 0.7546 [[art:01cf8178:metrics.train.auc]], sits close to the held-out figure, so the holdout result does not appear to rest on an optimistic fit.
Across the slices of the held-out split reported here, the widest shortfall in discrimination relative to the split as a whole is 0.04359 [[art:41c300dd:metrics.test.sub.limit_bal_high.auc_gap]], on a slice holding 0.513 [[art:0f3d3609:metrics.test.sub.limit_bal_high.share]] of the split.
As part of the outcomes analysis contemplated by the guidance [[reg:SR26-2:V.1.b]], a challenger was scored on the same holdout and reached a discrimination advantage over the subject of 0.02391 [[art:3877bdd0:challenger.delta_auc]], which the later sections take up as a question of headroom rather than of threshold breach.
The design shows no acute collinearity, with a largest variance inflation factor of 3.544 [[art:d3785ba9:vif.max]] and a condition number of 4.279 [[art:ba0d9cc4:condition_number]].

No findings were raised in this section, at any severity.

## 2. Conceptual soundness

This section assesses the design of the credit_default 1.0 champion — its modeling choices, the variables it retains, the interpretability evidence around its fitted parameters, and benchmarking against an alternative model — as contemplated for a conceptual soundness review [[reg:SR26-2:V.1.a]].

### Design and inputs

The champion is a single linear-in-coefficients scoring model with an intercept of -1.442 [[art:ca1c764c:run.model_summary#intercept]], fitted on 21000 [[art:ca1c764c:run.model_summary#n_train]] training rows.
The declared feature inventory holds 12 [[art:792cb79c:run.features#n]] features.
Of those, 10 [[art:792cb79c:run.features#before_period_start]] are known before the performance period opens and 2 [[art:792cb79c:run.features#at_origination]] are fixed at origination.
None are observed during the performance period, 0 [[art:792cb79c:run.features#during_period]], and none after the outcome is determined, 0 [[art:792cb79c:run.features#after_outcome]].
Every input is therefore available at the moment the score would be used, which is what the intended decision point requires.

### The developer's own feature screen

The developer applied a collinearity screen with a cutoff of 10 [[art:ca1c764c:run.model_summary#vif_threshold]] on the variance inflation factor.
It removed bill_last, whose inflation factor was 33.8 [[art:ca1c764c:run.model_summary#removed.bill_last.vif]], and utilisation_mean_6m at 10.96 [[art:ca1c764c:run.model_summary#removed.utilisation_mean_6m.vif]].
Both of the removed variables restate information the retained billing and utilisation terms already carry, so the screen removed redundancy rather than a distinct risk driver, and the cutoff itself is a conventional one for a linear model of this kind.

### Coefficients and the signs subject matter expects

The three delinquency terms carry the largest weights and all push the score toward default: delinq_last at 0.4847 [[art:ca1c764c:run.model_summary#coefficients.delinq_last.value]], delinq_count_6m at 0.2801 [[art:ca1c764c:run.model_summary#coefficients.delinq_count_6m.value]], and delinq_max_6m at 0.2263 [[art:ca1c764c:run.model_summary#coefficients.delinq_max_6m.value]].
That is the direction credit subject matter expects, since recent and repeated delinquency is the strongest observable precursor of default.
The next largest weight is on the credit limit, -0.2091 [[art:ca1c764c:run.model_summary#coefficients.limit_bal.value]], and its negative sign matches the expectation that larger granted limits mark better-underwritten borrowers.
The remaining weights are small by comparison: pay_ratio_mean_6m at -0.09824 [[art:ca1c764c:run.model_summary#coefficients.pay_ratio_mean_6m.value]], utilisation at -0.08257 [[art:ca1c764c:run.model_summary#coefficients.utilisation.value]], age at 0.07253 [[art:ca1c764c:run.model_summary#coefficients.age.value]], bill_trend_6m at 0.04808 [[art:ca1c764c:run.model_summary#coefficients.bill_trend_6m.value]], bill_mean_6m at -0.007568 [[art:ca1c764c:run.model_summary#coefficients.bill_mean_6m.value]], and pay_ratio_last at 0.00678 [[art:ca1c764c:run.model_summary#coefficients.pay_ratio_last.value]].
The sustained repayment ratio enters negative, which is the expected direction: borrowers who repay a larger share of the bill over six months default less often.

### Fitted signs against univariate direction

Among the retained features, the count whose fitted sign contradicts the direction of that feature's own single-feature relationship with the outcome on train is 3 [[art:e223cd4a:sign_check.n_disagreements]].
The three are utilisation, pay_ratio_last, and bill_trend_6m, and each is set out below with the ablation delta that measures how much the model actually leans on the feature; the baseline these deltas are measured from is a test AUC of 0.755 [[art:789072f8:ablation.baseline_auc]] for a refit of the champion's form on every retained feature.

Utilisation is fitted negative, -1 [[art:46230409:sign_check.utilisation.coef_sign]], while on its own it points positive toward default, 1 [[art:f0995196:sign_check.utilisation.univariate_direction]], so the two disagree, 0 [[art:cb5a7bc7:sign_check.utilisation.agrees]].
Refitting without utilisation changes test AUC by 1.92e-05 [[art:dc9ac505:ablation.utilisation.delta_auc]], an improvement rather than a loss, so the model is not drawing discrimination from this term and the sign reversal reflects the credit limit and billing terms absorbing what utilisation would otherwise carry.

The most recent repayment ratio is fitted positive, 1 [[art:f018263e:sign_check.pay_ratio_last.coef_sign]], against a univariate direction that is negative, -1 [[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]], and the two disagree, 0 [[art:79abee77:sign_check.pay_ratio_last.agrees]].
A positive weight says a larger last repayment raises the score, which runs against what credit subject matter expects, but refitting without the term costs -5.589e-05 [[art:e26d8112:ablation.pay_ratio_last.delta_auc]] of test AUC, so the counter-intuitive sign sits on a term the model barely uses and its practical effect on any score is slight.

The six-month billing trend is fitted positive, 1 [[art:abd4aaba:sign_check.bill_trend_6m.coef_sign]], against a negative univariate direction, -1 [[art:a9bff389:sign_check.bill_trend_6m.univariate_direction]], and the two disagree, 0 [[art:c0f6d07d:sign_check.bill_trend_6m.agrees]].
This is the disagreement that matters most of the three: refitting without the term costs -0.001393 [[art:99f9dd71:ablation.bill_trend_6m.delta_auc]] of test AUC, so the model is drawing real discrimination through a coefficient whose direction is opposite to the feature's standalone relationship with default.
A rising billing trend is conventionally read as growing exposure and hence higher risk, and the positive fitted weight is consistent with that reading even though the univariate direction on train is not, so the disagreement is better explained by conditioning on the delinquency and limit terms than by an error in the specification.

The features whose fitted signs agree with their univariate directions include the dominant delinquency terms, delinq_last at 1 [[art:a8ba9372:sign_check.delinq_last.agrees]], delinq_count_6m at 1 [[art:a337d16b:sign_check.delinq_count_6m.agrees]], and delinq_max_6m at 1 [[art:da92a015:sign_check.delinq_max_6m.agrees]], together with limit_bal at 1 [[art:103d99fb:sign_check.limit_bal.agrees]], pay_ratio_mean_6m at 1 [[art:7e9a76ca:sign_check.pay_ratio_mean_6m.agrees]], bill_mean_6m at 1 [[art:89279c3b:sign_check.bill_mean_6m.agrees]], and age at 1 [[art:4116add1:sign_check.age.agrees]].
The weight the model places on each of these is visible in the refit deltas: delinq_last at -0.005914 [[art:40f4e6bf:ablation.delinq_last.delta_auc]] and limit_bal at -0.003748 [[art:57710b23:ablation.limit_bal.delta_auc]] are the two features the champion depends on most, followed by age at -0.002225 [[art:f6fdd709:ablation.age.delta_auc]], delinq_count_6m at -0.002146 [[art:db90576e:ablation.delinq_count_6m.delta_auc]], delinq_max_6m at -0.001133 [[art:18cb1559:ablation.delinq_max_6m.delta_auc]], pay_ratio_mean_6m at -0.0009816 [[art:cba98844:ablation.pay_ratio_mean_6m.delta_auc]], and bill_mean_6m at -0.0001527 [[art:5b4423ab:ablation.bill_mean_6m.delta_auc]].
Read together, the discrimination is concentrated in the most recent delinquency marker and the credit limit, and the model's leading weights sit on the variables a credit analyst would expect to lead.

### Effective challenge

The champion scores 0.755 [[art:365b7034:metrics.test.auc]] AUC on test with a Brier score of 0.1385 [[art:86e93c8f:metrics.test.brier]].
The challenger reaches 0.7789 [[art:5646e7f3:challenger.auc]] AUC on the same test data with a Brier score of 0.135 [[art:2031a154:challenger.brier]], so it is both better ranked and better calibrated than the champion.
The challenger's lead in AUC is 0.02391 [[art:3877bdd0:challenger.delta_auc]].
The threshold set for this review treats a challenger lead as material at 0.03 [[art:e042774c:threshold.E1.delta_auc]], and the observed lead sits below it.
On that criterion the challenger's advantage is not large enough to unseat the champion's functional form, though the margin is close enough to the threshold that the comparison is worth re-running whenever the model is refit or the population shifts.

### Judgement

The design is defensible on its own terms: the inputs are all knowable at the decision point, the collinearity screen removed only redundant variables, the largest weights sit on delinquency and the credit limit with the signs subject matter expects, and a stronger alternative did not beat the champion by the margin this review set as decisive.
The sign disagreements and ablation deltas above are developmental evidence supporting that judgement, and no rule in this review fires on either family, so nothing in this section is carried forward to the findings section.
The qualification worth recording is that one of the disagreements sits on a term the model genuinely uses, which is a reason to keep the specification under review rather than a reason to reject it.

## 3. Data integrity and drift

Sound development practice includes a critical assessment of data quality, relevance, and inputs, and the checks below examine the splits used to build and test this package, their stability against one another, and the screens run for contamination [[reg:SR26-2:IV.1]].

### Missingness

The training split holds 21000 [[art:a359de9d:profile.train.n]] rows and the test split holds 9000 [[art:abbe1a27:profile.test.n]] rows.
The largest missing fraction over any column of the training split is 0 [[art:050a3099:profile.train.missing.max]], and the largest over any column of the test split is likewise 0 [[art:f813848d:profile.test.missing.max]].
The two split maxima are therefore identical, so the gap between them sits at the floor of the permitted range, whose upper bound is 0.1 [[art:9cce25ea:threshold.D1.missing_gap]].
No column in either split contributes missingness, so imputation choices cannot be a source of divergence between the splits here.

### Population and characteristic stability

The declared stability bound for the training split measured against test is 0.25 [[art:278b9016:threshold.S1.psi]], and the package declares the same value of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
The largest population stability index across all features and the score is 0.003083 [[art:e1d82330:psi.max]], two orders of magnitude inside that bound.
The per-feature values, train against test, are as follows.

- age: 0.003083 [[art:06c22a63:psi.age]]
- credit limit: 0.001272 [[art:b0195847:psi.limit_bal]]
- utilisation: 0.0006523 [[art:f094559b:psi.utilisation]]
- six-month bill mean: 0.001488 [[art:127cdf82:psi.bill_mean_6m]]
- six-month bill trend: 0.0007484 [[art:78be70d2:psi.bill_trend_6m]]
- six-month delinquency count: 0.001856 [[art:d77ddb1d:psi.delinq_count_6m]]
- six-month delinquency maximum: 0.001027 [[art:4b0a94ab:psi.delinq_max_6m]]
- most recent delinquency: 0.0002347 [[art:cbc9de36:psi.delinq_last]]
- most recent payment ratio: 0.002264 [[art:82c97112:psi.pay_ratio_last]]
- six-month mean payment ratio: 0.001028 [[art:62e0e0f8:psi.pay_ratio_mean_6m]]
- model score: 0.001368 [[art:ec2b8d1b:psi.y_score]]

Age is the widest of these at 0.003083 [[art:06c22a63:psi.age]] and sets the maximum, and the score itself shifts by 0.001368 [[art:ec2b8d1b:psi.y_score]], so the distributional agreement between the splits carries through to the model output rather than being confined to the inputs.

Characteristic stability, which weights each feature's shift by its contribution to the linear predictor, is largest for the six-month delinquency maximum at 0.004737 [[art:ce1257d8:csi.max]].
The per-feature contributions are as follows.

- age: 0.001203 [[art:25b88f37:csi.age]]
- credit limit: 0.001384 [[art:c91a2a4b:csi.limit_bal]]
- utilisation: 0.0002136 [[art:6ed37e42:csi.utilisation]]
- six-month bill mean: 9.982e-06 [[art:0c34001d:csi.bill_mean_6m]]
- six-month bill trend: 0.0003675 [[art:9e5a9b68:csi.bill_trend_6m]]
- six-month delinquency count: 0.0008781 [[art:f0438233:csi.delinq_count_6m]]
- six-month delinquency maximum: 0.004737 [[art:35990a39:csi.delinq_max_6m]]
- most recent delinquency: 0.001698 [[art:e755cf0a:csi.delinq_last]]
- most recent payment ratio: 0.0001132 [[art:5898a9c5:csi.pay_ratio_last]]
- six-month mean payment ratio: 0.002043 [[art:5e53c153:csi.pay_ratio_mean_6m]]

The ordering differs from the population view, in that the delinquency terms and the six-month mean payment ratio carry more weight into the predictor than their raw distributional shifts alone would suggest, but the largest of them at 0.004737 [[art:ce1257d8:csi.max]] remains far below the declared bound of 0.25 [[art:278b9016:threshold.S1.psi]].

### Leakage screens

The timing screen reads the declared observation window of each feature and counts those declared as observed during the performance period or after the outcome, and that count is 0 [[art:742bcd24:leakage.timing.n_flagged]].
The target-association screen fits each feature alone against the outcome, and the strongest single feature reaches an AUC of 0.728 [[art:2e212f3a:leakage.target_corr.max_single_feature_auc]], inside the bound of 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]] above which a lone feature would be treated as standing in for the target.
That margin is wide enough that no individual input behaves like a leaked outcome, though the screen speaks only to univariate association and not to combinations of features.

The contamination screen has two arms, each read against its own bound.
On identifiers, the share of test rows whose client identifier also identifies a row of the training split is 0 [[art:63d37fc5:leakage.overlap.ids]], against the declared bound of 0.005 [[art:9f336eaf:threshold.L2.overlap]], so no subject appears on both sides of the split.
On feature vectors, the share of test rows whose feature values also appear in the training split is 0.01256 [[art:517f3049:leakage.overlap.features]], and the overall feature-value overlap agrees at 0.01256 [[art:ebd7ff30:leakage.overlap]].
This arm is read against the bound the rule actually applied, 0.02324 [[art:7cdc63cb:threshold.L2.overlap.features_effective]], which is the larger of the declared bound and twice the share of training rows whose feature values are not unique within the training split, that share being 0.01162 [[art:c988bb0e:leakage.duplicates.train]].
The widening is deliberate: with discrete features, two different subjects can write the same row by coincidence, and the rate at which the training split repeats itself internally sets the scale at which such coincidences are expected.
Read against that applied bound of 0.02324 [[art:7cdc63cb:threshold.L2.overlap.features_effective]], the feature-vector overlap of 0.01256 [[art:517f3049:leakage.overlap.features]] sits inside it, and taken together with the identifier arm at 0.0 [[art:63d37fc5:leakage.overlap.ids]] the coincidence reading is the one the evidence supports.
The name screen matches feature names against a lexicon of target-adjacent terms and matched 0 [[art:407e62be:leakage.name_screen.n_matched]] names.

### Assessment

The splits agree on missingness, the distributional and predictor-weighted shifts between them are small fractions of the declared bound, and each leakage arm reads inside the bound applied to it.
The residual caveat is that the feature-overlap arm is judged against a widened bound whose width is set by the training split's own internal duplication rate, so its assurance rests on the assumption that repeated discrete rows are coincidence; the identifier arm at 0 [[art:63d37fc5:leakage.overlap.ids]] is the independent evidence for that assumption, and it holds here.

## 4. Outcomes analysis

Outcomes analysis compares model outputs against the corresponding real-world outcomes, to assess performance relative to the model's objectives and business use [[reg:SR26-2:V.1.b]].
This section reports discrimination first and calibration second, because the observed event rate on the evaluation split is 0.2212 [[art:f60ae2a7:metrics.test.event_rate]], at or above the 0.05 [[art:42f1351e:rule.calibration_first_event_rate]] below which this report would lead with calibration instead.

### Discrimination and fit by split

| Metric | Train | Test |
| --- | --- | --- |
| Rows scored | 21000 [[art:1721ceae:metrics.train.n]] | 9000 [[art:5367a59f:metrics.test.n]] |
| Observed event rate | 0.2212 [[art:657aa7fc:metrics.train.event_rate]] | 0.2212 [[art:f60ae2a7:metrics.test.event_rate]] |
| AUC | 0.7546 [[art:01cf8178:metrics.train.auc]] | 0.755 [[art:365b7034:metrics.test.auc]] |
| Gini | 0.5091 [[art:eaaf0f79:metrics.train.gini]] | 0.51 [[art:296bfeeb:metrics.test.gini]] |
| KS | 0.4144 [[art:18df22bd:metrics.train.ks]] | 0.4067 [[art:d3c4ed61:metrics.test.ks]] |
| Brier score | 0.1384 [[art:c95106e9:metrics.train.brier]] | 0.1385 [[art:86e93c8f:metrics.test.brier]] |
| Log loss | 0.4439 [[art:b816b083:metrics.train.logloss]] | 0.4442 [[art:2de58c1b:metrics.test.logloss]] |
| Mean predicted probability | 0.2212 [[art:935d2cb7:metrics.train.mean_predicted]] | 0.2206 [[art:89d241ea:metrics.test.mean_predicted]] |

Rank ordering concentrates events in the highest-scoring deciles, with the top two deciles holding 0.5031 [[art:5131afa7:deciles.train.top2_capture]] of train events and 0.4952 [[art:e2c0ad9f:deciles.test.top2_capture]] of test events.
The decile detail on the evaluation split is set out below.

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

### Train-to-test gap

AUC on the evaluation split, 0.755 [[art:365b7034:metrics.test.auc]], is not below AUC on the development split, 0.7546 [[art:01cf8178:metrics.train.auc]], so the train-to-test gap is on the favourable side of zero and well inside the bound of 0.08 [[art:630f28f4:threshold.O1.auc_gap]] the package sets for it.
The other paired quantities move in the same narrow way, with the Brier score and the log loss on the evaluation split each within a thousandth of their development-split values, so the fit does not depend on the sample the model was estimated on.

### Calibration

The logistic regression of the outcome on the logit of the predicted probability gives a slope of 0.9886 [[art:e06564c7:calibration_slope.test]] on the evaluation split, inside the band running from 0.8 [[art:749634ae:threshold.C1.calibration_slope.min]] to 1.2 [[art:b6672579:threshold.C1.calibration_slope.max]], against 1.001 [[art:85461245:calibration_slope.train]] on the development split.
The same regression gives an intercept of -0.008632 [[art:2ee976d3:calibration_intercept.test]] on the evaluation split and 0.0003779 [[art:2ce8cd09:calibration_intercept.train]] on the development split, so neither split shows a systematic shift in level.
Mean predicted probability on the evaluation split is 0.2206 [[art:89d241ea:metrics.test.mean_predicted]] against an observed rate of 0.2212 [[art:f60ae2a7:metrics.test.event_rate]], a relative gap of 0.002944 [[art:bae28fd6:calibration.mean_rel_gap.test]] against a tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
The corresponding relative gap on the development split is 0.0001555 [[art:a03ea014:calibration.mean_rel_gap.train]], so the small widening on the evaluation split is a fraction of the tolerance.
Calibration by decile of predicted probability on the evaluation split is set out below.

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

The table sets each bound the package declares beside the value recomputed for this report and the outcome of that comparison, one row per declared bound.
It is produced by the tool from the same recomputed values reported above, so it cannot disagree with them.

### Follow-up analyses

Aggregate metrics cleared every declared bound, so the loop asked for metrics on `limit_bal < median(limit_bal)`, to test whether discrimination and calibration hold on the low-limit half where pooled results could mask weakness.

<!-- quaestor:renderer:begin table metrics.train.sub.limit_bal_low -->
Every metric on the limit_bal below_median slice of train [[art:87a13a33:metrics.train.sub.limit_bal_low]]:

| metric | value |
|---|---|
| n | 10158 |
| event_rate | 0.2846 |
| auc | 0.7557 |
| gini | 0.5113 |
| ks | 0.4305 |
| brier | 0.1623 |
| logloss | 0.5042 |
| mean_predicted | 0.282 |
| share | 0.4837 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.limit_bal_low -->
Every metric on the limit_bal below_median slice of test [[art:c0819f02:metrics.test.sub.limit_bal_low]]:

| metric | value |
|---|---|
| n | 4383 |
| event_rate | 0.2877 |
| auc | 0.7477 |
| gini | 0.4955 |
| ks | 0.4047 |
| brier | 0.1675 |
| logloss | 0.5165 |
| mean_predicted | 0.2802 |
| share | 0.487 |
<!-- quaestor:renderer:end -->

AUC on this slice falls 0.007286 [[art:15e1edcb:metrics.test.sub.limit_bal_low.auc_gap]] below the evaluation split's own on test and -0.001109 [[art:021950a5:metrics.train.sub.limit_bal_low.auc_gap]] below it on train, both inside the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] on how far a sub-population may fall below its split.
The slice holds 0.487 [[art:e7847e2b:metrics.test.sub.limit_bal_low.share]] of the evaluation split and 0.4837 [[art:d4eb837c:metrics.train.sub.limit_bal_low.share]] of the development split, comfortably above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] a sub-population must hold to raise an open item.
Mean predicted probability of 0.2802 [[art:e3d342d5:metrics.test.sub.limit_bal_low.mean_predicted]] sits just under an observed rate of 0.2877 [[art:9629805c:metrics.test.sub.limit_bal_low.event_rate]] on the evaluation split, so the level of the probabilities tracks the outcome and the ordering is intact on this half.

The complementary half, `limit_bal >= median(limit_bal)`, was then asked for, to tell whether the low-limit slice's metrics are a real disparity or simply the split-wide level.

<!-- quaestor:renderer:begin table metrics.train.sub.limit_bal_high -->
Every metric on the limit_bal above_median slice of train [[art:3f1e33d4:metrics.train.sub.limit_bal_high]]:

| metric | value |
|---|---|
| n | 10842 |
| event_rate | 0.1618 |
| auc | 0.7085 |
| gini | 0.4169 |
| ks | 0.3484 |
| brier | 0.1159 |
| logloss | 0.3875 |
| mean_predicted | 0.1642 |
| share | 0.5163 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.limit_bal_high -->
Every metric on the limit_bal above_median slice of test [[art:1fdb46f8:metrics.test.sub.limit_bal_high]]:

| metric | value |
|---|---|
| n | 4617 |
| event_rate | 0.1581 |
| auc | 0.7114 |
| gini | 0.4229 |
| ks | 0.3431 |
| brier | 0.111 |
| logloss | 0.3755 |
| mean_predicted | 0.164 |
| share | 0.513 |
<!-- quaestor:renderer:end -->

AUC on the high-limit half falls 0.04359 [[art:41c300dd:metrics.test.sub.limit_bal_high.auc_gap]] below the evaluation split's own and 0.04609 [[art:b9498743:metrics.train.sub.limit_bal_high.auc_gap]] below the development split's, the widest separation among the slices run and still inside the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].
The slice holds 0.513 [[art:0f3d3609:metrics.test.sub.limit_bal_high.share]] of the evaluation split and 0.5163 [[art:59ef1a64:metrics.train.sub.limit_bal_high.share]] of the development split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].
Mean predicted probability of 0.164 [[art:c30b141c:metrics.test.sub.limit_bal_high.mean_predicted]] against an observed rate of 0.1581 [[art:6c8ff585:metrics.test.sub.limit_bal_high.event_rate]] keeps the level of the probabilities close to the outcome, so what separation there is lies in the ordering of the scores within this half rather than in their level.

With the limit halves showing nothing outside the bound, the loop asked for metrics on `delinq_count_6m >= median(delinq_count_6m)`, the risk-concentrated delinquency slice where discrimination and calibration are most likely to diverge from the pooled result.

<!-- quaestor:renderer:begin table metrics.train.sub.delinq_count_6m_high -->
Every metric on the delinq_count_6m above_median slice of train [[art:400c814d:metrics.train.sub.delinq_count_6m_high]]:

| metric | value |
|---|---|
| n | 21000 |
| event_rate | 0.2212 |
| auc | 0.7546 |
| gini | 0.5091 |
| ks | 0.4144 |
| brier | 0.1384 |
| logloss | 0.4439 |
| mean_predicted | 0.2212 |
| share | 1 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.delinq_count_6m_high -->
Every metric on the delinq_count_6m above_median slice of test [[art:55bd496f:metrics.test.sub.delinq_count_6m_high]]:

| metric | value |
|---|---|
| n | 9000 |
| event_rate | 0.2212 |
| auc | 0.755 |
| gini | 0.51 |
| ks | 0.4067 |
| brier | 0.1385 |
| logloss | 0.4442 |
| mean_predicted | 0.2206 |
| share | 1 |
<!-- quaestor:renderer:end -->

AUC on this slice falls 0 [[art:5125fbea:metrics.test.sub.delinq_count_6m_high.auc_gap]] below the evaluation split's own and 0 [[art:48e23659:metrics.train.sub.delinq_count_6m_high.auc_gap]] below the development split's, inside the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].
The slice holds 1 [[art:dd55d203:metrics.test.sub.delinq_count_6m_high.share]] of the evaluation split and 1 [[art:025f5eaa:metrics.train.sub.delinq_count_6m_high.share]] of the development split, so the rule as applied selected the whole of each split rather than a proper subset, which is why it reproduces the split-wide numbers and why the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] is not the binding consideration here.
Mean predicted probability of 0.2206 [[art:a703edcb:metrics.test.sub.delinq_count_6m_high.mean_predicted]] against an observed rate of 0.2212 [[art:951c81ed:metrics.test.sub.delinq_count_6m_high.event_rate]] repeats the split-wide level, so this step carries no information about the delinquency-concentrated population beyond what the pooled result already showed.

Utilisation was not covered by the earlier slices, so the loop asked for metrics on `utilisation >= median(utilisation)`, the high-utilisation borrowers among whom discrimination and calibration most often degrade.

<!-- quaestor:renderer:begin table metrics.train.sub.utilisation_high -->
Every metric on the utilisation above_median slice of train [[art:7feaf808:metrics.train.sub.utilisation_high]]:

| metric | value |
|---|---|
| n | 10500 |
| event_rate | 0.255 |
| auc | 0.7819 |
| gini | 0.5638 |
| ks | 0.4801 |
| brier | 0.1455 |
| logloss | 0.4626 |
| mean_predicted | 0.2577 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.utilisation_high -->
Every metric on the utilisation above_median slice of test [[art:b866a9dd:metrics.test.sub.utilisation_high]]:

| metric | value |
|---|---|
| n | 4500 |
| event_rate | 0.2658 |
| auc | 0.7781 |
| gini | 0.5562 |
| ks | 0.4739 |
| brier | 0.1492 |
| logloss | 0.4717 |
| mean_predicted | 0.2608 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

AUC on this slice falls -0.02309 [[art:7132f197:metrics.test.sub.utilisation_high.auc_gap]] below the evaluation split's own and -0.02732 [[art:41fca294:metrics.train.sub.utilisation_high.auc_gap]] below the development split's, that is above each split on both, and so inside the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].
The slice holds 0.5 [[art:9404484e:metrics.test.sub.utilisation_high.share]] of the evaluation split and 0.5 [[art:0ff76e00:metrics.train.sub.utilisation_high.share]] of the development split, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].
Mean predicted probability of 0.2608 [[art:e68f1a3d:metrics.test.sub.utilisation_high.mean_predicted]] sits a little below an observed rate of 0.2658 [[art:e4a00a59:metrics.test.sub.utilisation_high.event_rate]], a mild understatement of level on a slice whose ordering is stronger than the split's, so neither the level nor the ordering of the probabilities weakens where risk concentrates.

## 5. Sensitivity and scenario analysis

Sensitivity analysis of the kind described in the earlier guidance — checking the effect of small changes in inputs and parameter values, and probing behaviour at extreme values to establish where a model becomes unstable — is the frame for this section [[reg:SR11-7:V.1.a]].

### 5.1 Multicollinearity among the retained features

The largest variance inflation factor across the retained features is 3.544 [[art:d3785ba9:vif.max]], against a threshold of 10 [[art:aeb4f33c:threshold.M1.vif]].
That largest value belongs to the six-month delinquency count, at 3.544 [[art:7273e0be:vif.delinq_count_6m]].
The six-month delinquency maximum is next, at 3.484 [[art:e7b701a1:vif.delinq_max_6m]].
The six-month mean payment ratio is 3.027 [[art:2cda5cfc:vif.pay_ratio_mean_6m]] and utilisation is 2.829 [[art:6ce4c102:vif.utilisation]].
The most recent payment ratio is 2.714 [[art:b68613a6:vif.pay_ratio_last]], the six-month mean bill amount is 2.265 [[art:87cb4e54:vif.bill_mean_6m]], and the most recent delinquency indicator is 2.321 [[art:59461811:vif.delinq_last]].
The credit limit is 2.097 [[art:0c6efb3f:vif.limit_bal]], the six-month bill trend is 1.33 [[art:6d3f01ce:vif.bill_trend_6m]], and age is 1.025 [[art:692cd6e9:vif.age]].
Every retained feature therefore sits below the threshold, and the spread is narrow enough that no single feature dominates the shared variance: the delinquency and payment-ratio blocks each carry the mild internal correlation one would expect from features built over the same six-month window, but none of it rises to the level at which a coefficient's variance would be inflated beyond the tolerance set for this model.

Belsley's condition number of the column-standardised design is 4.279 [[art:ba0d9cc4:condition_number]], against a threshold of 30 [[art:7e52fd7a:threshold.M1.condition_number]].
The design is thus well conditioned by a wide margin, which corroborates the per-feature reading: the near-dependency that a high condition number would reveal in combination across several columns at once, and that per-feature inflation factors can miss, is not present here.
Taken together the two diagnostics support reading the fitted coefficients as individually identified rather than as an unstable split of a shared effect.

### 5.2 Analyses that do not apply to this model

Stability across declared regimes does not apply to this model: the subject carries no regime column over which the declared partitions could be formed, so there is no regime-wise decomposition to report and none should be read into this section.
The rate-shock scenarios — the change in value at the extreme shocks, the monotonicity of the shock curve, and the sign of its convexity against the direction the package declares — do not apply either, because the subject is not a hazard model and has no term structure for a rate shock to act on.
Both exclusions are recorded in Appendix D, and neither was run; they are listed there as inapplicable to this model type rather than as analyses with results.

### 5.3 Reading

On the evidence in this section the model's coefficient estimates rest on a design without material collinearity, on both the per-feature and the whole-design view, and each diagnostic clears its threshold rather than approaching it.
The sensitivity evidence assembled here bears on the input side of the model only; the scenario dimensions that would exercise its behaviour under shifted conditions are the two that do not apply to this model type, so the robustness picture drawn here should be understood as resting on the collinearity diagnostics and on whatever stability evidence other sections of this report carry.

## 6. Findings and recommendations

Findings are ordered by severity, most severe first, and each carries the measured evidence that establishes the defect together with the validator's conclusion and the corrective action asked of the developer [[reg:SR26-2:V]].

This validation raised no finding.

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1, S1), `compute_metrics` (T1, C1, O1), `check_leakage` (L1, L2), `check_collinearity` (M1), `challenger_compare` (E1).

### Open items

This validation recorded no observation of this kind for the model developer to answer for.

## 7. Ongoing monitoring recommendations

Ongoing monitoring evaluates the extent to which this model continues to perform as expected given potential changes in products, exposures, activities, clients, data relevance, or market conditions, and the recommendations below are framed to that end [[reg:SR26-2:V.2]].

### Quantities to track, frequency, and bound

Monitoring should re-track the same quantities this validation checked, against the same declared bounds, so that a production reading is directly comparable with the validation reading rather than to a newly invented tolerance.

Input and score stability should be monitored at the highest frequency, monthly, because it requires no outcome maturity: compare the largest population shift statistic across scored features and the score itself against the declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
The validation reading of 0.003083 [[art:e1d82330:psi.max]] is the reference point for that comparison, and it is far enough below the ceiling that any sustained movement toward it in production should prompt investigation well before the ceiling is reached rather than only at breach.

Discrimination should be tracked on each production cohort once its performance window has closed, at quarterly reporting frequency, against the declared floor of 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]].
The validation reading of 0.755 [[art:365b7034:metrics.test.auc]] sits above that floor by a margin narrow enough that ordinary cohort-to-cohort variation could carry a production reading below it, so the monitoring report should present the trend across cohorts and not a single cohort's value in isolation.

Probability accuracy should be tracked on the same quarterly cycle against the declared ceiling of 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]], with the validation reading of 0.1385 [[art:86e93c8f:metrics.test.brier]] as the reference point.

Calibration should be tracked by regressing the realized outcome on the logit of the predicted probability for each matured cohort and comparing the slope against the declared band running from 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] to 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The validation reading of 0.9886 [[art:e06564c7:calibration_slope.test]] sits near the centre of that band, so drift toward either edge is informative even while the reading remains inside it.

Where a monitoring cohort's observed event rate falls below 0.05 [[art:42f1351e:rule.calibration_first_event_rate]], that monitoring report should lead with calibration and present discrimination after it, since rank-ordering statistics become unstable as events thin out.
Section 4 of this report led with discrimination because the observed event rate on the evaluation split was at or above that bound, and a future cohort falling below it would warrant the reversed ordering rather than a restatement of what this report did.

Persistent deviation outside these declared thresholds, as opposed to a single cohort excursion, is the trigger for considering overlays, adjustment, recalibration, or redevelopment, and the monitoring plan should state in advance who evaluates that question and on what timetable [[reg:SR26-2:V.1.b]].

### Benchmarking against a reference the development data cannot supply

Section 2 of this report compares the champion against a challenger fitted on the development data, so benchmarking against an alternative model was part of this validation; what monitoring adds is a benchmark the development data cannot give.
The recommended routine benchmark is the challenger refitted on production vintages, so that the comparison reflects the population actually being scored rather than the development sample, and the champion's advantage can be re-established rather than assumed to persist.
Separately and at lower frequency, an external reference — a retail credit bureau score or a vendor credit risk model applied to the same booked population — should be compared against the champion's rank-ordering, since an external benchmark can reveal deterioration that is invisible when both sides of the comparison are trained on the organization's own data [[reg:SR11-7:V.1.b]].
Discrepancies against either benchmark should trigger investigation into their source and degree rather than automatic revision, because the benchmark is itself an alternative prediction built on different data or methods.

### What this validation could not cover and monitoring should watch instead

The stability, discrimination, and calibration evidence in this report is drawn from a train-and-test partition of the development data, so it speaks to performance across that partition and not to performance across time; out-of-time behaviour on production vintages is the first thing monitoring must supply.
This validation observed the model as a scoring function and not as a deployed system, so process verification — that inputs arrive accurate and complete, that the scoring code in production matches the reviewed artifact, and that changes to it are logged and auditable — belongs to monitoring.
Override behaviour cannot be observed before the model is in use, and the monitoring plan should track the override rate and the realized performance of overridden cases, since a high rate or overrides that consistently improve on the model would point to a need for revision.
Use of the model outside the population and product scope it was developed on is likewise outside what this validation could examine, and monitoring should detect such extension by tracking the composition of the scored population against the development population rather than only the aggregate shift statistic.
Finally, macroeconomic conditions during the development sample are a single realization, so monitoring should watch performance separately by vintage and by exposure segment, since deterioration concentrated in one segment can be masked in a portfolio-level reading that still sits inside every declared bound.

## Appendix A — Claims

Grounding precision 1.0000 before repair (210 of 210 claims verified) and 1.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 18/18; conceptual_soundness 54/54; data_integrity 48/48; outcomes 66/66; sensitivity 14/14; monitoring 10/10.

Developer claims: 2 of 2 declared in `package.yaml` verify against this run's artifacts.

Excluded numeric tokens (not claims): section_number (5.1, 5.2, 5.3, Section 4); citation_hash (2ad8d1a5, a359de9d, abbe1a27, 365b7034); regulatory_section_id (SR26-2:V, SR26-2:V.1.b, SR26-2:V.1.a, SR26-2:IV.1); package_version (1.0); extractor_returned_excluded_token (1.0, 26.0, 2, 2.0).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The subject was executed on both of its declared splits unde… | 300 | ratio | runtime |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 2 | summary | The development split holds 21000 rows and the held-out spli… | 21000 | count | n | train | eq | `[[art:a359de9d:profile.train.n]]` | verified | 21000 |
| 3 | summary | The development split holds 21000 rows and the held-out spli… | 9000 | count | n | test | eq | `[[art:abbe1a27:profile.test.n]]` | verified | 9000 |
| 4 | summary | On the held-out split, discrimination clears the declared fl… | 0.755 | ratio | auc | test | eq | `[[art:365b7034:metrics.test.auc]]` | verified | 0.7550239453 |
| 5 | summary | On the held-out split, discrimination clears the declared fl… | 0.7 | ratio | auc | test | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 6 | summary | The mean squared error of the predicted probabilities is 0.1… | 0.1385 | ratio | brier | test | eq | `[[art:86e93c8f:metrics.test.brier]]` | verified | 0.1385162411 |
| 7 | summary | The mean squared error of the predicted probabilities is 0.1… | 0.2 | ratio | brier | test | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 8 | summary | The calibration slope is 0.9886 , inside the declared band r… | 0.9886 | ratio | calibration_slope | test | eq | `[[art:e06564c7:calibration_slope.test]]` | verified | 0.9885680158 |
| 9 | summary | The calibration slope is 0.9886 , inside the declared band r… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 10 | summary | The calibration slope is 0.9886 , inside the declared band r… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 11 | summary | The largest development-to-holdout distribution shift, score… | 0.003083 | ratio | psi |  | eq | `[[art:e1d82330:psi.max]]` | verified | 0.00308251646 |
| 12 | summary | The largest development-to-holdout distribution shift, score… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 13 | summary | Discrimination on the development split, at 0.7546 , sits cl… | 0.7546 | ratio | auc | train | eq | `[[art:01cf8178:metrics.train.auc]]` | verified | 0.7545552576 |
| 14 | summary | Across the slices of the held-out split reported here, the w… | 0.04359 | ratio | auc_gap | test | eq | `[[art:41c300dd:metrics.test.sub.limit_bal_high.auc_gap]]` | verified | 0.04358610017 |
| 15 | summary | Across the slices of the held-out split reported here, the w… | 0.513 | ratio | share | test | eq | `[[art:0f3d3609:metrics.test.sub.limit_bal_high.share]]` | verified | 0.513 |
| 16 | summary | As part of the outcomes analysis contemplated by the guidanc… | 0.02391 | ratio | delta_auc |  | eq | `[[art:3877bdd0:challenger.delta_auc]]` | verified | 0.02390594313 |
| 17 | summary | The design shows no acute collinearity, with a largest varia… | 3.544 | ratio | vif |  | eq | `[[art:d3785ba9:vif.max]]` | verified | 3.54357449 |
| 18 | summary | The design shows no acute collinearity, with a largest varia… | 4.279 | ratio | condition_number |  | eq | `[[art:ba0d9cc4:condition_number]]` | verified | 4.279282985 |
| 19 | conceptual_soundness | The champion is a single linear-in-coefficients scoring mode… | -1.442 | ratio | intercept |  | eq | `[[art:ca1c764c:run.model_summary#intercept]]` | verified | -1.441621171 |
| 20 | conceptual_soundness | The champion is a single linear-in-coefficients scoring mode… | 21000 | count | n_train | train | eq | `[[art:ca1c764c:run.model_summary#n_train]]` | verified | 21000 |
| 21 | conceptual_soundness | The declared feature inventory holds 12 features. | 12 | count | n |  | eq | `[[art:792cb79c:run.features#n]]` | verified | 12 |
| 22 | conceptual_soundness | Of those, 10 are known before the performance period opens a… | 10 | count | before_period_start |  | eq | `[[art:792cb79c:run.features#before_period_start]]` | verified | 10 |
| 23 | conceptual_soundness | Of those, 10 are known before the performance period opens a… | 2 | count | at_origination |  | eq | `[[art:792cb79c:run.features#at_origination]]` | verified | 2 |
| 24 | conceptual_soundness | None are observed during the performance period, 0 , and non… | 0 | count | during_period |  | eq | `[[art:792cb79c:run.features#during_period]]` | verified | 0 |
| 25 | conceptual_soundness | None are observed during the performance period, 0 , and non… | 0 | count | after_outcome |  | eq | `[[art:792cb79c:run.features#after_outcome]]` | verified | 0 |
| 26 | conceptual_soundness | The developer applied a collinearity screen with a cutoff of… | 10 | ratio | vif_threshold |  | eq | `[[art:ca1c764c:run.model_summary#vif_threshold]]` | verified | 10 |
| 27 | conceptual_soundness | It removed bill_last, whose inflation factor was 33.8 , and… | 33.8 | ratio | vif |  | eq | `[[art:ca1c764c:run.model_summary#removed.bill_last.vif]]` | verified | 33.803856 |
| 28 | conceptual_soundness | It removed bill_last, whose inflation factor was 33.8 , and… | 10.96 | ratio | vif |  | eq | `[[art:ca1c764c:run.model_summary#removed.utilisation_mean_6m.vif]]` | verified | 10.962284 |
| 29 | conceptual_soundness | The three delinquency terms carry the largest weights and al… | 0.4847 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.delinq_last.value]]` | verified | 0.4846949872 |
| 30 | conceptual_soundness | The three delinquency terms carry the largest weights and al… | 0.2801 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.delinq_count_6m.value]]` | verified | 0.2800755777 |
| 31 | conceptual_soundness | The three delinquency terms carry the largest weights and al… | 0.2263 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.delinq_max_6m.value]]` | verified | 0.2262527885 |
| 32 | conceptual_soundness | The next largest weight is on the credit limit, -0.2091 , an… | -0.2091 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.limit_bal.value]]` | verified | -0.2091380131 |
| 33 | conceptual_soundness | The remaining weights are small by comparison: pay_ratio_mea… | -0.09824 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.pay_ratio_mean_6m.value]]` | verified | -0.09823688664 |
| 34 | conceptual_soundness | The remaining weights are small by comparison: pay_ratio_mea… | -0.08257 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.utilisation.value]]` | verified | -0.08257487854 |
| 35 | conceptual_soundness | The remaining weights are small by comparison: pay_ratio_mea… | 0.07253 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.age.value]]` | verified | 0.07253007645 |
| 36 | conceptual_soundness | The remaining weights are small by comparison: pay_ratio_mea… | 0.04808 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.bill_trend_6m.value]]` | verified | 0.04808068095 |
| 37 | conceptual_soundness | The remaining weights are small by comparison: pay_ratio_mea… | -0.007568 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.bill_mean_6m.value]]` | verified | -0.007567968246 |
| 38 | conceptual_soundness | The remaining weights are small by comparison: pay_ratio_mea… | 0.00678 | ratio | coefficient |  | eq | `[[art:ca1c764c:run.model_summary#coefficients.pay_ratio_last.value]]` | verified | 0.006779706816 |
| 39 | conceptual_soundness | Among the retained features, the count whose fitted sign con… | 3 | count | n_disagreements | train | eq | `[[art:e223cd4a:sign_check.n_disagreements]]` | verified | 3 |
| 40 | conceptual_soundness | The three are utilisation, pay_ratio_last, and bill_trend_6m… | 0.755 | ratio | baseline_auc | test | eq | `[[art:789072f8:ablation.baseline_auc]]` | verified | 0.7550239453 |
| 41 | conceptual_soundness | Utilisation is fitted negative, -1 , while on its own it poi… | -1 | ratio | coef_sign |  | eq | `[[art:46230409:sign_check.utilisation.coef_sign]]` | verified | -1 |
| 42 | conceptual_soundness | Utilisation is fitted negative, -1 , while on its own it poi… | 1 | ratio | univariate_direction |  | eq | `[[art:f0995196:sign_check.utilisation.univariate_direction]]` | verified | 1 |
| 43 | conceptual_soundness | Utilisation is fitted negative, -1 , while on its own it poi… | 0 | ratio | agrees |  | eq | `[[art:cb5a7bc7:sign_check.utilisation.agrees]]` | verified | 0 |
| 44 | conceptual_soundness | Refitting without utilisation changes test AUC by 1.92e-05 ,… | 1.92e-05 | ratio | delta_auc | test | eq | `[[art:dc9ac505:ablation.utilisation.delta_auc]]` | verified | 1.920469764e-05 |
| 45 | conceptual_soundness | The most recent repayment ratio is fitted positive, 1 , agai… | 1 | ratio | coef_sign |  | eq | `[[art:f018263e:sign_check.pay_ratio_last.coef_sign]]` | verified | 1 |
| 46 | conceptual_soundness | The most recent repayment ratio is fitted positive, 1 , agai… | -1 | ratio | univariate_direction |  | eq | `[[art:f8e46d75:sign_check.pay_ratio_last.univariate_direction]]` | verified | -1 |
| 47 | conceptual_soundness | The most recent repayment ratio is fitted positive, 1 , agai… | 0 | ratio | agrees |  | eq | `[[art:79abee77:sign_check.pay_ratio_last.agrees]]` | verified | 0 |
| 48 | conceptual_soundness | A positive weight says a larger last repayment raises the sc… | -5.589e-05 | ratio | delta_auc | test | eq | `[[art:e26d8112:ablation.pay_ratio_last.delta_auc]]` | verified | -5.589426925e-05 |
| 49 | conceptual_soundness | The six-month billing trend is fitted positive, 1 , against… | 1 | ratio | coef_sign |  | eq | `[[art:abd4aaba:sign_check.bill_trend_6m.coef_sign]]` | verified | 1 |
| 50 | conceptual_soundness | The six-month billing trend is fitted positive, 1 , against… | -1 | ratio | univariate_direction |  | eq | `[[art:a9bff389:sign_check.bill_trend_6m.univariate_direction]]` | verified | -1 |
| 51 | conceptual_soundness | The six-month billing trend is fitted positive, 1 , against… | 0 | ratio | agrees |  | eq | `[[art:c0f6d07d:sign_check.bill_trend_6m.agrees]]` | verified | 0 |
| 52 | conceptual_soundness | This is the disagreement that matters most of the three: ref… | -0.001393 | ratio | delta_auc | test | eq | `[[art:99f9dd71:ablation.bill_trend_6m.delta_auc]]` | verified | -0.001392555557 |
| 53 | conceptual_soundness | The features whose fitted signs agree with their univariate… | 1 | ratio | agrees |  | eq | `[[art:a8ba9372:sign_check.delinq_last.agrees]]` | verified | 1 |
| 54 | conceptual_soundness | The features whose fitted signs agree with their univariate… | 1 | ratio | agrees |  | eq | `[[art:a337d16b:sign_check.delinq_count_6m.agrees]]` | verified | 1 |
| 55 | conceptual_soundness | The features whose fitted signs agree with their univariate… | 1 | ratio | agrees |  | eq | `[[art:da92a015:sign_check.delinq_max_6m.agrees]]` | verified | 1 |
| 56 | conceptual_soundness | The features whose fitted signs agree with their univariate… | 1 | ratio | agrees |  | eq | `[[art:103d99fb:sign_check.limit_bal.agrees]]` | verified | 1 |
| 57 | conceptual_soundness | The features whose fitted signs agree with their univariate… | 1 | ratio | agrees |  | eq | `[[art:7e9a76ca:sign_check.pay_ratio_mean_6m.agrees]]` | verified | 1 |
| 58 | conceptual_soundness | The features whose fitted signs agree with their univariate… | 1 | ratio | agrees |  | eq | `[[art:89279c3b:sign_check.bill_mean_6m.agrees]]` | verified | 1 |
| 59 | conceptual_soundness | The features whose fitted signs agree with their univariate… | 1 | ratio | agrees |  | eq | `[[art:4116add1:sign_check.age.agrees]]` | verified | 1 |
| 60 | conceptual_soundness | The weight the model places on each of these is visible in t… | -0.005914 | ratio | delta_auc | test | eq | `[[art:40f4e6bf:ablation.delinq_last.delta_auc]]` | verified | -0.005913828665 |
| 61 | conceptual_soundness | The weight the model places on each of these is visible in t… | -0.003748 | ratio | delta_auc | test | eq | `[[art:57710b23:ablation.limit_bal.delta_auc]]` | verified | -0.003748140709 |
| 62 | conceptual_soundness | The weight the model places on each of these is visible in t… | -0.002225 | ratio | delta_auc | test | eq | `[[art:f6fdd709:ablation.age.delta_auc]]` | verified | -0.002224986043 |
| 63 | conceptual_soundness | The weight the model places on each of these is visible in t… | -0.002146 | ratio | delta_auc | test | eq | `[[art:db90576e:ablation.delinq_count_6m.delta_auc]]` | verified | -0.002145551687 |
| 64 | conceptual_soundness | The weight the model places on each of these is visible in t… | -0.001133 | ratio | delta_auc | test | eq | `[[art:18cb1559:ablation.delinq_max_6m.delta_auc]]` | verified | -0.001133363798 |
| 65 | conceptual_soundness | The weight the model places on each of these is visible in t… | -0.0009816 | ratio | delta_auc | test | eq | `[[art:cba98844:ablation.pay_ratio_mean_6m.delta_auc]]` | verified | -0.0009815893593 |
| 66 | conceptual_soundness | The weight the model places on each of these is visible in t… | -0.0001527 | ratio | delta_auc | test | eq | `[[art:5b4423ab:ablation.bill_mean_6m.delta_auc]]` | verified | -0.00015270601 |
| 67 | conceptual_soundness | The champion scores 0.755 AUC on test with a Brier score of… | 0.755 | ratio | auc | test | eq | `[[art:365b7034:metrics.test.auc]]` | verified | 0.7550239453 |
| 68 | conceptual_soundness | The champion scores 0.755 AUC on test with a Brier score of… | 0.1385 | ratio | brier | test | eq | `[[art:86e93c8f:metrics.test.brier]]` | verified | 0.1385162411 |
| 69 | conceptual_soundness | The challenger reaches 0.7789 AUC on the same test data with… | 0.7789 | ratio | auc | test | eq | `[[art:5646e7f3:challenger.auc]]` | verified | 0.7789298885 |
| 70 | conceptual_soundness | The challenger reaches 0.7789 AUC on the same test data with… | 0.135 | ratio | brier | test | eq | `[[art:2031a154:challenger.brier]]` | verified | 0.1349523392 |
| 71 | conceptual_soundness | The challenger's lead in AUC is 0.02391 . | 0.02391 | ratio | delta_auc | test | eq | `[[art:3877bdd0:challenger.delta_auc]]` | verified | 0.02390594313 |
| 72 | conceptual_soundness | The threshold set for this review treats a challenger lead a… | 0.03 | ratio | delta_auc |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 73 | data_integrity | The training split holds 21000 rows and the test split holds… | 21000 | count | n | train | eq | `[[art:a359de9d:profile.train.n]]` | verified | 21000 |
| 74 | data_integrity | The training split holds 21000 rows and the test split holds… | 9000 | count | n | test | eq | `[[art:abbe1a27:profile.test.n]]` | verified | 9000 |
| 75 | data_integrity | The largest missing fraction over any column of the training… | 0 | ratio | missing.max | train | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 76 | data_integrity | The largest missing fraction over any column of the training… | 0 | ratio | missing.max | test | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 77 | data_integrity | The two split maxima are therefore identical, so the gap bet… | 0.1 | ratio | missing_gap |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 78 | data_integrity | The declared stability bound for the training split measured… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 79 | data_integrity | The declared stability bound for the training split measured… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 80 | data_integrity | The largest population stability index across all features a… | 0.003083 | ratio | psi |  | eq | `[[art:e1d82330:psi.max]]` | verified | 0.00308251646 |
| 81 | data_integrity | - age: 0.003083 | 0.003083 | ratio | psi |  | eq | `[[art:06c22a63:psi.age]]` | verified | 0.00308251646 |
| 82 | data_integrity | - credit limit: 0.001272 | 0.001272 | ratio | psi |  | eq | `[[art:b0195847:psi.limit_bal]]` | verified | 0.001272099805 |
| 83 | data_integrity | - utilisation: 0.0006523 | 0.0006523 | ratio | psi |  | eq | `[[art:f094559b:psi.utilisation]]` | verified | 0.0006522718782 |
| 84 | data_integrity | - six-month bill mean: 0.001488 | 0.001488 | ratio | psi |  | eq | `[[art:127cdf82:psi.bill_mean_6m]]` | verified | 0.001488231386 |
| 85 | data_integrity | - six-month bill trend: 0.0007484 | 0.0007484 | ratio | psi |  | eq | `[[art:78be70d2:psi.bill_trend_6m]]` | verified | 0.0007484247754 |
| 86 | data_integrity | - six-month delinquency count: 0.001856 | 0.001856 | ratio | psi |  | eq | `[[art:d77ddb1d:psi.delinq_count_6m]]` | verified | 0.00185562271 |
| 87 | data_integrity | - six-month delinquency maximum: 0.001027 | 0.001027 | ratio | psi |  | eq | `[[art:4b0a94ab:psi.delinq_max_6m]]` | verified | 0.001026806992 |
| 88 | data_integrity | - most recent delinquency: 0.0002347 | 0.0002347 | ratio | psi |  | eq | `[[art:cbc9de36:psi.delinq_last]]` | verified | 0.0002346592849 |
| 89 | data_integrity | - most recent payment ratio: 0.002264 | 0.002264 | ratio | psi |  | eq | `[[art:82c97112:psi.pay_ratio_last]]` | verified | 0.0022643364 |
| 90 | data_integrity | - six-month mean payment ratio: 0.001028 | 0.001028 | ratio | psi |  | eq | `[[art:62e0e0f8:psi.pay_ratio_mean_6m]]` | verified | 0.001027537662 |
| 91 | data_integrity | - model score: 0.001368 | 0.001368 | ratio | psi |  | eq | `[[art:ec2b8d1b:psi.y_score]]` | verified | 0.001367653962 |
| 92 | data_integrity | Age is the widest of these at 0.003083 and sets the maximum,… | 0.003083 | ratio | psi |  | eq | `[[art:06c22a63:psi.age]]` | verified | 0.00308251646 |
| 93 | data_integrity | Age is the widest of these at 0.003083 and sets the maximum,… | 0.001368 | ratio | psi |  | eq | `[[art:ec2b8d1b:psi.y_score]]` | verified | 0.001367653962 |
| 94 | data_integrity | Characteristic stability, which weights each feature's shift… | 0.004737 | ratio | csi |  | eq | `[[art:ce1257d8:csi.max]]` | verified | 0.00473710965 |
| 95 | data_integrity | - age: 0.001203 | 0.001203 | ratio | csi |  | eq | `[[art:25b88f37:csi.age]]` | verified | 0.001203264027 |
| 96 | data_integrity | - credit limit: 0.001384 | 0.001384 | ratio | csi |  | eq | `[[art:c91a2a4b:csi.limit_bal]]` | verified | 0.001384099928 |
| 97 | data_integrity | - utilisation: 0.0002136 | 0.0002136 | ratio | csi |  | eq | `[[art:6ed37e42:csi.utilisation]]` | verified | 0.0002135922405 |
| 98 | data_integrity | - six-month bill mean: 9.982e-06 | 9.982e-06 | ratio | csi |  | eq | `[[art:0c34001d:csi.bill_mean_6m]]` | verified | 9.982086887e-06 |
| 99 | data_integrity | - six-month bill trend: 0.0003675 | 0.0003675 | ratio | csi |  | eq | `[[art:9e5a9b68:csi.bill_trend_6m]]` | verified | 0.0003674527783 |
| 100 | data_integrity | - six-month delinquency count: 0.0008781 | 0.0008781 | ratio | csi |  | eq | `[[art:f0438233:csi.delinq_count_6m]]` | verified | 0.0008781439663 |
| 101 | data_integrity | - six-month delinquency maximum: 0.004737 | 0.004737 | ratio | csi |  | eq | `[[art:35990a39:csi.delinq_max_6m]]` | verified | 0.00473710965 |
| 102 | data_integrity | - most recent delinquency: 0.001698 | 0.001698 | ratio | csi |  | eq | `[[art:e755cf0a:csi.delinq_last]]` | verified | 0.001697603731 |
| 103 | data_integrity | - most recent payment ratio: 0.0001132 | 0.0001132 | ratio | csi |  | eq | `[[art:5898a9c5:csi.pay_ratio_last]]` | verified | 0.0001131831266 |
| 104 | data_integrity | - six-month mean payment ratio: 0.002043 | 0.002043 | ratio | csi |  | eq | `[[art:5e53c153:csi.pay_ratio_mean_6m]]` | verified | 0.002042601165 |
| 105 | data_integrity | The ordering differs from the population view, in that the d… | 0.004737 | ratio | csi |  | eq | `[[art:ce1257d8:csi.max]]` | verified | 0.00473710965 |
| 106 | data_integrity | The ordering differs from the population view, in that the d… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 107 | data_integrity | The timing screen reads the declared observation window of e… | 0 | count | leakage.timing.n_flagged |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 108 | data_integrity | The target-association screen fits each feature alone agains… | 0.728 | ratio | auc |  | eq | `[[art:2e212f3a:leakage.target_corr.max_single_feature_auc]]` | verified | 0.7279795601 |
| 109 | data_integrity | The target-association screen fits each feature alone agains… | 0.9 | ratio | auc |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 110 | data_integrity | On identifiers, the share of test rows whose client identifi… | 0 | ratio | leakage.overlap.ids | test | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 111 | data_integrity | On identifiers, the share of test rows whose client identifi… | 0.005 | ratio | leakage.overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 112 | data_integrity | On feature vectors, the share of test rows whose feature val… | 0.01256 | ratio | leakage.overlap.features | test | eq | `[[art:517f3049:leakage.overlap.features]]` | verified | 0.01255555556 |
| 113 | data_integrity | On feature vectors, the share of test rows whose feature val… | 0.01256 | ratio | leakage.overlap |  | eq | `[[art:ebd7ff30:leakage.overlap]]` | verified | 0.01255555556 |
| 114 | data_integrity | This arm is read against the bound the rule actually applied… | 0.02324 | ratio | leakage.overlap.features |  | eq | `[[art:7cdc63cb:threshold.L2.overlap.features_effective]]` | verified | 0.02323809524 |
| 115 | data_integrity | This arm is read against the bound the rule actually applied… | 0.01162 | ratio | leakage.duplicates | train | eq | `[[art:c988bb0e:leakage.duplicates.train]]` | verified | 0.01161904762 |
| 116 | data_integrity | Read against that applied bound of 0.02324 , the feature-vec… | 0.02324 | ratio | leakage.overlap.features |  | eq | `[[art:7cdc63cb:threshold.L2.overlap.features_effective]]` | verified | 0.02323809524 |
| 117 | data_integrity | Read against that applied bound of 0.02324 , the feature-vec… | 0.01256 | ratio | leakage.overlap.features | test | eq | `[[art:517f3049:leakage.overlap.features]]` | verified | 0.01255555556 |
| 118 | data_integrity | Read against that applied bound of 0.02324 , the feature-vec… | 0 | ratio | leakage.overlap.ids | test | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 119 | data_integrity | The name screen matches feature names against a lexicon of t… | 0 | count | leakage.name_screen.n_matched |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 120 | data_integrity | The residual caveat is that the feature-overlap arm is judge… | 0 | ratio | leakage.overlap.ids | test | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 121 | outcomes | This section reports discrimination first and calibration se… | 0.2212 | ratio | event_rate | test | eq | `[[art:f60ae2a7:metrics.test.event_rate]]` | verified | 0.2212222222 |
| 122 | outcomes | This section reports discrimination first and calibration se… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 123 | outcomes | \| Rows scored \| 21000 \| 9000 \| | 21000 | count | n | train | eq | `[[art:1721ceae:metrics.train.n]]` | verified | 21000 |
| 124 | outcomes | \| Rows scored \| 21000 \| 9000 \| | 9000 | count | n | test | eq | `[[art:5367a59f:metrics.test.n]]` | verified | 9000 |
| 125 | outcomes | \| Observed event rate \| 0.2212 \| 0.2212 \| | 0.2212 | ratio | event_rate | train | eq | `[[art:657aa7fc:metrics.train.event_rate]]` | verified | 0.2211904762 |
| 126 | outcomes | \| Observed event rate \| 0.2212 \| 0.2212 \| | 0.2212 | ratio | event_rate | test | eq | `[[art:f60ae2a7:metrics.test.event_rate]]` | verified | 0.2212222222 |
| 127 | outcomes | \| AUC \| 0.7546 \| 0.755 \| | 0.7546 | ratio | auc | train | eq | `[[art:01cf8178:metrics.train.auc]]` | verified | 0.7545552576 |
| 128 | outcomes | \| AUC \| 0.7546 \| 0.755 \| | 0.755 | ratio | auc | test | eq | `[[art:365b7034:metrics.test.auc]]` | verified | 0.7550239453 |
| 129 | outcomes | \| Gini \| 0.5091 \| 0.51 \| | 0.5091 | ratio | gini | train | eq | `[[art:eaaf0f79:metrics.train.gini]]` | verified | 0.5091105152 |
| 130 | outcomes | \| Gini \| 0.5091 \| 0.51 \| | 0.51 | ratio | gini | test | eq | `[[art:296bfeeb:metrics.test.gini]]` | verified | 0.5100478906 |
| 131 | outcomes | \| KS \| 0.4144 \| 0.4067 \| | 0.4144 | ratio | ks | train | eq | `[[art:18df22bd:metrics.train.ks]]` | verified | 0.4144375385 |
| 132 | outcomes | \| KS \| 0.4144 \| 0.4067 \| | 0.4067 | ratio | ks | test | eq | `[[art:d3c4ed61:metrics.test.ks]]` | verified | 0.4066831201 |
| 133 | outcomes | \| Brier score \| 0.1384 \| 0.1385 \| | 0.1384 | ratio | brier | train | eq | `[[art:c95106e9:metrics.train.brier]]` | verified | 0.1383762773 |
| 134 | outcomes | \| Brier score \| 0.1384 \| 0.1385 \| | 0.1385 | ratio | brier | test | eq | `[[art:86e93c8f:metrics.test.brier]]` | verified | 0.1385162411 |
| 135 | outcomes | \| Log loss \| 0.4439 \| 0.4442 \| | 0.4439 | ratio | logloss | train | eq | `[[art:b816b083:metrics.train.logloss]]` | verified | 0.4439401117 |
| 136 | outcomes | \| Log loss \| 0.4439 \| 0.4442 \| | 0.4442 | ratio | logloss | test | eq | `[[art:2de58c1b:metrics.test.logloss]]` | verified | 0.4441654047 |
| 137 | outcomes | \| Mean predicted probability \| 0.2212 \| 0.2206 \| | 0.2212 | ratio | mean_predicted | train | eq | `[[art:935d2cb7:metrics.train.mean_predicted]]` | verified | 0.2212248699 |
| 138 | outcomes | \| Mean predicted probability \| 0.2212 \| 0.2206 \| | 0.2206 | ratio | mean_predicted | test | eq | `[[art:89d241ea:metrics.test.mean_predicted]]` | verified | 0.2205710384 |
| 139 | outcomes | Rank ordering concentrates events in the highest-scoring dec… | 0.5031 | ratio | top2_capture | train | eq | `[[art:5131afa7:deciles.train.top2_capture]]` | verified | 0.5031216362 |
| 140 | outcomes | Rank ordering concentrates events in the highest-scoring dec… | 0.4952 | ratio | top2_capture | test | eq | `[[art:e2c0ad9f:deciles.test.top2_capture]]` | verified | 0.4952285284 |
| 141 | outcomes | AUC on the evaluation split, 0.755 , is not below AUC on the… | 0.755 | ratio | auc | test | eq | `[[art:365b7034:metrics.test.auc]]` | verified | 0.7550239453 |
| 142 | outcomes | AUC on the evaluation split, 0.755 , is not below AUC on the… | 0.7546 | ratio | auc | train | eq | `[[art:01cf8178:metrics.train.auc]]` | verified | 0.7545552576 |
| 143 | outcomes | AUC on the evaluation split, 0.755 , is not below AUC on the… | 0.08 | ratio | auc_gap |  | eq | `[[art:630f28f4:threshold.O1.auc_gap]]` | verified | 0.08 |
| 144 | outcomes | The logistic regression of the outcome on the logit of the p… | 0.9886 | ratio | calibration_slope | test | eq | `[[art:e06564c7:calibration_slope.test]]` | verified | 0.9885680158 |
| 145 | outcomes | The logistic regression of the outcome on the logit of the p… | 0.8 | ratio | calibration_slope |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 146 | outcomes | The logistic regression of the outcome on the logit of the p… | 1.2 | ratio | calibration_slope |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 147 | outcomes | The logistic regression of the outcome on the logit of the p… | 1.001 | ratio | calibration_slope | train | eq | `[[art:85461245:calibration_slope.train]]` | verified | 1.000539237 |
| 148 | outcomes | The same regression gives an intercept of -0.008632 on the e… | -0.008632 | ratio | calibration_intercept | test | eq | `[[art:2ee976d3:calibration_intercept.test]]` | verified | -0.008632158167 |
| 149 | outcomes | The same regression gives an intercept of -0.008632 on the e… | 0.0003779 | ratio | calibration_intercept | train | eq | `[[art:2ce8cd09:calibration_intercept.train]]` | verified | 0.0003779479547 |
| 150 | outcomes | Mean predicted probability on the evaluation split is 0.2206… | 0.2206 | ratio | mean_predicted | test | eq | `[[art:89d241ea:metrics.test.mean_predicted]]` | verified | 0.2205710384 |
| 151 | outcomes | Mean predicted probability on the evaluation split is 0.2206… | 0.2212 | ratio | event_rate | test | eq | `[[art:f60ae2a7:metrics.test.event_rate]]` | verified | 0.2212222222 |
| 152 | outcomes | Mean predicted probability on the evaluation split is 0.2206… | 0.002944 | ratio | mean_rel_gap | test | eq | `[[art:bae28fd6:calibration.mean_rel_gap.test]]` | verified | 0.00294357342 |
| 153 | outcomes | Mean predicted probability on the evaluation split is 0.2206… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 154 | outcomes | The corresponding relative gap on the development split is 0… | 0.0001555 | ratio | mean_rel_gap | train | eq | `[[art:a03ea014:calibration.mean_rel_gap.train]]` | verified | 0.0001554936592 |
| 155 | outcomes | AUC on this slice falls 0.007286 below the evaluation split'… | 0.007286 | ratio | auc_gap | test | eq | `[[art:15e1edcb:metrics.test.sub.limit_bal_low.auc_gap]]` | verified | 0.007286037626 |
| 156 | outcomes | AUC on this slice falls 0.007286 below the evaluation split'… | -0.001109 | ratio | auc_gap | train | eq | `[[art:021950a5:metrics.train.sub.limit_bal_low.auc_gap]]` | verified | -0.001109116413 |
| 157 | outcomes | AUC on this slice falls 0.007286 below the evaluation split'… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 158 | outcomes | The slice holds 0.487 of the evaluation split and 0.4837 of… | 0.487 | ratio | share | test | eq | `[[art:e7847e2b:metrics.test.sub.limit_bal_low.share]]` | verified | 0.487 |
| 159 | outcomes | The slice holds 0.487 of the evaluation split and 0.4837 of… | 0.4837 | ratio | share | train | eq | `[[art:d4eb837c:metrics.train.sub.limit_bal_low.share]]` | verified | 0.4837142857 |
| 160 | outcomes | The slice holds 0.487 of the evaluation split and 0.4837 of… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 161 | outcomes | Mean predicted probability of 0.2802 sits just under an obse… | 0.2802 | ratio | mean_predicted | test | eq | `[[art:e3d342d5:metrics.test.sub.limit_bal_low.mean_predicted]]` | verified | 0.2801722167 |
| 162 | outcomes | Mean predicted probability of 0.2802 sits just under an obse… | 0.2877 | ratio | event_rate | test | eq | `[[art:9629805c:metrics.test.sub.limit_bal_low.event_rate]]` | verified | 0.2877024869 |
| 163 | outcomes | AUC on the high-limit half falls 0.04359 below the evaluatio… | 0.04359 | ratio | auc_gap | test | eq | `[[art:41c300dd:metrics.test.sub.limit_bal_high.auc_gap]]` | verified | 0.04358610017 |
| 164 | outcomes | AUC on the high-limit half falls 0.04359 below the evaluatio… | 0.04609 | ratio | auc_gap | train | eq | `[[art:b9498743:metrics.train.sub.limit_bal_high.auc_gap]]` | verified | 0.04608975444 |
| 165 | outcomes | AUC on the high-limit half falls 0.04359 below the evaluatio… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 166 | outcomes | The slice holds 0.513 of the evaluation split and 0.5163 of… | 0.513 | ratio | share | test | eq | `[[art:0f3d3609:metrics.test.sub.limit_bal_high.share]]` | verified | 0.513 |
| 167 | outcomes | The slice holds 0.513 of the evaluation split and 0.5163 of… | 0.5163 | ratio | share | train | eq | `[[art:59ef1a64:metrics.train.sub.limit_bal_high.share]]` | verified | 0.5162857143 |
| 168 | outcomes | The slice holds 0.513 of the evaluation split and 0.5163 of… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 169 | outcomes | Mean predicted probability of 0.164 against an observed rate… | 0.164 | ratio | mean_predicted | test | eq | `[[art:c30b141c:metrics.test.sub.limit_bal_high.mean_predicted]]` | verified | 0.1639905825 |
| 170 | outcomes | Mean predicted probability of 0.164 against an observed rate… | 0.1581 | ratio | event_rate | test | eq | `[[art:6c8ff585:metrics.test.sub.limit_bal_high.event_rate]]` | verified | 0.1581113277 |
| 171 | outcomes | AUC on this slice falls 0 below the evaluation split's own a… | 0 | ratio | auc_gap | test | eq | `[[art:5125fbea:metrics.test.sub.delinq_count_6m_high.auc_gap]]` | verified | 0 |
| 172 | outcomes | AUC on this slice falls 0 below the evaluation split's own a… | 0 | ratio | auc_gap | train | eq | `[[art:48e23659:metrics.train.sub.delinq_count_6m_high.auc_gap]]` | verified | 0 |
| 173 | outcomes | AUC on this slice falls 0 below the evaluation split's own a… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 174 | outcomes | The slice holds 1 of the evaluation split and 1 of the devel… | 1 | ratio | share | test | eq | `[[art:dd55d203:metrics.test.sub.delinq_count_6m_high.share]]` | verified | 1 |
| 175 | outcomes | The slice holds 1 of the evaluation split and 1 of the devel… | 1 | ratio | share | train | eq | `[[art:025f5eaa:metrics.train.sub.delinq_count_6m_high.share]]` | verified | 1 |
| 176 | outcomes | The slice holds 1 of the evaluation split and 1 of the devel… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 177 | outcomes | Mean predicted probability of 0.2206 against an observed rat… | 0.2206 | ratio | mean_predicted | test | eq | `[[art:a703edcb:metrics.test.sub.delinq_count_6m_high.mean_predicted]]` | verified | 0.2205710384 |
| 178 | outcomes | Mean predicted probability of 0.2206 against an observed rat… | 0.2212 | ratio | event_rate | test | eq | `[[art:951c81ed:metrics.test.sub.delinq_count_6m_high.event_rate]]` | verified | 0.2212222222 |
| 179 | outcomes | AUC on this slice falls -0.02309 below the evaluation split'… | -0.02309 | ratio | auc_gap | test | eq | `[[art:7132f197:metrics.test.sub.utilisation_high.auc_gap]]` | verified | -0.02309035011 |
| 180 | outcomes | AUC on this slice falls -0.02309 below the evaluation split'… | -0.02732 | ratio | auc_gap | train | eq | `[[art:41fca294:metrics.train.sub.utilisation_high.auc_gap]]` | verified | -0.02732151154 |
| 181 | outcomes | AUC on this slice falls -0.02309 below the evaluation split'… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 182 | outcomes | The slice holds 0.5 of the evaluation split and 0.5 of the d… | 0.5 | ratio | share | test | eq | `[[art:9404484e:metrics.test.sub.utilisation_high.share]]` | verified | 0.5 |
| 183 | outcomes | The slice holds 0.5 of the evaluation split and 0.5 of the d… | 0.5 | ratio | share | train | eq | `[[art:0ff76e00:metrics.train.sub.utilisation_high.share]]` | verified | 0.5 |
| 184 | outcomes | The slice holds 0.5 of the evaluation split and 0.5 of the d… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 185 | outcomes | Mean predicted probability of 0.2608 sits a little below an… | 0.2608 | ratio | mean_predicted | test | eq | `[[art:e68f1a3d:metrics.test.sub.utilisation_high.mean_predicted]]` | verified | 0.2608314072 |
| 186 | outcomes | Mean predicted probability of 0.2608 sits a little below an… | 0.2658 | ratio | event_rate | test | eq | `[[art:e4a00a59:metrics.test.sub.utilisation_high.event_rate]]` | verified | 0.2657777778 |
| 187 | sensitivity | The largest variance inflation factor across the retained fe… | 3.544 | ratio | vif |  | eq | `[[art:d3785ba9:vif.max]]` | verified | 3.54357449 |
| 188 | sensitivity | The largest variance inflation factor across the retained fe… | 10 | ratio | vif |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 189 | sensitivity | That largest value belongs to the six-month delinquency coun… | 3.544 | ratio | vif |  | eq | `[[art:7273e0be:vif.delinq_count_6m]]` | verified | 3.54357449 |
| 190 | sensitivity | The six-month delinquency maximum is next, at 3.484 . | 3.484 | ratio | vif |  | eq | `[[art:e7b701a1:vif.delinq_max_6m]]` | verified | 3.483514414 |
| 191 | sensitivity | The six-month mean payment ratio is 3.027 and utilisation is… | 3.027 | ratio | vif |  | eq | `[[art:2cda5cfc:vif.pay_ratio_mean_6m]]` | verified | 3.026650797 |
| 192 | sensitivity | The six-month mean payment ratio is 3.027 and utilisation is… | 2.829 | ratio | vif |  | eq | `[[art:6ce4c102:vif.utilisation]]` | verified | 2.829009901 |
| 193 | sensitivity | The most recent payment ratio is 2.714 , the six-month mean… | 2.714 | ratio | vif |  | eq | `[[art:b68613a6:vif.pay_ratio_last]]` | verified | 2.713577274 |
| 194 | sensitivity | The most recent payment ratio is 2.714 , the six-month mean… | 2.265 | ratio | vif |  | eq | `[[art:87cb4e54:vif.bill_mean_6m]]` | verified | 2.264665681 |
| 195 | sensitivity | The most recent payment ratio is 2.714 , the six-month mean… | 2.321 | ratio | vif |  | eq | `[[art:59461811:vif.delinq_last]]` | verified | 2.320694749 |
| 196 | sensitivity | The credit limit is 2.097 , the six-month bill trend is 1.33… | 2.097 | ratio | vif |  | eq | `[[art:0c6efb3f:vif.limit_bal]]` | verified | 2.096817173 |
| 197 | sensitivity | The credit limit is 2.097 , the six-month bill trend is 1.33… | 1.33 | ratio | vif |  | eq | `[[art:6d3f01ce:vif.bill_trend_6m]]` | verified | 1.330477005 |
| 198 | sensitivity | The credit limit is 2.097 , the six-month bill trend is 1.33… | 1.025 | ratio | vif |  | eq | `[[art:692cd6e9:vif.age]]` | verified | 1.024899403 |
| 199 | sensitivity | Belsley's condition number of the column-standardised design… | 4.279 | ratio | condition_number |  | eq | `[[art:ba0d9cc4:condition_number]]` | verified | 4.279282985 |
| 200 | sensitivity | Belsley's condition number of the column-standardised design… | 30 | ratio | condition_number |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 201 | monitoring | Input and score stability should be monitored at the highest… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 202 | monitoring | The validation reading of 0.003083 is the reference point fo… | 0.003083 | ratio | psi |  | eq | `[[art:e1d82330:psi.max]]` | verified | 0.00308251646 |
| 203 | monitoring | Discrimination should be tracked on each production cohort o… | 0.7 | ratio | auc | test | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 204 | monitoring | The validation reading of 0.755 sits above that floor by a m… | 0.755 | ratio | auc | test | eq | `[[art:365b7034:metrics.test.auc]]` | verified | 0.7550239453 |
| 205 | monitoring | Probability accuracy should be tracked on the same quarterly… | 0.2 | ratio | brier | test | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 206 | monitoring | Probability accuracy should be tracked on the same quarterly… | 0.1385 | ratio | brier | test | eq | `[[art:86e93c8f:metrics.test.brier]]` | verified | 0.1385162411 |
| 207 | monitoring | Calibration should be tracked by regressing the realized out… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 208 | monitoring | Calibration should be tracked by regressing the realized out… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 209 | monitoring | The validation reading of 0.9886 sits near the centre of tha… | 0.9886 | ratio | calibration_slope | test | eq | `[[art:e06564c7:calibration_slope.test]]` | verified | 0.9885680158 |
| 210 | monitoring | Where a monitoring cohort's observed event rate falls below… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |

## Appendix B — Artifact index

The store holds 258 artifacts; the 159 this report cites or rests a finding on are indexed here.

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
| `condition_number` | `ba0d9cc4` | scalar | 4.279282985 | Belsley's condition number of the column-standardised design |
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
| `metrics.test.sub.delinq_count_6m_high` | `55bd496f` | table | table, 9 rows | every metric on the delinq_count_6m above_median slice of test |
| `metrics.test.sub.delinq_count_6m_high.auc_gap` | `5125fbea` | scalar | 0 | how far AUC on the delinq_count_6m above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.delinq_count_6m_high.event_rate` | `951c81ed` | scalar | 0.2212222222 | event_rate on the delinq_count_6m above_median slice of test |
| `metrics.test.sub.delinq_count_6m_high.mean_predicted` | `a703edcb` | scalar | 0.2205710384 | mean_predicted on the delinq_count_6m above_median slice of test |
| `metrics.test.sub.delinq_count_6m_high.share` | `dd55d203` | scalar | 1 | the share of test the delinq_count_6m above_median slice holds |
| `metrics.test.sub.limit_bal_high` | `1fdb46f8` | table | table, 9 rows | every metric on the limit_bal above_median slice of test |
| `metrics.test.sub.limit_bal_high.auc_gap` | `41c300dd` | scalar | 0.04358610017 | how far AUC on the limit_bal above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.limit_bal_high.event_rate` | `6c8ff585` | scalar | 0.1581113277 | event_rate on the limit_bal above_median slice of test |
| `metrics.test.sub.limit_bal_high.mean_predicted` | `c30b141c` | scalar | 0.1639905825 | mean_predicted on the limit_bal above_median slice of test |
| `metrics.test.sub.limit_bal_high.share` | `0f3d3609` | scalar | 0.513 | the share of test the limit_bal above_median slice holds |
| `metrics.test.sub.limit_bal_low` | `c0819f02` | table | table, 9 rows | every metric on the limit_bal below_median slice of test |
| `metrics.test.sub.limit_bal_low.auc_gap` | `15e1edcb` | scalar | 0.007286037626 | how far AUC on the limit_bal below_median slice of test falls below AUC on all of test |
| `metrics.test.sub.limit_bal_low.event_rate` | `9629805c` | scalar | 0.2877024869 | event_rate on the limit_bal below_median slice of test |
| `metrics.test.sub.limit_bal_low.mean_predicted` | `e3d342d5` | scalar | 0.2801722167 | mean_predicted on the limit_bal below_median slice of test |
| `metrics.test.sub.limit_bal_low.share` | `e7847e2b` | scalar | 0.487 | the share of test the limit_bal below_median slice holds |
| `metrics.test.sub.utilisation_high` | `b866a9dd` | table | table, 9 rows | every metric on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.auc_gap` | `7132f197` | scalar | -0.02309035011 | how far AUC on the utilisation above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.utilisation_high.event_rate` | `e4a00a59` | scalar | 0.2657777778 | event_rate on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.mean_predicted` | `e68f1a3d` | scalar | 0.2608314072 | mean_predicted on the utilisation above_median slice of test |
| `metrics.test.sub.utilisation_high.share` | `9404484e` | scalar | 0.5 | the share of test the utilisation above_median slice holds |
| `metrics.train.auc` | `01cf8178` | scalar | 0.7545552576 | auc on train, recomputed by quaestor |
| `metrics.train.brier` | `c95106e9` | scalar | 0.1383762773 | brier on train, recomputed by quaestor |
| `metrics.train.event_rate` | `657aa7fc` | scalar | 0.2211904762 | event_rate on train, recomputed by quaestor |
| `metrics.train.gini` | `eaaf0f79` | scalar | 0.5091105152 | gini on train, recomputed by quaestor |
| `metrics.train.ks` | `18df22bd` | scalar | 0.4144375385 | ks on train, recomputed by quaestor |
| `metrics.train.logloss` | `b816b083` | scalar | 0.4439401117 | logloss on train, recomputed by quaestor |
| `metrics.train.mean_predicted` | `935d2cb7` | scalar | 0.2212248699 | mean_predicted on train, recomputed by quaestor |
| `metrics.train.n` | `1721ceae` | scalar | 21000 | n on train, recomputed by quaestor |
| `metrics.train.sub.delinq_count_6m_high` | `400c814d` | table | table, 9 rows | every metric on the delinq_count_6m above_median slice of train |
| `metrics.train.sub.delinq_count_6m_high.auc_gap` | `48e23659` | scalar | 0 | how far AUC on the delinq_count_6m above_median slice of train falls below AUC on all of train |
| `metrics.train.sub.delinq_count_6m_high.share` | `025f5eaa` | scalar | 1 | the share of train the delinq_count_6m above_median slice holds |
| `metrics.train.sub.limit_bal_high` | `3f1e33d4` | table | table, 9 rows | every metric on the limit_bal above_median slice of train |
| `metrics.train.sub.limit_bal_high.auc_gap` | `b9498743` | scalar | 0.04608975444 | how far AUC on the limit_bal above_median slice of train falls below AUC on all of train |
| `metrics.train.sub.limit_bal_high.share` | `59ef1a64` | scalar | 0.5162857143 | the share of train the limit_bal above_median slice holds |
| `metrics.train.sub.limit_bal_low` | `87a13a33` | table | table, 9 rows | every metric on the limit_bal below_median slice of train |
| `metrics.train.sub.limit_bal_low.auc_gap` | `021950a5` | scalar | -0.001109116413 | how far AUC on the limit_bal below_median slice of train falls below AUC on all of train |
| `metrics.train.sub.limit_bal_low.share` | `d4eb837c` | scalar | 0.4837142857 | the share of train the limit_bal below_median slice holds |
| `metrics.train.sub.utilisation_high` | `7feaf808` | table | table, 9 rows | every metric on the utilisation above_median slice of train |
| `metrics.train.sub.utilisation_high.auc_gap` | `41fca294` | scalar | -0.02732151154 | how far AUC on the utilisation above_median slice of train falls below AUC on all of train |
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
| `threshold.M1.condition_number` | `7e52fd7a` | scalar | 30 | M1: Belsley's condition number of the design |
| `threshold.M1.vif` | `aeb4f33c` | scalar | 10 | M1: the variance inflation factor of any retained feature |
| `threshold.O1.auc_gap` | `630f28f4` | scalar | 0.08 | O1: the train-to-test AUC gap |
| `threshold.O1.slice_auc_gap` | `0a827b87` | scalar | 0.08 | how far a sub-population's AUC may fall below the split's before the result is an open item; it raises no candidate |
| `threshold.O1.slice_min_share` | `9a6f1a87` | scalar | 0.1 | the share of a split a sub-population must hold before it can raise an open item |
| `threshold.S1.psi` | `278b9016` | scalar | 0.25 | S1: the population stability index, train against test |
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
| LLM calls | 18 (plan 4, draft 7, extract 7) |
| re-asks | 0 |
| repair rounds | 0 |
| tokens in / out | 207,429 / 74,618 |
| notional cost (USD) | 3.9739 |
| wall-clock (s) | 872.74 |
| subject run (s) | 1.40 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | credit_default-full_agent-20260909T002419Z-d03b07c6 |

## Appendix D — Not checked

| item | reason |
|---|---|
| `check_stability` (R1) | package declares no `regime.column` |
| `run_scenarios` (X1) | not applicable to `binary_classification` |
| out-of-time and vintage-holdout metrics (O1, second rule) | package declares neither split |
| developer documentation | package has no `docs/` directory |
