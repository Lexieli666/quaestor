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
