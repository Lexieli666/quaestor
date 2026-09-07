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

### Changed

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
