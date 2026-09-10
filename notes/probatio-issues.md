# Issues to file against Probatio 0.1.0

Found while building Quaestor's Phase 11 test layer against `probatio-llm 0.1.0` as shipped. Each
is reproduced from this repository's committed tapes and case files. None is worked around inside
`probatio/`: Quaestor treats it as a dev dependency and the remedies below live in this repository
until they are fixed upstream.

Filed by: Yichen Li, 2026-09-10. Upstream: <https://github.com/Lexieli666/probatio>.

---

## 1. The judge parser rejects a repairable reply, and a rubric has to do its job

**Where:** `probatio/judge/core.py`, `Judge.grade`; `probatio/assertions/judge.py`.

**What happens:** `grade` strips at most one code fence, calls `json.loads`, and raises
`JudgeOutputError` on anything else. A reply that carries a complete, correct verdict but is
malformed in one of three mechanical ways is discarded whole:

- the `rationale` string is not closed before the object's `}` — `…unavailable.}` for
  `…unavailable."}`. **6 occurrences** on Quaestor's first recording.
- the model appends prose and a corrected second object after the first — the first object is
  complete and parseable on its own.
- an unescaped `"` inside `rationale`, from a rubric that asked the judge to quote what it judged.

**Why it matters:** the discarded verdicts were **passes**. On Quaestor's first recording 16 of 20
judge replies (80%) were unparseable, every one of them carrying `"verdict": "pass"` or a
considered `"fail"`; on the second, 8 of 32 (25%). Because a discarded verdict fails its
assertion, and because a metamorphic variant's verdict is compared with the original's, **every
relation violation Quaestor measured on those two recordings was a JSON formatting failure in the
grader rather than a change in the application's behaviour**. A user reading the relation table
would conclude the system under test was unstable when it was not.

**Suggested fix:** parse the first balanced JSON object in the reply rather than requiring the
whole reply to be one; optionally repair a single unterminated trailing string. Keep the strictness
about `verdict` and `score` — that part is right and DECISIONS 29 argues it well. A `repaired:
true` flag on `JudgeVerdict`, surfaced in the assertion detail, would keep the leniency visible.

**Quaestor's stopgap:** `tests/probatio/rubrics/grounding.md` instructs the judge in prohibitions —
no quotation marks, no line breaks, no braces, at most fifteen words, nothing after the closing
brace, check the string closes. It took **two paid recordings and two rubric revisions** to reach
0 of 60 unparseable. That is a rubric spending its instruction budget on a parser, not on the thing
it grades. See Quaestor DECISIONS D-148 and D-153.

---

## 2. `--max-cost` is not a ceiling: it cannot stop a run, and it cannot see judge spend

**Where:** `probatio/collector.py`, `RunState.observe`; `probatio/session.py`, `Probatio.check`;
`probatio/plugin.py`, `pytest_sessionfinish`.

**What happens, two parts:**

1. **Judge spend is invisible.** `observe` records a completion only while a sink is open, and
   `check` opens one around the system under test (`_call_sut`) and around each relation variant
   (`_call_variant`). A `judge` assertion is evaluated inside `evaluate_case`, outside both, so its
   completions reach no sink, no case cost and no session total. Measured on Quaestor's tapes:
   **$16.73 of drafting calls and $12.19 of judge calls across seven cases — 58% visible.** This
   contradicts `session.py`'s own module docstring, which states that judge calls "are real money
   and they do count toward the session total under `--max-cost`".
2. **The ceiling is post-hoc.** It is read in `pytest_sessionfinish`, so it can only set a non-zero
   exit status after the session has finished spending. A recording given `--max-cost 7` spent
   $7.59 visible / $12.34 actual and ran to completion.

**Why it matters:** `--max-cost` reads as a circuit breaker for an operator about to spend real
money on a record run, and it is a post-hoc verdict on 58% of the bill. The honest reading is "fail
the sitting if it turns out to have spent more than about `N / 0.6`".

**Suggested fix:** open the sink around `evaluate_case` as well, or give the judge its own recorded
category so the total is complete and the split stays visible; and check the running total after
each case so a ceiling can stop a session rather than grade it.

**Quaestor's stopgap:** none possible — a shim in Quaestor's suite would be a second copy of
Probatio's accounting. The consequence is documented where it is acted on and `-k` is used to bound
a sitting instead. See Quaestor DECISIONS D-149.

---

## 3. Replay silently cannot match a tape unless the session names the recorded model

**Where:** `probatio/cassette.py`, `interaction_key` and `resolve_model`; `probatio/cli.py`,
`build_provider`.

**What happens:** an interaction key includes the resolved model, whose fallback is the answering
adapter's own. A replay session that names no `--probatio-model` builds `FakeProvider(model or
"fake-1")`, so every key is computed against the literal string `fake-1`, no tape carries it, and
every case fails with `StaleCassetteError: the prompt, the model or the params changed since it was
recorded`.

**Why it matters:** putting the model in the key is right. The **default** is not: a fake provider's
model name is a plausible string that no real tape can match, so the failure lands on every case at
once and its message invites the wrong diagnosis — that the prompts drifted. Quaestor lost time to
exactly that.

**Suggested fix:** when `--cassette=replay` and no `--probatio-model` is given, take the model from
the tape being replayed, or fail at configure time with "these tapes were recorded against
`<model>`; pass `--probatio-model`" rather than reporting drift per case.

**Quaestor's stopgap:** `--probatio-model` in `pyproject.toml`'s `addopts`. See DECISIONS D-151.

---

## 4. No per-case provider timeout

**Where:** `probatio/providers/claude_cli.py`, `DEFAULT_TIMEOUT_S = 120.0`; `probatio/plugin.py`,
`--probatio-timeout`.

**What happens:** the Claude CLI adapter's timeout is session-wide. A `timeout` in a case's
`params` is not honoured — the adapter files it under `probatio_ignored_params` — and, because
`params` is hashed into the interaction key, setting one would silently strand that case's own
tape.

**Why it matters:** a suite whose cases have genuinely different shapes — a two-line planning
action beside a seven-thousand-token report section — has one hang ceiling for both. Quaestor lost
three cases mid-recording to the 120 s default, which the constant's own docstring calls "a
hung-process ceiling, not a budget" and which was acting as a budget.

**Suggested fix:** honour a per-case timeout without putting it in the cassette key — a
`Budget.max_latency_ms`-derived timeout would do it, since the case already declares one.

**Quaestor's stopgap:** `--probatio-timeout 600` in `addopts`, with per-case `max_latency_ms` as
the budget beneath it. See DECISIONS D-150.

---

## 5. An offline fake run silently writes a baseline

**Where:** `probatio/snapshot.py`, `BaselineStore.compare`.

**What happens:** `compare` is called with `update=False` on every run and records a baseline when
the case has none. A verification run against `--probatio-provider fake --cassette=off`, whose
answers fail every content assertion by design, therefore stamps those failures as the reference
for any case lacking one. A later real recording reports `scores_changed` against it.

**Why it matters:** silent in both directions — nothing about the fake run says it wrote a
reference, and nothing about `scores_changed` says the reference came from a fake. It reads as
drift in the recording, which is the one thing it is not.

**Suggested fix:** do not record a baseline from a session whose provider is `fake`, or stamp the
provider on the baseline and report `baseline recorded by provider 'fake'` on comparison.

**Quaestor's stopgap:** every fake invocation passes `--baseline-dir $(mktemp -d)`. See DECISIONS
D-154. Arguably documented behaviour rather than a defect; filed for the diagnosability of the
message.
