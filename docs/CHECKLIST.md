# CHECKLIST.md — what each check encodes, and where its defect was met

Each automated check in Quaestor names the manual practice it encodes and, for every defect class
the study seeds, the concrete instance its author met in practice. Practices and projects are named;
employers are not. The interview sentence this file backs: *"Each check is a thing I used to do by
hand in my quant role or in my own models; the agent decides which to run and writes them up, the
artifact store proves the numbers, and the seeded-defect study says how often it works."*

Class codes are `02-SPEC.md` §3.7's twelve; the seeded fourteen variants are `eval/taxonomy.yaml`'s
and their parameters live there, not here.

## 1. Practice → check

| practice (validation and modelling work) | check | tool | classes |
|---|---|---|---|
| Declared thresholds with explicit pass/fail rules (R² floors, residual σ bands) | every `package.yaml` bound re-evaluated against recomputed values; a breach is a finding with the artifact attached; the table itself is an artifact (D-092) | `compute_metrics` | T1 |
| Sensitivity scenarios over holding-period and stop-loss assumptions (100+ per validation) | rate-shock sweep with the base case marked, monotonicity and convexity read against the declared expectation | `run_scenarios` | X1 |
| Classifying feature relationships as stable, regime-dependent or unreliable | per-regime coefficient sign and AUC across a declared regime split; a flip on a leading feature is a finding | `check_stability` | R1 |
| Beginning-of-month lagging to remove payoff-balance leakage from a prepayment hazard | feature-timing declarations against the outcome window; target-adjacent name screen; single-feature AUC ceiling | `check_leakage` | L1 |
| Holdout hygiene: no subject on both sides of the split | identifier overlap and feature-vector overlap between train and test, the latter read against a within-train duplicate baseline (D-086) | `check_leakage` | L2 |
| Leave-one-vintage-out split holding out an unseen refinancing wave | metrics on declared out-of-time and vintage-holdout splits beside in-sample; PSI train-vs-test tested, other comparisons reported (D-046) | `compute_metrics`, `profile_data` | S1, O1 |
| Calibration and monthly CPR fit prioritised over AUC under a low event rate | calibration slope and intercept, mean-predicted vs observed, Brier, decile table; section order decided by declared `use` or the event-rate rule (D-098) | `compute_metrics` | C1 |
| VIF-based screening (28 → 12 features) | VIF and Belsley condition number on the retained design; reintroduced collinear features are a finding; sign check against univariate direction as evidence (D-095) | `check_collinearity` | M1 |
| Champion vs challenger under several imbalance strategies | effective challenge against a challenger at library defaults; SMOTE-without-recalibration shows in the calibration checks | `challenger_compare`, `compute_metrics` | E1, C1 |
| Input completeness before scoring | missingness per feature per split; a gap between splits is a finding | `profile_data` | D1 |
| Sub-population performance where a pooled result can mask a weak segment | slice metrics with headline gap and share; a material slice is an open item for the developer, not a finding (D-102) | `compute_metrics` (bounded loop) | — |
| Score mapping (300–900) with SHAP/LIME | out of scope; a monitoring recommendation, not a check | — | — |

## 2. Seeded class → the instance met

One sentence each, the author's own. These are the `met_where` fields of `eval/taxonomy.yaml`.

| class | name | met where |
|---|---|---|
| L1 | target leakage | A retail scorecard where a "months since last payment" feature was refreshed after the observation window closed, so it encoded the outcome. And, on the prepayment side: a hazard model where the end-of-month balance leaked the payoff, fixed by lagging to beginning-of-month. |
| L2 | train/test contamination | A model whose holdout was drawn after de-duplication on account id, but re-issued accounts carried new ids and the same customer appeared on both sides. |
| R1 | regime-dependent feature | A behavioural feature whose sign reversed between a low-rate and a rising-rate period, and the pooled fit averaged the two into a coefficient near zero. |
| C1 | miscalibration | A class-balanced training set whose predicted default rate came out several times the observed portfolio rate because no one recalibrated back to the base rate. |
| S1 | population shift | A model built on one origination channel and later applied to a channel with a different applicant profile, with no PSI check at deployment. And: a prepayment model fitted on pre-refinance-wave vintages and used to price servicing on post-wave originations. |
| M1 | multicollinearity | The same balance expressed in two currencies or two scalings entering as separate features, producing unstable coefficients between refits. |
| D1 | data integrity | A data-vendor field that went dark for part of the scoring population and was silently filled with zero by the pipeline default. |
| T1 | false developer claim | Model documentation that reported a development-sample AUC as if it were the validation-sample AUC. |
| X1 | scenario inconsistency | A rate-shock table where one scenario had been entered with the wrong sign and the value curve was non-monotone across shocks. |

Not seeded: `R0` (the subject fails to run) and `O1` (generalisation gap) arise as consequences and
are scored only where a recipe targets them; `E1` is the clean synthetic credit subject's own
expected finding (D-017).

## 3. What this file does not claim

The study measures whether the agent finds what its author knows to plant, not what it would find
in the wild: two subjects, one to two variants per class, one model, one run per pair, defects
seeded by the same person who built the checks (`04-SEEDED-DEFECT-STUDY.md` §8). That limitation is
written here before anyone raises it.
