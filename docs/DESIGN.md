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
a late level rise in the rate path, the real 2022–23 move, which moves the surviving book about
two points — mean first-projected-month incentive **+1.288** without the ramp and **−0.717** with
it, a move of 2.005 points that leaves the book out of the money at the valuation month, which is
the sign the inequality needs (D-170). The rejected alternative was raising
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

## Phase 7 — Findings, the claim grammar and the verifier that owns the denominator

**The pre-pass is the point, not the extractor.** Grounding precision is the number this project
asks to be judged on, and it has an obvious failure mode: an extractor that returns fewer numbers
scores better, because every number it omits leaves the denominator. So the model does not own the
denominator. `extract()` makes one `structured()` call and then tokenises the same prose
deterministically; every numeric token the model did not return becomes a claim with status
`unattributed`. The pre-pass can only add. Two consequences fall out of that and are asserted:
a `FakeLLM` that returns two of four numbers still produces four claims, and a silent extractor
scores an extraction recall of 0.0 with every sentence `unattributed` rather than a precision of
1.0 over nothing. The rejected alternative — trusting the extractor and spot-checking it — is what
makes a grounding figure a measurement of an extractor rather than of a report.

**A line is the sentence.** The pre-pass works line by line, and within a line matches tokens to
the model's claims **by value and in order**. That is what attaches the right citation to the right
number in "0.7412 against 0.7538", with no model involvement in the attachment. The rejected
alternative is matching by character offset inside the sentence, which breaks the first time the
drafter writes `3,500` and the extractor returns `3500`; matching by value and order survives every
reformatting of the number that does not change which number it is. The report format writes one
sentence, or one table row, per line, so the unit is the unit a claim quotes; a drafter that writes
a three-sentence paragraph on one line still gets order matching within the paragraph.

**Six exclusion classes, and only what they actually swallowed.** D-015 fixed the list — section
and finding numbering, regulatory section ids, the eight hex characters of a citation, the package
version, inline code, renderer blocks. Every one of them lowers the denominator, so `claims.json`
publishes the list with the tokens each class removed, and the count is printed in Appendix A. Two
details are Phase 7's own. A class is recorded only when it *did* swallow a numeric token, so the
published list is evidence rather than boilerplate; citations are the exception, since their hash
and logical name are excluded by construction. And `\d+\.` is section numbering **only at the start
of a line** — an unanchored version also matches the `0.` of "no feature is flagged 0." and would
delete a claim invisibly, which is the failure mode an exclusion list is most dangerous for.

**Matching is arithmetic with a receipt.** The matcher resolves the citation itself, normalises
percent to ratio (and basis points to a rate) when the artifact lives in the unit interval, applies
D-014's per-unit tolerance widened by any declared rounding, and records the artifact value and the
tolerance it used on the claim. That last field is why Appendix A can be read: a reader who wants
to know why 0.74 verified against 0.7412 can see the 0.005 that allowed it, and why `23%` did not
verify against 0.2213. A `delta` is `second − first` and a `ratio` is `second ÷ first` over two
adjacent citations; a `delta` carrying one citation **dangles with a message** rather than
verifying against its single operand, which is the one place a permissive reading would let a
made-up difference through.

**Findings: three verbs and a receipt.** `Finding.from_candidates` merges candidates of one class,
unions their evidence, and demands a one-sentence reason whenever the severity it publishes differs
from the one the check suggested — and refuses a reason with no change, because a reason beside an
unchanged severity reads as a change that did not happen. Every promotion writes one `finding`
trace event carrying both severities and whether they differ, so the study counts re-severitisation
from structured data. The evidence rule reaches the model through pydantic's validation context
rather than through a field, and reading a written document back waives it deliberately and by
name (D-061): `eval/score.py` scores a run from `findings.json` on a machine that no longer has the
artifacts, and the golden report's hashes resolve to nothing by design.

**The verifier component fixtures are this repository's own.** `04` §6 evaluates the verifier alone
on FinQA and TAT-QA in Phase 13; Phase 7 ships the offline half against ten tables written here.
Each item renders three sentences — correctly cited, perturbed, uncited — and the expected statuses
are `verified`, `mismatch`, `unsupported`. The number that matters is the middle one: a ±5–15%
perturbation of a rate of 0.035 moves it by less than the 0.005 the grammar allows, so the sentence
is *supposed* to verify. Those items are reported as **tolerance boundaries**, with the tolerance
that produced them, and never as errors — a component eval that scored its own tolerance as a
mistake would push the tolerance down until real reports started failing. Two of the ten items
land there at seed 20260901, and the run log says which.

## Phase 8 — The drafter, the repair loop, the renderer, the planner and `validate()`

**The tolerance is the precision the prose used, not a constant (D-069, amending D-014).** Phase 1
gave every claim a flat tolerance from its unit — 0.005 for a ratio in the unit interval, 0.5 for a
percentage on a 0–100 scale, 1% relative otherwise — and that rule verifies `0.021` against an
artifact of `0.0175` and `22.0%` against `0.2212`. Neither sentence is true at the precision it
chose to write, and grounding precision is the number this project asks to be judged on, so the
rule now reads: a claim verifies when the artifact **rounds to the value as written, at the
decimals the prose actually used**, with spec §0's default for the unit as the ceiling the
tolerance never exceeds and `rounding` an explicit override that can only narrow. The precision is
read from the claim's own sentence rather than from its float, because `22.0` and `22` are one
float and two statements. Trailing zeros before the point run the same rule backwards: `-1130000`
claims nothing below ten thousand, so its precision is `10^4` — which is what lets a currency
amount written to four significant figures verify against the figure it was rounded from, and what
the ceiling stops from ever becoming loose. The rejected alternative was keeping the flat rule and
asking the drafter to declare `rounding` on every number, which puts the honesty of the headline in
the hands of the component being measured. Measured consequence: the golden report's 92 claims all
still verify and its pre-repair `0.0136` still mismatches, 60 of the 92 record a narrower tolerance
than the Phase 1 file, and the two tolerance boundaries of the Phase 7 component eval are now
caught as the mismatches they are.

**A drafter can only cite what it was given.** The rule in the prompt is "write no number that is
not in the JSON", and `report/sections.py` is what builds that JSON: per section, a selector over
logical names, the tables the section may direct the renderer to expand, and the JSON artifacts
whose numeric paths it may address. The selectors select **scalars** — a table matched by
`calibration.` would hand the outcomes section every calibration table the run produced — and JSON
artifacts are flattened into the dotted paths a citation can name, so `run.model_summary` can be
cited as `#coefficients.utilisation.value` without the drafter guessing the payload's shape.
Values arrive at four significant figures, which the tolerance rule above makes safe: a number
copied out of the JSON verifies against the artifact it came from, and a number rounded further
verifies too.

**The renderer owns the report's structure and the drafter owns its prose (D-071).** Section 6 has
a fixed shape — one `### F-NNN · <class> <name> · severity **<severity>**` heading per finding, in
severity order, with the ids the findings document assigned. Asking a model to reproduce that
exactly is asking it for something a renderer already knows, so the drafter is *given* each heading
and asked to write beneath it, and the renderer then re-composes the section from what came back:
the text before the first `###` is the section's opening, each finding is emitted under the
canonical heading with the drafter's body under it, and a finding the drafter ignored keeps the
narrative its candidates gave it. Nothing the drafter wrote is discarded, which is the failure mode
of the obvious alternative. The rejected alternative was one `structured()` call per finding, which
would make section 6 a different prompt shape from every other section and the study's per-section
token counts incomparable.

**The wrapper is the other end of the pre-pass's argument.** A pipeline that deleted a number it
could not verify would report a better grounding precision the worse its drafter was, because the
denominator would shrink with the numerator. So a claim that survives two repair rounds stays in
the prose, wrapped `⟦unverified: 0.68⟧`, and `REPORT_SCHEMA.json`'s third refusal rule makes it
compulsory: under `full_agent` an uncovered number that is not wrapped is a report the renderer
will not write. Wrapping runs over the *masked* prose — the same masking the pre-pass uses — so a
claim of `6` can never turn `[[art:6bff3109:…]]` into something that is not a citation.

**Nothing the renderer or the template writes carries an uncited number (D-076).** `rules_only` is
the study's control and spec §3.13 calls its claims "trivially verified"; if its precision is not
1.0 then the figure reported for the other two arms is not a property of the models that wrote
them. So the template writes `The value of \`<logical_name>\` is <n> <citation>.` — the name in
inline code, the value cited — and never the artifact's caption, since a caption like "change in
servicing value at -300 bp" carries a number no citation follows. The renderer's own section-6
lines name classes and tools in inline code and nothing else. The rejected alternative was wrapping
renderer-written lines in renderer blocks, which the schema's block pattern does not allow and
which would make the exclusion list unauditable.

**The planner's refusals are traced, not raised.** The rule-based plan is a function of
`package.yaml`; the bounded loop is four steps at most, and an action it takes may be refused for
three reasons — an unknown tool, arguments the tool's own closed `Args` model rejects (which is
where an invented `entrypoint` is caught), or a path that leaves the package and the run's own
directories. A refusal is a `plan_step` event with its reason and the loop continues, because a
model that mistypes a tool name has not asked to stop. The loop is shown the tools' generated JSON
schemas rather than a prose description of them, which is the same "one source, three consumers"
the registry was built for.

**`validate()` lives in `pipeline.py`, the configurations in `configs.py` (D-070).** The three arms
of the study differ only in a table of data — which plan runs, who writes the narrative, whether
the repair loop runs — because a difference between two runs has to be a difference a reader can
point at, not a difference in what some branch happened to do. The pipeline reads the table and
runs one pipeline. The module is outside `CLAUDE.md`'s layout, like `vocab.py` before it, and for
the same reason: `configs.py` is imported by the layers `validate()` orchestrates, so a module that
was both would be a cycle waiting for the first import in the wrong direction.

## Phase 9 — The command line and the record of a run

**The pre-pass owns the eligible set in both directions (D-077).** Phase 7 made the regex pre-pass
the floor under the denominator of grounding precision: a number the extractor omits is added back
as `unattributed`, so the headline cannot be improved by an extractor that works less. That left
the ceiling open. A model asked to list "every number, including those inside a citation's logical
name" will sooner or later return the digits of `[[art:a3f2b1c9:scenario.value_change.-300]]`, and
Phase 7 would have counted them — as a claim, resolving as `unsupported`, *lowering* precision for
a number no reader would call a claim. So a returned claim now survives only if it can be matched
to a token the pre-pass left eligible, and one that cannot is dropped and published under
`extractor_returned_excluded_token`. The matching is two passes, both by value: within the line the
claim quotes, then, for what is left over, against any unfilled token of the section. The second
pass is what keeps a paraphrasing extractor from losing its citations, and it is the rejected
alternative's answer — the alternative being to match by the sentence alone and throw away any
claim whose text does not appear verbatim, which punishes a model for rewording rather than for
being wrong.

**A prompt too long for one argument goes on stdin (D-078).** `ClaudeCLILLM` passes the prompt as
the positional argument after `-p`, which is what a human debugging a call would paste into a
shell. Above 64 KiB of UTF-8 it does not: macOS caps a single argument well below the total it
allows, and the failure is an `OSError` raised before the CLI runs, so the adapter emits `-p` with
no prompt after it and writes the prompt to the subprocess's stdin instead. The rejected
alternative was always using stdin, which would have made the argument vector the tests assert on
differ from the command a human can run by hand — and the first thing anyone does with a failing
live call is run it by hand.

**Two cassette stores, deliberately (D-079).** `llm/recording.py` writes one JSON file per model
call beside the run's own report, keyed by `stable_hash(system, prompt, params)`, so that a
published validation can be replayed (`--llm replay`) and re-read rather than taken on trust.
Phase 11's Probatio cassettes are a different thing with a different job: a test suite's tapes,
recorded through Probatio's provider fixture, committed under `tests/probatio/`, replayed by CI as
gate condition 6. Keying by request is what makes a replay reproduce a run over the same artifacts;
its cost is that one identical question asked twice keeps one tape, which the file records as
`calls` rather than hiding. The rejected alternative was recording through Probatio, which would
put a development dependency inside the live `validate` path.

**The fake that `--llm fake` builds ships in the wheel (D-080).** `CLAUDE.md`'s own command list
ends with `--llm fake`, and a bare `FakeLLM` answers a drafting prompt with a string
`structured()` rejects. So the competent offline drafter is `quaestor.llm.OfflineLLM`, in `src/`,
and `tests/reportsupport.py` subclasses it to build the drafters that forget a citation or refuse
to correct a number. The behaviour the quick start runs is therefore the behaviour the repair-loop
tests are written against, and a reader with the wheel and no API key can reproduce the demo. The
rejected alternative — importing the test helper from `cli.py` — would put `tests/` on the runtime
import path.

**Three commands, and the other five are unknown (D-082).** `--help` lists `validate`, `tool` and
`corpus`; `quaestor study run` is an "invalid choice" error, exactly as a misspelling is. It is the
Phase 0 argument about half-built flag surfaces applied to the front door: a `--help` that lists
what the program will do one day cannot be read to find out what it does today. The exit codes are
the other half of that interface — `0` did it, `1` ran and produced nothing (a report the renderer
refused, a check whose run directory is empty), `2` the request was wrong before anything ran — and
every message on standard error names a fixing command, which is spec §3.1's rule about errors
applied to the command line. `--timeout` caps the subject rather than the provider (D-083), because
the subject's cap is the one a real-sample run on a slow machine actually hits; and bare
`--synthetic` reads each subject's documented size from a table in `configs.py` (D-081) rather than
inventing one, because the size of a generated panel decides every figure computed from it.

## Phase 9 follow-up — What the first live validation changed

The operator's half of Phase 9 ran on 2026-09-08 and refused to render. It found three things nine
phases of offline tests had not, and `docs/EVALUATION.md` §1 writes the run up with its numbers.
Two of the three are decisions about structure and belong here.

**One tokenizer, and the wrong call no longer exists (D-084).** Four rules in this pipeline are
statements about one set — the numbers of a section's prose that count as claims. The pre-pass owns
the denominator (D-064); a claim for a token outside the set is dropped (D-077); a claim that did
not verify is wrapped in the prose and never deleted (D-073); and a report carrying an unwrapped
number outside every verified claim is not written. Phase 7 to Phase 9 computed that set in three
places, all of them calling one masking helper whose `package_version` argument defaulted to
`None`. The pre-pass passed it; the renderer and the repair loop did not, and neither had ever met
prose that mentions the package's version, because the offline drafter writes one sentence per
artifact. The first live drafter mentioned it in its first paragraph of section 2. The fix is
`src/quaestor/verifier/tokens.py` and the single function `eligible_numbers(markdown, *,
package_version=None)`, which returns the masked text, the section's lines, the eligible tokens
with their offsets and line indices, and the excluded tokens with their classes — everything all
three callers want, so that none of them has a reason to compute a part of it. `masked_prose` is
deleted rather than given a required argument: the trap was that the short call was the wrong one,
and a public function whose easy spelling is wrong is a defect waiting for its second author. The
rejected alternative was reading the version out of the report's own front matter inside
`uncovered_numbers`, which makes a checker parse the artifact it is checking and does nothing for
`wrap_unverified`, which has no report to parse.

**The extractor names a line instead of quoting it (D-085).** `ExtractedClaim` asked for the whole
line each number sits on, copied exactly. On the live run that made extraction 8 of 17 model calls
and 63,865 of 92,196 output tokens, with the longest call at 20,257 tokens and 197 seconds, because
a sentence carrying four numbers is re-typed four times with its citations. The field is now
`line`, a 1-based index into the prose the prompt showed — `numbered_prose` prints it, one numbered
line per line, and `numbered_lines` reads it back — and the deterministic side resolves the index
against the prose it sent before the pre-pass runs, so `Claim`, `claims.json`, `CLAIMS_SCHEMA.json`
and the claim id (which hashes `[section, text, value]`) are all unchanged. An index out of range
is treated as D-077 treats an ineligible token's claim: dropped, counted in `n_from_model`, and
published in the exclusion list. D-077's second matching pass now covers the misnamed line as well
as the paraphrase it was written for. The argument is D-063's, one field further on — a value the
caller can compute is a value it should not ask for — and the reason it took a live run to notice
is that no offline test pays for an output token. The rejected alternatives were a character offset
inside the sentence, which the drafter's own thousands separators make unreliable, and a truncated
prefix of the text, which keeps the failure mode and makes the claim id depend on how the model
truncated.

**`L2` needed a null, and the synthetic control could not supply one (D-086).** The contamination
screen hashed each row's feature values and fired above 0.5%. That is exact on both synthetic
subjects, whose generators draw continuous features, and it is a false-alarm generator on a real
credit panel of coarse integers, where 1.2556% of the test rows repeat a feature vector of train
because two different clients wrote the same row. The screen now measures three things and reports
all of them: the identifier overlap (`leakage.overlap.ids`, using the row's identity — the declared
`id_column`, and the period as well for a hazard panel), the feature-vector overlap
(`leakage.overlap.features`, the Phase 5 quantity, with `leakage.overlap` kept as an alias because
the Phase 1 golden cites it), and `leakage.duplicates.train`, the share of train rows whose feature
vector is not unique within train. A shared identifier is severity high at the unchanged threshold.
A shared feature vector is severity medium, and only above twice the within-train share — the rate
at which coincidence happens in this dataset, measured on the one split where contamination cannot
be the explanation. The threshold did not move; what changed is that the question now has a
comparison in it. This is the shape of every honest fix to a false alarm: the rejected alternative
was raising `threshold.L2.overlap` until the real sample passed, which is choosing the number that
makes the run green and would hide a real 3% contamination on a coarser panel.

## Phase 9 follow-up 2 — What the second live validation changed

The second `credit_default` attempt (`eval/results/first-live/credit-attempt2/`) is a shorter
story than the first and a sharper one. The plan ran clean in 2.69 seconds — thirteen calls, no
candidate at all, D-086's `L2` false alarm gone — and the bounded loop spent the run's one model
call asking for `check_stability` on a package that declares no `regime.column`. The tool raised,
and the exception walked out of `validate()`: fourteen tool calls, 693 output tokens, $0.10,
fifteen seconds, exit 1, no report. Three things were wrong at once, and they are three decisions.

**A tool that raises is the step's failure, not the run's (D-088).** `follow_up_plan` catches
`ToolError` from a loop-requested call. The step is traced with `accepted: true`, `executed:
false` and the tool's message; the message is quoted back to the model on the next step; the step
counts against the maximum of four; the pipeline goes on to draft. `PlanStep` and the `plan_step`
event both gain `executed` and `error`, which is what lets a reader — and `eval/score.py` — tell a
step the planner refused from a step the planner accepted and the tool could not answer. The
asymmetry is deliberate and is the point: a `ToolError` from the **rule-based** plan is still the
run's failure, because that plan is what a validation of this package must check and a report
missing one of its own checks is not a report. The loop is the model's extra question, and being
told no is one of the answers it was always allowed to get. The rejected alternative was recording
the failure as a refusal, which would make the planner's record disagree with the registry's own
`tool_call` event and its `ok: false`.

**The menu is filtered by what the package supports (D-089).** The request was answerable before
it was made: the same `regime.column` that decides whether the rule-based plan calls
`check_stability` decides whether the tool can say anything at all. `inapplicable_reason` is now
the single definition — `check_stability` needs a regime column, `run_scenarios` needs a hazard
subject with a `scenarios` block, `run_model` is never applicable, which is spec §3.12's own rule
read as an applicability question — and `loop_prompt` filters the catalogue by it while
`validate_action` refuses a request for a filtered tool with `not applicable to this package: …`.
Filtering is the fix and refusing is the second line of defence, because a model may name a tool
that is not on its list. The new rule is applied **last** of the four, after the tool exists, its
`Args` take the arguments and no path leaves the package: `run_model` is the only tool carrying a
path argument, so an applicability-first order would make the path rule unreachable through
`validate_action` and would answer two precise questions with one vague message. The rejected
alternative was leaving the menu whole and relying on D-088's catch, which is a model call and a
tool call spent learning a fact `package.yaml` states.

**The loop is shown what ran, not only what was found (D-090).** The attempt's stated reason was
"the plan only compared regimes on the fitting split" — a sentence about a call the plan never
made. The Phase 8 prompt said the plan "has already run" and then showed only the candidates, and
a planner told only what was found cannot tell a check that did not run from a check that ran and
found nothing. Those are exactly the two cases a follow-up is chosen between. The prompt now
carries one line per completed call — tool, arguments, and the defect classes it raised or `no
candidate` — built by `completed_calls(plan, results)` from the two lists `pipeline.py` already
holds, and one line per earlier step of the loop, saying whether it was refused and why, accepted
and failed and with what message, or accepted and run. The instruction that the loop is for a
follow-up on what the candidates show, and not for repeating the plan, stays. The prompt became
`loop_prompt`, a function, so that a test can send the loop the bytes a recorded run was sent; the
rejected alternative was pasting each call's `ToolResult` summary, which would scale the loop's
cost with the store rather than with the plan.

**How the attempt is replayed.** `tests/test_live_credit_attempt2.py` reads the trace for every
figure `docs/EVALUATION.md` quotes, then puts the live model's own answer back through the
pipeline: `ReplayLLM` serves the run's single cassette under the key it was recorded with — the
recorded prompt, read back out of the cassette — and the offline fake answers every call the
attempt never made. The tape is not re-keyed onto today's prompt, because D-089 and D-090 changed
that prompt on purpose and a cassette's key is a hash of the request; what is replayed is the
answer, byte for byte, and the assertion is that it is now refused with a reason and the run
renders a report.

## Phase 9 follow-up 3 — What the first rendered live report changed

The third live `credit_default` validation is the first that reached a report: 19 model calls, 13
tool calls, 159 post-repair claims, grounding precision 0.9816 rising to 1.0000, no finding, exit
0. Every number in it verifies. Two of its *sentences* are false, and neither is a failure of the
model's reasoning — in both, the drafter was handed an incomplete set of artifacts and reasoned
correctly over what it had. `docs/EVALUATION.md` §1 carries the run; this section carries the
design argument.

**A rule that derives its bound has to store it (D-091).** D-086 made the feature-overlap arm of
`L2` fire on `max(threshold.L2.overlap, 2 × leakage.duplicates.train)`, which on the live panel is
0.02324 rather than the declared 0.005. That number lived in a local variable. So section 3 was
shown a threshold of 0.005 and an overlap of 0.01256, compared them correctly, called the result an
exceedance and wrote that it "is recorded as a finding" — while section 6, which had
`findings.json`, correctly said none was raised. The invariant D-086 broke is Phase 5's:
`Thresholds.artifact` is the only way a tool reads a threshold, so a number that decided a
candidate is in the store by construction and its hash is in that candidate's evidence. A bound
computed from the data is still a bound that decided a candidate. `tools/thresholds.py` gains
`effective_name(base, rule)` as the one spelling of the pattern, `check_leakage` writes
`threshold.L2.overlap.features_effective`, both `L2` candidates cite it, and section 3's brief says
which arm is read against which bound. The prompt half is the second line of defence, not the fix:
`_candidates_block` now writes the literal `candidates raised for this section: none -- describe
nothing as a finding`, lists and counts the candidates where there are any, and says they are the
only findings that section may describe. A drafter told "describe nothing as a finding" while
holding an exceedance it can demonstrate is being asked to write a sentence it can see is wrong,
which is how a competent model is made to look incompetent.

**A prefix is not a taxonomy (D-092).** Section 4.4's developer-threshold table said PSI was "not
recomputed in the artifacts available to this section" while sections 1 and 3 both cited
`psi.max`, and listed the subject's wall-clock cap as a performance threshold. Both follow from
one selector: `threshold.package.` matched `threshold.package.max_seconds` and did not match
`psi.max`. D-013 already forbids the drafter to retype a table the store holds, and this was the
one table it was still being asked to compose — from scalars whose relationship to each other it
had to infer, for the table a validation report is most often read for. `compute_metrics` now
writes `thresholds.evaluation` from the same loop that raises `T1`, so the table and the rule
cannot disagree; the drafter writes `[[table:thresholds.evaluation]]`; the cap becomes
`runtime.max_seconds`, which is the name `package.yaml` gives it; and section 4's selector takes
every `threshold.*` and `psi.*` scalar so the prose around the table can cite what it discusses.

**The record has to describe the run (D-093).** Three failures of that, each fixed where it is
produced. The front matter said `model: claude-cli`, which is a subprocess — the adapter is what
you re-run and the model id is what a published study compares, so `ReportInputs` gains `model_id`,
read off the run's own `llm_call` events, and Appendix C gains a `provider adapter` row beside the
`model` row. The `run_id` was `credit_default-full_agent-d03b07c6`, which is the string attempt 1
carries: an identifier introduced to join a report to its trace was joining each report to two
traces, so `_run_id` puts the UTC second the run began in front of the input hash — the hash still
says two runs had the same inputs, and the stamp says they were different runs. And Appendix C
reported 38 input tokens for 19 calls: `input_tokens` alone is what the prompt cache neither wrote
nor read, and `ClaudeCLILLM` now sums it with `cache_creation_input_tokens` and
`cache_read_input_tokens` for the 176,851 the cassettes actually record. Cached input is cheaper
than fresh input; it is not free, and Phase 12 publishes a cost per report.

**One number, one spelling (D-094).** The decile table printed `0.6855555556` four lines below
prose that wrote `0.4952`. The drafter is shown four significant figures and writes what it sees;
a renderer block beside it showing ten digits of the same quantity invites the arithmetic to be
checked against the wrong number, and asserts a precision no statistic in the report has.
`_table_cell` prints measures at four figures and integral cells as integers, recovering the type
first — a table artifact's payload is canonical text, so a period label like `2024-01` has to
survive being printed as it stands. The artifact keeps every digit; only the rendering of it is a
reader's number.

**Evidence for the paragraph the validator wrote from inference (D-095).** Section 2's most useful
paragraph observed that utilisation enters the champion negatively "against the standard view",
offered a reading, and said the reading was the validator's own. "The sign is wrong" and "the sign
is wrong and it costs two AUC points" are different statements to a developer, and only the second
can be acted on. `check_collinearity` is where the sign check belongs, because a near-dependency
among the columns is *why* a coefficient takes a sign its own marginal relationship contradicts;
`challenger_compare` is where the ablation belongs, because an ablation is a refit-and-compare and
that is what the tool already is. Neither raises a candidate: a sign flip is frequently the model
correctly conditioning on the other columns, and a rule that fired on it would manufacture exactly
the false alarm D-086 exists to refuse. `ablation.baseline_auc` is stored beside the deltas because
the refit is not the champion's own fit — the validator never imports the subject — so the number
each delta is measured from is named rather than assumed to be `metrics.test.auc`.

**"No findings" must not mean "no questions" (D-096).** Section 6 of the third attempt is four
sentences saying nothing was raised, immediately after sections 2 and 3 made two observations a
developer should answer for. A finding in this project is a rule firing, and the rules are
deliberately narrow — the whole seeded-defect study measures how narrow — so a section 6 that says
only "no finding was raised" invites the reader to conclude something about the model that it does
not support. `### Open items` is a required level-3 subsection: one line per observation, each
citing its artifact and naming an owner. The renderer lifts whatever the drafter wrote under the
heading, places it last and supplies the heading where the drafter omitted it, on D-071's argument;
`check_structure` asserts it. It is checked in code rather than added to `REPORT_SCHEMA.json`,
whose heading list is the eleven level-2 headings and is pinned to the Phase 1 golden under D-011.
Promoting open items to `info` findings was rejected: they would enter `findings.json`, the
severity counts and the study's precision denominator, so a helpful observation would score as a
false alarm.

**Both halves of a repair (D-097).** Appendix A said "after 0 repaired claim(s)" of a run whose two
rounds removed three numbers. A rewritten claim is paired with what replaced it and becomes a
`repairs` row; a removed number has no `after` side, and D-073 records it on the trace event alone
rather than inventing a half-empty row. That was right; the appendix was reading half the record.
The count comes from the trace rather than from a new `claims.json` field, which keeps
`CLAIMS_SCHEMA.json` untouched and costs nothing, since the renderer already holds the events for
Appendix C.

**What the model is for is not a property of the sample (D-098).** Spec §3.11 orders section 4 by
the event rate. `msr_prepayment`'s hazard probabilities are multiplied by a surviving balance to
value a servicing strip, so calibration leads whatever its rate is; `credit_default`'s scorecard
ranks applicants at a 22% default rate. The two questions only coincide because rare events are
usually modelled for their level. `PackageSpec` gains an optional, nullable
`use: ranking | probability | both` — the one `package.yaml` change of this follow-up, decided in
Cowork — and `section_four_order` returns the ordering **and** the ground for it. Where the
declared use decided, `rule.calibration_first_event_rate` is dropped from section 4's selector
rather than merely not mentioned in the brief: D-091's lesson applied before the fact, since the
surest way to stop a drafter citing a number as a justification it did not serve is not to hand it
the number. A package that declares nothing behaves exactly as it did in Phase 8.

**How the attempt is checked.** `tests/test_live_credit_attempt3.py` re-derives every figure
`docs/EVALUATION.md` quotes from that directory's trace, claims, findings, index and 19 cassettes,
and for each defect asserts both halves: the attempt's own store lacks
`threshold.L2.overlap.features_effective` and `thresholds.evaluation` and carries
`threshold.package.max_seconds`, and a run of the same plan on this build is the other way round.
The token defect is asserted against the attempt's own recorded `usage` objects, which is the one
place `ClaudeCLILLM`'s mapping can be checked against a real payload without calling a model.

## Phase 9 follow-up 4 — What the first working loop changed

The fourth live `credit_default` validation is the first in which the bounded follow-up loop did
anything: 22 model calls, 17 tool calls, four plan steps of which three executed, 161 post-repair
claims, grounding precision 0.9641 rising to 1.0000, no finding, exit 0, $4.1603, 908.59 s. Its own
record is accurate for the first time — D-093's model id, run-id stamp and three-field token sum
all hold, and the cassettes agree with the trace. `docs/EVALUATION.md` §1 carries the run; this
section carries the design argument.

**The pipeline taught the drafter a form its own verifier could not read (D-099).** All six of the
run's failed claims are one defect. `NUMERIC_TOKEN_RE` had no exponent form, so `1.92e-05` matched
as `1.92` and then, the lookbehind having refused the sign, as `05`: a mantissa the artifact does
not hold and a bare exponent that is a *claim of five the report never made*. Three literals
produced six `unattributed` claims, and attempt 3's removal of `9.982` and `6` was the same defect
a run earlier, recorded there as an extraction miss. The drafter did not invent the notation:
`json.dumps` writes a value of 1.9e-05 at four significant figures as `1.92e-05`, and the drafting
prompt is where it came from. The tolerance half matters as much as the tokenizer half — the
mantissa keeps the precision and the exponent moves it, so `1.920e-05` claims 10^-8 and is held to
half of that, where holding the mantissa's three decimals against an unscaled `0.0005` would verify
anything of that order and read D-069 backwards. The two other copies of the expression in the tree
move with it: the offline fake's, which is deliberately a copy because a provider may not import
the report layer, and `tests/test_golden_spec.py` check 7's literal. `eval/verifier_eval.py`'s fake
extractor gains the citation mask the offline fake always had, because `[[art:2e30351e:answer]]`
holds `2e30351`, which is `inf`.

**A selector is not a list of the names its author thought of (D-100).** Section 7 recommended
monitoring the Brier score against its declared ceiling and then wrote that "no recomputed test
Brier value is carried in this report's artifact store" — of a report that cites
`metrics.test.brier` in three other sections. The monitoring selector took every
`threshold.package.*` and hand-listed three of the four recomputed values a declared bound needs.
So the fix is at the selector and it is a derivation:
`recomputed_for_declared_bounds` reads the `thresholds.evaluation` rows D-092 already writes and
adds `metric_artifact_name(metric, split)` for every bound this section matched, which means the
selector cannot fall behind `package.yaml` again. `DRAFT_INSTRUCTION` gains the standing rule
beside it — the artifacts listed are this section's selection and not the store, and no section may
call a quantity absent, uncomputed or "not carried" — because every section has a selection and
every section can make this mistake. The prompt rule could not have been the whole fix: the
sentence was true of what the drafter was shown, and a drafter forbidden to say a number is missing
while genuinely not having it would simply have said nothing about Brier monitoring.

**A step the run paid for is reported (D-101).** Three executed loop steps computed twenty-four
sub-population scalars, among them test AUC of 0.5875 and Gini of 0.1749 on the 6,048 rows of 9,000
where `delinq_count_6m == 0`, against 0.7550 and 0.5100 on the whole split. Section 4's selector
matched every one and its drafter was shown every one, and the report says nothing about any of
them — correctly, because the brief does not ask and the step's own stated reason was never passed
to any prompt. That is D-090's argument in the other direction: do not withhold from the model what
the caller already has, and the caller had `PlannedCall.why`. `FollowUp` carries the tool, the
arguments, the reason and the names the step **added** to the store; a section whose selector
matched one of those names is shown the block and must answer it under `### Follow-up analyses`, a
level-3 heading for D-096's reason. Three parts of the rule are decisions rather than mechanics.
Routing on what a step *added* rather than on everything it stored, because a follow-up
`compute_metrics` recomputes every split's metrics on its way to the slice and routing on those
names put the block in section 2, which cites `metrics.test.auc` and knows nothing about slices.
The summary is never assigned a step although its `metrics.` selector matches, because section 1 is
derivative by construction and an analysis reported there before it is reported anywhere is a
headline with no body. And the renderer supplies the heading where the drafter omitted it, so the
rule cannot throw away a finished report — which is the lesson of D-084 stated as a constraint on
every new structural rule.

**Where a follow-up result goes is a rule, and a rule needs a bound in the store (D-102).** The
practitioner's answer is that a slice materially worse than the headline is a question for the
model developer and belongs in section 6's open items, and any other slice is supporting evidence
where it was computed. "Materially worse" therefore has to be citable (D-091), so
`compute_metrics` stores `metrics.<split>.sub.<slug>.auc_gap` and `.share` beside the eight scalars,
and `threshold.O1.slice_auc_gap` = 0.08 and `threshold.O1.slice_min_share` = 0.10 through
`Thresholds.artifact`. The bound is new rather than a second use of `threshold.O1.auc_gap`, which
carries the same number, because the two comparisons are different questions:
`threshold.O1.auc_gap` reads train against test and measures overfitting, while a slice-to-headline
gap reads one split against part of itself and measures heterogeneity. Sharing the number would
mean re-tuning one rule silently re-tunes the other and that `THRESHOLD_SUMMARIES` puts a
train-to-test caption on a within-split comparison, which is D-092's naming argument. The size
floor exists because a slice of thirty rows can differ from its split by anything at all. Neither
bound raises a candidate, on D-095's argument: a model that discriminates less well on a segment
selected by one of its own features is usually a model conditioning correctly. And an open item is
written as a question — conditioning on a delinquency count also conditions on its correlates, so
the segment is also one of near-constant delinquency history, and what a developer is asked is what
the model discriminates on inside it.

**A section with nothing to report says so once (D-103).** Section 6 said no finding was raised and
then listed seven reviews, two of which — "input data lineage" and "documentation of intended use
and known limitations" — no check performs, on a package whose Appendix D says it has no `docs/`.
The prompt had asked it to "say what was checked instead" without giving it the list, so it
produced a plausible one, which is the one thing a validation report must never do: overstating
coverage is worse than understating it. The list was two lines lower the whole time, in the
renderer's own "Checks that ran and raised no candidate" line built from
`checks_without_candidates`. So the drafter is forbidden to describe what was reviewed, and the
computed line is the enumeration — D-013's argument about retyping what the store holds, applied to
a sentence rather than a table.

**Section 7 is told what section 4 did (D-104).** Section 7 recommended that monitoring lead with
calibration below a 0.05 event rate "as this report does", of a report whose section 4 opens by
saying it reports discrimination first. D-098 made `section_four_order` return the ground as well
as the answer and gave it to section 4's brief alone; `ordered_briefs` now fills section 7's brief
from the same function, with the sentence that says which way section 4 reported and, where it led
with discrimination, the prohibition on the sentence this run wrote. One function fills both, so
the two sections cannot disagree. This is the third instance in three follow-ups of one section
reasoning correctly from an incomplete brief, and the fix is the same shape each time.

**Nearness is not identity (D-105).** Appendix A reported "1 claim(s) rewritten and 5 number(s)
removed" of a round that rewrote none and removed six, and `claims.json` carried a row saying the
`1.92` of an ablation sentence became the `2` of "2 are known at origination".  `_pair` tried the
claim id, failed — the re-draft dropped the sentence, and the id hashes the text — and fell through
to "the nearest unpaired verified value within a tenth", which on a report of 167 claims is a
coincidence waiting to happen. What the fallback is actually for is the two things a repair does to
a line, and both leave the line's prose standing, so the test is now about the line: the claim's
text with its citations and numbers removed, or the logical name it still cites. The reason the
id-first pass cannot do that job is that `Claim.text` is the whole line including the citation
(D-085), so attaching a citation changes the id — which the docstring claiming otherwise had wrong.
Where a re-draft leaves neither link the round is recorded as a removal, which under-reports one
rewrite and cannot invent a row joining two unrelated sentences; a reader can find the number in
the prose and see it was not removed, whereas a false pairing invites them to believe a sentence
about utilisation was corrected into a sentence about feature timing.

**Two smaller ones, and one deferred nothing (D-106, D-107, D-108).** The prose reads "the timing
screen flags 0.0 features": D-094 made integral values integers in the renderer's tables and left
the drafting prompt out, and the prompt is the half a reader quotes. The loop's first step asked for
a sub-population of `credit_limit` on a subject whose column is `limit_bal`, spending a model call
and a tool call on a static fact, so `loop_prompt` now carries the data's own column names, read
from the header of `data_<split>.csv` rather than from `package.yaml` — the subject's screen drops
features before fitting, and what a slice can be taken on is what the data holds. And
`retrieve_guidance` ranked one list across both corpus documents, so the data-quality and
sensitivity queries returned three SR 11-7 spans each and no SR 26-2 span at all: sections 3 and 5
could only open on text superseded in April 2026, while `SR26-2:IV.1` and `SR26-2:V.1.a` sat
unretrieved. BM25 scores compare inside a document and not across two of different length and
vocabulary, so a single ranked list chose the report's anchor by term frequency — which is not the
retriever's decision to make. `k` becomes per document, the revision's spans first, and which to
cite stays the drafter's choice under D-055 and `DRAFT_INSTRUCTION`. That instruction was already
there and already obeyed; it did nothing for a section that was never shown a revision span, which
is worth recording as the shape of a prompt fix that cannot work.

**How the attempt is checked.** `tests/test_live_credit_attempt4.py` re-derives every figure
`docs/EVALUATION.md` quotes from that directory's trace, claims, findings, index and 22 cassettes,
and for each defect asserts both halves: the run's own six failures are the two halves of three
literals and each literal verifies on this build; the twenty-four slice scalars were all selected
for section 4 and the step's reason appears in no cassette's prompt; the monitoring selector still
does not name `metrics.test.brier` and `artifact_briefs` now hands it over; the run's own two
retrievals held no SR 26-2 span and `retrieve_per_document` offers three; and the pairing that
produced Appendix A's false row is refused by `_pair` on the run's own two sentences.

## Phase 9 follow-up 5 — What the first defect the verifier cannot see changed

The fifth live `credit_default` validation rendered on a build carrying D-084 to D-108: 22 model
calls, 17 tool calls, four plan steps of which **all four executed**, 285 post-repair claims,
grounding precision 0.9827 rising to 1.0000, no finding, exit 0, $6.0535, 1,328.47 s. Six of the
seven defects the fourth attempt found did not recur. It is also the first report to carry
`### Open items` with anything in them: two questions for the model developer, on the two
delinquency slices the loop chose. `docs/EVALUATION.md` §1 carries the run; this section carries the
design argument.

**A repair round is not licensed to rewrite the section (D-109).** The round on section 4 flagged
four numbers. The drafter was sent the whole section, as it always has been, and returned the whole
section — including a line nobody had flagged, which came back as "…by 0.007286 […] on test and by
-0.02732 `[[art:41fca294:metrics.train.sub.utilisation_high.auc_gap]]` **is not the figure for this
slice**; on train the gap is -0.001109 […]". That is a clause about the high-utilisation slice
spliced into the low-limit paragraph, with the sentence adjudicating itself in the middle. Every
citation in it resolves and every number matches its artifact, so the report's grounding precision
is 1.0000 and no part of this pipeline can see anything wrong with it. That is what makes it
different from every defect the four earlier runs found: grounding precision measures
whether a number matches the artifact it cites and says nothing about whether a sentence is about
the thing its paragraph is about, so the answer cannot be a better check. It is a smaller blast
radius. A round provoked by four numbers may change the four lines those numbers are on; every
other line of the section is kept byte-identical, and a line the re-draft added elsewhere is not
taken. The attribution is the delicate half, because section 4's four sub-population paragraphs are
written to one sentence skeleton and each flagged line therefore has three siblings that read almost
exactly like it. Attributing *every* returned line to the line of the previous draft it most
resembles, before deciding what to keep, is what solves that: a re-drafted sibling resembles its own
former self more than it resembles the flagged line, because its numbers are its own. Citations come
out before the comparison, for the reason `_skeleton` takes them out — attaching one is a thing a
repair *does*, and thirty characters of shared hash and logical name made a line whose citation was
being added look more like any other line carrying that citation than like itself. Replayed on the
run's own section 4: four lines re-drafted at 0.926 to 0.981, no other returned line attributed to a
flagged line at all, and the damaged sentence never written.

**The prompt rounded two counts and then flagged them (D-110).** `four_significant_figures(10158)`
is 10160, and the matcher holds a count to half a unit, so `metrics.train.sub.limit_bal_low.n` and
`metrics.train.sub.delinq_last_eq_0.n` reached the drafter as numbers their own artifacts do not
hold. The drafter copied what it was shown, which is the rule the entire selection mechanism rests
on. This is the same shape as D-099 one run earlier — the pipeline teaching the drafter something
its own verifier refuses — and the fix is the same kind of one-line distinction: four significant
figures is a rule about how much *precision* to quote, and a count has none to give up. 10,158 rows
rounded to 10,160 is not a simpler statement of the same quantity. `prompt_value` returns an
integral value exactly and everything else at four figures; `four_significant_figures` still decides
precision and D-106's `as_written` still decides spelling.

**Nearness, the line and the name are three tests, and only one of them survives a generated family
(D-111).** D-105 gave `_pair`'s fallback two grounds, either sufficient. On a report whose section 4
holds four paragraphs of one shape — which is the bounded loop's own doing, one per executed step —
the line ground pairs anything with anything: the flagged `limit_bal_low.n` of 10160 and the
untouched, verified `utilisation_high.n` of 10500 have the same line once numbers and citations come
out, and 10500 is inside the relative window. Appendix A duly reported a rewrite of a round that
rewrote nothing. The grounds are therefore ordered rather than alternative: a flagged claim that
cites a name is about that quantity and its replacement must cite it too; the line is for the claim
with no citation, which is the case it was invented for. The general point is worth keeping: a test
that is strong on seven hand-written paragraphs and weak on a generated family will keep weakening,
because the loop is meant to do more work over time.

**Two of the run's five failed claims were never claims (D-112).** "**delinq_last equals 0.**" opens
a follow-up paragraph and the `0` is a slice rule's parameter; "Section 4 of this report" is the
report's own numbering. Both were counted in the denominator, flagged as unsupported and removed by
a repair round that existed largely for them. The two halves are fixed differently on purpose. A
section reference is an exclusion class — the numbering is the report's wherever it appears, and a
reader can check the rule without reading the sentence, which is what an exclusion class has to be.
A slice parameter is not: `0` in "delinq_last equals 0" is a value in the data, and a pattern
excluding a bare integer after a column name would swallow real claims about that column. What makes
it not a claim is that it is a rule, and the way prose says "rule, not measurement" is to set it in
code — which the tokenizer has masked since D-015, which needs no new pattern, and which reads
better. So one number leaves the denominator by a rule about structure and two by a rule about
style, and both are recorded, because a denominator that quietly shrinks is what an exclusion list is
most dangerous for.

**Two the reading found that no rule fired on (D-113, D-114).** The prose writes logical names
beside the citations that carry them — "by up to threshold.O1.slice_auc_gap at 0.08
`[[art:0a827b87:threshold.O1.slice_auc_gap]]`" — because the prompt shows the drafter a JSON object
keyed by logical name and gives it no other vocabulary for the quantity; one sentence in the standing
instruction, not in a brief, for D-100's reason. And section 7 wrote that benchmarking against an
alternative model "was not part of this validation" three pages after section 2 reported the
challenger comparison. That is D-100 in the half D-100 could not reach: it made a section shown a
*bound* also shown the *value* and forbade calling a quantity absent, but an activity is not an
artifact and the prohibition is about numbers. Section 7's brief is now told the challenger exists,
which is the same fix as D-104's and for the same reason it is a fact rather than a prohibition — a
drafter told only what not to say has nothing true to put there.

**The loop's output was 72 of the report's 285 claims, and none of them was a judgement (D-115).**
Each executed slice wrote nine metrics on each of two splits into section 4's prose, one cited number
at a time. That is D-092's situation exactly, one table later: `compute_metrics` now stores
`metrics.<split>.sub.<slug>` beside the scalars, the renderer expands the directive as it does for
any table, and the follow-up brief asks for the directive plus the sentences that *read* it — the gap
against its bound, the share against its floor, and whether mean predicted against the observed rate
puts the weakness in the level of the probabilities or in their ordering. The evidence is unchanged
and better attested, since a table the tool computed cannot be mistyped and is not extraction's
business at all (D-013). The scaling is the argument: a design where every question the loop earns
adds eighteen transcribed numbers to one section gets more expensive and less readable with every
step, and the part that is actually a validator's work — a number read against a bound — is the part
that stays in prose. No saving is claimed. Four live runs at n = 1 each have put extraction at 357,
284, 173 and 183 output tokens per claim check with no change to the extractor between the last
three, which measures how much the model chose to think and nothing else; what Phase 12 will measure
is a report with 72 fewer claims in it.

**How the attempt is checked.** `tests/test_live_credit_attempt5.py` re-derives every figure
`docs/EVALUATION.md` quotes from that directory's trace, claims, findings, index and 22 cassettes,
and for each defect asserts both halves: the six defects of attempt 4 are each read off the report as
absent; the two mismatched counts are shown to be what `four_significant_figures` produces and what
`prompt_value` no longer does; the three unsupported tokens are shown excluded under the new rules;
the pairing that produced Appendix A's false row is refused by `_same_statement` on the run's own two
claims; and the run's own section 4 is replayed line by line through `scope_to_flagged_lines`, which
re-drafts four lines and leaves the damaged sentence unwritten.

## Phase 9 pre-flight — What the archive found without a live call

Five live runs have cost about $22 and an hour and a half of wall-clock, and every defect class in
`docs/EVALUATION.md` came out of a person reading one of their reports. The runs are committed
(D-087), which means the reading is repeatable by machine, and the sixth live run should not be
paying to rediscover anything the fifth already wrote down. This follow-up turns the three rendered
runs into fixtures.

**The check has to run over the drafts, not the reports.** Generalising `tests/test_golden_spec.py`
check 7 — every eligible numeric token of the prose covered by a post-repair claim, and every claim
covered by a token — to the three archived reports passes on all three. That is worth asserting and
finds nothing, and the reason it finds nothing is structural: a repair round's answer to a number it
could not verify is usually to delete it, so a token that provoked a round is precisely the token
the shipped report no longer holds. The population of unknown token classes lives in the *first
drafts*, and those are recoverable — every drafting call is a committed cassette, and a repair
round's previous draft is quoted verbatim inside its own repair prompt. Rejected alternative:
pointing the check at `report.md` only, which is the version written first and which passes.

**What sharing means here.** The coverage counting lives once, in `tests/claimsupport.py`, and
check 7 calls it: two copies of "what does covered mean" are two chances to disagree, which is
D-084's whole lesson. The *tokenizer* is deliberately not shared. `tests/test_golden_spec.py` is
the executable specification of the report and imports no part of the package it specifies, so
check 7 keeps the numeric expression as a literal kept in step by hand — as D-099 did when the
exponent group was added to both — and `claimsupport.py` importing nothing but the standard library
is what lets the specification use it without acquiring a dependency on the implementation.
Rejected alternative: importing `quaestor.verifier.tokens` into the golden test, which would make a
change to the tokenizer agree with the specification by construction.

**One new token class in five runs.** `(D-050)`, in attempt 3's section 4: a reference to this
project's own decision log, counted as a claim of fifty, flagged, and removed by a round whose
re-draft also cost the section a verified `0.08` on a line nobody had flagged. D-116 takes both
halves — the tokenizer excludes `\bD-\d{3}\b` under a class of its own, and no artifact caption
carries a decision reference, which is where this one came from. Both are needed, and the archive
is what shows it: attempts 1 and 3 sent byte-identical section-4 prompts, and only attempt 3 copied
the reference out of the caption, so a caption fix alone leaves a form the verifier cannot read and
an exclusion alone leaves the tool's bookkeeping in a bank's report. Rejected alternative: a
sentence in `DRAFT_INSTRUCTION`, which is D-113's remedy and cannot stop a caption being copied.

**Three classes the archive shows earlier than the run that named them.** D-099's exponent form
appears in attempts 1, 3 and 4 and was named at 4; D-112's section cross-reference in words appears
in attempt 1 and was named at 5; and D-109 — a repair round rewriting a line nobody flagged — was
decided on one round of one run and is visible in five of the six rounds the archive holds, ten
lines in all, with `scope_to_flagged_lines` keeping all 245 unflagged lines of those six previous
drafts byte-identical. The D-111 pairing over the three runs' real records reports 0 rewritten and
3, 6 and 5 removed, which is the third instance of a false rewrite row and the first time attempt
3's has been recorded.

**What the fixtures cannot do is written into them.** The re-extraction after each archived round
ran on that run's own unscoped re-draft, so no cassette holds the extraction of a scoped one: the
replay asserts the text and its docstring says the claims cannot be replayed. Attempts 1 and 2
wrote no `claims.json`, so the coverage question cannot be asked of them, and attempt 1's drafts are
read against the verified `claim_check` events of its trace instead. A re-draft is found by the
section its prompt names, which is unambiguous only because no archived section went to a second
round — asserted, so an archive that acquires one fails rather than replaying the wrong tape.

**Two residuals closed while the archive was open.** `scope_to_flagged_lines` now returns a
`ScopedRedraft` carrying `scoped`, and the `repair` trace event prints it, so the one path on which
D-109's guarantee does not hold is a fact in the record rather than an inference from a line count
(D-117); the decision is read off the return value rather than recomputed by the caller, for the
reason D-084 exists. And `tests/test_pipeline.py`'s two Phase 9 follow-up cases move from a
1,200-row panel and `"E1" in` the findings to the default panel and the whole set, because `in`
passes on a panel that also raises `T1` at high and the difference is 0.24 s a run (D-119).

## Phase 9 follow-up 6 — What the run the README excerpts changed

The sixth live `credit_default` run is the `credit_default` live validation. It rendered on
`fc33dd7` with 210 claims, grounding precision 1.0000 before repair and 1.0000 after, no repair
round, no finding, no open item, exit 0, $3.9739 and 872.74 s, and it is committed under the bare
name `eval/results/first-live/credit/` because it is the run the README excerpts. Reading it against
that bar found one deterministic defect and five sentences whose wording misreads outside the
report's own context. The two get different treatments, and the difference is the point of this
follow-up.

**The record is not edited, and the excerpt is.** `report.md` is what the pipeline produced. Its
value in a README is that a reader can be told "unedited, and here is the trace, the cassettes and
the artifact store it was written from" — which an edited file cannot be told about, however small
the edit. The five wording edits are therefore applied in the excerpt only, listed verbatim in
D-120 so Phase 16 copies rather than reconstructs them, and printed as a before/after diff in
`docs/PROVENANCE.md`. None of them changes a number, asserted by tokenizing both sides of each pair
and comparing values; each `before` is asserted to be in the committed file exactly once, so the
decision entry cannot drift from the file it quotes. Rejected alternatives: editing `report.md` and
noting the edits, which makes every later citation of the run's grounding precision a citation of a
file a human touched; and excerpting a paraphrase, which is the thing a validation report exists not
to be.

**A slice that is the whole split is a refusal, not an answer.** The loop's third step asked for
`delinq_count_6m above_median`; the column's median is 0, `>= median` selected every row of both
splits, and the tool answered — share 1, an AUC gap of 0, 22 logical names per split for a
population identical to its parent, two rendered tables, and a step of four spent. `_select` now
raises on the D-088 path, so the step is recorded accepted and not executed and the loop re-plans.
Two choices inside it. The bound is a **stored ceiling** at 0.95 (`threshold.O1.slice_max_share`)
rather than an exact share of 1, because a slice holding 0.98 of its split has the same defect and
testing for degeneracy alone would fix the one case the run produced; 0.95 says only that nobody has
measured a better value, which is what D-102 says about its own two numbers, and it is deliberately
not derived from `slice_min_share` so that re-tuning the open-item floor cannot silently re-tune
what the tool will compute. And the check is a **pre-pass over every split asked for**, because a
slice that is a proper part of train and the whole of test would otherwise raise with train's
artifacts already stored, leaving the drafter half a slice it could legitimately cite. Rejected
alternatives: answering and letting the section plan drop it, which spends the step and leaves the
artifacts; and raising a candidate finding, which would put a defect in Quaestor's own rule into the
developer's `findings.json`.

**The two median rules partition the split, and the median's rows are in the lower half.** The
refusal alone leaves the interesting population unreachable: on a delinquency count that is 0 for
two thirds of the book, `< median` selected nothing and `>= median` everything, so neither rule
could name the never-delinquent segment that attempts 4 and 5 both found material at test AUC 0.5875
and 0.6312 against 0.755. `below_median` is now `<= median` and `above_median` is `> median`. Which
side the tie closes is arbitrary on a continuous column — the sample median of an even draw sits
between two observations — and not arbitrary on the coarse, heaped, zero-inflated columns a real
credit panel is made of, where the population worth slicing is almost always the mode at the bottom.
`equals:` needs no edge of its own, because D-121's check reads the share the rule resolved to and
not the rule. Rejected alternatives: `<` and `>`, which partitions nothing and leaves the median's
own rows in neither half; and a fourth rule such as `equals_min`, which is a new argument for a case
two existing rules cover.

**The loop is told the rule.** D-089, D-090, D-107 and now D-123 are one argument applied four
times: a prompt that invites a mistake and then charges a model call for it is a prompt with a fact
missing. `_LOOP_INSTRUCTION` states that a sub-population must be a proper part of the split, where
the median boundary falls, and that a rule resolving to the whole split is refused with the share it
selected. The boundary is the half the model cannot derive, because D-122 is a choice. Rejected
alternative: putting it in the `Subpopulation` field description, which is generated from the `Args`
model and shown to every caller, where this is a sentence about how the bounded loop should choose.

**The archive gains its negative case.** D-118's fixture is keyed on tables — `KNOWN_RESIDUE`,
`REDRAFTED`, `UNFLAGGED` — that only a run with a repair round contributes rows to, so until now
every check in it was a check of what failure looks like. This run flagged nothing, so it adds no
row to any of them, and that absence is asserted rather than assumed: zero uncovered tokens in every
one of its seven first drafts, the absence of a round read out of the trace, `claims.json` and
Appendix C together, and every written line of every first draft found in `report.md` — the last
being a check the general one has to skip for a repaired section (D-124).

**What did not happen is also a result.** No repair round means D-109's scoped re-draft has still
not run live, and no cassette in the archive holds one, because all six archived rounds were made by
builds without the scoping in them. `docs/EVALUATION.md` §1 records that as a gap in the evidence
rather than as a passing test, and its "What the excerpt does not show" subsection carries the rest
of the known limitations — zero findings is evidence and judgement and not detection, the loop's
slice choice varies and this run missed the segment, the decile reversals no rule reads, the sign
disagreement nothing routes, the mixed corpora, and n = 1 — so Phase 16 quotes that list rather than
writing a new one.

## Phase 10 — The taxonomy and the seeded-defect generator

`eval/taxonomy.yaml` is the study's specification and `eval/seed.py` is the only thing that reads
it. The taxonomy holds eighteen rows — fourteen seeded variants over nine classes and two
subjects, plus four controls — and every seeded row carries the class, the recipe, the recipe's
parameters, one `met_where` sentence in the author's own words and an `expected_signal` written in
the tools' own logical names. That last column is the point of the file: it is a prediction made
before the recipe was written, and `tests/test_seed.py` reads it as an acceptance test, artifact
by artifact and bound by bound. D-136 records what each one measured.

**A recipe patches the package, not the data.** There is no data file anywhere in a variant: a
recipe edits `package.yaml`, edits `code/`, or hangs a transform off the one seam in each
subject's entrypoint where the data-building step has finished and the model has not started —
the classifier's `splits = {...}` line and the hazard subject's. So a variant is a package a
developer could plausibly have handed over, its diff against the clean subject is a few dozen
lines, and both data modes go through the same code. Every anchor is checked: an anchor that
appears the wrong number of times raises rather than silently seeding nothing, because a generator
that quietly seeds nothing puts a guaranteed miss in the study and blames the detector for it.
The rejected alternative is a directory of `.patch` files, which is the same fragility with none
of the error message.

**`SEED.yaml` is the answer key and lives outside `package.yaml`.** Spec §5 asks for the
provenance in a file the pipeline never reads; `quaestor.package.loader` opens `package.yaml` and
nothing else, and two tests hold that line — one spies on `Path.read_text` through a
`load_package` call, the other plants a value in a variant's `SEED.yaml`, validates that variant
end to end under the offline provider and asserts the value reaches no trace event, no artifact,
no claim and no line of `report.md`. The generator itself stays in `eval/` for the same reason
(D-127): moving it into `src/quaestor` would make the module that plants the defects importable
from inside the process that is supposed to find them, so `quaestor study build` loads it from
beside the `--taxonomy` it was given and says so when it is not there.

**Variants are artefacts, not sources.** `eval/variants/` is gitignored and only
`eval/taxonomy.yaml` and `eval/seed.py` are committed; a variant built from real data would carry
rows of it, which is the second reason. Building the same recipe twice writes the same bytes —
`seed()` removes its target and rebuilds from the clean subject, and nothing a variant writes
depends on where it was written, which is why `Variant` carries the variant's *id* rather than its
directory name.

**Two defects in Quaestor were found by seeding, and both are the same shape**: a tool refusing to
run on precisely the data the seeded defect produces, and the refusal ending the whole validation
rather than being reported. `challenger_compare` conflated "not a number" with "missing", so the
`D1` variant produced no report at all (D-125); `compute_metrics` propagated the calibration
slope's non-convergence, so the `msr` `L1` variant — whose leaked balance separates the outcome
exactly — produced no report either (D-126). Both are now facts the report can carry: a
`challenger.missing_values` record and a skipped ablation in the first case, an absent slope, a
`calibration.separable.<split>` flag and a "not evaluated" threshold row in the second. Neither
changes anything about the clean controls, which have no missing cell and no separable split.

## Phase 11 — The Probatio test layer, and what four record sittings cost to learn

Spec section 6 fixes three case families and what each asserts. It does not say where a case's
input comes from, and that turned out to be the load-bearing question. A Probatio case is committed
data, and committed data drifts: a `draft_section` case whose artifacts no longer match the store
still drafts *something*, and a `contains` needle that is no longer a claim of the live report
still passes as long as the model writes the digits. Neither failure shows in a green suite, and
both would be replayed from a tape for as long as the tape lived.

So nothing in `tests/probatio/cases/` is typed by hand. `casebuilder.py` runs the pipeline once,
offline, with `OfflineLLM`, and **spies on the two collaborators that decide what a model is
shown** — `pipeline._draft_inputs` and `pipeline.follow_up_plan` — rather than re-deriving their
answers. What a case carries is the object the drafter and the loop were actually passed,
serialised. `test_inputs_pinned.py` then asserts that every committed file is byte-identical to
what the builder produces now, and, the assertion that matters, that **the prompt a case builds is
the prompt the pipeline sent, to the byte**. Rejected alternative: hand-written YAML reviewed once,
which is the drift this arrangement exists to prevent; and a spot check over a few artifact names,
which passes on exactly the changes that invalidate a tape.

A byte count is not a pin, and this was learned the expensive way. Correcting one word pair in
`_LOOP_INSTRUCTION` (D-146) changed every planning tape's cassette key and not one byte of any case
file, one command before a recording. Each case therefore carries `metadata.prompt_sha256`, the
digest of the prompt its system under test really sends — `structured()`'s appended schema
included, because that is what a cassette key hashes — computed by running the case's own system
under test against a recorder, so no composition is restated. After the third sitting a second
door appeared: a rubric is part of every *judge* prompt, and editing it strands the judge half of
every drafting tape without touching the system-under-test prompt at all. Hence
`metadata.rubric_sha256` beside it. Rejected alternative: committing the whole prompt beside each
case, which is 190 KB of a second copy of what the builder can produce.

**No adapter sits between Probatio's `Provider` and Quaestor's `LLM`.** The protocols were written
to be structurally identical for exactly this phase, and they are: the `provider` fixture goes
straight into `Drafter`, `extract` and `structured`. The one wrapper the suite adds, `_LastAnswer`,
is not an adapter — it passes the call through and remembers the answer's text, because a case
asserts on *what the model returned* and all three systems under test return something parsed.
Asserting `schema_valid` on a re-serialisation of the parsed object would be a statement about
pydantic; and an answer `structured()` refused twice would arrive as an exception where the suite
needs a failing assertion.

Two relations needed an encoding rather than a field name. `@format_jitter` reformats a **string**
and `@distractor_robust` inserts **strings**, while the drafter needs six typed spans and a list of
typed artifacts. So `input.guidance` is the spans' bodies joined by a separator with their
identities in `metadata` — which puts the jitter on the only part of a span that is prose, and
never on the `[[reg:...]]` citation an upper-casing transform would destroy — and the distractor is
one artifact of the *other* subject carried as a JSON string. What the distractor relation cannot
see is recorded rather than claimed: the distractor is in the variant's own artifact list, so a
drafter that cited it would still satisfy the case's assertions.

### What the four record sittings actually found

The layer cost about $71 across four sittings and found four defects. Exactly one is in
`src/quaestor`, and it is small: `_LOOP_INSTRUCTION`'s degenerate-slice example named a rule that
D-122 had already made impossible, so the prompt's own first clause falsified its own example
(D-146). The other three were in the test layer, and the two rubric defects are the interesting
ones because of *how* they failed.

The first asked the judge to quote the sentence that decided its verdict — inside a JSON string
field. **80% of judge replies came back unparseable**, every one of them carrying a verdict the
model had got right, and because a discarded verdict fails its assertion and a variant's verdict is
compared with the original's, **every relation violation the first two recordings measured was a
formatting failure in the grader rather than a change in the application** (D-148, D-152). The
second was subtler and is the one worth remembering: criterion 5 forbade a section to say that a
quantity is absent — and collapsed *quantity* into *activity*, so it failed sections 5 and 7 for
saying that a cross-regime comparison is undefined without a regime column and that no post-sample
outcomes exist yet. Both sections were doing exactly what their own briefs ask, and D-114 had
already drawn that line: D-100's prohibition "is about numbers … it could not stop a section
calling an entire activity absent" (D-153). The grader was wrong and the drafter was right, on two
of seven sections, on the first recording where the replies parsed at all.

The progression across the three graded recordings is **80% → 25% → 0%** unparseable. Only the
criterion-5 rewrite is a permanent correction; the four bullets the rubric now spends on JSON
syntax are a stopgap for Probatio issue 1 (`notes/probatio-issues.md`), and when a parser that
reads the first balanced object lands upstream they can go.

Two measurement lessons are recorded because they change what a future phase should trust. The
**cost** model fitted from the Phase 9 trace held: it predicted a whole record run's spend to
within 6%. The **latency** model from the same eighteen calls did not — it was out by a factor of
6.6 on one section — because wall clock on this provider is dominated by service variance and not
by how much the model writes. So per-case cost ceilings are estimated and per-case latency is one
uniform generous number, and D-150 says which of the two earned the right to a per-section figure.
Rejected alternative: re-fitting the latency model on two sittings of a quantity that varied
6.6-fold within one of them.

Finally, the layer is exercised offline in a way that cannot poison it. An offline
`--probatio-provider fake --cassette=off` run fails every content assertion by design — that is
what proves the cases load, the systems under test are wired and the relations expand — and
`BaselineStore.compare` records a baseline when a case has none, so such a run silently stamped the
fake's failures as the reference for three cases and made a clean live recording report drift
(D-154). Every fake invocation now passes `--baseline-dir $(mktemp -d)`.

### What the fifth sitting found: a prompt that contradicted itself on every run ever made

The tapes are not only a regression fixture; they are eight samples of what a live model does with
a real prompt, and reading them found a defect that no amount of reading the code had. Section 6's
prompt carried `candidates raised for this section: none -- describe nothing as a finding` and,
eleven lines lower, the finding it was ordered to write about. The two lines came from two
arguments of `Drafter.prompt` filled from two objects, and because `SECTION_FOR_CLASS` maps no
defect class to the findings section — a finding's `section` names the material it rests on, not
where it is printed — the first was empty on **every run this project has ever made** while the
second was not.

What makes it worth a paragraph is the shape of the failure rather than the wording bug. All eight
recorded drafts obeyed the more specific instruction, wrote "this validation raised no findings",
and moved the `E1` finding into `### Open items` — with every number cited, every value matching the
store, and the grounding judge passing all eight at 1.0. **Grounding precision cannot see a missing
finding.** Neither can the claims appendix, the severity counts or the renderer, which prints
`FindingsDocument`'s own headings and would have put `### F-001` two lines below the drafter's
sentence saying nothing was raised. This project's whole verification apparatus measures whether
what the report *says* is true of the store; it has no instrument for what the report *omits*, and
that is a limitation worth stating plainly rather than discovering again.

The fix single-sources the two blocks in `Drafter.prompt` rather than in `pipeline._draft_inputs`,
so the contradiction is unassemblable for every caller and not merely unreached by the one that
exists (D-156). Rejected alternative: editing the committed case's `input.candidates` by hand so
that the case stopped contradicting itself — which is precisely the drift D-138 exists to prevent,
and would have left every future run's prompt exactly as wrong while making the layer report it
fixed.

## Phase 9 follow-up 7 — An honest subject, and the check that nothing said had happened

Two things the first real MSR sample left behind, fixed together because both are about the gap
between what the run did and what the record shows.

**The subject's own calibration slope was not the estimator it claimed to be, and nothing said so.**
`run.py` computed it with `sklearn.linear_model.LogisticRegression(max_iter=1000)` — the default
`C = 1.0`, the default `tol = 1e-4` — where `quaestor.tools.stats.calibration_slope_intercept`
computes the unpenalised maximum likelihood estimate by its own Newton iteration and says in its
docstring that it avoids scikit-learn for the penalty's sake. The first real run had the developer
reporting 0.966 where the validator recomputed 1.017, and the first draft of the package answered
it by dropping the claim. That was the wrong repair. These subjects are honest developers whose
every deliberate structure is documented (D-017, D-045); an undocumented estimator quirk that moves
a headline diagnostic by 0.05 is neither, and the disagreement it produces is our artefact rather
than a finding about the model. `_calibration_slope` now fits the
maximum likelihood estimate, the claim is back at 1.017, and an offline test asserts that the
subject and the tool agree to 1e-6 on every synthetic split so that the pair cannot drift apart
again (D-160's consequence paragraph).

**The diagnosis was right about the disagreement and wrong about its cause**, which is the part
worth writing down. Decomposing the real splits into penalised, unpenalised at lbfgs's default
`tol = 1e-4`, and unpenalised and converged gives test 0.965971 / 0.966011 / 1.016836 and train
0.957077 / 0.957093 / 0.997101: the penalty is worth **4e-5**, because at 135,060 rows and two
parameters `C = 1.0` is nearly no prior, and the whole **0.0508** gap is lbfgs stopping on the
gradient short of the optimum. Removing the penalty was still necessary — spec 3.7 means the
maximum likelihood estimate — but a commit that had removed only the penalty would have re-run the
panel, moved nothing, and left the two estimators as far apart as they started. What made the
effect look like shrinkage is that it appears only where the slope is near 1: at 0.43 out-of-time
the default tolerance is already converged to 5e-5, and the two splits that disagreed were the two
whose model is roughly calibrated. The lesson generalises past this subject — **two implementations
of one estimator can differ by more than the quantity being measured purely through convergence
criteria**, and neither one is wrong in a way its own tests would catch.

The spelling is `C = np.inf` rather than `penalty=None` because scikit-learn deprecated `penalty`
in 1.8 and 1.9 emits a `FutureWarning` naming `C=np.inf` as the replacement — and the subject's
standard error is stored as the `run.stderr` artifact, so a warning there is a content-addressed
change to every run rather than noise on a terminal. `tol` is set to the 1e-10 the tool's own
Newton iteration uses, so the two are converged to the same place by construction. Rejected
alternative: relaxing the agreement test to the 1e-2 the default tolerance can actually hold, which
would have passed while leaving a headline diagnostic 0.05 short and the drift the test exists to
catch invisible.

**The manifest check was performed and unreported.** Under `--data` the loader verifies every
SHA-256 in `data.manifest` before anything else happens, and a report of a run that got as far as
being written is a report in which that check passed — but only its *absence* was ever printed, as
an Appendix D row when no data directory was read. `pipeline.validate` now writes a `data.manifest`
table artifact when and only when the loader verified one, section 3 may cite it, and Appendix C
carries one positive row. The guard is the artifact's presence rather than the data mode, so
synthetic runs and the golden report do not move (D-162). Rejected alternative: a renderer sentence
in section 3, which is prose no claim can be checked against — the point of the artifact is that
the digest check now lives under the same grounding contract as every other number in the report.

## Phase 9 follow-up 8 — A converged comparison, and a rule that reads how well it is estimated

The instance of the previous follow-up's defect that it left open was our own.
`tools/stability.py` documented "a plain unpenalised logistic regression is fitted within each
regime" and called `LogisticRegression(max_iter=_MAX_ITERATIONS)` — the penalised default at
lbfgs's default stopping tolerance — and it was deferred on the ground that changing it would move
the golden report and every committed run's `stability.*` artifacts. That ground was checked
rather than trusted, and it is false on both counts: the golden report and `credit_default`
declare no regime column, so `check_stability` never runs on either, and **not one of the six
committed runs under `eval/results/` holds a single `stability.*` artifact**. A reason that is
never re-checked outlives the fact it was about, which is why the correction is a dated line on
D-160 rather than a silent fix. Converged at `C = np.inf` and `tol = 1e-10` (D-163), the
per-regime coefficients agree with an independent Newton fit sharing no code with them to **1e-5
absolute**, where the old estimator differed from the same fit by up to **0.314** — and the regime
AUCs do not move by a byte, because that arm reads the champion's own scores and refits nothing.

**The agreement test asserts an absolute difference and not a relative one**, which looks like a
weakened bound and is not. scikit-learn's `tol` is a gradient tolerance where the Newton routine's
is a coefficient-step tolerance, so on the fifty-event rising regime of the synthetic hazard panel
— a near-flat likelihood — the two land 2.8e-6 apart on a coefficient near zero, which is 9.1e-4
in relative terms. A relative bound would be asserting that a shallow optimum has a sharp one's
properties. Rejected alternative: running the test on the falling regime only, which would leave
the regime where the estimator matters most untested.

**What the converged fit exposed is the more interesting half.** On the clean synthetic hazard
control, `burnout`'s rising-regime coefficient goes from −0.0008 to −0.0943, crosses
`threshold.R1.sign_flip_coef` of 0.05, disagrees in sign with the falling regime, and raises `R1`
on a control D-047 fixes at exactly `{}`. Its standard error is **0.290** on fifty events for ten
features; its **z is −0.32**. The under-converged fit had been suppressing the finding by pinning a
coefficient near zero rather than by getting its sign right — an accident, not an argument. So
`R1`'s sign-flip arm now asks two questions instead of one: `|coef| > threshold.R1.sign_flip_coef`
(materiality, unchanged at 0.05) **and** `|coef / s.e.| >= threshold.R1.sign_flip_z` (precision,
new, 2.0), in **every** regime. The standard errors come from each regime fit's own observed
information, `(X'WX)^-1` with `W = mu(1 - mu)`, which is the matrix
`stats.calibration_slope_intercept`'s Newton step already forms — factored out as
`stats.logistic_standard_errors` and tested against the 2x2 table's closed form
`sqrt(1/a + 1/b + 1/c + 1/d)`, so the number a report cites has arithmetic behind it and not
another routine.

Three alternatives were rejected. **Re-baselining the control to `{R1 medium}`** would publish, as
the hazard control's baseline, a finding whose entire evidence is a coefficient indistinguishable
from zero — and the study's headline false-alarm rate would then rest on it. **Replacing the
absolute gate with the z gate alone** fails the mirror-image case: a precisely estimated 0.001 is
not a regime effect either, and on a large enough panel every arbitrarily small disagreement
clears two standard errors. **Reverting the estimator** keeps the control clean by means of a fit
that did not finish. Materiality and precision are different questions, and a rule that asks only
one of them decides findings by sample size.

The order matters more than usual here and is recorded in D-164 in so many words: the tightening
was decided on **2026-09-09**, in the Phase 12 pre-flight list, for the collateral `R1`s that
`msr__L2__contamination` and `msr__S1__vintage_shift` raise on `burnout` and `sato`. What
2026-09-16 changed is only *when* it ships. A reader who finds a detector rule tightened on the
day a control failed will assume the reverse order, and the defence against that is not a clean
result but a dated record of the decision that preceded it.

One smaller choice. A feature that does not vary inside a regime — every feature of a package whose
regime column is one of its own features — has no coefficient there to estimate, so its `se` and
`z` cells are **empty** rather than a large finite stand-in on the pattern of `VIF_CAP`. Printing a
precision for a parameter the data never identified is worse than printing nothing, and an empty
cell cannot clear the precision gate, which is the right answer. A regime whose *varying* features
still leave the information matrix singular is refused by name: that one is a real degeneracy and
regularising it away would be inventing the number the whole rule depends on.

## Phase 12 pre-flight — Two rules the machinery cannot check, and an open item that is minted

Three bullets were added to `DRAFT_INSTRUCTION` and one of them is not like the other two. **A
quantity goes in digits with its citation** is enforced once it is obeyed: a number in digits is
tokenized as a claim and is either cited and matched or counted against the report, and "roughly
half", "twice" and "six times" are precisely the quantities that escape both. **Do not do
arithmetic** and **say which comparison you are making** are enforced by nothing, and the
docstring under `DRAFT_INSTRUCTION` was rewritten to say so rather than left to read as though
every rule in the prompt had a checker behind it. A cited number that happens to be the quotient
of two others is indistinguishable, downstream, from a number read off an artifact; and whether a
paragraph concluded that two populations are alike is a judgement about a sentence, not about any
number in it. The rejected alternative was to drop the two rules for being uncheckable, which
leaves the drafting failures they answer — a derived "roughly six times", and two absolute gaps of
0.009 and 0.008 read as alike where the ratios are 3.8x and 1.5x — with nowhere to be answered.
The place to answer a drafting failure is the drafting instruction, and the honest thing is to
label it.

**Open items are minted by a rule with one home.** `quaestor.findings.open_items` reads three
families a tool already stored against a bound that tool already stored — a sub-population's
`auc_gap` and `share` against `threshold.O1.slice_auc_gap` and `threshold.O1.slice_min_share`, the
`sign_check.*` triple, and `leakage.overlap.features` between `threshold.L2.overlap` and
`threshold.L2.overlap.features_effective` — and section 6 is handed the list rather than told what
kind of thing might qualify. It lives in `findings.py` because an open item is a sibling of a
finding and that module is the one both the report drafter and `eval/score.py` can import; the two
threshold modules are imported inside the functions that need them, because `quaestor.tools`
imports `findings` for `FindingCandidate` and a module-level import is a cycle. Measured on the
committed real-MSR run: the rule mints the run's own three sub-populations, by name, and three
sign disagreements — `orig_ltv`, `sato`, `season_sin` — that the run's store records and its
section 6 never mentions, on a coefficient sign that is one of D-096's own two examples.

Three alternatives were rejected. **Writing the minted list into `findings.json`** as an
`open_items` block beside `findings` is a report-schema change after Phase 1, which `CLAUDE.md`
makes a stop-and-ask, and nothing needs it: `eval/score.py` imports the same function and re-reads
the store. **Promoting an open item to an `info` finding** is D-096's own rejected alternative and
would put a helpful observation in the study's precision denominator. **Leaving the examples in
the brief and adding the sign check to them** is the shape D-156 and D-165 already removed twice:
a section told what might qualify decides for itself, and the excerpt run is the measurement of
what it decides. Section 6 is no longer given the bounded loop's steps either — a material step
reached it as a follow-up block and now reaches it as one of the minted items, so the list is one
object and not two. The slice rule the loop asked for is joined onto the item it produced, on the
artifacts they share, because the store knows a sub-population by an artifact stem and the drafter
is forbidden to write a logical name in the prose; guessing the expression back out of the slug
would be wrong on any column whose own name ends in `_low`.

## Phase 12 commit D — The chunk, the two ceilings, and a scorer that refuses three things

The study is 62 paid runs and about eleven hours of model time in nineteen sittings (D-180), and
the object the harness is built around is therefore the **chunk** — one invocation of `quaestor
study run` — and not the study. Resumability is a **ledger** rewritten after every cell rather
than a scan of the output tree: `ledger.json` records, per `(variant, configuration)` cell, the
status, the attempt count, the cost, the wall clock, both grounding figures, the finding classes
and the checks that did not run, and the next chunk skips whatever is `done`. The rejected
alternative was to infer resumption from the presence of a `report.md`, which cannot tell a cell
that finished from a cell whose directory was half written when the sitting was killed — and
D-174's sitting *was* killed — and which has nowhere to put the cost the cell actually incurred,
the number that prices the next one.

**`--max-cost` is two ceilings and both are load-bearing.** Before a cell starts, its estimate is
compared with what is left and a cell that does not fit does not start; before every model call,
the ceiling is checked against what has been spent. Only the first makes a chunk end on a cell
boundary rather than stranding a half-paid run, and only the second is the circuit breaker D-179
asks for — a ceiling read between runs cannot see the one run that doubles its own drafting bill
through a pair of re-asks, which is measured at 16.2% of a run. The estimate is D-179's measured
table until the ledger has a completed cell of the same configuration and subject, and that cell's
own cost afterwards. Two alternatives were rejected: **a per-study ceiling**, which is the one
D-179 shows cannot stop a runaway run; and **Probatio's `--max-cost`**, which on probatio 0.1.0
sees about half the spend and is read at session end, so it reports and does not stop (D-149).
A completion whose `cost_usd` is `None` under a ceiling is an error rather than a free call, which
is `quaestor.llm.base`'s own sentence about why the field is not `0.0` enforced where it matters.

**The exit code is not the answer, twice over.** A chunk that stopped on its ceiling exits `0`
exactly as one that finished the study does, so `remaining` in `ledger.json` is what a driver
reads; and a cell that reported without one of its checks is `done` with a non-empty
`checks_failed`, which is D-177's rule carried from one run to a study of them.

`eval/score.py` reads `findings.json`, `claims.json`, `trace.jsonl` and `artifacts/index.json` and
never `report.md`, and it **refuses three things rather than guessing them**. It refuses to score a
variant whose seeded class's check did not run, because that scores a crash as a miss — read off
the trace's own `tool_call` error and not off Appendix D, since the appendix is prose. It refuses
to count false alarms on a control whose baseline the taxonomy records as `null`, because `null` is
"not yet measured" and scoring against it publishes every one of that control's findings as a false
alarm. And it refuses to judge a collateral pairing nobody decided in advance: `docs/STUDY.md` §5
held five, and anything else is recorded `unjudged` and counted in neither half of precision until
a dated judgement exists. The rejected alternative to all three is a default — score it as a miss,
treat `null` as empty, call an unforeseen collateral finding spurious — and each default is a
number nobody decided arriving in a published table.

**The procedure then ran, which is the point of it.** The eighteen free `rules_only` directories
surfaced exactly one unjudged pairing — a seeded MSR `S1` also raising `C1` — and it was judged a
true consequence and written in as §5's sixth rule: `train_pre_test_post` fits the hazard through
2019 and tests it on the 2020–21 refinancing wave, which is the same mechanism D-161 measured on
the *real* MSR control and recorded there as a true finding, and a mechanism cannot be true on a
real panel and spurious on a synthetic one built to carry it. So every rule now carries the **date
it was decided**, five reading 2026-09-09 and one 2026-09-17, and `summary.json` carries both: a
reader can tell a rule fixed before the runs from one written after the numbers were seen without
being told, which is the property the in-advance list was protecting and the only one a
scoring-time judgement can threaten.

The perturbed controls are scored against **their own** taxonomy rows and not against the clean
control's, while a seeded variant is scored against the clean control's: a seeded variant asks what
the subject does with nothing planted in it, and a perturbed control asks what the perturbation
does. Their synthetic baselines — `{E1 low}` and `{}` — are now written in, so the false-alarm
denominator is four controls and not two; the two agree with their clean controls today, which is
what "harmless" is supposed to mean, and keying every baseline by subject alone would give a silent
wrong answer on the day a perturbation stops being harmless.

Scored with both in: 14/14 detected, four controls, 0 false alarms, 0 collateral spurious, 0
unjudged, precision 1.0000, and the scorer exits 0.

**`study build --data` is the flag, the pass-through and nothing else.** A recipe is the same patch
in both data modes because every one of them hangs off the seam after the subject has chosen where
its rows come from, or only edits `package.yaml`; so `--data` changes what `SEED.yaml` records and
hands the directory to `load_package`, which verifies the declared manifest at build time rather
than at the third hour of a paid sitting. The four recipes that need a *column* the real sample
does not carry are skipped by name with their reason. The alternative — writing the four CSV
transforms now — is the cut list's cut 3, and building them into the commit that cannot run them
is how a Phase 12 session discovers at the shell that five variants do not build.

## Phase 12 — A diagnostic is not a citation

The renderer refuses a report carrying a double-bracket token that is not a well-formed citation,
and a resolver's dangling message quotes the token that failed so that the repair loop can hand it
straight back to the drafter. Those two rules are each right on their own and together they cost a
paid cell: the message becomes `Repair.instruction`, Appendix A prints it in the repairs table, and
`check_structure` reads the whole report. **The report was refused for faithfully quoting its own
verifier.** It is only reachable when a repair round *succeeds* — a flagged claim the round cannot
pair with a replacement is dropped and writes no row — so the first cell in the study to rewrite a
claim was the first to hit it.

So a malformed token is named in `⟪…⟫` rather than in its brackets, with a clause saying that this
is a quoted diagnostic, and a well-formed one is still named verbatim because that is the form the
drafter is being asked to recognise. The predicate is the renderer's own, factored out as
`schema.is_report_citation` and shared by the structural check, the repair loop's
`malformed_citations` and the resolver, because three expressions of one grammar are three chances
to disagree about the same bytes.

Two alternatives were rejected. **Neutralising double-bracket tokens in every markdown table cell**
changes the renderer for all of its output to fix one column, and leaves the bad token being
manufactured. **Scoping the structural check past the repairs table** puts a hole in the check
exactly where a genuinely bad citation would next show up, and would hide it.

D-189 refused to sanitise a malformed token in the renderer, and that refusal deliberately does not
carry over here: **in prose the token is an evidence chain**, and a report whose citations resolve
to nothing is the one thing this project must not emit, so quietly repairing one hides the failure
the whole verifier exists to surface. A diagnostic quoted in an appendix is a sentence *about* a
citation that failed — nothing resolves it and nothing is grounded on it — so re-quoting it removes
no guarantee. The shapes are the same and the arguments are not.

## `quaestor study score`: the command, and the two documents it writes

`eval/score.py` was finished before it had an entry point in the program that spec §3.14 names it
a command of, and for one phase the only way to reach it was `python eval/score.py` from a
checkout. Phase 12 gives it `quaestor study score`, built exactly as `study build` and `study run`
are: the module is loaded from beside the `--taxonomy` it was given (D-127), the flags are spelled
as the other two actions spell them, and the failures are the same ones — a taxonomy that is not
there, a module that is not beside it, a directory that holds no run.

Three things about the module's interface did not fit a `study` action and the command moved
rather than the module. **`--variants` is required** although spec §3.14 writes the command as
`--results DIR` alone: a study directory records which variants ran and not where their answer
keys are, and `SEED.yaml` is a file no pipeline code may open, so guessing `eval/variants` would
score a tree against whichever keys that directory holds today. **`--out` is a directory here and
stays a file in `eval/score.py`**, whose `--out` has meant "write `summary.json` to this path"
since the eighteen free `rules_only` directories were scored with it; the action writes two
documents and its `--out` defaults to `--results`, which is spec §8's own layout. And **the exit
code is the scorer's**: `1` means the scoring left a person something to do and says so with both
documents already written, where `1` elsewhere in `cli.py` means the command produced nothing. A
miss exits `0`, because a miss is a result the study publishes.

`report.md` is new and lives in `eval/score.py` beside the numbers rather than in `cli.py`. The
CLI reaches the scorer through `importlib`, so every attribute of it is untyped to
`mypy --strict`; a table-builder written against `Any` would be the one untyped corner of the
shipped package, and it would put the study's tables in a second place from the file that computes
them. The document carries `04` §4's four tables — the headline (rows the defect class; columns
the seeded n and each configuration's detections), the controls, the grounding figures, the miss
list — and two more that are the scorer's own: the collateral verdicts each with the date it was
decided, and **what was not scored and why**, which is D-182's three refusals written where a
reader will meet them. A study whose claim is that its misses are published cannot leave the
refusals in a JSON file nobody opens.

The miss list's "said instead" column is every finding the missed run raised, class and severity,
**including those below `medium`**: a seeded class raised `low` is the near miss a reader most
wants to see. It is the one figure in `report.md` that `summary.json` does not carry, and it is
read from `findings.json`, not from the report — the report's path is printed, never its text,
which is the rule the whole file is built on.

Two alternatives were rejected. **Rebuilding an `argv` and calling `score.py`'s own `main()`**,
which makes the CLI a string formatter for a second parser and throws away the run directories and
answer keys a report has to be rendered from. **Putting the "said instead" column into
`summary.json`**, which changes a schema D-182 fixed, and which the free sweep's eighteen
directories were scored under, to carry a string only a reader of the prose report needs.
