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
