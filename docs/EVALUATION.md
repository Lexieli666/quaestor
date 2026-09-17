# Evaluation: what Quaestor has been measured on, and what it got wrong

Every number in this file comes from a run committed in this repository, and the run is named
where the number is used. `tests/test_live_credit_attempt1.py`,
`tests/test_live_credit_attempt2.py`, `tests/test_live_credit_attempt3.py`,
`tests/test_live_credit_attempt4.py` and `tests/test_live_credit_attempt5.py` re-derive each
figure of section 1 from the trace it claims to come from, and `tests/test_archive_fixtures.py`
re-derives the figures of the last entry from the three archived runs together, so a number that
drifts from its run fails the suite rather than sitting in a document. The Probatio entry's figures
come from the committed tapes under `tests/probatio/cassettes/` and from
`.probatio/judges/grounding.validation.json`, which `pytest tests/probatio --cassette=replay` and
`tests/probatio/test_inputs_pinned.py` re-derive with no provider call; the one figure that is the
operator's observation across sittings rather than a committed artefact says so where it is used. Where a figure was computed from a file the repository deliberately
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
| repair rounds | **1**, on section 3 — three numbers, all **removed**, and all 140 post-repair claims verified. Two of the three, `9.982` and `6`, are **one defect and not two numbers**: the section wrote `9.982e-06`, the tokenizer of the day had no exponent form, and it split the literal into a mantissa and a bare exponent that no claim could cover. That is D-099, found on the fourth attempt and unrecognised here and on the third; this row said "the extractor omitted" until Phase 9 follow-up 5. The third, `3.3`, was written with no citation |
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
attempt on a build carrying D-099 to D-108. Both are the operator's; the second has now happened
and is the entry below.

### 2026-09-08 — `credit_default`, `full_agent`, Claude CLI — fifth attempt, and the first open items

The record is `eval/results/first-live/credit-attempt5/`.

**The run.** The same command as the first four attempts, on a build carrying D-084 to D-108. It
rendered: 285 post-repair claims, grounding precision 0.9827 before repair and 1.0000 after, no
finding at any severity, exit 0. The bounded loop ran four steps and **all four executed** —
the first run in which none of them raised — and the report carries the first `### Open items` the
pipeline has produced live: two of them, both questions for the model developer.

| quantity | value |
|---|---|
| model calls | **22** — 4 plan, 9 draft, 9 extract; no re-ask. Seven sections, plus one repair re-draft each for sections 4 and 7 and their re-extractions |
| model | `claude-opus-5[1m]`, through `ClaudeCLILLM` — on every one of the 22 calls |
| tool calls | **17** — the 13 of the rule-based plan, plus the loop's four `compute_metrics` calls, **none of which raised** — 3.56 s in total, over 250 artifacts |
| candidates raised | **none**, by any of the 17 |
| plan steps (bounded loop) | **4**, all accepted and all executed: `limit_bal below_median`, `delinq_last equals:0`, `delinq_last equals:1`, `utilisation above_median` |
| claim checks | **417**: 412 verified, 2 mismatched, 3 unsupported, 0 unattributed, 0 dangling |
| claims, pre-repair | **289** at **0.9827** |
| claims, post-repair | **285**, all verified |
| findings | **0** |
| output tokens | **123,170** — 1,400 plan, 45,370 draft, 76,400 extract |
| input tokens | **290,392**, and the 22 cassettes carry the same figure |
| longest single call | an extraction: **25,647 output tokens, 250.9 s** |
| notional cost | **$6.0535**, of which $2.7065 extraction, $3.0089 drafting, $0.3381 the four plan steps |
| wall-clock | **22:08** from the first traced event to the last (1,328.47 s) |
| report written | **yes** |

**Six of the seven defects the fourth attempt found did not recur.** The three exponent literals
`1.92e-05`, `-5.589e-05` and `9.982e-06` are one token each and all three verify (D-099); section 7
recommends a Brier ceiling and gives the recomputed 0.1385 beside it (D-100); section 6 says it
raised no finding in one sentence and does not describe what it reviewed (D-103); section 7 says
this report "presented discrimination before calibration", which is what section 4 did (D-104); no
count reaches the prose as `0.0` (D-106); and sections 3 and 5 both open on SR 26-2, on the spans
`SR26-2:IV.1` and `SR26-2:V.1.a` that the whole-corpus ranking had left unretrieved (D-108). The
seventh, **D-105, recurred** — it is defect 3 below, and the reason is that this report is the
first with four paragraphs of the same generated shape in it.

**The loop chose different slices from the fourth run's, and the two open items are the result.**
Attempt 4 sliced `limit_bal` twice and `delinq_count_6m == 0`; attempt 5 sliced `limit_bal` once,
`delinq_last == 0`, `delinq_last == 1` and `utilisation` — same prompt, same subject, same model.
Two of the four cleared the gap bound and two did not:

| slice of test | rows | share | AUC | AUC gap | event rate | mean predicted |
|---|---|---|---|---|---|---|
| the split | 9,000 | — | **0.755** | — | 0.2212 | — |
| `limit_bal < median` | 4,383 | 0.487 | 0.7477 | 0.007286 | 0.2877 | 0.2802 |
| `utilisation >= median` | 4,500 | 0.5 | 0.7781 | −0.02309 | 0.2658 | 0.2608 |
| `delinq_last == 0` | 6,975 | **0.775** | **0.6312** | **0.1238** | 0.1405 | 0.1371 |
| `delinq_last == 1` | 1,096 | 0.1218 | **0.6513** | **0.1037** | 0.3321 | 0.3858 |

Both delinquency slices exceed `threshold.O1.slice_auc_gap` at 0.08 on more than
`threshold.O1.slice_min_share` at 0.10 of the split, so D-102 carried both into section 6 as open
items, written as questions and not as verdicts. It is the same observation attempt 4 made and
failed to surface, on a different column, now in the report: the model ranks poorly inside a
segment selected on its own delinquency feature, and what the developer is asked is what it
discriminates on there. The report also reads the two the right way round — mean predicted sits
close to the observed rate on the `== 0` slice and above it on the `== 1` slice, so it says the
weakness is in ordering on one and in level on the other.

**Five failed claims, and four of them are not the drafter's mistakes.** Two counts were rounded by
the prompt itself (D-110), two slice-rule parameters and one section reference were never claims
(D-112), and the fifth is a pairing defect in the repair loop's own bookkeeping (D-111). What the
reading found that no number could is the sixth: a line the repair round rewrote without being
asked to, whose citations all resolve.

| # | what the live run exposed | kind | fixed in |
|---|---|---|---|
| DECISIONS D-109 | The repair round on section 4 flagged four numbers and the drafter, sent the whole section, also rewrote a line nobody flagged: "…by -0.02732 [[art:41fca294:metrics.train.sub.utilisation_high.auc_gap]] **is not the figure for this slice**; on train the gap is -0.001109…", a clause about another slice spliced into the limit_bal paragraph. Every citation resolves and every number matches, so grounding precision was 1.0000 and nothing downstream could see it. A round now re-drafts only the lines carrying flagged claims; every other line is kept byte-identical. | defect | this commit |
| DECISIONS D-110 | `four_significant_figures(10158)` is 10160, so two sub-population counts reached the drafter as numbers their artifacts do not hold, and the matcher holds a count to half a unit. Both failed as mismatches and one left the prose in the repair round. Integral values now reach the prompt exactly. | defect | same commit |
| DECISIONS D-111 | Appendix A reads "10160 (mismatch) → 10500 (verified)" and "1 rewritten, 4 removed" of a round that rewrote nothing and removed five: D-105's two pairing grounds are alternatives, and section 4's four slice paragraphs share one sentence skeleton. A flagged claim that cites a name is now paired only by that name; the line is for a claim with no citation. | defect | same commit |
| DECISIONS D-112 | Three tokens that are not claims were counted, flagged and removed: the `0` and `1` of "**delinq_last equals 0.**", which are a slice rule's parameters, and the `4` of "Section 4 of this report". A section reference is now an exclusion; a slice rule reaches the prose as inline code, `delinq_last == 0`, which the tokenizer has masked since D-015. | defect | same commit |
| DECISIONS D-113 | The prose reads "by up to threshold.O1.slice_auc_gap at 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]]": the logical name written twice, once in the sentence and once in the citation that carries it. The drafting prompt now says the citation carries the name. | defect | same commit |
| DECISIONS D-114 | Section 7 wrote that "benchmarking against an alternative internal or vendor model … was not part of this validation" three pages after section 2 reported the challenger comparison. Section 7's brief is now told a challenger was compared, where the run compared one. | defect | same commit |
| DECISIONS D-115 | Each follow-up slice wrote nine metrics on each of two splits into prose, one cited number at a time — 72 of 285 claims. `compute_metrics` now stores `metrics.<split>.sub.<slug>` as a table, the renderer expands it, and the brief asks for the directive plus the sentences that interpret it. | cost | same commit |

All seven ship in one commit, which cannot cite its own hash; the run-log line under Phase 9 in
`PROGRESS.md` is written in the same commit.

**What is new about D-109.** It is the first defect any live run has produced that the verifier is
structurally unable to catch. Every other prose defect in this document is a sentence that is wrong
about a number, or a number that is wrong about an artifact, and grounding precision is the measure
of exactly that. This one is a sentence that is wrong about *which slice it is describing*, written
by a repair round, with four correct citations in it. No claim-level check can see it, and the
answer is not a better check but a smaller blast radius: a round that was provoked by four numbers
may change the four lines those numbers are on.

**What extraction cost, and what that still does not measure.** Extraction output rose from 45,230
tokens over 262 claim checks to **76,400 over 417** — from 173 to **183** per check, against 284 on
attempt 3 and 357 on attempt 1:

| | attempt 1 | attempt 3 | attempt 4 | attempt 5 |
|---|---|---|---|---|
| claim checks | 179 | 247 | 262 | **417** |
| extraction output, total | 63,865 | 70,147 | 45,230 | **76,400** |
| **extraction output per claim check** | 357 | 284 | 173 | **183** |
| notional cost, whole run | $3.82 | $4.3822 | $4.1603 | **$6.0535** |
| wall-clock, whole run | 1,019 s | 1,217.79 s | 908.59 s | **1,328.47 s** |

Four runs, n = 1 each, and the same reading as attempt 4's entry: the per-check figure has moved
357 → 284 → 173 → 183 with no change to `verifier/extract.py` between the last three of them —
D-085 shipped between attempts 1 and 3 and nothing has touched that module since — so what the
column measures after attempt 3 is how much the model chose to think about differently-shaped
reports. The
*total* is a different matter and is not variance: this run checked 417 claims where the last
checked 262, because four executed slices wrote 72 more claims into section 4. That is what D-115
addresses, and it addresses it by removing the transcription rather than by making the extractor
cheaper. Whether the bill falls is Phase 12's to measure.

**What the loop is worth, so far.** Two live runs of the bounded loop. Attempt 4 found the
observation and could not report it; attempt 5 reported two, in the section a developer is asked to
answer from, with the bounds they were read against cited beside them. The rules found nothing on
this panel either time, and both times the model's own question found the thing a validator would
most want to ask about. It is also the most expensive part of the run to write up — 72 of 285
claims before D-115 — which is the trade the seeded-defect study's third configuration exists to
price.

**Still outstanding.** The `msr_prepayment` live run of `03-RUNBOOK.md` §3, and a `credit_default`
attempt on a build carrying D-109 to D-115. Both are the operator's, and neither has happened.

### 2026-09-08 — `credit_default`, `full_agent`, Claude CLI — sixth attempt, the README excerpt, and the first run with nothing to repair

The record is `eval/results/first-live/credit/`, committed under the bare name because it is the run
the README excerpts (D-120). `report.md` is committed as produced and is never edited; the five
wording edits the excerpt carries are listed verbatim in D-120 and will be printed as a before/after
diff in `docs/PROVENANCE.md` when Phase 16 writes it. No edit changes a number.

**The run.** The same command as the first five attempts, on `fc33dd7` — the build carrying D-084 to
D-119. It rendered: 210 claims, grounding precision **1.0000 before repair and 1.0000 after**, no
finding at any severity, no open item, exit 0. It is the **first live run with no repair round in
it**: nothing was flagged, so nothing was re-drafted, and the pre- and post-repair claim sets are
one document.

| quantity | value |
|---|---|
| model calls | **18** — 4 plan, 7 draft, 7 extract; no re-ask, and **no repair re-draft**, which is the first time |
| model | `claude-opus-5[1m]`, through `ClaudeCLILLM` — on every one of the 18 calls |
| tool calls | **17** — the 13 of the rule-based plan, plus the loop's four `compute_metrics` calls, **none of which raised** — 3.76 s in total, over 258 artifacts |
| candidates raised | **none**, by any of the 17 |
| plan steps (bounded loop) | **4**, all accepted and all executed: `limit_bal below_median`, `limit_bal above_median`, `delinq_count_6m above_median`, `utilisation above_median` |
| claim checks | **210**: 210 verified, 0 mismatched, 0 unsupported, 0 unattributed, 0 dangling |
| claims, pre-repair | **210** at **1.0000** |
| claims, post-repair | **210**, the same 210 |
| findings | **0**, and **no open item** |
| output tokens | **74,618** — 1,331 plan, 30,549 draft, 42,738 extract |
| input tokens | **207,429**, and the 18 cassettes carry the same figure |
| longest single call | an extraction: **14,316 output tokens, 141.0 s** |
| notional cost | **$3.9739**, of which $1.6208 extraction, $2.0168 drafting, $0.3364 the four plan steps |
| wall-clock | **14:33** from the first traced event to the last (872.74 s) |
| report written | **yes** |

**No repair round, so D-109 has still not run live.** The scoped re-draft shipped in follow-up 5
and the run that would exercise it is the run that flags a claim; this one flagged none. The six
rounds the archive holds were all made by builds without the scoping in them, so **no tape holds a
scoped re-draft** and the only replays of D-109's guarantee are the offline ones over those six
previous drafts (`tests/test_archive_fixtures.py`) and the fixture-level test of the claims
(`tests/test_repair.py`). That is a gap in the evidence and not a result.

**The loop's four slices, and why no open item was raised.** Slice choice is the model's, on the
same prompt, subject and model each time, and it has now differed on all three runs whose loop
executed: attempt 4 took `credit_limit` (refused), `limit_bal` twice and `delinq_count_6m == 0`;
attempt 5 took `limit_bal` once, `delinq_last == 0`, `delinq_last == 1` and `utilisation`; this run
took both `limit_bal` halves, `delinq_count_6m` and `utilisation`. The expressions below are the
rules **as this build resolved them**, which D-122 has since changed:

| slice of test | rows | share | AUC | AUC gap | event rate | mean predicted |
|---|---|---|---|---|---|---|
| the split | 9,000 | — | **0.755** | — | 0.2212 | — |
| `limit_bal < median` | 4,383 | 0.487 | 0.7477 | 0.007286 | 0.2877 | 0.2802 |
| `limit_bal >= median` | 4,617 | 0.513 | 0.7114 | 0.04359 | 0.1581 | 0.164 |
| `delinq_count_6m >= median` | 9,000 | **1** | 0.755 | **0** | 0.2212 | 0.2206 |
| `utilisation >= median` | 4,500 | 0.5 | 0.7781 | −0.02309 | 0.2658 | 0.2608 |

Every one of them is inside `threshold.O1.slice_auc_gap` at 0.08, so D-102 routed none of them to
section 6 and the report's `### Open items` says it recorded no observation of that kind. **That is
not the same as there being none.** Attempts 4 and 5 both found the never-delinquent segment
material — test AUC **0.5875** on `delinq_count_6m == 0` and **0.6312** on `delinq_last == 0`,
against a split-wide 0.755 — and this run did not test it. Its `delinq_count_6m` step was the whole
split (below), so the segment attempts 4 and 5 named went untouched. What a reader should take from
"no open item" is that this run's four questions found nothing, not that the model has none to
answer.

**One deterministic defect, found by reading, fixed in this commit.** The third step asked for
`delinq_count_6m above_median`. `above_median` was `>= median`, the median of `delinq_count_6m` on
this sample is **0**, and the rule therefore selected every row of both splits: share **1** on each,
an AUC gap of **0**, `n` of 21,000 and 9,000 — the splits' own counts — and 22 logical names per
split describing a population identical to its parent. The tool answered, the section gained two
rendered tables and three interpreting sentences, and one of four loop steps was spent. The drafter
described it honestly, and **that paragraph stays in the committed report**: it says the rule
"selected the whole of each split rather than a proper subset", and that the step "carries no
information about the delinquency-concentrated population beyond what the pooled result already
showed".

| # | what the live run exposed | kind | fixed in |
|---|---|---|---|
| DECISIONS D-121 | `compute_metrics` computed a sub-population that was the whole split. It now refuses one, on the D-088 path — the step is recorded accepted and not executed, the message names the resolved rule and the share, and the loop re-plans. The bound is a stored ceiling, `threshold.O1.slice_max_share` at **0.95**, rather than an exact share of 1: a slice holding 0.98 of its split has the same defect. The check is a pre-pass over every split asked for, so a slice degenerate on the second one stores nothing of the first. | defect | this commit |
| DECISIONS D-122 | `below_median` was `< median` and `above_median` was `>= median`, so on a discrete column whose median is its minimum the upper half was everything and the lower half nothing — and **neither rule could name** the never-delinquent segment attempts 4 and 5 found material. The two are now `<= median` and `> median`: they partition the split, the median's own rows are in the lower half, and on this column `below_median` is the 67% that has never been delinquent. | defect | same commit |
| DECISIONS D-123 | The loop prompt now states the rule — a sub-population must be a proper part of the split, where the median boundary falls, and that a rule resolving to the whole split is refused with the share it selected — so the planner does not spend a step of four finding out. It is D-089, D-090 and D-107's argument on the next fact. | cost | same commit |
| DECISIONS D-120 | The excerpt-edit policy, and the five wording edits verbatim. | policy | same commit |
| DECISIONS D-124 | The run joins `tests/test_archive_fixtures.py` as the archive's negative case: four rendered reports instead of three, no entry in any of the three expectation tables, and that absence asserted. | test | same commit |

All five ship in one commit, which cannot cite its own hash; the run-log line under Phase 9 in
`PROGRESS.md` is written in the same commit. `tests/test_live_credit.py` (30 checks) re-derives
every figure above from the committed directory.

**What extraction cost.** Extraction output was **42,738 tokens over 210 claim checks — 204 per
check**, the fifth reading of a series with no change to `verifier/extract.py` behind any of the
last four:

| | attempt 1 | attempt 3 | attempt 4 | attempt 5 | attempt 6 |
|---|---|---|---|---|---|
| claim checks | 179 | 247 | 262 | 417 | **210** |
| extraction output, total | 63,865 | 70,147 | 45,230 | 76,400 | **42,738** |
| **extraction output per claim check** | 357 | 284 | 173 | 183 | **204** |
| notional cost, whole run | $3.82 | $4.3822 | $4.1603 | $6.0535 | **$3.9739** |
| wall-clock, whole run | 1,019 s | 1,217.79 s | 908.59 s | 1,328.47 s | **872.74 s** |

357 → 284 → 173 → 183 → 204, **n = 1 at every point**, and no saving is claimed from any of it.
Five runs of one prompt on one model over five differently shaped reports is not a measurement of
extraction cost; what the column measures is how much the model chose to think, and a claim about
the cost of extraction needs repeated runs, which is Phase 12's.

**D-115, measured.** The fifth run wrote nine metrics per split per slice into cited prose — 72 of
its 285 claims — and D-115 replaced that with a table the renderer expands and three interpreting
sentences per slice. Both runs executed **four** slices. This run wrote **210** claims against the
fifth's **285** and cost **$3.97** against **$6.05**, with all 210 verified on the first pass. The
comparison is not controlled — different columns, different prose, seven drafting calls against
nine — so what it establishes is the direction and not a coefficient: the table form did not cost
the report its numbers.

#### What the excerpt does not show

The list Phase 16 quotes rather than rewrites. Every item is a property of this run or of this
build, and none of them is a defect fixed in this commit.

* **Zero findings and no open item, on a package that passes every bound it declares.** This is the
  clean control, and what it demonstrates is evidence and judgement — 210 numbers, each carrying a
  citation to a computed artifact, verified — and **not detection**. What Quaestor finds when
  something is wrong is Phase 12's seeded-defect study, with precision, recall, false-alarm rate
  and misses published. A reader shown only this report has been shown no detection result at all.
* **Loop slice choice varies between runs, and this run missed the segment.** Four steps, all
  executed, none of them the never-delinquent segment attempts 4 and 5 both found material at test
  AUC 0.5875 and 0.6312 against 0.755. "No open item" is this run's four questions coming back
  clean, not the package having no question to answer.
* **The degenerate step.** One of the four asked for a slice that was the whole split, reported the
  split to itself, and spent a step of four doing it. The paragraph describing it is in the excerpt
  deliberately. It is fixed in this commit (D-121, D-122) and was not fixed when the report was
  written.
* **Decile reversals go unremarked.** The test event rate is non-monotone at deciles 4 and 5
  (0.1711 against 0.1767) and at 8 and 9 (0.09667 against 0.1), and calibration bin 6 predicts
  0.1416 against 0.1767 observed. All three are in tables the report renders, and no sentence
  mentions any of them, because **no rule this build ships reads within-decile ordering**. A
  monotonicity rule is not a decision this commit takes.
* **A sign disagreement the report qualifies and does not route.** §2 records `bill_trend_6m`
  fitted positive against a negative univariate direction with an ablation delta of −0.001393 of
  test AUC — the largest of the three disagreements — and calls it "a reason to keep the
  specification under review". A validator would log that in open items with an owner. Today only
  D-102's slice rule routes anything there; a rule that routed a sign disagreement with a material
  ablation delta (D-095) is a DECISIONS question and not this commit's.
* **SR 26-2 and SR 11-7 citations are mixed.** §7's benchmarking paragraph cites `SR11-7:V.1.b`
  where the SR 26-2 retrieval returned no span for the same point; §3 and §5 open on SR 26-2. The
  mixture is D-108's retrieval doing what it can with two corpora and is visible in the excerpt.
* **One run, and no stability repeats.** Every figure in the excerpt is n = 1. Nothing here says
  what the next run of the same command would produce, and the five runs before it produced five
  different reports.

**Still outstanding.** The `msr_prepayment` live run of `03-RUNBOOK.md` §3, which waits on the
Freddie Mac download. The `credit_default` live validation is **done**: this run is it.

### 2026-09-08 — the archive as an offline fixture: what `pytest` found without a live call

No run. This entry is about the three archived runs above, read as fixtures rather than as history.

**Why the archive is worth reading again.** Every defect class in this document was found by a
person reading a rendered report — attempt 3 at $4.38 and 20:18, attempt 4 at $4.16 and 15:09,
attempt 5 at $6.05 and 22:08. All three runs are committed under `eval/results/first-live/` with
their reports, `claims.json`, traces, cassettes and artifact indexes (D-087), so the same reading
can be done by the suite, on the same bytes, at no cost and on every commit.
`tests/archivesupport.py` reads them; `tests/test_archive_fixtures.py` asks two questions of each.

**The tokenizer question, and why it has to be asked of the drafts.** Generalising
`tests/test_golden_spec.py` check 7 to the three live reports finds nothing: every eligible numeric
token of every one of the three bodies is covered by a post-repair claim, and every post-repair
claim has a token in the prose — 159, 161 and 285 tokens against 159, 161 and 285 claims. That is
worth having and is not where the defects are. **A repair round's answer to a number it could not
verify is usually to delete it, so a token that provoked a round is exactly the token the shipped
report no longer holds.** The same check over the twenty-one *first drafts* the three runs made,
recovered from their cassettes, leaves five residues:

| run | section | token in the first draft | what it is |
|---|---|---|---|
| attempt 3 | 4. Outcomes | `50`, of "under rule O1 **(D-050)** is 0.08" | **a new class** — DECISIONS D-116 |
| attempt 3 | 4. Outcomes | a second `0.08` | a verified claim an unflagged line lost — D-109 |
| attempt 3 | 3. Data integrity | `9.982e-06` | the exponent form — D-099 |
| attempt 4 | 2. Conceptual soundness | `1.92e-05`, `-5.589e-05` | the same, twice — D-099 |
| attempt 4 | 3. Data integrity | `9.982e-06` | the same literal, one run later — D-099 |
| attempt 5 | 4. Outcomes | `10160`, `16210` | counts the prompt rounded — D-110 |

**One new token class, and the run it came from.** `(D-050)`, in the first draft of attempt 3's
section 4: "The declared bound on the train-to-test AUC gap under rule O1 (D-050) is 0.08
`[[art:630f28f4:threshold.O1.auc_gap]]`". The `50` was counted in the denominator, reported
`unattributed`, and provoked a repair round — and that round's re-draft also rewrote the
neighbouring sentence "…the bound of 0.08 `[[art:630f28f4:threshold.O1.auc_gap]]` is not breached"
into "…the declared bound is not breached", so the report lost a *verified* claim to a line nobody
had flagged. One reference cost a model call and two claims. The drafter did not invent it: the
caption of the artifact the sentence cites reads "O1: the train-to-test AUC gap (D-050)", which is
what the drafting prompt showed it. D-116 takes both halves — `\bD-\d{3}\b` is a new exclusion
class `decisions_reference`, and no artifact caption carries a decision reference any more.

**The archive also says the reference is a choice and not a transcription.** Attempts 1 and 3 sent
byte-identical section-4 drafting prompts — the cassette key is a hash of the request and both runs
stored the tape under `a3a5316ac0480158` — and only attempt 3 copied the reference out of the
caption. So the exclusion is not redundant with the caption fix: a live model may write the form
whatever the prompt does.

**What the fixture measures about the exclusion.** An exclusion lowers the grounding denominator,
which D-015 names as the failure an exclusion list is most dangerous for, so the new class's blast
radius is asserted as an equality rather than argued: over the draft calls of all four archived runs
that made any, `decisions_reference` removes **exactly one token**, attempt 3's `D-050`.

**Three classes the archive shows a run earlier than the run that found them.** Not new, and that
is the point of a regression fixture:

* **D-099, the exponent form** — the same three literals in three runs. Attempt 1's trace records
  `9.982` and `6` as its only two unattributed claims, attempt 3 removed them, attempt 4 lost all
  six of its failed claims to them, and the class was named only at attempt 4. The fixture reads
  each literal as one token now, in every draft that wrote one.
* **D-112, a section cross-reference in words** — attempt 1's section 3 wrote "the contamination
  finding in section 3.3", and the `3.3` was one of the three flagged claims of that run's single
  repair round. It is excluded now, and the exclusion was decided at attempt 5, four runs later.
* **D-109, a repair round rewriting a line nobody flagged** — decided on one round of one run, and
  the archive holds six rounds over three runs. Replaying each against the previous draft its own
  repair prompt quotes: the drafter changed a line it was not asked about in **five of the six** —
  two lines in attempt 3's outcomes round, two and one in attempt 4's, two and three in attempt 5's
  outcomes and monitoring rounds, and none in attempt 3's data-integrity round. **Ten lines across
  the archive that the current build discards**, and on all six rounds `scope_to_flagged_lines`
  keeps every one of the previous draft's unflagged lines byte-identical — 39, 41, 41, 49, 52 and 23
  of them.

**What the D-111 pairing says of the three runs now.** Given each round's flagged claims and the
claims of the section after it, `_round_records` reports **attempt 3: 0 rewritten / 3 removed;
attempt 4: 0 / 6; attempt 5: 0 / 5** — the splits the entries above state. All three runs reported
one fewer removal and one rewrite at the time, because D-105's two pairing grounds were read as
alternatives; attempt 3's Appendix A is the third instance of that, unrecorded until now.

**What the cassettes cannot support, said rather than worked around.** The re-extraction that
followed each archived round ran on that run's own *unscoped* re-draft, so no tape holds the
extraction of a scoped one: the replay asserts the text a scoped round produces and not the claims
it would have yielded, and the test's docstring says so. Attempts 1 and 2 wrote no `claims.json` —
the first was refused by the renderer (D-084), the second exited 1 when a tool the loop asked for
raised (D-088) — so the coverage question cannot be asked of them; attempt 1's draft calls are read
all the same, against the verified `claim_check` events of its trace, which is where its `3.3` came
from.

| # | what the archive fixtures found offline | kind | fixed in |
|---|---|---|---|
| DECISIONS D-116 | Attempt 3's section 4 drafted "under rule O1 (D-050) is 0.08" and the `50` was counted, flagged and removed by a round that also cost the section a verified `0.08`. The reference came from the artifact caption the prompt showed. `\bD-\d{3}\b` is now an exclusion class, and no caption carries a decision reference. | defect | this commit |
| DECISIONS D-117 | `scope_to_flagged_lines`' fallback returns the whole re-draft when it can find no flagged line, and nothing on the trace distinguished that from a round that re-drafted every line. The `repair` event now carries `scoped`. No archived round took the path. | gap | same commit |
| DECISIONS D-118 | The archive fixture reads the drafters' completions and not only `report.md`, because a repair round removes the token the check is for; the coverage arithmetic is shared with check 7 and the tokenizer deliberately is not. | gap | same commit |
| DECISIONS D-119 | `tests/test_pipeline.py`'s two Phase 9 follow-up cases ran at 1,200 rows and asserted `"E1" in` the findings, which passes on a panel that also raises `T1` at high. They run at the default 5,000 and assert the set; the cost is 0.24 s a run. | defect | same commit |

All four ship in one commit, which cannot cite its own hash; the run-log line under Phase 9 in
`PROGRESS.md` is written in the same commit.

**Still outstanding.** The `msr_prepayment` live run of `03-RUNBOOK.md` §3, and a `credit_default`
attempt on a build carrying D-109 to D-119. Both are the operator's, and neither has happened.

### 2026-09-15 — the Probatio test layer: five record sittings, a judge measured against a human, and three classes a clean relation table found

No validation run. This entry is about `tests/probatio/` — ten cases, ten committed tapes, and what
five live recording sittings against `claude-opus-5[1m]` cost and found. The tapes are the record;
`pytest tests/probatio --cassette=replay` re-derives every figure below from them with zero
provider calls, and `.probatio/judges/grounding.validation.json` carries the judge's own
measurement.

**What the layer cost, against what it was estimated to cost.** D-145 estimated one record run at
**119 provider calls, $25.69 and 62 minutes**, from a least-squares fit over the eighteen calls of
the first committed live run. The four sittings that built the layer cost about **$71** — the
operator's figure across the sittings — and the fifth, the one-case re-record D-156 forced, cost
**$2.46 over 16 calls**, which is the only sitting whose whole spend survives as a tape. About
**$73** in all, against $25.69 for one run. The committed tapes account for **$28.95** of it, and
the gap is not waste that pruning created: two sittings died part way (D-155) and two rubric
revisions stranded what earlier ones had bought, so the calls were made and paid for and the tapes
they wrote are gone. D-158's pruning removes 64 interactions that no replay can reach and does not
move this figure by a cent. The $28.95 is the tapes **as this phase left them**: a sixth sitting on
2026-09-17 re-recorded `draft_section.summary` for D-165 and took them to $29.3297 over 123
interactions, which the entry for that work records. Three causes, none of them the cost model,
which predicted the whole of the first run's spend to within 6%:

* **The 120 s provider timeout.** The second sitting lost `data_integrity`, `sensitivity` and
  `monitoring` to `ClaudeCLIProvider`'s default hung-process ceiling, which was acting as a budget:
  a drafting call writing seven thousand tokens over a 39 KB prompt exceeds two minutes often
  enough to lose three cases in ten. Raised to 600 s in `addopts`, with a uniform 480 s per-case
  `max_latency_ms` beneath it, so a slow case now fails a verdict and only a hung subprocess errors
  (D-150). The latency regression that produced the old per-case ceilings was abandoned rather than
  re-fitted: it predicted `findings` at 15.1 s and one of its variants took **100.2 s**, out by a
  factor of 6.6.
* **Criterion 5 of the grounding rubric, over-tightened.** It collapsed "a quantity is absent from
  the store" into "an activity was not performed", and so failed sections 5 and 7 for writing
  exactly what their briefs ask for and what D-114 sanctions. Two of seven sections, independently,
  on the first recording whose judge replies parsed — and the grader was wrong and the drafter was
  right on both (D-153). The rewrite cost a re-record of seven tapes.
* **Judge replies that were not JSON.** Below.

**The judge's replies: 80% → 25% → 0 of 60.** The first rubric asked the judge to quote the
sentence that decided its verdict, inside the JSON string field the same prompt demanded, and
**16 of 20 replies (80%) stopped parsing at the first unescaped quotation mark** — every one of
them carrying a verdict Probatio then discarded, most of them passes (D-148). After that
prohibition, **8 of 32 (25%)** still failed, six by omitting the closing quote of a 250–450
character `rationale` and two by emitting a second, corrected object after the first (D-152). After
D-153's rewrite, which capped the rationale at fifteen words and forbade anything after the closing
brace, **0 of 60**. The fifth sitting's eight judge replies also all parse.

**The consequence for the relation rates, stated because it is the reason two recordings' figures
are not published.** A case's verdict is its original run's assertions, and all four complete
drafting cases of the second recording passed 4 of 4. The eight malformed replies were all on
metamorphic *variants*, so each one made a variant's verdict differ from its original's, which
Probatio reports as a relation violation. The counts matched exactly — `distractor_robust` 1 of 4,
`format_jitter` 3 of 12, `order_invariant` 4 of 12, **8 violations against 8 malformed replies**.
So on the first two recordings **every observed relation violation was a JSON formatting failure in
the grader**, not a change in the application: those relation rates measured the grader, and they
are not this layer's published numbers.

**The relation table as committed**, from the tapes as they now stand — six flips over 49 variant
runs, every one of them a judge assertion and none of them a parse failure:

| relation | cases | violations | mean rate | worst case | worst rate |
|---|---:|---:|---:|---|---:|
| `distractor_robust` | 7 | 1/7 | 0.14 | `draft_section.summary` | 1.00 |
| `format_jitter` | 7 | 2/21 | 0.10 | `draft_section.findings` | 0.33 |
| `order_invariant` | 7 | 3/21 | 0.14 | `draft_section.conceptual_soundness` | 0.33 |

`extract_claims.conceptual_soundness` runs under `@flaky_tolerant(p=0.8, n=5)` and passes **5 of 5,
a rate of 1.00 with a 95% Wilson interval of [0.57, 1.00]** against its 0.8 floor — an interval
that wide is a statement about five runs and not about the extractor, which is D-144's point and is
repeated here rather than left to be misread.

**The judge measured against a human: kappa 0.771.** The operator labelled **40 drafter outputs**
against the committed rubric — all five live judge fails plus a round-robin across the seven
sections, shuffled, the judge column hidden until the labels were in — and
`probatio validate-judge` reports **n=40, agreement 0.950 (38/40), Cohen's kappa 0.771**. Both label
distributions are 35 pass / 5 fail. The 2×2 of (human, judge):

| | judge pass | judge fail |
|---|---:|---:|
| **human pass** | 34 | 1 |
| **human fail** | 1 | 4 |

The two disagreements are the interesting rows and both are boundary questions the rubric does not
answer (D-157):

* **`conceptual_soundness-03`, human pass / judge fail at 0.60**, on "uncited word-numbers like
  ten, seven, two and a half". The human read criterion 1's "every number" as digits — the
  tokenizer's reading, and therefore the reading the whole verifier operates under — and the judge
  read spelled-out words as numbers. The sentence at issue, "roughly two and a half times that
  bound", is a **derived ratio of two artifacts that exists nowhere in the store**. The rubric is
  silent on words and two careful graders split on it.
* **`summary-03`, human fail / judge pass at 1.00.** The human failed "No findings were raised for
  this section, so no severity is assigned here" as a criterion-5 absence statement. The judge
  passed it — while having **failed** `summary-07`'s near-identical "no severity counts exist to
  report in this section" at 0.80 on that same criterion. This row is the judge being inconsistent
  at its own boundary, not two readings of one rule.

**0.771 is recorded as it stands and the rubric is not revised on the strength of these labels.**
Revising a rubric after reading the human's labels and re-grading the same 40 rows would tune the
judge to the labels, which is choosing a threshold on a test set. Both boundary questions —
whether spelled-out words count as numbers, and where criterion 5's line falls in D-103's terms
("no findings were raised" is a statement about the run and is allowed; "no counts exist to report"
asserts a quantity's absence and is not) — go to the Phase 12 pre-flight alongside the
`DRAFT_INSTRUCTION` change, and a revised rubric is validated on a **fresh** label set.

#### Three classes the clean relation table found, each with the tape it came from

These are what the layer was built for: defects visible only because a live model was shown a real
prompt eight times.

**1. Section 6 was told to describe nothing as a finding and then ordered to describe one —
`draft_section.findings`, the tape recorded 2026-09-09.** The prompt carried `candidates raised for
this section: none -- describe nothing as a finding` (D-091) and, eleven lines below it, `Findings
to write about, in this order` with `### F-001 · E1 effective challenge · severity **low**`. Not an
accident of the case: `SECTION_FOR_CLASS` maps no defect class to the findings section, so
`candidates_by_section` is empty for section 6 on **every** run, and every section-6 prompt this
project has ever built for a package with a finding said both things. **All eight recorded drafts
resolved it the same way**: a sentence saying no finding was raised, and `E1` moved into
`### Open items` as a question for the developer. Every number in all eight is cited and correct —
0.824, 0.748, 0.07598, 0.03 — and the grounding judge passed 8 of 8 at 1.0. So the failure mode is
**silent demotion with perfect grounding**: a published finding disappears from the findings
section, from the severity counts and from anything that reads them, and nothing in this project can
see it, because the verifier measures whether numbers match the store and the judge measures
grounding, and both were satisfied. The prompt's two halves are now one object (D-156), the tape
was re-recorded, and all eight new drafts write `F-001` under its own heading.

**2. The drafter writes about any artifact it is shown — `draft_section.summary` and
`draft_section.findings`, the `@distractor_robust` variants.** The distractor is one artifact of the
*other* subject, `projection.convexity`, a mortgage-servicing rate-shock number with no place in a
credit report (D-141). Section 1 wrote it into its prose — "a change in servicing value under a plus
or minus 300 basis point parallel shock of -168055 dollars
`[[art:0d15720c:projection.convexity]]`" — and section 6 made it an **open item**, a question for
the model developer about a model the package does not contain. The citation resolves and the value
matches, so the judge passed section 6's version at 1.0 and failed section 1's **only** for the
incidental `300` carrying no citation of its own. Nothing else caught either. That is why **open
items become rule-minted in the Phase 12 pre-flight**: an open item is currently the one thing in
the report a model may invent from whatever it was handed, and a selector bug is enough to hand it
anything.

**3. Spelled-out quantities walk past the verifier — `draft_section.conceptual_soundness` under one
artifact ordering, and `draft_section.findings` under one ordering and one jitter.** "which exceeds
the effective-challenge threshold of 0.03 `[[art:e042774c:threshold.E1.delta_auc]]` by roughly a
factor of **two and a half**" is a ratio the drafter computed from two artifacts; it is in no store,
it carries no citation, and the extractor's tokenizer does not see it at all, because nothing
tokenises a number written in words. It reached the reports only because the judge happened to read
words as numbers — inconsistently, which is disagreement (i) above. Three of the 49 variant runs
wrote one. This is why `DRAFT_INSTRUCTION` gains a **no-spelled-out-quantities** rule in the Phase
12 pre-flight: the drafter can be told not to write them far more cheaply than the verifier can be
taught to read them, and the rule is checkable offline.

**What this entry does not show.** One recording of each case, so every rate here has n = 8 at best
and n = 1 at worst; the relation violations are all judge assertions, so what they measure is a
grader's stability as much as a drafter's; the kappa rests on 40 rows with five failures in each
margin, where moving one cell of the 2×2 moves it by about 0.1; and the three classes above are
three that eight samples of seven prompts happened to surface, not an enumeration.

### 2026-09-16 — `msr_prepayment`, the first real sample offline: the clean control is not clean

The record is `subjects/msr_prepayment/artifacts/real/` and `package.yaml`'s `data.manifest`. No
live call was made: this is `quaestor validate subjects/msr_prepayment --data … --llm fake`, run by
a human against the Release 47 Freddie Mac sample panel, whose rows this repository does not hold.

D-047 fixed this subject's expectation at **no finding at all** — the hazard subject is the control
whose champion is the correct functional form for its process, against the credit subject's
deliberately misspecified one. That expectation holds on the synthetic panel and **does not hold on
the real one**. The validate raises exactly one finding: `C1` at severity **medium**, merged from
two candidates, on the `out_of_time` and `vintage_holdout` splits — calibration slope **0.432**
out-of-time against the declared [0.80, 1.20] band, and mean predicted-to-observed gaps of
**0.4618** and **0.4932** against the 0.25 threshold. Grounding precision is 1.0000 pre- and
post-repair over 51 claims and 271 artifacts, and `T1`, `O1`, `S1`, `D1`, `L1`, `L2`, `R1`, `M1`,
`E1` and `X1` raise nothing. The finding is **correct**: a hazard fitted through 2019
under-predicts the 2020–21 refinancing wave by about half, out-of-time CPR 0.203 observed against
0.114 predicted and vintage holdout 0.210 against 0.112. It is a fact about the model, not a false
alarm, and `C1` is scoped to every split deliberately (`metrics.py`'s module docstring) because a
calibration slope on a period split is the model's own claim about that period, where PSI on one
compares populations defined to differ (D-046).

This is the first control measured on real data that carries a finding, and it changes how the
Phase 12 study must score. **D-161** is the rule: every control carries a **baseline finding set
per data mode**, measured with `--llm fake` and written into `eval/taxonomy.yaml` before the study
runs, and a baseline finding on a control is **not** a false alarm. Detection of a baseline class on
a seeded variant of the same subject and data mode then requires evidence *outside* the baseline —
for `msr__C1__oversampled_hazard` on real data, a `C1` whose evidence includes a **test-split**
artifact, since the clean control's test slope is 0.966 — **1.0168** from the estimator fix
recorded below onward — and its test mean-ratio gap about 4 %. The two alternatives were refused
in writing: re-scoping `C1` to the test split is choosing the scoping that makes the control pass
after seeing the control, and refitting the subject until the validator
has nothing to say inverts the roles the study depends on. The four measured baselines are in the
taxonomy; the two perturbed controls are `null` until the Phase 12 pre-flight measures them.

One defect in the **package**, found by the same run and not by review. The first draft of this
commit declared three developer claims, the third being the test calibration slope of 0.966 that
the subject's `metrics.json` reports. It came back `mismatch` and minted a `T1` at medium: the
subject computes its slope with `sklearn.linear_model.LogisticRegression` at the default `C = 1.0`,
a penalised fit, while `quaestor.tools.stats.calibration_slope_intercept` computes the unpenalised
maximum likelihood estimate and reads **1.017** on the same split. On four synthetic samples of the
four splits' sizes and event rates the two estimators differ by −0.005 to +0.059, so the 0.051 gap
is the estimator and not the panel. The claim is dropped rather than restated at the validator's
number, for the reason D-160 gives, and the package ships two claims: `auc test 0.655` and
`brier test 0.00906`, both verified.

**Closed by `fix(msr): the subject reports the unpenalised calibration slope, and a real run
records its manifest check` (2026-09-16).** The defect was ours and not the developer's, so the fix
is in the subject rather than in the claim list:
`subjects/msr_prepayment/code/run.py::_calibration_slope` now fits the maximum likelihood slope
the way `calibration_slope_intercept` does — unpenalised at `C = np.inf`, and converged at
`tol = 1e-10` rather than lbfgs's default 1e-4 — and the two now agree to about 1e-9 on all four
splits.

**The diagnosis in the paragraph above was wrong about which half mattered**, and the decomposition
is the useful part of this entry. Penalised / unpenalised at the default tolerance / unpenalised and
converged, on the real splits: test **0.965971 / 0.966011 / 1.016836**, train 0.957077 / 0.957093 /
0.997101, out-of-time 0.432127 / 0.432172 / 0.432126, vintage holdout 0.850647 / 0.850950 /
0.850199. The penalty moves the test slope by **4e-5** — at 135,060 rows and two parameters
`C = 1.0` is nearly no prior — and the entire **0.0508** gap was lbfgs stopping on the gradient
short of the optimum. Removing the penalty was still right, because spec 3.7 means the maximum
likelihood estimate, but a fix that had removed only the penalty would have re-run the panel, moved
nothing, and left the two estimators exactly as far apart. The gap appears only where the slope is
near 1: at 0.43 out-of-time the default tolerance is already converged to 5e-5, which is why it read
as a shrinkage effect.

The four `calibration_slope` values in `artifacts/real/metrics.json` are the only four numbers the
re-run moves — test 0.966 → 1.0168, train 0.957 → 0.9971, out-of-time 0.4321272 → 0.4321258,
vintage holdout 0.8506 → 0.8502 — and AUC, Brier, CPR, the coefficients, the splits, the features
and the projection are byte-identical. The claim is back as `calibration slope test 1.017`, at four
significant figures rather than three so that `tolerance_for`'s half-a-last-decimal rule admits it,
and the `--data --llm fake` re-run verifies all three developer claims and still raises exactly the
one `C1` at medium on the same nine evidence artifacts. An offline test now asserts the two
estimators agree to 1e-6, which is what stops the pair drifting apart a second time (D-160's
consequence paragraph).

**What this entry does not show.** One panel, one seed and one fit, so the baseline it measures is
a measurement of this sample and not a property of mortgage prepayment models; and it is a
fake-LLM run, so nothing here is evidence about drafting, repair or a model's judgement — the
`msr_prepayment` live run remains outstanding and will be the first live run with a finding to
write about.

### 2026-09-16 — `R1`'s sign-flip rule reads a coefficient's precision, and a control stays clean

No live call and no new run of anything: this is the offline `--llm fake` suite plus five
re-measured validates, recorded because a detector rule changed and the number it changed is the
false-alarm rate the Phase 12 study will publish. `tools/stability.py` fitted its per-regime
comparison with scikit-learn's **penalised** default at lbfgs's default stopping tolerance, under a
docstring that said "unpenalised" — the same defect D-160 found in a subject, in our own code, and
left open there for a reason that turned out to be false. Converged at `C = np.inf` and
`tol = 1e-10` (D-163), the coefficients move by up to 0.31 on the synthetic hazard panel, the
regime AUCs do not move at all, and the real MSR finding set is untouched.

**What the fix exposed is the useful part.** On the clean synthetic hazard control the converged
`burnout` coefficient in the rising regime goes from −0.0008 to **−0.0943**, crosses
`threshold.R1.sign_flip_coef` of 0.05, disagrees in sign with the falling regime's +0.2235, and
raises `R1` at medium on a control D-047 and D-161 fix at exactly `{}`. Its standard error is
**0.290** — nearly six times the gate it cleared — on **fifty events for ten features**, its
**z is −0.32**, and its 95 % interval covers zero and both signs. An absolute gate on a quantity
whose precision varies by two orders of magnitude between the regimes of the same panel decides a
finding by where a point estimate happens to land; D-047 had already recorded that one weak
coefficient flips at each of four other seeds tried, which is the same observation from the other
side.

So `R1` now asks both questions. A flip must clear `threshold.R1.sign_flip_coef` (unchanged, 0.05,
materiality) **and** `threshold.R1.sign_flip_z` (new, 2.0, precision) in **every** regime, with the
standard errors coming from each regime fit's own observed information and stored beside the
coefficients so a reader can see them (D-164). The tightening was decided on **2026-09-09** for a
different pair of cases, and 2026-09-16 moved only *when* it ships — before the MSR live run
rather than in the Phase 12 pre-flight — so that the live run's §5 is computed by the rule the
study will use. Measured offline afterwards: the clean synthetic hazard control is **`{}`**, the
real MSR control is the same one `C1` at medium on the same nine evidence artifacts, synthetic
credit is `{E1 low}` with no `stability.*` artifact at all, and the seeded
`credit__R1__regime_flip` still fires with `bill_trend_6m` at **z = +7.77 and −11.13** — a factor
of four clear of the new gate, so no recipe parameter moves. The two collateral `R1`s D-136
recorded — `burnout` on `msr__L2__contamination` (z **+1.97 / −0.17**) and `sato` on
`msr__S1__vintage_shift` (z **−0.70 / +1.11**) — are gone, as are D-130's two collateral flips on
the seeded variant (`delinq_max_6m` at z +0.69 / −0.68, `pay_ratio_last` at z −1.84 / +1.07).
**No baseline in `eval/taxonomy.yaml` moves**, which is the result rather than a side effect: the
detector stopped reporting four findings it could not have defended, and kept the one it could.

**What this entry does not show.** `z = 2.0` is a convention and not a measured optimum; nothing
here establishes how many true regime instabilities a two-standard-error gate would miss, and the
only positive case it has been exercised against is one seeded recipe that clears it by a factor
of four. The four cases it removed were all on synthetic panels. Whether the gate is right on a
real panel with a real regime effect is a question for the Phase 12 study and the MSR live run,
neither of which has run.

### 2026-09-16 — `msr_prepayment`, `full_agent`, Claude CLI — the first live run with a finding to write

The record is `eval/results/first-live/msr-attempt1/`. It is named `msr-attempt1` for the reason
D-087 named `credit-attempt1`: it is one attempt of several the runbook expects, and its section 1
carries a defect that makes it the wrong run to excerpt. It is archived, not superseded — every
number below is re-derivable from the committed trace, claims and findings.

**The run.** `quaestor validate subjects/msr_prepayment --data … --llm claude-cli --model
"claude-opus-5[1m]" --config full_agent`, started 2026-09-16 23:56 UTC, **exit 0**, and it
rendered. It is the **first live run of the hazard subject**, the **first live run against a
sample this repository does not hold that is not the UCI credit panel**, and the **first live run
with a finding to draft**: the six previous live runs are all `credit_default`, and the one that
raised `L2 high` on attempt 1 never reached a report. Committed: `trace.jsonl` (475 events), the
23 cassettes, `artifacts/` (320 logical names) and `run/*.json`. Not committed: the row-level
files, which are the real sample (D-087, and the sweep below).

| quantity | value |
|---|---|
| model calls | **23** — 4 plan, 9 draft, 1 re-ask, 9 extract |
| model | `claude-opus-5[1m]`, through `ClaudeCLILLM` — on all 23 |
| tool calls | **19** — the 15 of the rule-based plan (`run_model`, `profile_data`, `compute_metrics`, `check_leakage`, `check_stability`, `check_collinearity`, `challenger_compare`, `run_scenarios` and `retrieve_guidance` seven times), plus the loop's four `compute_metrics` calls — **28.73 s** in total, 17.12 s of it the subject's own fit, over 320 artifacts |
| plan steps (bounded loop) | **4**, all accepted and all executed: the incentive 2×2, `above_median` and `below_median` on each of `out_of_time` and `vintage_holdout` |
| claim checks | **426** trace events over the two rounds |
| claims, pre-repair | **305** at **0.9934** — 303 verified, 1 mismatch, 1 unsupported, 0 dangling, 0 unattributed |
| claims, post-repair | **304** at **1.0000**, after 2 repair rounds that rewrote no claim and **removed two numbers** |
| findings | **1** — `F-001`, `C1 calibration` at severity **medium**, **six candidates merged**, nine evidence artifacts; three open items |
| developer claims | **3 of 3 verified** — `auc test 0.655`, `brier test 0.00906`, `calibration_slope test 1.017` |
| output tokens | **141,514** — 1,712 plan, 51,048 draft, 5,462 re-ask, 83,292 extract |
| input tokens | **352,860** |
| longest single call | an extraction: **17,802 output tokens, 178.4 s** |
| notional cost | **$7.1697** — $0.4169 the four plan steps, $3.3090 drafting, $0.5157 the one re-ask, $2.9281 extraction |
| wall-clock | **25:50** from the first traced event to the last (1,549.94 s); the operator's shell clock read 26:09 |
| report written | **yes** |

**Against the credit excerpt run, which is the only fair comparison.** That run
(`eval/results/first-live/credit/`) cost **$3.9739** over **14:33** (872.74 s) for 18 model calls
and 210 claims; this one cost **$7.1697** over **25:50** for 23 calls and 305. The difference is
not drift. This run has **a finding to draft** — section 6 writes `F-001`'s six-paragraph
narrative and three open items where the credit run wrote one sentence and none — it drafts and
extracts **nine** sections against seven because two were re-drafted, it carries **one re-ask** at
$0.5157 that the credit run did not need, and its four loop steps put 39 new logical names into
the store each, which section 4 then reports. Per claim the two runs are $0.0189 and $0.0235.

**What held, and it is most of the run.** D-156 held in section 6: the drafter was handed the
findings document, named `F-001` under the heading the prompt gave it, and did not move the
finding to the open items — the failure mode of all eight recorded drafts before the fix. D-162's
manifest table is cited in section 3 (`data.manifest`, five files verified against `package.yaml`)
and its Appendix C row is present. D-164's z gate is cited in section 5: the sign-flip screen is
reported as a coefficient magnitude of 0.05 **and** an absolute z of at least 2, and no feature
meets it. The bounded loop ran a coherent 2×2 rather than four unrelated slices, and its own
`why` strings say so.

**The substantive result, which is the model's and not the pipeline's.** Three of the four slices
breached `threshold.O1.slice_auc_gap` at 0.08 and became open items: `out_of_time` high-incentive
AUC **0.6046** (gap 0.08523), `vintage_holdout` low-incentive **0.5956** (gap 0.1432), and
`out_of_time` **below**-median incentive at **0.5198** (gap 0.17) — a segment holding half the
split on which the model ranks barely better than chance. That is the finding a reader of this
report should carry away, and no rule minted it: D-102 routed all three to section 6 as questions
for the developer.

**Per-section grounding, pre-repair, as `claims.json` records it.** summary **12/12**,
conceptual soundness **70/70**, data integrity **72/72**, outcomes **91/92**, sensitivity
**29/30**, findings **22/22**, monitoring **7/7**. The sections in which **every claim verified
before any repair** are therefore **1, 2, 3, 6 and 7**; the two that did not are section 4, on
claim `8dc85fe2b8ce10b4`, and section 5, on claim `e08daa963ce63f32`.

**Neither of those two is a false sentence, and that is the point of recording them separately.**
Section 4 wrote "the decile separation on test, with decile 1 holding the highest probabilities" —
a bin label, true, and tokenised as a claim of value 1.0 with no artifact behind it. Section 5
wrote "the servicing value falls by 1078000" against
`scenario.value_change.-300 = -1077724.40` — a magnitude inside tolerance (275.6 against 500),
whose sign the verb carried and the matcher did not read. Both are defects in **our** tokeniser
and matcher, and the repair loop's corrections made the prose worse in both places: "the first
decile", a word-number our own repair instruction asked for, and "changes by -1078000", which
verifies and reads badly. Section 1's defect is of the third kind and is the reason this run is
archived.

| # | what the live run exposed | kind | fixed in |
|---|---|---|---|
| DECISIONS D-165 | **Section 1 said "No findings were raised at any severity." under a scope table reading 0 / 1 / 0 / 0.** `_draft_inputs` hands `findings=[]` to every section but 6, and `SECTION_FOR_CLASS` maps `C1` to `outcomes`, so section 1's candidates block was `NO_CANDIDATES` — "describe nothing as a finding" — while `_SUMMARY_BRIEF` asked it for "how many findings were raised at which severity". This is **D-156's second half**: that fix single-sourced section 6 and left section 1 asking for a count it is never given. It never showed on `credit_default` because all six of those runs raised zero findings — the same blind spot that hid the first half — and it would have hit section 1 of **every Phase 12 seeded variant**. Study scoring reads `findings.json` and is unaffected; every such report's opening sentence would have been wrong | defect | follow-up commit |
| DECISIONS D-166 | `decile 1` tokenised as a claim. A `label_number` exclusion, on the pattern of `section_number`: an integer that **labels** a bin rather than measuring one. The renderer's own caption "decile 1 holds the highest probabilities" is inside a renderer block and was already excluded, which is why the credit runs never met this | defect | same |
| DECISIONS D-167 | "falls by 1078000" against a negative artifact. The verb carries the sign and the matcher compared signed values. A direction verb governing `by` now compares **magnitudes** and requires the verb's direction to match the artifact's sign. A classifier has no signed scenario artifact, which is why this is the hazard subject's defect to find | defect | same |

**Two things read and deliberately not changed**, named here so they are not rediscovered as
defects. Section 5's "roughly six times" (1,078,000 / 167,100 = 6.45) is the derived-ratio
word-number class already on the Phase 12 pre-flight list against `DRAFT_INSTRUCTION`. Section 4's
"these two exceedances are raised as calibration findings" describes two candidates that merged
into one finding: it is wording, not a number, and it stays.

**What the archive holds, on D-087's terms.** Twenty row-level CSVs are outside the repository, in
`~/code/data-raw/credit/first-live-msr-rows/attempt1/`: the eight under `run/` and twelve under
`artifacts/`. Eight of the twelve are the byte-identical content-addressed twins of the `run/`
files (`run.data_*`, `run.predictions_*`, 135,061 to 313,539 lines each). The other four are the
`cpr.*` period tables (`cpr.train` 72 lines, `cpr.test` 72, `cpr.out_of_time` 76,
`cpr.vintage_holdout` 87) — monthly actual-against-predicted CPR with a row count, carrying no
identifier and no per-loan value, moved because the sweep's rule is a line count and not a
judgement about each file. The consequence is the one D-087 already states: those twelve logical
names resolve in `artifacts/index.json`, with their hash, kind and summary, and have no payload
file in the repository. Nothing a reader needs is lost — `cpr.test`'s 71 rows are rendered in full
inside section 4's renderer block in `report.md`. `find … -name '*.csv' -size +20k` prints
nothing, and no committed file matches `loan_sequence`. The directory is 3.4 MB.

**The one tape the fixes cost, and the sixth record sitting.** Class A is the only one of the three
that is in a prompt, and `tests/probatio/cases/draft_section.yaml` pins each case's brief and
findings, so re-running `casebuilder.py` moved the `draft_section.summary` case's
`prompt_sha256` from `820145888ff24b37` to `1c56fd2d5e0d30c8` and stranded its 18 recorded
interactions. **Exactly one case** moved, which was engineered rather than lucky: a first cut of
the fix also reworded the lead-in of the shared candidates block, which stranded
`draft_section.findings` instead and which the replay caught, so that line is section-aware and
section 6's prompt is unchanged to the byte. The operator recorded the case on **2026-09-17** —
the sixth record sitting, and the first since Phase 11 — and the new tape carries **20**
interactions (8 drafting, 4 re-asks, 8 judge) at **$3.6610**, with the case's replayed cost going
$0.185098 → $0.357327 and its latency 28,368 ms → 53,305 ms on the longer prompt. Every assertion
still passes 4/4 and no baseline score moves. The recording was made over the old tape, so D-158's
prune applies: the live key set was **measured** with a session-scoped patch over
`CassetteStore.replay` — 127 replay requests, 123 distinct keys over the ten cases — and the 18
dead interactions, exactly the 18 the superseded tape held, were removed. The committed tapes go
**121 → 123 interactions** and **$28.9458 → $29.3297**, 4.9 MB either way, and the other nine
tapes prune nothing.

**What this entry does not show.** One run, one panel, one model and one seed: the three classes
are three that one live report surfaced, not an enumeration, and the two that section 4 and
section 5 carried are both classes the six credit runs structurally could not have met. Nothing
here measures whether the fixes are right — that is the re-run, which is the excerpt candidate and
which had not been made when this was written. The `msr_prepayment` **excerpt run remains
outstanding**.

### 2026-09-17 — `msr_prepayment`, `full_agent`, Claude CLI — second attempt, and the MSR excerpt run

The record is `eval/results/first-live/msr/`. It carries **no `attempt` suffix** because it is the
run the README excerpts, on the same terms `eval/results/first-live/credit/` is: committed
byte-for-byte as produced, `report.md` never edited, and the excerpt's wording edits living in
DECISIONS D-168 rather than in the file. It is the re-run the previous entry said was outstanding,
made on `a87aa4a` with D-165, D-166 and D-167 in the build.

**The run.** `quaestor validate subjects/msr_prepayment --data … --llm claude-cli --model
"claude-opus-5[1m]" --config full_agent`, started 2026-09-17 04:44:53 UTC, **exit 0**, and it
rendered. Committed: `trace.jsonl` (414 events), the 21 cassettes, `artifacts/` (364 logical names)
and `run/*.json`. Not committed: the row-level files, which are the real sample (D-087, and the
sweep below).

| quantity | value |
|---|---|
| model calls | **21** — 4 plan, 8 draft, 1 re-ask, 8 extract |
| model | `claude-opus-5[1m]`, through `ClaudeCLILLM` — on all 21 |
| tool calls | **19** — the 15 of the rule-based plan (`run_model`, `profile_data`, `compute_metrics`, `check_leakage`, `check_stability`, `check_collinearity`, `challenger_compare`, `run_scenarios` and `retrieve_guidance` seven times), plus the loop's four `compute_metrics` calls — **30.53 s** in total, 9.92 s of it the subject's own fit, over 364 artifacts. None raised; the only candidate class raised at all is `C1`, once per `compute_metrics` call |
| plan steps (bounded loop) | **4**, all accepted and all executed: `incentive` above and below median, then `loan_age` above and below median, **each over `out_of_time` and `vintage_holdout` at once** |
| claim checks | **368** trace events over the two rounds — 298 pre-repair and section 3's 70 again after |
| claims, pre-repair | **298** at **0.9966** — 297 verified, 0 mismatch, 1 unsupported, 0 dangling, 0 unattributed |
| claims, post-repair | **297** at **1.0000**, after **one** repair round that rewrote no claim and **removed one number** |
| findings | **1** — `F-001`, `C1 calibration` at severity **medium**, **ten candidates merged**, nine evidence artifacts; **two** open items |
| developer claims | **3 of 3 verified** — `auc test 0.655`, `brier test 0.00906`, `calibration_slope test 1.017` |
| output tokens | **122,054** — 1,757 plan, 46,664 draft, 6,216 re-ask, 67,417 extract |
| input tokens | **333,584**, re-derived from the 21 tapes under D-093's three-field sum |
| notional cost | **$6.4858** — $0.4180 the four plan steps, $3.0149 drafting, $0.6244 the one re-ask, $2.4284 extraction |
| wall-clock | **22:54** from the first traced event to the last (1,373.77 s); the operator's shell clock read 23:12.75 |
| report written | **yes** |

**Against the two runs it should be read against.** Attempt 1 cost **$7.1697** over 1,549.94 s
(operator's clock 26:09) for 23 model calls and 305 claims; this one cost **$6.4858** over
1,373.77 s (operator's clock 23:12.75) for 21 calls and 298. The credit excerpt run cost
**$3.9739** over 872.74 s (14:33) for 18 calls and 210. The MSR-to-credit gap is not drift and is
the same gap the previous entry described: this run has a finding to draft, one re-ask the credit
run did not need, and four loop steps whose artifacts section 4 then reports. The attempt-1-to-
attempt-2 movement is two fewer model calls — one fewer section re-drafted, so one fewer draft and
one fewer extraction — and it is the **first** attempt-to-attempt comparison on this subject, which
means n = 1 on each side and nothing here establishes a trend. Per claim: **$0.0218** here,
$0.0235 on attempt 1, $0.0189 on credit.

**Per-section grounding, pre-repair, as `claims.json` records it.** summary **12/12**, conceptual
soundness **48/48**, data integrity **70/71**, outcomes **109/109**, sensitivity **30/30**,
findings **21/21**, monitoring **7/7**. The sections in which **every claim verified before any
repair** are therefore **1, 2, 4, 5, 6 and 7** — six of the seven, against attempt 1's five. The
one that did not is section 3, on claim `7a2768dcbeb4fed3`.

**The one failure, and it is our tokeniser again.** Section 3 wrote "verified each one against its
recorded **SHA-256** digest before any split was read", and the `256` was tokenised as a claim of
value 256.0 with no artifact behind it — unsupported, because no artifact holds it and none could:
it is the name of a hash function. The scoped repair round removed the number and the drafter wrote
"its recorded **cryptographic** digest", which is honest and slightly worse prose. This is the third
run of this class after D-116's `D-050` and D-166's `decile 1`, and the pattern is now clear enough
to name: an identifier whose digits a reader does not read as a measurement. **D-169** adds the
`algorithm_name` exclusion. The renderer's own caption two lines below writes `SHA-256` as well and
was never a claim, because it is inside a renderer block — the same near-miss that hid `decile 1`
until a drafter wrote it in its own prose.

**Why this is the excerpt run, and attempt 1 was not.** Section 1 publishes the finding — "This
validation published F-001, a C1 calibration finding at medium severity, which section 6 sets out
in full." — under a scope table reading 0 / 1 / 0 / 0, which is **D-165 holding live for the first
time**; attempt 1's section 1 said "No findings were raised at any severity." under the same table
and that is why it was archived. Sections **2 and 4 both verified whole pre-repair**, 48 of 48 and
109 of 109, and Cowork's read of both found no wrong number. The single pre-repair failure is in
section 3, outside the excerpt. D-156 held in section 6 again, D-162's manifest table is cited in
section 3 with its Appendix C row present (`verified: 5 file(s) against package.yaml`), and
D-164's z gate is cited in section 5. **D-167 was not exercised**: section 5 wrote "the change in
servicing value is -1078000" rather than attempt 1's "falls by 1078000", so the verb rule's live
evidence is still nil.

**The substantive result, which is this run's addition over attempt 1.** Attempt 1 spent all four
loop steps on the incentive 2×2. This run spent two on incentive and two on `loan_age`, which is
the partition that answers the question `F-001` raises — is the ~50% under-prediction a flat level
shift or a failure of the seasoning shape? The answer is **neither reading survives on its own**.
Out of time, the seasoned half predicts **0.0032** against an observed **0.0123**, and the newer
half predicts **0.0168** against **0.0250**. The **absolute** gaps are nearly equal (0.0091 and
0.0082), which reads as a level shift; the **relative** shortfalls are **3.8×** and **1.5×**, which
does not. Neither loan-age half is past `threshold.O1.slice_auc_gap` on either forward split —
0.03303 and 0.02328 out of time, 0.02861 and 0.02765 on the vintage holdout, all well inside 0.08 —
so the seasoning partition **raised no open item**: discrimination inside each half is intact and
only the level is wrong. The two open items are both the incentive partition's, and there are two
rather than attempt 1's three because `vintage_holdout` high-incentive came in at a gap of 0.07345,
inside the bound: `incentive > median` out of time (AUC **0.6046**, gap 0.08523) and
`incentive <= median` on both forward splits (**0.5198**, gap 0.17, and **0.5956**, gap 0.1432).
The out-of-time out-of-the-money segment ranking barely better than chance on half the split is
still the result a reader should carry away, and it replicates.

**Read and deliberately not changed.** Four wording sentences in sections 2 and 4 are edited **in
the excerpt and not in the record**, and D-168 carries all four verbatim with the reason for each:
"raised as C1 calibration findings" for ten candidates that merged into one finding; "the lower
bound of 0.8" for a `C1` rule threshold sitting two lines from the developer's band of the same
value; "the **declared** gap allowance of 0.08" for a bound `package.yaml` does not declare, which
is the second live run to write it; and a closing clause reading the loan-age partition as "a level
shift rather than a seasoning-shape failure", which the relative gaps above contradict. Beyond
those: section 6's `F-001` narrative says the shortfall "widens as predicted risk rises", true of
the absolute gap on `calibration.out_of_time` (bin 1 gap 0.009, bin 10 gap 0.015) and false of the
relative one (bin 1 observed/predicted ≈ **37×**, bin 10 ≈ **1.45×**) — the same
absolute-versus-relative reading, in a section the excerpt does not take. "Roughly half" (sections
4 and 6) and "three developer-declared thresholds" (section 1) are the word-number class already on
the Phase 12 pre-flight list, where attempt 1's "roughly six times" went.

| # | what the live run exposed | kind | fixed in |
|---|---|---|---|
| DECISIONS D-169 | **`SHA-256` tokenised as a claim of 256.** An `algorithm_name` exclusion beside `regulatory_section_id`: a hyphenated `[A-Z]{2,}-\d{1,4}` identifier whose letters are not a regulator code already covered. `SHA-256`, `SHA-3`, `MD-5`, `ISO-8601` and `RFC-8259` mask; `SR 11-7` keeps its existing class; a shock label keeps its number | defect | follow-up commit |

**Two pre-flight items this run points at, recorded and not done.** Both are artifact-shape
questions and both are about the same missing quantity. First, a `C1` candidate's evidence should
carry the **breached split's `calibration.<split>` decile table**: F-001's nine artifacts are two
thresholds, one slope, two `mean_predicted`/`event_rate` pairs and the two relative gaps derived
from them, and the table that would settle whether the shortfall widens with score is in the store
and not among them. Second, sub-population artifacts should carry a **`mean_rel_gap`** beside
`mean_predicted` and `event_rate`: the name exists at split level and at no `sub.<slug>` level, so
a drafter comparing two slices has only the absolute difference to write about — which is edit 4
and section 6's paragraph both, from one cause.

**What the archive holds, on D-087's terms.** Twenty row-level CSVs are outside the repository, in
`~/code/data-raw/credit/first-live-msr-rows/excerpt/`: the eight under `run/` and twelve under
`artifacts/`, the same shape attempt 1 swept. Eight of the twelve are the byte-identical
content-addressed twins of the `run/` files (`run.data_*`, `run.predictions_*`, 135,061 to 313,539
lines each). The other four are the `cpr.*` period tables (`cpr.train` 72 lines, `cpr.test` 72,
`cpr.out_of_time` 76, `cpr.vintage_holdout` 87) — monthly actual-against-predicted CPR with a row
count, carrying no identifier and no per-loan value, moved because the sweep's rule is a line count
and not a judgement about each file. Those twelve logical names resolve in `artifacts/index.json`,
with their hash, kind and summary, and have no payload file in the repository; `cpr.test`'s rows
are rendered in full inside section 4's renderer block in `report.md` regardless.
`find … -name '*.csv' -size +20k` prints nothing, `git grep --cached -i loan_sequence` over the
directory finds nothing, and the directory is **219 MB → 3.4 MB**.

**What this entry does not show.** One run, one panel, one model and one seed, and the comparison
against attempt 1 is n = 1 against n = 1 over a changed build — the two-call and $0.68 difference is
not a measured improvement. The excerpt's four edits are Cowork's reading of two sections, not an
enumeration of everything a reader outside this project would misread. D-167 still has no live
evidence. And the `algorithm_name` class is a fourth instance of one pattern rather than proof the
pattern is now closed: the next live run is the test of whether an exclusion list assembled one
defect at a time has stopped finding new ones.
