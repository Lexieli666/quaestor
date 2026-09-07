# DESIGN.md — why Quaestor is built the way it is

One section per phase. Every non-obvious choice gets a paragraph that names the alternative it
rejected, so that a later session can tell a decision from an accident.

## Phase 0 — Scaffolding

**The scaffold is a whole gate, not a skeleton.** Phase 0 ships eleven Python modules of which ten
are empty, and eighteen tests that assert almost nothing about behaviour. The point is that the six
conditions of `CLAUDE.md`'s quality gate are all *runnable* from the first commit: four of them
really run, and the two that cannot yet (the golden report, the Probatio replay) exist in `ci.yml`
as guarded steps that say out loud why they are inert. The rejected alternative was the usual one —
add each gate condition to CI in the phase that first satisfies it. That produces a CI file which
silently under-checks, and a reader cannot tell whether a missing step means "not yet" or
"forgotten". Guarding on the artefact's existence (`examples/golden_report/report.md`,
`tests/probatio/`) makes the transition automatic: the step starts checking the moment the phase
that owns it lands, without anyone editing YAML.

**Empty `src/` subpackages carry a docstring, not a `.gitkeep`.** Each of the nine directories
under `src/quaestor/` is a real package whose `__init__.py` docstring names the phase and the spec
section that fills it, and `tests/test_scaffold.py` imports all nine and asserts each is
documented. The rejected alternative, a `.gitkeep` per directory, keeps git happy and nothing else:
it is invisible to a reader of the package, invisible to `mypy`, and deleting one is undetectable.
A docstring is read by the two audiences that matter — the next session, and anyone who runs
`help(quaestor.verifier)` — and the import test turns a deleted `__init__.py` from a mystery into a
failure. Directories outside `src/` (`subjects/*/code/`, `eval/results/published/`,
`examples/golden_report/`) cannot be packages, so they do get an annotated `.gitkeep`, which says
why it exists and to delete it when the owning phase arrives.

**`tests/probatio/` is deliberately the one layout directory that does not exist.** Gate condition
6 is `pytest tests/probatio --cassette=replay`, and `pytest` has no "run these tests if there are
any" mode: a missing path is a usage error and an empty directory is "no tests collected". Both are
red. Creating the directory with a placeholder would therefore make CI fail for a phase that has
not happened, so the directory is left out and the CI step is guarded on it. The rejected
alternative was `continue-on-error: true`, which would keep the step permanently unable to fail —
including after Phase 11, when a stale cassette or an accidental live provider call is exactly what
it must catch.

**The CLI stub has no argument parser.** `quaestor.cli.main` prints the version, ignores its
`argv`, and returns zero. The `argv` parameter is in the signature from the start so that Phase 9
can add a parser without changing a single caller or test, but there is no half-built flag surface.
The rejected alternative — scaffolding `argparse` subcommands for `validate`, `study`, `tool` and
the rest, with each raising `NotImplementedError` — reads as a working CLI to anyone who runs
`quaestor --help`, and invites a phase to fill in a subcommand without the spec section that
defines it. A stub that plainly does one thing cannot be mistaken for a product.

**Tests assert the wiring that fails silently.** The three failure modes a scaffold really has are
a version that drifts between `__init__.py` and the built metadata, a console-script entry point
naming a function that does not exist, and an import name that does not match the distribution
name. So the tests read the *installed* metadata (`importlib.metadata.version("quaestor-mrm")`,
the `console_scripts` entry point's value) rather than only the source constant, and they run the
console script found on `PATH` as a subprocess. The rejected alternative, asserting
`quaestor.__version__` and calling `main()` in-process, passes cheerfully on a broken
`pyproject.toml`. One further test pins the list of modules under `src/quaestor/`, so that the run
log's claim that Phase 0 shipped no implementation code stays checkable rather than remembered.

## Phase 1 — The golden report as an executable specification

**The renderer writes the tables, not the drafter (D-013).** The golden report contains two
ten-row artifact tables, a calibration table and a decile table. If the drafter wrote them, each of
their eighty cells would be a number requiring its own `[[art:…]]` citation, and 80 of the report's
172 candidate numbers would be table transcription; the headline grounding precision would then be
mostly a measurement of whether an LLM can copy a table correctly, which is a question nobody is
asking and which a deterministic renderer answers perfectly for free. So the drafter writes
`[[table:<logical_name>]]` on a line of its own, the renderer expands the directive inside a
`<!-- quaestor:renderer:begin table … -->` block, and everything inside such a block is excluded
from extraction and from the grounding denominator — no model produced it, so there is nothing to
verify. The scope block under section 1 works the same way, and is how the two grounding figures
reach the report's first page although neither exists until after extraction has run. The rejected
alternative was to let the drafter write the tables and to count every cell as a claim. It has the
attraction of a single uniform rule, and it was rejected for two reasons: it dilutes the metric the
whole project is built to report, and it manufactures a failure mode — a real drafter *will*
mistype a cell — that no amount of repair-loop iteration can fix, because the model cannot see the
table any more precisely than the JSON it was handed. Tables the drafter genuinely reasons over
(metrics by split, the threshold pass/fail table) stay prose in table layout: every cell carries
its own citation and is an ordinary claim.

**Developer claims are evaluated only under `--data` (D-016).** `package.yaml` `claims:` are the
developer's declared numbers about the *real* fit — "AUC on test is 0.76". Under `--synthetic`, the
data comes from a generating process with nothing in common with the real sample, so verifying those
claims against synthetic artifacts would produce either a false `T1` finding or a meaningless pass,
and `T1` detection is one of the classes the seeded-defect study scores. They are therefore listed
in Appendix D as not evaluated, with `status: not_evaluated` in `claims.json`; under `--data` each
becomes an ordinary `VerifiedClaim` with `source: developer`, and a `mismatch` is the claim channel
of a `T1`. The rejected alternative was a per-mode `claims:` block in `package.yaml`, or a separate
schema for synthetic runs. Both duplicate the developer's own declaration, and a duplicated
declaration drifts: the synthetic copy would be quietly maintained to keep the suite green, which is
precisely the incentive this project exists to remove. One extra status value costs a line of code
and keeps one source of truth.

**The clean synthetic subject is not defect-free by construction (D-017).** The synthetic
`credit_default` generator carries one interaction term (`utilisation × delinq_last`) and one
near-collinear pair (`bill_last`, `bill_mean_6m`). The interaction is invisible to the additive
logistic champion, so a boosted challenger beats it by more than the 0.03 effective-challenge
threshold, and the clean subject therefore yields exactly one finding: `E1` at severity `low`. That
is binding on Phase 3 and Phase 8 — the end-to-end test asserts the finding set `{E1 low}`, not an
empty one. The collinear pair does the same job one layer down: the subject's own VIF screen removes
one of the two before fitting, so the report has a real feature-removal to describe without an `M1`
candidate being raised. The rejected alternative was a purely additive generating process, giving a
control subject with no findings at all, plus a seeded variant later to exercise the finding path.
It was rejected because "no findings" is the weakest end-to-end assertion available: it passes when
every tool silently fails to run, when the `Finding` constructor is broken, and when section 6 of
the report renders empty — and it defers the entire finding path, severity handling and evidence
rule to Phase 10. A clean subject with one *legitimate* finding exercises all of it, and an `E1`
raised because a challenger is better is a true statement about the champion's functional form
rather than an accusation of a defect, which is exactly what the class is for.

**The golden directory is pinned by two hashes, not by `git` (D-011).** Gate condition 5 asks for
`examples/golden_report/` to be byte-identical to its introducing commit except for sanctioned
edits. Implemented literally that is `git diff` against a commit nobody wrote down, on full history,
which is why such conditions go unrun. Instead `MANIFEST.json` holds the `sha256` of each of the six
specification files and `DECISIONS.md` D-011 pins the `sha256` of `MANIFEST.json`, so
`tests/test_golden_spec.py` closes the loop inside `pytest -q`: a changed file breaks the manifest, a
changed manifest breaks the pin, and the only way through is a decision entry — written *before* the
bytes change, which is what makes the record a decision rather than a description. The rejected
alternative, a CI step diffing against a recorded SHA, needs unshallow history, cannot express
"sanctioned", and is invisible on a laptop.

## Phase 2 — Foundations, the package loader, the artifact store, the LLM layer

**`structured()` validates in Quaestor, not in the provider (D-025).** The Claude Code CLI has a
`--json-schema` flag that would enforce a section's shape server-side, and using it would remove a
class of failure from the drafter entirely. It is not used. `AnthropicLLM` cannot offer the same
guarantee through the Messages API without tool-use scaffolding, so a pipeline that leaned on the
flag would have two providers with two different failure modes: under `claude-cli` a malformed
answer would never reach `structured()`, and under `anthropic` it would, and the re-ask count —
which the study publishes as a quality signal per configuration — would mean different things in
the two halves of the same table. Validation therefore lives in provider-agnostic code, every
provider fails identically, and the re-ask is comparable. The cost is one extra round trip on the
answers the flag would have caught; the benefit is that the number the study reports is a property
of the prompt rather than of the transport.

**One re-ask, and the second failure is fatal.** `structured()` asks once, quotes the validation
error back and asks once more, then raises `LLMOutputError` carrying the raw text. The rejected
alternative is the usual retry loop with a backoff and a cap of three or five. A loop hides a prompt
that does not work: the cost line grows, the report still renders, and nobody looks. With exactly
one retry, a section that needs a re-ask is rare enough that `eval/score.py` counting them per
configuration is a measurement rather than a rounding error, and a prompt that fails twice is a
prompt to fix rather than to pay for.

**The artifact address includes the logical name (D-023).** "Content-addressed" would ordinarily
mean the hash is a function of the payload alone. Here it is a function of `(kind, name, payload)`,
because on a stratified split the train and test event rates are *the same number*, and pure value
addressing would make `metrics.train.event_rate` and `metrics.test.event_rate` one artifact with one
hash. A finding whose evidence is that hash could no longer say which split it rested on; Appendix B
would print one row under two names; and the citation rule "`hash8` prefixes a stored artifact and
`logical_name` is in its index entry" would have to admit a set of names rather than one. The
rejected alternative saves a few kilobytes of duplicated scalar files and costs the evidence rule
its precision, which is the one thing this project is for.

**A logical name cannot be re-pointed.** Storing a different payload under a name the store already
holds raises rather than replacing. The rejected alternative — last write wins, which is what a
cache does — breaks the only invariant citations have: prose already drafted against the old hash
would silently become dangling, and a dangling citation that *used to* resolve is indistinguishable,
to the verifier and to a reader, from a drafter that invented a hash. A tool that legitimately
recomputes something under new conditions gives it a new name (`metrics.test.sub.limit_bal_low.auc`,
not a second `metrics.test.auc`), which is also what makes Appendix B readable.

**Citation paths walk, they never compute.** `#coefficients.utilisation.value` addresses a key, then
a list element by its `feature` field, then a key. There is no aggregate, no index arithmetic and no
count. The consequence is visible in the golden report: `run.features#n` resolves only because
`run.features` is stored as an object carrying its own counts, not as the bare list spec §3.3
describes on disk. That is deliberate. The rejected alternative — letting a citation say "the length
of this list" — would make the number in the prose the output of a small expression language that
lives nowhere except inside a citation string, and every such expression is a place where a report's
number stops being a stored artifact that somebody can recompute. The project's rule is that a
number in a report is a number in the store; a count the report wants to state is a count some tool
decided to store.

**The trace is typed as an envelope plus a payload (D-020).** On disk a trace line is flat, exactly
as spec §3.1 writes it. In memory the type-specific fields sit in `TraceEvent.payload`, because the
alternative, pydantic's `extra="allow"`, puts them where `mypy --strict` cannot see them and makes
every read in `eval/score.py` either an error or an untyped `getattr`. Six models, one per event
type, was the other alternative and is where a trace format grows two spellings of `duration`; the
field names the study actually counts are pinned instead by one typed method, `TraceWriter.llm_call`.

**The CLI adapter runs on the login the project actually has, and names what that costs (D-025).**
The default argument vector does not pass `--bare`. It would have been the tidier choice — `--bare`
suppresses hooks, plugins, auto-memory, keychain reads and `CLAUDE.md` discovery in one flag — and
it was the first draft's default, but `claude --help` is explicit that under `--bare` authentication
is "strictly `ANTHROPIC_API_KEY` or `apiKeyHelper`" and OAuth and the keychain are never read.
`CLAUDE.md` forbids an API key anywhere in this project, and every live run the runbook describes is
made on a subscription login, so `--bare` by default is a default that cannot run. Context is
excluded by the two mechanisms that do not touch authentication instead: each call runs in a fresh
empty temporary working directory, which removes project context and project `CLAUDE.md`
auto-discovery, and `--strict-mcp-config` is passed with no `--mcp-config`, which removes every MCP
server the operator has configured. `--bare` remains available as `bare_flag="--bare"` for an
operator who does have a key.

*The limitation this leaves, stated plainly:* without `--bare`, a live run still sees the operator's
user-level configuration — hooks, plugins, `~/.claude/CLAUDE.md`, output styles. None of it is
visible in the payload the adapter parses, so two operators can in principle get different answers
to the same prompt from the same commit. Three things bound the damage: the study's comparisons are
between configurations within one operator's run, not across machines; the answer, its tokens and
its notional cost are all recorded in the trace, so a surprising result is inspectable; and whether
`--bare` was passed is itself recorded on every `llm_call` event as `quaestor_bare`, so a run under
one regime is never silently compared with a run under the other. The rejected alternative was to
keep `--bare` and instruct operators to export an API key, which contradicts `CLAUDE.md` and would
make the published study unreproducible by anyone who obeys it.

**Two error classes for the LLM layer, not one (D-024).** `LLMOutputError` means the model answered
and the answer is unusable; `LLMProviderError` means there was no answer. The study retries the
second and records the first, and `eval/run_study.py` is resumable, so collapsing them would mean
either re-asking a prompt the model reliably fails at — inflating the very re-ask count the study
publishes — or abandoning a variant because a laptop's network blinked. Rejected alternative: one
class with a flag, which is a type distinction written as data and branched on in three places.

**The loader takes the data directory as an argument (D-022).** `data.manifest` is a statement about
specific files, and under `--synthetic` those files are not read at all. Verifying them against the
package directory — the only path `load_package(path)` would otherwise know — would pass vacuously
on every real package, since nobody keeps their data inside the package. Passing the directory
explicitly means the check is honest in both modes, `--synthetic` needs no special case, and
Appendix D's "data manifest: not checked in synthetic mode" line is a fact about the code rather
than a caveat about it.

## Phase 3 — The sandbox and the `credit_default` subject

**The subject is a subprocess, and the working tree is a copy of `code/` and nothing else
(D-029).** `run_model` copies the package's `code/` into a fresh temporary directory, runs the
declared entrypoint with the working directory one level above the copy, and deletes the tree
afterwards. The rejected alternative is copying the whole package directory, which is simpler and
gives the subject its own `package.yaml`, its `docs/` and any committed artifacts. That is exactly
what should not be available: the drafter quotes `docs/` with a file citation and the validator
reads `package.yaml`, so a subject that could read either could be written to agree with them. The
other rejected alternative — leaving the subject where it is and setting `PYTHONPATH` — makes the
subject's imports depend on a variable the environment scrub is meant to be able to drop.

**A cap that is not enforced is recorded rather than pretended (D-028).** On Linux the address
space is capped with `RLIMIT_AS` in a `preexec_fn`; on macOS the same call is not reliably
honoured, so it is not made and the run records `memory_cap: unenforced` on its result, its
`run.status` artifact, its trace event and the report's Appendix C. The rejected alternative is to
set the limit everywhere and let a kill become an `R0` finding: numpy's BLAS reserves far more
address space than it commits, so on a host that did enforce the limit a healthy 5,000-row fit
would be killed, and the study would score a platform difference as a defect. `sandbox/Dockerfile`
documents the path where all four limits are real — `--memory` is a kernel limit, `--network none`
is what `QUAESTOR_NO_NETWORK` can only ask for — and no test builds it.

**A failed run raises, but stores its evidence first (D-033).** `run_model` puts `run.stdout`,
`run.stderr`, `run.duration_s` and `run.status` in the store before it raises `SandboxError`, so
the Phase 5 tool can promote an `R0` candidate that satisfies `CLAUDE.md`'s evidence rule for the
one defect class that describes a run which produced nothing. The rejected alternative is
returning a `RunResult` with an `ok` flag, which every caller has to remember to check and the one
that forgets goes on to read contract files that were never written.

**The contract check is shallow on purpose.** `read_contract` asks whether each spec §3.3 file is
present, parses, and carries the keys and columns the contract fixes; it never asks whether a
number in it is right. The developer's `metrics.json` is never trusted — Phase 5 recomputes every
metric from `predictions_<split>.csv` — so a validator here would be checking the wrong claim in
the wrong place, and would have to be relaxed the first time a seeded variant reported a metric
Quaestor disagreed with, which is the case the study exists to measure.

**One definition of the twelve features, over a canonical raw schema.** `code/features.py` owns
`engineer`, the stratified split and the VIF screen; `code/synthetic.py` renders the raw statement
schema from the generating process and `sample.py` renames the UCI columns into the same schema.
The rejected alternative is engineering the features twice, once per data source, which is the
arrangement in which a real fit and a synthetic fit come to mean subtly different things by
`pay_ratio_last` and no test can see it. The cost is that `sample.py` imports out of `code/` by
path, under an alias, because the package is literally named `code` and importing it as such would
shadow the standard library module for the whole process.

**The screen removes the last-declared collinear feature, not the worst (D-031).** On the clean
panel `utilisation` has a VIF of 49.2 and `utilisation_mean_6m` 50.1 — a distinction on the second
decimal deciding which feature the champion is fitted on. Declaration order is the developer's own
and is stable across seeds and across the study's variants, so the report always discusses the
feature the package lists first. The textbook rule, removing the maximum, is reproducible for one
dataset and not across two hundred.

**The interaction is a reversal, and it was chosen by measurement (D-036).** D-017 requires the
clean synthetic subject to yield exactly one finding, `E1`, which means the challenger has to beat
the champion by more than 0.03 for a reason that is true rather than tuned. A saturating
interaction of the same magnitude left the gap at 0.016 — inside the range a challenger's
`max_leaf_nodes` moves it — so the process instead reverses the sign of the utilisation effect
once a client is past due, with the credit story written down in `code/synthetic.py` and the
subject's `README.md`. The measured gap is +0.076 and holds under every challenger configuration
tried. The rejected alternative was tuning towards the golden report's illustrative 0.0323, which
would optimise a number that was never a measurement.

**The process's intercept is solved, not declared (D-036).** `SyntheticProcess` carries every
parameter of the generating process so that a Phase 10 recipe can perturb one field, and the
intercept is deliberately not one of them: it is bisected for each parameter set so that the mean
default probability is `target_event_rate`. A recipe that changes a coefficient therefore changes
the coefficient, and not also the base rate — which the study's `T1` and `C1` scoring would
otherwise confound with the seeded defect.

## Phase 4 — The `msr_prepayment` subject and its projection

**One lagging rule, with no exceptions, because a rule with an exception cannot be tested
(D-038).** Every raw value the hazard subject reads is a *closing* value of the month it is
labelled with: the balance and age at the close of month *t*, whether the loan paid off during
month *t*, and the market rate at the close of month *t*. Every feature at month *t* is then a
function of month *t − 1*'s closes and of month *t*'s calendar position. The awkward consequence
is that the rate calendar is indexed by the month whose *close* each rate stands at, so the FRED
print published in the first week of February 2020 is stored under `2020-01` — and that is
exactly the month-start rate of February, since no time passes between a month's close and the
next month's start. The rejected alternative labels the calendar by the month whose start the
rate stands at, which reads better in isolation and makes `incentive` the one feature at month
*t* built from a month-*t* raw value; the Phase 4 leakage test could then perturb the balance and
the payoff and would have to leave the rate alone, which is the one of the three most likely to
be lagged wrongly in a real prepayment model.

**The generating process reads its own features through `build_panel`.** `code/synthetic.py`
draws the loans, renders the raw schema they would produce if none of them ever paid off, passes
that schedule panel through the same `build_panel` the champion is fitted on, and evaluates the
hazard on the resulting feature columns. Only then are the uniforms drawn and the loans censored.
So the process and the model cannot disagree about what `incentive`, `burnout` or `loan_age`
means, and a lagging bug has nowhere to hide: it would move both. The arrangement is also what
makes the draw cheap — the whole hazard path of a loan is determined before a single payoff is
drawn, because the scheduled balance is deterministic and every other input is a market or
origination quantity.

**Negative convexity had to be arranged, and the first arrangement had the sign backwards
(D-040).** The Phase 4 prompt asks that the base case sit where the incentive response is convex,
so that the projection's sign pattern is a property of the process. Two of the three ingredients
were obvious: a small logistic hazard is convex (the whole operating range is below a logit of
zero), and a turnover floor bounds the up shock's upside while nothing bounds the down shock's
downside. The third was not. With a mildly falling rate path, every loan still alive at the end
of the panel carried a large positive incentive, the base-case CPR was 24.9%, and the projection
reported **+871,718** at +300bp against **−488,601** at −300bp: positive convexity, and the wrong
answer for a servicing right. Writing the valuation as `V ≈ 1 / (δ + h)` for a monthly discount δ
and a monthly hazard `h`, the most the down shock can take away is `V(0)` while the most the up
shock can add is `h₀ / (δ (δ + h₀))`, so `|down| > |up|` requires `h₀ < δ` — the base hazard below
the monthly discount rate, which is to say a book at or out of the money. That is also the
textbook statement of when a servicing right is negatively convex, so the fix was the economics:
a late level rise in the rate path, the real 2022–23 move, which leaves the surviving book about
two points out of the money at the valuation month. The rejected alternative was raising
`discount_rate_annual` until the inequality held, which would have made a declared valuation
assumption a knob for getting the sign right.

**A natural spline, written out, because the projection extrapolates on every run (D-039).** The
champion's `loan_age` term is the natural cubic spline basis of Hastie, Tibshirani and Friedman
§5.2.1, in numpy. scikit-learn's `SplineTransformer` gives a B-spline basis with no natural
boundary constraint, so the fitted seasoning curve is a free cubic beyond the oldest loan age in
the sample — and the projection runs 180 months forward from a book whose oldest loan is 60 months
old, so it leaves the fitting range immediately. An unconstrained cubic there invents a prepayment
ramp and the `X1` sign pattern would be reporting an extrapolation artefact. A natural spline is
linear outside its boundary knots, which is the assumption an MSR projection ought to be making
and which a test can check by taking a second difference.

**The screen is not in the prompt, and the subject needs it anyway (D-045).** `bom_balance_log` is
`orig_upb_log` plus the log of a scheduled amortisation factor whose spread over five years of a
thirty-year loan is about 0.03 against 0.44 for the loan size, so its VIF on the training panel is
about 40,000. Fitting the champion on both is fitting on a difference of two columns that agree to
three decimal places, and the clean control would carry an `M1` on its first run — a finding that
would be *true*, about a package that declares both the original and the current balance, which is
what real prepayment packages do. So the hazard champion screens at a VIF of 10 exactly as the
classification champion does, by the same last-declared rule (D-031), and `model_summary.json`
lists what left. The cost is named rather than hidden: the rule takes `rate_change_12m` first,
because it happens to be declared tenth, and that is the column the regime is defined from. The
regime survives, because `regime.column` is `rate_regime`, which the subject writes into
`data_<split>.csv` and which was never a model feature.

**A split rule can be a drift finding, and here it would be one on every hazard package (D-046).**
Measured on the clean panel, PSI train-against-test is 0.065 at worst; train-against-out-of-time
is 3.09 on `burnout` and 2.41 on `loan_age`, and train-against-vintage-holdout is 0.62 on
`note_rate`. Those are not drift. An out-of-time split is *defined* as older loans in a later rate
environment — `package.yaml`'s own rule calls it "the refinancing wave the training window never
sees" — and a quantile-binned PSI between a window of ages 0–59 and a window of ages 24–59 puts
several bins on the 0.5% floor, each worth about 0.29 by itself. So the `psi` threshold and `S1`
are read as the train-to-test comparison, and the others are computed, stored and reported without
raising a candidate; Appendix D says so. Deciding it in Phase 4 rather than in Phase 5 is
deliberate, for the reason D-035 gives: the alternative is discovering in Phase 8 that the clean
control yields two findings and then picking the scoping that makes the test pass, which is the
same decision arrived at in the order that cannot be trusted. The rejected alternative — raising
the package's own threshold to 3.5 — would hide a real finding on the one comparison where PSI
means what it says.

**Two clean controls that behave differently (D-047).** The classification subject must yield
exactly `{E1 low}`: its champion cannot represent the interaction in its process, so a boosted
challenger legitimately beats it. The hazard subject must yield exactly `{}`: its champion is the
correct functional form for its process, and the measured challenger gap is **−0.0415**. A study
whose only control is one that always produces a finding cannot tell a detector that finds real
defects from one that finds findings; a study whose only control is silent cannot tell a detector
that works from one that says nothing. Three caveats are recorded with the expectation rather
than smoothed away: the `{}` depends on D-046's PSI scoping; `R1`'s sign-flip rule sits close to
the noise on this subject, since at four other seeds tried one weak seasonality or burnout
coefficient flips; and the fitted `burnout` coefficient is +0.079 where the process's is −0.18,
because burnout is a near-monotone function of loan age whose effect the spline absorbs. The last
of those is a fact about the fit that belongs in a validation report, not a defect.

**A common observation cut-off, so the projection has a book to value (D-044).** Spec §4.2's
"2,000 loans × 60 months", read as 60 months from each loan's own origination and combined with
originations spread over each cohort year (D-041), leaves the panel's last month reached only by
the loans originated in the youngest cohort's twelfth month — a servicing book of 26 loans. The
window therefore ends on one calendar month for every loan, as a real performance file does, and
the book is the whole surviving 2019 vintage: 511 loans and 96.6 million of balance. The rejected
alternative, valuing each loan from its own last observed month, makes "surviving balance by
month" a sum over loans at different calendar dates under paths shocked from different starting
points — a table nobody could interpret and `run_scenarios` could not reproduce.

**The subject restates its own declarations, and a test reconciles them (D-043).** Spec §3.2 hands
a subject a data directory and an output directory and no path to the package it is being
validated against, which is deliberate: a seeded variant's subject must not be able to read the
declaration it is being measured against. So `code/run.py` carries the five `scenarios` numbers
and `code/features.py` carries the split rules, and two tests assert that each agrees with the
loaded `package.yaml`. Duplication pinned by a test is the cheaper failure mode: it breaks the
moment the two drift. The rejected alternative — having `run_model` pass the block through on the
command line — makes the sandbox's argument vector depend on the model type and puts a declaration
Quaestor is verifying inside the process that produces the thing being verified.

**Two subjects, two copies of the VIF screen.** `variance_inflation_factors` and `vif_screen` are
about forty lines and now exist in both subjects' `code/features.py`. That is on purpose: a
subject is somebody else's code, the sandbox copies only its own `code/`, and a shared helper
module would either have to be copied in anyway or make one subject's fit depend on a file the
other subject owns. The two copies are identical and the two subjects' tests both check the
last-declared rule, so a divergence would be visible.

## Phase 5 — The tools, the registry and the statistics by hand

**One trace event per tool call, written in one place.** Every call goes through
`ToolRegistry.call`, which validates the arguments against the tool's own `Args` model, times the
run and writes the `tool_call` event — tool, argument hash, duration, artifacts, candidate
classes. No tool writes its own, which is why `RunModelTool` deliberately calls
`quaestor.sandbox.run_model` *without* a trace writer even though the sandbox is perfectly capable
of emitting one: the study counts tool calls from the trace, and one call that produced two events
would make every count of a run that ran a subject wrong by one. The rejected alternative — letting
each tool emit and having the registry not — spreads the field names of the event the study reads
across nine modules.

**A threshold is read by the name it is stored under, or not at all.** `Thresholds` is keyed by
logical artifact name (`threshold.M1.vif`, `rule.calibration_first_event_rate`), and
`Thresholds.artifact(store, key)` both stores the value and returns the artifact whose hash goes
into the candidate's evidence. There is no way to read a threshold without naming where a reader
can find it, which is what makes spec §12's "thresholds hard-coded in prose" unwriteable here. The
thresholds are stored **whether or not they are breached**, because the golden report's §3 says
the missingness screen "fires when missingness differs between splits by more than 10%" while
raising no candidate at all: prose that describes a rule that passed is still prose with a number
in it, and every number in a report needs an artifact behind it. The rejected alternative — storing
a threshold only when it decides something — makes exactly the sentences a clean report is made of
uncitable.

**The statistics are written out because a validator has to defend them one line at a time.** PSI,
CSI, KS, Brier, log loss, the calibration slope, VIF and Belsley's kappa are about fifteen lines
each in `tools/stats.py`, each with a longhand test whose expected value was computed by hand. Two
of them are not the obvious implementation. The calibration slope is fitted by Newton iterations
rather than by `LogisticRegression`, whose default `C = 1.0` penalises the coefficient: a perfectly
calibrated sample would come back with a slope short of 1 by an amount that depends on the sample
size, and the test that asserts a slope of exactly 1.0 on a sample constructed to have one could
not exist. PSI's bins are closed at the top (`(e1, e2]`), not half-open, because a feature with a
mass point — an imputed zero, a capped ratio — has several quantile edges at that point, and under
`numpy.histogram`'s convention every one of those rows lands in the *upper* bin along with
everything above it: a feature that is zero in 95% of the training rows and 50% of the test rows
then scores a PSI of exactly zero (D-051).

**`csi.<feature>` is not `psi.<feature>` under another name.** The golden report cites both, with
different values, so they cannot be the same computation. CSI here is the shift in the linear
predictor attributable to one feature: the same bins, weighted by what the feature contributes to
the fitted log odds in each of them. It answers "how much of the score's movement is this feature
responsible for", which the feature's own PSI cannot, and it is comparable across features because
it is in one unit. No rule reads it, so it is a reporting choice (D-052).

**`check_stability` refits, and says so.** The champion is one fit with one coefficient per
feature, so there is nothing of its own to compare across regimes; the tool fits a plain
unpenalised logistic regression *within each regime* on the standardised retained features and
compares those. The AUC half of the rule is different in kind: it is computed from the champion's
own stored scores within each regime, so it is a statement about the model that shipped. Ranking
the features by the refits' own mean absolute coefficient rather than by the champion's is what
lets the rule work on the hazard subject at all, whose design expands `loan_age` into spline
columns under names no regime fit shares (D-053).

**`run_scenarios` reads the subject's projection and recomputes everything derived from it.**
Rolling the fitted hazard forward needs the fitted hazard, which the validator never imports, so
spec §4.2 has the subject write `projection.json` itself. What the tool refuses to take on trust is
the arithmetic on top of it: the value change at each shock is recomputed as that shock's value
minus the base case's, and the convexity as the sum of the changes at the extremes. Where the
subject's own `value_change` or `convexity` disagrees with the recomputation the tool says so in
its summary and stores its own number — the same rule that keeps the developer's `metrics.json` out
of the outcomes analysis.

**`run_model` is the one tool that turns an exception into a finding.** The sandbox raises when a
subject fails, because a caller that asked for a run and did not get one must not carry on as
though it had; a *validation* of that subject does carry on, since "the model does not run" is the
finding. The tool tells the two cases apart by the store: the sandbox writes `run.stdout`,
`run.stderr`, `run.duration_s` and `run.status` before it raises anything about how the subprocess
ended, so their presence means the subject ran and failed, and their absence means the run never
started — a package with no `code/`, a contradictory pair of arguments — which is a failure of the
request and not a defect of the model. The rejected alternative, catching every `SandboxError` as
an `R0`, would put "you called the tool wrongly" into a validation report as a finding about
somebody else's model.

**`retrieve_guidance` is registered by nothing.** It needs the corpus and the BM25 index of
Phase 6. A stub returning no spans would let a planner call it, get an empty answer and carry on
as though guidance had been retrieved; an unregistered name is refused by `ToolRegistry.get`, and
the refusal is traced.

## Phase 6 — The regulatory corpus, BM25 by hand and the ninth tool

**Two documents, and one of them is superseded on purpose.** SR 11-7 was superseded on 2026-04-17
by SR 26-2, the interagency revision the OCC issued as Bulletin 2026-13. The corpus holds both:
`SR26-2` because it is the current guidance and what the drafter will cite from Phase 8, and
`SR11-7` because a citation written before April 2026 — the golden report's, this repository's
own, any bank document a validator has on file — must keep resolving. `SOURCES.json` records each
document's status, so "which guidance is this?" is answerable from the data rather than from
prose. OCC Bulletin 2011-12 is deliberately absent: it carried the same text as SR 11-7 and has
been rescinded, so ingesting it would give the retriever two ways to say one thing and would put a
rescinded issuance in front of a reader. The rejected alternative is ingesting OCC 2026-13 as a
third document — identical text under a second number, which would split the BM25 statistics
across duplicate sections and leave the retriever choosing between two identical spans on nothing
but corpus order (DECISIONS D-055).

**The ingest is a dev-time script and the corpus is data.** `python -m quaestor.corpus.ingest`
reads two PDFs the human downloaded, extracts their text with `pypdf`, splits by the outline files
in `data/regulatory/`, and writes three files into the package: `sr11-7.jsonl`, `sr26-2.jsonl` and
`SOURCES.json`. `pypdf` is imported inside one function of that script and nowhere else, so no
validation run and no test has a PDF parser in it; the PDFs themselves are never committed, and
`SOURCES.json` carries each one's `sha256` and page count so that the committed text can be traced
back to the bytes it came from. The rejected alternative is parsing the PDFs at runtime, which
would make every report depend on a parser's version and would put the corpus's provenance inside
a user's run instead of inside a reviewed commit.

**Splitting is equality, not similarity.** A heading matches a line only when the line *is* the
heading, its whitespace collapsed and its `I.` / `1.` / `a.` label removed; the search for each
heading starts after the previous one. That is what keeps SR 11-7's table-of-contents entry
`V. Model Validation, page 9` from being taken for the body heading `V. MODEL VALIDATION`, and
what keeps `Model Use` from matching the wrong one of the two sections that phrase heads. A
heading the outline names and the document lacks is an error naming it, and the fix in the message
says to correct the outline, never the text. Fuzzy matching was rejected for exactly that reason:
a near-match would pass and nobody would see which heading had drifted (D-056).

**BM25 by hand, with the `+1` idf.** `k1 = 1.5` and `b = 0.75` come from the spec; the smoothing
does not, and it decides the ranking. `ln((N − df + 0.5)/(df + 0.5) + 1)` keeps a term that
appears in every section at a small positive weight, where the unsmoothed form makes it negative
and quietly inverts the ranking of any query whose terms are all common — over a corpus about
models, that is the query "model". A span's scored text is its heading followed by its body,
because the acceptance query is "outcomes analysis" and that phrase is a section's *name* rather
than something its prose repeats. Spans scoring zero are dropped, so a query about something the
guidance does not discuss returns nothing rather than three arbitrary sections a drafter would
then cite. There is no persisted index: 37 sections is a linear pass, and a hand-written scorer is
the only kind whose arithmetic a test can check longhand, which `tests/test_bm25.py` does digit by
digit on a three-document toy corpus. A stop-word list was rejected: on two documents it would be
tuned against the queries it was tested on, and the idf already does the job visibly (D-057).

**`[[reg:...]]` stops being deferred.** Phase 2 parsed regulatory citations and returned
`deferred`, because there was nothing to resolve them against; that status is now gone from
`CitationStatus`, and a `reg` citation resolves against the committed JSONL or dangles with a
message naming it — `[[reg:SR11-7:V.3]]` lists the sections SR 11-7 actually has, and
`[[reg:OCC2011-12:V]]` says which two documents the corpus holds. A resolved regulatory citation
carries the section's heading, so a renderer can name the anchor without re-reading the corpus. The
new `CorpusError` covers the corpus failing to load or to ingest and is deliberately *not* what a
dangling citation raises: a broken installation stops a run, an invented citation is prose the
repair loop fixes (D-058).

**The ninth tool computes nothing about the model.** `retrieve_guidance(query, k, docs)` stores
one JSON artifact, `guidance.<query_hash>`, holding the spans with their scores, and raises no
finding candidate — it can raise none, because guidance is what a section is anchored to and not
evidence that a model is wrong. The artifact matters as much as the return value: it is what the
drafter is shown and therefore what the trace records it was shown, so a report anchored to the
wrong section is diagnosable afterwards without re-running anything. The name hashes the whole
request rather than slugifying the query, because "outcomes analysis" and "outcomes analysis, by
split" slugify alike and the store refuses to reuse a name for a different payload; the golden
report's readable `guidance.outcomes_analysis` stays illustrative, under the carve-out Phase 5
already wrote into `tests/test_tools_clean.py` (D-059).
