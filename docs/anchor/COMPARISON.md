# Anchor comparison — manual validation vs `full_agent`, `credit_default` (clean)

n = 1, one subject, one validator, one run. This is an anchor for reading the reports, not an
evaluation. The manual validation (`manual_credit_default.md`) was committed at `225d902` before
the copilot's report was opened. The copilot's report is
`eval/results/published/full_agent/control_credit_clean/report.md`, run `credit_default-full_agent-20260918T222547Z-e2e51e00`,
264 claims, grounding 0.9924 → 1.0000, findings {high 0, medium 0, low 1, info 0}.

## 1. Findings both raised

| finding | manual | copilot |
| --- | --- | --- |
| `F-001` E1 effective challenge, severity low | raised | raised, severity low |

Both read the challenger's lead the same way: as a statement against the champion's
specification rather than as a result in the challenger's favour. The copilot states the
mechanism more sharply — a linear-in-log-odds specification leaving structure a non-linear
learner recovers from the same inputs — and supports it with a second comparison the manual
validation does not use, `challenger.brier` 0.1258 against `metrics.test.brier` 0.1489.

## 2. The one disagreement of judgement

**The three sign-check disagreements.** `sign_check.delinq_max_6m`, `sign_check.limit_bal` and
`sign_check.pay_ratio_last` all read `agrees` = 0: the fitted coefficient direction is opposite
to the univariate direction on train.

- **Manual:** raise as a finding in its own right, or at minimum as a documented issue requiring
  follow-up, distinct from the ineffective-champion finding `F-001`. The pattern across all three
  tested variables could indicate feature-definition errors, suppression effects, or an unstable
  specification, and the model owner should verify feature coding and expected directions,
  examine predictor correlations and coefficient stability, and document the explanation before
  the model is relied upon.
- **Copilot:** all three appear, in `### Open items`, phrased as questions to the model developer
  — for `delinq_max_6m`, "which correlated features absorb the direction the feature shows on its
  own?"; for `limit_bal`, "is the reversal an intended conditional effect given the other
  credit-exposure features in the specification?"; for `pay_ratio_last`, "how is that conditional
  direction explained to users of the model output?". Not promoted to a finding.

Both sides saw the same evidence and reached the same mechanistic suspicion. They differ on
whether it crosses the bar for a finding. I hold the position. An open item asks the developer a question; a finding records that the validator judged something wrong. Three reversals out of three tested features is a pattern rather than three separate questions, and the copilot's own multicollinearity paragraph supplies the mechanism. Leaving it as a question concludes nothing the model owner is obliged to answer.

## 3. Numbers only the copilot cites

- `profile.train.n` 3500, `profile.test.n` 1500, `runtime.max_seconds` 300, `metrics.train.auc` 0.7584
- `challenger.brier` 0.1258
- the developer's own VIF screen: `removed.bill_last.vif` 160.9, `removed.utilisation_mean_6m.vif` 36.36, `vif_threshold` 10
- fitted coefficients: `coefficients.pay_ratio_mean_6m.value` −0.3554, `coefficients.pay_ratio_last.value` 0.1026
- two bounded-loop slice analyses the manual validation has no counterpart for:
  `metrics.test.sub.delinq_count_6m_low.auc` 0.6599 with a gap of 0.08813, and
  `metrics.test.sub.utilisation_high.auc` 0.5689 with a gap of 0.1791, both against the open-item
  bound `threshold.O1.slice_auc_gap` 0.08
- SR 26-2 section citations (`reg:SR26-2:V`, `V.1.b`)

## 4. Numbers only the manual validation cites

None. Every figure in the manual validation appears in the copilot's report.

## 5. Open items the copilot raised and the manual validation did not

Two slice items: within `delinq_count_6m <= median`, AUC 0.6599 on a 0.6333 share; within
`utilisation > median`, AUC 0.5689 on a 0.5 share. Both breach `threshold.O1.slice_auc_gap`. The
manual validation did not partition the test split at all, so this is a coverage gap on the human
side rather than a disagreement.

## 6. Severity disagreements

None on the shared finding: both place `F-001` at low. The sign-check disagreement in section 2 is
a promotion disagreement, not a severity one.

## 7. What this anchor shows

On this one package the copilot cites strictly more than the human and misses nothing the human
found. The human's contribution is a single promotion judgement — whether a consistent pattern of
sign reversals is a finding or an open question — and the copilot's is coverage the human did not
attempt, principally the two conditional slices its bounded loop chose to compute.

n = 1. Nothing here generalises.
