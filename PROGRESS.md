# PROGRESS.md — Quaestor

The run's only durable memory. A fresh session reads this file first, immediately after
`CLAUDE.md`. One phase per session; the checkbox and the run-log line for phase N are committed
with phase N's code (`git show --stat HEAD | grep PROGRESS.md`).

## Phases

Scope lines are taken from `02-SPEC.md` section 11; the spec sections each phase implements from
are named in brackets.

- [x] **Phase 0** — Scaffolding, CI, name check, dev deps incl. `probatio-llm` (spec §2)
- [x] **Phase 1** — Golden report, claim grammar, report schema, synthetic `package.yaml`
  (spec §7, §3.2, §3.10–3.11)
- [x] **Phase 2** — Foundations, package loader, artifact store, LLM layer, trace (spec §3.1–3.5)
- [x] **Phase 3** — Sandbox `run_model` + `credit_default` subject (synthetic first, then
  `sample.py`) (spec §3.6, §4.1)
  - clean synthetic `credit_default` must yield exactly {E1 low} (D-017) — asserted at **data**
    level in Phase 3 (challenger − champion AUC +0.0760 > 0.03; every `package.yaml` threshold
    passed; the screen resolves both collinear pairs); the pipeline-level assertion of exactly
    {E1 low} needs the tools, the findings and the report, so it stays with Phase 8
- [x] **Phase 4** — `msr_prepayment` subject incl. projection (spec §4.2)
  - clean synthetic `msr_prepayment` must yield exactly {} — no finding at all, the counterpart of
    D-017 (D-047) — asserted at **data** level in Phase 4 (challenger − champion AUC −0.0415;
    every `package.yaml` threshold passed; the projection's negative-convexity sign pattern
    holds); the pipeline-level assertion of exactly {} needs the tools, the findings and the
    report, so it stays with Phase 8, and it depends on D-046's reading of the `psi` threshold
- [x] **Phase 5** — Tools, registry, statistics by hand (spec §3.7)
  - eight of spec §3.7's nine tools are registered; **`retrieve_guidance` is not**, because it
    needs the corpus and the BM25 index of Phase 6, and a stub that returned no spans would look
    to a planner like guidance that had been retrieved
  - clean synthetic `credit_default` raises exactly {E1 low} and clean synthetic
    `msr_prepayment` exactly {} **at tool level** (D-053); the pipeline-level assertion, over
    findings and a rendered report, stays with Phase 8
- [x] **Phase 6** — Corpus ingest + BM25 + guidance citations (spec §3.8)
  - the acceptance criterion's `retrieve_guidance("outcomes analysis")` must return `V.1.c`, not
    the `V.3` spec §3.7 names: the verified outline wins over the spec's sentence (D-054)
  - the corpus holds **two** documents, `SR11-7` (superseded 2026-04-17, kept so historical
    citations resolve) and `SR26-2` (current, the drafter's default from Phase 8); OCC Bulletin
    2011-12 is **not** ingested, and spec §3.8's `occ-2011-12.jsonl` is therefore never written
    (D-055)
- [x] **Phase 7** — Findings + claim verifier (spec §3.9–3.10)
  - the extractor's regex pre-pass is the denominator of grounding precision: a model that omits a
    number cannot lower it, and a silent extractor scores extraction recall 0.0 rather than
    precision 1.0 over nothing (D-064)
  - the evidence rule binds **construction**; reading a written `findings.json` back waives it
    deliberately and by name, because `eval/score.py` scores a run from the file alone (D-061)
- [x] **Phase 8** — Drafter, repair, renderer, planner, configs; end-to-end on synthetic with
  `FakeLLM` (spec §3.11–3.13)
  - clean synthetic `credit_default` must yield exactly {E1 low} (D-017)
  - clean synthetic `msr_prepayment` must yield exactly {} at pipeline level (D-047), which
    depends on D-046 (the `psi` threshold and `S1` are read train-against-test; the out-of-time
    and vintage comparisons are reported, not tested) and, for `R1`, on seed 20260901
  - the tolerance rule is amended before the drafter is built: a claim verifies when the artifact
    **rounds to the value as written at the precision the prose used**, with spec §0's defaults as
    a ceiling and `rounding` narrowing only (D-069, amending D-014)
- [x] **Phase 9** — CLI; first live validations of both real subjects (Claude CLI); reports
  committed (spec §3.14)
  - the **CLI half is done**: `validate`, `tool` and `corpus ingest` exist, `study`,
    `verifier-eval` and `mcp` are refused as unknown commands until their own phases (D-082), and
    `CLAUDE.md`'s `quaestor validate ... --synthetic --llm fake` line runs on both subjects, which
    is gate condition **5b**, applicable for the first time since Phase 1
  - the **live half is the operator's**, and is outstanding: the two `--llm claude-cli` runs of
    `03-RUNBOOK.md` §3 need real data and a live model, which `CLAUDE.md` forbids this session from
    reaching, so `eval/results/first-live/` does not exist and no report is committed. The
    recording layer those runs need is here and tested (`--record-cassettes`, `--llm replay`)
- [ ] **Phase 10** — Taxonomy and seeded-defect generator (spec §5, `04` §2)
- [ ] **Phase 11** — Probatio test layer with recorded cassettes and judge validation (spec §6)
- [ ] **Phase 12** — The study: build variants, run three configurations live, score, publish
  (`04` §3–5)
- [ ] **Phase 13** — Verifier component eval on FinQA / TAT-QA (`04` §6)
- [ ] **Phase 14** — Human anchor: the manual validation vs the copilot's (`04` §7)
- [ ] **Phase 15** — MCP server + Claude Desktop demo (spec §3.15)
- [ ] **Phase 16** — Prior art, docs, README, publish, resume bullets (spec §10, `05`)

## Run log

One line per phase, appended in the phase's own commit: date, phase, gate result, notes.

- 2026-09-06 — **Phase 0** — gate green on the four conditions that apply: `pytest -q` 18 passed,
  0 failed, 0 skipped, 0 xfailed; coverage of `src/quaestor` 100% (`coverage run -m pytest`, 10
  statements); `ruff check` and `ruff format --check` clean on `src tests eval subjects`;
  `mypy --strict src/quaestor` clean (11 source files). Gate condition 5 is **not applicable**:
  `examples/golden_report/` is created in Phase 1 and there is no subject to run
  `quaestor validate --synthetic --llm fake` against until Phase 3, so the `quaestor validate` line
  of CLAUDE.md's command list was not run — the CLI is a stub that prints the version. Gate
  condition 6 is **not applicable**: `tests/probatio/` arrives in Phase 11; the CI step is present
  and guarded on the directory's existence (DECISIONS D-007). Shipped `pyproject.toml`
  (hatchling, `src/` layout, distribution `quaestor-mrm`, import `quaestor`, version 0.1.0.dev0),
  `src/quaestor/__init__.py`, `src/quaestor/cli.py` (version stub), `py.typed`, the nine empty
  subpackages of the CLAUDE.md layout each with a docstring naming its phase,
  `tests/test_scaffold.py`, `.github/workflows/ci.yml` with all six gate conditions as steps,
  `.gitignore`, `README.md`, `LICENSE`, `PROGRESS.md`, `DECISIONS.md` (D-001 to D-010),
  `BLOCKERS.md`, `CHANGELOG.md` and `docs/DESIGN.md`. PyPI name check: `quaestor` is taken by an
  unrelated project (0.6.3, 2025-08-07, per the Phase 0 prompt), so the distribution is
  `quaestor-mrm` (DECISIONS D-002). Local interpreter is Python 3.13.5; CI covers 3.11 and 3.12
  (DECISIONS D-009). No push; CI has not run yet.
- 2026-09-07 — **Phase 0 follow-up** — virtualenv rebuilt on Python 3.12.14 (D-009 amended);
  `pytest -q` 18 passed, `ruff` and `mypy --strict` clean on 3.12 locally; `pip index versions
  quaestor` confirmed `quaestor` taken (0.6.3) and `quaestor-mrm` free (no distribution); first
  push to `Lexieli666/quaestor`; CI run 34085866073 green on 3.11 and 3.12.
- 2026-09-07 — **Phase 1** — gate green on the five conditions that apply: `pytest -q` 31 passed,
  0 failed, 0 skipped, 0 xfailed (18 scaffold + the 13 checks of `tests/test_golden_spec.py`);
  coverage of `src/quaestor` 100% (`coverage run -m pytest`, 10 statements — Phase 1 ships no
  `src/` code, per the runbook); `ruff check` and `ruff format --check` clean on
  `src tests eval subjects`; `mypy --strict src/quaestor` clean. Gate condition 5 splits: **5a
  applies and is `tests/test_golden_spec.py`** — the golden set is pinned by
  `examples/golden_report/MANIFEST.json` and by the `MANIFEST.json` `sha256` in DECISIONS D-011
  (`1f7df2f39df557dc4b8e39d46e36dbefef4a8f15889c8546b06054c8c8c76c80`), so a byte change to any of
  the six specification files fails the suite; **5b is still not applicable**, since there is no
  runnable subject until Phase 3 and the `quaestor validate --synthetic --llm fake` line of
  `CLAUDE.md`'s command list was therefore not run (the CLI is still the Phase 0 version stub).
  Gate condition 6 is **not applicable**: `tests/probatio/` arrives in Phase 11 (DECISIONS D-007).
  Shipped `examples/golden_report/` — `report.md`, `claims.json`, `findings.json` and
  `REPORT_SCHEMA.json` copied byte-for-byte from the Cowork draft of 2026-09-07, plus
  `CLAIMS_SCHEMA.json`, `FINDINGS_SCHEMA.json`, `MANIFEST.json` and `README.md` written here —
  `subjects/credit_default/package.yaml`, `data/regulatory/sr11-7-outline.yaml` (Phase 6 ingests
  from it), `docs/REPORT_SCHEMA.md`, the Phase 1 section of `docs/DESIGN.md`,
  `tests/test_golden_spec.py` and DECISIONS D-011 to D-018. The two `.gitkeep` placeholders of
  `examples/golden_report/` and `subjects/credit_default/` are deleted;
  `subjects/credit_default/code/.gitkeep` stays for Phase 3. Every number in the golden report is
  illustrative (`illustrative: true`) and every artifact hash in it is `sha256(logical_name)[:8]`,
  which resolves to nothing: the directory fixes shape and is never quoted as a result. No push.
- 2026-09-07 — **Phase 2** — gate green on the four conditions that apply plus 5a: `pytest -q` 311
  passed, 0 failed, 0 skipped, 0 xfailed; coverage of `src/quaestor` **100%** (`coverage run -m
  pytest`, 1061 statements) against the 85% floor; `ruff check` and `ruff format --check` clean on
  `src tests eval subjects`; `mypy --strict src/quaestor` clean (24 source files). Gate condition
  **5a applies and passes** — `tests/test_golden_spec.py` (13 checks) still pins
  `examples/golden_report/`, which this phase did not touch; **5b is still not applicable**, since
  the first runnable subject arrives in Phase 3 and the `quaestor validate --synthetic --llm fake`
  line of `CLAUDE.md`'s command list was therefore not run (the CLI is still the Phase 0 version
  stub). Gate condition 6 is **not applicable**: `tests/probatio/` arrives in Phase 11 (D-007).
  Shipped `src/quaestor/errors.py` (the spec §3.1 hierarchy plus `LLMProviderError`, D-024),
  `hashing.py` (`stable_hash`, `canonical_json`, `sha256_file`; cross-process stability proved by a
  `python -c` subprocess), `trace.py` (`TraceWriter`, `TraceReader`, the six event types, envelope
  plus flattened payload, D-020), `findings.py` (`DefectClass`, `Severity`, `FindingCandidate` with
  the `load_package` evidence exemption, D-021), `package/{spec,loader}.py` (`PackageSpec` and its
  sub-models with `extra="forbid"`, `Feature.note` per D-017, `load_package`, manifest verification
  under `--data` only per D-022, the pre-run `L1` candidate), `artifacts/{store,citations}.py`
  (content-addressed store whose address includes the logical name per D-023, canonical `%.10g`
  payload bytes, `index.json`, and the five citation forms of `docs/REPORT_SCHEMA.md` §5 including
  table cells, JSON paths, list elements by `feature`, adjacent delta pairs, deferred `[[reg:...]]`
  and `[[table:...]]`), `llm/{base,fake,anthropic,claude_cli,structured}.py`, the public API of spec
  §9 as far as it exists, eight test modules (293 new tests), `tests/fixtures/hazard_package/`
  and `tests/fixtures/claude_cli_payload.json`. **`ClaudeCLILLM` does not pass `--bare`**: it would
  restrict authentication to an API key, which `CLAUDE.md` forbids and the operator does not have,
  so context is excluded by an empty temporary working directory and `--strict-mcp-config` instead,
  and `quaestor_bare` on every `llm_call` event records which regime a run used (D-025, corrected
  after Cowork review). No test calls a live model, downloads data, trains on real data or reads an
  API key; `anthropic` is deliberately absent from the dev environment and its lazy import is
  covered with a stub module. No push.
- 2026-09-07 — **Phase 3** — gate green on the four conditions that apply plus 5a: `pytest -q` 441
  passed, 0 failed, 0 skipped, 0 xfailed (130 new); coverage of `src/quaestor` **100%**
  (`coverage run -m pytest`, 1442 statements) against the 85% floor; `ruff check` and `ruff format
  --check` clean on `src tests eval subjects`; `mypy --strict src/quaestor` clean (26 source
  files). Gate condition **5a applies and passes** — `tests/test_golden_spec.py` still pins
  `examples/golden_report/`, which this phase did not touch, and the golden's `run.features#n`,
  `run.features#at_origination`, `run.model_summary#removed.bill_last.vif` and
  `run.metrics#test.auc` citations now resolve against a real run's store (D-026); **5b is still
  not applicable**, since `quaestor validate` arrives in Phase 9 and the CLI is still the Phase 0
  version stub — the `quaestor validate --synthetic --llm fake` line of `CLAUDE.md`'s command list
  was therefore not run, and `run_model` was exercised directly instead. Gate condition 6 is **not
  applicable**: `tests/probatio/` arrives in Phase 11 (D-007). Shipped
  `src/quaestor/sandbox/{runner,contract}.py` and `src/quaestor/sandbox/Dockerfile` (documented,
  never built by a test), and `subjects/credit_default/{code/run.py,code/features.py,
  code/synthetic.py,synthetic.py,sample.py,README.md}`; `tests/{conftest,test_sandbox,
  test_contract,test_subject_credit_default,test_credit_sample}.py`; DECISIONS D-026 to D-036; the
  Phase 3 section of `docs/DESIGN.md`. **Measured on the synthetic subject, seed 20260901,
  `--synthetic 5000`, through `run_model` on this machine (Python 3.12.14, scikit-learn 1.9.0):
  wall-clock 1.61 s on a cold store and 1.19 s and 1.20 s on two repeats, of which the subprocess
  itself was 1.57 s, 1.15 s and 1.16 s — against the 60 s budget; event rate 0.2246; ten of twelve
  features retained (`bill_last` at VIF 160.9 and then `utilisation_mean_6m` at 36.4 removed, worst
  retained VIF 7.30); champion test AUC 0.7480, Brier 0.1489, calibration slope 0.997; challenger
  (`HistGradientBoostingClassifier`, defaults, seed 20260901) test AUC 0.8240, so the
  challenger-minus-champion gap is +0.0760 against the `E1` threshold of 0.03 (D-036).** Two runs
  of one seed are byte-identical. `memory_cap` is `unenforced` on this machine and on every
  non-Linux platform, recorded on the result, on `run.status`, in the trace and in Appendix C, and
  never a reason to fail a run (D-028); the `enforced` branch is exercised only by CI, which is
  the one code path of this phase no local run covers. No test calls a live model, downloads data,
  trains on real data or reads an API key; `sample.py` is covered for argument handling and the UCI
  column map only, on a three-row frame the test writes itself. No push.
- 2026-09-07 — **Phase 3 follow-up (commit `524c169`)** — `data(credit_default)`: first real-sample
  run. Shipped `subjects/credit_default/artifacts/real/{splits,features,metrics,model_summary}.json`
  (aggregates and coefficients only, no rows), the `data.manifest` sha256 digests and the developer
  `claims:` in `subjects/credit_default/package.yaml`, and the provenance section of the subject's
  `README.md`. **The commit turned CI red on one fixture test**: `tests/test_package.py::
  test_a_data_dir_without_a_manifest_verifies_nothing` had borrowed the shipped `credit_default`
  package, which now declares a manifest, so the assertion it made was no longer true of its
  fixture; the repair — pointing the test at `tests/fixtures/hazard_package/`, which declares no
  manifest — shipped inside `a0e5b27` (Phase 4). Phases 4 and 5 both omitted this line; it is
  written here in Phase 6's commit, out of order, rather than left unrecorded.
- 2026-09-07 — **Phase 4** — gate green on the four conditions that apply plus 5a: `pytest -q` 534
  passed, 0 failed, 0 skipped, 0 xfailed (93 new); coverage of `src/quaestor` **100%**
  (`coverage run -m pytest`, 1453 statements) against the 85% floor; `ruff check` and `ruff format
  --check` clean on `src tests eval subjects`; `mypy --strict src/quaestor` clean (26 source
  files). Gate condition **5a applies and passes** — `tests/test_golden_spec.py` (13 checks) still
  pins `examples/golden_report/`, which this phase did not touch; **5b is still not applicable**,
  since `quaestor validate` arrives in Phase 9 and the CLI is still the Phase 0 version stub — the
  `quaestor validate --synthetic --llm fake` line of `CLAUDE.md`'s command list was therefore not
  run, and `run_model` was exercised directly on both subjects instead. Gate condition 6 is **not
  applicable**: `tests/probatio/` arrives in Phase 11 (D-007). Shipped
  `subjects/msr_prepayment/{package.yaml,README.md,synthetic.py,sample_freddie.py,
  code/features.py,code/synthetic.py,code/projection.py,code/run.py}`,
  `tests/{test_subject_msr_prepayment,test_msr_sample_freddie}.py`, the four new `msr_*` fixtures
  in `tests/conftest.py`, the `ScenariosSpec` addition of D-037 in `src/quaestor/package/spec.py`
  with `ConvexityExpectation` exported, the three new lines in
  `tests/fixtures/hazard_package/package.yaml`, DECISIONS D-037 to D-048 and the Phase 4 section
  of `docs/DESIGN.md`. `package.yaml` is byte-identical to `quaestor-package/phase4-draft/
  package.yaml`; both `.gitkeep` placeholders of `subjects/msr_prepayment/` are deleted.
  **Measured on the synthetic subject, seed 20260901, `--synthetic 2000`, through `run_model` on
  this machine (Python 3.12.14, scikit-learn 1.9.0): wall-clock 3.13 s, 3.09 s and 3.16 s over
  three runs, of which the subprocess itself was 2.37 s, 2.36 s and 2.40 s — against the 60 s
  budget; 95,829 loan-months over 2,000 loans in three cohorts; observed monthly payoff rate
  0.0084 against the 0.0105 the intercept is solved for on the uncensored schedule; splits 36,013
  / 15,382 / 12,257 / 32,177 loan-months; ten of twelve features retained (`rate_change_12m` at
  VIF 12.4 and then `bom_balance_log` at 40,090 removed, worst retained VIF 4.98, Belsley kappa
  4.94); champion test AUC 0.7753, Brier 0.007894, calibration slope 0.959, train 0.7883,
  out-of-time 0.7846, vintage holdout 0.7718; challenger (`HistGradientBoostingClassifier`,
  defaults, seed 20260901) test AUC 0.7337, so the challenger-minus-champion gap is **−0.0415**
  against the `E1` threshold of +0.03 — the opposite sign to the credit subject, by design;
  projection over 511 loans and 96.6 million of balance as of 2024-01, value change **−1,297,986**
  at −300bp and **+168,055** at +300bp, monotone across all seven shocks, convexity −1,129,932
  (D-047).** Two runs of one seed are byte-identical. `memory_cap` is `unenforced` on this machine
  (D-028). One pre-existing failure on `main` was repaired:
  `test_a_data_dir_without_a_manifest_verifies_nothing` asserted on `credit_default`, which gained
  a `data.manifest` in the Phase 3 real-sample commit, so it now uses the hazard fixture. No test
  calls a live model, downloads data, trains on real data or reads an API key; `sample_freddie.py`
  is covered for argument handling, the FRED month-close convention, the stratified draw and the
  Freddie Mac column map only, on three-loan pipe-delimited frames the tests write themselves. No
  push.
- 2026-09-07 — **Phase 5** — gate green on the four conditions that apply plus 5a: `pytest -q` 695
  passed, 0 failed, 0 skipped, 0 xfailed (161 new); coverage of `src/quaestor` **100%**
  (`coverage run -m pytest`, 2696 statements) against the 85% floor; `ruff check` and `ruff format
  --check` clean on `src tests eval subjects`; `mypy --strict src/quaestor` clean (38 source
  files). Gate condition **5a applies and passes** — `tests/test_golden_spec.py` still pins
  `examples/golden_report/`, which this phase did not touch, and `tests/test_tools_clean.py` now
  asserts that **every logical name in the golden report's Appendix B other than `guidance.*`
  resolves in a real run's store**; **5b is still not applicable**, since `quaestor validate`
  arrives in Phase 9 and the CLI is still the Phase 0 version stub — the `quaestor validate
  --synthetic --llm fake` line of `CLAUDE.md`'s command list was therefore not run, and the eight
  tools were driven through `ToolRegistry.call` instead. Gate condition 6 is **not applicable**:
  `tests/probatio/` arrives in Phase 11 (D-007). Shipped `src/quaestor/tools/` — `registry.py`
  (`ToolRegistry`, `ToolContext`, `ToolResult`, the generic `Tool` with its nested `Args`, one
  `tool_call` trace event per call), `thresholds.py` (every spec §3.7 number keyed by the logical
  name it is stored under), `stats.py` (PSI, CSI, KS, Gini, Brier, log loss, the calibration slope
  and intercept by hand-written Newton iterations, VIF, Belsley's kappa, CPR, the calibration and
  decile tables), `frames.py` (the one place a tool reads the spec §3.3 contract) and the eight
  tools `run.py`, `profiler.py`, `metrics.py`, `leakage.py`, `stability.py`, `collinearity.py`,
  `challenger.py`, `scenarios.py`; `tests/{test_stats,test_tool_registry,test_tool_rules,
  test_tool_frames,test_tools_clean}.py` and `tests/toolsupport.py`; the two clean-run fixtures in
  `tests/conftest.py`; DECISIONS D-049 to D-054 and the consequence paragraph added to D-046; the
  Phase 5 section of `docs/DESIGN.md`. `pyproject.toml` gains a `mypy` override for `sklearn.*`
  (no `py.typed`) and **loses its `python_version = "3.11"` pin**, which numpy 2.5's stubs — 3.12
  syntax, on a distribution that requires 3.12 — make unparsable on a 3.12 machine; CI still checks
  both versions (D-049). **Measured through the tools at seed 20260901 on this machine (Python
  3.12.14, scikit-learn 1.9.0, numpy 2.5.3, pandas 3.0.5): `credit_default --synthetic 5000`, eight
  tool calls in 2.60 s over 130 artifacts, raising exactly `{E1 low}` — challenger 0.8240 against
  the champion's 0.7480, a lead of +0.0760 against 0.03; every other rule clear, the closest being
  the worst retained VIF at 7.295 against 10. `msr_prepayment --synthetic 2000`, eight tool calls
  in 4.39 s over 220 artifacts, raising exactly `{}` — the closest calls being the vintage
  holdout's calibration slope at 0.8373 against a floor of 0.80 and its mean-to-observed gap at
  17.2% against 25%. `O1`'s second rule was measured as spec §3.7 writes it and not adjusted: the
  out-of-time AUC of 0.7846 is *above* test's 0.7753 and the vintage holdout's 0.7718 is below it
  by 0.0035 against a threshold of 0.05 (D-053).** Two scoping decisions are Phase 5's own, both
  taken before those numbers were read: `C1` is applied to every split computed, and `R1` compares
  per-regime refits while reading the AUC half of its rule from the champion's own scores. PSI's
  bins are closed at the top so that a mass point does not split across the boundary, which moves
  the clean panels' indices in the fourth decimal and the reported-not-tested out-of-time
  comparison from D-046's 3.09 to 2.945 (D-051). `retrieve_guidance` is deliberately unregistered
  until Phase 6. No test calls a live model, downloads data, trains on real data or reads an API
  key. No push.
- 2026-09-07 — **Phase 6** — gate green on the four conditions that apply plus 5a: `pytest -q` 769
  passed, 0 failed, 0 skipped, 0 xfailed (74 new); coverage of `src/quaestor` **100%**
  (`coverage run -m pytest`, 3034 statements) against the 85% floor; `ruff check` and `ruff format
  --check` clean on `src tests eval subjects`; `mypy --strict src/quaestor` clean (42 source
  files). Gate condition **5a applies and passes** — `tests/test_golden_spec.py` (13 checks,
  **unchanged**) still pins `examples/golden_report/`, which this phase edited **once, under
  D-011's procedure**: the D-011 table row and the new pin were written first, then
  `REPORT_SCHEMA.json`'s `x-quaestor-citation-patterns.regulatory` widened from
  `(SR11-7|OCC2011-12)` to `(SR11-7|SR26-2)`, `MANIFEST.json` was regenerated to sha256
  **`40a9a75ffbed3cce3d50f226f79f84b0e21873f2326ba6383fb0ac4d6bc73116`**, and
  `docs/REPORT_SCHEMA.md` §5's document list was updated. No other byte of the directory changed.
  **5b belongs to Phase 9**, where `quaestor validate` arrives — the CLI is still the Phase 0
  version stub, so the `quaestor validate --synthetic --llm fake` line of `CLAUDE.md`'s command
  list was not run, and the corpus, the retriever and `retrieve_guidance` were exercised directly
  and through `ToolRegistry.call` instead. **Gate condition 6 belongs to Phase 11**, where
  `tests/probatio/` arrives (D-007). Shipped `src/quaestor/corpus/{documents,bm25,ingest}.py`, the
  committed corpus `src/quaestor/corpus/{sr11-7.jsonl,sr26-2.jsonl,SOURCES.json}`,
  `src/quaestor/tools/guidance.py`, `data/regulatory/sr26-2-outline.yaml`, `data/README.md`,
  `tests/{test_corpus,test_bm25,test_tool_guidance}.py`, DECISIONS D-055 to D-059 with the new
  D-011 row, and the Phase 6 section of `docs/DESIGN.md`. `quaestor.errors` gains `CorpusError`
  (D-058) and `CitationStatus.deferred` is **gone**: a `[[reg:...]]` citation now resolves against
  the corpus or dangles. **Reality first (D-055): SR 11-7 was superseded on 2026-04-17 by SR 26-2**
  (Federal Reserve, interagency with the OCC and the FDIC; the OCC issued the identical text as
  Bulletin 2026-13, rescinding OCC 2011-12), so the corpus holds `SR11-7` **and** `SR26-2`, and
  **OCC 2011-12 is deliberately not ingested**. **The ingest was run once in this session** on
  `~/code/data-raw/regulatory/{sr1107a1,sr2602a1}.pdf`, which are not committed: **SR 11-7, 21
  pages → 21 sections**, pdf sha256 `0046c0e4…`; **SR 26-2, 12 pages → 16 sections**, pdf sha256
  `209ce4c1…`. **Every heading of both outlines matched the PDF text in document order, so no
  outline was changed**; two SR 26-2 sections (`IV`, `V.1`) are pure container headings and are
  ingested with an empty body. `retrieve_guidance("outcomes analysis")` returns, in order,
  **SR26-2 V.1.b (4.5018), SR11-7 V.1.c (4.2604) and SR11-7 V.1 (3.3853)** — the acceptance
  criterion of spec §3.7 as D-054 corrects it. BM25 is by hand at `k1 = 1.5`, `b = 0.75` with the
  `+1` idf smoothing (D-057), checked longhand against a three-document toy corpus. The registry
  now holds **nine** tools. No test reads a PDF, calls a live model, downloads data, trains on real
  data or reads an API key. No push.
- 2026-09-07 — **Phase 7** — gate green on the four conditions that apply plus 5a: `pytest -q` 871
  passed, 0 failed, 0 skipped, 0 xfailed (102 new); coverage of `src/quaestor` **100%**
  (`coverage run -m pytest`, 3726 statements) against the 85% floor; `ruff check` and `ruff format
  --check` clean on `src tests eval subjects`; `mypy --strict src/quaestor` clean (49 source
  files). Gate condition **5a applies and passes** — `tests/test_golden_spec.py` (13 checks) still
  pins `examples/golden_report/`, which this phase **did not touch**: no byte of the directory
  changed and no new D-011 row was needed. **5b belongs to Phase 9**, where `quaestor validate`
  arrives — the CLI is still the Phase 0 version stub, so the `quaestor validate --synthetic --llm
  fake` line of `CLAUDE.md`'s command list was not run, and the verifier was exercised directly and
  through `eval/verifier_eval.py` instead. **Gate condition 6 belongs to Phase 11**, where
  `tests/probatio/` arrives (D-007). Shipped `src/quaestor/vocab.py` (`ReportSection`,
  `Configuration`), the second half of `src/quaestor/findings.py` (`Finding`,
  `Finding.from_candidates`, `CandidateNotPromoted`, `FindingsDocument`), `src/quaestor/verifier/`
  (`claim.py`, `extract.py`, `match.py`, `grounding.py`, `claims_doc.py`, `developer.py`),
  `eval/verifier_eval.py`, the ten fixtures under `tests/fixtures/verifier_eval/`,
  `tests/verifiersupport.py` and eight test modules
  (`test_findings_document`, `test_verifier_claims`, `test_verifier_extract`, `test_verifier_match`,
  `test_verifier_grounding`, `test_verifier_developer`, `test_verifier_golden`,
  `test_verifier_eval_fixtures`), DECISIONS D-060 to D-068 and the Phase 7 section of
  `docs/DESIGN.md`. `tests/test_scaffold.py`'s module list and public-API list were updated for the
  seven new modules and for `Finding`, `Claim`, `ClaimStatus`, `VerifiedClaim`, `ClaimsDocument`,
  `FindingsDocument`, `Configuration` and `ReportSection`; `validate` is still asserted absent.
  **Measured on the Phase 1 golden report: all 92 post-repair claims re-match as `verified`
  against a store rebuilt from Appendix B, with every `artifact_value` and every `tolerance` equal
  to the golden's own, and the pre-pass reproduces the golden's claim set section by section —
  13 / 14 / 13 / 39 / 4 / 4 / 5 = 92 tokens, none extra and none missing.** That one test matches
  on the **logical name and path, not on the hash**: the golden's hashes are
  `sha256(logical_name)[:8]` and cannot agree with a content address computed today, and the two
  table artifacts and the five JSON artifacts are rebuilt from the report's renderer blocks and
  prose rather than from Appendix B, which prints no value for them (D-068). **The offline verifier
  component eval (`04` §6) over the ten committed fixtures at seed 20260901 returns status accuracy
  1.0 on all three expected classes and extraction recall 1.0, with the per-item statuses:
  vq01 relative_down verified/mismatch/unsupported; vq02 percent_ratio_confusion
  verified/mismatch/unsupported; vq03 relative_down verified/mismatch/unsupported; vq04
  relative_down verified/verified/unsupported — a tolerance boundary, 0.035 perturbed to 0.03255,
  inside the 0.005 the grammar allows; vq05 relative_down verified/mismatch/unsupported; vq06
  digit_transposition verified/mismatch/unsupported; vq07 percent_ratio_confusion
  verified/mismatch/unsupported; vq08 relative_up verified/mismatch/unsupported; vq09 decimal_shift
  verified/mismatch/unsupported; vq10 relative_up verified/verified/unsupported — the second
  tolerance boundary, 0.0725 perturbed to 0.076125.** Both boundaries are reported as boundaries
  and not as errors, which is what `04` §6 asks for. All five perturbation types are drawn by the
  seed. The ten fixture tables were written for this repository; no FinQA or TAT-QA row is in it,
  and the live half of the component eval is Phase 13. No test calls a live model, downloads data,
  trains on real data or reads an API key. No push.
- 2026-09-07 — **Phase 8** — gate green on the four conditions that apply plus 5a, and **5b's
  substance now runs through `validate()`**: `pytest -q` 1036 passed, 0 failed, 0 skipped, 0
  xfailed (165 new); coverage of `src/quaestor` **100%** (`coverage run -m pytest`, 5021
  statements) against the 85% floor; `ruff check` and `ruff format --check` clean on
  `src tests eval subjects` (120 files); `mypy --strict src/quaestor` clean (57 source files).
  Gate condition **5a applies and passes** — `tests/test_golden_spec.py` (13 checks) still pins
  `examples/golden_report/`, which this phase **did not touch**: no byte of the directory changed
  and no new D-011 row was needed. **5b: the `quaestor validate` command line is Phase 9 and the
  CLI is still the Phase 0 version stub, so that line of `CLAUDE.md`'s command list was again not
  run — but what the command will do is `validate()`, and `tests/test_pipeline.py` runs it on both
  synthetic subjects under `FakeLLM` and validates the report it writes by the same checks
  `tests/test_golden_spec.py` applies to the golden.** So the substance of 5b holds today and the
  line itself is Phase 9's. **Gate condition 6 belongs to Phase 11**, where `tests/probatio/`
  arrives (D-007). Shipped `src/quaestor/report/{sections,drafter,repair,renderer,schema}.py` and
  the packaged `report_schema.json`, `src/quaestor/agent/planner.py`, `src/quaestor/configs.py`,
  `src/quaestor/pipeline.py` with `validate()`, the amended `verifier/match.py`, `extraction_from`
  and `masked_prose` in `verifier/extract.py`, `trace_fields` on `structured()`,
  `tests/reportsupport.py` and ten test modules (`test_verifier_rounding`, `test_report_schema`,
  `test_report_sections`, `test_drafter`, `test_repair`, `test_renderer`, `test_planner`,
  `test_configs`, `test_pipeline`, `test_pipeline_units`), DECISIONS D-069 to D-076, the Phase 8
  section of `docs/DESIGN.md` and the amended §6 of `docs/REPORT_SCHEMA.md`. `pyproject.toml` gains
  `types-jsonschema` (dev only, D-074); the public API gains `validate`, `ValidationRun`,
  `ConfigSpec` and `CONFIGURATIONS`, completing spec §9's surface, and `tests/test_scaffold.py`'s
  "validate is absent" assertion turns over into "validate is exported".
  **The amendment first (D-069):** a claim verifies when the artifact rounds to the written value
  at the precision the prose used — `0.74` against `0.7412` yes, `0.021` against `0.0175` no,
  `22.0%` against `0.2212` no — with spec §0's 0.005 / 0.5 / 1% as a ceiling, counts exact, and
  `rounding` narrowing only. **Measured: all 92 of the golden report's post-repair claims still
  verify and its pre-repair `0.0136` still mismatches; 60 of the 92 record a narrower `tolerance`
  than the Phase 1 `claims.json`** (every four-decimal metric 0.005 → 0.00005, `22.0%`
  0.005 → 0.0005, and each of the six claims that declared a `rounding`, whose field reverses
  direction), so `tests/test_verifier_golden.py` asserts the statuses exactly and the tolerances as
  an inequality with the narrowing count pinned. `examples/golden_report/claims.json` is **not**
  edited: it specifies the file's shape and its numbers are illustrative. The two tolerance
  boundaries Phase 7 measured, `vq04` and `vq10`, are gone — both perturbed sentences write four
  decimals and are now caught as the mismatches they are — so `eval/verifier_eval.py` reports
  `tolerance_boundaries == []` with status accuracy still 1.0 on all three classes.
  **Measured end to end at seed 20260901 on this machine (Python 3.12.14), `full_agent` under
  `FakeLLM`: `credit_default --synthetic 5000` — grounding precision 1.0000 pre-repair and 1.0000
  post-repair over 49 claims, 121 artifacts, exactly one finding, `F-001 E1` at severity `low`
  (D-017), 3.1 s wall-clock. `msr_prepayment --synthetic 2000` — 1.0000 and 1.0000 over 45 claims,
  227 artifacts, exactly no finding (D-047), 4.8 s, with the scenario table and the CPR table
  expanded inside renderer blocks.** Both figures are 1.0 because the offline fake is a competent
  drafter: it copies the values and the citations out of the JSON it is given, which is the rule the
  prompt states. The repair loop is exercised by fakes that break that rule on purpose:
  **an uncited number costs exactly one round (0.9804 → 1.0000 over 51 claims), and a number the
  drafter refuses to correct survives two rounds and is wrapped `⟦unverified: 0.9⟧`, leaving the
  post-repair figure at 0.9804 and the front matter saying so.** `rules_only` on the same subject
  emits **zero `llm_call` events** and scores 1.0000 over 139 claims; `plain_llm` records a finding
  whose evidence resolves as an ordinary finding and one whose evidence does not as an
  `unevidenced:` entry in `candidates_not_promoted`, pointing at the `unevidenced_record.<i>` JSON
  artifact that holds what the model claimed (D-072). The bounded loop runs exactly one follow-up
  for a scripted fake and refuses an unknown tool, a closed-`Args` violation (which is where an
  invented `entrypoint` is caught) and a path outside the package, each traced as a `plan_step`
  with its reason and never executed. No test calls a live model, downloads data, trains on real
  data or reads an API key. No push.
- 2026-09-07 — **Phase 9** — gate green on **all five** conditions that apply, 5b included for the
  first time: `pytest -q` 1110 passed, 0 failed, 0 skipped, 0 xfailed (74 new); coverage of
  `src/quaestor` **100%** (`coverage run -m pytest`, 5423 statements) against the 85% floor;
  `ruff check` and `ruff format --check` clean on `src tests eval subjects` (125 files);
  `mypy --strict src/quaestor` clean (59 source files). Gate condition **5a** passes —
  `tests/test_golden_spec.py` (13 checks) still pins `examples/golden_report/`, which this phase
  **did not touch**: no byte of the directory changed and no new D-011 row was needed. Gate
  condition **5b applies and passes**: `quaestor validate subjects/credit_default --synthetic
  --llm fake --out DIR` and the same line on `subjects/msr_prepayment` are run **through the
  installed console script, as subprocesses**, in `tests/test_cli.py`, and each report is put
  through the renderer's own `check_report`. Measured from a shell on this machine (Python
  3.12.14): **`credit_default` bare `--synthetic` (5,000 rows) — 3.7 s, grounding precision 1.0000
  pre- and post-repair over 49 claims, 121 artifacts, one finding; `msr_prepayment` bare
  `--synthetic` (2,000 loans) — grounding precision 1.0000 and 1.0000 over 45 claims, 227
  artifacts, no finding** — the same figures Phase 8 measured through `validate()`, which is what
  the command line was supposed to leave unchanged. **Gate condition 6 belongs to Phase 11**
  (D-007). Shipped `src/quaestor/cli.py` (the parser: `validate`, `tool`, `corpus ingest`, the
  three exit codes and a fixing command on every error), `src/quaestor/llm/offline.py`
  (`OfflineLLM`, the provider `--llm fake` builds, moved out of `tests/reportsupport.py`, which now
  subclasses it), `src/quaestor/llm/recording.py` (`RecordingLLM`, `ReplayLLM`, `cassette_key`),
  `SYNTHETIC_DEFAULT_N` and `synthetic_default_n` in `configs.py`, `tests/{test_cli,test_recording,
  test_offline_llm}.py`, DECISIONS D-077 to D-083, the Phase 9 section of `docs/DESIGN.md`, the
  README's quick start (no number from a run in it) and the `CHANGELOG.md` entries. `CLAUDE.md`
  is unchanged: every flag in its command list is correct as written. **Two fixes, each with its
  own tests.** (a) The pre-pass now defines the eligible numbers in *both* directions (D-077): a
  claim the extractor returns for a token that was excluded — a citation's hash or logical name,
  inline code, a heading, a renderer block — is dropped and recorded under
  `extractor_returned_excluded_token`, where Phase 7 would have kept it and let it *lower* the
  precision of a number the report never claimed. Claims are matched to tokens by value, within
  the quoted line first and then against any unfilled token of the section, so a paraphrasing
  extractor keeps its citations; two Phase 7 tests asserted the old behaviour and are rewritten,
  one into its mirror image and one into the paraphrase case. Every other verifier and pipeline
  test is unchanged and still passes, including the golden report's 92 claims. (b) `ClaudeCLILLM`
  passes a prompt over **64 KiB** on the subprocess's stdin with no positional argument, because a
  single argument that long is refused by macOS before the CLI runs (D-078); both paths are
  asserted with the monkeypatched `subprocess.run`. **The recording round trip is measured**: a
  `credit_default` run at 600 rows recorded 15 cassettes, and replaying them wrote a `report.md`
  **byte-identical** to the recorded run's apart from `generated` and Appendix C's two wall-clock
  rows — `run_id`, every claim, every artifact hash and both grounding figures are the same file
  twice — with `claims.json` and `findings.json` equal as JSON; deleting one cassette makes the
  replay exit 1 naming the missing hash rather than answering from anywhere else. The Phase 0 CLI
  stub is gone: bare `quaestor` is now a usage error and `quaestor --version` prints the version,
  so four `tests/test_scaffold.py` cases were rewritten. No test calls a live model, downloads
  data, trains on real data or reads an API key; `--llm anthropic` is covered by the error the
  missing extra raises, and no PDF is read anywhere. No push.
