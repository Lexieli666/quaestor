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
