# STUDY.md — the seeded-defect study: protocol, decided before the first live run

*Cowork draft of 2026-09-09 for `docs/STUDY.md`. Copied into the repository at the start of Phase
12 and frozen there before the first live study run; after that, changes are made only by adding a
dated "Protocol amendment" paragraph to §9. Items marked `[TBD]` are filled at freeze time.*

## 1. The question

How often does an agent-based validator catch a model-risk defect its author has met in practice,
how often does it cry wolf on a clean model, and how much of what it writes is grounded in a
computed artifact? Three configurations answer the sub-question "what does the agent add":
`rules_only` (deterministic checks, a template over the candidates, no model call), `plain_llm`
(one model call over the contract files, no tools, no checks, no repair loop), and `full_agent`
(rules plus the bounded loop, one cited model call per section, repair on). The configurations are
those `src/quaestor/configs.py` ships; the study measures the product as shipped, not a cooled
version (temperature default).

## 2. Variants

Eighteen packages from `eval/taxonomy.yaml` (final, Phase 10, D-125 to D-137): fourteen seeded and
four controls, exactly one seeded defect per variant, built by `quaestor study build`. The recipe
parameters and the `met_where` sentence for each are in the taxonomy and are not restated here.

| class | credit_default | msr_prepayment |
|---|---|---|
| L1 target leakage | `pay_amt_next` declared `after_outcome` (A); the same declared `before_period_start` (B) | end-of-month balance in place of beginning-of-month |
| L2 contamination | 3% of test rows copied into train under **fresh ids** | same, on loan-months |
| R1 regime-dependent feature | `application_cohort` × `bill_trend_6m`, effect reversed on one cohort | — |
| C1 miscalibration | SMOTE at ratio 1.0, raw probabilities | events oversampled 5×, raw hazards |
| S1 population shift | trained on `limit_bal` ≤ median, scored on all | **train-to-test re-cut**: train = 2014 vintage through 2019-12, test = periods from 2020-01 |
| M1 multicollinearity | `bill_last`, `utilisation_mean_6m` reintroduced, plus `bill_last_adj` | — |
| D1 data integrity | `pay_ratio_last` 30% missing in the delivered test file, imputed 0 in the fit | — |
| T1 false developer claim | declared test AUC 0.05 above the artifact; floor set between them | — |
| X1 scenario inconsistency | — | projection sign error: value rises at −300 bp |
| controls | clean; harmless perturbation (rows shuffled, features prefixed `f_`) | clean; harmless perturbation |

**Decisions the taxonomy carries, restated because the scoring depends on them.**

- **L2 re-keys what it copies** (D-128). The duplicated rows carry new identifiers, so the
  identifier arm of `check_leakage` stays clean and detection rests on the feature-overlap arm at
  severity medium. This matches the instance the author met — the same customer on both sides of a
  split under different ids — and the medium arm is the honest test; a recipe that kept the ids
  would be caught trivially by the identifier arm and would say nothing about the harder case.
- **The hazard S1 is a train-to-test re-cut, not an out-of-time comparison** (D-129, resolving
  D-046). The `psi` rule and `S1` read train against test only; the recipe therefore moves the
  refinancing wave into the test split rather than relying on the out-of-time comparison, which is
  reported and not tested and on which the clean control already reads a PSI of 3.09.
- **R1 plants an effect and reverses it** (D-130): the clean synthetic process carried no
  `bill_trend_6m` effect, so the recipe adds one and reverses its sign on one cohort — the pooled
  coefficient near zero, the per-cohort coefficients opposite — which is the instance met.
- **D1's hole is in the delivered file** (D-133). `04` §2's "imputed as 0 by the subject" would have
  put zeros in the file the profiler reads and guaranteed a miss; the variant blanks the delivered
  `data_test.csv` and imputes on the way into the fit.

## 3. Data modes and the five synthetic-only variants

`04` §3 runs the study on the real samples. Nine of the fourteen recipes and both controls apply in
either data mode. Five variants needed a column the real samplers do not write (D-137) and are made
data-mode-capable in the Phase 12 pre-flight by transforms on the **delivered split files**, never
by reading raw data inside a recipe:

- `credit__M1`: `bill_last_adj` = `bill_last` plus small noise, added to the delivered files.
- `credit__R1`: `application_cohort` defined from an existing column (age or limit band), and
  `bill_trend_6m` negated on one cohort.
- `msr__L1`: end-of-month balance = the next month's beginning-of-month balance within each loan
  (the last month of each loan is dropped or carried).
- `credit__L1` (both arms): **`pay_amt_next` on real data is drawn conditioned on the observed
  outcome with overlap, tuned so its single-feature test AUC lands around 0.92–0.95 rather than
  1.0** (human decision, 2026-09-09). A real panel has no latent margin to draw from, so a
  label-conditioned draw is the only construction available; keeping leakage out of the real-data
  study would cost more than the construction's imperfection. The declared timing is honest in arm
  A and dishonest in arm B exactly as on synthetic. The measured single-feature AUC of the real
  variant is recorded in §9 before the study runs; if it cannot be held under 0.95 the arm is
  reported with that caveat, not dropped.

Where a real-data variant does not build or does not fire, that is recorded here as an amendment
and the variant is scored on synthetic only, with the miss list saying so.

## 4. Model, run protocol, cost

- **Model**: `claude-opus-5[1m]` for every `full_agent` and `plain_llm` run and for the verifier's
  extractor, pinned with `--model` on every call (HANDOFF §9; the CLI also makes a small `haiku`
  side call of its own, visible in the trace's `modelUsage`). Provider: `ClaudeCLILLM` on the
  author's plan; no API key anywhere.
- **Order**: `quaestor study build`; `rules_only` on all 18 (no model call, minutes); then
  `plain_llm` on all 18; then `full_agent` on all 18. `study run` is resumable per (variant,
  configuration) and writes each result directory as it finishes. Run in sittings.
- **Recording**: every call through `--record-cassettes`; the cassettes of the published run are
  committed and are the run. Cassette stores are per run directory (pre-flight `fc33dd7`: keys hash
  the request, so pooling across runs is ambiguous — never pool).
- **Cost guard**: Quaestor's own `quaestor study run --max-cost`, checked before every model call
  against the trace's D-093 token accounting and stopping the sitting when the ceiling is reached
  (built in the Phase 12 pre-flight). Not Probatio's `--max-cost`: on probatio 0.1.0 that flag sees
  about half of the spend and is read only at session end, so it reports and does not stop
  (D-149, amended in Phase 11). Measured on the six live credit runs of Phase 9, a
  `full_agent` run costs **$4.0–6.1 notional and 15–22 minutes** (attempts 4, 5, 6: $4.16 / $6.05 /
  $3.97; 908 / 1328 / 873 s), the loop's slice count being the main driver. Expect 18 `full_agent`
  runs at roughly **$70–110 and 5–7 hours**; `plain_llm` at roughly one draft call plus extraction
  per variant, **$1–2 each**; `rules_only` free. Stability repeats (§6) are the cuttable item.
- **Pre-flight before the first live run** (Claude Code, offline): (i) **D-088 for the checklist**
  — a rule-based tool that raises is recorded on the trace, its candidates are absent, Appendix D
  carries "did not run: <error>", §1 names the checks that did not run, the report renders, exit 0
  (human decision, 2026-09-09; D-125 and D-126 fixed two instances of this class, the pre-flight
  fixes the class); (i-b) **`study run --max-cost` as a real circuit breaker** (above); (ii) **R1 requires the flipping coefficient to be distinguishable from zero in
  both regimes** (human decision 2026-09-09; the measured reason is the collateral R1 that `msr__L2` and
  `msr__S1` raised on `burnout` and `sato`, which D-047 places at seed-to-seed noise) — **landed
  early, 2026-09-16, commit `6a9051f`, D-164**: `threshold.R1.sign_flip_z` = 2.0 beside the 0.05
  materiality gate, after the converged per-regime fit (D-163) exposed the same mechanism on the
  clean synthetic hazard control (`burnout` rising z = −0.32); both collateral R1s gone, seeded
  `credit__R1` clears at z = 7.8 / 11.1; (iii) the
  four CSV-level transforms and the label-conditioned `pay_amt_next` of §3; (iv) `eval/score.py`
  and `quaestor study run` / `study score` (D-082 lifted); (v) **Open items are rule-minted** —
  D-102's slices and a D-095-based sign-disagreement rule decide what is an open item, the drafter
  is handed the list and phrases it, as D-091 disciplined findings (Phase 11's distractor relation
  showed the drafter minting an open item from an irrelevant artifact it was shown); (vi)
  `DRAFT_INSTRUCTION` forbids spelled-out quantities and derived ratios (Phase 11's order relation
  caught "roughly two and a half", a ratio in words the digit tokenizer cannot see); (vii) the
  section-6 prompt's "candidates raised" line and its findings list are single-sourced (Phase 11's
  findings case showed the drafter silently demoting a finding to an open item under a
  contradictory prompt).


**Pre-flight list, amended 2026-09-17** after the inventory session
(`preflight-inventory-report.md`), which measured every item's tape exposure. Corrections to the
list above: **(ii) landed early** — `6a9051f`, D-164. **(vii) landed** — D-156 (`d12be1f`) for
section 6 and D-165 (`a87aa4a`) for section 1. **(iii) is four constructions over five variants**,
not five: three plain transforms (`credit__M1`, `credit__R1`, `msr__L1`) plus the label-conditioned
`pay_amt_next` covering both `credit__L1` arms — and §3's mechanism, transforms on the delivered
split files, **supersedes D-137's recorded answer** (an edit to the samplers), because a transform
on a delivered file is testable offline where a sampler edit is not; D-137 takes a dated amendment
and `study build` gains the `--data` flag D-137 withheld. Four items are added:

- **(viii) absolute versus relative.** Where a shortfall is reported on two populations, the draft
  says which comparison it is making and does not conclude uniformity from absolute gaps alone
  (D-168's known limitation; the MSR excerpt's §4 read 3.8× and 1.5× as alike).
- **(ix) `C1` evidence carries the breached split's `calibration.<split>` decile table.** Measured
  knock-on: the real-MSR control baseline's evidence list in `eval/taxonomy.yaml` goes from three
  keys to five (`+calibration.out_of_time`, `+calibration.vintage_holdout`), so **D-161 is amended
  and `score.py` must be written against the amended list**.
- **(x) sub-population artifacts carry `mean_rel_gap`.** Pairs with (vi): (vi) forbids the drafter
  from dividing, (x) supplies the quotient.
- **(xi)** the "two points out of the money" wording in D-040, the subject README and
  `docs/DESIGN.md` — the two points are the size of the move, not the level (D-170).

**Two contract clauses this section owes §5.** `score.py` matches `findings.json`'s **8-character**
evidence hashes against `artifacts/index.json`'s **16-character** ones by prefix, not by equality.
And it **refuses to score a variant whose seeded class's tool did not run**, reading the Appendix D
"did not run" rows that item (i) introduces — otherwise a crashed `check_leakage` scores a seeded
`L1` as a miss it never had the chance to detect.

**The perturbed controls' baselines, measured offline 2026-09-17**: `control_credit_perturbed` =
`{E1 low}`, identical to its clean control to the artifact hash; `control_msr_perturbed` = `{}`,
identical to its clean control's finding set. Both `real` cells stay `null` until a human runs them
under `--data`. Recorded with them: on `msr_prepayment` the harmless perturbation is **not**
value-neutral — the row shuffle moves `challenger.auc` 0.7337 → 0.7000 and `challenger.delta_auc`
−0.0415 → −0.0753. It changes no finding set, but a control whose challenger fit moves 3.4 points
under a perturbation called harmless is a fact the false-alarm arm should carry.

**Cost model, amended 2026-09-17.** Traced wall-clock (first to last trace event) and notional cost,
from each run's Appendix C: the credit excerpt run, no finding, **$3.9739 / 872.74 s (14:33)**; MSR live
attempt 1, one finding and four loop steps, **$7.1697 / 1,549.94 s (25:50)**; MSR live attempt 2, the
excerpt run, one finding and four loop steps, **$6.4858 / 1,373.77 s (22:54)**. The operator's shell
clock reads 20-40 s longer on each and is not the figure quoted here. A seeded variant carries at least
one finding by construction, so the study's per-run budget is the MSR figure and not the credit one:
`full_agent` at up to **$7.20** per variant (`rules_only` and `plain_llm` are cheaper by construction),
and `study run --max-cost` is set from that.

## 5. Scoring (`eval/score.py`)

Reads `findings.json`, `claims.json`, `trace.jsonl` and `SEED.yaml` only — never prose.

- **Detection**: a variant is detected when `findings.json` carries a finding of the seeded class
  at severity ≥ `medium`. A finding of another class is not a detection of the seeded one. `T1`
  variants are additionally detected when the developer claim is marked `mismatch` in
  `claims.json` — this channel exists only under `--data` (D-016), so on synthetic the T1 arm is
  the threshold breach alone.
- **Per-class recall** = detected / seeded, reported as counts (n is 1–2 per class), never as
  percentages without the counts beside them.
- **False alarms**: on the four controls, every finding at severity ≥ `medium` **that is not in the
  control's baseline** is a false alarm, counted per configuration with its class. Each control ×
  data mode carries a baseline finding set measured with `--llm fake` before the study and recorded
  in `eval/taxonomy.yaml` (D-161, D-017 generalised): synthetic credit {`E1` low}; real credit {};
  synthetic MSR {}; **real MSR {`C1` medium on `out_of_time` and `vintage_holdout`}** — the model
  trained through 2019 under-predicts the 2020–21 refinancing wave by about half, a true finding
  on the real model and not a false alarm. The perturbed controls' baselines are measured in the
  pre-flight. Detection of a baseline class on a seeded variant of the same subject and data mode
  requires evidence outside the baseline: `msr__C1` on real data counts only when the `C1`'s
  evidence includes a **test-split** artifact, which is why `score.py` reads artifact keys from
  `artifacts/index.json` beside `findings.json` (pre-flight item).
- **Collateral findings** on seeded variants (findings of non-seeded classes ≥ medium) are listed
  separately with a judgement each. The judgements decided in advance, from the Phase 10
  synthetic measurements (D-136): a `T1` raised because a seeded `S1` or `C1` breaches the
  package's own declared `psi` or `calibration_slope` bound is a **true consequence**; an `X1`
  raised on `msr__L1` because a leaked balance dominates the projection is a **true consequence**;
  a `C1` on the credit `L1` arms where the leak distorts the champion is a **true consequence**; an
  `R1` on a coefficient indistinguishable from zero would be **spurious** — and is the reason the
  R1 rule is tightened before the study (§4), so that if one still appears it counts against
  precision. Any collateral class not listed here is judged at scoring time and the judgement is
  added to §9 with its date.
- **Precision** = detections / (detections + false alarms on controls + collateral findings judged
  spurious).
- **`plain_llm`'s unevidenced findings** (D-072) sit in `candidates_not_promoted` with a reason
  beginning `unevidenced:`; each counts as a false alarm, per `04` §4.
- **Follow-up analyses and Open items are not findings** and are scored by rule, not by which slice
  the loop chose: the loop's slice choice varies between runs (attempt 4 tested `delinq_count_6m ==
  0`, attempt 5 `delinq_last == 0` and `== 1`, attempt 6 neither), so `score.py` reads
  `metrics.<split>.sub.*.auc_gap` and `.share` against `threshold.O1.slice_auc_gap` (0.08) and
  `threshold.O1.slice_min_share` (0.10) and reports, per `full_agent` run, how many slices were
  run and how many qualified as open items — as a descriptive column, not as detection. The 0.10
  floor stands as set (D-102); the `delinq_last == 1` item of attempt 5 at a 12% share is the case
  that tests it, and the human's judgement on whether that floor is right is recorded in §9 when
  the study's own slices are in.
- **A run that produces no report** (a crash) is scored as a miss with no report, listed in the
  miss list with the trace's last event, and counted against the configuration — but only if the
  D-088-for-the-checklist pre-flight (§4) still lets one through; the pre-flight exists so that
  this row is empty.
- **Grounding precision** per report, pre- and post-repair, from `claims.json`; mean and minimum
  per configuration. `rules_only` is trivially 1.0 and is reported as such, not celebrated.
- **Cost and latency** from traces: model calls, tokens in/out, notional cost, wall-clock, re-asks,
  repair rounds.

## 6. Stability repeats

For the six variants with the most disagreement between configurations, five repeats of
`full_agent` under `--runs 5` through the Probatio layer, detection pass rate with a Wilson 95%
interval. Roughly 30 `full_agent` runs, **$120–180 and 8–11 hours** at Phase 9's measured rate:
this is the cuttable item (`03-RUNBOOK.md` §4), cut before the anchor or the study.

## 7. Publishing

The run is copied to `eval/results/published/` with `MANIFEST.json` (commit, model, timestamps,
cassette hashes). The README quotes only from `published/summary.json`. Every miss is in the README
by count and in `docs/EVALUATION.md` by variant, with what the report said instead and the report
path. The sentence to write, in some form: "on this study, `rules_only` catches classes {…} without
a model call; `full_agent` adds {…} and adds {n} false alarms on the controls; `plain_llm` catches
{…} and asserts {n} unevidenced findings."

## 8. Limitations, written before anyone raises them

Two subjects; one to two variants per class; one model; one run per pair for the headline table;
defects seeded by the same person who built the checks, so the study measures whether the agent
finds what its author knows to plant, not what it would find in the wild. Two recipes clear their
bounds thinly on synthetic data (`credit__L1__after_outcome_hidden` at 0.945 against 0.90; the SMOTE
slope arm at 0.795 against 0.80, D-136), and the real-data `pay_amt_next` is a constructed leak
whose realism is bounded by construction (§3). The loop's follow-up choices are the model's and
vary run to run, so `full_agent`'s Open items are a descriptive result, not a detection result. The
MSR half depends on the Freddie Mac sample being downloaded and the real MSR fit existing
(HANDOFF §7); until it does, MSR variants run on synthetic only.

## 9. Dates, freeze, amendments

- Protocol drafted 2026-09-09 in Cowork (`quaestor-package/phase12-draft/STUDY.md`), amended in
  place 2026-09-17 (§3, §4), committed to `docs/STUDY.md` on 2026-09-20.
- **The freeze is dated when this file entered the repository, which is after all 54 cells had
  run.** The protocol was decided and amended before those runs and no scoring rule was changed
  because of what they produced, but the file was not in the tree when they were made, and the
  date is not backdated to pretend otherwise.
- Model `claude-opus-5[1m]`, pinned with `--model` on every call; provider `ClaudeCLILLM`; data
  mode synthetic for all 54 cells. Scored 2026-09-20T23:31:20Z (`summary.json`, `generated`).
- Cost: `ledger.json`'s `cost_usd` reads **$127.265707** over 54 cells and counts each cell's
  **last attempt only**. Discarded attempts are absent from it: $15.9583 on two cells alone
  (D-192 amendment), plus a batch of fast-exit failures paid for on 2026-09-18. Sittings are one
  line per chunk in `PROGRESS.md`'s run log.

### Amendment 1 — 2026-09-20

1. **Collateral pairings are not judged after the fact.** §5 decided five pairings in advance; the
   run produced 93 collateral findings outside them and `score.py` set every one aside as
   `unjudged` (D-182). They are not judged here. A verdict written after the numbers were seen is
   a different object from a rule fixed before them, and judging 93 pairings now would make the
   study's main claim a construction of its own results. Every collateral finding outside §5's
   five pairings is therefore published as `unjudged`, in neither the numerator nor the
   denominator of precision, and the precision figures are precision **over the pairings decided
   in advance** — stated that way wherever they are quoted.
2. **Stability repeats (§6) were not run.** `03-RUNBOOK.md` §4 names them the cuttable item; they
   are cut. No Wilson intervals; one run per pair.
3. **The two real-data bridge runs were not made** and the four CSV-level transforms of §3 were
   never built (D-183). The study is synthetic on both subjects.
4. **Cost.** §4's "$70–110 and 5–7 hours" and D-180's $170.15 over 62 paid runs are superseded by
   the figures above.
5. **§8's MSR sentence is spent.** The Freddie Mac sample was built and the real MSR fit committed
   on 2026-09-16; the MSR half ran on synthetic anyway, by item 3.
6. **Added to §8.** The grounding judge fails about one reply in ten on its own tapes, beside its
   kappa of 0.771 against a human labeller (D-175). `pytest tests/probatio --cassette=replay`
   stands at 7 failed / 33 passed and is not fixed in this version (D-188).
7. **What the study found, recorded here because it is the reason §6 was cut.** `full_agent` and
   `rules_only` both detect 14 of 14 with 0 false alarms; the LLM adds no detection over the
   deterministic checks on these variants. Repeats of a configuration that ties its own ablation
   would measure the tie more precisely, not answer a different question.

### Amendment 2 — 2026-09-20, before the component eval's first live call

**The verifier component eval of `04` §6 samples 50 items per dataset, not 150.** The study's
budget was cut and the operator fixed the number at 100 items in total — 50 FinQA, 50 TAT-QA, 300
sentences — before any live call was made for it (D-194). The consequence is stated where the
figures are: a per-perturbation-type rate falls to roughly twenty sentences, which is indicative
and not a comparison between types; the headline status accuracies are over 100 items.

The deviation is **not** recorded only here. `SAMPLE_NOTE` is a field of `verifier_eval.json` and
the first line `quaestor verifier-eval` prints, so a figure read from a terminal or from the JSON
carries its own qualification. Nothing else of §6 changed: seed 20260901, arithmetic-answer items
only, the three sentences per item and their expected statuses, and the offline half on the ten
committed fixtures, all stand as written.

### Amendment 3 — 2026-09-20, correcting Amendment 1's collateral count

1. **Amendment 1 item 1's figure of 93 is wrong. The count is 46.** Amendment 1 says the run
   produced 93 collateral findings outside the five pairings §5 decided in advance. That figure was
   taken from a line count of the rendered report, not from the data. The renderer prints each
   unjudged finding **twice** — once as a row of the "Collateral findings" table and once as a
   bullet under "What was not scored, and why" — and one further line of the section's prose
   contains the word, giving 46 + 46 + 1 = 93.

   The count in the data is `collateral_unjudged: 46` in `eval/results/published/summary.json`,
   over **44 distinct `(variant, class)` pairings**, all of them in `plain_llm`; `full_agent` and
   `rules_only` have none. Two pairings carry two findings each — `msr__L2__contamination` raised
   `C1` at high and at medium, and `msr__S1__vintage_shift` raised `D1` twice — which is the whole
   of the difference between 46 and 44. Collateral at or above `medium` across all three arms is 63
   findings: 46 unjudged, 17 `true_consequence`, **0 spurious**.

2. **The rule Amendment 1 states is unchanged.** Every collateral pairing outside §5's five is
   published as `unjudged`, in neither the numerator nor the denominator of precision, and the
   precision figures are precision **over the pairings decided in advance** — stated that way
   wherever they are quoted. Only the count is corrected. No judgement is added, none is withdrawn,
   and no figure in `summary.json` or `eval/results/published/report.md` changes: those files always
   carried 46 and are what the scorer wrote.

3. **Amendment 1 is left as written.** A dated amendment that is silently edited is not a dated
   amendment, and the value of freezing a protocol comes entirely from the frozen text still saying
   what it said. The correction lives here, in its own dated entry, and `README.md` quotes 46 over
   44 pairings with `summary.json` named as the source.

4. **Recorded as D-198**, which also notes what this was: a quantitative claim in prose that no
   artifact supported, in the one document the verifier does not read.
