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
- [ ] **Phase 4** — `msr_prepayment` subject incl. projection (spec §4.2)
- [ ] **Phase 5** — Tools, registry, statistics by hand (spec §3.7)
- [ ] **Phase 6** — Corpus ingest + BM25 + guidance citations (spec §3.8)
- [ ] **Phase 7** — Findings + claim verifier (spec §3.9–3.10)
- [ ] **Phase 8** — Drafter, repair, renderer, planner, configs; end-to-end on synthetic with
  `FakeLLM` (spec §3.11–3.13)
  - clean synthetic `credit_default` must yield exactly {E1 low} (D-017)
- [ ] **Phase 9** — CLI; first live validations of both real subjects (Claude CLI); reports
  committed (spec §3.14)
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
