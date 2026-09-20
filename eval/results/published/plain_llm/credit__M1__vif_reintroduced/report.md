---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: plain_llm
model: claude-opus-5[1m]
run_id: credit_default-plain_llm-20260918T182619Z-6e98ce62
data_mode: synthetic
synthetic_n: 5000
grounding_precision_pre: 0.0000
grounding_precision_post: 0.0000
n_claims: 200
n_findings_by_severity: {high: 1, medium: 1, low: 1, info: 1}
generated: "2026-09-18T18:26:19Z"
illustrative: false
---

# Validation report — `credit_default` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `credit_default` v1.0 | `plain_llm` | claude-opus-5[1m] | synthetic, n = 5000 | 0.0000 → 0.0000 | 1 / 1 / 1 / 1 |
<!-- quaestor:renderer:end -->

This report is a validation of package `credit_default` version 1.0, a binary classification model predicting `default_next_month` for credit card clients. The subject is a standardised logistic regression with ⟦unverified: 13⟧ features and an intercept of ⟦unverified: -1.3997⟧, fitted on ⟦unverified: 3,500⟧ training rows and evaluated on ⟦unverified: 1,500⟧ held-out test rows ([[art:f2e0e9a7:run.model_summary]], [[art:3b6b0a38:run.splits]]).

The validation covers conceptual soundness, data integrity, outcomes analysis, and such sensitivity analysis as the artifact store supports. It is based **solely** on the artifacts the developer produced; no re-estimation, no independent data pull, and no challenger model was available to the validator. The scope limitations this imposes are stated explicitly in sections ⟦unverified: 3⟧ and ⟦unverified: 5⟧ and should be read as part of the conclusion.

Headline results. Discrimination is adequate and stable: test AUC ⟦unverified: 0.7505⟧, Gini ⟦unverified: 0.5009⟧, KS ⟦unverified: 0.4317⟧; train AUC ⟦unverified: 0.7607⟧, Gini ⟦unverified: 0.5215⟧, KS ⟦unverified: 0.4489⟧ ([[art:c586d0a7:run.metrics]]). The train-to-test AUC gap is ⟦unverified: 0.0102⟧, well inside any conventional degradation tolerance, so there is no evidence of overfitting at the performance level. Aggregate calibration is good: mean predicted probability on train is ⟦unverified: 0.22455⟧ against an observed event rate of ⟦unverified: 0.22457⟧, and on test ⟦unverified: 0.22148⟧ against ⟦unverified: 0.22467⟧. Brier scores are effectively identical across splits (⟦unverified: 0.14861⟧ train, ⟦unverified: 0.14863⟧ test).

The material problem is not performance but structure. The feature set contains a near-duplicate pair, `bill_last` and `bill_last_adj`, whose univariate moments agree to within a rounding error, and the developer's declared VIF screen at threshold ⟦unverified: 10.0⟧ removed nothing (`"removed": []`). The fitted coefficient vector shows the expected symptoms of variance inflation: inflated, oppositely-signed loadings within the billing block and within two other correlated feature families. The model as fitted is usable for ranking but its coefficients are not interpretable, not stable, and should not be relied on for attribution, adverse-action reason codes, or any downstream sensitivity work.

**Overall assessment: approve for ranking use only, conditional on remediation of the collinearity defect and on completion of the monitoring and challenger work that the artifact store does not currently evidence.**

## 2. Conceptual soundness

The model form — a standardised logistic regression on ⟦unverified: 13⟧ continuous predictors — is appropriate for a binary default outcome and is the conventional choice for this use case. It is transparent, monotone in each predictor, and produces calibrated probabilities directly. No objection is raised to the functional form.

**Feature timing.** The feature manifest ([[art:f79bb8bb:run.features]]) declares ⟦unverified: 2⟧ features `at_origination` (`limit_bal`, `age`), ⟦unverified: 11⟧ `before_period_start`, ⟦unverified: 0⟧ `during_period`, and ⟦unverified: 0⟧ `after_outcome`. On the developer's own declarations there is no target leakage: every predictor is observable strictly before the performance window opens. The counts reconcile to the declared n of ⟦unverified: 13⟧ and to the ⟦unverified: 13⟧ coefficients in the model summary. No feature is declared post-outcome, and no per-feature discrimination artifact was supplied that would allow the validator to test the second leakage criterion (a single feature scoring AUC > ⟦unverified: 0.90⟧) independently. Given an overall model AUC of ⟦unverified: 0.7505⟧, a single feature above ⟦unverified: 0.90⟧ is arithmetically implausible, so leakage is judged unlikely rather than ruled out.

**Coefficient plausibility.** This is where the model fails conceptual review. Three feature families each contain a sign reversal between members that economic reasoning says should point the same way:

- *Billing level.* `bill_mean_6m` loads +⟦unverified: 0.6805⟧ while `bill_last` loads ⟦unverified: -0.5348⟧ and `bill_last_adj` loads ⟦unverified: -0.5619⟧. These three variables measure the same quantity — outstanding bill size — at nearly the same moment. Their net contribution to a joint one-standard-deviation rise in billing is ⟦unverified: 0.6805⟧ - ⟦unverified: 0.5348⟧ - ⟦unverified: 0.5619⟧ = **⟦unverified: -0.416⟧ log-odds**, i.e. the model says that clients with larger bills are *less* likely to default, holding everything else at the mean. That is the wrong sign for a credit risk model and it is produced entirely by the way the collinear decomposition splits a single underlying effect across three loadings.
- *Payment behaviour.* `pay_ratio_mean_6m` loads ⟦unverified: -0.3621⟧ (correct: paying down more of the bill lowers risk) while `pay_ratio_last` loads +⟦unverified: 0.1093⟧ (wrong sign). The net of ⟦unverified: -0.2528⟧ is directionally sensible, but the individual loadings are not, and either coefficient taken alone would mislead a reviewer.
- *Delinquency.* `delinq_last` (+⟦unverified: 0.7357⟧) and `delinq_count_6m` (+⟦unverified: 0.1219⟧) carry the expected positive sign; `delinq_max_6m` is ⟦unverified: -0.0322⟧. The magnitude here is small and the net (+⟦unverified: 0.8253⟧) is strongly and correctly positive, so this is the least serious of the three, but it is the same pathology.

`limit_bal` at +⟦unverified: 0.1149⟧ is also worth flagging: a larger credit limit is normally underwritten to better-quality clients and should, if anything, reduce risk. `age` at ⟦unverified: -0.0672⟧ (younger clients riskier) and `utilisation` at +⟦unverified: 0.1640⟧ are both conventionally signed.

Singly, any one sign reversal might be defended as a genuine conditional effect. Three of them, concentrated inside three correlated families, in a model that declares a VIF screen and then removes nothing, are not three coincidences. They are the fingerprint of an unaddressed multicollinearity problem (see section 6, finding M1).

**Documentation.** The model summary records `class_weight: null` — appropriate here, since the ⟦unverified: 22.5%⟧ event rate is not severe imbalance and the model is well calibrated as fitted. `standardised: true` is confirmed by the coefficient scale. No development rationale, feature selection log, variable definition dictionary, or model design document is present in the artifact store; in particular there is no documented definition of what the `_adj` suffix on `bill_last_adj` adjusts for, which is precisely the documentation that would have caught the duplicate.

## 3. Data integrity and drift

**Completeness.** The training profile shows `missing: 0.0` for all ⟦unverified: 15⟧ columns including the target ([[art:c522fc63:run.data_train]]). Complete data is a positive finding on its face, though for a credit bureau panel it is unusual enough to warrant a question: a real six-month billing history will normally have some clients with short tenure, and zero missingness across `bill_trend_6m` and all the `_6m` aggregates suggests either an inner-join that silently dropped short-tenure clients, or imputation performed upstream of the profile. Either would be a selection effect not visible in these artifacts.

**Split integrity.** Train and test carry distinct row hashes (`e028347d...` and `3e28943d...`) and the row counts sum to ⟦unverified: 5,000,⟧ matching the `client_id` range of ⟦unverified: 1⟧ to ⟦unverified: 5,000⟧ in the training profile. Event rates are near-identical across splits (⟦unverified: 0.224571⟧ train, ⟦unverified: 0.224667⟧ test), consistent with a stratified or a large random split. Nothing in the store evidences train/test row overlap, and no contamination finding is raised. The validator notes, however, that no per-client overlap check artifact exists; the absence of contamination is inferred from distinct hashes, not demonstrated.

**Distributional anomalies in the training profile.**

1. *The near-duplicate pair.* `bill_last` has mean ⟦unverified: 47,409.0966⟧ and standard deviation ⟦unverified: 44,429.8135⟧; `bill_last_adj` has mean ⟦unverified: 47,412.8452⟧ and standard deviation ⟦unverified: 44,429.8166⟧. The standard deviations agree to six significant figures and the means differ by ⟦unverified: 3.75⟧ on a scale of ⟦unverified: 47,000⟧ (⟦unverified: 0.008%⟧). The minima are ⟦unverified: 513.48⟧ and ⟦unverified: 513.5673⟧. These are not two variables; they are one variable and a negligible perturbation of it. The pairwise correlation is necessarily within rounding distance of 1.0. Curiously the maxima diverge more (⟦unverified: 536,181.78⟧ versus ⟦unverified: 535,345.13⟧), which suggests the adjustment is a small, mostly-zero correction applied to a handful of extreme rows.
2. *Capping.* `pay_ratio_last` has an exact maximum of ⟦unverified: 2.0000⟧ while `pay_ratio_mean_6m` peaks at ⟦unverified: 1.6385⟧. A maximum landing on a round 2.0 to full precision is a winsorisation cap, not a natural bound. The cap is nowhere declared in the feature manifest or model summary, and a capped variable that has been standardised will have a distorted upper tail.
3. *Out-of-range utilisation.* `utilisation` reaches ⟦unverified: 1.1297⟧ and `utilisation_mean_6m` reaches ⟦unverified: 1.4310⟧. Over-limit balances are legitimate in credit data, so this is not an error, but note that the six-month *mean* exceeds the last-month maximum, which implies sustained over-limit behaviour in some clients and is worth confirming rather than assuming.
4. *Skew.* `bill_trend_6m` has mean ⟦unverified: -237.6⟧ with standard deviation ⟦unverified: 3,118.5⟧, a minimum of ⟦unverified: -67,201⟧ and a maximum of +⟦unverified: 27,398⟧ — a heavy and asymmetric left tail, roughly ⟦unverified: 21⟧ standard deviations to the downside against ⟦unverified: 9⟧ to the upside. Standardisation does not fix skew of this order, and the feature's coefficient (⟦unverified: -0.0240⟧) is among the smallest in the model, consistent with the tail dominating the scaling and flattening the informative central range.
5. *Identifier hygiene.* `client_id` is present in the profiled table with mean ⟦unverified: 2,513.9⟧. It does not appear in the feature manifest and is not among the ⟦unverified: 13⟧ coefficients, so it was correctly excluded from the fit; this is noted only to confirm the exclusion.

**Drift. Not assessed — scope limitation.** No population stability index, no test-split or out-of-time data profile, and no scoring-period distribution artifact exists in the store. The artifact list contains `run.data_test` ([[art:a006dcd9:run.data_test]]) but no profile of it was supplied to the validator, so train-versus-test covariate comparison could not be performed and split-wise missingness could not be compared. No PSI finding is raised in either direction: drift is **unevaluated**, not absent, and the reader should not read section 6 as clearing it. This is a required remediation, not an observation.

## 4. Outcomes analysis

**Discrimination.** Test AUC is ⟦unverified: 0.7504688⟧ (Gini ⟦unverified: 0.5009377⟧, KS ⟦unverified: 0.4316704⟧) on ⟦unverified: 1,500⟧ rows; train AUC is ⟦unverified: 0.7607383⟧ (Gini ⟦unverified: 0.5214766⟧, KS ⟦unverified: 0.4489285⟧) on ⟦unverified: 3,500⟧ rows ([[art:c586d0a7:run.metrics]]). For a behavioural credit default model this is a normal and acceptable level of discrimination — neither strong enough to suggest leakage nor weak enough to question the feature set's relevance.

The out-of-sample gap is AUC ⟦unverified: 0.7607⟧ - ⟦unverified: 0.7505⟧ = **⟦unverified: 0.0102⟧**, KS ⟦unverified: 0.0173⟧, Gini ⟦unverified: 0.0205⟧. A gap of one AUC point between a ⟦unverified: 3,500⟧-row fit and a ⟦unverified: 1,500⟧-row test is within sampling noise for a ⟦unverified: 13⟧-parameter linear model; the approximate standard error of the test AUC alone at n=⟦unverified: 1,500⟧ with a ⟦unverified: 22.5%⟧ event rate is of order ⟦unverified: 0.013⟧, so the gap is not distinguishable from zero. **No out-of-sample degradation finding is raised.** The model generalises.

**Calibration.** On train, mean predicted ⟦unverified: 0.2245529⟧ against observed ⟦unverified: 0.2245714⟧ — a shortfall of ⟦unverified: 0.0000186⟧, essentially exact, as expected from a maximum-likelihood logistic fit with an intercept. On test, mean predicted ⟦unverified: 0.2214797⟧ against observed ⟦unverified: 0.2246667⟧ — a shortfall of ⟦unverified: 0.0031869⟧, or ⟦unverified: 1.42%⟧ in relative terms. This is a mild under-prediction of the aggregate default rate on held-out data. It is small: the standard error of the test event rate at n=⟦unverified: 1,500⟧ is about ⟦unverified: 0.0108⟧, so the deviation is roughly ⟦unverified: 0.3⟧ standard errors and is not statistically meaningful. It is recorded as an informational observation only, with the caveat below.

**The caveat is important.** Aggregate calibration — one number against one number — is the weakest calibration test available. No calibration-slope artifact, no decile or bin table, no reliability curve, and no Hosmer–Lemeshow-style partition exists in the store, even though the prediction tables that would support them do ([[art:c3cfe7db:run.predictions_test]], [[art:71768746:run.predictions_train]]). A model can match the overall mean exactly while being badly miscalibrated in the tails, and the tails are where a default model is used. **Calibration slope is untested.** The developer had the raw material to test it and did not.

**Loss.** Log loss is ⟦unverified: 0.4669720⟧ test against ⟦unverified: 0.4639850⟧ train; Brier is ⟦unverified: 0.1486259⟧ test against ⟦unverified: 0.1486067⟧ train. Both are consistent with the AUC picture — a small, unremarkable held-out penalty.

**Effective challenge. Not performed — scope limitation.** No challenger model, benchmark, or alternative specification exists in the artifact store. The validator therefore cannot state whether the champion's ⟦unverified: 0.7505⟧ test AUC is a good result or merely an adequate one. A penalised specification with the duplicate feature dropped, or a gradient-boosted benchmark, would be the obvious comparators; neither was run. No challenger finding is raised because none can be evidenced, but the absence of effective challenge is itself a gap against standard model risk management expectations and is carried into section 6 as a recommendation.

## 5. Sensitivity and scenario analysis

**No scenario artifacts exist.** The store contains no value curves, no stress grids, no partial dependence or marginal effect tables, and no univariate response profiles. Monotonicity of predicted risk in each driver — the standard scenario test for a credit model — **could not be tested**, and no scenario finding is raised. What follows is an analytical sensitivity computed by the validator from the fitted coefficients alone.

At the covariate mean, the standardised model predicts logit ⟦unverified: -1.3997⟧, i.e. a baseline default probability of **⟦unverified: 19.8%⟧**. Single-feature one-standard-deviation shocks, holding all else at the mean:

| Shock (+⟦unverified: 1⟧ sd) | Coefficient | Logit | P(default) | Direction |
|---|---|---|---|---|
| `delinq_last` | +⟦unverified: 0.7357⟧ | ⟦unverified: -0.6641⟧ | ⟦unverified: 34.0%⟧ | Sensible |
| `bill_mean_6m` | +⟦unverified: 0.6805⟧ | ⟦unverified: -0.7193⟧ | ⟦unverified: 32.8%⟧ | Sensible alone |
| `bill_last_adj` | ⟦unverified: -0.5619⟧ | ⟦unverified: -1.9616⟧ | ⟦unverified: 12.3%⟧ | **Wrong sign** |
| `bill_last` | ⟦unverified: -0.5348⟧ | ⟦unverified: -1.9345⟧ | ⟦unverified: 12.6%⟧ | **Wrong sign** |
| `pay_ratio_mean_6m` | ⟦unverified: -0.3621⟧ | ⟦unverified: -1.7618⟧ | ⟦unverified: 14.6%⟧ | Sensible |
| `utilisation` | +⟦unverified: 0.1640⟧ | ⟦unverified: -1.2357⟧ | ⟦unverified: 22.5%⟧ | Sensible |
| `utilisation_mean_6m` | +⟦unverified: 0.1425⟧ | ⟦unverified: -1.2573⟧ | ⟦unverified: 22.1%⟧ | Sensible |
| `delinq_count_6m` | +⟦unverified: 0.1219⟧ | ⟦unverified: -1.2778⟧ | ⟦unverified: 21.8%⟧ | Sensible |
| `limit_bal` | +⟦unverified: 0.1149⟧ | ⟦unverified: -1.2848⟧ | ⟦unverified: 21.7%⟧ | Questionable |
| `pay_ratio_last` | +⟦unverified: 0.1093⟧ | ⟦unverified: -1.2904⟧ | ⟦unverified: 21.6%⟧ | **Wrong sign** |
| `age` | ⟦unverified: -0.0672⟧ | ⟦unverified: -1.4669⟧ | ⟦unverified: 18.7%⟧ | Sensible |
| `delinq_max_6m` | ⟦unverified: -0.0322⟧ | ⟦unverified: -1.4320⟧ | ⟦unverified: 19.3%⟧ | **Wrong sign** |
| `bill_trend_6m` | ⟦unverified: -0.0240⟧ | ⟦unverified: -1.4237⟧ | ⟦unverified: 19.4%⟧ | Ambiguous |

The single most influential driver is recent delinquency, which alone moves predicted risk from ⟦unverified: 19.8%⟧ to ⟦unverified: 34.0%⟧ — a sensible and defensible concentration of signal for a default model.

**The billing block makes this table unusable feature-by-feature.** `bill_last` and `bill_last_adj` are the same variable, so the row for each is a fiction: they cannot move independently. Any realistic shock moves both together, contributing ⟦unverified: -1.0967⟧ in combination, and the *coherent* billing scenario (all three billing variables up one standard deviation together) gives ⟦unverified: 0.6805⟧ - ⟦unverified: 0.5348⟧ - ⟦unverified: 0.5619⟧ = ⟦unverified: -0.4162⟧, taking predicted risk from ⟦unverified: 19.8%⟧ to **⟦unverified: 14.0%⟧**. A model that lowers predicted default risk by ⟦unverified: 6⟧ percentage points when a client's outstanding balance rises by a standard deviation across every measurement of it is producing a wrong-signed response curve on its most economically important driver. The same applies to the payment block, where the coherent scenario (⟦unverified: -0.2528⟧, risk falling to ⟦unverified: 16.1%⟧) is correctly signed but where the `pay_ratio_last` row above is not.

The practical consequence: these sensitivities are artefacts of the collinear decomposition, not estimates of behaviour. Per-feature stress testing, reason-code generation, and any attribution of a score to its drivers are all invalid on the current specification. Fixing the collinearity is a prerequisite to meaningful scenario analysis, not a separate workstream.

## 6. Findings and recommendations

**M1 — high — Near-duplicate features `bill_last` and `bill_last_adj` produce severe multicollinearity.** The two variables are statistically indistinguishable in the training profile (standard deviations ⟦unverified: 44,429.8135⟧ and ⟦unverified: 44,429.8166⟧, agreeing to six significant figures; means ⟦unverified: 47,409.10⟧ and ⟦unverified: 47,412.85⟧). Their correlation is within rounding distance of 1.0, which drives the VIF for the pair into the thousands. The fit responds exactly as theory predicts: large opposed loadings (⟦unverified: -0.5348⟧ and ⟦unverified: -0.5619⟧) that are individually meaningless, contaminating the third member of the family (`bill_mean_6m` at +⟦unverified: 0.6805⟧) and producing a net billing response with the wrong economic sign. The sign reversals in the payment and delinquency families are the same effect at smaller scale. *Remediation: drop one of the pair — retain whichever has a documented definition — refit, and confirm that the billing block's net response turns positive and that `pay_ratio_last` recovers its expected negative sign. Expect discrimination to be essentially unchanged, since a duplicate carries no incremental information; if AUC falls materially on removal, that itself requires investigation.*

**T1 — medium — The declared VIF screen at threshold ⟦unverified: 10.0⟧ removed nothing and did not fire on a correlation of ~1.0.** The model summary declares `vif_threshold: 10.0` and reports `removed: []`. A pair of features with a correlation this close to unity cannot pass a VIF screen at any conventional threshold, so the screen was either not executed, executed on a different feature matrix than the one fitted, or its result was overridden without documentation. The developer's own declared control is therefore breached. *Remediation: re-run the screen, publish the full VIF vector and the condition number of the design matrix as artifacts, and record the disposition of every feature the screen flags. If a flagged feature is deliberately retained, the override and its justification must be documented.*

**D1 — low — Undocumented capping and distributional anomalies in the training data.** `pay_ratio_last` has an exact maximum of ⟦unverified: 2.0000⟧, a winsorisation cap that appears nowhere in the feature manifest; `utilisation_mean_6m` exceeds 1.0 (max ⟦unverified: 1.4310⟧); `bill_trend_6m` is severely left-skewed (min ⟦unverified: -67,201⟧ against max +⟦unverified: 27,398⟧ on a standard deviation of ⟦unverified: 3,119⟧); and zero missingness across all six-month aggregates is unusual enough to suggest an upstream join or imputation that is not documented. *Remediation: publish a variable dictionary recording every cap, floor, imputation rule and join condition, and confirm that caps applied in development are reproduced identically in the scoring pipeline — a cap applied in training but not in production is a silent source of score drift.*

**C1 — info — Mild aggregate under-prediction on the test split; calibration slope untested.** Mean predicted ⟦unverified: 0.2214797⟧ against an observed event rate of ⟦unverified: 0.2246667⟧, a relative shortfall of ⟦unverified: 1.42%⟧ and roughly ⟦unverified: 0.3⟧ standard errors — not material on its own. It is recorded because it is the *only* calibration evidence available: no slope, no reliability curve, and no decile table were produced, despite the prediction tables being present in the store. *Remediation: produce a decile calibration table and a calibration slope on the test split before any use that depends on the probability level rather than the rank.*

**Scope limitations carried forward (no finding raised, as none can be evidenced).** Drift/PSI was not assessed: no test-split profile or scoring-period distribution exists. Effective challenge was not performed: no challenger model exists. Scenario monotonicity was not tested: no value curves exist. Train/test contamination was inferred from distinct row hashes rather than demonstrated by a client-level overlap check. Each of these is a gap in the developer's evidence pack, and none should be read as a clean result.

**Overall recommendation.** Do not deploy the current coefficient vector for any use that depends on individual feature effects — reason codes, adverse action notices, driver attribution, or per-feature stress testing — because those effects are not identified. Ranking use (score-ordering for cutoff decisions) may proceed on an interim basis, since discrimination is stable out-of-sample and aggregate calibration holds. Full approval should follow a refit with the duplicate removed, an enforced and published VIF screen, a calibration slope, a drift baseline, and at least one challenger.

### F-001 · M1 collinearity · severity **high**

The training profile shows bill_last (mean 47,409.0966, sd 44,429.8135, min 513.48) and bill_last_adj (mean 47,412.8452, sd 44,429.8166, min 513.5673) to be statistically indistinguishable: their standard deviations agree to six significant figures and their means differ by 0.008%. The pairwise correlation is necessarily within rounding distance of 1.0, implying a VIF in the thousands. The fitted model shows the textbook consequences of this variance inflation. The pair receives large opposed loadings of -0.5348 and -0.5619 that are individually uninterpretable, and the contamination spreads to the third member of the billing family, bill_mean_6m, at +0.6805. The net effect is that a coherent one-standard-deviation rise across all three billing measures changes the log-odds by 0.6805 - 0.5348 - 0.5619 = -0.4162, i.e. the model predicts that clients with larger outstanding bills are less likely to default, taking baseline predicted risk from 19.8% down to 14.0%. That is the wrong economic sign on the model's most important balance driver. The same pathology appears in two other correlated families: pay_ratio_mean_6m loads -0.3621 (correct sign) while pay_ratio_last loads +0.1093 (wrong sign), and delinq_last (+0.7357) and delinq_count_6m (+0.1219) are opposed by delinq_max_6m (-0.0322). Three sign reversals concentrated inside three correlated families are not coincidence; they are the fingerprint of an unaddressed collinearity problem. The practical consequence is that the coefficient vector cannot support reason codes, adverse-action explanations, driver attribution, or per-feature sensitivity analysis. Discrimination is unaffected (test AUC 0.7505) because a duplicate carries no incremental information, so ranking use survives, but interpretation does not. Remediation is to drop whichever of the pair lacks a documented definition, refit, and confirm that the billing block's net response turns positive and pay_ratio_last recovers its expected negative sign.

### F-002 · T1 declared threshold · severity **medium**

The model summary declares a developer-set control, vif_threshold: 10.0, and reports its outcome as removed: [] — no feature was eliminated. This is impossible to reconcile with the data. bill_last and bill_last_adj have standard deviations of 44,429.8135 and 44,429.8166 in the training profile, agreeing to six significant figures, and means differing by 0.008%; their correlation is within rounding distance of unity and their variance inflation factors run into the thousands. No screen at any conventional threshold, let alone 10.0, would pass such a pair. The declared control was therefore either not executed, executed against a different feature matrix than the one actually fitted, or its result was overridden without documentation. Either way the developer's own stated threshold is breached, and the breach is the direct cause of the multicollinearity finding recorded separately. The control's failure is compounded by a documentation gap: nothing in the artifact store defines what the _adj suffix on bill_last_adj adjusts for, which is precisely the documentation that would have prompted a reviewer to question the pair. Remediation requires re-running the screen against the fitted design matrix, publishing the full VIF vector and the matrix condition number as first-class artifacts, and recording an explicit disposition for every feature the screen flags. Where a flagged feature is deliberately retained, the override and its justification must be documented rather than silently absorbed into an empty removal list.

### F-003 · D1 data integrity · severity **low**

Several integrity anomalies are visible in the training profile and none is declared in the feature manifest or model summary. First, pay_ratio_last has an exact maximum of 2.0000 to full precision while its six-month counterpart pay_ratio_mean_6m peaks at 1.6385; a maximum landing on a round 2.0 is a winsorisation cap, not a natural bound, and a capped variable that has then been standardised carries a distorted upper tail into the fit. Second, utilisation reaches 1.1297 and utilisation_mean_6m reaches 1.4310; over-limit balances are legitimate in credit data, but a six-month mean exceeding the last-month maximum implies sustained over-limit behaviour that should be confirmed rather than assumed. Third, bill_trend_6m is severely left-skewed, with mean -237.59 and standard deviation 3,118.55 against a minimum of -67,201 (about 21 standard deviations) and a maximum of +27,398 (about 9); standardisation does not correct skew of this order, and the feature's near-zero coefficient of -0.0240 is consistent with the tail dominating the scale and flattening the informative central range. Fourth, missingness is reported as exactly zero for all fifteen columns including every six-month aggregate, which is unusual for a behavioural panel where short-tenure clients normally lack full history; this suggests an upstream inner join that dropped those clients, or imputation performed before profiling, either of which is a selection effect invisible in these artifacts. The severity is low because none of these individually undermines the fitted model, but collectively they indicate an undocumented preprocessing layer. Remediation is a published variable dictionary recording every cap, floor, imputation rule and join condition, plus confirmation that caps applied in development are reproduced identically in production scoring — a cap present in training but absent at scoring time is a silent source of score drift.

### F-004 · C1 calibration · severity **info**

On the test split the mean predicted probability is 0.2214797 against an observed event rate of 0.2246667, an absolute shortfall of 0.0031869 and a relative under-prediction of 1.42%. At n=1,500 with a 22.5% base rate the standard error of the observed rate is about 0.0108, so the deviation is roughly 0.3 standard errors and is not statistically or practically material. Training calibration is essentially exact (0.2245529 predicted against 0.2245714 observed), as expected of a maximum-likelihood logistic fit with an intercept, and Brier scores are effectively identical across splits at 0.1486067 and 0.1486259. No remediation is attached to the deviation itself. The observation is recorded because it is the only calibration evidence in the entire artifact store. Matching one aggregate number to another is the weakest available calibration test: a model can reproduce the overall mean exactly while being badly miscalibrated in the upper and lower deciles, and the deciles are where a default model actually drives cutoff and pricing decisions. No calibration slope, reliability curve, decile table, or binned partition was produced, even though the per-row prediction tables for both splits exist in the store and would have supported all of them directly. The calibration slope is therefore untested rather than acceptable. Before any use that depends on the probability level rather than the rank ordering, a decile calibration table and a fitted calibration slope should be produced on the test split.

Candidates raised and not promoted: none.

### Open items

No open item was recorded for this validation.

## 7. Ongoing monitoring recommendations

1. **Discrimination.** Track AUC, Gini and KS monthly on scored-and-matured cohorts. Set an amber trigger at a ⟦unverified: 0.03⟧ absolute AUC drop from the ⟦unverified: 0.7505⟧ test baseline and a red trigger at ⟦unverified: 0.05⟧. Report on a rolling three-month window to damp small-cohort noise.
2. **Calibration.** Track the ratio of mean predicted to observed default rate, overall and by score decile. The development baseline is ⟦unverified: 0.9858⟧ on test. Amber at a ±⟦unverified: 10%⟧ deviation of the overall ratio, red at ±⟦unverified: 20%⟧ or at any two adjacent deciles breaching ±⟦unverified: 25%⟧. The by-decile view is the part that matters and is the part development skipped.
3. **Population stability.** Establish a PSI baseline against the training distribution for all ⟦unverified: 13⟧ features at the next scoring run — this does not exist today and is the first monitoring gap to close. Standard thresholds: PSI < ⟦unverified: 0.10⟧ stable, ⟦unverified: 0.10⟧–⟦unverified: 0.25⟧ investigate, > ⟦unverified: 0.25⟧ escalate. Monitor score PSI on the same schedule.
4. **Coefficient and collinearity surveillance.** At every refit, publish the full VIF vector and design-matrix condition number, and diff the coefficient signs against the prior version. Any feature whose sign flips between refits, or whose VIF exceeds the declared threshold of ⟦unverified: 10.0⟧, must be dispositioned explicitly rather than silently retained — the failure mode this model already exhibits.
5. **Data integrity gates.** Run automated pre-scoring checks for missingness by feature (development baseline: zero), for cap saturation on `pay_ratio_last` at its ⟦unverified: 2.0⟧ ceiling, for `utilisation` values above 1.0, and for any newly-introduced feature pair with a pairwise correlation above ⟦unverified: 0.95⟧. The last check would have caught the defect in this package before the fit.
6. **Effective challenge.** Stand up at least one challenger — minimally a refit with the duplicate dropped, preferably also a regularised or tree-based benchmark — and re-run the comparison annually. Escalate if a challenger exceeds the champion's test AUC by more than ⟦unverified: 0.02⟧.
7. **Review cadence.** Full revalidation annually, or on trigger: any red threshold above, a change in the underwriting or collections policy that alters the meaning of the delinquency and payment features, or a material shift in the portfolio's ⟦unverified: 22.5%⟧ base default rate.

## Appendix A — Claims

Grounding precision 0.0000 before repair (0 of 200 claims verified; 177 unsupported, 23 dangling) and 0.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 0/20; conceptual_soundness 0/28; data_integrity 0/30; outcomes 0/34; sensitivity 0/54; findings 0/17; monitoring 0/17.

Developer claims: `plain_llm` runs no check over `package.yaml`'s declared claims See Appendix D.

Excluded numeric tokens (not claims): section_number (section 6, 1., 2., 3.); label_number (round 2); inline_code (`missing: 0.0`, `3e28943d...`, `vif_threshold: 10.0`); citation_hash (f2e0e9a7, 3b6b0a38, c586d0a7, f79bb8bb); package_version (1.0); extractor_returned_excluded_token (1.0, 6,, 0.0, 1).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | This report is a validation of package `credit_default` vers… | 13 | count | n_features |  | eq | `[[art:f2e0e9a7:run.model_summary]]` | dangling |  |
| 2 | summary | This report is a validation of package `credit_default` vers… | -1.3997 | ratio | coefficient |  | eq | `[[art:f2e0e9a7:run.model_summary]]` | dangling |  |
| 3 | summary | This report is a validation of package `credit_default` vers… | 3500 | count | n_rows | train | eq | `[[art:3b6b0a38:run.splits]]` | dangling |  |
| 4 | summary | This report is a validation of package `credit_default` vers… | 1500 | count | n_rows | test | eq | `[[art:3b6b0a38:run.splits]]` | dangling |  |
| 5 | summary | The validation covers conceptual soundness, data integrity,… | 3 | ratio |  |  | eq |  | unsupported |  |
| 6 | summary | The validation covers conceptual soundness, data integrity,… | 5 | ratio |  |  | eq |  | unsupported |  |
| 7 | summary | Headline results. Discrimination is adequate and stable: tes… | 0.7505 | ratio | auc | test | eq | `[[art:c586d0a7:run.metrics]]` | dangling |  |
| 8 | summary | Headline results. Discrimination is adequate and stable: tes… | 0.5009 | ratio | gini | test | eq | `[[art:c586d0a7:run.metrics]]` | dangling |  |
| 9 | summary | Headline results. Discrimination is adequate and stable: tes… | 0.4317 | ratio | ks | test | eq | `[[art:c586d0a7:run.metrics]]` | dangling |  |
| 10 | summary | Headline results. Discrimination is adequate and stable: tes… | 0.7607 | ratio | auc | train | eq | `[[art:c586d0a7:run.metrics]]` | dangling |  |
| 11 | summary | Headline results. Discrimination is adequate and stable: tes… | 0.5215 | ratio | gini | train | eq | `[[art:c586d0a7:run.metrics]]` | dangling |  |
| 12 | summary | Headline results. Discrimination is adequate and stable: tes… | 0.4489 | ratio | ks | train | eq | `[[art:c586d0a7:run.metrics]]` | dangling |  |
| 13 | summary | Headline results. Discrimination is adequate and stable: tes… | 0.0102 | ratio | delta_auc |  | delta |  | unsupported |  |
| 14 | summary | Headline results. Discrimination is adequate and stable: tes… | 0.22455 | ratio | mean_predicted_probability | train | eq |  | unsupported |  |
| 15 | summary | Headline results. Discrimination is adequate and stable: tes… | 0.22457 | ratio | event_rate | train | eq |  | unsupported |  |
| 16 | summary | Headline results. Discrimination is adequate and stable: tes… | 0.22148 | ratio | mean_predicted_probability | test | eq |  | unsupported |  |
| 17 | summary | Headline results. Discrimination is adequate and stable: tes… | 0.22467 | ratio | event_rate | test | eq |  | unsupported |  |
| 18 | summary | Headline results. Discrimination is adequate and stable: tes… | 0.14861 | ratio | brier | train | eq |  | unsupported |  |
| 19 | summary | Headline results. Discrimination is adequate and stable: tes… | 0.14863 | ratio | brier | test | eq |  | unsupported |  |
| 20 | summary | The material problem is not performance but structure. The f… | 10 | ratio | vif |  | eq |  | unsupported |  |
| 21 | conceptual_soundness | The model form — a standardised logistic regression on 13 co… | 13 | count | features |  | eq |  | unsupported |  |
| 22 | conceptual_soundness | **Feature timing.** The feature manifest () declares 2 featu… | 2 | count | features |  | eq | `[[art:f79bb8bb:run.features]]` | dangling |  |
| 23 | conceptual_soundness | **Feature timing.** The feature manifest () declares 2 featu… | 11 | count | features |  | eq | `[[art:f79bb8bb:run.features]]` | dangling |  |
| 24 | conceptual_soundness | **Feature timing.** The feature manifest () declares 2 featu… | 0 | count | features |  | eq | `[[art:f79bb8bb:run.features]]` | dangling |  |
| 25 | conceptual_soundness | **Feature timing.** The feature manifest () declares 2 featu… | 0 | count | features |  | eq | `[[art:f79bb8bb:run.features]]` | dangling |  |
| 26 | conceptual_soundness | **Feature timing.** The feature manifest () declares 2 featu… | 13 | count | features |  | eq |  | unsupported |  |
| 27 | conceptual_soundness | **Feature timing.** The feature manifest () declares 2 featu… | 13 | count | coefficient |  | eq |  | unsupported |  |
| 28 | conceptual_soundness | **Feature timing.** The feature manifest () declares 2 featu… | 0.9 | ratio | auc |  | eq |  | unsupported |  |
| 29 | conceptual_soundness | **Feature timing.** The feature manifest () declares 2 featu… | 0.7505 | ratio | auc |  | eq |  | unsupported |  |
| 30 | conceptual_soundness | **Feature timing.** The feature manifest () declares 2 featu… | 0.9 | ratio | auc |  | eq |  | unsupported |  |
| 31 | conceptual_soundness | - *Billing level.* `bill_mean_6m` loads +0.6805 while `bill_… | 0.6805 | ratio | coefficient |  | eq |  | unsupported |  |
| 32 | conceptual_soundness | - *Billing level.* `bill_mean_6m` loads +0.6805 while `bill_… | -0.5348 | ratio | coefficient |  | eq |  | unsupported |  |
| 33 | conceptual_soundness | - *Billing level.* `bill_mean_6m` loads +0.6805 while `bill_… | -0.5619 | ratio | coefficient |  | eq |  | unsupported |  |
| 34 | conceptual_soundness | - *Billing level.* `bill_mean_6m` loads +0.6805 while `bill_… | 0.6805 | ratio | coefficient |  | eq |  | unsupported |  |
| 35 | conceptual_soundness | - *Billing level.* `bill_mean_6m` loads +0.6805 while `bill_… | 0.5348 | ratio | coefficient |  | eq |  | unsupported |  |
| 36 | conceptual_soundness | - *Billing level.* `bill_mean_6m` loads +0.6805 while `bill_… | 0.5619 | ratio | coefficient |  | eq |  | unsupported |  |
| 37 | conceptual_soundness | - *Billing level.* `bill_mean_6m` loads +0.6805 while `bill_… | -0.416 | ratio | coefficient |  | eq |  | unsupported |  |
| 38 | conceptual_soundness | - *Payment behaviour.* `pay_ratio_mean_6m` loads -0.3621 (co… | -0.3621 | ratio | coefficient |  | eq |  | unsupported |  |
| 39 | conceptual_soundness | - *Payment behaviour.* `pay_ratio_mean_6m` loads -0.3621 (co… | 0.1093 | ratio | coefficient |  | eq |  | unsupported |  |
| 40 | conceptual_soundness | - *Payment behaviour.* `pay_ratio_mean_6m` loads -0.3621 (co… | -0.2528 | ratio | coefficient |  | eq |  | unsupported |  |
| 41 | conceptual_soundness | - *Delinquency.* `delinq_last` (+0.7357) and `delinq_count_6… | 0.7357 | ratio | coefficient |  | eq |  | unsupported |  |
| 42 | conceptual_soundness | - *Delinquency.* `delinq_last` (+0.7357) and `delinq_count_6… | 0.1219 | ratio | coefficient |  | eq |  | unsupported |  |
| 43 | conceptual_soundness | - *Delinquency.* `delinq_last` (+0.7357) and `delinq_count_6… | -0.0322 | ratio | coefficient |  | eq |  | unsupported |  |
| 44 | conceptual_soundness | - *Delinquency.* `delinq_last` (+0.7357) and `delinq_count_6… | 0.8253 | ratio | coefficient |  | eq |  | unsupported |  |
| 45 | conceptual_soundness | `limit_bal` at +0.1149 is also worth flagging: a larger cred… | 0.1149 | ratio | coefficient |  | eq |  | unsupported |  |
| 46 | conceptual_soundness | `limit_bal` at +0.1149 is also worth flagging: a larger cred… | -0.0672 | ratio | coefficient |  | eq |  | unsupported |  |
| 47 | conceptual_soundness | `limit_bal` at +0.1149 is also worth flagging: a larger cred… | 0.164 | ratio | coefficient |  | eq |  | unsupported |  |
| 48 | conceptual_soundness | **Documentation.** The model summary records `class_weight:… | 22.5 | percent | event_rate |  | eq |  | unsupported |  |
| 49 | data_integrity | **Completeness.** The training profile shows `missing: 0.0`… | 15 | count | columns | train | eq | `[[art:c522fc63:run.data_train]]` | dangling |  |
| 50 | data_integrity | **Split integrity.** Train and test carry distinct row hashe… | 5000 | count | row_count |  | eq |  | unsupported |  |
| 51 | data_integrity | **Split integrity.** Train and test carry distinct row hashe… | 1 | count | client_id_min | train | eq |  | unsupported |  |
| 52 | data_integrity | **Split integrity.** Train and test carry distinct row hashe… | 5000 | count | client_id_max | train | eq |  | unsupported |  |
| 53 | data_integrity | **Split integrity.** Train and test carry distinct row hashe… | 0.224571 | ratio | event_rate | train | eq |  | unsupported |  |
| 54 | data_integrity | **Split integrity.** Train and test carry distinct row hashe… | 0.224667 | ratio | event_rate | test | eq |  | unsupported |  |
| 55 | data_integrity | 1. *The near-duplicate pair.* `bill_last` has mean 47,409.09… | 47409.0966 | currency | mean | train | eq |  | unsupported |  |
| 56 | data_integrity | 1. *The near-duplicate pair.* `bill_last` has mean 47,409.09… | 44429.8135 | currency | std | train | eq |  | unsupported |  |
| 57 | data_integrity | 1. *The near-duplicate pair.* `bill_last` has mean 47,409.09… | 47412.8452 | currency | mean | train | eq |  | unsupported |  |
| 58 | data_integrity | 1. *The near-duplicate pair.* `bill_last` has mean 47,409.09… | 44429.8166 | currency | std | train | eq |  | unsupported |  |
| 59 | data_integrity | 1. *The near-duplicate pair.* `bill_last` has mean 47,409.09… | 3.75 | currency | mean | train | delta |  | unsupported |  |
| 60 | data_integrity | 1. *The near-duplicate pair.* `bill_last` has mean 47,409.09… | 47000 | currency | mean | train | eq |  | unsupported |  |
| 61 | data_integrity | 1. *The near-duplicate pair.* `bill_last` has mean 47,409.09… | 0.008 | percent | mean | train | eq |  | unsupported |  |
| 62 | data_integrity | 1. *The near-duplicate pair.* `bill_last` has mean 47,409.09… | 513.48 | currency | min | train | eq |  | unsupported |  |
| 63 | data_integrity | 1. *The near-duplicate pair.* `bill_last` has mean 47,409.09… | 513.5673 | currency | min | train | eq |  | unsupported |  |
| 64 | data_integrity | 1. *The near-duplicate pair.* `bill_last` has mean 47,409.09… | 536181.78 | currency | max | train | eq |  | unsupported |  |
| 65 | data_integrity | 1. *The near-duplicate pair.* `bill_last` has mean 47,409.09… | 535345.13 | currency | max | train | eq |  | unsupported |  |
| 66 | data_integrity | 2. *Capping.* `pay_ratio_last` has an exact maximum of 2.000… | 2 | ratio | max | train | eq |  | unsupported |  |
| 67 | data_integrity | 2. *Capping.* `pay_ratio_last` has an exact maximum of 2.000… | 1.6385 | ratio | max | train | eq |  | unsupported |  |
| 68 | data_integrity | 3. *Out-of-range utilisation.* `utilisation` reaches 1.1297… | 1.1297 | ratio | max | train | eq |  | unsupported |  |
| 69 | data_integrity | 3. *Out-of-range utilisation.* `utilisation` reaches 1.1297… | 1.431 | ratio | max | train | eq |  | unsupported |  |
| 70 | data_integrity | 4. *Skew.* `bill_trend_6m` has mean -237.6 with standard dev… | -237.6 | currency | mean | train | eq |  | unsupported |  |
| 71 | data_integrity | 4. *Skew.* `bill_trend_6m` has mean -237.6 with standard dev… | 3118.5 | currency | std | train | eq |  | unsupported |  |
| 72 | data_integrity | 4. *Skew.* `bill_trend_6m` has mean -237.6 with standard dev… | -67201 | currency | min | train | eq |  | unsupported |  |
| 73 | data_integrity | 4. *Skew.* `bill_trend_6m` has mean -237.6 with standard dev… | 27398 | currency | max | train | eq |  | unsupported |  |
| 74 | data_integrity | 4. *Skew.* `bill_trend_6m` has mean -237.6 with standard dev… | 21 | ratio | std | train | eq |  | unsupported |  |
| 75 | data_integrity | 4. *Skew.* `bill_trend_6m` has mean -237.6 with standard dev… | 9 | ratio | std | train | eq |  | unsupported |  |
| 76 | data_integrity | 4. *Skew.* `bill_trend_6m` has mean -237.6 with standard dev… | -0.024 | ratio | coefficient |  | eq |  | unsupported |  |
| 77 | data_integrity | 5. *Identifier hygiene.* `client_id` is present in the profi… | 2513.9 | ratio | mean | train | eq |  | unsupported |  |
| 78 | data_integrity | 5. *Identifier hygiene.* `client_id` is present in the profi… | 13 | count | coefficient |  | eq |  | unsupported |  |
| 79 | outcomes | **Discrimination.** Test AUC is 0.7504688 (Gini 0.5009377, K… | 0.7504688 | ratio | auc | test | eq | `[[art:c586d0a7:run.metrics]]` | dangling |  |
| 80 | outcomes | **Discrimination.** Test AUC is 0.7504688 (Gini 0.5009377, K… | 0.5009377 | ratio | gini | test | eq | `[[art:c586d0a7:run.metrics]]` | dangling |  |
| 81 | outcomes | **Discrimination.** Test AUC is 0.7504688 (Gini 0.5009377, K… | 0.4316704 | ratio | ks | test | eq | `[[art:c586d0a7:run.metrics]]` | dangling |  |
| 82 | outcomes | **Discrimination.** Test AUC is 0.7504688 (Gini 0.5009377, K… | 1500 | count | n_rows | test | eq | `[[art:c586d0a7:run.metrics]]` | dangling |  |
| 83 | outcomes | **Discrimination.** Test AUC is 0.7504688 (Gini 0.5009377, K… | 0.7607383 | ratio | auc | train | eq | `[[art:c586d0a7:run.metrics]]` | dangling |  |
| 84 | outcomes | **Discrimination.** Test AUC is 0.7504688 (Gini 0.5009377, K… | 0.5214766 | ratio | gini | train | eq | `[[art:c586d0a7:run.metrics]]` | dangling |  |
| 85 | outcomes | **Discrimination.** Test AUC is 0.7504688 (Gini 0.5009377, K… | 0.4489285 | ratio | ks | train | eq | `[[art:c586d0a7:run.metrics]]` | dangling |  |
| 86 | outcomes | **Discrimination.** Test AUC is 0.7504688 (Gini 0.5009377, K… | 3500 | count | n_rows | train | eq | `[[art:c586d0a7:run.metrics]]` | dangling |  |
| 87 | outcomes | The out-of-sample gap is AUC 0.7607 - 0.7505 = **0.0102**, K… | 0.7607 | ratio | auc | train | eq |  | unsupported |  |
| 88 | outcomes | The out-of-sample gap is AUC 0.7607 - 0.7505 = **0.0102**, K… | 0.7505 | ratio | auc | test | eq |  | unsupported |  |
| 89 | outcomes | The out-of-sample gap is AUC 0.7607 - 0.7505 = **0.0102**, K… | 0.0102 | ratio | delta_auc |  | delta |  | unsupported |  |
| 90 | outcomes | The out-of-sample gap is AUC 0.7607 - 0.7505 = **0.0102**, K… | 0.0173 | ratio | delta_ks |  | delta |  | unsupported |  |
| 91 | outcomes | The out-of-sample gap is AUC 0.7607 - 0.7505 = **0.0102**, K… | 0.0205 | ratio | delta_gini |  | delta |  | unsupported |  |
| 92 | outcomes | The out-of-sample gap is AUC 0.7607 - 0.7505 = **0.0102**, K… | 3500 | count | n_rows | train | eq |  | unsupported |  |
| 93 | outcomes | The out-of-sample gap is AUC 0.7607 - 0.7505 = **0.0102**, K… | 1500 | count | n_rows | test | eq |  | unsupported |  |
| 94 | outcomes | The out-of-sample gap is AUC 0.7607 - 0.7505 = **0.0102**, K… | 13 | count | n_features |  | eq |  | unsupported |  |
| 95 | outcomes | The out-of-sample gap is AUC 0.7607 - 0.7505 = **0.0102**, K… | 1500 | count | n_rows | test | eq |  | unsupported |  |
| 96 | outcomes | The out-of-sample gap is AUC 0.7607 - 0.7505 = **0.0102**, K… | 22.5 | percent | event_rate | test | eq |  | unsupported |  |
| 97 | outcomes | The out-of-sample gap is AUC 0.7607 - 0.7505 = **0.0102**, K… | 0.013 | ratio | auc_standard_error | test | eq |  | unsupported |  |
| 98 | outcomes | **Calibration.** On train, mean predicted 0.2245529 against… | 0.2245529 | ratio | mean_predicted | train | eq |  | unsupported |  |
| 99 | outcomes | **Calibration.** On train, mean predicted 0.2245529 against… | 0.2245714 | ratio | event_rate | train | eq |  | unsupported |  |
| 100 | outcomes | **Calibration.** On train, mean predicted 0.2245529 against… | 1.86e-05 | ratio | calibration_shortfall | train | delta |  | unsupported |  |
| 101 | outcomes | **Calibration.** On train, mean predicted 0.2245529 against… | 0.2214797 | ratio | mean_predicted | test | eq |  | unsupported |  |
| 102 | outcomes | **Calibration.** On train, mean predicted 0.2245529 against… | 0.2246667 | ratio | event_rate | test | eq |  | unsupported |  |
| 103 | outcomes | **Calibration.** On train, mean predicted 0.2245529 against… | 0.0031869 | ratio | calibration_shortfall | test | delta |  | unsupported |  |
| 104 | outcomes | **Calibration.** On train, mean predicted 0.2245529 against… | 1.42 | percent | calibration_shortfall_relative | test | ratio |  | unsupported |  |
| 105 | outcomes | **Calibration.** On train, mean predicted 0.2245529 against… | 1500 | count | n_rows | test | eq |  | unsupported |  |
| 106 | outcomes | **Calibration.** On train, mean predicted 0.2245529 against… | 0.0108 | ratio | event_rate_standard_error | test | eq |  | unsupported |  |
| 107 | outcomes | **Calibration.** On train, mean predicted 0.2245529 against… | 0.3 | ratio | calibration_shortfall_standard_errors | test | eq |  | unsupported |  |
| 108 | outcomes | **Loss.** Log loss is 0.4669720 test against 0.4639850 train… | 0.466972 | ratio | log_loss | test | eq |  | unsupported |  |
| 109 | outcomes | **Loss.** Log loss is 0.4669720 test against 0.4639850 train… | 0.463985 | ratio | log_loss | train | eq |  | unsupported |  |
| 110 | outcomes | **Loss.** Log loss is 0.4669720 test against 0.4639850 train… | 0.1486259 | ratio | brier | test | eq |  | unsupported |  |
| 111 | outcomes | **Loss.** Log loss is 0.4669720 test against 0.4639850 train… | 0.1486067 | ratio | brier | train | eq |  | unsupported |  |
| 112 | outcomes | **Effective challenge. Not performed — scope limitation.** N… | 0.7505 | ratio | auc | test | eq |  | unsupported |  |
| 113 | sensitivity | At the covariate mean, the standardised model predicts logit… | -1.3997 | ratio | logit |  | eq |  | unsupported |  |
| 114 | sensitivity | At the covariate mean, the standardised model predicts logit… | 19.8 | percent | predicted_probability |  | eq |  | unsupported |  |
| 115 | sensitivity | \| Shock (+1 sd) \| Coefficient \| Logit \| P(default) \| Directi… | 1 | ratio |  |  | eq |  | unsupported |  |
| 116 | sensitivity | \| `delinq_last` \| +0.7357 \| -0.6641 \| 34.0% \| Sensible \| | 0.7357 | ratio | coefficient |  | eq |  | unsupported |  |
| 117 | sensitivity | \| `delinq_last` \| +0.7357 \| -0.6641 \| 34.0% \| Sensible \| | -0.6641 | ratio | logit |  | eq |  | unsupported |  |
| 118 | sensitivity | \| `delinq_last` \| +0.7357 \| -0.6641 \| 34.0% \| Sensible \| | 34 | percent | predicted_probability |  | eq |  | unsupported |  |
| 119 | sensitivity | \| `bill_mean_6m` \| +0.6805 \| -0.7193 \| 32.8% \| Sensible alon… | 0.6805 | ratio | coefficient |  | eq |  | unsupported |  |
| 120 | sensitivity | \| `bill_mean_6m` \| +0.6805 \| -0.7193 \| 32.8% \| Sensible alon… | -0.7193 | ratio | logit |  | eq |  | unsupported |  |
| 121 | sensitivity | \| `bill_mean_6m` \| +0.6805 \| -0.7193 \| 32.8% \| Sensible alon… | 32.8 | percent | predicted_probability |  | eq |  | unsupported |  |
| 122 | sensitivity | \| `bill_last_adj` \| -0.5619 \| -1.9616 \| 12.3% \| **Wrong sign… | -0.5619 | ratio | coefficient |  | eq |  | unsupported |  |
| 123 | sensitivity | \| `bill_last_adj` \| -0.5619 \| -1.9616 \| 12.3% \| **Wrong sign… | -1.9616 | ratio | logit |  | eq |  | unsupported |  |
| 124 | sensitivity | \| `bill_last_adj` \| -0.5619 \| -1.9616 \| 12.3% \| **Wrong sign… | 12.3 | percent | predicted_probability |  | eq |  | unsupported |  |
| 125 | sensitivity | \| `bill_last` \| -0.5348 \| -1.9345 \| 12.6% \| **Wrong sign** \| | -0.5348 | ratio | coefficient |  | eq |  | unsupported |  |
| 126 | sensitivity | \| `bill_last` \| -0.5348 \| -1.9345 \| 12.6% \| **Wrong sign** \| | -1.9345 | ratio | logit |  | eq |  | unsupported |  |
| 127 | sensitivity | \| `bill_last` \| -0.5348 \| -1.9345 \| 12.6% \| **Wrong sign** \| | 12.6 | percent | predicted_probability |  | eq |  | unsupported |  |
| 128 | sensitivity | \| `pay_ratio_mean_6m` \| -0.3621 \| -1.7618 \| 14.6% \| Sensible… | -0.3621 | ratio | coefficient |  | eq |  | unsupported |  |
| 129 | sensitivity | \| `pay_ratio_mean_6m` \| -0.3621 \| -1.7618 \| 14.6% \| Sensible… | -1.7618 | ratio | logit |  | eq |  | unsupported |  |
| 130 | sensitivity | \| `pay_ratio_mean_6m` \| -0.3621 \| -1.7618 \| 14.6% \| Sensible… | 14.6 | percent | predicted_probability |  | eq |  | unsupported |  |
| 131 | sensitivity | \| `utilisation` \| +0.1640 \| -1.2357 \| 22.5% \| Sensible \| | 0.164 | ratio | coefficient |  | eq |  | unsupported |  |
| 132 | sensitivity | \| `utilisation` \| +0.1640 \| -1.2357 \| 22.5% \| Sensible \| | -1.2357 | ratio | logit |  | eq |  | unsupported |  |
| 133 | sensitivity | \| `utilisation` \| +0.1640 \| -1.2357 \| 22.5% \| Sensible \| | 22.5 | percent | predicted_probability |  | eq |  | unsupported |  |
| 134 | sensitivity | \| `utilisation_mean_6m` \| +0.1425 \| -1.2573 \| 22.1% \| Sensib… | 0.1425 | ratio | coefficient |  | eq |  | unsupported |  |
| 135 | sensitivity | \| `utilisation_mean_6m` \| +0.1425 \| -1.2573 \| 22.1% \| Sensib… | -1.2573 | ratio | logit |  | eq |  | unsupported |  |
| 136 | sensitivity | \| `utilisation_mean_6m` \| +0.1425 \| -1.2573 \| 22.1% \| Sensib… | 22.1 | percent | predicted_probability |  | eq |  | unsupported |  |
| 137 | sensitivity | \| `delinq_count_6m` \| +0.1219 \| -1.2778 \| 21.8% \| Sensible \| | 0.1219 | ratio | coefficient |  | eq |  | unsupported |  |
| 138 | sensitivity | \| `delinq_count_6m` \| +0.1219 \| -1.2778 \| 21.8% \| Sensible \| | -1.2778 | ratio | logit |  | eq |  | unsupported |  |
| 139 | sensitivity | \| `delinq_count_6m` \| +0.1219 \| -1.2778 \| 21.8% \| Sensible \| | 21.8 | percent | predicted_probability |  | eq |  | unsupported |  |
| 140 | sensitivity | \| `limit_bal` \| +0.1149 \| -1.2848 \| 21.7% \| Questionable \| | 0.1149 | ratio | coefficient |  | eq |  | unsupported |  |
| 141 | sensitivity | \| `limit_bal` \| +0.1149 \| -1.2848 \| 21.7% \| Questionable \| | -1.2848 | ratio | logit |  | eq |  | unsupported |  |
| 142 | sensitivity | \| `limit_bal` \| +0.1149 \| -1.2848 \| 21.7% \| Questionable \| | 21.7 | percent | predicted_probability |  | eq |  | unsupported |  |
| 143 | sensitivity | \| `pay_ratio_last` \| +0.1093 \| -1.2904 \| 21.6% \| **Wrong sig… | 0.1093 | ratio | coefficient |  | eq |  | unsupported |  |
| 144 | sensitivity | \| `pay_ratio_last` \| +0.1093 \| -1.2904 \| 21.6% \| **Wrong sig… | -1.2904 | ratio | logit |  | eq |  | unsupported |  |
| 145 | sensitivity | \| `pay_ratio_last` \| +0.1093 \| -1.2904 \| 21.6% \| **Wrong sig… | 21.6 | percent | predicted_probability |  | eq |  | unsupported |  |
| 146 | sensitivity | \| `age` \| -0.0672 \| -1.4669 \| 18.7% \| Sensible \| | -0.0672 | ratio | coefficient |  | eq |  | unsupported |  |
| 147 | sensitivity | \| `age` \| -0.0672 \| -1.4669 \| 18.7% \| Sensible \| | -1.4669 | ratio | logit |  | eq |  | unsupported |  |
| 148 | sensitivity | \| `age` \| -0.0672 \| -1.4669 \| 18.7% \| Sensible \| | 18.7 | percent | predicted_probability |  | eq |  | unsupported |  |
| 149 | sensitivity | \| `delinq_max_6m` \| -0.0322 \| -1.4320 \| 19.3% \| **Wrong sign… | -0.0322 | ratio | coefficient |  | eq |  | unsupported |  |
| 150 | sensitivity | \| `delinq_max_6m` \| -0.0322 \| -1.4320 \| 19.3% \| **Wrong sign… | -1.432 | ratio | logit |  | eq |  | unsupported |  |
| 151 | sensitivity | \| `delinq_max_6m` \| -0.0322 \| -1.4320 \| 19.3% \| **Wrong sign… | 19.3 | percent | predicted_probability |  | eq |  | unsupported |  |
| 152 | sensitivity | \| `bill_trend_6m` \| -0.0240 \| -1.4237 \| 19.4% \| Ambiguous \| | -0.024 | ratio | coefficient |  | eq |  | unsupported |  |
| 153 | sensitivity | \| `bill_trend_6m` \| -0.0240 \| -1.4237 \| 19.4% \| Ambiguous \| | -1.4237 | ratio | logit |  | eq |  | unsupported |  |
| 154 | sensitivity | \| `bill_trend_6m` \| -0.0240 \| -1.4237 \| 19.4% \| Ambiguous \| | 19.4 | percent | predicted_probability |  | eq |  | unsupported |  |
| 155 | sensitivity | The single most influential driver is recent delinquency, wh… | 19.8 | percent | predicted_probability |  | eq |  | unsupported |  |
| 156 | sensitivity | The single most influential driver is recent delinquency, wh… | 34 | percent | predicted_probability |  | eq |  | unsupported |  |
| 157 | sensitivity | **The billing block makes this table unusable feature-by-fea… | -1.0967 | ratio | coefficient |  | eq |  | unsupported |  |
| 158 | sensitivity | **The billing block makes this table unusable feature-by-fea… | 0.6805 | ratio | coefficient |  | eq |  | unsupported |  |
| 159 | sensitivity | **The billing block makes this table unusable feature-by-fea… | 0.5348 | ratio | coefficient |  | eq |  | unsupported |  |
| 160 | sensitivity | **The billing block makes this table unusable feature-by-fea… | 0.5619 | ratio | coefficient |  | eq |  | unsupported |  |
| 161 | sensitivity | **The billing block makes this table unusable feature-by-fea… | -0.4162 | ratio | coefficient |  | eq |  | unsupported |  |
| 162 | sensitivity | **The billing block makes this table unusable feature-by-fea… | 19.8 | percent | predicted_probability |  | eq |  | unsupported |  |
| 163 | sensitivity | **The billing block makes this table unusable feature-by-fea… | 14 | percent | predicted_probability |  | eq |  | unsupported |  |
| 164 | sensitivity | **The billing block makes this table unusable feature-by-fea… | 6 | ratio | predicted_probability |  | eq |  | unsupported |  |
| 165 | sensitivity | **The billing block makes this table unusable feature-by-fea… | -0.2528 | ratio | coefficient |  | eq |  | unsupported |  |
| 166 | sensitivity | **The billing block makes this table unusable feature-by-fea… | 16.1 | percent | predicted_probability |  | eq |  | unsupported |  |
| 167 | findings | **M1 — high — Near-duplicate features `bill_last` and `bill_… | 44429.8135 | currency |  | train | eq |  | unsupported |  |
| 168 | findings | **M1 — high — Near-duplicate features `bill_last` and `bill_… | 44429.8166 | currency |  | train | eq |  | unsupported |  |
| 169 | findings | **M1 — high — Near-duplicate features `bill_last` and `bill_… | 47409.1 | currency |  | train | eq |  | unsupported |  |
| 170 | findings | **M1 — high — Near-duplicate features `bill_last` and `bill_… | 47412.85 | currency |  | train | eq |  | unsupported |  |
| 171 | findings | **M1 — high — Near-duplicate features `bill_last` and `bill_… | -0.5348 | ratio | coefficient | train | eq |  | unsupported |  |
| 172 | findings | **M1 — high — Near-duplicate features `bill_last` and `bill_… | -0.5619 | ratio | coefficient | train | eq |  | unsupported |  |
| 173 | findings | **M1 — high — Near-duplicate features `bill_last` and `bill_… | 0.6805 | ratio | coefficient | train | eq |  | unsupported |  |
| 174 | findings | **T1 — medium — The declared VIF screen at threshold 10.0 re… | 10 | ratio | vif |  | eq |  | unsupported |  |
| 175 | findings | **D1 — low — Undocumented capping and distributional anomali… | 2 | ratio |  | train | eq |  | unsupported |  |
| 176 | findings | **D1 — low — Undocumented capping and distributional anomali… | 1.431 | ratio |  | train | eq |  | unsupported |  |
| 177 | findings | **D1 — low — Undocumented capping and distributional anomali… | -67201 | currency |  | train | eq |  | unsupported |  |
| 178 | findings | **D1 — low — Undocumented capping and distributional anomali… | 27398 | currency |  | train | eq |  | unsupported |  |
| 179 | findings | **D1 — low — Undocumented capping and distributional anomali… | 3119 | currency |  | train | eq |  | unsupported |  |
| 180 | findings | **C1 — info — Mild aggregate under-prediction on the test sp… | 0.2214797 | ratio | mean_predicted | test | eq |  | unsupported |  |
| 181 | findings | **C1 — info — Mild aggregate under-prediction on the test sp… | 0.2246667 | ratio | event_rate | test | eq |  | unsupported |  |
| 182 | findings | **C1 — info — Mild aggregate under-prediction on the test sp… | 1.42 | percent |  | test | eq |  | unsupported |  |
| 183 | findings | **C1 — info — Mild aggregate under-prediction on the test sp… | 0.3 | ratio |  | test | eq |  | unsupported |  |
| 184 | monitoring | 1. **Discrimination.** Track AUC, Gini and KS monthly on sco… | 0.03 | ratio | auc |  | eq |  | unsupported |  |
| 185 | monitoring | 1. **Discrimination.** Track AUC, Gini and KS monthly on sco… | 0.7505 | ratio | auc | test | eq |  | unsupported |  |
| 186 | monitoring | 1. **Discrimination.** Track AUC, Gini and KS monthly on sco… | 0.05 | ratio | auc |  | eq |  | unsupported |  |
| 187 | monitoring | 2. **Calibration.** Track the ratio of mean predicted to obs… | 0.9858 | ratio | calibration_ratio | test | eq |  | unsupported |  |
| 188 | monitoring | 2. **Calibration.** Track the ratio of mean predicted to obs… | 10 | percent | calibration_ratio |  | eq |  | unsupported |  |
| 189 | monitoring | 2. **Calibration.** Track the ratio of mean predicted to obs… | 20 | percent | calibration_ratio |  | eq |  | unsupported |  |
| 190 | monitoring | 2. **Calibration.** Track the ratio of mean predicted to obs… | 25 | percent | calibration_ratio |  | eq |  | unsupported |  |
| 191 | monitoring | 3. **Population stability.** Establish a PSI baseline agains… | 13 | count | feature_count |  | eq |  | unsupported |  |
| 192 | monitoring | 3. **Population stability.** Establish a PSI baseline agains… | 0.1 | ratio | psi |  | eq |  | unsupported |  |
| 193 | monitoring | 3. **Population stability.** Establish a PSI baseline agains… | 0.1 | ratio | psi |  | eq |  | unsupported |  |
| 194 | monitoring | 3. **Population stability.** Establish a PSI baseline agains… | 0.25 | ratio | psi |  | eq |  | unsupported |  |
| 195 | monitoring | 3. **Population stability.** Establish a PSI baseline agains… | 0.25 | ratio | psi |  | eq |  | unsupported |  |
| 196 | monitoring | 4. **Coefficient and collinearity surveillance.** At every r… | 10 | ratio | vif |  | eq |  | unsupported |  |
| 197 | monitoring | 5. **Data integrity gates.** Run automated pre-scoring check… | 2 | ratio |  |  | eq |  | unsupported |  |
| 198 | monitoring | 5. **Data integrity gates.** Run automated pre-scoring check… | 0.95 | ratio | correlation |  | eq |  | unsupported |  |
| 199 | monitoring | 6. **Effective challenge.** Stand up at least one challenger… | 0.02 | ratio | auc | test | eq |  | unsupported |  |
| 200 | monitoring | 7. **Review cadence.** Full revalidation annually, or on tri… | 22.5 | percent | event_rate |  | eq |  | unsupported |  |

## Appendix B — Artifact index

The store holds 14 artifacts; the 8 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `run.data_test` | `a006dcd9` | table | table, 1500 rows | the subject's data_test.csv |
| `run.data_train` | `c522fc63` | table | table, 3500 rows | the subject's data_train.csv |
| `run.features` | `f79bb8bb` | json | json | the subject's features.json |
| `run.metrics` | `c586d0a7` | json | json | the subject's metrics.json |
| `run.model_summary` | `f2e0e9a7` | json | json | the subject's model_summary.json |
| `run.predictions_test` | `c3cfe7db` | table | table, 1500 rows | the subject's predictions_test.csv |
| `run.predictions_train` | `71768746` | table | table, 3500 rows | the subject's predictions_train.csv |
| `run.splits` | `3b6b0a38` | json | json | the subject's splits.json |

## Appendix C — Run trace summary

| quantity | value |
|---|---|
| tool calls | 1 (run_model 1) |
| plan steps (bounded loop) | 0 |
| LLM calls | 8 (plain_llm 1, extract 7) |
| re-asks | 0 |
| repair rounds | 0 |
| tokens in / out | 61,673 / 40,348 |
| notional cost (USD) | 1.6113 |
| wall-clock (s) | 468.15 |
| subject run (s) | 1.39 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | credit_default-plain_llm-20260918T182619Z-6e98ce62 |

## Appendix D — Not checked

| item | reason |
|---|---|
| `check_stability` (R1) | package declares no `regime.column` |
| `run_scenarios` (X1) | not applicable to `binary_classification` |
| out-of-time and vintage-holdout metrics (O1, second rule) | package declares neither split |
| developer claims (T1, claim channel) | `plain_llm` runs no check over `package.yaml`'s declared claims |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
| every check of spec 3.7 but `run_model` | `plain_llm` runs the subject and one model call, by design |
