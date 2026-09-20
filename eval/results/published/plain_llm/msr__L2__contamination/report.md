---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: msr_prepayment
version: "1.0"
model_type: discrete_time_hazard
configuration: plain_llm
model: claude-opus-5[1m]
run_id: msr_prepayment-plain_llm-20260918T214026Z-986f3824
data_mode: synthetic
synthetic_n: 2000
grounding_precision_pre: 0.0000
grounding_precision_post: 0.0000
n_claims: 171
n_findings_by_severity: {high: 1, medium: 4, low: 2, info: 1}
generated: "2026-09-18T21:40:26Z"
illustrative: false
---

# Validation report — `msr_prepayment` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `msr_prepayment` v1.0 | `plain_llm` | claude-opus-5[1m] | synthetic, n = 2000 | 0.0000 → 0.0000 | 1 / 4 / 2 / 1 |
<!-- quaestor:renderer:end -->

This review covers version 1.0 of the `msr_prepayment` package, a discrete-time hazard model estimated on a loan-month panel with a binary `prepaid` outcome. The model produces a single-month mortality (SMM) hazard per loan-month, which is annualized to CPR and, per the presence of [[art:d4375126:run.projection]], carried into a projection used for MSR valuation.

The following artifacts were available and were used: [[art:3e60c932:run.metrics]], [[art:3f2870ab:run.splits]], [[art:61276a96:run.features]], [[art:8e6d6768:run.model_summary]], the raw profile of the training split, and the split and prediction tables [[art:74d4436f:run.data_train]], [[art:f0ac9fe8:run.data_test]], [[art:940d14da:run.data_vintage_holdout]], [[art:7ddcc721:run.data_out_of_time]], [[art:d02960f5:run.predictions_train]], [[art:c1dbcaa3:run.predictions_test]], [[art:b7f67f98:run.predictions_vintage_holdout]], [[art:ce5d5d56:run.predictions_out_of_time]]. The run completed within its cap ([[art:77e73bee:run.duration_s]] against [[art:2ad8d1a5:runtime.max_seconds]]) and no execution failure is indicated by [[art:5c222bcc:run.status]]; no R0-class finding is raised.

Three scope limitations should be recorded before the conclusions are read. First, the covariate coefficient vector is not present in the portion of [[art:8e6d6768:run.model_summary]] made available — only `age_spline_knots` and the tabulated `baseline_hazard` — so coefficient signs, magnitudes and standard errors could not be reviewed, and no regime-partitioned refit exists to test coefficient stability (R1). Second, no developer-declared performance thresholds, acceptance criteria, or model documentation exist anywhere in the store, so there is no declared claim to test and no T1-class finding can be raised or cleared. Third, no challenger model was run, so effective challenge was not performed.

**Overall conclusion.** Discrimination is adequate and stable, and the model's internal arithmetic is self-consistent. Calibration is not acceptable for a valuation use. The model systematically over-predicts prepayment in every split, and the over-prediction grows as the evaluation population moves away from the training regime, reaching +⟦unverified: 22%⟧ on the vintage holdout. Because CPR feeds MSR fair value directly, a directional level bias of this size is a material weakness. The model is fit for rank-ordering and for relative-value work as it stands; it should not be used to produce MSR fair value until it is recalibrated and the projection is independently reviewed.

## 2. Conceptual soundness

The discrete-time hazard specification is appropriate for the problem. Prepayment is a competing-risk, time-to-event process observed monthly; a loan-month panel with a period-level binary outcome and an age-dependent baseline is the standard formulation, and it handles right-censoring and time-varying covariates natively. The annualization is correct: the reported CPR values reconcile exactly to `1 - (1 - SMM)^12`. For the training split, a mean predicted SMM of ⟦unverified: 0.0086936⟧ implies a CPR of ⟦unverified: 0.099477⟧, which is the reported `cpr_predicted` to six decimal places; the same identity holds on test, vintage holdout and out-of-time ([[art:3e60c932:run.metrics]]). The observed-side CPRs reconcile to the split event rates in [[art:3f2870ab:run.splits]] the same way. This is a meaningful check and it passes.

The covariate set in [[art:61276a96:run.features]] is economically sensible and covers the four drivers a prepayment model is expected to contain: refinance incentive (`incentive`, `sato`, `note_rate`, `rate_change_12m`), seasoning (`loan_age` with a spline, plus the tabulated baseline), burnout (`burnout`), and borrower/collateral characteristics (`credit_score`, `orig_ltv`, `orig_upb_log`, `bom_balance_log`). Seasonality is entered as a sine/cosine pair, whose sample standard deviations of ⟦unverified: 0.705⟧ and ⟦unverified: 0.709⟧ are the expected `1/sqrt(2)` for even month coverage.

Feature timing is declared cleanly and no leakage is indicated by the timing metadata. [[art:61276a96:run.features]] reports `after_outcome: 0` and `during_period: 0`, with five features at origination and seven known before period start. The counts reconcile to the twelve items listed. `bom_balance_log` being a beginning-of-month balance is consistent with a `before_period_start` declaration. No single feature is reported as achieving pathological standalone discrimination, and the model-level AUC of ⟦unverified: 0.79⟧ is in the normal range for a monthly prepayment hazard — high enough to be useful, not so high as to suggest the outcome has been reconstructed from the inputs. No L1 finding is raised.

Two conceptual concerns are raised. The first is the treatment of loan age beyond the support of the data. The training panel contains loan ages from ⟦unverified: 0⟧ to ⟦unverified: 59⟧ months and the age spline's outermost knot is at ⟦unverified: 53⟧ ([[art:8e6d6768:run.model_summary#age_spline_knots]]). The tabulated baseline hazard nonetheless extends past age ⟦unverified: 100⟧ and, given the MSR use, must be evaluated out to ⟦unverified: 360⟧ months in projection. Everything beyond roughly age ⟦unverified: 55⟧ is spline extrapolation, not estimation. The extrapolated shape — a peak of ⟦unverified: 0.003425⟧ at age ⟦unverified: 40⟧ followed by an uninterrupted decay to ⟦unverified: 0.001801⟧ by age ⟦unverified: 101⟧ and continuing downward — is the behaviour a constrained spline produces outside its knots, not a behaviour the data can support. An economically motivated seasoning ramp typically plateaus rather than decaying without limit, and a decaying tail systematically extends projected MSR life. This is recorded as finding X1-⟦unverified: 01⟧.

The second concern is structural collinearity in the rate block. `note_rate`, `sato`, `incentive` and `rate_change_12m` are all linear functions of a note rate and a market rate at two dates; `incentive` minus `sato` is, up to sign and scaling, the change in market rate since origination, which makes the block close to rank-deficient by construction. No VIF, condition number, or correlation matrix appears anywhere in the store. Coefficients on individual rate terms should therefore not be interpreted individually, and the model's response to a rate shock may be unstable even where its fitted values are not. This is recorded as finding M1-⟦unverified: 01⟧.

## 3. Data integrity and drift

The training split contains ⟦unverified: 36,474⟧ loan-months across ⟦unverified: 1,395⟧ loans over periods ⟦unverified: 201402⟧ to ⟦unverified: 201912⟧. Row counts reconcile across [[art:3f2870ab:run.splits]], [[art:3e60c932:run.metrics]] and the raw profile, and the profile's `prepaid` mean of ⟦unverified: 0.008608872⟧ matches the declared training event rate exactly. The four `rows_hash` values in [[art:3f2870ab:run.splits]] are distinct.

Covariate ranges are plausible and free of sentinel values: `credit_score` spans ⟦unverified: 620⟧–⟦unverified: 820,⟧ `orig_ltv` ⟦unverified: 31⟧–⟦unverified: 97,⟧ `note_rate` ⟦unverified: 2.285⟧–⟦unverified: 6.476⟧, `orig_upb_log` ⟦unverified: 10.65⟧–⟦unverified: 13.54⟧. There are no negative balances, no ⟦unverified: 999⟧-type codes, and no out-of-range LTVs.

Two integrity issues are recorded. First, two features the model declares as inputs — `bom_balance_log` and `rate_change_12m` — do not appear among the thirteen columns of the raw training profile, which lists `loan_id`, `period`, `note_rate`, `orig_ltv`, `credit_score`, `orig_upb_log`, `sato`, `loan_age`, `incentive`, `burnout`, `season_sin`, `season_cos` and `prepaid`. Either these are derived downstream of the profiled table, in which case their construction and lineage are undocumented and unprofiled, or the feature manifest and the estimation data disagree. Either way, two of twelve model inputs have no distributional evidence at all. Second, every column in the profile reports exactly zero missingness, and no profile of the test, vintage-holdout or out-of-time splits exists. Zero missingness across an entire servicing panel — including `credit_score`, which is missing in real agency data — indicates either a synthetic panel or silent upstream imputation, neither of which is documented; and with no non-training profile, the cross-split missingness comparison that a D1 test requires cannot be performed. These are recorded jointly as finding D1-⟦unverified: 01⟧.

On drift, the evidence is indirect but strong. The realized monthly prepayment rate differs by a factor of ⟦unverified: 3.7⟧ across the evaluation populations: ⟦unverified: 0.004817⟧ on the vintage holdout, ⟦unverified: 0.008609⟧ on train, ⟦unverified: 0.008061⟧ on test, and ⟦unverified: 0.017949⟧ out of time. In CPR terms the book moves from ⟦unverified: 5.6%⟧ to ⟦unverified: 19.5%⟧. The score distribution moves with it — mean predicted SMM rises from ⟦unverified: 0.008694⟧ in train to ⟦unverified: 0.019451⟧ out of time — which confirms that the covariates are tracking the regime shift rather than the model being blind to it. But no population stability index, on either features or scores, was computed for any split, so the magnitude of the input drift is unquantified and there is no stored baseline against which future production drift can be measured. Given that the training window closes in December ⟦unverified: 2019⟧ and the out-of-time split evidently sits in a materially faster prepayment regime, this is a gap that should be closed before deployment. Recorded as finding S1-⟦unverified: 01⟧.

The splits also differ structurally in a way that complicates comparison: rows per loan are ⟦unverified: 26.1⟧ in train, ⟦unverified: 38.5⟧ in test, ⟦unverified: 48.3⟧ in the vintage holdout and ⟦unverified: 23.8⟧ out of time. The vintage holdout carries nearly as many rows as train from less than half the loans, meaning it is dominated by long, well-seasoned, largely burned-out histories. That is a defensible holdout design, but it means the vintage-holdout metrics are not drawn from the same observation-window design as train, and part of the calibration gap discussed in section 4 may be a seasoning effect rather than a vintage effect.

## 4. Outcomes analysis

| Split | n | Loans | Event rate | Mean pred. | AUC | Gini | KS | Brier | LogLoss | Cal. slope | CPR actual | CPR pred. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train | ⟦unverified: 36,474⟧ | ⟦unverified: 1,395⟧ | ⟦unverified: 0.008609⟧ | ⟦unverified: 0.008694⟧ | ⟦unverified: 0.7888⟧ | ⟦unverified: 0.5775⟧ | ⟦unverified: 0.4561⟧ | ⟦unverified: 0.008396⟧ | ⟦unverified: 0.04442⟧ | ⟦unverified: 0.996⟧ | ⟦unverified: 9.86%⟧ | ⟦unverified: 9.95%⟧ |
| test | ⟦unverified: 15,382⟧ | ⟦unverified: 400⟧ | ⟦unverified: 0.008061⟧ | ⟦unverified: 0.008364⟧ | ⟦unverified: 0.7759⟧ | ⟦unverified: 0.5519⟧ | ⟦unverified: 0.4195⟧ | ⟦unverified: 0.007893⟧ | ⟦unverified: 0.04261⟧ | ⟦unverified: 0.939⟧ | ⟦unverified: 9.26%⟧ | ⟦unverified: 9.59%⟧ |
| vintage_holdout | ⟦unverified: 32,177⟧ | ⟦unverified: 666⟧ | ⟦unverified: 0.004817⟧ | ⟦unverified: 0.005914⟧ | ⟦unverified: 0.7722⟧ | ⟦unverified: 0.5443⟧ | ⟦unverified: 0.4492⟧ | ⟦unverified: 0.004765⟧ | ⟦unverified: 0.02814⟧ | ⟦unverified: 0.836⟧ | ⟦unverified: 5.63%⟧ | ⟦unverified: 6.87%⟧ |
| out_of_time | ⟦unverified: 12,257⟧ | ⟦unverified: 515⟧ | ⟦unverified: 0.017949⟧ | ⟦unverified: 0.019451⟧ | ⟦unverified: 0.7871⟧ | ⟦unverified: 0.5742⟧ | ⟦unverified: 0.4422⟧ | ⟦unverified: 0.017122⟧ | ⟦unverified: 0.07960⟧ | ⟦unverified: 1.008⟧ | ⟦unverified: 19.53%⟧ | ⟦unverified: 21.00%⟧ |

**Discrimination is adequate and stable.** AUC ranges from ⟦unverified: 0.7722⟧ to ⟦unverified: 0.7888⟧ across all four populations. The train-to-test gap is ⟦unverified: 0.0128⟧ and the train-to-vintage-holdout gap is ⟦unverified: 0.0166⟧; out of time, AUC is essentially unchanged from train at ⟦unverified: 0.7871⟧. These gaps are well inside any conventional degradation threshold, and KS is stable in a ⟦unverified: 0.42⟧–⟦unverified: 0.46⟧ band. There is no evidence of overfitting in the ranking dimension and no O1 finding is raised. Brier and log-loss differences across splits are driven almost entirely by differences in base rate and carry no independent signal.

**Calibration is the problem, and it is directional.** The model over-predicts in all four splits, without exception, and the size of the over-prediction increases monotonically with distance from the training regime: +1.0% in train (⟦unverified: 0.008694⟧ vs ⟦unverified: 0.008609⟧), +⟦unverified: 3.8%⟧ in test (⟦unverified: 0.008364⟧ vs ⟦unverified: 0.008061⟧), +⟦unverified: 8.4%⟧ out of time (⟦unverified: 0.019451⟧ vs ⟦unverified: 0.017949⟧), and +⟦unverified: 22.8%⟧ on the vintage holdout (⟦unverified: 0.005914⟧ vs ⟦unverified: 0.004817⟧). In the units that matter for valuation, the vintage holdout is predicted at ⟦unverified: 6.87⟧ CPR against ⟦unverified: 5.63⟧ realized — ⟦unverified: 124⟧ basis points of CPR, ⟦unverified: 22%⟧ in relative terms — and the out-of-time split at ⟦unverified: 21.00⟧ against ⟦unverified: 19.53⟧, a further ⟦unverified: 146⟧ basis points. A bias that never changes sign across four independent populations is not sampling noise; it is a level error in the fitted hazard.

The calibration slope tells the same story from the other direction, declining from ⟦unverified: 0.996⟧ in train to ⟦unverified: 0.939⟧ in test and ⟦unverified: 0.836⟧ on the vintage holdout. A slope of ⟦unverified: 0.836⟧ means predicted log-odds are roughly ⟦unverified: 16%⟧ too dispersed relative to realized outcomes on that population: the model is not only too high on average there, it is too confident in the spread of its rankings. Notably, the out-of-time slope of ⟦unverified: 1.008⟧ is fine, so the slope deterioration is specific to the seasoned/burned-out vintage-holdout population rather than being a general property of the fit. The most likely explanation, consistent with the rows-per-loan asymmetry noted in section 3, is that burnout is under-captured: the model does not decay the hazard fast enough for loans that have already passed through refinance opportunities without acting.

For MSR use, the direction is conservative for asset value — over-predicting CPR shortens projected life and understates MSR fair value — but a ⟦unverified: 22%⟧ relative CPR error is material regardless of sign, and the same bias applied to a hedging or amortization decision is not conservative at all. These are recorded as findings C1-⟦unverified: 01⟧ (high) and C1-⟦unverified: 02⟧ (medium).

## 5. Sensitivity and scenario analysis

This section could not be completed to a standard sufficient to support the model's intended use, and that is itself the principal result.

[[art:d4375126:run.projection]] exists in the store, but its contents were not available for this review, so the projected CPR vector, the projected MSR value, and the assumptions carrying the monthly hazard out to the end of the amortization schedule could not be inspected. No rate-shock grid, no S-curve (predicted CPR against refinance incentive), and no value-versus-rate table appears anywhere in the store. A prepayment model used for MSR valuation must demonstrate, at minimum, that predicted CPR rises monotonically with refinance incentive across the full plausible incentive range, that it saturates rather than diverging at high incentive, and that MSR value falls monotonically as rates fall. None of these can be confirmed from the available artifacts. I am therefore not asserting that the value curve is non-monotone or wrong-signed — I am recording that it is untested.

What can be assessed is the sensitivity structure the fitted model implies. Two features of it warrant attention. The baseline hazard is tabulated on a fine age grid and is smooth and single-peaked within the estimated range, rising from ⟦unverified: 0.000871⟧ at age ⟦unverified: 0⟧ to a maximum of ⟦unverified: 0.003425⟧ at age ⟦unverified: 40⟧ — a plausible seasoning ramp, and a reassuring shape in the region the data actually covers. Beyond the data's support at age ⟦unverified: 59,⟧ however, the curve decays continuously with no plateau, and by age ⟦unverified: 101⟧ it has fallen to ⟦unverified: 0.001801⟧, roughly half the peak. Because MSR valuation discounts cash flows over the whole remaining term, the extrapolated tail materially drives the answer, and it is the least evidenced part of the model. This is finding X1-⟦unverified: 01⟧.

Separately, the collinearity noted in section 2 bears directly on scenario work. The rate-shock response of this model is the sum of the `note_rate`, `sato`, `incentive` and `rate_change_12m` coefficients along whatever path the shock traces through those four correlated inputs. When the block is near rank-deficient, that sum can be stable while the individual coefficients are not, and a scenario generator that perturbs one rate input without consistently perturbing the others will produce responses the fit does not support. Any scenario framework built on this model must shock the underlying market rate and rebuild all four derived features from it, not shock `incentive` in isolation.

## 6. Findings and recommendations

Eight findings are recorded: one high, four medium, two low, one informational.

- **C1-⟦unverified: 01⟧ (high)** — Vintage-holdout calibration failure: slope ⟦unverified: 0.836⟧, predicted CPR ⟦unverified: 22%⟧ above realized.
- **C1-⟦unverified: 02⟧ (medium)** — One-directional over-prediction in all four splits, growing with regime distance.
- **X1-⟦unverified: 01⟧ (medium)** — Baseline hazard extrapolated far beyond observed loan age; projection not reviewable.
- **D1-⟦unverified: 01⟧ (medium)** — Two declared features absent from the data profile; unexplained zero missingness; no non-training profile.
- **S1-⟦unverified: 01⟧ (medium)** — Large realized-rate and score shift across splits with no PSI computed and no stored drift baseline.
- **M1-⟦unverified: 01⟧ (low)** — Structural collinearity in the rate block, with no VIF or condition number produced.
- **L2-⟦unverified: 01⟧ (low)** — Split independence asserted but not demonstrated; loan-count arithmetic leaves loan sharing open.
- **E1-⟦unverified: 01⟧ (info)** — No challenger model; effective challenge not performed.

**Required before production use.**

1. Recalibrate. Refit or apply an explicit recalibration (intercept plus slope) so that mean predicted SMM matches realized on each holdout within a tight tolerance and the calibration slope returns to a ⟦unverified: 0.9⟧–⟦unverified: 1.1⟧ band. Recalibration must be validated on a population not used to fit the adjustment.
2. Diagnose the vintage-holdout bias rather than only correcting it. Decompose the calibration error by loan age bucket, by incentive bucket, and by burnout bucket. The combination of a slope of ⟦unverified: 0.836⟧, the highest rows-per-loan count of any split, and the lowest event rate points specifically at under-modelled burnout; if that is confirmed, the burnout term should be respecified rather than the output shifted.
3. Produce and review the projection. Publish the S-curve, a rate-shock grid spanning at least +/⟦unverified: -200⟧bp, and the resulting MSR value curve, and confirm monotonicity and correct sign in both.
4. Constrain or justify the age extrapolation. Either impose a plateau on the baseline hazard beyond the last knot, extend the estimation panel to cover older loans, or document and bound the valuation impact of the current extrapolated tail.
5. Close the data gaps. Profile `bom_balance_log` and `rate_change_12m`, publish profiles for all four splits, and document the source of the panel's zero missingness — including any imputation applied.
6. Compute and store collinearity and stability diagnostics: VIF and condition number for the design matrix, and PSI for every feature and for the score, with the training distribution stored as the production baseline.
7. Demonstrate split independence. Publish per-split distinct `loan_id` sets and their pairwise intersections.
8. Run a challenger. A logistic benchmark on the same panel and, preferably, a published agency-style prepayment model would establish whether the ⟦unverified: 0.79⟧ AUC and the calibration behaviour are the best this data supports.

**Not required but recommended.** Add confidence intervals to the reported metrics — the out-of-time split has only ⟦unverified: 12,257⟧ rows and ⟦unverified: 220⟧ events, and several of the comparisons above are being made on that base. Record developer-declared acceptance thresholds in the artifact store so that future validations have a stated claim to test.

### F-001 · C1 calibration · severity **high**

On the vintage_holdout split the calibration slope is 0.8363, outside any conventional acceptance band for a valuation model, and the level bias is large: mean predicted SMM is 0.0059139 against a realized event rate of 0.0048171, an over-prediction of 22.8%. In valuation units the model predicts 6.87 CPR against 5.63 realized, an overstatement of 124 basis points of CPR, or 22% in relative terms. Discrimination on this same split is essentially intact (AUC 0.7722, KS 0.4492), so the failure is one of level and scale, not of rank-ordering: the model places loans in the right order but assigns hazards that are too high and too dispersed. The vintage_holdout population is the most seasoned of the four (48.3 rows per loan against 26.1 in train, from 666 loans and 32,177 rows) and has the lowest realized event rate, which points at under-modelled burnout as the mechanism -- the fitted hazard does not decay fast enough for loans that have already passed through refinance opportunities without acting. Because CPR is a direct input to MSR fair value, a 22% CPR error propagates into the valuation; the direction understates MSR value, which is conservative for the asset but is not conservative for hedging or amortization decisions built on the same projection. The model should not be used to produce MSR fair value until it is recalibrated and the burnout specification is re-examined, with the recalibration validated out of sample.

### F-002 · C1 calibration · severity **medium**

The model over-predicts prepayment in every evaluated population, without a single exception, and the magnitude increases monotonically as the evaluation population moves away from the training regime: train +1.0% (0.0086936 predicted against 0.0086089 realized), test +3.8% (0.0083640 against 0.0080614), out_of_time +8.4% (0.0194506 against 0.0179489), and vintage_holdout +22.8% (0.0059139 against 0.0048171). The calibration slope degrades in parallel on the in-regime splits, from 0.9958 in train to 0.9390 in test to 0.8363 on the vintage holdout. In CPR terms the out-of-time split alone is overstated by 146 basis points (21.00% predicted against 19.53% realized). A bias that never changes sign across four independent populations, and that scales with regime distance, is a structural level error in the fitted hazard rather than sampling variation. This finding is recorded separately from the vintage-holdout failure because the remediation differs: the vintage-holdout gap may be a specification problem in the burnout term, whereas the pervasive positive bias indicates the intercept/baseline level itself is high and that the error will grow, not shrink, as the production population drifts further from the December 2019 end of the training window. Remediation should include an explicit level recalibration plus a decomposition of calibration error by loan age, incentive and burnout bucket.

### F-003 · X1 scenario analysis · severity **medium**

The training panel contains loan ages from 0 to 59 months and the outermost age spline knot sits at 53 (age_spline_knots [1, 10, 19, 31, 53]). The tabulated baseline hazard in run.model_summary nonetheless extends beyond loan age 101, and the MSR use requires evaluation out to the full remaining amortization term. Everything beyond roughly age 55 is therefore spline extrapolation rather than estimation. Within the supported range the curve is plausible: it rises smoothly from 0.0008706 at age 0 to a peak of 0.0034253 at age 40, a recognisable seasoning ramp. Beyond the data, however, it decays continuously and without plateau, reaching 0.0018010 by age 101 -- roughly half the peak -- which is the behaviour a constrained spline produces outside its knots rather than a behaviour the data supports. An economically motivated seasoning curve typically plateaus; a monotonically decaying tail systematically lengthens projected MSR life and inflates projected value in exactly the region where the evidence is weakest. Compounding this, run.projection exists in the store but its contents were not available for review, and no S-curve, rate-shock grid, or value-versus-rate table appears anywhere in the artifact set. I am not asserting that the realized value curve is non-monotone or wrong-signed; I am recording that the extrapolated hazard tail is unsupported by data and that the scenario evidence needed to confirm the curve's shape and sign does not exist in reviewable form. Remediation: impose a plateau beyond the last knot or extend the estimation panel to older loans, and publish the S-curve and a +/-200bp value grid for independent review.

### F-004 · D1 data integrity · severity **medium**

run.features declares twelve inputs, but two of them -- bom_balance_log and rate_change_12m -- do not appear among the thirteen columns of the raw training profile, which contains only loan_id, period, note_rate, orig_ltv, credit_score, orig_upb_log, sato, loan_age, incentive, burnout, season_sin, season_cos and prepaid. Either these two features are derived downstream of the profiled table, in which case their construction and lineage are undocumented and their distributions are entirely unevidenced, or the feature manifest and the estimation data disagree. Two of twelve model inputs therefore have no distributional evidence of any kind, including no range checks and no missingness measurement. Separately, every profiled column reports exactly zero missingness. A servicing panel with no missing credit_score is not characteristic of real agency data and indicates either a synthetic panel or silent upstream imputation; neither is documented, and if imputation is occurring it is invisible to this review. Finally, profiles exist only for the training split: no comparable profile was produced for test, vintage_holdout or out_of_time, so the cross-split missingness and distribution comparison that this class of test requires cannot be performed at all. Remediation: profile all four splits on all twelve model features, document the derivation of bom_balance_log and rate_change_12m, and state explicitly what imputation, if any, precedes the profiled table.

### F-005 · S1 population drift · severity **medium**

The realized monthly prepayment rate differs by a factor of 3.7 across the four evaluation populations: 0.0048171 on vintage_holdout, 0.0086089 on train, 0.0080614 on test and 0.0179489 on out_of_time -- from 5.6 CPR to 19.5 CPR. The score distribution shifts with it, mean predicted SMM rising 2.2x from 0.0086936 in train to 0.0194506 out of time, which confirms the covariates are tracking a genuine regime change rather than the model being blind to it. Despite a shift of this magnitude, no population stability index was computed for any feature or for the score, on any split, and no baseline distribution was stored against which future production drift could be measured. The training window closes at period 201912, so the production population will by construction sit outside the estimation regime, and the calibration bias documented in C1-02 is already larger out of time (+8.4%) than in sample (+1.0%) -- meaning drift and calibration failure are coupled here, not independent. The severity is medium rather than high because the shift is visible and the model's discrimination survives it (out-of-time AUC 0.7871, essentially equal to train); the defect is the absence of the measurement and of the baseline, which leaves the model without any drift control at deployment. Remediation: compute PSI for all twelve features and for the score, store the training distribution as the production baseline, and set 0.10/0.25 action levels with the rate-driven features monitored on every refinance-wave transition.

### F-006 · M1 collinearity · severity **low**

Four of the twelve inputs -- note_rate, sato, incentive and rate_change_12m -- are all linear functions of a note rate and a market rate observed at two dates. sato is the spread of the note rate over the market rate at origination; incentive is the spread over the current market rate; their difference is, up to sign and scaling, the change in market rate since origination, which rate_change_12m partly measures again over a twelve-month window. The block is therefore close to rank-deficient by construction. No VIF, condition number, or correlation matrix appears anywhere in the artifact store, so the degree of the resulting instability is unmeasured. The severity is low because near-collinearity does not bias fitted values and the model's discrimination is stable across four populations, so the predictive use is not directly impaired. It matters for two secondary uses. First, the individual coefficients on the rate terms should not be interpreted or attributed economically, and no coefficient-level review is possible in any case since the covariate coefficients are not present in the available portion of run.model_summary. Second, and more practically, any scenario generator must shock the underlying market rate and rebuild all four derived features consistently from it; shocking incentive in isolation will trace a path the fit does not support and can produce a rate response of the wrong magnitude or sign. Remediation: publish VIF and the design-matrix condition number, and document the scenario generator's feature-rebuild logic.

### F-007 · L2 contamination · severity **low**

run.splits reports distinct rows_hash values for the four splits, which establishes that the split tables differ but says nothing about whether the same loans appear in more than one of them -- and in a loan-month panel, loan-level sharing is the contamination that matters, because rows from the same loan are strongly correlated and their presence on both sides of a split inflates apparent holdout performance. The declared loan counts sum to 2,976 (1,395 train, 400 test, 666 vintage_holdout, 515 out_of_time), while the maximum loan_id observed in the training profile is 2,461. If the loan identifier space is global and does not extend past the training maximum, then at least 515 loans are assigned to two splits; if instead other splits carry identifiers above 2,461, the splits may be entirely disjoint. The available artifacts do not resolve which is the case, so this is recorded as an unresolved control gap at low severity rather than as a confirmed contamination. Note that an out-of-time split reusing training loans at later periods is a legitimate and common design, but a vintage holdout sharing loans with train is not, and the two cannot be distinguished from what is published. The supporting evidence is weakly consistent with block structure: the row-weighted mean loan_id in train is 581.7 against a maximum of 2,461, far below the ~1,231 that random assignment over that range would give, indicating training loans are concentrated at low identifiers. Remediation: publish the distinct loan_id set size per split and all six pairwise intersection counts.

### F-008 · E1 effective challenge · severity **info**

The artifact store contains exactly one model run and no challenger, benchmark, or alternative specification of any kind. There is consequently no evidence that a challenger outperforms the champion -- and equally no evidence that it does not. This is recorded as informational rather than as a substantive defect precisely because nothing was beaten: the class cannot be tested at all in the absence of a comparison model. It is nonetheless a gap in the validation package, since the central question the champion's 0.79 AUC and its systematic over-prediction raise is whether a different specification would do better on the same panel. Two comparisons would be informative and cheap: a plain logistic regression on the same twelve features and the same splits, which would establish how much the hazard structure and the age spline are contributing over a flat specification; and a published agency-style prepayment benchmark, which would establish whether the calibration bias documented in C1-01 and C1-02 is specific to this fit or is a property of the data. No remediation is attached to this finding beyond running those comparisons before the next validation cycle. Related to this, no developer-declared acceptance thresholds or model documentation exist in the store either, so no declared claim could be tested and no threshold-breach finding can be raised or cleared.

Candidates raised and not promoted: none.

### Open items

No open item was recorded for this validation.

## 7. Ongoing monitoring recommendations

**Monthly.** Report actual versus predicted CPR at the portfolio level and by the primary MSR strata (vintage, note rate band, loan age bucket, servicer), as an actual-to-expected ratio. Given the bias documented in section 4, the A/E ratio is the primary control: amber at a sustained deviation beyond +/⟦unverified: -10%⟧, red beyond +/⟦unverified: -20%⟧ or at any three consecutive months of same-signed deviation beyond ⟦unverified: 10%⟧. Same-signed persistence should escalate even inside the band, because the defect found here is directional rather than noisy.

**Monthly.** Track the mean predicted SMM and the realized event rate side by side, and track the score distribution's mean and dispersion against the stored training baseline.

**Quarterly.** Compute PSI for every model feature and for the score against the training baseline, with the usual ⟦unverified: 0.10⟧ and ⟦unverified: 0.25⟧ action levels. Given that the training window ends in December ⟦unverified: 2019⟧ and the out-of-time evidence already shows a ⟦unverified: 2.2⟧x shift in mean predicted hazard, the rate-driven features (`incentive`, `sato`, `rate_change_12m`) should be expected to breach first and should be reviewed on every refinance-wave transition regardless of the calendar.

**Quarterly.** Recompute AUC, KS and the calibration slope on the trailing twelve months of realized performance. Discrimination should be alerted below an AUC of ⟦unverified: 0.72⟧; the calibration slope should be alerted outside ⟦unverified: 0.85⟧–⟦unverified: 1.15⟧ and escalated outside ⟦unverified: 0.80⟧–⟦unverified: 1.20⟧.

**Quarterly.** Back-test the prior quarter's projection against realized runoff, reporting the CPR error and the implied MSR value error, cumulatively and by stratum. This is the only control that tests the extrapolated portion of the baseline hazard, and it is the one that matters most for the valuation use.

**Annually, or on trigger.** Refit the baseline hazard and re-estimate the model on a panel extended through the most recent data, and re-run the challenger comparison. Triggers for an off-cycle refit: a red A/E breach, a feature PSI above ⟦unverified: 0.25⟧, a calibration slope outside ⟦unverified: 0.80⟧–⟦unverified: 1.20⟧, or a sustained market rate move beyond ⟦unverified: 150⟧bp from the level prevailing at the last refit.

## Appendix A — Claims

Grounding precision 0.0000 before repair (0 of 171 claims verified; 152 unsupported, 4 dangling, 15 unattributed) and 0.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 0/1; conceptual_soundness 0/17; data_integrity 0/30; outcomes 0/82; sensitivity 0/8; findings 0/17; monitoring 0/16.

Developer claims: `plain_llm` runs no check over `package.yaml`'s declared claims See Appendix D.

Excluded numeric tokens (not claims): section_number (section 4, section 3, section 2, 1.); inline_code (`1 - (1 - SMM)^12`, `1/sqrt(2)`, `after_outcome: 0`, `during_period: 0`); citation_hash (d4375126, 3e60c932, 3f2870ab, 61276a96); package_version (1.0); extractor_returned_excluded_token (1.0, 12, 1, 2).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | **Overall conclusion.** Discrimination is adequate and stabl… | 22 | percent |  | vintage_holdout | eq |  | unsupported |  |
| 2 | conceptual_soundness | The discrete-time hazard specification is appropriate for th… | 0.0086936 | ratio | smm | train | eq | `[[art:3e60c932:run.metrics]]` | dangling |  |
| 3 | conceptual_soundness | The discrete-time hazard specification is appropriate for th… | 0.099477 | ratio | cpr_predicted | train | eq | `[[art:3e60c932:run.metrics]]` | dangling |  |
| 4 | conceptual_soundness | The covariate set in is economically sensible and covers the… | 0.705 | ratio |  |  | eq |  | unsupported |  |
| 5 | conceptual_soundness | The covariate set in is economically sensible and covers the… | 0.709 | ratio |  |  | eq |  | unsupported |  |
| 6 | conceptual_soundness | Feature timing is declared cleanly and no leakage is indicat… | 0.79 | ratio | auc |  | eq |  | unsupported |  |
| 7 | conceptual_soundness | Two conceptual concerns are raised. The first is the treatme… | 0 | months | loan_age | train | eq |  | unsupported |  |
| 8 | conceptual_soundness | Two conceptual concerns are raised. The first is the treatme… | 59 | months | loan_age | train | eq |  | unsupported |  |
| 9 | conceptual_soundness | Two conceptual concerns are raised. The first is the treatme… | 53 | months | age_spline_knots |  | eq | `[[art:8e6d6768:run.model_summary#age_spline_knots]]` | dangling |  |
| 10 | conceptual_soundness | Two conceptual concerns are raised. The first is the treatme… | 100 | months | loan_age |  | eq |  | unsupported |  |
| 11 | conceptual_soundness | Two conceptual concerns are raised. The first is the treatme… | 360 | months | loan_age |  | eq |  | unsupported |  |
| 12 | conceptual_soundness | Two conceptual concerns are raised. The first is the treatme… | 55 | months | loan_age |  | eq |  | unsupported |  |
| 13 | conceptual_soundness | Two conceptual concerns are raised. The first is the treatme… | 0.003425 | ratio | baseline_hazard |  | eq |  | unsupported |  |
| 14 | conceptual_soundness | Two conceptual concerns are raised. The first is the treatme… | 40 | months | loan_age |  | eq |  | unsupported |  |
| 15 | conceptual_soundness | Two conceptual concerns are raised. The first is the treatme… | 0.001801 | ratio | baseline_hazard |  | eq |  | unsupported |  |
| 16 | conceptual_soundness | Two conceptual concerns are raised. The first is the treatme… | 101 | months | loan_age |  | eq |  | unsupported |  |
| 17 | conceptual_soundness | The discrete-time hazard specification is appropriate for th… | 1 | ratio |  |  | eq |  | unsupported |  |
| 18 | conceptual_soundness | The discrete-time hazard specification is appropriate for th… | 1 | ratio |  |  | eq |  | unsupported |  |
| 19 | data_integrity | The training split contains 36,474 loan-months across 1,395… | 36474 | count | row_count | train | eq |  | unsupported |  |
| 20 | data_integrity | The training split contains 36,474 loan-months across 1,395… | 1395 | count | loan_count | train | eq |  | unsupported |  |
| 21 | data_integrity | The training split contains 36,474 loan-months across 1,395… | 201402 | ratio | period_start | train | eq |  | unsupported |  |
| 22 | data_integrity | The training split contains 36,474 loan-months across 1,395… | 201912 | ratio | period_end | train | eq |  | unsupported |  |
| 23 | data_integrity | The training split contains 36,474 loan-months across 1,395… | 0.008608872 | ratio | event_rate | train | eq | `[[art:3e60c932:run.metrics]]` | dangling |  |
| 24 | data_integrity | Covariate ranges are plausible and free of sentinel values:… | 620 | ratio | credit_score |  | eq |  | unsupported |  |
| 25 | data_integrity | Covariate ranges are plausible and free of sentinel values:… | 820 | ratio | credit_score |  | eq |  | unsupported |  |
| 26 | data_integrity | Covariate ranges are plausible and free of sentinel values:… | 31 | ratio | orig_ltv |  | eq |  | unsupported |  |
| 27 | data_integrity | Covariate ranges are plausible and free of sentinel values:… | 97 | ratio | orig_ltv |  | eq |  | unsupported |  |
| 28 | data_integrity | Covariate ranges are plausible and free of sentinel values:… | 2.285 | ratio | note_rate |  | eq |  | unsupported |  |
| 29 | data_integrity | Covariate ranges are plausible and free of sentinel values:… | 6.476 | ratio | note_rate |  | eq |  | unsupported |  |
| 30 | data_integrity | Covariate ranges are plausible and free of sentinel values:… | 10.65 | ratio | orig_upb_log |  | eq |  | unsupported |  |
| 31 | data_integrity | Covariate ranges are plausible and free of sentinel values:… | 13.54 | ratio | orig_upb_log |  | eq |  | unsupported |  |
| 32 | data_integrity | Covariate ranges are plausible and free of sentinel values:… | 999 | ratio |  |  | eq |  | unsupported |  |
| 33 | data_integrity | Two integrity issues are recorded. First, two features the m… | 1 | count |  |  | eq |  | unattributed |  |
| 34 | data_integrity | On drift, the evidence is indirect but strong. The realized… | 3.7 | ratio | event_rate |  | eq |  | unsupported |  |
| 35 | data_integrity | On drift, the evidence is indirect but strong. The realized… | 0.004817 | ratio | event_rate | vintage_holdout | eq |  | unsupported |  |
| 36 | data_integrity | On drift, the evidence is indirect but strong. The realized… | 0.008609 | ratio | event_rate | train | eq |  | unsupported |  |
| 37 | data_integrity | On drift, the evidence is indirect but strong. The realized… | 0.008061 | ratio | event_rate | test | eq |  | unsupported |  |
| 38 | data_integrity | On drift, the evidence is indirect but strong. The realized… | 0.017949 | ratio | event_rate | out_of_time | eq |  | unsupported |  |
| 39 | data_integrity | On drift, the evidence is indirect but strong. The realized… | 5.6 | percent | cpr | vintage_holdout | eq |  | unsupported |  |
| 40 | data_integrity | On drift, the evidence is indirect but strong. The realized… | 19.5 | percent | cpr | out_of_time | eq |  | unsupported |  |
| 41 | data_integrity | On drift, the evidence is indirect but strong. The realized… | 0.008694 | ratio | mean_predicted | train | eq |  | unsupported |  |
| 42 | data_integrity | On drift, the evidence is indirect but strong. The realized… | 0.019451 | ratio | mean_predicted | out_of_time | eq |  | unsupported |  |
| 43 | data_integrity | On drift, the evidence is indirect but strong. The realized… | 2019 | ratio |  | train | eq |  | unsupported |  |
| 44 | data_integrity | On drift, the evidence is indirect but strong. The realized… | 1 | count |  |  | eq |  | unattributed |  |
| 45 | data_integrity | The splits also differ structurally in a way that complicate… | 26.1 | ratio | rows_per_loan | train | eq |  | unsupported |  |
| 46 | data_integrity | The splits also differ structurally in a way that complicate… | 38.5 | ratio | rows_per_loan | test | eq |  | unsupported |  |
| 47 | data_integrity | The splits also differ structurally in a way that complicate… | 48.3 | ratio | rows_per_loan | vintage_holdout | eq |  | unsupported |  |
| 48 | data_integrity | The splits also differ structurally in a way that complicate… | 23.8 | ratio | rows_per_loan | out_of_time | eq |  | unsupported |  |
| 49 | outcomes | \| train \| 36,474 \| 1,395 \| 0.008609 \| 0.008694 \| 0.7888 \| 0.… | 36474 | count | n_rows | train | eq |  | unsupported |  |
| 50 | outcomes | \| train \| 36,474 \| 1,395 \| 0.008609 \| 0.008694 \| 0.7888 \| 0.… | 1395 | count | n_loans | train | eq |  | unsupported |  |
| 51 | outcomes | \| train \| 36,474 \| 1,395 \| 0.008609 \| 0.008694 \| 0.7888 \| 0.… | 0.008609 | ratio | event_rate | train | eq |  | unsupported |  |
| 52 | outcomes | \| train \| 36,474 \| 1,395 \| 0.008609 \| 0.008694 \| 0.7888 \| 0.… | 0.008694 | ratio | mean_pred | train | eq |  | unsupported |  |
| 53 | outcomes | \| train \| 36,474 \| 1,395 \| 0.008609 \| 0.008694 \| 0.7888 \| 0.… | 0.7888 | ratio | auc | train | eq |  | unsupported |  |
| 54 | outcomes | \| train \| 36,474 \| 1,395 \| 0.008609 \| 0.008694 \| 0.7888 \| 0.… | 0.5775 | ratio | gini | train | eq |  | unsupported |  |
| 55 | outcomes | \| train \| 36,474 \| 1,395 \| 0.008609 \| 0.008694 \| 0.7888 \| 0.… | 0.4561 | ratio | ks | train | eq |  | unsupported |  |
| 56 | outcomes | \| train \| 36,474 \| 1,395 \| 0.008609 \| 0.008694 \| 0.7888 \| 0.… | 0.008396 | ratio | brier | train | eq |  | unsupported |  |
| 57 | outcomes | \| train \| 36,474 \| 1,395 \| 0.008609 \| 0.008694 \| 0.7888 \| 0.… | 0.04442 | ratio | logloss | train | eq |  | unsupported |  |
| 58 | outcomes | \| train \| 36,474 \| 1,395 \| 0.008609 \| 0.008694 \| 0.7888 \| 0.… | 0.996 | ratio | calibration_slope | train | eq |  | unsupported |  |
| 59 | outcomes | \| train \| 36,474 \| 1,395 \| 0.008609 \| 0.008694 \| 0.7888 \| 0.… | 9.86 | percent | cpr_actual | train | eq |  | unsupported |  |
| 60 | outcomes | \| train \| 36,474 \| 1,395 \| 0.008609 \| 0.008694 \| 0.7888 \| 0.… | 9.95 | percent | cpr_pred | train | eq |  | unsupported |  |
| 61 | outcomes | \| test \| 15,382 \| 400 \| 0.008061 \| 0.008364 \| 0.7759 \| 0.551… | 15382 | count | n_rows | test | eq |  | unsupported |  |
| 62 | outcomes | \| test \| 15,382 \| 400 \| 0.008061 \| 0.008364 \| 0.7759 \| 0.551… | 400 | count | n_loans | test | eq |  | unsupported |  |
| 63 | outcomes | \| test \| 15,382 \| 400 \| 0.008061 \| 0.008364 \| 0.7759 \| 0.551… | 0.008061 | ratio | event_rate | test | eq |  | unsupported |  |
| 64 | outcomes | \| test \| 15,382 \| 400 \| 0.008061 \| 0.008364 \| 0.7759 \| 0.551… | 0.008364 | ratio | mean_pred | test | eq |  | unsupported |  |
| 65 | outcomes | \| test \| 15,382 \| 400 \| 0.008061 \| 0.008364 \| 0.7759 \| 0.551… | 0.7759 | ratio | auc | test | eq |  | unsupported |  |
| 66 | outcomes | \| test \| 15,382 \| 400 \| 0.008061 \| 0.008364 \| 0.7759 \| 0.551… | 0.5519 | ratio | gini | test | eq |  | unsupported |  |
| 67 | outcomes | \| test \| 15,382 \| 400 \| 0.008061 \| 0.008364 \| 0.7759 \| 0.551… | 0.4195 | ratio | ks | test | eq |  | unsupported |  |
| 68 | outcomes | \| test \| 15,382 \| 400 \| 0.008061 \| 0.008364 \| 0.7759 \| 0.551… | 0.007893 | ratio | brier | test | eq |  | unsupported |  |
| 69 | outcomes | \| test \| 15,382 \| 400 \| 0.008061 \| 0.008364 \| 0.7759 \| 0.551… | 0.04261 | ratio | logloss | test | eq |  | unsupported |  |
| 70 | outcomes | \| test \| 15,382 \| 400 \| 0.008061 \| 0.008364 \| 0.7759 \| 0.551… | 0.939 | ratio | calibration_slope | test | eq |  | unsupported |  |
| 71 | outcomes | \| test \| 15,382 \| 400 \| 0.008061 \| 0.008364 \| 0.7759 \| 0.551… | 9.26 | percent | cpr_actual | test | eq |  | unsupported |  |
| 72 | outcomes | \| test \| 15,382 \| 400 \| 0.008061 \| 0.008364 \| 0.7759 \| 0.551… | 9.59 | percent | cpr_pred | test | eq |  | unsupported |  |
| 73 | outcomes | \| vintage_holdout \| 32,177 \| 666 \| 0.004817 \| 0.005914 \| 0.7… | 32177 | count | n_rows | vintage_holdout | eq |  | unsupported |  |
| 74 | outcomes | \| vintage_holdout \| 32,177 \| 666 \| 0.004817 \| 0.005914 \| 0.7… | 666 | count | n_loans | vintage_holdout | eq |  | unsupported |  |
| 75 | outcomes | \| vintage_holdout \| 32,177 \| 666 \| 0.004817 \| 0.005914 \| 0.7… | 0.004817 | ratio | event_rate | vintage_holdout | eq |  | unsupported |  |
| 76 | outcomes | \| vintage_holdout \| 32,177 \| 666 \| 0.004817 \| 0.005914 \| 0.7… | 0.005914 | ratio | mean_pred | vintage_holdout | eq |  | unsupported |  |
| 77 | outcomes | \| vintage_holdout \| 32,177 \| 666 \| 0.004817 \| 0.005914 \| 0.7… | 0.7722 | ratio | auc | vintage_holdout | eq |  | unsupported |  |
| 78 | outcomes | \| vintage_holdout \| 32,177 \| 666 \| 0.004817 \| 0.005914 \| 0.7… | 0.5443 | ratio | gini | vintage_holdout | eq |  | unsupported |  |
| 79 | outcomes | \| vintage_holdout \| 32,177 \| 666 \| 0.004817 \| 0.005914 \| 0.7… | 0.4492 | ratio | ks | vintage_holdout | eq |  | unsupported |  |
| 80 | outcomes | \| vintage_holdout \| 32,177 \| 666 \| 0.004817 \| 0.005914 \| 0.7… | 0.004765 | ratio | brier | vintage_holdout | eq |  | unsupported |  |
| 81 | outcomes | \| vintage_holdout \| 32,177 \| 666 \| 0.004817 \| 0.005914 \| 0.7… | 0.02814 | ratio | logloss | vintage_holdout | eq |  | unsupported |  |
| 82 | outcomes | \| vintage_holdout \| 32,177 \| 666 \| 0.004817 \| 0.005914 \| 0.7… | 0.836 | ratio | calibration_slope | vintage_holdout | eq |  | unsupported |  |
| 83 | outcomes | \| vintage_holdout \| 32,177 \| 666 \| 0.004817 \| 0.005914 \| 0.7… | 5.63 | percent | cpr_actual | vintage_holdout | eq |  | unsupported |  |
| 84 | outcomes | \| vintage_holdout \| 32,177 \| 666 \| 0.004817 \| 0.005914 \| 0.7… | 6.87 | percent | cpr_pred | vintage_holdout | eq |  | unsupported |  |
| 85 | outcomes | \| out_of_time \| 12,257 \| 515 \| 0.017949 \| 0.019451 \| 0.7871… | 12257 | count | n_rows | out_of_time | eq |  | unsupported |  |
| 86 | outcomes | \| out_of_time \| 12,257 \| 515 \| 0.017949 \| 0.019451 \| 0.7871… | 515 | count | n_loans | out_of_time | eq |  | unsupported |  |
| 87 | outcomes | \| out_of_time \| 12,257 \| 515 \| 0.017949 \| 0.019451 \| 0.7871… | 0.017949 | ratio | event_rate | out_of_time | eq |  | unsupported |  |
| 88 | outcomes | \| out_of_time \| 12,257 \| 515 \| 0.017949 \| 0.019451 \| 0.7871… | 0.019451 | ratio | mean_pred | out_of_time | eq |  | unsupported |  |
| 89 | outcomes | \| out_of_time \| 12,257 \| 515 \| 0.017949 \| 0.019451 \| 0.7871… | 0.7871 | ratio | auc | out_of_time | eq |  | unsupported |  |
| 90 | outcomes | \| out_of_time \| 12,257 \| 515 \| 0.017949 \| 0.019451 \| 0.7871… | 0.5742 | ratio | gini | out_of_time | eq |  | unsupported |  |
| 91 | outcomes | \| out_of_time \| 12,257 \| 515 \| 0.017949 \| 0.019451 \| 0.7871… | 0.4422 | ratio | ks | out_of_time | eq |  | unsupported |  |
| 92 | outcomes | \| out_of_time \| 12,257 \| 515 \| 0.017949 \| 0.019451 \| 0.7871… | 0.017122 | ratio | brier | out_of_time | eq |  | unsupported |  |
| 93 | outcomes | \| out_of_time \| 12,257 \| 515 \| 0.017949 \| 0.019451 \| 0.7871… | 0.0796 | ratio | logloss | out_of_time | eq |  | unsupported |  |
| 94 | outcomes | \| out_of_time \| 12,257 \| 515 \| 0.017949 \| 0.019451 \| 0.7871… | 1.008 | ratio | calibration_slope | out_of_time | eq |  | unsupported |  |
| 95 | outcomes | \| out_of_time \| 12,257 \| 515 \| 0.017949 \| 0.019451 \| 0.7871… | 19.53 | percent | cpr_actual | out_of_time | eq |  | unsupported |  |
| 96 | outcomes | \| out_of_time \| 12,257 \| 515 \| 0.017949 \| 0.019451 \| 0.7871… | 21 | percent | cpr_pred | out_of_time | eq |  | unsupported |  |
| 97 | outcomes | **Discrimination is adequate and stable.** AUC ranges from 0… | 0.7722 | ratio | auc | vintage_holdout | eq |  | unsupported |  |
| 98 | outcomes | **Discrimination is adequate and stable.** AUC ranges from 0… | 0.7888 | ratio | auc | train | eq |  | unsupported |  |
| 99 | outcomes | **Discrimination is adequate and stable.** AUC ranges from 0… | 0.0128 | ratio | delta_auc | test | delta |  | unsupported |  |
| 100 | outcomes | **Discrimination is adequate and stable.** AUC ranges from 0… | 0.0166 | ratio | delta_auc | vintage_holdout | delta |  | unsupported |  |
| 101 | outcomes | **Discrimination is adequate and stable.** AUC ranges from 0… | 0.7871 | ratio | auc | out_of_time | eq |  | unsupported |  |
| 102 | outcomes | **Discrimination is adequate and stable.** AUC ranges from 0… | 0.42 | ratio | ks |  | eq |  | unsupported |  |
| 103 | outcomes | **Discrimination is adequate and stable.** AUC ranges from 0… | 0.46 | ratio | ks |  | eq |  | unsupported |  |
| 104 | outcomes | **Calibration is the problem, and it is directional.** The m… | 0.008694 | ratio | mean_pred | train | eq |  | unsupported |  |
| 105 | outcomes | **Calibration is the problem, and it is directional.** The m… | 0.008609 | ratio | event_rate | train | eq |  | unsupported |  |
| 106 | outcomes | **Calibration is the problem, and it is directional.** The m… | 3.8 | percent | calibration_error | test | eq |  | unsupported |  |
| 107 | outcomes | **Calibration is the problem, and it is directional.** The m… | 0.008364 | ratio | mean_pred | test | eq |  | unsupported |  |
| 108 | outcomes | **Calibration is the problem, and it is directional.** The m… | 0.008061 | ratio | event_rate | test | eq |  | unsupported |  |
| 109 | outcomes | **Calibration is the problem, and it is directional.** The m… | 8.4 | percent | calibration_error | out_of_time | eq |  | unsupported |  |
| 110 | outcomes | **Calibration is the problem, and it is directional.** The m… | 0.019451 | ratio | mean_pred | out_of_time | eq |  | unsupported |  |
| 111 | outcomes | **Calibration is the problem, and it is directional.** The m… | 0.017949 | ratio | event_rate | out_of_time | eq |  | unsupported |  |
| 112 | outcomes | **Calibration is the problem, and it is directional.** The m… | 22.8 | percent | calibration_error | vintage_holdout | eq |  | unsupported |  |
| 113 | outcomes | **Calibration is the problem, and it is directional.** The m… | 0.005914 | ratio | mean_pred | vintage_holdout | eq |  | unsupported |  |
| 114 | outcomes | **Calibration is the problem, and it is directional.** The m… | 0.004817 | ratio | event_rate | vintage_holdout | eq |  | unsupported |  |
| 115 | outcomes | **Calibration is the problem, and it is directional.** The m… | 6.87 | ratio | cpr_pred | vintage_holdout | eq |  | unsupported |  |
| 116 | outcomes | **Calibration is the problem, and it is directional.** The m… | 5.63 | ratio | cpr_actual | vintage_holdout | eq |  | unsupported |  |
| 117 | outcomes | **Calibration is the problem, and it is directional.** The m… | 124 | bp | cpr | vintage_holdout | eq |  | unsupported |  |
| 118 | outcomes | **Calibration is the problem, and it is directional.** The m… | 22 | percent | cpr | vintage_holdout | eq |  | unsupported |  |
| 119 | outcomes | **Calibration is the problem, and it is directional.** The m… | 21 | ratio | cpr_pred | out_of_time | eq |  | unsupported |  |
| 120 | outcomes | **Calibration is the problem, and it is directional.** The m… | 19.53 | ratio | cpr_actual | out_of_time | eq |  | unsupported |  |
| 121 | outcomes | **Calibration is the problem, and it is directional.** The m… | 146 | bp | cpr | out_of_time | eq |  | unsupported |  |
| 122 | outcomes | The calibration slope tells the same story from the other di… | 0.996 | ratio | calibration_slope | train | eq |  | unsupported |  |
| 123 | outcomes | The calibration slope tells the same story from the other di… | 0.939 | ratio | calibration_slope | test | eq |  | unsupported |  |
| 124 | outcomes | The calibration slope tells the same story from the other di… | 0.836 | ratio | calibration_slope | vintage_holdout | eq |  | unsupported |  |
| 125 | outcomes | The calibration slope tells the same story from the other di… | 0.836 | ratio | calibration_slope | vintage_holdout | eq |  | unsupported |  |
| 126 | outcomes | The calibration slope tells the same story from the other di… | 16 | percent | calibration_slope | vintage_holdout | eq |  | unsupported |  |
| 127 | outcomes | The calibration slope tells the same story from the other di… | 1.008 | ratio | calibration_slope | out_of_time | eq |  | unsupported |  |
| 128 | outcomes | For MSR use, the direction is conservative for asset value —… | 22 | percent | cpr | vintage_holdout | eq |  | unsupported |  |
| 129 | outcomes | **Calibration is the problem, and it is directional.** The m… | 1 | percent | calibration_error | train | eq |  | unsupported |  |
| 130 | outcomes | For MSR use, the direction is conservative for asset value —… | 2 | count |  |  | eq |  | unattributed |  |
| 131 | sensitivity | What can be assessed is the sensitivity structure the fitted… | 0.000871 | ratio |  |  | eq |  | unsupported |  |
| 132 | sensitivity | What can be assessed is the sensitivity structure the fitted… | 0 | months |  |  | eq |  | unsupported |  |
| 133 | sensitivity | What can be assessed is the sensitivity structure the fitted… | 0.003425 | ratio |  |  | eq |  | unsupported |  |
| 134 | sensitivity | What can be assessed is the sensitivity structure the fitted… | 40 | months |  |  | eq |  | unsupported |  |
| 135 | sensitivity | What can be assessed is the sensitivity structure the fitted… | 59 | months |  |  | eq |  | unsupported |  |
| 136 | sensitivity | What can be assessed is the sensitivity structure the fitted… | 101 | months |  |  | eq |  | unsupported |  |
| 137 | sensitivity | What can be assessed is the sensitivity structure the fitted… | 0.001801 | ratio |  |  | eq |  | unsupported |  |
| 138 | sensitivity | What can be assessed is the sensitivity structure the fitted… | 1 | count |  |  | eq |  | unattributed |  |
| 139 | findings | - **C1-01 (high)** — Vintage-holdout calibration failure: sl… | 1 | count |  |  | eq |  | unattributed |  |
| 140 | findings | - **C1-01 (high)** — Vintage-holdout calibration failure: sl… | 0.836 | ratio | calibration_slope | vintage_holdout | eq |  | unsupported |  |
| 141 | findings | - **C1-01 (high)** — Vintage-holdout calibration failure: sl… | 22 | percent |  | vintage_holdout | eq |  | unsupported |  |
| 142 | findings | - **C1-02 (medium)** — One-directional over-prediction in al… | 2 | count |  |  | eq |  | unattributed |  |
| 143 | findings | - **X1-01 (medium)** — Baseline hazard extrapolated far beyo… | 1 | count |  |  | eq |  | unattributed |  |
| 144 | findings | - **D1-01 (medium)** — Two declared features absent from the… | 1 | count |  |  | eq |  | unattributed |  |
| 145 | findings | - **S1-01 (medium)** — Large realized-rate and score shift a… | 1 | count |  |  | eq |  | unattributed |  |
| 146 | findings | - **M1-01 (low)** — Structural collinearity in the rate bloc… | 1 | count |  |  | eq |  | unattributed |  |
| 147 | findings | - **L2-01 (low)** — Split independence asserted but not demo… | 1 | count |  |  | eq |  | unattributed |  |
| 148 | findings | - **E1-01 (info)** — No challenger model; effective challeng… | 1 | count |  |  | eq |  | unattributed |  |
| 149 | findings | 1. Recalibrate. Refit or apply an explicit recalibration (in… | 0.9 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 150 | findings | 1. Recalibrate. Refit or apply an explicit recalibration (in… | 1.1 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 151 | findings | 2. Diagnose the vintage-holdout bias rather than only correc… | 0.836 | ratio | calibration_slope | vintage_holdout | eq |  | unsupported |  |
| 152 | findings | 3. Produce and review the projection. Publish the S-curve, a… | -200 | count |  |  | eq |  | unattributed |  |
| 153 | findings | 8. Run a challenger. A logistic benchmark on the same panel… | 0.79 | ratio | auc |  | eq |  | unsupported |  |
| 154 | findings | **Not required but recommended.** Add confidence intervals t… | 12257 | count | row_count | out_of_time | eq |  | unsupported |  |
| 155 | findings | **Not required but recommended.** Add confidence intervals t… | 220 | count | event_count | out_of_time | eq |  | unsupported |  |
| 156 | monitoring | **Monthly.** Report actual versus predicted CPR at the portf… | -10 | percent |  |  | eq |  | unattributed |  |
| 157 | monitoring | **Monthly.** Report actual versus predicted CPR at the portf… | -20 | percent |  |  | eq |  | unattributed |  |
| 158 | monitoring | **Monthly.** Report actual versus predicted CPR at the portf… | 10 | percent |  |  | eq |  | unsupported |  |
| 159 | monitoring | **Quarterly.** Compute PSI for every model feature and for t… | 0.1 | ratio | psi |  | eq |  | unsupported |  |
| 160 | monitoring | **Quarterly.** Compute PSI for every model feature and for t… | 0.25 | ratio | psi |  | eq |  | unsupported |  |
| 161 | monitoring | **Quarterly.** Compute PSI for every model feature and for t… | 2019 | ratio |  | train | eq |  | unsupported |  |
| 162 | monitoring | **Quarterly.** Compute PSI for every model feature and for t… | 2.2 | ratio |  | out_of_time | eq |  | unsupported |  |
| 163 | monitoring | **Quarterly.** Recompute AUC, KS and the calibration slope o… | 0.72 | ratio | auc |  | eq |  | unsupported |  |
| 164 | monitoring | **Quarterly.** Recompute AUC, KS and the calibration slope o… | 0.85 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 165 | monitoring | **Quarterly.** Recompute AUC, KS and the calibration slope o… | 1.15 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 166 | monitoring | **Quarterly.** Recompute AUC, KS and the calibration slope o… | 0.8 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 167 | monitoring | **Quarterly.** Recompute AUC, KS and the calibration slope o… | 1.2 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 168 | monitoring | **Annually, or on trigger.** Refit the baseline hazard and r… | 0.25 | ratio | psi |  | eq |  | unsupported |  |
| 169 | monitoring | **Annually, or on trigger.** Refit the baseline hazard and r… | 0.8 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 170 | monitoring | **Annually, or on trigger.** Refit the baseline hazard and r… | 1.2 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 171 | monitoring | **Annually, or on trigger.** Refit the baseline hazard and r… | 150 | bp |  |  | eq |  | unsupported |  |

## Appendix B — Artifact index

The store holds 19 artifacts; the 17 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `run.data_out_of_time` | `7ddcc721` | table | table, 12257 rows | the subject's data_out_of_time.csv |
| `run.data_test` | `f0ac9fe8` | table | table, 15382 rows | the subject's data_test.csv |
| `run.data_train` | `74d4436f` | table | table, 36474 rows | the subject's data_train.csv |
| `run.data_vintage_holdout` | `940d14da` | table | table, 32177 rows | the subject's data_vintage_holdout.csv |
| `run.duration_s` | `77e73bee` | scalar | 2.607765208 | subject wall-clock seconds |
| `run.features` | `61276a96` | json | json | the subject's features.json |
| `run.metrics` | `3e60c932` | json | json | the subject's metrics.json |
| `run.model_summary` | `8e6d6768` | json | json | the subject's model_summary.json |
| `run.predictions_out_of_time` | `ce5d5d56` | table | table, 12257 rows | the subject's predictions_out_of_time.csv |
| `run.predictions_test` | `c1dbcaa3` | table | table, 15382 rows | the subject's predictions_test.csv |
| `run.predictions_train` | `d02960f5` | table | table, 36474 rows | the subject's predictions_train.csv |
| `run.predictions_vintage_holdout` | `b7f67f98` | table | table, 32177 rows | the subject's predictions_vintage_holdout.csv |
| `run.projection` | `d4375126` | json | json | the subject's projection.json |
| `run.splits` | `3f2870ab` | json | json | the subject's splits.json |
| `run.status` | `5c222bcc` | json | json | how the subject's subprocess ended |
| `run.stdout` | `07ba0043` | json | json | the subject's stdout |
| `runtime.max_seconds` | `2ad8d1a5` | scalar | 300 | the wall-clock cap package.yaml declares for the subject |

## Appendix C — Run trace summary

| quantity | value |
|---|---|
| tool calls | 1 (run_model 1) |
| plan steps (bounded loop) | 0 |
| LLM calls | 8 (plain_llm 1, extract 7) |
| re-asks | 0 |
| repair rounds | 0 |
| tokens in / out | 64,512 / 48,864 |
| notional cost (USD) | 1.8554 |
| wall-clock (s) | 589.79 |
| subject run (s) | 2.61 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | msr_prepayment-plain_llm-20260918T214026Z-986f3824 |

## Appendix D — Not checked

| item | reason |
|---|---|
| `check_stability` (R1) | this configuration runs no checks |
| `run_scenarios` (X1) | this configuration runs no checks |
| developer claims (T1, claim channel) | `plain_llm` runs no check over `package.yaml`'s declared claims |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
| every check of spec 3.7 but `run_model` | `plain_llm` runs the subject and one model call, by design |
