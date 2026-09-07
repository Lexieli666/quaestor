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
    `1f7df2f39df557dc4b8e39d46e36dbefef4a8f15889c8546b06054c8c8c76c80`

  | date | `MANIFEST.json` `sha256` | reason |
  |---|---|---|
  | 2026-09-07 | `1f7df2f39df557dc4b8e39d46e36dbefef4a8f15889c8546b06054c8c8c76c80` | Phase 1: the golden report set is introduced (the Cowork draft of 2026-09-07, copied byte-for-byte) together with the two schemas written for it |

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
