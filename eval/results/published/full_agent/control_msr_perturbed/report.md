---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: msr_prepayment
version: "1.0"
model_type: discrete_time_hazard
configuration: full_agent
model: claude-opus-5[1m]
run_id: msr_prepayment-full_agent-20260920T005827Z-e61d346a
data_mode: synthetic
synthetic_n: 2000
grounding_precision_pre: 0.9971
grounding_precision_post: 1.0000
n_claims: 349
n_findings_by_severity: {high: 0, medium: 0, low: 0, info: 0}
generated: "2026-09-20T00:58:27Z"
illustrative: false
---

# Validation report — `msr_prepayment` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `msr_prepayment` v1.0 | `full_agent` | claude-opus-5[1m] | synthetic, n = 2000 | 0.9971 → 1.0000 | 0 / 0 / 0 / 0 |
<!-- quaestor:renderer:end -->

The subject of this report is the model package msr_prepayment version 1.0, a scoring model that predicts the probability that a loan prepays, and this report follows the structure of the Federal Reserve's model risk management guidance on model validation and monitoring [[reg:SR26-2:V]].
The subject was executed by the validation harness, which scored each split and recomputed every metric below from those outputs rather than carrying the developer's reported values forward, within the wall-clock cap of 300 [[art:2ad8d1a5:runtime.max_seconds]] seconds the package declares.
The development split holds 36013 [[art:6fdfeabb:metrics.train.n]] rows and the held-out test split holds 15382 [[art:e55953e1:metrics.test.n]] rows.
The out-of-time split holds 12257 [[art:7898809e:metrics.out_of_time.n]] rows and the vintage holdout split holds 32177 [[art:37a92951:metrics.vintage_holdout.n]] rows.

The model passes each developer-declared threshold evaluated in this section.
Discrimination on test is 0.7753 [[art:57066271:metrics.test.auc]], above the declared floor of 0.65 [[art:fececac1:threshold.package.auc.test.min]].
The calibration slope on test is 0.9365 [[art:3e42ee62:calibration_slope.test]], inside the declared band running from 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] to 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The largest train-to-test population stability index, the score included, is 0.06189 [[art:c2e8c8fd:psi.max]], below the declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].

Discrimination holds away from the split the thresholds are stated on, at 0.7846 [[art:6f2a2d99:metrics.out_of_time.auc]] out of time and 0.7718 [[art:ac6794c5:metrics.vintage_holdout.auc]] on the vintage holdout.
Calibration is nearest to a neutral slope out of time, at 0.9969 [[art:a49b2789:calibration_slope.out_of_time]], with the development split just behind it at 0.9937 [[art:534cb102:calibration_slope.train]].
The vintage holdout carries the lowest of the slopes recomputed for this section, 0.8373 [[art:08d6b321:calibration_slope.vintage_holdout]], further below the test slope than either of the other two splits, and the declared band is stated against test rather than against that split.

No finding was raised by this validation.

## 2. Conceptual soundness

Design, construction, and developmental evidence for the champion are assessed here against the expectation that key modeling choices, interpretability evidence, and benchmarking to alternative models be subjected to critical analysis [[reg:SR26-2:V.1.a]].

### Design and feature inventory

The champion is a logistic model of the monthly prepayment event, fitted with a linear index over loan- and rate-level covariates plus a four-term spline in loan age, and estimated on 36013 [[art:22858a09:run.model_summary#n_train]] loan-months drawn from 934 [[art:22858a09:run.model_summary#n_train_loans]] loans.
The feature file carries 12 [[art:0b1995f4:run.features#n]] features in total.
Of these, 5 [[art:0b1995f4:run.features#at_origination]] are known at origination and 7 [[art:0b1995f4:run.features#before_period_start]] are known before the start of the performance period.
None are dated inside the performance period, at 0 [[art:0b1995f4:run.features#during_period]], and none are dated after the outcome is observed, at 0 [[art:0b1995f4:run.features#after_outcome]].
That timing profile means every input is observable at the point the model is asked to predict, which is the design property that matters most for a monthly prepayment forecast and the one an as-of-date reconstruction would otherwise put at risk.

The developer applied a collinearity screen with a variance inflation cut-off of 10 [[art:22858a09:run.model_summary#vif_threshold]].
The screen removed f_rate_change_12m, whose variance inflation factor was 12.38 [[art:22858a09:run.model_summary#removed.f_rate_change_12m.vif]], and f_bom_balance_log, whose variance inflation factor was 40090 [[art:22858a09:run.model_summary#removed.f_bom_balance_log.vif]].
The second of those two is far the larger and is the kind of magnitude that arises when a feature is close to a linear combination of others already in the design, here plausibly of original balance and loan age; dropping it is a defensible choice, though it leaves the current balance channel represented only indirectly.
Removing the twelve-month rate change also leaves the rate environment represented through the incentive and spread-at-origination terms rather than through a direct change variable, which is a judgment the developer should continue to document as rate paths move.

### Coefficients and expected direction

The largest fitted coefficient is on the refinance incentive at 1.253 [[art:22858a09:run.model_summary#coefficients.f_incentive.value]], and its positive sign is what prepayment theory expects, since a wider gap between the note rate and the prevailing rate raises the value of refinancing.
The first loan-age spline term is the next largest at 0.6491 [[art:22858a09:run.model_summary#coefficients.loan_age_spline_1.value]], with later terms at 0.04548 [[art:22858a09:run.model_summary#coefficients.loan_age_spline_2.value]], -0.09539 [[art:22858a09:run.model_summary#coefficients.loan_age_spline_3.value]] and -0.2386 [[art:22858a09:run.model_summary#coefficients.loan_age_spline_4.value]], a pattern consistent with the usual seasoning ramp followed by a flattening at higher ages.
The credit score coefficient is 0.4074 [[art:22858a09:run.model_summary#coefficients.f_credit_score.value]], positive as expected because stronger borrowers refinance more readily.
The log original balance coefficient is 0.3036 [[art:22858a09:run.model_summary#coefficients.f_orig_upb_log.value]], again in the expected direction, as larger balances make the fixed costs of refinancing easier to recover.
Original loan-to-value enters at -0.243 [[art:22858a09:run.model_summary#coefficients.f_orig_ltv.value]], negative as expected, since thinner equity impedes a refinance.
The note rate coefficient is -0.4457 [[art:22858a09:run.model_summary#coefficients.f_note_rate.value]], which is not the direction a reader coming to the model cold would expect from note rate alone; conditional on incentive and spread-at-origination already being in the index, a negative partial effect is interpretable but rests on the collinearity structure of the design rather than on a direct economic reading.
The burnout coefficient is 0.07952 [[art:22858a09:run.model_summary#coefficients.f_burnout.value]], and the subject matter ordinarily expects burnout to dampen rather than raise prepayment response, so this term does not read in the conventional direction even though it is small.
The spread-at-origination term at 0.01282 [[art:22858a09:run.model_summary#coefficients.f_sato.value]] and the two seasonality terms at 0.0702 [[art:22858a09:run.model_summary#coefficients.f_season_sin.value]] and -0.1239 [[art:22858a09:run.model_summary#coefficients.f_season_cos.value]] are small relative to the incentive and age terms, and the intercept is -5.502 [[art:22858a09:run.model_summary#intercept]], consistent with a low base monthly hazard.

### Fitted signs against univariate direction

The sign comparison shows 1 [[art:f96ece96:sign_check.n_disagreements]] retained feature whose fitted coefficient sign contradicts the direction of its own single-feature relationship with the outcome on train.
That feature is the note rate, whose fitted coefficient sign is -1 [[art:9a57eeb9:sign_check.f_note_rate.coef_sign]] against a univariate direction of 1 [[art:33e2a051:sign_check.f_note_rate.univariate_direction]], recorded as disagreement at 0 [[art:e3173464:sign_check.f_note_rate.agrees]].
The weight the model places on that feature is measured by refitting without it, which changes test discrimination by -0.002585 [[art:034cea8e:ablation.f_note_rate.delta_auc]], so the reversal sits on a term the model uses but does not lean on heavily.
Every other checked feature agrees with its univariate direction: the incentive at 1 [[art:aab920d4:sign_check.f_incentive.agrees]], with a coefficient sign of 1 [[art:34fbc238:sign_check.f_incentive.coef_sign]] and a univariate direction of 1 [[art:284b2d7c:sign_check.f_incentive.univariate_direction]]; credit score at 1 [[art:6a693a4d:sign_check.f_credit_score.agrees]], with signs of 1 [[art:4893edbf:sign_check.f_credit_score.coef_sign]] and 1 [[art:5364f2d9:sign_check.f_credit_score.univariate_direction]]; log original balance at 1 [[art:57b59c6a:sign_check.f_orig_upb_log.agrees]], with signs of 1 [[art:5165217f:sign_check.f_orig_upb_log.coef_sign]] and 1 [[art:901ddb38:sign_check.f_orig_upb_log.univariate_direction]]; original loan-to-value at 1 [[art:56d6495e:sign_check.f_orig_ltv.agrees]], with signs of -1 [[art:eb67b95a:sign_check.f_orig_ltv.coef_sign]] and -1 [[art:1883c240:sign_check.f_orig_ltv.univariate_direction]]; spread at origination at 1 [[art:44052838:sign_check.f_sato.agrees]], with signs of 1 [[art:55450fdb:sign_check.f_sato.coef_sign]] and 1 [[art:5cc2f196:sign_check.f_sato.univariate_direction]]; burnout at 1 [[art:a7b47126:sign_check.f_burnout.agrees]], with signs of 1 [[art:434a2eb4:sign_check.f_burnout.coef_sign]] and 1 [[art:6c04f9a3:sign_check.f_burnout.univariate_direction]]; and the two seasonality terms at 1 [[art:caceebf9:sign_check.f_season_sin.agrees]] and 1 [[art:e02a4777:sign_check.f_season_cos.agrees]], with coefficient signs of 1 [[art:a6b9d22d:sign_check.f_season_sin.coef_sign]] and -1 [[art:25dfa200:sign_check.f_season_cos.coef_sign]] against univariate directions of 1 [[art:8a2dc987:sign_check.f_season_sin.univariate_direction]] and -1 [[art:7f6fd623:sign_check.f_season_cos.univariate_direction]].
The burnout agreement is worth reading carefully: the fitted sign matches the feature's own univariate direction on train, so the two are internally consistent, but both run against the conventional expectation that burnout suppresses response, which points at how the burnout measure is constructed rather than at an inconsistency between fit and data.

### Contribution of individual features

Ablation is measured from a refit of the champion's functional form on all retained features, which reaches a test AUC of 0.7673 [[art:54367df6:ablation.baseline_auc]].
Dropping the refinance incentive changes test discrimination by -0.04117 [[art:cc8b34d4:ablation.f_incentive.delta_auc]], the largest loss of any single feature and confirmation that the rate-response channel carries most of the model's discrimination.
Log original balance follows at -0.01927 [[art:dbd54a4a:ablation.f_orig_upb_log.delta_auc]] and credit score at -0.01474 [[art:302cee1d:ablation.f_credit_score.delta_auc]].
Original loan-to-value contributes -0.002294 [[art:45bbe28a:ablation.f_orig_ltv.delta_auc]], close to the note rate's contribution and well below the three leading terms.
The remaining terms move test discrimination very little: seasonality at -0.0004826 [[art:f01715f5:ablation.f_season_cos.delta_auc]] and -0.0003885 [[art:a81a1fce:ablation.f_season_sin.delta_auc]], and burnout at -0.0001876 [[art:4c92a645:ablation.f_burnout.delta_auc]].
Two features have positive deltas, meaning test discrimination was slightly higher without them: spread at origination at 0.0005201 [[art:452f8833:ablation.f_sato.delta_auc]] and loan age at 0.0008166 [[art:cd3be5c5:ablation.f_loan_age.delta_auc]].
The loan age result deserves comment because the spline is the most elaborate part of the specification and the second largest coefficient sits on its first term, yet removing it does not cost test discrimination; the seasoning shape may be substantially absorbed by the incentive and burnout terms on this sample, and the developer should be able to justify carrying four spline terms on that evidence.

### Effective challenge

The champion attains a test AUC of 0.7753 [[art:57066271:metrics.test.auc]] and a test Brier score of 0.007894 [[art:7d3583cd:metrics.test.brier]] on recomputation.
The challenger attains a test AUC of 0.7 [[art:a55c39c9:challenger.auc]] and a test Brier score of 0.008371 [[art:57c3e2f5:challenger.brier]].
On discrimination, the challenger's AUC minus the champion's is -0.07528 [[art:89de5f90:challenger.delta_auc]], so the challenger ranks worse than the champion rather than better.
On calibration error, the champion's Brier score is the lower of the two, so the two comparisons point the same way, and the ranking difference is reported here as a difference in AUC rather than as a ratio.
The declared decision rule requires the challenger to lead the champion on test AUC by 0.03 [[art:e042774c:threshold.E1.delta_auc]] before the difference is treated as material, and the observed lead is negative rather than above that level, so the challenge does not displace the champion.
A benchmark that loses on both discrimination and calibration establishes that the champion is not obviously dominated, but it is weak effective challenge: a challenger that does not approach the champion cannot probe whether the champion's functional form, and in particular the loan-age spline whose ablation delta is positive, is the right one.
Stronger challenge on this point would use an alternative specification of the age and burnout channels rather than a uniformly weaker model.

### Assessment

The design is aligned with the stated purpose, the input timing is clean, the collinearity screen is documented with its cut-off and the values that triggered it, and the leading coefficients carry the signs prepayment economics expects.
The reservations are the note rate's reversal against its own univariate direction on a term of modest ablation weight, the burnout term's direction relative to conventional expectation, the positive ablation delta on the loan-age spline, and the limited reach of the current challenger.
On the balance of developmental evidence reviewed here, the champion's conceptual design is adequate for its intended use, with the functional form of the age and burnout channels the area where further developmental evidence would do the most good.

## 3. Data integrity and drift

Sound development practice includes a critical assessment of data quality, relevance, and inputs, and this section reads the package's split profiles, stability indices, and contamination screens against the bounds the package declares [[reg:SR26-2:IV.1]].

### Split sizes and missingness

The training split holds 36013 rows [[art:c5ebd9c9:profile.train.n]], the test split holds 15382 rows [[art:e3abc1b8:profile.test.n]], the vintage holdout holds 32177 rows [[art:426e712a:profile.vintage_holdout.n]], and the out-of-time split holds 12257 rows [[art:fa39c5cf:profile.out_of_time.n]].

The largest missing fraction in the training split is 0 [[art:050a3099:profile.train.missing.max]].
The largest missing fraction in the test split is 0 [[art:f813848d:profile.test.missing.max]].
The largest missing fraction in the vintage holdout is 0 [[art:329bb430:profile.vintage_holdout.missing.max]].
The largest missing fraction in the out-of-time split is 0 [[art:4dafce11:profile.out_of_time.missing.max]].

Because no column in any of the four splits carries a missing value, the split-to-split missingness gap cannot rise above the declared allowance of 0.1 [[art:9cce25ea:threshold.D1.missing_gap]], so the missingness screen passes on every split and on the gap between them.

### Population stability

The declared population stability bound, train against test, is 0.25 [[art:278b9016:threshold.S1.psi]], and the package file declares the same maximum at 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].

The largest train-to-test index, the score included, is 0.06189 [[art:c2e8c8fd:psi.max]], which sits below that bound.

The train-to-test indices by feature are as follows.

- Credit score: 0.06189 [[art:5829d6ed:psi.f_credit_score]], the largest of the train-to-test set.
- Original loan balance in logs: 0.04817 [[art:75026ee2:psi.f_orig_upb_log]].
- Original loan-to-value: 0.03617 [[art:212acb3a:psi.f_orig_ltv]].
- Spread at origination: 0.02773 [[art:2beb335c:psi.f_sato]].
- Note rate: 0.01371 [[art:63c68948:psi.f_note_rate]].
- Burnout: 0.004614 [[art:445ec3e0:psi.f_burnout]].
- Refinance incentive: 0.0009923 [[art:8075e035:psi.f_incentive]].
- Loan age: 0.0001994 [[art:6ec631ed:psi.f_loan_age]].
- Seasonal cosine term: 1.79e-05 [[art:cb2ce435:psi.f_season_cos]].
- Seasonal sine term: 2.939e-06 [[art:44d14048:psi.f_season_sin]].

The score itself shifts by 0.001953 [[art:3b9dee2d:psi.y_score]] between train and test, far below the declared bound of 0.25 [[art:278b9016:threshold.S1.psi]].

The two remaining splits are read against the same declared bound of 0.25 [[art:278b9016:threshold.S1.psi]], noting that the bound as declared names the train-against-test comparison.

The train-to-out-of-time indices by feature are as follows.

- Burnout: 2.945 [[art:a696b6ff:psi.out_of_time.f_burnout]], above the declared bound.
- Loan age: 2.484 [[art:eec03fdd:psi.out_of_time.f_loan_age]], above the declared bound.
- Note rate: 0.6977 [[art:b0278c59:psi.out_of_time.f_note_rate]], above the declared bound.
- Refinance incentive: 0.4958 [[art:58b6089b:psi.out_of_time.f_incentive]], above the declared bound.
- Original loan balance in logs: 0.07136 [[art:fddf2a0a:psi.out_of_time.f_orig_upb_log]].
- Credit score: 0.05988 [[art:e02f8367:psi.out_of_time.f_credit_score]].
- Original loan-to-value: 0.04301 [[art:3422cd60:psi.out_of_time.f_orig_ltv]].
- Seasonal sine term: 0.02789 [[art:eb28b9bb:psi.out_of_time.f_season_sin]].
- Spread at origination: 0.01299 [[art:5090c358:psi.out_of_time.f_sato]].
- Seasonal cosine term: 0.007524 [[art:3487f524:psi.out_of_time.f_season_cos]].

The score shifts by 0.7056 [[art:2dc61374:psi.out_of_time.y_score]] between train and the out-of-time split, above the declared bound of 0.25 [[art:278b9016:threshold.S1.psi]].

The train-to-vintage-holdout indices by feature are as follows.

- Note rate: 0.6088 [[art:c1ffae38:psi.vintage_holdout.f_note_rate]], above the declared bound.
- Refinance incentive: 0.4475 [[art:81260b55:psi.vintage_holdout.f_incentive]], above the declared bound.
- Loan age: 0.07112 [[art:256aaeda:psi.vintage_holdout.f_loan_age]].
- Burnout: 0.04749 [[art:b76fb2b0:psi.vintage_holdout.f_burnout]].
- Original loan balance in logs: 0.0404 [[art:ce7dc6c5:psi.vintage_holdout.f_orig_upb_log]].
- Credit score: 0.03996 [[art:abf4e0aa:psi.vintage_holdout.f_credit_score]].
- Spread at origination: 0.02989 [[art:17126bd4:psi.vintage_holdout.f_sato]].
- Original loan-to-value: 0.02942 [[art:09f015f3:psi.vintage_holdout.f_orig_ltv]].
- Seasonal cosine term: 0.001288 [[art:5123c902:psi.vintage_holdout.f_season_cos]].
- Seasonal sine term: 0.0007309 [[art:403ec3c2:psi.vintage_holdout.f_season_sin]].

The score shifts by 0.1421 [[art:3713457e:psi.vintage_holdout.y_score]] between train and the vintage holdout, below the declared bound of 0.25 [[art:278b9016:threshold.S1.psi]].

Comparing the two out-of-sample splits feature by feature on the level of the index itself, rather than on any difference or ratio between the two levels, the out-of-time split is the more displaced of the pair on burnout at 2.945 [[art:a696b6ff:psi.out_of_time.f_burnout]] against 0.04749 [[art:b76fb2b0:psi.vintage_holdout.f_burnout]] and on loan age at 2.484 [[art:eec03fdd:psi.out_of_time.f_loan_age]] against 0.07112 [[art:256aaeda:psi.vintage_holdout.f_loan_age]], while the two sit closer together on note rate at 0.6977 [[art:b0278c59:psi.out_of_time.f_note_rate]] and 0.6088 [[art:c1ffae38:psi.vintage_holdout.f_note_rate]] and on refinance incentive at 0.4958 [[art:58b6089b:psi.out_of_time.f_incentive]] and 0.4475 [[art:81260b55:psi.vintage_holdout.f_incentive]].

The displacement is concentrated in the age-and-rate-path features on both splits, which is the pattern one would expect of a prepayment panel observed over a later rate environment, and it is the score-level shift of 0.7056 [[art:2dc61374:psi.out_of_time.y_score]] on the out-of-time split that carries this displacement through to the model output.

### Characteristic stability

The largest characteristic contribution to the shift in the linear predictor is 0.03438 [[art:54bd75b0:csi.max]], carried by original loan-to-value at 0.03438 [[art:1f963d83:csi.f_orig_ltv]].

The remaining contributions are note rate at 0.01822 [[art:06292416:csi.f_note_rate]], credit score at 0.007909 [[art:70748e80:csi.f_credit_score]], refinance incentive at 0.005804 [[art:ac5ee43b:csi.f_incentive]], original loan balance in logs at 0.002969 [[art:a10d20d5:csi.f_orig_upb_log]], spread at origination at 0.001487 [[art:ce21936e:csi.f_sato]], burnout at 0.0009851 [[art:94a1612f:csi.f_burnout]], the seasonal cosine term at 0.0004785 [[art:15fe2d99:csi.f_season_cos]], the seasonal sine term at 7.624e-05 [[art:81e8dbf0:csi.f_season_sin]], and loan age at 0 [[art:53ae3ece:csi.f_loan_age]].

The ordering of these contributions differs from the ordering of the train-to-test population indices, since a feature shifts the linear predictor in proportion to both its own displacement and the weight the model places on it.

### Leakage and contamination screens

The declared-timing screen flags 0 features [[art:742bcd24:leakage.timing.n_flagged]] as measured during the performance period or after the outcome is known, so no input is declared to be observed later than the point of prediction.

The strongest single feature reaches an area under the curve of 0.7239 [[art:1fe630dd:leakage.target_corr.max_single_feature_auc]] on its own, below the bound of 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]] that one feature may reach, so no single input stands in for the target.

The contamination screen has two arms, each read against its own bound.

On the identifier arm, the share of test rows whose loan and period keys also identify a row of train is 0 [[art:63d37fc5:leakage.overlap.ids]], below the declared bound of 0.005 [[art:9f336eaf:threshold.L2.overlap]].

On the feature-vector arm, the share of test rows whose feature values also appear in train is 0 [[art:0fec8048:leakage.overlap.features]], below the bound the rule actually applied, 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].

That applied bound is the larger of the declared overlap bound and an allowance scaled off the within-train duplicate share, on the reasoning that two different subjects writing the same discrete row is coincidence rather than contamination.

The share of train rows whose feature values are not unique within train is 0 [[art:4474c227:leakage.duplicates.train]], so the duplicate-driven allowance does not lift the applied bound above the declared one, and the two coincide here.

The row-level overlap screen likewise reports 0 [[art:4c9fcd09:leakage.overlap]].

The name screen matches 0 feature names [[art:407e62be:leakage.name_screen.n_matched]] against the target-adjacent lexicon, so no input is named in a way that suggests it encodes the outcome.

### Assessment

The data integrity screens pass: missingness is absent on every split and therefore within the declared gap of 0.1 [[art:9cce25ea:threshold.D1.missing_gap]], and all four leakage screens sit within the bounds each is read against.

Train-to-test stability is well within the declared bound, with a maximum of 0.06189 [[art:c2e8c8fd:psi.max]] against 0.25 [[art:278b9016:threshold.S1.psi]], so the test split supports out-of-sample reading of the model's performance without a stability caveat.

The two dated splits are a different matter, and the score-level shifts of 0.7056 [[art:2dc61374:psi.out_of_time.y_score]] and 0.1421 [[art:3713457e:psi.vintage_holdout.y_score]] should be carried forward when performance on those splits is interpreted, since a displaced input population bears on whether observed performance reflects the model or the sample it was scored on.

## 4. Outcomes analysis

Outcomes analysis compares model outputs with the real-world outcomes they were meant to predict, and sound practice is to review those comparisons for reasonableness and appropriateness, with further testing where warranted [[reg:SR26-2:V.1.b]].
This section reports calibration before discrimination.
The ordering follows from the declared use: package.yaml declares that this model's output is consumed as a probability and not only as a ranking, so whether the predicted probabilities mean what they say is the leading question here, whatever the event rate turns out to be.

### Calibration

The logistic recalibration slope of the outcome on the logit of the predicted probability is 0.9937 [[art:534cb102:calibration_slope.train]] on train, 0.9365 [[art:3e42ee62:calibration_slope.test]] on test, 0.9969 [[art:a49b2789:calibration_slope.out_of_time]] on the out-of-time split and 0.8373 [[art:08d6b321:calibration_slope.vintage_holdout]] on the vintage holdout.
The declared band for that slope runs from 0.8 [[art:749634ae:threshold.C1.calibration_slope.min]] to 1.2 [[art:b6672579:threshold.C1.calibration_slope.max]], and each slope above sits inside it, with the vintage holdout the nearest to the lower edge and the out-of-time split the nearest to unity.
The intercept of the same regression is -0.01454 [[art:11d7a3ca:calibration_intercept.train]] on train, -0.277 [[art:e87b5c13:calibration_intercept.test]] on test, -0.06272 [[art:fc7ece3a:calibration_intercept.out_of_time]] on the out-of-time split and -0.9028 [[art:44715143:calibration_intercept.vintage_holdout]] on the vintage holdout, so every intercept is negative and the vintage holdout is the furthest from zero.

On train, the mean predicted probability is 0.008427 [[art:a63f6555:metrics.train.mean_predicted]] against an observed rate of 0.008525 [[art:b9ef3327:metrics.train.event_rate]], a relative gap of 0.01152 [[art:e28c45a9:calibration.mean_rel_gap.train]].
On test, the mean predicted probability is 0.008116 [[art:3bc93911:metrics.test.mean_predicted]] against an observed rate of 0.008061 [[art:570cc08a:metrics.test.event_rate]], a relative gap of 0.006755 [[art:d1b269ea:calibration.mean_rel_gap.test]].
On the out-of-time split, the mean predicted probability is 0.01887 [[art:3833e0c5:metrics.out_of_time.mean_predicted]] against an observed rate of 0.01795 [[art:83ccf5c0:metrics.out_of_time.event_rate]], a relative gap of 0.05109 [[art:c599bd89:calibration.mean_rel_gap.out_of_time]].
On the vintage holdout, the mean predicted probability is 0.005647 [[art:5ae28866:metrics.vintage_holdout.mean_predicted]] against an observed rate of 0.004817 [[art:e3590a16:metrics.vintage_holdout.event_rate]], a relative gap of 0.1722 [[art:55a672c2:calibration.mean_rel_gap.vintage_holdout]].
The declared tolerance on that relative gap is 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]], and each of the relative gaps above lies below it, the vintage holdout being the largest of them and therefore the closest to the tolerance.
In every split above the mean predicted probability stands above the observed rate except on train, where it stands below.

Calibration within the test split, decile by decile of predicted probability, is set out below.

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

Actual against predicted conditional prepayment rate by period on test is set out below.

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

The mean absolute difference between actual and predicted conditional prepayment rate is 0.02658 [[art:f2c3683c:cpr.train.mae]] on train, 0.04264 [[art:ff266c97:cpr.test.mae]] on test, 0.05857 [[art:a7ecd72b:cpr.out_of_time.mae]] on the out-of-time split and 0.0289 [[art:172ebed4:cpr.vintage_holdout.mae]] on the vintage holdout, the out-of-time split being the largest of the four values and train the smallest.

### Discrimination

Recomputed discrimination and accuracy metrics by split are as follows.

| Metric | Train | Test | Out of time | Vintage holdout |
| --- | --- | --- | --- | --- |
| AUC | 0.7883 [[art:fa609ae1:metrics.train.auc]] | 0.7753 [[art:57066271:metrics.test.auc]] | 0.7846 [[art:6f2a2d99:metrics.out_of_time.auc]] | 0.7718 [[art:ac6794c5:metrics.vintage_holdout.auc]] |
| Gini | 0.5767 [[art:0b6b2058:metrics.train.gini]] | 0.5505 [[art:fe7f75d7:metrics.test.gini]] | 0.5691 [[art:890252d7:metrics.out_of_time.gini]] | 0.5436 [[art:a4a532f0:metrics.vintage_holdout.gini]] |
| KS | 0.4562 [[art:c355478b:metrics.train.ks]] | 0.4162 [[art:c569c301:metrics.test.ks]] | 0.4321 [[art:16d3e4fe:metrics.out_of_time.ks]] | 0.4516 [[art:b5b9e888:metrics.vintage_holdout.ks]] |
| Brier | 0.008317 [[art:83666c70:metrics.train.brier]] | 0.007894 [[art:7d3583cd:metrics.test.brier]] | 0.01713 [[art:40d244d4:metrics.out_of_time.brier]] | 0.004763 [[art:f3c6bdcc:metrics.vintage_holdout.brier]] |
| Log loss | 0.04408 [[art:199c7db5:metrics.train.logloss]] | 0.04263 [[art:320e4c6b:metrics.test.logloss]] | 0.07975 [[art:2b7c9b2d:metrics.out_of_time.logloss]] | 0.02811 [[art:c32e3713:metrics.vintage_holdout.logloss]] |
| Rows | 36013 [[art:6fdfeabb:metrics.train.n]] | 15382 [[art:e55953e1:metrics.test.n]] | 12257 [[art:7898809e:metrics.out_of_time.n]] | 32177 [[art:37a92951:metrics.vintage_holdout.n]] |

The declared bound on the train-to-test AUC gap is 0.08 [[art:630f28f4:threshold.O1.auc_gap]].
Test AUC of 0.7753 [[art:57066271:metrics.test.auc]] falls below train AUC of 0.7883 [[art:fa609ae1:metrics.train.auc]], and the distance between the two lies below that bound.
Rank-ordering holds up across the splits on the same reading: the share of events falling in the top two deciles of predicted probability is 0.5961 [[art:e8dd0c53:deciles.train.top2_capture]] on train, 0.5806 [[art:43c4adc5:deciles.test.top2_capture]] on test, 0.5773 [[art:df63152b:deciles.out_of_time.top2_capture]] on the out-of-time split and 0.5871 [[art:8b59f312:deciles.vintage_holdout.top2_capture]] on the vintage holdout.

Decile separation on test, with the highest predicted probabilities in the first decile, is set out below.

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

### Developer-declared thresholds

The bounds package.yaml declares, each paired with the value recomputed in this run and the outcome, are set out in the table the tool computed.

<!-- quaestor:renderer:begin table thresholds.evaluation -->
Every threshold package.yaml declares, with its bound, the recomputed value and the outcome [[art:f71ddec9:thresholds.evaluation]]:

| metric | split | bound | value | result |
|---|---|---|---|---|
| auc | test | minimum 0.65 | 0.7753 | pass |
| calibration_slope | test | minimum 0.8 | 0.9365 | pass |
| calibration_slope | test | maximum 1.2 | 0.9365 | pass |
| psi |  | maximum 0.25 | 0.06189 | pass |
<!-- quaestor:renderer:end -->

Each row pairs a declared bound with the corresponding recomputed quantity, so the table reports the same comparisons stated in prose above rather than a separate assessment.
Where a row concerns the test split's slope or its discrimination, the recomputed value is the one reported earlier in this section.

### Follow-up analyses

The bounded planning loop recomputed every metric on the sub-population `f_incentive > median(f_incentive)` within each split, because the aggregate metrics passed and a prepayment hazard model's discrimination and calibration typically degrade in the in-the-money half, which pooled AUC and Brier can mask.

<!-- quaestor:renderer:begin table metrics.train.sub.f_incentive_high -->
Every metric on the f_incentive above_median slice of train [[art:78c63acb:metrics.train.sub.f_incentive_high]]:

| metric | value |
|---|---|
| n | 18006 |
| event_rate | 0.01433 |
| auc | 0.7182 |
| gini | 0.4364 |
| ks | 0.3337 |
| brier | 0.01393 |
| logloss | 0.07032 |
| mean_predicted | 0.01412 |
| mean_rel_gap | 0.01445 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.f_incentive_high -->
Every metric on the f_incentive above_median slice of test [[art:26bcaea2:metrics.test.sub.f_incentive_high]]:

| metric | value |
|---|---|
| n | 7691 |
| event_rate | 0.01313 |
| auc | 0.7269 |
| gini | 0.4537 |
| ks | 0.37 |
| brier | 0.01281 |
| logloss | 0.06538 |
| mean_predicted | 0.01359 |
| mean_rel_gap | 0.03492 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.out_of_time.sub.f_incentive_high -->
Every metric on the f_incentive above_median slice of out_of_time [[art:e8891641:metrics.out_of_time.sub.f_incentive_high]]:

| metric | value |
|---|---|
| n | 6127 |
| event_rate | 0.02824 |
| auc | 0.7472 |
| gini | 0.4944 |
| ks | 0.3876 |
| brier | 0.0267 |
| logloss | 0.1176 |
| mean_predicted | 0.03172 |
| mean_rel_gap | 0.1235 |
| share | 0.4999 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.vintage_holdout.sub.f_incentive_high -->
Every metric on the f_incentive above_median slice of vintage_holdout [[art:95c63ecb:metrics.vintage_holdout.sub.f_incentive_high]]:

| metric | value |
|---|---|
| n | 16088 |
| event_rate | 0.007397 |
| auc | 0.753 |
| gini | 0.5061 |
| ks | 0.3841 |
| brier | 0.007298 |
| logloss | 0.04077 |
| mean_predicted | 0.009598 |
| mean_rel_gap | 0.2976 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

This slice's AUC falls below its own split's by 0.07016 [[art:4494db64:metrics.train.sub.f_incentive_high.auc_gap]] on train, by 0.0484 [[art:95828768:metrics.test.sub.f_incentive_high.auc_gap]] on test, by 0.03734 [[art:d9f9bdc9:metrics.out_of_time.sub.f_incentive_high.auc_gap]] on the out-of-time split and by 0.01875 [[art:c847bcca:metrics.vintage_holdout.sub.f_incentive_high.auc_gap]] on the vintage holdout, each of which lies below the declared bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] on how far a sub-population's AUC may fall.
The slice holds 0.5 [[art:6271ed11:metrics.train.sub.f_incentive_high.share]] of train, 0.5 [[art:694313d4:metrics.test.sub.f_incentive_high.share]] of test, 0.4999 [[art:a90b35be:metrics.out_of_time.sub.f_incentive_high.share]] of the out-of-time split and 0.5 [[art:f4a76ad4:metrics.vintage_holdout.sub.f_incentive_high.share]] of the vintage holdout, all above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] a sub-population must reach to be read at all and below the ceiling of 0.95 [[art:a928a05c:threshold.O1.slice_max_share]] at which it would be refused as the whole split.
On the level of the probabilities, mean predicted against observed on this slice gives a relative gap of 0.01445 [[art:961d0143:metrics.train.sub.f_incentive_high.mean_rel_gap]] on train, 0.03492 [[art:fd7ebc81:metrics.test.sub.f_incentive_high.mean_rel_gap]] on test and 0.1235 [[art:45ddf6b4:metrics.out_of_time.sub.f_incentive_high.mean_rel_gap]] on the out-of-time split, each below the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]], while on the vintage holdout the same relative gap is 0.2976 [[art:b3815f8c:metrics.vintage_holdout.sub.f_incentive_high.mean_rel_gap]], above that tolerance.
So on the vintage holdout the weakness in this slice is in the level of the probabilities rather than in their ordering, the ordering gap there being the smallest of the four reported above, while on the other splits neither the level nor the ordering crosses its bound.

The loop then recomputed every metric on the complementary sub-population `f_incentive <= median(f_incentive)`, so that the above-median slice could be read against its complement rather than only against the whole split.

<!-- quaestor:renderer:begin table metrics.train.sub.f_incentive_low -->
Every metric on the f_incentive below_median slice of train [[art:9bfedc02:metrics.train.sub.f_incentive_low]]:

| metric | value |
|---|---|
| n | 18007 |
| event_rate | 0.002721 |
| auc | 0.7213 |
| gini | 0.4426 |
| ks | 0.3665 |
| brier | 0.002705 |
| logloss | 0.01785 |
| mean_predicted | 0.002732 |
| mean_rel_gap | 0.003953 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.f_incentive_low -->
Every metric on the f_incentive below_median slice of test [[art:c9d117e4:metrics.test.sub.f_incentive_low]]:

| metric | value |
|---|---|
| n | 7691 |
| event_rate | 0.002991 |
| auc | 0.6824 |
| gini | 0.3649 |
| ks | 0.3145 |
| brier | 0.00298 |
| logloss | 0.01989 |
| mean_predicted | 0.002641 |
| mean_rel_gap | 0.1169 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.out_of_time.sub.f_incentive_low -->
Every metric on the f_incentive below_median slice of out_of_time [[art:3b3a801d:metrics.out_of_time.sub.f_incentive_low]]:

| metric | value |
|---|---|
| n | 6130 |
| event_rate | 0.007667 |
| auc | 0.7683 |
| gini | 0.5365 |
| ks | 0.4679 |
| brier | 0.007557 |
| logloss | 0.04189 |
| mean_predicted | 0.006015 |
| mean_rel_gap | 0.2155 |
| share | 0.5001 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.vintage_holdout.sub.f_incentive_low -->
Every metric on the f_incentive below_median slice of vintage_holdout [[art:c916cc71:metrics.vintage_holdout.sub.f_incentive_low]]:

| metric | value |
|---|---|
| n | 16089 |
| event_rate | 0.002238 |
| auc | 0.6724 |
| gini | 0.3447 |
| ks | 0.3456 |
| brier | 0.002229 |
| logloss | 0.01545 |
| mean_predicted | 0.001696 |
| mean_rel_gap | 0.2422 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

This slice's AUC falls below its own split's by 0.06703 [[art:3ec4f0fb:metrics.train.sub.f_incentive_low.auc_gap]] on train and by 0.0163 [[art:6def945c:metrics.out_of_time.sub.f_incentive_low.auc_gap]] on the out-of-time split, both below the declared bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].
On test the same shortfall is 0.09283 [[art:f89dd8d1:metrics.test.sub.f_incentive_low.auc_gap]] and on the vintage holdout it is 0.09945 [[art:94bab5c0:metrics.vintage_holdout.sub.f_incentive_low.auc_gap]], both above that bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]], and both are carried forward as questions for the model developer in the section that reports open items.
The slice holds 0.5 [[art:b323ed54:metrics.train.sub.f_incentive_low.share]] of train, 0.5 [[art:e2282cb8:metrics.test.sub.f_incentive_low.share]] of test, 0.5001 [[art:4ad39f3f:metrics.out_of_time.sub.f_incentive_low.share]] of the out-of-time split and 0.5 [[art:b86413de:metrics.vintage_holdout.sub.f_incentive_low.share]] of the vintage holdout, so on every split it is well above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] and the shortfalls above are not artefacts of a thin sub-population.
Mean predicted against observed on this slice gives a relative gap of 0.003953 [[art:ed8020c9:metrics.train.sub.f_incentive_low.mean_rel_gap]] on train, 0.1169 [[art:988b8044:metrics.test.sub.f_incentive_low.mean_rel_gap]] on test, 0.2155 [[art:970a62bf:metrics.out_of_time.sub.f_incentive_low.mean_rel_gap]] on the out-of-time split and 0.2422 [[art:2f10187b:metrics.vintage_holdout.sub.f_incentive_low.mean_rel_gap]] on the vintage holdout, each below the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
On test and on the vintage holdout, then, the level of the probabilities in this slice stays inside its tolerance while the ordering shortfall stands above its bound, so the weakness these two splits show is in the ordering rather than in the level.

The loop next recomputed every metric on the sub-population `f_credit_score <= median(f_credit_score)`, on the reasoning that the incentive halves had shown nothing on the aggregate reading and a different axis was worth testing, lower-credit borrowers being where prepayment discrimination and calibration most plausibly degrade relative to the pooled split.

<!-- quaestor:renderer:begin table metrics.train.sub.f_credit_score_low -->
Every metric on the f_credit_score below_median slice of train [[art:46ae8e9c:metrics.train.sub.f_credit_score_low]]:

| metric | value |
|---|---|
| n | 18391 |
| event_rate | 0.005981 |
| auc | 0.7741 |
| gini | 0.5482 |
| ks | 0.446 |
| brier | 0.005882 |
| logloss | 0.03346 |
| mean_predicted | 0.006177 |
| mean_rel_gap | 0.03277 |
| share | 0.5107 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.f_credit_score_low -->
Every metric on the f_credit_score below_median slice of test [[art:c9acf630:metrics.test.sub.f_credit_score_low]]:

| metric | value |
|---|---|
| n | 7791 |
| event_rate | 0.005391 |
| auc | 0.7381 |
| gini | 0.4761 |
| ks | 0.4039 |
| brier | 0.005336 |
| logloss | 0.03163 |
| mean_predicted | 0.006007 |
| mean_rel_gap | 0.1143 |
| share | 0.5065 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.out_of_time.sub.f_credit_score_low -->
Every metric on the f_credit_score below_median slice of out_of_time [[art:407fbd64:metrics.out_of_time.sub.f_credit_score_low]]:

| metric | value |
|---|---|
| n | 6191 |
| event_rate | 0.01115 |
| auc | 0.7896 |
| gini | 0.5791 |
| ks | 0.4647 |
| brier | 0.01084 |
| logloss | 0.05497 |
| mean_predicted | 0.01408 |
| mean_rel_gap | 0.2632 |
| share | 0.5051 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.vintage_holdout.sub.f_credit_score_low -->
Every metric on the f_credit_score below_median slice of vintage_holdout [[art:6a47626f:metrics.vintage_holdout.sub.f_credit_score_low]]:

| metric | value |
|---|---|
| n | 16477 |
| event_rate | 0.003156 |
| auc | 0.7519 |
| gini | 0.5038 |
| ks | 0.4442 |
| brier | 0.00314 |
| logloss | 0.02009 |
| mean_predicted | 0.004006 |
| mean_rel_gap | 0.2694 |
| share | 0.5121 |
<!-- quaestor:renderer:end -->

This slice's AUC falls below its own split's by 0.01424 [[art:c37c76fc:metrics.train.sub.f_credit_score_low.auc_gap]] on train, by 0.03718 [[art:0bd4944d:metrics.test.sub.f_credit_score_low.auc_gap]] on test and by 0.01988 [[art:1e45f493:metrics.vintage_holdout.sub.f_credit_score_low.auc_gap]] on the vintage holdout, each below the declared bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]].
On the out-of-time split the same shortfall is -0.005002 [[art:b7ff625e:metrics.out_of_time.sub.f_credit_score_low.auc_gap]], so there the slice's AUC stands above the split's own rather than below it.
The slice holds 0.5107 [[art:db111665:metrics.train.sub.f_credit_score_low.share]] of train, 0.5065 [[art:db444481:metrics.test.sub.f_credit_score_low.share]] of test, 0.5051 [[art:2a7161de:metrics.out_of_time.sub.f_credit_score_low.share]] of the out-of-time split and 0.5121 [[art:24402460:metrics.vintage_holdout.sub.f_credit_score_low.share]] of the vintage holdout, all above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].
Mean predicted against observed on this slice gives a relative gap of 0.03277 [[art:1aedaa05:metrics.train.sub.f_credit_score_low.mean_rel_gap]] on train and 0.1143 [[art:c03012ad:metrics.test.sub.f_credit_score_low.mean_rel_gap]] on test, both below the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]], but 0.2632 [[art:c16c2369:metrics.out_of_time.sub.f_credit_score_low.mean_rel_gap]] on the out-of-time split and 0.2694 [[art:4aeed415:metrics.vintage_holdout.sub.f_credit_score_low.mean_rel_gap]] on the vintage holdout, both above that tolerance.
On those two splits the ordering of this slice stays inside its bound while the level of its probabilities does not, so what the slice shows there is a level problem and not a ranking one.

Finally the loop recomputed every metric on the complementary sub-population `f_credit_score > median(f_credit_score)`, so that the below-median credit slice could be read against its complement rather than only against the whole split.

<!-- quaestor:renderer:begin table metrics.train.sub.f_credit_score_high -->
Every metric on the f_credit_score above_median slice of train [[art:c01fd0e6:metrics.train.sub.f_credit_score_high]]:

| metric | value |
|---|---|
| n | 17622 |
| event_rate | 0.01118 |
| auc | 0.7809 |
| gini | 0.5618 |
| ks | 0.4403 |
| brier | 0.01086 |
| logloss | 0.05517 |
| mean_predicted | 0.01077 |
| mean_rel_gap | 0.03625 |
| share | 0.4893 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.f_credit_score_high -->
Every metric on the f_credit_score above_median slice of test [[art:10c679a4:metrics.test.sub.f_credit_score_high]]:

| metric | value |
|---|---|
| n | 7591 |
| event_rate | 0.0108 |
| auc | 0.7795 |
| gini | 0.5591 |
| ks | 0.4366 |
| brier | 0.01052 |
| logloss | 0.05392 |
| mean_predicted | 0.01028 |
| mean_rel_gap | 0.04833 |
| share | 0.4935 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.out_of_time.sub.f_credit_score_high -->
Every metric on the f_credit_score above_median slice of out_of_time [[art:f725a00a:metrics.out_of_time.sub.f_credit_score_high]]:

| metric | value |
|---|---|
| n | 6066 |
| event_rate | 0.02489 |
| auc | 0.7621 |
| gini | 0.5241 |
| ks | 0.3948 |
| brier | 0.02355 |
| logloss | 0.105 |
| mean_predicted | 0.02375 |
| mean_rel_gap | 0.04583 |
| share | 0.4949 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.vintage_holdout.sub.f_credit_score_high -->
Every metric on the f_credit_score above_median slice of vintage_holdout [[art:a0163007:metrics.vintage_holdout.sub.f_credit_score_high]]:

| metric | value |
|---|---|
| n | 15700 |
| event_rate | 0.006561 |
| auc | 0.7631 |
| gini | 0.5262 |
| ks | 0.4218 |
| brier | 0.006467 |
| logloss | 0.03652 |
| mean_predicted | 0.007369 |
| mean_rel_gap | 0.1232 |
| share | 0.4879 |
<!-- quaestor:renderer:end -->

This slice's AUC falls below its own split's by 0.007432 [[art:bf2cbaa2:metrics.train.sub.f_credit_score_high.auc_gap]] on train, by 0.0225 [[art:61605613:metrics.out_of_time.sub.f_credit_score_high.auc_gap]] on the out-of-time split and by 0.008704 [[art:65d309d4:metrics.vintage_holdout.sub.f_credit_score_high.auc_gap]] on the vintage holdout, each below the declared bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]], while on test the shortfall is -0.00429 [[art:61fcae59:metrics.test.sub.f_credit_score_high.auc_gap]] and the slice's AUC therefore stands above the split's own.
The slice holds 0.4893 [[art:59d4af35:metrics.train.sub.f_credit_score_high.share]] of train, 0.4935 [[art:c84c6685:metrics.test.sub.f_credit_score_high.share]] of test, 0.4949 [[art:7696fcbc:metrics.out_of_time.sub.f_credit_score_high.share]] of the out-of-time split and 0.4879 [[art:73cedd3e:metrics.vintage_holdout.sub.f_credit_score_high.share]] of the vintage holdout, all above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].
Mean predicted against observed on this slice gives a relative gap of 0.03625 [[art:840702d6:metrics.train.sub.f_credit_score_high.mean_rel_gap]] on train, 0.04833 [[art:7415cfef:metrics.test.sub.f_credit_score_high.mean_rel_gap]] on test, 0.04583 [[art:5da6c245:metrics.out_of_time.sub.f_credit_score_high.mean_rel_gap]] on the out-of-time split and 0.1232 [[art:31e9c5fc:metrics.vintage_holdout.sub.f_credit_score_high.mean_rel_gap]] on the vintage holdout, each below the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].
On this side of the credit-score partition neither the level of the probabilities nor their ordering crosses its declared bound on any split.

## 5. Sensitivity and scenario analysis

This section reports the sensitivity and scenario evidence bearing on the model's design, construction and developmental testing, and on the extent and quality of that evidence [[reg:SR26-2:V.1.a]].
The extreme-shock work below follows the expectation that sensitivity analysis and stress testing be carried out over a wide range of inputs and parameter values, including extreme values, to establish where a model may become unstable [[reg:SR11-7:V.1.a]].
The exercises named for this section -- multicollinearity among the retained features, stability across the declared rate regimes, and the rate-shock grid -- all apply to a hazard model of this kind and all are reported here; Appendix D carries the checks set aside as inapplicable to this model type, and nothing listed there is described in this section as though it had been run.

### Multicollinearity among the retained features

The largest variance inflation factor among the retained features is 4.976 [[art:f9e0db60:vif.max]], below the tolerance of 10 [[art:aeb4f33c:threshold.M1.vif]].
That maximum is carried by the note-rate feature at 4.976 [[art:f6dfe789:vif.f_note_rate]], with the burnout feature next at 3.439 [[art:3f7564f6:vif.f_burnout]] and the loan-age feature after it at 2.929 [[art:903503b0:vif.f_loan_age]].
The refinance-incentive feature stands at 2.226 [[art:31179b0a:vif.f_incentive]] and the spread-at-origination feature at 1.713 [[art:9a173f4f:vif.f_sato]], while the remaining retained features sit close to the no-inflation floor: the cosine seasonality term at 1.018 [[art:77f16218:vif.f_season_cos]], the credit-score feature at 1.008 [[art:59d19ea1:vif.f_credit_score]], the log original balance at 1.006 [[art:8b0886fe:vif.f_orig_upb_log]], the original loan-to-value feature at 1.005 [[art:d0eadaeb:vif.f_orig_ltv]] and the sine seasonality term at 1.004 [[art:3d38c119:vif.f_season_sin]].
Belsley's condition number of the column-standardised design is 4.943 [[art:4f06a3c5:condition_number]], well below the tolerance of 30 [[art:7e52fd7a:threshold.M1.condition_number]].
On both the per-feature and the whole-design measure, then, the retained design shows no collinearity of the degree the declared tolerances are set to catch, and the coefficient-level inferences relied on elsewhere in this report are not undermined by inflated standard errors from that source.

### Stability across the declared rate regimes

The model package declares a regime column, so discrimination was measured within each regime separately.

<!-- quaestor:renderer:begin table stability.auc_by_regime -->
The champion's AUC within each rate_regime on train [[art:960f708f:stability.auc_by_regime]]:

| regime | n | event_rate | auc |
|---|---|---|---|
| falling | 17873 | 0.01438 | 0.7227 |
| rising | 18140 | 0.002756 | 0.7238 |
<!-- quaestor:renderer:end -->

The declared tolerance on the difference in AUC across regimes is 0.1 [[art:b64213d7:threshold.R1.auc_gap]], and the per-regime values in the table above are to be read against that tolerance.
Coefficient stability was assessed by a sign-flip test, which registers only where a top-ranked feature changes sign across regimes with a coefficient magnitude above 0.05 [[art:aca84377:threshold.R1.sign_flip_coef]] and an absolute z-statistic of at least 2 [[art:2e4428c7:threshold.R1.sign_flip_z]] in each regime.
The test registers at 0 for the refinance-incentive feature [[art:1e3dbc9b:stability.f_incentive.sign_flip]], at 0 for the note-rate feature [[art:4a9e3c32:stability.f_note_rate.sign_flip]], at 0 for the burnout feature [[art:ffc296b7:stability.f_burnout.sign_flip]], at 0 for the loan-age feature [[art:02339bed:stability.f_loan_age.sign_flip]] and at 0 for the spread-at-origination feature [[art:a7092419:stability.f_sato.sign_flip]].
It likewise registers at 0 for the credit-score feature [[art:453c8949:stability.f_credit_score.sign_flip]], at 0 for the original loan-to-value feature [[art:bb5e04ca:stability.f_orig_ltv.sign_flip]], at 0 for the log original balance [[art:5a5daefb:stability.f_orig_upb_log.sign_flip]], at 0 for the sine seasonality term [[art:3c609ed8:stability.f_season_sin.sign_flip]] and at 0 for the cosine seasonality term [[art:4c9ae175:stability.f_season_cos.sign_flip]].
No retained feature therefore reverses direction between regimes at a magnitude and significance that both clear the declared screen, which is evidence that the estimated response to the drivers keeps its sign as the rate environment changes.

### Rate-shock scenarios

The subject is a prepayment hazard model feeding a servicing valuation, so the scenario grid applies rate shocks in both directions and reports servicing value, its change from the base case and first-year prepayment speed at each shock.

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

At the extreme downward shock the change in servicing value is -1298000 [[art:4829926e:scenario.value_change.-300]], and at the extreme upward shock it is 168100 [[art:38e75872:scenario.value_change.300]].
The fall at the downward extreme is far larger in magnitude than the rise at the upward extreme, which is the asymmetry expected of a servicing asset whose prepayment speeds accelerate as rates decline.
Across the grid the change in value increases without reversal as the shock moves upward, from -1298000 [[art:4829926e:scenario.value_change.-300]] through -854300 [[art:03816874:scenario.value_change.-200]] and -322600 [[art:d33e8e3c:scenario.value_change.-100]] to 0 at the base case [[art:1e1b0b88:scenario.value_change.0]], then on through 119600 [[art:d0970bd9:scenario.value_change.100]] and 157000 [[art:d69c2be1:scenario.value_change.200]] to 168100 [[art:38e75872:scenario.value_change.300]].
The response curve is therefore monotone in the shock, with no local reversal that would suggest an unstable or non-smooth valuation response.
The increments are not symmetric about the base case: each further step downward subtracts more than the step before it, while each further step upward adds less than the step before it, so the curve flattens on the upside and steepens on the downside.
The convexity measure, the change at the extreme downward shock added to the change at the extreme upward shock, is -1130000 [[art:538e0e09:scenario.convexity]], negative because the fall at the downward extreme outweighs the rise at the upward extreme.
Read against the direction the package declares for this valuation, negative convexity, the sign of the measured response agrees with the declared direction, and its magnitude confirms that the asymmetry is economically material rather than a rounding artefact of the grid.

### Assessment

The sensitivity evidence in this section is consistent with a stable design: collinearity sits below both declared tolerances, coefficient signs hold across regimes, and the valuation response to rate shocks is monotone and negatively convex in the declared direction.
Nothing in this section is raised as a finding.

## 6. Findings and recommendations

Findings are ordered by severity and each carries the recomputed artifact evidence on which the defect rests, in keeping with the expectation that sound validation identifies model limitations and errors and clarifies whether corrective actions may be warranted [[reg:SR26-2:V]].

This validation raised no finding.

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1, S1), `compute_metrics` (T1, C1, O1), `check_leakage` (L1, L2), `check_stability` (R1), `check_collinearity` (M1), `challenger_compare` (E1), `run_scenarios` (X1).

### Open items

On the test split, the sub-population defined by `f_incentive <= median(f_incentive)` ranks at an AUC of 0.6824 [[art:1966c5b1:metrics.test.sub.f_incentive_low.auc]], which falls 0.09283 [[art:f89dd8d1:metrics.test.sub.f_incentive_low.auc_gap]] below the split's own 0.7753 [[art:57066271:metrics.test.auc]] and therefore above the 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] bound it was read against, on a sub-population holding 0.5 [[art:e2282cb8:metrics.test.sub.f_incentive_low.share]] of the split and so at or above the 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] share bound — selecting on that feature also selects on whatever is correlated with it, so can the model developer say which signal the model is still discriminating on inside that segment?

On the vintage_holdout split, the same sub-population defined by `f_incentive <= median(f_incentive)` ranks at an AUC of 0.6724 [[art:fa61514e:metrics.vintage_holdout.sub.f_incentive_low.auc]], which falls 0.09945 [[art:94bab5c0:metrics.vintage_holdout.sub.f_incentive_low.auc_gap]] below the split's own 0.7718 [[art:ac6794c5:metrics.vintage_holdout.auc]] and therefore above the 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] bound it was read against, on a sub-population holding 0.5 [[art:b86413de:metrics.vintage_holdout.sub.f_incentive_low.share]] of the split and so at or above the 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]] share bound — can the model developer account for what the model separates on within that segment on a later vintage, and whether the ranking it retains there is one the intended use relies on?

The fitted coefficient on `f_note_rate` carries sign -1 [[art:9a57eeb9:sign_check.f_note_rate.coef_sign]] where that feature's own univariate direction, the quantity this observation was read against, is 1 [[art:33e2a051:sign_check.f_note_rate.univariate_direction]], leaving the agreement indicator at 0 [[art:e3173464:sign_check.f_note_rate.agrees]] — conditioning on that feature also conditions on everything correlated with it, so can the model developer explain what the fitted sign is absorbing in the presence of the other features and whether that reversal is intended behavior?

## 7. Ongoing monitoring recommendations

Ongoing monitoring evaluates the extent to which this model continues to perform as expected given potential changes in products, exposures, activities, clients, data relevance, or market conditions, and the frequency and scope of monitoring reports depend on the nature of the model, the availability of new data, and model materiality [[reg:SR26-2:V.2]].
The recommendations below re-use the bounds already declared in the model package and checked in this validation, so that a production reading of each quantity is judged against the same edge the development reading was judged against.
Nothing in this section is raised as a finding; these are forward-looking recommendations for the monitoring plan.

### Quantities, cadence, and bounds

Calibration should be tracked first: on each production vintage with realized outcomes, refit the logistic regression of the realized outcome on the logit of the predicted probability and report the slope against the declared band running from 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] to 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The validation reading of that slope on held-out test data, 0.9365 [[art:3e42ee62:calibration_slope.test]], sits inside that band and is the reference point against which production drift in either direction should be read.
Because prepayment outcomes for a servicing portfolio resolve on a monthly remittance cycle, the slope can be recomputed monthly on a rolling window and reported formally each quarter, with the rolling window long enough that the estimate is not dominated by a single month's seasonality.
Discrimination should be tracked next: report the area under the ROC curve on each production vintage against the declared floor of 0.65 [[art:fececac1:threshold.package.auc.test.min]], with the validation reading of 0.7753 [[art:57066271:metrics.test.auc]] as the reference point, on the same quarterly reporting cadence.
Input and score stability should be tracked monthly, because it does not require realized outcomes and is therefore the earliest warning available: compute the population stability index for each model input and for the score itself, production vintage against the development sample, against the declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
The largest train-to-test stability reading in this validation, 0.06189 [[art:c2e8c8fd:psi.max]], lies below that ceiling, and the monitoring plan should treat sustained movement of the production reading toward the ceiling as a trigger for investigation rather than waiting for the ceiling itself to be crossed.
Where a monitored quantity falls outside its declared bound, or drifts persistently within it, the plan should route the result to a documented decision on overlays, adjustment, recalibration, or redevelopment rather than to a footnote [[reg:SR26-2:V.1.b]].

### Ordering of the monitoring report

The monitoring report should present calibration before discrimination, as this report did, because the model package declares that the output of this model is consumed as a probability and not only as a ranking.
A score that continues to rank loans correctly while drifting away from the declared slope band remains usable for ordering and unusable for the valuation arithmetic it feeds, so the ordering of the evidence should match the order in which the use of the output can break.

### Benchmarking, which monitoring adds

A challenger was compared with the champion in this validation and the comparison is reported earlier in this report, so benchmarking against an alternative model is already part of the validation record rather than a gap in it.
What monitoring adds is the comparison the development data cannot give: the challenger refitted on production vintages, so that the champion is measured against an alternative estimated on the same regime it is now being asked to predict, not against one estimated on the development sample.
Discrepancies between the champion and the refitted challenger should trigger investigation into the sources and degree of the difference rather than an automatic switch, since the challenger is an alternative prediction and the difference may reflect its data or method [[reg:SR11-7:V.1.b]].

### What this validation could not cover

The performance evidence in this report rests on a holdout drawn from the development sample, which is an analysis of fit outside the estimation data but not a back-test over a later period, and monitoring is where the back-test over production vintages accumulates [[reg:SR11-7:V.1.c]].
The stability evidence in this report compares the training sample with the test sample, so it characterizes the development data and cannot speak to how production populations will move away from it; only the production readings of the stability index can do that.
This validation examined the model as packaged and not as implemented in the production servicing systems, so monitoring should carry process verification: that input feeds remain accurate, complete, and consistent with the model's purpose, and that the deployed code is under change control with all changes logged and auditable [[reg:SR11-7:V.1.b]].
Prepayment behavior is conditioned on an interest-rate and refinancing environment that the development sample observed over a particular stretch of history, and monitoring should record when production conditions approach or move outside the range of input values the model was estimated on [[reg:SR11-7:V.1.b]].
Where users ignore, alter, or reverse the model output, the overrides should be logged, their reasons evaluated, and their performance tracked, since a high override rate or an override process that consistently improves on the model is evidence that the model needs revision [[reg:SR11-7:V.1.b]].
Any extension of the model beyond the use declared in the model package, including use of the output in a way that depends on properties this validation did not test, should be treated as a change of scope and routed back to validation rather than absorbed into monitoring [[reg:SR26-2:V]].
Finally, monitoring should periodically revisit the model limitations recorded at the development stage and in this report, since limitations that are tolerable at one portfolio composition can become material at another [[reg:SR26-2:V.2]].

## Appendix A — Claims

Grounding precision 0.9971 before repair (349 of 350 claims verified; 1 unsupported) and 1.0000 after 0 claim(s) rewritten and 1 number(s) removed from the prose. Per section (post-repair): summary 17/17; conceptual_soundness 69/69; data_integrity 84/84; outcomes 120/120; sensitivity 37/37; findings 15/15; monitoring 7/7.

Developer claims: The package declares 3 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). See Appendix D.

Excluded numeric tokens (not claims): citation_hash (2ad8d1a5, 6fdfeabb, e55953e1, 7898809e); regulatory_section_id (SR26-2:V, SR26-2:V.1.a, SR26-2:IV.1, SR26-2:V.1.b); package_version (1.0); extractor_returned_excluded_token (1.0, 12.0, 2.0, 3.0).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The subject was executed by the validation harness, which sc… | 300 | ratio | runtime.max_seconds |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 2 | summary | The development split holds 36013 rows and the held-out test… | 36013 | count | n | train | eq | `[[art:6fdfeabb:metrics.train.n]]` | verified | 36013 |
| 3 | summary | The development split holds 36013 rows and the held-out test… | 15382 | count | n | test | eq | `[[art:e55953e1:metrics.test.n]]` | verified | 15382 |
| 4 | summary | The out-of-time split holds 12257 rows and the vintage holdo… | 12257 | count | n | out_of_time | eq | `[[art:7898809e:metrics.out_of_time.n]]` | verified | 12257 |
| 5 | summary | The out-of-time split holds 12257 rows and the vintage holdo… | 32177 | count | n | vintage_holdout | eq | `[[art:37a92951:metrics.vintage_holdout.n]]` | verified | 32177 |
| 6 | summary | Discrimination on test is 0.7753 , above the declared floor… | 0.7753 | ratio | auc | test | eq | `[[art:57066271:metrics.test.auc]]` | verified | 0.7752553922 |
| 7 | summary | Discrimination on test is 0.7753 , above the declared floor… | 0.65 | ratio | auc | test | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 8 | summary | The calibration slope on test is 0.9365 , inside the declare… | 0.9365 | ratio | calibration_slope | test | eq | `[[art:3e42ee62:calibration_slope.test]]` | verified | 0.9365180494 |
| 9 | summary | The calibration slope on test is 0.9365 , inside the declare… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 10 | summary | The calibration slope on test is 0.9365 , inside the declare… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 11 | summary | The largest train-to-test population stability index, the sc… | 0.06189 | ratio | psi |  | eq | `[[art:c2e8c8fd:psi.max]]` | verified | 0.06188985797 |
| 12 | summary | The largest train-to-test population stability index, the sc… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 13 | summary | Discrimination holds away from the split the thresholds are… | 0.7846 | ratio | auc | out_of_time | eq | `[[art:6f2a2d99:metrics.out_of_time.auc]]` | verified | 0.7845616168 |
| 14 | summary | Discrimination holds away from the split the thresholds are… | 0.7718 | ratio | auc | vintage_holdout | eq | `[[art:ac6794c5:metrics.vintage_holdout.auc]]` | verified | 0.7717974135 |
| 15 | summary | Calibration is nearest to a neutral slope out of time, at 0.… | 0.9969 | ratio | calibration_slope | out_of_time | eq | `[[art:a49b2789:calibration_slope.out_of_time]]` | verified | 0.9969389246 |
| 16 | summary | Calibration is nearest to a neutral slope out of time, at 0.… | 0.9937 | ratio | calibration_slope | train | eq | `[[art:534cb102:calibration_slope.train]]` | verified | 0.9936945557 |
| 17 | summary | The vintage holdout carries the lowest of the slopes recompu… | 0.8373 | ratio | calibration_slope | vintage_holdout | eq | `[[art:08d6b321:calibration_slope.vintage_holdout]]` | verified | 0.837279841 |
| 18 | conceptual_soundness | The champion is a logistic model of the monthly prepayment e… | 36013 | count | n_train | train | eq | `[[art:22858a09:run.model_summary#n_train]]` | verified | 36013 |
| 19 | conceptual_soundness | The champion is a logistic model of the monthly prepayment e… | 934 | count | n_train_loans | train | eq | `[[art:22858a09:run.model_summary#n_train_loans]]` | verified | 934 |
| 20 | conceptual_soundness | The feature file carries 12 features in total. | 12 | count | n |  | eq | `[[art:0b1995f4:run.features#n]]` | verified | 12 |
| 21 | conceptual_soundness | Of these, 5 are known at origination and 7 are known before… | 5 | count | at_origination |  | eq | `[[art:0b1995f4:run.features#at_origination]]` | verified | 5 |
| 22 | conceptual_soundness | Of these, 5 are known at origination and 7 are known before… | 7 | count | before_period_start |  | eq | `[[art:0b1995f4:run.features#before_period_start]]` | verified | 7 |
| 23 | conceptual_soundness | None are dated inside the performance period, at 0 , and non… | 0 | count | during_period |  | eq | `[[art:0b1995f4:run.features#during_period]]` | verified | 0 |
| 24 | conceptual_soundness | None are dated inside the performance period, at 0 , and non… | 0 | count | after_outcome |  | eq | `[[art:0b1995f4:run.features#after_outcome]]` | verified | 0 |
| 25 | conceptual_soundness | The developer applied a collinearity screen with a variance… | 10 | ratio | vif_threshold |  | eq | `[[art:22858a09:run.model_summary#vif_threshold]]` | verified | 10 |
| 26 | conceptual_soundness | The screen removed f_rate_change_12m, whose variance inflati… | 12.38 | ratio | vif |  | eq | `[[art:22858a09:run.model_summary#removed.f_rate_change_12m.vif]]` | verified | 12.377209 |
| 27 | conceptual_soundness | The screen removed f_rate_change_12m, whose variance inflati… | 40090 | ratio | vif |  | eq | `[[art:22858a09:run.model_summary#removed.f_bom_balance_log.vif]]` | verified | 40090.39108 |
| 28 | conceptual_soundness | The largest fitted coefficient is on the refinance incentive… | 1.253 | ratio | coefficient |  | eq | `[[art:22858a09:run.model_summary#coefficients.f_incentive.value]]` | verified | 1.253400948 |
| 29 | conceptual_soundness | The first loan-age spline term is the next largest at 0.6491… | 0.6491 | ratio | coefficient |  | eq | `[[art:22858a09:run.model_summary#coefficients.loan_age_spline_1.value]]` | verified | 0.6491385114 |
| 30 | conceptual_soundness | The first loan-age spline term is the next largest at 0.6491… | 0.04548 | ratio | coefficient |  | eq | `[[art:22858a09:run.model_summary#coefficients.loan_age_spline_2.value]]` | verified | 0.04547611044 |
| 31 | conceptual_soundness | The first loan-age spline term is the next largest at 0.6491… | -0.09539 | ratio | coefficient |  | eq | `[[art:22858a09:run.model_summary#coefficients.loan_age_spline_3.value]]` | verified | -0.09538696407 |
| 32 | conceptual_soundness | The first loan-age spline term is the next largest at 0.6491… | -0.2386 | ratio | coefficient |  | eq | `[[art:22858a09:run.model_summary#coefficients.loan_age_spline_4.value]]` | verified | -0.2385660288 |
| 33 | conceptual_soundness | The credit score coefficient is 0.4074 , positive as expecte… | 0.4074 | ratio | coefficient |  | eq | `[[art:22858a09:run.model_summary#coefficients.f_credit_score.value]]` | verified | 0.4073637042 |
| 34 | conceptual_soundness | The log original balance coefficient is 0.3036 , again in th… | 0.3036 | ratio | coefficient |  | eq | `[[art:22858a09:run.model_summary#coefficients.f_orig_upb_log.value]]` | verified | 0.3036365647 |
| 35 | conceptual_soundness | Original loan-to-value enters at -0.243 , negative as expect… | -0.243 | ratio | coefficient |  | eq | `[[art:22858a09:run.model_summary#coefficients.f_orig_ltv.value]]` | verified | -0.2430424725 |
| 36 | conceptual_soundness | The note rate coefficient is -0.4457 , which is not the dire… | -0.4457 | ratio | coefficient |  | eq | `[[art:22858a09:run.model_summary#coefficients.f_note_rate.value]]` | verified | -0.4457241706 |
| 37 | conceptual_soundness | The burnout coefficient is 0.07952 , and the subject matter… | 0.07952 | ratio | coefficient |  | eq | `[[art:22858a09:run.model_summary#coefficients.f_burnout.value]]` | verified | 0.07951968723 |
| 38 | conceptual_soundness | The spread-at-origination term at 0.01282 and the two season… | 0.01282 | ratio | coefficient |  | eq | `[[art:22858a09:run.model_summary#coefficients.f_sato.value]]` | verified | 0.01281978784 |
| 39 | conceptual_soundness | The spread-at-origination term at 0.01282 and the two season… | 0.0702 | ratio | coefficient |  | eq | `[[art:22858a09:run.model_summary#coefficients.f_season_sin.value]]` | verified | 0.07019923172 |
| 40 | conceptual_soundness | The spread-at-origination term at 0.01282 and the two season… | -0.1239 | ratio | coefficient |  | eq | `[[art:22858a09:run.model_summary#coefficients.f_season_cos.value]]` | verified | -0.1238708376 |
| 41 | conceptual_soundness | The spread-at-origination term at 0.01282 and the two season… | -5.502 | ratio | intercept |  | eq | `[[art:22858a09:run.model_summary#intercept]]` | verified | -5.502203635 |
| 42 | conceptual_soundness | The sign comparison shows 1 retained feature whose fitted co… | 1 | count | n_disagreements | train | eq | `[[art:f96ece96:sign_check.n_disagreements]]` | verified | 1 |
| 43 | conceptual_soundness | That feature is the note rate, whose fitted coefficient sign… | -1 | ratio | coef_sign |  | eq | `[[art:9a57eeb9:sign_check.f_note_rate.coef_sign]]` | verified | -1 |
| 44 | conceptual_soundness | That feature is the note rate, whose fitted coefficient sign… | 1 | ratio | univariate_direction |  | eq | `[[art:33e2a051:sign_check.f_note_rate.univariate_direction]]` | verified | 1 |
| 45 | conceptual_soundness | That feature is the note rate, whose fitted coefficient sign… | 0 | ratio | agrees |  | eq | `[[art:e3173464:sign_check.f_note_rate.agrees]]` | verified | 0 |
| 46 | conceptual_soundness | The weight the model places on that feature is measured by r… | -0.002585 | ratio | delta_auc | test | eq | `[[art:034cea8e:ablation.f_note_rate.delta_auc]]` | verified | -0.002585106068 |
| 47 | conceptual_soundness | Every other checked feature agrees with its univariate direc… | 1 | ratio | agrees |  | eq | `[[art:aab920d4:sign_check.f_incentive.agrees]]` | verified | 1 |
| 48 | conceptual_soundness | Every other checked feature agrees with its univariate direc… | 1 | ratio | coef_sign |  | eq | `[[art:34fbc238:sign_check.f_incentive.coef_sign]]` | verified | 1 |
| 49 | conceptual_soundness | Every other checked feature agrees with its univariate direc… | 1 | ratio | univariate_direction |  | eq | `[[art:284b2d7c:sign_check.f_incentive.univariate_direction]]` | verified | 1 |
| 50 | conceptual_soundness | Every other checked feature agrees with its univariate direc… | 1 | ratio | agrees |  | eq | `[[art:6a693a4d:sign_check.f_credit_score.agrees]]` | verified | 1 |
| 51 | conceptual_soundness | Every other checked feature agrees with its univariate direc… | 1 | ratio | coef_sign |  | eq | `[[art:4893edbf:sign_check.f_credit_score.coef_sign]]` | verified | 1 |
| 52 | conceptual_soundness | Every other checked feature agrees with its univariate direc… | 1 | ratio | univariate_direction |  | eq | `[[art:5364f2d9:sign_check.f_credit_score.univariate_direction]]` | verified | 1 |
| 53 | conceptual_soundness | Every other checked feature agrees with its univariate direc… | 1 | ratio | agrees |  | eq | `[[art:57b59c6a:sign_check.f_orig_upb_log.agrees]]` | verified | 1 |
| 54 | conceptual_soundness | Every other checked feature agrees with its univariate direc… | 1 | ratio | coef_sign |  | eq | `[[art:5165217f:sign_check.f_orig_upb_log.coef_sign]]` | verified | 1 |
| 55 | conceptual_soundness | Every other checked feature agrees with its univariate direc… | 1 | ratio | univariate_direction |  | eq | `[[art:901ddb38:sign_check.f_orig_upb_log.univariate_direction]]` | verified | 1 |
| 56 | conceptual_soundness | Every other checked feature agrees with its univariate direc… | 1 | ratio | agrees |  | eq | `[[art:56d6495e:sign_check.f_orig_ltv.agrees]]` | verified | 1 |
| 57 | conceptual_soundness | Every other checked feature agrees with its univariate direc… | -1 | ratio | coef_sign |  | eq | `[[art:eb67b95a:sign_check.f_orig_ltv.coef_sign]]` | verified | -1 |
| 58 | conceptual_soundness | Every other checked feature agrees with its univariate direc… | -1 | ratio | univariate_direction |  | eq | `[[art:1883c240:sign_check.f_orig_ltv.univariate_direction]]` | verified | -1 |
| 59 | conceptual_soundness | Every other checked feature agrees with its univariate direc… | 1 | ratio | agrees |  | eq | `[[art:44052838:sign_check.f_sato.agrees]]` | verified | 1 |
| 60 | conceptual_soundness | Every other checked feature agrees with its univariate direc… | 1 | ratio | coef_sign |  | eq | `[[art:55450fdb:sign_check.f_sato.coef_sign]]` | verified | 1 |
| 61 | conceptual_soundness | Every other checked feature agrees with its univariate direc… | 1 | ratio | univariate_direction |  | eq | `[[art:5cc2f196:sign_check.f_sato.univariate_direction]]` | verified | 1 |
| 62 | conceptual_soundness | Every other checked feature agrees with its univariate direc… | 1 | ratio | agrees |  | eq | `[[art:a7b47126:sign_check.f_burnout.agrees]]` | verified | 1 |
| 63 | conceptual_soundness | Every other checked feature agrees with its univariate direc… | 1 | ratio | coef_sign |  | eq | `[[art:434a2eb4:sign_check.f_burnout.coef_sign]]` | verified | 1 |
| 64 | conceptual_soundness | Every other checked feature agrees with its univariate direc… | 1 | ratio | univariate_direction |  | eq | `[[art:6c04f9a3:sign_check.f_burnout.univariate_direction]]` | verified | 1 |
| 65 | conceptual_soundness | Every other checked feature agrees with its univariate direc… | 1 | ratio | agrees |  | eq | `[[art:caceebf9:sign_check.f_season_sin.agrees]]` | verified | 1 |
| 66 | conceptual_soundness | Every other checked feature agrees with its univariate direc… | 1 | ratio | agrees |  | eq | `[[art:e02a4777:sign_check.f_season_cos.agrees]]` | verified | 1 |
| 67 | conceptual_soundness | Every other checked feature agrees with its univariate direc… | 1 | ratio | coef_sign |  | eq | `[[art:a6b9d22d:sign_check.f_season_sin.coef_sign]]` | verified | 1 |
| 68 | conceptual_soundness | Every other checked feature agrees with its univariate direc… | -1 | ratio | coef_sign |  | eq | `[[art:25dfa200:sign_check.f_season_cos.coef_sign]]` | verified | -1 |
| 69 | conceptual_soundness | Every other checked feature agrees with its univariate direc… | 1 | ratio | univariate_direction |  | eq | `[[art:8a2dc987:sign_check.f_season_sin.univariate_direction]]` | verified | 1 |
| 70 | conceptual_soundness | Every other checked feature agrees with its univariate direc… | -1 | ratio | univariate_direction |  | eq | `[[art:7f6fd623:sign_check.f_season_cos.univariate_direction]]` | verified | -1 |
| 71 | conceptual_soundness | Ablation is measured from a refit of the champion's function… | 0.7673 | ratio | baseline_auc | test | eq | `[[art:54367df6:ablation.baseline_auc]]` | verified | 0.7672992275 |
| 72 | conceptual_soundness | Dropping the refinance incentive changes test discrimination… | -0.04117 | ratio | delta_auc | test | eq | `[[art:cc8b34d4:ablation.f_incentive.delta_auc]]` | verified | -0.0411745927 |
| 73 | conceptual_soundness | Log original balance follows at -0.01927 and credit score at… | -0.01927 | ratio | delta_auc | test | eq | `[[art:dbd54a4a:ablation.f_orig_upb_log.delta_auc]]` | verified | -0.01926646624 |
| 74 | conceptual_soundness | Log original balance follows at -0.01927 and credit score at… | -0.01474 | ratio | delta_auc | test | eq | `[[art:302cee1d:ablation.f_credit_score.delta_auc]]` | verified | -0.0147431913 |
| 75 | conceptual_soundness | Original loan-to-value contributes -0.002294 , close to the… | -0.002294 | ratio | delta_auc | test | eq | `[[art:45bbe28a:ablation.f_orig_ltv.delta_auc]]` | verified | -0.002294407165 |
| 76 | conceptual_soundness | The remaining terms move test discrimination very little: se… | -0.0004826 | ratio | delta_auc | test | eq | `[[art:f01715f5:ablation.f_season_cos.delta_auc]]` | verified | -0.00048256018 |
| 77 | conceptual_soundness | The remaining terms move test discrimination very little: se… | -0.0003885 | ratio | delta_auc | test | eq | `[[art:a81a1fce:ablation.f_season_sin.delta_auc]]` | verified | -0.0003884794439 |
| 78 | conceptual_soundness | The remaining terms move test discrimination very little: se… | -0.0001876 | ratio | delta_auc | test | eq | `[[art:4c92a645:ablation.f_burnout.delta_auc]]` | verified | -0.0001876329287 |
| 79 | conceptual_soundness | Two features have positive deltas, meaning test discriminati… | 0.0005201 | ratio | delta_auc | test | eq | `[[art:452f8833:ablation.f_sato.delta_auc]]` | verified | 0.0005200867657 |
| 80 | conceptual_soundness | Two features have positive deltas, meaning test discriminati… | 0.0008166 | ratio | delta_auc | test | eq | `[[art:cd3be5c5:ablation.f_loan_age.delta_auc]]` | verified | 0.0008165996474 |
| 81 | conceptual_soundness | The champion attains a test AUC of 0.7753 and a test Brier s… | 0.7753 | ratio | auc | test | eq | `[[art:57066271:metrics.test.auc]]` | verified | 0.7752553922 |
| 82 | conceptual_soundness | The champion attains a test AUC of 0.7753 and a test Brier s… | 0.007894 | ratio | brier | test | eq | `[[art:7d3583cd:metrics.test.brier]]` | verified | 0.00789356705 |
| 83 | conceptual_soundness | The challenger attains a test AUC of 0.7 and a test Brier sc… | 0.7 | ratio | auc | test | eq | `[[art:a55c39c9:challenger.auc]]` | verified | 0.6999704544 |
| 84 | conceptual_soundness | The challenger attains a test AUC of 0.7 and a test Brier sc… | 0.008371 | ratio | brier | test | eq | `[[art:57c3e2f5:challenger.brier]]` | verified | 0.008371219123 |
| 85 | conceptual_soundness | On discrimination, the challenger's AUC minus the champion's… | -0.07528 | ratio | delta_auc | test | eq | `[[art:89de5f90:challenger.delta_auc]]` | verified | -0.07528493778 |
| 86 | conceptual_soundness | The declared decision rule requires the challenger to lead t… | 0.03 | ratio | delta_auc | test | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 87 | data_integrity | The training split holds 36013 rows , the test split holds 1… | 36013 | count | n | train | eq | `[[art:c5ebd9c9:profile.train.n]]` | verified | 36013 |
| 88 | data_integrity | The training split holds 36013 rows , the test split holds 1… | 15382 | count | n | test | eq | `[[art:e3abc1b8:profile.test.n]]` | verified | 15382 |
| 89 | data_integrity | The training split holds 36013 rows , the test split holds 1… | 32177 | count | n | vintage_holdout | eq | `[[art:426e712a:profile.vintage_holdout.n]]` | verified | 32177 |
| 90 | data_integrity | The training split holds 36013 rows , the test split holds 1… | 12257 | count | n | out_of_time | eq | `[[art:fa39c5cf:profile.out_of_time.n]]` | verified | 12257 |
| 91 | data_integrity | The largest missing fraction in the training split is 0 . | 0 | ratio | missing | train | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 92 | data_integrity | The largest missing fraction in the test split is 0 . | 0 | ratio | missing | test | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 93 | data_integrity | The largest missing fraction in the vintage holdout is 0 . | 0 | ratio | missing | vintage_holdout | eq | `[[art:329bb430:profile.vintage_holdout.missing.max]]` | verified | 0 |
| 94 | data_integrity | The largest missing fraction in the out-of-time split is 0 . | 0 | ratio | missing | out_of_time | eq | `[[art:4dafce11:profile.out_of_time.missing.max]]` | verified | 0 |
| 95 | data_integrity | Because no column in any of the four splits carries a missin… | 0.1 | ratio | missing_gap |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 96 | data_integrity | The declared population stability bound, train against test,… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 97 | data_integrity | The declared population stability bound, train against test,… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 98 | data_integrity | The largest train-to-test index, the score included, is 0.06… | 0.06189 | ratio | psi |  | eq | `[[art:c2e8c8fd:psi.max]]` | verified | 0.06188985797 |
| 99 | data_integrity | - Credit score: 0.06189 , the largest of the train-to-test s… | 0.06189 | ratio | psi |  | eq | `[[art:5829d6ed:psi.f_credit_score]]` | verified | 0.06188985797 |
| 100 | data_integrity | - Original loan balance in logs: 0.04817 . | 0.04817 | ratio | psi |  | eq | `[[art:75026ee2:psi.f_orig_upb_log]]` | verified | 0.04817081196 |
| 101 | data_integrity | - Original loan-to-value: 0.03617 . | 0.03617 | ratio | psi |  | eq | `[[art:212acb3a:psi.f_orig_ltv]]` | verified | 0.03617297258 |
| 102 | data_integrity | - Spread at origination: 0.02773 . | 0.02773 | ratio | psi |  | eq | `[[art:2beb335c:psi.f_sato]]` | verified | 0.02772829856 |
| 103 | data_integrity | - Note rate: 0.01371 . | 0.01371 | ratio | psi |  | eq | `[[art:63c68948:psi.f_note_rate]]` | verified | 0.01370911382 |
| 104 | data_integrity | - Burnout: 0.004614 . | 0.004614 | ratio | psi |  | eq | `[[art:445ec3e0:psi.f_burnout]]` | verified | 0.004614338236 |
| 105 | data_integrity | - Refinance incentive: 0.0009923 . | 0.0009923 | ratio | psi |  | eq | `[[art:8075e035:psi.f_incentive]]` | verified | 0.0009922551416 |
| 106 | data_integrity | - Loan age: 0.0001994 . | 0.0001994 | ratio | psi |  | eq | `[[art:6ec631ed:psi.f_loan_age]]` | verified | 0.0001993816816 |
| 107 | data_integrity | - Seasonal cosine term: 1.79e-05 . | 1.79e-05 | ratio | psi |  | eq | `[[art:cb2ce435:psi.f_season_cos]]` | verified | 1.790085913e-05 |
| 108 | data_integrity | - Seasonal sine term: 2.939e-06 . | 2.939e-06 | ratio | psi |  | eq | `[[art:44d14048:psi.f_season_sin]]` | verified | 2.939045338e-06 |
| 109 | data_integrity | The score itself shifts by 0.001953 between train and test,… | 0.001953 | ratio | psi |  | eq | `[[art:3b9dee2d:psi.y_score]]` | verified | 0.001952903716 |
| 110 | data_integrity | The score itself shifts by 0.001953 between train and test,… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 111 | data_integrity | The two remaining splits are read against the same declared… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 112 | data_integrity | - Burnout: 2.945 , above the declared bound. | 2.945 | ratio | psi | out_of_time | eq | `[[art:a696b6ff:psi.out_of_time.f_burnout]]` | verified | 2.944521522 |
| 113 | data_integrity | - Loan age: 2.484 , above the declared bound. | 2.484 | ratio | psi | out_of_time | eq | `[[art:eec03fdd:psi.out_of_time.f_loan_age]]` | verified | 2.483993033 |
| 114 | data_integrity | - Note rate: 0.6977 , above the declared bound. | 0.6977 | ratio | psi | out_of_time | eq | `[[art:b0278c59:psi.out_of_time.f_note_rate]]` | verified | 0.6976589281 |
| 115 | data_integrity | - Refinance incentive: 0.4958 , above the declared bound. | 0.4958 | ratio | psi | out_of_time | eq | `[[art:58b6089b:psi.out_of_time.f_incentive]]` | verified | 0.4958065489 |
| 116 | data_integrity | - Original loan balance in logs: 0.07136 . | 0.07136 | ratio | psi | out_of_time | eq | `[[art:fddf2a0a:psi.out_of_time.f_orig_upb_log]]` | verified | 0.07136421414 |
| 117 | data_integrity | - Credit score: 0.05988 . | 0.05988 | ratio | psi | out_of_time | eq | `[[art:e02f8367:psi.out_of_time.f_credit_score]]` | verified | 0.05987964443 |
| 118 | data_integrity | - Original loan-to-value: 0.04301 . | 0.04301 | ratio | psi | out_of_time | eq | `[[art:3422cd60:psi.out_of_time.f_orig_ltv]]` | verified | 0.04300793312 |
| 119 | data_integrity | - Seasonal sine term: 0.02789 . | 0.02789 | ratio | psi | out_of_time | eq | `[[art:eb28b9bb:psi.out_of_time.f_season_sin]]` | verified | 0.02788988464 |
| 120 | data_integrity | - Spread at origination: 0.01299 . | 0.01299 | ratio | psi | out_of_time | eq | `[[art:5090c358:psi.out_of_time.f_sato]]` | verified | 0.01298850667 |
| 121 | data_integrity | - Seasonal cosine term: 0.007524 . | 0.007524 | ratio | psi | out_of_time | eq | `[[art:3487f524:psi.out_of_time.f_season_cos]]` | verified | 0.00752368457 |
| 122 | data_integrity | The score shifts by 0.7056 between train and the out-of-time… | 0.7056 | ratio | psi | out_of_time | eq | `[[art:2dc61374:psi.out_of_time.y_score]]` | verified | 0.7055906656 |
| 123 | data_integrity | The score shifts by 0.7056 between train and the out-of-time… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 124 | data_integrity | - Note rate: 0.6088 , above the declared bound. | 0.6088 | ratio | psi | vintage_holdout | eq | `[[art:c1ffae38:psi.vintage_holdout.f_note_rate]]` | verified | 0.608822927 |
| 125 | data_integrity | - Refinance incentive: 0.4475 , above the declared bound. | 0.4475 | ratio | psi | vintage_holdout | eq | `[[art:81260b55:psi.vintage_holdout.f_incentive]]` | verified | 0.4475226601 |
| 126 | data_integrity | - Loan age: 0.07112 . | 0.07112 | ratio | psi | vintage_holdout | eq | `[[art:256aaeda:psi.vintage_holdout.f_loan_age]]` | verified | 0.07111526296 |
| 127 | data_integrity | - Burnout: 0.04749 . | 0.04749 | ratio | psi | vintage_holdout | eq | `[[art:b76fb2b0:psi.vintage_holdout.f_burnout]]` | verified | 0.04749372789 |
| 128 | data_integrity | - Original loan balance in logs: 0.0404 . | 0.0404 | ratio | psi | vintage_holdout | eq | `[[art:ce7dc6c5:psi.vintage_holdout.f_orig_upb_log]]` | verified | 0.04039645306 |
| 129 | data_integrity | - Credit score: 0.03996 . | 0.03996 | ratio | psi | vintage_holdout | eq | `[[art:abf4e0aa:psi.vintage_holdout.f_credit_score]]` | verified | 0.03995819732 |
| 130 | data_integrity | - Spread at origination: 0.02989 . | 0.02989 | ratio | psi | vintage_holdout | eq | `[[art:17126bd4:psi.vintage_holdout.f_sato]]` | verified | 0.02989256711 |
| 131 | data_integrity | - Original loan-to-value: 0.02942 . | 0.02942 | ratio | psi | vintage_holdout | eq | `[[art:09f015f3:psi.vintage_holdout.f_orig_ltv]]` | verified | 0.0294150369 |
| 132 | data_integrity | - Seasonal cosine term: 0.001288 . | 0.001288 | ratio | psi | vintage_holdout | eq | `[[art:5123c902:psi.vintage_holdout.f_season_cos]]` | verified | 0.0012879007 |
| 133 | data_integrity | - Seasonal sine term: 0.0007309 . | 0.0007309 | ratio | psi | vintage_holdout | eq | `[[art:403ec3c2:psi.vintage_holdout.f_season_sin]]` | verified | 0.0007309374015 |
| 134 | data_integrity | The score shifts by 0.1421 between train and the vintage hol… | 0.1421 | ratio | psi | vintage_holdout | eq | `[[art:3713457e:psi.vintage_holdout.y_score]]` | verified | 0.142110315 |
| 135 | data_integrity | The score shifts by 0.1421 between train and the vintage hol… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 136 | data_integrity | Comparing the two out-of-sample splits feature by feature on… | 2.945 | ratio | psi | out_of_time | eq | `[[art:a696b6ff:psi.out_of_time.f_burnout]]` | verified | 2.944521522 |
| 137 | data_integrity | Comparing the two out-of-sample splits feature by feature on… | 0.04749 | ratio | psi | vintage_holdout | eq | `[[art:b76fb2b0:psi.vintage_holdout.f_burnout]]` | verified | 0.04749372789 |
| 138 | data_integrity | Comparing the two out-of-sample splits feature by feature on… | 2.484 | ratio | psi | out_of_time | eq | `[[art:eec03fdd:psi.out_of_time.f_loan_age]]` | verified | 2.483993033 |
| 139 | data_integrity | Comparing the two out-of-sample splits feature by feature on… | 0.07112 | ratio | psi | vintage_holdout | eq | `[[art:256aaeda:psi.vintage_holdout.f_loan_age]]` | verified | 0.07111526296 |
| 140 | data_integrity | Comparing the two out-of-sample splits feature by feature on… | 0.6977 | ratio | psi | out_of_time | eq | `[[art:b0278c59:psi.out_of_time.f_note_rate]]` | verified | 0.6976589281 |
| 141 | data_integrity | Comparing the two out-of-sample splits feature by feature on… | 0.6088 | ratio | psi | vintage_holdout | eq | `[[art:c1ffae38:psi.vintage_holdout.f_note_rate]]` | verified | 0.608822927 |
| 142 | data_integrity | Comparing the two out-of-sample splits feature by feature on… | 0.4958 | ratio | psi | out_of_time | eq | `[[art:58b6089b:psi.out_of_time.f_incentive]]` | verified | 0.4958065489 |
| 143 | data_integrity | Comparing the two out-of-sample splits feature by feature on… | 0.4475 | ratio | psi | vintage_holdout | eq | `[[art:81260b55:psi.vintage_holdout.f_incentive]]` | verified | 0.4475226601 |
| 144 | data_integrity | The displacement is concentrated in the age-and-rate-path fe… | 0.7056 | ratio | psi | out_of_time | eq | `[[art:2dc61374:psi.out_of_time.y_score]]` | verified | 0.7055906656 |
| 145 | data_integrity | The largest characteristic contribution to the shift in the… | 0.03438 | ratio | csi |  | eq | `[[art:54bd75b0:csi.max]]` | verified | 0.03438094941 |
| 146 | data_integrity | The largest characteristic contribution to the shift in the… | 0.03438 | ratio | csi |  | eq | `[[art:1f963d83:csi.f_orig_ltv]]` | verified | 0.03438094941 |
| 147 | data_integrity | The remaining contributions are note rate at 0.01822 , credi… | 0.01822 | ratio | csi |  | eq | `[[art:06292416:csi.f_note_rate]]` | verified | 0.01822065751 |
| 148 | data_integrity | The remaining contributions are note rate at 0.01822 , credi… | 0.007909 | ratio | csi |  | eq | `[[art:70748e80:csi.f_credit_score]]` | verified | 0.007908848663 |
| 149 | data_integrity | The remaining contributions are note rate at 0.01822 , credi… | 0.005804 | ratio | csi |  | eq | `[[art:ac5ee43b:csi.f_incentive]]` | verified | 0.005803522882 |
| 150 | data_integrity | The remaining contributions are note rate at 0.01822 , credi… | 0.002969 | ratio | csi |  | eq | `[[art:a10d20d5:csi.f_orig_upb_log]]` | verified | 0.00296903904 |
| 151 | data_integrity | The remaining contributions are note rate at 0.01822 , credi… | 0.001487 | ratio | csi |  | eq | `[[art:ce21936e:csi.f_sato]]` | verified | 0.001487358985 |
| 152 | data_integrity | The remaining contributions are note rate at 0.01822 , credi… | 0.0009851 | ratio | csi |  | eq | `[[art:94a1612f:csi.f_burnout]]` | verified | 0.0009851123767 |
| 153 | data_integrity | The remaining contributions are note rate at 0.01822 , credi… | 0.0004785 | ratio | csi |  | eq | `[[art:15fe2d99:csi.f_season_cos]]` | verified | 0.0004785421555 |
| 154 | data_integrity | The remaining contributions are note rate at 0.01822 , credi… | 7.624e-05 | ratio | csi |  | eq | `[[art:81e8dbf0:csi.f_season_sin]]` | verified | 7.624273793e-05 |
| 155 | data_integrity | The remaining contributions are note rate at 0.01822 , credi… | 0 | ratio | csi |  | eq | `[[art:53ae3ece:csi.f_loan_age]]` | verified | 0 |
| 156 | data_integrity | The declared-timing screen flags 0 features as measured duri… | 0 | count | n_flagged |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 157 | data_integrity | The strongest single feature reaches an area under the curve… | 0.7239 | ratio | auc |  | eq | `[[art:1fe630dd:leakage.target_corr.max_single_feature_auc]]` | verified | 0.7238936567 |
| 158 | data_integrity | The strongest single feature reaches an area under the curve… | 0.9 | ratio | single_feature_auc |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 159 | data_integrity | On the identifier arm, the share of test rows whose loan and… | 0 | ratio | overlap |  | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 160 | data_integrity | On the identifier arm, the share of test rows whose loan and… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 161 | data_integrity | On the feature-vector arm, the share of test rows whose feat… | 0 | ratio | overlap |  | eq | `[[art:0fec8048:leakage.overlap.features]]` | verified | 0 |
| 162 | data_integrity | On the feature-vector arm, the share of test rows whose feat… | 0.005 | ratio | overlap |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 163 | data_integrity | The share of train rows whose feature values are not unique… | 0 | ratio | duplicates | train | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 164 | data_integrity | The row-level overlap screen likewise reports 0 . | 0 | ratio | overlap |  | eq | `[[art:4c9fcd09:leakage.overlap]]` | verified | 0 |
| 165 | data_integrity | The name screen matches 0 feature names against the target-a… | 0 | count | n_matched |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 166 | data_integrity | The data integrity screens pass: missingness is absent on ev… | 0.1 | ratio | missing_gap |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 167 | data_integrity | Train-to-test stability is well within the declared bound, w… | 0.06189 | ratio | psi |  | eq | `[[art:c2e8c8fd:psi.max]]` | verified | 0.06188985797 |
| 168 | data_integrity | Train-to-test stability is well within the declared bound, w… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 169 | data_integrity | The two dated splits are a different matter, and the score-l… | 0.7056 | ratio | psi | out_of_time | eq | `[[art:2dc61374:psi.out_of_time.y_score]]` | verified | 0.7055906656 |
| 170 | data_integrity | The two dated splits are a different matter, and the score-l… | 0.1421 | ratio | psi | vintage_holdout | eq | `[[art:3713457e:psi.vintage_holdout.y_score]]` | verified | 0.142110315 |
| 171 | outcomes | The logistic recalibration slope of the outcome on the logit… | 0.9937 | ratio | calibration_slope | train | eq | `[[art:534cb102:calibration_slope.train]]` | verified | 0.9936945557 |
| 172 | outcomes | The logistic recalibration slope of the outcome on the logit… | 0.9365 | ratio | calibration_slope | test | eq | `[[art:3e42ee62:calibration_slope.test]]` | verified | 0.9365180494 |
| 173 | outcomes | The logistic recalibration slope of the outcome on the logit… | 0.9969 | ratio | calibration_slope | out_of_time | eq | `[[art:a49b2789:calibration_slope.out_of_time]]` | verified | 0.9969389246 |
| 174 | outcomes | The logistic recalibration slope of the outcome on the logit… | 0.8373 | ratio | calibration_slope | vintage_holdout | eq | `[[art:08d6b321:calibration_slope.vintage_holdout]]` | verified | 0.837279841 |
| 175 | outcomes | The declared band for that slope runs from 0.8 to 1.2 , and… | 0.8 | ratio | calibration_slope |  | eq | `[[art:749634ae:threshold.C1.calibration_slope.min]]` | verified | 0.8 |
| 176 | outcomes | The declared band for that slope runs from 0.8 to 1.2 , and… | 1.2 | ratio | calibration_slope |  | eq | `[[art:b6672579:threshold.C1.calibration_slope.max]]` | verified | 1.2 |
| 177 | outcomes | The intercept of the same regression is -0.01454 on train, -… | -0.01454 | ratio | calibration_intercept | train | eq | `[[art:11d7a3ca:calibration_intercept.train]]` | verified | -0.01453793696 |
| 178 | outcomes | The intercept of the same regression is -0.01454 on train, -… | -0.277 | ratio | calibration_intercept | test | eq | `[[art:e87b5c13:calibration_intercept.test]]` | verified | -0.2769708146 |
| 179 | outcomes | The intercept of the same regression is -0.01454 on train, -… | -0.06272 | ratio | calibration_intercept | out_of_time | eq | `[[art:fc7ece3a:calibration_intercept.out_of_time]]` | verified | -0.06272473851 |
| 180 | outcomes | The intercept of the same regression is -0.01454 on train, -… | -0.9028 | ratio | calibration_intercept | vintage_holdout | eq | `[[art:44715143:calibration_intercept.vintage_holdout]]` | verified | -0.9028328443 |
| 181 | outcomes | On train, the mean predicted probability is 0.008427 against… | 0.008427 | ratio | mean_predicted | train | eq | `[[art:a63f6555:metrics.train.mean_predicted]]` | verified | 0.008426526894 |
| 182 | outcomes | On train, the mean predicted probability is 0.008427 against… | 0.008525 | ratio | event_rate | train | eq | `[[art:b9ef3327:metrics.train.event_rate]]` | verified | 0.008524699414 |
| 183 | outcomes | On train, the mean predicted probability is 0.008427 against… | 0.01152 | ratio | mean_rel_gap | train | eq | `[[art:e28c45a9:calibration.mean_rel_gap.train]]` | verified | 0.01151624417 |
| 184 | outcomes | On test, the mean predicted probability is 0.008116 against… | 0.008116 | ratio | mean_predicted | test | eq | `[[art:3bc93911:metrics.test.mean_predicted]]` | verified | 0.008115821785 |
| 185 | outcomes | On test, the mean predicted probability is 0.008116 against… | 0.008061 | ratio | event_rate | test | eq | `[[art:570cc08a:metrics.test.event_rate]]` | verified | 0.008061370433 |
| 186 | outcomes | On test, the mean predicted probability is 0.008116 against… | 0.006755 | ratio | mean_rel_gap | test | eq | `[[art:d1b269ea:calibration.mean_rel_gap.test]]` | verified | 0.006754602373 |
| 187 | outcomes | On the out-of-time split, the mean predicted probability is… | 0.01887 | ratio | mean_predicted | out_of_time | eq | `[[art:3833e0c5:metrics.out_of_time.mean_predicted]]` | verified | 0.01886588953 |
| 188 | outcomes | On the out-of-time split, the mean predicted probability is… | 0.01795 | ratio | event_rate | out_of_time | eq | `[[art:83ccf5c0:metrics.out_of_time.event_rate]]` | verified | 0.01794892714 |
| 189 | outcomes | On the out-of-time split, the mean predicted probability is… | 0.05109 | ratio | mean_rel_gap | out_of_time | eq | `[[art:c599bd89:calibration.mean_rel_gap.out_of_time]]` | verified | 0.05108730888 |
| 190 | outcomes | On the vintage holdout, the mean predicted probability is 0.… | 0.005647 | ratio | mean_predicted | vintage_holdout | eq | `[[art:5ae28866:metrics.vintage_holdout.mean_predicted]]` | verified | 0.005646788012 |
| 191 | outcomes | On the vintage holdout, the mean predicted probability is 0.… | 0.004817 | ratio | event_rate | vintage_holdout | eq | `[[art:e3590a16:metrics.vintage_holdout.event_rate]]` | verified | 0.004817105386 |
| 192 | outcomes | On the vintage holdout, the mean predicted probability is 0.… | 0.1722 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:55a672c2:calibration.mean_rel_gap.vintage_holdout]]` | verified | 0.1722367603 |
| 193 | outcomes | The declared tolerance on that relative gap is 0.25 , and ea… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 194 | outcomes | The mean absolute difference between actual and predicted co… | 0.02658 | ratio | mae | train | eq | `[[art:f2c3683c:cpr.train.mae]]` | verified | 0.02657629251 |
| 195 | outcomes | The mean absolute difference between actual and predicted co… | 0.04264 | ratio | mae | test | eq | `[[art:ff266c97:cpr.test.mae]]` | verified | 0.042636033 |
| 196 | outcomes | The mean absolute difference between actual and predicted co… | 0.05857 | ratio | mae | out_of_time | eq | `[[art:a7ecd72b:cpr.out_of_time.mae]]` | verified | 0.05856944955 |
| 197 | outcomes | The mean absolute difference between actual and predicted co… | 0.0289 | ratio | mae | vintage_holdout | eq | `[[art:172ebed4:cpr.vintage_holdout.mae]]` | verified | 0.0289048118 |
| 198 | outcomes | \| AUC \| 0.7883 \| 0.7753 \| 0.7846 \| 0.7718 \| | 0.7883 | ratio | auc | train | eq | `[[art:fa609ae1:metrics.train.auc]]` | verified | 0.7883327303 |
| 199 | outcomes | \| AUC \| 0.7883 \| 0.7753 \| 0.7846 \| 0.7718 \| | 0.7753 | ratio | auc | test | eq | `[[art:57066271:metrics.test.auc]]` | verified | 0.7752553922 |
| 200 | outcomes | \| AUC \| 0.7883 \| 0.7753 \| 0.7846 \| 0.7718 \| | 0.7846 | ratio | auc | out_of_time | eq | `[[art:6f2a2d99:metrics.out_of_time.auc]]` | verified | 0.7845616168 |
| 201 | outcomes | \| AUC \| 0.7883 \| 0.7753 \| 0.7846 \| 0.7718 \| | 0.7718 | ratio | auc | vintage_holdout | eq | `[[art:ac6794c5:metrics.vintage_holdout.auc]]` | verified | 0.7717974135 |
| 202 | outcomes | \| Gini \| 0.5767 \| 0.5505 \| 0.5691 \| 0.5436 \| | 0.5767 | ratio | gini | train | eq | `[[art:0b6b2058:metrics.train.gini]]` | verified | 0.5766654607 |
| 203 | outcomes | \| Gini \| 0.5767 \| 0.5505 \| 0.5691 \| 0.5436 \| | 0.5505 | ratio | gini | test | eq | `[[art:fe7f75d7:metrics.test.gini]]` | verified | 0.5505107844 |
| 204 | outcomes | \| Gini \| 0.5767 \| 0.5505 \| 0.5691 \| 0.5436 \| | 0.5691 | ratio | gini | out_of_time | eq | `[[art:890252d7:metrics.out_of_time.gini]]` | verified | 0.5691232337 |
| 205 | outcomes | \| Gini \| 0.5767 \| 0.5505 \| 0.5691 \| 0.5436 \| | 0.5436 | ratio | gini | vintage_holdout | eq | `[[art:a4a532f0:metrics.vintage_holdout.gini]]` | verified | 0.5435948269 |
| 206 | outcomes | \| KS \| 0.4562 \| 0.4162 \| 0.4321 \| 0.4516 \| | 0.4562 | ratio | ks | train | eq | `[[art:c355478b:metrics.train.ks]]` | verified | 0.4562056834 |
| 207 | outcomes | \| KS \| 0.4562 \| 0.4162 \| 0.4321 \| 0.4516 \| | 0.4162 | ratio | ks | test | eq | `[[art:c569c301:metrics.test.ks]]` | verified | 0.4161772354 |
| 208 | outcomes | \| KS \| 0.4562 \| 0.4162 \| 0.4321 \| 0.4516 \| | 0.4321 | ratio | ks | out_of_time | eq | `[[art:16d3e4fe:metrics.out_of_time.ks]]` | verified | 0.4321115953 |
| 209 | outcomes | \| KS \| 0.4562 \| 0.4162 \| 0.4321 \| 0.4516 \| | 0.4516 | ratio | ks | vintage_holdout | eq | `[[art:b5b9e888:metrics.vintage_holdout.ks]]` | verified | 0.4515647508 |
| 210 | outcomes | \| Brier \| 0.008317 \| 0.007894 \| 0.01713 \| 0.004763 \| | 0.008317 | ratio | brier | train | eq | `[[art:83666c70:metrics.train.brier]]` | verified | 0.008317491392 |
| 211 | outcomes | \| Brier \| 0.008317 \| 0.007894 \| 0.01713 \| 0.004763 \| | 0.007894 | ratio | brier | test | eq | `[[art:7d3583cd:metrics.test.brier]]` | verified | 0.00789356705 |
| 212 | outcomes | \| Brier \| 0.008317 \| 0.007894 \| 0.01713 \| 0.004763 \| | 0.01713 | ratio | brier | out_of_time | eq | `[[art:40d244d4:metrics.out_of_time.brier]]` | verified | 0.0171279495 |
| 213 | outcomes | \| Brier \| 0.008317 \| 0.007894 \| 0.01713 \| 0.004763 \| | 0.004763 | ratio | brier | vintage_holdout | eq | `[[art:f3c6bdcc:metrics.vintage_holdout.brier]]` | verified | 0.004763025704 |
| 214 | outcomes | \| Log loss \| 0.04408 \| 0.04263 \| 0.07975 \| 0.02811 \| | 0.04408 | ratio | logloss | train | eq | `[[art:199c7db5:metrics.train.logloss]]` | verified | 0.04408402922 |
| 215 | outcomes | \| Log loss \| 0.04408 \| 0.04263 \| 0.07975 \| 0.02811 \| | 0.04263 | ratio | logloss | test | eq | `[[art:320e4c6b:metrics.test.logloss]]` | verified | 0.04263297829 |
| 216 | outcomes | \| Log loss \| 0.04408 \| 0.04263 \| 0.07975 \| 0.02811 \| | 0.07975 | ratio | logloss | out_of_time | eq | `[[art:2b7c9b2d:metrics.out_of_time.logloss]]` | verified | 0.07975283787 |
| 217 | outcomes | \| Log loss \| 0.04408 \| 0.04263 \| 0.07975 \| 0.02811 \| | 0.02811 | ratio | logloss | vintage_holdout | eq | `[[art:c32e3713:metrics.vintage_holdout.logloss]]` | verified | 0.02810570342 |
| 218 | outcomes | \| Rows \| 36013 \| 15382 \| 12257 \| 32177 \| | 36013 | count | n | train | eq | `[[art:6fdfeabb:metrics.train.n]]` | verified | 36013 |
| 219 | outcomes | \| Rows \| 36013 \| 15382 \| 12257 \| 32177 \| | 15382 | count | n | test | eq | `[[art:e55953e1:metrics.test.n]]` | verified | 15382 |
| 220 | outcomes | \| Rows \| 36013 \| 15382 \| 12257 \| 32177 \| | 12257 | count | n | out_of_time | eq | `[[art:7898809e:metrics.out_of_time.n]]` | verified | 12257 |
| 221 | outcomes | \| Rows \| 36013 \| 15382 \| 12257 \| 32177 \| | 32177 | count | n | vintage_holdout | eq | `[[art:37a92951:metrics.vintage_holdout.n]]` | verified | 32177 |
| 222 | outcomes | The declared bound on the train-to-test AUC gap is 0.08 . | 0.08 | ratio | auc_gap |  | eq | `[[art:630f28f4:threshold.O1.auc_gap]]` | verified | 0.08 |
| 223 | outcomes | Test AUC of 0.7753 falls below train AUC of 0.7883 , and the… | 0.7753 | ratio | auc | test | eq | `[[art:57066271:metrics.test.auc]]` | verified | 0.7752553922 |
| 224 | outcomes | Test AUC of 0.7753 falls below train AUC of 0.7883 , and the… | 0.7883 | ratio | auc | train | eq | `[[art:fa609ae1:metrics.train.auc]]` | verified | 0.7883327303 |
| 225 | outcomes | Rank-ordering holds up across the splits on the same reading… | 0.5961 | ratio | top2_capture | train | eq | `[[art:e8dd0c53:deciles.train.top2_capture]]` | verified | 0.5960912052 |
| 226 | outcomes | Rank-ordering holds up across the splits on the same reading… | 0.5806 | ratio | top2_capture | test | eq | `[[art:43c4adc5:deciles.test.top2_capture]]` | verified | 0.5806451613 |
| 227 | outcomes | Rank-ordering holds up across the splits on the same reading… | 0.5773 | ratio | top2_capture | out_of_time | eq | `[[art:df63152b:deciles.out_of_time.top2_capture]]` | verified | 0.5772727273 |
| 228 | outcomes | Rank-ordering holds up across the splits on the same reading… | 0.5871 | ratio | top2_capture | vintage_holdout | eq | `[[art:8b59f312:deciles.vintage_holdout.top2_capture]]` | verified | 0.5870967742 |
| 229 | outcomes | This slice's AUC falls below its own split's by 0.07016 on t… | 0.07016 | ratio | auc_gap | train | eq | `[[art:4494db64:metrics.train.sub.f_incentive_high.auc_gap]]` | verified | 0.07015660217 |
| 230 | outcomes | This slice's AUC falls below its own split's by 0.07016 on t… | 0.0484 | ratio | auc_gap | test | eq | `[[art:95828768:metrics.test.sub.f_incentive_high.auc_gap]]` | verified | 0.04840270693 |
| 231 | outcomes | This slice's AUC falls below its own split's by 0.07016 on t… | 0.03734 | ratio | auc_gap | out_of_time | eq | `[[art:d9f9bdc9:metrics.out_of_time.sub.f_incentive_high.auc_gap]]` | verified | 0.0373425714 |
| 232 | outcomes | This slice's AUC falls below its own split's by 0.07016 on t… | 0.01875 | ratio | auc_gap | vintage_holdout | eq | `[[art:c847bcca:metrics.vintage_holdout.sub.f_incentive_high.auc_gap]]` | verified | 0.01874804418 |
| 233 | outcomes | This slice's AUC falls below its own split's by 0.07016 on t… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 234 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.4999 of the out… | 0.5 | ratio | share | train | eq | `[[art:6271ed11:metrics.train.sub.f_incentive_high.share]]` | verified | 0.4999861161 |
| 235 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.4999 of the out… | 0.5 | ratio | share | test | eq | `[[art:694313d4:metrics.test.sub.f_incentive_high.share]]` | verified | 0.5 |
| 236 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.4999 of the out… | 0.4999 | ratio | share | out_of_time | eq | `[[art:a90b35be:metrics.out_of_time.sub.f_incentive_high.share]]` | verified | 0.499877621 |
| 237 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.4999 of the out… | 0.5 | ratio | share | vintage_holdout | eq | `[[art:f4a76ad4:metrics.vintage_holdout.sub.f_incentive_high.share]]` | verified | 0.499984461 |
| 238 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.4999 of the out… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 239 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.4999 of the out… | 0.95 | ratio | slice_max_share |  | eq | `[[art:a928a05c:threshold.O1.slice_max_share]]` | verified | 0.95 |
| 240 | outcomes | On the level of the probabilities, mean predicted against ob… | 0.01445 | ratio | mean_rel_gap | train | eq | `[[art:961d0143:metrics.train.sub.f_incentive_high.mean_rel_gap]]` | verified | 0.01445428336 |
| 241 | outcomes | On the level of the probabilities, mean predicted against ob… | 0.03492 | ratio | mean_rel_gap | test | eq | `[[art:fd7ebc81:metrics.test.sub.f_incentive_high.mean_rel_gap]]` | verified | 0.03491504769 |
| 242 | outcomes | On the level of the probabilities, mean predicted against ob… | 0.1235 | ratio | mean_rel_gap | out_of_time | eq | `[[art:45ddf6b4:metrics.out_of_time.sub.f_incentive_high.mean_rel_gap]]` | verified | 0.123516925 |
| 243 | outcomes | On the level of the probabilities, mean predicted against ob… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 244 | outcomes | On the level of the probabilities, mean predicted against ob… | 0.2976 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:b3815f8c:metrics.vintage_holdout.sub.f_incentive_high.mean_rel_gap]]` | verified | 0.2975984466 |
| 245 | outcomes | This slice's AUC falls below its own split's by 0.06703 on t… | 0.06703 | ratio | auc_gap | train | eq | `[[art:3ec4f0fb:metrics.train.sub.f_incentive_low.auc_gap]]` | verified | 0.06702950807 |
| 246 | outcomes | This slice's AUC falls below its own split's by 0.06703 on t… | 0.0163 | ratio | auc_gap | out_of_time | eq | `[[art:6def945c:metrics.out_of_time.sub.f_incentive_low.auc_gap]]` | verified | 0.01629917634 |
| 247 | outcomes | This slice's AUC falls below its own split's by 0.06703 on t… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 248 | outcomes | On test the same shortfall is 0.09283 and on the vintage hol… | 0.09283 | ratio | auc_gap | test | eq | `[[art:f89dd8d1:metrics.test.sub.f_incentive_low.auc_gap]]` | verified | 0.09282587144 |
| 249 | outcomes | On test the same shortfall is 0.09283 and on the vintage hol… | 0.09945 | ratio | auc_gap | vintage_holdout | eq | `[[art:94bab5c0:metrics.vintage_holdout.sub.f_incentive_low.auc_gap]]` | verified | 0.09944645103 |
| 250 | outcomes | On test the same shortfall is 0.09283 and on the vintage hol… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 251 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.5001 of the out… | 0.5 | ratio | share | train | eq | `[[art:b323ed54:metrics.train.sub.f_incentive_low.share]]` | verified | 0.5000138839 |
| 252 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.5001 of the out… | 0.5 | ratio | share | test | eq | `[[art:e2282cb8:metrics.test.sub.f_incentive_low.share]]` | verified | 0.5 |
| 253 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.5001 of the out… | 0.5001 | ratio | share | out_of_time | eq | `[[art:4ad39f3f:metrics.out_of_time.sub.f_incentive_low.share]]` | verified | 0.500122379 |
| 254 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.5001 of the out… | 0.5 | ratio | share | vintage_holdout | eq | `[[art:b86413de:metrics.vintage_holdout.sub.f_incentive_low.share]]` | verified | 0.500015539 |
| 255 | outcomes | The slice holds 0.5 of train, 0.5 of test, 0.5001 of the out… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 256 | outcomes | Mean predicted against observed on this slice gives a relati… | 0.003953 | ratio | mean_rel_gap | train | eq | `[[art:ed8020c9:metrics.train.sub.f_incentive_low.mean_rel_gap]]` | verified | 0.003953431529 |
| 257 | outcomes | Mean predicted against observed on this slice gives a relati… | 0.1169 | ratio | mean_rel_gap | test | eq | `[[art:988b8044:metrics.test.sub.f_incentive_low.mean_rel_gap]]` | verified | 0.1169064836 |
| 258 | outcomes | Mean predicted against observed on this slice gives a relati… | 0.2155 | ratio | mean_rel_gap | out_of_time | eq | `[[art:970a62bf:metrics.out_of_time.sub.f_incentive_low.mean_rel_gap]]` | verified | 0.2155153206 |
| 259 | outcomes | Mean predicted against observed on this slice gives a relati… | 0.2422 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:2f10187b:metrics.vintage_holdout.sub.f_incentive_low.mean_rel_gap]]` | verified | 0.2421532582 |
| 260 | outcomes | Mean predicted against observed on this slice gives a relati… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 261 | outcomes | This slice's AUC falls below its own split's by 0.01424 on t… | 0.01424 | ratio | auc_gap | train | eq | `[[art:c37c76fc:metrics.train.sub.f_credit_score_low.auc_gap]]` | verified | 0.01423940939 |
| 262 | outcomes | This slice's AUC falls below its own split's by 0.01424 on t… | 0.03718 | ratio | auc_gap | test | eq | `[[art:0bd4944d:metrics.test.sub.f_credit_score_low.auc_gap]]` | verified | 0.03718473485 |
| 263 | outcomes | This slice's AUC falls below its own split's by 0.01424 on t… | 0.01988 | ratio | auc_gap | vintage_holdout | eq | `[[art:1e45f493:metrics.vintage_holdout.sub.f_credit_score_low.auc_gap]]` | verified | 0.0198819469 |
| 264 | outcomes | This slice's AUC falls below its own split's by 0.01424 on t… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 265 | outcomes | On the out-of-time split the same shortfall is -0.005002 , s… | -0.005002 | ratio | auc_gap | out_of_time | eq | `[[art:b7ff625e:metrics.out_of_time.sub.f_credit_score_low.auc_gap]]` | verified | -0.005002274857 |
| 266 | outcomes | The slice holds 0.5107 of train, 0.5065 of test, 0.5051 of t… | 0.5107 | ratio | share | train | eq | `[[art:db111665:metrics.train.sub.f_credit_score_low.share]]` | verified | 0.5106767001 |
| 267 | outcomes | The slice holds 0.5107 of train, 0.5065 of test, 0.5051 of t… | 0.5065 | ratio | share | test | eq | `[[art:db444481:metrics.test.sub.f_credit_score_low.share]]` | verified | 0.5065011052 |
| 268 | outcomes | The slice holds 0.5107 of train, 0.5065 of test, 0.5051 of t… | 0.5051 | ratio | share | out_of_time | eq | `[[art:2a7161de:metrics.out_of_time.sub.f_credit_score_low.share]]` | verified | 0.505099127 |
| 269 | outcomes | The slice holds 0.5107 of train, 0.5065 of test, 0.5051 of t… | 0.5121 | ratio | share | vintage_holdout | eq | `[[art:24402460:metrics.vintage_holdout.sub.f_credit_score_low.share]]` | verified | 0.5120738416 |
| 270 | outcomes | The slice holds 0.5107 of train, 0.5065 of test, 0.5051 of t… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 271 | outcomes | Mean predicted against observed on this slice gives a relati… | 0.03277 | ratio | mean_rel_gap | train | eq | `[[art:1aedaa05:metrics.train.sub.f_credit_score_low.mean_rel_gap]]` | verified | 0.03277197737 |
| 272 | outcomes | Mean predicted against observed on this slice gives a relati… | 0.1143 | ratio | mean_rel_gap | test | eq | `[[art:c03012ad:metrics.test.sub.f_credit_score_low.mean_rel_gap]]` | verified | 0.1143031528 |
| 273 | outcomes | Mean predicted against observed on this slice gives a relati… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 274 | outcomes | Mean predicted against observed on this slice gives a relati… | 0.2632 | ratio | mean_rel_gap | out_of_time | eq | `[[art:c16c2369:metrics.out_of_time.sub.f_credit_score_low.mean_rel_gap]]` | verified | 0.2631841364 |
| 275 | outcomes | Mean predicted against observed on this slice gives a relati… | 0.2694 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:4aeed415:metrics.vintage_holdout.sub.f_credit_score_low.mean_rel_gap]]` | verified | 0.2693996749 |
| 276 | outcomes | This slice's AUC falls below its own split's by 0.007432 on… | 0.007432 | ratio | auc_gap | train | eq | `[[art:bf2cbaa2:metrics.train.sub.f_credit_score_high.auc_gap]]` | verified | 0.007431842548 |
| 277 | outcomes | This slice's AUC falls below its own split's by 0.007432 on… | 0.0225 | ratio | auc_gap | out_of_time | eq | `[[art:61605613:metrics.out_of_time.sub.f_credit_score_high.auc_gap]]` | verified | 0.02249861616 |
| 278 | outcomes | This slice's AUC falls below its own split's by 0.007432 on… | 0.008704 | ratio | auc_gap | vintage_holdout | eq | `[[art:65d309d4:metrics.vintage_holdout.sub.f_credit_score_high.auc_gap]]` | verified | 0.008703813819 |
| 279 | outcomes | This slice's AUC falls below its own split's by 0.007432 on… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 280 | outcomes | This slice's AUC falls below its own split's by 0.007432 on… | -0.00429 | ratio | auc_gap | test | eq | `[[art:61fcae59:metrics.test.sub.f_credit_score_high.auc_gap]]` | verified | -0.004290453598 |
| 281 | outcomes | The slice holds 0.4893 of train, 0.4935 of test, 0.4949 of t… | 0.4893 | ratio | share | train | eq | `[[art:59d4af35:metrics.train.sub.f_credit_score_high.share]]` | verified | 0.4893232999 |
| 282 | outcomes | The slice holds 0.4893 of train, 0.4935 of test, 0.4949 of t… | 0.4935 | ratio | share | test | eq | `[[art:c84c6685:metrics.test.sub.f_credit_score_high.share]]` | verified | 0.4934988948 |
| 283 | outcomes | The slice holds 0.4893 of train, 0.4935 of test, 0.4949 of t… | 0.4949 | ratio | share | out_of_time | eq | `[[art:7696fcbc:metrics.out_of_time.sub.f_credit_score_high.share]]` | verified | 0.494900873 |
| 284 | outcomes | The slice holds 0.4893 of train, 0.4935 of test, 0.4949 of t… | 0.4879 | ratio | share | vintage_holdout | eq | `[[art:73cedd3e:metrics.vintage_holdout.sub.f_credit_score_high.share]]` | verified | 0.4879261584 |
| 285 | outcomes | The slice holds 0.4893 of train, 0.4935 of test, 0.4949 of t… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 286 | outcomes | Mean predicted against observed on this slice gives a relati… | 0.03625 | ratio | mean_rel_gap | train | eq | `[[art:840702d6:metrics.train.sub.f_credit_score_high.mean_rel_gap]]` | verified | 0.03624570798 |
| 287 | outcomes | Mean predicted against observed on this slice gives a relati… | 0.04833 | ratio | mean_rel_gap | test | eq | `[[art:7415cfef:metrics.test.sub.f_credit_score_high.mean_rel_gap]]` | verified | 0.04833124053 |
| 288 | outcomes | Mean predicted against observed on this slice gives a relati… | 0.04583 | ratio | mean_rel_gap | out_of_time | eq | `[[art:5da6c245:metrics.out_of_time.sub.f_credit_score_high.mean_rel_gap]]` | verified | 0.045831109 |
| 289 | outcomes | Mean predicted against observed on this slice gives a relati… | 0.1232 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:31e9c5fc:metrics.vintage_holdout.sub.f_credit_score_high.mean_rel_gap]]` | verified | 0.1231836384 |
| 290 | outcomes | Mean predicted against observed on this slice gives a relati… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 291 | sensitivity | The largest variance inflation factor among the retained fea… | 4.976 | ratio | vif |  | eq | `[[art:f9e0db60:vif.max]]` | verified | 4.975500767 |
| 292 | sensitivity | The largest variance inflation factor among the retained fea… | 10 | ratio | vif |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 293 | sensitivity | That maximum is carried by the note-rate feature at 4.976 ,… | 4.976 | ratio | vif |  | eq | `[[art:f6dfe789:vif.f_note_rate]]` | verified | 4.975500767 |
| 294 | sensitivity | That maximum is carried by the note-rate feature at 4.976 ,… | 3.439 | ratio | vif |  | eq | `[[art:3f7564f6:vif.f_burnout]]` | verified | 3.439328594 |
| 295 | sensitivity | That maximum is carried by the note-rate feature at 4.976 ,… | 2.929 | ratio | vif |  | eq | `[[art:903503b0:vif.f_loan_age]]` | verified | 2.928871763 |
| 296 | sensitivity | The refinance-incentive feature stands at 2.226 and the spre… | 2.226 | ratio | vif |  | eq | `[[art:31179b0a:vif.f_incentive]]` | verified | 2.22632259 |
| 297 | sensitivity | The refinance-incentive feature stands at 2.226 and the spre… | 1.713 | ratio | vif |  | eq | `[[art:9a173f4f:vif.f_sato]]` | verified | 1.71256814 |
| 298 | sensitivity | The refinance-incentive feature stands at 2.226 and the spre… | 1.018 | ratio | vif |  | eq | `[[art:77f16218:vif.f_season_cos]]` | verified | 1.017653349 |
| 299 | sensitivity | The refinance-incentive feature stands at 2.226 and the spre… | 1.008 | ratio | vif |  | eq | `[[art:59d19ea1:vif.f_credit_score]]` | verified | 1.007978309 |
| 300 | sensitivity | The refinance-incentive feature stands at 2.226 and the spre… | 1.006 | ratio | vif |  | eq | `[[art:8b0886fe:vif.f_orig_upb_log]]` | verified | 1.005846447 |
| 301 | sensitivity | The refinance-incentive feature stands at 2.226 and the spre… | 1.005 | ratio | vif |  | eq | `[[art:d0eadaeb:vif.f_orig_ltv]]` | verified | 1.004506143 |
| 302 | sensitivity | The refinance-incentive feature stands at 2.226 and the spre… | 1.004 | ratio | vif |  | eq | `[[art:3d38c119:vif.f_season_sin]]` | verified | 1.004128844 |
| 303 | sensitivity | Belsley's condition number of the column-standardised design… | 4.943 | ratio | condition_number |  | eq | `[[art:4f06a3c5:condition_number]]` | verified | 4.942565522 |
| 304 | sensitivity | Belsley's condition number of the column-standardised design… | 30 | ratio | condition_number |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 305 | sensitivity | The declared tolerance on the difference in AUC across regim… | 0.1 | ratio | auc_gap |  | eq | `[[art:b64213d7:threshold.R1.auc_gap]]` | verified | 0.1 |
| 306 | sensitivity | Coefficient stability was assessed by a sign-flip test, whic… | 0.05 | ratio | sign_flip_coef |  | eq | `[[art:aca84377:threshold.R1.sign_flip_coef]]` | verified | 0.05 |
| 307 | sensitivity | Coefficient stability was assessed by a sign-flip test, whic… | 2 | ratio | sign_flip_z |  | eq | `[[art:2e4428c7:threshold.R1.sign_flip_z]]` | verified | 2 |
| 308 | sensitivity | The test registers at 0 for the refinance-incentive feature… | 0 | count | sign_flip |  | eq | `[[art:1e3dbc9b:stability.f_incentive.sign_flip]]` | verified | 0 |
| 309 | sensitivity | The test registers at 0 for the refinance-incentive feature… | 0 | count | sign_flip |  | eq | `[[art:4a9e3c32:stability.f_note_rate.sign_flip]]` | verified | 0 |
| 310 | sensitivity | The test registers at 0 for the refinance-incentive feature… | 0 | count | sign_flip |  | eq | `[[art:ffc296b7:stability.f_burnout.sign_flip]]` | verified | 0 |
| 311 | sensitivity | The test registers at 0 for the refinance-incentive feature… | 0 | count | sign_flip |  | eq | `[[art:02339bed:stability.f_loan_age.sign_flip]]` | verified | 0 |
| 312 | sensitivity | The test registers at 0 for the refinance-incentive feature… | 0 | count | sign_flip |  | eq | `[[art:a7092419:stability.f_sato.sign_flip]]` | verified | 0 |
| 313 | sensitivity | It likewise registers at 0 for the credit-score feature , at… | 0 | count | sign_flip |  | eq | `[[art:453c8949:stability.f_credit_score.sign_flip]]` | verified | 0 |
| 314 | sensitivity | It likewise registers at 0 for the credit-score feature , at… | 0 | count | sign_flip |  | eq | `[[art:bb5e04ca:stability.f_orig_ltv.sign_flip]]` | verified | 0 |
| 315 | sensitivity | It likewise registers at 0 for the credit-score feature , at… | 0 | count | sign_flip |  | eq | `[[art:5a5daefb:stability.f_orig_upb_log.sign_flip]]` | verified | 0 |
| 316 | sensitivity | It likewise registers at 0 for the credit-score feature , at… | 0 | count | sign_flip |  | eq | `[[art:3c609ed8:stability.f_season_sin.sign_flip]]` | verified | 0 |
| 317 | sensitivity | It likewise registers at 0 for the credit-score feature , at… | 0 | count | sign_flip |  | eq | `[[art:4c9ae175:stability.f_season_cos.sign_flip]]` | verified | 0 |
| 318 | sensitivity | At the extreme downward shock the change in servicing value… | -1298000 | currency | value_change |  | eq | `[[art:4829926e:scenario.value_change.-300]]` | verified | -1297986.399 |
| 319 | sensitivity | At the extreme downward shock the change in servicing value… | 168100 | currency | value_change |  | eq | `[[art:38e75872:scenario.value_change.300]]` | verified | 168054.7452 |
| 320 | sensitivity | Across the grid the change in value increases without revers… | -1298000 | currency | value_change |  | eq | `[[art:4829926e:scenario.value_change.-300]]` | verified | -1297986.399 |
| 321 | sensitivity | Across the grid the change in value increases without revers… | -854300 | currency | value_change |  | eq | `[[art:03816874:scenario.value_change.-200]]` | verified | -854265.8614 |
| 322 | sensitivity | Across the grid the change in value increases without revers… | -322600 | currency | value_change |  | eq | `[[art:d33e8e3c:scenario.value_change.-100]]` | verified | -322648.7678 |
| 323 | sensitivity | Across the grid the change in value increases without revers… | 0 | currency | value_change |  | eq | `[[art:1e1b0b88:scenario.value_change.0]]` | verified | 0 |
| 324 | sensitivity | Across the grid the change in value increases without revers… | 119600 | currency | value_change |  | eq | `[[art:d0970bd9:scenario.value_change.100]]` | verified | 119555.7352 |
| 325 | sensitivity | Across the grid the change in value increases without revers… | 157000 | currency | value_change |  | eq | `[[art:d69c2be1:scenario.value_change.200]]` | verified | 156987.0553 |
| 326 | sensitivity | Across the grid the change in value increases without revers… | 168100 | currency | value_change |  | eq | `[[art:38e75872:scenario.value_change.300]]` | verified | 168054.7452 |
| 327 | sensitivity | The convexity measure, the change at the extreme downward sh… | -1130000 | currency | convexity |  | eq | `[[art:538e0e09:scenario.convexity]]` | verified | -1129931.654 |
| 328 | findings | On the test split, the sub-population defined by `f_incentiv… | 0.6824 | ratio | auc | test | eq | `[[art:1966c5b1:metrics.test.sub.f_incentive_low.auc]]` | verified | 0.6824295208 |
| 329 | findings | On the test split, the sub-population defined by `f_incentiv… | 0.09283 | ratio | auc_gap | test | eq | `[[art:f89dd8d1:metrics.test.sub.f_incentive_low.auc_gap]]` | verified | 0.09282587144 |
| 330 | findings | On the test split, the sub-population defined by `f_incentiv… | 0.7753 | ratio | auc | test | eq | `[[art:57066271:metrics.test.auc]]` | verified | 0.7752553922 |
| 331 | findings | On the test split, the sub-population defined by `f_incentiv… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 332 | findings | On the test split, the sub-population defined by `f_incentiv… | 0.5 | ratio | share | test | eq | `[[art:e2282cb8:metrics.test.sub.f_incentive_low.share]]` | verified | 0.5 |
| 333 | findings | On the test split, the sub-population defined by `f_incentiv… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 334 | findings | On the vintage_holdout split, the same sub-population define… | 0.6724 | ratio | auc | vintage_holdout | eq | `[[art:fa61514e:metrics.vintage_holdout.sub.f_incentive_low.auc]]` | verified | 0.6723509624 |
| 335 | findings | On the vintage_holdout split, the same sub-population define… | 0.09945 | ratio | auc_gap | vintage_holdout | eq | `[[art:94bab5c0:metrics.vintage_holdout.sub.f_incentive_low.auc_gap]]` | verified | 0.09944645103 |
| 336 | findings | On the vintage_holdout split, the same sub-population define… | 0.7718 | ratio | auc | vintage_holdout | eq | `[[art:ac6794c5:metrics.vintage_holdout.auc]]` | verified | 0.7717974135 |
| 337 | findings | On the vintage_holdout split, the same sub-population define… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 338 | findings | On the vintage_holdout split, the same sub-population define… | 0.5 | ratio | share | vintage_holdout | eq | `[[art:b86413de:metrics.vintage_holdout.sub.f_incentive_low.share]]` | verified | 0.500015539 |
| 339 | findings | On the vintage_holdout split, the same sub-population define… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 340 | findings | The fitted coefficient on `f_note_rate` carries sign -1 wher… | -1 | ratio | coef_sign |  | eq | `[[art:9a57eeb9:sign_check.f_note_rate.coef_sign]]` | verified | -1 |
| 341 | findings | The fitted coefficient on `f_note_rate` carries sign -1 wher… | 1 | ratio | univariate_direction |  | eq | `[[art:33e2a051:sign_check.f_note_rate.univariate_direction]]` | verified | 1 |
| 342 | findings | The fitted coefficient on `f_note_rate` carries sign -1 wher… | 0 | ratio | agrees |  | eq | `[[art:e3173464:sign_check.f_note_rate.agrees]]` | verified | 0 |
| 343 | monitoring | Calibration should be tracked first: on each production vint… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 344 | monitoring | Calibration should be tracked first: on each production vint… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 345 | monitoring | The validation reading of that slope on held-out test data,… | 0.9365 | ratio | calibration_slope | test | eq | `[[art:3e42ee62:calibration_slope.test]]` | verified | 0.9365180494 |
| 346 | monitoring | Discrimination should be tracked next: report the area under… | 0.65 | ratio | auc | test | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 347 | monitoring | Discrimination should be tracked next: report the area under… | 0.7753 | ratio | auc | test | eq | `[[art:57066271:metrics.test.auc]]` | verified | 0.7752553922 |
| 348 | monitoring | Input and score stability should be tracked monthly, because… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 349 | monitoring | The largest train-to-test stability reading in this validati… | 0.06189 | ratio | psi |  | eq | `[[art:c2e8c8fd:psi.max]]` | verified | 0.06188985797 |

## Appendix B — Artifact index

The store holds 467 artifacts; the 281 this report cites or rests a finding on are indexed here.

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
| `metrics.out_of_time.sub.f_credit_score_high` | `f725a00a` | table | table, 10 rows | every metric on the f_credit_score above_median slice of out_of_time |
| `metrics.out_of_time.sub.f_credit_score_high.auc_gap` | `61605613` | scalar | 0.02249861616 | how far AUC on the f_credit_score above_median slice of out_of_time falls below AUC on all of out_of_time |
| `metrics.out_of_time.sub.f_credit_score_high.mean_rel_gap` | `5da6c245` | scalar | 0.045831109 | mean predicted against observed on the f_credit_score above_median slice of out_of_time, relative |
| `metrics.out_of_time.sub.f_credit_score_high.share` | `7696fcbc` | scalar | 0.494900873 | the share of out_of_time the f_credit_score above_median slice holds |
| `metrics.out_of_time.sub.f_credit_score_low` | `407fbd64` | table | table, 10 rows | every metric on the f_credit_score below_median slice of out_of_time |
| `metrics.out_of_time.sub.f_credit_score_low.auc_gap` | `b7ff625e` | scalar | -0.005002274857 | how far AUC on the f_credit_score below_median slice of out_of_time falls below AUC on all of out_of_time |
| `metrics.out_of_time.sub.f_credit_score_low.mean_rel_gap` | `c16c2369` | scalar | 0.2631841364 | mean predicted against observed on the f_credit_score below_median slice of out_of_time, relative |
| `metrics.out_of_time.sub.f_credit_score_low.share` | `2a7161de` | scalar | 0.505099127 | the share of out_of_time the f_credit_score below_median slice holds |
| `metrics.out_of_time.sub.f_incentive_high` | `e8891641` | table | table, 10 rows | every metric on the f_incentive above_median slice of out_of_time |
| `metrics.out_of_time.sub.f_incentive_high.auc_gap` | `d9f9bdc9` | scalar | 0.0373425714 | how far AUC on the f_incentive above_median slice of out_of_time falls below AUC on all of out_of_time |
| `metrics.out_of_time.sub.f_incentive_high.mean_rel_gap` | `45ddf6b4` | scalar | 0.123516925 | mean predicted against observed on the f_incentive above_median slice of out_of_time, relative |
| `metrics.out_of_time.sub.f_incentive_high.share` | `a90b35be` | scalar | 0.499877621 | the share of out_of_time the f_incentive above_median slice holds |
| `metrics.out_of_time.sub.f_incentive_low` | `3b3a801d` | table | table, 10 rows | every metric on the f_incentive below_median slice of out_of_time |
| `metrics.out_of_time.sub.f_incentive_low.auc_gap` | `6def945c` | scalar | 0.01629917634 | how far AUC on the f_incentive below_median slice of out_of_time falls below AUC on all of out_of_time |
| `metrics.out_of_time.sub.f_incentive_low.mean_rel_gap` | `970a62bf` | scalar | 0.2155153206 | mean predicted against observed on the f_incentive below_median slice of out_of_time, relative |
| `metrics.out_of_time.sub.f_incentive_low.share` | `4ad39f3f` | scalar | 0.500122379 | the share of out_of_time the f_incentive below_median slice holds |
| `metrics.test.auc` | `57066271` | scalar | 0.7752553922 | auc on test, recomputed by quaestor |
| `metrics.test.brier` | `7d3583cd` | scalar | 0.00789356705 | brier on test, recomputed by quaestor |
| `metrics.test.event_rate` | `570cc08a` | scalar | 0.008061370433 | event_rate on test, recomputed by quaestor |
| `metrics.test.gini` | `fe7f75d7` | scalar | 0.5505107844 | gini on test, recomputed by quaestor |
| `metrics.test.ks` | `c569c301` | scalar | 0.4161772354 | ks on test, recomputed by quaestor |
| `metrics.test.logloss` | `320e4c6b` | scalar | 0.04263297829 | logloss on test, recomputed by quaestor |
| `metrics.test.mean_predicted` | `3bc93911` | scalar | 0.008115821785 | mean_predicted on test, recomputed by quaestor |
| `metrics.test.n` | `e55953e1` | scalar | 15382 | n on test, recomputed by quaestor |
| `metrics.test.sub.f_credit_score_high` | `10c679a4` | table | table, 10 rows | every metric on the f_credit_score above_median slice of test |
| `metrics.test.sub.f_credit_score_high.auc_gap` | `61fcae59` | scalar | -0.004290453598 | how far AUC on the f_credit_score above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.f_credit_score_high.mean_rel_gap` | `7415cfef` | scalar | 0.04833124053 | mean predicted against observed on the f_credit_score above_median slice of test, relative |
| `metrics.test.sub.f_credit_score_high.share` | `c84c6685` | scalar | 0.4934988948 | the share of test the f_credit_score above_median slice holds |
| `metrics.test.sub.f_credit_score_low` | `c9acf630` | table | table, 10 rows | every metric on the f_credit_score below_median slice of test |
| `metrics.test.sub.f_credit_score_low.auc_gap` | `0bd4944d` | scalar | 0.03718473485 | how far AUC on the f_credit_score below_median slice of test falls below AUC on all of test |
| `metrics.test.sub.f_credit_score_low.mean_rel_gap` | `c03012ad` | scalar | 0.1143031528 | mean predicted against observed on the f_credit_score below_median slice of test, relative |
| `metrics.test.sub.f_credit_score_low.share` | `db444481` | scalar | 0.5065011052 | the share of test the f_credit_score below_median slice holds |
| `metrics.test.sub.f_incentive_high` | `26bcaea2` | table | table, 10 rows | every metric on the f_incentive above_median slice of test |
| `metrics.test.sub.f_incentive_high.auc_gap` | `95828768` | scalar | 0.04840270693 | how far AUC on the f_incentive above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.f_incentive_high.mean_rel_gap` | `fd7ebc81` | scalar | 0.03491504769 | mean predicted against observed on the f_incentive above_median slice of test, relative |
| `metrics.test.sub.f_incentive_high.share` | `694313d4` | scalar | 0.5 | the share of test the f_incentive above_median slice holds |
| `metrics.test.sub.f_incentive_low` | `c9d117e4` | table | table, 10 rows | every metric on the f_incentive below_median slice of test |
| `metrics.test.sub.f_incentive_low.auc` | `1966c5b1` | scalar | 0.6824295208 | auc on the f_incentive below_median slice of test |
| `metrics.test.sub.f_incentive_low.auc_gap` | `f89dd8d1` | scalar | 0.09282587144 | how far AUC on the f_incentive below_median slice of test falls below AUC on all of test |
| `metrics.test.sub.f_incentive_low.mean_rel_gap` | `988b8044` | scalar | 0.1169064836 | mean predicted against observed on the f_incentive below_median slice of test, relative |
| `metrics.test.sub.f_incentive_low.share` | `e2282cb8` | scalar | 0.5 | the share of test the f_incentive below_median slice holds |
| `metrics.train.auc` | `fa609ae1` | scalar | 0.7883327303 | auc on train, recomputed by quaestor |
| `metrics.train.brier` | `83666c70` | scalar | 0.008317491392 | brier on train, recomputed by quaestor |
| `metrics.train.event_rate` | `b9ef3327` | scalar | 0.008524699414 | event_rate on train, recomputed by quaestor |
| `metrics.train.gini` | `0b6b2058` | scalar | 0.5766654607 | gini on train, recomputed by quaestor |
| `metrics.train.ks` | `c355478b` | scalar | 0.4562056834 | ks on train, recomputed by quaestor |
| `metrics.train.logloss` | `199c7db5` | scalar | 0.04408402922 | logloss on train, recomputed by quaestor |
| `metrics.train.mean_predicted` | `a63f6555` | scalar | 0.008426526894 | mean_predicted on train, recomputed by quaestor |
| `metrics.train.n` | `6fdfeabb` | scalar | 36013 | n on train, recomputed by quaestor |
| `metrics.train.sub.f_credit_score_high` | `c01fd0e6` | table | table, 10 rows | every metric on the f_credit_score above_median slice of train |
| `metrics.train.sub.f_credit_score_high.auc_gap` | `bf2cbaa2` | scalar | 0.007431842548 | how far AUC on the f_credit_score above_median slice of train falls below AUC on all of train |
| `metrics.train.sub.f_credit_score_high.mean_rel_gap` | `840702d6` | scalar | 0.03624570798 | mean predicted against observed on the f_credit_score above_median slice of train, relative |
| `metrics.train.sub.f_credit_score_high.share` | `59d4af35` | scalar | 0.4893232999 | the share of train the f_credit_score above_median slice holds |
| `metrics.train.sub.f_credit_score_low` | `46ae8e9c` | table | table, 10 rows | every metric on the f_credit_score below_median slice of train |
| `metrics.train.sub.f_credit_score_low.auc_gap` | `c37c76fc` | scalar | 0.01423940939 | how far AUC on the f_credit_score below_median slice of train falls below AUC on all of train |
| `metrics.train.sub.f_credit_score_low.mean_rel_gap` | `1aedaa05` | scalar | 0.03277197737 | mean predicted against observed on the f_credit_score below_median slice of train, relative |
| `metrics.train.sub.f_credit_score_low.share` | `db111665` | scalar | 0.5106767001 | the share of train the f_credit_score below_median slice holds |
| `metrics.train.sub.f_incentive_high` | `78c63acb` | table | table, 10 rows | every metric on the f_incentive above_median slice of train |
| `metrics.train.sub.f_incentive_high.auc_gap` | `4494db64` | scalar | 0.07015660217 | how far AUC on the f_incentive above_median slice of train falls below AUC on all of train |
| `metrics.train.sub.f_incentive_high.mean_rel_gap` | `961d0143` | scalar | 0.01445428336 | mean predicted against observed on the f_incentive above_median slice of train, relative |
| `metrics.train.sub.f_incentive_high.share` | `6271ed11` | scalar | 0.4999861161 | the share of train the f_incentive above_median slice holds |
| `metrics.train.sub.f_incentive_low` | `9bfedc02` | table | table, 10 rows | every metric on the f_incentive below_median slice of train |
| `metrics.train.sub.f_incentive_low.auc_gap` | `3ec4f0fb` | scalar | 0.06702950807 | how far AUC on the f_incentive below_median slice of train falls below AUC on all of train |
| `metrics.train.sub.f_incentive_low.mean_rel_gap` | `ed8020c9` | scalar | 0.003953431529 | mean predicted against observed on the f_incentive below_median slice of train, relative |
| `metrics.train.sub.f_incentive_low.share` | `b323ed54` | scalar | 0.5000138839 | the share of train the f_incentive below_median slice holds |
| `metrics.vintage_holdout.auc` | `ac6794c5` | scalar | 0.7717974135 | auc on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.brier` | `f3c6bdcc` | scalar | 0.004763025704 | brier on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.event_rate` | `e3590a16` | scalar | 0.004817105386 | event_rate on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.gini` | `a4a532f0` | scalar | 0.5435948269 | gini on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.ks` | `b5b9e888` | scalar | 0.4515647508 | ks on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.logloss` | `c32e3713` | scalar | 0.02810570342 | logloss on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.mean_predicted` | `5ae28866` | scalar | 0.005646788012 | mean_predicted on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.n` | `37a92951` | scalar | 32177 | n on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.sub.f_credit_score_high` | `a0163007` | table | table, 10 rows | every metric on the f_credit_score above_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.f_credit_score_high.auc_gap` | `65d309d4` | scalar | 0.008703813819 | how far AUC on the f_credit_score above_median slice of vintage_holdout falls below AUC on all of vintage_holdout |
| `metrics.vintage_holdout.sub.f_credit_score_high.mean_rel_gap` | `31e9c5fc` | scalar | 0.1231836384 | mean predicted against observed on the f_credit_score above_median slice of vintage_holdout, relative |
| `metrics.vintage_holdout.sub.f_credit_score_high.share` | `73cedd3e` | scalar | 0.4879261584 | the share of vintage_holdout the f_credit_score above_median slice holds |
| `metrics.vintage_holdout.sub.f_credit_score_low` | `6a47626f` | table | table, 10 rows | every metric on the f_credit_score below_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.f_credit_score_low.auc_gap` | `1e45f493` | scalar | 0.0198819469 | how far AUC on the f_credit_score below_median slice of vintage_holdout falls below AUC on all of vintage_holdout |
| `metrics.vintage_holdout.sub.f_credit_score_low.mean_rel_gap` | `4aeed415` | scalar | 0.2693996749 | mean predicted against observed on the f_credit_score below_median slice of vintage_holdout, relative |
| `metrics.vintage_holdout.sub.f_credit_score_low.share` | `24402460` | scalar | 0.5120738416 | the share of vintage_holdout the f_credit_score below_median slice holds |
| `metrics.vintage_holdout.sub.f_incentive_high` | `95c63ecb` | table | table, 10 rows | every metric on the f_incentive above_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.f_incentive_high.auc_gap` | `c847bcca` | scalar | 0.01874804418 | how far AUC on the f_incentive above_median slice of vintage_holdout falls below AUC on all of vintage_holdout |
| `metrics.vintage_holdout.sub.f_incentive_high.mean_rel_gap` | `b3815f8c` | scalar | 0.2975984466 | mean predicted against observed on the f_incentive above_median slice of vintage_holdout, relative |
| `metrics.vintage_holdout.sub.f_incentive_high.share` | `f4a76ad4` | scalar | 0.499984461 | the share of vintage_holdout the f_incentive above_median slice holds |
| `metrics.vintage_holdout.sub.f_incentive_low` | `c916cc71` | table | table, 10 rows | every metric on the f_incentive below_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.f_incentive_low.auc` | `fa61514e` | scalar | 0.6723509624 | auc on the f_incentive below_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.f_incentive_low.auc_gap` | `94bab5c0` | scalar | 0.09944645103 | how far AUC on the f_incentive below_median slice of vintage_holdout falls below AUC on all of vintage_holdout |
| `metrics.vintage_holdout.sub.f_incentive_low.mean_rel_gap` | `2f10187b` | scalar | 0.2421532582 | mean predicted against observed on the f_incentive below_median slice of vintage_holdout, relative |
| `metrics.vintage_holdout.sub.f_incentive_low.share` | `b86413de` | scalar | 0.500015539 | the share of vintage_holdout the f_incentive below_median slice holds |
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
| `run.features` | `0b1995f4` | json | json | the subject's features.json |
| `run.model_summary` | `22858a09` | json | json | the subject's model_summary.json |
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
| `threshold.O1.slice_auc_gap` | `0a827b87` | scalar | 0.08 | how far a sub-population's AUC may fall below the split's before the result is an open item; it raises no candidate |
| `threshold.O1.slice_max_share` | `a928a05c` | scalar | 0.95 | the share of a split at which a sub-population is the whole split and is refused |
| `threshold.O1.slice_min_share` | `9a6f1a87` | scalar | 0.1 | the share of a split a sub-population must hold before it can raise an open item |
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
| tool calls | 19 (run_model 1, profile_data 1, compute_metrics 5, check_leakage 1, check_stability 1, check_collinearity 1, challenger_compare 1, run_scenarios 1, retrieve_guidance 7) |
| plan steps (bounded loop) | 4 |
| LLM calls | 20 (plan 4, draft 8, extract 8) |
| re-asks | 0 |
| repair rounds | 1 |
| tokens in / out | 345,763 / 124,601 |
| notional cost (USD) | 6.6505 |
| wall-clock (s) | 1325.39 |
| subject run (s) | 2.45 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | msr_prepayment-full_agent-20260920T005827Z-e61d346a |

## Appendix D — Not checked

| item | reason |
|---|---|
| developer claims (T1, claim channel) | The package declares 3 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
