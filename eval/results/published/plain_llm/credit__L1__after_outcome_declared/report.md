---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: plain_llm
model: claude-opus-5[1m]
run_id: credit_default-plain_llm-20260918T083124Z-6e98ce62
data_mode: synthetic
synthetic_n: 5000
grounding_precision_pre: 0.0000
grounding_precision_post: 0.0000
n_claims: 104
n_findings_by_severity: {high: 1, medium: 1, low: 1, info: 0}
generated: "2026-09-18T08:31:24Z"
illustrative: false
---

# Validation report — `credit_default` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `credit_default` v1.0 | `plain_llm` | claude-opus-5[1m] | synthetic, n = 5000 | 0.0000 → 0.0000 | 1 / 1 / 1 / 0 |
<!-- quaestor:renderer:end -->

This report documents the independent validation of package `credit_default`, version 1.0, a binary classification model estimating the probability that a revolving credit client defaults in the following month. The subject is a standardised logistic regression with an intercept of ⟦unverified: -6.1028⟧ and eleven retained coefficients, fitted on ⟦unverified: 3,500⟧ training rows and evaluated on ⟦unverified: 1,500⟧ held-out test rows [[art:e4b3fd0e:run.model_summary]] [[art:3b6b0a38:run.splits]].

Scope covers conceptual soundness, data integrity and drift, outcomes analysis, and such sensitivity and scenario work as the submitted artifact set supports. The validation was performed against the developer-submitted artifacts only: metrics, model summary, feature inventory, split manifest, prediction tables, and the raw training-split profile [[art:65d0d3f7:run.metrics]] [[art:7276ca89:run.features]] [[art:1eb04cca:run.predictions_test]] [[art:ebd7a887:run.predictions_train]]. No re-fit, no challenger benchmark, no out-of-time sample, and no PSI computation were available in the submission, and those gaps are carried into the recommendations rather than treated as passes.

**Conclusion: the model is not fit for use as submitted.** The headline finding is target leakage: the feature `pay_amt_next` is declared by the developers themselves as observed `after_outcome`, and it carries by far the largest coefficient in the model. Every reported performance figure is therefore uninterpretable as an estimate of forward-looking discrimination. A secondary finding concerns severe multicollinearity in the bill/utilisation feature family, which the developers partially remediated but which still shows through in the surviving coefficient signs.

## 2. Conceptual soundness

The choice of a standardised logistic regression for a monthly default flag is appropriate and defensible. It is interpretable, its coefficients map directly to log-odds contributions, and a linear-in-log-odds structure is the accepted default for this exposure class. Standardisation is declared (`standardised: true`), so coefficient magnitudes are comparable across features [[art:e4b3fd0e:run.model_summary]]. `class_weight` is null, which is acceptable at a ⟦unverified: 22.5%⟧ event rate — the base rate is not so rare as to require reweighting, and the fitted mean predicted probability on train (⟦unverified: 0.22455⟧) reproduces the observed train event rate (⟦unverified: 0.22457⟧) almost exactly, as unweighted maximum-likelihood logistic regression should.

Conceptual soundness nevertheless fails on the feature set. The developers' own feature inventory classifies each variable by observation timing relative to the performance window: ⟦unverified: 2⟧ at origination, ⟦unverified: 10⟧ before period start, ⟦unverified: 0⟧ during period, and **⟦unverified: 1⟧ after outcome** [[art:7276ca89:run.features]]. The single `after_outcome` feature is `pay_amt_next`. A variable observed after the outcome window cannot be available at scoring time and cannot legitimately enter a forward-looking default model. It was nonetheless retained through fitting, and it carries a coefficient of **⟦unverified: -12.3667⟧** — an order of magnitude larger in absolute value than the next largest term, `bill_mean_6m` at ⟦unverified: 1.6512⟧, and more than thirteen times the largest delinquency coefficient [[art:e4b3fd0e:run.model_summary#coefficients]]. The sign is exactly what a leaked payment variable would produce: a large next-period payment mechanically implies the account did not default, so the model reads the answer rather than predicting it.

This is a first-order design defect, not a tuning issue. It invalidates the discrimination and calibration evidence in Section 4 and must be remediated by dropping the feature and re-fitting before any other conclusion about the model can be drawn.

A second conceptual concern is the coefficient structure within the delinquency family. `delinq_last` enters at +⟦unverified: 0.9159⟧ and `delinq_count_6m` at +⟦unverified: 0.1073⟧, both correctly signed, but `delinq_max_6m` enters at **⟦unverified: -0.0999⟧** — implying that, holding recent and count-based delinquency fixed, a worse maximum delinquency over six months *reduces* default risk. `age` also enters at ⟦unverified: -0.0887⟧, which is directionally plausible for this product but is small enough to be noise. The wrong-signed `delinq_max_6m` term is best read as an artifact of correlation within the delinquency block rather than as economic signal, and it would not survive a sign-constrained fit.

## 3. Data integrity and drift

The raw training-split profile reports ⟦unverified: 3,500⟧ rows with **zero missingness in every column**, including the target `default_next_month` [[art:43dc824d:run.data_train]]. That is clean but also unusual for retail credit data and suggests upstream imputation or row-filtering that is not documented in the submission. No corresponding profile was supplied for the test split [[art:7db99b1c:run.data_test]], so a like-for-like missingness comparison between splits could not be performed; no split-wise missingness differential is asserted in this report because no artifact supports one either way.

Split hygiene appears sound on the evidence available. The train and test row hashes are distinct (`e028347d…` and `3e28943d…`), the split sizes sum to ⟦unverified: 5,000,⟧ and `client_id` in the training profile spans ⟦unverified: 1⟧ to ⟦unverified: 5,000⟧ with a mean of ⟦unverified: 2,513.9⟧ — consistent with a single client population randomly partitioned ⟦unverified: 70⟧/⟦unverified: 30⟧ [[art:3b6b0a38:run.splits]] [[art:43dc824d:run.data_train]]. Event rates are effectively identical across splits (⟦unverified: 0.224571⟧ train, ⟦unverified: 0.224667⟧ test), as expected under a stratified or large random split. No row-level identifier intersection could be computed from the submitted artifacts, so train/test contamination is recorded as untested rather than as absent.

Three data-quality observations are noted without being raised as formal defects, because the submission contains no declared bound that they breach:

- `utilisation` has a maximum of ⟦unverified: 1.1298⟧, i.e. balances exceeding the credit limit. This is realistic for revolving products but should be documented as intentional rather than left as an apparent range violation.
- `pay_ratio_last` has a maximum of exactly ⟦unverified: 2.0000⟧ against a mean of ⟦unverified: 0.7838⟧, which is the signature of an undocumented cap. `pay_ratio_mean_6m` peaks at ⟦unverified: 1.6385⟧ and shows no such round ceiling, which supports the censoring reading. Capping is acceptable practice; undocumented capping is not, because it silently changes the tail behaviour the coefficient is fitted to.
- `bill_trend_6m` is heavily left-skewed (mean ⟦unverified: -237.6⟧, standard deviation ⟦unverified: 3,118.5⟧, minimum ⟦unverified: -67,201.4⟧ against a maximum of ⟦unverified: 27,397.9⟧). A standardised linear term on a variable this asymmetric gives extreme leverage to a small number of rows.

On drift: no population stability index, characteristic analysis, or score-distribution comparison was submitted, and no out-of-time sample exists in the artifact store. The near-identical train/test event rates are evidence of a well-executed random split, not evidence of stability over time, and they should not be read as such. Drift is therefore **unassessed**, and this report makes no PSI-based finding because no artifact would evidence it.

## 4. Outcomes analysis

Reported performance [[art:65d0d3f7:run.metrics]]:

| Metric | Train (n=⟦unverified: 3,500⟧) | Test (n=⟦unverified: 1,500⟧) |
|---|---|---|
| AUC | ⟦unverified: 0.98118⟧ | ⟦unverified: 0.97551⟧ |
| Gini | ⟦unverified: 0.96236⟧ | ⟦unverified: 0.95101⟧ |
| KS | ⟦unverified: 0.88945⟧ | ⟦unverified: 0.87844⟧ |
| Log loss | ⟦unverified: 0.15047⟧ | ⟦unverified: 0.16700⟧ |
| Brier | ⟦unverified: 0.03817⟧ | ⟦unverified: 0.04247⟧ |
| Mean predicted | ⟦unverified: 0.22455⟧ | ⟦unverified: 0.23302⟧ |
| Observed event rate | ⟦unverified: 0.22457⟧ | ⟦unverified: 0.22467⟧ |

These numbers must be read in the light of Section 2. A test AUC of ⟦unverified: 0.9755⟧ and a KS of ⟦unverified: 0.8784⟧ are far outside the range any honest behavioural default model attains on this product class, where ⟦unverified: 0.75⟧–⟦unverified: 0.85⟧ AUC is a strong result. The performance is not a strength of the model; it is a symptom of the `after_outcome` feature and should be treated as evidence for the leakage finding rather than as a passed test [[art:7276ca89:run.features#items]] [[art:e4b3fd0e:run.model_summary#coefficients]]. The true out-of-sample performance of the model after removal of `pay_amt_next` is unknown and cannot be inferred from the submitted artifacts.

**Generalisation.** The train-to-test AUC gap is ⟦unverified: 0.00567⟧ (⟦unverified: 0.98118⟧ → ⟦unverified: 0.97551⟧), with a Gini gap of ⟦unverified: 0.01135⟧ and a KS gap of ⟦unverified: 0.01101⟧. On its own this is a narrow gap, comfortably inside the tolerance a validator would normally set for an eleven-parameter linear model on ⟦unverified: 3,500⟧ rows, and no out-of-sample degradation defect is raised. The caveat is that a leaked feature suppresses the apparent gap: both splits share the same leakage, so the small degradation measures the stability of the leak, not the stability of genuine signal.

**Calibration.** On train, mean predicted (⟦unverified: 0.224552⟧) matches observed (⟦unverified: 0.224571⟧) to within ⟦unverified: 2e-5⟧, which is the expected in-sample identity for unweighted logistic regression and carries no independent information. On test, mean predicted is ⟦unverified: 0.233018⟧ against an observed event rate of ⟦unverified: 0.224667⟧ — an absolute over-prediction of ⟦unverified: 0.00835⟧ and a relative over-prediction of ⟦unverified: 3.7%⟧. This is modest, and in isolation would be a low-severity observation rather than a breach, but it is the one direction in which the test set behaves worse than the train set and it is recorded as a finding at low severity. No calibration slope, no intercept test, and no decile-level reliability table were submitted, so calibration was assessable only at the aggregate mean level; the prediction tables exist in the store [[art:1eb04cca:run.predictions_test]] but no binned calibration artifact was produced from them.

**Effective challenge.** No challenger model, benchmark, or baseline was submitted. There is no artifact in the store against which the champion's performance could be benchmarked, so effective challenge was not performed. This report raises no challenger-based defect, because doing so would name no artifact; it is instead carried as a required remediation in Section 6.

## 5. Sensitivity and scenario analysis

No sensitivity or scenario artifacts were submitted: there is no stress-scenario output, no value or profit curve, no threshold-sweep table, and no partial-dependence or monotonicity evidence in the artifact store. The analysis below is therefore limited to what the coefficient vector itself implies, and no scenario-based defect is raised because none could be evidenced.

On the standardised coefficients, model sensitivity is dominated by a single term. `pay_amt_next` at ⟦unverified: -12.3667⟧ is ⟦unverified: 7.5⟧ times the magnitude of the next largest coefficient and accounts for the overwhelming majority of the score's variance contribution; a one-standard-deviation move in that feature shifts the log-odds by more than twelve units, which is enough to drive the predicted probability from near one to near zero on its own [[art:e4b3fd0e:run.model_summary#coefficients]]. A model this concentrated in one input is fragile by construction, and in this case the dominant input is the illegitimate one. Sensitivity analysis on the current specification is consequently not informative about the deployed behaviour of any remediated model.

Among the legitimate features, the ranking by absolute standardised effect is `bill_mean_6m` (⟦unverified: 1.6512⟧), `delinq_last` (⟦unverified: 0.9159⟧), `utilisation` (⟦unverified: 0.8591⟧), `pay_ratio_mean_6m` (⟦unverified: 0.7072⟧), `limit_bal` (⟦unverified: 0.4311⟧), `pay_ratio_last` (⟦unverified: 0.2086⟧), `bill_trend_6m` (⟦unverified: 0.1993⟧), `delinq_count_6m` (⟦unverified: 0.1073⟧), `delinq_max_6m` (⟦unverified: -0.0999⟧), and `age` (⟦unverified: -0.0887⟧). Two directional features of this ordering warrant scrutiny once the model is re-fitted. First, `limit_bal` enters positively at ⟦unverified: 0.4311⟧: a higher credit limit raising default odds is contrary to the usual underwriting relationship, in which limit is assigned as a function of assessed quality, and here it likely absorbs exposure effects left over from the bill/utilisation block. Second, `bill_mean_6m` outranks every delinquency variable, which is unexpected for a next-month default model where recent delinquency is normally the dominant driver; this again points at the collinear bill family rather than at genuine economics.

A monotonicity review across the risk-driver curves could not be performed. Required before approval: a threshold sweep with the associated confusion matrices and expected-value curve, a one-at-a-time sensitivity run over each retained feature, and a downturn scenario in which delinquency and utilisation distributions are shifted adversely.

## 6. Findings and recommendations

Three findings are raised. They are listed in the structured findings block with defect classes and evidence.

**Finding ⟦unverified: 1⟧ (L1, high) — Target leakage via `pay_amt_next`.** The feature is developer-declared as `after_outcome`, is retained in the fitted model, and carries a coefficient of ⟦unverified: -12.3667⟧, dwarfing every other term. *Remediation:* drop `pay_amt_next`, re-fit, and re-report all metrics. Additionally, institute a hard gate in the training pipeline that refuses to fit when any feature carries a timing label of `after_outcome` or `during_period` — the label existed and was correct here, and the failure was that nothing acted on it. Re-examine `bill_trend_6m` and `pay_ratio_last` for partial-period contamination while the pipeline is open, since their construction windows are not documented.

**Finding ⟦unverified: 2⟧ (M1, medium) — Severe multicollinearity in the bill and utilisation block.** `bill_last` was measured at VIF ⟦unverified: 162.93⟧ and `utilisation_mean_6m` at VIF ⟦unverified: 36.78⟧ against a declared threshold of ⟦unverified: 10.0⟧, and both were dropped. The drops are documented and the direction of the remediation was right, but VIFs of that magnitude indicate near-linear dependence across the whole block, not two isolated offenders, and the residual instability is visible in the surviving coefficients: `delinq_max_6m` is wrong-signed at ⟦unverified: -0.0999⟧ and `limit_bal` is counter-intuitively positive at +⟦unverified: 0.4311⟧. *Remediation:* report post-removal VIFs and the design-matrix condition number for the final eleven-feature specification, and confirm the threshold is met after the leakage fix rather than only before it. Consider consolidating the bill family into a single exposure measure, or applying sign constraints to the delinquency block.

**Finding ⟦unverified: 3⟧ (C1, low) — Aggregate over-prediction on the test split.** Test mean predicted is ⟦unverified: 0.23302⟧ against an observed ⟦unverified: 0.22467⟧, a ⟦unverified: 3.7%⟧ relative over-prediction, while the train split is exact by construction. The magnitude is small and conservative in direction. *Remediation:* produce a decile reliability table and a calibration slope/intercept from the existing test prediction table; re-assess after the leakage fix, since calibration on a leaked model carries little information.

**Matters not raised as findings, but required before approval.** Each of the following is a gap in the submission rather than an observed defect, and none is recorded as a finding because no artifact in the store would evidence it: (a) no challenger or benchmark model was submitted, so effective challenge has not been performed; (b) no PSI or out-of-time sample exists, so drift is unassessed; (c) no scenario, threshold-sweep, or value-curve artifacts exist, so scenario analysis is unassessed; (d) no test-split data profile was submitted, so cross-split missingness could not be compared; (e) no row-level identifier overlap check between splits was submitted, so contamination is untested, though the split hashes and the `client_id` range are consistent with a clean ⟦unverified: 70⟧/⟦unverified: 30⟧ partition of ⟦unverified: 5,000⟧ clients.

**Overall assessment: not approved for use.** The model must be re-fitted without `pay_amt_next` and resubmitted with the multicollinearity diagnostics, calibration evidence, challenger comparison, and scenario analysis described above. The realistic expectation is that discrimination will fall substantially from the reported ⟦unverified: 0.9755⟧ test AUC once the leak is removed; that fall is the correct outcome and should not be treated as a regression.

### F-001 · L1 leakage · severity **high**

The developer-submitted feature inventory classifies features by observation timing and reports `after_outcome: 1`. The feature so labelled is `pay_amt_next`, and it was retained through model fitting. In the fitted standardised logistic regression it carries a coefficient of -12.3667, against a next-largest absolute coefficient of 1.6512 (`bill_mean_6m`) and a largest delinquency coefficient of 0.9159 (`delinq_last`) — a term roughly 7.5 times the magnitude of any other and more than twice the intercept of -6.1028. The sign and magnitude are exactly what a leaked next-period payment amount produces: a large payment in the following period mechanically implies the account did not default, so the model is reading the outcome rather than predicting it. This is corroborated by the reported performance, where test AUC is 0.97551, Gini 0.95101, and KS 0.87844; discrimination at that level is not attainable on a next-month revolving-credit default model with legitimate behavioural inputs, where 0.75-0.85 AUC is a strong result. Every discrimination and calibration figure in the submission is therefore uninterpretable as an estimate of forward-looking performance, and the small train-to-test AUC gap of 0.00567 measures the stability of the leak rather than the stability of genuine signal. The feature is also unavailable at scoring time by construction, so the specification could not be deployed even if the statistics were accepted. Remediation: drop `pay_amt_next`, re-fit, and re-report all metrics; institute a hard pipeline gate that refuses to fit when any feature carries a timing label of `after_outcome` or `during_period`, since the label was present and correct here and the failure was that nothing acted on it. `bill_trend_6m` and `pay_ratio_last` should also be reviewed for partial-period contamination, as their construction windows are undocumented.

### F-002 · M1 collinearity · severity **medium**

The model summary records two features removed for multicollinearity against a declared VIF threshold of 10.0: `bill_last` at VIF 162.931 and `utilisation_mean_6m` at VIF 36.782. The removals are documented and the direction of the remediation was correct, but a VIF of 163 indicates near-linear dependence across the whole bill/utilisation block rather than two isolated offenders, and the submission provides no post-removal VIFs or design-matrix condition number to demonstrate that the declared threshold of 10.0 is actually met by the final eleven-feature specification. Residual instability is visible in the surviving coefficients. `delinq_max_6m` enters at -0.0999, implying that a worse maximum delinquency over six months lowers default odds once recent delinquency (`delinq_last`, +0.9159) and delinquency count (`delinq_count_6m`, +0.1073) are held fixed, which is economically wrong-signed and characteristic of correlated predictors splitting a shared effect. `limit_bal` enters at +0.4311, so a higher assigned credit limit raises default odds, which runs against the usual underwriting relationship in which limit is granted as a function of assessed quality. `bill_mean_6m` at 1.6512 outranks every delinquency variable, which is unexpected for a next-month default model where recent delinquency is normally the dominant legitimate driver. The raw training profile supports the collinearity reading: `bill_mean_6m` (mean 47,885, sd 44,975) and `utilisation` (mean 0.447, sd 0.234) are alternative scalings of the same exposure, and the removed `bill_last` and `utilisation_mean_6m` are lagged or averaged versions of both. Remediation: report post-removal VIFs and the condition number for the final specification after the leakage fix, consider consolidating the bill family into a single exposure measure, and apply sign constraints to the delinquency block.

### F-003 · C1 calibration · severity **low**

On the test split, mean predicted probability is 0.233018 against an observed event rate of 0.224667 — an absolute over-prediction of 0.00835 and a relative over-prediction of 3.7%. On the training split, mean predicted (0.224552) matches observed (0.224571) to within 2e-5, which is the expected in-sample identity for an unweighted maximum-likelihood logistic regression with an intercept and carries no independent validation information. The test-split discrepancy is modest and conservative in direction, and on its own would not bar use, but it is the one dimension on which the held-out sample behaves materially worse than the training sample, and it is recorded here so that it is tracked rather than lost. The severity is held at low because the magnitude is small; the interpretation is heavily qualified by the leakage finding, since aggregate calibration measured on a model that reads the outcome tells the validator little about the calibration of any remediated model. No calibration slope, no calibration intercept test, and no decile-level reliability table were submitted, so calibration could be assessed only at the aggregate mean level even though the row-level prediction tables for both splits exist in the artifact store. Remediation: produce a decile reliability table and a calibration slope and intercept from the existing test prediction table, and re-assess both after `pay_amt_next` has been removed and the model re-fitted.

Candidates raised and not promoted: none.

### Open items

No open item was recorded for this validation.

## 7. Ongoing monitoring recommendations

Conditional on remediation and re-approval, the following monitoring is recommended.

*Pre-deployment gate, at each re-fit.* Automated enforcement of the feature timing taxonomy already present in `run.features`: the fit must abort if any feature is labelled `after_outcome` or `during_period`, and the counts must be logged with the model summary. A single-feature AUC screen should be run over every candidate input, with any feature exceeding ⟦unverified: 0.90⟧ standalone AUC quarantined for manual review before it can enter a specification. Post-removal VIFs and the condition number must be recorded alongside the declared threshold of ⟦unverified: 10.0⟧.

*Monthly.* Population stability index on each retained feature and on the score distribution, against the development sample as baseline; amber at PSI ⟦unverified: 0.10⟧, red at ⟦unverified: 0.25⟧, with red requiring investigation within one reporting cycle. Missingness rate per feature, alerting on any departure from the zero-missingness baseline observed in development. Mean predicted probability versus the scored population's realised event rate once outcomes mature, tracked as a running ratio.

*Quarterly.* Discrimination on the most recent matured cohort — AUC, Gini, and KS — with an alert if AUC falls more than ⟦unverified: 0.05⟧ below the re-fit test value or if the train-to-recent-cohort gap exceeds ⟦unverified: 0.05⟧. Calibration slope and intercept on the matured cohort, with the slope expected inside [⟦unverified: 0.8⟧, ⟦unverified: 1.2⟧]. Decile-level reliability with observed-versus-expected default rates. Coefficient stability monitoring: re-estimate on a rolling window and flag any sign change in a top-five feature, with particular attention to `delinq_max_6m` and `limit_bal`, both of which are currently signed against economic expectation.

*Annually, or on trigger.* Full re-validation including a fresh effective-challenge exercise against at least one alternative specification (a regularised logistic fit and a gradient-boosted benchmark are the natural choices), a downturn scenario run, and a documented review of the `pay_ratio_last` cap at ⟦unverified: 2.0⟧ and the `utilisation` values above 1.0. Triggers for early re-validation: two consecutive months of red PSI, a quarterly AUC breach, a calibration slope outside band, or any change to the upstream feature-engineering pipeline.

*Governance.* Given that the leakage in this submission was correctly labelled in the developers' own artifact and still reached a fitted model, the monitoring plan should be accompanied by a control attestation that the timing gate is active in the production training pipeline, reviewed at each model change.

## Appendix A — Claims

Grounding precision 0.0000 before repair (0 of 104 claims verified; 70 unsupported, 34 dangling) and 0.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 0/3; conceptual_soundness 0/13; data_integrity 0/17; outcomes 0/33; sensitivity 0/13; findings 0/16; monitoring 0/9.

Developer claims: `plain_llm` runs no check over `package.yaml`'s declared claims See Appendix D.

Excluded numeric tokens (not claims): section_number (Section 4, Section 2, Section 6); inline_code (`3e28943d…`); citation_hash (e4b3fd0e, 3b6b0a38, 65d0d3f7, 7276ca89); package_version (1.0); extractor_returned_excluded_token (1.0, 4, 6.0, 2).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | This report documents the independent validation of package… | -6.1028 | ratio | coefficient |  | eq | `[[art:e4b3fd0e:run.model_summary]]` | dangling |  |
| 2 | summary | This report documents the independent validation of package… | 3500 | count | splits | train | eq | `[[art:3b6b0a38:run.splits]]` | dangling |  |
| 3 | summary | This report documents the independent validation of package… | 1500 | count | splits | test | eq | `[[art:3b6b0a38:run.splits]]` | dangling |  |
| 4 | conceptual_soundness | The choice of a standardised logistic regression for a month… | 22.5 | percent | event_rate |  | eq |  | unsupported |  |
| 5 | conceptual_soundness | The choice of a standardised logistic regression for a month… | 0.22455 | ratio | mean_predicted_probability | train | eq |  | unsupported |  |
| 6 | conceptual_soundness | The choice of a standardised logistic regression for a month… | 0.22457 | ratio | event_rate | train | eq |  | unsupported |  |
| 7 | conceptual_soundness | Conceptual soundness nevertheless fails on the feature set.… | 2 | count | features |  | eq | `[[art:7276ca89:run.features]]` | dangling |  |
| 8 | conceptual_soundness | Conceptual soundness nevertheless fails on the feature set.… | 10 | count | features |  | eq | `[[art:7276ca89:run.features]]` | dangling |  |
| 9 | conceptual_soundness | Conceptual soundness nevertheless fails on the feature set.… | 0 | count | features |  | eq | `[[art:7276ca89:run.features]]` | dangling |  |
| 10 | conceptual_soundness | Conceptual soundness nevertheless fails on the feature set.… | 1 | count | features |  | eq | `[[art:7276ca89:run.features]]` | dangling |  |
| 11 | conceptual_soundness | Conceptual soundness nevertheless fails on the feature set.… | -12.3667 | ratio | coefficient |  | eq | `[[art:e4b3fd0e:run.model_summary#coefficients]]` | dangling |  |
| 12 | conceptual_soundness | Conceptual soundness nevertheless fails on the feature set.… | 1.6512 | ratio | coefficient |  | eq | `[[art:e4b3fd0e:run.model_summary#coefficients]]` | dangling |  |
| 13 | conceptual_soundness | A second conceptual concern is the coefficient structure wit… | 0.9159 | ratio | coefficient |  | eq |  | unsupported |  |
| 14 | conceptual_soundness | A second conceptual concern is the coefficient structure wit… | 0.1073 | ratio | coefficient |  | eq |  | unsupported |  |
| 15 | conceptual_soundness | A second conceptual concern is the coefficient structure wit… | -0.0999 | ratio | coefficient |  | eq |  | unsupported |  |
| 16 | conceptual_soundness | A second conceptual concern is the coefficient structure wit… | -0.0887 | ratio | coefficient |  | eq |  | unsupported |  |
| 17 | data_integrity | The raw training-split profile reports 3,500 rows with **zer… | 3500 | count | n_rows | train | eq | `[[art:43dc824d:run.data_train]]` | dangling |  |
| 18 | data_integrity | Split hygiene appears sound on the evidence available. The t… | 5000 | count | n_rows |  | eq | `[[art:3b6b0a38:run.splits]]` | dangling |  |
| 19 | data_integrity | Split hygiene appears sound on the evidence available. The t… | 1 | count |  | train | eq | `[[art:43dc824d:run.data_train]]` | dangling |  |
| 20 | data_integrity | Split hygiene appears sound on the evidence available. The t… | 5000 | count |  | train | eq | `[[art:43dc824d:run.data_train]]` | dangling |  |
| 21 | data_integrity | Split hygiene appears sound on the evidence available. The t… | 2513.9 | ratio |  | train | eq | `[[art:43dc824d:run.data_train]]` | dangling |  |
| 22 | data_integrity | Split hygiene appears sound on the evidence available. The t… | 70 | ratio |  |  | eq | `[[art:3b6b0a38:run.splits]]` | dangling |  |
| 23 | data_integrity | Split hygiene appears sound on the evidence available. The t… | 30 | ratio |  |  | eq | `[[art:3b6b0a38:run.splits]]` | dangling |  |
| 24 | data_integrity | Split hygiene appears sound on the evidence available. The t… | 0.224571 | ratio | event_rate | train | eq |  | unsupported |  |
| 25 | data_integrity | Split hygiene appears sound on the evidence available. The t… | 0.224667 | ratio | event_rate | test | eq |  | unsupported |  |
| 26 | data_integrity | - `utilisation` has a maximum of 1.1298, i.e. balances excee… | 1.1298 | ratio |  |  | eq |  | unsupported |  |
| 27 | data_integrity | - `pay_ratio_last` has a maximum of exactly 2.0000 against a… | 2 | ratio |  |  | eq |  | unsupported |  |
| 28 | data_integrity | - `pay_ratio_last` has a maximum of exactly 2.0000 against a… | 0.7838 | ratio |  |  | eq |  | unsupported |  |
| 29 | data_integrity | - `pay_ratio_last` has a maximum of exactly 2.0000 against a… | 1.6385 | ratio |  |  | eq |  | unsupported |  |
| 30 | data_integrity | - `bill_trend_6m` is heavily left-skewed (mean -237.6, stand… | -237.6 | ratio |  |  | eq |  | unsupported |  |
| 31 | data_integrity | - `bill_trend_6m` is heavily left-skewed (mean -237.6, stand… | 3118.5 | ratio |  |  | eq |  | unsupported |  |
| 32 | data_integrity | - `bill_trend_6m` is heavily left-skewed (mean -237.6, stand… | -67201.4 | ratio |  |  | eq |  | unsupported |  |
| 33 | data_integrity | - `bill_trend_6m` is heavily left-skewed (mean -237.6, stand… | 27397.9 | ratio |  |  | eq |  | unsupported |  |
| 34 | outcomes | \| Metric \| Train (n=3,500) \| Test (n=1,500) \| | 3500 | count | n_rows | train | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 35 | outcomes | \| Metric \| Train (n=3,500) \| Test (n=1,500) \| | 1500 | count | n_rows | test | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 36 | outcomes | \| AUC \| 0.98118 \| 0.97551 \| | 0.98118 | ratio | auc | train | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 37 | outcomes | \| AUC \| 0.98118 \| 0.97551 \| | 0.97551 | ratio | auc | test | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 38 | outcomes | \| Gini \| 0.96236 \| 0.95101 \| | 0.96236 | ratio | gini | train | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 39 | outcomes | \| Gini \| 0.96236 \| 0.95101 \| | 0.95101 | ratio | gini | test | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 40 | outcomes | \| KS \| 0.88945 \| 0.87844 \| | 0.88945 | ratio | ks | train | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 41 | outcomes | \| KS \| 0.88945 \| 0.87844 \| | 0.87844 | ratio | ks | test | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 42 | outcomes | \| Log loss \| 0.15047 \| 0.16700 \| | 0.15047 | ratio | log_loss | train | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 43 | outcomes | \| Log loss \| 0.15047 \| 0.16700 \| | 0.167 | ratio | log_loss | test | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 44 | outcomes | \| Brier \| 0.03817 \| 0.04247 \| | 0.03817 | ratio | brier | train | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 45 | outcomes | \| Brier \| 0.03817 \| 0.04247 \| | 0.04247 | ratio | brier | test | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 46 | outcomes | \| Mean predicted \| 0.22455 \| 0.23302 \| | 0.22455 | ratio | mean_predicted | train | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 47 | outcomes | \| Mean predicted \| 0.22455 \| 0.23302 \| | 0.23302 | ratio | mean_predicted | test | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 48 | outcomes | \| Observed event rate \| 0.22457 \| 0.22467 \| | 0.22457 | ratio | event_rate | train | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 49 | outcomes | \| Observed event rate \| 0.22457 \| 0.22467 \| | 0.22467 | ratio | event_rate | test | eq | `[[art:65d0d3f7:run.metrics]]` | dangling |  |
| 50 | outcomes | These numbers must be read in the light of Section 2. A test… | 0.9755 | ratio | auc | test | eq |  | unsupported |  |
| 51 | outcomes | These numbers must be read in the light of Section 2. A test… | 0.8784 | ratio | ks | test | eq |  | unsupported |  |
| 52 | outcomes | These numbers must be read in the light of Section 2. A test… | 0.75 | ratio | auc |  | eq |  | unsupported |  |
| 53 | outcomes | These numbers must be read in the light of Section 2. A test… | 0.85 | ratio | auc |  | eq |  | unsupported |  |
| 54 | outcomes | **Generalisation.** The train-to-test AUC gap is 0.00567 (0.… | 0.00567 | ratio | delta_auc |  | delta |  | unsupported |  |
| 55 | outcomes | **Generalisation.** The train-to-test AUC gap is 0.00567 (0.… | 0.98118 | ratio | auc | train | eq |  | unsupported |  |
| 56 | outcomes | **Generalisation.** The train-to-test AUC gap is 0.00567 (0.… | 0.97551 | ratio | auc | test | eq |  | unsupported |  |
| 57 | outcomes | **Generalisation.** The train-to-test AUC gap is 0.00567 (0.… | 0.01135 | ratio | gini |  | delta |  | unsupported |  |
| 58 | outcomes | **Generalisation.** The train-to-test AUC gap is 0.00567 (0.… | 0.01101 | ratio | ks |  | delta |  | unsupported |  |
| 59 | outcomes | **Generalisation.** The train-to-test AUC gap is 0.00567 (0.… | 3500 | count | n_rows | train | eq |  | unsupported |  |
| 60 | outcomes | **Calibration.** On train, mean predicted (0.224552) matches… | 0.224552 | ratio | mean_predicted | train | eq |  | unsupported |  |
| 61 | outcomes | **Calibration.** On train, mean predicted (0.224552) matches… | 0.224571 | ratio | event_rate | train | eq |  | unsupported |  |
| 62 | outcomes | **Calibration.** On train, mean predicted (0.224552) matches… | 2e-05 | ratio |  | train | eq |  | unsupported |  |
| 63 | outcomes | **Calibration.** On train, mean predicted (0.224552) matches… | 0.233018 | ratio | mean_predicted | test | eq |  | unsupported |  |
| 64 | outcomes | **Calibration.** On train, mean predicted (0.224552) matches… | 0.224667 | ratio | event_rate | test | eq |  | unsupported |  |
| 65 | outcomes | **Calibration.** On train, mean predicted (0.224552) matches… | 0.00835 | ratio |  | test | delta |  | unsupported |  |
| 66 | outcomes | **Calibration.** On train, mean predicted (0.224552) matches… | 3.7 | percent |  | test | eq |  | unsupported |  |
| 67 | sensitivity | On the standardised coefficients, model sensitivity is domin… | -12.3667 | ratio | coefficient |  | eq | `[[art:e4b3fd0e:run.model_summary#coefficients]]` | dangling |  |
| 68 | sensitivity | On the standardised coefficients, model sensitivity is domin… | 7.5 | ratio | coefficient |  | eq | `[[art:e4b3fd0e:run.model_summary#coefficients]]` | dangling |  |
| 69 | sensitivity | Among the legitimate features, the ranking by absolute stand… | 1.6512 | ratio | coefficient |  | eq |  | unsupported |  |
| 70 | sensitivity | Among the legitimate features, the ranking by absolute stand… | 0.9159 | ratio | coefficient |  | eq |  | unsupported |  |
| 71 | sensitivity | Among the legitimate features, the ranking by absolute stand… | 0.8591 | ratio | coefficient |  | eq |  | unsupported |  |
| 72 | sensitivity | Among the legitimate features, the ranking by absolute stand… | 0.7072 | ratio | coefficient |  | eq |  | unsupported |  |
| 73 | sensitivity | Among the legitimate features, the ranking by absolute stand… | 0.4311 | ratio | coefficient |  | eq |  | unsupported |  |
| 74 | sensitivity | Among the legitimate features, the ranking by absolute stand… | 0.2086 | ratio | coefficient |  | eq |  | unsupported |  |
| 75 | sensitivity | Among the legitimate features, the ranking by absolute stand… | 0.1993 | ratio | coefficient |  | eq |  | unsupported |  |
| 76 | sensitivity | Among the legitimate features, the ranking by absolute stand… | 0.1073 | ratio | coefficient |  | eq |  | unsupported |  |
| 77 | sensitivity | Among the legitimate features, the ranking by absolute stand… | -0.0999 | ratio | coefficient |  | eq |  | unsupported |  |
| 78 | sensitivity | Among the legitimate features, the ranking by absolute stand… | -0.0887 | ratio | coefficient |  | eq |  | unsupported |  |
| 79 | sensitivity | Among the legitimate features, the ranking by absolute stand… | 0.4311 | ratio | coefficient |  | eq |  | unsupported |  |
| 80 | findings | **Finding 1 (L1, high) — Target leakage via `pay_amt_next`.*… | 1 | ratio |  |  | eq |  | unsupported |  |
| 81 | findings | **Finding 1 (L1, high) — Target leakage via `pay_amt_next`.*… | -12.3667 | ratio | coefficient |  | eq |  | unsupported |  |
| 82 | findings | **Finding 2 (M1, medium) — Severe multicollinearity in the b… | 2 | ratio |  |  | eq |  | unsupported |  |
| 83 | findings | **Finding 2 (M1, medium) — Severe multicollinearity in the b… | 162.93 | ratio | vif |  | eq |  | unsupported |  |
| 84 | findings | **Finding 2 (M1, medium) — Severe multicollinearity in the b… | 36.78 | ratio | vif |  | eq |  | unsupported |  |
| 85 | findings | **Finding 2 (M1, medium) — Severe multicollinearity in the b… | 10 | ratio | vif |  | eq |  | unsupported |  |
| 86 | findings | **Finding 2 (M1, medium) — Severe multicollinearity in the b… | -0.0999 | ratio | coefficient |  | eq |  | unsupported |  |
| 87 | findings | **Finding 2 (M1, medium) — Severe multicollinearity in the b… | 0.4311 | ratio | coefficient |  | eq |  | unsupported |  |
| 88 | findings | **Finding 3 (C1, low) — Aggregate over-prediction on the tes… | 3 | ratio |  |  | eq |  | unsupported |  |
| 89 | findings | **Finding 3 (C1, low) — Aggregate over-prediction on the tes… | 0.23302 | ratio | mean_predicted | test | eq |  | unsupported |  |
| 90 | findings | **Finding 3 (C1, low) — Aggregate over-prediction on the tes… | 0.22467 | ratio | event_rate | test | eq |  | unsupported |  |
| 91 | findings | **Finding 3 (C1, low) — Aggregate over-prediction on the tes… | 3.7 | percent |  | test | eq |  | unsupported |  |
| 92 | findings | **Matters not raised as findings, but required before approv… | 70 | ratio |  |  | eq |  | unsupported |  |
| 93 | findings | **Matters not raised as findings, but required before approv… | 30 | ratio |  |  | eq |  | unsupported |  |
| 94 | findings | **Matters not raised as findings, but required before approv… | 5000 | count |  |  | eq |  | unsupported |  |
| 95 | findings | **Overall assessment: not approved for use.** The model must… | 0.9755 | ratio | auc | test | eq |  | unsupported |  |
| 96 | monitoring | *Pre-deployment gate, at each re-fit.* Automated enforcement… | 0.9 | ratio | auc |  | eq |  | unsupported |  |
| 97 | monitoring | *Pre-deployment gate, at each re-fit.* Automated enforcement… | 10 | ratio | vif |  | eq |  | unsupported |  |
| 98 | monitoring | *Monthly.* Population stability index on each retained featu… | 0.1 | ratio | psi |  | eq |  | unsupported |  |
| 99 | monitoring | *Monthly.* Population stability index on each retained featu… | 0.25 | ratio | psi |  | eq |  | unsupported |  |
| 100 | monitoring | *Quarterly.* Discrimination on the most recent matured cohor… | 0.05 | ratio | delta_auc | test | eq |  | unsupported |  |
| 101 | monitoring | *Quarterly.* Discrimination on the most recent matured cohor… | 0.05 | ratio | delta_auc | train | eq |  | unsupported |  |
| 102 | monitoring | *Quarterly.* Discrimination on the most recent matured cohor… | 0.8 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 103 | monitoring | *Quarterly.* Discrimination on the most recent matured cohor… | 1.2 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 104 | monitoring | *Annually, or on trigger.* Full re-validation including a fr… | 2 | ratio |  |  | eq |  | unsupported |  |

## Appendix B — Artifact index

The store holds 14 artifacts; the 8 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `run.data_test` | `7db99b1c` | table | table, 1500 rows | the subject's data_test.csv |
| `run.data_train` | `43dc824d` | table | table, 3500 rows | the subject's data_train.csv |
| `run.features` | `7276ca89` | json | json | the subject's features.json |
| `run.metrics` | `65d0d3f7` | json | json | the subject's metrics.json |
| `run.model_summary` | `e4b3fd0e` | json | json | the subject's model_summary.json |
| `run.predictions_test` | `1eb04cca` | table | table, 1500 rows | the subject's predictions_test.csv |
| `run.predictions_train` | `ebd7a887` | table | table, 3500 rows | the subject's predictions_train.csv |
| `run.splits` | `3b6b0a38` | json | json | the subject's splits.json |

## Appendix C — Run trace summary

| quantity | value |
|---|---|
| tool calls | 1 (run_model 1) |
| plan steps (bounded loop) | 0 |
| LLM calls | 8 (plain_llm 1, extract 7) |
| re-asks | 0 |
| repair rounds | 0 |
| tokens in / out | 59,698 / 28,571 |
| notional cost (USD) | 1.2955 |
| wall-clock (s) | 348.49 |
| subject run (s) | 1.38 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | credit_default-plain_llm-20260918T083124Z-6e98ce62 |

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
