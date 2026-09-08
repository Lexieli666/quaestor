# Evaluation: what Quaestor has been measured on, and what it got wrong

Every number in this file comes from a run committed in this repository, and the run is named
where the number is used. `tests/test_live_credit_attempt1.py`,
`tests/test_live_credit_attempt2.py`, `tests/test_live_credit_attempt3.py` and
`tests/test_live_credit_attempt4.py` re-derive each
figure of section 1 from the trace it claims to come from, so a number that drifts from its run fails the suite rather than sitting in a
document. Where a figure was computed from a file the repository deliberately
does *not* hold — a real sample's rows — it says so at the point of use.

This document is not yet the evaluation the project is for. The seeded-defect study of
`04-SEEDED-DEFECT-STUDY.md` — detection precision and recall, false-alarm rate and per-report
grounding precision across three configurations, misses included — is Phase 12, the verifier
component eval on FinQA / TAT-QA is Phase 13, and the human anchor is Phase 14. Until those run,
what this file records is the one thing already measured: what happened the first time the
pipeline met a real model and a real sample.

Nothing here is a compliance claim. The reports the runs below produce are SR 11-7-*shaped*.

## 1. Defects found in live runs

Live runs are not tests. They pay for output tokens, they meet prose no fixture wrote, and they
run against real samples whose distributions no synthetic generator reproduces — so they find
things the offline suite structurally cannot. Each defect below is recorded as a numbered decision
and fixed in a named commit; none was found by review.

### 2026-09-08 — `credit_default`, `full_agent`, Claude CLI

The record is `eval/results/first-live/credit-attempt1/`.

**The run.** `quaestor validate subjects/credit_default --data … --llm claude-cli` against the
real UCI sample, configuration `full_agent`, model `claude-opus-5[1m]` through
`ClaudeCLILLM`. Committed: `trace.jsonl` (212 events), the 17 cassettes, `artifacts/` (121 logical
names) and `run/*.json`. Not committed: the row-level files, which are the real sample (D-087).

| quantity | value |
|---|---|
| model calls | **17** — 1 plan, 8 draft, 8 extract; no re-ask |
| tool calls | 13 — `run_model`, `profile_data`, `compute_metrics`, `check_leakage`, `check_collinearity`, `challenger_compare`, and `retrieve_guidance` seven times — 2.66 s in total |
| claim checks | **179**: **176 verified**, **2 unattributed**, **1 unsupported** |
| repair rounds | **1**, on section 3 — two numbers the extractor omitted (`9.982`, `6`) and one written with no citation (`3.3`); the drafter removed all three and all 140 post-repair claims verified |
| findings | 1 — `L2 contamination` at severity **high**, evidence `leakage.overlap` and `threshold.L2.overlap` (`F-000` on the trace, which is the id a finding carries before the document numbers it `F-001`) |
| output tokens | **92,196**, of which **63,865 (69.3%)** were the 8 extraction calls |
| longest single call | extraction of section 4: **20,257 output tokens, 197 s** |
| notional cost | **$3.82** as the trace records it, of which **$2.18** was extraction |
| wall-clock | **16:59** from the first traced event to the last (1,019 s) |
| report written | **none** — the renderer refused |

The wall-clock figure is the trace's span, which is what the committed record supports. The
operator's own shell clock read 17:02 for the whole command; the 3-second difference is interpreter
start-up before the first event and the refusal after the last, neither of which the trace records.

**The refusal.** After a clean repair round, `render_report` raised the message below. The trace
records no error event — it ends with the `repair` event — so this text is the renderer's own,
reconstructed from `report/schema.py` and the one uncovered token the check found:

```
the rendered report does not satisfy docs/REPORT_SCHEMA.md: these numbers in the prose are
covered by no verified claim and are not wrapped ⟦unverified: …⟧: ['1.0']
```

The `1.0` is in section 2: "The champion in credit_default 1.0 is a linear-in-log-odds
scorecard". It is the package version, which D-015 excludes from the claim set — and the
extraction pre-pass did exclude it. So a run in which every one of 140 claims verified produced no
report, after 17 model calls and 17 minutes, over a number nobody had claimed.

| # | what the live run exposed | kind | fixed in |
|---|---|---|---|
| DECISIONS D-084 | The renderer's uncovered-number check and the extraction pre-pass disagreed about which numbers are claims. The pre-pass is given `package_version` and excludes the version string; `uncovered_numbers` called the same masking helper with that argument defaulted away, so the version was a claim to one caller and not to the other. The repair loop's wrapper had the same defect and had not yet been paid for. | defect | `fix(live): one tokenizer, a cheaper extractor and an L2 rule for discrete data` |
| DECISIONS D-085 | The extraction prompt asked the model to copy back the whole line each number sits on. That made extraction 8 of the 17 calls and 63,865 of the 92,196 output tokens — 69% of everything the run generated — with the longest call at 20,257 tokens and 197 s, because a sentence carrying four numbers is re-typed four times, citations included. The caller already had the prose. | cost | same commit |
| DECISIONS D-086 | `check_leakage` raised `L2` at severity high on 1.2556% feature-vector overlap between train and test, against a 0.5% threshold. The panel's features are coarse integers and its identifiers are disjoint by construction: the overlap was two different clients writing the same row. The synthetic control could not have caught it, because `synthetic.py` draws continuous features and scores exactly 0.0. | false alarm | same commit |

All three ship in one commit, which cannot cite its own hash; the commit's subject is above and the
run-log line under Phase 9 in `PROGRESS.md` is written in the same commit.

**Why the first survived nine phases.** It lives in the seam between two features that had never
been exercised over the same text with a version to exclude. `tests/test_renderer.py` checks
`uncovered_numbers` on prose written by the test, `tests/test_verifier_extract.py` checks the
pre-pass on prose written by the test, and `tests/test_pipeline.py` runs both end to end under the
offline fake — whose drafter writes one sentence per artifact and has no reason to mention the
package's version. The version exclusion had a test; the *disagreement* had none, because no
fixture had ever put a version string into a section's prose. That is what a live drafter does on
its first paragraph, and it is why the fix is a single function both callers must go through rather
than a second argument at one call site: the trap was the default, and the default was wrong in two
places.

**The second is not a defect and is listed anyway.** Nothing computed the wrong answer. A field the
caller could have filled itself was being asked of the model, which D-063 already refuses to do for
`section`, `id` and `source` on the grounds that "asking a model for a value the caller can compute
is a way of being told a different one" — and the pre-pass's whitespace normalisation and substring
fallback exist because the copy did come back changed. It is here because the *cost* of that choice
is invisible from inside the offline suite: no test pays for an output token, so a prompt that asks
a model to re-type its input is free 1,120 times and 69% of the bill once.

**The third is the one the open evaluation exists for.** A severity-high finding that says the
held-out split is not held out invalidates every metric in the report, so it is the most expensive
false alarm the tool can produce — and it fired on the first real sample it ever saw, on a screen
that is exact on both synthetic controls. The fix does not move the threshold: it adds the
comparison the question needs. The share of *train* rows that repeat a feature vector inside train
is what coincidence looks like in this dataset, measured where contamination cannot be the
explanation, and the screen now fires only when the cross-split share beats twice it. On the
attempt's panel the cross-split share was 1.2556% (`leakage.overlap`, committed with the run)
against a within-train share of 1.1619% recomputed from that run's own `data_train.csv`, which is
not committed — a ratio of 1.08 where the rule asks for more than 2. A shared *identifier* is still
severity high on its own, at the unchanged 0.5%.

**What none of the three needed.** A live model. Each is a statement about Quaestor's own code that
a differently-shaped offline fixture would have caught. What the live run supplied was the
*shape*: prose that mentions a version, a bill that makes a redundant field visible, and a sample
whose features are discrete. That is the argument for running the operator's half of Phase 9
before the study rather than after it.

### 2026-09-08 — `credit_default`, `full_agent`, Claude CLI — second attempt

The record is `eval/results/first-live/credit-attempt2/`.

**The run.** The same command as the first attempt, on a build carrying D-084 to D-086. The plan
was clean and the run still produced no report: the bounded loop asked for `check_stability` on a
package that declares no `regime.column`, the tool raised, and the exception left `validate()`.

| quantity | value |
|---|---|
| model calls | **1** — the loop's first plan step, and the only one the run reached |
| tool calls | **14** — 13 of the rule-based plan, every one clean, plus the loop's `check_stability`, which raised — 2.69 s in total |
| artifacts stored | 124 across the 13 clean calls |
| candidates raised | **none** — including no `L2`, which is D-086's fix on the panel that provoked it |
| output tokens | **693** (628 of them thinking), on 2 input tokens |
| notional cost | **$0.10093** as the trace records it |
| wall-clock | **15.09 s** from the first traced event to the last, of which the plan call was 13.0 s |
| plan step | `check_stability({"split": "test"})`, **accepted**, then the tool raised |
| report written | **none** — `validate()` exited 1 |

The plan step is the whole of the run's agency and it is worth quoting. The model's stated reason
was "the plan only compared regimes on the fitting split, so regime-dependent degradation out of
sample is still untested" — a follow-up on a call the plan had never made, because on this package
it cannot: `check_stability` is in the rule-based plan only when `regime.column` is set, and
`credit_default`'s is not.

| # | what the live run exposed | kind | fixed in |
|---|---|---|---|
| DECISIONS D-088 | A `ToolError` from a loop-requested tool ended the run. Fourteen tool calls, 124 artifacts and a clean plan were discarded over the model's optional fifth question. The error is now caught: the step is traced `accepted: true`, `executed: false` with the tool's message, the message reaches the next step's prompt, and the pipeline drafts with what it has. A failing rule-based call is still the run's failure. | defect | `fix(planner): a bounded loop that survives a tool it may not call` |
| DECISIONS D-089 | The loop was offered all nine tool schemas, including three that cannot run on this package. The menu is now filtered by applicability — `check_stability` needs a `regime.column`, `run_scenarios` a hazard subject with `scenarios`, and `run_model` is never offered (spec §3.12) — and a request for a filtered tool is refused before execution with `not applicable to this package: …`. | defect | same commit |
| DECISIONS D-090 | The prompt said the plan "has already run" and then showed only the candidates it raised, so a planner could not tell a check that did not run from a check that ran and found nothing. The prompt now lists every completed call with its arguments and the classes it raised, and every earlier step of the loop with its refusal reason or its tool's error. | cost | same commit |

All three ship in one commit, which cannot cite its own hash; the commit's subject is above and the
run-log line under Phase 9 in `PROGRESS.md` is written in the same commit.

**Why this attempt is worth its own entry.** The first attempt's three defects were all in code
that had been exercised offline against prose no fixture wrote. This one is different: every
condition involved — a package without a regime column, a tool that raises, a loop bounded at four
steps — is in the offline suite, and `tests/test_planner.py` had a case for each of the loop's
three refusals. What no test had was the *combination*: an action that passes every rule the
planner applies and then fails inside the tool. The offline fake stops the loop at once (D-080),
and every scripted loop test asked for a tool that runs. So the fifth outcome had no test because
no fake had ever produced it, and the shape of the miss is the same as the first attempt's: not a
rule that was wrong, but a case that sat between two features which each had their own tests.

**What the fix does not do.** It does not let the model reach anything new, and it does not soften
the run's failure modes. `run_model` moves from "callable with the plan's arguments only" to "not
callable", the three refusals of spec §3.12 keep their own messages, and a `ToolError` from the
rule-based plan still exits 1. The only behaviour that became more permissive is the one the
attempt argues for: the loop's own extra question may now be answered "no" without taking the
report with it.

**Replayed, not re-enacted.** `tests/test_live_credit_attempt2.py` puts the recorded answer back
through `validate()`: `ReplayLLM` serves the run's single cassette under the key it was recorded
with, and the offline fake answers every call the attempt never made. On this build the same
action is refused — "not applicable to this package: package 'credit_default' declares no
`regime.column`, so there are no regimes to compare …" — the loop stops, and the pipeline renders
a report whose post-repair grounding precision is 1.0000. The cassette is **not** re-keyed onto today's prompt: D-089 and D-090 changed
that prompt deliberately and a cassette's key is a hash of the request, so what the test replays
is the live model's answer and not the question.

### 2026-09-08 — `credit_default`, `full_agent`, Claude CLI — third attempt, and the first report

The record is `eval/results/first-live/credit-attempt3/`. It is kept as the record of what the
pipeline produced on 2026-09-08; the excerpt the README will eventually carry comes from the run
**after** the fixes below, not from this one.

**The run.** The same command as the first two attempts, on a build carrying D-084 to D-090. It
rendered: 159 post-repair claims, grounding precision 0.9816 before repair and 1.0000 after, no
finding at any severity, exit 0.

| quantity | value |
|---|---|
| model calls | **19** — 1 plan, 9 draft, 9 extract; no re-ask. Seven sections, plus one repair re-draft each for sections 3 and 4 and their re-extractions |
| model | `claude-opus-5[1m]`, through `ClaudeCLILLM` — on every one of the 19 calls |
| tool calls | 13 — `run_model`, `profile_data`, `compute_metrics`, `check_leakage`, `check_collinearity`, `challenger_compare`, and `retrieve_guidance` seven times — 2.89 s in total, over 124 artifacts |
| candidates raised | **none**, by any of the 13 |
| plan steps (bounded loop) | 1 — the model stopped at once |
| claim checks | **247**: 244 verified, 2 unattributed, 1 unsupported |
| repair rounds | **2** — section 3 (`9.982` and `6`) and section 4 (`50`); all three numbers were **removed**, none rewritten. The first two are **one defect, not two numbers**: the section wrote `9.982e-06` and the tokenizer of the day had no exponent form, so it split the literal into `9.982` and `06` and no claim could ever have covered either half. It is D-099, found on the fourth attempt and unrecognised here |
| claims, post-repair | **159**, all verified |
| findings | **0** |
| output tokens | **104,675** — 525 plan, 34,003 draft, 70,147 extract |
| input tokens | **176,851** as the cassettes record them; **38** as the trace does (see D-093 below) |
| longest single call | extraction of section 4: **16,192 output tokens, 180.6 s** |
| notional cost | **$4.3822**, of which $2.4414 extraction, $1.8569 drafting, $0.0839 the plan |
| wall-clock | **20:18** from the first traced event to the last (1,217.79 s) |
| report written | **yes** |

**Two false sentences, both the tool's fault.** Every number in the report verifies; two of its
*sentences* do not follow from the numbers, and neither is a failure of the model's reasoning.

Section 3, on the contamination screen: "The measured share is above that bound, so the test split
is not a fully clean holdout under the package's own standard, and **this is recorded as a finding**
rather than as an observation." Section 6: "**No finding was raised** for the credit_default version
1.0 model package in this section." `findings.json` is empty, so section 6 is right. Section 3's
arithmetic is also right on the numbers it was given: it compared `leakage.overlap` = 0.01256 with
`threshold.L2.overlap` = 0.005. The bound the rule **applied** under D-086 is
`max(0.005, 2 × 0.011619)` = 0.02324, and 0.01256 does not exceed it — but that number existed only
inside the checking function's local scope, so it was not an artifact, the drafter was never shown
it, and no reader could have resolved a citation to it.

Section 4.4, on the developer-declared thresholds: the row `PSI, maximum 0.25` reads "Not
recomputed in the artifacts available to this section / Not evaluated here", while sections 1 and 3
of the same report both cite `psi.max` = 0.003083. And the table carries a row
`Wall-clock seconds, maximum 300` — the subject's runtime cap, listed among AUC and Brier as a
performance threshold. Both come from the drafter being asked to *assemble* that table out of the
loose scalars its selector matched: `threshold.package.` matched the runtime cap and did not match
`psi.max`.

| # | what the live run exposed | kind | fixed in |
|---|---|---|---|
| DECISIONS D-091 | A rule that derives its bound from the data kept that bound in a local variable, so the one number section 3 had to compare against was not an artifact and could not be cited. Every such rule now stores it — `threshold.L2.overlap.features_effective`, and `effective_name()` as the one spelling of the pattern — the candidate cites it, section 3's brief says which arm is read against which bound, and the section prompt states the candidate list explicitly, including the literal `candidates raised for this section: none -- describe nothing as a finding`. | defect | this commit |
| DECISIONS D-092 | Section 4 assembled the developer-threshold table itself and got two of six rows wrong. `compute_metrics` now writes `thresholds.evaluation` — one row per declared bound with the metric, split, bound, recomputed value and `pass`/`fail`/`not evaluated` — and the drafter writes `[[table:thresholds.evaluation]]` instead. The runtime cap moves to `runtime.max_seconds`, out of the threshold family; section 4's selector takes every `threshold.*` and `psi.*` scalar. | defect | same commit |
| DECISIONS D-093 | Three things the record got wrong about the run: `model: claude-cli` is the adapter, not the model the trace names on all 19 calls; `run_id` was `credit_default-full_agent-d03b07c6`, **the same string attempt 1 carries**; and Appendix C reported 38 input tokens against the 176,851 the cassettes record across `input_tokens`, `cache_creation_input_tokens` and `cache_read_input_tokens`. | defect | same commit |
| DECISIONS D-094 | The decile table printed `0.6855555556` four lines below prose that wrote `0.4952`: one number, two spellings. Renderer tables now print measures at four significant figures and integral cells as integers. | defect | same commit |
| DECISIONS D-095 | Section 2's best paragraph — utilisation enters negatively "against the standard view" — rested on nothing the run computed, and said so. `check_collinearity` now stores `sign_check.<feature>.{coef_sign,univariate_direction,agrees}` and `sign_check.n_disagreements`; `challenger_compare` stores `ablation.<feature>.delta_auc` against `ablation.baseline_auc`. Neither raises a candidate. | gap | same commit |
| DECISIONS D-096 | Section 6 was four sentences saying nothing was raised, while sections 2 and 3 had just made two observations a developer should answer for. Section 6 gains a required `### Open items` subsection. | gap | same commit |
| DECISIONS D-097 | Appendix A said "after 0 repaired claim(s)" of a run whose two repair rounds removed three numbers: only rewrites become `repairs` rows, and the removals live on the trace. The sentence now counts both. | defect | same commit |
| DECISIONS D-098 | Section 4's order was decided by the event rate alone, which asks the data what the model is for. `package.yaml` gains an optional `use: ranking \| probability \| both`; `credit_default` declares `ranking`, `msr_prepayment` `probability`; the report states which rule ordered it and cites `rule.calibration_first_event_rate` only where that rule was the reason. | gap | same commit |

All eight ship in one commit, which cannot cite its own hash; the run-log line under Phase 9 in
`PROGRESS.md` is written in the same commit.

**What the two false sentences have in common.** Neither is a hallucination and neither is an
arithmetic slip. In both the model was handed an incomplete set of artifacts and reasoned correctly
over what it had: a threshold it could see but not the threshold that was applied, and a family of
scalars whose membership was decided by a name prefix rather than by what the numbers are. That is
the same shape as D-084 — a fact one part of the pipeline knew and another did not — and the fix is
the same shape too: put the fact in the store, where anything that needs it can cite it. A prompt
instruction alone would not have been enough here and is not the fix: a drafter told "describe
nothing as a finding" while holding an exceedance it can demonstrate is being asked to write a
sentence it can see is wrong.

**What D-085 actually saved, measured.** D-085 replaced the extractor's copied-back line with a
line index and said the saving would be measured on the next live run rather than estimated. It is
measurable now, and it is not what the token totals suggest. Extraction output went **up**, from
63,865 tokens over 8 calls to 70,147 over 9 — but the two runs' cassettes separate reasoning from
answer, and the answer is the half D-085 changed:

| | attempt 1 | attempt 3 |
|---|---|---|
| extraction calls | 8 | 9 |
| claim checks | 179 | 247 |
| extraction output, total | 63,865 | 70,147 |
| — of which thinking | 33,833 (53%) | 47,550 (68%) |
| — of which answer | 30,032 | 22,597 |
| **answer tokens per claim check** | **168** | **91** |

So the field D-085 removed cost about what it was thought to: the answer more than halved per
claim. The bill did not fall, because reasoning grew faster than the answer shrank — a longer,
denser report is more to think about — and reasoning is now **68% of everything extraction
generates**. That is where the next cost decision has to look, and this entry claims no saving the
trace does not show.

### 2026-09-08 — `credit_default`, `full_agent`, Claude CLI — fourth attempt, and the first loop

The record is `eval/results/first-live/credit-attempt4/`.

**The run.** The same command as the first three attempts, on a build carrying D-084 to D-098. It
rendered: 161 post-repair claims, grounding precision 0.9641 before repair and 1.0000 after, no
finding at any severity, exit 0. It is the first attempt in which the **bounded follow-up loop did
anything**: four steps, three of them executed.

| quantity | value |
|---|---|
| model calls | **22** — 4 plan, 9 draft, 9 extract; no re-ask. Seven sections, plus one repair re-draft each for sections 2 and 3 and their re-extractions |
| model | `claude-opus-5[1m]`, through `ClaudeCLILLM` — on every one of the 22 calls |
| tool calls | **17** — the 13 of the rule-based plan, plus the loop's four `compute_metrics` calls, one of which raised — 3.16 s in total, over 192 artifacts |
| candidates raised | **none**, by any of the 16 that ran |
| plan steps (bounded loop) | **4**, all accepted; step 1's tool raised and steps 2, 3 and 4 executed |
| claim checks | **262**: 256 verified, 6 unattributed, 0 unsupported, 0 mismatched, 0 dangling |
| repair rounds | **2** — section 2 (`1.92`, `5`, `-5.589`, `5`) and section 3 (`9.982`, `6`) |
| claims, post-repair | **161**, all verified |
| findings | **0** |
| output tokens | **77,808** — 1,357 plan, 31,221 draft, 45,230 extract |
| input tokens | **219,975**, and the cassettes record the same figure: D-093's three-field sum agrees with the record for the first time |
| longest single call | an extraction: **9,359 output tokens, 102.9 s** |
| notional cost | **$4.1603**, of which $1.8347 extraction, $1.9922 drafting, $0.3333 the four plan steps |
| wall-clock | **15:09** from the first traced event to the last (908.59 s) |
| report written | **yes** |

**Every number in the report verifies, and its own record is accurate.** The three things D-093
fixed hold: the front matter names `claude-opus-5[1m]` and not the adapter, the `run_id` carries
the run's own UTC second (`credit_default-full_agent-20260908T090332Z-d03b07c6`), and Appendix C's
input-token figure is the one the cassettes carry. D-092's `thresholds.evaluation` table replaced
the drafted one and no row of it is wrong. What the reading found instead is **six failed claims
that are all one tokenizer defect**, and **six sentences or omissions that are all one shape**: a
section reasoning correctly from a brief that did not carry the fact its sentence needed.

**One defect, six claims.** The six pre-repair failures are `1.92`, `5`, `-5.589`, `5`, `9.982`
and `6`. There are three literals: `1.92e-05` and `-5.589e-05` in section 2's ablation sentences
and `9.982e-06` in section 3's characteristic-shift list. `NUMERIC_TOKEN_RE` had no exponent form,
so each split into a mantissa the artifact does not hold and a bare exponent — `1.92` and `05` —
and the pre-pass counted both against the report. Attempt 3's two removals of `9.982` and `6` were
the same defect one run earlier, recorded there as an extraction miss; that entry is amended above.
The drafter did not invent the notation: `json.dumps` writes a value of 1.9e-05 at four significant
figures as `1.92e-05`, and the drafting prompt is where it came from. So the pipeline taught the
drafter a form its own verifier could not read, and the grounding precision this project asks to be
judged on paid for it.

**The loop worked, and the report does not say so.** Step 1 asked `compute_metrics` for a
sub-population of `credit_limit`; the column is `limit_bal`, the tool raised, D-088 caught it and
D-090's history block carried the message into step 2, which asked again correctly. Steps 2, 3 and
4 computed `metrics.test.sub.limit_bal_low.*`, `.limit_bal_high.*` and `.delinq_count_6m_eq_0.*`.
The third is the observation of the run:

| | test split | `delinq_count_6m == 0` |
|---|---|---|
| rows | 9,000 | **6,048** |
| AUC | 0.7550 | **0.5875** |
| Gini | 0.5100 | **0.1749** |
| event rate | 0.2213 | 0.1212 |

On two thirds of the held-out split the model ranks barely better than a coin. Section 4's selector
matched all twenty-four of the loop's scalars and its drafter was shown every one of them, and the
report mentions none: the brief does not ask for them and the step's own stated reason —
"discrimination and calibration often collapse on the never-delinquent majority segment, which no
prior call examined" — was never passed to any prompt. That is the single largest thing this run
found and failed to surface, and it is what D-101 and D-102 are for. The number is not by itself a
defect: conditioning on a delinquency count also conditions on its correlates, so the segment is
also one of near-constant delinquency history, and what a developer should be asked is what the
model discriminates on inside it.

| # | what the live run exposed | kind | fixed in |
|---|---|---|---|
| DECISIONS D-099 | `NUMERIC_TOKEN_RE` had no exponent form, so `1.92e-05` tokenised as `1.92` and `05`. All six pre-repair failures are this one cause, over three literals, and attempt 3's `9.982`/`6` removals were the same defect unrecognised. Exponent notation is now one token, and the tolerance is the mantissa's precision at the exponent's scale — `1.920e-05` claims 10^-8 and is held to half of it. | defect | this commit |
| DECISIONS D-100 | Section 7 wrote that "no recomputed test Brier value is carried in this report's artifact store" while `metrics.test.brier` sat in the store and was cited in three other sections: the monitoring selector listed the declared ceiling and hand-listed three of the four recomputed values. Every section shown a declared bound is now shown the recomputed value for it, derived from the `thresholds.evaluation` rows, and `DRAFT_INSTRUCTION` forbids any section to call a quantity absent. | defect | same commit |
| DECISIONS D-101 | Three executed loop steps and twenty-four scalars reached the store and nothing reached the prose. A section whose selector matched a step's artifacts is now shown the step, its arguments and its `why`, and must report it under a required `### Follow-up analyses` subsection. | gap | same commit |
| DECISIONS D-102 | A follow-up result had no route to a developer's attention. A slice whose AUC gap exceeds `threshold.O1.slice_auc_gap` on at least `threshold.O1.slice_min_share` of the split is an open item in section 6 — a question, not a verdict — and both bounds are stored artifacts so the sentence can cite them. On this run's numbers the never-delinquent segment qualifies at 0.1676 and neither `limit_bal` half does. | gap | same commit |
| DECISIONS D-103 | Section 6, with nothing raised, enumerated seven reviews including "input data lineage" and "documentation of intended use and known limitations" — on a package whose Appendix D says it has no `docs/`. The prompt had asked it to "say what was checked instead" without giving it the list. It is now forbidden to describe what was reviewed; the renderer's "Checks that ran and raised no candidate" line is the enumeration. | defect | same commit |
| DECISIONS D-104 | Section 7 recommended leading with calibration below a 0.05 event rate "as this report does"; section 4 of the same report led with discrimination, and said so in its opening sentence. Section 4's ordering decision, rule and all, is now passed into section 7's brief. | defect | same commit |
| DECISIONS D-105 | Appendix A reported "1 claim(s) rewritten and 5 number(s) removed" of a round that rewrote none and removed six: `_pair`'s nearest-value fallback paired the removed `1.92` with the unrelated verified `2` of "2 are known at origination". The fallback now needs the same line — citations and numbers removed — or the same cited logical name. | defect | same commit |
| DECISIONS D-106 | The prose reads "flags 0.0 features": D-094 made integral values integers in the renderer's tables and left the drafting prompt out. | defect | same commit |
| DECISIONS D-107 | Step 1 asked for a sub-population of `credit_limit` on a subject whose column is `limit_bal`, spending a model call and a tool call on a static fact. The loop prompt now lists the data's columns. | cost | same commit |
| DECISIONS D-108 | `retrieve_guidance` ranked one list across both corpus documents, so the data-quality and sensitivity queries returned three SR 11-7 spans each and no SR 26-2 span at all, and sections 3 and 5 opened on text superseded in April 2026 while `SR26-2:IV.1` and `SR26-2:V.1.a` sat unretrieved. `k` is now per document, the revision's spans first, and which to cite stays the drafter's choice under D-055. | defect | same commit |

All ten ship in one commit, which cannot cite its own hash; the run-log line under Phase 9 in
`PROGRESS.md` is written in the same commit.

**What the six prose defects have in common.** Not one is a hallucination and not one is an
arithmetic slip. In every case the drafter reasoned correctly over what its prompt carried, and its
prompt was missing the fact the sentence needed: section 7 had a Brier ceiling and no Brier value,
and had section 4's ordering rule but not section 4's ordering; section 6 was asked for a list of
checks it had never been given; section 4 had twenty-four numbers and no question. That is the same
shape as D-084, D-091 and D-092 — a fact one part of the pipeline knew and another did not — which
is now the commonest of the twenty-four defects the four live runs have found. The fix is the same
shape too, and it is not a prompt instruction on its own: put the fact where the sentence that
needs it can see it, and say the rule once for every section rather than in the brief of the
section that got it wrong.

**What D-085 cost and saved on this run, and what that measures.** Attempt 3's entry measured
D-085's line-index change and reported that extraction output had gone *up*. On this run it is down:

| | attempt 3 | attempt 4 |
|---|---|---|
| extraction calls | 9 | 9 |
| claim checks | 247 | 262 |
| extraction output, total | 70,147 | 45,230 |
| **extraction output per claim check** | **284** | **173** |
| notional cost, whole run | $4.3822 | $4.1603 |
| wall-clock, whole run | 1,217.79 s | 908.59 s |

**None of that is a saving, and this entry does not claim one.** The extractor's code did not change
between the two runs: D-085 shipped before attempt 3, and nothing in `verifier/extract.py` differs
between the two builds. What differs is the report — a longer section 2 with an ablation family,
a shorter section 4 — and how much the model chose to think. Two runs of one prompt on one model,
n = 1 each, are a measurement of run-to-run variance and of nothing else, and the honest reading of
the two entries together is that the reasoning half of an extraction call is not stable enough for
either number to be evidence about the field D-085 removed. A cost claim about extraction needs
repeated runs, which is Phase 12's business.

**What the loop is worth, so far.** One live run of the bounded loop, four steps, $0.3333 and
30.5 s of model time, one column name the tool refused, and one observation — AUC 0.5875 on 6,048 of
9,000 test rows — that no rule in this project screens for and no other part of the pipeline would
have produced. It is also the strongest argument yet for the seeded-defect study's third
configuration: the rules found nothing on this panel, and the model's own question found the thing
a validator would most want to ask about.

**Still outstanding.** The `msr_prepayment` live run of `03-RUNBOOK.md` §3, and a `credit_default`
attempt on a build carrying D-099 to D-108. Both are the operator's, and neither has happened.
