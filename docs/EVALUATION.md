# Evaluation: what Quaestor has been measured on, and what it got wrong

Every number in this file comes from a run committed in this repository, and the run is named
where the number is used. `tests/test_live_credit_attempt1.py` and
`tests/test_live_credit_attempt2.py` re-derive each figure of section 1 from the trace it claims
to come from, so a number that drifts from its run fails the suite rather than sitting in a
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

**Still outstanding.** The `msr_prepayment` live run of `03-RUNBOOK.md` §3, and a `credit_default`
attempt that reaches a report. Both are the operator's, and neither has happened.
