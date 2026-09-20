---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: full_agent
model: claude-opus-5[1m]
run_id: credit_default-full_agent-20260919T034749Z-e2e51e00
data_mode: synthetic
synthetic_n: 5000
grounding_precision_pre: 1.0000
grounding_precision_post: 1.0000
n_claims: 239
n_findings_by_severity: {high: 0, medium: 0, low: 1, info: 0}
generated: "2026-09-19T03:47:49Z"
illustrative: false
---

# Validation report — `credit_default` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `credit_default` v1.0 | `full_agent` | claude-opus-5[1m] | synthetic, n = 5000 | 1.0000 → 1.0000 | 0 / 0 / 1 / 0 |
<!-- quaestor:renderer:end -->

The subject of this validation is the credit_default model package, a binary classification model that predicts the probability that a borrower defaults on a credit obligation, and this report follows the structure of the Federal Reserve's model risk management guidance on model validation and monitoring [[reg:SR26-2:V]].
The subject was run end to end by the validation harness under the wall-clock cap the package declares for it, 300 seconds [[art:2ad8d1a5:runtime.max_seconds]], and every metric quoted here was recomputed from the subject's own scored output rather than carried over from the developer's own reporting.
The run covers a training split of 3500 rows [[art:2510d49d:profile.train.n]] and a held-out test split of 1500 rows [[art:2193cf5f:profile.test.n]].

Discrimination on test clears the declared floor, with an AUC of 0.748 [[art:5c6c2bfc:metrics.test.auc]] against a declared minimum of 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]].
Probabilistic accuracy on test clears its declared ceiling, with a Brier score of 0.1489 [[art:bbe69430:metrics.test.brier]] against a declared maximum of 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]].
Calibration on test falls inside its declared band, with a slope of the outcome regressed on the logit of the predicted probability of 1.003 [[art:b7dbb687:calibration_slope.test]], above the declared minimum of 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] and below the declared maximum of 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
Population stability between the two splits clears its declared ceiling, with a largest index across the features and the score of 0.01095 [[art:381b2570:psi.max]] against a declared maximum of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
Each developer-declared threshold named above is therefore met by the subject on the test split.

This validation raised F-001, an E1 effective challenge finding at low severity, arising from the comparison of the subject against its challenger.
The findings section below sets that finding out in full, together with its evidence and the action it calls for.

## 2. Conceptual soundness

Model design, key modeling choices, and developmental evidence are assessed here in the manner described for validating conceptual soundness [[reg:SR26-2:V.1.a]], with benchmarking to an alternative model treated as part of that assessment.

The champion is a logistic regression with a fitted intercept of -1.396 [[art:f181acb8:run.model_summary#intercept]], estimated on 3500 [[art:f181acb8:run.model_summary#n_train]] training rows, and scoring 0.748 [[art:5c6c2bfc:metrics.test.auc]] AUC and 0.1489 [[art:bbe69430:metrics.test.brier]] Brier on test.
The subject's feature inventory declares 12 [[art:2f9cb453:run.features#n]] features in total.
Of these, 2 [[art:2f9cb453:run.features#at_origination]] are known at origination and 10 [[art:2f9cb453:run.features#before_period_start]] are known before the performance period starts.
None are drawn from during the performance period, at 0 [[art:2f9cb453:run.features#during_period]], and none are drawn from after the outcome is observed, at 0 [[art:2f9cb453:run.features#after_outcome]], so on the timing evidence carried here the design does not take information that postdates the point of use.

The developer's own screen removed two features for collinearity against a variance inflation threshold of 10 [[art:f181acb8:run.model_summary#vif_threshold]].
The last billed amount was removed at a variance inflation factor of 160.9 [[art:f181acb8:run.model_summary#removed.f_bill_last.vif]], and the six-month mean utilisation was removed at 36.36 [[art:f181acb8:run.model_summary#removed.f_utilisation_mean_6m.vif]], both above that threshold and the former much the larger of the two.
Removing these leaves a retained set in which the surviving billing and utilisation terms carry the exposure information, which is the right instinct for a linear form, though it also means the retained terms absorb variation their dropped partners would otherwise have shared.

The largest coefficient by magnitude is on the most recent delinquency indicator, at 0.7334 [[art:f181acb8:run.model_summary#coefficients.f_delinq_last.value]], and it is positive, which is what credit subject matter expects: recent delinquency should raise default risk.
The next largest are the six-month mean bill, at -0.3726 [[art:f181acb8:run.model_summary#coefficients.f_bill_mean_6m.value]], and the six-month mean payment ratio, at -0.3554 [[art:f181acb8:run.model_summary#coefficients.f_pay_ratio_mean_6m.value]], the latter negative in the expected direction since paying down a larger share of the balance should lower risk.
Utilisation enters positively at 0.2662 [[art:f181acb8:run.model_summary#coefficients.f_utilisation.value]], again as expected, and the six-month bill trend enters negatively at -0.2225 [[art:f181acb8:run.model_summary#coefficients.f_bill_trend_6m.value]].
The smaller terms are the delinquency count at 0.1226 [[art:f181acb8:run.model_summary#coefficients.f_delinq_count_6m.value]], the last payment ratio at 0.1026 [[art:f181acb8:run.model_summary#coefficients.f_pay_ratio_last.value]], the credit limit at 0.07266 [[art:f181acb8:run.model_summary#coefficients.f_limit_bal.value]], age at -0.06726 [[art:f181acb8:run.model_summary#coefficients.f_age.value]], and the six-month maximum delinquency at -0.03221 [[art:f181acb8:run.model_summary#coefficients.f_delinq_max_6m.value]].

Fitted signs were compared against each feature's own univariate direction on train, and the count of retained features where the two contradict each other is 3 [[art:e223cd4a:sign_check.n_disagreements]].
On the six-month maximum delinquency the fitted sign is -1 [[art:b2de2a5f:sign_check.f_delinq_max_6m.coef_sign]] while its univariate direction is 1 [[art:5a76c041:sign_check.f_delinq_max_6m.univariate_direction]], recorded as a disagreement at 0 [[art:b5785264:sign_check.f_delinq_max_6m.agrees]]; refitting without it changes test AUC by 0.0003598 [[art:aace9667:ablation.f_delinq_max_6m.delta_auc]] against a baseline of 0.748 [[art:3a44e438:ablation.baseline_auc]], a positive change, so the model was not drawing discrimination from it and the flipped sign is a statement about a term the fit barely uses.
On the credit limit the fitted sign is 1 [[art:76765f24:sign_check.f_limit_bal.coef_sign]] while its univariate direction is -1 [[art:8cc36ad2:sign_check.f_limit_bal.univariate_direction]], recorded as a disagreement at 0 [[art:dc9d1c95:sign_check.f_limit_bal.agrees]]; its ablation change is 0.0004286 [[art:1549706f:ablation.f_limit_bal.delta_auc]], likewise positive and of similar smallness, so the same reading applies.
On the last payment ratio the fitted sign is 1 [[art:8b49eed8:sign_check.f_pay_ratio_last.coef_sign]] while its univariate direction is -1 [[art:c9abae5e:sign_check.f_pay_ratio_last.univariate_direction]], recorded as a disagreement at 0 [[art:847710b6:sign_check.f_pay_ratio_last.agrees]]; its ablation change is 0.002411 [[art:9f0e8a67:ablation.f_pay_ratio_last.delta_auc]], the largest of the three positive changes among the disagreeing features, and still a change in the direction that says dropping the term did not cost discrimination.
In all three cases the fitted coefficient carries a sign a credit reviewer would not predict from the feature alone, and in all three the ablation evidence says the model leans on the term lightly, which points at the correlation structure among the retained terms rather than at a mispriced driver.
The remaining retained features agree with their univariate directions, including the most recent delinquency indicator at 1 [[art:547a15bd:sign_check.f_delinq_last.agrees]], utilisation at 1 [[art:b45fb558:sign_check.f_utilisation.agrees]], the six-month mean payment ratio at 1 [[art:e5f0e61f:sign_check.f_pay_ratio_mean_6m.agrees]], the six-month mean bill at 1 [[art:7144f385:sign_check.f_bill_mean_6m.agrees]], the six-month bill trend at 1 [[art:5a646254:sign_check.f_bill_trend_6m.agrees]], the delinquency count at 1 [[art:e78b83df:sign_check.f_delinq_count_6m.agrees]], and age at 1 [[art:ef6b0a61:sign_check.f_age.agrees]].

The ablation evidence also shows where the champion's discrimination actually sits, measured from a refit baseline of 0.748 [[art:3a44e438:ablation.baseline_auc]].
Dropping the most recent delinquency indicator changes test AUC by -0.07585 [[art:746389ef:ablation.f_delinq_last.delta_auc]], by far the largest negative change and consistent with its being the largest coefficient.
Dropping utilisation changes test AUC by -0.01977 [[art:3e7f047d:ablation.f_utilisation.delta_auc]], and dropping the six-month mean bill changes it by -0.0016 [[art:8a56b9fe:ablation.f_bill_mean_6m.delta_auc]], so these three are the terms carrying discrimination.
The rest change test AUC upward when removed: the six-month mean payment ratio by 0.006603 [[art:562f5fd1:ablation.f_pay_ratio_mean_6m.delta_auc]], the six-month bill trend by 0.003279 [[art:b8b0b1b2:ablation.f_bill_trend_6m.delta_auc]], the delinquency count by 0.0006812 [[art:6e7487cc:ablation.f_delinq_count_6m.delta_auc]], and age by 8.675e-05 [[art:d9569286:ablation.f_age.delta_auc]].
A linear form whose out-of-sample discrimination improves on the removal of most of its terms is one that is carried by a small number of drivers, which bears directly on how much weight the coefficient story can hold.

Effective challenge was exercised by fitting a histogram gradient boosting challenger on the same data.
The challenger reaches 0.824 [[art:bf5be719:challenger.auc]] AUC on test against the champion's 0.748 [[art:5c6c2bfc:metrics.test.auc]], a lead of 0.07598 [[art:c9e502ae:challenger.delta_auc]].
The threshold that decides whether such a difference matters is a challenger AUC lead of 0.03 [[art:e042774c:threshold.E1.delta_auc]], and the observed lead is above it.
The challenger's Brier score of 0.1258 [[art:f9e0583d:challenger.brier]] is below the champion's 0.1489 [[art:bbe69430:metrics.test.brier]], so the challenger is ahead on ranking and on calibration-inclusive accuracy alike, and the comparison being drawn in both cases is the difference between the two models' scores on the same test split.
Because the challenger differs from the champion principally in functional form, this result is evidence about the champion's functional form and not about its feature set, and it is raised as a candidate finding on effective challenge, reported in the findings section.

On the whole the design is defensible in its inputs: the timing evidence shows no feature drawn from during or after the outcome window, the collinearity screen removed the two most inflated terms against a declared threshold, and the coefficients on the terms the model actually leans on carry the signs credit subject matter expects.
The weaknesses are in the functional form rather than the inputs, and they are visible in two places, the sign disagreements on lightly-used terms and the margin a non-linear challenger opens on the same data.

## 3. Data integrity and drift

Model testing is a core component of development that includes a critical assessment of data quality, relevance, and inputs, and this section reviews the data behind the credit_default package version 1.0 on that basis [[reg:SR26-2:IV.1]].

### Missingness within and between splits

The training split holds 3500 [[art:2510d49d:profile.train.n]] rows and the test split holds 1500 [[art:2193cf5f:profile.test.n]] rows.
The largest missing fraction over any column of the training split is 0 [[art:050a3099:profile.train.missing.max]].
The largest missing fraction over any column of the test split is 0 [[art:f813848d:profile.test.missing.max]].
The comparison the rule draws between the two splits is a difference rather than a ratio, and because the two maxima stand at the same value that difference cannot reach the bound of 0.1 [[art:9cce25ea:threshold.D1.missing_gap]].
Neither split therefore carries a missingness pattern that the other does not.

### Population and characteristic stability

Population stability between the training split and the test split, feature by feature, is as follows.

- f_age: 0.008124 [[art:5017e61e:psi.f_age]]
- f_bill_mean_6m: 0.007124 [[art:c519fca2:psi.f_bill_mean_6m]]
- f_bill_trend_6m: 0.00958 [[art:c3f51172:psi.f_bill_trend_6m]]
- f_delinq_count_6m: 0.002069 [[art:6a2fba4e:psi.f_delinq_count_6m]]
- f_delinq_last: 0.00285 [[art:9d44627e:psi.f_delinq_last]]
- f_delinq_max_6m: 0.005498 [[art:05bccd03:psi.f_delinq_max_6m]]
- f_limit_bal: 0.01095 [[art:1932cef9:psi.f_limit_bal]]
- f_pay_ratio_last: 0.004966 [[art:f85ffaec:psi.f_pay_ratio_last]]
- f_pay_ratio_mean_6m: 0.0055 [[art:4d206390:psi.f_pay_ratio_mean_6m]]
- f_utilisation: 0.004244 [[art:b8b6b215:psi.f_utilisation]]

The score itself shifts between the two splits by 0.007023 [[art:a2885abf:psi.y_score]], which is smaller than the shift seen in the most displaced input.
The largest population stability index across the features and the score together is 0.01095 [[art:381b2570:psi.max]], carried by the credit limit feature, and it sits below the declared bound of 0.25 [[art:278b9016:threshold.S1.psi]].
The package file declares the same bound at 0.25 [[art:fbb5a9d1:threshold.package.psi.max]], so the validation rule and the package agree on what the population shift was allowed to be.

Characteristic stability, measured as each feature's contribution to the shift in the linear predictor, is as follows.

- f_age: 0.0009476 [[art:7eca72ca:csi.f_age]]
- f_bill_mean_6m: 0.002369 [[art:a56ef25e:csi.f_bill_mean_6m]]
- f_bill_trend_6m: 0.00633 [[art:e6bbd7a6:csi.f_bill_trend_6m]]
- f_delinq_count_6m: 0.002449 [[art:5c1ddd21:csi.f_delinq_count_6m]]
- f_delinq_last: 0.02363 [[art:dadfe01c:csi.f_delinq_last]]
- f_delinq_max_6m: 0.0008965 [[art:20767939:csi.f_delinq_max_6m]]
- f_limit_bal: 0.001211 [[art:810ae3c7:csi.f_limit_bal]]
- f_pay_ratio_last: 0.001924 [[art:f337e4e5:csi.f_pay_ratio_last]]
- f_pay_ratio_mean_6m: 0.001768 [[art:ff31f4b4:csi.f_pay_ratio_mean_6m]]
- f_utilisation: 0.004042 [[art:b9d55682:csi.f_utilisation]]

The largest characteristic contribution is 0.02363 [[art:e56cb179:csi.max]], and it comes from the most recent delinquency feature at 0.02363 [[art:dadfe01c:csi.f_delinq_last]].
That largest contribution is above the largest population index of 0.01095 [[art:381b2570:psi.max]], so the feature that moves the predictor most is not the feature whose marginal distribution moves most, and both remain below the declared bound of 0.25 [[art:278b9016:threshold.S1.psi]].
The ordering is worth noting for monitoring: a feature can shift little in its own distribution and still carry the larger share of the movement in the score.

### Leakage screens

The declared-timing screen counts features declared as observed during the performance period or after the outcome, and that count is 0 [[art:742bcd24:leakage.timing.n_flagged]].
The strongest single feature reaches an area under the curve of 0.6831 [[art:fd829fc4:leakage.target_corr.max_single_feature_auc]], below the bound of 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]] that any one feature is allowed to reach on its own.
That margin is wide, and no individual input behaves like a restatement of the target.

The contamination screen runs two arms, and each is read against its own bound.
The first arm measures the share of test rows whose identifier also identifies a row of train, and that share is 0 [[art:63d37fc5:leakage.overlap.ids]], below the declared bound of 0.005 [[art:9f336eaf:threshold.L2.overlap]].
The second arm measures the share of test rows whose feature values also appear in train, and that share is 0 [[art:0fec8048:leakage.overlap.features]].
The second arm is read against the bound that rule actually applied, 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]], which is the larger of the declared overlap bound and a multiple of the share of train rows whose feature values are not unique within train.
That construction exists because two different subjects writing the same discrete row is coincidence rather than contamination, so the bound relaxes when the training data itself repeats feature vectors.
Here the share of train rows whose feature values are not unique within train is 0 [[art:4474c227:leakage.duplicates.train]], so the applied bound of 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]] is the declared bound of 0.005 [[art:9f336eaf:threshold.L2.overlap]] rather than a relaxed one, and the feature-vector arm was judged on the stricter of the two readings available to it.
The overlap screen over test rows records 0 [[art:4c9fcd09:leakage.overlap]], consistent with the feature-vector arm.

The name screen matches feature names against a target-adjacent lexicon and returns 0 [[art:407e62be:leakage.name_screen.n_matched]] matches, so no feature is named in a way that suggests it encodes the outcome.

### Assessment

Every data check reviewed in this section returns a value inside the bound it was read against, and the two contamination arms were each read against the bound that belongs to them.
The residual concern is not a breach but a ceiling: the stability evidence here covers the training split against the test split only, and the shift observed there is small enough that it says little about how the population will move once the model is in use.
Ongoing monitoring should therefore continue to track the population and characteristic indices against the same declared bound of 0.25 [[art:278b9016:threshold.S1.psi]], with attention to the most recent delinquency feature, which carries the largest share of the movement in the linear predictor.

## 4. Outcomes analysis

Outcomes analysis compares model output with the corresponding realised outcomes, and this section reads the recomputed performance of the package against the objectives and thresholds set for it [[reg:SR26-2:V.1.b]].

Discrimination is reported first and calibration second, because the observed event rate on the evaluation split is 0.2247 [[art:9209d200:metrics.test.event_rate]], at or above 0.05 [[art:42f1351e:rule.calibration_first_event_rate]], the rate below which this report would lead with calibration instead.

The metrics recomputed on each split are as follows.

| Metric | Train | Test |
| --- | --- | --- |
| Rows | 3500 [[art:564683ee:metrics.train.n]] | 1500 [[art:64fcf14d:metrics.test.n]] |
| Event rate | 0.2246 [[art:133a5ff8:metrics.train.event_rate]] | 0.2247 [[art:9209d200:metrics.test.event_rate]] |
| AUC | 0.7584 [[art:14b38a2b:metrics.train.auc]] | 0.748 [[art:5c6c2bfc:metrics.test.auc]] |
| Gini | 0.5169 [[art:b4da846e:metrics.train.gini]] | 0.496 [[art:8e5918d8:metrics.test.gini]] |
| KS | 0.4451 [[art:ccc12729:metrics.train.ks]] | 0.4183 [[art:90751047:metrics.test.ks]] |
| Brier | 0.1489 [[art:be669a99:metrics.train.brier]] | 0.1489 [[art:bbe69430:metrics.test.brier]] |
| Log loss | 0.465 [[art:4f02e465:metrics.train.logloss]] | 0.4673 [[art:dda8da69:metrics.test.logloss]] |
| Mean predicted | 0.2246 [[art:605cce58:metrics.train.mean_predicted]] | 0.2211 [[art:4d2f8a37:metrics.test.mean_predicted]] |

Rank-ordering concentrates events in the upper deciles of predicted probability, where decile 1 holds the highest probabilities.

<!-- quaestor:renderer:begin table deciles.test -->
Decile separation on test; decile 1 holds the highest probabilities [[art:15d50c28:deciles.test]]:

| decile | count | events | event_rate | lift |
|---|---|---|---|---|
| 1 | 150 | 87 | 0.58 | 2.582 |
| 2 | 150 | 72 | 0.48 | 2.136 |
| 3 | 150 | 47 | 0.3133 | 1.395 |
| 4 | 150 | 35 | 0.2333 | 1.039 |
| 5 | 150 | 24 | 0.16 | 0.7122 |
| 6 | 150 | 15 | 0.1 | 0.4451 |
| 7 | 150 | 16 | 0.1067 | 0.4748 |
| 8 | 150 | 11 | 0.07333 | 0.3264 |
| 9 | 150 | 11 | 0.07333 | 0.3264 |
| 10 | 150 | 19 | 0.1267 | 0.5638 |
<!-- quaestor:renderer:end -->

The top two deciles hold 0.4718 [[art:d4a1cf7d:deciles.test.top2_capture]] of test events, and on train the same two deciles hold 0.4517 [[art:1d20c762:deciles.train.top2_capture]] of events.

On the train-to-test movement in discrimination, AUC is 0.7584 [[art:14b38a2b:metrics.train.auc]] on train against 0.748 [[art:5c6c2bfc:metrics.test.auc]] on test, the test value being the lower of the two.

The bound declared for the train-to-test AUC gap is 0.08 [[art:630f28f4:threshold.O1.auc_gap]], and the test value sits below the train value by less than that bound.

Turning to calibration, the logistic regression of the outcome on the logit of the predicted probability gives a slope of 1.003 [[art:b7dbb687:calibration_slope.test]] on test, inside the band running from 0.8 [[art:749634ae:threshold.C1.calibration_slope.min]] to 1.2 [[art:b6672579:threshold.C1.calibration_slope.max]].

The intercept of that same regression on test is 0.02729 [[art:b69c6b52:calibration_intercept.test]].

The corresponding train values are a slope of 1.002 [[art:d02e3091:calibration_slope.train]] and an intercept of 0.002062 [[art:ed381a81:calibration_intercept.train]], both consistent with the test picture in direction.

Mean predicted probability on test is 0.2211 [[art:4d2f8a37:metrics.test.mean_predicted]] against an observed rate of 0.2247 [[art:9209d200:metrics.test.event_rate]], the predicted level sitting below the observed one.

Expressed relatively, that separation is 0.01585 [[art:d8ffb3d0:calibration.mean_rel_gap.test]], inside the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]] on mean predicted against observed.

On train the same relative quantity is 0.0002283 [[art:53738d45:calibration.mean_rel_gap.train]], and comparing the two relative gaps as an ordering, the test one is the larger of the two; both sit inside that tolerance.

<!-- quaestor:renderer:begin table calibration.test -->
Calibration by decile of predicted probability on test [[art:508ffcf8:calibration.test]]:

| bin | mean_predicted | observed | count |
|---|---|---|---|
| 1 | 0.08255 | 0.1267 | 150 |
| 2 | 0.1076 | 0.07333 | 150 |
| 3 | 0.1227 | 0.07333 | 150 |
| 4 | 0.1364 | 0.1067 | 150 |
| 5 | 0.1543 | 0.1 | 150 |
| 6 | 0.1732 | 0.16 | 150 |
| 7 | 0.1972 | 0.2333 | 150 |
| 8 | 0.248 | 0.3133 | 150 |
| 9 | 0.3812 | 0.48 | 150 |
| 10 | 0.608 | 0.58 | 150 |
<!-- quaestor:renderer:end -->

The bounds the developer declared in package.yaml, each paired with the value recomputed on this run, are set out below.

<!-- quaestor:renderer:begin table thresholds.evaluation -->
Every threshold package.yaml declares, with its bound, the recomputed value and the outcome [[art:bc507a88:thresholds.evaluation]]:

| metric | split | bound | value | result |
|---|---|---|---|---|
| auc | test | minimum 0.7 | 0.748 | pass |
| brier | test | maximum 0.2 | 0.1489 | pass |
| calibration_slope | test | minimum 0.8 | 1.003 | pass |
| calibration_slope | test | maximum 1.2 | 1.003 | pass |
| psi |  | maximum 0.25 | 0.01095 | pass |
<!-- quaestor:renderer:end -->

The table states, for every bound package.yaml declares, the metric and split it applies to, the bound itself, the value recomputed here and the outcome of the comparison. Because the tool assembled it from the same recomputed quantities cited above, the outcomes recorded there govern the reading of the prose in this section.

### Follow-up analyses

The bounded planning loop ran three further recomputations of the metric set on sub-populations of each split, and all three are reported here.

The first recomputed every metric on the sub-population `f_utilisation > median(f_utilisation)`.

It was asked in order to localise the challenger model's AUC lead, by testing whether the champion's discrimination degrades on the high-utilisation half, where an unmodelled nonlinearity would show itself.

<!-- quaestor:renderer:begin table metrics.train.sub.f_utilisation_high -->
Every metric on the f_utilisation above_median slice of train [[art:a1a2ba5f:metrics.train.sub.f_utilisation_high]]:

| metric | value |
|---|---|
| n | 1750 |
| event_rate | 0.2246 |
| auc | 0.5732 |
| gini | 0.1463 |
| ks | 0.178 |
| brier | 0.1957 |
| logloss | 0.5836 |
| mean_predicted | 0.2329 |
| mean_rel_gap | 0.03719 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.f_utilisation_high -->
Every metric on the f_utilisation above_median slice of test [[art:93ddb9c9:metrics.test.sub.f_utilisation_high]]:

| metric | value |
|---|---|
| n | 750 |
| event_rate | 0.2333 |
| auc | 0.5689 |
| gini | 0.1378 |
| ks | 0.156 |
| brier | 0.1945 |
| logloss | 0.5856 |
| mean_predicted | 0.2286 |
| mean_rel_gap | 0.02024 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

On test, AUC on this sub-population falls 0.1791 [[art:f0689663:metrics.test.sub.f_utilisation_high.auc_gap]] below AUC on all of test, above the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] on how far a sub-population's AUC may fall below its split's.

On train the same shortfall is 0.1853 [[art:43f1ad7f:metrics.train.sub.f_utilisation_high.auc_gap]], likewise above that bound.

The sub-population holds 0.5 [[art:8e769cfa:metrics.test.sub.f_utilisation_high.share]] of test and 0.5 [[art:d3d28c9a:metrics.train.sub.f_utilisation_high.share]] of train, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] a sub-population must hold to be read as a segment and below the share of 0.95 [[art:a928a05c:threshold.O1.slice_max_share]] at which it would be refused as standing for the whole split.

Mean predicted on this sub-population of test is 0.2286 [[art:c37ecc36:metrics.test.sub.f_utilisation_high.mean_predicted]] against an observed rate of 0.2333 [[art:5b836e8e:metrics.test.sub.f_utilisation_high.event_rate]], a relative separation of 0.02024 [[art:42b00194:metrics.test.sub.f_utilisation_high.mean_rel_gap]], inside the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].

On train, mean predicted of 0.2329 [[art:315b25f7:metrics.train.sub.f_utilisation_high.mean_predicted]] against an observed rate of 0.2246 [[art:b34c6bc2:metrics.train.sub.f_utilisation_high.event_rate]] gives a relative separation of 0.03719 [[art:82b6fda5:metrics.train.sub.f_utilisation_high.mean_rel_gap]], also inside that tolerance.

The level of the probabilities on this sub-population therefore tracks its observed rate while the ordering does not, so the weakness here is in the ranking of the probabilities rather than in their level.

The second recomputed every metric on the complementary sub-population `f_utilisation <= median(f_utilisation)`.

It was asked to complete the utilisation partition, so that the high-utilisation result could be read against the other half and show whether the champion's discrimination shortfall is concentrated in one segment.

<!-- quaestor:renderer:begin table metrics.train.sub.f_utilisation_low -->
Every metric on the f_utilisation below_median slice of train [[art:061af581:metrics.train.sub.f_utilisation_low]]:

| metric | value |
|---|---|
| n | 1750 |
| event_rate | 0.2246 |
| auc | 0.9142 |
| gini | 0.8284 |
| ks | 0.7562 |
| brier | 0.1021 |
| logloss | 0.3464 |
| mean_predicted | 0.2163 |
| mean_rel_gap | 0.03674 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.f_utilisation_low -->
Every metric on the f_utilisation below_median slice of test [[art:8373aea6:metrics.test.sub.f_utilisation_low]]:

| metric | value |
|---|---|
| n | 750 |
| event_rate | 0.216 |
| auc | 0.8986 |
| gini | 0.7972 |
| ks | 0.7659 |
| brier | 0.1032 |
| logloss | 0.349 |
| mean_predicted | 0.2136 |
| mean_rel_gap | 0.01111 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

On test, the distance of this sub-population's AUC below AUC on all of test is -0.1506 [[art:03dfbb51:metrics.test.sub.f_utilisation_low.auc_gap]], a negative shortfall, meaning the half separates better than the split as a whole and stays inside the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].

On train the corresponding quantity is -0.1558 [[art:0e0b12c1:metrics.train.sub.f_utilisation_low.auc_gap]], likewise inside that bound and likewise in the favourable direction.

The sub-population holds 0.5 [[art:03601889:metrics.test.sub.f_utilisation_low.share]] of test and 0.5 [[art:6314e9e5:metrics.train.sub.f_utilisation_low.share]] of train, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].

Mean predicted on this sub-population of test is 0.2136 [[art:2a5870fc:metrics.test.sub.f_utilisation_low.mean_predicted]] against an observed rate of 0.216 [[art:7a44f440:metrics.test.sub.f_utilisation_low.event_rate]], a relative separation of 0.01111 [[art:6a2eb11d:metrics.test.sub.f_utilisation_low.mean_rel_gap]], inside the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].

On train, mean predicted of 0.2163 [[art:cfd48cc6:metrics.train.sub.f_utilisation_low.mean_predicted]] against an observed rate of 0.2246 [[art:ecfe7914:metrics.train.sub.f_utilisation_low.event_rate]] gives a relative separation of 0.03674 [[art:e1454a17:metrics.train.sub.f_utilisation_low.mean_rel_gap]], also inside that tolerance.

Here neither the level nor the ordering reads as weak: the level tracks the observed rate and the ordering is better than the split's own.

Comparing the two halves on the absolute distance of each one's AUC from its split's, and not on their ratio, the high-utilisation half sits below the split while the low-utilisation half sits above it, so across this partition the discrimination shortfall is concentrated in the high-utilisation half rather than spread evenly.

The third recomputed every metric on the sub-population `f_delinq_count_6m > median(f_delinq_count_6m)`.

It was asked because the challenger's AUC lead was not explained by the utilisation halves already tested, and localising champion separation on the recently delinquent segment shows whether the deficiency sits in the high-risk sub-population.

<!-- quaestor:renderer:begin table metrics.train.sub.f_delinq_count_6m_high -->
Every metric on the f_delinq_count_6m above_median slice of train [[art:001f70e9:metrics.train.sub.f_delinq_count_6m_high]]:

| metric | value |
|---|---|
| n | 1322 |
| event_rate | 0.3162 |
| auc | 0.7469 |
| gini | 0.4938 |
| ks | 0.4063 |
| brier | 0.1853 |
| logloss | 0.5486 |
| mean_predicted | 0.3177 |
| mean_rel_gap | 0.004935 |
| share | 0.3777 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.f_delinq_count_6m_high -->
Every metric on the f_delinq_count_6m above_median slice of test [[art:d4fbdc76:metrics.test.sub.f_delinq_count_6m_high]]:

| metric | value |
|---|---|
| n | 550 |
| event_rate | 0.3455 |
| auc | 0.75 |
| gini | 0.4999 |
| ks | 0.4298 |
| brier | 0.1932 |
| logloss | 0.5683 |
| mean_predicted | 0.3198 |
| mean_rel_gap | 0.07415 |
| share | 0.3667 |
<!-- quaestor:renderer:end -->

On test, the distance of this sub-population's AUC below AUC on all of test is -0.001967 [[art:5b735235:metrics.test.sub.f_delinq_count_6m_high.auc_gap]], inside the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] and in the favourable direction.

On train the corresponding shortfall is 0.01154 [[art:066e4d48:metrics.train.sub.f_delinq_count_6m_high.auc_gap]], also inside that bound.

The sub-population holds 0.3667 [[art:8ea39bd5:metrics.test.sub.f_delinq_count_6m_high.share]] of test and 0.3777 [[art:49900347:metrics.train.sub.f_delinq_count_6m_high.share]] of train, above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].

Mean predicted on this sub-population of test is 0.3198 [[art:4aa724a5:metrics.test.sub.f_delinq_count_6m_high.mean_predicted]] against an observed rate of 0.3455 [[art:d9d79704:metrics.test.sub.f_delinq_count_6m_high.event_rate]], the predicted level sitting below the observed one, a relative separation of 0.07415 [[art:88c4873c:metrics.test.sub.f_delinq_count_6m_high.mean_rel_gap]] that remains inside the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].

On train, mean predicted of 0.3177 [[art:ec725b41:metrics.train.sub.f_delinq_count_6m_high.mean_predicted]] against an observed rate of 0.3162 [[art:70daaf30:metrics.train.sub.f_delinq_count_6m_high.event_rate]] gives a relative separation of 0.004935 [[art:41f6e723:metrics.train.sub.f_delinq_count_6m_high.mean_rel_gap]], also inside that tolerance.

On this sub-population the ordering of the probabilities is in line with the split's own, while it is the level that moves away from the observed rate on test, so what weakness there is here lies in the level rather than in the ranking.

Across the three steps, the champion's separation deficiency localises to the high-utilisation half and not to the recently delinquent segment.

## 5. Sensitivity and scenario analysis

Sensitivity analysis, together with the robustness and stability checks that probe how a model behaves across a wide range of inputs including extreme values, is the element of validation this section addresses [[reg:SR11-7:V.1.a]].

### Multicollinearity among the retained features

The largest variance inflation factor across the retained features is 7.295 [[art:9ae7c45b:vif.max]], which sits below the declared threshold of 10 [[art:aeb4f33c:threshold.M1.vif]].
Belsley's condition number of the column-standardised design is 5.547 [[art:e41b9562:condition_number]], below the declared threshold of 30 [[art:7e52fd7a:threshold.M1.condition_number]].
Neither diagnostic breaches its declared threshold, so the design does not exhibit collinearity of the degree that would make the fitted coefficients unstable under the criteria this package declares.

The feature carrying the largest inflation is f_bill_mean_6m at 7.295 [[art:7b32e2ef:vif.f_bill_mean_6m]], followed closely by f_pay_ratio_last at 7.264 [[art:5f2b9e12:vif.f_pay_ratio_last]] and then f_pay_ratio_mean_6m at 7.259 [[art:bf28797b:vif.f_pay_ratio_mean_6m]].
The billing and payment-ratio aggregates cluster together at the upper end of the observed range, which is consistent with their being drawn from a common six-month window over the same underlying statements.
The remaining retained features fall further below the threshold: f_limit_bal at 4.803 [[art:99b238f2:vif.f_limit_bal]], f_utilisation at 3.215 [[art:da156a12:vif.f_utilisation]], f_delinq_count_6m at 2.561 [[art:15bac45f:vif.f_delinq_count_6m]], f_delinq_max_6m at 2.408 [[art:e4b87600:vif.f_delinq_max_6m]], f_delinq_last at 1.412 [[art:be34e000:vif.f_delinq_last]], f_bill_trend_6m at 1.201 [[art:c2d88735:vif.f_bill_trend_6m]] and f_age at 1.002 [[art:561dd3fe:vif.f_age]].
The inflation on f_age is close to the value a fully orthogonal column would take, indicating that it carries information largely independent of the billing, payment and delinquency aggregates.
Because the highest inflation in the set remains on the passing side of the threshold, the coefficient-level interpretation of the billing and payment-ratio terms can be read with the usual caution about correlated aggregates rather than being set aside.

### Items that do not apply to this model type

The package under review does not declare a regime column, so stability across declared regimes is not part of the sensitivity work carried out for this model; it is listed in Appendix D and is not to be read as having been exercised.
The subject of this report is a credit default classification model rather than a hazard model, so the rate-shock scenarios do not apply to it.
That exclusion covers the value change at the extreme upward and downward shocks, whether the shocked curve is monotone, and the convexity of that curve against the direction the package declares.
Those scenario items are likewise listed in Appendix D as out of scope for this model type, and nothing above should be read as reporting a shocked value, a monotonicity verdict or a convexity direction for this model.

### Disposition

Within the sensitivity work that does apply to this model type, no condition arising in this section was raised as a finding.
The guidance treats sensitivity and robustness checks as activities to be repeated periodically as part of ongoing monitoring rather than settled once at development, so the collinearity diagnostics reported here are expected to be re-run on the schedule set for this model and re-read against the same declared thresholds [[reg:SR11-7:V.1.b]].

## 6. Findings and recommendations

Findings below are ordered by severity, most severe first, and each carries the recomputed quantities and the declared bounds it was read against, so that the source and extent of the model risk it describes can be traced [[reg:SR26-2:V]].

### F-001 · E1 effective challenge · severity **low**

**An alternative specification out-performs the champion on held-out discrimination by a margin wider than the declared effective-challenge bound, so the retained model is not the strongest candidate on the evidence reviewed.**

A gradient-boosted challenger reaches an AUC of 0.824 [[art:bf5be719:challenger.auc]] on the test split, against the champion's 0.748 [[art:5c6c2bfc:metrics.test.auc]] on the same split.

The challenger's lead over the champion is 0.07598 [[art:c9e502ae:challenger.delta_auc]], above the declared effective-challenge bound of 0.03 [[art:e042774c:threshold.E1.delta_auc]].

The validator concludes that the choice of the champion's functional form is not supported by discrimination on the test split alone, and that the margin is wide enough relative to the declared bound that the decision to retain the champion rests on grounds the package has not set out.

The model developer should either record the reasons the champion is retained in spite of the challenger's lead — interpretability, stability under monitoring, implementation constraints or the cost of the richer form — or carry the challenger forward as a candidate replacement and submit it for validation, and in either case document the decision so that the response can be tracked [[reg:SR26-2:VI.3]].

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1, S1), `compute_metrics` (T1, C1, O1), `check_leakage` (L1, L2), `check_collinearity` (M1).

### Open items

Model developer: within the sub-population `f_utilisation > median(f_utilisation)` of the test split, where AUC is 0.5689 [[art:8b9b9b27:metrics.test.sub.f_utilisation_high.auc]] against 0.748 [[art:5c6c2bfc:metrics.test.auc]] for the whole split — a shortfall, taken as a difference, of 0.1791 [[art:f0689663:metrics.test.sub.f_utilisation_high.auc_gap]] read against the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]], on a sub-population holding 0.5 [[art:8e769cfa:metrics.test.sub.f_utilisation_high.share]] of the split and so at or above the share bound of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] — what does the model still discriminate on once utilisation is held near-constant by the selection itself, and which other risk drivers are expected to carry the ranking there?

Model developer: within the same sub-population `f_utilisation > median(f_utilisation)` of the train split, where AUC is 0.5732 [[art:22699b62:metrics.train.sub.f_utilisation_high.auc]] against 0.7584 [[art:14b38a2b:metrics.train.auc]] for the whole split — a shortfall, taken as a difference, of 0.1853 [[art:43f1ad7f:metrics.train.sub.f_utilisation_high.auc_gap]] read against the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]], on a sub-population holding 0.5 [[art:d3d28c9a:metrics.train.sub.f_utilisation_high.share]] of the split and so at or above the share bound of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] — was this in-sample behaviour anticipated at development, and what ranking signal was the specification expected to retain there?

Model developer: on what grounds does the fitted coefficient on `f_delinq_max_6m` take sign -1 [[art:b2de2a5f:sign_check.f_delinq_max_6m.coef_sign]] where that feature's own single-feature direction on train is 1 [[art:5a76c041:sign_check.f_delinq_max_6m.univariate_direction]], the agreement check against that univariate direction returning 0 [[art:b5785264:sign_check.f_delinq_max_6m.agrees]], and which correlated features is the fitted term adjusting for once the rest of the specification is held fixed?

Model developer: on what grounds does the fitted coefficient on `f_limit_bal` take sign 1 [[art:76765f24:sign_check.f_limit_bal.coef_sign]] where that feature's own single-feature direction on train is -1 [[art:8cc36ad2:sign_check.f_limit_bal.univariate_direction]], the agreement check against that univariate direction returning 0 [[art:dc9d1c95:sign_check.f_limit_bal.agrees]], and is the reversal the intended conditional effect given the other features in the specification?

Model developer: on what grounds does the fitted coefficient on `f_pay_ratio_last` take sign 1 [[art:8b49eed8:sign_check.f_pay_ratio_last.coef_sign]] where that feature's own single-feature direction on train is -1 [[art:c9abae5e:sign_check.f_pay_ratio_last.univariate_direction]], the agreement check against that univariate direction returning 0 [[art:847710b6:sign_check.f_pay_ratio_last.agrees]], and what business reading of the conditional relationship supports the fitted direction?

## 7. Ongoing monitoring recommendations

Ongoing monitoring evaluates the extent to which this model continues to perform as expected given potential changes in products, exposures, activities, clients, data relevance, or market conditions, and it is the control that carries this validation's conclusions forward once the package is in use [[reg:SR26-2:V.2]].

The plan below re-runs on production cohorts the same quantities this validation recomputed, judged against the same declared bounds the checks used, so that drift is measured against a fixed reference rather than a renegotiated one.

### Quantities, frequency, and bounds

- Rank-ordering should be recomputed on each completed performance window, quarterly once outcomes mature, and compared with the declared floor of 0.7 [[art:8bfd02cc:threshold.package.auc.test.min]]; on the evaluation split this validation observed 0.748 [[art:5c6c2bfc:metrics.test.auc]], which sits above that floor, and the margin between the two is narrow enough that a single deteriorating vintage could carry the production value under it.
- Probabilistic accuracy should be tracked on the same quarterly cadence against the declared ceiling of 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]]; the observed value on the evaluation split was 0.1489 [[art:bbe69430:metrics.test.brier]], below that ceiling.
- The calibration slope should be refitted quarterly on realized outcomes and held inside the declared band running from 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] to 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]]; the observed value on the evaluation split was 1.003 [[art:b7dbb687:calibration_slope.test]], inside that band and close to its centre, so movement in either direction is a meaningful early signal.
- Population stability of the scoring inputs and of the score itself should be computed monthly against the development reference distribution and compared with the declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]]; the largest value this validation observed between the development splits was 0.01095 [[art:381b2570:psi.max]], far below that ceiling, but a comparison between two splits of one development sample is a weaker test than a comparison of a live vintage against that reference, and only the monthly production computation exercises the ceiling as intended.

Stability and sensitivity checks deserve the same periodic repetition they received at development, because a model that works well only over certain ranges of input values or market conditions needs monitoring that identifies when those ranges are approached [[reg:SR11-7:V.1.b]].

### Report ordering

The earlier performance section of this report presented discrimination before calibration, because the observed event rate on the evaluation split was at or above 0.05 [[art:42f1351e:rule.calibration_first_event_rate]].

If a future monitored cohort has an event rate that falls below 0.05 [[art:42f1351e:rule.calibration_first_event_rate]], the monitoring report for that cohort should lead with calibration and place discrimination after it, since rank-ordering statistics become unstable as the positive class thins.

### Benchmarking that monitoring adds

This validation compared the champion against a challenger fitted on the development data, and that comparison is reported in the earlier benchmarking section; what it cannot supply is a reference estimated on data the development sample does not contain.

Monitoring should add two benchmarks of a kind the development data cannot give: the challenger refitted on successive production vintages and scored in parallel on the live cohorts, and an external or vendor reference such as a bureau-sourced or consortium score applied to the same accounts [[reg:SR11-7:V.1.b]].

Discrepancies against either benchmark should trigger investigation into the sources and degree of the differences rather than an automatic conclusion that the champion is in error, since the benchmark is itself an alternative prediction and may differ because of its data or its method [[reg:SR11-7:V.1.b]].

Where the external reference is a vendor product, the monitoring programme should also cover the bank's own outcomes analysis of that vendor's performance and the continued relevance of the data behind it [[reg:SR11-7:V.2]].

### What this validation could not cover

This validation observed the model on a fixed held-out split rather than on cohorts scored in production, so back-testing against realized outcomes over the model's performance window falls to monitoring, and that comparison of model outputs with corresponding real-world outcomes is where deterioration will first become visible [[reg:SR26-2:V.1.b]].

Implementation behaviour in the production scoring path was outside the scope exercised here, so monitoring should verify that inputs remain accurate, complete, and consistent with the model's purpose and design, and that code changes pass through change control [[reg:SR11-7:V.1.b]].

Override behaviour cannot be observed before the model is in use, so monitoring should record overrides, evaluate the reasons given, and track whether overridden decisions outperform the model, since a high override rate or a consistently improving override process points to needed revision [[reg:SR11-7:V.1.b]].

Stability of performance across sub-populations and across time was assessed on a single sample here, so the monitoring report should recompute the same slice-level views on each vintage rather than relying on the development-stage result to stand in for them.

The model's limitations identified at development should be reassessed regularly as part of monitoring, with the frequency and scope of the reports scaled to the model's materiality and to the availability of new data or modelling approaches [[reg:SR26-2:V.2]].

### Escalation

Persistent deviations outside the declared bounds cited above, or material errors surfaced by outcomes analysis, should trigger consideration of overlays, adjustment, recalibration, or redevelopment under the organisation's model risk policy [[reg:SR26-2:V.1.b]].

Any adjustment or redevelopment that follows should itself be subject to validation activity of appropriate range and rigour before it replaces the model in use [[reg:SR26-2:V]].

## Appendix A — Claims

Grounding precision 1.0000 before repair (239 of 239 claims verified) and 1.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 12/12; conceptual_soundness 57/57; data_integrity 46/46; outcomes 74/74; sensitivity 14/14; findings 25/25; monitoring 11/11.

Developer claims: The package declares 2 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). See Appendix D.

Excluded numeric tokens (not claims): label_number (decile 1); citation_hash (2ad8d1a5, 2510d49d, 2193cf5f, 5c6c2bfc); regulatory_section_id (SR26-2:V, SR26-2:V.1.a, SR26-2:IV.1, SR26-2:V.1.b); finding_id (F-001); package_version (1.0); extractor_returned_excluded_token (1.0, 6.0, 6, 2.0).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The subject was run end to end by the validation harness und… | 300 | ratio | runtime.max_seconds |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 2 | summary | The run covers a training split of 3500 rows and a held-out… | 3500 | count | n | train | eq | `[[art:2510d49d:profile.train.n]]` | verified | 3500 |
| 3 | summary | The run covers a training split of 3500 rows and a held-out… | 1500 | count | n | test | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 4 | summary | Discrimination on test clears the declared floor, with an AU… | 0.748 | ratio | auc | test | eq | `[[art:5c6c2bfc:metrics.test.auc]]` | verified | 0.7479888042 |
| 5 | summary | Discrimination on test clears the declared floor, with an AU… | 0.7 | ratio | auc | test | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 6 | summary | Probabilistic accuracy on test clears its declared ceiling,… | 0.1489 | ratio | brier | test | eq | `[[art:bbe69430:metrics.test.brier]]` | verified | 0.148850901 |
| 7 | summary | Probabilistic accuracy on test clears its declared ceiling,… | 0.2 | ratio | brier | test | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 8 | summary | Calibration on test falls inside its declared band, with a s… | 1.003 | ratio | calibration_slope | test | eq | `[[art:b7dbb687:calibration_slope.test]]` | verified | 1.002737656 |
| 9 | summary | Calibration on test falls inside its declared band, with a s… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 10 | summary | Calibration on test falls inside its declared band, with a s… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 11 | summary | Population stability between the two splits clears its decla… | 0.01095 | ratio | psi |  | eq | `[[art:381b2570:psi.max]]` | verified | 0.01095273358 |
| 12 | summary | Population stability between the two splits clears its decla… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 13 | conceptual_soundness | The champion is a logistic regression with a fitted intercep… | -1.396 | ratio | intercept |  | eq | `[[art:f181acb8:run.model_summary#intercept]]` | verified | -1.395828048 |
| 14 | conceptual_soundness | The champion is a logistic regression with a fitted intercep… | 3500 | count | n_train | train | eq | `[[art:f181acb8:run.model_summary#n_train]]` | verified | 3500 |
| 15 | conceptual_soundness | The champion is a logistic regression with a fitted intercep… | 0.748 | ratio | auc | test | eq | `[[art:5c6c2bfc:metrics.test.auc]]` | verified | 0.7479888042 |
| 16 | conceptual_soundness | The champion is a logistic regression with a fitted intercep… | 0.1489 | ratio | brier | test | eq | `[[art:bbe69430:metrics.test.brier]]` | verified | 0.148850901 |
| 17 | conceptual_soundness | The subject's feature inventory declares 12 features in tota… | 12 | count | features |  | eq | `[[art:2f9cb453:run.features#n]]` | verified | 12 |
| 18 | conceptual_soundness | Of these, 2 are known at origination and 10 are known before… | 2 | count | at_origination |  | eq | `[[art:2f9cb453:run.features#at_origination]]` | verified | 2 |
| 19 | conceptual_soundness | Of these, 2 are known at origination and 10 are known before… | 10 | count | before_period_start |  | eq | `[[art:2f9cb453:run.features#before_period_start]]` | verified | 10 |
| 20 | conceptual_soundness | None are drawn from during the performance period, at 0 , an… | 0 | count | during_period |  | eq | `[[art:2f9cb453:run.features#during_period]]` | verified | 0 |
| 21 | conceptual_soundness | None are drawn from during the performance period, at 0 , an… | 0 | count | after_outcome |  | eq | `[[art:2f9cb453:run.features#after_outcome]]` | verified | 0 |
| 22 | conceptual_soundness | The developer's own screen removed two features for collinea… | 10 | ratio | vif_threshold |  | eq | `[[art:f181acb8:run.model_summary#vif_threshold]]` | verified | 10 |
| 23 | conceptual_soundness | The last billed amount was removed at a variance inflation f… | 160.9 | ratio | vif |  | eq | `[[art:f181acb8:run.model_summary#removed.f_bill_last.vif]]` | verified | 160.888514 |
| 24 | conceptual_soundness | The last billed amount was removed at a variance inflation f… | 36.36 | ratio | vif |  | eq | `[[art:f181acb8:run.model_summary#removed.f_utilisation_mean_6m.vif]]` | verified | 36.356335 |
| 25 | conceptual_soundness | The largest coefficient by magnitude is on the most recent d… | 0.7334 | ratio | coefficient |  | eq | `[[art:f181acb8:run.model_summary#coefficients.f_delinq_last.value]]` | verified | 0.7334219534 |
| 26 | conceptual_soundness | The next largest are the six-month mean bill, at -0.3726 , a… | -0.3726 | ratio | coefficient |  | eq | `[[art:f181acb8:run.model_summary#coefficients.f_bill_mean_6m.value]]` | verified | -0.3726281079 |
| 27 | conceptual_soundness | The next largest are the six-month mean bill, at -0.3726 , a… | -0.3554 | ratio | coefficient |  | eq | `[[art:f181acb8:run.model_summary#coefficients.f_pay_ratio_mean_6m.value]]` | verified | -0.3553721566 |
| 28 | conceptual_soundness | Utilisation enters positively at 0.2662 , again as expected,… | 0.2662 | ratio | coefficient |  | eq | `[[art:f181acb8:run.model_summary#coefficients.f_utilisation.value]]` | verified | 0.2662083574 |
| 29 | conceptual_soundness | Utilisation enters positively at 0.2662 , again as expected,… | -0.2225 | ratio | coefficient |  | eq | `[[art:f181acb8:run.model_summary#coefficients.f_bill_trend_6m.value]]` | verified | -0.2224749257 |
| 30 | conceptual_soundness | The smaller terms are the delinquency count at 0.1226 , the… | 0.1226 | ratio | coefficient |  | eq | `[[art:f181acb8:run.model_summary#coefficients.f_delinq_count_6m.value]]` | verified | 0.1225797828 |
| 31 | conceptual_soundness | The smaller terms are the delinquency count at 0.1226 , the… | 0.1026 | ratio | coefficient |  | eq | `[[art:f181acb8:run.model_summary#coefficients.f_pay_ratio_last.value]]` | verified | 0.1025909773 |
| 32 | conceptual_soundness | The smaller terms are the delinquency count at 0.1226 , the… | 0.07266 | ratio | coefficient |  | eq | `[[art:f181acb8:run.model_summary#coefficients.f_limit_bal.value]]` | verified | 0.07265585996 |
| 33 | conceptual_soundness | The smaller terms are the delinquency count at 0.1226 , the… | -0.06726 | ratio | coefficient |  | eq | `[[art:f181acb8:run.model_summary#coefficients.f_age.value]]` | verified | -0.06725800744 |
| 34 | conceptual_soundness | The smaller terms are the delinquency count at 0.1226 , the… | -0.03221 | ratio | coefficient |  | eq | `[[art:f181acb8:run.model_summary#coefficients.f_delinq_max_6m.value]]` | verified | -0.03221440242 |
| 35 | conceptual_soundness | Fitted signs were compared against each feature's own univar… | 3 | count | n_disagreements | train | eq | `[[art:e223cd4a:sign_check.n_disagreements]]` | verified | 3 |
| 36 | conceptual_soundness | On the six-month maximum delinquency the fitted sign is -1 w… | -1 | ratio | coef_sign |  | eq | `[[art:b2de2a5f:sign_check.f_delinq_max_6m.coef_sign]]` | verified | -1 |
| 37 | conceptual_soundness | On the six-month maximum delinquency the fitted sign is -1 w… | 1 | ratio | univariate_direction | train | eq | `[[art:5a76c041:sign_check.f_delinq_max_6m.univariate_direction]]` | verified | 1 |
| 38 | conceptual_soundness | On the six-month maximum delinquency the fitted sign is -1 w… | 0 | ratio | agrees |  | eq | `[[art:b5785264:sign_check.f_delinq_max_6m.agrees]]` | verified | 0 |
| 39 | conceptual_soundness | On the six-month maximum delinquency the fitted sign is -1 w… | 0.0003598 | ratio | delta_auc | test | eq | `[[art:aace9667:ablation.f_delinq_max_6m.delta_auc]]` | verified | 0.0003597572022 |
| 40 | conceptual_soundness | On the six-month maximum delinquency the fitted sign is -1 w… | 0.748 | ratio | baseline_auc | test | eq | `[[art:3a44e438:ablation.baseline_auc]]` | verified | 0.7479888042 |
| 41 | conceptual_soundness | On the credit limit the fitted sign is 1 while its univariat… | 1 | ratio | coef_sign |  | eq | `[[art:76765f24:sign_check.f_limit_bal.coef_sign]]` | verified | 1 |
| 42 | conceptual_soundness | On the credit limit the fitted sign is 1 while its univariat… | -1 | ratio | univariate_direction | train | eq | `[[art:8cc36ad2:sign_check.f_limit_bal.univariate_direction]]` | verified | -1 |
| 43 | conceptual_soundness | On the credit limit the fitted sign is 1 while its univariat… | 0 | ratio | agrees |  | eq | `[[art:dc9d1c95:sign_check.f_limit_bal.agrees]]` | verified | 0 |
| 44 | conceptual_soundness | On the credit limit the fitted sign is 1 while its univariat… | 0.0004286 | ratio | delta_auc | test | eq | `[[art:1549706f:ablation.f_limit_bal.delta_auc]]` | verified | 0.0004286468792 |
| 45 | conceptual_soundness | On the last payment ratio the fitted sign is 1 while its uni… | 1 | ratio | coef_sign |  | eq | `[[art:8b49eed8:sign_check.f_pay_ratio_last.coef_sign]]` | verified | 1 |
| 46 | conceptual_soundness | On the last payment ratio the fitted sign is 1 while its uni… | -1 | ratio | univariate_direction | train | eq | `[[art:c9abae5e:sign_check.f_pay_ratio_last.univariate_direction]]` | verified | -1 |
| 47 | conceptual_soundness | On the last payment ratio the fitted sign is 1 while its uni… | 0 | ratio | agrees |  | eq | `[[art:847710b6:sign_check.f_pay_ratio_last.agrees]]` | verified | 0 |
| 48 | conceptual_soundness | On the last payment ratio the fitted sign is 1 while its uni… | 0.002411 | ratio | delta_auc | test | eq | `[[art:9f0e8a67:ablation.f_pay_ratio_last.delta_auc]]` | verified | 0.002411138695 |
| 49 | conceptual_soundness | The remaining retained features agree with their univariate… | 1 | ratio | agrees |  | eq | `[[art:547a15bd:sign_check.f_delinq_last.agrees]]` | verified | 1 |
| 50 | conceptual_soundness | The remaining retained features agree with their univariate… | 1 | ratio | agrees |  | eq | `[[art:b45fb558:sign_check.f_utilisation.agrees]]` | verified | 1 |
| 51 | conceptual_soundness | The remaining retained features agree with their univariate… | 1 | ratio | agrees |  | eq | `[[art:e5f0e61f:sign_check.f_pay_ratio_mean_6m.agrees]]` | verified | 1 |
| 52 | conceptual_soundness | The remaining retained features agree with their univariate… | 1 | ratio | agrees |  | eq | `[[art:7144f385:sign_check.f_bill_mean_6m.agrees]]` | verified | 1 |
| 53 | conceptual_soundness | The remaining retained features agree with their univariate… | 1 | ratio | agrees |  | eq | `[[art:5a646254:sign_check.f_bill_trend_6m.agrees]]` | verified | 1 |
| 54 | conceptual_soundness | The remaining retained features agree with their univariate… | 1 | ratio | agrees |  | eq | `[[art:e78b83df:sign_check.f_delinq_count_6m.agrees]]` | verified | 1 |
| 55 | conceptual_soundness | The remaining retained features agree with their univariate… | 1 | ratio | agrees |  | eq | `[[art:ef6b0a61:sign_check.f_age.agrees]]` | verified | 1 |
| 56 | conceptual_soundness | The ablation evidence also shows where the champion's discri… | 0.748 | ratio | baseline_auc | test | eq | `[[art:3a44e438:ablation.baseline_auc]]` | verified | 0.7479888042 |
| 57 | conceptual_soundness | Dropping the most recent delinquency indicator changes test… | -0.07585 | ratio | delta_auc | test | eq | `[[art:746389ef:ablation.f_delinq_last.delta_auc]]` | verified | -0.07585263733 |
| 58 | conceptual_soundness | Dropping utilisation changes test AUC by -0.01977 , and drop… | -0.01977 | ratio | delta_auc | test | eq | `[[art:3e7f047d:ablation.f_utilisation.delta_auc]]` | verified | -0.01976623436 |
| 59 | conceptual_soundness | Dropping utilisation changes test AUC by -0.01977 , and drop… | -0.0016 | ratio | delta_auc | test | eq | `[[art:8a56b9fe:ablation.f_bill_mean_6m.delta_auc]]` | verified | -0.001599771388 |
| 60 | conceptual_soundness | The rest change test AUC upward when removed: the six-month… | 0.006603 | ratio | delta_auc | test | eq | `[[art:562f5fd1:ablation.f_pay_ratio_mean_6m.delta_auc]]` | verified | 0.006603203115 |
| 61 | conceptual_soundness | The rest change test AUC upward when removed: the six-month… | 0.003279 | ratio | delta_auc | test | eq | `[[art:b8b0b1b2:ablation.f_bill_trend_6m.delta_auc]]` | verified | 0.003278638332 |
| 62 | conceptual_soundness | The rest change test AUC upward when removed: the six-month… | 0.0006812 | ratio | delta_auc | test | eq | `[[art:6e7487cc:ablation.f_delinq_count_6m.delta_auc]]` | verified | 0.0006812423615 |
| 63 | conceptual_soundness | The rest change test AUC upward when removed: the six-month… | 8.675e-05 | ratio | delta_auc | test | eq | `[[art:d9569286:ablation.f_age.delta_auc]]` | verified | 8.674996364e-05 |
| 64 | conceptual_soundness | The challenger reaches 0.824 AUC on test against the champio… | 0.824 | ratio | auc | test | eq | `[[art:bf5be719:challenger.auc]]` | verified | 0.823969015 |
| 65 | conceptual_soundness | The challenger reaches 0.824 AUC on test against the champio… | 0.748 | ratio | auc | test | eq | `[[art:5c6c2bfc:metrics.test.auc]]` | verified | 0.7479888042 |
| 66 | conceptual_soundness | The challenger reaches 0.824 AUC on test against the champio… | 0.07598 | ratio | delta_auc | test | eq | `[[art:c9e502ae:challenger.delta_auc]]` | verified | 0.0759802108 |
| 67 | conceptual_soundness | The threshold that decides whether such a difference matters… | 0.03 | ratio | delta_auc |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 68 | conceptual_soundness | The challenger's Brier score of 0.1258 is below the champion… | 0.1258 | ratio | brier | test | eq | `[[art:f9e0583d:challenger.brier]]` | verified | 0.1258050391 |
| 69 | conceptual_soundness | The challenger's Brier score of 0.1258 is below the champion… | 0.1489 | ratio | brier | test | eq | `[[art:bbe69430:metrics.test.brier]]` | verified | 0.148850901 |
| 70 | data_integrity | The training split holds 3500 rows and the test split holds… | 3500 | count | n | train | eq | `[[art:2510d49d:profile.train.n]]` | verified | 3500 |
| 71 | data_integrity | The training split holds 3500 rows and the test split holds… | 1500 | count | n | test | eq | `[[art:2193cf5f:profile.test.n]]` | verified | 1500 |
| 72 | data_integrity | The largest missing fraction over any column of the training… | 0 | ratio | missing | train | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 73 | data_integrity | The largest missing fraction over any column of the test spl… | 0 | ratio | missing | test | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 74 | data_integrity | The comparison the rule draws between the two splits is a di… | 0.1 | ratio | missing_gap |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 75 | data_integrity | - f_age: 0.008124 | 0.008124 | ratio | psi |  | eq | `[[art:5017e61e:psi.f_age]]` | verified | 0.008124281436 |
| 76 | data_integrity | - f_bill_mean_6m: 0.007124 | 0.007124 | ratio | psi |  | eq | `[[art:c519fca2:psi.f_bill_mean_6m]]` | verified | 0.007124196275 |
| 77 | data_integrity | - f_bill_trend_6m: 0.00958 | 0.00958 | ratio | psi |  | eq | `[[art:c3f51172:psi.f_bill_trend_6m]]` | verified | 0.009579614525 |
| 78 | data_integrity | - f_delinq_count_6m: 0.002069 | 0.002069 | ratio | psi |  | eq | `[[art:6a2fba4e:psi.f_delinq_count_6m]]` | verified | 0.002069275496 |
| 79 | data_integrity | - f_delinq_last: 0.00285 | 0.00285 | ratio | psi |  | eq | `[[art:9d44627e:psi.f_delinq_last]]` | verified | 0.002849633848 |
| 80 | data_integrity | - f_delinq_max_6m: 0.005498 | 0.005498 | ratio | psi |  | eq | `[[art:05bccd03:psi.f_delinq_max_6m]]` | verified | 0.005498249408 |
| 81 | data_integrity | - f_limit_bal: 0.01095 | 0.01095 | ratio | psi |  | eq | `[[art:1932cef9:psi.f_limit_bal]]` | verified | 0.01095273358 |
| 82 | data_integrity | - f_pay_ratio_last: 0.004966 | 0.004966 | ratio | psi |  | eq | `[[art:f85ffaec:psi.f_pay_ratio_last]]` | verified | 0.00496591109 |
| 83 | data_integrity | - f_pay_ratio_mean_6m: 0.0055 | 0.0055 | ratio | psi |  | eq | `[[art:4d206390:psi.f_pay_ratio_mean_6m]]` | verified | 0.005500252946 |
| 84 | data_integrity | - f_utilisation: 0.004244 | 0.004244 | ratio | psi |  | eq | `[[art:b8b6b215:psi.f_utilisation]]` | verified | 0.0042440485 |
| 85 | data_integrity | The score itself shifts between the two splits by 0.007023 ,… | 0.007023 | ratio | psi |  | eq | `[[art:a2885abf:psi.y_score]]` | verified | 0.007023143302 |
| 86 | data_integrity | The largest population stability index across the features a… | 0.01095 | ratio | psi |  | eq | `[[art:381b2570:psi.max]]` | verified | 0.01095273358 |
| 87 | data_integrity | The largest population stability index across the features a… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 88 | data_integrity | The package file declares the same bound at 0.25 , so the va… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 89 | data_integrity | - f_age: 0.0009476 | 0.0009476 | ratio | csi |  | eq | `[[art:7eca72ca:csi.f_age]]` | verified | 0.0009475732594 |
| 90 | data_integrity | - f_bill_mean_6m: 0.002369 | 0.002369 | ratio | csi |  | eq | `[[art:a56ef25e:csi.f_bill_mean_6m]]` | verified | 0.002369326368 |
| 91 | data_integrity | - f_bill_trend_6m: 0.00633 | 0.00633 | ratio | csi |  | eq | `[[art:e6bbd7a6:csi.f_bill_trend_6m]]` | verified | 0.006329590221 |
| 92 | data_integrity | - f_delinq_count_6m: 0.002449 | 0.002449 | ratio | csi |  | eq | `[[art:5c1ddd21:csi.f_delinq_count_6m]]` | verified | 0.002448902116 |
| 93 | data_integrity | - f_delinq_last: 0.02363 | 0.02363 | ratio | csi |  | eq | `[[art:dadfe01c:csi.f_delinq_last]]` | verified | 0.02362581795 |
| 94 | data_integrity | - f_delinq_max_6m: 0.0008965 | 0.0008965 | ratio | csi |  | eq | `[[art:20767939:csi.f_delinq_max_6m]]` | verified | 0.0008964784296 |
| 95 | data_integrity | - f_limit_bal: 0.001211 | 0.001211 | ratio | csi |  | eq | `[[art:810ae3c7:csi.f_limit_bal]]` | verified | 0.001211461258 |
| 96 | data_integrity | - f_pay_ratio_last: 0.001924 | 0.001924 | ratio | csi |  | eq | `[[art:f337e4e5:csi.f_pay_ratio_last]]` | verified | 0.001923767196 |
| 97 | data_integrity | - f_pay_ratio_mean_6m: 0.001768 | 0.001768 | ratio | csi |  | eq | `[[art:ff31f4b4:csi.f_pay_ratio_mean_6m]]` | verified | 0.001768345794 |
| 98 | data_integrity | - f_utilisation: 0.004042 | 0.004042 | ratio | csi |  | eq | `[[art:b9d55682:csi.f_utilisation]]` | verified | 0.004041856699 |
| 99 | data_integrity | The largest characteristic contribution is 0.02363 , and it… | 0.02363 | ratio | csi |  | eq | `[[art:e56cb179:csi.max]]` | verified | 0.02362581795 |
| 100 | data_integrity | The largest characteristic contribution is 0.02363 , and it… | 0.02363 | ratio | csi |  | eq | `[[art:dadfe01c:csi.f_delinq_last]]` | verified | 0.02362581795 |
| 101 | data_integrity | That largest contribution is above the largest population in… | 0.01095 | ratio | psi |  | eq | `[[art:381b2570:psi.max]]` | verified | 0.01095273358 |
| 102 | data_integrity | That largest contribution is above the largest population in… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 103 | data_integrity | The declared-timing screen counts features declared as obser… | 0 | count | n_flagged |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 104 | data_integrity | The strongest single feature reaches an area under the curve… | 0.6831 | ratio | auc |  | eq | `[[art:fd829fc4:leakage.target_corr.max_single_feature_auc]]` | verified | 0.6831414154 |
| 105 | data_integrity | The strongest single feature reaches an area under the curve… | 0.9 | ratio | auc |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 106 | data_integrity | The first arm measures the share of test rows whose identifi… | 0 | ratio | overlap | test | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 107 | data_integrity | The first arm measures the share of test rows whose identifi… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 108 | data_integrity | The second arm measures the share of test rows whose feature… | 0 | ratio | overlap | test | eq | `[[art:0fec8048:leakage.overlap.features]]` | verified | 0 |
| 109 | data_integrity | The second arm is read against the bound that rule actually… | 0.005 | ratio | overlap |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 110 | data_integrity | Here the share of train rows whose feature values are not un… | 0 | ratio | duplicates | train | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 111 | data_integrity | Here the share of train rows whose feature values are not un… | 0.005 | ratio | overlap |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 112 | data_integrity | Here the share of train rows whose feature values are not un… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 113 | data_integrity | The overlap screen over test rows records 0 , consistent wit… | 0 | ratio | overlap | test | eq | `[[art:4c9fcd09:leakage.overlap]]` | verified | 0 |
| 114 | data_integrity | The name screen matches feature names against a target-adjac… | 0 | count | n_matched |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 115 | data_integrity | Ongoing monitoring should therefore continue to track the po… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 116 | outcomes | Discrimination is reported first and calibration second, bec… | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 117 | outcomes | Discrimination is reported first and calibration second, bec… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 118 | outcomes | \| Rows \| 3500 \| 1500 \| | 3500 | count | n | train | eq | `[[art:564683ee:metrics.train.n]]` | verified | 3500 |
| 119 | outcomes | \| Rows \| 3500 \| 1500 \| | 1500 | count | n | test | eq | `[[art:64fcf14d:metrics.test.n]]` | verified | 1500 |
| 120 | outcomes | \| Event rate \| 0.2246 \| 0.2247 \| | 0.2246 | ratio | event_rate | train | eq | `[[art:133a5ff8:metrics.train.event_rate]]` | verified | 0.2245714286 |
| 121 | outcomes | \| Event rate \| 0.2246 \| 0.2247 \| | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 122 | outcomes | \| AUC \| 0.7584 \| 0.748 \| | 0.7584 | ratio | auc | train | eq | `[[art:14b38a2b:metrics.train.auc]]` | verified | 0.7584356677 |
| 123 | outcomes | \| AUC \| 0.7584 \| 0.748 \| | 0.748 | ratio | auc | test | eq | `[[art:5c6c2bfc:metrics.test.auc]]` | verified | 0.7479888042 |
| 124 | outcomes | \| Gini \| 0.5169 \| 0.496 \| | 0.5169 | ratio | gini | train | eq | `[[art:b4da846e:metrics.train.gini]]` | verified | 0.5168713353 |
| 125 | outcomes | \| Gini \| 0.5169 \| 0.496 \| | 0.496 | ratio | gini | test | eq | `[[art:8e5918d8:metrics.test.gini]]` | verified | 0.4959776083 |
| 126 | outcomes | \| KS \| 0.4451 \| 0.4183 \| | 0.4451 | ratio | ks | train | eq | `[[art:ccc12729:metrics.train.ks]]` | verified | 0.4451397991 |
| 127 | outcomes | \| KS \| 0.4451 \| 0.4183 \| | 0.4183 | ratio | ks | test | eq | `[[art:90751047:metrics.test.ks]]` | verified | 0.4182675012 |
| 128 | outcomes | \| Brier \| 0.1489 \| 0.1489 \| | 0.1489 | ratio | brier | train | eq | `[[art:be669a99:metrics.train.brier]]` | verified | 0.1489149059 |
| 129 | outcomes | \| Brier \| 0.1489 \| 0.1489 \| | 0.1489 | ratio | brier | test | eq | `[[art:bbe69430:metrics.test.brier]]` | verified | 0.148850901 |
| 130 | outcomes | \| Log loss \| 0.465 \| 0.4673 \| | 0.465 | ratio | logloss | train | eq | `[[art:4f02e465:metrics.train.logloss]]` | verified | 0.4650014911 |
| 131 | outcomes | \| Log loss \| 0.465 \| 0.4673 \| | 0.4673 | ratio | logloss | test | eq | `[[art:dda8da69:metrics.test.logloss]]` | verified | 0.4672914712 |
| 132 | outcomes | \| Mean predicted \| 0.2246 \| 0.2211 \| | 0.2246 | ratio | mean_predicted | train | eq | `[[art:605cce58:metrics.train.mean_predicted]]` | verified | 0.2246226934 |
| 133 | outcomes | \| Mean predicted \| 0.2246 \| 0.2211 \| | 0.2211 | ratio | mean_predicted | test | eq | `[[art:4d2f8a37:metrics.test.mean_predicted]]` | verified | 0.2211048954 |
| 134 | outcomes | The top two deciles hold 0.4718 of test events, and on train… | 0.4718 | ratio | top2_capture | test | eq | `[[art:d4a1cf7d:deciles.test.top2_capture]]` | verified | 0.471810089 |
| 135 | outcomes | The top two deciles hold 0.4718 of test events, and on train… | 0.4517 | ratio | top2_capture | train | eq | `[[art:1d20c762:deciles.train.top2_capture]]` | verified | 0.451653944 |
| 136 | outcomes | On the train-to-test movement in discrimination, AUC is 0.75… | 0.7584 | ratio | auc | train | eq | `[[art:14b38a2b:metrics.train.auc]]` | verified | 0.7584356677 |
| 137 | outcomes | On the train-to-test movement in discrimination, AUC is 0.75… | 0.748 | ratio | auc | test | eq | `[[art:5c6c2bfc:metrics.test.auc]]` | verified | 0.7479888042 |
| 138 | outcomes | The bound declared for the train-to-test AUC gap is 0.08 , a… | 0.08 | ratio | auc_gap |  | eq | `[[art:630f28f4:threshold.O1.auc_gap]]` | verified | 0.08 |
| 139 | outcomes | Turning to calibration, the logistic regression of the outco… | 1.003 | ratio | calibration_slope | test | eq | `[[art:b7dbb687:calibration_slope.test]]` | verified | 1.002737656 |
| 140 | outcomes | Turning to calibration, the logistic regression of the outco… | 0.8 | ratio | calibration_slope |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 141 | outcomes | Turning to calibration, the logistic regression of the outco… | 1.2 | ratio | calibration_slope |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 142 | outcomes | The intercept of that same regression on test is 0.02729 . | 0.02729 | ratio | calibration_intercept | test | eq | `[[art:b69c6b52:calibration_intercept.test]]` | verified | 0.0272850692 |
| 143 | outcomes | The corresponding train values are a slope of 1.002 and an i… | 1.002 | ratio | calibration_slope | train | eq | `[[art:d02e3091:calibration_slope.train]]` | verified | 1.002102954 |
| 144 | outcomes | The corresponding train values are a slope of 1.002 and an i… | 0.002062 | ratio | calibration_intercept | train | eq | `[[art:ed381a81:calibration_intercept.train]]` | verified | 0.002061562686 |
| 145 | outcomes | Mean predicted probability on test is 0.2211 against an obse… | 0.2211 | ratio | mean_predicted | test | eq | `[[art:4d2f8a37:metrics.test.mean_predicted]]` | verified | 0.2211048954 |
| 146 | outcomes | Mean predicted probability on test is 0.2211 against an obse… | 0.2247 | ratio | event_rate | test | eq | `[[art:9209d200:metrics.test.event_rate]]` | verified | 0.2246666667 |
| 147 | outcomes | Expressed relatively, that separation is 0.01585 , inside th… | 0.01585 | ratio | mean_rel_gap | test | eq | `[[art:d8ffb3d0:calibration.mean_rel_gap.test]]` | verified | 0.01585358118 |
| 148 | outcomes | Expressed relatively, that separation is 0.01585 , inside th… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 149 | outcomes | On train the same relative quantity is 0.0002283 , and compa… | 0.0002283 | ratio | mean_rel_gap | train | eq | `[[art:53738d45:calibration.mean_rel_gap.train]]` | verified | 0.0002282786273 |
| 150 | outcomes | On test, AUC on this sub-population falls 0.1791 below AUC o… | 0.1791 | ratio | auc_gap | test | eq | `[[art:f0689663:metrics.test.sub.f_utilisation_high.auc_gap]]` | verified | 0.1790943942 |
| 151 | outcomes | On test, AUC on this sub-population falls 0.1791 below AUC o… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 152 | outcomes | On train the same shortfall is 0.1853 , likewise above that… | 0.1853 | ratio | auc_gap | train | eq | `[[art:43f1ad7f:metrics.train.sub.f_utilisation_high.auc_gap]]` | verified | 0.1852827953 |
| 153 | outcomes | The sub-population holds 0.5 of test and 0.5 of train, above… | 0.5 | ratio | share | test | eq | `[[art:8e769cfa:metrics.test.sub.f_utilisation_high.share]]` | verified | 0.5 |
| 154 | outcomes | The sub-population holds 0.5 of test and 0.5 of train, above… | 0.5 | ratio | share | train | eq | `[[art:d3d28c9a:metrics.train.sub.f_utilisation_high.share]]` | verified | 0.5 |
| 155 | outcomes | The sub-population holds 0.5 of test and 0.5 of train, above… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 156 | outcomes | The sub-population holds 0.5 of test and 0.5 of train, above… | 0.95 | ratio | slice_max_share |  | eq | `[[art:a928a05c:threshold.O1.slice_max_share]]` | verified | 0.95 |
| 157 | outcomes | Mean predicted on this sub-population of test is 0.2286 agai… | 0.2286 | ratio | mean_predicted | test | eq | `[[art:c37ecc36:metrics.test.sub.f_utilisation_high.mean_predicted]]` | verified | 0.2286105275 |
| 158 | outcomes | Mean predicted on this sub-population of test is 0.2286 agai… | 0.2333 | ratio | event_rate | test | eq | `[[art:5b836e8e:metrics.test.sub.f_utilisation_high.event_rate]]` | verified | 0.2333333333 |
| 159 | outcomes | Mean predicted on this sub-population of test is 0.2286 agai… | 0.02024 | ratio | mean_rel_gap | test | eq | `[[art:42b00194:metrics.test.sub.f_utilisation_high.mean_rel_gap]]` | verified | 0.02024059629 |
| 160 | outcomes | Mean predicted on this sub-population of test is 0.2286 agai… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 161 | outcomes | On train, mean predicted of 0.2329 against an observed rate… | 0.2329 | ratio | mean_predicted | train | eq | `[[art:315b25f7:metrics.train.sub.f_utilisation_high.mean_predicted]]` | verified | 0.2329237961 |
| 162 | outcomes | On train, mean predicted of 0.2329 against an observed rate… | 0.2246 | ratio | event_rate | train | eq | `[[art:b34c6bc2:metrics.train.sub.f_utilisation_high.event_rate]]` | verified | 0.2245714286 |
| 163 | outcomes | On train, mean predicted of 0.2329 against an observed rate… | 0.03719 | ratio | mean_rel_gap | train | eq | `[[art:82b6fda5:metrics.train.sub.f_utilisation_high.mean_rel_gap]]` | verified | 0.03719247611 |
| 164 | outcomes | On test, the distance of this sub-population's AUC below AUC… | -0.1506 | ratio | auc_gap | test | eq | `[[art:03dfbb51:metrics.test.sub.f_utilisation_low.auc_gap]]` | verified | -0.1506002611 |
| 165 | outcomes | On test, the distance of this sub-population's AUC below AUC… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 166 | outcomes | On train the corresponding quantity is -0.1558 , likewise in… | -0.1558 | ratio | auc_gap | train | eq | `[[art:0e0b12c1:metrics.train.sub.f_utilisation_low.auc_gap]]` | verified | -0.155785382 |
| 167 | outcomes | The sub-population holds 0.5 of test and 0.5 of train, above… | 0.5 | ratio | share | test | eq | `[[art:03601889:metrics.test.sub.f_utilisation_low.share]]` | verified | 0.5 |
| 168 | outcomes | The sub-population holds 0.5 of test and 0.5 of train, above… | 0.5 | ratio | share | train | eq | `[[art:6314e9e5:metrics.train.sub.f_utilisation_low.share]]` | verified | 0.5 |
| 169 | outcomes | The sub-population holds 0.5 of test and 0.5 of train, above… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 170 | outcomes | Mean predicted on this sub-population of test is 0.2136 agai… | 0.2136 | ratio | mean_predicted | test | eq | `[[art:2a5870fc:metrics.test.sub.f_utilisation_low.mean_predicted]]` | verified | 0.2135992633 |
| 171 | outcomes | Mean predicted on this sub-population of test is 0.2136 agai… | 0.216 | ratio | event_rate | test | eq | `[[art:7a44f440:metrics.test.sub.f_utilisation_low.event_rate]]` | verified | 0.216 |
| 172 | outcomes | Mean predicted on this sub-population of test is 0.2136 agai… | 0.01111 | ratio | mean_rel_gap | test | eq | `[[art:6a2eb11d:metrics.test.sub.f_utilisation_low.mean_rel_gap]]` | verified | 0.01111452166 |
| 173 | outcomes | Mean predicted on this sub-population of test is 0.2136 agai… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 174 | outcomes | On train, mean predicted of 0.2163 against an observed rate… | 0.2163 | ratio | mean_predicted | train | eq | `[[art:cfd48cc6:metrics.train.sub.f_utilisation_low.mean_predicted]]` | verified | 0.2163215908 |
| 175 | outcomes | On train, mean predicted of 0.2163 against an observed rate… | 0.2246 | ratio | event_rate | train | eq | `[[art:ecfe7914:metrics.train.sub.f_utilisation_low.event_rate]]` | verified | 0.2245714286 |
| 176 | outcomes | On train, mean predicted of 0.2163 against an observed rate… | 0.03674 | ratio | mean_rel_gap | train | eq | `[[art:e1454a17:metrics.train.sub.f_utilisation_low.mean_rel_gap]]` | verified | 0.03673591886 |
| 177 | outcomes | On test, the distance of this sub-population's AUC below AUC… | -0.001967 | ratio | auc_gap | test | eq | `[[art:5b735235:metrics.test.sub.f_delinq_count_6m_high.auc_gap]]` | verified | -0.001967336199 |
| 178 | outcomes | On test, the distance of this sub-population's AUC below AUC… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 179 | outcomes | On train the corresponding shortfall is 0.01154 , also insid… | 0.01154 | ratio | auc_gap | train | eq | `[[art:066e4d48:metrics.train.sub.f_delinq_count_6m_high.auc_gap]]` | verified | 0.01153989343 |
| 180 | outcomes | The sub-population holds 0.3667 of test and 0.3777 of train,… | 0.3667 | ratio | share | test | eq | `[[art:8ea39bd5:metrics.test.sub.f_delinq_count_6m_high.share]]` | verified | 0.3666666667 |
| 181 | outcomes | The sub-population holds 0.3667 of test and 0.3777 of train,… | 0.3777 | ratio | share | train | eq | `[[art:49900347:metrics.train.sub.f_delinq_count_6m_high.share]]` | verified | 0.3777142857 |
| 182 | outcomes | The sub-population holds 0.3667 of test and 0.3777 of train,… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 183 | outcomes | Mean predicted on this sub-population of test is 0.3198 agai… | 0.3198 | ratio | mean_predicted | test | eq | `[[art:4aa724a5:metrics.test.sub.f_delinq_count_6m_high.mean_predicted]]` | verified | 0.3198382924 |
| 184 | outcomes | Mean predicted on this sub-population of test is 0.3198 agai… | 0.3455 | ratio | event_rate | test | eq | `[[art:d9d79704:metrics.test.sub.f_delinq_count_6m_high.event_rate]]` | verified | 0.3454545455 |
| 185 | outcomes | Mean predicted on this sub-population of test is 0.3198 agai… | 0.07415 | ratio | mean_rel_gap | test | eq | `[[art:88c4873c:metrics.test.sub.f_delinq_count_6m_high.mean_rel_gap]]` | verified | 0.07415231158 |
| 186 | outcomes | Mean predicted on this sub-population of test is 0.3198 agai… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 187 | outcomes | On train, mean predicted of 0.3177 against an observed rate… | 0.3177 | ratio | mean_predicted | train | eq | `[[art:ec725b41:metrics.train.sub.f_delinq_count_6m_high.mean_predicted]]` | verified | 0.3177478342 |
| 188 | outcomes | On train, mean predicted of 0.3177 against an observed rate… | 0.3162 | ratio | event_rate | train | eq | `[[art:70daaf30:metrics.train.sub.f_delinq_count_6m_high.event_rate]]` | verified | 0.3161875946 |
| 189 | outcomes | On train, mean predicted of 0.3177 against an observed rate… | 0.004935 | ratio | mean_rel_gap | train | eq | `[[art:41f6e723:metrics.train.sub.f_delinq_count_6m_high.mean_rel_gap]]` | verified | 0.004934537744 |
| 190 | sensitivity | The largest variance inflation factor across the retained fe… | 7.295 | ratio | vif |  | eq | `[[art:9ae7c45b:vif.max]]` | verified | 7.295299885 |
| 191 | sensitivity | The largest variance inflation factor across the retained fe… | 10 | ratio | vif |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 192 | sensitivity | Belsley's condition number of the column-standardised design… | 5.547 | ratio | condition_number |  | eq | `[[art:e41b9562:condition_number]]` | verified | 5.546934633 |
| 193 | sensitivity | Belsley's condition number of the column-standardised design… | 30 | ratio | condition_number |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 194 | sensitivity | The feature carrying the largest inflation is f_bill_mean_6m… | 7.295 | ratio | vif |  | eq | `[[art:7b32e2ef:vif.f_bill_mean_6m]]` | verified | 7.295299885 |
| 195 | sensitivity | The feature carrying the largest inflation is f_bill_mean_6m… | 7.264 | ratio | vif |  | eq | `[[art:5f2b9e12:vif.f_pay_ratio_last]]` | verified | 7.264342098 |
| 196 | sensitivity | The feature carrying the largest inflation is f_bill_mean_6m… | 7.259 | ratio | vif |  | eq | `[[art:bf28797b:vif.f_pay_ratio_mean_6m]]` | verified | 7.25926398 |
| 197 | sensitivity | The remaining retained features fall further below the thres… | 4.803 | ratio | vif |  | eq | `[[art:99b238f2:vif.f_limit_bal]]` | verified | 4.803401129 |
| 198 | sensitivity | The remaining retained features fall further below the thres… | 3.215 | ratio | vif |  | eq | `[[art:da156a12:vif.f_utilisation]]` | verified | 3.215148369 |
| 199 | sensitivity | The remaining retained features fall further below the thres… | 2.561 | ratio | vif |  | eq | `[[art:15bac45f:vif.f_delinq_count_6m]]` | verified | 2.561484187 |
| 200 | sensitivity | The remaining retained features fall further below the thres… | 2.408 | ratio | vif |  | eq | `[[art:e4b87600:vif.f_delinq_max_6m]]` | verified | 2.40773 |
| 201 | sensitivity | The remaining retained features fall further below the thres… | 1.412 | ratio | vif |  | eq | `[[art:be34e000:vif.f_delinq_last]]` | verified | 1.411555667 |
| 202 | sensitivity | The remaining retained features fall further below the thres… | 1.201 | ratio | vif |  | eq | `[[art:c2d88735:vif.f_bill_trend_6m]]` | verified | 1.201449441 |
| 203 | sensitivity | The remaining retained features fall further below the thres… | 1.002 | ratio | vif |  | eq | `[[art:561dd3fe:vif.f_age]]` | verified | 1.001957997 |
| 204 | findings | A gradient-boosted challenger reaches an AUC of 0.824 on the… | 0.824 | ratio | auc | test | eq | `[[art:bf5be719:challenger.auc]]` | verified | 0.823969015 |
| 205 | findings | A gradient-boosted challenger reaches an AUC of 0.824 on the… | 0.748 | ratio | auc | test | eq | `[[art:5c6c2bfc:metrics.test.auc]]` | verified | 0.7479888042 |
| 206 | findings | The challenger's lead over the champion is 0.07598 , above t… | 0.07598 | ratio | delta_auc | test | eq | `[[art:c9e502ae:challenger.delta_auc]]` | verified | 0.0759802108 |
| 207 | findings | The challenger's lead over the champion is 0.07598 , above t… | 0.03 | ratio | delta_auc |  | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 208 | findings | Model developer: within the sub-population `f_utilisation >… | 0.5689 | ratio | auc | test | eq | `[[art:8b9b9b27:metrics.test.sub.f_utilisation_high.auc]]` | verified | 0.5688944099 |
| 209 | findings | Model developer: within the sub-population `f_utilisation >… | 0.748 | ratio | auc | test | eq | `[[art:5c6c2bfc:metrics.test.auc]]` | verified | 0.7479888042 |
| 210 | findings | Model developer: within the sub-population `f_utilisation >… | 0.1791 | ratio | auc_gap | test | eq | `[[art:f0689663:metrics.test.sub.f_utilisation_high.auc_gap]]` | verified | 0.1790943942 |
| 211 | findings | Model developer: within the sub-population `f_utilisation >… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 212 | findings | Model developer: within the sub-population `f_utilisation >… | 0.5 | ratio | share | test | eq | `[[art:8e769cfa:metrics.test.sub.f_utilisation_high.share]]` | verified | 0.5 |
| 213 | findings | Model developer: within the sub-population `f_utilisation >… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 214 | findings | Model developer: within the same sub-population `f_utilisati… | 0.5732 | ratio | auc | train | eq | `[[art:22699b62:metrics.train.sub.f_utilisation_high.auc]]` | verified | 0.5731528724 |
| 215 | findings | Model developer: within the same sub-population `f_utilisati… | 0.7584 | ratio | auc | train | eq | `[[art:14b38a2b:metrics.train.auc]]` | verified | 0.7584356677 |
| 216 | findings | Model developer: within the same sub-population `f_utilisati… | 0.1853 | ratio | auc_gap | train | eq | `[[art:43f1ad7f:metrics.train.sub.f_utilisation_high.auc_gap]]` | verified | 0.1852827953 |
| 217 | findings | Model developer: within the same sub-population `f_utilisati… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 218 | findings | Model developer: within the same sub-population `f_utilisati… | 0.5 | ratio | share | train | eq | `[[art:d3d28c9a:metrics.train.sub.f_utilisation_high.share]]` | verified | 0.5 |
| 219 | findings | Model developer: within the same sub-population `f_utilisati… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 220 | findings | Model developer: on what grounds does the fitted coefficient… | -1 | ratio | coef_sign |  | eq | `[[art:b2de2a5f:sign_check.f_delinq_max_6m.coef_sign]]` | verified | -1 |
| 221 | findings | Model developer: on what grounds does the fitted coefficient… | 1 | ratio | univariate_direction | train | eq | `[[art:5a76c041:sign_check.f_delinq_max_6m.univariate_direction]]` | verified | 1 |
| 222 | findings | Model developer: on what grounds does the fitted coefficient… | 0 | ratio | agrees |  | eq | `[[art:b5785264:sign_check.f_delinq_max_6m.agrees]]` | verified | 0 |
| 223 | findings | Model developer: on what grounds does the fitted coefficient… | 1 | ratio | coef_sign |  | eq | `[[art:76765f24:sign_check.f_limit_bal.coef_sign]]` | verified | 1 |
| 224 | findings | Model developer: on what grounds does the fitted coefficient… | -1 | ratio | univariate_direction | train | eq | `[[art:8cc36ad2:sign_check.f_limit_bal.univariate_direction]]` | verified | -1 |
| 225 | findings | Model developer: on what grounds does the fitted coefficient… | 0 | ratio | agrees |  | eq | `[[art:dc9d1c95:sign_check.f_limit_bal.agrees]]` | verified | 0 |
| 226 | findings | Model developer: on what grounds does the fitted coefficient… | 1 | ratio | coef_sign |  | eq | `[[art:8b49eed8:sign_check.f_pay_ratio_last.coef_sign]]` | verified | 1 |
| 227 | findings | Model developer: on what grounds does the fitted coefficient… | -1 | ratio | univariate_direction | train | eq | `[[art:c9abae5e:sign_check.f_pay_ratio_last.univariate_direction]]` | verified | -1 |
| 228 | findings | Model developer: on what grounds does the fitted coefficient… | 0 | ratio | agrees |  | eq | `[[art:847710b6:sign_check.f_pay_ratio_last.agrees]]` | verified | 0 |
| 229 | monitoring | - Rank-ordering should be recomputed on each completed perfo… | 0.7 | ratio | auc | test | eq | `[[art:8bfd02cc:threshold.package.auc.test.min]]` | verified | 0.7 |
| 230 | monitoring | - Rank-ordering should be recomputed on each completed perfo… | 0.748 | ratio | auc | test | eq | `[[art:5c6c2bfc:metrics.test.auc]]` | verified | 0.7479888042 |
| 231 | monitoring | - Probabilistic accuracy should be tracked on the same quart… | 0.2 | ratio | brier | test | eq | `[[art:d0f98b9c:threshold.package.brier.test.max]]` | verified | 0.2 |
| 232 | monitoring | - Probabilistic accuracy should be tracked on the same quart… | 0.1489 | ratio | brier | test | eq | `[[art:bbe69430:metrics.test.brier]]` | verified | 0.148850901 |
| 233 | monitoring | - The calibration slope should be refitted quarterly on real… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 234 | monitoring | - The calibration slope should be refitted quarterly on real… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 235 | monitoring | - The calibration slope should be refitted quarterly on real… | 1.003 | ratio | calibration_slope | test | eq | `[[art:b7dbb687:calibration_slope.test]]` | verified | 1.002737656 |
| 236 | monitoring | - Population stability of the scoring inputs and of the scor… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 237 | monitoring | - Population stability of the scoring inputs and of the scor… | 0.01095 | ratio | psi |  | eq | `[[art:381b2570:psi.max]]` | verified | 0.01095273358 |
| 238 | monitoring | The earlier performance section of this report presented dis… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |
| 239 | monitoring | If a future monitored cohort has an event rate that falls be… | 0.05 | ratio | event_rate |  | eq | `[[art:42f1351e:rule.calibration_first_event_rate]]` | verified | 0.05 |

## Appendix B — Artifact index

The store holds 243 artifacts; the 166 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `ablation.baseline_auc` | `3a44e438` | scalar | 0.7479888042 | AUC on test of a refit of the champion's functional form on every retained feature, the level each ablation delta is measured from |
| `ablation.f_age.delta_auc` | `d9569286` | scalar | 8.674996364e-05 | change in test AUC when the champion's form is refitted without f_age |
| `ablation.f_bill_mean_6m.delta_auc` | `8a56b9fe` | scalar | -0.001599771388 | change in test AUC when the champion's form is refitted without f_bill_mean_6m |
| `ablation.f_bill_trend_6m.delta_auc` | `b8b0b1b2` | scalar | 0.003278638332 | change in test AUC when the champion's form is refitted without f_bill_trend_6m |
| `ablation.f_delinq_count_6m.delta_auc` | `6e7487cc` | scalar | 0.0006812423615 | change in test AUC when the champion's form is refitted without f_delinq_count_6m |
| `ablation.f_delinq_last.delta_auc` | `746389ef` | scalar | -0.07585263733 | change in test AUC when the champion's form is refitted without f_delinq_last |
| `ablation.f_delinq_max_6m.delta_auc` | `aace9667` | scalar | 0.0003597572022 | change in test AUC when the champion's form is refitted without f_delinq_max_6m |
| `ablation.f_limit_bal.delta_auc` | `1549706f` | scalar | 0.0004286468792 | change in test AUC when the champion's form is refitted without f_limit_bal |
| `ablation.f_pay_ratio_last.delta_auc` | `9f0e8a67` | scalar | 0.002411138695 | change in test AUC when the champion's form is refitted without f_pay_ratio_last |
| `ablation.f_pay_ratio_mean_6m.delta_auc` | `562f5fd1` | scalar | 0.006603203115 | change in test AUC when the champion's form is refitted without f_pay_ratio_mean_6m |
| `ablation.f_utilisation.delta_auc` | `3e7f047d` | scalar | -0.01976623436 | change in test AUC when the champion's form is refitted without f_utilisation |
| `calibration.mean_rel_gap.test` | `d8ffb3d0` | scalar | 0.01585358118 | mean predicted against observed on test, relative |
| `calibration.mean_rel_gap.train` | `53738d45` | scalar | 0.0002282786273 | mean predicted against observed on train, relative |
| `calibration.test` | `508ffcf8` | table | table, 10 rows | calibration by decile of predicted probability on test |
| `calibration_intercept.test` | `b69c6b52` | scalar | 0.0272850692 | logistic regression of the outcome on logit(p) on test: the intercept |
| `calibration_intercept.train` | `ed381a81` | scalar | 0.002061562686 | logistic regression of the outcome on logit(p) on train: the intercept |
| `calibration_slope.test` | `b7dbb687` | scalar | 1.002737656 | logistic regression of the outcome on logit(p) on test: the slope |
| `calibration_slope.train` | `d02e3091` | scalar | 1.002102954 | logistic regression of the outcome on logit(p) on train: the slope |
| `challenger.auc` | `bf5be719` | scalar | 0.823969015 | the challenger's AUC on test |
| `challenger.brier` | `f9e0583d` | scalar | 0.1258050391 | the challenger's Brier score on test |
| `challenger.delta_auc` | `c9e502ae` | scalar | 0.0759802108 | the challenger's AUC on test minus the champion's |
| `condition_number` | `e41b9562` | scalar | 5.546934633 | Belsley's condition number of the column-standardised design |
| `csi.f_age` | `7eca72ca` | scalar | 0.0009475732594 | CSI of f_age: its contribution to the shift in the linear predictor |
| `csi.f_bill_mean_6m` | `a56ef25e` | scalar | 0.002369326368 | CSI of f_bill_mean_6m: its contribution to the shift in the linear predictor |
| `csi.f_bill_trend_6m` | `e6bbd7a6` | scalar | 0.006329590221 | CSI of f_bill_trend_6m: its contribution to the shift in the linear predictor |
| `csi.f_delinq_count_6m` | `5c1ddd21` | scalar | 0.002448902116 | CSI of f_delinq_count_6m: its contribution to the shift in the linear predictor |
| `csi.f_delinq_last` | `dadfe01c` | scalar | 0.02362581795 | CSI of f_delinq_last: its contribution to the shift in the linear predictor |
| `csi.f_delinq_max_6m` | `20767939` | scalar | 0.0008964784296 | CSI of f_delinq_max_6m: its contribution to the shift in the linear predictor |
| `csi.f_limit_bal` | `810ae3c7` | scalar | 0.001211461258 | CSI of f_limit_bal: its contribution to the shift in the linear predictor |
| `csi.f_pay_ratio_last` | `f337e4e5` | scalar | 0.001923767196 | CSI of f_pay_ratio_last: its contribution to the shift in the linear predictor |
| `csi.f_pay_ratio_mean_6m` | `ff31f4b4` | scalar | 0.001768345794 | CSI of f_pay_ratio_mean_6m: its contribution to the shift in the linear predictor |
| `csi.f_utilisation` | `b9d55682` | scalar | 0.004041856699 | CSI of f_utilisation: its contribution to the shift in the linear predictor |
| `csi.max` | `e56cb179` | scalar | 0.02362581795 | the largest characteristic stability index |
| `deciles.test` | `15d50c28` | table | table, 10 rows | decile separation on test; decile 1 holds the highest probabilities |
| `deciles.test.top2_capture` | `d4a1cf7d` | scalar | 0.471810089 | share of test events in the top two deciles |
| `deciles.train.top2_capture` | `1d20c762` | scalar | 0.451653944 | share of train events in the top two deciles |
| `leakage.duplicates.train` | `4474c227` | scalar | 0 | share of train rows whose feature values are not unique within train |
| `leakage.name_screen.n_matched` | `407e62be` | scalar | 0 | feature names matching the target-adjacent lexicon |
| `leakage.overlap` | `4c9fcd09` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.features` | `0fec8048` | scalar | 0 | share of test rows whose feature values also appear in train |
| `leakage.overlap.ids` | `63d37fc5` | scalar | 0 | share of test rows whose ['client_id'] also identify a row of train |
| `leakage.target_corr.max_single_feature_auc` | `fd829fc4` | scalar | 0.6831414154 | the AUC of the strongest single feature |
| `leakage.timing.n_flagged` | `742bcd24` | scalar | 0 | features declared during_period or after_outcome |
| `metrics.test.auc` | `5c6c2bfc` | scalar | 0.7479888042 | auc on test, recomputed by quaestor |
| `metrics.test.brier` | `bbe69430` | scalar | 0.148850901 | brier on test, recomputed by quaestor |
| `metrics.test.event_rate` | `9209d200` | scalar | 0.2246666667 | event_rate on test, recomputed by quaestor |
| `metrics.test.gini` | `8e5918d8` | scalar | 0.4959776083 | gini on test, recomputed by quaestor |
| `metrics.test.ks` | `90751047` | scalar | 0.4182675012 | ks on test, recomputed by quaestor |
| `metrics.test.logloss` | `dda8da69` | scalar | 0.4672914712 | logloss on test, recomputed by quaestor |
| `metrics.test.mean_predicted` | `4d2f8a37` | scalar | 0.2211048954 | mean_predicted on test, recomputed by quaestor |
| `metrics.test.n` | `64fcf14d` | scalar | 1500 | n on test, recomputed by quaestor |
| `metrics.test.sub.f_delinq_count_6m_high` | `d4fbdc76` | table | table, 10 rows | every metric on the f_delinq_count_6m above_median slice of test |
| `metrics.test.sub.f_delinq_count_6m_high.auc_gap` | `5b735235` | scalar | -0.001967336199 | how far AUC on the f_delinq_count_6m above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.f_delinq_count_6m_high.event_rate` | `d9d79704` | scalar | 0.3454545455 | event_rate on the f_delinq_count_6m above_median slice of test |
| `metrics.test.sub.f_delinq_count_6m_high.mean_predicted` | `4aa724a5` | scalar | 0.3198382924 | mean_predicted on the f_delinq_count_6m above_median slice of test |
| `metrics.test.sub.f_delinq_count_6m_high.mean_rel_gap` | `88c4873c` | scalar | 0.07415231158 | mean predicted against observed on the f_delinq_count_6m above_median slice of test, relative |
| `metrics.test.sub.f_delinq_count_6m_high.share` | `8ea39bd5` | scalar | 0.3666666667 | the share of test the f_delinq_count_6m above_median slice holds |
| `metrics.test.sub.f_utilisation_high` | `93ddb9c9` | table | table, 10 rows | every metric on the f_utilisation above_median slice of test |
| `metrics.test.sub.f_utilisation_high.auc` | `8b9b9b27` | scalar | 0.5688944099 | auc on the f_utilisation above_median slice of test |
| `metrics.test.sub.f_utilisation_high.auc_gap` | `f0689663` | scalar | 0.1790943942 | how far AUC on the f_utilisation above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.f_utilisation_high.event_rate` | `5b836e8e` | scalar | 0.2333333333 | event_rate on the f_utilisation above_median slice of test |
| `metrics.test.sub.f_utilisation_high.mean_predicted` | `c37ecc36` | scalar | 0.2286105275 | mean_predicted on the f_utilisation above_median slice of test |
| `metrics.test.sub.f_utilisation_high.mean_rel_gap` | `42b00194` | scalar | 0.02024059629 | mean predicted against observed on the f_utilisation above_median slice of test, relative |
| `metrics.test.sub.f_utilisation_high.share` | `8e769cfa` | scalar | 0.5 | the share of test the f_utilisation above_median slice holds |
| `metrics.test.sub.f_utilisation_low` | `8373aea6` | table | table, 10 rows | every metric on the f_utilisation below_median slice of test |
| `metrics.test.sub.f_utilisation_low.auc_gap` | `03dfbb51` | scalar | -0.1506002611 | how far AUC on the f_utilisation below_median slice of test falls below AUC on all of test |
| `metrics.test.sub.f_utilisation_low.event_rate` | `7a44f440` | scalar | 0.216 | event_rate on the f_utilisation below_median slice of test |
| `metrics.test.sub.f_utilisation_low.mean_predicted` | `2a5870fc` | scalar | 0.2135992633 | mean_predicted on the f_utilisation below_median slice of test |
| `metrics.test.sub.f_utilisation_low.mean_rel_gap` | `6a2eb11d` | scalar | 0.01111452166 | mean predicted against observed on the f_utilisation below_median slice of test, relative |
| `metrics.test.sub.f_utilisation_low.share` | `03601889` | scalar | 0.5 | the share of test the f_utilisation below_median slice holds |
| `metrics.train.auc` | `14b38a2b` | scalar | 0.7584356677 | auc on train, recomputed by quaestor |
| `metrics.train.brier` | `be669a99` | scalar | 0.1489149059 | brier on train, recomputed by quaestor |
| `metrics.train.event_rate` | `133a5ff8` | scalar | 0.2245714286 | event_rate on train, recomputed by quaestor |
| `metrics.train.gini` | `b4da846e` | scalar | 0.5168713353 | gini on train, recomputed by quaestor |
| `metrics.train.ks` | `ccc12729` | scalar | 0.4451397991 | ks on train, recomputed by quaestor |
| `metrics.train.logloss` | `4f02e465` | scalar | 0.4650014911 | logloss on train, recomputed by quaestor |
| `metrics.train.mean_predicted` | `605cce58` | scalar | 0.2246226934 | mean_predicted on train, recomputed by quaestor |
| `metrics.train.n` | `564683ee` | scalar | 3500 | n on train, recomputed by quaestor |
| `metrics.train.sub.f_delinq_count_6m_high` | `001f70e9` | table | table, 10 rows | every metric on the f_delinq_count_6m above_median slice of train |
| `metrics.train.sub.f_delinq_count_6m_high.auc_gap` | `066e4d48` | scalar | 0.01153989343 | how far AUC on the f_delinq_count_6m above_median slice of train falls below AUC on all of train |
| `metrics.train.sub.f_delinq_count_6m_high.event_rate` | `70daaf30` | scalar | 0.3161875946 | event_rate on the f_delinq_count_6m above_median slice of train |
| `metrics.train.sub.f_delinq_count_6m_high.mean_predicted` | `ec725b41` | scalar | 0.3177478342 | mean_predicted on the f_delinq_count_6m above_median slice of train |
| `metrics.train.sub.f_delinq_count_6m_high.mean_rel_gap` | `41f6e723` | scalar | 0.004934537744 | mean predicted against observed on the f_delinq_count_6m above_median slice of train, relative |
| `metrics.train.sub.f_delinq_count_6m_high.share` | `49900347` | scalar | 0.3777142857 | the share of train the f_delinq_count_6m above_median slice holds |
| `metrics.train.sub.f_utilisation_high` | `a1a2ba5f` | table | table, 10 rows | every metric on the f_utilisation above_median slice of train |
| `metrics.train.sub.f_utilisation_high.auc` | `22699b62` | scalar | 0.5731528724 | auc on the f_utilisation above_median slice of train |
| `metrics.train.sub.f_utilisation_high.auc_gap` | `43f1ad7f` | scalar | 0.1852827953 | how far AUC on the f_utilisation above_median slice of train falls below AUC on all of train |
| `metrics.train.sub.f_utilisation_high.event_rate` | `b34c6bc2` | scalar | 0.2245714286 | event_rate on the f_utilisation above_median slice of train |
| `metrics.train.sub.f_utilisation_high.mean_predicted` | `315b25f7` | scalar | 0.2329237961 | mean_predicted on the f_utilisation above_median slice of train |
| `metrics.train.sub.f_utilisation_high.mean_rel_gap` | `82b6fda5` | scalar | 0.03719247611 | mean predicted against observed on the f_utilisation above_median slice of train, relative |
| `metrics.train.sub.f_utilisation_high.share` | `d3d28c9a` | scalar | 0.5 | the share of train the f_utilisation above_median slice holds |
| `metrics.train.sub.f_utilisation_low` | `061af581` | table | table, 10 rows | every metric on the f_utilisation below_median slice of train |
| `metrics.train.sub.f_utilisation_low.auc_gap` | `0e0b12c1` | scalar | -0.155785382 | how far AUC on the f_utilisation below_median slice of train falls below AUC on all of train |
| `metrics.train.sub.f_utilisation_low.event_rate` | `ecfe7914` | scalar | 0.2245714286 | event_rate on the f_utilisation below_median slice of train |
| `metrics.train.sub.f_utilisation_low.mean_predicted` | `cfd48cc6` | scalar | 0.2163215908 | mean_predicted on the f_utilisation below_median slice of train |
| `metrics.train.sub.f_utilisation_low.mean_rel_gap` | `e1454a17` | scalar | 0.03673591886 | mean predicted against observed on the f_utilisation below_median slice of train, relative |
| `metrics.train.sub.f_utilisation_low.share` | `6314e9e5` | scalar | 0.5 | the share of train the f_utilisation below_median slice holds |
| `profile.test.missing.max` | `f813848d` | scalar | 0 | the largest missing fraction in test |
| `profile.test.n` | `2193cf5f` | scalar | 1500 | rows in test |
| `profile.train.missing.max` | `050a3099` | scalar | 0 | the largest missing fraction in train |
| `profile.train.n` | `2510d49d` | scalar | 3500 | rows in train |
| `psi.f_age` | `5017e61e` | scalar | 0.008124281436 | PSI of f_age between train and test |
| `psi.f_bill_mean_6m` | `c519fca2` | scalar | 0.007124196275 | PSI of f_bill_mean_6m between train and test |
| `psi.f_bill_trend_6m` | `c3f51172` | scalar | 0.009579614525 | PSI of f_bill_trend_6m between train and test |
| `psi.f_delinq_count_6m` | `6a2fba4e` | scalar | 0.002069275496 | PSI of f_delinq_count_6m between train and test |
| `psi.f_delinq_last` | `9d44627e` | scalar | 0.002849633848 | PSI of f_delinq_last between train and test |
| `psi.f_delinq_max_6m` | `05bccd03` | scalar | 0.005498249408 | PSI of f_delinq_max_6m between train and test |
| `psi.f_limit_bal` | `1932cef9` | scalar | 0.01095273358 | PSI of f_limit_bal between train and test |
| `psi.f_pay_ratio_last` | `f85ffaec` | scalar | 0.00496591109 | PSI of f_pay_ratio_last between train and test |
| `psi.f_pay_ratio_mean_6m` | `4d206390` | scalar | 0.005500252946 | PSI of f_pay_ratio_mean_6m between train and test |
| `psi.f_utilisation` | `b8b6b215` | scalar | 0.0042440485 | PSI of f_utilisation between train and test |
| `psi.max` | `381b2570` | scalar | 0.01095273358 | the largest train-to-test PSI, score included |
| `psi.y_score` | `a2885abf` | scalar | 0.007023143302 | PSI of the score between train and test |
| `rule.calibration_first_event_rate` | `42f1351e` | scalar | 0.05 | the event rate below which the report puts calibration before discrimination |
| `run.features` | `2f9cb453` | json | json | the subject's features.json |
| `run.model_summary` | `f181acb8` | json | json | the subject's model_summary.json |
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |
| `sign_check.f_age.agrees` | `ef6b0a61` | scalar | 1 | 1 when the fitted sign on f_age agrees with its univariate direction, 0 when it does not |
| `sign_check.f_bill_mean_6m.agrees` | `7144f385` | scalar | 1 | 1 when the fitted sign on f_bill_mean_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.f_bill_trend_6m.agrees` | `5a646254` | scalar | 1 | 1 when the fitted sign on f_bill_trend_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.f_delinq_count_6m.agrees` | `e78b83df` | scalar | 1 | 1 when the fitted sign on f_delinq_count_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.f_delinq_last.agrees` | `547a15bd` | scalar | 1 | 1 when the fitted sign on f_delinq_last agrees with its univariate direction, 0 when it does not |
| `sign_check.f_delinq_max_6m.agrees` | `b5785264` | scalar | 0 | 1 when the fitted sign on f_delinq_max_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.f_delinq_max_6m.coef_sign` | `b2de2a5f` | scalar | -1 | the sign of the fitted coefficient on f_delinq_max_6m |
| `sign_check.f_delinq_max_6m.univariate_direction` | `5a76c041` | scalar | 1 | the sign of f_delinq_max_6m's own single-feature AUC on train minus 0.5 |
| `sign_check.f_limit_bal.agrees` | `dc9d1c95` | scalar | 0 | 1 when the fitted sign on f_limit_bal agrees with its univariate direction, 0 when it does not |
| `sign_check.f_limit_bal.coef_sign` | `76765f24` | scalar | 1 | the sign of the fitted coefficient on f_limit_bal |
| `sign_check.f_limit_bal.univariate_direction` | `8cc36ad2` | scalar | -1 | the sign of f_limit_bal's own single-feature AUC on train minus 0.5 |
| `sign_check.f_pay_ratio_last.agrees` | `847710b6` | scalar | 0 | 1 when the fitted sign on f_pay_ratio_last agrees with its univariate direction, 0 when it does not |
| `sign_check.f_pay_ratio_last.coef_sign` | `8b49eed8` | scalar | 1 | the sign of the fitted coefficient on f_pay_ratio_last |
| `sign_check.f_pay_ratio_last.univariate_direction` | `c9abae5e` | scalar | -1 | the sign of f_pay_ratio_last's own single-feature AUC on train minus 0.5 |
| `sign_check.f_pay_ratio_mean_6m.agrees` | `e5f0e61f` | scalar | 1 | 1 when the fitted sign on f_pay_ratio_mean_6m agrees with its univariate direction, 0 when it does not |
| `sign_check.f_utilisation.agrees` | `b45fb558` | scalar | 1 | 1 when the fitted sign on f_utilisation agrees with its univariate direction, 0 when it does not |
| `sign_check.n_disagreements` | `e223cd4a` | scalar | 3 | retained features whose fitted sign contradicts their univariate direction, of 10 checked |
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
| `thresholds.evaluation` | `bc507a88` | table | table, 5 rows | every threshold package.yaml declares, with its bound, the recomputed value and the outcome |
| `vif.f_age` | `561dd3fe` | scalar | 1.001957997 | variance inflation factor of f_age on train |
| `vif.f_bill_mean_6m` | `7b32e2ef` | scalar | 7.295299885 | variance inflation factor of f_bill_mean_6m on train |
| `vif.f_bill_trend_6m` | `c2d88735` | scalar | 1.201449441 | variance inflation factor of f_bill_trend_6m on train |
| `vif.f_delinq_count_6m` | `15bac45f` | scalar | 2.561484187 | variance inflation factor of f_delinq_count_6m on train |
| `vif.f_delinq_last` | `be34e000` | scalar | 1.411555667 | variance inflation factor of f_delinq_last on train |
| `vif.f_delinq_max_6m` | `e4b87600` | scalar | 2.40773 | variance inflation factor of f_delinq_max_6m on train |
| `vif.f_limit_bal` | `99b238f2` | scalar | 4.803401129 | variance inflation factor of f_limit_bal on train |
| `vif.f_pay_ratio_last` | `5f2b9e12` | scalar | 7.264342098 | variance inflation factor of f_pay_ratio_last on train |
| `vif.f_pay_ratio_mean_6m` | `bf28797b` | scalar | 7.25926398 | variance inflation factor of f_pay_ratio_mean_6m on train |
| `vif.f_utilisation` | `da156a12` | scalar | 3.215148369 | variance inflation factor of f_utilisation on train |
| `vif.max` | `9ae7c45b` | scalar | 7.295299885 | the largest variance inflation factor |

## Appendix C — Run trace summary

| quantity | value |
|---|---|
| tool calls | 17 (run_model 1, profile_data 1, compute_metrics 4, check_leakage 1, check_collinearity 1, challenger_compare 2, retrieve_guidance 7) |
| plan steps (bounded loop) | 4 |
| LLM calls | 19 (plan 4, draft 7, reask 1, extract 7) |
| re-asks | 1 |
| repair rounds | 0 |
| tokens in / out | 242,581 / 98,659 |
| notional cost (USD) | 4.9393 |
| wall-clock (s) | 1068.66 |
| subject run (s) | 1.15 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | credit_default-full_agent-20260919T034749Z-e2e51e00 |

## Appendix D — Not checked

| item | reason |
|---|---|
| `check_stability` (R1) | package declares no `regime.column` |
| `run_scenarios` (X1) | not applicable to `binary_classification` |
| out-of-time and vintage-holdout metrics (O1, second rule) | package declares neither split |
| developer claims (T1, claim channel) | The package declares 2 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
