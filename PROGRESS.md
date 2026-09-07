# PROGRESS.md — Quaestor

The run's only durable memory. A fresh session reads this file first, immediately after
`CLAUDE.md`. One phase per session; the checkbox and the run-log line for phase N are committed
with phase N's code (`git show --stat HEAD | grep PROGRESS.md`).

## Phases

Scope lines are taken from `02-SPEC.md` section 11; the spec sections each phase implements from
are named in brackets.

- [x] **Phase 0** — Scaffolding, CI, name check, dev deps incl. `probatio-llm` (spec §2)
- [ ] **Phase 1** — Golden report, claim grammar, report schema, synthetic `package.yaml`
  (spec §7, §3.2, §3.10–3.11)
- [ ] **Phase 2** — Foundations, package loader, artifact store, LLM layer, trace (spec §3.1–3.5)
- [ ] **Phase 3** — Sandbox `run_model` + `credit_default` subject (synthetic first, then
  `sample.py`) (spec §3.6, §4.1)
- [ ] **Phase 4** — `msr_prepayment` subject incl. projection (spec §4.2)
- [ ] **Phase 5** — Tools, registry, statistics by hand (spec §3.7)
- [ ] **Phase 6** — Corpus ingest + BM25 + guidance citations (spec §3.8)
- [ ] **Phase 7** — Findings + claim verifier (spec §3.9–3.10)
- [ ] **Phase 8** — Drafter, repair, renderer, planner, configs; end-to-end on synthetic with
  `FakeLLM` (spec §3.11–3.13)
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
