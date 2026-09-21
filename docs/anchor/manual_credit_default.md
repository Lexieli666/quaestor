# Manual validation — `credit_default` (clean), written 2026-09-20

n = 1, one subject, one validator. This is an anchor for reading the reports, not an evaluation.
Written from `eval/results/published/rules_only/control_credit_clean/` before opening the
`full_agent` report on the same package. Every number is cited by its logical name.

## 1. Summary and scope
This review covers the clean credit_default v1.0 package, which uses synthetic data. Four checks—profile_data, compute_metrics, check_leakage, and check_collinearity—produced no finding candidate. The challenger_compare check produced the package’s sole finding.
## 2. Conceptual soundness
The champion model achieved metrics.test.auc = 0.748, while the challenger achieved challenger.auc = 0.824. The difference, challenger.delta_auc = 0.07598, exceeds threshold.E1.delta_auc = 0.03. The challenger outperforms the champion by more than the declared bound, which is a finding against the champion’s specification: the incumbent is leaving measurable discrimination on the table.

All three directional checks—sign_check.delinq_max_6m, sign_check.limit_bal, and sign_check.pay_ratio_last—have agrees = 0. In each case, the fitted coefficient direction is opposite to the corresponding univariate direction. Although coefficient reversals can arise in multivariable models, disagreement across all three tested variables warrants further investigation into feature definitions, correlation, suppression effects, and model specification.
## 3. Data integrity and drift
Observed drift is limited. psi.max = 0.01095, which is well below the threshold of 0.25. The profile_data check did not trigger D1 or S1, so the report provides no evidence of a material data-integrity issue or population drift for this package.
## 4. Outcomes analysis
The champion model meets the reported performance and calibration thresholds. metrics.test.auc = 0.748 is above the minimum of 0.7, while metrics.test.brier = 0.1489 is below the maximum of 0.2. In addition, calibration_slope.test = 1.003 falls within the acceptable range of 0.8–1.2.

The two developer-declared claims were not evaluated. Under D-016, metrics calculated from the synthetic data-generation process are not meaningful evidence for claims about performance on real-world samples.
## 5. Sensitivity and scenario analysis
The maximum variance inflation factor is vif.max = 7.295, below the threshold of 10. The feature-level values are delinq_last = 1.412, delinq_max_6m = 2.408, limit_bal = 4.803, pay_ratio_last = 7.264, pay_ratio_mean_6m = 7.259, and utilisation = 3.215.

The similar, elevated VIF values for pay_ratio_last and pay_ratio_mean_6m indicate that these two variables are likely strongly related. This matters because sign_check.pay_ratio_last is one of the three directional checks with agrees = 0. Multicollinearity between the two payment-ratio variables is therefore a plausible explanation for the fitted sign reversal, even though neither the feature-level values nor vif.max breaches the threshold of 10. The relationship should be tested directly rather than treated as proof that the reversal is harmless.

Scenario analysis is not applicable because this model does not include a scenario-analysis component.
## 6. Findings and recommendations
The report contains one finding: F-001, classified under E1 with low severity and originating from challenger_compare. It identifies a weakness in the champion specification because the challenger improves discrimination by more than the declared bound.

I would raise the three sign-check failures as a separate finding, or at minimum as a documented issue requiring follow-up. The disagreement affects all three tested variables and is conceptually distinct from the ineffective champion selection captured by F-001. Although coefficient reversals may legitimately result from correlated predictors or multivariable adjustment, the consistent pattern could also indicate feature-definition errors, suppression effects, or an unstable specification. The model owner should verify feature coding and expected directions, examine predictor correlations and coefficient stability, and document the explanation before the model is relied upon.
## 7. Ongoing monitoring recommendations
Continue monitoring metrics.test.auc, metrics.test.brier, calibration_slope.test, and psi.max on each new validation sample, with alerts tied to the existing acceptance thresholds. The three sign checks should also be repeated and tracked over time, with particular attention to the relationship between pay_ratio_last and pay_ratio_mean_6m. Challenger performance should be reassessed periodically to determine whether continued use of the current champion remains justified.