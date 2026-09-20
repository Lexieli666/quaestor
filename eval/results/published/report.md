# Seeded-defect study: scores

Scored 2026-09-20T23:31:20Z from `eval/results/20260918T065257Z`, against the answer keys in `eval/variants` and the control baselines measured in `eval/taxonomy.yaml`.

Detection is `04-SEEDED-DEFECT-STUDY.md` section 4's criterion unchanged: a finding of the *seeded* class at severity at least `medium`. Counts, never percentages -- n is one or two variants per class. Nothing here is read from a report's prose.

## Detection

| defect class | seeded n | rules_only | plain_llm | full_agent |
|---|---|---|---|---|
| `L1` | 3 | 3 | 3 | 3 |
| `L2` | 2 | 2 | 0 | 2 |
| `R1` | 1 | 1 | 0 | 1 |
| `C1` | 2 | 2 | 2 | 2 |
| `S1` | 2 | 2 | 1 | 2 |
| `M1` | 1 | 1 | 1 | 1 |
| `D1` | 1 | 1 | 0 | 1 |
| `T1` | 1 | 1 | 0 | 1 |
| `X1` | 1 | 1 | 1 | 1 |
| **all** | **14** | **14** | **8** | **14** |

- `rules_only`: 14 detected, 0 missed over 18 run(s); false alarms 0, collateral spurious 0, unevidenced findings 0, precision 1.0000
- `plain_llm`: 8 detected, 6 missed over 18 run(s); false alarms 16, collateral spurious 0, unevidenced findings 0, precision 0.3333
- `full_agent`: 14 detected, 0 missed over 18 run(s); false alarms 0, collateral spurious 0, unevidenced findings 0, precision 1.0000

## Controls

Every finding at or above `medium` that the control's own measured baseline does not carry is a false alarm (`04` section 4). A control whose baseline reads `null` in the taxonomy is not scored for false alarms at all: there, `null` is "not yet measured" and never "empty".

| control | data mode | rules_only | plain_llm | full_agent |
|---|---|---|---|---|
| `control_credit_clean` | synthetic | 0 | 2 (M1 medium, E1 medium) | 0 |
| `control_credit_perturbed` | synthetic | 0 | 4 (M1 medium, X1 medium, E1 medium, S1 medium) | 0 |
| `control_msr_clean` | synthetic | 0 | 6 (C1 high, X1 medium, E1 medium, S1 medium, D1 medium, M1 medium) | 0 |
| `control_msr_perturbed` | synthetic | 0 | 4 (D1 high, C1 medium, S1 medium, X1 medium) | 0 |

## Grounding precision

| configuration | reports | pre mean | pre min | post mean | post min |
|---|---|---|---|---|---|
| `rules_only` | 18 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| `plain_llm` | 18 | 0.0004 | 0.0000 | 0.0004 | 0.0000 |
| `full_agent` | 18 | 0.9950 | 0.9840 | 1.0000 | 1.0000 |

## Misses

Every seeded variant whose class its configuration did not raise at `medium` or above, with what its report said instead and the path to read it at.

### `plain_llm`

- `credit__D1__test_only_missingness` -- said instead: M1 medium, E1 medium, T1 medium, C1 low, X1 low, S1 low, L2 low, D1 low, R1 low, O1 info, L1 info; report: `plain_llm/credit__D1__test_only_missingness/report.md`
- `credit__L2__contamination` -- said instead: M1 medium, X1 medium, S1 medium, E1 medium, C1 low, D1 low, T1 low, O1 info, L2 info; report: `plain_llm/credit__L2__contamination/report.md`
- `credit__R1__regime_flip` -- said instead: M1 medium, E1 medium, S1 medium, X1 low, O1 low, C1 low, L2 low, D1 low, T1 low, L1 info; report: `plain_llm/credit__R1__regime_flip/report.md`
- `credit__S1__segment_shift` -- said instead: C1 medium, M1 medium, S1 low, D1 low; report: `plain_llm/credit__S1__segment_shift/report.md`
- `credit__T1__false_claim` -- said instead: M1 medium, X1 medium, C1 low, S1 low, D1 low, E1 low, R1 info, O1 info; report: `plain_llm/credit__T1__false_claim/report.md`
- `msr__L2__contamination` -- said instead: C1 high, C1 medium, X1 medium, D1 medium, S1 medium, M1 low, L2 low, E1 info; report: `plain_llm/msr__L2__contamination/report.md`

## Collateral findings

A finding of a class the variant was not seeded with. Only `spurious` counts against precision and `unjudged` counts in neither half of it, so each verdict carries the date it was decided: a rule fixed before the study reads differently from one written after the numbers were seen.

| configuration | variant | class | severity | verdict | decided |
|---|---|---|---|---|---|
| `rules_only` | `credit__C1__smote_uncalibrated` | `T1` | high | true_consequence | 2026-09-09, D-136, before any variant was run |
| `rules_only` | `credit__L1__after_outcome_declared` | `C1` | medium | true_consequence | 2026-09-09, D-136, before any variant was run |
| `rules_only` | `credit__L1__after_outcome_hidden` | `C1` | medium | true_consequence | 2026-09-09, D-136, before any variant was run |
| `rules_only` | `credit__S1__segment_shift` | `T1` | high | true_consequence | 2026-09-09, D-136, before any variant was run |
| `rules_only` | `msr__L1__eom_balance` | `X1` | high | true_consequence | 2026-09-09, D-136, before any variant was run |
| `rules_only` | `msr__S1__vintage_shift` | `T1` | high | true_consequence | 2026-09-09, D-136, before any variant was run |
| `rules_only` | `msr__S1__vintage_shift` | `C1` | medium | true_consequence | 2026-09-17, D-182 amendment, at scoring time |
| `plain_llm` | `credit__C1__smote_uncalibrated` | `E1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `credit__C1__smote_uncalibrated` | `T1` | medium | true_consequence | 2026-09-09, D-136, before any variant was run |
| `plain_llm` | `credit__C1__smote_uncalibrated` | `M1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `credit__C1__smote_uncalibrated` | `X1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `credit__D1__test_only_missingness` | `M1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `credit__D1__test_only_missingness` | `E1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `credit__D1__test_only_missingness` | `T1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `credit__L1__after_outcome_declared` | `M1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `credit__L1__after_outcome_hidden` | `T1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `credit__L1__after_outcome_hidden` | `M1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `credit__L1__after_outcome_hidden` | `E1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `credit__L1__after_outcome_hidden` | `X1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `credit__L2__contamination` | `M1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `credit__L2__contamination` | `X1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `credit__L2__contamination` | `S1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `credit__L2__contamination` | `E1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `credit__M1__vif_reintroduced` | `T1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `credit__R1__regime_flip` | `M1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `credit__R1__regime_flip` | `E1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `credit__R1__regime_flip` | `S1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `credit__S1__segment_shift` | `C1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `credit__S1__segment_shift` | `M1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `credit__T1__false_claim` | `M1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `credit__T1__false_claim` | `X1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `msr__C1__oversampled_hazard` | `L2` | high | unjudged | nobody has decided one |
| `plain_llm` | `msr__C1__oversampled_hazard` | `D1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `msr__C1__oversampled_hazard` | `X1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `msr__C1__oversampled_hazard` | `S1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `msr__C1__oversampled_hazard` | `M1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `msr__L1__eom_balance` | `L2` | high | unjudged | nobody has decided one |
| `plain_llm` | `msr__L1__eom_balance` | `C1` | high | unjudged | nobody has decided one |
| `plain_llm` | `msr__L1__eom_balance` | `T1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `msr__L1__eom_balance` | `S1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `msr__L1__eom_balance` | `X1` | medium | true_consequence | 2026-09-09, D-136, before any variant was run |
| `plain_llm` | `msr__L2__contamination` | `C1` | high | unjudged | nobody has decided one |
| `plain_llm` | `msr__L2__contamination` | `C1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `msr__L2__contamination` | `X1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `msr__L2__contamination` | `D1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `msr__L2__contamination` | `S1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `msr__S1__vintage_shift` | `D1` | high | unjudged | nobody has decided one |
| `plain_llm` | `msr__S1__vintage_shift` | `C1` | high | true_consequence | 2026-09-17, D-182 amendment, at scoring time |
| `plain_llm` | `msr__S1__vintage_shift` | `X1` | high | unjudged | nobody has decided one |
| `plain_llm` | `msr__S1__vintage_shift` | `D1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `msr__S1__vintage_shift` | `L2` | medium | unjudged | nobody has decided one |
| `plain_llm` | `msr__S1__vintage_shift` | `M1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `msr__X1__projection_sign` | `L2` | high | unjudged | nobody has decided one |
| `plain_llm` | `msr__X1__projection_sign` | `C1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `msr__X1__projection_sign` | `D1` | medium | unjudged | nobody has decided one |
| `plain_llm` | `msr__X1__projection_sign` | `S1` | medium | unjudged | nobody has decided one |
| `full_agent` | `credit__C1__smote_uncalibrated` | `T1` | high | true_consequence | 2026-09-09, D-136, before any variant was run |
| `full_agent` | `credit__L1__after_outcome_declared` | `C1` | medium | true_consequence | 2026-09-09, D-136, before any variant was run |
| `full_agent` | `credit__L1__after_outcome_hidden` | `C1` | medium | true_consequence | 2026-09-09, D-136, before any variant was run |
| `full_agent` | `credit__S1__segment_shift` | `T1` | high | true_consequence | 2026-09-09, D-136, before any variant was run |
| `full_agent` | `msr__L1__eom_balance` | `X1` | high | true_consequence | 2026-09-09, D-136, before any variant was run |
| `full_agent` | `msr__S1__vintage_shift` | `T1` | high | true_consequence | 2026-09-09, D-136, before any variant was run |
| `full_agent` | `msr__S1__vintage_shift` | `C1` | medium | true_consequence | 2026-09-17, D-182 amendment, at scoring time |

## What was not scored, and why

Each of these is a refusal rather than a number. A crash scored as a miss, an unmeasured baseline read as an empty one, or an unforeseen collateral pairing called spurious would each put a figure nobody decided into a published table (D-182).

### `plain_llm`

- `credit__C1__smote_uncalibrated` raised `E1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `credit__C1__smote_uncalibrated` raised `M1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `credit__C1__smote_uncalibrated` raised `X1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `credit__D1__test_only_missingness` raised `M1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `credit__D1__test_only_missingness` raised `E1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `credit__D1__test_only_missingness` raised `T1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `credit__L1__after_outcome_declared` raised `M1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `credit__L1__after_outcome_hidden` raised `T1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `credit__L1__after_outcome_hidden` raised `M1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `credit__L1__after_outcome_hidden` raised `E1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `credit__L1__after_outcome_hidden` raised `X1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `credit__L2__contamination` raised `M1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `credit__L2__contamination` raised `X1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `credit__L2__contamination` raised `S1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `credit__L2__contamination` raised `E1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `credit__M1__vif_reintroduced` raised `T1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `credit__R1__regime_flip` raised `M1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `credit__R1__regime_flip` raised `E1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `credit__R1__regime_flip` raised `S1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `credit__S1__segment_shift` raised `C1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `credit__S1__segment_shift` raised `M1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `credit__T1__false_claim` raised `M1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `credit__T1__false_claim` raised `X1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `msr__C1__oversampled_hazard` raised `L2` high -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `msr__C1__oversampled_hazard` raised `D1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `msr__C1__oversampled_hazard` raised `X1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `msr__C1__oversampled_hazard` raised `S1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `msr__C1__oversampled_hazard` raised `M1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `msr__L1__eom_balance` raised `L2` high -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `msr__L1__eom_balance` raised `C1` high -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `msr__L1__eom_balance` raised `T1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `msr__L1__eom_balance` raised `S1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `msr__L2__contamination` raised `C1` high -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `msr__L2__contamination` raised `C1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `msr__L2__contamination` raised `X1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `msr__L2__contamination` raised `D1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `msr__L2__contamination` raised `S1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `msr__S1__vintage_shift` raised `D1` high -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `msr__S1__vintage_shift` raised `X1` high -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `msr__S1__vintage_shift` raised `D1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `msr__S1__vintage_shift` raised `L2` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `msr__S1__vintage_shift` raised `M1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `msr__X1__projection_sign` raised `L2` high -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `msr__X1__projection_sign` raised `C1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `msr__X1__projection_sign` raised `D1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
- `msr__X1__projection_sign` raised `S1` medium -- unjudged: no judgement was decided in advance for this pairing; docs/STUDY.md section 9 owes one, with its date, before this finding enters a published number
