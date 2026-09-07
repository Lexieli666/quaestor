# DECISIONS.md — judgement calls made without asking, numbered and dated

Each entry is a `Q / A / Why`. The rule from `CLAUDE.md`: stop and ask only for a new runtime
dependency, a Python-floor change, a change to `package.yaml` or the report schema after Phase 1,
or anything that would call a live model or download data from a test. Everything else is decided
here and recorded.

## D-001. `pypdf`, `build` and `twine` as development-only dependencies

- **Date:** 2026-09-06 (Phase 0)
- **Q:** `pypdf`, `build` and `twine` are not in `CLAUDE.md`'s dev list. May they be added?
- **A:** Add all three as dev-only dependencies. `pypdf` is used only by the dev-time corpus
  ingest script (spec §3.8), never at runtime.
- **Why:** Spec §3.8 requires `pypdf` at ingest; `build` and `twine` are release tooling. None of
  the three touches the runtime dependency list, which stays exactly `pydantic>=2`, `PyYAML>=6`,
  `numpy`, `pandas`, `scikit-learn>=1.4`, `jsonschema>=4`. Rejected alternative: shipping `pypdf`
  as a runtime extra, which would invite a code path that parses a PDF during validation and put
  the corpus's provenance inside a user's run rather than inside a committed JSONL file.

## D-002. Distribution name `quaestor-mrm`, import name `quaestor`

- **Date:** 2026-09-06 (Phase 0)
- **Q:** What distribution name goes on PyPI, given that spec §2 prefers `quaestor` if it is free?
- **A:** `quaestor-mrm`. The import name stays `quaestor`, so every example, docstring and
  `import quaestor` line in the spec is unaffected.
- **Why:** PyPI `quaestor` is taken by an unrelated project (0.6.3, 2025-08-07); brief §8 names
  the fallback. Decided by the user in the Phase 0 prompt; recorded here because spec §2 leaves
  the name conditional. The name check was not re-run over the network from this session: the
  prompt supplies the answer, and the runbook's `pip index versions quaestor` is a human step.
  Rejected alternative: renaming the import package to match a free distribution name, which
  would contradict `CLAUDE.md`'s "import path `quaestor`".

## D-003. `LICENSE` is committed although `CLAUDE.md`'s root listing does not name it

- **Date:** 2026-09-06 (Phase 0)
- **Q:** `CLAUDE.md`'s repository layout lists the root files and `LICENSE` is not among them, but
  the project is MIT. Commit the licence text or not?
- **A:** Commit `LICENSE` (MIT, Yichen Li, 2026) and declare it with
  `license = "MIT"` plus `license-files = ["LICENSE"]`.
- **Why:** MIT requires its notice to travel with the distribution, so an MIT project without the
  text is not actually MIT-licensed for anyone who installs it. The layout in `CLAUDE.md` names
  the documents a reader navigates by, not the complete file list. Rejected alternative: the
  SPDX expression alone with no file, which under PEP 639 produces a wheel whose stated licence
  has no accompanying notice.

## D-004. Ruff's `D` rules apply to `src/` only

- **Date:** 2026-09-06 (Phase 0)
- **Q:** Spec §2 asks for ruff rules `E, F, I, B, UP, N, D` with "`D` on public API". The gate runs
  `ruff check src tests eval subjects`. Where does `D` apply?
- **A:** `D` is selected globally and ignored per-file for `tests/**`, `eval/**`, `subjects/**` and
  `examples/**`. `E, F, I, B, UP, N` apply everywhere.
- **Why:** "On public API" means the shipped package. Requiring a docstring on every pytest
  function, on every seeded-variant recipe and on every line of a subject's `code/run.py` would
  add noise to the directories that are read as prose examples, and `examples/golden_report/` is
  frozen after Phase 1, so a later docstring-rule change there would be unfixable without a
  sanctioned edit. Rejected alternative: a `src/**`-scoped `select`, which ruff expresses less
  directly than a per-file ignore and which would silently stop applying if a module moved.

## D-005. The sdist ships the package and its documents, not the suite

- **Date:** 2026-09-06 (Phase 0)
- **Q:** What goes into the source distribution?
- **A:** `src/quaestor`, `README.md`, `CHANGELOG.md`, `LICENSE`, `pyproject.toml`. `tests/`,
  `eval/`, `subjects/` and `examples/` are excluded.
- **Why:** The suite is inseparable from `subjects/`, `examples/golden_report/`,
  `eval/results/published/` and this repository's git history — gate condition 5 diffs a directory
  against its introducing commit — so a test tree extracted from an sdist does not collect and
  would read as a broken suite. The auditable source is the tagged repository, and the README says
  so. Rejected alternative: shipping everything, which makes `pip download` pull committed study
  results and subject datasets that only make sense in place.

## D-006. Gate condition 5 is a guard in CI, not a duplicate check

- **Date:** 2026-09-06 (Phase 0)
- **Q:** `CLAUDE.md`'s gate condition 5 (golden report byte-identical to its introducing commit;
  `quaestor validate --synthetic --llm fake` schema-valid on both subjects) has no subject and no
  golden directory in Phase 0. What does CI do?
- **A:** A step that fails if `examples/golden_report/report.md` exists while
  `tests/test_golden_spec.py` does not, and otherwise prints that there is nothing to check. From
  Phase 1 the real check lives in `tests/test_golden_spec.py` and therefore runs inside gate 1.
- **Why:** The condition must be visible in `ci.yml` from the first commit so that it cannot be
  forgotten, but duplicating it as shell would give two implementations that can disagree. The
  guard catches the one failure mode a missing implementation has: the golden directory appearing
  without the test that pins it, which would let gate 5 pass vacuously. Rejected alternative:
  omitting the step until Phase 1, which loses the reminder exactly where a reader looks for the
  six conditions.

## D-007. Gate condition 6 is guarded on `tests/probatio/` existing

- **Date:** 2026-09-06 (Phase 0)
- **Q:** `pytest tests/probatio --cassette=replay` cannot run before Phase 11. Skip it, allow it to
  fail, or guard it?
- **A:** Guard it on the directory's existence, and do not create `tests/probatio/` in Phase 0.
- **Why:** `pytest` on a missing path exits with a usage error and on an empty directory exits
  with "no tests collected"; either would make CI red for a phase that has not happened, and
  `continue-on-error` would leave the step green-ish forever, including after Phase 11 when it
  must be able to fail. A `.gitkeep` in `tests/probatio/` would trip the guard immediately, which
  is why that one directory of the layout is left uncreated. Rejected alternative: `--exitfirst`
  with an ignored exit code, which cannot distinguish "not built yet" from "the tapes are stale".

## D-008. Empty layout directories are tracked with an annotated `.gitkeep`

- **Date:** 2026-09-06 (Phase 0)
- **Q:** Git does not track empty directories, but `CLAUDE.md`'s layout names several that Phase 0
  cannot fill (`subjects/*/code/`, `eval/results/published/`, `examples/golden_report/`).
- **A:** Each gets a two-line `.gitkeep` naming why it is there and saying to delete it when the
  owning phase fills the directory. Directories under `src/quaestor/` get a real package
  `__init__.py` with a docstring naming the phase and spec section that fills it instead, and
  `tests/test_scaffold.py` imports every one of them.
- **Why:** The layout is the shared map between `CLAUDE.md`, the spec and every later session; a
  directory that exists only in prose gets created twice in two places with two spellings. A
  docstring under `src/` is strictly better than a `.gitkeep` because it is also the thing a
  reader of the package sees, and because the import test then fails if one is deleted. Rejected
  alternative: creating directories lazily per phase, which was how the layout drifted in an
  earlier project.

## D-009. Local interpreter Python 3.13, CI on 3.11 and 3.12

- **Date:** 2026-09-06 (Phase 0)
- **Q:** The development virtualenv is Python 3.13.5 while spec §2 fixes the CI matrix at 3.11 and
  3.12 and the floor at `>=3.11`. Is that a conflict?
- **A:** No. The floor stays `>=3.11`, `mypy` and `ruff` are pinned to `python_version = "3.11"`
  and `target-version = "py311"` so that local runs type-check and lint against the floor, and CI
  is what proves 3.11 and 3.12 actually pass.
- **Why:** Linting against the floor locally is what stops a 3.12-only syntax or a 3.13-only
  standard-library name from reaching CI; running the local suite on the newest interpreter is
  free coverage of the top of the supported range. A Python-floor change would be a stop-and-ask,
  and none is proposed. Rejected alternative: rebuilding the virtualenv on 3.11 to match CI
  exactly, which hides forward-compatibility breaks until a user reports one.
- **Amended 2026-09-07 (before the first push):** the answer above is withdrawn. The virtualenv
  was rebuilt on Python 3.12.14, inside the CI matrix. Reason: every live run this project
  publishes (Phase 9 validations, the Phase 12 study, the recorded cassettes) executes in this
  local virtualenv, and the published numbers must come from an interpreter CI exercises.
  Forward-compatibility with 3.13 is not a goal of v0.1. Adding 3.13 to the CI matrix was
  rejected because it changes spec §2 for a version nothing in the project has verified.

## D-010. `py.typed` is shipped

- **Date:** 2026-09-06 (Phase 0)
- **Q:** `CLAUDE.md` requires `mypy --strict` to pass on `src/quaestor` but does not mention a
  `py.typed` marker.
- **A:** Ship `src/quaestor/py.typed`, and claim `Typing :: Typed` in the classifiers.
- **Why:** Without the marker, PEP 561 says a type checker must ignore the annotations of an
  installed `quaestor`, so the strictness the gate enforces would be invisible to anyone importing
  the package — including the eval scripts, if they are ever type-checked from outside the source
  tree. Rejected alternative: no marker, which makes the `Typing :: Typed` classifier false.
