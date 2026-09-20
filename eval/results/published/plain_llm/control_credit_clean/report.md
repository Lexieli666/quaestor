---
schema_version: 1
quaestor_version: "0.1.0.dev0"
package: credit_default
version: "1.0"
model_type: binary_classification
configuration: plain_llm
model: claude-opus-5[1m]
run_id: credit_default-plain_llm-20260918T081127Z-6e98ce62
data_mode: synthetic
synthetic_n: 5000
grounding_precision_pre: 0.0000
grounding_precision_post: 0.0000
n_claims: 87
n_findings_by_severity: {high: 0, medium: 2, low: 3, info: 0}
generated: "2026-09-18T08:11:27Z"
illustrative: false
---

# Validation report — `credit_default` v1.0

## 1. Summary and scope

<!-- quaestor:renderer:begin scope -->
| package | configuration | model | data | grounding precision (pre → post repair) | findings (high / medium / low / info) |
|---|---|---|---|---|---|
| `credit_default` v1.0 | `plain_llm` | claude-opus-5[1m] | synthetic, n = 5000 | 0.0000 → 0.0000 | 0 / 2 / 3 / 0 |
<!-- quaestor:renderer:end -->

This report documents an independent validation of package `credit_default` version 1.0, a binary classification model that estimates the probability of `default_next_month` for revolving credit clients. The subject is a standardised logistic regression with ten retained predictors and an intercept of ⟦unverified: -1.3958⟧ [[art:74c10f15:run.model_summary]]. It was fitted on ⟦unverified: 3,500⟧ rows and evaluated on ⟦unverified: 1,500⟧ held-out rows drawn from a ⟦unverified: 5,000⟧-client population [[art:3b6b0a38:run.splits]].

The scope of this review is limited to what the developer placed in the artifact store: the metrics file [[art:aebcad6a:run.metrics]], the model summary [[art:74c10f15:run.model_summary]], the feature inventory [[art:abbb748e:run.features]], the split manifest [[art:3b6b0a38:run.splits]], the train and test datasets and prediction tables [[art:6a89f2be:run.data_train]] [[art:26fbbf1d:run.data_test]] [[art:6fd8f98a:run.predictions_train]] [[art:66bafeec:run.predictions_test]], and a raw profile of the training split [[art:ecf908fa:plain_llm.profile]]. No re-execution of the training code was performed and no independent data source was available, so every statement below is a statement about the developer's own record.

Headline result: discrimination is adequate and stable (test AUC ⟦unverified: 0.7480⟧, Gini ⟦unverified: 0.4960⟧, KS ⟦unverified: 0.4183⟧), mean-level calibration is close (mean predicted ⟦unverified: 0.2211⟧ against an observed event rate ⟦unverified: 0.2247⟧), and there is no evidence of target leakage or of out-of-sample collapse. The material weaknesses are not in performance but in the evidence base: residual multicollinearity has left several coefficients with economically wrong signs, no challenger model was built, no calibration slope or drift statistic was computed, and the validation design is a random rather than an out-of-time split. The model is usable for the purpose described, subject to the remediations in section 6.

## 2. Conceptual soundness

The choice of a logistic regression for a binary default outcome is appropriate and conventional. Inputs are standardised, so coefficient magnitudes are directly comparable [[art:74c10f15:run.model_summary#standardised]]. The feature set is small (ten retained), which supports interpretability and reduces overfitting risk, and the identifier `client_id` present in the raw data does not appear among the model inputs [[art:abbb748e:run.features]] [[art:ecf908fa:plain_llm.profile]]. No class weighting was applied; with a ⟦unverified: 22.5%⟧ event rate this is a defensible choice, since the class imbalance is mild and the model is used to rank and to produce probabilities rather than hard labels.

The dominant predictor is `delinq_last` (+⟦unverified: 0.7334⟧), which is the economically expected relationship: a client delinquent in the most recent observed month is materially more likely to default next month. `utilisation` (+⟦unverified: 0.2662⟧) and `pay_ratio_last` (+⟦unverified: 0.1026⟧) also carry the expected positive sign, and `limit_bal` (+⟦unverified: 0.0727⟧) and `age` (⟦unverified: -0.0673⟧) are small and directionally unremarkable.

Several other coefficients are not economically coherent. `delinq_max_6m` carries a negative coefficient (⟦unverified: -0.0322⟧): holding the rest of the vector fixed, a client whose worst delinquency over six months was more severe is scored as marginally *safer*. `pay_ratio_mean_6m` (⟦unverified: -0.3554⟧) points in the opposite direction to `pay_ratio_last` (+⟦unverified: 0.1026⟧), so the same underlying behaviour measured over two windows enters the score with opposite signs. `bill_mean_6m` (⟦unverified: -0.3726⟧) and `bill_trend_6m` (⟦unverified: -0.2225⟧) are both strongly negative, implying that larger and rising balances reduce default risk. These are the classic symptoms of correlated predictors sharing a single underlying signal, and they are treated as a multicollinearity finding in section 6 rather than as three separate conceptual defects. The practical consequence is that individual coefficients cannot be used to explain or justify a decline decision, even though the aggregate score performs acceptably.

No documentation of the intended use, the population of applicability, the score cut-offs, or the economic rationale for each feature was placed in the store. The conceptual review above is therefore reconstructed from the artifacts rather than assessed against a developer's stated design.

## 3. Data integrity and drift

The training profile reports ⟦unverified: 3,500⟧ rows and zero missing values in all thirteen columns, including the target [[art:ecf908fa:plain_llm.profile]]. Complete absence of missingness across every field is unusual for credit bureau and billing data and normally indicates either a synthetic dataset or an upstream imputation step that has not been documented. Neither an imputation record nor a data lineage note is present in the store.

No equivalent profile was produced for the test split [[art:26fbbf1d:run.data_test]], so a like-for-like comparison of missingness and distribution between train and test could not be made. The declared row hashes differ between the two splits, which is consistent with disjoint partitions, but no explicit overlap or duplicate-client check was recorded [[art:3b6b0a38:run.splits]]. Given that `client_id` runs from ⟦unverified: 1⟧ to ⟦unverified: 5,000⟧ and the two splits sum to exactly ⟦unverified: 5,000⟧ rows, a clean partition is plausible; it remains unverified.

Two integrity observations arise from the profile itself. First, `pay_ratio_last` has a maximum of exactly ⟦unverified: 2.0⟧ against a mean of ⟦unverified: 0.784⟧, which is the signature of an undocumented cap or winsorisation at ⟦unverified: 2.0⟧; `pay_ratio_mean_6m` tops out at ⟦unverified: 1.639⟧, consistent with the same cap applied to its components. Second, `utilisation` reaches ⟦unverified: 1.1297⟧, which is legitimate for an over-limit account but confirms the variable is not bounded at ⟦unverified: 1⟧ and so should not be treated as a rate in downstream logic. `bill_trend_6m` has a mean of ⟦unverified: -237.6⟧ with a standard deviation of ⟦unverified: 3,118.5⟧ and a minimum of ⟦unverified: -67,201,⟧ a heavy left tail that the linear specification treats symmetrically.

On drift: the train and test event rates are ⟦unverified: 0.224571⟧ and ⟦unverified: 0.224667⟧, essentially identical [[art:3b6b0a38:run.splits]]. No population stability index or characteristic analysis was computed for any input or for the score. More importantly, the partition appears to be a random split of a single population rather than an out-of-time sample, so it cannot in principle detect temporal drift, which is the drift that matters for a monthly default model. The near-identical event rates are therefore a property of the split design and should not be read as evidence of stability.

## 4. Outcomes analysis

Discrimination on the held-out split is acceptable for a credit default scorecard: AUC ⟦unverified: 0.7480⟧, Gini ⟦unverified: 0.4960⟧, KS ⟦unverified: 0.4183⟧ on ⟦unverified: 1,500⟧ observations [[art:aebcad6a:run.metrics#test]]. The corresponding training figures are AUC ⟦unverified: 0.7584⟧, Gini ⟦unverified: 0.5169⟧, KS ⟦unverified: 0.4451⟧ on ⟦unverified: 3,500⟧ observations [[art:aebcad6a:run.metrics#train]]. The train-to-test AUC gap is ⟦unverified: 0.0104⟧, well inside any conventional degradation threshold and consistent with a ten-parameter model fitted on ⟦unverified: 3,500⟧ rows. There is no evidence of overfitting and no out-of-sample degradation finding is raised.

Accuracy of the probabilities is likewise reasonable in aggregate. Test log loss is ⟦unverified: 0.4673⟧ and Brier score ⟦unverified: 0.1489⟧, against training values of ⟦unverified: 0.4650⟧ and ⟦unverified: 0.1489⟧ respectively. Mean predicted probability on test is ⟦unverified: 0.2211⟧ against an observed event rate of ⟦unverified: 0.2247⟧, an absolute shortfall of ⟦unverified: 0.0036⟧ or about ⟦unverified: 1.6%⟧ in relative terms, which is immaterial at this sample size. On train the two agree to within ⟦unverified: 0.00005⟧, as expected for a fitted logistic model.

These are aggregate statistics only. No calibration curve, decile table, calibration slope or intercept, and no rank-order or reversal analysis by score band was produced, although the prediction tables needed to compute them are in the store [[art:66bafeec:run.predictions_test]] [[art:6fd8f98a:run.predictions_train]]. A model can match the mean event rate exactly while being badly calibrated in the tails, and it is precisely the tails that drive cut-off decisions, so the calibration evidence presented is not sufficient to support use of the raw probabilities as expected loss inputs.

No segment-level outcomes were reported. Performance by age band, limit band, or delinquency status is unknown, so it is not possible to say whether the aggregate AUC is uniform or whether it is carried by one subpopulation.

## 5. Sensitivity and scenario analysis

No sensitivity or scenario artifacts exist in the store. There is no stressed-population run, no value or profit curve across candidate cut-offs, no univariate perturbation analysis, and no reporting of confidence intervals around the headline metrics. The assessment below is therefore analytic, derived from the coefficient vector, and is offered as an indication of where the model is fragile rather than as a completed scenario analysis.

Because inputs are standardised, coefficient magnitude is sensitivity. A one-standard-deviation increase in `delinq_last` moves the log-odds by ⟦unverified: 0.733⟧, roughly twice the effect of the next largest term (`bill_mean_6m` at ⟦unverified: -0.373⟧) and nearly three times that of `utilisation` (+⟦unverified: 0.266⟧). With an intercept of ⟦unverified: -1.3958⟧, a client at the population mean scores about ⟦unverified: 0.198⟧; a two-standard-deviation move in `delinq_last` alone lifts that to roughly ⟦unverified: 0.518⟧. The model is thus concentrated in a single behavioural variable whose raw distribution is highly skewed (mean ⟦unverified: 0.660⟧, standard deviation ⟦unverified: 1.324⟧, maximum ⟦unverified: 8.0⟧) [[art:ecf908fa:plain_llm.profile]]. Any change in the upstream definition, reporting lag, or cure policy for delinquency would move the score distribution sharply, and no such dependency is documented.

The wrong-signed terms identified in section 2 create a second and less obvious fragility. Because `bill_mean_6m` and `pay_ratio_mean_6m` offset positively-signed relatives, the response of the score to a coordinated stress — a recession in which balances rise, payment ratios fall, and delinquencies rise together — cannot be inferred from the coefficients term by term, and may be muted or non-monotone. This is exactly the regime under which the model would be relied upon, and it is untested.

No formal non-monotone or wrong-signed value curve was observed, because no value curve was produced; no scenario-analysis defect is raised on the evidence available, and the absence is instead recorded as a remediation in section 6.

## 6. Findings and recommendations

Five findings are raised, two of medium severity and three of low severity. None of them prevents use of the model as a ranking device; two of them constrain how its output may be used and how it must be explained.

**Medium — residual multicollinearity and implausible coefficient signs (M1).** The developer applied a VIF threshold of ⟦unverified: 10.0⟧ and dropped `bill_last` (VIF ⟦unverified: 160.89⟧) and `utilisation_mean_6m` (VIF ⟦unverified: 36.36⟧) [[art:74c10f15:run.model_summary#removed]]. Diagnosing and removing those two is good practice, but the record stops there: no post-removal VIF vector and no design-matrix condition number were reported, so compliance with the developer's own stated threshold is unverified for the ten retained features. Three correlated blocks remain by construction — `delinq_last`/`delinq_count_6m`/`delinq_max_6m`, `pay_ratio_last`/`pay_ratio_mean_6m`, and `bill_mean_6m`/`bill_trend_6m` — and the coefficient signs behave as collinear blocks do, with `delinq_max_6m`, `pay_ratio_mean_6m`, `bill_mean_6m` and `bill_trend_6m` all carrying signs contrary to credit intuition. Recommendation: report VIFs and the condition number for the fitted design; drop or combine one member of each correlated block, or fit with a penalty and monotonic sign constraints; re-estimate and confirm that all retained signs are economically defensible. Until then, individual coefficients must not be used for adverse-action reasoning or reason-code generation.

**Medium — no effective challenge (E1).** The store contains a single model summary and a single set of metrics [[art:74c10f15:run.model_summary]] [[art:aebcad6a:run.metrics]]. No benchmark or challenger was fitted — not a univariate `delinq_last` cut, not a regularised variant, not a gradient-boosted alternative — so there is no basis on which to judge whether a test AUC of ⟦unverified: 0.7480⟧ is good, adequate, or a substantial underperformance against what the same data supports. Given that one feature carries most of the signal, a trivial single-variable benchmark is a necessary reference point. Recommendation: fit at least a naive univariate benchmark and one non-linear challenger on the identical split, and report the AUC and log-loss deltas.

**Low — calibration assessed only at the mean (C1).** Mean predicted ⟦unverified: 0.2211⟧ versus observed ⟦unverified: 0.2247⟧ on test is a pass, but it is the weakest possible calibration test [[art:aebcad6a:run.metrics#test]]. No calibration slope, intercept, decile table, or Hosmer-Lemeshow style statistic was produced, though `run.predictions_test` contains everything needed to compute them [[art:66bafeec:run.predictions_test]]. Recommendation: publish a decile calibration table and a calibration slope with its confidence interval before the probabilities are used as anything other than a rank.

**Low — no drift analysis and a validation design that cannot detect drift (S1).** No PSI was computed for any input or for the score [[art:3b6b0a38:run.splits]] [[art:6a89f2be:run.data_train]] [[art:26fbbf1d:run.data_test]]. The split appears to be random over a single ⟦unverified: 5,000⟧-client population, so the near-identical train and test event rates (⟦unverified: 0.22457⟧ and ⟦unverified: 0.22467⟧) are an artifact of the design rather than evidence of stability, and the model has never been tested on a period it was not fitted on. Recommendation: construct an out-of-time holdout and report input and score PSI against it.

**Low — undocumented data treatment and no cross-split integrity comparison (D1).** The training profile shows exactly zero missing values in all thirteen columns and a `pay_ratio_last` maximum of precisely ⟦unverified: 2.0⟧, indicating undocumented imputation and an undocumented cap [[art:ecf908fa:plain_llm.profile]]. No profile was produced for the test split, so missingness and distribution could not be compared across splits [[art:26fbbf1d:run.data_test]]. Recommendation: document the imputation and capping rules, and publish a matched profile for the test split.

Matters reviewed and not raised as findings: leakage by timing, since the feature inventory declares zero `after_outcome` and zero `during_period` features, ten `before_period_start` and two `at_origination` [[art:abbb748e:run.features]] — noting that these labels are developer-declared and were not verified against the source extract, and that no single-feature AUC was reported to corroborate them; out-of-sample degradation, since the train-to-test AUC gap of ⟦unverified: 0.0104⟧ is immaterial [[art:aebcad6a:run.metrics]]; and run integrity, since `run.status`, `run.stderr`, `run.duration_s` and `runtime.max_seconds` are present in the store but their contents were not available for this review, so no conclusion is drawn about runtime caps.

### F-001 · M1 collinearity · severity **medium**

The developer declared a VIF threshold of 10.0 and removed bill_last (VIF 160.89) and utilisation_mean_6m (VIF 36.36). No post-removal VIF vector and no design-matrix condition number were reported, so compliance with the developer's own threshold is unverified for the ten retained features. Three strongly correlated blocks remain by construction: delinq_last/delinq_count_6m/delinq_max_6m, pay_ratio_last/pay_ratio_mean_6m, and bill_mean_6m/bill_trend_6m. The fitted coefficients show the classic signature of this condition: delinq_max_6m is negative (-0.0322), so a more severe worst delinquency scores as safer; pay_ratio_mean_6m (-0.3554) opposes pay_ratio_last (+0.1026) although both measure the same behaviour over different windows; and bill_mean_6m (-0.3726) and bill_trend_6m (-0.2225) imply that larger and rising balances reduce default risk. Aggregate discrimination is unaffected, but individual coefficients cannot support adverse-action reasoning or reason codes in this state. Remediation: publish VIFs and the condition number for the fitted design, drop or combine one member of each block or impose sign constraints, and re-estimate until all retained signs are economically defensible.

### F-002 · E1 effective challenge · severity **medium**

The artifact store contains a single model summary and a single metrics file. No benchmark and no challenger were built on the same split, so there is no basis for judging whether a test AUC of 0.7480 represents good use of the available data or a material underperformance. This gap is more consequential than usual here because one feature, delinq_last, carries roughly twice the standardised weight of any other term, which raises the question of how much of the 0.7480 a single-variable rule would reproduce on its own. Remediation: fit at least a univariate delinq_last benchmark and one non-linear challenger such as a gradient-boosted model on the identical train and test partitions, and report the AUC and log-loss deltas against the champion.

### F-003 · C1 calibration · severity **low**

The only calibration evidence in the record is the agreement between mean predicted probability and observed event rate: 0.2211 against 0.2247 on test, an absolute shortfall of 0.0036, and effectively exact agreement on train. That is a pass, but it is the weakest available test, since a model can reproduce the overall event rate while being badly miscalibrated in the score tails that drive cut-off decisions. No calibration slope or intercept, no decile or bucketed observed-versus-expected table, and no goodness-of-fit statistic was reported, even though the per-row prediction tables needed to compute all of them are in the store. Remediation: publish a decile calibration table and a calibration slope with a confidence interval before the output is used as a probability rather than as a rank.

### F-004 · S1 population drift · severity **low**

No population stability index or characteristic analysis was computed for any input or for the score. The train and test event rates are 0.224571 and 0.224667, essentially identical, but the split manifest and the client identifier range indicate a random partition of a single 5,000-client population rather than an out-of-time sample. The matching event rates are therefore a property of the split design and carry no information about stability over time, which is the drift that matters for a monthly default model. The model has never been evaluated on a period it was not fitted on. Remediation: construct an out-of-time holdout, and report input-level and score-level PSI against the development distribution with amber and red thresholds at 0.10 and 0.25.

### F-005 · D1 data integrity · severity **low**

The training profile reports exactly zero missing values across all thirteen columns including the target, which is not a realistic outcome for credit bureau and billing data and indicates an upstream imputation step that is nowhere documented. The profile also shows pay_ratio_last with a maximum of precisely 2.0 against a mean of 0.784, the signature of an undocumented cap, with pay_ratio_mean_6m topping out at 1.639 consistent with the same cap applied to its components; utilisation reaches 1.1297 and so is not bounded at 1. No profile was produced for the test split, so missingness and distributional integrity could not be compared across the two partitions and the split-level integrity test could not be completed. Remediation: document the imputation and capping rules and their rationale, and publish a matched profile for the test split so that a like-for-like comparison is possible.

Candidates raised and not promoted: none.

### Open items

No open item was recorded for this validation.

## 7. Ongoing monitoring recommendations

Monthly, compute and report the population stability index for the score and for each of the ten retained inputs against the training distribution, with an amber threshold at ⟦unverified: 0.10⟧ and a red threshold at ⟦unverified: 0.25⟧. `delinq_last` warrants a dedicated tripwire: it carries roughly twice the weight of any other term, so a shift in its distribution or in its upstream definition will move the score distribution before any deterioration in AUC becomes visible.

Quarterly, once outcomes have matured, recompute AUC, Gini, KS, log loss and Brier score on the realised book and compare them to the validation baselines of ⟦unverified: 0.7480⟧, ⟦unverified: 0.4960⟧, ⟦unverified: 0.4183⟧, ⟦unverified: 0.4673⟧ and ⟦unverified: 0.1489⟧ [[art:aebcad6a:run.metrics#test]]. Set an escalation trigger at an absolute AUC decline of ⟦unverified: 0.05⟧ from baseline, or two consecutive quarters of any decline.

Quarterly, produce a decile calibration table comparing predicted to realised default rates and track the calibration slope. Mean-level agreement alone should not be accepted as the monitoring test, for the reason given in section 4. Trigger recalibration if the slope falls outside ⟦unverified: 0.8⟧ to ⟦unverified: 1.2⟧ or if the observed-to-expected ratio in the top two score deciles moves outside ⟦unverified: 0.8⟧ to ⟦unverified: 1.25⟧.

Annually, or sooner if any trigger fires, refit and re-examine coefficient signs and magnitudes. Given the multicollinearity finding, sign flips between refits should be expected and must be treated as a signal that the specification needs restructuring rather than as a routine parameter update. Each refit should also re-run the VIF and condition-number diagnostics that are missing from the current record, and should be benchmarked against the challenger models recommended in section 6.

Finally, monitor upstream data quality directly: missingness rates by field, the share of `pay_ratio_last` observations sitting exactly at the ⟦unverified: 2.0⟧ cap, and the share of `utilisation` observations above 1.0. The current record shows zero missingness everywhere, which is not a realistic steady state and should be re-established as a baseline from live data rather than from the development extract.

## Appendix A — Claims

Grounding precision 0.0000 before repair (0 of 87 claims verified; 57 unsupported, 30 dangling) and 0.0000 after 0 claim(s) rewritten and 0 number(s) removed from the prose. Per section (post-repair): summary 0/9; conceptual_soundness 0/11; data_integrity 0/15; outcomes 0/19; sensitivity 0/9; findings 0/11; monitoring 0/13.

Developer claims: `plain_llm` runs no check over `package.yaml`'s declared claims See Appendix D.

Excluded numeric tokens (not claims): section_number (section 6, section 2, section 4); citation_hash (74c10f15, 3b6b0a38, aebcad6a, abbb748e); package_version (1.0); extractor_returned_excluded_token (1.0, 6, 2, 10.0).

All claims, post-repair:

| # | section | text | value | unit | metric | split | cmp | citation | status | artifact value |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | summary | This report documents an independent validation of package `… | -1.3958 | ratio | coefficient |  | eq | `[[art:74c10f15:run.model_summary]]` | dangling |  |
| 2 | summary | This report documents an independent validation of package `… | 3500 | count | n_train | train | eq | `[[art:3b6b0a38:run.splits]]` | dangling |  |
| 3 | summary | This report documents an independent validation of package `… | 1500 | count | n_test | test | eq | `[[art:3b6b0a38:run.splits]]` | dangling |  |
| 4 | summary | This report documents an independent validation of package `… | 5000 | count | n_total |  | eq | `[[art:3b6b0a38:run.splits]]` | dangling |  |
| 5 | summary | Headline result: discrimination is adequate and stable (test… | 0.748 | ratio | auc | test | eq |  | unsupported |  |
| 6 | summary | Headline result: discrimination is adequate and stable (test… | 0.496 | ratio | gini | test | eq |  | unsupported |  |
| 7 | summary | Headline result: discrimination is adequate and stable (test… | 0.4183 | ratio | ks | test | eq |  | unsupported |  |
| 8 | summary | Headline result: discrimination is adequate and stable (test… | 0.2211 | ratio | mean_predicted | test | eq |  | unsupported |  |
| 9 | summary | Headline result: discrimination is adequate and stable (test… | 0.2247 | ratio | event_rate | test | eq |  | unsupported |  |
| 10 | conceptual_soundness | The choice of a logistic regression for a binary default out… | 22.5 | percent | event_rate |  | eq |  | unsupported |  |
| 11 | conceptual_soundness | The dominant predictor is `delinq_last` (+0.7334), which is… | 0.7334 | ratio | coefficient |  | eq |  | unsupported |  |
| 12 | conceptual_soundness | The dominant predictor is `delinq_last` (+0.7334), which is… | 0.2662 | ratio | coefficient |  | eq |  | unsupported |  |
| 13 | conceptual_soundness | The dominant predictor is `delinq_last` (+0.7334), which is… | 0.1026 | ratio | coefficient |  | eq |  | unsupported |  |
| 14 | conceptual_soundness | The dominant predictor is `delinq_last` (+0.7334), which is… | 0.0727 | ratio | coefficient |  | eq |  | unsupported |  |
| 15 | conceptual_soundness | The dominant predictor is `delinq_last` (+0.7334), which is… | -0.0673 | ratio | coefficient |  | eq |  | unsupported |  |
| 16 | conceptual_soundness | Several other coefficients are not economically coherent. `d… | -0.0322 | ratio | coefficient |  | eq |  | unsupported |  |
| 17 | conceptual_soundness | Several other coefficients are not economically coherent. `d… | -0.3554 | ratio | coefficient |  | eq |  | unsupported |  |
| 18 | conceptual_soundness | Several other coefficients are not economically coherent. `d… | 0.1026 | ratio | coefficient |  | eq |  | unsupported |  |
| 19 | conceptual_soundness | Several other coefficients are not economically coherent. `d… | -0.3726 | ratio | coefficient |  | eq |  | unsupported |  |
| 20 | conceptual_soundness | Several other coefficients are not economically coherent. `d… | -0.2225 | ratio | coefficient |  | eq |  | unsupported |  |
| 21 | data_integrity | The training profile reports 3,500 rows and zero missing val… | 3500 | count |  | train | eq | `[[art:ecf908fa:plain_llm.profile]]` | dangling |  |
| 22 | data_integrity | No equivalent profile was produced for the test split , so a… | 1 | count |  |  | eq |  | unsupported |  |
| 23 | data_integrity | No equivalent profile was produced for the test split , so a… | 5000 | count |  |  | eq |  | unsupported |  |
| 24 | data_integrity | No equivalent profile was produced for the test split , so a… | 5000 | count |  |  | eq |  | unsupported |  |
| 25 | data_integrity | Two integrity observations arise from the profile itself. Fi… | 2 | ratio |  | train | eq |  | unsupported |  |
| 26 | data_integrity | Two integrity observations arise from the profile itself. Fi… | 0.784 | ratio |  | train | eq |  | unsupported |  |
| 27 | data_integrity | Two integrity observations arise from the profile itself. Fi… | 2 | ratio |  | train | eq |  | unsupported |  |
| 28 | data_integrity | Two integrity observations arise from the profile itself. Fi… | 1.639 | ratio |  | train | eq |  | unsupported |  |
| 29 | data_integrity | Two integrity observations arise from the profile itself. Fi… | 1.1297 | ratio |  | train | eq |  | unsupported |  |
| 30 | data_integrity | Two integrity observations arise from the profile itself. Fi… | 1 | ratio |  |  | eq |  | unsupported |  |
| 31 | data_integrity | Two integrity observations arise from the profile itself. Fi… | -237.6 | currency |  | train | eq |  | unsupported |  |
| 32 | data_integrity | Two integrity observations arise from the profile itself. Fi… | 3118.5 | currency |  | train | eq |  | unsupported |  |
| 33 | data_integrity | Two integrity observations arise from the profile itself. Fi… | -67201 | currency |  | train | eq |  | unsupported |  |
| 34 | data_integrity | On drift: the train and test event rates are 0.224571 and 0.… | 0.224571 | ratio | event_rate | train | eq | `[[art:3b6b0a38:run.splits]]` | dangling |  |
| 35 | data_integrity | On drift: the train and test event rates are 0.224571 and 0.… | 0.224667 | ratio | event_rate | test | eq | `[[art:3b6b0a38:run.splits]]` | dangling |  |
| 36 | outcomes | Discrimination on the held-out split is acceptable for a cre… | 0.748 | ratio | auc | test | eq | `[[art:aebcad6a:run.metrics#test]]` | dangling |  |
| 37 | outcomes | Discrimination on the held-out split is acceptable for a cre… | 0.496 | ratio | gini | test | eq | `[[art:aebcad6a:run.metrics#test]]` | dangling |  |
| 38 | outcomes | Discrimination on the held-out split is acceptable for a cre… | 0.4183 | ratio | ks | test | eq | `[[art:aebcad6a:run.metrics#test]]` | dangling |  |
| 39 | outcomes | Discrimination on the held-out split is acceptable for a cre… | 1500 | count | n_observations | test | eq | `[[art:aebcad6a:run.metrics#test]]` | dangling |  |
| 40 | outcomes | Discrimination on the held-out split is acceptable for a cre… | 0.7584 | ratio | auc | train | eq | `[[art:aebcad6a:run.metrics#train]]` | dangling |  |
| 41 | outcomes | Discrimination on the held-out split is acceptable for a cre… | 0.5169 | ratio | gini | train | eq | `[[art:aebcad6a:run.metrics#train]]` | dangling |  |
| 42 | outcomes | Discrimination on the held-out split is acceptable for a cre… | 0.4451 | ratio | ks | train | eq | `[[art:aebcad6a:run.metrics#train]]` | dangling |  |
| 43 | outcomes | Discrimination on the held-out split is acceptable for a cre… | 3500 | count | n_observations | train | eq | `[[art:aebcad6a:run.metrics#train]]` | dangling |  |
| 44 | outcomes | Discrimination on the held-out split is acceptable for a cre… | 0.0104 | ratio | delta_auc |  | delta |  | unsupported |  |
| 45 | outcomes | Discrimination on the held-out split is acceptable for a cre… | 3500 | count | n_observations | train | eq |  | unsupported |  |
| 46 | outcomes | Accuracy of the probabilities is likewise reasonable in aggr… | 0.4673 | ratio | log_loss | test | eq |  | unsupported |  |
| 47 | outcomes | Accuracy of the probabilities is likewise reasonable in aggr… | 0.1489 | ratio | brier | test | eq |  | unsupported |  |
| 48 | outcomes | Accuracy of the probabilities is likewise reasonable in aggr… | 0.465 | ratio | log_loss | train | eq |  | unsupported |  |
| 49 | outcomes | Accuracy of the probabilities is likewise reasonable in aggr… | 0.1489 | ratio | brier | train | eq |  | unsupported |  |
| 50 | outcomes | Accuracy of the probabilities is likewise reasonable in aggr… | 0.2211 | ratio | mean_predicted_probability | test | eq |  | unsupported |  |
| 51 | outcomes | Accuracy of the probabilities is likewise reasonable in aggr… | 0.2247 | ratio | event_rate | test | eq |  | unsupported |  |
| 52 | outcomes | Accuracy of the probabilities is likewise reasonable in aggr… | 0.0036 | ratio |  | test | delta |  | unsupported |  |
| 53 | outcomes | Accuracy of the probabilities is likewise reasonable in aggr… | 1.6 | percent |  | test | ratio |  | unsupported |  |
| 54 | outcomes | Accuracy of the probabilities is likewise reasonable in aggr… | 5e-05 | ratio |  | train | eq |  | unsupported |  |
| 55 | sensitivity | Because inputs are standardised, coefficient magnitude is se… | 0.733 | ratio | coefficient |  | eq |  | unsupported |  |
| 56 | sensitivity | Because inputs are standardised, coefficient magnitude is se… | -0.373 | ratio | coefficient |  | eq |  | unsupported |  |
| 57 | sensitivity | Because inputs are standardised, coefficient magnitude is se… | 0.266 | ratio | coefficient |  | eq |  | unsupported |  |
| 58 | sensitivity | Because inputs are standardised, coefficient magnitude is se… | -1.3958 | ratio | coefficient |  | eq |  | unsupported |  |
| 59 | sensitivity | Because inputs are standardised, coefficient magnitude is se… | 0.198 | ratio |  |  | eq |  | unsupported |  |
| 60 | sensitivity | Because inputs are standardised, coefficient magnitude is se… | 0.518 | ratio |  |  | eq |  | unsupported |  |
| 61 | sensitivity | Because inputs are standardised, coefficient magnitude is se… | 0.66 | ratio | profile |  | eq | `[[art:ecf908fa:plain_llm.profile]]` | dangling |  |
| 62 | sensitivity | Because inputs are standardised, coefficient magnitude is se… | 1.324 | ratio | profile |  | eq | `[[art:ecf908fa:plain_llm.profile]]` | dangling |  |
| 63 | sensitivity | Because inputs are standardised, coefficient magnitude is se… | 8 | ratio | profile |  | eq | `[[art:ecf908fa:plain_llm.profile]]` | dangling |  |
| 64 | findings | **Medium — residual multicollinearity and implausible coeffi… | 10 | ratio | vif |  | eq | `[[art:74c10f15:run.model_summary#removed]]` | dangling |  |
| 65 | findings | **Medium — residual multicollinearity and implausible coeffi… | 160.89 | ratio | vif |  | eq | `[[art:74c10f15:run.model_summary#removed]]` | dangling |  |
| 66 | findings | **Medium — residual multicollinearity and implausible coeffi… | 36.36 | ratio | vif |  | eq | `[[art:74c10f15:run.model_summary#removed]]` | dangling |  |
| 67 | findings | **Medium — no effective challenge (E1).** The store contains… | 0.748 | ratio | auc | test | eq |  | unsupported |  |
| 68 | findings | **Low — calibration assessed only at the mean (C1).** Mean p… | 0.2211 | ratio | mean_predicted | test | eq | `[[art:aebcad6a:run.metrics#test]]` | dangling |  |
| 69 | findings | **Low — calibration assessed only at the mean (C1).** Mean p… | 0.2247 | ratio | event_rate | test | eq | `[[art:aebcad6a:run.metrics#test]]` | dangling |  |
| 70 | findings | **Low — no drift analysis and a validation design that canno… | 5000 | count |  |  | eq |  | unsupported |  |
| 71 | findings | **Low — no drift analysis and a validation design that canno… | 0.22457 | ratio | event_rate | train | eq |  | unsupported |  |
| 72 | findings | **Low — no drift analysis and a validation design that canno… | 0.22467 | ratio | event_rate | test | eq |  | unsupported |  |
| 73 | findings | **Low — undocumented data treatment and no cross-split integ… | 2 | ratio | max | train | eq | `[[art:ecf908fa:plain_llm.profile]]` | dangling |  |
| 74 | findings | Matters reviewed and not raised as findings: leakage by timi… | 0.0104 | ratio | delta_auc |  | delta | `[[art:aebcad6a:run.metrics]]` | dangling |  |
| 75 | monitoring | Monthly, compute and report the population stability index f… | 0.1 | ratio | psi |  | eq |  | unsupported |  |
| 76 | monitoring | Monthly, compute and report the population stability index f… | 0.25 | ratio | psi |  | eq |  | unsupported |  |
| 77 | monitoring | Quarterly, once outcomes have matured, recompute AUC, Gini,… | 0.748 | ratio | auc | test | eq | `[[art:aebcad6a:run.metrics#test]]` | dangling |  |
| 78 | monitoring | Quarterly, once outcomes have matured, recompute AUC, Gini,… | 0.496 | ratio | gini | test | eq | `[[art:aebcad6a:run.metrics#test]]` | dangling |  |
| 79 | monitoring | Quarterly, once outcomes have matured, recompute AUC, Gini,… | 0.4183 | ratio | ks | test | eq | `[[art:aebcad6a:run.metrics#test]]` | dangling |  |
| 80 | monitoring | Quarterly, once outcomes have matured, recompute AUC, Gini,… | 0.4673 | ratio | log_loss | test | eq | `[[art:aebcad6a:run.metrics#test]]` | dangling |  |
| 81 | monitoring | Quarterly, once outcomes have matured, recompute AUC, Gini,… | 0.1489 | ratio | brier | test | eq | `[[art:aebcad6a:run.metrics#test]]` | dangling |  |
| 82 | monitoring | Quarterly, once outcomes have matured, recompute AUC, Gini,… | 0.05 | ratio | delta_auc |  | eq |  | unsupported |  |
| 83 | monitoring | Quarterly, produce a decile calibration table comparing pred… | 0.8 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 84 | monitoring | Quarterly, produce a decile calibration table comparing pred… | 1.2 | ratio | calibration_slope |  | eq |  | unsupported |  |
| 85 | monitoring | Quarterly, produce a decile calibration table comparing pred… | 0.8 | ratio | observed_to_expected |  | eq |  | unsupported |  |
| 86 | monitoring | Quarterly, produce a decile calibration table comparing pred… | 1.25 | ratio | observed_to_expected |  | eq |  | unsupported |  |
| 87 | monitoring | Finally, monitor upstream data quality directly: missingness… | 2 | ratio | pay_ratio_last_cap |  | eq |  | unsupported |  |

## Appendix B — Artifact index

The store holds 14 artifacts; the 9 this report cites or rests a finding on are indexed here.

| logical name | hash | kind | value | summary |
|---|---|---|---|---|
| `plain_llm.profile` | `ecf908fa` | json | json | raw profile of data_train.csv |
| `run.data_test` | `26fbbf1d` | table | table, 1500 rows | the subject's data_test.csv |
| `run.data_train` | `6a89f2be` | table | table, 3500 rows | the subject's data_train.csv |
| `run.features` | `abbb748e` | json | json | the subject's features.json |
| `run.metrics` | `aebcad6a` | json | json | the subject's metrics.json |
| `run.model_summary` | `74c10f15` | json | json | the subject's model_summary.json |
| `run.predictions_test` | `66bafeec` | table | table, 1500 rows | the subject's predictions_test.csv |
| `run.predictions_train` | `6fd8f98a` | table | table, 3500 rows | the subject's predictions_train.csv |
| `run.splits` | `3b6b0a38` | json | json | the subject's splits.json |

## Appendix C — Run trace summary

| quantity | value |
|---|---|
| tool calls | 1 (run_model 1) |
| plan steps (bounded loop) | 0 |
| LLM calls | 8 (plain_llm 1, extract 7) |
| re-asks | 0 |
| repair rounds | 0 |
| tokens in / out | 59,109 / 26,167 |
| notional cost (USD) | 1.2291 |
| wall-clock (s) | 321.81 |
| subject run (s) | 1.19 |
| memory cap | unenforced (RLIMIT_AS 4096 MB) |
| provider adapter | claude-cli |
| model | claude-opus-5[1m] |
| run id | credit_default-plain_llm-20260918T081127Z-6e98ce62 |

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
