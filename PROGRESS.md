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
- [ ] **Phase 2** — Foundations, package loader, artifact store, LLM layer, trace (spec §3.1–3.5)
- [ ] **Phase 3** — Sandbox `run_model` + `credit_default` subject (synthetic first, then
  `sample.py`) (spec §3.6, §4.1)
  - clean synthetic `credit_default` must yield exactly {E1 low} (D-017)
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
