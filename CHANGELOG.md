# Changelog

All notable changes to Quaestor are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). No number in this file may come from a
run that was not committed.

## [Unreleased]

### Added

- Phase 0 scaffolding: `src/` layout under the distribution name `quaestor-mrm` and the import
  name `quaestor`, the `quaestor` console script as a version stub, the empty subpackages of the
  repository layout, the scaffold tests, the CI quality gate on Python 3.11 and 3.12, and the
  project documents (`README.md`, `PROGRESS.md`, `DECISIONS.md`, `BLOCKERS.md`, `LICENSE`,
  `docs/DESIGN.md`).
- Phase 1 executable specification: `examples/golden_report/` (`report.md`, `claims.json`,
  `findings.json`, `REPORT_SCHEMA.json`, the new `CLAIMS_SCHEMA.json` and `FINDINGS_SCHEMA.json`,
  `MANIFEST.json`, `README.md`), `subjects/credit_default/package.yaml`,
  `data/regulatory/sr11-7-outline.yaml`, `docs/REPORT_SCHEMA.md` and `tests/test_golden_spec.py`.
  Every number in the golden report is illustrative and no citation in it resolves; the directory
  fixes the report's shape, the claim grammar and the citation syntax, and is pinned by
  `MANIFEST.json` and by DECISIONS D-011.
- Phase 2 foundations: `quaestor.errors` (the spec section 3.1 hierarchy plus `LLMProviderError`,
  D-024), `quaestor.hashing` (`stable_hash`, `canonical_json`, `sha256_file`), `quaestor.trace`
  (`TraceWriter`, `TraceReader`, the six event types), `quaestor.findings` (`DefectClass`,
  `Severity`, `FindingCandidate`), `quaestor.package` (`PackageSpec` and its sub-models,
  `load_package`, the pre-run `L1` candidate), `quaestor.artifacts` (`ArtifactStore`, `Artifact`,
  the canonical payload bytes, `index.json`, and the citation parser and resolver of
  `docs/REPORT_SCHEMA.md` section 5) and `quaestor.llm` (`Completion`, the `LLM` protocol,
  `FakeLLM`, `ScriptedLLM`, `AnthropicLLM`, `ClaudeCLILLM`, `structured`). `ClaudeCLILLM`
  runs on the operator's ordinary Claude login: it does not pass `--bare`, which would restrict
  authentication to an API key, and excludes context with an empty working directory and
  `--strict-mcp-config` instead (D-025). The public API of spec
  section 9 is exported as far as Phase 2 implements it; `Finding` arrives in Phase 7 and
  `validate` in Phase 8. No test in the suite calls a live model, downloads data or reads an API
  key.
- Phase 3 sandbox and first subject: `quaestor.sandbox` (`run_model`, `RunResult`, `MemoryCap`,
  `build_argv`, `memory_cap_policy`, and `read_contract`/`required_files`/`features_artifact` for
  the standard artifact contract of spec section 3.3) plus `src/quaestor/sandbox/Dockerfile`, which
  documents the containerised path and is not used by any test; and
  `subjects/credit_default/` (`code/run.py`, `code/features.py`, `code/synthetic.py`,
  `synthetic.py`, `sample.py`, `README.md`). A subject runs in a subprocess whose working tree is a
  copy of the package's `code/`, whose environment is scrubbed to `PATH`, `PYTHONPATH`, `HOME` and
  `QUAESTOR_NO_NETWORK`, whose wall clock is capped from `runtime.max_seconds` and whose address
  space is capped from `runtime.max_memory_mb` on Linux only, with `memory_cap: unenforced`
  recorded everywhere else (D-028). `run.features` is stored as an object carrying its counts, and
  a list element in a citation path may be addressed by its `name` as well as by its `feature`
  (D-026). The synthetic `credit_default` panel is the clean control of D-017: 5,000 clients, an
  event rate of 0.2246, a champion test AUC of 0.7480 and a challenger-minus-champion AUC gap of
  +0.0760 against the 0.03 effective-challenge threshold. `sample.py` needs no `xlrd` (D-027) and
  is never run by a test.
- Phase 4 hazard subject: `subjects/msr_prepayment/` (`package.yaml` copied byte-for-byte from
  the Cowork draft of 2026-09-07, `code/features.py`, `code/synthetic.py`, `code/projection.py`,
  `code/run.py`, `synthetic.py`, `sample_freddie.py`, `README.md`) and its tests
  (`tests/test_subject_msr_prepayment.py`, `tests/test_msr_sample_freddie.py`). The subject builds
  a loan-month panel under one lagging rule with no exceptions — every raw value is a closing
  value of the month it is labelled with, so every feature at month *t* is a function of month
  *t − 1*'s closes and of *t*'s calendar position (D-038) — screens the twelve declared features
  for multicollinearity (D-045), fits a logistic hazard with a hand-written natural cubic spline
  basis on loan age (D-039), and writes `projection.json`: the surviving balance by month and the
  present value of a declared servicing fee under each declared parallel rate shock (D-042). The
  clean synthetic panel is the second control of the study and is expected to yield **no finding
  at all**, the counterpart of D-017: 95,829 loan-months over 2,000 loans, champion test AUC
  0.7753, challenger-minus-champion AUC gap −0.0415, and a value change of −1,297,986 at −300bp
  against +168,055 at +300bp — the negative-convexity sign pattern, which is a property of the
  process rather than a tuned number (D-040, D-047).
- Phase 5 tools: `quaestor.tools` — `ToolRegistry`, `ToolContext`, `ToolResult` and a generic
  `Tool` whose nested pydantic `Args` model is closed (`extra="forbid"`) and whose JSON schema is
  generated once at registration for the planner, the MCP server and the CLI; the effective
  thresholds keyed by the logical artifact names they are stored under; the statistics of spec
  §3.7 written by hand with a longhand test each (PSI with ten quantile bins and a 0.5% floor,
  CSI, KS, Gini, Brier, log loss, the calibration slope and intercept by Newton iterations, VIF,
  Belsley's condition number, CPR, the calibration and decile tables); and eight of the nine tools
  — `run_model`, `profile_data`, `compute_metrics`, `check_leakage`, `check_stability`,
  `check_collinearity`, `challenger_compare` and `run_scenarios` — with a positive and a negative
  test for every candidate rule of the fixed class list. Every tool call writes exactly one
  `tool_call` trace event, and every threshold a rule applied is stored as an artifact whose hash
  is in that rule's evidence. Run through the tools at seed 20260901, the clean synthetic
  `credit_default` raises exactly `{E1 low}` and the clean synthetic `msr_prepayment` exactly `{}`
  (D-053). `retrieve_guidance` is deliberately not registered until its corpus exists in Phase 6.
- Phase 6 regulatory corpus: `quaestor.corpus` — the committed spans of **SR 11-7** (21 sections,
  superseded 2026-04-17) and **SR 26-2** (16 sections, current; the interagency revision the OCC
  issued as Bulletin 2026-13), with `SOURCES.json` recording each document's status, source URL,
  issue date, PDF `sha256`, page count, outline `sha256` and ingest date; `corpus/ingest.py`, a
  dev-time `python -m quaestor.corpus.ingest --sr117 PDF --sr262 PDF [--out DIR]` that is the only
  code in the project importing `pypdf` and is idempotent; `corpus/bm25.py`, BM25 written by hand
  at `k1 = 1.5`, `b = 0.75` with `retrieve(query, k=3, docs=None)` over one document or both; and
  the ninth tool, `retrieve_guidance`, storing `guidance.<query_hash>` and raising no finding
  candidate, which brings the registry to nine. `retrieve_guidance("outcomes analysis")` returns
  SR 26-2 V.1.b, SR 11-7 V.1.c and SR 11-7 V.1, in that order (D-054, D-055). `data/README.md`
  says where the two PDFs come from and why they are not committed.
- Phase 7 findings and the claim verifier: `quaestor.vocab` (`ReportSection`, `Configuration`,
  D-060); `quaestor.findings` gains `Finding`, whose evidence rule is enforced against an
  `ArtifactStore` passed in the pydantic validation context (D-061), `Finding.from_candidates` —
  the only public way to make a finding, which merges candidates of one class, unions their
  evidence and demands a one-sentence reason for a changed severity — `CandidateNotPromoted` and
  `FindingsDocument`, the `findings.json` envelope of `FINDINGS_SCHEMA.json`; and
  `quaestor.verifier` — `Claim` and `VerifiedClaim` field-for-field against `CLAIMS_SCHEMA.json`,
  `extract()` (one `structured()` call plus the deterministic regex pre-pass that owns the
  denominator of grounding precision, D-064), `match_claim`/`match_claims` (citation resolution,
  percent-to-ratio and basis-point normalisation, D-014's per-unit tolerances, `delta` and `ratio`
  over two adjacent citations), `grounding()` per section and per report, `ClaimsDocument` (the
  `claims.json` envelope, with `repairs` left for Phase 8) and `verify_developer_claims`, which
  evaluates `package.yaml` `claims:` only under `--data` and stores each mismatch's comparison as
  `developer_claim.<i>` so its `T1` candidate has evidence (D-016, D-067). `eval/verifier_eval.py`
  ships the offline half of the `04` section 6 component eval over ten committed fixtures written
  for this repository, reporting a perturbation that lands inside tolerance as a tolerance boundary
  rather than as an error.
- Phase 8 the drafter, the repair loop, the renderer, the planner and `validate()`:
  `quaestor.report` — `sections.py` (one brief per report section, the artifact selectors that
  decide what a drafter may cite, the JSON-path flattening that lets `run.model_summary` be cited
  by path, and spec §3.11's rare-event rule that puts calibration before discrimination),
  `drafter.py` (one `structured()` call per section returning `{"markdown": …}`, the rules the
  prompt states and the verifier enforces, and the `rules_only` template that writes the same shape
  with no model call), `repair.py` (at most two re-drafts of a section with the flagged claims
  listed in the verifier's own words, then `⟦unverified: …⟧` around whatever still does not
  verify), `renderer.py` (front matter, the scope block, `[[table:…]]` expansion, section 6's
  recomposition, Appendices A to D and the four refusals) and `schema.py` (the report schema,
  shipped inside the package and pinned byte-for-byte to `examples/golden_report/` by a test,
  D-074); `quaestor.agent.planner` (the rule-based plan of spec §3.12 and the bounded four-step
  follow-up loop, whose refusals — an unknown tool, arguments a closed `Args` rejects, a path
  outside the package — are traced and never executed); `quaestor.configs` (spec §3.13's three
  configurations as data, and the class list each check screens for); and `quaestor.pipeline`
  with **`validate()`**, the pipeline entry of spec §9, which writes `report.md`, `claims.json`,
  `findings.json`, `trace.jsonl` and `artifacts/` (D-070). `validate`, `ValidationRun`,
  `ConfigSpec` and `CONFIGURATIONS` join the public API, completing the surface spec §9 names.
- Phase 9 the command line and the recording layer: `quaestor.cli` — `quaestor validate PKG
  [--data DIR | --synthetic [N]] --llm {fake,anthropic,claude-cli,replay} [--model M] [--config C]
  --out DIR [--timeout S] [--record-cassettes DIR] [--cassettes DIR]`, which runs the pipeline and
  writes the four files and the store; `quaestor tool NAME --pkg PKG --run-dir DIR --args-json
  '{…}'`, which runs one registered check over a run directory and prints its summary, its
  candidates and every artifact it stored; and `quaestor corpus ingest --sr117 PDF --sr262 PDF`.
  Exit codes are `0` for a command that did what it was asked, `1` for one that ran and produced
  nothing, `2` for a request that was wrong before anything ran, and every message on standard
  error names a fixing command (D-082). Bare `--synthetic` takes the subject's documented size
  from `configs.SYNTHETIC_DEFAULT_N` — 5,000 rows for `credit_default`, 2,000 loans for
  `msr_prepayment` — and refuses a package the table does not know (D-081); `--timeout` overrides
  the subject's wall-clock cap rather than the provider's (D-083). `quaestor.llm.OfflineLLM` is
  the provider behind `--llm fake`: the competent offline drafter, extractor, planner and baseline
  that `CLAUDE.md`'s own command line needs, now shipped in the package with the defective
  variants left in `tests/reportsupport.py` as subclasses (D-080). `quaestor.llm.recording` adds
  `RecordingLLM` and `ReplayLLM`, one JSON file per model call named by `stable_hash(system,
  prompt, params)`, so that a live run's calls survive beside its report and can be replayed; a
  call that is not on tape raises and names the missing hash (D-079). `quaestor.corpus.ingest`,
  `quaestor.tools` and the pipeline are unchanged behind them.

### Changed

- **The tolerance a claim is held to is the precision its own prose used** (D-069, amending
  D-014): a claim verifies when the artifact rounds to the value as written, at the decimals the
  sentence wrote, with spec §0's per-unit default as the ceiling the tolerance never exceeds and
  `rounding` an override that can only narrow. `0.74` still verifies against `0.7412`; `0.021` no
  longer verifies against `0.0175` and `22.0%` no longer verifies against `0.2212`. Counts stay
  exact, and trailing zeros before the point run the rule backwards, so `-1130000` is held to ten
  thousand rather than to the unit. `verifier/match.py` gains `written_decimals`,
  `normalisation_scale` and `default_tolerance`; `docs/REPORT_SCHEMA.md` §6 carries the formula.
  The golden report's 92 post-repair claims all still verify and its pre-repair `0.0136` still
  mismatches, while 60 of the 92 record a narrower tolerance than the Phase 1 file; the two
  tolerance boundaries the Phase 7 component eval reported are now caught as the mismatches they
  are, and `eval/verifier_eval.py` reports none.
- `structured()` gains `trace_fields`, merged into every `llm_call` event and never passed to the
  provider, so a draft event can say which section it drafted without handing an adapter an
  argument it has never heard of (D-075).
- `verifier/extract.py` gains `extraction_from` (the pre-pass on its own, for the arm that writes
  its own claims) and `masked_prose` (the exclusion masking, which the repair loop and the renderer
  now share with the pre-pass).
- **The regex pre-pass now defines the eligible numbers in both directions** (D-077). A claim the
  extractor returns for a token the pre-pass excluded — the digits inside a citation's hash or
  logical name, a feature name in inline code, a section number in a heading, a cell of a renderer
  block — is dropped rather than counted, and published in `claims.json` under the exclusion
  pattern `extractor_returned_excluded_token`. Claims are matched to tokens by value, first within
  the line the claim quotes and then, for what is left over, against any unfilled token of the
  section, so a paraphrasing extractor keeps its citations and only a number that is nowhere in the
  eligible prose is dropped. `n_from_model` still counts everything the model returned.
- `ClaudeCLILLM` passes a prompt larger than 64 KiB of UTF-8 on the subprocess's **stdin**, with no
  positional argument after `-p`, because a single argument that long is refused by the operating
  system before the CLI runs (D-078). The threshold is a constructor argument and both paths are
  asserted with the monkeypatched `subprocess.run`.
- `quaestor` with no arguments is now a usage error naming `quaestor --help`, and the version is
  printed by `quaestor --version`: the Phase 0 stub that printed the version and exited zero is
  gone.
- `pyproject.toml`: `types-jsonschema` joins the dev dependencies, because `jsonschema` is now
  imported by `src/quaestor/report/schema.py` and `mypy --strict` has no stubs for it. No runtime
  dependency changes (D-074).
- `[[reg:DOC:SECTION]]` citations resolve. `CitationStatus.deferred` is gone: a regulatory citation
  now resolves against the committed corpus, carrying the section's heading, or dangles with a
  message naming the citation — `[[reg:SR11-7:V.3]]` lists the sections SR 11-7 has, and
  `[[reg:OCC2011-12:V]]` says which two documents the corpus holds (D-055, D-058).
- `quaestor.errors` gains `CorpusError`, the second addition to the closed spec §3.1 hierarchy
  after `LLMProviderError`: the corpus failing to ingest or to load, never a dangling citation
  (D-058).
- **Sanctioned golden edit (D-011).** `examples/golden_report/REPORT_SCHEMA.json`'s regulatory
  citation pattern widens from `(SR11-7|OCC2011-12)` to `(SR11-7|SR26-2)`; `MANIFEST.json` and the
  D-011 pin are regenerated to
  `40a9a75ffbed3cce3d50f226f79f84b0e21873f2326ba6383fb0ac4d6bc73116`, and `docs/REPORT_SCHEMA.md`
  §5 names the same two documents. No other byte of `examples/golden_report/` changes and
  `tests/test_golden_spec.py` is unchanged.
- `data/regulatory/sr11-7-outline.yaml` records that the letter was superseded, and its trailing
  note no longer asks for OCC Bulletin 2011-12 to be ingested (D-055).
- `pyproject.toml`: `mypy` gains an `ignore_missing_imports` override for `sklearn.*`, which ships
  no `py.typed`, and **loses its `python_version = "3.11"` pin** — numpy 2.5 requires Python 3.12
  and writes `type` statements in its stubs, which mypy refuses to parse when told to assume 3.11.
  CI checks both versions and mypy now infers the one it runs under (D-049).
- `ScenariosSpec` gains `servicing_fee_bp`, `discount_rate_annual` and `convexity_expectation`
  (a new `ConvexityExpectation`), all required, and insists that `rate_shocks_bp` include the base
  case. Spec §4.2 requires a declared servicing fee and §3.7's `X1` requires a declared convexity
  expectation; the addition was decided in Cowork on 2026-09-07 before Phase 4 (D-037).
  `tests/fixtures/hazard_package/package.yaml` declares the three new fields.

### Fixed

- `tests/test_package.py::test_a_data_dir_without_a_manifest_verifies_nothing` asserted on
  `credit_default`, which gained a `data.manifest` when its real sample was committed, so the test
  had been failing on `main`; it now uses the hazard fixture, which is the package that declares
  no manifest.
