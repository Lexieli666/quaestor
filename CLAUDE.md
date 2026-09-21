# CLAUDE.md — Quaestor

Project constitution. Re-read this file at the start of every session, before touching code. It
overrides any prompt that contradicts it.

## What Quaestor is

An **agentic model-validation copilot**. It takes a model package (code, data reference, fitted
artifacts, developer claims) and produces an SR 11-7-shaped validation report in which every
quantitative claim carries a machine-checked citation to a computed artifact. Its differentiator is
the open evaluation: seeded defects in the author's own rebuilt models, with detection precision
and recall, false-alarm rate and per-report grounding precision published, misses included.

It is not a compliance product. Every document says "SR 11-7-shaped", never "compliant" or
"certified".

## Hard constraints

Violating any of these is a defect, even if tests pass.

- **No live LLM call in the test suite or in any code path exercised by `pytest`.** All model
  interaction goes through the `LLM` protocol (`complete(prompt, *, system=None, **params) ->
  Completion`, structurally identical to Probatio's `Provider`). Tests use `FakeLLM` and committed
  Probatio cassettes. Live calls happen only through `quaestor validate --llm claude-cli`,
  `quaestor study run`, and `quaestor verifier-eval`, invoked deliberately by a human.
- **Anthropic is the only live provider shipped**: `AnthropicLLM` (SDK, optional extra) and
  `ClaudeCLILLM` (subprocess over the Claude Code CLI). No OpenAI adapter.
- **Tests never download data and never train on real data.** Every subject has a `--synthetic`
  mode that generates a small panel from a known process; tests, the demo and CI use only that.
  Real data is read from a path the human passes on the command line and is never committed.
- **A finding requires evidence.** A `Finding` object cannot be constructed without at least one
  artifact hash that exists in the store. The LLM writes narrative; it does not mint findings.
- **Every numeric claim in a report is verified or marked.** The renderer refuses to emit a report
  whose claims appendix is missing or whose grounding precision is not printed.
- **`run_model` executes subjects in a subprocess** with a wall-clock cap, a memory cap and network
  disabled; never `import`ed into the validator's process.
- **Nothing proprietary, nothing personal.** No former-employer or client material of any kind; the
  employer names stay on the resume and out of this repository, including out of this sentence. No
  Freddie Mac rows in the repo. No API keys anywhere.
- **`src/` layout, Python 3.11+.** Import path `quaestor`.
- **Runtime dependencies are exactly:** `pydantic>=2`, `PyYAML`, `numpy`, `pandas`,
  `scikit-learn`, `jsonschema`. Optional extras: `anthropic`, `mcp`, `xgboost`. Dev: `pytest`,
  `probatio-llm`, `ruff`, `mypy`, `coverage`, type stubs. Anything else needs a numbered
  `DECISIONS.md` entry, and adding a runtime dependency is a stop-and-ask.
- **Typed, docstringed, tested.** `mypy --strict src/quaestor` passes; every module ships with tests.

## Repository layout

```
quaestor/
  pyproject.toml  README.md  CLAUDE.md  PROGRESS.md  DECISIONS.md  BLOCKERS.md  CHANGELOG.md
  src/quaestor/
    errors.py  hashing.py  trace.py
    package/        ModelPackage, package.yaml schema, loader, validation
    artifacts/      content-addressed ArtifactStore, index, citation syntax
    llm/            LLM protocol, Completion, FakeLLM, AnthropicLLM, ClaudeCLILLM, structured-output helper
    sandbox/        run_model: subprocess with caps
    tools/          registry + one module per tool (profiler, metrics, leakage, stability,
                    collinearity, challenger, scenarios, guidance)
    corpus/         regulatory corpus chunking, BM25 (hand-written), section ids
    findings.py     Finding, Severity, DefectClass
    verifier/       claim grammar, extractor (LLM), matcher (deterministic), grounding precision
    report/         section plan, drafter, repair loop, renderer (markdown + appendices)
    agent/          planner: rule-based check list + bounded JSON-action loop
    configs.py      full_agent, rules_only, plain_llm
    mcp_server.py   the tool registry over MCP stdio (optional extra)
    cli.py          `quaestor` console script
  subjects/
    credit_default/   package.yaml, code/, sample.py, synthetic.py
    msr_prepayment/   package.yaml, code/, sample_freddie.py, synthetic.py
  eval/
    taxonomy.yaml     defect classes and recipes
    seed.py           subject + defect -> variant package
    run_study.py  score.py  verifier_eval.py
    results/<ts>/     summary.json, per-variant reports, traces
    results/published/
  tests/            unit + pytester; tests/probatio/ = Probatio cases, cassettes, variants
  docs/             DESIGN.md CHECKLIST.md REPORT_SCHEMA.md EVALUATION.md STUDY.md PROVENANCE.md
  examples/         golden_report/ (Phase 1 executable spec), demo packages in synthetic mode
```

## Commands

```bash
. .venv/bin/activate
pytest -q
coverage run -m pytest -q && coverage report
ruff check src tests eval subjects && ruff format --check src tests eval subjects
mypy --strict src/quaestor
quaestor validate subjects/credit_default --synthetic --llm fake --out /tmp/r   # end-to-end, offline
```

## Quality gate (definition of done for every phase)

1. `pytest -q`: zero failures, errors, skips, xfails.
2. Line coverage of `src/quaestor` at least 85% (`coverage run -m pytest`).
3. `ruff check` and `ruff format --check` clean.
4. `mypy --strict src/quaestor` clean.
5. `examples/golden_report/` (Phase 1) is byte-identical to its introducing commit except the
   sanctioned edits recorded in `DECISIONS.md`; `quaestor validate --synthetic --llm fake` on both
   subjects produces a report that validates against `docs/REPORT_SCHEMA.md`.
6. From Phase 11 on: `pytest tests/probatio --cassette=replay` passes with zero provider calls.

## Working style

- One phase per Claude Code session; conventional commits; the `PROGRESS.md` tick and run-log
  line ship in the same commit as the phase's code (`git show --stat HEAD | grep PROGRESS.md`).
- Judgement calls go to `DECISIONS.md` as numbered `Q / A / Why` entries; stop and ask only for a
  new runtime dependency, a Python-floor change, a change to `package.yaml` or the report schema
  after Phase 1, or anything that would call a live model or download data from a test.
- Three-strike rule → `BLOCKERS.md`, `[blocked]` in `PROGRESS.md`, move on.
- Never commit or push a broken tree; push only at a green phase end.
- Statistics by hand where small (PSI, KS, VIF, Brier, Wilson); scikit-learn for models and AUC.
- Every non-obvious choice gets a `docs/DESIGN.md` paragraph naming the rejected alternative.
- No number in `README.md`, `docs/` or a report that a committed run did not produce.
