---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: msr_prepayment
version: "1.0"
model_type: discrete_time_hazard
configuration: plain_llm
model: claude-opus-5[1m]
run_id: msr_prepayment-plain_llm-20260918T213037Z-986f3824
data_mode: synthetic
synthetic_n: 2000
grounding_precision_pre: 0.0000
grounding_precision_post: 0.0000
n_claims: 173
n_findings_by_severity: {high: 3, medium: 3, low: 1, info: 1}
generated: "2026-09-18T21:30:37Z"
illustrative: false
---

# Validation report — `msr_prepayment` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `msr_prepayment` v1.0 | `plain_llm` | claude-opus-5[1m] | synthetic, n = 2000 | 0.0000 → 0.0000 | 3 / 3 / 1 / 1 |
<!-- quaestor:renderer:end -->

This report validates package `msr_prepayment` version 1.0, a discrete-time hazard model of monthly voluntary prepayment intended to support MSR valuation. The model uses ⟦unverified: 12⟧ features and is fit and evaluated on four splits: train (⟦unverified: 36,013⟧ loan-months, ⟦unverified: 934⟧ loans), test (⟦unverified: 15,382⟧ / ⟦unverified: 400⟧), out-of-time (⟦unverified: 12,257⟧ / ⟦unverified: 515⟧) and vintage holdout (⟦unverified: 32,177⟧ / ⟦unverified: 666⟧) [[art:dca79f2f:run.splits]]. Reported performance, the fitted baseline hazard, the feature inventory and a raw profile of the training split were available for review [[art:e8f6c83d:run.metrics]] [[art:f6c2df89:run.model_summary]] [[art:61276a96:run.features]] [[art:232eef87:run.data_train]].

**Overall conclusion: the model is not fit for use in its current form.** The reported discrimination is perfect (AUC = Gini = KS = 1.0) on all four splits, including both holdouts, with Brier scores near ⟦unverified: 1e-8⟧. For a monthly prepayment hazard with an event rate under ⟦unverified: 2%⟧, this is not an achievable result; it is the standard signature of target leakage. Every downstream result in this report — calibration, drift, scenario behaviour — is conditioned on that finding and should be re-derived after the leakage is removed.

Scope limits, stated up front so that the absence of a finding is not read as a clean opinion:

- The model summary supplied was **truncated** after `age_spline_knots` and the baseline hazard series; no coefficient vector, standard errors or covariance matrix were available, so sign, magnitude and stability of covariate effects could not be inspected [[art:f6c2df89:run.model_summary]].
- **No challenger model** was run. Effective challenge (defect class E1) could not be assessed, and no E1 finding is raised in either direction.
- No per-feature AUC, VIF, condition number or PSI was produced by the subject; the multicollinearity and drift findings below rest on structural and distributional reasoning, not on the diagnostics themselves.
- Raw profiles were available for the **training split only**; the corresponding tables for test, out-of-time and vintage holdout were listed but their contents were not provided [[art:057dd4f6:run.data_test]] [[art:32b32e79:run.data_out_of_time]] [[art:eefd735d:run.data_vintage_holdout]].
- The values of `run.status`, `run.stderr`, `run.duration_s` and `runtime.max_seconds` were not provided, so execution success and runtime-cap compliance (defect class R0) could not be verified. No R0 finding is raised.

## 2. Conceptual soundness

The *choice* of feature set is appropriate for a prepayment model and reflects standard industry practice. The design includes a refinance incentive (`incentive`), a burnout proxy (`burnout`), spread-at-origination (`sato`), loan age, origination credit quality (`credit_score`, `orig_ltv`, `orig_upb_log`), note rate, a ⟦unverified: 12⟧-month rate-change term and a sine/cosine seasonality pair [[art:61276a96:run.features]]. Encoding seasonality as an orthogonal sin/cos pair rather than eleven month dummies is a sound choice for a monthly hazard, and the training profile confirms both terms are centred near zero with standard deviation ≈ ⟦unverified: 0.706⟧, consistent with a full annual cycle [[art:232eef87:run.data_train]].

The timing taxonomy is declared as five `at_origination` features, seven `before_period_start` features, zero `during_period` and zero `after_outcome` [[art:61276a96:run.features]]. On its face this is the correct discipline for a discrete-time hazard: every covariate is known at the start of the month whose prepayment is being predicted. The declaration is not, however, consistent with the observed outcome metrics, and the declaration itself is a developer claim that the results breach (Finding ⟦unverified: 2⟧).

The specific concern is `bom_balance_log`, declared `before_period_start`. Its training distribution has mean ⟦unverified: 11.986⟧ and standard deviation ⟦unverified: 1.193⟧ but a **minimum of ⟦unverified: 0.0⟧** [[art:232eef87:run.data_train]], against `orig_upb_log` which has a minimum of ⟦unverified: 10.645⟧ and never approaches zero. A beginning-of-month balance whose log is exactly zero is not an economically meaningful active balance; it is the fingerprint of a terminated loan. If the balance field is populated after the payoff is applied — or if the zero floor is written for loan-months at or after termination — then `bom_balance_log` is functionally an indicator of the outcome, is `after_outcome` in substance whatever its declared timing, and would by itself produce the perfect separation observed. This is the single most likely mechanism for the leakage and the first thing the developer should test.

Two further conceptual points, independent of leakage:

**Baseline hazard shape.** The fitted baseline hazard is essentially flat from loan age ⟦unverified: 0⟧ (⟦unverified: 1.0476e-4⟧) to a maximum at age ⟦unverified: 16⟧ (⟦unverified: 1.0568e-4⟧) — a rise of less than ⟦unverified: 1%⟧ — and then declines monotonically thereafter, reaching ⟦unverified: 7.52e-5⟧ at age ⟦unverified: 53⟧ and roughly ⟦unverified: 3.37e-5⟧ by age ⟦unverified: 99⟧ [[art:f6c2df89:run.model_summary#baseline_hazard]]. Prepayment behaviour does not have this shape. A voluntary prepayment baseline should show a pronounced seasoning ramp over roughly the first ⟦unverified: 24⟧–⟦unverified: 30⟧ months, typically several-fold, before plateauing. A curve that is flat through seasoning and then decays by a factor of three is the wrong functional form for the phenomenon, and it will systematically understate prepayment on newly originated collateral and overstate the value of the servicing strip on it.

**Extrapolation beyond support.** The age spline knots are placed at ⟦unverified: 1,⟧ ⟦unverified: 10,⟧ ⟦unverified: 19,⟧ ⟦unverified: 31⟧ and ⟦unverified: 53⟧ months, and the maximum `loan_age` observed in training is ⟦unverified: 59⟧ months [[art:f6c2df89:run.model_summary]] [[art:232eef87:run.data_train]]. The published baseline hazard nevertheless extends past age ⟦unverified: 99⟧. Every value beyond age ⟦unverified: 53⟧ is an extrapolation past the final knot of a spline, and everything beyond ⟦unverified: 59⟧ is outside the data entirely. For an MSR application the projection horizon is ⟦unverified: 360⟧ months, so the great majority of the hazard path that drives the valuation is unconstrained by any observation. This is a material model-risk exposure regardless of the leakage.

**Level of the baseline.** The baseline hazard of ~⟦unverified: 1.05e-4⟧ per month implies an annualised CPR of about ⟦unverified: 0.13%⟧, against an observed training CPR of ⟦unverified: 9.76%⟧ [[art:e8f6c83d:run.metrics]]. This is not in itself a defect: with uncentred covariates (e.g. `credit_score` with a mean of ⟦unverified: 738⟧) the linear predictor absorbs the level, and the ratio of mean predicted probability to baseline is about ⟦unverified: 82⟧×, which is consistent with that explanation. It is flagged only because an uncentred baseline is not interpretable as a standalone seasoning curve and should not be published or reused as one.

## 3. Data integrity and drift

**Split composition is internally inconsistent.** The four splits declare ⟦unverified: 934⟧ + ⟦unverified: 400⟧ + ⟦unverified: 515⟧ + ⟦unverified: 666⟧ = ⟦unverified: 2,515⟧ loans [[art:dca79f2f:run.splits]]. The training profile reports `loan_id` with minimum ⟦unverified: 1⟧ and maximum ⟦unverified: 1,334⟧ [[art:232eef87:run.data_train]]. If loan identifiers are drawn from a universe of roughly ⟦unverified: 1,334⟧ loans, then ⟦unverified: 2,515⟧ split-loan memberships cannot be disjoint: loans must appear in more than one split. It is suggestive that train (⟦unverified: 934⟧) and test (⟦unverified: 400⟧) sum to exactly ⟦unverified: 1,334,⟧ which would be a clean loan-level partition of the whole universe — and which would then require that essentially all ⟦unverified: 1,181⟧ loans in the out-of-time and vintage-holdout splits be loans already used for fitting. The four `rows_hash` values are distinct, so this is not a duplicated-rows error; it is loan-level, not row-level, contamination. A loan-level overlap of this kind is enough to invalidate the holdouts as independent evidence, because loan-specific unobserved heterogeneity — the dominant driver of prepayment propensity — is shared between fitting and evaluation. This is recorded as Finding ⟦unverified: 3⟧ (L2). The inference rests on the loan-count arithmetic and the observed identifier range rather than on a direct membership comparison, which the available artifacts do not support; the developer should confirm or refute it by intersecting the identifier sets directly.

**Missingness.** All fourteen columns of the training split report exactly ⟦unverified: 0.0⟧ missing [[art:232eef87:run.data_train]]. Complete absence of missingness across credit score, LTV and balance fields is unusual in servicing data and is more consistent with synthetic or heavily pre-imputed data than with a production feed; if imputation occurred upstream it is not documented in any provided artifact. Materially, the cross-split missingness comparison that defect class D1 is defined on **could not be performed at all**, because profiles for the test, out-of-time and vintage-holdout tables were not provided. This is recorded as an informational finding (Finding ⟦unverified: 8⟧) so that the gap is on the record; it is not an assertion that missingness differs.

**Outcome drift across splits is large.** Monthly event rates are ⟦unverified: 0.852%⟧ (train), ⟦unverified: 0.806%⟧ (test), ⟦unverified: 1.795%⟧ (out-of-time) and ⟦unverified: 0.482%⟧ (vintage holdout); the corresponding actual CPRs are ⟦unverified: 9.76%⟧, ⟦unverified: 9.26%⟧, ⟦unverified: 19.53%⟧ and ⟦unverified: 5.63%⟧ [[art:dca79f2f:run.splits]] [[art:e8f6c83d:run.metrics]]. The out-of-time period runs at ⟦unverified: 2.11⟧× the training event rate and the vintage holdout at ⟦unverified: 0.57⟧×, so actual prepayment speeds vary by a factor of ⟦unverified: 3.5⟧ across the evaluation regimes. That is a genuine rate-regime shift, and it means the out-of-time and vintage splits are testing the model in environments materially unlike the fitting environment. PSI on features and on scores was not computed and could not be computed from the artifacts supplied, so the drift finding (Finding ⟦unverified: 5⟧) is evidenced on the outcome distributions rather than on a PSI statistic.

**Sample window.** The training split spans periods ⟦unverified: 201402⟧ to ⟦unverified: 201912⟧ [[art:232eef87:run.data_train]]. Because the period ranges of the other three splits were not provided, it could not be verified that the out-of-time split is in fact strictly later than training, or that the vintage holdout comprises genuinely held-out origination cohorts. Given the loan-count inconsistency above, this verification is the necessary next step, not an optional one.

**Covariate ranges are plausible.** Note rate ⟦unverified: 2.285⟧–⟦unverified: 6.384⟧, original LTV ⟦unverified: 31⟧–⟦unverified: 97,⟧ credit score ⟦unverified: 620⟧–⟦unverified: 820,⟧ incentive −⟦unverified: 3.12⟧ to +⟦unverified: 3.17⟧ and burnout ⟦unverified: 0⟧–⟦unverified: 9.32⟧ are all within reasonable bounds for agency collateral and show no sentinel values (−⟦unverified: 999,⟧ ⟦unverified: 9999⟧) or impossible entries [[art:232eef87:run.data_train]]. The sole exception is the `bom_balance_log` floor at zero discussed in section 2.

## 4. Outcomes analysis

The outcome metrics are the central finding of this validation.

| Split | n | Event rate | AUC | Gini | KS | Brier | Logloss | Cal. slope |
|---|---|---|---|---|---|---|---|---|
| train | ⟦unverified: 36,013⟧ | ⟦unverified: 0.00852⟧ | 1.0 | 1.0 | 1.0 | ⟦unverified: 1.10e-8⟧ | ⟦unverified: 9.13e-5⟧ | ⟦unverified: 2.867⟧ |
| test | ⟦unverified: 15,382⟧ | ⟦unverified: 0.00806⟧ | 1.0 | 1.0 | 1.0 | ⟦unverified: 1.01e-8⟧ | ⟦unverified: 9.04e-5⟧ | ⟦unverified: 2.833⟧ |
| out_of_time | ⟦unverified: 12,257⟧ | ⟦unverified: 0.01795⟧ | 1.0 | 1.0 | 1.0 | ⟦unverified: 1.38e-8⟧ | ⟦unverified: 9.06e-5⟧ | ⟦unverified: 2.924⟧ |
| vintage_holdout | ⟦unverified: 32,177⟧ | ⟦unverified: 0.00482⟧ | 1.0 | 1.0 | 1.0 | ⟦unverified: 8.65e-9⟧ | ⟦unverified: 8.63e-5⟧ | ⟦unverified: 2.797⟧ |

(all from [[art:e8f6c83d:run.metrics]])

**Discrimination is perfect on every split, which is not a credible result.** AUC, Gini and KS all attain their theoretical maxima simultaneously on four separate populations, including a regime whose event rate is more than double the training regime's. Prepayment is a borrower decision driven substantially by unobservable factors — life events, solicitation, broker contact — and no covariate set restricted to loan characteristics and rates can order ⟦unverified: 36,013⟧ loan-months without a single inversion. The scale of the improbability is worth stating numerically: a null model predicting the base rate on the training split would score a Brier of roughly ⟦unverified: 8.45e-3⟧ and a logloss of roughly ⟦unverified: 4.9e-2⟧. The reported Brier of ⟦unverified: 1.10e-8⟧ is better by a factor of about ⟦unverified: 770,000⟧ and the logloss by a factor of about ⟦unverified: 540⟧. Results of this kind arise from a covariate that encodes the label, not from a well-specified hazard model. This is Finding ⟦unverified: 1⟧ (L1, high).

The usual corroborating check reinforces the diagnosis. Under genuine signal one expects some out-of-sample degradation, and under the severe regime shift documented in section 3 one expects a visible gap between the training and out-of-time AUC. There is none — the out-of-time AUC is identical to the training AUC to the reported precision. A leak that travels with the row travels into every split equally, which is exactly the pattern observed. Accordingly **no O1 finding is raised**: the train-to-holdout gap is zero, and its being zero is evidence for the leakage finding rather than evidence of robustness. For the same reason, the absence of an R1 finding should not be read as a demonstration of regime stability; with AUC saturated at 1.0 in every regime the statistic has no power to reveal instability, and the coefficient vector that would allow a sign-flip test across regimes was not available in the truncated model summary [[art:f6c2df89:run.model_summary]].

**Calibration is materially wrong in slope on all four splits.** The calibration slope ranges from ⟦unverified: 2.797⟧ to ⟦unverified: 2.924⟧ [[art:e8f6c83d:run.metrics]], against an acceptance band that for a model of this type would conventionally be about ⟦unverified: 0.85⟧ to ⟦unverified: 1.15⟧. Every split breaches it, and breaches it in the same direction by roughly a factor of three. A slope near ⟦unverified: 3⟧ means the predicted log-odds are compressed relative to the outcome: the model's dispersion of risk across loans is far too narrow, so low-propensity loans are over-predicted and high-propensity loans under-predicted. For MSR the aggregate speed is only half the requirement; loan-level dispersion drives the convexity of the servicing strip and the value of the tail, and a slope of ⟦unverified: 2.9⟧ will misprice that tail in both directions. This is Finding ⟦unverified: 4⟧ (C1, high).

**Calibration in level is good but biased one way.** Mean predicted probability tracks the observed event rate closely on all four splits — ⟦unverified: 0.008607⟧ vs ⟦unverified: 0.008525⟧ (train), ⟦unverified: 0.008144⟧ vs ⟦unverified: 0.008061⟧ (test), ⟦unverified: 0.018019⟧ vs ⟦unverified: 0.017949⟧ (out-of-time), ⟦unverified: 0.004899⟧ vs ⟦unverified: 0.004817⟧ (vintage) — and the CPR comparison is correspondingly tight [[art:e8f6c83d:run.metrics]]. The bias is small but **consistently positive on all four splits**: predicted CPR exceeds actual by +⟦unverified: 0.9%⟧ relative (train), +1.0% (test), +⟦unverified: 0.4%⟧ (out-of-time) and +⟦unverified: 1.7%⟧ (vintage). A one-sided error repeated across four independent populations is a systematic over-prediction of speed, not sampling noise. Its magnitude is immaterial next to the slope defect and it is folded into Finding ⟦unverified: 4⟧ rather than raised separately. Note also that this level agreement is what one would expect under leakage: a leaking model still reproduces the base rate, so aggregate CPR agreement provides no reassurance here.

## 5. Sensitivity and scenario analysis

A `run.projection` artifact exists [[art:7d3ba32d:run.projection]] but its contents were not provided, so the projected CPR vector, the horizon used and any scenario grid could not be examined. No rate-shock scenario set, no incentive-response curve and no S-curve diagnostic were supplied by the subject. The sensitivity assessment below is therefore confined to what the fitted structure itself implies, and it is incomplete; an S-curve test against the incentive variable is a required addition before the model can be approved.

The one response curve that was available is the age dimension of the baseline hazard, and it does not have the correct shape. Across ages ⟦unverified: 0⟧–⟦unverified: 16⟧ it is flat to within ⟦unverified: 1%⟧, and from age ⟦unverified: 17⟧ onward it declines monotonically for the remainder of the published series, ending at roughly a third of its peak [[art:f6c2df89:run.model_summary#baseline_hazard]]. A prepayment model is expected to produce a rising seasoning ramp through roughly the first two years; this curve is directionally wrong over precisely the region that dominates MSR value for recent originations, and it is then extrapolated far beyond both its final knot (⟦unverified: 53⟧) and the maximum age observed in training (⟦unverified: 59⟧) [[art:232eef87:run.data_train]]. Under a ⟦unverified: 360⟧-month MSR projection the model would be operating outside its estimation support for over ⟦unverified: 80%⟧ of the horizon, with a decaying hazard that will mechanically overstate the length of the servicing cash-flow stream and therefore overstate MSR value. This is Finding ⟦unverified: 6⟧ (X1).

A further structural sensitivity concern is the rate-family feature block. `note_rate`, `sato`, `incentive` and `rate_change_12m` are four near-affine functions of the same two underlying quantities — the loan's note rate and the prevailing market rate — and `burnout` is by construction a path functional of `incentive` [[art:61276a96:run.features]]. Separately, `bom_balance_log` (mean ⟦unverified: 11.986⟧) and `orig_upb_log` (mean ⟦unverified: 12.123⟧) are near-duplicates for unseasoned loans [[art:232eef87:run.data_train]]. Under collinearity of this kind the individual coefficients are unstable and can take economically wrong signs even when the fitted surface is adequate, which makes the model's response to a rate shock unreliable even where its in-sample fit is not. No VIF or condition number was produced, so this is raised at low severity as a design and diagnostic gap rather than a measured breach (Finding ⟦unverified: 7,⟧ M1).

## 6. Findings and recommendations

Findings are listed in the accompanying JSON. In summary:

| # | Class | Severity | Title |
|---|---|---|---|
| ⟦unverified: 1⟧ | L1 | high | Perfect discrimination on all four splits indicates target leakage |
| ⟦unverified: 2⟧ | T1 | medium | Declared leakage-free feature timing is contradicted by the outcome metrics |
| ⟦unverified: 3⟧ | L2 | high | Split loan counts exceed the loan universe, implying loans shared across splits |
| ⟦unverified: 4⟧ | C1 | high | Calibration slope ≈ ⟦unverified: 2.8⟧–⟦unverified: 2.9⟧ on every split, with consistent positive CPR bias |
| ⟦unverified: 5⟧ | S1 | medium | Event rate varies ⟦unverified: 3.5⟧× across splits; no PSI computed |
| ⟦unverified: 6⟧ | X1 | medium | Baseline hazard has no seasoning ramp and is extrapolated far beyond support |
| ⟦unverified: 7⟧ | M1 | low | Collinear rate-family and balance features; no VIF or condition number produced |
| ⟦unverified: 8⟧ | D1 | info | Cross-split missingness comparison not possible from the artifacts supplied |

Recommendations, in priority order:

1. **Do not deploy, and do not use the current results to support any MSR mark.** Treat Findings ⟦unverified: 1⟧ and ⟦unverified: 3⟧ as blocking.
2. **Isolate the leak.** Compute single-feature AUC for all twelve features; any feature exceeding ⟦unverified: 0.90⟧ alone is the leak. Begin with `bom_balance_log`, whose zero floor is the leading candidate, and audit the construction query for whether balance is snapshot at the start of the month or written after the payoff posts. Re-examine `burnout` on the same question, since a path functional can absorb terminal-month information.
3. **Rebuild the splits with a documented, verified loan-level partition.** Intersect the identifier sets of all four splits and publish the intersections. The out-of-time split must be strictly later in calendar time and the vintage holdout must consist of origination cohorts wholly absent from training.
4. **Refit and re-evaluate from scratch after (⟦unverified: 2⟧) and (⟦unverified: 3⟧).** Every metric in this report must be regenerated; none of them carry forward.
5. **Respecify the age effect.** Add knots in the ⟦unverified: 2⟧–⟦unverified: 30⟧ month range so the seasoning ramp can be expressed, and either cap the projection at the estimation support or document and reserve for the extrapolation beyond age ⟦unverified: 59⟧.
6. **Address calibration explicitly** once leakage is removed, reporting the slope with a confidence interval against a pre-declared band, and produce a decile-level reliability table rather than the slope alone.
7. **Produce collinearity diagnostics** (VIF and condition number over the twelve-feature design) and a rate-shock S-curve showing predicted CPR against incentive from −⟦unverified: 200⟧bp to +⟦unverified: 200⟧bp.
8. **Commission a challenger.** No effective challenge was performed. A simple seasoning-plus-incentive logistic baseline would be sufficient to bound the value added by the current specification.

### F-001 · L1 leakage · severity **high**

AUC, Gini and KS are all exactly 1.0 on train, test, out-of-time and vintage holdout simultaneously, with Brier scores of 8.6e-9 to 1.4e-8 and logloss of roughly 9e-5. For a monthly prepayment hazard with event rates between 0.48% and 1.79% this is not an attainable result. A null model predicting the base rate on the training split would score a Brier near 8.45e-3 and a logloss near 4.9e-2, so the reported values are better by factors of roughly 770,000 and 540 respectively. Prepayment is driven substantially by unobservable borrower factors, and no covariate set limited to loan characteristics and rates can rank 36,013 loan-months without a single inversion. The pattern is the standard signature of a covariate that encodes the outcome. The leading candidate is bom_balance_log, declared before_period_start but showing a training minimum of exactly 0.0 against a mean of 11.99 and standard deviation of 1.19, while orig_upb_log never falls below 10.65; a zero log balance is not an active-loan value but the fingerprint of a terminated loan, so if the balance field is snapshot after the payoff posts the feature is after_outcome in substance. The corroborating evidence is that there is no degradation whatsoever from train to the out-of-time split even though the out-of-time event rate is 2.11 times the training rate, which is what happens when a leak travels with the row into every split. Single-feature AUC was not computed by the subject, so the specific feature is identified as the leading hypothesis rather than as confirmed; the developer should compute univariate AUC for all twelve features, where any value above 0.90 identifies the leak. No metric in this submission can be relied upon until this is resolved.

### F-002 · L2 contamination · severity **high**

The four splits declare 934, 400, 515 and 666 loans, summing to 2,515 loan memberships. The training raw profile reports loan_id with a minimum of 1 and a maximum of 1,334, indicating a loan universe of roughly 1,334. Those two facts cannot both hold under a disjoint partition: at least 1,181 memberships must be repeats. It is notable that train and test sum to exactly 1,334, which would constitute a clean loan-level partition of the entire universe and would then force essentially every loan in the out-of-time and vintage-holdout splits to be a loan already used in fitting. The four rows_hash values are distinct, so this is loan-level rather than row-level duplication, but for a panel hazard model that distinction does not mitigate: loan-specific unobserved heterogeneity is the dominant driver of prepayment propensity and is shared between fitting and evaluation whenever the same loan appears in both, which destroys the independence of the holdouts. The inference is drawn from the loan-count arithmetic and the observed identifier range rather than from a direct membership comparison, which the supplied artifacts do not permit; the developer should intersect the identifier sets of all four splits directly and publish the result, which will either confirm this finding or refute it immediately. Until then the out-of-time and vintage-holdout results provide no independent evidence about generalisation.

### F-003 · C1 calibration · severity **high**

The calibration slope is 2.867 on train, 2.833 on test, 2.924 out-of-time and 2.797 on the vintage holdout. All four breach a conventional acceptance band of roughly 0.85 to 1.15, all in the same direction and by roughly a factor of three. A slope near 3 means the predicted log-odds are compressed relative to the observed outcome: the model spreads risk across loans far too narrowly, over-predicting low-propensity loans and under-predicting high-propensity ones. For MSR this is material even though the aggregate level is close, because loan-level dispersion drives the convexity of the servicing strip and the value of the fast-pay tail; a slope of 2.9 will misprice that tail in both directions. Separately, calibration in level is tight but biased one way on every split: mean predicted exceeds the observed event rate on all four (0.008607 vs 0.008525, 0.008144 vs 0.008061, 0.018019 vs 0.017949, 0.004899 vs 0.004817), and predicted CPR exceeds actual by +0.9%, +1.0%, +0.4% and +1.7% relative. A one-sided error repeated across four populations is systematic over-prediction of speed rather than noise; it is small next to the slope defect and is reported here rather than as a separate finding. Note that aggregate level agreement offers no reassurance in the presence of the leakage finding, since a leaking model still reproduces the base rate. Remediation requires refitting after leakage removal and then re-testing the slope with a confidence interval against a pre-declared band, supported by a decile reliability table rather than the slope statistic alone.

### F-004 · T1 declared threshold · severity **medium**

The feature inventory declares a clean timing taxonomy: five features at_origination, seven before_period_start, zero during_period and zero after_outcome. That declaration is a developer claim that no covariate carries information unavailable at the start of the predicted month, and it is the control on which the hazard specification depends. The outcome metrics breach it: perfect separation on four populations cannot be produced by a feature set that is genuinely restricted to pre-period information. Either the timing labels are wrong for at least one feature, or the construction of a labelled feature does not match its label. bom_balance_log is labelled before_period_start yet takes a value of exactly 0.0 at its training minimum, which is inconsistent with a beginning-of-month balance on an active loan and consistent with a post-termination snapshot. The declared taxonomy should not be accepted at face value again until the feature-construction queries have been audited against it row by row and the audit published as an artifact.

### F-005 · S1 population drift · severity **medium**

Monthly event rates are 0.852% on train, 0.806% on test, 1.795% out-of-time and 0.482% on the vintage holdout, with corresponding actual CPRs of 9.76%, 9.26%, 19.53% and 5.63%. The out-of-time split runs at 2.11 times the training rate and the vintage holdout at 0.57 times it, so realised prepayment speeds differ by a factor of about 3.5 across the evaluation regimes. This is a genuine rate-regime shift, and it means the holdouts test the model in environments materially unlike the one it was fitted in, which raises the required standard for the age and incentive response functions discussed elsewhere in this report. No PSI was computed on features or on scores by the subject, and it could not be computed from the artifacts supplied, so this finding is evidenced on the outcome distributions across splits rather than on a PSI statistic against a threshold. Feature-level and score-level PSI against the training reference should be produced as part of remediation and thereafter monitored monthly at 0.10 watch and 0.25 breach thresholds.

### F-006 · X1 scenario analysis · severity **medium**

The fitted baseline hazard is flat to within 1% from loan age 0 (1.0476e-4) to its maximum at age 16 (1.0568e-4) and then declines monotonically, reaching 7.52e-5 at age 53 and about 3.37e-5 by age 99. This is the wrong shape for voluntary prepayment, which is expected to ramp upward substantially over roughly the first 24 to 30 months before plateauing. A curve that is flat through the seasoning window and then decays by a factor of three is directionally wrong over precisely the region that dominates MSR value for recently originated collateral, and the monotone decay thereafter will mechanically overstate the expected length of the servicing cash-flow stream and hence MSR value. Compounding this, the age spline knots are placed at 1, 10, 19, 31 and 53 while the maximum loan_age in training is 59, yet the published hazard series extends past age 99. Every value beyond age 53 extrapolates past the final knot and everything beyond 59 leaves the data entirely; under a 360-month MSR projection the model would be extrapolating for more than 80% of the horizon. The projection artifact itself was not available for inspection, and no rate-shock scenario grid or incentive S-curve was produced, so this finding rests on the age response alone and the sensitivity assessment is incomplete. Remediation should add knots in the 2 to 30 month range so a seasoning ramp can be expressed, and should either cap the projection at the estimation support or document and reserve for the extrapolation.

### F-007 · M1 collinearity · severity **low**

The design contains four near-affine functions of the same two underlying quantities: note_rate, sato, incentive and rate_change_12m are all constructed from the loan's note rate and the prevailing market rate, and burnout is by construction a path functional of incentive. Separately, bom_balance_log (training mean 11.986) and orig_upb_log (training mean 12.123) are close to duplicates for unseasoned loans. Under collinearity of this severity individual coefficients become unstable and can take economically wrong signs even where the fitted surface is adequate, which makes the model's response to a rate shock unreliable and undermines any attribution of effect to a specific driver. No VIF, condition number or correlation matrix was produced by the subject, and the truncated model summary contains no coefficient vector against which sign plausibility could be checked, so no measured threshold breach is asserted. This is raised at low severity as a specification and diagnostic gap: VIF and the design condition number should be computed and published, and if they confirm the concern the rate-family block should be reduced to an orthogonal parameterisation.

### F-008 · D1 data integrity · severity **info**

The defect class D1 is defined on a comparison of missingness between splits, and that comparison could not be performed for this submission. A raw profile was available for the training split only, where all fourteen columns report exactly 0.0 missing; the corresponding tables for the test, out-of-time and vintage-holdout splits exist in the store but their profiles were not provided. This finding therefore records a validation gap rather than an assertion that missingness differs across splits. Two related observations are noted for the record: complete absence of missingness across credit score, LTV and balance fields is unusual for production servicing data and is more typical of synthetic or pre-imputed inputs, and no artifact documents whether upstream imputation occurred. Remediation is to publish raw profiles for all four splits so that the comparison can be made, and to document any imputation applied upstream of the profile.

Candidates raised and not promoted: none.

### Open items

No open item was recorded for this validation.

## 7. Ongoing monitoring recommendations

Once the model is rebuilt and re-approved, the following monitoring should be in place before any production use.

- **Leakage tripwire.** Any monthly refresh reporting AUC above ⟦unverified: 0.90⟧, or a Brier more than two orders of magnitude below the base-rate null, should halt promotion automatically and route to re-validation. The present submission would have been caught at this gate.
- **Monthly actual-vs-predicted CPR** at portfolio level and by vintage, coupon and servicer, with a tolerance band (for example ±⟦unverified: 10%⟧ relative) and escalation on three consecutive one-sided breaches. The consistent positive bias in section 4 is the pattern this control is designed to detect.
- **Quarterly recalibration check.** Refit the calibration slope and intercept on a rolling twelve-month window; escalate on a slope outside ⟦unverified: 0.85⟧–⟦unverified: 1.15⟧.
- **Feature and score PSI monthly** against the training reference, with thresholds at ⟦unverified: 0.10⟧ (watch) and ⟦unverified: 0.25⟧ (breach), reported per feature. This control does not currently exist and could not be evaluated for this submission.
- **Split-integrity check at every refresh.** Assert programmatically that loan identifier sets across train, test, out-of-time and vintage holdout are pairwise disjoint, and fail the build otherwise.
- **Age-support monitor.** Alert when the weighted-average loan age of the served portfolio moves outside the estimation range, since the hazard is extrapolated beyond age ⟦unverified: 59⟧.
- **Rate-regime monitor.** Track the distribution of `incentive` and the realised CPR against the regime in which the model was fit; the ⟦unverified: 3.5⟧× spread across splits documented in section 3 shows the model will be asked to operate well outside its fitting environment.
- **Annual full revalidation**, with a documented challenger, since no effective challenge exists for this version.

## Appendix A — Claims

Grounding precision 0.0000 before repair (0 of 173 claims verified; 73 unsupported, 96 dangling, 4 unattributed) and 0.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 0/11; conceptual_soundness 0/33; data_integrity 0/42; outcomes 0/46; sensitivity 0/12; findings 0/21; monitoring 0/8.

Developer claims: `plain_llm` runs no check over `package.yaml`'s declared claims See Appendix D.

Excluded numeric tokens (not claims): section_number (section 2, section 3, 1., 2.); citation_hash (dca79f2f, e8f6c83d, f6c2df89, 61276a96); package_version (1.0); extractor_returned_excluded_token (1.0, 4.0, 11.0, 5.0).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | This report validates package `msr_prepayment` version 1.0,… | 12 | count | features |  | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 2 | summary | This report validates package `msr_prepayment` version 1.0,… | 36013 | count | splits | train | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 3 | summary | This report validates package `msr_prepayment` version 1.0,… | 934 | count | splits | train | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 4 | summary | This report validates package `msr_prepayment` version 1.0,… | 15382 | count | splits | test | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 5 | summary | This report validates package `msr_prepayment` version 1.0,… | 400 | count | splits | test | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 6 | summary | This report validates package `msr_prepayment` version 1.0,… | 12257 | count | splits | out_of_time | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 7 | summary | This report validates package `msr_prepayment` version 1.0,… | 515 | count | splits | out_of_time | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 8 | summary | This report validates package `msr_prepayment` version 1.0,… | 32177 | count | splits | vintage_holdout | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 9 | summary | This report validates package `msr_prepayment` version 1.0,… | 666 | count | splits | vintage_holdout | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 10 | summary | **Overall conclusion: the model is not fit for use in its cu… | 1e-08 | ratio | brier |  | eq |  | unsupported |  |
| 11 | summary | **Overall conclusion: the model is not fit for use in its cu… | 2 | percent | event_rate |  | eq |  | unsupported |  |
| 12 | conceptual_soundness | The *choice* of feature set is appropriate for a prepayment… | 12 | months |  |  | eq | `[[art:61276a96:run.features]]` | dangling |  |
| 13 | conceptual_soundness | The *choice* of feature set is appropriate for a prepayment… | 0.706 | ratio |  | train | eq | `[[art:232eef87:run.data_train]]` | dangling |  |
| 14 | conceptual_soundness | The timing taxonomy is declared as five `at_origination` fea… | 2 | count |  |  | eq |  | unsupported |  |
| 15 | conceptual_soundness | The specific concern is `bom_balance_log`, declared `before_… | 11.986 | ratio |  | train | eq | `[[art:232eef87:run.data_train]]` | dangling |  |
| 16 | conceptual_soundness | The specific concern is `bom_balance_log`, declared `before_… | 1.193 | ratio |  | train | eq | `[[art:232eef87:run.data_train]]` | dangling |  |
| 17 | conceptual_soundness | The specific concern is `bom_balance_log`, declared `before_… | 0 | ratio |  | train | eq | `[[art:232eef87:run.data_train]]` | dangling |  |
| 18 | conceptual_soundness | The specific concern is `bom_balance_log`, declared `before_… | 10.645 | ratio |  | train | eq | `[[art:232eef87:run.data_train]]` | dangling |  |
| 19 | conceptual_soundness | **Baseline hazard shape.** The fitted baseline hazard is ess… | 0 | months |  |  | eq | `[[art:f6c2df89:run.model_summary#baseline_hazard]]` | dangling |  |
| 20 | conceptual_soundness | **Baseline hazard shape.** The fitted baseline hazard is ess… | 0.00010476 | ratio | baseline_hazard |  | eq | `[[art:f6c2df89:run.model_summary#baseline_hazard]]` | dangling |  |
| 21 | conceptual_soundness | **Baseline hazard shape.** The fitted baseline hazard is ess… | 16 | months |  |  | eq | `[[art:f6c2df89:run.model_summary#baseline_hazard]]` | dangling |  |
| 22 | conceptual_soundness | **Baseline hazard shape.** The fitted baseline hazard is ess… | 0.00010568 | ratio | baseline_hazard |  | eq | `[[art:f6c2df89:run.model_summary#baseline_hazard]]` | dangling |  |
| 23 | conceptual_soundness | **Baseline hazard shape.** The fitted baseline hazard is ess… | 1 | percent | baseline_hazard |  | eq | `[[art:f6c2df89:run.model_summary#baseline_hazard]]` | dangling |  |
| 24 | conceptual_soundness | **Baseline hazard shape.** The fitted baseline hazard is ess… | 7.52e-05 | ratio | baseline_hazard |  | eq | `[[art:f6c2df89:run.model_summary#baseline_hazard]]` | dangling |  |
| 25 | conceptual_soundness | **Baseline hazard shape.** The fitted baseline hazard is ess… | 53 | months |  |  | eq | `[[art:f6c2df89:run.model_summary#baseline_hazard]]` | dangling |  |
| 26 | conceptual_soundness | **Baseline hazard shape.** The fitted baseline hazard is ess… | 3.37e-05 | ratio | baseline_hazard |  | eq | `[[art:f6c2df89:run.model_summary#baseline_hazard]]` | dangling |  |
| 27 | conceptual_soundness | **Baseline hazard shape.** The fitted baseline hazard is ess… | 99 | months |  |  | eq | `[[art:f6c2df89:run.model_summary#baseline_hazard]]` | dangling |  |
| 28 | conceptual_soundness | **Baseline hazard shape.** The fitted baseline hazard is ess… | 24 | months |  |  | eq |  | unsupported |  |
| 29 | conceptual_soundness | **Baseline hazard shape.** The fitted baseline hazard is ess… | 30 | months |  |  | eq |  | unsupported |  |
| 30 | conceptual_soundness | **Extrapolation beyond support.** The age spline knots are p… | 1 | months |  |  | eq | `[[art:f6c2df89:run.model_summary]]` | dangling |  |
| 31 | conceptual_soundness | **Extrapolation beyond support.** The age spline knots are p… | 10 | months |  |  | eq | `[[art:f6c2df89:run.model_summary]]` | dangling |  |
| 32 | conceptual_soundness | **Extrapolation beyond support.** The age spline knots are p… | 19 | months |  |  | eq | `[[art:f6c2df89:run.model_summary]]` | dangling |  |
| 33 | conceptual_soundness | **Extrapolation beyond support.** The age spline knots are p… | 31 | months |  |  | eq | `[[art:f6c2df89:run.model_summary]]` | dangling |  |
| 34 | conceptual_soundness | **Extrapolation beyond support.** The age spline knots are p… | 53 | months |  |  | eq | `[[art:f6c2df89:run.model_summary]]` | dangling |  |
| 35 | conceptual_soundness | **Extrapolation beyond support.** The age spline knots are p… | 59 | months |  | train | eq | `[[art:232eef87:run.data_train]]` | dangling |  |
| 36 | conceptual_soundness | **Extrapolation beyond support.** The age spline knots are p… | 99 | months |  |  | eq |  | unsupported |  |
| 37 | conceptual_soundness | **Extrapolation beyond support.** The age spline knots are p… | 53 | months |  |  | eq |  | unsupported |  |
| 38 | conceptual_soundness | **Extrapolation beyond support.** The age spline knots are p… | 59 | months |  |  | eq |  | unsupported |  |
| 39 | conceptual_soundness | **Extrapolation beyond support.** The age spline knots are p… | 360 | months |  |  | eq |  | unsupported |  |
| 40 | conceptual_soundness | **Level of the baseline.** The baseline hazard of ~1.05e-4 p… | 0.000105 | ratio | baseline_hazard |  | eq |  | unsupported |  |
| 41 | conceptual_soundness | **Level of the baseline.** The baseline hazard of ~1.05e-4 p… | 0.13 | percent | event_rate |  | eq |  | unsupported |  |
| 42 | conceptual_soundness | **Level of the baseline.** The baseline hazard of ~1.05e-4 p… | 9.76 | percent | event_rate | train | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 43 | conceptual_soundness | **Level of the baseline.** The baseline hazard of ~1.05e-4 p… | 738 | ratio |  | train | eq |  | unsupported |  |
| 44 | conceptual_soundness | **Level of the baseline.** The baseline hazard of ~1.05e-4 p… | 82 | ratio |  |  | eq |  | unsupported |  |
| 45 | data_integrity | **Split composition is internally inconsistent.** The four s… | 934 | count | loans | train | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 46 | data_integrity | **Split composition is internally inconsistent.** The four s… | 400 | count | loans | test | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 47 | data_integrity | **Split composition is internally inconsistent.** The four s… | 515 | count | loans | out_of_time | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 48 | data_integrity | **Split composition is internally inconsistent.** The four s… | 666 | count | loans | vintage_holdout | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 49 | data_integrity | **Split composition is internally inconsistent.** The four s… | 2515 | count | loans |  | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 50 | data_integrity | **Split composition is internally inconsistent.** The four s… | 1 | count | loan_id | train | eq | `[[art:232eef87:run.data_train]]` | dangling |  |
| 51 | data_integrity | **Split composition is internally inconsistent.** The four s… | 1334 | count | loan_id | train | eq | `[[art:232eef87:run.data_train]]` | dangling |  |
| 52 | data_integrity | **Split composition is internally inconsistent.** The four s… | 1334 | count | loans |  | eq |  | unsupported |  |
| 53 | data_integrity | **Split composition is internally inconsistent.** The four s… | 2515 | count | loans |  | eq |  | unsupported |  |
| 54 | data_integrity | **Split composition is internally inconsistent.** The four s… | 934 | count | loans | train | eq |  | unsupported |  |
| 55 | data_integrity | **Split composition is internally inconsistent.** The four s… | 400 | count | loans | test | eq |  | unsupported |  |
| 56 | data_integrity | **Split composition is internally inconsistent.** The four s… | 1334 | count | loans |  | eq |  | unsupported |  |
| 57 | data_integrity | **Split composition is internally inconsistent.** The four s… | 1181 | count | loans |  | eq |  | unsupported |  |
| 58 | data_integrity | **Split composition is internally inconsistent.** The four s… | 3 | ratio |  |  | eq |  | unsupported |  |
| 59 | data_integrity | **Missingness.** All fourteen columns of the training split… | 0 | percent | missing_rate | train | eq | `[[art:232eef87:run.data_train]]` | dangling |  |
| 60 | data_integrity | **Missingness.** All fourteen columns of the training split… | 8 | ratio |  |  | eq |  | unsupported |  |
| 61 | data_integrity | **Outcome drift across splits is large.** Monthly event rate… | 0.852 | percent | event_rate | train | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 62 | data_integrity | **Outcome drift across splits is large.** Monthly event rate… | 0.806 | percent | event_rate | test | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 63 | data_integrity | **Outcome drift across splits is large.** Monthly event rate… | 1.795 | percent | event_rate | out_of_time | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 64 | data_integrity | **Outcome drift across splits is large.** Monthly event rate… | 0.482 | percent | event_rate | vintage_holdout | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 65 | data_integrity | **Outcome drift across splits is large.** Monthly event rate… | 9.76 | percent | actual_cpr | train | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 66 | data_integrity | **Outcome drift across splits is large.** Monthly event rate… | 9.26 | percent | actual_cpr | test | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 67 | data_integrity | **Outcome drift across splits is large.** Monthly event rate… | 19.53 | percent | actual_cpr | out_of_time | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 68 | data_integrity | **Outcome drift across splits is large.** Monthly event rate… | 5.63 | percent | actual_cpr | vintage_holdout | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 69 | data_integrity | **Outcome drift across splits is large.** Monthly event rate… | 2.11 | ratio | event_rate | out_of_time | ratio |  | unsupported |  |
| 70 | data_integrity | **Outcome drift across splits is large.** Monthly event rate… | 0.57 | ratio | event_rate | vintage_holdout | ratio |  | unsupported |  |
| 71 | data_integrity | **Outcome drift across splits is large.** Monthly event rate… | 3.5 | ratio | actual_cpr |  | ratio |  | unsupported |  |
| 72 | data_integrity | **Outcome drift across splits is large.** Monthly event rate… | 5 | ratio |  |  | eq |  | unsupported |  |
| 73 | data_integrity | **Sample window.** The training split spans periods 201402 t… | 201402 | ratio | period_min | train | eq | `[[art:232eef87:run.data_train]]` | dangling |  |
| 74 | data_integrity | **Sample window.** The training split spans periods 201402 t… | 201912 | ratio | period_max | train | eq | `[[art:232eef87:run.data_train]]` | dangling |  |
| 75 | data_integrity | **Covariate ranges are plausible.** Note rate 2.285–6.384, o… | 2.285 | ratio | note_rate_min | train | eq | `[[art:232eef87:run.data_train]]` | dangling |  |
| 76 | data_integrity | **Covariate ranges are plausible.** Note rate 2.285–6.384, o… | 6.384 | ratio | note_rate_max | train | eq | `[[art:232eef87:run.data_train]]` | dangling |  |
| 77 | data_integrity | **Covariate ranges are plausible.** Note rate 2.285–6.384, o… | 31 | ratio | original_ltv_min | train | eq | `[[art:232eef87:run.data_train]]` | dangling |  |
| 78 | data_integrity | **Covariate ranges are plausible.** Note rate 2.285–6.384, o… | 97 | ratio | original_ltv_max | train | eq | `[[art:232eef87:run.data_train]]` | dangling |  |
| 79 | data_integrity | **Covariate ranges are plausible.** Note rate 2.285–6.384, o… | 620 | ratio | credit_score_min | train | eq | `[[art:232eef87:run.data_train]]` | dangling |  |
| 80 | data_integrity | **Covariate ranges are plausible.** Note rate 2.285–6.384, o… | 820 | ratio | credit_score_max | train | eq | `[[art:232eef87:run.data_train]]` | dangling |  |
| 81 | data_integrity | **Covariate ranges are plausible.** Note rate 2.285–6.384, o… | 3.12 | ratio |  |  | eq |  | unattributed |  |
| 82 | data_integrity | **Covariate ranges are plausible.** Note rate 2.285–6.384, o… | 3.17 | ratio | incentive_max | train | eq | `[[art:232eef87:run.data_train]]` | dangling |  |
| 83 | data_integrity | **Covariate ranges are plausible.** Note rate 2.285–6.384, o… | 0 | ratio | burnout_min | train | eq | `[[art:232eef87:run.data_train]]` | dangling |  |
| 84 | data_integrity | **Covariate ranges are plausible.** Note rate 2.285–6.384, o… | 9.32 | ratio | burnout_max | train | eq | `[[art:232eef87:run.data_train]]` | dangling |  |
| 85 | data_integrity | **Covariate ranges are plausible.** Note rate 2.285–6.384, o… | 999 | count |  |  | eq |  | unattributed |  |
| 86 | data_integrity | **Covariate ranges are plausible.** Note rate 2.285–6.384, o… | 9999 | ratio | sentinel |  | eq |  | unsupported |  |
| 87 | outcomes | \| train \| 36,013 \| 0.00852 \| 1.0 \| 1.0 \| 1.0 \| 1.10e-8 \| 9.1… | 36013 | count | n | train | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 88 | outcomes | \| train \| 36,013 \| 0.00852 \| 1.0 \| 1.0 \| 1.0 \| 1.10e-8 \| 9.1… | 0.00852 | ratio | event_rate | train | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 89 | outcomes | \| train \| 36,013 \| 0.00852 \| 1.0 \| 1.0 \| 1.0 \| 1.10e-8 \| 9.1… | 1.1e-08 | ratio | brier | train | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 90 | outcomes | \| train \| 36,013 \| 0.00852 \| 1.0 \| 1.0 \| 1.0 \| 1.10e-8 \| 9.1… | 9.13e-05 | ratio | logloss | train | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 91 | outcomes | \| train \| 36,013 \| 0.00852 \| 1.0 \| 1.0 \| 1.0 \| 1.10e-8 \| 9.1… | 2.867 | ratio | calibration_slope | train | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 92 | outcomes | \| test \| 15,382 \| 0.00806 \| 1.0 \| 1.0 \| 1.0 \| 1.01e-8 \| 9.04… | 15382 | count | n | test | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 93 | outcomes | \| test \| 15,382 \| 0.00806 \| 1.0 \| 1.0 \| 1.0 \| 1.01e-8 \| 9.04… | 0.00806 | ratio | event_rate | test | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 94 | outcomes | \| test \| 15,382 \| 0.00806 \| 1.0 \| 1.0 \| 1.0 \| 1.01e-8 \| 9.04… | 1.01e-08 | ratio | brier | test | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 95 | outcomes | \| test \| 15,382 \| 0.00806 \| 1.0 \| 1.0 \| 1.0 \| 1.01e-8 \| 9.04… | 9.04e-05 | ratio | logloss | test | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 96 | outcomes | \| test \| 15,382 \| 0.00806 \| 1.0 \| 1.0 \| 1.0 \| 1.01e-8 \| 9.04… | 2.833 | ratio | calibration_slope | test | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 97 | outcomes | \| out_of_time \| 12,257 \| 0.01795 \| 1.0 \| 1.0 \| 1.0 \| 1.38e-8… | 12257 | count | n | out_of_time | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 98 | outcomes | \| out_of_time \| 12,257 \| 0.01795 \| 1.0 \| 1.0 \| 1.0 \| 1.38e-8… | 0.01795 | ratio | event_rate | out_of_time | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 99 | outcomes | \| out_of_time \| 12,257 \| 0.01795 \| 1.0 \| 1.0 \| 1.0 \| 1.38e-8… | 1.38e-08 | ratio | brier | out_of_time | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 100 | outcomes | \| out_of_time \| 12,257 \| 0.01795 \| 1.0 \| 1.0 \| 1.0 \| 1.38e-8… | 9.06e-05 | ratio | logloss | out_of_time | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 101 | outcomes | \| out_of_time \| 12,257 \| 0.01795 \| 1.0 \| 1.0 \| 1.0 \| 1.38e-8… | 2.924 | ratio | calibration_slope | out_of_time | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 102 | outcomes | \| vintage_holdout \| 32,177 \| 0.00482 \| 1.0 \| 1.0 \| 1.0 \| 8.6… | 32177 | count | n | vintage_holdout | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 103 | outcomes | \| vintage_holdout \| 32,177 \| 0.00482 \| 1.0 \| 1.0 \| 1.0 \| 8.6… | 0.00482 | ratio | event_rate | vintage_holdout | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 104 | outcomes | \| vintage_holdout \| 32,177 \| 0.00482 \| 1.0 \| 1.0 \| 1.0 \| 8.6… | 8.65e-09 | ratio | brier | vintage_holdout | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 105 | outcomes | \| vintage_holdout \| 32,177 \| 0.00482 \| 1.0 \| 1.0 \| 1.0 \| 8.6… | 8.63e-05 | ratio | logloss | vintage_holdout | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 106 | outcomes | \| vintage_holdout \| 32,177 \| 0.00482 \| 1.0 \| 1.0 \| 1.0 \| 8.6… | 2.797 | ratio | calibration_slope | vintage_holdout | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 107 | outcomes | **Discrimination is perfect on every split, which is not a c… | 36013 | count | n | train | eq |  | unsupported |  |
| 108 | outcomes | **Discrimination is perfect on every split, which is not a c… | 0.00845 | ratio | brier | train | eq |  | unsupported |  |
| 109 | outcomes | **Discrimination is perfect on every split, which is not a c… | 0.049 | ratio | logloss | train | eq |  | unsupported |  |
| 110 | outcomes | **Discrimination is perfect on every split, which is not a c… | 1.1e-08 | ratio | brier | train | eq |  | unsupported |  |
| 111 | outcomes | **Discrimination is perfect on every split, which is not a c… | 770000 | ratio | brier | train | eq |  | unsupported |  |
| 112 | outcomes | **Discrimination is perfect on every split, which is not a c… | 540 | ratio | logloss | train | eq |  | unsupported |  |
| 113 | outcomes | **Discrimination is perfect on every split, which is not a c… | 1 | ratio |  |  | eq |  | unsupported |  |
| 114 | outcomes | **Calibration is materially wrong in slope on all four split… | 2.797 | ratio | calibration_slope |  | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 115 | outcomes | **Calibration is materially wrong in slope on all four split… | 2.924 | ratio | calibration_slope |  | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 116 | outcomes | **Calibration is materially wrong in slope on all four split… | 0.85 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 117 | outcomes | **Calibration is materially wrong in slope on all four split… | 1.15 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 118 | outcomes | **Calibration is materially wrong in slope on all four split… | 3 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 119 | outcomes | **Calibration is materially wrong in slope on all four split… | 2.9 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 120 | outcomes | **Calibration is materially wrong in slope on all four split… | 4 | count |  |  | eq |  | unsupported |  |
| 121 | outcomes | **Calibration in level is good but biased one way.** Mean pr… | 0.008607 | ratio | mean_predicted_probability | train | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 122 | outcomes | **Calibration in level is good but biased one way.** Mean pr… | 0.008525 | ratio | event_rate | train | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 123 | outcomes | **Calibration in level is good but biased one way.** Mean pr… | 0.008144 | ratio | mean_predicted_probability | test | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 124 | outcomes | **Calibration in level is good but biased one way.** Mean pr… | 0.008061 | ratio | event_rate | test | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 125 | outcomes | **Calibration in level is good but biased one way.** Mean pr… | 0.018019 | ratio | mean_predicted_probability | out_of_time | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 126 | outcomes | **Calibration in level is good but biased one way.** Mean pr… | 0.017949 | ratio | event_rate | out_of_time | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 127 | outcomes | **Calibration in level is good but biased one way.** Mean pr… | 0.004899 | ratio | mean_predicted_probability | vintage_holdout | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 128 | outcomes | **Calibration in level is good but biased one way.** Mean pr… | 0.004817 | ratio | event_rate | vintage_holdout | eq | `[[art:e8f6c83d:run.metrics]]` | dangling |  |
| 129 | outcomes | **Calibration in level is good but biased one way.** Mean pr… | 0.9 | percent | cpr | train | eq |  | unsupported |  |
| 130 | outcomes | **Calibration in level is good but biased one way.** Mean pr… | 0.4 | percent | cpr | out_of_time | eq |  | unsupported |  |
| 131 | outcomes | **Calibration in level is good but biased one way.** Mean pr… | 1.7 | percent | cpr | vintage_holdout | eq |  | unsupported |  |
| 132 | outcomes | **Calibration in level is good but biased one way.** Mean pr… | 4 | count |  |  | eq |  | unsupported |  |
| 133 | sensitivity | The one response curve that was available is the age dimensi… | 0 | months | baseline_hazard |  | eq | `[[art:f6c2df89:run.model_summary#baseline_hazard]]` | dangling |  |
| 134 | sensitivity | The one response curve that was available is the age dimensi… | 16 | months | baseline_hazard |  | eq | `[[art:f6c2df89:run.model_summary#baseline_hazard]]` | dangling |  |
| 135 | sensitivity | The one response curve that was available is the age dimensi… | 1 | percent | baseline_hazard |  | eq | `[[art:f6c2df89:run.model_summary#baseline_hazard]]` | dangling |  |
| 136 | sensitivity | The one response curve that was available is the age dimensi… | 17 | months | baseline_hazard |  | eq | `[[art:f6c2df89:run.model_summary#baseline_hazard]]` | dangling |  |
| 137 | sensitivity | The one response curve that was available is the age dimensi… | 53 | months |  |  | eq | `[[art:232eef87:run.data_train]]` | dangling |  |
| 138 | sensitivity | The one response curve that was available is the age dimensi… | 59 | months |  | train | eq | `[[art:232eef87:run.data_train]]` | dangling |  |
| 139 | sensitivity | The one response curve that was available is the age dimensi… | 360 | months |  |  | eq |  | unsupported |  |
| 140 | sensitivity | The one response curve that was available is the age dimensi… | 80 | percent |  |  | eq |  | unsupported |  |
| 141 | sensitivity | The one response curve that was available is the age dimensi… | 6 | ratio |  |  | eq |  | unsupported |  |
| 142 | sensitivity | A further structural sensitivity concern is the rate-family… | 11.986 | ratio |  | train | eq | `[[art:232eef87:run.data_train]]` | dangling |  |
| 143 | sensitivity | A further structural sensitivity concern is the rate-family… | 12.123 | ratio |  | train | eq | `[[art:232eef87:run.data_train]]` | dangling |  |
| 144 | sensitivity | A further structural sensitivity concern is the rate-family… | 7 | ratio |  |  | eq |  | unsupported |  |
| 145 | findings | \| 1 \| L1 \| high \| Perfect discrimination on all four splits… | 1 | ratio |  |  | eq |  | unsupported |  |
| 146 | findings | \| 2 \| T1 \| medium \| Declared leakage-free feature timing is… | 2 | ratio |  |  | eq |  | unsupported |  |
| 147 | findings | \| 3 \| L2 \| high \| Split loan counts exceed the loan universe… | 3 | ratio |  |  | eq |  | unsupported |  |
| 148 | findings | \| 4 \| C1 \| high \| Calibration slope ≈ 2.8–2.9 on every split… | 4 | ratio |  |  | eq |  | unsupported |  |
| 149 | findings | \| 4 \| C1 \| high \| Calibration slope ≈ 2.8–2.9 on every split… | 2.8 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 150 | findings | \| 4 \| C1 \| high \| Calibration slope ≈ 2.8–2.9 on every split… | 2.9 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 151 | findings | \| 5 \| S1 \| medium \| Event rate varies 3.5× across splits; no… | 5 | ratio |  |  | eq |  | unsupported |  |
| 152 | findings | \| 5 \| S1 \| medium \| Event rate varies 3.5× across splits; no… | 3.5 | ratio | event_rate |  | eq |  | unsupported |  |
| 153 | findings | \| 6 \| X1 \| medium \| Baseline hazard has no seasoning ramp an… | 6 | ratio |  |  | eq |  | unsupported |  |
| 154 | findings | \| 7 \| M1 \| low \| Collinear rate-family and balance features;… | 7 | ratio |  |  | eq |  | unsupported |  |
| 155 | findings | \| 8 \| D1 \| info \| Cross-split missingness comparison not pos… | 8 | ratio |  |  | eq |  | unsupported |  |
| 156 | findings | 1. **Do not deploy, and do not use the current results to su… | 1 | ratio |  |  | eq |  | unsupported |  |
| 157 | findings | 1. **Do not deploy, and do not use the current results to su… | 3 | ratio |  |  | eq |  | unsupported |  |
| 158 | findings | 2. **Isolate the leak.** Compute single-feature AUC for all… | 0.9 | ratio | auc |  | eq |  | unsupported |  |
| 159 | findings | 4. **Refit and re-evaluate from scratch after (2) and (3).**… | 2 | ratio |  |  | eq |  | unsupported |  |
| 160 | findings | 4. **Refit and re-evaluate from scratch after (2) and (3).**… | 3 | ratio |  |  | eq |  | unsupported |  |
| 161 | findings | 5. **Respecify the age effect.** Add knots in the 2–30 month… | 2 | months |  |  | eq |  | unsupported |  |
| 162 | findings | 5. **Respecify the age effect.** Add knots in the 2–30 month… | 30 | months |  |  | eq |  | unsupported |  |
| 163 | findings | 5. **Respecify the age effect.** Add knots in the 2–30 month… | 59 | months |  |  | eq |  | unsupported |  |
| 164 | findings | 7. **Produce collinearity diagnostics** (VIF and condition n… | 200 | bp |  |  | eq |  | unattributed |  |
| 165 | findings | 7. **Produce collinearity diagnostics** (VIF and condition n… | 200 | count |  |  | eq |  | unattributed |  |
| 166 | monitoring | - **Leakage tripwire.** Any monthly refresh reporting AUC ab… | 0.9 | ratio | auc |  | eq |  | unsupported |  |
| 167 | monitoring | - **Monthly actual-vs-predicted CPR** at portfolio level and… | 10 | percent |  |  | eq |  | unsupported |  |
| 168 | monitoring | - **Quarterly recalibration check.** Refit the calibration s… | 0.85 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 169 | monitoring | - **Quarterly recalibration check.** Refit the calibration s… | 1.15 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 170 | monitoring | - **Feature and score PSI monthly** against the training ref… | 0.1 | ratio | psi |  | eq |  | unsupported |  |
| 171 | monitoring | - **Feature and score PSI monthly** against the training ref… | 0.25 | ratio | psi |  | eq |  | unsupported |  |
| 172 | monitoring | - **Age-support monitor.** Alert when the weighted-average l… | 59 | months |  |  | eq |  | unsupported |  |
| 173 | monitoring | - **Rate-regime monitor.** Track the distribution of `incent… | 3.5 | ratio |  |  | eq |  | unsupported |  |

## Appendix B — Artifact index

The store holds 19 artifacts; the 12 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `run.data_out_of_time` | `32b32e79` | table | table, 12257 rows | the subject's data_out_of_time.csv |
| `run.data_test` | `057dd4f6` | table | table, 15382 rows | the subject's data_test.csv |
| `run.data_train` | `232eef87` | table | table, 36013 rows | the subject's data_train.csv |
| `run.data_vintage_holdout` | `eefd735d` | table | table, 32177 rows | the subject's data_vintage_holdout.csv |
| `run.features` | `61276a96` | json | json | the subject's features.json |
| `run.metrics` | `e8f6c83d` | json | json | the subject's metrics.json |
| `run.model_summary` | `f6c2df89` | json | json | the subject's model_summary.json |
| `run.predictions_out_of_time` | `2fb38ea7` | table | table, 12257 rows | the subject's predictions_out_of_time.csv |
| `run.predictions_train` | `48acd876` | table | table, 36013 rows | the subject's predictions_train.csv |
| `run.predictions_vintage_holdout` | `019a88af` | table | table, 32177 rows | the subject's predictions_vintage_holdout.csv |
| `run.projection` | `7d3ba32d` | json | json | the subject's projection.json |
| `run.splits` | `dca79f2f` | json | json | the subject's splits.json |

## Appendix C — Run trace summary

| quantity | value |
|---|---|
| tool calls | 1 (run_model 1) |
| plan steps (bounded loop) | 0 |
| LLM calls | 8 (plain_llm 1, extract 7) |
| re-asks | 0 |
| repair rounds | 0 |
| tokens in / out | 65,039 / 50,561 |
| notional cost (USD) | 1.9036 |
| wall-clock (s) | 584.68 |
| subject run (s) | 2.89 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | msr_prepayment-plain_llm-20260918T213037Z-986f3824 |

## Appendix D — Not checked

| item | reason |
|---|---|
| `check_stability` (R1) | this configuration runs no checks |
| `run_scenarios` (X1) | this configuration runs no checks |
| developer claims (T1, claim channel) | `plain_llm` runs no check over `package.yaml`'s declared claims |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
| every check of spec 3.7 but `run_model` | `plain_llm` runs the subject and one model call, by design |
