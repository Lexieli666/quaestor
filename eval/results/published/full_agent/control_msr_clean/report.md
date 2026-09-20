---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: msr_prepayment
version: "1.0"
model_type: discrete_time_hazard
configuration: full_agent
model: claude-opus-5[1m]
run_id: msr_prepayment-full_agent-20260919T040539Z-e61d346a
data_mode: synthetic
synthetic_n: 2000
grounding_precision_pre: 0.9968
grounding_precision_post: 1.0000
n_claims: 316
n_findings_by_severity: {high: 0, medium: 0, low: 0, info: 0}
generated: "2026-09-19T04:05:39Z"
illustrative: false
---

# Validation report — `msr_prepayment` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `msr_prepayment` v1.0 | `full_agent` | claude-opus-5[1m] | synthetic, n = 2000 | 0.9968 → 1.0000 | 0 / 0 / 0 / 0 |
<!-- quaestor:renderer:end -->

The subject of this validation is the msr_prepayment model package, a scoring model that estimates the probability that a serviced loan prepays, and this report follows the structure of the Federal Reserve's model risk management guidance on model validation and monitoring [[reg:SR26-2:V]].

The subject was executed by quaestor, which scored each split from the packaged artifact and independently recomputed every metric reported here, under the wall-clock cap of 300 [[art:2ad8d1a5:runtime.max_seconds]] seconds the package declares for itself.
The development split holds 36013 [[art:6fdfeabb:metrics.train.n]] rows, the test split 15382 [[art:e55953e1:metrics.test.n]] rows, the out-of-time split 12257 [[art:7898809e:metrics.out_of_time.n]] rows, and the vintage holdout 32177 [[art:37a92951:metrics.vintage_holdout.n]] rows.

The model clears each threshold the developer declared, on the split each was declared for.
Discrimination on test is 0.7753 [[art:57066271:metrics.test.auc]], above the declared floor of 0.65 [[art:fececac1:threshold.package.auc.test.min]].
The calibration slope on test is 0.9365 [[art:3e42ee62:calibration_slope.test]], inside the declared band running from 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] up to 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The largest train-to-test population stability index, the score itself included, is 0.06189 [[art:c2e8c8fd:psi.max]], below the declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].

Beyond the declared bounds, discrimination holds broadly steady away from the development sample, at 0.7883 [[art:fa609ae1:metrics.train.auc]] on train, 0.7846 [[art:6f2a2d99:metrics.out_of_time.auc]] out of time, and 0.7718 [[art:ac6794c5:metrics.vintage_holdout.auc]] on the vintage holdout.
Calibration is a different matter across splits: the slope is 0.9937 [[art:534cb102:calibration_slope.train]] on train and 0.9969 [[art:a49b2789:calibration_slope.out_of_time]] out of time, but 0.8373 [[art:08d6b321:calibration_slope.vintage_holdout]] on the vintage holdout, the lowest of the slopes reported here.
Discrimination is also uneven across sub-populations, and the widest shortfall reported here is on the below-median incentive slice of the vintage holdout, whose AUC of 0.6724 [[art:0510c841:metrics.vintage_holdout.sub.incentive_low.auc]] sits below the AUC on all of that split by an absolute difference of 0.09945 [[art:9de83338:metrics.vintage_holdout.sub.incentive_low.auc_gap]].
The challenger benchmark does not beat the champion on test, its AUC differing from the champion's by -0.04155 [[art:4d28c096:challenger.delta_auc]].

No finding was raised by this validation.

## 2. Conceptual soundness

Validating conceptual soundness means assessing and documenting the design, construction and developmental evidence behind the model, using interpretability measures and benchmarking against alternatives where those are the more practical tests [[reg:SR26-2:V.1.a]].

### Design and feature timing

The champion is a coefficient-per-feature linear-index model for a binary prepayment outcome, fitted with an intercept of -5.502 [[art:b764932a:run.model_summary#intercept]] on 36013 [[art:b764932a:run.model_summary#n_train]] loan-month records drawn from 934 [[art:b764932a:run.model_summary#n_train_loans]] loans, with loan age entered through spline basis terms rather than a single slope.
The feature manifest carries 12 [[art:61276a96:run.features#n]] features in total.
Of these, 5 [[art:61276a96:run.features#at_origination]] are known at origination and 7 [[art:61276a96:run.features#before_period_start]] are known before the start of the performance period.
None are labelled as observed during the period, at 0 [[art:61276a96:run.features#during_period]], and none as observed after the outcome, at 0 [[art:61276a96:run.features#after_outcome]].
On the timing labels as declared, then, every input is knowable before the period whose outcome the model predicts, which is the design property that rules out look-ahead in the feature set.

### The model's own screen

The developer applied a collinearity screen with a variance inflation cut-off of 10 [[art:b764932a:run.model_summary#vif_threshold]].
The twelve-month rate change feature was dropped at an inflation factor of 12.38 [[art:b764932a:run.model_summary#removed.rate_change_12m.vif]], marginally above that cut-off.
The log beginning-of-month balance feature was dropped at an inflation factor of 40090 [[art:b764932a:run.model_summary#removed.bom_balance_log.vif]], which is not a marginal exceedance but a near-exact linear dependence on the terms retained, most plausibly on the log original balance and the loan age spline that together determine amortised balance.
Removing that feature is the right call for coefficient interpretability, and it is worth recording that the retained log original balance term now absorbs whatever balance-level effect the dropped feature carried.

### Coefficient magnitudes and expected signs

The largest coefficient in the fitted index is on the refinance incentive, at 1.253 [[art:b764932a:run.model_summary#coefficients.incentive.value]], which is the sign and the prominence subject matter expects: borrowers prepay when the market rate sits below their note rate.
The leading loan age spline term, at 0.6491 [[art:b764932a:run.model_summary#coefficients.loan_age_spline_1.value]], carries the early ramp in prepayment speed after origination, and the terminal spline term, at -0.2386 [[art:b764932a:run.model_summary#coefficients.loan_age_spline_4.value]], bends the curve back down at longer seasoning, which is the seasoning shape the subject matter expects.
The note rate coefficient, at -0.4457 [[art:b764932a:run.model_summary#coefficients.note_rate.value]], is the largest remaining term and is discussed below.
Credit score enters at 0.4074 [[art:b764932a:run.model_summary#coefficients.credit_score.value]] and log original balance at 0.3036 [[art:b764932a:run.model_summary#coefficients.orig_upb_log.value]], both positive, consistent with the expectation that stronger borrowers and larger balances refinance more readily.
Original loan-to-value enters at -0.243 [[art:b764932a:run.model_summary#coefficients.orig_ltv.value]], negative, consistent with the expectation that thinner equity impedes refinancing.
The spread at origination enters at 0.01282 [[art:b764932a:run.model_summary#coefficients.sato.value]] and the seasonal pair at 0.0702 [[art:b764932a:run.model_summary#coefficients.season_sin.value]] and -0.1239 [[art:b764932a:run.model_summary#coefficients.season_cos.value]], all small relative to the incentive term.
Burnout enters at 0.07952 [[art:b764932a:run.model_summary#coefficients.burnout.value]], and a positive sign here runs against the usual prepayment intuition that pools repeatedly exposed to refinancing opportunity respond less to the next one; the term is small and, as noted below, its own univariate direction on train is positive too, so the fitted sign is following the data rather than contradicting it.

### Fitted signs against univariate directions

The sign comparison covers the retained features and reports disagreement between the fitted sign and the univariate direction for 1 [[art:f96ece96:sign_check.n_disagreements]] of them.
That feature is the note rate: the fitted coefficient has sign -1 [[art:aecf7ccb:sign_check.note_rate.coef_sign]] while its own single-feature relationship with the outcome on train has sign 1 [[art:61f6e1ac:sign_check.note_rate.univariate_direction]], and the agreement indicator is accordingly 0 [[art:a453463d:sign_check.note_rate.agrees]].
The reading is mechanical rather than alarming: the refinance incentive is itself built from the note rate against the prevailing market rate, so once incentive is in the index the note rate coefficient is a partial effect holding incentive fixed, and its sign need not match the marginal relationship.
The measure of how much this disagreement matters is the ablation delta on that feature, which is -0.002585 [[art:14558b82:ablation.note_rate.delta_auc]], a small loss of discrimination when the note rate is dropped and refitted, far smaller in magnitude than the loss on the incentive term at -0.04117 [[art:78108590:ablation.incentive.delta_auc]].
A sign inversion on a term the model leans on lightly is a weaker signal about conceptual soundness than one on a term it depends on, and this is the former; it remains worth carrying in the limitations the model is used under, because the note rate coefficient should not be read on its own as a statement about how note rate drives prepayment.
Every other checked feature agrees, with agreement indicators of 1 for the incentive [[art:f7b2338e:sign_check.incentive.agrees]], credit score [[art:915bf8eb:sign_check.credit_score.agrees]], log original balance [[art:07a9d3e6:sign_check.orig_upb_log.agrees]], original loan-to-value [[art:7021aeb0:sign_check.orig_ltv.agrees]], spread at origination [[art:2401eba2:sign_check.sato.agrees]], burnout [[art:2eec20ab:sign_check.burnout.agrees]], and the two seasonal terms [[art:e110f357:sign_check.season_sin.agrees]] [[art:7f18ddf7:sign_check.season_cos.agrees]].
The underlying pairs are consistent in each of those cases, for instance the fitted sign of 1 [[art:684cf11a:sign_check.incentive.coef_sign]] on the incentive against its univariate direction of 1 [[art:8098d951:sign_check.incentive.univariate_direction]], and the fitted sign of -1 [[art:7eec65ec:sign_check.orig_ltv.coef_sign]] on original loan-to-value against its univariate direction of -1 [[art:76dbc708:sign_check.orig_ltv.univariate_direction]].

### What each feature contributes

Ablation refits the champion's functional form without one feature at a time, measured against a refit on all retained features that scores 0.7673 [[art:54367df6:ablation.baseline_auc]] on test.
The incentive term is where the discrimination lives, at -0.04117 [[art:78108590:ablation.incentive.delta_auc]], followed by log original balance at -0.01927 [[art:0ddb11a9:ablation.orig_upb_log.delta_auc]] and credit score at -0.01474 [[art:9bdeb0df:ablation.credit_score.delta_auc]].
Original loan-to-value contributes -0.002294 [[art:57ea66c5:ablation.orig_ltv.delta_auc]] and the note rate -0.002585 [[art:14558b82:ablation.note_rate.delta_auc]], an order of standing well below the leading three.
The seasonal terms and burnout are close to inert on this measure, at -0.0004826 [[art:a288439d:ablation.season_cos.delta_auc]], -0.0003885 [[art:e54c8581:ablation.season_sin.delta_auc]] and -0.0001876 [[art:3cba039b:ablation.burnout.delta_auc]].
Two features have positive deltas, meaning test AUC rose slightly when they were dropped and the form refitted: loan age at 0.0008166 [[art:be669163:ablation.loan_age.delta_auc]] and the spread at origination at 0.0005201 [[art:57703504:ablation.sato.delta_auc]].
Those two are small movements at the scale of the seasonal terms, and a positive delta on loan age does not mean seasoning is irrelevant to prepayment, only that on this test set the spline terms are not buying discrimination beyond what incentive and balance already provide.
The design carries several terms whose retention rests on subject matter reasoning rather than on measured test discrimination, which is a defensible choice for a prepayment model that must behave sensibly out of the fitted range, but one that should be stated as such in the model documentation rather than implied by their presence.

### Effective challenge

The benchmark comparison sets the champion's recomputed test AUC of 0.7753 [[art:57066271:metrics.test.auc]] against the challenger's 0.7337 [[art:705b66f0:challenger.auc]].
The reported difference, the challenger's AUC on test less the champion's, is -0.04155 [[art:4d28c096:challenger.delta_auc]].
The threshold that decides whether the comparison matters is a challenger lead over the champion of 0.03 [[art:e042774c:threshold.E1.delta_auc]] in AUC, and the observed difference is negative, so the challenger does not lead at all and the threshold is not approached from the side that would trigger it.
On the probability scale the ordering is the same: the champion's Brier score of 0.007894 [[art:7d3583cd:metrics.test.brier]] is below the challenger's 0.00863 [[art:85a89ef9:challenger.brier]], and lower is better for that measure, so the champion is the more accurate of the two on both discrimination and calibrated accuracy.
Effective challenge here is therefore satisfied in the narrow sense that an alternative was built, scored on the same test data and lost on both metrics, and the deciding threshold was declared in advance of the comparison rather than fitted to it.
The weaker part of the challenge is qualitative rather than numeric: a single benchmark that loses does not probe the choices most open to question in this design, namely the spline placement in loan age and the collinearity between the incentive construction and the note rate, and a future validation cycle would gain more from a challenger that varies those choices than from one that loses by a wider margin.

### Judgement

The design is conceptually sound for its stated purpose: the feature timing is clean, the collinearity screen was applied with a declared cut-off and removed the one near-degenerate term, the dominant coefficients carry the signs and the relative prominence that prepayment behaviour implies, and the champion beats its benchmark on both reported test metrics.
The qualification to carry forward is interpretive rather than structural, that the note rate coefficient is a partial effect conditional on the incentive term and should not be read in isolation, and that several retained terms contribute little measured discrimination and are held on judgement.
Nothing in this section is raised as a finding.

## 3. Data integrity and drift

Sound model testing includes a critical assessment of data quality, relevance, and inputs, alongside out-of-sample and out-of-time testing [[reg:SR26-2:IV.1]].

### Missingness

The splits carry 36013 [[art:c5ebd9c9:profile.train.n]] training rows, 15382 [[art:e3abc1b8:profile.test.n]] test rows, 32177 [[art:426e712a:profile.vintage_holdout.n]] vintage-holdout rows and 12257 [[art:fa39c5cf:profile.out_of_time.n]] out-of-time rows.
The largest missing fraction is 0 [[art:050a3099:profile.train.missing.max]] in train, 0 [[art:f813848d:profile.test.missing.max]] in test, 0 [[art:329bb430:profile.vintage_holdout.missing.max]] in the vintage holdout and 0 [[art:4dafce11:profile.out_of_time.missing.max]] out of time.
The bound on the missingness gap between splits is 0.1 [[art:9cce25ea:threshold.D1.missing_gap]], and because every split's largest missing fraction sits at the same level, no split is more sparsely populated than another and the bound is nowhere approached.

### Population and characteristic stability

The comparisons below read each index as a level against the declared bound, not as a difference or a ratio between one split's index and another's.
Between train and test the largest population stability index, the score included, is 0.06189 [[art:c2e8c8fd:psi.max]], below the declared bound of 0.25 [[art:278b9016:threshold.S1.psi]], which the package restates as 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
That maximum is carried by credit_score at 0.06189 [[art:7e87527c:psi.credit_score]], with orig_upb_log at 0.04817 [[art:55030a3b:psi.orig_upb_log]], orig_ltv at 0.03617 [[art:cd1ff136:psi.orig_ltv]], sato at 0.02773 [[art:584da64f:psi.sato]], note_rate at 0.01371 [[art:ecc6adf3:psi.note_rate]], burnout at 0.004614 [[art:9dc7ecc2:psi.burnout]], incentive at 0.0009923 [[art:2da5570f:psi.incentive]], loan_age at 0.0001994 [[art:2202b157:psi.loan_age]], season_cos at 1.79e-05 [[art:addec503:psi.season_cos]] and season_sin at 2.939e-06 [[art:4d2ed98d:psi.season_sin]] all lower.
The score shifts by 0.001953 [[art:3b9dee2d:psi.y_score]] between train and test.

Against the vintage holdout the picture is different: note_rate reaches 0.6088 [[art:f281f8a7:psi.vintage_holdout.note_rate]] and incentive reaches 0.4475 [[art:5e61b6f9:psi.vintage_holdout.incentive]], both above the declared bound of 0.25 [[art:278b9016:threshold.S1.psi]], a bound stated for train against test.
The other inputs stay lower on that split: loan_age at 0.07112 [[art:6d92c48b:psi.vintage_holdout.loan_age]], burnout at 0.04749 [[art:e29067e6:psi.vintage_holdout.burnout]], orig_upb_log at 0.0404 [[art:77ec758a:psi.vintage_holdout.orig_upb_log]], credit_score at 0.03996 [[art:3498d307:psi.vintage_holdout.credit_score]], sato at 0.02989 [[art:eea64c25:psi.vintage_holdout.sato]], orig_ltv at 0.02942 [[art:d07cfb7d:psi.vintage_holdout.orig_ltv]], season_cos at 0.001288 [[art:9fe842a8:psi.vintage_holdout.season_cos]] and season_sin at 0.0007309 [[art:b0dc9745:psi.vintage_holdout.season_sin]].
The score shifts by 0.1421 [[art:3713457e:psi.vintage_holdout.y_score]] on that split, below 0.25 [[art:278b9016:threshold.S1.psi]].

Out of time the shifts are larger still: burnout reaches 2.945 [[art:7b0bbebb:psi.out_of_time.burnout]], loan_age 2.484 [[art:d6eaaaf5:psi.out_of_time.loan_age]], note_rate 0.6977 [[art:cabd371d:psi.out_of_time.note_rate]] and incentive 0.4958 [[art:42076ed1:psi.out_of_time.incentive]], each above 0.25 [[art:278b9016:threshold.S1.psi]].
The remaining inputs stay below that level: orig_upb_log at 0.07136 [[art:ac349b67:psi.out_of_time.orig_upb_log]], credit_score at 0.05988 [[art:d7249e47:psi.out_of_time.credit_score]], orig_ltv at 0.04301 [[art:3eee5db4:psi.out_of_time.orig_ltv]], season_sin at 0.02789 [[art:144e1bd9:psi.out_of_time.season_sin]], sato at 0.01299 [[art:c2233ce6:psi.out_of_time.sato]] and season_cos at 0.007524 [[art:25cf6b85:psi.out_of_time.season_cos]].
The score shifts by 0.7056 [[art:2dc61374:psi.out_of_time.y_score]] out of time, above 0.25 [[art:278b9016:threshold.S1.psi]].
So the ordering across the three comparisons is consistent for the drifting inputs: the burnout, loan_age, note_rate and incentive levels are lowest between train and test, higher against the vintage holdout, and highest out of time.

The characteristic stability indices, which attribute the shift in the linear predictor to individual inputs, top out at 0.03438 [[art:54bd75b0:csi.max]], carried by orig_ltv at 0.03438 [[art:97d51193:csi.orig_ltv]].
Behind it are note_rate at 0.01822 [[art:92901ac4:csi.note_rate]], credit_score at 0.007909 [[art:c40b4ede:csi.credit_score]], incentive at 0.005804 [[art:874ef644:csi.incentive]], orig_upb_log at 0.002969 [[art:bb919ade:csi.orig_upb_log]], sato at 0.001487 [[art:6a5f7a41:csi.sato]], burnout at 0.0009851 [[art:b2729e08:csi.burnout]], season_cos at 0.0004785 [[art:75b544aa:csi.season_cos]], season_sin at 7.624e-05 [[art:d55271d6:csi.season_sin]] and loan_age at 0 [[art:df52c920:csi.loan_age]].
The attribution is therefore concentrated in the loan-to-value and rate inputs rather than spread across the seasonal terms.

### Leakage screens

The declared timings flag no feature as measured during the period or after the outcome, at 0 [[art:742bcd24:leakage.timing.n_flagged]].
The strongest single feature reaches an AUC of 0.7239 [[art:1fe630dd:leakage.target_corr.max_single_feature_auc]], below the bound of 0.9 [[art:c29e7a34:threshold.L1.single_feature_auc]] that any one feature may reach on its own.
On identifiers, the share of test rows whose loan and period also identify a training row is 0 [[art:63d37fc5:leakage.overlap.ids]], below the declared contamination bound of 0.005 [[art:9f336eaf:threshold.L2.overlap]].
On feature vectors, the share of test rows whose values also appear in train is 0 [[art:0fec8048:leakage.overlap.features]], below the bound that arm of the rule actually applied, 0.005 [[art:1ee888c5:threshold.L2.overlap.features_effective]].
That applied bound is the larger of the declared contamination bound of 0.005 [[art:9f336eaf:threshold.L2.overlap]] and a multiple of the share of train rows whose feature values are not unique within train, which is 0 [[art:4474c227:leakage.duplicates.train]], since two different subjects writing the same discrete row is coincidence rather than contamination; here the declared bound is the one that binds.
The overall share of test rows whose feature values also appear in train is likewise 0 [[art:4c9fcd09:leakage.overlap]].
The name screen matches no feature name against the target-adjacent lexicon, at 0 [[art:407e62be:leakage.name_screen.n_matched]].

### Assessment

On missingness, contamination and target adjacency the evidence is unremarkable: the screens return at or below their respective bounds and the strongest single feature stays well short of the level at which a feature would be suspected of encoding the outcome.
The stability evidence separates sharply by split, with train against test well inside the declared bound while the vintage holdout and the out-of-time sample carry inputs and the score beyond it, which bears directly on how far test-split evidence of developmental quality can be read as evidence for those populations [[reg:SR26-2:V.1.a]].

## 4. Outcomes analysis

Outcomes analysis compares model outputs with the corresponding real-world outcomes, and sound validation practice reviews that comparison for reasonableness and appropriateness against the model's objectives and business use [[reg:SR26-2:V.1.b]].

This section reports calibration before discrimination.

The ordering follows from the declared use: package.yaml declares that this model's output is consumed as a probability and not only as a ranking, so whether the probabilities mean what they say is the leading question, whatever the event rate on a given split happens to be.

### Calibration

On test, the logistic regression of the outcome on logit(p) returns a slope of 0.9365 [[art:3e42ee62:calibration_slope.test]] and an intercept of -0.277 [[art:e87b5c13:calibration_intercept.test]].

On train, the same regression returns a slope of 0.9937 [[art:534cb102:calibration_slope.train]] and an intercept of -0.01454 [[art:11d7a3ca:calibration_intercept.train]].

On the out-of-time split, the slope is 0.9969 [[art:a49b2789:calibration_slope.out_of_time]] and the intercept is -0.06272 [[art:fc7ece3a:calibration_intercept.out_of_time]].

On the vintage holdout, the slope is 0.8373 [[art:08d6b321:calibration_slope.vintage_holdout]] and the intercept is -0.9028 [[art:44715143:calibration_intercept.vintage_holdout]], the lowest slope and the most negative intercept among the splits reported here.

The declared band for the slope runs from 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] to 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]], and every slope reported above lies inside that band, with the vintage holdout value nearest the lower edge.

Mean predicted probability on test is 0.008116 [[art:3bc93911:metrics.test.mean_predicted]] against an observed event rate of 0.008061 [[art:570cc08a:metrics.test.event_rate]], a relative gap of 0.006755 [[art:59b8a1f5:calibration.mean_rel_gap.test]].

Mean predicted probability on train is 0.008427 [[art:a63f6555:metrics.train.mean_predicted]] against an observed rate of 0.008525 [[art:b9ef3327:metrics.train.event_rate]], a relative gap of 0.01152 [[art:e28c45a9:calibration.mean_rel_gap.train]].

Out of time, mean predicted is 0.01887 [[art:3833e0c5:metrics.out_of_time.mean_predicted]] against an observed rate of 0.01795 [[art:83ccf5c0:metrics.out_of_time.event_rate]], a relative gap of 0.05109 [[art:c599bd89:calibration.mean_rel_gap.out_of_time]].

On the vintage holdout, mean predicted is 0.005647 [[art:5ae28866:metrics.vintage_holdout.mean_predicted]] against an observed rate of 0.004817 [[art:e3590a16:metrics.vintage_holdout.event_rate]], a relative gap of 0.1722 [[art:55a672c2:calibration.mean_rel_gap.vintage_holdout]].

The tolerance applied to that relative gap is 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]], and each split-level gap reported above sits below it, the vintage holdout gap being the largest and the closest to it.

The mean absolute difference between actual and predicted CPR is 0.02658 [[art:f2c3683c:cpr.train.mae]] on train, 0.04264 [[art:ff266c97:cpr.test.mae]] on test, 0.05857 [[art:a7ecd72b:cpr.out_of_time.mae]] out of time, and 0.0289 [[art:172ebed4:cpr.vintage_holdout.mae]] on the vintage holdout.

The decile view of calibration on test and the period-by-period CPR comparison follow.

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

### Discrimination

Discrimination, recomputed on every split, reads as follows.

| Metric | train | test | out_of_time | vintage_holdout |
| --- | --- | --- | --- | --- |
| AUC | 0.7883 [[art:fa609ae1:metrics.train.auc]] | 0.7753 [[art:57066271:metrics.test.auc]] | 0.7846 [[art:6f2a2d99:metrics.out_of_time.auc]] | 0.7718 [[art:ac6794c5:metrics.vintage_holdout.auc]] |
| Gini | 0.5767 [[art:0b6b2058:metrics.train.gini]] | 0.5505 [[art:fe7f75d7:metrics.test.gini]] | 0.5691 [[art:890252d7:metrics.out_of_time.gini]] | 0.5436 [[art:a4a532f0:metrics.vintage_holdout.gini]] |
| KS | 0.4562 [[art:c355478b:metrics.train.ks]] | 0.4162 [[art:c569c301:metrics.test.ks]] | 0.4321 [[art:16d3e4fe:metrics.out_of_time.ks]] | 0.4516 [[art:b5b9e888:metrics.vintage_holdout.ks]] |
| Brier | 0.008317 [[art:83666c70:metrics.train.brier]] | 0.007894 [[art:7d3583cd:metrics.test.brier]] | 0.01713 [[art:40d244d4:metrics.out_of_time.brier]] | 0.004763 [[art:f3c6bdcc:metrics.vintage_holdout.brier]] |
| Log loss | 0.04408 [[art:199c7db5:metrics.train.logloss]] | 0.04263 [[art:320e4c6b:metrics.test.logloss]] | 0.07975 [[art:2b7c9b2d:metrics.out_of_time.logloss]] | 0.02811 [[art:c32e3713:metrics.vintage_holdout.logloss]] |
| Top-decile-pair event capture | 0.5961 [[art:e8dd0c53:deciles.train.top2_capture]] | 0.5806 [[art:43c4adc5:deciles.test.top2_capture]] | 0.5773 [[art:df63152b:deciles.out_of_time.top2_capture]] | 0.5871 [[art:8b59f312:deciles.vintage_holdout.top2_capture]] |
| Rows | 36013 [[art:6fdfeabb:metrics.train.n]] | 15382 [[art:e55953e1:metrics.test.n]] | 12257 [[art:7898809e:metrics.out_of_time.n]] | 32177 [[art:37a92951:metrics.vintage_holdout.n]] |

Test AUC of 0.7753 [[art:57066271:metrics.test.auc]] sits below train AUC of 0.7883 [[art:fa609ae1:metrics.train.auc]], and the bound declared for that train-to-test gap is 0.08 [[art:630f28f4:threshold.O1.auc_gap]], which the separation between those recomputed values stays inside.

The declared AUC floor for test is 0.65 [[art:fececac1:threshold.package.auc.test.min]], below which no recomputed split AUC in the table falls.

The decile separation on test, where decile 1 holds the highest predicted probabilities, is reported below.

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

<!-- quaestor:renderer:begin table thresholds.evaluation -->
Every threshold package.yaml declares, with its bound, the recomputed value and the outcome [[art:f71ddec9:thresholds.evaluation]]:

| metric | split | bound | value | result |
|---|---|---|---|---|
| auc | test | minimum 0.65 | 0.7753 | pass |
| calibration_slope | test | minimum 0.8 | 0.9365 | pass |
| calibration_slope | test | maximum 1.2 | 0.9365 | pass |
| psi |  | maximum 0.25 | 0.06189 | pass |
<!-- quaestor:renderer:end -->

The table sets each bound package.yaml declares beside the value recomputed against it and the outcome the tool recorded, so it cannot disagree with the figures reported above.

The calibration slope band from 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] to 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]], the AUC floor of 0.65 [[art:fececac1:threshold.package.auc.test.min]] and the stability bound of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]] are the developer's own, and the table shows how the recomputed values stand against them.

### Follow-up analyses

A step recomputed the full metric set on the sub-population `incentive > median(incentive)`, on every split.

It was asked because the split-level numbers passed while a prepayment hazard most plausibly mis-ranks or mis-calibrates where refinance incentive is strongest, which aggregation over the whole split would average away.

<!-- quaestor:renderer:begin table metrics.train.sub.incentive_high -->
Every metric on the incentive above_median slice of train [[art:58071691:metrics.train.sub.incentive_high]]:

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

<!-- quaestor:renderer:begin table metrics.test.sub.incentive_high -->
Every metric on the incentive above_median slice of test [[art:142c806c:metrics.test.sub.incentive_high]]:

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

<!-- quaestor:renderer:begin table metrics.out_of_time.sub.incentive_high -->
Every metric on the incentive above_median slice of out_of_time [[art:6c7182e4:metrics.out_of_time.sub.incentive_high]]:

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

<!-- quaestor:renderer:begin table metrics.vintage_holdout.sub.incentive_high -->
Every metric on the incentive above_median slice of vintage_holdout [[art:672368b3:metrics.vintage_holdout.sub.incentive_high]]:

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

On train, this sub-population's AUC falls below the split's own by 0.07016 [[art:8d8827f2:metrics.train.sub.incentive_high.auc_gap]], on a share of 0.5 [[art:277218fb:metrics.train.sub.incentive_high.share]] of that split.

On test, the shortfall is 0.0484 [[art:5a0ba9c4:metrics.test.sub.incentive_high.auc_gap]], on a share of 0.5 [[art:549aa934:metrics.test.sub.incentive_high.share]].

Out of time, the shortfall is 0.03734 [[art:1c0207f9:metrics.out_of_time.sub.incentive_high.auc_gap]], on a share of 0.4999 [[art:431d1ff2:metrics.out_of_time.sub.incentive_high.share]].

On the vintage holdout, the shortfall is 0.01875 [[art:2ebd6757:metrics.vintage_holdout.sub.incentive_high.auc_gap]], on a share of 0.5 [[art:cb627056:metrics.vintage_holdout.sub.incentive_high.share]].

Those shortfalls are read against a bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] and the shares against a floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]]; each shortfall here is below that bound and each share above that floor.

Mean predicted against observed on this sub-population is 0.01445 [[art:7d3d3639:metrics.train.sub.incentive_high.mean_rel_gap]] on train, 0.03492 [[art:f90b2790:metrics.test.sub.incentive_high.mean_rel_gap]] on test, 0.1235 [[art:f0899b32:metrics.out_of_time.sub.incentive_high.mean_rel_gap]] out of time and 0.2976 [[art:d14397a7:metrics.vintage_holdout.sub.incentive_high.mean_rel_gap]] on the vintage holdout.

On the vintage holdout that relative gap stands above the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]] while the AUC shortfall there stays below its bound, so what weakens on that split is the level of the probabilities rather than their ordering.

A step recomputed the same metric set on the complement sub-population `incentive <= median(incentive)`.

It was asked so that the above-median incentive numbers could be judged against the out-of-the-money population rather than against the split alone.

<!-- quaestor:renderer:begin table metrics.train.sub.incentive_low -->
Every metric on the incentive below_median slice of train [[art:9c590135:metrics.train.sub.incentive_low]]:

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

<!-- quaestor:renderer:begin table metrics.test.sub.incentive_low -->
Every metric on the incentive below_median slice of test [[art:53406e16:metrics.test.sub.incentive_low]]:

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

<!-- quaestor:renderer:begin table metrics.out_of_time.sub.incentive_low -->
Every metric on the incentive below_median slice of out_of_time [[art:1ebd5e5e:metrics.out_of_time.sub.incentive_low]]:

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

<!-- quaestor:renderer:begin table metrics.vintage_holdout.sub.incentive_low -->
Every metric on the incentive below_median slice of vintage_holdout [[art:10caac80:metrics.vintage_holdout.sub.incentive_low]]:

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

On train, this sub-population's AUC falls below the split's own by 0.06703 [[art:134d7c07:metrics.train.sub.incentive_low.auc_gap]], on a share of 0.5 [[art:d7af12f0:metrics.train.sub.incentive_low.share]], below the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] and above the share floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].

On test, the shortfall is 0.09283 [[art:a0523ad8:metrics.test.sub.incentive_low.auc_gap]], on a share of 0.5 [[art:1d5dd4c2:metrics.test.sub.incentive_low.share]], and that shortfall stands above the same bound.

Out of time, the shortfall is 0.0163 [[art:faa1a185:metrics.out_of_time.sub.incentive_low.auc_gap]], on a share of 0.5001 [[art:c7aaafd2:metrics.out_of_time.sub.incentive_low.share]], below the bound.

On the vintage holdout, the shortfall is 0.09945 [[art:9de83338:metrics.vintage_holdout.sub.incentive_low.auc_gap]], on a share of 0.5 [[art:d94e6531:metrics.vintage_holdout.sub.incentive_low.share]], and it too stands above the bound.

Mean predicted against observed on this sub-population is 0.003953 [[art:05adce6c:metrics.train.sub.incentive_low.mean_rel_gap]] on train, 0.1169 [[art:aede705c:metrics.test.sub.incentive_low.mean_rel_gap]] on test, 0.2155 [[art:81d9f6b7:metrics.out_of_time.sub.incentive_low.mean_rel_gap]] out of time and 0.2422 [[art:20691619:metrics.vintage_holdout.sub.incentive_low.mean_rel_gap]] on the vintage holdout, each below the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]].

On test and on the vintage holdout, then, the relative level of the probabilities holds inside its tolerance while the AUC shortfall passes its bound, which points to the ordering within this sub-population rather than to the level of its probabilities.

A step recomputed the metric set on the sub-population `burnout > median(burnout)`.

It was asked because the incentive sub-populations held up and high-burnout loans are the other classic weak spot, where a hazard model's discrimination and calibration most often degrade.

<!-- quaestor:renderer:begin table metrics.train.sub.burnout_high -->
Every metric on the burnout above_median slice of train [[art:66fd45a2:metrics.train.sub.burnout_high]]:

| metric | value |
|---|---|
| n | 18006 |
| event_rate | 0.01311 |
| auc | 0.7514 |
| gini | 0.5028 |
| ks | 0.3726 |
| brier | 0.01273 |
| logloss | 0.06407 |
| mean_predicted | 0.01312 |
| mean_rel_gap | 0.0009105 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.burnout_high -->
Every metric on the burnout above_median slice of test [[art:92eab39d:metrics.test.sub.burnout_high]]:

| metric | value |
|---|---|
| n | 7691 |
| event_rate | 0.01248 |
| auc | 0.7244 |
| gini | 0.4489 |
| ks | 0.3471 |
| brier | 0.01218 |
| logloss | 0.06285 |
| mean_predicted | 0.01257 |
| mean_rel_gap | 0.006956 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.out_of_time.sub.burnout_high -->
Every metric on the burnout above_median slice of out_of_time [[art:322f57c1:metrics.out_of_time.sub.burnout_high]]:

| metric | value |
|---|---|
| n | 6128 |
| event_rate | 0.01942 |
| auc | 0.7765 |
| gini | 0.553 |
| ks | 0.4329 |
| brier | 0.01855 |
| logloss | 0.08614 |
| mean_predicted | 0.0256 |
| mean_rel_gap | 0.3184 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.vintage_holdout.sub.burnout_high -->
Every metric on the burnout above_median slice of vintage_holdout [[art:bf16f833:metrics.vintage_holdout.sub.burnout_high]]:

| metric | value |
|---|---|
| n | 16088 |
| event_rate | 0.007583 |
| auc | 0.7337 |
| gini | 0.4674 |
| ks | 0.3532 |
| brier | 0.007474 |
| logloss | 0.04204 |
| mean_predicted | 0.007987 |
| mean_rel_gap | 0.05321 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

On train, its AUC falls below the split's own by 0.03694 [[art:c5d72bde:metrics.train.sub.burnout_high.auc_gap]], on a share of 0.5 [[art:31040ed8:metrics.train.sub.burnout_high.share]].

On test, the shortfall is 0.05082 [[art:9dce50b2:metrics.test.sub.burnout_high.auc_gap]], on a share of 0.5 [[art:ec1e0d04:metrics.test.sub.burnout_high.share]].

Out of time, the shortfall is 0.008043 [[art:fc407765:metrics.out_of_time.sub.burnout_high.auc_gap]], on a share of 0.5 [[art:b5c30bbc:metrics.out_of_time.sub.burnout_high.share]].

On the vintage holdout, the shortfall is 0.0381 [[art:b2bfad0a:metrics.vintage_holdout.sub.burnout_high.auc_gap]], on a share of 0.5 [[art:379549be:metrics.vintage_holdout.sub.burnout_high.share]].

Each of those shortfalls is below the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] and each share is above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].

Mean predicted against observed on this sub-population is 0.0009105 [[art:7b4ba231:metrics.train.sub.burnout_high.mean_rel_gap]] on train, 0.006956 [[art:da3a2aa8:metrics.test.sub.burnout_high.mean_rel_gap]] on test, 0.3184 [[art:56cf9db6:metrics.out_of_time.sub.burnout_high.mean_rel_gap]] out of time and 0.05321 [[art:f497ef02:metrics.vintage_holdout.sub.burnout_high.mean_rel_gap]] on the vintage holdout.

Out of time that relative gap stands above the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]] while the AUC shortfall on the same split is the smallest recorded for this sub-population, so the weakness there is in the level of the probabilities and not in their ordering.

A step recomputed the metric set on the complement sub-population `burnout <= median(burnout)`.

It was asked to complete the burnout partition, so that the above-median numbers have their complement to be judged against.

<!-- quaestor:renderer:begin table metrics.train.sub.burnout_low -->
Every metric on the burnout below_median slice of train [[art:b3d9b1ff:metrics.train.sub.burnout_low]]:

| metric | value |
|---|---|
| n | 18007 |
| event_rate | 0.003943 |
| auc | 0.75 |
| gini | 0.5 |
| ks | 0.4354 |
| brier | 0.003905 |
| logloss | 0.0241 |
| mean_predicted | 0.003735 |
| mean_rel_gap | 0.05282 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.test.sub.burnout_low -->
Every metric on the burnout below_median slice of test [[art:4faad122:metrics.test.sub.burnout_low]]:

| metric | value |
|---|---|
| n | 7691 |
| event_rate | 0.003641 |
| auc | 0.7435 |
| gini | 0.4871 |
| ks | 0.4061 |
| brier | 0.003603 |
| logloss | 0.02241 |
| mean_predicted | 0.003663 |
| mean_rel_gap | 0.006065 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.out_of_time.sub.burnout_low -->
Every metric on the burnout below_median slice of out_of_time [[art:f6714bf8:metrics.out_of_time.sub.burnout_low]]:

| metric | value |
|---|---|
| n | 6129 |
| event_rate | 0.01648 |
| auc | 0.8102 |
| gini | 0.6205 |
| ks | 0.4794 |
| brier | 0.01571 |
| logloss | 0.07337 |
| mean_predicted | 0.01213 |
| mean_rel_gap | 0.2638 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

<!-- quaestor:renderer:begin table metrics.vintage_holdout.sub.burnout_low -->
Every metric on the burnout below_median slice of vintage_holdout [[art:ba6fbd31:metrics.vintage_holdout.sub.burnout_low]]:

| metric | value |
|---|---|
| n | 16089 |
| event_rate | 0.002051 |
| auc | 0.7459 |
| gini | 0.4917 |
| ks | 0.4584 |
| brier | 0.002053 |
| logloss | 0.01418 |
| mean_predicted | 0.003307 |
| mean_rel_gap | 0.6123 |
| share | 0.5 |
<!-- quaestor:renderer:end -->

On train, its AUC falls below the split's own by 0.03835 [[art:7a5c3299:metrics.train.sub.burnout_low.auc_gap]], on a share of 0.5 [[art:9d770878:metrics.train.sub.burnout_low.share]].

On test, the shortfall is 0.03172 [[art:acc515db:metrics.test.sub.burnout_low.auc_gap]], on a share of 0.5 [[art:2cb9dc34:metrics.test.sub.burnout_low.share]].

Out of time, the recorded shortfall is -0.02568 [[art:36fd04a3:metrics.out_of_time.sub.burnout_low.auc_gap]], on a share of 0.5 [[art:d6102b4a:metrics.out_of_time.sub.burnout_low.share]], which is to say its AUC stands above the split's own rather than below it.

On the vintage holdout, the shortfall is 0.02593 [[art:180537c0:metrics.vintage_holdout.sub.burnout_low.auc_gap]], on a share of 0.5 [[art:b327a747:metrics.vintage_holdout.sub.burnout_low.share]].

Each of those values is below the bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] and each share is above the floor of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]].

Mean predicted against observed on this sub-population is 0.05282 [[art:c979f2dc:metrics.train.sub.burnout_low.mean_rel_gap]] on train, 0.006065 [[art:6ef3aca5:metrics.test.sub.burnout_low.mean_rel_gap]] on test, 0.2638 [[art:fc98bff4:metrics.out_of_time.sub.burnout_low.mean_rel_gap]] out of time and 0.6123 [[art:508e2e1f:metrics.vintage_holdout.sub.burnout_low.mean_rel_gap]] on the vintage holdout, the largest relative gap recorded anywhere in these follow-ups.

Out of time and on the vintage holdout those relative gaps stand above the tolerance of 0.25 [[art:20e93a8c:threshold.C1.mean_ratio_rel]] while the corresponding AUC shortfalls stay below their bound, so on those splits it is the level of the probabilities on this sub-population, not their ordering, that carries the weakness.

## 5. Sensitivity and scenario analysis

Sound practice subjects a model's design and the quality and extent of its developmental evidence to critical analysis [[reg:SR26-2:V.1.a]], and the tests below do that by examining how the retained specification and its outputs respond to correlated inputs, to a change of rate regime, and to parallel rate shocks.
The superseded guidance is the more explicit of the two on the point that sensitivity analysis and stress testing should reach extreme values in order to establish the boundaries of model performance [[reg:SR11-7:V.1.a]], and that is the standard applied to the shock grid here.
Each family of checks named for this section bears on a model of this type: the design is estimated on a set of retained numeric features, the package declares a rate regime column, and the servicing value is repriced across a grid of parallel shocks.
Nothing reported below is drawn from a check that Appendix D lists as outside the scope of this model type, and no such check is described here as though it had been run.

### Multicollinearity among the retained features

The largest variance inflation factor across the retained features is 4.976 [[art:f9e0db60:vif.max]], below the declared tolerance of 10 [[art:aeb4f33c:threshold.M1.vif]].
That maximum belongs to the note-rate term, whose factor is 4.976 [[art:37532fa8:vif.note_rate]], with the next largest values at 3.439 [[art:88879cb2:vif.burnout]] and 2.929 [[art:5573d536:vif.loan_age]].
The remaining retained features sit lower still, down to a smallest factor of 1.004 [[art:669c5fcb:vif.season_sin]], so every retained feature falls below the declared tolerance.
Belsley's condition number of the column-standardised design is 4.943 [[art:4f06a3c5:condition_number]], well below the declared tolerance of 30 [[art:7e52fd7a:threshold.M1.condition_number]].
On both the per-feature measure and the whole-design measure, then, the retained specification sits on the comfortable side of its declared tolerance rather than near it.

### Stability across the declared regimes

The declared tolerance on the AUC difference across regimes is 0.1 [[art:b64213d7:threshold.R1.auc_gap]], and the discrimination achieved within each declared regime is set out in the table below.

<!-- quaestor:renderer:begin table stability.auc_by_regime -->
The champion's AUC within each rate_regime on train [[art:960f708f:stability.auc_by_regime]]:

| regime | n | event_rate | auc |
|---|---|---|---|
| falling | 17873 | 0.01438 | 0.7227 |
| rising | 18140 | 0.002756 | 0.7238 |
<!-- quaestor:renderer:end -->

A coefficient sign change is screened as material only where the coefficient exceeds 0.05 [[art:aca84377:threshold.R1.sign_flip_coef]] in both regimes and its absolute z reaches 2 [[art:2e4428c7:threshold.R1.sign_flip_z]] in both.
No screened feature meets that condition, the indicator reading 0 [[art:0cc7a37d:stability.incentive.sign_flip]], 0 [[art:e7ce4912:stability.note_rate.sign_flip]], 0 [[art:1f302ccd:stability.sato.sign_flip]], 0 [[art:6bc05e82:stability.burnout.sign_flip]], 0 [[art:b7191217:stability.loan_age.sign_flip]], 0 [[art:d956c276:stability.credit_score.sign_flip]], 0 [[art:054d5fab:stability.orig_ltv.sign_flip]], 0 [[art:fb1ae6c8:stability.orig_upb_log.sign_flip]], 0 [[art:6ba36a3b:stability.season_sin.sign_flip]] and 0 [[art:1850e2de:stability.season_cos.sign_flip]].
The sign structure of the fitted coefficients is therefore stable across the declared regimes on the screen as the package defines it, which is a weaker statement than stability of the coefficient magnitudes themselves.

### Rate-shock scenarios

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

At the downward extreme of the grid the servicing value changes by -1298000 [[art:4829926e:scenario.value_change.-300]], and at the upward extreme it changes by 168100 [[art:38e75872:scenario.value_change.300]].
The intermediate steps run -854300 [[art:03816874:scenario.value_change.-200]], -322600 [[art:d33e8e3c:scenario.value_change.-100]], 0 [[art:1e1b0b88:scenario.value_change.0]], 119600 [[art:d0970bd9:scenario.value_change.100]] and 157000 [[art:d69c2be1:scenario.value_change.200]].
The change in value therefore rises monotonically with the shock across every step of the grid, with no reversal and no flat segment between adjacent shocks.
The sum of the change at the downward extreme and the change at the upward extreme is -1130000 [[art:538e0e09:scenario.convexity]], negative because the fall outweighs the rise.
That negative sign is the direction the package declares for this measure, and it matches the asymmetry visible in the grid itself, where the downward shocks move the value further from the base case than the upward shocks of the same size do.
The upward side also flattens as the shock grows, the increments between successive upward shocks shrinking while the downward side continues to steepen, which is the behaviour expected of servicing value when prepayment slows toward a floor.

No result reported in this section is raised as a finding.

## 6. Findings and recommendations

Findings are ordered by severity, most severe first, and each carries the recomputed artifact values and the declared bound it was read against as its evidence [[reg:SR26-2:V]].

This validation raised no finding.

Candidates raised and not promoted: none.

Checks that ran and raised no candidate: `profile_data` (D1, S1), `compute_metrics` (T1, C1, O1), `check_leakage` (L1, L2), `check_stability` (R1), `check_collinearity` (M1), `challenger_compare` (E1), `run_scenarios` (X1).

### Open items

- On the test split, where AUC over the whole split is 0.7753 [[art:57066271:metrics.test.auc]] and AUC on `incentive <= median(incentive)` is 0.6824 [[art:0f9a3d96:metrics.test.sub.incentive_low.auc]], a shortfall of 0.09283 [[art:a0523ad8:metrics.test.sub.incentive_low.auc_gap]] read against a bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] on a sub-population holding 0.5 [[art:1d5dd4c2:metrics.test.sub.incentive_low.share]] of the split against a minimum share of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]]: what does the model discriminate on within that sub-population, given that selecting on incentive also selects on everything correlated with incentive, and which signals does the model developer expect to carry the ranking there?
- On the vintage_holdout split, where AUC over the whole split is 0.7718 [[art:ac6794c5:metrics.vintage_holdout.auc]] and AUC on `incentive <= median(incentive)` is 0.6724 [[art:0510c841:metrics.vintage_holdout.sub.incentive_low.auc]], a shortfall of 0.09945 [[art:9de83338:metrics.vintage_holdout.sub.incentive_low.auc_gap]] read against a bound of 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]] on a sub-population holding 0.5 [[art:d94e6531:metrics.vintage_holdout.sub.incentive_low.share]] of the split against a minimum share of 0.1 [[art:9a6f1a87:threshold.O1.slice_min_share]]: what ranking behaviour does the model developer expect within that sub-population on this vintage, and is the narrower separation there consistent with how borrowers with little rate incentive are understood to prepay?
- The fitted coefficient on `note_rate` carries sign -1 [[art:aecf7ccb:sign_check.note_rate.coef_sign]] where that feature's own univariate direction on train is 1 [[art:61f6e1ac:sign_check.note_rate.univariate_direction]], with agreement between the two recorded as 0 [[art:a453463d:sign_check.note_rate.agrees]] and the fitted sign read against that univariate direction: which covariates does the model developer understand `note_rate` to be conditioned against in the fitted specification, such that its contribution runs opposite to the direction it shows on its own?

## 7. Ongoing monitoring recommendations

Ongoing monitoring evaluates the extent to which a model continues to perform as expected given potential changes in products, exposures, activities, clients, data relevance, or market conditions [[reg:SR26-2:V.2]].

The monitoring programme should track the same quantities this validation recomputed and compare them against the same bounds declared in the model package, so that a production reading is directly comparable with the reading reported here rather than against a separately invented tolerance.

**Calibration.** Report, for each production vintage, the slope of the logistic regression of the realized prepayment outcome on the logit of the predicted probability, evaluated against the declared lower bound of 0.8 [[art:95fdb848:threshold.package.calibration_slope.test.min]] and the declared upper bound of 1.2 [[art:0adb7a89:threshold.package.calibration_slope.test.max]].
The validation reading of 0.9365 [[art:3e42ee62:calibration_slope.test]] sits inside that band and should serve as the reference point against which production readings are read.
Because this quantity requires realized outcomes, report it on a cadence matched to the model's performance window, and refresh it each quarter once a vintage has seasoned.

**Discrimination.** Report the area under the ROC curve on each seasoned production vintage against the declared floor of 0.65 [[art:fececac1:threshold.package.auc.test.min]], with the validation reading of 0.7753 [[art:57066271:metrics.test.auc]] as the reference point, on the same quarterly cadence as the calibration slope.

**Input and score stability.** Report the population stability index of the score and of each model input, computed from the development distribution to the current production vintage, against the declared ceiling of 0.25 [[art:fbb5a9d1:threshold.package.psi.max]].
The largest such reading in this validation was 0.06189 [[art:c2e8c8fd:psi.max]], well below that ceiling, so a production reading approaching the ceiling is a material change in the input population rather than ordinary period-to-period noise.
This quantity needs no realized outcomes and should therefore be reported monthly, which makes it the earliest of the tracked signals.

A monitoring report should present its calibration evidence before its discrimination evidence, as this report did, because the model package declares that the output is used as a probability and not only as a ranking, and a monitoring pack ordered the other way would lead with the weaker guarantee about the quantity actually consumed downstream.

This validation compared the champion against a challenger, and monitoring should add the comparison that the development data cannot supply: a benchmark against the challenger refitted on production vintages and scored against the same realized outcomes as the champion.
Refitting on production vintages is what distinguishes this from the comparison already reported, because it lets the challenger absorb any change in borrower behaviour or rate environment that the champion's fixed parameters cannot.
Where the refitted challenger calibrates or separates better than the champion on recent vintages, treat the discrepancy as a trigger to investigate its source and degree rather than as evidence in itself that the champion is in error, since the benchmark is an alternative prediction built on different data [[reg:SR11-7:V.1.b]].

Several matters fall outside what this validation could cover and should be carried by monitoring instead.
Outcomes analysis here rested on a held-out sample drawn from the development data, so back-testing against realized prepayments on vintages originated and scored in production remains for monitoring to perform [[reg:SR26-2:V.1.b]].
The development data cannot represent rate and macroeconomic regimes that had not occurred when it was assembled, so monitoring should record the prevailing regime alongside each reported reading and flag vintages scored under conditions outside the development range.
Process verification of the production implementation — input accuracy and completeness, the scoring code under change control, and the integration between upstream servicing data and downstream reporting — was not exercised by recomputation on a static extract and should be verified on the live path [[reg:SR11-7:V.1.b]].
Overrides of model output by users, including the reasons given and the subsequent performance of overridden cases, should be logged and analysed, since a persistent pattern of overrides is itself a signal that the model is not performing as intended.
Portfolio composition effects such as servicing transfers, new origination channels, and shifts in segment mix should be tracked, because they can move the population that the model is applied to without moving any single input's stability reading far.

When a tracked quantity crosses its declared bound, or drifts persistently toward it across successive vintages, escalate for outcomes analysis and consider whether an overlay, recalibration, or redevelopment is warranted under the organization's model risk policy [[reg:SR26-2:V.2]].
The scope and frequency set out above should be revisited at least annually, and sooner if the model's use, materiality, or data sources change.

## Appendix A — Claims

Grounding precision 0.9968 before repair (315 of 316 claims verified; 1 dangling) and 1.0000 after 0 claim(s) rewritten and 1 number(s) removed from the prose. Per section (post-repair): summary 21/21; conceptual_soundness 50/50; data_integrity 71/71; outcomes 123/123; sensitivity 29/29; findings 15/15; monitoring 7/7.

Developer claims: The package declares 3 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). See Appendix D.

Excluded numeric tokens (not claims): label_number (decile 1); citation_hash (2ad8d1a5, 6fdfeabb, e55953e1, 7898809e); regulatory_section_id (SR26-2:V, SR26-2:V.1.a, SR26-2:IV.1, SR26-2:V.1.b); extractor_returned_excluded_token (12.0, 1.0, 4.0, 1).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | The subject was executed by quaestor, which scored each spli… | 300 | ratio | runtime.max_seconds |  | eq | `[[art:2ad8d1a5:runtime.max_seconds]]` | verified | 300 |
| 2 | summary | The development split holds 36013 rows, the test split 15382… | 36013 | count | n | train | eq | `[[art:6fdfeabb:metrics.train.n]]` | verified | 36013 |
| 3 | summary | The development split holds 36013 rows, the test split 15382… | 15382 | count | n | test | eq | `[[art:e55953e1:metrics.test.n]]` | verified | 15382 |
| 4 | summary | The development split holds 36013 rows, the test split 15382… | 12257 | count | n | out_of_time | eq | `[[art:7898809e:metrics.out_of_time.n]]` | verified | 12257 |
| 5 | summary | The development split holds 36013 rows, the test split 15382… | 32177 | count | n | vintage_holdout | eq | `[[art:37a92951:metrics.vintage_holdout.n]]` | verified | 32177 |
| 6 | summary | Discrimination on test is 0.7753 , above the declared floor… | 0.7753 | ratio | auc | test | eq | `[[art:57066271:metrics.test.auc]]` | verified | 0.7752553922 |
| 7 | summary | Discrimination on test is 0.7753 , above the declared floor… | 0.65 | ratio | auc | test | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 8 | summary | The calibration slope on test is 0.9365 , inside the declare… | 0.9365 | ratio | calibration_slope | test | eq | `[[art:3e42ee62:calibration_slope.test]]` | verified | 0.9365180494 |
| 9 | summary | The calibration slope on test is 0.9365 , inside the declare… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 10 | summary | The calibration slope on test is 0.9365 , inside the declare… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 11 | summary | The largest train-to-test population stability index, the sc… | 0.06189 | ratio | psi |  | eq | `[[art:c2e8c8fd:psi.max]]` | verified | 0.06188985797 |
| 12 | summary | The largest train-to-test population stability index, the sc… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 13 | summary | Beyond the declared bounds, discrimination holds broadly ste… | 0.7883 | ratio | auc | train | eq | `[[art:fa609ae1:metrics.train.auc]]` | verified | 0.7883327303 |
| 14 | summary | Beyond the declared bounds, discrimination holds broadly ste… | 0.7846 | ratio | auc | out_of_time | eq | `[[art:6f2a2d99:metrics.out_of_time.auc]]` | verified | 0.7845616168 |
| 15 | summary | Beyond the declared bounds, discrimination holds broadly ste… | 0.7718 | ratio | auc | vintage_holdout | eq | `[[art:ac6794c5:metrics.vintage_holdout.auc]]` | verified | 0.7717974135 |
| 16 | summary | Calibration is a different matter across splits: the slope i… | 0.9937 | ratio | calibration_slope | train | eq | `[[art:534cb102:calibration_slope.train]]` | verified | 0.9936945557 |
| 17 | summary | Calibration is a different matter across splits: the slope i… | 0.9969 | ratio | calibration_slope | out_of_time | eq | `[[art:a49b2789:calibration_slope.out_of_time]]` | verified | 0.9969389246 |
| 18 | summary | Calibration is a different matter across splits: the slope i… | 0.8373 | ratio | calibration_slope | vintage_holdout | eq | `[[art:08d6b321:calibration_slope.vintage_holdout]]` | verified | 0.837279841 |
| 19 | summary | Discrimination is also uneven across sub-populations, and th… | 0.6724 | ratio | auc | vintage_holdout | eq | `[[art:0510c841:metrics.vintage_holdout.sub.incentive_low.auc]]` | verified | 0.6723509624 |
| 20 | summary | Discrimination is also uneven across sub-populations, and th… | 0.09945 | ratio | auc_gap | vintage_holdout | eq | `[[art:9de83338:metrics.vintage_holdout.sub.incentive_low.auc_gap]]` | verified | 0.09944645103 |
| 21 | summary | The challenger benchmark does not beat the champion on test,… | -0.04155 | ratio | delta_auc | test | eq | `[[art:4d28c096:challenger.delta_auc]]` | verified | -0.04154748012 |
| 22 | conceptual_soundness | The champion is a coefficient-per-feature linear-index model… | -5.502 | ratio | intercept |  | eq | `[[art:b764932a:run.model_summary#intercept]]` | verified | -5.502203635 |
| 23 | conceptual_soundness | The champion is a coefficient-per-feature linear-index model… | 36013 | count | n_train | train | eq | `[[art:b764932a:run.model_summary#n_train]]` | verified | 36013 |
| 24 | conceptual_soundness | The champion is a coefficient-per-feature linear-index model… | 934 | count | n_train_loans | train | eq | `[[art:b764932a:run.model_summary#n_train_loans]]` | verified | 934 |
| 25 | conceptual_soundness | The feature manifest carries 12 features in total. | 12 | count | n |  | eq | `[[art:61276a96:run.features#n]]` | verified | 12 |
| 26 | conceptual_soundness | Of these, 5 are known at origination and 7 are known before… | 5 | count | at_origination |  | eq | `[[art:61276a96:run.features#at_origination]]` | verified | 5 |
| 27 | conceptual_soundness | Of these, 5 are known at origination and 7 are known before… | 7 | count | before_period_start |  | eq | `[[art:61276a96:run.features#before_period_start]]` | verified | 7 |
| 28 | conceptual_soundness | None are labelled as observed during the period, at 0 , and… | 0 | count | during_period |  | eq | `[[art:61276a96:run.features#during_period]]` | verified | 0 |
| 29 | conceptual_soundness | None are labelled as observed during the period, at 0 , and… | 0 | count | after_outcome |  | eq | `[[art:61276a96:run.features#after_outcome]]` | verified | 0 |
| 30 | conceptual_soundness | The developer applied a collinearity screen with a variance… | 10 | ratio | vif_threshold |  | eq | `[[art:b764932a:run.model_summary#vif_threshold]]` | verified | 10 |
| 31 | conceptual_soundness | The twelve-month rate change feature was dropped at an infla… | 12.38 | ratio | vif |  | eq | `[[art:b764932a:run.model_summary#removed.rate_change_12m.vif]]` | verified | 12.377209 |
| 32 | conceptual_soundness | The log beginning-of-month balance feature was dropped at an… | 40090 | ratio | vif |  | eq | `[[art:b764932a:run.model_summary#removed.bom_balance_log.vif]]` | verified | 40090.39108 |
| 33 | conceptual_soundness | The largest coefficient in the fitted index is on the refina… | 1.253 | ratio | coefficient |  | eq | `[[art:b764932a:run.model_summary#coefficients.incentive.value]]` | verified | 1.253400948 |
| 34 | conceptual_soundness | The leading loan age spline term, at 0.6491 , carries the ea… | 0.6491 | ratio | coefficient |  | eq | `[[art:b764932a:run.model_summary#coefficients.loan_age_spline_1.value]]` | verified | 0.6491385114 |
| 35 | conceptual_soundness | The leading loan age spline term, at 0.6491 , carries the ea… | -0.2386 | ratio | coefficient |  | eq | `[[art:b764932a:run.model_summary#coefficients.loan_age_spline_4.value]]` | verified | -0.2385660288 |
| 36 | conceptual_soundness | The note rate coefficient, at -0.4457 , is the largest remai… | -0.4457 | ratio | coefficient |  | eq | `[[art:b764932a:run.model_summary#coefficients.note_rate.value]]` | verified | -0.4457241706 |
| 37 | conceptual_soundness | Credit score enters at 0.4074 and log original balance at 0.… | 0.4074 | ratio | coefficient |  | eq | `[[art:b764932a:run.model_summary#coefficients.credit_score.value]]` | verified | 0.4073637042 |
| 38 | conceptual_soundness | Credit score enters at 0.4074 and log original balance at 0.… | 0.3036 | ratio | coefficient |  | eq | `[[art:b764932a:run.model_summary#coefficients.orig_upb_log.value]]` | verified | 0.3036365647 |
| 39 | conceptual_soundness | Original loan-to-value enters at -0.243 , negative, consiste… | -0.243 | ratio | coefficient |  | eq | `[[art:b764932a:run.model_summary#coefficients.orig_ltv.value]]` | verified | -0.2430424725 |
| 40 | conceptual_soundness | The spread at origination enters at 0.01282 and the seasonal… | 0.01282 | ratio | coefficient |  | eq | `[[art:b764932a:run.model_summary#coefficients.sato.value]]` | verified | 0.01281978784 |
| 41 | conceptual_soundness | The spread at origination enters at 0.01282 and the seasonal… | 0.0702 | ratio | coefficient |  | eq | `[[art:b764932a:run.model_summary#coefficients.season_sin.value]]` | verified | 0.07019923172 |
| 42 | conceptual_soundness | The spread at origination enters at 0.01282 and the seasonal… | -0.1239 | ratio | coefficient |  | eq | `[[art:b764932a:run.model_summary#coefficients.season_cos.value]]` | verified | -0.1238708376 |
| 43 | conceptual_soundness | Burnout enters at 0.07952 , and a positive sign here runs ag… | 0.07952 | ratio | coefficient |  | eq | `[[art:b764932a:run.model_summary#coefficients.burnout.value]]` | verified | 0.07951968723 |
| 44 | conceptual_soundness | The sign comparison covers the retained features and reports… | 1 | count | n_disagreements |  | eq | `[[art:f96ece96:sign_check.n_disagreements]]` | verified | 1 |
| 45 | conceptual_soundness | That feature is the note rate: the fitted coefficient has si… | -1 | ratio | coef_sign |  | eq | `[[art:aecf7ccb:sign_check.note_rate.coef_sign]]` | verified | -1 |
| 46 | conceptual_soundness | That feature is the note rate: the fitted coefficient has si… | 1 | ratio | univariate_direction | train | eq | `[[art:61f6e1ac:sign_check.note_rate.univariate_direction]]` | verified | 1 |
| 47 | conceptual_soundness | That feature is the note rate: the fitted coefficient has si… | 0 | ratio | agrees |  | eq | `[[art:a453463d:sign_check.note_rate.agrees]]` | verified | 0 |
| 48 | conceptual_soundness | The measure of how much this disagreement matters is the abl… | -0.002585 | ratio | delta_auc | test | eq | `[[art:14558b82:ablation.note_rate.delta_auc]]` | verified | -0.002585106068 |
| 49 | conceptual_soundness | The measure of how much this disagreement matters is the abl… | -0.04117 | ratio | delta_auc | test | eq | `[[art:78108590:ablation.incentive.delta_auc]]` | verified | -0.0411745927 |
| 50 | conceptual_soundness | Every other checked feature agrees, with agreement indicator… | 1 | ratio | agrees |  | eq | `[[art:f7b2338e:sign_check.incentive.agrees]]` | verified | 1 |
| 51 | conceptual_soundness | The underlying pairs are consistent in each of those cases,… | 1 | ratio | coef_sign |  | eq | `[[art:684cf11a:sign_check.incentive.coef_sign]]` | verified | 1 |
| 52 | conceptual_soundness | The underlying pairs are consistent in each of those cases,… | 1 | ratio | univariate_direction | train | eq | `[[art:8098d951:sign_check.incentive.univariate_direction]]` | verified | 1 |
| 53 | conceptual_soundness | The underlying pairs are consistent in each of those cases,… | -1 | ratio | coef_sign |  | eq | `[[art:7eec65ec:sign_check.orig_ltv.coef_sign]]` | verified | -1 |
| 54 | conceptual_soundness | The underlying pairs are consistent in each of those cases,… | -1 | ratio | univariate_direction | train | eq | `[[art:76dbc708:sign_check.orig_ltv.univariate_direction]]` | verified | -1 |
| 55 | conceptual_soundness | Ablation refits the champion's functional form without one f… | 0.7673 | ratio | baseline_auc | test | eq | `[[art:54367df6:ablation.baseline_auc]]` | verified | 0.7672992275 |
| 56 | conceptual_soundness | The incentive term is where the discrimination lives, at -0.… | -0.04117 | ratio | delta_auc | test | eq | `[[art:78108590:ablation.incentive.delta_auc]]` | verified | -0.0411745927 |
| 57 | conceptual_soundness | The incentive term is where the discrimination lives, at -0.… | -0.01927 | ratio | delta_auc | test | eq | `[[art:0ddb11a9:ablation.orig_upb_log.delta_auc]]` | verified | -0.01926646624 |
| 58 | conceptual_soundness | The incentive term is where the discrimination lives, at -0.… | -0.01474 | ratio | delta_auc | test | eq | `[[art:9bdeb0df:ablation.credit_score.delta_auc]]` | verified | -0.0147431913 |
| 59 | conceptual_soundness | Original loan-to-value contributes -0.002294 and the note ra… | -0.002294 | ratio | delta_auc | test | eq | `[[art:57ea66c5:ablation.orig_ltv.delta_auc]]` | verified | -0.002294407165 |
| 60 | conceptual_soundness | Original loan-to-value contributes -0.002294 and the note ra… | -0.002585 | ratio | delta_auc | test | eq | `[[art:14558b82:ablation.note_rate.delta_auc]]` | verified | -0.002585106068 |
| 61 | conceptual_soundness | The seasonal terms and burnout are close to inert on this me… | -0.0004826 | ratio | delta_auc | test | eq | `[[art:a288439d:ablation.season_cos.delta_auc]]` | verified | -0.00048256018 |
| 62 | conceptual_soundness | The seasonal terms and burnout are close to inert on this me… | -0.0003885 | ratio | delta_auc | test | eq | `[[art:e54c8581:ablation.season_sin.delta_auc]]` | verified | -0.0003884794439 |
| 63 | conceptual_soundness | The seasonal terms and burnout are close to inert on this me… | -0.0001876 | ratio | delta_auc | test | eq | `[[art:3cba039b:ablation.burnout.delta_auc]]` | verified | -0.0001876329287 |
| 64 | conceptual_soundness | Two features have positive deltas, meaning test AUC rose sli… | 0.0008166 | ratio | delta_auc | test | eq | `[[art:be669163:ablation.loan_age.delta_auc]]` | verified | 0.0008165996474 |
| 65 | conceptual_soundness | Two features have positive deltas, meaning test AUC rose sli… | 0.0005201 | ratio | delta_auc | test | eq | `[[art:57703504:ablation.sato.delta_auc]]` | verified | 0.0005200867657 |
| 66 | conceptual_soundness | The benchmark comparison sets the champion's recomputed test… | 0.7753 | ratio | auc | test | eq | `[[art:57066271:metrics.test.auc]]` | verified | 0.7752553922 |
| 67 | conceptual_soundness | The benchmark comparison sets the champion's recomputed test… | 0.7337 | ratio | auc | test | eq | `[[art:705b66f0:challenger.auc]]` | verified | 0.7337079121 |
| 68 | conceptual_soundness | The reported difference, the challenger's AUC on test less t… | -0.04155 | ratio | delta_auc | test | eq | `[[art:4d28c096:challenger.delta_auc]]` | verified | -0.04154748012 |
| 69 | conceptual_soundness | The threshold that decides whether the comparison matters is… | 0.03 | ratio | delta_auc | test | eq | `[[art:e042774c:threshold.E1.delta_auc]]` | verified | 0.03 |
| 70 | conceptual_soundness | On the probability scale the ordering is the same: the champ… | 0.007894 | ratio | brier | test | eq | `[[art:7d3583cd:metrics.test.brier]]` | verified | 0.00789356705 |
| 71 | conceptual_soundness | On the probability scale the ordering is the same: the champ… | 0.00863 | ratio | brier | test | eq | `[[art:85a89ef9:challenger.brier]]` | verified | 0.008629514666 |
| 72 | data_integrity | The splits carry 36013 training rows, 15382 test rows, 32177… | 36013 | count | n | train | eq | `[[art:c5ebd9c9:profile.train.n]]` | verified | 36013 |
| 73 | data_integrity | The splits carry 36013 training rows, 15382 test rows, 32177… | 15382 | count | n | test | eq | `[[art:e3abc1b8:profile.test.n]]` | verified | 15382 |
| 74 | data_integrity | The splits carry 36013 training rows, 15382 test rows, 32177… | 32177 | count | n | vintage_holdout | eq | `[[art:426e712a:profile.vintage_holdout.n]]` | verified | 32177 |
| 75 | data_integrity | The splits carry 36013 training rows, 15382 test rows, 32177… | 12257 | count | n | out_of_time | eq | `[[art:fa39c5cf:profile.out_of_time.n]]` | verified | 12257 |
| 76 | data_integrity | The largest missing fraction is 0 in train, 0 in test, 0 in… | 0 | ratio | missing | train | eq | `[[art:050a3099:profile.train.missing.max]]` | verified | 0 |
| 77 | data_integrity | The largest missing fraction is 0 in train, 0 in test, 0 in… | 0 | ratio | missing | test | eq | `[[art:f813848d:profile.test.missing.max]]` | verified | 0 |
| 78 | data_integrity | The largest missing fraction is 0 in train, 0 in test, 0 in… | 0 | ratio | missing | vintage_holdout | eq | `[[art:329bb430:profile.vintage_holdout.missing.max]]` | verified | 0 |
| 79 | data_integrity | The largest missing fraction is 0 in train, 0 in test, 0 in… | 0 | ratio | missing | out_of_time | eq | `[[art:4dafce11:profile.out_of_time.missing.max]]` | verified | 0 |
| 80 | data_integrity | The bound on the missingness gap between splits is 0.1 , and… | 0.1 | ratio | missing_gap |  | eq | `[[art:9cce25ea:threshold.D1.missing_gap]]` | verified | 0.1 |
| 81 | data_integrity | Between train and test the largest population stability inde… | 0.06189 | ratio | psi |  | eq | `[[art:c2e8c8fd:psi.max]]` | verified | 0.06188985797 |
| 82 | data_integrity | Between train and test the largest population stability inde… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 83 | data_integrity | Between train and test the largest population stability inde… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 84 | data_integrity | That maximum is carried by credit_score at 0.06189 , with or… | 0.06189 | ratio | psi |  | eq | `[[art:7e87527c:psi.credit_score]]` | verified | 0.06188985797 |
| 85 | data_integrity | That maximum is carried by credit_score at 0.06189 , with or… | 0.04817 | ratio | psi |  | eq | `[[art:55030a3b:psi.orig_upb_log]]` | verified | 0.04817081196 |
| 86 | data_integrity | That maximum is carried by credit_score at 0.06189 , with or… | 0.03617 | ratio | psi |  | eq | `[[art:cd1ff136:psi.orig_ltv]]` | verified | 0.03617297258 |
| 87 | data_integrity | That maximum is carried by credit_score at 0.06189 , with or… | 0.02773 | ratio | psi |  | eq | `[[art:584da64f:psi.sato]]` | verified | 0.02772829856 |
| 88 | data_integrity | That maximum is carried by credit_score at 0.06189 , with or… | 0.01371 | ratio | psi |  | eq | `[[art:ecc6adf3:psi.note_rate]]` | verified | 0.01370911382 |
| 89 | data_integrity | That maximum is carried by credit_score at 0.06189 , with or… | 0.004614 | ratio | psi |  | eq | `[[art:9dc7ecc2:psi.burnout]]` | verified | 0.004614338236 |
| 90 | data_integrity | That maximum is carried by credit_score at 0.06189 , with or… | 0.0009923 | ratio | psi |  | eq | `[[art:2da5570f:psi.incentive]]` | verified | 0.0009922551416 |
| 91 | data_integrity | That maximum is carried by credit_score at 0.06189 , with or… | 0.0001994 | ratio | psi |  | eq | `[[art:2202b157:psi.loan_age]]` | verified | 0.0001993816816 |
| 92 | data_integrity | That maximum is carried by credit_score at 0.06189 , with or… | 1.79e-05 | ratio | psi |  | eq | `[[art:addec503:psi.season_cos]]` | verified | 1.790085913e-05 |
| 93 | data_integrity | That maximum is carried by credit_score at 0.06189 , with or… | 2.939e-06 | ratio | psi |  | eq | `[[art:4d2ed98d:psi.season_sin]]` | verified | 2.939045338e-06 |
| 94 | data_integrity | The score shifts by 0.001953 between train and test. | 0.001953 | ratio | psi |  | eq | `[[art:3b9dee2d:psi.y_score]]` | verified | 0.001952903716 |
| 95 | data_integrity | Against the vintage holdout the picture is different: note_r… | 0.6088 | ratio | psi | vintage_holdout | eq | `[[art:f281f8a7:psi.vintage_holdout.note_rate]]` | verified | 0.608822927 |
| 96 | data_integrity | Against the vintage holdout the picture is different: note_r… | 0.4475 | ratio | psi | vintage_holdout | eq | `[[art:5e61b6f9:psi.vintage_holdout.incentive]]` | verified | 0.4475226601 |
| 97 | data_integrity | Against the vintage holdout the picture is different: note_r… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 98 | data_integrity | The other inputs stay lower on that split: loan_age at 0.071… | 0.07112 | ratio | psi | vintage_holdout | eq | `[[art:6d92c48b:psi.vintage_holdout.loan_age]]` | verified | 0.07111526296 |
| 99 | data_integrity | The other inputs stay lower on that split: loan_age at 0.071… | 0.04749 | ratio | psi | vintage_holdout | eq | `[[art:e29067e6:psi.vintage_holdout.burnout]]` | verified | 0.04749372789 |
| 100 | data_integrity | The other inputs stay lower on that split: loan_age at 0.071… | 0.0404 | ratio | psi | vintage_holdout | eq | `[[art:77ec758a:psi.vintage_holdout.orig_upb_log]]` | verified | 0.04039645306 |
| 101 | data_integrity | The other inputs stay lower on that split: loan_age at 0.071… | 0.03996 | ratio | psi | vintage_holdout | eq | `[[art:3498d307:psi.vintage_holdout.credit_score]]` | verified | 0.03995819732 |
| 102 | data_integrity | The other inputs stay lower on that split: loan_age at 0.071… | 0.02989 | ratio | psi | vintage_holdout | eq | `[[art:eea64c25:psi.vintage_holdout.sato]]` | verified | 0.02989256711 |
| 103 | data_integrity | The other inputs stay lower on that split: loan_age at 0.071… | 0.02942 | ratio | psi | vintage_holdout | eq | `[[art:d07cfb7d:psi.vintage_holdout.orig_ltv]]` | verified | 0.0294150369 |
| 104 | data_integrity | The other inputs stay lower on that split: loan_age at 0.071… | 0.001288 | ratio | psi | vintage_holdout | eq | `[[art:9fe842a8:psi.vintage_holdout.season_cos]]` | verified | 0.0012879007 |
| 105 | data_integrity | The other inputs stay lower on that split: loan_age at 0.071… | 0.0007309 | ratio | psi | vintage_holdout | eq | `[[art:b0dc9745:psi.vintage_holdout.season_sin]]` | verified | 0.0007309374015 |
| 106 | data_integrity | The score shifts by 0.1421 on that split, below 0.25 . | 0.1421 | ratio | psi | vintage_holdout | eq | `[[art:3713457e:psi.vintage_holdout.y_score]]` | verified | 0.142110315 |
| 107 | data_integrity | The score shifts by 0.1421 on that split, below 0.25 . | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 108 | data_integrity | Out of time the shifts are larger still: burnout reaches 2.9… | 2.945 | ratio | psi | out_of_time | eq | `[[art:7b0bbebb:psi.out_of_time.burnout]]` | verified | 2.944521522 |
| 109 | data_integrity | Out of time the shifts are larger still: burnout reaches 2.9… | 2.484 | ratio | psi | out_of_time | eq | `[[art:d6eaaaf5:psi.out_of_time.loan_age]]` | verified | 2.483993033 |
| 110 | data_integrity | Out of time the shifts are larger still: burnout reaches 2.9… | 0.6977 | ratio | psi | out_of_time | eq | `[[art:cabd371d:psi.out_of_time.note_rate]]` | verified | 0.6976589281 |
| 111 | data_integrity | Out of time the shifts are larger still: burnout reaches 2.9… | 0.4958 | ratio | psi | out_of_time | eq | `[[art:42076ed1:psi.out_of_time.incentive]]` | verified | 0.4958065489 |
| 112 | data_integrity | Out of time the shifts are larger still: burnout reaches 2.9… | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 113 | data_integrity | The remaining inputs stay below that level: orig_upb_log at… | 0.07136 | ratio | psi | out_of_time | eq | `[[art:ac349b67:psi.out_of_time.orig_upb_log]]` | verified | 0.07136421414 |
| 114 | data_integrity | The remaining inputs stay below that level: orig_upb_log at… | 0.05988 | ratio | psi | out_of_time | eq | `[[art:d7249e47:psi.out_of_time.credit_score]]` | verified | 0.05987964443 |
| 115 | data_integrity | The remaining inputs stay below that level: orig_upb_log at… | 0.04301 | ratio | psi | out_of_time | eq | `[[art:3eee5db4:psi.out_of_time.orig_ltv]]` | verified | 0.04300793312 |
| 116 | data_integrity | The remaining inputs stay below that level: orig_upb_log at… | 0.02789 | ratio | psi | out_of_time | eq | `[[art:144e1bd9:psi.out_of_time.season_sin]]` | verified | 0.02788988464 |
| 117 | data_integrity | The remaining inputs stay below that level: orig_upb_log at… | 0.01299 | ratio | psi | out_of_time | eq | `[[art:c2233ce6:psi.out_of_time.sato]]` | verified | 0.01298850667 |
| 118 | data_integrity | The remaining inputs stay below that level: orig_upb_log at… | 0.007524 | ratio | psi | out_of_time | eq | `[[art:25cf6b85:psi.out_of_time.season_cos]]` | verified | 0.00752368457 |
| 119 | data_integrity | The score shifts by 0.7056 out of time, above 0.25 . | 0.7056 | ratio | psi | out_of_time | eq | `[[art:2dc61374:psi.out_of_time.y_score]]` | verified | 0.7055906656 |
| 120 | data_integrity | The score shifts by 0.7056 out of time, above 0.25 . | 0.25 | ratio | psi |  | eq | `[[art:278b9016:threshold.S1.psi]]` | verified | 0.25 |
| 121 | data_integrity | The characteristic stability indices, which attribute the sh… | 0.03438 | ratio | csi |  | eq | `[[art:54bd75b0:csi.max]]` | verified | 0.03438094941 |
| 122 | data_integrity | The characteristic stability indices, which attribute the sh… | 0.03438 | ratio | csi |  | eq | `[[art:97d51193:csi.orig_ltv]]` | verified | 0.03438094941 |
| 123 | data_integrity | Behind it are note_rate at 0.01822 , credit_score at 0.00790… | 0.01822 | ratio | csi |  | eq | `[[art:92901ac4:csi.note_rate]]` | verified | 0.01822065751 |
| 124 | data_integrity | Behind it are note_rate at 0.01822 , credit_score at 0.00790… | 0.007909 | ratio | csi |  | eq | `[[art:c40b4ede:csi.credit_score]]` | verified | 0.007908848663 |
| 125 | data_integrity | Behind it are note_rate at 0.01822 , credit_score at 0.00790… | 0.005804 | ratio | csi |  | eq | `[[art:874ef644:csi.incentive]]` | verified | 0.005803522882 |
| 126 | data_integrity | Behind it are note_rate at 0.01822 , credit_score at 0.00790… | 0.002969 | ratio | csi |  | eq | `[[art:bb919ade:csi.orig_upb_log]]` | verified | 0.00296903904 |
| 127 | data_integrity | Behind it are note_rate at 0.01822 , credit_score at 0.00790… | 0.001487 | ratio | csi |  | eq | `[[art:6a5f7a41:csi.sato]]` | verified | 0.001487358985 |
| 128 | data_integrity | Behind it are note_rate at 0.01822 , credit_score at 0.00790… | 0.0009851 | ratio | csi |  | eq | `[[art:b2729e08:csi.burnout]]` | verified | 0.0009851123767 |
| 129 | data_integrity | Behind it are note_rate at 0.01822 , credit_score at 0.00790… | 0.0004785 | ratio | csi |  | eq | `[[art:75b544aa:csi.season_cos]]` | verified | 0.0004785421555 |
| 130 | data_integrity | Behind it are note_rate at 0.01822 , credit_score at 0.00790… | 7.624e-05 | ratio | csi |  | eq | `[[art:d55271d6:csi.season_sin]]` | verified | 7.624273793e-05 |
| 131 | data_integrity | Behind it are note_rate at 0.01822 , credit_score at 0.00790… | 0 | ratio | csi |  | eq | `[[art:df52c920:csi.loan_age]]` | verified | 0 |
| 132 | data_integrity | The declared timings flag no feature as measured during the… | 0 | count | n_flagged |  | eq | `[[art:742bcd24:leakage.timing.n_flagged]]` | verified | 0 |
| 133 | data_integrity | The strongest single feature reaches an AUC of 0.7239 , belo… | 0.7239 | ratio | auc |  | eq | `[[art:1fe630dd:leakage.target_corr.max_single_feature_auc]]` | verified | 0.7238936567 |
| 134 | data_integrity | The strongest single feature reaches an AUC of 0.7239 , belo… | 0.9 | ratio | auc |  | eq | `[[art:c29e7a34:threshold.L1.single_feature_auc]]` | verified | 0.9 |
| 135 | data_integrity | On identifiers, the share of test rows whose loan and period… | 0 | ratio | overlap |  | eq | `[[art:63d37fc5:leakage.overlap.ids]]` | verified | 0 |
| 136 | data_integrity | On identifiers, the share of test rows whose loan and period… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 137 | data_integrity | On feature vectors, the share of test rows whose values also… | 0 | ratio | overlap |  | eq | `[[art:0fec8048:leakage.overlap.features]]` | verified | 0 |
| 138 | data_integrity | On feature vectors, the share of test rows whose values also… | 0.005 | ratio | overlap |  | eq | `[[art:1ee888c5:threshold.L2.overlap.features_effective]]` | verified | 0.005 |
| 139 | data_integrity | That applied bound is the larger of the declared contaminati… | 0.005 | ratio | overlap |  | eq | `[[art:9f336eaf:threshold.L2.overlap]]` | verified | 0.005 |
| 140 | data_integrity | That applied bound is the larger of the declared contaminati… | 0 | ratio | duplicates | train | eq | `[[art:4474c227:leakage.duplicates.train]]` | verified | 0 |
| 141 | data_integrity | The overall share of test rows whose feature values also app… | 0 | ratio | overlap |  | eq | `[[art:4c9fcd09:leakage.overlap]]` | verified | 0 |
| 142 | data_integrity | The name screen matches no feature name against the target-a… | 0 | count | n_matched |  | eq | `[[art:407e62be:leakage.name_screen.n_matched]]` | verified | 0 |
| 143 | outcomes | On test, the logistic regression of the outcome on logit(p)… | 0.9365 | ratio | calibration_slope | test | eq | `[[art:3e42ee62:calibration_slope.test]]` | verified | 0.9365180494 |
| 144 | outcomes | On test, the logistic regression of the outcome on logit(p)… | -0.277 | ratio | calibration_intercept | test | eq | `[[art:e87b5c13:calibration_intercept.test]]` | verified | -0.2769708146 |
| 145 | outcomes | On train, the same regression returns a slope of 0.9937 and… | 0.9937 | ratio | calibration_slope | train | eq | `[[art:534cb102:calibration_slope.train]]` | verified | 0.9936945557 |
| 146 | outcomes | On train, the same regression returns a slope of 0.9937 and… | -0.01454 | ratio | calibration_intercept | train | eq | `[[art:11d7a3ca:calibration_intercept.train]]` | verified | -0.01453793696 |
| 147 | outcomes | On the out-of-time split, the slope is 0.9969 and the interc… | 0.9969 | ratio | calibration_slope | out_of_time | eq | `[[art:a49b2789:calibration_slope.out_of_time]]` | verified | 0.9969389246 |
| 148 | outcomes | On the out-of-time split, the slope is 0.9969 and the interc… | -0.06272 | ratio | calibration_intercept | out_of_time | eq | `[[art:fc7ece3a:calibration_intercept.out_of_time]]` | verified | -0.06272473851 |
| 149 | outcomes | On the vintage holdout, the slope is 0.8373 and the intercep… | 0.8373 | ratio | calibration_slope | vintage_holdout | eq | `[[art:08d6b321:calibration_slope.vintage_holdout]]` | verified | 0.837279841 |
| 150 | outcomes | On the vintage holdout, the slope is 0.8373 and the intercep… | -0.9028 | ratio | calibration_intercept | vintage_holdout | eq | `[[art:44715143:calibration_intercept.vintage_holdout]]` | verified | -0.9028328443 |
| 151 | outcomes | The declared band for the slope runs from 0.8 to 1.2 , and e… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 152 | outcomes | The declared band for the slope runs from 0.8 to 1.2 , and e… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 153 | outcomes | Mean predicted probability on test is 0.008116 against an ob… | 0.008116 | ratio | mean_predicted | test | eq | `[[art:3bc93911:metrics.test.mean_predicted]]` | verified | 0.008115821785 |
| 154 | outcomes | Mean predicted probability on test is 0.008116 against an ob… | 0.008061 | ratio | event_rate | test | eq | `[[art:570cc08a:metrics.test.event_rate]]` | verified | 0.008061370433 |
| 155 | outcomes | Mean predicted probability on test is 0.008116 against an ob… | 0.006755 | ratio | mean_rel_gap | test | eq | `[[art:59b8a1f5:calibration.mean_rel_gap.test]]` | verified | 0.006754602372 |
| 156 | outcomes | Mean predicted probability on train is 0.008427 against an o… | 0.008427 | ratio | mean_predicted | train | eq | `[[art:a63f6555:metrics.train.mean_predicted]]` | verified | 0.008426526894 |
| 157 | outcomes | Mean predicted probability on train is 0.008427 against an o… | 0.008525 | ratio | event_rate | train | eq | `[[art:b9ef3327:metrics.train.event_rate]]` | verified | 0.008524699414 |
| 158 | outcomes | Mean predicted probability on train is 0.008427 against an o… | 0.01152 | ratio | mean_rel_gap | train | eq | `[[art:e28c45a9:calibration.mean_rel_gap.train]]` | verified | 0.01151624417 |
| 159 | outcomes | Out of time, mean predicted is 0.01887 against an observed r… | 0.01887 | ratio | mean_predicted | out_of_time | eq | `[[art:3833e0c5:metrics.out_of_time.mean_predicted]]` | verified | 0.01886588953 |
| 160 | outcomes | Out of time, mean predicted is 0.01887 against an observed r… | 0.01795 | ratio | event_rate | out_of_time | eq | `[[art:83ccf5c0:metrics.out_of_time.event_rate]]` | verified | 0.01794892714 |
| 161 | outcomes | Out of time, mean predicted is 0.01887 against an observed r… | 0.05109 | ratio | mean_rel_gap | out_of_time | eq | `[[art:c599bd89:calibration.mean_rel_gap.out_of_time]]` | verified | 0.05108730888 |
| 162 | outcomes | On the vintage holdout, mean predicted is 0.005647 against a… | 0.005647 | ratio | mean_predicted | vintage_holdout | eq | `[[art:5ae28866:metrics.vintage_holdout.mean_predicted]]` | verified | 0.005646788012 |
| 163 | outcomes | On the vintage holdout, mean predicted is 0.005647 against a… | 0.004817 | ratio | event_rate | vintage_holdout | eq | `[[art:e3590a16:metrics.vintage_holdout.event_rate]]` | verified | 0.004817105386 |
| 164 | outcomes | On the vintage holdout, mean predicted is 0.005647 against a… | 0.1722 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:55a672c2:calibration.mean_rel_gap.vintage_holdout]]` | verified | 0.1722367603 |
| 165 | outcomes | The tolerance applied to that relative gap is 0.25 , and eac… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 166 | outcomes | The mean absolute difference between actual and predicted CP… | 0.02658 | ratio | cpr_mae | train | eq | `[[art:f2c3683c:cpr.train.mae]]` | verified | 0.02657629251 |
| 167 | outcomes | The mean absolute difference between actual and predicted CP… | 0.04264 | ratio | cpr_mae | test | eq | `[[art:ff266c97:cpr.test.mae]]` | verified | 0.042636033 |
| 168 | outcomes | The mean absolute difference between actual and predicted CP… | 0.05857 | ratio | cpr_mae | out_of_time | eq | `[[art:a7ecd72b:cpr.out_of_time.mae]]` | verified | 0.05856944955 |
| 169 | outcomes | The mean absolute difference between actual and predicted CP… | 0.0289 | ratio | cpr_mae | vintage_holdout | eq | `[[art:172ebed4:cpr.vintage_holdout.mae]]` | verified | 0.0289048118 |
| 170 | outcomes | \| AUC \| 0.7883 \| 0.7753 \| 0.7846 \| 0.7718 \| | 0.7883 | ratio | auc | train | eq | `[[art:fa609ae1:metrics.train.auc]]` | verified | 0.7883327303 |
| 171 | outcomes | \| AUC \| 0.7883 \| 0.7753 \| 0.7846 \| 0.7718 \| | 0.7753 | ratio | auc | test | eq | `[[art:57066271:metrics.test.auc]]` | verified | 0.7752553922 |
| 172 | outcomes | \| AUC \| 0.7883 \| 0.7753 \| 0.7846 \| 0.7718 \| | 0.7846 | ratio | auc | out_of_time | eq | `[[art:6f2a2d99:metrics.out_of_time.auc]]` | verified | 0.7845616168 |
| 173 | outcomes | \| AUC \| 0.7883 \| 0.7753 \| 0.7846 \| 0.7718 \| | 0.7718 | ratio | auc | vintage_holdout | eq | `[[art:ac6794c5:metrics.vintage_holdout.auc]]` | verified | 0.7717974135 |
| 174 | outcomes | \| Gini \| 0.5767 \| 0.5505 \| 0.5691 \| 0.5436 \| | 0.5767 | ratio | gini | train | eq | `[[art:0b6b2058:metrics.train.gini]]` | verified | 0.5766654607 |
| 175 | outcomes | \| Gini \| 0.5767 \| 0.5505 \| 0.5691 \| 0.5436 \| | 0.5505 | ratio | gini | test | eq | `[[art:fe7f75d7:metrics.test.gini]]` | verified | 0.5505107844 |
| 176 | outcomes | \| Gini \| 0.5767 \| 0.5505 \| 0.5691 \| 0.5436 \| | 0.5691 | ratio | gini | out_of_time | eq | `[[art:890252d7:metrics.out_of_time.gini]]` | verified | 0.5691232337 |
| 177 | outcomes | \| Gini \| 0.5767 \| 0.5505 \| 0.5691 \| 0.5436 \| | 0.5436 | ratio | gini | vintage_holdout | eq | `[[art:a4a532f0:metrics.vintage_holdout.gini]]` | verified | 0.5435948269 |
| 178 | outcomes | \| KS \| 0.4562 \| 0.4162 \| 0.4321 \| 0.4516 \| | 0.4562 | ratio | ks | train | eq | `[[art:c355478b:metrics.train.ks]]` | verified | 0.4562056834 |
| 179 | outcomes | \| KS \| 0.4562 \| 0.4162 \| 0.4321 \| 0.4516 \| | 0.4162 | ratio | ks | test | eq | `[[art:c569c301:metrics.test.ks]]` | verified | 0.4161772354 |
| 180 | outcomes | \| KS \| 0.4562 \| 0.4162 \| 0.4321 \| 0.4516 \| | 0.4321 | ratio | ks | out_of_time | eq | `[[art:16d3e4fe:metrics.out_of_time.ks]]` | verified | 0.4321115953 |
| 181 | outcomes | \| KS \| 0.4562 \| 0.4162 \| 0.4321 \| 0.4516 \| | 0.4516 | ratio | ks | vintage_holdout | eq | `[[art:b5b9e888:metrics.vintage_holdout.ks]]` | verified | 0.4515647508 |
| 182 | outcomes | \| Brier \| 0.008317 \| 0.007894 \| 0.01713 \| 0.004763 \| | 0.008317 | ratio | brier | train | eq | `[[art:83666c70:metrics.train.brier]]` | verified | 0.008317491392 |
| 183 | outcomes | \| Brier \| 0.008317 \| 0.007894 \| 0.01713 \| 0.004763 \| | 0.007894 | ratio | brier | test | eq | `[[art:7d3583cd:metrics.test.brier]]` | verified | 0.00789356705 |
| 184 | outcomes | \| Brier \| 0.008317 \| 0.007894 \| 0.01713 \| 0.004763 \| | 0.01713 | ratio | brier | out_of_time | eq | `[[art:40d244d4:metrics.out_of_time.brier]]` | verified | 0.0171279495 |
| 185 | outcomes | \| Brier \| 0.008317 \| 0.007894 \| 0.01713 \| 0.004763 \| | 0.004763 | ratio | brier | vintage_holdout | eq | `[[art:f3c6bdcc:metrics.vintage_holdout.brier]]` | verified | 0.004763025704 |
| 186 | outcomes | \| Log loss \| 0.04408 \| 0.04263 \| 0.07975 \| 0.02811 \| | 0.04408 | ratio | logloss | train | eq | `[[art:199c7db5:metrics.train.logloss]]` | verified | 0.04408402922 |
| 187 | outcomes | \| Log loss \| 0.04408 \| 0.04263 \| 0.07975 \| 0.02811 \| | 0.04263 | ratio | logloss | test | eq | `[[art:320e4c6b:metrics.test.logloss]]` | verified | 0.04263297829 |
| 188 | outcomes | \| Log loss \| 0.04408 \| 0.04263 \| 0.07975 \| 0.02811 \| | 0.07975 | ratio | logloss | out_of_time | eq | `[[art:2b7c9b2d:metrics.out_of_time.logloss]]` | verified | 0.07975283787 |
| 189 | outcomes | \| Log loss \| 0.04408 \| 0.04263 \| 0.07975 \| 0.02811 \| | 0.02811 | ratio | logloss | vintage_holdout | eq | `[[art:c32e3713:metrics.vintage_holdout.logloss]]` | verified | 0.02810570342 |
| 190 | outcomes | \| Top-decile-pair event capture \| 0.5961 \| 0.5806 \| 0.5773 \|… | 0.5961 | ratio | top2_capture | train | eq | `[[art:e8dd0c53:deciles.train.top2_capture]]` | verified | 0.5960912052 |
| 191 | outcomes | \| Top-decile-pair event capture \| 0.5961 \| 0.5806 \| 0.5773 \|… | 0.5806 | ratio | top2_capture | test | eq | `[[art:43c4adc5:deciles.test.top2_capture]]` | verified | 0.5806451613 |
| 192 | outcomes | \| Top-decile-pair event capture \| 0.5961 \| 0.5806 \| 0.5773 \|… | 0.5773 | ratio | top2_capture | out_of_time | eq | `[[art:df63152b:deciles.out_of_time.top2_capture]]` | verified | 0.5772727273 |
| 193 | outcomes | \| Top-decile-pair event capture \| 0.5961 \| 0.5806 \| 0.5773 \|… | 0.5871 | ratio | top2_capture | vintage_holdout | eq | `[[art:8b59f312:deciles.vintage_holdout.top2_capture]]` | verified | 0.5870967742 |
| 194 | outcomes | \| Rows \| 36013 \| 15382 \| 12257 \| 32177 \| | 36013 | count | n | train | eq | `[[art:6fdfeabb:metrics.train.n]]` | verified | 36013 |
| 195 | outcomes | \| Rows \| 36013 \| 15382 \| 12257 \| 32177 \| | 15382 | count | n | test | eq | `[[art:e55953e1:metrics.test.n]]` | verified | 15382 |
| 196 | outcomes | \| Rows \| 36013 \| 15382 \| 12257 \| 32177 \| | 12257 | count | n | out_of_time | eq | `[[art:7898809e:metrics.out_of_time.n]]` | verified | 12257 |
| 197 | outcomes | \| Rows \| 36013 \| 15382 \| 12257 \| 32177 \| | 32177 | count | n | vintage_holdout | eq | `[[art:37a92951:metrics.vintage_holdout.n]]` | verified | 32177 |
| 198 | outcomes | Test AUC of 0.7753 sits below train AUC of 0.7883 , and the… | 0.7753 | ratio | auc | test | eq | `[[art:57066271:metrics.test.auc]]` | verified | 0.7752553922 |
| 199 | outcomes | Test AUC of 0.7753 sits below train AUC of 0.7883 , and the… | 0.7883 | ratio | auc | train | eq | `[[art:fa609ae1:metrics.train.auc]]` | verified | 0.7883327303 |
| 200 | outcomes | Test AUC of 0.7753 sits below train AUC of 0.7883 , and the… | 0.08 | ratio | auc_gap |  | eq | `[[art:630f28f4:threshold.O1.auc_gap]]` | verified | 0.08 |
| 201 | outcomes | The declared AUC floor for test is 0.65 , below which no rec… | 0.65 | ratio | auc | test | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 202 | outcomes | The calibration slope band from 0.8 to 1.2 , the AUC floor o… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 203 | outcomes | The calibration slope band from 0.8 to 1.2 , the AUC floor o… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 204 | outcomes | The calibration slope band from 0.8 to 1.2 , the AUC floor o… | 0.65 | ratio | auc | test | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 205 | outcomes | The calibration slope band from 0.8 to 1.2 , the AUC floor o… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 206 | outcomes | On train, this sub-population's AUC falls below the split's… | 0.07016 | ratio | auc_gap | train | eq | `[[art:8d8827f2:metrics.train.sub.incentive_high.auc_gap]]` | verified | 0.07015660217 |
| 207 | outcomes | On train, this sub-population's AUC falls below the split's… | 0.5 | ratio | share | train | eq | `[[art:277218fb:metrics.train.sub.incentive_high.share]]` | verified | 0.4999861161 |
| 208 | outcomes | On test, the shortfall is 0.0484 , on a share of 0.5 . | 0.0484 | ratio | auc_gap | test | eq | `[[art:5a0ba9c4:metrics.test.sub.incentive_high.auc_gap]]` | verified | 0.04840270693 |
| 209 | outcomes | On test, the shortfall is 0.0484 , on a share of 0.5 . | 0.5 | ratio | share | test | eq | `[[art:549aa934:metrics.test.sub.incentive_high.share]]` | verified | 0.5 |
| 210 | outcomes | Out of time, the shortfall is 0.03734 , on a share of 0.4999… | 0.03734 | ratio | auc_gap | out_of_time | eq | `[[art:1c0207f9:metrics.out_of_time.sub.incentive_high.auc_gap]]` | verified | 0.0373425714 |
| 211 | outcomes | Out of time, the shortfall is 0.03734 , on a share of 0.4999… | 0.4999 | ratio | share | out_of_time | eq | `[[art:431d1ff2:metrics.out_of_time.sub.incentive_high.share]]` | verified | 0.499877621 |
| 212 | outcomes | On the vintage holdout, the shortfall is 0.01875 , on a shar… | 0.01875 | ratio | auc_gap | vintage_holdout | eq | `[[art:2ebd6757:metrics.vintage_holdout.sub.incentive_high.auc_gap]]` | verified | 0.01874804418 |
| 213 | outcomes | On the vintage holdout, the shortfall is 0.01875 , on a shar… | 0.5 | ratio | share | vintage_holdout | eq | `[[art:cb627056:metrics.vintage_holdout.sub.incentive_high.share]]` | verified | 0.499984461 |
| 214 | outcomes | Those shortfalls are read against a bound of 0.08 and the sh… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 215 | outcomes | Those shortfalls are read against a bound of 0.08 and the sh… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 216 | outcomes | Mean predicted against observed on this sub-population is 0.… | 0.01445 | ratio | mean_rel_gap | train | eq | `[[art:7d3d3639:metrics.train.sub.incentive_high.mean_rel_gap]]` | verified | 0.01445428336 |
| 217 | outcomes | Mean predicted against observed on this sub-population is 0.… | 0.03492 | ratio | mean_rel_gap | test | eq | `[[art:f90b2790:metrics.test.sub.incentive_high.mean_rel_gap]]` | verified | 0.03491504769 |
| 218 | outcomes | Mean predicted against observed on this sub-population is 0.… | 0.1235 | ratio | mean_rel_gap | out_of_time | eq | `[[art:f0899b32:metrics.out_of_time.sub.incentive_high.mean_rel_gap]]` | verified | 0.123516925 |
| 219 | outcomes | Mean predicted against observed on this sub-population is 0.… | 0.2976 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:d14397a7:metrics.vintage_holdout.sub.incentive_high.mean_rel_gap]]` | verified | 0.2975984466 |
| 220 | outcomes | On the vintage holdout that relative gap stands above the to… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 221 | outcomes | On train, this sub-population's AUC falls below the split's… | 0.06703 | ratio | auc_gap | train | eq | `[[art:134d7c07:metrics.train.sub.incentive_low.auc_gap]]` | verified | 0.06702950807 |
| 222 | outcomes | On train, this sub-population's AUC falls below the split's… | 0.5 | ratio | share | train | eq | `[[art:d7af12f0:metrics.train.sub.incentive_low.share]]` | verified | 0.5000138839 |
| 223 | outcomes | On train, this sub-population's AUC falls below the split's… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 224 | outcomes | On train, this sub-population's AUC falls below the split's… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 225 | outcomes | On test, the shortfall is 0.09283 , on a share of 0.5 , and… | 0.09283 | ratio | auc_gap | test | eq | `[[art:a0523ad8:metrics.test.sub.incentive_low.auc_gap]]` | verified | 0.09282587144 |
| 226 | outcomes | On test, the shortfall is 0.09283 , on a share of 0.5 , and… | 0.5 | ratio | share | test | eq | `[[art:1d5dd4c2:metrics.test.sub.incentive_low.share]]` | verified | 0.5 |
| 227 | outcomes | Out of time, the shortfall is 0.0163 , on a share of 0.5001… | 0.0163 | ratio | auc_gap | out_of_time | eq | `[[art:faa1a185:metrics.out_of_time.sub.incentive_low.auc_gap]]` | verified | 0.01629917634 |
| 228 | outcomes | Out of time, the shortfall is 0.0163 , on a share of 0.5001… | 0.5001 | ratio | share | out_of_time | eq | `[[art:c7aaafd2:metrics.out_of_time.sub.incentive_low.share]]` | verified | 0.500122379 |
| 229 | outcomes | On the vintage holdout, the shortfall is 0.09945 , on a shar… | 0.09945 | ratio | auc_gap | vintage_holdout | eq | `[[art:9de83338:metrics.vintage_holdout.sub.incentive_low.auc_gap]]` | verified | 0.09944645103 |
| 230 | outcomes | On the vintage holdout, the shortfall is 0.09945 , on a shar… | 0.5 | ratio | share | vintage_holdout | eq | `[[art:d94e6531:metrics.vintage_holdout.sub.incentive_low.share]]` | verified | 0.500015539 |
| 231 | outcomes | Mean predicted against observed on this sub-population is 0.… | 0.003953 | ratio | mean_rel_gap | train | eq | `[[art:05adce6c:metrics.train.sub.incentive_low.mean_rel_gap]]` | verified | 0.003953431529 |
| 232 | outcomes | Mean predicted against observed on this sub-population is 0.… | 0.1169 | ratio | mean_rel_gap | test | eq | `[[art:aede705c:metrics.test.sub.incentive_low.mean_rel_gap]]` | verified | 0.1169064836 |
| 233 | outcomes | Mean predicted against observed on this sub-population is 0.… | 0.2155 | ratio | mean_rel_gap | out_of_time | eq | `[[art:81d9f6b7:metrics.out_of_time.sub.incentive_low.mean_rel_gap]]` | verified | 0.2155153206 |
| 234 | outcomes | Mean predicted against observed on this sub-population is 0.… | 0.2422 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:20691619:metrics.vintage_holdout.sub.incentive_low.mean_rel_gap]]` | verified | 0.2421532582 |
| 235 | outcomes | Mean predicted against observed on this sub-population is 0.… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 236 | outcomes | On train, its AUC falls below the split's own by 0.03694 , o… | 0.03694 | ratio | auc_gap | train | eq | `[[art:c5d72bde:metrics.train.sub.burnout_high.auc_gap]]` | verified | 0.03693754896 |
| 237 | outcomes | On train, its AUC falls below the split's own by 0.03694 , o… | 0.5 | ratio | share | train | eq | `[[art:31040ed8:metrics.train.sub.burnout_high.share]]` | verified | 0.4999861161 |
| 238 | outcomes | On test, the shortfall is 0.05082 , on a share of 0.5 . | 0.05082 | ratio | auc_gap | test | eq | `[[art:9dce50b2:metrics.test.sub.burnout_high.auc_gap]]` | verified | 0.05082182845 |
| 239 | outcomes | On test, the shortfall is 0.05082 , on a share of 0.5 . | 0.5 | ratio | share | test | eq | `[[art:ec1e0d04:metrics.test.sub.burnout_high.share]]` | verified | 0.5 |
| 240 | outcomes | Out of time, the shortfall is 0.008043 , on a share of 0.5 . | 0.008043 | ratio | auc_gap | out_of_time | eq | `[[art:fc407765:metrics.out_of_time.sub.burnout_high.auc_gap]]` | verified | 0.008042921487 |
| 241 | outcomes | Out of time, the shortfall is 0.008043 , on a share of 0.5 . | 0.5 | ratio | share | out_of_time | eq | `[[art:b5c30bbc:metrics.out_of_time.sub.burnout_high.share]]` | verified | 0.499959207 |
| 242 | outcomes | On the vintage holdout, the shortfall is 0.0381 , on a share… | 0.0381 | ratio | auc_gap | vintage_holdout | eq | `[[art:b2bfad0a:metrics.vintage_holdout.sub.burnout_high.auc_gap]]` | verified | 0.03809536629 |
| 243 | outcomes | On the vintage holdout, the shortfall is 0.0381 , on a share… | 0.5 | ratio | share | vintage_holdout | eq | `[[art:379549be:metrics.vintage_holdout.sub.burnout_high.share]]` | verified | 0.499984461 |
| 244 | outcomes | Each of those shortfalls is below the bound of 0.08 and each… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 245 | outcomes | Each of those shortfalls is below the bound of 0.08 and each… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 246 | outcomes | Mean predicted against observed on this sub-population is 0.… | 0.0009105 | ratio | mean_rel_gap | train | eq | `[[art:7b4ba231:metrics.train.sub.burnout_high.mean_rel_gap]]` | verified | 0.0009104580871 |
| 247 | outcomes | Mean predicted against observed on this sub-population is 0.… | 0.006956 | ratio | mean_rel_gap | test | eq | `[[art:da3a2aa8:metrics.test.sub.burnout_high.mean_rel_gap]]` | verified | 0.006955749093 |
| 248 | outcomes | Mean predicted against observed on this sub-population is 0.… | 0.3184 | ratio | mean_rel_gap | out_of_time | eq | `[[art:56cf9db6:metrics.out_of_time.sub.burnout_high.mean_rel_gap]]` | verified | 0.3183858398 |
| 249 | outcomes | Mean predicted against observed on this sub-population is 0.… | 0.05321 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:f497ef02:metrics.vintage_holdout.sub.burnout_high.mean_rel_gap]]` | verified | 0.05320653872 |
| 250 | outcomes | Out of time that relative gap stands above the tolerance of… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 251 | outcomes | On train, its AUC falls below the split's own by 0.03835 , o… | 0.03835 | ratio | auc_gap | train | eq | `[[art:7a5c3299:metrics.train.sub.burnout_low.auc_gap]]` | verified | 0.03834607983 |
| 252 | outcomes | On train, its AUC falls below the split's own by 0.03835 , o… | 0.5 | ratio | share | train | eq | `[[art:9d770878:metrics.train.sub.burnout_low.share]]` | verified | 0.5000138839 |
| 253 | outcomes | On test, the shortfall is 0.03172 , on a share of 0.5 . | 0.03172 | ratio | auc_gap | test | eq | `[[art:acc515db:metrics.test.sub.burnout_low.auc_gap]]` | verified | 0.03171500332 |
| 254 | outcomes | On test, the shortfall is 0.03172 , on a share of 0.5 . | 0.5 | ratio | share | test | eq | `[[art:2cb9dc34:metrics.test.sub.burnout_low.share]]` | verified | 0.5 |
| 255 | outcomes | Out of time, the recorded shortfall is -0.02568 , on a share… | -0.02568 | ratio | auc_gap | out_of_time | eq | `[[art:36fd04a3:metrics.out_of_time.sub.burnout_low.auc_gap]]` | verified | -0.02568035627 |
| 256 | outcomes | Out of time, the recorded shortfall is -0.02568 , on a share… | 0.5 | ratio | share | out_of_time | eq | `[[art:d6102b4a:metrics.out_of_time.sub.burnout_low.share]]` | verified | 0.500040793 |
| 257 | outcomes | On the vintage holdout, the shortfall is 0.02593 , on a shar… | 0.02593 | ratio | auc_gap | vintage_holdout | eq | `[[art:180537c0:metrics.vintage_holdout.sub.burnout_low.auc_gap]]` | verified | 0.02592501233 |
| 258 | outcomes | On the vintage holdout, the shortfall is 0.02593 , on a shar… | 0.5 | ratio | share | vintage_holdout | eq | `[[art:b327a747:metrics.vintage_holdout.sub.burnout_low.share]]` | verified | 0.500015539 |
| 259 | outcomes | Each of those values is below the bound of 0.08 and each sha… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 260 | outcomes | Each of those values is below the bound of 0.08 and each sha… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 261 | outcomes | Mean predicted against observed on this sub-population is 0.… | 0.05282 | ratio | mean_rel_gap | train | eq | `[[art:c979f2dc:metrics.train.sub.burnout_low.mean_rel_gap]]` | verified | 0.0528219024 |
| 262 | outcomes | Mean predicted against observed on this sub-population is 0.… | 0.006065 | ratio | mean_rel_gap | test | eq | `[[art:6ef3aca5:metrics.test.sub.burnout_low.mean_rel_gap]]` | verified | 0.006064956473 |
| 263 | outcomes | Mean predicted against observed on this sub-population is 0.… | 0.2638 | ratio | mean_rel_gap | out_of_time | eq | `[[art:fc98bff4:metrics.out_of_time.sub.burnout_low.mean_rel_gap]]` | verified | 0.263848584 |
| 264 | outcomes | Mean predicted against observed on this sub-population is 0.… | 0.6123 | ratio | mean_rel_gap | vintage_holdout | eq | `[[art:508e2e1f:metrics.vintage_holdout.sub.burnout_low.mean_rel_gap]]` | verified | 0.6122878825 |
| 265 | outcomes | Out of time and on the vintage holdout those relative gaps s… | 0.25 | ratio | mean_ratio_rel |  | eq | `[[art:20e93a8c:threshold.C1.mean_ratio_rel]]` | verified | 0.25 |
| 266 | sensitivity | The largest variance inflation factor across the retained fe… | 4.976 | ratio | vif |  | eq | `[[art:f9e0db60:vif.max]]` | verified | 4.975500767 |
| 267 | sensitivity | The largest variance inflation factor across the retained fe… | 10 | ratio | vif |  | eq | `[[art:aeb4f33c:threshold.M1.vif]]` | verified | 10 |
| 268 | sensitivity | That maximum belongs to the note-rate term, whose factor is… | 4.976 | ratio | vif |  | eq | `[[art:37532fa8:vif.note_rate]]` | verified | 4.975500767 |
| 269 | sensitivity | That maximum belongs to the note-rate term, whose factor is… | 3.439 | ratio | vif |  | eq | `[[art:88879cb2:vif.burnout]]` | verified | 3.439328594 |
| 270 | sensitivity | That maximum belongs to the note-rate term, whose factor is… | 2.929 | ratio | vif |  | eq | `[[art:5573d536:vif.loan_age]]` | verified | 2.928871763 |
| 271 | sensitivity | The remaining retained features sit lower still, down to a s… | 1.004 | ratio | vif |  | eq | `[[art:669c5fcb:vif.season_sin]]` | verified | 1.004128844 |
| 272 | sensitivity | Belsley's condition number of the column-standardised design… | 4.943 | ratio | condition_number |  | eq | `[[art:4f06a3c5:condition_number]]` | verified | 4.942565522 |
| 273 | sensitivity | Belsley's condition number of the column-standardised design… | 30 | ratio | condition_number |  | eq | `[[art:7e52fd7a:threshold.M1.condition_number]]` | verified | 30 |
| 274 | sensitivity | The declared tolerance on the AUC difference across regimes… | 0.1 | ratio | auc_gap |  | eq | `[[art:b64213d7:threshold.R1.auc_gap]]` | verified | 0.1 |
| 275 | sensitivity | A coefficient sign change is screened as material only where… | 0.05 | ratio | coefficient |  | eq | `[[art:aca84377:threshold.R1.sign_flip_coef]]` | verified | 0.05 |
| 276 | sensitivity | A coefficient sign change is screened as material only where… | 2 | ratio | sign_flip_z |  | eq | `[[art:2e4428c7:threshold.R1.sign_flip_z]]` | verified | 2 |
| 277 | sensitivity | No screened feature meets that condition, the indicator read… | 0 | ratio | sign_flip |  | eq | `[[art:0cc7a37d:stability.incentive.sign_flip]]` | verified | 0 |
| 278 | sensitivity | No screened feature meets that condition, the indicator read… | 0 | ratio | sign_flip |  | eq | `[[art:e7ce4912:stability.note_rate.sign_flip]]` | verified | 0 |
| 279 | sensitivity | No screened feature meets that condition, the indicator read… | 0 | ratio | sign_flip |  | eq | `[[art:1f302ccd:stability.sato.sign_flip]]` | verified | 0 |
| 280 | sensitivity | No screened feature meets that condition, the indicator read… | 0 | ratio | sign_flip |  | eq | `[[art:6bc05e82:stability.burnout.sign_flip]]` | verified | 0 |
| 281 | sensitivity | No screened feature meets that condition, the indicator read… | 0 | ratio | sign_flip |  | eq | `[[art:b7191217:stability.loan_age.sign_flip]]` | verified | 0 |
| 282 | sensitivity | No screened feature meets that condition, the indicator read… | 0 | ratio | sign_flip |  | eq | `[[art:d956c276:stability.credit_score.sign_flip]]` | verified | 0 |
| 283 | sensitivity | No screened feature meets that condition, the indicator read… | 0 | ratio | sign_flip |  | eq | `[[art:054d5fab:stability.orig_ltv.sign_flip]]` | verified | 0 |
| 284 | sensitivity | No screened feature meets that condition, the indicator read… | 0 | ratio | sign_flip |  | eq | `[[art:fb1ae6c8:stability.orig_upb_log.sign_flip]]` | verified | 0 |
| 285 | sensitivity | No screened feature meets that condition, the indicator read… | 0 | ratio | sign_flip |  | eq | `[[art:6ba36a3b:stability.season_sin.sign_flip]]` | verified | 0 |
| 286 | sensitivity | No screened feature meets that condition, the indicator read… | 0 | ratio | sign_flip |  | eq | `[[art:1850e2de:stability.season_cos.sign_flip]]` | verified | 0 |
| 287 | sensitivity | At the downward extreme of the grid the servicing value chan… | -1298000 | currency | value_change |  | eq | `[[art:4829926e:scenario.value_change.-300]]` | verified | -1297986.399 |
| 288 | sensitivity | At the downward extreme of the grid the servicing value chan… | 168100 | currency | value_change |  | eq | `[[art:38e75872:scenario.value_change.300]]` | verified | 168054.7452 |
| 289 | sensitivity | The intermediate steps run -854300 , -322600 , 0 , 119600 an… | -854300 | currency | value_change |  | eq | `[[art:03816874:scenario.value_change.-200]]` | verified | -854265.8614 |
| 290 | sensitivity | The intermediate steps run -854300 , -322600 , 0 , 119600 an… | -322600 | currency | value_change |  | eq | `[[art:d33e8e3c:scenario.value_change.-100]]` | verified | -322648.7678 |
| 291 | sensitivity | The intermediate steps run -854300 , -322600 , 0 , 119600 an… | 0 | currency | value_change |  | eq | `[[art:1e1b0b88:scenario.value_change.0]]` | verified | 0 |
| 292 | sensitivity | The intermediate steps run -854300 , -322600 , 0 , 119600 an… | 119600 | currency | value_change |  | eq | `[[art:d0970bd9:scenario.value_change.100]]` | verified | 119555.7352 |
| 293 | sensitivity | The intermediate steps run -854300 , -322600 , 0 , 119600 an… | 157000 | currency | value_change |  | eq | `[[art:d69c2be1:scenario.value_change.200]]` | verified | 156987.0553 |
| 294 | sensitivity | The sum of the change at the downward extreme and the change… | -1130000 | currency | convexity |  | eq | `[[art:538e0e09:scenario.convexity]]` | verified | -1129931.654 |
| 295 | findings | - On the test split, where AUC over the whole split is 0.775… | 0.7753 | ratio | auc | test | eq | `[[art:57066271:metrics.test.auc]]` | verified | 0.7752553922 |
| 296 | findings | - On the test split, where AUC over the whole split is 0.775… | 0.6824 | ratio | auc | test | eq | `[[art:0f9a3d96:metrics.test.sub.incentive_low.auc]]` | verified | 0.6824295208 |
| 297 | findings | - On the test split, where AUC over the whole split is 0.775… | 0.09283 | ratio | auc_gap | test | eq | `[[art:a0523ad8:metrics.test.sub.incentive_low.auc_gap]]` | verified | 0.09282587144 |
| 298 | findings | - On the test split, where AUC over the whole split is 0.775… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 299 | findings | - On the test split, where AUC over the whole split is 0.775… | 0.5 | ratio | share | test | eq | `[[art:1d5dd4c2:metrics.test.sub.incentive_low.share]]` | verified | 0.5 |
| 300 | findings | - On the test split, where AUC over the whole split is 0.775… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 301 | findings | - On the vintage_holdout split, where AUC over the whole spl… | 0.7718 | ratio | auc | vintage_holdout | eq | `[[art:ac6794c5:metrics.vintage_holdout.auc]]` | verified | 0.7717974135 |
| 302 | findings | - On the vintage_holdout split, where AUC over the whole spl… | 0.6724 | ratio | auc | vintage_holdout | eq | `[[art:0510c841:metrics.vintage_holdout.sub.incentive_low.auc]]` | verified | 0.6723509624 |
| 303 | findings | - On the vintage_holdout split, where AUC over the whole spl… | 0.09945 | ratio | auc_gap | vintage_holdout | eq | `[[art:9de83338:metrics.vintage_holdout.sub.incentive_low.auc_gap]]` | verified | 0.09944645103 |
| 304 | findings | - On the vintage_holdout split, where AUC over the whole spl… | 0.08 | ratio | slice_auc_gap |  | eq | `[[art:0a827b87:threshold.O1.slice_auc_gap]]` | verified | 0.08 |
| 305 | findings | - On the vintage_holdout split, where AUC over the whole spl… | 0.5 | ratio | share | vintage_holdout | eq | `[[art:d94e6531:metrics.vintage_holdout.sub.incentive_low.share]]` | verified | 0.500015539 |
| 306 | findings | - On the vintage_holdout split, where AUC over the whole spl… | 0.1 | ratio | slice_min_share |  | eq | `[[art:9a6f1a87:threshold.O1.slice_min_share]]` | verified | 0.1 |
| 307 | findings | - The fitted coefficient on `note_rate` carries sign -1 wher… | -1 | ratio | coef_sign |  | eq | `[[art:aecf7ccb:sign_check.note_rate.coef_sign]]` | verified | -1 |
| 308 | findings | - The fitted coefficient on `note_rate` carries sign -1 wher… | 1 | ratio | univariate_direction | train | eq | `[[art:61f6e1ac:sign_check.note_rate.univariate_direction]]` | verified | 1 |
| 309 | findings | - The fitted coefficient on `note_rate` carries sign -1 wher… | 0 | ratio | agrees |  | eq | `[[art:a453463d:sign_check.note_rate.agrees]]` | verified | 0 |
| 310 | monitoring | **Calibration.** Report, for each production vintage, the sl… | 0.8 | ratio | calibration_slope | test | eq | `[[art:95fdb848:threshold.package.calibration_slope.test.min]]` | verified | 0.8 |
| 311 | monitoring | **Calibration.** Report, for each production vintage, the sl… | 1.2 | ratio | calibration_slope | test | eq | `[[art:0adb7a89:threshold.package.calibration_slope.test.max]]` | verified | 1.2 |
| 312 | monitoring | The validation reading of 0.9365 sits inside that band and s… | 0.9365 | ratio | calibration_slope | test | eq | `[[art:3e42ee62:calibration_slope.test]]` | verified | 0.9365180494 |
| 313 | monitoring | **Discrimination.** Report the area under the ROC curve on e… | 0.65 | ratio | auc | test | eq | `[[art:fececac1:threshold.package.auc.test.min]]` | verified | 0.65 |
| 314 | monitoring | **Discrimination.** Report the area under the ROC curve on e… | 0.7753 | ratio | auc | test | eq | `[[art:57066271:metrics.test.auc]]` | verified | 0.7752553922 |
| 315 | monitoring | **Input and score stability.** Report the population stabili… | 0.25 | ratio | psi |  | eq | `[[art:fbb5a9d1:threshold.package.psi.max]]` | verified | 0.25 |
| 316 | monitoring | The largest such reading in this validation was 0.06189 , we… | 0.06189 | ratio | psi |  | eq | `[[art:c2e8c8fd:psi.max]]` | verified | 0.06188985797 |

## Appendix B — Artifact index

The store holds 467 artifacts; the 260 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `ablation.baseline_auc` | `54367df6` | scalar | 0.7672992275 | AUC on test of a refit of the champion's functional form on every retained feature, the level each ablation delta is measured from |
| `ablation.burnout.delta_auc` | `3cba039b` | scalar | -0.0001876329287 | change in test AUC when the champion's form is refitted without burnout |
| `ablation.credit_score.delta_auc` | `9bdeb0df` | scalar | -0.0147431913 | change in test AUC when the champion's form is refitted without credit_score |
| `ablation.incentive.delta_auc` | `78108590` | scalar | -0.0411745927 | change in test AUC when the champion's form is refitted without incentive |
| `ablation.loan_age.delta_auc` | `be669163` | scalar | 0.0008165996474 | change in test AUC when the champion's form is refitted without loan_age |
| `ablation.note_rate.delta_auc` | `14558b82` | scalar | -0.002585106068 | change in test AUC when the champion's form is refitted without note_rate |
| `ablation.orig_ltv.delta_auc` | `57ea66c5` | scalar | -0.002294407165 | change in test AUC when the champion's form is refitted without orig_ltv |
| `ablation.orig_upb_log.delta_auc` | `0ddb11a9` | scalar | -0.01926646624 | change in test AUC when the champion's form is refitted without orig_upb_log |
| `ablation.sato.delta_auc` | `57703504` | scalar | 0.0005200867657 | change in test AUC when the champion's form is refitted without sato |
| `ablation.season_cos.delta_auc` | `a288439d` | scalar | -0.00048256018 | change in test AUC when the champion's form is refitted without season_cos |
| `ablation.season_sin.delta_auc` | `e54c8581` | scalar | -0.0003884794439 | change in test AUC when the champion's form is refitted without season_sin |
| `calibration.mean_rel_gap.out_of_time` | `c599bd89` | scalar | 0.05108730888 | mean predicted against observed on out_of_time, relative |
| `calibration.mean_rel_gap.test` | `59b8a1f5` | scalar | 0.006754602372 | mean predicted against observed on test, relative |
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
| `challenger.auc` | `705b66f0` | scalar | 0.7337079121 | the challenger's AUC on test |
| `challenger.brier` | `85a89ef9` | scalar | 0.008629514666 | the challenger's Brier score on test |
| `challenger.delta_auc` | `4d28c096` | scalar | -0.04154748012 | the challenger's AUC on test minus the champion's |
| `condition_number` | `4f06a3c5` | scalar | 4.942565522 | Belsley's condition number of the column-standardised design |
| `cpr.out_of_time.mae` | `a7ecd72b` | scalar | 0.05856944955 | mean absolute difference between actual and predicted CPR on out_of_time |
| `cpr.test` | `ecbd1494` | table | table, 71 rows | actual against predicted CPR by period on test |
| `cpr.test.mae` | `ff266c97` | scalar | 0.042636033 | mean absolute difference between actual and predicted CPR on test |
| `cpr.train.mae` | `f2c3683c` | scalar | 0.02657629251 | mean absolute difference between actual and predicted CPR on train |
| `cpr.vintage_holdout.mae` | `172ebed4` | scalar | 0.0289048118 | mean absolute difference between actual and predicted CPR on vintage_holdout |
| `csi.burnout` | `b2729e08` | scalar | 0.0009851123767 | CSI of burnout: its contribution to the shift in the linear predictor |
| `csi.credit_score` | `c40b4ede` | scalar | 0.007908848663 | CSI of credit_score: its contribution to the shift in the linear predictor |
| `csi.incentive` | `874ef644` | scalar | 0.005803522882 | CSI of incentive: its contribution to the shift in the linear predictor |
| `csi.loan_age` | `df52c920` | scalar | 0 | CSI of loan_age: its contribution to the shift in the linear predictor |
| `csi.max` | `54bd75b0` | scalar | 0.03438094941 | the largest characteristic stability index |
| `csi.note_rate` | `92901ac4` | scalar | 0.01822065751 | CSI of note_rate: its contribution to the shift in the linear predictor |
| `csi.orig_ltv` | `97d51193` | scalar | 0.03438094941 | CSI of orig_ltv: its contribution to the shift in the linear predictor |
| `csi.orig_upb_log` | `bb919ade` | scalar | 0.00296903904 | CSI of orig_upb_log: its contribution to the shift in the linear predictor |
| `csi.sato` | `6a5f7a41` | scalar | 0.001487358985 | CSI of sato: its contribution to the shift in the linear predictor |
| `csi.season_cos` | `75b544aa` | scalar | 0.0004785421555 | CSI of season_cos: its contribution to the shift in the linear predictor |
| `csi.season_sin` | `d55271d6` | scalar | 7.624273793e-05 | CSI of season_sin: its contribution to the shift in the linear predictor |
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
| `metrics.out_of_time.sub.burnout_high` | `322f57c1` | table | table, 10 rows | every metric on the burnout above_median slice of out_of_time |
| `metrics.out_of_time.sub.burnout_high.auc_gap` | `fc407765` | scalar | 0.008042921487 | how far AUC on the burnout above_median slice of out_of_time falls below AUC on all of out_of_time |
| `metrics.out_of_time.sub.burnout_high.mean_rel_gap` | `56cf9db6` | scalar | 0.3183858398 | mean predicted against observed on the burnout above_median slice of out_of_time, relative |
| `metrics.out_of_time.sub.burnout_high.share` | `b5c30bbc` | scalar | 0.499959207 | the share of out_of_time the burnout above_median slice holds |
| `metrics.out_of_time.sub.burnout_low` | `f6714bf8` | table | table, 10 rows | every metric on the burnout below_median slice of out_of_time |
| `metrics.out_of_time.sub.burnout_low.auc_gap` | `36fd04a3` | scalar | -0.02568035627 | how far AUC on the burnout below_median slice of out_of_time falls below AUC on all of out_of_time |
| `metrics.out_of_time.sub.burnout_low.mean_rel_gap` | `fc98bff4` | scalar | 0.263848584 | mean predicted against observed on the burnout below_median slice of out_of_time, relative |
| `metrics.out_of_time.sub.burnout_low.share` | `d6102b4a` | scalar | 0.500040793 | the share of out_of_time the burnout below_median slice holds |
| `metrics.out_of_time.sub.incentive_high` | `6c7182e4` | table | table, 10 rows | every metric on the incentive above_median slice of out_of_time |
| `metrics.out_of_time.sub.incentive_high.auc_gap` | `1c0207f9` | scalar | 0.0373425714 | how far AUC on the incentive above_median slice of out_of_time falls below AUC on all of out_of_time |
| `metrics.out_of_time.sub.incentive_high.mean_rel_gap` | `f0899b32` | scalar | 0.123516925 | mean predicted against observed on the incentive above_median slice of out_of_time, relative |
| `metrics.out_of_time.sub.incentive_high.share` | `431d1ff2` | scalar | 0.499877621 | the share of out_of_time the incentive above_median slice holds |
| `metrics.out_of_time.sub.incentive_low` | `1ebd5e5e` | table | table, 10 rows | every metric on the incentive below_median slice of out_of_time |
| `metrics.out_of_time.sub.incentive_low.auc_gap` | `faa1a185` | scalar | 0.01629917634 | how far AUC on the incentive below_median slice of out_of_time falls below AUC on all of out_of_time |
| `metrics.out_of_time.sub.incentive_low.mean_rel_gap` | `81d9f6b7` | scalar | 0.2155153206 | mean predicted against observed on the incentive below_median slice of out_of_time, relative |
| `metrics.out_of_time.sub.incentive_low.share` | `c7aaafd2` | scalar | 0.500122379 | the share of out_of_time the incentive below_median slice holds |
| `metrics.test.auc` | `57066271` | scalar | 0.7752553922 | auc on test, recomputed by quaestor |
| `metrics.test.brier` | `7d3583cd` | scalar | 0.00789356705 | brier on test, recomputed by quaestor |
| `metrics.test.event_rate` | `570cc08a` | scalar | 0.008061370433 | event_rate on test, recomputed by quaestor |
| `metrics.test.gini` | `fe7f75d7` | scalar | 0.5505107844 | gini on test, recomputed by quaestor |
| `metrics.test.ks` | `c569c301` | scalar | 0.4161772354 | ks on test, recomputed by quaestor |
| `metrics.test.logloss` | `320e4c6b` | scalar | 0.04263297829 | logloss on test, recomputed by quaestor |
| `metrics.test.mean_predicted` | `3bc93911` | scalar | 0.008115821785 | mean_predicted on test, recomputed by quaestor |
| `metrics.test.n` | `e55953e1` | scalar | 15382 | n on test, recomputed by quaestor |
| `metrics.test.sub.burnout_high` | `92eab39d` | table | table, 10 rows | every metric on the burnout above_median slice of test |
| `metrics.test.sub.burnout_high.auc_gap` | `9dce50b2` | scalar | 0.05082182845 | how far AUC on the burnout above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.burnout_high.mean_rel_gap` | `da3a2aa8` | scalar | 0.006955749093 | mean predicted against observed on the burnout above_median slice of test, relative |
| `metrics.test.sub.burnout_high.share` | `ec1e0d04` | scalar | 0.5 | the share of test the burnout above_median slice holds |
| `metrics.test.sub.burnout_low` | `4faad122` | table | table, 10 rows | every metric on the burnout below_median slice of test |
| `metrics.test.sub.burnout_low.auc_gap` | `acc515db` | scalar | 0.03171500332 | how far AUC on the burnout below_median slice of test falls below AUC on all of test |
| `metrics.test.sub.burnout_low.mean_rel_gap` | `6ef3aca5` | scalar | 0.006064956473 | mean predicted against observed on the burnout below_median slice of test, relative |
| `metrics.test.sub.burnout_low.share` | `2cb9dc34` | scalar | 0.5 | the share of test the burnout below_median slice holds |
| `metrics.test.sub.incentive_high` | `142c806c` | table | table, 10 rows | every metric on the incentive above_median slice of test |
| `metrics.test.sub.incentive_high.auc_gap` | `5a0ba9c4` | scalar | 0.04840270693 | how far AUC on the incentive above_median slice of test falls below AUC on all of test |
| `metrics.test.sub.incentive_high.mean_rel_gap` | `f90b2790` | scalar | 0.03491504769 | mean predicted against observed on the incentive above_median slice of test, relative |
| `metrics.test.sub.incentive_high.share` | `549aa934` | scalar | 0.5 | the share of test the incentive above_median slice holds |
| `metrics.test.sub.incentive_low` | `53406e16` | table | table, 10 rows | every metric on the incentive below_median slice of test |
| `metrics.test.sub.incentive_low.auc` | `0f9a3d96` | scalar | 0.6824295208 | auc on the incentive below_median slice of test |
| `metrics.test.sub.incentive_low.auc_gap` | `a0523ad8` | scalar | 0.09282587144 | how far AUC on the incentive below_median slice of test falls below AUC on all of test |
| `metrics.test.sub.incentive_low.mean_rel_gap` | `aede705c` | scalar | 0.1169064836 | mean predicted against observed on the incentive below_median slice of test, relative |
| `metrics.test.sub.incentive_low.share` | `1d5dd4c2` | scalar | 0.5 | the share of test the incentive below_median slice holds |
| `metrics.train.auc` | `fa609ae1` | scalar | 0.7883327303 | auc on train, recomputed by quaestor |
| `metrics.train.brier` | `83666c70` | scalar | 0.008317491392 | brier on train, recomputed by quaestor |
| `metrics.train.event_rate` | `b9ef3327` | scalar | 0.008524699414 | event_rate on train, recomputed by quaestor |
| `metrics.train.gini` | `0b6b2058` | scalar | 0.5766654607 | gini on train, recomputed by quaestor |
| `metrics.train.ks` | `c355478b` | scalar | 0.4562056834 | ks on train, recomputed by quaestor |
| `metrics.train.logloss` | `199c7db5` | scalar | 0.04408402922 | logloss on train, recomputed by quaestor |
| `metrics.train.mean_predicted` | `a63f6555` | scalar | 0.008426526894 | mean_predicted on train, recomputed by quaestor |
| `metrics.train.n` | `6fdfeabb` | scalar | 36013 | n on train, recomputed by quaestor |
| `metrics.train.sub.burnout_high` | `66fd45a2` | table | table, 10 rows | every metric on the burnout above_median slice of train |
| `metrics.train.sub.burnout_high.auc_gap` | `c5d72bde` | scalar | 0.03693754896 | how far AUC on the burnout above_median slice of train falls below AUC on all of train |
| `metrics.train.sub.burnout_high.mean_rel_gap` | `7b4ba231` | scalar | 0.0009104580871 | mean predicted against observed on the burnout above_median slice of train, relative |
| `metrics.train.sub.burnout_high.share` | `31040ed8` | scalar | 0.4999861161 | the share of train the burnout above_median slice holds |
| `metrics.train.sub.burnout_low` | `b3d9b1ff` | table | table, 10 rows | every metric on the burnout below_median slice of train |
| `metrics.train.sub.burnout_low.auc_gap` | `7a5c3299` | scalar | 0.03834607983 | how far AUC on the burnout below_median slice of train falls below AUC on all of train |
| `metrics.train.sub.burnout_low.mean_rel_gap` | `c979f2dc` | scalar | 0.0528219024 | mean predicted against observed on the burnout below_median slice of train, relative |
| `metrics.train.sub.burnout_low.share` | `9d770878` | scalar | 0.5000138839 | the share of train the burnout below_median slice holds |
| `metrics.train.sub.incentive_high` | `58071691` | table | table, 10 rows | every metric on the incentive above_median slice of train |
| `metrics.train.sub.incentive_high.auc_gap` | `8d8827f2` | scalar | 0.07015660217 | how far AUC on the incentive above_median slice of train falls below AUC on all of train |
| `metrics.train.sub.incentive_high.mean_rel_gap` | `7d3d3639` | scalar | 0.01445428336 | mean predicted against observed on the incentive above_median slice of train, relative |
| `metrics.train.sub.incentive_high.share` | `277218fb` | scalar | 0.4999861161 | the share of train the incentive above_median slice holds |
| `metrics.train.sub.incentive_low` | `9c590135` | table | table, 10 rows | every metric on the incentive below_median slice of train |
| `metrics.train.sub.incentive_low.auc_gap` | `134d7c07` | scalar | 0.06702950807 | how far AUC on the incentive below_median slice of train falls below AUC on all of train |
| `metrics.train.sub.incentive_low.mean_rel_gap` | `05adce6c` | scalar | 0.003953431529 | mean predicted against observed on the incentive below_median slice of train, relative |
| `metrics.train.sub.incentive_low.share` | `d7af12f0` | scalar | 0.5000138839 | the share of train the incentive below_median slice holds |
| `metrics.vintage_holdout.auc` | `ac6794c5` | scalar | 0.7717974135 | auc on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.brier` | `f3c6bdcc` | scalar | 0.004763025704 | brier on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.event_rate` | `e3590a16` | scalar | 0.004817105386 | event_rate on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.gini` | `a4a532f0` | scalar | 0.5435948269 | gini on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.ks` | `b5b9e888` | scalar | 0.4515647508 | ks on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.logloss` | `c32e3713` | scalar | 0.02810570342 | logloss on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.mean_predicted` | `5ae28866` | scalar | 0.005646788012 | mean_predicted on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.n` | `37a92951` | scalar | 32177 | n on vintage_holdout, recomputed by quaestor |
| `metrics.vintage_holdout.sub.burnout_high` | `bf16f833` | table | table, 10 rows | every metric on the burnout above_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.burnout_high.auc_gap` | `b2bfad0a` | scalar | 0.03809536629 | how far AUC on the burnout above_median slice of vintage_holdout falls below AUC on all of vintage_holdout |
| `metrics.vintage_holdout.sub.burnout_high.mean_rel_gap` | `f497ef02` | scalar | 0.05320653872 | mean predicted against observed on the burnout above_median slice of vintage_holdout, relative |
| `metrics.vintage_holdout.sub.burnout_high.share` | `379549be` | scalar | 0.499984461 | the share of vintage_holdout the burnout above_median slice holds |
| `metrics.vintage_holdout.sub.burnout_low` | `ba6fbd31` | table | table, 10 rows | every metric on the burnout below_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.burnout_low.auc_gap` | `180537c0` | scalar | 0.02592501233 | how far AUC on the burnout below_median slice of vintage_holdout falls below AUC on all of vintage_holdout |
| `metrics.vintage_holdout.sub.burnout_low.mean_rel_gap` | `508e2e1f` | scalar | 0.6122878825 | mean predicted against observed on the burnout below_median slice of vintage_holdout, relative |
| `metrics.vintage_holdout.sub.burnout_low.share` | `b327a747` | scalar | 0.500015539 | the share of vintage_holdout the burnout below_median slice holds |
| `metrics.vintage_holdout.sub.incentive_high` | `672368b3` | table | table, 10 rows | every metric on the incentive above_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.incentive_high.auc_gap` | `2ebd6757` | scalar | 0.01874804418 | how far AUC on the incentive above_median slice of vintage_holdout falls below AUC on all of vintage_holdout |
| `metrics.vintage_holdout.sub.incentive_high.mean_rel_gap` | `d14397a7` | scalar | 0.2975984466 | mean predicted against observed on the incentive above_median slice of vintage_holdout, relative |
| `metrics.vintage_holdout.sub.incentive_high.share` | `cb627056` | scalar | 0.499984461 | the share of vintage_holdout the incentive above_median slice holds |
| `metrics.vintage_holdout.sub.incentive_low` | `10caac80` | table | table, 10 rows | every metric on the incentive below_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.incentive_low.auc` | `0510c841` | scalar | 0.6723509624 | auc on the incentive below_median slice of vintage_holdout |
| `metrics.vintage_holdout.sub.incentive_low.auc_gap` | `9de83338` | scalar | 0.09944645103 | how far AUC on the incentive below_median slice of vintage_holdout falls below AUC on all of vintage_holdout |
| `metrics.vintage_holdout.sub.incentive_low.mean_rel_gap` | `20691619` | scalar | 0.2421532582 | mean predicted against observed on the incentive below_median slice of vintage_holdout, relative |
| `metrics.vintage_holdout.sub.incentive_low.share` | `d94e6531` | scalar | 0.500015539 | the share of vintage_holdout the incentive below_median slice holds |
| `profile.out_of_time.missing.max` | `4dafce11` | scalar | 0 | the largest missing fraction in out_of_time |
| `profile.out_of_time.n` | `fa39c5cf` | scalar | 12257 | rows in out_of_time |
| `profile.test.missing.max` | `f813848d` | scalar | 0 | the largest missing fraction in test |
| `profile.test.n` | `e3abc1b8` | scalar | 15382 | rows in test |
| `profile.train.missing.max` | `050a3099` | scalar | 0 | the largest missing fraction in train |
| `profile.train.n` | `c5ebd9c9` | scalar | 36013 | rows in train |
| `profile.vintage_holdout.missing.max` | `329bb430` | scalar | 0 | the largest missing fraction in vintage_holdout |
| `profile.vintage_holdout.n` | `426e712a` | scalar | 32177 | rows in vintage_holdout |
| `psi.burnout` | `9dc7ecc2` | scalar | 0.004614338236 | PSI of burnout between train and test |
| `psi.credit_score` | `7e87527c` | scalar | 0.06188985797 | PSI of credit_score between train and test |
| `psi.incentive` | `2da5570f` | scalar | 0.0009922551416 | PSI of incentive between train and test |
| `psi.loan_age` | `2202b157` | scalar | 0.0001993816816 | PSI of loan_age between train and test |
| `psi.max` | `c2e8c8fd` | scalar | 0.06188985797 | the largest train-to-test PSI, score included |
| `psi.note_rate` | `ecc6adf3` | scalar | 0.01370911382 | PSI of note_rate between train and test |
| `psi.orig_ltv` | `cd1ff136` | scalar | 0.03617297258 | PSI of orig_ltv between train and test |
| `psi.orig_upb_log` | `55030a3b` | scalar | 0.04817081196 | PSI of orig_upb_log between train and test |
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
| `psi.out_of_time.y_score` | `2dc61374` | scalar | 0.7055906656 | PSI of the score between train and out_of_time |
| `psi.sato` | `584da64f` | scalar | 0.02772829856 | PSI of sato between train and test |
| `psi.season_cos` | `addec503` | scalar | 1.790085913e-05 | PSI of season_cos between train and test |
| `psi.season_sin` | `4d2ed98d` | scalar | 2.939045338e-06 | PSI of season_sin between train and test |
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
| `psi.vintage_holdout.y_score` | `3713457e` | scalar | 0.142110315 | PSI of the score between train and vintage_holdout |
| `psi.y_score` | `3b9dee2d` | scalar | 0.001952903716 | PSI of the score between train and test |
| `run.features` | `61276a96` | json | json | the subject's features.json |
| `run.model_summary` | `b764932a` | json | json | the subject's model_summary.json |
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
| `sign_check.burnout.agrees` | `2eec20ab` | scalar | 1 | 1 when the fitted sign on burnout agrees with its univariate direction, 0 when it does not |
| `sign_check.credit_score.agrees` | `915bf8eb` | scalar | 1 | 1 when the fitted sign on credit_score agrees with its univariate direction, 0 when it does not |
| `sign_check.incentive.agrees` | `f7b2338e` | scalar | 1 | 1 when the fitted sign on incentive agrees with its univariate direction, 0 when it does not |
| `sign_check.incentive.coef_sign` | `684cf11a` | scalar | 1 | the sign of the fitted coefficient on incentive |
| `sign_check.incentive.univariate_direction` | `8098d951` | scalar | 1 | the sign of incentive's own single-feature AUC on train minus 0.5 |
| `sign_check.n_disagreements` | `f96ece96` | scalar | 1 | retained features whose fitted sign contradicts their univariate direction, of 9 checked |
| `sign_check.note_rate.agrees` | `a453463d` | scalar | 0 | 1 when the fitted sign on note_rate agrees with its univariate direction, 0 when it does not |
| `sign_check.note_rate.coef_sign` | `aecf7ccb` | scalar | -1 | the sign of the fitted coefficient on note_rate |
| `sign_check.note_rate.univariate_direction` | `61f6e1ac` | scalar | 1 | the sign of note_rate's own single-feature AUC on train minus 0.5 |
| `sign_check.orig_ltv.agrees` | `7021aeb0` | scalar | 1 | 1 when the fitted sign on orig_ltv agrees with its univariate direction, 0 when it does not |
| `sign_check.orig_ltv.coef_sign` | `7eec65ec` | scalar | -1 | the sign of the fitted coefficient on orig_ltv |
| `sign_check.orig_ltv.univariate_direction` | `76dbc708` | scalar | -1 | the sign of orig_ltv's own single-feature AUC on train minus 0.5 |
| `sign_check.orig_upb_log.agrees` | `07a9d3e6` | scalar | 1 | 1 when the fitted sign on orig_upb_log agrees with its univariate direction, 0 when it does not |
| `sign_check.sato.agrees` | `2401eba2` | scalar | 1 | 1 when the fitted sign on sato agrees with its univariate direction, 0 when it does not |
| `sign_check.season_cos.agrees` | `7f18ddf7` | scalar | 1 | 1 when the fitted sign on season_cos agrees with its univariate direction, 0 when it does not |
| `sign_check.season_sin.agrees` | `e110f357` | scalar | 1 | 1 when the fitted sign on season_sin agrees with its univariate direction, 0 when it does not |
| `stability.auc_by_regime` | `960f708f` | table | table, 2 rows | the champion's AUC within each rate_regime on train |
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
| `vif.burnout` | `88879cb2` | scalar | 3.439328594 | variance inflation factor of burnout on train |
| `vif.loan_age` | `5573d536` | scalar | 2.928871763 | variance inflation factor of loan_age on train |
| `vif.max` | `f9e0db60` | scalar | 4.975500767 | the largest variance inflation factor |
| `vif.note_rate` | `37532fa8` | scalar | 4.975500767 | variance inflation factor of note_rate on train |
| `vif.season_sin` | `669c5fcb` | scalar | 1.004128844 | variance inflation factor of season_sin on train |

## Appendix C — Run trace summary

| quantity | value |
|---|---|
| tool calls | 19 (run_model 1, profile_data 1, compute_metrics 5, check_leakage 1, check_stability 1, check_collinearity 1, challenger_compare 1, run_scenarios 1, retrieve_guidance 7) |
| plan steps (bounded loop) | 4 |
| LLM calls | 20 (plan 4, draft 8, extract 8) |
| re-asks | 0 |
| repair rounds | 1 |
| tokens in / out | 307,028 / 117,348 |
| notional cost (USD) | 6.0894 |
| wall-clock (s) | 1289.67 |
| subject run (s) | 2.89 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | msr_prepayment-full_agent-20260919T040539Z-e61d346a |

## Appendix D — Not checked

| item | reason |
|---|---|
| developer claims (T1, claim channel) | The package declares 3 developer claim(s) about its real fit; synthetic mode does not evaluate them, because a metric computed from the generating process has no bearing on a number declared for the real sample (DECISIONS D-016). |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
