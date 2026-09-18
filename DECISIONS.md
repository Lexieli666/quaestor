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

## D-011. Sanctioned edits to `examples/golden_report/`, and the order they are made in

- **Date:** 2026-09-07 (Phase 1, decided in Cowork)
- **Q:** `CLAUDE.md`'s gate condition 5 requires `examples/golden_report/` to be byte-identical to
  its introducing commit "except the sanctioned edits recorded in `DECISIONS.md`". How is a
  sanctioned edit actually made, and how does a test tell one from an accident, without calling
  `git`?
- **A:** `examples/golden_report/MANIFEST.json` holds the `sha256` of each of the six specification
  files (`report.md`, `claims.json`, `findings.json`, `REPORT_SCHEMA.json`, `CLAIMS_SCHEMA.json`,
  `FINDINGS_SCHEMA.json`), and this entry pins the `sha256` of `MANIFEST.json` itself.
  `tests/test_golden_spec.py` checks both links (checks 10 and 11) and **fails, rather than skips,
  when this entry or its pin is missing**. A sanctioned edit is made in this order: compute the new
  manifest, commit the `DECISIONS.md` entry and the new row of the table below **first**, then
  commit the changed files. The pin therefore always states what the bytes must satisfy, never what
  they happen to be.
  - **Pinned hash:** `MANIFEST.json` has sha256
    `40a9a75ffbed3cce3d50f226f79f84b0e21873f2326ba6383fb0ac4d6bc73116`

  | date | `MANIFEST.json` `sha256` | reason |
  |---|---|---|
  | 2026-09-07 | `1f7df2f39df557dc4b8e39d46e36dbefef4a8f15889c8546b06054c8c8c76c80` | Phase 1: the golden report set is introduced (the Cowork draft of 2026-09-07, copied byte-for-byte) together with the two schemas written for it |
  | 2026-09-07 | `40a9a75ffbed3cce3d50f226f79f84b0e21873f2326ba6383fb0ac4d6bc73116` | Phase 6: regulatory citation pattern widened from `(SR11-7|OCC2011-12)` to `(SR11-7|SR26-2)` after SR 26-2 superseded SR 11-7 (D-055). One character range in `REPORT_SCHEMA.json`; no other byte of the directory changes, and every `[[reg:...]]` citation the golden report already carries still matches |

- **Why:** Gate condition 5 as written is a `git diff` against a commit nobody records, which means
  in practice nobody runs it. Two hash links turn it into an ordinary test: the manifest catches a
  changed file, and the pin in this file catches a changed manifest, so the only way to edit the
  directory is to write down why. Putting the decision before the bytes is what makes the record
  trustworthy — an entry written afterwards is a description of what happened, and the suite is red
  in the interval, which is exactly when someone notices. `MANIFEST.json` is not in its own file
  list, and `README.md` is not either: the manifest pins the specification, not the prose about it,
  so the directory's README can be improved without a decision entry. Rejected alternative: a CI
  step running `git diff --exit-code <introducing-sha> -- examples/golden_report/`, which needs
  full history, breaks on a shallow clone, cannot express "sanctioned", and is invisible to
  `pytest -q` on a laptop.

## D-012. Grammar additions to spec §3.9–3.11

- **Date:** 2026-09-07 (Phase 1, decided in Cowork)
- **Q:** The claim grammar and the report front matter of `02-SPEC.md` §3.9–3.11 name fields in
  prose without listing them all. Which fields does Quaestor actually persist?
- **A:** The fields below, all recorded in `docs/REPORT_SCHEMA.md` §10 and enforced by
  `examples/golden_report/CLAIMS_SCHEMA.json` and `FINDINGS_SCHEMA.json`:
  - `Claim.rounding` (spec §0 allows a claim to declare its own rounding but gives the field no
    home), `Claim.id` (`stable_hash([section, text, value])`, so the repair loop, the trace and the
    `repairs` list can all name one claim), `Claim.source` ∈ {`report`, `developer`}.
  - `VerifiedClaim` = `Claim` + `status`, `artifact_value`, `tolerance`. Spec §3.10 names the five
    statuses and says the artifact value is recorded; it does not name the object that carries them,
    nor the applied tolerance, without which a reader cannot see why 0.74 verified against 0.7412.
  - Front matter gains `schema_version`, `quaestor_version`, `model_type`, `run_id`, `data_mode`,
    `synthetic_n` and `n_claims`. A persisted file carries its schema version, as `trace.jsonl`
    already does; the report must be joinable to its trace and must say out loud when it ran on
    synthetic data; and the two grounding precisions are uninterpretable without their denominator.
  - `claims.json` keeps both `pre_repair` and `post_repair` claim lists, so the pre-repair precision
    is recomputable rather than remembered.
  - `findings.json` carries `candidates_not_promoted` and `checks_without_candidates` beside
    `findings`, so the study's miss list can say what the report did instead of raising the seeded
    class from structured data rather than from prose.
  - `Finding` gains `suggested_severity`, `severity_reason`, `tool` and `candidates_merged`. Spec
    §3.9 lets the agent re-severitise and merge candidates; the record of what it did needs fields.
  - A `comparison` of `delta` or `ratio` is cited by **two adjacent `[[art:…]]` tokens**, in order:
    the claimed value is `second − first` for `delta` and `second ÷ first` for `ratio`. Spec §3.10
    defines the comparison kinds but not how one sentence cites both operands.
- **Why:** Every item is a field the spec's own prose implies and does not list, so writing them
  down now is what lets Phase 7 and Phase 8 be implementations rather than re-designs; the golden
  report is the proof that the set is sufficient to render a whole report and its four appendices.
  Rejected alternative: leaving each field to the phase that needs it, which is how a report format
  ends up with three spellings of the same idea and a schema that has to be relaxed to admit them.

## D-013. Renderer blocks and the `[[table:…]]` directive

- **Date:** 2026-09-07 (Phase 1, decided in Cowork)
- **Q:** A calibration table and a decile table are ten rows of four columns each. If the drafter
  writes them, every cell is a number that needs its own citation. Who writes a table artifact into
  the report?
- **A:** The renderer. The drafter writes `[[table:<logical_name>]]` on a line of its own and the
  renderer replaces the directive with the artifact's caption, the table's own citation and its
  rows, inside a `<!-- quaestor:renderer:begin table <logical_name> --> … <!-- quaestor:renderer:end
  -->` block. A required `scope` block of the same kind carries the front page's summary line.
  Everything inside a renderer block, and the scope block entirely, is excluded from claim
  extraction and from the grounding denominator: no LLM produced it, so there is nothing to verify.
- **Why:** See `docs/DESIGN.md`, Phase 1, for the rejected alternative (the drafter writes the
  tables): 80 of the golden report's 172 candidate numbers would be table cells, and the headline
  grounding precision would then be a measurement of an LLM's ability to transcribe a ten-row table
  rather than of whether its prose is grounded.

## D-014. Tolerances made precise per unit

- **Date:** 2026-09-07 (Phase 1, decided in Cowork)
- **Q:** Spec §0 gives three tolerance defaults — 0.005 for quantities in [0, 1], 0.5 for
  percentages written 0–100, 1% relative otherwise — but not the mapping from a claim's `unit` to
  the default that applies.
- **A:** `count` → absolute 0.5, so integers match exactly. `ratio` or `percent` whose artifact
  value is in the unit interval → absolute 0.005, applied **after** percent → ratio normalisation.
  `percent` on a 0–100 scale → absolute 0.5. Everything else → relative 1%. A `rounding` declaration
  widens the applied tolerance to `max(default, 0.5 · 10^-rounding)` and can never narrow it. The
  applied value is persisted on every `VerifiedClaim` as `tolerance`.
- **Why:** "3,500 rows" is either right or wrong, so a 1% relative tolerance on a count (±35 rows)
  would verify a claim that is simply false; that is the one place the spec's default is too loose,
  and tightening it is safe because no count is ever approximate. Normalising percent to ratio
  before comparing is what lets "22.0%" verify against an artifact of 0.22 without a second
  tolerance regime. Rounding may only widen because a drafter that writes fewer decimals is being
  honest, while one that writes more must still be right. Rejected alternative: a single relative
  tolerance everywhere, which is both too loose on counts and meaningless on a value near zero, such
  as a PSI of 0.014 or a calibration intercept of −0.021.

## D-015. What the extraction pre-pass excludes, and why inline code is a loophole

- **Date:** 2026-09-07 (Phase 1, decided in Cowork)
- **Q:** Spec §3.10 excludes "numbers that are dates, section numbers, or citation hashes" by an
  allow-list of patterns. What exactly is the list, and where is it auditable?
- **A:** Six classes: section and finding numbering (`1.`, `§6`, `F-001`); regulatory section ids
  (`V.1.c`, `IV.1`); the eight hex characters inside an artifact citation; the package version
  string from the front matter; anything inside inline code (`` `bill_mean_6m` ``); and everything
  inside a renderer block (D-013). Each class is listed with examples in `claims.json` `exclusions`
  and its count is printed in Appendix A. The Phase 11 Probatio grounding judge is told explicitly
  that a number hidden in backticks is a failure of the draft.
- **Why:** Every exclusion lowers the grounding denominator, so an unaudited exclusion list is a way
  to make the headline number look better; printing the list with examples is what keeps the figure
  honest, and it is the same argument as the regex pre-pass that stops the extractor lowering the
  denominator by omission. Inline code is the one class that a drafter could genuinely abuse — a
  number in backticks reads as prose but is excluded — so it is not left to the deterministic layer
  alone: the judge sees it as a defect. Rejected alternative: no inline-code exclusion at all, which
  would turn every legitimate mention of `bill_mean_6m`, `V.1.c` or a `%.10g` format string into an
  unattributed claim and make the denominator noise.

## D-016. Developer claims are evaluated only under `--data`

- **Date:** 2026-09-07 (Phase 1, decided in Cowork)
- **Q:** `package.yaml` `claims:` are developer-declared numbers about the **real** fit, and spec
  §3.2 says they are "verified like report claims". What happens under `--synthetic`?
- **A:** They are not evaluated. Under `--synthetic` each is listed in Appendix D as not evaluated,
  and `claims.json` `developer_claims` entries carry `status: not_evaluated`; under `--data` each
  becomes an ordinary `VerifiedClaim` with `source: developer`, and a `mismatch` is the claim channel
  of a `T1` finding. One status value, no branch in the schema.
- **Why:** A synthetic AUC drawn from a generating process has nothing to do with the AUC the
  developer declared for the real sample, so comparing them would manufacture either a false `T1`
  finding or a meaningless pass, and the seeded-defect study measures `T1` detection. Rejected
  alternative: a separate synthetic-mode schema, or a `claims:` block per data mode in
  `package.yaml`, either of which duplicates the developer's declaration and lets the two copies
  drift. See `docs/DESIGN.md`, Phase 1.

## D-017. The synthetic credit generator carries one interaction and one near-collinear pair

- **Date:** 2026-09-07 (Phase 1, decided in Cowork)
- **Q:** The synthetic `credit_default` subject is the clean control that every test, the demo and
  CI run against. Should its generating process be a plain additive logistic model?
- **A:** No. It carries exactly two deliberate structures: one interaction term
  (`utilisation × delinq_last`), which the additive logistic champion cannot represent, and one
  near-collinear pair (`bill_last`, `bill_mean_6m`), which the subject's own VIF screen is expected
  to resolve by removing one of the two. **Consequence, binding on Phase 3 and Phase 8: the clean
  synthetic credit subject is expected to yield exactly one finding, `E1` at severity `low`, and the
  end-to-end test asserts that exact finding set, not an empty one.** Also decided here: `features`
  entries in `package.yaml` may carry an optional `note` string, which `PackageSpec` accepts in
  Phase 2.
- **Why:** A clean subject that produces no finding at all cannot exercise the `Finding` object, the
  severity path, section 6 of the report or the evidence rule, and a pipeline whose finding path is
  only ever exercised by seeded variants is a pipeline whose finding path is untested where it
  matters. The interaction makes the boosted challenger legitimately better by more than the 0.03
  effective-challenge threshold, which is a true statement about the champion's functional form
  rather than a defect — exactly the shape of an `E1`. The collinear pair does the same job for the
  VIF screen without raising `M1`, since the screen removes the feature before fitting. An
  end-to-end assertion of "no findings" would also be the weakest possible test: it passes when the
  tools silently fail to run. Rejected alternative: a purely additive generator plus a seeded
  variant to exercise the finding path, which defers the whole of section 6 to Phase 10. The `note`
  field exists because the near-collinearity and the interaction have to be documented where a
  reader of the package meets the features, not only in `synthetic.py`.

## D-018. Where `CLAIMS_SCHEMA.json` and `FINDINGS_SCHEMA.json` go beyond `GRAMMAR.md`

- **Date:** 2026-09-07 (Phase 1)
- **Q:** The two new schemas must encode `docs/REPORT_SCHEMA.md` §6–8 exactly, with closed enums and
  closed objects, and the golden `claims.json` and `findings.json` must validate against them
  unchanged. Three points are not settled by §6–8 alone.
- **A:** (a) `Claim.comparison` is **not** nullable: spec §3.10 writes its type as
  `{"eq","delta","ratio"} | None`, but the grammar makes `eq` the explicit default and the golden
  uses it on all 90 non-delta claims, so the enum is the three values and a plain equality claim says
  so. (b) `claims.json` may carry an optional `developer_claims_note` string, which the golden uses
  to say why `developer_claims` is empty; §7 does not list it. (c) Objects are closed with
  `unevaluatedProperties: false` over an `allOf` of `$defs/claim_core` and `$defs/verdict` rather
  than with `additionalProperties: false` repeated on each variant, so `Claim`, `VerifiedClaim` and
  the developer variant share one definition of the eleven `Claim` fields.
- **Why:** (a) A nullable `comparison` gives two spellings of "this number equals its artifact", and
  the matcher would have to treat them identically — a distinction with no consequence is a bug
  waiting for someone to branch on it. (b) The note is human-facing provenance for an empty list, and
  Appendix D renders it; a null-or-absent key is cheaper than a synthetic `not_evaluated` entry per
  declared claim in a mode where nothing was evaluated. (c) `additionalProperties: false` cannot be
  combined with `allOf` composition in JSON Schema — the base's `additionalProperties` rejects the
  subclass's own keys — so the literal reading of "additionalProperties false" would force the eleven
  `Claim` fields to be written out three times, which is exactly the drift the schema exists to
  prevent; `unevaluatedProperties: false` is the 2020-12 keyword for the same closure and is
  enforced by `jsonschema>=4`. Rejected alternative for (c): three fully written-out object schemas,
  which is what the phrase says and what a later reader would have to keep in sync by hand.

## D-019. Floats are hashed by `repr` and stored by `%.10g`

- **Date:** 2026-09-07 (Phase 2)
- **Q:** Spec §0 says every persisted identity is a `stable_hash` of canonical JSON; spec §3.4 says
  artifact payload bytes use "fixed float formatting `%.10g`". Does `stable_hash` also round to ten
  significant digits?
- **A:** No. `canonical_json` serialises a float with Python's `repr`, which since 3.1 is the
  shortest string that round-trips to the same double and is therefore both fixed and lossless.
  `%.10g` is applied by `quaestor.artifacts` on the way *into* the store, before the bytes are
  hashed, so an artifact's hash is the hash of its rounded payload and two runs that agree to ten
  significant digits are one artifact.
- **Why:** The two formats answer different questions. An artifact is rounded once so that
  `0.3333333333333333` computed on one machine and `0.3333333333` read back from a CSV on another
  are the same evidence; a hash must never conflate two values that differ, because it is also the
  identity of a claim, a cassette key and a tool's argument set. Rounding inside `stable_hash` would
  make `stable_hash({"tol": 1e-12})` equal `stable_hash({"tol": 0})`. Rejected alternative: `%.10g`
  everywhere, which buys nothing — the rounding that matters already happened at `put` — and makes
  the hash lossy for every non-artifact use.

## D-020. Trace events carry their type-specific fields in a `payload` dict, flattened on disk

- **Date:** 2026-09-07 (Phase 2)
- **Q:** Spec §3.1 writes a trace line as `ts, run_id, type, ...`, so the type-specific fields are
  top level in the JSON. How are they typed in memory under `mypy --strict`?
- **A:** `TraceEvent` has the four envelope fields plus `payload: dict[str, Any]`. `to_line()`
  writes the payload's keys at the top level, and `from_record()` folds every non-envelope key back
  into it. A payload key that collides with an envelope key is a `QuaestorError` at emit time.
- **Why:** The alternative, `model_config = ConfigDict(extra="allow")`, puts the fields on the model
  where they belong conceptually and where the type checker has never heard of them: every
  `event.tokens_in` in `eval/score.py` is then an `attr-defined` error or an untyped `getattr`. A
  model per event type was the other option and was rejected because six models with one shared
  envelope is where a trace format acquires two spellings of `duration`; the field names that the
  study actually counts are pinned instead by `TraceWriter.llm_call`, which is a typed method.
  Nothing about the file on disk changes either way, which is the part the spec fixes.

## D-021. A candidate may have no evidence only when its `tool` is `load_package`

- **Date:** 2026-09-07 (Phase 2)
- **Q:** `CLAUDE.md` says a finding requires evidence and spec §3.9 types `FindingCandidate.evidence`
  as non-empty, but spec §3.2 requires a `timing: after_outcome` feature to yield an `L1` candidate
  *before anything runs*, when no artifact exists. How is the exemption expressed?
- **A:** `findings.PRE_RUN_TOOL = "load_package"`. A `FindingCandidate` validator rejects empty
  evidence unless `tool == PRE_RUN_TOOL`. `check_leakage` attaches the `leakage.timing` artifact when
  it promotes the candidate in Phase 7, so no *finding* ever lacks evidence.
- **Why:** The exemption has to exist, so the only question is whether it is checkable. A boolean
  `pre_run` flag would be settable by any caller and would drift into meaning "evidence optional".
  Keying it to a `tool` value that no tool has means the exemption is visible in `findings.json`, is
  scoped to one producer, and fails loudly the day a real tool tries to use it. Rejected
  alternative: dropping the non-empty rule and checking evidence only at `Finding` construction,
  which would let a tool emit evidence-free candidates all through Phase 5 with nothing to catch it
  until Phase 7.

## D-022. The data manifest is verified only when a data directory is given; `code/` is required

- **Date:** 2026-09-07 (Phase 2)
- **Q:** Spec §3.2 says `data.manifest` is "optional; verified if present", but `load_package(path)`
  is given a package directory and the data lives wherever `--data DIR` points. Verified against
  what, under `--synthetic`?
- **A:** `load_package(path, *, data_dir=None)`. With a `data_dir`, every digest in the manifest is
  verified and a mismatch is a `PackageError` naming the file, both digests and `shasum -a 256`.
  With none — which is what `--synthetic` passes — the manifest is not verified, and the report
  says so in Appendix D, as the golden report already does. Also decided here: a package directory
  without `code/` is a `PackageError`, because `entrypoint` would have nothing to import.
- **Why:** A manifest is a statement about specific files, and in synthetic mode those files are not
  read at all: verifying them would either fail on a machine that never downloaded the data or, if
  the loader went looking inside the package directory, would silently verify nothing. Making the
  data directory an explicit argument keeps the check honest in both modes and keeps `--synthetic`
  from needing a special case. Rejected alternative: resolving manifest paths relative to the
  package directory, which is where nobody's data lives and which would make the check pass
  vacuously on every real package.

## D-023. The artifact address covers the logical name, and a name cannot be re-pointed

- **Date:** 2026-09-07 (Phase 2)
- **Q:** Spec §3.4 calls the store content-addressed. Is the address a function of the payload
  alone?
- **A:** No: the hash is `stable_hash({"kind", "name", "payload_sha256"})`, so the logical name is
  part of the identity. Storing the same payload under the same name twice is idempotent; storing a
  *different* payload under a name that is already taken is an `ArtifactError`.
- **Why:** Under pure value addressing, `metrics.train.event_rate` and `metrics.test.event_rate`
  collapse into one artifact whenever the two splits happen to have the same event rate — which for
  a stratified split is the normal case, and is exactly what the golden report shows (0.22 on both).
  A finding's evidence list could then no longer say which split it rested on, Appendix B would list
  one hash under two names, and the citation rule "`logical_name` is in its index entry" would have
  to admit a set. Refusing to re-point a name follows from the same idea: prose already written
  against the old hash would silently stop resolving, and a dangling citation that used to resolve
  is the one failure the verifier cannot distinguish from a drafting error. Rejected alternative:
  pure value addressing with a name-to-hash index allowing many-to-one, which saves a few kilobytes
  of duplicated scalars and costs the evidence rule its precision.

## D-024. `LLMProviderError`, additive to the spec §3.1 hierarchy

- **Date:** 2026-09-07 (Phase 2)
- **Q:** Spec §3.1 lists `LLMOutputError` for the LLM layer. A provider that cannot be reached — no
  executable, a timeout, a non-zero exit, an error payload — has not produced a bad answer; it has
  produced no answer. Which error is that?
- **A:** A new `LLMProviderError(QuaestorError)`, kept strictly separate from `LLMOutputError`, which
  means "the model answered and the answer is unusable" and which carries the raw text.
- **Why:** The study retries transport failures and records bad answers, and `eval/run_study.py` is
  resumable: one exception type for both would mean either retrying a prompt the model reliably
  fails at, inflating the re-ask count, or abandoning a variant because the laptop's network
  blinked. The rest of the hierarchy stays closed. Rejected alternative: reusing `LLMOutputError`
  with a flag, which is a type distinction written as data and would have to be branched on in
  three places.

## D-025. The exact flag list `ClaudeCLILLM` passes, and why each one is there

- **Date:** 2026-09-07 (Phase 2; the `--bare` default corrected the same day after Cowork review)
- **Q:** Spec §3.5 requires the CLI adapter's flags to be read from `claude --help` and recorded
  here. Which flags, in which order, which were deliberately not used, and does the default vector
  run on the login this project actually has?
- **A:** Six flags by default, all present in `notes/claude-help.txt`, emitted in this order (the
  vector is asserted verbatim in `tests/test_llm.py`):

  ```
  claude -p <prompt> --output-format json --no-session-persistence --strict-mcp-config \
         [--model <m>] [--system-prompt <s>] --tools ""
  ```

  | flag | why |
  |---|---|
  | `-p <prompt>` | Non-interactive print mode; the prompt is the positional argument. Without it the CLI opens a session. |
  | `--output-format json` | The parser needs `result`, `usage`, `total_cost_usd` and `duration_api_ms`; `text` gives none of them, so a trace could not record tokens or cost. |
  | `--no-session-persistence` | A validation run is not a conversation; nothing should be resumable, and nothing should accumulate in the session store across a 200-variant study. |
  | `--strict-mcp-config` | Restricts MCP servers to those named by `--mcp-config`, of which this adapter passes none — so no MCP server configured on the operator's machine is loaded, and a validation call cannot reach out through one. |
  | `--model <m>` | Passed only when a model is configured, so that the study can name the model it is measuring. |
  | `--system-prompt <s>` | Passed only when the caller has one. Replaces the default system prompt rather than appending to it, which is what a section-drafting instruction wants. |
  | `--tools ""` | Disables every built-in tool. Placed **last**, because the flag is variadic and anything after it would be parsed as another tool name. With no tools the CLI cannot take a second turn, which is how "one turn" is obtained on a version that has no `--max-turns`. |

  **`--bare` is not in the default vector.** `claude --help` states that under `--bare` "Anthropic
  auth is strictly `ANTHROPIC_API_KEY` or `apiKeyHelper` via `--settings` (OAuth and keychain are
  never read)". `CLAUDE.md` forbids an API key anywhere in this project and the runbook's live
  runs are made on a subscription login, so a default that passes `--bare` is a default that
  cannot run at all. It is an opt-in for an operator who does have a key:
  `ClaudeCLILLM(bare_flag="--bare")`. Every call, with or without it, still runs in a **fresh empty
  temporary working directory**, which is what excludes project context and project `CLAUDE.md`
  discovery.

  Whether `--bare` was passed is recorded on `Completion.raw` as `quaestor_bare` and copied onto
  every `llm_call` trace event by `structured()`, so a published run states which of the two
  configurations produced it rather than leaving a reader to assume.

  Deliberately **not** used: `--json-schema` (see `docs/DESIGN.md`, Phase 2 — validation stays
  provider-agnostic in `structured()`, so the re-ask count means the same thing under both
  adapters); `--dangerously-skip-permissions` and `--allow-dangerously-skip-permissions` (nothing
  needs permission once tools are off); `--add-dir`, `--mcp-config`, `--agents`, `--settings`,
  `--plugin-dir` (every one of them adds context the prompt did not ask for); `--max-budget-usd`
  (the study enforces its own ceiling from the trace, across providers); `--continue`, `--resume`,
  `--fork-session` (no session exists); `--effort`, `--fallback-model`, `--permission-mode` (each
  would make two runs differ in a way the trace does not record).

  Every flag is a constructor argument, so a user whose CLI version has renamed one overrides that
  argument rather than waiting for a release.
- **Why:** The first draft of this entry had `--bare` on by default, on the reasoning that the most
  hermetic context is the most reproducible one. That was wrong in the way that matters: the
  adapter exists precisely so that a developer *without* an API key can run Quaestor live, and
  `--bare` turns off the authentication path such a developer has. A default that fails on the only
  supported login is not a strict default, it is a broken one. What `--bare` would additionally
  have suppressed — hooks, plugins, auto-memory, user-level `CLAUDE.md` — is real residual context
  and is named as a limitation in `docs/DESIGN.md`, Phase 2, rather than pretended away; the empty
  working directory removes the project-scoped part of it, `--strict-mcp-config` removes the MCP
  part, and the trace field says which regime the run used so that two runs are never silently
  compared across it. Rejected alternative: keeping `--bare` on and telling operators to export an
  API key, which contradicts `CLAUDE.md`'s "No API keys anywhere" and would make the published
  study unreproducible by anyone who follows that rule.

## D-026. The list-element key accepts `feature` then `name`, and `run.features` is an object

- **Date:** 2026-09-07 (Phase 3)
- **Q:** The golden report writes `[[art:8b373477:run.features#n]]`, but `features.json` is a list
  in spec §3.3 and a list has no `n`. And `docs/REPORT_SCHEMA.md` §5 addresses a list element by its
  `feature` value, which is the label in `model_summary.json`; the elements of `features.json`
  label themselves `name`. What resolves what?
- **A:** Two changes, both narrow. (a) The artifact the sandbox stores under `run.features` is
  `{"n": <count>, <timing>: <count> for each of the four timings, "items": [<the list as written>]}`.
  The file on disk stays exactly the list spec §3.3 fixes; the transformation happens in
  `quaestor.sandbox.contract.features_artifact` on the way into the store. (b) `citations.py`
  addresses a list element by its `feature` value and, failing that, by its `name`; the error
  message names both keys. The parenthetical in `docs/REPORT_SCHEMA.md` §5 is amended to say so,
  which is a documentation correction and not a schema change: no field, enum or pattern moves, and
  every citation in `examples/golden_report/` resolves before and after.
- **Why:** The golden report is the executable specification, so a citation it writes has to be
  resolvable by construction — `run.features#n` failing would mean either the golden was wrong from
  the start or the store's shape was. Storing counts rather than computing them at citation time is
  what keeps path resolution structural: a resolver that could count list elements would be a
  resolver that computes, and the next request would be a sum. All four timings are stored, zeros
  included, because "no feature is declared `after_outcome`" is a sentence a report should be able
  to cite rather than assert. Rejected alternative: making `features.json` an object on disk, which
  would put the store's convenience into the contract that two subjects and every seeded variant
  have to write, and would contradict spec §3.3 as written.

## D-027. `xlrd` is not a dependency, so `sample.py` accepts two input forms

- **Date:** 2026-09-07 (Phase 3)
- **Q:** The UCI *Default of Credit Card Clients* distribution is a legacy `.xls`, which pandas can
  only read through `xlrd`. `CLAUDE.md` fixes the runtime dependencies and a new one is a
  stop-and-ask. Add `xlrd`, or not?
- **A:** Not. `subjects/credit_default/sample.py` reads either
  `default of credit card clients.xls` — only when `xlrd` happens to be importable in the
  operator's environment — or `default_of_credit_card_clients.csv`, which is what the operator
  exports once from a spreadsheet. With neither present the message names both file names and the
  dataset id; with only the `.xls` and no `xlrd`, the message is the one-off export instruction.
  `xlrd_available()` is a function so a test can pin both branches without installing anything.
- **Why:** `xlrd` would be a dependency of one script that runs once per machine, is never executed
  by a test, and is not needed at all by anyone who exports a CSV — and a runtime dependency added
  for that is a dependency every user of the library installs. A dev-only dependency was the other
  option and is worse than useless: the script is not run in CI, so the dev environment is exactly
  where it would never be used. Rejected alternative: `openpyxl`, which does not read the legacy
  `.xls` format at all and would have produced a confusing failure instead of an instruction.

## D-028. The memory cap is unenforced off Linux, recorded, and never fails a run

- **Date:** 2026-09-07 (Phase 3)
- **Q:** Spec §3.6 caps the subject's memory with `resource.setrlimit(RLIMIT_AS)` in a
  `preexec_fn`, "on platforms without it, record `memory_cap: unenforced`". macOS *has*
  `RLIMIT_AS` and does not reliably enforce it. Set it anyway?
- **A:** No. `quaestor.sandbox.memory_cap_policy(platform)` returns `enforced` only on Linux, and
  `unenforced` everywhere else including macOS; the limit is set only in the first case. Either way
  the answer is recorded on `RunResult.memory_cap`, on the `run.status` artifact, on the run's
  `tool_call` trace event and in the report's Appendix C, and a run is never failed because a cap
  could not be applied — the `setrlimit` call inside the child swallows its own failure.
  `subjects/../code/` is capped in practice by the container path of `sandbox/Dockerfile`, whose
  `--memory` is a kernel limit and holds on every host.
- **Why:** The macOS kernel does not fail an `mmap` of address space a process never touches, and
  numpy's BLAS reserves far more address space than it commits, so the limit as actually
  implemented stops nothing — while a limit that *were* honoured at 4,096 MB would kill a healthy
  5,000-row fit. A cap whose effect depends on which machine ran the validation is worse than no
  cap, because Appendix C would print "enforced (RLIMIT_AS 4096 MB)" and a reader would believe it.
  Recording `unenforced` is the honest version of the same line. Rejected alternatives: setting the
  limit everywhere and treating a kill as an `R0` finding, which manufactures a defect out of a
  platform difference; and `RLIMIT_DATA`, which on macOS bounds only the legacy heap and on Linux
  no longer bounds `mmap` at all, so it means two different things.

## D-029. What the sandbox copies, and where the subject's own modules live

- **Date:** 2026-09-07 (Phase 3)
- **Q:** Spec §3.6 says the subprocess's `cwd` is "a temp copy of `code/`" and spec §3.2 fixes the
  entrypoint as `python -m code.run`. Those two cannot both be literally true: if the working
  directory *is* the copy of `code/`, there is no package named `code` on `sys.path` and
  `python -m code.run` does not import. And spec §4 lists `synthetic.py` beside `code/`, where the
  sandbox would not copy it, so a subject could not draw its own synthetic panel.
- **A:** The working tree is a fresh temporary directory holding a copy of `code/` at `<work>/code`,
  with `cwd = <work>` and `HOME = <work>/home`; the copy is removed when the run ends. The
  generating process lives at `subjects/credit_default/code/synthetic.py`, so it travels with the
  copy, and `subjects/credit_default/synthetic.py` is the file spec §4 and `CLAUDE.md` name: a
  human-facing CLI that re-exports `SyntheticProcess`, `generate` and `engineer` and carries the
  loader that imports out of `code/` under an alias. `sample.py` does not use that loader; it loads
  `code/features.py` from its path directly, so that the second subject's `synthetic.py` (Phase 4)
  cannot collide with the first's.
- **Why:** The entrypoint is the part of the spec a user writes in their own `package.yaml`, so it
  is the part that must work as written; "a temp copy of `code/`" is satisfied by a tree whose only
  content is that copy. The subject is then genuinely self-contained: nothing outside `code/` is
  visible to it, which is what makes "the subject cannot read its own `package.yaml`, its `docs/`,
  or the validator" a property of the sandbox rather than a convention. Rejected alternatives:
  copying the whole package directory, which hands the subject the developer documentation the
  drafter is supposed to quote and any committed artifacts, and would make an "unexpected output"
  check ambiguous about which directory it is about; and putting `code/` on `PYTHONPATH` with
  `cwd` inside it, which leaves the subject's imports depending on an environment variable the
  spec's own scrub list does not promise.

## D-030. Under `--data` the split is read, not re-drawn

- **Date:** 2026-09-07 (Phase 3)
- **Q:** `code/run.py` draws a stratified 70/30 split by client identifier at the declared seed.
  `sample.py` writes `train.csv` and `test.csv`, whose digests `package.yaml`'s `data.manifest`
  pins. Does the `--data` path re-draw the split from the concatenated sample?
- **A:** No. `sample.py` draws the split once, with the same `stratified_split` at the same declared
  seed, and the two files *are* the split; `run.py --data DIR` reads them as the train and test
  splits and refuses a sample whose two identifier sets overlap. `--synthetic N` draws the split
  itself, from the same function.
- **Why:** The manifest is the reproducibility mechanism for the real fit, and it can only pin
  bytes — so whatever the two files contain has to be what the model was fitted on. Re-drawing the
  split inside `run.py` would give a run whose splits depended on the seed *and* on the row order
  of a concatenation, and a manifest that verified files whose contents no longer determined the
  fit. Reading the split also keeps `sample.py` honest about being the documented sample rule
  rather than half of it. Rejected alternative: one `sample.csv` plus a split drawn at run time,
  which would have needed `package.yaml`'s `data.manifest` to change after Phase 1 — a
  stop-and-ask — and would have made the real fit unverifiable from digests alone.

## D-031. The VIF screen removes the last-declared offender, not the worst

- **Date:** 2026-09-07 (Phase 3)
- **Q:** The screen must leave every retained feature at or below a VIF of 10. Which feature leaves
  each round?
- **A:** The **last declared** of the features whose VIF exceeds the threshold, one per round, until
  none does. `package.yaml`'s feature order is the developer's own order.
- **Why:** Near-duplicate features come in pairs whose two VIFs are equal up to the noise in their
  construction: on the clean synthetic panel `utilisation` is 49.2 and `utilisation_mean_6m` is
  50.1. A rule that removes the larger therefore decides which of the two survives on a fourth
  decimal, so a different seed — or a Phase 10 recipe that perturbs an unrelated parameter — would
  silently swap which feature the champion is fitted on and which coefficient the report discusses.
  Declaration order is stable across every seed and is visible in the package a reader is holding.
  Rejected alternative: removing the maximum-VIF feature, which is the textbook rule and is
  reproducible only for a fixed dataset, not across the study's variants.

## D-032. A contract CSV may name its identifier `id` or the column `package.yaml` declares

- **Date:** 2026-09-07 (Phase 3)
- **Q:** Spec §3.3 writes the first column of `predictions_<split>.csv` as `id`. Both shipped
  subjects declare `data.id_column` (`client_id`, `loan_id`) and write that instead, which is what
  makes the file joinable to `data_<split>.csv`. Reject it?
- **A:** No: `read_contract` accepts either spelling, and the error message names both when neither
  is present.
- **Why:** A subject that writes the identifier its own package declares is saying the same thing
  more usefully, and the alternative is a contract that forces every subject to rename its key
  column on the way out and every tool to rename it back. Accepting exactly two spellings — the
  spec's and the declared one — is bounded, and neither is a guess. Rejected alternative: insisting
  on `id`, which would make the leakage screen's overlap check join two files on a column whose
  name no longer says what it holds.

## D-033. A failed run raises, after storing the evidence an `R0` finding will need

- **Date:** 2026-09-07 (Phase 3)
- **Q:** Spec §3.6 says a subject that outruns its cap is "killed and reported", and that a missing
  or malformed contract file is a `SandboxError`. Spec §3.7 says the `run_model` tool raises an
  `R0` candidate when the run fails — and a candidate needs evidence hashes that exist in the
  store. Does `run_model` return a failed `RunResult` or raise?
- **A:** It raises `SandboxError`, and before raising it stores `run.stdout`, `run.stderr`,
  `run.duration_s` and `run.status` (`returncode`, `timed_out`, `memory_cap`, both caps, the data
  mode and the seed) and emits the run's `tool_call` trace event with `ok: false`. The Phase 5 tool
  therefore catches one exception type and builds an evidenced `R0` from artifacts it can look up
  by name. Two related choices: each captured stream is truncated at 64 KiB with a marker naming
  what was dropped; and an unexpected file is described by a `run.unexpected.<path>` JSON artifact
  carrying its relative path, its byte count, its SHA-256 and its text when it decodes, rather than
  having its bytes copied into the store.
- **Why:** A `RunResult` with an `ok` flag is a result every caller has to remember to check, and
  the one that forgets proceeds to read contract files that are not there; an exception cannot be
  forgotten. Storing the evidence first is what keeps `CLAUDE.md`'s evidence rule intact for the one
  finding class that describes a run that produced nothing. The stream cap exists because a subject
  that prints a megabyte per row would otherwise put its log in the report's artifact index, and the
  marker exists because a silently truncated log reads as a complete one. An unexpected file is
  described rather than copied because the store's four kinds are a scalar, a table, a JSON object
  and a figure, and arbitrary bytes are none of them — while the file itself is still where the
  subject wrote it. Rejected alternative: a `figure`-kind artifact holding whatever the subject
  wrote, which would make the kind a lie the moment the file was not a PNG.

## D-034. The champion is fitted on standardised features and reports standardised coefficients

- **Date:** 2026-09-07 (Phase 3)
- **Q:** `model_summary.json` carries `coefficients: [{feature, value}]`, and the golden report
  calls them "standardised coefficients" and compares their magnitudes. The twelve features range
  from a utilisation ratio near 1 to a credit limit near 10^5. On which scale?
- **A:** The champion is a `Pipeline` of `StandardScaler` and `LogisticRegression`
  (`class_weight=None`, `lbfgs`, `max_iter=1000`), and `model_summary.json` reports the
  coefficients on the standardised scale, with `"standardised": true` beside them.
  `data_<split>.csv` is written in the original units, because a drift or collinearity screen has
  to report a PSI or a VIF a reader can compare against the developer's own monitoring.
- **Why:** A sentence like "the three largest coefficients are on `delinq_last`, `utilisation` and
  `delinq_count_6m`" is meaningless on raw coefficients, where the ranking is a statement about
  units; it is exactly what a validator wants to read on standardised ones. Standardising also
  gives `lbfgs` a conditioned problem, so the fit is reproducible rather than
  convergence-tolerance-dependent. Rejected alternative: raw coefficients plus a note about units,
  which pushes the comparison onto the reader and makes the report's own ranking unciteable.

## D-035. `condition_number` means Belsley's kappa, which the clean synthetic panel passes

- **Date:** 2026-09-07 (Phase 3)
- **Q:** Spec §3.7 stores `condition_number` and raises `M1` above 30, without defining it. On the
  clean synthetic panel's ten retained features the ratio of the correlation matrix's extreme
  eigenvalues is 30.8 and the ratio of the design matrix's extreme singular values is 5.55. The
  first would raise `M1` on the clean control and break D-017; the second would not.
- **A:** `condition_number` is Belsley's condition number: the ratio of the largest to the smallest
  **singular value** of the column-standardised design matrix, equivalently the square root of the
  eigenvalue ratio of the correlation matrix. On the clean synthetic panel it is **5.55**. This
  binds Phase 5: `check_collinearity` implements that definition, and the threshold of 30 is
  Belsley's own rule of thumb, which is stated for that quantity.
- **Why:** The number and the threshold have to come from the same source, and 30 is the textbook
  cut-off for the singular-value ratio; pairing it with the eigenvalue ratio compares a quantity
  with the square of the threshold it was meant for, which is how a clean model acquires a
  collinearity finding. Deciding it here rather than in Phase 5 is deliberate: the alternative is
  discovering in Phase 8 that the clean control yields two findings instead of the one D-017
  fixes, and then choosing the definition that makes the test pass — which is the same arithmetic
  arrived at in the order that cannot be trusted. Rejected alternative: raising the threshold to
  100 for the eigenvalue ratio, which is the same rule wearing a number no source states.

## D-036. What the clean synthetic panel actually contains, measured

- **Date:** 2026-09-07 (Phase 3)
- **Q:** D-017 fixes the two deliberate structures of the synthetic `credit_default` panel. What do
  they come out as, and does anything in the realisation contradict the golden report?
- **A:** At the declared seed 20260901 and `--synthetic 5000`: event rate 0.2246; the screen removes
  **two** features, `bill_last` (VIF 160.9) and then `utilisation_mean_6m` (VIF 36.4), leaving ten
  whose worst VIF is 7.30; champion test AUC 0.7480, Brier 0.1489, calibration slope 0.997,
  train-minus-test AUC gap 0.0104; the largest single-feature AUC is 0.693; the worst train-to-test
  PSI is 0.0102; a default `HistGradientBoostingClassifier` on the retained features scores 0.8240,
  a challenger-minus-champion gap of **+0.0760** against the `E1` threshold of 0.03. The
  interaction is a **reversal**, not a mere curvature: `beta_utilisation = 4.6` and
  `beta_interaction = -5.4`, so a high balance predicts default for a client who is current and
  predicts it less for one already past due — the past-due client with almost no balance is the one
  who has stopped using the card. Two consequences for the golden report, which is **not** edited:
  its "the screen removed one feature, the eleven retained" and its `challenger.delta_auc` of
  0.0323 are illustrative, as its front matter says, and nothing compares them to a run.
- **Why:** The two near-collinear pairs are unavoidable rather than chosen: `utilisation` is
  `bill_last / limit_bal` and `utilisation_mean_6m` is `bill_mean_6m / limit_bal`, so making the
  statement path persistent enough for the second pair to be collinear makes the first pair
  collinear too. `package.yaml`'s own note says the screen "is expected to remove one of the pair",
  which it does, once per pair. The reversal was chosen after measuring: a saturating interaction of
  the same size left the challenger 0.016 ahead, inside the noise of a hyperparameter choice, and a
  clean control whose only finding depends on the challenger's `max_leaf_nodes` is a control that
  will flake. At +0.076 the `E1` holds under every challenger configuration tried (defaults, and
  two regularised ones), which is what a control has to do. The margin is generous rather than
  tight for the same reason. Rejected alternative: tuning for a gap near the golden's illustrative
  0.0323, which optimises a number that was never a measurement.

## D-037. `ScenariosSpec` gains a servicing fee, a discount rate and a convexity expectation

- **Date:** 2026-09-07 (Phase 4)
- **Q:** Spec §3.2's `scenarios` block carries only `rate_shocks_bp` and `horizon_months`, but
  spec §4.2 requires the projection to report "the servicing value change per shock from a
  declared servicing fee" and §3.7's `X1` fires when the realised sign pattern is "inconsistent
  with declared convexity expectation". Neither declaration exists. May the block be extended
  after Phase 1?
- **A:** Yes, and it was decided in Cowork on 2026-09-07 before this phase began rather than
  taken here: `ScenariosSpec` gains `servicing_fee_bp`, `discount_rate_annual` and
  `convexity_expectation` (a `ConvexityExpectation` of `negative` or `positive`). All three are
  **required**, not defaulted, and the block must include the `0` shock. The hazard fixture
  `tests/fixtures/hazard_package/package.yaml` gains the same three lines.
- **Why:** Spec §4.2 requires a declared servicing fee and `X1` requires a declared convexity
  expectation, so both have to be somewhere a package can say them; `package.yaml` is where a
  developer's declarations live and the alternative -- a threshold in `configs.py` -- would make
  Quaestor's own default the thing the report verified against. Required rather than defaulted for
  the same reason: a rule that silently supplies its own declaration is not checking a
  declaration. The base-case check is there because every `value_change` is stated relative to
  the `0` shock, and a `scenarios` block without it would divide by nothing. Rejected
  alternative: putting the fee and the discount rate in the subject's `code/` alone, which is
  where they in fact also live (D-043) but which no validator may read, so the report would be
  quoting a number no declaration backs. `CLAUDE.md` makes a change to `package.yaml` after Phase
  1 a stop-and-ask; the user's own Phase 4 prompt supplies the answer, and this entry records it.

## D-038. Every raw value the hazard subject reads is a closing value of the month it is labelled with

- **Date:** 2026-09-07 (Phase 4)
- **Q:** Beginning-of-month lagging says a feature at month `t` uses the balance, age and burnout
  at the close of month `t - 1` and "the rate at the start of month `t`". A month-start rate is
  naturally labelled by the month whose start it is -- and then perturbing the raw rate of month
  `t` changes month `t`'s own `incentive`, so the lagging rule has an exception and the leakage
  screen cannot check it. Which labelling wins?
- **A:** The closing one. The market-rate calendar column is `market_rate_close`, and
  `market_rate_close[m]` is the rate at the **close** of month `m`, which is the rate a borrower
  faces at the start of month `m + 1`: no time passes between them. From FRED's weekly
  `MORTGAGE30US` the month-start rate of month `m` is the first observation of month `m` (which
  is the convention spec §4.2 and the Phase 4 prompt fix), and it is stored under month `m - 1`.
  So `incentive` at month `t` reads `market_rate_close[t - 1]` and `rate_change_12m` reads
  `market_rate_close[t - 1] - market_rate_close[t - 13]`, exactly as the balance, the age and the
  burnout read month `t - 1`. One rule, no exceptions.
- **Why:** The rule is what the leakage screen tests, and a rule with an exception is a rule
  nobody can test. A Freddie Mac performance row *is* the closing record of its month -- the
  current actual UPB is a month-end balance, the zero-balance code is what happened during the
  month -- so a market rate carried as a closing value is the only column in the schema that
  agrees with the rest of it. The cost is one line of documentation wherever the calendar is
  built, because a reader who looks up `2020-01` in `rates.csv` sees the print published in the
  first week of `2020-02`. Rejected alternative: labelling the calendar by the month whose start
  the rate stands at, which reads more naturally in isolation and makes `incentive` the one
  feature at month `t` that is a function of a month-`t` raw value -- so the Phase 4 leakage test
  could perturb the balance and the payoff and would have to leave the rate alone, which is the
  one of the three most likely to be lagged wrongly in a real prepayment model.

## D-039. The natural cubic spline basis is written out, not taken from `SplineTransformer`

- **Date:** 2026-09-07 (Phase 4)
- **Q:** Spec §4.2's champion is a "logistic hazard with age splines". scikit-learn ships
  `SplineTransformer`. Why write a basis by hand?
- **A:** `code/features.py` implements the natural cubic spline basis of Hastie, Tibshirani and
  Friedman §5.2.1 in numpy: `N_1 = x` and `N_{k+1} = d_k - d_{K-1}` with
  `d_k(x) = ((x - xi_k)_+^3 - (x - xi_K)_+^3) / (xi_K - xi_k)`, five knots at the 5th, 27.5th,
  50th, 72.5th and 95th percentiles of the fitting split's `loan_age`, rounded to whole months.
  On the clean synthetic panel that is knots at 1, 10, 19, 31 and 53 months and four basis
  columns.
- **Why:** `SplineTransformer` gives a B-spline basis with no natural boundary constraint, so the
  fitted seasoning curve is a free cubic beyond the oldest loan age in the sample. The projection
  runs 180 months forward from a book whose oldest loan is 60 months old, so it evaluates the
  basis far outside the fitting range on every run; an unconstrained cubic there invents a
  prepayment ramp, and the `X1` sign pattern would be reporting an extrapolation artefact. A
  natural spline is linear outside its boundary knots, which is the assumption an MSR projection
  should be making and can be tested (the second difference beyond the boundary is zero).
  `CLAUDE.md`'s "statistics by hand where small" points the same way. Rejected alternative:
  `SplineTransformer` with `extrapolation="linear"`, which is linear in the *transformed* columns
  and not in the fitted function, and still leaves the basis's own boundary behaviour to a keyword
  a reader of the report cannot see.

## D-040. The projection's negative convexity is a property of the process, not a tuned number

- **Date:** 2026-09-07 (Phase 4)
- **Q:** The Phase 4 prompt asks that the base case sit where the incentive response is convex, so
  that the projection's sign pattern is structural. Three things had to be arranged for that, and
  the first attempt got the sign *backwards*. What are they?
- **A:** (1) **The logistic is convex below zero.** The base-case monthly payoff rate is around
  one per cent, a logit near -4.6, and the whole operating range of the hazard is below zero, so
  a parallel fall in rates raises the hazard by more than the same parallel rise lowers it. This
  needs no tuning: it is true of any small logistic hazard. (2) **A turnover floor.**
  `turnover_floor` (0.0008 a month) is the share of borrowers who move whatever rates do, so the
  hazard cannot fall below it and the up-shock's upside is bounded while the down-shock's downside
  is not. (3) **The book must be out of the money at the valuation month.** A late level rise in
  the rate path -- `rate_ramp_pp_per_year` 1.05 for two years from 2022-01, the real 2022-23 move
  -- puts the surviving book 2 points out of the money in 2024-01.
- **Why:** (3) was not foreseen and was found by measuring. Without the ramp every loan still
  alive at the end of the panel carried a large *positive* incentive, the base-case CPR was 24.9%,
  and the down shock could only take a value that was already running off fast to zero while the
  up shock could take it all the way to a fully amortising annuity: value change **+871,718** at
  +300bp against **-488,601** at -300bp, which is positive convexity and the wrong answer for a
  servicing right. The arithmetic behind it: with `V ~ 1 / (delta + h)` for a monthly discount
  `delta` and a monthly hazard `h`, the most the down shock can take is `V(0)` and the most the up
  shock can add is `h_0 / (delta (delta + h_0))`, so `|down| > |up|` needs `h_0 < delta` -- the
  base hazard below the monthly discount rate. A book at or out of the money satisfies it; a book
  deep in the money does not. That is also the textbook statement of when a servicing right is
  negatively convex, so the fix is the economics rather than a fudge. Rejected alternative:
  raising `discount_rate_annual` until the inequality held, which would have made the declared
  discount rate a knob for getting the sign right.
- **Correction, 2026-09-17 (Phase 12 pre-flight):** "puts the surviving book 2 points out of the
  money" in (3) above reads as a **level** and is not one. Two points is the size of the **move**
  the ramp makes. Re-measured offline at the declared seed, the book's mean first-projected-month
  incentive is **+1.288** with `rate_ramp_pp_per_year` at zero and **−0.717** at the declared 1.05
  for two years — a move of **2.005** points, and a resulting level of −0.717, not −2. The
  argument (3) makes is unaffected, because it is about the move and about the sign of the level:
  the book *is* out of the money at the valuation month, which is what `h₀ < δ` needs. The
  sentence above is left as it was recorded; **D-170**'s reconciling paragraph carries the
  measurement, and `docs/DESIGN.md` and `subjects/msr_prepayment/README.md` are rewritten to say
  the move in the same commit.

## D-041. Originations are spread across each cohort year, not concentrated in one month

- **Date:** 2026-09-07 (Phase 4)
- **Q:** Three origination cohorts is what spec §4.2 and the Phase 4 prompt ask for. With all of
  a cohort originating in one month, `loan_age` had a VIF of 242 on the training panel even after
  the collinear balance pair was accounted for. Why?
- **A:** Because calendar time is origination month plus loan age, and with three origination
  months the rate features -- which are deterministic functions of the calendar -- nearly
  determine the pair. Originations are therefore drawn uniformly over the twelve months of each
  cohort year (`origination_months`), as the real Freddie Mac sample files are.
- **Why:** That collinearity is a property of the *sampling design*, not of the model, and a
  clean control that carries an `M1` because its three cohorts share a birthday is measuring the
  generator. Spreading them is also what the real data does, so the synthetic panel and the real
  panel have the same structure. Rejected alternative: raising `rate_noise_sd` to decorrelate the
  calendar, which barely moved the VIFs (12.75 to 11.27 on `note_rate` as the noise tripled) and
  buys the decorrelation with an implausibly jumpy mortgage-rate series.

## D-042. The rate shock is parallel over the whole path, history included

- **Date:** 2026-09-07 (Phase 4)
- **Q:** A shock of -300bp shifts the rate path the projection uses. Does it shift only the months
  after the valuation date, or the twelve months of history `rate_change_12m` also needs?
- **A:** The whole path. `rate_change_12m` is therefore unaffected by the shock, and the shock
  acts entirely through `incentive`.
- **Why:** A rate shock on a servicing right acts through the refinance incentive; that is what
  the shock is for. Shifting only the forward months turns a level shock into a level shock plus a
  one-off twelve-month slope shock that decays over the first year, so the reported convexity
  table would be describing two shocks at once and `X1` would be comparing a compound experiment
  with a declaration about a parallel one. Recorded on the file itself as
  `rate_path_assumption`, so a reader of `projection.json` does not have to infer it. Rejected
  alternative: shocking forward months only, which is arguably the more realistic scenario but is
  not the one `package.yaml` declares (`rate_shocks_bp`, "parallel shocks in basis points").

## D-043. The `scenarios` block is restated in `code/run.py` and reconciled by a test

- **Date:** 2026-09-07 (Phase 4)
- **Q:** `projection.json` needs the shocks, the horizon, the servicing fee, the discount rate and
  the convexity expectation. Those are declarations in `package.yaml`, and spec §3.2 hands the
  subject a data directory and an output directory and no path to the package. Where do they live?
- **A:** In both places. `code/run.py` carries `RATE_SHOCKS_BP`, `HORIZON_MONTHS`,
  `SERVICING_FEE_BP`, `DISCOUNT_RATE_ANNUAL` and `CONVEXITY_EXPECTATION` as module constants, and
  `tests/test_subject_msr_prepayment.py::test_the_subjects_scenario_declarations_match_package_yaml`
  asserts that the five agree with the loaded `package.yaml`. That test is the only place the
  duplication is allowed to be resolved.
- **Why:** A subject is somebody else's code and must not need to know it is being validated;
  giving it a `--package` argument would let a seeded variant's subject read the declaration it is
  supposed to be measured against. Duplicating five numbers and pinning them with a test is the
  cheaper failure mode: the test breaks the moment the two drift. The same argument applies to the
  split rules, which `code/features.py` restates and a second test reconciles. Rejected
  alternative: having `run_model` pass the `scenarios` block through on the command line, which
  makes the sandbox's argument vector depend on the model type and puts a declaration Quaestor is
  verifying inside the process that produces the thing being verified.

## D-044. The synthetic panel has one common observation cut-off, not 60 months per loan

- **Date:** 2026-09-07 (Phase 4)
- **Q:** Spec §4.2 says "2,000 loans x 60 months". Taken literally -- 60 months from each loan's
  own origination -- and with originations spread over each cohort year (D-041), the panel's last
  month is reached only by the loans originated in the youngest cohort's twelfth month, and the
  projection had a servicing book of **26** loans to value.
- **A:** The observation window ends on one calendar month for every loan:
  `observation_end_month` is the month the youngest cohort's *first* loan completes its
  `months_observed`, which is 2024-01 at the declared cohorts, and a loan is observed to the
  earlier of its 60th month and that month. Only the youngest cohort's later originations are
  truncated, by at most eleven months; the projection's book is then the whole surviving 2019
  vintage, **511** loans and about 96.6 million of balance.
- **Why:** A real performance file ends on one reporting month for every loan, so this is the
  shape the real panel has and the synthetic one should have too. And a projection valuing 26
  loans is a projection whose sign pattern is a small-sample statement. Rejected alternative:
  valuing each loan from its own last observed month, which makes "surviving balance by month"
  a sum over loans at different calendar dates under a rate path shocked from different
  starting points -- a table nobody could interpret and `run_scenarios` could not reproduce.

## D-045. The hazard champion runs the same VIF screen as the classification champion

- **Date:** 2026-09-07 (Phase 4)
- **Q:** The Phase 4 prompt's champion is "a logistic hazard with a natural cubic spline basis on
  loan_age plus the other features" and says nothing about a screen. But `bom_balance_log` is
  `orig_upb_log` plus `log(scheduled amortisation factor)`, whose standard deviation over 60
  months of a 360-month loan is about 0.03 against 0.44 for the loan size, so its VIF on the
  training panel is **40,090**. Fitting on both is fitting on a difference of two columns that
  agree to three decimal places.
- **A:** The subject screens the twelve declared features at a VIF of 10 before the spline basis
  is built, removing the last-declared offender per round exactly as the credit subject does
  (D-031), and lists what left in `model_summary.json`'s `removed`. On the clean synthetic panel
  it removes `rate_change_12m` (VIF 12.4) and then `bom_balance_log` (40,090), leaving ten
  features whose worst VIF is **4.98** and whose Belsley condition number is **4.94**.
  `data_<split>.csv` holds the post-screen matrix, as spec §3.3's "the feature matrix actually
  used" requires and as the sibling subject already does.
- **Why:** Without the screen the clean control carries an `M1` on its first run, and the finding
  would be true: the model really is collinear. The collinearity is not a defect the study should
  be scoring, though -- it is the ordinary consequence of a package declaring both the original
  and the current balance, which real prepayment packages do -- and the sibling subject already
  establishes the screen as this project's answer to it. `rate_change_12m` leaving is a cost worth
  naming: it is the column the regime is *defined* from, and the last-declared rule takes it
  because it happens to be declared tenth. The regime itself is unaffected, because
  `regime.column` is `rate_regime`, which `code/features.py` writes into `data_<split>.csv` and
  which was never a model feature. Rejected alternative: removing the worst offender instead of
  the last declared, which would take `bom_balance_log` first and keep `rate_change_12m` -- and
  would put two different removal rules in two subjects of one repository, so a study result
  would depend on which subject a variant came from.

## D-046. The `psi` threshold and `S1` mean train against test; the period splits are reported

- **Date:** 2026-09-07 (Phase 4)
- **Q:** `package.yaml` declares `{metric: psi, features: all, max: 0.25}` without naming a
  comparison, and spec §3.7 has `profile_data` compute PSI "train vs each other split". Measured
  on the clean synthetic panel: train against **test**, the worst feature is `credit_score` at
  **0.065**; train against **out_of_time**, `burnout` is at **3.09** and `loan_age` at 2.41; train
  against **vintage_holdout**, `note_rate` is at **0.62**. Which comparison does the threshold
  govern?
- **A:** Train against test. `profile_data` still computes and stores the other comparisons --
  they are exactly what a reader wants to see about an out-of-time split -- but the `S1` candidate
  and the `T1` breach of a `psi` threshold are raised on the train-to-test comparison only, and
  the report's Appendix D says that the period-based and vintage-based comparisons were reported
  and not tested. This binds Phase 5.
- **Why:** PSI asks whether an expected distribution and an actual one are the same population
  sampled twice. Train and test are; that is what a random 70/30 over loans means. `out_of_time`
  is *defined* as a later period -- `package.yaml`'s own rule calls it "the refinancing wave the
  training window never sees" -- so its loans are older and its rate environment is different by
  construction, and a quantile-binned PSI on `loan_age` between a window of ages 0-59 and a window
  of ages 24-59 puts several bins on the 0.5% floor, each contributing about 0.29 on its own.
  `vintage_holdout` is *defined* as a different origination cohort, so its note rates differ. A
  rule that fires on those is measuring the split design, and it would fire on every hazard
  package anyone ever writes. Deciding it here rather than in Phase 5 is deliberate, for the
  reason D-035 gives: the alternative is discovering in Phase 8 that the clean control yields two
  findings and then choosing the scoping that makes the test pass, which is the same decision
  arrived at in the order that cannot be trusted. Rejected alternative: raising the package's
  threshold to 3.5, which would hide a real drift finding on the one comparison where PSI means
  what it says.
- **Consequence for the study, added 2026-09-07 (Phase 5).** `04-SEEDED-DEFECT-STUDY.md` §2's
  `msr` `S1` recipe is "train on pre-2015 vintages, out-of-time is 2020+ with no monitoring
  split", whose expected signal is "PSI > 0.25 on features or on `y_score`". That signal lands
  entirely on the train-to-**out_of_time** comparison, which this decision reports and does not
  test, so the recipe as written would be seeded and then detected by nothing — a guaranteed miss
  that says something about the recipe rather than about the detector. **The recipe will be
  redesigned or dropped in Phase 10**, and whichever happens is recorded in `docs/STUDY.md`:
  either it becomes a shift between the *train and test* loans (the credit subject's own recipe,
  "train on one segment, score all"), or the `msr` row of the taxonomy loses `S1` and the study
  reports 13 seeded variants rather than 14. It is not fixed by re-scoping `S1`, because the
  scoping was decided on the clean control before any variant existed. Measured through the
  Phase 5 tools, whose binning puts a value exactly on a bin edge into the lower bin: the worst
  train-to-out_of_time feature PSI is **2.945** on `burnout` where D-046's Phase 4 measurement
  read 3.09, and train-to-vintage_holdout `note_rate` is **0.609** where it read 0.62 — the same
  conclusion by a slightly different convention (D-051).

## D-047. What the clean synthetic hazard panel actually contains, measured

- **Date:** 2026-09-07 (Phase 4)
- **Q:** D-017 fixes the classification subject's clean control at exactly one finding, `E1` at
  severity low. What does the hazard subject's clean control come out as?
- **A:** At the declared seed 20260901 and `--synthetic 2000`, through `run_model`: 95,829
  loan-months over 2,000 loans in three cohorts; monthly payoff rate 0.0084 observed against the
  0.0105 the intercept is solved for on the uncensored schedule (censoring removes the fast
  payers' later months); 40.3% of loans pay off inside the window. The screen removes two of
  twelve features (D-045); champion test AUC **0.7753**, Brier 0.0079, calibration slope 0.959
  (**0.937** from 2026-09-16 on: the slope, and only the slope, moves with D-160's unpenalised
  estimator; the fit, the splits and every other number in this entry are untouched);
  train 0.7883, out-of-time 0.7846, vintage holdout 0.7718; largest single-feature AUC 0.724;
  worst retained VIF 4.98 and Belsley kappa 4.94; PSI train-to-test 0.065 (D-046); regime AUCs
  0.7227 falling and 0.7238 rising and no coefficient sign flip; a default
  `HistGradientBoostingClassifier` on the retained features as `data_train.csv` and
  `data_test.csv` carry them scores **0.7337**, a challenger-minus-champion gap of **-0.0415**
  against the `E1` threshold of +0.03 (fitted on the same columns in memory, before the CSVs'
  ten-significant-digit round trip moves the boosted model's bin edges, it scores 0.7269 for a
  gap of -0.0484; the test uses the files, because the tools do). The
  projection values 511 loans and 96.6 million as of 2024-01: value change **-1,297,986** at
  -300bp and **+168,055** at +300bp, monotone across all seven shocks, convexity -1,129,932.
  **So the expectation for Phase 8 is that the clean synthetic `msr_prepayment` yields exactly
  `{}` -- no finding at all -- which is the counterpart of D-017 and is asserted at data level
  here and at pipeline level in Phase 8.**
- **Why:** Two clean controls that behave differently are worth more than two that behave the
  same: the classification subject's champion is misspecified on purpose and must yield `E1`,
  while the hazard subject's champion is the correct functional form for its process and must
  yield nothing, so the study can tell a detector that finds real defects from one that finds
  findings. Three caveats are recorded rather than smoothed over. **The `{}` expectation depends
  on D-046's PSI scoping**; without it the control carries `S1` and `T1` on the out-of-time and
  vintage comparisons. **`R1`'s sign-flip rule is close to the noise** on this subject: at the
  declared seed no retained coefficient flips across regimes, but at four other seeds tried
  (11, 202, 3003, 777) one weak coefficient -- `season_cos`, `season_sin` or `burnout`, all with
  |coef| just above the 0.05 gate -- flips at one seed each, so Phase 8's assertion is a statement
  about seed 20260901 and not about the process. **The fitted `burnout` coefficient is +0.079
  where the process's is -0.18**: burnout is a near-monotone function of loan age, whose effect the
  spline absorbs, so its own coefficient is weakly identified. That is a fact about the fit worth a
  sentence in the report rather than a defect, and it is in the subject's `README.md`. Rejected
  alternative: strengthening `beta_burnout` until the fitted sign matched, which would optimise a
  coefficient nothing depends on and move the base rate the intercept solve is there to hold.
- **Consequence, added 2026-09-16 (Phase 9, the first real MSR sample).** The `{}` expectation
  above holds on the **synthetic** panel and **does not hold on the real one**. The offline
  `--data … --llm fake` validate of the Release 47 panel raises exactly one finding, `C1` at
  medium, on the `out_of_time` and `vintage_holdout` splits: calibration slope 0.432 out-of-time
  against the declared [0.80, 1.20] band, and mean predicted-to-observed gaps of 0.4618 and 0.4932
  against the 0.25 threshold. That is the model under-predicting the 2020-21 refinancing wave by
  about half and not a defect in the rule, so this entry's expectation is now read as a statement
  about the synthetic panel alone. **See D-161**, which generalises it: every control carries a
  measured baseline finding set per data mode, and a baseline finding on a control is not a false
  alarm.
- **Consequence, added 2026-09-16 (Phase 9, the `R1` precision commit).** The converged per-regime
  estimator of D-163 and the precision gate of D-164 land together, and this entry's two `R1`
  sentences both survive them: **the recorded regime AUCs do not move** — 0.7227144937 falling and
  0.7237965727 rising, the same `stability.auc_by_regime` content hash as before, because that arm
  reads the champion's own scores and refits nothing — and **the "no coefficient sign flip" clause
  still holds**, now for a stated reason rather than by accident. Converged, `burnout`'s rising
  coefficient is −0.0943 rather than −0.0008 and does clear the 0.05 materiality gate; it is the
  new precision gate, `|coef / s.e.| >= 2`, that it fails at z = −0.32 on fifty events. This
  entry's own warning — that `R1`'s sign-flip rule sits close to the noise on this subject, with
  one weak coefficient flipping at each of four other seeds tried — is what D-164 acts on.

## D-048. The Freddie Mac layouts are positional, written out, and checked by field count

- **Date:** 2026-09-07 (Phase 4)
- **Q:** `sample_orig_YYYY.txt` and `sample_svcg_YYYY.txt` are pipe-delimited with no header row,
  and Freddie Mac revises the field list between publications. How does `sample_freddie.py` avoid
  silently mapping the wrong column when the layout moves?
- **A:** Both layouts are written out as tuples (`ORIGINATION_LAYOUT`, `PERFORMANCE_LAYOUT`, 32
  fields each, the order the 2024 user guide documents) and the reader compares the file's field
  count with the layout's length, raising a `SystemExit` that names the constant and tells the
  operator to check the current user guide. The origination *month* is not taken from the
  origination file at all -- there is no such field -- but from the performance file as
  `monthly_reporting_period - loan_age`, which is Freddie Mac's own definition of loan age and is
  exact; `first_payment_date` is used only to look SATO's market rate up, two months earlier by
  the usual convention.
- **Why:** A positional map that is wrong is worse than one that fails: `oltv` and `ocltv` are
  adjacent, both are plausible loan-to-value numbers, and a report fitted on the wrong one is
  indistinguishable from a report fitted on the right one. A field count is a weak check and it
  is the only one available without a header, so it is paired with a message that names what to
  read. The test suite covers the map on a three-loan frame it writes itself -- one voluntary
  payoff, one repurchase, one loan six months past due -- because the zero-balance code is the
  only place this project interprets a Freddie Mac code, and a subject that counted a repurchase
  as a prepayment would fit beautifully for a reason no reader could see. Rejected alternative:
  reading the layout from the published Excel file dictionary at run time, which is a download
  inside a data-building step and a second file to keep.
- **Amended 2026-09-15 (Phase 11, before the first real MSR run): the same decision, with a second
  layout to choose between.** The operator's files are **Release 47, July 2026**, whose origination
  file has **31** fields and whose performance file has **35**, against the 32 and 32 this script
  encoded. So both 2024 tuples are kept, two more are written out beside them
  (`ORIGINATION_LAYOUT_2026`, `PERFORMANCE_LAYOUT_2026`), and `_read_pipe_delimited` **selects the
  layout by the field count it counts** -- 32 or 31 for an origination file, 32 or 35 for a
  performance one -- prints the release it read the file as, and raises the same `SystemExit` for
  any other count, now naming both constants and both widths. Nothing else in the sampler changes,
  and the Release 47 tuples keep **this script's own column names** wherever the quantity is
  unchanged: the guide renames field 1 to *Classic FICO*, field 20 to *Loan Identifier*, and nine
  performance fields including *Period* and *Current Non-Interest Bearing UPB*, and adopting those
  spellings here would rename them in `to_raw_panel`, in `code/features.py` and in `package.yaml`
  for a change no reader of the report could see.
  **What the field count cannot answer, measured rather than assumed.** A count says the file is
  one of two shapes; it does not say the fields this script reads are where it left them, and
  `oltv` and `ocltv` are adjacent and both plausible. So `tests/test_msr_sample_freddie.py` asserts
  the **position** of every column read downstream of `read_raw` in both layouts -- origination
  `credit_score`, `first_payment_date`, `orig_upb`, `oltv`, `orig_interest_rate`,
  `loan_sequence_number`, `orig_loan_term`; performance `loan_sequence_number`,
  `monthly_reporting_period`, `current_actual_upb`, `current_loan_delinquency_status`, `loan_age`,
  `remaining_months_to_legal_maturity`, `zero_balance_code`, `zero_balance_effective_date`,
  `current_interest_rate` -- and **every one of them is at the same index in both**. The origination
  columns all fall in positions 1-24, which the two publications share exactly; the performance ones
  all fall in 1-32, where Release 47 changes names and not order. The whole mapping suite is
  parameterised over the two releases, and one test builds the panel through each and asserts the
  two frames are equal.
  **`CENSORING_CODES` against the July 2026 enumeration**, which lists `01`, `02`, `03`, `09`, `15`,
  `16` and `96`. The list here is now a superset of it by three and a subset by none. **`16`
  (Reperforming) is added**, because a reperforming-loan sale is a disposition -- the loan leaves
  the dataset without paying off -- and treating that month as one the loan survived would put a
  competing exit in the hazard's denominator. **`06`, `97` and `98` are kept** although the guide
  no longer lists them, because this script reads the *archived* distributions of the 2014, 2017 and
  2019 vintages, which were published under earlier guides and still carry them; a retired code that
  never appears costs nothing, and a code that appears and is not listed is silently read as a month
  survived, which is the error this whole entry exists to prevent. `VOLUNTARY_PAYOFF_CODE` stays
  `01`. Delinquency status is two characters wide in Release 47 (`00`, `01`, ..., with `RA` and
  `XX`); `_months_past_due` already converts before it compares, so the padded and unpadded forms
  agree, and a test now pins that on the exact tokens the July 2026 files carry -- a status compared
  as a string would make `"06"` differ from `"6"` and censor nothing.
  Rejected alternatives for this amendment: replacing the 2024 tuples rather than keeping both,
  which makes every archived distribution unreadable by a script whose whole job is to read them;
  selecting the layout from a `--release` flag, which asks an operator to know something the file
  already says and fails silently when they get it wrong; and adopting the guide's new field names,
  above.

## D-049. The tool contract: nested `Args`, a frozen context, and thresholds keyed by their names

- **Date:** 2026-09-07 (Phase 5)
- **Q:** Spec §3.7 fixes a tool as "a class with `name`, `description`, `Args` (pydantic), and
  `run(args, ctx)`", says the JSON schemas are "generated from `Args` once and consumed by the
  planner, the MCP server and the CLI", and says the default thresholds live in `configs.py` —
  which arrives in Phase 8, three phases after the tools that need them. Four shapes had to be
  chosen: where the thresholds live, what `ctx` is, how `Args` is typed, and how `mypy --strict`
  sees scikit-learn.
- **A:** (a) The class-default thresholds live in `src/quaestor/tools/thresholds.py` and
  `configs.py` will import them, not restate them. (b) Each threshold's dictionary key *is* its
  logical artifact name — `threshold.M1.vif`, `rule.calibration_first_event_rate` — and
  `Thresholds.artifact(store, key)` is the only way a tool reads one, so a threshold that decided
  a candidate is in the store by construction. An override naming a key that is not a default is
  an error. (c) `ToolContext` is a frozen dataclass of `package`, `store`, `out_dir`, `trace` and
  `thresholds`, not a pydantic model: three of the five fields are objects with behaviour and
  structural validation of them buys nothing. (d) `Tool` is generic in its `Args` type
  (`Tool["ProfileDataTool.Args"]`) with the model itself declared as a nested class, so
  `tool.Args.model_json_schema()` is generated once at registration and `run` is typed against the
  concrete model. (e) `pyproject.toml` gains a `mypy` override making `sklearn.*` an untyped
  import, and *loses* its `python_version = "3.11"` pin, because numpy 2.5 — which requires Python
  3.12 — writes `type` statements in its stubs that mypy refuses to parse when told to assume 3.11;
  CI still checks both versions, on each of which mypy now infers the version it is running under.
- **Why:** A tool module that imported `configs` would make the tool layer depend on the pipeline
  layer, and Phase 8 would then be free to change a threshold without any tool's test noticing.
  Keying the thresholds by their artifact names is what makes spec §12's "thresholds hard-coded in
  prose rather than stored as artifacts" impossible to write here: there is no way to read a
  threshold that does not also name where it is stored. The mypy pin had to go rather than the
  numpy version: pinning numpy below 2.5 would be a runtime dependency change, which is a
  stop-and-ask, to work around a type-checker configuration. Rejected alternative for (d): a
  non-generic `Tool` whose `run` takes a bare `BaseModel` and re-validates inside, which types
  every tool's body as `Any` and makes the planner's schema and the tool's own reading of its
  arguments two separate claims.

## D-050. `O1`'s first rule is read as train minus test, a generalisation gap

- **Date:** 2026-09-07 (Phase 5)
- **Q:** Spec §3.7 states `O1` as "test-minus-train AUC gap > 0.08". Read literally that fires
  when the *test* AUC exceeds the training AUC by 0.08 — a model that generalises better than it
  fits, which is a curiosity rather than a defect and which the threshold's own name,
  `threshold.O1.auc_gap`, does not describe. Which subtraction is meant?
- **A:** Train minus test. `compute_metrics` raises `O1` when the training AUC exceeds the test
  AUC by more than `threshold.O1.auc_gap`, and the candidate's sentence says so in words. The
  golden report settles it: its §4 calls the same quantity "the train-to-test AUC gap" of 0.0126
  against "a generalisation-gap threshold of 0.08", computed as train (0.7538) minus test
  (0.7412), and `examples/golden_report/` is the executable specification of what a report says.
- **Why:** Overfitting is the thing the rule exists to catch, and every seeded-defect recipe that
  targets `O1` produces a model that fits its training split better than its test split. A rule
  read the other way would score zero on every one of them and fire on sampling noise in the
  opposite direction. Recording it rather than silently implementing the sensible reading matters
  because the study's detection numbers are stated per class: a reader who takes `O1`'s definition
  from spec §3.7 and finds a different one in the code deserves to be told which is authoritative
  and why. Rejected alternative: implementing the absolute gap, which would fire on a test split
  that happens to be easier and would make `O1` a test of split luck.

## D-051. PSI bins are closed at the top, so a mass point does not split across the boundary

- **Date:** 2026-09-07 (Phase 5)
- **Q:** PSI cuts the expected sample into ten quantile bins and applies the same edges to the
  actual sample. A feature whose value is zero in most rows has several of its quantile edges at
  exactly zero, which collapse to one edge; on which side of that edge do the zeros fall?
- **A:** Below it. The bins are `(-inf, e1], (e1, e2], ..., (ek, inf)` — a value equal to an edge
  belongs to the bin the edge closes — implemented with `numpy.digitize(..., right=True)`. The
  alternative, `numpy.histogram`'s half-open `[e1, e2)` bins with `-inf` as the first edge, puts
  every zero into the *upper* bin along with everything above it, and a feature that is zero in
  95% of the training rows and 50% of the test rows then scores a PSI of exactly **0**: the two
  samples are reported as identical when one has moved by 45 points. Under the convention adopted
  the same pair scores 1.325, which is what a reader expects. A test asserts both.
- **Why:** Every feature a seeded `D1` or `S1` recipe touches is a candidate for a mass point —
  an imputed zero, a capped ratio, a delinquency count — so the degenerate case is not exotic. The
  change moves the clean panels' numbers in the fourth decimal (`credit_default`'s worst PSI reads
  0.0110 against the 0.0102 of the Phase 3 measurement; `msr_prepayment`'s reads 0.0619 against
  0.065) and moves the out-of-time comparison from 3.09 to 2.945, none of which changes a verdict.
  Rejected alternative: leaving the histogram convention and documenting the zero, which is a
  documented wrong answer.

## D-052. CSI is the coefficient-weighted shift, not a second name for a feature's PSI

- **Date:** 2026-09-07 (Phase 5)
- **Q:** Spec §3.7 has `profile_data` produce both `psi.<feature>` and `csi.<feature>`, and the
  golden report cites `psi.utilisation` at 0.021 and `csi.max` at 0.018 — two different numbers.
  In much of the scorecard literature "PSI" means the shift in the *score* and "CSI" the shift in
  a *characteristic*, which would make `csi.<feature>` an exact copy of `psi.<feature>` here.
  What is the second number?
- **A:** `csi.<feature>` is the shift in the linear predictor attributable to that feature: the
  same bins as its PSI, but the redistribution of mass is weighted by what the feature contributes
  to the fitted log odds in each bin — the champion's coefficient times the bin's mean standardised
  value — and the result is reported as an absolute value in log-odds. A feature the champion does
  not carry a coefficient for, because the design expanded it (the hazard champion's spline on
  `loan_age`) or the screen removed it, contributes zero. Measured on the clean controls: `csi.max`
  is 0.0236 on `credit_default` and 0.0344 on `msr_prepayment`.
- **Why:** Two artifact names that always hold the same number are a reporting bug, and the golden
  report — which is the specification — writes them as different numbers. The version adopted
  answers a question the feature's own PSI cannot: *how much of the score's movement is this
  feature responsible for*, which is what a monitoring pack uses CSI for and which is directly
  comparable across features because it is in one unit. No candidate rule reads it, so the
  definition is a reporting choice rather than a detection one. Rejected alternative: making CSI
  the feature-level PSI and PSI the score-level index only, which would leave nothing to store
  under `psi.<feature>` — a name the golden report cites twice.

## D-053. What the clean synthetic subjects raise through the tools, measured

- **Date:** 2026-09-07 (Phase 5)
- **Q:** D-017 fixes `credit_default`'s clean control at exactly one finding, `E1` at severity
  low, and D-047 fixes `msr_prepayment`'s at none. Both were asserted at data level. What do the
  eight tools of spec §3.7 actually raise, and what are the numbers behind each rule that did not
  fire?
- **A:** Exactly what the two decisions predict. At seed 20260901 on this machine (Python 3.12.14,
  scikit-learn 1.9.0, numpy 2.5.3, pandas 3.0.5):

  **`credit_default`, `--synthetic 5000`, eight tool calls in 2.60 s over 130 artifacts →
  `{E1}`.** `T1`: test AUC 0.7480 ≥ 0.70, Brier 0.1489 ≤ 0.20, calibration slope 1.0027 ∈
  [0.80, 1.20], worst PSI 0.0110 ≤ 0.25 — four declared thresholds, four passes. `C1`: slope
  1.0027, mean predicted 0.2211 against an observed 0.2247, a relative gap of 1.59% against 25%.
  `O1`: train 0.7584 minus test 0.7480 is 0.0104 against 0.08; no period split is declared.
  `S1`: worst feature PSI 0.0110 (`limit_bal`), score PSI 0.0070, `csi.max` 0.0236. `D1`: no
  missing value in either split. `L1`: no feature declared during or after the outcome, strongest
  single feature `delinq_last` at AUC 0.6831 against 0.90, no name matches the lexicon. `L2`:
  row-hash overlap 0.0000. `M1`: worst retained VIF 7.295, Belsley kappa 5.547 against 10 and 30.
  **`E1`: the challenger scores 0.8240 against the champion's 0.7480, a lead of +0.0760 against
  0.03**, at severity `low` — the one candidate. The planner's follow-up finds AUC 0.7588 on the
  744 test clients below the median credit limit against 0.7218 on the 756 above it, which is the
  *opposite* ordering to the golden report's illustrative numbers and is a monitoring
  recommendation rather than a finding, since no threshold governs it.

  **`msr_prepayment`, `--synthetic 2000`, eight tool calls in 4.39 s over 220 artifacts → `{}`.**
  `T1`: test AUC 0.7753 ≥ 0.65, slope 0.9365 ∈ [0.80, 1.20], worst train-to-test PSI 0.0619 ≤
  0.25. `C1`, on **every** split: slopes 0.9937 (train), 0.9365 (test), 0.9969 (out_of_time) and
  0.8373 (vintage_holdout), all inside the band, with relative mean-to-observed gaps of 1.2%,
  0.7%, 5.1% and 17.2%, all inside 25% — the vintage holdout is the closest call in the whole
  control and it passes on both halves of the rule. **`O1`'s second rule, measured as spec §3.7
  writes it and not softened:** out_of_time AUC 0.7846 is *above* test's 0.7753, and vintage
  holdout 0.7718 is below it by 0.0035, against a threshold of 0.05 — so the rule as written does
  not fire, and the margin on the vintage holdout is a factor of fourteen. `S1`: 0.0619 on
  train-to-test (D-046); the reported-not-tested comparisons are 2.945 on `burnout` out-of-time
  and 0.609 on `note_rate` for the vintage. `L1`: strongest single feature `incentive` at 0.7239.
  `L2`: overlap 0.0000. `M1`: worst VIF 4.976, kappa 4.943. `E1`: challenger 0.7337, a lead of
  **−0.0415**. `R1`: the champion's AUC within the training split's regimes is 0.7227 falling and
  0.7238 rising, a spread of 0.0011 against 0.10, and none of the ten retained features changes
  sign between the per-regime refits. `X1`: value change −1,297,986 at −300 bp and +168,055 at
  +300 bp, monotone across all seven shocks, convexity −1,129,932, which is the `negative` the
  package declares. `cpr.<split>.mae` is 0.0266 on train and 0.0426 on test; no package declares a
  `cpr_mae` threshold today, and one that does gets it checked by `T1` with no further change.

  Two scoping decisions inside this are Phase 5's own, both taken before the numbers above were
  read. **`C1` is applied to every split computed**, not to `test` alone: D-046's argument for
  keeping `S1` on train-against-test is that a later period's *composition* differs by
  construction, which is not true of whether the model's probabilities still mean what they say —
  that is precisely what an outcomes analysis asks of an out-of-time split. **`R1` compares
  per-regime refits**, fitted here on the standardised retained features within each regime of the
  *training* split, ranked by mean absolute coefficient across regimes: the champion is one fit and
  has one coefficient per feature, so there is nothing of its own to compare across regimes, and
  its hazard design expands `loan_age` into spline columns no regime shares. The champion's *own*
  scores are what `stability.auc_by_regime` is computed from, so the AUC half of the rule is a
  statement about the model that shipped.
- **Why:** These are the numbers Phase 8's pipeline-level assertion rests on and the numbers the
  study's false-alarm rate is measured against, so they are recorded here rather than left in a
  test's assertions. The two closest calls are named because they are where a later change will
  first show: the vintage holdout's calibration slope of 0.8373 sits 0.037 above the band's floor,
  and `R1`'s sign-flip rule was already known to be near the noise at other seeds (D-047).

## D-054. SR 11-7's outcomes-analysis section is `V.1.c`, not the `V.3` spec §3.7 names

- **Date:** 2026-09-07 (Phase 5)
- **Q:** Spec §3.7's acceptance criterion says `retrieve_guidance("outcomes analysis")` must
  return a span whose `section_id` is SR 11-7 **§V.3**. The section outline this project verified
  against the published PDF, `data/regulatory/sr11-7-outline.yaml`, has outcomes analysis at
  **V.1.c** — one of the three elements of "Model Validation" under V.1, "Evaluation of Conceptual
  Soundness" and its siblings — and has no V.3 at all. Which identifier does Phase 6 assert?
- **A:** `V.1.c`. The outline wins because it was checked against the document; the spec's `V.3`
  is a drafting error in a sentence written before the outline existed. Phase 6's acceptance test
  therefore asserts that the retrieved span's `section_id` is `V.1.c`, and `docs/DESIGN.md` records
  the substitution so that a reader comparing the spec with the tests is not left to guess. The
  golden report already cites `[[reg:SR11-7:V.1.c]]` in its outcomes section, which is the third
  witness.
- **Why:** A regulatory citation that does not resolve is the one failure this project cannot
  afford, since the whole claim of the tool is that its citations are machine-checked. Asserting
  `V.3` would either force a fake section into the corpus or make Phase 6's acceptance test
  permanently red. Recording it in Phase 5 rather than Phase 6 is deliberate: the decision is
  visible now, in the phase that read the acceptance criteria, rather than discovered by whoever
  finds the test failing. Rejected alternative: adding a `V.3` alias to the outline, which would
  put an identifier in the corpus that the source document does not use.

## D-055. The corpus holds SR 11-7 and SR 26-2; OCC Bulletin 2011-12 is not ingested

- **Date:** 2026-09-07 (Phase 6, decided with the user in Cowork)
- **Q:** Spec §3.8 says to ingest two documents, SR 11-7 and OCC Bulletin 2011-12, "and let the
  retriever cite whichever copy matched". Since that sentence was written, **SR 11-7 was
  superseded on 2026-04-17 by SR 26-2** — "Revised Guidance on Model Risk Management", Board of
  Governors of the Federal Reserve System, interagency with the OCC and the FDIC; the OCC issued
  the identical text as **Bulletin 2026-13**, which **rescinds OCC Bulletin 2011-12**. What does
  the corpus hold?
- **A:** Two documents, and neither of them is an OCC bulletin:
  - **`SR11-7`** — *Supervisory Guidance on Model Risk Management*, issued 2011-04-04,
    <https://www.federalreserve.gov/boarddocs/srletters/2011/sr1107a1.pdf>, 21 pages, ingested as
    21 sections, recorded in `SOURCES.json` with status `superseded by SR26-2 on 2026-04-17`. It
    stays in the corpus so that a **historical citation still resolves**: the golden report, this
    project's own earlier documents and any bank document written before April 2026 cite it, and
    a citation that stops resolving is the one failure this tool cannot afford.
  - **`SR26-2`** — *Supervisory Guidance on Model Risk Management (revised)*, issued 2026-04-17,
    <https://www.federalreserve.gov/supervisionreg/srletters/SR2602a1.pdf>, 12 pages, ingested as
    16 sections, status `current`. It is **the drafter's default from Phase 8**.
  - **OCC Bulletin 2011-12 is not ingested.** It carried the same interagency text as SR 11-7 and
    has been rescinded by OCC 2026-13; a second copy of a superseded document would give the
    retriever two ways to say one thing and would put a rescinded issuance in front of a reader.
    The trailing note in `data/regulatory/sr11-7-outline.yaml` that asked for it is replaced.
    `[[reg:OCC2011-12:V]]` is therefore **dangling**, and the message says so by name.
- **Consequences**, all of which are discharged in this phase except the last:
  - The sanctioned golden edit of D-011: `examples/golden_report/REPORT_SCHEMA.json`'s
    `x-quaestor-citation-patterns.regulatory` widens from `(SR11-7|OCC2011-12)` to
    `(SR11-7|SR26-2)`. One character range; the golden report's own citations are all `SR11-7`
    and still match. `docs/REPORT_SCHEMA.md` §5 names the same two documents.
  - `data/regulatory/sr26-2-outline.yaml` is copied in from the Cowork draft. **Every one of its
    sixteen headings matched the PDF text at ingest, in document order, so no heading was
    changed**; the same is true of the twenty-one in `sr11-7-outline.yaml`. Had one not matched,
    the outline would have been corrected to the document, never the text to the outline.
  - **Phase 16 (README and pitch) must say "shaped after the interagency model-validation
    guidance, SR 11-7 as revised by SR 26-2"**, and must never say "compliant" or "certified".
    The two-document corpus is what makes that sentence checkable rather than decorative.
- **Why:** A validation copilot whose regulatory anchors point at a superseded letter is wrong in
  the way that matters most to its reader, and one that silently dropped the superseded letter
  would break every citation written before April 2026. Keeping both, and recording each
  document's status in `SOURCES.json`, is the only arrangement in which "which guidance does this
  sentence rest on?" has an answer a machine can check. Rejected alternative: ingesting OCC
  2026-13 as a third document, which is the same text as SR 26-2 under another number — it would
  double the corpus, split the BM25 statistics across duplicate sections, and force the retriever
  to pick between two identical spans on nothing but corpus order.

## D-056. The outline is a claim about the document, and the ingest holds it to that

- **Date:** 2026-09-07 (Phase 6)
- **Q:** How does `corpus/ingest.py` decide where a section begins, and what happens when the
  outline and the PDF disagree?
- **A:** A heading matches a line of the extracted text when the line, with its whitespace
  collapsed and an optional `I.` / `1.` / `a.` label removed, **equals** the outline's heading
  case-insensitively; the search for each heading starts after the previous one, so the outline's
  order must be the document's order. A heading the outline names and the text lacks raises
  `CorpusError` naming the heading, the section id and the document, with the fix "correct the
  heading in the outline to the document's own wording; never force the text to the outline".
  Three further rules, each visible in the committed JSONL: the text before the first heading (the
  cover page and, in SR 11-7, the table of contents) is discarded; a line that is only a page
  number — `Page 9` in SR 11-7, a bare `2` in SR 26-2 — is dropped; and a heading whose next
  heading follows it immediately is ingested with an **empty body** rather than with the text of
  the sections beneath it. Two SR 26-2 sections are like that, `IV` and `V.1`, and they are pure
  container headings in the document too.
- **Why:** Equality rather than containment is what keeps `V. Model Validation, page 9` in SR
  11-7's table of contents from being mistaken for the body heading `V. MODEL VALIDATION` eight
  pages later; the in-order search is what keeps `Model Use` from matching the wrong one of the
  two places that phrase heads a section. Both documents split cleanly under these rules, which
  is the evidence that they are strict enough. Rejected alternative: fuzzy matching on a
  similarity score, which would have made "the outline is a verified claim about the document"
  untrue — a near-match would pass and nobody would ever see which heading had drifted.

## D-057. BM25's idf smoothing, and scoring the heading with the body

- **Date:** 2026-09-07 (Phase 6)
- **Q:** Spec §3.8 fixes `k1 = 1.5`, `b = 0.75` and the tokenizer, and says nothing about the idf
  or about what text a section's document is. Both choices change the ranking.
- **A:** `idf(t) = ln((N − df + 0.5) / (df + 0.5) + 1)`, the Robertson/Sparck Jones form **with
  the `+ 1` inside the logarithm**; and a span's scored text is **its heading followed by its
  body**. Ties are broken by corpus order, and a span scoring zero is not returned at all.
- **Why:** Without the `+ 1`, a term appearing in every document has idf `ln(0.5/(N+0.5)) < 0`, so
  a query whose only term is "model" would score every section of a corpus about models
  identically negative and the "ranking" would be the corpus order in reverse — the failure is
  silent and looks like a working retriever. Scoring the heading matters because the acceptance
  query is *"outcomes analysis"* and that phrase is the name of the section rather than something
  its prose repeats: on the body alone, SR 11-7 V.1.b ("Ongoing Monitoring", which discusses
  outcomes analysis in passing) competes with the section actually called Outcomes Analysis.
  Dropping zero-scoring spans is what makes "the guidance does not discuss prepayment convexity"
  return nothing instead of three arbitrary sections a drafter would then cite. Rejected
  alternative: adding a stop-word list so that "the" and "of" stop contributing, which on a corpus
  of two documents would be tuned against the queries it was tested on, and which the idf already
  does in a way a reader can check.

## D-058. `CorpusError`, and why a dangling `[[reg:...]]` is not one

- **Date:** 2026-09-07 (Phase 6)
- **Q:** Spec §3.1's exception hierarchy is closed. The corpus can fail to ingest, fail to load,
  and be asked for a document it does not hold. Which exception is that?
- **A:** A new `CorpusError(QuaestorError)`, added under the same rule that admitted
  `LLMProviderError` in D-024. It is raised when an outline is missing or malformed, when a
  heading is not in the document, when a committed JSONL is missing or unreadable, and when a
  retrieval is restricted to a document that was never ingested. It is **not** raised when a
  `[[reg:DOC:SECTION]]` citation names a document or a section the corpus does not have: that
  resolves to `dangling` with a message quoting the citation, exactly as a bad `[[art:...]]` does.
  `retrieve_guidance` converts the errors it can provoke into `ToolError`, so a planner sees one
  failure type from a tool call.
- **Why:** The two failures are different in kind and in audience. A corpus that will not load is
  a broken installation and stops the run; a drafter that invented `[[reg:SR11-7:V.3]]` is prose
  the repair loop fixes, and turning it into an exception would abort a report over a sentence.
  Making the distinction in the type is what lets Phase 7's verifier count dangling regulatory
  citations in the grounding denominator without catching installation failures by accident.
  Rejected alternative: reusing `ArtifactError` for the corpus, which reads as "this run's
  computed evidence is wrong" when the truth is "the shipped guidance text is missing".

## D-059. `guidance.<query_hash>`, not the golden report's readable slug

- **Date:** 2026-09-07 (Phase 6)
- **Q:** Spec §3.7 names the artifact `guidance.<query_hash>`. The golden report's Appendix B
  shows `guidance.outcomes_analysis`, a slug of the query. Which does `retrieve_guidance` store?
- **A:** `guidance.<query_hash>`, where the hash is the `stable_hash` of the whole request —
  query, `k` and the document restriction — so that the same request in a run resolves to the same
  artifact and a different request cannot land on the same name. The golden's readable slug stays
  as it is: it is illustrative, and `tests/test_tools_clean.py` has excluded `guidance.*` from the
  Appendix-B resolution check since Phase 5, which is exactly the carve-out this decision needs.
- **Why:** The store refuses to put a different payload under a name it already holds, because a
  citation written against the old hash would stop resolving (D-023). A slug makes that refusal
  reachable by ordinary drafting: "outcomes analysis" and "outcomes analysis, by split" slugify
  to the same name and would collide, and a plan that asked for `k=3` and then `k=5` on one query
  would collide with itself. Hashing the request also makes the trace answer "which guidance was
  the drafter shown for this section?" exactly rather than approximately. Rejected alternative:
  a slug with a disambiguating counter, which makes the artifact's name depend on the order the
  plan happened to run in, so two runs of one package would produce different Appendix B names.

## D-060. `vocab.py`: where the section identifiers and the configuration names live

- **Date:** 2026-09-07 (Phase 7)
- **Q:** `report.md`'s front matter, `claims.json` and `findings.json` all name the same seven
  sections and the same three configurations, and both JSON Schemas spell the enums out.
  `CLAUDE.md`'s repository layout gives sections no home and puts configurations in `configs.py`.
  Where does one spelling of each live?
- **A:** A new module, `src/quaestor/vocab.py`, holding `ReportSection` and `Configuration` and
  importing nothing. `findings.py` and `verifier/` both need them in Phase 7; `report/` and
  `configs.py` arrive in Phase 8 and will import `findings`, `verifier` and `tools`.
- **Why:** Putting the vocabulary in `configs.py` or under `report/` makes the import graph a
  cycle the moment Phase 8 fills either one — `configs.py` will import the tool registry, the
  registry imports `findings.py`, and `findings.py` would import `configs.py`. A module with no
  imports of its own cannot participate in a cycle, and the two enums are shared vocabulary rather
  than behaviour, so nothing else belongs in it. It is one module outside `CLAUDE.md`'s layout,
  recorded here because the layout is the contract. Rejected alternative: defining
  `ReportSection` inside `findings.py`, which is where the first consumer happens to be and which
  would leave a reader looking for the report's section list inside the findings module.

## D-061. The evidence rule binds construction; reading a document back waives it deliberately

- **Date:** 2026-09-07 (Phase 7)
- **Q:** `CLAUDE.md`: "A `Finding` object cannot be constructed without at least one artifact hash
  that exists in the store." The store is not a field of a persisted finding, and `eval/score.py`
  scores a run from `findings.json` alone — often on a machine that no longer has that run's
  artifacts, and always for the golden report, whose hashes resolve to nothing by design. How is
  the rule enforced without making a written document unreadable?
- **A:** The store reaches the validator through pydantic's **validation context**, under the key
  `store`. `Finding.model_validate(payload, context={"store": store})` looks every hash up;
  `context={"store": None}` says out loud "this document was written by a run that checked it, and
  I am reading it back without that run's store"; **no context at all is refused**, so the waiver
  is always written down at the call site. `FindingsDocument.read` defaults to `None` and
  `Finding.from_candidates` always passes a real store. The non-empty-list half of the rule is a
  field constraint and is never waived. A `_evidence_checked` private attribute records that the
  check has run, because a pydantic `mode="after"` validator fires again whenever the instance is
  placed inside another model — putting a finding into a `FindingsDocument` re-runs it with no
  context, which would otherwise fail every document ever built.
- **Why:** The rule exists to stop a validator inventing a finding, and that is a property of the
  moment a finding is made, not of every later read of the file it was written to. Making the
  waiver a distinct, named value rather than a missing argument is what keeps it from becoming the
  default by accident: forgetting the store is an error, waiving it is a sentence. Rejected
  alternative: a module-level "checking on/off" flag or a context variable, which is action at a
  distance — a test that forgot to reset it would silently disable the constraint the project is
  built around.

## D-062. A claim's id is computed when it is made and kept when it is read

- **Date:** 2026-09-07 (Phase 7)
- **Q:** `Claim.id` is `stable_hash([section, text, value])` (D-012). Should reading a
  `claims.json` recompute it and check it?
- **A:** No. A claim built in the pipeline computes its id; a claim read from a file keeps the id
  the file carries. The golden `claims.json`'s ids were written by hand in Phase 1 and do not
  reproduce the hash, and it is pinned by `MANIFEST.json`, so recomputation would make the Phase 1
  specification unreadable by the Phase 7 code that implements it.
- **Why:** An id is an identifier: its job is to let the repair loop, the `repairs` list and the
  trace name one claim, and it does that whatever it is. Treating it as a checksum would add a
  failure mode ("this file's ids disagree with this version's hashing") that no consumer of the
  file can act on, and would couple the readability of every archived study result to the
  stability of a hash function across releases. Rejected alternative: validating the id on read
  and rewriting it when it disagrees, which is the worst of both — it changes a persisted
  identifier and tells nobody.

## D-063. The extractor is asked for eight fields, not eleven

- **Date:** 2026-09-07 (Phase 7)
- **Q:** `structured()` returns a pydantic model. Should the extractor's model be `Claim` itself?
- **A:** No. `ExtractedClaim` is the eight fields a model can know — `text`, `value`, `unit`,
  `metric`, `split`, `comparison`, `citation`, `rounding` — and the caller adds the three it
  already knows: `section` (it passed it in), `id` (a hash of the other three) and `source`
  (always `report` for an extraction).
- **Why:** Asking a model for a value the caller can compute is a way of being told a different
  one, and each of the three has a consequence: a wrong `section` moves a claim into another
  section's grounding row, a wrong `id` breaks the repair loop's ability to name a claim, and a
  `source` of `developer` would smuggle report prose into the channel that raises `T1` findings.
  Rejected alternative: asking for all eleven and overwriting three after the fact, which is the
  same thing with a longer prompt and a silent correction.

## D-064. `extract` returns a record, not a bare `list[Claim]`

- **Date:** 2026-09-07 (Phase 7)
- **Q:** Spec §3.10 writes the extractor as returning `list[Claim]`. The same section also
  requires that a number found by the regex pre-pass be marked `unattributed` rather than
  `unsupported`, and that the exclusion list appear in `claims.json`. Neither fits in the list.
- **A:** `extract` returns an `Extraction`: `claims` is the list the spec names, and beside it are
  `unattributed` (the ids the pre-pass added), `exclusions`, `n_excluded_tokens` and
  `n_from_model`. The matcher takes the ids as `match_claims(..., unattributed=...)`. An exclusion
  class is recorded only when it actually swallowed a numeric token — except for citations, whose
  hash and logical name are excluded by construction — so the published list is what was excluded
  rather than what could have been.
- **Why:** `unattributed` and `unsupported` are different failures and the study counts them
  separately, so the distinction cannot be reconstructed from a claim's fields: a pre-pass claim
  and an uncited extracted claim are identical objects. `n_from_model` is extraction recall, which
  `04` §6 asks for by name. Widening the return type is the smallest change that keeps the spec's
  list intact — `extraction.claims` is exactly what §3.10 describes. Rejected alternative:
  a `status` field on `Claim` set to `unattributed` at extraction time, which would put the
  matcher's vocabulary on the extractor's output and give `claims.json` two places to disagree
  about a claim's verdict.

## D-065. The matcher's message is not a field of `VerifiedClaim`

- **Date:** 2026-09-07 (Phase 7)
- **Q:** The repair loop hands the drafter a sentence — "you wrote 0.68 for `metrics.oot.auc`; the
  artifact says 0.6812; cite or remove" (§3.11). Where does that sentence live?
- **A:** On `Match`, which carries the `VerifiedClaim` and the message together; only the claim is
  persisted. The message also goes onto the `claim_check` trace event, so a run's own record of
  why a claim failed survives without enlarging `claims.json`.
- **Why:** `claims.json` is the study's scoring input and `CLAIMS_SCHEMA.json` is closed, so a new
  field is a schema change after Phase 1, which `CLAUDE.md` makes a stop-and-ask. It would also be
  the wrong place: the message is written for the drafter and changes with the wording of the
  repair prompt, while the persisted claim is a measurement. Rejected alternative: reconstructing
  the sentence in the repair loop from `status`, `value` and `artifact_value`, which duplicates
  the matcher's knowledge of *why* a claim failed — a dangling citation and a mismatched value
  need different sentences and only the matcher knows which happened.

## D-066. A report with no claims scores 0.0, not 1.0

- **Date:** 2026-09-07 (Phase 7)
- **Q:** Grounding precision is `verified / (verified + mismatch + unsupported + dangling +
  unattributed)`. What is it when the denominator is zero?
- **A:** `0.0`, printed beside `n_claims: 0`.
- **Why:** This is the one number in the repository that could flatter by construction. A vacuous
  `1.0000` on the front page of a report that made no checkable statement is exactly the headline
  a reader would misread, and it is reachable — a `plain_llm` run whose model wrote prose with no
  numbers in it produces it. `0.0` beside a zero denominator is unmistakable and cannot be quoted
  out of context in the README, because the README quotes the study's mean and minimum. Rejected
  alternative: `None`, which the schema would have to admit as a nullable number and which every
  consumer — the front matter, the scope block, `summary.json` — would then have to special-case.

## D-067. A mismatched developer claim stores its comparison as an artifact

- **Date:** 2026-09-07 (Phase 7)
- **Q:** D-016 makes a mismatched `package.yaml` claim the claim channel of a `T1` finding. A
  finding needs evidence, and the comparison — declared 0.139 against a computed 0.1602 — is not
  an artifact any tool wrote. What does the candidate point at?
- **A:** At the cited artifact **and** at `developer_claim.<i>`, a JSON artifact this check writes
  holding the declaration, the logical name it was compared to, both values, their difference, the
  tolerance and the status. Under `--synthetic` nothing is compared and nothing is stored.
- **Why:** Every other candidate points at a number a tool computed; this one is the only
  comparison in Quaestor with no threshold behind it, so without a stored record its evidence
  would be the artifact alone — which is the number that is *right*, not the disagreement that is
  the finding. Storing the comparison also lets the report cite it rather than restate it, which
  is the rule the whole citation apparatus exists to enforce. Rejected alternative: exempting `T1`
  from the evidence rule the way `PRE_RUN_TOOL` is exempted (D-021), which would put a second hole
  in the one constraint `CLAUDE.md` states as non-negotiable.

## D-068. The golden report's 92 claims are re-matched on logical name, and the test says so

- **Date:** 2026-09-07 (Phase 7)
- **Q:** The Phase 7 acceptance asks that every one of the golden report's 92 post-repair claims
  verify against a store built from Appendix B. The golden's hashes are `sha256(logical_name)[:8]`
  and resolve to nothing, and a content address of an illustrative value is not the address of the
  same value stored today. How is the test honest about what it checks?
- **A:** `tests/verifiersupport.py` rebuilds a store from Appendix B under the golden's own logical
  names and rewrites each citation's `hash8` to the rebuilt store's before matching; the module
  docstring, the test module's docstring and the Phase 7 run-log line all state that this one test
  matches on the logical name and the path and not on the hash. Appendix B carries values only for
  the scalars, so the two table artifacts are read back out of the report's own renderer blocks and
  the five JSON artifacts are written out from the report's prose, which is stated where they are
  defined.
- **Why:** The hash is the half of a citation that stops a number being cited to another run's
  artifact, so a test that quietly dropped it while claiming to check citations would be worse than
  no test. Naming the licence keeps the check worth having — it exercises the matcher over 92 real
  claims covering percent normalisation, counts, a declared rounding, a delta, a table cell and
  five JSON paths — while leaving the hash assertion to `tests/test_citations.py`,
  `tests/test_verifier_match.py` and, from Phase 8, the pipeline itself. Rejected alternative:
  editing the golden report's hashes so that they resolve, which is a sanctioned-edit request under
  D-011 for a directory whose whole purpose is to be a fixed specification.

## D-069. A claim is held to the precision its own sentence used (amends D-014)

- **Date:** 2026-09-07 (Phase 8, decided in Cowork)
- **Q:** D-014 gives every claim a flat tolerance from its unit: 0.005 for a ratio or a per cent in
  the unit interval, 0.5 for a percentage on a 0–100 scale, 1% relative otherwise, and a declared
  `rounding` may widen it. That verifies `0.021` against an artifact of `0.0175`, and `22.0%`
  against `0.2212`. Is a number that the artifact does not round to a verified claim?
- **A:** No. A claim verifies when the artifact value **rounds to the value as written, at the
  precision the prose used**: `0.74` verifies against `0.7412`, `0.021` does not verify against
  `0.0175`, `22.0%` does not verify against `0.2212`. The applied tolerance is
  `min(0.5·10^-decimals_written · scale, default_for_unit, 0.5·10^-rounding · scale)`, where
  `decimals_written` is read from the claim's own `text` — the first numeric token in it whose
  value is the claim's value, so `22.0%` declares one decimal and `22%` declares none although both
  parse to the same float — and `scale` carries a tolerance stated in the units the prose wrote
  into the units the artifact is held in (`0.01` for a per cent against a unit-interval artifact,
  `0.0001` for basis points against a rate). Spec §0's three defaults survive **as the ceiling the
  tolerance never exceeds**, which is what keeps a fifteen-decimal drafter from being held to
  floating-point noise. Counts stay exact. The `rounding` field stays, as an explicit override that
  can only narrow; under D-014 it could only widen, and that is the one direction it may no longer
  go. Implemented in `verifier/match.py` (`written_decimals`, `normalisation_scale`,
  `default_tolerance`, `tolerance_for`); `docs/REPORT_SCHEMA.md` §6 carries the formula.
- **Why:** Grounding precision is the number this project asks to be judged on, and under D-014 it
  counted as grounded a sentence whose number the cited artifact does not produce at the precision
  the sentence itself chose. `22.0%` is a claim about tenths of a per cent; verifying it against
  22.12% measures the tolerance rather than the model. The direction of the `rounding` field
  reverses for the same reason: a drafter that writes fewer decimals has already been given the
  wider tolerance by the rule itself, so the only honest thing left for an explicit declaration to
  do is to promise *more* precision than the token shows. Reading the precision off the sentence
  rather than off the float is what makes trailing zeros mean what they say; the float `22.0` is
  the float `22`, and only the prose distinguishes them. Measured consequences, all of them
  recorded rather than assumed: **the golden report's 92 post-repair claims all still verify and
  its pre-repair `0.0136` still mismatches**, while 60 of the 92 record a narrower `tolerance` than
  the Phase 1 `claims.json` does (every four-decimal metric from 0.005 to 0.00005, `22.0%` from
  0.005 to 0.0005, and each of the six claims that declared a `rounding`), so
  `tests/test_verifier_golden.py` now asserts the statuses exactly and the tolerances as an
  inequality with the narrowing count pinned; and **the two tolerance boundaries the Phase 7
  component eval reported, `vq04` and `vq10`, are gone** — both perturbed sentences write four
  decimals and are now caught as the mismatches they are, so `tolerance_boundaries` is empty and
  status accuracy stays 1.0 on all three classes. `examples/golden_report/claims.json` is not
  edited: it is the Phase 1 specification of the file's *shape*, its numbers are illustrative, and
  D-011's procedure exists for changes to the shape rather than for a re-measurement of a
  tolerance. Rejected alternative: keeping D-014 and asking the drafter to declare `rounding` on
  every number, which puts the honesty of the headline figure in the hands of the component being
  measured.

## D-070. `pipeline.py` holds `validate()`; `configs.py` holds the three configurations

- **Date:** 2026-09-07 (Phase 8)
- **Q:** `CLAUDE.md`'s layout gives Phase 8 four homes — `report/`, `agent/`, `configs.py` and
  `cli.py` — and spec §9 puts `validate()` on the public surface without saying which module it
  lives in. Where does the pipeline entry go?
- **A:** A new module, `src/quaestor/pipeline.py`, holding `validate()` and the objects it returns.
  `configs.py` keeps what the layout says it keeps: the three configurations, as data — which plan
  runs, who writes the narrative, whether the repair loop runs — plus the class list each tool
  screens for, which `findings.json`'s `checks_without_candidates` is built from.
- **Why:** `validate()` imports the planner, the tool registry, the drafter, the verifier, the
  renderer and the findings layer; `configs.py` is imported *by* several of those, and a module
  that is both the vocabulary and the orchestrator is a cycle waiting for the first import to be
  added in the wrong direction. It is the second module outside `CLAUDE.md`'s layout, after
  `vocab.py` (D-060), and is recorded for the same reason: the layout is the contract. Rejected
  alternative: putting the pipeline in `cli.py`, which would make every caller of the library go
  through the command-line module and would leave Phase 9 unable to add a parser without touching
  the pipeline.

## D-071. The renderer owns section 6's structure and the drafter owns its prose

- **Date:** 2026-09-07 (Phase 8)
- **Q:** Section 6 has a fixed shape: one `### F-NNN · <class> <name> · severity **<severity>**`
  heading per finding, in severity order, with the ids the findings document assigned. The drafter
  writes one `structured()` call per section returning `{"markdown": str}` (spec §3.11). If the
  model writes those headings, the report's structure depends on it copying twelve characters
  correctly; if the renderer writes them, where does the finding's prose come from?
- **A:** Both, in that order. The drafter is given the exact heading line for each finding and asked
  to write the section with them; the renderer then **re-composes** the section from what came
  back: the text before the first `###` is kept as the section's opening, each finding is emitted
  under the canonical heading with the body the drafter wrote beneath it, and a finding the drafter
  did not write about keeps the narrative its candidates gave it. The drafted body also becomes the
  finding's `title` and `narrative` in `findings.json`, the title being the leading `**bold**` run
  when there is one.
- **Why:** The structural half of a report is not a thing to ask a language model for twice. Every
  finding is guaranteed to appear, exactly once, under the id the findings document assigned and in
  severity order, whatever the drafter did — and nothing the drafter wrote is discarded, which is
  the failure mode of the alternative. Rejected alternative: one `structured()` call per finding,
  which would give the renderer the narrative directly and is a different prompt shape from every
  other section, so the study's per-section token counts would stop being comparable.

## D-072. An unevidenced `plain_llm` finding is recorded against a stored record of itself

- **Date:** 2026-09-07 (Phase 8)
- **Q:** Spec §3.13: a `plain_llm` finding "naming no existing artifact is recorded as
  `unevidenced` and scored as a false alarm". `findings.json` is closed by
  `FINDINGS_SCHEMA.json`, whose only home for a rejected candidate is `candidates_not_promoted`,
  and whose `evidence` there must be at least one eight-character hex hash. A finding whose
  evidence does not resolve has, by definition, no such hash to give. Where is it written?
- **A:** In `candidates_not_promoted`, with a `reason` that begins with the literal token
  `unevidenced:` and with the evidence pointing at `unevidenced_record.<i>` — a JSON artifact this
  configuration writes, holding what the model claimed, the evidence strings it named, and the fact
  that none of them resolves. The record exists in the store, so the entry satisfies both the
  schema and the evidence rule, and the study reads the token rather than the prose.
- **Why:** It is D-067's move applied to the baseline: the only comparison with nothing behind it
  gets a stored record of the disagreement, so the thing being pointed at is the false alarm
  itself rather than an artifact chosen to stand in for it. It also keeps the report schema
  untouched, which after Phase 1 is a stop-and-ask. Rejected alternative: dropping unevidenced
  findings entirely, which would flatter the baseline exactly where the study means to measure it —
  a model that names an artifact that does not exist would be scored as having said nothing.

## D-073. How a claim before a repair round is paired with the claim after it

- **Date:** 2026-09-07 (Phase 8)
- **Q:** `claims.json` `repairs` is a list of `{section, claim_id, before, after, instruction}`
  (D-012), so every round has to say which claim after it replaced which claim before it. A claim's
  id is `stable_hash([section, text, value])`, and a re-draft rewrites the sentence, so the ids do
  not generally survive a round. What is the pairing rule?
- **A:** Three cases, in order. **By id**, which covers the commonest repair exactly: a number the
  drafter wrote correctly and forgot to cite keeps its id when the citation is added, because the
  id hashes the section, the text and the value and the citation is none of the three — the text
  changes, so this holds only when the drafter re-drafts the sentence identically, and it is tried
  first because when it matches it is certain. Then **by nearest unpaired verified value** within
  ten per cent of the claimed value, which is the drafter correcting a number it got wrong (0.0136
  for 0.0126). Otherwise the number is **gone**: "cite or remove" allows removing, and a claim that
  no longer exists has no `after` side to record, so the round writes it on the `repair` trace
  event's `removed` field and no row in the repairs table.
- **Why:** The repairs table is read by a human asking "what did the loop change?", and a wrong row
  in it is worse than a missing one: it would attribute a number to a repair that did not produce
  it. The ten per cent window is the smallest thing that distinguishes a correction from a
  different statement — a claim that moved further than that is not the same claim repaired, it is
  a new sentence. Recording a removal on the trace rather than in `claims.json` keeps the schema
  closed (a `removed` status would be a sixth `ClaimStatus` and a change to `CLAIMS_SCHEMA.json`,
  which is a stop-and-ask after Phase 1) while keeping the fact recoverable, since `eval/score.py`
  reads the trace. Rejected alternative: pairing by position in the section's claim list, which is
  wrong the moment a re-draft adds or drops a sentence — exactly what a repair round does.

## D-074. The report schema is shipped inside the package, pinned to the golden by a test

- **Date:** 2026-09-07 (Phase 8)
- **Q:** The renderer enforces `examples/golden_report/REPORT_SCHEMA.json` at runtime: the front
  matter's JSON Schema, the eleven required headings, the renderer-block pattern, the citation
  forms and the forbidden patterns. `examples/` is not inside the wheel. Where does the installed
  renderer read those rules from?
- **A:** From `src/quaestor/report/report_schema.json`, a copy of the golden file that ships with
  the package, exactly as the regulatory corpus ships as `src/quaestor/corpus/*.jsonl`.
  `tests/test_report_schema.py` compares the two **byte for byte**, so a sanctioned edit to the
  golden schema under D-011 that forgot the copy is a failing test rather than a renderer quietly
  enforcing last month's rules. Also decided here: `types-jsonschema` joins the dev dependencies,
  because `jsonschema` is now imported by `src/` and `mypy --strict` has no stubs for it;
  `CLAUDE.md`'s dev list already names "type stubs", and no runtime dependency changes.
- **Why:** A schema the code cannot read at runtime is documentation, and the four refusals of spec
  §3.11 are the difference between a report format and a report. Copying the file rather than
  restating it as a Python literal keeps the diff between the two copies readable and the pin
  exact. Rejected alternatives: reading the golden file by relative path from the installed package
  (it is not there), and moving the golden schema into `src/` (the golden directory is the Phase 1
  specification and `MANIFEST.json` pins its contents).

## D-075. `structured()` gains `trace_fields`, which go on the event and not to the provider

- **Date:** 2026-09-07 (Phase 8)
- **Q:** A `draft` event should say which section it drafted and whether it was a repair round; a
  `plan` event should say which step of the bounded loop it was. `structured(...)`'s `**params` is
  forwarded to the provider, so passing `section="outcomes"` through it would hand a real adapter
  an argument it has never heard of. Where do per-call trace fields go?
- **A:** A new keyword-only `trace_fields: Mapping[str, Any] | None` on
  :func:`quaestor.llm.structured.structured`, merged into every `llm_call` event of that call and
  never passed to the provider. Two callers use it today: the drafter (`section`, `repair`) and the
  planner (`step`).
- **Why:** Without it the study cannot say which section cost what, and with it hidden inside
  `**params` the first live run would fail on the first draft. Keeping the two channels separate is
  the same distinction `Completion.raw`'s `quaestor_` prefix already makes in the other direction
  (D-025): what the adapter knows goes onto the trace, what the provider needs goes to the
  provider. Rejected alternative: emitting a second, per-section event beside the `llm_call`, which
  would double the event count the study divides by.

## D-076. Nothing the renderer or the template writes carries an uncited number

- **Date:** 2026-09-07 (Phase 8)
- **Q:** Grounding precision is computed over the drafted prose, and the pre-pass counts every
  numeric token it finds there. The renderer adds prose of its own to section 6 ("candidates raised
  and not promoted", "checks that ran and raised no candidate") and the `rules_only` template
  writes the whole report. A number in either would be counted against a model that did not write
  it. What may they write?
- **A:** No bare numeric token. The renderer's section-6 lines name defect classes and tools, both
  in inline code, and nothing else; the template writes `The value of \`<logical_name>\` is <n>
  <citation>.` — the logical name in inline code (excluded, D-015) and the value cited — and never
  the artifact's caption, because a caption like "change in servicing value at -300 bp" carries a
  number that no citation follows. Section 6's template statement names the class, the tool and the
  severity and leaves the check's own sentence, which is full of numbers, in `findings.json`.
  `tests/test_pipeline.py` asserts `rules_only`'s post-repair precision is 1.0 on a real subject,
  which is what catches the next such leak.
- **Why:** `rules_only` is the arm spec §3.13 describes as "trivially verified", and it is the
  study's control: if its precision is not 1.0, the number the study reports for the other two arms
  cannot be read as a property of the model that wrote them. The renderer's own prose is the same
  argument from the other side — the report's structure must not be able to lower the score of the
  prose. Rejected alternative: excluding renderer-written lines from extraction by wrapping them in
  renderer blocks, which `REPORT_SCHEMA.json`'s block pattern does not allow (`scope` and
  `table <name>` are the two kinds) and which would make the exclusion list unauditable.

## D-077. The pre-pass defines the eligible numbers; a claim for an excluded token is dropped

- **Date:** 2026-09-07 (Phase 9)
- **Q:** D-064 made the regex pre-pass the floor under the denominator: a number the extractor
  omits is added back as `unattributed`, so an extractor cannot improve grounding precision by
  working less. The other direction was left open. What happens to a claim the model returns for a
  number the pre-pass had *excluded* — the digits inside a citation's hash or logical name, a
  feature name in inline code, a section number in a heading, a cell of a renderer block?
- **A:** It is dropped, and recorded in `claims.json`'s exclusion list under the pattern
  `extractor_returned_excluded_token`, with the number as the model's own sentence wrote it. The
  pre-pass owns the eligible set in both directions and the model only classifies it: a returned
  claim is kept when, and only when, it can be matched to an eligible token — first by value inside
  the line it quotes, then, for what is left over, by value against any unfilled token of the
  section. That second pass is why a model that paraphrases the sentence, or attributes a number to
  the wrong line, still has its citation used rather than thrown away; only a number that is
  nowhere in the eligible prose is dropped. `n_from_model` still counts what the model returned,
  including what was dropped, so extraction recall is measured against what it actually said.
- **Why:** Grounding precision is `verified / (verified + mismatch + unsupported + dangling +
  unattributed)`, and D-064 protected the denominator only from below. An extractor that returned
  `[[art:a3f2b1c9:...]]`'s digits as a verified claim would raise the numerator with a number no
  reader would call a claim — the mirror image of the omission D-064 forbids, and the easier one to
  produce accidentally, since the drafting prompt tells the model to list numbers "including those
  inside a citation's logical name" (that instruction exists so the model does not silently skip
  the sentence; the pre-pass, not the model, decides what survives it). The exclusion is published
  rather than silent for the same reason every other exclusion class is: a list of what was left
  out is auditable, and a number that vanished is not. Two Phase 7 tests asserted the old
  behaviour and are rewritten here, one into its mirror image and one into the paraphrase case the
  second pass now covers. Rejected alternative: keeping the claim and matching it, which is what
  Phase 7 did — the claim then resolves as `unsupported` or `dangling` and *lowers* precision for a
  number the report never claimed, which is the same corruption of the measure in the other
  direction.

## D-078. A prompt over 64 KiB goes to the Claude CLI on stdin, not in the argument vector

- **Date:** 2026-09-07 (Phase 9)
- **Q:** `ClaudeCLILLM` passes the prompt as the positional argument after `-p`. A `plain_llm`
  prompt carries `metrics.json`, `model_summary.json`, `features.json`, `splits.json` and a raw
  data profile in one call, and a `full_agent` extraction prompt carries a whole rendered section.
  How large may that argument be?
- **A:** Not this large. macOS caps a *single* argument well below the `ARG_MAX` it allows in
  total, so a long enough prompt fails with `OSError: [Errno 7] Argument list too long` before the
  CLI runs at all. Above `STDIN_THRESHOLD_BYTES = 64 * 1024` UTF-8 bytes the adapter emits `-p`
  with **no** positional prompt and writes the prompt to the subprocess's stdin, which is how
  `claude -p` reads a prompt when it is given none. The threshold is a constructor argument, the
  length is counted in encoded bytes rather than characters, and both paths are asserted with the
  monkeypatched `subprocess.run` — the short one carries the prompt in `argv` and nothing on
  stdin, the long one the other way round.
- **Why:** 64 KiB is a conservative fraction of the smallest single-argument limit either supported
  platform imposes (macOS's is the binding one; Linux's per-argument limit is larger), chosen so
  that the switch happens long before the failure rather than at the edge of it. It is not a tuned
  number and nothing measures it: the point is that a live run must not die on a prompt that is
  merely long, and a run that switched at 200 KiB would still be one growing artifact away from the
  same crash. Rejected alternatives: always using stdin, which would make the argument vector the
  tests assert on differ from what a human debugging a call would paste into a shell; and writing
  the prompt to a temporary file and passing its path, which is a third thing to clean up and does
  not match any documented flag of the CLI.

## D-079. Quaestor's cassettes and Probatio's cassettes are different stores with different jobs

- **Date:** 2026-09-07 (Phase 9)
- **Q:** `quaestor validate --record-cassettes DIR` writes one JSON file per model call, and Phase
  11 records Probatio cassettes for the test layer. Two recording formats in one repository invites
  the question of which one is *the* cassette format. Are they the same thing?
- **A:** No, and neither reads the other's files. `llm/recording.py` is **the record of a
  validation run**: it is written beside that run's report, under whatever directory the operator
  named, it holds the request and the `Completion` for every call the run made, and it exists so
  that a published report can be re-examined and re-rendered (`--llm replay --cassettes DIR`).
  Phase 11's cassettes are **a test suite's tapes**: they are recorded through Probatio's own
  provider fixture, committed under `tests/probatio/cassettes/`, and replayed by `pytest` in CI as
  gate condition 6. A file of one kind in the other's directory is meaningless.
- **Why:** They differ in what they are keyed by, in who owns them and in what breaks when they go
  stale. A run's record is keyed by request — `stable_hash(system, prompt, params)` — because the
  question a replay asks is "what did the model answer *this*"; two consequences follow and are
  accepted rather than engineered away: re-running a validation over the same artifacts hits the
  same tapes, and a run that asks one identical question twice keeps one tape for both, with the
  number of times it was asked recorded on the file (`calls`) and a non-deterministic provider's
  last answer overwriting the first. A test suite's tapes are keyed by case and are pinned to the
  assertions written against them; a stale one there is a failing test, while a missing one here is
  a failed replay that names the hash. Rejected alternative: making Quaestor's runs record through
  Probatio, which would put a dev-only dependency inside the live `validate` path — `CLAUDE.md`
  puts `probatio-llm` in the dev list, and a live validation that imports the test framework is a
  live validation that cannot be installed from the wheel.

## D-080. The provider behind `--llm fake` ships inside the package

- **Date:** 2026-09-07 (Phase 9)
- **Q:** `CLAUDE.md`'s command list, the README's quick start and gate condition 5b are all one
  line: `quaestor validate subjects/credit_default --synthetic --llm fake --out /tmp/r`. A bare
  `FakeLLM` answers a drafting prompt with `FAKE(<hash>)`, which `structured()` rejects, so that
  line needs a fake that can actually draft. Phase 8's lives in `tests/reportsupport.py`. Where
  does the shipped one live?
- **A:** In `src/quaestor/llm/offline.py`, as `OfflineLLM`, which is what `--llm fake` builds. It
  is the Phase 8 `SectionFake` minus its defects: it dispatches on which of the four prompts it was
  sent, drafts one cited sentence per artifact from the JSON the prompt carries, extracts every
  numeric token outside an exclusion, stops the bounded loop and writes the baseline's seven
  headings. `tests/reportsupport.py` now subclasses it, overriding three hooks
  (`scalar_sentence`, `plan_action`, `plain_findings`) to forget a citation, to script a follow-up
  or to name an artifact that does not exist — so the repair loop's tests still have a model that
  breaks the rules, and the behaviour under test is the same code the shipped command line runs.
- **Why:** A command line in the project's own constitution that only works if the test tree is
  installed is not a command line. Shipping the fake also makes the demo and the quick start
  reproducible by a reader who has the wheel and no key, which is what an open evaluation needs; it
  is named `fake` in the flag, in `Completion.model` and in the report's front matter, so no report
  it writes can be mistaken for a model's work. Rejected alternatives: making `--llm fake` a bare
  `FakeLLM` and letting the quick start fail (the line is in `CLAUDE.md`); and importing the test
  helper from `cli.py`, which would put `tests/` on the runtime import path.

## D-081. Bare `--synthetic` reads a table in `configs.py`, and refuses an unknown package

- **Date:** 2026-09-07 (Phase 9)
- **Q:** Spec 3.14 writes `--synthetic N`; `CLAUDE.md` writes `--synthetic` with no number. The two
  subjects document different sizes — 5,000 rows for `credit_default` (spec 4.1), 2,000 loans for
  `msr_prepayment` (spec 4.2). Where does a bare `--synthetic` get its number, and what happens for
  a package that is neither?
- **A:** From `SYNTHETIC_DEFAULT_N` in `configs.py`, keyed by package name; a package the table
  does not know makes bare `--synthetic` a usage error (exit 2) whose message names the flag with a
  number in it. `--synthetic 0` and a negative count are the same error. A `synthetic_default_n`
  field in `package.yaml` would replace the lookup without touching the parser, and is not added
  now because a change to `package.yaml` after Phase 1 is a stop-and-ask.
- **Why:** The size of a generated panel decides every figure computed from it, so a program that
  invents one is a program whose numbers cannot be compared with `PROGRESS.md`'s. The table lives
  in `configs.py` rather than in `cli.py` because it is a property of the subjects, and because the
  study and the MCP server will want the same defaults without going through a parser. Rejected
  alternative: one default for every package, which would silently run the credit subject at the
  hazard subject's size and quietly move every number this repository has measured.

## D-082. `cli.py` has parsers for three commands and refuses the other five as unknown

- **Date:** 2026-09-07 (Phase 9)
- **Q:** Spec 3.14 tabulates eight commands. `study build`, `study run`, `study score`,
  `verifier-eval` and `mcp` belong to Phases 10, 12, 13 and 15. Should the parser accept them now
  and report that they are not implemented?
- **A:** No. `quaestor study run` is an argparse "invalid choice" error, exit 2, exactly as a
  misspelling would be, and `--help` lists `validate`, `tool` and `corpus`. Each later phase adds
  its own subcommand in its own commit, beside the code that makes it work.
- **Why:** It is the Phase 0 rule about half-built flag surfaces, applied to the program's front
  door: a `--help` that lists what the program is going to do cannot be read to find out what it
  does, and a command that parses and apologises has already cost the user the time it takes to
  type. Also recorded here, because they are the interface a script sees: **exit 0** for a command
  that did what it was asked, **1** for a command that ran and did not produce what it was asked
  for (a report the renderer refused, a check whose run directory holds no contract files, an
  ingest whose outline does not match its document), and **2** for a request that was wrong before
  anything ran (a bad flag, a package that does not load, a PDF that is not there). Every message
  on standard error names a fixing command, which is spec 3.1's rule about errors applied to the
  command line. Rejected alternative: a single `quaestor` command with a `--command` flag, which
  would make `--help` one wall of flags belonging to six different jobs.
- **2026-09-17 (Phase 12 pre-flight, commit C): what exit 1 means for `validate` is narrowed.**
  A run whose *checklist* partly failed now exits **0**, not 1: it wrote a report, and the report
  names the check it is missing. Exit 1 keeps its meaning — "ran and did not produce what it was
  asked for" — and `validate` still returns it for a report the renderer refused and for a subject
  that could not be run at all. The codes are unchanged; what changed is which outcome falls under
  which, and the operator signed it on the ground that a report naming its own gap did produce what
  was asked for. D-177 carries the decision and the sentence a caller needs.

## D-083. `--timeout` overrides the subject's wall-clock cap, not the provider's

- **Date:** 2026-09-07 (Phase 9)
- **Q:** Spec 3.14 lists `--timeout S` on `validate` without saying what it caps. There are two
  candidates: the subject's subprocess (`runtime.max_seconds` in `package.yaml`, enforced by the
  sandbox) and the provider's own call timeout (`ClaudeCLILLM.timeout_s`).
- **A:** The subject's. `--timeout S` replaces `runtime.max_seconds` on the loaded package for that
  run; the provider's timeout keeps its default and has no flag this phase.
- **Why:** The subject's cap is the one an operator actually hits — it is declared per package,
  five minutes by convention, and a real-sample run on a slower machine is exactly the case the
  runbook's Phase 9 puts in front of a human. The provider's timeout is a hung-process ceiling that
  no run should approach, and a flag for it would be a flag nobody has yet needed. Rejected
  alternative: making `--timeout` a total budget for the whole validation, which would need a clock
  threaded through the planner, the tools and the drafter, and would kill a run half-way with a
  report the renderer would then refuse — a failure mode strictly worse than the tool's own caps.

## D-084. One eligible-number tokenizer, and no way to call it without the package version

- **Date:** 2026-09-08 (Phase 9 follow-up, decided in Cowork)
- **Q:** The first live validation of `credit_default` produced a report in which all 140
  post-repair claims verified, and then refused to render it:
  `the rendered report does not satisfy docs/REPORT_SCHEMA.md: these numbers in the prose are
  covered by no verified claim and are not wrapped: ['1.0']`. The number is the `1.0` of "The
  champion in credit_default 1.0 is a linear-in-log-odds scorecard", section 2, which D-015
  excludes as the package version. The extraction pre-pass excluded it — the pipeline passes
  `package_version=loaded.spec.version` to `extract` — and the renderer's `uncovered_numbers` did
  not, because it called `masked_prose(body)` with the version argument defaulted away. Two
  callers of one rule, one of which could not see the whole rule. How is that closed?
- **A:** The rule becomes a function and the wrong call stops existing.
  `src/quaestor/verifier/tokens.py` holds the tokenizer (`NUMERIC_TOKEN_RE`, `numeric_tokens`,
  `token_value`, `line_spans`), the nine exclusion patterns of D-015, `ExcludedToken`,
  `Exclusion`, `exclusions_of`, `drafted_prose`, and **one** function that answers the only
  question any caller has: `eligible_numbers(markdown, *, package_version=None)`, returning the
  masked text, the section's lines, the eligible tokens with their offsets and line indices, and
  the tokens excluded with the class each fell into. All three callers read it — the pre-pass
  (`verifier/extract.py`), the repair loop's wrapper (`report/repair.py`) and the renderer's
  uncovered-number check (`report/renderer.py`) — and `uncovered_numbers`, `check_report` and
  `wrap_unverified` all take `package_version`, which `render_report` and `pipeline.validate`
  fill from `package.spec.version`. **`masked_prose` is deleted**, not deprecated: it was the
  spelling that made this defect possible, it had no caller left after the refactor, and a public
  function whose easy call is the wrong one is a defect waiting for its second author. Two
  narrower things are decided here as well. The version guard's trailing lookahead becomes
  `(?!\w|\.\d)` instead of `(?![\w.])`, because version `1.0` at the end of a sentence is written
  `1.0.` and the old guard left exactly the token this exclusion exists for eligible; `1.0.3` and
  `1.0x` are still not the version. And `check_report`'s new keyword is optional, so the Phase 9
  CLI test that calls it on a written report keeps working; the renderer, which is the caller that
  can refuse a run, always passes it.
- **Why:** Grounding precision is the number this project asks to be judged on, and the apparatus
  that protects it is a set of agreements about which numbers count: the pre-pass owns the
  denominator (D-064), a claim for an excluded token is dropped (D-077), an unverified number is
  wrapped and never deleted (D-073), and a report with an unwrapped uncovered number is not
  written. Every one of those is a statement about the *same set*, so the set has to be computed
  once. Three code paths computing it separately is not a style problem: it is two of the four
  agreements silently disagreeing, and the failure it produced was the worst available shape — not
  a wrong number in a report, but a correct report thrown away, after 17 model calls and 17
  minutes, over a number nobody had claimed. Deleting `masked_prose` rather than fixing its
  default is the part that makes this a fix rather than a patch: a default argument that is wrong
  for every real caller is a trap, and the version was defaulted away in `repair.py` too, where
  it had not yet cost anything. Rejected alternatives: giving `masked_prose` a required
  `package_version` parameter, which leaves three tokenizing loops in three modules and fixes only
  the argument that happened to be missing this time; and reading the version off the report's own
  front matter inside `uncovered_numbers`, which makes a checker parse the artifact it is checking
  and would have gone on being wrong for `wrap_unverified`, which has no report to parse.
  Measured: `tests/test_live_credit_attempt1.py` reconstructs sections 2 and 3 of the attempt from
  its recorded extraction prompts and asserts that the pre-pass and the renderer return the same
  token set for each; and that every section of the attempt, checked against its own post-repair
  verdicts, now has nothing uncovered, while section 2 checked *without* the version still reports
  `['1.0']` — the defect is fixed by the version reaching the check, not by the rule being
  relaxed. See `docs/DESIGN.md`, Phase 9 follow-up, and `docs/EVALUATION.md`.

## D-085. The extractor returns the line's number, not the line's text

- **Date:** 2026-09-08 (Phase 9 follow-up, decided in Cowork)
- **Q:** `ExtractedClaim.text` asks the model to copy back "the whole line the number appears on,
  copied exactly, citations included". On the first live run that made extraction **8 of 17 model
  calls and 63,865 of 92,196 output tokens** — 69% of everything the run generated — with the
  longest single call at **20,257 tokens and 197 seconds** (section 4, 44 claims), because a
  sentence carrying four numbers is re-typed four times, citations and all. The caller already has
  the prose it sent. Can the field go?
- **A:** Yes. `ExtractedClaim.text` is replaced by `ExtractedClaim.line`, a 1-based index into the
  prose the extraction prompt showed; the prompt prints that prose one numbered line per line
  (`numbered_prose`, and `numbered_lines` reads it back), and `extract` resolves each returned
  index against the lines it sent and fills `Claim.text` from it before the pre-pass runs. So
  `claims.json`, `CLAIMS_SCHEMA.json`, `Claim`, `VerifiedClaim`, the claim id — which hashes
  `[section, text, value]` — and every appendix are unchanged: the text is still the sentence, it
  is simply no longer transmitted. A line number that is not in the prose is treated exactly as an
  ineligible token's claim is: the claim is dropped, counted in `n_from_model`, and published in
  the exclusion list under `extractor_returned_excluded_token` (D-077). D-077's second matching
  pass survives unchanged and now covers the misnamed-line case: a claim whose own line has no
  token of its value is offered to any unfilled token of the section, so naming the wrong line
  costs the report nothing. The offline fake and `eval/verifier_eval.py`'s fake extractor read the
  numbers back out of the prompt they were sent, which is what a competent extractor does.
- **Why:** The field was a way for the answer to disagree with the prose, and it was the single
  largest cost in the run. Both halves of that matter and the first is the reason to prefer the
  index even at equal cost: D-063 already refuses to ask a model for `section`, `id` and `source`
  because "asking a model for a value the caller can compute is a way of being told a different
  one", and `text` is that value — the pre-pass had to normalise whitespace and fall back to
  substring matching precisely because the copy came back slightly changed. An index is verifiable
  in one comparison. The cost is the reason it was found now rather than in Phase 7: nothing in
  the offline suite pays for output tokens, so a prompt that asks a model to re-type its input is
  free in every test and 69% of the bill on the first real run. Rejected alternatives: asking for
  a character offset, which is what the drafter's own thousands separators make unreliable and
  which D-064's note already rejected for the pre-pass; and keeping `text` and asking for a
  truncated prefix, which trades a whole failure mode for a smaller one and leaves the claim id
  depending on how the model truncated. Not claimed here: how much this saves live. The number
  above is what the field cost on one run, and the saving will be measured on the next one rather
  than estimated in this entry.

## D-086. `L2` is two overlaps read against a within-train baseline, and only the identifier is high

- **Date:** 2026-09-08 (Phase 9 follow-up, decided in Cowork)
- **Q:** The first live validation raised `F-001 L2` at severity **high** on the real
  `credit_default` sample: 1.2556% of the test rows carried a feature vector that also appears in
  the training split, against `threshold.L2.overlap` of 0.5%. The panel's features are coarse
  integers and small ratios — delinquency counts, six-month means of rounded bills — and its
  identifiers are disjoint by construction: the split is a random 70/30 over `client_id`. Is a
  repeated feature vector contamination?
- **A:** Not on its own, and the a-priori reason is that **identical feature vectors from distinct
  clients are not contamination**: on discrete data two different subjects can write the same row,
  and the rate at which that happens is a property of the feature set, not of the split. So
  `check_leakage` computes three quantities and reports all of them: `leakage.overlap.ids`, the
  share of test rows whose *identifier* — the declared `id_column`, and the period as well for a
  hazard panel, which is what `key_columns` returns — also identifies a row of train;
  `leakage.overlap.features`, the share whose *feature vector* appears in train, which is the
  Phase 5 quantity unchanged; and `leakage.duplicates.train`, the share of train rows whose
  feature vector occurs more than once inside train, which is what coincidence looks like in this
  dataset measured on the one split that cannot be contaminated by itself. The `L2` candidate
  follows: **severity high** when the identifier overlap exceeds `threshold.L2.overlap`, because
  the same row is in both splits under the same name; **severity medium** when the feature overlap
  exceeds `max(threshold.L2.overlap, 2 × leakage.duplicates.train)`, because a re-keyed copy looks
  exactly like this and a coincidence does not; otherwise **no candidate**, and the three numbers
  are reported. `leakage.overlap` stays in the store as an alias of `leakage.overlap.features`:
  the Phase 1 golden report cites it, `tests/test_tools_clean.py` requires every golden Appendix B
  name to resolve in a real run, and a logical name that stops resolving is a committed citation
  that dangles. `threshold.L2.overlap` keeps its value and its meaning; nothing was loosened.
- **Why:** The screen was measuring the feature set's granularity and calling it contamination,
  which is the highest-cost mistake a validation copilot can make — a severity-high finding that
  says the held-out split is not held out invalidates every metric in the report. And it was not
  detectable from the synthetic control: `synthetic.py` draws continuous features, so the clean
  panel's feature overlap is exactly 0.0 and the rule looked exact. The baseline is a *measured*
  null rather than a chosen constant for the same reason the exclusion list is published: the
  question "is 1.2556% a lot?" has no answer that does not come from the data, and the within-train
  duplicate share answers it in the only units that mean anything. The factor of 2 is deliberately
  blunt (`DUPLICATE_MULTIPLE`), and it is a factor rather than a test because the quantity it
  guards is a false-alarm rate rather than a p-value; on the attempt's own panel the cross-split
  share was 1.2556% — `leakage.overlap`, committed with the run — against a within-train share of
  1.1619% recomputed from that run's `data_train.csv`, which is not committed (D-087): a ratio of
  1.08 where the rule asks for more than 2, and the margin the constant exists to refuse.
  Splitting the severity is the second half: the study's
  `L2` recipe copies rows, and whether it re-keys them is the difference between certain
  contamination and probable contamination, so it is the difference between high and medium rather
  than between fires and does not. Rejected alternatives: raising `threshold.L2.overlap` until the
  real sample passed, which is choosing the number that makes the run green and would hide a real
  3% contamination on a coarser panel; dropping the feature-vector screen for the identifier one,
  which loses the re-keyed variant of the seeded defect entirely; and hashing the identifier into
  the feature vector, which makes every row unique and turns the screen off without saying so.
  Measured: `tests/test_tool_rules.py` now carries both branches of the seeded shape (3% of test
  rows copied into train — ids kept, high, identifier overlap 3.0%; ids re-keyed, medium,
  identifier overlap 0.0% and feature overlap 3.0%), the clean synthetic control at 0.0 / 0.0 /
  0.0 with the alias equal to the feature overlap, and the attempt's case as a discrete panel:
  feature overlap **1.2667%** against a within-train duplicate share of **1.2857%**, identifiers
  disjoint, **no candidate** — where the Phase 5 rule raises `L2` high. The clean synthetic
  `credit_default` still yields exactly `{E1 low}` (D-017) and `msr_prepayment` exactly `{}`
  (D-047), each now over three more artifacts.

## D-087. What of the first live run is committed, and what is kept outside the repository

- **Date:** 2026-09-08 (Phase 9 follow-up)
- **Q:** The operator's first live validation is committed as `eval/results/first-live/`, so that
  `docs/EVALUATION.md` and `tests/test_live_credit_attempt1.py` read the run rather than a
  retelling of it. The run directory as written holds the trace, the 17 cassettes, the 121-entry
  artifact store, `run/*.json` — and `run/data_train.csv`, `run/data_test.csv`,
  `run/predictions_{train,test}.csv` plus the four `run.data_*` / `run.predictions_*` **artifacts**,
  which are byte-for-byte the same rows. `CLAUDE.md`: real data is never committed. What goes in?
- **A:** The directory is named `credit-attempt1` — the run is one attempt of several the runbook
  expects, and the report it would have written does not exist — and it is committed without any
  row-level file: not the four CSVs under `run/`, which the Cowork decision names, and **not the
  four row-level CSV artifacts either**, which it does not name but which hold the identical rows
  under a content address. Everything else goes in: `trace.jsonl`, `cassettes/`, `run/*.json`
  (splits, features, metrics, model_summary — aggregates and coefficients, as the Phase 3
  follow-up committed for the same subject), and `artifacts/` including `index.json`, so every
  logical name the trace cites is still listed with its hash, its kind and its summary. The eight
  excluded files are moved to `~/code/data-raw/credit/first-live-attempt1-rows/`, outside the tree
  and inside `.gitignore`'s guard, rather than deleted. The consequence is stated rather than
  hidden: a citation to `run.data_train`, `run.data_test`, `run.predictions_train` or
  `run.predictions_test` resolves in `index.json` and has no payload file in the repository. No
  report claim cites one — all four are `kind: table` with no value — and no test reads one.
- **Why:** The instruction excluded `run/*.csv` in order to keep client rows out of the
  repository, and the same rows arrive a second time through the artifact store, so honouring the
  words and not the reason would have committed 2.8 MB of exactly what was being excluded. The
  precedent is the subject's own: the Phase 3 real-sample commit shipped
  `subjects/credit_default/artifacts/real/*.json` as "aggregates and coefficients only, no rows".
  Keeping `index.json` complete rather than pruning the four entries is deliberate: the index is
  the run's inventory, and an inventory with four rows quietly removed misrepresents what the run
  computed, while an inventory whose four largest payloads are absent from the repository is a
  fact a reader can see. Rejected alternatives: committing the row files because the UCI credit
  dataset is public, which puts 30,000 rows of client data in a repository whose constitution says
  no rows and invites the same argument for the next dataset; and dropping `artifacts/` entirely,
  which would leave the trace's artifact hashes citing nothing.

## D-088. A tool the bounded loop asked for and that raised is the step's failure, not the run's

- **Date:** 2026-09-08 (Phase 9 follow-up 2)
- **Q:** The second live validation (`eval/results/first-live/credit-attempt2/`) ran the plan
  clean, spent its one model call, and the loop asked for `check_stability` on `credit_default`,
  which declares no `regime.column`. The tool raised `ToolError`, the exception left
  `validate()`, and the command exited 1 after 14 tool calls with no report — where the pipeline
  had every artifact it needed to draft one. Does a `ToolError` from a loop-requested call fail
  the run?
- **A:** No. `follow_up_plan` catches it: the step is recorded and traced with `accepted: true`,
  `executed: false` and the tool's message on a new `error` field, the message is quoted back to
  the model in the next step's prompt, the step counts against the maximum of four, and the
  pipeline goes on to promote, draft, verify, repair and render with what it has. `PlanStep` gains
  `executed` and `error`, and `plan_step` gains the same two fields on the trace, so a reader and
  `eval/score.py` can tell a step the loop refused from a step the loop accepted and the tool
  could not answer. `pipeline.py`'s `tools_run` counts only the steps that executed, so a check
  that raised is not listed in `checks_without_candidates` as having screened for anything.
  **Nothing about the rule-based plan changes**: a `ToolError` from one of its calls is still the
  run's failure and still exits 1, because the rule-based plan is what a validation of this
  package must check, and a validation missing one of its own checks is not a report to render.
- **Why:** The asymmetry is the whole decision. The rule-based plan is derived from
  `package.yaml`; if `compute_metrics` cannot run, the report would have no metrics section worth
  reading, and failing loudly is right. The loop is the model's own extra question, bounded at
  four steps and refusable on four grounds already — a fifth outcome, "the tool tried and could
  not", belongs in the same place as the other four: on the trace, in the prompt of the next step,
  and not in the exit code. The alternative the attempt demonstrated is the worst of both: 17
  minutes of a live run in the first attempt and a full plan in the second, discarded over a
  question the model was free to ask and free to be told no about. Rejected alternatives:
  converting the `ToolError` into a refusal with `accepted: false`, which would lose the
  distinction between a call the planner would not make and a call the tool could not answer —
  the registry already wrote a `tool_call` event with `ok: false` for the second and none for the
  first, and the two records should agree; and catching the error inside `pipeline.py`'s
  `_execute`, which would leave `follow_up_plan`'s own `execute=` callers — the tests, and Phase
  12's study harness — with the defect still in them.
- **2026-09-17 (Phase 12 pre-flight, commit C): the last sentence of the answer above is
  reversed.** "Nothing about the rule-based plan changes: a `ToolError` from one of its calls is
  still the run's failure and still exits 1" held for nine days and is now false for every call of
  the checklist but `run_model`. The argument that overturned it is this entry's own, applied to a
  fact this entry did not have: the loop's exemption was granted because seventeen minutes of a
  live run had been discarded over a question the model was free to ask, and a checklist check
  that raises after eleven others have run discards the same eleven checks' worth of artifacts and,
  under `full_agent`, the paid model call as well — over a question the *package* was free to pose.
  What is kept is the asymmetry's real content: a validation missing one of its own checks is not a
  complete report, so the missing check is named in Appendix D, excluded from `tools_run` and
  therefore from `checks_without_candidates`, carried on the trace with its message, and said aloud
  by section 1. `run_model` keeps the old rule for the reason this entry gives for the checklist
  generally, and it is the only call that does. The sentence above is left as recorded; D-177
  carries the reversal.

## D-089. The loop is offered only the tools that apply to the package, and refused the others

- **Date:** 2026-09-08 (Phase 9 follow-up 2)
- **Q:** D-088 stops a tool that raises from killing the run, but the attempt's request was
  answerable before it was made: `check_stability` cannot say anything about a package with no
  regime column, and the plan already knows that, because the same condition decides whether the
  rule-based plan calls it. The loop was shown all nine schemas. What is it offered?
- **A:** Only the applicable ones. `inapplicable_reason(tool, package)` is the one definition:
  `check_stability` needs a `regime.column`; `run_scenarios` needs a `discrete_time_hazard`
  subject with a `scenarios` block; and `run_model` is never applicable, which is spec §3.12's
  own rule read as an applicability question rather than an argument question. `loop_prompt`
  filters the catalogue by it, and `validate_action` applies it as a fourth refusal —
  `"not applicable to this package: <why>"`, traced `accepted: false`, fed back to the next step.
  The order of the four rules is fixed and the new one is **last**: the tool exists, its `Args`
  take the arguments, no path leaves the package, and only then does it apply. So spec §3.12's
  three named refusals keep their own messages — `run_model` with an invented `entrypoint` is
  still caught by the closed `Args` that names the field, and a path pointing at `/etc` is still
  caught by the rule that says so.
- **Why:** A menu that offers a tool which cannot run is a prompt that invites the mistake and
  then charges a model call for it; the attempt paid 693 output tokens and $0.10 to be told
  something `package.yaml` already said. Filtering the menu is the fix and refusing the request is
  the second line of defence, because a model is free to name a tool that is not on its list and
  the refusal has to be legible when it does. Keeping the applicability rule last, rather than
  first where it would be cheapest, is deliberate: `run_model` is the only tool with a path
  argument, so an applicability-first order would make the path rule unreachable through
  `validate_action` and would replace two precise messages with one vague one. Rejected
  alternatives: leaving the menu whole and relying on D-088's catch, which spends a model call and
  a tool call to learn a static fact; and deriving applicability from whether the rule-based plan
  called the tool, which would refuse every follow-up that was worth making — the loop exists to
  call `compute_metrics` a second time.

## D-090. The loop is shown what the plan already ran, not only what it raised

- **Date:** 2026-09-08 (Phase 9 follow-up 2)
- **Q:** The attempt's `why` was "the plan only compared regimes on the fitting split, so
  regime-dependent degradation out of sample is still untested" — a sentence about a call the plan
  never made, on a package that has no regimes. The Phase 8 prompt showed the candidate findings,
  the artifact prefixes and the tool schemas, and said the plan "has already run" without saying
  what it ran. What should the model reason from?
- **A:** The run. `loop_prompt` gains two blocks. **What the plan called**: one line per call,
  `- <tool>(<args as JSON>) -> <defect classes raised, or "no candidate">`, built by
  `completed_calls(plan, results)` from the same two lists `pipeline.py` already has. **What
  earlier steps of this loop did**: one line per step, saying whether it was refused and why,
  accepted and failed and with what message, or accepted and run — which is where D-088's error
  and D-089's reason reach the model. The instruction that the loop is for a follow-up question
  about what the candidates show, and not for repeating the plan, stays and is stated in the same
  paragraph. The prompt itself becomes a function rather than a `format` call at the call site, so
  a test can send the loop exactly the bytes a recorded run was sent.
- **Why:** A planner told only what was *found* cannot tell a check that was not run from a check
  that ran and found nothing, and those are the two cases a follow-up should be chosen between. It
  is the same argument D-063 makes about the extractor from the other side: do not ask a model for
  something the caller already has — here the caller has the plan and its results and was
  withholding them. The history block is the cheaper half of the same idea: four steps with no
  memory of the first three is four chances to make one mistake. Rejected alternatives: passing
  the full `ToolResult` summaries, which would put every number the plan computed into the prompt
  and make the loop's cost scale with the store rather than with the plan; and re-sending the
  whole conversation as turns, which the `LLM` protocol does not have — `complete(prompt, ...)` is
  one turn by construction, and the history block is how a bounded loop keeps state inside it.

## D-091. A rule that derives its bound stores it, and the prompt names the section's candidates

- **Date:** 2026-09-08 (Phase 9 follow-up 3, decided in Cowork)
- **Q:** The third live validation of `credit_default` rendered a report — 19 model calls, 159
  claims, grounding precision 0.9816 pre-repair and 1.0000 post — and two of its sentences are
  false. Section 3: "The measured share is above that bound, so the test split is not a fully
  clean holdout under the package's own standard, and this is recorded as a finding rather than
  as an observation." Section 6: "No finding was raised for the credit_default version 1.0 model
  package in this section." Both are drafted prose, both verified, and they contradict each other.
  Whose defect is it?
- **A:** The tool's, twice over. First, the bound the `L2` feature-overlap rule actually applied
  is `max(threshold.L2.overlap, 2 x leakage.duplicates.train)` = 0.02324 on that panel (D-086),
  and it was **not an artifact**. The drafter was shown `threshold.L2.overlap` = 0.005 and
  `leakage.overlap.features` = 0.01256, and comparing the two is the correct arithmetic on the
  only two numbers it had: 0.01256 does exceed 0.005. So every rule that derives an effective
  bound now stores it —
  `check_leakage` writes `threshold.L2.overlap.features_effective`, `tools/thresholds.py` holds
  `effective_name(base, rule)` as the one spelling of the pattern, and the candidate's evidence
  cites the derived bound as well as the declared one. Section 3's brief tells the drafter which
  arm is read against which bound and forbids comparing a feature-vector overlap with the declared
  threshold. Second, the prompt said "(none: every check that ran on this section's material
  raised nothing)", which states a fact and not its consequence; it now says, word for word,
  `candidates raised for this section: none -- describe nothing as a finding`, and where there are
  candidates it lists them, numbers them, and adds that they are the only findings the section may
  describe. `DRAFT_INSTRUCTION` gains the matching rule.
- **Why:** Only the drafter can put two contradictory sentences in one report, but it did not
  invent either number and it did not misread the rule it was given — it was given the wrong rule.
  A threshold that decides a candidate is in the store by construction (`Thresholds.artifact` is
  the only way a tool reads one, Phase 5), and D-086 broke that invariant the moment it made one
  bound a function of the data: the number the screen applied existed only inside
  `_contamination`'s local scope, so no report could cite it and no reader could check the
  comparison. Storing it restores the invariant rather than patching the prose. The prompt half is
  the cheaper half and is not sufficient on its own: a drafter told "describe nothing as a finding"
  while holding an exceedance it can demonstrate is being asked to write a sentence it can see is
  wrong, which is how a competent model is made to look incompetent. Rejected alternatives: telling
  section 3 not to mention the overlap at all, which suppresses the one number a validator most
  wants to see and would have hidden D-086's own false alarm; and having the renderer cross-check
  section 3's prose against `findings.json` for the word "finding", which is a grep over natural
  language standing in for a fact the prompt could simply have carried.

## D-092. `compute_metrics` writes the developer-threshold table; the runtime cap leaves `threshold.*`

- **Date:** 2026-09-08 (Phase 9 follow-up 3, decided in Cowork)
- **Q:** Section 4.4 of the third live report carries a table headed "one row per threshold
  declared in package.yaml". Two of its six rows are wrong. `PSI, maximum 0.25` says
  "Not recomputed in the artifacts available to this section / Not evaluated here" while sections
  1 and 3 of the same report both cite `psi.max` = 0.003083; and `Wall-clock seconds, maximum 300`
  is a row of a performance-threshold table describing how long the subject may run. What went
  wrong?
- **A:** The drafter was asked to assemble a table it did not have the artifacts for, out of a
  family whose membership was decided by a name prefix. Both halves change. (a) `compute_metrics`
  writes `thresholds.evaluation`, a **table artifact**: one row per bound `package.yaml` declares,
  with `metric`, `split`, `bound`, `value` and `result` — `pass`, `fail`, or `not evaluated` with
  the reason in the value cell — computed by the same loop that raises `T1`, so the table and the
  rule cannot disagree. Section 4's brief tells the drafter to write `[[table:thresholds.evaluation]]`
  on a line of its own and *not* to assemble the table, and section 4's selector is widened to
  every `threshold.*` and every `psi.*` scalar so that the prose around the table can cite what it
  discusses. (b) The subject's wall-clock cap moves from `threshold.package.max_seconds` to
  **`runtime.max_seconds`**, out of the `threshold.*` family altogether, and section 1's selector
  gains `runtime.` so the cap is still citable where it belongs.
- **Why:** D-013 already says the drafter must not retype a table the store holds, on the grounds
  that grounding precision should measure prose and not transcription. The developer-threshold
  table is the table a validation report is most often read for, and it was the one table the
  drafter was still being asked to compose — from scalars whose relationship to one another it had
  to infer. It inferred wrongly in the one direction that matters: it reported a threshold as not
  evaluated when the rule had evaluated it and it had passed, which is a false negative in the
  report about a check that ran. The naming half is the same argument about inference: PSI was
  missing from section 4 because `threshold.package.` matched it and `psi.` did not, and the
  runtime cap was present because `threshold.package.` matched *it*. A prefix is not a taxonomy,
  and `runtime.max_seconds` is the name `package.yaml` gives the thing. Rejected alternatives:
  adding `psi.max` alone to section 4's selector, which fixes this report and leaves the next
  metric to be discovered the same way; and keeping the drafter's table and repairing it in the
  loop, which spends model calls to reconstruct a table the tool already computed.

## D-093. What a run is called, what model wrote it, and what a token costs

- **Date:** 2026-09-08 (Phase 9 follow-up 3, decided in Cowork)
- **Q:** Three things the third live run's own record gets wrong about the run. Its front matter
  says `model: claude-cli`, which is the adapter; the trace's own `llm_call` events say
  `claude-opus-5[1m]`. Its `run_id` is `credit_default-full_agent-d03b07c6` — the same identifier
  the **first** attempt carried, seventeen minutes and one build earlier, because the id hashes
  the package, the version, the configuration, the data mode and the seed and nothing else. And
  Appendix C reports **38 tokens in for 19 calls** against 104,675 out, while the run's own
  cassettes carry 176,851 input tokens across `input_tokens`, `cache_creation_input_tokens` and
  `cache_read_input_tokens`.
- **A:** Each is fixed where it is produced. (a) `ReportInputs` gains `model_id`, filled by
  `pipeline._model_id` from the `model` field of the run's own `llm_call` events; the front matter
  and the scope block print it, and Appendix C gains a `provider adapter` row carrying the
  adapter's name beside a `model` row carrying the id — `none: no model answered` under
  `rules_only`, which is a different fact from "the adapter was called `fake`". (b) `_run_id` gains
  the UTC second the run began, formatted `%Y%m%dT%H%M%SZ` and placed before the input hash, so an
  id reads `credit_default-full_agent-20260908T063934Z-d03b07c6`: the hash still says two runs had
  the same inputs and the stamp says they were different runs. The second comes from `generated`
  where a caller pins it, so a byte-stable test stays byte-stable. (c) `ClaudeCLILLM` sums the
  three input-token fields.
- **Why:** All three are the record failing to describe the run, which is the one thing this
  project's evaluation rests on. The model id matters most: `claude-cli` is a subprocess, not a
  model, and a published study that reports which configuration produced which grounding precision
  has to be able to say which model produced it — the adapter is what you re-run, the id is what
  you compare. The run id matters second: `eval/results/first-live/credit-attempt1/` and
  `credit-attempt3/` are two directories whose every file, trace event and claim carries the string
  `credit_default-full_agent-d03b07c6`, so an id that was introduced to join a report to its trace
  joins each report to two traces. And the token count matters because Phase 12 publishes a cost
  per report: `input_tokens` alone is what the prompt cache neither wrote nor read, which for a CLI
  run is a rounding error, so a cost table built on it says a report was drafted from nothing.
  Cached input is cheaper than fresh input and it is not free. Rejected alternatives: reading the
  model id out of the cassettes at render time, which would make the report depend on a recording
  layer that a live run does not use; making the run id a random string, which discards the
  property that two runs of one set of inputs are recognisable as such; and reporting the three
  token fields separately in Appendix C, which puts the arithmetic of a provider's billing into
  every report to save one addition.

## D-094. Renderer tables print measures at four significant figures and counts as integers

- **Date:** 2026-09-08 (Phase 9 follow-up 3, decided in Cowork)
- **Q:** The third live report's decile table prints `0.6855555556` and `3.098945254`; its prose,
  four lines below, prints `0.4952` and `0.755`. Both are correct and they are not written alike.
  What precision does an expanded table print at?
- **A:** Four significant figures, the same the drafter is shown (spec §3.11), with any cell whose
  value is integral printed as an integer — `900` is a count and not a measurement to four
  figures. `_table_cell` does it, and it recovers the type first: a table artifact's payload is
  canonical text, every cell rendered through `%.10g` by `ArtifactStore.put`, so the cells come
  back as strings and a period label such as `2024-01` has to survive being printed as it stands.
- **Why:** One number, two spellings, and the reader cannot tell which one the validator meant.
  The prose's figure is the claim — it is what the verifier matched and what Appendix A records —
  and a renderer block beside it showing four more digits invites the arithmetic to be checked
  against the wrong one. Ten digits also assert a precision no statistic in this report has: a
  decile event rate over 900 rows is known to about a percentage point. Rejected alternatives:
  printing tables at the artifact's full stored precision and rounding the prose to match, which
  inverts the rule that the drafter writes what it is shown; and rounding inside `stats.py` before
  the artifact is stored, which would throw away precision the claims matcher needs — the artifact
  keeps every digit, and only the rendering of it is a reader's number.

## D-095. The sign check and the ablation are evidence, and neither raises anything

- **Date:** 2026-09-08 (Phase 9 follow-up 3, decided in Cowork)
- **Q:** Section 2 of the third live report observes that utilisation enters the champion with a
  negative coefficient "against the standard view that a borrower drawing more of an available
  line is more likely to default", offers a plausible reading, and says the reading is the
  validator's own inference. It is the most useful paragraph in the report and it rests on nothing
  the run computed. What evidence should a validator have for it?
- **A:** Two families, in the tools that already ask the neighbouring question, and neither raises
  a candidate. `check_collinearity` stores, per retained feature,
  `sign_check.<feature>.coef_sign`, `sign_check.<feature>.univariate_direction` — the sign of that
  feature's own single-feature AUC on the fitting split minus a half — and
  `sign_check.<feature>.agrees`, plus `sign_check.n_disagreements`. `challenger_compare` stores
  `ablation.<feature>.delta_auc`, the change in held-out AUC when the champion's functional form is
  refitted without that feature, against `ablation.baseline_auc`, the refit on every feature; above
  `MAX_ABLATION_FEATURES` = 25 the whole ablation is skipped and `ablation.skipped` says so.
  Section 2's selector gains both prefixes and its brief asks that, for any coefficient whose sign
  disagrees with its univariate direction, the ablation delta be stated as the measure of how much
  the disagreement matters.
- **Why:** "The sign is wrong" and "the sign is wrong and it costs two AUC points" are different
  statements to a model developer, and only the second can be acted on. The placement is the
  decision: a near-dependency among the columns is *why* a fitted coefficient takes a sign its own
  marginal relationship contradicts, so the sign check belongs beside the VIFs rather than in a
  tool of its own, and an ablation is a refit-and-compare, which is what `challenger_compare`
  already is. That neither raises a candidate is the other half: a sign flip is frequently the
  model correctly conditioning on the other columns, and a rule that fired on it would generate
  exactly the kind of false alarm D-086 exists to refuse. The ablation's baseline is stored beside
  the deltas because the refit is **not** the champion's own fit — the validator never imports the
  subject (spec §3.6) — so subtracting a delta from `metrics.test.auc` would mix two fits, and the
  number to subtract from is named. Rejected alternatives: comparing the coefficient's sign against
  a developer-declared expected sign, which no `package.yaml` field carries and which would be a
  change to the package schema for a question the data can answer; and permuting the feature
  instead of refitting, which measures the fitted model's reliance rather than the feature's
  contribution and would have given the flipped coefficient credit for the variance it removes.

## D-096. Section 6 carries `### Open items`, findings or none

- **Date:** 2026-09-08 (Phase 9 follow-up 3, decided in Cowork)
- **Q:** The third live run raised no finding, and its section 6 is four sentences saying so —
  while section 2 had just reported a coefficient whose sign contradicts subject-matter
  expectation and section 3 a feature-vector overlap of 1.256% that the within-train duplicate
  share explains but does not settle. Both are things a model developer should answer. Where do
  they go?
- **A:** Into `### Open items`, a level-3 subsection at the end of section 6, present in every
  report. One line per observation, each citing the artifact it rests on and each naming an owner —
  `model developer` unless the artifacts name someone else — and one sentence saying so where there
  is genuinely nothing. The drafter is asked for it in section 6's brief, with the utilisation sign
  and the feature overlap named as the examples; `renderer._findings_section` lifts whatever the
  drafter wrote under the heading and re-places it last, supplying the heading and `NO_OPEN_ITEMS`
  where the drafter omitted it, exactly as it supplies a finding's heading under D-071; and
  `check_structure` refuses a report whose section 6 has no such heading.
- **Why:** A finding in this project is a rule firing, and rules are deliberately narrow — the
  whole seeded-defect study measures how narrow. So "no findings" is a statement about twelve
  defect classes and not about whether the model is sound, and a section 6 that says only "no
  finding was raised" invites the reader to draw the second conclusion from the first. The
  observations were in the report already; what was missing was a place where a developer is asked
  to respond to them, which is what makes an observation actionable and what SR 11-7-shaped
  reporting is for. The heading is required rather than conditional because an optional section
  that is usually absent teaches a reader to skip it. It is checked in `report/schema.py` and
  **not** added to `REPORT_SCHEMA.json`: that file's heading list is the eleven level-2 headings
  and is pinned to the Phase 1 golden report under D-011, this is a level-3 rule, and the golden
  is a specification of shape that this decision does not change. Rejected alternatives: promoting
  open items to `info`-severity findings, which would put them in `findings.json`, in the severity
  counts and in the study's precision denominator, so a helpful observation would score as a false
  alarm; and leaving them in sections 2 and 3 where the drafter already wrote them, which is where
  they were and is why nobody was asked to answer for them.

## D-097. Appendix A counts claims rewritten and numbers removed separately

- **Date:** 2026-09-08 (Phase 9 follow-up 3)
- **Q:** Appendix A of the third live report says "1.0000 after 0 repaired claim(s)" — of a run
  whose trace carries two `repair` events, one removing `9.982` and `6` from section 3 and one
  removing `50` from section 4. The sentence is true of the field it counts and false about the
  run: the repair loop did something, three times.
- **A:** The sentence becomes "after N claim(s) rewritten and M number(s) removed from the prose".
  N is what it always was, the distinct `(section, claim_id)` pairs of `claims.json`'s `repairs`;
  M is read off the `removed` field of the run's `repair` trace events, which is where D-073 put
  it.
- **Why:** A repair has two outcomes and `claims.json` records only one. A claim that was rewritten
  — corrected, or given the citation it was missing — is paired with what replaced it and becomes a
  `repairs` row; a number the drafter removed instead has no `after` side to pair with, and D-073
  deliberately records it on the trace event alone rather than inventing a half-empty row. That was
  right, and the appendix was reading only half the record. Taking M from the trace rather than
  adding a field to `claims.json` keeps `CLAIMS_SCHEMA.json` — pinned to the golden under D-011 —
  untouched, and the renderer already holds the events for Appendix C. Rejected alternative: adding
  a `removed` list to `claims.json`, which is a schema change under D-011's procedure for a number
  the trace already carries and the renderer already reads.

## D-098. `package.yaml` gains `use`, and section 4 says which rule ordered it

- **Date:** 2026-09-08 (Phase 9 follow-up 3, decided in Cowork; a `package.yaml` addition)
- **Q:** Spec §3.11 orders section 4 by the event rate: calibration before discrimination when the
  observed rate is below `rule.calibration_first_event_rate`. That asks the data what the model is
  for. `msr_prepayment`'s hazard probabilities are multiplied by a surviving balance to value a
  servicing strip, so calibration leads whatever its rate happens to be;
  `credit_default`'s scorecard ranks applicants. Is the event rate the right question?
- **A:** Not the first one. `PackageSpec` gains an optional, nullable `use: ranking | probability |
  both`. Section 4 orders itself by two rules in order: a declared `use` of `probability` or
  `both` puts calibration first whatever the event rate is; otherwise the rare-event rule decides,
  as before. `section_four_order` returns the answer **and** the ground for it as a
  `SectionOrder`, the report states which one applied, and
  `rule.calibration_first_event_rate` is cited only where it was the ground — where the declared
  use decided, that scalar is dropped from section 4's selector, so the drafter cannot cite a
  number that decided nothing. `credit_default` declares `use: ranking`, `msr_prepayment`
  `use: probability`; a package that declares neither behaves exactly as it did before.
  `docs/REPORT_SCHEMA.md` §3 and §10 carry it.
- **Why:** This is the change `CLAUDE.md` says to stop and ask about — a change to `package.yaml`
  after Phase 1 — and it was asked and decided in Cowork on 2026-09-08. The substance: an event
  rate is a property of the sample and the ordering question is a property of the model's use, and
  the two only coincide because rare events are usually modelled for their level. A 22% default
  rate does not tell you whether the bank ranks applicants or prices them. Making the field
  optional and nullable is what keeps it from being a schema break: every existing package, every
  fixture and every seeded variant of Phase 10 keeps the Phase 8 behaviour. Returning the reason
  beside the answer, and withholding the artifact when it was not the reason, is D-091's lesson
  applied before the fact: the surest way to stop a drafter citing a number as a justification it
  did not serve is not to hand it the number. Rejected alternatives: inferring the use from
  `model_type`, which makes every hazard model calibration-first and every classifier not, and is
  false in both directions — a hazard model used only to rank refinance candidates exists, and so
  does a scorecard whose probabilities go into an expected-loss calculation; and leaving the
  ordering to the event rate and letting the drafter argue in prose that calibration matters more,
  which is a decision about the report's structure taken by a model call.

## D-099. Exponent notation is one token, and the exponent moves the tolerance

- **Date:** 2026-09-08 (Phase 9 follow-up 4, decided in Cowork)
- **Q:** The fourth live validation of `credit_default` rendered — 22 model calls, 167 pre-repair
  claims, grounding precision 0.9641 rising to 1.0000, zero findings, exit 0 — and **all six of
  its pre-repair failures are one defect**. `NUMERIC_TOKEN_RE` had no exponent form, so
  `1.92e-05` tokenised as `1.92` and, after the lookbehind refused `-05`, as `05`: two claims, one
  of which asserts a mantissa the artifact does not hold (0.0000192) and one of which asserts five.
  The three literals `1.92e-05`, `-5.589e-05` and `9.982e-06` produced the six `unattributed`
  claims (1.92, 5, -5.589, 5, 9.982, 6), and attempt 3's two removals of `9.982` and `6` were the
  same defect a run earlier, recorded then as an extraction miss. The drafter writes the exponent
  form because that is what `json.dumps` prints for a value of 1.9e-05 at four significant
  figures, which is what the prompt shows it. What is a number in the prose?
- **A:** One token, mantissa and exponent together, with the tolerance held to the mantissa's
  precision at the exponent's scale. `NUMERIC_TOKEN_RE` gains `(?:[eE][+-]?\d+)?` before the per
  cent sign; `token_value` needed no change, because `float` reads the form already; and
  `match._decimals_of_token` subtracts the exponent from the mantissa's decimal count, so
  `1.920e-05` writes three decimals of a mantissa scaled by 10^-5, claims 10^-8, and is held to
  half of that. Spec section 0's default for the unit is still the ceiling (D-069), so the rule
  only ever narrows. The two other tokenizers in the tree — the offline fake's `_TOKEN_RE`, which
  is deliberately a copy because a provider may not import the report layer, and
  `tests/test_golden_spec.py` check 7's literal — move with it. `eval/verifier_eval.py`'s fake
  extractor gains the citation mask the offline fake always had: it tokenised raw lines, and
  `[[art:2e30351e:answer]]` holds `2e30351`, which is `inf`.
- **Why:** This is the whole of the run's lost grounding precision, and it is the shape D-084 and
  D-091 have now produced three times: one part of the pipeline knowing something another does not.
  Here the drafter was taught to write a form the verifier could not read, by the same codebase, in
  the same run — the prompt's own JSON is where `1.92e-05` came from. Splitting the mantissa from
  the exponent is worse than failing to tokenise at all: a number nobody can verify is at least
  reported as unverified, whereas `05` is a *claim of five* that the report never made, and the
  repair loop is then asked to fix a sentence that is correct. Holding the mantissa's decimals
  against an unscaled tolerance would have been the other error, and the worse one: `0.0005`
  against a value of 1.9e-05 verifies anything of that order, which is D-069 read backwards.
  Rejected alternatives: teaching the drafter never to write exponent notation, by rounding the
  prompt's own values into positional form, which loses four significant figures of a small number
  and leaves the tokenizer unable to read a form a live model may write anyway; excluding exponent
  literals from the claim set, which lowers the denominator by hiding the numbers hardest to check;
  and normalising the prose after drafting, which edits the sentence the claim id hashes. Measured:
  `tests/test_verifier_extract.py` asserts one token per literal and one claim per line for the
  run's own two sentences, over both the extractor's line-index path (D-085) and the pre-pass;
  `tests/test_verifier_rounding.py` verifies all three of the run's claims against the artifacts it
  cited, verifies `1.920e-05` against 1.9204697640939905e-05 (a difference of 4.70e-9 against a
  tolerance of 5e-9) and refuses `1.92e-04`; `tests/test_offline_llm.py` asserts the fake returns
  one claim for the form. See `docs/EVALUATION.md` §1.

## D-100. A section's artifact list is a selection, not the store

- **Date:** 2026-09-08 (Phase 9 follow-up 4, decided in Cowork)
- **Q:** Section 7 of the fourth live report recommends tracking the Brier score "against the
  declared ceiling of 0.2 [[art:d0f98b9c:threshold.package.brier.test.max]]; **no recomputed test
  Brier value is carried in this report's artifact store**, so the first monitoring run establishes
  that baseline rather than inheriting it from validation." `metrics.test.brier` is in the store at
  0.1385 and is cited in sections 1, 2 and 4 of the same report. The monitoring selector lists
  `threshold.package.` and, by name, `metrics.test.auc`, `calibration_slope.test` and `psi.max` —
  every recomputed value a declared bound needs except the Brier one. Whose defect is it?
- **A:** The selector's, and it is fixed generally rather than by adding one name.
  `recomputed_for_declared_bounds(store, brief)` reads the `thresholds.evaluation` rows D-092
  already writes — one per bound `package.yaml` declares, each carrying its metric and its split —
  and adds `metric_artifact_name(metric, split)` for every row whose declared bound this section's
  selectors match. So **any** section shown `threshold.package.<metric>[.<split>].<min|max>` is
  shown the recomputed `<metric>` for that split, for every metric a package declares now and
  every one it declares later. `DRAFT_INSTRUCTION` gains the standing rule beside it: the artifacts
  listed are this section's selection and not the store, and no section may state that a quantity
  is absent, uncomputed, not recomputed, not available or "not carried".
- **Why:** A bound with no value beside it is not a monitoring recommendation, it is half of one,
  and hand-listing the pairs is what made it possible to write half of one — the four names in the
  selector were the four the Phase 8 author thought of, and `brier` was the one they did not.
  Deriving the pair from the table means the selector cannot fall behind `package.yaml` again,
  which is exactly D-092's argument about a prefix not being a taxonomy, applied to the other end
  of the same table. The prompt rule is the necessary second half and could not have been the whole
  fix: the drafter's sentence was *true of what it was shown*, and a drafter forbidden to say a
  number is missing while genuinely not having it would simply have said nothing about Brier
  monitoring at all. It is a standing rule rather than a sentence in section 7's brief because
  every section has a selection and every section can make this mistake; section 5's brief already
  carries the narrower version of it ("say plainly which of these do not apply … they are listed in
  Appendix D"), and Appendix D remains the one place that says what a run did not compute.
  Rejected alternatives: adding `metrics.test.brier` to section 7's selector, which fixes this
  report and leaves the next metric to be found the same way; giving every section every scalar,
  which is what a selector exists to prevent — a drafter can only cite what it is given, and a
  section handed the whole store writes a report that wanders (spec section 3.11); and having the
  renderer grep the prose for "not carried", which is a grep over natural language standing in for
  a fact the prompt could carry. Measured: `tests/test_report_sections.py` asserts, for every
  declared bound of a run-shaped store and every one of the seven sections, that a section shown
  the bound is shown the recomputed value — and asserts separately that the monitoring selector
  still does not name `metrics.test.brier`, so the test is about the derivation and not about a
  list.

## D-101. The bounded loop's executed steps reach the prose, under a heading of their own

- **Date:** 2026-09-08 (Phase 9 follow-up 4, decided in Cowork)
- **Q:** The fourth live run is the first in which the bounded loop did anything: four steps, three
  of them executed, computing `metrics.test.sub.{limit_bal_low,limit_bal_high,delinq_count_6m_eq_0}.*`
  — twenty-four scalars, among them test AUC of **0.5875** and Gini of **0.1749** on the 6,048 rows
  of 9,000 where `delinq_count_6m == 0`, against 0.7550 and 0.5100 on the split as a whole. The
  report does not mention any of it. Section 4's selector matched every one of the twenty-four and
  its drafter was shown all of them. Why did it write nothing, and where should the answer go?
- **A:** Because the brief does not ask and the step's own `why` was never passed on, and both are
  fixed. `FollowUp` carries the tool, the arguments, the loop's stated reason, the logical names
  the step **added** to the store, and whether the result is material (D-102);
  `sections_for_follow_up` assigns a step to every section whose selector matched one of those
  names; and the drafting prompt gains a "Follow-up analyses the bounded planning loop ran" block
  naming each, with the instruction to report every one under `### Follow-up analyses` — a level-3
  heading, like `### Open items` under D-096 and for the same reason, so that
  `REPORT_SCHEMA.json`'s pinned list of eleven level-2 headings does not move. The renderer
  supplies the heading where the drafter omitted it and `check_structure` asserts it is there, so
  the rule cannot lose a finished report. Two exclusions are part of the rule. **The summary is
  never assigned a step** although its `metrics.` selector matches: section 1 states the headline
  and the findings count and is derivative by construction, and an analysis reported there before
  it is reported anywhere is a headline with no body. **Section 6 is never assigned one either**:
  a material step reaches it as an open item, which is a different sentence with a different point
  (D-102). And a step is routed by what it *added*, not by everything it stored — a follow-up
  `compute_metrics` recomputes every split's metrics on its way to the slice, and routing on those
  names put the block in section 2, which cites `metrics.test.auc` and knows nothing about slices.
- **Why:** The loop is the one part of this pipeline that is the model's own initiative, it is
  bounded at four steps precisely so that each one has to be worth making, and the run paid for
  four model calls and three tool calls to produce the most interesting number in the whole
  validation — a segment covering two thirds of the test split on which the model discriminates
  barely better than a coin. A report that omits it is worse than a report that never asked. The
  reason it was omitted is not the drafter's: it was given numbers and no question, and its brief
  told it what section 4 is for. D-090 made the same argument in the other direction — do not
  withhold from the model what the caller already has — and the caller had the `why` in
  `PlannedCall.why` the whole time. Requiring the subsection rather than leaving it optional is
  D-096's argument: an optional section that is usually absent teaches a reader to skip it, and
  here the subsection is present exactly when there is something in it. Rejected alternatives:
  writing the follow-up results into every matching section's brief, which makes one prompt's text
  depend on what another section is doing; having the renderer write the results itself from the
  store, which produces a table of numbers with no claim attached and is D-013's rule inverted —
  the renderer prints what the tool computed, and what a result *means* is prose; and assigning
  each step to a single section chosen by the tool's defect classes, which puts a sub-population
  metric in section 4 by coincidence and a re-profiled feature nowhere. Measured:
  `tests/test_report_sections.py` asserts the step's `why` and its column reach section 4's prompt
  and that section 1 and section 6 are excluded by the rule rather than by their selectors;
  `tests/test_renderer.py` asserts the renderer supplies the heading, keeps what the drafter wrote,
  and asks no other section for it; `tests/test_report_schema.py` asserts the structural check
  looks inside the right section; `tests/test_pipeline.py` runs a scripted sub-population step end
  to end.

## D-102. A follow-up becomes an open item when the slice is materially worse and large enough

- **Date:** 2026-09-08 (Phase 9 follow-up 4, decided in Cowork)
- **Q:** D-101 puts a follow-up analysis in the section that computed it. The practitioner's rule
  is that some of them belong somewhere else: a slice whose metric is materially worse than the
  headline is a question for the model developer, and section 6's `### Open items` is where a
  developer is asked to answer (D-096). "Materially worse" has to be an artifact or the sentence
  that says it cannot be cited (D-091). Which bound, and how large must the slice be?
- **A:** Two new bounds of their own, both stored by the tool that computes the slice, and neither
  raising a candidate. `compute_metrics._subpopulation` writes
  `metrics.<split>.sub.<slug>.auc_gap` — the split's own AUC minus the slice's — and
  `metrics.<split>.sub.<slug>.share`, and stores `threshold.O1.slice_auc_gap` = **0.08** and
  `threshold.O1.slice_min_share` = **0.10** through `Thresholds.artifact`. A slice raises an open
  item when its gap exceeds the first **and** its share reaches the second; on the fourth live run
  that is `delinq_count_6m == 0` (gap 0.1676 on 0.672 of the split) and not `limit_bal_high`
  (0.0436) or `limit_bal_low` (0.0073). `follow_up_for` reads the four numbers and writes the
  clause the prompt carries, section 6 is given the material step's artifacts and both bounds so
  that it can cite them, and its brief says what kind of sentence an open item is: **a request for
  a developer response, not a verdict.** Conditioning on one feature conditions on everything
  correlated with it — a segment selected on a delinquency count is also a segment of near-constant
  delinquency history, which on this panel means `delinq_last` and `delinq_max_6m` are nearly fixed
  inside it too — so the item asks what the model discriminates on for that segment rather than
  asserting that it is defective there.
- **Why:** The bound is new rather than a second use of `threshold.O1.auc_gap` (0.08, the same
  number) because the two comparisons are different questions about different populations.
  `threshold.O1.auc_gap` reads *train against test*: one population, two splits, and what it
  measures is overfitting. A slice-to-headline gap reads *one split against part of itself*, and
  what it measures is heterogeneity. Sharing the number would mean that re-tuning the overfitting
  bound silently re-tunes the sub-population rule and that `THRESHOLD_SUMMARIES` gives a
  train-to-test caption to a within-split comparison, which is the naming failure D-092 is about.
  Starting both rules at 0.08 is deliberate and says only that nobody has yet measured a better
  value for either. The size floor exists because a slice of thirty rows can differ from its split
  by anything at all, and asking a developer to account for sampling noise is how a validation
  report loses its reader; it is a tenth of the split rather than an absolute count because what
  makes a segment worth answering for is how much of the portfolio it is. That neither bound raises
  a candidate is the same decision as D-095's: a model that discriminates less well on a segment
  selected by one of its own features is usually a model conditioning correctly, and a rule that
  fired on it would manufacture the false alarm D-086 exists to refuse. Rejected alternatives:
  reusing `threshold.O1.auc_gap`, above; declaring the bound in `package.yaml`, which is a schema
  change under D-098's procedure for a number no developer has an opinion about and which would
  make the rule silent on every package that omitted it; leaving materiality to the drafter's
  judgement in prose, which is a decision about the report's structure taken by a model call
  (D-098); and promoting a material slice to an `O1` candidate, which would put it in
  `findings.json`, in the severity counts and in the study's precision denominator, so the most
  useful observation in the report would score as a false alarm. Measured:
  `tests/test_report_sections.py` carries the run's own three slices at their own numbers — the
  never-delinquent segment material, the two `limit_bal` halves not — plus a slice below the floor
  whose gap is 0.4 and a step with no slice reading at all; `tests/test_pipeline.py` runs the same
  step end to end at three settings of the two bounds and asserts the artifacts reach
  `### Follow-up analyses` and `### Open items`, `### Follow-up analyses` only, and
  `### Follow-up analyses` only.

## D-103. A section with no finding says so and does not describe what it reviewed

- **Date:** 2026-09-08 (Phase 9 follow-up 4, decided in Cowork)
- **Q:** Section 6 of the fourth live report says no finding was raised and then writes: "The
  validation instead reviewed input data lineage and quality, the construction of the estimation
  and holdout samples, the overlap between training and test feature vectors, the fitted
  coefficient signs against their univariate directions, discriminatory power and calibration on
  the holdout sample, and **the documentation of intended use and known limitations**." Appendix D
  of the same report says the package has no `docs/` directory, and no check this pipeline runs
  reads data lineage. The prompt asked for exactly that sentence: "Say so in one sentence, say what
  was checked instead". What should it ask for?
- **A:** One sentence, and nothing else. The no-findings block now says so and forbids the drafter
  to describe what was reviewed, to list the reviews carried out, or to say that any review produced
  no defect; section 6's brief carries the same rule with the two false items named. The
  enumeration a reader needs is the renderer's own line, printed immediately beneath the drafter's
  prose from `FindingsDocument.checks_without_candidates`: "Checks that ran and raised no candidate:
  `profile_data` (D1, S1), `compute_metrics` (T1, C1, O1), `check_leakage` (L1, L2),
  `check_collinearity` (M1), `challenger_compare` (E1)."
- **Why:** The prompt asked a model with no list of the checks to produce a list of the checks, so
  it produced a plausible one — which is the one thing this project must never let a report do,
  because a validation report that overstates its own coverage is worse than one that understates
  it. And the fix costs nothing: the pipeline has the list, in the document that section 6 renders
  from, and prints it two lines lower. The two sentences sat side by side in the shipped report, one
  drafted and one computed, and they disagreed. Keeping the drafter's sentence and giving it the
  list was rejected: it is D-013's rule about tables read for prose — a drafter asked to retype what
  the store holds is a drafter whose transcription is being scored instead of its reasoning — and
  the list is not the interesting half of section 6 either way. Also rejected: dropping the
  renderer's line and letting the drafter own the enumeration, which puts the coverage claim of the
  whole report inside a model call; and having `check_structure` refuse a section 6 whose prose
  names a check that did not run, which is a grep over natural language for a fact the prompt can
  simply not ask for. Measured: `tests/test_report_sections.py` asserts the prohibition and the two
  named items are in section 6's brief and that the no-findings block points at the renderer's
  line.

## D-104. Section 7 is told how section 4 ordered itself

- **Date:** 2026-09-08 (Phase 9 follow-up 4, decided in Cowork)
- **Q:** Section 7 of the fourth live report recommends that monitoring "track the observed default
  rate on each monitored cohort monthly, and when it sits below 0.05
  [[art:42f1351e:rule.calibration_first_event_rate]] the monitoring report should order calibration
  evidence ahead of discrimination evidence, **as this report does**". Section 4 of the same report
  opens by saying it reports discrimination before calibration, because the observed event rate is
  at or above that bound. The number verifies, the recommendation is sound, and the last four words
  are false. What was missing?
- **A:** The ordering itself. D-098 made `section_four_order` return the answer *and* the ground for
  it and gave the answer to section 4's brief alone; `ordered_briefs` now gives it to section 7's
  as well, through `monitoring_brief(brief, order)`, which appends one sentence saying which way
  section 4 reported and on which ground — and, where section 4 led with discrimination, forbids
  the sentence this report wrote. The four combinations are a table, exactly as section 4's four
  briefs are, so the two sections cannot disagree: one function fills both.
- **Why:** The drafter of section 7 was asked to describe a decision it had not been told about,
  while holding the artifact that decides it in the ordinary case. Reasoning from `rule.
  calibration_first_event_rate` to "as this report does" is what a competent model does with the
  only relevant fact it has, and it is wrong here for the same reason D-091's section 3 was wrong:
  the number it was shown is not the number that decided. This is the third instance of one
  pattern in three follow-ups — a section reasoning correctly from an incomplete brief — and the
  fix is the same shape each time: put the fact where the sentence that needs it can see it.
  Rejected alternatives: telling section 7 not to refer to section 4's ordering at all, which
  removes a genuinely useful monitoring recommendation to avoid getting one clause wrong; having
  the renderer cross-check the two sections' opening sentences, which is a grep over natural
  language; and drafting the whole report in one call so that the model can see its own section 4,
  which is the `plain_llm` baseline and gives up the per-section artifact selection that grounding
  precision rests on. Measured: `tests/test_report_sections.py` asserts each of the four
  combinations states what section 4 did, that the declared-use case still withholds
  `rule.calibration_first_event_rate` under D-098, and that `ordered_briefs` gives both sections
  the same answer on `credit_default`.

## D-105. Nearness is not identity: a repair pairs on the line or on the name

- **Date:** 2026-09-08 (Phase 9 follow-up 4)
- **Q:** Appendix A of the fourth live report says grounding precision reached "1.0000 after **1
  claim(s) rewritten and 5 number(s) removed** from the prose", and `claims.json` carries a
  `repairs` row saying the `1.92` of "Refitting without `utilisation` changes test AUC by 1.92e-05"
  became the `2` of "Of these, 2 are known at origination". The round rewrote nothing and removed
  six numbers. `_pair` tried the claim id, failed — the id hashes `[section, text, value]` and the
  re-draft dropped the sentence — and fell through to "the nearest unpaired verified value within a
  tenth", which `2.0` satisfies for anything near two. What may the fallback pair?
- **A:** Only a claim that is the same statement, on either of two grounds. **The same line around
  the number**: the claim's `text` with its citations and its numbers taken out, whitespace
  collapsed, is the same — which is the line a re-draft kept while it corrected the number or
  attached the citation it was missing, and is the case the fallback exists for. **The same cited
  logical name**: the replacement cites an artifact the flagged claim cited, so it is about the
  same quantity wherever in the section the sentence moved to. The relative window still applies
  on top of both; it is necessary and was never sufficient. Where a re-draft leaves neither link —
  it re-words the sentence *and* attaches a citation the flagged claim did not have — the round is
  recorded as a removal, which under-reports one rewrite and cannot invent a row joining two
  unrelated sentences.
- **Why:** A value is not an identity, and on a report of 167 claims the chance that some verified
  number sits within ten per cent of a removed one is close to one. What the pairing is actually
  for is the two things a repair does to a line, and both leave the line's prose standing: D-073's
  own example is a number "corrected, or given the citation it was missing". So the test should be
  about the line, and the reason the id-first pass cannot do it is that `Claim.text` is the whole
  line, citations included (D-085) — adding a citation changes the text and therefore the id, which
  is what the docstring claiming otherwise had wrong. The consequence of getting this wrong is
  precisely what D-097 exists to stop: an appendix that misdescribes what the repair loop did, this
  time in both directions at once, and a published repairs table with a false row in it. Choosing
  to under-report a rewrite rather than risk a false row is the direction that keeps Appendix A
  auditable — a reader can find the number in the prose and see that it was not removed, whereas a
  false pairing invites them to believe a sentence about `utilisation` was corrected into a
  sentence about feature timing. Rejected alternatives: dropping the fallback entirely and pairing
  by id alone, which reports every citation-added repair as a removal and undoes D-097; narrowing
  the window to a fraction of a per cent, which fixes this collision and not the next one, because
  the problem is the kind of evidence and not its amount; and comparing the *after* claim's
  artifact value with the *before* claim's written value, which re-admits exactly this pairing —
  `run.features#at_origination` is 2 and the removed number was 1.92. Not claimed here: that the
  removal count is now exact in every case. A number the drafter kept while re-wording its whole
  sentence is still counted as removed, and the trace's `removed` field is what Appendix A reads;
  separating "unpaired" from "gone from the prose" would change the `repair` event's fields, which
  D-073 fixed, and no live run has produced that case. Measured: `tests/test_repair.py` records the
  attempt-4 case as a removal with an empty `repaired` list, keeps the two grounds working — a
  number corrected in place, and a sentence moved but still citing its artifact — and asserts the
  boundary case is a removal.

## D-106. Integral values reach the drafter as integers

- **Date:** 2026-09-08 (Phase 9 follow-up 4)
- **Q:** D-094 made the renderer's expanded tables print an integral cell as an integer, because
  `900` is a count of rows and not a measurement to four significant figures. The drafting prompt
  was left out of that decision, and a live report's prose reads "the screen flags 0.0 features".
- **A:** `ArtifactBrief.to_payload` writes an integral value as an `int`, for a scalar and for
  every path of a JSON artifact. `four_significant_figures` still decides the precision; this
  decides the spelling.
- **Why:** The drafter writes what it is shown — that is the rule the whole selection mechanism
  rests on — so a prompt that shows `0.0` gets `0.0` in the prose, and the half of the report a
  reader quotes is the prose and not the appendix table D-094 fixed. It costs nothing and it is
  the same sentence as D-094's, applied to the larger surface. Rejected alternative: making the
  drafter responsible for the spelling in `DRAFT_INSTRUCTION`, which adds a rule to a prompt in
  order to avoid changing one line of a serialiser, and which the verifier could not enforce —
  `0.0` and `0` are the same claim to the matcher, so a drafter that ignored the instruction would
  never be caught. Measured: `tests/test_report_sections.py` asserts `profile.train.n` reaches the
  prompt as `3500` and that a measurement is untouched.

## D-107. The loop is shown the columns it can slice on

- **Date:** 2026-09-08 (Phase 9 follow-up 4)
- **Q:** The fourth live run's first plan step asked `compute_metrics` for a sub-population of
  `credit_limit`. The subject's column is `limit_bal`. The tool raised, D-088 caught it, D-090's
  history block carried the message back, and step 2 asked again correctly — one model call and one
  tool call spent learning a static fact, out of a budget of four steps.
- **A:** `loop_prompt` gains the column list, taken by `pipeline._data_columns` from the header of
  the first declared split's `data_<split>.csv` and named as the data spells them, with the
  sentence that a column not on the list does not exist. A configuration that ran no subject shows
  "(none: this configuration ran no subject, so there is no data to slice)".
- **Why:** It is D-089 and D-090 again, in the argument they share: a prompt that invites a mistake
  and then charges a model call for it is a prompt with a fact missing, and the caller had the fact.
  Reading the header rather than the whole frame keeps the cost at one `read_csv` with `nrows=0`,
  and reading the *data* rather than `package.yaml`'s declared features is deliberate: the subject's
  own screen drops features before fitting, so `data_<split>.csv` is what a slice can actually be
  taken on and `package.yaml` would name columns that are not there — the same distinction
  `declared_features` draws for every tool. Rejected alternatives: listing `package.yaml`'s features,
  above; putting the columns in the `Subpopulation` schema's description, which is generated from the
  `Args` model and would make one tool's schema depend on a run; and leaving it to D-088's catch,
  which is what this run measured the cost of. Measured: `tests/test_planner.py` asserts the block
  names the columns and says an unlisted one does not exist, and says "none" for a run with no data;
  `tests/test_pipeline.py` asserts the live prompt of a real run carries `limit_bal` and not
  `credit_limit`; `tests/test_pipeline_units.py` covers both arms of `_data_columns`.

## D-108. Guidance is retrieved top-k per document, and the drafter chooses

- **Date:** 2026-09-08 (Phase 9 follow-up 4, decided in Cowork)
- **Q:** The fourth live run's `retrieve_guidance` returned, for "data quality accuracy completeness
  and representativeness", `SR11-7:VI.4`, `SR11-7:III` and `SR11-7:V.1.c` — no span of SR 26-2 at
  all — and for "sensitivity analysis stability benchmarking alternative models", `SR11-7:V.1.b`,
  `SR11-7:V.1.a` and `SR11-7:V.2`. So sections 3 and 5 opened on superseded text while `SR26-2:IV.1`
  and `SR26-2:V.1.a` sat in the corpus unretrieved, and section 7 — which did get `SR26-2:V.2`, at
  rank 2, and opened on it — went on to cite `SR11-7:V.1.b` five times. D-055 keeps both documents
  and `DRAFT_INSTRUCTION` tells the drafter to prefer the revision. Is the retrieval or the prompt
  at fault?
- **A:** The retrieval, and `k` becomes per document. `retrieve_per_document(query, k, docs)`
  returns each searched document's own best `k`, the current guidance's first, and
  `RetrieveGuidanceTool` calls it; `corpus.retrieve` is unchanged, so Phase 6's acceptance criterion
  (D-054) still reads the whole-corpus ranking. On the two queries above the drafter is now shown
  `SR26-2:V.1.a`, `SR26-2:IV.1` and `SR26-2:V.1.b`, and `SR26-2:V.1.a`, `SR26-2:IV.1` and
  `SR26-2:VII`, beside the three superseded spans it had before.
- **Why:** BM25 scores are comparable inside one document and not across two, and this corpus holds
  a text and the revision that replaced it — different lengths, different vocabulary, one of them
  written fifteen years later. Ranking them in a single list therefore chooses which document a
  report anchors to by an accident of term frequency, which is not a choice the retriever is
  entitled to make; D-055 and the drafting prompt already say the choice is the drafter's, and this
  gives it something to choose between. It is not the prompt at fault, and that is the point worth
  recording: the instruction to prefer SR 26-2 was already there, is already obeyed —
  `pipeline._current_first` even reorders the spans so the revision comes first — and did nothing
  for a section that was never shown a revision span. The cost is a larger guidance block in seven
  drafting prompts, which is input tokens against a bill whose output half is 80% of it. Rejected
  alternatives: leaving it to Phase 16's prior-art and documentation pass, which ships a report
  whose data-quality section cites text superseded in April 2026 as if it were current; promoting
  the best current-guidance span into a whole-corpus top three, which keeps the prompt the same size
  and makes `k` mean something different in each half of the answer; restricting the retrieval to
  `docs=["SR26-2"]`, which is what D-055 refused, because a historical citation has to keep
  resolving and a validation of a model developed under SR 11-7 may need to quote it; and tuning
  BM25's length normalisation until the revision wins, which is choosing the parameter that makes
  the answer come out right. Measured: `tests/test_tool_guidance.py` asserts six spans for two
  documents at `k=3`, the revision's three first and each document's own best first, that the
  run's own data-quality query now offers `SR26-2:IV.1`, and that the whole-corpus top three for
  that query are all superseded — the defect, recorded in a test.

## D-109. A repair round re-drafts lines, not sections

- **Date:** 2026-09-08 (Phase 9 follow-up 5, decided in Cowork)
- **Q:** The fifth live run's repair round on section 4 flagged four numbers. The drafter was sent
  the whole section and returned the whole section, and one line it was not asked about came back
  changed: "…falls below its split's by 0.007286 [[art:15e1edcb:metrics.test.sub.limit_bal_low.
  auc_gap]] on test and by -0.001109 […] on train, both within the allowance" became "…on test and
  by -0.02732 [[art:41fca294:metrics.train.sub.utilisation_high.auc_gap]] **is not the figure for
  this slice**; on train the gap is -0.001109 […]". The sentence now reports another slice's train
  gap inside the limit_bal paragraph, and adjudicates itself in the middle of a clause. Every
  citation in it resolves and every number matches its artifact, so grounding precision was 1.0000
  and no part of this pipeline could see anything wrong. What is a repair round allowed to change?
- **A:** The lines that carry a flagged claim, and nothing else. `scope_to_flagged_lines` takes the
  previous draft and the re-draft and returns the previous draft with the flagged lines replaced by
  the re-draft's version of them: every other line is kept byte-identical, and a line the re-draft
  added elsewhere is not taken. The flagged lines are found by matching `Claim.text` -- which *is*
  the line the number sits on (D-085) -- back against the draft. Each returned line is attributed to
  the line of the previous draft it most resembles, citations removed before the comparison and
  ties going to the earlier line; a returned line whose best match is an unflagged line is the
  re-draft of *that* line and is discarded, and one whose best match is a flagged line replaces it.
  `REDRAFT_SIMILARITY` = 0.5 is the floor beneath the argmax: a line that resembles even its best
  match this little is a sentence the drafter wrote fresh. The `repair` trace event gains
  `lines_redrafted`, and `REPAIR_INSTRUCTION` tells the drafter the rule, because a model asked for
  a whole section and given no reason to leave the rest of it alone will not.
- **Why:** This is the first defect any of the five live runs has produced that the verifier is
  *structurally* unable to catch. Grounding precision measures whether a number matches the artifact
  it cites; it says nothing about whether the sentence is about the thing the paragraph is about,
  and a repair round is exactly the moment when a model rewrites prose nobody is checking for that.
  The apparatus already assumes the drafter's first pass is the text under review -- the extraction,
  the matching, the candidate list, the whole selection mechanism -- and the repair loop was the one
  place where that text could be replaced wholesale on the strength of four numbers. Scoping the
  round to lines makes the blast radius of a repair equal to the damage that provoked it.
  The argmax is what makes it safe on this report's own shape. Section 4's four sub-population
  paragraphs are written to one sentence skeleton, so a flagged line has three siblings that read
  almost exactly like it; attributing every returned line to its closest original *before* deciding
  what to keep is what stops a re-drafted sibling being spliced over the flagged line, because a
  sibling's numbers are its own and it resembles its own former self more. Measured on the run's own
  section 4, replayed line by line: the four flagged lines match their replacements at 0.926, 0.931,
  0.974 and 0.981 with citations removed, no other returned line attributes to a flagged line at
  all, and the damaged gap sentence keeps its original text.
  Rejected alternatives: asking the drafter for only the flagged lines, which takes the sentence out
  of the paragraph it has to read in and is the context a repair most needs; diffing the two drafts
  and asking a model whether each changed line is an improvement, which is a second model call to
  check the first and has the same blind spot; re-extracting the whole section and comparing claim
  sets, which is what already happens and which passed this report; and forbidding the drafter to
  change an unflagged line in the prompt alone, which is a rule with no enforcement -- the same
  argument D-106 makes against putting a serialiser's job in an instruction. Measured:
  `tests/test_repair.py` asserts that a re-draft altering an unrelated line leaves it unchanged,
  that a flagged line is still replaced, that a flagged line the re-draft dropped is dropped, and
  that the event records the count.

## D-110. Integral values reach the drafter unrounded

- **Date:** 2026-09-08 (Phase 9 follow-up 5)
- **Q:** Two of the fifth live run's five failed claims are counts the prompt itself rounded.
  `four_significant_figures(10158)` is 10160 and `four_significant_figures(16207)` is 16210, so
  `metrics.train.sub.limit_bal_low.n` and `metrics.train.sub.delinq_last_eq_0.n` reached the drafter
  as numbers their artifacts do not hold. The drafter copied what it was shown, which is the rule
  the whole selection mechanism rests on; the matcher holds a count to half a unit (D-014), so both
  failed as `mismatch`, one was removed from the prose in the repair round and the other became the
  false pairing of D-111. D-106 already decided that an integral value is *spelled* as an integer.
  Should it also be rounded like a measurement?
- **A:** No. `prompt_value` returns an integral value exactly and everything else at four
  significant figures, and `_artifact_brief` uses it for a scalar and for every path of a JSON
  artifact. `four_significant_figures` is unchanged and still decides the precision of a
  measurement; `as_written` is unchanged and still decides the spelling. This decides which values
  have a precision to round at all.
- **Why:** Four significant figures is a rule about how much precision a report needs to quote, and
  a count has none to give up: 10,158 rows rounded to 10,160 is not a simpler statement of the same
  quantity, it is a different number of rows. The pipeline was therefore showing the drafter a
  number, telling it to write what it was shown, and then flagging it -- the same shape as D-099,
  where the prompt taught the drafter a form its own verifier could not read, and the same shape as
  D-084 and D-091 before that. It also costs the report a real sentence: the repair round's answer
  to "you wrote 10160; the artifact says 10158" was to delete the count, so the fifth report's
  limit_bal paragraph states the slice's share of train and not how many rows that is.
  Rejected alternatives: widening the matcher's tolerance for a count to the precision the prose
  wrote, which is D-069 read backwards and would verify "10,000 rows" against 10,158; rounding the
  artifact rather than the prompt, which changes the evidence to fit the presentation; and leaving
  it to the repair loop, which is what this run measured -- two model calls and a lost count.
  Measured: `tests/test_report_sections.py` asserts 10158 reaches the prompt as the integer 10158,
  that a measurement is still rounded, and that a claim of 10158 verifies against the artifact.

## D-111. A cited claim is paired by its name, and only an uncited one by its line

- **Date:** 2026-09-08 (Phase 9 follow-up 5)
- **Q:** D-105 gave `_pair`'s fallback two grounds, either sufficient: the same line with numbers
  and citations removed, or the same cited logical name. Section 4 of the fifth live run writes its
  four sub-population paragraphs to one sentence skeleton, so the flagged
  `metrics.train.sub.limit_bal_low.n` of 10160 and the untouched, verified
  `metrics.train.sub.utilisation_high.n` of 10500 have the same line under that test -- and 10500 is
  inside the relative window of 10160. Appendix A reads "10160 (mismatch) → 10500 (verified)" and
  "1 claim(s) rewritten and 4 number(s) removed" of a round that rewrote nothing and removed five.
  Which ground applies when?
- **A:** They are ordered, not alternative. A flagged claim that cites a logical name is a statement
  about that quantity, so its replacement must cite it too; the line is consulted only for a flagged
  claim with no citation, which is the case it exists for -- a number that gains the citation it was
  missing, where there is no name to compare and the sentence is what survives. The relative window
  still applies on top of either.
- **Why:** D-105 got the grounds right and their relation wrong, and the report that found it is the
  first one whose section 4 has four paragraphs of the same shape -- which is the bounded loop's
  own doing, since each executed step adds one. A skeleton is a strong test on a report of seven
  hand-written paragraphs and a weak one on a report with a generated family in it, and the number
  of siblings only grows: the fix has to be a test that does not weaken as the loop does more work.
  The name is that test, and it is available exactly when the flagged claim has one. The cost is the
  case where a re-draft corrects the number *and* moves the citation to the artifact it should have
  cited -- one of the three answers the repair prompt offers -- which is now recorded as a removal
  and a new claim rather than as a rewrite. That is D-105's own direction, stated again: an
  under-reported rewrite is a number a reader can find in the prose and see was not removed, and a
  false pairing invites them to believe a sentence about the low-limit half was corrected into a
  sentence about the high-utilisation half. Under D-109 the fallback also has less to do, because a
  replacement now sits on the line the flagged claim sat on; the pairing is kept general because
  `_pair` is also what `rules_only` and any future re-draft path go through.
  Rejected alternatives: requiring both grounds, which loses the uncited-number case that is the
  fallback's whole purpose; keeping the skeleton but requiring the two claims to be on the same line
  index, which D-109 makes true by construction and which therefore tests nothing; and narrowing the
  window, which D-105 already rejected and which this collision would survive -- 10500 against 10160
  is 3.3%. Measured: `tests/test_repair.py` reproduces the run's two paragraphs and asserts the
  round is recorded as a removal with an empty `repaired` list, and the reworded-in-place case still
  pairs by name.

## D-112. A section reference and a slice rule are not claims

- **Date:** 2026-09-08 (Phase 9 follow-up 5, decided in Cowork)
- **Q:** Three of the fifth live run's five failed claims are not numbers anybody claimed. Section
  4's follow-up paragraphs open "**delinq_last equals 0.**" and "**delinq_last equals 1.**" -- the
  parameters of the slice rule the bounded loop asked for -- and section 7 opens a paragraph
  "Section 4 of this report reported discrimination before calibration". All three were counted in
  the denominator, flagged as `unsupported`, and removed by a repair round that spent two model
  calls on them. D-015's exclusion list already holds section numbering, inline code and finding
  ids. Are these three the same kind of thing?
- **A:** Yes, and each is handled where it belongs. A reference to a section of this report written
  in words is an exclusion: `_SECTION_REFERENCE_RE` masks `[Ss]ection \d+(\.\d+)*` under the
  existing `section_number` class, beside the `§4` and heading forms it already masks. A slice rule
  is not an exclusion but a formatting rule: `subpopulation_expression` renders the loop's step as
  `delinq_last == 0`, the follow-up block shows it to the drafter that way, and the brief asks for
  it inside backticks -- which the tokenizer has masked as inline code since D-015.
- **Why:** The two halves are different because the numbers are. A section number is the report's
  own numbering wherever it appears, so a reader of the exclusion list can check the rule without
  seeing the sentence; that is what an exclusion class is, and the alternative is a pattern that has
  to look at what the sentence means. A slice parameter is not like that: `0` in "delinq_last equals
  0" is a value in the data, and a rule excluding a bare integer after a column name would exclude
  real claims about that column. What makes it not a claim is that it is a *rule*, and the way prose
  says "this is a rule and not a measurement" is to set it in code -- which the tokenizer already
  understands, which needs no new pattern, and which reads better besides. So one number leaves the
  denominator by a rule about the report's structure and two by a rule about how the report writes.
  Both directions are recorded here because D-077's list is the audit trail for the denominator, and
  a denominator that quietly shrinks is the failure an exclusion list is most dangerous for.
  Rejected alternatives: excluding a bare integer that follows the word `equals`, which is a pattern
  over English and would swallow "the event rate equals 0"; leaving all three to the repair loop,
  which is what this run paid for -- three of five failures and a round on section 7 that existed
  only for them; and asking the drafter not to mention section numbers, which forbids a
  cross-reference a validation report legitimately makes. Measured:
  `tests/test_verifier_extract.py` asserts the run's own section-7 sentence yields one claim and
  records "Section 4" as excluded, and that "the cross-section holds 4 rows" still claims four;
  `tests/test_report_sections.py` asserts the rule reaches both prompts as `delinq_last == 0`.

## D-113. The citation carries the logical name, so the prose does not

- **Date:** 2026-09-08 (Phase 9 follow-up 5)
- **Q:** The fifth live report writes "A sub-population's AUC may fall below its split's own AUC by
  up to threshold.O1.slice_auc_gap at 0.08 [[art:0a827b87:threshold.O1.slice_auc_gap]]" and "at or
  above the ordering rule's bound of 0.05 [[art:42f1351e:rule.calibration_first_event_rate]]". The
  name is in the sentence and in the citation immediately after it. Nothing is wrong -- every claim
  verifies -- and the sentences read like a debug log.
- **A:** `DRAFT_INSTRUCTION` gains the rule: do not write an artifact's logical name in the prose,
  because the citation after the number carries it. Say in words what the number is.
- **Why:** The drafter was never told, and it had a reason to guess: the prompt shows it a JSON
  object whose keys are logical names, tells it to copy the citation exactly, and gives it no
  vocabulary for the quantity other than the name. The remedy is one sentence in the standing
  instruction rather than in a brief, for D-100's reason -- every section can do this, and the one
  that did it twice is not the one that will do it next. It is not enforced downstream and this
  entry does not pretend otherwise: a logical name in prose is a readability defect and not a
  grounding defect, and the verifier has nothing to say about it. Rejected alternatives: stripping
  the names in the renderer, which edits the sentence the claim id hashes (D-099's argument against
  normalising prose after drafting); and shipping the artifact's `summary` in place of its name in
  the prompt, which is a larger change to what the drafter can cite and would leave it unable to
  copy a citation it cannot see.

## D-114. Section 7 is told the run compared a challenger

- **Date:** 2026-09-08 (Phase 9 follow-up 5)
- **Q:** The fifth live report's section 7 writes "Benchmarking against an alternative internal or
  vendor model, or against retail credit bureau data, was not part of this validation" under "What
  this validation could not cover". Section 2 of the same report reports the challenger comparison
  `challenger_compare` ran, with the challenger's AUC against the champion's and the threshold that
  decides whether the difference matters. The sentence is true of section 7's own selection --
  `challenger.` is not among its scalars -- and false of the report.
- **A:** `monitoring_brief` takes the store, and where `challenger.delta_auc` is in it the brief
  gains a paragraph: a challenger was compared and section 2 reports it, so do not write that
  benchmarking was not part of this validation; what monitoring adds is the comparison development
  data cannot give -- an external or vendor reference, or the challenger refitted on production
  vintages -- and say which you mean.
- **Why:** This is D-100 again, in the half D-100 did not reach. That decision made a section shown
  a *bound* also shown the *value*, and forbade any section to call a quantity absent; it could not
  stop a section calling an entire **activity** absent, because an activity is not an artifact
  selector and the prohibition is about numbers. Telling section 7 what section 2 did is the same
  fix as D-104's -- pass the fact to the sentence that needs it -- and the same reason it is a fact
  and not a prohibition: a drafter told only what not to say has nothing true to put there, and
  "monitoring should benchmark" with no reference to what validation already benchmarked is a
  weaker recommendation than the one the report can actually make. It is keyed on the artifact
  rather than on the configuration because `rules_only` and a package with no challenger both
  produce runs where the sentence would be correct.
  Rejected alternatives: adding `challenger.` to section 7's selector, which hands it numbers it has
  no recommendation to make about and invites it to restate section 2 (spec section 3.11's wandering
  report); a standing rule in `DRAFT_INSTRUCTION` forbidding any section to say an activity was not
  performed, which would also forbid Appendix D's own subject matter -- `check_stability` really was
  not run; and leaving it, which ships a report whose section 7 contradicts its section 2 in a
  paragraph a reader of the limitations is reading precisely for what is missing. Measured:
  `tests/test_report_sections.py` asserts the paragraph appears exactly when the artifact is in the
  store, and that the two-argument call is unchanged.

## D-115. A follow-up slice reports its metrics as a table

- **Date:** 2026-09-08 (Phase 9 follow-up 5, decided in Cowork)
- **Q:** The fifth live run's four executed steps each wrote nine metrics on each of two splits into
  section 4's prose, one cited number at a time: 72 of the report's 285 claims, and most of the 155
  extra claim checks it ran over the fourth run's. Extraction is 76,400 of the run's 123,170 output
  tokens. The numbers are right and every one of them verifies. Is the enumeration what the section
  is for?
- **A:** No. `compute_metrics` stores `metrics.<split>.sub.<slug>` -- one row per metric, the eight
  scalars and the share -- beside the scalars it already stores, the renderer expands
  `[[table:...]]` for it as for any table artifact, and section 4's `tables` entry becomes the
  prefix `metrics.` because the family's members are named by the run and not by this file. The
  follow-up brief asks for the directive on a line of its own and then the interpreting sentences:
  how far the slice's AUC falls below the split's own and against which bound, how much of the split
  it holds and against which floor, and whether mean predicted against the observed rate puts the
  weakness in the level of the probabilities or in their ordering. The gap and the share stay
  scalars and stay cited in prose, because that is what the sentences are about.
- **Why:** It is D-092's argument about `thresholds.evaluation`, applied to the family the bounded
  loop generates. A table the tool computed and the drafter only points at cannot disagree with the
  store, cannot be mistyped, and is not extraction's business at all -- D-013 excludes a renderer
  block from the claim set because no model wrote it. So the evidence in the report is unchanged and
  strictly better attested, while the claims that carry it stop scaling with the number of steps the
  loop takes. That scaling is the point: the loop is meant to ask more questions as the project goes
  on, and a design where each question adds eighteen transcribed numbers to one section's prose gets
  more expensive and less readable with every step it earns. What is left in prose is the part that
  is a judgement -- a gap read against a bound, a share read against a floor, a level-versus-ordering
  reading -- which is what a validator writes and a table cannot.
  Not claimed here: a measured saving. The three cost figures this project has are three runs of one
  prompt on one model at n = 1 each, and D-085's entry in `docs/EVALUATION.md` says at length why
  that is variance and not evidence. The claim is structural -- 72 fewer claims to extract, check and
  print, on the run this was measured on -- and the money is Phase 12's to measure.
  Rejected alternatives: one table per slice with a column per split, which reads better and does not
  fit `metrics.<split>.sub.<slug>`, the stem the scalars already share and the name the citation
  resolver already understands; dropping the per-metric scalars now that a table carries them, which
  would leave the interpreting sentences with nothing to cite and break D-102's materiality reading;
  capping how many metrics a follow-up paragraph may enumerate, which is a limit on the drafter
  rather than a better shape for the evidence; and leaving it to the study, which is Phase 12 paying
  for the enumeration on every variant of every configuration. Measured: `tests/test_pipeline.py`
  asserts a follow-up step's report carries the expanded table block and still cites `auc_gap` and
  `share` in prose; `tests/test_report_sections.py` asserts the prefix offers the table to section 4
  and not to section 5.

## D-116. A reference to this project's decision log is not a claim, and a caption does not carry one

- **Date:** 2026-09-08 (Phase 9 pre-flight, follow-up 6)
- **Q:** Turning the three archived live runs into offline fixtures asks the tokenizer question of
  every draft those runs made rather than of the reports they shipped, and the first thing it finds
  is section 4 of the third run: "The declared bound on the train-to-test AUC gap under rule O1
  **(D-050)** is 0.08 `[[art:630f28f4:threshold.O1.auc_gap]]`". The `50` was an eligible token, was
  counted in the denominator, was reported `unattributed`, and provoked a repair round whose
  re-draft also rewrote the neighbouring sentence and cost the report a *verified* `0.08`. The
  drafter did not invent the reference: the caption of the artifact it was shown reads "O1: the
  train-to-test AUC gap (D-050)". Is `D-050` an exclusion or a thing the prose should not contain?
- **A:** Both, each where it belongs. `_DECISIONS_REFERENCE_RE` masks `\bD-\d{3}\b` under a new
  exclusion class `decisions_reference`, so a decision reference wherever a model writes it is not
  a claim; and no artifact caption carries one any more -- the four in `THRESHOLD_SUMMARIES` and
  the one in `check_collinearity` lose theirs, and `tests/test_pipeline.py` asserts that no
  artifact either synthetic run stores has one. It is a class of its own and not a widening of
  `finding_id`: `F-001` numbers a finding of *this report*, which Appendix A resolves for the
  reader, and `D-050` numbers an entry of a file the reader does not have. This amends D-015's list
  of six classes to seven, which is why it is recorded here rather than folded into D-112.
- **Why:** Neither half is sufficient. With the exclusion alone the report still prints Quaestor's
  own bookkeeping in its prose and in Appendix B, in a document addressed to a model developer at a
  bank who cannot look the reference up -- the same readability defect as D-113, one document
  further out. With the caption fix alone a live model that writes `D-050` from anywhere else still
  mints a claim of fifty, and the archive shows it is a *choice* the model makes rather than a
  transcription: attempts 1 and 3 sent byte-identical section-4 prompts -- the cassette key is a
  hash of the request and both runs stored the same one -- and only attempt 3 copied the reference
  out of the caption. So the tokenizer has to read a form the prompt no longer teaches, which is
  D-099's rule in reverse and for the same reason.
  The cost is the usual one: an exclusion lowers the denominator, and D-015 is emphatic that a
  denominator which quietly shrinks is the failure an exclusion list is most dangerous for. So the
  blast radius is measured rather than argued -- over the draft calls of all four archived runs
  that made any, the class removes exactly one token, attempt 3's `D-050`, which
  `tests/test_archive_fixtures.py` asserts as an equality and not as a bound.
  Rejected alternatives: an instruction to the drafter not to write a decision reference, which is
  D-113's remedy and right where the prompt has a legitimate reason to show the name but wrong
  here, because the prompt has no reason at all to show this one -- and an instruction cannot stop
  a caption from being copied, which is the mechanism; widening `_FINDING_ID_RE` to `[DF]-\d{3}`,
  which puts two documents in one audit class and makes the exclusion list less legible than the
  thing it audits; excluding only `(D-\d{3})` in parentheses, which is a pattern over punctuation
  and would count a bare "as D-050 requires"; and stripping the reference in the renderer, which
  edits the sentence the claim id hashes (D-099's argument against normalising prose after
  drafting). Measured: `tests/test_verifier_extract.py` asserts one claim for the run's own
  sentence and `D-050` recorded as excluded, and that "the D-050 cohort holds 12 rows" still claims
  twelve; `tests/test_archive_fixtures.py` asserts the sentence as the cassette holds it, the
  caption as attempt 3's own index holds it, and the shipped caption without it.

## D-117. The repair event says whether the round was scoped at all

- **Date:** 2026-09-08 (Phase 9 pre-flight, follow-up 6)
- **Q:** D-109 scopes a repair round to the lines carrying a flagged claim, and
  `scope_to_flagged_lines` has one fallback: when no line of the previous draft carries one of the
  flagged claims it returns the whole re-draft, with `lines_redrafted` set to the re-draft's line
  count. That is the one path on which D-109's guarantee does not hold, and nothing on the trace
  distinguishes it from a round that happened to re-draft every line. What should a live run that
  took it look like in the record?
- **A:** Explicit. `scope_to_flagged_lines` returns a `ScopedRedraft` -- the markdown, the count,
  and `scoped` -- and the `repair` trace event carries `scoped: false` when the fallback fired and
  `scoped: true` when it did not. The decision is not recomputed by the caller: `repair_sections`
  reads it off the return value, because a rule evaluated in two places is the shape of defect
  D-084 named and D-091 and D-099 repeated.
- **Why:** The whole of D-109's argument is that a repair round's blast radius should equal the
  damage that provoked it, and the fallback is the case where it does not: the section is replaced
  wholesale on the strength of claims that could not be located in it. That is a legitimate
  outcome -- the alternative is a round that changes nothing at all -- but it is one a reader of a
  live trace has to be able to find, and `lines_redrafted == len(lines)` is an inference over two
  documents rather than a fact in one. None of the six archived rounds took the path, which
  `tests/test_archive_fixtures.py` asserts by the reason it cannot: `Claim.text` *is* the line the
  number sits on (D-085), so a flagged claim of a draft is findable in that draft.
  Rejected alternatives: deriving `scoped` in `repair_sections` from `_flagged_line_numbers`, which
  states the rule twice; raising instead of falling back, which turns a repairable section into a
  failed run over a claim the round could not place; and reading it off `lines_redrafted`, which is
  the inference this entry exists to remove.

## D-118. The archive is a fixture over the drafts, and the coverage arithmetic is shared

- **Date:** 2026-09-08 (Phase 9 pre-flight, follow-up 6)
- **Q:** Every defect class this project has found came out of a person reading a live report at
  roughly $6 and twenty-two minutes a run. The runs are committed, so the reading can be a test --
  but of what text, and sharing what code with `tests/test_golden_spec.py` check 7, which asks the
  same question of the Phase 1 golden?
- **A:** Of the drafters' own completions, and sharing the counting but not the tokenizer.
  `tests/archivesupport.py` reads each archived run -- report, `claims.json`, trace, cassettes,
  index -- and recovers every drafting call from its cassette, a repair round's *previous* draft
  from the repair prompt that quotes it verbatim, and the round's flagged claims from the ids its
  own `repair` event lists. `tests/claimsupport.py` holds the coverage arithmetic, stdlib only, and
  check 7 now calls it. Check 7 keeps its numeric pattern as a literal.
- **Why:** `report.md` cannot answer the question the fixture is for. A repair round's answer to a
  number it could not verify is usually to delete it, so a token that provoked a round is exactly
  the token the shipped report no longer holds: the third run's `(D-050)` is not in its report at
  all, and a check over the three reports passes on all three -- which is worth asserting, and
  finds nothing. The first drafts are where the population of unknown token classes lives, and the
  cassettes hold them.
  What is shared is chosen the same way. The counting is arithmetic over tokens and claims already
  in hand and belongs in one place, because two copies of it are two chances to disagree about what
  "covered" means -- D-084's whole lesson. The tokenizer is *not* shared, and that is deliberate:
  `tests/test_golden_spec.py` is the executable specification of the report and imports no part of
  the package it specifies, so a change to `tokens.py` cannot make the specification agree with it
  by construction. D-099 already treats the two expressions as copies kept in step by hand, and
  `claimsupport.py` importing nothing is what lets check 7 use it without acquiring the dependency.
  What the cassettes cannot support is recorded where it bites rather than worked around. The
  re-extraction that followed each archived round ran on that run's own unscoped re-draft, so no
  tape holds the extraction of a scoped one and the claims a scoped round would have produced
  cannot be replayed; the replay asserts the text and says so in its docstring. Attempts 1 and 2
  wrote no `claims.json` -- the first was refused by the renderer (D-084), the second exited 1 when
  a tool raised (D-088) -- so the coverage check cannot run on them; attempt 1's draft calls are
  still read, against the verified `claim_check` events of its trace, which is how the fixture
  shows that D-112's section-reference exclusion would have saved that run a flagged claim four
  runs before the run that found it. And a re-draft is located by the section its prompt names,
  which is unambiguous only because no archived section went to a second round: that is asserted,
  so an archive that acquires one fails rather than silently replaying the wrong tape.
  Rejected alternatives: checking the reports only, which is the check that finds nothing and was
  written first; adding the archive's tokens to `tests/test_golden_spec.py`, which would make the
  Phase 1 specification depend on the operator's run directory and on `quaestor` itself; copying
  check 7's loop into the new module, which is what this entry exists not to do; and reconstructing
  a first draft by re-running the pipeline against the cassettes, which is a replay layer and is
  Phase 11's.

## D-119. The two Phase 9 follow-up pipeline cases run at the default panel and assert the set

- **Date:** 2026-09-08 (Phase 9 pre-flight, follow-up 6)
- **Q:** `tests/test_pipeline.py`'s two Phase 9 follow-up cases -- a tool the loop asked for that
  does not apply (D-089) and one that raised inside itself (D-088) -- run at `SMALL = 1200` rows
  and assert `"E1" in` the run's findings. D-017 says the clean synthetic `credit_default` panel
  raises exactly `{E1 low}`, and `in` is not that statement. At 1,200 rows the subject raises `T1`
  at high and `C1` at medium beside the `E1`, so the weaker assertion is what the small panel
  forced. Is the small panel worth it?
- **A:** No, for these two. Both run at the default 5,000 rows and assert
  `{("E1", "low")} == the finding set`, through a `_finding_set` helper that says what D-017 is a
  statement about. **Measured on this machine: one `full_agent` run of the case is 2.16 s at 1,200
  rows and 2.40 s at 5,000, and the two cases together went from 7.07 s to 6.93 s of wall-clock
  under `pytest -q -k`, which is inside the noise of the session fixtures they share.** `SMALL`
  stays for the thirteen other cases that use it, whose subject is a planner action or a
  configuration and not the finding set.
- **Why:** These two cases exist to show that a refused step and a raising tool do not cost the run
  its report, and "the report is still the report D-017 describes" is the strongest form of that
  claim available. `"E1" in` passes on a panel that also raised `T1` at high -- a *high*-severity
  finding on a clean subject -- which is precisely the outcome the case would want to fail on, and
  it passes at 1,200 rows today for that reason. A quarter of a second per run is not a trade.
  Rejected alternatives: keeping `SMALL` and asserting the whole `{T1, C1, E1}` set it produces,
  which pins a small panel's artefacts as though they were the subject's behaviour and would fail
  the next time the generator's tails change; moving every use of `SMALL` to the default, which buys
  nothing for the cases that assert a planner action and costs a second and a half; and dropping the
  finding assertion from the two cases, which removes the only line in either that says the run
  produced a *correct* report and not merely a report.

## D-120. The excerpt is edited; the record is not

- **Date:** 2026-09-08 (Phase 9 follow-up 6, decided in Cowork)
- **Q:** `eval/results/first-live/credit/` is the sixth `credit_default` live run and the one the
  README will excerpt in Phase 16. Reading it against the excerpt bar found five sentences whose
  wording a reader outside this project would misread — a delta called a "cost" when it is an
  improvement, a mechanism asserted where the evidence supports consistency, a bound attributed to
  the package that Quaestor sets, an overfitting conclusion stated more strongly than a
  train-to-test comparison supports, and a signed gap read as a shortfall. None of them is a wrong
  number. May `report.md` be edited?
- **A:** No. The committed `report.md` is what the pipeline produced on `fc33dd7` and it is never
  edited, now or later; the run is committed byte-for-byte on D-087's terms (row-level CSVs
  outside the repository, `find … -name '*.csv' -size +20k` prints nothing). The **excerpt** is
  where the five edits are applied. Phase 16 takes **§2 and §4 whole** — `### Follow-up analyses`
  and the degenerate-slice paragraph included — applies the five edits below and nothing else, and
  prints them as a before/after diff in `docs/PROVENANCE.md` beside a line saying the excerpt is
  edited and the record is not. **No edit changes a number**, which
  `tests/test_live_credit.py::test_no_excerpt_edit_changes_a_number` asserts by tokenizing both
  sides of each pair and comparing the values.

  The five, verbatim, so Phase 16 copies rather than reconstructs them. Each `before` is asserted
  to be in the committed `report.md` **exactly once**, so this entry cannot drift from the file it
  quotes:

  1. §2 "Fitted signs against univariate direction", two sentences of the same shape:
     - `but refitting without the term costs -5.589e-05 [[art:e26d8112:ablation.pay_ratio_last.delta_auc]] of test AUC`
       → `but refitting without the term changes test AUC by -5.589e-05 [[art:e26d8112:ablation.pay_ratio_last.delta_auc]]`
     - `refitting without the term costs -0.001393 [[art:99f9dd71:ablation.bill_trend_6m.delta_auc]] of test AUC`
       → `refitting without the term changes test AUC by -0.001393 [[art:99f9dd71:ablation.bill_trend_6m.delta_auc]]`
  2. §2, the utilisation paragraph:
     `the sign reversal reflects the credit limit and billing terms absorbing`
     → `the sign reversal is consistent with the credit limit and billing terms absorbing`
  3. §4 "Train-to-test gap":
     `the bound of 0.08 [[art:630f28f4:threshold.O1.auc_gap]] the package sets for it`
     → `the bound of 0.08 [[art:630f28f4:threshold.O1.auc_gap]] rule O1 sets for it`
  4. §4 "Train-to-test gap":
     `so the fit does not depend on the sample the model was estimated on`
     → `so there is no sign of overfitting to the estimation sample`
  5. §4 "Follow-up analyses", the `limit_bal` below-median paragraph:
     `and -0.001109 [[art:021950a5:metrics.train.sub.limit_bal_low.auc_gap]] below it on train`
     → `and by -0.001109 [[art:021950a5:metrics.train.sub.limit_bal_low.auc_gap]] on train, that is, marginally above it`

  The prompt this entry was written from quoted edits 1's two `before` strings **without** their
  citations — `costs -5.589e-05 of test AUC`. Neither string is in `report.md`: the drafter wrote
  the citation between the number and the words, as the grammar requires. The strings above are
  the file's, and the `after` strings keep each citation immediately after the number it carries,
  which is where D-113 puts it.
- **Why:** The report is evidence. Its value in a README is that a reader can be told "this is
  what the pipeline wrote, unedited, and here is the trace, the cassettes and the artifact store it
  wrote it from" — and an edited `report.md` cannot be told that about, however small the edit and
  however honest the intent. The five sentences are still worth fixing, because a README excerpt is
  read by people who will not read §4's Follow-up analyses for context and three of the five would
  mislead them: "costs -5.589e-05 of test AUC" reads as a loss when the sign says the refit was
  *better* without the term, "the package sets" attributes `threshold.O1.auc_gap` to a developer
  declaration when `package.yaml` says nothing about it, and "the fit does not depend on the
  sample" is a stronger claim than one train-and-test partition supports. Applying them in the
  excerpt and printing the diff gets both: the record stays a record, and the excerpt says what the
  evidence says. Rejected alternatives: editing `report.md` and noting the edits in
  `DECISIONS.md`, which makes every future citation of the run's grounding precision a citation of
  a file a human has touched; excerpting §2 and §4 unedited, which publishes three sentences that
  misread on their own; excerpting a *paraphrase* of the two sections, which is the thing a
  validation report exists not to be; re-running the pipeline hoping for better wording, which is
  $4 and fifteen minutes for a different set of five sentences and would throw away a run whose
  verifier flagged nothing; and dropping the degenerate-slice paragraph from the excerpt, which
  would publish the run's four loop steps as four findings-worth of analysis when one of them was
  the split reported to itself — the paragraph is the most honest thing in the section and D-121 is
  the fix.

## D-121. A sub-population that is the whole split is refused, at a stored ceiling and before anything is stored

- **Date:** 2026-09-08 (Phase 9 follow-up 6)
- **Q:** The sixth live run's third loop step asked `compute_metrics` for `delinq_count_6m`
  `above_median`. `above_median` resolved to `>= median`, the median of `delinq_count_6m` on the
  real credit sample is 0, and the rule therefore selected **every row of both splits**:
  `metrics.<split>.sub.delinq_count_6m_high.share` is 1 on train and test, `auc_gap` is 0 on both,
  `n` is 21,000 and 9,000 — the splits' own row counts — and 22 logical names per split describe a
  population identical to its parent. The tool answered, section 4 gained two tables and three
  interpreting sentences about it, and one of four loop steps was spent. The drafter described it
  honestly. Does the tool answer a rule that selects the whole split?
- **A:** No. `ComputeMetricsTool._select` raises `ToolError` on the D-088 path, so the step is
  recorded `accepted: true, executed: false`, the message is quoted back to the loop in the next
  step's prompt, the step still counts against the maximum of four and the run goes on to draft.
  The message names the **resolved** rule, the share and the bound:
  `the sub-population delinq_count_6m:above_median resolves to
  `delinq_count_6m > median(delinq_count_6m)`, which holds 1 of 'test' — at or above the ceiling of
  0.95 (threshold.O1.slice_max_share) …`.

  Two sub-decisions, both deliberate.

  **The bound is a stored ceiling and not exact degeneracy.** `threshold.O1.slice_max_share` joins
  the three numbers `Thresholds` already carries that decide nothing about pass or fail, at
  **0.95**, and is stored by the tool through `Thresholds.artifact` on every successful slice call
  on D-102's pattern. A slice holding 0.98 of its split has the same defect as one holding 1.0 —
  the residual 2% cannot move a metric far enough to make the slice a different population, and
  the step is spent either way — so testing `share == 1.0` would fix the case the run produced and
  none of the cases next to it. **0.95 says only that nobody has measured a better value**, which
  is what D-102 says about its own 0.08 and 0.10. It is deliberately *not* derived from
  `threshold.O1.slice_min_share` as `1 - 0.10`: sharing the number would mean that re-tuning the
  open-item floor silently re-tunes what the tool will compute at all, which is the coupling D-102
  refused for the same reason.

  **The check is a pre-pass over every split before any of them is computed.** `_subpopulation`
  now resolves the column, the mask, the emptiness and the share for *all* the splits asked for
  first, and only then stores anything. Otherwise a slice that is a proper part of train and the
  whole of test would raise after train's 22 artifacts were already in the store, and the run would
  go on to draft with half a slice in it — a half the section plan would show the drafter and the
  drafter could legitimately cite.
- **Why:** D-088's asymmetry is the whole argument for where this lives. A loop step is the model's
  own extra question and it is refusable on four grounds already; "the rule you asked for is the
  split you already have" is the fifth, and it belongs where the other four are — on the trace, in
  the next step's prompt, and not in the exit code. The alternative the run demonstrated is worse
  than a refusal in every dimension: a step of four, 63 artifact references, two rendered tables,
  three sentences of prose, and a paragraph the report had to spend explaining that the step said
  nothing. Refusing it also does not lose information, because the interesting population was the
  *complement* and D-122 makes it reachable. Rejected alternatives: answering the call and letting
  the section plan drop a slice whose share is 1, which would leave the artifacts in the store for
  the drafter to find and would still have spent the step; raising a candidate finding, which would
  put a defect in *Quaestor's own rule* into the model developer's `findings.json`; making it a
  hard failure like a rule-based plan's `ToolError`, which would throw away a $4 run over a
  question the model was free to ask; and putting the ceiling in `package.yaml`, which is a schema
  change under D-098 for a number no developer has an opinion about.

## D-122. `below_median` and `above_median` partition the split, with the median's own rows in the lower half

- **Date:** 2026-09-08 (Phase 9 follow-up 6)
- **Q:** D-121 refuses the degenerate call, but the run's step was reasonable and the tool's
  reading of it was the problem. `above_median` was `>= median` and `below_median` was `< median`:
  on a discrete column whose median is its minimum — a delinquency count that is 0 for two thirds
  of the book — the upper half is everything and the lower half is nothing, so *neither* rule can
  name the never-delinquent segment that attempts 4 and 5 both found material. Which way does the
  boundary go?
- **A:** `below_median` is `<= median` and `above_median` is `> median`. The two partition every
  split, and the median's own rows are in the **lower** half. On `delinq_count_6m` that makes
  `below_median` the 67% of the book that has never been delinquent and `above_median` the rest,
  both proper parts, both inside D-121's ceiling. `subpopulation_expression` reads
  `delinq_count_6m <= median(delinq_count_6m)` and `delinq_count_6m > median(delinq_count_6m)`,
  which is what the prose quotes in inline code (D-112). `equals:<value>` needs no edge of its own:
  it degenerates on a constant column, and D-121's check is on the **share the rule resolved to**
  rather than on the rule, so one check covers all three.

  The prompt this was written from asked only for `above_median` to become strict `>`. Taken alone
  that leaves the median's own rows in *neither* half — `< median` and `> median` do not partition
  — and on the run's own column it would make `below_median` raise "selects no row" where a 67%
  segment exists. Both halves of the boundary have to move for either goal to hold, so
  `below_median` closed.
- **Why:** Which side the tie goes to is arbitrary in general and not arbitrary here. A median rule
  on a continuous column is unaffected either way, because the sample median of an even-sized draw
  sits between two observations and no row equals it; the choice only bites on the coarse, heaped,
  zero-inflated columns a real credit panel is made of, and on those the interesting population is
  almost always the *mode at the bottom* — never delinquent, no balance, no utilisation. Closing
  the lower side names that population; closing the upper side names its complement and leaves the
  population itself unreachable. That is the case the archive has twice. Rejected alternatives:
  `<` and `>`, which is what the prompt asked for and partitions nothing; keeping `<` and `>=` and
  relying on D-121 to refuse the degenerate arm, which is honest but leaves the segment
  unreachable by any rule the loop can name; adding a fourth rule such as `equals_min`, which is a
  new parameter in the `Args` schema for a case two existing rules can cover; and slicing at a
  quantile the caller passes, which is a wider change to the tool's contract than this defect
  argues for and would need its own decision. Measured: `tests/test_tool_rules.py` builds a count
  whose median is its minimum and asserts the two halves are 2/3 and 1/3, disjoint and exhaustive;
  the same file asserts the halves of `limit_bal` still sum to the split.

## D-123. The loop is told that a rule resolving to the whole split is refused

- **Date:** 2026-09-08 (Phase 9 follow-up 6)
- **Q:** D-121 refuses the call and D-088 carries the message back, so the loop can recover from
  the mistake in one step. It still costs a step of four and a model call to make it. D-089, D-090
  and D-107 each answered the same question the same way — the caller had the fact and the prompt
  did not carry it. Does the loop prompt carry this one?
- **A:** Yes. `_LOOP_INSTRUCTION` gains a paragraph after D-107's column list: a sub-population
  must be a proper part of the split; `below_median` selects the rows at or below the median and
  `above_median` the rows strictly above it, so the two partition the split; and a rule that
  resolves to the whole of it — `above_median` on a column whose median is also its minimum, or an
  equality on a column that never varies — is refused with the share it selected. The refusal in
  `_select` stays, because a model is free to ask for a slice the prompt told it not to and the
  refusal has to be legible when it does.
- **Why:** It is D-107's argument on the next fact: a prompt that invites a mistake and then
  charges a model call for it is a prompt with a fact missing. The paragraph also states the
  *boundary* and not only the refusal, which is the part the model cannot derive — D-122 is a
  choice, and a planner that assumed `>=` would keep asking for the arm that used to work. Saying
  it in the prompt rather than in the `Subpopulation` schema's field description is D-107's
  arrangement again: the schemas are generated from each tool's `Args` and are shown to every
  caller, and this is a sentence about how the bounded loop should choose, not about what the
  argument means. Rejected alternatives: leaving it to D-121's refusal, which is what the run
  measured the cost of; naming the columns whose median is their minimum in the prompt, which
  would put a scan of the data into a prompt builder and would be a fact about the sample rather
  than about the rule; and stating the ceiling's value, which would date the prompt against a
  threshold a configuration may override.

## D-124. The sixth run joins the archive as its negative case

- **Date:** 2026-09-08 (Phase 9 follow-up 6)
- **Q:** D-118 built `tests/test_archive_fixtures.py` over the three archived runs that rendered,
  and every check in it is keyed on a table of expectations — `KNOWN_RESIDUE`, `REDRAFTED`,
  `UNFLAGGED` — that only a run with a repair round in it contributes rows to. The sixth run has
  none: 210 claims, all verified on the first pass, no `repair` event, no re-draft cassette. What
  does adding it to the fixture assert?
- **A:** The negative case of both questions D-118 asks, which no previous run could give. It joins
  `RENDERED_RUNS`, so the two parametrized coverage checks run over four reports and four sets of
  first drafts instead of three, and its claim count (210) joins the row of counts
  `docs/EVALUATION.md` prints. It adds **no** entry to any of the three tables, and that absence
  is asserted rather than left implicit: `test_every_token_of_every_first_draft_of_the_sixth_run_is_a_claim_of_its_report`
  says every one of its seven completions has zero uncovered tokens — the strongest form the
  coverage question has been answered in — and
  `test_the_sixth_run_carries_no_repair_event_and_no_round_to_replay` reads the absence of a round
  out of the trace, `claims.json` and Appendix C together, because those three have to agree for
  the coverage checks to be checks of what the drafters wrote. A third case asserts every written
  line of every first draft is in `report.md`, which the general cassette-to-report check has to
  skip for a repaired section and does not have to skip here; a `[[table:<name>]]` line is the one
  exception, being a directive the renderer replaces (D-115), and the count of them is asserted at
  11 so the exception cannot widen.
- **Why:** A fixture built only on runs that failed something asserts only what failure looks like.
  `KNOWN_RESIDUE`'s docstring says "a new entry appearing here is the next one", and that reading
  depends on the table being a table of *defects* rather than a table of whatever the archive
  happens to hold — which is a claim about runs with no entry, and until now there were none.
  Keeping the run's directory name bare, `credit` rather than `credit-attempt6`, is D-120's: it is
  the run the README excerpts. Rejected alternatives: leaving the run out of the archive and
  testing it only through `tests/test_live_credit.py`, which would leave the two generalised
  coverage checks running over exactly the three runs they were written from; adding empty entries
  to the three tables to make the parametrisation uniform, which would assert nothing and would
  read as though the run had a round; and asserting the zero-residue property inside the
  parametrized check for every run, which is false for the other three and is what
  `KNOWN_RESIDUE` exists to record.

## D-125. The challenger reads a missing value and refuses a non-numeric one

- **Date:** 2026-09-08 (Phase 10)
- **Q:** `challenger_compare` coerced its feature matrix with `pd.to_numeric(errors="coerce")` and
  raised a `ToolError` on any `NaN` in the result, calling it "a non-numeric or missing value".
  The `D1` recipe of `04` §2 puts a hole in `data_test.csv` — a vendor field that went dark for
  30% of the scoring population, which the subject imputes on its way into the fit and does not
  impute in the file it delivers — and that hole is the whole of what the `D1` screen measures.
  With the rule as written, `quaestor validate` on the `D1` variant **exited 1 with no report**:
  the one class of defect the tool could not survive was the one the tool's neighbour exists to
  find. Is a hole a non-numeric value?
- **A:** No, and the two are told apart by comparing the missingness mask before and after
  coercion. A cell that held something and is `NaN` after coercion was not a number, and no model
  in this file can take it: that is still a `ToolError`, now worded "a non-numeric value in
  `[...]`". A cell that was already empty is *missing data*, which
  `HistGradientBoostingClassifier` reads natively, so the challenger is fitted on the matrix as
  delivered. Two consequences are stored rather than left implicit. `challenger.missing_values`
  is a JSON artifact — the share of rows carrying a missing feature value in each split, and one
  sentence saying that the challenger used its own native handling while the champion's treatment
  is the subject's and is not recoverable from the contract files — and it is stored **only when
  something is missing**, on the pattern `ablation.skipped` already sets. And the per-feature
  ablation, which refits a standardised `LogisticRegression`, does not run on a matrix with holes:
  it returns `ablation.skipped` naming that reason. `check_collinearity` is deliberately left
  alone: a variance inflation factor of a column with holes has no answer, its message already
  says to impute or drop, and the `D1` recipe puts the hole in `test` where the VIF is not
  computed.
- **Why:** The guard was written to catch a string in a numeric column and it caught a fact about
  the data instead, and the cost of that conflation is the highest a validation copilot can pay:
  no report at all, on a package whose defect is *reportable*. Distinguishing the two is one line
  of masks and it makes each message true. Storing the missing-value note is D-095's rule applied
  to a measurement that *was* made but not on the same terms as the champion's, and skipping the
  ablation is the same rule applied to one that could not be. Rejected alternatives: imputing the
  holes inside the tool with a zero or a median, which invents a treatment the developer did not
  declare and then compares a challenger fitted on invented data with a champion fitted on
  whatever the subject actually did; dropping the rows with holes, which changes the split the
  comparison is stated on; and leaving the refusal and marking the `D1` recipe `status: dropped`,
  which would publish a guaranteed miss caused by this codebase and score it against the detector.
  Measured: `tests/test_tool_frames.py` carries both halves — a string column still refuses in both
  tools, and a `NaN` column in `test` gives a challenger AUC, a `challenger.missing_values` record
  with `train` at 0.0 and `test` above it, and `ablation.skipped`; the same hole moved into `train`
  still refuses in `check_collinearity`. The clean synthetic subjects have no missing cell, so
  neither control's artifact set changes.

## D-126. A separable split has no calibration slope, and the run says so instead of ending

- **Date:** 2026-09-08 (Phase 10)
- **Q:** `stats.calibration_slope_intercept` fits `logit(P(y=1)) = a + b·logit(p)` by Newton's
  method and raises when it does not converge, which on this design means the sample is separable
  and the maximum likelihood estimate is infinite. The `msr` `L1` variant — `bom_balance_log`
  reading the *closing* balance, which is exactly zero on the loan-months that prepaid — is
  separable by construction: test AUC 1.0000, Brier 1.01e-08. `quaestor validate` on it **exited
  1 with no report**. Separation is the signature of the leak the `L1` screen exists to find. What
  should the tool do?
- **A:** Report it. `stats` gains `SeparableSampleError`, a `ToolError` subclass raised only on
  non-convergence, so a caller can tell "there is no slope here" from "this sample cannot be
  read". `compute_metrics._calibration_fit` catches it and, for that split, stores no
  `calibration_slope.<split>` and no `calibration_intercept.<split>` and stores
  `calibration.separable.<split>` = 1 instead, only in that case. Everything else about the split
  is computed and stored as before — AUC, KS, Brier, log loss, the calibration table, the decile
  table, `calibration.mean_rel_gap.<split>`. `C1`'s slope arm has nothing to read for that split
  and does not run, its mean-predicted arm is unaffected, and a developer-declared
  `calibration_slope` rule falls into the threshold table's existing **"not evaluated"** row, the
  same one any rule nothing answers already lands in.
- **Why:** A validation report that cannot be written about a model whose scores separate its own
  outcome is a validation report missing from exactly the case it was built for. The absent
  artifact is the honest encoding: there is no finite estimate, so there is no number, and the
  report's threshold table says the rule was not evaluated rather than showing a figure that is
  an artefact of where the iteration was stopped. The flag is stored only when it is 1 because its
  presence is the fact — `ablation.skipped` sets the pattern — and storing a 0 on every split of
  every run would move the artifact count of both clean controls for nothing. Rejected
  alternatives: returning the last finite Newton iterate, which is a number whose value is decided
  by `max_iterations` and which a drafter would quote as an estimate; falling back to a penalised
  fit, which silently answers a different question with the same name; raising `C1`, which calls
  separation miscalibration when it is the opposite — the predictions are perfectly ordered and
  the defect is upstream of them; and leaving the failure and marking the `msr` `L1` recipe
  dropped, which would blame a recipe for a hole in the detector. Measured:
  `tests/test_tool_rules.py` scores a test split at 1e-9 and 1-1e-9 by outcome and asserts
  `calibration.separable.test` = 1, no slope and no intercept artifact, test AUC 1.0, no `C1`, the
  threshold row `not evaluated`, and the summary naming `calibration_slope on test`; the clean
  subject stores no separability flag and does store a slope.

## D-127. The seeded-defect generator stays outside the package, and `study build` loads it

- **Date:** 2026-09-08 (Phase 10)
- **Q:** Spec §5 and `CLAUDE.md`'s layout both put `seed()` in `eval/seed.py`, which is not
  shipped: `pyproject.toml` excludes `eval/` from the sdist and the wheel packages `src/quaestor`
  only. Spec §3.14 tabulates `quaestor study build` as a console-script command. Where does the
  code live?
- **A:** In `eval/seed.py`, and `cli.py` loads it from the directory holding `--taxonomy` — which
  is `eval/` for the default `eval/taxonomy.yaml` — under the alias `quaestor_eval_seed`. A
  `--taxonomy` with no `seed.py` beside it is a usage error naming that `quaestor study build`
  works inside a checkout of this repository. `study` takes exactly one action, so
  `quaestor study run` and `quaestor study score` remain argparse "invalid choice" errors, which
  is D-082 unchanged for the two commands Phase 12 writes.
- **Why:** The separation is the same one `quaestor/package/loader.py` is built around: the
  pipeline being measured must not be able to see the answer key, and moving the recipes into
  `src/quaestor` would make the module that plants the defects importable from inside the process
  that is supposed to find them. The command is a development command by nature — it reads
  `subjects/`, it writes a gitignored tree, and its real-data half will read a `--data` path the
  operator names — so binding it to a checkout costs nothing that is not already bound. Rejected
  alternatives: `src/quaestor/study/seed.py` with `eval/seed.py` as a thin re-export, which puts
  the generator in the wheel and contradicts the layout `CLAUDE.md` fixes; a `--seed-module` flag,
  which is a path a user would have to know to pass; and leaving `study build` out of `cli.py` and
  documenting `python eval/seed.py`, which loses the one command spec §3.14 names.

## D-128. `L2` re-keys what it copies, on both subjects, and the medium arm is the honest test

- **Date:** 2026-09-08 (Phase 10; the decision and the sentence are the human's, Cowork 2026-09-09)
- **Q:** D-086 split `L2` into two arms: an identifier overlap above `threshold.L2.overlap` is
  severity **high**, and a feature-vector overlap above the larger of that bound and twice the
  within-train duplicate share is severity **medium**. The taxonomy's `duplicate_test_into_train`
  recipe carries `fresh_ids: true` on both subjects, which means the copied rows are re-keyed and
  only the medium arm can fire. Should the study seed the high arm instead, or as well?
- **A:** No: `fresh_ids: true` on both, and the medium arm is what the study measures. **The
  human's reason, recorded here so that `docs/STUDY.md` can quote it in Phase 12: the recipe
  matches the instance she met and the medium arm is the honest test.** The instance is the
  `met_where` sentence of the same row — "a model whose holdout was drawn after de-duplication on
  account id, but re-issued accounts carried new ids and the same customer appeared on both
  sides". A detection at severity medium is a detection under `04` §4, whose criterion is severity
  at least medium, so nothing about the scoring changes.
- **Why:** The high arm is the case a `SELECT` with a wrong join key produces and it is caught by
  reading two files; the medium arm is the case a de-duplication step lets through, and it is the
  one that needs a within-train baseline to be distinguished from coincidence at all. Seeding the
  arm that the detector finds trivially would measure the wrong thing. `eval/seed.py` raises on
  `fresh_ids: false` rather than silently seeding the other arm, because a recipe that quietly
  answers a different question than its parameters state is worse than one that refuses.
  Measured, at the default panel: on `credit_default`, 45 of the 1,500 test clients copied into
  train under new `client_id`s — feature overlap **3.00%** against an effective bound of 0.50%
  (the declared 0.5% wins, because the within-train duplicate share is 0.0000 on continuous
  synthetic features), identifier overlap **0.0000**, `L2` at severity **medium**; on
  `msr_prepayment`, 461 of 15,382 test loan-months — feature overlap **2.997%**, identifier
  overlap 0.0000, `L2` **medium**.

## D-129. The `msr` `S1` recipe becomes a train-to-test re-cut, not an out-of-time one

- **Date:** 2026-09-08 (Phase 10)
- **Q:** D-046 promised this decision. `04` §2's `msr` `S1` recipe is "train on pre-2015 vintages,
  out-of-time is 2020+ with no monitoring split", whose signal — PSI above 0.25 — would land
  entirely on the train-to-**out_of_time** comparison, which D-046 reports and does not test. As
  written the variant would be seeded and detected by nothing. Redesign or drop?
- **A:** Redesign, along the line D-046 named: the shift must land on the *train-to-test*
  comparison. `train_pre_test_post` rewrites **which rows `splits.json` calls what** and nothing
  else — train is the 2014 vintage through 2019-12, test is every training-vintage loan-month from
  2020-01 onward, and `out_of_time` and `vintage_holdout` keep the rules they had. The panel, the
  features and the beginning-of-month lagging are the clean subject's, value for value; the
  variant's `package.yaml` states the two new split rules in words, so the declaration and the
  code say the same thing. The clean `msr` control still reads 0.0619 on train-to-test and still
  raises nothing, which is the property that makes the seeded variant's 3.016 mean something.
- **Why:** A recipe whose signal lands on a comparison the detector deliberately does not test is
  a statement about the recipe, and publishing it as a miss would make the study's recall figure
  a measurement of `04`'s draft rather than of this pipeline. The redesign keeps the defect the
  row is about — a model fitted before a refinancing wave and used to price servicing after it —
  and moves it onto the comparison a validator would actually make. That test and `out_of_time`
  now hold the same rows is deliberate and is part of the instance: the recipe's own words in
  `04` are "with no monitoring split". Rejected alternatives: dropping the row, which is the other
  branch D-046 offered and would leave the study with 13 seeded variants and no `S1` on the hazard
  subject at all; and re-scoping `S1` to fire on the out-of-time comparison, which D-046 refuses by
  name because the scoping was decided on the clean control before any variant existed.
  Measured, at the default panel: train-to-test PSI **3.016** on `burnout` against 0.25, with
  `loan_age` at 1.680, `note_rate` at 1.342, `incentive` at 0.873 and the score itself at 0.837;
  `S1` at severity medium, and the package's own `psi` rule breached as a `T1` at severity high.

## D-130. `R1` needs a cohort *and* an effect, because the clean process has no trend effect

- **Date:** 2026-09-08 (Phase 10)
- **Q:** The taxonomy proposes `regime_sign_flip`: a synthetic two-level `application_cohort`
  written into `data_<split>.csv` and declared as `regime.column`, with `bill_trend_6m`'s
  relationship to the outcome reversed on one cohort. The mechanism is marked "to confirm". But
  `bill_trend_6m` is not in the clean generating process at all — `_drivers` uses utilisation,
  the two delinquency terms, the payment ratio, the limit, the age and the interaction — so its
  true coefficient is zero and reversing zero reverses nothing. `R1` needs a top-ten feature whose
  fitted coefficient is above 0.05 **in both regimes** and changes sign between them. Confirm or
  drop?
- **A:** Confirmed, with the mechanism made explicit: the recipe adds the effect and then reverses
  it. `application_cohort` is assigned by client index — deterministic, balanced, and drawing no
  random number, so every other column of the panel is the clean control's — and the linear
  predictor gains `1.10 · sign(cohort) · z(bill_trend_6m)`, where `z` is the standardised
  six-month statement slope and `sign` is +1 on one cohort and −1 on the other. The intercept is
  re-solved on the new predictor, as it is for every parameter set, so the base rate does not
  move. `code/features.py` carries the cohort through the engineering step as a non-feature
  column, `code/run.py` writes it into `data_<split>.csv` beside the features, and the variant's
  `package.yaml` declares `regime: {column: application_cohort}` — which is also what makes the
  rule-based plan call `check_stability` at all, since the clean credit subject declares no regime.
- **Why:** "Reverse the feature's relationship with the outcome" presupposes a relationship, and
  the clean subject was built without one for this column; saying so here is the difference
  between a recipe that seeds a defect and a recipe that seeds a coincidence. The pooled fit
  averaging two opposite effects into a coefficient near zero is exactly the `met_where` sentence
  — "the pooled fit averaged the two into a coefficient near zero" — and it is what makes the
  champion look stable when it is not. Rejected alternatives: reversing an existing driver such as
  `delinq_last`, which would change the base rate and the interaction the clean control's `E1`
  depends on; and using the sign of an existing weak coefficient, which D-047 already records as
  sitting inside the seed-to-seed noise. Measured, at the default panel:
  `stability.bill_trend_6m.sign_flip` = **1**, `R1` at severity medium. Two other retained
  features, `delinq_max_6m` and `pay_ratio_last`, also flip on this variant and are collateral:
  they are near-zero coefficients that the cohort split resolves differently, and the study reports
  them under `04` §4's collateral-findings rule rather than as detections.

## D-131. SMOTE is written out by hand, and the resampling never leaves the fit

- **Date:** 2026-09-08 (Phase 10)
- **Q:** The `credit` `C1` recipe is "train on SMOTE-resampled data, report raw probabilities" at
  ratio 1.0. `imbalanced-learn` is not a runtime dependency of this repository and adding one is a
  stop-and-ask. And where does the resampled matrix go — into the fit only, or into the
  `data_train.csv` the variant delivers?
- **A:** Written out by hand, in the variant's own `code/run.py`, from `numpy` and
  scikit-learn's `NearestNeighbors`: pick a minority row, pick one of its five minority
  neighbours, take a uniform point on the segment between them, repeat until the classes are
  balanced. And the resampling stays **inside the fit**: `data_train.csv`,
  `predictions_train.csv` and `splits.json` are the panel's own rows, so the variant carries
  exactly one defect and it is a calibration defect.
- **Why:** Both halves keep the variant a one-defect variant. A dependency added to a seeded
  variant makes the variant harder to run than the subject it came from, and the five lines of
  Chawla et al. (2002) are not the part of this project anybody doubts. Writing the synthetic rows
  into the delivered training file would move every feature distribution as well, so the drift
  screen would fire on a variant seeded for calibration and the study's confusion table would
  record a defect the recipe did not plant; keeping them in the fit is also the instance, where
  the resampler sat inside a modelling pipeline and the data as handed over was real. Rejected
  alternatives: `class_weight="balanced"`, which is a different defect with a different signature;
  and adding `imbalanced-learn` as a dev dependency, which is a dependency question asked to avoid
  writing five lines. Measured, at the default panel: mean predicted **0.4379** against an
  observed rate of **0.2247**, a relative gap of **94.9%** against the 25% bound; the calibration
  slope falls to **0.7952**, outside [0.80, 1.20], so `C1` fires on both arms and the package's own
  declared `calibration_slope` minimum of 0.80 is breached as a `T1` at severity high. The `msr`
  counterpart, `oversample_events` at factor 5 — every prepaid loan-month repeated five times in
  the fitting rows and nowhere else — gives mean predicted **0.03802** against an observed
  **0.008061**, a relative gap of **371.6%**, and `C1` at severity medium.

## D-132. The post-outcome payment is drawn from the latent margin, and it is drawn sharply

- **Date:** 2026-09-08 (Phase 10)
- **Q:** The `credit` `L1` recipe adds `pay_amt_next`, "a synthetic payment in month t+1,
  correlated with the outcome, **not derived from `default_next_month`**", declared honestly as
  `after_outcome` in one variant and as `before_period_start` in the other. Variant B's only
  detector is the single-feature AUC ceiling of 0.90, so the construction has to be strong enough
  to clear it without being a recoding of the target column. What construction?
- **A:** The latent margin. The clean process draws `target = 1[u < sigmoid(eta)]` for a uniform
  `u`; the same draw written as a threshold is `target = 1[margin > 0]` with
  `margin = eta - logit(u)`, so the recipe reuses the uniform it already drew, keeps the target
  bit-for-bit the same, and takes the payment as `usual_payment · sigmoid(-margin / 0.25) ·
  lognormal(0, 0.35²)`, drawn *after* the target so no other column of the panel moves. The
  feature is therefore derived from the latent variable the outcome is a threshold of, and not
  from the outcome column: neither is recoverable from the other, 3.7% of clients pay exactly
  nothing and a defaulted client can still make a payment.
- **Why:** A payment "correlated with the outcome" has to be correlated through something, and the
  only thing available that is not the target column is the latent distress the target is a
  reading of. **The temperature was changed once, and it is the change worth recording.** The
  first construction used 1.0, at which a client a full margin unit into distress still pays a
  quarter of their usual amount; measured, that gave a single-feature AUC of **0.8323** and
  variant B did not fire. The temperature was then set to 0.25 — a client one unit into distress
  pays about two per cent of their usual amount — because that is what the payment received on an
  account that has gone bad looks like, and the 1.0 version was the artificial one. This is not
  the tuning `04` §2 forbids: the detector, its threshold and the recipe's declared parameters are
  untouched, and what changed is the mechanism's fidelity to the sentence the row is about. It is
  reported to Cowork as a change made here, to overrule if the reading is wrong. Measured, at the
  default panel and identical in both arms: single-feature AUC **0.9450** against the 0.90
  ceiling, a margin of **0.045** — the narrowest margin of any recipe in the taxonomy, and one to
  watch on real data. Variant A additionally has `leakage.timing.n_flagged` = 1 and the pre-run
  `L1` candidate `load_package` raises from `package.yaml` alone; both arms carry `L1` at severity
  **high**, and both push the champion's test AUC to **0.9755**, which is the "implausible test
  AUC" the taxonomy's signal column also names and which no rule of this pipeline fires on.

## D-133. `D1`'s hole is in the delivered file and the imputation is in the fit

- **Date:** 2026-09-08 (Phase 10)
- **Q:** `04` §2's `D1` recipe is "one feature is ≈30% missing in test only, imputed as 0 by the
  subject", and its signal is the missingness gap between splits. But `profile_data` measures
  missingness in `data_<split>.csv`, which is the matrix the subject used: if the subject imputes
  before it writes, the gap is zero and the recipe is undetectable by the rule that names it.
  Where does the imputation happen?
- **A:** After the file is written and before the model sees it. The variant blanks
  `pay_ratio_last` on 30% of the held-out rows, writes `data_test.csv` with the hole in it — which
  is what a validator is handed, and what a data vendor's outage actually leaves behind — and
  imputes with 0 on the way into the screen, the fit and the score, so nothing fails and no metric
  complains. `data_train.csv` is untouched.
- **Why:** The recipe's sentence has two halves and they happen at different moments: the field
  went dark in the delivered data, and the pipeline's default filled it in silently. Imputing
  before the write would put the defect somewhere nothing can see it and would make the row a
  guaranteed miss; imputing nowhere would make the subject fail to run, which is an `R0` and a
  different class. This is also the recipe that found D-125. Measured, at the default panel:
  `profile.test.missing.max` **0.3000** against `profile.train.missing.max` **0.0000** and a
  `threshold.D1.missing_gap` of 0.10, `D1` at severity medium; the champion's test AUC falls from
  0.7480 to 0.7446, which no rule fires on and which is the point — a silently imputed field costs
  almost nothing on the headline number.

## D-134. `T1` inflates the package's own declaration and puts the floor between it and the truth

- **Date:** 2026-09-08 (Phase 10)
- **Q:** The `T1` recipe is "`package.yaml` claims test AUC ≈0.05 above the artifact and its
  declared minimum sits so the true value breaches it". `eval/seed.py` writes packages and runs
  nothing, so it cannot read "the artifact": the true AUC is not known until the variant runs.
  What is the claim inflated *from*, and where does the floor go?
- **A:** From the package's own declared claim, and the floor goes half the inflation below the
  claim. `credit_default` declares "AUC on the test split is 0.755", from its committed real-sample
  run; the variant declares 0.805 and moves the declared `auc` minimum on `test` from 0.70 to
  **0.78**, which is `0.755 + 0.05/2`. Both the synthetic truth (0.7480) and the real one (0.755)
  are below it, so the rule breaches in either data mode, and no parameter beyond the taxonomy's
  own `inflate_by` is invented. A package that declares no claim about the metric, or no threshold
  on it, is an error naming which is missing rather than a silently unseeded variant.
- **Why:** Anchoring on the developer's own declaration is what makes the recipe a *false
  declaration* rather than a number chosen against a measurement the developer never made, and it
  is the shape of the instance: documentation that reported a development-sample figure as if it
  were the validation-sample one, with a comfort floor set just underneath it. Deriving the floor
  from `inflate_by` rather than adding a second parameter keeps the taxonomy's row the whole of the
  specification. Rejected alternative: running the subject inside `seed()` to read the true AUC and
  placing the floor from that, which makes seeding cost a model fit, makes a variant's bytes depend
  on the machine that built it and breaks idempotence. Measured, at the default panel:
  `threshold.package.auc.test.min` **0.78** against a recomputed `metrics.test.auc` of **0.7480**,
  `T1` at severity **high**. The claim channel of `T1` — the verifier marking the declaration a
  `mismatch` — is **not** exercised under `--synthetic`, because D-016 does not evaluate developer
  claims there; on this subject the threshold arm is the whole of the synthetic signal, and the
  claim arm is a real-data measurement for Phase 12.

## D-135. The harmless control renames at the boundary and shuffles the panel

- **Date:** 2026-09-08 (Phase 10)
- **Q:** Spec §5's second control is "the two subjects with a harmless perturbation (row order
  shuffled, feature columns renamed with a prefix)". The hazard subject names its feature columns
  in a dozen places — the servicing book, the projection's feature frame, the baseline hazard —
  so renaming them *inside* the subject is a large edit for a control whose whole point is to
  change nothing. Where does the rename happen?
- **A:** At the boundary. The variant renames the declared features in `package.yaml` and renames
  them again in the three files the subject writes that name a feature — `data_<split>.csv`,
  `features.json` and `model_summary.json`'s coefficients and removals — and leaves the subject's
  own internals alone. So every check that reads a declaration and every check that reads a
  contract file still agree about what a column is called, which is the property the control
  exists to test, and a spline column of the hazard design keeps the name it had, because it is
  not a declared feature. The shuffle is a permutation of the panel applied at the same seam every
  data-transforming recipe uses; both subjects draw their splits over *sorted* identifiers, which
  is documented in their own code as the reason a shuffled variant gets the same split.
- **Why:** A control that required a hundred-line edit would be testing the edit. Renaming what
  the package declares and what the subject publishes is the whole of what any check can see.
  Measured, at the default panel: `control_credit_perturbed` raises exactly `{E1 low}` like
  `control_credit_clean` (D-017) and `control_msr_perturbed` exactly `{}` like `control_msr_clean`
  (D-047), and on the credit pair `metrics.test.auc`, `metrics.train.auc`, `vif.max`,
  `condition_number`, `psi.max`, `calibration_slope.test`, `challenger.auc` and
  `challenger.delta_auc` are equal to ten significant figures. **One number does move, on the
  hazard pair, and it is worth naming**: the challenger's AUC goes from 0.7337 to 0.6999 and its
  lead from −0.0415 to −0.0753. `HistGradientBoostingClassifier` turns early stopping on
  automatically above 10,000 rows and draws its validation split by position from a fixed random
  state, so shuffling the rows changes which loan-months it holds out; the credit subject's 3,500
  training rows are below that threshold and its challenger is unchanged. Neither figure is
  anywhere near the +0.03 that raises `E1`, so the finding set is identical — but a control that
  is bit-identical in every number would have been the stronger claim, and this one is not.

## D-136. What every recipe produced on the synthetic subjects, measured

- **Date:** 2026-09-08 (Phase 10)
- **Q:** The taxonomy's `expected_signal` column is a prediction as well as an acceptance test.
  What did each recipe actually produce at the declared seed and the documented panel size, and
  which of them only just cleared its bound?
- **A:** All fourteen fired, and the four controls raised what D-017 and D-047 fix. Measured at
  seed 20260901 on this machine (Python 3.12.14, scikit-learn 1.9.0, numpy 2.5.3, pandas 3.0.5),
  `credit_default --synthetic 5000` and `msr_prepayment --synthetic 2000`, through `run_model` and
  the `rules_only` configuration, which calls no model:

  | variant | measured | bound | finding |
  |---|---|---|---|
  | `credit__L1__after_outcome_declared` | `leakage.timing.n_flagged` 1; single-feature AUC 0.9450 | ≥ 1; > 0.90 | `L1` high |
  | `credit__L1__after_outcome_hidden` | single-feature AUC **0.9450** | > 0.90 | `L1` high |
  | `msr__L1__eom_balance` | single-feature AUC **1.0000**, test AUC 1.0000 | > 0.90 | `L1` high |
  | `credit__L2__contamination` | feature overlap **3.00%**, id overlap 0.00% | > 0.50% | `L2` medium |
  | `msr__L2__contamination` | feature overlap **2.997%**, id overlap 0.00% | > 0.50% | `L2` medium |
  | `credit__R1__regime_flip` | `stability.bill_trend_6m.sign_flip` **1** | = 1 | `R1` medium |
  | `credit__C1__smote_uncalibrated` | mean-to-observed gap **94.9%**, slope 0.7952 | > 25%; ∉ [0.8, 1.2] | `C1` medium |
  | `msr__C1__oversampled_hazard` | mean-to-observed gap **371.6%** | > 25% | `C1` medium |
  | `credit__S1__segment_shift` | `psi.limit_bal` **1.196**, score PSI 0.187 | > 0.25 | `S1` medium |
  | `msr__S1__vintage_shift` | `psi.burnout` **3.016**, score PSI 0.837 | > 0.25 | `S1` medium |
  | `credit__M1__vif_reintroduced` | `vif.max` **121,914**, kappa **1,023** | > 10; > 30 | `M1` medium |
  | `credit__D1__test_only_missingness` | test missingness **0.300**, train 0.000 | > 0.10 | `D1` medium |
  | `credit__T1__false_claim` | declared minimum **0.78**, recomputed AUC 0.7480 | breach | `T1` high |
  | `msr__X1__projection_sign` | convexity **+336,109**, −300 bp and +300 bp both +168,055 | declared negative; monotone | `X1` high |

  **The margins are not alike, and two of them are thin.** `credit__L1__after_outcome_hidden`
  clears its ceiling by **0.045** (0.9450 against 0.90) and is the recipe to watch when the study
  runs on real data; every other bound is cleared by at least a factor of two, and most by orders
  of magnitude. `credit__C1__smote_uncalibrated`'s slope arm is also close — 0.7952 against a floor
  of 0.80, a margin of 0.005 — but its mean-predicted arm clears 25% by a factor of nearly four, so
  the `C1` finding does not depend on the slope.

  **Collateral findings, reported here because `04` §4 scores them separately.** Every
  `credit_default` variant except the two `L1` arms also raises the clean control's own `E1` at
  severity low, which is D-017's expected finding travelling with the subject rather than a false
  alarm; on the two `L1` arms the leak lifts the champion above the challenger and `E1` stops
  firing, and a `C1` appears instead (train slope 1.383). `credit__S1__segment_shift` and
  `msr__S1__vintage_shift` each raise a `T1` at high, because the shift breaches the package's own
  declared `psi` ceiling of 0.25 — a true consequence of the seeded defect, not a second defect.
  `credit__C1__smote_uncalibrated` raises a `T1` on the declared calibration-slope floor for the
  same reason. `msr__L1__eom_balance` raises an `X1` at high: a champion dominated by a leaked
  balance projects a value curve whose convexity is positive where the package declares negative.
  `msr__L2__contamination` and `msr__S1__vintage_shift` each raise an `R1` on one weak coefficient
  (`burnout`, `sato`), which D-047 already records as sitting close to the seed-to-seed noise on
  this subject.
- **Correction, 2026-09-17 (the recalibration-thread close):** that last sentence is false on HEAD,
  and has been since **D-164**. The precision gate D-164 added to `R1` — `|coef / s.e.|` at least
  `threshold.R1.sign_flip_z`, 2.0, in **every** regime — removed both of those collateral `R1`s,
  and D-164's own entry names these two variants as the cases the rule was decided for. The
  coefficients are exactly the ones this paragraph calls weak: on `msr__L2__contamination`,
  `burnout` is **+0.222939081** falling at **z +1.97** and **−0.048147452** rising at **z −0.17**;
  on `msr__S1__vintage_shift`, `sato` is **−0.062575844** falling at **z −0.70** and
  **+0.210835407** rising at **z +1.11**. Each clears the 0.05 materiality gate in both regimes and
  none of the four reaches |z| 2. Re-measured at `666a41b` on this machine (Python 3.12.14,
  scikit-learn 1.9.0), `--synthetic 2000` through `run_model` and the `rules_only` configuration,
  `--llm fake`, no model call: `msr__L2__contamination` raises **`{L2 medium}`** and
  `msr__S1__vintage_shift` raises **`{T1 high, S1 medium, C1 medium}`**. The rest of the collateral
  paragraph and the whole of the table above are unchanged, and the original sentence is left as it
  was written on the pattern of D-160.
- **Why:** These are the numbers the study's recall is measured against and the numbers a later
  change would first show up in, so they are recorded here rather than left in a test's
  assertions, on the pattern D-047 and D-053 set. The two thin margins are named because a recipe
  that barely clears its bound on synthetic data is a recipe whose real-data result says as much
  about the panel as about the detector.

## D-137. Five of the eighteen variants are synthetic-only, and Phase 12 is where that is paid

- **Date:** 2026-09-08 (Phase 10)
- **Q:** `quaestor study build` writes synthetic-mode variants; `04` §3 runs the study on the real
  samples as well, and the prompt for this phase says real-data variants are built at study time
  from a `--data` path. Which recipes actually work in both data modes as written, and which do
  not?
- **A:** Nine of the fourteen work in both, because they hang off the seam *after* the subject has
  chosen its data mode, or they only edit `package.yaml`: `duplicate_test_into_train` on both
  subjects, `train_on_segment`, `train_pre_test_post`, `test_only_missing`,
  `smote_no_recalibration`, `oversample_events`, `false_declared_claim` and
  `projection_sign_error`, and so do both `harmless_perturbation` controls. **Five variants are
  synthetic-only** and are named here rather than discovered in Phase 12:
  `credit__L1__after_outcome_declared` and `credit__L1__after_outcome_hidden` need a
  `pay_amt_next` column the real sample does not carry; `credit__R1__regime_flip` needs an
  `application_cohort`; `credit__M1__vif_reintroduced` needs `bill_last_adj`, which its patched
  `engineer` computes from the raw statement schema that `--data` mode never sees, because
  `sample.py` writes the engineered features and `code/run.py` reads them back; and
  `msr__L1__eom_balance` patches `build_panel`, which a `--data` run does not call at all, since
  `sample_freddie.py` builds the panel and `code/run.py` reads the four split files it wrote.
  `quaestor study build` therefore offers no `--data` flag in this phase: it would build packages
  that cannot run.
- **Why:** All five need a *column* that the real sample does not have, and a column is built by
  `sample.py` and `sample_freddie.py` rather than by a recipe — so the real-data half of these
  five is an edit to the samplers, which are the two files that read the real data and which no
  test in this repository may exercise. Writing that edit blind, in the phase that cannot run it,
  is how a Phase 12 session discovers at the shell that five variants do not build. Recording the
  list is the alternative. The synthetic construction of the post-outcome payment also does not
  carry over unchanged: it reads the latent margin of the generating process (D-132), and a real
  panel has none, so the real-data variant will have to draw the payment conditioned on the
  observed outcome with overlap — a weaker claim than the synthetic one, and one whose
  single-feature AUC has to be measured rather than assumed, given that the synthetic arm clears
  its ceiling by only 0.045. Rejected alternative: writing the `--data` branches now, guarded and
  untested, which puts five untestable code paths in a generator whose whole value is that a
  variant is what it says it is.

## D-138. Every Probatio case input is built by running the pipeline, and pinned byte for byte

- **Date:** 2026-09-08 (Phase 11)
- **Q:** Spec §6 says a `draft_section` case's input is `{section, artifacts_json, candidates,
  guidance}` "for the synthetic credit subject" and that an `extract_claims` case's input is "a
  fixed section text". Where do those bytes come from, and what stops them drifting away from the
  pipeline they are supposed to be about?
- **A:** They are **generated, never typed**, by `tests/probatio/casebuilder.py`, which runs
  `validate(..., llm=OfflineLLM(), config="full_agent", synthetic=5000)` once and *spies* on the
  two collaborators that decide what a model is shown -- `pipeline._draft_inputs` and
  `pipeline.follow_up_plan` -- rather than re-deriving their answers. What a case carries is the
  object the drafter and the loop were actually handed, serialised: `ArtifactBrief.to_payload()`
  for the artifacts, `FindingCandidate.model_dump()` for the candidates, the retrieved spans'
  bodies for the guidance. The `extract_claims` prose is section 2 of
  `eval/results/first-live/credit/report.md`, cut at the heading and passed through the pipeline's
  own `drafted_prose`, and its six `contains` needles are values of that run's own `claims.json`.
  `tests/probatio/test_inputs_pinned.py` then asserts, offline and in the ordinary suite, that
  every committed file is **byte-identical to what the builder produces now**, that each case
  rebuilds into the objects the run produced, and -- the load-bearing one -- that the prompt a case
  builds is the prompt the pipeline sent, to the byte. Re-running
  `python tests/probatio/casebuilder.py` is the fix when it fails.
- **Why:** A cassette is keyed on the prompt, so a case that builds a *nearly* identical prompt
  records a tape for a call the pipeline never makes and the suite measures the harness. And a case
  file is committed data, which drifts silently: a drafting case whose artifacts no longer match
  the store still drafts something, and a `contains` needle that is no longer a claim of the live
  report still passes as long as the model writes the digits. Neither failure shows in a green
  suite and both would be replayed from a tape for as long as the tape lives. Spying rather than
  re-deriving is D-084's rule -- a second expression of "which artifacts does section 4 get" is a
  second chance to disagree with the first -- and it is why the builder holds no selector logic at
  all. Rejected alternatives: hand-written YAML reviewed once, which is the drift this entry
  exists to prevent; building the inputs inside the test at run time, which would make the case
  file unreviewable and would silently re-record a different tape on the day a selector changed;
  and asserting a spot check (a few artifact names, a candidate count) instead of the whole prompt,
  which passes on exactly the changes that invalidate a tape.

## D-139. Probatio's provider is passed into the systems under test with no adapter

- **Date:** 2026-09-08 (Phase 11)
- **Q:** `CLAUDE.md` says Quaestor's `LLM` protocol is "structurally identical to Probatio's
  `Provider`", and `llm/base.py` says the identity exists so that Phase 11 can pass the fixture
  straight in. Is it actually identical where it matters, or does the test layer need an adapter?
- **A:** No adapter. `probatio.plugin.provider` yields `_ObservingProvider(CassetteProvider(...))`,
  whose `complete(prompt, *, system=None, **params)` returns a `probatio.providers.Completion`;
  Quaestor's `LLM` is a `Protocol` and its consumers -- `structured()`, `Drafter.draft`,
  `extract`, `follow_up_plan` -- read `.text`, `.model`, `.tokens_in`, `.tokens_out`, `.cost_usd`,
  `.latency_ms` and `.raw`, every one of which Probatio's `Completion` carries under the same name
  and the same type. Nothing in Quaestor does an `isinstance` against its own `Completion`, so the
  two classes never have to be the same class. The one wrapper the suite adds, `_LastAnswer`, is
  **not** an adapter: it passes the call through unchanged and remembers the answer's text.
- **Why:** The wrapper exists because a Probatio case asserts on **what the model returned** and
  all three systems under test return something parsed -- markdown, an `Extraction`, a
  `FollowUpAction`. Asserting `schema_valid` on a re-serialisation of the parsed object would be a
  statement about pydantic rather than about the model, and an answer `structured()` refused twice
  would arrive as an exception where the suite needs a failing assertion. So each system under test
  catches `LLMOutputError` and returns the raw answer, which is also what makes
  `--probatio-provider fake --cassette=off` run all ten cases to completion and fail their content
  assertions instead of erroring. Probatio's own `schema_valid` strips one wrapping code fence
  before parsing, exactly as `structured()`'s `strip_fence` does, so a fenced answer is judged the
  same way on both sides of the boundary and no normalisation is needed here.
  Rejected alternatives: a `QuaestorLLM` shim converting one `Completion` into the other, which is
  a class whose only job is to be a place where the two definitions can drift apart; and returning
  the parsed object and dropping `schema_valid`, which is the one assertion in the family that is
  about the model's own output shape.

## D-140. Where the tapes and the baselines live, and Probatio's cassette keys confirmed

- **Date:** 2026-09-08 (Phase 11)
- **Q:** `.gitignore` says the tapes live in `tests/probatio/cassettes/`; Probatio resolves
  `--cassette-dir` and `--baseline-dir` against rootdir and defaults them to `cassettes/` and
  `.probatio/baseline/`, and `03-RUNBOOK.md`'s two commands pass neither. Where do the files go?
  And Quaestor's own run cassettes collide across run directories -- do Probatio's?
- **A:** Both directories are set in `pyproject.toml`'s `addopts`, so the runbook's commands write
  and read `tests/probatio/cassettes/` and `tests/probatio/baseline/` without a flag, and so does
  CI's gate-6 step. Every case declares `snapshot: scores`, which is what gives
  `--update-baseline` something to write.
  **Probatio's keys do not collide, and the mechanism is not the same one.** A tape is one file at
  `<cassette-dir>/<suite>/<case_id>.json`, where the suite is the test module's stem, so two cases
  can never share a file; inside the file an interaction is keyed on
  `stable_hash({prompt, system, model, params, template})`, and `template` is the judge prompt
  template's hash when a judge is speaking, so a judge call and a system-under-test call carrying
  the same text are different interactions. A metamorphic variant is filed under the id of the case
  it was taken from, which is why one drafting case's tape holds all eight of its calls.
- **Why:** D-079 already said the two stores have different jobs; this entry records the
  measurement behind the half of it that was an assumption. Quaestor's own `llm/recording.py` is
  keyed by request **alone** -- `stable_hash(system, prompt, params)` -- because the question a
  replay asks there is "what did the model answer *this*", and the accepted consequence is that
  re-running a validation over the same artifacts hits the same tapes wherever they were written.
  Probatio's key adds the case and the suite as *path segments* rather than as hash inputs, which
  is the stronger arrangement for a test suite: a stale tape names the case it belongs to in its
  own path, so a human reading a `StaleCassetteError` is told which case to re-record rather than a
  hash. Nothing here needed changing. Rejected alternative: passing `--cassette-dir` on the command
  line, which would make the runbook's two commands differ from the ones CI runs and from the two
  printed in the Phase 11 report.

## D-141. `input.guidance` is one joined string and the distractor is a JSON string

- **Date:** 2026-09-08 (Phase 11)
- **Q:** `@format_jitter(field=...)` reformats a **string** and `@distractor_robust` inserts
  **strings** into a list. The drafter needs six typed `GuidanceSpan`s and a list of typed
  `ArtifactBrief`s. How do the two relations reach real inputs without the case carrying a shape
  the drafter cannot use?
- **A:** Two encodings, each with one rule.
  **Guidance.** `input.guidance` is the six retrieved spans' **bodies**, joined with
  `"\n\n---\n\n"`; each span's `doc`, `section_id` and `heading` live in the case's `metadata`, and
  the system under test zips the two back together positionally. So the jitter reformats exactly
  the prose the retriever returned and never touches the `[[reg:...]]` citation the drafter is told
  to copy -- which the casing transform would have upper-cased into a citation that resolves to
  nothing. `test_inputs_pinned.py` asserts that all three jitter transforms leave the separator
  count unchanged, so the zip cannot silently lose a span.
  **The distractor.** One artifact of the *other* subject -- a mortgage-servicing projection has no
  place in a credit report -- carried as a one-line JSON object string and appended to
  `input.artifacts_json`. `probatiosupport.artifact_briefs` parses a string item and copies a
  mapping item, which is **the only tolerance this harness adds** to what the pipeline itself
  accepts.
- **Why:** The alternative for guidance was to make `input.guidance` the whole span list as JSON
  text, and every one of the three fixed transforms breaks it: the markdown transform wraps it in a
  fence, the casing transform upper-cases the first sentence and therefore the first keys, and
  `json.loads` then fails -- so the relation would measure whether the harness can parse its own
  input rather than whether the drafter's verdict moves. Splitting identity from body puts the
  jitter on the only part of a span that is prose.
  For the distractor, the alternative was to teach `DistractorRobust` about mappings, which is a
  change to a dev dependency for one case, or to leave the string in the list untouched and let the
  drafter be shown a JSON string among its artifacts, which is a shape the pipeline never produces.
  **What this relation cannot see is recorded rather than claimed:** the distractor is in the
  variant's own `artifacts_json`, so a drafter that cites it still satisfies the case's assertions
  and the relation reports no violation. The relation measures whether the *verdict moves*, and on
  this suite a citation of the irrelevant artifact would have to be caught by the judge's fourth
  criterion or by a reader, not by the relation.

## D-142. The `above_median` refusal spec §6 and the phase prompt ask for cannot be provoked

- **Date:** 2026-09-08 (Phase 11)
- **Q:** The Phase 11 prompt asks for a `plan_followup` case "whose menu shows that `above_median`
  on a discrete column would be refused, asserting the returned action is not that", citing D-121
  and D-123. What does that case look like on the synthetic credit subject?
- **A:** It does not exist, and the second planning case tests the same behaviour on two refusals
  that are real. Two facts make the asked-for case unbuildable.
  **`above_median` can no longer resolve to a whole split at all.** D-122 made `below_median` be
  `<= median` and `above_median` be `> median`. On a column whose median is its minimum,
  `P(X <= min) >= 0.5` by the definition of a median, so `above_median` selects at most half the
  split -- and D-121's ceiling is 0.95. The degenerate rules that remain reachable are
  `below_median` on a near-constant column and `equals:` on a constant one.
  **No rule reaches the ceiling on this subject.** Measured over all twelve columns of both splits
  of the synthetic credit run at seed 20260901, the largest share any median rule selects is
  **0.7754** (`below_median` on `default_next_month`, train) and the largest `equals:` share is the
  same. D-121's guard is unreachable offline; it is reachable only on the real sample, where
  `delinq_count_6m`'s median is 0.
  So `plan_followup.after_refusal` carries a history of **two failures the code actually
  produces**, generated by calling the code in the builder rather than written out: an action
  refused as inapplicable (`check_stability` on a package with no `regime.column`, D-089) and one
  accepted whose tool then raised (a sub-population of `credit_limit`, which is not a column of
  this subject -- the fourth live run's own mistake, D-088 and D-107). The case asserts that the
  third step repeats neither.
- **Why:** A case whose assertion cannot fail for the reason it names is worse than no case: it
  reads in the suite as coverage of D-121 and covers nothing. `not_contains: ["above_median"]` on a
  menu of every column would forbid an action the tool would happily run, which is a false alarm
  waiting to be recorded into a tape; restricting the menu to the one column whose median is its
  minimum would make the assertion fair only if the model could tell -- and the loop prompt lists
  column *names* and no medians, so it cannot.
  **A defect in `_LOOP_INSTRUCTION` was found while establishing this. It is fixed in D-146**,
  by the operator's decision, on the same day and before any tape was recorded; the paragraph
  below is what was reported to them and the reasoning that put the choice in their hands. D-123's
  paragraph said "`below_median` selects the rows at or below the column's
  median and `above_median` the rows strictly above it, so the two partition the split; a rule that
  resolves to the whole of it -- `above_median` on a column whose median is also its minimum, or an
  equality on a column that never varies -- is refused with the share it selected". Its own first
  clause makes its first example impossible: under `>` that rule selects at most half. The sentence
  describes the pre-D-122 semantics and survived the rewrite. It is a wording defect in a live
  prompt, it changes what the planner is told, and every `plan_followup` tape will be keyed on the
  text that carries it -- so fixing it *before* the recording is cheaper than fixing it after, and
  the choice belonged to the operator, who was told in the Phase 11 report rather than presented
  with a silent edit to the planner in a phase whose scope is the test layer. They chose to fix it
  (D-146), which is why this entry's own case still stands: correcting the example does not make
  D-121's guard reachable on the synthetic subject, it only stops the prompt naming a rule that
  cannot trip it.
  Rejected alternatives: seeding a degenerate column into the subject so that the guard can fire,
  which changes the clean control D-017 fixes; writing the refusal message by hand, which is a
  second copy of a sentence the tool owns (D-084); and dropping the second planning case entirely,
  which would leave D-088, D-089, D-090 and D-107 -- four decisions bought with live runs -- with
  no case in the layer built to hold them.

## D-143. `tests/probatio/` has no `conftest.py`

- **Date:** 2026-09-08 (Phase 11)
- **Q:** The pinning tests need one shared offline run. A session fixture belongs in a
  `conftest.py`. Why is there not one?
- **A:** Because it breaks six existing modules. `tests/` is not a package, so pytest imports every
  `conftest.py` under the bare module name `conftest`, and the first one imported wins in
  `sys.modules`: `tests/probatio/conftest.py` sorts before `tests/test_*.py`, so
  `from conftest import REPO_ROOT, load_module` -- which `tests/test_seed.py`,
  `tests/test_verifier_eval_fixtures.py` and four others do -- resolved to the new file and the
  collection failed with `ImportError`. The fixture is a module fixture in
  `tests/probatio/test_inputs_pinned.py`, which is the only module that wants it.
- **Why:** The alternatives are worse for the size of the problem. Adding `__init__.py` to
  `tests/probatio/` alone does not help, because pytest then walks up for the package root and
  `tests/` has none; adding it to `tests/` as well changes how every existing module is imported
  and how `tests/conftest.py`'s own `sys.path` care (its docstring's whole subject) behaves, for a
  fixture with one consumer. Renaming the shared helpers so that a second `conftest` is harmless
  would edit six modules to accommodate a seventh. Recorded here because the absence looks like an
  oversight and the next session to add a fixture will otherwise repeat the failure.

## D-144. `--runs 5` is declared on the extraction test, and the floor is 0.8

- **Date:** 2026-09-08 (Phase 11)
- **Q:** Spec §6 says `extract_claims` is "run with `--runs 5` and `@flaky_tolerant(p=0.8, n=5)`".
  `--runs` is a command-line flag that applies to every case in the session. Is it passed?
- **A:** No, and it must not be. `@flaky_tolerant(n=5)` overrides `--runs` for the marked test, so
  the marker alone gives the extraction case its five runs; passing `--runs 5` as well would
  multiply the seven drafting cases **and their seven metamorphic variants each** by five -- 280
  drafting calls and 280 judge calls instead of 56 and 56, on a record run that is already an hour
  of model time. The runbook's two commands therefore stay exactly as `03-RUNBOOK.md` writes them,
  with no `--runs`.
  **The floor is 0.8 because the extractor's labels vary and its values do not.** D-111 recorded
  the count-against-ratio disagreement: the same number is classified `count` on one run and
  `ratio` on the next. A `unit` that moves changes the answer's bytes without changing any value
  the case asserts on -- but `schema_valid` and `contains` are evaluated over the whole answer, and
  a run in which the model also drops or re-orders a claim fails the `contains` list. Four of five
  is the tolerance that lets one such run through while still failing a case that misses a value
  twice; `p = 1.0` would make a known, recorded and harmless instability into a red suite, and
  `p = 0.6` would pass a case that got two of its six values wrong.
- **Why:** The Wilson interval Probatio prints beside the pass rate is the honest part of this and
  decides nothing: five runs support `[0.28, 0.99]` around a rate of 0.8, which is a statement
  about the run length, not about the extractor. The floor is a declared tolerance, and this entry
  is where the declaration is argued rather than in the marker. Rejected alternatives: asserting
  only the values and dropping `schema_valid`, which removes the one assertion that would catch an
  answer whose shape changed; and recording more samples per interaction to tighten the interval,
  which is `--runs 25` at five times the bill for a bound nobody reads.

## D-145. What one record run costs, measured before it is made, and the budgets that follow

- **Date:** 2026-09-08 (Phase 11)
- **Q:** Spec §6 asks for a `budget` block on every case "so a record run cannot silently spend".
  What number goes in it?
- **A:** One derived from the committed live run rather than guessed. Least squares over the
  eighteen calls of `eval/results/first-live/credit/` gives **$10.43 per million input tokens and
  $24.65 per million output tokens** -- blended rates that include what the CLI's `total_cost_usd`
  reports for a turn partly served from cache, reproducing all eighteen recorded costs to within
  **6.6%** -- with **2.04 prompt bytes per input token** over that run's seven drafting calls and
  a wall clock of **9.96 ms per output token plus 7.0 s**. Each case's ceiling is
  `2.5 x` its own estimate, rounded up: twice because `structured()` may re-ask once and a re-ask
  is the same call again, and a half more because a regression over one run is not a guarantee. No
  latency ceiling is below two minutes.
  Measured on the built cases, the record run is **119 provider calls** -- 56 drafting calls (seven
  cases x eight runs each: the original, three permutations, three jitters and one distractor), 56
  judge calls (one per drafting run), five extractions and two planning steps -- at an estimated
  **$25.69** and **62 minutes** of model time. The largest single prompt in it is **53,196 bytes**,
  the judge's grading of the whitespace-jittered outcomes draft.
- **Why:** The last number is the one that had to be checked rather than estimated. Probatio
  0.1.0's `claude-cli` provider passes the prompt as a **positional argument** with no stdin
  fallback, which is exactly the failure D-078 exists for -- above about 64 KiB a single argument
  is rejected by macOS before the CLI runs. Every prompt in this suite is under that threshold, by
  20%, so the shipped provider is usable as it is; the run that would break it is one that adds a
  follow-up step to a drafting case, since the live outcomes prompt with four executed slices was
  **71,325 bytes**. That is recorded here so the next person to widen a case knows what it costs.
  The budgets are enforceable in the record run and not in the offline one: a ceiling is checked
  against `Completion.cost_usd`, which the `claude-cli` provider fills from the CLI's payload and
  the fake leaves `None`, so `--probatio-provider fake` reports ten unenforceable ceilings and says
  so. Rejected alternatives: one flat ceiling for every case, which is either too loose for the
  planning cases or too tight for the outcomes one; and a `--probatio-prices` table, which would
  put a list price in the repository that no committed run produced and that `CLAUDE.md`'s "no
  number a committed run did not produce" rule would not survive.

## D-146. The loop prompt's degenerate-slice example is corrected to one D-122 can produce

- **Date:** 2026-09-08 (Phase 11, decided by the operator)
- **Q:** D-142 found that `_LOOP_INSTRUCTION`'s standing paragraph names an example its own first
  clause makes impossible. What replaces it, and when?
- **A:** `below_median` on a column whose median is also its **maximum**, changed now, before any
  tape is recorded. The paragraph reads, with the one substitution:

  > A sub-population must be a proper part of the split. `below_median` selects the rows at or
  > below the column's median and `above_median` the rows strictly above it, so the two partition
  > the split; a rule that resolves to the whole of it -- `below_median` on a column whose median
  > is also its maximum, or an equality on a column that never varies -- is refused with the share
  > it selected, because its metrics would only repeat the split's.

  Nothing else in the prompt, in `_mask`, in `subpopulation_expression` or in the D-121 ceiling
  changes. `tests/test_pipeline.py`'s existing assertion is tightened from the generic substring
  `"on a column whose median is also its"` -- which the falsified sentence and the corrected one
  both satisfy -- to the corrected example in full, plus a negative assertion that the falsified
  one is gone.
- **Why:** The example was arithmetically impossible under the semantics the same sentence
  states. `below_median` is `<= median` and `above_median` is `> median` (D-122), so on a column
  whose median is its minimum `P(X <= min) >= 0.5` by the definition of a median and
  `above_median` selects at most half a split -- it can never reach D-121's 0.95 ceiling. The rule
  that *can* is the mirror of it: when the median is the maximum, `<= median` selects everything.
  The correction is one word pair and it is length-preserving, which is the reason D-147 exists.
  **Timing was the whole of the decision.** A cassette key is a hash of the prompt, so this edit
  invalidates every `plan_followup` tape. Made before the recording it costs nothing; made after
  it costs both planning tapes and a second live sitting. That is why it was reported at the end
  of the build rather than folded silently into the test layer, and why it is dated to the day the
  operator answered.
  What the correction does **not** do is make D-142's case buildable: no rule reaches the ceiling
  on the synthetic subject at any median, so the guard stays unreachable offline and
  `plan_followup.after_refusal` still tests the loop's response to two refusals that are real.
  Rejected alternatives: deleting the example and leaving only the rule, which drops the concrete
  case a model reads fastest and leaves the equality example unbalanced; naming the real sample's
  `delinq_count_6m` explicitly, which puts a column of one subject's real data into a prompt every
  subject sees; and describing both degenerate median rules, which is a longer sentence for a
  second case a planner has no way to detect from a list of column names.

## D-147. A case pins the digest of the prompt it sends, not the length of it

- **Date:** 2026-09-08 (Phase 11)
- **Q:** D-138 pins each case by rebuilding its prompt and comparing it with the pipeline's, and
  each case carries `metadata.prompt_bytes`. D-146 changed `_LOOP_INSTRUCTION` by swapping
  `above_median` for `below_median` and `minimum` for `maximum` -- both substitutions the same
  length. Would the offline suite have noticed?
- **A:** No, and it does now. Every case gains `metadata.prompt_sha256`, the first sixteen hex
  characters of the SHA-256 of **the prompt its system under test actually sends** -- not the one
  `Drafter.prompt` or `loop_prompt` composes, but that string with `structured()`'s strict-JSON
  instruction and the pydantic schema appended, which is what a cassette key hashes. The builder
  computes it by running the case's own system under test against a `_PromptRecorder`, a provider
  that answers with one fixed valid object and keeps the prompt, so the digest comes from the real
  code path and no composition is restated. `test_every_case_pins_the_prompt_its_tape_will_be_keyed_on`
  fails with the two digests when they diverge and names the fix: re-run the builder and re-record
  that family's tapes.
  Measured, on the tree as it stands: a length-preserving edit to `_LOOP_INSTRUCTION` leaves
  `test_planning_prompts_rebuild_byte_for_byte` green and fails the digest assertion alone; an
  edit that also changes the length fails both.
- **Why:** The prompt is the only thing a tape is keyed on, so it is the only thing whose change
  makes a committed tape wrong. `prompt_bytes` was chosen in D-138 as a cheap witness and it is a
  weak one -- it cannot see a substitution, a transposition or a reordering, which is most of what
  prompt editing consists of. The distinction matters more here than in an ordinary suite because
  the failure is silent in the *worst* direction: a stale tape does not error, it replays an answer
  to a question nobody asked any more, and every assertion written against it keeps passing.
  D-138's whole-prompt equality check does not cover this either, because both sides of that
  comparison are built from the same edited instruction.
  Hashing the sent prompt rather than the composed one is deliberate: `structured()` appends a
  schema generated from a pydantic model, so a field added to `DraftedSection` or `FollowUpAction`
  changes the prompt and the tape key without changing a line of the drafter. The schema files are
  separately pinned, but a digest that stopped at the caller's prompt would let a change reach the
  tapes through a door the pin does not watch.
  Rejected alternatives: committing the whole prompt beside each case, which is 190 KB of a second
  copy of what the builder can produce and a second thing to keep in step; hashing the caller's
  prompt only, which is the door above; and relying on Probatio's own `StaleCassetteError`, which
  is the right error but arrives at the *next recording session* -- after a green offline suite has
  said the layer is sound.

## D-148. The grounding rubric asked the judge to quote, which made 80% of its replies unparseable

- **Date:** 2026-09-08 (Phase 11, found by an interrupted record run)
- **Q:** The first record run was stopped after two cases. `draft_section.summary` passed and
  `draft_section.conceptual_soundness` failed 3 of 4 assertions. Is the failure the drafter's, the
  case's, or live variance?
- **A:** None of the three. It is `rubrics/grounding.md`'s, in its last sentence: "The `rationale`
  names the criterion that decided the verdict **and quotes the sentence that decided it**". The
  judge obeyed, inside a JSON string field, and produced

  > `{"verdict": "pass", "score": 1.0, "rationale": "All five criteria hold: ... (e.g. "dropping
  > the most recent delinquency status costs -0.07585 [[art:3150b111:...]]"), ...`

  which stops parsing at column 209 on the first unescaped quotation mark. `Judge.grade` raises
  `JudgeOutputError`, `evaluate_judge` returns a failed result, and a verdict of **pass at score
  1.0** is thrown away. Measured over the three tapes the interrupted run left: **16 of 20 judge
  replies, 80%, are unparseable** -- fourteen on an unescaped quote and two on a literal newline
  inside the string. The four that parsed simply happened not to quote anything.
  The rubric now forbids all three: no quotation marks, no line breaks, no citations or backticks
  copied out of the prose, with the reason given ("makes your reply unparseable and throws your
  verdict away"). `test_the_rubric_forbids_the_quoting_that_made_80_per_cent_of_replies_unparseable`
  asserts the prohibition and the absence of the old sentence.
  A second thing this exposed and fixed: **a rubric is part of every judge prompt**, so editing it
  changes every judge interaction key and strands every judge tape -- which D-147's
  `prompt_sha256` does not see, because it digests the system under test's prompt and a judge call
  is not the system under test. Each drafting case now also carries `metadata.rubric_sha256`,
  Probatio's own `Rubric.content_hash` so that one number means the same thing in the case file, in
  a validation record and in the unvalidated-judge warning.
- **Why:** The instruction was written to make a failing verdict diagnosable from the report -- a
  rationale that names the sentence is worth more than one that names a criterion -- and it was
  written without asking what a quotation mark does inside the JSON object the same prompt demands.
  The failure mode is the worst available: it does not look like a formatting problem, it looks
  like the drafter failing a grounding rubric, and on a red suite of seven cases a reader would go
  looking at the prose. It cost about $10 of live calls to find, which is the argument for the
  rubric pin rather than against it -- the *next* rubric edit will be caught by a green-to-red
  offline suite instead of by a record run.
  What was **not** wrong is worth recording too, because it is what the run bought: on
  `conceptual_soundness` the drafted section passed `schema_valid`, `contains` and `not_contains`,
  and the judge's own verdict on it was pass at 1.0. The drafter, the case, the schemas and the
  three relations were all working on the first live call ever made through this layer.
  Rejected alternatives: marking the drafting test `@flaky_tolerant`, which tolerates a formatting
  defect and multiplies seven cases and their variants by `n`; relaxing Probatio's `JudgeVerdict`
  parse, which is a dev dependency's deliberate strictness and not ours to loosen; and repairing
  the replies in the tapes by hand, which would make the committed evidence disagree with what the
  model said.
  **This entry is a stopgap, and its final form is D-153's.** Every prohibition it adds to the
  rubric works around a parser that discards a repairable reply: six of the sixteen failures were a
  `rationale` string left unclosed before the object's own `}`, and two were a complete first
  object followed by a corrected second one -- in both, a parser reading the first balanced JSON
  object would have recovered a verdict the model got right. Filed against Probatio as **issue 1 in
  `notes/probatio-issues.md`**. Until it is fixed, this rubric spends part of its instruction budget
  on JSON syntax rather than on the thing it grades.

## D-149. Probatio's session cost total excludes judge calls, so `--max-cost` under-counts by half

- **Date:** 2026-09-08 (Phase 11)
- **Q:** `--max-cost` is the only ceiling that covers a whole record run, and the Phase 11 report
  offers it as the guard against a runaway sitting. Does it see everything the run spends?
- **A:** No. `RunState.observe` records a completion only while a sink is open, and
  `Probatio.check` opens one around the system under test (`_call_sut`) and around each relation
  variant (`_call_variant`) -- but a `judge` assertion is evaluated inside `evaluate_case`, which
  is outside both. So judge spend reaches no sink, no case cost and no session total.
  Measured on the three tapes of the interrupted record run: **$5.1071 of drafting calls and
  $4.6768 of judge calls, so `--max-cost` sees 52% of what the run actually spends.** Probatio's
  own `session.py` docstring states the opposite -- "they are real money and they do count toward
  the session total under `--max-cost`" -- so this is a defect in probatio 0.1.0 as shipped and not
  a design we are reading wrongly.
  Nothing in Quaestor changes. The consequence is recorded where it is acted on: a `--max-cost`
  value passed to the record run is roughly **half** the dollars it will let through, and the
  Phase 11 report states the ceiling in both currencies rather than one.
- **Why:** Per-case `budget.max_cost_usd` is unaffected and is still worth having: it covers the
  calls a case's own system under test makes, which is what a case can be held responsible for,
  and D-145's ceilings are sized for exactly that. It is the *session* figure that is partial. The
  distinction matters because the two ceilings are offered to an operator for different jobs -- one
  stops a case that has gone wrong, the other stops a sitting that has gone long -- and an operator
  who reads "cost: $16.40" at the end of a run that spent $31 has been told something false about
  the second.
  **Amended 2026-09-09, after the third record run.** There is a second half to this, and it is
  the half that bites: `--max-cost` is **not a circuit breaker**. The ceiling is read in
  `pytest_sessionfinish`, so it can only set a non-zero exit status *after* the session has
  finished spending. The third record run was given `--max-cost 7`, spent **$7.59 of visible
  drafting cost** -- $12.34 in total across the three cases, by their tapes -- and ran to
  completion; the ceiling failed the session afterwards rather than stopping it. Taken with the
  judge blindness above, a `--max-cost N` should be read as "fail the sitting if it turns out to
  have spent more than about `N / 0.6` dollars", not as "stop at `N`". The only ceiling that can
  actually halt work mid-run is the per-case one, and even that fails the case after its calls are
  made. What genuinely bounds a sitting is `-k`: recording three cases costs three cases.
  Not fixed here, and the reason is `CLAUDE.md`'s: `probatio-llm` is a dev dependency of this
  project, a patch to it is not in Phase 11's scope, and a monkeypatch in `tests/probatio/` that
  wrapped the judge provider in a sink would put a copy of Probatio's accounting in Quaestor's
  suite -- two expressions of one rule, which is D-084's whole lesson. It is filed against Probatio
  as **issue 2 in `notes/probatio-issues.md`**, covering both halves -- judge spend invisible to the
  total, and a ceiling evaluated in `pytest_sessionfinish` that cannot stop a run -- with the
  measured 58% visible share that makes both concrete. Rejected alternative: summing the tapes after the run
  and printing the real total, which is a useful script and still not a ceiling -- it cannot stop
  anything, because by the time it can be computed the money is spent.

## D-150. The Claude CLI provider's timeout is raised to 600 s in `addopts`, and latency ceilings go uniform

- **Date:** 2026-09-09 (Phase 11, after the second record run)
- **Q:** The second record run recorded 34 of 37 tests and lost three drafting cases --
  `data_integrity`, `sensitivity` and `monitoring` -- to `ProbatioConfigError: the Claude CLI did
  not answer within 120s`. That is a provider timeout, not a verdict. Where is it configured, and
  what else has to move with it?
- **A:** Two changes, and one of them was not the obvious one.
  **The provider timeout goes to 600 s, in `pyproject.toml`'s `addopts`, because that is the only
  place probatio 0.1.0 will take it.** `ClaudeCLIProvider(timeout_s: float = DEFAULT_TIMEOUT_S)`
  defaults to 120.0 and is reachable only through `--probatio-timeout`, a session-wide flag; there
  is **no per-case timeout**. A `timeout` in a case's `params` would not work twice over: the
  adapter pops `model` and files everything else under `probatio_ignored_params` without acting on
  it, and `params` is hashed into the interaction key, so the case would silently strand its own
  tape. Setting it in `addopts` also keeps the runbook's record command unchanged, which is
  D-140's argument for the two directory flags.
  **The per-case latency ceilings become one uniform 480 s, and stop being estimated at all.** They
  had to move regardless of the provider: `sensitivity` and `monitoring` carried the 120 s floor of
  D-145, exactly the provider's own default, so even without the kill they would have failed their
  own budgets. But the deeper reason is that the latency model does not work. D-145 fitted wall
  clock as `9.96 ms x output tokens + 7.0 s` over one run's eighteen calls; measured against the
  record run, `findings` was predicted at 15.1 s and one of its variants took **100.2 s**, out by a
  factor of 6.6, because wall clock here is dominated by service variance and not by how much the
  model writes. The cost model from the same run, by contrast, predicted the whole run's spend to
  within 6%. So cost keeps its per-case ceiling and latency gets one number taken from the observed
  tail -- twice the longest single call any tape holds (106.5 s, itself censored, since the three
  calls that overran 120 s recorded nothing), doubled again for a run in which `structured()`
  re-asks.
  The two now sit in the right order: `--probatio-timeout` at 600 s is the hung-process ceiling and
  `max_latency_ms` at 480 s is the budget, so a slow case **fails a verdict** and only a hung
  subprocess errors. Before this change they were inverted -- the hang ceiling was tighter than the
  budget -- which is why three cases errored instead of failing.
- **Why:** `DEFAULT_TIMEOUT_S`'s own docstring says "two minutes is a hung-process ceiling, not a
  budget", and on this suite it was acting as a budget: a drafting call that legitimately writes
  seven thousand tokens over a 39 KB prompt takes longer than that often enough to lose three cases
  in ten. Raising it does not weaken anything, because the thing that was actually protecting the
  run -- the per-case ceilings, and `--max-cost` -- is unchanged in cost terms.
  Abandoning the latency regression rather than re-fitting it is the honest move and the reason is
  recorded rather than the coefficient: a model fitted on eighteen calls of one sitting was always
  going to describe that sitting, and one more sitting is not enough to fit a distribution whose
  spread is the point. A uniform generous ceiling says what it is -- a pathology detector -- where
  a per-section number derived from a broken fit would have claimed a precision it does not have.
  **The changed budget does not strand a tape**, which is why the three cases can be re-recorded
  alone: an interaction key hashes the prompt, the system prompt, the model, the params and the
  judge template, and a baseline is keyed on `prompt_hash`, which Probatio defines over `input`,
  `system` and `params` only -- "its assertions, its budget, its tags may change without
  invalidating the baseline". Verified rather than assumed: after the rebuild all seven complete
  tapes replay to 34 passed with **zero provider calls** and every snapshot `unchanged`.
  Rejected alternatives: leaving the timeout at 120 s and shortening the drafting prompts, which
  changes what the layer tests to fit a subprocess ceiling; passing `--probatio-timeout` on the
  command line, which would make the runbook's command differ from CI's and from the one printed in
  the Phase 11 report; and re-fitting the latency model on the two runs now in hand, which is two
  sittings of a quantity that varied 6.6-fold within one of them.

## D-151. A replay session has to name the model the tapes were recorded against

- **Date:** 2026-09-09 (Phase 11, found replaying the first record run's tapes)
- **Q:** `03-RUNBOOK.md`'s replay line and `CLAUDE.md`'s gate condition 6 are both
  `pytest tests/probatio --cassette=replay`, with no provider and no model. The tapes were
  recorded through `--probatio-provider claude-cli --probatio-model "claude-opus-5[1m]"`. Does
  replay find them?
- **A:** No, not as written, and the flag has to be supplied. `interaction_key` hashes
  `{prompt, system, model, params, template}`, where `model` is `resolve_model(params, model)` and
  the fallback is the *answering adapter's* own model. A replay session with the default provider
  builds `FakeProvider(model=model or "fake-1")`, so with no `--probatio-model` every key is
  computed against the literal string `fake-1`, no tape carries it, and every case fails with
  `StaleCassetteError: the prompt, the model or the params changed since it was recorded`. The
  message is accurate and the diagnosis it invites -- that the prompt drifted -- is wrong.
  So `--probatio-model "claude-opus-5[1m]"` goes into `pyproject.toml`'s `addopts` beside the
  cassette and baseline directories. **The provider stays `fake`**: replay never touches the inner
  adapter, so naming a model does not make a session capable of a live call, and a machine with no
  Claude CLI installed replays these tapes exactly as one with it. That is what lets CI's gate-6
  step stay the bare command the runbook prints.
- **Why:** Putting the model in the key is right, and Probatio argues it well -- a tape recorded
  against one model replaying silently against another is worse than no tape. What is wrong is only
  the *default*: a fake provider's model name is a plausible-looking string that no real tape can
  ever match, so the failure lands on every case at once and looks like prompt drift. Configuring
  it in `addopts` rather than in each of the three commands is D-140's rule, and here it is
  load-bearing rather than tidy: `pytest -q` is gate condition 1 and passes no Probatio flags at
  all, so without this the whole suite is red the moment tapes exist.
  Recorded as a finding against spec section 6 as well: the spec's acceptance line
  (`pytest tests/probatio --cassette=replay` passes with zero provider calls) is achievable only
  with a flag the spec does not mention, and this entry is where the difference is written down
  rather than absorbed into a command nobody can explain.
  Rejected alternatives: recording without `--probatio-model`, which the plugin refuses outright
  for a live provider -- and rightly, since the tape would then be keyed on the string
  `claude-cli`; passing the flag in each of the three commands, which puts a fact about the
  committed tapes in three places that can disagree; and `--probatio-provider claude-cli` in
  `addopts`, which would make every offline session construct a live adapter it must never call.
  **The consequence for anyone changing the recorded model.** Its name now lives in exactly two
  places -- inside every interaction key on every tape, and in `pyproject.toml`'s `addopts` -- and
  they move together: recording against a different model means re-recording every tape and
  editing that one line in the same commit, because a tape whose key names one model and an
  `addopts` that names another is a suite that fails every case at once with a message about
  prompt drift.

## D-152. A quarter of the judge's replies still do not parse, and every relation violation is one

- **Date:** 2026-09-09 (Phase 11, measured on the second record run's tapes)
- **Q:** D-148 fixed the rubric sentence that made 80% of judge replies unparseable. On the second
  record run, are they parsing?
- **A:** Better, and not yet well. **8 of 32 judge replies on the seven complete tapes still do not
  parse -- 25%, down from 80%** -- and the cause is now a different one. Six of the eight simply
  **omit the closing quotation mark** of the `rationale` value, ending `...unavailable.}` where
  `...unavailable."}` was needed, on rationales of 250 to 450 characters. The other two are a model
  that noticed its own mistake, wrote a paragraph about it, and emitted a **second** JSON object
  after the first. None is a truncation: every completion reports `stop_reason: end_turn`.
  **No case verdict is affected, and that is exactly why this needs saying.** A case's verdict is
  its original run's assertions, and all four complete drafting cases pass 4 of 4. The eight
  malformed replies are all on metamorphic *variants* -- so each one makes its variant's verdict
  differ from the original's, which Probatio reports as a **relation violation**. The counts match
  exactly: `distractor_robust` 1 of 4, `format_jitter` 3 of 12, `order_invariant` 4 of 12, **8 in
  total, against 8 malformed replies.** So on this recording *every observed relation violation is
  a JSON formatting failure in the grader*, and there is **no evidence of a single genuine
  violation** -- no permutation, reformatting or distractor changed what the drafter did. That is a
  good result about the drafter and a worthless one about the relations, and spec §6's acceptance
  criterion asks for the relation rates by name.
- **A, continued -- what is done about it now:** nothing to the rubric, and the three timed-out
  cases are re-recorded against the rubric as it stands. The reason is sequencing, not tolerance. A
  rubric is part of every judge prompt (D-148), so any edit to it strands the judge half of all
  seven complete tapes and turns a $10.66 re-record of three cases into a $27 re-record of ten,
  discarding the $20.41 already spent. And the rubric has **one more revision coming regardless**:
  the operator's 40-row labelling and `probatio validate-judge` are still outstanding, and a κ
  measured against human labels is the evidence that would say what the rubric should ask for. Two
  re-records for two rubric edits is one too many, so the order is: record the three, take the
  layer green, measure κ, and fold whatever the labelling says about the rationale into one
  revision and one re-record.
  **Superseded in part, 2026-09-09.** The deferral above rested entirely on the cost of a rubric
  edit -- "two re-records for two rubric edits is one too many". D-153 then found a defect in the
  rubric's criterion 5 that *has* to be fixed, which forces exactly the re-record this entry was
  avoiding. So the rationale cap is folded into that same edit and ships with it, and the argument
  for waiting for the kappa no longer applies: the kappa will now be measured against the corrected
  rubric, which is the better order anyway.
  Written down rather than absorbed: until that recording is made, the relation rates this layer
  publishes are contaminated at 25% and the Phase 11 run-log line says so. The remedy, when it comes, is most
  likely to cap the rationale hard -- fifteen words, not one sentence of any length -- or to drop it
  and return `verdict` and `score` alone, which `JudgeVerdict` already permits since `rationale`
  defaults to empty and unknown keys are ignored.
- **Why:** The instinct is to fix the rubric now, and it is wrong for a measurable reason: the fix
  is unverifiable offline. There is no way to know whether a fifteen-word cap stops a model dropping
  a closing quote without recording against it, so "fix it now" means buying one experiment at $27
  and possibly buying a second. Recording the three, on the other hand, buys a complete, green,
  committable layer for $10.66 whose case verdicts are sound and whose one weak number is measured
  and published. That is the project's own standard applied to itself -- the differentiator is an
  evaluation that publishes misses, and a relation rate known to be 25% grader noise is a miss to
  publish, not one to hide behind a rubric edit nobody has tested.
  Rejected alternatives: fixing the rubric now and re-recording all ten, which spends $27 to
  replace one unvalidated rubric with another unvalidated rubric before the κ that would tell us
  which is better; tolerating malformed replies by relaxing the judge assertion, which is D-148's
  rejected alternative for the same reason; and dropping the three relations from the drafting test,
  which removes the measurement instead of the noise and is the one thing spec §6 names.

## D-153. The grounding rubric's criterion 5 forbade what two sections' briefs require

- **Date:** 2026-09-09 (Phase 11, found by the third record run)
- **Q:** The third record run recorded all three outstanding cases and left two of them failing on
  a judge verdict. `sensitivity` scored 0.80 with the rationale that "the closing paragraph fails
  the last criterion by declaring that the cross-regime stability comparison and the rate-shock
  quantities are not defined or not carried for this model and that no regime column exists";
  `monitoring` scored 0.80 for "declaring quantities absent from this validation, stating that no
  realised post-sample outcomes were available and that no override history exists to analyse". Is
  the defect in the drafter, in a brief, or in the rubric?
- **A:** In the rubric, and the drafted prose is right. Read what the drafter actually wrote:

  > Two of the analyses this section would otherwise carry are not defined for a model of this
  > type, and they are recorded in Appendix D on that basis. The stability comparison across
  > declared regimes presupposes a regime column in the evaluation data, and no regime column is
  > declared for this package...

  That is section 5's brief, quoted almost back at it: "**Say plainly which of these do not apply
  to this model type**; they are listed in Appendix D and must not be described as though they had
  been run." Section 7's is the same shape: "**name anything this validation could not cover** that
  monitoring should watch instead." And D-114 already drew the line this rubric erased -- D-100's
  prohibition "is about numbers ... it could not stop a section calling an entire **activity**
  absent, because an activity is not an artifact selector" -- and its rejected alternatives name a
  standing rule against saying an activity was not performed as wrong precisely because it "would
  also forbid Appendix D's own subject matter".
  So criterion 5 is rewritten to say what D-100 says and no more: a sentence claiming a **number**
  is not available, not carried, not computed or not recomputed is a failure, and two kinds of
  sentence are named as explicitly not violations -- an analysis that does not apply to this model
  type, and something this validation could not cover that monitoring should watch. The test given
  is whether the sentence is about a quantity a computed artifact could have supplied, with one
  example each way. `test_the_rubric_lets_a_section_say_an_analysis_does_not_apply` pins it.
  **The fix is neither of the two things the operator asked me to choose between.** It is not the
  monitoring brief: D-114 already fixed section 7's one illegitimate absence sentence (benchmarking,
  contradicted by section 2's own challenger comparison) and these sentences are not that -- there
  is no artifact and no other section that contradicts them. And it is not a red test documenting a
  drafter defect: there is no drafter defect to document. On both sections the drafter obeyed its
  brief, cited Appendix D for the reader, and was failed by a grader I wrote.
- **Why:** This is the first genuine finding the Probatio layer has produced about the *project*
  rather than about itself, and it is worth being clear that it points at the rubric: two of seven
  sections, independently, on the first recording where the judge's replies parsed. A rubric is a
  specification of what a good section looks like, and mine contradicted two of the seven briefs
  the pipeline ships. Had it been shipped, the layer would have held the drafter to a standard the
  report cannot meet, and the natural reading of a red suite -- that the drafter is wrong -- would
  have sent the next reader to the prose.
  **The cost, stated because it is the reason this is one decision and not two.** A rubric is part
  of every judge prompt, so this edit strands the judge half of all seven drafting tapes: measured
  on the tapes as they stand, re-recording those seven is **124 calls, $28.92 (of which $16.73,
  58%, is visible to `--max-cost`) and about 79 minutes of model time.** The three non-drafting
  cases carry no judge assertion and are untouched. Because a re-record is now unavoidable, D-152's
  rationale-length fix is folded into the same edit rather than deferred to the kappa: fifteen
  words, nothing after the closing brace, and a reminder to close the string.
  Rejected alternatives: lowering the judge threshold to 0.8, which passes these two sections by
  passing any single-criterion failure anywhere; dropping criterion 5 altogether, which is the same
  re-record and abandons D-100's rule instead of stating it correctly; and leaving the two cases red
  as documentation, which `CLAUDE.md`'s gate condition 1 forbids and which would publish a false
  claim about the drafter in the one artefact of this phase a reader will trust.
  **Measured on the recording this entry produced: 60 live judge replies, 0 unparseable.** The
  progression across the three recordings is 80%, 25%, 0%. The criterion-5 rewrite is a permanent
  correction -- it is what D-100 and D-114 already say -- but the four prohibitions this rubric
  carries about JSON syntax are, with D-148's, a **stopgap for Probatio issue 1**
  (`notes/probatio-issues.md`): a parser that read the first balanced JSON object would have
  recovered every one of the 24 verdicts the two earlier recordings threw away. When that is fixed
  upstream those four bullets can go and the rubric can spend its whole instruction budget on
  grounding, which is what it is for. Until then they stay and this sentence says why.

## D-154. An offline fake run must never be allowed to write a Probatio baseline

- **Date:** 2026-09-09 (Phase 11)
- **Q:** All three cases of the third record run reported `snapshot scores_changed` against a
  baseline whose every content assertion had **failed** -- `schema_valid fail 0.000`,
  `contains fail 0.000`, `judge fail n/a`, `budget_cost fail n/a` -- on cases that had just been
  recorded live and passed 4 of 4. Where did that baseline come from?
- **A:** From my own offline verification run. `pytest tests/probatio --probatio-provider fake
  --cassette=off` is the step that proves the cases load and the systems under test are wired, and
  the fake's answers fail every content assertion by design (D-139). `BaselineStore.compare` is
  called with `update=False` on every run and **records a baseline when the case has none** -- so
  that fake run silently created baselines for exactly the three cases whose baselines were absent
  at the time, stamping the fake's failures as the reference. The record run then compared its real
  results against them and reported drift.
  The rule from now on: **every fake or `--cassette=off` invocation passes
  `--baseline-dir` to a throwaway path.** The verification command is
  `pytest tests/probatio -q --probatio-provider fake --cassette=off --baseline-dir $(mktemp -d)`,
  and it is written that way in the Phase 11 report and in the run log.
- **Why:** The failure is silent in both directions and cost real money to see: nothing about a
  fake run announces that it has written a reference, and nothing about `scores_changed` says the
  reference came from a fake. It looked like the recording had drifted, which is the one thing it
  had not done. The asymmetry that makes it dangerous is that `compare` refuses to *overwrite* an
  existing baseline without `--update-baseline` but is happy to *create* one -- reasonable for a
  first real run and wrong for a run whose provider is a stub.
  This is not a Probatio defect and is not filed as one: a baseline recorded on first sight is the
  documented behaviour, and a suite that runs a fake against a real baseline directory has
  misconfigured itself. It is a defect in how this suite was being exercised, which is why the
  remedy is a command and a rule rather than a patch. Rejected alternatives: setting
  `snapshot: off` on every case, which throws away the drift detection the second runbook command
  exists to establish; deleting `tests/probatio/baseline/` before each record run, which is the
  workaround I had been applying by hand and which fails the first time somebody forgets; and
  teaching the suite to refuse a baseline write when the provider is fake, which puts a rule about
  Probatio's own store inside Quaestor's tests.

## D-155. Two record sittings ended on a fast exit 1 from `claude -p` that did not reproduce

- **Date:** 2026-09-10 (Phase 11, operator observation across four record sittings)
- **Q:** Two of the four recording sittings ended early, not on a timeout and not on a verdict, but
  on the Claude CLI exiting **1 within a few seconds** of being invoked. A trivial `claude -p` call
  made immediately afterwards, by hand, answered normally. What is recorded about it, and what is
  done?
- **A:** Recorded, not diagnosed, and worked around by the shape of the commands. What is known:
  the failure is fast -- seconds, against the 14 to 106 seconds a real drafting call takes -- so it
  is not `--probatio-timeout`, whose message is different and whose ceiling was 600 s by then; the
  CLI exits non-zero, which `ClaudeCLIProvider._payload` turns into `ProbatioConfigError` quoting
  the tail of stderr; and it did **not** reproduce on a hand-run call seconds later, which rules
  out the argument vector, the model name and the empty working directory, all of which were
  unchanged. Most likely a transient on the service or the subscription session rather than
  anything this repository controls, but that is a guess and it is labelled as one: nothing in the
  tapes carries the stderr, because a call that fails is a call that records nothing.
  What follows from it operationally is the useful half. **A record run is not atomic and must not
  be treated as one.** A sitting that dies part way leaves complete tapes for the cases that
  finished, a partial tape for the one in flight, and nothing for the rest -- exactly the state the
  second sitting left. So recording is done in `-k`-scoped sittings, a dead sitting costs only the
  cases it had not reached, and a partial tape is moved aside rather than kept: `record()` replaces
  the samples of keys it re-records in the same session and leaves the others in place, so a
  half-recorded case that is re-recorded ends up carrying dead interactions from the attempt that
  died.
- **Why:** It is written down because the next operator will meet it and will otherwise spend the
  time this one did deciding whether the suite is broken. The distinguishing signature is the one
  to remember: **seconds, not minutes.** A drafting call that fails in three seconds did not fail
  for any reason this repository can fix, and the response is to re-run the `-k` selection for the
  cases with no tape rather than to change a case, a prompt or a ceiling.
  It is deliberately **not** filed against Probatio: the adapter reported what the subprocess did,
  with stderr quoted, which is the correct behaviour for an exit code it cannot interpret. Nor is a
  retry added here -- a retry inside a recording adapter would turn a transient into a silent extra
  call against the same tape key, and D-088's argument applies unchanged: the failure belongs on
  the record, not in the exit code of the sitting.
  Rejected alternatives: retrying the call inside `probatiosupport`, which puts a provider concern
  in the harness and would spend money without saying so; recording everything in one sitting with
  a longer ceiling, which is what made the loss expensive the first time; and asserting the
  stderr text in a test, which would pin a message this repository does not own.

## D-156. Section 6's candidate line and its findings list are one object, not two

- **Date:** 2026-09-15 (Phase 11, found reading the `draft_section.findings` tape)
- **Q:** The `draft_section.findings` case's prompt carries
  `candidates raised for this section: none -- describe nothing as a finding` (D-091) and, eleven
  lines below it, `Findings to write about, in this order` with `### F-001 · E1 effective
  challenge · severity **low**` and its four evidence hashes. All eight recorded drafts resolved
  the contradiction the same way and the judge passed all eight. Is that the case's defect or the
  pipeline's?
- **A:** The pipeline's, and the state is not merely reachable live -- it is the **only** state a
  run with a finding can produce. `_candidates_block` read `candidates` and `_findings_block` read
  `findings`, two arguments of `Drafter.prompt` filled from two objects in `_draft_inputs`:
  `candidates_by_section.get(brief.section, [])` and the promoted `findings`. And
  `SECTION_FOR_CLASS` maps **no** defect class to `ReportSection.findings` -- `section` on a
  finding names the material it rests on and not where it is printed, which D-103's entry spells
  out -- so `candidates_by_section[findings]` is empty on every run that has ever been made, while
  the findings list beneath it is not. Every section-6 prompt this project has built for a package
  with a finding has told the drafter to describe nothing as a finding and then ordered it to
  describe one.
  The two are now **one source**. `_candidates_block(candidates, findings)` derives the line from
  `findings` whenever the prompt also lists them, and falls back to the candidate list and then to
  `NO_CANDIDATES` when it does not; `Drafter.prompt` passes both. A section-6 prompt with a finding
  now reads `findings raised by this validation: 1, listed in full below with the heading to copy`,
  names each by id, class, severity and tool, and adds the two prohibitions the recording earned:
  do not write that no finding was raised, and do not move one to the open items.
  `test_a_prompt_that_lists_a_finding_never_says_there_are_none` asserts, for **every** section and
  a listed finding, that `NO_CANDIDATES` is absent and the heading is present; two more assert the
  empty case still says none, and that a candidate handed to section 6 does not produce a second
  account of the same list. The same fix makes `DRAFT_INSTRUCTION`'s own standing rule true of
  section 6 for the first time: "Call something a finding only if it is in the candidate list at
  the end of this prompt" was a rule section 6's prompt broke.
- **A, continued -- what the drafter did under the contradiction, which is why this is a defect
  and not a wording complaint.** All eight drafts wrote a sentence saying no finding was raised
  ("This validation raised no findings against this model package at version 1.0"; "This validation
  raised no candidate defects, so this section reports no findings") and moved `E1` into
  `### Open items`, phrased as a question for the model developer. Every number in all eight is
  cited and correct -- 0.824 `challenger.auc`, 0.748 `metrics.test.auc`, 0.07598
  `challenger.delta_auc`, 0.03 `threshold.E1.delta_auc` -- and the grounding judge passed 8 of 8 at
  1.0. So the failure is **silent demotion with perfect grounding**: a published finding of
  severity low disappears from the findings section of the report, the severity counts and anything
  that reads them, and not one check in this project can see it. The verifier measures whether a
  number is what the store says; it has no opinion about whether a finding was reported. The judge
  measures grounding; the prose was grounded. The renderer prints `FindingsDocument`'s own
  headings, so a reader gets `### F-001` from the renderer and "no findings were raised" from the
  drafter in the same section, which is D-091's two-contradictory-sentences failure in a new place.
  The drafter was obeying the more specific of two instructions it was given, and it chose the one
  that understates the report's own conclusions, which is the safer of the two ways to be wrong and
  is still wrong.
- **Why:** D-091 fixed this shape once already, and fixed it in the prompt's *words*: the Phase 8
  line stated a fact without its consequence, so it was rewritten to state the consequence. What it
  did not do is remove the second copy of the fact, and a year of live runs later the second copy
  is what failed. Two renderings of "what may this section call a finding" are two chances to
  disagree, which is D-084's rule and the same argument D-100 makes about a selector that fell
  behind `package.yaml`. Putting the fix in `Drafter.prompt` rather than in `_draft_inputs` is
  deliberate: the contradiction is assembled where the two blocks meet, so that is where it is made
  unassemblable, and a future caller of `Drafter.prompt` -- `rules_only`, a repair round, a study
  configuration not yet written -- cannot reproduce it either.
  **The cost is one tape and the operator was told before it was spent.** The edit changes the
  section-6 prompt, so `draft_section.findings`'s tape is stranded and nothing else is:
  `prompt_bytes` 21,947 -> 22,296 and `prompt_sha256` `405694630f3c281f` -> `2747cbbb12cc5043` on
  that case alone, with the other six drafting cases, both planning cases and the extraction case
  byte-identical, which is D-147's pin doing exactly the job it was added for. The re-record is
  `pytest tests/probatio -q -k "draft_section.findings" --probatio-provider claude-cli
  --probatio-model "claude-opus-5[1m]" --cassette=record`, one case, 16 calls, measured at **$2.36
  on the stranded tape** ($1.31 drafting over eight calls at $0.163 each, against the case's $0.34
  ceiling, and $1.05 of judge calls that `--max-cost` cannot see, D-149).
  Rejected alternatives: editing the case's `input.candidates` by hand to carry the `E1` candidate,
  which is the one thing D-138 forbids -- a case input is generated by running the pipeline, never
  typed, and a hand-typed candidate would make this case the only one in the layer that describes a
  state no run produces while leaving every future run's prompt contradictory; giving section 6 its
  candidates in `_draft_inputs` by matching promoted candidates back to findings, which is a second
  derivation of the promotion `FindingsDocument` already performed and would disagree with it the
  first time a merge changed (`candidates_merged` is 1 here and need not be); mapping some defect
  class to `ReportSection.findings` so that `candidates_by_section` is non-empty, which breaks what
  `section` means on a finding and every cross-reference the report builds from it; and adding a
  renderer check that section 6's prose does not say "no finding" while `findings.json` holds one,
  which is D-091's and D-103's rejected alternative for the third time -- a grep over natural
  language standing in for a fact the prompt can simply carry.

## D-157. The grounding judge's kappa is 0.771, recorded as it stands, and the rubric is not revised here

- **Date:** 2026-09-15 (Phase 11, labelled by the operator, decided in Cowork)
- **Q:** Every graded judge assertion in this layer printed "1 judge verdict(s) from a rubric with
  no validation record", seven warnings on every replay. What does the rubric measure against human
  judgement, and what follows from the disagreements?
- **A:** **Cohen's kappa 0.771 over 40 labelled drafter outputs, agreement 38/40 (0.950).**
  Cowork built the labelling packet from the committed tapes -- all five live judge fails plus a
  round-robin across the seven sections, shuffled, the judge column hidden until the human's labels
  were in -- and `probatio validate-judge --labels tests/probatio/labels/grounding.labels.csv
  --rubric <abs>/tests/probatio/rubrics/grounding.md --judge-column judge --human-column human`
  reports `n=40 agreement=0.950 kappa=0.771`, which is the operator's own figure to three decimals,
  so there are not two numbers to reconcile. Both label distributions are **35 pass / 5 fail**, and
  the 2x2 of (human, judge) is pass/pass **34**, pass/fail **1**, fail/pass **1**, fail/fail **4**.
  The record is written to `.probatio/judges/grounding.validation.json`, which is where
  `ProbatioSettings.validation_dir` reads it from -- `<rootdir>/.probatio/judges`, fixed, with no
  flag to move it -- and both it and the 40 labelled rows are committed. The seven warnings are
  gone. `test_the_grounding_judge_has_a_validation_record_for_the_rubric_it_grades_with` and
  `test_the_validation_record_names_the_committed_labels_it_was_measured_on` pin the kappa, the n,
  the 2x2, the rubric hash and the labels hash, so an edit to the rubric makes the judge
  unvalidated again -- which is the mechanism's whole point -- and an edit to the labels is caught
  rather than absorbed.
  **The CSV is safe to commit and was checked rather than assumed.** Its `answer` column is prose
  the drafter wrote, its `context` column is the artifact briefs the drafter was shown, and the 141
  distinct artifact names in it are all from the synthetic `credit_default` run at seed 20260901
  plus `projection.convexity`, which is the synthetic hazard subject's artifact used as D-141's
  distractor. No data row, no identifier, no credential, nothing proprietary.
- **A, continued -- the two disagreements, and what each one is about.**
  **(i) `conceptual_soundness-03`: human pass, judge fail at 0.60**, on "Criteria 1 and 3: uncited
  word-numbers like ten, seven, two and a half". The human read criterion 1's "every number" as
  meaning digits -- which is the tokenizer's reading, and therefore the reading under which the
  whole verifier operates -- and the judge read spelled-out words as numbers. Neither is careless.
  The sentence at issue is "roughly two and a half times that bound", which is a **derived ratio of
  two artifacts** (0.07598 against 0.03) that exists nowhere in the store, so on the judge's
  reading it is exactly what criterion 1 is for, and on the human's it is not a number at all. The
  rubric is silent on words, and two careful graders split on it.
  **(ii) `summary-03`: human fail, judge pass at 1.00.** The human failed "No findings were raised
  for this section, so no severity is assigned here" as a criterion-5 absence statement. The judge
  passed it -- while having **failed** `summary-07`'s near-identical "no severity counts exist to
  report in this section" at 0.80 for exactly that criterion. So this row is not a boundary the two
  graders drew differently; it is the judge being **inconsistent at its own criterion-5 boundary**,
  and the human's label is the defensible one on at least one of the two rows.
- **A, continued -- the decision.** **0.771 is recorded as it stands and the rubric is NOT revised
  in this commit.** Both boundary questions go to the Phase 12 pre-flight, beside the
  `DRAFT_INSTRUCTION` change D-156 and the distractor observation call for, and a revised rubric is
  validated on a **fresh label set**, not on these 40. The two questions, stated so that the
  pre-flight has them in one place:
  1. **Do spelled-out words count as numbers?** The verifier's answer today is no -- nothing
     tokenises "two and a half" -- which is why the cheapest fix is at the other end, forbidding
     the drafter to write them at all.
  2. **Where is criterion 5's boundary, in D-103's terms?** "No findings were raised" is a
     statement about *the run* and is allowed -- it is the sentence section 6's own brief asks for
     when nothing fired. "No severity counts exist to report" asserts the *absence of a quantity*
     and is not, which is D-100's rule as D-114 reads it.
- **Why:** Revising a rubric after reading the human labels and re-grading the same 40 rows would
  tune the judge to the labels, and the resulting kappa would measure nothing except how well the
  edit was fitted to the sample it was made from. That is the same error as choosing a threshold on
  a test set, it is the error this whole project exists to catch other people making, and a number
  produced that way could not honestly be published beside a claim about grounding precision. So
  the sequence is the one that costs a second label set: publish what the committed rubric scored,
  say which two rows it split on and why, change the rubric once in the pre-flight where it can be
  changed alongside `DRAFT_INSTRUCTION`, and measure the new one on rows nobody has seen.
  The kappa itself is worth reading with its width in mind and the entry says so rather than
  leaving it to be inferred: 0.771 over 40 rows with 5 failures in each margin is a **substantial**
  agreement by the usual convention and a thin one arithmetically -- moving a single cell of that
  2x2 moves the kappa by roughly 0.1 -- so what the measurement supports is "this judge is usable
  and its two error modes are named", not a comparison against any other judge's number.
  Rejected alternatives: revising criterion 5 now because disagreement (ii) is plainly the judge's
  fault, which is the tuning above wearing a better argument -- the judge is inconsistent, but the
  fix is a rubric edit, and a rubric edit re-grades all seven tapes at about $29 (D-153) to produce
  a kappa nobody could trust; dropping the two disagreeing rows and reporting agreement on 38,
  which is publishing a measurement with its failures removed; treating the human's labels as
  ground truth and reporting an error rate instead of a kappa, which throws away the fact that two
  competent graders can disagree about criterion 1 and hides boundary question 1 entirely; and
  waiting for a second labelling before recording anything, which leaves the layer shipping seven
  "no validation record" warnings on every run and the kappa unpublished for a phase.

## D-158. Every tape is pruned to the interactions a replay reads, and the costs stay as spent

- **Date:** 2026-09-15 (Phase 11)
- **Q:** Four record sittings, two of which died part way (D-155), and two rubric revisions
  (D-148, D-153) left each drafting tape carrying interactions no replay can reach. What happens
  to them?
- **A:** They are pruned. The keys a replay actually reads were **measured**, not reasoned about --
  a session-scoped patch over `CassetteStore.replay` logged every key requested during
  `pytest tests/probatio --cassette=replay`, and an interaction whose key is not in that set is
  removed; each tape is then rewritten through `CassetteStore.write`, whose sorted-key output is
  byte-identical to a no-op round trip, so the diff is deletions only. **64 interactions pruned
  across six tapes:**

  | tape | before | pruned | kept | of which dead judge calls | dead drafting calls |
  | --- | ---: | ---: | ---: | ---: | ---: |
  | `draft_section.summary` | 27 | 9 | 18 | 8 | 1 |
  | `draft_section.conceptual_soundness` | 27 | 9 | 18 | 8 | 1 |
  | `draft_section.data_integrity` | 28 | 12 | 16 | 9 | 3 |
  | `draft_section.outcomes` | 29 | 11 | 18 | 8 | 3 |
  | `draft_section.sensitivity` | 25 | 9 | 16 | 8 | 1 |
  | `draft_section.findings` | 16 | 0 | 16 | 0 | 0 |
  | `draft_section.monitoring` | 30 | 14 | 16 | 12 | 2 |
  | `extract_claims.conceptual_soundness` | 1 | 0 | 1 | 0 | 0 |
  | `plan_followup.first_step` | 1 | 0 | 1 | 0 | 0 |
  | `plan_followup.after_refusal` | 1 | 0 | 1 | 0 | 0 |
  | **total** | **185** | **64** | **121** | **53** | **11** |

  The tapes go from **7.5 MB to 4.9 MB**. `draft_section.findings` prunes nothing because D-156's
  re-record was made into a moved-aside file rather than over the old tape, which is D-155's rule
  doing exactly what it is for -- a tape recorded that way never accumulates a dead interaction in
  the first place.
  **What the 64 were.** Fifty-three are judge calls keyed on a superseded rubric: D-148's quoting
  prohibition and D-153's criterion-5 rewrite each changed `Rubric.content_hash`, which enters
  every judge interaction key, so each revision stranded a tape's whole judge half. Eleven are
  `structured()` **re-ask** prompts whose first-call answer was later re-recorded: a re-ask prompt
  quotes the answer it is correcting, so once a re-recording replaced that first answer with one
  that parsed, the old re-ask became unreachable. Those eleven are worth naming because of what
  they contain -- the Claude CLI answering a drafting prompt with an attempted
  `<invoke name="Bash">` tool call listing its own `~/.claude/projects/.../memory/` directory
  instead of the JSON object it was asked for. Three such first-call answers are still *live*
  interactions on `summary`, `conceptual_soundness` and `outcomes`, because the re-ask that
  followed each is a call the replay makes, so those three tapes still carry the operator's home
  path; that is unchanged from the previous commit, carries no credential, and is a fact about the
  provider rather than about this suite.
  **The published layer cost does not move.** `docs/EVALUATION.md` keeps **~$73** for Phase 11:
  the pruned interactions were paid for, in sittings that happened, and the cost figure is a record
  of what the phase spent and not an inventory of what the repository still stores. The replay's
  own per-case cost column, which sums the tapes, is a different number and always was -- it is
  what these calls would cost to make again.
- **Why:** A dead interaction is committed data that nothing checks. It is keyed on a prompt no
  code builds any more, so no test can ever fail because of it, no reader can tell it apart from a
  live one without running the measurement above, and it makes the next stale-tape diagnosis harder
  by putting near-miss prompts in the file a human greps. Two thirds of these tapes were answers to
  a rubric this project has decided twice over was wrong, and keeping them reads as evidence when
  it is residue. Doing it after the re-record rather than before is deliberate: the set of live keys
  is only knowable once the tapes are the ones the suite will ship with, and pruning against a
  measurement taken before D-156's re-record would have deleted the wrong eight.
  Rejected alternatives: re-recording every case from scratch so that no tape has ever held a dead
  interaction, which is about $29 (D-153's measurement) to buy tidiness and would discard four
  sittings' worth of evidence for three published defect classes; leaving them, which is the status
  quo and costs a reader's time on every future stale-tape failure; deleting by hand from the
  visible pattern -- short judge replies, old rubric wording -- which is the guess this measurement
  replaces and would have missed all eleven re-asks; and adding a `probatio prune-cassettes`
  command, which is a patch to a dev dependency for a one-off and belongs upstream with the other
  five issues if it belongs anywhere.

## D-159. The performance file is read under either published name and renamed under neither

- **Date:** 2026-09-15 (Phase 11, before the first real MSR run)
- **Q:** `sample_freddie.py` looks for `sample_svcg_YYYY.txt`. The operator's July 2026 download
  writes `sample_perf_YYYY.txt`. Which name does the script expect, and what happens to the file on
  disk?
- **A:** **Both names are accepted, per vintage, and no file is renamed.** `_performance_path`
  tries `sample_svcg_{year}.txt` first and `sample_perf_{year}.txt` second, returning the first
  that exists; when neither does it returns the first, so the missing-file message names
  `sample_svcg_YYYY.txt`, which is the spelling an operator of the archived vintages should be
  looking for. The order is deliberate rather than alphabetical: the 2014, 2017 and 2019 sample
  files are **archived** distributions, `svcg` is what those archives carry, and a directory
  holding both should be read as the archive it is. The docstring's file table and the subject
  README both show the two names side by side; `--raw`'s help text names both.
- **Why:** The alternative the `HANDOFF` note rules out, and rightly, is renaming the download.
  A downloaded artefact keeps the name its distribution gave it, for three reasons that all bite
  here. The digest an operator records in `package.yaml`'s `data.manifest` is of the files *this
  script writes*, but the provenance trail a reader follows starts at the file they downloaded, and
  a renamed input breaks the one link in that chain nobody can reconstruct. A rename is a
  hand-edit performed once and forgotten, so the next operator on the next machine meets a
  missing-file error whose fix is undocumented. And a script that renames its inputs writes to the
  raw data directory, which is exactly the directory `CLAUDE.md` says never enters this repository
  and which nothing here should be modifying.
  Accepting two names rather than one is the smallest change that makes the script read what the
  operator actually has, and it costs one `next()` over two paths. Rejected alternatives: a
  `--performance-name` flag, which asks the operator to describe a file the script can simply look
  for and adds an argument that will be wrong in someone's shell history; globbing
  `sample_*_{year}.txt` and taking whatever is not `orig`, which would silently read a stray file a
  human left in the directory; and switching the expected name to `perf` outright, which breaks
  every archived distribution and is the mirror of the mistake this entry avoids.

## D-160. The real `msr_prepayment` fit, measured, and what of it becomes the package's word

- **Date:** 2026-09-16 (Phase 9, the first real MSR sample)
- **Q:** `sample_freddie.py` has been run over the Release 47 sample files and
  `python -m code.run --data` has fitted the panel. Which of those numbers go into
  `package.yaml` as the developer's own declarations, which go into the README as measurement,
  and which of the subject's declared thresholds move now that the fit is known?
- **A:** **The measurement.** Run of 2026-09-16 on this machine (Python 3.12.14,
  scikit-learn 1.9.0, numpy 2.5.3, pandas 3.0.5), 20,000 loans at seed 20260901 over the 2014,
  2017 and 2019 sample files, sampler 26.97 s and subject 10.16 s wall-clock. The five digests are
  in `data.manifest`. Loan-months / loans / event rate: train 313,538 / 8,596 / 0.00948; test
  135,060 / 3,685 / 0.00917; out_of_time 283,343 / 7,954 / 0.01868; vintage_holdout
  221,779 / 6,123 / 0.01948. The VIF screen removes two of twelve, `bom_balance_log` at 16.50 and
  then `note_rate` at 18.07. Test AUC **0.6549**, Brier 0.00906, slope 0.966, CPR 0.1047 actual
  against 0.1094 predicted; train 0.6504 and 0.957; out_of_time AUC 0.690, slope **0.432**, CPR
  0.203 against 0.114; vintage_holdout AUC 0.739, slope 0.851, CPR 0.210 against 0.112. The
  projection values 3,946 loans and $560.9M of beginning balance as of 202603 at
  **$9,498,507**, changing **−$1,077,724 (−11.35 %)** at −300 bp and **+$167,117 (+1.76 %)** at
  +300 bp, convexity −910,607, realised negative as declared.
  **Two developer claims, not three, and no CPR claim.** `claims` carries
  `auc test 0.655` and `brier test 0.00906`, rounded to three significant figures from
  `artifacts/real/metrics.json`. There is **no CPR claim** because `verifier/developer.py`
  resolves a claim to `metrics.<split>.<metric>`, `<metric>.<split>`, `<metric>` or
  `<metric>.max`, and no artifact holds an annualised CPR *level* — `cpr.<split>` is a by-period
  table and `cpr.<split>.mae` an error — so the declaration would be checked by nothing. There is
  **no `calibration_slope` claim** for a sharper version of the same reason, found by making the
  claim and running the validate: the claim *does* resolve, to `calibration_slope.test`, and the
  two numbers are **1.017 and 0.966**, so it came back `mismatch` and minted a `T1` at medium on
  the clean control. The subject computes its own slope with
  `sklearn.linear_model.LogisticRegression(max_iter=1000)`, whose default `C = 1.0` penalises the
  coefficient; `quaestor.tools.stats.calibration_slope_intercept` computes the unpenalised maximum
  likelihood estimate by its own Newton iteration and says in its docstring that it does not use
  scikit-learn for exactly this reason. On four synthetic samples of the four splits' sizes and
  event rates the two estimators differ by −0.005 to +0.059, the order of the 0.051 seen here, so
  the gap is the estimator and not the panel. A claim checked against a differently-defined
  artifact is not a claim, so it is dropped and the disagreement is recorded here.
  **There is also no out-of-time or vintage claim**: the developer does not get to claim drift.
  **No threshold moves.** `auc test min 0.65` stays where it was set before the run although the
  fit clears it by **0.005**. No `cpr_mae` threshold is added: CPR is reported and not tested
  until the `scenarios` block carries a claim one could sit under. `--n-loans 20000` stands.
  The sampler's zero-balance docstring and the subject README are softened from "still carry" to
  "may carry", with the measured enumeration beside them.
- **Why:** A floor moved after seeing the number is the `T1` this tool exists to catch, and 0.005
  is exactly the margin at which moving it is tempting. The floor was a declaration made before
  the fit; if a later sampler or library change takes the fit under it, that is a real finding on
  a real model and the control is re-cut then, with the re-cut recorded. `--n-loans 20000` is left
  alone on the same principle and because it is adequate: 8,596 training loans give about 2,970
  events for ten coefficients, and the whole sample costs 27 s. Dropping the slope claim rather
  than declaring 1.017 is the same order-of-decision rule: 1.017 is the *validator's* number, and
  writing the validator's recomputation into the package as the developer's word inverts the two
  roles the study depends on — the subject is the developer's model, and its documentation must
  say what its own code computed. Dropping it rather than changing `run.py` to the unpenalised
  estimator is deliberate too: that would be tuning the subject to the validator, it would move
  every committed number in `artifacts/real/`, and it would need a second real run. **Whether the
  subject should report a penalised calibration slope at all is a real question about the subject
  and is left open here**, named so the next person does not rediscover it.
  Two numbers in this entry are worth flagging as not being artifacts. The two wall-clocks are the
  operator's `time`, as the credit README's are; and the zero-balance enumeration —
  `01` (40,813), `16` (141), `96` (95), `09` (82), `02` (61), `15` (41), `03` (28) on
  `sample_perf_2014.txt` — was measured on the raw download, which this repository does not hold
  and no test may read, so it is quoted as the operator's measurement of 2026-09-16 and is why the
  three retired codes stay in `CENSORING_CODES` on a "may carry" rather than a "does carry".
  Rejected alternatives: declaring the CPR level anyway and adding an artifact to hold it, which
  is a tool change made to fit a claim; adding a `cpr_mae` threshold at whatever the run produced,
  which is the moved floor in a new metric; and recalibrating or refitting the subject so that the
  real control comes out clean, which D-161 rejects at length.
- **Consequence (2026-09-16, the follow-up commit):** the answer above was right that the two
  numbers are two estimators and wrong about where the defect lived, and it is reversed here. The
  disagreement is **our** artefact, not the developer's: D-017 and D-045 make these subjects honest
  developers whose every deliberate structure is documented, and `run.py` reported a headline
  diagnostic 0.05 away from the estimator spec 3.7 names, with nothing in its docstring saying so.
  That is neither honest nor documented, so `_calibration_slope` now fits the unpenalised maximum
  likelihood estimate to convergence and the claim returns. Before against after, on the same fit
  and the same four splits:
  train **0.9570768542841445 → 0.9971012403150885**, test **0.9659710007447115 →
  1.0168355099200166**, out_of_time **0.4321272469586856 → 0.4321257819341887**, vintage_holdout
  **0.8506474891789182 → 0.8501990160137237**. Nothing else in `artifacts/real/` moves: the
  champion fit, the splits, the features, the coefficients and the projection are byte-identical,
  and the four slopes are the only four values `metrics.json` changes. `claims` carries three
  entries again, the third `calibration slope test 1.017` — **four** significant figures, because
  `verifier/match.py::tolerance_for` allows half a unit of the last decimal written and "1.02"
  would be checked to 0.0005 against 1.0168 and fail by 0.003, where "1.017" differs by 0.00016
  and verifies. The open question the entry above named — *whether the subject should report a
  penalised slope at all* — is therefore answered no, and closed.
  **The diagnosis above is wrong about the cause, and the measurement that proves it is worth
  recording.** Removing the penalty is necessary — spec 3.7 means the MLE and `C = 1.0` is not it
  — but on this panel it is not what moved the number. Decomposed on the real splits, penalised /
  unpenalised at lbfgs's default `tol = 1e-4` / unpenalised and converged: test **0.965971 /
  0.966011 / 1.016836**, train 0.957077 / 0.957093 / 0.997101, out_of_time 0.432127 / 0.432172 /
  0.432126, vintage_holdout 0.850647 / 0.850950 / 0.850199. The penalty is worth **4e-5** on the
  test split — at 135,060 rows and two parameters, `C = 1.0` is nearly no prior at all — and the
  whole **0.0508** gap the last commit attributed to it is lbfgs stopping on the gradient before
  the optimum. Both are fixed here, but only the tolerance ever moved the number, and a commit that
  had removed the penalty alone would have re-run the panel, moved nothing, and left the two
  estimators as far apart as before. The reason the disagreement looked like a penalty is that it
  appears only where the slope is near 1: at 0.43 out-of-time the default tolerance is already
  converged to 5e-5.
  Two details of the spelling. It says `C = np.inf`, not `penalty=None`: scikit-learn deprecated
  `penalty` in 1.8 and 1.9 emits a `FutureWarning` naming `C=np.inf` as the replacement, and the
  subject's stderr is stored as the `run.stderr` artifact, so a warning there would be a
  content-addressed change to every run of every subject rather than a cosmetic one. And `tol` is
  set to **1e-10**, which is the tolerance `calibration_slope_intercept`'s own Newton iteration
  uses, so the two routines are converged to the same place by construction rather than by luck.
  Unpenalised *and* converged, the subject and
  `quaestor.tools.stats.calibration_slope_intercept` agree to about 1e-9, and
  `tests/test_subject_msr_prepayment.py::test_the_subjects_slope_is_the_same_estimator_quaestor_recomputes`
  asserts 1e-6 on all four synthetic splits so that they cannot drift apart again.
  **One instance of the same defect is left open, named here so it is not rediscovered.**
  `tools/stability.py::_coefficients` documents itself as fitting "one unpenalised logistic
  regression per regime" and calls `LogisticRegression(max_iter=_MAX_ITERATIONS)`, which is the
  penalised default — the same docstring-against-code mismatch, in our code rather than a
  subject's. It is not fixed in this commit because the per-regime coefficients feed `R1` and
  changing the estimator would move the golden report and every committed run's `stability.*`
  artifacts, which is a change that needs its own commit and its own re-measurement.
- **Correction, 2026-09-16 (the `R1` precision commit):** that last sentence is wrong, and the
  open instance is now closed. The golden report declares no regime column, `credit_default`
  declares `regime.column: null`, and none of the six committed runs under `eval/results/` holds a
  single `stability.*` artifact, so the change moves neither the golden nor any committed run. It
  is made in **D-163**, in this entry's own spelling — `C = np.inf` at `tol = 1e-10` — and the only
  thing it did move is recorded there and in **D-164**.

## D-161. Every control carries a measured baseline finding set per data mode; a baseline finding is not a false alarm

- **Date:** 2026-09-16 (Phase 9, decided by the human and confirmed in Cowork)
- **Q:** The offline `--llm fake` validate of the real `msr_prepayment` panel yields `C1` at
  medium on `out_of_time` and `vintage_holdout`. `docs/STUDY.md` §5 counts every finding at
  severity ≥ medium on a control as a **false alarm**, and D-047 fixes this control's expectation
  at exactly `{}`. Worse for the study: `msr__C1__oversampled_hazard` seeds `C1` on this subject,
  so on real data its own class would be present *before* the seed. What is the rule?
- **A:** **D-017 is generalised.** Each control × data mode has a **baseline finding set**,
  measured with `--llm fake` and recorded in `eval/taxonomy.yaml` before the study runs, and
  **a baseline finding on a control is not a false alarm**. Detection of a baseline class on a
  seeded variant of the same subject and the same data mode requires **evidence outside the
  baseline**: for `msr__C1` on real data, a `C1` whose evidence includes a **test-split** artifact,
  since the clean control's test slope is 0.966 — **1.0168 from the estimator fix of D-160's
  consequence paragraph onward** — and its test mean-ratio gap about 4 %, so the seed has to move
  the test split to count.
  The values, measured: **real `msr_prepayment`** = {`C1` medium, splits `out_of_time` and
  `vintage_holdout`, evidence `calibration_slope.out_of_time`,
  `calibration.mean_rel_gap.out_of_time`, `calibration.mean_rel_gap.vintage_holdout`};
  **synthetic `msr_prepayment`** = {} (D-047); **synthetic `credit_default`** = {`E1` low}
  (D-017); **real `credit_default`** = {} (the committed excerpt run,
  `eval/results/first-live/credit/findings.json`, and its five predecessors). The two **perturbed**
  controls are not yet measured and carry `null` until the Phase 12 pre-flight runs them offline;
  a perturbed control whose baseline differs from its clean control's would itself be a finding
  about the perturbation. `score.py` reading artifact keys from `artifacts/index.json` beside
  `findings.json`, so that "evidence includes a test-split artifact" is checkable rather than a
  sentence, is a **Phase 12 pre-flight item, named here**. The scorer is not written in this
  commit; the taxonomy carries the values and `eval/seed.py` parses them.
  Also recorded: the `msr_prepayment` **live** run will be the first live run with a finding, and
  therefore the first live exercise of the D-156 fix to section 6's prompt.
- **Why:** Two fixes were available and both are refused. (i) **Re-scoping `C1` to the test split**,
  as D-046 did for `psi` and `S1`, would make the control pass — and would be choosing the scoping
  that makes the control pass *after* seeing the control, which is the exact order D-035 and D-046
  refused when the scoping was cheap to get right. `metrics.py`'s module docstring already applies
  `C1` to every split and gives the reason D-046's train-versus-test argument does not transfer:
  PSI on a period split compares populations that are *defined* to differ, while a calibration
  slope on a period split is the model's own claim about that period and is exactly what a
  validator should read. Re-scoping would blind the outcomes analysis on every real hazard model
  this tool is ever pointed at, which is a large price for a tidy control. (ii) **Refitting or
  recalibrating the subject so the validator's control comes out clean** inverts the roles the
  whole study depends on: the subject is the developer's model, the validator is the reader, and a
  subject tuned until the reader has nothing to say measures nothing. The out-of-time
  miscalibration is the phenomenon — a hazard fitted through 2019 under-predicts the 2020–21
  refinancing wave by about half — and not noise.
  What the baseline rule buys is that both readings stay true at once: the control is *not* clean
  on real data, which is published rather than smoothed, and the study still has a false-alarm
  rate that means something, because a false alarm is a finding the control did not already carry.
  The cost is that it is one more measured number per control that must be re-measured whenever a
  subject, a threshold or a tool changes, which is why it lives in the taxonomy beside the recipes
  rather than in prose. Rejected alternatives: counting the baseline `C1` as a false alarm and
  publishing a non-zero false-alarm rate on a control nothing is wrong with, which would make the
  headline number a statement about the panel rather than about the detector; excluding the real
  `msr` control from the study, which discards the only real hazard panel this project has; and
  scoring detection of a seeded `C1` on this subject without the evidence rule, which would credit
  the detector for a finding it would have raised with no seed at all.
- **Consequence (2026-09-17, the Phase 12 pre-flight commit A):** the measured real
  `msr_prepayment` baseline above is **five evidence keys, not three**. D-171 gives each `C1`
  candidate the decile table of the split it fired on, so the finding gains
  `calibration.out_of_time` and `calibration.vintage_holdout` and the recorded set becomes
  {`calibration_slope.out_of_time`, `calibration.mean_rel_gap.out_of_time`,
  `calibration.mean_rel_gap.vintage_holdout`, `calibration.out_of_time`,
  `calibration.vintage_holdout`}, re-measured offline against the five verified `package.yaml`
  digests. `eval/taxonomy.yaml` and
  `tests/test_seed.py::test_every_control_carries_the_baseline_d161_measured` carry the five.
  Nothing else in this entry changes: the class, the severity, the two splits and the run itself
  are as measured on 2026-09-16, and the **evidence rule is unaffected** — a seeded `C1` on this
  subject and data mode still has to reach a **test-split** artifact to count as detected, and
  neither new key is one. It is the first illustration of this entry's own warning that a baseline
  is a measured number which must be re-measured whenever a subject, a threshold or a **tool**
  changes.

## D-162. The verified data manifest becomes an artifact, so a `--data` report can cite the check

- **Date:** 2026-09-16 (Phase 9, the MSR follow-up commit; approved in Cowork)
- **Q:** Under `--data` the loader verifies every digest in `data.manifest` before anything runs —
  a mismatch is a `PackageError` and there is no report at all — but no report says so. Appendix D
  carries a negative row when the manifest was *not* verified and nothing carries a positive row
  when it was, so a reader of a real-data report cannot tell the check from its absence. Where
  does the positive go, and what stops it leaking into synthetic reports and the golden?
- **A:** `pipeline.validate` writes one table artifact, `data.manifest`, immediately after the
  store is opened and only when `package.data_dir` is not `None` — that is, only when the loader
  actually verified something. Its rows are `{file, sha256, verified: true}`, one per declared
  file, sorted by name. Section 3's brief gains `tables=("data.manifest",)`, which is what makes
  the check citable in prose rather than merely recorded, and `renderer._appendix_c` gains one row,
  `("data manifest", "verified: N file(s) against package.yaml (see data.manifest)")`, guarded on
  the artifact being in the store. Appendix D's two existing negative rows are untouched: a
  package that declares no manifest, and a run that read no data directory, still say so there.
  Nothing is conditional on the data mode itself — the guard is the artifact's presence — so a
  `--synthetic` run writes no artifact, offers section 3 nothing, renders no Appendix C row, and
  the golden report is byte-identical, which the gate checks.
- **Why:** The digests are already committed in `package.yaml`, so the artifact publishes nothing
  the repository does not already hold; what it adds is a content-addressed hash of the verified
  set that a claim can cite, which is the whole grounding contract applied to the one check that
  had been exempt from it. Rejected alternatives: a sentence in the renderer's section 3 template,
  which would be prose no claim can be checked against and would have to be written twice, once
  for the drafter and once for the template; putting the row in Appendix D as a "verified" row,
  which turns the appendix of what did *not* run into a mixed ledger and makes its one job
  ambiguous; and keying the row on `data_mode == "real"` rather than on the artifact, which would
  print "verified" for a package that declares no manifest at all.

## D-163. The per-regime fit converges, and the deferral reason that held it back was wrong

- **Date:** 2026-09-16 (Phase 9, the `R1` precision commit)
- **Q:** D-160's last paragraph left one instance of its own defect open: `tools/stability.py`
  documents itself as fitting "one unpenalised logistic regression per regime" and calls
  `LogisticRegression(max_iter=_MAX_ITERATIONS)`, which is scikit-learn's penalised default at
  lbfgs's default stopping tolerance of 1e-4. It was deferred because changing it "would move the
  golden report and every committed run's `stability.*` artifacts". Is that true, and what does
  the converged estimator actually move?
- **A:** **The deferral reason is dead on both counts, and the fix lands.**
  `_regime_coefficients` now fits `LogisticRegression(C=np.inf, max_iter=_MAX_ITERATIONS,
  tol=_TOLERANCE)` with `_TOLERANCE = 1e-10`, which is where
  `stats.calibration_slope_intercept`'s own Newton iteration stops, so the two routines are
  converged to the same place by construction rather than by luck — D-160's spelling, for
  D-160's reasons, including `C=np.inf` over `penalty=None` because 1.9 emits a `FutureWarning`
  for the latter and a subject's stderr is a stored artifact.
  **Neither half of the deferral reason survives checking.** The golden report declares no regime
  (`examples/golden_report/report.md:120` and `:339`: "Regime stability was not assessed because
  the package declares no regime column", and Appendix D's `check_stability (R1) | package
  declares no regime.column`); `subjects/credit_default/package.yaml` declares `regime: column:
  null`, so `check_stability` never runs on it; and **no committed run holds a `stability.*`
  artifact** — 0 of the 192, 124, 124, 121, 258 and 250 names in the six `eval/results/**/index.json`
  begin `stability.`. `git status --short examples/` is empty after the change.
  **Convergence, measured.** All four regime fits of the two MSR runs converge well inside the cap
  and **no `ConvergenceWarning` is emitted** under `PYTHONWARNINGS=always`: synthetic falling
  16 → 27 iterations, synthetic rising 11 → 25, real falling 14 → 28, real rising 18 → 31, against
  a cap of 1000 that was never approached and is not raised.
  **What moves.** On the **real** panel the largest absolute move is `burnout` falling, 0.0342
  (−0.104120123 → −0.138303264), and the largest relative one is `rate_change_12m` falling, 125.0%
  (−0.010870683 → +0.002716470) — a sign change that gives that feature opposite signs across the
  regimes without raising `R1`, because +0.0027 does not clear the 0.05 materiality gate. On the
  **synthetic** panel the largest absolute move is `note_rate` rising, 0.3136 (−0.226697682 →
  −0.540305863), and the largest relative one is `burnout` rising, 12,316% (−0.000759889 →
  −0.094344680); no synthetic cell changes sign. **`stability.auc_by_regime` and
  `stability.psi_over_time` are byte-identical before and after on both runs and on all three
  variants re-measured here** — nothing is refitted for the AUC arm, which reads the champion's
  own scores. The real MSR finding set is unchanged: exactly one `C1` at medium on the same nine
  evidence hashes. Credit is untouched, because it declares no regime and stores no `stability.*`.
  **The converged fit is the maximum likelihood estimate, checked against a fit sharing no code
  with it.** `test_the_per_regime_fit_agrees_with_an_independent_converged_newton_fit`, in
  `tests/test_tool_rules.py`, fits the same per-regime designs by the IRLS step written out in
  `stats.calibration_slope_intercept` and asserts agreement to **1e-5 absolute**. The tolerance is
  absolute and not relative on purpose: measured, the two agree to 1.31e-7 / 6.52e-6 (synthetic
  falling), 2.81e-6 / **9.06e-4** (synthetic rising), 6.22e-7 / 1.49e-5 (real falling) and
  4.22e-7 / 1.12e-5 (real rising) absolute / relative, so a relative bound of 1e-6 would fail on
  the fifty-event rising regime. scikit-learn's `tol` is a gradient tolerance where the Newton
  routine's is a coefficient-step tolerance, and on a near-flat likelihood the two stop at
  different points of a very shallow optimum. For scale, the **old** estimator differs from the
  same Newton fit by up to 0.314 absolute and 40x relative, which is the case for the change.
- **Why:** A diagnostic whose whole content is a comparison of coefficients across regimes must
  not be reading a penalty nobody declared or a descent nobody finished; and a docstring that says
  "unpenalised" over code that is penalised is the exact defect D-160 found in a subject and fixed
  there, so leaving our own instance open was the harder position to defend. The deferral reason
  was checked rather than trusted because it was the only thing standing in the way, and it was
  wrong — which is worth recording on its own, since a reason that is never re-checked outlives
  the fact it was about. Rejected alternatives: raising `_MAX_ITERATIONS` instead, which addresses
  a cap that was never reached; and fixing only the penalty, which D-160's own decomposition shows
  is the smaller of the two effects and would have moved almost nothing.
- **Consequence:** the converged estimator raised a new `R1` on the clean synthetic hazard control
  and the whole of the reason is in **D-164**, which lands in the same commit. The control's
  baseline in `eval/taxonomy.yaml` does **not** move, and that is the point.

## D-164. `R1`'s sign flip must clear a precision gate as well as a materiality one

- **Date:** 2026-09-16 (Phase 9, the `R1` precision commit; **decided 2026-09-09**, see below)
- **Q:** With the converged estimator of D-163, the clean synthetic hazard control's `burnout`
  coefficient in the rising regime moves from −0.000759889 to −0.094344680, clears
  `threshold.R1.sign_flip_coef` of 0.05, disagrees in sign with the falling regime's +0.223546677,
  and raises `R1` at medium on a control D-047 fixes at exactly `{}`. Its standard error is
  **0.290452**, nearly six times the gate it cleared, on **fifty events for ten features**; its
  **z is −0.32** and its 95 % interval, [−0.6636, +0.4749], covers zero and both signs. Is a point
  estimate that cannot be told from zero a regime instability?
- **A:** **No, and the rule now says so.** A feature flips when it is in the top `TOP_FEATURES`
  by mean |coef|, its coefficients have opposite signs, `|coef| > threshold.R1.sign_flip_coef`
  (unchanged, 0.05) in **every** regime, **and** `|coef / s.e.| >= threshold.R1.sign_flip_z` (new,
  default **2.0**) in every regime. Each regime fit's standard errors come from its own observed
  information, `(X'WX)^-1` with `W = mu(1 - mu)` on the standardised design plus the intercept
  column the fit used — the algebra `stats.calibration_slope_intercept` already writes out,
  factored into `stats.logistic_standard_errors` and tested against the 2x2 closed form
  `sqrt(1/a + 1/b + 1/c + 1/d)`. `stability.<f>.coef_or_importance_by_regime` gains `se` and `z`
  columns, the `sign_flip` scalar's description names both gates, the candidate's `detail` names
  both, and **`threshold.R1.sign_flip_z` is stored beside `threshold.R1.sign_flip_coef` whether or
  not the rule fires**, so a report that says the signs held can cite both halves of what "held"
  meant. The AUC-gap arm of `R1` is untouched.
  **The order this landed in is not the order it reads as, and the record matters.** The
  tightening was **decided on 2026-09-09**, in the Phase 12 pre-flight list of the `docs/STUDY.md`
  draft, §4 item (ii) — *"R1 requires the flipping coefficient to be distinguishable from zero in
  both regimes"* — for the collateral `R1`s that `msr__L2__contamination` and
  `msr__S1__vintage_shift` raise on `burnout` and `sato`, which D-047 had already placed at
  seed-to-seed noise and D-136 recorded as collateral. Today's measurement on the control is one
  more instance of the same failure mode, found before the rule shipped. **What changed on
  2026-09-16 is only *when* the rule lands** — before the MSR live run instead of in the
  pre-flight — so that §5 of the MSR excerpt is computed by the rule the study will use. A reader
  who sees a rule change land the day a control failed will assume the reverse order, so it is
  written down here: the rule was not invented to make a control pass.
  **Measured, offline, on this machine (Python 3.12.14, scikit-learn 1.9.0, numpy 2.5.3,
  pandas 3.0.5), every run `--llm fake`:**
  - **clean synthetic MSR** (`--synthetic 2000`): findings **`{}`**, as D-047 and D-161 require —
    measured, not assumed. `burnout` falling +0.223546677 (s.e. 0.113799, z **+1.96**), rising
    −0.094344680 (s.e. 0.290452, z **−0.32**); neither regime reaches |z| 2, and the rising one is
    the coefficient the estimator fix moved across the materiality gate. 45 claims, 272 artifacts,
    grounding precision 1.0000.
  - **real MSR** (`--data`): findings exactly the one **`C1` at medium** on the same nine evidence
    hashes as before. Its largest per-regime |z| among features whose signs disagree is
    `rate_change_12m`, +0.09 falling and −2.36 rising, which the materiality gate stops first.
    51 claims, 273 artifacts.
  - **synthetic credit**: `{E1 low}`, **zero** `stability.*` artifacts, 168 artifacts — the package
    declares `regime.column: null`, so this rule cannot reach it.
  - **the seeded variant still fires.** `credit__R1__regime_flip`:
    `stability.bill_trend_6m.sign_flip` is **1** and `R1` is raised at medium, with
    `bill_trend_6m` at +0.908915937 (s.e. 0.117038, z **+7.77**) in the 2013 cohort and
    −1.170632298 (s.e. 0.105151, z **−11.13**) in the 2016 one. D-130's planted effect clears the
    new gate by a factor of four, so no recipe parameter moves.
  - **the two collateral `R1`s the rule was written for are gone.**
    `msr__L2__contamination` raised `{L2 medium, R1 medium}` and now raises **`{L2 medium}`**:
    `burnout` +0.222939081 (z **+1.97**) falling against −0.048147452 (z **−0.17**) rising.
    `msr__S1__vintage_shift` raised `{T1 high, S1 medium, C1 medium, R1 medium}` and now raises
    **`{T1 high, S1 medium, C1 medium}`**: `sato` −0.062575844 (z **−0.70**) falling against
    +0.210835407 (z **+1.11**) rising. Both cleared the 0.05 materiality gate in both regimes and
    neither comes near |z| 2, which is exactly the case the rule was decided for.
  - **D-130's own collateral flips go with them.** On `credit__R1__regime_flip`,
    `delinq_max_6m` (z +0.69 / −0.68) and `pay_ratio_last` (z −1.84 / +1.07) had
    `sign_flip` 1 and now have 0; the entry records them as "near-zero coefficients that the
    cohort split resolves differently", which is the same thing this gate measures.
  **A feature that does not vary inside a regime has no standard error and no `z`**, and its cells
  are left empty rather than filled with a large finite stand-in on the pattern of `VIF_CAP`: a
  package whose regime column is one of its own features identifies no coefficient for it, and
  printing a precision for a parameter that was never estimated is worse than printing nothing. It
  cannot clear the precision gate, which is the right answer anyway. A regime whose *varying*
  features leave the information matrix singular is refused with a message naming the regime — the
  one case this must not paper over.
- **Why:** Materiality and precision are different questions and both are worth asking, so both
  gates stay. A coefficient of 0.001 estimated to four decimals is not a regime effect; neither is
  a coefficient of 0.09 with a standard error of 0.29. `threshold.R1.sign_flip_coef` is an
  absolute bound on a quantity whose precision varies by two orders of magnitude between the
  regimes of the same panel — 0.066 against 0.290 on the synthetic hazard control — so on its own
  it decides a finding by where a point estimate happens to land, which is what D-047 warned about
  when it recorded that one weak coefficient flips at each of four other seeds tried. **`z = 2.0`
  is the conventional two-standard-error reading and is deliberately not tuned**: it was not
  chosen by trying values against the control, and the seeded variant clears it by a factor of
  four while the three collateral cases miss it by factors of two to twelve, so nothing here sits
  near the bound.
  Rejected alternatives. **(i) Re-baselining the control to `{R1 medium}`** in
  `eval/taxonomy.yaml` under D-161: honest bookkeeping, but it publishes as the hazard control's
  baseline a finding whose entire evidence is a coefficient with z = −0.32, and the published
  false-alarm rate then rests on a control that is not clean for a reason nobody can defend.
  **(ii) Replacing the absolute gate with the z gate alone**: a precisely estimated 0.001 is not a
  regime effect either, and dropping materiality would make `R1` fire on large samples for
  arbitrarily small disagreements. **(iii) Leaving the rule and reverting D-163**: that keeps a
  control clean by means of an under-converged fit pinning a coefficient near zero, which is
  suppressing a finding by accident rather than by argument.
- **Consequence:** **no baseline in `eval/taxonomy.yaml` moves, and that is the point** — D-161's
  four measured baselines are re-measured and unchanged: real `msr_prepayment` `{C1 medium}`,
  synthetic `msr_prepayment` `{}`, synthetic `credit_default` `{E1 low}`, real `credit_default`
  `{}` (not re-run here; no `stability.*` artifact exists in it). `eval/taxonomy.yaml` is not
  edited. The Phase 12 pre-flight list in the `docs/STUDY.md` draft loses its §4 item (ii), which
  is Cowork's to move.

## D-165. Section 1 is handed the findings document, and stops being asked for a count

- **Date:** 2026-09-17 (Phase 9 follow-up 7)
- **Q:** Section 1 of the first live `msr_prepayment` run
  (`eval/results/first-live/msr-attempt1/report.md`) closes: **"No findings were raised at any
  severity."** Directly above it, inside a renderer block the same report writes, the scope table
  reads **0 / 1 / 0 / 0**, and three pages later section 6 writes `F-001` out in full under the
  heading the prompt gave it. One report, two answers to one question. Which half is wrong, and
  where?
- **A:** Section 1's, and in the prompt it was given. `_draft_inputs` handed
  `findings=list(findings) if brief.section is ReportSection.findings else []` — every section but
  6 got an empty list — and `SECTION_FOR_CLASS` maps `C1` to `outcomes`, so
  `candidates_by_section` held nothing for section 1 either. Its candidates block was therefore
  `NO_CANDIDATES`, word for word *"candidates raised for this section: none — describe nothing as
  a finding"*, sitting above a brief whose last clause asked it to state "how many findings were
  raised at which severity". The drafter was told there were none and asked how many there were.
  It answered the half it could see, which is the only coherent thing it could have done.

  **This is D-156's mechanism, and D-156 fixed only its first half.** That decision found the same
  contradiction in section 6 — a prompt built from `candidates` alone saying "none" above the
  findings it ordered the drafter to describe — and fixed it by deriving section 6's block from
  the findings document, so that "both halves come from one object". Section 1 asks about the same
  object, was never given it, and was left outside the fix.

  Two changes, and nothing else. `pipeline._SECTIONS_GIVEN_FINDINGS` is now `(summary, findings)`,
  so section 1 is handed the same document section 6 is and its `_candidates_block` renders the
  findings list rather than `NO_CANDIDATES`. And `_SUMMARY_BRIEF` stops asking for a count: **the
  count by severity is already in the scope table the renderer writes immediately above the
  prose**, from `findings.json`, so the drafter is asked to **name each finding** — "F-001, a C1
  calibration finding at medium severity" — and to write **no count as a digit**. A count the
  drafter wrote itself would be a number with no artifact behind it: an unsupported claim by
  construction, which the verifier would flag, the repair loop would remove, and the reader would
  then find only in a table. The brief also carries D-091's sentence in D-091's words: never write
  that none was raised when the list is not empty.

  Section 1 is given the findings' **ids, classes and severities and nothing else** —
  `_findings_block` takes the section now and writes a different instruction for each. Section 6
  gets the narrative and the evidence keys because it writes them out; section 1 gets neither,
  because they are numbers cited to artifacts its own selector does not carry, and a section
  handed a number it may not cite is a section being set up to write an unsupported claim. It is
  told what section 6's heading will be, so that it can name the finding as the reader will meet
  it, and told not to write a heading itself.
- **Why:** The opening sentence of a validation report is the sentence most likely to be read
  alone, and this one was false on a run that found a real defect. Nothing downstream would have
  caught it: `findings.json` is correct, the scope table is correct, grounding precision is
  **1.0000** post-repair because "no findings were raised" contains no number to verify, and
  `eval/score.py` reads `findings.json` and never the prose. A false sentence carrying no number
  is invisible to every check this pipeline has, which is why it had to be fixed in the prompt
  rather than in a verifier.

  **Why it never showed on `credit_default`, which is the part worth recording.** All six live
  runs of that subject raised **zero findings**, so section 1's "none" was true every time and its
  brief's count question was answerable every time. That is the same blind spot that hid D-156's
  first half — a contradiction between two lists can only appear when one of them is non-empty —
  and it is the second time in this project that a defect survived six runs by being invisible on
  a clean one. It would have reached **section 1 of every seeded variant in the Phase 12 study**,
  all of which are built to carry a finding. Study *scoring* is unaffected, because it reads
  `findings.json`; every report's opening sentence would have been wrong.

  Rejected alternative: letting the renderer append the count sentence to section 1, which would
  make the sentence true and make the drafter's own closing paragraph contradict a line printed
  underneath it — the defect moved rather than fixed. The renderer already states the count in the
  only form that cannot drift, which is the table.
- **Measured:** `tests/test_drafter.py` gains six cases — the summary prompt with one finding
  names it and carries neither `NO_CANDIDATES` nor "describe nothing as a finding"; it carries the
  no-count-as-a-digit instruction and the scope-table reason; it is told section 6's heading and
  told not to write one, and is given neither the narrative nor "Findings to write about, in this
  order"; with no finding it still says none; section 6's own instruction is unchanged; and
  `_draft_inputs` gives the findings to exactly `{summary, findings}` and no third section. The
  six existing D-156 cases pass unchanged. Offline afterwards: `credit_default --synthetic` 1.0000
  → 1.0000 over 49 claims, 168 artifacts, `{E1 low}`; `msr_prepayment --synthetic` 1.0000 → 1.0000
  over 45 claims, 272 artifacts, `{}`; `msr_prepayment --data … --llm fake` 1.0000 → 1.0000 over
  51 claims, 273 artifacts, the same one `C1` at medium on the same nine evidence hashes, and its
  section-1 prompt now carries `F-001`. The golden report is byte-identical: its section 1 says no
  finding was raised **and it has none**, so this change cannot move it, and the fact that it does
  not is the assertion that the change stayed in the prompt.

  **One tape was stranded, and re-recording it was the human's call (D-149).**
  `tests/probatio/cases/draft_section.yaml` pins each case's brief and findings, so `python
  tests/probatio/casebuilder.py` rewrites the `draft_section.summary` case — brief, `findings`,
  `prompt_bytes` 20,307 → 21,758, `prompt_sha256` `820145888ff24b37` → `1c56fd2d5e0d30c8` — and
  its cassette key moved with it. **Exactly one case** moved: the lead-in line of
  `_candidates_block` is section-aware for this reason, so section 6's prompt is unchanged to the
  byte and its tape, and every other tape, replayed throughout. The work stopped there and the
  operator recorded the case on 2026-09-17, a sixth record sitting and the first since Phase 11.
  The tape it wrote carries **20** interactions — 8 drafting calls, 4 `structured()` re-asks and 8
  judge calls — at **$3.6610**, against the superseded tape's 18 at $3.2771; the case's replayed
  cost goes $0.185098 → $0.357327 and its latency 28,368 ms → 53,305 ms, both of them the longer
  prompt. Every assertion still passes 4/4 and no baseline score moves; the ten baseline files are
  re-stamped and nothing in them but `recorded` changes.

  The recording was made **over** the old tape rather than into a moved-aside file, so it arrived
  carrying all 38 interactions, and D-158's prune is what this commit applies: the live key set was
  measured with a session-scoped patch over `CassetteStore.replay` rather than read off the visible
  pattern — 127 replay requests over the ten cases, 123 distinct keys — and the 18 interactions
  whose keys are not in it were removed and the tape rewritten through `CassetteStore.write`. The
  18 are exactly the 18 the superseded tape held, which is the check that the measurement found the
  right set. The other nine tapes prune **nothing**, and a no-op round trip through the same writer
  leaves all nine byte-identical. Committed tapes go **121 → 123 interactions** and
  **$28.9458 → $29.3297**; 4.9 MB either way.

## D-166. A bin label is not a claim: the `label_number` exclusion class

- **Date:** 2026-09-17 (Phase 9 follow-up 7)
- **Q:** Section 4 of the first live `msr_prepayment` run
  (`eval/results/first-live/msr-attempt1/`) wrote "The decile separation on test, with decile 1
  holding the highest probabilities, is shown below." The `1` was tokenised as a claim of value
  1.0, entered grounding precision's denominator, came back `unsupported` — claim
  `8dc85fe2b8ce10b4`, one of the run's two pre-repair failures — and was removed by a repair round
  whose replacement reads "the first decile". Is that number a claim?
- **A:** No. It is the **name of a bucket**, not a measurement of one. No artifact in the store
  holds it, and none could: `deciles.test` is a table whose `decile` column is a label, and a
  citation to it would resolve to a cell that the claim does not assert anything about. So
  `verifier/tokens.py` gains a seventh regex exclusion class, `label_number`, on the pattern
  `section_number` set: `decile`, `bin`, `quantile`, `quintile`, `step`, `round` or `regime`,
  case-insensitive, immediately followed by a whole-word integer of one to three digits. It is
  added to `_PATTERN_ORDER` directly after `section_number`, so `claims.json`'s `exclusions` lists
  it beside the others and Appendix A prints it with its examples, and it is masked in `_masked`
  after the two section-number passes.

  **The bound is the whole of the design**, because an exclusion class is the one kind of rule that
  fails invisibly: it lowers the denominator, which flatters the headline. Three refusals are
  asserted rather than argued. The label word must be immediately before the integer, so "top 2
  deciles capture 0.38" keeps both its 2 and its 0.38 and "decile event rate 0.021" keeps its
  0.021. The integer is one to three digits and a whole word, so `decile 1000` is not a bin of any
  partition this pipeline computes and stays a claim. And the word is the singular, so `deciles 3`
  — a pooled range, where the number is a count of buckets — stays a claim too.
- **Why:** The repair the pipeline made was worse than the sentence it repaired, which is the
  signal that the rule and not the drafter was wrong. "The first decile" is a **word-number**, the
  class `DRAFT_INSTRUCTION` already has a rule against and that the Phase 11 relations found
  walking past the verifier three times in 49 variant runs; our own `REPAIR_INSTRUCTION` produced
  one here by asking the drafter to remove a number it could not cite. A pipeline that converts
  true, citation-free prose into vaguer true, citation-free prose has spent a round and bought
  nothing. The repair instruction is **not** touched: it is right in general, and the defect is
  that this token reached it.

  Why a class of its own rather than a widening of `_SECTION_NUMBER_RE`, which already excludes
  report numbering: it is D-116's argument on the next document. A section number numbers *this
  report*, which the reader is holding; a bin label numbers a *partition the report computed*,
  which Appendix A's own table resolves. Collapsing them would make the exclusion list say less
  about what was excluded and why.

  Why the six `credit_default` runs never met it, which is the part worth recording. They wrote
  `decile 1` exactly once each, in the renderer's own caption "decile separation on test; decile 1
  holds the highest probabilities" — inside a renderer block, and therefore already excluded as
  `renderer_block` before any of this could apply. The tokenizer had been meeting the phrase for
  six runs and never tokenising it, because the phrase was never in drafted prose. The hazard
  subject's section 4 is the first to put it there.
- **Measured:** `tests/test_verifier_extract.py` gains four cases — the live sentence, with the
  `0.748` still a claim and `decile 1` recorded under `label_number`; one case per label word, so
  the list cannot shrink without a failure; "top 2 deciles capture 0.38 … decile event rate
  0.021", which keeps all three numbers and records no exclusion; and `decile 1000` /
  `deciles 3 and 4`, which keeps all three. Offline afterwards: `credit_default --synthetic`
  1.0000 → 1.0000 over 49 claims, 168 artifacts, `{E1 low}`; `msr_prepayment --synthetic`
  1.0000 → 1.0000 over 45 claims, 272 artifacts, `{}`; `msr_prepayment --data … --llm fake`
  1.0000 → 1.0000 over 51 claims, 273 artifacts, the same one `C1` at medium on the same nine
  evidence hashes. The golden report is byte-identical, and carries no token this class would
  have taken.

## D-167. A direction verb carries the sign, and the direction is derived rather than stored

- **Date:** 2026-09-17 (Phase 9 follow-up 7)
- **Q:** Section 5 of the same run wrote "At the downward extreme the servicing value **falls by**
  1078000 [[art:9bab8e73:scenario.value_change.-300]]". The artifact holds **-1077724.40**. The
  matcher compared a written `+1078000` with a stored negative and recorded a `mismatch` — claim
  `e08daa963ce63f32`, the run's other pre-repair failure — although the magnitude was 275.6 inside
  a tolerance of 500. The repair round rewrote it to "changes by -1078000", which verifies. Where
  does the sign of a change belong?
- **A:** In the verb, when the prose puts it there, and the matcher now reads it. `DIRECTION_VERBS`
  is one `Final` mapping in `verifier/match.py`: `falls`, `drops`, `declines`, `decreases`,
  `shrinks` and `loses` to −1, and symmetrically `rises`, `gains`, `increases` and `grows` to +1.
  `direction_of(text, value)` finds a verb governing `by` before **this claim's own token** and
  returns its sign, or `None`. Where it returns a sign, the claim is matched on **magnitude** and
  the verb's direction must equal the artifact's sign; where it returns `None` — "changes by
  -1078000", "falls to 0.43" — today's signed comparison is untouched. All four quadrants are
  tested: a `falls by` against a negative artifact verifies, a `falls by` against a positive one is
  **still a mismatch** with a message that says the magnitude agrees and the direction does not, a
  `rises by` against a positive verifies, and a `rises by` against a negative is a mismatch. The
  tolerance is not relaxed: a magnitude outside it fails on the magnitude, with the artifact's
  magnitude in the message.

  Two bounds in the pattern. Only a **positive** claimed value can take a direction, because a
  signed number states its own; and at most two lowercase words may sit between `by` and the
  number, because the very sentence this was written for carries one — "while at the upward
  extreme it **rises by only** 167100" — and an unbounded gap would let a verb reach across a
  clause and attach itself to the next number.

  **The matcher and not the extractor.** The extractor already returns `comparison`, so it was the
  other candidate, and it is the wrong one: this module's own first paragraph is "the extractor may
  be wrong about anything; the matcher is not allowed to be wrong about anything". A verb before a
  number is a deterministic fact about a string, and a deterministic fact belongs on the
  deterministic side, where it costs no tokens and cannot vary between two runs of one report. One
  place, not both: the extractor is unchanged.
- **Why:** The failure was ours and the repair made the report worse, the same shape as D-166. "The
  servicing value changes by -1078000" is prose no validator would write and no reader wants, and
  the pipeline produced it by refusing to read a word it had already been shown. A validation
  report that may not say a value **fell** is less well grounded, not more: the direction is the
  substantive half of a rate-shock sentence, and dropping it to satisfy a matcher is the report
  improving its own headline by writing worse prose — the thing the unverified-wrapper exists to
  prevent. And the sign is **checked**, not discarded: "falls by" against a positive artifact is
  exactly the error a signed comparison was there to catch, and it is still caught.

  Why `credit_default` could not have found it, in six live runs: a classifier's artifacts are
  probabilities, rates, counts and AUCs, and none of them is signed. The rule needs a scenario
  table with two ends to bite on, and only the hazard subject has one.

  **The rejected alternative, which the prompt for this work asked for: a `direction` field on the
  claim record, shown in a column of Appendix A.** It is refused, and the refusal is not a
  judgement about taste. `examples/golden_report/CLAIMS_SCHEMA.json` was written in Phase 1, before
  any of this code, and closes both `claim_core` and `verified_claim` with
  `unevaluatedProperties: false`; a new field would make every `claims.json` this pipeline writes
  fail its own schema until the schema moved, and `CLAUDE.md` makes a change to the report schema
  after Phase 1 a **stop-and-ask**. A new column in Appendix A would move the golden report's
  claims table, which gate condition 5 fixes byte-for-byte. Neither price buys anything: `text` is
  already on the claim, it already carries the verb, and `direction_of` is already the one reading
  of it. So Appendix A prints the direction **in the `cmp` cell it already has** — `eq (down)` —
  derived by the same function the matcher calls, and the two cannot disagree because there is one
  of them. If a later phase wants the field, the schema change is the human's to authorise and this
  paragraph is what it should be weighed against.
- **Measured:** `tests/test_verifier_match.py` gains seven cases: the four quadrants over a store
  holding the live run's two scenario ends and their mirror images, the signed-number path in both
  its verifying and its mismatching form, a magnitude outside tolerance, and `direction_of` read
  directly on six sentences. `tests/test_renderer.py` asserts Appendix A prints `eq (down)` for the
  live sentence and a bare `eq` for the repair round's rewrite of it. The suite goes 1573 → 1585;
  the golden report, both synthetic validates and the real-panel fake validate are unchanged, and
  `pytest tests/probatio --cassette=replay` still passes 40 with zero provider calls, because
  nothing here is in a prompt.

## D-168. The MSR excerpt run, and its four edits

- **Date:** 2026-09-17 (Phase 9 follow-up 8, decided in Cowork)
- **Q:** `eval/results/first-live/msr/` is the second live `msr_prepayment` run and the one the
  README will excerpt in Phase 16 beside the credit run. It is the excerpt candidate because
  sections 2 and 4 verified whole before any repair — 48 of 48 and 109 of 109 — section 1 names
  `F-001` under D-165 rather than announcing no findings, and section 6 draws the finding under
  D-156; its single pre-repair failure is in section 3 and outside the excerpt. Reading sections 2
  and 4 against the excerpt bar found four sentences whose wording a reader outside this project
  would misread. None of them is a wrong number. May `report.md` be edited?
- **A:** No, on D-120's terms and for D-120's reason, which this entry does not restate and does
  not weaken. The committed `report.md` is what the pipeline produced on `a87aa4a` and it is never
  edited; the run is committed byte-for-byte on D-087's terms, with the row-level CSVs outside the
  repository and `find … -name '*.csv' -size +20k` printing nothing. The **excerpt** is where the
  four edits are applied. Phase 16 takes **§2 and §4 whole** — `### Follow-up analyses` and all of
  the loop's four paragraphs included — applies the four edits below and nothing else, and prints
  them as a before/after diff in `docs/PROVENANCE.md` beside the line saying the excerpt is edited
  and the record is not. **No edit changes a number**, which
  `tests/test_live_msr.py::test_no_excerpt_edit_changes_a_number` asserts by tokenizing both sides
  of each pair with `eligible_numbers` and comparing the values.

  The four, verbatim, so Phase 16 copies rather than reconstructs them. Each `before` is copied
  byte-for-byte out of `report.md`, citations included — which is the thing D-120 learned the hard
  way, its prompt having quoted two `before` strings with the citation stripped out of the middle —
  and each is asserted to be in the committed file **exactly once**, so this entry cannot drift
  from the file it quotes:

  1. §4 `### Calibration`, line 177:
     - `Both breaches are raised as C1 calibration findings.`
       → `Both breaches are raised together as one C1 calibration finding.`

     Ten candidates merged into one finding. The plural reads as two findings where the scope table
     in §1, `findings.json` and §6 all say one, and a reader of the excerpt alone has no way to
     resolve it. The same sentence in a different wording was read and left in place on attempt 1,
     recorded there as "wording, not a number, and it stays"; the difference is that this run is
     the one that gets excerpted.
  2. §4 `### Calibration`, line 168:
     - `the latter well below the lower bound of 0.8 [[art:749634ae:threshold.C1.calibration_slope.min]]`
       → `the latter well below rule C1's floor of 0.8 [[art:749634ae:threshold.C1.calibration_slope.min]]`

     The **previous** sentence's 0.8 is `threshold.package.calibration_slope.test.min`, which the
     package declares; this one is `threshold.C1.calibration_slope.min`, which Quaestor's rule sets.
     Same value, different artifact, and the two sit two lines apart, so "the lower bound" with no
     owner reads as the developer's band carried forward. D-120 edit 3's class exactly.
  3. §4 `### Discrimination`, line 308:
     - `comfortably inside the declared gap allowance of 0.08 [[art:630f28f4:threshold.O1.auc_gap]]`
       → `comfortably inside the gap allowance of 0.08 [[art:630f28f4:threshold.O1.auc_gap]] rule O1 sets`

     `package.yaml` declares no AUC-gap bound. **Declared** attributes a number to the developer
     that Quaestor set, which is D-120 edit 3's class over the same artifact and the same 0.08 —
     the second live run to write it, so it is a drafting habit and not one run's slip. The `after`
     keeps the citation immediately after the number it carries, where D-113 puts it.
  4. §4 `### Follow-up analyses`, line 482, the `loan_age below_median` paragraph — delete the
     closing clause:
     - `, and across the loan-age partition the defect reads as a level shift rather than a seasoning-shape failure.`
       → `.`

     The absolute gaps across the two loan-age halves are alike — 0.0091 on seasoned loans out of
     time against 0.0082 on newer ones — and the relative shortfalls are not: about **3.8×** on the
     seasoned half against **1.5×** on the newer. A level shift is what the absolute reading says
     and the relative reading denies, so the clause resolves an absolute-versus-relative ambiguity
     in the direction the evidence does not support. Cutting it is a wording edit and leaves the
     paragraph's own numbers standing; the replacement reading would need a derived ratio the
     excerpt may not add, and the pre-flight item below is the way to give the drafter that
     quantity instead of asking Phase 16 to compute it.

  **Read and deliberately not edited**, named here so they are not rediscovered as defects. Each
  is either outside §2/§4 or not a wording matter:

  - **§6, `F-001`'s fourth paragraph:** "the shallow slope means the shortfall is not a constant
    offset but widens as predicted risk rises, so predicted prepayment speeds understate realised
    speeds most where the model scores highest". True of the **absolute** gap on the forward-split
    decile tables — `calibration.out_of_time` bin 1 at 0.009 against bin 10 at 0.015 — and false
    of the **relative** one, which collapses from about 37× in bin 1 to about 1.45× in bin 10, so
    the understatement is worst where the model scores **lowest**. It is the same
    absolute-versus-relative reading as edit 4, and it is in §6, which the excerpt does not take.
    It is not edited because the excerpt is §2 and §4, and it is not repaired in the record because
    the record is the record.
  - **"Roughly half" (§4 line 178, §4 line 331, §6 line 552) and "three developer-declared
    thresholds" (§1 line 34):** the word-number class already on the Phase 12 pre-flight list
    against `DRAFT_INSTRUCTION`, the same list attempt 1's "roughly six times" went on. A
    word-number is not verifiable and not a claim, so nothing flags it; whether the drafter should
    be told to write the figure instead is a prompt question for the pre-flight, not an excerpt
    edit.
  - **§5 line 534:** the drafter wrote "the change in servicing value is -1078000", so **D-167's
    verb rule was not exercised live on this run**. Attempt 1 wrote "falls by 1078000" against the
    same negative artifact and that is what D-167 was built for; this run chose the neutral verb
    and the signed path never ran. D-167 therefore still has no live evidence, only
    `tests/test_verifier_match.py`'s seven cases, and the next run that writes a direction verb
    over a scenario end is its first.

  **Two pre-flight items this points at, stated and not done here.** Both are artifact-shape
  changes rather than prompt changes, and both would give the drafter the quantity it reached for
  and had to approximate:

  1. A `C1` candidate's evidence should carry the **breached split's `calibration.<split>` decile
     table**. F-001's nine evidence artifacts are the two `C1` thresholds, the out-of-time
     calibration slope, the `mean_predicted`/`event_rate` pair on each forward split, and the two
     `calibration.mean_rel_gap.<split>` figures derived from those pairs. The decile table that
     shows whether the shortfall widens or narrows **with score** is in the store and is not among
     them, which is why §6's fourth paragraph asserts a shape from a slope alone.
  2. Sub-population artifacts should carry a **`mean_rel_gap` beside `mean_predicted` and
     `event_rate`**. `calibration.mean_rel_gap.<split>` exists at split level — F-001 cites two of
     them — and no `metrics.<split>.sub.<slug>.*` name carries it, which
     `tests/test_live_msr.py::test_the_loan_age_partition_is_a_level_shift_only_in_absolute_terms`
     asserts. The relative gap is the quantity a prepayment reader uses, and a drafter that has
     only `mean_predicted` and `event_rate` per slice will keep writing the absolute reading, which
     is edit 4 and §6's paragraph both.

  **With this commit the MSR half of Phase 9 is closed, and Phase 9 with it.** This run is the
  **first live run with a finding** in a report the README can excerpt, and four decisions were
  exercised live for the first time on it or its predecessor: **D-156** (section 6 draws the
  finding it is handed and moves nothing to the open items), **D-162** (the verified data manifest
  is cited in §3 and carries its Appendix C row), **D-164** (`R1`'s z gate is cited in §5) and
  **D-165** (§1 names `F-001` instead of asking for a count it is never given). D-165 had no live
  evidence at all before this run, because attempt 1 is the run that exposed it.
- **Why:** The reason is D-120's and it has not changed: a report's value in a README is that a
  reader can be told "this is what the pipeline wrote, unedited, and here are the trace, the
  cassettes and the artifact store it wrote it from", and an edited `report.md` cannot be told that
  about however small the edit. What is new here is that this excerpt has a **finding** in it, so
  the four sentences matter more than the credit run's five did. A reader who sees §4 alone is
  reading the section that raises `F-001`, and three of the four edits are about who owns a number
  or how many findings there are — precisely the things a validation report exists to be exact
  about. Edit 4 is the different one: it removes a sentence rather than rewording one, because the
  sentence's error is a **conclusion** and the honest excerpt is the one that stops at the evidence.

  Rejected alternatives. Editing `report.md` and noting it here, which makes every future citation
  of this run's 0.9966 a citation of a file a human touched — refused for D-120's reason. Excerpting
  §2 and §4 unedited, which publishes "raised as C1 calibration findings" beside a scope table
  reading one finding. Rewriting edit 4's clause into a relative reading, which would put a ratio
  the artifacts do not hold into an excerpt whose whole claim is that every number in it is cited —
  the pre-flight item is the fix, and the excerpt waits for it. Excerpting §6 as well, so the
  finding's own narrative is in the excerpt: refused, because §6's fourth paragraph carries the
  absolute-versus-relative error above and would then need a fifth edit, which is an edit to a
  **conclusion** rather than to wording and past what D-120 licenses. And re-running the pipeline
  for better wording, which is $6.49 and twenty-three minutes for a different four sentences, and
  would throw away the first run whose §2 and §4 both verified whole.
- **Measured:** `tests/test_live_msr.py`, 22 checks, every figure re-derived from the committed
  `trace.jsonl`, `claims.json`, `findings.json`, the 21 cassettes and `artifacts/index.json`. The
  four `before` strings are each in `report.md` exactly once and no `after` changes a number under
  `eligible_numbers`; the excerpt is asserted to be §2 and §4 whole, with all four edits inside §4
  and none in §2. The suite goes 1591 → 1613. `docs/EVALUATION.md` carries the dated attempt-2
  entry with the per-section pre-repair counts and the loop's loan-age result; `PROGRESS.md` ticks
  Phase 9 closed on both halves.

## D-169. An algorithm name is not a claim: the `algorithm_name` exclusion class

- **Date:** 2026-09-17 (Phase 9 follow-up 8)
- **Q:** Section 3 of the MSR excerpt run wrote "The run resolved the declared input files and
  verified each one against its recorded **SHA-256** digest before any split was read." The `256`
  went into grounding precision's denominator as claim `7a2768dcbeb4fed3`, came back `unsupported`
  — nothing in the store holds it, and nothing could, because it names a hash function — and the
  scoped repair round removed it, leaving "its recorded **cryptographic** digest". It is the run's
  **only** pre-repair failure: 297 of 298 rather than 298 of 298, and 0.9966 rather than 1.0000.
  Is the fix an exclusion class, and where does it stop?
- **A:** An exclusion class, `algorithm_name`, beside `regulatory_section_id`, for a hyphenated
  identifier of the form `[A-Z]{2,}-\d{1,4}` whose letters are **not** a regulator code the
  existing class already covers. `SHA-256`, `SHA-3`, `MD-5`, `ISO-8601` and `RFC-8259` mask;
  `SR 11-7` and `OCC 2011-12` keep their existing class, which the mask order guarantees as well as
  the lookahead — `_ALGORITHM_NAME_RE` runs **after** `_REG_SECTION_ID_RE`, so a regulator code is
  already blanked before this pattern sees the line. It is added to `_PATTERN_ORDER` after
  `regulatory_section_id`, so `claims.json` and Appendix A list it in one place across runs.

  Bounded so that it cannot eat a measurement, which is the failure mode an exclusion list is most
  dangerous for, because it lowers the denominator invisibly. The letters are two or more, upper
  case and a whole word, so a **shock label keeps its number**: `a shock of -300 bp` and
  `scenario -300` both tokenise as -300, and the lower-case `bp-300` tokenises as 300. That last
  case keeps its digits and loses its sign because the minus follows a word character and
  `NUMERIC_TOKEN_RE`'s lookbehind refuses it — the tokenizer's long-standing reading of a hyphen
  inside an identifier, not something this class introduces, and the test says so. The integer is
  one to four digits and a whole word, so `SHA-25612` does not match.

  **The one place the shape rule over-reaches, stated rather than hidden:** an upper-case `BP-300`
  would be masked. Nothing in this pipeline writes it — the renderer's shock column is `shock_bp`
  with a bare integer, and both live runs of the hazard subject wrote the shock as a bare number in
  prose — and the alternative is a whitelist of algorithm names, which a drafter falls off the first
  time it reaches for a fifth one. **The second, also stated:** `SR-11-7`, hyphenated where the
  corpus writes `SR 11-7`, is refused by the lookahead and is not matched by `_REG_SECTION_ID_RE`
  either, so its `11` and `7` would both be eligible. No committed corpus chunk, subject, fixture
  or report writes that spelling; whether the **regulatory** pattern should learn it is that
  pattern's question and deliberately not answered here, because answering it inside this class
  would file a regulator code under "algorithm name".
- **Why:** This is the **fourth** class of one shape, and naming the shape is most of the value of
  the entry. D-112 excluded a section cross-reference written in words, D-116 a reference to this
  project's own decision log, D-166 an integer that labels a bin, and this one the digits of an
  algorithm or standard name. What the four have in common is an **identifier whose digits a reader
  does not read as a measurement** — and in all four the pipeline put the number in the denominator,
  failed to verify it, and repaired prose that was already true. The repair is the real cost: "its
  recorded cryptographic digest" is honest and worse, exactly as D-166's "the first decile" was, and
  a validation report that may not name the hash function it checked against is a report our own
  tokenizer has made vaguer.

  The near-miss is worth recording because it is the same one D-166 had. The renderer's own caption
  two lines below the drafted sentence reads "each verified against its SHA-256 before the run", and
  it was never a claim — it is inside a renderer block, and `drafted_prose` removes those before the
  model ever sees them. So the class was invisible until a drafter wrote the phrase in its **own**
  prose, which is the third time that ordering has hidden a class from six or seven live runs.

  Rejected alternatives. Widening `_REG_SECTION_ID_RE` to take any `[A-Z]{2,}-\d+`, which would file
  `SHA-256` as a regulatory section id in `claims.json` and Appendix A and make the exclusion list
  lie about why a number was dropped — the list is auditable or it is nothing. Telling the drafter
  in `DRAFT_INSTRUCTION` not to name hash functions, which trades a true sentence for a prompt rule
  and would not have helped the run that is already committed. Letting the claim stand and accepting
  0.9966 as the honest figure: refused, because the number was never a claim, so 0.9966 is not a
  measurement of the drafter's grounding but of our own tokenizer's reach — which is D-084's whole
  argument for there being one definition of an eligible number. And a whitelist of the five names
  above, refused for the reason given under the `BP-300` limitation: the shape is the rule, and a
  list of five is a list that is wrong on the sixth.

  **Not** retrofitted to the committed run. `eval/results/first-live/msr/` keeps its 0.9966, its
  repair round and its "cryptographic digest", because the record is what the pipeline produced
  (D-087, D-120, D-168). `tests/test_live_msr.py` asserts the run's figures as they are, and the
  test below asserts the same sentence produces no claim under this build — the two together are
  the before and after.
- **Measured:** `tests/test_verifier_extract.py` gains five cases: the live sentence verbatim from
  `claims.json`'s `pre_repair` record, which now yields zero claims with `SHA-256` listed under
  `algorithm_name`; one case per family the class covers, so the shape rule cannot shrink silently;
  `SR 11-7` and `OCC 2011-12` asserted to stay `regulatory_section_id` with no `algorithm_name`
  entry at all; the three shock-label spellings, each keeping its number; and the bounds,
  `SHA-25612`, `A-5` and `sha-256` all still claims. The suite goes 1613 → 1618. The golden report
  is untouched, both `--synthetic --llm fake` validates and the real-panel `--data … --llm fake`
  validate differ only in run id, timestamp and wall-clock — the real panel still raises one `C1` at
  medium over the same nine evidence keys at 1.0000 over 51 claims — and
  `pytest tests/probatio --cassette=replay` still passes 40 with every snapshot `unchanged` and
  zero provider calls, because this touches no prompt.

## D-170. The synthetic MSR process is not recalibrated to the real fit, and the thread's premise was backwards

- **Date:** 2026-09-17 (Phase 9 follow-up, decided by the human in Cowork)
- **Q:** The handoff's §6.1 asks for the synthetic MSR process to be recalibrated to the real
  Freddie fit, on the grounds that "the synthetic projection loses only 1.3% of servicing value at
  −300 bp where a real MSR loses about a third, so the incentive effect is too weak". Should it be?
- **A:** **No, and the premise is backwards.** Measured, the synthetic book loses **81.29%** of its
  servicing value at −300 bp — **−1,297,986** on a base of **1,596,815**, the figure D-047 and the
  subject's `README.md` have carried since Phase 4 — where the real panel loses **11.35%**
  (**−1,077,724** of **9,498,507**, `eval/results/first-live/msr/` and
  `subjects/msr_prepayment/artifacts/real/projection.json`). The synthetic projection is **7.2×
  more responsive** than the real one, not tamer. The **1.3%** of §6.1 predates **D-040**'s rate
  ramp, which is the change that moved the book out of the money and the convexity to negative;
  nothing since Phase 4 has reported it.

  **The incentive coefficient is the strong axis too, not the weak one.** The synthetic champion
  recovers **1.2527** per percentage point of incentive — standardised **1.2534** over an
  `sd(incentive)` of **1.00055** on its training split, against the generating process's
  `beta_incentive` of **1.15** — where the real champion recovers **0.65626**, its standardised
  **0.3952** over an `sd(incentive)` of **0.60214**. That is a factor of **1.91**, and
  **1.17×–1.58×** on a like-for-like retained-feature set, so the synthetic responds more under
  every comparison made.

  **The gap decomposes multiplicatively, and moneyness is the larger half.** Of the 69.94 points
  between −81.29% and −11.35%: matching the real book's moneyness alone takes the synthetic to
  **−38.97%** (**60.5%** of the gap), matching the coefficient alone to **−49.25%** (**45.8%**),
  and both together to **−21.61%** (**85.3%**). The residual **10.26** points is the real book's
  tighter incentive dispersion — p10-to-p90 of **1.25 pp** against **2.00** — its mean loan age of
  **102.6** months against **54.6**, and its further-amortised balances.

  **The mechanism is the book's moneyness at the valuation month.** Mean first-projected-month
  incentive is **−2.293** on the real book and **−0.717** on the synthetic one, so the same −300 bp
  lands the synthetic book deep in the money — **100%** of loans above 0 and **97.8%** above 1 pp —
  and the real one barely at it, **91.4%** above 0 and **29.8%** above 1 pp. The base hazard the
  shock multiplies is also **3.55×** higher on the synthetic side to begin with. **The declared
  machinery is shared and is not the difference**: horizon 180 months, servicing fee 25 bp,
  discount 0.08 and the same seven-point shock grid, through one code path on both panels (D-043).
  The `turnover_floor` acts on the **generating process** and not on the projection, which rolls
  the fitted champion forward; at +300 bp both projections run below it.

  **One apparent disagreement with D-040 and the subject `README.md`, reconciled rather than left.**
  Both describe the ramp as leaving the surviving book "about two points out of the money", which
  reads as a level and is not one: the measured mean first-projected-month incentive is **−0.717**.
  Two points is the size of the **move**. Re-measured offline at the declared seed, the same book's
  mean first-projected-month incentive is **+1.288** with `rate_ramp_pp_per_year` set to zero and
  **−0.717** at the declared 1.05 for two years — a move of **2.005** points, which is the quantity
  D-040's own argument is about. Both readings agree the book is out of the money; the real book,
  at −2.293, is further out, which is the whole of the mechanism above.

  **And the knob §6.1 names cannot reach its target from either side.** Swept over
  `beta_incentive ∈ [0.50, 2.30]`, the −300 bp response stays between **−47%** and **−83%** and is
  **non-monotone**, peaking near **1.40**, because the intercept solve holds `target_smm` fixed and
  a stronger incentive slope is paid for with a lower intercept. Nothing in that range comes near
  −11.35%. The band on which the `{}` expectation of D-047 survives is recorded here because it is
  a useful robustness statement about the control in its own right: **[0.80, 1.40]**, with the
  shipped **1.15** near its middle, a **`C1`** below it — the out-of-time calibration slope crosses
  the declared 1.20 — and an **`R1`** above **1.75**, on the **AUC-gap** arm at 0.109 and 0.169
  against the 0.10 threshold, not on the sign-flip arm D-164 tightened.

  **§6.1's second clause is answered the same way.** It reports that the synthetic's fitted
  `burnout` came out **+0.079** against the process's **−0.18** (D-047). The **real** champion's
  fitted `burnout` is **+0.0008253** — positive, against the same negative subject-matter prior,
  on the real panel. The synthetic reproduces the real panel's behaviour on exactly the point the
  thread complained about, so there is nothing to calibrate there either.
- **Why:** D-047's own argument for having a second control is that **two clean controls that
  behave differently are worth more than two that behave the same**. This subject's job is to be a
  clean control with a known generating process and a detectable seeded defect, not a replica of
  one Freddie Mac sample; the replica is what `--data` mode is for, and D-161 already records what
  each control measures in each data mode.

  Against no benefit, recalibrating costs. It rewrites the whole `A` paragraph of **D-047**,
  **D-053**'s `msr_prepayment` paragraph, five rows of **D-136**'s table and its collateral
  paragraph, **D-044**, **D-161** and **D-164**; the subject `README.md`'s measured table; four
  lines of `PROGRESS.md`; `CHANGELOG.md`; two lines of `docs/DESIGN.md`; `eval/taxonomy.yaml`'s
  control baseline; and **8 tests across four files with about 24 pinned assertions**. It makes the
  clean control **stop being clean** — at the literal recalibration the control raises `{C1
  medium}`, on an out-of-time calibration slope of **1.2227** against the declared 1.20 — which
  would put into D-161 a baseline **chosen** rather than discovered, and choosing the arithmetic
  that makes a control come out the way one wants is what **D-035**, **D-046** and **D-161** each
  refuse. And it changes four of the seven MSR rows' **collateral** finding sets, with
  `msr__C1__oversampled_hazard` gaining an **`X1` at high** on a projection convexity that flips
  from **−541,832** to **+325,859** — a finding `04` §4 scores. Every `msr__*` recipe does still
  fire its own class at severity ≥ medium under the probe, so detection is not what breaks; the
  collateral is.

  Rejected alternatives. **(i) Recalibrating through the rate path instead**, which is the larger
  lever — **+157.63 bp** of extra ramp is worth **42** of the 70 points — refused for the same
  reason, and because the ramp, the cut dates and the three vintages are **declarations** decided
  before Phase 4 rather than free parameters; moving them to land a projection figure is the moved
  floor of `T1` wearing a generator's clothes. **(ii) Recalibrating `beta_incentive`**, which is
  what §6.1 asks for: it cannot reach the target at any value in the sweep, and the direction §6.1
  proposes — *more* incentive response — is the wrong one. **(iii) Leaving the thread open**, which
  leaves a stale number in the handoff for the next reader to act on, and is why this entry is long
  enough to carry the arithmetic that closes it.

  The working record is the diagnosis session of **2026-09-17**, whose report is
  `~/code/quaestor-package/phase10-draft/msr-synthetic-recalibration-diagnosis-report.md` — outside
  the repository, like every Cowork draft. Every figure above is that session's measurement,
  reproduced there from `/tmp/msr_data` with all five `package.yaml` digests verified and from a
  `/tmp` copy of the subject, **except** the two committed figures, the coefficient arithmetic, the
  `beta_incentive` and `turnover_floor` readings and the D-040 reconciliation, which were
  re-measured against this repository at `666a41b` while the entry was written.

## D-171. The calibration finding carries its decile table, and a slice carries its relative gap

- **Date:** 2026-09-17 (Phase 12 pre-flight, commit A; ruled in Cowork from
  `preflight-inventory-report.md`, one entry for both halves because D-168 says the two are one
  decision)
- **Q:** Two of the pre-flight's items are about the same missing quantity read at two levels.
  (ix) A `C1` candidate cites the scalars its detail sentence quotes — a slope, a mean predicted
  probability, an observed rate, the bound each was read against — and not the **decile table** of
  the split it fired on, so the reader of the finding is shown the means and not the shape behind
  them. (x) A sub-population stores eight scalars and no **relative** gap, so a report that wants
  to say whether a level error is uniform across a partition or concentrated in one half has the
  two absolute shortfalls and nothing to divide them by. Should either be stored, and in which
  order?
- **A:** **Both, and the artifact side lands before the prompt side.**

  **(ix)** `_calibration_rule` now opens each firing split's candidate with
  `calibration.<split>` and adds the branch evidence to it, so on the real MSR panel F-001's
  evidence goes **9 → 11**, gaining `calibration.out_of_time` and `calibration.vintage_holdout`
  and nothing else. The table is already stored for every split computed, so the candidate mints
  no artifact: it cites what the store holds. The eleven keys, measured offline on 2026-09-17 with
  `quaestor validate subjects/msr_prepayment --data /tmp/msr_data --llm fake` against the five
  verified `package.yaml` digests, are `calibration.out_of_time`, `calibration.vintage_holdout`,
  `calibration.mean_rel_gap.out_of_time`, `calibration.mean_rel_gap.vintage_holdout`,
  `calibration_slope.out_of_time`, `metrics.out_of_time.mean_predicted`,
  `metrics.out_of_time.event_rate`, `metrics.vintage_holdout.mean_predicted`,
  `metrics.vintage_holdout.event_rate`, `threshold.C1.calibration_slope.min` and
  `threshold.C1.mean_ratio_rel`. The breached splits are `out_of_time` — slope **0.4321** below
  0.80 **and** relative gap **0.4618** above 0.25 — and `vintage_holdout`, on the gap alone at
  **0.4932**, its slope **0.8502** being inside the band; `test` and `train` do not fire and their
  tables are not cited, which is what the new rule test asserts. The store still holds **273**
  artifacts and the run still writes **51** claims at grounding precision **1.0000**: the two
  tables were already there, and a table's cells are excluded from extraction because the renderer
  and not a model writes them (D-013, D-115). The visible change to the report is that section 6
  now renders both decile tables and the artifact appendix indexes **52** entries rather than 50.

  **(x)** Each slice now stores `metrics.<split>.sub.<slug>.mean_rel_gap` beside its
  `mean_predicted` and `event_rate`, and the per-slice metrics table gains the row. The formula is
  **not copied**: `relative_gap(mean_predicted, event_rate)` is now a module-level function that
  both `_one_split` and `_subpopulation` call, so `calibration.mean_rel_gap.<split>` and
  `metrics.<split>.sub.<slug>.mean_rel_gap` are the same arithmetic under two names — unsigned,
  `|mean_predicted - event_rate| / event_rate`, guarded at a zero denominator. A slice that is the
  whole of its split is refused by D-121, so the two levels cannot be made to agree by
  construction; one function is how they agree.

  **The order is forced.** Pre-flight item (vi) forbids the drafter from computing a quotient of
  two cited numbers, because a number in prose needs an artifact behind it and a division the
  renderer did not do mints a third number nothing verifies. So the quotient has to exist in the
  store before the prompt may forbid deriving it, and this commit is the artifact half.

  **The knock-on to D-161 is measured, not expected.** `control_msr_clean`'s baseline evidence in
  `eval/taxonomy.yaml` goes from three keys to five, gaining the two tables, and
  `tests/test_seed.py::test_every_control_carries_the_baseline_d161_measured` with it. D-161
  itself is **amended with a dated paragraph and not rewritten**, on D-160's pattern. The evidence
  rule the baseline exists to support is untouched: detection of a seeded `C1` on this subject and
  data mode still requires a **test-split** artifact, and neither new key is one.

  **The pre-flight assertion is discharged.** `tests/test_live_msr.py` asserted that no
  sub-population artifact carried the relative quantity, with `(pre-flight)` in its own message.
  It now reads two runs and says which is which: the **committed** run of 2026-09-17 in
  `eval/results/first-live/msr/` still has no `.sub.*.mean_rel_gap`, because it predates this
  commit and that is a fact about the run rather than about the code, and a **fresh** offline
  slice of the synthetic hazard subject carries the quotient as an artifact a sentence can cite.
  The ratios that test derives by hand — the seasoned half of `loan_age` out of time about **3.8**
  times its observed rate against **1.5** on the newer half, where the absolute shortfalls are
  **0.0091** and **0.0082** and read as a level shift — are exactly what the run could not state,
  and are why D-168 cut edit 4's closing clause.

- **Why:** The two items share a reader. The `C1` detail sentence reports means, and means are the
  statistic under which a level error looks uniform: out of time the absolute gap **widens** from
  about 0.009 in bin 1 to 0.015 in bin 10 while the relative one **collapses** from about 37 times
  to about 1.5, and the same reversal appears across the `loan_age` partition. A finding that
  carries only the means hands the reader the reading that is wrong in both places. The table is
  free — it is stored, hashed and rendered already — so citing it costs nothing and removes the
  need for the narrative to describe a shape it cannot cite.

  Storing the slice quotient rather than letting the sentence compute it is the same argument from
  the other side. Rejected alternatives: **(i)** having the drafter divide the two cited scalars,
  which is what (vi) forbids and what the excerpt run actually could not do, so the clause was cut
  instead of being written; **(ii)** putting `mean_rel_gap` in `SCALAR_METRICS`, which would rename
  the split-level artifact from `calibration.mean_rel_gap.<split>` to `metrics.<split>.mean_rel_gap`
  and break every committed run's index and every citation into it, for tidiness; **(iii)** adding
  the slice gap as a *candidate* rule, which D-086 refuses — a slice selected by one of the model's
  own features discriminating or calibrating differently is usually the model conditioning
  correctly, and this commit raises no new candidate on any subject; and **(iv)** duplicating the
  four-token formula at the two call sites, which is two chances to disagree about the one number
  a report will put side by side. The zero-denominator guard is kept although it is **unreachable
  through the tool** — `stats.auc` refuses a sample with no event before any gap is computed, on a
  split and on a slice alike — so it is exercised on the function directly and documented as the
  guard it is rather than as a branch the pipeline can take.

  Measured at both ends: **1,618 → 1,622** offline tests, zero failures, coverage 99% of
  `src/quaestor`; both synthetic validates unchanged at `{E1 low}` and `{}`; the real MSR fake
  validate differing from its predecessor only in the two rendered tables, the appendix count and
  the run id; `examples/golden_report/` untouched; and `pytest tests/probatio --cassette=replay`
  **40 passed** with zero provider calls, because this commit touches no prompt.

## D-172. Two rules the machinery cannot check, kept and labelled as drafting rules

- **Date:** 2026-09-17 (Phase 12 pre-flight, commit B; the wording ruled in Cowork rather than left
  to the session, because it is what a $28 sitting carries)
- **Q:** The inventory's items (vi) and (viii) put three bullets into `DRAFT_INSTRUCTION`. The
  first — a quantity goes in digits with its citation, never in words — is enforced downstream.
  The second and third — do not do arithmetic, and say which comparison you are making across two
  populations — are not, and `DRAFT_INSTRUCTION`'s own docstring says "Every rule in it is enforced
  somewhere downstream, or it is not a rule". Do the two unenforceable rules go in, and what
  happens to the sentence?
- **A:** They go in, and the sentence is rewritten to say which rules rest on what. "A quantity
  goes in digits" is enforced by the tokenizer and the matcher **once it is obeyed**, which is
  precisely the point of asking: a number in digits is tokenized as a claim and is either cited
  and matched or counted against the report, and a quantity written as a word — "roughly half",
  "twice", "six times" — is exactly the quantity that escapes both. "Do not do arithmetic" and
  "say which comparison you are making" are enforced by nothing and are **drafting rules rather
  than checked ones**, and the docstring now says so in those words. A cited number that happens
  to be the quotient of two others is indistinguishable, downstream, from a number read off an
  artifact; and whether a paragraph concluded that two populations are alike is a judgement about
  a sentence, not about any number in it.
- **Why:** The measured failures they answer are failures of drafting, and the place to answer a
  drafting failure is the drafting instruction. Named as evidence: D-168's "roughly half" in three
  places and its "three developer-declared thresholds"; attempt 1's "roughly six times"; and
  D-168's cut clause together with its §6 counterpart, where absolute gaps of **0.009** and
  **0.008** were read as alike while the relative gaps behind them were **3.8×** and **1.5×** —
  the case that is the third bullet's whole subject. The rejected alternative is dropping the two
  for being uncheckable, which leaves those failures with nowhere to be answered and leaves the
  reader of the prompt with a docstring that overstates what the pipeline can see. Labelling an
  unenforceable rule is cheaper than pretending it is enforced, and this project's whole argument
  is that the difference between the two is worth writing down.
  **The cross-reference the first sitting proved necessary** is recorded in D-174 and is part of
  the same two bullets: both are instructions to *omit* something, and the rule twenty lines above
  them — never write that a quantity is absent (D-100, and criterion 5 of the grounding rubric) —
  says the omission has to be silent. A drafter reading both at once explained why it left a
  comparison out, and the explanation is the forbidden sentence. Each bullet now ends by pointing
  at that rule. It is a cross-reference and not a fourth rule: no new obligation is created, and
  the obligation it names has been in the prompt since D-100.

## D-173. Open items are minted by a rule, and the rule has one home

- **Date:** 2026-09-17 (Phase 12 pre-flight, commit B; the schema question ruled in Cowork)
- **Q:** D-096 put `### Open items` at the end of section 6 and told the drafter what kind of thing
  belongs there, naming two examples in the brief: a coefficient whose fitted sign disagrees with
  its univariate direction, and a feature-vector overlap the within-train duplicate share explains.
  A brief's examples are not a rule. What decides which observations are open items, and where does
  the decision live, given that `eval/score.py` has to recompute the same list to score a run?
- **A:** A function, `quaestor.findings.open_items(store, thresholds)`, beside `Finding` and
  `SECTION_FOR_CLASS`. It reads three families — a sub-population's `auc_gap` and `share` against
  `threshold.O1.slice_auc_gap` and `threshold.O1.slice_min_share` (D-102); `sign_check.<f>.agrees`
  against the feature's own `univariate_direction` (D-095); and `leakage.overlap.features` above
  `threshold.L2.overlap` but within `threshold.L2.overlap.features_effective` (D-086) — and returns
  an `OpenItem` per qualifying observation carrying its artifact names, the bound it was read
  against, the sentence-sized facts section 6 needs and an owner. Every quantity and every bound is
  already in the store, so nothing here computes a number a report cannot cite; a bound the store
  does not hold mints nothing, because an uncitable comparison is the case D-091 refuses.
  `_FINDINGS_BRIEF` stops naming examples and says the open items are the ones listed at the end of
  the prompt and no others; `drafter.open_items_block` renders them on `_findings_block`'s pattern;
  and `eval/score.py` will import the same function rather than re-derive the rule. **No
  `open_items` block in `findings.json`**: that is a report-schema change after Phase 1, which
  `CLAUDE.md` makes a stop-and-ask, and nothing needs it.
- **Why:** It is D-156's and D-165's shape a third time — the section is handed the list, not the
  criterion — and the committed real-MSR excerpt run is the measurement that says the shape is
  still missing here. Run over `eval/results/first-live/msr/artifacts/`, the rule mints **six**:
  the run's own three sub-populations, by name and by the same numbers, and three features whose
  fitted sign contradicts their univariate direction — `orig_ltv`, `sato`, `season_sin` — which
  that run recorded as `sign_check.n_disagreements` = 3 and whose names appear nowhere under its
  `### Open items`. A superset and not a subset, which is the direction that makes this a fix
  rather than a regression: a rule that minted fewer than a validator reported would be dropping
  an observation, and that would have been a stop-and-report. The observation it adds is one of
  D-096's own two examples, computed, stored, and never asked about on six live runs.
  Three alternatives were rejected. **The schema change**, above. **Promoting an open item to an
  `info` finding**, which is D-096's own rejected alternative and would put a helpful observation
  in the study's precision denominator, so a validator that noticed something would score a false
  alarm for it. **Leaving the examples and adding the sign check to them**, which is the shape the
  excerpt run already falsified.
  Two consequences worth naming. Section 6 is no longer handed the bounded loop's steps: a material
  step reached it as a follow-up block and now reaches it as one of the minted items, so the list
  is one object and not two, and `tests/test_report_sections.py` gained an assertion that the
  step's own `why` no longer reaches section 6. And the slice rule the loop asked for is joined
  onto the item it produced, on the artifacts they share, because the store knows a sub-population
  by an artifact stem and the drafter may not write a logical name in the prose (D-112) — guessing
  the expression back out of the slug would be wrong on any column whose own name ends in `_low`.
  The two threshold modules are imported **inside** the functions that need them: `quaestor.tools`
  imports this module for `FindingCandidate`, so a module-level import is a circular-import failure,
  measured rather than assumed.

## D-174. The seventh record sitting was killed at three and a half cases, and what it fixes about how a sitting is run

- **Date:** 2026-09-17 (Phase 12 pre-flight, commit B; the sitting run and killed by the operator)
- **Q:** The seventh record sitting was started against the seven stranded drafting cases and was
  killed by the operator after three completed cases and one partial one. What did it cost, what
  did it find, and what does the fact that it had to be killed say about how the next sitting is
  run?
- **A:** **$17.1014**, on four tapes, none of which is committed: the working tree was restored to
  `82e7bab` for exactly those four paths and the tapes were copied out of the repository to
  `~/code/quaestor-package/phase12-draft/killed-sitting-tapes/` first, so the recordings survive
  and the repository does not carry a tape that was never checked. Per tape, the new interactions
  alone: `conceptual_soundness` +17 at **$4.9868**, `data_integrity` +17 at **$4.8015**, `outcomes`
  +14 at **$4.0417** (partial — one relation interaction, `f193ba8656ecf59b`, was never recorded),
  `summary` +17 at **$3.2714**. That is about **$4.4 a completed case** against $3.94 on the
  committed tapes, which is on estimate and well under the $35 ceiling the session prompt set.
  **The operational rule this sets, which is the reason the entry exists.** The sitting ran for
  about **35 minutes** and completed **3.25 cases** before it had to be stopped, and it was driven
  from a Claude Code background shell, which is what made stopping it a kill rather than a clean
  exit. So: a record sitting is run **from a plain shell, never from a Claude Code background
  shell**, and it is recorded in **batches of at most three cases**, with `--max-cost` set from
  that chunk and not from the whole layer. Lean D's pricing runs take their `--max-cost` from the
  same measurement.
- **Why:** A sitting that cannot be stopped cleanly cannot be budgeted, and a sitting driven from
  an agent's background shell has no operator at the keyboard when it needs one. Three cases is
  the largest batch this sitting demonstrated it can finish inside the window the operator was
  willing to sit for, and a per-chunk `--max-cost` is the only ceiling that can stop a run rather
  than report on it afterwards (D-149: Probatio's own total excludes judge calls and under-counts
  by about half, so the ceiling has to be set below what it will read). Recording the cost of a
  sitting whose tapes were discarded is deliberate: `docs/EVALUATION.md` publishes what this layer
  has cost, and $17.10 that bought nothing is part of that figure exactly as the ~$44 of stranded
  calls in D-140's four sittings is.
  **The seven drafting cases are left stranded in this commit, knowingly.** `pytest -q` therefore
  fails gate condition 6 on those seven until the tapes are recorded, which is planned for after
  lean D, together with the pricing runs. `CLAUDE.md`'s "never commit a broken tree" is being set
  aside for that one gate condition and for no other: the full offline suite excluding
  `tests/probatio` is **1,599 passed**, and every other gate is green. It is recorded here rather
  than absorbed, because a stranded tape that nobody wrote down is indistinguishable from a
  forgotten one.

## D-175. The grounding judge fails about one reply in ten, and that goes in the study's limitations

- **Date:** 2026-09-17 (Phase 12 pre-flight, commit B; measured on the killed sitting's own tapes)
- **Q:** The killed sitting's `draft_section.data_integrity` failed its judge assertion at **0.80**
  where its baseline is **1.000** — the stop-and-report the session prompt names. Is that the new
  rules making the drafting worse, or is it the judge?
- **A:** Both, and the proportions are measurable because a Probatio case draws eight times: once
  for the run and once for each of the seven relation perturbations. Over the **30 judge replies**
  the sitting recorded, **3 are failures**: `data_integrity`'s base run (criterion 5 — "sentence
  declares no characteristic-index bound was provided to this section"), and two perturbations of
  `conceptual_soundness`, which passed its own base run 4/4 (one criterion 5 — "sentence declares
  no ratio of the two AUCs is reported" — and one criterion 1, an uncited `1`). `summary` and the
  partial `outcomes` recorded none. So the rate is about **1 in 10 draws**, and `data_integrity`'s
  base run drew one of them; its other seven draws all scored 1.0.
  Two of the three are the same defect and it is real: both new bullets are instructions to omit
  something, and the drafter explained the omission, which criterion 5 and D-100 forbid. That is
  fixed by the cross-reference recorded in D-172. What the count adds is that **a single clean
  re-record would not be evidence the fix worked**, because a 1-in-10 failure passes nine sittings
  in ten by itself.
- **Why:** This is the same limitation D-157 records from the other end. There, the judge was
  measured against a human on 40 labelled drafter outputs and agreed on 38, **Cohen's kappa
  0.771**, recorded as it stands with the rubric deliberately not revised to fit. Here the judge is
  measured against *itself* on eight draws of one prompt and disagrees with itself about one time
  in ten. The two numbers are the same fact seen twice: a model judging prose is a noisy instrument
  with a quantified amount of noise, and a gate built on one draw of it inherits that noise.
  **It belongs in `docs/STUDY.md` §8, beside kappa 0.771**, as a limitation written before anyone
  raises it. That file does not exist in the repository yet — it is drafted at
  `~/code/quaestor-package/phase12-draft/STUDY.md` — so this entry is where the measurement is
  recorded until §8 carries it, and the sentence §8 owes is that a per-case judge verdict is one
  draw from a distribution whose self-disagreement rate is about 10% and whose agreement with a
  human is kappa 0.771. The rejected alternative is raising `--runs` on every drafting case so the
  gate reads a majority rather than a draw, which multiplies the layer's recording cost by the
  number of runs and buys an answer the study can state instead.

## D-176. The Claude CLI provider records an occasional tool-call transcript in place of an answer

- **Date:** 2026-09-17 (Phase 12 pre-flight, commit B; found reading the killed sitting's tapes,
  present at `82e7bab` and earlier)
- **Q:** One of `draft_section.data_integrity`'s new interactions holds, in place of a drafted
  section, 487 bytes of a Claude Code agent issuing a `Bash` tool call — an `ls` and a `cat` over
  the memory directory of its own scratch session. Is that something this commit introduced?
- **A:** No. `ClaudeCLILLM` drives `claude -p` as a subprocess, and the process it drives is a full
  Claude Code session, so an answer that begins with agentic tool-call text is a shape that
  provider can always produce. `structured()` re-asks on an answer that is not the requested JSON,
  and the retry answered normally, which is why the case still produced a draft and why the tape
  carries more interactions than calls. The committed tapes at `82e7bab` already hold seven of
  these — 2 in `draft_section.conceptual_soundness`, 2 in `draft_section.outcomes`, 3 in
  `draft_section.summary` — so it is a pre-existing property of the record path and part of what
  D-165's "4 `structured()` re-asks" counted without naming.
- **Why:** Recorded because nothing in this log named it and the next reader of a tape will meet
  it, and because it changes what a tape's interaction count means: an interaction is a *call*, not
  an *answer*, and a tape with 33 interactions did not draft 33 sections. It is deliberately **not
  fixed here**. Suppressing the shape means either constraining the subprocess, which makes the
  offline layer depend on a flag of a tool this project does not own, or filtering the answer,
  which is a provider quietly rewriting what a model said — and the retry that `structured()`
  already performs is the correct handling of a malformed answer whatever produced it. The cost is
  one wasted call per occurrence, about 1 in 20 of this sitting's drafting calls, which is
  recorded in `docs/EVALUATION.md` as part of what the layer cost rather than removed from it.
  Rejected alternatives: counting these interactions out of the published tape totals, which would
  make the totals stop matching the money spent; and pruning them under D-158, which would remove
  interactions a replay genuinely reads, because the retry is keyed on a different prompt and the
  failed first call is part of the recorded sequence.

## D-177. A check of the checklist that raises costs its own row, not the run

- **Date:** 2026-09-17 (Phase 12 pre-flight, commit C; the exit-code change signed by the operator
  before the commit, because it is `quaestor validate`'s scripted interface)
- **Q:** D-088 made a `ToolError` from a *loop-requested* call the step's failure rather than the
  run's, and said in so many words that nothing about the rule-based plan changes: a `ToolError`
  from one of its calls is still the run's failure and still exits 1. The Phase 12 study is
  eighteen seeded variants across three configurations, and a seeded variant is a package built to
  be abnormal — a copied split, a collinear design, a regime column that partitions badly. One
  check raising on one variant discards that variant's whole run, including the paid model call
  under `full_agent`. Does the checklist keep the old rule?
- **A:** No, for every call but one. `_run_checklist` runs the rule-based plan call by call and
  catches `ToolError`: the check is recorded as a `FailedCheck` carrying the tool and the tool's
  own message, and the pipeline goes on to promote, draft, verify, repair and render with what it
  has. Four things then say what is missing, in four places a different reader looks at:
  **Appendix D** carries the first row, `` `check_collinearity` (M1) | did not run: <message> ``,
  and the tool is skipped in the rows below it so that a check which crashed is not also reported
  as a check that did not apply; **`tools_run`** excludes it, so `checks_without_candidates` never
  claims a dead check looked and found nothing; the **trace**'s `tool_call` event gains an `error`
  field carrying the message, which is the same field `plan_step` has carried since D-088; and
  **section 1** is told, through a block in the drafter's `{extra}` slot, to say in one sentence
  that the validation is incomplete and to name the checks and the classes they would have
  screened for.
  **`run_model` is the exception and the only one.** Everything after it reads what it wrote, so a
  run whose subject never ran has no predictions, every check behind it would raise in turn, and
  the report would be Appendix D and nothing else — which is not a validation of the model, it is
  a note saying the model was never seen. A subject that runs *and fails* does not come through
  here at all: `run_model` turns that into an `R0` candidate and returns normally, and `R0` is a
  finding the report makes.
  **The exit code changes with it.** A run whose checklist partly failed exits **0** where D-082's
  rule was 1 for "ran and did not produce what it was asked for". A report that names the check it
  is missing did produce what was asked for, minus one row. `run_model` failing still exits 1.
  **Any harness or CI step that judges a run must read the run's failed checks — `Appendix D`'s
  "did not run" rows in the report, `ValidationRun.checks_failed` in process, or the `tool_call`
  event's `error` field on the trace — and not the exit code alone**, because a partial checklist
  and a clean one are now the same code.
- **Why:** The cut list puts this commit before any paid run for exactly this reason: a tool that
  crashes mid-run without it costs the whole run, and `docs/STUDY.md` §5's "a run that produces no
  report" row is meant to be empty. The failure mode it removes is the expensive one — not a
  defect the study wants to measure, but the study losing a measurement to an unrelated crash
  after it has been paid for.
  **The instruction to section 1 is a conditional block and not a sentence in `_SUMMARY_BRIEF`,
  and that is a measured choice.** A brief is in the prompt whether or not it applies, so a
  sentence about crashed checks would be in the prompt of every clean run — where it is a rule the
  drafter has to be told to ignore, and where, measured, it moves the pinned `draft_section.summary`
  case by 182 bytes and strands its $3.66 tape for nothing. The conditional block is empty on a
  clean run, and `python tests/probatio/casebuilder.py` rebuilds all three case files
  **byte-identical** under this commit: 0 of 10 cases move, which is what makes commit C free and
  is asserted directly (`test_a_clean_run_adds_not_one_byte_to_any_prompt`).
  Rejected alternatives. **Catching the error inside `registry.call`**, which would hide a failed
  check from `quaestor tool` and from the study harness's own callers — D-088 rejected the mirror
  image of this for the same reason. **Converting the failure into an `R0` candidate**, which
  would put a crash of *this* codebase into the study's detection numbers as a defect found in the
  subject; `R0` is about the subject's run, and a check that cannot run is our problem, not the
  model's. **Letting `run_model` fail softly too**, which produces the empty report described
  above and would make the "produced no report" row read as a clean run. **Naming the failed checks
  in every section's prompt**, which is D-096's two accounts of one fact: Appendix D is the table
  every reader gets, and what section 1 owes is only the sentence that stops a reader taking the
  report as complete.

## D-178. A precision ceiling that erased a number, and a wrapper that marked the wrong one

- **Date:** 2026-09-17 (Phase 12 pre-flight, found by the free `rules_only` sweep over the
  eighteen seeded variants — the cut list's step 3, which exists to be the first live exercise of
  the harness before any paid run)
- **Q:** Seventeen of the eighteen variants came back at grounding precision **1.0000**.
  `msr__L1__eom_balance` came back at **0.9969** — 317 verified and one `unattributed` — and its
  section 2 carried `⟦unverified: 0⟧` around a number whose own claim verified. `rules_only` is
  the configuration whose grounding is 1.0 **by construction**: the template writes the prose and
  declares the claims, so there is nothing for a model to reconstruct and nothing for it to get
  wrong. What broke, and is it one thing?
- **A:** **Two defects, in two modules, and only the first caused this run's failure. The second
  was already there and this run is what made it visible.**

  **Defect one — `written_number`'s twelve-decimal format is a precision ceiling, not a rounding.**
  `f"{value:.12f}".rstrip("0")` on a value below about `5e-13` produces `"0."`, which the function
  then returned as `"0.0"`. On this variant the seeded end-of-month-balance leak makes the
  challenger near-perfect and `challenger.brier` is **3.2264600208103315e-13**, so section 2 read
  *"The value of `challenger.brier` is 0.0"* — prose asserting a value the artifact does not hold,
  in a document whose entire claim is that it does not do that. The declared claim carries the
  artifact's value and the prose token reads zero, so the two cannot pair and the token lands as
  `unattributed`. Note that a **true** zero renders as `"0"`, never `"0.0"`: the two spellings were
  already distinct, which is why the flattened value had no claim to pair with rather than
  silently borrowing one. Fixed by choosing the decimal count from the value's own exponent so
  that :data:`SIGNIFICANT_FIGURES` survive, with twelve decimals kept as a **floor** — every
  number written before this is written identically, and only a value too small for twelve
  decimals gets more of them, which `test_no_number_written_before_this_fix_moves` asserts by
  reimplementing the old function and comparing. The branch that returned `"0.0"` now raises.

  **Defect two — `wrap_unverified` pairs a failed claim to a prose token by value alone.** It took
  the first unused token in the section whose value matched, with no regard for which line the
  claim came from. Section 2 here had one failed claim at `0.0` and eleven verified claims at the
  same value, so the wrapper landed on the first of the eleven: `ablation.burnout.delta_auc`, whose
  claim verified against an artifact of exactly 0.0, was printed as `⟦unverified: 0⟧`. **This
  mispairs whenever a section repeats a value and any claim fails, and it is independent of defect
  one** — it needed only a failed claim and a repeated number, and defect one supplied the failed
  claim. Fixed by locating the claim's own sentence in the prose and preferring a token inside it,
  with the value-only search kept as the fallback for a claim whose line a repair round reworded.
- **Why:** The first is the more serious of the two and it is the project's own thesis turned on
  itself: a report that writes a number the artifact does not support is the failure every other
  mechanism here exists to prevent, and it arrived through the one path that was believed to be
  incapable of it. The fix stays positional rather than reaching for exponent notation — which
  D-099 made safe for the tokenizer — because `written_number`'s contract is what a report reader
  expects to see, and `0.0000000000003226` is ugly and true where `3.226e-13` is compact and
  correct but not what this function is for. The cost is a long string for an absurdly small
  value; no artifact this project computes is near it.
  The second matters less to arithmetic and more to trust: `⟦unverified: …⟧` is the report telling
  its reader which numbers not to rely on, so putting it on a correct sentence while leaving the
  incorrect one bare is worse than not marking anything. It is recorded as its own defect rather
  than as a consequence, because fixing `written_number` alone would have hidden it again.
  **Measured, and this is what bounds the damage.** Across all eighteen variants' artifact
  indices, exactly **one** scalar on **one** variant falls below the old ceiling —
  `challenger.brier` on `msr__L1__eom_balance` at 3.2265e-13. The next-smallest non-zero scalar
  anywhere in the eighteen is **2.93905e-06**, seven orders of magnitude above it. So the other
  seventeen sweep directories under
  `~/code/quaestor-package/phase12-draft/rules-only-sweep/` are unaffected and are **not**
  regenerated; `msr__L1__eom_balance` alone is re-run and replaced, and it comes back at
  **1.0000 / 1.0000 over 318 claims, 318 verified and 0 unattributed**, with its finding set
  `{L1 high, X1 high}` unchanged and no wrapper in its prose. Defect two has **never** been
  observed in a committed artifact: no report under `eval/results/` and not
  `examples/golden_report/report.md` carries a single `⟦unverified: …⟧`, because every committed
  run reached 1.0 post-repair and so never gave the wrapper a claim to place.
  Rejected alternatives. **Declaring the template's claim at the value it wrote rather than at the
  artifact's**, which would have made the run verify by agreeing that the Brier score is zero —
  the matcher's tolerance would have accepted it — and would have published a number that is
  false about the one quantity the seeded defect exists to make extreme. **Rounding to four
  significant figures everywhere**, which changes every number in every committed report and the
  golden with them, for a defect that touches values below 5e-13. **Making `uncovered_numbers`
  positional too**, which is a larger change for a smaller problem: that function answers "is
  there at least as much accounting as there are tokens", which is a count and is deliberately
  position-independent; its only weakness is naming the wrong token in a refusal message, and with
  the wrapper landing correctly its budget balances.

## D-179. What a run costs, measured on three seeded variants, and which terms are the volatile ones

- **Date:** 2026-09-17 (Phase 12 pre-flight, the cut list's step 4, run before commit D so that
  its measurement can set the harness's parameters rather than arrive after them)
- **Q:** The cut list prices the study from two estimates it marks as unmeasured: `plain_llm` at
  about $2.20 a run and `full_agent` at about $5.50. `rules_only` is $0 and measured. What does a
  run actually cost, and on which variants?
- **A:** Three runs, $12.3290 between them, each written outside the repository under
  `~/code/quaestor-package/phase12-draft/pricing/` with its cassettes. `quaestor study run` does
  not exist yet, so a pricing run is one `quaestor validate` on a variant `quaestor study build`
  already wrote:

  ```
  quaestor validate eval/variants/<variant> \
    --synthetic <n> --llm claude-cli --model "claude-opus-5[1m]" \
    --config <plain_llm|full_agent> \
    --out  ~/code/quaestor-package/phase12-draft/pricing/<name> \
    --record-cassettes ~/code/quaestor-package/phase12-draft/pricing/<name>/cassettes
  ```

  `--model` has to be typed: it defaults to `None`, and a run priced against an unnamed model is
  not comparable to the tape layer or to the committed live runs, which are all
  `claude-opus-5[1m]` (D-151). `--out` is outside the repository because `eval/results/` is
  deliberately not gitignored and a pricing run is not a committed study result. There is no
  `--max-cost` on `validate`; that is what commit D adds, and until it exists a pricing run is
  uncapped and wants an operator at the keyboard (D-174).

  | run | variant | calls | cost | wall clock | grounding | findings |
  | --- | --- | ---: | ---: | ---: | ---: | --- |
  | `plain_llm` | `credit__C1__smote_uncalibrated` | 8 | **$1.5622** | 461 s | 0.0000 | 10 |
  | `full_agent` | `credit__C1__smote_uncalibrated` | 20 | **$5.2635** | 1,019 s | 1.0000 | 3 |
  | `full_agent` | `msr__C1__oversampled_hazard` | 17 | **$5.5033** | 1,305 s | 1.0000 | 1 |

  Against the estimates: `plain_llm` **29% under** $2.20, `full_agent` **4% under** $5.50. Both
  `full_agent` runs reached grounding **1.0000 pre- and post-repair** with no repair round, and
  each found exactly what `rules_only` found on the same variant — `{T1 high, C1 medium, E1 low}`
  and `{C1 medium}` — so the agent neither missed the seeded defect nor invented a finding beside
  it. `plain_llm`'s 0.0000 over 106 claims is the arm working as designed (D-072): 10 findings
  across ten defect classes on a package with one seeded defect, none of them citing a computed
  artifact, six of them of the form "no such check was performed".
- **Why:** Two findings that change how the study is budgeted and run, and neither is the headline
  per-run figure.

  **Subject is not the volatile term.** MSR is only **4.6%** dearer per run than credit
  ($5.5033 against $5.2635) — but **23.0%** dearer per *call* and **23.8%** dearer on drafting
  alone ($2.9269 against $2.3644), which is the number that tracks the artifact counts, 371
  against 267. The per-run figures nearly agree because two accidents cancelled: the MSR loop
  stopped after **3** steps where credit used all **4**, and MSR had **no** `structured()` reasks
  where credit had **two**. Quoting the study from per-run costs alone would therefore hide a real
  24% subject effect behind two coincidences.

  **The volatile terms are the loop's step count and the reask rate.** A loop step is about $0.10,
  so 3-against-4 is ±$0.40 a run, and the loop's choices are the model's own and vary run to run —
  `docs/STUDY.md` §8 already says so of its results, and it is true of its cost. A reask is worse:
  credit's two cost **$0.8521**, **16.2% of that run**, because a reask resends the whole prompt
  and is dearer per call than a first draft. That is D-176's artifact priced — the Claude CLI
  subprocess occasionally answers with tool-call text instead of the requested JSON, and each
  occurrence costs a full drafting call. Two in seven drafts here against roughly one in twenty on
  the record sitting. **This is the argument for `--max-cost` being per-chunk rather than
  per-study**: a ceiling set on a 62-run total cannot see a single run doubling its drafting bill,
  and a per-chunk ceiling can stop the sitting that is doing it.

  **The synthetic-to-real ratio, which is what the bridge is priced from.** The synthetic MSR
  `C1` cost **$5.5033**; the committed real-MSR excerpt run, also a `C1`, cost **$6.4858**
  (D-168). Real is **17.9% dearer**, on a panel with more rows and more splits. The two bridge
  runs of the cut list's cut 3 are therefore priced at `$5.5033 x 1.1785 = $6.49` each, **$12.97
  for the pair**, and that is a measured ratio rather than a guess — which is the reason the MSR
  pricing run was chosen to be a `C1` at all: it is the only class with a committed live run on
  the other side of the comparison.

## D-180. The study re-quoted from measured runs: $170, 62 paid runs, and about eleven hours in nineteen sittings

- **Date:** 2026-09-17 (Phase 12 pre-flight, the cut list's step 5, from D-179's three runs)
- **Q:** The cut list's accepted minimum — 18 variants, three configurations, cuts 1, 3 and 4 —
  was costed at **$215–220** and **6–7 h** of model runtime from two unmeasured per-run
  estimates. With those estimates now measured, what is the study's budget, and how many sittings
  is it?
- **A:** **$170.15 for 62 paid runs, and $227.58–230.58 all-in.** Every figure below is either a
  measured cost from D-179 or a stated scaling of one; the only arm still unmeasured is
  `plain_llm` on MSR, scaled by the measured MSR/credit `full_agent` ratio of 1.0456.

  | arm | runs | at | subtotal |
  | --- | ---: | ---: | ---: |
  | `rules_only` x 18 | 18 | $0, measured | **$0** |
  | `plain_llm` x 18 | 11 credit + 7 MSR | $1.5622 / $1.6335 scaled | **$28.62** |
  | `full_agent` x 18 | 11 credit + 7 MSR | $5.2635 / $5.5033 | **$96.42** |
  | 2 variants x 3 repeats | 6 | $5.3568, the 18-variant mean | **$32.14** |
  | 2 real-data bridge runs | 2 | $6.4858, D-179's measured ratio | **$12.97** |
  | **the study** | **62 paid** | | **$170.15** |
  | already spent | | killed sitting $17.1014 + pricing $12.3290 | **$29.43** |
  | the seven stranded tapes | 7 | D-174 | **$28–31** |
  | **all-in** | | | **$227.58–230.58** |

  So the money estimate was good: **$170 against $215–220 quoted**, 21% under, and the whole
  pre-flight-plus-study lands within a few dollars of the cut list's figure once the $29.43
  already spent and the tapes still owed are counted.

  **The runtime estimate was not, and this entry is where it is corrected.** From the measured
  wall clocks — 461 s for `plain_llm` credit, 1,019 s for `full_agent` credit, 1,305 s for
  `full_agent` MSR, 1,373.77 s for the committed real-MSR run — the study is **39,077 s ≈ 10.85 h**
  of model time: 2.56 h for `plain_llm`, 5.65 h for `full_agent`, 1.88 h for the repeats, 0.76 h
  for the bridge. At D-174's measured sitting ceiling of about 35 minutes that is **≈19 chunks**,
  not counting the tape sitting's own three.

  **The cut list's "≈6–7 h" is superseded, and the cut list's own other runtime figure was the
  right one.** Its full-plan line reads "Runtime ≈ 15 h of model time" for 84 runs, which scales
  to **11.07 h** for 62 — within 2% of the measurement. So the 6–7 h in the recommended-minimum
  table disagrees with both the measurement and with the cut list's own arithmetic, and it is the
  outlier rather than the estimate that was merely optimistic.
- **Why:** Recorded as a decision rather than a note because it is what the human commits the
  budget against, and because the two halves fail differently and want different responses. The
  **money** estimate was reliable and can be trusted for the rest of the plan: a per-run cost is
  a function of prompt bytes and call counts, both of which the pre-flight could see in advance.
  The **runtime** estimate was not, and could not have been: it is a function of provider latency
  on 300 KB prompts, which nothing before these three runs had measured. Wall clock is the
  constraint that decides how many sittings a human sits for, so it is the one a plan should be
  built on, and an eleven-hour plan in nineteen chunks is a different object from a six-hour plan.
  **A correction of this session's own figure, recorded because it was stated before it was
  checked.** An ≈18 h runtime and ≈32 chunks were quoted in conversation immediately after the
  third pricing run. That was wrong: it applied `full_agent`'s ~18-minute duration to all 62 runs,
  including the 18 `plain_llm` runs that take 7.7 minutes. The arithmetic above is per arm and is
  the figure that stands. It is written down rather than quietly replaced for the reason D-170's
  own correction is: an estimate that is revised without saying so is indistinguishable from an
  estimate that was always right.
  Rejected alternatives. **Pricing the two unmeasured arms with a fourth and fifth run**
  (`plain_llm` on MSR, and one repeat) for about $2, which buys a quote good to a few per cent
  rather than to ten and is not worth another sitting — the scaling is stated and the arm is 17%
  of the bill. **Quoting from the per-run costs alone** without D-179's per-call decomposition,
  which would carry the 4.6% subject figure into the plan and hide the 24% drafting effect behind
  it. **Keeping the 6–7 h figure** and treating the measurement as pessimistic, which is choosing
  the number that makes the plan look affordable — the same move D-086 rejected when it declined
  to raise a threshold until the data passed.

## D-181. The study runs in chunks, and `--max-cost` is two ceilings rather than one

- **Date:** 2026-09-17 (Phase 12 pre-flight, commit D lean, the cut list's step 6)
- **Q:** `docs/STUDY.md` §4 asks for a `quaestor study run` that is "resumable per (variant,
  configuration)" and for a `--max-cost` that stops a sitting rather than reporting on it. D-174
  measured the sitting at about 35 minutes and D-180 measured the study at ≈10.85 h in ≈19 chunks.
  What does the harness resume *from*, and what exactly does the ceiling check?
- **A:** **A ledger, and two ceilings.**

  **Resumption is `<out>/ledger.json`**, rewritten in full after every cell — to a temporary name
  and then renamed, so a killed chunk leaves a file that parses — and holding, per
  `(variant, configuration)` cell: `status`, `attempts`, `cost_usd`, `calls`, `seconds`,
  `out_dir`, `precision_pre`, `precision_post`, `n_claims`, the finding classes, `checks_failed`
  and `budget_stopped`. A cell whose latest attempt is `done` is skipped by the next chunk;
  anything else is attempted again and its `attempts` counter is what tells the operator a cell is
  failing repeatedly. **The rejected alternative is inferring resumption from a `report.md` on
  disk**, which cannot tell a finished cell from a directory that was half written when the sitting
  was killed — D-174's seventh sitting *was* killed — and which has nowhere to put the cost the
  cell incurred, the figure that prices the next one.

  **`--max-cost` is checked in two places and both are needed.** *Before a cell starts*, its
  estimate is compared with what is left of the ceiling and a cell that does not fit is not
  started; that is what makes a chunk end on a cell boundary instead of stranding a half-paid run,
  and it is how an operator sizes a 35-minute sitting by setting a dollar figure. *Before every
  model call*, the ceiling is checked against what has actually been spent; that is the circuit
  breaker, and it is the one D-179 argues for — a ceiling that can only be read between runs
  cannot see the single run that doubles its drafting bill through a pair of re-asks, measured at
  **16.2%** of a run. The estimate is D-179's measured table (`rules_only` $0; `plain_llm` $1.5622
  credit, $1.6335 MSR scaled; `full_agent` $5.2635 and $5.5033) until the ledger holds a completed
  cell of the same configuration and subject, and that cell's own cost afterwards.

  **The ceiling is per chunk and not per study, by construction**: it counts inside one invocation
  and starts again at the next, which is D-174's "`--max-cost` set from that chunk and not from
  the whole layer" made literal.

  **A completion with no price, under a ceiling, is an error.** `quaestor.llm.base` already says
  why `cost_usd` is `None` rather than `0.0` — "a zero that means 'unknown' turns a cost ceiling
  into a check that always passes" — and `BudgetedLLM` refuses rather than counting the call free.

  **Two exit codes that do not distinguish what a caller needs, and what to read instead.** A
  chunk that stopped on its ceiling exits `0` exactly as one that finished the study does, so a
  driver reads `remaining` in `ledger.json`. And a cell that produced a report without one of its
  checks is `done` with a non-empty `checks_failed`, which is **D-177**'s rule carried from one run
  to a study of them: `quaestor study run` prints those cells and writes them down, and no caller
  of it is entitled to judge a run by the code alone.
- **Why:** The failure this design is against is not a wrong number, it is a lost sitting. Every
  paid arrangement in it — the ledger flush after each cell, the atomic rename, the soft ceiling on
  the cell boundary, the retry of a failed cell — exists so that an interrupted chunk costs at most
  the cell it was in the middle of, and so that the next chunk needs no argument but the same
  command line. Nineteen sittings is nineteen chances to lose the run to a detail.
  Rejected alternatives. **Probatio's `--max-cost`**, which on probatio 0.1.0 sees about half the
  spend and is read at session end, so it reports and does not stop (D-149, amended in Phase 11).
  **A `--max-runs` or `--max-seconds` chunk size** beside the ceiling, which is a second way of
  saying the same thing: at a measured $5.26–5.50 a `full_agent` run, a dollar figure *is* a run
  count and a wall clock, and a second knob is a second thing to set wrong. **Catching every
  exception per cell** so that a chunk always runs to its end, which would go on spending against
  a broken harness; only a `QuaestorError` and the budget stop are caught, the ledger is already
  flushed, and anything else ends the chunk. **A `main()` in `eval/run_study.py`** beside
  `quaestor study run`, which would need a second implementation of `--llm`'s provider construction
  and its rules about which flags combine; `seed.py` has a `main` because it builds no provider.
  **Pooling cassettes across cells**, which the pre-flight already measured as ambiguous, cassette
  keys being a hash of the request: each cell records into a store of its own.

## D-182. What `eval/score.py` refuses to score, and the pairing the free runs left unjudged

- **Date:** 2026-09-17 (Phase 12 pre-flight, commit D lean; developed against the eighteen
  `rules_only` result directories of the cut list's step 3)
- **Q:** `docs/STUDY.md` §5 defines detection, false alarms, collateral judgements and precision,
  and §4 owes §5 two contract clauses. Where does the scorer have to *decline* rather than compute,
  and what did it find on the eighteen free runs?
- **A:** **Three refusals, and one thing a human now owes.**

  **It refuses to score a variant whose seeded class's check did not run.** Since D-177 a
  rule-based check that raises costs its own row and not the run, so a report can be complete but
  for the one check that would have screened for the planted defect; scoring that as a miss
  measures a crash. The variant is set aside, named with the tool and the tool's own message, and
  is in neither the numerator nor the denominator. The clause §4 writes says to read Appendix D's
  "did not run" rows; the scorer reads the **trace's `tool_call` `error` field** instead, which
  D-177 names as one of the three places the fact is written and is the only machine-readable one
  in the run directory — `score.py` opens no prose. A variant whose check crashed *and whose class
  was found anyway* is a detection, not a refusal: there is nothing to decline.

  **It refuses to count false alarms on a control whose baseline is `null`.** D-161 writes `null`
  for "not yet measured", and the two perturbed controls still carry it. Scoring against an
  unmeasured baseline publishes every one of that control's findings as a false alarm, which is
  arithmetic about a missing measurement and not a fact about the detector. A perturbed control is
  scored against **its own** row; a *seeded* variant is scored against the **clean** control's row
  for its subject and mode, because those two ask different questions. Keying baselines by subject
  alone would have lent the clean measurement to the perturbed control and hidden that nobody has
  made it.

  **It refuses to judge a collateral pairing nobody decided in advance.** §5 decided five, from
  D-136's Phase 10 measurements: seeded `S1` → `T1` and seeded `C1` → `T1` are true consequences of
  breaching the package's own declared bound; `msr__L1` → `X1` and credit `L1` → `C1` are true
  consequences of the leak; a collateral `R1` is spurious, which is what D-164's tightened rule is
  for. The scorer holds exactly those five. Anything else is `unjudged`, counted in neither half of
  precision, and printed, because §5 says such a judgement is made at scoring time and recorded in
  §9 with its date. A collateral class that the subject's own clean control raises at the same
  severity is `baseline` rather than either verdict — the same reading of D-161, and the case that
  will arise on the real-MSR bridge runs, whose control baseline is `{C1 medium}`.

  **Measured on the eighteen `rules_only` directories, free and offline: 14/14 seeded variants
  detected**, per class `C1` 2/2, `D1` 1/1, `L1` 3/3, `L2` 2/2, `M1` 1/1, `R1` 1/1, `S1` 2/2, `T1`
  1/1, `X1` 1/1; **0 false alarms** on the two controls whose baselines are measured; **0
  collateral spurious**; **precision 1.0000**; grounding precision 1.0000 mean and minimum, pre-
  and post-repair, which is `rules_only` being trivially grounded and is reported as such. All six
  collateral findings the six pre-decided rules cover fired exactly where §5 says they should.
  **Two controls are not scorable for false alarms** — `control_credit_perturbed` and
  `control_msr_perturbed`, baseline `null` — and that is the pre-flight item those baselines were
  always going to be. **And exactly one pairing came back unjudged: `msr__S1__vintage_shift`
  raising `C1 medium`.** It is not judged in this commit, deliberately: it is a study number, §5
  says it is recorded in §9 with its date, and the mechanism is the same one D-161 measured on the
  real MSR control — a model fitted through 2019 under-predicting the 2020–21 refinancing wave —
  which makes "true consequence" the likely answer and exactly the kind of likely answer that
  should be written down by a person rather than assumed by the scorer that surfaced it.
- **Why:** Each refusal replaces a default that would have put a number nobody decided into a
  published table: a crash scored as a miss, an unmeasured baseline read as an empty one, an
  unforeseen collateral finding called spurious because that is the conservative-looking option.
  The study's whole claim is that its misses are published; a miss that is really a crash, or a
  false alarm that is really an unmeasured control, is a way of being wrong in both directions at
  once. Two columns §5 asks for are absent and their absence is the cut list's rather than an
  oversight — the descriptive open-items column and the cost and latency aggregation, both
  recoverable from the traces and the ledger after the fact.
  Rejected alternatives. **Reading Appendix D** for the failed checks, which makes the scorer a
  reader of prose and would break on a renderer change that moves a table. **Matching evidence
  hashes by equality**, which cannot work: `findings.json` shortens to eight characters and
  `artifacts/index.json` keeps sixteen, so the join is a prefix match, as §4's contract clause
  says. **Scoring `plain_llm`'s unevidenced candidates as misses rather than false alarms**, which
  would make the arm look merely unhelpful instead of wrong; `04` §4 counts each as a false alarm
  and D-072 is the decision it implements. **Judging the `msr__S1` → `C1` pairing here**, which is
  a study judgement made by the session that wrote the scorer, in the commit whose whole point is
  that the scoring rules were fixed before the paid runs.

  **Amended 2026-09-17, same commit, by the human: the `msr__S1` → `C1` pairing is a true
  consequence and is section 5's sixth collateral rule.** The reasoning, recorded in the rule
  itself and not only here: `train_pre_test_post` fits the hazard through 2019 and tests it on the
  2020–21 refinancing wave, so the model really does under-predict prepayment on the tested split
  — and that is the **same mechanism D-161 measured on the real MSR control**, where it is recorded
  as a true finding and not a false alarm. A mechanism cannot be true on a real panel and spurious
  on a synthetic one built to carry it; the data being generated changes what the finding is
  evidence *about*, not whether the model has the defect. The rule is `seeded S1 → raised C1` on
  `msr_prepayment` only, because the credit `S1` recipe shifts a limit-balance segment rather than
  a time window and has no wave to under-predict — `credit__S1` → `C1` stays unjudged, and the
  eighteen free runs do not raise it. Every rule now carries **the date it was decided**: the
  original five read "2026-09-09, D-136, before any variant was run" and this one reads
  "2026-09-17, D-182 amendment, at scoring time", and both appear in `summary.json`, so a reader
  can tell a rule fixed in advance from one written after the numbers were seen without being
  told. That distinction is the reason the entry above declined to make the judgement itself and
  is not weakened by the judgement being made: what section 5 forbids is a scorer quietly deciding,
  not a person deciding on the record. **The eighteen `rules_only` directories now score with
  nothing owed**: 14/14 detected, four controls scored, 0 false alarms, 0 collateral spurious, 0
  unjudged, precision 1.0000, and `eval/score.py` exits 0.

## D-183. `study build --data`, and D-137's dated amendment

- **Date:** 2026-09-17 (Phase 12 pre-flight, commit D lean; amends **D-137** of 2026-09-08)
- **Q:** D-137 said `quaestor study build` offers no `--data` flag, because five of the eighteen
  variants need a column the real sample does not carry and the flag would build packages that
  cannot run. The cut list's accepted plan keeps a two-run real-data bridge, which needs a way to
  apply a recipe to a real data directory. What is the minimum, and what does it do to D-137?
- **A:** **The flag, the pass-through, and four recipes skipped by name.**

  `quaestor study build --data DIR` and `seed(..., data_dir=DIR)` change no byte of any recipe,
  because every recipe hangs off the seam *after* the subject has chosen where its rows come from,
  or only edits `package.yaml`. What `--data` changes is two things. `SEED.yaml` records
  `mode: real`, `data_dir: DIR` and `synthetic_n: null`, so the scorer reads the right control
  baseline for the run it is scoring. And the directory is handed to `load_package`, which
  **verifies the package's declared manifest at build time** — so a data directory that does not
  hold the declared sample is refused in the build, in seconds, rather than at the third hour of a
  paid sitting.

  **D-137 is amended, with this date.** Its answer named five *variants*; they are four *recipes*,
  because both `credit__L1` arms run `add_post_outcome_feature`. `SYNTHETIC_ONLY_RECIPES` names
  them with D-137's own reasons — `add_post_outcome_feature` (a `pay_amt_next` column, and a
  synthetic construction that reads the generating process's latent margin, D-132),
  `end_of_month_balance` (patches `build_panel`, which a `--data` run never calls),
  `regime_sign_flip` (an `application_cohort` column), `reintroduce_collinear` (a `bill_last_adj`
  computed from a raw statement schema `--data` mode never sees) — and under `--data` those rows
  are skipped with their reason rather than built. Ten of the fourteen recipes build in both modes;
  with the four controls that is **thirteen of the eighteen variants** on real data, and the two
  bridge variants are chosen from the nine seeded ones. D-137's recorded fix — an edit to
  `sample.py` and `sample_freddie.py` — is superseded by `docs/STUDY.md` §3's mechanism, a
  transform on the delivered split files, which is testable offline where a sampler edit is not;
  those four transforms are the cut list's cut 3 and are **not** in this commit.
- **Why:** D-137's reasoning was right and its conclusion has an expiry date on it: the flag would
  build packages that cannot run *while the four transforms do not exist*, which is an argument for
  refusing the four rows, not for refusing the flag. Naming them at the point of the build is
  strictly better than D-137's alternative of recording the list in a decision entry, because the
  list is then executable and a test asserts it is the same five variants.
  Rejected alternatives. **Writing the four transforms now**, which is cut 3 and one to two
  engineering sessions, and which the accepted plan removed. **Letting `--data` build all
  eighteen** and discovering the five at validation time, which is exactly the shell-hour D-137
  set out to avoid. **Skipping by variant id** rather than by recipe, which would have to be
  re-derived every time a row is added and which mis-states the fact: it is the recipe that needs
  a column, and both `credit__L1` arms need the same one.

## D-184. The two perturbed controls' synthetic baselines are written into the taxonomy

- **Date:** 2026-09-17 (Phase 12 pre-flight, commit D lean; the human's instruction, from the
  offline measurement of 2026-09-17)
- **Q:** D-161 gives every control a measured baseline per data mode, and the two perturbed
  controls have carried `baseline: null` — "not yet measured" — since it was written.
  `eval/score.py` refuses to score a `null` baseline for false alarms (D-182), so the study's
  false-alarm denominator was two controls and not four. The measurement exists. Is it written in?
- **A:** **Yes, for `synthetic`; `real` stays `null`.** `control_credit_perturbed` =
  `{E1 low}`, identical to `control_credit_clean`'s synthetic baseline down to the artifact hash;
  `control_msr_perturbed` = `{}`, identical to `control_msr_clean`'s finding set. Both `real` cells
  stay `null` and will until a human runs the pair under `--data`, because no test in this
  repository may read the real sample and an unmeasured cell is the honest record of that.
  **Recorded with the credit row and carried in the YAML comment**: on `msr_prepayment` the
  harmless perturbation is *not* value-neutral — the row shuffle moves `challenger.auc`
  0.7337 → 0.7000 and `challenger.delta_auc` −0.0415 → −0.0753. It changes no finding set, which is
  what a baseline records, but a control whose challenger fit moves 3.4 points under a
  perturbation called harmless is a fact the false-alarm arm carries as a note rather than
  discards.
- **Why:** A `null` baseline is not a neutral placeholder in the study's arithmetic: it removes a
  control from the false-alarm denominator, and a false-alarm rate quoted over half the controls
  is a weaker number than one quoted over all of them — quietly, in the direction that flatters
  the detector, because the controls that were dropped are the ones nobody had checked. The
  measurement was made and sat in a draft; the taxonomy is where the scorer reads it.
  That both perturbed baselines equal their clean controls' is the result "harmless perturbation"
  is named for, and it is why `eval/score.py` still keys a control's baseline to the **control**
  and a seeded variant's to the **clean control of its subject**: the two agree today, and keying
  by subject alone would give a silent wrong answer on the day a perturbation stops being harmless.
  Rejected alternatives. **Leaving both `null` and quoting the false-alarm rate over two
  controls**, with a footnote, which publishes a number that a measurement already in hand makes
  better. **Writing a `real` cell from the synthetic one**, which is not a measurement of anything
  — D-161's whole point is that a baseline is measured per data mode, and the real MSR control's
  `{C1 medium}` against its synthetic `{}` is the case that proves the modes differ. **Deriving a
  perturbed baseline from its clean control at scoring time** rather than writing the row, which
  would make "the perturbation is harmless" an assumption of the scorer instead of a measurement
  it can be checked against.
