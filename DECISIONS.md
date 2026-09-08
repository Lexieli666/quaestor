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
  twelve features (D-045); champion test AUC **0.7753**, Brier 0.0079, calibration slope 0.959;
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
