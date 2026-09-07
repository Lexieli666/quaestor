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
