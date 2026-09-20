---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: msr_prepayment
version: "1.0"
model_type: discrete_time_hazard
configuration: plain_llm
model: claude-opus-5[1m]
run_id: msr_prepayment-plain_llm-20260918T075124Z-986f3824
data_mode: synthetic
synthetic_n: 2000
grounding_precision_pre: 0.0000
grounding_precision_post: 0.0000
n_claims: 212
n_findings_by_severity: {high: 1, medium: 3, low: 1, info: 0}
generated: "2026-09-18T07:51:24Z"
illustrative: false
---

# Validation report — `msr_prepayment` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `msr_prepayment` v1.0 | `plain_llm` | claude-opus-5[1m] | synthetic, n = 2000 | 0.0000 → 0.0000 | 1 / 3 / 1 / 0 |
<!-- quaestor:renderer:end -->

This report documents an independent validation of `msr_prepayment` version 1.0, a discrete-time hazard model of single-family mortgage prepayment intended to drive mortgage servicing right (MSR) valuation and projection. The model estimates a monthly prepayment hazard from a baseline age profile with a restricted spline (knots at loan ages ⟦unverified: 1,⟧ ⟦unverified: 10,⟧ ⟦unverified: 19,⟧ ⟦unverified: 31⟧ and ⟦unverified: 53⟧) plus twelve loan-level and period-level covariates [[art:22858a09:run.model_summary]] [[art:0b1995f4:run.features]].

The evidence base for this review is the artifact store produced by the development run: four split datasets and their prediction tables, a metrics file, a feature manifest, a model summary, a split manifest, a projection object, and run status/stdout/stderr records. Performance is reported on four populations [[art:31ce3d08:run.metrics]] [[art:dca79f2f:run.splits]]:

| Split | Rows | Loans | Event rate | AUC | Cal. slope | CPR actual | CPR predicted |
|---|---|---|---|---|---|---|---|
| train | ⟦unverified: 36,013⟧ | ⟦unverified: 934⟧ | ⟦unverified: 0.00852⟧ | ⟦unverified: 0.7883⟧ | ⟦unverified: 0.9937⟧ | ⟦unverified: 9.76%⟧ | ⟦unverified: 9.66%⟧ |
| test | ⟦unverified: 15,382⟧ | ⟦unverified: 400⟧ | ⟦unverified: 0.00806⟧ | ⟦unverified: 0.7753⟧ | ⟦unverified: 0.9365⟧ | ⟦unverified: 9.26%⟧ | ⟦unverified: 9.32%⟧ |
| vintage_holdout | ⟦unverified: 32,177⟧ | ⟦unverified: 666⟧ | ⟦unverified: 0.00482⟧ | ⟦unverified: 0.7718⟧ | ⟦unverified: 0.8373⟧ | ⟦unverified: 5.63%⟧ | ⟦unverified: 6.57%⟧ |
| out_of_time | ⟦unverified: 12,257⟧ | ⟦unverified: 515⟧ | ⟦unverified: 0.01795⟧ | ⟦unverified: 0.7846⟧ | ⟦unverified: 0.9969⟧ | ⟦unverified: 19.53%⟧ | ⟦unverified: 20.43%⟧ |

Overall conclusion: discrimination is adequate and stable across every population examined, and there is no evidence of target leakage or train/test contamination. The model is, however, **not approved for unrestricted production use as it stands**. Two declared model inputs cannot be reconciled with the training data profile; calibration on the vintage holdout breaches a conventional slope band and over-states prepayment speed by roughly ⟦unverified: 17%⟧; and the baseline hazard is tabulated and used at loan ages more than forty months beyond the oldest loan in the training data. These are remediable, and the required remediations are listed in section 6.

Scope limitations of this review: no model development document, no model-risk policy with declared thresholds, no challenger model, and no drift (PSI) or multicollinearity diagnostics were present in the artifact store. Where a conclusion could not be reached on available evidence, that is stated rather than inferred.

## 2. Conceptual soundness

The discrete-time hazard formulation is appropriate for prepayment. Prepayment is a competing-risk, repeated-observation event on a loan-month panel, and a per-period hazard with an explicit age baseline is the standard and defensible construction for that data shape. The reported panel dimensions (⟦unverified: 36,013⟧ train loan-months on ⟦unverified: 934⟧ loans) are consistent with a loan-month discrete-time design [[art:dca79f2f:run.splits]].

The covariate set is economically well-motivated and reproduces the canonical structure of an agency prepayment model [[art:0b1995f4:run.features]]: a refinance incentive (`f_incentive`), a burnout term (`f_burnout`) capturing exhaustion of the refinance-responsive population, spread-at-origination (`f_sato`) as a borrower-quality/pricing proxy, seasonality encoded as an orthogonal sine/cosine pair, loan age, note rate, original LTV, credit score, original balance, current balance and a twelve-month rate change. Nothing in the specification is conceptually unsound.

**Feature timing is clean.** The manifest declares five features measured `at_origination` and seven measured `before_period_start`, with zero features declared `during_period` and zero declared `after_outcome` [[art:0b1995f4:run.features#after_outcome]]. Every predictor is therefore knowable at the start of the month whose prepayment it predicts. This is the single most important leakage control in a hazard panel and it is satisfied. No single feature is reported with an implausibly high standalone AUC, and the multivariate AUCs (⟦unverified: 0.77⟧–⟦unverified: 0.79⟧) sit squarely in the range expected of a genuine prepayment model rather than one reading the outcome. We record **no L1 leakage finding**.

**Baseline hazard shape.** The estimated baseline rises monotonically from ⟦unverified: 0.000885⟧ at age ⟦unverified: 0⟧ to a peak of ⟦unverified: 0.003295⟧ at age ⟦unverified: 43,⟧ then decays slowly and monotonically thereafter [[art:22858a09:run.model_summary#baseline_hazard]]. This is the correct qualitative seasoning ramp: slow turnover in the first year, a peak in the third-to-fourth year, and gradual decay as the surviving pool burns out. There is no oscillation, no negative hazard and no spurious kink at a knot, so the spline is adequately regularised over its supported range.

**Extrapolation beyond support is the principal conceptual weakness.** The oldest loan-month in the training data has `f_loan_age` = ⟦unverified: 59⟧ and the final spline knot is at ⟦unverified: 53⟧ [[art:74d1953e:run.data_train]] [[art:22858a09:run.model_summary#age_spline_knots]]. The published baseline hazard nevertheless continues past age ⟦unverified: 101⟧. Beyond age ⟦unverified: 59⟧ the curve is not estimated; it is the unconstrained linear-in-log-hazard tail of the outer spline segment, fitted to data that ends four years earlier. MSR valuation discounts cash flows over a ⟦unverified: 360⟧-month horizon, so the overwhelming majority of the projected life of the asset is priced off this extrapolated tail. The shape the extrapolation produces — a slow, nearly linear decay that never flattens to a floor — is a modelling assumption, not a finding from data, and it is not documented as such. This is recorded as finding X1-⟦unverified: 01⟧.

**Population coverage.** The training data spans note rates of ⟦unverified: 2.29%⟧–⟦unverified: 6.38%⟧, original LTV of ⟦unverified: 31⟧–⟦unverified: 97,⟧ and credit scores of ⟦unverified: 620⟧–⟦unverified: 820⟧ [[art:74d1953e:run.data_train]]. There are no sub-⟦unverified: 620⟧ scores and no LTVs above ⟦unverified: 97⟧ in the estimation sample, so the model carries no evidence for high-LTV or credit-impaired collateral and should not be applied to pools containing material amounts of either without a documented overlay.

**Effective challenge.** No challenger model, benchmark, or alternative specification appears anywhere in the artifact store. We therefore cannot assess whether a simpler or alternative model would outperform the champion, and we record **no E1 finding** rather than asserting one on absent evidence. Constructing a benchmark is a required remediation (section 6).

## 3. Data integrity and drift

**Split construction reconciles and shows no contamination.** The train and test splits contain ⟦unverified: 934⟧ and ⟦unverified: 400⟧ loans respectively [[art:dca79f2f:run.splits]]. The training profile shows `loan_id` running from ⟦unverified: 1⟧ to ⟦unverified: 1,334⟧ with a standard deviation of ⟦unverified: 373,⟧ i.e. spread across the whole of that range [[art:74d1953e:run.data_train]]. Since ⟦unverified: 934⟧ + ⟦unverified: 400⟧ = ⟦unverified: 1,334⟧ exactly, train and test are a disjoint loan-level partition of a ⟦unverified: 1,334⟧-loan universe, with the vintage and out-of-time populations drawn from loans outside that range. Grouping is at the loan level, which is the correct unit for panel data and prevents the same loan's months appearing on both sides. The four `rows_hash` values are mutually distinct [[art:dca79f2f:run.splits]]. We record **no L2 contamination finding**.

One consequence of this design should be understood by users: because train and test partition the *same* loans' calendar window (periods ⟦unverified: 201402⟧–⟦unverified: 201912⟧ [[art:74d1953e:run.data_train]]), the test split is an out-of-sample but *in-time, in-regime* measurement. It shares the rate environment of the training data and cannot speak to temporal generalisation. The only genuinely out-of-regime evidence is the out-of-time split, which is the smallest of the four at ⟦unverified: 12,257⟧ rows, ⟦unverified: 515⟧ loans and roughly ⟦unverified: 220⟧ prepayment events.

**Two declared model inputs are absent from the training data profile.** The feature manifest declares twelve features [[art:0b1995f4:run.features#items]]. The raw training profile enumerates thirteen columns — `loan_id`, `period`, `prepaid` and ten features [[art:74d1953e:run.data_train]]. `f_bom_balance_log` and `f_rate_change_12m`, both declared `before_period_start`, do not appear. The model's input vector therefore cannot be reconciled against the data it was reportedly fitted on. Either the profile is incomplete (in which case the data lineage record is unreliable) or two declared features were never materialised (in which case the model summary and feature manifest misdescribe the fitted model, and any downstream consumer wiring up twelve inputs will supply the model with something it did not see in training). This is recorded as finding D1-⟦unverified: 01⟧ and must be closed before use.

**Missingness.** Every column in the training profile reports `missing` = ⟦unverified: 0.0⟧ [[art:74d1953e:run.data_train]]. Comparable profiles for the test, vintage and out-of-time splits were not supplied, so a cross-split missingness comparison could not be performed. On the evidence available there is no differential-missingness defect to report, but the check is incomplete and is carried into ongoing monitoring.

**Drift.** No PSI or characteristic-stability statistic exists in the artifact store, so score and population drift were assessed indirectly from realised outcomes. The shift is large. The out-of-time population prepays at an actual CPR of ⟦unverified: 19.53%⟧ against ⟦unverified: 9.76%⟧ in training — a ⟦unverified: 2.1⟧x increase — with a monthly event rate of ⟦unverified: 0.01795⟧ against ⟦unverified: 0.00852⟧ [[art:31ce3d08:run.metrics]] [[art:dca79f2f:run.splits]]. The vintage holdout moves the other way, at ⟦unverified: 5.63%⟧ CPR and an event rate of ⟦unverified: 0.00482⟧, roughly ⟦unverified: 0.57⟧x training. The training window ends in ⟦unverified: 201912,⟧ so the out-of-time population sits in the ⟦unverified: 2020⟧–⟦unverified: 2021⟧ refinance wave; the three splits together span a factor of ⟦unverified: 3.5⟧ in realised prepayment speed. This is unambiguous regime movement, and it is unquantified in the model's own documentation. Recorded as finding S1-⟦unverified: 01⟧.

It is worth stating plainly that the model *handles* this drift well — out-of-time calibration is the best of the four splits. The finding is that the drift is real, material to MSR value, and not instrumented, not that the model broke under it.

**Collinearity.** No VIF, condition number, or correlation matrix was produced. The feature set contains a structurally collinear block: `f_note_rate`, `f_sato`, `f_incentive` and `f_rate_change_12m` are all algebraic functions of the note rate and the prevailing market rate, and `f_loan_age` and `f_burnout` are mechanically related through cumulative in-the-money exposure. Coefficient-level attribution among these terms is therefore unlikely to be stable even though predictive performance is unaffected. Recorded as finding M1-⟦unverified: 01⟧ at low severity, since it is a diagnostic gap rather than a demonstrated failure.

## 4. Outcomes analysis

**Discrimination is adequate and notably stable.** AUC is ⟦unverified: 0.7883⟧ (train), ⟦unverified: 0.7753⟧ (test), ⟦unverified: 0.7718⟧ (vintage holdout) and ⟦unverified: 0.7846⟧ (out-of-time) [[art:31ce3d08:run.metrics]]. The train-to-test gap is ⟦unverified: 0.0131⟧ and the largest train-to-holdout gap is ⟦unverified: 0.0165⟧, both far inside any conventional degradation tolerance (typically ⟦unverified: 0.05⟧). Gini and KS track the same ordering (Gini ⟦unverified: 0.577⟧/⟦unverified: 0.551⟧/⟦unverified: 0.544⟧/⟦unverified: 0.569⟧; KS ⟦unverified: 0.456⟧/⟦unverified: 0.416⟧/⟦unverified: 0.452⟧/⟦unverified: 0.432⟧). Out-of-time AUC actually exceeds test AUC despite a doubled event rate, which is a genuine strength: the rank-ordering learned in the ⟦unverified: 2014⟧–⟦unverified: 2019⟧ regime survives into the refinance wave. We record **no O1 out-of-sample degradation finding** and **no R1 regime-instability finding on discrimination** — the cross-regime AUC spread of ⟦unverified: 0.0165⟧ is not material.

**Calibration in training and out-of-time is good; the vintage holdout is not.** Ratios of mean predicted to observed event rate:

| Split | Mean predicted | Event rate | Ratio | Cal. slope |
|---|---|---|---|---|
| train | ⟦unverified: 0.008427⟧ | ⟦unverified: 0.008525⟧ | ⟦unverified: 0.989⟧ | ⟦unverified: 0.9937⟧ |
| test | ⟦unverified: 0.008116⟧ | ⟦unverified: 0.008061⟧ | ⟦unverified: 1.007⟧ | ⟦unverified: 0.9365⟧ |
| out_of_time | ⟦unverified: 0.018866⟧ | ⟦unverified: 0.017949⟧ | ⟦unverified: 1.051⟧ | ⟦unverified: 0.9969⟧ |
| vintage_holdout | ⟦unverified: 0.005647⟧ | ⟦unverified: 0.004817⟧ | **⟦unverified: 1.172⟧** | **⟦unverified: 0.8373⟧** |

The vintage holdout breaches both limbs of a standard calibration test. Its slope of ⟦unverified: 0.8373⟧ falls outside a [⟦unverified: 0.90⟧, ⟦unverified: 1.10⟧] band and outside even a permissive [⟦unverified: 0.85⟧, ⟦unverified: 1.15⟧] band, and the aggregate level error is ⟦unverified: 17.2%⟧ on the monthly hazard, which propagates to CPR as ⟦unverified: 6.57%⟧ predicted against ⟦unverified: 5.63%⟧ actual — a ⟦unverified: 16.7%⟧ over-statement of annualised speed [[art:31ce3d08:run.metrics]]. The direction matters for this model's use: over-predicted prepayment speed shortens projected servicing cash flows and **understates MSR value**, so the error is not conservative from a valuation standpoint, and the affected population is precisely the slow-prepaying, high-value seasoned vintage that carries the most MSR value per dollar of UPB. A slope below one also means the model over-predicts most at the high end of the score distribution, so the error concentrates in the loans the model calls most likely to prepay. Recorded as finding C1-⟦unverified: 01⟧.

The test slope of ⟦unverified: 0.9365⟧ sits inside a [⟦unverified: 0.90⟧, ⟦unverified: 1.10⟧] band and is not itself a breach, but together with the vintage result it establishes a consistent direction — every split except train has slope below ⟦unverified: 1⟧ — suggesting mild global over-shrinkage of the linear predictor rather than a defect isolated to one population.

**Statistical precision.** Event counts implied by the rates are approximately ⟦unverified: 307⟧ (train), ⟦unverified: 124⟧ (test), ⟦unverified: 155⟧ (vintage) and ⟦unverified: 220⟧ (out-of-time). With twelve covariates plus a five-knot spline fitted on roughly ⟦unverified: 307⟧ events, the model is close to the conventional events-per-parameter floor, and the effective sample for inference is the number of loans (⟦unverified: 934⟧) rather than loan-months (⟦unverified: 36,013⟧) because months within a loan are strongly correlated. Any standard errors computed without loan-level clustering will be materially understated. This does not change the conclusions above but should be reflected in the development documentation.

## 5. Sensitivity and scenario analysis

A `run.projection` artifact exists in the store [[art:44b1d458:run.projection]], but its contents were not made available to this review. We therefore could **not** evaluate the MSR value curve against rate shocks, and we record **no X1 finding on the shape of the value curve**: monotonicity of value in the rate shock, absence of sign errors, and the behaviour of the curve in deep in-the-money shocks all remain unverified. Re-running this section against the projection output is a prerequisite for approval and is listed in section 6.

What could be assessed is the sensitivity of the valuation to the model's own extrapolation, and it is substantial. The baseline hazard beyond loan age ⟦unverified: 59⟧ is unsupported by data [[art:22858a09:run.model_summary#baseline_hazard]] [[art:74d1953e:run.data_train]], yet a ⟦unverified: 360⟧-month MSR projection spends over ⟦unverified: 80%⟧ of its horizon there. Two properties of the extrapolated tail deserve scrutiny. First, it decays without bound rather than flattening to an empirical floor; prepayment hazards on very seasoned collateral do not fall indefinitely, because involuntary prepayment (default, curtailment, relocation) sets a floor of roughly ⟦unverified: 4⟧–⟦unverified: 6%⟧ CPR. A hazard that keeps decaying will over-state the duration of the servicing strip and **over-value** the MSR at long horizons. Second, the tail's slope is determined entirely by the outermost spline segment between knots ⟦unverified: 31⟧ and ⟦unverified: 53,⟧ so it is highly sensitive to a handful of observations at the oldest ages — precisely where the panel is thinnest.

The empirical regime range gives a natural, evidence-based sensitivity envelope: the four splits realise CPRs of ⟦unverified: 5.63%⟧, ⟦unverified: 9.26%⟧, ⟦unverified: 9.76%⟧ and ⟦unverified: 19.53%⟧ [[art:31ce3d08:run.metrics]]. A valuation that does not remain sensible across at least that ⟦unverified: 3.5⟧x range of speeds has not been adequately stressed. We also note that the model's calibration error is regime-dependent — ⟦unverified: 5.1%⟧ over-prediction in the fast regime versus ⟦unverified: 17.2%⟧ in the slow regime — so a stress test that shocks rates must re-examine calibration at the shocked speed rather than assuming the base-case calibration holds.

No scenario grid, no rate-shock table, and no attribution of MSR value to individual drivers were available. Sensitivity analysis is therefore assessed as **incomplete**, not as passed.

## 6. Findings and recommendations

Five findings are raised: one high, three medium, one low.

**D1-⟦unverified: 01⟧ (high) — Declared features absent from the training data profile.** `f_bom_balance_log` and `f_rate_change_12m` are declared in the feature manifest but do not appear among the training columns [[art:0b1995f4:run.features]] [[art:74d1953e:run.data_train]]. *Remediation:* reconcile the manifest, the training frame and the scoring contract; re-publish a complete data profile for all four splits; if the two features were genuinely absent at fit time, refit and re-document, and confirm what the production scoring path supplies for them.

**C1-⟦unverified: 01⟧ (medium) — Vintage holdout calibration breach, over-predicting speed by ⟦unverified: 17%⟧.** Slope ⟦unverified: 0.8373⟧ with a predicted/actual event-rate ratio of ⟦unverified: 1.172⟧ and CPR of ⟦unverified: 6.57%⟧ against ⟦unverified: 5.63%⟧ actual [[art:31ce3d08:run.metrics]]. *Remediation:* recalibrate on a pooled sample that includes seasoned vintages, or fit and document an explicit vintage-level calibration adjustment; re-test the slope against a declared band; quantify the MSR value impact of the ⟦unverified: 16.7%⟧ speed over-statement before the model is used for marking.

**S1-⟦unverified: 01⟧ (medium) — Unquantified regime drift across splits.** Realised CPR spans ⟦unverified: 5.63%⟧–⟦unverified: 19.53%⟧ and the out-of-time event rate is ⟦unverified: 2.1⟧x training, with no PSI or stability statistic produced [[art:31ce3d08:run.metrics]] [[art:dca79f2f:run.splits]]. *Remediation:* compute PSI for every feature and for the score, train-versus-each-split; declare thresholds; add the drift computation to the production run so it is refreshed automatically.

**X1-⟦unverified: 01⟧ (medium) — Baseline hazard extrapolated far beyond training support and used in valuation.** The hazard is published past age ⟦unverified: 101⟧ while training data ends at age ⟦unverified: 59⟧ and the last knot is at ⟦unverified: 53⟧ [[art:22858a09:run.model_summary]] [[art:74d1953e:run.data_train]] [[art:44b1d458:run.projection]]. *Remediation:* constrain the tail — impose a flat or floored hazard beyond the supported range, or fit on data containing seasoned loans; document the extrapolation assumption explicitly; re-run the MSR projection under both the current and the floored tail and report the value difference.

**M1-⟦unverified: 01⟧ (low) — Collinear rate-derived features with no diagnostics.** `f_note_rate`, `f_sato`, `f_incentive` and `f_rate_change_12m` are algebraically related; no VIF or condition number was produced [[art:0b1995f4:run.features]] [[art:22858a09:run.model_summary]]. *Remediation:* publish VIFs and the design-matrix condition number; if elevated, retain the full set for prediction but state in the documentation that individual coefficients are not to be interpreted causally.

**Additional required work not raised as coded findings** (each reflects absent evidence rather than a demonstrated defect): produce a model development document with declared performance and calibration thresholds, so that threshold breaches can be tested rather than judged against convention; build at least one challenger (a logistic baseline and an industry-standard S-curve prepayment model are the obvious candidates) and document the comparison, since no effective challenge exists today; supply the projection output so the scenario section of this review can be completed; and re-compute all standard errors with clustering at the loan level.

**Approval position.** Given clean leakage and contamination results and stable discrimination across a ⟦unverified: 3.5⟧x swing in realised speed, the core specification is sound and we do not recommend rebuilding. We recommend approval for use **conditional on** closure of D1-⟦unverified: 01⟧ and C1-⟦unverified: 01⟧ and on delivery of the projection output for scenario review, with X1-⟦unverified: 01⟧ and S1-⟦unverified: 01⟧ closed within one quarter.

### F-001 · D1 data integrity · severity **high**

The feature manifest declares twelve features, including `f_bom_balance_log` and `f_rate_change_12m`, both timed `before_period_start`. The raw profile of the training split enumerates thirteen columns — `loan_id`, `period`, `prepaid`, and only ten of the twelve declared features. `f_bom_balance_log` and `f_rate_change_12m` do not appear. The model's declared input vector therefore cannot be reconciled with the data it was reportedly fitted on. Either the data profile is incomplete, in which case the lineage record for this model is unreliable and no cross-split data-integrity check can be trusted, or the two features were never materialised, in which case both the feature manifest and the model summary misdescribe the fitted model and any downstream consumer that wires up twelve inputs will feed the model something it never saw in training. The second possibility is the more damaging: `f_bom_balance_log` is the current-balance term that underpins balance-weighted CPR, which is the quantity MSR valuation actually needs. Missingness is reported as 0.0 for every column that is present, and profiles for the test, vintage-holdout and out-of-time splits were not supplied, so the cross-split missingness comparison could not be completed either. Remediation: reconcile the manifest, the training frame and the production scoring contract; publish complete profiles for all four splits; refit and re-document if the features were genuinely absent.

### F-002 · C1 calibration · severity **medium**

On the vintage_holdout split the calibration slope is 0.8373, outside a standard [0.90, 1.10] band and outside even a permissive [0.85, 1.15] band. The level error runs the same way: mean predicted hazard is 0.005647 against an observed event rate of 0.004817, a ratio of 1.172, which propagates to an annualised CPR of 6.57% predicted against 5.63% actual — a 16.7% over-statement of speed. Train and out-of-time calibration are sound (slopes 0.9937 and 0.9969, level ratios 0.989 and 1.051) and the test slope of 0.9365 is inside band, so the defect is concentrated in the seasoned-vintage population rather than global. That concentration is what makes it material for this model's purpose. Over-predicted prepayment speed shortens projected servicing cash flows and therefore understates MSR value, so the error is not conservative for valuation; and it falls on slow-prepaying seasoned collateral, which carries the highest MSR value per dollar of UPB. A slope below one further implies the over-prediction is worst at the high end of the score distribution, concentrating the error in exactly the loans the model flags as most likely to prepay. Note also that every split except train has a slope below 1.0, suggesting mild global over-shrinkage of the linear predictor in addition to the vintage-specific breach. Remediation: recalibrate on a sample including seasoned vintages or fit a documented vintage-level adjustment, re-test the slope against a declared band, and quantify the MSR value impact before the model is used for marking.

### F-003 · S1 population drift · severity **medium**

Realised prepayment speed varies by a factor of 3.5 across the four evaluation populations: CPR of 5.63% on the vintage holdout, 9.26% on test, 9.76% on train and 19.53% out-of-time, with corresponding monthly event rates of 0.00482, 0.00806, 0.00852 and 0.01795. The out-of-time event rate is 2.1x the training rate. The training window closes at period 201912, so the out-of-time population sits in the 2020-2021 refinance wave, and the drift is economically explicable rather than anomalous. The defect is that it is entirely unquantified: the artifact store contains no PSI, no characteristic-stability statistic, and no correlation of score distribution against the training distribution, so there is no instrument that would detect the next such shift in production. This matters because the model's calibration error is itself regime-dependent — 5.1% over-prediction of the hazard in the fast regime versus 17.2% in the slow regime — so drift monitoring is not a formality here but the mechanism by which the known calibration weakness would be caught in flight. It should be recorded in the model's favour that discrimination survived this drift well (out-of-time AUC of 0.7846 actually exceeds test AUC of 0.7753); the finding concerns the absence of instrumentation and documentation, not a demonstrated failure under drift. Remediation: compute feature-level and score-level PSI for each split against train, declare amber/red thresholds, and embed the computation in the production run.

### F-004 · X1 scenario analysis · severity **medium**

The oldest loan-month in the training data has `f_loan_age` = 59 and the outermost age-spline knot is at 53, yet the published baseline hazard is tabulated past loan age 101. Beyond age 59 the curve is not estimated from data; it is the unconstrained tail of the outer spline segment, whose slope is set by a thin set of observations at the oldest supported ages. MSR valuation discounts servicing cash flows over a 360-month horizon, so the large majority of the projected life of the asset is priced off this extrapolated region. Two properties of the tail are concerning. It decays continuously and without bound from its peak of 0.003295 at age 43 rather than flattening to a floor, whereas real prepayment hazards on very seasoned collateral are floored by involuntary prepayment — default, curtailment and relocation — at roughly 4-6% CPR; a hazard that keeps falling overstates the duration of the servicing strip and over-values the MSR at long horizons, in the opposite direction to the vintage-holdout calibration error. And the assumption is nowhere documented as an assumption. The `run.projection` artifact exists but its contents were not supplied to this review, so the MSR value curve itself could not be tested for monotonicity or sign, and this finding concerns the hazard input to that projection rather than a demonstrated defect in the curve. Remediation: impose a floored or flat hazard beyond the supported age range, or refit on data containing seasoned loans; document the extrapolation explicitly; and re-run the projection under both the current and the floored tail, reporting the value difference.

### F-005 · M1 collinearity · severity **low**

The feature set contains a block of terms that are algebraic functions of one another. `f_note_rate`, `f_sato` (spread at origination, the note rate less the prevailing rate at origination), `f_incentive` (the note rate less the current market rate) and `f_rate_change_12m` all derive from the note rate and the market rate path, and `f_loan_age` and `f_burnout` are mechanically linked through cumulative in-the-money exposure. No VIF, condition number, or correlation matrix appears in the artifact store, so the degree of collinearity is not quantified and the threshold test for this defect class cannot formally be executed; this finding is therefore raised as a diagnostic gap at low severity rather than as a demonstrated breach. The practical consequence is limited to inference, not prediction: collinearity of this kind leaves AUC and calibration unaffected — and the observed performance is stable — but it makes individual coefficient magnitudes and signs unstable across refits and resamples. That matters here because prepayment models are routinely used for attribution, and an unstable split of explanatory weight between `f_incentive` and `f_sato` would make period-over-period attribution commentary unreliable. Remediation: publish VIFs and the design-matrix condition number; if elevated, retain the full feature set for prediction but state in the model documentation that individual coefficients are not to be interpreted causally or used for attribution.

Candidates raised and not promoted: none.

### Open items

No open item was recorded for this validation.

## 7. Ongoing monitoring recommendations

Monitoring should be run monthly on the production scoring population, with results reported to the model owner and escalated on breach.

**Calibration (monthly, primary).** Track actual-versus-predicted CPR in aggregate and the ratio of mean predicted to observed monthly hazard. Given the model's demonstrated behaviour, amber at a ratio outside [⟦unverified: 0.90⟧, ⟦unverified: 1.10⟧] and red outside [⟦unverified: 0.85⟧, ⟦unverified: 1.15⟧] — the vintage holdout result of ⟦unverified: 1.172⟧ would trip red today. Recompute the calibration slope quarterly on a rolling twelve-month window, amber outside [⟦unverified: 0.90⟧, ⟦unverified: 1.10⟧].

**Calibration by segment (quarterly).** The aggregate calibration hides the defect found here, because the model is well calibrated in aggregate and poorly calibrated on seasoned collateral. Report actual-versus-predicted CPR cut by loan age bucket (⟦unverified: 0⟧–⟦unverified: 12,⟧ ⟦unverified: 13⟧–⟦unverified: 36,⟧ ⟦unverified: 37⟧–⟦unverified: 60,⟧ ⟦unverified: 60⟧+), by incentive bucket (out-of-the-money, at-the-money, ⟦unverified: 50⟧bp+, ⟦unverified: 100⟧bp+ in-the-money), and by vintage. The ⟦unverified: 60⟧+ age bucket is both the least supported by training data and the most valuable, and should be reviewed explicitly every quarter.

**Discrimination (quarterly).** Track AUC, Gini and KS on a rolling twelve-month realised window. Against the ⟦unverified: 0.7718⟧–⟦unverified: 0.7883⟧ range established here, amber below ⟦unverified: 0.72⟧ and red below ⟦unverified: 0.70⟧. A fall in AUC with calibration intact points to feature degradation; a fall in calibration with AUC intact points to regime shift and is the more likely failure mode for this model.

**Drift (monthly).** PSI on the score and on each input feature against the training distribution, amber at ⟦unverified: 0.10⟧ and red at ⟦unverified: 0.25⟧. Given that the training window closes at ⟦unverified: 201912,⟧ feature drift on `f_incentive`, `f_note_rate` and `f_sato` should be expected to be persistently elevated and should trigger a documented review of whether the estimation window needs to roll forward rather than a mechanical alert.

**Data integrity (monthly).** Per-feature missingness and out-of-range counts against the training ranges recorded in the profile — note rate outside [⟦unverified: 2.29⟧, ⟦unverified: 6.38⟧], LTV outside [⟦unverified: 31,⟧ ⟦unverified: 97⟧], credit score outside [⟦unverified: 620,⟧ ⟦unverified: 820⟧], loan age above ⟦unverified: 59⟧ [[art:74d1953e:run.data_train]]. The loan-age check is the important one: it measures how much of the scored book sits in the extrapolated region of the baseline hazard, and that share should be reported alongside every valuation.

**Projection stability (quarterly).** Re-run the MSR value curve across the standard rate-shock grid and confirm monotonicity and correct sign; report the value delta attributable to model change versus rate-environment change.

**Annual review.** Full revalidation, including refit on data extended through the current period, re-execution of the outcomes and scenario analysis in this report, and confirmation that the findings above remain closed. Trigger an off-cycle review if any red threshold is breached for two consecutive months, if realised CPR moves outside the ⟦unverified: 5%⟧–⟦unverified: 20%⟧ range observed across the validation splits, or if the share of scored loans above age ⟦unverified: 59⟧ exceeds ⟦unverified: 25%⟧.

## Appendix A — Claims

Grounding precision 0.0000 before repair (0 of 212 claims verified; 136 unsupported, 62 dangling, 14 unattributed) and 0.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 0/34; conceptual_soundness 0/22; data_integrity 0/30; outcomes 0/55; sensitivity 0/14; findings 0/22; monitoring 0/35.

Developer claims: `plain_llm` runs no check over `package.yaml`'s declared claims See Appendix D.

Excluded numeric tokens (not claims): section_number (section 6); citation_hash (22858a09, 0b1995f4, 31ce3d08, dca79f2f); package_version (1.0); extractor_returned_excluded_token (1.0, 6, 4.0, 2.0).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | This report documents an independent validation of `msr_prep… | 1 | ratio |  |  | eq |  | unsupported |  |
| 2 | summary | This report documents an independent validation of `msr_prep… | 10 | months |  |  | eq | `[[art:22858a09:run.model_summary]]` | dangling |  |
| 3 | summary | This report documents an independent validation of `msr_prep… | 19 | months |  |  | eq | `[[art:22858a09:run.model_summary]]` | dangling |  |
| 4 | summary | This report documents an independent validation of `msr_prep… | 31 | months |  |  | eq | `[[art:22858a09:run.model_summary]]` | dangling |  |
| 5 | summary | This report documents an independent validation of `msr_prep… | 53 | months |  |  | eq | `[[art:22858a09:run.model_summary]]` | dangling |  |
| 6 | summary | \| train \| 36,013 \| 934 \| 0.00852 \| 0.7883 \| 0.9937 \| 9.76% \|… | 36013 | count | rows | train | eq |  | unsupported |  |
| 7 | summary | \| train \| 36,013 \| 934 \| 0.00852 \| 0.7883 \| 0.9937 \| 9.76% \|… | 934 | count | loans | train | eq |  | unsupported |  |
| 8 | summary | \| train \| 36,013 \| 934 \| 0.00852 \| 0.7883 \| 0.9937 \| 9.76% \|… | 0.00852 | ratio | event_rate | train | eq |  | unsupported |  |
| 9 | summary | \| train \| 36,013 \| 934 \| 0.00852 \| 0.7883 \| 0.9937 \| 9.76% \|… | 0.7883 | ratio | auc | train | eq |  | unsupported |  |
| 10 | summary | \| train \| 36,013 \| 934 \| 0.00852 \| 0.7883 \| 0.9937 \| 9.76% \|… | 0.9937 | ratio | calibration_slope | train | eq |  | unsupported |  |
| 11 | summary | \| train \| 36,013 \| 934 \| 0.00852 \| 0.7883 \| 0.9937 \| 9.76% \|… | 9.76 | percent | cpr_actual | train | eq |  | unsupported |  |
| 12 | summary | \| train \| 36,013 \| 934 \| 0.00852 \| 0.7883 \| 0.9937 \| 9.76% \|… | 9.66 | percent | cpr_predicted | train | eq |  | unsupported |  |
| 13 | summary | \| test \| 15,382 \| 400 \| 0.00806 \| 0.7753 \| 0.9365 \| 9.26% \|… | 15382 | count | rows | test | eq |  | unsupported |  |
| 14 | summary | \| test \| 15,382 \| 400 \| 0.00806 \| 0.7753 \| 0.9365 \| 9.26% \|… | 400 | count | loans | test | eq |  | unsupported |  |
| 15 | summary | \| test \| 15,382 \| 400 \| 0.00806 \| 0.7753 \| 0.9365 \| 9.26% \|… | 0.00806 | ratio | event_rate | test | eq |  | unsupported |  |
| 16 | summary | \| test \| 15,382 \| 400 \| 0.00806 \| 0.7753 \| 0.9365 \| 9.26% \|… | 0.7753 | ratio | auc | test | eq |  | unsupported |  |
| 17 | summary | \| test \| 15,382 \| 400 \| 0.00806 \| 0.7753 \| 0.9365 \| 9.26% \|… | 0.9365 | ratio | calibration_slope | test | eq |  | unsupported |  |
| 18 | summary | \| test \| 15,382 \| 400 \| 0.00806 \| 0.7753 \| 0.9365 \| 9.26% \|… | 9.26 | percent | cpr_actual | test | eq |  | unsupported |  |
| 19 | summary | \| test \| 15,382 \| 400 \| 0.00806 \| 0.7753 \| 0.9365 \| 9.26% \|… | 9.32 | percent | cpr_predicted | test | eq |  | unsupported |  |
| 20 | summary | \| vintage_holdout \| 32,177 \| 666 \| 0.00482 \| 0.7718 \| 0.8373… | 32177 | count | rows | vintage_holdout | eq |  | unsupported |  |
| 21 | summary | \| vintage_holdout \| 32,177 \| 666 \| 0.00482 \| 0.7718 \| 0.8373… | 666 | count | loans | vintage_holdout | eq |  | unsupported |  |
| 22 | summary | \| vintage_holdout \| 32,177 \| 666 \| 0.00482 \| 0.7718 \| 0.8373… | 0.00482 | ratio | event_rate | vintage_holdout | eq |  | unsupported |  |
| 23 | summary | \| vintage_holdout \| 32,177 \| 666 \| 0.00482 \| 0.7718 \| 0.8373… | 0.7718 | ratio | auc | vintage_holdout | eq |  | unsupported |  |
| 24 | summary | \| vintage_holdout \| 32,177 \| 666 \| 0.00482 \| 0.7718 \| 0.8373… | 0.8373 | ratio | calibration_slope | vintage_holdout | eq |  | unsupported |  |
| 25 | summary | \| vintage_holdout \| 32,177 \| 666 \| 0.00482 \| 0.7718 \| 0.8373… | 5.63 | percent | cpr_actual | vintage_holdout | eq |  | unsupported |  |
| 26 | summary | \| vintage_holdout \| 32,177 \| 666 \| 0.00482 \| 0.7718 \| 0.8373… | 6.57 | percent | cpr_predicted | vintage_holdout | eq |  | unsupported |  |
| 27 | summary | \| out_of_time \| 12,257 \| 515 \| 0.01795 \| 0.7846 \| 0.9969 \| 1… | 12257 | count | rows | out_of_time | eq |  | unsupported |  |
| 28 | summary | \| out_of_time \| 12,257 \| 515 \| 0.01795 \| 0.7846 \| 0.9969 \| 1… | 515 | count | loans | out_of_time | eq |  | unsupported |  |
| 29 | summary | \| out_of_time \| 12,257 \| 515 \| 0.01795 \| 0.7846 \| 0.9969 \| 1… | 0.01795 | ratio | event_rate | out_of_time | eq |  | unsupported |  |
| 30 | summary | \| out_of_time \| 12,257 \| 515 \| 0.01795 \| 0.7846 \| 0.9969 \| 1… | 0.7846 | ratio | auc | out_of_time | eq |  | unsupported |  |
| 31 | summary | \| out_of_time \| 12,257 \| 515 \| 0.01795 \| 0.7846 \| 0.9969 \| 1… | 0.9969 | ratio | calibration_slope | out_of_time | eq |  | unsupported |  |
| 32 | summary | \| out_of_time \| 12,257 \| 515 \| 0.01795 \| 0.7846 \| 0.9969 \| 1… | 19.53 | percent | cpr_actual | out_of_time | eq |  | unsupported |  |
| 33 | summary | \| out_of_time \| 12,257 \| 515 \| 0.01795 \| 0.7846 \| 0.9969 \| 1… | 20.43 | percent | cpr_predicted | out_of_time | eq |  | unsupported |  |
| 34 | summary | Overall conclusion: discrimination is adequate and stable ac… | 17 | percent |  | vintage_holdout | eq |  | unsupported |  |
| 35 | conceptual_soundness | The discrete-time hazard formulation is appropriate for prep… | 36013 | count | loan_months | train | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 36 | conceptual_soundness | The discrete-time hazard formulation is appropriate for prep… | 934 | count | loans | train | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 37 | conceptual_soundness | **Feature timing is clean.** The manifest declares five feat… | 0.77 | ratio | auc |  | eq |  | unsupported |  |
| 38 | conceptual_soundness | **Feature timing is clean.** The manifest declares five feat… | 0.79 | ratio | auc |  | eq |  | unsupported |  |
| 39 | conceptual_soundness | **Baseline hazard shape.** The estimated baseline rises mono… | 0.000885 | ratio | baseline_hazard |  | eq | `[[art:22858a09:run.model_summary#baseline_hazard]]` | dangling |  |
| 40 | conceptual_soundness | **Baseline hazard shape.** The estimated baseline rises mono… | 0 | months | age |  | eq | `[[art:22858a09:run.model_summary#baseline_hazard]]` | dangling |  |
| 41 | conceptual_soundness | **Baseline hazard shape.** The estimated baseline rises mono… | 0.003295 | ratio | baseline_hazard |  | eq | `[[art:22858a09:run.model_summary#baseline_hazard]]` | dangling |  |
| 42 | conceptual_soundness | **Baseline hazard shape.** The estimated baseline rises mono… | 43 | months | age |  | eq | `[[art:22858a09:run.model_summary#baseline_hazard]]` | dangling |  |
| 43 | conceptual_soundness | **Extrapolation beyond support is the principal conceptual w… | 59 | months | loan_age | train | eq | `[[art:74d1953e:run.data_train]]` | dangling |  |
| 44 | conceptual_soundness | **Extrapolation beyond support is the principal conceptual w… | 53 | months | age_spline_knots |  | eq | `[[art:22858a09:run.model_summary#age_spline_knots]]` | dangling |  |
| 45 | conceptual_soundness | **Extrapolation beyond support is the principal conceptual w… | 101 | months | age |  | eq |  | unsupported |  |
| 46 | conceptual_soundness | **Extrapolation beyond support is the principal conceptual w… | 59 | months | age |  | eq |  | unsupported |  |
| 47 | conceptual_soundness | **Extrapolation beyond support is the principal conceptual w… | 360 | months |  |  | eq |  | unsupported |  |
| 48 | conceptual_soundness | **Extrapolation beyond support is the principal conceptual w… | 1 | count |  |  | eq |  | unattributed |  |
| 49 | conceptual_soundness | **Population coverage.** The training data spans note rates… | 2.29 | percent | note_rate | train | eq | `[[art:74d1953e:run.data_train]]` | dangling |  |
| 50 | conceptual_soundness | **Population coverage.** The training data spans note rates… | 6.38 | percent | note_rate | train | eq | `[[art:74d1953e:run.data_train]]` | dangling |  |
| 51 | conceptual_soundness | **Population coverage.** The training data spans note rates… | 31 | ratio | original_ltv | train | eq | `[[art:74d1953e:run.data_train]]` | dangling |  |
| 52 | conceptual_soundness | **Population coverage.** The training data spans note rates… | 97 | ratio | original_ltv | train | eq | `[[art:74d1953e:run.data_train]]` | dangling |  |
| 53 | conceptual_soundness | **Population coverage.** The training data spans note rates… | 620 | ratio | credit_score | train | eq | `[[art:74d1953e:run.data_train]]` | dangling |  |
| 54 | conceptual_soundness | **Population coverage.** The training data spans note rates… | 820 | ratio | credit_score | train | eq | `[[art:74d1953e:run.data_train]]` | dangling |  |
| 55 | conceptual_soundness | **Population coverage.** The training data spans note rates… | 620 | ratio | credit_score | train | eq |  | unsupported |  |
| 56 | conceptual_soundness | **Population coverage.** The training data spans note rates… | 97 | ratio | original_ltv | train | eq |  | unsupported |  |
| 57 | data_integrity | **Split construction reconciles and shows no contamination.*… | 934 | count | n_loans | train | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 58 | data_integrity | **Split construction reconciles and shows no contamination.*… | 400 | count | n_loans | test | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 59 | data_integrity | **Split construction reconciles and shows no contamination.*… | 1 | ratio | loan_id_min | train | eq | `[[art:74d1953e:run.data_train]]` | dangling |  |
| 60 | data_integrity | **Split construction reconciles and shows no contamination.*… | 1334 | ratio | loan_id_max | train | eq | `[[art:74d1953e:run.data_train]]` | dangling |  |
| 61 | data_integrity | **Split construction reconciles and shows no contamination.*… | 373 | ratio | loan_id_std | train | eq | `[[art:74d1953e:run.data_train]]` | dangling |  |
| 62 | data_integrity | **Split construction reconciles and shows no contamination.*… | 934 | count | n_loans | train | eq |  | unsupported |  |
| 63 | data_integrity | **Split construction reconciles and shows no contamination.*… | 400 | count | n_loans | test | eq |  | unsupported |  |
| 64 | data_integrity | **Split construction reconciles and shows no contamination.*… | 1334 | count | n_loans |  | eq |  | unsupported |  |
| 65 | data_integrity | **Split construction reconciles and shows no contamination.*… | 1334 | count | n_loans |  | eq |  | unsupported |  |
| 66 | data_integrity | One consequence of this design should be understood by users… | 201402 | ratio | period_min | train | eq | `[[art:74d1953e:run.data_train]]` | dangling |  |
| 67 | data_integrity | One consequence of this design should be understood by users… | 201912 | ratio | period_max | train | eq | `[[art:74d1953e:run.data_train]]` | dangling |  |
| 68 | data_integrity | One consequence of this design should be understood by users… | 12257 | count | n_rows | out_of_time | eq |  | unsupported |  |
| 69 | data_integrity | One consequence of this design should be understood by users… | 515 | count | n_loans | out_of_time | eq |  | unsupported |  |
| 70 | data_integrity | One consequence of this design should be understood by users… | 220 | count | n_events | out_of_time | eq |  | unsupported |  |
| 71 | data_integrity | **Two declared model inputs are absent from the training dat… | 1 | count |  |  | eq |  | unattributed |  |
| 72 | data_integrity | **Missingness.** Every column in the training profile report… | 0 | ratio | missing | train | eq | `[[art:74d1953e:run.data_train]]` | dangling |  |
| 73 | data_integrity | **Drift.** No PSI or characteristic-stability statistic exis… | 19.53 | percent | cpr | out_of_time | eq | `[[art:31ce3d08:run.metrics]]` | dangling |  |
| 74 | data_integrity | **Drift.** No PSI or characteristic-stability statistic exis… | 9.76 | percent | cpr | train | eq | `[[art:31ce3d08:run.metrics]]` | dangling |  |
| 75 | data_integrity | **Drift.** No PSI or characteristic-stability statistic exis… | 2.1 | ratio | cpr |  | ratio | `[[art:31ce3d08:run.metrics]] [[art:dca79f2f:run.splits]]` | dangling |  |
| 76 | data_integrity | **Drift.** No PSI or characteristic-stability statistic exis… | 0.01795 | ratio | event_rate | out_of_time | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 77 | data_integrity | **Drift.** No PSI or characteristic-stability statistic exis… | 0.00852 | ratio | event_rate | train | eq | `[[art:dca79f2f:run.splits]]` | dangling |  |
| 78 | data_integrity | **Drift.** No PSI or characteristic-stability statistic exis… | 5.63 | percent | cpr | vintage_holdout | eq |  | unsupported |  |
| 79 | data_integrity | **Drift.** No PSI or characteristic-stability statistic exis… | 0.00482 | ratio | event_rate | vintage_holdout | eq |  | unsupported |  |
| 80 | data_integrity | **Drift.** No PSI or characteristic-stability statistic exis… | 0.57 | ratio | event_rate |  | ratio |  | unsupported |  |
| 81 | data_integrity | **Drift.** No PSI or characteristic-stability statistic exis… | 201912 | ratio | period_max | train | eq |  | unsupported |  |
| 82 | data_integrity | **Drift.** No PSI or characteristic-stability statistic exis… | 2020 | ratio |  | out_of_time | eq |  | unsupported |  |
| 83 | data_integrity | **Drift.** No PSI or characteristic-stability statistic exis… | 2021 | ratio |  | out_of_time | eq |  | unsupported |  |
| 84 | data_integrity | **Drift.** No PSI or characteristic-stability statistic exis… | 3.5 | ratio | cpr |  | ratio |  | unsupported |  |
| 85 | data_integrity | **Drift.** No PSI or characteristic-stability statistic exis… | 1 | count |  |  | eq |  | unattributed |  |
| 86 | data_integrity | **Collinearity.** No VIF, condition number, or correlation m… | 1 | count |  |  | eq |  | unattributed |  |
| 87 | outcomes | **Discrimination is adequate and notably stable.** AUC is 0.… | 0.7883 | ratio | auc | train | eq | `[[art:31ce3d08:run.metrics]]` | dangling |  |
| 88 | outcomes | **Discrimination is adequate and notably stable.** AUC is 0.… | 0.7753 | ratio | auc | test | eq | `[[art:31ce3d08:run.metrics]]` | dangling |  |
| 89 | outcomes | **Discrimination is adequate and notably stable.** AUC is 0.… | 0.7718 | ratio | auc | vintage_holdout | eq | `[[art:31ce3d08:run.metrics]]` | dangling |  |
| 90 | outcomes | **Discrimination is adequate and notably stable.** AUC is 0.… | 0.7846 | ratio | auc | out_of_time | eq | `[[art:31ce3d08:run.metrics]]` | dangling |  |
| 91 | outcomes | **Discrimination is adequate and notably stable.** AUC is 0.… | 0.0131 | ratio | delta_auc |  | delta |  | unsupported |  |
| 92 | outcomes | **Discrimination is adequate and notably stable.** AUC is 0.… | 0.0165 | ratio | delta_auc |  | delta |  | unsupported |  |
| 93 | outcomes | **Discrimination is adequate and notably stable.** AUC is 0.… | 0.05 | ratio | delta_auc |  | eq |  | unsupported |  |
| 94 | outcomes | **Discrimination is adequate and notably stable.** AUC is 0.… | 0.577 | ratio | gini | train | eq |  | unsupported |  |
| 95 | outcomes | **Discrimination is adequate and notably stable.** AUC is 0.… | 0.551 | ratio | gini | test | eq |  | unsupported |  |
| 96 | outcomes | **Discrimination is adequate and notably stable.** AUC is 0.… | 0.544 | ratio | gini | vintage_holdout | eq |  | unsupported |  |
| 97 | outcomes | **Discrimination is adequate and notably stable.** AUC is 0.… | 0.569 | ratio | gini | out_of_time | eq |  | unsupported |  |
| 98 | outcomes | **Discrimination is adequate and notably stable.** AUC is 0.… | 0.456 | ratio | ks | train | eq |  | unsupported |  |
| 99 | outcomes | **Discrimination is adequate and notably stable.** AUC is 0.… | 0.416 | ratio | ks | test | eq |  | unsupported |  |
| 100 | outcomes | **Discrimination is adequate and notably stable.** AUC is 0.… | 0.452 | ratio | ks | vintage_holdout | eq |  | unsupported |  |
| 101 | outcomes | **Discrimination is adequate and notably stable.** AUC is 0.… | 0.432 | ratio | ks | out_of_time | eq |  | unsupported |  |
| 102 | outcomes | **Discrimination is adequate and notably stable.** AUC is 0.… | 2014 | ratio |  |  | eq |  | unsupported |  |
| 103 | outcomes | **Discrimination is adequate and notably stable.** AUC is 0.… | 2019 | ratio |  |  | eq |  | unsupported |  |
| 104 | outcomes | **Discrimination is adequate and notably stable.** AUC is 0.… | 0.0165 | ratio | delta_auc |  | delta |  | unsupported |  |
| 105 | outcomes | \| train \| 0.008427 \| 0.008525 \| 0.989 \| 0.9937 \| | 0.008427 | ratio | mean_predicted | train | eq |  | unsupported |  |
| 106 | outcomes | \| train \| 0.008427 \| 0.008525 \| 0.989 \| 0.9937 \| | 0.008525 | ratio | event_rate | train | eq |  | unsupported |  |
| 107 | outcomes | \| train \| 0.008427 \| 0.008525 \| 0.989 \| 0.9937 \| | 0.989 | ratio | calibration_ratio | train | eq |  | unsupported |  |
| 108 | outcomes | \| train \| 0.008427 \| 0.008525 \| 0.989 \| 0.9937 \| | 0.9937 | ratio | calibration_slope | train | eq |  | unsupported |  |
| 109 | outcomes | \| test \| 0.008116 \| 0.008061 \| 1.007 \| 0.9365 \| | 0.008116 | ratio | mean_predicted | test | eq |  | unsupported |  |
| 110 | outcomes | \| test \| 0.008116 \| 0.008061 \| 1.007 \| 0.9365 \| | 0.008061 | ratio | event_rate | test | eq |  | unsupported |  |
| 111 | outcomes | \| test \| 0.008116 \| 0.008061 \| 1.007 \| 0.9365 \| | 1.007 | ratio | calibration_ratio | test | eq |  | unsupported |  |
| 112 | outcomes | \| test \| 0.008116 \| 0.008061 \| 1.007 \| 0.9365 \| | 0.9365 | ratio | calibration_slope | test | eq |  | unsupported |  |
| 113 | outcomes | \| out_of_time \| 0.018866 \| 0.017949 \| 1.051 \| 0.9969 \| | 0.018866 | ratio | mean_predicted | out_of_time | eq |  | unsupported |  |
| 114 | outcomes | \| out_of_time \| 0.018866 \| 0.017949 \| 1.051 \| 0.9969 \| | 0.017949 | ratio | event_rate | out_of_time | eq |  | unsupported |  |
| 115 | outcomes | \| out_of_time \| 0.018866 \| 0.017949 \| 1.051 \| 0.9969 \| | 1.051 | ratio | calibration_ratio | out_of_time | eq |  | unsupported |  |
| 116 | outcomes | \| out_of_time \| 0.018866 \| 0.017949 \| 1.051 \| 0.9969 \| | 0.9969 | ratio | calibration_slope | out_of_time | eq |  | unsupported |  |
| 117 | outcomes | \| vintage_holdout \| 0.005647 \| 0.004817 \| **1.172** \| **0.83… | 0.005647 | ratio | mean_predicted | vintage_holdout | eq |  | unsupported |  |
| 118 | outcomes | \| vintage_holdout \| 0.005647 \| 0.004817 \| **1.172** \| **0.83… | 0.004817 | ratio | event_rate | vintage_holdout | eq |  | unsupported |  |
| 119 | outcomes | \| vintage_holdout \| 0.005647 \| 0.004817 \| **1.172** \| **0.83… | 1.172 | ratio | calibration_ratio | vintage_holdout | eq |  | unsupported |  |
| 120 | outcomes | \| vintage_holdout \| 0.005647 \| 0.004817 \| **1.172** \| **0.83… | 0.8373 | ratio | calibration_slope | vintage_holdout | eq |  | unsupported |  |
| 121 | outcomes | The vintage holdout breaches both limbs of a standard calibr… | 0.8373 | ratio | calibration_slope | vintage_holdout | eq | `[[art:31ce3d08:run.metrics]]` | dangling |  |
| 122 | outcomes | The vintage holdout breaches both limbs of a standard calibr… | 0.9 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 123 | outcomes | The vintage holdout breaches both limbs of a standard calibr… | 1.1 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 124 | outcomes | The vintage holdout breaches both limbs of a standard calibr… | 0.85 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 125 | outcomes | The vintage holdout breaches both limbs of a standard calibr… | 1.15 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 126 | outcomes | The vintage holdout breaches both limbs of a standard calibr… | 17.2 | percent | calibration_ratio | vintage_holdout | eq | `[[art:31ce3d08:run.metrics]]` | dangling |  |
| 127 | outcomes | The vintage holdout breaches both limbs of a standard calibr… | 6.57 | percent | cpr_predicted | vintage_holdout | eq | `[[art:31ce3d08:run.metrics]]` | dangling |  |
| 128 | outcomes | The vintage holdout breaches both limbs of a standard calibr… | 5.63 | percent | cpr_actual | vintage_holdout | eq | `[[art:31ce3d08:run.metrics]]` | dangling |  |
| 129 | outcomes | The vintage holdout breaches both limbs of a standard calibr… | 16.7 | percent | cpr_error | vintage_holdout | eq | `[[art:31ce3d08:run.metrics]]` | dangling |  |
| 130 | outcomes | The vintage holdout breaches both limbs of a standard calibr… | 1 | count |  |  | eq |  | unattributed |  |
| 131 | outcomes | The test slope of 0.9365 sits inside a [0.90, 1.10] band and… | 0.9365 | ratio | calibration_slope | test | eq |  | unsupported |  |
| 132 | outcomes | The test slope of 0.9365 sits inside a [0.90, 1.10] band and… | 0.9 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 133 | outcomes | The test slope of 0.9365 sits inside a [0.90, 1.10] band and… | 1.1 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 134 | outcomes | The test slope of 0.9365 sits inside a [0.90, 1.10] band and… | 1 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 135 | outcomes | **Statistical precision.** Event counts implied by the rates… | 307 | count | event_count | train | eq |  | unsupported |  |
| 136 | outcomes | **Statistical precision.** Event counts implied by the rates… | 124 | count | event_count | test | eq |  | unsupported |  |
| 137 | outcomes | **Statistical precision.** Event counts implied by the rates… | 155 | count | event_count | vintage_holdout | eq |  | unsupported |  |
| 138 | outcomes | **Statistical precision.** Event counts implied by the rates… | 220 | count | event_count | out_of_time | eq |  | unsupported |  |
| 139 | outcomes | **Statistical precision.** Event counts implied by the rates… | 307 | count | event_count | train | eq |  | unsupported |  |
| 140 | outcomes | **Statistical precision.** Event counts implied by the rates… | 934 | count | n_loans |  | eq |  | unsupported |  |
| 141 | outcomes | **Statistical precision.** Event counts implied by the rates… | 36013 | count | n_rows |  | eq |  | unsupported |  |
| 142 | sensitivity | What could be assessed is the sensitivity of the valuation t… | 59 | months | baseline_hazard |  | eq | `[[art:22858a09:run.model_summary#baseline_hazard]]` | dangling |  |
| 143 | sensitivity | What could be assessed is the sensitivity of the valuation t… | 360 | months |  |  | eq |  | unsupported |  |
| 144 | sensitivity | What could be assessed is the sensitivity of the valuation t… | 80 | percent |  |  | eq |  | unsupported |  |
| 145 | sensitivity | What could be assessed is the sensitivity of the valuation t… | 4 | percent |  |  | eq |  | unsupported |  |
| 146 | sensitivity | What could be assessed is the sensitivity of the valuation t… | 6 | percent |  |  | eq |  | unsupported |  |
| 147 | sensitivity | What could be assessed is the sensitivity of the valuation t… | 31 | months |  |  | eq |  | unsupported |  |
| 148 | sensitivity | What could be assessed is the sensitivity of the valuation t… | 53 | months |  |  | eq |  | unsupported |  |
| 149 | sensitivity | The empirical regime range gives a natural, evidence-based s… | 5.63 | percent |  |  | eq | `[[art:31ce3d08:run.metrics]]` | dangling |  |
| 150 | sensitivity | The empirical regime range gives a natural, evidence-based s… | 9.26 | percent |  |  | eq | `[[art:31ce3d08:run.metrics]]` | dangling |  |
| 151 | sensitivity | The empirical regime range gives a natural, evidence-based s… | 9.76 | percent |  |  | eq | `[[art:31ce3d08:run.metrics]]` | dangling |  |
| 152 | sensitivity | The empirical regime range gives a natural, evidence-based s… | 19.53 | percent |  |  | eq | `[[art:31ce3d08:run.metrics]]` | dangling |  |
| 153 | sensitivity | The empirical regime range gives a natural, evidence-based s… | 3.5 | ratio |  |  | eq |  | unsupported |  |
| 154 | sensitivity | The empirical regime range gives a natural, evidence-based s… | 5.1 | percent |  |  | eq |  | unsupported |  |
| 155 | sensitivity | The empirical regime range gives a natural, evidence-based s… | 17.2 | percent |  |  | eq |  | unsupported |  |
| 156 | findings | **D1-01 (high) — Declared features absent from the training… | 1 | count |  |  | eq |  | unattributed |  |
| 157 | findings | **C1-01 (medium) — Vintage holdout calibration breach, over-… | 1 | count |  |  | eq |  | unattributed |  |
| 158 | findings | **C1-01 (medium) — Vintage holdout calibration breach, over-… | 17 | percent | event_rate | vintage_holdout | eq |  | unsupported |  |
| 159 | findings | **C1-01 (medium) — Vintage holdout calibration breach, over-… | 0.8373 | ratio | calibration_slope | vintage_holdout | eq | `[[art:31ce3d08:run.metrics]]` | dangling |  |
| 160 | findings | **C1-01 (medium) — Vintage holdout calibration breach, over-… | 1.172 | ratio | event_rate | vintage_holdout | eq | `[[art:31ce3d08:run.metrics]]` | dangling |  |
| 161 | findings | **C1-01 (medium) — Vintage holdout calibration breach, over-… | 6.57 | percent | event_rate | vintage_holdout | eq | `[[art:31ce3d08:run.metrics]]` | dangling |  |
| 162 | findings | **C1-01 (medium) — Vintage holdout calibration breach, over-… | 5.63 | percent | event_rate | vintage_holdout | eq | `[[art:31ce3d08:run.metrics]]` | dangling |  |
| 163 | findings | **C1-01 (medium) — Vintage holdout calibration breach, over-… | 16.7 | percent | event_rate | vintage_holdout | eq |  | unsupported |  |
| 164 | findings | **S1-01 (medium) — Unquantified regime drift across splits.*… | 1 | count |  |  | eq |  | unattributed |  |
| 165 | findings | **S1-01 (medium) — Unquantified regime drift across splits.*… | 5.63 | percent | event_rate |  | eq | `[[art:31ce3d08:run.metrics]]` | dangling |  |
| 166 | findings | **S1-01 (medium) — Unquantified regime drift across splits.*… | 19.53 | percent | event_rate |  | eq | `[[art:31ce3d08:run.metrics]]` | dangling |  |
| 167 | findings | **S1-01 (medium) — Unquantified regime drift across splits.*… | 2.1 | ratio | event_rate | out_of_time | ratio | `[[art:31ce3d08:run.metrics]] [[art:dca79f2f:run.splits]]` | dangling |  |
| 168 | findings | **X1-01 (medium) — Baseline hazard extrapolated far beyond t… | 1 | count |  |  | eq |  | unattributed |  |
| 169 | findings | **X1-01 (medium) — Baseline hazard extrapolated far beyond t… | 101 | months |  |  | eq | `[[art:44b1d458:run.projection]]` | dangling |  |
| 170 | findings | **X1-01 (medium) — Baseline hazard extrapolated far beyond t… | 59 | months |  | train | eq | `[[art:74d1953e:run.data_train]]` | dangling |  |
| 171 | findings | **X1-01 (medium) — Baseline hazard extrapolated far beyond t… | 53 | months |  |  | eq | `[[art:22858a09:run.model_summary]]` | dangling |  |
| 172 | findings | **M1-01 (low) — Collinear rate-derived features with no diag… | 1 | count |  |  | eq |  | unattributed |  |
| 173 | findings | **Approval position.** Given clean leakage and contamination… | 3.5 | ratio | event_rate |  | eq |  | unsupported |  |
| 174 | findings | **Approval position.** Given clean leakage and contamination… | 1 | count |  |  | eq |  | unattributed |  |
| 175 | findings | **Approval position.** Given clean leakage and contamination… | 1 | count |  |  | eq |  | unattributed |  |
| 176 | findings | **Approval position.** Given clean leakage and contamination… | 1 | count |  |  | eq |  | unattributed |  |
| 177 | findings | **Approval position.** Given clean leakage and contamination… | 1 | count |  |  | eq |  | unattributed |  |
| 178 | monitoring | **Calibration (monthly, primary).** Track actual-versus-pred… | 0.9 | ratio | calibration_ratio |  | eq |  | unsupported |  |
| 179 | monitoring | **Calibration (monthly, primary).** Track actual-versus-pred… | 1.1 | ratio | calibration_ratio |  | eq |  | unsupported |  |
| 180 | monitoring | **Calibration (monthly, primary).** Track actual-versus-pred… | 0.85 | ratio | calibration_ratio |  | eq |  | unsupported |  |
| 181 | monitoring | **Calibration (monthly, primary).** Track actual-versus-pred… | 1.15 | ratio | calibration_ratio |  | eq |  | unsupported |  |
| 182 | monitoring | **Calibration (monthly, primary).** Track actual-versus-pred… | 1.172 | ratio | calibration_ratio | vintage_holdout | eq |  | unsupported |  |
| 183 | monitoring | **Calibration (monthly, primary).** Track actual-versus-pred… | 0.9 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 184 | monitoring | **Calibration (monthly, primary).** Track actual-versus-pred… | 1.1 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 185 | monitoring | **Calibration by segment (quarterly).** The aggregate calibr… | 0 | months | loan_age |  | eq |  | unsupported |  |
| 186 | monitoring | **Calibration by segment (quarterly).** The aggregate calibr… | 12 | months | loan_age |  | eq |  | unsupported |  |
| 187 | monitoring | **Calibration by segment (quarterly).** The aggregate calibr… | 13 | months | loan_age |  | eq |  | unsupported |  |
| 188 | monitoring | **Calibration by segment (quarterly).** The aggregate calibr… | 36 | months | loan_age |  | eq |  | unsupported |  |
| 189 | monitoring | **Calibration by segment (quarterly).** The aggregate calibr… | 37 | months | loan_age |  | eq |  | unsupported |  |
| 190 | monitoring | **Calibration by segment (quarterly).** The aggregate calibr… | 60 | months | loan_age |  | eq |  | unsupported |  |
| 191 | monitoring | **Calibration by segment (quarterly).** The aggregate calibr… | 60 | months | loan_age |  | eq |  | unsupported |  |
| 192 | monitoring | **Calibration by segment (quarterly).** The aggregate calibr… | 50 | bp | incentive |  | eq |  | unsupported |  |
| 193 | monitoring | **Calibration by segment (quarterly).** The aggregate calibr… | 100 | bp | incentive |  | eq |  | unsupported |  |
| 194 | monitoring | **Calibration by segment (quarterly).** The aggregate calibr… | 60 | months | loan_age |  | eq |  | unsupported |  |
| 195 | monitoring | **Discrimination (quarterly).** Track AUC, Gini and KS on a… | 0.7718 | ratio | auc |  | eq |  | unsupported |  |
| 196 | monitoring | **Discrimination (quarterly).** Track AUC, Gini and KS on a… | 0.7883 | ratio | auc |  | eq |  | unsupported |  |
| 197 | monitoring | **Discrimination (quarterly).** Track AUC, Gini and KS on a… | 0.72 | ratio | auc |  | eq |  | unsupported |  |
| 198 | monitoring | **Discrimination (quarterly).** Track AUC, Gini and KS on a… | 0.7 | ratio | auc |  | eq |  | unsupported |  |
| 199 | monitoring | **Drift (monthly).** PSI on the score and on each input feat… | 0.1 | ratio | psi |  | eq |  | unsupported |  |
| 200 | monitoring | **Drift (monthly).** PSI on the score and on each input feat… | 0.25 | ratio | psi |  | eq |  | unsupported |  |
| 201 | monitoring | **Drift (monthly).** PSI on the score and on each input feat… | 201912 | ratio |  | train | eq |  | unsupported |  |
| 202 | monitoring | **Data integrity (monthly).** Per-feature missingness and ou… | 2.29 | ratio | note_rate | train | eq | `[[art:74d1953e:run.data_train]]` | dangling |  |
| 203 | monitoring | **Data integrity (monthly).** Per-feature missingness and ou… | 6.38 | ratio | note_rate | train | eq | `[[art:74d1953e:run.data_train]]` | dangling |  |
| 204 | monitoring | **Data integrity (monthly).** Per-feature missingness and ou… | 31 | ratio | ltv | train | eq | `[[art:74d1953e:run.data_train]]` | dangling |  |
| 205 | monitoring | **Data integrity (monthly).** Per-feature missingness and ou… | 97 | ratio | ltv | train | eq | `[[art:74d1953e:run.data_train]]` | dangling |  |
| 206 | monitoring | **Data integrity (monthly).** Per-feature missingness and ou… | 620 | ratio | credit_score | train | eq | `[[art:74d1953e:run.data_train]]` | dangling |  |
| 207 | monitoring | **Data integrity (monthly).** Per-feature missingness and ou… | 820 | ratio | credit_score | train | eq | `[[art:74d1953e:run.data_train]]` | dangling |  |
| 208 | monitoring | **Data integrity (monthly).** Per-feature missingness and ou… | 59 | months | loan_age | train | eq | `[[art:74d1953e:run.data_train]]` | dangling |  |
| 209 | monitoring | **Annual review.** Full revalidation, including refit on dat… | 5 | percent | cpr |  | eq |  | unsupported |  |
| 210 | monitoring | **Annual review.** Full revalidation, including refit on dat… | 20 | percent | cpr |  | eq |  | unsupported |  |
| 211 | monitoring | **Annual review.** Full revalidation, including refit on dat… | 59 | months | loan_age |  | eq |  | unsupported |  |
| 212 | monitoring | **Annual review.** Full revalidation, including refit on dat… | 25 | percent | share_above_age_59 |  | eq |  | unsupported |  |

## Appendix B — Artifact index

The store holds 19 artifacts; the 8 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `run.data_out_of_time` | `049d2ab6` | table | table, 12257 rows | the subject's data_out_of_time.csv |
| `run.data_train` | `74d1953e` | table | table, 36013 rows | the subject's data_train.csv |
| `run.features` | `0b1995f4` | json | json | the subject's features.json |
| `run.metrics` | `31ce3d08` | json | json | the subject's metrics.json |
| `run.model_summary` | `22858a09` | json | json | the subject's model_summary.json |
| `run.predictions_vintage_holdout` | `632eda50` | table | table, 32177 rows | the subject's predictions_vintage_holdout.csv |
| `run.projection` | `44b1d458` | json | json | the subject's projection.json |
| `run.splits` | `dca79f2f` | json | json | the subject's splits.json |

## Appendix C — Run trace summary

| quantity | value |
|---|---|
| tool calls | 1 (run_model 1) |
| plan steps (bounded loop) | 0 |
| LLM calls | 8 (plain_llm 1, extract 7) |
| re-asks | 0 |
| repair rounds | 0 |
| tokens in / out | 65,256 / 46,263 |
| notional cost (USD) | 1.7985 |
| wall-clock (s) | 540.03 |
| subject run (s) | 2.60 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | msr_prepayment-plain_llm-20260918T075124Z-986f3824 |

## Appendix D — Not checked

| item | reason |
|---|---|
| `check_stability` (R1) | this configuration runs no checks |
| `run_scenarios` (X1) | this configuration runs no checks |
| developer claims (T1, claim channel) | `plain_llm` runs no check over `package.yaml`'s declared claims |
| developer documentation | package has no `docs/` directory |
| data manifest | not verified: the run read no data directory |
| every check of spec 3.7 but `run_model` | `plain_llm` runs the subject and one model call, by design |
