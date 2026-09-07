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
